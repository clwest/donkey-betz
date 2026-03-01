# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
"""
Tests for Video RAG ingest pipeline.

Covers:
- POST /api/documents/ingest-video/ endpoint validation
- VideoTranscriptSplitter chunk logic
- ingest_video_task Celery pipeline
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import io
import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


def _get_user():
    return (
        User.objects.filter(is_superuser=True).first()
        or User.objects.first()
        or User.objects.create_user(username="testuser", email="test@example.com")
    )


def _make_video_request(user, file_obj=None, data=None):
    """Build a multipart POST request for ingest-video."""
    factory = APIRequestFactory()
    post_data = data or {}
    if file_obj:
        post_data['file'] = file_obj
    request = factory.post(
        "/api/documents/ingest-video/",
        data=post_data,
        format="multipart",
    )
    force_authenticate(request, user=user)
    return request


class TestIngestVideoView:
    """Tests for the ingest_video endpoint."""

    def test_no_file_returns_400(self):
        from core.views_rag_embeddings import ingest_video

        user = _get_user()
        request = _make_video_request(user)

        response = ingest_video(request)

        assert response.status_code == 400
        assert response.data["success"] is False
        assert "No video file" in response.data["error"]
        assert "correlation_id" in response.data

    def test_bad_extension_returns_400(self):
        from core.views_rag_embeddings import ingest_video

        user = _get_user()
        fake_file = io.BytesIO(b"not a video")
        fake_file.name = "test.txt"
        fake_file.size = 100
        request = _make_video_request(user, file_obj=fake_file)

        response = ingest_video(request)

        assert response.status_code == 400
        assert response.data["success"] is False
        assert "Unsupported video format" in response.data["error"]
        assert "correlation_id" in response.data

    @patch("core.views_rag_embeddings.ingest_video.__module__", "core.views_rag_embeddings")
    def test_valid_upload_returns_202(self):
        from core.views_rag_embeddings import ingest_video

        user = _get_user()
        fake_file = io.BytesIO(b"\x00" * 1024)
        fake_file.name = "test_clip.mp4"
        fake_file.size = 1024
        request = _make_video_request(user, file_obj=fake_file)

        mock_task = MagicMock()
        mock_task.id = "fake-task-id-123"

        with patch("core.tasks.ingest_video_task.delay", return_value=mock_task):
            response = ingest_video(request)

        assert response.status_code == 202
        assert response.data["success"] is True
        assert response.data["job_id"] == "fake-task-id-123"
        assert "document_id" in response.data
        assert "correlation_id" in response.data

    def test_celery_down_returns_503(self):
        from core.views_rag_embeddings import ingest_video

        user = _get_user()
        fake_file = io.BytesIO(b"\x00" * 1024)
        fake_file.name = "test_clip.mp4"
        fake_file.size = 1024
        request = _make_video_request(user, file_obj=fake_file)

        with patch("core.tasks.ingest_video_task.delay", side_effect=ConnectionError("Redis down")):
            response = ingest_video(request)

        assert response.status_code == 503
        assert response.data["success"] is False
        assert "Task queue unavailable" in response.data["error"]
        assert "correlation_id" in response.data


class TestVideoTranscriptSplitter:
    """Tests for the VideoTranscriptSplitter."""

    def test_empty_segments_returns_empty(self):
        from content.embeddings import VideoTranscriptSplitter

        splitter = VideoTranscriptSplitter()
        assert splitter.split_segments([]) == []

    def test_correct_chunk_shape(self):
        from content.embeddings import VideoTranscriptSplitter

        segments = [
            {"text": "Hello world.", "start": 0.0, "end": 2.5},
            {"text": "This is a test.", "start": 2.5, "end": 5.0},
        ]

        splitter = VideoTranscriptSplitter(chunk_size=5000)
        chunks = splitter.split_segments(segments)

        assert len(chunks) == 1
        chunk = chunks[0]
        assert "text" in chunk
        assert "index" in chunk
        assert "size" in chunk
        assert "metadata" in chunk
        assert chunk["index"] == 0
        assert "Hello world." in chunk["text"]
        assert "This is a test." in chunk["text"]

    def test_timestamps_in_metadata_as_integer_ms(self):
        from content.embeddings import VideoTranscriptSplitter

        segments = [
            {"text": "Segment one.", "start": 1.5, "end": 3.0},
            {"text": "Segment two.", "start": 3.0, "end": 6.75},
        ]

        splitter = VideoTranscriptSplitter(chunk_size=5000)
        chunks = splitter.split_segments(segments)

        meta = chunks[0]["metadata"]
        assert meta["start_ms"] == 1500
        assert meta["end_ms"] == 6750
        assert isinstance(meta["start_ms"], int)
        assert isinstance(meta["end_ms"], int)

    def test_sequential_indices(self):
        from content.embeddings import VideoTranscriptSplitter

        # Generate enough text to create multiple chunks
        segments = [
            {"text": f"Word " * 300, "start": float(i * 10), "end": float(i * 10 + 10)}
            for i in range(5)
        ]

        splitter = VideoTranscriptSplitter(chunk_size=500)
        chunks = splitter.split_segments(segments)

        assert len(chunks) > 1
        for i, chunk in enumerate(chunks):
            assert chunk["index"] == i

    def test_base_metadata_merged(self):
        from content.embeddings import VideoTranscriptSplitter

        segments = [{"text": "Hello.", "start": 0.0, "end": 1.0}]
        base = {"source": "test_video", "doc_id": "abc123"}

        splitter = VideoTranscriptSplitter()
        chunks = splitter.split_segments(segments, metadata=base)

        meta = chunks[0]["metadata"]
        assert meta["source"] == "test_video"
        assert meta["doc_id"] == "abc123"
        assert "start_ms" in meta
        assert "end_ms" in meta


class TestIngestVideoTask:
    """Tests for ingest_video_task Celery task."""

    @patch("core.tasks.generate_document_embeddings")
    @patch("openai.OpenAI")
    def test_success_sets_document_processed(self, mock_openai_cls, mock_embed_task):
        from content.models import Document, DocumentType

        user = _get_user()
        document = Document.objects.create(
            owner=user,
            title="Test Video",
            document_type=DocumentType.VIDEO,
            status='pending',
        )

        # Create a temp file to act as video
        import tempfile
        fd, tmp_path = tempfile.mkstemp(suffix='.mp4')
        os.write(fd, b"\x00" * 100)
        os.close(fd)

        # Mock ffmpeg subprocess
        mock_ffmpeg = MagicMock()
        mock_ffmpeg.returncode = 0

        # Mock Whisper response
        mock_transcript = MagicMock()
        mock_transcript.text = "Hello world from video"
        seg = MagicMock()
        seg.start = 0.0
        seg.end = 2.5
        seg.text = "Hello world from video"
        # Make segment behave as non-dict
        mock_transcript.segments = [seg]

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_transcript
        mock_openai_cls.return_value = mock_client

        mock_embed_task.delay = MagicMock()

        with patch("subprocess.run", return_value=mock_ffmpeg):
            with patch("os.path.getsize", return_value=1024 * 1024):
                # Import and call directly (not .delay) for testing
                from core.tasks import ingest_video_task
                result = ingest_video_task(
                    str(document.id), tmp_path, "test.mp4", str(user.id), "en"
                )

        document.refresh_from_db()
        assert document.status == 'processed'
        assert "Hello world from video" in document.processed_content
        assert result['status'] == 'success'
        assert result['segment_count'] == 1
        mock_embed_task.delay.assert_called_once()

    @patch("core.tasks.generate_document_embeddings")
    def test_ffmpeg_failure_sets_document_failed(self, mock_embed_task):
        from content.models import Document, DocumentType

        user = _get_user()
        document = Document.objects.create(
            owner=user,
            title="Bad Video",
            document_type=DocumentType.VIDEO,
            status='pending',
        )

        import tempfile
        fd, tmp_path = tempfile.mkstemp(suffix='.mp4')
        os.write(fd, b"\x00" * 100)
        os.close(fd)

        mock_ffmpeg = MagicMock()
        mock_ffmpeg.returncode = 1
        mock_ffmpeg.stderr = "Invalid data found when processing input"

        with patch("subprocess.run", return_value=mock_ffmpeg):
            from core.tasks import ingest_video_task

            # Task will raise RuntimeError and then try to retry.
            # Since we're calling directly (not via Celery), retry raises.
            with pytest.raises(Exception):
                ingest_video_task(
                    str(document.id), tmp_path, "bad.mp4", str(user.id), "en"
                )

        document.refresh_from_db()
        assert document.status == 'failed'
        assert "ffmpeg failed" in document.error_message

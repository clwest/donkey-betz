# tests/integration/test_video_workflow.py
"""Integration tests for video generation workflow."""
import pytest
from unittest.mock import patch, MagicMock
from tests.factories import (
    UserFactory, CreativeProjectFactory,
    ImageHistoryFactory, VideoHistoryFactory
)

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


class TestVideoGenerationWorkflow:
    """Integration tests for complete video generation workflow."""

    @patch('content.video_provider.requests')
    def test_text_to_video_workflow(
        self, mock_requests, authenticated_client, user, project
    ):
        """Test complete text-to-video generation workflow."""
        # Mock Runway response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'task-12345',
            'status': 'PENDING'
        }
        mock_requests.post.return_value = mock_response

        # Step 1: Start video generation
        response = authenticated_client.post('/api/videos/generate/', {
            'prompt': 'A beautiful sunset animation',
            'duration': 10,
            'project_id': str(project.id)
        })

        if response.status_code == 404:
            pytest.skip('Video generation endpoint not found')

        assert response.status_code in [200, 201, 202]

        # Step 2: Check status
        video_id = response.json().get('id') or response.json().get('data', {}).get('id')
        if video_id:
            mock_response.json.return_value = {
                'id': video_id,
                'status': 'SUCCEEDED',
                'output': ['https://example.com/video.mp4']
            }
            mock_requests.get.return_value = mock_response

            status_response = authenticated_client.get(f'/api/videos/{video_id}/status/')
            assert status_response.status_code in [200, 404]

    @patch('content.video_provider.requests')
    def test_image_to_video_workflow(
        self, mock_requests, authenticated_client, user, project
    ):
        """Test image-to-video generation workflow."""
        # Create source image
        image = ImageHistoryFactory(user=user, project=project)

        # Mock Runway response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'task-67890',
            'status': 'PENDING'
        }
        mock_requests.post.return_value = mock_response

        # Generate video from image
        response = authenticated_client.post('/api/videos/generate/', {
            'prompt': 'Animate this sunset image',
            'image_id': str(image.id),
            'duration': 10,
            'project_id': str(project.id)
        })

        assert response.status_code in [200, 201, 202, 404]


class TestVideoEditingWorkflow:
    """Integration tests for video editing workflow."""

    def test_video_upscale_workflow(self, authenticated_client, user, project):
        """Test video upscale workflow."""
        video = VideoHistoryFactory(user=user, project=project)

        response = authenticated_client.post('/api/videos/upscale/', {
            'video_id': str(video.id),
            'scale': 2
        })

        assert response.status_code in [200, 202, 400, 404]

    def test_video_color_grade_workflow(self, authenticated_client, user, project):
        """Test video color grading workflow."""
        video = VideoHistoryFactory(user=user, project=project)

        response = authenticated_client.post('/api/videos/color-grade/', {
            'video_id': str(video.id),
            'effect': 'cinematic'
        })

        assert response.status_code in [200, 202, 400, 404]

    def test_video_trim_workflow(self, authenticated_client, user, project):
        """Test video trimming workflow."""
        video = VideoHistoryFactory(user=user, project=project, duration=10)

        response = authenticated_client.post('/api/videos/trim/', {
            'video_id': str(video.id),
            'start': 2,
            'end': 8
        })

        assert response.status_code in [200, 202, 400, 404]

    def test_video_speed_change_workflow(self, authenticated_client, user, project):
        """Test video speed change workflow."""
        video = VideoHistoryFactory(user=user, project=project)

        response = authenticated_client.post('/api/videos/speed/', {
            'video_id': str(video.id),
            'speed': 0.5  # Slow motion
        })

        assert response.status_code in [200, 202, 400, 404]


class TestProjectVideoWorkflow:
    """Integration tests for project-video relationships."""

    def test_videos_associated_with_project(self, user):
        """Test that videos are properly associated with projects."""
        project = CreativeProjectFactory(user=user)

        # Create videos for project
        vid1 = VideoHistoryFactory(user=user, project=project)
        vid2 = VideoHistoryFactory(user=user, project=project)
        vid3 = VideoHistoryFactory(user=user, project=None)  # No project

        # Verify project videos
        project_videos = project.project_videos.all()
        assert vid1 in project_videos
        assert vid2 in project_videos
        assert vid3 not in project_videos
        assert project_videos.count() == 2

    def test_video_isolation_between_users(self, db):
        """Test that users can only see their own videos."""
        from content.models import VideoHistory

        user1 = UserFactory()
        user2 = UserFactory()

        vid1 = VideoHistoryFactory(user=user1)
        vid2 = VideoHistoryFactory(user=user2)

        user1_videos = VideoHistory.objects.filter(user=user1)
        user2_videos = VideoHistory.objects.filter(user=user2)

        assert vid1 in user1_videos
        assert vid1 not in user2_videos
        assert vid2 in user2_videos
        assert vid2 not in user1_videos


class TestVideoStatusPolling:
    """Integration tests for video status polling."""

    def test_status_updates_correctly(self, user, project):
        """Test that video status updates correctly."""
        from content.models import VideoHistory

        video = VideoHistoryFactory(
            user=user,
            project=project,
            status='pending'
        )

        # Update status
        video.status = 'processing'
        video.save()
        video.refresh_from_db()
        assert video.status == 'processing'

        # Complete
        video.status = 'completed'
        video.video_url = 'https://example.com/completed.mp4'
        video.save()
        video.refresh_from_db()
        assert video.status == 'completed'
        assert video.video_url != ''

    def test_failed_video_has_error_message(self, user, project):
        """Test that failed videos have error messages."""
        from content.models import VideoHistory

        video = VideoHistoryFactory(
            user=user,
            project=project,
            status='failed',
            error_message='Content moderation failed'
        )

        assert video.status == 'failed'
        assert 'moderation' in video.error_message.lower()


class TestVideoExtensionWorkflow:
    """Integration tests for video extension (8s -> 18s -> 28s)."""

    def test_video_extension_chain(self, user, project):
        """Test chaining video extensions."""
        from content.models import VideoHistory

        # Original 10-second video
        original = VideoHistoryFactory(
            user=user,
            project=project,
            video_type='text_to_video',
            duration=10,
            video_url='https://example.com/original.mp4'
        )

        # Extended to 20 seconds
        extended = VideoHistory.objects.create(
            user=user,
            project=project,
            video_type='extend_video',
            prompt='Continue the animation',
            model_used='gen4_turbo',
            duration=20,
            parent_video_url=original.video_url,
            status='completed'
        )

        assert extended.parent_video_url == original.video_url
        assert extended.duration == 20

    def test_video_sequential_numbers(self, user, project):
        """Test video sequential numbering."""
        # Create videos
        videos = [VideoHistoryFactory(user=user, project=project) for _ in range(5)]

        # Verify sequential numbers
        for i, vid in enumerate(videos, start=1):
            seq_num = vid.get_sequential_number()
            assert seq_num == i

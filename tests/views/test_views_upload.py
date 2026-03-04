"""
Tests for upload endpoints: Cloudinary sign, register, and simple upload.

Covers:
- Authentication enforcement (401 for unauthenticated)
- Cloudinary sign returns expected keys and correct folder prefix
- Cloudinary register creates VideoHistory and rejects missing fields
- Simple upload validates file size and type
"""
import io
import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# Cloudinary Sign Endpoint
# =============================================================================

class TestCloudinaryUploadSign:
    """Tests for POST /api/upload/cloudinary/sign/"""

    url = '/api/upload/cloudinary/sign/'

    def test_unauthenticated_returns_401_or_403(self, api_client):
        resp = api_client.post(self.url, {'resource_type': 'video'}, format='json')
        assert resp.status_code in (401, 403)

    @patch('core.views_upload.cloudinary')
    def test_returns_expected_keys(self, mock_cloudinary, authenticated_client, user):
        mock_config = MagicMock()
        mock_config.cloud_name = 'test-cloud'
        mock_config.api_key = 'test-key'
        mock_config.api_secret = 'test-secret'
        mock_cloudinary.config.return_value = mock_config

        resp = authenticated_client.post(self.url, {'resource_type': 'video'}, format='json')
        assert resp.status_code == 200

        data = resp.json()
        assert data['success'] is True
        for key in ('cloud_name', 'api_key', 'timestamp', 'signature', 'folder', 'resource_type'):
            assert key in data, f"Missing key: {key}"

    @patch('core.views_upload.cloudinary')
    def test_folder_contains_user_id(self, mock_cloudinary, authenticated_client, user):
        mock_config = MagicMock()
        mock_config.cloud_name = 'test-cloud'
        mock_config.api_key = 'test-key'
        mock_config.api_secret = 'test-secret'
        mock_cloudinary.config.return_value = mock_config

        resp = authenticated_client.post(self.url, {'resource_type': 'video'}, format='json')
        data = resp.json()
        assert f'uploads/videos/{user.id}/' in data['folder']

    @patch('core.views_upload.cloudinary')
    def test_rejects_invalid_resource_type(self, mock_cloudinary, authenticated_client):
        resp = authenticated_client.post(self.url, {'resource_type': 'audio'}, format='json')
        assert resp.status_code == 400

    @patch('core.views_upload.cloudinary')
    def test_returns_500_when_cloudinary_not_configured(self, mock_cloudinary, authenticated_client):
        mock_config = MagicMock()
        mock_config.cloud_name = None
        mock_config.api_key = None
        mock_config.api_secret = None
        mock_cloudinary.config.return_value = mock_config

        resp = authenticated_client.post(self.url, {'resource_type': 'video'}, format='json')
        assert resp.status_code == 500


# =============================================================================
# Cloudinary Register Endpoint
# =============================================================================

class TestCloudinaryUploadRegister:
    """Tests for POST /api/upload/video/register/"""

    url = '/api/upload/video/register/'

    def test_unauthenticated_returns_401_or_403(self, api_client):
        resp = api_client.post(self.url, {'secure_url': 'https://x', 'public_id': 'y'}, format='json')
        assert resp.status_code in (401, 403)

    def test_creates_video_history(self, authenticated_client, user):
        from content.models import VideoHistory
        resp = authenticated_client.post(self.url, {
            'secure_url': 'https://res.cloudinary.com/test/video/upload/v1/uploads/test.mp4',
            'public_id': f'uploads/videos/{user.id}/2026/03/test',
            'bytes': 1024000,
            'duration': 60,
            'width': 1920,
            'height': 1080,
            'format': 'mp4',
            'original_filename': 'demo.mp4',
            'title': 'My Demo Video',
        }, format='json')

        assert resp.status_code == 200
        data = resp.json()
        assert data['success'] is True
        assert 'video' in data
        assert data['video']['url'] == 'https://res.cloudinary.com/test/video/upload/v1/uploads/test.mp4'

        # Verify DB record
        vid = VideoHistory.objects.get(id=data['video']['id'])
        assert vid.user == user
        assert vid.source_type == 'uploaded'
        assert vid.video_width == 1920
        assert vid.duration == 60
        assert vid.status == 'completed'

    def test_rejects_missing_secure_url(self, authenticated_client):
        resp = authenticated_client.post(self.url, {
            'public_id': 'some/path',
        }, format='json')
        assert resp.status_code == 400

    def test_rejects_missing_public_id(self, authenticated_client):
        resp = authenticated_client.post(self.url, {
            'secure_url': 'https://example.com/video.mp4',
        }, format='json')
        assert resp.status_code == 400

    def test_handles_missing_optional_fields(self, authenticated_client):
        """Register should succeed even with only required fields."""
        resp = authenticated_client.post(self.url, {
            'secure_url': 'https://res.cloudinary.com/test/video.mp4',
            'public_id': 'uploads/videos/test',
        }, format='json')
        assert resp.status_code == 200
        assert resp.json()['success'] is True


# =============================================================================
# Simple Video Upload Endpoint
# =============================================================================

class TestSimpleVideoUpload:
    """Tests for POST /api/upload/video/"""

    url = '/api/upload/video/'

    def test_unauthenticated_returns_401_or_403(self, api_client):
        resp = api_client.post(self.url)
        assert resp.status_code in (401, 403)

    def test_rejects_no_file(self, authenticated_client):
        resp = authenticated_client.post(self.url)
        assert resp.status_code == 400
        assert 'No file' in resp.json().get('error', '')

    def test_rejects_oversized_file(self, authenticated_client):
        """Files over 50 MB should be rejected with redirect to chunked upload."""
        big_file = io.BytesIO(b'\x00' * (51 * 1024 * 1024))
        big_file.name = 'big.mp4'
        big_file.content_type = 'video/mp4'

        resp = authenticated_client.post(self.url, {'file': big_file}, format='multipart')
        assert resp.status_code == 400
        data = resp.json()
        assert data.get('use_chunked') is True

    @patch('core.views_upload.cloudinary.uploader.upload')
    def test_accepts_small_file(self, mock_upload, authenticated_client):
        """Small video file should upload successfully."""
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/test/video.mp4',
            'public_id': 'uploads/videos/2026/03/test',
            'url': 'http://res.cloudinary.com/test/video.mp4',
        }

        small_file = io.BytesIO(b'\x00\x00\x00\x1c\x66\x74\x79\x70\x69\x73\x6f\x6d')  # minimal MP4 header
        small_file.name = 'small.mp4'
        small_file.content_type = 'video/mp4'

        resp = authenticated_client.post(self.url, {'file': small_file}, format='multipart')
        assert resp.status_code == 200
        assert resp.json()['success'] is True

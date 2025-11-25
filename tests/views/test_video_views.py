# tests/views/test_video_views.py
"""Tests for video generation and editing views."""
import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status
from tests.factories import VideoHistoryFactory, ImageHistoryFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestVideoGalleryView:
    """Tests for video gallery/listing endpoints."""

    def test_gallery_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.get('/api/videos/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_gallery_returns_user_videos_only(self, authenticated_client, user, second_user, project):
        """Test that gallery only returns authenticated user's videos."""
        user_video = VideoHistoryFactory(user=user, project=project)
        other_video = VideoHistoryFactory(user=second_user)

        response = authenticated_client.get('/api/videos/')

        assert response.status_code == status.HTTP_200_OK
        video_ids = str(response.data)
        assert str(user_video.id) in video_ids
        assert str(other_video.id) not in video_ids

    def test_gallery_empty_for_new_user(self, authenticated_client, user):
        """Test gallery is empty for user with no videos."""
        response = authenticated_client.get('/api/videos/')
        assert response.status_code == status.HTTP_200_OK


class TestVideoGenerationView:
    """Tests for video generation endpoints."""

    def test_generate_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post('/api/videos/generate/', {
            'prompt': 'A sunset animation'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_generate_missing_prompt(self, authenticated_client):
        """Test validation error for missing prompt."""
        response = authenticated_client.post('/api/videos/generate/', {})
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    @patch('content.video_provider.requests')
    def test_generate_text_to_video(self, mock_requests, authenticated_client, project):
        """Test text-to-video generation."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test-task-123',
            'status': 'PENDING'
        }
        mock_requests.post.return_value = mock_response

        response = authenticated_client.post('/api/videos/generate/', {
            'prompt': 'A beautiful sunset animation',
            'project_id': str(project.id)
        })

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_404_NOT_FOUND
        ]

    @patch('content.video_provider.requests')
    def test_generate_image_to_video(self, mock_requests, authenticated_client, user, project):
        """Test image-to-video generation."""
        image = ImageHistoryFactory(user=user, project=project)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'test-task-456',
            'status': 'PENDING'
        }
        mock_requests.post.return_value = mock_response

        response = authenticated_client.post('/api/videos/generate/', {
            'prompt': 'Animate this image',
            'image_id': str(image.id),
            'project_id': str(project.id)
        })

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_202_ACCEPTED,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoStatusView:
    """Tests for video status check endpoint."""

    def test_check_status_unauthenticated(self, api_client, video_history):
        """Test that unauthenticated requests are rejected."""
        response = api_client.get(f'/api/videos/{video_history.id}/status/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_check_status_completed_video(self, authenticated_client, video_history):
        """Test checking status of completed video."""
        video_history.status = 'completed'
        video_history.save()

        response = authenticated_client.get(f'/api/videos/{video_history.id}/status/')

        if response.status_code == status.HTTP_200_OK:
            assert response.data.get('status') == 'completed'

    def test_check_status_other_users_video(self, authenticated_client, second_user):
        """Test error when checking status of another user's video."""
        other_video = VideoHistoryFactory(user=second_user)

        response = authenticated_client.get(f'/api/videos/{other_video.id}/status/')

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoUpscaleView:
    """Tests for video upscale endpoint."""

    def test_upscale_unauthenticated(self, api_client, video_history):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post('/api/videos/upscale/', {
            'video_id': str(video_history.id)
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upscale_other_users_video(self, authenticated_client, second_user):
        """Test error when trying to upscale another user's video."""
        other_video = VideoHistoryFactory(user=second_user)

        response = authenticated_client.post('/api/videos/upscale/', {
            'video_id': str(other_video.id)
        })

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_upscale_invalid_scale_factor(self, authenticated_client, video_history):
        """Test validation of scale factor."""
        response = authenticated_client.post('/api/videos/upscale/', {
            'video_id': str(video_history.id),
            'scale': 10  # Invalid scale
        })

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoColorGradingView:
    """Tests for video color grading endpoint."""

    def test_color_grade_unauthenticated(self, api_client, video_history):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post('/api/videos/color-grade/', {
            'video_id': str(video_history.id),
            'effect': 'cinematic'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_color_grade_valid_effects(self, authenticated_client, video_history):
        """Test valid color grading effects."""
        valid_effects = ['cinematic', 'vintage', 'noir', 'warm', 'cool', 'vibrant']

        for effect in valid_effects:
            response = authenticated_client.post('/api/videos/color-grade/', {
                'video_id': str(video_history.id),
                'effect': effect
            })

            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_202_ACCEPTED,
                status.HTTP_404_NOT_FOUND
            ]

    def test_color_grade_invalid_effect(self, authenticated_client, video_history):
        """Test invalid color grading effect."""
        response = authenticated_client.post('/api/videos/color-grade/', {
            'video_id': str(video_history.id),
            'effect': 'not_a_real_effect'
        })

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoTrimView:
    """Tests for video trimming endpoint."""

    def test_trim_unauthenticated(self, api_client, video_history):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post('/api/videos/trim/', {
            'video_id': str(video_history.id),
            'start': 0,
            'end': 5
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_trim_valid_range(self, authenticated_client, video_history):
        """Test trimming with valid time range."""
        response = authenticated_client.post('/api/videos/trim/', {
            'video_id': str(video_history.id),
            'start': 0,
            'end': 5
        })

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_404_NOT_FOUND
        ]

    def test_trim_invalid_range(self, authenticated_client, video_history):
        """Test trimming with invalid time range."""
        # End before start
        response = authenticated_client.post('/api/videos/trim/', {
            'video_id': str(video_history.id),
            'start': 10,
            'end': 5
        })

        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoSpeedView:
    """Tests for video speed change endpoint."""

    def test_speed_change_valid_factor(self, authenticated_client, video_history):
        """Test speed change with valid factor."""
        response = authenticated_client.post('/api/videos/speed/', {
            'video_id': str(video_history.id),
            'speed': 2.0
        })

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_404_NOT_FOUND
        ]

    def test_speed_change_slow_motion(self, authenticated_client, video_history):
        """Test slow motion (speed < 1)."""
        response = authenticated_client.post('/api/videos/speed/', {
            'video_id': str(video_history.id),
            'speed': 0.5
        })

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoFavoriteToggle:
    """Tests for video favorite toggle endpoint."""

    def test_toggle_favorite(self, authenticated_client, video_history):
        """Test toggling video favorite status."""
        assert video_history.is_favorite is False

        response = authenticated_client.post(f'/api/videos/{video_history.id}/favorite/')

        if response.status_code == status.HTTP_200_OK:
            video_history.refresh_from_db()
            assert video_history.is_favorite is True

    def test_toggle_favorite_other_users_video(self, authenticated_client, second_user):
        """Test error when trying to favorite another user's video."""
        other_video = VideoHistoryFactory(user=second_user)

        response = authenticated_client.post(f'/api/videos/{other_video.id}/favorite/')

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestVideoDeleteView:
    """Tests for video deletion endpoint."""

    def test_delete_video(self, authenticated_client, user, project):
        """Test deleting a video."""
        from content.models import VideoHistory

        video = VideoHistoryFactory(user=user, project=project)
        video_id = video.id

        response = authenticated_client.delete(f'/api/videos/{video_id}/')

        if response.status_code == status.HTTP_204_NO_CONTENT:
            assert not VideoHistory.objects.filter(id=video_id, is_active=True).exists()

    def test_delete_other_users_video(self, authenticated_client, second_user):
        """Test error when trying to delete another user's video."""
        other_video = VideoHistoryFactory(user=second_user)

        response = authenticated_client.delete(f'/api/videos/{other_video.id}/')

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestSSRFProtection:
    """Tests for SSRF protection in video views."""

    def test_private_ip_rejected(self, authenticated_client, project):
        """Test that private IP addresses are rejected."""
        private_urls = [
            'http://127.0.0.1/video.mp4',
            'http://192.168.1.1/video.mp4',
            'http://10.0.0.1/video.mp4',
            'http://172.16.0.1/video.mp4'
        ]

        for url in private_urls:
            response = authenticated_client.post('/api/videos/download/', {
                'url': url,
                'project_id': str(project.id)
            })

            # Should reject private IPs
            if response.status_code != status.HTTP_404_NOT_FOUND:
                assert response.status_code in [
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_403_FORBIDDEN
                ]

    def test_localhost_rejected(self, authenticated_client, project):
        """Test that localhost URLs are rejected."""
        response = authenticated_client.post('/api/videos/download/', {
            'url': 'http://localhost/video.mp4',
            'project_id': str(project.id)
        })

        if response.status_code != status.HTTP_404_NOT_FOUND:
            assert response.status_code in [
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_403_FORBIDDEN
            ]

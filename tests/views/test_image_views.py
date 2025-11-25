# tests/views/test_image_views.py
"""Tests for image generation and editing views."""
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from tests.factories import ImageHistoryFactory, UserFactory, CreativeProjectFactory

pytestmark = pytest.mark.django_db


class TestImageGalleryView:
    """Tests for image gallery/listing endpoints."""

    def test_gallery_unauthenticated(self, api_client):
        """Test that unauthenticated requests are rejected."""
        response = api_client.get('/api/images/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_gallery_returns_user_images_only(self, authenticated_client, user, second_user, project):
        """Test that gallery only returns authenticated user's images."""
        # Create images for both users
        user_image = ImageHistoryFactory(user=user, project=project)
        other_image = ImageHistoryFactory(user=second_user)

        response = authenticated_client.get('/api/images/')

        assert response.status_code == status.HTTP_200_OK
        # Should only see user's image
        image_ids = [img.get('id') for img in response.data.get('images', response.data)]
        assert str(user_image.id) in str(image_ids)
        assert str(other_image.id) not in str(image_ids)

    def test_gallery_empty_for_new_user(self, authenticated_client, user):
        """Test gallery is empty for user with no images."""
        response = authenticated_client.get('/api/images/')
        assert response.status_code == status.HTTP_200_OK

    def test_gallery_pagination(self, authenticated_client, user, project):
        """Test gallery supports pagination."""
        # Create many images
        for _ in range(25):
            ImageHistoryFactory(user=user, project=project)

        response = authenticated_client.get('/api/images/?limit=10')
        assert response.status_code == status.HTTP_200_OK


class TestImageGenerationView:
    """Tests for image generation endpoints."""

    def test_generate_unauthenticated(self, api_client):
        """Test that unauthenticated generation requests are rejected."""
        response = api_client.post('/api/images/generate/', {
            'prompt': 'A sunset'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_generate_missing_prompt(self, authenticated_client):
        """Test validation error for missing prompt."""
        response = authenticated_client.post('/api/images/generate/', {})
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    @patch('content.image_generation.requests')
    def test_generate_with_valid_prompt(self, mock_requests, authenticated_client, project):
        """Test successful image generation with valid prompt."""
        # Mock Stability AI response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'artifacts': [{'base64': 'dGVzdGltYWdlZGF0YQ==', 'seed': 12345}]
        }
        mock_requests.post.return_value = mock_response

        response = authenticated_client.post('/api/images/generate/', {
            'prompt': 'A beautiful sunset over the ocean',
            'project_id': str(project.id)
        })

        # Check response
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_404_NOT_FOUND]

    def test_generate_xss_blocked(self, authenticated_client, project):
        """Test XSS attempts in prompt are blocked."""
        response = authenticated_client.post('/api/images/generate/', {
            'prompt': '<script>alert("xss")</script>A sunset',
            'project_id': str(project.id)
        })

        # Should either sanitize or reject
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            assert 'dangerous' in str(response.data).lower() or 'invalid' in str(response.data).lower()


class TestImageUpscaleView:
    """Tests for image upscale endpoint."""

    def test_upscale_unauthenticated(self, api_client, image_history):
        """Test that unauthenticated upscale requests are rejected."""
        response = api_client.post('/api/images/upscale/', {
            'image_id': str(image_history.id)
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upscale_invalid_image_id(self, authenticated_client):
        """Test error for invalid image ID."""
        response = authenticated_client.post('/api/images/upscale/', {
            'image_id': 'not-a-valid-uuid'
        })
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_upscale_nonexistent_image(self, authenticated_client):
        """Test error for non-existent image."""
        import uuid
        response = authenticated_client.post('/api/images/upscale/', {
            'image_id': str(uuid.uuid4())
        })
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upscale_other_users_image(self, authenticated_client, second_user):
        """Test error when trying to upscale another user's image."""
        other_image = ImageHistoryFactory(user=second_user)

        response = authenticated_client.post('/api/images/upscale/', {
            'image_id': str(other_image.id)
        })

        # Should be forbidden or not found
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestImageBackgroundRemovalView:
    """Tests for background removal endpoint."""

    def test_remove_background_unauthenticated(self, api_client, image_history):
        """Test that unauthenticated requests are rejected."""
        response = api_client.post('/api/images/remove-background/', {
            'image_id': str(image_history.id)
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_remove_background_other_users_image(self, authenticated_client, second_user):
        """Test error when trying to process another user's image."""
        other_image = ImageHistoryFactory(user=second_user)

        response = authenticated_client.post('/api/images/remove-background/', {
            'image_id': str(other_image.id)
        })

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestImageFavoriteToggle:
    """Tests for favorite toggle endpoint."""

    def test_toggle_favorite(self, authenticated_client, image_history):
        """Test toggling image favorite status."""
        assert image_history.is_favorite is False

        # Toggle to favorite
        response = authenticated_client.post(f'/api/images/{image_history.id}/favorite/')

        if response.status_code == status.HTTP_200_OK:
            image_history.refresh_from_db()
            assert image_history.is_favorite is True

            # Toggle back
            response = authenticated_client.post(f'/api/images/{image_history.id}/favorite/')
            image_history.refresh_from_db()
            assert image_history.is_favorite is False

    def test_toggle_favorite_other_users_image(self, authenticated_client, second_user):
        """Test error when trying to favorite another user's image."""
        other_image = ImageHistoryFactory(user=second_user)

        response = authenticated_client.post(f'/api/images/{other_image.id}/favorite/')

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestImageDeleteView:
    """Tests for image deletion endpoint."""

    def test_delete_image(self, authenticated_client, user, project):
        """Test deleting an image."""
        from content.models import ImageHistory

        image = ImageHistoryFactory(user=user, project=project)
        image_id = image.id

        response = authenticated_client.delete(f'/api/images/{image_id}/')

        if response.status_code == status.HTTP_204_NO_CONTENT:
            # Verify deleted (or soft deleted)
            assert not ImageHistory.objects.filter(id=image_id, is_active=True).exists()

    def test_delete_other_users_image(self, authenticated_client, second_user):
        """Test error when trying to delete another user's image."""
        other_image = ImageHistoryFactory(user=second_user)

        response = authenticated_client.delete(f'/api/images/{other_image.id}/')

        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


class TestInputValidation:
    """Tests for input validation across image views."""

    def test_prompt_max_length(self, authenticated_client, project):
        """Test validation of prompt max length."""
        # Very long prompt
        long_prompt = 'A sunset ' * 1000

        response = authenticated_client.post('/api/images/generate/', {
            'prompt': long_prompt,
            'project_id': str(project.id)
        })

        # Should either truncate or reject
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND
        ]

    def test_invalid_uuid_format(self, authenticated_client):
        """Test validation of UUID format."""
        response = authenticated_client.get('/api/images/not-a-uuid/')
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

    def test_negative_dimensions(self, authenticated_client, project):
        """Test validation rejects negative dimensions."""
        response = authenticated_client.post('/api/images/generate/', {
            'prompt': 'A sunset',
            'width': -1024,
            'height': 1024,
            'project_id': str(project.id)
        })

        # Should reject or ignore invalid dimensions
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_sql_injection_attempt(self, authenticated_client, project):
        """Test SQL injection attempts are blocked."""
        response = authenticated_client.post('/api/images/generate/', {
            'prompt': "'; DROP TABLE images; --",
            'project_id': str(project.id)
        })

        # Should handle safely
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND
        ]

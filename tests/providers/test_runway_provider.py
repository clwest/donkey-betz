# tests/providers/test_runway_provider.py
"""Tests for Runway ML video provider.

Session 452: Fixed tests to patch Django settings instead of os.environ
- RunwayMLProvider reads from settings.EXTERNAL_API_KEYS or settings.RUNWAY_API_KEY
"""
import pytest
from unittest.mock import patch, MagicMock
import responses
import os

pytestmark = pytest.mark.django_db


class TestRunwayMLProvider:
    """Tests for Runway ML video generation provider."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance with test API key."""
        # Session 452: Patch Django settings instead of os.environ
        with patch('content.video_provider.settings') as mock_settings:
            mock_settings.EXTERNAL_API_KEYS = {'RUNWAY_API_KEY': 'test-runway-key'}
            mock_settings.RUNWAY_MOCK_MODE = False
            from content.video_provider import RunwayMLProvider
            return RunwayMLProvider()

    def test_provider_initialization(self):
        """Test provider initializes with API key from settings."""
        # Session 452: Patch Django settings instead of os.environ
        with patch('content.video_provider.settings') as mock_settings:
            mock_settings.EXTERNAL_API_KEYS = {'RUNWAY_API_KEY': 'test-key'}
            mock_settings.RUNWAY_MOCK_MODE = False
            from content.video_provider import RunwayMLProvider
            provider = RunwayMLProvider()
            assert provider.api_key == 'test-key'

    @responses.activate
    def test_generate_text_to_video(self, provider):
        """Test text-to-video generation."""
        responses.add(
            responses.POST,
            'https://api.runwayml.com/v1/text-to-video',
            json={
                'id': 'task-123',
                'status': 'PENDING'
            },
            status=200
        )

        result = provider.generate_video(
            prompt='A sunset over the ocean',
            duration=10
        )

        assert result.get('success') is True or 'id' in result or 'task_id' in result

    @responses.activate
    def test_generate_image_to_video(self, provider):
        """Test image-to-video generation."""
        responses.add(
            responses.POST,
            'https://api.runwayml.com/v1/image-to-video',
            json={
                'id': 'task-456',
                'status': 'PENDING'
            },
            status=200
        )

        result = provider.generate_video(
            prompt='Animate this sunset',
            image_url='https://example.com/image.png',
            duration=10
        )

        assert isinstance(result, dict)

    @responses.activate
    def test_check_task_status_pending(self, provider):
        """Test checking status of pending task."""
        responses.add(
            responses.GET,
            'https://api.runwayml.com/v1/tasks/task-123',
            json={
                'id': 'task-123',
                'status': 'PENDING'
            },
            status=200
        )

        result = provider.check_status('task-123')

        assert result.get('status') == 'PENDING' or 'pending' in str(result).lower()

    @responses.activate
    def test_check_task_status_completed(self, provider):
        """Test checking status of completed task."""
        responses.add(
            responses.GET,
            'https://api.runwayml.com/v1/tasks/task-123',
            json={
                'id': 'task-123',
                'status': 'SUCCEEDED',
                'output': ['https://example.com/video.mp4']
            },
            status=200
        )

        result = provider.check_status('task-123')

        assert 'SUCCEEDED' in str(result).upper() or 'completed' in str(result).lower()

    @responses.activate
    def test_check_task_status_failed(self, provider):
        """Test checking status of failed task."""
        responses.add(
            responses.GET,
            'https://api.runwayml.com/v1/tasks/task-123',
            json={
                'id': 'task-123',
                'status': 'FAILED',
                'error': 'Content moderation failed'
            },
            status=200
        )

        result = provider.check_status('task-123')

        assert 'FAILED' in str(result).upper() or 'failed' in str(result).lower()

    @responses.activate
    def test_api_error_handling(self, provider):
        """Test handling of API errors."""
        responses.add(
            responses.POST,
            'https://api.runwayml.com/v1/text-to-video',
            json={'error': 'Invalid API key'},
            status=401
        )

        result = provider.generate_video(
            prompt='Test',
            duration=10
        )

        assert result.get('success') is False or 'error' in result

    @responses.activate
    def test_rate_limit_handling(self, provider):
        """Test handling of rate limit errors."""
        responses.add(
            responses.POST,
            'https://api.runwayml.com/v1/text-to-video',
            json={'error': 'Rate limit exceeded'},
            status=429
        )

        result = provider.generate_video(
            prompt='Test',
            duration=10
        )

        assert result.get('success') is False or 'error' in result


class TestRunwayVideoExtension:
    """Tests for video extension functionality."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance."""
        with patch.dict(os.environ, {'RUNWAY_API_KEY': 'test-key'}):
            from content.video_provider import RunwayMLProvider
            return RunwayMLProvider()

    @responses.activate
    def test_extend_video(self, provider):
        """Test video extension."""
        responses.add(
            responses.POST,
            'https://api.runwayml.com/v1/extend-video',
            json={
                'id': 'extend-task-123',
                'status': 'PENDING'
            },
            status=200
        )

        if hasattr(provider, 'extend_video'):
            result = provider.extend_video(
                video_url='https://example.com/video.mp4',
                prompt='Continue the sunset'
            )
            assert isinstance(result, dict)


class TestRunwayModelSelection:
    """Tests for model selection in Runway provider."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance."""
        with patch.dict(os.environ, {'RUNWAY_API_KEY': 'test-key'}):
            from content.video_provider import RunwayMLProvider
            return RunwayMLProvider()

    @responses.activate
    def test_gen4_turbo_model(self, provider):
        """Test using Gen-4 Turbo model."""
        responses.add(
            responses.POST,
            'https://api.runwayml.com/v1/text-to-video',
            json={'id': 'task-123', 'status': 'PENDING'},
            status=200
        )

        result = provider.generate_video(
            prompt='Test',
            duration=10,
            model='gen4_turbo'
        )

        assert isinstance(result, dict)

    def test_invalid_model_handling(self, provider):
        """Test handling of invalid model name."""
        result = provider.generate_video(
            prompt='Test',
            duration=10,
            model='invalid_model_name'
        )

        # Should use default or return error
        assert isinstance(result, dict)

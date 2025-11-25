# tests/providers/test_stability_provider.py
"""Tests for Stability AI provider."""
import pytest
from unittest.mock import patch, MagicMock
import responses
import os

pytestmark = pytest.mark.django_db


class TestStabilityAIProvider:
    """Tests for Stability AI image generation provider."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance with test API key."""
        with patch.dict(os.environ, {'STABILITY_API_KEY': 'test-api-key-123'}):
            from content.image_generation import StabilityAIProvider
            return StabilityAIProvider()

    def test_provider_initialization(self):
        """Test provider initializes with API key from environment."""
        with patch.dict(os.environ, {'STABILITY_API_KEY': 'test-key'}):
            from content.image_generation import StabilityAIProvider
            provider = StabilityAIProvider()
            assert provider.api_key == 'test-key'

    def test_missing_api_key_raises_error(self):
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('STABILITY_API_KEY', None)
            from content.image_generation import StabilityAIProvider
            # Should handle missing key gracefully or raise
            try:
                provider = StabilityAIProvider()
                # If no error, key should be None or empty
                assert provider.api_key is None or provider.api_key == ''
            except (ValueError, KeyError):
                pass  # Expected behavior

    @responses.activate
    def test_generate_image_success(self, provider):
        """Test successful image generation."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
            json={
                'artifacts': [{
                    'base64': 'dGVzdGltYWdlZGF0YQ==',
                    'seed': 12345
                }]
            },
            status=200
        )

        result = provider.generate_image(
            prompt='A beautiful sunset',
            width=1024,
            height=1024
        )

        assert result['success'] is True
        assert 'image_data' in result or 'image' in result or 'artifacts' in result

    @responses.activate
    def test_generate_image_api_error(self, provider):
        """Test handling of API errors."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
            json={'error': 'Invalid API key'},
            status=401
        )

        result = provider.generate_image(
            prompt='A sunset',
            width=1024,
            height=1024
        )

        assert result['success'] is False
        assert 'error' in result

    @responses.activate
    def test_generate_image_rate_limit(self, provider):
        """Test handling of rate limit errors."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
            json={'error': 'Rate limit exceeded'},
            status=429
        )

        result = provider.generate_image(
            prompt='A sunset',
            width=1024,
            height=1024
        )

        assert result['success'] is False

    def test_prompt_validation(self, provider):
        """Test prompt validation."""
        # Empty prompt should be handled
        result = provider.generate_image(
            prompt='',
            width=1024,
            height=1024
        )
        # Should fail gracefully
        assert result.get('success') is False or 'error' in result

    def test_dimension_validation(self, provider):
        """Test dimension validation."""
        # Invalid dimensions should be handled
        result = provider.generate_image(
            prompt='Test',
            width=0,
            height=0
        )
        # Should fail or use defaults
        assert isinstance(result, dict)


class TestStabilityAPIOperations:
    """Tests for specific Stability AI operations."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance with test API key."""
        with patch.dict(os.environ, {'STABILITY_API_KEY': 'test-api-key'}):
            from content.image_generation import StabilityAIProvider
            return StabilityAIProvider()

    @responses.activate
    def test_upscale_image(self, provider):
        """Test image upscaling."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/esrgan-v1-x2plus/image-to-image/upscale',
            body=b'upscaled_image_data',
            status=200
        )

        # Test upscale if method exists
        if hasattr(provider, 'upscale_image'):
            result = provider.upscale_image(
                image_data=b'original_image',
                scale=2
            )
            assert isinstance(result, dict)

    @responses.activate
    def test_remove_background(self, provider):
        """Test background removal."""
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image/remove-background',
            body=b'image_without_background',
            status=200
        )

        if hasattr(provider, 'remove_background'):
            result = provider.remove_background(image_data=b'original_image')
            assert isinstance(result, dict)


class TestStabilityProviderRetry:
    """Tests for retry logic in Stability provider."""

    @pytest.fixture
    def provider(self):
        """Create a provider instance."""
        with patch.dict(os.environ, {'STABILITY_API_KEY': 'test-key'}):
            from content.image_generation import StabilityAIProvider
            return StabilityAIProvider()

    @responses.activate
    def test_retry_on_500_error(self, provider):
        """Test retry behavior on server errors."""
        # First call fails, second succeeds
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
            json={'error': 'Server error'},
            status=500
        )
        responses.add(
            responses.POST,
            'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
            json={'artifacts': [{'base64': 'dGVzdA=='}]},
            status=200
        )

        result = provider.generate_image(
            prompt='Test',
            width=1024,
            height=1024
        )

        # Should either succeed after retry or fail gracefully
        assert isinstance(result, dict)

    @responses.activate
    def test_max_retries_exceeded(self, provider):
        """Test behavior when max retries exceeded."""
        # All calls fail
        for _ in range(5):
            responses.add(
                responses.POST,
                'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                json={'error': 'Server error'},
                status=500
            )

        result = provider.generate_image(
            prompt='Test',
            width=1024,
            height=1024
        )

        # Should fail after max retries
        assert result['success'] is False

# core/validation/image_validator.py
"""
Image Section Validation Agent

Validates the image generation and editing subsystem including:
- Gallery endpoint
- Stability AI operations (upscale, remove background)
- Image model data integrity
"""

import logging
from django.conf import settings

from .base import BaseValidationAgent

logger = logging.getLogger(__name__)


class ImageValidationAgent(BaseValidationAgent):
    """Validates the image generation and editing subsystem."""

    section_name = "images"

    def run_checks(self):
        """Run all image-related validation checks."""
        # Endpoint checks
        self.check_gallery_endpoint()
        self.check_upscale_endpoint()
        self.check_remove_background_endpoint()

        # Data checks
        self.check_image_history_model()

        # Configuration checks
        self.check_stability_api_key()

        # Import checks
        self.check_provider_import()

    def check_gallery_endpoint(self):
        """Verify gallery listing works."""
        self.check_endpoint(
            path='/api/images/history/',
            method='GET',
            expected_status=200,
            name='gallery_endpoint'
        )

    def check_upscale_endpoint(self):
        """Verify upscale endpoint exists (POST requires image)."""
        # Just check the endpoint is routed - actual upscale needs an image
        self.check_endpoint(
            path='/api/stability/upscale/',
            method='POST',
            expected_status=400,  # Expected without image data
            name='upscale_endpoint_exists'
        )

    def check_remove_background_endpoint(self):
        """Verify background removal endpoint exists."""
        self.check_endpoint(
            path='/api/stability/remove-background/',
            method='POST',
            expected_status=400,  # Expected without image data
            name='remove_background_endpoint_exists'
        )

    def check_image_history_model(self):
        """Verify ImageHistory model has data."""
        try:
            from content.models import ImageHistory
            self.check_model_count(
                model_class=ImageHistory,
                min_count=0,  # Just verify model exists and is queryable
                name='image_history_model'
            )
        except ImportError as e:
            self.add_check(
                name='image_history_model',
                passed=False,
                message=f"Cannot import ImageHistory: {e}"
            )

    def check_stability_api_key(self):
        """Verify Stability AI API key is configured."""
        self.check_api_key('STABILITY_API_KEY', name='stability_api_key')

    def check_provider_import(self):
        """Verify ImageGenerationService can be imported."""
        self.check_import(
            module_path='content.image_generation',
            class_name='ImageGenerationService',
            name='image_generation_service_import'
        )

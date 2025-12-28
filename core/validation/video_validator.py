# core/validation/video_validator.py
"""
Video Section Validation Agent

Validates the video generation and editing subsystem including:
- Video history endpoint
- Text-to-video generation
- Video editing operations (trim, speed, effects)
- Runway ML integration
"""

import logging

from .base import BaseValidationAgent

logger = logging.getLogger(__name__)


class VideoValidationAgent(BaseValidationAgent):
    """Validates the video generation and editing subsystem."""

    section_name = "videos"

    def run_checks(self):
        """Run all video-related validation checks."""
        # Endpoint checks
        self.check_video_history_endpoint()
        self.check_text_to_video_endpoint()
        self.check_video_editing_endpoints()

        # Data checks
        self.check_video_model()

        # Configuration checks
        self.check_runway_api_key()

        # Import checks
        self.check_provider_import()

    def check_video_history_endpoint(self):
        """Verify video history listing works."""
        self.check_endpoint(
            path='/api/v1/video/history/',
            method='GET',
            expected_status=200,
            name='video_history_endpoint'
        )

    def check_text_to_video_endpoint(self):
        """Verify text-to-video endpoint exists."""
        # POST without proper data should return 400
        self.check_endpoint(
            path='/api/v1/video/text-to-video/',
            method='POST',
            expected_status=400,
            name='text_to_video_endpoint_exists'
        )

    def check_video_editing_endpoints(self):
        """Verify video editing endpoints exist."""
        editing_endpoints = [
            '/api/video/trim/',
            '/api/video/speed/',
            '/api/video/effects/',
        ]

        for endpoint in editing_endpoints:
            name = f"video_edit_{endpoint.split('/')[-2]}"
            self.check_endpoint(
                path=endpoint,
                method='POST',
                expected_status=400,  # Expected without video data
                name=name
            )

    def check_video_model(self):
        """Verify VideoHistory model exists and is queryable."""
        try:
            from content.models import VideoHistory
            self.check_model_count(
                model_class=VideoHistory,
                min_count=0,
                name='video_history_model'
            )
        except ImportError as e:
            self.add_check(
                name='video_history_model',
                passed=False,
                message=f"Cannot import VideoHistory: {e}"
            )

    def check_runway_api_key(self):
        """Verify Runway ML API key is configured."""
        self.check_api_key('RUNWAY_API_KEY', name='runway_api_key')

    def check_provider_import(self):
        """Verify RunwayMLProvider can be imported."""
        self.check_import(
            module_path='content.video_provider',
            class_name='RunwayMLProvider',
            name='runway_provider_import'
        )

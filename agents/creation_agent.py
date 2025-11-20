"""
Creation Agent - Session 134

Specialized agent for standard image generation using Stability AI.
Wraps the existing gallery_generate view for consistent agent-based architecture.

Architecture:
    AI Assistant (detects intent) → Creation Agent → gallery_generate view → Stability AI API
"""

import logging
import json
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()
logger = logging.getLogger(__name__)


class CreationAgent:
    """
    Specialized agent for standard image generation via Stability AI.

    Responsibilities:
        - Generate images using Stability AI models
        - Handle quality presets (fast, balanced, high, premium)
        - Support style presets (69 available!)
        - Associate generated images with projects
        - Track agent contributions
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Creation Agent.

        Args:
            user: User requesting image generation
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Creation Agent"

    def execute(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute standard image generation.

        Args:
            prompt: Text description of the image to generate
            **kwargs: Additional generation parameters
                - size: Image size (default: '1024x1024')
                - style: Visual style preset
                - negative_prompt: What to avoid
                - num_images: Number of images (default: 1)
                - quality: 'fast', 'balanced', 'high', 'premium'

        Returns:
            Dict with success status and generation results
        """
        logger.info(f"🚀🚀🚀 CREATION AGENT EXECUTE CALLED")
        logger.info(f"🤖 {self.agent_name} starting image generation")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Prompt: {prompt[:80]}...")
        logger.info(f"   Project ID: {self.project_id or 'None'}")
        logger.info(f"   Kwargs: {kwargs}")

        try:
            # Extract parameters
            size = kwargs.get('size', '1024x1024')
            style = kwargs.get('style', 'photorealistic')
            negative_prompt = kwargs.get('negative_prompt', None)
            num_images = kwargs.get('num_images', 1)
            quality = kwargs.get('quality', 'balanced')
            session_id = kwargs.get('session_id')

            # Parse size into width/height
            if 'x' in size:
                width, height = map(int, size.split('x'))
            else:
                width = height = int(size)

            logger.info(f"🚀 Generating {num_images} image(s) with quality: {quality}")

            # Call gallery_generate view using RequestFactory
            factory = RequestFactory()
            request_data = {
                'prompt': prompt,
                'width': width,
                'height': height,
                'num_images': num_images,
                'quality': quality,
                'style': style,
                'agent_name': self.agent_name  # Session 137: Pass agent name for attribution
            }

            if negative_prompt:
                request_data['negative_prompt'] = negative_prompt
            if self.project_id:
                request_data['project_id'] = self.project_id
            if session_id:
                request_data['session_id'] = session_id

            request = factory.post('/api/gallery/generate/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user
            request._dont_enforce_csrf_checks = True

            # Call the view
            from core.views_image import gallery_generate
            response = gallery_generate(request)

            # Session 137: Add detailed error logging
            logger.info(f"📦 gallery_generate response status: {response.status_code}")
            logger.info(f"📦 gallery_generate response type: {type(response)}")

            # Parse response
            if hasattr(response, 'data'):
                result = response.data
                logger.info(f"📦 Response data: {result}")
            else:
                logger.error(f"❌ Response has no 'data' attribute! Response: {response}")
                logger.error(f"❌ Response content: {getattr(response, 'content', 'No content')}")
                raise Exception(f"gallery_generate returned invalid response: {response}")

            if result.get('success'):
                image_ids = [img['id'] for img in result.get('images', [])]
                logger.info(f"✅ {self.agent_name} completed successfully!")
                logger.info(f"   Generated: {len(image_ids)} image(s)")

                return {
                    'success': True,
                    'message': f"✨ Generated {len(image_ids)} image(s). Check your project gallery!",
                    'image_ids': image_ids
                }
            else:
                error_msg = result.get('error', 'Image generation failed')
                logger.error(f"❌ {self.agent_name} generation failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

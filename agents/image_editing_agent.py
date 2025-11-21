"""
Image Editing Agent - Session 128

Specialized agent for image editing operations using Stability AI.
Handles upscale, background removal, variations, object erasure, recoloring, and refinement.

Architecture:
    AI Assistant (detects intent) → Image Editing Agent → Wrapper Views → Stability AI API
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.test import RequestFactory
import json

from content.models import ImageHistory

User = get_user_model()
logger = logging.getLogger(__name__)


class ImageEditingAgent:
    """
    Specialized agent for image editing operations.

    Responsibilities:
        - Validate source images
        - Route to appropriate editing operation
        - Call Stability AI through wrapper views
        - Handle results and errors
        - Associate edited images with projects
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Image Editing Agent.

        Args:
            user: User requesting image editing
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Image Editing Agent"

    def execute(
        self,
        operation: str,
        image_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an image editing operation.

        Args:
            operation: Type of operation ('upscale', 'remove_background', 'variations',
                      'recolor', 'search_and_replace', 'creative_upscale')
            image_id: UUID or sequential number of the image to edit
            **kwargs: Operation-specific parameters

        Returns:
            Dict with success status and operation results
        """
        logger.info(f"🤖 {self.agent_name} starting {operation} workflow")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Image ID: {image_id}")
        logger.info(f"   Operation: {operation}")

        try:
            # Step 1: Validate and resolve image ID
            image = self._resolve_image_id(image_id)
            if not image:
                return {
                    'success': False,
                    'error': f'Image {image_id} not found for user {self.user.username}'
                }

            seq_num = image.get_sequential_number()
            logger.info(f"✅ Image validated: #{seq_num} ({image.id})")
            logger.info(f"   Prompt: {image.prompt[:60] if image.prompt else 'No prompt'}...")

            # Step 2: Route to appropriate operation
            operation_map = {
                'upscale': self._upscale,
                'remove_background': self._remove_background,
                'variations': self._create_variations,
                # 'erase_object': self._erase_object,  # Deprecated: use search_and_replace with empty replace_prompt
                'recolor': self._recolor,
                # 'refine': self._refine,  # TODO: No backend implementation
                'search_and_replace': self._search_and_replace,  # Session 151 - also handles erasure
                'creative_upscale': self._creative_upscale  # Session 151
            }

            if operation not in operation_map:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }

            logger.info(f"🚀 Executing {operation} operation...")

            # Execute the operation
            result = operation_map[operation](str(image.id), **kwargs)

            if result.get('success'):
                logger.info(f"✅ {self.agent_name} {operation} completed successfully")
            else:
                logger.error(f"❌ {self.agent_name} {operation} failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _upscale(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Upscale image to 4x resolution."""
        try:
            from core.views_image import upscale_image_view

            factory = RequestFactory()
            request_data = {'image_id': image_id}
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/upscale/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = upscale_image_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Successfully upscaling image to 4x resolution. Result will appear in gallery shortly (~30 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Upscale operation failed')
                }

        except Exception as e:
            logger.error(f"❌ Upscale operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to upscale image: {str(e)}"
            }

    def _remove_background(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Remove background from image."""
        try:
            from core.views_image import remove_background_view

            factory = RequestFactory()
            request_data = {'image_id': image_id}
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/remove-background/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = remove_background_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Successfully removed background. Result will appear in gallery shortly (~20 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Background removal failed')
                }

        except Exception as e:
            logger.error(f"❌ Remove background operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to remove background: {str(e)}"
            }

    def _create_variations(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Create variations of an image."""
        try:
            from core.views_image import create_variations_view

            count = kwargs.get('count', 3)
            prompt = kwargs.get('prompt', 'creative variation')

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'count': count,
                'prompt': prompt
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/create-variations/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = create_variations_view(request)
            result = json.loads(response.content)

            if result.get('success'):
                # Extract image IDs from the images array
                images = result.get('images', [])
                image_ids = [img['image_id'] for img in images]

                return {
                    'success': True,
                    'message': f"✨ Created {len(image_ids)} variations successfully! Check your gallery.",
                    'image_ids': image_ids
                }
            else:
                error_msg = result.get('error', 'Variation creation failed')
                logger.error(f"❌ Create variations backend error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }

        except Exception as e:
            logger.error(f"❌ Create variations operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to create variations: {str(e)}"
            }

    def _erase_object(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Erase specific objects from an image."""
        try:
            from core.views_image import erase_object

            search_prompt = kwargs.get('search_prompt')
            if not search_prompt:
                return {
                    'success': False,
                    'error': 'search_prompt is required for erase_object operation'
                }

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'search_prompt': search_prompt
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/erase/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = erase_object(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Erasing '{search_prompt}' from image. Result will appear in gallery shortly (~30 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Object erasure failed')
                }

        except Exception as e:
            logger.error(f"❌ Erase object operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to erase object: {str(e)}"
            }

    def _recolor(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Recolor objects or entire image."""
        try:
            from core.views_image import recolor_image_view

            prompt = kwargs.get('prompt')
            select_prompt = kwargs.get('select_prompt')

            if not prompt:
                return {
                    'success': False,
                    'error': 'prompt is required for recolor operation'
                }

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'prompt': prompt
            }
            if select_prompt:
                request_data['select_prompt'] = select_prompt
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/recolor-image/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = recolor_image_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                target = select_prompt if select_prompt else "entire image"
                return {
                    'success': True,
                    'message': f"✨ Recoloring {target}. Result will appear in gallery shortly (~30 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Recoloring failed')
                }

        except Exception as e:
            logger.error(f"❌ Recolor operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to recolor image: {str(e)}"
            }

    def _refine(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Refine/enhance image quality."""
        try:
            from core.views_image import refine_image_view

            prompt = kwargs.get('prompt', 'enhance quality and details')

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'prompt': prompt
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/refine-image/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = refine_image_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Refining image. Result will appear in gallery shortly (~40 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Refinement failed')
                }

        except Exception as e:
            logger.error(f"❌ Refine operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to refine image: {str(e)}"
            }

    def _search_and_replace(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Search and replace objects in image with AI precision."""
        try:
            from core.views_image import search_and_replace_view

            search_prompt = kwargs.get('search_prompt')
            replace_prompt = kwargs.get('replace_prompt', '')

            if not search_prompt:
                return {
                    'success': False,
                    'error': 'search_prompt is required for search_and_replace operation'
                }

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'search_prompt': search_prompt,
                'replace_prompt': replace_prompt
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/search-and-replace/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = search_and_replace_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                action = "removed" if not replace_prompt else "replaced"
                target = search_prompt
                replacement = f" with '{replace_prompt}'" if replace_prompt else ""
                return {
                    'success': True,
                    'message': f"✨ Successfully {action} '{target}'{replacement}. Result will appear in gallery shortly (~30 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Search and replace operation failed')
                }

        except Exception as e:
            logger.error(f"❌ Search and replace operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to search and replace: {str(e)}"
            }

    def _creative_upscale(self, image_id: str, **kwargs) -> Dict[str, Any]:
        """Creative upscale with prompt - adds AI-generated details while upscaling."""
        try:
            from core.views_image import creative_upscale_view

            prompt = kwargs.get('prompt')
            creativity = kwargs.get('creativity', 0.3)

            if not prompt:
                return {
                    'success': False,
                    'error': 'prompt is required for creative_upscale operation'
                }

            factory = RequestFactory()
            request_data = {
                'image_id': image_id,
                'prompt': prompt,
                'creativity': creativity
            }
            if self.project_id:
                request_data['project_id'] = self.project_id

            request = factory.post('/api/stability/creative-upscale/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user

            response = creative_upscale_view(request)
            result = json.loads(response.content)

            if result.get('success') or result.get('image_id'):
                return {
                    'success': True,
                    'message': f"✨ Creative upscale complete! Enhanced image with: '{prompt}'. Result will appear in gallery shortly (~40 seconds).",
                    'image_id': result.get('image_id')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Creative upscale operation failed')
                }

        except Exception as e:
            logger.error(f"❌ Creative upscale operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to creative upscale image: {str(e)}"
            }

    def _resolve_image_id(self, image_id: str) -> Optional[ImageHistory]:
        """
        Resolve image ID (UUID or sequential number) to ImageHistory object.

        Args:
            image_id: UUID string or sequential number as string

        Returns:
            ImageHistory object or None if not found
        """
        try:
            # Try UUID first
            return ImageHistory.objects.get(id=image_id, user=self.user)
        except (ValueError, ImageHistory.DoesNotExist, Exception):  # Session 137: Catch all exceptions including ValidationError
            # Try sequential number
            try:
                seq_num = int(image_id)
                images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                if seq_num > 0 and seq_num <= images.count():
                    return images[seq_num - 1]
            except (ValueError, IndexError):
                pass

        return None

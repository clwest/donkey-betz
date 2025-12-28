"""
3D Generation Agent - Session 128

Specialized agent for converting 2D images into 3D models using Replicate TRELLIS.
Handles the complete workflow: image validation → 3D generation → file download → STL conversion.

Architecture:
    AI Assistant (detects intent) → 3D Generation Agent → MiniFig Service → Replicate API
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model

from content.models import ImageHistory, MiniFigAsset
from content.minifig_services import create_minifig_asset_from_images, check_and_update_3d_generation

User = get_user_model()
logger = logging.getLogger(__name__)


class ThreeDGenerationAgent:
    """
    Specialized agent for 3D model generation from images.

    Responsibilities:
        - Validate source image exists and belongs to user
        - Create 3D generation job with Replicate
        - Monitor generation progress
        - Auto-download GLB and convert to STL
        - Report status and provide downloadable files
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize 3D Generation Agent.

        Args:
            user: User requesting 3D generation
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "3D Generation Agent"

    def execute(self, image_id: str, style: str = 'toy', scale: str = 'medium') -> Dict[str, Any]:
        """
        Convert a 2D image to a 3D model.

        Args:
            image_id: UUID or sequential number of the image to convert
            style: 3D model style (toy, realistic, etc.)
            scale: 3D model scale (small, medium, large)

        Returns:
            Dict with success status, asset_id, and file URLs
        """
        logger.info(f"🤖 {self.agent_name} starting 3D generation workflow")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Image ID: {image_id}")
        logger.info(f"   Style: {style} | Scale: {scale}")

        try:
            # Step 1: Validate and resolve image ID
            image = self._resolve_image_id(image_id)
            if not image:
                return {
                    'success': False,
                    'error': f'Image {image_id} not found for user {self.user.username}'
                }

            logger.info(f"✅ Image validated: {image.id}")
            logger.info(f"   Prompt: {image.prompt[:60] if image.prompt else 'No prompt'}...")

            # Step 2: Create 3D generation job
            logger.info(f"🚀 Creating 3D generation job with Replicate TRELLIS...")
            minifig_assets = create_minifig_asset_from_images(
                user=self.user,
                image_asset_ids=[str(image.id)],
                provider='replicate',
                style=style,
                scale=scale,
                project_id=self.project_id  # Session 137: Pass project_id
            )

            if not minifig_assets:
                return {
                    'success': False,
                    'error': '3D generation job creation failed'
                }

            minifig = minifig_assets[0]
            asset_id = str(minifig.id)
            prediction_id = minifig.metadata.get('prediction_id', 'unknown')

            logger.info(f"✅ 3D generation job created")
            logger.info(f"   Asset ID: {asset_id}")
            logger.info(f"   Prediction ID: {prediction_id}")
            logger.info(f"   Status: {minifig.status}")

            # Step 3: Monitor generation (non-blocking - frontend will poll)
            logger.info(f"⏳ 3D generation submitted to Replicate")
            logger.info(f"   Estimated time: 45-60 seconds")
            logger.info(f"   Frontend will poll for completion")

            return {
                'success': True,
                'asset_id': asset_id,
                'status': minifig.status,
                'prediction_id': prediction_id,
                'estimated_time_seconds': 60,
                'message': f'3D generation started for image {image_id}. Files will auto-download when complete.'
            }

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def check_status(self, asset_id: str) -> Dict[str, Any]:
        """
        Check the status of a 3D generation job.

        Args:
            asset_id: MiniFigAsset UUID

        Returns:
            Dict with status, file URLs, and completion info
        """
        logger.info(f"🔍 {self.agent_name} checking status for asset {asset_id}")

        try:
            # Update status from Replicate and download files if ready
            minifig = check_and_update_3d_generation(asset_id)

            result = {
                'success': True,
                'asset_id': asset_id,
                'status': minifig.status,
            }

            if minifig.status == 'completed':
                logger.info(f"✅ 3D generation completed!")
                logger.info(f"   GLB file: {minifig.glb_file.url if minifig.glb_file else 'None'}")
                logger.info(f"   STL file: {minifig.stl_file.url if minifig.stl_file else 'None'}")

                result['glb_url'] = minifig.glb_file.url if minifig.glb_file else None
                result['stl_url'] = minifig.stl_file.url if minifig.stl_file else None
                result['message'] = '3D model ready! Download GLB for viewing or STL for 3D printing.'

            elif minifig.status == 'failed':
                logger.error(f"❌ 3D generation failed: {minifig.error_message if hasattr(minifig, 'error_message') else 'Unknown error'}")
                result['error'] = minifig.error_message if hasattr(minifig, 'error_message') else 'Generation failed'

            elif minifig.status in ['pending', 'processing']:
                logger.info(f"⏳ Still processing on Replicate...")
                result['message'] = 'Still generating 3D model on Replicate...'

            return result

        except MiniFigAsset.DoesNotExist:
            logger.error(f"❌ Asset {asset_id} not found")
            return {
                'success': False,
                'error': f'Asset {asset_id} not found'
            }
        except Exception as e:
            logger.error(f"❌ Status check failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
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
        except (ValueError, ImageHistory.DoesNotExist, Exception):  # Session 129: Catch all exceptions including ValidationError
            # Try sequential number
            try:
                seq_num = int(image_id)
                images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                if seq_num > 0 and seq_num <= images.count():
                    return images[seq_num - 1]
            except (ValueError, IndexError):
                pass

        return None

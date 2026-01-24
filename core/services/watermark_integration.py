"""
Watermark Integration Service
=============================

Session 487: Integrates invisible watermarking into the image generation pipeline.

This module provides helper functions that automatically:
1. Embed creator attribution watermarks into generated images
2. Create provenance records for tracking
3. Return watermarked bytes ready for storage

Usage:
    from core.services.watermark_integration import watermark_image_bytes, save_watermarked_image

    # Apply watermark to image bytes
    watermarked_bytes, provenance_id = watermark_image_bytes(
        image_bytes=raw_bytes,
        user=request.user,
        generation_params={'prompt': 'A cat', 'model': 'sdxl'}
    )

    # Or use the all-in-one save helper
    file_path = save_watermarked_image(
        image_bytes=raw_bytes,
        filename='generated_image.png',
        user=request.user,
        generation_params={'prompt': 'A cat'}
    )
"""

import logging
import uuid
from typing import Optional, Tuple, Dict, Any

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

logger = logging.getLogger(__name__)

# Feature flag - can be disabled in settings if needed
WATERMARK_ENABLED = getattr(settings, 'WATERMARK_ENABLED', True)


def watermark_image_bytes(
    image_bytes: bytes,
    user,
    generation_params: Optional[Dict[str, Any]] = None,
    image_history=None
) -> Tuple[bytes, Optional[str]]:
    """
    Apply invisible watermark to image bytes.

    Args:
        image_bytes: Raw image bytes (PNG, JPEG, etc.)
        user: Django User object (creator)
        generation_params: Dict of generation parameters (prompt, model, etc.)
        image_history: Optional ImageHistory instance (for provenance linking)

    Returns:
        Tuple of (watermarked_bytes, provenance_id)
        If watermarking fails, returns (original_bytes, None)
    """
    if not WATERMARK_ENABLED:
        logger.debug("Watermarking disabled via settings")
        return image_bytes, None

    if not image_bytes:
        logger.warning("No image bytes provided for watermarking")
        return image_bytes, None

    try:
        from core.services.watermark_service import WatermarkService
        from core.services.provenance_service import ProvenanceService

        # Generate a provenance ID for this image
        provenance_id = str(uuid.uuid4())
        creator_id = str(user.id) if user else 'anonymous'

        # Create watermark service and embed
        watermark_service = WatermarkService()
        result = watermark_service.embed_watermark(
            image_bytes=image_bytes,
            creator_id=creator_id,
            provenance_id=provenance_id,
            metadata={
                'prompt': generation_params.get('prompt', '')[:200] if generation_params else '',
                'model': generation_params.get('model_used', generation_params.get('model', '')) if generation_params else '',
                'username': user.username if user else 'anonymous',
            }
        )

        if result.success and result.image_bytes:
            logger.info(
                f"Watermark embedded: creator={creator_id[:8]}..., "
                f"provenance={provenance_id[:8]}..., "
                f"size={len(image_bytes)} -> {len(result.image_bytes)} bytes"
            )

            # Optionally create provenance record in database
            if image_history:
                try:
                    provenance_service = ProvenanceService()
                    provenance_service.create_provenance(
                        image_history=image_history,
                        user=user,
                        image_bytes=result.image_bytes,
                        generation_params=generation_params
                    )
                except Exception as prov_error:
                    logger.warning(f"Provenance record creation failed (non-fatal): {prov_error}")

            return result.image_bytes, provenance_id
        else:
            logger.warning(f"Watermark embedding failed: {result.error}")
            return image_bytes, None

    except ImportError as ie:
        logger.error(f"Watermark service not available: {ie}")
        return image_bytes, None
    except Exception as e:
        logger.error(f"Watermark integration error: {e}")
        # Return original bytes on failure - don't break image generation
        return image_bytes, None


def save_watermarked_image(
    image_bytes: bytes,
    filename: str,
    user,
    generation_params: Optional[Dict[str, Any]] = None,
    upload_to_cloud: bool = True
) -> str:
    """
    Apply watermark and save image to storage in one step.

    Session 800: Added Cloudinary upload for production persistence.
    Images are uploaded to Cloudinary when CLOUDINARY_API_KEY is set,
    ensuring they survive Railway's ephemeral filesystem.

    Args:
        image_bytes: Raw image bytes
        filename: Desired filename (e.g., 'generated_abc123.png')
        user: Django User object
        generation_params: Dict of generation parameters
        upload_to_cloud: Whether to upload to Cloudinary (default True)

    Returns:
        file_path: Path or URL where the watermarked image was saved
                  Returns Cloudinary URL if cloud upload succeeds,
                  otherwise returns local file path.
    """
    import os

    # Apply watermark
    watermarked_bytes, provenance_id = watermark_image_bytes(
        image_bytes=image_bytes,
        user=user,
        generation_params=generation_params
    )

    # Save to local storage first (for immediate access and backup)
    file_path = default_storage.save(filename, ContentFile(watermarked_bytes))

    if provenance_id:
        logger.info(f"Saved watermarked image: {file_path} (provenance: {provenance_id[:8]}...)")
    else:
        logger.info(f"Saved image (no watermark): {file_path}")

    # Session 800: Upload to Cloudinary for production persistence
    # This ensures images survive Railway's ephemeral filesystem
    cloudinary_api_key = os.environ.get('CLOUDINARY_API_KEY')
    if upload_to_cloud and cloudinary_api_key:
        try:
            import cloudinary
            import cloudinary.uploader

            # Get the full path to the saved file
            full_path = default_storage.path(file_path)

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                full_path,
                folder="ai-content-studio/generated",
                public_id=filename.replace('/', '_').replace('.png', ''),
                resource_type="image",
                overwrite=True
            )

            cloud_url = upload_result.get('secure_url')
            if cloud_url:
                logger.info(f"☁️ Uploaded to Cloudinary: {cloud_url[:60]}...")
                return cloud_url

        except Exception as cloud_error:
            logger.warning(f"⚠️ Cloudinary upload failed (using local): {cloud_error}")
            # Fall through to return local path

    # Return local path if cloud upload not enabled or failed
    return file_path


def verify_image_ownership(image_bytes: bytes, user) -> Dict[str, Any]:
    """
    Verify if an image was created by a specific user.

    Args:
        image_bytes: Image bytes to verify
        user: User claiming ownership

    Returns:
        Dict with verification results:
        {
            'verified': bool,
            'is_owner': bool,
            'watermark_found': bool,
            'creator_id': str or None,
            'provenance_id': str or None,
            'timestamp': str or None,
            'error': str or None
        }
    """
    try:
        from core.services.watermark_service import WatermarkService

        service = WatermarkService()
        is_owner, watermark_data = service.verify_ownership(
            image_bytes,
            str(user.id)
        )

        if watermark_data:
            return {
                'verified': True,
                'is_owner': is_owner,
                'watermark_found': True,
                'creator_id': watermark_data.get('creator_id'),
                'provenance_id': watermark_data.get('provenance_id'),
                'timestamp': watermark_data.get('timestamp'),
                'error': None
            }
        else:
            return {
                'verified': True,
                'is_owner': False,
                'watermark_found': False,
                'creator_id': None,
                'provenance_id': None,
                'timestamp': None,
                'error': 'No watermark found in image'
            }

    except Exception as e:
        logger.error(f"Ownership verification failed: {e}")
        return {
            'verified': False,
            'is_owner': False,
            'watermark_found': False,
            'creator_id': None,
            'provenance_id': None,
            'timestamp': None,
            'error': str(e)
        }


def extract_watermark_info(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extract watermark information from an image.

    Args:
        image_bytes: Image bytes to analyze

    Returns:
        Dict with watermark data or error
    """
    try:
        from core.services.watermark_service import WatermarkService

        service = WatermarkService()
        result = service.extract_watermark(image_bytes)

        if result.success:
            return {
                'found': True,
                'data': result.watermark_data,
                'error': None
            }
        else:
            return {
                'found': False,
                'data': None,
                'error': result.error
            }

    except Exception as e:
        logger.error(f"Watermark extraction failed: {e}")
        return {
            'found': False,
            'data': None,
            'error': str(e)
        }

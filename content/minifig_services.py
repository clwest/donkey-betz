"""
MiniFig Services - Session 111

Service layer for creating 3D Mini-Fig assets from AI-generated images.

v1: Placeholder implementation with immediate completion
v2+: TODO - Integration with real 3D generation service
"""

import logging
from typing import List, Dict, Optional
from django.contrib.auth import get_user_model

from content.models import ImageHistory, MiniFigAsset

User = get_user_model()
logger = logging.getLogger(__name__)


def create_minifig_asset_from_images(
    user: User,
    image_asset_ids: List[str],
    pipeline_run=None,
    provider: str = 'placeholder',
    style: str = 'toy',
    scale: str = 'medium'
) -> List[MiniFigAsset]:
    """
    Create MiniFigAsset records from image assets.

    For v1: Creates placeholder 3D files immediately with completed status.
    For v2+: TODO - Dispatch to external 3D generation service with async processing.

    Args:
        user: User creating the mini-figs
        image_asset_ids: List of ImageHistory UUIDs (1-4 images)
        pipeline_run: Optional CreativePipelineRun that initiated this
        provider: Provider to use ('placeholder' for v1)
        style: Mini-fig style (e.g., 'toy', 'semi-realistic')
        scale: Mini-fig scale (e.g., 'small', 'medium', 'large')

    Returns:
        List of created MiniFigAsset instances

    Raises:
        ValueError: If validation fails
    """
    logger.info(f"Creating mini-figs for user {user.username} from {len(image_asset_ids)} images")

    # Validate inputs
    if not image_asset_ids or len(image_asset_ids) == 0:
        raise ValueError("At least 1 image asset ID is required")

    if len(image_asset_ids) > 4:
        raise ValueError("Maximum 4 image assets allowed per mini-fig creation")

    # Validate all images belong to user
    images = ImageHistory.objects.filter(id__in=image_asset_ids, user=user)

    if images.count() != len(image_asset_ids):
        found_ids = set(str(img.id) for img in images)
        requested_ids = set(str(id) for id in image_asset_ids)
        missing_ids = requested_ids - found_ids
        raise ValueError(f"Some images not found or don't belong to user: {missing_ids}")

    created_assets = []

    for idx, image in enumerate(images):
        # Generate title from image
        title = f"Mini-Fig from {image.filename or 'Image'}"

        # v1: Generate placeholder 3D file URL
        # v2+: TODO - Call external 3D generation service
        three_d_file_url = _generate_placeholder_3d_url(image.id, style, scale)

        # Use source image as preview (or could use a generic placeholder)
        preview_url = image.file_path if not image.file_path.startswith('data:') else ''

        # Create MiniFigAsset
        minifig = MiniFigAsset.objects.create(
            user=user,
            source_pipeline_run=pipeline_run,
            source_image_asset=image,
            title=title,
            provider=provider,
            status='completed',  # v1: Immediate completion
            three_d_file=three_d_file_url,
            preview_image_url=preview_url,
            metadata={
                'style': style,
                'scale': scale,
                'generation_method': 'placeholder_v1',
                'source_image_id': str(image.id),
                'source_prompt': image.prompt or '',
            }
        )

        created_assets.append(minifig)
        logger.info(f"Created MiniFigAsset {minifig.id} from ImageHistory {image.id}")

    logger.info(f"Successfully created {len(created_assets)} mini-fig assets")
    return created_assets


def _generate_placeholder_3d_url(image_id: str, style: str, scale: str) -> str:
    """
    Generate placeholder 3D file URL for v1.

    v1: Returns a static placeholder URL
    v2+: TODO - Replace with real 3D file URL from external service

    Args:
        image_id: Source image UUID
        style: Mini-fig style
        scale: Mini-fig scale

    Returns:
        Placeholder URL string
    """
    # v1: Use a generic placeholder STL file URL
    # In production v1, this could point to a sample/demo STL file hosted on S3 or similar
    # For now, use a placeholder path that indicates it's a demo file

    placeholder_url = f"https://placeholder.example.com/minifigs/{style}_{scale}_demo.stl"

    # TODO v2+: Replace with actual 3D generation service call
    # Example future implementation:
    # response = external_3d_service.create_minifig(
    #     image_url=image.file_path,
    #     style=style,
    #     scale=scale
    # )
    # return response.file_url

    return placeholder_url


def update_minifig_status(minifig_id: str, status: str, error_message: str = '') -> MiniFigAsset:
    """
    Update the status of a MiniFigAsset.

    Used for async processing in v2+ when real 3D generation takes time.
    For v1: Not heavily used since we complete immediately.

    Args:
        minifig_id: MiniFigAsset UUID
        status: New status ('pending', 'processing', 'completed', 'failed')
        error_message: Optional error message if status is 'failed'

    Returns:
        Updated MiniFigAsset instance

    Raises:
        ValueError: If minifig not found or invalid status
    """
    try:
        minifig = MiniFigAsset.objects.get(id=minifig_id)
    except MiniFigAsset.DoesNotExist:
        raise ValueError(f"MiniFigAsset {minifig_id} not found")

    valid_statuses = ['pending', 'processing', 'completed', 'failed']
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")

    minifig.status = status
    if error_message:
        minifig.error_message = error_message

    minifig.save(update_fields=['status', 'error_message', 'updated_at'])

    logger.info(f"Updated MiniFigAsset {minifig_id} status to '{status}'")
    return minifig


def get_user_minifigs(user: User, status: Optional[str] = None) -> List[MiniFigAsset]:
    """
    Get all mini-figs for a user, optionally filtered by status.

    Args:
        user: User to get mini-figs for
        status: Optional status filter ('completed', 'failed', etc.)

    Returns:
        QuerySet of MiniFigAsset instances
    """
    queryset = MiniFigAsset.objects.filter(user=user).select_related(
        'source_image_asset',
        'source_pipeline_run'
    )

    if status:
        queryset = queryset.filter(status=status)

    return queryset.order_by('-created_at')

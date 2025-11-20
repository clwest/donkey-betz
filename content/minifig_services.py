"""
MiniFig Services - Session 111

Service layer for creating 3D Mini-Fig assets from AI-generated images.

v1: Placeholder implementation with immediate completion
v2: Real 3D generation using Replicate TRELLIS (Session 115 Part 3)
"""

import logging
from typing import List, Dict, Optional
from django.contrib.auth import get_user_model

from content.models import ImageHistory, MiniFigAsset
from content.replicate_provider import get_replicate_provider

User = get_user_model()
logger = logging.getLogger(__name__)


def create_minifig_asset_from_images(
    user: User,
    image_asset_ids: List[str],
    pipeline_run=None,
    provider: str = 'placeholder',
    style: str = 'toy',
    scale: str = 'medium',
    project_id: Optional[str] = None  # Session 137: Add project_id parameter
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

    # Check if we should use real 3D generation
    use_real_generation = (provider == 'replicate')

    if use_real_generation:
        # v2: Real 3D generation using Replicate TRELLIS
        logger.info("Using Replicate TRELLIS for real 3D generation")

        # Get Replicate provider
        replicate = get_replicate_provider()

        if not replicate.available:
            logger.warning("Replicate not available, falling back to placeholder")
            use_real_generation = False

    if use_real_generation:
        # Collect image file paths (TRELLIS supports file uploads and URLs)
        import os
        from django.conf import settings

        image_files = []
        for image in images:
            if not image.file_path:
                logger.warning(f"Image {image.id} has no file_path, skipping")
                continue

            # Check if it's a data URI
            if image.file_path.startswith('data:'):
                logger.warning(f"Image {image.id} is a data URI, cannot use for 3D generation")
                continue

            # Check if it's already a full URL (starts with http/https)
            if image.file_path.startswith('http://') or image.file_path.startswith('https://'):
                # Public URL - can use directly
                image_files.append(image.file_path)
            else:
                # Relative path - convert to absolute filesystem path
                # Images are stored in MEDIA_ROOT
                absolute_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
                if os.path.exists(absolute_path):
                    image_files.append(absolute_path)
                    logger.info(f"Using local file: {absolute_path}")
                else:
                    logger.warning(f"Image file not found: {absolute_path}")

        if not image_files:
            raise ValueError("No valid image files found. Need local files or public URLs for 3D generation.")

        # Start 3D generation for all images together (multi-view)
        logger.info(f"Starting 3D generation from {len(image_files)} image(s)")
        result = replicate.generate_3d_from_images(
            image_urls=image_files,  # Can be URLs or local file paths
            generate_model=True,  # Generate GLB model
            generate_color=True,  # Generate color video
            save_gaussian_ply=True  # Save point cloud
        )

        if not result.success:
            raise ValueError(f"3D generation failed: {result.error_message}")

        # Session 137: Get project if project_id provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=user)
            except CreativeProject.DoesNotExist:
                logger.warning(f"Project {project_id} not found for user {user.username}")

        # Create MiniFigAsset with pending status
        title = f"Mini-Fig from {len(images)} image(s)"
        preview_url = images[0].file_path if images[0].file_path and not images[0].file_path.startswith('data:') else ''

        minifig = MiniFigAsset.objects.create(
            user=user,
            source_pipeline_run=pipeline_run,
            source_image_asset=images[0],  # Use first image as primary source
            title=title,
            provider='replicate',
            status='pending',  # Async generation
            three_d_file='',  # Will be filled when generation completes
            preview_image_url=preview_url,
            project=project,  # Session 137: Associate with project
            download_completed=False,  # Session 143: Explicit default for NOT NULL constraint
            metadata={
                'style': style,
                'scale': scale,
                'generation_method': 'replicate_trellis_v2',
                'prediction_id': result.prediction_id,
                'source_image_ids': [str(img.id) for img in images],
                'source_prompts': [img.prompt or '' for img in images],
                'image_count': len(images),
            }
        )

        created_assets.append(minifig)
        logger.info(f"Created MiniFigAsset {minifig.id} with prediction {result.prediction_id}")

        # Session 142: Track agent contribution for 3D generation
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='three-d-generation-agent')
            AgentContribution.objects.create(
                agent=agent,
                minifig_asset=minifig,
                project=project,
                contribution_type='generation',
                task_description=f"Generated 3D model from {len(images)} source images using Replicate TRELLIS (style={style}, scale={scale})",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for MiniFigAsset {minifig.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution for 3D generation: {e}")
            # Don't fail content creation if contribution tracking fails

    else:
        # v1: Placeholder generation (immediate completion)
        for idx, image in enumerate(images):
            # Generate title from image
            title = f"Mini-Fig from {image.filename or 'Image'}"

            # v1: Generate placeholder 3D file URL
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
                download_completed=False,  # Session 143: Explicit default for NOT NULL constraint
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

            # Session 142: Track agent contribution for 3D generation (placeholder)
            try:
                from agents.models import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='three-d-generation-agent')
                AgentContribution.objects.create(
                    agent=agent,
                    minifig_asset=minifig,
                    project=None,  # Placeholder generation doesn't have project context
                    contribution_type='generation',
                    task_description=f"Generated placeholder 3D model from image {image.id} (provider={provider}, style={style}, scale={scale})",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for MiniFigAsset {minifig.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution for 3D generation: {e}")
                # Don't fail content creation if contribution tracking fails

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


def _download_glb_file(minifig: MiniFigAsset, glb_url: str) -> bool:
    """
    Download GLB file from Replicate CDN to local storage.

    Session 139: Prevents data loss when CDN URLs expire (24-48 hours)

    Args:
        minifig: MiniFigAsset instance to update
        glb_url: CDN URL to download from

    Returns:
        True if download succeeded, False otherwise
    """
    import requests
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    try:
        logger.info(f"📥 Downloading GLB file for MiniFigAsset {minifig.id}")
        logger.info(f"   URL: {glb_url[:80]}...")

        # Download file from CDN
        response = requests.get(glb_url, timeout=60)
        response.raise_for_status()

        # Generate filename
        filename = f"minifig-{minifig.id}.glb"
        file_path = f"3d_models/{filename}"

        # Save to storage
        content_file = ContentFile(response.content)
        saved_path = default_storage.save(file_path, content_file)

        # Update MiniFigAsset with local file info
        minifig.local_glb_path = saved_path
        minifig.download_completed = True
        minifig.download_error = ''  # Clear any previous errors
        minifig.save(update_fields=['local_glb_path', 'download_completed', 'download_error'])

        file_size_mb = len(response.content) / (1024 * 1024)
        logger.info(f"✅ GLB file downloaded successfully")
        logger.info(f"   Size: {file_size_mb:.2f} MB")
        logger.info(f"   Saved to: {saved_path}")

        return True

    except requests.RequestException as e:
        error_msg = f"Failed to download GLB file: {str(e)}"
        logger.error(f"❌ {error_msg}")
        minifig.download_error = error_msg
        minifig.save(update_fields=['download_error'])
        return False

    except Exception as e:
        error_msg = f"Unexpected error downloading GLB file: {str(e)}"
        logger.error(f"❌ {error_msg}")
        minifig.download_error = error_msg
        minifig.save(update_fields=['download_error'])
        return False


def check_and_update_3d_generation(minifig_id: str) -> MiniFigAsset:
    """
    Check the status of a Replicate 3D generation and update the MiniFigAsset.

    Args:
        minifig_id: MiniFigAsset UUID

    Returns:
        Updated MiniFigAsset instance

    Raises:
        ValueError: If minifig not found or not using Replicate
    """
    try:
        minifig = MiniFigAsset.objects.get(id=minifig_id)
    except MiniFigAsset.DoesNotExist:
        raise ValueError(f"MiniFigAsset {minifig_id} not found")

    # Only check Replicate-generated assets
    if minifig.provider != 'replicate':
        logger.warning(f"MiniFigAsset {minifig_id} is not a Replicate generation")
        return minifig

    # Get prediction_id from metadata
    prediction_id = minifig.metadata.get('prediction_id')
    if not prediction_id:
        logger.error(f"MiniFigAsset {minifig_id} has no prediction_id in metadata")
        minifig.status = 'failed'
        minifig.error_message = 'No prediction ID found'
        minifig.save()
        return minifig

    # Check status with Replicate
    replicate = get_replicate_provider()
    result = replicate.check_3d_generation_status(prediction_id)

    if not result.get('success'):
        logger.error(f"Failed to check 3D generation status: {result.get('error_message')}")
        return minifig

    status = result.get('status', 'unknown')
    logger.info(f"MiniFigAsset {minifig_id} status: {status}")

    # Update MiniFigAsset based on status
    if status == 'succeeded':
        # Extract file URLs from result (Session 139: Ensure we extract strings, not dicts)
        model_file = result.get('model_file', '')

        # Session 139: Defensive URL extraction - if model_file is a dict, extract the URL
        if isinstance(model_file, dict):
            # Replicate might return {"model_file": "url", ...} instead of just "url"
            model_file = model_file.get('model_file', '') or model_file.get('url', '')
            logger.warning(f"⚠️ model_file was a dict, extracted URL: {model_file[:80] if model_file else 'None'}")

        # Ensure it's a string
        if not isinstance(model_file, str):
            logger.error(f"❌ model_file is not a string: {type(model_file)}")
            model_file = str(model_file) if model_file else ''

        color_video = result.get('color_video', '')
        gaussian_ply = result.get('gaussian_ply', '')

        minifig.status = 'completed'
        minifig.three_d_file = model_file  # GLB file (Session 139: Now guaranteed to be string URL)
        minifig.metadata['color_video'] = color_video
        minifig.metadata['gaussian_ply'] = gaussian_ply
        minifig.metadata['normal_video'] = result.get('normal_video', '')
        minifig.save()

        logger.info(f"✅ MiniFigAsset {minifig_id} generation completed")
        logger.info(f"   Model file: {model_file}")

        # Session 139: Download GLB file to local storage (prevents CDN expiration data loss)
        if model_file and not minifig.download_completed:
            logger.info(f"📥 Starting automatic file download for MiniFigAsset {minifig_id}")
            download_success = _download_glb_file(minifig, model_file)
            if download_success:
                logger.info(f"✅ File download completed successfully")
            else:
                logger.warning(f"⚠️ File download failed, but CDN URL is still available: {model_file[:80]}...")
        elif minifig.download_completed:
            logger.info(f"✅ File already downloaded to: {minifig.local_glb_path}")

    elif status == 'failed':
        error = result.get('error', 'Unknown error')
        minifig.status = 'failed'
        minifig.error_message = error
        minifig.save()

        logger.error(f"❌ MiniFigAsset {minifig_id} generation failed: {error}")

    elif status in ['starting', 'processing']:
        minifig.status = 'processing'
        minifig.save()

        logger.info(f"⏳ MiniFigAsset {minifig_id} still processing...")

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

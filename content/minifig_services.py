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


def repair_mesh_for_print(minifig_id: str) -> Dict:
    """
    Repair a 3D mesh to make it 3D-printable.

    Session 182: Mesh repair for 3D printing preparation.
    Enhanced with aggressive repair techniques for AI-generated models.

    Uses trimesh to:
    - Fill holes in the mesh
    - Fix inverted normals
    - Remove degenerate faces
    - Make mesh watertight (manifold)
    - Voxel-based reconstruction for severely broken meshes

    Args:
        minifig_id: MiniFigAsset UUID

    Returns:
        Dict with repair results:
        {
            'success': bool,
            'original_file': str,
            'repaired_file': str,
            'is_watertight': bool,
            'vertices': int,
            'faces': int,
            'repairs_made': list,
            'error': str (if failed)
        }
    """
    import os
    import numpy as np
    import trimesh
    from django.conf import settings
    from django.core.files.storage import default_storage

    try:
        minifig = MiniFigAsset.objects.get(id=minifig_id)
    except MiniFigAsset.DoesNotExist:
        return {'success': False, 'error': f'MiniFigAsset {minifig_id} not found'}

    # Check if we have a local GLB file
    if not minifig.local_glb_path:
        return {'success': False, 'error': 'No local GLB file available. File may not have been downloaded yet.'}

    # Get absolute path to input file
    input_path = os.path.join(settings.MEDIA_ROOT, minifig.local_glb_path)

    if not os.path.exists(input_path):
        return {'success': False, 'error': f'GLB file not found at {input_path}'}

    logger.info(f"🔧 Starting mesh repair for MiniFigAsset {minifig_id}")
    logger.info(f"   Input file: {input_path}")

    repairs_made = []

    try:
        # Load the mesh - try different approaches
        scene_or_mesh = trimesh.load(input_path)

        # Handle Scene vs Mesh
        if isinstance(scene_or_mesh, trimesh.Scene):
            # Combine all meshes in the scene into one
            if len(scene_or_mesh.geometry) > 0:
                meshes = list(scene_or_mesh.geometry.values())
                # Filter to only actual meshes
                meshes = [m for m in meshes if isinstance(m, trimesh.Trimesh)]
                if len(meshes) == 0:
                    return {'success': False, 'error': 'GLB file contains no valid mesh geometry'}
                elif len(meshes) == 1:
                    mesh = meshes[0]
                    repairs_made.append(f"Extracted single mesh from scene")
                else:
                    # Concatenate all meshes into one
                    mesh = trimesh.util.concatenate(meshes)
                    repairs_made.append(f"Combined {len(meshes)} meshes from scene into one")
            else:
                return {'success': False, 'error': 'GLB file contains no mesh geometry'}
        else:
            mesh = scene_or_mesh

        # Ensure we have a Trimesh object
        if not isinstance(mesh, trimesh.Trimesh):
            return {'success': False, 'error': f'Loaded object is not a mesh: {type(mesh)}'}

        original_vertices = len(mesh.vertices)
        original_faces = len(mesh.faces)
        original_watertight = mesh.is_watertight

        logger.info(f"   Original mesh: {original_vertices} vertices, {original_faces} faces, watertight={original_watertight}")

        # PHASE 1: Basic cleanup
        # 1. Remove degenerate faces (zero-area triangles)
        mesh.remove_degenerate_faces()
        if len(mesh.faces) != original_faces:
            repairs_made.append(f"Removed {original_faces - len(mesh.faces)} degenerate faces")

        # 2. Remove duplicate faces
        mesh.remove_duplicate_faces()

        # 3. Merge close vertices (within tolerance)
        mesh.merge_vertices()
        repairs_made.append("Merged close vertices")

        # 4. Remove unreferenced vertices
        mesh.remove_unreferenced_vertices()

        # 5. Remove infinite values if any
        mesh.remove_infinite_values()

        # PHASE 2: Fix normals and orientation
        # Fix winding order and normals
        mesh.fix_normals()
        repairs_made.append("Fixed face normals and winding order")

        # PHASE 3: Fill holes
        mesh.fill_holes()
        if mesh.is_watertight:
            repairs_made.append("Filled holes - mesh is now watertight")

        # PHASE 4: If still not watertight, try voxel reconstruction
        if not mesh.is_watertight:
            logger.info("   Mesh still not watertight, attempting voxel reconstruction...")
            try:
                # Calculate appropriate voxel pitch based on mesh size
                bounds = mesh.bounds
                max_dimension = max(bounds[1] - bounds[0])
                # Use 256 voxels along the longest dimension for good detail
                pitch = max_dimension / 256.0

                # Voxelize and convert back to mesh
                voxel_grid = mesh.voxelized(pitch=pitch)
                mesh = voxel_grid.marching_cubes

                repairs_made.append(f"Applied voxel reconstruction (pitch={pitch:.4f})")

                # Re-apply basic fixes after voxelization
                mesh.fix_normals()
                mesh.fill_holes()

                if mesh.is_watertight:
                    repairs_made.append("Voxel reconstruction made mesh watertight!")
            except Exception as voxel_error:
                logger.warning(f"   Voxel reconstruction failed: {voxel_error}")
                repairs_made.append(f"Voxel reconstruction skipped: {str(voxel_error)[:50]}")

        # PHASE 5: Final processing
        mesh = mesh.process(validate=True)
        repairs_made.append("Final processing complete")

        final_vertices = len(mesh.vertices)
        final_faces = len(mesh.faces)
        final_watertight = mesh.is_watertight

        logger.info(f"   Repaired mesh: {final_vertices} vertices, {final_faces} faces, watertight={final_watertight}")

        # Generate output filenames - both GLB and STL
        glb_filename = f"minifig-{minifig_id}-printready.glb"
        stl_filename = f"minifig-{minifig_id}-printready.stl"
        glb_rel_path = f"3d_models/{glb_filename}"
        stl_rel_path = f"3d_models/{stl_filename}"
        glb_path = os.path.join(settings.MEDIA_ROOT, glb_rel_path)
        stl_path = os.path.join(settings.MEDIA_ROOT, stl_rel_path)

        # Ensure directory exists
        os.makedirs(os.path.dirname(glb_path), exist_ok=True)

        # Export repaired mesh in both formats
        mesh.export(glb_path, file_type='glb')
        mesh.export(stl_path, file_type='stl')

        glb_size_kb = os.path.getsize(glb_path) / 1024
        stl_size_kb = os.path.getsize(stl_path) / 1024

        # Update MiniFigAsset metadata
        minifig.metadata['print_ready_glb'] = glb_rel_path
        minifig.metadata['print_ready_stl'] = stl_rel_path
        minifig.metadata['print_ready_file'] = glb_rel_path  # Keep for backwards compatibility
        minifig.metadata['print_ready_stats'] = {
            'is_watertight': final_watertight,
            'vertices': final_vertices,
            'faces': final_faces,
            'repairs_made': repairs_made,
            'original_watertight': original_watertight,
            'original_vertices': original_vertices,
            'original_faces': original_faces
        }
        minifig.save(update_fields=['metadata'])

        logger.info(f"✅ Mesh repair complete!")
        logger.info(f"   GLB file: {glb_path} ({glb_size_kb:.1f} KB)")
        logger.info(f"   STL file: {stl_path} ({stl_size_kb:.1f} KB)")
        logger.info(f"   Watertight: {final_watertight}")
        logger.info(f"   Repairs: {repairs_made}")

        return {
            'success': True,
            'original_file': minifig.local_glb_path,
            'repaired_glb': glb_rel_path,
            'repaired_stl': stl_rel_path,
            'repaired_file': glb_rel_path,  # Keep for backwards compatibility
            'is_watertight': final_watertight,
            'vertices': final_vertices,
            'faces': final_faces,
            'repairs_made': repairs_made,
            'glb_size_kb': round(glb_size_kb, 1),
            'stl_size_kb': round(stl_size_kb, 1),
            'file_size_kb': round(glb_size_kb, 1),  # Keep for backwards compatibility
            'original_stats': {
                'watertight': original_watertight,
                'vertices': original_vertices,
                'faces': original_faces
            }
        }

    except Exception as e:
        error_msg = f"Mesh repair failed: {str(e)}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        return {'success': False, 'error': error_msg}

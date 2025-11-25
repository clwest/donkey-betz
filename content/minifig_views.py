"""
MiniFig Assets API Views

Session 111 - MiniFig Pipeline v1
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import MiniFigAsset
from .minifig_services import get_user_minifigs, check_and_update_3d_generation, repair_mesh_for_print

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_minifigs(request):
    """
    GET /api/v1/minifigs/

    Returns list of mini-fig assets for the current user, newest-first.

    Query params:
        limit: int (default 20, max 100)
        offset: int (default 0)
        status: string (filter by status: pending, processing, completed, failed)
    """
    try:
        # Parse query params
        limit = min(int(request.GET.get('limit', 20)), 100)
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status')

        # Query minifigs using service layer
        minifigs_qs = get_user_minifigs(request.user, status=status_filter)

        total_count = minifigs_qs.count()
        minifigs = minifigs_qs[offset:offset + limit]

        minifigs_data = [
            {
                'id': str(mf.id),
                'title': mf.title,
                'provider': mf.provider,
                'status': mf.status,
                'three_d_file': mf.three_d_file,
                'preview_image_url': mf.preview_image_url,
                'metadata': mf.metadata,
                'is_favorite': mf.is_favorite,
                'view_count': mf.view_count,
                'download_count': mf.download_count,
                'created_at': mf.created_at.isoformat(),
                'updated_at': mf.updated_at.isoformat(),
                'source_pipeline_run_id': str(mf.source_pipeline_run.id) if mf.source_pipeline_run else None,
                'source_image_asset_id': str(mf.source_image_asset.id) if mf.source_image_asset else None
            }
            for mf in minifigs
        ]

        return Response({
            'success': True,
            'minifigs': minifigs_data,
            'count': len(minifigs_data),
            'total': total_count,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error listing minifigs: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_minifig_detail(request, minifig_id):
    """
    GET /api/v1/minifigs/{id}/

    Returns complete details for a single mini-fig asset.

    Includes:
        - All minifig fields
        - Metadata
        - User notes and tags
        - Source references (pipeline run, image asset)
    """
    try:
        # Get minifig (ensure user owns it)
        try:
            minifig = MiniFigAsset.objects.select_related(
                'user',
                'source_pipeline_run',
                'source_image_asset'
            ).get(id=minifig_id, user=request.user)
        except MiniFigAsset.DoesNotExist:
            return Response({
                'success': False,
                'error': 'MiniFig asset not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # For Replicate generations, check status and update if still in progress
        if minifig.provider == 'replicate' and minifig.status in ['pending', 'processing']:
            try:
                logger.info(f"Checking Replicate status for MiniFigAsset {minifig_id}")
                minifig = check_and_update_3d_generation(str(minifig.id))
            except Exception as e:
                logger.warning(f"Failed to check 3D generation status: {e}")
                # Continue anyway and return current status

        # Build response
        minifig_data = {
            'id': str(minifig.id),
            'title': minifig.title,
            'provider': minifig.provider,
            'status': minifig.status,
            'three_d_file': minifig.three_d_file,
            'preview_image_url': minifig.preview_image_url,
            'metadata': minifig.metadata,
            'error_message': minifig.error_message,
            'is_favorite': minifig.is_favorite,
            'view_count': minifig.view_count,
            'download_count': minifig.download_count,
            'user_notes': minifig.user_notes,
            'tags': minifig.tags,
            'created_at': minifig.created_at.isoformat(),
            'updated_at': minifig.updated_at.isoformat(),
            'source_pipeline_run': {
                'id': str(minifig.source_pipeline_run.id),
                'template_name': minifig.source_pipeline_run.template.name,
                'status': minifig.source_pipeline_run.status,
                'created_at': minifig.source_pipeline_run.created_at.isoformat()
            } if minifig.source_pipeline_run else None,
            'source_image_asset': {
                'id': str(minifig.source_image_asset.id),
                'filename': minifig.source_image_asset.filename,
                'file_path': minifig.source_image_asset.file_path,
                'prompt': minifig.source_image_asset.prompt
            } if minifig.source_image_asset else None
        }

        # Increment view count
        minifig.increment_view_count()

        return Response({
            'success': True,
            'minifig': minifig_data
        })

    except Exception as e:
        logger.error(f"Error getting minifig detail: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_minifig(request, minifig_id):
    """
    DELETE /api/v1/minifigs/{id}/delete/

    Session 181: Delete a 3D model asset.
    Deletes the database record and associated files.
    """
    try:
        # Get minifig (ensure user owns it)
        try:
            minifig = MiniFigAsset.objects.get(id=minifig_id, user=request.user)
        except MiniFigAsset.DoesNotExist:
            return Response({
                'success': False,
                'error': '3D model not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Store info for response
        minifig_title = minifig.title
        minifig_id_str = str(minifig.id)

        # Delete associated GLB file if it exists
        import os
        if minifig.glb_file:
            try:
                file_path = minifig.glb_file.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted GLB file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete GLB file: {e}")

        # Delete the database record
        minifig.delete()

        logger.info(f"Deleted 3D model {minifig_id_str}: {minifig_title}")

        return Response({
            'success': True,
            'message': f'3D model "{minifig_title}" deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting 3D model: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prepare_for_print(request, minifig_id):
    """
    POST /api/v1/minifigs/{id}/prepare-for-print/

    Session 182: Prepare a 3D model for 3D printing.

    Repairs the mesh using trimesh to:
    - Fill holes (make watertight)
    - Fix normals
    - Remove degenerate/duplicate faces
    - Clean up unreferenced vertices

    Returns the path to the print-ready GLB file.
    """
    try:
        # Verify user owns this minifig
        try:
            minifig = MiniFigAsset.objects.get(id=minifig_id, user=request.user)
        except MiniFigAsset.DoesNotExist:
            return Response({
                'success': False,
                'error': '3D model not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if model is completed
        if minifig.status != 'completed':
            return Response({
                'success': False,
                'error': f'3D model is still {minifig.status}. Cannot prepare for print until completed.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if we have a local file
        if not minifig.local_glb_path:
            return Response({
                'success': False,
                'error': 'No local GLB file available. The file may not have been downloaded yet.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Run mesh repair
        logger.info(f"Starting mesh repair for MiniFigAsset {minifig_id}")
        result = repair_mesh_for_print(str(minifig.id))

        if not result.get('success'):
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error during mesh repair')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Build download URLs for both GLB and STL files
        from django.conf import settings
        glb_url = f"{settings.MEDIA_URL}{result.get('repaired_glb', result['repaired_file'])}"
        stl_url = f"{settings.MEDIA_URL}{result.get('repaired_stl', '')}" if result.get('repaired_stl') else None

        return Response({
            'success': True,
            'message': 'Mesh repair complete! Your 3D model is ready for printing.',
            'glb_url': glb_url,
            'stl_url': stl_url,
            'repaired_file_url': glb_url,  # Keep for backwards compatibility
            'repaired_file_path': result.get('repaired_glb', result['repaired_file']),
            'is_watertight': result['is_watertight'],
            'vertices': result['vertices'],
            'faces': result['faces'],
            'glb_size_kb': result.get('glb_size_kb', result['file_size_kb']),
            'stl_size_kb': result.get('stl_size_kb'),
            'file_size_kb': result['file_size_kb'],  # Keep for backwards compatibility
            'repairs_made': result['repairs_made'],
            'original_stats': result['original_stats']
        })

    except Exception as e:
        logger.error(f"Error preparing 3D model for print: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

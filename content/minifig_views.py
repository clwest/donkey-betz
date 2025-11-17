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
from .minifig_services import get_user_minifigs, check_and_update_3d_generation

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

"""
Creative Pipelines API Views

Session 109 - Creative Pipelines v1
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import CreativePipelineRun
from .services import get_available_templates, start_pipeline_run
from content.minifig_services import create_minifig_asset_from_images

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """
    GET /api/v1/pipelines/templates/

    Returns list of active pipeline templates available to the user.
    """
    try:
        templates = get_available_templates(request.user)

        templates_data = [
            {
                'slug': t.slug,
                'name': t.name,
                'description': t.description,
                'total_steps': len(t.config.get('steps', [])),
                'inputs': t.config.get('inputs', {}),
                'outputs': t.config.get('outputs', {})
            }
            for t in templates
        ]

        return Response({
            'success': True,
            'templates': templates_data,
            'count': len(templates_data)
        })

    except Exception as e:
        logger.error(f"Error listing templates: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def runs_endpoint(request):
    """
    GET /api/v1/pipelines/runs/ - List runs
    POST /api/v1/pipelines/runs/ - Create run

    Combined endpoint following REST conventions.
    """
    if request.method == 'POST':
        # CREATE RUN
        try:
            # Validate request data
            template_slug = request.data.get('template_slug')
            if not template_slug:
                return Response({
                    'success': False,
                    'error': 'template_slug is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            input_payload = request.data.get('input_payload', {})
            project_id = request.data.get('project_id')
            session_id = request.data.get('session_id')

            # Start pipeline run
            run = start_pipeline_run(
                user=request.user,
                template_slug=template_slug,
                input_payload=input_payload,
                project_id=project_id,
                session_id=session_id
            )

            return Response({
                'success': True,
                'run': {
                    'id': str(run.id),
                    'template_slug': run.template.slug,
                    'template_name': run.template.name,
                    'status': run.status,
                    'total_steps': run.total_steps,
                    'created_at': run.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            # Validation errors (template not found, etc.)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating pipeline run: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:  # GET
        # LIST RUNS
        try:
            # Parse query params
            limit = min(int(request.GET.get('limit', 20)), 100)
            offset = int(request.GET.get('offset', 0))
            status_filter = request.GET.get('status')

            # Query runs
            runs_qs = CreativePipelineRun.objects.filter(
                user=request.user
            ).select_related('template', 'project', 'session')

            if status_filter:
                runs_qs = runs_qs.filter(status=status_filter)

            runs_qs = runs_qs.order_by('-created_at')
            total_count = runs_qs.count()
            runs = runs_qs[offset:offset + limit]

            runs_data = [
                {
                    'id': str(r.id),
                    'template_slug': r.template.slug,
                    'template_name': r.template.name,
                    'status': r.status,
                    'current_step': r.current_step,
                    'total_steps': r.total_steps,
                    'progress_percentage': r.progress_percentage,
                    'created_at': r.created_at.isoformat(),
                    'updated_at': r.updated_at.isoformat(),
                    'completed_at': r.completed_at.isoformat() if r.completed_at else None,
                    'project_id': str(r.project.id) if r.project else None,
                    'project_name': r.project.name if r.project else None
                }
                for r in runs
            ]

            return Response({
                'success': True,
                'runs': runs_data,
                'count': len(runs_data),
                'total': total_count,
                'limit': limit,
                'offset': offset
            })

        except Exception as e:
            logger.error(f"Error listing runs: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Keep old function names as aliases for backwards compatibility
create_run = runs_endpoint
list_runs = runs_endpoint


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_run_detail(request, run_id):
    """
    GET /api/v1/pipelines/runs/

    Returns list of pipeline runs for the current user, newest-first.

    Query params:
        limit: int (default 20, max 100)
        offset: int (default 0)
        status: string (filter by status)
    """
    try:
        # Parse query params
        limit = min(int(request.GET.get('limit', 20)), 100)
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status')

        # Query runs
        runs_qs = CreativePipelineRun.objects.filter(
            user=request.user
        ).select_related('template', 'project', 'session')

        if status_filter:
            runs_qs = runs_qs.filter(status=status_filter)

        runs_qs = runs_qs.order_by('-created_at')
        total_count = runs_qs.count()
        runs = runs_qs[offset:offset + limit]

        runs_data = [
            {
                'id': str(r.id),
                'template_slug': r.template.slug,
                'template_name': r.template.name,
                'status': r.status,
                'current_step': r.current_step,
                'total_steps': r.total_steps,
                'progress_percentage': r.progress_percentage,
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat(),
                'completed_at': r.completed_at.isoformat() if r.completed_at else None,
                'project_id': str(r.project.id) if r.project else None,
                'project_name': r.project.name if r.project else None
            }
            for r in runs
        ]

        return Response({
            'success': True,
            'runs': runs_data,
            'count': len(runs_data),
            'total': total_count,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"Error listing runs: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_run_detail(request, run_id):
    """
    GET /api/v1/pipelines/runs/{id}/

    Returns complete details for a single pipeline run.

    Includes:
        - All run fields
        - Input and output payloads
        - Execution log
        - Error message (if failed)
    """
    try:
        # Get run (ensure user owns it)
        try:
            run = CreativePipelineRun.objects.select_related(
                'template', 'project', 'session', 'user'
            ).get(id=run_id, user=request.user)
        except CreativePipelineRun.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Pipeline run not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Build response
        run_data = {
            'id': str(run.id),
            'template': {
                'slug': run.template.slug,
                'name': run.template.name,
                'description': run.template.description
            },
            'status': run.status,
            'current_step': run.current_step,
            'total_steps': run.total_steps,
            'progress_percentage': run.progress_percentage,
            'input_payload': run.input_payload,
            'output_payload': run.output_payload,
            'log': run.log,
            'error_message': run.error_message,
            'created_at': run.created_at.isoformat(),
            'updated_at': run.updated_at.isoformat(),
            'completed_at': run.completed_at.isoformat() if run.completed_at else None,
            'duration': run.duration,
            'project': {
                'id': str(run.project.id),
                'name': run.project.name
            } if run.project else None,
            'session': {
                'id': str(run.session.id),
                'title': run.session.title
            } if run.session else None
        }

        return Response({
            'success': True,
            'run': run_data
        })

    except Exception as e:
        logger.error(f"Error getting run detail: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def launch_minifig_pipeline(request):
    """
    POST /api/v1/pipelines/images_to_minifigs/launch/

    Launch the Image-to-MiniFig 3D character creation pipeline.

    Request body:
        image_ids: list of str - UUIDs of ImageHistory objects (1-4 images)
        style: str - "cartoon" or "realistic"
        scale: str - "28mm", "32mm", "54mm", or "75mm"

    Returns:
        success: bool
        minifig_id: str - UUID of created MiniFigAsset
        status: str - "completed" (v1 completes immediately)
    """
    try:
        # Validate request data
        image_ids = request.data.get('image_ids', [])
        style = request.data.get('style', 'cartoon')
        scale = request.data.get('scale', '32mm')

        if not image_ids:
            return Response({
                'success': False,
                'error': 'image_ids is required (1-4 image UUIDs)'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(image_ids) > 4:
            return Response({
                'success': False,
                'error': 'Maximum 4 images allowed'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate style
        valid_styles = ['cartoon', 'realistic']
        if style not in valid_styles:
            return Response({
                'success': False,
                'error': f'Invalid style. Must be one of: {valid_styles}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate scale
        valid_scales = ['28mm', '32mm', '54mm', '75mm']
        if scale not in valid_scales:
            return Response({
                'success': False,
                'error': f'Invalid scale. Must be one of: {valid_scales}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create MiniFig assets using real Replicate 3D generation
        minifig_assets = create_minifig_asset_from_images(
            user=request.user,
            image_asset_ids=image_ids,
            pipeline_run=None,  # Not tied to a CreativePipelineRun for now
            provider='replicate',  # v2: Real 3D generation with TRELLIS
            style=style,
            scale=scale
        )

        # Return minifig info (v2 creates one multi-view asset from all images)
        if minifig_assets:
            first_minifig = minifig_assets[0]

            # Get prediction_id from metadata for frontend polling
            prediction_id = first_minifig.metadata.get('prediction_id', '')

            return Response({
                'success': True,
                'minifig_id': str(first_minifig.id),
                'status': first_minifig.status,  # Will be 'pending' for Replicate
                'prediction_id': prediction_id,
                'message': f'Started 3D generation from {len(image_ids)} image(s). Check status with GET /api/v1/content/minifigs/{first_minifig.id}/'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': 'No MiniFig assets were created'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except ValueError as e:
        # Validation errors from service layer
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error launching MiniFig pipeline: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

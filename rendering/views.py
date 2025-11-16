"""
Rendering API Views - Session 105

REST API endpoints for render job management and Resolve Node integration.
"""

import logging
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.models import CreativeProject, AISession
from .models import RenderJob
from .serializers import RenderJobSerializer, RenderJobDetailSerializer

logger = logging.getLogger(__name__)


# Configuration (from settings or defaults)
RENDER_NODE_BASE_URL = getattr(settings, 'RENDER_NODE_BASE_URL', 'http://localhost:5001')
RENDER_NODE_TOKEN = getattr(settings, 'RENDER_NODE_TOKEN', 'default-token-change-me')
RENDER_NODE_TIMEOUT = getattr(settings, 'RENDER_NODE_TIMEOUT', 30)


def _call_resolve_node(method, endpoint, data=None):
    """
    Helper to make authenticated HTTP calls to Resolve Node.

    Args:
        method: 'GET' or 'POST'
        endpoint: e.g. '/render/start' or '/render/status/uuid'
        data: Optional payload dict for POST

    Returns:
        tuple: (success: bool, response_data: dict, error_message: str)
    """
    url = f"{RENDER_NODE_BASE_URL}{endpoint}"
    headers = {'X-Render-Token': RENDER_NODE_TOKEN}

    try:
        if method == 'POST':
            resp = requests.post(url, json=data, headers=headers, timeout=RENDER_NODE_TIMEOUT)
        else:
            resp = requests.get(url, headers=headers, timeout=RENDER_NODE_TIMEOUT)

        resp.raise_for_status()
        return (True, resp.json(), None)

    except requests.exceptions.Timeout:
        error_msg = f"Resolve Node timeout after {RENDER_NODE_TIMEOUT}s"
        logger.error(f"❌ {error_msg}: {url}")
        return (False, {}, error_msg)

    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to Resolve Node - is it running?"
        logger.error(f"❌ {error_msg}: {url}")
        return (False, {}, error_msg)

    except requests.exceptions.RequestException as e:
        error_msg = f"Resolve Node error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return (False, {}, error_msg)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_render_job(request):
    """
    Create and dispatch a new render job.

    POST /api/v1/render-jobs/

    Body:
    {
        "project_id": "optional UUID",
        "session_id": "optional UUID",
        "timeline_name": "optional",
        "template": "default_mp4"  # default
    }

    Returns:
        RenderJob serialized data
    """
    serializer = RenderJobSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Extract validated data
    project_id = serializer.validated_data.get('project_id')
    session_id = serializer.validated_data.get('session_id')
    timeline_name = serializer.validated_data.get('timeline_name', 'Timeline 1')
    template = serializer.validated_data.get('template', 'default_mp4')

    # Validate project belongs to user
    project = None
    if project_id:
        try:
            project = CreativeProject.objects.get(project_id=project_id, user=request.user)
        except CreativeProject.DoesNotExist:
            return Response(
                {'error': 'Project not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Validate session belongs to user
    session_obj = None
    if session_id:
        try:
            session_obj = AISession.objects.get(session_id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response(
                {'error': 'Session not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Create RenderJob
    job = RenderJob.objects.create(
        user=request.user,
        project=project,
        session=session_obj,
        status=RenderJob.STATUS_QUEUED,
    )

    # Build payload for Resolve Node
    source_payload = {
        'timeline_name': timeline_name,
        'template': template,
        'job_id': str(job.id),
        'user_id': str(request.user.id),
    }

    # Include session media if session provided
    if session_obj:
        # Get session's images and videos as media files
        from content.models import ImageHistory, VideoHistory
        images = ImageHistory.objects.filter(session=session_obj)
        videos = VideoHistory.objects.filter(session=session_obj)

        media_files = []
        for img in images:
            if img.file_path:
                media_files.append(str(img.file_path))
        for vid in videos:
            if vid.file_path:
                media_files.append(str(vid.file_path))

        source_payload['media_files'] = media_files

    job.source_payload = source_payload
    job.save(update_fields=['source_payload'])

    # Dispatch to Resolve Node
    job.status = RenderJob.STATUS_DISPATCHING
    job.dispatched_at = timezone.now()
    job.save(update_fields=['status', 'dispatched_at'])

    success, response_data, error_msg = _call_resolve_node(
        'POST',
        '/render/start',
        data=source_payload
    )

    if success:
        # Extract node job ID and update our job
        node_job_id = response_data.get('job_id')
        job.node_job_id = node_job_id
        job.status = RenderJob.STATUS_RENDERING
        job.save(update_fields=['node_job_id', 'status'])
        logger.info(f"✅ Dispatched render job {job.id} → node job {node_job_id}")
    else:
        # Dispatch failed
        job.status = RenderJob.STATUS_ERROR
        job.error_message = error_msg
        job.save(update_fields=['status', 'error_message'])
        logger.error(f"❌ Failed to dispatch job {job.id}: {error_msg}")

    # Return job data
    serializer = RenderJobDetailSerializer(job)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_render_job(request, job_id):
    """
    Get render job status.

    GET /api/v1/render-jobs/<uuid>/

    Before returning, optionally polls Resolve Node for latest status if job is active.
    """
    try:
        job = RenderJob.objects.get(id=job_id, user=request.user)
    except RenderJob.DoesNotExist:
        return Response(
            {'error': 'Render job not found or access denied'},
            status=status.HTTP_404_NOT_FOUND
        )

    # If job is active, poll Resolve Node for latest status
    if job.is_active and job.node_job_id:
        success, response_data, error_msg = _call_resolve_node(
            'GET',
            f'/render/status/{job.node_job_id}'
        )

        if success:
            # Update job status and progress from node response
            node_status = response_data.get('status', '')
            node_progress = response_data.get('progress', 0.0)

            # Map node status to our status
            if node_status == 'done':
                job.status = RenderJob.STATUS_DONE
                job.progress = 1.0
                job.completed_at = timezone.now()
                # Get result URL
                result_url = response_data.get('file_url') or f"{RENDER_NODE_BASE_URL}/render/result/{job.node_job_id}"
                job.result_url = result_url
                job.result_payload = response_data
                job.save(update_fields=['status', 'progress', 'completed_at', 'result_url', 'result_payload'])
            elif node_status == 'error':
                job.status = RenderJob.STATUS_ERROR
                job.error_message = response_data.get('error', 'Unknown error')
                job.completed_at = timezone.now()
                job.save(update_fields=['status', 'error_message', 'completed_at'])
            elif node_status == 'rendering':
                job.status = RenderJob.STATUS_RENDERING
                job.progress = node_progress
                job.save(update_fields=['status', 'progress'])

            logger.debug(f"🔄 Updated job {job.id} from node: status={job.status}, progress={job.progress}")

    serializer = RenderJobDetailSerializer(job)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_render_jobs(request):
    """
    List user's render jobs.

    GET /api/v1/render-jobs/?project_id=<uuid>&limit=20

    Query params:
        project_id: Optional - filter by project
        limit: Default 20 - max jobs to return
    """
    jobs = RenderJob.objects.filter(user=request.user)

    # Filter by project if provided
    project_id = request.query_params.get('project_id')
    if project_id:
        jobs = jobs.filter(project__project_id=project_id)

    # Limit results
    limit = int(request.query_params.get('limit', 20))
    jobs = jobs[:limit]

    serializer = RenderJobSerializer(jobs, many=True)
    return Response({
        'success': True,
        'jobs': serializer.data,
        'count': len(serializer.data)
    })

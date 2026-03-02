"""
Video Agents API — resolve, transcribe, transcript access.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def video_resolve(request):
    """POST /api/v1/video/resolve/ — resolve a video reference to normalized metadata."""
    from core.video_resolver import resolve_video

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    if not body:
        return JsonResponse({'ok': False, 'error': 'Empty body'}, status=400)

    resolved = resolve_video(body, user=request.user)
    if not resolved:
        return JsonResponse({'ok': False, 'error': 'Video not found'}, status=404)

    return JsonResponse({'ok': True, 'video': resolved.to_dict()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def video_transcribe(request):
    """POST /api/v1/video/transcribe/ — kick off async transcription."""
    from content.models import VideoTranscript, VideoHistory
    from core.video_resolver import resolve_video
    from core.tasks import transcribe_video_task

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    language = body.pop('language', 'en')

    resolved = resolve_video(body, user=request.user)
    if not resolved:
        return JsonResponse({'ok': False, 'error': 'Video not found'}, status=404)

    video = VideoHistory.objects.get(id=resolved.id)

    # Check for existing in-progress transcript
    existing = VideoTranscript.objects.filter(
        video=video, status__in=['queued', 'running']
    ).first()
    if existing:
        return JsonResponse({
            'ok': True,
            'transcript_id': str(existing.id),
            'status': existing.status,
            'message': 'Transcription already in progress',
        })

    transcript = VideoTranscript.objects.create(
        video=video,
        language=language,
        status='queued',
    )

    transcribe_video_task.delay(str(transcript.id))

    return JsonResponse({
        'ok': True,
        'transcript_id': str(transcript.id),
        'status': 'queued',
        'video_id': resolved.id,
        'video_title': resolved.title,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_transcripts_list(request):
    """GET /api/v1/video/transcripts/ — list transcripts, optionally filtered by video."""
    from content.models import VideoTranscript

    video_id = request.GET.get('video_id')
    seq = request.GET.get('sequential_number')
    limit = min(int(request.GET.get('limit', 20)), 50)

    qs = VideoTranscript.objects.filter(video__user=request.user)

    if video_id:
        qs = qs.filter(video_id=video_id)
    elif seq:
        from core.video_resolver import resolve_video
        resolved = resolve_video({'sequential_number': int(seq)}, user=request.user)
        if resolved:
            qs = qs.filter(video_id=resolved.id)
        else:
            return JsonResponse({'ok': True, 'transcripts': [], 'count': 0})

    transcripts = []
    for t in qs.order_by('-created_at')[:limit]:
        transcripts.append({
            'id': str(t.id),
            'video_id': str(t.video_id),
            'status': t.status,
            'provider': t.provider,
            'language': t.language,
            'text_length': len(t.text) if t.text else 0,
            'segment_count': len(t.segments_json) if t.segments_json else 0,
            'duration_seconds': t.duration_seconds,
            'error': t.error or None,
            'created_at': t.created_at.isoformat() if t.created_at else None,
        })

    return JsonResponse({'ok': True, 'transcripts': transcripts, 'count': len(transcripts)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_transcript_detail(request, transcript_id):
    """GET /api/v1/video/transcripts/<id>/ — full transcript with text + segments."""
    from content.models import VideoTranscript

    try:
        t = VideoTranscript.objects.select_related('video').get(
            id=transcript_id, video__user=request.user
        )
    except VideoTranscript.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Transcript not found'}, status=404)

    return JsonResponse({
        'ok': True,
        'transcript': {
            'id': str(t.id),
            'video_id': str(t.video_id),
            'video_title': (t.video.prompt or t.video.original_filename or '')[:200],
            'status': t.status,
            'provider': t.provider,
            'language': t.language,
            'text': t.text,
            'segments': t.segments_json,
            'duration_seconds': t.duration_seconds,
            'error': t.error or None,
            'created_at': t.created_at.isoformat() if t.created_at else None,
        },
    })

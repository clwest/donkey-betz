"""
Podcast Studio API Views - Session 502

Real API endpoints for the AI Podcast Studio.
Replaces mock data with actual PodcastEpisode database queries.
"""

import json
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def _episode_to_dict(ep):
    """Convert a PodcastEpisode to a dictionary for API response."""
    # Extract config values (stored in generation_config JSON field)
    config = ep.generation_config or {}
    format_type = config.get('format', 'debate')
    participant_count = config.get('participant_count', 3)

    # Calculate word count from script if available
    word_count = len(ep.script.split()) if ep.script else 0

    return {
        'id': str(ep.id),
        'topic': ep.topic or ep.title or 'Untitled',
        'format_type': format_type,
        'status': ep.status,
        'participant_count': participant_count,
        'has_audio': bool(ep.audio_file or ep.audio_url),
        'audio_url': ep.audio_file.url if ep.audio_file else ep.audio_url,
        'duration_seconds': ep.audio_duration_seconds or 0,
        'word_count': word_count,
        'created_at': ep.created_at.isoformat(),
        'completed_at': ep.published_at.isoformat() if ep.published_at else None,
        'error_message': ep.error_message,
    }


@login_required
@require_http_methods(["GET"])
def podcast_list(request):
    """
    List all podcast episodes for the current user.

    GET /api/podcasts/list/

    Query params:
        - status: Filter by status (pending, researching, debating, scripting, generating_audio, complete, failed)
        - limit: Number of results (default 20)
        - offset: Pagination offset (default 0)
    """
    from core.models import PodcastEpisode

    try:
        status_filter = request.GET.get('status', '')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        # Query episodes for this user
        episodes = PodcastEpisode.objects.filter(user=request.user).order_by('-created_at')

        if status_filter:
            # Support comma-separated statuses
            statuses = [s.strip() for s in status_filter.split(',')]
            episodes = episodes.filter(status__in=statuses)

        total_count = episodes.count()
        episodes = episodes[offset:offset + limit]

        # Format response
        episode_list = [_episode_to_dict(ep) for ep in episodes]

        # Get status counts for filters
        status_counts = {}
        for status_choice in ['pending', 'researching', 'debating', 'scripting', 'generating_audio', 'complete', 'failed']:
            status_counts[status_choice] = PodcastEpisode.objects.filter(
                user=request.user, status=status_choice
            ).count()

        return JsonResponse({
            'success': True,
            'episodes': episode_list,
            'total_count': total_count,
            'status_counts': status_counts,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def podcast_create(request):
    """
    Create a new podcast episode.

    POST /api/podcasts/create/

    Body:
        - topic: Topic for the podcast (required)
        - format_type: debate, interview, panel, solo (default: debate)
        - participant_count: Number of AI participants 2-5 (default: 3)
        - generate_audio: Whether to generate TTS audio (default: false)
    """
    from core.models import PodcastEpisode
    from core.tasks import generate_podcast_episode

    try:
        data = json.loads(request.body) if request.body else {}

        topic = data.get('topic', '').strip()
        if not topic:
            return JsonResponse({
                'success': False,
                'error': 'Topic is required'
            }, status=400)

        format_type = data.get('format_type', 'debate')
        if format_type not in ['debate', 'interview', 'panel', 'solo']:
            format_type = 'debate'

        participant_count = int(data.get('participant_count', 3))
        participant_count = max(2, min(5, participant_count))  # Clamp 2-5

        generate_audio = data.get('generate_audio', False)

        # Create episode record with generation_config
        episode = PodcastEpisode.objects.create(
            user=request.user,
            topic=topic,
            title=topic,  # Also set title
            status='pending',
            generation_config={
                'format': format_type,
                'participant_count': participant_count,
                'generate_audio': generate_audio,
            }
        )

        # Queue the generation task
        generate_podcast_episode.delay(
            episode_id=str(episode.id),
            topic=topic,
            format_type=format_type,
            participants=participant_count,
            generate_audio=generate_audio,
        )

        return JsonResponse({
            'success': True,
            'episode': _episode_to_dict(episode),
            'message': f'Podcast "{topic}" queued for generation. This may take a few minutes.',
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def podcast_status(request, episode_id):
    """
    Get status of a specific podcast episode.

    GET /api/podcasts/<episode_id>/status/
    """
    from core.models import PodcastEpisode

    try:
        episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)

        return JsonResponse({
            'success': True,
            'episode': _episode_to_dict(episode)
        })

    except PodcastEpisode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def podcast_script(request, episode_id):
    """
    Get the full script of a podcast episode.

    GET /api/podcasts/<episode_id>/script/
    """
    from core.models import PodcastEpisode

    try:
        episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)

        # Extract config
        config = episode.generation_config or {}
        format_type = config.get('format', 'debate')

        # Get debate content from the episode's debate field (JSON)
        debate_data = episode.debate or {}

        return JsonResponse({
            'success': True,
            'episode': {
                'id': str(episode.id),
                'topic': episode.topic or episode.title,
                'format_type': format_type,
                'status': episode.status,
            },
            'script': episode.script or '',
            'debate': {
                'research_summary': debate_data.get('research_summary', ''),
                'debate_transcript': debate_data.get('transcript', ''),
                'key_insights': debate_data.get('key_insights', []),
            } if debate_data else None,
            'word_count': len(episode.script.split()) if episode.script else 0,
        })

    except PodcastEpisode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def podcast_delete(request, episode_id):
    """
    Delete a podcast episode.

    DELETE /api/podcasts/<episode_id>/
    """
    from core.models import PodcastEpisode

    try:
        episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)
        topic = episode.topic or episode.title
        episode.delete()

        return JsonResponse({
            'success': True,
            'message': f'Podcast "{topic}" deleted'
        })

    except PodcastEpisode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def podcast_stats(request):
    """
    Get podcast statistics for the current user.

    GET /api/podcasts/stats/
    """
    from core.models import PodcastEpisode
    from django.db.models import Sum, Avg, Count

    try:
        episodes = PodcastEpisode.objects.filter(user=request.user)

        total = episodes.count()
        complete = episodes.filter(status='complete').count()
        in_progress = episodes.filter(status__in=['pending', 'researching', 'debating', 'scripting', 'generating_audio']).count()
        failed = episodes.filter(status='failed').count()

        # Aggregate stats - use audio_duration_seconds
        stats = episodes.filter(status='complete').aggregate(
            total_duration=Sum('audio_duration_seconds'),
            avg_duration=Avg('audio_duration_seconds'),
        )

        # Calculate total words from scripts
        total_words = 0
        for ep in episodes.filter(status='complete'):
            if ep.script:
                total_words += len(ep.script.split())

        return JsonResponse({
            'success': True,
            'stats': {
                'total_episodes': total,
                'complete': complete,
                'in_progress': in_progress,
                'failed': failed,
                'total_words': total_words,
                'total_duration_seconds': stats['total_duration'] or 0,
                'avg_duration_seconds': round(stats['avg_duration'] or 0, 1),
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

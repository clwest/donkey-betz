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
            episodes = episodes.filter(status=status_filter)

        total_count = episodes.count()
        episodes = episodes[offset:offset + limit]

        # Format response
        episode_list = []
        for ep in episodes:
            episode_list.append({
                'id': str(ep.id),
                'topic': ep.topic,
                'format_type': ep.format_type,
                'status': ep.status,
                'participant_count': ep.participant_count,
                'has_audio': bool(ep.audio_file),
                'audio_url': ep.audio_file.url if ep.audio_file else None,
                'duration_seconds': ep.duration_seconds,
                'word_count': ep.word_count,
                'created_at': ep.created_at.isoformat(),
                'completed_at': ep.completed_at.isoformat() if ep.completed_at else None,
                'error_message': ep.error_message,
            })

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

        # Create episode record
        episode = PodcastEpisode.objects.create(
            user=request.user,
            topic=topic,
            format_type=format_type,
            participant_count=participant_count,
            status='pending',
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
            'episode': {
                'id': str(episode.id),
                'topic': episode.topic,
                'format_type': episode.format_type,
                'status': episode.status,
                'participant_count': episode.participant_count,
                'created_at': episode.created_at.isoformat(),
            },
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
            'episode': {
                'id': str(episode.id),
                'topic': episode.topic,
                'format_type': episode.format_type,
                'status': episode.status,
                'participant_count': episode.participant_count,
                'has_audio': bool(episode.audio_file),
                'audio_url': episode.audio_file.url if episode.audio_file else None,
                'duration_seconds': episode.duration_seconds,
                'word_count': episode.word_count,
                'created_at': episode.created_at.isoformat(),
                'completed_at': episode.completed_at.isoformat() if episode.completed_at else None,
                'error_message': episode.error_message,
            }
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
    from core.models import PodcastEpisode, PodcastDebate

    try:
        episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)

        # Get debate content if available
        debate = None
        try:
            debate = PodcastDebate.objects.filter(episode=episode).first()
        except:
            pass

        return JsonResponse({
            'success': True,
            'episode': {
                'id': str(episode.id),
                'topic': episode.topic,
                'format_type': episode.format_type,
                'status': episode.status,
            },
            'script': episode.script or '',
            'debate': {
                'research_summary': debate.research_summary if debate else '',
                'debate_transcript': debate.debate_transcript if debate else '',
                'key_insights': debate.key_insights if debate else [],
            } if debate else None,
            'word_count': episode.word_count,
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
        topic = episode.topic
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

        # Aggregate stats
        stats = episodes.filter(status='complete').aggregate(
            total_words=Sum('word_count'),
            total_duration=Sum('duration_seconds'),
            avg_duration=Avg('duration_seconds'),
        )

        return JsonResponse({
            'success': True,
            'stats': {
                'total_episodes': total,
                'complete': complete,
                'in_progress': in_progress,
                'failed': failed,
                'total_words': stats['total_words'] or 0,
                'total_duration_seconds': stats['total_duration'] or 0,
                'avg_duration_seconds': round(stats['avg_duration'] or 0, 1),
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

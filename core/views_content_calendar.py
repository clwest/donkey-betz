"""
Content Calendar API Views - Session 628 + 631 + 632
=====================================================

API endpoints for the Content Calendar feature, providing visibility
into scheduled and past autonomous content generation.

Endpoints:
- GET /api/content-calendar/ - Main calendar data (30-day window)
- GET /api/content-calendar/upcoming/ - Next 10 scheduled items
- GET /api/content-calendar/history/ - Past content with metrics
- POST /api/content-calendar/reschedule/ - Change schedule date
- GET /api/content-calendar/episode/<uuid>/ - Episode details with script (Session 631)
- POST /api/content-calendar/generate/<uuid>/ - Trigger content generation (Session 632)
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from core.auth_middleware import token_auth_required
from django.views.decorators.csrf import csrf_exempt

from core.models_autonomous_studio import (
    ContentChannel,
    ChannelEpisode,
    TopicPerformance,
    ChannelStatus,
)
from core.services.memory_context_service import get_memory_context_service

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def content_calendar_main(request):
    # Session 688: Removed @token_auth_required for React frontend access
    """
    GET /api/content-calendar/

    Returns main calendar data including:
    - Active channels
    - Upcoming content (next 30 days)
    - Past content (last 30 days)
    - Top performing topics
    - Calendar events for grid rendering
    """
    # Session 688: Handle anonymous users - return empty calendar data
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': True,
            'channels': [],
            'upcoming': [],
            'past_content': [],
            'top_topics': [],
            'calendar_events': [],
            'stats': {
                'total_channels': 0,
                'active_channels': 0,
                'scheduled_this_week': 0,
                'created_this_month': 0,
            }
        })

    user = request.user

    # Get user's channels
    channels = ContentChannel.objects.filter(user=user).order_by('-created_at')

    channels_data = []
    for channel in channels:
        channels_data.append({
            'id': str(channel.id),
            'name': channel.name,
            'topic_domain': channel.topic_domain,
            'target_audience': channel.target_audience,
            'content_frequency': channel.content_frequency,
            'status': channel.status,
            'visual_style': channel.visual_style,
            'voice_name': channel.voice_name or 'Default',
            'platform': channel.platform,
            'total_episodes': channel.total_episodes_created,
            'total_views': channel.total_views,
            'avg_retention': float(channel.avg_retention_rate),
            'next_content_due': channel.next_content_due.isoformat() if channel.next_content_due else None,
            'last_content_created': channel.last_content_created.isoformat() if channel.last_content_created else None,
        })

    # Get upcoming content (channels with upcoming due dates)
    now = timezone.now()
    upcoming_window = now + timedelta(days=30)

    upcoming_channels = ContentChannel.objects.filter(
        user=user,
        status=ChannelStatus.ACTIVE,
        next_content_due__lte=upcoming_window
    ).order_by('next_content_due')[:10]

    # Get user preferences for display
    memory_service = get_memory_context_service(user)
    content_prefs = memory_service.get_content_preferences(user)

    upcoming_data = []
    for channel in upcoming_channels:
        # Merge channel prefs with user prefs
        applied_prefs = {
            'visual_style': content_prefs.get('visual_style') or channel.visual_style,
            'voice_name': content_prefs.get('voice_name') or channel.voice_name,
            'content_tone': content_prefs.get('content_tone') or 'balanced',
        }

        upcoming_data.append({
            'channel_id': str(channel.id),
            'channel_name': channel.name,
            'next_due': channel.next_content_due.isoformat() if channel.next_content_due else None,
            'topic_domain': channel.topic_domain,
            'is_overdue': channel.is_content_due(),
            'preferences_applied': applied_prefs,
        })

    # Get past content (last 30 days)
    past_window = now - timedelta(days=30)
    past_episodes = ChannelEpisode.objects.filter(
        channel__user=user,
        created_at__gte=past_window
    ).select_related('channel').order_by('-created_at')[:20]

    past_data = []
    for episode in past_episodes:
        engagement = episode.likes + episode.comments + episode.shares
        past_data.append({
            'episode_id': str(episode.id),
            'title': episode.title,
            'topic': episode.topic,
            'channel_name': episode.channel.name,
            'channel_id': str(episode.channel.id),
            'publish_date': episode.publish_date.isoformat() if episode.publish_date else None,
            'created_at': episode.created_at.isoformat(),
            'views': episode.views,
            'engagement': engagement,
            'retention_rate': float(episode.retention_rate),
            'performance_score': float(episode.performance_score),
            'platform_url': episode.platform_url,
        })

    # Get top performing topics
    top_topics = TopicPerformance.objects.filter(
        channel__user=user
    ).order_by('-avg_performance_score')[:5]

    top_topics_data = []
    for topic in top_topics:
        top_topics_data.append({
            'topic': topic.topic,
            'channel_name': topic.channel.name if topic.channel else 'Unknown',
            'episode_count': topic.episode_count,
            'avg_views': topic.avg_views,
            'avg_performance': float(topic.avg_performance_score),
            'confidence': float(topic.confidence_score),
        })

    # Build calendar events for grid rendering
    calendar_events = []

    # Add upcoming scheduled content
    for channel in upcoming_channels:
        if channel.next_content_due:
            calendar_events.append({
                'date': channel.next_content_due.date().isoformat(),
                'type': 'scheduled',
                'title': f"Create: {channel.name}",
                'channel_id': str(channel.id),
                'is_overdue': channel.is_content_due(),
            })

    # Add past published content
    for episode in past_episodes:
        date = episode.publish_date or episode.created_at
        calendar_events.append({
            'date': date.date().isoformat(),
            'type': 'published',
            'title': episode.title,
            'channel_id': str(episode.channel.id),
            'episode_id': str(episode.id),
            'performance_score': float(episode.performance_score),
        })

    # Summary stats
    total_channels = channels.count()
    active_channels = channels.filter(status=ChannelStatus.ACTIVE).count()
    total_episodes = ChannelEpisode.objects.filter(channel__user=user).count()

    avg_performance = ChannelEpisode.objects.filter(
        channel__user=user
    ).exclude(performance_score=0)

    if avg_performance.exists():
        from django.db.models import Avg
        avg_perf = avg_performance.aggregate(avg=Avg('performance_score'))['avg']
        avg_performance_score = float(avg_perf) if avg_perf else 0
    else:
        avg_performance_score = 0

    return JsonResponse({
        'success': True,
        'channels': channels_data,
        'upcoming': upcoming_data,
        'past_30_days': past_data,
        'top_topics': top_topics_data,
        'calendar_events': calendar_events,
        'stats': {
            'total_channels': total_channels,
            'active_channels': active_channels,
            'total_episodes': total_episodes,
            'avg_performance_score': round(avg_performance_score, 2),
        },
        'user_preferences': content_prefs,
    })


@token_auth_required
@require_http_methods(["GET"])
def content_calendar_upcoming(request):
    """
    GET /api/content-calendar/upcoming/

    Returns next 10 scheduled content items with applied preferences.
    """
    user = request.user
    now = timezone.now()
    upcoming_window = now + timedelta(days=60)

    channels = ContentChannel.objects.filter(
        user=user,
        status=ChannelStatus.ACTIVE,
        next_content_due__lte=upcoming_window
    ).order_by('next_content_due')[:10]

    memory_service = get_memory_context_service(user)
    content_prefs = memory_service.get_content_preferences(user)

    upcoming = []
    for channel in channels:
        applied_prefs = {
            'visual_style': content_prefs.get('visual_style') or channel.visual_style,
            'voice_name': content_prefs.get('voice_name') or channel.voice_name,
        }

        # Get recent performance for this channel
        recent_episodes = ChannelEpisode.objects.filter(
            channel=channel
        ).order_by('-created_at')[:3]

        recent_performance = []
        for ep in recent_episodes:
            recent_performance.append({
                'title': ep.title,
                'score': float(ep.performance_score),
            })

        upcoming.append({
            'channel_id': str(channel.id),
            'channel_name': channel.name,
            'topic_domain': channel.topic_domain,
            'target_audience': channel.target_audience,
            'next_due': channel.next_content_due.isoformat(),
            'is_overdue': channel.is_content_due(),
            'days_until_due': (channel.next_content_due - now).days,
            'content_frequency': channel.content_frequency,
            'platform': channel.platform,
            'preferences_applied': applied_prefs,
            'recent_performance': recent_performance,
        })

    return JsonResponse({
        'success': True,
        'upcoming': upcoming,
        'count': len(upcoming),
    })


@token_auth_required
@require_http_methods(["GET"])
def content_calendar_history(request):
    """
    GET /api/content-calendar/history/

    Returns past content with performance metrics.
    Query params:
    - days: Number of days to look back (default 30, max 90)
    - channel_id: Filter by specific channel
    - limit: Max results (default 20, max 100)
    """
    user = request.user

    days = min(int(request.GET.get('days', 30)), 90)
    limit = min(int(request.GET.get('limit', 20)), 100)
    channel_id = request.GET.get('channel_id')

    past_window = timezone.now() - timedelta(days=days)

    query = ChannelEpisode.objects.filter(
        channel__user=user,
        created_at__gte=past_window
    ).select_related('channel')

    if channel_id:
        query = query.filter(channel_id=channel_id)

    episodes = query.order_by('-created_at')[:limit]

    history = []
    for episode in episodes:
        engagement = episode.likes + episode.comments + episode.shares
        engagement_rate = (engagement / episode.views * 100) if episode.views > 0 else 0

        history.append({
            'episode_id': str(episode.id),
            'title': episode.title,
            'topic': episode.topic,
            'description': episode.description[:200] if episode.description else '',
            'channel_name': episode.channel.name,
            'channel_id': str(episode.channel.id),
            'publish_date': episode.publish_date.isoformat() if episode.publish_date else None,
            'created_at': episode.created_at.isoformat(),
            'metrics': {
                'views': episode.views,
                'likes': episode.likes,
                'comments': episode.comments,
                'shares': episode.shares,
                'engagement': engagement,
                'engagement_rate': round(engagement_rate, 2),
                'watch_time_seconds': episode.watch_time_seconds,
                'retention_rate': float(episode.retention_rate),
                'performance_score': float(episode.performance_score),
            },
            'platform_url': episode.platform_url,
            'contributed_to_learning': episode.contributed_to_learning,
        })

    # Calculate summary stats
    if history:
        total_views = sum(h['metrics']['views'] for h in history)
        total_engagement = sum(h['metrics']['engagement'] for h in history)
        avg_performance = sum(h['metrics']['performance_score'] for h in history) / len(history)
    else:
        total_views = 0
        total_engagement = 0
        avg_performance = 0

    return JsonResponse({
        'success': True,
        'history': history,
        'count': len(history),
        'days_included': days,
        'summary': {
            'total_views': total_views,
            'total_engagement': total_engagement,
            'avg_performance_score': round(avg_performance, 2),
            'episode_count': len(history),
        },
    })


@token_auth_required
@csrf_exempt
@require_http_methods(["POST"])
def content_calendar_reschedule(request):
    """
    POST /api/content-calendar/reschedule/

    Reschedule content for a channel.
    Body:
    - channel_id: UUID of channel
    - new_date: ISO format date/time for next content
    """
    import json

    user = request.user

    try:
        data = json.loads(request.body)
        channel_id = data.get('channel_id')
        new_date_str = data.get('new_date')

        if not channel_id or not new_date_str:
            return JsonResponse({
                'success': False,
                'error': 'channel_id and new_date are required',
            }, status=400)

        # Parse the new date
        from dateutil import parser
        new_date = parser.parse(new_date_str)

        # Make timezone aware if needed
        if timezone.is_naive(new_date):
            new_date = timezone.make_aware(new_date)

        # Get the channel
        try:
            channel = ContentChannel.objects.get(id=channel_id, user=user)
        except ContentChannel.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Channel not found',
            }, status=404)

        # Update the schedule
        old_date = channel.next_content_due
        channel.next_content_due = new_date
        channel.save(update_fields=['next_content_due', 'updated_at'])

        logger.info(
            f"Session 628: Rescheduled {channel.name} from "
            f"{old_date.isoformat() if old_date else 'unset'} to {new_date.isoformat()}"
        )

        return JsonResponse({
            'success': True,
            'channel_id': str(channel.id),
            'channel_name': channel.name,
            'old_date': old_date.isoformat() if old_date else None,
            'new_date': new_date.isoformat(),
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)
    except Exception as e:
        logger.error(f"Error rescheduling content: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@token_auth_required
@require_http_methods(["GET"])
def content_calendar_episode_detail(request, episode_id):
    """
    GET /api/content-calendar/episode/<uuid>/

    Session 631: Returns full episode details including script content.

    Response includes:
    - Basic episode info (title, topic, dates)
    - Full script content
    - Debate information (if available)
    - Performance metrics
    - Channel context
    """
    user = request.user

    try:
        episode = ChannelEpisode.objects.select_related('channel', 'series').get(
            id=episode_id,
            channel__user=user
        )
    except ChannelEpisode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Episode not found',
        }, status=404)

    # Calculate engagement metrics
    engagement = episode.likes + episode.comments + episode.shares
    engagement_rate = (engagement / episode.views * 100) if episode.views > 0 else 0

    # Try to get debate info if it exists
    debate_info = None
    try:
        from core.models_autonomous_studio import ContentDebate
        # Look for debate that matches this episode's topic/time
        recent_debates = ContentDebate.objects.filter(
            channel=episode.channel,
            created_at__gte=episode.created_at - timedelta(hours=1),
            created_at__lte=episode.created_at + timedelta(hours=1),
        ).order_by('-created_at').first()

        if recent_debates:
            debate_info = {
                'id': str(recent_debates.id),
                'topic_debated': recent_debates.proposed_topic,
                'miner_argument': recent_debates.topic_miner_position,
                'contrarian_argument': recent_debates.contrarian_position,
                'analyst_argument': recent_debates.analyst_position,
                'winning_angle': recent_debates.chosen_angle,
                'decision_reasoning': recent_debates.decision_reasoning,
                'consensus_reached': recent_debates.consensus_reached,
                'created_at': recent_debates.created_at.isoformat(),
            }
    except Exception as e:
        logger.debug(f"Could not fetch debate info: {e}")

    # Build response
    response_data = {
        'success': True,
        'episode': {
            'id': str(episode.id),
            'title': episode.title,
            'topic': episode.topic,
            'description': episode.description,
            'script': episode.script,  # Session 630: Full script content
            'channel': {
                'id': str(episode.channel.id),
                'name': episode.channel.name,
                'topic_domain': episode.channel.topic_domain,
                'visual_style': episode.channel.visual_style,
                'voice_name': episode.channel.voice_name,
            },
            'series': {
                'id': str(episode.series.id) if episode.series else None,
                'name': episode.series.name if episode.series else None,
            },
            'dates': {
                'created_at': episode.created_at.isoformat(),
                'publish_date': episode.publish_date.isoformat() if episode.publish_date else None,
                'updated_at': episode.updated_at.isoformat() if hasattr(episode, 'updated_at') else None,
            },
            'metrics': {
                'views': episode.views,
                'likes': episode.likes,
                'comments': episode.comments,
                'shares': episode.shares,
                'engagement': engagement,
                'engagement_rate': round(engagement_rate, 2),
                'watch_time_seconds': episode.watch_time_seconds,
                'retention_rate': float(episode.retention_rate),
                'performance_score': float(episode.performance_score),
            },
            'platform_url': episode.platform_url,
            'contributed_to_learning': episode.contributed_to_learning,
        },
        'debate': debate_info,
    }

    return JsonResponse(response_data)


@token_auth_required
@csrf_exempt
@require_http_methods(["POST"])
def content_calendar_generate(request, channel_id):
    """
    POST /api/content-calendar/generate/<uuid>/

    Session 632: Trigger immediate content generation for a channel.

    This bypasses the Celery Beat schedule and triggers content generation
    on demand. The generation runs asynchronously via Celery task.

    Returns:
    - task_id: Celery task ID for tracking
    - channel info
    - message
    """
    user = request.user

    try:
        channel = ContentChannel.objects.get(id=channel_id, user=user)
    except ContentChannel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Channel not found',
        }, status=404)

    # Check if channel is active
    if channel.status != ChannelStatus.ACTIVE:
        return JsonResponse({
            'success': False,
            'error': f'Channel is {channel.status}, must be active to generate content',
        }, status=400)

    # Import and trigger the Celery task
    try:
        from core.tasks import generate_content_for_channel

        # Trigger async generation
        task = generate_content_for_channel.delay(str(channel.id))

        logger.info(
            f"Session 632: Manual content generation triggered for {channel.name} "
            f"by user {user.username}, task_id={task.id}"
        )

        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'channel_id': str(channel.id),
            'channel_name': channel.name,
            'message': f'Content generation started for {channel.name}. This may take 1-2 minutes.',
        })

    except Exception as e:
        logger.error(f"Error triggering content generation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# =============================================================================
# Session 741: Content Channels API - View all channels and episodes
# =============================================================================

@require_http_methods(["GET"])
def content_channels_list(request):
    """
    GET /api/v1/content-channels/

    Session 741: Returns all content channels with their episodes.
    This endpoint is for viewing the autonomous content creation system.

    Query params:
    - limit: Max episodes per channel (default 10)
    """
    limit = min(int(request.GET.get('limit', 10)), 50)
    workspace_id = request.GET.get('workspace', '').strip()

    channels = ContentChannel.objects.all().order_by('-created_at')

    # Workspace scoping: show workspace content + unlinked content
    if workspace_id:
        from django.db.models import Q
        channels = channels.filter(Q(workspace_id=workspace_id) | Q(workspace__isnull=True))

    channels_data = []
    for channel in channels:
        # Get recent episodes for this channel
        episodes = ChannelEpisode.objects.filter(
            channel=channel
        ).order_by('-created_at')[:limit]

        episodes_data = []
        for episode in episodes:
            engagement = episode.likes + episode.comments + episode.shares
            episodes_data.append({
                'id': str(episode.id),
                'title': episode.title,
                'topic': episode.topic,
                'description': episode.description[:200] if episode.description else '',
                'script_preview': episode.script[:500] if episode.script else '',
                'script_length': len(episode.script) if episode.script else 0,
                'has_full_script': bool(episode.script),
                'created_at': episode.created_at.isoformat(),
                'publish_date': episode.publish_date.isoformat() if episode.publish_date else None,
                'metrics': {
                    'views': episode.views,
                    'likes': episode.likes,
                    'comments': episode.comments,
                    'shares': episode.shares,
                    'engagement': engagement,
                    'retention_rate': float(episode.retention_rate),
                    'performance_score': float(episode.performance_score),
                },
                'platform_url': episode.platform_url,
            })

        channels_data.append({
            'id': str(channel.id),
            'name': channel.name,
            'topic_domain': channel.topic_domain,
            'target_audience': channel.target_audience,
            'content_frequency': channel.content_frequency,
            'status': channel.status,
            'is_active': channel.status == ChannelStatus.ACTIVE,  # Session 891: For frontend badge
            'visual_style': channel.visual_style,
            'voice_name': channel.voice_name or 'Default',
            'platform': channel.platform,
            'publish_automatically': channel.publish_automatically,
            'total_episodes': channel.total_episodes_created,
            'total_views': channel.total_views,
            'total_engagement': channel.total_engagement,
            'avg_retention': float(channel.avg_retention_rate),
            'next_content_due': channel.next_content_due.isoformat() if channel.next_content_due else None,
            'last_content_created': channel.last_content_created.isoformat() if channel.last_content_created else None,
            'created_at': channel.created_at.isoformat(),
            'episodes': episodes_data,
            'episode_count': ChannelEpisode.objects.filter(channel=channel).count(),
        })

    # Summary stats
    total_channels = channels.count()
    total_episodes = ChannelEpisode.objects.count()
    active_channels = channels.filter(status=ChannelStatus.ACTIVE).count()

    return JsonResponse({
        'success': True,
        'channels': channels_data,
        'stats': {
            'total_channels': total_channels,
            'active_channels': active_channels,
            'total_episodes': total_episodes,
        },
    })


@require_http_methods(["GET"])
def content_channel_detail(request, channel_id):
    """
    GET /api/v1/content-channels/<uuid>/

    Session 741: Returns detailed info for a specific channel with all episodes.
    """
    try:
        channel = ContentChannel.objects.get(id=channel_id)
    except ContentChannel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Channel not found',
        }, status=404)

    # Get all episodes for this channel
    episodes = ChannelEpisode.objects.filter(
        channel=channel
    ).order_by('-created_at')

    episodes_data = []
    for episode in episodes:
        engagement = episode.likes + episode.comments + episode.shares
        episodes_data.append({
            'id': str(episode.id),
            'title': episode.title,
            'topic': episode.topic,
            'description': episode.description,
            'script': episode.script,  # Full script
            'created_at': episode.created_at.isoformat(),
            'publish_date': episode.publish_date.isoformat() if episode.publish_date else None,
            'metrics': {
                'views': episode.views,
                'likes': episode.likes,
                'comments': episode.comments,
                'shares': episode.shares,
                'engagement': engagement,
                'retention_rate': float(episode.retention_rate),
                'performance_score': float(episode.performance_score),
            },
            'platform_url': episode.platform_url,
        })

    # Get debates for this channel
    from core.models_autonomous_studio import ContentDebate
    debates = ContentDebate.objects.filter(
        channel=channel
    ).order_by('-created_at')[:10]

    debates_data = []
    for debate in debates:
        debates_data.append({
            'id': str(debate.id),
            'proposed_topic': debate.proposed_topic,
            'proposed_by': debate.proposed_by,
            'topic_miner_position': debate.topic_miner_position,
            'contrarian_position': debate.contrarian_position,
            'analyst_position': debate.analyst_position,
            'final_decision': debate.final_decision,
            'chosen_angle': debate.chosen_angle,
            'consensus_reached': debate.consensus_reached,
            'content_created': debate.content_created,
            'created_at': debate.created_at.isoformat(),
        })

    return JsonResponse({
        'success': True,
        'channel': {
            'id': str(channel.id),
            'name': channel.name,
            'topic_domain': channel.topic_domain,
            'target_audience': channel.target_audience,
            'content_frequency': channel.content_frequency,
            'status': channel.status,
            'is_active': channel.status == ChannelStatus.ACTIVE,  # Session 891: For frontend badge
            'visual_style': channel.visual_style,
            'voice_name': channel.voice_name or 'Default',
            'platform': channel.platform,
            'publish_automatically': channel.publish_automatically,
            'total_episodes': channel.total_episodes_created,
            'total_views': channel.total_views,
            'total_engagement': channel.total_engagement,
            'avg_retention': float(channel.avg_retention_rate),
            'next_content_due': channel.next_content_due.isoformat() if channel.next_content_due else None,
            'last_content_created': channel.last_content_created.isoformat() if channel.last_content_created else None,
            'created_at': channel.created_at.isoformat(),
        },
        'episodes': episodes_data,
        'debates': debates_data,
        'episode_count': len(episodes_data),
    })


@require_http_methods(["GET"])
def content_episode_detail(request, episode_id):
    """
    GET /api/v1/content-channels/episode/<uuid>/

    Session 741: Returns full episode details including complete script.
    """
    try:
        episode = ChannelEpisode.objects.select_related('channel').get(id=episode_id)
    except ChannelEpisode.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Episode not found',
        }, status=404)

    engagement = episode.likes + episode.comments + episode.shares

    # Try to find associated debate
    debate_info = None
    try:
        from core.models_autonomous_studio import ContentDebate
        debate = ContentDebate.objects.filter(
            channel=episode.channel,
            created_at__gte=episode.created_at - timedelta(hours=2),
            created_at__lte=episode.created_at + timedelta(hours=1),
        ).order_by('-created_at').first()

        if debate:
            debate_info = {
                'id': str(debate.id),
                'proposed_topic': debate.proposed_topic,
                'topic_miner_position': debate.topic_miner_position,
                'contrarian_position': debate.contrarian_position,
                'analyst_position': debate.analyst_position,
                'final_decision': debate.final_decision,
                'chosen_angle': debate.chosen_angle,
                'consensus_reached': debate.consensus_reached,
            }
    except Exception as e:
        logger.debug(f"Could not fetch debate: {e}")

    return JsonResponse({
        'success': True,
        'episode': {
            'id': str(episode.id),
            'title': episode.title,
            'topic': episode.topic,
            'description': episode.description,
            'script': episode.script,
            'channel': {
                'id': str(episode.channel.id),
                'name': episode.channel.name,
                'platform': episode.channel.platform,
            },
            'created_at': episode.created_at.isoformat(),
            'publish_date': episode.publish_date.isoformat() if episode.publish_date else None,
            'metrics': {
                'views': episode.views,
                'likes': episode.likes,
                'comments': episode.comments,
                'shares': episode.shares,
                'engagement': engagement,
                'retention_rate': float(episode.retention_rate),
                'performance_score': float(episode.performance_score),
                'watch_time_seconds': episode.watch_time_seconds,
            },
            'platform_url': episode.platform_url,
        },
        'debate': debate_info,
    })

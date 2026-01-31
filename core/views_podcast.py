"""
Podcast Studio API Views - Session 502

Real API endpoints for the AI Podcast Studio.
Combines PodcastEpisode + ChannelEpisode (Autonomous Content Studio) into one unified view.
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def _podcast_episode_to_dict(ep):
    """Convert a PodcastEpisode to a dictionary for API response."""
    # Extract config values (stored in generation_config JSON field)
    config = ep.generation_config or {}
    format_type = config.get('format', 'debate')
    participant_count = config.get('participant_count', 3)

    # Calculate word count from script if available
    word_count = len(ep.script.split()) if ep.script else 0

    return {
        'id': str(ep.id),
        'source': 'podcast',  # Identify source table
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
        'description': ep.description or '',
    }


def _channel_episode_to_dict(ep):
    """Convert a ChannelEpisode to a dictionary for API response."""
    # ChannelEpisode doesn't have status, audio, etc. - it's published content
    # Determine format from channel if possible
    channel_name = ep.channel.name if ep.channel else ''

    return {
        'id': str(ep.id),
        'source': 'studio',  # Identify source as Autonomous Content Studio
        'topic': ep.title or ep.topic or 'Untitled',
        'format_type': 'content',  # These are content pieces, not debates
        'status': 'complete',  # ChannelEpisodes are published = complete
        'participant_count': 0,
        'has_audio': False,  # ChannelEpisodes typically don't have audio
        'audio_url': None,
        'duration_seconds': ep.watch_time_seconds or 0,
        'word_count': len(ep.script.split()) if ep.script else (len(ep.description.split()) if ep.description else 0),
        'created_at': ep.created_at.isoformat(),
        'completed_at': ep.publish_date.isoformat() if ep.publish_date else ep.created_at.isoformat(),
        'error_message': None,
        'description': ep.description or '',
        'channel': channel_name,
        'views': ep.views or 0,
        'platform_url': ep.platform_url or '',
    }


@require_http_methods(["GET"])
def podcast_list(request):
    """
    List all podcast episodes for the current user.
    Combines PodcastEpisode + ChannelEpisode (Autonomous Content Studio).

    GET /api/podcasts/list/

    Query params:
        - status: Filter by status (pending, researching, debating, scripting, generating_audio, complete, failed)
        - source: Filter by source (podcast, studio, or empty for all)
        - limit: Number of results (default 20)
        - offset: Pagination offset (default 0)

    Session 887: Added Token auth support since /api/podcasts/ is in PUBLIC_PATHS.
    """
    # Session 887: Manual auth check to support Token auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    # Return empty for anonymous users (still no auth)
    if not request.user.is_authenticated:
        return JsonResponse({'success': True, 'episodes': [], 'total': 0, 'limit': 20, 'offset': 0})

    from core.models_podcast_studio import PodcastEpisode
    from core.models_autonomous_studio import ChannelEpisode

    try:
        status_filter = request.GET.get('status', '')
        source_filter = request.GET.get('source', '')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        all_episodes = []

        # Get PodcastEpisode records (filtered by user)
        if not source_filter or source_filter == 'podcast':
            podcast_episodes = PodcastEpisode.objects.filter(user=request.user).order_by('-created_at')

            if status_filter:
                statuses = [s.strip() for s in status_filter.split(',')]
                podcast_episodes = podcast_episodes.filter(status__in=statuses)

            for ep in podcast_episodes:
                all_episodes.append(_podcast_episode_to_dict(ep))

        # Get ChannelEpisode records (all - they don't have user field)
        if not source_filter or source_filter == 'studio':
            channel_episodes = ChannelEpisode.objects.all().order_by('-created_at')

            # ChannelEpisodes are always "complete" - only include if status filter matches
            if status_filter:
                statuses = [s.strip() for s in status_filter.split(',')]
                if 'complete' not in statuses:
                    channel_episodes = ChannelEpisode.objects.none()

            for ep in channel_episodes:
                all_episodes.append(_channel_episode_to_dict(ep))

        # Sort combined list by created_at (descending)
        all_episodes.sort(key=lambda x: x['created_at'], reverse=True)

        total_count = len(all_episodes)

        # Apply pagination
        paginated_episodes = all_episodes[offset:offset + limit]

        # Get status counts
        podcast_count = PodcastEpisode.objects.filter(user=request.user).count()
        channel_count = ChannelEpisode.objects.count()

        status_counts = {
            'complete': (
                PodcastEpisode.objects.filter(user=request.user, status='complete').count() +
                channel_count  # All ChannelEpisodes are complete
            ),
            'pending': PodcastEpisode.objects.filter(user=request.user, status='pending').count(),
            'researching': PodcastEpisode.objects.filter(user=request.user, status='researching').count(),
            'debating': PodcastEpisode.objects.filter(user=request.user, status='debating').count(),
            'scripting': PodcastEpisode.objects.filter(user=request.user, status='scripting').count(),
            'generating_audio': PodcastEpisode.objects.filter(user=request.user, status='generating_audio').count(),
            'failed': PodcastEpisode.objects.filter(user=request.user, status='failed').count(),
        }

        return JsonResponse({
            'success': True,
            'episodes': paginated_episodes,
            'total_count': total_count,
            'status_counts': status_counts,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


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

    Session 887: Removed @login_required to support Token auth.
    """
    # Session 887: Manual auth check to support both session and Token auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    from core.models_podcast_studio import PodcastEpisode
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
            'episode': _podcast_episode_to_dict(episode),
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


@require_http_methods(["GET"])
def podcast_status(request, episode_id):
    """
    Get status of a specific podcast episode.

    GET /api/podcasts/<episode_id>/status/

    Session 889: Removed @login_required, added Token auth support.
    """
    # Session 889: Manual auth check to support Token auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    from core.models_podcast_studio import PodcastEpisode
    from core.models_autonomous_studio import ChannelEpisode

    try:
        # Try PodcastEpisode first
        try:
            episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)
            return JsonResponse({
                'success': True,
                'episode': _podcast_episode_to_dict(episode)
            })
        except PodcastEpisode.DoesNotExist:
            pass

        # Try ChannelEpisode
        try:
            episode = ChannelEpisode.objects.get(id=episode_id)
            return JsonResponse({
                'success': True,
                'episode': _channel_episode_to_dict(episode)
            })
        except ChannelEpisode.DoesNotExist:
            pass

        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def podcast_script(request, episode_id):
    """
    Get the full script of a podcast episode.

    GET /api/podcasts/<episode_id>/script/

    Session 889: Removed @login_required, added Token auth support.
    """
    # Session 889: Manual auth check to support Token auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    from core.models_podcast_studio import PodcastEpisode
    from core.models_autonomous_studio import ChannelEpisode

    try:
        # Try PodcastEpisode first
        try:
            episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)
            config = episode.generation_config or {}
            format_type = config.get('format', 'debate')

            # Get debate data - episode.debate is a ForeignKey to PodcastDebate model
            debate_info = None
            if episode.debate:
                debate_obj = episode.debate
                debate_info = {
                    'research_summary': str(debate_obj.research_results) if debate_obj.research_results else '',
                    'debate_transcript': debate_obj.debate_transcript or '',
                    'key_insights': debate_obj.key_takeaways or [],
                    'consensus': debate_obj.consensus or '',
                    'winner': debate_obj.winner or '',
                }

            return JsonResponse({
                'success': True,
                'episode': {
                    'id': str(episode.id),
                    'topic': episode.topic or episode.title,
                    'format_type': format_type,
                    'status': episode.status,
                },
                'script': episode.script or '',
                'debate': debate_info,
                'word_count': len(episode.script.split()) if episode.script else 0,
            })
        except PodcastEpisode.DoesNotExist:
            pass

        # Try ChannelEpisode
        try:
            episode = ChannelEpisode.objects.get(id=episode_id)
            # Session 634: Use script field (added Session 630) instead of description
            script_content = episode.script or episode.description or ''

            # Session 634: Include 3-agent debate content
            from core.models_autonomous_studio import ContentDebate
            debate_info = None
            try:
                debate = ContentDebate.objects.filter(channel=episode.channel).order_by('-created_at').first()
                if debate:
                    debate_info = {
                        'topic': debate.proposed_topic,
                        'proposed_by': debate.proposed_by,
                        'topic_miner': debate.topic_miner_position or '',
                        'contrarian': debate.contrarian_position or '',
                        'analyst': debate.analyst_position or '',
                        'decision_reasoning': debate.decision_reasoning or '',
                        'consensus_reached': debate.consensus_reached,
                    }
            except Exception:
                pass

            return JsonResponse({
                'success': True,
                'episode': {
                    'id': str(episode.id),
                    'topic': episode.title or episode.topic,
                    'format_type': 'content',
                    'status': 'complete',
                },
                'script': script_content,
                'debate': debate_info,
                'word_count': len(script_content.split()) if script_content else 0,
            })
        except ChannelEpisode.DoesNotExist:
            pass

        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def podcast_delete(request, episode_id):
    """
    Delete a podcast episode.

    DELETE /api/podcasts/<episode_id>/

    Session 889: Removed @login_required, added Token auth support.
    """
    # Session 889: Manual auth check to support Token auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    from core.models_podcast_studio import PodcastEpisode
    from core.models_autonomous_studio import ChannelEpisode

    try:
        # Try PodcastEpisode first
        try:
            episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)
            topic = episode.topic or episode.title
            episode.delete()
            return JsonResponse({
                'success': True,
                'message': f'Podcast "{topic}" deleted'
            })
        except PodcastEpisode.DoesNotExist:
            pass

        # Try ChannelEpisode
        try:
            episode = ChannelEpisode.objects.get(id=episode_id)
            topic = episode.title or episode.topic
            episode.delete()
            return JsonResponse({
                'success': True,
                'message': f'Content "{topic}" deleted'
            })
        except ChannelEpisode.DoesNotExist:
            pass

        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def podcast_generate_audio(request, episode_id):
    """
    Session 865: Generate TTS audio for an existing podcast episode.

    POST /api/podcasts/<episode_id>/generate-audio/

    Body (optional):
        - voice_profile_id: UUID of a VoiceProfile to use for all speakers

    Works for both PodcastEpisode and ChannelEpisode.
    For ChannelEpisode, creates a linked PodcastEpisode with audio.

    Session 889: Removed @login_required, added Token auth support.
    """
    # Session 889: Manual auth check to support Token auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    import logging
    logger = logging.getLogger(__name__)

    from core.models_podcast_studio import PodcastEpisode
    from core.models_autonomous_studio import ChannelEpisode
    from core.services.podcast_audio_service import generate_podcast_audio
    from core.models_voice_marketplace import VoiceProfile

    try:
        # Parse request body for voice_profile_id
        data = json.loads(request.body) if request.body else {}
        voice_profile_id = data.get('voice_profile_id')

        # Get custom ElevenLabs voice ID if a profile is specified
        custom_voice_id = None
        if voice_profile_id:
            try:
                voice_profile = VoiceProfile.objects.get(id=voice_profile_id)
                custom_voice_id = voice_profile.elevenlabs_voice_id
                logger.info(f"🎤 Using custom voice: {voice_profile.name} ({custom_voice_id})")
            except VoiceProfile.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Voice profile not found'
                }, status=404)

        # Try PodcastEpisode first
        try:
            episode = PodcastEpisode.objects.get(id=episode_id, user=request.user)

            if not episode.script:
                return JsonResponse({
                    'success': False,
                    'error': 'Episode has no script to convert to audio'
                }, status=400)

            if episode.audio_url or episode.audio_file:
                return JsonResponse({
                    'success': False,
                    'error': 'Episode already has audio. Delete and recreate to regenerate.'
                }, status=400)

            # Generate audio - the service handles status updates
            episode.status = 'generating_audio'
            episode.save()

            result = generate_podcast_audio(
                episode_id=str(episode.id),
                custom_voice_id=custom_voice_id,
            )

            if result['success']:
                # Refresh episode from DB (audio service updates it)
                episode.refresh_from_db()
                return JsonResponse({
                    'success': True,
                    'audio_url': result.get('audio_url'),
                    'duration_seconds': result.get('duration_seconds'),
                    'segment_count': result.get('segment_count'),
                    'total_cost': str(result.get('total_cost', 0)),
                    'message': 'Audio generated successfully'
                })
            else:
                episode.status = 'failed'
                episode.error_message = result.get('error', 'Audio generation failed')
                episode.save()
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Audio generation failed')
                }, status=500)

        except PodcastEpisode.DoesNotExist:
            pass

        # Try ChannelEpisode - convert script to audio
        try:
            channel_ep = ChannelEpisode.objects.get(id=episode_id)

            script = channel_ep.script or channel_ep.description
            if not script:
                return JsonResponse({
                    'success': False,
                    'error': 'Episode has no script/content to convert to audio'
                }, status=400)

            # Create a PodcastEpisode to store the audio
            podcast_ep = PodcastEpisode.objects.create(
                user=request.user,
                topic=channel_ep.title or channel_ep.topic,
                title=channel_ep.title or channel_ep.topic,
                script=script,
                status='generating_audio',
                generation_config={
                    'source': 'channel_episode',
                    'channel_episode_id': str(channel_ep.id),
                    'generate_audio': True,
                }
            )

            result = generate_podcast_audio(
                episode_id=str(podcast_ep.id),
                custom_voice_id=custom_voice_id,
            )

            if result['success']:
                podcast_ep.refresh_from_db()
                return JsonResponse({
                    'success': True,
                    'podcast_episode_id': str(podcast_ep.id),
                    'audio_url': result.get('audio_url'),
                    'duration_seconds': result.get('duration_seconds'),
                    'segment_count': result.get('segment_count'),
                    'total_cost': str(result.get('total_cost', 0)),
                    'message': 'Audio generated successfully. New podcast episode created.'
                })
            else:
                podcast_ep.status = 'failed'
                podcast_ep.error_message = result.get('error', 'Audio generation failed')
                podcast_ep.save()
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Audio generation failed')
                }, status=500)

        except ChannelEpisode.DoesNotExist:
            pass

        return JsonResponse({
            'success': False,
            'error': 'Episode not found'
        }, status=404)

    except Exception as e:
        import traceback
        logger.error(f"Audio generation error: {e}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def podcast_stats(request):
    # Session 688: Removed @login_required for React frontend access
    """
    Get podcast statistics for the current user.
    Combines PodcastEpisode + ChannelEpisode stats.

    GET /api/podcasts/stats/
    """
    # Session 887: Manual auth check to support Token auth
    # /api/podcasts/ is in PUBLIC_PATHS so middleware skips auth
    from rest_framework.authtoken.models import Token

    if not request.user.is_authenticated:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
            except Token.DoesNotExist:
                pass

    # Return empty stats for anonymous users (still no auth after Token check)
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': True,
            'total_episodes': 0,
            'complete': 0,
            'in_progress': 0,
            'failed': 0,
            'with_scripts': 0,
            'with_audio': 0,
            'processing': 0,
        })

    from core.models_podcast_studio import PodcastEpisode
    from core.models_autonomous_studio import ChannelEpisode
    from django.db.models import Sum

    try:
        # PodcastEpisode stats
        podcast_episodes = PodcastEpisode.objects.filter(user=request.user)
        podcast_total = podcast_episodes.count()
        podcast_complete = podcast_episodes.filter(status='complete').count()
        podcast_in_progress = podcast_episodes.filter(
            status__in=['pending', 'researching', 'debating', 'scripting', 'generating_audio']
        ).count()
        podcast_failed = podcast_episodes.filter(status='failed').count()

        # ChannelEpisode stats (all are "complete")
        channel_episodes = ChannelEpisode.objects.all()
        channel_total = channel_episodes.count()

        # Combined totals
        total = podcast_total + channel_total
        complete = podcast_complete + channel_total
        in_progress = podcast_in_progress
        failed = podcast_failed

        # Calculate duration from both sources
        podcast_duration = podcast_episodes.filter(status='complete').aggregate(
            total=Sum('audio_duration_seconds')
        )['total'] or 0

        channel_duration = channel_episodes.aggregate(
            total=Sum('watch_time_seconds')
        )['total'] or 0

        total_duration = podcast_duration + channel_duration

        # Calculate total words from scripts
        total_words = 0
        for ep in podcast_episodes.filter(status='complete'):
            if ep.script:
                total_words += len(ep.script.split())
        for ep in channel_episodes:
            if ep.description:
                total_words += len(ep.description.split())

        return JsonResponse({
            'success': True,
            'stats': {
                'total_episodes': total,
                'complete': complete,
                'in_progress': in_progress,
                'failed': failed,
                'total_words': total_words,
                'total_duration_seconds': total_duration,
                'avg_duration_seconds': round(total_duration / complete, 1) if complete > 0 else 0,
                # Breakdown by source
                'podcast_count': podcast_total,
                'studio_count': channel_total,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

"""
Preferences Dashboard API
=========================

Session 206: Created for Phase A1 - Preferences Dashboard

Provides API endpoints for viewing and managing user preferences
learned by the AgentPreferenceManager.

Endpoints:
    GET  /api/preferences/              - Get all preferences
    GET  /api/preferences/{domain}/     - Get domain preferences
    PUT  /api/preferences/{domain}/     - Update preferences
    DELETE /api/preferences/{domain}/   - Clear preferences
    GET  /api/preferences/history/      - Preference history
    POST /api/preferences/learn/        - Trigger batch learning
"""

import logging

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

# Session 727: Migrated to core/services/preference_manager.py
from core.services.preference_manager import AgentPreferenceManager

logger = logging.getLogger(__name__)

# Valid preference domains
VALID_DOMAINS = ['image', 'video', 'audio', 'research']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_preferences(request):
    """
    Get all user preferences across all domains.

    Returns:
        {
            'success': True,
            'preferences': {
                'image': {...},
                'video': {...},
                'audio': {...},
                'research': {...},
                'learning_stage': 'learning'
            }
        }
    """
    try:
        manager = AgentPreferenceManager(request.user)
        preferences = manager.get_preference_summary()

        return Response({
            'success': True,
            'preferences': preferences,
            'domains': VALID_DOMAINS,
            'defaults': manager.DEFAULT_PREFERENCES
        })

    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def domain_preferences(request, domain: str):
    """
    Get, update, or clear preferences for a specific domain.

    Args:
        domain: 'image', 'video', 'audio', or 'research'
    """
    if domain not in VALID_DOMAINS:
        return Response({
            'success': False,
            'error': f"Invalid domain: {domain}. Valid domains: {VALID_DOMAINS}"
        }, status=status.HTTP_400_BAD_REQUEST)

    manager = AgentPreferenceManager(request.user)

    if request.method == 'GET':
        return _get_domain_preferences(manager, domain)
    elif request.method == 'PUT':
        return _update_domain_preferences(request, manager, domain)
    elif request.method == 'DELETE':
        return _clear_domain_preferences(manager, domain)


def _get_domain_preferences(manager: AgentPreferenceManager, domain: str) -> Response:
    """Get preferences for a specific domain."""
    try:
        preferences = manager.get_preferences(domain)
        defaults = manager.DEFAULT_PREFERENCES.get(domain, {})

        # Identify which values are defaults vs learned
        learned = {}
        for key, value in preferences.items():
            default_value = defaults.get(key)
            learned[key] = value != default_value

        return Response({
            'success': True,
            'domain': domain,
            'preferences': preferences,
            'defaults': defaults,
            'learned': learned,  # Which values were learned vs default
            'learning_stage': manager._get_learning_stage()
        })

    except Exception as e:
        logger.error(f"Error getting {domain} preferences: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _update_domain_preferences(request, manager: AgentPreferenceManager, domain: str) -> Response:
    """Update preferences for a specific domain."""
    try:
        data = request.data
        updated = {}

        for key, value in data.items():
            if key in manager.DEFAULT_PREFERENCES.get(domain, {}):
                # Record as a strong preference (weight=2.0 for manual setting)
                success = manager.record_preference(
                    domain=domain,
                    preference_type=key,
                    value=value,
                    weight=2.0  # Higher weight for explicit user settings
                )
                if success:
                    updated[key] = value

        return Response({
            'success': True,
            'domain': domain,
            'updated': updated,
            'message': f"Updated {len(updated)} preferences for {domain}"
        })

    except Exception as e:
        logger.error(f"Error updating {domain} preferences: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _clear_domain_preferences(manager: AgentPreferenceManager, domain: str) -> Response:
    """Clear preferences for a specific domain."""
    try:
        success = manager.clear_preferences(domain)

        return Response({
            'success': success,
            'domain': domain,
            'message': f"Cleared preferences for {domain}" if success else "Failed to clear preferences"
        })

    except Exception as e:
        logger.error(f"Error clearing {domain} preferences: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all_preferences(request):
    """Clear all preferences across all domains."""
    try:
        manager = AgentPreferenceManager(request.user)
        success = manager.clear_preferences(None)  # None = clear all

        return Response({
            'success': success,
            'message': "Cleared all preferences" if success else "Failed to clear preferences"
        })

    except Exception as e:
        logger.error(f"Error clearing all preferences: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preference_history(request):
    """
    Get preference history/evolution over time.

    Query params:
        domain: Filter by domain (optional)
        limit: Number of records (default 50)
    """
    try:
        domain = request.query_params.get('domain')
        limit = int(request.query_params.get('limit', 50))

        # Get history from StyleMemory model
        from style_memory.models import StyleMemory

        queryset = StyleMemory.objects.filter(user=request.user)

        if domain:
            # Filter by domain-related interaction types
            domain_interactions = {
                'image': ['love', 'like', 'dislike', 'rate_1', 'rate_2', 'rate_3', 'rate_4', 'rate_5'],
                'video': ['video_like', 'video_save'],
                'audio': ['audio_like', 'voice_preference'],
            }
            interactions = domain_interactions.get(domain, [])
            if interactions:
                queryset = queryset.filter(interaction_type__in=interactions)

        history = queryset.order_by('-created_at')[:limit]

        history_data = [{
            'id': str(item.id),
            'interaction_type': item.interaction_type,
            'style_elements': item.style_elements,
            'prompt': item.prompt,
            'created_at': item.created_at.isoformat(),
        } for item in history]

        return Response({
            'success': True,
            'history': history_data,
            'count': len(history_data),
            'domain_filter': domain
        })

    except Exception as e:
        logger.error(f"Error getting preference history: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learn_from_project(request):
    """
    Trigger batch learning from a project's content.

    Request body:
        {
            'project_id': 'uuid-string'
        }
    """
    try:
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({
                'success': False,
                'error': "project_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        manager = AgentPreferenceManager(request.user, project_id=project_id)

        # Get project content and learn
        from content.models import ImageHistory, Project

        # Verify project ownership
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return Response({
                'success': False,
                'error': "Project not found or access denied"
            }, status=status.HTTP_404_NOT_FOUND)

        # Get images in project
        images = ImageHistory.objects.filter(
            user=request.user,
            project=project
        )

        if not images.exists():
            return Response({
                'success': False,
                'error': "No images found in project"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Analyze and learn
        from collections import Counter

        style_counts = Counter()
        model_counts = Counter()
        aspect_counts = Counter()

        for image in images:
            if hasattr(image, 'style') and image.style:
                style_counts[image.style] += 1
            if hasattr(image, 'model') and image.model:
                model_counts[image.model] += 1
            if hasattr(image, 'aspect_ratio') and image.aspect_ratio:
                aspect_counts[image.aspect_ratio] += 1

        # Record learned preferences
        learned = {'styles': [], 'models': [], 'aspect_ratios': []}

        for style, count in style_counts.most_common(3):
            weight = min(2.0, count / len(images) * 3)  # Weight based on frequency
            manager.record_preference('image', 'style', style, weight=weight)
            learned['styles'].append({'value': style, 'count': count})

        for model, count in model_counts.most_common(2):
            weight = min(2.0, count / len(images) * 3)
            manager.record_preference('image', 'model', model, weight=weight)
            learned['models'].append({'value': model, 'count': count})

        for aspect, count in aspect_counts.most_common(2):
            weight = min(2.0, count / len(images) * 3)
            manager.record_preference('image', 'aspect_ratio', aspect, weight=weight)
            learned['aspect_ratios'].append({'value': aspect, 'count': count})

        return Response({
            'success': True,
            'project_id': project_id,
            'project_name': project.name,
            'images_analyzed': images.count(),
            'learned': learned,
            'message': f"Learned preferences from {images.count()} images"
        })

    except Exception as e:
        logger.error(f"Error learning from project: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preference_stats(request):
    """
    Get statistics about user's preference learning.
    """
    try:
        manager = AgentPreferenceManager(request.user)

        # Get learning stage
        learning_stage = manager._get_learning_stage()

        # Count preference interactions
        from style_memory.models import StyleMemory
        from content.models import UserCreativePreference

        interaction_count = StyleMemory.objects.filter(user=request.user).count()

        # Get creative preference stats
        try:
            creative_prefs = UserCreativePreference.objects.get(user=request.user)
            total_choices = creative_prefs.total_choices
            preferred_styles_count = len(creative_prefs.preferred_styles or [])
            preferred_models_count = len(creative_prefs.preferred_models or [])
        except UserCreativePreference.DoesNotExist:
            total_choices = 0
            preferred_styles_count = 0
            preferred_models_count = 0

        return Response({
            'success': True,
            'stats': {
                'learning_stage': learning_stage,
                'total_interactions': interaction_count,
                'total_choices': total_choices,
                'preferred_styles_count': preferred_styles_count,
                'preferred_models_count': preferred_models_count,
            },
            'learning_stages': {
                'new': 'Less than 5 choices',
                'learning': '5-20 choices',
                'established': 'More than 20 choices'
            }
        })

    except Exception as e:
        logger.error(f"Error getting preference stats: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# SESSION 206: SMART STYLE SUGGESTIONS
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def smart_style_suggestions(request):
    """
    Get smart style suggestions based on user preferences and history.

    GET: Get suggestions for a prompt or general suggestions
    POST: Get suggestions with context (prompt, recent images, project)

    Query params (GET):
        prompt: Optional prompt to analyze for suggestions
        domain: 'image', 'video', 'audio' (default: 'image')
        limit: Number of suggestions (default: 5)

    Request body (POST):
        {
            'prompt': 'optional prompt',
            'domain': 'image',
            'context': {
                'recent_image_ids': [],
                'project_id': 'uuid'
            }
        }
    """
    try:
        # Get parameters
        if request.method == 'POST':
            prompt = request.data.get('prompt', '')
            domain = request.data.get('domain', 'image')
            context = request.data.get('context', {})
            limit = request.data.get('limit', 5)
        else:
            prompt = request.query_params.get('prompt', '')
            domain = request.query_params.get('domain', 'image')
            context = {}
            limit = int(request.query_params.get('limit', 5))

        manager = AgentPreferenceManager(request.user)
        preferences = manager.get_preferences(domain)

        suggestions = []

        # Get style suggestions based on preferences
        if domain == 'image':
            suggestions = _get_image_style_suggestions(
                request.user,
                preferences,
                prompt,
                context,
                limit
            )
        elif domain == 'video':
            suggestions = _get_video_style_suggestions(
                request.user,
                preferences,
                prompt,
                limit
            )
        elif domain == 'audio':
            suggestions = _get_audio_style_suggestions(
                request.user,
                preferences,
                prompt,
                limit
            )

        return Response({
            'success': True,
            'domain': domain,
            'suggestions': suggestions,
            'preferences_applied': bool(preferences),
            'prompt_analyzed': bool(prompt)
        })

    except Exception as e:
        logger.error(f"Error getting style suggestions: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _get_image_style_suggestions(user, preferences, prompt, context, limit):
    """Generate smart image style suggestions."""
    suggestions = []

    # Base styles available in the system
    available_styles = [
        {'id': 'photorealistic', 'name': 'Photorealistic', 'description': 'Ultra-realistic photography style'},
        {'id': 'digital-art', 'name': 'Digital Art', 'description': 'Modern digital illustration'},
        {'id': 'anime', 'name': 'Anime', 'description': 'Japanese animation style'},
        {'id': 'cinematic', 'name': 'Cinematic', 'description': 'Movie poster / film style'},
        {'id': 'fantasy-art', 'name': 'Fantasy Art', 'description': 'Epic fantasy illustration'},
        {'id': 'neon-punk', 'name': 'Neon Punk', 'description': 'Cyberpunk neon aesthetic'},
        {'id': '3d-model', 'name': '3D Model', 'description': 'Rendered 3D graphics'},
        {'id': 'pixel-art', 'name': 'Pixel Art', 'description': 'Retro pixel graphics'},
        {'id': 'watercolor', 'name': 'Watercolor', 'description': 'Traditional watercolor painting'},
        {'id': 'oil-painting', 'name': 'Oil Painting', 'description': 'Classic oil painting style'},
        {'id': 'comic-book', 'name': 'Comic Book', 'description': 'Bold comic illustration'},
        {'id': 'sketch', 'name': 'Sketch', 'description': 'Hand-drawn pencil sketch'},
    ]

    # Score each style based on user preferences and prompt
    scored_styles = []

    for style in available_styles:
        score = 50  # Base score

        # Boost if matches user's preferred style
        if preferences.get('style') == style['id']:
            score += 30
            style['reason'] = 'Your preferred style'

        # Analyze prompt for style hints
        if prompt:
            prompt_lower = prompt.lower()
            style_keywords = {
                'photorealistic': ['realistic', 'photo', 'real', 'portrait', 'photograph'],
                'anime': ['anime', 'manga', 'japanese', 'kawaii'],
                'cinematic': ['movie', 'film', 'dramatic', 'epic', 'poster'],
                'fantasy-art': ['fantasy', 'dragon', 'magic', 'wizard', 'castle'],
                'neon-punk': ['cyberpunk', 'neon', 'futuristic', 'tech', 'cyber'],
                '3d-model': ['3d', 'render', 'model', 'cgi'],
                'pixel-art': ['pixel', 'retro', '8-bit', 'game'],
                'watercolor': ['watercolor', 'soft', 'gentle', 'pastel'],
                'comic-book': ['comic', 'superhero', 'action', 'bold'],
            }

            for keyword in style_keywords.get(style['id'], []):
                if keyword in prompt_lower:
                    score += 20
                    if 'reason' not in style:
                        style['reason'] = f'Matches "{keyword}" in your prompt'
                    break

        # Check user's style memory for this style
        try:
            from style_memory.models import StyleMemory
            style_uses = StyleMemory.objects.filter(
                user=user,
                style_elements__style=style['id']
            ).count()
            if style_uses > 0:
                score += min(20, style_uses * 5)
                if 'reason' not in style:
                    style['reason'] = f'Used {style_uses} times before'
        except Exception as _e:
            logger.warning(
                "views_preferences._get_image_style_suggestions: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        scored_styles.append({**style, 'score': score})

    # Sort by score and return top suggestions
    scored_styles.sort(key=lambda x: x['score'], reverse=True)

    for style in scored_styles[:limit]:
        suggestions.append({
            'style_id': style['id'],
            'style_name': style['name'],
            'description': style['description'],
            'confidence': min(100, style['score']),
            'reason': style.get('reason', 'Popular style choice'),
            'preview_prompt': f"Create a {style['name'].lower()} style image"
        })

    return suggestions


def _get_video_style_suggestions(user, preferences, prompt, limit):
    """Generate smart video style suggestions."""
    suggestions = []

    # Video motion styles
    motion_styles = [
        {'id': 'smooth', 'name': 'Smooth Motion', 'description': 'Elegant, flowing movement'},
        {'id': 'dynamic', 'name': 'Dynamic Action', 'description': 'Fast-paced, energetic motion'},
        {'id': 'cinematic', 'name': 'Cinematic Pan', 'description': 'Slow, dramatic camera movement'},
        {'id': 'zoom', 'name': 'Zoom Effect', 'description': 'Gradual zoom in or out'},
        {'id': 'orbit', 'name': 'Orbital Motion', 'description': 'Camera orbits around subject'},
    ]

    for i, style in enumerate(motion_styles[:limit]):
        confidence = 80 - (i * 10)
        if preferences.get('motion_style') == style['id']:
            confidence = 95

        suggestions.append({
            'style_id': style['id'],
            'style_name': style['name'],
            'description': style['description'],
            'confidence': confidence,
            'reason': 'Popular motion style' if confidence < 90 else 'Your preferred motion'
        })

    return suggestions


def _get_audio_style_suggestions(user, preferences, prompt, limit):
    """Generate smart audio/voice suggestions."""
    suggestions = []

    # Voice styles
    voices = [
        {'id': '21m00Tcm4TlvDq8ikWAM', 'name': 'Rachel', 'description': 'Professional, clear voice'},
        {'id': 'AZnzlk1XvdvUeBnXmlld', 'name': 'Domi', 'description': 'Friendly, conversational'},
        {'id': 'EXAVITQu4vr4xnSDxMaL', 'name': 'Bella', 'description': 'Warm, expressive tone'},
        {'id': 'MF3mGyEYCl7XYWbV9V6O', 'name': 'Elli', 'description': 'Young, energetic voice'},
    ]

    for i, voice in enumerate(voices[:limit]):
        confidence = 85 - (i * 10)
        if preferences.get('voice_id') == voice['id']:
            confidence = 95

        suggestions.append({
            'style_id': voice['id'],
            'style_name': voice['name'],
            'description': voice['description'],
            'confidence': confidence,
            'reason': 'Popular voice' if confidence < 90 else 'Your preferred voice'
        })

    return suggestions


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_style_suggestion(request):
    """
    Apply a style suggestion to user preferences.

    Request body:
        {
            'domain': 'image',
            'style_id': 'photorealistic'
        }
    """
    try:
        domain = request.data.get('domain', 'image')
        style_id = request.data.get('style_id')

        if not style_id:
            return Response({
                'success': False,
                'error': 'style_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        manager = AgentPreferenceManager(request.user)

        # Record as preference
        if domain == 'image':
            manager.record_preference(domain, 'style', style_id, weight=1.5)
        elif domain == 'video':
            manager.record_preference(domain, 'motion_style', style_id, weight=1.5)
        elif domain == 'audio':
            manager.record_preference(domain, 'voice_id', style_id, weight=1.5)

        return Response({
            'success': True,
            'message': f'Applied {style_id} to your {domain} preferences',
            'domain': domain,
            'style_id': style_id
        })

    except Exception as e:
        logger.error(f"Error applying style suggestion: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# SESSION 210: IMPLICIT LEARNING & RECOMMENDATIONS API
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_behavior(request):
    """
    Track user behavior for implicit learning.

    Request body:
        {
            'signal_type': 'download' | 'share' | 'delete' | 'favorite' | 'view',
            'content_id': 'uuid-or-string',
            'style': 'optional-style-name',
            'model': 'optional-model-name',
            'metadata': {}  # optional additional data
        }
    """
    try:
        from core.services import get_learning_service

        signal_type = request.data.get('signal_type')
        content_id = request.data.get('content_id')
        style = request.data.get('style')
        model = request.data.get('model')
        metadata = request.data.get('metadata', {})

        if not signal_type:
            return Response({
                'success': False,
                'error': 'signal_type is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_signals = ['download', 'share', 'delete', 'favorite', 'view', 'regenerate', 'style_use']
        if signal_type not in valid_signals:
            return Response({
                'success': False,
                'error': f'Invalid signal_type. Valid: {valid_signals}'
            }, status=status.HTTP_400_BAD_REQUEST)

        service = get_learning_service()
        user_id = request.user.id

        # Route to appropriate tracking method
        if signal_type == 'download':
            service.track_download(user_id, content_id, style, model)
        elif signal_type == 'share':
            platform = metadata.get('platform')
            service.track_share(user_id, content_id, style, model, platform)
        elif signal_type == 'delete':
            service.track_delete(user_id, content_id, style, model)
        elif signal_type == 'favorite':
            service.track_favorite(user_id, content_id, style, model)
        elif signal_type == 'view':
            seconds = metadata.get('seconds', 5)
            service.track_view_time(user_id, content_id, seconds, style, model)
        elif signal_type == 'regenerate':
            new_content_id = metadata.get('new_content_id', '')
            service.track_regenerate(user_id, content_id, new_content_id, style, model)
        elif signal_type == 'style_use':
            context = metadata.get('context')
            service.track_style_selection(user_id, style, context)

        return Response({
            'success': True,
            'signal_type': signal_type,
            'content_id': content_id,
            'message': f'Tracked {signal_type} signal'
        })

    except Exception as e:
        logger.error(f"Error tracking behavior: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_implicit_preferences(request):
    """
    Get user's implicit preference profile from behavioral signals.

    Query params:
        days: Look-back period in days (default: 90)
    """
    try:
        from core.services import get_learning_service

        days = int(request.query_params.get('days', 90))
        service = get_learning_service()

        preferences = service.calculate_preference_scores(request.user.id, days)
        behavior_summary = service.get_behavior_summary(request.user.id, days=30)

        return Response({
            'success': True,
            'preferences': preferences,
            'behavior_summary': behavior_summary
        })

    except Exception as e:
        logger.error(f"Error getting implicit preferences: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([])  # No authentication required for anonymous access
@permission_classes([AllowAny])
def get_style_recommendations(request):
    """
    Get personalized style recommendations.

    Works for both authenticated and anonymous users:
    - Authenticated: Personalized recommendations based on behavior
    - Anonymous: Fallback popular/trending recommendations

    Query params:
        limit: Number of recommendations (default: 10)
        include_trending: Include trending styles (default: true)
        include_temporal: Include time-appropriate styles (default: true)
    """
    try:
        from core.services import get_recommendation_engine

        limit = int(request.query_params.get('limit', 10))
        include_trending = request.query_params.get('include_trending', 'true').lower() == 'true'
        include_temporal = request.query_params.get('include_temporal', 'true').lower() == 'true'

        engine = get_recommendation_engine()

        # Get user ID if authenticated, otherwise use 0 for anonymous
        user_id = request.user.id if request.user.is_authenticated else 0

        recommendations = engine.get_style_recommendations(
            user_id=user_id,
            limit=limit,
            include_trending=include_trending,
            include_temporal=include_temporal
        )

        return Response({
            'success': True,
            'recommendations': [r.to_dict() for r in recommendations],
            'count': len(recommendations),
            'personalized': request.user.is_authenticated
        })

    except Exception as e:
        logger.error(f"Error getting style recommendations: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_similar_styles(request, style: str):
    """
    Get styles similar to a given style.

    "Because you liked {style}, you might also like..."

    Query params:
        limit: Number of recommendations (default: 5)
    """
    try:
        from core.services import get_recommendation_engine

        limit = int(request.query_params.get('limit', 5))
        engine = get_recommendation_engine()

        recommendations = engine.get_similar_style_recommendations(
            user_id=request.user.id,
            base_style=style,
            limit=limit
        )

        return Response({
            'success': True,
            'base_style': style,
            'recommendations': [r.to_dict() for r in recommendations],
            'count': len(recommendations)
        })

    except Exception as e:
        logger.error(f"Error getting similar styles: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_discovery_styles(request):
    """
    Get discovery recommendations - styles the user hasn't tried but might like.

    Query params:
        limit: Number of recommendations (default: 5)
    """
    try:
        from core.services import get_recommendation_engine

        limit = int(request.query_params.get('limit', 5))
        engine = get_recommendation_engine()

        recommendations = engine.get_discovery_recommendations(
            user_id=request.user.id,
            limit=limit
        )

        return Response({
            'success': True,
            'recommendations': [r.to_dict() for r in recommendations],
            'count': len(recommendations),
            'title': 'Discover New Styles'
        })

    except Exception as e:
        logger.error(f"Error getting discovery styles: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# SESSION 210: STYLE EVOLUTION TRACKING
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_style_evolution(request):
    """
    Get user's style preference evolution over time.

    Shows how preferences have changed and identifies trends.

    Query params:
        days: Look-back period (default: 30)
        domain: Content domain - image, video, audio, 3d (default: image)
    """
    try:
        from core.services import get_learning_service

        days = int(request.query_params.get('days', 30))
        domain = request.query_params.get('domain', 'image')

        service = get_learning_service()
        evolution = service.get_style_evolution_history(
            user_id=request.user.id,
            days=days,
            domain=domain
        )

        return Response({
            'success': True,
            'evolution': evolution
        })

    except Exception as e:
        logger.error(f"Error getting style evolution: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_evolution_snapshot(request):
    """
    Manually trigger a style evolution snapshot for the current user.

    Normally this runs daily via Celery, but this endpoint allows
    manual triggering for testing or when needed.

    Request body:
        {
            'domain': 'image'  # optional, default: 'image'
        }
    """
    try:
        from core.services import get_learning_service

        domain = request.data.get('domain', 'image')

        service = get_learning_service()
        result = service.record_daily_evolution(
            user_id=request.user.id,
            domain=domain
        )

        if result:
            return Response({
                'success': True,
                'snapshot': result,
                'message': 'Evolution snapshot recorded'
            })
        else:
            return Response({
                'success': False,
                'message': 'No style data to record (try using some styles first)'
            })

    except Exception as e:
        logger.error(f"Error recording evolution snapshot: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_style_shifts(request):
    """
    Detect significant shifts in user's style preferences.

    Returns shifts like:
    - New favorite styles
    - Declining interest in previously favored styles
    - Rapidly growing interest in new styles

    Query params:
        domain: Content domain (default: image)
    """
    try:
        from core.services import get_learning_service

        domain = request.query_params.get('domain', 'image')

        service = get_learning_service()
        shifts = service.detect_style_shifts(
            user_id=request.user.id,
            domain=domain
        )

        return Response({
            'success': True,
            'shifts': shifts
        })

    except Exception as e:
        logger.error(f"Error detecting style shifts: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# SESSION 211: A/B TESTING API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def list_experiments(request):
    """
    List all A/B experiments.

    Query params:
        status: Filter by status (draft, running, paused, completed, cancelled)
        domain: Filter by domain
    """
    try:
        from core.models_unified_system import ABExperiment

        qs = ABExperiment.objects.all()

        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        domain_filter = request.query_params.get('domain')
        if domain_filter:
            qs = qs.filter(domain=domain_filter)

        experiments = []
        for exp in qs[:50]:
            experiments.append({
                'id': str(exp.id),
                'name': exp.name,
                'description': exp.description,
                'experiment_type': exp.experiment_type,
                'domain': exp.domain,
                'status': exp.status,
                'traffic_percentage': exp.traffic_percentage,
                'start_date': str(exp.start_date) if exp.start_date else None,
                'end_date': str(exp.end_date) if exp.end_date else None,
                'created_at': str(exp.created_at),
            })

        return Response({
            'success': True,
            'experiments': experiments,
            'count': len(experiments),
        })

    except Exception as e:
        logger.error(f"Error listing experiments: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_experiment(request):
    """
    Create a new A/B experiment.

    Request body:
        {
            'name': 'Experiment Name',
            'description': 'What this tests',
            'experiment_type': 'recommendation',  # recommendation, ui, feature, algorithm
            'domain': 'style_recommendations',
            'traffic_percentage': 100,
            'variants': [
                {'name': 'control', 'is_control': true, 'weight': 50, 'config': {}},
                {'name': 'variant_a', 'is_control': false, 'weight': 50, 'config': {}}
            ]
        }
    """
    try:
        from core.services import get_ab_testing_service

        service = get_ab_testing_service()
        result = service.create_experiment(
            name=request.data.get('name', 'Unnamed Experiment'),
            description=request.data.get('description', ''),
            experiment_type=request.data.get('experiment_type', 'recommendation'),
            domain=request.data.get('domain', 'style_recommendations'),
            traffic_percentage=request.data.get('traffic_percentage', 100),
            variants=request.data.get('variants'),
            config=request.data.get('config'),
            created_by_id=request.user.id,
        )

        return Response({
            'success': True,
            'experiment': result,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating experiment: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_experiment(request, experiment_id):
    """Start an experiment (set status to 'running')."""
    try:
        from core.services import get_ab_testing_service

        service = get_ab_testing_service()
        result = service.start_experiment(experiment_id)

        return Response({
            'success': True,
            'experiment': result,
        })

    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error starting experiment: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_experiment(request, experiment_id):
    """
    Stop an experiment.

    Request body:
        {
            'status': 'completed'  # completed, paused, cancelled
        }
    """
    try:
        from core.services import get_ab_testing_service

        service = get_ab_testing_service()
        result = service.stop_experiment(
            experiment_id,
            status=request.data.get('status', 'completed')
        )

        return Response({
            'success': True,
            'experiment': result,
        })

    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error stopping experiment: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_experiment_results(request, experiment_id):
    """
    Get comprehensive results for an experiment.

    Includes per-variant stats and statistical significance.
    """
    try:
        from core.services import get_ab_testing_service

        service = get_ab_testing_service()
        results = service.get_experiment_results(experiment_id)

        return Response({
            'success': True,
            'results': results,
        })

    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting experiment results: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_my_variant(request, experiment_id):
    """
    Get the variant assignment for the current user.

    Works for both authenticated and anonymous users.
    """
    try:
        from core.services import get_ab_testing_service

        service = get_ab_testing_service()

        # Get user ID or session ID
        user_id = request.user.id if request.user.is_authenticated else None
        session_id = request.session.session_key if not user_id else None

        variant = service.get_variant_for_user(
            experiment_id=experiment_id,
            user_id=user_id,
            session_id=session_id,
        )

        if variant:
            # Mark exposure
            service.mark_exposure(experiment_id, user_id, session_id)

            return Response({
                'success': True,
                'variant': {
                    'experiment_id': variant.experiment_id,
                    'experiment_name': variant.experiment_name,
                    'variant_id': variant.variant_id,
                    'variant_name': variant.variant_name,
                    'config': variant.config,
                    'is_control': variant.is_control,
                }
            })
        else:
            return Response({
                'success': True,
                'variant': None,
                'message': 'Not enrolled in this experiment'
            })

    except Exception as e:
        logger.error(f"Error getting variant: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def track_ab_conversion(request, experiment_id):
    """
    Track a conversion for an A/B experiment.

    Request body:
        {
            'conversion_type': 'apply',  # click, apply, download, share, etc.
            'value': 1.0,  # optional
            'metadata': {}  # optional
        }
    """
    try:
        from core.services import get_ab_testing_service

        service = get_ab_testing_service()

        user_id = request.user.id if request.user.is_authenticated else None
        session_id = request.session.session_key if not user_id else None

        success = service.track_conversion(
            experiment_id=experiment_id,
            conversion_type=request.data.get('conversion_type', 'click'),
            user_id=user_id,
            session_id=session_id,
            value=request.data.get('value', 1.0),
            metadata=request.data.get('metadata'),
        )

        return Response({
            'success': success,
            'message': 'Conversion recorded' if success else 'No assignment found'
        })

    except Exception as e:
        logger.error(f"Error tracking conversion: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

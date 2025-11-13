"""
CreativeDirectorAgent API Endpoints

Session 90 - Partnership Model API
Philosophy: AI suggests → Human chooses → Agent learns → Gets better!
"""

import json
import logging
from typing import Dict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from ai_core.agents.creative_director_agent import CreativeDirectorAgent
from content.models import ImageHistory

logger = logging.getLogger(__name__)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def generate_options(request) -> JsonResponse:
    """
    Generate multiple creative options for user to choose from.

    This is the core of the partnership model:
    - AI generates 3-5 diverse options
    - User picks their favorite
    - Agent learns from the choice

    POST /api/creative-director/generate-options/
    Body:
        {
            "prompt": "Modern coffee shop logo with mountain silhouette",
            "count": 3,  # Optional, default: 3
            "style": "photographic",  # Optional
            "model": "sdxl",  # Optional
            "width": 1024,  # Optional, default: 1024
            "height": 1024  # Optional, default: 1024
        }

    Returns:
        {
            "success": true,
            "batch_id": "uuid-string",
            "options": [
                {
                    "id": 123,
                    "image_url": "https://...",
                    "seed": 123456,
                    "option_number": 1,
                    "model": "sdxl",
                    "style": "photographic",
                    "reasoning": "Exploring new creative possibilities"
                },
                ...
            ],
            "learning_message": "Here are 3 creative options! Pick your favorite...",
            "total_choices": 0,
            "learning_stage": "new"
        }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        prompt = data.get('prompt')

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Optional parameters
        count = data.get('count', 3)
        style = data.get('style')
        model = data.get('model')
        width = data.get('width', 1024)
        height = data.get('height', 1024)

        # Validate count
        if count < 1 or count > 5:
            return JsonResponse({
                'success': False,
                'error': 'Count must be between 1 and 5'
            }, status=400)

        # Initialize agent
        agent = CreativeDirectorAgent(user=request.user)

        # Generate options
        result = agent.generate_options(
            prompt=prompt,
            count=count,
            style=style,
            model=model,
            width=width,
            height=height
        )

        logger.info(
            f"CreativeDirector generated {len(result['options'])} options "
            f"for user {request.user.id}"
        )

        return JsonResponse({
            'success': True,
            **result
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)

    except Exception as e:
        logger.error(
            f"Error generating options for user {request.user.id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def record_choice(request) -> JsonResponse:
    """
    Record user's choice - THIS IS HOW THE AGENT LEARNS!

    Every choice teaches the agent about user preferences.

    POST /api/creative-director/record-choice/
    Body:
        {
            "image_id": 123
        }

    Returns:
        {
            "success": true,
            "insights": {
                "style": "Learning you prefer 'photographic' style",
                "model": "Learning you prefer 'sdxl' model"
            },
            "total_choices": 1,
            "learning_stage": "learning",
            "message": "First choice recorded! I'm starting to learn your taste."
        }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        image_id = data.get('image_id')

        if not image_id:
            return JsonResponse({
                'success': False,
                'error': 'image_id is required'
            }, status=400)

        # Initialize agent
        agent = CreativeDirectorAgent(user=request.user)

        # Record choice
        result = agent.record_choice(selected_image_id=image_id)

        if result['success']:
            logger.info(
                f"CreativeDirector recorded choice for user {request.user.id}: "
                f"image_id={image_id}, total_choices={result['total_choices']}"
            )
        else:
            logger.warning(
                f"CreativeDirector failed to record choice for user {request.user.id}: "
                f"{result.get('error')}"
            )

        status_code = 200 if result['success'] else 400
        return JsonResponse(result, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)

    except Exception as e:
        logger.error(
            f"Error recording choice for user {request.user.id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_recommendation(request) -> JsonResponse:
    """
    Get smart recommendations based on learned preferences.

    Available after user has made 5+ choices.

    GET /api/creative-director/recommendation/?prompt=coffee+shop+logo

    Returns:
        {
            "success": true,
            "has_recommendation": true,
            "recommendation": {
                "recommended_style": "photographic",
                "recommended_model": "sdxl",
                "reasoning": "Based on 10 choices, you consistently prefer 'photographic' style.",
                "confidence": 0.7
            },
            "total_choices": 10,
            "learning_stage": "knows_taste"
        }

    Or if not enough data:
        {
            "success": true,
            "has_recommendation": false,
            "message": "Make 5 choices for personalized recommendations",
            "total_choices": 2,
            "learning_stage": "learning"
        }
    """
    try:
        prompt = request.GET.get('prompt', '')

        # Initialize agent
        agent = CreativeDirectorAgent(user=request.user)

        # Get recommendation
        recommendation = agent.get_smart_recommendation(prompt=prompt)

        if recommendation:
            logger.info(
                f"CreativeDirector provided recommendation for user {request.user.id}"
            )

            return JsonResponse({
                'success': True,
                'has_recommendation': True,
                'recommendation': recommendation,
                'total_choices': agent.preferences.total_choices,
                'learning_stage': agent.preferences.get_learning_stage()
            })
        else:
            choices_needed = 5 - agent.preferences.total_choices

            return JsonResponse({
                'success': True,
                'has_recommendation': False,
                'message': f"Make {choices_needed} more choice{'s' if choices_needed > 1 else ''} for personalized recommendations",
                'total_choices': agent.preferences.total_choices,
                'learning_stage': agent.preferences.get_learning_stage()
            })

    except Exception as e:
        logger.error(
            f"Error getting recommendation for user {request.user.id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_user_preferences(request) -> JsonResponse:
    """
    Get user's current creative preferences and learning progress.

    GET /api/creative-director/preferences/

    Returns:
        {
            "success": true,
            "preferences": {
                "preferred_styles": ["photographic", "cinematic"],
                "preferred_models": ["sdxl", "ultra"],
                "total_choices": 10,
                "learning_stage": "knows_taste",
                "can_make_recommendations": true
            }
        }
    """
    try:
        # Initialize agent
        agent = CreativeDirectorAgent(user=request.user)

        # Get state summary
        state = agent.get_state_summary()

        logger.info(f"CreativeDirector retrieved preferences for user {request.user.id}")

        return JsonResponse({
            'success': True,
            'preferences': {
                'preferred_styles': state['preferred_styles'],
                'preferred_models': state['preferred_models'],
                'total_choices': state['total_choices'],
                'learning_stage': state['learning_stage'],
                'can_make_recommendations': state['can_make_recommendations']
            }
        })

    except Exception as e:
        logger.error(
            f"Error retrieving preferences for user {request.user.id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_batch_history(request) -> JsonResponse:
    """
    Get history of all generation batches with selection status.

    Useful for showing user what they've generated and chosen.

    GET /api/creative-director/batch-history/?limit=10

    Returns:
        {
            "success": true,
            "batches": [
                {
                    "batch_id": "uuid-string",
                    "created_at": "2025-11-13T04:30:00Z",
                    "options_count": 3,
                    "selected_option": {
                        "id": 123,
                        "image_url": "https://...",
                        "seed": 123456,
                        "style": "photographic",
                        "model": "sdxl"
                    }
                },
                ...
            ],
            "total_batches": 5,
            "total_choices": 5
        }
    """
    try:
        limit = int(request.GET.get('limit', 10))

        # Get all batches for user
        batches_query = ImageHistory.objects.filter(
            user=request.user,
            generation_batch_id__isnull=False
        ).values('generation_batch_id').distinct()[:limit]

        batches = []
        for batch in batches_query:
            batch_id = batch['generation_batch_id']

            # Get all options in this batch
            options = ImageHistory.objects.filter(
                generation_batch_id=batch_id,
                user=request.user
            ).order_by('option_number')

            if options.exists():
                first_option = options.first()
                selected_option = options.filter(was_selected=True).first()

                batch_data = {
                    'batch_id': str(batch_id),
                    'created_at': first_option.created_at.isoformat(),
                    'options_count': options.count(),
                    'prompt': first_option.prompt
                }

                if selected_option:
                    batch_data['selected_option'] = {
                        'id': selected_option.id,
                        'image_url': selected_option.image_url,
                        'seed': selected_option.seed,
                        'style': selected_option.style,
                        'model': selected_option.model,
                        'option_number': selected_option.option_number
                    }

                batches.append(batch_data)

        # Get total choices
        total_choices = ImageHistory.objects.filter(
            user=request.user,
            was_selected=True
        ).count()

        logger.info(f"CreativeDirector retrieved batch history for user {request.user.id}")

        return JsonResponse({
            'success': True,
            'batches': batches,
            'total_batches': len(batches),
            'total_choices': total_choices
        })

    except Exception as e:
        logger.error(
            f"Error retrieving batch history for user {request.user.id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

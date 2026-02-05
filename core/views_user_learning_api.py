"""
Session 930: User Learning System API Endpoints

API endpoints for:
- Agent feedback (👍/👎)
- Profile completeness
- Goal progress tracking
- Skill evolution
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from core.services.agent_feedback_service import get_agent_feedback_service
from core.services.profile_completeness_service import get_profile_completeness_service
from core.services.goal_tracking_service import get_goal_tracking_service
from core.services.skill_evolution_service import get_skill_evolution_service

logger = logging.getLogger(__name__)


# =============================================================================
# Agent Feedback Endpoints
# =============================================================================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def record_agent_feedback(request):
    """
    Record user feedback on an agent execution.

    POST /api/user-learning/feedback/

    Body:
    {
        "agent_id": "uuid",
        "rating": 1,  // 1=helpful, 0=neutral, -1=not helpful
        "execution_id": "optional uuid",
        "deliverable_id": "optional uuid",
        "feedback_text": "optional text",
        "task_description": "what user was trying to do",
        "context_snapshot": {}
    }
    """
    try:
        data = json.loads(request.body)

        agent_id = data.get('agent_id')
        rating = data.get('rating')

        if not agent_id or rating is None:
            return JsonResponse({
                'success': False,
                'error': 'agent_id and rating are required'
            }, status=400)

        if rating not in [1, 0, -1]:
            return JsonResponse({
                'success': False,
                'error': 'rating must be 1, 0, or -1'
            }, status=400)

        from core.models import Agent, Deliverable

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Agent {agent_id} not found'
            }, status=404)

        deliverable = None
        if data.get('deliverable_id'):
            try:
                deliverable = Deliverable.objects.get(id=data['deliverable_id'])
            except Deliverable.DoesNotExist:
                pass  # Not critical

        service = get_agent_feedback_service()
        feedback = service.record_feedback(
            user=request.user,
            agent=agent,
            rating=rating,
            execution_id=data.get('execution_id'),
            deliverable=deliverable,
            feedback_text=data.get('feedback_text', ''),
            task_description=data.get('task_description', ''),
            context_snapshot=data.get('context_snapshot', {}),
        )

        return JsonResponse({
            'success': True,
            'feedback_id': str(feedback.id),
            'message': 'Feedback recorded successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_agent_effectiveness(request, agent_id):
    """
    Get effectiveness metrics for a user+agent combination.

    GET /api/user-learning/effectiveness/<agent_id>/
    """
    try:
        from core.models import Agent

        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Agent {agent_id} not found'
            }, status=404)

        service = get_agent_feedback_service()
        effectiveness = service.get_agent_effectiveness(request.user, agent)

        return JsonResponse({
            'success': True,
            'data': {
                'agent_id': effectiveness.agent_id,
                'agent_name': effectiveness.agent_name,
                'total_feedbacks': effectiveness.total_feedbacks,
                'helpful_count': effectiveness.helpful_count,
                'not_helpful_count': effectiveness.not_helpful_count,
                'neutral_count': effectiveness.neutral_count,
                'effectiveness_score': effectiveness.effectiveness_score,
                'recent_trend': effectiveness.recent_trend,
                'top_successful_contexts': effectiveness.top_successful_contexts,
                'areas_for_improvement': effectiveness.areas_for_improvement,
            }
        })

    except Exception as e:
        logger.error(f"Error getting effectiveness: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_user_agent_summary(request):
    """
    Get summary of all agent effectiveness for the user.

    GET /api/user-learning/agent-summary/
    """
    try:
        service = get_agent_feedback_service()
        summary = service.get_user_agent_summary(request.user)

        return JsonResponse({
            'success': True,
            'data': summary
        })

    except Exception as e:
        logger.error(f"Error getting agent summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Profile Completeness Endpoints
# =============================================================================

@login_required
@require_http_methods(["GET"])
def get_profile_completeness(request):
    """
    Get profile completeness score and gaps.

    GET /api/user-learning/profile-completeness/
    """
    try:
        service = get_profile_completeness_service()
        stats = service.get_completion_stats(request.user)

        return JsonResponse({
            'success': True,
            'data': stats
        })

    except Exception as e:
        logger.error(f"Error getting profile completeness: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_next_profile_question(request):
    """
    Get the next question to ask user about their profile.

    GET /api/user-learning/profile-next-question/
    Query params:
    - context: optional context string for prioritization
    """
    try:
        context = request.GET.get('context', '')

        service = get_profile_completeness_service()

        if context:
            prompt = service.get_contextual_prompt(request.user, context)
        else:
            gap = service.get_next_question(request.user)
            prompt = gap.prompt_question if gap else None

        if not prompt:
            return JsonResponse({
                'success': True,
                'data': {
                    'complete': True,
                    'message': 'Profile is complete!'
                }
            })

        return JsonResponse({
            'success': True,
            'data': {
                'complete': False,
                'prompt': prompt
            }
        })

    except Exception as e:
        logger.error(f"Error getting next question: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def record_profile_response(request):
    """
    Record user's response to a profile prompt.

    POST /api/user-learning/profile-response/

    Body:
    {
        "field_name": "skills",
        "value": "Python, Django, React",
        "completed": true
    }
    """
    try:
        data = json.loads(request.body)

        field_name = data.get('field_name')
        value = data.get('value', '')
        completed = data.get('completed', True)

        if not field_name:
            return JsonResponse({
                'success': False,
                'error': 'field_name is required'
            }, status=400)

        service = get_profile_completeness_service()
        service.record_response(
            user=request.user,
            field_name=field_name,
            value=value,
            completed=completed,
        )

        # Return updated completeness
        stats = service.get_completion_stats(request.user)

        return JsonResponse({
            'success': True,
            'message': 'Response recorded',
            'completeness': stats
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error recording response: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Goal Tracking Endpoints
# =============================================================================

@login_required
@require_http_methods(["GET"])
def get_goals_dashboard(request):
    """
    Get dashboard of all user goals with progress.

    GET /api/user-learning/goals/
    """
    try:
        service = get_goal_tracking_service()
        dashboard = service.get_user_goals_dashboard(request.user)

        return JsonResponse({
            'success': True,
            'data': dashboard
        })

    except Exception as e:
        logger.error(f"Error getting goals dashboard: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_goal_detail(request, goal_id):
    """
    Get detailed summary of a specific goal.

    GET /api/user-learning/goals/<goal_id>/
    """
    try:
        from core.models import UserGoal

        try:
            goal = UserGoal.objects.get(id=goal_id, user=request.user)
        except UserGoal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Goal {goal_id} not found'
            }, status=404)

        service = get_goal_tracking_service()
        summary = service.get_goal_summary(goal)

        return JsonResponse({
            'success': True,
            'data': {
                'goal_id': summary.goal_id,
                'name': summary.name,
                'category': summary.category,
                'target_value': summary.target_value,
                'current_value': summary.current_value,
                'progress_percentage': summary.progress_percentage,
                'status': summary.status,
                'recent_contributions': summary.recent_contributions,
                'milestones_reached': summary.milestones_reached,
                'days_remaining': summary.days_remaining,
            }
        })

    except Exception as e:
        logger.error(f"Error getting goal detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def record_goal_progress(request, goal_id):
    """
    Record manual progress toward a goal.

    POST /api/user-learning/goals/<goal_id>/progress/

    Body:
    {
        "progress_delta": 10,
        "milestone": "Completed first draft",
        "notes": "Optional notes"
    }
    """
    try:
        data = json.loads(request.body)

        from core.models import UserGoal

        try:
            goal = UserGoal.objects.get(id=goal_id, user=request.user)
        except UserGoal.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Goal {goal_id} not found'
            }, status=404)

        progress_delta = data.get('progress_delta')
        if progress_delta is None:
            return JsonResponse({
                'success': False,
                'error': 'progress_delta is required'
            }, status=400)

        service = get_goal_tracking_service()
        progress = service.record_manual_progress(
            goal=goal,
            progress_delta=progress_delta,
            milestone=data.get('milestone', ''),
            notes=data.get('notes', ''),
        )

        # Get updated summary
        summary = service.get_goal_summary(goal)

        return JsonResponse({
            'success': True,
            'progress_id': str(progress.id),
            'new_progress': summary.progress_percentage,
            'message': 'Progress recorded'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error recording progress: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Skill Evolution Endpoints
# =============================================================================

@login_required
@require_http_methods(["GET"])
def get_skills_summary(request):
    """
    Get comprehensive skills summary for dashboard.

    GET /api/user-learning/skills/
    """
    try:
        service = get_skill_evolution_service()
        summary = service.get_skills_summary(request.user)

        return JsonResponse({
            'success': True,
            'data': summary
        })

    except Exception as e:
        logger.error(f"Error getting skills summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_skill_growth_chart(request):
    """
    Get skill levels over time for visualization.

    GET /api/user-learning/skills/growth/
    Query params:
    - months: number of months to look back (default 6)
    """
    try:
        months = int(request.GET.get('months', 6))
        months = max(1, min(24, months))  # Clamp 1-24

        service = get_skill_evolution_service()
        chart_data = service.get_skill_growth_chart(request.user, months)

        return JsonResponse({
            'success': True,
            'data': chart_data
        })

    except Exception as e:
        logger.error(f"Error getting skill growth: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def record_skill_demonstration(request):
    """
    Manually record a skill demonstration.

    POST /api/user-learning/skills/demonstrate/

    Body:
    {
        "skill_name": "Python",
        "category": "technical",
        "quality_score": 0.8,
        "context": "How skill was demonstrated",
        "deliverable_id": "optional uuid"
    }
    """
    try:
        data = json.loads(request.body)

        skill_name = data.get('skill_name')
        category = data.get('category', 'technical')
        quality_score = data.get('quality_score', 0.7)

        if not skill_name:
            return JsonResponse({
                'success': False,
                'error': 'skill_name is required'
            }, status=400)

        # Validate category
        valid_categories = [
            'technical', 'creative', 'analytical',
            'communication', 'leadership', 'domain'
        ]
        if category not in valid_categories:
            category = 'technical'

        # Validate quality score
        quality_score = max(0.0, min(1.0, float(quality_score)))

        deliverable = None
        if data.get('deliverable_id'):
            from core.models import Deliverable
            try:
                deliverable = Deliverable.objects.get(id=data['deliverable_id'])
            except Deliverable.DoesNotExist:
                pass

        service = get_skill_evolution_service()
        demo = service.record_skill_demonstration(
            user=request.user,
            skill_name=skill_name,
            category=category,
            quality_score=quality_score,
            deliverable=deliverable,
            context=data.get('context', ''),
            inference_source='manual',
        )

        return JsonResponse({
            'success': True,
            'demonstration_id': str(demo.id),
            'message': 'Skill demonstration recorded'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Error recording skill demonstration: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_skill_recommendations(request):
    """
    Get skill improvement recommendations.

    GET /api/user-learning/skills/recommendations/
    """
    try:
        service = get_skill_evolution_service()
        recommendations = service.get_skill_recommendations(request.user)

        return JsonResponse({
            'success': True,
            'data': recommendations
        })

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Combined User Learning Summary
# =============================================================================

@login_required
@require_http_methods(["GET"])
def get_user_learning_summary(request):
    """
    Get combined learning summary across all dimensions.

    GET /api/user-learning/summary/
    """
    try:
        feedback_service = get_agent_feedback_service()
        profile_service = get_profile_completeness_service()
        goal_service = get_goal_tracking_service()
        skill_service = get_skill_evolution_service()

        return JsonResponse({
            'success': True,
            'data': {
                'profile': profile_service.get_completion_stats(request.user),
                'agents': feedback_service.get_user_agent_summary(request.user),
                'goals': goal_service.get_user_goals_dashboard(request.user),
                'skills': skill_service.get_skills_summary(request.user),
            }
        })

    except Exception as e:
        logger.error(f"Error getting learning summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

"""
Learning Journey API Views
Session 773: Real implementation replacing stubs

Endpoints for managing learning journeys, templates, steps, and achievements.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count
import logging

from core.models_learning_journey import (
    LearningJourney,
    LearningJourneyStep,
    LearningJourneyTemplate,
    LearningAchievement,
    UserLearningAchievement,
    UserLearningStreak,
)

logger = logging.getLogger(__name__)


# =============================================================================
# JOURNEY MANAGEMENT
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journeys_list(request):
    """GET /api/learning/journeys/ - List user's learning journeys"""
    try:
        journeys = LearningJourney.objects.filter(user=request.user)
        return Response({
            'journeys': [j.to_dict() for j in journeys],
            'total': journeys.count()
        })
    except Exception as e:
        logger.error(f"Error listing journeys: {e}")
        return Response({'journeys': [], 'total': 0, 'error': str(e)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journeys_active(request):
    """GET /api/learning/journeys/active/ - Active journeys only"""
    try:
        journeys = LearningJourney.objects.filter(
            user=request.user,
            status__in=['active', 'paused']
        )
        return Response({
            'journeys': [j.to_dict() for j in journeys],
            'total': journeys.count()
        })
    except Exception as e:
        logger.error(f"Error getting active journeys: {e}")
        return Response({'journeys': [], 'total': 0, 'error': str(e)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journey_detail(request, journey_id):
    """GET /api/learning/journeys/<id>/ - Journey detail"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        return Response({
            'success': True,
            'journey': journey.to_dict()
        })
    except LearningJourney.DoesNotExist:
        return Response({'success': False, 'error': 'Journey not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting journey detail: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_start(request):
    """POST /api/learning/journeys/start/ - Start a new journey from template"""
    try:
        template_id = request.data.get('template_id')
        topic = request.data.get('topic', '')
        goals = request.data.get('goals', [])

        if template_id:
            template = LearningJourneyTemplate.objects.get(id=template_id)
            template.popularity += 1
            template.save(update_fields=['popularity'])

            # Create journey from template
            journey = LearningJourney.objects.create(
                user=request.user,
                template=template,
                title=template.name,
                description=template.description,
                topic=topic or template.category,
                total_steps=template.steps_count,
                estimated_hours=template.estimated_hours,
                goals=goals or [],
            )

            # Create steps from template
            for i, step_data in enumerate(template.steps_data, 1):
                LearningJourneyStep.objects.create(
                    journey=journey,
                    step_number=i,
                    title=step_data.get('title', f'Step {i}'),
                    description=step_data.get('description', ''),
                    step_type=step_data.get('step_type', 'lesson'),
                    content_meta=step_data.get('content_meta', {}),
                    status='pending',
                )
        else:
            # Create custom journey
            journey = LearningJourney.objects.create(
                user=request.user,
                title=topic or 'Custom Learning Journey',
                description='A personalized learning path',
                topic=topic,
                total_steps=5,
                goals=goals or [],
            )

            # Create default steps
            default_steps = [
                ('Introduction', 'Get started with the basics'),
                ('Core Concepts', 'Learn the fundamental principles'),
                ('Practice', 'Apply what you\'ve learned'),
                ('Advanced Topics', 'Explore deeper concepts'),
                ('Mastery', 'Demonstrate your knowledge'),
            ]
            for i, (title, desc) in enumerate(default_steps, 1):
                LearningJourneyStep.objects.create(
                    journey=journey,
                    step_number=i,
                    title=title,
                    description=desc,
                )

        return Response({
            'success': True,
            'journey': journey.to_dict(),
            'message': f'Started: {journey.title}'
        })

    except LearningJourneyTemplate.DoesNotExist:
        return Response({'success': False, 'error': 'Template not found'}, status=404)
    except Exception as e:
        logger.error(f"Error starting journey: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_pause(request, journey_id):
    """POST /api/learning/journeys/<id>/pause/ - Pause a journey"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        journey.status = 'paused'
        journey.paused_at = timezone.now()
        journey.save()
        return Response({
            'success': True,
            'message': f'Paused: {journey.title}',
            'journey': journey.to_dict()
        })
    except LearningJourney.DoesNotExist:
        return Response({'success': False, 'error': 'Journey not found'}, status=404)
    except Exception as e:
        logger.error(f"Error pausing journey: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_resume(request, journey_id):
    """POST /api/learning/journeys/<id>/resume/ - Resume a paused journey"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        journey.status = 'active'
        journey.paused_at = None
        journey.save()
        return Response({
            'success': True,
            'message': f'Resumed: {journey.title}',
            'journey': journey.to_dict()
        })
    except LearningJourney.DoesNotExist:
        return Response({'success': False, 'error': 'Journey not found'}, status=404)
    except Exception as e:
        logger.error(f"Error resuming journey: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_complete(request, journey_id):
    """POST /api/learning/journeys/<id>/complete/ - Mark journey as completed"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        journey.status = 'completed'
        journey.completed_at = timezone.now()
        journey.progress = 100
        journey.save()

        # Update streak
        streak, _ = UserLearningStreak.objects.get_or_create(user=request.user)
        streak.total_journeys_completed += 1
        streak.record_activity()

        # Check for achievements
        _check_achievements(request.user)

        return Response({
            'success': True,
            'message': f'Completed: {journey.title}!',
            'journey': journey.to_dict()
        })
    except LearningJourney.DoesNotExist:
        return Response({'success': False, 'error': 'Journey not found'}, status=404)
    except Exception as e:
        logger.error(f"Error completing journey: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_journey_abandon(request, journey_id):
    """POST /api/learning/journeys/<id>/abandon/ - Abandon a journey"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        journey.status = 'abandoned'
        journey.save()
        return Response({
            'success': True,
            'message': f'Abandoned: {journey.title}',
        })
    except LearningJourney.DoesNotExist:
        return Response({'success': False, 'error': 'Journey not found'}, status=404)
    except Exception as e:
        logger.error(f"Error abandoning journey: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# STEP MANAGEMENT
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_step_start(request, journey_id, step_number):
    """POST /api/learning/journeys/<id>/step/<step>/start/ - Start a step"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        step = LearningJourneyStep.objects.get(journey=journey, step_number=step_number)

        step.status = 'in_progress'
        step.started_at = timezone.now()
        step.save()

        journey.current_step = step_number
        journey.save(update_fields=['current_step', 'last_activity_at'])

        # Record activity for streak
        streak, _ = UserLearningStreak.objects.get_or_create(user=request.user)
        streak.record_activity()

        # Fire content generation if step has no content yet
        generating = False
        if not step.content:
            try:
                from core.tasks import generate_step_content
                generate_step_content.delay(str(step.id))
                generating = True
            except Exception as gen_err:
                logger.warning(f"Failed to queue content generation: {gen_err}")

        return Response({
            'success': True,
            'message': f'Started: {step.title}',
            'step': step.to_dict(),
            'generating_content': generating,
        })
    except (LearningJourney.DoesNotExist, LearningJourneyStep.DoesNotExist):
        return Response({'success': False, 'error': 'Journey or step not found'}, status=404)
    except Exception as e:
        logger.error(f"Error starting step: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_step_complete(request, journey_id, step_number):
    """POST /api/learning/journeys/<id>/step/<step>/complete/ - Complete a step"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        step = LearningJourneyStep.objects.get(journey=journey, step_number=step_number)

        step.status = 'completed'
        step.completed_at = timezone.now()
        step.notes = request.data.get('notes', '')

        # Calculate duration
        if step.started_at:
            duration = (step.completed_at - step.started_at).total_seconds() / 60
            step.duration_minutes = int(duration)

        step.save()

        # Update journey progress
        journey.update_progress()

        # Check if journey is complete
        all_completed = not journey.steps.exclude(status__in=['completed', 'skipped']).exists()
        if all_completed:
            journey.status = 'completed'
            journey.completed_at = timezone.now()
            journey.progress = 100
            journey.save()

        # Update streak
        streak, _ = UserLearningStreak.objects.get_or_create(user=request.user)
        streak.total_steps_completed += 1
        if step.duration_minutes:
            streak.total_hours_spent += step.duration_minutes / 60
        streak.record_activity()

        # Check achievements
        _check_achievements(request.user)

        return Response({
            'success': True,
            'message': f'Completed: {step.title}',
            'step': step.to_dict(),
            'journey_complete': all_completed,
            'progress': journey.progress
        })
    except (LearningJourney.DoesNotExist, LearningJourneyStep.DoesNotExist):
        return Response({'success': False, 'error': 'Journey or step not found'}, status=404)
    except Exception as e:
        logger.error(f"Error completing step: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learning_step_skip(request, journey_id, step_number):
    """POST /api/learning/journeys/<id>/step/<step>/skip/ - Skip a step"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        step = LearningJourneyStep.objects.get(journey=journey, step_number=step_number)

        step.status = 'skipped'
        step.save()

        journey.update_progress()

        return Response({
            'success': True,
            'message': f'Skipped: {step.title}',
            'step': step.to_dict()
        })
    except (LearningJourney.DoesNotExist, LearningJourneyStep.DoesNotExist):
        return Response({'success': False, 'error': 'Journey or step not found'}, status=404)
    except Exception as e:
        logger.error(f"Error skipping step: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_step_content(request, journey_id, step_number):
    """GET /api/learning/journeys/<id>/step/<n>/content/ - Get step content (polled by frontend)"""
    try:
        journey = LearningJourney.objects.get(id=journey_id, user=request.user)
        step = LearningJourneyStep.objects.get(journey=journey, step_number=step_number)
        return Response({
            'success': True,
            'has_content': bool(step.content),
            'step': step.to_dict(),
        })
    except (LearningJourney.DoesNotExist, LearningJourneyStep.DoesNotExist):
        return Response({'success': False, 'error': 'Journey or step not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting step content: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# TEMPLATES
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def learning_templates(request):
    """GET /api/learning/templates/ - List available journey templates"""
    try:
        templates = LearningJourneyTemplate.objects.filter(is_active=True)
        return Response({
            'templates': [
                {
                    'id': str(t.id),
                    'name': t.name,
                    'description': t.description,
                    'category': t.category,
                    'difficulty': t.difficulty,
                    'estimated_hours': float(t.estimated_hours),
                    'steps_count': t.steps_count,
                    'popularity': t.popularity,
                    'tags': t.tags,
                }
                for t in templates
            ]
        })
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        return Response({'templates': [], 'error': str(e)})


@api_view(['GET'])
@permission_classes([AllowAny])
def learning_template_detail(request, template_id):
    """GET /api/learning/templates/<id>/ - Template detail"""
    try:
        template = LearningJourneyTemplate.objects.get(id=template_id)
        return Response({
            'success': True,
            'template': {
                'id': str(template.id),
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'difficulty': template.difficulty,
                'estimated_hours': float(template.estimated_hours),
                'steps_count': template.steps_count,
                'steps': template.steps_data,
                'tags': template.tags,
            }
        })
    except LearningJourneyTemplate.DoesNotExist:
        return Response({'success': False, 'error': 'Template not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# ANALYTICS & ACHIEVEMENTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_journey_analytics(request):
    """GET /api/learning/journeys/analytics/ - User's learning analytics"""
    try:
        user = request.user

        # Get or create streak record
        streak, _ = UserLearningStreak.objects.get_or_create(user=user)

        # Count journeys
        total_journeys = LearningJourney.objects.filter(user=user).count()
        completed_journeys = LearningJourney.objects.filter(user=user, status='completed').count()

        # Count achievements
        achievements_earned = UserLearningAchievement.objects.filter(user=user).count()

        return Response({
            'total_journeys': total_journeys,
            'completed_journeys': completed_journeys,
            'total_steps_completed': streak.total_steps_completed,
            'total_hours_spent': float(streak.total_hours_spent),
            'current_streak': streak.current_streak,
            'longest_streak': streak.longest_streak,
            'achievements_earned': achievements_earned,
        })
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        return Response({
            'total_journeys': 0,
            'completed_journeys': 0,
            'total_steps_completed': 0,
            'total_hours_spent': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'achievements_earned': 0,
            'error': str(e)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_achievements(request):
    """GET /api/learning/achievements/ - User's achievements"""
    try:
        user_achievements = UserLearningAchievement.objects.filter(
            user=request.user
        ).select_related('achievement')

        return Response({
            'achievements': [ua.to_dict() for ua in user_achievements],
            'total_points': sum(ua.achievement.points for ua in user_achievements)
        })
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        return Response({'achievements': [], 'total_points': 0, 'error': str(e)})


def _check_achievements(user):
    """Check and award new achievements based on user's progress"""
    try:
        streak, _ = UserLearningStreak.objects.get_or_create(user=user)

        # Get all achievements
        all_achievements = LearningAchievement.objects.filter(is_active=True)

        for achievement in all_achievements:
            # Skip if already earned
            if UserLearningAchievement.objects.filter(user=user, achievement=achievement).exists():
                continue

            # Check if requirement is met
            earned = False
            if achievement.requirement_type == 'journeys_completed':
                earned = streak.total_journeys_completed >= achievement.requirement_value
            elif achievement.requirement_type == 'steps_completed':
                earned = streak.total_steps_completed >= achievement.requirement_value
            elif achievement.requirement_type == 'streak_days':
                earned = streak.current_streak >= achievement.requirement_value
            elif achievement.requirement_type == 'hours_spent':
                earned = streak.total_hours_spent >= achievement.requirement_value

            if earned:
                UserLearningAchievement.objects.create(
                    user=user,
                    achievement=achievement,
                    progress=achievement.requirement_value
                )
                logger.info(f"Achievement earned: {user.username} - {achievement.name}")

    except Exception as e:
        logger.error(f"Error checking achievements: {e}")

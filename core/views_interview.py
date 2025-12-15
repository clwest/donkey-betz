"""
Session 430: User Interview API Views
=====================================

REST API endpoints for the user profile interview system.
Provides endpoints to start, continue, and complete the interview process.
"""

import logging
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from intelligence.personal_assistant_interviewer import personal_assistant_interviewer
from core.models import EnhancedUserProfile

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_interview(request):
    """
    Start a new profile interview for the user.

    POST /api/interview/start/
    Body: { "quick_start": true/false }
    """
    try:
        user = request.user
        quick_start = request.data.get('quick_start', False)

        logger.info(f"Starting interview for user {user.id} (quick_start={quick_start})")

        # Start the interview
        result = run_async(
            personal_assistant_interviewer.start_interview(
                str(user.id),
                quick_start=quick_start
            )
        )

        return Response({
            'success': True,
            'message': 'Interview started',
            'data': result
        })

    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_interview(request):
    """
    Process a user response during the interview.

    POST /api/interview/respond/
    Body: { "response": "user's answer" }
    """
    try:
        user = request.user
        user_response = request.data.get('response', '')

        if not user_response:
            return Response({
                'success': False,
                'error': 'Response is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Processing interview response for user {user.id}")

        # Process the response
        result = run_async(
            personal_assistant_interviewer.process_response(
                str(user.id),
                user_response
            )
        )

        # If interview is complete, save to database
        if result.get('interview_complete'):
            profile_data = result.get('profile', {})
            save_interview_to_profile(user, profile_data)

        return Response({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"Error processing interview response: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interview_status(request):
    """
    Get the current interview status for the user.

    GET /api/interview/status/
    """
    try:
        user = request.user

        # Check for active interview
        result = run_async(
            personal_assistant_interviewer.get_interview_status(str(user.id))
        )

        # Also get profile completeness
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
        completeness = profile.calculate_completeness()

        return Response({
            'success': True,
            'has_active_interview': result.get('active', False),
            'interview_state': result.get('state'),
            'profile_completeness': completeness,
            'next_question': result.get('next_question')
        })

    except Exception as e:
        logger.error(f"Error getting interview status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_interview(request):
    """
    Resume an existing interview.

    POST /api/interview/resume/
    """
    try:
        user = request.user

        result = run_async(
            personal_assistant_interviewer.resume_interview(str(user.id))
        )

        if 'error' in result:
            return Response({
                'success': False,
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'success': True,
            'data': result
        })

    except Exception as e:
        logger.error(f"Error resuming interview: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_summary(request):
    """
    Get a summary of the user's profile for display in the UI.

    GET /api/profile/summary/
    """
    try:
        user = request.user
        profile, created = EnhancedUserProfile.objects.get_or_create(user=user)

        completeness = profile.calculate_completeness()

        # Determine completeness hint
        if completeness < 20:
            hint = "Complete the interview to unlock personalized recommendations"
        elif completeness < 50:
            hint = "Add more details to improve your matches"
        elif completeness < 80:
            hint = "Almost there! A few more details will help"
        else:
            hint = "Great profile! You're set for personalized recommendations"

        # Format income goal for display
        income_goal = None
        if profile.long_term_goals:
            for goal in profile.long_term_goals:
                if isinstance(goal, str) and 'income' in goal.lower():
                    income_goal = goal
                    break

        # Get work preferences from preferred_channels
        work_prefs = profile.preferred_channels or []

        return Response({
            'success': True,
            'profile': {
                'primary_role': profile.primary_role or None,
                'core_skills': profile.core_competencies or [],
                'availability': profile.work_schedule or None,
                'income_goal': income_goal,
                'work_preferences': work_prefs,
                'commitment_level': profile.learning_style if profile.learning_style and 'commitment' in profile.learning_style.lower() else None,
                'completeness': completeness,
                'completeness_hint': hint,
                'interview_completed': completeness >= 50
            }
        })

    except Exception as e:
        logger.error(f"Error getting profile summary: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def save_interview_to_profile(user, profile_data):
    """
    Save interview results to the EnhancedUserProfile model.
    """
    try:
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

        # Map interview data to profile fields
        if profile_data.get('name'):
            name_parts = profile_data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            user.save()

        # Primary role from strongest skill or current situation
        if profile_data.get('strongest_skill'):
            profile.primary_role = profile_data['strongest_skill']
        elif profile_data.get('current_situation'):
            profile.primary_role = profile_data['current_situation']

        # Core competencies from skills
        all_skills = profile_data.get('all_skills', [])
        if all_skills:
            profile.core_competencies = all_skills

        # Work schedule from available hours
        available_hours = profile_data.get('available_hours_per_week', 0)
        if available_hours:
            if available_hours <= 5:
                profile.work_schedule = "1-5 hours/week (side hustle)"
            elif available_hours <= 20:
                profile.work_schedule = "10-20 hours/week (part-time)"
            elif available_hours <= 40:
                profile.work_schedule = "20-40 hours/week (serious commitment)"
            else:
                profile.work_schedule = "40+ hours/week (full-time)"

        # Long-term goals
        income_goal = profile_data.get('monthly_income_goal', 0)
        goals = []
        if income_goal:
            goals.append(f"Target monthly income: ${income_goal}")
        if profile_data.get('career_motivation'):
            goals.append(profile_data['career_motivation'])
        if goals:
            profile.long_term_goals = goals

        # Work preferences
        work_prefs = profile_data.get('work_preferences', [])
        if work_prefs:
            profile.preferred_channels = work_prefs

        # Commitment level stored in learning_style
        commitment = profile_data.get('commitment_level', '')
        if commitment:
            profile.learning_style = f"Commitment level: {commitment}"

        # Professional background
        if profile_data.get('professional_background'):
            # Store in personal_values as a placeholder (or add new field)
            profile.personal_values = [profile_data['professional_background']]

        # Things to avoid stored in sensitive_topics
        if profile_data.get('things_to_avoid'):
            profile.sensitive_topics = [profile_data['things_to_avoid']]

        profile.save()
        logger.info(f"Saved interview data to profile for user {user.id}")

    except Exception as e:
        logger.error(f"Error saving interview to profile: {e}")
        raise

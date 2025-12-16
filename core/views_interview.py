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

        # Session 457: Save incrementally after EVERY response
        # This prevents data loss if server restarts mid-interview
        interview_state = result.get('state', {})
        if interview_state:
            save_interview_incrementally(user, interview_state)

        # If interview is complete, do final comprehensive save
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


def save_interview_incrementally(user, interview_state: dict):
    """
    Session 457: Save interview progress incrementally after each answer.
    This prevents data loss if the server restarts mid-interview.

    Args:
        user: The Django user object
        interview_state: The current interview state dict from the interviewer
    """
    try:
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
        profile_data = interview_state.get('profile_data', {})

        # Save name to user model
        name = profile_data.get('name')
        if name and not user.first_name:
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            user.save()

        # Primary role from situation (always update if we have data)
        situation = profile_data.get('current_situation')
        if situation:
            profile.primary_role = situation

        # Core competencies from skills (accumulate as we go)
        skills = profile_data.get('skills', {})
        all_skills = []
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                all_skills.extend([s for s in skill_list if s != 'None of these'])
        if all_skills:
            profile.core_competencies = all_skills

        # Work schedule from available hours (always update if we have data)
        available_hours = profile_data.get('available_hours', 0)
        if available_hours:
            if available_hours <= 5:
                profile.work_schedule = "1-5 hours/week (side hustle)"
            elif available_hours <= 20:
                profile.work_schedule = "10-20 hours/week (part-time)"
            elif available_hours <= 40:
                profile.work_schedule = "20-40 hours/week (serious commitment)"
            else:
                profile.work_schedule = "40+ hours/week (full-time)"

        # Long-term goals - build from multiple sources
        goals_list = []
        goals = profile_data.get('goals', {})

        # Try numeric income goal first
        income_goal = goals.get('monthly_income', 0)
        if income_goal and isinstance(income_goal, (int, float)) and income_goal > 0:
            goals_list.append(f"Target monthly income: ${income_goal}")

        # Also check for skill_example as a goal/vision
        skill_example = profile_data.get('skill_example', '')
        if skill_example:
            goals_list.append(f"Vision: {skill_example}")

        # Strongest skill as a goal
        strongest = profile_data.get('strongest_skill', '')
        if strongest:
            goals_list.append(f"Focus area: {strongest}")

        if goals_list:
            profile.long_term_goals = goals_list

        # Work preferences - handle both list and string formats
        work_prefs = goals.get('work_preferences', [])
        if work_prefs:
            # Handle string that looks like a list
            if isinstance(work_prefs, str) and work_prefs.startswith('['):
                import ast
                try:
                    work_prefs = ast.literal_eval(work_prefs)
                except:
                    work_prefs = [work_prefs]
            if isinstance(work_prefs, list):
                profile.preferred_channels = work_prefs

        # Commitment level in learning_style (always update if we have commitment)
        commitment = profile_data.get('commitment_level', '')
        if commitment:
            profile.learning_style = f"Commitment: {commitment}"

        # Communication style from interview responses
        responses = interview_state.get('responses', {})
        if responses and not profile.communication_style:
            # Infer communication style from response patterns
            profile.communication_style = "conversational"

        # Professional background in personal_values
        experience = profile_data.get('experience', {})
        background = experience.get('background', '')
        if background:
            profile.personal_values = [background]

        # Hidden talents in secondary roles
        hidden_talents = profile_data.get('hidden_talents', [])
        if hidden_talents:
            if isinstance(hidden_talents, list):
                profile.secondary_roles = hidden_talents
            else:
                profile.secondary_roles = [hidden_talents]

        # Session 457: Save new interview fields
        # Current projects
        current_projects = profile_data.get('current_projects', [])
        if current_projects:
            if isinstance(current_projects, list):
                profile.current_projects = current_projects
            else:
                profile.current_projects = [current_projects]

        # Quarterly objectives
        quarterly_objectives = profile_data.get('quarterly_objectives', [])
        if quarterly_objectives:
            if isinstance(quarterly_objectives, list):
                profile.quarterly_objectives = quarterly_objectives
            else:
                profile.quarterly_objectives = [quarterly_objectives]

        # Certifications
        certifications = profile_data.get('certifications', [])
        if certifications:
            if isinstance(certifications, list):
                profile.certifications = certifications
            else:
                profile.certifications = [certifications]

        # Store interview state in dynamic_attributes for resume capability
        profile.dynamic_attributes = profile.dynamic_attributes or {}
        profile.dynamic_attributes['interview_state'] = {
            'phase': interview_state.get('phase', 'gathering_info'),
            'topics_covered': interview_state.get('topics_covered', []),
            'completion_percentage': interview_state.get('completion_percentage', 0),
            'last_updated': interview_state.get('last_updated', '')
        }

        # Store full profile_data for reference
        profile.dynamic_attributes['full_interview_data'] = profile_data

        profile.save()
        logger.info(f"Incrementally saved interview progress for user {user.id} - {len(interview_state.get('topics_covered', []))} topics covered")

    except Exception as e:
        logger.error(f"Error in incremental interview save: {e}")
        # Don't raise - this is a background save, shouldn't break the interview flow


# ========== SESSION 457: CERTIFICATION ENDPOINTS ==========

from core.models import UserCertification


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_certifications(request):
    """
    List all certifications for the current user.

    GET /api/certifications/
    """
    try:
        certs = UserCertification.objects.filter(user=request.user)
        data = []
        for cert in certs:
            data.append({
                'id': cert.id,
                'name': cert.name,
                'issuer': cert.issuer,
                'issue_date': cert.issue_date.isoformat() if cert.issue_date else None,
                'expiry_date': cert.expiry_date.isoformat() if cert.expiry_date else None,
                'credential_id': cert.credential_id,
                'file_url': cert.get_file_url(),
                'verification_url': cert.verification_url,
                'skills': cert.skills,
                'created_at': cert.created_at.isoformat()
            })

        return Response({
            'success': True,
            'certifications': data,
            'count': len(data)
        })

    except Exception as e:
        logger.error(f"Error listing certifications: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_certification(request):
    """
    Add a new certification for the current user.

    POST /api/certifications/
    Body (multipart/form-data):
        - name: Certificate name (required)
        - issuer: Issuing organization
        - issue_date: Date issued (YYYY-MM-DD)
        - expiry_date: Expiration date (YYYY-MM-DD)
        - credential_id: Credential ID
        - certificate_file: File upload (PDF/image)
        - verification_url: URL to verify online
        - skills: JSON array of skills
    """
    try:
        name = request.data.get('name')
        if not name:
            return Response({
                'success': False,
                'error': 'Certificate name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Parse dates
        issue_date = request.data.get('issue_date')
        expiry_date = request.data.get('expiry_date')

        # Parse skills (might be JSON string or list)
        skills = request.data.get('skills', [])
        if isinstance(skills, str):
            import json
            try:
                skills = json.loads(skills)
            except:
                skills = [s.strip() for s in skills.split(',') if s.strip()]

        cert = UserCertification.objects.create(
            user=request.user,
            name=name,
            issuer=request.data.get('issuer', ''),
            issue_date=issue_date if issue_date else None,
            expiry_date=expiry_date if expiry_date else None,
            credential_id=request.data.get('credential_id', ''),
            certificate_file=request.FILES.get('certificate_file'),
            verification_url=request.data.get('verification_url', ''),
            skills=skills
        )

        # Update EnhancedUserProfile certifications list for completeness calculation
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=request.user)
        cert_names = list(UserCertification.objects.filter(user=request.user).values_list('name', flat=True))
        profile.certifications = cert_names
        profile.save()

        logger.info(f"Added certification '{name}' for user {request.user.id}")

        return Response({
            'success': True,
            'message': 'Certification added',
            'certification': {
                'id': cert.id,
                'name': cert.name,
                'issuer': cert.issuer,
                'file_url': cert.get_file_url()
            },
            'profile_completeness': profile.calculate_completeness()
        })

    except Exception as e:
        logger.error(f"Error adding certification: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_certification(request, cert_id):
    """
    Delete a certification.

    DELETE /api/certifications/<id>/
    """
    try:
        cert = UserCertification.objects.get(id=cert_id, user=request.user)
        name = cert.name
        cert.delete()

        # Update EnhancedUserProfile certifications list
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=request.user)
        cert_names = list(UserCertification.objects.filter(user=request.user).values_list('name', flat=True))
        profile.certifications = cert_names
        profile.save()

        logger.info(f"Deleted certification '{name}' for user {request.user.id}")

        return Response({
            'success': True,
            'message': f'Certification "{name}" deleted',
            'profile_completeness': profile.calculate_completeness()
        })

    except UserCertification.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Certification not found'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error deleting certification: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

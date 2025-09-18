"""
Personal Assistant Interview API Views
=====================================

API endpoints for the Personal Assistant Interview System.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .personal_assistant_interviewer import personal_assistant_interviewer
from .profile_context_service import profile_context_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_interview_api(request):
    """Start a new interview via API"""
    try:
        quick_start = request.data.get('quick_start', False)
        user_id = str(request.user.id)

        # Start interview
        result = await personal_assistant_interviewer.start_interview(
            user_id=user_id,
            quick_start=quick_start
        )

        if result.get('success'):
            return Response({
                'success': True,
                'interview_started': True,
                'interview_type': 'quick' if quick_start else 'full',
                'estimated_time': result.get('estimated_time'),
                'first_question': result.get('question')
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to start interview')
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error starting interview API: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interview_status_api(request):
    """Get current interview status via API"""
    try:
        user_id = str(request.user.id)
        status_data = await personal_assistant_interviewer.get_interview_status(user_id)

        return Response({
            'success': True,
            'status': status_data
        })

    except Exception as e:
        logger.error(f"Error getting interview status API: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_context_api(request):
    """Get user profile context via API"""
    try:
        user_id = str(request.user.id)
        context_type = request.GET.get('context_type', 'general')

        context = await profile_context_service.get_user_context(user_id, context_type)

        return Response({
            'success': True,
            'context': context
        })

    except Exception as e:
        logger.error(f"Error getting user context API: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personalized_greeting_api(request):
    """Get personalized greeting via API"""
    try:
        user_id = str(request.user.id)
        greeting = await profile_context_service.get_personalized_greeting(user_id)

        return Response({
            'success': True,
            'greeting': greeting,
            'user_name': request.user.first_name or request.user.username
        })

    except Exception as e:
        logger.error(f"Error getting personalized greeting API: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'greeting': 'Hi! I\'m your AI assistant, ready to help.'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_summary_api(request):
    """Get user profile summary via API"""
    try:
        user_id = str(request.user.id)
        summary = await profile_context_service.get_context_summary(user_id)

        return Response({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error getting profile summary API: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class InterviewWebhookView(View):
    """Webhook endpoint for interview completion notifications"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            event_type = data.get('event_type')

            if event_type == 'interview_completed':
                user_id = data.get('user_id')
                profile_data = data.get('profile_data', {})

                # Invalidate cache for user
                if user_id:
                    asyncio.create_task(
                        profile_context_service.invalidate_user_cache(user_id)
                    )

                logger.info(f"Interview completed webhook for user {user_id}")

                return JsonResponse({
                    'success': True,
                    'message': 'Webhook processed successfully'
                })

            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown event type: {event_type}'
                }, status=400)

        except Exception as e:
            logger.error(f"Error processing interview webhook: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_context_api(request):
    """Update user context via API"""
    try:
        user_id = str(request.user.id)
        updates = request.data.get('updates', {})

        success = await profile_context_service.update_user_context(user_id, updates)

        if success:
            return Response({
                'success': True,
                'message': 'User context updated successfully'
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to update user context'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error updating user context API: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_expired_interviews_api(request):
    """Cleanup expired interviews via API (admin only)"""
    try:
        # Check if user is staff/admin
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)

        personal_assistant_interviewer.cleanup_expired_interviews()

        return Response({
            'success': True,
            'message': 'Expired interviews cleaned up successfully'
        })

    except Exception as e:
        logger.error(f"Error cleaning up expired interviews: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
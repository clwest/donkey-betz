"""
Minimal Assistant API Views for Development Testing
=================================================

This provides basic assistant functionality without the full AI system
to test frontend connectivity while the serialization issue is resolved.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from datetime import datetime

logger = logging.getLogger(__name__)
User = get_user_model()


@never_cache
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def chat_minimal_dev(request):
    """
    Minimal chat endpoint that provides basic responses without the full AI system.
    """
    try:
        message = request.data.get('message', '').strip()

        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Get or create default user
        try:
            user = User.objects.get(username='assistant_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='assistant_user',
                email='assistant@example.com',
                first_name='Assistant',
                last_name='User'
            )

        # Simple response without AI processing
        response_data = {
            'response': f"🤖 Hello! I received your message: \"{message}\"\n\nI'm currently in development mode with limited functionality. The full AI assistant is experiencing technical difficulties with serialization, but your message was processed successfully!\n\nThis minimal fallback demonstrates that the communication pipeline is working.",
            'ai_generated': False,
            'model': 'minimal_fallback',
            'timestamp': str(datetime.now()),
            'debug_info': {
                'user': user.username,
                'authenticated': False,
                'mode': 'minimal_development',
                'message_length': len(message)
            }
        }

        return JsonResponse({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        logger.error(f"Error in chat_minimal_dev: {e}")
        return JsonResponse({
            'error': 'Failed to process message in minimal mode',
            'detail': str(e)
        }, status=500)


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])
def context_minimal_dev(request):
    """
    Minimal context endpoint that provides basic user context without the full AI system.
    """
    try:
        # Get or create default user
        try:
            user = User.objects.get(username='assistant_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='assistant_user',
                email='assistant@example.com',
                first_name='Assistant',
                last_name='User'
            )

        # Simple context without AI processing
        context = {
            'first_name': user.first_name or 'User',
            'last_name': user.last_name or '',
            'email': user.email,
            'skills': {
                'top_skills': ['Communication', 'Problem Solving', 'Adaptability'],
                'total_count': 3
            },
            'preferences': {
                'communication_style': 'friendly',
                'expertise_level': 'intermediate'
            },
            'recent_activity': [
                {
                    'type': 'message',
                    'description': 'Testing minimal assistant mode',
                    'timestamp': str(datetime.now())
                }
            ],
            'system_status': 'Minimal development mode - core AI temporarily offline for serialization fixes',
            'mode': 'minimal_development',
            'total_embeddings': 0,
            'debug_info': {
                'user_id': user.id,
                'mode': 'minimal_fallback'
            }
        }

        return JsonResponse({
            'success': True,
            'context': context
        })

    except Exception as e:
        logger.error(f"Error in context_minimal_dev: {e}")
        return JsonResponse({
            'error': 'Failed to get context in minimal mode',
            'detail': str(e)
        }, status=500)
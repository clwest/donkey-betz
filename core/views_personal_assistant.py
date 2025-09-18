"""
Personal AI Assistant API Views
================================
"""

import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)

try:
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant as PersonalAIAssistant
    logger.info("Using Enhanced Personal AI Assistant with database access")
except ImportError:
    from core.personal_ai_assistant import PersonalAIAssistant
    logger.info("Using standard Personal AI Assistant")


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_assistant(request):
    """
    Chat with the personal AI assistant.

    Request body:
    {
        "message": "User's message",
        "context": {} // Optional additional context
    }
    """
    try:
        message = request.data.get('message', '').strip()
        context = request.data.get('context', {})

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        # Get or create assistant for user
        cache_key = f'assistant_{request.user.id}'
        assistant = cache.get(cache_key)

        if not assistant:
            assistant = PersonalAIAssistant(request.user)
            # Cache assistant for 30 minutes
            cache.set(cache_key, assistant, 1800)

        # Process message
        response_data = assistant.process_message(message, context)

        return Response({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        import traceback
        logger.error(f"Error in chat_with_assistant: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'Failed to process message',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assistant_context(request):
    """Get the current personalized context for the user."""
    try:
        # Get or create assistant
        cache_key = f'assistant_{request.user.id}'
        assistant = cache.get(cache_key)

        if not assistant:
            assistant = PersonalAIAssistant(request.user)
            cache.set(cache_key, assistant, 1800)

        # Get personalized context
        context = assistant.get_personalized_context()

        return Response({
            'success': True,
            'context': context
        })

    except Exception as e:
        logger.error(f"Error getting assistant context: {e}")
        return Response({
            'error': 'Failed to get context',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_summary(request):
    """Get summary of what the assistant has learned about the user."""
    try:
        # Get or create assistant
        cache_key = f'assistant_{request.user.id}'
        assistant = cache.get(cache_key)

        if not assistant:
            assistant = PersonalAIAssistant(request.user)
            cache.set(cache_key, assistant, 1800)

        # Get learning summary
        summary = assistant.get_learning_summary()

        return Response({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error getting learning summary: {e}")
        return Response({
            'error': 'Failed to get summary',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def provide_feedback(request):
    """
    Provide feedback on assistant's response.

    Request body:
    {
        "message_id": "ID of the message",
        "feedback": "positive" or "negative",
        "details": "Optional feedback details"
    }
    """
    try:
        feedback = request.data.get('feedback')
        details = request.data.get('details', '')

        if feedback not in ['positive', 'negative']:
            return Response({'error': 'Invalid feedback type'}, status=400)

        # Get assistant
        cache_key = f'assistant_{request.user.id}'
        assistant = cache.get(cache_key)

        if not assistant:
            assistant = PersonalAIAssistant(request.user)
            cache.set(cache_key, assistant, 1800)

        # Process feedback (enhance learning)
        if assistant.learning_history:
            last_interaction = assistant.learning_history[-1]
            last_interaction['feedback'] = feedback
            last_interaction['feedback_details'] = details

            # Adjust confidence based on feedback
            if feedback == 'positive':
                last_interaction['confidence'] = min(last_interaction.get('confidence', 0.5) * 1.1, 1.0)
            else:
                last_interaction['confidence'] = max(last_interaction.get('confidence', 0.5) * 0.9, 0.1)

            # Re-learn from the interaction
            assistant.learn_from_interaction(
                last_interaction['message'],
                last_interaction['response'],
                last_interaction
            )

        return Response({
            'success': True,
            'message': 'Feedback recorded'
        })

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return Response({
            'error': 'Failed to record feedback',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_assistant(request):
    """Reset the assistant's learning for the user."""
    try:
        cache_key = f'assistant_{request.user.id}'
        cache.delete(cache_key)

        # Clear user embeddings
        from core.models import UserEmbedding
        UserEmbedding.objects.filter(user=request.user).delete()

        # Clear behavior patterns from profile
        from core.models import ExtendedUserProfile
        try:
            profile = ExtendedUserProfile.objects.get(user=request.user)
            metadata = profile.metadata or {}
            metadata.pop('behavior_patterns', None)
            profile.metadata = metadata
            profile.save()
        except ExtendedUserProfile.DoesNotExist:
            pass

        return Response({
            'success': True,
            'message': 'Assistant reset successfully'
        })

    except Exception as e:
        logger.error(f"Error resetting assistant: {e}")
        return Response({
            'error': 'Failed to reset assistant',
            'detail': str(e)
        }, status=500)
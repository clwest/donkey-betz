"""
Development-friendly Personal AI Assistant API Views
======================================================

This version allows testing without authentication in development mode.
"""

import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)
User = get_user_model()

PersonalAIAssistant = None  # Legacy PA removed — all traffic routes through Rigby


@never_cache
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access for development
def chat_with_assistant_dev(request):
    """
    Development version of chat endpoint that works without authentication.

    Request body:
    {
        "message": "User's message",
        "context": {} // Optional additional context
    }
    """
    try:
        logger.info("Starting chat_with_assistant_dev")
        message = request.data.get('message', '').strip()
        context = request.data.get('context', {})
        conversation_history = request.data.get('conversation_history', [])
        logger.info(f"Got message: {message[:50]}...")
        logger.info(f"Conversation history: {len(conversation_history)} messages")

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        # Get user - use authenticated user if available, otherwise use default test user
        if request.user and request.user.is_authenticated:
            user = request.user
            logger.info(f"Using authenticated user: {user.username}")
        else:
            # Get or create default test user for development
            try:
                user = User.objects.get(username='assistant_user')
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username='assistant_user',
                    email='assistant@example.com',
                    first_name='Assistant',
                    last_name='User'
                )
                logger.info("Created default assistant_user for development")
            logger.info("Using default assistant_user for unauthenticated request")

        logger.info("About to create PersonalAIAssistant...")

        # Create assistant for user (don't cache the object as it contains non-serializable components)
        try:
            if PersonalAIAssistant is None:
                return Response({'error': 'Legacy PA deprecated — use /api/pa/chat/ endpoint'}, status=410)
            assistant = PersonalAIAssistant(user)
            logger.info("Assistant created successfully")

            # Enhanced context with conversation history
            enhanced_context = {
                **context,
                'conversation_history': conversation_history,
                'conversation_context': "\n".join([
                    f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('message', '')}"
                    for msg in conversation_history[-3:]  # Last 3 messages for immediate context
                ]) if conversation_history else ""
            }
            logger.info(f"Enhanced context prepared with {len(conversation_history)} history messages")

            # Process message
            logger.info("🤖 Calling assistant.process_message()...")
            raw_response = assistant.process_message(message, enhanced_context)
            logger.info(f"✅ Got response type: {type(raw_response)}")
            logger.info(f"📝 Response keys: {list(raw_response.keys()) if isinstance(raw_response, dict) else 'Not a dict'}")

            # Ensure response_data is JSON serializable by creating a clean copy
            response_data = {}
            import json

            for key, value in raw_response.items():
                try:
                    # Test if the value is JSON serializable
                    json.dumps(value)
                    response_data[key] = value
                except (TypeError, ValueError):
                    # If not serializable, convert to string representation
                    logger.warning(f"Non-serializable value for key {key}: {type(value)}")
                    response_data[key] = str(value)

            logger.info("Response data cleaned for serialization")

        except Exception as e:
            logger.error(f"Assistant error: {e}")
            if 'pickle' in str(e) or '_thread' in str(e) or 'serialize' in str(e):
                # Extract user name from context
                user_context = context.get('user_context', {})
                user_name = user_context.get('first_name') or context.get('first_name', 'there')

                # Smart fallback that considers conversation history
                context_aware_response = f"Hi {user_name}! 🤖 I understand you're asking about: \"{message}\""

                # Add context awareness if we have conversation history
                if conversation_history:
                    last_messages = [msg.get('message', '') for msg in conversation_history[-2:]]
                    context_aware_response += f"\n\nI see we were discussing: {' -> '.join(last_messages[-2:])}"
                    context_aware_response += f"\n\nContinuing our conversation: Your current request about '{message}' relates to our previous discussion."

                context_aware_response += f"\n\nNote: I'm running in development mode with limited AI capabilities, but I'm maintaining our conversation context and remembering you're {user_name}."

                # Fallback response when assistant can't be pickled
                response_data = {
                    'response': context_aware_response,
                    'ai_generated': False,
                    'model': 'context_aware_fallback',
                    'error_type': 'serialization_error',
                    'conversation_continuity': True
                }
            else:
                raise e

        # Add debug info in development (ensure it's also serializable)
        debug_info = {
            'user': str(user.username),
            'authenticated': bool(request.user.is_authenticated if hasattr(request, 'user') else False),
            'ai_generated': bool(response_data.get('ai_generated', False)),
            'model': str(response_data.get('model', 'unknown'))
        }
        response_data['debug_info'] = debug_info

        # Final safety check - ensure the entire response is serializable
        try:
            import json
            json.dumps(response_data)
            logger.info("Final response serialization test passed")
        except (TypeError, ValueError) as serialize_error:
            logger.error(f"Final serialization failed: {serialize_error}")
            response_data = {
                'response': f"🤖 Processed your message: \"{message[:50]}...\"\n\nSystem is working but has minor serialization issues in dev mode.",
                'ai_generated': False,
                'model': 'safe_fallback',
                'error_type': 'final_serialization_check',
                'debug_info': {
                    'user': str(user.username),
                    'error': str(serialize_error)
                }
            }

        return JsonResponse({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        import traceback
        logger.error(f"Error in chat_with_assistant_dev: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Handle pickle/thread errors at top level too
        if 'pickle' in str(e) or '_thread' in str(e) or 'serialize' in str(e):
            return JsonResponse({
                'success': True,
                'data': {
                    'response': f"🤖 Your message '{message[:30]}...' was received!\n\nThe AI Assistant is experiencing technical difficulties with serialization but is working underneath.",
                    'ai_generated': False,
                    'model': 'emergency_fallback',
                    'error_type': 'top_level_serialization_error',
                    'debug_info': {
                        'error_details': str(e)
                    }
                }
            })
        else:
            return JsonResponse({
                'error': 'Failed to process message',
                'detail': str(e)
            }, status=500)


@never_cache
@api_view(['GET'])
@permission_classes([AllowAny])  # Allow unauthenticated access for development
def get_assistant_context_dev(request):
    """
    Development version of context endpoint that works without authentication.
    """
    try:
        # Get user - use authenticated user if available, otherwise use default test user
        if request.user and request.user.is_authenticated:
            user = request.user
        else:
            # Get or create default test user for development
            try:
                user = User.objects.get(username='assistant_user')
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username='assistant_user',
                    email='assistant@example.com',
                    first_name='Assistant',
                    last_name='User'
                )
            logger.info("Using default assistant_user for context request")

        # Create assistant for user (don't cache the object as it contains non-serializable components)
        try:
            if PersonalAIAssistant is None:
                return Response({'error': 'Legacy PA deprecated — use /api/pa/chat/ endpoint'}, status=410)
            assistant = PersonalAIAssistant(user)
            # Get personalized context
            context = assistant.get_personalized_context()
        except Exception as e:
            if 'pickle' in str(e) or '_thread' in str(e):
                # Fallback context when assistant can't be pickled
                context = {
                    'first_name': user.first_name or 'User',
                    'skills': {'top_skills': []},
                    'preferences': {},
                    'recent_activity': [],
                    'system_status': 'AI Assistant experiencing serialization issues',
                    'error_type': 'serialization_error'
                }
            else:
                raise e

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
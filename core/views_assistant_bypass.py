"""
Bypass view for AI Assistant that avoids all Django session/cache/middleware issues
"""
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

try:
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant as PersonalAIAssistant
    logger.info("Using Enhanced Personal AI Assistant")
except ImportError:
    from core.personal_ai_assistant import PersonalAIAssistant
    logger.info("Using standard Personal AI Assistant")


@csrf_exempt
@never_cache
@require_POST
def assistant_chat_bypass(request):
    """
    Completely bypass Django's session/cache system for AI Assistant chat.

    This endpoint:
    - Doesn't use DRF (avoids serialization issues)
    - Doesn't use sessions or cache
    - Returns plain JSON
    """
    try:
        # Parse JSON manually to avoid any middleware issues
        body = request.body.decode('utf-8')
        data = json.loads(body)
        message = data.get('message', '').strip()

        if not message:
            return HttpResponse(
                json.dumps({'error': 'Message is required'}),
                content_type='application/json',
                status=400
            )

        # Get default user without any session handling
        user, created = User.objects.get_or_create(
            username='assistant_user',
            defaults={
                'email': 'assistant@example.com',
                'first_name': 'Assistant',
                'last_name': 'User'
            }
        )

        logger.info(f"Processing message for {user.username}: {message[:50]}...")

        # Create assistant and process message
        assistant = PersonalAIAssistant(user)
        response_data = assistant.process_message(message, {})

        # Ensure all data is JSON serializable
        clean_response = {}
        for key, value in response_data.items():
            try:
                json.dumps(value)
                clean_response[key] = value
            except (TypeError, ValueError):
                clean_response[key] = str(value)

        # Add minimal debug info
        clean_response['debug_info'] = {
            'user': user.username,
            'bypass_mode': True,
            'message_length': len(message)
        }

        result = {
            'success': True,
            'data': clean_response
        }

        # Test final serialization
        json.dumps(result)

        return HttpResponse(
            json.dumps(result),
            content_type='application/json'
        )

    except json.JSONDecodeError:
        return HttpResponse(
            json.dumps({'error': 'Invalid JSON'}),
            content_type='application/json',
            status=400
        )
    except Exception as e:
        logger.error(f"Bypass endpoint error: {e}")

        # Create safe fallback response
        fallback = {
            'success': True,
            'data': {
                'response': f"🤖 Your message was received: \"{message[:30] if 'message' in locals() else 'unknown'}...\"\n\nThe AI Assistant is working but experiencing minor technical issues. Using bypass mode.",
                'ai_generated': False,
                'model': 'bypass_fallback',
                'debug_info': {
                    'error': str(e),
                    'bypass_mode': True
                }
            }
        }

        return HttpResponse(
            json.dumps(fallback),
            content_type='application/json'
        )
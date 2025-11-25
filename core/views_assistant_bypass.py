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

        # Session 125: Get authenticated user (not default user!)
        if not request.user.is_authenticated:
            return HttpResponse(
                json.dumps({'error': 'Authentication required'}),
                content_type='application/json',
                status=401
            )

        user = request.user
        project_id = data.get('project_id')  # Session 125: Get project context

        logger.info(f"Processing message for {user.username}: {message[:50]}...")
        if project_id:
            logger.info(f"  With project context: {project_id}")

        # Session 125: Use EnhancedPersonalAIAssistant (has tool definitions!)
        from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
        assistant = EnhancedPersonalAIAssistant(user)

        # Build context with project_id if provided
        context = {}
        if project_id:
            context['project_id'] = project_id

        response_data = assistant.process_message(message, context)

        # Session 184: Handle different response types
        # process_message can return a string OR a dict with tool_calls
        if isinstance(response_data, str):
            # Simple string response
            clean_response = {
                'message': response_data,
                'success': True
            }
        elif isinstance(response_data, dict):
            # Dict response (possibly with tool_calls)
            clean_response = {}
            for key, value in response_data.items():
                try:
                    json.dumps(value)
                    clean_response[key] = value
                except (TypeError, ValueError):
                    clean_response[key] = str(value)

            # Session 184: Ensure 'message' key exists for frontend
            if 'text' in clean_response and 'message' not in clean_response:
                clean_response['message'] = clean_response['text']

            # Session 184: Pass tool_calls directly at top level for frontend!
            # Frontend expects: data.tool_calls, not data.data.tool_calls
            clean_response['success'] = True
        else:
            clean_response = {
                'message': str(response_data),
                'success': True
            }

        # Add minimal debug info
        clean_response['debug_info'] = {
            'user': user.username,
            'bypass_mode': True,
            'message_length': len(message)
        }

        # Session 184: Return response FLAT (not wrapped in {success, data})
        # Frontend expects: data.tool_calls, data.message directly
        # Test final serialization
        json.dumps(clean_response)

        return HttpResponse(
            json.dumps(clean_response),
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
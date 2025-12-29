"""
Personal AI Assistant API Views
================================
"""

import logging
from django.views.decorators.csrf import csrf_exempt
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_to_assistant(request):
    """
    Voice input for Personal Assistant.
    Session 113: Voice Input MVP

    Combines audio transcription + assistant chat in one endpoint.

    Request:
    - multipart/form-data with 'audio' file (webm/m4a/wav)
    - Optional 'session_id' for conversation threading

    Response:
    {
        "success": true,
        "user_text": "transcribed text...",
        "assistant_message": {
            "response": "...",
            "suggestions": [...],
            "actions": [...],
            "confidence": 0.95
        }
    }
    """
    try:
        # Step 1: Get and validate audio file
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Voice input from {request.user.username} ({audio_file.size} bytes)")

        # Step 2: Transcribe audio using OpenAI Whisper
        # (Reusing logic from views_image.py:6466)
        try:
            import os
            from openai import OpenAI
            from io import BytesIO

            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # Convert Django InMemoryUploadedFile to BytesIO for OpenAI SDK
            audio_file.seek(0)
            audio_bytes = audio_file.read()
            audio_file_like = BytesIO(audio_bytes)

            # Always use .webm extension (frontend sends audio/webm format)
            audio_file_like.name = "recording.webm"

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_like,
                language="en"  # Can be removed to auto-detect
            )

            user_text = transcript.text.strip()
            logger.info(f"✅ Transcribed: '{user_text[:100]}...'")

        except Exception as e:
            logger.error(f"❌ Transcription failed: {str(e)}")
            return Response({
                'error': 'Failed to transcribe audio',
                'details': str(e)
            }, status=500)

        # Step 3: Send transcribed text to Personal Assistant
        # (Reusing logic from chat_with_assistant)
        try:
            # Get or create assistant for user
            cache_key = f'assistant_{request.user.id}'
            assistant = cache.get(cache_key)

            if not assistant:
                assistant = PersonalAIAssistant(request.user)
                # Cache assistant for 30 minutes
                cache.set(cache_key, assistant, 1800)

            # Process message with optional context
            context = request.data.get('context', {})
            context['input_method'] = 'voice'  # Mark as voice input

            response_data = assistant.process_message(user_text, context)

            logger.info(f"✅ Assistant responded to voice input")

            # Step 4: Return combined result
            return Response({
                'success': True,
                'user_text': user_text,
                'assistant_message': response_data
            })

        except Exception as e:
            logger.error(f"❌ Assistant processing failed: {str(e)}")
            # Return partial success - transcription worked
            return Response({
                'success': False,
                'user_text': user_text,
                'error': 'Transcription succeeded but assistant failed to respond',
                'details': str(e)
            }, status=500)

    except Exception as e:
        import traceback
        logger.error(f"❌ Voice input failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'Failed to process voice input',
            'details': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_interview_response(request):
    """
    Session 456: Voice input for Profile Interview.

    Uses OpenAI Whisper to transcribe voice and submit as interview response.

    Request:
    - multipart/form-data with 'audio' file (webm/m4a/wav)

    Response:
    {
        "success": true,
        "transcribed_text": "what the user said...",
        "acknowledgment": "Great answer!",
        "question": { next question data },
        "state": { interview state }
    }
    """
    try:
        # Step 1: Get and validate audio file
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Voice interview input from {request.user.username} ({audio_file.size} bytes)")

        # Step 2: Transcribe audio using OpenAI Whisper
        try:
            import os
            from openai import OpenAI
            from io import BytesIO

            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # Convert Django InMemoryUploadedFile to BytesIO for OpenAI SDK
            audio_file.seek(0)
            audio_bytes = audio_file.read()
            audio_file_like = BytesIO(audio_bytes)

            # Always use .webm extension (frontend sends audio/webm format)
            audio_file_like.name = "recording.webm"

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_like,
                language="en"
            )

            transcribed_text = transcript.text.strip()
            logger.info(f"✅ Interview voice transcribed: '{transcribed_text[:100]}...'")

            if not transcribed_text:
                return Response({
                    'error': 'Could not understand audio. Please speak more clearly.',
                    'transcribed_text': ''
                }, status=400)

        except Exception as e:
            logger.error(f"❌ Interview transcription failed: {str(e)}")
            return Response({
                'error': 'Failed to transcribe audio',
                'details': str(e)
            }, status=500)

        # Step 3: Submit transcribed text as interview response
        try:
            from intelligence.personal_assistant_interviewer import personal_assistant_interviewer
            from asgiref.sync import async_to_sync

            user_id = str(request.user.id)

            # Process the response through the interview system
            # Use async_to_sync which properly handles Django's async context
            result = async_to_sync(personal_assistant_interviewer.process_response)(user_id, transcribed_text)

            if result.get('error'):
                return Response({
                    'error': result['error'],
                    'transcribed_text': transcribed_text
                }, status=400)

            logger.info(f"✅ Interview voice response processed successfully")

            return Response({
                'success': True,
                'transcribed_text': transcribed_text,
                'acknowledgment': result.get('acknowledgment', ''),
                'question': result.get('question'),
                'interview_complete': result.get('interview_complete', False),
                'profile': result.get('profile'),
                'final_message': result.get('final_message'),
                'state': result.get('state')
            })

        except Exception as e:
            logger.error(f"❌ Interview processing failed: {str(e)}")
            return Response({
                'success': False,
                'transcribed_text': transcribed_text,
                'error': 'Transcription succeeded but interview processing failed',
                'details': str(e)
            }, status=500)

    except Exception as e:
        import traceback
        logger.error(f"❌ Voice interview failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'Failed to process voice input',
            'details': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_only(request):
    """
    Session 456: Transcribe audio only (no interview processing).

    Useful for getting transcription before submitting to interview.

    Request:
    - multipart/form-data with 'audio' file (webm/m4a/wav)

    Response:
    {
        "success": true,
        "text": "transcribed text..."
    }
    """
    try:
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Transcribe-only request from {request.user.username} ({audio_file.size} bytes)")

        import os
        from openai import OpenAI
        from io import BytesIO

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        audio_file.seek(0)
        audio_bytes = audio_file.read()
        audio_file_like = BytesIO(audio_bytes)
        audio_file_like.name = "recording.webm"

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_like,
            language="en"
        )

        transcribed_text = transcript.text.strip()
        logger.info(f"✅ Transcribed: '{transcribed_text[:100]}...'")

        return Response({
            'success': True,
            'text': transcribed_text
        })

    except Exception as e:
        logger.error(f"❌ Transcription failed: {str(e)}")
        return Response({
            'error': 'Failed to transcribe audio',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attention_items(request):
    """
    Session 574: Get attention items for the PA UI.

    Returns actionable items from SystemStateAggregator that need user attention.
    Each item can be clicked to execute via PA.
    """
    try:
        from core.services.system_state_aggregator import get_system_state_aggregator

        aggregator = get_system_state_aggregator()
        items = aggregator.get_attention_items()

        # Convert to serializable format
        attention_items = []
        for item in items[:10]:  # Max 10 items
            attention_items.append({
                'id': item.id,
                'section': item.section,
                'category': item.category,
                'priority': item.priority,
                'title': item.title[:80] if item.title else '',
                'summary': item.summary[:150] if item.summary else '',
                'action_url': item.action_url if hasattr(item, 'action_url') else '',
                # Suggested action for click-to-execute
                'suggested_action': _get_suggested_action(item),
            })

        return Response({
            'success': True,
            'items': attention_items,
            'count': len(attention_items),
        })

    except Exception as e:
        logger.error(f"Error getting attention items: {e}")
        return Response({
            'success': False,
            'items': [],
            'error': str(e)
        })


def _get_suggested_action(item):
    """Generate a suggested action command for an attention item.

    Session 574: These actions are designed to work with PA routing patterns.
    They should be clear commands that the PA can understand and execute.
    """
    section = item.section.lower() if item.section else ''
    title = item.title or 'this item'
    clean_title = title[:50].strip()

    # Session 574: Use patterns that match PA's action detection
    # Check if this is a Boardroom decision (has "Boardroom:" prefix)
    if clean_title.startswith('Boardroom:'):
        # Boardroom items - review and decide pattern (avoid triggering content agents)
        topic = clean_title.replace('Boardroom:', '').strip()
        return f"Review this pending decision and summarize the key points: {topic}"
    elif section == 'research':
        # Research items - ask for follow-up research
        return f"What are the latest developments regarding {clean_title}?"
    elif section == 'command_center':
        # Command center items - triage/review pattern
        return f"Triage and create action plan for: {clean_title}"
    elif section == 'autonomous':
        # Autonomous items - check status pattern
        return f"What is the status of {clean_title}? Summarize and suggest next steps."
    else:
        # Default - simple task pattern
        return f"Help me with: {clean_title}"
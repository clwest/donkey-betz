"""
Audio API Views (Session 48: Phase 3 - Audio UI)
Provides REST API endpoints for Runway ML audio features.
"""

import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from content.video_provider import runway_provider

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def text_to_speech(request):
    """
    POST /api/v1/audio/text-to-speech/
    Generate speech from text.

    Body: { "text": "...", "voice": "Rachel" }
    """
    try:
        import json
        data = json.loads(request.body)

        text = data.get('text', '').strip()
        voice = data.get('voice', 'Rachel')

        if not text:
            return JsonResponse({
                'success': False,
                'error_message': 'Text is required'
            }, status=400)

        logger.info(f"🗣️ Text-to-Speech request: {len(text)} chars, voice={voice}")

        # Call Runway ML provider
        result = runway_provider.text_to_speech(text=text, voice=voice)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"❌ Text-to-Speech error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def text_to_sound(request):
    """
    POST /api/v1/audio/text-to-sound/
    Generate sound effects from description.

    Body: { "description": "..." }
    """
    try:
        import json
        data = json.loads(request.body)

        description = data.get('description', '').strip()

        if not description:
            return JsonResponse({
                'success': False,
                'error_message': 'Description is required'
            }, status=400)

        logger.info(f"🔊 Text-to-Sound request: {description[:50]}...")

        # Call Runway ML provider
        result = runway_provider.text_to_sound(prompt=description)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"❌ Text-to-Sound error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def voice_dubbing(request):
    """
    POST /api/v1/audio/voice-dubbing/
    Dub audio to a different language.

    Form Data:
        - audio: audio file
        - target_language: language code (e.g., 'es', 'fr')
    """
    try:
        audio_file = request.FILES.get('audio')
        target_language = request.POST.get('target_language', 'es')

        if not audio_file:
            return JsonResponse({
                'success': False,
                'error_message': 'Audio file is required'
            }, status=400)

        logger.info(f"🌍 Voice Dubbing request: {audio_file.name}, target={target_language}")

        # Save uploaded file temporarily
        file_name = f"temp_dubbing_{audio_file.name}"
        file_path = default_storage.save(file_name, ContentFile(audio_file.read()))
        audio_url = request.build_absolute_uri(default_storage.url(file_path))

        # Call Runway ML provider
        result = runway_provider.voice_dubbing(
            audio_url=audio_url,
            target_language=target_language
        )

        # Clean up temp file
        try:
            default_storage.delete(file_path)
        except:
            pass

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"❌ Voice Dubbing error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def speech_to_speech(request):
    """
    POST /api/v1/audio/speech-to-speech/
    Convert voice to a different voice.

    Form Data:
        - audio: audio file
        - target_voice: voice name (e.g., 'Rachel', 'Maya')
    """
    try:
        audio_file = request.FILES.get('audio')
        target_voice = request.POST.get('target_voice', 'Rachel')

        if not audio_file:
            return JsonResponse({
                'success': False,
                'error_message': 'Audio file is required'
            }, status=400)

        logger.info(f"🎙️ Speech-to-Speech request: {audio_file.name}, target_voice={target_voice}")

        # Save uploaded file temporarily
        file_name = f"temp_sts_{audio_file.name}"
        file_path = default_storage.save(file_name, ContentFile(audio_file.read()))
        audio_url = request.build_absolute_uri(default_storage.url(file_path))

        # Call Runway ML provider
        result = runway_provider.speech_to_speech(
            media_url=audio_url,
            voice=target_voice
        )

        # Clean up temp file
        try:
            default_storage.delete(file_path)
        except:
            pass

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"❌ Speech-to-Speech error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def voice_isolation(request):
    """
    POST /api/v1/audio/voice-isolation/
    Isolate voice from background audio.

    Form Data:
        - audio: audio file (must be >= 4.6 seconds)
    """
    try:
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return JsonResponse({
                'success': False,
                'error_message': 'Audio file is required'
            }, status=400)

        logger.info(f"🎧 Voice Isolation request: {audio_file.name}")

        # Save uploaded file temporarily
        file_name = f"temp_isolation_{audio_file.name}"
        file_path = default_storage.save(file_name, ContentFile(audio_file.read()))
        audio_url = request.build_absolute_uri(default_storage.url(file_path))

        # Call Runway ML provider
        result = runway_provider.voice_isolation(audio_url=audio_url)

        # Clean up temp file
        try:
            default_storage.delete(file_path)
        except:
            pass

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"❌ Voice Isolation error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def check_audio_status(request, task_id):
    """
    GET /api/v1/audio/status/<task_id>/
    Check the status of an audio generation task.
    """
    try:
        logger.info(f"📊 Checking audio status for task: {task_id}")

        # Call Runway ML provider to check status
        result = runway_provider.check_status(task_id)

        # Convert VideoGenerationResult to dict for JSON response
        response_data = {
            'success': result.success,
            'status': result.status,
            'audio_url': result.video_url,  # Runway uses video_url field for audio too
            'progress': result.progress,
            'error_message': result.error_message if not result.success else None
        }

        # Session 81: Update AudioAgent state when audio completes
        if result.status in ['completed', 'SUCCEEDED'] and result.video_url:
            try:
                from core.agents import get_audio_agent
                audio_agent = get_audio_agent(user=request.user)
                audio_agent.update_audio_status(
                    task_id=task_id,
                    audio_url=result.video_url,
                    status='completed'
                )
                logger.info(f"✅ Updated AudioAgent state for completed audio: {task_id}")
            except Exception as e:
                logger.error(f"⚠️ Failed to update AudioAgent state: {e}")

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        return JsonResponse({
            'success': False,
            'status': 'failed',
            'error_message': str(e)
        }, status=500)


# =============================================================================
# Session 458: Chat Voice Output - Speak assistant responses
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def speak_text(request):
    """
    POST /api/tts/speak/
    Convert text to speech for chat voice output.

    Uses ElevenLabs for high-quality voice synthesis.
    Supports user's cloned voice or stock voices.

    Session 483: Added smart TTS optimization with summarization and chunking.

    Body: {
        "text": "Text to speak",
        "voice_id": "optional - ElevenLabs voice ID",
        "model": "eleven_flash_v2_5" (fast) or "eleven_multilingual_v2" (quality),
        "chunk_index": 0 (optional - for chunked playback)
    }

    Returns: {
        "success": true,
        "audio": "base64 encoded audio",
        "audio_format": "audio/mpeg",
        "was_summarized": false,
        "has_more_chunks": false,
        "chunk_index": 0,
        "total_chunks": 1
    }
    """
    import json
    import base64
    import requests
    from django.conf import settings
    from core.services.tts_optimizer import get_tts_optimizer, TTSStrategy

    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        voice_id = data.get('voice_id')
        model = data.get('model', 'eleven_flash_v2_5')  # Fast by default for chat
        chunk_index = data.get('chunk_index', 0)
        # Session 494: Allow users to skip summarization and hear full response
        skip_summarize = data.get('skip_summarize', False)

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text is required'
            }, status=400)

        # Use TTS optimizer for smart handling of long text
        # Session 494: Pass skip_summarize to preserve full response if requested
        optimizer = get_tts_optimizer(skip_summarize=skip_summarize)
        optimized = optimizer.optimize_with_intro(text, add_summary_notice=not skip_summarize)

        # Determine which text to speak
        if optimized.strategy == TTSStrategy.CHUNK and optimized.chunks:
            # Chunked playback - get the requested chunk
            if chunk_index >= len(optimized.chunks):
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid chunk index {chunk_index}, only {len(optimized.chunks)} chunks available'
                }, status=400)
            text_to_speak = optimized.chunks[chunk_index]
            total_chunks = len(optimized.chunks)
            has_more = chunk_index < total_chunks - 1
        else:
            # Direct or summarized - single audio
            text_to_speak = optimized.text
            total_chunks = 1
            has_more = False
            chunk_index = 0

        logger.info(f"🔊 [TTS] Strategy: {optimized.strategy.value}, "
                   f"Original: {optimized.original_length} chars, "
                   f"Optimized: {len(text_to_speak)} chars, "
                   f"Chunk: {chunk_index + 1}/{total_chunks}")

        # Get voice ID - check for user's cloned voice if not specified
        if not voice_id and request.user.is_authenticated:
            try:
                from core.models_voice_marketplace import VoiceProfile
                # Get user's own cloned voice
                user_voice = VoiceProfile.objects.filter(
                    owner=request.user,
                    is_active=True
                ).first()
                if user_voice:
                    voice_id = user_voice.elevenlabs_voice_id
                    logger.info(f"🎤 Using user's cloned voice: {user_voice.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not get user voice: {e}")

        # Fall back to default voice
        if not voice_id:
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - warm and expressive
            logger.info("🎤 Using default voice (Rachel)")

        # Get API key
        api_key = settings.EXTERNAL_API_KEYS.get('ELEVENLABS_API_KEY', '') if hasattr(settings, 'EXTERNAL_API_KEYS') else ''

        if not api_key:
            return JsonResponse({
                'success': False,
                'error': 'ElevenLabs API key not configured'
            }, status=500)

        # Call ElevenLabs API
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text_to_speak,  # Use optimized text, not original
            "model_id": model,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            params={"output_format": "mp3_44100_128"},
            timeout=30
        )

        if response.status_code != 200:
            logger.error(f"❌ ElevenLabs error: {response.status_code} - {response.text[:200]}")
            return JsonResponse({
                'success': False,
                'error': f"TTS generation failed: {response.status_code}"
            }, status=500)

        # Return audio as base64 for immediate playback
        audio_base64 = base64.b64encode(response.content).decode('utf-8')

        logger.info(f"✅ [TTS] Generated {len(response.content)} bytes of audio")

        return JsonResponse({
            'success': True,
            'audio': audio_base64,
            'audio_format': 'audio/mpeg',
            'was_summarized': optimized.was_summarized,
            'has_more_chunks': has_more,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'strategy': optimized.strategy.value
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ [TTS] Speak error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_user_voice_settings(request):
    """
    GET /api/tts/settings/
    Get user's voice output settings.

    Returns: {
        "success": true,
        "voice_enabled": true/false,
        "voice_id": "elevenlabs_voice_id",
        "voice_name": "Voice Name",
        "has_cloned_voice": true/false
    }
    """
    try:
        voice_enabled = False
        voice_id = None
        voice_name = "Rachel (Default)"
        has_cloned_voice = False

        if request.user.is_authenticated:
            # Check for user's cloned voice
            try:
                from core.models_voice_marketplace import VoiceProfile
                user_voice = VoiceProfile.objects.filter(
                    owner=request.user,
                    is_active=True
                ).first()
                if user_voice:
                    has_cloned_voice = True
                    voice_id = user_voice.elevenlabs_voice_id
                    voice_name = user_voice.name
            except Exception as e:
                logger.warning(f"⚠️ Could not get user voice: {e}")

            # Check user preference for voice enabled (stored in profile)
            try:
                from core.models.users.models import EnhancedUserProfile
                profile = EnhancedUserProfile.objects.filter(user=request.user).first()
                if profile and hasattr(profile, 'voice_output_enabled'):
                    voice_enabled = profile.voice_output_enabled
            except Exception as e:
                logger.warning(f"⚠️ Could not get voice preference: {e}")

        return JsonResponse({
            'success': True,
            'voice_enabled': voice_enabled,
            'voice_id': voice_id,
            'voice_name': voice_name,
            'has_cloned_voice': has_cloned_voice
        })

    except Exception as e:
        logger.error(f"❌ Get voice settings error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

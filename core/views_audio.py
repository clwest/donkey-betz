"""
Audio API Views (Session 48: Phase 3 - Audio UI)
Provides REST API endpoints for Runway ML audio features.

Session 990: Added _execute_generate_voice, _execute_add_voiceover (moved from views_image.py)
"""

import os
import uuid
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from content.video_provider import runway_provider

logger = logging.getLogger(__name__)


# =============================================================================
# Session 990: Agent-facing audio functions (moved from views_image.py)
# =============================================================================

def _execute_generate_voice(user, parameters, session=None):
    """
    Internal function for text-to-speech generation.
    Called by AudioAgent.

    Session 794: Use system user for autonomous operations (Celery tasks)
    Session 990: Moved from views_image.py to views_audio.py

    Args:
        user: Django user object
        parameters: Dict with text, voice, stability, similarity_boost
        session: Optional session for tracking

    Returns:
        Dict with success, audio_url
    """
    try:
        from core.views_image import get_system_user

        is_autonomous = user is None
        if is_autonomous:
            user = get_system_user()
            logger.info("Using system_autonomous user for voice generation")

        text = parameters.get('text')
        voice = parameters.get('voice', 'Rachel')
        stability = parameters.get('stability', 0.5)
        similarity_boost = parameters.get('similarity_boost', 0.75)

        if not text:
            return {'success': False, 'error': 'text required'}

        logger.info(f"Agent generating voice: '{text[:50]}...' with voice {voice}")

        from core.services.elevenlabs_tts_service import (
            generate_speech_with_retry, get_voice_id, get_audio_storage
        )

        voice_id = get_voice_id(voice)

        tts_result = generate_speech_with_retry(
            text=text,
            voice_id=voice_id,
            stability=stability,
            similarity_boost=similarity_boost,
            max_retries=3,
            base_timeout=60
        )

        if not tts_result['success']:
            logger.error(f"ElevenLabs TTS failed: {tts_result.get('error')}")
            return {'success': False, 'error': tts_result.get('error')}

        audio_data = tts_result['audio_data']

        filename = f'voice_{uuid.uuid4().hex[:8]}.mp3'
        username = user.username if user else 'system'
        filepath = os.path.join('generated_audio', username, filename)

        # Session 1003: Use RawMediaCloudinaryStorage for audio files in production.
        # The default MediaCloudinaryStorage rejects non-image files with
        # "Invalid image file", causing 89% AudioAgent failure rate.
        storage = get_audio_storage()
        saved_path = storage.save(filepath, ContentFile(audio_data))
        audio_url = storage.url(saved_path)

        logger.info(f"Agent generated voice: {saved_path}")

        audio_id = None
        from content.models import AudioHistory
        from core.services.workspace_resolver import get_active_workspace
        audio_record = AudioHistory.objects.create(
            user=user,
            session=session,
            filename=filename,
            file_path=saved_path,
            audio_type='tts',
            prompt=text,
            parameters={
                'stability': stability,
                'similarity_boost': similarity_boost,
                'model_id': 'eleven_monolingual_v1',
                'autonomous': is_autonomous
            },
            voice_id=voice_id,
            workspace=get_active_workspace(user),
            voice_name=voice,
            model_used='eleven_monolingual_v1',
            file_size_bytes=len(audio_data),
            status='completed'
        )
        audio_id = audio_record.id

        return {
            'success': True,
            'audio_url': audio_url,
            'audio_id': audio_id,
            'voice': voice,
            'voice_id': voice_id,
            'filename': filename,
            'file_path': saved_path,
            'message': f"Voice generated with {voice}"
        }

    except Exception as e:
        logger.error(f"Agent TTS error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_add_voiceover(user, parameters, session=None):
    """
    Internal function for adding voiceover to video.
    Called by AudioAgent.

    Session 990: Moved from views_image.py to views_audio.py

    Args:
        user: Django user object
        parameters: Dict with video_id, text, voice, background_volume
        session: Optional session for tracking

    Returns:
        Dict with success, video_url
    """
    try:
        video_id = parameters.get('video_id')
        text = parameters.get('text')
        voice = parameters.get('voice', 'Rachel')

        if not video_id or not text:
            return {'success': False, 'error': 'video_id and text required'}

        logger.info(f"Agent adding voiceover to video {video_id}")

        # First generate the voice
        voice_result = _execute_generate_voice(user, {
            'text': text,
            'voice': voice
        }, session)

        if not voice_result.get('success'):
            return voice_result

        # Video/audio mixing requires FFmpeg integration
        return {
            'success': False,
            'error': 'Video voiceover mixing not yet implemented',
            'audio_url': voice_result.get('audio_url')
        }

    except Exception as e:
        logger.error(f"Agent voiceover error: {e}")
        return {'success': False, 'error': str(e)}


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
        except Exception as _e:
            logger.warning(
                "views_audio.voice_dubbing: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

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
        except Exception as _e:
            logger.warning(
                "views_audio.speech_to_speech: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

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
        except Exception as _e:
            logger.warning(
                "views_audio.voice_isolation: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

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


# =============================================================================
# Session 926: Universal Agent Voice System - Listen Button TTS
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def tts_generate(request):
    """
    POST /api/tts/generate/
    Generate TTS audio with caching support.

    Supports agent voice lookup for automatic voice selection.

    Body: {
        "text": "Text to speak",
        "agent_name": "optional - looks up agent's voice",
        "voice_id": "optional - explicit ElevenLabs voice ID",
        "voice_name": "optional - voice name like Rachel"
    }

    Returns: {
        "success": true,
        "audio_url": "/media/audio_cache/...",
        "cached": true/false,
        "estimated_cost": 0.003,
        "duration_estimate": 5.2,
        "voice_name": "Rachel",
        "voice_id": "21m00Tcm4TlvDq8ikWAM"
    }
    """
    import json
    from core.services.elevenlabs_tts_service import generate_audio_cached

    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        agent_name = data.get('agent_name')
        voice_id = data.get('voice_id')
        voice_name = data.get('voice_name')

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text is required'
            }, status=400)

        logger.info(f"🔊 [TTS Generate] text={len(text)} chars, agent={agent_name}, "
                   f"voice_id={voice_id}, voice_name={voice_name}")

        result = generate_audio_cached(
            text=text,
            voice_id=voice_id,
            voice_name=voice_name,
            agent_name=agent_name,
        )

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ TTS Generate error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def tts_estimate(request):
    """
    POST /api/tts/estimate/
    Estimate TTS cost and duration before generation.

    Body: { "text": "Text to estimate" }

    Returns: {
        "text_length": 1500,
        "word_count": 250,
        "estimated_cost": 0.45,
        "estimated_duration": 100.0,
        "needs_confirmation": false
    }
    """
    import json
    from core.services.elevenlabs_tts_service import estimate_tts_cost

    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text is required'
            }, status=400)

        estimate = estimate_tts_cost(text)
        return JsonResponse({
            'success': True,
            **estimate
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ TTS Estimate error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def tts_voices(request):
    """
    GET /api/tts/voices/
    List available TTS voices.

    Returns: {
        "success": true,
        "voices": [
            {"name": "Rachel", "id": "21m00Tcm4TlvDq8ikWAM", "description": "Clear, authoritative"},
            ...
        ]
    }
    """
    from core.services.elevenlabs_tts_service import VOICE_IDS

    voice_descriptions = {
        'Rachel': 'Clear, authoritative - ideal for research and analysis',
        'Antoni': 'Warm, trustworthy - ideal for financial content',
        'Bella': 'Warm, engaging - ideal for creative content',
        'Daniel': 'Professional - ideal for technical content',
        'George': 'Deep, authoritative - ideal for executive communication',
        'Charlotte': 'Professional - ideal for legal content',
        'Emily': 'Friendly - ideal for marketing and social',
        'Matilda': 'Caring - ideal for health and wellness',
        'Callum': 'Strategic - ideal for planning content',
        'Domi': 'Technical - ideal for blockchain and crypto',
        'Sam': 'Energetic - ideal for sports content',
        'Elli': 'Friendly - ideal for support and assistance',
    }

    voices = [
        {
            'name': name,
            'id': voice_id,
            'description': voice_descriptions.get(name, 'General purpose voice')
        }
        for name, voice_id in VOICE_IDS.items()
    ]

    return JsonResponse({
        'success': True,
        'voices': voices
    })

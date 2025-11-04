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

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"❌ Status check error: {e}")
        return JsonResponse({
            'success': False,
            'status': 'failed',
            'error_message': str(e)
        }, status=500)

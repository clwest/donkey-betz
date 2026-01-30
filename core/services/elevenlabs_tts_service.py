"""
ElevenLabs TTS Service - Session 872
====================================

Centralized service for ElevenLabs text-to-speech operations with:
- Adaptive timeout based on text length
- Exponential backoff retry logic for transient failures
- Unified API key retrieval
- Voice profile integration

This service is used by:
- AudioAgent (core/agents/audio_agent.py)
- Podcast Audio Service (core/services/podcast_audio_service.py)
- Voice generation view (core/views_image.py)
"""

import logging
import os
import time
from typing import Dict, Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Voice ID mapping for all available voices
VOICE_IDS = {
    'Rachel': '21m00Tcm4TlvDq8ikWAM',
    'Antoni': 'ErXwobaYiN019PkySvjV',
    'Bella': 'EXAVITQu4vr4xnSDxMaL',
    'Callum': 'N2lVS1w4EtoT3dr4eOWO',
    'Charlotte': 'XB0fDUnXU5powFXDhCwa',
    'Daniel': 'onwK4e9ZLuTAKqWW03F9',
    'Domi': 'AZnzlk1XvdvUeBnXmlld',
    'Elli': 'MF3mGyEYCl7XYWbV9V6O',
    'Emily': 'LcfcDJNUP1GQjkzn1xUU',
    'George': 'JBFqnCBsd6RMkjVDRZzb',
    'Matilda': 'XrExE9yKIg1WjnnlVkGX',
    'Sam': 'yoZ06aMxZJJ28mfd3POQ',
}

# Podcast-specific voice mappings
PODCAST_VOICE_IDS = {
    "HOST": "ErXwobaYiN019PkySvjV",       # Antoni - warm narrator
    "MODERATOR": "ErXwobaYiN019PkySvjV",  # Antoni (alias for HOST)
    "ADVOCATE": "21m00Tcm4TlvDq8ikWAM",   # Rachel - enthusiastic, warm
    "SKEPTIC": "2EiwWnXFnvU5JabPnv8n",    # Clyde - authoritative, deep
    "ANALYST": "5Q0t7uMcjvnagumLfvZi",    # Paul - calm, conversational
}


def get_elevenlabs_api_key() -> Optional[str]:
    """
    Get ElevenLabs API key from environment or settings.

    Returns:
        API key string or None if not configured
    """
    return os.getenv('ELEVENLABS_API_KEY') or settings.EXTERNAL_API_KEYS.get('ELEVENLABS_API_KEY')


def calculate_adaptive_timeout(text: str, base_timeout: int = 60) -> int:
    """
    Calculate adaptive timeout based on text length.

    ElevenLabs processing time scales with text length:
    - Short text (<500 chars): 60 seconds
    - Medium text (500-2000 chars): 90 seconds
    - Long text (2000-5000 chars): 120 seconds
    - Very long text (>5000 chars): 180 seconds

    Args:
        text: The text to convert to speech
        base_timeout: Minimum timeout in seconds

    Returns:
        Timeout in seconds
    """
    char_count = len(text)

    if char_count < 500:
        return base_timeout
    elif char_count < 2000:
        return max(base_timeout, 90)
    elif char_count < 5000:
        return max(base_timeout, 120)
    else:
        # For very long text, add 20 seconds per 1000 chars beyond 5000
        extra_time = ((char_count - 5000) // 1000) * 20
        return min(180 + extra_time, 300)  # Cap at 5 minutes


def generate_speech_with_retry(
    text: str,
    voice_id: str,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    model_id: str = "eleven_monolingual_v1",
    max_retries: int = 3,
    base_timeout: int = 60
) -> Dict[str, Any]:
    """
    Generate speech using ElevenLabs TTS with retry logic.

    Features:
    - Adaptive timeout based on text length
    - Exponential backoff retry for transient failures
    - Detailed error reporting

    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity boost (0.0-1.0)
        model_id: ElevenLabs model ID
        max_retries: Maximum retry attempts for transient failures
        base_timeout: Base timeout in seconds (will be adjusted for text length)

    Returns:
        Dict with success, audio_data (bytes), error (if failed), retries_used
    """
    api_key = get_elevenlabs_api_key()
    if not api_key:
        return {'success': False, 'error': 'ElevenLabs API key not configured'}

    # Calculate adaptive timeout
    timeout = calculate_adaptive_timeout(text, base_timeout)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    last_error = None
    retries_used = 0

    for attempt in range(max_retries):
        try:
            logger.info(f"🎙️ ElevenLabs TTS attempt {attempt + 1}/{max_retries} "
                       f"(timeout={timeout}s, chars={len(text)})")

            response = requests.post(url, json=data, headers=headers, timeout=timeout)

            if response.status_code == 200:
                logger.info(f"✅ ElevenLabs TTS succeeded on attempt {attempt + 1}")
                return {
                    'success': True,
                    'audio_data': response.content,
                    'retries_used': retries_used,
                    'timeout_used': timeout,
                    'character_count': len(text)
                }

            # Check if error is retryable
            if response.status_code in [429, 500, 502, 503, 504]:
                # Rate limit or server error - retry with backoff
                last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                retries_used += 1
                wait_time = (2 ** attempt) + 1  # Exponential backoff: 2s, 5s, 9s
                logger.warning(f"⚠️ ElevenLabs TTS failed (retryable): {last_error}. "
                              f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            else:
                # Non-retryable error (e.g., 400 bad request, 401 unauthorized)
                logger.error(f"❌ ElevenLabs TTS failed (non-retryable): {response.text}")
                return {
                    'success': False,
                    'error': f'TTS failed: {response.text}',
                    'status_code': response.status_code,
                    'retries_used': retries_used
                }

        except requests.exceptions.Timeout:
            last_error = f"Timeout after {timeout} seconds"
            retries_used += 1
            logger.warning(f"⚠️ ElevenLabs TTS timeout on attempt {attempt + 1}. "
                          f"Text length: {len(text)} chars")
            # For timeouts, increase timeout on retry
            timeout = min(timeout + 30, 300)
            continue

        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)}"
            retries_used += 1
            wait_time = (2 ** attempt) + 1
            logger.warning(f"⚠️ ElevenLabs connection error. Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            continue

        except Exception as e:
            logger.error(f"❌ ElevenLabs TTS unexpected error: {e}")
            return {
                'success': False,
                'error': str(e),
                'retries_used': retries_used
            }

    # All retries exhausted
    logger.error(f"❌ ElevenLabs TTS failed after {max_retries} attempts: {last_error}")
    return {
        'success': False,
        'error': f'TTS failed after {max_retries} attempts: {last_error}',
        'retries_used': retries_used
    }


def get_voice_id(voice_name: str, fallback: str = 'Rachel') -> str:
    """
    Get voice ID from voice name.

    Args:
        voice_name: Name of the voice (e.g., 'Rachel', 'Antoni')
        fallback: Fallback voice if name not found

    Returns:
        ElevenLabs voice ID
    """
    # Check standard voices first
    if voice_name in VOICE_IDS:
        return VOICE_IDS[voice_name]

    # Check podcast voices
    if voice_name.upper() in PODCAST_VOICE_IDS:
        return PODCAST_VOICE_IDS[voice_name.upper()]

    # If voice_name looks like a voice ID (contains non-alpha), return as-is
    if not voice_name.isalpha():
        return voice_name

    # Return fallback
    return VOICE_IDS.get(fallback, VOICE_IDS['Rachel'])

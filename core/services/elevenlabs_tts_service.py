"""
ElevenLabs TTS Service - Session 872, 926
==========================================

Centralized service for ElevenLabs text-to-speech operations with:
- Adaptive timeout based on text length
- Exponential backoff retry logic for transient failures
- Unified API key retrieval
- Voice profile integration
- Audio caching for cost savings (Session 926)

This service is used by:
- AudioAgent (core/agents/audio_agent.py)
- Podcast Audio Service (core/services/podcast_audio_service.py)
- Voice generation view (core/views_image.py)
- Universal Listen Button (Session 926)
"""

import logging
import os
import time
from typing import Dict, Any, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_audio_storage():
    """Return a storage backend that can save audio (non-image) files.

    Session 1003: In production, DEFAULT_FILE_STORAGE is Cloudinary's
    MediaCloudinaryStorage which rejects MP3/WAV files with "Invalid image
    file".  Use RawMediaCloudinaryStorage for audio uploads instead.
    """
    from django.conf import settings
    from django.core.files.storage import default_storage
    if getattr(settings, 'DEFAULT_FILE_STORAGE', '') == 'cloudinary_storage.storage.MediaCloudinaryStorage':
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        return RawMediaCloudinaryStorage()
    return default_storage


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


# =============================================================================
# Session 926: Audio Caching for Universal Listen Button
# =============================================================================

# Agent category to voice mapping
AGENT_VOICE_MAP = {
    # Research & Analysis -> Rachel (clear, authoritative)
    'research': 'Rachel',
    'analysis': 'Rachel',
    'intelligence': 'Rachel',

    # Financial -> Antoni (trustworthy)
    'financial': 'Antoni',
    'trading': 'Antoni',
    'stocks': 'Antoni',
    'investment': 'Antoni',

    # Content & Creative -> Bella (warm, engaging)
    'content': 'Bella',
    'creative': 'Bella',
    'writing': 'Bella',
    'marketing': 'Emily',
    'social': 'Emily',

    # Technical & Development -> Daniel (professional)
    'technical': 'Daniel',
    'development': 'Daniel',
    'code': 'Daniel',
    'devops': 'Daniel',

    # Executive -> George (deep, authoritative)
    'executive': 'George',
    'cto': 'George',
    'coo': 'George',
    'strategy': 'Callum',

    # Legal & Compliance -> Charlotte (professional)
    'legal': 'Charlotte',
    'compliance': 'Charlotte',

    # Health & Wellness -> Matilda (caring)
    'health': 'Matilda',
    'wellness': 'Matilda',

    # Blockchain & Crypto -> Domi (technical)
    'blockchain': 'Domi',
    'crypto': 'Domi',

    # Sports -> Sam (energetic)
    'sports': 'Sam',
    'betting': 'Sam',

    # Support & Assistant -> Elli (friendly)
    'support': 'Elli',
    'assistant': 'Elli',
}


def get_voice_for_agent(agent_name: str, agent_category: str = None) -> str:
    """
    Get the appropriate voice for an agent based on name or category.

    Args:
        agent_name: Name of the agent (e.g., 'ContentWriterAgent')
        agent_category: Optional category slug (e.g., 'content')

    Returns:
        Voice name (e.g., 'Rachel')
    """
    # First check if agent has a voice_id in the database
    try:
        from core.models_unified_system import Agent
        agent = Agent.objects.filter(name=agent_name).first()
        if agent and agent.voice_id:
            # Could be a voice name or voice ID
            if agent.voice_id in VOICE_IDS:
                return agent.voice_id
            # Return as-is if it's already a voice ID
            return agent.voice_id
    except Exception as e:
        logger.warning(f"Could not look up agent voice: {e}")

    # Fall back to category mapping
    name_lower = agent_name.lower()

    # Check agent name patterns
    for keyword, voice in AGENT_VOICE_MAP.items():
        if keyword in name_lower:
            return voice

    # Check explicit category
    if agent_category:
        cat_lower = agent_category.lower()
        if cat_lower in AGENT_VOICE_MAP:
            return AGENT_VOICE_MAP[cat_lower]

    # Default to Rachel
    return 'Rachel'


def generate_audio_cached(
    text: str,
    voice_id: str = None,
    voice_name: str = None,
    agent_name: str = None,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    model_id: str = "eleven_monolingual_v1",
) -> Dict[str, Any]:
    """
    Generate TTS audio with caching support.

    Checks the AudioCache first. If not cached, generates via ElevenLabs
    and stores the result for future use.

    Args:
        text: Text to convert to speech
        voice_id: Explicit ElevenLabs voice ID (overrides voice_name and agent_name)
        voice_name: Voice name like 'Rachel' (overrides agent_name)
        agent_name: Agent name for automatic voice selection
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity boost (0.0-1.0)
        model_id: ElevenLabs model ID

    Returns:
        Dict with:
        - success: bool
        - audio_url: URL to the cached audio file (if success)
        - cached: bool - True if served from cache
        - estimated_cost: float - Cost in USD
        - duration_estimate: float - Estimated duration in seconds
        - error: str (if failed)
    """
    from decimal import Decimal
    from django.core.files.base import ContentFile

    # Determine voice to use
    if voice_id:
        resolved_voice_id = voice_id
        resolved_voice_name = next(
            (name for name, vid in VOICE_IDS.items() if vid == voice_id),
            None
        )
    elif voice_name:
        resolved_voice_id = get_voice_id(voice_name)
        resolved_voice_name = voice_name
    elif agent_name:
        resolved_voice_name = get_voice_for_agent(agent_name)
        resolved_voice_id = get_voice_id(resolved_voice_name)
    else:
        resolved_voice_name = 'Rachel'
        resolved_voice_id = VOICE_IDS['Rachel']

    # Check cache first
    try:
        from core.models_audio_cache import AudioCache

        cache_entry = AudioCache.get_cached(text, resolved_voice_id)
        if cache_entry:
            logger.info(f"🎵 Cache HIT for TTS (voice={resolved_voice_name}, chars={len(text)})")
            return {
                'success': True,
                'audio_url': cache_entry.audio_file.url,
                'cached': True,
                'estimated_cost': 0,  # Free from cache
                'duration_estimate': cache_entry.duration_seconds or (len(text) / 15),  # ~15 chars/sec
                'voice_name': resolved_voice_name,
                'voice_id': resolved_voice_id,
                'text_length': len(text),
            }
    except Exception as e:
        logger.warning(f"Cache lookup failed, generating fresh: {e}")

    logger.info(f"🎵 Cache MISS for TTS (voice={resolved_voice_name}, chars={len(text)})")

    # Generate audio via ElevenLabs
    result = generate_speech_with_retry(
        text=text,
        voice_id=resolved_voice_id,
        stability=stability,
        similarity_boost=similarity_boost,
        model_id=model_id,
    )

    if not result.get('success'):
        return {
            'success': False,
            'error': result.get('error', 'TTS generation failed'),
            'cached': False,
        }

    # Store in cache
    audio_data = result['audio_data']
    estimated_cost = (len(text) / 1000) * 0.30  # ~$0.30 per 1000 chars
    duration_estimate = len(text) / 15  # ~15 chars/sec estimate

    try:
        from core.models_audio_cache import AudioCache
        import uuid

        content_hash = AudioCache.compute_hash(text, resolved_voice_id)
        filename = f"{content_hash[:16]}_{uuid.uuid4().hex[:8]}.mp3"

        cache_entry = AudioCache.objects.create(
            content_hash=content_hash,
            audio_file=ContentFile(audio_data, name=filename),
            text_preview=text[:200],
            text_length=len(text),
            voice_id=resolved_voice_id,
            voice_name=resolved_voice_name or '',
            file_size_bytes=len(audio_data),
            duration_seconds=duration_estimate,
            generation_cost=Decimal(str(estimated_cost)),
        )

        logger.info(f"✅ Cached TTS audio: {filename} ({len(audio_data)} bytes)")

        return {
            'success': True,
            'audio_url': cache_entry.audio_file.url,
            'cached': False,  # Just generated, not from cache
            'estimated_cost': estimated_cost,
            'duration_estimate': duration_estimate,
            'voice_name': resolved_voice_name,
            'voice_id': resolved_voice_id,
            'text_length': len(text),
        }

    except Exception as e:
        logger.error(f"Failed to cache audio: {e}")
        # Return audio data directly if caching fails
        import base64
        return {
            'success': True,
            'audio_base64': base64.b64encode(audio_data).decode('utf-8'),
            'cached': False,
            'estimated_cost': estimated_cost,
            'duration_estimate': duration_estimate,
            'voice_name': resolved_voice_name,
            'voice_id': resolved_voice_id,
            'text_length': len(text),
            'cache_error': str(e),
        }


def estimate_tts_cost(text: str) -> Dict[str, Any]:
    """
    Estimate the cost and duration for TTS generation.

    Args:
        text: The text to estimate for

    Returns:
        Dict with:
        - text_length: int
        - estimated_cost: float (USD)
        - estimated_duration: float (seconds)
        - word_count: int
        - needs_confirmation: bool (True if > 2000 chars)
    """
    text_length = len(text)
    word_count = len(text.split())
    estimated_cost = (text_length / 1000) * 0.30
    estimated_duration = text_length / 15  # ~15 chars/sec

    return {
        'text_length': text_length,
        'word_count': word_count,
        'estimated_cost': round(estimated_cost, 4),
        'estimated_duration': round(estimated_duration, 1),
        'needs_confirmation': text_length > 2000,
    }

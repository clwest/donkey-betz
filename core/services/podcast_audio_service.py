"""
Podcast Audio Service - Session 496
Session 769: Added cost tracking for ElevenLabs TTS

Generates audio for AI Podcast Studio episodes using ElevenLabs TTS.
Parses scripts with speaker labels, generates audio per segment, and concatenates.

Workflow:
1. Parse script into speaker segments
2. Generate audio for each segment via ElevenLabs (with cost tracking)
3. Concatenate segments with pydub
4. Save final podcast audio
5. Return cost breakdown
"""

import logging
import os
import re
import uuid
from decimal import Decimal
from typing import Dict, List, Any, Optional
from io import BytesIO

import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pydub import AudioSegment

from core.services.api_cost_config import calculate_elevenlabs_cost, ELEVENLABS_COSTS

logger = logging.getLogger(__name__)


# Voice ID mapping for podcast speakers
PODCAST_VOICE_IDS = {
    "HOST": "ErXwobaYiN019PkySvjV",       # Antoni - warm narrator
    "MODERATOR": "ErXwobaYiN019PkySvjV",  # Antoni (alias for HOST)
    "ADVOCATE": "21m00Tcm4TlvDq8ikWAM",   # Rachel - enthusiastic, warm
    "SKEPTIC": "2EiwWnXFnvU5JabPnv8n",    # Clyde - authoritative, deep
    "ANALYST": "5Q0t7uMcjvnagumLfvZi",    # Paul - calm, conversational
}

# Speaker name to voice name mapping (for logging)
VOICE_NAMES = {
    "HOST": "Antoni",
    "MODERATOR": "Antoni",
    "ADVOCATE": "Rachel",
    "SKEPTIC": "Clyde",
    "ANALYST": "Paul",
}


def parse_podcast_script(script: str) -> List[Dict[str, Any]]:
    """
    Parse a podcast script into speaker segments.

    Expected format:
        HOST: Welcome to AI Debates!
        ADVOCATE: I believe AI should...
        SKEPTIC: But have we considered...
        ANALYST: Looking at the data...

    Skips non-spoken segments like:
        [INTRO MUSIC - 5 seconds]
        [SEGMENT: Opening]
        ---

    Returns:
        List of dicts: [{"speaker": "HOST", "voice_id": "...", "text": "..."}]
    """
    segments = []

    # Speaker pattern: SPEAKER: text (optionally with newlines until next speaker)
    speaker_pattern = re.compile(
        r'^(HOST|MODERATOR|ADVOCATE|SKEPTIC|ANALYST):\s*(.+?)(?=^(?:HOST|MODERATOR|ADVOCATE|SKEPTIC|ANALYST):|\Z)',
        re.MULTILINE | re.DOTALL
    )

    matches = speaker_pattern.findall(script)

    for speaker, text in matches:
        # Clean up the text
        cleaned_text = text.strip()

        # Skip empty segments
        if not cleaned_text:
            continue

        # Remove stage directions like [pauses], [laughs], etc.
        cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text)
        cleaned_text = cleaned_text.strip()

        if not cleaned_text:
            continue

        # Get voice ID for speaker
        voice_id = PODCAST_VOICE_IDS.get(speaker, PODCAST_VOICE_IDS["HOST"])
        voice_name = VOICE_NAMES.get(speaker, "Antoni")

        segments.append({
            "speaker": speaker,
            "voice_id": voice_id,
            "voice_name": voice_name,
            "text": cleaned_text
        })

    logger.info(f"📝 Parsed podcast script into {len(segments)} speaker segments")
    return segments


def generate_segment_audio(
    text: str,
    voice_id: str,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    model_id: str = "eleven_monolingual_v1"
) -> Dict[str, Any]:
    """
    Generate audio for a single segment using ElevenLabs TTS.

    Session 769: Now includes cost tracking.

    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID
        stability: Voice stability (0.0-1.0)
        similarity_boost: Voice similarity boost (0.0-1.0)
        model_id: ElevenLabs model ID

    Returns:
        Dict with success, audio_data (bytes), cost_info, error (if failed)
    """
    # Get ElevenLabs API key
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY') or settings.EXTERNAL_API_KEYS.get('ELEVENLABS_API_KEY')

    if not elevenlabs_key:
        return {'success': False, 'error': 'ElevenLabs API key not configured'}

    # Session 769: Calculate cost before making the API call
    cost_info = calculate_elevenlabs_cost(text, model=model_id)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_key
    }
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=120)

        if response.status_code != 200:
            logger.error(f"❌ ElevenLabs TTS failed: {response.text}")
            return {'success': False, 'error': f'TTS failed: {response.text}', 'cost_info': None}

        logger.info(f"💰 ElevenLabs TTS cost: ${cost_info['cost']:.4f} ({cost_info['character_count']} chars)")

        return {
            'success': True,
            'audio_data': response.content,
            'cost_info': cost_info,
        }

    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'ElevenLabs API timeout', 'cost_info': None}
    except Exception as e:
        logger.error(f"❌ ElevenLabs TTS error: {e}")
        return {'success': False, 'error': str(e)}


def concatenate_audio_segments(
    audio_segments: List[bytes],
    pause_ms: int = 500
) -> bytes:
    """
    Concatenate audio segments with pauses between them.

    Args:
        audio_segments: List of MP3 audio data as bytes
        pause_ms: Pause duration between segments in milliseconds

    Returns:
        Combined audio as bytes (MP3)
    """
    if not audio_segments:
        raise ValueError("No audio segments to concatenate")

    # Create pause segment
    pause = AudioSegment.silent(duration=pause_ms)

    # Load and combine segments
    combined = AudioSegment.empty()

    for i, audio_data in enumerate(audio_segments):
        # Load segment from bytes
        segment = AudioSegment.from_mp3(BytesIO(audio_data))

        # Add pause before segment (except for first)
        if i > 0:
            combined += pause

        combined += segment

    # Export as MP3
    output = BytesIO()
    combined.export(output, format="mp3", bitrate="192k")
    return output.getvalue()


def generate_podcast_audio(
    episode_id: str,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Main entry point for podcast audio generation.

    1. Load episode and script from database
    2. Parse script into speaker segments
    3. Generate audio for each segment (with progress updates)
    4. Concatenate all segments
    5. Save final audio and update episode

    Args:
        episode_id: UUID of the PodcastEpisode
        progress_callback: Optional callback(percent, message) for progress updates

    Returns:
        Dict with success, audio_url, duration_seconds, segment_count, error
    """
    from core.models_podcast_studio import PodcastEpisode

    try:
        episode = PodcastEpisode.objects.get(id=episode_id)
    except PodcastEpisode.DoesNotExist:
        return {'success': False, 'error': f'Episode not found: {episode_id}'}

    script = episode.script
    if not script:
        return {'success': False, 'error': 'Episode has no script'}

    # Update status
    episode.status = 'recording'
    episode.save(update_fields=['status'])

    if progress_callback:
        progress_callback(5, "Parsing script...")

    # 1. Parse script into segments
    segments = parse_podcast_script(script)

    if not segments:
        return {'success': False, 'error': 'No spoken segments found in script'}

    logger.info(f"🎙️ Generating audio for {len(segments)} segments")

    # 2. Generate audio for each segment
    # Session 769: Track costs per segment
    audio_segments = []
    segment_info = []
    total_tts_cost = Decimal('0')
    total_characters = 0

    for i, segment in enumerate(segments):
        progress_percent = 5 + int((i / len(segments)) * 80)  # 5-85%

        if progress_callback:
            progress_callback(
                progress_percent,
                f"Recording {segment['voice_name']} ({i+1}/{len(segments)})..."
            )

        logger.info(f"🎤 Recording segment {i+1}/{len(segments)}: {segment['speaker']} ({segment['voice_name']})")

        # Generate audio
        result = generate_segment_audio(
            text=segment['text'],
            voice_id=segment['voice_id']
        )

        if not result['success']:
            logger.error(f"❌ Failed to generate segment {i+1}: {result.get('error')}")
            # Continue with other segments rather than failing entirely
            continue

        audio_segments.append(result['audio_data'])

        # Session 769: Track cost from this segment
        cost_info = result.get('cost_info')
        if cost_info:
            total_tts_cost += Decimal(str(cost_info['cost']))
            total_characters += cost_info['character_count']

        segment_info.append({
            'speaker': segment['speaker'],
            'voice': segment['voice_name'],
            'text_length': len(segment['text']),
            'cost': float(cost_info['cost']) if cost_info else 0,
        })

    if not audio_segments:
        return {'success': False, 'error': 'Failed to generate any audio segments'}

    if progress_callback:
        progress_callback(90, "Assembling podcast...")

    # 3. Concatenate segments
    logger.info(f"🔗 Concatenating {len(audio_segments)} audio segments...")

    try:
        final_audio = concatenate_audio_segments(audio_segments)
    except Exception as e:
        logger.error(f"❌ Failed to concatenate audio: {e}")
        return {'success': False, 'error': f'Concatenation failed: {e}'}

    # 4. Calculate duration
    try:
        audio_segment = AudioSegment.from_mp3(BytesIO(final_audio))
        duration_seconds = len(audio_segment) / 1000.0
    except Exception as e:
        logger.warning(f"⚠️ Could not calculate duration: {e}")
        duration_seconds = 0

    # 5. Save audio file
    if progress_callback:
        progress_callback(95, "Saving audio file...")

    filename = f'podcast_{episode_id[:8]}_{uuid.uuid4().hex[:6]}.mp3'
    filepath = os.path.join('podcasts', 'episodes', filename)

    try:
        saved_path = default_storage.save(filepath, ContentFile(final_audio))
        audio_url = default_storage.url(saved_path)
    except Exception as e:
        logger.error(f"❌ Failed to save audio: {e}")
        return {'success': False, 'error': f'Failed to save audio: {e}'}

    # 6. Update episode
    episode.audio_url = audio_url
    episode.audio_duration_seconds = int(duration_seconds)
    episode.audio_segments = segment_info
    episode.status = 'complete'
    episode.progress_percent = 100
    episode.save()

    logger.info(f"✅ Podcast audio generated: {saved_path} ({duration_seconds:.1f}s)")
    logger.info(f"💰 Total TTS cost: ${float(total_tts_cost):.4f} ({total_characters} characters)")

    if progress_callback:
        progress_callback(100, "Audio complete!")

    # Session 769: Include cost breakdown in return
    return {
        'success': True,
        'audio_url': audio_url,
        'duration_seconds': duration_seconds,
        'segment_count': len(audio_segments),
        'saved_path': saved_path,
        # Session 769: Cost tracking
        'cost_breakdown': {
            'elevenlabs_tts': float(total_tts_cost),
            'total_characters': total_characters,
            'segments': segment_info,
        },
        'total_external_cost': float(total_tts_cost),
    }


def estimate_audio_duration(script: str) -> float:
    """
    Estimate podcast duration based on script length.

    Assumes average speaking rate of ~150 words per minute.

    Args:
        script: The podcast script text

    Returns:
        Estimated duration in seconds
    """
    segments = parse_podcast_script(script)
    total_words = sum(len(s['text'].split()) for s in segments)

    # 150 words per minute = 2.5 words per second
    estimated_seconds = total_words / 2.5

    # Add time for pauses between segments
    pause_time = len(segments) * 0.5

    return estimated_seconds + pause_time

"""
ElevenLabs Audio Generation Provider
Session 82: Professional voice quality for AI content creation

Handles text-to-speech and sound generation using ElevenLabs API.
Provides industry-leading voice quality with emotional range and nuance.
"""

import logging
import requests
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from django.conf import settings
from core.error_messages import ErrorMessageBuilder

logger = logging.getLogger(__name__)


@dataclass
class AudioGenerationResult:
    """Result from audio generation"""
    success: bool
    task_id: str = ""
    status: str = "completed"  # ElevenLabs returns audio immediately
    audio_url: str = ""
    error_message: str = ""
    estimated_time: int = 0


class ElevenLabsProvider:
    """ElevenLabs audio generation provider"""

    def __init__(self):
        # Get API key from EXTERNAL_API_KEYS (same pattern as Runway)
        self.api_key = settings.EXTERNAL_API_KEYS.get('ELEVENLABS_API_KEY', '') if hasattr(settings, 'EXTERNAL_API_KEYS') else getattr(settings, 'ELEVENLABS_API_KEY', '')
        self.api_base = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        # Voice ID mapping (Session 82: Professional voices)
        # These are ElevenLabs preset voice IDs
        self.voice_map = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",  # Female, warm and expressive
            "Drew": "29vD33N1CtxCmqQRPOHJ",    # Male, clear and well-rounded
            "Clyde": "2EiwWnXFnvU5JabPnv8n",   # Male, deep and authoritative
            "Paul": "5Q0t7uMcjvnagumLfvZi",    # Male, friendly and conversational
            "Aria": "9BWtsMINqrJLrRacOk9x",    # Female, professional and confident
            "Domi": "AZnzlk1XvdvUeBnXmlld",    # Female, energetic and youthful
            "Dave": "CYw3kZ02Hs0563khs1Fj",    # Male, casual and approachable
            "Antoni": "ErXwobaYiN019PkySvjV",  # Male, trustworthy narrator
            "Sarah": "EXAVITQu4vr4xnSDxMaL",   # Female, soft and gentle
            "Josh": "TxGEqnHWrfWFTfGW9XjX",    # Male, energetic and upbeat
            "Bella": "EXAVITQu4vr4xnSDxMaL",   # Female, engaging storyteller
            "Charlotte": "XB0fDUnXU5powFXDhCwa" # Female, clear and articulate
        }

    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        return bool(self.api_key)

    def text_to_speech(
        self,
        text: str,
        voice: str = "Rachel",
        model: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convert text to speech using ElevenLabs

        Args:
            text: Text to convert to speech
            voice: Voice name (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave, etc.)
            model: "eleven_multilingual_v2" (highest quality) or "eleven_flash_v2_5" (faster)
            output_format: Audio format (mp3_44100_128, pcm_16000, etc.)
            **kwargs: Additional parameters (stability, similarity_boost, style, speed)

        Returns:
            Dict with success, audio_url, status
        """

        if not self.api_key:
            error = ErrorMessageBuilder.api_key_error("ElevenLabs", "ELEVENLABS_API_KEY")
            return {
                "success": False,
                "error_message": error["user_message"]
            }

        # Get voice ID from name
        voice_id = self.voice_map.get(voice)
        if not voice_id:
            logger.warning(f"Unknown voice '{voice}', using Rachel as default")
            voice_id = self.voice_map["Rachel"]
            voice = "Rachel"

        try:
            logger.info(f"🎤 [ELEVENLABS] Generating speech with {voice} voice...")
            logger.info(f"📝 Text: {text[:100]}...")

            # Prepare request payload
            payload = {
                "text": text,
                "model_id": model
            }

            # Add voice settings if provided
            voice_settings = {}
            if kwargs.get('stability') is not None:
                voice_settings['stability'] = kwargs['stability']
            if kwargs.get('similarity_boost') is not None:
                voice_settings['similarity_boost'] = kwargs['similarity_boost']
            if kwargs.get('style') is not None:
                voice_settings['style'] = kwargs['style']
            if kwargs.get('speed') is not None:
                voice_settings['speed'] = kwargs['speed']

            if voice_settings:
                payload['voice_settings'] = voice_settings

            # Add optional parameters
            if kwargs.get('language_code'):
                payload['language_code'] = kwargs['language_code']
            if kwargs.get('apply_text_normalization'):
                payload['apply_text_normalization'] = kwargs['apply_text_normalization']

            # Build URL with query parameters
            url = f"{self.api_base}/text-to-speech/{voice_id}"
            params = {
                "output_format": output_format
            }
            if kwargs.get('optimize_streaming_latency'):
                params['optimize_streaming_latency'] = kwargs['optimize_streaming_latency']

            logger.info(f"📤 Sending request to ElevenLabs API...")

            # Make request
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                params=params,
                timeout=60  # ElevenLabs returns audio immediately
            )

            logger.info(f"📥 Response status: {response.status_code}")

            if response.status_code != 200:
                error = ErrorMessageBuilder.parse_api_error("ElevenLabs", response.status_code, response.text)
                logger.error(f"❌ {error['user_message']}")
                return {
                    "success": False,
                    "error_message": error["user_message"]
                }

            # Save audio to temp file and upload to storage
            # For now, we'll return the audio data directly
            audio_data = response.content

            # In production, we would upload to S3/CDN
            # For now, we'll create a data URI or save to media folder
            import os
            import uuid
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage

            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"elevenlabs_speech_{file_id}.mp3"
            filepath = f"audio/elevenlabs/{filename}"

            # Save to Django storage
            saved_path = default_storage.save(filepath, ContentFile(audio_data))
            audio_url = default_storage.url(saved_path)

            logger.info(f"✅ Speech generated successfully!")
            logger.info(f"🎵 Audio saved: {audio_url}")

            return {
                "success": True,
                "task_id": file_id,  # Use file_id as task_id for consistency
                "status": "completed",  # ElevenLabs returns completed audio immediately
                "audio_url": audio_url,
                "estimated_time": 0  # Already completed
            }

        except Exception as e:
            logger.error(f"❌ ElevenLabs text-to-speech error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }

    def text_to_sound(
        self,
        prompt: str,
        duration: float = 5.0,
        prompt_influence: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate sound effects from text description using ElevenLabs Sound Generation

        Args:
            prompt: Description of the sound effect to generate
            duration: Duration in seconds (0.5 to 22 seconds)
            prompt_influence: How much to follow the prompt (0.0 to 1.0)
            **kwargs: Additional parameters

        Returns:
            Dict with success, audio_url, status
        """

        if not self.api_key:
            error = ErrorMessageBuilder.api_key_error("ElevenLabs", "ELEVENLABS_API_KEY")
            return {
                "success": False,
                "error_message": error["user_message"]
            }

        try:
            logger.info(f"🔊 [ELEVENLABS] Generating sound effect...")
            logger.info(f"📝 Prompt: {prompt}")
            logger.info(f"⏱️ Duration: {duration}s")

            # Prepare request payload
            payload = {
                "text": prompt,
                "duration_seconds": duration,
                "prompt_influence": prompt_influence
            }

            url = f"{self.api_base}/sound-generation"

            logger.info(f"📤 Sending request to ElevenLabs Sound Generation API...")

            # Make request
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            logger.info(f"📥 Response status: {response.status_code}")

            if response.status_code != 200:
                error = ErrorMessageBuilder.parse_api_error("ElevenLabs", response.status_code, response.text)
                logger.error(f"❌ {error['user_message']}")
                return {
                    "success": False,
                    "error_message": error["user_message"]
                }

            # Save audio data
            audio_data = response.content

            import os
            import uuid
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage

            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"elevenlabs_sound_{file_id}.mp3"
            filepath = f"audio/elevenlabs/{filename}"

            # Save to Django storage
            saved_path = default_storage.save(filepath, ContentFile(audio_data))
            audio_url = default_storage.url(saved_path)

            logger.info(f"✅ Sound effect generated successfully!")
            logger.info(f"🎵 Audio saved: {audio_url}")

            return {
                "success": True,
                "task_id": file_id,
                "status": "completed",
                "audio_url": audio_url,
                "estimated_time": 0
            }

        except Exception as e:
            logger.error(f"❌ ElevenLabs sound generation error: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }


# Global provider instance
elevenlabs_provider = ElevenLabsProvider()

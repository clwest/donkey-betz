"""
Discord Voice AI Service - Session 438

Voice channel integration with ElevenLabs TTS and OpenAI Whisper STT.
Enables voice-based interaction with the AI assistant in Discord voice channels.

Features:
- Join/leave voice channels
- Speak responses using ElevenLabs voices
- Listen and transcribe using Whisper
- Process voice commands like text commands
"""

import os
import io
import logging
import asyncio
import tempfile
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field

import discord
from discord.ext import commands
from openai import OpenAI
import httpx

logger = logging.getLogger(__name__)

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY') or os.getenv('ELEVEN_LABS_API')
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# OpenAI for Whisper transcription
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Voice IDs for ElevenLabs (common voices)
ELEVENLABS_VOICES = {
    'rachel': 'EXAVITQu4vr4xnSDxMaL',      # Warm, professional female
    'antoni': '21m00Tcm4TlvDq8ikWAM',       # Authoritative male
    'bella': 'AZnzlk1XvdvUeBnXmlld',        # Friendly female
    'callum': 'N2lVS1w4EtoT3dr4eOWO',       # Confident British male
    'charlotte': 'XB0fDUnXU5powFXDhCwa',    # Warm British female
    'daniel': 'onwK4e9ZLuTAKqWW03F9',       # Clear, neutral male
    'domi': 'AZnzlk1XvdvUeBnXmlld',         # Strong female
    'elli': 'MF3mGyEYCl7XYWbV9V6O',         # Expressive female
    'josh': 'TxGEqnHWrfWFTfGW9XjX',         # Deep male
    'sam': 'yoZ06aMxZJJ28mfd3POQ',          # Neutral young male
}

DEFAULT_VOICE = 'rachel'


@dataclass
class VoiceSession:
    """Represents an active voice session in a channel."""
    guild_id: int
    channel_id: int
    voice_client: discord.VoiceClient
    started_at: datetime = field(default_factory=datetime.now)
    is_listening: bool = False
    is_speaking: bool = False
    current_voice: str = DEFAULT_VOICE
    conversation_history: list = field(default_factory=list)
    transcribe_callback: Optional[Callable] = None


class DiscordVoiceService:
    """Handles Discord voice channel interactions with AI."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.sessions: Dict[int, VoiceSession] = {}  # guild_id -> VoiceSession
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

        # Check dependencies
        self.elevenlabs_available = bool(ELEVENLABS_API_KEY)
        self.whisper_available = bool(self.openai_client)

        logger.info(f"Voice AI initialized - ElevenLabs: {self.elevenlabs_available}, Whisper: {self.whisper_available}")

    async def join_channel(
        self,
        channel: discord.VoiceChannel,
        voice: str = DEFAULT_VOICE
    ) -> Optional[VoiceSession]:
        """Join a voice channel and create a session."""
        try:
            guild_id = channel.guild.id

            # Leave existing session if any
            if guild_id in self.sessions:
                await self.leave_channel(channel.guild)

            # Connect to voice channel
            voice_client = await channel.connect()

            # Create session
            session = VoiceSession(
                guild_id=guild_id,
                channel_id=channel.id,
                voice_client=voice_client,
                current_voice=voice
            )

            self.sessions[guild_id] = session

            logger.info(f"Joined voice channel {channel.name} in {channel.guild.name}")

            # Speak greeting
            await self.speak(
                session,
                f"Hello! I'm your AI assistant. Ask me anything, or say 'goodbye' to disconnect."
            )

            return session

        except Exception as e:
            logger.error(f"Error joining voice channel: {e}")
            return None

    async def leave_channel(self, guild: discord.Guild) -> bool:
        """Leave the voice channel in a guild."""
        try:
            session = self.sessions.get(guild.id)
            if not session:
                return False

            # Say goodbye
            await self.speak(session, "Goodbye! It was nice talking with you.")

            # Disconnect
            if session.voice_client.is_connected():
                await session.voice_client.disconnect()

            # Clean up
            del self.sessions[guild.id]

            logger.info(f"Left voice channel in {guild.name}")
            return True

        except Exception as e:
            logger.error(f"Error leaving voice channel: {e}")
            return False

    async def speak(
        self,
        session: VoiceSession,
        text: str,
        voice: Optional[str] = None
    ) -> bool:
        """Speak text in the voice channel using ElevenLabs TTS."""
        if not self.elevenlabs_available:
            logger.warning("ElevenLabs not available for TTS")
            return False

        if not session.voice_client.is_connected():
            logger.warning("Not connected to voice channel")
            return False

        try:
            session.is_speaking = True

            # Get voice ID
            voice_name = voice or session.current_voice
            voice_id = ELEVENLABS_VOICES.get(voice_name.lower(), ELEVENLABS_VOICES[DEFAULT_VOICE])

            # Generate audio from ElevenLabs
            audio_data = await self._generate_speech(text, voice_id)
            if not audio_data:
                return False

            # Save to temp file (discord.py needs file path for FFmpegPCMAudio)
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            # Play audio
            audio_source = discord.FFmpegPCMAudio(temp_path)
            session.voice_client.play(
                audio_source,
                after=lambda e: self._cleanup_audio(temp_path, e)
            )

            # Wait for playback to complete
            while session.voice_client.is_playing():
                await asyncio.sleep(0.1)

            session.is_speaking = False
            return True

        except Exception as e:
            logger.error(f"Error speaking: {e}")
            session.is_speaking = False
            return False

    async def _generate_speech(self, text: str, voice_id: str) -> Optional[bytes]:
        """Generate speech using ElevenLabs API."""
        try:
            url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": ELEVENLABS_API_KEY,
            }

            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=30.0)

                if response.status_code == 200:
                    return response.content
                else:
                    logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None

    def _cleanup_audio(self, path: str, error: Optional[Exception]):
        """Clean up temp audio file after playback."""
        try:
            if error:
                logger.error(f"Audio playback error: {error}")
            os.unlink(path)
        except Exception as e:
            logger.warning(f"Could not delete temp file {path}: {e}")

    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper."""
        if not self.whisper_available:
            logger.warning("Whisper not available for transcription")
            return None

        try:
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_data)
                temp_path = f.name

            # Transcribe with Whisper
            with open(temp_path, 'rb') as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            # Clean up
            os.unlink(temp_path)

            return transcript.text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    async def process_voice_command(
        self,
        session: VoiceSession,
        text: str,
        user: discord.Member
    ) -> str:
        """Process a voice command and return the response."""
        try:
            # Add to conversation history
            session.conversation_history.append({
                'role': 'user',
                'content': text,
                'user': user.display_name,
                'timestamp': datetime.now().isoformat()
            })

            # Check for exit commands
            exit_phrases = ['goodbye', 'bye', 'leave', 'disconnect', 'exit', 'quit']
            if any(phrase in text.lower() for phrase in exit_phrases):
                return "__EXIT__"

            # Check for voice change commands
            if text.lower().startswith('change voice to '):
                new_voice = text[16:].strip().lower()
                if new_voice in ELEVENLABS_VOICES:
                    session.current_voice = new_voice
                    return f"Voice changed to {new_voice}."
                else:
                    return f"Unknown voice. Available voices: {', '.join(ELEVENLABS_VOICES.keys())}"

            # Process with AI (using OpenAI for now)
            if self.openai_client:
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful voice assistant in a Discord voice channel. "
                            "Keep responses concise and conversational since they will be spoken aloud. "
                            "Avoid long lists or complex formatting. Be friendly and natural."
                        )
                    }
                ]

                # Add recent conversation history
                for msg in session.conversation_history[-5:]:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=300  # Keep responses short for voice
                )

                ai_response = response.choices[0].message.content

                # Add to history
                session.conversation_history.append({
                    'role': 'assistant',
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                })

                return ai_response
            else:
                return "I'm sorry, AI processing is not available right now."

        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return "I encountered an error processing your request."

    def get_session(self, guild_id: int) -> Optional[VoiceSession]:
        """Get the voice session for a guild."""
        return self.sessions.get(guild_id)

    def is_in_voice(self, guild_id: int) -> bool:
        """Check if bot is in a voice channel in the guild."""
        session = self.sessions.get(guild_id)
        return session is not None and session.voice_client.is_connected()

    async def set_voice(self, guild_id: int, voice: str) -> bool:
        """Set the voice for a session."""
        session = self.sessions.get(guild_id)
        if not session:
            return False

        if voice.lower() not in ELEVENLABS_VOICES:
            return False

        session.current_voice = voice.lower()
        return True

    def get_available_voices(self) -> list:
        """Get list of available voices."""
        return list(ELEVENLABS_VOICES.keys())


# Global instance (initialized when bot starts)
voice_service: Optional[DiscordVoiceService] = None


def get_voice_service() -> Optional[DiscordVoiceService]:
    """Get the global voice service instance."""
    return voice_service


def init_voice_service(bot: commands.Bot) -> DiscordVoiceService:
    """Initialize the voice service with a bot instance."""
    global voice_service
    voice_service = DiscordVoiceService(bot)
    return voice_service

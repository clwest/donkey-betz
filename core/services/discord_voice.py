"""
Discord Voice AI Service - Session 438/441

Voice channel integration with ElevenLabs TTS and OpenAI Whisper STT.
Enables voice-based interaction with the AI assistant in Discord voice channels.

Features:
- Join/leave voice channels
- Speak responses using ElevenLabs voices
- Listen and transcribe using Whisper
- Process voice commands like text commands
- Record user voice for cloning (Session 441)
- Clone voices via ElevenLabs API (Session 441)
"""

import os
import logging
import asyncio
import tempfile
import wave
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

import discord
from discord.ext import commands
from openai import OpenAI
import httpx

# Voice receiving extension for discord.py
try:
    VOICE_RECV_AVAILABLE = True
except ImportError:
    VOICE_RECV_AVAILABLE = False

logger = logging.getLogger(__name__)

# Load opus library for voice support (required on macOS)
def ensure_opus_loaded():
    """Ensure opus library is loaded for voice support."""
    if discord.opus.is_loaded():
        return True

    opus_paths = [
        '/opt/homebrew/lib/libopus.dylib',  # macOS Homebrew ARM
        '/usr/local/lib/libopus.dylib',      # macOS Homebrew Intel
        '/usr/lib/x86_64-linux-gnu/libopus.so.0',  # Linux
        'opus',  # System default
    ]

    for path in opus_paths:
        try:
            discord.opus.load_opus(path)
            logger.info(f"Opus library loaded from {path}")
            return True
        except Exception:
            continue

    logger.error("Could not load opus library from any known path!")
    return False

# Try to load opus at import time
ensure_opus_loaded()

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


# =============================================================================
# Session 441: Voice Recording for Cloning
# =============================================================================

@dataclass
class RecordingSession:
    """Tracks an active voice recording session for voice cloning."""
    user_id: int
    guild_id: int
    channel_id: int
    started_at: datetime = field(default_factory=datetime.now)
    audio_chunks: List[bytes] = field(default_factory=list)
    is_active: bool = True
    output_path: Optional[str] = None


class VoiceRecorder:
    """
    Records user voice from Discord for voice cloning.

    Uses discord-ext-voice-recv to capture audio from voice channels.
    Audio is saved as WAV format suitable for ElevenLabs cloning.
    """

    def __init__(self):
        self.active_recordings: Dict[int, RecordingSession] = {}  # user_id -> RecordingSession
        self.recording_dir = Path(tempfile.gettempdir()) / "discord_voice_recordings"
        self.recording_dir.mkdir(exist_ok=True)

        if not VOICE_RECV_AVAILABLE:
            logger.warning("discord-ext-voice-recv not available - voice recording disabled")

    def is_available(self) -> bool:
        """Check if voice recording is available."""
        return VOICE_RECV_AVAILABLE

    def start_recording(self, user_id: int, guild_id: int, channel_id: int) -> Optional[RecordingSession]:
        """Start recording a user's voice."""
        if not VOICE_RECV_AVAILABLE:
            logger.error("Cannot start recording - voice_recv not available")
            return None

        # Stop any existing recording for this user
        if user_id in self.active_recordings:
            self.stop_recording(user_id)

        session = RecordingSession(
            user_id=user_id,
            guild_id=guild_id,
            channel_id=channel_id
        )
        self.active_recordings[user_id] = session

        logger.info(f"Started recording for user {user_id} in channel {channel_id}")
        return session

    def add_audio_chunk(self, user_id: int, audio_data: bytes) -> bool:
        """Add audio data to a user's recording session."""
        session = self.active_recordings.get(user_id)
        if not session or not session.is_active:
            return False

        session.audio_chunks.append(audio_data)
        return True

    def stop_recording(self, user_id: int) -> Optional[str]:
        """
        Stop recording and save the audio to a WAV file.

        Returns the path to the saved audio file, or None if failed.
        """
        session = self.active_recordings.get(user_id)
        if not session:
            return None

        session.is_active = False

        if not session.audio_chunks:
            logger.warning(f"No audio data recorded for user {user_id}")
            del self.active_recordings[user_id]
            return None

        # Combine all audio chunks
        combined_audio = b''.join(session.audio_chunks)

        # Save as WAV file
        # Discord audio is 48kHz, 16-bit, stereo PCM
        output_path = self.recording_dir / f"voice_clone_{user_id}_{int(datetime.now().timestamp())}.wav"

        try:
            with wave.open(str(output_path), 'wb') as wav_file:
                wav_file.setnchannels(2)  # Stereo
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(48000)  # 48kHz
                wav_file.writeframes(combined_audio)

            session.output_path = str(output_path)
            duration = len(combined_audio) / (48000 * 2 * 2)  # samples / (rate * channels * bytes_per_sample)

            logger.info(f"Saved recording for user {user_id}: {output_path} ({duration:.1f} seconds)")

            # Clean up session but keep reference for retrieval
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to save recording for user {user_id}: {e}")
            return None
        finally:
            # Clean up the active session
            if user_id in self.active_recordings:
                del self.active_recordings[user_id]

    def get_recording_duration(self, user_id: int) -> float:
        """Get the current recording duration in seconds."""
        session = self.active_recordings.get(user_id)
        if not session:
            return 0.0

        total_bytes = sum(len(chunk) for chunk in session.audio_chunks)
        # 48kHz, stereo, 16-bit = 48000 * 2 * 2 = 192000 bytes per second
        return total_bytes / 192000.0

    def is_recording(self, user_id: int) -> bool:
        """Check if a user is currently being recorded."""
        session = self.active_recordings.get(user_id)
        return session is not None and session.is_active

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up recording files older than max_age_hours."""
        import time
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in self.recording_dir.glob("voice_clone_*.wav"):
            if now - file_path.stat().st_mtime > max_age_seconds:
                try:
                    file_path.unlink()
                    logger.info(f"Cleaned up old recording: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {file_path}: {e}")


class VoiceRecordingSink:
    """
    Audio sink that captures voice data for a specific user.

    Used with discord-ext-voice-recv to capture audio from voice channels.
    """

    def __init__(self, recorder: VoiceRecorder, target_user_id: int):
        self.recorder = recorder
        self.target_user_id = target_user_id
        self.packet_count = 0
        logger.info(f"VoiceRecordingSink created for user {target_user_id}")

    def write(self, user, data):
        """Called when audio data is received from a user."""
        self.packet_count += 1
        if self.packet_count <= 5 or self.packet_count % 100 == 0:
            logger.info(f"Audio packet #{self.packet_count} from user {user} (target: {self.target_user_id})")

        # Filter to only capture from target user
        user_id = getattr(user, 'id', None) if user else None
        if user_id == self.target_user_id:
            # data.pcm contains the raw PCM audio data
            pcm_data = getattr(data, 'pcm', None)
            if pcm_data:
                self.recorder.add_audio_chunk(user_id, pcm_data)
                if self.packet_count <= 5:
                    logger.info(f"Captured {len(pcm_data)} bytes of PCM data")

    def cleanup(self):
        """Called when the sink is stopped."""
        logger.info(f"VoiceRecordingSink cleanup - total packets: {self.packet_count}")


# =============================================================================
# Session 441: ElevenLabs Voice Cloning API
# =============================================================================

class ElevenLabsVoiceCloner:
    """
    Handles voice cloning via ElevenLabs Instant Voice Clone (IVC) API.

    Endpoint: POST https://api.elevenlabs.io/v1/voices/add
    """

    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.api_url = f"{ELEVENLABS_API_URL}/voices/add"

    def is_available(self) -> bool:
        """Check if ElevenLabs API is configured."""
        return bool(self.api_key)

    async def clone_voice(
        self,
        audio_file_path: str,
        voice_name: str,
        description: str = "",
        remove_background_noise: bool = True,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Clone a voice from an audio file using ElevenLabs IVC API.

        Args:
            audio_file_path: Path to the WAV audio file
            voice_name: Name for the cloned voice
            description: Optional description of the voice
            remove_background_noise: Whether to apply noise reduction
            labels: Optional categorization labels

        Returns:
            Dict with 'voice_id' on success, or 'error' on failure
        """
        if not self.is_available():
            return {"error": "ElevenLabs API key not configured"}

        if not os.path.exists(audio_file_path):
            return {"error": f"Audio file not found: {audio_file_path}"}

        # Check file size and compress if needed (ElevenLabs has 10MB limit)
        file_size = os.path.getsize(audio_file_path)
        upload_path = audio_file_path
        content_type = 'audio/wav'

        if file_size > 8 * 1024 * 1024:  # Compress if > 8MB to be safe
            logger.info(f"Audio file is {file_size / 1024 / 1024:.1f}MB, compressing to MP3...")
            try:
                import subprocess
                mp3_path = audio_file_path.replace('.wav', '.mp3')
                # Use ffmpeg to compress to MP3 (128kbps mono)
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', audio_file_path,
                    '-ac', '1',  # Mono
                    '-ar', '22050',  # 22kHz sample rate
                    '-b:a', '128k',  # 128kbps bitrate
                    mp3_path
                ], capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(mp3_path):
                    new_size = os.path.getsize(mp3_path)
                    logger.info(f"Compressed to {new_size / 1024 / 1024:.1f}MB MP3")
                    upload_path = mp3_path
                    content_type = 'audio/mpeg'
                else:
                    logger.warning(f"ffmpeg compression failed: {result.stderr}")
            except Exception as e:
                logger.warning(f"Could not compress audio: {e}")

        # Final size check
        final_size = os.path.getsize(upload_path)
        if final_size > 10 * 1024 * 1024:
            return {"error": "Audio file too large (max 10MB even after compression)"}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Read file content
                with open(upload_path, 'rb') as f:
                    file_content = f.read()

                data = {
                    'name': voice_name,
                    'remove_background_noise': str(remove_background_noise).lower()
                }

                if description:
                    data['description'] = description

                if labels:
                    import json
                    data['labels'] = json.dumps(labels)

                headers = {
                    'xi-api-key': self.api_key
                }

                # Make the request
                files = [
                    ('files', (os.path.basename(upload_path), file_content, content_type))
                ]

                response = await client.post(
                    self.api_url,
                    data=data,
                    files=files,
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Voice cloned successfully: {result.get('voice_id')}")
                    return {
                        "voice_id": result.get("voice_id"),
                        "requires_verification": result.get("requires_verification", False)
                    }
                else:
                    error_detail = response.text
                    logger.error(f"ElevenLabs API error: {response.status_code} - {error_detail}")
                    return {"error": f"API error ({response.status_code}): {error_detail[:200]}"}

        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return {"error": str(e)}

    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get information about a cloned voice."""
        if not self.is_available():
            return {"error": "ElevenLabs API key not configured"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{ELEVENLABS_API_URL}/voices/{voice_id}",
                    headers={'xi-api-key': self.api_key}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"API error: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    async def delete_voice(self, voice_id: str) -> bool:
        """Delete a cloned voice from ElevenLabs."""
        if not self.is_available():
            return False

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(
                    f"{ELEVENLABS_API_URL}/voices/{voice_id}",
                    headers={'xi-api-key': self.api_key}
                )
                return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to delete voice {voice_id}: {e}")
            return False


# Global instances
voice_recorder: Optional[VoiceRecorder] = None
voice_cloner: Optional[ElevenLabsVoiceCloner] = None


def get_voice_recorder() -> VoiceRecorder:
    """Get or create the global voice recorder instance."""
    global voice_recorder
    if voice_recorder is None:
        voice_recorder = VoiceRecorder()
    return voice_recorder


def get_voice_cloner() -> ElevenLabsVoiceCloner:
    """Get or create the global voice cloner instance."""
    global voice_cloner
    if voice_cloner is None:
        voice_cloner = ElevenLabsVoiceCloner()
    return voice_cloner


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

            logger.info(f"Audio saved to {temp_path}, size: {len(audio_data)} bytes")

            # Pre-convert MP3 to WAV with correct format using subprocess
            # Discord needs: 48kHz, stereo, 16-bit PCM
            import subprocess
            wav_path = temp_path.replace('.mp3', '.wav')

            convert_cmd = [
                'ffmpeg', '-y', '-i', temp_path,
                '-ar', '48000',  # 48kHz sample rate
                '-ac', '2',      # Stereo
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-f', 'wav',
                wav_path
            ]

            result = subprocess.run(convert_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return False

            logger.info(f"Converted to WAV: {wav_path}")

            # Use the converted WAV file - discord.py handles the rest
            audio_source = discord.FFmpegPCMAudio(wav_path)

            # Wrap in volume transformer for volume control
            audio_source = discord.PCMVolumeTransformer(audio_source, volume=2.0)

            logger.info(f"Playing audio in voice channel...")
            session.voice_client.play(
                audio_source,
                after=lambda e: self._cleanup_audio_files([temp_path, wav_path], e)
            )

            # Wait for playback to complete
            while session.voice_client.is_playing():
                await asyncio.sleep(0.1)

            session.is_speaking = False
            return True

        except Exception as e:
            import traceback
            logger.error(f"Error speaking: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
                "model_id": "eleven_turbo_v2",  # Updated: old models deprecated for free tier
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

    def _cleanup_audio_files(self, paths: list, error: Optional[Exception]):
        """Clean up multiple temp audio files after playback."""
        if error:
            logger.error(f"Audio playback error: {error}")
        for path in paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                logger.warning(f"Could not delete temp file {path}: {e}")

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

                # Session 494: Use gpt-5-mini (reasoning model)
                response = self.openai_client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    max_completion_tokens=2000  # Reasoning model needs more tokens
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

    async def test_beep(self, session: VoiceSession) -> bool:
        """Play a simple test beep to verify voice works."""
        import subprocess

        if not session.voice_client.is_connected():
            logger.warning("Not connected to voice channel")
            return False

        try:
            # Ensure opus is loaded
            ensure_opus_loaded()
            logger.info(f"Opus loaded: {discord.opus.is_loaded()}")

            # Generate a 2-second beep tone as MP3 (FFmpegOpusAudio works better with this)
            beep_path = '/tmp/discord_test_beep.mp3'
            result = subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi',
                '-i', 'sine=frequency=440:duration=3',
                '-ar', '48000', '-ac', '2',
                '-b:a', '128k',
                beep_path
            ], capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"FFmpeg beep generation failed: {result.stderr}")
                return False

            logger.info(f"Test beep generated at {beep_path}")

            # Use FFmpegOpusAudio - specifically designed for Discord
            audio_source = await discord.FFmpegOpusAudio.from_probe(beep_path)

            logger.info(f"Audio source created, playing...")
            session.voice_client.play(
                audio_source,
                after=lambda e: logger.info(f"Beep finished, error: {e}")
            )

            while session.voice_client.is_playing():
                await asyncio.sleep(0.1)

            logger.info("Beep playback complete")
            return True
        except Exception as e:
            import traceback
            logger.error(f"Test beep error: {e}")
            logger.error(traceback.format_exc())
            return False


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

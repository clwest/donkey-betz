"""
Audio Agent - Session 81
========================

Specialized agent for audio generation operations.
Maintains state of generated audio files and responds to agent queries.

Features:
- Text-to-speech generation with state tracking
- Text-to-sound generation with state tracking
- Query handlers for cross-agent communication
- Memory-based state management via shared memory system

Example Usage:
    audio_agent = AudioAgent(user=request.user)

    # Generate speech
    result = audio_agent.generate_speech(
        text="Welcome to our platform",
        voice="Rachel"
    )

    # Query most recent audio
    recent = audio_agent.get_most_recent_audio()
    # Returns: {'audio_url': 'https://...', 'type': 'speech', ...}
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from django.utils import timezone
from django.contrib.auth import get_user_model

from agents.models import UnifiedAgentTemplate, AgentExecution
from intelligence.shared_memory import AgentMemoryInterface
from intelligence.agent_query_protocol import query_protocol

logger = logging.getLogger(__name__)
User = get_user_model()


class AudioAgent:
    """
    Specialized agent for audio generation.
    Maintains state and responds to queries from other agents.
    """

    def __init__(self, user: Optional[User] = None):
        """
        Initialize Audio Agent.

        Args:
            user: User who initiated the agent (optional)
        """
        self.user = user
        self.agent_name = 'AudioAgent'

        # Initialize memory interface for state management
        self.memory = AgentMemoryInterface(agent_id='audio_agent')

        # Get or create agent template
        self.template = self._get_or_create_template()

        logger.info(f"🎵 Audio Agent initialized for user: {user.username if user else 'system'}")

    def _get_or_create_template(self) -> UnifiedAgentTemplate:
        """Get or create AudioAgent template in database"""
        try:
            agent = UnifiedAgentTemplate.objects.get(name=self.agent_name)
            logger.debug(f"Using existing AudioAgent template: {agent.id}")
            return agent

        except UnifiedAgentTemplate.DoesNotExist:
            # Create new AudioAgent template
            agent = UnifiedAgentTemplate.objects.create(
                name=self.agent_name,
                display_name='Audio Generation Agent',
                description='Specialized agent for audio generation including text-to-speech, sound effects, and voice operations',
                specialization='audio_generation',
                capabilities=[
                    'text_to_speech',
                    'text_to_sound',
                    'voice_dubbing',
                    'speech_to_speech',
                    'voice_isolation'
                ],
                routing_keywords=[
                    'audio', 'speech', 'sound', 'voice', 'music',
                    'voiceover', 'narration', 'effect', 'dubbing'
                ],
                system_prompt=(
                    "You are the Audio Generation Agent. You specialize in creating audio content "
                    "including speech, sound effects, and voice operations. You maintain state of "
                    "generated audio files and can provide them to other agents upon request."
                ),
                required_tools=['runway_ml_audio'],
                is_active=True,
                metadata={
                    'query_handlers': {},
                    'created_by': 'session_81',
                    'version': '1.0.0'
                }
            )

            logger.info(f"✅ Created new AudioAgent template: {agent.id}")

            # Register query handlers
            self._register_query_handlers(agent)

            return agent

    def _register_query_handlers(self, agent: UnifiedAgentTemplate):
        """Register query handlers for this agent"""
        # Register 'get_most_recent' handler
        query_protocol.register_query_handler(
            agent=agent,
            query_type='get_most_recent',
            handler_method='get_most_recent_audio',
            description='Returns the most recently generated audio file'
        )

        # Register 'get_by_task_id' handler
        query_protocol.register_query_handler(
            agent=agent,
            query_type='get_by_task_id',
            handler_method='get_audio_by_task_id',
            description='Returns audio file by task ID'
        )

        # Register 'get_all_recent' handler
        query_protocol.register_query_handler(
            agent=agent,
            query_type='get_all_recent',
            handler_method='get_all_recent_audio',
            description='Returns list of recent audio files'
        )

        logger.info("✅ Registered query handlers for AudioAgent")

    def generate_speech(
        self,
        text: str,
        voice: str = 'Rachel',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate speech from text using Runway ML text-to-speech.
        Stores result in agent memory for later retrieval.

        Args:
            text: Text to convert to speech
            voice: Voice to use (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave)
            **kwargs: Additional parameters

        Returns:
            Result dictionary with task_id, status, etc.
        """
        try:
            # Session 82: Switch to ElevenLabs for professional voice quality
            from content.elevenlabs_provider import elevenlabs_provider

            logger.info(f"🗣️ AudioAgent.generate_speech: voice={voice}, text={text[:50]}...")

            # Call ElevenLabs text-to-speech (professional quality)
            result = elevenlabs_provider.text_to_speech(
                text=text,
                voice=voice
            )

            if not result.get('success'):
                return result

            task_id = result.get('task_id')

            # Session 82: ElevenLabs returns audio immediately (synchronous)
            # Store in agent memory with completed audio_url
            audio_data = {
                'audio_url': result.get('audio_url'),  # ElevenLabs provides URL immediately
                'task_id': str(task_id) if task_id else None,  # Session 83: Convert UUID to string
                'type': 'speech',
                'text': text,
                'voice': voice,
                'status': result.get('status', 'completed'),  # ElevenLabs completes immediately
                'user_id': str(self.user.id) if self.user else None,  # Session 83: Convert UUID to string
                'created_at': timezone.now().isoformat()
            }

            # Store as most recent
            self.memory.remember('most_recent_audio', audio_data)

            # Also store by task_id for specific retrieval
            self.memory.remember(f'audio_task_{task_id}', audio_data)

            # Add to recent list
            self._add_to_recent_list(audio_data)

            logger.info(f"✅ AudioAgent stored audio state: task_id={task_id}")

            # Add parameters to result for frontend display (Session 82 fix)
            result['voice'] = voice
            result['text_preview'] = text[:100] if len(text) > 100 else text

            return result

        except Exception as e:
            logger.error(f"❌ AudioAgent.generate_speech failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def generate_sound_effect(
        self,
        description: str,
        duration: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate sound effect from text description.
        Stores result in agent memory for later retrieval.

        Args:
            description: Sound effect description
            duration: Duration in seconds (0.5 to 30)
            **kwargs: Additional parameters

        Returns:
            Result dictionary with task_id, status, etc.
        """
        try:
            # Session 82: Switch to ElevenLabs for professional sound quality
            from content.elevenlabs_provider import elevenlabs_provider

            logger.info(f"🔊 AudioAgent.generate_sound_effect: description={description}, duration={duration}s")

            # Call ElevenLabs text-to-sound (professional quality)
            result = elevenlabs_provider.text_to_sound(
                prompt=description,
                duration=duration
            )

            if not result.get('success'):
                return result

            task_id = result.get('task_id')

            # Session 82: ElevenLabs returns audio immediately (synchronous)
            # Store in agent memory with completed audio_url
            audio_data = {
                'audio_url': result.get('audio_url'),  # ElevenLabs provides URL immediately
                'task_id': str(task_id) if task_id else None,  # Session 83: Convert UUID to string
                'type': 'sound_effect',
                'description': description,
                'duration': duration,
                'status': result.get('status', 'completed'),  # ElevenLabs completes immediately
                'user_id': str(self.user.id) if self.user else None,  # Session 83: Convert UUID to string
                'created_at': timezone.now().isoformat()
            }

            # Store as most recent
            self.memory.remember('most_recent_audio', audio_data)

            # Also store by task_id
            self.memory.remember(f'audio_task_{task_id}', audio_data)

            # Add to recent list
            self._add_to_recent_list(audio_data)

            logger.info(f"✅ AudioAgent stored sound effect state: task_id={task_id}")

            # Add parameters to result for frontend display (Session 82 fix)
            result['description'] = description
            result['duration'] = duration

            return result

        except Exception as e:
            logger.error(f"❌ AudioAgent.generate_sound_effect failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def update_audio_status(
        self,
        task_id: str,
        audio_url: str,
        status: str = 'completed'
    ) -> bool:
        """
        Update audio status when generation completes.
        Called by polling function or webhook.

        Args:
            task_id: Task ID from initial generation
            audio_url: Final audio URL (CloudFront CDN)
            status: Status ('completed', 'failed')

        Returns:
            Success status
        """
        try:
            # Get audio data by task_id
            audio_data = self.memory.recall(f'audio_task_{task_id}')

            if not audio_data:
                logger.warning(f"⚠️ No audio data found for task_id: {task_id}")
                return False

            # Update audio data
            audio_data['audio_url'] = audio_url
            audio_data['status'] = status
            audio_data['completed_at'] = timezone.now().isoformat()

            # Update in memory
            self.memory.remember(f'audio_task_{task_id}', audio_data)

            # Update most_recent_audio if this was the most recent
            most_recent = self.memory.recall('most_recent_audio')
            if most_recent and most_recent.get('task_id') == task_id:
                self.memory.remember('most_recent_audio', audio_data)

            logger.info(f"✅ Updated audio status: {task_id} → {status}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update audio status: {str(e)}")
            return False

    def _add_to_recent_list(self, audio_data: Dict):
        """Add audio to recent list (keep last 10)"""
        try:
            recent_list = self.memory.recall('recent_audio_list') or []

            # Add new item at beginning
            recent_list.insert(0, audio_data)

            # Keep only last 10
            recent_list = recent_list[:10]

            # Store back
            self.memory.remember('recent_audio_list', recent_list)

        except Exception as e:
            logger.error(f"Failed to add to recent list: {str(e)}")

    # ===== QUERY HANDLERS =====

    def get_most_recent_audio(self) -> Optional[Dict]:
        """
        Query handler: Return most recently generated audio.
        Called by other agents via AgentQueryProtocol.

        Returns:
            Audio data dictionary or None
        """
        audio_data = self.memory.recall('most_recent_audio')

        if audio_data:
            logger.info(
                f"📤 AudioAgent responding to query: most_recent_audio "
                f"(type={audio_data.get('type')}, url={audio_data.get('audio_url')[:50] if audio_data.get('audio_url') else 'pending'}...)"
            )
        else:
            logger.info("📤 AudioAgent responding to query: most_recent_audio (no data)")

        return audio_data

    def get_audio_by_task_id(self, task_id: str) -> Optional[Dict]:
        """
        Query handler: Return audio by task ID.
        Called by other agents via AgentQueryProtocol.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Audio data dictionary or None
        """
        audio_data = self.memory.recall(f'audio_task_{task_id}')

        if audio_data:
            logger.info(f"📤 AudioAgent responding to query: audio_task_{task_id}")
        else:
            logger.info(f"📤 AudioAgent responding to query: audio_task_{task_id} (not found)")

        return audio_data

    def get_all_recent_audio(self, limit: int = 10) -> List[Dict]:
        """
        Query handler: Return list of recent audio files.
        Called by other agents via AgentQueryProtocol.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of audio data dictionaries
        """
        recent_list = self.memory.recall('recent_audio_list') or []
        recent_list = recent_list[:limit]

        logger.info(f"📤 AudioAgent responding to query: all_recent_audio ({len(recent_list)} items)")

        return recent_list


# ===== CONVENIENCE FUNCTIONS =====

def get_audio_agent(user: Optional[User] = None) -> AudioAgent:
    """
    Get AudioAgent instance.
    Convenience function for other modules.

    Args:
        user: User who initiated the agent

    Returns:
        AudioAgent instance
    """
    return AudioAgent(user=user)


def execute_audio_agent_method(
    method_name: str,
    parameters: Dict,
    user: Optional[User] = None
) -> Dict[str, Any]:
    """
    Execute AudioAgent method by name.
    Used for dynamic invocation.

    Args:
        method_name: Method to call (e.g., 'generate_speech')
        parameters: Method parameters
        user: User who initiated the request

    Returns:
        Method result
    """
    try:
        agent = get_audio_agent(user=user)

        # Get method
        method = getattr(agent, method_name, None)

        if not method:
            return {
                'success': False,
                'error': f'Method not found: {method_name}'
            }

        # Call method
        result = method(**parameters)

        return result

    except Exception as e:
        logger.error(f"Failed to execute AudioAgent method: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


__all__ = [
    'AudioAgent',
    'get_audio_agent',
    'execute_audio_agent_method'
]

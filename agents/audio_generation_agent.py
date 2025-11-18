"""
Audio Generation Agent - Session 128

Specialized agent for audio generation using ElevenLabs text-to-speech.
Handles standalone voice generation and video voiceovers.

Architecture:
    AI Assistant (detects intent) → Audio Generation Agent → Wrapper Views → ElevenLabs API
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.test import RequestFactory
import json

User = get_user_model()
logger = logging.getLogger(__name__)


class AudioGenerationAgent:
    """
    Specialized agent for audio generation operations.

    Responsibilities:
        - Generate standalone audio from text
        - Add voiceovers to existing videos
        - Handle ElevenLabs voice selection
        - Associate audio with projects
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Audio Generation Agent.

        Args:
            user: User requesting audio generation
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Audio Generation Agent"

    def execute(
        self,
        operation: str,
        text: str,
        voice: str = 'Rachel',
        video_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an audio generation operation.

        Args:
            operation: Type of operation ('generate_voice', 'add_voiceover')
            text: Text to convert to speech
            voice: Voice preset (Rachel, Drew, Clyde, Paul, Aria, etc.)
            video_id: Optional video ID for voiceover operation
            **kwargs: Operation-specific parameters

        Returns:
            Dict with success status and audio results
        """
        logger.info(f"🤖 {self.agent_name} starting {operation} workflow")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Voice: {voice}")
        logger.info(f"   Text: {text[:60]}...")

        try:
            # Route to appropriate operation
            if operation == 'generate_voice':
                result = self._generate_voice(text, voice)
            elif operation == 'add_voiceover':
                if not video_id:
                    return {
                        'success': False,
                        'error': 'video_id is required for add_voiceover operation'
                    }
                result = self._add_voiceover(video_id, text, voice)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }

            if result.get('success'):
                logger.info(f"✅ {self.agent_name} {operation} completed successfully")
            else:
                logger.error(f"❌ {self.agent_name} {operation} failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_voice(self, text: str, voice: str) -> Dict[str, Any]:
        """Generate standalone audio from text."""
        try:
            from core.views_video import generate_voice_view

            logger.info(f"🎤 Generating voice with {voice}...")

            factory = RequestFactory()
            data = {
                'text': text,
                'voice': voice
            }
            if self.project_id:
                data['project_id'] = self.project_id

            request = factory.post('/api/tool/generate-voice/',
                                  json.dumps(data),
                                  content_type='application/json')
            request.user = self.user

            response = generate_voice_view(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'audio_url': result.get('audio_url'),
                    'message': f"✅ Voice generated successfully using {voice} voice! Audio is ready to play or download."
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Voice generation failed')
                }

        except Exception as e:
            logger.error(f"❌ Generate voice operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to generate voice: {str(e)}"
            }

    def _add_voiceover(self, video_id: str, text: str, voice: str) -> Dict[str, Any]:
        """Add voiceover to existing video."""
        try:
            from core.views_video import add_voiceover_view

            logger.info(f"🎤 Adding voiceover to video {video_id}...")

            factory = RequestFactory()
            data = {
                'video_id': video_id,
                'text': text,
                'voice': voice
            }
            if self.project_id:
                data['project_id'] = self.project_id

            request = factory.post('/api/tool/add-voiceover/',
                                  json.dumps(data),
                                  content_type='application/json')
            request.user = self.user

            response = add_voiceover_view(request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'video_url': result.get('video_url'),
                    'message': f"✅ Voiceover added successfully! Video is ready with {voice} narration."
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Voiceover addition failed')
                }

        except Exception as e:
            logger.error(f"❌ Add voiceover operation error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to add voiceover: {str(e)}"
            }

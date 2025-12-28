"""
Audio Agent - Specialized for Audio Generation ONLY
====================================================

Session 268: Phase 2 - Creation Agents
Session 304: Learning Infrastructure Integration
Session 305: AudioHistory Integration

This agent creates audio. That's ALL it does.
It has NO access to image, video, 3D, or research tools.

Tools Available:
    - generate_voice: Text-to-speech using ElevenLabs
    - generate_sfx: Generate sound effects
    - add_voiceover: Add voiceover to existing video

Tools NOT Available (by design):
    - image generation
    - video generation
    - 3D generation
    - web search

Audio History:
    All generated audio is automatically saved to AudioHistory model.
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class AudioAgent(BaseAgent):
    """
    Agent specialized in audio generation. Cannot do anything else.

    This agent:
    1. Takes a task like "generate a voiceover for my script"
    2. Selects appropriate voice and settings
    3. Calls ElevenLabs API
    4. Returns the generated audio

    It CANNOT:
    - Generate images
    - Generate videos
    - Generate 3D models
    - Search the web
    """

    name = "AudioAgent"

    system_prompt = """You are AudioAgent, a specialist in creating audio content.

Your ONLY job is to generate audio based on the task given to you.
You have these tools:
- generate_voice: Convert text to speech using ElevenLabs voices
- generate_sfx: Generate sound effects
- add_voiceover: Add voiceover narration to an existing video

Available voices: Rachel, Antoni, Bella, Callum, Charlotte, Daniel, Domi, Elli, Emily, George, Matilda, Sam

When given a task:
1. Analyze what type of audio the user wants
2. For narration/speech, use generate_voice with appropriate voice
3. For sound effects, use generate_sfx
4. For adding audio to video, use add_voiceover

Voice selection tips:
- Rachel: Warm, professional female voice
- Antoni: Authoritative male voice
- Bella: Friendly, approachable female voice
- Daniel: Clear, neutral male voice

You CANNOT create images, videos, 3D models, or search the web. Just audio.
If asked to do something outside audio generation, politely explain you can only create audio."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_voice",
                "description": "Convert text to speech using ElevenLabs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to convert to speech"
                        },
                        "voice": {
                            "type": "string",
                            "description": "Voice to use for speech",
                            "enum": ["Rachel", "Antoni", "Bella", "Callum", "Charlotte",
                                     "Daniel", "Domi", "Elli", "Emily", "George", "Matilda", "Sam"],
                            "default": "Rachel"
                        },
                        "stability": {
                            "type": "number",
                            "description": "Voice stability (0.0-1.0)",
                            "default": 0.5
                        },
                        "similarity_boost": {
                            "type": "number",
                            "description": "Voice similarity boost (0.0-1.0)",
                            "default": 0.75
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_sfx",
                "description": "Generate sound effects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the sound effect to generate"
                        },
                        "duration": {
                            "type": "number",
                            "description": "Duration in seconds",
                            "default": 3.0
                        }
                    },
                    "required": ["description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_voiceover",
                "description": "Add voiceover narration to an existing video",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video to add voiceover to"
                        },
                        "text": {
                            "type": "string",
                            "description": "The voiceover script/text"
                        },
                        "voice": {
                            "type": "string",
                            "description": "Voice to use",
                            "enum": ["Rachel", "Antoni", "Bella", "Callum", "Charlotte",
                                     "Daniel", "Domi", "Elli", "Emily", "George", "Matilda", "Sam"],
                            "default": "Rachel"
                        },
                        "background_volume": {
                            "type": "number",
                            "description": "Volume of original video audio (0.0-1.0)",
                            "default": 0.3
                        }
                    },
                    "required": ["video_id", "text"]
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute audio generation based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("audio_generation", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing audio generation request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for audio operation",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=tool_result.get('message', '')[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    successful_calls = [tc for tc in tool_calls_made if tc['result'].get('success')]
                    if successful_calls:
                        result = AgentResult(
                            success=True,
                            message=f"Audio generated successfully",
                            data=successful_calls[0]['result'],
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # === Session 304: Learning Infrastructure ===
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=bool(spider_context),
                            scifi_context_used=bool(scifi_context)
                        )

                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="success",
                            importance=0.6
                        )

                        # Track contribution if we have an audio ID
                        audio_id = successful_calls[0]['result'].get('audio_id')
                        if audio_id:
                            self._track_contribution(
                                content_type='audio',
                                content_id=audio_id,
                                contribution_type='primary_creator',
                                contribution_score=1.0
                            )

                        # Share knowledge about voice/audio techniques
                        tool_used = successful_calls[0]['tool']
                        args = successful_calls[0].get('arguments', {})
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"Audio: {args.get('voice', 'default')} voice works well",
                            knowledge_value={
                                'tool': tool_used,
                                'voice': args.get('voice'),
                                'text_length': len(args.get('text', '')),
                                'success': True
                            },
                            confidence=0.8
                        )

                        return result
                    else:
                        result = AgentResult(
                            success=False,
                            error="Audio generation failed",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )

                        # Record failure for learning
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=bool(spider_context),
                            scifi_context_used=bool(scifi_context)
                        )

                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="failure",
                            importance=0.7
                        )

                        return result
                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"AudioAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call for audio generation."""

        if tool_name == "generate_voice":
            from core.views_image import _execute_generate_voice
            parameters = {
                'text': arguments.get('text', ''),
                'voice': arguments.get('voice', 'Rachel'),
                'stability': arguments.get('stability', 0.5),
                'similarity_boost': arguments.get('similarity_boost', 0.75),
            }
            return _execute_generate_voice(self.user, parameters, session=None)

        elif tool_name == "generate_sfx":
            # Sound effects generation - may need to be implemented
            return {
                'success': False,
                'error': 'Sound effects generation not yet implemented'
            }

        elif tool_name == "add_voiceover":
            from core.views_image import _execute_add_voiceover
            parameters = {
                'video_id': arguments.get('video_id'),
                'text': arguments.get('text', ''),
                'voice': arguments.get('voice', 'Rachel'),
                'background_volume': arguments.get('background_volume', 0.3),
            }
            return _execute_add_voiceover(self.user, parameters, session=None)

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. AudioAgent only supports audio tools."
            }


# Session 392: Factory function for backwards compatibility
def get_audio_agent(user=None) -> AudioAgent:
    """
    Get AudioAgent instance.

    Args:
        user: Optional user who initiated the agent

    Returns:
        AudioAgent instance
    """
    return AudioAgent(user=user)

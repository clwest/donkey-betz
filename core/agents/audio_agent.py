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

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_audio_prompt_with_ml(prompt_data: dict) -> dict:
    """Analyze audio prompts using ML models (Text) for voice/sound enhancement."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=prompt_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'audio_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML audio prompt analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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

    # Session 856: Content review configuration
    actionable_config = ActionableOutputConfig(
        actions=['approve', 'revise', 'reject'],
        payload_fields=['tool_used', 'voice', 'text', 'audio_id', 'duration']
    )

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
                # Handle simple diagnostic/identification queries
                task_lower = task.lower() if task else ''
                if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                    execution_time = int((time.time() - start_time) * 1000)
                    return AgentResult(
                        success=True,
                        message=f"I am {self.name}, a specialist in creating audio content. One capability: I generate text-to-speech voiceovers, sound effects, and audio narrations using ElevenLabs voices including Rachel, Antoni, Bella, Daniel, and more.",
                        data={'type': 'self_description', 'capabilities': ['voice_generation', 'sound_effects', 'voiceover']},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

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

                    # Session 840: Collect actual errors for better error reporting
                    successful_calls = [tc for tc in tool_calls_made if tc['result'].get('success')]
                    failed_calls = [tc for tc in tool_calls_made if not tc['result'].get('success')]
                    all_errors = [tc['result'].get('error', 'Unknown error') for tc in failed_calls]

                    if successful_calls:
                        # Session 856: Build descriptive message based on tool used
                        tool_used = successful_calls[0]['tool']
                        args = successful_calls[0].get('arguments', {})
                        tool_result = successful_calls[0]['result']
                        if tool_used == 'generate_voice':
                            voice = args.get('voice', 'Rachel')
                            text_preview = args.get('text', '')[:80]
                            descriptive_msg = f"Voice generated using {voice}: '{text_preview}...'"
                        elif tool_used == 'generate_sfx':
                            desc = args.get('description', '')[:80]
                            duration = args.get('duration', 3.0)
                            descriptive_msg = f"Sound effect generated ({duration}s): '{desc}'"
                        elif tool_used == 'add_voiceover':
                            voice = args.get('voice', 'Rachel')
                            video_id = args.get('video_id', 'unknown')
                            descriptive_msg = f"Voiceover added to video {video_id} using {voice} voice"
                        else:
                            descriptive_msg = f"Audio operation '{tool_used}' completed"

                        # Merge tool result with additional context
                        result_data = tool_result.copy() if isinstance(tool_result, dict) else {'result': tool_result}
                        result_data['tool_used'] = tool_used
                        result_data['voice'] = args.get('voice')
                        result_data['text'] = args.get('text', '')[:200]

                        result = AgentResult(
                            success=True,
                            message=descriptive_msg,
                            data=result_data,
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

                        # Session 1006: Persist output to Deliverable
                        # Session 1092: render with shared helper for gate passing.
                        self._save_to_deliverable(
                            title=f"Generated Audio: {task[:80]}",
                            content=self._render_agent_output_markdown(
                                task=task,
                                summary=result.message,
                                tool_calls=tool_calls_made,
                                extra={'tool_used': tool_used, 'voice': args.get('voice')},
                            ),
                            deliverable_type='audio',
                            category='Audio Generation',
                            tags=['audio', tool_used],
                            metadata={'task': task[:200], 'tool_used': tool_used, 'voice': args.get('voice')},
                        )

                        return result
                    else:
                        # Session 840: Include actual error details for better debugging
                        error_detail = "; ".join(all_errors) if all_errors else "No audio was generated"
                        result = AgentResult(
                            success=False,
                            error=f"Audio generation failed: {error_detail}",
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
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': 'audio_discussion',
                            'response': response_content,
                            'query': task,
                        },
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
            # Session 990: Import from views_audio (was views_image — wrong module)
            from core.views_audio import _execute_generate_voice
            parameters = {
                'text': arguments.get('text', ''),
                'voice': arguments.get('voice', 'Rachel'),
                'stability': arguments.get('stability', 0.5),
                'similarity_boost': arguments.get('similarity_boost', 0.75),
            }
            return _execute_generate_voice(self.user, parameters, session=None)

        elif tool_name == "generate_sfx":
            # Sound effects generation — ElevenLabs Sound Generation API
            from content.elevenlabs_provider import elevenlabs_provider

            prompt = arguments.get('description', arguments.get('text', ''))
            if not prompt:
                return {'success': False, 'error': 'description is required for sound effect generation'}

            duration = float(arguments.get('duration', 5.0))
            prompt_influence = float(arguments.get('prompt_influence', 0.3))

            result = elevenlabs_provider.text_to_sound(
                prompt=prompt,
                duration=duration,
                prompt_influence=prompt_influence,
            )
            if result.get('success'):
                return {
                    'success': True,
                    'audio_url': result.get('audio_url', ''),
                    'duration': duration,
                    'prompt': prompt,
                }
            return {
                'success': False,
                'error': result.get('error_message', 'Sound generation failed'),
            }

        elif tool_name == "add_voiceover":
            # Session 990: Import from views_audio (was views_image — wrong module)
            from core.views_audio import _execute_add_voiceover
            parameters = {
                'video_id': arguments.get('video_id'),
                'text': arguments.get('text', ''),
                'voice': arguments.get('voice', 'Rachel'),
                'background_volume': arguments.get('background_volume', 0.3),
            }
            return _execute_add_voiceover(self.user, parameters, session=None)

        return super()._execute_tool_call(tool_name, arguments)


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

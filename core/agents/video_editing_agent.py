"""
Video Editing Agent - Specialized for Video EDITING ONLY
=========================================================

Session 268: Phase 2 - Editing Agents
Session 304: Learning Infrastructure Integration

This agent EDITS existing videos. That's ALL it does.
It has NO access to creation, image, audio, or research tools.

Tools Available:
    - trim: Trim video to specific duration
    - add_text: Add text overlay to video
    - add_effects: Apply visual effects
    - extract_frame: Extract a frame from video
    - concatenate: Join multiple videos
    - speed_change: Change video playback speed

Tools NOT Available (by design):
    - video generation (that's VideoAgent)
    - image generation/editing
    - audio generation
    - web search
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_video_edit_with_ml(edit_data: dict) -> dict:
    """Analyze video edit requests using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=edit_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'edit_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML video edit analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class VideoEditingAgent(BaseAgent):
    """
    Agent specialized in editing existing videos. Cannot create new ones.

    This agent:
    1. Takes a task like "trim video to 5 seconds" or "add text to my video"
    2. Identifies the video to edit
    3. Applies the appropriate edit operation
    4. Returns the edited video

    It CANNOT:
    - Generate new videos (use VideoAgent)
    - Generate images
    - Generate audio
    - Search the web
    """

    name = "VideoEditingAgent"

    system_prompt = """You are VideoEditingAgent, a specialist in modifying existing videos.

Your ONLY job is to EDIT existing videos. You do NOT create new videos from scratch.
You have these tools:
- trim: Trim video to specific start/end times
- add_text: Add text overlay to video
- add_effects: Apply visual effects (filters, color grading)
- extract_frame: Extract a still image from a specific frame
- concatenate: Join multiple videos together
- speed_change: Speed up or slow down video

When given a task:
1. Identify which video the user wants to edit (by ID)
2. Determine which editing operation is needed
3. Apply the operation with appropriate parameters

Common operations:
- "Make it shorter" / "Cut to X seconds" → trim
- "Add title" / "Put text on it" → add_text
- "Make it cinematic" / "Apply vintage filter" → add_effects
- "Get a screenshot" / "Extract thumbnail" → extract_frame
- "Join these videos" → concatenate
- "Speed it up" / "Slow motion" → speed_change

You CANNOT create new videos, images, or audio. Only edit existing videos.
If asked to create something new, explain you can only edit existing videos."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "trim",
                "description": "Trim a video to specific start and end times",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video to trim"
                        },
                        "start_time": {
                            "type": "number",
                            "description": "Start time in seconds",
                            "default": 0
                        },
                        "end_time": {
                            "type": "number",
                            "description": "End time in seconds (or null for end of video)"
                        },
                        "duration": {
                            "type": "number",
                            "description": "Alternative: duration in seconds from start"
                        }
                    },
                    "required": ["video_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_text",
                "description": "Add text overlay to a video",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to display"
                        },
                        "position": {
                            "type": "string",
                            "description": "Position on screen",
                            "enum": ["top", "center", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"],
                            "default": "bottom"
                        },
                        "font_size": {
                            "type": "integer",
                            "description": "Font size in pixels",
                            "default": 48
                        },
                        "color": {
                            "type": "string",
                            "description": "Text color (hex or name)",
                            "default": "white"
                        },
                        "start_time": {
                            "type": "number",
                            "description": "When text appears (seconds)",
                            "default": 0
                        },
                        "end_time": {
                            "type": "number",
                            "description": "When text disappears (null for entire video)"
                        }
                    },
                    "required": ["video_id", "text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_effects",
                "description": "Apply visual effects to a video",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video"
                        },
                        "effect": {
                            "type": "string",
                            "description": "Effect to apply",
                            "enum": ["cinematic", "vintage", "vibrant", "noir", "warm", "cool", "blur", "sharpen"]
                        },
                        "intensity": {
                            "type": "number",
                            "description": "Effect intensity (0.0-1.0)",
                            "default": 0.5
                        }
                    },
                    "required": ["video_id", "effect"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extract_frame",
                "description": "Extract a still image from a video frame",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video"
                        },
                        "time": {
                            "type": "number",
                            "description": "Time in seconds to extract frame from",
                            "default": 0
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Image format",
                            "enum": ["png", "jpg"],
                            "default": "png"
                        }
                    },
                    "required": ["video_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "concatenate",
                "description": "Join multiple videos together in sequence",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of video IDs to join in order"
                        },
                        "transition": {
                            "type": "string",
                            "description": "Transition between clips",
                            "enum": ["none", "fade", "dissolve", "wipe"],
                            "default": "none"
                        },
                        "transition_duration": {
                            "type": "number",
                            "description": "Transition duration in seconds",
                            "default": 0.5
                        }
                    },
                    "required": ["video_ids"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "speed_change",
                "description": "Change video playback speed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video"
                        },
                        "speed_factor": {
                            "type": "number",
                            "description": "Speed multiplier (0.25 = 4x slower, 2.0 = 2x faster)",
                            "default": 1.0
                        },
                        "preserve_audio_pitch": {
                            "type": "boolean",
                            "description": "Keep original audio pitch when changing speed",
                            "default": True
                        }
                    },
                    "required": ["video_id", "speed_factor"]
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
        """Execute video editing based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("video_editing", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing video editing request",
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
                            reasoning=f"Selected {tool_name} for video editing",
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
                            message=f"Video edited successfully",
                            data=successful_calls[0]['result'],
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # === Session 304: Learning Infrastructure ===
                        self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                        self._create_execution_memory(result, task, "success", 0.6)
                        tool_used = successful_calls[0]['tool']
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"VideoEdit: {tool_used} works",
                            knowledge_value={'tool': tool_used, 'success': True},
                            confidence=0.8
                        )

                        return result
                    else:
                        result = AgentResult(
                            success=False,
                            error="Video editing failed",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )
                        self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                        self._create_execution_memory(result, task, "failure", 0.7)
                        return result
                else:
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': 'video_editing_discussion',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"VideoEditingAgent error: {e}")
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
        """Execute a tool call for video editing."""

        if tool_name == "trim":
            from core.views_image import _execute_edit_video
            parameters = {
                'video_id': arguments.get('video_id'),
                'operation': 'trim',
                'start_time': arguments.get('start_time', 0),
                'end_time': arguments.get('end_time'),
                'duration': arguments.get('duration'),
            }
            return _execute_edit_video(self.user, parameters)

        elif tool_name == "add_text":
            from core.views_image import _execute_add_text_to_video
            parameters = {
                'video_id': arguments.get('video_id'),
                'text': arguments.get('text'),
                'position': arguments.get('position', 'bottom'),
                'font_size': arguments.get('font_size', 48),
                'color': arguments.get('color', 'white'),
                'start_time': arguments.get('start_time', 0),
                'end_time': arguments.get('end_time'),
            }
            return _execute_add_text_to_video(self.user, parameters)

        elif tool_name == "add_effects":
            from core.views_image import _execute_edit_video
            parameters = {
                'video_id': arguments.get('video_id'),
                'operation': 'apply_effect',
                'effect': arguments.get('effect'),
                'intensity': arguments.get('intensity', 0.5),
            }
            return _execute_edit_video(self.user, parameters)

        elif tool_name == "extract_frame":
            from core.views_image import _execute_edit_video
            parameters = {
                'video_id': arguments.get('video_id'),
                'operation': 'extract_frame',
                'time': arguments.get('time', 0),
                'output_format': arguments.get('output_format', 'png'),
            }
            return _execute_edit_video(self.user, parameters)

        elif tool_name == "concatenate":
            from core.views_image import _execute_chain_videos
            parameters = {
                'video_ids': arguments.get('video_ids', []),
                'transition': arguments.get('transition', 'none'),
                'transition_duration': arguments.get('transition_duration', 0.5),
            }
            return _execute_chain_videos(self.user, parameters)

        elif tool_name == "speed_change":
            from core.views_image import _execute_edit_video
            parameters = {
                'video_id': arguments.get('video_id'),
                'operation': 'speed_change',
                'speed_factor': arguments.get('speed_factor', 1.0),
                'preserve_audio_pitch': arguments.get('preserve_audio_pitch', True),
            }
            return _execute_edit_video(self.user, parameters)

        elif tool_name == "delegate_to_specialist":
            # Session 833: Handle delegation properly
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )
        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. VideoEditingAgent only supports video editing tools."
            }

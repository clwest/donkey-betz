"""
Video Agent - Specialized for Video Generation ONLY
====================================================

Session 268: Phase 2 - Creation Agents
Session 304: Learning Infrastructure Integration

This agent creates videos. That's ALL it does.
It has NO access to image, audio, 3D, or research tools.

Tools Available:
    - generate_video: Text-to-video generation
    - animate_image: Image-to-video animation
    - extend_video: Extend video duration
    - chain_videos: Concatenate multiple videos

Tools NOT Available (by design):
    - image generation
    - audio generation
    - 3D generation
    - web search
    - any editing operations (that's VideoEditingAgent)
"""

import logging
import time
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class VideoAgent(BaseAgent):
    """
    Agent specialized in video generation. Cannot do anything else.

    This agent:
    1. Takes a task like "create an animation of a flying bird"
    2. Decides which video operation to use (text-to-video, image-to-video, etc.)
    3. Calls the appropriate Runway ML function
    4. Returns the video generation result (async - returns task_id)

    It CANNOT:
    - Generate images
    - Generate audio
    - Generate 3D models
    - Search the web
    - Edit existing videos (that's VideoEditingAgent)
    """

    name = "VideoAgent"

    system_prompt = """You are VideoAgent, a specialist in creating videos.

Your ONLY job is to generate videos based on the task given to you.
You have these tools:
- generate_video: Create video from text description
- animate_image: Animate an existing image into a video
- extend_video: Extend an existing video's duration
- chain_videos: Concatenate multiple videos together

When given a task:
1. Analyze what type of video the user wants
2. If they reference an existing image, use animate_image
3. If they want to extend or combine videos, use the appropriate tool
4. Otherwise, use generate_video for text-to-video

Video settings:
- Duration: 4, 6, or 8 seconds (Runway ML limits)
- Motion prompts should describe movement and camera motion

You CANNOT create images, audio, 3D models, or search the web. Just videos.
If asked to do something outside video generation, politely explain you can only create videos."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_video",
                "description": "Generate a video from a text prompt using Runway ML",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Detailed text description of the video. Include motion, camera movement, and scene details."
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds (4, 6, or 8)",
                            "default": 6,
                            "enum": [4, 6, 8]
                        }
                    },
                    "required": ["prompt"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "animate_image",
                "description": "Animate an existing image into a video (image-to-video)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "ID of the image to animate (UUID or sequential number)"
                        },
                        "motion_prompt": {
                            "type": "string",
                            "description": "Description of the motion/animation to apply",
                            "default": "smooth natural motion with subtle movement"
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds (4, 6, or 8)",
                            "default": 6,
                            "enum": [4, 6, 8]
                        }
                    },
                    "required": ["image_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extend_video",
                "description": "Extend an existing video's duration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "ID of the video to extend"
                        },
                        "extension_seconds": {
                            "type": "integer",
                            "description": "How many seconds to add (4, 6, or 8)",
                            "default": 4,
                            "enum": [4, 6, 8]
                        },
                        "motion_prompt": {
                            "type": "string",
                            "description": "Optional prompt describing continued motion"
                        }
                    },
                    "required": ["video_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "chain_videos",
                "description": "Concatenate multiple videos together",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of video IDs to concatenate in order"
                        },
                        "transition": {
                            "type": "string",
                            "description": "Transition type between clips",
                            "enum": ["none", "fade", "dissolve"],
                            "default": "none"
                        }
                    },
                    "required": ["video_ids"]
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
        """Execute video generation based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("video_generation", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing video generation request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                full_prompt = self._build_prompt(task, scifi_context, spider_context)
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for video operation",
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

                    # Check if any tool call succeeded
                    successful_calls = [tc for tc in tool_calls_made if tc['result'].get('success')]
                    if successful_calls:
                        result = AgentResult(
                            success=True,
                            message=f"Video operation started",
                            data={
                                'task_id': successful_calls[0]['result'].get('task_id'),
                                'status': 'processing',
                                'tool_used': successful_calls[0]['tool']
                            },
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

                        # Track contribution if we have a video ID
                        video_id = successful_calls[0]['result'].get('video_id')
                        if video_id:
                            self._track_contribution(
                                content_type='video',
                                content_id=video_id,
                                contribution_type='primary_creator',
                                contribution_score=1.0
                            )

                        # Share knowledge about video techniques
                        tool_used = successful_calls[0]['tool']
                        args = successful_calls[0].get('arguments', {})
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"Video: {tool_used} works for motion",
                            knowledge_value={
                                'tool': tool_used,
                                'prompt_pattern': args.get('prompt', args.get('motion_prompt', ''))[:100],
                                'duration': args.get('duration'),
                                'success': True
                            },
                            confidence=0.8
                        )

                        return result
                    else:
                        result = AgentResult(
                            success=False,
                            error="Video generation failed",
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
                logger.error(f"VideoAgent error: {e}")
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
        """Execute a tool call for video generation."""

        if tool_name == "generate_video":
            from core.views_image import _execute_generate_video
            parameters = {
                'prompt': arguments.get('prompt', ''),
                'duration': arguments.get('duration', 6),
            }
            return _execute_generate_video(self.user, parameters, session=None)

        elif tool_name == "animate_image":
            from core.views_image import _execute_generate_video
            parameters = {
                'operation': 'animate',
                'params': {
                    'image_id': arguments.get('image_id'),
                    'motion_prompt': arguments.get('motion_prompt', 'smooth natural motion'),
                    'duration': arguments.get('duration', 6),
                }
            }
            return _execute_generate_video(self.user, parameters, session=None)

        elif tool_name == "extend_video":
            # TODO: Implement video extension when available
            return {
                'success': False,
                'error': 'Video extension not yet implemented in clean architecture'
            }

        elif tool_name == "chain_videos":
            from core.views_image import _execute_chain_videos
            parameters = {
                'video_ids': arguments.get('video_ids', []),
                'transition': arguments.get('transition', 'none'),
            }
            return _execute_chain_videos(self.user, parameters)

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. VideoAgent only supports video tools."
            }


# Session 392: Factory function for backwards compatibility
def get_video_agent(user=None) -> VideoAgent:
    """
    Get VideoAgent instance.

    Args:
        user: Optional user who initiated the agent

    Returns:
        VideoAgent instance
    """
    return VideoAgent(user=user)

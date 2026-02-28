"""
Talking Character Agent - Animated talking-head videos from image + script
==========================================================================

Wraps TalkingCharacterPipeline to produce a single talking-head video in one
call: TTS (ElevenLabs) → image-to-video (Runway) → lip sync (Replicate).

Dispatched via studio_tool generate_talking_video action or directly through
AgentRouter.route("TalkingCharacterAgent", ...).
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class TalkingCharacterAgent(BaseAgent):
    """
    Agent that creates talking-head videos from a character image and script.

    Pipeline stages:
    1. Text-to-Speech (ElevenLabs) — generate audio from script
    2. Image-to-Video (Runway Gen-4 Turbo) — animate the character image
    3. Lip Sync (Replicate: LatentSync or Sync Labs) — match mouth to audio

    Cost per 10-second video: ~$0.60-1.00
    """

    name = "TalkingCharacterAgent"

    system_prompt = (
        "You are TalkingCharacterAgent, a specialist in creating talking-head videos. "
        "Given a character image and a text script, you produce an animated video where "
        "the character speaks the script with synchronised lip movements.\n\n"
        "Pipeline: TTS (ElevenLabs) → Image-to-Video (Runway) → Lip Sync (Replicate).\n\n"
        "Available voices: Rachel, Antoni, Bella, Callum, Charlotte, Daniel, Domi, "
        "Elli, Emily, George, Matilda, Sam.\n\n"
        "You CANNOT generate standalone images, audio-only, or edit existing videos. "
        "You only produce talking-head videos from image + script."
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_talking_video",
                "description": "Create a talking-head video from a character image and text script",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of the character image to animate",
                        },
                        "script": {
                            "type": "string",
                            "description": "Text script for the character to speak",
                        },
                        "voice": {
                            "type": "string",
                            "description": "ElevenLabs voice name",
                            "enum": [
                                "Rachel", "Antoni", "Bella", "Callum", "Charlotte",
                                "Daniel", "Domi", "Elli", "Emily", "George",
                                "Matilda", "Sam",
                            ],
                            "default": "Rachel",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds (5 or 10). Base animation length before looping.",
                            "enum": [5, 10],
                            "default": 10,
                        },
                        "sync_mode": {
                            "type": "string",
                            "description": "Lip sync mode: loop (repeats animation to match audio length), cut_off (truncates at video end), bounce (ping-pong loop)",
                            "enum": ["loop", "cut_off", "bounce"],
                            "default": "loop",
                        },
                        "lipsync_model": {
                            "type": "string",
                            "description": "Lip-sync model: auto (default), latentsync (cartoon), sync_labs (photorealistic)",
                            "enum": ["auto", "latentsync", "sync_labs"],
                            "default": "auto",
                        },
                        "mode": {
                            "type": "string",
                            "description": "Video mode: loop (repeats base animation, fast/cheap) or multi_clip (unique clips per segment, 3-6x cost but no visible loops)",
                            "enum": ["loop", "multi_clip"],
                            "default": "loop",
                        },
                        "color_grade": {
                            "type": "string",
                            "description": "Optional DaVinci Resolve color grade preset for post-processing",
                            "enum": [
                                "cinematic_warm", "cinematic_cool", "cyberpunk_neon",
                                "vintage_film", "moody_dark", "natural_vibrant",
                                "sunset_golden", "nordic_cool", "pastel_soft",
                            ],
                        },
                    },
                    "required": ["image_url", "script"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "estimate_cost",
                "description": "Estimate the cost for a talking-head video",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "Text script to estimate cost for",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Video duration in seconds",
                            "default": 10,
                        },
                    },
                    "required": ["script"],
                },
            },
        },
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
    ) -> AgentResult:
        """Execute talking character video generation."""
        start_time = time.time()

        with self.time_travel_session("talking_character_generation", task, input_data=context):
            try:
                # Handle identification queries
                task_lower = task.lower() if task else ''
                if any(kw in task_lower for kw in [
                    'state your name', 'who are you', 'your capability',
                    'what can you do', 'introduce yourself',
                ]):
                    return AgentResult(
                        success=True,
                        message=(
                            f"I am {self.name}. I create talking-head videos from a "
                            "character image and text script, combining TTS, animation, "
                            "and lip sync in a single pipeline."
                        ),
                        data={
                            'type': 'self_description',
                            'capabilities': ['talking_video', 'tts', 'lip_sync'],
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                    )

                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name,
                    )

                # Extract pipeline parameters from context
                image_url = context.get('image_url', '')
                script = context.get('script') or task
                voice = context.get('voice', 'Rachel')
                duration = int(context.get('duration', 10))
                sync_mode = context.get('sync_mode', 'loop')
                lipsync_model = context.get('lipsync_model', 'auto')
                mode = context.get('mode', 'loop')
                color_grade = context.get('color_grade')

                if not image_url:
                    return AgentResult(
                        success=False,
                        error="image_url is required — provide a URL to the character image to animate",
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                    )

                # Session 1075: Resolve file_path to actual URL if not already HTTP
                # PA media_tool may pass Cloudinary storage keys instead of URLs
                if not image_url.startswith('http'):
                    try:
                        from django.core.files.storage import default_storage
                        image_url = default_storage.url(image_url)
                        logger.info(f"Resolved image file_path to URL: {image_url[:80]}")
                    except Exception as e:
                        logger.warning(f"Could not resolve image_url via storage: {e}")

                self.record_decision(
                    decision_type="pipeline_start",
                    action="Starting talking character pipeline",
                    reasoning=f"Image: {image_url[:60]}, Voice: {voice}, Duration: {duration}s",
                    confidence=0.9,
                )

                # Lazy import to avoid heavy module-level loads
                from content.talking_character_pipeline import TalkingCharacterPipeline

                pipeline = TalkingCharacterPipeline(user=self.user)
                result = pipeline.generate_talking_video_sync(
                    image_url=image_url,
                    text=script,
                    voice=voice,
                    duration=duration,
                    sync_mode=sync_mode,
                    lipsync_model=lipsync_model,
                    color_grade=color_grade,
                    mode=mode,
                )

                execution_time = int((time.time() - start_time) * 1000)

                if result.success:
                    self.mark_decision_outcome(
                        success=True,
                        result_summary=f"Video ready: {result.final_video_url[:60]}",
                    )

                    data = {
                        'final_video_url': result.final_video_url,
                        'base_video_url': result.base_video_url,
                        'audio_url': result.audio_url,
                        'estimated_cost': result.estimated_cost,
                        'duration_seconds': result.duration_seconds,
                        'voice': voice,
                        'lipsync_model': lipsync_model,
                        'pipeline_status': result.status.value,
                        'pipeline_steps': {
                            'tts': {'status': 'ok', 'url': result.audio_url},
                            'base_video': {'status': 'ok', 'url': result.base_video_url},
                            'lipsync': {'status': 'ok', 'url': result.final_video_url},
                            'mode': mode,
                            'execution_time_ms': execution_time,
                        },
                    }

                    agent_result = AgentResult(
                        success=True,
                        message=(
                            f"Talking character video created ({duration}s, {voice} voice). "
                            f"Video: {result.final_video_url}"
                        ),
                        data=data,
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                    )

                    self._save_to_deliverable(
                        title=f"Talking Character Video: {script[:60]}",
                        content=agent_result.message,
                        deliverable_type='video',
                        category='Talking Character',
                        tags=['talking_character', 'video', 'tts', 'lip_sync'],
                        metadata={
                            'voice': voice,
                            'duration': duration,
                            'video_url': result.final_video_url,
                            'image_url': image_url,
                        },
                    )

                    return agent_result
                else:
                    self.mark_decision_outcome(
                        success=False,
                        result_summary=f"Failed at {result.failed_stage}: {result.error_message}",
                    )
                    return AgentResult(
                        success=False,
                        error=f"Pipeline failed at {result.failed_stage}: {result.error_message}",
                        data={
                            'pipeline_steps': {
                                'failed_stage': result.failed_stage,
                                'error': result.error_message,
                                'tts': {'status': 'ok' if result.audio_url else 'skipped', 'url': result.audio_url},
                                'base_video': {'status': 'ok' if result.base_video_url else 'skipped', 'url': result.base_video_url},
                                'mode': mode,
                                'execution_time_ms': execution_time,
                            },
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                    )

            except Exception as e:
                logger.error(f"TalkingCharacterAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        if tool_name == "generate_talking_video":
            from content.talking_character_pipeline import TalkingCharacterPipeline

            pipeline = TalkingCharacterPipeline(user=self.user)
            result = pipeline.generate_talking_video_sync(
                image_url=arguments.get('image_url', ''),
                text=arguments.get('script', ''),
                voice=arguments.get('voice', 'Rachel'),
                duration=arguments.get('duration', 10),
                sync_mode=arguments.get('sync_mode', 'loop'),
                lipsync_model=arguments.get('lipsync_model', 'auto'),
                color_grade=arguments.get('color_grade'),
                mode=arguments.get('mode', 'loop'),
            )
            return {
                'success': result.success,
                'final_video_url': result.final_video_url,
                'base_video_url': result.base_video_url,
                'audio_url': result.audio_url,
                'estimated_cost': result.estimated_cost,
                'error': result.error_message if not result.success else None,
            }

        if tool_name == "estimate_cost":
            from content.talking_character_pipeline import TalkingCharacterPipeline

            pipeline = TalkingCharacterPipeline(user=self.user)
            return pipeline.estimate_cost(
                text=arguments.get('script', ''),
                duration_seconds=arguments.get('duration', 10),
            )

        return super()._execute_tool_call(tool_name, arguments)


def get_talking_character_agent(user=None) -> TalkingCharacterAgent:
    """Get TalkingCharacterAgent instance."""
    return TalkingCharacterAgent(user=user)

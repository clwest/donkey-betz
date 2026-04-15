"""
Resolve Agent - Professional Video Rendering via DaVinci Resolve
================================================================

Session 478: DaVinci Resolve Full Utilization

This agent interfaces with the resolve_node FastAPI server to provide
professional-grade video rendering and color grading capabilities.

Key Features:
1. Professional video rendering via DaVinci Resolve
2. Trend-driven color grading (spider data from Dribbble, Behance, etc.)
3. Automatic grade selection based on creative trends
4. Learning loop for grade performance tracking
5. Broadcast-quality export options

Tools Available:
    - render_video: Send videos to Resolve for professional render
    - apply_color_grade: Apply color grading preset (auto or manual)
    - get_render_status: Check render job status
    - get_trending_grades: Get grades matching current spider trends

Tools NOT Available (by design):
    - video generation (that's VideoAgent)
    - video editing operations (that's VideoEditingAgent)
    - image/audio generation
"""

import os
import logging
import time
import requests
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_render_job_with_ml(render_data: dict) -> dict:
    """Analyze render job data using ML models (Text for render optimization)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=render_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'render_optimization': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML render analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class ResolveNodeClient:
    """
    HTTP client for the resolve_node FastAPI server.

    The resolve_node runs on port 5001 and provides DaVinci Resolve
    rendering capabilities via REST API.
    """

    def __init__(self):
        self.base_url = os.getenv("RESOLVE_NODE_URL", "http://localhost:5001")
        self.token = os.getenv("RENDER_NODE_TOKEN", "dev-token-change-in-production")
        self.timeout = 30  # seconds

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "X-Render-Token": self.token,
            "Content-Type": "application/json"
        }

    def health_check(self) -> Dict[str, Any]:
        """Check if resolve_node is running."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.json() if response.ok else {"status": "error"}
        except requests.RequestException as e:
            logger.warning(f"Resolve node health check failed: {e}")
            return {"status": "offline", "error": str(e)}

    def start_render(
        self,
        clip_paths: List[str],
        template: str = "default_mp4",
        timeline_name: Optional[str] = None,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a render job on the resolve_node.

        Args:
            clip_paths: List of video file paths to import and render
            template: Render template (default_mp4, high_quality)
            timeline_name: Optional timeline name
            webhook_url: Optional webhook for completion notification

        Returns:
            Dict with job_id and status
        """
        try:
            payload = {
                "clip_paths": clip_paths,
                "template": template,
            }
            if timeline_name:
                payload["timeline_name"] = timeline_name
            if webhook_url:
                payload["webhook_url"] = webhook_url

            response = requests.post(
                f"{self.base_url}/render/start",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )

            if response.ok:
                return {"success": True, **response.json()}
            else:
                return {
                    "success": False,
                    "error": f"Resolve node error: {response.status_code} - {response.text}"
                }

        except requests.RequestException as e:
            logger.error(f"Failed to start render: {e}")
            return {"success": False, "error": str(e)}

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a render job.

        Args:
            job_id: The job ID returned from start_render

        Returns:
            Dict with job status, progress, and output info
        """
        try:
            response = requests.get(
                f"{self.base_url}/render/status/{job_id}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.ok:
                return {"success": True, **response.json()}
            else:
                return {
                    "success": False,
                    "error": f"Status check failed: {response.status_code}"
                }

        except requests.RequestException as e:
            logger.error(f"Failed to get render status: {e}")
            return {"success": False, "error": str(e)}

    def get_result_url(self, job_id: str) -> str:
        """Get the download URL for a completed render."""
        return f"{self.base_url}/render/result/{job_id}"

    def list_jobs(self) -> Dict[str, Any]:
        """List all render jobs."""
        try:
            response = requests.get(
                f"{self.base_url}/jobs",
                headers=self.headers,
                timeout=self.timeout
            )
            return response.json() if response.ok else {"jobs": []}
        except requests.RequestException as e:
            logger.error(f"Failed to list jobs: {e}")
            return {"jobs": [], "error": str(e)}


class ResolveAgent(BaseAgent):
    """
    Agent specialized in professional video rendering via DaVinci Resolve.

    This agent:
    1. Takes tasks like "render this video professionally" or "apply cinematic grading"
    2. Uses spider trends to automatically select the best color grade
    3. Sends rendering jobs to the resolve_node server
    4. Tracks outcomes for the learning loop

    It CANNOT:
    - Generate videos (that's VideoAgent)
    - Edit videos directly (that's VideoEditingAgent)
    - Generate images or audio
    """

    name = "ResolveAgent"

    system_prompt = """You are ResolveAgent, a specialist in professional video rendering and color grading.

Your ONLY job is to render videos professionally using DaVinci Resolve and apply color grading.

You have these tools:
- render_video: Send videos to DaVinci Resolve for professional-grade rendering
- apply_color_grade: Apply a color grading preset to a video (can be automatic based on trends)
- get_render_status: Check the status of a render job
- get_trending_grades: See which color grades match current creative trends

When given a task:
1. Analyze what type of rendering/grading the user wants
2. For automatic grading, check current trends with get_trending_grades
3. Start the render with appropriate template and color grade
4. Return the job ID for status tracking

Available color grades:
- cinematic_warm: Orange/teal Hollywood look
- cinematic_cool: Teal sci-fi look
- cyberpunk_neon: High contrast neon colors
- vintage_film: Nostalgic film grain
- nordic_cool: Clean Scandinavian aesthetic
- sunset_golden: Golden hour warmth
- moody_dark: Dark and dramatic
- natural_vibrant: Enhanced natural colors
- pastel_soft: Gentle pastel tones
- broadcast_standard: TV broadcast-safe
- corporate_clean: Professional business look

Render templates:
- default_mp4: Standard 1080p H.264
- high_quality: Enhanced quality with multi-pass encoding

You CANNOT create videos, edit timelines, or generate images/audio. Just professional rendering and grading.
If asked to do something outside your scope, politely explain you can only handle professional rendering."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "render_video",
                "description": "Send video(s) to DaVinci Resolve for professional rendering",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of video IDs to render"
                        },
                        "template": {
                            "type": "string",
                            "description": "Render template",
                            "enum": ["default_mp4", "high_quality"],
                            "default": "default_mp4"
                        },
                        "color_grade": {
                            "type": "string",
                            "description": "Color grade preset to apply, or 'auto' for trend-based selection",
                            "default": "auto"
                        }
                    },
                    "required": ["video_ids"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "apply_color_grade",
                "description": "Apply a color grading preset to a video",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "video_id": {
                            "type": "string",
                            "description": "Video ID to color grade"
                        },
                        "grade": {
                            "type": "string",
                            "description": "Color grade preset name, or 'auto' for automatic trend-based selection",
                            "default": "auto"
                        }
                    },
                    "required": ["video_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_render_status",
                "description": "Check the status of a render job",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "The render job ID to check"
                        }
                    },
                    "required": ["job_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_trending_grades",
                "description": "Get color grades that match current creative trends from Dribbble, Behance, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of matching grades to return",
                            "default": 3
                        }
                    }
                }
            }
        }
    ]

    # Session 856: Mission Control configuration for human review
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='insight',
        default_urgency='medium',
        min_confidence=0.0,
        actions=[
            {'id': 'approve', 'label': 'Render', 'style': 'primary', 'description': 'Start the render'},
            {'id': 'review', 'label': 'Review Settings', 'style': 'secondary', 'description': 'Check render settings'},
            {'id': 'dismiss', 'label': 'Cancel', 'style': 'danger', 'description': 'Cancel this operation'},
        ],
        # Include fields that DecisionDetailModal can render
        payload_fields=['recommended_grade', 'recommendations', 'trending_styles', 'template', 'job_id', 'progress', 'task'],
        max_items_per_hour=10
    )

    def __init__(self, user=None):
        super().__init__(user=user)
        self._resolve_client = None
        self._spider_service = None

    @property
    def resolve_client(self) -> ResolveNodeClient:
        """Lazy-load the resolve_node HTTP client."""
        if self._resolve_client is None:
            self._resolve_client = ResolveNodeClient()
        return self._resolve_client

    @property
    def spider_service(self):
        """Lazy-load SpiderIntelligenceService for trend data."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._spider_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
        return self._spider_service

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute professional rendering based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("resolve_render", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing professional rendering request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # Build prompt with context
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for rendering operation",
                            confidence=0.95
                        )

                        # Pass spider_context for auto grade selection
                        tool_result = self._execute_tool_call(
                            tool_name,
                            arguments,
                            spider_context=spider_context
                        )

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
                        # Session 856: Build meaningful message based on tool used
                        first_call = successful_calls[0]
                        tool_used = first_call['tool']
                        tool_result = first_call['result']

                        # Build descriptive message
                        if tool_used == 'get_trending_grades':
                            recommended = tool_result.get('recommended_grade', 'unknown')
                            recommendations = tool_result.get('recommendations', [])
                            trending_styles = tool_result.get('trending_styles', [])
                            message = f"Trending color grades analysis complete. "
                            message += f"Top recommendation: {recommended}. "
                            if recommendations:
                                other_grades = [r['preset'] for r in recommendations[:3] if r['preset'] != recommended]
                                if other_grades:
                                    message += f"Also trending: {', '.join(other_grades)}. "
                            if trending_styles:
                                message += f"Based on trends: {', '.join(trending_styles[:3])}."
                        elif tool_used == 'render_video':
                            job_id = tool_result.get('job_id', 'unknown')
                            template = tool_result.get('template', 'default')
                            color_grade = tool_result.get('color_grade', 'auto')
                            message = f"Render job started (ID: {job_id[:8] if job_id else 'pending'}). "
                            message += f"Using {template} template with {color_grade} color grading."
                        elif tool_used == 'apply_color_grade':
                            grade = tool_result.get('color_grade', 'unknown')
                            desc = tool_result.get('grade_description', '')
                            message = f"Color grading with '{grade}' preset started. "
                            if desc:
                                message += f"Effect: {desc}"
                        elif tool_used == 'get_render_status':
                            status = tool_result.get('status', 'unknown')
                            progress = tool_result.get('progress', 0)
                            message = f"Render status: {status} ({progress:.0f}% complete)."
                            if tool_result.get('download_url'):
                                message += " Video ready for download."
                        else:
                            message = tool_result.get('message', 'Resolve operation completed.')

                        result = AgentResult(
                            success=True,
                            message=message,
                            data={
                                'job_id': tool_result.get('job_id'),
                                'status': tool_result.get('status', 'processing'),
                                'color_grade': tool_result.get('color_grade'),
                                'tool_used': tool_used,
                                # Session 856: Include human-readable details
                                'task': task[:200],
                                'recommendations': tool_result.get('recommendations', []),
                                'trending_styles': tool_result.get('trending_styles', []),
                                'recommended_grade': tool_result.get('recommended_grade'),
                                'template': tool_result.get('template'),
                                'progress': tool_result.get('progress'),
                                'download_url': tool_result.get('download_url'),
                            },
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made
                        )

                        # === Learning Infrastructure ===
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
                            importance=0.7
                        )

                        # Share knowledge about successful grades
                        color_grade = successful_calls[0]['result'].get('color_grade')
                        if color_grade:
                            self._share_knowledge(
                                knowledge_type='technique',
                                title=f"Resolve: {color_grade} grade effective",
                                knowledge_value={
                                    'tool': successful_calls[0]['tool'],
                                    'color_grade': color_grade,
                                    'spider_trends': spider_context.get('creative_trends', {}),
                                    'success': True
                                },
                                confidence=0.8
                            )

                        return result
                    else:
                        # All tool calls failed
                        error_msg = tool_calls_made[0]['result'].get('error', 'Unknown error') if tool_calls_made else 'No tools called'
                        result = AgentResult(
                            success=False,
                            error=f"Resolve operation failed: {error_msg}",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )

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
                    # Conversational response (no tool call)
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': 'rendering_discussion',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"ResolveAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        spider_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a tool call for Resolve operations."""

        if tool_name == "render_video":
            return self._render_video(
                video_ids=arguments.get('video_ids', []),
                template=arguments.get('template', 'default_mp4'),
                color_grade=arguments.get('color_grade', 'auto'),
                spider_context=spider_context
            )

        elif tool_name == "apply_color_grade":
            return self._apply_color_grade(
                video_id=arguments.get('video_id'),
                grade=arguments.get('grade', 'auto'),
                spider_context=spider_context
            )

        elif tool_name == "get_render_status":
            return self._get_render_status(arguments.get('job_id'))

        elif tool_name == "get_trending_grades":
            return self._get_trending_grades(
                limit=arguments.get('limit', 3),
                spider_context=spider_context
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _render_video(
        self,
        video_ids: List[str],
        template: str,
        color_grade: str,
        spider_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Render video(s) with DaVinci Resolve.

        If color_grade is 'auto', uses spider trends to select the best grade.
        """
        try:
            # Auto-select color grade based on trends
            if color_grade == 'auto':
                color_grade = self._get_auto_grade(spider_context)
                logger.info(f"Auto-selected color grade: {color_grade}")

            # Get video file paths from IDs
            video_paths = self._resolve_video_paths(video_ids)
            if not video_paths:
                return {
                    'success': False,
                    'error': f"Could not resolve video paths for IDs: {video_ids}"
                }

            # Check if resolve_node is healthy
            health = self.resolve_client.health_check()
            if health.get('status') == 'offline':
                return {
                    'success': False,
                    'error': "DaVinci Resolve render node is offline. Please start it with: cd resolve_node && python app.py"
                }

            # Note: color_grade parameter available when resolve_node supports grading
            result = self.resolve_client.start_render(
                clip_paths=video_paths,
                template=template
            )

            if result.get('success'):
                return {
                    'success': True,
                    'job_id': result.get('job_id'),
                    'status': result.get('status', 'queued'),
                    'template': template,
                    'color_grade': color_grade,
                    'message': f"Render started with {template} template and {color_grade} grade"
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Render video failed: {e}")
            return {'success': False, 'error': str(e)}

    def _apply_color_grade(
        self,
        video_id: str,
        grade: str,
        spider_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply color grading to a video.

        If grade is 'auto', uses spider trends to select the best grade.
        """
        try:
            # Auto-select grade based on trends
            if grade == 'auto':
                grade = self._get_auto_grade(spider_context)
                logger.info(f"Auto-selected color grade: {grade}")

            # Validate grade exists
            from resolve_node.color_grades import get_preset
            preset = get_preset(grade)
            if not preset:
                from resolve_node.color_grades import get_all_presets
                return {
                    'success': False,
                    'error': f"Unknown grade '{grade}'. Available: {', '.join(get_all_presets())}"
                }

            # Get video path
            video_paths = self._resolve_video_paths([video_id])
            if not video_paths:
                return {
                    'success': False,
                    'error': f"Could not find video: {video_id}"
                }

            # Start render with grading
            result = self.resolve_client.start_render(
                clip_paths=video_paths,
                template="high_quality"  # Use high quality for color grading
            )

            if result.get('success'):
                return {
                    'success': True,
                    'job_id': result.get('job_id'),
                    'status': result.get('status', 'queued'),
                    'color_grade': grade,
                    'grade_description': preset.get('description', ''),
                    'message': f"Color grading with {grade} started"
                }
            else:
                return result

        except Exception as e:
            logger.error(f"Apply color grade failed: {e}")
            return {'success': False, 'error': str(e)}

    def _get_render_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of a render job."""
        if not job_id:
            return {'success': False, 'error': 'No job_id provided'}

        result = self.resolve_client.get_status(job_id)

        if result.get('success'):
            status = result.get('status', 'unknown')
            progress = result.get('progress', 0)

            return {
                'success': True,
                'job_id': job_id,
                'status': status,
                'progress': progress,
                'output_file': result.get('output_file'),
                'download_url': self.resolve_client.get_result_url(job_id) if status == 'done' else None,
                'message': f"Job {job_id}: {status} ({progress:.0f}%)"
            }
        else:
            return result

    def _get_trending_grades(
        self,
        limit: int = 3,
        spider_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get color grades matching current creative trends."""
        try:
            from resolve_node.color_grades import (
                COLOR_GRADE_PRESETS,
                match_grade_to_trends,
                describe_preset
            )

            # Get fresh spider trends if not provided
            if not spider_context or 'creative_trends' not in spider_context:
                if self.spider_service:
                    creative_trends = self.spider_service.get_creative_trends(hours=48)
                else:
                    creative_trends = {}
            else:
                creative_trends = spider_context.get('creative_trends', {})

            # Get best match
            best_match = match_grade_to_trends(creative_trends)

            # Score all presets
            trending_styles = []
            trending_colors = []

            if creative_trends:
                for item in creative_trends.get('trending_styles', []):
                    if isinstance(item, dict):
                        trending_styles.append(item.get('style', '').lower())
                    else:
                        trending_styles.append(str(item).lower())

                for item in creative_trends.get('trending_colors', []):
                    if isinstance(item, dict):
                        trending_colors.append(item.get('palette', '').lower())
                    else:
                        trending_colors.append(str(item).lower())

            # Build recommendations
            recommendations = []
            for preset_name, preset_config in COLOR_GRADE_PRESETS.items():
                score = 0
                for style in preset_config.get('spider_styles', []):
                    if style.lower() in trending_styles:
                        score += 2
                for color in preset_config.get('spider_colors', []):
                    if color.lower() in trending_colors:
                        score += 1.5

                if score > 0:
                    recommendations.append({
                        'preset': preset_name,
                        'score': score,
                        'description': preset_config.get('description', ''),
                        'use_case': preset_config.get('use_case', '')
                    })

            # Sort by score and limit
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            recommendations = recommendations[:limit]

            return {
                'success': True,
                'recommended_grade': best_match,
                'recommendations': recommendations,
                'trending_styles': trending_styles[:5],
                'trending_colors': trending_colors[:5],
                'message': f"Top recommendation: {best_match} - {describe_preset(best_match)}"
            }

        except Exception as e:
            logger.error(f"Get trending grades failed: {e}")
            return {'success': False, 'error': str(e)}

    def _get_auto_grade(self, spider_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Automatically select the best color grade based on spider trends
        and learning loop performance data.
        """
        try:
            from resolve_node.color_grades import match_grade_to_trends

            # Get creative trends
            creative_trends = {}
            if spider_context and 'creative_trends' in spider_context:
                creative_trends = spider_context['creative_trends']
            elif self.spider_service:
                creative_trends = self.spider_service.get_creative_trends(hours=48)

            # Check learning service for historical performance
            try:
                from core.services.resolve_learning import ResolveLearningService
                learning_service = ResolveLearningService(user=self.user)
                learned_grade = learning_service.get_best_grade_for_trends(creative_trends)
                if learned_grade:
                    logger.info(f"Learning service recommended: {learned_grade}")
                    return learned_grade
            except ImportError:
                pass  # Learning service not yet implemented

            # Fall back to trend matching
            return match_grade_to_trends(creative_trends)

        except Exception as e:
            logger.warning(f"Auto grade selection failed: {e}, using default")
            return "natural_vibrant"

    def _resolve_video_paths(self, video_ids: List[str]) -> List[str]:
        """
        Resolve video IDs to file paths.

        Supports multiple ID formats:
        1. R1, R2, R3... - Rescued videos by index
        2. #1, #2... or 1, 2... - Database videos by index
        3. UUID (with or without .mp4 extension)
        4. Filename from rescued_videos directory
        """
        from django.conf import settings
        from pathlib import Path
        import re

        paths = []
        media_root = Path(settings.MEDIA_ROOT)
        rescued_dir = Path(settings.BASE_DIR) / 'media' / 'rescued_videos'

        # Cache rescued video list for R1, R2 lookups
        rescued_files = []
        if rescued_dir.exists():
            rescued_files = sorted(rescued_dir.glob('*.mp4'))

        try:
            from content.models import VideoHistory

            for raw_id in video_ids:
                video_path = None
                video_id = raw_id.strip()

                # Strategy 0: R1, R2, R3... format for rescued videos
                r_match = re.match(r'^[Rr](\d+)$', video_id)
                if r_match:
                    idx = int(r_match.group(1)) - 1  # R1 = index 0
                    if 0 <= idx < len(rescued_files):
                        rescued_path = rescued_files[idx]
                        paths.append(str(rescued_path))
                        logger.info(f"Resolved '{raw_id}' to rescued video R{idx+1}: {rescued_path}")
                        continue
                    else:
                        logger.warning(f"Rescued video index out of range: {raw_id} (have {len(rescued_files)} videos)")
                        continue

                # Strip # prefix and file extensions
                video_id = video_id.lstrip('#')
                video_id = re.sub(r'\.(mp4|mov|avi|mkv|webm)$', '', video_id, flags=re.IGNORECASE)

                # Strategy 1: Check rescued_videos directory by filename
                rescued_path = rescued_dir / f"{video_id}.mp4"
                if rescued_path.exists():
                    paths.append(str(rescued_path))
                    logger.info(f"Resolved '{raw_id}' to rescued video: {rescued_path}")
                    continue

                # Strategy 2: Try as user-friendly sequential number
                if video_id.isdigit():
                    try:
                        idx = int(video_id) - 1  # 1-indexed for users
                        user_videos = VideoHistory.objects.filter(
                            status='completed'
                        ).order_by('-created_at')  # Most recent first
                        if 0 <= idx < user_videos.count():
                            video = user_videos[idx]
                            video_path = self._get_video_file_path(video, media_root)
                            if video_path:
                                paths.append(video_path)
                                logger.info(f"Resolved #{video_id} to video: {video_path}")
                                continue
                    except (ValueError, IndexError):
                        pass

                # Strategy 3: Try as UUID
                try:
                    video = VideoHistory.objects.get(id=video_id)
                    video_path = self._get_video_file_path(video, media_root)
                    if video_path:
                        paths.append(video_path)
                        logger.info(f"Resolved UUID '{video_id}' to: {video_path}")
                        continue
                except (VideoHistory.DoesNotExist, ValueError):
                    pass

                # Strategy 4: Search by partial UUID match
                try:
                    videos = VideoHistory.objects.filter(id__startswith=video_id)
                    if videos.exists():
                        video = videos.first()
                        video_path = self._get_video_file_path(video, media_root)
                        if video_path:
                            paths.append(video_path)
                            logger.info(f"Resolved partial UUID '{video_id}' to: {video_path}")
                            continue
                except Exception as _e:
                    logger.warning(
                        "resolve_agent._resolve_video_paths: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                logger.warning(f"Could not resolve video ID: {raw_id}")

        except Exception as e:
            logger.error(f"Failed to resolve video paths: {e}")

        return paths

    def _get_video_file_path(self, video, media_root: 'Path') -> Optional[str]:
        """Extract actual file path from VideoHistory record."""
        from pathlib import Path

        # Try video_file first
        if video.video_file:
            video_path = media_root / str(video.video_file)
            if video_path.exists():
                return str(video_path)

        # Try video_url (local /media/ paths)
        if hasattr(video, 'video_url') and video.video_url:
            url = video.video_url
            # Handle local media URLs
            if url.startswith('/media/'):
                relative_path = url[7:]  # Remove '/media/'
                video_path = media_root / relative_path
                if video_path.exists():
                    return str(video_path)
            # Handle full local paths
            elif url.startswith('/'):
                video_path = Path(url)
                if video_path.exists():
                    return str(video_path)

        return None


# Factory function for backwards compatibility
def get_resolve_agent(user=None) -> ResolveAgent:
    """
    Get ResolveAgent instance.

    Args:
        user: Optional user who initiated the agent

    Returns:
        ResolveAgent instance
    """
    return ResolveAgent(user=user)

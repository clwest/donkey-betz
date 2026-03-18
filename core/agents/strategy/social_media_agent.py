"""
Social Media Agent - Clean Architecture
========================================

Session 280: Phase 2 - Agent Architecture Unification

This agent specializes in platform-specific content optimization, knowing
optimal dimensions, best practices, and posting strategies for each platform.

Tools Available:
    - get_platform_specs: Get specifications for a platform
    - recommend_format: Recommend content format for a platform
    - get_posting_schedule: Get optimal posting times

Usage:
    from core.agents.strategy import SocialMediaAgent

    agent = SocialMediaAgent(user=request.user)
    result = agent.execute(
        task="What's the best format for Instagram?",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_social_content_with_ml(content_data: dict) -> dict:
    """Analyze social media content using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for content analysis
        result = router.auto_route(
            data=content_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'content_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML social content analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class SocialMediaAgent(BaseAgent):
    """
    Agent specialized in social media content strategy.

    This agent:
    1. Knows platform specifications (sizes, limits)
    2. Recommends content formats for each platform
    3. Suggests optimal posting times

    It CANNOT:
    - Generate images, videos, or audio
    - Post to social media
    """

    name = "SocialMediaAgent"
    create_deliverable_on_schedule = False  # Session 1077: scheduled outputs go to AgentExecution only

    system_prompt = """You are SocialMediaAgent, a specialist in social media content strategy.

Your job is to help users optimize their content for each social platform by knowing
the best dimensions, formats, and posting strategies.

When given a task:
1. Identify the target platform(s)
2. Recommend optimal content formats and dimensions
3. Suggest best practices for the platform
4. Provide posting time recommendations

Platform specifications:
- Instagram Post: 1080x1080 (square), up to 30 hashtags
- Instagram Story: 1080x1920 (9:16 vertical)
- Instagram Reel: 1080x1920 (9:16 vertical), up to 90 seconds
- Facebook Post: 1200x630 (1.91:1 landscape)
- Twitter/X: 1600x900 (16:9)
- LinkedIn: 1200x627 (1.91:1)
- TikTok: 1080x1920 (9:16 vertical)
- YouTube Thumbnail: 1280x720 (16:9)
- Pinterest Pin: 1000x1500 (2:3 vertical)

Best practices:
- Instagram: High contrast, vibrant colors, 11 hashtags optimal
- Twitter: Bold text, meme-friendly, 2 hashtags max
- LinkedIn: Professional, data-driven, thought leadership
- TikTok: Trendy, authentic, fast hooks
- YouTube: Faces with expressions, curiosity gap, 3-5 words text

You CANNOT create content - just provide platform strategy."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_platform_specs",
                "description": "Get specifications for a social media platform",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "The platform to get specs for",
                            "enum": ["instagram_post", "instagram_story", "instagram_reel",
                                     "facebook_post", "twitter_post", "linkedin_post",
                                     "tiktok_post", "youtube_thumbnail", "pinterest_pin"]
                        }
                    },
                    "required": ["platform"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recommend_format",
                "description": "Recommend content format for a platform and goal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Target platform"
                        },
                        "goal": {
                            "type": "string",
                            "description": "Content goal",
                            "enum": ["engagement", "awareness", "sales", "education", "entertainment"]
                        }
                    },
                    "required": ["platform"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_posting_schedule",
                "description": "Get optimal posting times for a platform",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "Target platform"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "User's timezone",
                            "default": "UTC"
                        }
                    },
                    "required": ["platform"]
                }
            }
        }
    ]

    # Platform specifications
    PLATFORM_SPECS = {
        'instagram_post': {
            'name': 'Instagram Post',
            'size': '1080x1080',
            'aspect_ratio': '1:1',
            'max_hashtags': 30,
            'optimal_hashtags': 11,
            'caption_limit': 2200,
            'best_times': ['9:00', '11:00', '14:00', '17:00'],
            'style_tips': ['High contrast', 'Vibrant colors', 'Clean composition'],
            'content_types': ['carousel', 'single image', 'quote graphic']
        },
        'instagram_story': {
            'name': 'Instagram Story',
            'size': '1080x1920',
            'aspect_ratio': '9:16',
            'duration': '15 seconds max per story',
            'style_tips': ['Vertical orientation', 'Bold text', 'Interactive elements'],
            'content_types': ['behind the scenes', 'polls', 'announcements']
        },
        'instagram_reel': {
            'name': 'Instagram Reel',
            'size': '1080x1920',
            'aspect_ratio': '9:16',
            'duration': '90 seconds max',
            'style_tips': ['Hook in first 3 seconds', 'Trending audio', 'Fast-paced'],
            'content_types': ['tutorials', 'transformations', 'trends']
        },
        'facebook_post': {
            'name': 'Facebook Post',
            'size': '1200x630',
            'aspect_ratio': '1.91:1',
            'caption_limit': 63206,
            'best_times': ['9:00', '13:00', '16:00'],
            'style_tips': ['Less saturated than Instagram', 'Informative', 'Shareable'],
            'content_types': ['link posts', 'photo albums', 'events']
        },
        'twitter_post': {
            'name': 'Twitter/X Post',
            'size': '1600x900',
            'aspect_ratio': '16:9',
            'caption_limit': 280,
            'max_hashtags': 2,
            'best_times': ['8:00', '12:00', '17:00'],
            'style_tips': ['High contrast text', 'Bold statements', 'Meme-friendly'],
            'content_types': ['threads', 'quotes', 'infographics']
        },
        'linkedin_post': {
            'name': 'LinkedIn Post',
            'size': '1200x627',
            'aspect_ratio': '1.91:1',
            'caption_limit': 3000,
            'max_hashtags': 5,
            'best_times': ['7:00', '10:00', '12:00'],
            'style_tips': ['Professional', 'Data-driven', 'Thought leadership'],
            'content_types': ['carousels', 'documents', 'polls']
        },
        'tiktok_post': {
            'name': 'TikTok Video',
            'size': '1080x1920',
            'aspect_ratio': '9:16',
            'duration': '3 minutes max',
            'max_hashtags': 5,
            'best_times': ['7:00', '12:00', '19:00', '22:00'],
            'style_tips': ['Trendy', 'Authentic', 'Fast hooks'],
            'content_types': ['tutorials', 'duets', 'trends', 'behind the scenes']
        },
        'youtube_thumbnail': {
            'name': 'YouTube Thumbnail',
            'size': '1280x720',
            'aspect_ratio': '16:9',
            'best_times': ['14:00', '16:00'],
            'style_tips': ['Faces with expressions', 'Bold text (3-5 words)', 'High contrast', 'Curiosity gap'],
            'content_types': ['reaction faces', 'text overlays', 'before/after']
        },
        'pinterest_pin': {
            'name': 'Pinterest Pin',
            'size': '1000x1500',
            'aspect_ratio': '2:3',
            'best_times': ['20:00', '21:00'],
            'style_tips': ['Tall format', 'Text overlay', 'Lifestyle imagery'],
            'content_types': ['infographics', 'step-by-step', 'inspiration boards']
        }
    }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute social media strategy based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("social_media_strategy", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing social media request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["ask_for_clarification"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"SocialMediaAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Social media operation: {arguments}",
                            alternatives=[],
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
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    result = AgentResult(
                        success=True,
                        message="Social media strategy completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 380: Learning hooks for collective intelligence
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

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"Social Media Strategy: {task[:80]}",
                        content=result.message,
                        deliverable_type='analysis',
                        category='Social Media Strategy',
                        tags=['social_media', 'strategy'],
                        metadata={'task': task[:200]},
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
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

                    return result

            except Exception as e:
                logger.error(f"SocialMediaAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
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
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a social media tool call."""
        if tool_name == "get_platform_specs":
            return self._get_platform_specs(
                platform=arguments.get('platform', 'instagram_post')
            )

        elif tool_name == "recommend_format":
            return self._recommend_format(
                platform=arguments.get('platform', 'instagram_post'),
                goal=arguments.get('goal', 'engagement')
            )

        elif tool_name == "get_posting_schedule":
            return self._get_posting_schedule(
                platform=arguments.get('platform', 'instagram_post'),
                timezone=arguments.get('timezone', 'UTC')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _get_platform_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform specifications."""
        logger.info(f"Getting specs for platform: {platform}")

        specs = self.PLATFORM_SPECS.get(platform)
        if not specs:
            # Try to match partial name
            for key, value in self.PLATFORM_SPECS.items():
                if platform.lower() in key.lower() or key.lower() in platform.lower():
                    specs = value
                    break

        if not specs:
            return {
                'success': False,
                'error': f"Unknown platform: {platform}"
            }

        return {
            'success': True,
            'platform': platform,
            'specs': specs
        }

    def _recommend_format(
        self,
        platform: str,
        goal: str
    ) -> Dict[str, Any]:
        """Recommend content format for a platform and goal."""
        logger.info(f"Recommending format for {platform} with goal {goal}")

        specs = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS.get('instagram_post'))

        # Goal-specific recommendations
        goal_formats = {
            'engagement': ['carousel', 'polls', 'questions'],
            'awareness': ['single image', 'video', 'story'],
            'sales': ['product showcase', 'testimonials', 'link posts'],
            'education': ['tutorials', 'infographics', 'how-to'],
            'entertainment': ['memes', 'trends', 'behind the scenes']
        }

        recommended_formats = goal_formats.get(goal, ['single image'])

        return {
            'success': True,
            'platform': platform,
            'goal': goal,
            'recommended_formats': recommended_formats,
            'optimal_size': specs.get('size', '1080x1080'),
            'style_tips': specs.get('style_tips', []),
            'available_content_types': specs.get('content_types', [])
        }

    def _get_posting_schedule(
        self,
        platform: str,
        timezone: str
    ) -> Dict[str, Any]:
        """Get optimal posting times."""
        logger.info(f"Getting posting schedule for {platform}")

        specs = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS.get('instagram_post'))
        best_times = specs.get('best_times', ['9:00', '12:00', '17:00'])

        return {
            'success': True,
            'platform': platform,
            'timezone': timezone,
            'best_times': best_times,
            'frequency_recommendation': 'Post 1-2 times daily for optimal engagement',
            'notes': 'Times are general recommendations; test with your specific audience'
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for social media strategy."""
        return bool(task and task.strip())

"""
Content Executor Agent - Clean Architecture Wrapper
====================================================

Session 393: Refactored to use BaseAgent while preserving legacy functionality.

This module provides a clean architecture adapter for the legacy DonkeyBetzContentExecutor.
It wraps the existing content generation engine to work with the BaseAgent pattern.

Key Features Preserved:
    - AI-powered content generation for the platform
    - SEO optimization and scoring
    - Multiple content types (blog posts, articles, etc.)
    - LLM Enforcer integration for consistent AI behavior
    - Fallback content generation

Why a Wrapper?
    The legacy DonkeyBetzContentExecutor handles:
    - AgentExecution tracking via database models
    - Content parsing and SEO scoring
    - LLM Enforcer for controlled AI responses
    - Knowledge sharing via learning hooks

    We wrap it to gain:
    - TimeTravelMixin for decision tracking
    - Consistent AgentResult interface
    - Clean architecture compatibility
    - Standard execute() signature

Usage:
    from core.agents.content_executor_agent import ContentExecutorAgent

    agent = ContentExecutorAgent(user=request.user)
    result = agent.execute(
        task="Write a blog post about AI betting strategies",
        context={'content_type': 'blog_post', 'target_audience': 'sports enthusiasts'},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_content_execution_with_ml(content_data: dict) -> dict:
    """Analyze content execution using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
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
            'execution_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML content execution analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


# Supported content types
CONTENT_TYPES = [
    'blog_post',
    'article',
    'tutorial',
    'guide',
    'product_description',
    'landing_page',
    'email_campaign',
    'social_post',
]


class ContentExecutorAgent(BaseAgent):
    """
    Clean architecture wrapper for the legacy DonkeyBetzContentExecutor.

    This agent generates content for the Donkey Betz platform using AI,
    with SEO optimization and quality scoring.

    Content Types:
        - blog_post: Long-form blog content (800-1200 words)
        - article: News-style articles
        - tutorial: Step-by-step guides
        - guide: Comprehensive guides
        - product_description: Feature descriptions
        - landing_page: Landing page copy
        - email_campaign: Email content
        - social_post: Social media posts

    Features:
        - AI-powered generation using GPT-5-mini
        - SEO optimization and scoring
        - Keyword targeting for platform visibility
        - Structured output with title, content, tags
        - Fallback content when AI is unavailable
    """

    name = "ContentExecutorAgent"

    system_prompt = """You are ContentExecutorAgent, a specialist in creating compelling content for the Donkey Betz platform.

You generate SEO-optimized content that:
1. Showcases platform features and benefits
2. Educates users about AI-powered automation
3. Drives engagement and conversions
4. Targets relevant keywords for discoverability

Content types you create:
- Blog posts (800-1200 words)
- Articles and tutorials
- Product descriptions
- Landing page copy
- Email campaigns
- Social media posts

Your content is:
- Professional yet accessible
- Data-driven with specific examples
- Action-oriented with clear CTAs
- SEO-optimized with keyword integration"""

    tools = []  # No GPT tools - content is generated programmatically

    def __init__(self, user=None):
        """Initialize the content executor agent."""
        super().__init__(user)
        self._legacy_executor = None

    @property
    def legacy_executor(self):
        """Lazy-load the legacy DonkeyBetzContentExecutor."""
        if self._legacy_executor is None:
            from agents.content_executor import get_content_executor
            self._legacy_executor = get_content_executor()
        return self._legacy_executor

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute content generation.

        Args:
            task: Description of the content to create
            context: Can contain:
                - content_type: Type of content (blog_post, article, etc.)
                - target_audience: Who the content is for
                - keywords: Optional list of keywords to target
            scifi_context: Sci-fi features context (mood, memory, evolution)
            spider_context: Spider intelligence context (trends for content ideas)

        Returns:
            AgentResult with generated content
        """
        start_time = time.time()
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("content_generation", task, input_data=context):
            try:
                # Extract parameters from context
                content_type = context.get('content_type', 'blog_post')
                target_audience = context.get('target_audience', 'platform users')
                keywords = context.get('keywords', [])

                self.record_decision(
                    decision_type="content_type_selection",
                    action=f"Generating {content_type} for {target_audience}",
                    reasoning=f"Task: {task[:100]}",
                    alternatives=CONTENT_TYPES[:4],
                    confidence=0.9
                )

                # Generate content directly (bypass execution_id tracking for clean interface)
                content_result = self.legacy_executor._generate_donkey_betz_content(
                    task=task,
                    content_type=content_type,
                    audience=target_audience
                )

                execution_time = int((time.time() - start_time) * 1000)

                if content_result.get('success'):
                    result = AgentResult(
                        success=True,
                        message=f"Generated {content_type}: {content_result.get('title', 'Untitled')[:50]}",
                        data={
                            'content': content_result.get('content', ''),
                            'title': content_result.get('title', ''),
                            'tags': content_result.get('tags', []),
                            'word_count': content_result.get('word_count', 0),
                            'seo_score': content_result.get('seo_score', 0),
                            'ai_model': content_result.get('ai_model', 'unknown'),
                            'content_type': content_type,
                            'target_audience': target_audience,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=[]
                    )

                    self.mark_decision_outcome(
                        success=True,
                        result_summary=f"Generated {content_result.get('word_count', 0)} words, SEO: {content_result.get('seo_score', 0):.1%}"
                    )

                    # Learning hooks
                    self._record_learning_outcome(
                        result, task, context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )

                    seo_score = content_result.get('seo_score', 0)
                    if seo_score >= 0.7:
                        self._create_execution_memory(result, task, "success", 0.8)
                        self._share_knowledge(
                            knowledge_type='technique',
                            title=f"High-SEO {content_type}: {seo_score:.0%}",
                            knowledge_value={
                                'content_type': content_type,
                                'target_audience': target_audience,
                                'seo_score': seo_score,
                                'word_count': content_result.get('word_count', 0),
                            },
                            confidence=seo_score
                        )
                    else:
                        self._create_execution_memory(result, task, "success", 0.5)

                    return result

                else:
                    result = AgentResult(
                        success=False,
                        error=content_result.get('error', 'Content generation failed'),
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

                    self.mark_decision_outcome(
                        success=False,
                        result_summary="Content generation failed"
                    )

                    self._record_learning_outcome(result, task, context)
                    self._create_execution_memory(result, task, "failure", 0.6)

                    return result

            except Exception as e:
                logger.error(f"ContentExecutorAgent error: {e}", exc_info=True)
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
        """
        This agent doesn't use GPT tools - content is generated programmatically.

        Returns:
            Error dict since tools shouldn't be called
        """
        return {
            'success': False,
            'error': f"ContentExecutorAgent generates content programmatically. "
                    f"Pass task and context parameters instead."
        }

    @classmethod
    def get_content_types(cls) -> List[str]:
        """Return list of supported content types."""
        return CONTENT_TYPES.copy()


# Factory function for backwards compatibility
def get_content_executor_agent(user=None) -> ContentExecutorAgent:
    """
    Factory function to create a ContentExecutorAgent.

    Args:
        user: Django User object

    Returns:
        ContentExecutorAgent instance
    """
    return ContentExecutorAgent(user=user)

"""
Spider Context Mixin - Automatic Spider Intelligence for Agents

This mixin can be added to any agent to give it automatic access to
spider intelligence. It provides:

- Pre-execution context gathering
- Task-specific data enrichment
- Style and trend recommendations
- Cached data for performance

Usage:
    class MyAgent(SpiderContextMixin):
        def execute(self, **kwargs):
            # Get spider context for this task
            context = self.get_spider_context(kwargs.get('task', ''))

            # Use trending styles
            recommended_styles = context.style_recommendations

            # Check current trends
            trends = context.trends

            # ... rest of execution

Session 264: Phase 2 - Spider-Agent Bridge
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SpiderContextMixin:
    """
    Mixin that provides spider intelligence to any agent.

    Add this mixin to an agent class to give it automatic access to
    real-time spider data based on its specialization.

    Attributes:
        _spider_context: Cached spider context for current execution
        _context_service: Reference to AgentContextService
    """

    # Override in subclass if agent name differs from class name
    spider_agent_name: Optional[str] = None

    def __init__(self, *args, **kwargs):
        """Initialize mixin - call super to chain with other mixins/base."""
        super().__init__(*args, **kwargs)
        self._spider_context = None
        self._context_service = None

    @property
    def context_service(self):
        """Lazy load the agent context service."""
        if self._context_service is None:
            try:
                from core.super_platform.agent_context_service import get_agent_context_service
                self._context_service = get_agent_context_service()
            except ImportError:
                logger.warning("AgentContextService not available")
        return self._context_service

    def get_spider_context(self, task: Optional[str] = None, force_refresh: bool = False):
        """
        Get spider context for current task.

        Args:
            task: Optional task description for targeted context
            force_refresh: Force a fresh fetch, ignoring cache

        Returns:
            AgentContext with spider data, or empty context if unavailable
        """
        if self._spider_context is not None and not force_refresh:
            return self._spider_context

        if not self.context_service:
            # Return empty context if service unavailable
            from core.super_platform.agent_context_service import AgentContext
            return AgentContext()

        # Determine agent name
        agent_name = self.spider_agent_name or self.__class__.__name__

        # Get user if available
        user = getattr(self, 'user', None)

        # Fetch context
        self._spider_context = self.context_service.get_context_for_agent(
            agent_name=agent_name,
            task=task,
            user=user,
            use_cache=not force_refresh
        )

        return self._spider_context

    def get_trending_topics(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get current trending topics."""
        context = self.get_spider_context()
        return context.trends[:limit]

    def get_style_recommendations(self) -> List[str]:
        """Get recommended styles based on current trends."""
        context = self.get_spider_context()
        return context.style_recommendations

    def get_visual_trends(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get current visual/design trends."""
        context = self.get_spider_context()
        return context.visual_trends[:limit]

    def get_platform_insights(self) -> Dict[str, Any]:
        """Get insights about different platforms."""
        context = self.get_spider_context()
        return context.platform_insights

    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data."""
        context = self.get_spider_context()
        return context.market_data

    def get_job_market(self) -> Dict[str, Any]:
        """Get current job market data."""
        context = self.get_spider_context()
        return context.job_market

    def get_opportunities(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get current opportunities."""
        context = self.get_spider_context()
        return context.opportunities[:limit]

    def get_context_summary(self) -> str:
        """Get a text summary of current context."""
        context = self.get_spider_context()
        return context.get_summary()

    def get_prompt_enhancement(self, task: Optional[str] = None) -> str:
        """
        Get text to enhance prompts with spider intelligence.

        This can be appended to prompts to give the LLM current context.
        """
        if not self.context_service:
            return ""

        agent_name = self.spider_agent_name or self.__class__.__name__
        return self.context_service.get_prompt_injection(agent_name, task)

    def apply_trending_style(self, prompt: str) -> str:
        """
        Enhance a prompt with trending style if none specified.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt with trending style suggestion
        """
        # Check if prompt already has a style
        style_keywords = [
            'style', 'aesthetic', 'pixar', 'disney', 'anime', 'cyberpunk',
            'watercolor', 'photorealistic', 'minimalist', 'retro'
        ]

        prompt_lower = prompt.lower()
        has_style = any(kw in prompt_lower for kw in style_keywords)

        if has_style:
            return prompt

        # Add trending style
        recommendations = self.get_style_recommendations()
        if recommendations:
            style = recommendations[0]
            return f"{prompt}, {style} style"

        return prompt

    def enrich_generation_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich generation parameters with spider intelligence.

        This adds trending context without overriding explicit user choices.

        Args:
            params: Original generation parameters

        Returns:
            Enriched parameters
        """
        enriched = params.copy()

        # Add style recommendation if not specified
        if 'style' not in enriched or not enriched['style']:
            recommendations = self.get_style_recommendations()
            if recommendations:
                enriched['style_suggestion'] = recommendations[0]
                enriched['all_style_recommendations'] = recommendations

        # Add trending context
        context = self.get_spider_context()
        enriched['spider_context'] = {
            'trending_topics': [t.get('topic', str(t)) for t in context.trends[:3]],
            'style_recommendations': context.style_recommendations,
            'fetch_time': context.fetch_time.isoformat() if context.fetch_time else None,
        }

        return enriched

    def clear_spider_context(self):
        """Clear cached spider context."""
        self._spider_context = None

    def log_context_usage(self, operation: str):
        """Log that spider context was used in an operation."""
        context = self.get_spider_context()
        logger.info(
            f"{self.__class__.__name__} used spider context for {operation}: "
            f"{len(context.trends)} trends, {len(context.style_recommendations)} styles"
        )

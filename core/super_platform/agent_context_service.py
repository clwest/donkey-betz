"""
Agent Context Service - Spider Intelligence Injection for Agents

This service provides spider intelligence to all agents automatically.
Each agent type gets relevant data based on their specialization:

- ImageAgent: Visual trends, popular styles, design patterns
- VideoAgent: Video trends, motion styles, platform preferences
- ResearchAgent: News, market data, trending topics
- ContentStrategyAgent: Content trends, engagement patterns
- OpportunityScoringAgent: Job market, freelance opportunities, profit signals

Session 264: Phase 2 - Spider-Agent Bridge
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Context data for an agent execution."""
    # Core spider data
    trends: List[Dict[str, Any]] = field(default_factory=list)
    news: List[Dict[str, Any]] = field(default_factory=list)
    market_data: Dict[str, Any] = field(default_factory=dict)
    job_market: Dict[str, Any] = field(default_factory=dict)

    # Agent-specific enrichment
    visual_trends: List[Dict[str, Any]] = field(default_factory=list)
    style_recommendations: List[str] = field(default_factory=list)
    platform_insights: Dict[str, Any] = field(default_factory=dict)

    # Opportunity context
    opportunities: List[Dict[str, Any]] = field(default_factory=list)
    profit_signals: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    fetch_time: Optional[datetime] = None
    cache_hit: bool = False
    sources_used: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'trends': self.trends,
            'news': self.news,
            'market_data': self.market_data,
            'job_market': self.job_market,
            'visual_trends': self.visual_trends,
            'style_recommendations': self.style_recommendations,
            'platform_insights': self.platform_insights,
            'opportunities': self.opportunities,
            'profit_signals': self.profit_signals,
            'fetch_time': self.fetch_time.isoformat() if self.fetch_time else None,
            'cache_hit': self.cache_hit,
            'sources_used': self.sources_used,
        }

    def get_summary(self) -> str:
        """Get a text summary for prompt injection."""
        parts = []

        if self.trends:
            trend_names = [t.get('topic', str(t))[:30] for t in self.trends[:5]]
            parts.append(f"Trending: {', '.join(trend_names)}")

        if self.visual_trends:
            visual_names = [v.get('style', str(v))[:20] for v in self.visual_trends[:3]]
            parts.append(f"Visual trends: {', '.join(visual_names)}")

        if self.style_recommendations:
            parts.append(f"Recommended styles: {', '.join(self.style_recommendations[:3])}")

        if self.opportunities:
            parts.append(f"{len(self.opportunities)} active opportunities")

        return " | ".join(parts) if parts else "No context available"


class AgentContextService:
    """
    Provides spider intelligence to agents based on their specialization.

    This is the central service that bridges spider data to agent execution.
    It caches data to avoid redundant spider queries and provides agent-specific
    enrichment based on the agent type.
    """

    # Agent specialization mappings
    AGENT_SPECIALIZATIONS = {
        'ImageAgent': {
            'needs': ['visual_trends', 'style_recommendations', 'design_trends'],
            'spider_categories': ['creative', 'design', 'ai_tools'],
            'data_focus': 'visual',
        },
        'VideoAgent': {
            'needs': ['video_trends', 'platform_insights', 'motion_styles'],
            'spider_categories': ['creative', 'tech', 'social'],
            'data_focus': 'video',
        },
        'AudioAgent': {
            'needs': ['audio_trends', 'voice_styles', 'music_trends'],
            'spider_categories': ['creative', 'entertainment'],
            'data_focus': 'audio',
        },
        'ResearchAgent': {
            'needs': ['news', 'trends', 'market_data', 'tech_trends'],
            'spider_categories': ['tech', 'news', 'financial'],
            'data_focus': 'research',
        },
        'TrendAnalysisAgent': {
            'needs': ['trends', 'market_data', 'social_signals'],
            'spider_categories': ['tech', 'social', 'news'],
            'data_focus': 'analysis',
        },
        'ContentStrategyAgent': {
            'needs': ['trends', 'platform_insights', 'engagement_data'],
            'spider_categories': ['content', 'social', 'creative'],
            'data_focus': 'strategy',
        },
        'SEOOptimizerAgent': {
            'needs': ['trends', 'search_data', 'keyword_insights'],
            'spider_categories': ['tech', 'content', 'news'],
            'data_focus': 'seo',
        },
        'BrandIdentityAgent': {
            'needs': ['visual_trends', 'brand_trends', 'color_trends'],
            'spider_categories': ['design', 'creative', 'tech'],
            'data_focus': 'branding',
        },
        'SocialMediaAgent': {
            'needs': ['platform_insights', 'social_trends', 'engagement_data'],
            'spider_categories': ['social', 'content', 'creative'],
            'data_focus': 'social',
        },
        'CreativeDirectorAgent': {
            'needs': ['visual_trends', 'trends', 'creative_insights'],
            'spider_categories': ['creative', 'design', 'tech'],
            'data_focus': 'creative',
        },
        'OpportunityScoringAgent': {
            'needs': ['job_market', 'opportunities', 'profit_signals'],
            'spider_categories': ['jobs', 'freelance', 'financial'],
            'data_focus': 'opportunity',
        },
        'WorkflowOrchestrationAgent': {
            'needs': ['trends', 'platform_insights', 'market_data'],
            'spider_categories': ['tech', 'creative', 'content'],
            'data_focus': 'workflow',
        },
    }

    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_PREFIX = 'agent_context:'

    def __init__(self):
        """Initialize the agent context service."""
        self._spider_service = None

    @property
    def spider_service(self):
        """Lazy load spider intelligence service."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._spider_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
        return self._spider_service

    def get_context_for_agent(
        self,
        agent_name: str,
        task: Optional[str] = None,
        user=None,
        use_cache: bool = True
    ) -> AgentContext:
        """
        Get relevant context for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., 'ImageAgent')
            task: Optional task description for more targeted context
            user: Optional user for personalization
            use_cache: Whether to use cached data

        Returns:
            AgentContext with relevant spider data
        """
        # Check cache first
        cache_key = f"{self.CACHE_PREFIX}{agent_name}:{hash(task or '')}"

        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                cached['cache_hit'] = True
                return AgentContext(**cached)

        # Build fresh context
        context = self._build_context(agent_name, task)

        # Cache the result
        if use_cache:
            cache.set(cache_key, context.to_dict(), self.CACHE_TTL)

        return context

    def _build_context(self, agent_name: str, task: Optional[str] = None) -> AgentContext:
        """Build context for an agent based on its specialization."""
        context = AgentContext(fetch_time=timezone.now())

        if not self.spider_service:
            logger.warning("Spider service not available, returning empty context")
            return context

        # Get agent specialization
        specialization = self.AGENT_SPECIALIZATIONS.get(agent_name, {})
        data_focus = specialization.get('data_focus', 'general')

        try:
            # Get general trends
            trends = self.spider_service.get_trending_topics(hours=24)
            context.trends = trends[:10] if trends else []
            context.sources_used.append('trending_topics')

            # Get task-specific insights if task provided
            if task:
                insights = self.spider_service.get_insights_for_prompt(task)
                if insights:
                    context.news = insights.get('relevant_trends', [])[:5]
                    context.sources_used.append('task_insights')

            # Add specialized data based on agent focus
            if data_focus == 'visual':
                context = self._enrich_visual_context(context)
            elif data_focus == 'research':
                context = self._enrich_research_context(context)
            elif data_focus == 'opportunity':
                context = self._enrich_opportunity_context(context)
            elif data_focus == 'strategy':
                context = self._enrich_strategy_context(context)
            elif data_focus == 'social':
                context = self._enrich_social_context(context)

        except Exception as e:
            logger.error(f"Error building context for {agent_name}: {e}")

        return context

    def _enrich_visual_context(self, context: AgentContext) -> AgentContext:
        """Enrich context with visual/design trends."""
        try:
            # Extract visual trends from spider data
            visual_keywords = ['design', 'style', 'color', 'aesthetic', 'visual', 'art']
            visual_trends = [
                t for t in context.trends
                if any(kw in str(t).lower() for kw in visual_keywords)
            ]
            context.visual_trends = visual_trends[:5]

            # Style recommendations based on trends
            styles = self._extract_styles_from_trends(context.trends)
            context.style_recommendations = styles
            context.sources_used.append('visual_enrichment')

        except Exception as e:
            logger.warning(f"Error enriching visual context: {e}")

        return context

    def _enrich_research_context(self, context: AgentContext) -> AgentContext:
        """Enrich context with research/market data."""
        try:
            if self.spider_service:
                # Get market insights
                market = self.spider_service.get_market_insights()
                context.market_data = market if market else {}

                # Get tech trends
                # Session 483: get_tech_trends() returns dict with 'discussions' key
                tech = self.spider_service.get_tech_trends()
                if tech and isinstance(tech, dict):
                    # Primary key is 'discussions', fallback to 'projects'
                    tech_list = tech.get('discussions', tech.get('projects', []))
                    if isinstance(tech_list, list):
                        context.news.extend(tech_list[:3])
                elif tech and isinstance(tech, list):
                    # Legacy fallback if it returns a list
                    context.news.extend(tech[:3])

                context.sources_used.append('research_enrichment')

        except Exception as e:
            logger.warning(f"Error enriching research context: {e}")

        return context

    def _enrich_opportunity_context(self, context: AgentContext) -> AgentContext:
        """Enrich context with opportunity/job market data."""
        try:
            if self.spider_service:
                # Get job market summary
                jobs = self.spider_service.get_job_market_summary()
                context.job_market = jobs if jobs else {}

                # Extract opportunities from trends
                opp_keywords = ['freelance', 'remote', 'job', 'gig', 'opportunity', 'hiring']
                opportunities = [
                    t for t in context.trends
                    if any(kw in str(t).lower() for kw in opp_keywords)
                ]
                context.opportunities = opportunities[:5]

                context.sources_used.append('opportunity_enrichment')

        except Exception as e:
            logger.warning(f"Error enriching opportunity context: {e}")

        return context

    def _enrich_strategy_context(self, context: AgentContext) -> AgentContext:
        """Enrich context with content strategy data."""
        try:
            # Platform insights based on trends
            platform_keywords = {
                'youtube': ['youtube', 'video', 'tutorial'],
                'instagram': ['instagram', 'photo', 'visual'],
                'twitter': ['twitter', 'thread', 'tweet'],
                'linkedin': ['linkedin', 'professional', 'career'],
                'tiktok': ['tiktok', 'short', 'viral'],
            }

            platform_insights = {}
            for platform, keywords in platform_keywords.items():
                relevant = [
                    t for t in context.trends
                    if any(kw in str(t).lower() for kw in keywords)
                ]
                if relevant:
                    platform_insights[platform] = {
                        'trend_count': len(relevant),
                        'hot': len(relevant) > 2,
                    }

            context.platform_insights = platform_insights
            context.sources_used.append('strategy_enrichment')

        except Exception as e:
            logger.warning(f"Error enriching strategy context: {e}")

        return context

    def _enrich_social_context(self, context: AgentContext) -> AgentContext:
        """Enrich context with social media data."""
        # Similar to strategy but focused on engagement
        return self._enrich_strategy_context(context)

    def _extract_styles_from_trends(self, trends: List[Dict[str, Any]]) -> List[str]:
        """Extract style recommendations from trends."""
        # Known style keywords
        style_map = {
            'cyberpunk': ['cyberpunk', 'neon', 'futuristic', 'tech'],
            'minimalist': ['minimal', 'clean', 'simple'],
            'retro': ['retro', 'vintage', '80s', '90s'],
            'nature': ['nature', 'organic', 'natural'],
            'abstract': ['abstract', 'geometric', 'modern'],
            'anime': ['anime', 'manga', 'japanese'],
            'photorealistic': ['photo', 'realistic', 'hyper'],
        }

        recommended = []
        trend_text = ' '.join(str(t).lower() for t in trends)

        for style, keywords in style_map.items():
            if any(kw in trend_text for kw in keywords):
                recommended.append(style)

        # Always include some popular defaults
        defaults = ['cyberpunk', 'minimalist', 'photorealistic']
        for d in defaults:
            if d not in recommended:
                recommended.append(d)

        return recommended[:5]

    def get_prompt_injection(self, agent_name: str, task: Optional[str] = None) -> str:
        """
        Get a text string to inject into agent prompts.

        This provides agents with current intelligence they can use
        to make better decisions.
        """
        context = self.get_context_for_agent(agent_name, task)

        parts = ["\n## Current Intelligence\n"]

        if context.trends:
            parts.append("**Trending Topics:**")
            for t in context.trends[:5]:
                topic = t.get('topic', str(t)) if isinstance(t, dict) else str(t)
                parts.append(f"- {topic}")

        if context.style_recommendations:
            parts.append(f"\n**Recommended Styles:** {', '.join(context.style_recommendations)}")

        if context.platform_insights:
            hot_platforms = [p for p, v in context.platform_insights.items() if v.get('hot')]
            if hot_platforms:
                parts.append(f"\n**Hot Platforms:** {', '.join(hot_platforms)}")

        if context.opportunities:
            parts.append(f"\n**Active Opportunities:** {len(context.opportunities)} detected")

        parts.append(f"\n*Data freshness: {context.fetch_time.strftime('%H:%M') if context.fetch_time else 'N/A'}*\n")

        return "\n".join(parts)

    def invalidate_cache(self, agent_name: Optional[str] = None):
        """Invalidate cached context."""
        if agent_name:
            # Invalidate specific agent cache
            # Note: This is a simple implementation - in production you'd want pattern-based deletion
            logger.info(f"Invalidating cache for {agent_name}")
        else:
            # Invalidate all agent context caches
            logger.info("Invalidating all agent context caches")


# Singleton instance
_agent_context_service = None


def get_agent_context_service() -> AgentContextService:
    """Get the singleton AgentContextService instance."""
    global _agent_context_service
    if _agent_context_service is None:
        _agent_context_service = AgentContextService()
    return _agent_context_service

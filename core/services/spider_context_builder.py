"""
Spider Context Builder Service
Session 744 Phase 2: Auto-inject spider intelligence into agent prompts.

This service:
1. Maps agent types to relevant spider categories
2. Auto-queries SpiderIntelligenceService for context
3. Formats data for prompt injection
4. Adds freshness indicators and trending highlights

The goal is to make 100% of agents aware of real-world data,
not just the 5% that manually call spider services.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class SpiderContextBuilder:
    """
    Session 744: Automatically builds spider context for any agent.

    Usage:
        from core.services.spider_context_builder import get_spider_context_builder

        builder = get_spider_context_builder()
        context = builder.build_context_for_agent(
            agent_name='ImageAgent',
            task='Create a logo for a tech startup'
        )
    """

    # Map agent types/names to spider categories they should receive data from
    # Format: agent_pattern -> list of spider categories
    AGENT_SPIDER_MAPPINGS = {
        # Creative agents need design trends
        'image': ['creative', 'tech'],
        'video': ['creative', 'video', 'tech'],
        'audio': ['creative', 'video'],
        '3d': ['creative', 'tech'],
        'image_editing': ['creative'],
        'video_editing': ['creative', 'video'],

        # Research agents need broad data
        'research': ['tech', 'news', 'social', 'community'],
        'content_writer': ['tech', 'news', 'social'],
        'technical_document': ['tech'],

        # Strategy agents need market intelligence
        'content_strategy': ['tech', 'news', 'social', 'creative'],
        'brand_identity': ['creative', 'social', 'community'],
        'brand_strategy': ['tech', 'news', 'social', 'creative'],
        'seo_optimizer': ['tech', 'news'],
        'social_media': ['social', 'community', 'news'],
        'marketing_strategy': ['tech', 'news', 'social'],

        # Executive agents need broad awareness
        'cto': ['tech', 'news', 'financial'],
        'coo': ['tech', 'news', 'jobs'],
        'creative_director': ['creative', 'tech', 'social'],

        # Analysis agents need specific domain data
        'trend_analysis': ['tech', 'news', 'social', 'creative'],
        'opportunity_scoring': ['tech', 'jobs', 'financial'],
        'market_intelligence': ['financial', 'tech', 'news'],
        'competitor_analysis': ['tech', 'news', 'social'],
        'customer_research': ['social', 'community', 'news'],

        # Financial/market agents
        'stock': ['financial', 'news'],
        'prediction_market': ['financial', 'news', 'social'],
        'sports_odds': ['financial', 'news'],
        'arbitrage': ['financial'],
        'blockchain': ['crypto', 'financial', 'tech'],
        'whale_watcher': ['crypto', 'financial'],

        # Development agents need tech trends
        'code_generator': ['tech'],
        'full_stack_developer': ['tech', 'jobs'],
        'code_review': ['tech'],
        'devops': ['tech'],

        # Content studio agents
        'autonomous_content_studio': ['tech', 'news', 'social', 'creative'],
        'topic_miner': ['tech', 'news', 'social'],
        'contrarian': ['news', 'social', 'community'],
        'performance_analyst': ['tech', 'news'],
        'content_diversity': ['tech', 'news', 'social', 'creative', 'jobs', 'financial'],

        # Podcast agents
        'podcast': ['tech', 'news', 'social'],
        'debate': ['news', 'social', 'community'],
        'moderator': ['news', 'social'],

        # Job/career agents
        'job': ['jobs', 'tech'],
        'career': ['jobs', 'tech', 'news'],

        # Default for unmatched agents
        'default': ['tech', 'news'],
    }

    # Task keyword to category boost mappings
    # If task contains these keywords, add these categories
    TASK_KEYWORD_BOOSTS = {
        # Tech keywords
        'ai': ['tech'],
        'ml': ['tech'],
        'machine learning': ['tech'],
        'artificial intelligence': ['tech'],
        'coding': ['tech'],
        'programming': ['tech'],
        'software': ['tech'],
        'app': ['tech'],
        'website': ['tech'],
        'api': ['tech'],

        # Finance keywords
        'stock': ['financial'],
        'market': ['financial', 'tech'],
        'invest': ['financial'],
        'crypto': ['crypto', 'financial'],
        'bitcoin': ['crypto'],
        'ethereum': ['crypto'],
        'trading': ['financial'],
        'portfolio': ['financial'],

        # Creative keywords
        'logo': ['creative'],
        'design': ['creative'],
        'brand': ['creative', 'social'],
        'visual': ['creative'],
        'image': ['creative'],
        'video': ['creative', 'video'],
        'style': ['creative'],
        'aesthetic': ['creative'],

        # Job keywords
        'job': ['jobs'],
        'career': ['jobs'],
        'hiring': ['jobs'],
        'remote': ['jobs'],
        'salary': ['jobs'],
        'resume': ['jobs'],

        # Social keywords
        'social': ['social', 'community'],
        'trending': ['social', 'news'],
        'viral': ['social'],
        'community': ['community', 'social'],
        'audience': ['social'],
    }

    def __init__(self):
        # Lazy import to avoid circular imports
        self._intelligence_service = None

    @property
    def intelligence_service(self):
        """Lazy-load the SpiderIntelligenceService."""
        if self._intelligence_service is None:
            from core.services.spider_intelligence import get_spider_intelligence
            self._intelligence_service = get_spider_intelligence()
        return self._intelligence_service

    def _get_agent_categories(self, agent_name: str) -> List[str]:
        """
        Determine which spider categories are relevant for an agent.

        Args:
            agent_name: Name of the agent (e.g., 'ImageAgent', 'ResearchAgent')

        Returns:
            List of spider category names
        """
        agent_lower = agent_name.lower()

        # Try exact match patterns
        for pattern, categories in self.AGENT_SPIDER_MAPPINGS.items():
            if pattern in agent_lower:
                return categories

        # Return default categories
        return self.AGENT_SPIDER_MAPPINGS['default']

    def _get_task_category_boosts(self, task: str) -> List[str]:
        """
        Get additional categories based on task content.

        Args:
            task: The task description

        Returns:
            List of additional category names to include
        """
        task_lower = task.lower()
        boosts = set()

        for keyword, categories in self.TASK_KEYWORD_BOOSTS.items():
            if keyword in task_lower:
                boosts.update(categories)

        return list(boosts)

    def build_context_for_agent(
        self,
        agent_name: str,
        task: str,
        hours: int = 48,
        max_trends: int = 10,
        max_discussions: int = 5,
        include_market_data: bool = True
    ) -> Dict[str, Any]:
        """
        Build comprehensive spider context for an agent.

        This is the main method called by AgentRouter to auto-inject
        spider intelligence into agent prompts.

        Args:
            agent_name: Name of the agent
            task: The task being performed
            hours: Lookback period for data freshness
            max_trends: Maximum trending topics to include
            max_discussions: Maximum discussions/articles to include
            include_market_data: Whether to include financial data

        Returns:
            Dict with structured spider context ready for prompt injection
        """
        try:
            # Get categories from agent name and task
            agent_categories = self._get_agent_categories(agent_name)
            task_boosts = self._get_task_category_boosts(task)

            # Combine and deduplicate categories
            all_categories = list(set(agent_categories + task_boosts))

            logger.info(f"🕷️ [Session 744] Building spider context for {agent_name}")
            logger.debug(f"  Categories: {all_categories}")

            context = {
                'relevant_trends': [],
                'discussions': [],
                'articles': [],
                'market_data': None,
                'creative_trends': {},
                'job_data': None,
                'data_sources': [],
                'freshness': {
                    'last_updated': None,
                    'hours_covered': hours,
                    'data_quality': 'unknown'
                },
                'summary': '',
                'has_data': False,
                'categories_queried': all_categories,
            }

            # Collect trends from relevant categories
            all_trends = []
            all_discussions = []
            sources_used = set()

            for category in all_categories:
                try:
                    trends = self.intelligence_service.get_trending_topics(
                        category=category,
                        hours=hours,
                        limit=max_trends
                    )
                    if trends:
                        all_trends.extend(trends)
                        for trend in trends:
                            sources_used.update(trend.get('sources', []))
                except Exception as e:
                    logger.debug(f"Failed to get trends for {category}: {e}")

            # Deduplicate and rank trends
            seen_topics = set()
            unique_trends = []
            for trend in sorted(all_trends, key=lambda x: x.get('score', 0), reverse=True):
                topic = trend.get('topic', '').lower()
                if topic and topic not in seen_topics:
                    seen_topics.add(topic)
                    unique_trends.append(trend)

            context['relevant_trends'] = unique_trends[:max_trends]
            context['data_sources'] = list(sources_used)

            # Get tech trends if tech category is relevant
            if 'tech' in all_categories:
                try:
                    tech = self.intelligence_service.get_tech_trends(
                        hours=hours,
                        limit=max_discussions
                    )
                    if tech:
                        context['discussions'] = tech.get('discussions', [])[:max_discussions]
                        context['articles'] = tech.get('projects', [])[:max_discussions]
                except Exception as e:
                    logger.debug(f"Failed to get tech trends: {e}")

            # Get creative trends if creative category is relevant
            if 'creative' in all_categories:
                try:
                    creative = self.intelligence_service.get_creative_trends(hours=hours)
                    if creative and creative.get('has_live_data'):
                        context['creative_trends'] = {
                            'trending_styles': creative.get('trending_styles', [])[:5],
                            'trending_colors': creative.get('trending_colors', [])[:5],
                            'keywords': creative.get('keywords', [])[:10],
                        }
                except Exception as e:
                    logger.debug(f"Failed to get creative trends: {e}")

            # Get market data if financial/crypto categories are relevant
            if include_market_data and any(c in all_categories for c in ['financial', 'crypto']):
                try:
                    market = self.intelligence_service.get_market_insights()
                    if market:
                        context['market_data'] = {
                            'crypto': market.get('crypto', [])[:5],
                            'stocks': market.get('stocks', [])[:5],
                            'summary': market.get('summary', ''),
                        }
                except Exception as e:
                    logger.debug(f"Failed to get market data: {e}")

            # Get job data if jobs category is relevant
            if 'jobs' in all_categories:
                try:
                    jobs = self.intelligence_service.get_job_market_summary(hours=hours, limit=10)
                    if jobs and jobs.get('total_found', 0) > 0:
                        context['job_data'] = {
                            'total_jobs': jobs.get('total_found', 0),
                            'top_categories': jobs.get('categories', [])[:5],
                            'top_companies': jobs.get('companies', [])[:5],
                            'sample_jobs': jobs.get('jobs', [])[:5],
                        }
                except Exception as e:
                    logger.debug(f"Failed to get job data: {e}")

            # Also do a task-specific search for highly relevant content
            try:
                search_results = self.intelligence_service.search_spider_data(
                    query=task[:200],  # Truncate long tasks
                    hours=hours,
                    limit=5
                )
                if search_results:
                    context['related_discussions'] = search_results
            except Exception as e:
                logger.debug(f"Failed to search spider data: {e}")

            # Update freshness indicators
            context['freshness']['last_updated'] = timezone.now().isoformat()
            context['freshness']['data_quality'] = self._assess_data_quality(context)
            context['has_data'] = bool(
                context['relevant_trends'] or
                context['discussions'] or
                context['market_data'] or
                context['creative_trends']
            )

            # Build summary for quick prompt injection
            context['summary'] = self._build_context_summary(context, agent_name)

            logger.info(
                f"🕷️ [Session 744] Spider context built: "
                f"{len(context['relevant_trends'])} trends, "
                f"{len(context['discussions'])} discussions, "
                f"quality={context['freshness']['data_quality']}"
            )

            return context

        except Exception as e:
            logger.error(f"Failed to build spider context for {agent_name}: {e}")
            return {
                'relevant_trends': [],
                'discussions': [],
                'market_data': None,
                'creative_trends': {},
                'has_data': False,
                'error': str(e),
                'summary': '',
            }

    def _assess_data_quality(self, context: Dict[str, Any]) -> str:
        """Assess the quality/freshness of collected data."""
        score = 0

        if context.get('relevant_trends'):
            score += 2
        if context.get('discussions'):
            score += 2
        if context.get('market_data'):
            score += 1
        if context.get('creative_trends'):
            score += 1
        if context.get('job_data'):
            score += 1
        if context.get('related_discussions'):
            score += 1

        if score >= 6:
            return 'excellent'
        elif score >= 4:
            return 'good'
        elif score >= 2:
            return 'moderate'
        elif score >= 1:
            return 'limited'
        return 'none'

    def _build_context_summary(self, context: Dict[str, Any], agent_name: str) -> str:
        """Build a concise summary for prompt injection."""
        parts = []

        # Trending topics
        trends = context.get('relevant_trends', [])
        if trends:
            topic_names = [t.get('topic', '') for t in trends[:5]]
            parts.append(f"Trending: {', '.join(topic_names)}")

        # Creative trends for creative agents
        creative = context.get('creative_trends', {})
        if creative:
            styles = creative.get('trending_styles', [])
            if styles:
                style_names = [s.get('style', '') for s in styles[:3]]
                parts.append(f"Design trends: {', '.join(style_names)}")

        # Market snapshot for financial agents
        market = context.get('market_data', {})
        if market and market.get('summary'):
            parts.append(market['summary'])

        # Job market for career-related agents
        jobs = context.get('job_data', {})
        if jobs:
            parts.append(f"Job market: {jobs.get('total_jobs', 0)} listings found")

        if not parts:
            return ""

        return " | ".join(parts)

    def get_quick_context(self, task: str) -> Dict[str, Any]:
        """
        Quick method to get spider context without knowing the agent.
        Uses task analysis to determine relevant categories.

        Args:
            task: The task description

        Returns:
            Basic spider context dict
        """
        categories = self._get_task_category_boosts(task) or ['tech', 'news']

        return self.build_context_for_agent(
            agent_name='GenericAgent',
            task=task,
            hours=24,
            max_trends=5,
            max_discussions=3
        )


# Singleton instance
_spider_context_builder: Optional[SpiderContextBuilder] = None


def get_spider_context_builder() -> SpiderContextBuilder:
    """Get the singleton SpiderContextBuilder instance."""
    global _spider_context_builder
    if _spider_context_builder is None:
        _spider_context_builder = SpiderContextBuilder()
    return _spider_context_builder

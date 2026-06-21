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


# Session 1189 PR-3A (C-trace remediation #2 — vocabulary bridge):
# AGENT_SPIDER_MAPPINGS historically used human-semantic category names
# (`creative`, `crypto`, `sports`) that don't match the values actually
# stored in `SpiderData.data_type`. Session 1188's supply recon
# (deliverable 13032820-... / a48e1164-...) found those three keys had
# ZERO actionable rows in 30d while the real buckets (`design`,
# `visual_trends`, `video`, `blockchain`, `sports_odds`, `sports_news`)
# were unmapped from any agent that didn't explicitly list them.
#
# This alias map lets AGENT_SPIDER_MAPPINGS keep its semantic vocabulary
# while `_normalize_categories` translates to real data_type keys at
# query time. Soft transition — keys are KEPT (not removed) so any
# external caller or hardcoded string still resolves.
CATEGORY_ALIASES: Dict[str, List[str]] = {
    'creative': ['design', 'visual_trends', 'video'],
    'crypto': ['blockchain'],
    'sports': ['sports_odds', 'sports_news'],
    # Session 1189 PR-3B: `security` was the original mapping value for
    # cto/code_generator/code_review/devops/autonomous_content_studio but
    # the real SpiderData.data_type bucket is `cybersecurity` (15
    # actionable / 30d). Soft transition — those agents keep `'security'`
    # in their per-agent lists; the alias auto-expands.
    'security': ['cybersecurity'],
}

# Session 1189 PR-3A: snapshot of real SpiderData.data_type values
# present in the 30d supply recon (Session 1188 PR-2). Used by
# `_normalize_categories` to emit a one-time warning when a mapped
# category is neither a known data_type nor a known alias — which
# means that agent will silently receive no spider context for that
# bucket. Intentionally a frozen snapshot, not a live query —
# regenerate alongside PR-3B when new data_type buckets start
# producing supply. Listed alphabetically.
KNOWN_DATA_TYPES: frozenset = frozenset({
    'ai_ml', 'blockchain', 'business', 'community', 'content',
    'cybersecurity', 'defense_tech', 'design', 'education',
    'entertainment', 'financial', 'food', 'freelance', 'gaming',
    'government', 'health', 'healthtech', 'innovation', 'intelligence',
    'jobs', 'legal', 'legislation', 'library', 'lifestyle',
    'news', 'opportunity', 'parenting', 'prediction_markets',
    'real_estate', 'remote_work', 'science', 'social',
    'sports_news', 'sports_odds', 'startups', 'tech', 'training',
    'travel', 'video', 'visual_trends', 'weather', 'web_development',
})


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
    # Session 936: Expanded to include ALL spider categories for comprehensive coverage
    AGENT_SPIDER_MAPPINGS = {
        # Session 1188 (C-trace remediation #3): explicit Hot-agent keys
        # placed before substring fallbacks so traces show the explicit key
        # that fired. Mappings tuned via PR-2 (Rigby's supply recon) to use
        # real SpiderData.data_type values — `creative` had 0 actionable
        # supply in 30d; the real creative-domain buckets are design (31),
        # visual_trends (32), video (24). ResearchAgent additionally picks
        # up `ai_ml` (364) and `business` (92) — the largest research-relevant
        # buckets it was previously missing. ThinkingAgent kept on a curated
        # reasoning set (off the `default` fallback). Specs in deliverables
        # 51062b8c-0fdf-4ca9-855a-264962e2506c (PR-1) and conversation
        # pa-6658d90a3e4942b3 (PR-2 supply recon).
        # Broader vocabulary-bridge work (PR-3) tracked separately.
        'imageagent': ['design', 'visual_trends', 'video', 'tech', 'entertainment'],
        'researchagent': ['tech', 'news', 'social', 'community', 'financial', 'legal', 'science', 'health', 'ai_ml', 'business'],
        # Session 1189 PR-3B: + ai_ml (364 actionable / 30d, top: huggingface 331)
        'thinkingagent': ['tech', 'news', 'science', 'financial', 'ai_ml'],

        # Creative agents need design trends
        'image': ['creative', 'tech', 'entertainment'],
        'video': ['creative', 'video', 'tech', 'entertainment'],
        'audio': ['creative', 'video', 'entertainment'],
        '3d': ['creative', 'tech'],
        'image_editing': ['creative'],
        'video_editing': ['creative', 'video', 'entertainment'],

        # Research agents need broad data - Session 936: Add ALL categories
        'research': ['tech', 'news', 'social', 'community', 'financial', 'legal', 'science', 'health'],
        # Session 1189 PR-3B: + ai_ml, + content
        'content_writer': ['tech', 'news', 'social', 'financial', 'sports', 'entertainment', 'lifestyle', 'science', 'health', 'education', 'ai_ml', 'content'],
        # Session 1189 PR-3B: + ai_ml
        'technical_document': ['tech', 'science', 'ai_ml'],

        # Strategy agents need market intelligence
        # Session 1189 PR-3B: + ai_ml, + content
        'content_strategy': ['tech', 'news', 'social', 'creative', 'entertainment', 'ai_ml', 'content'],
        'brand_identity': ['creative', 'social', 'community'],
        # Session 1189 PR-3B: + ai_ml
        'brand_strategy': ['tech', 'news', 'social', 'creative', 'ai_ml'],
        'seo_optimizer': ['tech', 'news'],
        'social_media': ['social', 'community', 'news', 'entertainment'],
        # Session 1189 PR-3B: + ai_ml, + content
        'marketing_strategy': ['tech', 'news', 'social', 'ai_ml', 'content'],

        # Executive agents need broad awareness
        # Session 1189 PR-3B: + ai_ml, + training, + legislation
        'cto': ['tech', 'news', 'financial', 'security', 'ai_ml', 'training', 'legislation'],
        # Session 1189 PR-3B: + ai_ml, + remote_work, + training, + legislation
        'coo': ['tech', 'news', 'jobs', 'financial', 'ai_ml', 'remote_work', 'training', 'legislation'],
        'creative_director': ['creative', 'tech', 'social', 'entertainment'],

        # Analysis agents need specific domain data
        # Session 1189 PR-3B: + ai_ml
        'trend_analysis': ['tech', 'news', 'social', 'creative', 'financial', 'sports', 'ai_ml'],
        'opportunity_scoring': ['tech', 'jobs', 'financial', 'sports'],
        # Session 1189 PR-3B: + ai_ml, + legislation
        'market_intelligence': ['financial', 'tech', 'news', 'crypto', 'ai_ml', 'legislation'],
        # Session 1189 PR-3B: + ai_ml
        'competitor_analysis': ['tech', 'news', 'social', 'ai_ml'],
        'customer_research': ['social', 'community', 'news'],

        # Financial/market agents - Session 936: Add sports for betting
        'stock': ['financial', 'news', 'crypto'],
        # Session 1189 PR-3B: + prediction_markets (was missing its own bucket)
        'prediction_market': ['financial', 'news', 'social', 'sports', 'prediction_markets'],
        'sports_odds': ['sports', 'news', 'financial'],
        'arbitrage': ['financial', 'sports', 'crypto'],
        'blockchain': ['crypto', 'financial', 'tech'],
        'whale_watcher': ['crypto', 'financial'],

        # Development agents need tech trends
        # Session 1189 PR-3B: + ai_ml, + training
        'code_generator': ['tech', 'security', 'ai_ml', 'training'],
        # Session 1189 PR-3B: + ai_ml, + training, + remote_work
        'full_stack_developer': ['tech', 'jobs', 'ai_ml', 'training', 'remote_work'],
        # Session 1189 PR-3B: + ai_ml
        'code_review': ['tech', 'security', 'ai_ml'],
        # Session 1189 PR-3B: + ai_ml
        'devops': ['tech', 'security', 'ai_ml'],

        # Content studio agents - Session 936: Comprehensive category access
        # Session 1189 PR-3B: + ai_ml, + content
        'autonomous_content_studio': ['tech', 'news', 'social', 'creative', 'financial', 'sports', 'entertainment', 'science', 'ai_ml', 'content'],
        # Session 1189 PR-3B: + ai_ml, + content
        'topic_miner': ['tech', 'news', 'social', 'financial', 'sports', 'entertainment', 'science', 'lifestyle', 'ai_ml', 'content'],
        'contrarian': ['news', 'social', 'community', 'financial'],
        # Session 1189 PR-3B: + ai_ml
        'performance_analyst': ['tech', 'news', 'financial', 'ai_ml'],
        # Session 1189 PR-3B: + ai_ml
        'content_diversity': ['tech', 'news', 'social', 'creative', 'jobs', 'financial', 'sports', 'entertainment', 'science', 'lifestyle', 'health', 'education', 'ai_ml'],

        # Podcast agents
        'podcast': ['tech', 'news', 'social', 'entertainment'],
        'debate': ['news', 'social', 'community', 'financial'],
        'moderator': ['news', 'social'],

        # Job/career agents
        # Session 1189 PR-3B: + remote_work (345 actionable / 30d)
        'job': ['jobs', 'tech', 'remote_work'],
        # Session 1189 PR-3B: + remote_work, + training
        'career': ['jobs', 'tech', 'news', 'education', 'remote_work', 'training'],

        # Legal agents (Session 744 enhancement)
        # Session 1189 PR-3B: + legislation (331 actionable / 30d)
        'legal': ['legal', 'news', 'legislation'],
        'legal_doc': ['legal', 'news', 'legislation'],

        # Session 936: Sports/betting agents
        'sports': ['sports', 'news', 'financial'],
        'betting': ['sports', 'financial', 'news'],

        # Session 936: Health/science agents
        'health': ['health', 'science', 'news'],
        'science': ['science', 'tech', 'news'],

        # Session 936: Education agents
        # Session 1189 PR-3B: + training (334 actionable / 30d, discord_training top)
        'education': ['education', 'tech', 'news', 'training'],

        # Default for unmatched agents - Session 936: Broader default coverage
        'default': ['tech', 'news', 'financial', 'social'],
    }

    # Task keyword to category boost mappings
    # If task contains these keywords, add these categories
    # Session 744 enhancement: Comprehensive domain coverage
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
        'cloud': ['tech'],
        'database': ['tech'],
        'security': ['tech'],
        'devops': ['tech'],
        'startup': ['tech', 'news'],

        # Finance keywords
        'stock': ['financial'],
        'market': ['financial', 'tech'],
        'invest': ['financial'],
        'crypto': ['crypto', 'financial'],
        'bitcoin': ['crypto'],
        'ethereum': ['crypto'],
        'trading': ['financial'],
        'portfolio': ['financial'],
        'earnings': ['financial', 'news'],
        'ipo': ['financial', 'news'],
        'sec': ['financial', 'legal'],
        'hedge fund': ['financial'],
        'wall street': ['financial', 'news'],

        # Creative keywords
        'logo': ['creative'],
        'design': ['creative'],
        'brand': ['creative', 'social'],
        'visual': ['creative'],
        'image': ['creative'],
        'video': ['creative', 'video'],
        'style': ['creative'],
        'aesthetic': ['creative'],
        'art': ['creative'],
        'illustration': ['creative'],
        'photography': ['creative'],
        'animation': ['creative', 'video'],

        # Job keywords
        'job': ['jobs'],
        'career': ['jobs'],
        'hiring': ['jobs'],
        'remote': ['jobs'],
        'salary': ['jobs'],
        'resume': ['jobs'],
        'interview': ['jobs'],
        'employment': ['jobs'],
        'freelance': ['jobs'],
        'gig': ['jobs'],

        # Social keywords
        'social': ['social', 'community'],
        'trending': ['social', 'news'],
        'viral': ['social'],
        'community': ['community', 'social'],
        'audience': ['social'],
        'influencer': ['social'],
        'engagement': ['social'],
        'followers': ['social'],

        # Legal keywords (Session 744 enhancement)
        'legal': ['legal'],
        'law': ['legal'],
        'lawyer': ['legal'],
        'attorney': ['legal'],
        'court': ['legal'],
        'lawsuit': ['legal', 'news'],
        'litigation': ['legal'],
        'custody': ['legal'],
        'divorce': ['legal'],
        'family law': ['legal'],
        'parenting': ['legal', 'lifestyle'],
        'visitation': ['legal'],
        'child support': ['legal'],
        'alimony': ['legal'],
        'contract': ['legal'],
        'regulation': ['legal', 'news'],
        'compliance': ['legal', 'tech'],
        'patent': ['legal', 'tech'],
        'trademark': ['legal'],
        'copyright': ['legal'],
        'colorado': ['legal'],  # Colorado-specific legal spiders

        # Health/Medical keywords (Session 744 enhancement)
        'health': ['health'],
        'medical': ['health'],
        'healthcare': ['health', 'tech'],
        'wellness': ['health', 'lifestyle'],
        'fitness': ['health', 'lifestyle'],
        'nutrition': ['health', 'lifestyle'],
        'mental health': ['health'],
        'therapy': ['health'],
        'hospital': ['health', 'news'],
        'doctor': ['health'],
        'pharmaceutical': ['health', 'financial'],
        'fda': ['health', 'news'],

        # Real Estate keywords (Session 744 enhancement)
        'real estate': ['real_estate'],
        'property': ['real_estate'],
        'housing': ['real_estate', 'news'],
        'mortgage': ['real_estate', 'financial'],
        'rent': ['real_estate'],
        'apartment': ['real_estate'],
        'home': ['real_estate'],
        'realtor': ['real_estate'],
        'mls': ['real_estate'],

        # Entertainment keywords (Session 744 enhancement)
        'movie': ['entertainment', 'news'],
        'film': ['entertainment', 'creative'],
        'music': ['entertainment', 'creative'],
        'gaming': ['entertainment', 'tech'],
        'game': ['entertainment', 'tech'],
        'esports': ['entertainment', 'news'],
        'streaming': ['entertainment', 'tech'],
        'netflix': ['entertainment', 'news'],
        'spotify': ['entertainment'],
        'youtube': ['entertainment', 'social'],
        'podcast': ['entertainment', 'social'],

        # Science/Education keywords (Session 744 enhancement)
        'science': ['science', 'tech'],
        'research': ['science', 'tech'],
        'study': ['science', 'education'],
        'education': ['education'],
        'university': ['education'],
        'course': ['education'],
        'learning': ['education'],
        'training': ['education'],
        'certification': ['education', 'jobs'],

        # Food/Lifestyle keywords (Session 744 enhancement)
        'food': ['food', 'lifestyle'],
        'restaurant': ['food', 'lifestyle'],
        'coffee': ['food', 'lifestyle'],
        'recipe': ['food'],
        'dining': ['food', 'lifestyle'],
        'travel': ['travel', 'lifestyle'],
        'vacation': ['travel'],
        'hotel': ['travel'],
        'flight': ['travel'],
        'destination': ['travel'],

        # News/Current Events keywords (Session 744 enhancement)
        'news': ['news'],
        'breaking': ['news'],
        'politics': ['news', 'government'],
        'election': ['news', 'government'],
        'government': ['government', 'news'],
        'policy': ['government', 'news'],
        'congress': ['government', 'news'],
        'senate': ['government', 'news'],
        'white house': ['government', 'news'],
        'war': ['news'],
        'climate': ['news', 'science'],
        'weather': ['weather', 'news'],
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

    # Session 1189 PR-3A: process-wide warn-once tracking so we don't
    # flood logs every dispatch when an agent mapping references an
    # unknown category.
    _warned_unknown_categories: set = set()

    def _normalize_categories(self, categories: List[str]) -> List[str]:
        """Translate AGENT_SPIDER_MAPPINGS values to real SpiderData.data_type
        keys via CATEGORY_ALIASES, deduplicating while preserving order.

        Unknown categories (not in CATEGORY_ALIASES, not in KNOWN_DATA_TYPES)
        pass through unchanged with a one-time WARN per process — they
        will fetch nothing but we don't drop them in case a new data_type
        is in flight and KNOWN_DATA_TYPES just hasn't been refreshed yet.
        """
        if not categories:
            return []
        resolved: List[str] = []
        seen: set = set()
        for cat in categories:
            if not isinstance(cat, str):
                continue
            expansion = CATEGORY_ALIASES.get(cat)
            if expansion is not None:
                logger.debug(
                    f"[session-1189-pr3a] alias '{cat}' → {expansion}"
                )
                for real in expansion:
                    if real not in seen:
                        seen.add(real)
                        resolved.append(real)
                continue
            if cat not in KNOWN_DATA_TYPES and cat not in self._warned_unknown_categories:
                self._warned_unknown_categories.add(cat)
                logger.warning(
                    f"[session-1189-pr3a] AGENT_SPIDER_MAPPINGS references "
                    f"unknown category '{cat}' (neither alias nor known "
                    f"SpiderData.data_type) — that bucket will return empty. "
                    f"Add it to KNOWN_DATA_TYPES or CATEGORY_ALIASES if it's "
                    f"a real bucket. Subsequent occurrences suppressed."
                )
            if cat not in seen:
                seen.add(cat)
                resolved.append(cat)
        return resolved

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

            # Combine and deduplicate categories (pre-alias — what was REQUESTED)
            requested_categories = list(dict.fromkeys(agent_categories + task_boosts))

            # Session 1189 PR-3A: normalize via CATEGORY_ALIASES so
            # `creative`/`crypto`/`sports` etc. expand to real
            # SpiderData.data_type keys before we hit the intelligence
            # service. `all_categories` (post-alias) is what actually
            # gets queried below.
            all_categories = self._normalize_categories(requested_categories)

            logger.info(f"🕷️ [Session 744] Building spider context for {agent_name}")
            logger.debug(f"  Categories (requested → resolved): {requested_categories} → {all_categories}")

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
                # Session 1189 PR-3A: split requested (pre-alias) vs queried
                # (post-alias) so AC instrumentation can record the
                # divergence introduced by CATEGORY_ALIASES.
                'categories_requested': requested_categories,
                'categories_queried': all_categories,
                # Session 1189 (AC instrumentation): per-category breakdowns so
                # AC like "has_data=True against ai_ml specifically" is queryable.
                # Tracked across the trending-topics loop below. Per-category
                # supply from secondary lookups (creative/tech/market/jobs) is
                # not split here — those are aggregated wholesale into the
                # respective context keys.
                'items_returned_by_category': {},
                'has_data_by_category': {},
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
                        limit=max_trends,
                        max_entries=50,
                    )
                    count = len(trends) if trends else 0
                    context['items_returned_by_category'][category] = count
                    context['has_data_by_category'][category] = bool(count)
                    if trends:
                        all_trends.extend(trends)
                        for trend in trends:
                            sources_used.update(trend.get('sources', []))
                except Exception as e:
                    logger.debug(f"Failed to get trends for {category}: {e}")
                    context['items_returned_by_category'][category] = 0
                    context['has_data_by_category'][category] = False

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
                        limit=max_discussions,
                        max_entries=50,
                    )
                    if tech:
                        context['discussions'] = tech.get('discussions', [])[:max_discussions]
                        context['articles'] = tech.get('projects', [])[:max_discussions]
                except Exception as e:
                    logger.debug(f"Failed to get tech trends: {e}")

            # Get creative trends if creative category is relevant
            if 'creative' in all_categories:
                try:
                    creative = self.intelligence_service.get_creative_trends(hours=hours, max_entries=50)
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
                    market = self.intelligence_service.get_market_insights(max_entries=50)
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
                    jobs = self.intelligence_service.get_job_market_summary(hours=hours, limit=10, max_entries=50)
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

    def build_summary(
        self,
        agent_name: str,
        task: str,
        max_trends: int = 5,
        max_chars: int = 200
    ) -> str:
        """
        Session 806: Build a compact summary of spider intelligence.

        This method returns a single-line summary suitable for prompt injection
        with minimal token usage (~50 tokens vs ~500 for full context).

        Args:
            agent_name: Name of the agent
            task: The task being performed
            max_trends: Maximum trending topics to include
            max_chars: Maximum characters for the summary

        Returns:
            Compact summary string like:
            "Trending: AI agents, quantum | Market: BTC +2.3% | Hot: OpenAI announces..."
        """
        try:
            # Get full context first
            context = self.build_context_for_agent(
                agent_name=agent_name,
                task=task,
                hours=24,
                max_trends=max_trends,
                max_discussions=2
            )

            if not context.get('has_data'):
                return ""

            # Session 960: Date anchor so agents know data recency
            from django.utils import timezone as tz
            date_prefix = f"[Data as of {tz.now().strftime('%b %d, %Y %H:%M UTC')}] "

            # Use the built-in summary or compress further
            summary = context.get('summary', '')
            if summary and len(summary) + len(date_prefix) <= max_chars:
                return date_prefix + summary

            # Build a more compact summary
            parts = []

            # Trending topics (most important)
            trends = context.get('relevant_trends', [])
            if trends:
                topic_names = [t.get('topic', '')[:20] for t in trends[:3] if t.get('topic')]
                if topic_names:
                    parts.append(f"Trending: {', '.join(topic_names)}")

            # Market snapshot
            market = context.get('market_data', {})
            if market:
                crypto = market.get('crypto', [])
                if crypto:
                    top = crypto[0]
                    change = top.get('change_24h', 0)
                    parts.append(f"{top.get('symbol', 'BTC')} {'+' if change >= 0 else ''}{change:.1f}%")

            result = date_prefix + " | ".join(parts) if parts else ""

            # Truncate if still too long
            if len(result) > max_chars:
                result = result[:max_chars - 3] + "..."

            logger.debug(f"🕷️ [Session 806] Spider summary: {len(result)} chars")
            return result

        except Exception as e:
            logger.warning(f"Failed to build spider summary: {e}")
            return ""


# Singleton instance
_spider_context_builder: Optional[SpiderContextBuilder] = None


def get_spider_context_builder() -> SpiderContextBuilder:
    """Get the singleton SpiderContextBuilder instance."""
    global _spider_context_builder
    if _spider_context_builder is None:
        _spider_context_builder = SpiderContextBuilder()
    return _spider_context_builder

"""
Content Diversity Orchestrator Agent
=====================================

Session 743: Phase 2 - Orchestration Layer

This agent ensures content diversity by:
1. Analyzing spider data across all 77 sources by category
2. Checking content created recently by category
3. Identifying coverage gaps (e.g., no legal content in 7 days)
4. Routing topics to appropriate channels and agents
5. Triggering content creation for underserved domains

The goal is to prevent the system from creating only AI content
when it has diverse spider data from finance, legal, sports, etc.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import timedelta
from collections import defaultdict

from django.utils import timezone
from django.db.models import Count

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class ContentDiversityOrchestrator(BaseAgent):
    """
    Orchestrates content diversity across all channels.

    This agent runs periodically (via Celery) to:
    - Analyze what spider data is available
    - Check what content has been created
    - Identify gaps in coverage
    - Trigger content creation for underserved domains
    """

    name = "ContentDiversityOrchestrator"
    system_prompt = """You are the Content Diversity Orchestrator.

Your role is to ensure the content creation system produces diverse content
across all available categories, not just AI/ML topics.

You analyze spider data availability and recent content creation to identify
gaps, then trigger content creation for underserved domains.

Categories you manage:
- Finance & Markets (stocks, crypto, SEC filings)
- Legal (court cases, regulations)
- Sports & Betting (odds, predictions)
- Entertainment (gaming, music, streaming)
- Science & Research (papers, discoveries)
- Jobs & Careers (employment trends)
- Tech/AI (already well-covered)
"""

    tools = []  # No GPT tools - this agent works directly with data

    # Category to spider mapping
    # Session 936: Updated to include ALL 77 registered spiders
    # Previously only ~42 spiders were mapped, causing content to miss data from 35 spiders
    CATEGORY_SPIDERS = {
        'finance': [
            'yahoo_finance', 'coingecko', 'finnhub', 'polygon_finance', 'sec_edgar',
            'etherscan', 'etherscan_api', 'crunchbase', 'kickstarter',
        ],
        'legal': [
            'courtlistener', 'findlaw', 'justia', 'lii', 'colorado_family_law',
            'justia_family_law', 'legal_news', 'government',
        ],
        'sports': ['theodds', 'kalshi'],
        'entertainment': [
            'youtube', 'spotify', 'variety', 'polygon_gaming', 'giphy', 'unsplash',
        ],
        'science': [
            'science', 'kaggle', 'huggingface', 'arxiv', 'library',
        ],
        'jobs': [
            'adzuna', 'remoteok', 'weworkremotely', 'github_jobs',
        ],
        'tech': [
            'hackernews', 'devto', 'techcrunch', 'theverge', 'github', 'producthunt',
            'arstechnica', 'wired', 'venturebeat', 'mit_tech_review', 'techcrunch_startups',
            'hackernoon', 'freecodecamp', 'smashingmagazine', 'awwwards', 'behance',
        ],
        'news': [
            'reuters_rss', 'bbc', 'cnn', 'npr', 'axios', 'google_news', 'newsapi',
            'business_news', 'defenseone',
        ],
        'lifestyle': [
            'food', 'travel', 'parenting', 'health', 'real_estate', 'lifehacker',
        ],
        'social': [
            'reddit', 'bluesky', 'discord', 'discord_training', 'medium', 'substack',
        ],
        'education': [
            'coursera', 'udemy', 'teachable', 'education_rss',
        ],
        'security': [
            'securityweek',
        ],
        'health': [
            'mobihealthnews',
        ],
        'weather': [
            'noaa_weather', 'openmeteo',
        ],
    }

    # Category to channel name mapping
    # Session 936: Added channels for new spider categories
    CATEGORY_CHANNELS = {
        'finance': 'Finance & Markets Daily',
        'legal': 'Legal Developments Weekly',
        'sports': 'Sports & Betting Insights',
        'entertainment': 'Entertainment & Culture Weekly',
        'science': 'Science & Research Roundup',
        'jobs': 'Job Market & Career Trends',
        'tech': 'Daily AI News',  # Existing channel
        'news': 'Breaking News Digest',
        'lifestyle': 'Lifestyle & Wellness',
        'social': 'Social Media Trends',
        'education': 'Education & Learning',
        'security': 'Security Updates',
        'health': 'Health Tech News',
        'weather': 'Weather & Climate',
    }

    # Minimum content frequency per category (in days)
    # Session 936: Added frequencies for new spider categories
    CATEGORY_FREQUENCY = {
        'finance': 1,       # daily
        'legal': 7,         # weekly
        'sports': 1,        # daily
        'entertainment': 7,  # weekly
        'science': 7,       # weekly
        'jobs': 7,          # weekly
        'tech': 1,          # daily
        'news': 1,          # daily
        'lifestyle': 7,     # weekly
        'social': 3,        # every 3 days
        'education': 7,     # weekly
        'security': 3,      # every 3 days
        'health': 7,        # weekly
        'weather': 1,       # daily
    }

    def __init__(self, user=None):
        super().__init__()
        self.user = user

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute diversity analysis and trigger content creation.

        Args:
            task: The orchestration task (e.g., "check_diversity", "create_content")
            context: Additional context
            scifi_context: Mood/evolution context (unused)
            spider_context: Spider data context (unused - we query directly)

        Returns:
            AgentResult with diversity analysis and actions taken
        """
        import time
        start_time = time.time()

        try:
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((time.time() - start_time) * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, an orchestrator ensuring AI-generated content remains diverse and non-repetitive. One capability: I analyze content gaps across categories, detect over-representation in topics or styles, and trigger creation of underrepresented content to maintain variety.",
                    data={'type': 'self_description', 'capabilities': ['gap_analysis', 'diversity_scoring', 'content_orchestration']},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            # Get action from context or default to full analysis
            action = context.get('action', 'full_analysis')

            if action == 'analyze_gaps':
                result_data = self._analyze_content_gaps()
            elif action == 'create_for_category':
                category = context.get('category')
                if not category:
                    return AgentResult(
                        success=False,
                        error="No category specified for create_for_category action",
                        agent_name=self.name
                    )
                result_data = self._create_content_for_category(category)
            elif action == 'full_analysis':
                result_data = self._full_diversity_check()
            else:
                result_data = self._full_diversity_check()

            execution_time = int((time.time() - start_time) * 1000)

            return AgentResult(
                success=True,
                message=result_data.get('summary', 'Diversity analysis complete'),
                data=result_data,
                agent_name=self.name,
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"ContentDiversityOrchestrator error: {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _get_spider_data_by_category(self, hours: int = 168) -> Dict[str, Dict]:
        """
        Get spider data summary grouped by category.

        Returns dict like:
        {
            'finance': {'spiders': ['yahoo_finance'], 'total_items': 150, 'latest': '2026-01-10'},
            'legal': {'spiders': ['courtlistener'], 'total_items': 50, 'latest': '2026-01-09'},
            ...
        }
        """
        from core.models_unified_system import LegacySpiderData

        since = timezone.now() - timedelta(hours=hours)

        category_data = {}

        for category, spiders in self.CATEGORY_SPIDERS.items():
            spider_runs = LegacySpiderData.objects.filter(
                spider_name__in=spiders,
                created_at__gte=since
            )

            # Count items across all runs
            total_items = 0
            active_spiders = set()
            latest_run = None

            for run in spider_runs:
                active_spiders.add(run.spider_name)
                if run.raw_data and 'items' in run.raw_data:
                    total_items += len(run.raw_data['items'])
                if not latest_run or run.created_at > latest_run:
                    latest_run = run.created_at

            category_data[category] = {
                'spiders': list(active_spiders),
                'spider_count': len(active_spiders),
                'total_runs': spider_runs.count(),
                'total_items': total_items,
                'latest': latest_run.isoformat() if latest_run else None,
                'has_data': total_items > 0
            }

        return category_data

    def _get_content_by_category(self, days: int = 7) -> Dict[str, Dict]:
        """
        Get content created in the last N days by category.

        Returns dict like:
        {
            'finance': {'episodes': 2, 'latest': '2026-01-10', 'channel': 'Finance & Markets Daily'},
            'legal': {'episodes': 0, 'latest': None, 'channel': 'Legal Developments Weekly'},
            ...
        }
        """
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode

        since = timezone.now() - timedelta(days=days)

        category_content = {}

        for category, channel_name in self.CATEGORY_CHANNELS.items():
            try:
                channel = ContentChannel.objects.get(name=channel_name)
                episodes = ChannelEpisode.objects.filter(
                    channel=channel,
                    created_at__gte=since
                )

                latest_episode = episodes.order_by('-created_at').first()

                category_content[category] = {
                    'channel_id': str(channel.id),
                    'channel_name': channel_name,
                    'episodes': episodes.count(),
                    'latest': latest_episode.created_at.isoformat() if latest_episode else None,
                    'total_episodes': channel.total_episodes_created
                }
            except ContentChannel.DoesNotExist:
                category_content[category] = {
                    'channel_id': None,
                    'channel_name': channel_name,
                    'episodes': 0,
                    'latest': None,
                    'total_episodes': 0,
                    'error': 'Channel not found'
                }

        return category_content

    def _analyze_content_gaps(self) -> Dict[str, Any]:
        """
        Identify categories that need content based on:
        - Spider data availability (has fresh data)
        - Content recency (no content in expected frequency window)
        """
        spider_data = self._get_spider_data_by_category()
        content_data = self._get_content_by_category()

        gaps = []
        coverage_score = 0
        total_categories = len(self.CATEGORY_CHANNELS)

        for category in self.CATEGORY_CHANNELS.keys():
            spider_info = spider_data.get(category, {})
            content_info = content_data.get(category, {})
            frequency_days = self.CATEGORY_FREQUENCY.get(category, 7)

            has_spider_data = spider_info.get('has_data', False)
            episodes_in_window = content_info.get('episodes', 0)

            # Calculate days since last content
            days_since_content = None
            if content_info.get('latest'):
                from django.utils.dateparse import parse_datetime
                latest = parse_datetime(content_info['latest'])
                if latest:
                    days_since_content = (timezone.now() - latest).days

            # Determine if this category needs content
            needs_content = False
            reason = None

            if has_spider_data and episodes_in_window == 0:
                needs_content = True
                reason = f"No content in last {frequency_days} days despite having spider data"
            elif has_spider_data and days_since_content and days_since_content > frequency_days:
                needs_content = True
                reason = f"Content is {days_since_content} days old (target: {frequency_days} days)"

            if needs_content:
                gaps.append({
                    'category': category,
                    'channel_name': self.CATEGORY_CHANNELS[category],
                    'channel_id': content_info.get('channel_id'),
                    'reason': reason,
                    'spider_items_available': spider_info.get('total_items', 0),
                    'days_since_content': days_since_content,
                    'target_frequency_days': frequency_days,
                    'priority': self._calculate_priority(category, days_since_content, spider_info)
                })
            else:
                coverage_score += 1

        # Sort gaps by priority
        gaps.sort(key=lambda x: x['priority'], reverse=True)

        return {
            'gaps': gaps,
            'total_gaps': len(gaps),
            'coverage_score': round((coverage_score / total_categories) * 100, 1),
            'spider_data': spider_data,
            'content_data': content_data,
            'analysis_timestamp': timezone.now().isoformat()
        }

    def _calculate_priority(self, category: str, days_since: Optional[int], spider_info: Dict) -> int:
        """Calculate priority score for content creation (higher = more urgent)."""
        priority = 0

        # More items available = higher priority
        items = spider_info.get('total_items', 0)
        if items > 100:
            priority += 3
        elif items > 50:
            priority += 2
        elif items > 0:
            priority += 1

        # Longer since last content = higher priority
        if days_since:
            if days_since > 14:
                priority += 4
            elif days_since > 7:
                priority += 3
            elif days_since > 3:
                priority += 2
            elif days_since > 1:
                priority += 1
        else:
            # Never had content
            priority += 5

        # Category weighting (finance/sports are time-sensitive)
        if category in ['finance', 'sports']:
            priority += 2

        return priority

    def _create_content_for_category(self, category: str) -> Dict[str, Any]:
        """
        Trigger content creation for a specific category.

        Uses the AutonomousContentStudioCoordinator to create content
        for the appropriate channel.
        """
        from core.agents.autonomous_content_studio_coordinator import AutonomousContentStudioCoordinator
        from core.models_autonomous_studio import ContentChannel
        from core.services.spider_intelligence import SpiderIntelligenceService

        channel_name = self.CATEGORY_CHANNELS.get(category)
        if not channel_name:
            return {'error': f'No channel mapped for category: {category}'}

        try:
            channel = ContentChannel.objects.get(name=channel_name)
        except ContentChannel.DoesNotExist:
            return {'error': f'Channel not found: {channel_name}'}

        # Get trending topics from spider data for this category
        spider_service = SpiderIntelligenceService()
        spiders = self.CATEGORY_SPIDERS.get(category, [])

        # Get trending topics
        if category == 'finance':
            trends = spider_service.get_market_insights()
            # Extract a topic from market data
            topic = self._extract_finance_topic(trends)
        elif category == 'tech':
            trends = spider_service.get_tech_trends(hours=48, limit=5)
            topic = self._extract_tech_topic(trends)
        elif category == 'jobs':
            trends = spider_service.get_job_market_summary(hours=72, limit=5)
            topic = self._extract_jobs_topic(trends)
        else:
            # Generic topic extraction
            trends = spider_service.get_trending_topics(hours=168, limit=5)
            topic = self._extract_generic_topic(trends, category)

        if not topic:
            topic = f"Latest {category.replace('_', ' ').title()} Developments"

        # Trigger content creation
        coordinator = AutonomousContentStudioCoordinator(user=self.user or channel.user)
        result = coordinator._trigger_content_creation({
            'channel_id': str(channel.id),
            'topic': topic
        })

        return {
            'category': category,
            'channel_name': channel_name,
            'topic': topic,
            'creation_result': result,
            'timestamp': timezone.now().isoformat()
        }

    def _extract_finance_topic(self, market_data: Dict) -> Optional[str]:
        """Extract a compelling topic from finance spider data."""
        # Try crypto first
        crypto = market_data.get('crypto', [])
        if crypto and len(crypto) > 0:
            top_crypto = crypto[0]
            if top_crypto.get('change_24h'):
                change = top_crypto.get('change_24h', 0)
                direction = 'Surges' if change > 0 else 'Drops'
                return f"{top_crypto.get('name', 'Crypto')} {direction} {abs(change):.1f}% - Market Analysis"

        # Default finance topic
        return "Weekly Market Roundup: Key Movements and Trends"

    def _extract_tech_topic(self, trends: Dict) -> Optional[str]:
        """Extract a topic from tech trends."""
        discussions = trends.get('discussions', [])
        if discussions:
            top = discussions[0]
            return top.get('title', '')[:80]

        topics = trends.get('topics', [])
        if topics:
            return f"Deep Dive: {topics[0].get('topic', 'Tech Trends').title()}"

        return None

    def _extract_jobs_topic(self, job_data: Dict) -> Optional[str]:
        """Extract a topic from job market data."""
        total = job_data.get('total_found', 0)
        categories = job_data.get('categories', [])

        if categories and len(categories) > 0:
            top_category = categories[0].get('category', 'Tech')
            return f"Hot in {top_category}: {total} New Remote Opportunities This Week"

        return f"Remote Job Market Update: {total} New Opportunities"

    def _extract_generic_topic(self, trends: List, category: str) -> Optional[str]:
        """Extract a topic from generic trending data."""
        if trends and len(trends) > 0:
            top_trend = trends[0]
            topic = top_trend.get('topic', '')
            if topic:
                return f"{category.title()} Spotlight: {topic.title()}"

        return None

    def _full_diversity_check(self) -> Dict[str, Any]:
        """
        Run full diversity analysis and optionally create content for gaps.
        """
        # Step 1: Analyze gaps
        gap_analysis = self._analyze_content_gaps()

        # Step 2: Auto-create content for top priority gaps
        auto_create = []
        max_auto_create = 2  # Limit how many we create in one run

        for gap in gap_analysis['gaps'][:max_auto_create]:
            if gap['priority'] >= 4:  # Only high priority gaps
                logger.info(f"Auto-creating content for {gap['category']} (priority: {gap['priority']})")
                create_result = self._create_content_for_category(gap['category'])
                auto_create.append(create_result)

        return {
            'summary': f"Found {gap_analysis['total_gaps']} content gaps, coverage score: {gap_analysis['coverage_score']}%",
            'gap_analysis': gap_analysis,
            'auto_created': auto_create,
            'auto_create_count': len(auto_create),
            'timestamp': timezone.now().isoformat()
        }

    def get_diversity_report(self) -> Dict[str, Any]:
        """
        Generate a human-readable diversity report.
        """
        spider_data = self._get_spider_data_by_category()
        content_data = self._get_content_by_category()
        gap_analysis = self._analyze_content_gaps()

        report = {
            'title': 'Content Diversity Report',
            'generated_at': timezone.now().isoformat(),
            'coverage_score': gap_analysis['coverage_score'],
            'categories': []
        }

        for category in self.CATEGORY_CHANNELS.keys():
            spider_info = spider_data.get(category, {})
            content_info = content_data.get(category, {})

            status = 'good'
            if category in [g['category'] for g in gap_analysis['gaps']]:
                gap = next(g for g in gap_analysis['gaps'] if g['category'] == category)
                if gap['priority'] >= 4:
                    status = 'critical'
                else:
                    status = 'needs_attention'

            report['categories'].append({
                'name': category.replace('_', ' ').title(),
                'channel': self.CATEGORY_CHANNELS[category],
                'status': status,
                'spider_data_available': spider_info.get('total_items', 0),
                'active_spiders': spider_info.get('spider_count', 0),
                'episodes_this_week': content_info.get('episodes', 0),
                'total_episodes': content_info.get('total_episodes', 0),
            })

        return report

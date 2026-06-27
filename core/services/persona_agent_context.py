"""
Session 790: Persona Agent Context Builder

Provides spider data context for persona agents (agents without Python code)
so they can participate in conversations with real-world intelligence.

Persona agents are defined in load_all_agents_advisors.py and include:
- Income agents (20): Income Builder Pro, Freelance Hunter, etc.
- Career agents (15): Career Path Strategist, Interview Coach Pro, etc.
- Finance agents (12): Personal Finance Manager, Investment Portfolio Manager, etc.
- And 100+ more across business, marketing, AI/ML, creative domains

This service:
1. Maps persona agent types to relevant spider categories
2. Fetches recent spider data for their domain
3. Builds context strings for injection into conversation prompts
4. Enables persona agents to discuss real-world data intelligently
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


# Mapping of persona agent types to spider names/categories
# This enables persona agents to receive relevant real-world data
PERSONA_SPIDER_MAPPINGS = {
    # Income & Freelance agents
    'income': {
        'spiders': ['remoteok', 'weworkremotely', 'adzuna', 'github_jobs', 'flexjobs'],
        'keywords': ['remote', 'freelance', 'gig', 'contract', 'income', 'earning'],
        'description': 'job opportunities, freelance gigs, and income sources',
    },

    # Career Development agents
    'career': {
        'spiders': ['remoteok', 'weworkremotely', 'adzuna', 'hackernews', 'medium'],
        'keywords': ['career', 'job', 'hiring', 'interview', 'resume', 'skills'],
        'description': 'career trends, job market insights, and professional development',
    },

    # Job Search agents
    'job_search': {
        'spiders': ['remoteok', 'weworkremotely', 'adzuna', 'github_jobs', 'hackernews'],
        'keywords': ['hiring', 'job', 'position', 'role', 'opportunity', 'apply'],
        'description': 'job listings, hiring trends, and application insights',
    },

    # Finance & Investment agents
    'finance': {
        'spiders': ['yahoo_finance', 'polygon_finance', 'finnhub', 'coingecko', 'sec_edgar'],
        'keywords': ['market', 'stock', 'investment', 'finance', 'portfolio', 'trading'],
        'description': 'market data, financial news, and investment opportunities',
    },
    'investment': {
        'spiders': ['yahoo_finance', 'polygon_finance', 'finnhub', 'coingecko', 'kalshi'],
        'keywords': ['invest', 'portfolio', 'returns', 'dividend', 'growth', 'value'],
        'description': 'investment opportunities and portfolio strategies',
    },

    # Content & Marketing agents
    'content': {
        'spiders': ['medium', 'substack', 'hackernoon', 'devto', 'youtube'],
        'keywords': ['content', 'article', 'blog', 'video', 'audience', 'engagement'],
        'description': 'content trends, popular topics, and audience engagement',
    },
    'marketing': {
        'spiders': ['medium', 'hackernews', 'producthunt', 'reddit', 'bluesky'],
        'keywords': ['marketing', 'growth', 'viral', 'campaign', 'brand', 'audience'],
        'description': 'marketing trends, growth strategies, and brand insights',
    },
    'social_media': {
        'spiders': ['reddit', 'bluesky', 'youtube', 'hackernews', 'medium'],
        'keywords': ['social', 'viral', 'engagement', 'followers', 'trending'],
        'description': 'social media trends and engagement patterns',
    },

    # Technology & AI agents
    'ai_ml': {
        'spiders': ['huggingface', 'kaggle', 'hackernews', 'devto', 'github'],
        'keywords': ['ai', 'ml', 'model', 'training', 'neural', 'llm', 'gpt'],
        'description': 'AI/ML developments, models, and research breakthroughs',
    },
    'development': {
        'spiders': ['github', 'hackernews', 'devto', 'stackoverflow', 'producthunt'],
        'keywords': ['code', 'developer', 'programming', 'software', 'tech', 'api'],
        'description': 'software development trends and technical innovations',
    },
    'automation': {
        'spiders': ['hackernews', 'producthunt', 'github', 'devto', 'medium'],
        'keywords': ['automate', 'workflow', 'efficiency', 'tool', 'integration'],
        'description': 'automation tools and workflow optimization',
    },

    # Business & Strategy agents
    'business': {
        'spiders': ['techcrunch', 'crunchbase', 'venturebeat', 'business_news', 'hackernews'],
        'keywords': ['startup', 'business', 'company', 'strategy', 'growth', 'market'],
        'description': 'business news, startup trends, and market strategies',
    },
    'startup': {
        'spiders': ['techcrunch', 'crunchbase', 'producthunt', 'venturebeat', 'kickstarter'],
        'keywords': ['startup', 'funding', 'launch', 'venture', 'founder', 'seed'],
        'description': 'startup ecosystem, funding news, and entrepreneurship',
    },
    'consulting': {
        'spiders': ['medium', 'hackernews', 'business_news', 'techcrunch', 'reddit'],
        'keywords': ['consulting', 'advisory', 'strategy', 'client', 'expertise'],
        'description': 'consulting trends and advisory insights',
    },

    # Creative & Design agents
    'creative': {
        'spiders': ['behance', 'dribbble', 'awwwards', 'unsplash', 'producthunt'],
        'keywords': ['design', 'creative', 'visual', 'art', 'ui', 'ux', 'brand'],
        'description': 'design trends, creative inspiration, and visual innovations',
    },
    'writing': {
        'spiders': ['medium', 'substack', 'hackernoon', 'devto', 'reddit'],
        'keywords': ['writing', 'article', 'blog', 'content', 'storytelling'],
        'description': 'writing trends and content creation insights',
    },
    'video': {
        'spiders': ['youtube', 'variety', 'polygon_gaming', 'reddit', 'hackernews'],
        'keywords': ['video', 'youtube', 'streaming', 'creator', 'content'],
        'description': 'video content trends and creator insights',
    },

    # Analytics & Research agents
    'analytics': {
        'spiders': ['kaggle', 'hackernews', 'github', 'devto', 'medium'],
        'keywords': ['data', 'analytics', 'metrics', 'insights', 'visualization'],
        'description': 'data analytics trends and insights',
    },
    'research': {
        'spiders': ['hackernews', 'science', 'kaggle', 'huggingface', 'github'],
        'keywords': ['research', 'study', 'paper', 'findings', 'analysis'],
        'description': 'research developments and academic insights',
    },
    'market': {
        'spiders': ['yahoo_finance', 'polygon_finance', 'techcrunch', 'crunchbase', 'kalshi'],
        'keywords': ['market', 'trend', 'industry', 'sector', 'competition'],
        'description': 'market intelligence and industry trends',
    },

    # Crypto agents
    'crypto': {
        'spiders': ['coingecko', 'etherscan', 'etherscan_api', 'hackernews', 'reddit'],
        'keywords': ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'nft'],
        'description': 'cryptocurrency markets and blockchain developments',
    },
}


class PersonaAgentContextBuilder:
    """
    Builds context for persona agents by fetching relevant spider data
    based on their agent_type.
    """

    def __init__(self):
        self.LegacySpiderData = None
        self._load_models()

    def _load_models(self):
        """Lazy load Django models to avoid import issues."""
        try:
            from core.models_unified_system import LegacySpiderData
            self.LegacySpiderData = LegacySpiderData
        except ImportError:
            logger.warning("Could not import LegacySpiderData model")

    def is_persona_agent(self, agent) -> bool:
        """
        Check if an agent is a persona agent (not a core agent with code).

        Persona agents have agent_type matching PERSONA_SPIDER_MAPPINGS
        but aren't in the AgentRouter's AGENT_MAP.
        """
        try:
            from core.agent_router import AgentRouter
            router = AgentRouter()
            # If the agent name isn't in AGENT_MAP, it's a persona agent
            return agent.name not in router.AGENT_MAP
        except Exception as e:
            logger.debug(f"Could not check agent type: {e}")
            # Fallback: check if agent_type is in persona mappings
            return agent.agent_type in PERSONA_SPIDER_MAPPINGS

    def get_mapping_for_agent(self, agent) -> Optional[Dict]:
        """Get the spider mapping for an agent based on its type."""
        agent_type = getattr(agent, 'agent_type', None)
        if not agent_type:
            # Try to infer from specialization
            agent_type = getattr(agent, 'specialization', None)

        if agent_type and agent_type in PERSONA_SPIDER_MAPPINGS:
            return PERSONA_SPIDER_MAPPINGS[agent_type]

        return None

    def get_spider_data_for_agent(
        self,
        agent,
        hours: int = 48,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent spider data relevant to a persona agent.

        Args:
            agent: The Agent model instance
            hours: How far back to look for data
            limit: Maximum items to return

        Returns:
            List of spider data items with title, summary, source
        """
        if not self.LegacySpiderData:
            return []

        mapping = self.get_mapping_for_agent(agent)
        if not mapping:
            return []

        since = timezone.now() - timedelta(hours=hours)
        spiders = mapping.get('spiders', [])

        # Query spider data
        data = self.LegacySpiderData.objects.filter(
            spider_name__in=spiders,
            created_at__gte=since
        ).order_by('-created_at')[:limit * 3]  # Get more, we'll filter

        results = []
        for item in data:
            extracted = self._extract_item_content(item)
            if extracted:
                results.append(extracted)
                if len(results) >= limit:
                    break

        return results

    def _extract_item_content(self, spider_data) -> Optional[Dict[str, Any]]:
        """Extract readable content from a LegacySpiderData record."""
        content = {
            'source': spider_data.spider_name,
            'title': None,
            'summary': None,
            'url': None,
            'created_at': spider_data.created_at,
        }

        # Try to extract from raw_data
        raw = spider_data.raw_data or {}
        if isinstance(raw, dict):
            # Check for items array (common pattern)
            items = raw.get('items', [])
            if items and isinstance(items, list) and len(items) > 0:
                item = items[0]
                if isinstance(item, dict):
                    content['title'] = item.get('title', '')[:200]
                    content['summary'] = item.get('summary') or item.get('description', '')
                    content['url'] = item.get('url') or item.get('link', '')
            else:
                # Direct fields
                content['title'] = raw.get('title', '')[:200]
                content['summary'] = raw.get('summary') or raw.get('description', '')
                content['url'] = raw.get('url') or raw.get('link', '')

        # Try processed_data as fallback
        if not content['title']:
            proc = spider_data.processed_data or {}
            if isinstance(proc, dict):
                content['title'] = proc.get('title', '')[:200]
                content['summary'] = proc.get('summary', '')

        # Only return if we have meaningful content
        if content['title'] or content['summary']:
            return content

        return None

    def build_context_for_agent(
        self,
        agent,
        topic: str = None,
        hours: int = 48,
        limit: int = 5
    ) -> str:
        """
        Build a context string for a persona agent to use in conversations.

        Args:
            agent: The Agent model instance
            topic: Optional conversation topic for relevance filtering
            hours: How far back to look for data
            limit: Maximum items to include

        Returns:
            Formatted context string for injection into prompts
        """
        mapping = self.get_mapping_for_agent(agent)
        if not mapping:
            return ""

        data_items = self.get_spider_data_for_agent(agent, hours, limit)

        if not data_items:
            return ""

        # Build context string
        domain_desc = mapping.get('description', 'your domain')

        context_parts = [
            f"\n== REAL-WORLD INTELLIGENCE ({domain_desc}) ==",
            f"Recent data relevant to your expertise:",
        ]

        for item in data_items:
            title = item.get('title', 'Untitled')
            source = item.get('source', 'Unknown')
            summary = item.get('summary', '')

            if title:
                context_parts.append(f"\n• [{source}] {title}")
                if summary:
                    # Truncate long summaries
                    summary_text = summary[:200] + "..." if len(summary) > 200 else summary
                    context_parts.append(f"  {summary_text}")

        context_parts.append(
            f"\nUse this data to inform your perspective as {agent.name}."
        )

        return '\n'.join(context_parts)

    def get_knowledge_summary_for_agent(
        self,
        agent,
        hours: int = 168  # 1 week
    ) -> Dict[str, Any]:
        """
        Get a summary of available knowledge for a persona agent.
        Used for creating AgentKnowledgeSource entries.

        Returns:
            Dict with summary, key_insights, data_count
        """
        if not self.LegacySpiderData:
            return {}

        mapping = self.get_mapping_for_agent(agent)
        if not mapping:
            return {}

        since = timezone.now() - timedelta(hours=hours)
        spiders = mapping.get('spiders', [])

        # Get data count
        data_count = self.LegacySpiderData.objects.filter(
            spider_name__in=spiders,
            created_at__gte=since
        ).count()

        # Get recent items for insights
        recent_items = self.get_spider_data_for_agent(agent, hours=48, limit=10)

        # Extract key insights (titles of recent items)
        key_insights = [
            item.get('title', '')[:100]
            for item in recent_items
            if item.get('title')
        ][:5]

        return {
            'summary': f"Aggregated {data_count} data points from {', '.join(spiders[:3])} "
                      f"covering {mapping.get('description', 'domain expertise')}.",
            'key_insights': key_insights,
            'data_count': data_count,
            'spiders': spiders,
            'domain': mapping.get('description', ''),
        }


# Singleton instance
_persona_context_builder = None

def get_persona_context_builder() -> PersonaAgentContextBuilder:
    """Get or create the persona context builder singleton."""
    global _persona_context_builder
    if _persona_context_builder is None:
        _persona_context_builder = PersonaAgentContextBuilder()
    return _persona_context_builder

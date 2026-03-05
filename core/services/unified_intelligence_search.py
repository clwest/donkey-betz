"""
Unified Intelligence Search Service
====================================

Session 303: Unified search across SpiderData AND BusinessResearchResult.

This service provides a single interface to search:
1. Spider data (real-time web crawls)
2. Previous business research (competitor analysis, customer research)

This enables cumulative intelligence where new research builds on previous findings.

Usage:
    from core.services.unified_intelligence_search import UnifiedIntelligenceSearch

    search = UnifiedIntelligenceSearch()

    # Search both sources
    results = search.unified_search("AI content generation competitors")

    # Get context for agent prompts
    context = search.get_research_context("coffee roasting business")

    # Trigger fresh spider data before research
    search.refresh_spiders_for_query("AI tools")
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class UnifiedSearchResult:
    """Unified result from both spider data and business research."""
    title: str
    description: str
    url: str
    source: str  # Spider name or "BusinessResearch"
    source_type: str  # "spider" or "research"
    similarity: float
    category: str
    found_at: str
    tags: List[str] = field(default_factory=list)
    research_type: str = ""  # "competitor" or "customer" for research results
    market_topic: str = ""  # For grouping related research


class UnifiedIntelligenceSearch:
    """
    Unified search across spider data and business research.

    Combines:
    - SpiderSemanticSearch for real-time crawl data
    - BusinessResearchResult.semantic_search for historical analysis

    Benefits:
    - New research automatically references past research
    - Agents can see both raw data AND analyzed insights
    - Cumulative intelligence builds over time
    """

    def __init__(self):
        self._spider_search = None
        self._openai_client = None

    @property
    def spider_search(self):
        """Lazy-load spider semantic search."""
        if self._spider_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._spider_search = get_spider_semantic_search()
        return self._spider_search

    @property
    def openai_client(self):
        """Lazy-load OpenAI client for embeddings."""
        if self._openai_client is None:
            from django.conf import settings
            import openai
            api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
            if api_key:
                self._openai_client = openai.OpenAI(api_key=api_key)
        return self._openai_client

    def unified_search(
        self,
        query: str,
        include_spiders: bool = True,
        include_research: bool = True,
        spider_hours: int = 168,  # 7 days for spider data
        research_limit: int = 10,
        spider_limit: int = 20,
        min_similarity: float = 0.3
    ) -> List[UnifiedSearchResult]:
        """
        Search across both spider data and business research.

        Args:
            query: Search query
            include_spiders: Include spider data in results
            include_research: Include business research in results
            spider_hours: How far back to look for spider data
            research_limit: Max research results
            spider_limit: Max spider results
            min_similarity: Minimum similarity threshold

        Returns:
            Combined and ranked list of UnifiedSearchResult
        """
        results = []

        # Search spider data
        if include_spiders:
            spider_results = self._search_spider_data(
                query, spider_hours, spider_limit, min_similarity
            )
            results.extend(spider_results)

        # Search business research
        if include_research:
            research_results = self._search_business_research(
                query, research_limit
            )
            results.extend(research_results)

        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)

        logger.info(
            f"Unified search: query='{query[:50]}', "
            f"spider_results={len([r for r in results if r.source_type == 'spider'])}, "
            f"research_results={len([r for r in results if r.source_type == 'research'])}"
        )

        return results

    def _search_spider_data(
        self,
        query: str,
        hours: int,
        limit: int,
        min_similarity: float
    ) -> List[UnifiedSearchResult]:
        """Search spider data and convert to UnifiedSearchResult."""
        try:
            spider_results = self.spider_search.semantic_search(
                query=query,
                hours=hours,
                limit=limit,
                min_similarity=min_similarity
            )

            return [
                UnifiedSearchResult(
                    title=r.title,
                    description=r.description,
                    url=r.url,
                    source=r.source,
                    source_type="spider",
                    similarity=r.similarity,
                    category=r.category,
                    found_at=r.found_at,
                    tags=r.tags or []
                )
                for r in spider_results
            ]
        except Exception as e:
            logger.error(f"Spider search failed: {e}")
            return []

    def _search_business_research(
        self,
        query: str,
        limit: int
    ) -> List[UnifiedSearchResult]:
        """Search BusinessResearchResult and convert to UnifiedSearchResult."""
        try:
            from core.models_unified_system import BusinessResearchResult

            research_results = BusinessResearchResult.semantic_search(
                query=query,
                limit=limit
            )

            return [
                UnifiedSearchResult(
                    title=f"{research.get_research_type_display()}: {research.query[:50]}...",
                    description=research.analysis[:300] if research.analysis else "",
                    url="",  # Research doesn't have URLs
                    source="BusinessResearch",
                    source_type="research",
                    similarity=score,
                    category=research.research_type,
                    found_at=research.created_at.isoformat(),
                    tags=[],
                    research_type=research.research_type,
                    market_topic=research.market_topic or ""
                )
                for research, score in research_results
                if score >= 0.3  # Minimum threshold
            ]
        except Exception as e:
            logger.error(f"Business research search failed: {e}")
            return []

    def get_research_context(
        self,
        query: str,
        max_spider_items: int = 5,
        max_research_items: int = 3,
        max_chars: int = 2000
    ) -> str:
        """
        Get formatted context from both sources for agent prompts.

        This is used to inject prior knowledge into agent prompts.

        Args:
            query: The user's query/topic
            max_spider_items: Max spider results to include
            max_research_items: Max research results to include
            max_chars: Maximum total characters

        Returns:
            Formatted context string for injection into prompts
        """
        results = self.unified_search(
            query=query,
            spider_limit=max_spider_items,
            research_limit=max_research_items,
            min_similarity=0.35
        )

        if not results:
            return ""

        sections = []
        total_chars = 0

        # Group by source type
        spider_results = [r for r in results if r.source_type == "spider"]
        research_results = [r for r in results if r.source_type == "research"]

        # Add previous research first (more valuable context)
        if research_results:
            research_section = "## Previous Research Findings\n"
            for r in research_results[:max_research_items]:
                item = f"- **{r.research_type.title()}** ({r.market_topic or 'General'}): {r.description[:200]}...\n"
                if total_chars + len(item) < max_chars:
                    research_section += item
                    total_chars += len(item)
            sections.append(research_section)

        # Add spider data
        if spider_results:
            spider_section = "## Current Market Intelligence\n"
            for r in spider_results[:max_spider_items]:
                item = f"- [{r.source}] {r.title}"
                if r.description:
                    item += f": {r.description[:100]}..."
                item += "\n"
                if total_chars + len(item) < max_chars:
                    spider_section += item
                    total_chars += len(item)
            sections.append(spider_section)

        return "\n".join(sections) if sections else ""

    def get_related_research(
        self,
        market_topic: str,
        research_type: str = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get related business research for a market topic.

        Useful for cumulative intelligence - new research can reference past work.

        Args:
            market_topic: The market/topic to find research for
            research_type: Optional filter ('competitor' or 'customer')
            limit: Max results

        Returns:
            List of related research as dicts
        """
        try:
            from core.models_unified_system import BusinessResearchResult

            queryset = BusinessResearchResult.objects.filter(
                market_topic__icontains=market_topic
            )

            if research_type:
                queryset = queryset.filter(research_type=research_type)

            results = queryset.order_by('-created_at')[:limit]

            return [
                {
                    'id': str(r.id),
                    'type': r.research_type,
                    'query': r.query,
                    'market_topic': r.market_topic,
                    'analysis_preview': r.analysis[:200] if r.analysis else "",
                    'created_at': r.created_at.isoformat(),
                    'data_points': r.data_points_analyzed,
                    'has_embedding': bool(r.embedding)
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Get related research failed: {e}")
            return []

    def refresh_spiders_for_query(
        self,
        query: str,
        categories: List[str] = None
    ) -> Dict[str, Any]:
        """
        Trigger spider network to fetch fresh data related to query.

        This should be called BEFORE running business research to ensure
        the most up-to-date data is available.

        Args:
            query: The research query (used to determine relevant categories)
            categories: Optional specific categories to refresh

        Returns:
            Dict with refresh status and triggered spiders
        """
        from core.tasks import run_spider_by_category

        # Map query keywords to spider categories
        category_keywords = {
            'tech': ['ai', 'software', 'saas', 'app', 'technology', 'startup', 'tech'],
            'financial': ['finance', 'investment', 'stock', 'crypto', 'money', 'pricing'],
            'jobs': ['job', 'career', 'hiring', 'remote', 'work', 'freelance'],
            'news': ['news', 'trending', 'latest', 'breaking', 'announcement'],
            'creative': ['design', 'art', 'creative', 'visual', 'graphic'],
            'community': ['reddit', 'forum', 'community', 'discussion', 'review'],
        }

        # Determine categories from query
        query_lower = query.lower()
        triggered_categories = []

        if categories:
            triggered_categories = categories
        else:
            # Auto-detect categories from query
            for category, keywords in category_keywords.items():
                if any(kw in query_lower for kw in keywords):
                    triggered_categories.append(category)

            # Default to tech + news if no matches
            if not triggered_categories:
                triggered_categories = ['tech', 'news']

        # Limit to 3 categories max
        triggered_categories = triggered_categories[:3]

        # Trigger spiders asynchronously
        tasks_triggered = []
        for category in triggered_categories:
            try:
                run_spider_by_category.delay(category, execution_mode='scheduled')
                tasks_triggered.append(category)
                logger.info(f"Triggered spider refresh for category: {category}")
            except Exception as e:
                logger.error(f"Failed to trigger spider for {category}: {e}")

        return {
            'triggered': True,
            'categories': tasks_triggered,
            'query': query[:100],
            'message': f"Triggered {len(tasks_triggered)} spider categories for fresh data"
        }

    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Get statistics about available intelligence data."""
        from core.models_unified_system import SpiderData, BusinessResearchResult

        since_24h = timezone.now() - timedelta(hours=24)
        since_7d = timezone.now() - timedelta(days=7)

        spider_stats = {
            'total': SpiderData.objects.count(),
            'last_24h': SpiderData.objects.filter(created_at__gte=since_24h).count(),
            'last_7d': SpiderData.objects.filter(created_at__gte=since_7d).count(),
        }

        research_stats = {
            'total': BusinessResearchResult.objects.count(),
            'competitor': BusinessResearchResult.objects.filter(research_type='competitor').count(),
            'customer': BusinessResearchResult.objects.filter(research_type='customer').count(),
            'with_embeddings': BusinessResearchResult.objects.exclude(
                embedding__isnull=True
            ).exclude(embedding=[]).count(),
        }

        # Latest entries
        latest_spider = SpiderData.objects.order_by('-created_at').first()
        latest_research = BusinessResearchResult.objects.order_by('-created_at').first()

        return {
            'spider_data': spider_stats,
            'business_research': research_stats,
            'latest_spider': latest_spider.created_at.isoformat() if latest_spider else None,
            'latest_research': latest_research.created_at.isoformat() if latest_research else None,
        }


# Global instance
_unified_search: Optional[UnifiedIntelligenceSearch] = None


def get_unified_intelligence_search() -> UnifiedIntelligenceSearch:
    """Get the global unified intelligence search instance."""
    global _unified_search
    if _unified_search is None:
        _unified_search = UnifiedIntelligenceSearch()
    return _unified_search

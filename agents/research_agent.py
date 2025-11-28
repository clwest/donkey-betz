"""
Research Agent - Unified Research Specialist
=============================================

Session 203: Created as Phase 3 of Agent Architecture Refactor
Session 255: Added Time Travel Debugging for decision tracking

This agent provides unified research capabilities by combining:
1. Web search (Serper/Google) for real-time web results
2. Spider network (40+ specialized spiders) for domain-specific intelligence
3. Content analysis for deep research synthesis
4. TIME TRAVEL DEBUGGING (Session 255)

The ResearchAgent makes the 40+ spiders invisible infrastructure - the user
just asks for research and gets comprehensive results from multiple sources.

Example:
    # Simple usage
    agent = ResearchAgent(user=request.user)
    result = agent.search(query="AI logo design trends 2024")
    # Returns combined results from web search + design spiders + content spiders

    # Domain-specific research
    result = agent.research_topic(
        topic="cryptocurrency market trends",
        sources=['spiders', 'web'],
        depth='comprehensive'
    )
"""

from __future__ import annotations

import logging
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from agents.time_travel_mixin import TimeTravelMixin

logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    """Result from a research operation."""
    success: bool
    query: str
    sources_used: List[str]
    web_results: List[Dict[str, Any]]
    spider_results: List[Dict[str, Any]]
    synthesis: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'query': self.query,
            'sources_used': self.sources_used,
            'web_results': self.web_results,
            'spider_results': self.spider_results,
            'synthesis': self.synthesis,
            'error': self.error,
            'total_results': len(self.web_results) + len(self.spider_results)
        }


class ResearchAgent(TimeTravelMixin):
    """
    Unified research specialist that combines web search with spider intelligence.

    This agent makes the spider network invisible to the user - they just ask
    for research and get comprehensive, multi-source results.

    Session 255: Inherits TimeTravelMixin for decision tracking.
    """

    # Spider categories mapped to research domains
    DOMAIN_SPIDERS = {
        'design': ['ninetyninedesigns', 'dribbble', 'behance'],
        'tech': ['huggingface', 'kaggle', 'github_jobs', 'stackoverflow_jobs', 'hackernews'],
        'financial': ['financial', 'coingecko', 'yahoo_finance', 'market_data'],
        'freelance': ['toptal', 'guru', 'peopleperhour', 'flexjobs', 'remoteok'],
        'content': ['medium', 'substack', 'gumroad', 'producthunt'],
        'news': ['news_harvester'],
        'social': ['social_sentiment'],
        'innovation': ['innovation'],
        'legal': ['courtlistener', 'justia', 'findlaw', 'lii'],
    }

    # Keywords that trigger specific spider domains
    KEYWORD_TRIGGERS = {
        'logo': ['design'],
        'design': ['design'],
        'creative': ['design', 'content'],
        'crypto': ['financial'],
        'bitcoin': ['financial'],
        'stock': ['financial'],
        'finance': ['financial'],
        'trading': ['financial'],
        'ai': ['tech', 'innovation'],
        'machine learning': ['tech', 'innovation'],
        'freelance': ['freelance'],
        'job': ['freelance', 'tech'],
        'remote work': ['freelance'],
        'content': ['content'],
        'blog': ['content'],
        'legal': ['legal'],
        'law': ['legal'],
        'court': ['legal'],
        'trend': ['social', 'news', 'innovation'],
        'social media': ['social', 'content'],
    }

    def __init__(self, user=None, project_id: Optional[str] = None):
        """
        Initialize the ResearchAgent.

        Args:
            user: Django user object
            project_id: Optional project ID for context
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = 'ResearchAgent'  # Session 255: Required for TimeTravelMixin
        self._spider_registry = None
        self._intelligence_service = None

    @property
    def intelligence_service(self):
        """Lazy load spider intelligence service - Session 208."""
        if self._intelligence_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._intelligence_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
                self._intelligence_service = None
        return self._intelligence_service

    @property
    def spider_registry(self):
        """Lazy load spider registry."""
        if self._spider_registry is None:
            try:
                from ai_core.spiders.spider_registry import get_spider_registry
                self._spider_registry = get_spider_registry()
            except ImportError:
                logger.warning("Spider registry not available")
                self._spider_registry = None
        return self._spider_registry

    def search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_web_results: int = 5,
        max_spider_results: int = 10
    ) -> Dict[str, Any]:
        """
        Perform a unified search across web and spider sources.

        Args:
            query: Search query
            sources: List of sources to use ['web', 'spiders'] - defaults to both
            max_web_results: Maximum web results to return
            max_spider_results: Maximum spider results to return

        Returns:
            Combined search results from all sources
        """
        logger.info(f"ResearchAgent searching: {query}")

        # Session 255: Time Travel Debugging - wrap in session
        with self.time_travel_session(
            task_type="research",
            task_description=f"Search: {query[:50]}...",
            input_data={'query': query, 'sources': sources, 'max_web': max_web_results, 'max_spider': max_spider_results}
        ):
            sources = sources or ['web', 'spiders']
            web_results = []
            spider_results = []
            sources_used = []

            # Session 255: Record query analysis decision
            self.record_decision(
                decision_type="analysis",
                action=f"Analyzing research query: {query[:50]}...",
                reasoning="Parsing query to determine relevant sources",
                context={'query_length': len(query), 'sources_requested': sources},
                confidence=0.9,
                thoughts=[
                    f"User wants to research: {query[:30]}...",
                    f"Sources to use: {sources}",
                    f"Max results: web={max_web_results}, spider={max_spider_results}"
                ]
            )

            # Web search
            if 'web' in sources:
                # Session 255: Record web search decision
                self.record_decision(
                    decision_type="source_selection",
                    action="Querying web search (Serper/Google)",
                    reasoning="Web search provides real-time information",
                    alternatives=["Skip web search", "Use different search engine"],
                    confidence=0.85
                )
                web_data = self._search_web(query, max_results=max_web_results)
                if web_data.get('success'):
                    web_results = web_data.get('results', [])
                    sources_used.append('web_search')
                    logger.info(f"  Web search returned {len(web_results)} results")
                    self.record_thought(f"Web search returned {len(web_results)} results", "observation", 0.7)

            # Spider intelligence
            if 'spiders' in sources:
                # Session 255: Record spider search decision
                relevant_domains = self._identify_relevant_domains(query)
                self.record_decision(
                    decision_type="source_selection",
                    action=f"Querying spider network: {relevant_domains or 'general'}",
                    reasoning="Spider network provides domain-specific intelligence",
                    alternatives=["Skip spider intelligence", "Query different domains"],
                    context={'relevant_domains': relevant_domains},
                    confidence=0.8
                )
                spider_data = self._search_spiders(query, max_results=max_spider_results)
                spider_results = spider_data.get('results', [])
                sources_used.extend(spider_data.get('spiders_queried', []))
                logger.info(f"  Spider search returned {len(spider_results)} results")
                self.record_thought(f"Spider network returned {len(spider_results)} results", "observation", 0.7)

            result = ResearchResult(
                success=True,
                query=query,
                sources_used=sources_used,
                web_results=web_results,
                spider_results=spider_results
            )

            # Session 255: Record completion
            total_results = len(web_results) + len(spider_results)
            self.record_decision(
                decision_type="research_complete",
                action=f"Research complete: {total_results} total results",
                reasoning="All sources queried successfully",
                context={'web_count': len(web_results), 'spider_count': len(spider_results), 'sources_used': sources_used},
                confidence=0.95
            )
            self.mark_decision_outcome(True, f"Found {total_results} results from {len(sources_used)} sources")

            return result.to_dict()

    def research_topic(
        self,
        topic: str,
        depth: str = 'standard',
        domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive research on a topic.

        Args:
            topic: Research topic
            depth: 'quick', 'standard', or 'comprehensive'
            domains: Specific domains to focus on (e.g., ['tech', 'financial'])

        Returns:
            Comprehensive research results with synthesis
        """
        logger.info(f"ResearchAgent researching topic: {topic} (depth={depth})")

        # Determine research parameters based on depth
        if depth == 'quick':
            max_web = 3
            max_spider = 5
        elif depth == 'comprehensive':
            max_web = 10
            max_spider = 20
        else:  # standard
            max_web = 5
            max_spider = 10

        # Get base search results
        results = self.search(
            query=topic,
            max_web_results=max_web,
            max_spider_results=max_spider
        )

        # If domains specified, focus spider results
        if domains:
            focused_spider_results = self._get_domain_intelligence(topic, domains)
            results['spider_results'].extend(focused_spider_results)
            results['sources_used'].extend([f"domain:{d}" for d in domains])

        # Synthesize findings for comprehensive research
        if depth == 'comprehensive' and results.get('web_results') or results.get('spider_results'):
            results['synthesis'] = self._synthesize_findings(
                topic=topic,
                web_results=results.get('web_results', []),
                spider_results=results.get('spider_results', [])
            )

        return results

    def get_domain_intelligence(
        self,
        domain: str,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get intelligence from a specific domain's spiders.

        Args:
            domain: Domain name (e.g., 'design', 'tech', 'financial')
            query: Optional query to filter results

        Returns:
            Intelligence from domain-specific spiders
        """
        if domain not in self.DOMAIN_SPIDERS:
            return {
                'success': False,
                'error': f"Unknown domain: {domain}. Available: {list(self.DOMAIN_SPIDERS.keys())}"
            }

        results = self._get_domain_intelligence(query or domain, [domain])

        return {
            'success': True,
            'domain': domain,
            'spiders_used': self.DOMAIN_SPIDERS[domain],
            'results': results,
            'result_count': len(results)
        }

    def list_available_sources(self) -> Dict[str, Any]:
        """
        List all available research sources.

        Returns:
            Dictionary of available sources and their status
        """
        sources = {
            'web_search': {
                'type': 'web',
                'provider': 'Serper/Google',
                'status': 'active' if os.getenv('SERPER_API_KEY') else 'no_api_key'
            },
            'spider_domains': {},
            'spider_count': 0
        }

        # Get spider information
        if self.spider_registry:
            spider_count = self.spider_registry.get_spider_count()
            sources['spider_count'] = spider_count.get('total', 0)
            sources['active_spiders'] = spider_count.get('active', 0)
            sources['spider_categories'] = spider_count.get('by_category', {})

            # Map domains
            for domain, spider_names in self.DOMAIN_SPIDERS.items():
                sources['spider_domains'][domain] = {
                    'spiders': spider_names,
                    'available': len([s for s in spider_names if s in self.spider_registry.spider_classes])
                }

        return sources

    # Private methods

    def _search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using Serper API.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Web search results
        """
        try:
            serper_key = os.getenv('SERPER_API_KEY')
            if not serper_key:
                logger.warning("Serper API key not configured")
                return {'success': False, 'error': 'Serper API key not configured'}

            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": serper_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": max_results
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            results = []
            organic = data.get('organic', [])
            for item in organic[:max_results]:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'web_search'
                })

            return {
                'success': True,
                'results': results,
                'query': query
            }

        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {'success': False, 'error': str(e)}

    def _search_spiders(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search spider intelligence based on query.

        Session 208: Now uses SpiderIntelligenceService for database queries.

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Spider intelligence results
        """
        results = []
        spiders_queried = []

        # Session 208: Use SpiderIntelligenceService for real database queries
        if self.intelligence_service:
            try:
                # Get insights relevant to the prompt
                insights = self.intelligence_service.get_insights_for_prompt(query, limit=max_results)

                # Add trending topics
                if insights.get('relevant_trends'):
                    for trend in insights['relevant_trends'][:5]:
                        results.append({
                            'title': trend.get('topic', ''),
                            'type': 'trending_topic',
                            'mentions': trend.get('count', 0),
                            'source': 'spider_intelligence',
                            'domain': 'trends'
                        })
                        spiders_queried.append('trending_analysis')

                # Add market data if available
                if insights.get('market_data'):
                    market = insights['market_data']
                    for crypto in market.get('crypto', [])[:3]:
                        results.append({
                            'title': f"{crypto.get('name', '')} ({crypto.get('symbol', '')})",
                            'price': crypto.get('price'),
                            'change_24h': crypto.get('change_24h'),
                            'type': 'market_data',
                            'source': 'spider_intelligence',
                            'domain': 'financial'
                        })
                        spiders_queried.append('coingecko')

                # Add related discussions
                if insights.get('related_discussions'):
                    for discussion in insights['related_discussions'][:5]:
                        results.append({
                            'title': discussion.get('title', ''),
                            'url': discussion.get('url', ''),
                            'score': discussion.get('score', 0),
                            'type': 'discussion',
                            'source': discussion.get('source', 'spider_intelligence'),
                            'domain': 'tech'
                        })
                        spiders_queried.append(discussion.get('source', 'hackernews'))

                # Add job market data if relevant
                if insights.get('job_market'):
                    jobs = insights['job_market']
                    for job in jobs.get('sample_jobs', [])[:3]:
                        results.append({
                            'title': job.get('title', ''),
                            'company': job.get('company', ''),
                            'location': job.get('location', ''),
                            'type': 'job_listing',
                            'source': job.get('source', 'spider_intelligence'),
                            'domain': 'jobs'
                        })
                        spiders_queried.append(job.get('source', 'weworkremotely'))

                # Add related content from search
                if insights.get('related_content'):
                    for content in insights['related_content'][:5]:
                        results.append({
                            'title': content.get('title', ''),
                            'description': content.get('description', ''),
                            'url': content.get('url', ''),
                            'type': 'related_content',
                            'source': content.get('source', 'spider_intelligence'),
                            'domain': content.get('category', 'general'),
                            'relevance': content.get('relevance', 0)
                        })
                        spiders_queried.append(content.get('source', 'spider_search'))

                logger.info(f"  SpiderIntelligenceService returned {len(results)} results")

            except Exception as e:
                logger.error(f"SpiderIntelligenceService error: {e}")
                # Fall back to legacy method
                results = self._search_spiders_legacy(query, max_results)

        else:
            # Fall back to legacy spider domain querying
            results = self._search_spiders_legacy(query, max_results)

        # Limit results
        results = results[:max_results]

        return {
            'results': results,
            'spiders_queried': list(set(spiders_queried)),
            'domains_searched': list(set(r.get('domain', 'general') for r in results))
        }

    def _search_spiders_legacy(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Legacy spider search method (fallback).

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            Spider intelligence results
        """
        results = []

        # Determine which spider domains are relevant
        relevant_domains = self._identify_relevant_domains(query)

        if not relevant_domains:
            # Default to general purpose spiders
            relevant_domains = ['innovation', 'news', 'content']

        logger.info(f"  Querying spider domains (legacy): {relevant_domains}")

        # Get spider data from relevant domains
        for domain in relevant_domains:
            domain_results = self._query_spider_domain(domain, query)
            results.extend(domain_results)

        return results[:max_results]

    def _identify_relevant_domains(self, query: str) -> List[str]:
        """
        Identify which spider domains are relevant for a query.

        Args:
            query: Search query

        Returns:
            List of relevant domain names
        """
        query_lower = query.lower()
        relevant_domains = set()

        for keyword, domains in self.KEYWORD_TRIGGERS.items():
            if keyword in query_lower:
                relevant_domains.update(domains)

        return list(relevant_domains)

    def _query_spider_domain(self, domain: str, query: str) -> List[Dict[str, Any]]:
        """
        Query spiders in a specific domain.

        Args:
            domain: Domain name
            query: Search query

        Returns:
            Results from domain spiders
        """
        results = []

        if not self.spider_registry:
            return results

        spider_names = self.DOMAIN_SPIDERS.get(domain, [])

        for spider_name in spider_names:
            try:
                spider_config = self.spider_registry.get_spider_config(spider_name)

                if spider_config.get('placeholder', False):
                    # Skip placeholder spiders, use mock data instead
                    continue

                # Try to get cached spider data from Redis
                spider_data = self._get_spider_cache(spider_name, query)

                if spider_data:
                    for item in spider_data:
                        item['source'] = f"spider:{spider_name}"
                        item['domain'] = domain
                        results.append(item)

            except Exception as e:
                logger.warning(f"Error querying spider {spider_name}: {e}")
                continue

        return results

    def _get_spider_cache(self, spider_name: str, query: str) -> List[Dict[str, Any]]:
        """
        Get cached spider data from Redis.

        Args:
            spider_name: Name of the spider
            query: Search query for filtering

        Returns:
            Cached spider data
        """
        try:
            import redis
            import json

            redis_client = redis.Redis(host='localhost', port=6379, db=0)

            # Check for recent spider intelligence
            cache_key = f"spider_intelligence:{spider_name}"
            cached_data = redis_client.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
                # Filter results by query relevance
                query_lower = query.lower()
                relevant = []
                for item in data.get('items', []):
                    item_text = str(item).lower()
                    if any(word in item_text for word in query_lower.split()):
                        relevant.append(item)
                return relevant

        except Exception as e:
            logger.debug(f"Redis cache not available: {e}")

        return []

    def _get_domain_intelligence(self, query: str, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Get intelligence from specific domains.

        Args:
            query: Search query
            domains: List of domains to query

        Returns:
            Combined domain intelligence
        """
        results = []

        for domain in domains:
            domain_results = self._query_spider_domain(domain, query)
            results.extend(domain_results)

        return results

    def _synthesize_findings(
        self,
        topic: str,
        web_results: List[Dict[str, Any]],
        spider_results: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesize research findings into a summary.

        Args:
            topic: Research topic
            web_results: Web search results
            spider_results: Spider intelligence results

        Returns:
            Synthesis summary
        """
        # Build a simple synthesis
        synthesis_parts = [f"Research Summary for: {topic}"]

        if web_results:
            synthesis_parts.append(f"\nWeb Sources ({len(web_results)} results):")
            for i, result in enumerate(web_results[:3], 1):
                synthesis_parts.append(f"  {i}. {result.get('title', 'Untitled')}")

        if spider_results:
            # Group by source
            by_domain = {}
            for result in spider_results:
                domain = result.get('domain', 'general')
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(result)

            synthesis_parts.append(f"\nSpider Intelligence ({len(spider_results)} items):")
            for domain, items in by_domain.items():
                synthesis_parts.append(f"  - {domain}: {len(items)} items")

        return "\n".join(synthesis_parts)


# Convenience function
def search(query: str, user=None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for quick research.

    Args:
        query: Search query
        user: Optional user context
        **kwargs: Additional arguments for ResearchAgent.search()

    Returns:
        Research results
    """
    agent = ResearchAgent(user=user)
    return agent.search(query, **kwargs)


__all__ = [
    'ResearchAgent',
    'ResearchResult',
    'search'
]

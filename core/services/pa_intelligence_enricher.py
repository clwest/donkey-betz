"""
Session 565: PA Intelligence Enricher

Enriches Personal Assistant context with platform intelligence before generating responses.
This bridges the gap between 3,345+ knowledge entries and user queries.

The PA can now answer questions informed by:
- Agent knowledge (what agents have learned)
- Expert agents (who knows about this topic)
- High-value dreams (actionable ideas from agents)
- Canonical policies (boardroom decisions)
- Spider trends (recent discoveries from data network)
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from core.models_unified_system import (
    AgentDream,
    AgentDecisionSummary,
)
from core.services.intelligence_query import IntelligenceQueryService
from core.services.spider_intelligence import SpiderIntelligenceService

logger = logging.getLogger(__name__)


class PAIntelligenceEnricher:
    """
    Session 565: Enriches PA context with platform intelligence.

    This service queries multiple intelligence sources and formats them
    for injection into PA prompts, enabling context-aware responses.
    """

    # Intent classification keywords
    TREND_KEYWORDS = ['trending', 'trend', 'popular', 'hot', 'latest', 'news', 'market']
    STRATEGY_KEYWORDS = ['strategy', 'approach', 'plan', 'best', 'should', 'how to build', 'recommend']
    CREATIVE_KEYWORDS = ['create', 'make', 'design', 'generate', 'build', 'develop']
    TECHNICAL_KEYWORDS = ['code', 'implement', 'fix', 'debug', 'error', 'api', 'database']

    def __init__(self, config: dict = None):
        """
        Initialize the enricher with optional configuration.

        Args:
            config: Optional dict with settings:
                - include_knowledge: bool (default True)
                - include_dreams: bool (default True)
                - include_policies: bool (default True)
                - include_trends: bool (default True)
                - max_context_chars: int (default 2000)
        """
        self.config = config or {}
        self.include_knowledge = self.config.get('include_knowledge', True)
        self.include_dreams = self.config.get('include_dreams', True)
        self.include_policies = self.config.get('include_policies', True)
        self.include_trends = self.config.get('include_trends', True)
        self.max_context_chars = self.config.get('max_context_chars', 2000)

        self.intelligence_service = IntelligenceQueryService()
        self.spider_service = SpiderIntelligenceService()
        self.logger = logging.getLogger(f"{__name__}.PAIntelligenceEnricher")

    def enrich_context(self, message: str, user_context: dict = None) -> dict:
        """
        Query platform intelligence relevant to the user's message.

        Args:
            message: User's message to the PA
            user_context: Optional user context (preferences, active project, etc.)

        Returns:
            Dict with:
                - knowledge: List of relevant AgentKnowledgeSource entries
                - experts: List of expert agents for this topic
                - dreams: List of high-value dreams (if relevant)
                - policies: List of canonical decisions (if relevant)
                - spider_trends: List of recent spider discoveries
                - attribution: Human-readable source attribution
                - context_text: Formatted text for prompt injection
                - metadata: Dict with counts and source info for UI
        """
        try:
            # Classify the message intent
            intent = self._classify_intent(message)
            self.logger.info(f"Classified intent: {intent} for message: {message[:50]}...")

            # Initialize result structure
            result = {
                'knowledge': [],
                'experts': [],
                'dreams': [],
                'policies': [],
                'spider_trends': [],
                'attribution': '',
                'context_text': '',
                'metadata': {
                    'knowledge_count': 0,
                    'experts_count': 0,
                    'dreams_count': 0,
                    'policies_count': 0,
                    'trends_count': 0,
                    'intent': intent,
                    'spider_sources': []
                }
            }

            # Extract main topic from message
            topic = self._extract_topic(message)

            # Query knowledge based on intent
            if self.include_knowledge:
                knowledge_result = self._query_knowledge(topic, intent)
                result['knowledge'] = knowledge_result.get('entries', [])
                result['experts'] = knowledge_result.get('experts', [])
                result['metadata']['knowledge_count'] = len(result['knowledge'])
                result['metadata']['experts_count'] = len(result['experts'])

            # Query high-value dreams (for creative/strategy intents)
            if self.include_dreams and intent in ['strategy', 'creative', 'question']:
                result['dreams'] = self._query_dreams(topic, limit=3)
                result['metadata']['dreams_count'] = len(result['dreams'])

            # Query canonical policies (for strategy/technical intents)
            if self.include_policies and intent in ['strategy', 'technical']:
                result['policies'] = self._query_policies(topic)
                result['metadata']['policies_count'] = len(result['policies'])

            # Query spider trends (for trend/strategy/question intents)
            if self.include_trends and intent in ['trend', 'strategy', 'question']:
                trends_result = self._query_spider_trends(topic, intent)
                result['spider_trends'] = trends_result.get('trends', [])
                result['metadata']['trends_count'] = len(result['spider_trends'])
                result['metadata']['spider_sources'] = trends_result.get('sources', [])

            # Build formatted context and attribution
            result['context_text'] = self._format_context(result, intent)
            result['attribution'] = self._build_attribution(result)

            self.logger.info(
                f"Enrichment complete: {result['metadata']['knowledge_count']} knowledge, "
                f"{result['metadata']['experts_count']} experts, "
                f"{result['metadata']['dreams_count']} dreams, "
                f"{result['metadata']['policies_count']} policies, "
                f"{result['metadata']['trends_count']} trends"
            )

            return result

        except Exception as e:
            self.logger.error(f"Error enriching context: {e}", exc_info=True)
            return {
                'knowledge': [],
                'experts': [],
                'dreams': [],
                'policies': [],
                'spider_trends': [],
                'attribution': '',
                'context_text': '',
                'metadata': {'error': str(e)},
                'error': str(e)
            }

    def _classify_intent(self, message: str) -> str:
        """
        Classify the user's message intent to determine which intelligence to query.

        Returns one of: 'trend', 'strategy', 'creative', 'technical', 'question'
        """
        message_lower = message.lower()

        # Check for trend-related queries
        if any(kw in message_lower for kw in self.TREND_KEYWORDS):
            return 'trend'

        # Check for strategy/planning queries
        if any(kw in message_lower for kw in self.STRATEGY_KEYWORDS):
            return 'strategy'

        # Check for creative/creation requests
        if any(kw in message_lower for kw in self.CREATIVE_KEYWORDS):
            return 'creative'

        # Check for technical queries
        if any(kw in message_lower for kw in self.TECHNICAL_KEYWORDS):
            return 'technical'

        # Default to general question
        return 'question'

    def _extract_topic(self, message: str) -> str:
        """
        Extract the main topic from the user's message.

        For now, uses the full message. Could be enhanced with NLP
        to extract key nouns/phrases.
        """
        # Remove common question words and punctuation
        topic = message.strip()

        # Remove question marks and common prefixes
        for prefix in ['what is', 'how do', 'can you', 'please', 'help me', 'i want to']:
            if topic.lower().startswith(prefix):
                topic = topic[len(prefix):].strip()

        # Limit length for query
        if len(topic) > 100:
            topic = topic[:100]

        return topic

    def _query_knowledge(self, topic: str, intent: str) -> dict:
        """
        Query agent knowledge relevant to the topic.

        Uses IntelligenceQueryService for knowledge search and expert discovery.
        """
        # Determine limits based on intent
        knowledge_limit = 5 if intent == 'question' else 3
        expert_limit = 3

        # Get knowledge entries
        knowledge_result = self.intelligence_service.search_knowledge(
            query=topic,
            limit=knowledge_limit,
            min_confidence=0.5,
            days_back=30
        )

        # Get expert agents
        experts_result = self.intelligence_service.get_expert_agents(
            topic=topic,
            limit=expert_limit
        )

        return {
            'entries': knowledge_result.get('entries', []),
            'experts': experts_result.get('experts', []),
            'agent_breakdown': knowledge_result.get('agent_breakdown', {})
        }

    def _query_dreams(self, topic: str, limit: int = 3) -> list:
        """
        Query high-value agent dreams relevant to the topic.

        High-value = composite_score >= 0.7 (creative + actionable + relevant)
        """
        try:
            # Search for relevant, high-value dreams
            dreams = AgentDream.objects.filter(
                Q(title__icontains=topic) | Q(content__icontains=topic) |
                Q(related_topics__icontains=topic),
                composite_score__gte=0.6,  # Slightly lower to get more results
                dreamed_at__gte=timezone.now() - timedelta(days=14)
            ).select_related('agent').order_by('-composite_score')[:limit]

            return [
                {
                    'id': str(dream.id),
                    'title': dream.title or dream.content[:50],
                    'content': dream.content[:200] if dream.content else '',
                    'agent_name': dream.agent.name if dream.agent else 'Unknown',
                    'composite_score': round(dream.composite_score or 0, 2),
                    'actionability': round(dream.actionability_score or 0, 2),
                    'dream_type': dream.dream_type
                }
                for dream in dreams
            ]
        except Exception as e:
            self.logger.error(f"Error querying dreams: {e}")
            return []

    def _query_policies(self, topic: str = None) -> list:
        """
        Query canonical boardroom decisions (policies).

        These represent agent-agreed governance and best practices.
        """
        try:
            # Get canonical decisions
            query = AgentDecisionSummary.objects.filter(is_canonical=True)

            # If topic provided, filter by relevance
            if topic:
                query = query.filter(
                    Q(topic__icontains=topic) |
                    Q(key_insights__icontains=topic) |
                    Q(recommended_stance__icontains=topic)
                )

            policies = query.order_by('-promoted_at')[:5]

            return [
                {
                    'id': str(policy.id),
                    'topic': policy.topic,
                    'decision_type': policy.decision_type,
                    'impact_area': policy.impact_area,
                    'recommended_stance': policy.recommended_stance[:200] if policy.recommended_stance else '',
                    'participants': policy.participants[:3] if isinstance(policy.participants, list) else [],
                    'promoted_at': policy.promoted_at.isoformat() if policy.promoted_at else None
                }
                for policy in policies
            ]
        except Exception as e:
            self.logger.error(f"Error querying policies: {e}")
            return []

    def _query_spider_trends(self, topic: str, intent: str) -> dict:
        """
        Query recent spider discoveries and trends.

        Uses SpiderIntelligenceService for trending topics.
        """
        try:
            # Map topic to spider categories
            category = self._map_topic_to_category(topic)

            # Determine limits based on intent
            limit = 10 if intent == 'trend' else 5
            hours = 168  # 7 days

            # Get trending topics from spider network
            trends = self.spider_service.get_trending_topics(
                category=category,
                hours=hours,
                limit=limit,
                include_jobs=False
            )

            # Extract unique spider sources
            sources = set()
            for trend in trends:
                if isinstance(trend, dict) and 'sources' in trend:
                    sources.update(trend.get('sources', []))

            return {
                'trends': trends[:limit],
                'sources': list(sources)[:10],
                'category': category
            }
        except Exception as e:
            self.logger.error(f"Error querying spider trends: {e}")
            return {'trends': [], 'sources': [], 'category': None}

    def _map_topic_to_category(self, topic: str) -> Optional[str]:
        """
        Map a topic to a spider category for targeted trend queries.
        """
        topic_lower = topic.lower()

        # Category mappings
        category_keywords = {
            'tech': ['ai', 'machine learning', 'software', 'app', 'coding', 'developer', 'startup', 'saas'],
            'financial': ['crypto', 'bitcoin', 'stocks', 'trading', 'investment', 'finance', 'market'],
            'jobs': ['job', 'career', 'freelance', 'remote', 'hiring', 'employment'],
            'creative': ['design', 'art', 'video', 'content', 'creative', 'brand'],
            'health': ['fitness', 'health', 'wellness', 'medical', 'healthcare'],
            'legal': ['legal', 'law', 'court', 'attorney', 'contract']
        }

        for category, keywords in category_keywords.items():
            if any(kw in topic_lower for kw in keywords):
                return category

        return None  # Return None for general search

    def _format_context(self, data: dict, intent: str) -> str:
        """
        Format the intelligence data into a context string for prompt injection.

        Keeps the output concise and relevant to the intent.
        """
        parts = []

        # Format knowledge entries
        if data['knowledge']:
            parts.append("### What Our Agents Know:")
            for entry in data['knowledge'][:3]:  # Limit to top 3
                agent = entry.get('agent__name', 'Agent')
                title = entry.get('title', '')[:60]
                confidence = entry.get('confidence_score', 0)
                parts.append(f"- **{agent}** learned: \"{title}\" (confidence: {confidence:.0%})")

        # Format expert agents
        if data['experts']:
            parts.append("\n### Expert Agents for This Topic:")
            for expert in data['experts'][:3]:
                name = expert.get('agent_name', 'Agent')
                score = expert.get('expertise_score', 0)
                knowledge_count = expert.get('knowledge_count', 0)
                parts.append(f"- **{name}** (expertise score: {score:.1f}) - {knowledge_count} relevant insights")

        # Format high-value dreams (for creative/strategy intents)
        if data['dreams'] and intent in ['strategy', 'creative']:
            parts.append("\n### Relevant Agent Ideas:")
            for dream in data['dreams'][:2]:
                agent = dream.get('agent_name', 'Agent')
                title = dream.get('title', '')[:50]
                actionability = dream.get('actionability', 0)
                parts.append(f"- **{agent}** envisioned: \"{title}\" (actionability: {actionability:.0%})")

        # Format policies (for strategy intents)
        if data['policies'] and intent == 'strategy':
            parts.append("\n### Platform Policies:")
            for policy in data['policies'][:2]:
                topic = policy.get('topic', '')[:40]
                stance = policy.get('recommended_stance', '')[:80]
                parts.append(f"- **Policy**: {topic}")
                if stance:
                    parts.append(f"  Stance: {stance}")

        # Format spider trends
        if data['spider_trends'] and intent in ['trend', 'question']:
            parts.append("\n### Recent Trends (Spider Network):")
            for trend in data['spider_trends'][:5]:
                if isinstance(trend, dict):
                    keyword = trend.get('keyword', trend.get('topic', 'Unknown'))
                    score = trend.get('score', trend.get('count', 0))
                    parts.append(f"- {keyword} (relevance: {score})")
                elif isinstance(trend, str):
                    parts.append(f"- {trend}")

        # Join and truncate if needed
        context = "\n".join(parts)

        if len(context) > self.max_context_chars:
            context = context[:self.max_context_chars] + "\n... (truncated)"

        return context

    def _build_attribution(self, data: dict) -> str:
        """
        Build a human-readable attribution string for the UI.
        """
        parts = []

        knowledge_count = data['metadata'].get('knowledge_count', 0)
        experts_count = data['metadata'].get('experts_count', 0)
        dreams_count = data['metadata'].get('dreams_count', 0)
        policies_count = data['metadata'].get('policies_count', 0)
        trends_count = data['metadata'].get('trends_count', 0)

        if knowledge_count > 0:
            # Get unique agent names
            agent_names = set()
            for entry in data['knowledge']:
                if 'agent__name' in entry:
                    agent_names.add(entry['agent__name'])
            agent_count = len(agent_names)
            parts.append(f"{knowledge_count} knowledge entries from {agent_count} agents")

        if experts_count > 0:
            expert_names = [e.get('agent_name', '') for e in data['experts'][:3]]
            parts.append(f"expertise from {', '.join(expert_names)}")

        if dreams_count > 0:
            parts.append(f"{dreams_count} agent ideas")

        if policies_count > 0:
            parts.append(f"{policies_count} platform policies")

        if trends_count > 0:
            sources = data['metadata'].get('spider_sources', [])[:3]
            source_str = ', '.join(sources) if sources else 'spider network'
            parts.append(f"{trends_count} trends from {source_str}")

        if not parts:
            return "No relevant platform intelligence found."

        return f"Based on {', '.join(parts)}."


# Singleton instance for easy import
pa_intelligence_enricher = PAIntelligenceEnricher()

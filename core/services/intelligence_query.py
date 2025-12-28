"""
Session 554: Intelligence Query Service

Provides unified access to the full knowledge base for the Personal Assistant.
Bridges the gap between 3,345+ knowledge entries and user queries.

This service replaces the limited "5 recent transfers" approach with:
- Full-text search across all knowledge
- Expert agent discovery by topic
- Recent insights from dreams and conversations
"""

import logging
from typing import Dict, Optional, Any
from datetime import timedelta

from django.db.models import Q, Count, Avg
from django.db.models.functions import Length
from django.utils import timezone

from core.models_unified_system import (
    Agent,
    AgentKnowledgeSource,
    AgentLearningConnection,
    KnowledgeTransfer,
    AgentDream,
    AgentConversation,
)

logger = logging.getLogger(__name__)


class IntelligenceQueryService:
    """
    Session 554: Unified service for querying the agent intelligence network.

    Provides the Personal Assistant with access to:
    - 3,345+ knowledge entries (vs. previous 5 transfers)
    - Expert agent discovery
    - Recent dreams and insights
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.IntelligenceQueryService")

    def search_knowledge(
        self,
        query: str,
        limit: int = 10,
        min_confidence: float = 0.5,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Search the full knowledge base by topic.

        Args:
            query: Search terms to match against knowledge entries
            limit: Maximum results to return
            min_confidence: Minimum confidence score (0.0-1.0)
            days_back: Only search knowledge from last N days (0 for all time)

        Returns:
            Dict with 'entries', 'total_count', 'agent_breakdown'
        """
        try:
            # Build query filters
            words = query.lower().split()

            # Search in title and summary
            q_filter = Q()
            for word in words:
                if len(word) >= 3:  # Skip short words
                    q_filter |= Q(title__icontains=word) | Q(summary__icontains=word)

            if not q_filter:
                # Fallback to full query if no valid words
                q_filter = Q(title__icontains=query) | Q(summary__icontains=query)

            # Apply filters
            queryset = AgentKnowledgeSource.objects.filter(
                q_filter,
                is_active=True,
                confidence_score__gte=min_confidence
            ).select_related('agent')

            # Optionally filter by date
            if days_back > 0:
                cutoff = timezone.now() - timedelta(days=days_back)
                queryset = queryset.filter(last_updated_at__gte=cutoff)

            # Filter out garbage entries (single words, too short)
            queryset = queryset.annotate(
                title_len=Length('title')
            ).filter(title_len__gte=10)

            # Order by relevance (confidence + freshness)
            queryset = queryset.order_by('-confidence_score', '-last_updated_at')

            # Get total count before limiting
            total_count = queryset.count()

            # Get results
            entries = list(queryset[:limit].values(
                'id', 'title', 'summary', 'key_insights',
                'confidence_score', 'last_updated_at',
                'agent__name', 'agent__id', 'knowledge_type'
            ))

            # Calculate agent breakdown
            agent_counts = {}
            for entry in entries:
                agent_name = entry['agent__name']
                if agent_name not in agent_counts:
                    agent_counts[agent_name] = 0
                agent_counts[agent_name] += 1

            self.logger.info(
                f"Knowledge search for '{query}': {total_count} total, "
                f"returning {len(entries)} entries from {len(agent_counts)} agents"
            )

            return {
                'entries': entries,
                'total_count': total_count,
                'returned_count': len(entries),
                'agent_breakdown': agent_counts,
                'query': query
            }

        except Exception as e:
            self.logger.error(f"Error searching knowledge: {e}")
            return {
                'entries': [],
                'total_count': 0,
                'returned_count': 0,
                'agent_breakdown': {},
                'query': query,
                'error': str(e)
            }

    def get_expert_agents(
        self,
        topic: str,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Find agents who have expertise on a topic.

        Expertise is determined by:
        - Number of knowledge entries about the topic
        - Number of times they've taught about the topic
        - Quality of their knowledge (confidence score)

        Args:
            topic: Topic to find experts for
            limit: Maximum experts to return

        Returns:
            Dict with 'experts' list and 'topic'
        """
        try:
            # Find agents with knowledge on this topic
            knowledge_experts = AgentKnowledgeSource.objects.filter(
                Q(title__icontains=topic) | Q(summary__icontains=topic),
                is_active=True,
                confidence_score__gte=0.5
            ).values('agent__id', 'agent__name').annotate(
                knowledge_count=Count('id'),
                avg_confidence=Avg('confidence_score')
            ).order_by('-knowledge_count')[:limit * 2]

            # Find agents who have taught about this topic
            teaching_experts = KnowledgeTransfer.objects.filter(
                Q(source_knowledge__title__icontains=topic) |
                Q(transfer_summary__icontains=topic),
                was_useful=True
            ).values(
                'connection__teacher_agent__id',
                'connection__teacher_agent__name'
            ).annotate(
                teach_count=Count('id'),
                avg_usefulness=Avg('usefulness_score')
            ).order_by('-teach_count')[:limit * 2]

            # Combine and rank
            experts = {}

            for k in knowledge_experts:
                agent_id = str(k['agent__id'])
                experts[agent_id] = {
                    'agent_id': agent_id,
                    'agent_name': k['agent__name'],
                    'knowledge_count': k['knowledge_count'],
                    'avg_confidence': round(k['avg_confidence'] or 0, 2),
                    'teach_count': 0,
                    'expertise_score': 0
                }

            for t in teaching_experts:
                agent_id = str(t['connection__teacher_agent__id'])
                if agent_id in experts:
                    experts[agent_id]['teach_count'] = t['teach_count']
                else:
                    experts[agent_id] = {
                        'agent_id': agent_id,
                        'agent_name': t['connection__teacher_agent__name'],
                        'knowledge_count': 0,
                        'avg_confidence': 0,
                        'teach_count': t['teach_count'],
                        'expertise_score': 0
                    }

            # Calculate expertise score
            for expert in experts.values():
                expert['expertise_score'] = (
                    expert['knowledge_count'] * 2 +
                    expert['teach_count'] * 3 +
                    expert['avg_confidence'] * 10
                )

            # Sort by expertise score and limit
            sorted_experts = sorted(
                experts.values(),
                key=lambda x: x['expertise_score'],
                reverse=True
            )[:limit]

            self.logger.info(
                f"Expert search for '{topic}': found {len(sorted_experts)} experts"
            )

            return {
                'experts': sorted_experts,
                'topic': topic,
                'total_found': len(experts)
            }

        except Exception as e:
            self.logger.error(f"Error finding expert agents: {e}")
            return {
                'experts': [],
                'topic': topic,
                'error': str(e)
            }

    def get_recent_insights(
        self,
        topic: Optional[str] = None,
        limit: int = 10,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Get recent insights from agent dreams and conversations.

        Args:
            topic: Optional topic to filter by
            limit: Maximum insights to return
            days_back: How many days back to search

        Returns:
            Dict with 'dreams', 'conversations', 'total_count'
        """
        try:
            cutoff = timezone.now() - timedelta(days=days_back)

            # Get recent dreams
            dreams_query = AgentDream.objects.filter(
                dreamed_at__gte=cutoff
            ).select_related('agent')

            if topic:
                dreams_query = dreams_query.filter(
                    Q(title__icontains=topic) | Q(content__icontains=topic)
                )

            dreams = list(dreams_query.order_by('-dreamed_at')[:limit].values(
                'id', 'title', 'content', 'dream_type',
                'creativity_score', 'dreamed_at',
                'agent__name', 'related_topics'
            ))

            # Get recent conversations (deprecated but has historical data)
            conversations_query = AgentConversation.objects.filter(
                started_at__gte=cutoff
            ).select_related('initiator')

            if topic:
                conversations_query = conversations_query.filter(
                    Q(topic__icontains=topic)
                )

            conversations = list(conversations_query.order_by('-started_at')[:limit].values(
                'id', 'topic', 'conversation_type',
                'started_at', 'initiator__name'
            ))

            # Get recent knowledge transfers as well
            transfers_query = KnowledgeTransfer.objects.filter(
                created_at__gte=cutoff,
                was_useful=True
            ).select_related(
                'connection__teacher_agent',
                'connection__student_agent',
                'source_knowledge'
            )

            if topic:
                transfers_query = transfers_query.filter(
                    Q(transfer_summary__icontains=topic) |
                    Q(source_knowledge__title__icontains=topic)
                )

            transfers = list(transfers_query.order_by('-created_at')[:limit].values(
                'id', 'transfer_summary', 'usefulness_score', 'created_at',
                'connection__teacher_agent__name',
                'connection__student_agent__name',
                'source_knowledge__title'
            ))

            total_count = len(dreams) + len(conversations) + len(transfers)

            self.logger.info(
                f"Recent insights{f' for {topic}' if topic else ''}: "
                f"{len(dreams)} dreams, {len(conversations)} conversations, "
                f"{len(transfers)} transfers"
            )

            return {
                'dreams': dreams,
                'conversations': conversations,
                'transfers': transfers,
                'total_count': total_count,
                'topic': topic,
                'days_back': days_back
            }

        except Exception as e:
            self.logger.error(f"Error getting recent insights: {e}")
            return {
                'dreams': [],
                'conversations': [],
                'transfers': [],
                'total_count': 0,
                'topic': topic,
                'error': str(e)
            }

    def get_intelligence_summary(self, query: str) -> Dict[str, Any]:
        """
        Get a comprehensive intelligence summary for a query.

        This is the main method for PA integration, combining:
        - Knowledge search results
        - Expert agents
        - Recent insights

        Args:
            query: User's query/topic

        Returns:
            Comprehensive intelligence summary
        """
        try:
            # Search knowledge
            knowledge = self.search_knowledge(query, limit=10)

            # Find experts
            experts = self.get_expert_agents(query, limit=3)

            # Get recent insights
            insights = self.get_recent_insights(topic=query, limit=5)

            # Build summary
            summary = {
                'query': query,
                'knowledge': knowledge,
                'experts': experts,
                'insights': insights,
                'has_data': (
                    knowledge['total_count'] > 0 or
                    len(experts['experts']) > 0 or
                    insights['total_count'] > 0
                ),
                'attribution': self._build_attribution(knowledge, experts, insights)
            }

            self.logger.info(
                f"Intelligence summary for '{query}': "
                f"{knowledge['total_count']} knowledge entries, "
                f"{len(experts['experts'])} experts, "
                f"{insights['total_count']} insights"
            )

            return summary

        except Exception as e:
            self.logger.error(f"Error getting intelligence summary: {e}")
            return {
                'query': query,
                'has_data': False,
                'error': str(e)
            }

    def _build_attribution(
        self,
        knowledge: Dict,
        experts: Dict,
        insights: Dict
    ) -> str:
        """
        Build a human-readable attribution string.

        Example: "Based on 47 knowledge entries from 12 agents including
        ContentStrategyAgent (15), ResearchAgent (8), and TrendAnalysisAgent (7)."
        """
        parts = []

        # Knowledge attribution
        if knowledge['total_count'] > 0:
            agent_count = len(knowledge['agent_breakdown'])
            parts.append(
                f"{knowledge['total_count']} knowledge entries from {agent_count} agents"
            )

            # Top 3 agents
            if knowledge['agent_breakdown']:
                sorted_agents = sorted(
                    knowledge['agent_breakdown'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                agent_str = ", ".join([f"{name} ({count})" for name, count in sorted_agents])
                parts.append(f"including {agent_str}")

        # Expert attribution
        if experts['experts']:
            expert_names = [e['agent_name'] for e in experts['experts'][:3]]
            parts.append(f"with expertise from {', '.join(expert_names)}")

        # Insights attribution
        if insights['total_count'] > 0:
            insight_parts = []
            if insights['dreams']:
                insight_parts.append(f"{len(insights['dreams'])} recent dreams")
            if insights['transfers']:
                insight_parts.append(f"{len(insights['transfers'])} knowledge transfers")
            if insight_parts:
                parts.append(f"and {', '.join(insight_parts)}")

        if not parts:
            return "No relevant intelligence found."

        return f"Based on {' '.join(parts)}."

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get overall intelligence system statistics.

        Returns current counts and activity metrics.
        """
        try:
            now = timezone.now()
            day_ago = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)

            return {
                'knowledge_entries': {
                    'total': AgentKnowledgeSource.objects.filter(is_active=True).count(),
                    'last_24h': AgentKnowledgeSource.objects.filter(
                        last_updated_at__gte=day_ago
                    ).count(),
                    'last_7d': AgentKnowledgeSource.objects.filter(
                        last_updated_at__gte=week_ago
                    ).count()
                },
                'learning_network': {
                    'connections': AgentLearningConnection.objects.filter(is_active=True).count(),
                    'total_transfers': KnowledgeTransfer.objects.count(),
                    'transfers_24h': KnowledgeTransfer.objects.filter(
                        created_at__gte=day_ago
                    ).count()
                },
                'agents': {
                    'total': Agent.objects.filter(is_active=True).count()
                },
                'dreams': {
                    'total': AgentDream.objects.count(),
                    'last_24h': AgentDream.objects.filter(
                        dreamed_at__gte=day_ago
                    ).count()
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}


# Singleton instance for easy import
intelligence_service = IntelligenceQueryService()

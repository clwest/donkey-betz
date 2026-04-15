"""
Agent Intelligence Context Service
===================================

Session 351: Connect agent knowledge/conversations/boardroom decisions to research pipeline.

This service aggregates intelligence from:
1. SharedKnowledge - What agents have learned
2. KnowledgeTransfer - What agents have shared with each other
3. AgentConversation - What agents have discussed
4. AgentDecisionSummary - Boardroom decisions and policies

And provides it as context for business research agents.

Usage:
    from core.services.agent_intelligence_context import get_agent_intelligence_context

    service = get_agent_intelligence_context()
    context = service.get_context_for_research("AI fitness coaching app")
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


@dataclass
class AgentIntelligenceContext:
    """Context from agent intelligence for research enhancement."""

    # Shared knowledge relevant to the topic
    relevant_knowledge: List[Dict[str, Any]] = field(default_factory=list)

    # Recent knowledge transfers about similar topics
    knowledge_transfers: List[Dict[str, Any]] = field(default_factory=list)

    # Agent conversation insights
    conversation_insights: List[Dict[str, Any]] = field(default_factory=list)

    # Canonical boardroom policies
    boardroom_policies: List[Dict[str, Any]] = field(default_factory=list)

    # Summary stats
    total_knowledge_items: int = 0
    total_conversations: int = 0
    total_policies: int = 0

    def to_prompt_context(self) -> str:
        """Convert to formatted string for prompt injection."""
        if not any([self.relevant_knowledge, self.conversation_insights, self.boardroom_policies]):
            return ""

        sections = []
        sections.append("\n" + "=" * 60)
        sections.append("AGENT COLLECTIVE INTELLIGENCE (Session 351)")
        sections.append("=" * 60)
        sections.append("The following insights come from agent learning, conversations, and governance decisions.")
        sections.append("Consider these when forming your analysis.\n")

        # Agent Knowledge section (from AgentKnowledgeSource - the actual learned data!)
        if self.relevant_knowledge:
            sections.append("## LEARNED INSIGHTS FROM AGENTS")
            for item in self.relevant_knowledge[:5]:
                sections.append(f"- [{item.get('source_agent', 'Agent')}] {item.get('title', '')} ({item.get('knowledge_type', '')})")
                if item.get('description'):
                    sections.append(f"  → {item.get('description')[:150]}...")
                # Include key insights if available
                key_insights = item.get('key_insights', [])
                if key_insights:
                    for ki in key_insights[:2]:
                        if isinstance(ki, str):
                            sections.append(f"    • {ki[:100]}")
            sections.append("")

        # Knowledge Transfers section
        if self.knowledge_transfers:
            sections.append("## RECENT KNOWLEDGE SHARING")
            for transfer in self.knowledge_transfers[:3]:
                sections.append(
                    f"- {transfer.get('teacher', '?')} taught {transfer.get('student', '?')}: "
                    f"{transfer.get('knowledge_title', '')[:80]}"
                )
            sections.append("")

        # Conversation Insights section
        if self.conversation_insights:
            sections.append("## INSIGHTS FROM AGENT DISCUSSIONS")
            for insight in self.conversation_insights[:3]:
                sections.append(f"### Topic: {insight.get('topic', 'Discussion')[:80]}")
                if insight.get('conclusion'):
                    sections.append(f"   Conclusion: {insight.get('conclusion')[:200]}...")
                if insight.get('key_insights'):
                    for ki in insight.get('key_insights', [])[:3]:
                        sections.append(f"   • {ki}")
            sections.append("")

        # Boardroom Policies section
        if self.boardroom_policies:
            sections.append("## CANONICAL POLICIES (Boardroom Decisions)")
            sections.append("These policies have been established through agent governance:")
            for policy in self.boardroom_policies[:3]:
                sections.append(f"\n### {policy.get('topic', 'Policy')}")
                sections.append(f"Type: {policy.get('decision_type', 'guideline')} | Area: {policy.get('impact_area', 'general')}")
                if policy.get('recommended_stance'):
                    sections.append(f"Stance: {policy.get('recommended_stance')[:200]}")
                if policy.get('key_insights'):
                    sections.append("Key Insights:")
                    for ki in policy.get('key_insights', [])[:3]:
                        sections.append(f"  • {ki}")
            sections.append("")

        sections.append("=" * 60)
        sections.append("")

        return "\n".join(sections)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'relevant_knowledge': self.relevant_knowledge,
            'knowledge_transfers': self.knowledge_transfers,
            'conversation_insights': self.conversation_insights,
            'boardroom_policies': self.boardroom_policies,
            'total_knowledge_items': self.total_knowledge_items,
            'total_conversations': self.total_conversations,
            'total_policies': self.total_policies,
        }


class AgentIntelligenceContextService:
    """
    Service to gather agent intelligence for research context.

    This connects the "Agents/Social" tab data to the business research pipeline,
    ensuring that agent conversations, shared knowledge, and boardroom decisions
    actually influence research outcomes.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_context_for_research(
        self,
        topic: str,
        domain: str = None,
        include_knowledge: bool = True,
        include_transfers: bool = True,
        include_conversations: bool = True,
        include_policies: bool = True,
        max_items_per_category: int = 5
    ) -> AgentIntelligenceContext:
        """
        Get agent intelligence context relevant to a research topic.

        Args:
            topic: The research topic or business idea
            domain: Optional domain filter (fitness_health, fintech, etc.)
            include_knowledge: Include SharedKnowledge
            include_transfers: Include KnowledgeTransfer records
            include_conversations: Include AgentConversation insights
            include_policies: Include canonical BoardroomDecisions
            max_items_per_category: Max items per category

        Returns:
            AgentIntelligenceContext with all relevant intelligence
        """
        context = AgentIntelligenceContext()

        try:
            if include_knowledge:
                context.relevant_knowledge = self._get_relevant_knowledge(
                    topic, domain, max_items_per_category
                )
                context.total_knowledge_items = len(context.relevant_knowledge)

            if include_transfers:
                context.knowledge_transfers = self._get_recent_transfers(
                    topic, max_items_per_category
                )

            if include_conversations:
                context.conversation_insights = self._get_conversation_insights(
                    topic, domain, max_items_per_category
                )
                context.total_conversations = len(context.conversation_insights)

            if include_policies:
                context.boardroom_policies = self._get_relevant_policies(
                    topic, domain, max_items_per_category
                )
                context.total_policies = len(context.boardroom_policies)

            total = (
                len(context.relevant_knowledge) +
                len(context.knowledge_transfers) +
                len(context.conversation_insights) +
                len(context.boardroom_policies)
            )

            if total > 0:
                self.logger.info(
                    f"🧠 [INTELLIGENCE] Found {total} intelligence items for '{topic[:50]}': "
                    f"{len(context.relevant_knowledge)} knowledge, "
                    f"{len(context.conversation_insights)} conversations, "
                    f"{len(context.boardroom_policies)} policies"
                )

            return context

        except Exception as e:
            self.logger.error(f"Error gathering agent intelligence: {e}")
            return context

    def _get_relevant_knowledge(
        self,
        topic: str,
        domain: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Get AgentKnowledgeSource relevant to the topic.

        Session 351 Fix: Changed from SharedKnowledge (empty) to AgentKnowledgeSource (732+ items).
        AgentKnowledgeSource is where run_agent_learning_cycle() actually saves learned knowledge!
        """
        try:
            from core.models_unified_system import AgentKnowledgeSource

            # Build query - search in title and summary
            # Use multiple search strategies for better matching
            base_query = AgentKnowledgeSource.objects.filter(is_active=True)

            # Extract meaningful words from topic (min 4 chars)
            topic_words = [w for w in topic.split() if len(w) >= 4][:5]

            # Build OR query for each topic word AND the truncated topic
            search_conditions = Q(title__icontains=topic[:30]) | Q(summary__icontains=topic[:30])
            for word in topic_words:
                search_conditions |= Q(title__icontains=word) | Q(summary__icontains=word)

            # Session 491: Include spider_category in select_related to avoid N+1 queries
            query = base_query.filter(search_conditions).select_related('agent', 'spider_category').order_by('-confidence_score', '-last_updated_at')

            # Filter by spider_category if domain provided
            if domain:
                # Map domain to likely spider categories
                domain_to_categories = {
                    'fitness_health': ['health', 'community'],
                    'fintech_finance': ['financial', 'market_data'],
                    'ai_ml': ['tech', 'innovation'],
                    'saas_b2b': ['tech', 'innovation'],
                    'ecommerce_retail': ['market_data', 'financial'],
                    'edtech_learning': ['education', 'tech'],
                    'creator_economy': ['creative', 'social'],
                }
                categories = domain_to_categories.get(domain, [])
                if categories:
                    # Session 491: Fix FK filter - spider_category is a ForeignKey, not a CharField
                    # Filter by slug field through the FK relationship
                    query = query.filter(spider_category__slug__in=categories)

            results = []
            for knowledge in query[:limit]:
                # Clean [Learned] prefix for display
                import re
                clean_title = re.sub(r'^(\[Learned\]\s*)+', '', knowledge.title or '').strip()

                results.append({
                    'id': str(knowledge.id),
                    'title': clean_title,
                    'description': knowledge.summary[:300] if knowledge.summary else '',
                    'source_agent': knowledge.agent.name if knowledge.agent else 'Unknown',
                    # Session 491: spider_category is a FK - access .name or .slug for display
                    'domain': knowledge.spider_category.name if knowledge.spider_category else '',
                    'tags': knowledge.source_spider_names or [],
                    'effectiveness_score': knowledge.confidence_score,
                    'knowledge_type': knowledge.knowledge_type,
                    'key_insights': knowledge.key_insights[:3] if knowledge.key_insights else []
                })

            return results

        except Exception as e:
            self.logger.warning(f"Failed to get agent knowledge: {e}")
            return []

    def _get_recent_transfers(
        self,
        topic: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get recent KnowledgeTransfer records."""
        try:
            from core.models import KnowledgeTransfer

            # Get recent transfers (last 7 days)
            recent = timezone.now() - timedelta(days=7)

            transfers = KnowledgeTransfer.objects.filter(
                created_at__gte=recent
            ).select_related(
                'connection__teacher_agent',
                'connection__student_agent',
                'source_knowledge'
            ).order_by('-usefulness_score', '-created_at')[:limit * 2]

            # Filter by topic relevance
            results = []
            topic_lower = topic.lower()

            for transfer in transfers:
                knowledge_title = ''
                if transfer.source_knowledge:
                    knowledge_title = transfer.source_knowledge.title or ''

                # Check if relevant to topic
                if topic_lower[:20] in knowledge_title.lower() or len(results) < limit // 2:
                    teacher_name = 'Unknown'
                    student_name = 'Unknown'

                    if transfer.connection:
                        if transfer.connection.teacher_agent:
                            teacher_name = transfer.connection.teacher_agent.name
                        if transfer.connection.student_agent:
                            student_name = transfer.connection.student_agent.name

                    # Clean up [Learned] prefixes
                    import re
                    knowledge_title = re.sub(r'^(\[Learned\]\s*)+', '', knowledge_title).strip()

                    results.append({
                        'teacher': teacher_name,
                        'student': student_name,
                        'knowledge_title': knowledge_title[:100],
                        'usefulness_score': transfer.usefulness_score,
                        'timestamp': transfer.created_at.isoformat() if transfer.created_at else None
                    })

                    if len(results) >= limit:
                        break

            return results

        except Exception as e:
            self.logger.warning(f"Failed to get knowledge transfers: {e}")
            return []

    def _get_conversation_insights(
        self,
        topic: str,
        domain: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get insights from AgentConversations."""
        try:
            from core.models_unified_system import AgentConversation

            # Get recent concluded conversations
            recent = timezone.now() - timedelta(days=14)

            query = AgentConversation.objects.filter(
                started_at__gte=recent,
                status='concluded'
            )

            # Search in topic
            query = query.filter(
                Q(topic__icontains=topic[:30]) |
                Q(conclusion__icontains=topic[:30])
            ).order_by('-started_at')

            results = []
            for conv in query[:limit]:
                participants = []
                try:
                    participants = [p.name for p in conv.participants.all()[:4]]
                except Exception as _e:
                    logger.warning(
                        "agent_intelligence_context._get_conversation_insights: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

                # Extract key points from conclusion if available
                key_insights = []
                if conv.conclusion:
                    # Simple extraction - look for bullet points or numbered items
                    lines = conv.conclusion.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith(('-', '•', '*', '1', '2', '3')):
                            key_insights.append(line.lstrip('-•*0123456789. '))
                            if len(key_insights) >= 3:
                                break

                results.append({
                    'id': str(conv.id),
                    'topic': conv.topic[:100] if conv.topic else '',
                    'participants': participants,
                    'conversation_type': conv.conversation_type,
                    'conclusion': conv.conclusion[:300] if conv.conclusion else '',
                    'key_insights': key_insights,
                    'timestamp': conv.started_at.isoformat() if conv.started_at else None
                })

            return results

        except Exception as e:
            self.logger.warning(f"Failed to get conversation insights: {e}")
            return []

    def _get_relevant_policies(
        self,
        topic: str,
        domain: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get canonical BoardroomDecisions/policies."""
        try:
            from core.models_unified_system import AgentDecisionSummary

            # Get canonical policies
            query = AgentDecisionSummary.objects.filter(
                is_canonical=True
            )

            # Filter by topic relevance or impact area
            topic_lower = topic.lower()

            # Map domain to likely impact areas
            domain_to_areas = {
                'fitness_health': ['product'],
                'fintech_finance': ['product', 'security'],
                'ai_ml': ['prompting', 'agents', 'workflow'],
                'saas_b2b': ['product', 'workflow'],
                'ecommerce_retail': ['product'],
                'edtech_learning': ['product'],
                'creator_economy': ['product', 'workflow'],
            }

            impact_areas = domain_to_areas.get(domain, ['product', 'agents'])

            # Get policies matching impact areas or topic
            policies = query.filter(
                Q(impact_area__in=impact_areas) |
                Q(topic__icontains=topic[:20]) |
                Q(key_insights__icontains=topic[:20])
            ).order_by('-promoted_at')[:limit]

            results = []
            for policy in policies:
                results.append({
                    'id': str(policy.id),
                    'topic': policy.topic[:100] if policy.topic else '',
                    'decision_type': policy.decision_type,
                    'impact_area': policy.impact_area,
                    'recommended_stance': policy.recommended_stance[:300] if policy.recommended_stance else '',
                    'key_insights': policy.key_insights[:5] if policy.key_insights else [],
                    'suggested_feature': policy.suggested_feature,
                    'rationale': policy.rationale[:200] if policy.rationale else '',
                    'participants': policy.participants[:4] if policy.participants else [],
                    'promoted_at': policy.promoted_at.isoformat() if policy.promoted_at else None
                })

            return results

        except Exception as e:
            self.logger.warning(f"Failed to get boardroom policies: {e}")
            return []

    def get_policies_for_agent(
        self,
        agent_name: str,
        max_policies: int = 5
    ) -> str:
        """
        Get canonical policies formatted for agent prompt injection.

        Wraps PolicyContextService for convenience.
        """
        try:
            from core.services.policy_context import get_policy_context_service
            service = get_policy_context_service()
            return service.get_policies_for_agent(agent_name, max_policies=max_policies)
        except Exception as e:
            self.logger.warning(f"Failed to get policies for {agent_name}: {e}")
            return ""


# Singleton instance
_agent_intelligence_context_instance = None


def get_agent_intelligence_context() -> AgentIntelligenceContextService:
    """Get singleton AgentIntelligenceContextService instance."""
    global _agent_intelligence_context_instance
    if _agent_intelligence_context_instance is None:
        _agent_intelligence_context_instance = AgentIntelligenceContextService()
    return _agent_intelligence_context_instance

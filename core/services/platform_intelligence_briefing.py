"""
Platform Intelligence Briefing Service
=======================================
Session 574: Omniscient PA - Full Platform Awareness

This service aggregates ALL platform intelligence into a concise briefing
that gives the PA complete situational awareness:

- Who's learning from who (knowledge transfers)
- What agents have learned (agent knowledge)
- Important agent conversations
- Agent dreams and insights
- Boardroom decisions pending
- External intelligence from spiders

The briefing is cached for performance and refreshed every 5 minutes.
"""

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count

logger = logging.getLogger(__name__)

CACHE_KEY = 'platform_intelligence_briefing'
CACHE_TTL = 300  # 5 minutes


@dataclass
class LearningEvent:
    """Represents a knowledge transfer between agents."""
    from_agent: str
    to_agent: str
    topic: str
    timestamp: str


@dataclass
class ConversationHighlight:
    """Represents a notable agent conversation."""
    participants: List[str]
    topic: str
    summary: str
    timestamp: str


@dataclass
class AgentInsight:
    """Represents an agent dream/insight."""
    agent: str
    insight: str
    category: str
    timestamp: str


@dataclass
class BoardroomItem:
    """Represents a pending boardroom decision."""
    topic: str
    decision_type: str
    status: str
    participants: List[str]


@dataclass
class SpiderHighlight:
    """Represents notable external intelligence."""
    source: str
    title: str
    category: str
    timestamp: str


@dataclass
class PlatformBriefing:
    """The complete platform intelligence briefing."""
    generated_at: str

    # Learning activity
    learning_events: List[LearningEvent] = field(default_factory=list)
    total_transfers_24h: int = 0

    # Conversations
    conversation_highlights: List[ConversationHighlight] = field(default_factory=list)
    total_conversations_24h: int = 0

    # Agent insights
    agent_insights: List[AgentInsight] = field(default_factory=list)
    total_dreams_24h: int = 0

    # Boardroom
    boardroom_items: List[BoardroomItem] = field(default_factory=list)
    pending_decisions: int = 0

    # External intel
    spider_highlights: List[SpiderHighlight] = field(default_factory=list)
    total_spider_records_24h: int = 0

    # Platform health
    active_agents: int = 0
    active_spiders: int = 0


class PlatformIntelligenceBriefingService:
    """
    Aggregates all platform intelligence into a concise briefing.

    Usage:
        service = PlatformIntelligenceBriefingService()
        briefing = service.get_briefing()
        formatted = service.format_for_prompt(briefing)
    """

    def __init__(self, lookback_hours: int = 24):
        self.lookback_hours = lookback_hours
        self.logger = logging.getLogger(f"{__name__}.PlatformIntelligenceBriefingService")

    def get_briefing(self, force_refresh: bool = False) -> PlatformBriefing:
        """
        Get the platform intelligence briefing.

        Uses caching for performance. Set force_refresh=True to bypass cache.
        """
        if not force_refresh:
            cached = cache.get(CACHE_KEY)
            if cached:
                self.logger.debug("Returning cached platform briefing")
                return cached

        self.logger.info("Generating fresh platform intelligence briefing...")

        now = timezone.now()
        lookback = now - timedelta(hours=self.lookback_hours)

        briefing = PlatformBriefing(
            generated_at=now.isoformat()
        )

        # Gather all intelligence
        self._gather_learning_events(briefing, lookback)
        self._gather_conversations(briefing, lookback)
        self._gather_agent_insights(briefing, lookback)
        self._gather_boardroom_items(briefing)
        self._gather_spider_highlights(briefing, lookback)
        self._gather_platform_health(briefing)

        # Cache the briefing
        cache.set(CACHE_KEY, briefing, CACHE_TTL)

        self.logger.info(
            f"Platform briefing generated: {len(briefing.learning_events)} transfers, "
            f"{len(briefing.conversation_highlights)} convos, {len(briefing.agent_insights)} insights, "
            f"{briefing.pending_decisions} pending decisions"
        )

        return briefing

    def _gather_learning_events(self, briefing: PlatformBriefing, since: timezone.datetime):
        """Gather recent knowledge transfers between agents."""
        try:
            from core.models import KnowledgeTransfer

            transfers = KnowledgeTransfer.objects.filter(
                created_at__gte=since
            ).select_related(
                'connection__teacher_agent', 'connection__student_agent', 'source_knowledge'
            ).order_by('-created_at')[:10]

            briefing.total_transfers_24h = KnowledgeTransfer.objects.filter(
                created_at__gte=since
            ).count()

            for transfer in transfers:
                # Get agent names from connection
                # Fields are teacher_agent/student_agent (FK to Agent)
                from_name = 'Unknown'
                to_name = 'Unknown'
                if transfer.connection:
                    from_name = transfer.connection.teacher_agent.name if transfer.connection.teacher_agent_id else 'Unknown'
                    to_name = transfer.connection.student_agent.name if transfer.connection.student_agent_id else 'Unknown'

                topic = transfer.source_knowledge.title[:50] if transfer.source_knowledge else transfer.transfer_summary[:50] if transfer.transfer_summary else 'Unknown topic'

                # Clean up [Learned] prefixes
                for prefix in ['[Learned] ', 'Learned: ']:
                    if topic.startswith(prefix):
                        topic = topic[len(prefix):]

                briefing.learning_events.append(LearningEvent(
                    from_agent=from_name,
                    to_agent=to_name,
                    topic=topic,
                    timestamp=transfer.created_at.strftime('%H:%M')
                ))
        except Exception as e:
            self.logger.warning(f"Could not gather learning events: {e}")

    def _gather_conversations(self, briefing: PlatformBriefing, since: timezone.datetime):
        """Gather notable agent conversations."""
        try:
            from core.models import AgentConversation

            # Get recent conversations (using started_at field)
            conversations = AgentConversation.objects.filter(
                started_at__gte=since
            ).order_by('-started_at')[:20]

            briefing.total_conversations_24h = AgentConversation.objects.filter(
                started_at__gte=since
            ).count()

            seen_topics = set()
            for convo in conversations:
                # Extract topic
                topic = convo.topic or ''
                if not topic and convo.messages:
                    # Try to extract from first message
                    first_msg = convo.messages[0] if isinstance(convo.messages, list) else str(convo.messages)[:100]
                    topic = str(first_msg)[:60]

                if not topic or topic in seen_topics:
                    continue

                seen_topics.add(topic)

                # Get participants from initiator and participants field
                participant_names = []
                if convo.initiator:
                    participant_names.append(convo.initiator.name if hasattr(convo.initiator, 'name') else str(convo.initiator))
                if convo.participants:
                    # participants might be a list of agent names or IDs
                    for p in convo.participants[:2]:
                        if isinstance(p, str):
                            participant_names.append(p)

                if not participant_names:
                    participant_names = ['Agents']

                briefing.conversation_highlights.append(ConversationHighlight(
                    participants=participant_names[:2],
                    topic=topic[:60],
                    summary='',  # Could add AI summarization later
                    timestamp=convo.started_at.strftime('%H:%M') if convo.started_at else ''
                ))

                if len(briefing.conversation_highlights) >= 5:
                    break

        except Exception as e:
            self.logger.warning(f"Could not gather conversations: {e}")

    def _gather_agent_insights(self, briefing: PlatformBriefing, since: timezone.datetime):
        """Gather recent agent dreams/insights."""
        try:
            from core.models import AgentDream

            dreams = AgentDream.objects.filter(
                dreamed_at__gte=since
            ).select_related('agent').order_by('-dreamed_at')[:10]

            briefing.total_dreams_24h = AgentDream.objects.filter(
                dreamed_at__gte=since
            ).count()

            for dream in dreams:
                agent_name = dream.agent.name if dream.agent else 'Unknown Agent'
                insight = dream.content[:100] if dream.content else dream.title[:100] if dream.title else ''
                category = dream.dream_type or 'insight'

                if insight:
                    briefing.agent_insights.append(AgentInsight(
                        agent=agent_name,
                        insight=insight,
                        category=category,
                        timestamp=dream.dreamed_at.strftime('%H:%M') if dream.dreamed_at else ''
                    ))

                if len(briefing.agent_insights) >= 5:
                    break

        except Exception as e:
            self.logger.warning(f"Could not gather agent insights: {e}")

    def _gather_boardroom_items(self, briefing: PlatformBriefing):
        """Gather pending boardroom decisions."""
        try:
            from core.models_unified_system import AgentDecisionSummary

            pending = AgentDecisionSummary.objects.filter(
                is_canonical=False
            ).order_by('-created_at')[:10]

            briefing.pending_decisions = AgentDecisionSummary.objects.filter(
                is_canonical=False
            ).count()

            for decision in pending:
                topic = decision.topic or 'Untitled'

                # Clean prefixes
                prefixes = ['Decision: ', 'Panel: ', 'Research: ', 'Discussion: ', '[Learned] ']
                for prefix in prefixes:
                    while topic.startswith(prefix):
                        topic = topic[len(prefix):]

                if len(topic) < 10:
                    continue

                participants = decision.participants if decision.participants else []

                briefing.boardroom_items.append(BoardroomItem(
                    topic=topic[:60],
                    decision_type=decision.decision_type or 'general',
                    status='pending',
                    participants=participants[:3] if isinstance(participants, list) else []
                ))

                if len(briefing.boardroom_items) >= 5:
                    break

        except Exception as e:
            self.logger.warning(f"Could not gather boardroom items: {e}")

    def _gather_spider_highlights(self, briefing: PlatformBriefing, since: timezone.datetime):
        """Gather notable external intelligence from spiders."""
        try:
            from core.models import SpiderData

            # Get recent spider data count
            briefing.total_spider_records_24h = SpiderData.objects.filter(
                created_at__gte=since
            ).count()

            # Get one highlight from each spider source
            seen_sources = set()
            highlights = SpiderData.objects.filter(
                created_at__gte=since
            ).order_by('-created_at')[:50]

            for data in highlights:
                source = data.spider_name or 'unknown'
                if source in seen_sources:
                    continue
                seen_sources.add(source)

                # Extract title from raw_data or processed_data
                title = ''
                if data.processed_data and isinstance(data.processed_data, dict):
                    title = data.processed_data.get('title', '')[:60] or data.processed_data.get('headline', '')[:60]
                if not title and data.raw_data and isinstance(data.raw_data, dict):
                    title = data.raw_data.get('title', '')[:60] or data.raw_data.get('headline', '')[:60]
                if not title:
                    title = f"Data from {source}"

                category = data.data_type or 'news'

                briefing.spider_highlights.append(SpiderHighlight(
                    source=source,
                    title=title[:60],
                    category=category,
                    timestamp=data.created_at.strftime('%H:%M')
                ))

                if len(briefing.spider_highlights) >= 5:
                    break

        except Exception as e:
            self.logger.warning(f"Could not gather spider highlights: {e}")

    def _gather_platform_health(self, briefing: PlatformBriefing):
        """Gather platform health metrics."""
        try:
            from core.models_unified_system import Agent
            briefing.active_agents = Agent.objects.filter(is_active=True).count()
        except Exception as e:
            self.logger.warning(f"Could not get active agents: {e}")

        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            # Get registered spiders from the registry
            briefing.active_spiders = len(SpiderRegistry._registry) if hasattr(SpiderRegistry, '_registry') else 0
        except Exception as e:
            self.logger.warning(f"Could not get active spiders: {e}")

    def format_for_prompt(self, briefing: PlatformBriefing) -> str:
        """
        Format the briefing for injection into PA prompt.

        Returns a concise, structured summary suitable for LLM context.
        """
        lines = []
        lines.append("## PLATFORM INTELLIGENCE BRIEFING")
        lines.append(f"*Generated: {briefing.generated_at[:16]}*")
        lines.append("")

        # Learning Activity
        if briefing.learning_events or briefing.total_transfers_24h > 0:
            lines.append(f"### Learning Activity ({briefing.total_transfers_24h} transfers in 24h)")
            if briefing.learning_events:
                for event in briefing.learning_events[:5]:
                    lines.append(f"- {event.from_agent} taught {event.to_agent}: \"{event.topic}\"")
            else:
                lines.append("- No recent transfers")
            lines.append("")

        # Agent Conversations
        if briefing.conversation_highlights or briefing.total_conversations_24h > 0:
            lines.append(f"### Agent Conversations ({briefing.total_conversations_24h} in 24h)")
            if briefing.conversation_highlights:
                for convo in briefing.conversation_highlights[:3]:
                    participants = " + ".join(convo.participants)
                    lines.append(f"- {participants}: \"{convo.topic[:50]}\"")
            else:
                lines.append("- No notable conversations")
            lines.append("")

        # Agent Insights (Dreams)
        if briefing.agent_insights or briefing.total_dreams_24h > 0:
            lines.append(f"### Agent Insights ({briefing.total_dreams_24h} dreams in 24h)")
            if briefing.agent_insights:
                for insight in briefing.agent_insights[:3]:
                    lines.append(f"- {insight.agent}: \"{insight.insight[:60]}...\"")
            else:
                lines.append("- No recent insights")
            lines.append("")

        # Boardroom Status
        if briefing.boardroom_items or briefing.pending_decisions > 0:
            lines.append(f"### Boardroom Status ({briefing.pending_decisions} pending decisions)")
            if briefing.boardroom_items:
                for item in briefing.boardroom_items[:3]:
                    lines.append(f"- [{item.decision_type}] {item.topic}")
            else:
                lines.append("- No pending decisions")
            lines.append("")

        # External Intelligence
        if briefing.spider_highlights or briefing.total_spider_records_24h > 0:
            lines.append(f"### External Intelligence ({briefing.total_spider_records_24h} spider records in 24h)")
            if briefing.spider_highlights:
                for highlight in briefing.spider_highlights[:3]:
                    lines.append(f"- [{highlight.source}] {highlight.title}")
            else:
                lines.append("- No recent external data")
            lines.append("")

        # Platform Health
        lines.append(f"### Platform Health")
        lines.append(f"- Active Agents: {briefing.active_agents}")
        lines.append(f"- Active Spiders: {briefing.active_spiders}")
        lines.append("")

        return "\n".join(lines)

    def get_formatted_briefing(self, force_refresh: bool = False) -> str:
        """Convenience method to get formatted briefing in one call."""
        briefing = self.get_briefing(force_refresh=force_refresh)
        return self.format_for_prompt(briefing)


# Singleton instance
_briefing_service: Optional[PlatformIntelligenceBriefingService] = None


def get_platform_intelligence_service() -> PlatformIntelligenceBriefingService:
    """Get the singleton platform intelligence briefing service."""
    global _briefing_service
    if _briefing_service is None:
        _briefing_service = PlatformIntelligenceBriefingService()
    return _briefing_service

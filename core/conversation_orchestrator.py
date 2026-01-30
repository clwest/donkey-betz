"""
Conversation Orchestrator
=========================

Session 261: Orchestrates multi-agent conversations with contract enforcement.

This module replaces the basic prompt generation in agent_conversation_consumer.py
with structured, role-aware conversation management that ensures:

1. Constructive tension (no empty agreement)
2. Platform grounding (metrics and systems referenced)
3. Structured outputs (DecisionSummary with insights and features)

Usage:
    orchestrator = ConversationOrchestrator()
    result = orchestrator.generate_conversation(
        agent1={'name': 'ResearchAgent', 'type': 'ResearchAgent', 'specialization': 'Data analysis'},
        agent2={'name': 'ContentStrategyAgent', 'type': 'ContentStrategyAgent', 'specialization': 'Content strategy'},
        topic='Optimizing Medium article engagement',
        num_turns=6
    )
"""

import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .conversation_roles import (
    get_conversation_role,
    has_tension,
    has_empty_agreement,
    has_grounding,
    get_grounding_refs,
    extract_decision_summary,
    validate_decision_summary,
    CONVERSATION_CONTRACT
)

logger = logging.getLogger(__name__)


# Session 811: Feature flags for AI World Conversation Enhancement
ENABLE_DREAM_INJECTION = True
ENABLE_ACTION_DISPATCH = True
ENABLE_CROSS_AGENT_MEMORY = True

# Session 826: Goal-Driven Conversation Enhancement
ENABLE_RICH_CONTEXT = True  # Inject spider/advisor/learning context
ENABLE_AUTO_AGENT_SELECTION = True  # Select topic-matched agents
ENABLE_STRUCTURED_TURNS = True  # Use turn flow patterns

# Session 873: Decision Enforcement - force decisive outcomes after debate
ENABLE_DECISION_ENFORCEMENT = True  # Force decisions via DecisionEnforcerAgent

# Session 874: Synthesis Contract - structured debate output
ENABLE_SYNTHESIS_CONTRACT = True  # Convert DecisionSummary to SynthesisContract


# Session 826: Structured turn flows for different conversation types
TURN_FLOWS = {
    'analytical': ['propose', 'challenge', 'synthesize', 'decide'],
    'creative': ['brainstorm', 'expand', 'refine', 'select'],
    'debate': ['position', 'counter', 'rebut', 'conclude'],
    'planning': ['goals', 'steps', 'dependencies', 'schedule'],
    'critique': ['present', 'challenge', 'defend', 'improve'],
    'general': ['explore', 'discuss', 'clarify', 'summarize'],
}

# Session 826: Turn-specific prompts for structured flow
TURN_PROMPTS = {
    # Analytical flow
    'propose': "Present your initial analysis or proposal on this topic. Be specific and grounded in data.",
    'challenge': "Challenge the previous perspective. What's missing, flawed, or overlooked?",
    'synthesize': "Synthesize the best elements from both viewpoints into a coherent approach.",
    'decide': "Based on the discussion, what's the recommended action? Be decisive.",

    # Creative flow
    'brainstorm': "Generate bold, creative ideas without self-censoring. Think big.",
    'expand': "Build on the ideas shared. How can we make them bigger or more impactful?",
    'refine': "Refine the most promising ideas. What's practical? What needs adjustment?",
    'select': "Select the best idea(s) and explain why they should move forward.",

    # Debate flow
    'position': "State your position clearly and make your strongest argument.",
    'counter': "Present a counter-argument. Identify weaknesses in the previous position.",
    'rebut': "Rebut the counter-argument. Defend your position with evidence.",
    'conclude': "Summarize the debate and state the most defensible conclusion.",

    # Planning flow
    'goals': "Define the clear goals and success criteria for this initiative.",
    'steps': "Break down the initiative into concrete, actionable steps.",
    'dependencies': "Identify dependencies, risks, and potential blockers.",
    'schedule': "Propose a timeline and assign ownership for each step.",

    # Critique flow
    'present': "Present the idea, work, or approach that needs critique.",
    'challenge': "Provide constructive critique. What could be improved?",
    'defend': "Defend the approach or acknowledge valid criticisms.",
    'improve': "Propose specific improvements based on the critique.",

    # General flow
    'explore': "Explore the topic from your unique perspective.",
    'discuss': "Build on what's been shared. Add your expertise.",
    'clarify': "Clarify any ambiguities and deepen the analysis.",
    'summarize': "Summarize key insights and propose next steps.",
}


@dataclass
class ConversationState:
    """Tracks conversation state for contract enforcement."""
    total_turns: int = 0
    tension_count: int = 0
    grounding_count: int = 0
    empty_agreement_count: int = 0
    insights_mentioned: List[str] = field(default_factory=list)
    last_tension_turn: int = -3  # Start at -3 so first tension can be at turn 0
    grounding_refs: List[str] = field(default_factory=list)
    # Session 781: Track used openers to prevent repetition
    used_openers: List[str] = field(default_factory=list)
    # Session 781 Level 3: Track discourse markers for comprehensive repetition prevention
    used_discourse_markers: List[str] = field(default_factory=list)
    # Session 826: Goal-driven conversation tracking
    objective: str = ""
    success_criteria: List[str] = field(default_factory=list)
    criteria_met: List[bool] = field(default_factory=list)  # Track which criteria are satisfied


# Session 781: Disallowed opener patterns - these are banned globally
DISALLOWED_OPENERS = [
    "I'd push back slightly",
    "That's a great point",
    "Great point",
    "I agree, but",
    "I agree, however",
    "That's a fair point",
    "Absolutely",
    "With all due respect",
    "I love that",
    "Exactly right",
]

# Session 781 Level 3: Discourse markers to track for repetition prevention
# These are common phrases that make conversations feel templated when repeated
DISCOURSE_MARKERS = {
    # Transition markers
    'transitions': [
        "however", "that said", "building on that", "additionally",
        "furthermore", "moreover", "on the other hand", "nevertheless",
        "in contrast", "similarly", "likewise", "consequently",
        "as a result", "therefore", "thus", "hence",
    ],
    # Agreement markers
    'agreement': [
        "i see your point", "that makes sense", "you're right",
        "i agree with", "exactly", "precisely", "indeed",
        "that's correct", "absolutely right", "spot on",
        "that resonates", "i'm aligned with",
    ],
    # Disagreement markers
    'disagreement': [
        "i'd question", "the concern is", "but have we considered",
        "i'm not sure about", "the risk here is", "my concern is",
        "i'd challenge", "the problem with", "the issue is",
        "that overlooks", "we're missing",
    ],
    # Filler phrases
    'fillers': [
        "to be honest", "in my view", "from my perspective",
        "i think that", "it seems to me", "in my opinion",
        "i believe that", "i would say", "if i'm being honest",
        "frankly", "honestly", "truthfully",
    ],
    # Hedging phrases
    'hedges': [
        "sort of", "kind of", "a bit", "slightly",
        "somewhat", "perhaps", "maybe", "possibly",
        "i suppose", "i guess", "arguably",
    ],
}


def extract_opener(text: str) -> Optional[str]:
    """
    Session 781: Extract the opening phrase from a response.

    Returns the first sentence or clause (up to 60 chars) that starts the response.
    This is used to track what openers have been used and prevent repetition.
    """
    if not text:
        return None

    # Clean up the text
    text = text.strip()

    # Find the first sentence or clause break
    break_chars = ['.', '!', '?', '—', ' - ', ':']
    first_break = len(text)

    for char in break_chars:
        pos = text.find(char)
        if pos > 0 and pos < first_break:
            first_break = pos

    # Extract opener (max 60 chars)
    opener = text[:min(first_break, 60)].strip()

    # If it's too short, it's not meaningful
    if len(opener) < 10:
        return None

    return opener


def extract_discourse_markers(text: str) -> List[str]:
    """
    Session 781 Level 3: Extract discourse markers used in a response.

    This tracks common transitional, agreement, disagreement, filler, and
    hedging phrases to prevent repetition across the conversation.
    """
    if not text:
        return []

    text_lower = text.lower()
    found_markers = []

    for category, markers in DISCOURSE_MARKERS.items():
        for marker in markers:
            if marker in text_lower:
                found_markers.append(marker)

    return found_markers


def get_discourse_avoidance_prompt(used_markers: List[str], max_show: int = 8) -> str:
    """
    Session 781 Level 3: Generate a prompt section listing phrases to avoid.

    Groups the most frequently used markers and instructs the model to
    use fresh language instead.
    """
    if not used_markers:
        return ""

    # Count occurrences
    from collections import Counter
    marker_counts = Counter(used_markers)

    # Get the most overused markers
    most_used = [marker for marker, count in marker_counts.most_common(max_show) if count >= 2]

    if not most_used:
        return ""

    markers_list = ", ".join([f'"{m}"' for m in most_used])

    return f"""
DISCOURSE MEMORY (Session 781 Level 3):
These phrases have been OVERUSED in this conversation - find fresh alternatives:
{markers_list}

Vary your language. Don't fall into repetitive patterns."""


class ConversationOrchestrator:
    """
    Orchestrates multi-agent conversations with contract enforcement.

    Features:
    - Role-specific prompts for each agent type
    - Tension requirement enforcement (challenge every 2-3 turns)
    - Grounding requirement enforcement (metrics + systems)
    - DecisionSummary generation and validation
    - Retry logic for contract violations
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-mini"):
        """
        Initialize the orchestrator.

        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Model to use for generation
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model
        self._client = None
        # Session 826: Lazy-loaded context builders
        self._spider_context = None
        self._advisor_context = None
        self._learning_context = None

    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client

    # Session 826: Lazy-loaded context builders for rich context injection
    @property
    def spider_context_builder(self):
        """Lazy-load SpiderContextBuilder."""
        if self._spider_context is None:
            from core.services.spider_context_builder import get_spider_context_builder
            self._spider_context = get_spider_context_builder()
        return self._spider_context

    @property
    def advisor_context_builder(self):
        """Lazy-load AdvisorContextBuilder."""
        if self._advisor_context is None:
            from core.services.advisor_context_builder import get_advisor_context_builder
            self._advisor_context = get_advisor_context_builder()
        return self._advisor_context

    @property
    def learning_pattern_engine(self):
        """Lazy-load LearningPatternEngine."""
        if self._learning_context is None:
            from core.services.learning_pattern_engine import get_learning_pattern_engine
            self._learning_context = get_learning_pattern_engine()
        return self._learning_context

    def _get_rich_context(self, agent_name: str, topic: str) -> str:
        """
        Session 826: Build rich context from spider, advisor, and learning systems.

        This gives agents real-time intelligence, advisor wisdom, and learned patterns
        to make conversations more grounded and insightful.

        Args:
            agent_name: Name of the agent to get context for
            topic: The conversation topic

        Returns:
            Formatted context string for prompt injection (~115 tokens total)
        """
        if not ENABLE_RICH_CONTEXT:
            return ""

        context_parts = []

        try:
            # Spider data (~50 tokens) - real-time trends and intelligence
            spider_summary = self.spider_context_builder.build_summary(agent_name, topic)
            if spider_summary:
                context_parts.append(f"**Recent Intelligence:** {spider_summary}")
        except Exception as e:
            logger.debug(f"Could not get spider context for {agent_name}: {e}")

        try:
            # Advisor wisdom (~25 tokens) - decision frameworks from legendary advisors
            advisor_summary = self.advisor_context_builder.build_summary(agent_name, topic)
            if advisor_summary:
                context_parts.append(f"**Advisor Insights:** {advisor_summary}")
        except Exception as e:
            logger.debug(f"Could not get advisor context for {agent_name}: {e}")

        try:
            # Learning patterns (~40 tokens) - what this agent has learned
            learning_summary = self.learning_pattern_engine.get_summary(agent_name, topic)
            if learning_summary:
                context_parts.append(f"**Learned Patterns:** {learning_summary}")
        except Exception as e:
            logger.debug(f"Could not get learning context for {agent_name}: {e}")

        if context_parts:
            logger.debug(f"🧠 [Session 826] Rich context built for {agent_name}: {len(context_parts)} sources")
            return "\n".join(context_parts)

        return ""

    def _select_agents_for_topic(
        self,
        topic: str,
        required_capabilities: Optional[List[str]] = None,
        num_agents: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Session 826: Select agents best suited for the conversation topic.

        Uses the AgentRegistry's scoring system to find agents whose capabilities
        match the topic, then ensures diversity by selecting different specializations.

        Args:
            topic: The conversation topic to match agents against
            required_capabilities: Optional list of required capabilities
            num_agents: Number of agents to select (default 2)

        Returns:
            List of agent dicts with name, type, and specialization
        """
        if not ENABLE_AUTO_AGENT_SELECTION:
            return []

        try:
            from core.models.agents_registry.models import AgentRegistry

            # Get or create the registry
            registry, _ = AgentRegistry.objects.get_or_create(
                registry_name='unified_agent_registry'
            )

            # Find agents best suited for this topic
            candidates = registry.find_agents_for_task(
                task_description=topic,
                required_capabilities=required_capabilities,
                limit=num_agents * 3  # Get extras for diversity selection
            )

            if not candidates or len(candidates) < num_agents:
                logger.debug(f"Not enough candidates found for topic '{topic[:50]}...'")
                return []

            # Select diverse agents (different specializations)
            selected = []
            seen_specializations = set()

            for candidate in candidates:
                agent = candidate.get('agent')
                if not agent:
                    continue

                spec = getattr(agent, 'specialization', '') or 'general'

                # Skip if we already have this specialization
                if spec in seen_specializations:
                    continue

                selected.append({
                    'name': agent.name,
                    'type': getattr(agent, 'agent_type', agent.name),
                    'specialization': spec,
                    'score': candidate.get('score', 0)
                })
                seen_specializations.add(spec)

                if len(selected) >= num_agents:
                    break

            if selected:
                agent_names = [a['name'] for a in selected]
                logger.info(f"🎯 [Session 826] Auto-selected agents for topic: {agent_names}")

            return selected

        except Exception as e:
            logger.warning(f"Could not auto-select agents: {e}")
            return []

    def _get_turn_type(self, turn_number: int, conversation_type: str, total_turns: int) -> str:
        """
        Session 826: Get the turn type based on conversation flow.

        Maps the current turn to a structured role in the conversation flow.
        Handles cases where num_turns doesn't match flow length.

        Args:
            turn_number: Current turn (0-indexed)
            conversation_type: Type of conversation (analytical, creative, etc.)
            total_turns: Total number of turns in conversation

        Returns:
            Turn type string (e.g., 'propose', 'challenge', 'synthesize')
        """
        if not ENABLE_STRUCTURED_TURNS:
            return 'discuss'  # Default neutral turn type

        flow = TURN_FLOWS.get(conversation_type, TURN_FLOWS['general'])
        flow_length = len(flow)

        # Map turn_number to flow index
        # For 6 turns with 4-item flow: [0,1] -> 0, [2,3] -> 1, [4] -> 2, [5] -> 3
        if total_turns <= flow_length:
            # Direct mapping
            turn_index = min(turn_number, flow_length - 1)
        else:
            # Spread flow across more turns
            turns_per_phase = total_turns / flow_length
            turn_index = min(int(turn_number / turns_per_phase), flow_length - 1)

        return flow[turn_index]

    def _get_agent_dreams(self, agent_name: str, limit: int = 2) -> List[Dict[str, Any]]:
        """
        Session 811: Get recent dreams for an agent to inject into conversations.

        Uses the existing SciFiIntegrationService._get_recent_dreams() method.

        Args:
            agent_name: Name of the agent
            limit: Maximum number of dreams to return

        Returns:
            List of dream dicts with content, dream_type, and created_at
        """
        if not ENABLE_DREAM_INJECTION:
            return []

        try:
            from core.super_platform.scifi_integration import SciFiIntegrationService
            service = SciFiIntegrationService()
            dreams = service._get_recent_dreams(agent_name, limit=limit)
            return dreams
        except Exception as e:
            logger.warning(f"Could not fetch dreams for {agent_name}: {e}")
            return []

    def _format_dream_context(
        self,
        agent1_name: str,
        agent1_dreams: List[Dict],
        agent2_name: str,
        agent2_dreams: List[Dict]
    ) -> str:
        """
        Session 811: Format dreams from both agents into a context block.

        This gives agents awareness of each other's creative thoughts,
        enabling more meaningful cross-pollination of ideas.

        Args:
            agent1_name: Name of first agent
            agent1_dreams: Dreams from first agent
            agent2_name: Name of second agent
            agent2_dreams: Dreams from second agent

        Returns:
            Formatted string to inject into conversation prompts
        """
        if not agent1_dreams and not agent2_dreams:
            return ""

        lines = ["=== DREAM CONTEXT (Recent Creative Thoughts) ==="]

        if agent1_dreams:
            lines.append(f"\n{agent1_name}'s recent dreams:")
            for i, dream in enumerate(agent1_dreams, 1):
                dream_type = dream.get('dream_type', 'creative')
                content = dream.get('content', '')[:150]
                lines.append(f"  {i}. [{dream_type}] {content}")

        if agent2_dreams:
            lines.append(f"\n{agent2_name}'s recent dreams:")
            for i, dream in enumerate(agent2_dreams, 1):
                dream_type = dream.get('dream_type', 'creative')
                content = dream.get('content', '')[:150]
                lines.append(f"  {i}. [{dream_type}] {content}")

        lines.append("\nConsider how these creative insights might inform this discussion.")
        lines.append("=" * 50)

        return "\n".join(lines)

    def _get_agent_knowledge(self, agent_name: str) -> Dict[str, Any]:
        """
        Session 318: Get an agent's actual learned knowledge and memories.

        This is what makes conversations meaningful - agents bring their
        real experiences and insights to the discussion.
        """
        knowledge = {
            'knowledge_sources': [],
            'memories': [],
            'specialization': ''
        }

        try:
            from core.models import Agent, AgentKnowledgeSource, AgentMemory

            agent = Agent.objects.filter(name=agent_name).first()
            if not agent:
                return knowledge

            knowledge['specialization'] = agent.specialization or ''

            # Get recent knowledge sources (what they've learned)
            sources = AgentKnowledgeSource.objects.filter(
                agent=agent
            ).order_by('-last_updated_at')[:5]

            for source in sources:
                knowledge['knowledge_sources'].append({
                    'title': source.title,
                    'summary': source.summary[:200] if source.summary else ''
                })

            # Get recent memories (their experiences)
            memories = AgentMemory.objects.filter(
                agent=agent
            ).order_by('-created_at')[:5]

            for memory in memories:
                knowledge['memories'].append({
                    'type': memory.memory_type,
                    'content': memory.content[:200] if memory.content else ''
                })

        except Exception as e:
            logger.warning(f"Could not get agent knowledge for {agent_name}: {e}")

        return knowledge

    def _format_agent_context(self, agent_name: str, knowledge: Dict[str, Any]) -> str:
        """
        Session 318: Format an agent's knowledge into conversation context.

        This replaces the generic stats with actual learned insights.
        """
        lines = [f"=== {agent_name.upper()}'S KNOWLEDGE & EXPERIENCE ==="]

        if knowledge.get('specialization'):
            lines.append(f"Specialization: {knowledge['specialization']}")

        if knowledge.get('knowledge_sources'):
            lines.append("\nWhat I've Learned Recently:")
            for source in knowledge['knowledge_sources'][:3]:
                lines.append(f"• {source['title']}")
                if source['summary']:
                    lines.append(f"  → {source['summary'][:150]}...")

        if knowledge.get('memories'):
            lines.append("\nMy Experiences:")
            for memory in knowledge['memories'][:3]:
                lines.append(f"• [{memory['type']}] {memory['content'][:150]}...")

        if not knowledge.get('knowledge_sources') and not knowledge.get('memories'):
            lines.append("(No specific knowledge or memories yet)")

        lines.append("=" * 50)
        return "\n".join(lines)

    def _get_live_system_stats(self) -> Dict[str, Any]:
        """
        Gather real-time system statistics for grounding conversations.

        Session 315: Agents now discuss ACTUAL system state, not placeholders.
        Session 318: Reduced emphasis on raw counts - knowledge context is more important.
        """
        stats = {}

        try:
            # Spider count
            from ai_core.spiders.spider_registry import SpiderRegistry
            registry = SpiderRegistry()
            spider_counts = registry.get_spider_count()
            stats['spider_count'] = spider_counts.get('total', 0)
            stats['spider_categories'] = spider_counts.get('by_category', {})
        except Exception as e:
            logger.warning(f"Could not get spider stats: {e}")
            stats['spider_count'] = 'unknown'

        try:
            # Agent counts
            from core.models import Agent
            stats['active_agents'] = Agent.objects.filter(is_active=True).count()
            stats['total_agents'] = Agent.objects.count()
        except Exception as e:
            logger.warning(f"Could not get agent stats: {e}")
            stats['active_agents'] = 'unknown'

        try:
            # Memory and knowledge stats
            from core.models import AgentMemory, AgentKnowledgeSource
            stats['total_memories'] = AgentMemory.objects.count()
            stats['knowledge_sources'] = AgentKnowledgeSource.objects.count()
        except Exception as e:
            logger.warning(f"Could not get memory stats: {e}")
            stats['total_memories'] = 'unknown'

        try:
            # Spider data stats
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta

            stats['spider_data_total'] = SpiderData.objects.count()
            recent = timezone.now() - timedelta(hours=24)
            stats['spider_data_24h'] = SpiderData.objects.filter(created_at__gte=recent).count()
        except Exception as e:
            logger.warning(f"Could not get spider data stats: {e}")
            stats['spider_data_total'] = 'unknown'

        try:
            # Workflow stats
            from core.models_unified_system import Opportunity, ABTest
            stats['opportunities'] = Opportunity.objects.count()
            stats['ab_tests'] = ABTest.objects.count()
        except Exception as e:
            logger.warning(f"Could not get workflow stats: {e}")

        try:
            # Conversation stats
            from core.models import AgentConversation
            stats['total_conversations'] = AgentConversation.objects.count()
        except Exception as e:
            logger.warning(f"Could not get conversation stats: {e}")

        try:
            # Learning events
            from ai_core.intelligence.models import AgentLearningEvent
            stats['learning_events'] = AgentLearningEvent.objects.count()
        except Exception as e:
            logger.warning(f"Could not get learning stats: {e}")
            stats['learning_events'] = 0

        return stats

    def _format_system_context(self, stats: Dict[str, Any]) -> str:
        """
        Format live system stats into a context block for prompts.

        Session 318: Simplified - don't force agents to parrot numbers.
        The real context comes from agent knowledge, not dashboard stats.
        """
        lines = [
            "=== PLATFORM CONTEXT (Reference Only) ===",
            f"• Active spiders: {stats.get('spider_count', 'N/A')} | Recent data: {stats.get('spider_data_24h', 'N/A')} items",
            f"• Active agents: {stats.get('active_agents', 'N/A')} | Opportunities: {stats.get('opportunities', 'N/A')}",
            "",
            "Focus on your knowledge and experiences, not these numbers.",
            "================================================"
        ]
        return "\n".join(lines)

    def generate_conversation(
        self,
        agent1: Dict[str, Any],
        agent2: Dict[str, Any],
        topic: str,
        conversation_type: str = "brainstorm",
        num_turns: int = 6,
        max_retries: int = 2,
        # Session 826: Goal-driven conversation parameters
        objective: Optional[str] = None,
        success_criteria: Optional[List[str]] = None,
        auto_select_agents: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a complete conversation between two agents.

        Args:
            agent1: First agent dict with name, type, specialization
            agent2: Second agent dict
            topic: Conversation topic
            conversation_type: Type of conversation (analytical, creative, debate, planning, critique, general)
            num_turns: Number of message exchanges (default 6)
            max_retries: Retries per message if contract not met
            objective: Session 826 - Clear goal for the conversation (what should be achieved)
            success_criteria: Session 826 - List of criteria to evaluate outcome
            auto_select_agents: Session 826 - Override agent1/agent2 with topic-matched agents

        Returns:
            Dict with:
                - messages: List of message dicts
                - decision_summary: Extracted DecisionSummary or None
                - validation: Contract validation results
                - state: Conversation state metrics
                - objective: The conversation objective (Session 826)
                - success_criteria: The success criteria (Session 826)
        """
        # Session 826: Auto-select agents if requested
        if auto_select_agents:
            selected = self._select_agents_for_topic(topic, num_agents=2)
            if len(selected) >= 2:
                agent1 = selected[0]
                agent2 = selected[1]
                logger.info(f"🎯 [Session 826] Auto-selected: {agent1['name']} & {agent2['name']}")

        logger.info(f"Starting conversation: {agent1['name']} <-> {agent2['name']} on '{topic}'")

        # Session 786: Store topic for retry prompts in _generate_message
        self._current_topic = topic

        # Session 315: Gather live system stats once for the entire conversation
        system_stats = self._get_live_system_stats()
        system_context = self._format_system_context(system_stats)

        # Session 318: Load ACTUAL knowledge and memories for each agent
        # This is what makes conversations meaningful - real learned insights
        agent1_knowledge = self._get_agent_knowledge(agent1['name'])
        agent2_knowledge = self._get_agent_knowledge(agent2['name'])
        agent1_context = self._format_agent_context(agent1['name'], agent1_knowledge)
        agent2_context = self._format_agent_context(agent2['name'], agent2_knowledge)

        logger.info(f"Agent knowledge loaded: {agent1['name']} has {len(agent1_knowledge.get('knowledge_sources', []))} learnings, "
                    f"{agent2['name']} has {len(agent2_knowledge.get('knowledge_sources', []))} learnings")

        # Session 811: Load dreams for both agents (AI World Enhancement)
        agent1_dreams = self._get_agent_dreams(agent1['name'], limit=2)
        agent2_dreams = self._get_agent_dreams(agent2['name'], limit=2)
        dream_context = self._format_dream_context(
            agent1['name'], agent1_dreams,
            agent2['name'], agent2_dreams
        )
        dreams_injected = len(agent1_dreams) + len(agent2_dreams)
        if dreams_injected > 0:
            logger.info(f"Dreams loaded: {agent1['name']} has {len(agent1_dreams)}, {agent2['name']} has {len(agent2_dreams)}")

        # Session 826: Initialize state with objective and success criteria
        state = ConversationState(
            objective=objective or "",
            success_criteria=success_criteria or [],
            criteria_met=[False] * len(success_criteria or [])
        )
        messages = []
        conversation_context = []

        # Session 826: Build rich context for both agents (spider/advisor/learning)
        agent1_rich_context = self._get_rich_context(agent1['name'], topic) if ENABLE_RICH_CONTEXT else ""
        agent2_rich_context = self._get_rich_context(agent2['name'], topic) if ENABLE_RICH_CONTEXT else ""
        if agent1_rich_context or agent2_rich_context:
            logger.info(f"🧠 [Session 826] Rich context injected for agents")

        for turn in range(num_turns):
            # Alternate between agents
            current_agent = agent1 if turn % 2 == 0 else agent2
            other_agent = agent2 if turn % 2 == 0 else agent1

            # Session 318: Get the right knowledge context for the current speaker
            current_knowledge_context = agent1_context if turn % 2 == 0 else agent2_context

            # Session 826: Get the rich context for the current speaker
            current_rich_context = agent1_rich_context if turn % 2 == 0 else agent2_rich_context

            # Session 826: Get the turn type based on conversation flow
            turn_type = self._get_turn_type(turn, conversation_type, num_turns)

            # Determine if we need to force tension (every 2-3 turns)
            turns_since_tension = turn - state.last_tension_turn
            force_tension = turns_since_tension >= 2
            is_final_turn = (turn == num_turns - 1)

            # Build the prompt for this turn
            prompt = self._build_turn_prompt(
                current_agent=current_agent,
                other_agent=other_agent,
                topic=topic,
                conversation_type=conversation_type,
                turn=turn,
                context=conversation_context,
                force_tension=force_tension,
                is_final_turn=is_final_turn,
                state=state,
                system_context=system_context,
                agent_knowledge_context=current_knowledge_context,  # Session 318: Real knowledge
                dream_context=dream_context,  # Session 811: Dream injection
                # Session 826: Goal-driven conversation enhancements
                rich_context=current_rich_context,
                turn_type=turn_type,
                num_turns=num_turns
            )

            # Generate response with retry logic
            response = self._generate_message(
                prompt=prompt,
                is_final_turn=is_final_turn,
                max_retries=max_retries
            )

            # Analyze and track state
            msg_has_tension = has_tension(response)
            msg_has_grounding = has_grounding(response)
            msg_has_empty_agreement = has_empty_agreement(response)

            state.total_turns += 1
            if msg_has_tension:
                state.tension_count += 1
                state.last_tension_turn = turn
            if msg_has_grounding:
                state.grounding_count += 1
                state.grounding_refs.extend(get_grounding_refs(response))
            if msg_has_empty_agreement:
                state.empty_agreement_count += 1

            # Session 781: Track opener to prevent repetition in future turns
            opener = extract_opener(response)
            if opener:
                state.used_openers.append(opener)
                logger.debug(f"Tracked opener: '{opener[:40]}...'")  # Log first 40 chars

            # Session 781 Level 3: Track discourse markers for comprehensive repetition prevention
            discourse_markers = extract_discourse_markers(response)
            if discourse_markers:
                state.used_discourse_markers.extend(discourse_markers)
                logger.debug(f"Tracked {len(discourse_markers)} discourse markers")

            # Determine message type
            msg_type = self._classify_message(response, turn, num_turns)

            # Store message
            msg_data = {
                'agent': current_agent['name'],
                'agent_type': current_agent.get('type', ''),
                'content': response,
                'type': msg_type,
                'sequence': turn + 1,
                'contains_tension': msg_has_tension,
                'has_grounding': msg_has_grounding,
                'has_empty_agreement': msg_has_empty_agreement,
                'grounding_refs': get_grounding_refs(response)
            }
            messages.append(msg_data)
            conversation_context.append(msg_data)

            logger.debug(f"Turn {turn + 1}: {current_agent['name']} - tension={msg_has_tension}, grounding={msg_has_grounding}")

        # Extract decision summary from final message
        decision_summary = extract_decision_summary(messages[-1]['content'])
        summary_validation = validate_decision_summary(decision_summary)

        # Validate full contract
        validation = self._validate_contract(messages, decision_summary, state)

        logger.info(f"Conversation complete: {len(messages)} messages, valid={validation['is_valid']}")

        # Session 873: Enforce decision via DecisionEnforcerAgent
        execution_mandate = None
        if ENABLE_DECISION_ENFORCEMENT and decision_summary:
            try:
                mandate_result = self._enforce_decision(
                    messages=messages,
                    decision_summary=decision_summary,
                    topic=topic,
                    participants=[agent1['name'], agent2['name']],
                    conversation_type=conversation_type
                )
                execution_mandate = mandate_result.get('mandate')
                if execution_mandate:
                    logger.info(
                        f"🎯 [Session 873] Decision enforced: {execution_mandate.chosen_path[:50]}... "
                        f"(owner: {execution_mandate.decision_owner})"
                    )
            except Exception as e:
                logger.warning(f"[Session 873] Decision enforcement failed: {e}")

        # Session 874: Convert to SynthesisContract for debate-like conversations
        synthesis_contract = None
        synthesis_contract_dict = None
        if ENABLE_SYNTHESIS_CONTRACT and conversation_type in ('debate', 'analytical', 'critique', 'planning'):
            try:
                from core.contracts.synthesis_contract import (
                    SynthesisContract,
                    extract_synthesis_from_decision_summary
                )
                if decision_summary:
                    synthesis_contract = extract_synthesis_from_decision_summary(
                        decision_summary=decision_summary,
                        topic=topic,
                        participants=[agent1['name'], agent2['name']]
                    )
                    # Try to validate but don't fail on weak synthesis
                    try:
                        synthesis_contract.validate()
                        synthesis_contract_dict = synthesis_contract.to_dict()
                        logger.info(
                            f"📋 [Session 874] SynthesisContract created: "
                            f"{len(synthesis_contract.validated)} validated, "
                            f"{len(synthesis_contract.rejected)} rejected, "
                            f"quality_score={synthesis_contract.get_quality_score()}"
                        )
                    except ValueError as ve:
                        # Contract validation failed - still include the raw contract
                        logger.warning(f"[Session 874] SynthesisContract validation warning: {ve}")
                        synthesis_contract_dict = synthesis_contract.to_dict()
                        synthesis_contract_dict['validation_warning'] = str(ve)
            except Exception as e:
                logger.warning(f"[Session 874] SynthesisContract creation failed: {e}")

        # Session 811: AI World Enhancement - Create memories and dispatch actions
        ai_world_metadata = {
            'dreams_injected': dreams_injected,
            'memories_created': 0,
            'actions_dispatched': 0,
            'cluster_created': False,
        }

        # Generate a conversation ID for tracking
        import uuid
        conversation_id = str(uuid.uuid4())

        # Create cross-agent memories from conversation insights
        if ENABLE_CROSS_AGENT_MEMORY and decision_summary:
            try:
                from core.services.conversation_memory_service import create_conversation_memories
                memory_result = create_conversation_memories(
                    conversation_id=conversation_id,
                    participants=[agent1['name'], agent2['name']],
                    decision_summary=decision_summary,
                    topic=topic,
                    messages=messages
                )
                ai_world_metadata['memories_created'] = memory_result.get('memories_created', 0)
                ai_world_metadata['cluster_created'] = memory_result.get('cluster_created', False)
                ai_world_metadata['cluster_id'] = memory_result.get('cluster_id')
            except Exception as e:
                logger.warning(f"Failed to create conversation memories: {e}")

        # Session 884: Extract deliverables from conversation output
        # This creates Deliverable records from valuable content (personas, plans, analyses)
        deliverable_extraction = {'deliverables_created': 0}
        if decision_summary and messages:
            try:
                from core.services.conversation_deliverable_extractor import extract_conversation_deliverables
                deliverable_extraction = extract_conversation_deliverables(
                    conversation_id=conversation_id,
                    messages=messages,
                    decision_summary=decision_summary,
                    participants=[agent1['name'], agent2['name']],
                    topic=topic
                )
                ai_world_metadata['deliverables_created'] = deliverable_extraction.get('deliverables_created', 0)
                ai_world_metadata['deliverable_ids'] = deliverable_extraction.get('deliverable_ids', [])

                # Use concrete next steps from extraction if available
                concrete_steps = deliverable_extraction.get('concrete_next_steps', [])
                if concrete_steps:
                    logger.info(f"📦 Session 884: Created {len(concrete_steps)} concrete next steps from deliverable")
            except Exception as e:
                logger.warning(f"Failed to extract conversation deliverables: {e}")

        # Dispatch next_steps as actual agent tasks
        if ENABLE_ACTION_DISPATCH and decision_summary and decision_summary.get('next_steps'):
            try:
                from core.services.conversation_action_dispatcher import dispatch_conversation_actions

                # Session 884: If we have concrete steps from deliverable extraction, use those
                # instead of vague "document insights" type steps
                concrete_steps = deliverable_extraction.get('concrete_next_steps', [])
                if concrete_steps:
                    # Convert concrete steps to dispatch format
                    enhanced_summary = {
                        **decision_summary,
                        'next_steps': [f"{s['agent']}: {s['task']}" for s in concrete_steps]
                    }
                    dispatch_summary = enhanced_summary
                else:
                    dispatch_summary = decision_summary

                dispatch_result = dispatch_conversation_actions(
                    conversation_id=conversation_id,
                    decision_summary=dispatch_summary,
                    participants=[agent1['name'], agent2['name']],
                    context={'topic': topic, 'conversation_type': conversation_type}
                )
                ai_world_metadata['actions_dispatched'] = dispatch_result.get('dispatched_count', 0)
                ai_world_metadata['actions_failed'] = dispatch_result.get('failed_count', 0)
            except Exception as e:
                logger.warning(f"Failed to dispatch conversation actions: {e}")

        return {
            'messages': messages,
            'decision_summary': decision_summary,
            'summary_validation': summary_validation,
            'validation': validation,
            'state': {
                'total_turns': state.total_turns,
                'tension_count': state.tension_count,
                'grounding_count': state.grounding_count,
                'empty_agreement_count': state.empty_agreement_count,
                'unique_grounding_refs': list(set(state.grounding_refs)),
                # Session 781: Track unique openers used
                'unique_openers_count': len(set(state.used_openers)),
                'used_openers': state.used_openers,
                # Session 781 Level 3: Discourse marker stats
                'discourse_markers_total': len(state.used_discourse_markers),
                'discourse_markers_unique': len(set(state.used_discourse_markers)),
                'overused_phrases': self._get_overused_phrases(state.used_discourse_markers)
            },
            'topic': topic,
            'participants': [agent1['name'], agent2['name']],
            'conversation_type': conversation_type,
            'conversation_id': conversation_id,  # Session 811
            'ai_world': ai_world_metadata,  # Session 811: AI World Enhancement
            # Session 826: Goal-driven conversation metadata
            'objective': objective,
            'success_criteria': success_criteria,
            'auto_selected_agents': auto_select_agents,
            'rich_context_injected': bool(agent1_rich_context or agent2_rich_context),
            # Session 873: Decision Enforcement
            'execution_mandate': execution_mandate.to_dict() if execution_mandate else None,
            # Session 874: SynthesisContract for structured debate output
            'synthesis_contract': synthesis_contract_dict,
        }

    def _enforce_decision(
        self,
        messages: List[Dict[str, Any]],
        decision_summary: Dict[str, Any],
        topic: str,
        participants: List[str],
        conversation_type: str
    ) -> Dict[str, Any]:
        """
        Session 873: Enforce a decisive outcome using DecisionEnforcerAgent.

        This is the "Prefrontal Cortex" - it forces decisions after debate
        to prevent "further analysis recommended" loops.

        Args:
            messages: The conversation transcript
            decision_summary: Extracted decision summary from conversation
            topic: What the conversation was about
            participants: List of agent names that participated
            conversation_type: Type of conversation (debate, analytical, etc.)

        Returns:
            Dict with 'mandate' (ExecutionMandate) if successful, 'error' if not
        """
        from core.agents.decision_enforcer_agent import DecisionEnforcerAgent
        from core.contracts.execution_mandate import ExecutionMandate

        # Only enforce for debate-like conversations
        if conversation_type not in ('debate', 'analytical', 'critique', 'planning'):
            logger.debug(f"[Session 873] Skipping decision enforcement for {conversation_type} conversation")
            return {'mandate': None, 'skipped': True, 'reason': f'conversation_type={conversation_type}'}

        # Build synthesis dict from decision_summary
        synthesis = {
            'insights': decision_summary.get('insights', []),
            'proposed_feature': decision_summary.get('proposed_feature', ''),
            'next_steps': decision_summary.get('next_steps', []),
            'decision': decision_summary.get('decision', ''),
            'participants': participants,
        }

        # Execute the DecisionEnforcerAgent
        agent = DecisionEnforcerAgent(user=getattr(self, 'user', None))
        result = agent.execute(
            task=f"Enforce decision from {conversation_type} on: {topic}",
            context={
                'debate_messages': messages,
                'synthesis': synthesis,
                'topic': topic,
            }
        )

        if result.success:
            mandate_data = result.data.get('mandate', {})
            # Reconstruct the ExecutionMandate object from dict
            from core.contracts.execution_mandate import SpawnedTask, MandateStatus
            spawned_tasks = [
                SpawnedTask(**t) if isinstance(t, dict) else t
                for t in mandate_data.get('spawned_tasks', [])
            ]
            mandate = ExecutionMandate(
                chosen_path=mandate_data.get('chosen_path', ''),
                reason=mandate_data.get('reason', ''),
                decision_owner=mandate_data.get('decision_owner', ''),
                kill_criteria=mandate_data.get('kill_criteria', []),
                deadline=mandate_data.get('deadline', ''),
                experiments=mandate_data.get('experiments', []),
                rejected_paths=mandate_data.get('rejected_paths', {}),
                acknowledged_risks=mandate_data.get('acknowledged_risks', []),
                confidence=mandate_data.get('confidence', 0.6),
                confidence_reason=mandate_data.get('confidence_reason', ''),
                spawned_tasks=spawned_tasks,
                status=MandateStatus.ACTIVE,
            )
            logger.info(
                f"[Session 873] DecisionEnforcerAgent success: {mandate.chosen_path[:100]}"
            )
            return {'mandate': mandate, 'markdown': result.data.get('mandate_markdown', '')}
        else:
            logger.warning(f"[Session 873] DecisionEnforcerAgent failed: {result.error}")
            return {'mandate': None, 'error': result.error}

    def _build_turn_prompt(
        self,
        current_agent: Dict[str, Any],
        other_agent: Dict[str, Any],
        topic: str,
        conversation_type: str,
        turn: int,
        context: List[Dict],
        force_tension: bool,
        is_final_turn: bool,
        state: ConversationState,
        system_context: str = "",  # Session 315: Live system stats
        agent_knowledge_context: str = "",  # Session 318: Agent's real knowledge
        dream_context: str = "",  # Session 811: Dream injection
        # Session 826: Goal-driven conversation parameters
        rich_context: str = "",
        turn_type: str = "discuss",
        num_turns: int = 6
    ) -> str:
        """Build the complete prompt for a conversation turn."""

        # Get role-specific system prompt
        role_prompt = get_conversation_role(
            agent_name=current_agent['name'],
            agent_type=current_agent.get('type', ''),
            specialization=current_agent.get('specialization', '')
        )

        # Build context string from previous messages
        if context:
            context_lines = []
            for m in context[-4:]:  # Last 4 messages for context
                context_lines.append(f"{m['agent']}: {m['content']}")
            context_str = "\n\n".join(context_lines)
        else:
            context_str = "[This is the opening message - you speak first]"

        # Build conversation type instructions
        type_instructions = self._get_conversation_type_instructions(conversation_type)

        # Build turn-specific instructions
        turn_instructions = []

        # Session 826: Add objective-focused preamble if objective is set
        if state.objective:
            turn_instructions.append(f"""CONVERSATION OBJECTIVE:
This conversation has a clear goal: {state.objective}

Keep this objective in mind as you respond. Every contribution should move toward achieving this goal.""")

        # Session 826: Add structured turn directive
        if ENABLE_STRUCTURED_TURNS and turn_type in TURN_PROMPTS:
            turn_directive = TURN_PROMPTS[turn_type]
            turn_instructions.append(f"""TURN ROLE ({turn_type.upper()}):
{turn_directive}""")

        if turn == 0:
            turn_instructions.append(f"""OPENING MESSAGE INSTRUCTIONS:
You are starting a {conversation_type} conversation about: "{topic}"

- Open with an insight FROM YOUR KNOWLEDGE ABOVE - reference what you've learned
- Set the stage for a productive discussion
- Share a specific experience or learning that's relevant
- Keep it to 2-3 sentences""")
        else:
            turn_instructions.append(f"""RESPONSE INSTRUCTIONS:
Continue this {conversation_type} conversation about: "{topic}"

- Respond directly to what {other_agent['name']} just said
- Draw on YOUR specific experiences and learnings from above
- Build toward actionable conclusions
- Keep it to 2-4 sentences""")

        # Force tension if needed (Session 781: Use role-specific disagreement styles)
        if force_tension:
            turn_instructions.append("""
TENSION REQUIREMENT (MANDATORY FOR THIS TURN):
You MUST include constructive tension in this response.

Use YOUR ROLE-SPECIFIC DISAGREEMENT STYLE from above - challenge from your unique expertise.

NEVER use these generic hedging phrases:
- "I'd push back slightly..."
- "That's a great point, but..."
- "However, I'd question whether..."
- "I agree, however..."
- "With all due respect..."

Instead, disagree DIRECTLY using your domain voice (examples in Your Disagreement Style above).
Add friction to make this conversation valuable - but do it YOUR way.""")

        # Final turn requirements
        if is_final_turn:
            turn_instructions.append(f"""
FINAL MESSAGE REQUIREMENTS (CRITICAL):
This is the LAST message of the conversation. You MUST:

1. Synthesize the key points discussed
2. End with the EXACT DecisionSummary format below

{CONVERSATION_CONTRACT.split('3. OUTPUT REQUIREMENT:')[1]}

The DecisionSummary MUST appear at the end of your message. This is required.""")

        # Session 318: Removed generic grounding reminder
        # Agents now ground in their ACTUAL knowledge/experiences, not generic platform stats

        # Anti-agreement reminder (Session 781: Updated with explicit bans)
        turn_instructions.append("""
VOICE RULES:
- NEVER say: "Absolutely!", "Great point!", "I love that!", "Exactly right!"
- NEVER use: "I'd push back slightly", "That's a fair point", "I agree, but..."
- If you agree, add value from YOUR expertise - don't just validate
- Speak in YOUR distinct voice, not corporate AI hedging""")

        # Session 781: De-duplication - prevent reusing openers from this conversation
        if state.used_openers:
            # Show recent openers (last 5) so agent knows what to avoid
            recent_openers = state.used_openers[-5:]
            openers_list = "\n".join([f'- "{op}"' for op in recent_openers])
            turn_instructions.append(f"""
OPENER DE-DUPLICATION (CRITICAL):
These opening phrases have ALREADY been used in this conversation. Do NOT start with similar phrasing:
{openers_list}

Start your response with a FRESH, UNIQUE opening that hasn't been used yet.""")

        # Session 781 Level 3: Discourse memory - prevent overused phrases
        discourse_avoidance = get_discourse_avoidance_prompt(state.used_discourse_markers)
        if discourse_avoidance:
            turn_instructions.append(discourse_avoidance)

        # Assemble full prompt with agent knowledge (Session 318), system context, dreams (Session 811), and rich context (Session 826)
        prompt = f"""{role_prompt}

{agent_knowledge_context}

{dream_context}

{rich_context}

{system_context}

{type_instructions}

=== CONVERSATION SO FAR ===
{context_str}

=== YOUR TURN ({current_agent['name']} responding to {other_agent['name']}) ===

{chr(10).join(turn_instructions)}

Draw on your knowledge and experiences above. If relevant, reference the creative dreams shared above or the recent intelligence provided. Write your response now. Do NOT prefix with your name - just write the message content directly."""

        return prompt

    def _get_conversation_type_instructions(self, conversation_type: str) -> str:
        """Get instructions specific to conversation type."""
        instructions = {
            # Session 826: New structured conversation types
            'analytical': """CONVERSATION TYPE: Analytical Discussion
Goal: Rigorously analyze a topic through structured reasoning
Flow: Propose → Challenge → Synthesize → Decide
Approach: Use data and evidence. Challenge assumptions. Build toward a clear decision.""",

            'creative': """CONVERSATION TYPE: Creative Exploration
Goal: Generate innovative ideas through collaborative ideation
Flow: Brainstorm → Expand → Refine → Select
Approach: Think boldly. Build on ideas. Refine the best ones. Select winners.""",

            'debate': """CONVERSATION TYPE: Structured Debate
Goal: Explore opposing viewpoints to find the strongest position
Flow: Position → Counter → Rebut → Conclude
Approach: Argue clearly. Listen to counter-arguments. Seek truth, not victory.""",

            'planning': """CONVERSATION TYPE: Implementation Planning
Goal: Create actionable plan with clear steps and ownership
Flow: Goals → Steps → Dependencies → Schedule
Approach: Be specific. Identify blockers. Assign ownership. Set timelines.""",

            'critique': """CONVERSATION TYPE: Constructive Critique
Goal: Stress-test an idea through rigorous analysis
Flow: Present → Challenge → Defend → Improve
Approach: Find weaknesses, propose improvements, validate strengths.""",

            'general': """CONVERSATION TYPE: Open Discussion
Goal: Explore a topic freely while building toward insights
Flow: Explore → Discuss → Clarify → Summarize
Approach: Share perspectives. Ask questions. Build understanding. Summarize learnings.""",

            # Legacy types (kept for backwards compatibility)
            'brainstorm': """CONVERSATION TYPE: Strategic Brainstorm
Goal: Generate innovative ideas while maintaining practicality
Approach: Build on ideas, but challenge weak ones. Push for specifics.""",

            'consultation': """CONVERSATION TYPE: Expert Consultation
Goal: One agent consults the other's expertise
Approach: Ask probing questions, give detailed answers with caveats.""",

            'synthesis': """CONVERSATION TYPE: Knowledge Synthesis
Goal: Combine different perspectives into unified insights
Approach: Find connections, resolve contradictions, create frameworks.""",

            'analysis': """CONVERSATION TYPE: Deep Analysis
Goal: Thoroughly analyze a topic from multiple angles
Approach: Examine data, consider implications, draw conclusions."""
        }

        return instructions.get(conversation_type, instructions['brainstorm'])

    def _get_overused_phrases(self, markers: List[str], threshold: int = 2) -> List[Dict[str, Any]]:
        """
        Session 781 Level 3: Get list of overused discourse phrases.

        Returns phrases that were used more than `threshold` times with their counts.
        """
        from collections import Counter
        marker_counts = Counter(markers)
        return [
            {'phrase': phrase, 'count': count}
            for phrase, count in marker_counts.most_common()
            if count >= threshold
        ]

    def _generate_message(
        self,
        prompt: str,
        is_final_turn: bool,
        max_retries: int
    ) -> str:
        """Generate a message with retry logic for contract compliance."""

        # GPT-5 reasoning models: max_output_tokens includes BOTH reasoning + text
        # Need higher values to leave room for text after reasoning
        # Session 318: Increased from 1000 to 1500 for regular turns to fix empty messages
        # Final turn needs more for DecisionSummary
        max_output_tokens = 2500 if is_final_turn else 1500

        for attempt in range(max_retries + 1):
            try:
                # Use GPT-5 Responses API (Session 314 migration)
                response = self.client.responses.create(
                    model=self.model,
                    input=prompt,
                    reasoning={"effort": "medium"},
                    text={"verbosity": "medium"},
                    max_output_tokens=max_output_tokens,
                )

                content = response.output_text.strip() if response.output_text else ""

                # Session 318: Retry with higher tokens if response was incomplete or empty
                if response.status == 'incomplete' or not content:
                    logger.warning(f"Response incomplete or empty (attempt {attempt + 1}): {response.incomplete_details if hasattr(response, 'incomplete_details') else 'no content'}")
                    if attempt < max_retries:
                        # Try again with even more tokens
                        max_output_tokens = min(max_output_tokens + 500, 4000)
                        continue

                # Session 786: For final turn, validate and ENFORCE decision summary presence
                if is_final_turn:
                    if "=== DecisionSummary ===" not in content:
                        if attempt < max_retries:
                            logger.warning(f"Final turn missing DecisionSummary, retry {attempt + 1}/{max_retries}")
                            # Build a completely new, focused prompt for the retry
                            prompt = f"""You are writing the FINAL message in a conversation about: {self._current_topic if hasattr(self, '_current_topic') else 'a strategic topic'}

Your task is SIMPLE: Write a concluding message that includes the DecisionSummary block.

REQUIRED OUTPUT FORMAT - You MUST include this EXACT structure:

=== DecisionSummary ===
Insights:
1. [First key insight from the conversation]
2. [Second insight about implementation or approach]
3. [Third insight about impact or considerations]

Proposed Feature:
- Name: [Specific feature name based on what was discussed]
- Inputs: [What data or content the feature needs]
- Outputs: [What the feature produces]
- Where it plugs into the system: [Component like dashboard, API, workflow, etc.]

Next Steps:
1. [First concrete action with owner, e.g. "ResearchAgent: analyze X"]
2. [Second concrete action with owner]

Write a brief concluding paragraph (2-3 sentences) summarizing the discussion, then include the DecisionSummary block above. This is REQUIRED."""
                            continue
                        else:
                            # Session 786: Force append DecisionSummary if still missing after all retries
                            logger.warning(f"DecisionSummary still missing after {max_retries} retries, appending placeholder")
                            content += """

=== DecisionSummary ===
Insights:
1. Discussion explored multiple strategic perspectives
2. Trade-offs were identified between approaches
3. Further analysis recommended before implementation

Proposed Feature:
- Name: Discussion Outcome Tracker
- Inputs: Conversation insights and action items
- Outputs: Prioritized recommendations
- Where it plugs into the system: Knowledge base and planning workflows

Next Steps:
1. ResearchAgent: Synthesize key findings from this discussion
2. ContentStrategyAgent: Develop implementation roadmap"""

                return content

            except Exception as e:
                logger.error(f"Error generating message (attempt {attempt + 1}): {e}")
                if attempt == max_retries:
                    return f"[Message generation failed: {str(e)}]"

        return content

    def _classify_message(self, content: str, turn: int, total_turns: int) -> str:
        """Classify message type based on content analysis."""
        content_lower = content.lower()

        if turn == total_turns - 1:
            return 'conclusion'

        if '?' in content and content.count('?') >= 1:
            return 'question'

        # Check for tension/challenge
        tension_words = ['however', 'but', 'concern', 'trade-off', 'caveat', 'alternative']
        if any(word in content_lower for word in tension_words):
            return 'challenge'

        # Check for proposals
        proposal_words = ['propose', 'suggest', 'we should', 'let\'s', 'recommend', 'consider']
        if any(word in content_lower for word in proposal_words):
            return 'proposal'

        # Check for framework creation
        if 'call this' in content_lower or 'framework' in content_lower or 'pattern' in content_lower:
            return 'framework'

        return 'statement'

    def _validate_contract(
        self,
        messages: List[Dict],
        decision_summary: Optional[Dict],
        state: ConversationState
    ) -> Dict[str, Any]:
        """Validate that conversation meets all contract requirements."""

        # Tension validation
        tension_met = state.tension_count >= 2

        # Grounding validation
        grounding_met = state.grounding_count >= 2

        # Decision summary validation
        summary_validation = validate_decision_summary(decision_summary)

        # Overall validity
        is_valid = all([
            tension_met,
            grounding_met,
            summary_validation['is_valid']
        ])

        # Compile issues
        issues = []
        if not tension_met:
            issues.append(f"Insufficient tension: {state.tension_count}/2 required")
        if not grounding_met:
            issues.append(f"Insufficient grounding: {state.grounding_count}/2 required")
        if not summary_validation['has_insights']:
            issues.append(f"Insufficient insights: {summary_validation['insights_count']}/3 required")
        if not summary_validation['has_feature']:
            issues.append("Missing proposed feature in DecisionSummary")
        if not summary_validation['has_next_steps']:
            issues.append(f"Insufficient next steps: {summary_validation['next_steps_count']}/2 required")
        if state.empty_agreement_count > 0:
            issues.append(f"Warning: {state.empty_agreement_count} instances of empty agreement detected")

        return {
            'is_valid': is_valid,
            'tension_count': state.tension_count,
            'tension_required': 2,
            'tension_met': tension_met,
            'grounding_count': state.grounding_count,
            'grounding_required': 2,
            'grounding_met': grounding_met,
            'has_decision_summary': decision_summary is not None,
            'summary_validation': summary_validation,
            'empty_agreement_count': state.empty_agreement_count,
            'issues': issues,
            'score': self._calculate_quality_score(state, summary_validation)
        }

    def _calculate_quality_score(
        self,
        state: ConversationState,
        summary_validation: Dict
    ) -> int:
        """
        Calculate overall conversation quality score (0-100).

        Session 840: Enhanced scoring to reward high-value signals
        (experiments, KPIs, owners, budgets, risks, architecture)
        and penalize generic "productive discussion" summaries.
        """
        score = 0

        # Tension contribution (20 points max) - reduced from 30
        tension_score = min(state.tension_count * 10, 20)
        score += tension_score

        # Grounding contribution (20 points max) - reduced from 30
        grounding_score = min(state.grounding_count * 10, 20)
        score += grounding_score

        # Decision summary contribution (20 points max) - reduced from 40
        if summary_validation.get('has_insights'):
            score += 8
        if summary_validation.get('has_feature'):
            score += 7
        if summary_validation.get('has_next_steps'):
            score += 5

        # Session 840: High-value signals contribution (40 points max)
        # This is now the biggest scoring factor - concrete, actionable content
        high_value_score = summary_validation.get('high_value_score', 0)
        # Cap at 40 points
        score += min(high_value_score, 40)

        # Penalty for empty agreement
        score -= state.empty_agreement_count * 5

        # Session 840: Penalty for generic summaries
        generic_penalty = summary_validation.get('generic_penalty', 0)
        score -= generic_penalty

        # Session 840: Extra penalty if summary is flagged as generic
        if summary_validation.get('is_generic', False):
            score -= 15  # Additional penalty for overall generic tone

        return max(0, min(100, score))


# Convenience function for quick conversation generation
def generate_upgraded_conversation(
    agent1_name: str,
    agent1_type: str,
    agent2_name: str,
    agent2_type: str,
    topic: str,
    agent1_specialization: str = "",
    agent2_specialization: str = "",
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for generating upgraded conversations.

    Args:
        agent1_name: Name of first agent
        agent1_type: Type of first agent
        agent2_name: Name of second agent
        agent2_type: Type of second agent
        topic: Conversation topic
        agent1_specialization: Optional specialization for agent 1
        agent2_specialization: Optional specialization for agent 2
        **kwargs: Additional args passed to generate_conversation

    Returns:
        Conversation result dict
    """
    orchestrator = ConversationOrchestrator()

    return orchestrator.generate_conversation(
        agent1={
            'name': agent1_name,
            'type': agent1_type,
            'specialization': agent1_specialization
        },
        agent2={
            'name': agent2_name,
            'type': agent2_type,
            'specialization': agent2_specialization
        },
        topic=topic,
        **kwargs
    )


__all__ = [
    'ConversationOrchestrator',
    'ConversationState',
    'generate_upgraded_conversation',
]

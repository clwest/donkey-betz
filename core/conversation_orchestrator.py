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

    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client

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
            from core.models_unified_system import AgentLearningEvent
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
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a complete conversation between two agents.

        Args:
            agent1: First agent dict with name, type, specialization
            agent2: Second agent dict
            topic: Conversation topic
            conversation_type: Type of conversation (brainstorm, consultation, synthesis, critique)
            num_turns: Number of message exchanges (default 6)
            max_retries: Retries per message if contract not met

        Returns:
            Dict with:
                - messages: List of message dicts
                - decision_summary: Extracted DecisionSummary or None
                - validation: Contract validation results
                - state: Conversation state metrics
        """
        logger.info(f"Starting conversation: {agent1['name']} <-> {agent2['name']} on '{topic}'")

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

        state = ConversationState()
        messages = []
        conversation_context = []

        for turn in range(num_turns):
            # Alternate between agents
            current_agent = agent1 if turn % 2 == 0 else agent2
            other_agent = agent2 if turn % 2 == 0 else agent1

            # Session 318: Get the right knowledge context for the current speaker
            current_knowledge_context = agent1_context if turn % 2 == 0 else agent2_context

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
                agent_knowledge_context=current_knowledge_context  # Session 318: Real knowledge
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
                'unique_grounding_refs': list(set(state.grounding_refs))
            },
            'topic': topic,
            'participants': [agent1['name'], agent2['name']],
            'conversation_type': conversation_type
        }

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
        agent_knowledge_context: str = ""  # Session 318: Agent's real knowledge
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

        # Force tension if needed
        if force_tension:
            turn_instructions.append("""
TENSION REQUIREMENT (MANDATORY FOR THIS TURN):
You MUST include constructive tension in this response. Use one of these approaches:

- Challenge an assumption: "However, I'd question whether..."
- Highlight a trade-off: "The trade-off here is..."
- Offer an alternative: "What if instead we..."
- Raise a concern: "My concern with that approach is..."
- Add a caveat: "That works, but we should be careful about..."

DO NOT just agree. Add friction to make this conversation valuable.""")

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

        # Anti-agreement reminder
        turn_instructions.append("""
AGREEMENT RULES:
- NEVER say: "Absolutely!", "Great point!", "I love that!", "Exactly right!"
- If you agree, still add nuance: "That aligns with the data, though one consideration is..."
- Always contribute something new, don't just validate""")

        # Assemble full prompt with agent knowledge (Session 318) and system context
        prompt = f"""{role_prompt}

{agent_knowledge_context}

{system_context}

{type_instructions}

=== CONVERSATION SO FAR ===
{context_str}

=== YOUR TURN ({current_agent['name']} responding to {other_agent['name']}) ===

{chr(10).join(turn_instructions)}

Draw on your knowledge and experiences above. Write your response now. Do NOT prefix with your name - just write the message content directly."""

        return prompt

    def _get_conversation_type_instructions(self, conversation_type: str) -> str:
        """Get instructions specific to conversation type."""
        instructions = {
            'brainstorm': """CONVERSATION TYPE: Strategic Brainstorm
Goal: Generate innovative ideas while maintaining practicality
Approach: Build on ideas, but challenge weak ones. Push for specifics.""",

            'consultation': """CONVERSATION TYPE: Expert Consultation
Goal: One agent consults the other's expertise
Approach: Ask probing questions, give detailed answers with caveats.""",

            'synthesis': """CONVERSATION TYPE: Knowledge Synthesis
Goal: Combine different perspectives into unified insights
Approach: Find connections, resolve contradictions, create frameworks.""",

            'critique': """CONVERSATION TYPE: Constructive Critique
Goal: Stress-test an idea through rigorous analysis
Approach: Find weaknesses, propose improvements, validate strengths.""",

            'planning': """CONVERSATION TYPE: Implementation Planning
Goal: Create actionable plan from abstract idea
Approach: Break down into steps, identify dependencies, assign ownership.""",

            'analysis': """CONVERSATION TYPE: Deep Analysis
Goal: Thoroughly analyze a topic from multiple angles
Approach: Examine data, consider implications, draw conclusions."""
        }

        return instructions.get(conversation_type, instructions['brainstorm'])

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

                # For final turn, validate decision summary presence
                if is_final_turn and attempt < max_retries:
                    if "=== DecisionSummary ===" not in content:
                        logger.warning(f"Final turn missing DecisionSummary, retry {attempt + 1}/{max_retries}")
                        prompt += """

CRITICAL: Your response is MISSING the DecisionSummary block!

You MUST end your response with:

=== DecisionSummary ===
Insights:
1. [First insight]
2. [Second insight]
3. [Third insight]

Proposed Feature:
- Name: [Feature name]
- Inputs: [What it needs]
- Outputs: [What it produces]
- Where it plugs into the system: [Integration point]

Next Steps:
1. [First action]
2. [Second action]

Include this NOW."""
                        continue

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
        """Calculate overall conversation quality score (0-100)."""
        score = 0

        # Tension contribution (30 points max)
        tension_score = min(state.tension_count * 10, 30)
        score += tension_score

        # Grounding contribution (30 points max)
        grounding_score = min(state.grounding_count * 10, 30)
        score += grounding_score

        # Decision summary contribution (40 points max)
        if summary_validation['has_insights']:
            score += 15
        if summary_validation['has_feature']:
            score += 15
        if summary_validation['has_next_steps']:
            score += 10

        # Penalty for empty agreement
        score -= state.empty_agreement_count * 5

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

# Session 261: Agent Conversation Upgrade Implementation Plan

**Date:** November 28, 2025
**Phase:** Agent Conversation Quality Overhaul
**Goal:** Transform agent-to-agent conversations from polite and generic to useful and outcome-driven

---

## Executive Summary

This document outlines the complete implementation plan for upgrading the agent conversation system. The upgrade addresses five critical problems identified in the current system:

1. **Over-agreeable tone** - Agents constantly agree without challenge
2. **Generic content** - Conversations could apply to any platform
3. **No strategic artifacts** - No frameworks, specs, or decisions produced
4. **Not grounded in platform** - No references to RAG, embeddings, dashboards
5. **Open-ended conclusions** - No clear next steps or actionable outcomes

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Agent Role Definitions](#2-agent-role-definitions)
3. [Conversation Contract](#3-conversation-contract)
4. [Implementation Tasks](#4-implementation-tasks)
5. [Code Changes](#5-code-changes)
6. [Testing Strategy](#6-testing-strategy)
7. [Rollout Plan](#7-rollout-plan)

---

## 1. Architecture Overview

### Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Agent Conversation System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WebSocket Consumer                    GPT-4o-mini               │
│  (agent_conversation_consumer.py)  →   (generic prompts)        │
│           ↓                                   ↓                  │
│  Random agent selection              Basic turn-by-turn chat    │
│           ↓                                   ↓                  │
│  ConversationMessage model           No structure enforcement    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Enhanced Agent Conversation System                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Conversation Orchestrator                                       │
│  (conversation_orchestrator.py)                                  │
│           ↓                                                      │
│  Agent Role Definitions ─────────────────────────────────────┐   │
│  • ResearchAgent: Data realist, pattern enforcer             │   │
│  • ContentStrategyAgent: Storytelling, psychology, features  │   │
│           ↓                                                  │   │
│  Conversation Contract                                       │   │
│  • Tension requirement (critique every 2-3 turns)            │   │
│  • Grounding requirement (platform references)               │   │
│  • Output requirement (DecisionSummary block)                │   │
│           ↓                                                  │   │
│  GPT-4o-mini with Role-Specific Prompts                      │   │
│           ↓                                                  │   │
│  Structured Output Parser                                    │   │
│  • Extracts DecisionSummary                                  │   │
│  • Validates tension presence                                │   │
│  • Ensures grounding references                              │   │
│           ↓                                                  │   │
│  ConversationMessage + ConversationArtifact models           │   │
│                                                              │   │
└──────────────────────────────────────────────────────────────┘   │
                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Agent Role Definitions

### 2.1 ResearchAgent - The Data Realist

**Primary Role:** Bring data, patterns, and trade-offs to conversations. Challenge vague claims.

**System Prompt Template:**
```
You are ResearchAgent, the data realist and pattern enforcer of our AI Content Studio platform.

YOUR RESPONSIBILITIES:
1. Bring concrete data, patterns, and trade-offs to every conversation
2. Question vague or fluffy claims - always ask "What does the data say?"
3. Propose specific metrics, queries, and experiments
4. Ground discussions in measurable, buildable outcomes

BEHAVIORAL RULES:
- At least once every 2 responses, challenge an assumption or push for more precision
- NEVER use generic praise like "Great point!" or "Absolutely!"
- Instead, acknowledge and refine: "That partially matches the data, but..." or "The pattern suggests a nuance here..."
- Use concrete numbers or plausible placeholders: "Let's assume 7-11 minute read time correlates with..."

OUTPUT STYLE:
- Reference our platform systems: embeddings, RAG retrieval, spider data, scoring dashboards
- Propose measurable experiments: "We should A/B test X vs Y and measure Z"
- Cite specific metrics: "reading time", "scroll depth", "claps per view", "retention after 30 seconds"
- Always connect ideas to something we can BUILD or MEASURE

PLATFORM CONTEXT:
You have access to:
- 67 spiders across 17 categories collecting real data
- RAG embeddings for semantic search
- Scoring dashboards and analytics
- A/B testing framework
- User engagement metrics

When discussing ideas, ALWAYS tie them back to how we could implement them using these systems.
```

### 2.2 ContentStrategyAgent - The Storytelling Strategist

**Primary Role:** Convert analytical insights into powerful content and product strategy.

**System Prompt Template:**
```
You are ContentStrategyAgent, the storytelling and psychology specialist of our AI Content Studio platform.

YOUR RESPONSIBILITIES:
1. Translate data patterns into positioning, narrative, and buildable features
2. Care about audience psychology, emotional resonance, and long-term brand value
3. Turn abstract ideas into named frameworks and feature specifications
4. Drive conversations toward concrete deliverables

BEHAVIORAL RULES:
- At least once every 2 responses, consider trade-offs (virality vs depth, click-through vs trust)
- Push back if data-only approaches hurt narrative quality or authenticity
- Create and name frameworks: "Hook-Story-Depth pattern", "Authority vs Virality trade-off"
- NEVER give empty agreement - always add nuance, limitation, or alternative perspective

OUTPUT STYLE:
- Use named patterns and frameworks whenever possible
- Push toward actionable artifacts: roadmaps, modules, dashboard designs
- Consider user psychology: "This creates cognitive load..." or "The emotional hook here is..."
- End contributions with clear implications for what we should BUILD

PLATFORM CONTEXT:
You can propose features that integrate with:
- Content reflection UI for feedback loops
- Scoring systems and quality panels
- Workflow orchestration for automated pipelines
- Dashboard widgets for creator insights
- RAG-powered recommendation systems

When proposing ideas, specify HOW they would integrate with our existing infrastructure.
```

---

## 3. Conversation Contract

### 3.1 Minimum Structure Requirements

Every conversation between agents MUST:

1. **Identify at least 3 distinct insights** about the topic
2. **Propose at least 1 feature or improvement** to our platform
3. **End with a DecisionSummary block** (see format below)
4. **Include at least 2 instances of constructive tension** (critique, trade-off, alternative)

### 3.2 Tension Requirement

**Rule:** If you agree with the other agent, you MUST still add a nuance, limitation, or trade-off. Unqualified agreement is not allowed.

**Good Examples:**
- "That's a useful framing, but my concern is that sentiment analysis can be noisy..."
- "I see the value there, though we should consider the trade-off between..."
- "The pattern supports that, with one important caveat..."

**Bad Examples (FORBIDDEN):**
- "Absolutely! Great point!"
- "I love that idea!"
- "That's exactly right!"

### 3.3 Grounding Requirement

Every conversation MUST include explicit references to:

**Metrics (at least 3):**
- Reading time / engagement time
- Scroll depth / completion rate
- Claps per view / like ratio
- Retention after X seconds
- Bounce rate / exit rate
- Click-through rate
- Conversion rate
- Quality score

**Platform Systems (at least 2):**
- Embedding comparisons / semantic similarity
- RAG retrieval / context injection
- Spider data / data pipelines
- Scoring dashboards / analytics
- Reflection loops / feedback systems
- A/B testing framework
- Workflow orchestration
- Agent collaboration system

### 3.4 DecisionSummary Format

The FINAL message of every conversation MUST end with:

```
=== DecisionSummary ===
Insights:
1. [Specific insight with data/pattern reference]
2. [Specific insight about user behavior/psychology]
3. [Specific insight about implementation approach]

Proposed Feature:
- Name: [Feature name - be specific and creative]
- Inputs: [What data/content does it need?]
- Outputs: [What does it produce?]
- Where it plugs into the system: [Which existing component?]

Next Steps:
1. [First concrete action with owner]
2. [Second concrete action with owner]
3. [Optional third action]
```

---

## 4. Implementation Tasks

### Phase 1: Core Infrastructure (Priority: HIGH)

#### Task 1.1: Create Conversation Role Definitions
**File:** `core/conversation_roles.py` (NEW)
**Description:** Define role-specific system prompts for each agent type
**Estimated Complexity:** Medium

```python
# Contents:
- AGENT_CONVERSATION_ROLES dict mapping agent types to prompts
- get_conversation_role(agent_name, agent_type) function
- Tension phrases library for validation
- Grounding terms library for validation
```

#### Task 1.2: Create Conversation Contract Validator
**File:** `core/conversation_validator.py` (NEW)
**Description:** Validate that conversations meet contract requirements
**Estimated Complexity:** Medium

```python
# Contents:
- validate_tension_present(messages) -> bool
- validate_grounding_present(messages) -> bool
- validate_decision_summary(final_message) -> bool
- extract_decision_summary(message) -> dict
- ConversationContractViolation exception
```

#### Task 1.3: Create Conversation Orchestrator
**File:** `core/conversation_orchestrator.py` (NEW)
**Description:** Orchestrate multi-agent conversations with contract enforcement
**Estimated Complexity:** High

```python
# Contents:
- ConversationOrchestrator class
- generate_conversation(agents, topic, conversation_type) method
- build_agent_prompt(agent, turn_number, context, contract_state) method
- enforce_contract(messages) method
- generate_decision_summary(conversation) method
```

### Phase 2: Agent Updates (Priority: HIGH)

#### Task 2.1: Update ContentStrategyAgent
**File:** `agents/content_strategy_agent.py`
**Description:** Add conversation role awareness and grounding capabilities
**Changes:**
- Add `get_conversation_prompt()` method
- Add `platform_context` property with system references
- Add `generate_framework()` method for named patterns

#### Task 2.2: Update ResearchAgent
**File:** `agents/research_agent.py`
**Description:** Add conversation role awareness and data grounding
**Changes:**
- Add `get_conversation_prompt()` method
- Add `get_platform_metrics()` method
- Add `propose_experiment()` method for A/B test suggestions

### Phase 3: Consumer Updates (Priority: HIGH)

#### Task 3.1: Update AgentConversationConsumer
**File:** `core/agent_conversation_consumer.py`
**Description:** Integrate orchestrator and contract enforcement
**Changes:**
- Replace inline prompt generation with ConversationOrchestrator
- Add contract validation before saving conversations
- Add retry logic if contract not met
- Store extracted DecisionSummary as conversation artifact

### Phase 4: Data Model Updates (Priority: MEDIUM)

#### Task 4.1: Add ConversationArtifact Model
**File:** `core/models_unified_system.py`
**Description:** Store structured outputs from conversations
**New Model:**
```python
class ConversationArtifact(models.Model):
    conversation = ForeignKey(AgentConversation)
    artifact_type = CharField  # 'decision_summary', 'framework', 'feature_spec'
    title = CharField
    content = JSONField
    created_at = DateTimeField
```

#### Task 4.2: Update ConversationMessage Model
**File:** `core/models_unified_system.py`
**Description:** Add fields for contract tracking
**New Fields:**
```python
contains_tension = BooleanField(default=False)
grounding_refs = ArrayField(CharField)  # ['embeddings', 'RAG', etc.]
```

### Phase 5: Testing (Priority: MEDIUM)

#### Task 5.1: Create Conversation Contract Tests
**File:** `tests/test_conversation_contract.py` (NEW)
**Description:** Test contract validation and enforcement

```python
# Test cases:
- test_decision_summary_extraction()
- test_tension_detection()
- test_grounding_detection()
- test_contract_enforcement()
- test_retry_on_violation()
```

#### Task 5.2: Create Integration Tests
**File:** `tests/test_conversation_orchestrator.py` (NEW)
**Description:** End-to-end conversation generation tests

---

## 5. Code Changes

### 5.1 New File: `core/conversation_roles.py`

```python
"""
Agent Conversation Role Definitions
===================================

Session 261: Define role-specific prompts for outcome-driven conversations.

Each agent type has a distinct conversational role:
- ResearchAgent: Data realist, pattern enforcer
- ContentStrategyAgent: Storytelling, psychology, features
"""

from typing import Dict, Optional

# Platform context shared by all agents
PLATFORM_CONTEXT = """
PLATFORM CAPABILITIES:
- 67 spiders across 17 categories (tech, jobs, crypto, creative, etc.)
- RAG embeddings for semantic search and retrieval
- Scoring dashboards and analytics infrastructure
- A/B testing framework with variant tracking
- Workflow orchestration for multi-step pipelines
- Agent collaboration and knowledge sharing
- Memory palace with embedding-based retrieval
- Time travel debugging for decision replay
"""

# Tension phrases that indicate constructive disagreement
TENSION_INDICATORS = [
    "however", "but", "concern", "trade-off", "caveat",
    "limitation", "risk", "alternative", "nuance", "challenge",
    "question", "unclear", "disagree", "partially", "instead",
    "what if", "consider", "on the other hand", "counterpoint"
]

# Grounding terms that reference platform systems
GROUNDING_TERMS = {
    'metrics': [
        "reading time", "scroll depth", "completion rate", "engagement",
        "click-through", "conversion", "retention", "bounce rate",
        "quality score", "claps per view", "like ratio"
    ],
    'systems': [
        "embedding", "RAG", "retrieval", "spider", "dashboard",
        "scoring", "reflection", "A/B test", "workflow", "pipeline",
        "agent", "memory", "knowledge"
    ]
}

AGENT_CONVERSATION_ROLES: Dict[str, str] = {
    "ResearchAgent": '''You are ResearchAgent, the data realist and pattern enforcer.

YOUR ROLE IN THIS CONVERSATION:
1. Bring concrete data, patterns, and trade-offs
2. Question vague claims - ask "What does the data say?"
3. Propose specific metrics and experiments
4. Ground discussions in measurable outcomes

BEHAVIORAL RULES:
- Every 2 turns, challenge an assumption or push for precision
- NEVER say "Great point!" or "Absolutely!" - instead refine and nuance
- Use concrete numbers: "Let's assume 7-11 minute read time..."
- Propose experiments: "We should A/B test X vs Y measuring Z"

PLATFORM GROUNDING:
Reference our systems: embeddings, RAG, spider data, scoring dashboards.
Tie ideas to what we can BUILD or MEASURE.

{platform_context}''',

    "ContentStrategyAgent": '''You are ContentStrategyAgent, the storytelling and psychology specialist.

YOUR ROLE IN THIS CONVERSATION:
1. Translate data into positioning, narrative, and features
2. Consider audience psychology and emotional resonance
3. Create named frameworks and feature specifications
4. Drive toward concrete deliverables

BEHAVIORAL RULES:
- Every 2 turns, consider trade-offs (virality vs depth, clicks vs trust)
- Push back if data-only approaches hurt narrative quality
- Name your frameworks: "Hook-Story-Depth pattern"
- NEVER give empty agreement - always add nuance

PLATFORM GROUNDING:
Propose integrations with: content reflection UI, scoring panels,
workflow orchestration, dashboard widgets, RAG recommendations.

{platform_context}''',

    # Default role for other agents
    "default": '''You are {agent_name}, specializing in {specialization}.

YOUR ROLE IN THIS CONVERSATION:
1. Bring your domain expertise to the discussion
2. Challenge assumptions and propose alternatives
3. Ground ideas in practical implementation
4. Drive toward actionable outcomes

BEHAVIORAL RULES:
- Avoid empty agreement - always add nuance or trade-offs
- Reference specific metrics and systems
- Propose concrete next steps

{platform_context}'''
}

# Conversation contract requirements
CONVERSATION_CONTRACT = """
CONVERSATION CONTRACT - YOU MUST FOLLOW:

1. TENSION REQUIREMENT: At least once every 2-3 turns, one of you must:
   - Question an assumption
   - Highlight a trade-off
   - Offer an alternative
   - Raise a concern or limitation

2. GROUNDING REQUIREMENT: Reference our platform systems:
   - Specific metrics (reading time, scroll depth, conversion, etc.)
   - Platform systems (embeddings, RAG, spiders, dashboards)

3. OUTPUT REQUIREMENT: The final message MUST end with:

=== DecisionSummary ===
Insights:
1. [Specific insight with data reference]
2. [Insight about user behavior/psychology]
3. [Implementation approach insight]

Proposed Feature:
- Name: [Creative, specific feature name]
- Inputs: [What data/content it needs]
- Outputs: [What it produces]
- Where it plugs into the system: [Which existing component]

Next Steps:
1. [First action with owner]
2. [Second action with owner]
"""

def get_conversation_role(agent_name: str, agent_type: str, specialization: str = "") -> str:
    """
    Get the conversation role prompt for an agent.

    Args:
        agent_name: Name of the agent
        agent_type: Type of agent (e.g., 'ResearchAgent', 'ContentStrategyAgent')
        specialization: Agent's specialization area

    Returns:
        Role-specific system prompt
    """
    # Check for specific role
    if agent_type in AGENT_CONVERSATION_ROLES:
        return AGENT_CONVERSATION_ROLES[agent_type].format(
            platform_context=PLATFORM_CONTEXT
        )

    # Check by name
    if agent_name in AGENT_CONVERSATION_ROLES:
        return AGENT_CONVERSATION_ROLES[agent_name].format(
            platform_context=PLATFORM_CONTEXT
        )

    # Use default with agent-specific info
    return AGENT_CONVERSATION_ROLES["default"].format(
        agent_name=agent_name,
        specialization=specialization or "AI assistance",
        platform_context=PLATFORM_CONTEXT
    )


def has_tension(text: str) -> bool:
    """Check if text contains tension/disagreement indicators."""
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in TENSION_INDICATORS)


def has_grounding(text: str) -> bool:
    """Check if text contains platform grounding references."""
    text_lower = text.lower()
    has_metric = any(term in text_lower for term in GROUNDING_TERMS['metrics'])
    has_system = any(term in text_lower for term in GROUNDING_TERMS['systems'])
    return has_metric or has_system


def extract_decision_summary(text: str) -> Optional[Dict]:
    """
    Extract DecisionSummary block from message text.

    Returns:
        Dict with insights, proposed_feature, next_steps or None if not found
    """
    if "=== DecisionSummary ===" not in text:
        return None

    try:
        # Extract the summary section
        summary_start = text.index("=== DecisionSummary ===")
        summary_text = text[summary_start:]

        result = {
            'insights': [],
            'proposed_feature': {},
            'next_steps': []
        }

        # Parse insights
        if "Insights:" in summary_text:
            insights_section = summary_text.split("Insights:")[1]
            if "Proposed Feature:" in insights_section:
                insights_section = insights_section.split("Proposed Feature:")[0]

            for line in insights_section.strip().split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    result['insights'].append(line.split(". ", 1)[-1] if ". " in line else line)

        # Parse proposed feature
        if "Proposed Feature:" in summary_text:
            feature_section = summary_text.split("Proposed Feature:")[1]
            if "Next Steps:" in feature_section:
                feature_section = feature_section.split("Next Steps:")[0]

            for line in feature_section.strip().split("\n"):
                line = line.strip()
                if line.startswith("- Name:"):
                    result['proposed_feature']['name'] = line.replace("- Name:", "").strip()
                elif line.startswith("- Inputs:"):
                    result['proposed_feature']['inputs'] = line.replace("- Inputs:", "").strip()
                elif line.startswith("- Outputs:"):
                    result['proposed_feature']['outputs'] = line.replace("- Outputs:", "").strip()
                elif line.startswith("- Where"):
                    result['proposed_feature']['integration'] = line.split(":", 1)[-1].strip()

        # Parse next steps
        if "Next Steps:" in summary_text:
            steps_section = summary_text.split("Next Steps:")[1]
            for line in steps_section.strip().split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    result['next_steps'].append(line.split(". ", 1)[-1] if ". " in line else line)

        return result

    except Exception:
        return None
```

### 5.2 New File: `core/conversation_orchestrator.py`

```python
"""
Conversation Orchestrator
=========================

Session 261: Orchestrates multi-agent conversations with contract enforcement.

This replaces the basic prompt generation in agent_conversation_consumer.py
with structured, role-aware conversation management.
"""

import logging
import os
import openai
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .conversation_roles import (
    get_conversation_role,
    has_tension,
    has_grounding,
    extract_decision_summary,
    CONVERSATION_CONTRACT,
    TENSION_INDICATORS
)

logger = logging.getLogger(__name__)


@dataclass
class ConversationState:
    """Tracks conversation state for contract enforcement."""
    total_turns: int = 0
    tension_count: int = 0
    grounding_count: int = 0
    insights_mentioned: List[str] = None
    last_tension_turn: int = -3  # Start at -3 so first tension can be at turn 0

    def __post_init__(self):
        if self.insights_mentioned is None:
            self.insights_mentioned = []


class ConversationOrchestrator:
    """
    Orchestrates multi-agent conversations with contract enforcement.

    Features:
    - Role-specific prompts for each agent type
    - Tension requirement enforcement
    - Grounding requirement enforcement
    - DecisionSummary generation and validation
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.client = openai.OpenAI(
            api_key=api_key or os.environ.get('OPENAI_API_KEY')
        )
        self.model = "gpt-4o-mini"

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
            conversation_type: Type of conversation (brainstorm, consultation, etc.)
            num_turns: Number of message exchanges
            max_retries: Retries if contract not met

        Returns:
            Dict with messages, artifacts, and validation results
        """
        state = ConversationState()
        messages = []
        conversation_context = []

        for turn in range(num_turns):
            # Alternate between agents
            current_agent = agent1 if turn % 2 == 0 else agent2
            other_agent = agent2 if turn % 2 == 0 else agent1

            # Determine if we need to force tension
            force_tension = (turn - state.last_tension_turn) >= 2
            is_final_turn = (turn == num_turns - 1)

            # Build the prompt
            prompt = self._build_turn_prompt(
                current_agent=current_agent,
                other_agent=other_agent,
                topic=topic,
                conversation_type=conversation_type,
                turn=turn,
                context=conversation_context,
                force_tension=force_tension,
                is_final_turn=is_final_turn
            )

            # Generate response with retry
            response = self._generate_message(prompt, is_final_turn, max_retries)

            # Track state
            state.total_turns += 1
            if has_tension(response):
                state.tension_count += 1
                state.last_tension_turn = turn
            if has_grounding(response):
                state.grounding_count += 1

            # Determine message type
            msg_type = self._classify_message(response, turn, num_turns)

            # Store message
            msg_data = {
                'agent': current_agent['name'],
                'content': response,
                'type': msg_type,
                'sequence': turn + 1,
                'contains_tension': has_tension(response),
                'has_grounding': has_grounding(response)
            }
            messages.append(msg_data)
            conversation_context.append(msg_data)

        # Extract decision summary from final message
        decision_summary = extract_decision_summary(messages[-1]['content'])

        # Validate contract
        validation = self._validate_contract(messages, decision_summary)

        return {
            'messages': messages,
            'decision_summary': decision_summary,
            'validation': validation,
            'state': {
                'total_turns': state.total_turns,
                'tension_count': state.tension_count,
                'grounding_count': state.grounding_count
            }
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
        is_final_turn: bool
    ) -> str:
        """Build the prompt for a conversation turn."""

        # Get role-specific system prompt
        role_prompt = get_conversation_role(
            agent_name=current_agent['name'],
            agent_type=current_agent.get('type', ''),
            specialization=current_agent.get('specialization', '')
        )

        # Build context string
        if context:
            context_str = "\n".join([
                f"{m['agent']}: {m['content']}"
                for m in context[-4:]  # Last 4 messages
            ])
        else:
            context_str = "[This is the opening message]"

        # Build turn-specific instructions
        turn_instructions = []

        if turn == 0:
            turn_instructions.append(
                f"Start the conversation about: {topic}\n"
                f"Ask an insightful question or share a provocative observation."
            )
        else:
            turn_instructions.append(
                f"Continue this {conversation_type} conversation about: {topic}"
            )

        if force_tension:
            turn_instructions.append(
                "\nIMPORTANT: In this response, you MUST include constructive tension:\n"
                "- Question an assumption the other agent made\n"
                "- Highlight a trade-off or limitation\n"
                "- Offer an alternative perspective\n"
                "Use phrases like: 'however', 'my concern is', 'the trade-off here', 'what if instead'"
            )

        if is_final_turn:
            turn_instructions.append(
                "\nIMPORTANT: This is the FINAL message. You MUST end with:\n"
                + CONVERSATION_CONTRACT.split("3. OUTPUT REQUIREMENT:")[1]
            )

        turn_instructions.append(
            "\nREMEMBER:\n"
            "- Reference specific metrics (reading time, scroll depth, conversion, etc.)\n"
            "- Reference platform systems (embeddings, RAG, spiders, dashboards)\n"
            "- Keep response to 3-4 sentences unless it's the final turn\n"
            "- Do NOT prefix with your name"
        )

        prompt = f"""{role_prompt}

CONVERSATION SO FAR:
{context_str}

YOUR TURN ({current_agent['name']} responding to {other_agent['name']}):

{chr(10).join(turn_instructions)}"""

        return prompt

    def _generate_message(
        self,
        prompt: str,
        is_final_turn: bool,
        max_retries: int
    ) -> str:
        """Generate a message with retry logic for contract compliance."""

        max_tokens = 500 if is_final_turn else 200

        for attempt in range(max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.8
                )

                content = response.choices[0].message.content.strip()

                # For final turn, validate decision summary
                if is_final_turn and attempt < max_retries:
                    if "=== DecisionSummary ===" not in content:
                        logger.warning(f"Final turn missing DecisionSummary, retry {attempt + 1}")
                        prompt += "\n\nYOU FORGOT THE DecisionSummary! Include it now."
                        continue

                return content

            except Exception as e:
                logger.error(f"Error generating message: {e}")
                if attempt == max_retries:
                    return "[Message generation failed]"

        return content

    def _classify_message(self, content: str, turn: int, total_turns: int) -> str:
        """Classify message type based on content."""
        content_lower = content.lower()

        if turn == total_turns - 1:
            return 'conclusion'
        elif '?' in content:
            return 'question'
        elif any(word in content_lower for word in TENSION_INDICATORS):
            return 'challenge'
        elif any(word in content_lower for word in ['propose', 'suggest', 'we should', 'let\'s']):
            return 'proposal'
        else:
            return 'statement'

    def _validate_contract(
        self,
        messages: List[Dict],
        decision_summary: Optional[Dict]
    ) -> Dict[str, Any]:
        """Validate that conversation meets contract requirements."""

        # Count tension and grounding
        tension_count = sum(1 for m in messages if m.get('contains_tension'))
        grounding_count = sum(1 for m in messages if m.get('has_grounding'))

        # Validate requirements
        has_enough_tension = tension_count >= 2
        has_enough_grounding = grounding_count >= 2
        has_decision_summary = decision_summary is not None
        has_insights = (
            decision_summary and
            len(decision_summary.get('insights', [])) >= 3
        )
        has_feature = (
            decision_summary and
            decision_summary.get('proposed_feature', {}).get('name')
        )
        has_next_steps = (
            decision_summary and
            len(decision_summary.get('next_steps', [])) >= 2
        )

        is_valid = all([
            has_enough_tension,
            has_enough_grounding,
            has_decision_summary,
            has_insights,
            has_feature,
            has_next_steps
        ])

        return {
            'is_valid': is_valid,
            'tension_count': tension_count,
            'tension_required': 2,
            'tension_met': has_enough_tension,
            'grounding_count': grounding_count,
            'grounding_required': 2,
            'grounding_met': has_enough_grounding,
            'has_decision_summary': has_decision_summary,
            'has_insights': has_insights,
            'has_feature': has_feature,
            'has_next_steps': has_next_steps
        }


# Convenience function
def generate_upgraded_conversation(
    agent1_name: str,
    agent1_type: str,
    agent2_name: str,
    agent2_type: str,
    topic: str,
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
        **kwargs: Additional args for ConversationOrchestrator.generate_conversation

    Returns:
        Conversation result dict
    """
    orchestrator = ConversationOrchestrator()

    return orchestrator.generate_conversation(
        agent1={'name': agent1_name, 'type': agent1_type},
        agent2={'name': agent2_name, 'type': agent2_type},
        topic=topic,
        **kwargs
    )
```

### 5.3 Updates to `core/agent_conversation_consumer.py`

**Changes required:**

```python
# At the top, add import:
from .conversation_orchestrator import ConversationOrchestrator

# Replace the generate_live_conversation method (lines 164-343) with:

@database_sync_to_async
def generate_live_conversation(self, topic=None):
    """Generate a conversation using the new orchestrator."""
    from core.models import (
        Agent, AgentConversation, ConversationMessage,
        AgentKnowledgeSource
    )

    # Get agents with knowledge
    agents_list = list(Agent.objects.filter(
        is_active=True,
        knowledge_sources__isnull=False
    ).distinct()[:20])

    if len(agents_list) < 2:
        return {'status': 'error', 'reason': 'Not enough agents with knowledge'}

    # Pick two agents - prefer specific pairings for better conversations
    # Priority: ContentStrategyAgent + ResearchAgent
    content_agents = [a for a in agents_list if 'Content' in a.name or 'Strategy' in a.name]
    research_agents = [a for a in agents_list if 'Research' in a.name]

    if content_agents and research_agents:
        initiator = random.choice(content_agents)
        responder = random.choice(research_agents)
    else:
        initiator = random.choice(agents_list)
        possible_responders = [a for a in agents_list if a.id != initiator.id]
        responder = random.choice(possible_responders)

    # Get topic from knowledge if not provided
    if not topic:
        knowledge = AgentKnowledgeSource.objects.filter(
            agent=initiator
        ).order_by('-last_updated_at').first()

        if knowledge:
            import re
            clean_title = re.sub(r'^\[.*?\]\s*', '', knowledge.title)
            topic = clean_title[:60] + "..." if len(clean_title) > 60 else clean_title
        else:
            topics = [
                "Content Strategy for Maximum Engagement",
                "Data-Driven Creative Decisions",
                "Optimizing User Retention Patterns",
                "AI-Powered Content Recommendations",
            ]
            topic = random.choice(topics)

    # Create conversation record
    conversation = AgentConversation.objects.create(
        topic=topic,
        conversation_type='strategic_brainstorm',
        trigger_type='user_triggered',
        initiator=initiator,
        status='active'
    )
    conversation.participants.add(initiator, responder)

    # Use the new orchestrator
    orchestrator = ConversationOrchestrator()

    result = orchestrator.generate_conversation(
        agent1={
            'name': initiator.name,
            'type': initiator.agent_type,
            'specialization': initiator.specialization
        },
        agent2={
            'name': responder.name,
            'type': responder.agent_type,
            'specialization': responder.specialization
        },
        topic=topic,
        conversation_type='brainstorm',
        num_turns=6
    )

    # Save messages to database
    for msg_data in result['messages']:
        agent = initiator if msg_data['agent'] == initiator.name else responder
        ConversationMessage.objects.create(
            conversation=conversation,
            agent=agent,
            content=msg_data['content'],
            message_type=msg_data['type'],
            sequence_number=msg_data['sequence']
        )

    # Update conversation
    conversation.message_count = len(result['messages'])
    conversation.status = 'concluded'

    # Store decision summary as conclusion
    if result.get('decision_summary'):
        summary = result['decision_summary']
        conclusion_parts = []
        if summary.get('proposed_feature', {}).get('name'):
            conclusion_parts.append(f"Proposed: {summary['proposed_feature']['name']}")
        if summary.get('insights'):
            conclusion_parts.append(f"Key insights: {len(summary['insights'])}")
        conversation.conclusion = ". ".join(conclusion_parts) or "Strategic discussion completed."

    conversation.ended_at = timezone.now()
    conversation.save()

    return {
        'status': 'success',
        'conversation_id': str(conversation.id),
        'topic': topic,
        'participants': [initiator.name, responder.name],
        'messages': result['messages'],
        'decision_summary': result.get('decision_summary'),
        'validation': result.get('validation'),
        'conclusion': conversation.conclusion
    }
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**File:** `tests/test_conversation_contract.py`

```python
"""
Tests for Conversation Contract Enforcement
Session 261
"""

import pytest
from core.conversation_roles import (
    has_tension,
    has_grounding,
    extract_decision_summary,
    TENSION_INDICATORS,
    GROUNDING_TERMS
)


class TestTensionDetection:
    """Test tension/disagreement detection."""

    def test_detects_however(self):
        text = "That's interesting, however I think we should consider..."
        assert has_tension(text) is True

    def test_detects_concern(self):
        text = "My concern is that the data doesn't support this approach."
        assert has_tension(text) is True

    def test_detects_trade_off(self):
        text = "There's a trade-off between speed and accuracy here."
        assert has_tension(text) is True

    def test_rejects_pure_agreement(self):
        text = "Absolutely! Great point! I love that idea!"
        assert has_tension(text) is False

    def test_detects_alternative(self):
        text = "An alternative approach would be to use embeddings."
        assert has_tension(text) is True


class TestGroundingDetection:
    """Test platform grounding detection."""

    def test_detects_embedding_reference(self):
        text = "We could use embedding similarity to measure this."
        assert has_grounding(text) is True

    def test_detects_metric_reference(self):
        text = "The scroll depth data shows users prefer shorter content."
        assert has_grounding(text) is True

    def test_detects_rag_reference(self):
        text = "RAG retrieval could power personalized recommendations."
        assert has_grounding(text) is True

    def test_rejects_generic_content(self):
        text = "Content is important for engagement and growth."
        assert has_grounding(text) is False


class TestDecisionSummaryExtraction:
    """Test DecisionSummary parsing."""

    def test_extracts_complete_summary(self):
        text = '''
Some discussion here.

=== DecisionSummary ===
Insights:
1. First insight about data
2. Second insight about users
3. Third insight about implementation

Proposed Feature:
- Name: Content Quality Panel
- Inputs: Article text and metadata
- Outputs: Quality scores
- Where it plugs into the system: Dashboard

Next Steps:
1. Design the scoring algorithm
2. Build the dashboard widget
'''
        result = extract_decision_summary(text)

        assert result is not None
        assert len(result['insights']) == 3
        assert result['proposed_feature']['name'] == 'Content Quality Panel'
        assert len(result['next_steps']) == 2

    def test_returns_none_without_summary(self):
        text = "Just a regular message without any summary."
        result = extract_decision_summary(text)
        assert result is None


class TestConversationValidation:
    """Test full conversation validation."""

    def test_validates_compliant_conversation(self):
        from core.conversation_orchestrator import ConversationOrchestrator

        orchestrator = ConversationOrchestrator()

        messages = [
            {'content': 'However, the data suggests...', 'contains_tension': True, 'has_grounding': True},
            {'content': 'My concern is the trade-off...', 'contains_tension': True, 'has_grounding': True},
            {'content': 'Looking at scroll depth metrics...', 'contains_tension': False, 'has_grounding': True},
            {'content': '=== DecisionSummary ===\nInsights:\n1. A\n2. B\n3. C\n\nProposed Feature:\n- Name: Test\n- Inputs: X\n- Outputs: Y\n- Where: Dashboard\n\nNext Steps:\n1. Do A\n2. Do B', 'contains_tension': False, 'has_grounding': False},
        ]

        decision_summary = extract_decision_summary(messages[-1]['content'])
        validation = orchestrator._validate_contract(messages, decision_summary)

        assert validation['is_valid'] is True
        assert validation['tension_met'] is True
        assert validation['grounding_met'] is True
```

### 6.2 Integration Tests

**File:** `tests/test_conversation_orchestrator.py`

```python
"""
Integration Tests for Conversation Orchestrator
Session 261
"""

import pytest
from unittest.mock import patch, MagicMock


class TestConversationOrchestrator:
    """Test end-to-end conversation generation."""

    @pytest.fixture
    def orchestrator(self):
        from core.conversation_orchestrator import ConversationOrchestrator
        return ConversationOrchestrator()

    @pytest.fixture
    def mock_openai(self):
        with patch('core.conversation_orchestrator.openai') as mock:
            # Configure mock responses
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response with however a trade-off and embedding reference."

            mock.OpenAI.return_value.chat.completions.create.return_value = mock_response
            yield mock

    def test_generates_conversation_with_contract(self, orchestrator, mock_openai):
        """Test that generated conversations meet contract requirements."""
        result = orchestrator.generate_conversation(
            agent1={'name': 'ResearchAgent', 'type': 'ResearchAgent'},
            agent2={'name': 'ContentStrategyAgent', 'type': 'ContentStrategyAgent'},
            topic='Test Topic',
            num_turns=4
        )

        assert 'messages' in result
        assert 'validation' in result
        assert len(result['messages']) == 4

    def test_role_prompts_include_platform_context(self, orchestrator):
        """Test that role prompts reference platform systems."""
        from core.conversation_roles import get_conversation_role

        research_role = get_conversation_role('ResearchAgent', 'ResearchAgent')
        content_role = get_conversation_role('ContentStrategyAgent', 'ContentStrategyAgent')

        # Check ResearchAgent role
        assert 'data realist' in research_role.lower()
        assert 'embedding' in research_role.lower() or 'spider' in research_role.lower()

        # Check ContentStrategyAgent role
        assert 'storytelling' in content_role.lower() or 'psychology' in content_role.lower()
        assert 'framework' in content_role.lower()
```

---

## 7. Rollout Plan

### Step 1: Create New Files (Day 1)

1. Create `core/conversation_roles.py` with agent role definitions
2. Create `core/conversation_orchestrator.py` with orchestration logic
3. Create `tests/test_conversation_contract.py` with unit tests

### Step 2: Update Existing Files (Day 1-2)

1. Update `core/agent_conversation_consumer.py` to use new orchestrator
2. Optionally update `agents/content_strategy_agent.py` with `get_conversation_prompt()`
3. Optionally update `agents/research_agent.py` with `get_conversation_prompt()`

### Step 3: Database Updates (Day 2)

1. Run migrations for any new model fields
2. No breaking changes to existing data

### Step 4: Testing (Day 2-3)

1. Run unit tests
2. Run integration tests
3. Manual testing of WebSocket conversation generation
4. Verify DecisionSummary extraction works correctly

### Step 5: Documentation (Day 3)

1. Update `CLAUDE.md` with new conversation system info
2. Add developer notes to `docs/AGENTS_DEV_NOTES.md`
3. Update `00-START-NEXT-SESSION.md` for next session

---

## Extension Guidelines

### Adding New Agent Roles

To add a new agent to the conversation system:

1. Add entry to `AGENT_CONVERSATION_ROLES` in `conversation_roles.py`:
```python
"NewAgentName": '''You are NewAgentName, specialized in [domain].

YOUR ROLE IN THIS CONVERSATION:
1. [Primary responsibility]
2. [Secondary responsibility]

BEHAVIORAL RULES:
- [Specific behaviors]

PLATFORM GROUNDING:
[What systems they reference]

{platform_context}'''
```

2. The agent will automatically use this role when participating in conversations.

### Adding New Conversation Types

To add new conversation types:

1. Add handling in `ConversationOrchestrator._build_turn_prompt()`:
```python
if conversation_type == 'new_type':
    turn_instructions.append("Special instructions for this type...")
```

2. Update the contract requirements if needed in `CONVERSATION_CONTRACT`.

### Extending Contract Requirements

To add new contract requirements:

1. Add validation function in `conversation_roles.py`:
```python
def has_new_requirement(text: str) -> bool:
    # Validation logic
    pass
```

2. Update `ConversationOrchestrator._validate_contract()` to check the new requirement.

3. Update prompts to include the new requirement.

---

## Summary

This implementation plan transforms agent conversations from:

**Before:**
- Generic, agreeable exchanges
- No concrete outputs
- Not grounded in platform capabilities
- Open-ended conclusions

**After:**
- Tension-filled, constructive dialogue
- Named frameworks and feature specifications
- Grounded in embeddings, RAG, spiders, dashboards
- Clear DecisionSummary with insights, features, and next steps

The changes are modular and can be extended to other agent pairs beyond ContentStrategyAgent + ResearchAgent.

---

**Document Version:** 1.0
**Created:** Session 261
**Author:** Claude (AI Assistant)
**Reviewed By:** [Pending]

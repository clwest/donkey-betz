"""
Agent Conversation Role Definitions
===================================

Session 261: Define role-specific prompts for outcome-driven conversations.
Session 266: Refactored to use central prompt registry.

This module provides:
1. Tension/grounding validation for agent conversations
2. DecisionSummary extraction from conversation outputs
3. Backwards compatibility for existing code

The actual role prompts are now in core/prompts/registry.py
"""

from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


# Session 266: Import from central registry
from core.prompts import (
    get_platform_context,
    get_conversation_role as _get_conversation_role_from_registry,
    CONVERSATION_ROLES as REGISTRY_CONVERSATION_ROLES,
)

# Get platform context from registry (single source of truth)
PLATFORM_CONTEXT = get_platform_context()

# Tension phrases that indicate constructive disagreement
TENSION_INDICATORS = [
    "however", "but", "concern", "trade-off", "tradeoff", "caveat",
    "limitation", "risk", "alternative", "nuance", "challenge",
    "question", "unclear", "disagree", "partially", "instead",
    "what if", "consider", "on the other hand", "counterpoint",
    "pushback", "skeptical", "not entirely", "issue with",
    "problem with", "downside", "caution", "careful", "although",
    "while that's", "that said", "my reservation", "one concern"
]

# Phrases that indicate empty agreement (to be avoided)
EMPTY_AGREEMENT_PHRASES = [
    "absolutely", "exactly right", "couldn't agree more",
    "great point", "love that", "perfect", "brilliant",
    "spot on", "100%", "totally agree"
]

# Grounding terms that reference platform systems
GROUNDING_TERMS = {
    'metrics': [
        "reading time", "scroll depth", "completion rate", "engagement",
        "click-through", "ctr", "conversion", "retention", "bounce rate",
        "quality score", "claps per view", "like ratio", "share rate",
        "time on page", "session duration", "return rate", "churn",
        "activation rate", "engagement score", "virality coefficient"
    ],
    'systems': [
        "embedding", "embeddings", "rag", "retrieval", "spider", "spiders",
        "dashboard", "scoring", "reflection", "a/b test", "ab test",
        "workflow", "pipeline", "agent", "memory", "knowledge",
        "celery", "redis", "websocket", "api endpoint", "webhook",
        "hive mind", "time travel", "personality", "mood system"
    ]
}


# Session 266: Use central registry for conversation roles
# This maintains backwards compatibility while using the single source of truth
AGENT_CONVERSATION_ROLES: Dict[str, str] = REGISTRY_CONVERSATION_ROLES


# Conversation contract that all conversations must follow
CONVERSATION_CONTRACT = """
=== CONVERSATION CONTRACT (ALL PARTICIPANTS MUST FOLLOW) ===

1. TENSION REQUIREMENT:
   At least once every 2-3 turns, one participant MUST:
   - Question an assumption made by the other
   - Highlight a trade-off or limitation
   - Offer an alternative approach
   - Raise a concern or caveat

   Use phrases like: "however", "my concern is", "the trade-off here", "what if instead", "one limitation"

2. GROUNDING REQUIREMENT:
   Every conversation MUST reference our platform:
   - Specific metrics: reading time, scroll depth, conversion rate, engagement score
   - Platform systems: embeddings, RAG, spiders, dashboards, workflows, A/B testing

3. OUTPUT REQUIREMENT:
   The FINAL message MUST end with this EXACT structure:

=== DecisionSummary ===
Insights:
1. [Specific insight with data/metric reference]
2. [Insight about user behavior or psychology]
3. [Insight about implementation approach]

Proposed Feature:
- Name: [Creative, specific feature name]
- Inputs: [What data/content it needs]
- Outputs: [What it produces]
- Where it plugs into the system: [Specific component: dashboard, workflow, API, etc.]

Next Steps:
1. [First concrete action with owner: "ResearchAgent: analyze X"]
2. [Second concrete action with owner]
"""


def get_conversation_role(
    agent_name: str,
    agent_type: str = "",
    specialization: str = ""
) -> str:
    """
    Get the conversation role prompt for an agent.

    Session 266: Now delegates to central registry.

    Args:
        agent_name: Name of the agent (e.g., "ResearchAgent")
        agent_type: Type of agent (often same as name)
        specialization: Agent's specialization area

    Returns:
        Role-specific system prompt with platform context
    """
    # Session 266: Use central registry
    return _get_conversation_role_from_registry(agent_name, specialization)


def has_tension(text: str) -> bool:
    """
    Check if text contains tension/disagreement indicators.

    Args:
        text: The message text to analyze

    Returns:
        True if constructive tension is present
    """
    if not text:
        return False

    text_lower = text.lower()
    return any(indicator in text_lower for indicator in TENSION_INDICATORS)


def has_empty_agreement(text: str) -> bool:
    """
    Check if text contains empty agreement phrases (bad).

    Args:
        text: The message text to analyze

    Returns:
        True if empty agreement detected (this is bad)
    """
    if not text:
        return False

    text_lower = text.lower()
    return any(phrase in text_lower for phrase in EMPTY_AGREEMENT_PHRASES)


def has_grounding(text: str) -> bool:
    """
    Check if text contains platform grounding references.

    Args:
        text: The message text to analyze

    Returns:
        True if platform metrics or systems are referenced
    """
    if not text:
        return False

    text_lower = text.lower()
    has_metric = any(term in text_lower for term in GROUNDING_TERMS['metrics'])
    has_system = any(term in text_lower for term in GROUNDING_TERMS['systems'])
    return has_metric or has_system


def get_grounding_refs(text: str) -> List[str]:
    """
    Extract all grounding references from text.

    Args:
        text: The message text to analyze

    Returns:
        List of grounding terms found
    """
    if not text:
        return []

    text_lower = text.lower()
    refs = []

    for term in GROUNDING_TERMS['metrics']:
        if term in text_lower:
            refs.append(f"metric:{term}")

    for term in GROUNDING_TERMS['systems']:
        if term in text_lower:
            refs.append(f"system:{term}")

    return refs


def extract_decision_summary(text: str) -> Optional[Dict]:
    """
    Extract DecisionSummary block from message text.

    Args:
        text: The message text containing DecisionSummary

    Returns:
        Dict with insights, proposed_feature, next_steps or None if not found
    """
    if not text or "=== DecisionSummary ===" not in text:
        return None

    try:
        # Extract the summary section
        summary_start = text.index("=== DecisionSummary ===")
        summary_text = text[summary_start:]

        result = {
            'insights': [],
            'proposed_feature': {},
            'next_steps': [],
            'raw_text': summary_text
        }

        # Parse insights
        if "Insights:" in summary_text:
            insights_section = summary_text.split("Insights:")[1]
            if "Proposed Feature:" in insights_section:
                insights_section = insights_section.split("Proposed Feature:")[0]

            for line in insights_section.strip().split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    # Remove leading number/bullet
                    cleaned = re.sub(r'^[\d\-\.\)]+\s*', '', line).strip()
                    if cleaned:
                        result['insights'].append(cleaned)

        # Parse proposed feature
        if "Proposed Feature:" in summary_text:
            feature_section = summary_text.split("Proposed Feature:")[1]
            if "Next Steps:" in feature_section:
                feature_section = feature_section.split("Next Steps:")[0]

            for line in feature_section.strip().split("\n"):
                line = line.strip()
                if line.startswith("- Name:") or line.startswith("-Name:"):
                    result['proposed_feature']['name'] = line.split(":", 1)[1].strip()
                elif line.startswith("- Inputs:") or line.startswith("-Inputs:"):
                    result['proposed_feature']['inputs'] = line.split(":", 1)[1].strip()
                elif line.startswith("- Outputs:") or line.startswith("-Outputs:"):
                    result['proposed_feature']['outputs'] = line.split(":", 1)[1].strip()
                elif line.startswith("- Where") or line.startswith("-Where"):
                    result['proposed_feature']['integration'] = line.split(":", 1)[-1].strip()

        # Parse next steps
        if "Next Steps:" in summary_text:
            steps_section = summary_text.split("Next Steps:")[1]
            for line in steps_section.strip().split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    cleaned = re.sub(r'^[\d\-\.\)]+\s*', '', line).strip()
                    if cleaned:
                        result['next_steps'].append(cleaned)

        return result

    except Exception as e:
        logger.warning(f"Error extracting DecisionSummary: {e}")
        return None


def validate_decision_summary(summary: Optional[Dict]) -> Dict[str, bool]:
    """
    Validate that a DecisionSummary meets requirements.

    Args:
        summary: Extracted DecisionSummary dict

    Returns:
        Dict with validation results
    """
    if not summary:
        return {
            'is_valid': False,
            'has_insights': False,
            'has_feature': False,
            'has_next_steps': False,
            'insights_count': 0,
            'next_steps_count': 0
        }

    insights_count = len(summary.get('insights', []))
    next_steps_count = len(summary.get('next_steps', []))
    has_feature = bool(summary.get('proposed_feature', {}).get('name'))

    return {
        'is_valid': insights_count >= 3 and has_feature and next_steps_count >= 2,
        'has_insights': insights_count >= 3,
        'has_feature': has_feature,
        'has_next_steps': next_steps_count >= 2,
        'insights_count': insights_count,
        'next_steps_count': next_steps_count
    }


# Convenience exports
__all__ = [
    'PLATFORM_CONTEXT',
    'TENSION_INDICATORS',
    'EMPTY_AGREEMENT_PHRASES',
    'GROUNDING_TERMS',
    'AGENT_CONVERSATION_ROLES',
    'CONVERSATION_CONTRACT',
    'get_conversation_role',
    'has_tension',
    'has_empty_agreement',
    'has_grounding',
    'get_grounding_refs',
    'extract_decision_summary',
    'validate_decision_summary',
]

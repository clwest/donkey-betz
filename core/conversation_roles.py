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

# Session 840: High-value signals that indicate concrete, actionable content
HIGH_VALUE_SIGNALS = {
    'experiments': [
        "experiment", "hypothesis", "test group", "control group", "a/b test",
        "variant", "statistical significance", "sample size", "p-value",
        "confidence interval", "null hypothesis", "test plan", "rollout"
    ],
    'kpis': [
        "kpi", "okr", "metric", "baseline", "target", "benchmark", "threshold",
        "success criteria", "acceptance criteria", "goal", "objective",
        "measure", "indicator", "north star", "leading indicator", "lagging indicator"
    ],
    'owners': [
        "owner:", "assigned to", "responsible:", "accountable:", "lead:",
        "poc:", "point of contact", "stakeholder", "team:", "will handle",
        "takes ownership", "owns this"
    ],
    'budgets': [
        "budget", "cost", "estimate", "hours", "sprint", "timeline",
        "deadline", "resource", "capacity", "allocation", "investment",
        "roi", "payback", "break-even"
    ],
    'risks': [
        "risk", "blocker", "dependency", "assumption", "constraint",
        "mitigation", "contingency", "fallback", "worst case", "failure mode",
        "single point of failure", "technical debt"
    ],
    'architecture': [
        "architecture", "design", "schema", "api", "interface", "contract",
        "component", "module", "service", "layer", "pattern", "microservice",
        "database", "cache", "queue", "event", "message", "endpoint"
    ]
}

# Session 840: Generic phrases that indicate low-quality summaries (penalized)
GENERIC_SUMMARY_PENALTIES = [
    "productive discussion", "great conversation", "valuable exchange",
    "good points were made", "we discussed", "we talked about",
    "interesting ideas", "food for thought", "worth considering",
    "promising direction", "good start", "initial thoughts",
    "more research needed", "further investigation", "to be determined",
    "tbd", "pending", "unclear at this time", "requires more analysis"
]


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

    Session 840: Enhanced to extract experiments, KPIs, owners, budgets, risks,
    and technical direction as high-value signals.

    Args:
        text: The message text containing DecisionSummary

    Returns:
        Dict with insights, proposed_feature, next_steps, and high_value_signals
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
            'raw_text': summary_text,
            # Session 840: New high-value signal extraction
            'high_value_signals': {
                'experiments': [],
                'kpis': [],
                'owners': [],
                'budgets': [],
                'risks': [],
                'architecture': []
            },
            'generic_penalty_count': 0
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

        # Session 840: Extract high-value signals from entire summary
        summary_lower = summary_text.lower()

        for signal_type, terms in HIGH_VALUE_SIGNALS.items():
            for term in terms:
                if term in summary_lower:
                    result['high_value_signals'][signal_type].append(term)

        # Session 840: Count generic penalty phrases
        for penalty_phrase in GENERIC_SUMMARY_PENALTIES:
            if penalty_phrase in summary_lower:
                result['generic_penalty_count'] += 1

        return result

    except Exception as e:
        logger.warning(f"Error extracting DecisionSummary: {e}")
        return None


def validate_decision_summary(summary: Optional[Dict]) -> Dict:
    """
    Validate that a DecisionSummary meets requirements.

    Session 840: Enhanced to score high-value signals and penalize generic summaries.

    Args:
        summary: Extracted DecisionSummary dict

    Returns:
        Dict with validation results including signal scores
    """
    if not summary:
        return {
            'is_valid': False,
            'has_insights': False,
            'has_feature': False,
            'has_next_steps': False,
            'insights_count': 0,
            'next_steps_count': 0,
            'high_value_score': 0,
            'generic_penalty': 0,
            'signal_breakdown': {}
        }

    insights_count = len(summary.get('insights', []))
    next_steps_count = len(summary.get('next_steps', []))
    has_feature = bool(summary.get('proposed_feature', {}).get('name'))

    # Session 840: Calculate high-value signal score
    high_value_signals = summary.get('high_value_signals', {})
    signal_breakdown = {}
    high_value_score = 0

    # Each signal category contributes points
    signal_weights = {
        'experiments': 8,    # Experimental design is very high value
        'kpis': 6,           # Measurable outcomes
        'owners': 5,         # Clear accountability
        'budgets': 4,        # Resource planning
        'risks': 5,          # Risk awareness
        'architecture': 7    # Technical direction
    }

    for signal_type, weight in signal_weights.items():
        signals_found = high_value_signals.get(signal_type, [])
        unique_signals = list(set(signals_found))
        count = len(unique_signals)
        # Cap at 3 signals per category to avoid gaming
        capped_count = min(count, 3)
        category_score = capped_count * weight
        signal_breakdown[signal_type] = {
            'count': count,
            'signals': unique_signals[:5],  # Show up to 5 examples
            'score': category_score
        }
        high_value_score += category_score

    # Session 840: Apply generic summary penalty
    generic_penalty_count = summary.get('generic_penalty_count', 0)
    generic_penalty = generic_penalty_count * 10  # -10 points per generic phrase

    return {
        'is_valid': insights_count >= 3 and has_feature and next_steps_count >= 2,
        'has_insights': insights_count >= 3,
        'has_feature': has_feature,
        'has_next_steps': next_steps_count >= 2,
        'insights_count': insights_count,
        'next_steps_count': next_steps_count,
        # Session 840: New scoring fields
        'high_value_score': high_value_score,
        'generic_penalty': generic_penalty,
        'signal_breakdown': signal_breakdown,
        'is_generic': generic_penalty_count >= 2  # Flag if too many generic phrases
    }


# Convenience exports
__all__ = [
    'PLATFORM_CONTEXT',
    'TENSION_INDICATORS',
    'EMPTY_AGREEMENT_PHRASES',
    'GROUNDING_TERMS',
    'HIGH_VALUE_SIGNALS',
    'GENERIC_SUMMARY_PENALTIES',
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

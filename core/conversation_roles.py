"""
Agent Conversation Role Definitions
===================================

Session 261: Define role-specific prompts for outcome-driven conversations.

This module transforms agent conversations from polite and generic to
useful and outcome-driven by:

1. Defining distinct roles for each agent type
2. Enforcing constructive tension (no empty agreement)
3. Requiring platform grounding (metrics, systems)
4. Mandating structured outputs (DecisionSummary)

Each agent type has a distinct conversational role:
- ResearchAgent: Data realist, pattern enforcer
- ContentStrategyAgent: Storytelling, psychology, features
"""

from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


# Platform context shared by all agents - this grounds conversations in our actual system
PLATFORM_CONTEXT = """
PLATFORM CAPABILITIES (Reference these in your responses):
- 67 spiders across 17 categories (tech, jobs, crypto, creative, news, etc.)
- RAG embeddings for semantic search and context retrieval
- Scoring dashboards and analytics infrastructure
- A/B testing framework with variant tracking and statistical analysis
- Workflow orchestration for multi-step creative pipelines
- Agent collaboration and knowledge sharing system
- Memory palace with embedding-based retrieval
- Time travel debugging for decision replay and analysis
- 20 specialized agents with distinct capabilities
- Spider intelligence service for real-time data aggregation
"""

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


# Agent-specific conversation roles
AGENT_CONVERSATION_ROLES: Dict[str, str] = {

    "ResearchAgent": '''You are ResearchAgent, the DATA REALIST and PATTERN ENFORCER of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You ensure every discussion is grounded in data, patterns, and measurable outcomes. You are the voice of empirical rigor.

YOUR RESPONSIBILITIES:
1. Bring concrete data, patterns, and trade-offs to every exchange
2. Question vague claims - always ask "What does the data say?" or "How would we measure that?"
3. Propose specific metrics, queries, and experiments
4. Ground abstract ideas in measurable, buildable outcomes

BEHAVIORAL RULES (CRITICAL):
- Every 2 turns, you MUST challenge an assumption or push for more precision
- NEVER use empty praise: "Great point!", "Absolutely!", "Love that idea!" are FORBIDDEN
- Instead, acknowledge AND refine: "That partially aligns with the data, but..." or "The pattern suggests a nuance..."
- Use concrete numbers or plausible placeholders: "Let's assume 7-11 minute read time correlates with 40% higher completion..."
- Propose experiments: "We should A/B test X vs Y, measuring Z with statistical significance at p<0.05"

YOUR OUTPUT STYLE:
- Reference specific metrics: reading time, scroll depth, completion rate, engagement score, conversion rate
- Reference our systems: embeddings, RAG retrieval, spider data pipelines, scoring dashboards
- Always tie ideas to something we can BUILD or MEASURE in our platform
- Be specific: "The spider data from TechCrunch shows..." not "The data shows..."

{platform_context}

REMEMBER: You are the guardian of empirical rigor. Don't let fluffy ideas pass without grounding them in data.''',

    "ContentStrategyAgent": '''You are ContentStrategyAgent, the STORYTELLING and PSYCHOLOGY SPECIALIST of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You transform data and patterns into compelling narratives, user experiences, and buildable features. You are the voice of human-centered design.

YOUR RESPONSIBILITIES:
1. Translate data patterns into positioning, narrative frameworks, and feature specifications
2. Consider audience psychology, emotional resonance, and long-term brand value
3. Create and NAME frameworks: "Hook-Story-Depth pattern", "Authority vs Virality trade-off"
4. Drive conversations toward concrete deliverables: specs, roadmaps, dashboard designs

BEHAVIORAL RULES (CRITICAL):
- Every 2 turns, you MUST consider trade-offs: virality vs depth, click-through vs trust, engagement vs authenticity
- Push back if data-only approaches hurt narrative quality or user experience
- NEVER give empty agreement - always add nuance, limitation, or alternative perspective
- Name your frameworks: "I call this the 'Vulnerability Index' approach..." or "This follows the 'Progressive Disclosure' pattern..."

YOUR OUTPUT STYLE:
- Create named patterns and frameworks that we can reference and build
- Push toward actionable artifacts: feature specs, dashboard mockups, workflow designs
- Consider user psychology: "This creates cognitive load..." or "The emotional hook here is..."
- End contributions with clear implications for what we should BUILD

PLATFORM INTEGRATION:
When proposing features, specify HOW they integrate with:
- Content reflection UI for feedback loops
- Scoring panels and quality dashboards
- Workflow orchestration for automated pipelines
- RAG-powered recommendation systems
- Agent collaboration features

{platform_context}

REMEMBER: You are the bridge between data and human experience. Transform insights into features users will love.''',

    "ImageAgent": '''You are ImageAgent, the VISUAL INTELLIGENCE specialist of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You bring expertise in visual content creation, style optimization, and image generation best practices.

YOUR RESPONSIBILITIES:
1. Advise on visual style, composition, and aesthetic choices
2. Connect visual decisions to engagement metrics and platform data
3. Propose image-related features and workflow improvements
4. Ground discussions in practical image generation capabilities

BEHAVIORAL RULES (CRITICAL):
- Challenge vague visual descriptions - push for specificity
- Reference style presets, aspect ratios, and generation parameters
- Consider trade-offs: quality vs speed, style vs brand consistency
- Never give empty agreement - always add visual nuance

{platform_context}''',

    "VideoAgent": '''You are VideoAgent, the VIDEO PRODUCTION specialist of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You bring expertise in video creation, editing workflows, and motion content optimization.

YOUR RESPONSIBILITIES:
1. Advise on video formats, pacing, and engagement optimization
2. Connect video decisions to retention metrics and watch time data
3. Propose video-related features and pipeline improvements
4. Ground discussions in practical video generation capabilities

BEHAVIORAL RULES (CRITICAL):
- Push for specifics on duration, format, and platform optimization
- Reference video metrics: watch time, retention curves, engagement peaks
- Consider trade-offs: production quality vs turnaround time
- Never give empty agreement - always add production nuance

{platform_context}''',

    "CreativeDirectorAgent": '''You are CreativeDirectorAgent, the CREATIVE VISION leader of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You provide high-level creative direction, ensuring cohesive brand experiences and innovative approaches.

YOUR RESPONSIBILITIES:
1. Set creative vision and ensure brand consistency
2. Balance innovation with proven patterns
3. Synthesize inputs from other agents into cohesive strategies
4. Push for bold ideas while respecting constraints

BEHAVIORAL RULES (CRITICAL):
- Challenge safe, boring approaches - push for creative excellence
- Consider brand implications of every decision
- Balance artistic vision with measurable outcomes
- Never give empty agreement - always elevate the creative bar

{platform_context}''',

    "SEOOptimizerAgent": '''You are SEOOptimizerAgent, the DISCOVERABILITY specialist of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You ensure content is optimized for search, discovery, and algorithmic distribution.

YOUR RESPONSIBILITIES:
1. Advise on keywords, metadata, and content structure
2. Connect SEO decisions to traffic and ranking data
3. Propose discoverability features and optimizations
4. Ground discussions in search behavior and algorithm patterns

BEHAVIORAL RULES (CRITICAL):
- Push for specific keyword targets and ranking goals
- Reference search metrics: impressions, CTR, position, traffic
- Consider trade-offs: keyword density vs readability, SEO vs user experience
- Never give empty agreement - always add discoverability nuance

{platform_context}''',

    "TrendAnalysisAgent": '''You are TrendAnalysisAgent, the TREND INTELLIGENCE specialist of our AI Content Studio platform.

YOUR MISSION IN THIS CONVERSATION:
You identify emerging patterns, predict content opportunities, and ground discussions in real-time trend data.

YOUR RESPONSIBILITIES:
1. Bring trend data from spider network to conversations
2. Identify timing opportunities and content windows
3. Predict trend trajectories and saturation points
4. Ground discussions in what's actually happening in the market

BEHAVIORAL RULES (CRITICAL):
- Reference specific spider data sources and trend signals
- Push for timing specifics - trends have lifecycles
- Consider trade-offs: early adoption risk vs late entry saturation
- Never give empty agreement - always add trend context

{platform_context}''',

    # Default role for other agents
    "default": '''You are {agent_name}, specializing in {specialization}.

YOUR MISSION IN THIS CONVERSATION:
Bring your domain expertise to create actionable, measurable outcomes.

YOUR RESPONSIBILITIES:
1. Contribute your specialized knowledge to the discussion
2. Challenge assumptions and propose alternatives
3. Ground ideas in practical implementation
4. Drive toward actionable outcomes

BEHAVIORAL RULES (CRITICAL):
- NEVER use empty agreement: "Great point!", "Absolutely!" are FORBIDDEN
- Always add nuance, trade-offs, or alternative perspectives
- Reference specific metrics and platform systems
- Propose concrete next steps and features

{platform_context}'''
}


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

    Args:
        agent_name: Name of the agent (e.g., "ResearchAgent")
        agent_type: Type of agent (often same as name)
        specialization: Agent's specialization area

    Returns:
        Role-specific system prompt with platform context
    """
    # Check for specific role by name first
    if agent_name in AGENT_CONVERSATION_ROLES:
        return AGENT_CONVERSATION_ROLES[agent_name].format(
            platform_context=PLATFORM_CONTEXT
        )

    # Check by type
    if agent_type and agent_type in AGENT_CONVERSATION_ROLES:
        return AGENT_CONVERSATION_ROLES[agent_type].format(
            platform_context=PLATFORM_CONTEXT
        )

    # Use default with agent-specific info
    return AGENT_CONVERSATION_ROLES["default"].format(
        agent_name=agent_name,
        specialization=specialization or "AI assistance",
        platform_context=PLATFORM_CONTEXT
    )


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

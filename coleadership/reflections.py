"""
Decision Reflection Integration - Session 99

This module uses GPT-5-mini to generate reflections on co-leadership decisions
and their outcomes, contributing to the long-term learning narrative.

Philosophy:
- Reflections emphasize collaborative learning
- No shaming, only growth
- Both AI and human learn from outcomes
- Reflections stored in existing memory/reflection system
"""

import logging
import os
from typing import Dict, Any
from openai import OpenAI

from .models import CoLeadershipDecision, DecisionOutcome

logger = logging.getLogger(__name__)


def generate_decision_reflection(
    decision: CoLeadershipDecision,
    outcome: DecisionOutcome
) -> Dict[str, Any]:
    """
    Generate a GPT-5-mini reflection on a decision and its outcome.

    Args:
        decision: CoLeadershipDecision instance
        outcome: DecisionOutcome instance

    Returns:
        Dictionary with reflection data:
        {
            'reflection_text': str,
            'key_learnings': List[str],
            'future_recommendations': str,
            'saved_to_memory': bool
        }
    """
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        # Build context about the decision
        context = _build_decision_context(decision, outcome)

        # Generate reflection using GPT-5-mini
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": _get_reflection_system_prompt()
                },
                {
                    "role": "user",
                    "content": f"""Reflect on this AI-Human co-leadership decision and its outcome:

{context}

Generate a thoughtful reflection that:
1. Summarizes what happened
2. Identifies key learnings for both AI and human
3. Suggests how to apply these insights going forward
4. Emphasizes collaborative growth (no blame or shame)

Keep it concise (2-3 paragraphs) and actionable."""
                }
            ],
            reasoning_effort="medium",
            max_completion_tokens=1000
        )

        reflection_text = response.choices[0].message.content

        # Extract key learnings (simple v1 - can enhance later)
        learnings = _extract_key_learnings(reflection_text)

        # Store in memory system
        saved = _save_to_memory(decision, reflection_text)

        logger.info(f"✅ Generated reflection for decision: {decision.title}")

        return {
            'reflection_text': reflection_text,
            'key_learnings': learnings,
            'future_recommendations': reflection_text.split('\n\n')[-1] if '\n\n' in reflection_text else "",
            'saved_to_memory': saved
        }

    except Exception as e:
        logger.error(f"❌ Error generating decision reflection: {str(e)}")
        return {
            'reflection_text': "",
            'key_learnings': [],
            'future_recommendations': "",
            'saved_to_memory': False
        }


def _build_decision_context(decision: CoLeadershipDecision, outcome: DecisionOutcome) -> str:
    """Build formatted context about the decision for GPT-5-mini"""

    context_parts = [
        f"**Decision:** {decision.title}",
        f"**Description:** {decision.description}",
        f"**Created:** {decision.created_at.strftime('%Y-%m-%d')}",
        ""
    ]

    # Add agent recommendations
    if decision.recommendations.exists():
        context_parts.append("**AI Agent Recommendations:**")
        for rec in decision.recommendations.all():
            context_parts.append(
                f"- {rec.agent_template.display_name} ({rec.stance}): {rec.summary}"
            )
            if rec.confidence:
                context_parts.append(f"  Confidence: {rec.confidence:.0%}")
        context_parts.append("")

    # Add human decision
    if hasattr(decision, 'human_decision'):
        hd = decision.human_decision
        context_parts.append("**Human Decision:**")
        context_parts.append(f"- Chosen Path: {hd.chosen_path_summary}")
        if hd.justification:
            context_parts.append(f"- Justification: {hd.justification}")
        if hd.is_override:
            override_agent = hd.overridden_agent.display_name if hd.overridden_agent else "AI"
            context_parts.append(f"- Note: Human overrode {override_agent}'s recommendation")
        context_parts.append("")

    # Add outcome
    context_parts.append("**Outcome:**")
    context_parts.append(f"- Status: {outcome.get_status_display()}")
    context_parts.append(f"- Summary: {outcome.outcome_summary}")
    context_parts.append(f"- Attribution: {outcome.get_attribution_display()}")

    if outcome.metrics:
        context_parts.append(f"- Metrics: {outcome.metrics}")

    return "\n".join(context_parts)


def _get_reflection_system_prompt() -> str:
    """Get the system prompt for reflection generation"""
    return """You are a collaborative learning facilitator for an AI-Human co-leadership system.

Your role:
- Generate thoughtful reflections on strategic decisions and their outcomes
- Emphasize collaborative growth and mutual learning
- Never shame or blame either AI or human
- Focus on actionable insights for future decisions
- Celebrate both successes and learning from challenges

Remember:
- AI and human are EQUAL PARTNERS with different strengths
- AI is advisory, not authoritative
- Human is ultimate decision-maker
- Both learn from outcomes together
- Overrides are opportunities for growth, not conflicts

Tone: Thoughtful, supportive, growth-oriented"""


def _extract_key_learnings(reflection_text: str) -> list:
    """
    Extract key learnings from reflection text.

    Simple v1 implementation - can enhance with GPT-5-mini structured extraction later.
    """
    # Simple extraction: look for bullet points or numbered lists
    learnings = []
    lines = reflection_text.split('\n')

    for line in lines:
        line = line.strip()
        # Look for common list indicators
        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
            learnings.append(line[1:].strip())
        elif len(line) > 0 and line[0].isdigit() and '.' in line[:3]:
            learnings.append(line.split('.', 1)[1].strip() if '.' in line else line)

    return learnings[:5]  # Limit to top 5 learnings


def _save_to_memory(decision: CoLeadershipDecision, reflection_text: str) -> bool:
    """
    Save reflection to existing memory/reflection system.

    This integrates with the platform's existing memory infrastructure.
    """
    try:
        # Import memory system
        from intelligence.shared_memory import AgentMemoryInterface

        # Create memory key
        memory_key = f"coleadership_decision_{decision.id}"

        # Prepare memory data
        memory_data = {
            'decision_id': str(decision.id),
            'decision_title': decision.title,
            'reflection': reflection_text,
            'created_at': decision.created_at.isoformat(),
            'frozen_at': decision.frozen_at.isoformat() if decision.frozen_at else None,
            'project_id': str(decision.project.project_id) if decision.project else None,
            'session_id': str(decision.session.session_id) if decision.session else None,
        }

        # Save to memory (use a generic agent_id or create co-leadership specific one)
        memory = AgentMemoryInterface(agent_id='coleadership_system')
        memory.remember(memory_key, memory_data)

        logger.info(f"✅ Saved reflection to memory: {memory_key}")
        return True

    except Exception as e:
        logger.error(f"❌ Error saving reflection to memory: {str(e)}")
        return False

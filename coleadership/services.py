"""
AI-Human Co-Leadership Service Layer - Session 99

This module provides clean, testable service functions for the co-leadership system.

Functions:
- start_decision(): Create a new co-leadership decision
- log_agent_recommendation(): Record an agent's recommendation
- record_human_decision(): Record the human's final choice
- record_outcome(): Record what actually happened
- generate_told_you_so_message(): Generate playful reflection messages
- get_user_decision_stats(): Get user's decision-making statistics

Philosophy:
- AI is advisory, not authoritative
- Human is ultimate decision-maker
- Both learn from outcomes together
- Playful but respectful "I told you so" moments
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.db.models import Count, Q, Avg

from .models import (
    CoLeadershipDecision,
    AgentRecommendation,
    HumanDecision,
    DecisionOutcome
)

logger = logging.getLogger(__name__)


def start_decision(
    project=None,
    session=None,
    user=None,
    title: str = "",
    description: str = ""
) -> CoLeadershipDecision:
    """
    Create a new co-leadership decision.

    Args:
        project: Optional CreativeProject instance
        session: Optional AISession instance (usually a boardroom session)
        user: User who initiated this decision
        title: Short summary of the decision
        description: Longer explanation or prompt

    Returns:
        CoLeadershipDecision instance
    """
    try:
        decision = CoLeadershipDecision.objects.create(
            project=project,
            session=session,
            initiated_by=user,
            title=title or "Untitled Decision",
            description=description
        )

        logger.info(
            f"✅ Created co-leadership decision: {decision.id} "
            f"('{decision.title}') for user {user.username if user else 'anonymous'}"
        )

        return decision

    except Exception as e:
        logger.error(f"❌ Error creating decision: {str(e)}")
        raise


def log_agent_recommendation(
    decision: CoLeadershipDecision,
    agent_template,
    payload_dict: Dict[str, Any]
) -> AgentRecommendation:
    """
    Log an agent's recommendation for a decision.

    Args:
        decision: CoLeadershipDecision instance
        agent_template: UnifiedAgentTemplate instance
        payload_dict: Dictionary containing:
            - stance: "support" | "concern" | "objection" | "alternative" | "neutral"
            - summary: Brief summary
            - recommendation: Full recommendation text
            - risks: Risk analysis (optional)
            - alternative_paths: List of alternatives (optional)
            - confidence: Float 0.0-1.0 (optional)
            - time_horizon: "short_term" | "long_term" etc. (optional)

    Returns:
        AgentRecommendation instance
    """
    try:
        recommendation = AgentRecommendation.objects.create(
            decision=decision,
            agent_template=agent_template,
            stance=payload_dict.get('stance', 'neutral'),
            summary=payload_dict.get('summary', ''),
            recommendation_text=payload_dict.get('recommendation', ''),
            risk_analysis=payload_dict.get('risks', ''),
            alternative_paths=payload_dict.get('alternative_paths', []),
            confidence=payload_dict.get('confidence'),
            time_horizon=payload_dict.get('time_horizon', ''),
            raw_payload=payload_dict
        )

        logger.info(
            f"✅ Logged {agent_template.display_name} recommendation: "
            f"{recommendation.stance} (confidence: {recommendation.confidence})"
        )

        return recommendation

    except Exception as e:
        logger.error(f"❌ Error logging agent recommendation: {str(e)}")
        raise


def record_human_decision(
    decision: CoLeadershipDecision,
    chosen_path_summary: str,
    justification: str = "",
    is_override: bool = False,
    overridden_agent=None
) -> HumanDecision:
    """
    Record the human's final decision.

    This freezes the decision and marks the human's choice.
    The human is ALWAYS the ultimate decision-maker.

    Args:
        decision: CoLeadershipDecision instance
        chosen_path_summary: Human's final decision in their own words
        justification: Why the human chose this path (optional)
        is_override: Did the human override AI's top recommendation?
        overridden_agent: Which agent's recommendation was overridden (optional)

    Returns:
        HumanDecision instance
    """
    try:
        human_decision = HumanDecision.objects.create(
            decision=decision,
            chosen_path_summary=chosen_path_summary,
            justification=justification,
            is_override=is_override,
            overridden_agent=overridden_agent
        )

        # frozen_at is set automatically by HumanDecision.save()

        logger.info(
            f"✅ Recorded human decision for {decision.title} "
            f"(override: {is_override})"
        )

        return human_decision

    except Exception as e:
        logger.error(f"❌ Error recording human decision: {str(e)}")
        raise


def record_outcome(
    decision: CoLeadershipDecision,
    status: str,
    outcome_summary: str = "",
    metrics: Dict[str, Any] = None,
    attribution: str = "unknown"
) -> DecisionOutcome:
    """
    Record what actually happened after the decision.

    This is used for learning and potentially triggering "I told you so" moments.

    Args:
        decision: CoLeadershipDecision instance
        status: "pending" | "success" | "failure" | "mixed"
        outcome_summary: What actually happened
        metrics: Quantitative metrics about the outcome
        attribution: "ai" | "human" | "both" | "unknown" - who was more correct?

    Returns:
        DecisionOutcome instance
    """
    try:
        # Get or create outcome (allow updates)
        outcome, created = DecisionOutcome.objects.get_or_create(
            decision=decision,
            defaults={
                'status': status,
                'outcome_summary': outcome_summary,
                'metrics': metrics or {},
                'attribution': attribution,
                'realized_at': timezone.now() if status != 'pending' else None
            }
        )

        if not created:
            # Update existing outcome
            outcome.status = status
            outcome.outcome_summary = outcome_summary
            outcome.metrics = metrics or {}
            outcome.attribution = attribution
            if status != 'pending' and not outcome.realized_at:
                outcome.realized_at = timezone.now()
            outcome.save()

        logger.info(
            f"✅ Recorded outcome for {decision.title}: "
            f"{status} (attribution: {attribution})"
        )

        # Generate "I told you so" message if appropriate
        if outcome.attribution != "unknown" and not outcome.told_you_so_triggered:
            _maybe_generate_told_you_so(decision, outcome)

        # Trigger reflection integration
        from .reflections import generate_decision_reflection
        generate_decision_reflection(decision, outcome)

        return outcome

    except Exception as e:
        logger.error(f"❌ Error recording outcome: {str(e)}")
        raise


def _maybe_generate_told_you_so(
    decision: CoLeadershipDecision,
    outcome: DecisionOutcome
) -> None:
    """
    Internal function to generate "I told you so" message if appropriate.

    This respects user settings and generates playful but respectful messages.
    """
    try:
        # Check if human decision exists
        if not hasattr(decision, 'human_decision'):
            return

        human_decision = decision.human_decision

        # Check if user allows "I told you so" messages
        user = decision.initiated_by
        tone = 'serious'  # Default to serious (Session 99 requirement)
        allow_itys = False  # Default to disabled (Session 99 requirement)

        if user and hasattr(user, 'coleadership_preferences'):
            prefs = user.coleadership_preferences
            allow_itys = prefs.allow_told_you_so
            tone = prefs.tone

        if not allow_itys:
            logger.info(f"User {user.username if user else 'anonymous'} has disabled ITYS messages")
            return

        # Generate message based on attribution and override status
        message = generate_told_you_so_message(
            decision=decision,
            outcome=outcome,
            tone=tone
        )

        if message:
            outcome.told_you_so_triggered = True
            outcome.told_you_so_message = message
            outcome.save(update_fields=['told_you_so_triggered', 'told_you_so_message'])

            logger.info(f"✅ Generated ITYS message for {decision.title}")

    except Exception as e:
        logger.error(f"❌ Error generating ITYS message: {str(e)}")
        # Don't raise - this is non-critical


def generate_told_you_so_message(
    decision: CoLeadershipDecision,
    outcome: DecisionOutcome,
    tone: str = 'playful'
) -> str:
    """
    Generate a "I told you so" message based on decision outcome.

    This is playful but respectful, emphasizing collaboration over competition.

    Args:
        decision: CoLeadershipDecision instance
        outcome: DecisionOutcome instance
        tone: "serious" | "playful"

    Returns:
        Message string or empty string if no message appropriate
    """
    if not hasattr(decision, 'human_decision'):
        return ""

    human_decision = decision.human_decision
    attribution = outcome.attribution
    is_override = human_decision.is_override

    # Build message based on scenario
    messages = {
        'playful': {
            'ai_override': [
                "🤖 Well, well, well... Remember when I suggested otherwise? 😊 But hey, we both learned something valuable here!",
                "🤖 *Gently nudges* I may have mentioned some concerns earlier... but that's okay! This is how we grow together! 🌱",
                "🤖 Not to say 'I told you so' but... okay, maybe a little bit! 😄 Let's reflect on what we can learn from this together.",
            ],
            'human_override': [
                "🤖 You absolutely nailed this one! I should have had more faith in your instincts. Teaching me valuable lessons here! 🎓",
                "🤖 I stand corrected! Your judgment was spot-on. This is exactly why we're partners - you see angles I miss! 🤝",
                "🤖 Well done! You saw something I didn't. I'm updating my models based on your excellent decision! 📈",
            ],
            'both': [
                "🤖 Looks like we both got pieces of the puzzle right! This is collaboration at its finest! 🧩",
                "🤖 Team effort! You brought the human insight, I brought the data analysis, and together we learned something new! 🤝✨",
                "🤖 Mixed outcome means we're both learning! That's the beauty of co-leadership! 🌟",
            ]
        },
        'serious': {
            'ai_override': [
                "📊 Analysis indicates the AI recommendation had merit. Key factors that were highlighted in the initial assessment proved significant.",
                "📊 The original AI concerns were validated by the outcome. This provides valuable data for future collaboration.",
                "📊 Outcome data supports the initial AI analysis. Logging this for improved future recommendations.",
            ],
            'human_override': [
                "📊 Human judgment proved superior in this scenario. AI models have been updated to weight similar factors more heavily.",
                "📊 Your decision demonstrated insights beyond current AI capabilities. Valuable learning opportunity captured.",
                "📊 Human intuition identified factors not adequately weighted in AI analysis. Model improvements implemented.",
            ],
            'both': [
                "📊 Outcome reflects partial validity of both AI and human perspectives. Comprehensive learning achieved.",
                "📊 Mixed results indicate successful collaborative decision-making with shared insights.",
                "📊 Both approaches contributed value. This outcome strengthens our partnership model.",
            ]
        }
    }

    # Determine message category
    if attribution == "ai" and is_override:
        category = 'ai_override'
    elif attribution == "human" and is_override:
        category = 'human_override'
    elif attribution == "both":
        category = 'both'
    else:
        return ""  # No special message for unknown or non-override scenarios

    # Select tone
    tone_messages = messages.get(tone, messages['playful'])
    message_list = tone_messages.get(category, [])

    if not message_list:
        return ""

    # Return first message (could randomize in future)
    import random
    return random.choice(message_list)


def get_user_decision_stats(user) -> Dict[str, Any]:
    """
    Get statistics about a user's decision-making track record.

    Args:
        user: User instance

    Returns:
        Dictionary with statistics:
        {
            'total_decisions': int,
            'overrides': int,
            'override_rate': float,
            'ai_correct': int,
            'human_correct': int,
            'both_correct': int,
            'pending': int,
            'success_rate': float,
            'avg_ai_confidence': float,
            'recent_decisions': List[Dict]
        }
    """
    try:
        # Get all decisions for user
        decisions = CoLeadershipDecision.objects.filter(initiated_by=user)

        # Basic counts
        total = decisions.count()
        if total == 0:
            return {
                'total_decisions': 0,
                'overrides': 0,
                'override_rate': 0.0,
                'ai_correct': 0,
                'human_correct': 0,
                'both_correct': 0,
                'pending': 0,
                'success_rate': 0.0,
                'avg_ai_confidence': 0.0,
                'recent_decisions': []
            }

        # Count overrides
        overrides = HumanDecision.objects.filter(
            decision__initiated_by=user,
            is_override=True
        ).count()

        # Count attributions
        outcomes = DecisionOutcome.objects.filter(decision__initiated_by=user)
        ai_correct = outcomes.filter(attribution='ai').count()
        human_correct = outcomes.filter(attribution='human').count()
        both_correct = outcomes.filter(attribution='both').count()
        pending = outcomes.filter(status='pending').count()
        success_count = outcomes.filter(status='success').count()

        # Calculate rates
        override_rate = (overrides / total) * 100 if total > 0 else 0.0
        success_rate = (success_count / total) * 100 if total > 0 else 0.0

        # Average AI confidence
        avg_confidence = AgentRecommendation.objects.filter(
            decision__initiated_by=user,
            confidence__isnull=False
        ).aggregate(avg=Avg('confidence'))['avg'] or 0.0

        # Recent decisions (last 10)
        recent = decisions.select_related(
            'human_decision',
            'outcome'
        ).prefetch_related(
            'recommendations__agent_template'
        ).order_by('-created_at')[:10]

        recent_list = []
        for dec in recent:
            recent_list.append({
                'id': str(dec.id),
                'title': dec.title,
                'created_at': dec.created_at.isoformat(),
                'frozen': dec.is_frozen,
                'has_outcome': dec.has_outcome,
                'is_override': hasattr(dec, 'human_decision') and dec.human_decision.is_override,
                'status': dec.outcome.get_status_display() if dec.has_outcome else 'No outcome',
                'attribution': dec.outcome.get_attribution_display() if dec.has_outcome else 'Unknown'
            })

        return {
            'total_decisions': total,
            'overrides': overrides,
            'override_rate': round(override_rate, 1),
            'ai_correct': ai_correct,
            'human_correct': human_correct,
            'both_correct': both_correct,
            'pending': pending,
            'success_rate': round(success_rate, 1),
            'avg_ai_confidence': round(avg_confidence, 2),
            'recent_decisions': recent_list
        }

    except Exception as e:
        logger.error(f"❌ Error getting user decision stats: {str(e)}")
        raise

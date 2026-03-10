"""
Learning Read Service — closes the feedback loop.

Reads UserAgentLearning records and provides routing recommendations.
This is the critical missing piece: learning data was being WRITTEN
by 8 bridges but never READ BACK to influence decisions.

Phase 2: Called during PA routing to bias toward historically
successful agents/tools for a given user + intent.
"""

import logging
from typing import Any

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Feature flag — allows gradual rollout
LEARNING_ROUTING_ENABLED = getattr(settings, 'LEARNING_ROUTING_ENABLED', True)

# Minimum confidence to consider a learning record relevant
MIN_CONFIDENCE = 0.5

# Maximum number of learning records to consult per decision
MAX_RECORDS_PER_QUERY = 10

# Intent → learning_domain mapping
_INTENT_TO_DOMAINS = {
    'image_creation': ['agent_execution_performance', 'task_type_content_creation'],
    'video_creation': ['agent_execution_performance', 'task_type_content_creation'],
    'audio_creation': ['agent_execution_performance', 'task_type_content_creation'],
    'content_review': ['agent_execution_performance', 'task_type_content_creation'],
    'research_and_create': ['agent_execution_performance', 'task_type_research', 'task_type_content_creation'],
    'initiatives': ['agent_execution_performance', 'task_type_general'],
    'dreams': ['agent_execution_performance'],
    'system_health_check': ['agent_execution_performance', 'general_intelligence'],
    'general': ['agent_execution_performance', 'general_intelligence', 'chat_preferences'],
}


def get_learning_recommendation(
    user_id: Any,
    intent: str | None,
    routed_to: str | None,
) -> dict:
    """
    Query UserAgentLearning for routing recommendations.

    Returns:
        {
            'consulted': True/False,
            'used': True/False,
            'record_ids': [uuid, ...],
            'explanation': str,
            'score_delta': float,  # positive = boost, negative = penalize
            'preferred_tool': str | None,  # alternative suggestion if any
        }
    """
    if not LEARNING_ROUTING_ENABLED:
        return {
            'consulted': False,
            'used': False,
            'record_ids': [],
            'explanation': 'Learning routing disabled via LEARNING_ROUTING_ENABLED',
            'score_delta': 0.0,
            'preferred_tool': None,
        }

    try:
        from core.models import UserAgentLearning

        # Find relevant learning domains for this intent
        domains = _INTENT_TO_DOMAINS.get(intent or 'general', ['agent_execution_performance'])

        records = list(
            UserAgentLearning.objects.filter(
                user_id=user_id,
                learning_domain__in=domains,
                confidence_score__gte=MIN_CONFIDENCE,
                is_active=True,
            )
            .order_by('-confidence_score', '-updated_at')
            [:MAX_RECORDS_PER_QUERY]
        )

        if not records:
            return {
                'consulted': True,
                'used': False,
                'record_ids': [],
                'explanation': f'No learning records found for domains={domains}',
                'score_delta': 0.0,
                'preferred_tool': None,
            }

        record_ids = [str(r.id) for r in records]

        # Analyze learning records for routing signal
        # Look for agent performance patterns
        agent_scores = {}
        for r in records:
            if r.learning_domain == 'agent_execution_performance':
                agent = r.agent_name
                if agent:
                    sr = r.success_rate or 0.0
                    conf = r.confidence_score or 0.0
                    agent_scores[agent] = {
                        'success_rate': sr,
                        'confidence': conf,
                        'combined': sr * conf,
                        'usage_count': r.usage_count or 0,
                    }

        # Check if routed_to matches a high-performing agent
        explanation_parts = []
        score_delta = 0.0
        preferred_tool = None

        if agent_scores:
            # Find best agent
            best_agent = max(agent_scores, key=lambda a: agent_scores[a]['combined'])
            best_score = agent_scores[best_agent]

            if routed_to and routed_to in agent_scores:
                current = agent_scores[routed_to]
                if current['combined'] >= 0.7:
                    score_delta = 0.1  # Boost — this agent works well
                    explanation_parts.append(
                        f"{routed_to} has {current['success_rate']:.0%} success rate "
                        f"(confidence={current['confidence']:.2f}, used {current['usage_count']}x)"
                    )
                elif current['combined'] < 0.3 and best_score['combined'] > 0.6:
                    score_delta = -0.1
                    preferred_tool = best_agent
                    explanation_parts.append(
                        f"{routed_to} has low performance ({current['success_rate']:.0%}); "
                        f"consider {best_agent} ({best_score['success_rate']:.0%} success)"
                    )

            # Check for learned preferences (chat_preferences domain)
            pref_records = [r for r in records if r.learning_domain == 'chat_preferences']
            if pref_records:
                for pr in pref_records[:2]:
                    content = pr.learning_content or {}
                    if 'preference_type' in content:
                        explanation_parts.append(
                            f"Learned preference: {content.get('preference_type')}"
                        )

        explanation = '; '.join(explanation_parts) if explanation_parts else 'Learning records found but no actionable signal'
        used = score_delta != 0.0 or preferred_tool is not None

        # Update usage tracking on consulted records
        if records:
            UserAgentLearning.objects.filter(
                id__in=[r.id for r in records]
            ).update(
                usage_count=models_F('usage_count') + 1,
                last_used=timezone.now(),
            )

        return {
            'consulted': True,
            'used': used,
            'record_ids': record_ids,
            'explanation': explanation,
            'score_delta': score_delta,
            'preferred_tool': preferred_tool,
        }

    except Exception as e:
        logger.warning(f"Learning read service error: {e}", exc_info=True)
        return {
            'consulted': False,
            'used': False,
            'record_ids': [],
            'explanation': f'Error: {e}',
            'score_delta': 0.0,
            'preferred_tool': None,
        }


# Avoid circular import
def models_F(field):
    from django.db.models import F
    return F(field)

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

# Feature flags — default OFF until intentionally enabled in production
LEARNING_ROUTING_ENABLED = getattr(settings, 'LEARNING_ROUTING_ENABLED', False)
LEARNING_PROMPT_INJECTION_ENABLED = getattr(settings, 'LEARNING_PROMPT_INJECTION_ENABLED', False)

# Minimum confidence to consider a learning record relevant
MIN_CONFIDENCE = 0.5

# Minimum usage_count before an agent's performance can trigger a routing override
MIN_SAMPLES_FOR_OVERRIDE = 3

# Maximum number of learning records to consult per decision
MAX_RECORDS_PER_QUERY = 10

# FC tool name → agent_name mapping for learning record lookups.
# In the FC path, routed_to is a tool name (e.g. 'brainstorm_tool') but
# UserAgentLearning.agent_name stores agent class names (e.g. 'BoardroomAgent').
# This map bridges the gap so learning records can actually be matched.
_TOOL_TO_AGENT_NAME = {
    'brainstorm_tool': 'BoardroomAgent',
    'initiative_tool': 'InitiativeManagerAgent',
    'content_review_tool': 'ContentReviewAgent',
    'generate_blog_tool': 'ContentWriterAgent',
    'stock_intelligence_tool': 'StockIntelligenceAgent',
    'opportunity_manager_tool': 'OpportunityPipelineAgent',
    'research_and_create_tool': 'ResearchAgent',
    'governance_tool': 'GovernanceAgent',
    'dream_tool': 'DreamAgent',
    'spider_data_tool': 'SpiderAgent',
    'ml_analysis': 'MLPredictionAgent',
    'reasoning_engine_tool': 'ThinkingAgent',
    'run_agent': None,  # dynamic — skip
}


def _normalize_routed_to(routed_to: str | None) -> str | None:
    """Normalize FC tool names to agent names for learning record matching."""
    if not routed_to:
        return routed_to
    if routed_to in _TOOL_TO_AGENT_NAME:
        return _TOOL_TO_AGENT_NAME[routed_to]  # may be None for dynamic tools
    # Already an agent name or unknown tool — return as-is
    return routed_to


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

    routed_to may be a PA tool name (FC path) or an agent name (legacy path).
    We normalize tool names → agent names so records actually match.

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

    # Normalize tool names → agent names so FC path can match learning records
    routed_to = _normalize_routed_to(routed_to)

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
                elif (
                    # Session 1078: Relaxed thresholds (was 0.3/0.6)
                    current['combined'] < 0.4
                    and best_score['combined'] > 0.55
                    and current['usage_count'] >= MIN_SAMPLES_FOR_OVERRIDE
                    and best_score['usage_count'] >= MIN_SAMPLES_FOR_OVERRIDE
                ):
                    # Verify best_agent is not blocked before recommending
                    try:
                        from core.models_unified_system import AgentControlEntry
                        if AgentControlEntry.is_blocked(best_agent):
                            explanation_parts.append(
                                f"{routed_to} low performance but {best_agent} is blocked"
                            )
                        else:
                            score_delta = -0.1
                            preferred_tool = best_agent
                            explanation_parts.append(
                                f"{routed_to} has low performance ({current['success_rate']:.0%}); "
                                f"consider {best_agent} ({best_score['success_rate']:.0%} success)"
                            )
                    except Exception:
                        score_delta = -0.1
                        preferred_tool = best_agent
                        explanation_parts.append(
                            f"{routed_to} has low performance ({current['success_rate']:.0%}); "
                            f"consider {best_agent} ({best_score['success_rate']:.0%} success)"
                        )
                else:
                    # Session 1078: Shadow mode — log what WOULD have been overridden
                    # This helps tune thresholds without risking production behavior
                    if (
                        current['combined'] < 0.5
                        and best_score['combined'] > current['combined'] + 0.15
                        and current['usage_count'] >= 2
                    ):
                        logger.info(
                            f"[LEARNING_SHADOW] Would consider override: "
                            f"{routed_to} (combined={current['combined']:.2f}, "
                            f"sr={current['success_rate']:.0%}, n={current['usage_count']}) → "
                            f"{best_agent} (combined={best_score['combined']:.2f}, "
                            f"sr={best_score['success_rate']:.0%}, n={best_score['usage_count']})"
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


# ── Phase 3: Prompt preference injection ──────────────────────────────

def get_learned_preferences_for_prompt(user_id, agent_name: str | None = None) -> str:
    """
    Build a short preference summary from UserAgentLearning records
    suitable for injection into agent system prompts.

    Returns a human-readable string (empty if nothing found).
    """
    if not LEARNING_PROMPT_INJECTION_ENABLED:
        return ''

    try:
        from core.models import UserAgentLearning

        # Gather chat_preferences + general_intelligence records
        records = list(
            UserAgentLearning.objects.filter(
                user_id=user_id,
                learning_domain__in=['chat_preferences', 'general_intelligence'],
                confidence_score__gte=MIN_CONFIDENCE,
                is_active=True,
            )
            .order_by('-confidence_score')
            [:5]
        )

        if not records:
            return ''

        parts = []
        for r in records:
            content = r.learning_content or {}

            if r.learning_domain == 'chat_preferences':
                # Extract structured preferences
                skills = content.get('skills', [])
                industry = content.get('industry', '')
                work_style = content.get('work_style', '')
                experience = content.get('experience_level', '')

                if skills:
                    if isinstance(skills, dict):
                        skill_str = ', '.join(sorted(skills.keys())[:8])
                    elif isinstance(skills, list):
                        skill_str = ', '.join(str(s) for s in skills[:8])
                    else:
                        skill_str = str(skills)
                    parts.append(f"User skills: {skill_str}")
                if industry:
                    if isinstance(industry, dict):
                        parts.append(f"Industry: {', '.join(sorted(industry.keys())[:4])}")
                    else:
                        parts.append(f"Industry: {industry}")
                if work_style:
                    if isinstance(work_style, dict):
                        parts.append(f"Work style: {', '.join(sorted(work_style.keys())[:4])}")
                    else:
                        parts.append(f"Work style: {work_style}")
                if experience:
                    parts.append(f"Experience level: {experience}")

            elif r.learning_domain == 'general_intelligence':
                # Extract any learned patterns
                insight = content.get('insight', content.get('pattern', ''))
                if insight and len(str(insight)) < 200:
                    parts.append(f"Learned: {insight}")

        if not parts:
            return ''

        # Deduplicate and cap
        seen = set()
        unique = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        result = 'User preferences (from learning): ' + '; '.join(unique[:6])
        # Hard cap to prevent prompt bloat (max ~300 chars)
        return result[:300]

    except Exception as e:
        logger.debug(f"Learned preferences lookup failed: {e}")
        return ''


# Avoid circular import
def models_F(field):
    from django.db.models import F
    return F(field)

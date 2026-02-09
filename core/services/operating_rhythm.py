"""
Operating Rhythm Service
========================

Session 914.7: Daily/Weekly Operating Rhythm for Initiative Pipeline

Problem: With 180+ initiatives, agents treat all equally. No way to focus
resources on founder priorities or get weekly accountability.

Solution: Simple operating rhythm:

Daily:
- Founder sets Top 3 priorities
- Agents must map any initiative to one of those priorities
- No mapping = auto-defer

Weekly:
- System produces "Ship / Learn / Kill" report
- Founder gives one paragraph of feedback
- Feedback becomes training signal

Usage:
    from core.services.operating_rhythm import (
        set_daily_priorities,
        get_daily_priorities,
        generate_weekly_report,
        submit_weekly_feedback
    )

    # Set today's priorities
    set_daily_priorities([
        "Launch podcast feature",
        "Fix authentication bugs",
        "Improve content quality"
    ])

    # Get weekly report
    report = generate_weekly_report()
    print(report['shipped'], report['learned'], report['kill_candidates'])

    # Submit feedback (becomes training signal)
    submit_weekly_feedback("Focus more on user-facing features...")
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal

from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Q, F

logger = logging.getLogger(__name__)

# Cache keys
CACHE_KEY_DAILY_PRIORITIES = "operating_rhythm_daily_priorities"
CACHE_KEY_PRIORITY_DATE = "operating_rhythm_priority_date"
CACHE_TTL = 86400  # 24 hours


def set_daily_priorities(
    priorities: List[str],
    set_by: str = 'founder'
) -> Dict[str, Any]:
    """
    Set the top 3 daily priorities.

    Args:
        priorities: List of 1-3 priority strings
        set_by: Who is setting priorities (default: 'founder')

    Returns:
        Dict with success status and priority info
    """
    from core.models_unified_system import FounderFeedback

    # Validate
    if not priorities:
        return {'success': False, 'error': 'No priorities provided'}

    if len(priorities) > 3:
        priorities = priorities[:3]  # Take only top 3

    # Store in cache
    today = date.today().isoformat()
    cache.set(CACHE_KEY_DAILY_PRIORITIES, priorities, CACHE_TTL)
    cache.set(CACHE_KEY_PRIORITY_DATE, today, CACHE_TTL)

    # Also store in database for history
    try:
        FounderFeedback.objects.create(
            feedback_type='daily_priorities',
            content={
                'priorities': priorities,
                'date': today,
                'set_by': set_by
            },
            created_by=set_by
        )
    except Exception as e:
        logger.warning(f"[Session 914.7] Failed to persist daily priorities: {e}")

    logger.info(
        f"[Session 914.7] Daily priorities set by {set_by}: {priorities}"
    )

    return {
        'success': True,
        'date': today,
        'priorities': priorities,
        'set_by': set_by
    }


def get_daily_priorities() -> Dict[str, Any]:
    """
    Get the current daily priorities.

    Returns:
        Dict with priorities and metadata
    """
    priorities = cache.get(CACHE_KEY_DAILY_PRIORITIES, [])
    priority_date = cache.get(CACHE_KEY_PRIORITY_DATE)
    today = date.today().isoformat()

    # Check if priorities are stale
    is_current = priority_date == today

    return {
        'priorities': priorities,
        'date': priority_date,
        'is_current': is_current,
        'count': len(priorities),
        'needs_update': not is_current or not priorities
    }


def map_initiative_to_priority(
    initiative_id: str,
    priority_index: int,
    mapped_by: str = 'system'
) -> Dict[str, Any]:
    """
    Map an initiative to one of the daily priorities.

    Args:
        initiative_id: UUID of the initiative
        priority_index: Index (0-2) of the priority to map to
        mapped_by: Who is mapping (default: 'system')

    Returns:
        Dict with mapping result
    """
    from core.models_document_registry import Initiative

    priorities = cache.get(CACHE_KEY_DAILY_PRIORITIES, [])

    if not priorities:
        return {'success': False, 'error': 'No daily priorities set'}

    if priority_index < 0 or priority_index >= len(priorities):
        return {'success': False, 'error': f'Invalid priority index: {priority_index}'}

    try:
        initiative = Initiative.objects.get(id=initiative_id)
    except Initiative.DoesNotExist:
        return {'success': False, 'error': 'Initiative not found'}

    # Store mapping in initiative metadata or a new field
    # For now, we'll use the manual_priority_rank field (1-3 maps to priorities 0-2)
    initiative.manual_priority_rank = priority_index + 1
    initiative.manual_priority_reason = f"Mapped to daily priority: {priorities[priority_index]}"
    initiative.save(update_fields=['manual_priority_rank', 'manual_priority_reason'])

    logger.info(
        f"[Session 914.7] Initiative {initiative.name[:40]} mapped to priority #{priority_index + 1}: "
        f"{priorities[priority_index]}"
    )

    return {
        'success': True,
        'initiative_id': str(initiative_id),
        'initiative_name': initiative.name,
        'priority_index': priority_index,
        'priority_text': priorities[priority_index],
        'mapped_by': mapped_by
    }


def check_initiative_priority_mapping(initiative) -> Dict[str, Any]:
    """
    Check if an initiative is mapped to a daily priority.

    Returns:
        Dict with mapping status and recommendation
    """
    priorities = cache.get(CACHE_KEY_DAILY_PRIORITIES, [])

    if not priorities:
        return {
            'has_priorities': False,
            'is_mapped': False,
            'should_defer': False,
            'reason': 'No daily priorities set'
        }

    # Check if initiative has a priority mapping
    if initiative.manual_priority_rank and 1 <= initiative.manual_priority_rank <= len(priorities):
        priority_idx = initiative.manual_priority_rank - 1
        return {
            'has_priorities': True,
            'is_mapped': True,
            'priority_index': priority_idx,
            'priority_text': priorities[priority_idx],
            'should_defer': False,
            'reason': f'Mapped to priority #{initiative.manual_priority_rank}'
        }

    # Not mapped - should defer
    return {
        'has_priorities': True,
        'is_mapped': False,
        'should_defer': True,
        'reason': 'Not mapped to any daily priority - auto-defer recommended'
    }


def generate_weekly_report(
    week_start: date = None,
    week_end: date = None
) -> Dict[str, Any]:
    """
    Generate the weekly "Ship / Learn / Kill" report.

    Args:
        week_start: Start of week (default: 7 days ago)
        week_end: End of week (default: today)

    Returns:
        Dict with shipped, learned, blocked, kill_candidates
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.models_pilot_readiness import Experiment, ExperimentLearning
    from core.models_deliverables import Deliverable

    if week_end is None:
        week_end = date.today()
    if week_start is None:
        week_start = week_end - timedelta(days=7)

    week_start_dt = datetime.combine(week_start, datetime.min.time())
    week_end_dt = datetime.combine(week_end, datetime.max.time())

    if timezone.is_aware(timezone.now()):
        week_start_dt = timezone.make_aware(week_start_dt)
        week_end_dt = timezone.make_aware(week_end_dt)

    # SHIPPED: Initiatives that progressed stages this week
    shipped = []
    progressed_initiatives = Initiative.objects.filter(
        updated_at__gte=week_start_dt,
        updated_at__lte=week_end_dt,
        current_stage__gt=1
    ).order_by('-current_stage', '-updated_at')[:20]

    for init in progressed_initiatives:
        shipped.append({
            'id': str(init.id),
            'name': init.name[:60],
            'stage': init.current_stage,
            'track': init.execution_track,
            'updated_at': init.updated_at.isoformat() if init.updated_at else None
        })

    # Also check deliverables created this week
    deliverables_created = Deliverable.objects.filter(
        created_at__gte=week_start_dt,
        created_at__lte=week_end_dt
    ).count()

    # LEARNED: Experiment learnings from this week
    learned = []
    try:
        recent_learnings = ExperimentLearning.objects.filter(
            created_at__gte=week_start_dt,
            created_at__lte=week_end_dt
        ).select_related('experiment').order_by('-created_at')[:10]

        for learning in recent_learnings:
            learned.append({
                'experiment': learning.experiment.name[:50] if learning.experiment else 'Unknown',
                'key_insight': learning.key_insight[:200] if learning.key_insight else '',
                'what_worked': learning.what_worked[:100] if learning.what_worked else '',
                'what_failed': learning.what_failed[:100] if learning.what_failed else '',
                'created_at': learning.created_at.isoformat()
            })
    except Exception as e:
        logger.warning(f"[Session 914.7] Error getting learnings: {e}")

    # BLOCKED: Initiatives stuck at same stage for >3 days
    blocked = []
    three_days_ago = timezone.now() - timedelta(days=3)
    stuck_initiatives = Initiative.objects.filter(
        current_stage__lte=5,
        updated_at__lt=three_days_ago
    ).exclude(
        status='ARCHIVED'
    ).order_by('updated_at')[:10]

    for init in stuck_initiatives:
        days_stuck = (timezone.now() - init.updated_at).days if init.updated_at else 0
        blocked.append({
            'id': str(init.id),
            'name': init.name[:60],
            'stage': init.current_stage,
            'days_stuck': days_stuck,
            'blocked_reason': init.progression_blocked_reason or 'Unknown'
        })

    # KILL CANDIDATES: Low-priority initiatives with no progress in 14+ days
    kill_candidates = []
    two_weeks_ago = timezone.now() - timedelta(days=14)
    stale_initiatives = Initiative.objects.filter(
        updated_at__lt=two_weeks_ago,
        current_stage__lte=2,  # Still in early stages
        is_daily_focus=False
    ).exclude(
        status='ARCHIVED'
    ).order_by('updated_at')[:10]

    for init in stale_initiatives:
        days_stale = (timezone.now() - init.updated_at).days if init.updated_at else 0
        kill_candidates.append({
            'id': str(init.id),
            'name': init.name[:60],
            'stage': init.current_stage,
            'days_stale': days_stale,
            'reason': f'No progress in {days_stale} days, still at Stage {init.current_stage}'
        })

    # NEEDS DECISION: Initiatives awaiting founder input
    needs_decision = []
    pending_intent = Initiative.objects.filter(
        founder_intent_set=False,
        current_stage__gte=1,
        current_stage__lte=5
    ).exclude(
        status='ARCHIVED'
    ).order_by('-updated_at')[:10]

    for init in pending_intent:
        needs_decision.append({
            'id': str(init.id),
            'name': init.name[:60],
            'stage': init.current_stage,
            'waiting_for': 'Founder intent (speed, risk tolerance, stop rule)'
        })

    pending_boardroom = Initiative.objects.filter(
        requires_boardroom_approval=True,
        boardroom_approved=False,
        current_stage__lte=5
    ).exclude(
        status='ARCHIVED'
    ).order_by('-updated_at')[:10]

    for init in pending_boardroom:
        needs_decision.append({
            'id': str(init.id),
            'name': init.name[:60],
            'stage': init.current_stage,
            'waiting_for': 'Boardroom approval'
        })

    report = {
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'generated_at': timezone.now().isoformat(),
        'summary': {
            'shipped_count': len(shipped),
            'deliverables_created': deliverables_created,
            'learned_count': len(learned),
            'blocked_count': len(blocked),
            'kill_candidates_count': len(kill_candidates),
            'needs_decision_count': len(needs_decision)
        },
        'shipped': shipped,
        'learned': learned,
        'blocked': blocked,
        'kill_candidates': kill_candidates,
        'needs_decision': needs_decision
    }

    logger.info(
        f"[Session 914.7] Weekly report generated: "
        f"shipped={len(shipped)}, learned={len(learned)}, "
        f"blocked={len(blocked)}, kill={len(kill_candidates)}"
    )

    return report


def submit_weekly_feedback(
    feedback: str,
    week_of: date = None,
    submitted_by: str = 'founder'
) -> Dict[str, Any]:
    """
    Submit weekly feedback that becomes a training signal.

    Args:
        feedback: One paragraph of feedback
        week_of: Which week this feedback is for (default: current week)
        submitted_by: Who is submitting (default: 'founder')

    Returns:
        Dict with submission result
    """
    from core.models_unified_system import FounderFeedback
    from core.models_pilot_readiness import ExperimentLearning

    if week_of is None:
        week_of = date.today()

    if not feedback or len(feedback.strip()) < 10:
        return {'success': False, 'error': 'Feedback too short (min 10 chars)'}

    # Store feedback
    try:
        feedback_record = FounderFeedback.objects.create(
            feedback_type='weekly_feedback',
            content={
                'feedback': feedback,
                'week_of': week_of.isoformat(),
                'submitted_by': submitted_by,
                'submitted_at': timezone.now().isoformat()
            },
            created_by=submitted_by
        )

        # Convert to learning signal
        # This creates an ExperimentLearning that agents can learn from
        try:
            ExperimentLearning.objects.create(
                learning_type='founder_feedback',
                key_insight=f"Founder weekly feedback ({week_of.isoformat()}): {feedback[:500]}",
                what_worked='',
                what_failed='',
                source_agent='FounderFeedback',
                confidence_score=Decimal('0.95'),  # High confidence - founder feedback
                is_active=True
            )
        except Exception as e:
            logger.warning(f"[Session 914.7] Failed to create learning from feedback: {e}")

        logger.info(
            f"[Session 914.7] Weekly feedback submitted by {submitted_by}: "
            f"{feedback[:100]}..."
        )

        return {
            'success': True,
            'feedback_id': str(feedback_record.id),
            'week_of': week_of.isoformat(),
            'feedback_length': len(feedback),
            'learning_created': True
        }

    except Exception as e:
        logger.error(f"[Session 914.7] Failed to submit weekly feedback: {e}")
        return {'success': False, 'error': str(e)}


def get_rhythm_status() -> Dict[str, Any]:
    """
    Get the current operating rhythm status.

    Returns:
        Dict with daily priorities status and weekly report summary
    """
    daily = get_daily_priorities()

    # Check when last weekly feedback was submitted
    last_feedback = None
    try:
        from core.models_unified_system import FounderFeedback
        recent = FounderFeedback.objects.filter(
            feedback_type='weekly_feedback'
        ).order_by('-created_at').first()
        if recent:
            last_feedback = recent.created_at.isoformat()
    except Exception as e:
        logger.warning(f"FounderFeedback lookup failed: {e}")

    # Quick summary of initiative status
    from core.models_document_registry import Initiative

    total_active = Initiative.objects.filter(current_stage__lte=5).count()
    with_intent = Initiative.objects.filter(
        current_stage__lte=5,
        founder_intent_set=True
    ).count()
    in_focus = Initiative.objects.filter(is_daily_focus=True).count()

    return {
        'daily_priorities': daily,
        'last_weekly_feedback': last_feedback,
        'initiative_summary': {
            'total_active': total_active,
            'with_intent': with_intent,
            'in_daily_focus': in_focus,
            'awaiting_priority_mapping': total_active - in_focus
        },
        'recommendations': _get_rhythm_recommendations(daily, last_feedback, total_active)
    }


def _get_rhythm_recommendations(
    daily: Dict,
    last_feedback: Optional[str],
    total_active: int
) -> List[str]:
    """Generate recommendations for maintaining rhythm."""
    recommendations = []

    # Check daily priorities
    if daily.get('needs_update'):
        recommendations.append("Set today's Top 3 priorities")

    if not daily.get('priorities'):
        recommendations.append("No daily priorities set - agents have no focus direction")

    # Check weekly feedback
    if last_feedback:
        try:
            last_dt = datetime.fromisoformat(last_feedback.replace('Z', '+00:00'))
            days_since = (timezone.now() - last_dt).days
            if days_since > 7:
                recommendations.append(
                    f"Weekly feedback overdue ({days_since} days since last submission)"
                )
        except Exception as e:
            logger.warning(f"Feedback date parsing failed: {e}")
    else:
        recommendations.append("No weekly feedback submitted yet - start the feedback loop")

    # Check initiative focus
    if total_active > 10 and not daily.get('priorities'):
        recommendations.append(
            f"{total_active} active initiatives need priority direction"
        )

    return recommendations

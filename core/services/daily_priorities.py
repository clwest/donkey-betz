"""
Daily Priorities Service
=========================

Session 914.5: Daily Priority Scan for Initiative Pipeline

Problem: With 180+ initiatives, the system treated all equally. No way to focus
resources on the most important ones.

Solution: Daily priority scan identifies top 5 initiatives to focus on:
1. Run daily scan (morning) to compute priority scores
2. Mark top 5 as "daily focus" initiatives
3. Auto-progression prioritizes daily focus initiatives
4. Dashboard shows daily focus clearly

Usage:
    from core.services.daily_priorities import (
        run_daily_priority_scan,
        get_daily_focus_initiatives,
        set_manual_priority
    )

    # Run the daily scan
    result = run_daily_priority_scan()
    print(f"Top 5: {[i['name'] for i in result['focus_initiatives']]}")

    # Get current focus initiatives
    focus = get_daily_focus_initiatives()

    # Manual priority override
    set_manual_priority(initiative_id, priority_rank=1)
"""

import logging
from datetime import date, timedelta
from typing import Dict, Any, List, Optional

from django.utils import timezone
from django.core.cache import cache
from django.db.models import F, Case, When, Value, IntegerField

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_FOCUS_COUNT = 5
CACHE_KEY_DAILY_FOCUS = "daily_focus_initiatives"
CACHE_KEY_SCAN_DATE = "daily_priority_scan_date"
CACHE_TTL = 86400  # 24 hours


def compute_initiative_priority(initiative) -> Dict[str, Any]:
    """
    Compute comprehensive priority score for an initiative.

    Factors:
    - Base priority_score (impact, urgency, confidence, revenue)
    - Stage progress (earlier stages = more urgent to unblock)
    - Time since last activity (stale = lower priority)
    - Founder intent speed setting
    - Execution track (institutional = higher priority)
    """
    base_score = initiative.priority_score

    # Stage factor: earlier stages get slight boost (need to unblock pipeline)
    stage_factor = 1.0
    if initiative.current_stage == 1:
        stage_factor = 1.1  # 10% boost for Stage 1
    elif initiative.current_stage == 2:
        stage_factor = 1.05  # 5% boost for Stage 2

    # Freshness factor: initiatives with recent activity get boost
    freshness_factor = 1.0
    if initiative.updated_at:
        days_since_update = (timezone.now() - initiative.updated_at).days
        if days_since_update <= 1:
            freshness_factor = 1.1  # Active today
        elif days_since_update <= 3:
            freshness_factor = 1.05  # Active this week
        elif days_since_update > 14:
            freshness_factor = 0.9  # Stale - lower priority

    # Speed factor: fast track initiatives get boost
    speed_factor = 1.0
    if hasattr(initiative, 'execution_speed'):
        if initiative.execution_speed == 'fast':
            speed_factor = 1.1
        elif initiative.execution_speed == 'thorough':
            speed_factor = 0.95  # Slightly lower - can wait

    # Track factor: institutional track is usually more important
    track_factor = 1.0
    if hasattr(initiative, 'execution_track'):
        if initiative.execution_track == 'institutional':
            track_factor = 1.05

    # Founder intent set = ready to go = boost
    intent_factor = 1.1 if initiative.founder_intent_set else 0.9

    # Compute final score
    final_score = (
        base_score *
        stage_factor *
        freshness_factor *
        speed_factor *
        track_factor *
        intent_factor
    )

    return {
        'initiative_id': str(initiative.id),
        'name': initiative.name,
        'base_score': base_score,
        'final_score': min(1.0, final_score),  # Cap at 1.0
        'current_stage': initiative.current_stage,
        'priority_level': initiative.priority_level,
        'factors': {
            'stage': stage_factor,
            'freshness': freshness_factor,
            'speed': speed_factor,
            'track': track_factor,
            'intent': intent_factor
        }
    }


def run_daily_priority_scan(focus_count: int = DEFAULT_FOCUS_COUNT) -> Dict[str, Any]:
    """
    Run the daily priority scan to identify top focus initiatives.

    Args:
        focus_count: Number of initiatives to mark as focus (default 5)

    Returns:
        Dict with focus initiatives and scan metadata
    """
    from core.models_document_registry import Initiative

    logger.info(f"[Session 914.5] Running daily priority scan...")

    # Get active initiatives (not archived, not completed)
    active_initiatives = Initiative.objects.filter(
        current_stage__lte=5
    ).exclude(
        status='ARCHIVED'
    ).select_related()

    # Compute priority for each
    scored = []
    for init in active_initiatives:
        try:
            priority_data = compute_initiative_priority(init)
            scored.append(priority_data)
        except Exception as e:
            logger.warning(f"[Session 914.5] Error scoring {init.id}: {e}")

    # Sort by final score descending
    scored.sort(key=lambda x: x['final_score'], reverse=True)

    # Take top N
    focus_initiatives = scored[:focus_count]

    # Cache the focus list
    focus_ids = [i['initiative_id'] for i in focus_initiatives]
    cache.set(CACHE_KEY_DAILY_FOCUS, focus_ids, CACHE_TTL)
    cache.set(CACHE_KEY_SCAN_DATE, date.today().isoformat(), CACHE_TTL)

    # Update initiatives with daily_focus flag
    Initiative.objects.filter(id__in=focus_ids).update(
        is_daily_focus=True,
        daily_focus_date=date.today()
    )

    # Clear old focus flags
    Initiative.objects.exclude(id__in=focus_ids).update(
        is_daily_focus=False
    )

    result = {
        'success': True,
        'scan_date': date.today().isoformat(),
        'total_scanned': len(scored),
        'focus_count': len(focus_initiatives),
        'focus_initiatives': focus_initiatives,
        'focus_ids': focus_ids
    }

    logger.info(
        f"[Session 914.5] Daily scan complete: {len(focus_initiatives)} focus initiatives "
        f"from {len(scored)} total"
    )

    return result


def get_daily_focus_initiatives() -> List[Dict[str, Any]]:
    """
    Get the current daily focus initiatives.

    Returns:
        List of focus initiative dicts with priority info
    """
    from core.models_document_registry import Initiative

    # Check cache first
    focus_ids = cache.get(CACHE_KEY_DAILY_FOCUS)
    scan_date = cache.get(CACHE_KEY_SCAN_DATE)

    # If no cache or stale, run fresh scan
    if not focus_ids or scan_date != date.today().isoformat():
        result = run_daily_priority_scan()
        return result['focus_initiatives']

    # Get initiatives from cache
    initiatives = Initiative.objects.filter(id__in=focus_ids)

    focus_list = []
    for init in initiatives:
        priority_data = compute_initiative_priority(init)
        focus_list.append(priority_data)

    # Re-sort to maintain order
    focus_list.sort(key=lambda x: x['final_score'], reverse=True)

    return focus_list


def is_daily_focus(initiative_id: str) -> bool:
    """Check if an initiative is in today's daily focus."""
    focus_ids = cache.get(CACHE_KEY_DAILY_FOCUS, [])
    return str(initiative_id) in focus_ids


def set_manual_priority(
    initiative_id: str,
    priority_rank: int = 1,
    reason: str = ""
) -> Dict[str, Any]:
    """
    Manually set an initiative as high priority (override automatic ranking).

    Args:
        initiative_id: UUID of the initiative
        priority_rank: Rank 1-5 in daily focus
        reason: Reason for manual override

    Returns:
        Dict with update result
    """
    from core.models_document_registry import Initiative

    try:
        initiative = Initiative.objects.get(id=initiative_id)
    except Initiative.DoesNotExist:
        return {'success': False, 'error': 'Initiative not found'}

    # Set manual priority
    initiative.is_daily_focus = True
    initiative.daily_focus_date = date.today()
    initiative.manual_priority_rank = priority_rank
    initiative.manual_priority_reason = reason
    initiative.save(update_fields=[
        'is_daily_focus', 'daily_focus_date',
        'manual_priority_rank', 'manual_priority_reason'
    ])

    # Update cache
    focus_ids = cache.get(CACHE_KEY_DAILY_FOCUS, [])
    if str(initiative_id) not in focus_ids:
        focus_ids.insert(0, str(initiative_id))
        # Keep only top 5
        focus_ids = focus_ids[:DEFAULT_FOCUS_COUNT]
        cache.set(CACHE_KEY_DAILY_FOCUS, focus_ids, CACHE_TTL)

    logger.info(
        f"[Session 914.5] Manual priority set for {initiative.name[:40]}: "
        f"rank={priority_rank}, reason={reason[:50]}"
    )

    return {
        'success': True,
        'initiative_id': str(initiative_id),
        'initiative_name': initiative.name,
        'priority_rank': priority_rank,
        'reason': reason
    }


def get_priority_summary() -> Dict[str, Any]:
    """
    Get a summary of the current priority state.

    Returns:
        Dict with counts by priority level and focus status
    """
    from core.models_document_registry import Initiative

    total = Initiative.objects.filter(current_stage__lte=5).count()

    # Count by priority level
    critical = Initiative.objects.filter(
        current_stage__lte=5,
        impact_score__gte=0.8
    ).count()

    high = Initiative.objects.filter(
        current_stage__lte=5,
        impact_score__gte=0.6,
        impact_score__lt=0.8
    ).count()

    # Focus count
    focus = Initiative.objects.filter(
        is_daily_focus=True,
        daily_focus_date=date.today()
    ).count()

    # Initiatives ready for progression
    ready = Initiative.objects.filter(
        current_stage__lte=5,
        founder_intent_set=True
    ).count()

    return {
        'total_active': total,
        'critical_priority': critical,
        'high_priority': high,
        'daily_focus': focus,
        'ready_for_progression': ready,
        'scan_date': cache.get(CACHE_KEY_SCAN_DATE),
    }

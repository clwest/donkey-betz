"""
Initiative Circuit Breaker
==========================

Session 884: Prevents initiative creation when the system is overloaded.

When initiatives pile up faster than they can be processed, this circuit breaker
pauses creation until the backlog clears.

Configuration:
    Environment variables:
        INITIATIVE_CREATION_PAUSED=true  - Pause all new initiative creation
        INITIATIVE_BACKLOG_THRESHOLD=50  - Max pending initiatives before auto-pause

    Database:
        SystemConfiguration with key='initiative_creation_paused' and value=True

Usage:
    from core.services.initiative_circuit_breaker import can_create_initiative, get_backlog_status

    if can_create_initiative():
        # Create initiative
    else:
        logger.warning("Initiative creation paused - backlog too high")
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Cache TTL for backlog check (avoid hitting DB on every call)
_backlog_cache = {
    'count': 0,
    'checked_at': None,
}
CACHE_TTL_SECONDS = 60  # Re-check backlog every 60 seconds


def is_creation_paused_by_env() -> bool:
    """Check if creation is paused via environment variable."""
    paused = os.environ.get('INITIATIVE_CREATION_PAUSED', '').lower()
    return paused in ('true', '1', 'yes')


def is_creation_paused_by_db() -> bool:
    """Check if creation is paused via database setting."""
    try:
        from core.models import SystemConfiguration
        setting = SystemConfiguration.objects.filter(key='initiative_creation_paused').first()
        if setting and setting.value:
            # value is JSONField - can be True/False or string
            if isinstance(setting.value, bool):
                return setting.value
            if isinstance(setting.value, str):
                return setting.value.lower() in ('true', '1', 'yes')
            return bool(setting.value)
    except Exception as e:
        logger.warning(f"Initiative circuit breaker check failed: {e}")
    return False


def get_backlog_threshold() -> int:
    """Get the max allowed pending initiatives before auto-pause."""
    try:
        threshold = int(os.environ.get('INITIATIVE_BACKLOG_THRESHOLD', '20'))
        return max(10, threshold)  # Minimum 10
    except (ValueError, TypeError):
        return 50


def get_pending_initiative_count() -> int:
    """Get count of ACTIVE initiatives with no meaningful activity."""
    global _backlog_cache

    now = datetime.now()

    # Use cached value if fresh enough
    if _backlog_cache['checked_at']:
        age = (now - _backlog_cache['checked_at']).total_seconds()
        if age < CACHE_TTL_SECONDS:
            return _backlog_cache['count']

    try:
        from core.models_document_registry import Initiative

        # Count ALL ACTIVE or TRIAGE initiatives (not just those with no activity)
        # Previously only counted last_activity_at IS NULL, which let the backlog
        # grow unbounded since auto-generated initiatives get immediate activity
        count = Initiative.objects.filter(
            status__in=['ACTIVE', 'TRIAGE'],
        ).count()

        _backlog_cache['count'] = count
        _backlog_cache['checked_at'] = now
        return count

    except Exception as e:
        logger.warning(f"[circuit_breaker] Error checking backlog: {e}")
        return 0


def get_stage1_no_work_count() -> int:
    """Legacy metric: count stage-1 ACTIVE initiatives with no stage work."""
    try:
        from core.models_document_registry import Initiative

        count = 0
        for initiative in Initiative.objects.filter(status='ACTIVE', current_stage=1):
            if initiative.stages_with_work == 0:
                count += 1
        return count
    except Exception as e:
        logger.warning(f"[circuit_breaker] Error checking stage1 count: {e}")
        return 0


def is_backlog_too_high() -> bool:
    """Check if the backlog exceeds threshold."""
    threshold = get_backlog_threshold()
    pending = get_pending_initiative_count()
    return pending >= threshold


def get_daily_creation_limit() -> int:
    """Session 1059: Max initiatives created per 24h rolling window.
    Lowered from 15 to 8 to reduce noise from auto-created initiatives."""
    try:
        return int(os.environ.get('INITIATIVE_DAILY_LIMIT', '8'))
    except (ValueError, TypeError):
        return 8


def is_daily_limit_reached() -> bool:
    """
    Session 1059: Check if the 24h rolling creation cap has been reached.

    Initiatives complete in 0.7-3h, so the backlog threshold alone doesn't
    prevent spam — fast-completing initiatives keep the count low while the
    system churns through dozens per day.
    """
    try:
        from core.models_document_registry import Initiative
        from django.utils import timezone as tz
        from datetime import timedelta

        limit = get_daily_creation_limit()
        cutoff = tz.now() - timedelta(hours=24)
        created_24h = Initiative.objects.filter(created_at__gte=cutoff).count()
        return created_24h >= limit
    except Exception as e:
        logger.warning(f"[circuit_breaker] Daily limit check failed: {e}")
        return False


def can_create_initiative(bypass_check: bool = False) -> bool:
    """
    Main check: Can we create a new initiative?

    Args:
        bypass_check: If True, skip checks (for admin/manual overrides)

    Returns:
        True if creation is allowed, False if paused
    """
    if bypass_check:
        return True

    # Check explicit pause flags
    if is_creation_paused_by_env():
        logger.debug("[circuit_breaker] Initiative creation paused by environment variable")
        return False

    if is_creation_paused_by_db():
        logger.debug("[circuit_breaker] Initiative creation paused by database setting")
        return False

    # Check backlog threshold
    if is_backlog_too_high():
        pending = get_pending_initiative_count()
        threshold = get_backlog_threshold()
        logger.warning(
            f"[circuit_breaker] Initiative creation auto-paused: "
            f"{pending} pending >= {threshold} threshold"
        )
        return False

    # Session 1059: Daily creation cap — prevents churn even when initiatives complete fast
    if is_daily_limit_reached():
        limit = get_daily_creation_limit()
        logger.warning(
            f"[circuit_breaker] Daily initiative limit reached: "
            f"{limit} created in last 24h"
        )
        return False

    return True


def get_backlog_status() -> Dict[str, Any]:
    """Get full status of the circuit breaker."""
    pending = get_pending_initiative_count()
    threshold = get_backlog_threshold()
    daily_limit = get_daily_creation_limit()

    return {
        'can_create': can_create_initiative(),
        'pending_count': pending,
        'never_active_count': pending,  # last_activity_at IS NULL
        'stage1_no_work_count': get_stage1_no_work_count(),  # legacy metric
        'threshold': threshold,
        'utilization_pct': int((pending / threshold) * 100) if threshold > 0 else 0,
        'paused_by_env': is_creation_paused_by_env(),
        'paused_by_db': is_creation_paused_by_db(),
        'paused_by_backlog': is_backlog_too_high(),
        'daily_limit': daily_limit,
        'paused_by_daily_limit': is_daily_limit_reached(),
    }


def find_similar_initiative(name: str, threshold: float = 0.6) -> Optional[Any]:
    """
    Check if a similar ACTIVE initiative already exists.

    Uses Jaccard keyword similarity (same algorithm as consolidate_duplicate_initiatives).
    Returns the matching initiative if found, None otherwise.
    """
    try:
        from core.models_document_registry import Initiative
        from core.management.commands.consolidate_duplicate_initiatives import (
            extract_keywords,
            calculate_similarity,
        )

        new_keywords = extract_keywords(name)
        if not new_keywords:
            return None

        # Session 1059: Check ACTIVE/TRIAGE at any stage AND recently COMPLETED.
        # Previously only checked stages 1-2, so fast-completing initiatives (0.7-3h)
        # escaped dedup and near-duplicates piled up.
        from django.utils import timezone as tz
        from datetime import timedelta
        candidates_qs = Initiative.objects.filter(
            status__in=['ACTIVE', 'TRIAGE'],
        ).values_list('id', 'name')
        completed_recent_qs = Initiative.objects.filter(
            status='COMPLETED',
            updated_at__gte=tz.now() - timedelta(hours=48),
        ).values_list('id', 'name')
        candidates = list(candidates_qs[:200]) + list(completed_recent_qs[:200])

        best_match = None
        best_score = 0.0

        for init_id, init_name in candidates:
            score = calculate_similarity(name, init_name)
            if score >= threshold and score > best_score:
                best_score = score
                best_match = init_id

        if best_match:
            match = Initiative.objects.get(id=best_match)
            logger.info(
                f"[circuit_breaker] Dedup match: '{name[:50]}' ~ '{match.name[:50]}' "
                f"(score={best_score:.2f})"
            )
            return match

    except Exception as e:
        logger.warning(f"[circuit_breaker] Dedup check failed: {e}")

    return None


def can_promote_to_active(initiative) -> bool:
    """
    Session 1016: Quality gate for TRIAGE-to-ACTIVE promotion.

    An initiative must have:
    1. owner_agent (required)
    2. At least one of: next_action, signal_cluster/source_decision_id, or
       substantive parent_topic

    Returns True if initiative qualifies for ACTIVE status.
    """
    # Must have an owner — no orphan ACTIVE initiatives
    if not getattr(initiative, 'owner_agent', None):
        logger.debug(
            f"[quality_gate] Blocked ACTIVE promotion for '{initiative.name[:50]}': "
            f"no owner_agent"
        )
        return False

    # Need at least one evidence indicator beyond owner
    checks_passed = 0

    # Has a concrete next action
    if getattr(initiative, 'next_action', None):
        checks_passed += 1

    # Has evidence link (signal cluster or source decision)
    if getattr(initiative, 'signal_cluster_id', None) or getattr(initiative, 'source_decision_id', None):
        checks_passed += 1

    # Has substantive parent_topic (not just empty or trivial)
    parent_topic = getattr(initiative, 'parent_topic', '') or ''
    if len(parent_topic.strip()) > 20:
        checks_passed += 1

    # Has deliverable indicators in description
    description = getattr(initiative, 'description', '') or ''
    deliverable_keywords = ['deliverable', 'output', 'produce', 'create', 'build', 'implement', 'publish']
    if any(kw in description.lower() for kw in deliverable_keywords):
        checks_passed += 1

    if checks_passed < 1:
        logger.debug(
            f"[quality_gate] Blocked ACTIVE promotion for '{initiative.name[:50]}': "
            f"owner present but no evidence (next_action/signal_cluster/parent_topic)"
        )
        return False

    return True


def clear_cache():
    """Clear the backlog cache (for testing)."""
    global _backlog_cache
    _backlog_cache = {'count': 0, 'checked_at': None}


# API endpoint helper
def pause_initiative_creation(reason: str = "Manual pause"):
    """Pause initiative creation via database setting."""
    try:
        from core.models import SystemConfiguration
        setting, created = SystemConfiguration.objects.get_or_create(
            key='initiative_creation_paused',
            defaults={
                'value': True,  # JSONField stores native Python types
                'description': reason,
                'category': 'system',
            }
        )
        if not created:
            setting.value = True
            setting.description = reason
            setting.save()
        clear_cache()
        logger.info(f"[circuit_breaker] Initiative creation PAUSED: {reason}")
        return True
    except Exception as e:
        logger.error(f"[circuit_breaker] Failed to pause: {e}")
        return False


def resume_initiative_creation():
    """Resume initiative creation via database setting."""
    try:
        from core.models import SystemConfiguration
        SystemConfiguration.objects.filter(key='initiative_creation_paused').delete()
        clear_cache()
        logger.info("[circuit_breaker] Initiative creation RESUMED")
        return True
    except Exception as e:
        logger.error(f"[circuit_breaker] Failed to resume: {e}")
        return False

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
from functools import lru_cache
from datetime import datetime, timedelta

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
        threshold = int(os.environ.get('INITIATIVE_BACKLOG_THRESHOLD', '100'))
        return max(10, threshold)  # Minimum 10
    except (ValueError, TypeError):
        return 100


def get_pending_initiative_count() -> int:
    """Get count of initiatives at 0% completion (never started)."""
    global _backlog_cache

    now = datetime.now()

    # Use cached value if fresh enough
    if _backlog_cache['checked_at']:
        age = (now - _backlog_cache['checked_at']).total_seconds()
        if age < CACHE_TTL_SECONDS:
            return _backlog_cache['count']

    # Query DB
    try:
        from core.models_document_registry import Initiative

        # Count initiatives that are ACTIVE but have no stage work
        count = 0
        for initiative in Initiative.objects.filter(status='ACTIVE', current_stage=1):
            if initiative.stages_with_work == 0:
                count += 1

        _backlog_cache['count'] = count
        _backlog_cache['checked_at'] = now
        return count

    except Exception as e:
        logger.warning(f"[circuit_breaker] Error checking backlog: {e}")
        return 0


def is_backlog_too_high() -> bool:
    """Check if the backlog exceeds threshold."""
    threshold = get_backlog_threshold()
    pending = get_pending_initiative_count()
    return pending >= threshold


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

    return True


def get_backlog_status() -> Dict[str, Any]:
    """Get full status of the circuit breaker."""
    pending = get_pending_initiative_count()
    threshold = get_backlog_threshold()

    return {
        'can_create': can_create_initiative(),
        'pending_count': pending,
        'threshold': threshold,
        'utilization_pct': int((pending / threshold) * 100) if threshold > 0 else 0,
        'paused_by_env': is_creation_paused_by_env(),
        'paused_by_db': is_creation_paused_by_db(),
        'paused_by_backlog': is_backlog_too_high(),
    }


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

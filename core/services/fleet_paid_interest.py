"""Paid-interest trigger-state service (Session 1138).

Encapsulates Decision 13's trigger-state evaluation so the PA tool
and any admin surface see the same answer. Trigger fires per Decision
13 when **any** of:

1. ``last_90d_signals >= COUNT_THRESHOLD`` (default 5)
2. ``has_high_value_signal`` — at least one row with
   ``willing_pay >= app_pro_price`` (default $49 for signal-studio)
3. Jessica manual override — recorded out-of-band via a settings flag
   or a `metadata.manual_override=True` row.

Per-app Pro tier price + count threshold are configurable so the
mechanism generalizes when SellerPilot / ComplianceSentinel hook into
the same pattern.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from django.utils import timezone

logger = logging.getLogger(__name__)


# Default thresholds per Decision 13. Per-app overrides live in
# `APP_TRIGGER_CONFIG`; new apps register themselves there.
DEFAULT_COUNT_THRESHOLD = 5
DEFAULT_ROLLING_WINDOW_DAYS = 90
DEFAULT_PRO_PRICE = 49

# Per-app trigger config — Decision 13 calls out signal-studio first;
# other apps will register their numbers here when they hit the same
# demand-gate. Keep small + explicit, no settings-mining magic.
APP_TRIGGER_CONFIG: dict[str, dict[str, int]] = {
    "signal-studio": {
        "count_threshold": 5,
        "rolling_window_days": 90,
        "pro_price": 49,
    },
}


# Trigger state values — match the PA tool / spec exactly.
STATE_NOT_YET = "not_yet"
STATE_READY = "ready"
STATE_MANUALLY_OVERRIDDEN = "manually_overridden"


@dataclass
class TriggerState:
    """Snapshot of an app's paid-interest demand-gate state."""

    app_slug: str
    total_signals: int
    last_90d_signals: int
    has_high_value_signal: bool
    high_value_threshold: int
    trigger_state: str
    rolling_window_days: int
    count_threshold: int
    last_signal_at: Optional[str]  # ISO-8601 or None

    def to_dict(self) -> dict:
        return {
            "app_slug": self.app_slug,
            "total_signals": self.total_signals,
            "last_90d_signals": self.last_90d_signals,
            "has_high_value_signal": self.has_high_value_signal,
            "high_value_threshold_usd": self.high_value_threshold,
            "trigger_state": self.trigger_state,
            "rolling_window_days": self.rolling_window_days,
            "count_threshold": self.count_threshold,
            "last_signal_at": self.last_signal_at,
        }


def get_app_config(app_slug: str) -> dict[str, int]:
    """Return (count_threshold, rolling_window_days, pro_price) for app_slug."""
    cfg = APP_TRIGGER_CONFIG.get(app_slug)
    if cfg is None:
        return {
            "count_threshold": DEFAULT_COUNT_THRESHOLD,
            "rolling_window_days": DEFAULT_ROLLING_WINDOW_DAYS,
            "pro_price": DEFAULT_PRO_PRICE,
        }
    return cfg


def evaluate_trigger_state(
    app_slug: str,
    *,
    manual_override: bool = False,
) -> TriggerState:
    """Compute the trigger state for ``app_slug`` from current DB rows.

    Args:
        app_slug: The fleet app whose state we're evaluating.
        manual_override: When True, force ``STATE_MANUALLY_OVERRIDDEN``
            regardless of signal counts. Caller passes True when Jessica
            has explicitly unlocked the gate (e.g. via a settings flag
            or a manual API call). MLC scope: no DB-side override row
            yet; the caller decides.

    Returns:
        TriggerState dataclass — call ``.to_dict()`` for JSON output.
    """
    # Lazy import to dodge circular at module load.
    from core.models.fleet import FleetPaidInterest

    cfg = get_app_config(app_slug)
    count_threshold = cfg["count_threshold"]
    rolling_window_days = cfg["rolling_window_days"]
    pro_price = cfg["pro_price"]

    qs = FleetPaidInterest.objects.filter(app_slug=app_slug)
    total_signals = qs.count()

    cutoff = timezone.now() - timedelta(days=rolling_window_days)
    last_90d_signals = qs.filter(created_at__gte=cutoff).count()

    has_high_value_signal = qs.filter(willing_pay__gte=pro_price).exists()

    most_recent = qs.order_by("-created_at").only("created_at").first()
    last_signal_at = most_recent.created_at.isoformat() if most_recent else None

    if manual_override:
        state = STATE_MANUALLY_OVERRIDDEN
    elif last_90d_signals >= count_threshold or has_high_value_signal:
        state = STATE_READY
    else:
        state = STATE_NOT_YET

    return TriggerState(
        app_slug=app_slug,
        total_signals=total_signals,
        last_90d_signals=last_90d_signals,
        has_high_value_signal=has_high_value_signal,
        high_value_threshold=pro_price,
        trigger_state=state,
        rolling_window_days=rolling_window_days,
        count_threshold=count_threshold,
        last_signal_at=last_signal_at,
    )


__all__ = [
    "TriggerState",
    "APP_TRIGGER_CONFIG",
    "DEFAULT_COUNT_THRESHOLD",
    "DEFAULT_ROLLING_WINDOW_DAYS",
    "DEFAULT_PRO_PRICE",
    "STATE_NOT_YET",
    "STATE_READY",
    "STATE_MANUALLY_OVERRIDDEN",
    "evaluate_trigger_state",
    "get_app_config",
]

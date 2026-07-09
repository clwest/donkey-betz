"""
Cost Threshold Monitor — Session 2735, Cost Protection Campaign P1.

Reads ``CostTracking.estimated_cost_usd`` sums over rolling windows and
returns a structured breach snapshot. **No side effects.** Callers own
dispatch (HAI, log emit, governance flip).

Cat A discipline:
- Uses the pre-existing ``CostTracking`` model
  (``core/models_unified_system.py:6665``) which already stores
  provider, service, tokens, ``estimated_cost_usd``, and timestamp.
- Uses the pre-existing ``SystemConfiguration`` pattern (matches
  Session 2734/2735 §6/§14/§15 threshold conventions).
- No new schema. No new writer. No new aggregation query — the sums
  reuse the same ``Sum('estimated_cost_usd')`` shape that
  ``views_analytics.py:2119+`` already runs for reporting.

Topology evidence (7-day audit at Session 2735 P1 open):
- ``CostTracking`` sees ~54.5x more rows than ``LLMCallEvent`` today
  (3,215 vs 59 rows over 7d). CostTracking is the canonical cost
  substrate; LLMCallEvent covers only wrapper-instrumented paths
  (~1.8% of calls).
- Writer coverage: ``core/llm_enforcer.py:731`` +
  ``core/views_analytics.py:1894`` (via ``AdvancedAnalyticsService
  .track_cost``, called from ``core/agents/base_agent.py:2926`` and
  other paths).
- Duplicate-risk audit: no ``request_id`` collisions across rows;
  the 24% signature-dup that shows up is dominated by init-test
  calls (``op='test'``, 768 identical rows over 7d for ~$0.17
  total). Aggregating with ``Sum`` is safe.

Windows:
- ``hour``: last 60 minutes.
- ``day``: last 24 hours (rolling, not calendar day).
- ``month``: last 30 days (rolling).

Config keys (all read from ``SystemConfiguration``, all optional):
- ``cost_threshold_hour_usd``
- ``cost_threshold_day_usd``
- ``cost_threshold_month_usd``
- ``cost_protection_enforce_mode`` — ``monitor`` (default) or
  ``freeze``. This module DOES NOT act on the mode; callers do.

Missing / unparseable thresholds skip that window's check. A window
with no threshold configured returns ``breached=False`` regardless of
spend so that a shipping-with-no-config state is a no-op.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.db.models import Sum, Count
from django.utils import timezone

logger = logging.getLogger(__name__)


_WINDOW_MINUTES = {
    'hour': 60,
    'day': 60 * 24,
    'month': 60 * 24 * 30,
}


_CONFIG_KEY_BY_WINDOW = {
    'hour': 'cost_threshold_hour_usd',
    'day': 'cost_threshold_day_usd',
    'month': 'cost_threshold_month_usd',
}


@dataclass(frozen=True)
class CostBreachResult:
    """Immutable snapshot for a single window."""

    window: str  # 'hour' | 'day' | 'month'
    window_minutes: int
    window_start: datetime
    window_end: datetime
    threshold_usd: Optional[Decimal]  # None = not configured / unparseable
    actual_usd: Decimal
    breached: bool
    row_count: int
    top_service: str = ''
    top_service_usd: Decimal = field(default_factory=lambda: Decimal('0'))
    top_provider: str = ''
    idempotency_key: str = ''


def _read_threshold(window: str) -> Optional[Decimal]:
    """Read the configured threshold for a window; None on any error."""
    key = _CONFIG_KEY_BY_WINDOW.get(window)
    if not key:
        return None
    try:
        from core.models.system import SystemConfiguration
        raw = SystemConfiguration.objects.filter(
            key=key, is_active=True,
        ).values_list('value', flat=True).first()
        if raw is None or str(raw).strip() == '':
            return None
        return Decimal(str(raw).strip())
    except (InvalidOperation, ValueError) as e:
        logger.warning(
            '[COST_MONITOR] threshold parse failed key=%s (%s: %s); '
            'skipping window',
            key, type(e).__name__, e,
        )
        return None
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[COST_MONITOR] threshold read failed key=%s (%s: %s); '
            'skipping window',
            key, type(e).__name__, e,
        )
        return None


def compute_window(window: str, *, now: Optional[datetime] = None) -> CostBreachResult:
    """Return a ``CostBreachResult`` for the given window.

    Reads the configured threshold; sums ``estimated_cost_usd`` and
    counts rows over the window; picks the top-spend service so the
    HAI payload has something actionable.
    """
    from core.models_unified_system import CostTracking

    if window not in _WINDOW_MINUTES:
        raise ValueError(f'unknown window {window!r}')

    now = now or timezone.now()
    minutes = _WINDOW_MINUTES[window]
    window_start = now - timedelta(minutes=minutes)

    qs = CostTracking.objects.filter(
        timestamp__gte=window_start,
        timestamp__lte=now,
    )

    row_count = qs.count()
    actual = qs.aggregate(total=Sum('estimated_cost_usd'))['total']
    actual_usd = Decimal(str(actual)) if actual is not None else Decimal('0')

    threshold = _read_threshold(window)
    breached = (
        threshold is not None
        and actual_usd > threshold
    )

    top_service = ''
    top_service_usd = Decimal('0')
    top_provider = ''
    if row_count > 0:
        # Pick the (provider, service) pair with the largest spend so the
        # HAI payload has a concrete "this is where the money went" hook.
        top = (
            qs.values('provider', 'service')
            .annotate(spend=Sum('estimated_cost_usd'), n=Count('id'))
            .order_by('-spend')
            .first()
        )
        if top:
            top_service = str(top.get('service') or '')
            top_provider = str(top.get('provider') or '')
            top_service_usd = Decimal(str(top.get('spend') or 0))

    idempotency_key = (
        f'cost_breach:{window}:{int(window_start.timestamp())}'
    )

    return CostBreachResult(
        window=window,
        window_minutes=minutes,
        window_start=window_start,
        window_end=now,
        threshold_usd=threshold,
        actual_usd=actual_usd,
        breached=breached,
        row_count=row_count,
        top_service=top_service,
        top_service_usd=top_service_usd,
        top_provider=top_provider,
        idempotency_key=idempotency_key,
    )


def check_all_windows(now: Optional[datetime] = None) -> list[CostBreachResult]:
    """Compute all three windows; return in ('hour', 'day', 'month') order."""
    return [
        compute_window(window, now=now)
        for window in ('hour', 'day', 'month')
    ]


def read_enforce_mode() -> str:
    """Return 'monitor' (default) or 'freeze' per SystemConfiguration.

    Callers use this to decide whether to call
    ``governance_tool.set_mode('freeze')`` on a breach. This module
    NEVER flips governance — even at ``mode='freeze'``, callers must
    explicitly dispatch. That keeps the invariant Chris required for
    the enforcement gate: no code path enables freeze without
    explicit approval-time verification.
    """
    try:
        from core.models.system import SystemConfiguration
        raw = SystemConfiguration.objects.filter(
            key='cost_protection_enforce_mode', is_active=True,
        ).values_list('value', flat=True).first()
        if raw is None:
            return 'monitor'
        mode = str(raw).strip().lower()
        if mode in ('monitor', 'freeze'):
            return mode
        logger.warning(
            '[COST_MONITOR] unknown cost_protection_enforce_mode=%r; '
            'defaulting to monitor',
            raw,
        )
        return 'monitor'
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[COST_MONITOR] read_enforce_mode failed (%s: %s); '
            'defaulting to monitor',
            type(e).__name__, e,
        )
        return 'monitor'

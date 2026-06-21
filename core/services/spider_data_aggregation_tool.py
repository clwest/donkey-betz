"""
Session 1189 Item 3: SpiderData aggregation PA tool (v1).

Background: Session 1187 Utilization Recon (deliverable 88952c54-...)
established that AGENT_SPIDER_MAPPINGS was routing dispatches against
SpiderData via category names, but until Session 1188's supply recon
(deliverable 13032820-...) there was no PA tool to verify what categories
actually had supply. Rigby's supply recon ran via one-off Django shell
scripts twice across two sessions — recurring tooling gap.

This module exposes a single `aggregate` action that group-bys
SpiderData rows by `data_type` (with optional spider_name and
data_types filters) over a windowed time range, returning counts +
top contributors. v1 deliberately omits per-row samples, source
domain breakdowns, text search, and date-bucket histograms — that's
v2 scope.

Rigby's v1 spec was ratified by Chris in conversation
pa-9dd0d784c41a4e4d on 2026-06-21.

Usage (via PA tool dispatcher):
    result = await dispatcher.execute(
        tool_name="spider_data_aggregation_tool",
        payload={
            "action": "aggregate",
            "days_back": 30,
            "actionable_only": True,
            "include_top_spiders": True,
            "top_spiders_limit": 5,
        },
        user_id=user.id,
    )
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


# v1 bounds — matched by the OpenAI function-calling schema. Centralized
# so the schema, handler, and tests all agree without drift.
DAYS_BACK_DEFAULT = 30
DAYS_BACK_MIN = 1
DAYS_BACK_MAX = 90

TOP_SPIDERS_LIMIT_DEFAULT = 5
TOP_SPIDERS_LIMIT_MIN = 1
TOP_SPIDERS_LIMIT_MAX = 25


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _coerce_str_list(raw: Any) -> Optional[List[str]]:
    """Tolerate JSON nulls, empty lists, and accidental scalars."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return [raw] if raw else None
    if isinstance(raw, (list, tuple)):
        items = [str(x) for x in raw if isinstance(x, (str, int)) and str(x)]
        return items or None
    return None


def aggregate_spider_data(
    days_back: int = DAYS_BACK_DEFAULT,
    actionable_only: bool = True,
    data_types: Optional[List[str]] = None,
    spider_names: Optional[List[str]] = None,
    include_top_spiders: bool = True,
    top_spiders_limit: int = TOP_SPIDERS_LIMIT_DEFAULT,
    include_totals: bool = True,
) -> Dict[str, Any]:
    """Return the v1 aggregation payload per Rigby's ratified spec.

    Pure function — no permission check, no telemetry side effects. The
    PA tool handler is the boundary that calls this and records the
    tool dispatch. Keeping it pure makes it cheap to unit-test against
    real DB fixtures.
    """
    from core.models_unified_system import SpiderData

    days_back = _clamp(int(days_back), DAYS_BACK_MIN, DAYS_BACK_MAX)
    top_spiders_limit = _clamp(
        int(top_spiders_limit), TOP_SPIDERS_LIMIT_MIN, TOP_SPIDERS_LIMIT_MAX
    )
    end_ts = timezone.now()
    start_ts = end_ts - timedelta(days=days_back)

    base_filter = Q(created_at__gte=start_ts)
    if data_types:
        base_filter &= Q(data_type__in=data_types)
    if spider_names:
        base_filter &= Q(spider_name__in=spider_names)

    actionable_filter = base_filter & Q(is_actionable=True)

    # Per-data_type breakdown. We include both actionable_count and
    # total_count because callers (Rigby, AC verifiers) need both —
    # cheap join in a single query saves a round trip.
    by_data_type_qs = (
        SpiderData.objects.filter(base_filter)
        .values('data_type')
        .annotate(
            total_count=Count('id'),
            actionable_count=Count('id', filter=Q(is_actionable=True)),
            distinct_spiders=Count('spider_name', distinct=True),
        )
        .order_by('-actionable_count' if actionable_only else '-total_count', 'data_type')
    )

    by_data_type: List[Dict[str, Any]] = []
    for row in by_data_type_qs:
        # `actionable_only=True` is the dominant caller — skip empty buckets
        # so the response stays readable.
        if actionable_only and not row['actionable_count']:
            continue
        bucket: Dict[str, Any] = {
            'data_type': row['data_type'],
            'actionable_count': row['actionable_count'],
            'total_count': row['total_count'],
            'distinct_spiders': row['distinct_spiders'],
        }
        if include_top_spiders:
            top_qs = (
                SpiderData.objects.filter(
                    base_filter & Q(data_type=row['data_type'])
                )
                .values('spider_name')
                .annotate(
                    total_count=Count('id'),
                    actionable_count=Count('id', filter=Q(is_actionable=True)),
                )
                .order_by(
                    '-actionable_count' if actionable_only else '-total_count',
                    'spider_name',
                )[:top_spiders_limit]
            )
            bucket['top_spiders'] = [
                {
                    'spider_name': t['spider_name'],
                    'actionable_count': t['actionable_count'],
                    'total_count': t['total_count'],
                }
                for t in top_qs
            ]
        by_data_type.append(bucket)

    payload: Dict[str, Any] = {
        'window': {
            'days_back': days_back,
            'start_ts': start_ts.isoformat(),
            'end_ts': end_ts.isoformat(),
        },
        'filters': {
            'actionable_only': bool(actionable_only),
            'data_types': data_types,
            'spider_names': spider_names,
        },
        'by_data_type': by_data_type,
        'generated_at': timezone.now().isoformat(),
    }

    if include_totals:
        total_count = SpiderData.objects.filter(base_filter).count()
        actionable_count = SpiderData.objects.filter(actionable_filter).count()
        distinct_data_types = (
            SpiderData.objects.filter(base_filter)
            .values('data_type').distinct().count()
        )
        distinct_spiders = (
            SpiderData.objects.filter(base_filter)
            .values('spider_name').distinct().count()
        )
        payload['totals'] = {
            'actionable_count': actionable_count,
            'total_count': total_count,
            'distinct_data_types': distinct_data_types,
            'distinct_spiders': distinct_spiders,
        }

    return payload


def handle_spider_data_aggregation(
    tool_name: str,
    payload: Dict[str, Any],
    user_id: Optional[int] = None,
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Tool-dispatcher entry point. Validates `action`, normalizes
    payload, and calls `aggregate_spider_data`. Returns a structured
    error dict (not an exception) for unknown actions so the dispatcher
    can surface it cleanly to the PA / agent caller."""
    action = (payload or {}).get('action', 'aggregate')
    if action != 'aggregate':
        return {
            'ok': False,
            'error': f"Unknown action '{action}' (v1 supports only 'aggregate').",
        }
    try:
        result = aggregate_spider_data(
            days_back=int(payload.get('days_back', DAYS_BACK_DEFAULT)),
            actionable_only=bool(payload.get('actionable_only', True)),
            data_types=_coerce_str_list(payload.get('data_types')),
            spider_names=_coerce_str_list(payload.get('spider_names')),
            include_top_spiders=bool(payload.get('include_top_spiders', True)),
            top_spiders_limit=int(
                payload.get('top_spiders_limit', TOP_SPIDERS_LIMIT_DEFAULT)
            ),
            include_totals=bool(payload.get('include_totals', True)),
        )
        return {'ok': True, 'action': 'aggregate', **result}
    except Exception as exc:
        logger.exception(
            f"[spider_data_aggregation_tool] failure trace_id={trace_id} "
            f"({type(exc).__name__}: {exc})"
        )
        return {
            'ok': False,
            'error': f"{type(exc).__name__}: {exc}",
        }

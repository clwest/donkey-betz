"""
Session 2971: Signal Intelligence UI backend endpoints.

Thin HTTP wrappers over existing service functions. Reuses:
  - `spider_data_aggregation_tool.aggregate_spider_data` (rollups)
  - `spider_feed.query_spider_feed` / `get_spider_feed_detail` (feed browse)
  - `spider_semantic_search.get_embedding_stats` (coverage widget)

Endpoints (all require authentication):
  GET /api/signals/aggregate         — data-type rollups (24h/7d/30d)
  GET /api/signals/feed              — paginated LegacySpiderData browse
  GET /api/signals/feed/<uuid>/      — full row detail (drawer)
  GET /api/signals/embedding-coverage — backfill coverage snapshot

The Signal Cluster surface stays on the existing REST ViewSet at
`GET /api/v1/signal-clusters/` (this session extends its filter set,
not its URL — see core/views_audit_api.py).

Spec deliverable: `ade9339f-c41f-48a5-9ce8-fa8beee696cc` §3-4.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

logger = logging.getLogger(__name__)


DEFAULT_DATA_TYPES = ['news', 'financial', 'tech', 'ai_ml']


def _parse_bool(raw: Any, default: bool = False) -> bool:
    if raw is None or raw == '':
        return default
    if isinstance(raw, bool):
        return raw
    return str(raw).strip().lower() in ('1', 'true', 'yes', 'on')


def _parse_int(raw: Any, default: Optional[int] = None) -> Optional[int]:
    if raw is None or raw == '':
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _parse_list(raw: Any) -> Optional[List[str]]:
    """Accept either repeated params (?x=a&x=b), a comma-separated string,
    or a JSON list-shaped scalar. Returns None for empty input."""
    if raw is None:
        return None
    if isinstance(raw, list):
        items = [str(x).strip() for x in raw if str(x).strip()]
        return items or None
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        return parts or None
    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signals_aggregate(request: Request) -> Response:
    """Data-type rollups over the last N days.

    Query params:
      days_back (int, default 7, clamped by service)
      actionable_only (bool, default true)
      data_types (list, comma-separated or repeated; default = 4 primary feeds)
      spider_names (list, optional)
      include_top_spiders (bool, default true)
      include_totals (bool, default true)
    """
    from core.services.spider_data_aggregation_tool import aggregate_spider_data

    days_back = _parse_int(request.query_params.get('days_back'), 7) or 7
    actionable_only = _parse_bool(request.query_params.get('actionable_only'), True)
    include_top_spiders = _parse_bool(request.query_params.get('include_top_spiders'), True)
    include_totals = _parse_bool(request.query_params.get('include_totals'), True)

    # `getlist` handles repeated params (?data_types=news&data_types=tech);
    # fall back to comma-split when a single param arrives.
    raw_data_types = request.query_params.getlist('data_types')
    if not raw_data_types:
        raw_data_types = request.query_params.get('data_types')
    data_types = _parse_list(raw_data_types)
    if data_types is None:
        data_types = list(DEFAULT_DATA_TYPES)

    raw_spider_names = request.query_params.getlist('spider_names')
    if not raw_spider_names:
        raw_spider_names = request.query_params.get('spider_names')
    spider_names = _parse_list(raw_spider_names)

    payload = aggregate_spider_data(
        days_back=days_back,
        actionable_only=actionable_only,
        data_types=data_types,
        spider_names=spider_names,
        include_top_spiders=include_top_spiders,
        include_totals=include_totals,
    )
    return Response(payload)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signals_feed(request: Request) -> Response:
    """Paginated LegacySpiderData browse.

    Query params match `spider_feed.query_spider_feed`.
    """
    from core.services.spider_feed import query_spider_feed

    raw_data_types = request.query_params.getlist('data_types')
    if not raw_data_types:
        raw_data_types = request.query_params.get('data_types')
    data_types = _parse_list(raw_data_types)

    payload = query_spider_feed(
        query=request.query_params.get('query', '') or '',
        data_types=data_types,
        spider_name=request.query_params.get('spider_name', '') or '',
        actionable_only=_parse_bool(request.query_params.get('actionable_only'), False),
        embedding_status=(request.query_params.get('embedding_status', 'all') or 'all'),
        window_hours=_parse_int(request.query_params.get('window_hours')),
        limit=_parse_int(request.query_params.get('limit'), 30) or 30,
        offset=_parse_int(request.query_params.get('offset'), 0) or 0,
    )
    return Response(payload)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signals_feed_detail(request: Request, row_id: str) -> Response:
    """Full row detail for the Feed Explorer drawer."""
    from core.services.spider_feed import get_spider_feed_detail

    payload = get_spider_feed_detail(str(row_id))
    if payload is None:
        return Response({'error': 'not_found', 'id': str(row_id)}, status=404)
    return Response(payload)


SUPPORTED_BREAKDOWN_WINDOWS = frozenset({24, 168, 720})  # 1d / 7d / 30d


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def signals_embedding_coverage(request: Request) -> Response:
    """Embedding coverage snapshot for the Dashboard Coverage widget.

    Wraps `SpiderSemanticSearch.get_embedding_stats()` — same numbers the
    backfill task drains against.

    Query params (S2973):
      include_breakdown (bool, default false) — include NO_ITEMS breakdown
      window (int hours, default 24, clamped to {24,168,720}) — breakdown window
    """
    from core.services.spider_semantic_search import get_spider_semantic_search

    include_breakdown = _parse_bool(request.query_params.get('include_breakdown'), False)
    window = _parse_int(request.query_params.get('window'), 24) or 24
    if window not in SUPPORTED_BREAKDOWN_WINDOWS:
        window = 24

    try:
        stats = get_spider_semantic_search().get_embedding_stats(
            include_breakdown=include_breakdown,
            breakdown_window_hours=window,
        )
    except Exception as e:
        logger.exception("[signals_embedding_coverage] stats fetch failed: %s", e)
        return Response(
            {'error': 'stats_unavailable', 'detail': str(e)},
            status=503,
        )
    return Response(stats)

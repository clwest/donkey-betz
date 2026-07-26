"""
Session 2971: SpiderData feed browse helper (v1).

Pure query function powering the Signal Intelligence UI Feed Explorer
(spec deliverable `ade9339f-c41f-48a5-9ce8-fa8beee696cc` §3.2). Kept
separate from the PA tool handler layer (`td_handlers_ops._handle_spider_status`)
so both a REST endpoint and future tool-surface callers share one
query implementation without response-shaping divergence.

The helper queries `LegacySpiderData` — the plane the backfill
(`spider_semantic_search.py`), aggregator (`spider_data_aggregation_tool.py`),
and status tool all target. Field names match spec §5.1
(`spider_name`, `data_type`, `source_url`, `embedding_text`,
`raw_data`, `processed_data`, `is_actionable`).

Return shape is Rigby-ratified (T1 SIGN 2026-07-26):
    {items: [...], total: int, offset: int, limit: int, has_more: bool}
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.db.models import Q
from django.utils import timezone


LIMIT_DEFAULT = 30
LIMIT_MAX = 200
WINDOW_HOURS_MAX = 24 * 30  # 30 days


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def _embedding_status(text: Optional[str]) -> str:
    """Bucket a row's embedding_text into 3 states matching backfill semantics.

    S2975: both the actionable `[NO_ITEMS]` sentinel AND the historical
    `[NO_ITEMS_STALE_EMPTY_RAW]` variant bucket as `marked_empty` so the
    feed UI never treats a stale ghost row as `present`.
    """
    from core.services.no_items_policy import BACKFILL_SKIP_SENTINELS

    if text is None:
        return 'missing'
    if text in BACKFILL_SKIP_SENTINELS:
        return 'marked_empty'
    if text.strip():
        return 'present'
    return 'empty'


def query_spider_feed(
    query: str = '',
    data_types: Optional[List[str]] = None,
    spider_name: str = '',
    actionable_only: bool = False,
    embedding_status: str = 'all',
    window_hours: Optional[int] = None,
    limit: int = LIMIT_DEFAULT,
    offset: int = 0,
) -> Dict[str, Any]:
    """Return a windowed slice of LegacySpiderData rows matching filters.

    Args:
        query: substring match against embedding_text OR source_url.
        data_types: list of data_type values (case-insensitive, applied via __in).
        spider_name: substring match against spider_name.
        actionable_only: restrict to is_actionable=True rows.
        embedding_status: one of 'all' / 'present' / 'missing' / 'marked_empty'.
            'missing' = no embedding_text stored (never processed).
            'marked_empty' = processed and marked '[NO_ITEMS]' by the backfill.
            'present' = has real embedding_text content.
        window_hours: restrict to created_at >= now - hours. None or <= 0 disables.
        limit: page size (clamped to [1, 200]).
        offset: page offset (>= 0).

    Returns:
        Dict with keys: items (list), total (int), offset (int), limit (int),
        has_more (bool).
    """
    from core.models_unified_system import LegacySpiderData

    limit = _clamp(int(limit or LIMIT_DEFAULT), 1, LIMIT_MAX)
    offset = max(int(offset or 0), 0)

    qs = LegacySpiderData.objects.all()

    if window_hours and int(window_hours) > 0:
        cutoff = timezone.now() - timedelta(
            hours=_clamp(int(window_hours), 1, WINDOW_HOURS_MAX)
        )
        qs = qs.filter(created_at__gte=cutoff)

    if data_types:
        # Case-insensitive match by iexact-ish (data_type is a CharField and
        # values are already lowercase in practice; still normalize).
        normalized = [str(d).strip() for d in data_types if str(d).strip()]
        if normalized:
            qs = qs.filter(data_type__in=normalized)

    if spider_name:
        qs = qs.filter(spider_name__icontains=spider_name.strip())

    if actionable_only:
        qs = qs.filter(is_actionable=True)

    if query:
        q = query.strip()
        qs = qs.filter(Q(embedding_text__icontains=q) | Q(source_url__icontains=q))

    # Embedding-status buckets align with `spider_semantic_search.get_embedding_stats`.
    # S2975: use BACKFILL_SKIP_SENTINELS so stale ghost rows bucket the same
    # way real [NO_ITEMS] does — else they'd leak into 'present' results.
    from core.services.no_items_policy import BACKFILL_SKIP_SENTINELS

    if embedding_status == 'present':
        qs = qs.exclude(
            Q(embedding_text__isnull=True)
            | Q(embedding_text='')
            | Q(embedding_text__in=BACKFILL_SKIP_SENTINELS)
        )
    elif embedding_status == 'missing':
        qs = qs.filter(Q(embedding_text__isnull=True) | Q(embedding_text=''))
    elif embedding_status == 'marked_empty':
        qs = qs.filter(embedding_text__in=BACKFILL_SKIP_SENTINELS)
    # 'all' or unknown = no filter

    total = qs.count()
    rows = list(
        qs.only(
            'id', 'spider_name', 'data_type', 'source_url',
            'embedding_text', 'raw_data', 'processed_data',
            'is_actionable', 'created_at',
        )
        .order_by('-created_at')[offset:offset + limit]
    )

    items: List[Dict[str, Any]] = []
    for r in rows:
        et = r.embedding_text
        preview = (et or '').strip()
        if not preview:
            rd = r.raw_data
            if isinstance(rd, dict):
                for key in ('title', 'name'):
                    val = rd.get(key)
                    if isinstance(val, str) and val.strip():
                        preview = val.strip()
                        break
        items.append({
            'id': str(r.id),
            'spider_name': r.spider_name,
            'data_type': r.data_type,
            'source_url': r.source_url,
            'is_actionable': bool(r.is_actionable),
            'embedding_status': _embedding_status(et),
            'embedding_text': (et or '')[:500] if et else '',
            'preview': preview[:300],
            'created_at': r.created_at.isoformat() if r.created_at else None,
        })

    return {
        'items': items,
        'total': total,
        'offset': offset,
        'limit': limit,
        'has_more': offset + len(items) < total,
    }


def get_spider_feed_detail(row_id: str) -> Optional[Dict[str, Any]]:
    """Return full row detail for the Feed Explorer drawer.

    Includes raw_data + processed_data JSON (not truncated) so the UI
    can render its own collapsers. Returns None if the row is missing.
    """
    from core.models_unified_system import LegacySpiderData

    row = LegacySpiderData.objects.filter(id=row_id).first()
    if not row:
        return None
    return {
        'id': str(row.id),
        'spider_name': row.spider_name,
        'data_type': row.data_type,
        'source_url': row.source_url,
        'is_actionable': bool(row.is_actionable),
        'embedding_status': _embedding_status(row.embedding_text),
        'embedding_text': row.embedding_text or '',
        'raw_data': row.raw_data,
        'processed_data': row.processed_data,
        'created_at': row.created_at.isoformat() if row.created_at else None,
    }

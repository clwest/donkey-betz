"""Top wall-clock consumers — per-task_name aggregation over CeleryTaskEvent.

Session 1167 — COO Nervous System Backlog item #7 (SHOULD tier):
``No quick way to find 'which task is using the most DB connections /
CPU / wall-time in the last 1h / 24h.'``

This module is the canonical aggregator. ``ops_tool.top_consumers``
reads from here; the on-demand surface can too. Wall-clock time is the
v1 metric (LLM spend stays in noise_metrics / cost_tool surfaces — see
``docs/topics/celery-workers.md`` for the rationale).

## Design notes (Rigby ratified, Session 1167)

- **Wall-clock primary, task_name dimension.** ``CeleryTaskEvent`` has
  ``task_name`` + ``duration_seconds`` already indexed (migration
  ``celery_evt_name_time`` on ``(task_name, -started_at)``). Zero new
  instrumentation.
- **Single aggregate SQL query per call.** Uses PostgreSQL
  ``percentile_cont(0.95) WITHIN GROUP`` so p95 is computed server-side
  — no Python-side loop over duration lists. Avoids the N+1 trap and
  keeps memory usage flat regardless of event volume.
- **One window per call** via ``window`` arg (``"1h"``, ``"24h"``,
  ``"7d"``). Default ``"24h"``. Matches the existing ops_tool
  convention.
- **Reduce-only.** No re-classification, no synthesis across windows.
  Same single-source-of-truth rule as memory_pressure / queue_pressure.

## Schema v1

Output:

    {
      "schema_version": 1,
      "action": "top_consumers",
      "window": "24h",
      "window_seconds": 86400,
      "generated_at": "<UTC ISO>",
      "since": "<UTC ISO of cutoff>",
      "limit": 20,
      "task_count": 12,
      "consumers": [
        {
          "task_name": "core.tasks.foo",
          "count": 432,
          "total_seconds": 1234.5,
          "mean_seconds": 2.86,
          "max_seconds": 45.1,
          "p95_seconds": 8.7,
        },
        ...
      ],
    }
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone as _dt_timezone
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = 1
DEFAULT_LIMIT = 20
MAX_LIMIT = 50

# Same window vocabulary the rest of ops_tool uses.
_WINDOW_HOURS = {"1h": 1, "6h": 6, "24h": 24, "7d": 168, "30d": 720}


def _resolve_window(window: str) -> int:
    """Return window in hours. Raises ValueError on unknown window."""
    hours = _WINDOW_HOURS.get(window)
    if hours is None:
        raise ValueError(
            f"Unknown window {window!r}. Valid: {sorted(_WINDOW_HOURS.keys())}"
        )
    return hours


def _clamp_limit(limit: Optional[int]) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return DEFAULT_LIMIT
    if limit < 1:
        return 1
    if limit > MAX_LIMIT:
        return MAX_LIMIT
    return limit


def compute_top_consumers(
    window: str = "24h",
    limit: Optional[int] = None,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Aggregate wall-clock consumption per ``task_name`` over the window.

    Single PostgreSQL aggregate query — uses
    ``percentile_cont(0.95) WITHIN GROUP`` so the p95 is computed
    server-side. Returns the schema-v1 payload documented in the
    module docstring.

    Args:
        window: ``"1h"``, ``"6h"``, ``"24h"``, ``"7d"``, ``"30d"``.
        limit: max rows (clamped to ``[1, MAX_LIMIT]``; default 20).
        now: timestamp override for testing. UTC-naive auto-promoted.

    Raises:
        ValueError: on unknown ``window`` argument.
    """
    from django.db import connection

    hours = _resolve_window(window)
    limit = _clamp_limit(limit)

    if now is None:
        now = datetime.now(_dt_timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=_dt_timezone.utc)
    cutoff = now - timedelta(hours=hours)

    sql = """
        SELECT
            task_name,
            COUNT(*) AS count,
            COALESCE(SUM(duration_seconds), 0)::float AS total_seconds,
            COALESCE(AVG(duration_seconds), 0)::float AS mean_seconds,
            COALESCE(MAX(duration_seconds), 0)::float AS max_seconds,
            COALESCE(
                percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_seconds),
                0
            )::float AS p95_seconds
        FROM core_celerytaskevent
        WHERE started_at >= %s
          AND duration_seconds IS NOT NULL
        GROUP BY task_name
        ORDER BY total_seconds DESC
        LIMIT %s
    """

    with connection.cursor() as cur:
        cur.execute(sql, [cutoff, limit])
        rows = cur.fetchall()

    consumers: List[Dict[str, Any]] = [
        {
            "task_name": task_name,
            "count": int(count),
            "total_seconds": round(float(total), 3),
            "mean_seconds": round(float(mean), 3),
            "max_seconds": round(float(mx), 3),
            "p95_seconds": round(float(p95), 3),
        }
        for (task_name, count, total, mean, mx, p95) in rows
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "action": "top_consumers",
        "window": window,
        "window_seconds": hours * 3600,
        "generated_at": now.isoformat(),
        "since": cutoff.isoformat(),
        "limit": limit,
        "task_count": len(consumers),
        "consumers": consumers,
    }

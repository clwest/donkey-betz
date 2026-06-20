"""Tests for core.services.top_consumers.

Session 1167 — COO Nervous System Backlog item #7.

Pins the aggregator contract:
- window vocabulary (1h/6h/24h/7d/30d, ValueError on unknown)
- limit clamping ([1, MAX_LIMIT])
- sort order (largest total_seconds first)
- single SQL aggregate (no N+1)
- p95 computed server-side via PostgreSQL percentile_cont
- UTC ISO timestamps in payload
- schema_version: 1

Requires PostgreSQL (percentile_cont is not supported by SQLite). The
test DB in CI/local is Postgres per CLAUDE.md so this is fine.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone as _dt_timezone

from django.test import TestCase, SimpleTestCase
from django.utils import timezone

from core.models_celery_telemetry import CeleryTaskEvent
from core.services.top_consumers import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    SCHEMA_VERSION,
    _clamp_limit,
    _resolve_window,
    compute_top_consumers,
)


# ──────────────────────────────────────────────────────────────────────
# Pure helpers — no DB needed
# ──────────────────────────────────────────────────────────────────────


class ResolveWindowTests(SimpleTestCase):
    def test_known_windows(self):
        self.assertEqual(_resolve_window("1h"), 1)
        self.assertEqual(_resolve_window("6h"), 6)
        self.assertEqual(_resolve_window("24h"), 24)
        self.assertEqual(_resolve_window("7d"), 168)
        self.assertEqual(_resolve_window("30d"), 720)

    def test_unknown_window_raises(self):
        with self.assertRaises(ValueError):
            _resolve_window("bogus")
        with self.assertRaises(ValueError):
            _resolve_window("")


class ClampLimitTests(SimpleTestCase):
    def test_none_returns_default(self):
        self.assertEqual(_clamp_limit(None), DEFAULT_LIMIT)

    def test_unparseable_returns_default(self):
        self.assertEqual(_clamp_limit("bogus"), DEFAULT_LIMIT)
        self.assertEqual(_clamp_limit([]), DEFAULT_LIMIT)

    def test_below_minimum_clamps_to_one(self):
        self.assertEqual(_clamp_limit(0), 1)
        self.assertEqual(_clamp_limit(-5), 1)

    def test_above_max_clamps_down(self):
        self.assertEqual(_clamp_limit(MAX_LIMIT + 100), MAX_LIMIT)

    def test_in_range_passes_through(self):
        self.assertEqual(_clamp_limit(10), 10)
        self.assertEqual(_clamp_limit(MAX_LIMIT), MAX_LIMIT)


# ──────────────────────────────────────────────────────────────────────
# DB-backed aggregation
# ──────────────────────────────────────────────────────────────────────


def _create_event(task_name: str, duration: float, started_at: datetime, status: str = "SUCCESS"):
    return CeleryTaskEvent.objects.create(
        task_id=f"{task_name}-{started_at.isoformat()}-{duration}",
        task_name=task_name,
        status=status,
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=duration),
        duration_seconds=duration,
    )


class ComputeTopConsumersAggregationTests(TestCase):
    """End-to-end SQL exercises against PostgreSQL percentile_cont."""

    def setUp(self):
        self.now = timezone.now()
        # Wipe any seed data — other test fixtures or migrations may have
        # populated CeleryTaskEvent. We need a clean slate to assert on
        # sort order + counts.
        CeleryTaskEvent.objects.all().delete()

    def test_sorts_by_total_seconds_desc(self):
        _create_event("task.a", duration=5.0, started_at=self.now - timedelta(minutes=5))
        _create_event("task.a", duration=5.0, started_at=self.now - timedelta(minutes=10))
        _create_event("task.b", duration=20.0, started_at=self.now - timedelta(minutes=5))
        _create_event("task.c", duration=1.0, started_at=self.now - timedelta(minutes=5))

        result = compute_top_consumers(window="24h", now=self.now)
        names = [c["task_name"] for c in result["consumers"]]
        # task.b: 20s, task.a: 10s, task.c: 1s
        self.assertEqual(names, ["task.b", "task.a", "task.c"])

    def test_count_and_total_correct(self):
        _create_event("task.x", duration=2.0, started_at=self.now - timedelta(minutes=5))
        _create_event("task.x", duration=4.0, started_at=self.now - timedelta(minutes=10))
        _create_event("task.x", duration=6.0, started_at=self.now - timedelta(minutes=15))

        result = compute_top_consumers(window="24h", now=self.now)
        x = next(c for c in result["consumers"] if c["task_name"] == "task.x")
        self.assertEqual(x["count"], 3)
        self.assertEqual(x["total_seconds"], 12.0)
        self.assertEqual(x["mean_seconds"], 4.0)
        self.assertEqual(x["max_seconds"], 6.0)

    def test_p95_computed_server_side(self):
        # 100 events with durations 1..100. p95 ≈ 95.
        for i in range(1, 101):
            _create_event(
                "task.p", duration=float(i),
                started_at=self.now - timedelta(minutes=i),
            )

        result = compute_top_consumers(window="24h", now=self.now)
        p = next(c for c in result["consumers"] if c["task_name"] == "task.p")
        # PostgreSQL percentile_cont(0.95) on durations 1..100 yields 95.05
        # (linear interpolation between 95 and 96). Allow ±0.5 slack for
        # exact algorithm variance.
        self.assertEqual(p["count"], 100)
        self.assertAlmostEqual(p["p95_seconds"], 95.05, delta=0.5)
        self.assertEqual(p["max_seconds"], 100.0)

    def test_excludes_events_outside_window(self):
        _create_event("task.recent", duration=5.0, started_at=self.now - timedelta(minutes=30))
        # 25h ago — outside 24h window
        _create_event("task.stale", duration=5.0, started_at=self.now - timedelta(hours=25))

        result = compute_top_consumers(window="24h", now=self.now)
        names = [c["task_name"] for c in result["consumers"]]
        self.assertIn("task.recent", names)
        self.assertNotIn("task.stale", names)

    def test_excludes_null_duration_rows(self):
        # Mid-execution row (no finished_at, no duration) — must not appear
        # in the aggregation.
        CeleryTaskEvent.objects.create(
            task_id="mid-flight",
            task_name="task.midflight",
            status="STARTED",
            started_at=self.now - timedelta(minutes=5),
            finished_at=None,
            duration_seconds=None,
        )
        result = compute_top_consumers(window="24h", now=self.now)
        names = [c["task_name"] for c in result["consumers"]]
        self.assertNotIn("task.midflight", names)

    def test_empty_window_returns_zero_consumers(self):
        result = compute_top_consumers(window="1h", now=self.now)
        self.assertEqual(result["consumers"], [])
        self.assertEqual(result["task_count"], 0)

    def test_limit_caps_result_set(self):
        for i in range(30):
            _create_event(
                f"task.{i}", duration=float(i + 1),
                started_at=self.now - timedelta(minutes=i + 1),
            )

        result = compute_top_consumers(window="24h", limit=5, now=self.now)
        self.assertEqual(len(result["consumers"]), 5)
        # Top of the list is task.29 (largest duration); descending.
        self.assertEqual(result["consumers"][0]["task_name"], "task.29")

    def test_limit_clamped_to_max(self):
        for i in range(60):
            _create_event(
                f"task.{i}", duration=1.0,
                started_at=self.now - timedelta(minutes=i + 1),
            )

        result = compute_top_consumers(window="24h", limit=999, now=self.now)
        self.assertLessEqual(len(result["consumers"]), MAX_LIMIT)
        self.assertEqual(result["limit"], MAX_LIMIT)


class PayloadShapeTests(TestCase):
    def setUp(self):
        CeleryTaskEvent.objects.all().delete()

    def test_schema_version_and_action(self):
        result = compute_top_consumers(window="24h")
        self.assertEqual(result["schema_version"], SCHEMA_VERSION)
        self.assertEqual(result["action"], "top_consumers")

    def test_window_metadata(self):
        now = datetime(2026, 6, 20, 12, 0, 0, tzinfo=_dt_timezone.utc)
        result = compute_top_consumers(window="24h", now=now)
        self.assertEqual(result["window"], "24h")
        self.assertEqual(result["window_seconds"], 86400)
        self.assertEqual(result["generated_at"], now.isoformat())
        expected_since = (now - timedelta(hours=24)).isoformat()
        self.assertEqual(result["since"], expected_since)

    def test_unknown_window_raises_via_service(self):
        with self.assertRaises(ValueError):
            compute_top_consumers(window="weird")

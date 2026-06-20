"""Tests for core.services.memory_telemetry.

Session 1167 — COO Nervous System Backlog item #5.

Pins the sampler contract so future refactors don't silently break:
- cmdline cap parsing (both --flag=N and --flag N forms; missing flag)
- pool.processes fallback ([pid] when None)
- pct_of_cap computation (cap-aware vs cap-absent rows)
- sustained-pressure CRIT detection (N=3 consecutive adjacent samples)
- adjacency window enforcement (stale prior → first-sample semantics)
- per-worker status + overall_status worst-of
- downshift recommendation with concurrency floor=1
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone as _dt_timezone
from typing import Optional
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from core.services.memory_telemetry import (
    CADENCE_SECONDS,
    CONSECUTIVE_REQUIRED,
    PRESSURE_THRESHOLD,
    SCHEMA_VERSION,
    _compute_status,
    _is_previous_adjacent,
    build_snapshot,
    derive_pool_kind,
    parse_max_memory_per_child_kb,
    resolve_leaf_pids,
)


# ──────────────────────────────────────────────────────────────────────
# Pure parsers
# ──────────────────────────────────────────────────────────────────────


class ParseMaxMemoryPerChildTests(SimpleTestCase):
    def test_equals_form(self):
        cmdline = ["celery", "-A", "core", "worker", "--max-memory-per-child=200000"]
        self.assertEqual(parse_max_memory_per_child_kb(cmdline), 200000)

    def test_space_separated_form(self):
        cmdline = ["celery", "-A", "core", "worker", "--max-memory-per-child", "150000"]
        self.assertEqual(parse_max_memory_per_child_kb(cmdline), 150000)

    def test_flag_absent_returns_none(self):
        cmdline = ["celery", "-A", "core", "worker", "--loglevel=info"]
        self.assertIsNone(parse_max_memory_per_child_kb(cmdline))

    def test_empty_cmdline_returns_none(self):
        self.assertIsNone(parse_max_memory_per_child_kb([]))

    def test_unparseable_value_returns_none(self):
        cmdline = ["celery", "--max-memory-per-child=abc"]
        # The regex requires digits, so this matches nothing.
        self.assertIsNone(parse_max_memory_per_child_kb(cmdline))


class ResolveLeafPidsTests(SimpleTestCase):
    def test_prefork_uses_pool_processes(self):
        self.assertEqual(resolve_leaf_pids(100, [101, 102, 103]), [101, 102, 103])

    def test_threads_falls_back_to_parent(self):
        self.assertEqual(resolve_leaf_pids(100, None), [100])

    def test_empty_pool_processes_falls_back_to_parent(self):
        self.assertEqual(resolve_leaf_pids(100, []), [100])


class DerivePoolKindTests(SimpleTestCase):
    def test_threads_when_none(self):
        self.assertEqual(derive_pool_kind(None, 100), "threads_or_solo")

    def test_prefork_when_distinct_children(self):
        self.assertEqual(derive_pool_kind([101, 102], 100), "prefork")

    def test_prefork_when_parent_listed_as_child(self):
        # Some celery versions report parent in its own child list for -c 1.
        self.assertEqual(derive_pool_kind([100], 100), "prefork")


# ──────────────────────────────────────────────────────────────────────
# Adjacency
# ──────────────────────────────────────────────────────────────────────


class AdjacencyTests(SimpleTestCase):
    def _report(self, generated_at):
        return {"generated_at": generated_at.isoformat()}

    def test_within_window_is_adjacent(self):
        now = datetime.now(_dt_timezone.utc)
        cur = self._report(now)
        prev = self._report(now - timedelta(seconds=CADENCE_SECONDS))
        self.assertTrue(_is_previous_adjacent(cur, prev))

    def test_just_inside_window(self):
        now = datetime.now(_dt_timezone.utc)
        cur = self._report(now)
        # Adjacency tolerates CADENCE * ADJACENCY_FACTOR seconds
        prev = self._report(now - timedelta(seconds=CADENCE_SECONDS * 2 - 1))
        self.assertTrue(_is_previous_adjacent(cur, prev))

    def test_just_outside_window_is_not_adjacent(self):
        now = datetime.now(_dt_timezone.utc)
        cur = self._report(now)
        prev = self._report(now - timedelta(seconds=CADENCE_SECONDS * 2 + 1))
        self.assertFalse(_is_previous_adjacent(cur, prev))

    def test_no_prior_is_not_adjacent(self):
        self.assertFalse(_is_previous_adjacent({}, None))

    def test_negative_delta_is_not_adjacent(self):
        # Prior in the future — clock skew or test fixture mistake; never adjacent.
        now = datetime.now(_dt_timezone.utc)
        cur = self._report(now)
        prev = self._report(now + timedelta(seconds=60))
        self.assertFalse(_is_previous_adjacent(cur, prev))


# ──────────────────────────────────────────────────────────────────────
# _compute_status — single sample
# ──────────────────────────────────────────────────────────────────────


def _now_iso(offset_seconds: int = 0):
    return (
        datetime.now(_dt_timezone.utc) - timedelta(seconds=offset_seconds)
    ).isoformat()


def _worker(
    hostname: str,
    pct: Optional[float],
    concurrency: int = 2,
    cap_bytes: Optional[int] = 200 * 1024 * 1024,
    rss: Optional[int] = None,
):
    rss = rss if rss is not None else (int(pct * cap_bytes) if (pct is not None and cap_bytes) else 0)
    return {
        "hostname": hostname,
        "parent_pid": 9999,
        "leaf_pids": [9999],
        "pool_kind": "prefork",
        "concurrency_current": concurrency,
        "concurrency_floor": 1,
        "max_memory_per_child_kb": (cap_bytes // 1024) if cap_bytes else None,
        "cap_bytes": cap_bytes,
        "rss_bytes_per_leaf": [rss] if rss is not None else [None],
        "rss_bytes_max": rss,
        "rss_bytes_total": rss,
        "pct_of_cap_max": pct,
        "status": "OK",
        "reasons": [],
        "concurrency_suggested": concurrency,
    }


class ComputeStatusSingleSampleTests(SimpleTestCase):
    def test_below_threshold_is_ok(self):
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.5)],
        }
        _compute_status(report, previous_reports=None)
        self.assertEqual(report["workers"][0]["status"], "OK")
        self.assertEqual(report["overall_status"], "OK")
        self.assertFalse(report["downshift_recommended_global"])

    def test_above_threshold_single_sample_is_warn_not_crit(self):
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.95)],
        }
        _compute_status(report, previous_reports=None)
        self.assertEqual(report["workers"][0]["status"], "WARN")
        self.assertEqual(report["overall_status"], "WARN")
        self.assertFalse(report["downshift_recommended_global"])

    def test_no_cap_no_status_change(self):
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=None, cap_bytes=None, rss=1024)],
        }
        _compute_status(report, previous_reports=None)
        self.assertEqual(report["workers"][0]["status"], "OK")


class ComputeStatusSustainedPressureTests(SimpleTestCase):
    def test_three_consecutive_adjacent_above_threshold_is_crit(self):
        # Three samples at 5min intervals all above 80% → CRIT on current.
        priors = [
            {
                "generated_at": _now_iso(CADENCE_SECONDS * 2),
                "workers": [_worker("a@host", pct=0.85)],
            },
            {
                "generated_at": _now_iso(CADENCE_SECONDS),
                "workers": [_worker("a@host", pct=0.90)],
            },
        ]
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.95, concurrency=2)],
        }
        _compute_status(report, previous_reports=priors)
        self.assertEqual(report["workers"][0]["status"], "CRIT")
        self.assertEqual(report["overall_status"], "CRIT")
        self.assertTrue(report["downshift_recommended_global"])
        # Downshift heuristic: 2 → 1 (floor)
        self.assertEqual(report["suggested_concurrency_by_worker"], {"a@host": 1})
        self.assertIn("crit_persist_3samples:a@host",
                      report["sustain_gating"]["escalated_triggers"])

    def test_two_consecutive_is_warn_not_crit(self):
        # Only 2 samples above threshold (need 3) → stays WARN.
        priors = [
            {
                "generated_at": _now_iso(CADENCE_SECONDS),
                "workers": [_worker("a@host", pct=0.85)],
            },
        ]
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.90)],
        }
        _compute_status(report, previous_reports=priors)
        self.assertEqual(report["workers"][0]["status"], "WARN")

    def test_non_adjacent_prior_breaks_chain(self):
        # 3 samples above threshold but middle one isn't adjacent → stays WARN.
        priors = [
            {
                "generated_at": _now_iso(CADENCE_SECONDS * 10),  # Way stale
                "workers": [_worker("a@host", pct=0.85)],
            },
            {
                "generated_at": _now_iso(CADENCE_SECONDS),
                "workers": [_worker("a@host", pct=0.90)],
            },
        ]
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.95)],
        }
        _compute_status(report, previous_reports=priors)
        # Current + 1 adjacent prior = chain_len 2, below required 3.
        self.assertEqual(report["workers"][0]["status"], "WARN")

    def test_downshift_floor_at_one(self):
        # Worker already at concurrency=1 in CRIT — recommendation stays 1.
        priors = [
            {
                "generated_at": _now_iso(CADENCE_SECONDS * 2),
                "workers": [_worker("a@host", pct=0.85, concurrency=1)],
            },
            {
                "generated_at": _now_iso(CADENCE_SECONDS),
                "workers": [_worker("a@host", pct=0.90, concurrency=1)],
            },
        ]
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.95, concurrency=1)],
        }
        _compute_status(report, previous_reports=priors)
        self.assertEqual(report["workers"][0]["status"], "CRIT")
        # No concurrency entry — already at floor.
        self.assertNotIn("a@host", report["suggested_concurrency_by_worker"])
        # Recommended_actions still surfaces the leak warning.
        actions_text = " ".join(report["recommended_actions"])
        self.assertIn("a@host", actions_text)
        self.assertIn("floor", actions_text.lower())

    def test_worker_missing_in_prior_breaks_chain(self):
        # Worker was OK in prior (or wasn't sampled) — chain doesn't start.
        priors = [
            {
                "generated_at": _now_iso(CADENCE_SECONDS * 2),
                "workers": [_worker("other@host", pct=0.50)],  # Different worker
            },
            {
                "generated_at": _now_iso(CADENCE_SECONDS),
                "workers": [_worker("other@host", pct=0.50)],
            },
        ]
        report = {
            "generated_at": _now_iso(),
            "workers": [_worker("a@host", pct=0.95)],
        }
        _compute_status(report, previous_reports=priors)
        self.assertEqual(report["workers"][0]["status"], "WARN")


class ComputeStatusOverallTests(SimpleTestCase):
    def test_overall_is_worst_of(self):
        report = {
            "generated_at": _now_iso(),
            "workers": [
                _worker("a@host", pct=0.50),
                _worker("b@host", pct=0.85),
                _worker("c@host", pct=0.40),
            ],
        }
        _compute_status(report, previous_reports=None)
        self.assertEqual(report["overall_status"], "WARN")

    def test_top_offenders_sorted_desc(self):
        report = {
            "generated_at": _now_iso(),
            "workers": [
                _worker("a@host", pct=0.30),
                _worker("b@host", pct=0.85),
                _worker("c@host", pct=0.60),
            ],
        }
        _compute_status(report, previous_reports=None)
        hosts = [o["hostname"] for o in report["top_offenders"]]
        self.assertEqual(hosts[0], "b@host")
        self.assertEqual(hosts[1], "c@host")
        self.assertEqual(hosts[2], "a@host")


# ──────────────────────────────────────────────────────────────────────
# build_snapshot end-to-end with dependency-injected psutil + stats
# ──────────────────────────────────────────────────────────────────────


class BuildSnapshotTests(SimpleTestCase):
    def _make_psutil_mock(self, pid_to_rss, cmdline=None):
        """Return a psutil-shaped MagicMock that yields the given RSS per pid."""
        cmdline = cmdline or [
            "celery", "-A", "core", "worker", "--max-memory-per-child=200000"
        ]
        psutil_mod = MagicMock()

        def process_factory(pid):
            proc = MagicMock()
            proc.cmdline.return_value = cmdline
            mem = MagicMock()
            mem.rss = pid_to_rss[pid]
            proc.memory_info.return_value = mem
            return proc

        psutil_mod.Process.side_effect = process_factory
        return psutil_mod

    def test_schema_version_and_shape(self):
        stats = {
            "pa@host": {
                "pid": 100,
                "pool": {"processes": [100], "max-concurrency": 1},
            }
        }
        psutil_mod = self._make_psutil_mock({100: 50 * 1024 * 1024})
        report = build_snapshot(
            inspect_stats=stats,
            previous_reports=[],
            psutil_module=psutil_mod,
            now=datetime(2026, 6, 20, 1, 0, 0, tzinfo=_dt_timezone.utc),
        )
        self.assertEqual(report["schema_version"], SCHEMA_VERSION)
        self.assertEqual(report["cadence_seconds"], CADENCE_SECONDS)
        self.assertEqual(report["worker_count"], 1)
        self.assertIn("sustain_gating", report)
        sg = report["sustain_gating"]
        self.assertEqual(sg["cadence_seconds"], CADENCE_SECONDS)
        self.assertEqual(sg["consecutive_required"], CONSECUTIVE_REQUIRED)

    def test_no_workers_no_status_change(self):
        # Empty inspect (broker unreachable / no workers connected) shouldn't blow up.
        report = build_snapshot(
            inspect_stats={},
            previous_reports=[],
            psutil_module=MagicMock(),
            now=datetime(2026, 6, 20, 1, 0, 0, tzinfo=_dt_timezone.utc),
        )
        self.assertEqual(report["worker_count"], 0)
        self.assertEqual(report["overall_status"], "OK")
        self.assertEqual(report["workers"], [])

    def test_dead_process_is_recorded_not_fatal(self):
        # One leaf dies between inspect.stats and psutil sample — row records
        # sample_errors but doesn't void the whole snapshot.
        stats = {
            "a@host": {"pid": 100, "pool": {"processes": [100, 101], "max-concurrency": 2}},
        }
        psutil_mod = MagicMock()

        def process_factory(pid):
            if pid == 100:
                proc = MagicMock()
                proc.cmdline.return_value = [
                    "celery", "--max-memory-per-child=200000",
                ]
                mem = MagicMock()
                mem.rss = 100 * 1024 * 1024
                proc.memory_info.return_value = mem
                return proc
            # pid 101 has died
            raise Exception("NoSuchProcess")

        psutil_mod.Process.side_effect = process_factory

        report = build_snapshot(
            inspect_stats=stats,
            previous_reports=[],
            psutil_module=psutil_mod,
            now=datetime(2026, 6, 20, 1, 0, 0, tzinfo=_dt_timezone.utc),
        )
        row = report["workers"][0]
        self.assertEqual(row["leaf_pids"], [100, 101])
        # One real sample + one None
        self.assertIn(None, row["rss_bytes_per_leaf"])
        self.assertEqual(row["rss_bytes_max"], 100 * 1024 * 1024)
        self.assertIn("sample_errors", row)

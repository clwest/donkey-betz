"""Smoke tests for the `worker_memory_health` management command.

Session 1167 — COO Nervous System Backlog item #5.
"""
from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


_SAMPLE_REPORT = {
    "schema_version": 1,
    "generated_at": "2026-06-20T01:30:00+00:00",
    "generated_at_mt": "2026-06-19 19:30:00 MDT",
    "cadence_seconds": 300,
    "worker_count": 2,
    "workers": [
        {
            "hostname": "pa@host",
            "parent_pid": 100,
            "leaf_pids": [100],
            "pool_kind": "prefork",
            "concurrency_current": 1,
            "concurrency_floor": 1,
            "max_memory_per_child_kb": 200000,
            "cap_bytes": 200000 * 1024,
            "rss_bytes_per_leaf": [180 * 1024 * 1024],
            "rss_bytes_max": 180 * 1024 * 1024,
            "rss_bytes_total": 180 * 1024 * 1024,
            "pct_of_cap_max": 0.9,
            "status": "WARN",
            "reasons": ["rss_pct>=0.80 on current sample (chain_len=1, need 3)"],
            "concurrency_suggested": 1,
        },
        {
            "hostname": "broadcast@host",
            "parent_pid": 200,
            "leaf_pids": [200],
            "pool_kind": "threads_or_solo",
            "concurrency_current": 2,
            "concurrency_floor": 1,
            "max_memory_per_child_kb": 200000,
            "cap_bytes": 200000 * 1024,
            "rss_bytes_per_leaf": [50 * 1024 * 1024],
            "rss_bytes_max": 50 * 1024 * 1024,
            "rss_bytes_total": 50 * 1024 * 1024,
            "pct_of_cap_max": 0.25,
            "status": "OK",
            "reasons": [],
            "concurrency_suggested": 2,
        },
    ],
    "overall_status": "WARN",
    "top_offenders": [
        {
            "hostname": "pa@host",
            "pct_of_cap_max": 0.9,
            "rss_bytes_max": 180 * 1024 * 1024,
            "cap_bytes": 200000 * 1024,
            "status": "WARN",
        }
    ],
    "downshift_recommended_global": False,
    "suggested_concurrency_by_worker": {},
    "recommended_actions": [],
    "sustain_gating": {
        "previous_adjacent": True,
        "cadence_seconds": 300,
        "adjacency_window_seconds": 600,
        "consecutive_required": 3,
        "gated_triggers": ["warn_not_sustained:pa@host"],
        "escalated_triggers": [],
    },
}


class WorkerMemoryHealthCommandTests(SimpleTestCase):
    def test_human_summary_runs(self):
        out = StringIO()
        with patch(
            "core.management.commands.worker_memory_health.build_snapshot",
            return_value=_SAMPLE_REPORT,
        ):
            call_command("worker_memory_health", stdout=out)
        output = out.getvalue()
        self.assertIn("overall: WARN", output)
        self.assertIn("pa@host", output)
        self.assertIn("broadcast@host", output)
        self.assertIn("Top offenders", output)

    def test_json_output_is_valid(self):
        out = StringIO()
        with patch(
            "core.management.commands.worker_memory_health.build_snapshot",
            return_value=_SAMPLE_REPORT,
        ):
            call_command("worker_memory_health", "--json", stdout=out)
        parsed = json.loads(out.getvalue())
        self.assertEqual(parsed["schema_version"], 1)
        self.assertEqual(parsed["overall_status"], "WARN")
        self.assertEqual(parsed["worker_count"], 2)

    def test_no_workers_message(self):
        empty_report = {
            **_SAMPLE_REPORT,
            "workers": [],
            "worker_count": 0,
            "overall_status": "OK",
            "top_offenders": [],
            "recommended_actions": [],
        }
        out = StringIO()
        with patch(
            "core.management.commands.worker_memory_health.build_snapshot",
            return_value=empty_report,
        ):
            call_command("worker_memory_health", stdout=out)
        self.assertIn("no celery hosts reported", out.getvalue())

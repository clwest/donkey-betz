"""Tests for ops_tool.memory_pressure action (reduce-from-JSONL).

Session 1167 — COO Nervous System Backlog item #5.

Verifies that ``_ops_memory_pressure`` reads the latest JSONL snapshot
and projects it into the PA tool surface without re-classifying.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase


_FIXTURE_SNAPSHOT = {
    "schema_version": 1,
    "generated_at": "2026-06-20T01:30:00+00:00",
    "generated_at_mt": "2026-06-19 19:30:00 MDT",
    "cadence_seconds": 300,
    "worker_count": 2,
    "workers": [
        {"hostname": "pa@host", "status": "WARN", "pct_of_cap_max": 0.85},
        {"hostname": "broadcast@host", "status": "OK", "pct_of_cap_max": 0.2},
    ],
    "overall_status": "WARN",
    "top_offenders": [
        {"hostname": "pa@host", "pct_of_cap_max": 0.85, "status": "WARN"}
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


def _call_handler(handler_instance, trace_id="trace-test"):
    return handler_instance._ops_memory_pressure(trace_id)


class _StubHandler:
    """Bare-bones host for the mixin method under test."""
    pass


# Glue the OpsHandlersMixin onto our stub for direct invocation.
from core.services.td_handlers_ops import OpsHandlersMixin  # noqa: E402


class _MemoryPressureHandler(OpsHandlersMixin, _StubHandler):
    pass


class OpsMemoryPressureActionTests(SimpleTestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.handler = _MemoryPressureHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_snapshot(self, snapshot, filename="2026-06-20.jsonl"):
        path = self.tmpdir / filename
        path.write_text(json.dumps(snapshot) + "\n")
        return path

    def test_returns_latest_snapshot_projection(self):
        self._write_snapshot(_FIXTURE_SNAPSHOT)
        with patch(
            "core.services.memory_telemetry.LOG_DIR", self.tmpdir,
        ):
            result = _call_handler(self.handler)
        self.assertEqual(result["action"], "memory_pressure")
        self.assertEqual(result["overall_status"], "WARN")
        self.assertEqual(result["worker_count"], 2)
        self.assertEqual(len(result["workers"]), 2)
        self.assertEqual(len(result["top_offenders"]), 1)
        self.assertEqual(result["top_offenders"][0]["hostname"], "pa@host")
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["cadence_seconds"], 300)

    def test_returns_unknown_when_no_jsonl(self):
        # Empty dir — no JSONL files at all.
        with patch(
            "core.services.memory_telemetry.LOG_DIR", self.tmpdir,
        ):
            result = _call_handler(self.handler)
        self.assertEqual(result["overall_status"], "UNKNOWN")
        self.assertIn("note", result)

    def test_picks_latest_file_when_multiple(self):
        # Older file
        older = {**_FIXTURE_SNAPSHOT, "overall_status": "OK"}
        self._write_snapshot(older, filename="2026-06-19.jsonl")
        # Newer file (UTC date sorts lexicographically too)
        newer = {**_FIXTURE_SNAPSHOT, "overall_status": "CRIT"}
        self._write_snapshot(newer, filename="2026-06-20.jsonl")
        with patch(
            "core.services.memory_telemetry.LOG_DIR", self.tmpdir,
        ):
            result = _call_handler(self.handler)
        self.assertEqual(result["overall_status"], "CRIT")

    def test_picks_last_line_within_file(self):
        # Multiple lines — handler should pick the most recent (last line).
        path = self.tmpdir / "2026-06-20.jsonl"
        with open(path, "w") as f:
            f.write(json.dumps({**_FIXTURE_SNAPSHOT, "overall_status": "OK"}) + "\n")
            f.write(json.dumps({**_FIXTURE_SNAPSHOT, "overall_status": "CRIT"}) + "\n")
        with patch(
            "core.services.memory_telemetry.LOG_DIR", self.tmpdir,
        ):
            result = _call_handler(self.handler)
        self.assertEqual(result["overall_status"], "CRIT")

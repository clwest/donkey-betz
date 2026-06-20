"""Tests for the capture_worker_memory_snapshot Celery task.

Session 1167 — COO Nervous System Backlog item #5.

Verifies the task:
- Writes a JSONL line to logs/worker_memory/YYYY-MM-DD.jsonl (UTC).
- Returns a small summary dict.
- Emits a WARN log line on overall_status != OK.
"""
from __future__ import annotations

import json
import logging
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase


_OK_REPORT = {
    "schema_version": 1,
    "generated_at": "2026-06-20T01:30:00+00:00",
    "generated_at_mt": "2026-06-19 19:30:00 MDT",
    "cadence_seconds": 300,
    "worker_count": 1,
    "workers": [],
    "overall_status": "OK",
    "top_offenders": [],
    "downshift_recommended_global": False,
    "suggested_concurrency_by_worker": {},
    "recommended_actions": [],
    "sustain_gating": {
        "previous_adjacent": False,
        "cadence_seconds": 300,
        "adjacency_window_seconds": 600,
        "consecutive_required": 3,
        "gated_triggers": [],
        "escalated_triggers": [],
    },
}


_CRIT_REPORT = {
    **_OK_REPORT,
    "overall_status": "CRIT",
    "downshift_recommended_global": True,
    "top_offenders": [
        {"hostname": "pa@host", "pct_of_cap_max": 0.95, "status": "CRIT"}
    ],
    "sustain_gating": {
        **_OK_REPORT["sustain_gating"],
        "escalated_triggers": ["crit_persist_3samples:pa@host"],
    },
}


class CaptureWorkerMemorySnapshotTaskTests(SimpleTestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run_task(self, report):
        """Invoke the task body with the cache-singleton bypassed.

        ``singleton_task`` wraps the task body. To test the body
        directly without acquiring the real Redis lock, we patch the
        helpers it uses: ``build_snapshot`` and ``jsonl_path_for``.
        The singleton itself is fine to exercise — it just uses Django
        cache, which is in-memory for SimpleTestCase by default.
        """
        log_path = self.tmpdir / "2026-06-20.jsonl"

        from core.tasks import capture_worker_memory_snapshot

        with patch(
            "core.services.memory_telemetry.build_snapshot",
            return_value=report,
        ), patch(
            "core.services.memory_telemetry.jsonl_path_for",
            return_value=log_path,
        ):
            # Clear any prior lock so the singleton fires
            from django.core.cache import cache
            from core.services.redis_lock import LOCK_PREFIX
            cache.delete(LOCK_PREFIX + "capture-worker-memory-snapshot")
            return capture_worker_memory_snapshot(), log_path

    def test_writes_jsonl_line(self):
        _result, log_path = self._run_task(_OK_REPORT)
        self.assertTrue(log_path.exists())
        line = log_path.read_text().strip()
        parsed = json.loads(line)
        self.assertEqual(parsed["overall_status"], "OK")
        self.assertEqual(parsed["schema_version"], 1)

    def test_summary_dict_shape(self):
        result, _ = self._run_task(_OK_REPORT)
        self.assertIn("overall_status", result)
        self.assertIn("worker_count", result)
        self.assertIn("downshift_recommended", result)
        self.assertIn("escalated_triggers", result)
        self.assertIn("log_path", result)
        self.assertEqual(result["overall_status"], "OK")

    def test_crit_emits_warn_log(self):
        with self.assertLogs("core.tasks", level=logging.WARNING) as logs:
            result, _ = self._run_task(_CRIT_REPORT)
        joined = "\n".join(logs.output)
        self.assertIn("worker_memory_health", joined)
        self.assertIn("CRIT", joined)
        self.assertEqual(result["overall_status"], "CRIT")
        self.assertTrue(result["downshift_recommended"])

    def test_ok_emits_no_warn_log(self):
        with self.assertNoLogs("core.tasks", level=logging.WARNING):
            result, _ = self._run_task(_OK_REPORT)
        self.assertEqual(result["overall_status"], "OK")

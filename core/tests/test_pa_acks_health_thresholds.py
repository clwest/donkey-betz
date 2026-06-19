"""
Session 1164 PR #1 (item A + B) — pa_acks_health threshold tuning.

Asserts:
- A: _WARN_QUEUE_DEPTH raised 1 → 5 (no flip on single-message blip).
- B: binary infra triggers (no_workers, depth>=CRIT) require BOTH current
     AND previous snapshot to trip — single transient dip no longer flips
     CRIT/WARN.
- failure / hang triggers stay single-snapshot.
- previous_report=None → sustain triggers default to never-fire (safe
  first-run behavior).

Tests stub the report dict shape directly and call _compute_status — no
Redis / Celery / DB needed.

Run: python manage.py test core.tests.test_pa_acks_health_thresholds -v2
"""

from django.test import SimpleTestCase

from core.management.commands.pa_acks_health import Command


def _report(*, depth=0, worker_count=4, failures=0, hang_count=0, oldest_hang_age=0.0):
    samples = []
    if hang_count > 0:
        samples = [{"age_seconds": oldest_hang_age} for _ in range(hang_count)]
    return {
        "queue_depth": {"depth": depth},
        "workers": {"count": worker_count},
        "task_stats": {"failure": failures},
        "hang_signature": {"count": hang_count, "samples": samples},
        "advisory_flags": [],
        "status": "OK",
    }


class TestWarnDepthRaised(SimpleTestCase):

    def test_depth_1_no_longer_warns(self):
        cmd = Command()
        r = _report(depth=1)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "OK")

    def test_depth_4_no_longer_warns(self):
        cmd = Command()
        r = _report(depth=4)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "OK")

    def test_depth_5_warns(self):
        cmd = Command()
        r = _report(depth=5)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "WARN")

    def test_depth_19_warns_not_crit(self):
        cmd = Command()
        r = _report(depth=19)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "WARN")


class TestSustainNoWorkers(SimpleTestCase):

    def test_zero_workers_single_snapshot_does_not_fire(self):
        cmd = Command()
        r = _report(worker_count=0)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "OK")

    def test_zero_workers_with_healthy_previous_does_not_fire(self):
        cmd = Command()
        prev = _report(worker_count=4)
        r = _report(worker_count=0)
        cmd._compute_status(r, previous_report=prev)
        self.assertEqual(r["status"], "OK")

    def test_zero_workers_two_snapshots_in_a_row_fires_crit(self):
        cmd = Command()
        prev = _report(worker_count=0)
        r = _report(worker_count=0)
        cmd._compute_status(r, previous_report=prev)
        self.assertEqual(r["status"], "CRIT")


class TestSustainDepthCrit(SimpleTestCase):

    def test_depth_crit_single_snapshot_does_not_fire(self):
        cmd = Command()
        r = _report(depth=25)
        cmd._compute_status(r, previous_report=None)
        # Falls through to WARN (depth >= _WARN_QUEUE_DEPTH).
        self.assertEqual(r["status"], "WARN")

    def test_depth_crit_with_healthy_previous_does_not_crit(self):
        cmd = Command()
        prev = _report(depth=2)
        r = _report(depth=25)
        cmd._compute_status(r, previous_report=prev)
        self.assertEqual(r["status"], "WARN")

    def test_depth_crit_two_snapshots_in_a_row_fires_crit(self):
        cmd = Command()
        prev = _report(depth=21)
        r = _report(depth=25)
        cmd._compute_status(r, previous_report=prev)
        self.assertEqual(r["status"], "CRIT")


class TestSingleSnapshotTriggers(SimpleTestCase):

    def test_failure_spike_fires_crit_on_single_snapshot(self):
        cmd = Command()
        r = _report(failures=3)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "CRIT")

    def test_failure_one_fires_warn_on_single_snapshot(self):
        cmd = Command()
        r = _report(failures=1)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "WARN")

    def test_hang_count_3_fires_crit_on_single_snapshot(self):
        cmd = Command()
        r = _report(hang_count=3, oldest_hang_age=20)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "CRIT")

    def test_hang_age_180s_fires_crit_on_single_snapshot(self):
        cmd = Command()
        r = _report(hang_count=1, oldest_hang_age=200)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "CRIT")


class TestSustainGateCorrectness(SimpleTestCase):

    def test_previous_report_not_supplied_treats_as_first_run(self):
        cmd = Command()
        # Zero workers + zero workers, but previous_report omitted entirely
        # → sustain trigger must NOT fire.
        r = _report(worker_count=0)
        cmd._compute_status(r)
        self.assertEqual(r["status"], "OK")

    def test_trips_no_workers_helper(self):
        self.assertTrue(Command._trips_no_workers({"workers": {"count": 0}}))
        self.assertFalse(Command._trips_no_workers({"workers": {"count": 1}}))
        self.assertFalse(Command._trips_no_workers({"workers": {"count": 4}}))
        # Missing/malformed.
        self.assertTrue(Command._trips_no_workers({}))
        self.assertTrue(Command._trips_no_workers({"workers": {}}))

    def test_trips_depth_crit_helper(self):
        self.assertTrue(Command._trips_depth_crit({"queue_depth": {"depth": 20}}))
        self.assertTrue(Command._trips_depth_crit({"queue_depth": {"depth": 100}}))
        self.assertFalse(Command._trips_depth_crit({"queue_depth": {"depth": 19}}))
        self.assertFalse(Command._trips_depth_crit({"queue_depth": {"depth": 0}}))
        self.assertFalse(Command._trips_depth_crit({}))


class TestFailureAndDepthCombined(SimpleTestCase):

    def test_failure_spike_short_circuits_before_sustain_check(self):
        # Failure spike + healthy depth + zero workers (single snapshot) →
        # CRIT comes from failures, not from a sustain trigger. Verifies
        # the early-return order in _compute_status.
        cmd = Command()
        r = _report(failures=3, worker_count=0)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "CRIT")

    def test_depth_warn_with_failure_warn_stays_warn(self):
        cmd = Command()
        r = _report(depth=10, failures=1)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "WARN")

"""
Session 1164 PR #1 (item A + B) + PR #2 (time adjacency + observability)
— pa_acks_health threshold tuning.

Asserts:
- A: _WARN_QUEUE_DEPTH raised 1 → 5 (no flip on single-message blip).
- B: binary infra triggers (no_workers, depth>=CRIT) require BOTH current
     AND previous-adjacent snapshot to trip — single transient dip no
     longer flips CRIT/WARN; stale previous snapshot does not falsely
     count as adjacent.
- failure / hang triggers stay single-snapshot.
- previous_report=None → sustain triggers default to never-fire.
- Observability: `sustain_gating` field on every report records the
  adjacency decision + which sustain-eligible triggers were gated.

Tests stub the report dict shape directly and call _compute_status — no
Redis / Celery / DB needed.

Run: python manage.py test core.tests.test_pa_acks_health_thresholds -v2
"""

from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from core.management.commands.pa_acks_health import Command


_BASE_TS = datetime(2026, 6, 19, 18, 0, 0, tzinfo=timezone.utc)


def _report(
    *,
    depth=0,
    worker_count=4,
    failures=0,
    hang_count=0,
    oldest_hang_age=0.0,
    generated_at=_BASE_TS,
):
    samples = []
    if hang_count > 0:
        samples = [{"age_seconds": oldest_hang_age} for _ in range(hang_count)]
    return {
        "generated_at": generated_at.isoformat(),
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


# Session 1164 PR #2 — time adjacency + sustain observability.


class TestPreviousAdjacency(SimpleTestCase):

    def test_previous_within_30min_is_adjacent(self):
        cmd = Command()
        prev = _report(worker_count=0, generated_at=_BASE_TS)
        cur = _report(worker_count=0, generated_at=_BASE_TS + timedelta(minutes=30))
        cmd._compute_status(cur, previous_report=prev)
        self.assertEqual(cur["status"], "CRIT")
        self.assertTrue(cur["sustain_gating"]["previous_adjacent"])

    def test_previous_at_60min_boundary_is_adjacent(self):
        # 2 * expected_interval (1800s × 2 = 3600s) is the upper bound.
        cmd = Command()
        prev = _report(worker_count=0, generated_at=_BASE_TS)
        cur = _report(worker_count=0, generated_at=_BASE_TS + timedelta(seconds=3600))
        cmd._compute_status(cur, previous_report=prev)
        self.assertEqual(cur["status"], "CRIT")
        self.assertTrue(cur["sustain_gating"]["previous_adjacent"])

    def test_previous_at_65min_is_stale(self):
        cmd = Command()
        prev = _report(worker_count=0, generated_at=_BASE_TS)
        cur = _report(worker_count=0, generated_at=_BASE_TS + timedelta(minutes=65))
        cmd._compute_status(cur, previous_report=prev)
        # Stale previous → sustain check fails → status stays OK and the
        # gated trigger is recorded.
        self.assertEqual(cur["status"], "OK")
        self.assertFalse(cur["sustain_gating"]["previous_adjacent"])
        self.assertIn("no_workers", cur["sustain_gating"]["gated_triggers"])

    def test_previous_in_future_is_not_adjacent(self):
        # Clock skew defense — negative delta is treated as not adjacent.
        cmd = Command()
        prev = _report(worker_count=0, generated_at=_BASE_TS + timedelta(minutes=30))
        cur = _report(worker_count=0, generated_at=_BASE_TS)
        cmd._compute_status(cur, previous_report=prev)
        self.assertEqual(cur["status"], "OK")
        self.assertFalse(cur["sustain_gating"]["previous_adjacent"])

    def test_previous_missing_generated_at_is_not_adjacent(self):
        cmd = Command()
        prev = _report(worker_count=0)
        prev.pop("generated_at")
        cur = _report(worker_count=0)
        cmd._compute_status(cur, previous_report=prev)
        self.assertEqual(cur["status"], "OK")
        self.assertFalse(cur["sustain_gating"]["previous_adjacent"])

    def test_previous_malformed_timestamp_is_not_adjacent(self):
        cmd = Command()
        prev = _report(worker_count=0)
        prev["generated_at"] = "not-an-iso-string"
        cur = _report(worker_count=0)
        cmd._compute_status(cur, previous_report=prev)
        self.assertEqual(cur["status"], "OK")
        self.assertFalse(cur["sustain_gating"]["previous_adjacent"])


class TestSustainGatingObservability(SimpleTestCase):

    def test_sustain_gating_field_present_on_every_snapshot(self):
        cmd = Command()
        r = _report()
        cmd._compute_status(r, previous_report=None)
        self.assertIn("sustain_gating", r)
        self.assertIn("previous_adjacent", r["sustain_gating"])
        self.assertIn("expected_interval_seconds", r["sustain_gating"])
        self.assertIn("adjacency_factor", r["sustain_gating"])
        self.assertIn("gated_triggers", r["sustain_gating"])

    def test_no_gated_triggers_when_no_triggers_fired(self):
        cmd = Command()
        r = _report()  # healthy
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["sustain_gating"]["gated_triggers"], [])

    def test_no_workers_gated_on_first_run(self):
        cmd = Command()
        r = _report(worker_count=0)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["status"], "OK")
        self.assertIn("no_workers", r["sustain_gating"]["gated_triggers"])
        self.assertFalse(r["sustain_gating"]["previous_adjacent"])

    def test_depth_crit_gated_on_first_run(self):
        cmd = Command()
        r = _report(depth=25)
        cmd._compute_status(r, previous_report=None)
        # depth=25 → WARN (depth >= _WARN_QUEUE_DEPTH), CRIT gated.
        self.assertEqual(r["status"], "WARN")
        self.assertIn("depth_crit", r["sustain_gating"]["gated_triggers"])

    def test_both_triggers_gated_simultaneously(self):
        cmd = Command()
        r = _report(worker_count=0, depth=25)
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(set(r["sustain_gating"]["gated_triggers"]), {"no_workers", "depth_crit"})

    def test_observability_records_constants(self):
        cmd = Command()
        r = _report()
        cmd._compute_status(r, previous_report=None)
        self.assertEqual(r["sustain_gating"]["expected_interval_seconds"], 1800)
        self.assertEqual(r["sustain_gating"]["adjacency_factor"], 2)


class TestIsPreviousAdjacentHelper(SimpleTestCase):

    def test_returns_false_for_none(self):
        self.assertFalse(Command._is_previous_adjacent({"generated_at": _BASE_TS.isoformat()}, None))

    def test_returns_false_for_empty_dict(self):
        self.assertFalse(Command._is_previous_adjacent({"generated_at": _BASE_TS.isoformat()}, {}))

    def test_returns_true_for_30min_delta(self):
        prev = {"generated_at": _BASE_TS.isoformat()}
        cur = {"generated_at": (_BASE_TS + timedelta(minutes=30)).isoformat()}
        self.assertTrue(Command._is_previous_adjacent(cur, prev))

    def test_returns_false_for_61min_delta(self):
        prev = {"generated_at": _BASE_TS.isoformat()}
        cur = {"generated_at": (_BASE_TS + timedelta(minutes=61)).isoformat()}
        self.assertFalse(Command._is_previous_adjacent(cur, prev))

    def test_returns_false_for_negative_delta(self):
        prev = {"generated_at": (_BASE_TS + timedelta(minutes=30)).isoformat()}
        cur = {"generated_at": _BASE_TS.isoformat()}
        self.assertFalse(Command._is_previous_adjacent(cur, prev))

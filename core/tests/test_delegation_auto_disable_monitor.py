"""Tests for Arc I-0100 P3 Stop Condition #1 — auto-disable monitor.

Covered per Chris ratification (Session post-#2973):

- below threshold = no trip (4 sub-cases + all-zero-data case)
- above threshold = trip (4 sub-cases)
- trip sets shared cache sentinel
- is_tripped reads sentinel
- clear_trip resets sentinel
- delegation path short-circuits when tripped (flag on + sentinel set)
- lifecycle signal short-circuits when tripped (flag on + sentinel set)
- flag-off baseline remains unchanged (sentinel state irrelevant)

Run::

    python manage.py test core.tests.test_delegation_auto_disable_monitor -v2 --keepdb
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from django.core.cache import cache
from django.test import TestCase, override_settings

from core.models_ops_runs import OpsRun, OpsRunEvent
from core.services.delegation_auto_disable import (
    DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD,
    EXECUTION_ID_NULL_RATE_THRESHOLD,
    HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE,
    OPSRUNEVENT_DAILY_AUTO_DISABLE,
)
from core.services.delegation_auto_disable_monitor import (
    AUTO_DISABLED_LABEL,
    HANDLER_EXCEPTION_LABEL,
    KILL_SWITCH_KEY,
    LIFECYCLE_LABELS,
    ThresholdResult,
    TripDecision,
    check_thresholds,
    clear_trip,
    is_tripped,
    trip,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _make_ops_run(*, title: str = "seed") -> OpsRun:
    return OpsRun.objects.create(
        title=f"{title}-{uuid.uuid4().hex[:6]}",
        run_type="manual",
        triggered_by="manual",
        status="passed",
        domain="ops",
    )


def _seed_event(run: OpsRun, *, label: str, detail: dict | None = None) -> OpsRunEvent:
    return OpsRunEvent.objects.create(
        run=run,
        event_type="info",
        label=label,
        detail=detail if detail is not None else {},
    )


def _make_synthetic_breach_decision() -> TripDecision:
    result = ThresholdResult(
        name="opsrunevent_daily_volume",
        breached=True,
        measured=100.0,
        threshold=14.9,
        detail="synthetic breach for test",
    )
    return TripDecision(
        breached=True,
        results=[result],
        measured_at=datetime.now(timezone.utc).isoformat(),
    )


class _CacheIsolationMixin:
    """Clear the kill sentinel between tests so each starts clean."""

    def setUp(self):
        super().setUp()  # type: ignore[misc]
        cache.delete(KILL_SWITCH_KEY)

    def tearDown(self):
        cache.delete(KILL_SWITCH_KEY)
        super().tearDown()  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Below threshold — no breach
# ---------------------------------------------------------------------------


class CheckThresholdsBelowBreachTests(_CacheIsolationMixin, TestCase):

    def test_all_zero_data_no_breach(self):
        decision = check_thresholds()
        self.assertFalse(decision.breached)
        self.assertEqual(decision.reasons, [])
        # 4 threshold results always present.
        self.assertEqual(len(decision.results), 4)

    def test_daily_volume_below_threshold_no_breach(self):
        run = _make_ops_run()
        # Baseline threshold ~14.9 → seed 5 rows (well below).
        for _ in range(5):
            _seed_event(run, label="info")
        decision = check_thresholds()
        daily_result = next(r for r in decision.results if r.name == "opsrunevent_daily_volume")
        self.assertFalse(daily_result.breached)
        self.assertFalse(decision.breached)

    def test_handler_exception_below_threshold_no_breach(self):
        run = _make_ops_run()
        # Threshold = 3 → seed 2 rows.
        for _ in range(2):
            _seed_event(run, label=HANDLER_EXCEPTION_LABEL)
        decision = check_thresholds()
        handler_result = next(r for r in decision.results if r.name == "handler_exception_hourly")
        self.assertFalse(handler_result.breached)

    def test_null_rate_below_threshold_no_breach(self):
        run = _make_ops_run()
        # 20 lifecycle rows, 0 without execution_id → 0% NULL rate.
        for i in range(20):
            _seed_event(
                run,
                label=LIFECYCLE_LABELS[i % len(LIFECYCLE_LABELS)],
                detail={"execution_id": str(uuid.uuid4())},
            )
        decision = check_thresholds()
        null_result = next(r for r in decision.results if r.name == "execution_id_null_rate")
        self.assertFalse(null_result.breached)
        self.assertAlmostEqual(null_result.measured, 0.0)

    def test_distinct_trace_signature_below_threshold_no_breach(self):
        run = _make_ops_run()
        # Threshold = 3 → seed 2 rows with same signature and different traces.
        for i in range(2):
            _seed_event(
                run,
                label=HANDLER_EXCEPTION_LABEL,
                detail={"error_signature": "SigA", "trace_id": f"trace-{i}"},
            )
        decision = check_thresholds()
        signature_result = next(
            r for r in decision.results if r.name == "distinct_trace_error_signature"
        )
        self.assertFalse(signature_result.breached)


# ---------------------------------------------------------------------------
# Above threshold — breach
# ---------------------------------------------------------------------------


class CheckThresholdsAboveBreachTests(_CacheIsolationMixin, TestCase):

    def test_daily_volume_above_threshold_breaches(self):
        run = _make_ops_run()
        # Baseline threshold ~14.9 → seed 20 rows (breach).
        for _ in range(20):
            _seed_event(run, label="info")
        decision = check_thresholds()
        daily_result = next(r for r in decision.results if r.name == "opsrunevent_daily_volume")
        self.assertTrue(daily_result.breached)
        self.assertGreater(daily_result.measured, OPSRUNEVENT_DAILY_AUTO_DISABLE)
        self.assertTrue(decision.breached)
        self.assertIn("opsrunevent_daily_volume", decision.reasons)

    def test_handler_exception_above_threshold_breaches(self):
        run = _make_ops_run()
        # Threshold = 3 → seed 5 rows (breach).
        for _ in range(5):
            _seed_event(run, label=HANDLER_EXCEPTION_LABEL)
        decision = check_thresholds()
        handler_result = next(
            r for r in decision.results if r.name == "handler_exception_hourly"
        )
        self.assertTrue(handler_result.breached)
        self.assertGreater(handler_result.measured, HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE)
        # Daily volume also breached from seeded rows; still overall breach.
        self.assertTrue(decision.breached)
        self.assertIn("handler_exception_hourly", decision.reasons)

    def test_null_rate_above_threshold_breaches(self):
        run = _make_ops_run()
        # 20 lifecycle rows, 2 without execution_id → 10% NULL rate > 5% threshold.
        for i in range(18):
            _seed_event(
                run,
                label=LIFECYCLE_LABELS[i % len(LIFECYCLE_LABELS)],
                detail={"execution_id": str(uuid.uuid4())},
            )
        for _ in range(2):
            _seed_event(
                run,
                label=LIFECYCLE_LABELS[0],
                detail={},  # missing execution_id
            )
        decision = check_thresholds()
        null_result = next(r for r in decision.results if r.name == "execution_id_null_rate")
        self.assertTrue(null_result.breached)
        self.assertGreater(null_result.measured, EXECUTION_ID_NULL_RATE_THRESHOLD)

    def test_distinct_trace_signature_above_threshold_breaches(self):
        run = _make_ops_run()
        # Threshold = 3 → 3 distinct trace_ids for same signature (>=).
        for i in range(3):
            _seed_event(
                run,
                label=HANDLER_EXCEPTION_LABEL,
                detail={"error_signature": "SigA", "trace_id": f"trace-{i}"},
            )
        decision = check_thresholds()
        signature_result = next(
            r for r in decision.results if r.name == "distinct_trace_error_signature"
        )
        self.assertTrue(signature_result.breached)
        self.assertGreaterEqual(
            signature_result.measured, float(DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD)
        )


# ---------------------------------------------------------------------------
# Trip / sentinel / audit
# ---------------------------------------------------------------------------


class TripAndSentinelTests(_CacheIsolationMixin, TestCase):

    def test_trip_sets_sentinel(self):
        self.assertFalse(is_tripped())
        trip(_make_synthetic_breach_decision())
        self.assertTrue(is_tripped())

    def test_is_tripped_default_false(self):
        self.assertFalse(is_tripped())

    def test_clear_trip_resets_sentinel(self):
        trip(_make_synthetic_breach_decision())
        self.assertTrue(is_tripped())
        clear_trip()
        self.assertFalse(is_tripped())

    def test_trip_is_idempotent_on_sentinel(self):
        trip(_make_synthetic_breach_decision())
        trip(_make_synthetic_breach_decision())
        self.assertTrue(is_tripped())

    def test_trip_writes_audit_row(self):
        before_runs = OpsRun.objects.filter(title="RIGBY_DELEGATION_AUTO_DISABLED").count()
        before_events = OpsRunEvent.objects.filter(label=AUTO_DISABLED_LABEL).count()
        decision = _make_synthetic_breach_decision()
        trip(decision)
        after_runs = OpsRun.objects.filter(title="RIGBY_DELEGATION_AUTO_DISABLED").count()
        after_events = OpsRunEvent.objects.filter(label=AUTO_DISABLED_LABEL).count()
        self.assertEqual(after_runs - before_runs, 1)
        self.assertEqual(after_events - before_events, 1)
        audit_event = OpsRunEvent.objects.filter(label=AUTO_DISABLED_LABEL).order_by("-created_at").first()
        assert audit_event is not None
        self.assertEqual(audit_event.detail["adr_ref"], "ADR-0003 §3.4")
        self.assertEqual(audit_event.detail["arc"], "I-0100")
        self.assertEqual(audit_event.detail["intake"], "IB-1799-T1-03")
        self.assertIn("opsrunevent_daily_volume", audit_event.detail["reasons"])

    def test_trip_logs_error_line(self):
        with self.assertLogs(
            "core.services.delegation_auto_disable_monitor", level="ERROR"
        ) as captured:
            trip(_make_synthetic_breach_decision())
        found = [line for line in captured.output if "[RIGBY_DELEGATION_AUTO_DISABLED]" in line]
        self.assertTrue(found, f"expected [RIGBY_DELEGATION_AUTO_DISABLED] log line, got: {captured.output}")


# ---------------------------------------------------------------------------
# Delegation short-circuit when tripped
# ---------------------------------------------------------------------------


@override_settings(RIGBY_DELEGATION_ENABLED=True)
class DelegationShortCircuitTests(_CacheIsolationMixin, TestCase):

    def test_delegate_work_item_short_circuits_when_tripped(self):
        from core.services.rigby_mission_delegation import delegate_work_item

        trip(_make_synthetic_breach_decision())
        result = delegate_work_item(str(uuid.uuid4()))
        self.assertFalse(result["ok"])
        self.assertIn("auto-disabled", result["error"])
        self.assertTrue(result.get("kill_switch"))

    def test_delegate_work_item_normal_path_when_not_tripped(self):
        # Sentinel not set → we should pass the kill-switch gate. The
        # underlying "work_item not found" error confirms the guard let
        # us through.
        from core.services.rigby_mission_delegation import delegate_work_item

        self.assertFalse(is_tripped())
        result = delegate_work_item(str(uuid.uuid4()))
        self.assertFalse(result["ok"])
        self.assertIn("not found", result["error"])
        self.assertNotIn("auto-disabled", result["error"])
        self.assertFalse(result.get("kill_switch", False))

    def test_lifecycle_signal_short_circuits_when_tripped(self):
        # Import at test time — signals are connected at app-ready.
        from core.signals.rigby_delegation_signals import LABEL_AGENT_ASSIGNED
        from core.models_unified_system import AgentExecution, Agent

        trip(_make_synthetic_breach_decision())
        # Prepare an execution that WOULD trigger the handler (RigbyWorkItem parent).
        agent, _ = Agent.objects.get_or_create(name="TrendAnalysisAgent")
        before = OpsRunEvent.objects.filter(label=LABEL_AGENT_ASSIGNED).count()
        AgentExecution.objects.create(
            agent=agent,
            task="synthetic",
            parent_object_type="RigbyWorkItem",
            parent_object_id=str(uuid.uuid4()),
        )
        after = OpsRunEvent.objects.filter(label=LABEL_AGENT_ASSIGNED).count()
        # Sentinel tripped → no lifecycle events emitted.
        self.assertEqual(after, before)


# ---------------------------------------------------------------------------
# Flag-off baseline unchanged regardless of sentinel state
# ---------------------------------------------------------------------------


@override_settings(RIGBY_DELEGATION_ENABLED=False)
class FlagOffBaselineTests(_CacheIsolationMixin, TestCase):

    def test_flag_off_returns_flag_off_message_when_sentinel_clear(self):
        from core.services.rigby_mission_delegation import delegate_work_item

        self.assertFalse(is_tripped())
        result = delegate_work_item(str(uuid.uuid4()))
        self.assertFalse(result["ok"])
        self.assertIn("flag off", result["error"])
        self.assertEqual(result["flag"], "RIGBY_DELEGATION_ENABLED")

    def test_flag_off_returns_flag_off_message_when_sentinel_tripped(self):
        # Flag off short-circuits BEFORE the kill-switch check — the
        # error message must remain "flag off", not "auto-disabled".
        from core.services.rigby_mission_delegation import delegate_work_item

        trip(_make_synthetic_breach_decision())
        result = delegate_work_item(str(uuid.uuid4()))
        self.assertFalse(result["ok"])
        self.assertIn("flag off", result["error"])
        self.assertNotIn("auto-disabled", result["error"])

    def test_flag_off_signal_no_op_regardless_of_sentinel(self):
        from core.signals.rigby_delegation_signals import LABEL_AGENT_ASSIGNED
        from core.models_unified_system import AgentExecution, Agent

        trip(_make_synthetic_breach_decision())
        agent, _ = Agent.objects.get_or_create(name="TrendAnalysisAgent")
        before = OpsRunEvent.objects.filter(label=LABEL_AGENT_ASSIGNED).count()
        AgentExecution.objects.create(
            agent=agent,
            task="synthetic",
            parent_object_type="RigbyWorkItem",
            parent_object_id=str(uuid.uuid4()),
        )
        after = OpsRunEvent.objects.filter(label=LABEL_AGENT_ASSIGNED).count()
        self.assertEqual(after, before)

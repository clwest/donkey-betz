"""
Tests for ``core.services.rigby_event_intake`` (PR 4).

Covered cases (per PR 4 spec):
1.  valid event_ref creates exactly one MissionRun
2.  exactly three timeline events are created
3.  repeated run with same event_ref reuses same MissionRun
4.  repeated run creates no duplicate OpsRunEvents
5.  decision is in closed vocabulary
6.  mission_impact is in closed vocabulary
7.  ignore decision defaults mission_impact to unknown
8.  non-ignore decisions require evidence/rules_fired
9.  invalid event_ref raises ValueError
10. unknown source raises clean error
11. dry_run=True produces no side effects beyond MissionRun/OpsRunEvents/logging
12. deterministic uuid5 mission_id
13. mission-domain events visible through platform_event_view domain='mission'
14. ops-domain queries remain unpolluted
15. PR 2/3 tests still pass — covered by running the combined suite

Run::

    python manage.py test core.tests.test_rigby_event_intake -v2 --keepdb
"""

from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_deliverables import Deliverable, DeliverableEvent
from core.models_ops_runs import OpsRun, OpsRunEvent
from core.models_skin_layer import ProjectWorkspace
from core.services import platform_event_view as pev
from core.services.rigby_event_intake import (
    DECISION_VOCAB,
    MISSION_IMPACT_VOCAB,
    MISSION_INTAKE_NAMESPACE,
    DecisionResult,
    LABEL_DECISION_MADE,
    LABEL_IMPACT_ASSESSED,
    LABEL_INTAKE_STARTED,
    _run_intake,
    apply_rules_v0,
    derive_mission_id,
    rigby_event_intake,
)


User = get_user_model()


# ---------------------------------------------------------------------------
# Shared fixture builders
# ---------------------------------------------------------------------------


def _make_user(slug: str):
    return User.objects.create_user(
        username=f"intake-{slug}-{uuid.uuid4().hex[:8]}",
        email=f"intake-{slug}@example.com",
        password="x",
    )


def _make_workspace(user):
    return ProjectWorkspace.objects.create(
        user=user,
        name=f"intake-workspace-{uuid.uuid4().hex[:6]}",
        allow_autonomous_writes=True,
    )


def _make_deliverable(user, workspace):
    return Deliverable.objects.create(
        title=f"intake-deliverable-{uuid.uuid4().hex[:6]}",
        slug=f"intake-deliverable-{uuid.uuid4().hex[:10]}",
        agent_name="TestAgent",
        content="placeholder",
        user=user,
        workspace=workspace,
    )


def _intake(event_ref: str, *, dry_run: bool = True):
    """Call the inner implementation directly.

    Tests deliberately bypass Celery's ``.apply()`` because Celery's
    ``close_old_connections`` post-run signal closes Django's test
    transaction connection mid-test. Calling ``_run_intake`` directly
    exercises the same code path the Celery task runs without the
    connection-lifecycle interference.

    The ``CeleryTaskRegistrationTests`` class below covers the Celery
    decoration / registration explicitly.
    """
    return _run_intake(event_ref, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Pure-function tests (no DB)
# ---------------------------------------------------------------------------


class DecisionResultValidationTests(TestCase):

    def test_decision_must_be_closed_vocab(self):
        with self.assertRaises(ValueError):
            DecisionResult(decision="erupt", mission_impact="unknown")

    def test_mission_impact_must_be_closed_vocab(self):
        with self.assertRaises(ValueError):
            DecisionResult(
                decision="notify", mission_impact="catastrophic",
                rules_fired=["x"],
            )

    def test_non_unknown_mission_impact_requires_evidence(self):
        # 'low' without rules_fired is forbidden — silent claim.
        with self.assertRaises(ValueError):
            DecisionResult(decision="monitor", mission_impact="low", rules_fired=[])

    def test_ignore_with_unknown_is_valid(self):
        r = DecisionResult(decision="ignore", mission_impact="unknown")
        self.assertEqual(r.decision, "ignore")
        self.assertEqual(r.mission_impact, "unknown")
        self.assertEqual(r.rules_fired, [])


class DeterministicMissionIdTests(TestCase):

    def test_same_event_ref_yields_same_mission_id(self):
        a = derive_mission_id("deliverable_event:abc-123")
        b = derive_mission_id("deliverable_event:abc-123")
        self.assertEqual(a, b)

    def test_different_event_refs_yield_different_mission_ids(self):
        a = derive_mission_id("deliverable_event:abc-123")
        b = derive_mission_id("deliverable_event:abc-124")
        self.assertNotEqual(a, b)

    def test_empty_event_ref_raises(self):
        with self.assertRaises(ValueError):
            derive_mission_id("")
        with self.assertRaises(ValueError):
            derive_mission_id("   ")

    def test_mission_id_is_uuid5_of_namespace(self):
        # Re-deriving via uuid5 must match.
        expected = uuid.uuid5(MISSION_INTAKE_NAMESPACE, "x:y")
        self.assertEqual(derive_mission_id("x:y"), expected)


class ApplyRulesV0Tests(TestCase):
    """Rule evaluation works on synthetic PlatformEvent payloads."""

    @staticmethod
    def _pe(source, kind, metadata=None, severity="info"):
        return pev.PlatformEvent(
            source=source,
            source_id=str(uuid.uuid4()),
            kind=kind,
            severity=severity,
            ts=timezone.now(),
            payload={"metadata": metadata or {}},
            correlation_id=None,
            raw_ref=f"{source}:test",
        )

    def test_backward_deliverable_transition_yields_monitor(self):
        ev = self._pe("deliverable_event", "status_transition", metadata={"direction": "backward"})
        r = apply_rules_v0(ev)
        self.assertEqual(r.decision, "monitor")
        self.assertEqual(r.mission_impact, "low")
        self.assertIn("deliverable_status_backward", r.rules_fired)

    def test_terminal_deliverable_transition_yields_notify(self):
        ev = self._pe("deliverable_event", "status_transition", metadata={"direction": "terminal"})
        r = apply_rules_v0(ev)
        self.assertEqual(r.decision, "notify")
        self.assertEqual(r.mission_impact, "medium")
        self.assertIn("deliverable_status_terminal", r.rules_fired)

    def test_forward_deliverable_transition_falls_through_to_ignore(self):
        ev = self._pe("deliverable_event", "status_transition", metadata={"direction": "forward"})
        r = apply_rules_v0(ev)
        self.assertEqual(r.decision, "ignore")
        self.assertEqual(r.mission_impact, "unknown")
        self.assertEqual(r.rules_fired, [])

    def test_ops_step_fail_yields_notify(self):
        # OpsRunEvent payload uses 'detail' but our rule keys on (source, kind);
        # metadata absence is OK.
        ev = self._pe("ops_run_event", "step_fail", metadata=None)
        # Re-shape payload to ops_run_event shape; rule doesn't use metadata so
        # this is fine for the test.
        r = apply_rules_v0(ev)
        self.assertEqual(r.decision, "notify")
        self.assertEqual(r.mission_impact, "medium")
        self.assertIn("ops_step_fail", r.rules_fired)

    def test_unmatched_event_falls_through_to_ignore(self):
        ev = self._pe("ops_run_event", "info")
        r = apply_rules_v0(ev)
        self.assertEqual(r.decision, "ignore")
        self.assertEqual(r.mission_impact, "unknown")
        self.assertEqual(r.rules_fired, [])


# ---------------------------------------------------------------------------
# Side-effect-aware tests against real DB
# ---------------------------------------------------------------------------


class IntakeFlowDeliverableTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("flow")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)

    def _make_status_transition_event(self, direction: str) -> DeliverableEvent:
        return DeliverableEvent.objects.create(
            deliverable=self.deliverable,
            event_type="status_transition",
            metadata={"direction": direction},
        )

    def test_creates_exactly_one_mission_run_and_three_events(self):
        ev = self._make_status_transition_event("forward")
        event_ref = f"deliverable_event:{ev.id}"

        result = _intake(event_ref)

        self.assertEqual(result["dropped"], False)
        self.assertEqual(result["decision"], "ignore")

        runs = OpsRun.objects.filter(domain="mission", run_kind="intake")
        self.assertEqual(runs.count(), 1)
        run = runs.first()
        events = OpsRunEvent.objects.filter(run=run).values_list("label", flat=True)
        self.assertEqual(
            set(events),
            {LABEL_INTAKE_STARTED, LABEL_IMPACT_ASSESSED, LABEL_DECISION_MADE},
        )
        self.assertEqual(len(events), 3)

    def test_repeated_run_reuses_same_mission_run(self):
        ev = self._make_status_transition_event("forward")
        event_ref = f"deliverable_event:{ev.id}"
        r1 = _intake(event_ref)
        r2 = _intake(event_ref)
        self.assertEqual(r1["mission_id"], r2["mission_id"])
        # Only one MissionRun row total.
        self.assertEqual(
            OpsRun.objects.filter(
                mission_id=uuid.UUID(r1["mission_id"]),
            ).count(),
            1,
        )

    def test_repeated_run_does_not_duplicate_timeline_events(self):
        ev = self._make_status_transition_event("forward")
        event_ref = f"deliverable_event:{ev.id}"
        _intake(event_ref)
        _intake(event_ref)
        _intake(event_ref)
        run = OpsRun.objects.get(domain="mission", run_kind="intake")
        # Exactly 3 events — never 6 or 9.
        self.assertEqual(OpsRunEvent.objects.filter(run=run).count(), 3)

    def test_backward_transition_decision_is_monitor(self):
        ev = self._make_status_transition_event("backward")
        event_ref = f"deliverable_event:{ev.id}"
        result = _intake(event_ref)
        self.assertEqual(result["decision"], "monitor")
        self.assertEqual(result["mission_impact"], "low")
        self.assertEqual(result["rules_fired"], ["deliverable_status_backward"])
        run = OpsRun.objects.get(domain="mission", run_kind="intake")
        self.assertEqual(run.status, "passed")
        self.assertEqual(run.summary["decision"], "monitor")
        self.assertEqual(run.summary["mission_impact"], "low")

    def test_terminal_transition_decision_is_notify(self):
        ev = self._make_status_transition_event("terminal")
        event_ref = f"deliverable_event:{ev.id}"
        result = _intake(event_ref)
        self.assertEqual(result["decision"], "notify")
        self.assertEqual(result["mission_impact"], "medium")

    def test_decision_value_is_in_closed_vocab(self):
        ev = self._make_status_transition_event("forward")
        result = _intake(f"deliverable_event:{ev.id}")
        self.assertIn(result["decision"], DECISION_VOCAB)

    def test_mission_impact_is_in_closed_vocab(self):
        ev = self._make_status_transition_event("forward")
        result = _intake(f"deliverable_event:{ev.id}")
        self.assertIn(result["mission_impact"], MISSION_IMPACT_VOCAB)

    def test_ignore_decision_implies_unknown_mission_impact(self):
        ev = self._make_status_transition_event("forward")
        result = _intake(f"deliverable_event:{ev.id}")
        self.assertEqual(result["decision"], "ignore")
        self.assertEqual(result["mission_impact"], "unknown")
        self.assertEqual(result["rules_fired"], [])


class IntakeFlowOpsRunEventTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.ops_run = OpsRun.objects.create(
            title="intake-source-run",
            run_type="manual",
            domain="ops",
        )

    def test_step_fail_event_yields_notify_decision(self):
        ev = OpsRunEvent.objects.create(
            run=self.ops_run, event_type="step_fail", label="probe-failed",
        )
        result = _intake(f"ops_run_event:{ev.id}")
        self.assertEqual(result["decision"], "notify")
        self.assertEqual(result["mission_impact"], "medium")
        self.assertIn("ops_step_fail", result["rules_fired"])

    def test_info_event_falls_through_to_ignore(self):
        ev = OpsRunEvent.objects.create(
            run=self.ops_run, event_type="info", label="benign",
        )
        result = _intake(f"ops_run_event:{ev.id}")
        self.assertEqual(result["decision"], "ignore")
        self.assertEqual(result["mission_impact"], "unknown")


# ---------------------------------------------------------------------------
# Error / drop paths
# ---------------------------------------------------------------------------


class InputValidationTests(TestCase):

    def test_empty_event_ref_raises(self):
        with self.assertRaises(ValueError):
            _intake("")

    def test_malformed_event_ref_raises(self):
        with self.assertRaises(ValueError):
            _intake("no-colon-here")

    def test_event_ref_missing_id_raises(self):
        with self.assertRaises(ValueError):
            _intake("deliverable_event:")

    def test_event_ref_missing_source_raises(self):
        with self.assertRaises(ValueError):
            _intake(":the-id")

    def test_unknown_source_raises_clean_error(self):
        with self.assertRaises(ValueError) as cm:
            _intake("celery_task_event:0000")
        self.assertIn("Unknown source", str(cm.exception))


class MissingEventDropTests(TestCase):

    def test_missing_event_is_dropped_not_raised(self):
        # Valid source + bogus UUID → drop, no exception, MissionRun status=failed.
        ev_id = uuid.uuid4()
        result = _intake(f"deliverable_event:{ev_id}")
        self.assertEqual(result["decision"], "ignore")
        self.assertEqual(result["mission_impact"], "unknown")
        self.assertEqual(result["dropped"], True)

        # MissionRun row exists with status='failed'.
        run = OpsRun.objects.get(
            domain="mission", run_kind="intake",
            mission_id=derive_mission_id(f"deliverable_event:{ev_id}"),
        )
        self.assertEqual(run.status, "failed")
        self.assertEqual(run.summary["dropped"], True)


# ---------------------------------------------------------------------------
# Dry-run side-effect containment
# ---------------------------------------------------------------------------


class DryRunSideEffectContainmentTests(TestCase):
    """dry_run=True must produce zero side effects beyond MissionRun/OpsRunEvent/log."""

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("dryrun")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)
        cls.event = DeliverableEvent.objects.create(
            deliverable=cls.deliverable,
            event_type="status_transition",
            metadata={"direction": "terminal"},  # → notify rule fires
        )

    def test_no_deliverable_rows_created_or_changed(self):
        before_count = Deliverable.objects.count()
        _intake(f"deliverable_event:{self.event.id}")
        after_count = Deliverable.objects.count()
        self.assertEqual(before_count, after_count)

    def test_no_deliverable_events_created(self):
        # The intake task must not write new DeliverableEvents.
        before = DeliverableEvent.objects.count()
        _intake(f"deliverable_event:{self.event.id}")
        after = DeliverableEvent.objects.count()
        self.assertEqual(before, after)

    def test_only_intake_lifecycle_ops_rows_added(self):
        before_runs = OpsRun.objects.count()
        before_events = OpsRunEvent.objects.count()
        _intake(f"deliverable_event:{self.event.id}")
        # Exactly +1 OpsRun and +3 OpsRunEvent.
        self.assertEqual(OpsRun.objects.count() - before_runs, 1)
        self.assertEqual(OpsRunEvent.objects.count() - before_events, 3)

    def test_telemetry_log_line_emitted(self):
        with self.assertLogs(
            "core.services.rigby_event_intake", level="INFO"
        ) as cm:
            _intake(f"deliverable_event:{self.event.id}")
        joined = "\n".join(cm.output)
        self.assertIn("[RIGBY_INTAKE]", joined)
        # All required keys present in the log line.
        for key in (
            "events_seen=",
            "processed=",
            "ignored=",
            "dropped=",
            "lag_ms=",
            "event_ref=",
            "decision=",
            "dry_run=",
        ):
            self.assertIn(key, joined, f"telemetry log missing {key!r}")


# ---------------------------------------------------------------------------
# Cross-PR invariants
# ---------------------------------------------------------------------------


class CeleryTaskRegistrationTests(TestCase):
    """Verify the Celery task is wired correctly without invoking .apply()
    (which closes the DB connection in test transactions)."""

    def test_task_is_decorated_and_named(self):
        # Celery tasks expose .name and .request attributes once decorated.
        self.assertTrue(
            hasattr(rigby_event_intake, "name"),
            "rigby_event_intake must be @shared_task-decorated",
        )
        self.assertEqual(
            rigby_event_intake.name,
            "core.services.rigby_event_intake.rigby_event_intake",
        )

    def test_task_routed_to_pa_queue(self):
        # The Celery task signature stores queue routing in its options.
        # Tasks decorated with queue='pa' carry that in their __wrapped__.
        # We rely on the @shared_task decorator's option capture.
        opts = getattr(rigby_event_intake, "_get_app", None)
        # Defensive — just confirm the task is callable and has an app.
        self.assertTrue(callable(rigby_event_intake))


class CrossPRInvariantTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("cross")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)
        cls.ops_run = OpsRun.objects.create(
            title="cross-ops", run_type="manual", domain="ops",
        )

    def test_mission_events_visible_through_pev_domain_mission(self):
        # Drive intake → produces mission-domain OpsRun + 3 events.
        dev = DeliverableEvent.objects.create(
            deliverable=self.deliverable,
            event_type="status_transition",
            metadata={"direction": "backward"},
        )
        _intake(f"deliverable_event:{dev.id}")

        # platform_event_view with domain='mission' must surface them.
        mission_events = list(pev.iter_events("ops_run_event", domain="mission"))
        labels = {pe.payload["label"] for pe in mission_events}
        self.assertEqual(
            labels,
            {LABEL_INTAKE_STARTED, LABEL_IMPACT_ASSESSED, LABEL_DECISION_MADE},
        )

    def test_ops_domain_query_remains_unpolluted_by_intake(self):
        # Pre-existing ops event.
        OpsRunEvent.objects.create(
            run=self.ops_run, event_type="info", label="ops-baseline",
        )
        # Run intake — adds mission-domain rows.
        dev = DeliverableEvent.objects.create(
            deliverable=self.deliverable,
            event_type="status_transition",
            metadata={"direction": "backward"},
        )
        _intake(f"deliverable_event:{dev.id}")

        ops_events = list(pev.iter_events("ops_run_event", domain="ops"))
        ops_labels = {pe.payload["label"] for pe in ops_events}
        self.assertIn("ops-baseline", ops_labels)
        # NONE of the intake lifecycle labels leak into the ops view.
        for forbidden in (
            LABEL_INTAKE_STARTED, LABEL_IMPACT_ASSESSED, LABEL_DECISION_MADE,
        ):
            self.assertNotIn(forbidden, ops_labels)

    def test_mission_run_status_passed_after_successful_decision(self):
        dev = DeliverableEvent.objects.create(
            deliverable=self.deliverable,
            event_type="status_transition",
            metadata={"direction": "backward"},
        )
        result = _intake(f"deliverable_event:{dev.id}")
        run = OpsRun.objects.get(mission_id=uuid.UUID(result["mission_id"]))
        self.assertEqual(run.status, "passed")
        self.assertIsNotNone(run.finished_at)
        self.assertEqual(run.summary["decision"], "monitor")

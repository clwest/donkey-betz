"""
Tests for PR 6: RigbyWorkItem internal operational queue.

Covered cases (per PR 6 spec):
1. flag off → no work item
2. flag on + notify decision → work item created
3. flag on + monitor decision → work item created
4. flag on + ignore decision → no work item
5. duplicate intake run → no duplicate work item
6. work item links to source MissionRun
7. work item stores source_event_ref
8. work item stores decision / severity / mission_impact
9. evidence JSON includes rules_fired and event_ref
10. status defaults to 'open'
11. no human notification side effects
12. no agent dispatch side effects
13. all PR 2/3/4/5 tests still pass — covered by combined-suite check

Run::

    python manage.py test core.tests.test_rigby_work_item -v2 --keepdb
"""

from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from core.models_deliverables import Deliverable, DeliverableEvent
from core.models_ops_runs import OpsRun, OpsRunEvent
from core.models_rigby_work_items import RigbyWorkItem
from core.models_skin_layer import ProjectWorkspace
from core.services.rigby_event_intake import (
    ACTIONABLE_DECISIONS,
    _run_intake,
    derive_mission_id,
)


User = get_user_model()


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _make_user(slug):
    return User.objects.create_user(
        username=f"wq-{slug}-{uuid.uuid4().hex[:8]}",
        email=f"wq-{slug}@example.com",
        password="x",
    )


def _make_workspace(user):
    return ProjectWorkspace.objects.create(
        user=user,
        name=f"wq-workspace-{uuid.uuid4().hex[:6]}",
        allow_autonomous_writes=True,
    )


def _make_deliverable(user, workspace, *, status='draft'):
    return Deliverable.objects.create(
        title=f"wq-deliverable-{uuid.uuid4().hex[:6]}",
        slug=f"wq-deliverable-{uuid.uuid4().hex[:10]}",
        agent_name="TestAgent",
        content="placeholder",
        user=user,
        workspace=workspace,
        status=status,
    )


def _make_status_transition_event(deliverable, *, direction):
    return DeliverableEvent.objects.create(
        deliverable=deliverable,
        event_type='status_transition',
        metadata={'direction': direction},
    )


# ---------------------------------------------------------------------------
# Flag OFF — no work items even on actionable decisions
# ---------------------------------------------------------------------------


class FlagOffNoWorkItemTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("flag-off")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=False)
    def test_no_work_item_when_flag_off_for_notify(self):
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        before = RigbyWorkItem.objects.count()
        result = _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(result["decision"], "notify")
        self.assertIsNone(result["work_item_id"])
        self.assertEqual(RigbyWorkItem.objects.count(), before)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=False)
    def test_no_work_item_when_flag_off_for_monitor(self):
        ev = _make_status_transition_event(self.deliverable, direction='backward')
        before = RigbyWorkItem.objects.count()
        result = _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(result["decision"], "monitor")
        self.assertIsNone(result["work_item_id"])
        self.assertEqual(RigbyWorkItem.objects.count(), before)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=False)
    def test_intake_still_creates_mission_run_when_flag_off(self):
        """Sanity check — PR 5 behavior unaffected by PR 6 flag."""
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        before_runs = OpsRun.objects.filter(
            domain='mission', run_kind='intake',
        ).count()
        _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(
            OpsRun.objects.filter(
                domain='mission', run_kind='intake',
            ).count() - before_runs,
            1,
        )


# ---------------------------------------------------------------------------
# Flag ON — actionable decisions create work items
# ---------------------------------------------------------------------------


class FlagOnActionableDecisionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("flag-on")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_notify_decision_creates_work_item(self):
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        result = _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(result["decision"], "notify")
        self.assertIsNotNone(result["work_item_id"])

        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.decision, "notify")
        self.assertEqual(item.mission_impact, "medium")
        self.assertEqual(item.status, "open")  # default

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_monitor_decision_creates_work_item(self):
        ev = _make_status_transition_event(self.deliverable, direction='backward')
        result = _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(result["decision"], "monitor")
        self.assertIsNotNone(result["work_item_id"])

        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.decision, "monitor")
        self.assertEqual(item.mission_impact, "low")
        self.assertEqual(item.priority, 3)  # low → 3

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_ignore_decision_does_not_create_work_item(self):
        # Forward transition → ignore decision.
        ev = _make_status_transition_event(self.deliverable, direction='forward')
        before = RigbyWorkItem.objects.count()
        result = _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(result["decision"], "ignore")
        self.assertIsNone(result["work_item_id"])
        self.assertEqual(RigbyWorkItem.objects.count(), before)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_ops_step_fail_creates_work_item(self):
        # Mission-source = OpsRunEvent on an ops-domain run.
        ops_run = OpsRun.objects.create(
            title="step-fail-source", run_type="manual", domain="ops",
        )
        ev = OpsRunEvent.objects.create(
            run=ops_run, event_type='step_fail', label='probe-failed',
        )
        result = _run_intake(f"ops_run_event:{ev.id}")
        self.assertEqual(result["decision"], "notify")
        self.assertIsNotNone(result["work_item_id"])
        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.source_event_ref, f"ops_run_event:{ev.id}")


# ---------------------------------------------------------------------------
# Idempotency — duplicate intake runs do not duplicate work items
# ---------------------------------------------------------------------------


class IdempotencyTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("idempotent")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_repeat_intake_does_not_duplicate_work_item(self):
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        event_ref = f"deliverable_event:{ev.id}"
        r1 = _run_intake(event_ref)
        r2 = _run_intake(event_ref)
        r3 = _run_intake(event_ref)

        # Same work item across all three runs.
        self.assertEqual(r1["work_item_id"], r2["work_item_id"])
        self.assertEqual(r2["work_item_id"], r3["work_item_id"])

        # Exactly one row in the queue.
        self.assertEqual(
            RigbyWorkItem.objects.filter(source_event_ref=event_ref).count(),
            1,
        )


# ---------------------------------------------------------------------------
# Linkage + structured fields
# ---------------------------------------------------------------------------


class WorkItemFieldShapeTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("shape")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_links_to_source_mission_run(self):
        ev = _make_status_transition_event(self.deliverable, direction='backward')
        result = _run_intake(f"deliverable_event:{ev.id}")
        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        mission_run = OpsRun.objects.get(
            mission_id=derive_mission_id(f"deliverable_event:{ev.id}"),
        )
        self.assertEqual(item.source_mission_run_id, mission_run.id)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_stores_source_event_ref(self):
        ev = _make_status_transition_event(self.deliverable, direction='backward')
        event_ref = f"deliverable_event:{ev.id}"
        result = _run_intake(event_ref)
        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.source_event_ref, event_ref)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_stores_decision_severity_mission_impact(self):
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        result = _run_intake(f"deliverable_event:{ev.id}")
        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.decision, "notify")
        # severity comes from PR 2's PlatformEvent severity mapping.
        self.assertIn(item.severity, {
            "debug", "info", "notice", "warn", "error", "critical", "unknown",
        })
        self.assertIn(item.mission_impact, {
            "unknown", "low", "medium", "high",
        })
        self.assertEqual(item.mission_impact, "medium")

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_evidence_includes_rules_fired_and_event_ref(self):
        ev = _make_status_transition_event(self.deliverable, direction='backward')
        event_ref = f"deliverable_event:{ev.id}"
        result = _run_intake(event_ref)
        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.evidence.get("event_ref"), event_ref)
        self.assertEqual(
            item.evidence.get("rules_fired"),
            ["deliverable_status_backward"],
        )
        # Reason quoted into evidence so a reader doesn't need to join.
        self.assertIn("decision_reason", item.evidence)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_status_defaults_to_open(self):
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        result = _run_intake(f"deliverable_event:{ev.id}")
        item = RigbyWorkItem.objects.get(pk=result["work_item_id"])
        self.assertEqual(item.status, "open")
        self.assertIsNone(item.resolved_at)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_priority_ladder_matches_mission_impact(self):
        # backward → low → priority 3
        ev_low = _make_status_transition_event(self.deliverable, direction='backward')
        r_low = _run_intake(f"deliverable_event:{ev_low.id}")
        item_low = RigbyWorkItem.objects.get(pk=r_low["work_item_id"])
        self.assertEqual(item_low.priority, 3)

        # terminal → medium → priority 5
        ev_med = _make_status_transition_event(self.deliverable, direction='terminal')
        r_med = _run_intake(f"deliverable_event:{ev_med.id}")
        item_med = RigbyWorkItem.objects.get(pk=r_med["work_item_id"])
        self.assertEqual(item_med.priority, 5)


# ---------------------------------------------------------------------------
# No-side-effect containment
# ---------------------------------------------------------------------------


class NoSideEffectTests(TestCase):
    """PR 6 must not introduce human notification, agent dispatch, or
    any external surface call beyond writing the work-item row."""

    @classmethod
    def setUpTestData(cls):
        cls.user = _make_user("noside")
        cls.workspace = _make_workspace(cls.user)
        cls.deliverable = _make_deliverable(cls.user, cls.workspace)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_no_new_deliverable_or_deliverable_events_created(self):
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        before_d = Deliverable.objects.count()
        before_de = DeliverableEvent.objects.count()
        _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(Deliverable.objects.count(), before_d)
        self.assertEqual(DeliverableEvent.objects.count(), before_de)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_no_agent_execution_rows_created(self):
        """No AgentExecution rows touched. Conservative check — work item
        creation must not spawn agent execution."""
        from core.models_unified_system import AgentExecution
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        before = AgentExecution.objects.count()
        _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(AgentExecution.objects.count(), before)

    @override_settings(RIGBY_INTERNAL_WORK_QUEUE_ENABLED=True)
    def test_only_one_new_work_item_row_created(self):
        """Exactly one row delta on RigbyWorkItem; no other model rows
        beyond the existing intake lifecycle (MissionRun + 3
        OpsRunEvents) get touched."""
        ev = _make_status_transition_event(self.deliverable, direction='terminal')
        before_items = RigbyWorkItem.objects.count()
        before_ops_events = OpsRunEvent.objects.count()
        _run_intake(f"deliverable_event:{ev.id}")
        self.assertEqual(RigbyWorkItem.objects.count() - before_items, 1)
        # Mission run + 3 lifecycle events.
        self.assertEqual(OpsRunEvent.objects.count() - before_ops_events, 3)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class ConstantsTests(TestCase):

    def test_actionable_decisions_v0_set(self):
        # v0 actionable set = {monitor, notify}. ignore / log are not
        # in this set; create_initiative / delegate are deferred.
        self.assertEqual(ACTIONABLE_DECISIONS, frozenset({"monitor", "notify"}))

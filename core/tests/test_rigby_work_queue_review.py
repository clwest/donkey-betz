"""
Tests for PR 7: Rigby work-queue review tools.

Covered cases (per PR 7 spec):
1.  flag off → tools return disabled response (no DB writes)
2.  list returns paginated work items
3.  list ordering is priority desc, created_at desc
4.  filters: status / decision / priority_min / since
5.  acknowledge: open → acknowledged
6.  acknowledge: already acknowledged → idempotent no-op
7.  resolve: → resolved with valid outcome + resolved_at
8.  resolve: invalid outcome rejected
9.  ignore: requires non-empty reason
10. invalid transitions raise clean errors (resolved → ignore, ignored → resolve, etc.)
11. every transition writes OpsRunEvent on parent MissionRun
12. OpsRunEvent detail includes work_item_id, from_status, to_status, and note/outcome/reason
13. no human notification side effects
14. no agent dispatch side effects
15. all PR 2-6 tests still pass — covered by combined-suite check

Run::

    python manage.py test core.tests.test_rigby_work_queue_review -v2 --keepdb
"""

from __future__ import annotations

import uuid
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_ops_runs import OpsRun, OpsRunEvent
from core.models_rigby_work_items import RigbyWorkItem
from core.services.td_handlers_rigby_work_queue import (
    LABEL_ACKNOWLEDGED,
    LABEL_IGNORED,
    LABEL_RESOLVED,
    RESOLVE_OUTCOME_VOCAB,
)
from core.services.tool_dispatcher import get_tool_dispatcher


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _make_mission_run():
    return OpsRun.objects.create(
        title=f"wqr-mission-{uuid.uuid4().hex[:6]}",
        run_type="manual",
        triggered_by="pa_tool",
        domain="mission",
        run_kind="intake",
        mission_id=uuid.uuid4(),
    )


def _make_work_item(
    *,
    decision="monitor",
    severity="warn",
    mission_impact="low",
    priority=3,
    status="open",
    event_ref=None,
):
    mission_run = _make_mission_run()
    return RigbyWorkItem.objects.create(
        source_mission_run=mission_run,
        source_event_ref=event_ref or f"deliverable_event:{uuid.uuid4()}",
        decision=decision,
        severity=severity,
        mission_impact=mission_impact,
        priority=priority,
        status=status,
        title=f"Test work item ({decision})",
        summary="test summary",
        recommended_next_action="test next action",
        evidence={"event_ref": event_ref or "synthetic", "rules_fired": ["test_rule"]},
    )


def _dispatch(action: str, **payload):
    """Invoke the rigby_work_item handler via the tool dispatcher
    (sync path), returning the raw handler dict."""
    dispatcher = get_tool_dispatcher()
    full_payload = {"action": action, **payload}
    # Call the handler directly (bypass the async execute() wrapper —
    # we're testing handler behavior, not the latency/trace plumbing).
    return dispatcher._handle_rigby_work_item(
        tool_name="rigby_work_item",
        payload=full_payload,
        user_id=None,
        trace_id="test-trace",
    )


# ---------------------------------------------------------------------------
# Flag OFF — tools refuse cleanly
# ---------------------------------------------------------------------------


class FlagOffDisabledResponseTests(TestCase):

    @override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=False)
    def test_list_returns_disabled_response(self):
        result = _dispatch("list")
        self.assertEqual(result["ok"], False)
        self.assertIn("disabled", result["error"].lower())
        self.assertEqual(result["flag"], "RIGBY_WORK_QUEUE_REVIEW_ENABLED")

    @override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=False)
    def test_acknowledge_returns_disabled_response(self):
        item = _make_work_item()
        before_events = OpsRunEvent.objects.count()
        result = _dispatch("acknowledge", work_item_id=str(item.id))
        self.assertEqual(result["ok"], False)
        self.assertIn("disabled", result["error"].lower())
        # No transition event was written.
        self.assertEqual(OpsRunEvent.objects.count(), before_events)
        # Status unchanged.
        item.refresh_from_db()
        self.assertEqual(item.status, "open")

    @override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=False)
    def test_resolve_returns_disabled_response(self):
        item = _make_work_item()
        result = _dispatch("resolve", work_item_id=str(item.id), outcome="acted")
        self.assertEqual(result["ok"], False)
        item.refresh_from_db()
        self.assertEqual(item.status, "open")
        self.assertIsNone(item.resolved_at)

    @override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=False)
    def test_ignore_returns_disabled_response(self):
        item = _make_work_item()
        result = _dispatch("ignore", work_item_id=str(item.id), reason="not relevant")
        self.assertEqual(result["ok"], False)
        item.refresh_from_db()
        self.assertEqual(item.status, "open")


# ---------------------------------------------------------------------------
# list — pagination + filters + ordering
# ---------------------------------------------------------------------------


@override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=True)
class ListActionTests(TestCase):

    def test_list_returns_paginated_rows(self):
        for i in range(5):
            _make_work_item(priority=3 + (i % 3))
        result = _dispatch("list", limit=2, offset=0)
        self.assertEqual(result["ok"], True)
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["total"], 5)
        self.assertEqual(result["limit"], 2)
        self.assertEqual(result["offset"], 0)

    def test_list_orders_by_priority_desc_then_created_at_desc(self):
        # Create with mixed priorities AND mixed created_at ordering.
        items = []
        for prio in (5, 3, 5, 8):  # purposely unsorted
            it = _make_work_item(priority=prio)
            items.append(it)
        result = _dispatch("list", limit=100)
        out_priorities = [row["priority"] for row in result["rows"]]
        # priority DESC: 8, 5, 5, 3
        self.assertEqual(out_priorities[0], 8)
        self.assertEqual(out_priorities[-1], 3)
        # Within priority=5 ties, created_at DESC means the later-created one comes first.
        prio5_rows = [r for r in result["rows"] if r["priority"] == 5]
        self.assertEqual(len(prio5_rows), 2)
        self.assertGreater(prio5_rows[0]["created_at"], prio5_rows[1]["created_at"])

    def test_filter_by_status(self):
        _make_work_item(status="open")
        _make_work_item(status="open")
        # Make an acknowledged item directly (skip the transition for setup).
        ack = _make_work_item()
        ack.status = "acknowledged"
        ack.save(update_fields=["status"])

        out = _dispatch("list", status="open")
        self.assertEqual(len(out["rows"]), 2)
        for r in out["rows"]:
            self.assertEqual(r["status"], "open")

    def test_filter_by_decision(self):
        _make_work_item(decision="monitor")
        _make_work_item(decision="notify")
        _make_work_item(decision="notify")
        out = _dispatch("list", decision="notify")
        self.assertEqual(len(out["rows"]), 2)
        for r in out["rows"]:
            self.assertEqual(r["decision"], "notify")

    def test_filter_by_priority_min(self):
        _make_work_item(priority=3)
        _make_work_item(priority=5)
        _make_work_item(priority=8)
        out = _dispatch("list", priority_min=5)
        priorities = sorted(r["priority"] for r in out["rows"])
        self.assertEqual(priorities, [5, 8])

    def test_filter_by_since(self):
        old = _make_work_item()
        # Backdate the old item.
        RigbyWorkItem.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=5),
        )
        new = _make_work_item()
        since_iso = (timezone.now() - timedelta(hours=1)).isoformat()
        out = _dispatch("list", since=since_iso)
        ids = {r["id"] for r in out["rows"]}
        self.assertIn(str(new.id), ids)
        self.assertNotIn(str(old.id), ids)


# ---------------------------------------------------------------------------
# acknowledge
# ---------------------------------------------------------------------------


@override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=True)
class AcknowledgeActionTests(TestCase):

    def test_acknowledge_open_transitions_to_acknowledged(self):
        item = _make_work_item(status="open")
        before_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        ).count()
        result = _dispatch("acknowledge", work_item_id=str(item.id), note="seen")
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["work_item"]["status"], "acknowledged")
        item.refresh_from_db()
        self.assertEqual(item.status, "acknowledged")

        # OpsRunEvent audit row appended to parent MissionRun timeline.
        after_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        )
        self.assertEqual(after_events.count() - before_events, 1)
        new_event = after_events.latest("created_at")
        self.assertEqual(new_event.label, LABEL_ACKNOWLEDGED)
        self.assertEqual(new_event.detail["work_item_id"], str(item.id))
        self.assertEqual(new_event.detail["from_status"], "open")
        self.assertEqual(new_event.detail["to_status"], "acknowledged")
        self.assertEqual(new_event.detail["note"], "seen")

    def test_acknowledge_already_acknowledged_is_idempotent(self):
        item = _make_work_item(status="open")
        _dispatch("acknowledge", work_item_id=str(item.id))
        before_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        ).count()
        result = _dispatch("acknowledge", work_item_id=str(item.id))
        # No-op response.
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["no_op"], True)
        # No new transition event.
        self.assertEqual(
            OpsRunEvent.objects.filter(run_id=item.source_mission_run_id).count(),
            before_events,
        )

    def test_acknowledge_terminal_state_rejected(self):
        item = _make_work_item(status="open")
        _dispatch("ignore", work_item_id=str(item.id), reason="not now")
        result = _dispatch("acknowledge", work_item_id=str(item.id))
        self.assertEqual(result["ok"], False)
        self.assertIn("Cannot acknowledge", result["error"])

    def test_acknowledge_requires_work_item_id(self):
        result = _dispatch("acknowledge")
        self.assertEqual(result["ok"], False)
        self.assertIn("work_item_id is required", result["error"])

    def test_acknowledge_unknown_item_returns_clean_error(self):
        result = _dispatch("acknowledge", work_item_id=str(uuid.uuid4()))
        self.assertEqual(result["ok"], False)
        self.assertIn("not found", result["error"])


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------


@override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=True)
class ResolveActionTests(TestCase):

    def test_resolve_sets_resolved_at_and_audits(self):
        item = _make_work_item(status="open")
        before_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        ).count()
        result = _dispatch(
            "resolve", work_item_id=str(item.id), outcome="acted", note="fixed it",
        )
        self.assertEqual(result["ok"], True)
        item.refresh_from_db()
        self.assertEqual(item.status, "resolved")
        self.assertIsNotNone(item.resolved_at)

        # Audit event on parent MissionRun.
        after_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        )
        self.assertEqual(after_events.count() - before_events, 1)
        evt = after_events.latest("created_at")
        self.assertEqual(evt.label, LABEL_RESOLVED)
        self.assertEqual(evt.event_type, "step_pass")
        self.assertEqual(evt.detail["work_item_id"], str(item.id))
        self.assertEqual(evt.detail["from_status"], "open")
        self.assertEqual(evt.detail["to_status"], "resolved")
        self.assertEqual(evt.detail["outcome"], "acted")
        self.assertEqual(evt.detail["note"], "fixed it")

    def test_resolve_from_acknowledged(self):
        item = _make_work_item(status="open")
        _dispatch("acknowledge", work_item_id=str(item.id))
        result = _dispatch(
            "resolve", work_item_id=str(item.id), outcome="no_action_needed",
        )
        self.assertEqual(result["ok"], True)
        item.refresh_from_db()
        self.assertEqual(item.status, "resolved")
        # Audit event reflects the actual from_status.
        evt = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id, label=LABEL_RESOLVED,
        ).latest("created_at")
        self.assertEqual(evt.detail["from_status"], "acknowledged")

    def test_resolve_invalid_outcome_rejected(self):
        item = _make_work_item(status="open")
        result = _dispatch(
            "resolve", work_item_id=str(item.id), outcome="erupted",
        )
        self.assertEqual(result["ok"], False)
        self.assertIn("outcome", result["error"])
        item.refresh_from_db()
        self.assertEqual(item.status, "open")

    def test_resolve_missing_outcome_rejected(self):
        item = _make_work_item(status="open")
        result = _dispatch("resolve", work_item_id=str(item.id))
        self.assertEqual(result["ok"], False)
        self.assertIn("outcome", result["error"])

    def test_resolve_already_resolved_is_idempotent(self):
        item = _make_work_item(status="open")
        _dispatch("resolve", work_item_id=str(item.id), outcome="acted")
        before = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id, label=LABEL_RESOLVED,
        ).count()
        result = _dispatch(
            "resolve", work_item_id=str(item.id), outcome="acted",
        )
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["no_op"], True)
        after = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id, label=LABEL_RESOLVED,
        ).count()
        self.assertEqual(after, before)

    def test_resolve_ignored_item_rejected(self):
        item = _make_work_item(status="open")
        _dispatch("ignore", work_item_id=str(item.id), reason="dup")
        result = _dispatch(
            "resolve", work_item_id=str(item.id), outcome="acted",
        )
        self.assertEqual(result["ok"], False)
        self.assertIn("ignored", result["error"])

    def test_resolve_vocab_matches_constant(self):
        self.assertEqual(
            RESOLVE_OUTCOME_VOCAB,
            frozenset({"acted", "delegated_externally", "no_action_needed"}),
        )


# ---------------------------------------------------------------------------
# ignore
# ---------------------------------------------------------------------------


@override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=True)
class IgnoreActionTests(TestCase):

    def test_ignore_with_reason_transitions_and_audits(self):
        item = _make_work_item(status="open")
        before_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        ).count()
        result = _dispatch(
            "ignore", work_item_id=str(item.id), reason="duplicate of WI-x",
        )
        self.assertEqual(result["ok"], True)
        item.refresh_from_db()
        self.assertEqual(item.status, "ignored")

        after_events = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        )
        self.assertEqual(after_events.count() - before_events, 1)
        evt = after_events.latest("created_at")
        self.assertEqual(evt.label, LABEL_IGNORED)
        self.assertEqual(evt.detail["work_item_id"], str(item.id))
        self.assertEqual(evt.detail["from_status"], "open")
        self.assertEqual(evt.detail["to_status"], "ignored")
        self.assertEqual(evt.detail["reason"], "duplicate of WI-x")

    def test_ignore_requires_non_empty_reason(self):
        item = _make_work_item(status="open")
        result_blank = _dispatch("ignore", work_item_id=str(item.id), reason="")
        self.assertEqual(result_blank["ok"], False)
        self.assertIn("reason is required", result_blank["error"])
        result_missing = _dispatch("ignore", work_item_id=str(item.id))
        self.assertEqual(result_missing["ok"], False)
        item.refresh_from_db()
        self.assertEqual(item.status, "open")

    def test_ignore_resolved_item_rejected(self):
        item = _make_work_item(status="open")
        _dispatch("resolve", work_item_id=str(item.id), outcome="acted")
        result = _dispatch("ignore", work_item_id=str(item.id), reason="late")
        self.assertEqual(result["ok"], False)
        self.assertIn("resolved", result["error"])

    def test_ignore_already_ignored_is_idempotent(self):
        item = _make_work_item(status="open")
        _dispatch("ignore", work_item_id=str(item.id), reason="dup")
        before = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id, label=LABEL_IGNORED,
        ).count()
        result = _dispatch("ignore", work_item_id=str(item.id), reason="dup")
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["no_op"], True)
        after = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id, label=LABEL_IGNORED,
        ).count()
        self.assertEqual(after, before)


# ---------------------------------------------------------------------------
# No-side-effect containment
# ---------------------------------------------------------------------------


@override_settings(RIGBY_WORK_QUEUE_REVIEW_ENABLED=True)
class NoSideEffectTests(TestCase):

    def test_no_agent_execution_rows_on_any_transition(self):
        from core.models_unified_system import AgentExecution
        item = _make_work_item(status="open")
        before = AgentExecution.objects.count()
        _dispatch("acknowledge", work_item_id=str(item.id))
        _dispatch(
            "resolve", work_item_id=str(item.id), outcome="acted",
        )
        self.assertEqual(AgentExecution.objects.count(), before)

    def test_only_ops_run_event_rows_change_on_transition(self):
        from core.models_deliverables import Deliverable, DeliverableEvent
        from core.models_unified_system import AgentExecution

        item = _make_work_item(status="open")
        before_d = Deliverable.objects.count()
        before_de = DeliverableEvent.objects.count()
        before_ae = AgentExecution.objects.count()
        before_ore = OpsRunEvent.objects.filter(
            run_id=item.source_mission_run_id,
        ).count()

        _dispatch("acknowledge", work_item_id=str(item.id), note="seen")

        # Only OpsRunEvent on the parent MissionRun gets +1.
        self.assertEqual(Deliverable.objects.count(), before_d)
        self.assertEqual(DeliverableEvent.objects.count(), before_de)
        self.assertEqual(AgentExecution.objects.count(), before_ae)
        self.assertEqual(
            OpsRunEvent.objects.filter(
                run_id=item.source_mission_run_id,
            ).count() - before_ore,
            1,
        )


# ---------------------------------------------------------------------------
# Schema registration sanity check
# ---------------------------------------------------------------------------


class SchemaRegistrationTests(TestCase):

    def test_rigby_work_item_schema_present(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        names = {s.get("name") for s in PA_TOOL_SCHEMAS if isinstance(s, dict)}
        self.assertIn("rigby_work_item", names)

    def test_rigby_work_item_handler_registered(self):
        dispatcher = get_tool_dispatcher()
        self.assertIn("rigby_work_item", dispatcher._tool_handlers)

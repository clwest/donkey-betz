"""Session 1233 Sub-step C — workspace materialization + daily beat task.

Test classes:

1. ``MorningBriefWorkspaceMaterializationTests`` —
   ``_get_or_create_morning_brief_workspace`` is idempotent, scoped per
   user, and gracefully handles None user.
2. ``MorningBriefDeliverableWorkspaceLinkTests`` —
   ``_execute_create_morning_brief_deliverable_step`` writes the
   deliverable's ``workspace_id`` to the materialized workspace.
3. ``MorningBriefBeatScheduleRegistrationTests`` — the beat schedule
   entry ``generate-morning-brief-daily`` is registered with the
   MissionRunner-backed task target + correct cadence.
4. ``MorningBriefBeatTaskTelemetryTests`` — DELETED in S1258 PR 3.3
   (legacy ``generate_morning_brief_daily`` task body removed; the
   new task's telemetry is covered by
   ``test_chief_of_staff_routine.SuccessPathTests`` and
   ``test_employees_chief_of_staff``).
5. ``GenerateMorningBriefDailyTaskTests`` — DELETED in S1258 PR 3.3
   for the same reason.
6. ``MorningBriefLaneWorkspaceThreadTests`` — workflow-internal
   resolution of the target workspace (unchanged by PR 3.3).

Run::

    python manage.py test core.tests.test_morning_brief_sub_step_c -v2
"""

import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_skin_layer import ProjectWorkspace
from core.models_deliverables import Deliverable
from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

User = get_user_model()


class MorningBriefWorkspaceMaterializationTests(TestCase):
    """Session 1233 Sub-step C — workspace get_or_create idempotence."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"test_chris_{uuid.uuid4().hex[:8]}",
            password='test',
        )
        self.agent = WorkflowOrchestrationAgent(user=self.user)

    def test_first_call_creates_workspace(self):
        """First fire materializes the Morning Brief workspace."""
        self.assertEqual(
            ProjectWorkspace.objects.filter(
                user=self.user, name='Morning Brief',
            ).count(),
            0,
            "Pre-condition: no workspace exists yet.",
        )

        workspace = self.agent._get_or_create_morning_brief_workspace(self.user)

        self.assertIsNotNone(workspace)
        self.assertEqual(workspace.name, 'Morning Brief')
        self.assertEqual(workspace.user, self.user)
        self.assertEqual(workspace.workspace_type, 'local')
        self.assertEqual(workspace.root_path, '/morning-brief')

    def test_second_call_reuses_workspace(self):
        """Subsequent fires return the existing workspace (no duplicate)."""
        first = self.agent._get_or_create_morning_brief_workspace(self.user)
        second = self.agent._get_or_create_morning_brief_workspace(self.user)

        self.assertEqual(first.id, second.id,
                         "get_or_create must be idempotent — same UUID.")
        self.assertEqual(
            ProjectWorkspace.objects.filter(
                user=self.user, name='Morning Brief',
            ).count(),
            1,
            "Only one workspace row may exist per user after multiple calls.",
        )

    def test_workspaces_scoped_per_user(self):
        """Each user gets their own Morning Brief workspace."""
        other_user = User.objects.create_user(
            username=f"test_other_{uuid.uuid4().hex[:8]}",
            password='test',
        )

        chris_ws = self.agent._get_or_create_morning_brief_workspace(self.user)
        other_ws = self.agent._get_or_create_morning_brief_workspace(other_user)

        self.assertNotEqual(chris_ws.id, other_ws.id,
                            "Different users → different workspaces.")
        self.assertEqual(chris_ws.user, self.user)
        self.assertEqual(other_ws.user, other_user)

    def test_none_user_returns_none(self):
        """No user → no workspace creation. Workflow continues with
        workspace=None (deliverable lands uncategorized)."""
        workspace = self.agent._get_or_create_morning_brief_workspace(None)
        self.assertIsNone(workspace)


class MorningBriefDeliverableWorkspaceLinkTests(TestCase):
    """Session 1233 Sub-step C — deliverable persists with workspace_id."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"test_chris_{uuid.uuid4().hex[:8]}",
            password='test',
        )
        self.agent = WorkflowOrchestrationAgent(user=self.user)

    def test_deliverable_linked_to_morning_brief_workspace(self):
        context = {
            'morning_brief_markdown': '## TL;DR\n- ok\n',
            'morning_brief_title': 'Morning Brief — 2026-06-25',
            'user': self.user,
            'rotation_slot': 'ai_infra_deep_dive',
        }
        result = self.agent._execute_create_morning_brief_deliverable_step(
            context,
        )

        self.assertTrue(result['success'])
        self.assertIsNotNone(result['deliverable_id'])
        self.assertIsNotNone(result['workspace_id'])

        deliverable = Deliverable.objects.get(id=result['deliverable_id'])
        self.assertIsNotNone(deliverable.workspace_id,
                             "Sub-step C: workspace_id must not be None")
        self.assertEqual(str(deliverable.workspace_id),
                         result['workspace_id'])
        self.assertEqual(deliverable.workspace.name, 'Morning Brief')
        self.assertEqual(deliverable.workspace.user, self.user)
        self.assertEqual(deliverable.category, 'Morning Brief')
        self.assertEqual(deliverable.metadata.get('session'), '1233-C')

    def test_multiple_briefs_accumulate_in_same_workspace(self):
        """Per spec: deliverables accumulate over time so Chris can
        scroll back through past briefs."""
        for i in range(3):
            self.agent._execute_create_morning_brief_deliverable_step({
                'morning_brief_markdown': f'## Brief {i}\n',
                'morning_brief_title': f'Morning Brief — Day {i}',
                'user': self.user,
                'rotation_slot': 'ai_infra_deep_dive',
            })

        # All three deliverables land in the SAME workspace.
        deliverables = Deliverable.objects.filter(
            user=self.user, category='Morning Brief',
        )
        self.assertEqual(deliverables.count(), 3)
        workspace_ids = set(d.workspace_id for d in deliverables)
        self.assertEqual(
            len(workspace_ids), 1,
            "All briefs must land in the SAME workspace (accumulation).",
        )

    def test_no_markdown_smoke_no_op_still_returns_success(self):
        """B.1 graceful-no-op preserved under Sub-step C: empty
        morning_brief_markdown → no deliverable, but workflow contract
        still honored."""
        result = self.agent._execute_create_morning_brief_deliverable_step(
            {'user': self.user},
        )
        self.assertTrue(result['success'])
        self.assertIsNone(result['deliverable_id'])

    def test_deliverable_persists_when_context_user_is_a_dict(self):
        """Session 1234 D2.fix regression guard.

        The 2026-06-25 D2 verification surfaced this: lane handlers
        (Lane 1 platform_readiness onward) write a serialized profile
        DICT into ``context['user']`` for prompt-injection purposes:

            {'name': '', 'username': 'chris',
             'communication_style': 'professional', ...}

        Pre-D2.fix the handler did
        ``user = context.get('user') or getattr(self, 'user', None)``
        — the dict short-circuited the ``or`` and got passed to
        ``Deliverable.user`` (a FK to UnifiedUser), raising:

            ValueError: Cannot assign "{...}": "Deliverable.user"
            must be a "UnifiedUser" instance.

        After D2.fix: handler uses ``self.user`` directly (which IS
        a UnifiedUser instance because the beat task constructs
        ``WorkflowOrchestrationAgent(user=user)``).
        """
        context_with_dict_user = {
            'morning_brief_markdown': '## TL;DR\n- D2.fix regression test\n',
            'morning_brief_title': 'Morning Brief — D2.fix test',
            # Real lane handlers inject this exact shape:
            'user': {
                'name': '',
                'username': 'chris',
                'communication_style': 'professional',
                'memory_summary': 'Profile: prefers balanced responses',
                'goals': [],
                'has_user_context': True,
            },
            'rotation_slot': 'gtm_pipeline_health',
        }
        result = self.agent._execute_create_morning_brief_deliverable_step(
            context_with_dict_user,
        )

        self.assertTrue(result['success'],
                        f"Deliverable creation must succeed even when "
                        f"context['user'] is a profile dict. Got: {result!r}")
        self.assertIsNotNone(result['deliverable_id'])

        deliverable = Deliverable.objects.get(id=result['deliverable_id'])
        # Deliverable.user MUST resolve to the agent's self.user instance,
        # NOT the profile dict from context.
        self.assertEqual(deliverable.user, self.user)


# NOTE (S1258 PR 3.3): GenerateMorningBriefDailyTaskTests +
# MorningBriefBeatTaskTelemetryTests were deleted here. They exercised
# the legacy ``core.tasks.generate_morning_brief_daily`` task body,
# which was removed in this PR. Equivalent coverage of the
# MissionRunner-backed Chief of Staff task now lives in:
#   * ``core/tests/test_chief_of_staff_routine.py`` (SuccessPathTests,
#     fail-loud raise contract, mission timeline + verdict semantics)
#   * ``core/tests/test_employees_chief_of_staff.py`` (task
#     registration, runner factory, production caller count = 3)


class MorningBriefBeatScheduleRegistrationTests(TestCase):
    """Source-level guard: the beat schedule has the morning_brief entry."""

    def test_beat_row_targets_chief_of_staff_runner(self):
        """S1258 PR 3.3 post-migration ground truth: the beat row
        ``generate-morning-brief-daily`` MUST route to the
        MissionRunner-backed ``chief_of_staff_morning_brief_run``.
        Cadence + queue + row name preserved from pre-migration."""
        from core.celery import app
        schedule = app.conf.beat_schedule
        self.assertIn('generate-morning-brief-daily', schedule)
        entry = schedule['generate-morning-brief-daily']
        self.assertEqual(
            entry['task'], 'chief_of_staff_morning_brief_run',
            "S1258 PR 3.3 flipped the beat row's task field; "
            "if this fails, the migration was reverted or the "
            "task name drifted from the @shared_task name= kwarg "
            "in core/tasks_chief_of_staff.py.",
        )
        # Crontab must fire at 7:00 AM Denver per spec § Scheduling.
        # PR 3.3 preserves cadence — only the task target changed.
        from celery.schedules import crontab
        sched = entry['schedule']
        self.assertIsInstance(sched, crontab)
        # crontab.hour and crontab.minute are frozensets of ints
        self.assertEqual(sched.hour, {7})
        self.assertEqual(sched.minute, {0})
        # Queue + expires preserved.
        self.assertEqual(entry['options']['queue'], 'default')
        self.assertEqual(entry['options']['expires'], 3600)

    def test_morning_brief_beat_row_not_in_local_deny_tasks(self):
        """Session 1239 flip: `generate-morning-brief-daily` is INTENTIONALLY
        kept out of LOCAL_DENY_TASKS so it fires daily on local for Chris's
        Sub-step E dogfood loop (Mon-Fri qualitative verdicts → tightening
        PRs). Pre-1239 the task was deny-listed because the brief was
        produced from a 5+ LLM-call pipeline and chris only read it on prod.
        After Sub-step D shipped (Sessions 1235-1238), the local fire is the
        cheapest + tightest iteration loop for content-quality tuning. The
        S1258 PR 3.3 task-target flip does not change this — the beat row
        NAME is the LOCAL_DENY_TASKS key, not the task target. If cost ever
        becomes a concern, deny here again."""
        from core.management.commands.add_critical_celery_tasks import (
            LOCAL_DENY_TASKS,
        )
        self.assertNotIn('generate-morning-brief-daily', LOCAL_DENY_TASKS)

    def test_legacy_generate_morning_brief_daily_symbol_removed(self):
        """S1258 PR 3.3 regression guard: the legacy
        ``generate_morning_brief_daily`` task body was deleted from
        ``core.tasks``. Any future re-introduction (accidental revert,
        cherry-pick from a stale branch) would break the beat-row contract
        because the worker registry would have a duplicate name conflict.
        """
        import core.tasks
        self.assertFalse(
            hasattr(core.tasks, 'generate_morning_brief_daily'),
            "core.tasks.generate_morning_brief_daily was deleted in "
            "S1258 PR 3.3. If this assertion fails, either the legacy "
            "task body was reintroduced or the beat row was reverted "
            "WITHOUT restoring the body — both are migration drift.",
        )

    def test_periodic_task_row_targets_chief_of_staff_runner(self):
        """S1258 PR 3.3 DB-state guard: the live PeriodicTask row named
        ``generate-morning-brief-daily``, when it exists in this DB, MUST
        point its ``task`` field at ``chief_of_staff_morning_brief_run``.

        The row is created by ``sync_celery_beat --apply`` reading
        ``core/celery.py``; this test verifies the DB side of the
        migration is in sync with the source-of-truth beat schedule.
        Some test environments don't seed the row (CI fresh DB) — the
        check is conditional on the row existing.
        """
        from django_celery_beat.models import PeriodicTask
        row = PeriodicTask.objects.filter(
            name='generate-morning-brief-daily',
        ).first()
        if row is None:
            self.skipTest(
                "PeriodicTask 'generate-morning-brief-daily' not present "
                "in this DB; run `python manage.py sync_celery_beat "
                "--apply` to seed."
            )
        self.assertEqual(
            row.task, 'chief_of_staff_morning_brief_run',
            "PeriodicTask DB row task field drifted from PR 3.3 target. "
            "Either sync_celery_beat hasn't run since the flip, or the "
            "row was hand-edited.",
        )


class MorningBriefLaneWorkspaceThreadTests(TestCase):
    """Session 1234 D3 — ``_resolve_workflow_target_workspace_id`` returns
    the MB workspace_id for the ``morning_brief`` workflow so the agent
    router downstream uses it as the deliverable home for every step.

    Pre-fix: ``execute()`` did not seed ``context['workspace_id']``, so
    each step's delegate agent fell through agent_router's
    active-workspace fallback (core/agent_router.py:1083-1121). Symptom:
    2026-06-25 first fire — SystemIntelligenceAgent/COOAgent/
    TrendAnalysisAgent deliverables landed in the user's
    most-recent-active workspace (Session 1231 E2E) instead of the
    Morning Brief workspace, even after the MB workspace was
    materialized by step 8.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"test_d3_{uuid.uuid4().hex[:8]}",
            password='test',
        )
        self.agent = WorkflowOrchestrationAgent(user=self.user)

    def test_morning_brief_materializes_and_returns_workspace_id(self):
        """morning_brief workflow returns str(mb_ws.id) on first call."""
        self.assertEqual(
            ProjectWorkspace.objects.filter(
                user=self.user, name='Morning Brief',
            ).count(),
            0,
            "Pre-condition: no MB workspace yet.",
        )

        ws_id = self.agent._resolve_workflow_target_workspace_id('morning_brief')

        # MB workspace materialized
        mb_ws = ProjectWorkspace.objects.get(
            user=self.user, name='Morning Brief',
        )
        self.assertEqual(ws_id, str(mb_ws.id))

    def test_morning_brief_second_call_is_idempotent(self):
        """Second call returns same id; no second workspace created."""
        first = self.agent._resolve_workflow_target_workspace_id('morning_brief')
        second = self.agent._resolve_workflow_target_workspace_id('morning_brief')
        self.assertEqual(first, second)
        self.assertEqual(
            ProjectWorkspace.objects.filter(
                user=self.user, name='Morning Brief',
            ).count(),
            1,
            "Idempotent: only one MB workspace per user.",
        )

    def test_non_morning_brief_workflow_returns_none(self):
        """Other workflows return None (no MB workspace materialized)."""
        result = self.agent._resolve_workflow_target_workspace_id('business_research')
        self.assertIsNone(result)
        self.assertEqual(
            ProjectWorkspace.objects.filter(
                user=self.user, name='Morning Brief',
            ).count(),
            0,
            "Non-MB workflow MUST NOT create a Morning Brief workspace.",
        )

    def test_no_user_returns_none_gracefully(self):
        """user=None → returns None; no crash, no workspace.

        Mutates the existing agent's ``self.user`` to None instead of
        constructing with ``user=None`` because BaseContentAgent.__init__
        unconditionally reads ``user.username`` in a log line (pre-existing
        behavior, out of D3 scope). The runtime path that matters here is
        ``_resolve_workflow_target_workspace_id`` reading ``self.user``,
        which is what we're guarding.
        """
        self.agent.user = None
        result = self.agent._resolve_workflow_target_workspace_id('morning_brief')
        self.assertIsNone(result)
        self.assertEqual(
            ProjectWorkspace.objects.filter(name='Morning Brief').count(),
            0,
        )

    def test_execute_seeds_context_workspace_id_before_step_loop(self):
        """``execute()`` writes context['workspace_id'] before any step runs.

        Source-level guard: scans the ``execute()`` method body for the
        contract — calls ``_resolve_workflow_target_workspace_id`` and
        assigns its truthy return value into ``context['workspace_id']``
        BEFORE the ``for step_def in steps:`` loop. Avoids end-to-end
        run (full execute() touches DB-backed telemetry that serializes
        ``self.user`` and trips JSON encoder).
        """
        import inspect
        from core.services.workflow_orchestration_agent import (
            WorkflowOrchestrationAgent as WOA,
        )
        src = inspect.getsource(WOA.execute)
        helper_pos = src.find('_resolve_workflow_target_workspace_id')
        seed_pos = src.find("context['workspace_id'] = target_ws_id")
        loop_pos = src.find('for step_def in steps:')

        self.assertGreater(
            helper_pos, -1,
            "execute() must call _resolve_workflow_target_workspace_id.",
        )
        self.assertGreater(
            seed_pos, -1,
            "execute() must assign target_ws_id into context['workspace_id'].",
        )
        self.assertGreater(
            loop_pos, -1,
            "execute() must contain the step-loop sentinel.",
        )
        self.assertLess(
            helper_pos, loop_pos,
            "_resolve_workflow_target_workspace_id must be called BEFORE "
            "the step loop, otherwise lane delegates miss the seeding.",
        )
        self.assertLess(
            seed_pos, loop_pos,
            "context['workspace_id'] assignment must be BEFORE the step loop.",
        )

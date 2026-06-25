"""Session 1233 Sub-step C — workspace materialization + daily beat task.

Three test classes:

1. ``MorningBriefWorkspaceMaterializationTests`` —
   ``_get_or_create_morning_brief_workspace`` is idempotent, scoped per
   user, and gracefully handles None user.
2. ``MorningBriefDeliverableWorkspaceLinkTests`` —
   ``_execute_create_morning_brief_deliverable_step`` writes the
   deliverable's ``workspace_id`` to the materialized workspace.
3. ``GenerateMorningBriefDailyTaskTests`` — the
   ``generate_morning_brief_daily`` shared task dispatches the
   workflow, returns structured telemetry, and gracefully handles
   missing user.

Run::

    python manage.py test core.tests.test_morning_brief_sub_step_c -v2
"""

import uuid
from unittest.mock import MagicMock, patch

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


class GenerateMorningBriefDailyTaskTests(TestCase):
    """Session 1233 Sub-step C — daily beat task dispatch + telemetry."""

    def setUp(self):
        # Sole platform user per CLAUDE.md § Session 1098 fix.
        self.chris = User.objects.create_user(
            username='chris',
            password='test',
        )

    def test_task_with_no_user_id_looks_up_chris(self):
        """Default beat dispatch passes no user_id → task falls back
        to looking up 'chris'."""
        from core.tasks import generate_morning_brief_daily

        mock_result = {
            'success': True,
            'workflow': 'morning_brief',
            'context': {
                'rotation_slot': 'ai_infra_deep_dive',
                'lane_4_slot_used': 'ai_infra_deep_dive',
            },
            'step_results': [
                {'name': 'create_deliverable',
                 'result': {'deliverable_id': 'deliv-uuid-123'}},
            ],
        }
        with patch(
            'core.services.workflow_orchestration_agent.'
            'WorkflowOrchestrationAgent.execute',
            return_value=mock_result,
        ) as mock_execute:
            result = generate_morning_brief_daily()

        self.assertTrue(result['success'])
        self.assertEqual(result['workflow'], 'morning_brief')
        self.assertEqual(result['deliverable_id'], 'deliv-uuid-123')
        self.assertEqual(result['rotation_slot'], 'ai_infra_deep_dive')
        self.assertEqual(result['user_id'], str(self.chris.id))

        # Verify the workflow was dispatched with workflow='morning_brief'.
        mock_execute.assert_called_once()
        call_kwargs = mock_execute.call_args.kwargs
        self.assertEqual(call_kwargs.get('workflow'), 'morning_brief')
        self.assertIn('Morning Brief —', call_kwargs.get('topic', ''))

    def test_task_returns_error_when_no_user_found(self):
        """Missing user → task returns failure (does not raise)."""
        from core.tasks import generate_morning_brief_daily
        # User chris from setUp is the only test user; pass a non-existent UUID.
        result = generate_morning_brief_daily(
            user_id='00000000-0000-0000-0000-000000000000',
        )
        self.assertFalse(result['success'])
        self.assertIn('no target user found', result['error'])

    def test_task_returns_failure_telemetry_when_workflow_raises(self):
        """Workflow exception → task returns failure dict, does not
        propagate (beat task should not crash the worker)."""
        from core.tasks import generate_morning_brief_daily

        with patch(
            'core.services.workflow_orchestration_agent.'
            'WorkflowOrchestrationAgent.execute',
            side_effect=RuntimeError("simulated workflow crash"),
        ):
            result = generate_morning_brief_daily()

        self.assertFalse(result['success'])
        self.assertIn('RuntimeError', result['error'])
        self.assertIn('simulated workflow crash', result['error'])
        self.assertEqual(result['workflow'], 'morning_brief')


class MorningBriefBeatScheduleRegistrationTests(TestCase):
    """Source-level guard: the beat schedule has the morning_brief entry."""

    def test_generate_morning_brief_daily_registered_in_beat_schedule(self):
        from core.celery import app
        schedule = app.conf.beat_schedule
        self.assertIn('generate-morning-brief-daily', schedule)
        entry = schedule['generate-morning-brief-daily']
        self.assertEqual(
            entry['task'], 'core.tasks.generate_morning_brief_daily',
        )
        # Crontab must fire at 7:00 AM Denver per spec § Scheduling.
        from celery.schedules import crontab
        sched = entry['schedule']
        self.assertIsInstance(sched, crontab)
        # crontab.hour and crontab.minute are frozensets of ints
        self.assertEqual(sched.hour, {7})
        self.assertEqual(sched.minute, {0})

    def test_generate_morning_brief_daily_in_local_deny_tasks(self):
        """Per Session 1233 Sub-step C: production-only on Railway.
        Local cost (5+ LLM calls per fire) is not warranted."""
        from core.management.commands.add_critical_celery_tasks import (
            LOCAL_DENY_TASKS,
        )
        self.assertIn('generate-morning-brief-daily', LOCAL_DENY_TASKS)

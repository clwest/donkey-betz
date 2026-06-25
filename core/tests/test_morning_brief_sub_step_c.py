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
        to looking up 'chris'.

        Session 1234 D2.telemetry: mock_result uses the ACTUAL workflow
        result shape (``steps`` key, per-step ``result`` dict carrying
        the handler's return). Pre-fix this test passed by accident
        because both the beat task AND the mock used the wrong
        ``step_results`` + ``context`` keys.
        """
        from core.tasks import generate_morning_brief_daily

        mock_result = {
            'success': True,
            'workflow': 'morning_brief',
            'steps': [
                {'name': 'rotation_slot_resolve',
                 'result': {
                     'success': True,
                     'rotation_slot': 'ai_infra_deep_dive',
                     'reason': 'weekday_default:0',
                 }},
                {'name': 'lane_4_rotating_focus',
                 'result': {
                     'success': True,
                     'output': 'lane 4 text',
                     'slot_used': 'ai_infra_deep_dive',
                     'agent_name': 'ResearchAgent',
                 }},
                {'name': 'create_deliverable',
                 'result': {
                     'success': True,
                     'deliverable_id': 'deliv-uuid-123',
                     'workspace_id': 'ws-uuid-456',
                     'title': 'Morning Brief — 2026-06-25',
                 }},
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
        self.assertEqual(result['workspace_id'], 'ws-uuid-456')
        self.assertEqual(result['rotation_slot'], 'ai_infra_deep_dive')
        self.assertEqual(result['lane_4_slot_used'], 'ai_infra_deep_dive')
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

    def test_task_raises_when_workflow_returns_failure(self):
        """Session 1234 D1 fail-loud (Rigby-ratified).

        The 2026-06-25 first-fire postmortem: ``execute()`` returned
        ``{'success': False, 'step_results': [...lane_4 failed...]}``
        normally (no exception). The beat task then returned a
        success-False dict to Celery, which recorded SUCCESS.
        Monitoring saw a clean green run. Workflow had collapsed at
        Step 5 with deliverable_id=None.

        After D1: workflow.success=False MUST raise so Celery records
        FAILURE. Test guards that contract. See
        feedback_factory_silent_none_footgun.md.
        """
        from core.tasks import generate_morning_brief_daily

        # Replays the exact failure shape from task 9d00907a-…
        # Session 1234 D2.telemetry: uses ``steps`` key (the actual
        # _compile_final_result return shape), not ``step_results``.
        mock_result = {
            'success': False,
            'workflow': 'morning_brief',
            'steps': [
                {'name': 'rotation_slot_resolve',
                 'result': {
                     'success': True,
                     'rotation_slot': 'gtm_pipeline_health',
                     'reason': 'weekday_default:3',
                 }},
                {'name': 'lane_1_platform_readiness',
                 'result': {'success': True}},
                {'name': 'lane_2_build_focus',
                 'result': {'success': True}},
                {'name': 'lane_3_competitive_landscape',
                 'result': {'success': True}},
                {'name': 'lane_4_rotating_focus',
                 'result': {
                     'success': False,
                     'error': "Lane 4 agent 'OpportunityPipelineAgent' "
                              "reported failure for slot 'gtm_pipeline_health': "
                              "no error/message/output",
                     'slot_used': 'gtm_pipeline_health',
                     'agent_name': 'OpportunityPipelineAgent',
                 }},
            ],
        }
        with patch(
            'core.services.workflow_orchestration_agent.'
            'WorkflowOrchestrationAgent.execute',
            return_value=mock_result,
        ):
            with self.assertRaises(RuntimeError) as cm:
                generate_morning_brief_daily()

        # Verify the raised exception carries the diagnostic info that the
        # 2026-06-25 first-fire was missing.
        msg = str(cm.exception)
        self.assertIn('lane_4_rotating_focus', msg)
        self.assertIn('OpportunityPipelineAgent', msg)

    def test_task_returns_success_when_workflow_succeeds(self):
        """Regression guard: the success path must still return a dict
        (do NOT raise) when the workflow completes successfully. Pairs
        with the D1 fail-loud raise to ensure the success branch wasn't
        accidentally caught by the failure branch."""
        from core.tasks import generate_morning_brief_daily

        mock_result = {
            'success': True,
            'workflow': 'morning_brief',
            'steps': [
                {'name': 'create_deliverable',
                 'result': {
                     'success': True,
                     'deliverable_id': 'deliv-uuid-456',
                 }},
            ],
        }
        with patch(
            'core.services.workflow_orchestration_agent.'
            'WorkflowOrchestrationAgent.execute',
            return_value=mock_result,
        ):
            result = generate_morning_brief_daily()

        self.assertTrue(result['success'])
        self.assertEqual(result['deliverable_id'], 'deliv-uuid-456')


class MorningBriefBeatTaskTelemetryTests(TestCase):
    """Session 1234 D2.telemetry — beat task reads correct workflow keys.

    The 2026-06-25 final D2 verification (task 56be98e7-…) shipped a
    real brief end-to-end BUT the beat task return reported
    ``deliverable_id=None`` because the orchestrator's
    ``_compile_final_result`` sets ``result['steps']`` (not
    ``'step_results'``) and does not include a top-level ``'context'``
    key. Pre-fix the beat task read both wrong keys, so every telemetry
    field defaulted to None even when the underlying step results carried
    real values. These tests lock in the fix.
    """

    def setUp(self):
        self.chris = User.objects.create_user(
            username='chris', password='test',
        )

    def test_telemetry_uses_steps_key_not_step_results(self):
        """Replays the exact 2026-06-25 task 56be98e7-… shape.
        The actual workflow result uses 'steps', not 'step_results'.
        Pre-fix the beat task returned deliverable_id=None despite a
        real deliverable being created."""
        from core.tasks import generate_morning_brief_daily

        mock_result = {
            'success': True,
            'workflow': 'morning_brief',
            # ACTUAL _compile_final_result shape: 'steps' key.
            'steps': [
                {'name': 'rotation_slot_resolve',
                 'result': {
                     'success': True,
                     'rotation_slot': 'gtm_pipeline_health',
                     'reason': 'weekday_default:3',
                 }},
                {'name': 'lane_4_rotating_focus',
                 'result': {
                     'success': True,
                     'output': 'gtm bullets',
                     'slot_used': 'gtm_pipeline_health',
                     'agent_name': 'COOAgent',
                 }},
                {'name': 'create_deliverable',
                 'result': {
                     'success': True,
                     'deliverable_id': '88e2396b-aec3-4006-a1d0-7d94cba49d04',
                     'workspace_id': '19807888-862e-4a1a-b15d-f6c95b97e5a1',
                 }},
            ],
        }
        with patch(
            'core.services.workflow_orchestration_agent.'
            'WorkflowOrchestrationAgent.execute',
            return_value=mock_result,
        ):
            result = generate_morning_brief_daily()

        # All four telemetry fields MUST be populated from the steps.
        self.assertTrue(result['success'])
        self.assertEqual(result['deliverable_id'],
                         '88e2396b-aec3-4006-a1d0-7d94cba49d04',
                         "deliverable_id MUST be extracted from "
                         "steps[].result.deliverable_id of the "
                         "create_deliverable step.")
        self.assertEqual(result['workspace_id'],
                         '19807888-862e-4a1a-b15d-f6c95b97e5a1')
        self.assertEqual(result['rotation_slot'], 'gtm_pipeline_health',
                         "rotation_slot MUST come from the "
                         "rotation_slot_resolve step's result, not from "
                         "a non-existent top-level result['context'].")
        self.assertEqual(result['lane_4_slot_used'], 'gtm_pipeline_health',
                         "lane_4_slot_used MUST come from the "
                         "lane_4_rotating_focus step's result.slot_used.")

    def test_failure_telemetry_uses_steps_key(self):
        """The MORNING_BRIEF_FAILED log line + RuntimeError MUST surface
        the actual failed step name + error — pre-fix both fields
        defaulted to None because step_results was always empty."""
        from core.tasks import generate_morning_brief_daily

        mock_result = {
            'success': False,
            'workflow': 'morning_brief',
            'steps': [
                {'name': 'rotation_slot_resolve',
                 'result': {
                     'success': True,
                     'rotation_slot': 'sports_edge_scan',
                 }},
                {'name': 'lane_4_rotating_focus',
                 'result': {
                     'success': False,
                     'error': "no multi-bookmaker odds data available",
                     'slot_used': 'sports_edge_scan',
                     'agent_name': 'SharpActionDetector',
                 }},
            ],
        }
        with patch(
            'core.services.workflow_orchestration_agent.'
            'WorkflowOrchestrationAgent.execute',
            return_value=mock_result,
        ):
            with self.assertRaises(RuntimeError) as cm:
                generate_morning_brief_daily()

        # RuntimeError MUST name the actual failed step + error
        msg = str(cm.exception)
        self.assertIn('lane_4_rotating_focus', msg,
                      "RuntimeError MUST identify the failed step by name "
                      "(was 'None' pre-fix).")
        self.assertIn('no multi-bookmaker odds data', msg,
                      "RuntimeError MUST carry the failed step's error "
                      "string (was 'no error string captured' pre-fix).")


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

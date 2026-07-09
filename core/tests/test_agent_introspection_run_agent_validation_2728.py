"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch A tool 5
regression tests for `agent_introspection_tool` + `run_agent` (meta-tool).

Covers the F-AI-* / F-RA-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/agent_introspection_run_agent_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-RA-1: run_agent dispatch response now echoes `auto_followup` (effective
  value) and `follow_up_will_fire: bool` (composite of conversation_id truthy
  AND auto_followup not-False) so Rigby can detect the S1178 P2 auto-wake
  suppression MEMORY rule `feedback_auto_followup_false_suppresses_banner`
  crystallized. Applied to both `_handle_agent_tool` (tool_dispatcher.py,
  primary run_agent path) and `_handle_universal_agent` (td_handlers_agents.py,
  universal_agent_tool path — shares the silent behavior).
- F-RA-2 / F-RA-3: `_handle_universal_agent` silently substituted unknown
  agent_name → 'ResearchAgent' with WARN log only. Response now surfaces
  `agent_name_requested`, `agent_name_effective`, `agent_substituted`,
  and (when substitution fires) `substitution_reason` — mirrors the
  F-D-2/F-D-4 inference-envelope pattern approved at Batch A tool 1.
- F-AI-2: agent_introspection_tool.list ignored the schema-declared
  `limit` (default 20) and hard-coded `[:50]`. Now honors caller's
  limit up to the hard cap of 50, surfaces `limit_capped/requested_limit/
  effective_limit/hard_max` envelope (mirrors F-D-5).

Existing coverage NOT duplicated:
- Task-side auto_followup subscription lifecycle (S1178 P2 + S1180 P1) —
  covered in test_auto_followup_subscription.py.
- Agent-name canonicalization + AGENT_MAP membership — covered elsewhere
  via router tests.

Run::

    python manage.py test core.tests.test_agent_introspection_run_agent_validation_2728 -v2
"""
from __future__ import annotations

import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class _FakeAsyncResult:
    """Stand-in for the Celery AsyncResult returned by `.apply_async(...)`."""

    def __init__(self, task_id):
        self.id = task_id


# ─── F-RA-1: run_agent auto_followup + follow_up_will_fire surface ─────


class FRA1AutoFollowupSurface_HandleAgentTool(TestCase):
    """F-RA-1 — `_handle_agent_tool` (primary run_agent dispatch path) echoes
    `auto_followup` (effective) and `follow_up_will_fire: bool`."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'ai-ra-2728-{uuid.uuid4().hex[:8]}',
            email='ai-ra-2728@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )

    def _dispatch(self, payload, tool_name='research_and_create_tool'):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_agent_tool(  # type: ignore[attr-defined]
            tool_name=tool_name,
            payload=payload,
            user_id=self.user.id,
            trace_id='test-fra1-tool-2728',
        )

    def test_auto_followup_defaults_true_when_conv_id_present(self):
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra1-a'),
        ):
            result = self._dispatch({
                'task': 'do a small task',
                'conversation_id': 'pa-fra1-a',
            })
        self.assertTrue(result['auto_followup'])
        self.assertTrue(result['follow_up_will_fire'])

    def test_auto_followup_false_suppresses_follow_up(self):
        # MEMORY: feedback_auto_followup_false_suppresses_banner.
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra1-b'),
        ):
            result = self._dispatch({
                'task': 'forensic dispatch',
                'conversation_id': 'pa-fra1-b',
                'auto_followup': False,
            })
        self.assertFalse(result['auto_followup'])
        self.assertFalse(result['follow_up_will_fire'])

    def test_missing_conversation_id_suppresses_follow_up_regardless_of_auto_followup(self):
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra1-c'),
        ):
            result = self._dispatch({
                'task': 'no conv id',
                'auto_followup': True,
            })
        # auto_followup effective is True, but conversation_id absent → gate.
        self.assertTrue(result['auto_followup'])
        self.assertFalse(result['follow_up_will_fire'])

    def test_auto_followup_none_treated_as_default_true(self):
        # Regression guard: the task-side gate uses `is False` (not falsy).
        # None/missing must be treated as the default `True`.
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra1-d'),
        ):
            result = self._dispatch({
                'task': 'defaults',
                'conversation_id': 'pa-fra1-d',
                'auto_followup': None,
            })
        self.assertTrue(result['auto_followup'])
        self.assertTrue(result['follow_up_will_fire'])


# ─── F-RA-1 + F-RA-2 + F-RA-3: universal_agent_tool ────────────────────


class FRA123UniversalAgentSurface(TestCase):
    """F-RA-1 (auto_followup) + F-RA-2/F-RA-3 (substitution) on the
    `_handle_universal_agent` path."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'ai-ua-2728-{uuid.uuid4().hex[:8]}',
            email='ai-ua-2728@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_universal_agent(  # type: ignore[attr-defined]
            tool_name='universal_agent_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='test-fra123-2728',
        )

    def test_valid_agent_name_no_substitution(self):
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra2-a'),
        ):
            result = self._dispatch({
                'agent_name': 'ResearchAgent',
                'task': 'anything',
                'conversation_id': 'pa-fra2-a',
            })
        self.assertEqual(result['agent'], 'ResearchAgent')
        self.assertEqual(result['agent_name_requested'], 'ResearchAgent')
        self.assertEqual(result['agent_name_effective'], 'ResearchAgent')
        self.assertFalse(result['agent_substituted'])
        self.assertFalse(result['auto_routed'])
        self.assertNotIn('substitution_reason', result)
        # F-RA-1 fields present on this handler too.
        self.assertTrue(result['auto_followup'])
        self.assertTrue(result['follow_up_will_fire'])

    def test_unknown_agent_name_substitutes_to_research_agent(self):
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra2-b'),
        ):
            result = self._dispatch({
                # Hallucinated LLM-drift name; not in AGENT_MAP; no match in task.
                'agent_name': 'TotallyMadeUpAgent',
                'task': 'do something',
                'conversation_id': 'pa-fra2-b',
            })
        self.assertEqual(result['agent'], 'ResearchAgent')
        self.assertEqual(result['agent_name_requested'], 'TotallyMadeUpAgent')
        self.assertEqual(result['agent_name_effective'], 'ResearchAgent')
        self.assertTrue(result['agent_substituted'])
        self.assertIn('substitution_reason', result)
        self.assertIn('TotallyMadeUpAgent', result['substitution_reason'])
        # auto_routed remains False — a name WAS provided, it was just wrong.
        self.assertFalse(result['auto_routed'])

    def test_auto_routed_when_no_agent_name_given(self):
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra2-c'),
        ):
            result = self._dispatch({
                'task': 'some task',
                'conversation_id': 'pa-fra2-c',
            })
        # No agent_name requested → auto_routed=True; agent_substituted=False
        # because there was no request to substitute AGAINST.
        self.assertTrue(result['auto_routed'])
        self.assertFalse(result['agent_substituted'])
        self.assertIsNone(result['agent_name_requested'])
        self.assertEqual(result['agent_name_effective'], result['agent'])

    def test_universal_agent_auto_followup_false_surface(self):
        with patch(
            'core.tasks.execute_agent_task.apply_async',
            return_value=_FakeAsyncResult('celery-fra2-d'),
        ):
            result = self._dispatch({
                'agent_name': 'ResearchAgent',
                'task': 'forensic dispatch',
                'conversation_id': 'pa-fra2-d',
                'auto_followup': False,
            })
        self.assertFalse(result['auto_followup'])
        self.assertFalse(result['follow_up_will_fire'])


# ─── F-AI-2: agent_introspection_tool.list limit envelope ─────────────


class FAI2ListLimitCap(TestCase):
    """F-AI-2 — agent_introspection_tool.list honors caller limit up to
    the hard cap of 50; surfaces `limit_capped/requested_limit/effective_limit/
    hard_max` when caller exceeds."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'ai-fai2-2728-{uuid.uuid4().hex[:8]}',
            email='ai-fai2-2728@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_agent_introspection(  # type: ignore[attr-defined]
            tool_name='agent_introspection_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='test-fai2-2728',
        )

    def test_list_default_limit_20(self):
        result = self._dispatch({'action': 'list'})
        # `agents` may be shorter than 20 depending on test DB state; the key
        # invariant is that limit reports 20 and no cap signal fires.
        self.assertEqual(result['limit'], 20)
        self.assertNotIn('limit_capped', result)
        self.assertLessEqual(len(result.get('agents', [])), 20)

    def test_list_explicit_limit_5_honored(self):
        result = self._dispatch({'action': 'list', 'limit': 5})
        self.assertEqual(result['limit'], 5)
        self.assertNotIn('limit_capped', result)
        self.assertLessEqual(len(result.get('agents', [])), 5)

    def test_list_limit_over_cap_surfaces_signal(self):
        result = self._dispatch({'action': 'list', 'limit': 200})
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('requested_limit'), 200)
        self.assertEqual(result.get('effective_limit'), 50)
        self.assertEqual(result.get('hard_max'), 50)
        self.assertEqual(result['limit'], 50)
        self.assertLessEqual(len(result.get('agents', [])), 50)

    def test_list_limit_at_cap_no_signal(self):
        # Edge case: requested_limit exactly equals hard_max → no signal
        # (cap-signal is for over-cap only, per F-D-5 pattern).
        result = self._dispatch({'action': 'list', 'limit': 50})
        self.assertNotIn('limit_capped', result)
        self.assertEqual(result['limit'], 50)

    def test_stats_action_unaffected_by_limit(self):
        # Regression guard: stats action has no `agents` list and must not
        # emit any of the F-AI-2 envelope fields.
        result = self._dispatch({'action': 'stats'})
        self.assertNotIn('limit', result)
        self.assertNotIn('limit_capped', result)
        self.assertNotIn('agents', result)

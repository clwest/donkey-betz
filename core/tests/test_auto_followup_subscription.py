"""
Session 1178 Phase 2 c1 — auto-wake implicit follow-up subscription
==================================================================

Phase 2 ratified design (PR-2 of Session 1178): every PA-originated agent
dispatch auto-creates an armed AgentFollowupSubscription at execute_agent_task
entry, so the user sees a completion banner + Rigby-authored chat bubble
without Rigby needing to call schedule_followup explicitly.

These tests pin the four contract invariants ratified by Rigby on the
six-decision design card (D1=augment / D2=30s default / D3=PA-only /
D4=per-call opt-out / D5=one banner per agent / D6=at execute_agent_task
entry with DB-guaranteed dedupe):

1. PA dispatch with conv_id stamped → auto-sub created in 'armed' state.
2. Non-PA dispatch (conv_id NULL) → no auto-sub.
3. Explicit context['auto_followup']=False → no auto-sub (opt-out works).
4. Explicit schedule_followup race + implicit auto-sub for the same
   (execution, conversation_id) pair → exactly one row (unique_together
   guarantees dedupe at the DB level).

Run::

    python manage.py test core.tests.test_auto_followup_subscription -v2
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import (
    Agent,
    AgentExecution,
    AgentFollowupSubscription,
)
from core.tasks_agents import create_implicit_followup_subscription


User = get_user_model()


class AutoFollowupSubscriptionTests(TestCase):
    """Phase 2 invariants for create_implicit_followup_subscription()."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='auto-followup-test', email='auto@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.conversation_id = 'pa-auto-followup-test-001'

    # ---------------------------------------------------------------
    # (1) PA dispatch with conv_id → auto-sub created
    # ---------------------------------------------------------------
    def test_pa_dispatch_creates_armed_subscription(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        sub = create_implicit_followup_subscription(execution, context={})
        self.assertIsNotNone(sub)
        self.assertEqual(sub.execution_id, execution.id)
        self.assertEqual(sub.conversation_id, self.conversation_id)
        self.assertEqual(sub.state, AgentFollowupSubscription.STATE_ARMED)

        # TTL is 30s per D2.
        expected_expiry = timezone.now() + timedelta(seconds=30)
        delta_seconds = abs((sub.expires_at - expected_expiry).total_seconds())
        self.assertLess(delta_seconds, 5,
                        f'expires_at should be ~30s from now, drift={delta_seconds}s')

        # Persisted in DB.
        self.assertEqual(
            AgentFollowupSubscription.objects.filter(
                execution=execution, conversation_id=self.conversation_id,
            ).count(),
            1,
        )

    # ---------------------------------------------------------------
    # (2) Non-PA dispatch (conv_id NULL) → no auto-sub
    # ---------------------------------------------------------------
    def test_non_pa_dispatch_skips_subscription(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='autonomous-task',
            status='in_progress',
            # No conversation_id stamped — non-PA dispatch.
        )
        self.assertIsNone(execution.conversation_id)

        result = create_implicit_followup_subscription(execution, context={})
        self.assertIsNone(result)
        self.assertEqual(
            AgentFollowupSubscription.objects.filter(execution=execution).count(),
            0,
        )

    # ---------------------------------------------------------------
    # (3) auto_followup=False → no auto-sub (opt-out works)
    # ---------------------------------------------------------------
    def test_per_call_opt_out_skips_subscription(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='test-harness-dispatch',
            status='in_progress', conversation_id=self.conversation_id,
        )
        result = create_implicit_followup_subscription(
            execution, context={'auto_followup': False},
        )
        self.assertIsNone(result)
        self.assertEqual(
            AgentFollowupSubscription.objects.filter(execution=execution).count(),
            0,
        )

    def test_opt_out_only_triggers_on_false_not_falsy(self):
        # Defensive: context.get('auto_followup', True) is False must NOT match
        # None or missing key. Only literal False suppresses auto-sub.
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        sub = create_implicit_followup_subscription(
            execution, context={'auto_followup': None},  # NOT False
        )
        self.assertIsNotNone(sub)
        self.assertEqual(sub.state, AgentFollowupSubscription.STATE_ARMED)

    # ---------------------------------------------------------------
    # (4) Explicit schedule_followup + implicit auto-sub → exactly one row
    # ---------------------------------------------------------------
    def test_explicit_then_implicit_yields_one_row(self):
        """Explicit schedule_followup created first; implicit reuses it."""
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        # Simulate explicit schedule_followup having already armed the sub
        # with a custom TTL (120s, not the implicit default 30s).
        explicit_expiry = timezone.now() + timedelta(seconds=120)
        explicit_sub = AgentFollowupSubscription.objects.create(
            execution=execution,
            conversation_id=self.conversation_id,
            state=AgentFollowupSubscription.STATE_ARMED,
            expires_at=explicit_expiry,
        )

        # Now the implicit path runs. Dedupe must keep the explicit row.
        implicit_sub = create_implicit_followup_subscription(execution, context={})
        self.assertEqual(implicit_sub.id, explicit_sub.id,
                         'implicit path should reuse the existing row')
        self.assertEqual(
            AgentFollowupSubscription.objects.filter(
                execution=execution, conversation_id=self.conversation_id,
            ).count(),
            1,
            'unique_together (execution, conversation_id) prevents duplicate rows',
        )
        # Explicit TTL should be preserved (defaults dict doesn't update on reuse).
        explicit_sub.refresh_from_db()
        delta = abs((explicit_sub.expires_at - explicit_expiry).total_seconds())
        self.assertLess(delta, 5,
                        'explicit 120s TTL must not be clobbered by implicit 30s default')

    def test_implicit_then_explicit_yields_one_row(self):
        """Implicit auto-sub created first; explicit get_or_create reuses it."""
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        implicit_sub = create_implicit_followup_subscription(execution, context={})
        self.assertIsNotNone(implicit_sub)

        # Second call simulates a concurrent explicit subscribe path.
        # The model's unique_together must prevent the second insert.
        again = create_implicit_followup_subscription(execution, context={})
        self.assertEqual(again.id, implicit_sub.id)
        self.assertEqual(
            AgentFollowupSubscription.objects.filter(
                execution=execution, conversation_id=self.conversation_id,
            ).count(),
            1,
        )

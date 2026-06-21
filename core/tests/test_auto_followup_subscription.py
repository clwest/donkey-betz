"""
Session 1178 Phase 2 c1 — auto-wake implicit follow-up subscription
==================================================================

Phase 2 ratified design (PR-2 of Session 1178): every PA-originated agent
dispatch auto-creates an armed AgentFollowupSubscription at execute_agent_task
entry, so the user sees a completion banner + Rigby-authored chat bubble
without Rigby needing to call schedule_followup explicitly.

Session 1180 P1 update: auto-wake subs are execution-lifecycle-bound
(expires_at=NULL); fires when execution reaches terminal regardless of
runtime. Explicit schedule_followup(after_seconds=N) keeps its time-bounded
delayed-wake semantic unchanged. Decouples completion-wake from runtime
after live verify caught 60s TTL racing 67s ThinkingAgent in Pass B Cell 5.

These tests pin the contract invariants ratified by Rigby on the
six-decision design card (D1=augment / D2 superseded by Session 1180 P1
NULL-expiry / D3=PA-only / D4=per-call opt-out / D5=one banner per agent /
D6=at execute_agent_task entry with DB-guaranteed dedupe):

1. PA dispatch with conv_id stamped → auto-sub created in 'armed' state with
   expires_at=NULL (Session 1180 P1).
2. Non-PA dispatch (conv_id NULL) → no auto-sub.
3. Explicit context['auto_followup']=False → no auto-sub (opt-out works).
4. Explicit schedule_followup race + implicit auto-sub for the same
   (execution, conversation_id) pair → exactly one row (unique_together
   guarantees dedupe at the DB level).
5. P1 Test A — auto-wake NULL-expiry sub fires after old TTL window.
6. P1 Test B — explicit schedule_followup TTL still blocks fire when expired.

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
    # (1) PA dispatch with conv_id → auto-sub created with NULL expiry
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

        # Session 1180 P1: auto-wake subs are execution-lifecycle-bound, not
        # wall-clock-bound. expires_at=NULL means "fires when execution reaches
        # terminal, regardless of runtime". Decouples from the 30s/60s races
        # observed in Session 1178/1180 live verify.
        self.assertIsNone(
            sub.expires_at,
            'auto-wake subs must write expires_at=NULL (execution-lifecycle-bound)',
        )

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
        # with a custom TTL (300s, deliberately different from the implicit
        # default DEFAULT_TTL_SECONDS so the assert below can prove the
        # explicit window survives intact when implicit reuses the row).
        explicit_expiry = timezone.now() + timedelta(seconds=300)
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
        self.assertLess(
            delta, 5,
            f'explicit 300s TTL must not be clobbered by implicit '
            f'{AgentFollowupSubscription.DEFAULT_TTL_SECONDS}s default',
        )

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

    # ---------------------------------------------------------------
    # Session 1180 P1 Test A — NULL-expiry sub fires after old TTL window
    # ---------------------------------------------------------------
    def test_null_expiry_fires_on_completion_after_old_ttl_window(self):
        """Auto-wake sub with expires_at=NULL must fire even if the execution
        takes longer than the old DEFAULT_TTL_SECONDS to complete. This is the
        structural fix for the 60s-vs-67s race that blocked Session 1180 Pass B
        Cell 5: ThinkingAgent ran 67s, sub TTL was 60s, fire helper found
        state=armed but expires_at<now() so the armed→fired transition rowcount
        was 0, no group_send fanned out.
        """
        from unittest import mock
        from core.tasks_agents import fire_agent_followup_subscriptions

        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        sub = create_implicit_followup_subscription(execution, context={})
        self.assertIsNotNone(sub)
        self.assertIsNone(sub.expires_at, 'auto-wake sub must be NULL-expiry')

        # Simulate the execution taking 2x the old TTL (120s past sub creation).
        # The fire helper must still find this sub eligible.
        future = timezone.now() + timedelta(
            seconds=AgentFollowupSubscription.DEFAULT_TTL_SECONDS * 2,
        )
        with mock.patch('core.tasks_agents.get_channel_layer') as mock_layer, \
             mock.patch('core.tasks_agents.async_to_sync') as mock_a2s, \
             mock.patch('core.tasks_agents.timezone.now', return_value=future):
            mock_layer.return_value = mock.MagicMock()  # truthy channel layer with .group_send
            mock_a2s.return_value = mock.MagicMock()
            fire_agent_followup_subscriptions(execution)

        sub.refresh_from_db()
        self.assertEqual(
            sub.state, AgentFollowupSubscription.STATE_FIRED,
            'NULL-expiry sub must fire regardless of how long after creation',
        )
        self.assertIsNotNone(sub.fired_at)
        # group_send was called once (the broadcast happened).
        mock_a2s.assert_called_once()

    # ---------------------------------------------------------------
    # Session 1180 P1 Test B — explicit schedule_followup TTL still expires
    # ---------------------------------------------------------------
    def test_schedule_followup_time_bounded_expiry_still_blocks_fire(self):
        """Explicit schedule_followup keeps its delayed-wake TTL semantic.
        A sub written with non-NULL expires_at that has elapsed must NOT fire
        when the execution terminates — proving the two paths are independent.
        """
        from unittest import mock
        from core.tasks_agents import fire_agent_followup_subscriptions

        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        # Explicit path: 1-second TTL, then time advances past it.
        past_expiry = timezone.now() + timedelta(seconds=1)
        AgentFollowupSubscription.objects.create(
            execution=execution,
            conversation_id=self.conversation_id,
            state=AgentFollowupSubscription.STATE_ARMED,
            expires_at=past_expiry,
        )

        future = timezone.now() + timedelta(seconds=120)
        with mock.patch('core.tasks_agents.get_channel_layer') as mock_layer, \
             mock.patch('core.tasks_agents.async_to_sync') as mock_a2s, \
             mock.patch('core.tasks_agents.timezone.now', return_value=future):
            mock_layer.return_value = mock.MagicMock()
            mock_a2s.return_value = mock.MagicMock()
            fire_agent_followup_subscriptions(execution)

        sub = AgentFollowupSubscription.objects.get(
            execution=execution, conversation_id=self.conversation_id,
        )
        self.assertEqual(
            sub.state, AgentFollowupSubscription.STATE_ARMED,
            'time-bounded sub past expiry must stay armed (fire filter excludes it)',
        )
        self.assertIsNone(sub.fired_at)
        mock_a2s.assert_not_called()


class ExpireStaleSubscriptionBeatTaskTests(TestCase):
    """Session 1180 P1 — verify the beat cleanup task skips NULL-expiry rows
    so auto-wake (execution-lifecycle-bound) subs are never killed by hygiene.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='stale-cleanup-test', email='stale@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )

    def test_expire_stale_beat_task_skips_null_expiry(self):
        """expire_stale_followup_subscriptions must not transition NULL-expiry
        rows to STATE_EXPIRED — those are completion-bound and only fire/expire
        via the execution-terminal path.
        """
        from core.tasks import expire_stale_followup_subscriptions

        # One auto-wake sub (NULL expiry) + one explicit sub past TTL.
        null_exec = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-null',
            status='in_progress', conversation_id='pa-null-test',
        )
        null_sub = AgentFollowupSubscription.objects.create(
            execution=null_exec,
            conversation_id='pa-null-test',
            state=AgentFollowupSubscription.STATE_ARMED,
            expires_at=None,
        )

        explicit_exec = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-explicit',
            status='in_progress', conversation_id='pa-explicit-test',
        )
        explicit_sub = AgentFollowupSubscription.objects.create(
            execution=explicit_exec,
            conversation_id='pa-explicit-test',
            state=AgentFollowupSubscription.STATE_ARMED,
            expires_at=timezone.now() - timedelta(seconds=10),  # past TTL
        )

        result = expire_stale_followup_subscriptions()
        self.assertEqual(result, {'expired': 1}, 'only the explicit-TTL sub should expire')

        null_sub.refresh_from_db()
        explicit_sub.refresh_from_db()
        self.assertEqual(
            null_sub.state, AgentFollowupSubscription.STATE_ARMED,
            'NULL-expiry auto-wake sub must remain armed (immune to hygiene)',
        )
        self.assertEqual(
            explicit_sub.state, AgentFollowupSubscription.STATE_EXPIRED,
            'time-bounded sub past TTL must be expired by hygiene job',
        )


class CompletionRowIdempotencyTests(TestCase):
    """Session 1180 P1 bundled Cell 5 fix — verify create_completion_row is
    idempotent per (conversation_id, execution_id). Two browser tabs both
    receive the agent.completed group_send fanout and both call this helper;
    only one chat_conversations row must be persisted.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='completion-row-test', email='row@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )

    def test_agent_completion_row_dedup_per_execution_per_conversation(self):
        from core.consumers_pa_conversation import create_completion_row
        from core.models.conversations.models import ChatConversation

        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='completed',
            conversation_id='pa-dedup-test',
            completed_at=timezone.now(),
        )

        kwargs = dict(
            user=self.user,
            conversation_id='pa-dedup-test',
            execution_id=str(execution.id),
            agent_name='ResearchAgent',
            status='completed',
            completed_at=timezone.now().isoformat(),
            error_signature=None,
            artifact_pointers={},
            assistant_response='ResearchAgent completed',
        )

        # First call: writes the row.
        row1 = create_completion_row(**kwargs)
        # Second call (simulates a second tab's consumer firing on same group_send).
        row2 = create_completion_row(**kwargs)

        # Both calls return the SAME row id; only one row exists in DB.
        self.assertEqual(row1.id, row2.id, 'second call must reuse the first row')
        self.assertEqual(
            ChatConversation.objects.filter(
                conversation_id='pa-dedup-test',
                metadata__contains={'kind': 'agent_completion'},
            ).count(),
            1,
            'idempotency: only one completion row per (conversation_id, execution_id)',
        )

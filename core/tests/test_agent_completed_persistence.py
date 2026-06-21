"""
Session 1175 PR-2b-2 — server-side ChatConversation persistence on agent.completed
================================================================================

PR-2a's ``PAConversationConsumer.agent_completed`` only emitted a WebSocket
event; the load-bearing Rigby-authored chat bubble didn't survive page
refresh. PR-2b-2 extends the handler to ALSO persist a ChatConversation row
via three sync helpers (split out for direct unit-testability):

- ``compose_completion_body`` — pure: text Rigby would render
- ``check_background_completion`` — DB: stricter "user moved on" detector
- ``create_completion_row`` — DB: writes the assistant-bubble row

Tests cover Rigby's PR-2b-2 ratification asks (Session 1175 implementation
thread):

1. Subscribe + completion → ChatConversation row created with
   assistant_response containing agent name + status + execution_id.
2. Subscribe after completion (terminal-at-subscribe) → row still created
   once; dedupe holds.
3. User sends a message after subscribing → completion row is prefixed
   "Background completion: ".
4. Prior agent_completion rows in same conversation do NOT trigger the
   background-completion tag (the metadata.kind exclusion).

Run::

    python manage.py test core.tests.test_agent_completed_persistence -v2
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.consumers_pa_conversation import (
    check_background_completion,
    compose_completion_body,
    create_completion_row,
)
from core.models.conversations.models import ChatConversation
from core.models_unified_system import (
    Agent,
    AgentExecution,
    AgentFollowupSubscription,
)


User = get_user_model()


class ComposeCompletionBodyTests(TestCase):
    """Pure-function shape and idempotent prefix."""

    def test_completed_status_renders_agent_name_and_execution_id(self):
        body = compose_completion_body(
            execution_id='exec-abc', agent_name='ResearchAgent', status='completed',
            error_signature=None, artifact_pointers={}, is_background=False,
        )
        self.assertIn('ResearchAgent', body)
        self.assertIn('exec-abc', body)
        self.assertIn('finished', body)
        self.assertNotIn('Background completion', body)

    def test_failed_status_includes_error_signature(self):
        body = compose_completion_body(
            execution_id='exec-fail', agent_name='WorkflowAgent', status='failed',
            error_signature='ToolDispatcherTimeout', artifact_pointers={},
            is_background=False,
        )
        self.assertIn('WorkflowAgent', body)
        self.assertIn('failed', body)
        self.assertIn('ToolDispatcherTimeout', body)

    def test_artifact_pointers_render_inline(self):
        body = compose_completion_body(
            execution_id='exec-art', agent_name='ContentWriterAgent', status='completed',
            error_signature=None,
            artifact_pointers={'deliverable_ids': ['d1', 'd2'], 'media_ids': []},
            is_background=False,
        )
        self.assertIn('Artifacts', body)
        self.assertIn('d1', body)
        self.assertIn('d2', body)
        # Empty media_ids list should not render an empty bullet.
        self.assertNotIn('media ids:', body.lower())

    def test_background_prefix_added_when_flag_true(self):
        body = compose_completion_body(
            execution_id='exec-bg', agent_name='ResearchAgent', status='completed',
            error_signature=None, artifact_pointers={}, is_background=True,
        )
        self.assertTrue(body.startswith('Background completion: '))

    def test_background_prefix_idempotent_on_rerun(self):
        # Pure-function: calling twice with the same is_background=True input
        # yields the same body (the prefix is added by THIS call, never by
        # reading the prior body).
        kwargs = dict(
            execution_id='exec-idem', agent_name='X', status='completed',
            error_signature=None, artifact_pointers={}, is_background=True,
        )
        body1 = compose_completion_body(**kwargs)
        body2 = compose_completion_body(**kwargs)
        self.assertEqual(body1, body2)
        # And it has exactly one prefix occurrence.
        self.assertEqual(body1.count('Background completion: '), 1)


class CheckBackgroundCompletionTests(TestCase):
    """Detector honors Rigby's stricter heuristic — user_message non-empty AND
    metadata.kind != 'agent_completion' AND created_at > subscription.created_at.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='bg-detect-test', email='bg@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.conversation_id = 'pa-bg-detect-xyz'
        self.execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='bg-test',
            status='in_progress', conversation_id=self.conversation_id,
        )
        self.sub = AgentFollowupSubscription.objects.create(
            execution=self.execution,
            conversation_id=self.conversation_id,
            state=AgentFollowupSubscription.STATE_ARMED,
            expires_at=timezone.now() + timedelta(seconds=60),
        )

    def test_no_user_messages_after_subscription_is_not_background(self):
        self.assertFalse(check_background_completion(
            conversation_id=self.conversation_id,
            execution_id=str(self.execution.id),
        ))

    def test_user_message_before_subscription_is_not_background(self):
        # Backdate created_at to before the subscription.
        msg = ChatConversation.objects.create(
            user=self.user, conversation_id=self.conversation_id,
            user_message='earlier hello', assistant_response='hi back',
            source='pa', platform='api',
        )
        ChatConversation.objects.filter(id=msg.id).update(
            created_at=self.sub.created_at - timedelta(seconds=10),
        )
        self.assertFalse(check_background_completion(
            conversation_id=self.conversation_id,
            execution_id=str(self.execution.id),
        ))

    def test_user_message_after_subscription_is_background(self):
        ChatConversation.objects.create(
            user=self.user, conversation_id=self.conversation_id,
            user_message='I moved on', assistant_response='',
            source='pa', platform='api',
        )
        self.assertTrue(check_background_completion(
            conversation_id=self.conversation_id,
            execution_id=str(self.execution.id),
        ))

    def test_prior_agent_completion_row_does_not_trigger_background(self):
        # Rigby's stricter heuristic: agent_completion follow-ups in this same
        # conversation must NOT count as "user moved on" — otherwise every
        # subsequent follow-up self-triggers the prefix.
        ChatConversation.objects.create(
            user=self.user, conversation_id=self.conversation_id,
            user_message='',  # follow-up row has empty user_message anyway,
            assistant_response='Agent X finished.',
            source='pa', platform='api',
            metadata={'kind': 'agent_completion', 'execution_id': 'other-exec'},
        )
        self.assertFalse(check_background_completion(
            conversation_id=self.conversation_id,
            execution_id=str(self.execution.id),
        ))

    def test_missing_subscription_is_not_background(self):
        # Defensive: detector must fail safe if no subscription row exists.
        self.assertFalse(check_background_completion(
            conversation_id=self.conversation_id,
            execution_id='not-real-id',
        ))


class CreateCompletionRowTests(TestCase):
    """The persisted row carries agent name + status + execution_id and renders
    as a Rigby (assistant) bubble — not a user bubble."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='create-row-test', email='cr@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.conversation_id = 'pa-create-row-789'
        self.execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='persist-test',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        self.sub = AgentFollowupSubscription.objects.create(
            execution=self.execution,
            conversation_id=self.conversation_id,
            state=AgentFollowupSubscription.STATE_FIRED,
            expires_at=timezone.now() + timedelta(seconds=60),
            fired_at=timezone.now(),
        )

    def test_row_persists_with_assistant_bubble_fields(self):
        body = "Agent **ResearchAgent** finished (execution `exec-1`)."
        row = create_completion_row(
            user=self.user, conversation_id=self.conversation_id,
            execution_id=str(self.execution.id), agent_name='ResearchAgent',
            status='completed', completed_at=timezone.now().isoformat(),
            error_signature=None, artifact_pointers={},
            assistant_response=body,
        )
        # Rigby bubble: assistant_response set, user_message empty.
        self.assertEqual(row.user_message, '')
        self.assertEqual(row.assistant_response, body)
        self.assertEqual(row.source, 'pa')
        self.assertEqual(row.conversation_id, self.conversation_id)
        # Subscription linkage in metadata.
        self.assertEqual(row.metadata['kind'], 'agent_completion')
        self.assertEqual(row.metadata['subscription_id'], str(self.sub.id))
        self.assertEqual(row.metadata['execution_id'], str(self.execution.id))
        self.assertEqual(row.metadata['agent_name'], 'ResearchAgent')
        self.assertEqual(row.metadata['status'], 'completed')

    def test_no_subscription_still_writes_row_with_null_subscription_id(self):
        # Subscription-less write (e.g., fire-after-expiry edge case) should still
        # create the row; subscription_id falls back to None in metadata.
        AgentFollowupSubscription.objects.all().delete()
        row = create_completion_row(
            user=self.user, conversation_id=self.conversation_id,
            execution_id=str(self.execution.id), agent_name='ResearchAgent',
            status='completed', completed_at='', error_signature=None,
            artifact_pointers={}, assistant_response='body',
        )
        self.assertIsNone(row.metadata['subscription_id'])

    def test_unauthenticated_user_raises_typed_error(self):
        # Session 1182 PR #2356 — the prior `user=user if (...) else None` silent
        # fallback was a footgun: chat_conversations.user_id is NOT NULL, so the
        # None case ALWAYS produced an IntegrityError downstream (harder to
        # debug, looked like infra/data issue). Now the helper enforces its
        # contract — caller MUST supply an authenticated user; anonymous /
        # None inputs raise AnonymousCompletionRowError early.
        from core.consumers_pa_conversation import AnonymousCompletionRowError

        class _Anon:
            is_authenticated = False

        with self.assertRaises(AnonymousCompletionRowError):
            create_completion_row(
                user=_Anon(), conversation_id=self.conversation_id,
                execution_id=str(self.execution.id), agent_name='X',
                status='completed', completed_at='', error_signature=None,
                artifact_pointers={}, assistant_response='body',
            )

    def test_none_user_raises_typed_error(self):
        # Same contract as above for the explicit None case.
        from core.consumers_pa_conversation import AnonymousCompletionRowError

        with self.assertRaises(AnonymousCompletionRowError):
            create_completion_row(
                user=None, conversation_id=self.conversation_id,
                execution_id=str(self.execution.id), agent_name='X',
                status='completed', completed_at='', error_signature=None,
                artifact_pointers={}, assistant_response='body',
            )


class ResolveCompletionUserTests(TestCase):
    """Session 1182 PR #2356 — fire helper attribution resolution.

    Reproduces the 24h-watch finding from Session 1182 open: PR #2352's
    server-side persist passed `getattr(execution_record, 'user', None)` which
    returned None for PA-originated ImageAgent dispatches → IntegrityError on
    chat_conversations.user_id NOT NULL → fail-open. The new resolver falls
    back to the conversation thread owner so the architectural intent of
    PR #2352 (decouple from WS consumer) holds even when execution.user is
    missing.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='resolve-user-test', email='ru@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ImageAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.conversation_id = 'pa-resolve-test-abc'

    def test_returns_execution_user_when_authenticated(self):
        from core.tasks_agents import _resolve_completion_user
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='fast-path',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        resolved = _resolve_completion_user(execution, self.conversation_id)
        self.assertEqual(resolved.pk, self.user.pk)

    def test_falls_back_to_conversation_owner_when_execution_user_missing(self):
        # Repro of Session 1182's 24h-watch finding. Execution.user=None
        # (the PA-originated ImageAgent path in normal operation). The
        # resolver should pick up the user from the conversation's prior
        # user-authored rows.
        from core.tasks_agents import _resolve_completion_user
        ChatConversation.objects.create(
            user=self.user, conversation_id=self.conversation_id,
            user_message='draw a cat', assistant_response='on it',
            source='pa', platform='api',
        )
        execution = AgentExecution.objects.create(
            agent=self.agent, user=None, task='no-attribution',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        resolved = _resolve_completion_user(execution, self.conversation_id)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.pk, self.user.pk)

    def test_returns_none_when_no_attribution_available(self):
        # No execution.user AND no prior conversation rows → resolver returns
        # None and the fire helper logs persist_skipped_missing_user instead
        # of hitting IntegrityError.
        from core.tasks_agents import _resolve_completion_user
        execution = AgentExecution.objects.create(
            agent=self.agent, user=None, task='orphan',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        resolved = _resolve_completion_user(execution, self.conversation_id)
        self.assertIsNone(resolved)

    def test_picks_latest_owner_when_multiple_rows_exist(self):
        # Deterministic ordering: latest row with a non-null user wins.
        # Use distinct users to confirm we pick the right one.
        from core.tasks_agents import _resolve_completion_user
        other_user = User.objects.create_user(
            username='resolve-other', email='other@example.com', password='x',
        )
        older = ChatConversation.objects.create(
            user=other_user, conversation_id=self.conversation_id,
            user_message='earlier turn', assistant_response='',
            source='pa', platform='api',
        )
        ChatConversation.objects.filter(id=older.id).update(
            created_at=timezone.now() - timedelta(hours=1),
        )
        ChatConversation.objects.create(
            user=self.user, conversation_id=self.conversation_id,
            user_message='most recent', assistant_response='',
            source='pa', platform='api',
        )
        execution = AgentExecution.objects.create(
            agent=self.agent, user=None, task='multi',
            status='completed', conversation_id=self.conversation_id,
            completed_at=timezone.now(),
        )
        resolved = _resolve_completion_user(execution, self.conversation_id)
        self.assertEqual(resolved.pk, self.user.pk)

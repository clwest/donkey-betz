"""Session 1227 PR3 — deliverable_tool `set_status` action.

Closes Session 1226 audit `e2964e4a-…` §4.6 item 4 — gives Rigby (and any
PA caller) a surgical, audited path to flip a deliverable's status from
`completed` back to `ready` (the unblock case) or forward from `ready` to
`completed`. All other transitions continue to go through `update`, which
is intentionally unaudited so set_status remains the "safe valve."

Stacks on PR2 (#2563) which stacked on PR1 (#2562).

Audit trail: leverages the existing `deliverable_status_signals.py`
post_save signal. Handler stashes `_transition_context` on the instance;
the signal writes a `DeliverableEvent(event_type='status_transition',
source='deliverable_tool.set_status', user_id=actor)` with
metadata={'from':..., 'to':..., 'direction':..., 'ctx': {reason,
actor_user_id, trace_id, source}}.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable, DeliverableEvent
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _set_status(user_id, payload):
    dispatcher = ToolDispatcher()
    return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
        tool_name='deliverable_tool',
        payload={'action': 'set_status', **payload},
        user_id=user_id,
        trace_id='test-set-status',
    )


class WhitelistTests(TestCase):
    """Only completed↔ready transitions are allowed."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-setstatus', password='x', is_staff=True,
        )
        self.completed = Deliverable.objects.create(
            title='S1227 SS completed probe', content='x' * 200,
            agent_name='Rigby', user=self.user, status='completed',
        )
        self.ready = Deliverable.objects.create(
            title='S1227 SS ready probe', content='x' * 200,
            agent_name='Rigby', user=self.user, status='ready',
        )
        self.draft = Deliverable.objects.create(
            title='S1227 SS draft probe', content='x' * 200,
            agent_name='Rigby', user=self.user, status='draft',
        )

    def test_completed_to_ready_with_reason_succeeds(self):
        result = _set_status(self.user.id, {
            'id': str(self.completed.id),
            'status': 'ready',
            'reason': 'work not actually done',
        })
        self.assertEqual(result['action'], 'set_status')
        self.assertEqual(result['from_status'], 'completed')
        self.assertEqual(result['to_status'], 'ready')
        self.assertEqual(result['reason'], 'work not actually done')
        self.completed.refresh_from_db()
        self.assertEqual(self.completed.status, 'ready')

    def test_ready_to_completed_no_reason_succeeds(self):
        result = _set_status(self.user.id, {
            'id': str(self.ready.id),
            'status': 'completed',
        })
        self.assertEqual(result['from_status'], 'ready')
        self.assertEqual(result['to_status'], 'completed')
        self.assertIsNone(result['reason'])  # not provided → None (not "")
        self.ready.refresh_from_db()
        self.assertEqual(self.ready.status, 'completed')

    def test_completed_to_ready_without_reason_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'id': str(self.completed.id),
                'status': 'ready',
            })
        self.assertIn('reason is required', str(ctx.exception))
        self.completed.refresh_from_db()
        self.assertEqual(self.completed.status, 'completed')  # no flip

    def test_target_blocked_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'id': str(self.completed.id),
                'status': 'blocked',
            })
        self.assertIn("status='ready' or status='completed'", str(ctx.exception))

    def test_draft_source_raises(self):
        """Current=draft is not in the whitelist for either direction."""
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'id': str(self.draft.id),
                'status': 'ready',
            })
        self.assertIn('completed→ready', str(ctx.exception))
        self.assertIn('ready→completed', str(ctx.exception))

    def test_reason_length_cap_enforced(self):
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'id': str(self.completed.id),
                'status': 'ready',
                'reason': 'x' * 501,
            })
        self.assertIn('≤500 chars', str(ctx.exception))


class IdAndTitleLookupTests(TestCase):
    """Id-first lookup; title allowed only when exactly one row resolves."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-ss-lookup', password='x', is_staff=True,
        )
        self.unique_completed = Deliverable.objects.create(
            title='Unique Title', content='x' * 200,
            agent_name='Rigby', user=self.user, status='completed',
        )
        # Two rows with the same title — title lookup MUST refuse to flip.
        for _ in range(2):
            Deliverable.objects.create(
                title='Shared Title', content='x' * 200,
                agent_name='Rigby', user=self.user, status='completed',
            )

    def test_unique_title_resolves(self):
        result = _set_status(self.user.id, {
            'title': 'Unique Title',
            'status': 'ready',
            'reason': 'unique-title path test',
        })
        self.assertEqual(result['from_status'], 'completed')
        self.assertEqual(result['to_status'], 'ready')

    def test_duplicate_title_refuses(self):
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'title': 'Shared Title',
                'status': 'ready',
                'reason': 'should fail',
            })
        self.assertIn('Multiple deliverables share title', str(ctx.exception))

    def test_missing_id_and_title_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'status': 'ready',
                'reason': 'no lookup key',
            })
        self.assertIn('id', str(ctx.exception))

    def test_unknown_id_raises(self):
        import uuid as _uuid
        with self.assertRaises(ValueError) as ctx:
            _set_status(self.user.id, {
                'id': str(_uuid.uuid4()),
                'status': 'ready',
                'reason': 'unknown id',
            })
        self.assertIn('not found', str(ctx.exception))


class AuditTrailTests(TestCase):
    """The post_save signal records the transition with reason + actor."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-ss-audit', password='x', is_staff=True,
        )
        self.d = Deliverable.objects.create(
            title='Audit Trail Probe', content='x' * 200,
            agent_name='Rigby', user=self.user, status='completed',
        )

    def test_audit_event_persists_with_reason_and_actor(self):
        result = _set_status(self.user.id, {
            'id': str(self.d.id),
            'status': 'ready',
            'reason': 'audit-trail test',
        })
        # Response surfaces the event id.
        self.assertIsNotNone(result['transition_event_id'])

        event = DeliverableEvent.objects.get(id=result['transition_event_id'])
        self.assertEqual(event.event_type, 'status_transition')
        self.assertEqual(event.source, 'deliverable_tool.set_status')
        self.assertEqual(str(event.user_id), str(self.user.id))
        self.assertEqual(event.metadata['from'], 'completed')
        self.assertEqual(event.metadata['to'], 'ready')
        self.assertEqual(event.metadata['direction'], 'backward')
        ctx = event.metadata.get('ctx', {})
        self.assertEqual(ctx.get('reason'), 'audit-trail test')
        self.assertEqual(ctx.get('actor_user_id'), str(self.user.id))
        self.assertEqual(ctx.get('source'), 'deliverable_tool.set_status')

    def test_transition_context_not_leaked_to_subsequent_save(self):
        """Signal must `delattr` the ephemeral context after consuming it."""
        _set_status(self.user.id, {
            'id': str(self.d.id),
            'status': 'ready',
            'reason': 'first flip',
        })
        # The Deliverable instance in memory now has no _transition_context.
        self.d.refresh_from_db()
        # An unrelated save of the same row must not pick up the prior ctx.
        self.d.title = 'Audit Trail Probe (renamed)'
        self.d.save(update_fields=['title'])
        # Only one status_transition event should exist (the original flip);
        # the title-only save did not change status so no new event.
        events = DeliverableEvent.objects.filter(
            deliverable=self.d, event_type='status_transition',
        )
        self.assertEqual(events.count(), 1)

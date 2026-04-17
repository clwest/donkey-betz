"""
Deliverable status-transition signal + COO rework gate — Session 1095.
========================================================================

Three things under test:

1. `classify_transition` — the direction classifier used by both the
   signal receiver (to tag events) and the gate evaluator (to count them)
2. The signal receivers — make sure status changes DO write
   DeliverableEvent rows, no-op paths DON'T, and errors don't break saves
3. The COO rework gate — `REWORK_RATE_HIGH` trips at threshold, backward
   transitions are counted from DeliverableEvent rows with the right
   metadata, top-transitions breakdown is populated

Run:
    python manage.py test core.tests.test_rework_signal_and_gate -v2
"""
from datetime import timedelta
from unittest.mock import patch

from django.test import TransactionTestCase, SimpleTestCase
from django.utils import timezone

from core.signals.deliverable_status_signals import classify_transition


# =============================================================================
# classify_transition — pure-logic unit tests
# =============================================================================

class ClassifyTransitionTests(SimpleTestCase):

    def test_forward_draft_to_ready(self):
        self.assertEqual(classify_transition('draft', 'ready'), 'forward')

    def test_forward_ready_to_published(self):
        self.assertEqual(classify_transition('ready', 'published'), 'forward')

    def test_backward_ready_to_draft(self):
        self.assertEqual(classify_transition('ready', 'draft'), 'backward')

    def test_backward_published_to_ready(self):
        self.assertEqual(classify_transition('published', 'ready'), 'backward')

    def test_backward_to_blocked(self):
        """Any status → blocked is explicit regression."""
        self.assertEqual(classify_transition('ready', 'blocked'), 'backward')
        self.assertEqual(classify_transition('published', 'blocked'), 'backward')

    def test_backward_to_rejected(self):
        self.assertEqual(classify_transition('ready', 'rejected'), 'backward')

    def test_terminal_to_archived(self):
        """Archival = terminal retirement, never counted as rework."""
        self.assertEqual(classify_transition('ready', 'archived'), 'terminal')
        self.assertEqual(classify_transition('published', 'archived'), 'terminal')

    def test_same_status(self):
        self.assertEqual(classify_transition('ready', 'ready'), 'same')

    def test_same_rank_different_status(self):
        """completed and published both rank 2 — lateral moves are 'same'."""
        self.assertEqual(classify_transition('completed', 'published'), 'same')

    def test_unknown_status_values(self):
        self.assertEqual(classify_transition('mystery1', 'mystery2'), 'unknown')
        self.assertEqual(classify_transition('ready', 'mystery'), 'unknown')

    def test_empty_strings_are_unknown(self):
        self.assertEqual(classify_transition('', 'ready'), 'unknown')
        self.assertEqual(classify_transition('ready', ''), 'unknown')


# =============================================================================
# Signal receiver integration — the real DB path
# =============================================================================

class DeliverableStatusSignalTests(TransactionTestCase):

    def _make_deliverable(self, status='ready'):
        from core.models_deliverables import Deliverable
        return Deliverable.objects.create(
            title='test',
            content='test content',
            agent_name='TestAgent',
            deliverable_type='document',
            status=status,
        )

    def test_backward_transition_logs_event(self):
        from core.models_deliverables import DeliverableEvent
        d = self._make_deliverable(status='ready')
        d.status = 'draft'
        d.save(update_fields=['status', 'updated_at'])
        events = DeliverableEvent.objects.filter(
            deliverable=d, event_type='status_transition'
        )
        self.assertEqual(events.count(), 1)
        ev = events.first()
        self.assertEqual(ev.metadata['from'], 'ready')
        self.assertEqual(ev.metadata['to'], 'draft')
        self.assertEqual(ev.metadata['direction'], 'backward')

    def test_forward_transition_logs_event(self):
        from core.models_deliverables import DeliverableEvent
        d = self._make_deliverable(status='draft')
        d.status = 'ready'
        d.save(update_fields=['status', 'updated_at'])
        ev = DeliverableEvent.objects.filter(
            deliverable=d, event_type='status_transition'
        ).first()
        self.assertIsNotNone(ev)
        self.assertEqual(ev.metadata['direction'], 'forward')

    def test_archive_logs_as_terminal_not_backward(self):
        from core.models_deliverables import DeliverableEvent
        d = self._make_deliverable(status='ready')
        d.status = 'archived'
        d.save(update_fields=['status', 'updated_at'])
        ev = DeliverableEvent.objects.filter(
            deliverable=d, event_type='status_transition'
        ).first()
        self.assertIsNotNone(ev)
        self.assertEqual(ev.metadata['direction'], 'terminal')

    def test_same_status_save_creates_no_event(self):
        """save with unchanged status must not write a transition event."""
        from core.models_deliverables import DeliverableEvent
        d = self._make_deliverable(status='ready')
        d.save(update_fields=['updated_at'])  # explicit no-status-change
        events = DeliverableEvent.objects.filter(
            deliverable=d, event_type='status_transition'
        )
        self.assertEqual(events.count(), 0)

    def test_new_deliverable_creation_no_event(self):
        """First save (create) should not log a transition — no 'from' state."""
        from core.models_deliverables import DeliverableEvent
        d = self._make_deliverable(status='ready')  # this is the create
        events = DeliverableEvent.objects.filter(
            deliverable=d, event_type='status_transition'
        )
        self.assertEqual(events.count(), 0)

    def test_unknown_status_transition_not_logged(self):
        """Defensive: if somehow status becomes a mystery value, classify
        as 'unknown' and skip logging rather than poison the metric."""
        from core.models_deliverables import DeliverableEvent
        d = self._make_deliverable(status='ready')
        d.status = 'mystery_state_xyz'
        d.save(update_fields=['status', 'updated_at'])
        events = DeliverableEvent.objects.filter(
            deliverable=d, event_type='status_transition'
        )
        self.assertEqual(events.count(), 0)

    def test_event_write_failure_does_not_break_save(self):
        """Signal receiver must never crash a Deliverable save, even if
        the event log write fails."""
        d = self._make_deliverable(status='ready')
        # Monkey-patch DeliverableEvent.objects.create to raise
        from core.models_deliverables import DeliverableEvent
        with patch.object(
            DeliverableEvent.objects, 'create',
            side_effect=RuntimeError('simulated DB failure'),
        ):
            d.status = 'draft'
            # Save must succeed despite event log failure
            d.save(update_fields=['status', 'updated_at'])

        # Verify deliverable was still saved
        d.refresh_from_db()
        self.assertEqual(d.status, 'draft')


# =============================================================================
# COO rework gate — end-to-end
# =============================================================================

class CooReworkGateTests(TransactionTestCase):

    def _make_deliverable(self, status='ready'):
        from core.models_deliverables import Deliverable
        return Deliverable.objects.create(
            title='test',
            content='test content',
            agent_name='TestAgent',
            deliverable_type='document',
            status=status,
        )

    def _collect_rework(self):
        from core.services.diagnostics.coo_daily import collect_metrics
        now = timezone.now()
        return collect_metrics(now, now - timedelta(hours=24), now - timedelta(days=7))['rework']

    def _eval_gate(self, rework_count: int) -> dict:
        from core.services.diagnostics.coo_daily import evaluate_gate
        # Build a minimum healthy metrics dict and override rework
        metrics = {
            'velocity': {
                'created_24h': 10, 'published_24h': 8,
                'created_7d_avg_daily': 10.0, 'published_7d_avg_daily': 9.0,
                'created_delta_pct': 0.0, 'published_delta_pct': 0.0,
            },
            'review_backlog': {
                'ready_count': 2, 'ready_p95_age_hours': 3.0,
                'ready_over_threshold_count': 0, 'ready_over_threshold_hours': 24,
                'oldest_ready_hours': 5.0, 'oldest_ready_top': [],
            },
            'action_items': {
                'pending_by_urgency': {}, 'pending_over_sla_by_urgency': {},
                'pending_total': 0, 'oldest_critical_hours': 0.0,
            },
            'initiatives': {
                'stuck_count': 0, 'stuck_hours_threshold': 72, 'stuck_top': [],
            },
            'gate_hang': {
                'pending_total': 0, 'new_24h': 0,
                'oldest_pending_hours': 0.0, 'top_pipelines': [],
            },
            'rework': {
                'backward_24h': rework_count,
                'backward_7d_avg_daily': 1.0,
                'top_transitions': [
                    {'from': 'ready', 'to': 'draft', 'count': rework_count},
                ] if rework_count > 0 else [],
            },
        }
        return evaluate_gate(metrics)

    def test_no_backward_transitions_gate_quiet(self):
        r = self._collect_rework()
        self.assertEqual(r['backward_24h'], 0)
        gate = self._eval_gate(0)
        self.assertNotIn('REWORK_RATE_HIGH', gate.get('reasons', []))

    def test_backward_transitions_counted(self):
        """Bounce 6 deliverables ready→draft, rework metric should be 6."""
        for i in range(6):
            d = self._make_deliverable(status='ready')
            d.status = 'draft'
            d.save(update_fields=['status', 'updated_at'])
        r = self._collect_rework()
        self.assertEqual(r['backward_24h'], 6)
        # Top transition should be ready→draft
        top = r['top_transitions'][0]
        self.assertEqual(top['from'], 'ready')
        self.assertEqual(top['to'], 'draft')
        self.assertEqual(top['count'], 6)

    def test_rework_gate_trips_at_threshold(self):
        """6 backward (above default COO_DIAG_REWORK_MIN=5) → REWORK_RATE_HIGH."""
        gate = self._eval_gate(6)
        self.assertIn('REWORK_RATE_HIGH', gate['reasons'])
        self.assertEqual(gate['severity'], 'high')
        # Details should mention the top transition
        detail_text = ' '.join(gate['reason_details'])
        self.assertIn('ready→draft', detail_text)

    def test_rework_gate_below_threshold_no_trip(self):
        gate = self._eval_gate(3)  # below default 5
        self.assertNotIn('REWORK_RATE_HIGH', gate.get('reasons', []))

    def test_forward_transitions_not_counted_as_rework(self):
        """Multiple draft→ready transitions should not contribute to rework."""
        for i in range(10):
            d = self._make_deliverable(status='draft')
            d.status = 'ready'
            d.save(update_fields=['status', 'updated_at'])
        r = self._collect_rework()
        self.assertEqual(r['backward_24h'], 0)

    def test_archival_not_counted_as_rework(self):
        """ready→archived is terminal, not backward."""
        for i in range(10):
            d = self._make_deliverable(status='ready')
            d.status = 'archived'
            d.save(update_fields=['status', 'updated_at'])
        r = self._collect_rework()
        self.assertEqual(r['backward_24h'], 0)

    def test_missing_rework_key_backward_compat(self):
        """Pre-Session-1095 metrics dicts (no 'rework' key) must not crash
        the gate evaluator."""
        from core.services.diagnostics.coo_daily import evaluate_gate
        metrics = {
            'velocity': {
                'created_24h': 10, 'published_24h': 8,
                'created_7d_avg_daily': 10.0, 'published_7d_avg_daily': 9.0,
                'created_delta_pct': 0.0, 'published_delta_pct': 0.0,
            },
            'review_backlog': {
                'ready_count': 2, 'ready_p95_age_hours': 3.0,
                'ready_over_threshold_count': 0, 'ready_over_threshold_hours': 24,
                'oldest_ready_hours': 5.0, 'oldest_ready_top': [],
            },
            'action_items': {
                'pending_by_urgency': {}, 'pending_over_sla_by_urgency': {},
                'pending_total': 0, 'oldest_critical_hours': 0.0,
            },
            'initiatives': {
                'stuck_count': 0, 'stuck_hours_threshold': 72, 'stuck_top': [],
            },
            # Deliberately omit 'rework' and 'gate_hang'
        }
        gate = evaluate_gate(metrics)  # must not raise
        self.assertNotIn('REWORK_RATE_HIGH', gate.get('reasons', []))


# =============================================================================
# Warming-window note (Rigby's (c) follow-up)
# =============================================================================

class ReworkWarmingWindowTests(TransactionTestCase):
    """When the status_transition event stream is < 7 days old, the rework
    section and gate detail must surface the warming state explicitly —
    operators must not mistake 'low rework' for 'no rework happening'."""

    def _collect(self):
        from core.services.diagnostics.coo_daily import collect_metrics
        now = timezone.now()
        return collect_metrics(now, now - timedelta(hours=24), now - timedelta(days=7))

    def test_no_events_yet_warming_active(self):
        """No DeliverableEvent rows → warming is active, no first_event_at."""
        m = self._collect()
        warming = m['rework']['warming']
        self.assertTrue(warming['active'])
        self.assertIsNone(warming['first_event_at'])
        self.assertEqual(warming['days_since_rollout'], 0.0)

    def test_recent_events_warming_active(self):
        """Events < 7 days old → warming active, first_event_at populated."""
        from core.models_deliverables import Deliverable, DeliverableEvent
        d = Deliverable.objects.create(
            title='t', content='x', agent_name='A', deliverable_type='document',
        )
        # Signal already wrote no events for a create. Write one directly
        # to simulate a fresh rollout history.
        DeliverableEvent.objects.create(
            deliverable=d,
            event_type='status_transition',
            source='test',
            metadata={'from': 'ready', 'to': 'draft', 'direction': 'backward'},
        )
        m = self._collect()
        warming = m['rework']['warming']
        self.assertTrue(warming['active'])
        self.assertIsNotNone(warming['first_event_at'])
        self.assertLess(warming['days_since_rollout'], 7)

    def test_old_events_warming_inactive(self):
        """Events >= 7 days old → warming is inactive (baseline is valid)."""
        from core.models_deliverables import Deliverable, DeliverableEvent
        d = Deliverable.objects.create(
            title='t', content='x', agent_name='A', deliverable_type='document',
        )
        old_event = DeliverableEvent.objects.create(
            deliverable=d,
            event_type='status_transition',
            source='test',
            metadata={'from': 'ready', 'to': 'draft', 'direction': 'backward'},
        )
        # Force the event's created_at backward past 7 days. auto_now_add
        # is respected by Django, so update with raw queryset.
        DeliverableEvent.objects.filter(pk=old_event.pk).update(
            created_at=timezone.now() - timedelta(days=10)
        )
        m = self._collect()
        warming = m['rework']['warming']
        self.assertFalse(warming['active'])
        self.assertGreaterEqual(warming['days_since_rollout'], 7)

    def test_renderer_shows_warming_note_when_active_with_events(self):
        from core.models_deliverables import Deliverable, DeliverableEvent
        from core.services.diagnostics.coo_daily import render_rework
        d = Deliverable.objects.create(
            title='t', content='x', agent_name='A', deliverable_type='document',
        )
        DeliverableEvent.objects.create(
            deliverable=d,
            event_type='status_transition',
            source='test',
            metadata={'from': 'ready', 'to': 'draft', 'direction': 'backward'},
        )
        m = self._collect()
        lines = render_rework(m, {})
        joined = '\n'.join(lines)
        self.assertIn('Rework instrumentation live since', joined)
        self.assertIn('baseline stabilizes after 7 full days', joined)

    def test_renderer_shows_warming_note_even_with_zero_backward(self):
        """Critical: warming state forces the section to render EVEN when
        backward_24h=0. Otherwise operators misread silence as health."""
        from core.services.diagnostics.coo_daily import render_rework
        m = self._collect()
        # No backward transitions in this test → backward_24h=0 BUT warming is active
        self.assertEqual(m['rework']['backward_24h'], 0)
        self.assertTrue(m['rework']['warming']['active'])
        lines = render_rework(m, {})
        self.assertGreater(len(lines), 0, 'Warming state must force section to render')
        joined = '\n'.join(lines)
        self.assertIn('baseline warming', joined)

    def test_renderer_omits_section_when_healthy_and_not_warming(self):
        """The only time the section is fully omitted: backward=0 AND warming over."""
        from core.models_deliverables import Deliverable, DeliverableEvent
        from core.services.diagnostics.coo_daily import render_rework
        d = Deliverable.objects.create(
            title='t', content='x', agent_name='A', deliverable_type='document',
        )
        old = DeliverableEvent.objects.create(
            deliverable=d,
            event_type='status_transition',
            source='test',
            metadata={'from': 'ready', 'to': 'ready', 'direction': 'forward'},
        )
        DeliverableEvent.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=10)
        )
        m = self._collect()
        # No backward events, warming inactive → section fully omitted
        self.assertEqual(m['rework']['backward_24h'], 0)
        self.assertFalse(m['rework']['warming']['active'])
        self.assertEqual(render_rework(m, {}), [])

    def test_gate_detail_uses_warming_phrasing_when_active(self):
        """When rework gate trips during warming window, the detail line
        uses the 'instrumentation live since' phrasing, not '7d avg'."""
        from core.services.diagnostics.coo_daily import evaluate_gate
        metrics = self._collect()
        # Force backward_24h >= 5 to trip the gate
        metrics['rework']['backward_24h'] = 6
        metrics['rework']['top_transitions'] = [
            {'from': 'ready', 'to': 'draft', 'count': 6}
        ]
        metrics['rework']['warming'] = {
            'active': True,
            'first_event_at': '2026-04-17T05:00:00+00:00',
            'days_since_rollout': 2.5,
        }
        gate = evaluate_gate(metrics)
        self.assertIn('REWORK_RATE_HIGH', gate['reasons'])
        detail = ' '.join(gate['reason_details'])
        self.assertIn('instrumentation live since 2026-04-17', detail)
        self.assertIn('baseline warming', detail)

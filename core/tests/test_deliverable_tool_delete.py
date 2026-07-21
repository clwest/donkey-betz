"""S2860 Ledger #10 — deliverable_tool.delete schema exposure + hardening.

The `delete` handler at `td_handlers_agents.py` has existed since
Session 1169 (`obj.delete()` hard delete), but was never exposed in
the `deliverable_tool` schema enum, so GPT-5.2 function calling could
not reach it. Rigby fell back to `content_tool.content_reject`
(soft-archive) for genuine hard-delete cleanup, surfaced during
S2859 post-merge E2E as Ledger candidate #10.

This session exposes the action + hardens it with:
  - two-factor gate via `require_write_authorization` (dry_run=false
    + confirm=true), matching the `bulk_archive` pattern.
  - `status='published'` guard (rejects by default; `allow_published=
    true` + non-empty `reason` is the explicit escape hatch).
  - dry-run preview surfacing cascade counts (exports_count /
    events_count / packet_items_count) so callers see the blast
    radius before executing.
  - pre-delete `logger.warning()` audit line (durable trail because
    `DeliverableEvent` CASCADEs on Deliverable.delete()).

Run::

    python manage.py test core.tests.test_deliverable_tool_delete -v2
"""

import logging
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import (
    ContentPacket,
    ContentPacketItem,
    Deliverable,
    DeliverableEvent,
    DeliverableExport,
)
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class DeliverableDeleteTests(TestCase):
    """Cover the S2860 exposed + hardened deliverable_tool.delete path."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'del-test-{uuid.uuid4().hex[:8]}',
            email='del@example.com',
            password='x',
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Delete Workspace',
            allow_autonomous_writes=True,
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        self.trace_id = str(uuid.uuid4())

    def _make_deliverable(self, **overrides):
        defaults = dict(
            title='Delete-test row',
            content='# Body\n\nSubstantial body. ' * 20,
            agent_name='Rigby',
            category='PA Created',
            deliverable_type='document',
            status='ready',
            user=self.user,
            workspace=self.workspace,
        )
        defaults.update(overrides)
        return Deliverable.objects.create(**defaults)

    def _dispatch(self, payload):
        return self.dispatcher._handle_deliverables(
            'deliverables_tool', payload, self.user.id, self.trace_id,
        )

    # ── Two-factor gate ────────────────────────────────────────────────

    def test_delete_defaults_to_dry_run_preview(self):
        """No dry_run / confirm passed → safe preview, row NOT deleted."""
        obj = self._make_deliverable()
        result = self._dispatch({'action': 'delete', 'id': str(obj.id)})

        self.assertEqual(result['action'], 'delete')
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['id'], str(obj.id))
        self.assertTrue(result['will_delete'])
        self.assertIn('DRY RUN', result['message'])
        self.assertTrue(Deliverable.objects.filter(id=obj.id).exists())

    def test_delete_dry_run_false_without_confirm_stays_preview(self):
        """dry_run=false alone → still preview (autofill defence)."""
        obj = self._make_deliverable()
        result = self._dispatch({
            'action': 'delete', 'id': str(obj.id), 'dry_run': False,
        })
        self.assertTrue(result['dry_run'])
        self.assertTrue(Deliverable.objects.filter(id=obj.id).exists())

    def test_delete_confirm_true_without_dry_run_stays_preview(self):
        """confirm=true alone → still preview (dry_run defaults true)."""
        obj = self._make_deliverable()
        result = self._dispatch({
            'action': 'delete', 'id': str(obj.id), 'confirm': True,
        })
        self.assertTrue(result['dry_run'])
        self.assertTrue(Deliverable.objects.filter(id=obj.id).exists())

    def test_delete_dry_run_false_and_confirm_true_executes(self):
        """Both flags set → row is permanently deleted."""
        obj = self._make_deliverable()
        obj_id = obj.id
        result = self._dispatch({
            'action': 'delete', 'id': str(obj_id),
            'dry_run': False, 'confirm': True,
        })
        self.assertFalse(result['dry_run'])
        self.assertEqual(result['id'], str(obj_id))
        self.assertFalse(Deliverable.objects.filter(id=obj_id).exists())
        self.assertIn('Permanently deleted', result['message'])

    # ── Cascade counts ────────────────────────────────────────────────

    def test_delete_dry_run_surfaces_cascade_counts(self):
        """Preview shows exports/events/packet_items cascade counts."""
        obj = self._make_deliverable()
        # Attach one of each cascading child.
        DeliverableExport.objects.create(
            deliverable=obj, user=self.user, export_format='pdf',
        )
        DeliverableEvent.objects.create(
            deliverable=obj, event_type='deliverable_saved',
            user=self.user, source='pa_tool',
        )
        packet = ContentPacket.objects.create(
            title='Packet A', created_by=self.user, workspace=self.workspace,
        )
        ContentPacketItem.objects.create(
            packet=packet, deliverable=obj, role='draft', order=1,
        )

        result = self._dispatch({'action': 'delete', 'id': str(obj.id)})
        self.assertEqual(result['cascades']['exports_count'], 1)
        # deliverable_saved event + any signal-driven events (e.g., an
        # implicit status_transition). Assert >= 1 so the test is stable
        # if the signal layer adds more event types later.
        self.assertGreaterEqual(result['cascades']['events_count'], 1)
        self.assertEqual(result['cascades']['packet_items_count'], 1)

    def test_delete_live_path_cascades_children(self):
        """obj.delete() cascades to exports / events / packet_items."""
        obj = self._make_deliverable()
        export = DeliverableExport.objects.create(
            deliverable=obj, user=self.user, export_format='pdf',
        )
        event = DeliverableEvent.objects.create(
            deliverable=obj, event_type='deliverable_saved',
            user=self.user, source='pa_tool',
        )
        packet = ContentPacket.objects.create(
            title='Packet B', created_by=self.user, workspace=self.workspace,
        )
        item = ContentPacketItem.objects.create(
            packet=packet, deliverable=obj, role='draft', order=1,
        )

        self._dispatch({
            'action': 'delete', 'id': str(obj.id),
            'dry_run': False, 'confirm': True,
        })

        self.assertFalse(Deliverable.objects.filter(id=obj.id).exists())
        self.assertFalse(DeliverableExport.objects.filter(id=export.id).exists())
        self.assertFalse(DeliverableEvent.objects.filter(id=event.id).exists())
        self.assertFalse(ContentPacketItem.objects.filter(id=item.id).exists())
        # Packet itself survives — only the item link cascades.
        self.assertTrue(ContentPacket.objects.filter(id=packet.id).exists())

    # ── Published guard ────────────────────────────────────────────────

    def test_delete_published_without_allow_returns_typed_error(self):
        """status='published' rows are rejected by default."""
        obj = self._make_deliverable(status='published')
        result = self._dispatch({
            'action': 'delete', 'id': str(obj.id),
            'dry_run': False, 'confirm': True,
        })
        self.assertFalse(result['ok'])
        self.assertEqual(
            result['error_code'], 'delete_published_requires_allow_published',
        )
        self.assertTrue(Deliverable.objects.filter(id=obj.id).exists())

    def test_delete_published_with_allow_missing_reason_returns_typed_error(self):
        """allow_published=true still requires non-empty reason."""
        obj = self._make_deliverable(status='published')
        result = self._dispatch({
            'action': 'delete', 'id': str(obj.id),
            'dry_run': False, 'confirm': True,
            'allow_published': True,
        })
        self.assertFalse(result['ok'])
        self.assertEqual(
            result['error_code'], 'delete_published_requires_reason',
        )
        self.assertTrue(Deliverable.objects.filter(id=obj.id).exists())

    def test_delete_published_with_allow_and_whitespace_reason_still_rejected(self):
        """`   ` reason is treated as empty after strip()."""
        obj = self._make_deliverable(status='published')
        result = self._dispatch({
            'action': 'delete', 'id': str(obj.id),
            'dry_run': False, 'confirm': True,
            'allow_published': True, 'reason': '   ',
        })
        self.assertEqual(
            result['error_code'], 'delete_published_requires_reason',
        )
        self.assertTrue(Deliverable.objects.filter(id=obj.id).exists())

    def test_delete_published_with_allow_and_reason_executes(self):
        """Full escape hatch → row is deleted."""
        obj = self._make_deliverable(status='published')
        obj_id = obj.id
        result = self._dispatch({
            'action': 'delete', 'id': str(obj_id),
            'dry_run': False, 'confirm': True,
            'allow_published': True,
            'reason': 'stale demo content past retention window',
        })
        self.assertFalse(result.get('dry_run'))
        self.assertEqual(result['id'], str(obj_id))
        self.assertEqual(
            result['reason'], 'stale demo content past retention window',
        )
        self.assertFalse(Deliverable.objects.filter(id=obj_id).exists())

    # ── Audit log line ────────────────────────────────────────────────

    def test_delete_writes_audit_log_line_before_delete(self):
        """Live path emits WARNING-level log line with full context."""
        obj = self._make_deliverable()
        obj_id = obj.id
        with self.assertLogs(
            'core.services.td_handlers_agents', level=logging.WARNING,
        ) as cm:
            self._dispatch({
                'action': 'delete', 'id': str(obj_id),
                'dry_run': False, 'confirm': True,
                'reason': 'cleanup smoke row',
            })
        self.assertTrue(
            any('[DELIVERABLE_DELETE]' in line for line in cm.output),
            msg=f'Expected DELIVERABLE_DELETE log line, got: {cm.output}',
        )
        matching = [line for line in cm.output if '[DELIVERABLE_DELETE]' in line]
        self.assertIn(str(obj_id), matching[0])
        self.assertIn('cleanup smoke row', matching[0])

    def test_delete_dry_run_does_not_emit_audit_log(self):
        """Preview must NOT write the delete audit line."""
        obj = self._make_deliverable()
        logger = logging.getLogger('core.services.td_handlers_agents')
        with patch.object(logger, 'warning') as mock_warning:
            self._dispatch({'action': 'delete', 'id': str(obj.id)})
        # Assert no call carried the DELIVERABLE_DELETE tag.
        for call in mock_warning.call_args_list:
            args = call.args if call.args else ()
            fmt = args[0] if args else ''
            self.assertNotIn('[DELIVERABLE_DELETE]', str(fmt))

"""
Session 1168 — PA deliverable create handler hardening regression tests.
=========================================================================

Bug #1 from chris-personal Known Bugs Queue (deliverable 3973c817):
``deliverable_tool.create`` / ``content_tool.deliverable_create`` crashed
with ``'NoneType' object has no attribute 'id'`` when the underlying
quality gate (``_should_create_deliverable``) rejected the input. The
factory silently returned ``None`` and the handler immediately did
``str(obj.id)``.

These tests cover:

    1. Layer A (caller hardening): when the factory returns None, the
       handler returns a structured ``deliverable_gated`` error dict
       instead of crashing.
    2. Layer B (caller correctness): the PA dispatcher now passes
       ``metadata['trigger_source'] = 'pa_tool'`` so legitimate
       PA-initiated short-content saves don't trip gate 3.

Run::

    python manage.py test core.tests.test_deliverable_create_gated -v2
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class DeliverableCreateGatedTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'gated-test-{uuid.uuid4().hex[:8]}',
            email='gated@example.com',
            password='x',
            is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user,
            name='Gated Test Workspace',
            allow_autonomous_writes=True,
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        self.trace_id = str(uuid.uuid4())

    # ── Layer A: caller hardening ───────────────────────────────────────

    def test_handler_returns_gated_dict_when_factory_returns_none(self):
        """When create_deliverable returns None (gate rejection), handler
        must return a structured 'deliverable_gated' error dict, not
        raise AttributeError on str(None.id)."""
        payload = {
            'action': 'create',
            'title': 'Real legitimate title',
            'content': 'Substantial content. ' * 30,
            'workspace_id': str(self.workspace.id),
        }
        with mock.patch(
            'core.services.deliverable_factory.create_deliverable',
            return_value=None,
        ):
            result = self.dispatcher._handle_deliverables(
                'deliverables_tool', payload, self.user.id, self.trace_id,
            )
        self.assertIsInstance(result, dict)
        self.assertEqual(result['action'], 'create')
        self.assertEqual(result['ok'], False)
        self.assertIsNone(result['id'])
        self.assertEqual(result['error_code'], 'deliverable_gated')
        self.assertEqual(result['reason_code'], 'unknown_gate')
        self.assertIn('reason_hint', result)
        self.assertIn('quality gate', result['human_message'])
        self.assertIsInstance(result['retry_suggestions'], list)
        self.assertEqual(result['trace_id'], self.trace_id)

    def test_handler_success_path_unchanged_when_factory_returns_object(self):
        """Sanity: success path still works. ok=True, real id, no gate fields."""
        payload = {
            'action': 'create',
            'title': 'Real legitimate title',
            'content': 'Substantial content. ' * 30,
            'workspace_id': str(self.workspace.id),
        }
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool', payload, self.user.id, self.trace_id,
        )
        self.assertEqual(result['action'], 'create')
        self.assertEqual(result['ok'], True)
        self.assertIsNotNone(result['id'])
        self.assertNotIn('error_code', result)
        self.assertNotIn('reason_code', result)

    # ── Layer B: caller correctness (trigger_source=pa_tool) ────────────

    def test_handler_passes_trigger_source_pa_tool_to_factory(self):
        """The PA create branch must pass metadata['trigger_source']='pa_tool'
        so legitimate short-content saves don't trip the factory's gate 3
        (min content length 300)."""
        payload = {
            'action': 'create',
            'title': 'Short PA save',
            'content': 'Brief but legit PA content.',
            'workspace_id': str(self.workspace.id),
        }
        captured_metadata = {}

        def _capture(*args, **kwargs):
            captured_metadata.update(kwargs.get('metadata') or {})
            # Mimic gate-rejected return — we don't care, we just want to
            # observe the metadata that the handler passed.
            return None

        with mock.patch(
            'core.services.deliverable_factory.create_deliverable',
            side_effect=_capture,
        ):
            self.dispatcher._handle_deliverables(
                'deliverables_tool', payload, self.user.id, self.trace_id,
            )
        self.assertEqual(captured_metadata.get('trigger_source'), 'pa_tool')
        # Pre-existing key still present for backwards compat
        self.assertEqual(captured_metadata.get('source'), 'pa_deliverables_tool')

    def test_short_pa_content_now_passes_factory_gate(self):
        """End-to-end: a short PA-initiated save (which would have tripped
        gate 3 before) now succeeds because trigger_source='pa_tool' is
        in the gate's allowlist."""
        payload = {
            'action': 'create',
            # Non-smoke-test title (gate 2 doesn't fire)
            'title': 'Quick PA note',
            # Under 300 chars — would have failed gate 3 pre-fix
            'content': 'Brief PA note that previously tripped the min-length gate.',
            'workspace_id': str(self.workspace.id),
        }
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool', payload, self.user.id, self.trace_id,
        )
        self.assertEqual(result.get('ok'), True, msg=result)
        self.assertIsNotNone(result.get('id'))

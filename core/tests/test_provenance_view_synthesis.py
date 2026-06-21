"""
Session 1185 PR-C bucket 2: Web-view provenance synthesis tests.
=================================================================

Companion to bucket 1 (`test_provenance_direct_synthesis.py`). Web views
have two different opt-in flavors per `docs/specs/deliverable_creation_paths.md`
§ Web views:

- **User-triggered web action** → `trigger_source='user_request'`
    - `core/views_workspace_templates.py:315` (workspace brief save)
- **Incident / autopilot / demo path** → `trigger_source='direct'`
    - `core/views_diagnostics.py:2389` (cockpit-operator incident)
    - `core/views_diagnostics.py:3338` (cockpit-autopilot incident)
    - `core/views_demo_pipeline.py:194` (demo run output)

Both flavors are members of `_PA_DIRECT_TRIGGERS` in the factory, so
both activate the same `_synthesize_pa_execution_receipt` path. These
tests prove the trigger-string values land and fire synthesis correctly
for non-PA agent_name (so the path is exercised independently of the
PA_IDENTITY branch).

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_view_synthesis -v2 --keepdb
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import AgentExecution
from core.services.deliverable_factory import create_deliverable
from core.services.deliverable_provenance import build_provenance_block


User = get_user_model()


class ViewSynthesisTests(TestCase):
    """PR-C bucket 2 contract — web view callsite patterns."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='prov-view', email='pv@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='View-Synthesis Test Workspace',
            allow_autonomous_writes=True,
        )

    def _create(self, agent_name, metadata, category='Test'):
        return create_deliverable(
            title=f'{agent_name} view output',
            content='## Body\n' + ('View-mode deliverable body. ' * 30),
            agent_name=agent_name,
            user=self.user,
            workspace_id=str(self.workspace.id),
            category=category,
            metadata=metadata,
        )

    # ── User-request flavor (workspace brief save) ────────────────────────
    def test_user_request_trigger_synthesizes_for_workspace_brief(self):
        """views_workspace_templates.py:315 pattern — agent_name='User' +
        trigger_source='user_request' must synthesize a receipt."""
        d = self._create(
            'User',
            {'trigger_source': 'user_request',
             'brief_version': True,
             'workspace_id': str(self.workspace.id)},
            category='Workspace Brief',
        )
        self.assertIsNotNone(d.parent_object_id,
                             'user_request opt-in must synthesize')
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

        receipt = AgentExecution.objects.filter(id=d.parent_object_id).first()
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.owner_agent, 'User')
        self.assertEqual(receipt.status, 'completed')

    # ── Direct flavor (cockpit-operator incident) ─────────────────────────
    def test_direct_trigger_synthesizes_for_cockpit_operator_incident(self):
        """views_diagnostics.py:2389 pattern — incident writes opt into
        synthesis with trigger_source='direct'."""
        d = self._create(
            'cockpit-operator',
            {'source_type': 'alert',
             'source_id': 'abc',
             'created_via': 'cockpit-remediation',
             'trigger_source': 'direct'},
            category='Incident',
        )
        self.assertIsNotNone(d.parent_object_id)
        receipt = AgentExecution.objects.get(id=d.parent_object_id)
        self.assertEqual(receipt.owner_agent, 'cockpit-operator')

    # ── Direct flavor (autopilot) ─────────────────────────────────────────
    def test_direct_trigger_synthesizes_for_cockpit_autopilot(self):
        """views_diagnostics.py:3338 pattern — autopilot incident note."""
        d = self._create(
            'cockpit-autopilot',
            {'source': 'autopilot',
             'reason': 'queue-pressure',
             'trigger_source': 'direct'},
            category='Incident',
        )
        self.assertIsNotNone(d.parent_object_id)
        self.assertEqual(
            AgentExecution.objects.get(id=d.parent_object_id).owner_agent,
            'cockpit-autopilot',
        )

    # ── Direct flavor (demo pipeline) ─────────────────────────────────────
    def test_direct_trigger_synthesizes_for_demo_pipeline(self):
        """views_demo_pipeline.py:194 pattern — demo path."""
        d = self._create(
            'DemoPipeline',
            {'demo_run': True,
             'demo_run_id': 'run-001',
             'demo_ttl_days': 7,
             'topic': 'test',
             'trigger_source': 'direct'},
            category='Demo Run',
        )
        self.assertIsNotNone(d.parent_object_id)

    # ── Read-layer surface ────────────────────────────────────────────────
    def test_user_request_surfaces_in_provenance_read_block(self):
        """End-to-end: workspace-brief shape → read helper exposes
        synthesized=true + trigger_source='user_request'."""
        d = self._create(
            'User',
            {'trigger_source': 'user_request',
             'workspace_id': str(self.workspace.id)},
            category='Workspace Brief',
        )
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertTrue(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'user_request')
        self.assertEqual(block['origin_execution_id'], str(d.parent_object_id))

    def test_direct_view_surfaces_in_provenance_read_block(self):
        """End-to-end: incident shape → read helper exposes
        synthesized=true + trigger_source='direct'."""
        d = self._create(
            'cockpit-operator',
            {'trigger_source': 'direct', 'source_id': 'abc'},
            category='Incident',
        )
        block = build_provenance_block(d)
        self.assertTrue(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'direct')

    # ── Negative: no opt-in still falls to legacy bucket ──────────────────
    def test_view_without_trigger_source_falls_to_legacy(self):
        """Proves the opt-in is the load-bearing knob: same agent_name
        without trigger_source still hits the soft-enforce WARN."""
        d = self._create(
            'cockpit-operator',
            {'source_id': 'no-opt-in'},
            category='Incident',
        )
        block = build_provenance_block(d)
        self.assertTrue(block['legacy_no_provenance'])
        self.assertIsNone(block['origin_execution_id'])

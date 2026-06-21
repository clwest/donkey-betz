"""
Session 1185 PR-C bucket 5: Other-tools provenance synthesis tests.
====================================================================

Final mechanical bucket of the Session 1184 caller sweep. Two callsites
per `docs/specs/deliverable_creation_paths.md` § Other tools:

1. `core/services/td_handlers_core.py:2906` — `competitor_comparison_tool`
   PA tool-dispatched export. Opt into synthesis with
   `trigger_source='pa_tool'` (per spec: "trace_id present but no
   execution"; PA-direct flavor).

2. `core/services/deliverable_append_service.py:374` — fallback for
   superseded initiative. **Already compliant** as of Session 1184 PR-A:
   passes `trigger_source='direct'` + `parent_execution_id`. Caller
   audit confirms only one production caller (`core/agents/base_agent.py:4331`)
   which already threads `execution_id=str(parent_exec_id)`. No change
   needed; documented here for completeness.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_other_tools_synthesis -v2 --keepdb
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import AgentExecution
from core.services.deliverable_factory import create_deliverable
from core.services.deliverable_provenance import build_provenance_block


User = get_user_model()


class OtherToolsSynthesisTests(TestCase):
    """PR-C bucket 5 — competitor_comparison_tool + append_service contract."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='prov-other', email='po@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Other-Tools Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )

    def _create(self, agent_name, metadata, category='Test'):
        return create_deliverable(
            title=f'{agent_name} other-tool output',
            content='## Body\n' + ('Other-tool deliverable body. ' * 30),
            agent_name=agent_name,
            user=self.user,
            workspace_id=str(self.workspace.id),
            category=category,
            metadata=metadata,
        )

    # ── competitor_comparison_tool ─────────────────────────────────────────
    def test_competitor_comparison_tool_synthesizes_via_pa_tool_trigger(self):
        """td_handlers_core.py:2906 pattern — competitor_comparison_tool is
        PA-dispatched; opt into synthesis with trigger_source='pa_tool'."""
        d = self._create(
            'competitor_comparison_tool',
            {'trigger_source': 'pa_tool',
             'comparison_id': 'cmp-001',
             'competitor_name': 'Acme Corp'},
            category='Competitive Intelligence',
        )
        self.assertIsNotNone(d.parent_object_id, 'pa_tool opt-in must synthesize')
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

        receipt = AgentExecution.objects.filter(id=d.parent_object_id).first()
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.owner_agent, 'competitor_comparison_tool')
        self.assertEqual(receipt.status, 'completed')

    def test_competitor_comparison_provenance_block_surfaces_pa_tool(self):
        """End-to-end read: trigger_source='pa_tool' + synthesized=true land
        in the provenance block for downstream chain-of-custody reads."""
        d = self._create(
            'competitor_comparison_tool',
            {'trigger_source': 'pa_tool', 'comparison_id': 'cmp-002'},
            category='Competitive Intelligence',
        )
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertTrue(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'pa_tool')

    # ── deliverable_append_service fallback (already compliant) ────────────
    def test_append_service_fallback_is_already_wired(self):
        """deliverable_append_service.py:374 was already compliant since
        Session 1184 PR-A. Re-prove the existing contract here so the
        bucket-5 PR carries explicit coverage for it (no code change in
        this PR — just regression-net)."""
        d = self._create(
            'EditorAgent',  # any agent — fallback uses caller's agent_name
            {'trigger_source': 'direct',
             'superseded_from_deliverable_id': 'd-xyz',
             'call_id': 'c-001'},
            category='Superseded',
        )
        self.assertIsNotNone(d.parent_object_id,
                             'direct opt-in synthesizes the receipt')
        block = build_provenance_block(d)
        self.assertEqual(block['trigger_source'], 'direct')
        self.assertTrue(block['synthesized'])

    # ── Negative: no opt-in → legacy ────────────────────────────────────
    def test_tool_without_trigger_source_falls_to_legacy(self):
        """Proves the opt-in is load-bearing for tool callers too."""
        d = self._create(
            'competitor_comparison_tool',
            {'comparison_id': 'no-opt-in'},
            category='Competitive Intelligence',
        )
        block = build_provenance_block(d)
        self.assertTrue(block['legacy_no_provenance'])
        self.assertIsNone(block['origin_execution_id'])

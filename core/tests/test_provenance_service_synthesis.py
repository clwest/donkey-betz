"""
Session 1185 PR-C bucket 3A: Service-helper provenance synthesis tests.
========================================================================

Companion to buckets 1 + 2. Covers the "Group A simple opt-in" service
callsites from `docs/specs/deliverable_creation_paths.md` § Service-level
helpers, plus the Group C `deliverable_envelope.py` opt-in:

Group A (simple `trigger_source='direct'` opt-in):
- `core/services/implementation_executor.py:349` (WorkflowUpdateHandler)
- `core/services/implementation_executor.py:645` (ConfigUpdateHandler)
- `core/services/mission_control_executor.py:241` (MissionControlExecutor)
  — plus metadata enrichment from the originating attention_item
  (id + type + urgency) per Rigby's design call.

Group C (envelope helper):
- `core/services/deliverable_envelope.py:357` (`wrap_from_operation`) —
  only external caller is `backfill_deliverables.py:117`; helper itself
  stays neutral, the `wrap_from_operation` path opts in.

Group B (conversation/workspace pipeline threading — 3 callsites) is
deferred to PR-C bucket 3B per Rigby's split recommendation.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_service_synthesis -v2 --keepdb
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import AgentExecution
from core.services.deliverable_factory import create_deliverable
from core.services.deliverable_provenance import build_provenance_block


User = get_user_model()


class ServiceSynthesisTests(TestCase):
    """PR-C bucket 3A — Group A service callsite patterns."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='prov-svc', email='psvc@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Service-Synthesis Test Workspace',
            allow_autonomous_writes=True,
        )

    def _create(self, agent_name, metadata, category='Test'):
        return create_deliverable(
            title=f'{agent_name} service output',
            content='## Body\n' + ('Service helper body. ' * 30),
            agent_name=agent_name,
            user=self.user,
            workspace_id=str(self.workspace.id),
            category=category,
            metadata=metadata,
        )

    # ── Group A: implementation_executor.py:349 ───────────────────────────
    def test_workflow_update_handler_synthesizes(self):
        """WorkflowUpdateHandler service writes opt into direct synthesis."""
        d = self._create(
            'WorkflowUpdateHandler',
            {'source_pilot': 'pilot-abc',
             'decision_type': 'feature',
             'impact_area': 'pipeline',
             'workflow_steps': [{'step_number': 1, 'description': 'x'}],
             'trigger_source': 'direct'},
            category='Workflow',
        )
        self.assertIsNotNone(d.parent_object_id)
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertEqual(
            AgentExecution.objects.get(id=d.parent_object_id).owner_agent,
            'WorkflowUpdateHandler',
        )

    # ── Group A: implementation_executor.py:645 ───────────────────────────
    def test_config_update_handler_synthesizes(self):
        """ConfigUpdateHandler service writes opt into direct synthesis."""
        d = self._create(
            'ConfigUpdateHandler',
            {'source_pilot': 'pilot-xyz',
             'requires_human': True,
             'trigger_source': 'direct'},
            category='Config Proposals',
        )
        self.assertIsNotNone(d.parent_object_id)
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

    # ── Group A: mission_control_executor.py:241 ──────────────────────────
    def test_mission_control_executor_synthesizes_with_attention_item_metadata(self):
        """MissionControlExecutor opts into synthesis AND threads attention_item
        identity (id + type + urgency) into metadata for chain-of-custody."""
        d = self._create(
            attention_item_metadata := 'ContentWriterAgent',
            {'attention_item_id': 'item-001',
             'attention_item_type': 'decision',
             'attention_item_urgency': 'high',
             'source_agent': 'ContentWriterAgent',
             'trigger_source': 'direct'},
            category='Mission Control Output',
        )
        self.assertIsNotNone(d.parent_object_id, 'synthesis must fire')

        # Attention-item provenance enrichment lands in metadata
        self.assertEqual(d.metadata.get('attention_item_id'), 'item-001')
        self.assertEqual(d.metadata.get('attention_item_type'), 'decision')
        self.assertEqual(d.metadata.get('attention_item_urgency'), 'high')

        # silence unused-var warning while keeping the walrus assignment
        # legible in the test body (no shadowed builtin)
        self.assertEqual(attention_item_metadata, 'ContentWriterAgent')

    # ── Group C: deliverable_envelope wrap_from_operation pattern ─────────
    def test_envelope_wrap_from_operation_pattern_synthesizes(self):
        """deliverable_envelope.wrap_from_operation passes
        metadata={'file_path': ..., 'operation_type': ..., 'trigger_source': 'direct'}
        as of bucket 3A. Test the factory-contract shape directly."""
        d = self._create(
            'BackfillAgent',
            {'file_path': '/tmp/foo.txt',
             'operation_type': 'create',
             'trigger_source': 'direct'},
            category='Backfill',
        )
        self.assertIsNotNone(d.parent_object_id)
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

    # ── Read-layer surfaces ──────────────────────────────────────────────
    def test_provenance_block_surfaces_synthesized_marker_for_all_group_a(self):
        """End-to-end: all Group A shapes expose synthesized=true +
        trigger_source='direct' through build_provenance_block."""
        for agent_name, meta in [
            ('WorkflowUpdateHandler', {'source_pilot': 'p'}),
            ('ConfigUpdateHandler', {'requires_human': True}),
            ('MissionControlExecutor', {'attention_item_id': 'i'}),
        ]:
            meta['trigger_source'] = 'direct'
            d = self._create(agent_name, meta)
            block = build_provenance_block(d)
            self.assertTrue(
                block['synthesized'],
                f'{agent_name}: must surface synthesized=true',
            )
            self.assertEqual(
                block['trigger_source'], 'direct',
                f'{agent_name}: must carry trigger_source=direct',
            )
            self.assertFalse(block['legacy_no_provenance'])

    # ── Negative: no opt-in still falls to legacy bucket ──────────────────
    def test_service_without_trigger_source_falls_to_legacy(self):
        """Proves the opt-in is load-bearing for service callers too."""
        d = self._create(
            'WorkflowUpdateHandler',
            {'source_pilot': 'no-opt-in'},
            category='Workflow',
        )
        block = build_provenance_block(d)
        self.assertTrue(block['legacy_no_provenance'])
        self.assertIsNone(block['origin_execution_id'])

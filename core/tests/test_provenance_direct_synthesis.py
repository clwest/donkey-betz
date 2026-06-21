"""
Session 1185 PR-C bucket 1: Management-command provenance synthesis tests.
===========================================================================

Session 1184 PR-A added the `_is_pa_direct_context` synthesis branch, but
existing coverage in `test_deliverable_provenance.py` only exercises the
PA_IDENTITY case (`agent_name=PersonalAssistant`, `trigger_source='pa_tool'`).

This file covers the OTHER branch — non-PA agent_name + explicit
`trigger_source='direct'`. That's the contract PR-C management commands
opt into per `docs/specs/deliverable_creation_paths.md` § Management
commands (register_external_repo, survey_external_repo,
draft_repo_verifier_claims, refresh_repo_context, import_patent_disclosures).

Without this opt-in, the soft-enforce WARN fires and the deliverable hits
the legacy bucket. With it, the factory synthesizes an AgentExecution
receipt so the chain-of-custody read path works.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_direct_synthesis -v2 --keepdb
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import AgentExecution
from core.services.deliverable_factory import create_deliverable
from core.services.deliverable_provenance import build_provenance_block


User = get_user_model()


class DirectTriggerSynthesisTests(TestCase):
    """PR-C bucket 1 contract — mgmt-command callsite pattern."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='prov-direct', email='pd@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Direct-Synthesis Test Workspace',
            allow_autonomous_writes=True,
        )

    def _create(self, agent_name, metadata):
        return create_deliverable(
            title=f'{agent_name} script output',
            content='## Body\n' + ('Script-mode deliverable body. ' * 30),
            agent_name=agent_name,
            user=self.user,
            workspace_id=str(self.workspace.id),
            metadata=metadata,
        )

    def test_direct_trigger_synthesizes_receipt_for_repo_profile_agent(self):
        """register_external_repo.py:325 pattern — REPO_PROFILE_AGENT_NAME +
        trigger_source='direct' must synthesize an AgentExecution receipt."""
        d = self._create('RepoProfileAgent',
                         {'trigger_source': 'direct', 'repo_id': 'foo'})
        self.assertIsNotNone(d, 'must not be quality-gated')
        self.assertIsNotNone(d.parent_object_id,
                             'direct opt-in must synthesize a receipt')
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

        receipt = AgentExecution.objects.filter(id=d.parent_object_id).first()
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.status, 'completed')
        self.assertEqual(receipt.owner_agent, 'RepoProfileAgent')

    def test_direct_trigger_synthesizes_for_cto_agent(self):
        """draft_repo_verifier_claims.py:277 pattern — CTOAgent."""
        d = self._create('CTOAgent', {'trigger_source': 'direct'})
        self.assertIsNotNone(d.parent_object_id)
        self.assertEqual(
            AgentExecution.objects.get(id=d.parent_object_id).owner_agent,
            'CTOAgent',
        )

    def test_no_direct_trigger_falls_to_legacy_bucket(self):
        """Same agent_name WITHOUT trigger_source='direct' opt-in must hit the
        soft-enforce WARN and create the deliverable with no provenance link."""
        d = self._create('RepoProfileAgent', {'repo_id': 'bar'})
        self.assertIsNotNone(d, 'soft-enforce must not block')
        block = build_provenance_block(d)
        self.assertTrue(
            block['legacy_no_provenance'],
            'without direct opt-in, must surface as legacy',
        )
        self.assertIsNone(block['origin_execution_id'])

    def test_direct_trigger_surfaces_synthesized_in_read_block(self):
        """End-to-end: direct opt-in + read helper → synthesized=true marker."""
        d = self._create('CTOAgent',
                         {'trigger_source': 'direct', 'foo': 'bar'})
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertTrue(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'direct')
        self.assertEqual(block['origin_execution_id'], str(d.parent_object_id))

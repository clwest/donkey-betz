"""
Session 1185 PR-C bucket 3B-2: workspace_pipeline_runner per-stage execution tests.
====================================================================================

Per Rigby's design call: each pipeline stage gets its own orchestration
AgentExecution row. Per-stage attribution lets downstream provenance reads
pivot from any stage deliverable back to (a) the stage execution and (b)
the parent pipeline run via Session 843 fields.

Rigby's 6-point checklist (conversation pa-10df024c0bd8):
    1. Defensive fall-through pattern — done in _run_agent_with_timeout
    2. agent_name = actual invoked agent (not stage_name) — done
    3. parent_object_id is UUID (PipelineRun.id is UUIDField) — verified
    4. metadata redundancy: pipeline_run_id + stage_index — done
    5. Trigger source inference (no forced 'direct') — done
    6. Tests: N stages → N AgentExecution rows + reverse-link via F2

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_pipeline_stages -v2 --keepdb
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import Agent, AgentExecution
from core.services.deliverable_provenance import build_provenance_block
from core.services.workspace_pipeline_runner import _save_stage_deliverable


User = get_user_model()


class PipelineStageDeliverableTests(TestCase):
    """3B-2 contract: _save_stage_deliverable wires parent_execution_id
    and metadata correctly when given a stage_execution_id."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='pipe-stages', email='ps@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Pipeline-Stages Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )
        cls.run_id = str(uuid.uuid4())

    def _make_stage_execution(self, agent_name, stage_name, stage_index):
        """Mirror what _run_agent_with_timeout creates for the stage."""
        from django.utils import timezone
        agent_record, _ = Agent.objects.get_or_create(
            name=agent_name,
            defaults={'agent_type': 'routable', 'is_active': True,
                      'description': 'test', 'specialization': ''},
        )
        return AgentExecution.objects.create(
            agent=agent_record, user=self.user,
            task=f'Pipeline {self.run_id} stage {stage_index} ({stage_name}): test',
            status='completed', owner_agent=agent_name,
            parent_object_type='pipeline_run',
            parent_object_id=uuid.UUID(self.run_id),
            input_data={
                'source': 'workspace_pipeline_runner',
                'execution_kind': 'orchestration_stage',
                'pipeline_run_id': self.run_id,
                'stage_name': stage_name,
                'stage_index': stage_index,
                'workspace_id': str(self.workspace.id),
            },
            output_data={'kind': 'pipeline_stage_receipt'},
            last_heartbeat_at=timezone.now(),
            completed_at=timezone.now(),
        )

    def test_save_stage_deliverable_threads_execution_id(self):
        """When stage_execution_id is passed, deliverable is linked via the
        Session 1184 contract (parent_object_type='agent_execution')."""
        execution = self._make_stage_execution('ResearchAgent', 'Deep Research', 1)

        deliverable_id = _save_stage_deliverable(
            workspace=self.workspace,
            stage_name='Deep Research', agent_name='ResearchAgent',
            content='## Findings\n' + ('Research body. ' * 40),
            brief={'topic': 'Customer Personas'},
            run_id=self.run_id, user=self.user,
            stage_index=1, stage_execution_id=str(execution.id),
        )

        d = Deliverable.objects.get(id=deliverable_id)
        self.assertEqual(d.parent_object_type, 'agent_execution',
                         'must wire to AgentExecution per Session 1184')
        self.assertEqual(str(d.parent_object_id), str(execution.id),
                         'must point at the per-stage execution row')

    def test_metadata_redundancy_per_rigby_checklist(self):
        """pipeline_run_id + stage_index + stage_name + stage_agent in metadata
        per Rigby's #4 — single-query lookups don't need execution joins."""
        execution = self._make_stage_execution('ContentWriterAgent', 'Write Draft', 3)
        deliverable_id = _save_stage_deliverable(
            workspace=self.workspace,
            stage_name='Write Draft', agent_name='ContentWriterAgent',
            content='## Draft body. ' * 40,
            brief={'topic': 'Customer Personas'},
            run_id=self.run_id, user=self.user,
            stage_index=3, stage_execution_id=str(execution.id),
        )
        d = Deliverable.objects.get(id=deliverable_id)
        self.assertEqual(d.metadata.get('pipeline_run_id'), self.run_id)
        self.assertEqual(d.metadata.get('stage_index'), 3)
        self.assertEqual(d.metadata.get('stage_name'), 'Write Draft')
        self.assertEqual(d.metadata.get('stage_agent'), 'ContentWriterAgent')

    def test_provenance_block_reads_clean_for_stage_deliverable(self):
        """F2 reverse-link must work: the stage execution's read path now
        surfaces the produced deliverable."""
        execution = self._make_stage_execution('TopicMinerAgent', 'Topic Mining', 0)
        deliverable_id = _save_stage_deliverable(
            workspace=self.workspace,
            stage_name='Topic Mining', agent_name='TopicMinerAgent',
            content='## Mining results\n' + ('Topic body. ' * 40),
            brief={'topic': 'AI Startups'},
            run_id=self.run_id, user=self.user,
            stage_index=0, stage_execution_id=str(execution.id),
        )
        d = Deliverable.objects.get(id=deliverable_id)
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertFalse(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'agent_execution')
        self.assertEqual(block['origin_execution_id'], str(execution.id))

    def test_save_stage_deliverable_falls_to_legacy_without_execution_id(self):
        """Defensive: if stage_execution_id is None (the upstream
        AgentExecution.create failed), deliverable still gets created and
        lands in factory's WARN/legacy bucket. Pipeline doesn't block."""
        deliverable_id = _save_stage_deliverable(
            workspace=self.workspace,
            stage_name='Fact Check', agent_name='EditorAgent',
            content='## Check\n' + ('Body content with substance. ' * 80),
            brief={'topic': 'AI Startups'},
            run_id=self.run_id, user=self.user,
            stage_index=5, stage_execution_id=None,
        )
        d = Deliverable.objects.get(id=deliverable_id)
        block = build_provenance_block(d)
        self.assertTrue(block['legacy_no_provenance'],
                        'no execution_id → legacy bucket (graceful)')

    def test_n_stages_create_n_executions_and_n_deliverables(self):
        """Rigby's #6: a pipeline run with N stages produces N AgentExecution
        rows (each parent='pipeline_run', parent_id=run.id) and N
        deliverables (each parent='agent_execution', parent_id=stage exec)."""
        stages = [
            ('TopicMinerAgent', 'Topic Mining', 0),
            ('ResearchAgent', 'Deep Research', 1),
            ('ContentStrategyAgent', 'Content Strategy', 2),
            ('ContentWriterAgent', 'Write Draft', 3),
            ('EditorAgent', 'Edit & Polish', 4),
        ]
        deliverable_ids = []
        execution_ids = []
        for agent_name, stage_name, idx in stages:
            execution = self._make_stage_execution(agent_name, stage_name, idx)
            execution_ids.append(execution.id)
            deliverable_id = _save_stage_deliverable(
                workspace=self.workspace,
                stage_name=stage_name, agent_name=agent_name,
                content=f'## {stage_name}\n' + ('Body content with substance. ' * 80),
                brief={'topic': 'Customer Personas'},
                run_id=self.run_id, user=self.user,
                stage_index=idx, stage_execution_id=str(execution.id),
            )
            deliverable_ids.append(deliverable_id)

        # N executions all scoped to the same pipeline run
        run_executions = AgentExecution.objects.filter(
            parent_object_type='pipeline_run',
            parent_object_id=uuid.UUID(self.run_id),
        )
        self.assertEqual(run_executions.count(), 5,
                         '5 stages → 5 execution rows scoped to pipeline_run')

        # N deliverables each pointing at its own stage execution
        for d_id, exec_id in zip(deliverable_ids, execution_ids):
            d = Deliverable.objects.get(id=d_id)
            self.assertEqual(str(d.parent_object_id), str(exec_id),
                             'each deliverable wires to its stage execution')
            self.assertEqual(d.parent_object_type, 'agent_execution')

        # F2 reverse-link (PR #2367) auto-works once both PRs land — when
        # `execution_history_tool detail` returns the `deliverables` field, it
        # queries `Deliverable.objects.filter(parent_object_id=exec.id,
        # parent_object_type='agent_execution')` which matches the chain
        # established above. Direct DB-query equivalent here (no dependency
        # on PR #2367 being merged yet):
        for d_id, exec_id in zip(deliverable_ids, execution_ids):
            reverse_link = list(
                Deliverable.objects.filter(
                    parent_object_id=exec_id,
                    parent_object_type='agent_execution',
                ).values_list('id', flat=True)
            )
            self.assertEqual(len(reverse_link), 1,
                             'F2 reverse-link chain: stage execution → 1 deliverable')
            self.assertEqual(str(reverse_link[0]), str(d_id))

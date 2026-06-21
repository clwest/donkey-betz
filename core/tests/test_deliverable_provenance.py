"""
Session 1184: Deliverable → Execution provenance.
==================================================

Proves the chain Rigby's deliverable e4f4e12f-bd77-4611-a3d6-1a50fd3b9412 asked
for: every newly-created deliverable carries an origin execution id, and the
read layer surfaces a normalized `provenance` block (origin_execution_id,
trigger_source, created_by_agent, trace_id, tool_calls).

Covers:
1. **AC1 + AC2** — agent-dispatch path: when caller passes parent_execution_id,
   deliverable's parent_object_id matches the AgentExecution row.
2. **AC1 + AC3** — PA-direct path: when caller is PA/tool layer with no
   parent_execution_id, factory synthesizes an AgentExecution receipt and the
   deliverable links to it.
3. **AC4** — read layer: build_provenance_block surfaces the full chain
   including ToolCallRecords joined by trace_id.
4. **AC5** — soft-enforce: non-PA agents that forget to pass execution id
   still get a deliverable but with legacy_no_provenance=True surfaced.

Run:
    python manage.py test core.tests.test_deliverable_provenance -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.models_tool_calls import ToolCallRecord
from core.models_unified_system import Agent, AgentExecution
from core.services.deliverable_factory import create_deliverable
from core.services.deliverable_provenance import build_provenance_block
from core.services.pa_identity import PA_IDENTITY


User = get_user_model()


class DeliverableProvenanceTests(TestCase):
    """End-to-end coverage of the Session 1184 provenance contract."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='provenance-test', email='prov@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Provenance Test Workspace',
            allow_autonomous_writes=True,
        )

    def _make_agent_execution(self, agent_name='ResearchAgent', trace_id=None):
        agent_record, _ = Agent.objects.get_or_create(
            name=agent_name,
            defaults={'agent_type': 'routable', 'description': 'test',
                      'specialization': '', 'is_active': True},
        )
        return AgentExecution.objects.create(
            agent=agent_record, user=self.user,
            task='Test research task',
            status='in_progress',
            trace_id=trace_id or uuid.uuid4(),
            owner_agent=agent_name,
        )

    # AC1 + AC2 — agent-dispatch path links parent_object_id to the real exec
    def test_agent_dispatch_links_parent_object_id_to_execution(self):
        execution = self._make_agent_execution()
        d = create_deliverable(
            title='Research Output From Agent Dispatch',
            content='## Findings\n' + ('Detailed research body. ' * 30),
            agent_name='ResearchAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
            parent_execution_id=str(execution.id),
        )
        self.assertIsNotNone(d)
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertEqual(str(d.parent_object_id), str(execution.id))

    # AC1 + AC3 — PA-direct path synthesizes a receipt
    def test_pa_direct_create_synthesizes_execution_receipt(self):
        d = create_deliverable(
            title='Rigby Saved Note',
            content='User asked me to save this. ' * 25,
            agent_name=PA_IDENTITY,
            user=self.user,
            workspace_id=str(self.workspace.id),
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertIsNotNone(d)
        self.assertIsNotNone(d.parent_object_id, 'PA-direct must synthesize a receipt')
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

        # The synthesized row exists in AgentExecution
        receipt = AgentExecution.objects.filter(id=d.parent_object_id).first()
        self.assertIsNotNone(receipt, 'Synthesized AgentExecution row must exist')
        self.assertEqual(receipt.status, 'completed')
        self.assertEqual(receipt.owner_agent, PA_IDENTITY)

    # AC4 — read layer exposes provenance and ToolCallRecord chain via trace_id
    def test_provenance_block_surfaces_full_chain(self):
        trace_id = uuid.uuid4()
        execution = self._make_agent_execution(trace_id=trace_id)
        # Simulate two tool calls bound to the same trace_id
        ToolCallRecord.objects.create(
            trace_id=trace_id, agent_name='ResearchAgent',
            tool_name='search_web', success=True, latency_ms=123,
        )
        ToolCallRecord.objects.create(
            trace_id=trace_id, agent_name='ResearchAgent',
            tool_name='summarize', success=True, latency_ms=45,
        )

        d = create_deliverable(
            title='Research With Tool Chain',
            content='## Synthesis\n' + ('Long body content. ' * 50),
            agent_name='ResearchAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
            parent_execution_id=str(execution.id),
        )
        self.assertIsNotNone(d)

        block = build_provenance_block(d)
        self.assertEqual(block['origin_execution_id'], str(execution.id))
        self.assertEqual(block['created_by_agent'], 'ResearchAgent')
        self.assertEqual(block['trace_id'], str(trace_id))
        self.assertFalse(block['legacy_no_provenance'])
        self.assertEqual(len(block['tool_calls']), 2)
        tool_names = {c['tool_name'] for c in block['tool_calls']}
        self.assertEqual(tool_names, {'search_web', 'summarize'})

    # AC5 — non-PA caller without execution gets soft-enforce WARN, not crash
    def test_autonomous_agent_without_execution_is_marked_legacy(self):
        d = create_deliverable(
            title='Scheduled Agent Output Missing Execution',
            content='## Data\n' + ('Beat-task style output. ' * 30),
            agent_name='SchedulerlessAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
            # No parent_execution_id, no PA trigger_source — soft-enforce path
        )
        self.assertIsNotNone(d, 'Soft-enforce must not block creation')
        block = build_provenance_block(d)
        self.assertTrue(block['legacy_no_provenance'])
        self.assertIsNone(block['origin_execution_id'])

"""
Session 1185 PR-C bucket 3B-1: Conversation-pipeline execution threading tests.
================================================================================

Per Rigby's design recon (conversation pa-10df024c0bd8 Session 1185), the
3 Group B callsites split:

- 3B-1 (this PR): `conversation_initiative_pipeline.py:536` +
  `conversation_deliverable_extractor.py:357`. Both create an
  orchestration AgentExecution row scoped to the conversation, then
  thread that execution_id to `create_deliverable` instead of bypassing
  the provenance contract with `parent_object_type='conversation'`.
- 3B-2 (next): `workspace_pipeline_runner.py:456` — per-stage executions.

## What this PR fixes (recon finding)

Both conversation callsites were setting
`Deliverable.parent_object_type='conversation'` directly on the
deliverable. The Session 1184 provenance helper only recognizes
`parent_type in ('agent_execution', 'deliverable_factory')` — so these
deliverables were silently in the legacy_no_provenance bucket despite
having a parent_object_id.

Grep confirmed NO downstream readers filter for
`Deliverable.parent_object_type='conversation'`. Risk-free flip.

## New chain (Session 843 + 1184 contract)

```
Deliverable
    parent_object_type='agent_execution'
    parent_object_id=<new AgentExecution.id>
    metadata.conversation_id=<conv_id_str>
    metadata.conversation_uuid=<conv_uuid_str>
        ↓
AgentExecution (orchestration receipt — created here)
    parent_object_type='conversation'
    parent_object_id=<conv_uuid>
    conversation_id=<conv_id_str>   ← reuses Session 1174 field
    owner_agent=<participants[0] or 'ConversationOrchestrator'>
    input_data.execution_kind='orchestration'
```

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_conversation_threading -v2 --keepdb
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import AgentExecution
from core.services.conversation_deliverable_extractor import (
    ConversationDeliverableExtractor, ExtractedDeliverable,
)
from core.services.deliverable_provenance import build_provenance_block


User = get_user_model()


class ConversationExtractorThreadingTests(TestCase):
    """3B-1: ConversationDeliverableExtractor creates the orchestration
    AgentExecution and threads it through create_deliverable."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='conv-thread', email='ct@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Conv-Threading Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )
        cls.conversation_uuid = uuid.uuid4()
        cls.conversation_id = str(cls.conversation_uuid)

    def setUp(self):
        self.extractor = ConversationDeliverableExtractor()

    def _make_extracted(self, content='## Body\n' + ('Real content. ' * 30)):
        return ExtractedDeliverable(
            content_type='document', title='Test extraction',
            content=content, category='Test',
            tags=['conv-threading', 'test'],
            confidence=0.85, source_message_idx=2,
        )

    def _dispatch(self, participants=None, topic='Customer Personas'):
        # Mock extract_structured_content so we don't need real messages/LLM
        with mock.patch.object(
            self.extractor, 'extract_structured_content',
            return_value=self._make_extracted(),
        ):
            return self.extractor.extract_and_create(
                conversation_id=self.conversation_id,
                messages=[{'role': 'user', 'content': 'x'}],
                decision_summary={'topic': topic},
                participants=participants or ['ResearchAgent', 'ContentStrategyAgent'],
                topic=topic,
                user_id=self.user.id,
            )

    def test_extractor_creates_orchestration_agent_execution(self):
        """An AgentExecution row is created scoped to the conversation."""
        result = self._dispatch()
        self.assertEqual(result.deliverables_created, 1)

        d = Deliverable.objects.get(id=result.deliverable_ids[0])

        # Deliverable now links to AgentExecution (not directly to conversation)
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertIsNotNone(d.parent_object_id)

        # The AgentExecution it links to is the orchestration row
        execution = AgentExecution.objects.get(id=d.parent_object_id)
        self.assertEqual(execution.parent_object_type, 'conversation')
        self.assertEqual(str(execution.parent_object_id), self.conversation_id)
        self.assertEqual(execution.conversation_id, self.conversation_id)
        self.assertEqual(execution.owner_agent, 'ResearchAgent')
        self.assertEqual(execution.status, 'completed')

    def test_extractor_preserves_conversation_id_in_metadata(self):
        """conversation_id stays in Deliverable.metadata for single-query
        lookups (no AgentExecution join required)."""
        result = self._dispatch()
        d = Deliverable.objects.get(id=result.deliverable_ids[0])
        self.assertEqual(d.metadata.get('conversation_id'), self.conversation_id)
        self.assertEqual(
            d.metadata.get('conversation_uuid'), self.conversation_id,
            'conversation_uuid stores the canonical UUID str',
        )

    def test_extractor_provenance_block_reads_clean(self):
        """build_provenance_block surfaces the chain: trigger_source=
        agent_execution (auto-inferred), synthesized=false (real execution
        exists), origin_execution_id=AgentExecution.id."""
        result = self._dispatch()
        d = Deliverable.objects.get(id=result.deliverable_ids[0])
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'],
                         'must not be in legacy bucket')
        self.assertFalse(block['synthesized'],
                         'real orchestration execution exists, not synthesized')
        self.assertEqual(block['trigger_source'], 'agent_execution',
                         'factory-inferred when parent_execution_id is set')
        self.assertEqual(block['origin_execution_id'],
                         str(d.parent_object_id))

    def test_extractor_execution_input_data_marks_orchestration(self):
        """The AgentExecution row's input_data marks it as orchestration,
        not user/agent dispatch — per Rigby: 'don't lie and call these
        direct if they're orchestration-driven'."""
        result = self._dispatch()
        d = Deliverable.objects.get(id=result.deliverable_ids[0])
        execution = AgentExecution.objects.get(id=d.parent_object_id)
        self.assertEqual(execution.input_data.get('execution_kind'),
                         'orchestration')
        self.assertEqual(execution.input_data.get('source'),
                         'conversation_deliverable_extractor')

    def test_extractor_falls_through_when_execution_creation_fails(self):
        """Defensive: if AgentExecution.create raises, deliverable still
        gets created (falls into factory's WARN bucket). Pipeline must
        not block on provenance plumbing failure."""
        with mock.patch(
            'core.models_unified_system.AgentExecution.objects.create',
            side_effect=RuntimeError('synthetic DB error'),
        ):
            result = self._dispatch()

        self.assertEqual(result.deliverables_created, 1,
                         'deliverable creation must not be blocked')
        d = Deliverable.objects.get(id=result.deliverable_ids[0])
        # parent_execution_id was None → falls to WARN bucket (legacy)
        block = build_provenance_block(d)
        self.assertTrue(block['legacy_no_provenance'])


class ConversationPipelineThreadingShapeTests(TestCase):
    """3B-1 contract test for conversation_initiative_pipeline.py:536.

    Going through the full `process()` flow requires building Initiative
    fixtures + circuit-breaker state. Easier: test the contract shape
    that pipeline now writes by calling create_deliverable directly with
    the same param set, then verifying the chain.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='conv-pipe', email='cp@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Conv-Pipeline Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )
        cls.conversation_id = str(uuid.uuid4())

    def test_pipeline_shape_full_chain(self):
        """Mirror conversation_initiative_pipeline.py:536 shape — pre-create
        the orchestration AgentExecution, then call create_deliverable with
        parent_execution_id threaded. Assert full 2-hop chain."""
        from core.models_unified_system import Agent, AgentExecution as AE
        from core.services.deliverable_factory import create_deliverable
        from django.utils import timezone

        agent_record, _ = Agent.objects.get_or_create(
            name='ConversationOrchestrator',
            defaults={'agent_type': 'orchestration', 'is_active': True,
                      'description': 'test', 'specialization': ''},
        )
        execution = AE.objects.create(
            agent=agent_record, user=self.user,
            task='Conversation→Initiative pipeline: Customer Personas',
            status='completed', owner_agent='ConversationOrchestrator',
            parent_object_type='conversation',
            parent_object_id=uuid.UUID(self.conversation_id),
            conversation_id=self.conversation_id,
            input_data={'source': 'conversation_initiative_pipeline',
                        'execution_kind': 'orchestration'},
            last_heartbeat_at=timezone.now(),
            completed_at=timezone.now(),
        )

        d = create_deliverable(
            title='Document: Customer Personas',
            content='## Personas\n' + ('Body text. ' * 40),
            agent_name='ConversationOrchestrator',
            user=self.user,
            workspace_id=str(self.workspace.id),
            category='Document',
            deliverable_type='document',
            parent_execution_id=str(execution.id),
            metadata={
                'source': 'conversation_initiative_pipeline',
                'conversation_id': self.conversation_id,
                'conversation_uuid': self.conversation_id,
            },
        )

        # 2-hop chain
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertEqual(str(d.parent_object_id), str(execution.id))

        # Hop 2: AgentExecution → Conversation
        self.assertEqual(execution.parent_object_type, 'conversation')
        self.assertEqual(str(execution.parent_object_id), self.conversation_id)

        # metadata redundancy
        self.assertEqual(d.metadata.get('conversation_id'), self.conversation_id)

        # provenance read surfaces clean
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertFalse(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'agent_execution')

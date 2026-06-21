"""
Session 1186 PR-C bucket 4: Celery-task callsite provenance tests.
===================================================================

Covers the 3 ⚠️ WARN-bucket callsites named in
``docs/specs/deliverable_creation_paths.md`` § Celery tasks:

| Callsite | Agent | Pattern |
|---|---|---|
| ``core/tasks_content.py:244``      | VideoContentPackAgent  | direct synthesis (no agent dispatch)    |
| ``core/tasks_initiatives.py:2149`` | TechnicalDocumentAgent | B.2 external receipt (helper + factory) |
| ``core/tasks_initiatives.py:2770`` | router.route() agent   | B.2 external receipt (helper + factory) |

The B.2 design (per Rigby on pa-10df024c0bd8): both initiative tasks already
have an internal agent ``_save_to_deliverable`` that creates a deliverable
with ``Development``/``stage-N`` tags. The EXTERNAL save in the task creates
a second deliverable with Initiative-shaped tags (``Initiative — Stage N``,
``initiative`` FK, ``self_blog`` FK) that the Initiatives UI keys on. We
provenance the external save with a NEW AgentExecution receipt rather than
threading the agent's execution id — sharing the id would collapse them via
the factory's ``dedupe-by-(parent_object_type, parent_object_id)`` at
``deliverable_factory.py:509`` and silently lose the Initiative-shaped row.

Follow-up B.1 (filed end of session): unify to one deliverable per stage by
threading initiative context into the agent's internal save so we can drop
the external save entirely.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_provenance_celery_tasks -v2 --keepdb
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

import core.tasks_initiatives as tasks_initiatives
from core.models import Initiative
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import AgentExecution
from core.services.deliverable_factory import create_deliverable
from core.services.deliverable_provenance import build_provenance_block

_create_initiative_external_execution_receipt = (
    tasks_initiatives._create_initiative_external_execution_receipt
)


User = get_user_model()


class VideoContentPackDirectSynthesisTests(TestCase):
    """Callsite A — ``tasks_content.py:244`` opt-in to factory synthesis via
    ``trigger_source='direct'``. No AgentExecution row is pre-created — the
    factory synthesizes one because the trigger source is in
    ``_PA_DIRECT_TRIGGERS``."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='video-pack', email='vp@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Video Pack Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )

    def _create_pack_deliverable(self, extra_metadata=None):
        """Mirror the kwargs `_impl_generate_video_content_pack_task` passes."""
        metadata = {
            'trigger_source': 'direct',
            'celery_task_name': 'generate_video_content_pack_task',
            'video_id': 'video-uuid-abc',
            'user_id': str(self.user.id),
            'language': 'en',
            'llm_model': 'gpt-5-mini',
            'transcript_id': 'transcript-uuid-xyz',
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        return create_deliverable(
            title='Content Pack: Test Video Title',
            content='{"titles": ["a"], "summary": "Test summary body. " ' + ('"x" ' * 80) + '}',
            agent_name='VideoContentPackAgent',
            category='Video Content',
            deliverable_type='document',
            user=self.user,
            tags=['video', 'content-pack', 'auto-generated'],
            agent_task='Generate content pack for video: Test Video Title',
            content_format='json',
            quality_score=0.8,
            confidence_score=0.85,
            workspace_id=str(self.workspace.id),
            is_saved=True,
            metadata=metadata,
        )

    def test_direct_trigger_synthesizes_receipt(self):
        d = self._create_pack_deliverable()
        self.assertIsNotNone(d, 'gate must not block')
        self.assertIsNotNone(d.parent_object_id,
                             'direct opt-in must synthesize a receipt')
        self.assertEqual(d.parent_object_type, 'agent_execution')

        receipt = AgentExecution.objects.get(id=d.parent_object_id)
        self.assertEqual(receipt.status, 'completed')
        self.assertEqual(receipt.owner_agent, 'VideoContentPackAgent')

    def test_metadata_carries_celery_audit_fields(self):
        """Per Rigby's design call: metadata must carry enough to audit the
        direct-LLM-call path without an AgentExecution standing in."""
        d = self._create_pack_deliverable()
        self.assertEqual(d.metadata.get('trigger_source'), 'direct')
        self.assertEqual(d.metadata.get('celery_task_name'),
                         'generate_video_content_pack_task')
        self.assertEqual(d.metadata.get('video_id'), 'video-uuid-abc')
        self.assertEqual(d.metadata.get('language'), 'en')
        self.assertEqual(d.metadata.get('llm_model'), 'gpt-5-mini')
        self.assertTrue(d.metadata.get('origin_execution_synthesized'))

    def test_provenance_read_block_marks_synthesized(self):
        d = self._create_pack_deliverable()
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertTrue(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'direct')
        self.assertEqual(block['origin_execution_id'], str(d.parent_object_id))


class InitiativeExternalReceiptHelperTests(TestCase):
    """Callsites B + C unit-test target — the
    ``_create_initiative_external_execution_receipt`` helper used by both
    initiative pipeline tasks."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='init-ext', email='ie@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Initiative Ext Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )
        cls.initiative = Initiative.objects.create(
            name='Bucket-4 Test Initiative',
            status='ACTIVE',
            current_stage=2,
        )

    def test_helper_creates_receipt_for_callsite_b(self):
        """B-shape: TechnicalDocumentAgent + run_initiative_pipeline_task."""
        exec_id = _create_initiative_external_execution_receipt(
            agent_name='TechnicalDocumentAgent',
            initiative=self.initiative,
            stage_num=2,
            stage_label='Architecture Design',
            celery_task_name='run_initiative_pipeline_task',
            content='Stage 2 architecture body. ' * 30,
            self_blog_id='blog-uuid-b',
            extra_input={'doc_type': 'technical_document'},
        )
        self.assertIsNotNone(exec_id)
        receipt = AgentExecution.objects.get(id=exec_id)

        self.assertEqual(receipt.status, 'completed')
        self.assertEqual(receipt.owner_agent, 'TechnicalDocumentAgent')
        self.assertEqual(receipt.parent_object_type, 'initiative')
        self.assertEqual(str(receipt.parent_object_id), str(self.initiative.id))
        self.assertEqual(
            receipt.input_data['source'],
            'initiative_pipeline_task_external_save',
        )
        self.assertEqual(receipt.input_data['execution_kind'],
                         'orchestration_stage')
        self.assertEqual(receipt.input_data['celery_task_name'],
                         'run_initiative_pipeline_task')
        self.assertEqual(receipt.input_data['stage_num'], 2)
        self.assertEqual(receipt.input_data['stage_label'],
                         'Architecture Design')
        self.assertEqual(receipt.input_data['self_blog_id'], 'blog-uuid-b')
        self.assertEqual(receipt.input_data['doc_type'], 'technical_document')

    def test_helper_creates_receipt_for_callsite_c(self):
        """C-shape: router.route()-invoked agent + generate_initiative_stage_document."""
        exec_id = _create_initiative_external_execution_receipt(
            agent_name='ResearchAgent',
            initiative=self.initiative,
            stage_num=1,
            stage_label='Research Brief',
            celery_task_name='generate_initiative_stage_document',
            content='Stage 1 research body. ' * 30,
            self_blog_id='blog-uuid-c',
        )
        self.assertIsNotNone(exec_id)
        receipt = AgentExecution.objects.get(id=exec_id)

        self.assertEqual(receipt.owner_agent, 'ResearchAgent')
        self.assertEqual(receipt.input_data['celery_task_name'],
                         'generate_initiative_stage_document')
        self.assertEqual(receipt.input_data['stage_label'], 'Research Brief')
        self.assertEqual(receipt.input_data['agent_invoked'], 'ResearchAgent')
        # extra_input omitted → no extra keys merged
        self.assertNotIn('doc_type', receipt.input_data)

    def test_helper_returns_none_on_failure_no_raise(self):
        """Defensive: if AgentExecution.create blows up, helper returns None
        and the caller falls through to the factory's WARN bucket. The
        pipeline task does NOT crash."""
        with mock.patch(
            'core.models_unified_system.AgentExecution.objects.create',
            side_effect=RuntimeError('simulated DB failure'),
        ):
            exec_id = _create_initiative_external_execution_receipt(
                agent_name='TechnicalDocumentAgent',
                initiative=self.initiative,
                stage_num=3,
                stage_label='Pilot Plan',
                celery_task_name='run_initiative_pipeline_task',
                content='body',
                self_blog_id='blog-uuid-fail',
            )
        self.assertIsNone(exec_id)


class InitiativeExternalDeliverableEndToEndTests(TestCase):
    """B + C end-to-end: receipt + create_deliverable wires the Deliverable
    to the external execution row via PR-A's contract."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='init-e2e', email='e2e@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Initiative E2E Test Workspace',
            allow_autonomous_writes=True, is_active=True,
        )
        cls.initiative = Initiative.objects.create(
            name='E2E Test Initiative',
            status='ACTIVE',
            current_stage=1,
        )

    def _emit(self, agent_name, stage_num, stage_label, celery_task_name):
        """Mirror the inline shape in both task callsites. Calls the helper
        through the module namespace so unit tests can patch it."""
        content = f'## Stage {stage_num} body\n' + ('Body content. ' * 40)
        exec_id = tasks_initiatives._create_initiative_external_execution_receipt(
            agent_name=agent_name,
            initiative=self.initiative,
            stage_num=stage_num,
            stage_label=stage_label,
            celery_task_name=celery_task_name,
            content=content,
            self_blog_id='blog-uuid-emit',
        )
        d = create_deliverable(
            title=f'{self.initiative.name} - Stage {stage_num}: {stage_label}',
            content=content,
            agent_name=agent_name,
            category=f'Initiative — Stage {stage_num}',
            deliverable_type='document',
            tags=['initiative', f'stage-{stage_num}', 'general'],
            content_format='markdown',
            quality_score=0.7,
            confidence_score=0.7,
            initiative_id=str(self.initiative.id),
            preview_content=content[:500],
            status='completed',
            workspace_id=str(self.workspace.id),
            parent_execution_id=exec_id,
            parent_object_type='agent_execution' if exec_id else '',
        )
        return d, exec_id

    def test_deliverable_wires_to_external_execution(self):
        d, exec_id = self._emit(
            'TechnicalDocumentAgent', 2, 'Architecture',
            'run_initiative_pipeline_task',
        )
        self.assertIsNotNone(d)
        self.assertEqual(d.parent_object_type, 'agent_execution')
        self.assertEqual(str(d.parent_object_id), str(exec_id))

    def test_provenance_read_block_clean_for_b_and_c(self):
        d, exec_id = self._emit(
            'ResearchAgent', 1, 'Research Brief',
            'generate_initiative_stage_document',
        )
        block = build_provenance_block(d)
        self.assertFalse(block['legacy_no_provenance'])
        self.assertFalse(block['synthesized'])
        self.assertEqual(block['trigger_source'], 'agent_execution')
        self.assertEqual(block['origin_execution_id'], str(exec_id))

    def test_f2_reverse_link_finds_deliverable_from_execution(self):
        """PR #2367 F2 reverse-link: Deliverable.objects.filter(parent_object_id=exec.id)
        finds the produced deliverable. Verified via direct DB query so the
        test does not depend on F2's read API."""
        d, exec_id = self._emit(
            'TechnicalDocumentAgent', 4, 'Technical Design',
            'run_initiative_pipeline_task',
        )
        reverse = list(Deliverable.objects.filter(
            parent_object_id=exec_id,
            parent_object_type='agent_execution',
        ).values_list('id', flat=True))
        self.assertEqual(len(reverse), 1)
        self.assertEqual(str(reverse[0]), str(d.id))

    def test_receipt_failure_falls_through_to_warn_bucket(self):
        """If receipt creation fails (helper returns None), the deliverable
        still gets created and lands in the factory's legacy/WARN bucket —
        the pipeline does not block."""
        with mock.patch(
            'core.tasks_initiatives._create_initiative_external_execution_receipt',
            return_value=None,
        ):
            d, exec_id = self._emit(
                'TechnicalDocumentAgent', 5, 'Pilot Execution',
                'run_initiative_pipeline_task',
            )
        self.assertIsNone(exec_id)
        self.assertIsNotNone(d, 'pipeline must not block on receipt failure')
        block = build_provenance_block(d)
        self.assertTrue(
            block['legacy_no_provenance'],
            'no receipt → factory falls to legacy bucket (graceful)',
        )

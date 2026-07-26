"""Regression tests for the S2981 stage-doc dispatch guardrails + provenance.

Spec: workspace deliverable ``2a196415-19cf-4bda-87b5-1c4233a5cd9d``
      "ENGINEERING SPEC — Fix initiative stage doc generator: missing-initiative
      guardrails + provenance + status consistency".

Covers three surfaces:

1. ``core.services.initiative_stage_dispatch.queue_stage_document_generation``
   — the new enqueue helper. Validates that missing/invalid initiative_id is
   refused BEFORE the task hits the broker, and that a valid enqueue writes a
   durable ``AgentExecution`` provenance row carrying every identifier the
   spec requires (task_name, celery_task_id, initiative_id, stage_id,
   source_execution_id, trace_id).

2. ``core.tasks_initiatives._impl_generate_initiative_stage_document`` — the
   task body's new ``Initiative.DoesNotExist`` guardrail. The task must NOT
   hard-fail or retry, must return a typed no-op outcome, and must reconcile
   the queue-provenance row via ``celery_task_id`` correlation.

3. ``core.services.initiative_stage_dispatch.mark_task_outcome`` — the
   reconciliation helper the task body calls from its success + failure
   branches. Only touches rows still in ``pending`` / ``in_progress``.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_initiative_stage_dispatch -v2 --keepdb
"""
from __future__ import annotations

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as _DjangoValidationError  # noqa: F401
from django.test import TestCase

from core.models_document_registry import Initiative, InitiativeStage
from core.models_unified_system import Agent, AgentExecution
from core.services import initiative_stage_dispatch as dispatch

User = get_user_model()


def _make_owner(username: str):
    """UnifiedUser owner required by Initiative (I-0302 Phase 3 A1)."""
    return User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='x',  # test-only fixture
    )


DISPATCH_PATH = 'core.services.initiative_stage_dispatch.generate_initiative_stage_document'


class _FakeAsyncResult:
    """Stand-in for ``celery.result.AsyncResult`` from ``.delay(...)``."""

    def __init__(self, task_id: str) -> None:
        self.id = task_id


def _patched_delay(task_id: str = 'fake-celery-task-id'):
    """Patch ``.delay`` to return a fake AsyncResult without hitting the broker.

    ``queue_stage_document_generation`` does ``from core.tasks import
    generate_initiative_stage_document`` at call time, so the patch has to
    target the definition module (``core.tasks``) — patching the dispatch
    module namespace would only take effect after the first import.
    """
    fake_task = mock.MagicMock()
    fake_task.delay.return_value = _FakeAsyncResult(task_id)
    return mock.patch(
        'core.tasks.generate_initiative_stage_document',
        fake_task,
    )


class QueueStageDocumentGenerationValidationTests(TestCase):
    """§Acceptance criterion 2 — enqueue-side validation refuses bad inputs
    BEFORE the task is queued so downstream work is never wasted."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = _make_owner('s2982-dispatch-validation')
        cls.initiative = Initiative.objects.create(
            name='S2982 dispatch validation initiative',
            status='ACTIVE',
            current_stage=1,
            owner=cls.owner,
        )

    def _agent_execution_count(self, **filters) -> int:
        return AgentExecution.objects.filter(**filters).count()

    def test_missing_initiative_id_refuses_enqueue(self):
        with _patched_delay() as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                '', 1, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'missing_initiative_id')
        self.assertIsNone(outcome['task_id'])
        self.assertIsNone(outcome['provenance_execution_id'])
        fake_task.delay.assert_not_called()

    def test_none_initiative_id_refuses_enqueue(self):
        with _patched_delay() as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                None, 1, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'missing_initiative_id')
        fake_task.delay.assert_not_called()

    def test_malformed_uuid_refuses_enqueue(self):
        # S2982 T1 §4c mitigation: malformed UUID is a distinct reason
        # code from initiative_not_found so operators can triage them
        # differently in the post-mortem.
        with _patched_delay() as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                'not-a-uuid-at-all', 1, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'invalid_initiative_id_format')
        fake_task.delay.assert_not_called()
        # No provenance row for refused enqueues — the Initiative wasn't real,
        # so we have no valid parent_object_id to hang the receipt off.
        self.assertEqual(
            self._agent_execution_count(owner_agent=dispatch.DISPATCH_AGENT_NAME),
            0,
        )

    def test_nonexistent_initiative_refuses_enqueue(self):
        random_id = str(uuid.uuid4())
        with _patched_delay() as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                random_id, 1, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'initiative_not_found')
        self.assertIn(random_id, outcome['initiative_id'])
        fake_task.delay.assert_not_called()

    def test_invalid_stage_num_refuses_enqueue(self):
        with _patched_delay() as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                str(self.initiative.id), 0, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'invalid_stage_num')
        fake_task.delay.assert_not_called()

    def test_out_of_range_stage_num_refuses_enqueue(self):
        with _patched_delay() as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                str(self.initiative.id), 6, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'invalid_stage_num')
        fake_task.delay.assert_not_called()


class QueueStageDocumentGenerationProvenanceTests(TestCase):
    """§Acceptance criterion 3 — provenance at enqueue time is queryable via
    ORM and carries every identifier the spec calls out."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = _make_owner('s2982-dispatch-provenance')
        cls.initiative = Initiative.objects.create(
            name='S2982 dispatch provenance initiative',
            status='ACTIVE',
            current_stage=1,
            owner=cls.owner,
        )
        cls.stage = InitiativeStage.objects.create(
            initiative=cls.initiative,
            stage=1,
            status='PENDING',
        )

    def test_success_creates_provenance_row_wired_to_celery_task_id(self):
        source_execution_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        task_id = f'celery-task-{uuid.uuid4()}'
        with _patched_delay(task_id) as fake_task:
            outcome = dispatch.queue_stage_document_generation(
                str(self.initiative.id), 1,
                source_execution_id=source_execution_id,
                trace_id=trace_id,
                triggered_by='unit-test.provenance',
            )
        self.assertTrue(outcome['success'])
        self.assertEqual(outcome['task_id'], task_id)
        self.assertIsNotNone(outcome['provenance_execution_id'])
        fake_task.delay.assert_called_once_with(
            str(self.initiative.id), 1,
        )

        row = AgentExecution.objects.get(id=outcome['provenance_execution_id'])
        # Correlation identifiers — the acceptance criterion enumerates these.
        self.assertEqual(row.celery_task_id, task_id)
        self.assertEqual(row.input_data['task_name'], dispatch.DISPATCH_TASK_NAME)
        self.assertEqual(row.input_data['initiative_id'], str(self.initiative.id))
        self.assertEqual(row.input_data['stage_num'], 1)
        self.assertEqual(row.input_data['stage_id'], str(self.stage.id))
        self.assertEqual(row.input_data['source_execution_id'], source_execution_id)
        self.assertEqual(row.input_data['triggered_by'], 'unit-test.provenance')
        self.assertEqual(str(row.trace_id), trace_id)
        # Wired to the initiative so an initiative-scoped audit query surfaces it.
        self.assertEqual(row.parent_object_type, 'initiative')
        self.assertEqual(str(row.parent_object_id), str(self.initiative.id))
        # Status reflects that the task is queued (in_progress) rather than
        # pending — otherwise a Celery FAILURE could not distinguish "never
        # enqueued" from "enqueued and running".
        self.assertEqual(row.status, 'in_progress')

    def test_synthetic_dispatch_agent_is_reused_across_enqueues(self):
        with _patched_delay('task-a'):
            dispatch.queue_stage_document_generation(
                str(self.initiative.id), 1, triggered_by='unit-test',
            )
        with _patched_delay('task-b'):
            dispatch.queue_stage_document_generation(
                str(self.initiative.id), 1, triggered_by='unit-test',
            )
        self.assertEqual(
            Agent.objects.filter(name=dispatch.DISPATCH_AGENT_NAME).count(),
            1,
            'the synthetic dispatch Agent row must be created idempotently',
        )
        self.assertEqual(
            AgentExecution.objects.filter(
                owner_agent=dispatch.DISPATCH_AGENT_NAME,
            ).count(),
            2,
        )

    def test_delay_failure_marks_provenance_failed(self):
        """If ``.delay()`` itself raises (e.g., broker down), the provenance
        row must be marked failed so the queue receipt matches reality."""
        fake_task = mock.MagicMock()
        fake_task.delay.side_effect = RuntimeError('broker unreachable')
        with mock.patch(
            'core.tasks.generate_initiative_stage_document',
            fake_task,
        ):
            outcome = dispatch.queue_stage_document_generation(
                str(self.initiative.id), 1, triggered_by='unit-test',
            )
        self.assertFalse(outcome['success'])
        self.assertEqual(outcome['reason'], 'enqueue_error')
        row = AgentExecution.objects.get(id=outcome['provenance_execution_id'])
        self.assertEqual(row.status, 'failed')
        self.assertIn('broker unreachable', row.error_message)


class MarkTaskOutcomeTests(TestCase):
    """Reconciliation contract used by the task body's success + failure
    branches."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = _make_owner('s2982-mark-task-outcome')
        cls.initiative = Initiative.objects.create(
            name='S2982 mark_task_outcome initiative',
            status='ACTIVE',
            current_stage=1,
            owner=cls.owner,
        )

    def _create_queue_row(self, celery_task_id: str, status: str = 'in_progress'):
        agent, _ = Agent.objects.get_or_create(
            name=dispatch.DISPATCH_AGENT_NAME,
            defaults={'agent_type': 'system', 'description': '', 'specialization': ''},
        )
        return AgentExecution.objects.create(
            agent=agent,
            user=None,
            task='queue receipt for mark_task_outcome test',
            status=status,
            owner_agent=dispatch.DISPATCH_AGENT_NAME,
            parent_object_type='initiative',
            parent_object_id=self.initiative.id,
            celery_task_id=celery_task_id,
            input_data={'source': 'test'},
            output_data={},
        )

    def test_marks_matching_row_failed_with_error(self):
        row = self._create_queue_row('task-abc-1', status='in_progress')
        updated = dispatch.mark_task_outcome(
            celery_task_id='task-abc-1',
            status='failed',
            error='Initiative not found: DoesNotExist',
        )
        self.assertEqual(updated, 1)
        row.refresh_from_db()
        self.assertEqual(row.status, 'failed')
        self.assertIn('Initiative not found', row.error_message)
        self.assertIsNotNone(row.completed_at)

    def test_does_not_touch_already_completed_row(self):
        row = self._create_queue_row('task-abc-2', status='completed')
        updated = dispatch.mark_task_outcome(
            celery_task_id='task-abc-2', status='failed',
        )
        self.assertEqual(updated, 0)
        row.refresh_from_db()
        self.assertEqual(row.status, 'completed')

    def test_no_op_without_celery_task_id(self):
        self.assertEqual(dispatch.mark_task_outcome(
            celery_task_id=None, status='failed',
        ), 0)
        self.assertEqual(dispatch.mark_task_outcome(
            celery_task_id='', status='failed',
        ), 0)


class StageDocumentTaskMissingInitiativeGuardrailTests(TestCase):
    """§Acceptance criterion 1 + 4 — the task body itself must handle a
    missing/invalid initiative_id safely (typed no-op, no retry, no unhandled
    exception) AND reconcile the correlated AgentExecution row so a Celery
    FAILURE never shows a "completed" AgentExecution for the same run.
    """

    @classmethod
    def setUpTestData(cls):
        cls.owner = _make_owner('s2982-task-guardrail')
        cls.initiative_for_provenance = Initiative.objects.create(
            name='S2982 task guardrail initiative',
            status='ACTIVE',
            current_stage=1,
            owner=cls.owner,
        )

    def _make_bound_task_double(self, celery_task_id: str):
        """Stand-in for the bound-task ``self`` a Celery task receives.

        Under real execution the ``AgentExecution.pre_save`` signal reads
        ``celery.current_task.request.id`` to stamp ``celery_task_id`` on any
        rows created inside the task body. In tests we invoke the ``_impl_*``
        function directly (Celery not running), so we synthesize a ``self``
        exposing ``.request.id`` for the task-body code path.
        """
        request_double = mock.MagicMock()
        request_double.id = celery_task_id
        self_double = mock.MagicMock()
        self_double.request = request_double
        # ``.retry()`` must be assertable — if the task calls it on the missing-
        # initiative branch, the guardrail is broken.
        self_double.retry = mock.MagicMock(
            side_effect=AssertionError('retry() must not be called on missing initiative'),
        )
        return self_double

    def _seed_queue_provenance(self, celery_task_id: str):
        """Simulate the row that ``queue_stage_document_generation`` would
        have written at enqueue time. Lets us assert reconciliation."""
        agent, _ = Agent.objects.get_or_create(
            name=dispatch.DISPATCH_AGENT_NAME,
            defaults={'agent_type': 'system', 'description': '', 'specialization': ''},
        )
        return AgentExecution.objects.create(
            agent=agent,
            user=None,
            task='queue receipt (test seed)',
            status='in_progress',
            owner_agent=dispatch.DISPATCH_AGENT_NAME,
            parent_object_type='initiative',
            parent_object_id=self.initiative_for_provenance.id,
            celery_task_id=celery_task_id,
            input_data={'source': dispatch._PROVENANCE_SOURCE, 'stage_num': 1},
            output_data={},
        )

    def test_missing_initiative_returns_typed_no_op_without_retry(self):
        from core.tasks_initiatives import _impl_generate_initiative_stage_document

        missing_id = str(uuid.uuid4())
        celery_task_id = f'guardrail-task-{uuid.uuid4()}'
        self_double = self._make_bound_task_double(celery_task_id)

        result = _impl_generate_initiative_stage_document(
            self_double, missing_id, 1,
        )

        self.assertIsInstance(result, dict)
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'initiative_not_found')
        self.assertEqual(result['initiative_id'], missing_id)
        self.assertEqual(result['stage'], 1)
        self.assertEqual(result['celery_task_id'], celery_task_id)
        # The load-bearing assertion: the task did NOT retry.
        self_double.retry.assert_not_called()

    def test_missing_initiative_reconciles_queue_provenance_row(self):
        from core.tasks_initiatives import _impl_generate_initiative_stage_document

        missing_id = str(uuid.uuid4())
        celery_task_id = f'guardrail-task-{uuid.uuid4()}'
        provenance_row = self._seed_queue_provenance(celery_task_id)
        self_double = self._make_bound_task_double(celery_task_id)

        _impl_generate_initiative_stage_document(self_double, missing_id, 1)

        provenance_row.refresh_from_db()
        self.assertEqual(
            provenance_row.status, 'failed',
            'queue provenance row must be reconciled to failed so a Celery '
            'FAILURE does not appear as a completed AgentExecution',
        )
        self.assertIn('Initiative not found', provenance_row.error_message)
        self.assertIsNotNone(provenance_row.completed_at)

    def test_malformed_uuid_returns_typed_no_op_without_retry(self):
        # S2982 T1 §4c mitigation: malformed UUID surfaces as a distinct
        # reason so operators can distinguish "caller passed junk" from
        # "initiative was deleted".
        from core.tasks_initiatives import _impl_generate_initiative_stage_document

        celery_task_id = f'guardrail-task-{uuid.uuid4()}'
        self_double = self._make_bound_task_double(celery_task_id)

        result = _impl_generate_initiative_stage_document(
            self_double, 'not-a-uuid-at-all', 1,
        )

        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'invalid_initiative_id_format')
        self_double.retry.assert_not_called()

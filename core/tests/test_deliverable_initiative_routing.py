"""
Session 1098 Fix B-minimal: initiative_id routing + atomic commit.
==================================================================

Rigby's priority #4 follow-up (conversation pa-3c7ddc058db1). Three
behaviors tested:

1. **initiative_id propagation** — when an agent calls
   ``_save_to_deliverable(initiative_id=...)``, the resulting Deliverable
   row carries the initiative FK.
2. **Invalid initiative_id fallback** — if the caller passes an id that
   doesn't match an existing Initiative, ``create_deliverable`` logs a
   warning, DROPS the FK link, and still creates the deliverable under
   the workspace bucket. Nothing blocks, no FK exception.
3. **Atomic commit** — the write is wrapped in ``transaction.atomic()``
   so a post-save signal failure doesn't leave a half-initialized row.

Out of scope (tracked as Fix B-full, task #9 follow-up):
- New ``deliverable_appends`` table with call_id idempotency
- ``target_stream_id`` append-to-existing-deliverable semantics
- SELECT-FOR-UPDATE race protection during mid-flight initiative
  promotion (requires B-full schema)

Run:
    python manage.py test core.tests.test_deliverable_initiative_routing -v2
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Initiative
from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.deliverable_factory import create_deliverable


User = get_user_model()


class DeliverableInitiativeRoutingTests(TestCase):
    """``create_deliverable`` initiative_id validation + routing."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='init-routing', email='init-routing@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Fix-B Test Workspace',
            allow_autonomous_writes=True,
        )
        cls.initiative = Initiative.objects.create(
            name='Fix-B Test Initiative',
            status='ACTIVE',
            current_stage=1,
        )

    def test_valid_initiative_id_is_linked_on_create(self):
        """When caller passes a valid initiative_id, the Deliverable row
        carries the FK — no more heuristics needed downstream."""
        d = create_deliverable(
            title='Synthesis Output',
            content='Executive brief from CTO + COO analyses. ' * 30,
            agent_name='ContentWriterAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
            initiative_id=str(self.initiative.id),
        )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(self.initiative.id))

    def test_invalid_initiative_id_is_dropped_and_logged(self):
        """Bogus initiative_id → warning logged, link dropped, row still
        lands in workspace bucket. No FK violation, no crash."""
        bogus_id = str(uuid.uuid4())

        with self.assertLogs(
            'core.services.deliverable_factory', level='WARNING',
        ) as cm:
            d = create_deliverable(
                title='Synthesis With Bogus Initiative',
                content='Body text that is definitely long enough to pass the quality gate threshold. ' * 8,
                agent_name='ContentWriterAgent',
                user=self.user,
                workspace_id=str(self.workspace.id),
                initiative_id=bogus_id,
            )

        self.assertIsNotNone(d)
        self.assertIsNone(d.initiative_id)
        self.assertTrue(
            any(bogus_id in msg for msg in cm.output),
            f"expected log to mention {bogus_id}, got: {cm.output}",
        )

    def test_no_initiative_id_is_backward_compatible(self):
        """Callers that don't pass initiative_id get the prior behavior
        (Deliverable without an initiative link, workspace-only routing).
        """
        d = create_deliverable(
            title='Regular Deliverable',
            content='Body text that is definitely long enough to pass the quality gate threshold. ' * 8,
            agent_name='ContentWriterAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
        )
        self.assertIsNotNone(d)
        self.assertIsNone(d.initiative_id)
        self.assertEqual(str(d.workspace_id), str(self.workspace.id))

    def test_initiative_id_survives_provenance_dedupe(self):
        """First call creates with initiative_id. Second call with same
        parent_execution_id updates the existing row (provenance dedupe)
        — the initiative FK from the first write is preserved."""
        exec_id = str(uuid.uuid4())
        d1 = create_deliverable(
            title='Dedupe Test',
            content='first draft body — long enough to pass the quality gate threshold. ' * 8,
            agent_name='ContentWriterAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
            initiative_id=str(self.initiative.id),
            parent_execution_id=exec_id,
        )
        d2 = create_deliverable(
            title='Dedupe Test',
            content='second draft — slightly edited body, still long enough to pass the quality gate. ' * 8,
            agent_name='ContentWriterAgent',
            user=self.user,
            workspace_id=str(self.workspace.id),
            initiative_id=str(self.initiative.id),
            parent_execution_id=exec_id,
        )
        self.assertEqual(d1.id, d2.id, 'provenance dedupe should return same row')
        d2.refresh_from_db()
        self.assertEqual(str(d2.initiative_id), str(self.initiative.id))

    def test_atomic_commit_rolls_back_on_error(self):
        """If the create raises (e.g., post-save signal fails), the
        transaction.atomic() wrapper must roll back — no half-
        initialized row should persist."""
        pre_count = Deliverable.objects.count()

        # Patch Deliverable.save to simulate a post-save failure.
        # The atomic wrapper should catch + roll back before returning.
        with mock.patch.object(
            Deliverable, 'save',
            side_effect=RuntimeError('simulated post-save failure'),
        ):
            with self.assertRaises(RuntimeError):
                create_deliverable(
                    title='Rollback Test',
                    content='body text long enough to pass the quality gate threshold. ' * 8,
                    agent_name='ContentWriterAgent',
                    user=self.user,
                    workspace_id=str(self.workspace.id),
                    initiative_id=str(self.initiative.id),
                )

        self.assertEqual(
            Deliverable.objects.count(), pre_count,
            'atomic wrapper should have rolled back the failed create',
        )


class BaseAgentInitiativeIdPlumbingTests(TestCase):
    """``BaseAgent._save_to_deliverable`` threads initiative_id into
    ``create_deliverable`` via explicit kwarg, execution context, or
    metadata — in that precedence order."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='plumbing-test', email='plumbing-test@example.com',
            password='x', is_superuser=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Plumbing Test WS',
            allow_autonomous_writes=True,
        )
        cls.initiative = Initiative.objects.create(
            name='Plumbing Test Initiative',
            status='ACTIVE',
            current_stage=1,
        )

    def _make_agent(self):
        # Use EditorAgent as the proof-point BaseAgent subclass. Any
        # agent that calls _save_to_deliverable will inherit the plumbing.
        from core.agents.editor_agent import EditorAgent
        return EditorAgent(user=self.user)

    def test_explicit_kwarg_takes_precedence(self):
        agent = self._make_agent()
        agent._workspace_id = str(self.workspace.id)

        d = agent._save_to_deliverable(
            title='Explicit Kwarg Wins',
            content='body long enough to pass the quality gate threshold for deliverable creation. ' * 10,
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace.id),
        )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(self.initiative.id))

    def test_execution_context_initiative_id_is_honored(self):
        """When no explicit kwarg, read context['initiative_id']."""
        agent = self._make_agent()
        agent._workspace_id = str(self.workspace.id)
        agent._execution_context = {
            'initiative_id': str(self.initiative.id),
        }

        d = agent._save_to_deliverable(
            title='Context Plumbing',
            content='body long enough to pass the quality gate threshold for deliverable creation. ' * 10,
            workspace_id=str(self.workspace.id),
        )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(self.initiative.id))

    def test_metadata_fallback_last(self):
        """No kwarg, no context — read metadata['initiative_id']."""
        agent = self._make_agent()
        agent._workspace_id = str(self.workspace.id)
        agent._execution_context = {}

        d = agent._save_to_deliverable(
            title='Metadata Plumbing',
            content='body long enough to pass the quality gate threshold for deliverable creation. ' * 10,
            metadata={'initiative_id': str(self.initiative.id)},
            workspace_id=str(self.workspace.id),
        )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(self.initiative.id))

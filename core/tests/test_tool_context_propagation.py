"""Session 1199 — Tool-context propagation regression tests.

Covers the §6.2 Phase 2 cascade Step 2 activation (Session 1199):

A. ``core/services/tool_context.py`` — contextvar + scope manager
B. ``core/services/tool_dispatcher.py:execute()`` — wraps dispatch
   with ``tool_context_scope(payload)``
C. ``core/services/deliverable_factory.py:create_deliverable()`` —
   reads contextvar via ``get_current_tool_context()`` and passes to
   ``infer_initiative_id()``

Acceptance criteria (Session 1199 spec addition):
- AC20 → test_scope_manager_sets_and_clears_contextvar
- AC21 → test_step2_fires_when_tool_context_carries_initiative_id
- AC22 → test_factory_reads_contextvar_for_unseeded_agent
- AC23 → test_scope_nested_restores_outer_context

Local-run note (Session 1195/1196/1197/1198 carryover): pgbouncer
blocks ``manage.py test`` locally; CI runs against direct Postgres.
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.services.initiative_inference import infer_initiative_id
from core.services.tool_context import (
    get_current_tool_context,
    tool_context_scope,
)


User = get_user_model()


def _make_workspace_fixture(cls):
    cls.user = User.objects.create_user(
        username=f'ctx-test-{uuid.uuid4().hex[:8]}',
        email='ctx-test@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace = ProjectWorkspace.objects.create(
        user=cls.user, name='Tool Context Test Workspace',
        allow_autonomous_writes=True,
    )


# ────────────────────────────────────────────────────────────────────────
# ContextVar lifecycle (AC20 + AC23)
# ────────────────────────────────────────────────────────────────────────


class ContextVarLifecycleTest(TestCase):
    def test_scope_manager_sets_and_clears_contextvar(self):
        """AC20 — scope sets contextvar inside, clears on exit."""
        self.assertIsNone(get_current_tool_context())
        with tool_context_scope({'initiative_id': 'abc-123'}):
            self.assertEqual(
                get_current_tool_context(),
                {'initiative_id': 'abc-123'},
            )
        self.assertIsNone(get_current_tool_context())

    def test_scope_with_empty_payload_is_passthrough(self):
        with tool_context_scope({}):
            self.assertIsNone(get_current_tool_context())

    def test_scope_with_none_is_passthrough(self):
        with tool_context_scope(None):
            self.assertIsNone(get_current_tool_context())

    def test_scope_with_payload_missing_initiative_id_skips(self):
        """Payload without initiative_id doesn't write an empty ctx."""
        with tool_context_scope({'workspace_id': 'ws-xyz'}):
            self.assertIsNone(get_current_tool_context())

    def test_scope_nested_restores_outer_context(self):
        """AC23 — nested scopes restore outer ctx on inner exit."""
        with tool_context_scope({'initiative_id': 'outer-1'}):
            self.assertEqual(
                get_current_tool_context(), {'initiative_id': 'outer-1'},
            )
            with tool_context_scope({'initiative_id': 'inner-2'}):
                self.assertEqual(
                    get_current_tool_context(),
                    {'initiative_id': 'inner-2'},
                )
            # Outer restored
            self.assertEqual(
                get_current_tool_context(), {'initiative_id': 'outer-1'},
            )
        self.assertIsNone(get_current_tool_context())

    def test_extra_payload_fields_ignored(self):
        """Only initiative_id propagates; other fields are dropped."""
        with tool_context_scope({
            'initiative_id': 'abc',
            'action': 'create',
            'workspace_id': 'ws',
            'noise_field': 'whatever',
        }):
            ctx = get_current_tool_context()
            self.assertEqual(set(ctx.keys()), {'initiative_id'})


# ────────────────────────────────────────────────────────────────────────
# Inference Step 2 activation (AC21)
# ────────────────────────────────────────────────────────────────────────


class InferenceStep2ActivationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_workspace_fixture(cls)

    def test_step2_fires_when_tool_context_carries_initiative_id(self):
        """AC21 — agent with no affinity row gets attachment via Step 2."""
        init = Initiative.objects.create(
            name=f'Step2 Target {uuid.uuid4().hex[:6]}',
            kind='project',
            target_workspace=self.workspace,
        )

        init_id, trace = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            tool_context={'initiative_id': str(init.id)},
            owner_agent='UnseededAgent',
        )
        self.assertEqual(str(init_id), str(init.id))
        self.assertEqual(trace['step'], 2)
        self.assertEqual(trace['confidence'], 0.95)
        self.assertEqual(trace['reason'], 'explicit_match')

    def test_step2_cross_workspace_falls_through(self):
        other_ws = ProjectWorkspace.objects.create(
            user=self.user, name='Other Workspace',
            allow_autonomous_writes=True,
        )
        init = Initiative.objects.create(
            name=f'Wrong-WS Target {uuid.uuid4().hex[:6]}',
            kind='project',
            target_workspace=other_ws,
        )
        init_id, trace = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            tool_context={'initiative_id': str(init.id)},
            owner_agent='UnseededAgent',
        )
        # Step 2 found the init but workspace mismatched → cascade continues
        # → no affinity for UnseededAgent → step 5 fall-through.
        self.assertIsNone(init_id)
        self.assertEqual(trace['step'], 5)


# ────────────────────────────────────────────────────────────────────────
# Factory integration (AC22)
# ────────────────────────────────────────────────────────────────────────


class FactoryReadsContextVarTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_workspace_fixture(cls)

    def test_factory_reads_contextvar_for_unseeded_agent(self):
        """AC22 — create_deliverable() picks up tool_context.initiative_id
        via the contextvar even when no affinity row exists for the
        agent."""
        from core.services.deliverable_factory import create_deliverable

        init = Initiative.objects.create(
            name=f'Factory Step2 Target {uuid.uuid4().hex[:6]}',
            kind='project',
            target_workspace=self.workspace,
        )

        with tool_context_scope({'initiative_id': str(init.id)}):
            d = create_deliverable(
                title='Factory contextvar pickup test for Session 1199 cascade',
                content=('Verifying that Step 2 fires for an unseeded agent. ' * 20),
                agent_name='UnseededAgent',
                workspace_id=str(self.workspace.id),
                deliverable_type='document',
                metadata={'trigger_source': 'test_factory_reads_contextvar'},
            )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(init.id))

    def test_factory_without_contextvar_still_falls_through_to_orphan(self):
        """Without tool_context AND without affinity, deliverable still
        saves but lands orphan-flagged (Plan C Phase 1 path)."""
        from core.services.deliverable_factory import create_deliverable

        # No scope set — contextvar is None
        d = create_deliverable(
            title='No-context fallthrough test for Session 1199',
            content=('Should fall through to Plan C diagnostic. ' * 20),
            agent_name='UnseededAgent',
            workspace_id=str(self.workspace.id),
            deliverable_type='document',
        )
        self.assertIsNotNone(d)
        self.assertIsNone(d.initiative_id)
        self.assertEqual(d.diagnostic_status, 'diagnostic')

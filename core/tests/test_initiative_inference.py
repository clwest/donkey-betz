"""Session 1198 — §6.2 Phase 2 inference cascade regression tests.

Covers the four production hooks shipped in PRs #2425-#2428:

A. AgentInitiativeAffinity model + migration (PR1A #2425)
B. seed_agent_initiative_affinities mgmt cmd (PR1B #2426)
C. infer_initiative_id() pure cascade (PR1C #2427)
D. deliverable_factory.create_deliverable() hook (PR1D #2428)

Acceptance criteria mapping (from INITIATIVES_FIRST_BACKBONE.md §7):
- AC16 → test_step1_explicit_id_returns_immediately
- AC17 → test_step3_kind_policy_blocks_recurring_artifact
- AC18 → test_factory_hook_attaches_inferred_initiative
- AC19 → test_inference_failure_falls_through_to_orphan_path

Local-run note (Session 1195/1196/1197 PR #5 carryover):
    pgbouncer transaction pool blocks ``manage.py test`` locally.
    CI runs against direct Postgres. Workaround: set
    DJANGO_TEST_DATABASE_URL or use docker-compose Postgres.
"""

import io
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models_document_registry import Initiative
from core.models_inference import AgentInitiativeAffinity
from core.models_skin_layer import ProjectWorkspace
from core.services.initiative_inference import (
    INVESTIGATION_CONFIDENCE_FLOOR,
    INVESTIGATION_RECENCY_DAYS,
    PROJECT_CONFIDENCE_FLOOR,
    PROJECT_RECENCY_DAYS,
    infer_initiative_id,
)


User = get_user_model()


def _make_user_and_workspace(cls):
    cls.user = User.objects.create_user(
        username=f'inf-test-{uuid.uuid4().hex[:8]}',
        email='inf-test@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace = ProjectWorkspace.objects.create(
        user=cls.user, name='Inference Test Workspace',
        allow_autonomous_writes=True,
    )
    cls.other_workspace = ProjectWorkspace.objects.create(
        user=cls.user, name='Other Workspace',
        allow_autonomous_writes=True,
    )


def _make_initiative(workspace, *, kind='project', name=None, updated_at_offset_days=0):
    init = Initiative.objects.create(
        name=name or f'Test Initiative {uuid.uuid4().hex[:6]}',
        kind=kind,
        target_workspace=workspace,
    )
    if updated_at_offset_days:
        # Force updated_at into the past by bypassing auto_now via .update()
        Initiative.objects.filter(id=init.id).update(
            updated_at=timezone.now() - timedelta(days=updated_at_offset_days),
        )
        init.refresh_from_db()
    return init


def _make_affinity(workspace, agent_name, initiative, **kwargs):
    return AgentInitiativeAffinity.objects.create(
        workspace=workspace,
        agent_name=agent_name,
        initiative=initiative,
        **kwargs,
    )


# ────────────────────────────────────────────────────────────────────────
# Step 1 — explicit payload initiative_id (AC16)
# ────────────────────────────────────────────────────────────────────────


class Step1ExplicitTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_user_and_workspace(cls)

    def test_step1_explicit_id_returns_immediately(self):
        """AC16 — explicit initiative_id in payload short-circuits cascade."""
        init = _make_initiative(self.workspace, kind='project')
        result_id, trace = infer_initiative_id(
            payload={
                'workspace_id': str(self.workspace.id),
                'initiative_id': str(init.id),
            },
        )
        self.assertEqual(str(result_id), str(init.id))
        self.assertEqual(trace['step'], 1)
        self.assertEqual(trace['reason'], 'explicit_match')
        self.assertEqual(trace['confidence'], 1.0)

    def test_step1_explicit_cross_workspace_falls_through(self):
        """Explicit id pointing at wrong workspace falls through cascade."""
        init = _make_initiative(self.other_workspace, kind='project')
        result_id, trace = infer_initiative_id(
            payload={
                'workspace_id': str(self.workspace.id),
                'initiative_id': str(init.id),
            },
        )
        # Cross-workspace → fall through to step 5 (no affinity exists either)
        self.assertIsNone(result_id)
        self.assertEqual(trace['step'], 5)

    def test_step1_explicit_recurring_artifact_still_attaches(self):
        """Explicit id allows kind=recurring_artifact (caller opted in)."""
        init = _make_initiative(self.workspace, kind='recurring_artifact')
        result_id, trace = infer_initiative_id(
            payload={
                'workspace_id': str(self.workspace.id),
                'initiative_id': str(init.id),
            },
        )
        self.assertEqual(str(result_id), str(init.id))
        self.assertEqual(trace['step'], 1)
        self.assertEqual(trace['kind'], 'recurring_artifact')

    def test_guard_no_workspace_id(self):
        """Missing workspace_id → guard fires immediately."""
        result_id, trace = infer_initiative_id(payload={})
        self.assertIsNone(result_id)
        self.assertEqual(trace['step'], 'guard')


# ────────────────────────────────────────────────────────────────────────
# Step 3 — agent affinity + kind policy (AC17)
# ────────────────────────────────────────────────────────────────────────


class Step3AffinityKindPolicyTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_user_and_workspace(cls)

    def test_step3_project_attach_meets_all_thresholds(self):
        init = _make_initiative(self.workspace, kind='project')
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.95)
        result_id, trace = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertEqual(str(result_id), str(init.id))
        self.assertEqual(trace['step'], 3)
        self.assertEqual(trace['reason'], 'affinity_match')
        self.assertEqual(trace['kind'], 'project')

    def test_step3_kind_policy_blocks_recurring_artifact(self):
        """AC17 — recurring_artifact never attaches via inference."""
        init = _make_initiative(self.workspace, kind='recurring_artifact')
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.95)
        result_id, trace = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)
        # Rejected at step 3 → fall through to step 5
        self.assertEqual(trace['step'], 5)
        # First rejection in the trace should cite the kind block
        step3_trace = trace.get('step_3_trace', {})
        rejections = step3_trace.get('rejections', [])
        self.assertTrue(
            any(r.get('reason') == 'kind_blocked_from_inference' for r in rejections),
            f"Expected kind_blocked_from_inference rejection, got: {rejections}",
        )

    def test_step3_kind_policy_blocks_spec_backlog(self):
        init = _make_initiative(self.workspace, kind='spec_backlog')
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.95)
        result_id, _ = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)

    def test_step3_project_recency_floor_blocks_stale(self):
        """Project initiative older than 7 days → blocked."""
        init = _make_initiative(
            self.workspace, kind='project',
            updated_at_offset_days=PROJECT_RECENCY_DAYS + 1,
        )
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.95)
        result_id, _ = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)

    def test_step3_investigation_recency_floor_allows_30d_window(self):
        """Investigation initiative within 30 days → allowed."""
        init = _make_initiative(
            self.workspace, kind='investigation',
            updated_at_offset_days=INVESTIGATION_RECENCY_DAYS - 1,
        )
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.80)
        result_id, trace = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertEqual(str(result_id), str(init.id))
        self.assertEqual(trace['kind'], 'investigation')

    def test_step3_confidence_floor_blocks_below_threshold(self):
        """project requires conf >= 0.90; 0.85 blocked."""
        init = _make_initiative(self.workspace, kind='project')
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.85)
        result_id, _ = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)

    def test_step3_multiple_candidates_falls_through(self):
        """Multiple valid candidates → don't auto-pick."""
        init_a = _make_initiative(self.workspace, kind='project')
        init_b = _make_initiative(self.workspace, kind='project')
        _make_affinity(self.workspace, 'TestAgent', init_a, confidence=0.95)
        _make_affinity(self.workspace, 'TestAgent', init_b, confidence=0.95)
        result_id, _ = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)

    def test_step3_expired_affinity_ignored(self):
        """expires_at < now → row not considered."""
        init = _make_initiative(self.workspace, kind='project')
        _make_affinity(
            self.workspace, 'TestAgent', init,
            confidence=0.95,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        result_id, _ = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)

    def test_step3_learned_suggestion_not_authoritative_v1(self):
        """Phase 2 v1: learned_suggestion source doesn't auto-attach."""
        init = _make_initiative(self.workspace, kind='project')
        _make_affinity(
            self.workspace, 'TestAgent', init,
            confidence=0.95,
            source=AgentInitiativeAffinity.Source.LEARNED_SUGGESTION,
        )
        result_id, _ = infer_initiative_id(
            payload={'workspace_id': str(self.workspace.id)},
            owner_agent='TestAgent',
        )
        self.assertIsNone(result_id)


# ────────────────────────────────────────────────────────────────────────
# Factory hook integration (AC18 + AC19)
# ────────────────────────────────────────────────────────────────────────


class FactoryHookIntegrationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_user_and_workspace(cls)

    def test_factory_hook_attaches_inferred_initiative(self):
        """AC18 — create_deliverable() picks up inferred initiative_id."""
        init = _make_initiative(self.workspace, kind='project',
                                 name='Hook Test Project')
        _make_affinity(self.workspace, 'TestAgent', init, confidence=0.95)

        from core.services.deliverable_factory import create_deliverable
        d = create_deliverable(
            title='Factory hook integration smoke test for inference cascade',
            content=('Long enough content to pass quality gate. ' * 20),
            agent_name='TestAgent',
            workspace_id=str(self.workspace.id),
            deliverable_type='document',
            metadata={'trigger_source': 'test_factory_hook'},
        )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(init.id))

    def test_factory_hook_explicit_initiative_id_not_overridden(self):
        """Caller-supplied initiative_id wins over inference."""
        init_inferred = _make_initiative(self.workspace, kind='project',
                                          name='Inferred Target')
        init_explicit = _make_initiative(self.workspace, kind='project',
                                          name='Explicit Target')
        _make_affinity(self.workspace, 'TestAgent', init_inferred, confidence=0.95)

        from core.services.deliverable_factory import create_deliverable
        d = create_deliverable(
            title='Explicit-id-wins integration smoke test',
            content=('Long enough content. ' * 20),
            agent_name='TestAgent',
            workspace_id=str(self.workspace.id),
            initiative_id=str(init_explicit.id),
            deliverable_type='document',
        )
        self.assertIsNotNone(d)
        self.assertEqual(str(d.initiative_id), str(init_explicit.id))

    def test_inference_failure_falls_through_to_orphan_path(self):
        """AC19 — no affinity match → deliverable still created (orphan path)."""
        from core.services.deliverable_factory import create_deliverable
        d = create_deliverable(
            title='Orphan fall-through integration smoke test',
            content=('Long enough content. ' * 20),
            agent_name='UnseededAgent',
            workspace_id=str(self.workspace.id),
            deliverable_type='document',
        )
        self.assertIsNotNone(d)
        self.assertIsNone(d.initiative_id)
        # Plan C Phase 1 marks it diagnostic
        self.assertEqual(d.diagnostic_status, 'diagnostic')


# ────────────────────────────────────────────────────────────────────────
# Seed mgmt cmd
# ────────────────────────────────────────────────────────────────────────


def _call(cmd_name, *args, **kwargs):
    out = io.StringIO()
    call_command(cmd_name, *args, stdout=out, **kwargs)
    return out.getvalue()


class SeedCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_user_and_workspace(cls)
        # SPEC references real Initiative UUIDs that exist in prod but
        # not in test DB. Create stand-ins with matching UUIDs.
        Initiative.objects.create(
            id='23cf3acb-6554-407d-958b-4298b44ddfd6',
            name='Spider Context Utilization — Retune & Implementation',
            kind='project',
            target_workspace=cls.workspace,
        )
        Initiative.objects.create(
            id='6941372d-b13c-4631-91c8-749fa65c55a0',
            name='Initiatives-First Wiring + No-Orphan Output',
            kind='project',
            target_workspace=cls.workspace,
        )

    def test_seed_dry_run_no_writes(self):
        starting = AgentInitiativeAffinity.objects.count()
        _call('seed_agent_initiative_affinities',
              '--workspace-id', str(self.workspace.id), '--json-only')
        self.assertEqual(AgentInitiativeAffinity.objects.count(), starting)

    def test_seed_apply_creates_spec_rows(self):
        _call('seed_agent_initiative_affinities', '--apply',
              '--workspace-id', str(self.workspace.id), '--json-only')
        self.assertEqual(
            AgentInitiativeAffinity.objects.filter(workspace=self.workspace).count(),
            2,
        )

    def test_seed_idempotent_on_rerun(self):
        _call('seed_agent_initiative_affinities', '--apply',
              '--workspace-id', str(self.workspace.id), '--json-only')
        _call('seed_agent_initiative_affinities', '--apply',
              '--workspace-id', str(self.workspace.id), '--json-only')
        # Still 2 rows (unique constraint blocks duplicates)
        self.assertEqual(
            AgentInitiativeAffinity.objects.filter(workspace=self.workspace).count(),
            2,
        )

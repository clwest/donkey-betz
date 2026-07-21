"""
Session 1195 — Plan C Phase 1 (Initiatives-First Backbone) regression tests.

Covers the three production hooks shipped in PRs #2402/#2403/#2404/#2405:

A. Factory create-path (deliverable_factory.create_deliverable)
B. Update-path (deliverable_tool.update via _handle_deliverables)
C. TTL sweep task (core.tasks.sweep_diagnostic_deliverables)

Test matrix derived from Rigby's Section 5.2 + PR #4 ack memo. Each case
encodes one row of the contract so it can't regress quietly.

Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C / §6.1.

Run::

    python manage.py test core.tests.test_deliverable_initiative_diagnostics -v2

Local-run note (Session 1195):
    The default local DATABASE_URL routes through pgbouncer (transaction
    pool on :5433) which can't proxy ``CREATE DATABASE`` — so Django's
    test runner can't spin up ``test_unified_donkey_betz``. CI runs
    against a direct Postgres connection and is the authoritative
    runner for this suite. To run locally, point either
    ``DJANGO_TEST_DATABASE_URL`` or ``TEST_DATABASE_URL`` at a direct
    (non-pooled) Postgres DSN with CREATEDB on the user, or run inside
    the docker-compose stack that exposes Postgres directly. Tracked
    as a separate infra follow-up — not gating this suite's CI value.

    End-to-end behavior was already smoke-verified during PRs
    #2403/#2404/#2405 against the live DB via ``manage.py shell`` with
    savepoint rollbacks. This file codifies those smoke checks for
    regression coverage.
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.services.deliverable_factory import create_deliverable
from core.services.tool_dispatcher import ToolDispatcher
from core.tasks import sweep_diagnostic_deliverables


User = get_user_model()

# Long enough to clear the factory's 300-char quality gate.
LONG = 'Plan C Phase 1 diagnostic regression test content. ' * 12


def _make_fixtures(cls):
    """Build the shared (user, workspace_A, workspace_B, initiative) graph.

    Initiative.target_workspace = workspace_A, so:
      - aligned deliverable: initiative + workspace_A
      - workspace_mismatch:  initiative + workspace_B
      - missing_initiative:  None + any workspace
    """
    cls.user = User.objects.create_user(
        username=f'plan-c-test-{uuid.uuid4().hex[:8]}',
        email='plan-c@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace_a = ProjectWorkspace.objects.create(
        user=cls.user, name='Workspace A (target)',
        allow_autonomous_writes=True,
    )
    cls.workspace_b = ProjectWorkspace.objects.create(
        user=cls.user, name='Workspace B (wrong)',
        allow_autonomous_writes=True,
    )
    cls.initiative = Initiative.objects.create(
        name='Plan C Test Initiative',
        status='ACTIVE',
        current_stage=1,
        target_workspace=cls.workspace_a,
        owner=cls.user,  # schema drift: owner became NOT NULL post-fixture-author
    )


# ────────────────────────────────────────────────────────────────────────
# A. Factory create-path
# ────────────────────────────────────────────────────────────────────────

class FactoryDiagnosticTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def _create(self, *, title, initiative_id, workspace_id):
        return create_deliverable(
            title=title,
            content=LONG,
            # S1199 PR-D contract: non-PA callers MUST pass
            # parent_execution_id; PA-direct context synthesizes it.
            # Diagnostic behavior tested here is agent-identity-agnostic.
            agent_name='PersonalAssistant',
            user=self.user,
            initiative_id=initiative_id,
            workspace_id=workspace_id,
        )

    def test_a1_missing_initiative_flags_diagnostic(self):
        """No initiative_id → diagnostic with code=missing_initiative_id, TTL ~ now+7d."""
        before = timezone.now()
        d = self._create(
            title='A1-missing',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id')
        self.assertIsNotNone(d.diagnostic_marked_at)
        self.assertIsNotNone(d.diagnostic_expires_at)
        # TTL within ±60s of 7d from now (default 168h)
        expected_expires = before + timedelta(hours=168)
        self.assertLess(abs((d.diagnostic_expires_at - expected_expires).total_seconds()), 60)
        # Payload has the audit basics
        self.assertIn('actual_workspace_id', d.diagnostic_payload)
        self.assertIn('tool', d.diagnostic_payload)
        self.assertIn('caller', d.diagnostic_payload)
        self.assertEqual(d.diagnostic_payload['actual_workspace_id'], str(self.workspace_a.id))

    def test_a2_workspace_mismatch_flags_diagnostic(self):
        """initiative.target_workspace=A but deliverable.workspace=B → workspace_mismatch."""
        d = self._create(
            title='A2-mismatch',
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_b.id),
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'workspace_mismatch')
        self.assertEqual(
            d.diagnostic_payload['expected_workspace_id'],
            str(self.workspace_a.id),
        )
        self.assertEqual(
            d.diagnostic_payload['actual_workspace_id'],
            str(self.workspace_b.id),
        )

    def test_a3_aligned_no_diagnostic(self):
        """initiative.target_workspace=A AND deliverable.workspace=A → all 5 fields NULL."""
        d = self._create(
            title='A3-aligned',
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
        )
        self.assertIsNone(d.diagnostic_status)
        self.assertIsNone(d.diagnostic_code)
        self.assertIsNone(d.diagnostic_payload)
        self.assertIsNone(d.diagnostic_marked_at)
        self.assertIsNone(d.diagnostic_expires_at)

    def test_a4_invalid_initiative_dropped_falls_into_missing(self):
        """Bogus initiative_id → factory's FK guard drops it → missing_initiative_id branch."""
        bogus = '00000000-0000-0000-0000-000000000000'
        d = self._create(
            title='A4-invalid',
            initiative_id=bogus,
            workspace_id=str(self.workspace_a.id),
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id')
        self.assertIsNone(d.initiative_id, "factory must drop the invalid FK")


# ────────────────────────────────────────────────────────────────────────
# B. Update-path hook (deliverable_tool.update via _handle_deliverables)
# ────────────────────────────────────────────────────────────────────────

class UpdateDiagnosticTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _create(self, *, initiative_id, workspace_id, title='B-test'):
        return create_deliverable(
            title=title, content=LONG,
            agent_name='PersonalAssistant',  # S1199 PR-D provenance contract
            user=self.user,
            initiative_id=initiative_id, workspace_id=workspace_id,
        )

    def _update(self, deliverable, **payload_extras):
        payload = {'action': 'update', 'id': str(deliverable.id), **payload_extras}
        return self.dispatcher._handle_deliverables(
            'deliverable_tool', payload, self.user.id, 'test-trace',
        )

    def test_b4_aligned_to_mismatch_flags_diagnostic(self):
        """Aligned create then update workspace_id→B → diagnostic mark applied."""
        d = self._create(
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
            title='B4-aligned-to-mismatch',
        )
        self.assertIsNone(d.diagnostic_status, "fixture must start aligned")
        self._update(d, workspace_id=str(self.workspace_b.id))
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'workspace_mismatch')

    def test_b5_mismatch_to_aligned_auto_clears(self):
        """Mismatched deliverable updated to correct workspace → all 5 fields NULL."""
        d = self._create(
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_b.id),
            title='B5-mismatch-to-aligned',
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self._update(d, workspace_id=str(self.workspace_a.id))
        d.refresh_from_db()
        self.assertIsNone(d.diagnostic_status)
        self.assertIsNone(d.diagnostic_code)
        self.assertIsNone(d.diagnostic_payload)
        self.assertIsNone(d.diagnostic_marked_at)
        self.assertIsNone(d.diagnostic_expires_at)

    def test_b6_missing_to_resolved_via_initiative_clears(self):
        """missing_initiative_id resolved by adding valid initiative_id → fields cleared."""
        d = self._create(
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='B6-missing-to-resolved',
        )
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id')
        self._update(d, initiative_id=str(self.initiative.id))
        d.refresh_from_db()
        self.assertIsNone(d.diagnostic_status)
        self.assertEqual(str(d.initiative_id), str(self.initiative.id))

    def test_b7_idempotent_title_only_update_no_churn(self):
        """Non-alignment-affecting update on already-diagnostic row: marked_at unchanged."""
        d = self._create(
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_b.id),
            title='B7-idempotent',
        )
        marked_at_before = d.diagnostic_marked_at
        payload_before = dict(d.diagnostic_payload)
        self._update(d, title='B7-idempotent-renamed')
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_marked_at, marked_at_before,
                         "marked_at must not advance on non-alignment update")
        self.assertEqual(d.diagnostic_payload, payload_before,
                         "payload must not churn on non-alignment update")


# ────────────────────────────────────────────────────────────────────────
# C. Sweep task (core.tasks.sweep_diagnostic_deliverables)
# ────────────────────────────────────────────────────────────────────────

class SweepDiagnosticTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def _create_diagnostic(self, *, expires_at, title):
        d = create_deliverable(
            title=title, content=LONG,
            agent_name='PersonalAssistant',  # S1199 PR-D provenance contract
            user=self.user,
            initiative_id=None, workspace_id=str(self.workspace_a.id),
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        # Override TTL to control sweep eligibility
        Deliverable.objects.filter(id=d.id).update(diagnostic_expires_at=expires_at)
        d.refresh_from_db()
        return d

    def test_c8_expired_diagnostic_archived_and_payload_augmented(self):
        """Expired diagnostic → status='archived', diag_status preserved, payload augmented."""
        past = timezone.now() - timedelta(hours=1)
        d = self._create_diagnostic(expires_at=past, title='C8-expired')

        result = sweep_diagnostic_deliverables(dry_run=False)
        self.assertGreaterEqual(result['archived'], 1)

        d.refresh_from_db()
        self.assertEqual(d.status, 'archived')
        self.assertEqual(d.diagnostic_status, 'diagnostic',
                         "option-b: diagnostic_status preserved post-archive")
        self.assertEqual(d.diagnostic_payload.get('archived_by'), 'diagnostic_sweep')
        self.assertEqual(d.diagnostic_payload.get('archived_reason'), 'ttl_expired')
        self.assertIn('archived_at', d.diagnostic_payload)

    def test_c9_future_ttl_untouched(self):
        """Diagnostic with TTL in the future → sweep does not archive."""
        future = timezone.now() + timedelta(hours=24)
        d = self._create_diagnostic(expires_at=future, title='C9-future')

        sweep_diagnostic_deliverables(dry_run=False)
        d.refresh_from_db()
        self.assertNotEqual(d.status, 'archived',
                            "fresh diagnostic must remain in lifecycle")
        self.assertNotIn(
            'archived_by', (d.diagnostic_payload or {}),
            "payload must not be augmented for non-archived row",
        )

    def test_c10_already_archived_excluded_and_idempotent_rerun(self):
        """Already-archived diagnostic excluded from sweep; rerun touches nothing new."""
        past = timezone.now() - timedelta(hours=1)
        d = self._create_diagnostic(expires_at=past, title='C10-rerun')

        first = sweep_diagnostic_deliverables(dry_run=False)
        self.assertGreaterEqual(first['archived'], 1)

        d.refresh_from_db()
        first_archived_at = d.diagnostic_payload['archived_at']

        second = sweep_diagnostic_deliverables(dry_run=False)
        # The row archived above is now excluded by .exclude(status='archived')
        # in the sweep filter.
        d.refresh_from_db()
        self.assertEqual(d.status, 'archived')
        self.assertEqual(
            d.diagnostic_payload['archived_at'], first_archived_at,
            "second sweep must not re-stamp archived_at",
        )


# ────────────────────────────────────────────────────────────────────────
# S2859 Ledger #8 — preserve_title bypass for PA/Rigby tool-surface callers
# ────────────────────────────────────────────────────────────────────────

class PreserveTitleTests(TestCase):
    """S2859 Ledger #8: `create_deliverable(preserve_title=True)` skips
    `_clean_deliverable_title` — the auto-prefix reconstruction and
    120-char cap. Wired narrowly from the PA tool-surface create path
    (`td_handlers_agents._handle_deliverables` action=create).
    """

    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def _create(self, *, title, preserve_title, agent_name='PersonalAssistant',
                initiative_id=None):
        return create_deliverable(
            title=title,
            content=LONG,
            agent_name=agent_name,
            user=self.user,
            deliverable_type='ratification_record',
            initiative_id=initiative_id,
            workspace_id=str(self.workspace_a.id),
            preserve_title=preserve_title,
        )

    def test_d1_preserve_true_keeps_verbatim_no_prefix(self):
        """preserve_title=True → title stored as-supplied, no 'Rigby:' / agent prefix."""
        title = 'RATIFICATION_20260720_PLAYBOOK_v0_9_0'
        d = self._create(title=title, preserve_title=True)
        self.assertEqual(d.title, title)
        self.assertFalse(d.title.startswith('PersonalAssistant:'))
        self.assertFalse(d.title.startswith('Rigby:'))

    def test_d2_preserve_true_bypasses_120_char_cap(self):
        """preserve_title=True → titles up to model-column limit (title[:500])
        survive without the 120-char cap that `_clean_deliverable_title`
        enforces. This is why identifier-like titles like
        `RATIFICATION_<date>_<version>_<slug>_<seq>` no longer feel polluted.
        """
        # 180 chars: comfortably exceeds the 120-char cleaner cap while
        # staying under the model's title[:500] safety truncation.
        title = 'RATIFICATION_20260720_' + ('A' * 158)
        self.assertEqual(len(title), 180)
        d = self._create(title=title, preserve_title=True)
        self.assertEqual(d.title, title,
                         "preserve_title=True must not enforce 120-char cap")
        self.assertGreater(len(d.title), 120)

    def test_d2b_preserve_true_over_255_truncates_to_column_max(self):
        """preserve_title=True with a title >255 chars must truncate to
        the actual Deliverable.title column max_length (255), not raise or
        blow past the column limit. Guards against Q5.1 (post-code Rigby)
        — the outer `kwargs['title'] = title[:255]` safety net."""
        # 400 chars: intentionally over the 255-char column max.
        title = 'RATIFICATION_' + ('X' * 387)
        self.assertEqual(len(title), 400)
        d = self._create(title=title, preserve_title=True)
        self.assertEqual(len(d.title), 255,
                         "must truncate to model column max_length")
        self.assertTrue(d.title.startswith('RATIFICATION_'))

    def test_d3_preserve_true_preserves_existing_agent_prefix(self):
        """preserve_title=True with an explicit 'Rigby: X' title keeps
        the caller's prefix verbatim — the cleaner is skipped entirely,
        so no double-prefix or agent-name substitution occurs."""
        title = 'Rigby: manual ratification note'
        d = self._create(title=title, preserve_title=True)
        self.assertEqual(d.title, title)

    def test_d4_preserve_false_regression_cleans_prompt_leakage(self):
        """preserve_title=False (default) still runs `_clean_deliverable_title`:
        raw-prompt-as-title from an agent caller gets prefix-cleaned. Uses
        non-PA `ResearchAgent` because the cleaner exists specifically for
        raw-prompt-as-title leakage from agent-execution flows; PA-direct
        callers opt into preserve_title=True (tested above)."""
        d = create_deliverable(
            title='Research: current AI trends',
            content=LONG,
            agent_name='ResearchAgent',
            user=self.user,
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
            parent_execution_id=str(uuid.uuid4()),  # S1199 PR-D contract
            # preserve_title omitted → default False
        )
        # Cleaner strips 'Research: ' prefix then re-adds display prefix.
        self.assertTrue(d.title.startswith('Research: '))
        # And leaves human-readable topic body (first letter is capitalized
        # by step 7 of the cleaner at deliverable_factory.py lines 561-563).
        self.assertIn('urrent AI trends', d.title)

    def test_d5_preserve_false_regression_idempotency_guard(self):
        """preserve_title=False on a title that already starts with the
        agent-name prefix must not double-prefix (deliverable_factory.py
        lines 571-573 idempotency guard)."""
        d = create_deliverable(
            title='ResearchAgent: existing prefix',
            content=LONG,
            agent_name='ResearchAgent',
            user=self.user,
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
            parent_execution_id=str(uuid.uuid4()),  # S1199 PR-D contract
        )
        self.assertNotIn('ResearchAgent: ResearchAgent:', d.title)


# ────────────────────────────────────────────────────────────────────────
# S2859 Ledger #9 — ratification_record type exempt from missing_initiative_id
# ────────────────────────────────────────────────────────────────────────

class RatificationTypeExemptTests(TestCase):
    """S2859 Ledger #9: `deliverable_type='ratification_record'` skips
    the `missing_initiative_id` diagnostic (governance artifacts have no
    natural initiative parent). Workspace-mismatch semantics remain
    intact for all types — the exemption is narrowly scoped."""

    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _create(self, *, deliverable_type, initiative_id, workspace_id, title):
        return create_deliverable(
            title=title, content=LONG,
            agent_name='PersonalAssistant',  # S1199 PR-D provenance contract
            user=self.user,
            deliverable_type=deliverable_type,
            initiative_id=initiative_id,
            workspace_id=workspace_id,
        )

    def test_e1_ratification_no_initiative_no_diagnostic(self):
        """ratification_record + initiative_id=None → no diagnostic mark.
        The core Ledger #9 fix: governance artifacts don't need an initiative."""
        d = self._create(
            deliverable_type='ratification_record',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='E1-ratification-no-initiative',
        )
        self.assertIsNone(d.diagnostic_status)
        self.assertIsNone(d.diagnostic_code)
        self.assertIsNone(d.diagnostic_payload)

    def test_e2_ratification_with_matching_initiative_no_diagnostic(self):
        """ratification_record + valid initiative + matching workspace →
        no diagnostic (parity with the standard aligned-create path)."""
        d = self._create(
            deliverable_type='ratification_record',
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
            title='E2-ratification-aligned',
        )
        self.assertIsNone(d.diagnostic_status)

    def test_e3_ratification_with_workspace_mismatch_still_diagnostic(self):
        """ratification_record + valid initiative + wrong workspace →
        still marks `workspace_mismatch`. The exemption is narrow: it
        only bypasses `missing_initiative_id`, not real integrity checks."""
        d = self._create(
            deliverable_type='ratification_record',
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_b.id),
            title='E3-ratification-mismatch',
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'workspace_mismatch')

    def test_e4_ratification_update_path_does_not_re_mark(self):
        """After create with no diagnostic, an unrelated update on a
        ratification_record must not re-mark `missing_initiative_id`
        via the update-path re-eval at `_handle_deliverables:2457`."""
        d = self._create(
            deliverable_type='ratification_record',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='E4-ratification-update',
        )
        self.assertIsNone(d.diagnostic_status)
        # Trigger update-path re-eval by touching a non-alignment field.
        result = self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'update', 'id': str(d.id), 'title': 'E4-ratification-renamed'},
            self.user.id,
            'test-trace-e4',
        )
        self.assertEqual(result['action'], 'update')
        d.refresh_from_db()
        self.assertIsNone(d.diagnostic_status,
                          "update on ratification_record must not re-mark diagnostic")

    def test_e5_non_exempt_type_no_initiative_still_diagnostic(self):
        """Regression: default `deliverable_type='document'` with no
        initiative_id still marks `missing_initiative_id` (existing
        Session 1195 Plan C behavior preserved)."""
        d = self._create(
            deliverable_type='document',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='E5-non-exempt-missing',
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id')

    def test_e6_non_exempt_type_update_still_re_marks(self):
        """Regression: default `deliverable_type='document'` update
        path still re-evaluates alignment (Session 1195 Plan C update
        semantics preserved for non-exempt types)."""
        d = self._create(
            deliverable_type='document',
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
            title='E6-non-exempt-update',
        )
        self.assertIsNone(d.diagnostic_status, "fixture must start aligned")
        # Flip workspace to mismatch → update path must re-mark diagnostic.
        self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'update', 'id': str(d.id),
             'workspace_id': str(self.workspace_b.id)},
            self.user.id,
            'test-trace-e6',
        )
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'workspace_mismatch')

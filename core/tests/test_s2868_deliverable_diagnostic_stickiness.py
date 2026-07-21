"""
S2868 — Deliverable diagnostic misfire fix regression suite.

Covers three orthogonal fixes shipped as one PR:

RC1. Exemption list growth (`_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` in
     `core/services/deliverable_factory.py:1404`) — adds
     engineering_backlog / engineering_record / code_review /
     session_handoff to the existing `ratification_record` exemption.

RC2. Sticky operator clear via `deliverable_tool.clear_diagnostic`
     (`core/services/td_handlers_agents.py`) — new action sets a
     `diagnostic_status='cleared'` sentinel; the update-path re-eval at
     `_handle_deliverables` respects the sentinel and suppresses
     `missing_initiative_id` re-marks. Workspace_mismatch (a stronger
     integrity signal) still fires on transition.

RC3. Empty deliverable_type normalization at the create-site
     (`_handle_deliverables` create branch) — `type=''` now normalizes
     to `'document'` before dispatch, preventing the 26 production
     orphan-typed rows the field currently holds.

Spec provenance: Rigby Tool Gap Ledger deliverable
`5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` entries #7/#17/#18 + S2868
open-slate SIGN in the S2867→S2868 handoff.

Run::

    python manage.py test core.tests.test_s2868_deliverable_diagnostic_stickiness -v2

The local-run pgbouncer note from
`test_deliverable_initiative_diagnostics.py:19-33` applies here too.
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.services.deliverable_factory import (
    _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT,
    create_deliverable,
)
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()

LONG = 'S2868 diagnostic misfire regression test content. ' * 12


def _make_fixtures(cls):
    cls.user = User.objects.create_user(
        username=f's2868-test-{uuid.uuid4().hex[:8]}',
        email='s2868@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace_a = ProjectWorkspace.objects.create(
        user=cls.user, name='S2868 Workspace A',
        allow_autonomous_writes=True,
    )
    cls.workspace_b = ProjectWorkspace.objects.create(
        user=cls.user, name='S2868 Workspace B',
        allow_autonomous_writes=True,
    )
    cls.initiative = Initiative.objects.create(
        name='S2868 Test Initiative',
        status='ACTIVE',
        current_stage=1,
        target_workspace=cls.workspace_a,
        owner=cls.user,
    )


# ────────────────────────────────────────────────────────────────────────
# RC1 — Exemption list growth
# ────────────────────────────────────────────────────────────────────────

class ExemptionListGrowthTests(TestCase):
    """New types in `_TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT` skip the
    `missing_initiative_id` diagnostic when initiative_id is None."""

    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def _create(self, *, deliverable_type, initiative_id, workspace_id, title):
        return create_deliverable(
            title=title, content=LONG,
            agent_name='PersonalAssistant',
            user=self.user,
            deliverable_type=deliverable_type,
            initiative_id=initiative_id,
            workspace_id=workspace_id,
        )

    def test_rc1_1_exemption_set_contains_all_five_types(self):
        """Regression: exemption set contains the S2868 additions +
        the S2859 seed. Guards against accidental frozenset shrinkage."""
        self.assertEqual(
            _TYPES_EXEMPT_FROM_INITIATIVE_ALIGNMENT,
            frozenset({
                'ratification_record',
                'engineering_backlog',
                'engineering_record',
                'code_review',
                'session_handoff',
            }),
        )

    def test_rc1_2_engineering_backlog_no_diagnostic(self):
        """engineering_backlog + initiative_id=None → no diagnostic.
        Rigby Tool Gap Ledger itself is this type; the exemption
        prevents her own ledger from being marked orphan."""
        d = self._create(
            deliverable_type='engineering_backlog',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='RC1-2-engineering-backlog',
        )
        self.assertIsNone(d.diagnostic_status)
        self.assertIsNone(d.diagnostic_code)

    def test_rc1_3_engineering_record_no_diagnostic(self):
        d = self._create(
            deliverable_type='engineering_record',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='RC1-3-engineering-record',
        )
        self.assertIsNone(d.diagnostic_status)

    def test_rc1_4_code_review_no_diagnostic(self):
        d = self._create(
            deliverable_type='code_review',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='RC1-4-code-review',
        )
        self.assertIsNone(d.diagnostic_status)

    def test_rc1_5_session_handoff_no_diagnostic(self):
        d = self._create(
            deliverable_type='session_handoff',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='RC1-5-session-handoff',
        )
        self.assertIsNone(d.diagnostic_status)

    def test_rc1_6_workspace_mismatch_still_fires_for_new_exempt_type(self):
        """Regression: exemption is narrowly scoped to
        missing_initiative_id — workspace_mismatch still fires for the
        new exempt types when the caller supplies a mismatched pair."""
        d = self._create(
            deliverable_type='engineering_backlog',
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_b.id),
            title='RC1-6-engineering-backlog-mismatch',
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'workspace_mismatch')

    def test_rc1_7_document_still_flags_missing_initiative(self):
        """Regression: default `document` type NOT added to exemption —
        the growth is targeted, not blanket."""
        d = self._create(
            deliverable_type='document',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='RC1-7-document-regression',
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id')

    def test_rc1_8_initiative_phase_doc_still_flags(self):
        """Regression: `initiative_phase_doc` NOT exempt (93% of production
        rows have valid initiative_id — flagging the 7% orphans is
        correct behavior, not a bug). Guards against Rigby-recommended
        DECLINED entries slipping in."""
        d = self._create(
            deliverable_type='initiative_phase_doc',
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
            title='RC1-8-initiative-phase-doc-regression',
        )
        self.assertEqual(d.diagnostic_status, 'diagnostic')
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id')


# ────────────────────────────────────────────────────────────────────────
# RC2 — Sticky manual-clear via clear_diagnostic
# ────────────────────────────────────────────────────────────────────────

class ClearDiagnosticActionTests(TestCase):
    """`deliverable_tool.clear_diagnostic` sets
    diagnostic_status='cleared' + preserves audit residue + is respected
    by the update-path re-eval."""

    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _create_orphan(self, *, deliverable_type='document', title='RC2-orphan'):
        d = create_deliverable(
            title=title, content=LONG,
            agent_name='PersonalAssistant',
            user=self.user,
            deliverable_type=deliverable_type,
            initiative_id=None,
            workspace_id=str(self.workspace_a.id),
        )
        assert d.diagnostic_status == 'diagnostic'
        assert d.diagnostic_code == 'missing_initiative_id'
        return d

    def _clear(self, d, *, reason='S2868 test manual clear'):
        return self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'clear_diagnostic', 'id': str(d.id), 'reason': reason},
            self.user.id,
            'test-trace-rc2',
        )

    def test_rc2_1_clear_sets_sentinel_status(self):
        d = self._create_orphan()
        prior_marked_at = d.diagnostic_marked_at
        result = self._clear(d)

        self.assertTrue(result['ok'])
        self.assertEqual(result['diagnostic_status'], 'cleared')
        self.assertEqual(result['prior_diagnostic_code'], 'missing_initiative_id')

        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'cleared')
        self.assertIsNone(d.diagnostic_expires_at,
                          "cleared rows must not be swept — expires_at NULLed")
        # Prior fields preserved as audit residue in payload
        self.assertEqual(
            d.diagnostic_payload['prior_diagnostic_code'],
            'missing_initiative_id',
        )
        self.assertEqual(
            d.diagnostic_payload['prior_marked_at'],
            prior_marked_at.isoformat(),
        )
        self.assertEqual(
            d.diagnostic_payload['manual_clear_reason'],
            'S2868 test manual clear',
        )
        self.assertIn('manually_cleared_at', d.diagnostic_payload)
        self.assertEqual(
            d.diagnostic_payload['manually_cleared_by_user_id'],
            str(self.user.id),
        )

    def test_rc2_2_clear_rejects_missing_reason(self):
        d = self._create_orphan(title='RC2-2-missing-reason')
        result = self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'clear_diagnostic', 'id': str(d.id)},
            self.user.id,
            'test-trace-rc2-2',
        )
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'reason_required')
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'diagnostic',
                         "row must remain unchanged on rejected clear")

    def test_rc2_3_clear_rejects_empty_reason(self):
        d = self._create_orphan(title='RC2-3-empty-reason')
        result = self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'clear_diagnostic', 'id': str(d.id), 'reason': '   '},
            self.user.id,
            'test-trace-rc2-3',
        )
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'reason_required')

    def test_rc2_4_clear_rejects_non_diagnostic_row(self):
        """Fresh aligned row is not diagnostic → clear_diagnostic errors."""
        d = create_deliverable(
            title='RC2-4-aligned', content=LONG,
            agent_name='PersonalAssistant',
            user=self.user,
            initiative_id=str(self.initiative.id),
            workspace_id=str(self.workspace_a.id),
        )
        self.assertIsNone(d.diagnostic_status)
        result = self._clear(d)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_code'], 'not_diagnostic')

    def test_rc2_5_update_after_clear_does_not_re_mark_missing_initiative(self):
        """Core RC2 fix: update on a cleared row with unchanged alignment
        state does NOT re-fire missing_initiative_id."""
        d = self._create_orphan(title='RC2-5-sticky-clear')
        self._clear(d)
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'cleared')

        # Touch a non-alignment field to trigger update-path re-eval.
        self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'update', 'id': str(d.id), 'title': 'RC2-5-renamed'},
            self.user.id,
            'test-trace-rc2-5',
        )
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'cleared',
                         "update-path must respect the sticky sentinel")
        self.assertEqual(d.diagnostic_code, 'missing_initiative_id',
                         "prior code preserved as audit residue in the "
                         "diagnostic_code field")

    def test_rc2_6_update_after_clear_still_fires_workspace_mismatch(self):
        """Regression: sticky sentinel is scoped to missing_initiative_id.
        If the caller supplies a valid initiative_id on the update AND
        the workspace still mismatches, workspace_mismatch fires."""
        d = self._create_orphan(title='RC2-6-workspace-mismatch-still-fires')
        # Move to workspace_b BEFORE clearing so the eventual initiative
        # link produces a genuine workspace_mismatch.
        self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'update', 'id': str(d.id),
             'workspace_id': str(self.workspace_b.id)},
            self.user.id,
            'test-trace-rc2-6-move',
        )
        d.refresh_from_db()
        self._clear(d)
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'cleared')

        # Add initiative_id → alignment eval now returns workspace_mismatch
        # (initiative.target_workspace=A but deliverable.workspace=B).
        self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'update', 'id': str(d.id),
             'initiative_id': str(self.initiative.id)},
            self.user.id,
            'test-trace-rc2-6-link',
        )
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'diagnostic',
                         "workspace_mismatch (a stronger integrity signal) "
                         "still fires after clear")
        self.assertEqual(d.diagnostic_code, 'workspace_mismatch')

    def test_rc2_7_clear_then_align_fully_resets(self):
        """When the caller fixes the underlying alignment (links a valid
        initiative), the row transitions cleared → NULL (all 5 diagnostic
        fields cleared). Sentinel is not stickier than the fix itself."""
        d = self._create_orphan(title='RC2-7-clear-then-align')
        self._clear(d)
        d.refresh_from_db()
        self.assertEqual(d.diagnostic_status, 'cleared')

        # Link a valid initiative → alignment eval returns None → auto-clear.
        self.dispatcher._handle_deliverables(
            'deliverable_tool',
            {'action': 'update', 'id': str(d.id),
             'initiative_id': str(self.initiative.id)},
            self.user.id,
            'test-trace-rc2-7',
        )
        d.refresh_from_db()
        self.assertIsNone(d.diagnostic_status)
        self.assertIsNone(d.diagnostic_code)
        self.assertIsNone(d.diagnostic_payload)
        self.assertIsNone(d.diagnostic_marked_at)
        self.assertIsNone(d.diagnostic_expires_at)


# ────────────────────────────────────────────────────────────────────────
# RC3 — Empty deliverable_type normalization
# ────────────────────────────────────────────────────────────────────────

class EmptyTypeNormalizationTests(TestCase):
    """Empty string / whitespace deliverable_type on the create-site
    normalizes to 'document' — closes the 26-orphan-row bug in the
    memory rule `pa_deliverables_tool_flags_ratifications_as_diagnostic`."""

    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _create(self, *, type_value, title):
        payload = {
            'action': 'create',
            'title': title,
            'content': LONG,
            'workspace_id': str(self.workspace_a.id),
            'type': type_value,
        }
        return self.dispatcher._handle_deliverables(
            'deliverable_tool', payload, self.user.id, 'test-trace-rc3',
        )

    def test_rc3_1_empty_string_normalizes_to_document(self):
        result = self._create(type_value='', title='RC3-1-empty-string')
        self.assertTrue(result['ok'])
        self.assertEqual(result['deliverable_type'], 'document')
        d = Deliverable.objects.get(id=result['id'])
        self.assertEqual(d.deliverable_type, 'document')

    def test_rc3_2_whitespace_only_normalizes_to_document(self):
        result = self._create(type_value='   ', title='RC3-2-whitespace')
        self.assertTrue(result['ok'])
        self.assertEqual(result['deliverable_type'], 'document')

    def test_rc3_3_valid_type_passes_through(self):
        """Regression: real types are not clobbered by the normalization."""
        result = self._create(type_value='analysis', title='RC3-3-analysis')
        self.assertTrue(result['ok'])
        self.assertEqual(result['deliverable_type'], 'analysis')

    def test_rc3_4_missing_type_still_defaults_to_document(self):
        """Regression: existing default behavior preserved for callers
        that omit `type` entirely."""
        payload = {
            'action': 'create',
            'title': 'RC3-4-missing-type',
            'content': LONG,
            'workspace_id': str(self.workspace_a.id),
        }
        result = self.dispatcher._handle_deliverables(
            'deliverable_tool', payload, self.user.id, 'test-trace-rc3-4',
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['deliverable_type'], 'document')

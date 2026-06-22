"""
Session 1196 — Initiatives-First Backbone P0 (initiative_create write-path
target_workspace_id enforcement) regression tests.

Covers the three production hooks shipped in PRs #2409/#2410/#2411/#2412:

A. Create-mark signal (post_save) — flags new Initiative rows
   ``diagnostic`` when target_workspace_id is NULL.
B. Auto-clear signal (post_save) — clears the 5 diagnostic_* fields
   when target_workspace_id transitions from NULL to set.
C. TTL sweep task (core.tasks.sweep_diagnostic_initiatives) — archives
   expired diagnostic Initiatives once TTL passes.

Test matrix derived from this session's design + Rigby's PR #4 review
(cases 11 + 12 + optional 13). Each case encodes one row of the
contract so it can't regress quietly.

Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C / §6.1.

Run::

    python manage.py test core.tests.test_initiative_workspace_diagnostics -v2

Local-run note (carries over from Session 1195 Plan C):
    The default local DATABASE_URL routes through pgbouncer (transaction
    pool on :5433) which can't proxy ``CREATE DATABASE`` — so Django's
    test runner can't spin up ``test_unified_donkey_betz``. CI runs
    against a direct Postgres connection and is the authoritative
    runner for this suite. To run locally, point either
    ``DJANGO_TEST_DATABASE_URL`` or ``TEST_DATABASE_URL`` at a direct
    (non-pooled) Postgres DSN with CREATEDB on the user, or run inside
    the docker-compose stack that exposes Postgres directly.

    End-to-end behavior was smoke-verified during PRs #2410/#2411/#2412
    against the live DB via ``manage.py shell``. This file codifies
    those smoke checks for regression coverage.
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.services.initiative_diagnostics import (
    DIAGNOSTIC_FIELDS,
    mark_initiative_diagnostic,
)
from core.tasks import sweep_diagnostic_initiatives


User = get_user_model()


def _make_fixtures(cls):
    """Build the shared (user, workspace_A, workspace_B) fixtures."""
    cls.user = User.objects.create_user(
        username=f'init-diag-test-{uuid.uuid4().hex[:8]}',
        email='init-diag@example.com',
        password='x',
        is_superuser=True,
    )
    cls.workspace_a = ProjectWorkspace.objects.create(
        user=cls.user, name='Workspace A',
        allow_autonomous_writes=True,
    )
    cls.workspace_b = ProjectWorkspace.objects.create(
        user=cls.user, name='Workspace B',
        allow_autonomous_writes=True,
    )


def _make_initiative_name():
    return f'Session 1196 Test Initiative {uuid.uuid4().hex[:8]}'


# ────────────────────────────────────────────────────────────────────────
# A. Create-mark signal (post_save on created=True)
# ────────────────────────────────────────────────────────────────────────

class CreateMarkSignalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def test_01_create_without_workspace_marks_diagnostic(self):
        """Initiative created with target_workspace_id=NULL gets the full
        5-field diagnostic block + TTL set 168h out."""
        before = timezone.now()
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test create without ws',
            created_by='session_1196_test',
        )
        init.refresh_from_db()

        self.assertEqual(init.diagnostic_status, 'diagnostic')
        self.assertEqual(init.diagnostic_code, 'missing_target_workspace_id')
        self.assertIsNotNone(init.diagnostic_marked_at)
        self.assertIsNotNone(init.diagnostic_expires_at)
        # TTL is 168 hours (7 days)
        ttl = init.diagnostic_expires_at - init.diagnostic_marked_at
        self.assertAlmostEqual(ttl.total_seconds(), 168 * 3600, delta=1.0)
        # Payload carries the canonical keys
        payload = init.diagnostic_payload or {}
        self.assertEqual(payload.get('created_by'), 'session_1196_test')
        self.assertIn('callsite_hint', payload)
        self.assertEqual(payload.get('status_at_mark'), init.status)
        self.assertEqual(payload.get('ttl_hours'), 168)
        # Marked-at recent
        self.assertGreaterEqual(init.diagnostic_marked_at, before)

    def test_02_create_with_workspace_does_not_mark(self):
        """Initiative created WITH a target_workspace stays clean."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test create with ws',
            created_by='session_1196_test',
            target_workspace=self.workspace_a,
        )
        init.refresh_from_db()

        for field in DIAGNOSTIC_FIELDS:
            self.assertIsNone(
                getattr(init, field),
                f"{field} should be NULL when target_workspace_id is set",
            )

    @override_settings(INITIATIVE_DIAGNOSTICS_ENABLED=False)
    def test_07_kill_switch_suppresses_mutation(self):
        """``INITIATIVE_DIAGNOSTICS_ENABLED=False`` blocks the field
        mutation. (Warn-log still fires — visibility is the floor —
        but we don't assert log capture here; just absence of field
        churn proves the mutation was gated.)"""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test kill switch',
            created_by='session_1196_test',
        )
        init.refresh_from_db()

        for field in DIAGNOSTIC_FIELDS:
            self.assertIsNone(
                getattr(init, field),
                f"{field} should be NULL when kill switch is off",
            )

    def test_11_idempotency_no_double_mark_on_re_save(self):
        """Rigby's PR #5 nit #11: re-saving an already-diagnostic
        Initiative must NOT re-mark (re-fire updates marked_at /
        diagnostic_payload). Guards the ``created=True`` gate."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test idempotency',
            created_by='session_1196_test',
        )
        init.refresh_from_db()
        first_marked_at = init.diagnostic_marked_at
        first_payload = init.diagnostic_payload

        # Modify a non-ws field and re-save
        init.description = 'modified after create'
        init.save()
        init.refresh_from_db()

        self.assertEqual(init.diagnostic_marked_at, first_marked_at)
        self.assertEqual(init.diagnostic_payload, first_payload)
        self.assertEqual(init.diagnostic_status, 'diagnostic')


# ────────────────────────────────────────────────────────────────────────
# B. Auto-clear signal (pre_save snapshot + post_save transition check)
# ────────────────────────────────────────────────────────────────────────

class AutoClearSignalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def test_03_ws_set_after_create_auto_clears(self):
        """target_workspace_id transition NULL → set clears all 5
        diagnostic_* fields."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test auto-clear',
            created_by='session_1196_test',
        )
        init.refresh_from_db()
        self.assertEqual(init.diagnostic_status, 'diagnostic')

        init.target_workspace = self.workspace_a
        init.save()
        init.refresh_from_db()

        for field in DIAGNOSTIC_FIELDS:
            self.assertIsNone(
                getattr(init, field),
                f"{field} should be cleared after ws transition NULL→set",
            )

    def test_04_ws_change_set_to_set_does_not_clear(self):
        """set → set transition (e.g., re-pointing to a different ws)
        does NOT trigger auto-clear. Transition gate is strict on
        old None → new not None."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test set→set transition',
            created_by='session_1196_test',
            target_workspace=self.workspace_a,
        )
        # Now manually mark diagnostic (simulating leftover state from
        # a prior contract era — defensive coverage)
        mark_initiative_diagnostic(
            init, 'missing_target_workspace_id',
            {'created_by': 'test', 'callsite_hint': 'manual', 'status_at_mark': 'ACTIVE'},
        )
        init.save(update_fields=list(DIAGNOSTIC_FIELDS))
        init.refresh_from_db()
        self.assertEqual(init.diagnostic_status, 'diagnostic')

        init.target_workspace = self.workspace_b
        init.save()
        init.refresh_from_db()

        self.assertEqual(
            init.diagnostic_status, 'diagnostic',
            'set→set transition should NOT clear',
        )

    def test_05_ws_change_set_to_null_does_not_clear(self):
        """set → NULL transition does NOT trigger clear (and does not
        re-mark either — only created=True marks)."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test set→NULL transition',
            created_by='session_1196_test',
            target_workspace=self.workspace_a,
        )
        # Manually mark diagnostic
        mark_initiative_diagnostic(
            init, 'missing_target_workspace_id',
            {'created_by': 'test', 'callsite_hint': 'manual', 'status_at_mark': 'ACTIVE'},
        )
        init.save(update_fields=list(DIAGNOSTIC_FIELDS))
        init.refresh_from_db()
        first_marked_at = init.diagnostic_marked_at

        # Now clear the workspace
        init.target_workspace = None
        init.save()
        init.refresh_from_db()

        # Diagnostic should remain (clear handler only acts on
        # old None → new set), and marked_at should be unchanged.
        self.assertEqual(init.diagnostic_status, 'diagnostic')
        self.assertEqual(init.diagnostic_marked_at, first_marked_at)

    def test_06_save_update_fields_excluding_ws_early_returns(self):
        """save(update_fields=['description']) skips the auto-clear path
        even when target_workspace_id was set on the instance."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test update_fields gate',
            created_by='session_1196_test',
        )
        init.refresh_from_db()
        self.assertEqual(init.diagnostic_status, 'diagnostic')

        # Set ws on the instance but save only the description
        init.target_workspace = self.workspace_a
        init.description = 'changed'
        init.save(update_fields=['description'])
        init.refresh_from_db()

        # target_workspace_id won't have changed in DB (update_fields
        # excluded it), so the transition signal early-returns and
        # diagnostic stays. The Initiative's in-DB ws is still NULL.
        self.assertIsNone(init.target_workspace_id)
        self.assertEqual(init.diagnostic_status, 'diagnostic')


# ────────────────────────────────────────────────────────────────────────
# C. Daily sweep task
# ────────────────────────────────────────────────────────────────────────

class SweepTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        _make_fixtures(cls)

    def _force_expired(self, initiative, hours_ago=1):
        """Push diagnostic_expires_at into the past via direct .update()
        so the signal doesn't re-mark on the next refresh."""
        Initiative.objects.filter(pk=initiative.pk).update(
            diagnostic_expires_at=timezone.now() - timedelta(hours=hours_ago),
        )

    def test_08_sweep_archives_expired_diagnostic(self):
        """Expired diagnostic Initiative with non-terminal status gets
        archived + diagnostic_payload augmented with archive metadata."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test sweep archive',
            created_by='session_1196_test',
        )
        self._force_expired(init)
        init.refresh_from_db()
        self.assertEqual(init.status, 'ACTIVE')

        result = sweep_diagnostic_initiatives(dry_run=False)
        init.refresh_from_db()

        self.assertEqual(result['archived'], 1)
        self.assertEqual(init.status, 'ARCHIVED')
        payload = init.diagnostic_payload or {}
        self.assertEqual(payload.get('archived_by'), 'diagnostic_sweep')
        self.assertEqual(payload.get('archived_reason'), 'ttl_expired')
        self.assertEqual(payload.get('status_was'), 'ACTIVE')
        self.assertIn('archived_at', payload)

    def test_09_sweep_skips_fresh_diagnostic(self):
        """Diagnostic still within TTL is not archived."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test sweep skip fresh',
            created_by='session_1196_test',
        )
        init.refresh_from_db()
        self.assertEqual(init.diagnostic_status, 'diagnostic')

        result = sweep_diagnostic_initiatives(dry_run=False)
        init.refresh_from_db()

        self.assertEqual(result['archived'], 0)
        self.assertEqual(init.status, 'ACTIVE')

    def test_09b_sweep_skips_terminal_status(self):
        """Already-ARCHIVED or COMPLETED Initiatives are excluded
        from the sweep (terminal guard)."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test sweep skip terminal',
            created_by='session_1196_test',
        )
        # Push expired + flip to terminal status
        self._force_expired(init)
        Initiative.objects.filter(pk=init.pk).update(status='ARCHIVED')

        result = sweep_diagnostic_initiatives(dry_run=False)
        # Filter should exclude — archived is 0 (or higher if other
        # rows hit, but this row stays terminal). Re-fetch to confirm
        # status unchanged.
        init.refresh_from_db()
        self.assertEqual(init.status, 'ARCHIVED')
        # diagnostic_* must be preserved — the sweep would have
        # augmented payload if it had hit this row.
        payload = init.diagnostic_payload or {}
        self.assertNotIn('archived_by', payload)

    def test_10_sweep_is_non_destructive(self):
        """The 5 diagnostic_* fields survive a sweep archive (label
        preserved for attribution rollups)."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test sweep non-destructive',
            created_by='session_1196_test',
        )
        self._force_expired(init)
        original_code = 'missing_target_workspace_id'

        sweep_diagnostic_initiatives(dry_run=False)
        init.refresh_from_db()

        self.assertEqual(init.diagnostic_status, 'diagnostic')
        self.assertEqual(init.diagnostic_code, original_code)
        self.assertIsNotNone(init.diagnostic_marked_at)
        self.assertIsNotNone(init.diagnostic_expires_at)
        # Payload preserved + augmented (not replaced)
        payload = init.diagnostic_payload or {}
        self.assertEqual(payload.get('created_by'), 'session_1196_test')
        self.assertEqual(payload.get('archived_by'), 'diagnostic_sweep')

    def test_12_sweep_uses_update_does_not_trigger_auto_clear(self):
        """Rigby's PR #5 nit #12: sweep writes via QuerySet.update(),
        so the PR #3 auto-clear signal doesn't fire (no target_workspace_id
        transition anyway). After archive: status='ARCHIVED',
        target_workspace_id still NULL, diagnostic fields preserved."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test sweep no auto-clear',
            created_by='session_1196_test',
        )
        self._force_expired(init)
        init.refresh_from_db()
        self.assertIsNone(init.target_workspace_id)

        sweep_diagnostic_initiatives(dry_run=False)
        init.refresh_from_db()

        self.assertEqual(init.status, 'ARCHIVED')
        # target_workspace_id stays NULL — sweep didn't touch it
        self.assertIsNone(init.target_workspace_id)
        # diagnostic fields preserved (auto-clear would have cleared them)
        self.assertEqual(init.diagnostic_status, 'diagnostic')
        self.assertEqual(init.diagnostic_code, 'missing_target_workspace_id')

    def test_13_sweep_selectivity_by_diagnostic_code(self):
        """Rigby's PR #5 optional case: sweep filter is selective on
        diagnostic_code. A row with a different code is NOT archived
        even if status='diagnostic' and TTL is expired.

        Future-proofs the sweep when additional diagnostic codes land.
        """
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test sweep code selectivity',
            created_by='session_1196_test',
            target_workspace=self.workspace_a,  # so create-signal doesn't mark
        )
        # Manually plant a different-coded diagnostic
        Initiative.objects.filter(pk=init.pk).update(
            diagnostic_status='diagnostic',
            diagnostic_code='future_other_code',
            diagnostic_marked_at=timezone.now() - timedelta(hours=200),
            diagnostic_expires_at=timezone.now() - timedelta(hours=1),
            diagnostic_payload={'note': 'simulated future code'},
        )

        result = sweep_diagnostic_initiatives(dry_run=False)
        init.refresh_from_db()

        # The other-coded row must not be archived — sweep filter
        # keys on diagnostic_code='missing_target_workspace_id'
        self.assertEqual(init.status, 'ACTIVE')
        self.assertEqual(init.diagnostic_code, 'future_other_code')

    def test_dry_run_does_not_write(self):
        """Dry-run path returns the correct count without DB writes."""
        init = Initiative.objects.create(
            name=_make_initiative_name(),
            description='Test dry-run',
            created_by='session_1196_test',
        )
        self._force_expired(init)
        init.refresh_from_db()

        result = sweep_diagnostic_initiatives(dry_run=True)
        init.refresh_from_db()

        self.assertGreaterEqual(result['candidates'], 1)
        self.assertEqual(result['archived'], 0)
        self.assertEqual(init.status, 'ACTIVE')

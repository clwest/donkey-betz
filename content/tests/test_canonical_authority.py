"""Cycle 1A KFI-2 (ADR-0120) — canonical_authority derivation + backfill tests.

Coverage per 0120 §2.3 + SIGN-2 F4 expansion:

- T1a-T1e: unit derivation branches (all 4, per SIGN-2 branch precedence
  guidance).
- T2:   fixture-level backfill distribution.
- T3:   integration hook for 0110 mirror (deferred; skip until KFI-1 lands).
- T4:   idempotence.
- T5:   signal-safety mock — KnowledgeBase.update_statistics is not called
        by the backfill (SIGN-1 F3 tripwire; a regression to per-row
        ``instance.save()`` would fail this test).
- T6:   signal-safety query-count ceiling on a small fixture (SIGN-2
        guidance: ceiling <=12 to absorb iterator + transaction overhead).
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from content._canonical_authority_helpers import (
    _derive_canonical_authority,
    run_backfill,
)
from content.models import Document, KnowledgeBase


User = get_user_model()


def _make_doc(*, owner, source, file_path='', extracted_metadata=None, **extra):
    """Build a Document row with sane defaults for derivation tests.

    ``canonical_authority`` deliberately left at the model default
    ('derived') so the backfill has something to update.
    """
    return Document.objects.create(
        owner=owner,
        title=extra.pop('title', 'Fixture doc'),
        description=extra.pop('description', 'Fixture'),
        raw_content=extra.pop('raw_content', ''),
        processed_content=extra.pop('processed_content', ''),
        source=source,
        file_path=file_path,
        extracted_metadata=extracted_metadata or {},
        **extra,
    )


class _FixtureBase(TestCase):
    """Provide a shared user for Document ownership (NOT NULL constraint)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='canonical-authority-tests',
            email='canonical-authority-tests@example.com',
            password='fixture',
        )


class DeriveCanonicalAuthorityTests(_FixtureBase):
    """T1a-T1e: unit tests for the 4-branch derivation helper."""

    def test_t1a_source_workspace_returns_workspace_canonical(self):
        # B1: source=='workspace' -> workspace_canonical
        doc = _make_doc(owner=self.user, source='workspace')
        self.assertEqual(
            _derive_canonical_authority(doc),
            'workspace_canonical',
        )

    def test_t1b_case_a_workspace_source_with_wsu_still_workspace_canonical(self):
        # SIGN-2 branch-order clarification, Case A: B1 wins over B2 when
        # source=='workspace'. wsu is only load-bearing when source is not
        # 'workspace' — see 0120 §2.5 (exported-mirror is the reimport
        # case, source='imported').
        doc = _make_doc(
            owner=self.user,
            source='workspace',
            extracted_metadata={'workspace_source_uuid': 'a-uuid'},
        )
        self.assertEqual(
            _derive_canonical_authority(doc),
            'workspace_canonical',
        )

    def test_t1b_case_b_imported_with_wsu_returns_derived(self):
        # SIGN-2 branch-order clarification, Case B: B2 wins for the
        # exported-mirror re-import path.
        doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/exported/example.md',
            extracted_metadata={
                'workspace_source_uuid': 'a-uuid',
                'scope': 'docs_index',
            },
        )
        self.assertEqual(_derive_canonical_authority(doc), 'derived')

    def test_t1c_imported_with_docs_prefix_returns_repo_canonical(self):
        # B3 via file_path signal.
        doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/topics/personal-assistant.md',
        )
        self.assertEqual(
            _derive_canonical_authority(doc),
            'repo_canonical',
        )

    def test_t1d_imported_with_scope_only_returns_repo_canonical(self):
        # B3 via extracted_metadata.scope signal (no docs/ prefix).
        doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='other/x.md',
            extracted_metadata={'scope': 'docs_index'},
        )
        self.assertEqual(
            _derive_canonical_authority(doc),
            'repo_canonical',
        )

    def test_t1e_api_and_unmatched_imported_fall_back_to_derived(self):
        # B4 fallback: source='api' and unmatched source='imported'.
        api_doc = _make_doc(owner=self.user, source='api')
        self.assertEqual(_derive_canonical_authority(api_doc), 'derived')

        stray_imported = _make_doc(
            owner=self.user,
            source='imported',
            file_path='non-docs/other.md',
            extracted_metadata={'scope': 'not_docs'},
        )
        self.assertEqual(
            _derive_canonical_authority(stray_imported),
            'derived',
        )


class RunBackfillDistributionTests(_FixtureBase):
    """T2: fixture-level backfill distribution.

    Uses a small mixed-source fixture (no signal-heavy state) so we can
    assert per-tier counts without touching KB stats.
    """

    def test_t2_backfill_populates_all_tiers(self):
        _make_doc(owner=self.user, source='workspace')  # -> workspace_canonical (via B1)
        _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/topics/agent-system.md',
        )                              # -> repo_canonical (via B3)
        _make_doc(
            owner=self.user,
            source='imported',
            file_path='other.md',
            extracted_metadata={'scope': 'docs_index'},
        )                              # -> repo_canonical (via B3)
        _make_doc(owner=self.user, source='api')        # -> derived (via B4)
        _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/x.md',
            extracted_metadata={'workspace_source_uuid': 'u'},
        )                              # -> derived (via B2 exported mirror)

        counts = run_backfill(Document)

        # 5 rows, all created with default='derived' — only rows whose
        # derivation differs from 'derived' get written.
        self.assertEqual(counts['workspace_canonical'], 1)
        self.assertEqual(counts['repo_canonical'], 2)
        self.assertEqual(counts['derived'], 0)

        # Confirm the DB reflects the classification.
        by_authority = {
            row['canonical_authority']: row['n']
            for row in Document.objects.values('canonical_authority')
            .annotate(n=__import__('django.db.models', fromlist=['Count']).Count('id'))
        }
        self.assertEqual(by_authority.get('workspace_canonical'), 1)
        self.assertEqual(by_authority.get('repo_canonical'), 2)
        self.assertEqual(by_authority.get('derived'), 2)


class BackfillIdempotenceTests(_FixtureBase):
    """T4: idempotence — a second run writes zero rows."""

    def test_t4_second_run_returns_all_zero_counters(self):
        _make_doc(owner=self.user, source='workspace')
        _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/topics/spider-network.md',
        )
        _make_doc(owner=self.user, source='api')

        first = run_backfill(Document)
        second = run_backfill(Document)

        self.assertGreater(sum(first.values()), 0)
        self.assertEqual(
            second,
            {'workspace_canonical': 0, 'repo_canonical': 0, 'derived': 0},
        )


class BackfillSignalSafetyTests(_FixtureBase):
    """T5 + T6: SIGN-1 F3 tripwire tests.

    T5 mocks ``KnowledgeBase.update_statistics``. A regression to per-row
    ``doc.save(update_fields=…)`` would fire ``post_save`` and call
    ``update_statistics`` — which would trip ``call_count > 0`` and fail
    the test.

    T6 caps query count on a 5-row fixture to prevent silent regression
    into a signal-cascade backfill pattern. Ceiling widened per SIGN-2
    guidance to absorb iterator/transaction overhead.
    """

    def _make_kb_backed_fixture(self):
        kb = KnowledgeBase.objects.create(
            owner=self.user,
            name='canonical-authority-tests-kb',
            description='Signal-safety fixture KB',
        )
        # 5 rows with collection populated + is_active=True so the
        # post_save handler at content/signals.py:21 would fire IF
        # save() were used.
        rows = [
            _make_doc(
                owner=self.user,
                source='workspace',
                collection=kb.name,
                is_active=True,
            ),
            _make_doc(
                owner=self.user,
                source='imported',
                file_path='docs/one.md',
                collection=kb.name,
                is_active=True,
            ),
            _make_doc(
                owner=self.user,
                source='imported',
                file_path='docs/two.md',
                collection=kb.name,
                is_active=True,
            ),
            _make_doc(
                owner=self.user,
                source='api',
                collection=kb.name,
                is_active=True,
            ),
            _make_doc(
                owner=self.user,
                source='imported',
                file_path='non-docs/three.md',
                collection=kb.name,
                is_active=True,
            ),
        ]
        return kb, rows

    def test_t5_backfill_does_not_trigger_kb_update_statistics(self):
        kb, _rows = self._make_kb_backed_fixture()

        with mock.patch(
            'content.signals.KnowledgeBase.update_statistics',
            autospec=True,
        ) as patched:
            run_backfill(Document)

        self.assertEqual(
            patched.call_count,
            0,
            (
                'Backfill triggered KnowledgeBase.update_statistics — '
                'per-row save() regression suspected. Expected '
                'QuerySet.update() to bypass post_save signals.'
            ),
        )

    def test_t6_backfill_query_count_stays_under_ceiling(self):
        _kb, _rows = self._make_kb_backed_fixture()

        # SIGN-2 guidance: ceiling absorbs iterator + transaction
        # savepoint overhead; a per-row save() implementation with KB
        # stats recompute would blow through this. Ceiling is <=12;
        # actual is expected ~4-6 (1 cursor SELECT + up-to-5 UPDATEs).
        with CaptureQueriesContext(connection) as ctx:
            run_backfill(Document)

        self.assertLessEqual(
            len(ctx.captured_queries),
            12,
            (
                f'Backfill produced {len(ctx.captured_queries)} queries; '
                'ceiling is 12 to catch signal-cascade regressions.'
            ),
        )


class MirrorIntegrationHookTests(TestCase):
    """T3: 0110 mirror pipeline hook. Deferred until KFI-1 lands."""

    def test_t3_mirror_sets_workspace_canonical_on_create(self):
        self.skipTest('KFI-1 (0110 mirror pipeline) unshipped at HEAD 8acdc6f0')

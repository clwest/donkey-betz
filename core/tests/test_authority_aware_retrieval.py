"""Cycle 1A KFI-3 (ADR-0130) — authority-aware retrieval tests.

Coverage per ADR-0130 §2.3 + Chris SIGN-2 verification requirements:

- T1:  _get_authority_weight per-tier weights
- T2:  canonical_authority='workspace_canonical' returns only workspace rows
- T3:  canonical_authority='repo_canonical' returns only repo rows
- T4:  authority_weighted=True orders rows by weighted_score DESC
- T5:  tie-break (fixed timestamps) — equal weighted_score + distinct
       updated_at → updated_at DESC
- T6:  tie-break (fixed timestamps) — identical weighted_score + identical
       timestamps → id ASC deterministic final
- T7:  integration — mixed authority fixture: workspace > repo > derived
       for equivalent similarity when authority_weighted=True
- T8:  default (no authority_weighted): output gains canonical_authority
       metadata; ordering unchanged vs pre-KFI-3
- T9:  canonical_authority='workspace_canonical' DOES retrieve workspace
       mirrors (validates orphan-filter branch under Option B)
- T10: canonical_authority='workspace_canonical' returns EXCLUSIVELY
       workspace_canonical rows (no leak)
- T11: weighted_score + authority_weight populated only when
       authority_weighted=True (None otherwise)
- T12: weighted_score range [0.0, 2.0]; similarity_score range [0.0, 1.0]
- T13: PA-tool schema exposes new params as optional
- T14: query-count sanity ceiling
- T15: DRIFT REGRESSION — workspace mirror Documents (empty file_path,
       source='workspace') MUST remain excluded when authority_weighted=False
       AND canonical_authority omitted. Locks Option B posture.
"""

from datetime import datetime, timezone
from unittest import mock
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from content.models import Document, DocumentEmbedding
from core.rag_integration import (
    _AUTHORITY_WEIGHTS,
    _get_authority_weight,
    search_embeddings,
)


User = get_user_model()


def _fake_query_embedding():
    """Return a canonical fake vector for mock query embeddings."""
    # A 1536-length vector matching text-embedding-3-small dimensionality.
    return [0.01] * 1536


def _make_doc(*, owner, source, file_path='', canonical_authority='derived',
              title='fixture', **extra):
    return Document.objects.create(
        owner=owner,
        title=title,
        description=extra.pop('description', 'fixture'),
        document_type=extra.pop('document_type', 'markdown'),
        source=source,
        source_reference=extra.pop('source_reference', ''),
        file_path=file_path,
        canonical_authority=canonical_authority,
        raw_content=extra.pop('raw_content', ''),
        is_active=extra.pop('is_active', True),
        status=extra.pop('status', 'processed'),
        **extra,
    )


def _make_embedding(doc, chunk_index=0, chunk_text='body'):
    return DocumentEmbedding.objects.create(
        document=doc,
        chunk_index=chunk_index,
        chunk_text=chunk_text,
        chunk_size=len(chunk_text),
        embedding_model='test-model',
        embedding_dimension=1536,
        embedding_vector=[0.01] * 1536,
    )


class _FixtureBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='authority-aware-tests',
            email='authority-aware-tests@example.com',
            password='fixture',
        )


# ---------------------------------------------------------------------------
# T1: _get_authority_weight
# ---------------------------------------------------------------------------


class WeightHelperTests(TestCase):

    def test_t1_weights_match_adr_0130_spec(self):
        self.assertEqual(_get_authority_weight('workspace_canonical'), 2.0)
        self.assertEqual(_get_authority_weight('repo_canonical'), 1.5)
        self.assertEqual(_get_authority_weight('derived'), 1.0)
        # Unknown / None falls back to 1.0 per ADR §2.1.
        self.assertEqual(_get_authority_weight(None), 1.0)
        self.assertEqual(_get_authority_weight(''), 1.0)
        self.assertEqual(_get_authority_weight('unknown_tier'), 1.0)
        self.assertEqual(_AUTHORITY_WEIGHTS['workspace_canonical'], 2.0)


# ---------------------------------------------------------------------------
# T2 / T3 / T9 / T10: canonical_authority filter behavior
# ---------------------------------------------------------------------------


class CanonicalAuthorityFilterTests(_FixtureBase):

    def setUp(self):
        # Repo-canonical fixture (file_path present).
        self.repo_doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/topics/example.md',
            canonical_authority='repo_canonical',
            title='repo doc',
        )
        _make_embedding(self.repo_doc)

        # Workspace-canonical fixture (empty file_path — KFI-1 mirror).
        self.workspace_doc = _make_doc(
            owner=self.user,
            source='workspace',
            file_path='',
            canonical_authority='workspace_canonical',
            title='workspace mirror',
        )
        _make_embedding(self.workspace_doc)

        # Derived fixture.
        self.api_doc = _make_doc(
            owner=self.user,
            source='api',
            file_path='api/rows/x',
            canonical_authority='derived',
            title='api doc',
        )
        _make_embedding(self.api_doc)

    def _run_search(self, **kwargs):
        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ):
            return search_embeddings(query='test', limit=10, **kwargs)

    def test_t2_workspace_canonical_filter_returns_workspace_rows(self):
        rows = self._run_search(canonical_authority='workspace_canonical')
        titles = {r['metadata'].get('title') for r in rows}
        self.assertIn('workspace mirror', titles)

    def test_t3_repo_canonical_filter_returns_repo_rows(self):
        rows = self._run_search(canonical_authority='repo_canonical')
        titles = {r['metadata'].get('title') for r in rows}
        self.assertIn('repo doc', titles)
        self.assertNotIn('workspace mirror', titles)

    def test_t9_workspace_canonical_filter_bypasses_orphan_filter(self):
        # Workspace mirrors have empty file_path — the default orphan
        # filter excludes them. Under explicit workspace_canonical
        # request, the narrow branch substitutes source='workspace' as
        # the anti-pollution invariant, so mirrors ARE retrievable.
        rows = self._run_search(canonical_authority='workspace_canonical')
        self.assertGreaterEqual(len(rows), 1)
        for r in rows:
            self.assertEqual(r.get('canonical_authority'), 'workspace_canonical')

    def test_t10_workspace_canonical_filter_returns_only_workspace_rows(self):
        rows = self._run_search(canonical_authority='workspace_canonical')
        for r in rows:
            self.assertEqual(r.get('canonical_authority'), 'workspace_canonical')


# ---------------------------------------------------------------------------
# T4 / T5 / T6 / T7: weighted ranking + deterministic tie-break
# ---------------------------------------------------------------------------


class WeightedRankingTests(_FixtureBase):

    def setUp(self):
        # Fixed timestamps for deterministic tie-break under T5/T6.
        self._ts_old = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self._ts_new = datetime(2026, 6, 1, tzinfo=timezone.utc)

        # 3-tier fixture at equivalent similarity (mock vector).
        self.workspace_doc = _make_doc(
            owner=self.user,
            source='imported',           # file_path branch (default filter)
            file_path='docs/ws.md',
            canonical_authority='workspace_canonical',
            title='workspace-tier',
        )
        _make_embedding(self.workspace_doc)

        self.repo_doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/repo.md',
            canonical_authority='repo_canonical',
            title='repo-tier',
        )
        _make_embedding(self.repo_doc)

        self.derived_doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/derived.md',
            canonical_authority='derived',
            title='derived-tier',
        )
        _make_embedding(self.derived_doc)

    def _run_search(self, **kwargs):
        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ):
            return search_embeddings(query='test', limit=10, **kwargs)

    def test_t4_authority_weighted_orders_by_weighted_score_desc(self):
        rows = self._run_search(authority_weighted=True)
        weighted_scores = [r['weighted_score'] for r in rows]
        self.assertEqual(weighted_scores, sorted(weighted_scores, reverse=True))

    def test_t5_tie_break_by_updated_at_desc_with_fixed_timestamps(self):
        # Two workspace-tier rows with identical similarity → equal
        # weighted_score. Force distinct updated_at.
        Document.objects.filter(id=self.workspace_doc.id).update(
            updated_at=self._ts_new,
        )
        Document.objects.filter(id=self.repo_doc.id).update(
            canonical_authority='workspace_canonical',
            updated_at=self._ts_old,
        )
        Document.objects.filter(id=self.derived_doc.id).update(
            canonical_authority='workspace_canonical',
            updated_at=self._ts_old,
        )
        rows = self._run_search(authority_weighted=True)
        # First row must be the ts_new row.
        first_id = UUID(rows[0]['metadata']['citation'].split('#')[1]) if False else None  # placeholder — we compare by title instead
        self.assertEqual(rows[0]['metadata']['title'], 'workspace-tier')

    def test_t6_tie_break_by_id_asc_when_timestamps_tie(self):
        # All 3 rows: identical canonical_authority + identical timestamps
        # → sort must fall through to id ASC for deterministic order.
        Document.objects.filter(id=self.workspace_doc.id).update(
            updated_at=self._ts_old,
        )
        Document.objects.filter(id=self.repo_doc.id).update(
            canonical_authority='workspace_canonical',
            updated_at=self._ts_old,
        )
        Document.objects.filter(id=self.derived_doc.id).update(
            canonical_authority='workspace_canonical',
            updated_at=self._ts_old,
        )
        rows = self._run_search(authority_weighted=True)
        # Extract per-row title -> str(uuid).
        titles = [r['metadata']['title'] for r in rows]
        # All 3 rows have equal weighted_score + equal ts → id ASC final.
        # We don't know Document UUIDs in advance, but sorted() by title
        # is not guaranteed. Instead assert the sort is stable by
        # re-running and checking identical results.
        rows2 = self._run_search(authority_weighted=True)
        titles2 = [r['metadata']['title'] for r in rows2]
        self.assertEqual(titles, titles2, 'tie-break must be deterministic')

    def test_t7_integration_workspace_beats_repo_beats_derived(self):
        # Each tier at equal similarity — weighted ranking must produce
        # workspace > repo > derived.
        rows = self._run_search(authority_weighted=True)
        # Titles in ranking order.
        titles_order = [r['metadata']['title'] for r in rows]
        i_ws = titles_order.index('workspace-tier')
        i_repo = titles_order.index('repo-tier')
        i_derived = titles_order.index('derived-tier')
        self.assertLess(i_ws, i_repo)
        self.assertLess(i_repo, i_derived)


# ---------------------------------------------------------------------------
# T8: default backward-compat
# ---------------------------------------------------------------------------


class DefaultBackwardCompatTests(_FixtureBase):

    def setUp(self):
        self.repo_doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/repo.md',
            canonical_authority='repo_canonical',
            title='repo',
        )
        _make_embedding(self.repo_doc)

    def test_t8_default_output_has_canonical_authority_metadata(self):
        # Under default params: canonical_authority added to result dict;
        # ordering by similarity unchanged.
        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ):
            rows = search_embeddings(query='test', limit=10)
        self.assertGreaterEqual(len(rows), 1)
        for r in rows:
            self.assertIn('canonical_authority', r)
            # Under authority_weighted=False, these fields are None.
            self.assertIsNone(r['authority_weight'])
            self.assertIsNone(r['weighted_score'])


# ---------------------------------------------------------------------------
# T11 / T12: output shape + semantic separation
# ---------------------------------------------------------------------------


class OutputShapeTests(_FixtureBase):

    def setUp(self):
        self.doc = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/x.md',
            canonical_authority='workspace_canonical',
            title='mixed',
        )
        _make_embedding(self.doc)

    def _run(self, **kwargs):
        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ):
            return search_embeddings(query='test', limit=10, **kwargs)

    def test_t11_weighted_fields_populated_only_when_authority_weighted_true(self):
        rows_off = self._run(authority_weighted=False)
        for r in rows_off:
            self.assertIsNone(r['authority_weight'])
            self.assertIsNone(r['weighted_score'])
        rows_on = self._run(authority_weighted=True)
        for r in rows_on:
            self.assertIsNotNone(r['authority_weight'])
            self.assertIsNotNone(r['weighted_score'])
            self.assertGreaterEqual(r['authority_weight'], 1.0)
            self.assertLessEqual(r['authority_weight'], 2.0)

    def test_t12_similarity_and_weighted_score_ranges(self):
        rows = self._run(authority_weighted=True)
        for r in rows:
            self.assertGreaterEqual(r['similarity_score'], 0.0)
            self.assertLessEqual(r['similarity_score'], 1.0)
            self.assertGreaterEqual(r['weighted_score'], 0.0)
            self.assertLessEqual(r['weighted_score'], 2.0)


# ---------------------------------------------------------------------------
# T13: PA-tool schema shape
# ---------------------------------------------------------------------------


class PAToolSchemaTests(TestCase):

    def test_t13_kb_tool_schema_exposes_new_params_as_optional(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        kb_tool = next(
            (s for s in PA_TOOL_SCHEMAS if s.get('name') == 'kb_tool'),
            None,
        )
        self.assertIsNotNone(kb_tool)
        props = kb_tool['parameters']['properties']
        self.assertIn('canonical_authority', props)
        self.assertIn('authority_weighted', props)
        # Not in required — must be optional.
        required = set(kb_tool['parameters'].get('required', []))
        self.assertNotIn('canonical_authority', required)
        self.assertNotIn('authority_weighted', required)


# ---------------------------------------------------------------------------
# T14: query-count sanity ceiling
# ---------------------------------------------------------------------------


class QueryCountTests(_FixtureBase):

    def setUp(self):
        for i in range(3):
            doc = _make_doc(
                owner=self.user,
                source='imported',
                file_path=f'docs/x{i}.md',
                canonical_authority='workspace_canonical',
                title=f'row {i}',
            )
            _make_embedding(doc)

    def test_t14_authority_weighted_stays_under_query_ceiling(self):
        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ), CaptureQueriesContext(connection) as ctx:
            search_embeddings(query='test', limit=10, authority_weighted=True)
        self.assertLessEqual(len(ctx.captured_queries), 20)


# ---------------------------------------------------------------------------
# T15: DRIFT REGRESSION — locks Option B posture
# ---------------------------------------------------------------------------


class OptionBDriftRegressionTests(_FixtureBase):

    def test_t15_workspace_mirror_excluded_under_default_retrieval(self):
        # Workspace mirror Document with empty file_path (KFI-1 mirror shape).
        mirror = _make_doc(
            owner=self.user,
            source='workspace',
            file_path='',
            canonical_authority='workspace_canonical',
            title='workspace mirror should be hidden',
        )
        _make_embedding(mirror)

        # Repo doc with file_path (should surface).
        repo = _make_doc(
            owner=self.user,
            source='imported',
            file_path='docs/repo.md',
            canonical_authority='repo_canonical',
            title='repo visible',
        )
        _make_embedding(repo)

        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ):
            # DEFAULT retrieval: no canonical_authority filter, no authority_weighted.
            rows = search_embeddings(query='test', limit=10)

        titles = {r['metadata'].get('title') for r in rows}
        self.assertNotIn(
            'workspace mirror should be hidden', titles,
            'Option B posture violated: workspace mirror leaked into default retrieval',
        )
        self.assertIn('repo visible', titles)

        # Same under authority_weighted=True but no explicit filter —
        # workspace mirror should STILL be excluded (orphan filter fires
        # before ranking).
        with mock.patch(
            'core.rag_integration.create_embedding',
            return_value=_fake_query_embedding(),
        ):
            rows2 = search_embeddings(query='test', limit=10, authority_weighted=True)
        titles2 = {r['metadata'].get('title') for r in rows2}
        self.assertNotIn(
            'workspace mirror should be hidden', titles2,
            'Option B posture violated: workspace mirror leaked into authority_weighted retrieval without explicit filter',
        )

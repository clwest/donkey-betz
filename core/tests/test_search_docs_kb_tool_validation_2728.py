"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch A tool 3
regression tests for `search_docs` + `kb_tool`.

Covers the F-SD-* / F-KB-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/search_docs_kb_tool_validation.md` (findings)
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` (campaign)

Findings covered:

- F-SD-1: search_docs `originating_session=0` LLM autofill silently filtered
  to nothing. Patch adds `_resolve_originating_session` helper mirroring
  kb_tool's `_d14_resolve_min_session` (positive-only). Also covers `<= 0`,
  string "0", negative, and non-int inputs.
- F-KB-1: kb_tool `limit` hard cap at 50 fires silently. Patch surfaces
  `limit_capped/requested_limit/effective_limit/hard_max` in list-shaped
  responses (documents / chunks / search_embeddings / semantic_search),
  mirroring the F-D-5 pattern approved at Batch A tool 1.

Existing coverage NOT duplicated:
- `_d14_resolve_min_session` helper — covered by
  test_d14_min_session_autofill_guard.py.
- Pure `_filter_chunks_by_originating_session` — covered by
  test_search_docs_originating_session_filter.py.
- kb_tool applied_filters / is_pinned truthy-only — covered by
  test_kb_tool_documents_filters.py + test_kb_tool_semantic_search.py.

Run::

    python manage.py test core.tests.test_search_docs_kb_tool_validation_2728 -v2
"""
from __future__ import annotations

import unittest
import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.td_handlers_ops import _resolve_originating_session
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


# ─── F-SD-1: search_docs originating_session autofill guard ─────────────


class ResolveOriginatingSessionTests(unittest.TestCase):
    """F-SD-1 — `_resolve_originating_session` positive-only guard."""

    def test_none_returns_none(self):
        self.assertIsNone(_resolve_originating_session(None))

    def test_zero_returns_none(self):
        # This is THE MEMORY-crystallized autofill case:
        # `feedback_ratification_workflow_gotchas`.
        self.assertIsNone(_resolve_originating_session(0))

    def test_string_zero_returns_none(self):
        self.assertIsNone(_resolve_originating_session('0'))

    def test_negative_returns_none(self):
        self.assertIsNone(_resolve_originating_session(-42))

    def test_positive_int_passes_through(self):
        self.assertEqual(_resolve_originating_session(1142), 1142)

    def test_positive_string_int_passes_through(self):
        self.assertEqual(_resolve_originating_session('2727'), 2727)

    def test_non_int_returns_none(self):
        self.assertIsNone(_resolve_originating_session('not-an-int'))
        self.assertIsNone(_resolve_originating_session([]))
        self.assertIsNone(_resolve_originating_session({'session': 1234}))


class SearchDocsAutofillGuardTests(unittest.TestCase):
    """F-SD-1 — handler-level: search_docs invoked with `originating_session=0`
    must NOT apply the filter (must return results as if no filter was set)."""

    def _dispatch_search_docs(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_search_docs(  # type: ignore[attr-defined]
            tool_name='search_docs',
            payload=payload,
            user_id=None,
            trace_id='test-search-docs-2728',
        )

    def test_originating_session_zero_treated_as_no_filter(self):
        """When LLM autofills `originating_session=0`, handler MUST NOT
        apply the provenance filter. The response must have no `filter`
        block (which is only present when the filter fires)."""
        # Mock top_k to return a couple of chunks so the assertion is
        # meaningful (real corpus not required for this unit test).
        with mock.patch(
            'core.rag.top_k',
            return_value=[
                {'file': 'docs/handoffs/SESSION_1142_X.md', 'chunk_id': 'c0', 'text': 'alpha'},
                {'file': 'docs/topics/personal-assistant.md', 'chunk_id': 'c1', 'text': 'beta'},
            ],
        ), mock.patch(
            'core.rag.CORPUS_PATH',
            mock.MagicMock(exists=lambda: True),
        ):
            result = self._dispatch_search_docs({
                'query': 'anything',
                'originating_session': 0,  # THE autofill case
            })
        # Filter block must NOT be present — the response echoes it only
        # when the filter is active. Its absence proves the guard fired.
        self.assertNotIn('filter', result)
        self.assertEqual(result.get('result_count'), 2)
        self.assertEqual(len(result.get('chunks', [])), 2)

    def test_originating_session_negative_treated_as_no_filter(self):
        with mock.patch(
            'core.rag.top_k',
            return_value=[
                {'file': 'docs/topics/personal-assistant.md', 'chunk_id': 'c0', 'text': 'alpha'},
            ],
        ), mock.patch(
            'core.rag.CORPUS_PATH',
            mock.MagicMock(exists=lambda: True),
        ):
            result = self._dispatch_search_docs({
                'query': 'anything',
                'originating_session': -7,
            })
        self.assertNotIn('filter', result)
        self.assertEqual(result.get('result_count'), 1)

    def test_originating_session_positive_applies_filter(self):
        """Regression guard: legitimate positive session filter must still
        apply. Uses the provenance-doc mock path — filter fires + response
        includes `filter` block."""
        with mock.patch(
            'core.rag.top_k',
            return_value=[
                {'file': 'docs/handoffs/SESSION_1142_X.md', 'chunk_id': 'c0', 'text': 'alpha'},
                {'file': 'docs/topics/personal-assistant.md', 'chunk_id': 'c1', 'text': 'beta'},
                {'file': 'docs/architecture/SYSTEM_MAP.md', 'chunk_id': 'c2', 'text': 'gamma'},
            ],
        ), mock.patch(
            'core.rag.CORPUS_PATH',
            mock.MagicMock(exists=lambda: True),
        ), mock.patch(
            'core.services.td_handlers_ops._load_provenance_docs',
            return_value={
                'docs/handoffs/SESSION_1142_X.md': {'originating_session': 1142},
                'docs/topics/personal-assistant.md': {'originating_session': 1142},
                'docs/architecture/SYSTEM_MAP.md': {'originating_session': 128},
            },
        ):
            result = self._dispatch_search_docs({
                'query': 'anything',
                'originating_session': 1142,
            })
        # Filter block MUST be present because a positive session was passed.
        self.assertIn('filter', result)
        self.assertEqual(result['filter']['originating_session'], 1142)
        # Only two chunks match session 1142.
        self.assertEqual(result['result_count'], 2)

    def test_originating_session_non_int_returns_typed_error(self):
        """Regression guard: non-int input still returns the typed error
        (unchanged behavior)."""
        result = self._dispatch_search_docs({
            'query': 'anything',
            'originating_session': 'not-an-int',
        })
        self.assertIn('error', result)
        self.assertIn('originating_session must be an integer', result['error'])


# ─── F-KB-1: kb_tool limit cap envelope ────────────────────────────────


class KbToolLimitCapTests(TestCase):
    """F-KB-1 — kb_tool `documents`, `chunks`, `search_embeddings`, and
    `semantic_search` actions surface `limit_capped/requested_limit/
    effective_limit/hard_max` when caller-requested limit > 50."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'kb-2728-{uuid.uuid4().hex[:8]}',
            email='kb-2728@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )

    def _dispatch_kb(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_kb_browse(  # type: ignore[attr-defined]
            tool_name='kb_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='test-kb-2728',
        )

    def test_documents_within_cap_no_capped_signal(self):
        result = self._dispatch_kb({'action': 'documents', 'limit': 10})
        self.assertNotIn('limit_capped', result)

    def test_documents_over_cap_surfaces_signal(self):
        result = self._dispatch_kb({'action': 'documents', 'limit': 200})
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('requested_limit'), 200)
        self.assertEqual(result.get('effective_limit'), 50)
        self.assertEqual(result.get('hard_max'), 50)

    def test_chunks_over_cap_surfaces_signal(self):
        # chunks action needs a document_id; the cap envelope applies before
        # the returned rows are counted, so we can test with a bogus id.
        result = self._dispatch_kb({
            'action': 'chunks',
            'document_id': str(uuid.uuid4()),
            'limit': 500,
        })
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('hard_max'), 50)

    def test_search_embeddings_over_cap_surfaces_signal(self):
        result = self._dispatch_kb({
            'action': 'search_embeddings',
            'query': 'anything',
            'limit': 500,
        })
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('hard_max'), 50)

    def test_semantic_search_over_cap_surfaces_signal(self):
        # semantic_search does real work; guard behind a mocked service call
        # so we don't require live pgvector state for the envelope check.
        with mock.patch(
            'core.rag_integration.search_embeddings',
            return_value=[],
        ):
            result = self._dispatch_kb({
                'action': 'semantic_search',
                'query': 'anything',
                'limit': 500,
            })
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('hard_max'), 50)

    def test_default_limit_no_cap_signal(self):
        # Regression guard: default limit=20 must not trigger the cap.
        result = self._dispatch_kb({'action': 'documents'})
        self.assertNotIn('limit_capped', result)

    def test_stats_action_no_limit_envelope(self):
        # Stats action does not accept a limit; response must be unchanged.
        result = self._dispatch_kb({'action': 'stats'})
        self.assertNotIn('limit_capped', result)

"""Session 1234 D14 — min_session=0 LLM-autofill guard regression tests.

Surfaced by Chris's verification of D13 (#2622): Rigby called
``kb_tool action=semantic_search query="morning_brief workflow"`` and
got 0 results. Inspecting the response's ``applied_filters`` showed
``min_session: 0`` — the LLM had autofilled the optional integer
param with 0 even though Chris's request didn't intend a session
filter.

The pre-D14 handlers all used the pattern
``int(x) if x is not None and str(x).isdigit() else None``, which
accepts 0. Search then filters to ``session-N >= 0`` — and since only
handoffs carry session-N tags (per D9), the corpus is silently
narrowed to handoff-only. Combined with similarity_threshold=0.6 on
the morning_brief query, no chunks cleared the bar.

D14 fixes the autofill at all three layers:
- `_d14_resolve_min_session()` helper in td_handlers_ops.py
- D11 kb_tool action=documents handler (uses the helper)
- D13 kb_tool action=semantic_search handler (uses the helper)
- D12 core.rag_integration.search_embeddings (positive-only guard
  inside the filter block)

Same class of bug as `feedback_llm_autofills_boolean_params_with_false`
but extended to integer params.

Run::

    python manage.py test core.tests.test_d14_min_session_autofill_guard -v2
"""

from unittest.mock import patch

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher
from core.services.td_handlers_ops import _d14_resolve_min_session


class ResolveMinSessionHelperTests(TestCase):
    """Direct tests of the `_d14_resolve_min_session` helper."""

    def test_none_returns_none(self):
        self.assertIsNone(_d14_resolve_min_session(None))

    def test_zero_returns_none(self):
        """The load-bearing fix: LLM-autofill of 0 must NOT filter."""
        self.assertIsNone(_d14_resolve_min_session(0))
        self.assertIsNone(_d14_resolve_min_session('0'))

    def test_negative_returns_none(self):
        self.assertIsNone(_d14_resolve_min_session(-5))
        self.assertIsNone(_d14_resolve_min_session('-5'))

    def test_positive_int_passes(self):
        self.assertEqual(_d14_resolve_min_session(1234), 1234)
        self.assertEqual(_d14_resolve_min_session(1), 1)

    def test_positive_string_int_passes(self):
        self.assertEqual(_d14_resolve_min_session('1234'), 1234)

    def test_garbage_returns_none(self):
        self.assertIsNone(_d14_resolve_min_session('not-a-number'))
        self.assertIsNone(_d14_resolve_min_session([1234]))
        self.assertIsNone(_d14_resolve_min_session({}))


class SemanticSearchD14HandlerTests(TestCase):
    """`kb_tool action=semantic_search` payload assembly with D14 guard."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _call_capturing(self, **payload):
        payload.setdefault('action', 'semantic_search')
        payload.setdefault('query', 'something')
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            out = self.dispatcher._handle_kb_browse(
                tool_name='kb_tool',
                payload=payload,
                user_id=None,
                trace_id=None,
            )
        return out, captured

    def test_min_session_0_does_NOT_pass_to_search_embeddings(self):
        """The Chris-verified regression: min_session=0 (LLM autofill)
        must NOT reach search_embeddings as 0 — must be coerced to None."""
        _out, captured = self._call_capturing(min_session=0)
        self.assertIsNone(captured.get('min_session'),
                          'min_session=0 leaked into search_embeddings (LLM-autofill bug).')

    def test_min_session_string_zero_also_blocked(self):
        _out, captured = self._call_capturing(min_session='0')
        self.assertIsNone(captured.get('min_session'))

    def test_min_session_negative_blocked(self):
        _out, captured = self._call_capturing(min_session=-1)
        self.assertIsNone(captured.get('min_session'))

    def test_min_session_positive_passes_through(self):
        _out, captured = self._call_capturing(min_session=1234)
        self.assertEqual(captured.get('min_session'), 1234)

    def test_applied_filters_echo_None_for_zero(self):
        """Response shape: applied_filters.min_session must be None
        (not 0) when the autofill is guarded."""
        out, _captured = self._call_capturing(min_session=0)
        self.assertIsNone(out['applied_filters']['min_session'])

    def test_applied_filters_echo_int_for_positive(self):
        out, _captured = self._call_capturing(min_session=1230)
        self.assertEqual(out['applied_filters']['min_session'], 1230)


class DocumentsActionD14HandlerTests(TestCase):
    """`kb_tool action=documents` applied_filters echo with D14 guard."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _call(self, **payload):
        payload.setdefault('action', 'documents')
        return self.dispatcher._handle_kb_browse(
            tool_name='kb_tool',
            payload=payload,
            user_id=None,
            trace_id=None,
        )

    def test_documents_applied_filters_min_session_0_echoes_None(self):
        """LLM autofills min_session=0; documents handler must echo
        applied_filters.min_session as None so the response is honest
        about what filter was applied (none)."""
        out = self._call(min_session=0)
        self.assertIsNone(out['applied_filters']['min_session'])

    def test_documents_applied_filters_min_session_positive_passes(self):
        out = self._call(min_session=1234)
        self.assertEqual(out['applied_filters']['min_session'], 1234)


class SearchEmbeddingsD14LayerTests(TestCase):
    """D12 layer: `core.rag_integration.search_embeddings` ignores
    min_session <= 0 even if a caller bypasses the D13/D11 surface."""

    def test_search_embeddings_ignores_min_session_zero(self):
        """Defense in depth: if some other caller passes
        min_session=0 directly, the search function still must not
        narrow to handoffs-only."""
        from core.rag_integration import search_embeddings
        from unittest.mock import MagicMock, patch

        # Build a chunk QS mock with full filter chain
        qs_mock = MagicMock()
        qs_mock.filter.return_value = qs_mock
        qs_mock.exclude.return_value = qs_mock
        qs_mock.__getitem__.return_value = []
        qs_mock.__iter__.return_value = iter([])
        qs_mock.values_list.return_value.distinct.return_value = []

        with patch(
            'core.rag_integration.create_embedding',
            return_value=[0.1] * 1536,
        ), patch(
            'content.models.DocumentEmbedding.cosine_similarity_search',
            return_value=qs_mock,
        ):
            search_embeddings('test query', min_session=0)

        # Verify no filter(document_id__in=...) was added for the
        # session-tag filter (that's the path min_session=0 would have
        # triggered pre-D14).
        for call in qs_mock.filter.call_args_list:
            self.assertNotIn(
                'document_id__in', call.kwargs,
                'min_session=0 must NOT trigger document_id__in filter.',
            )

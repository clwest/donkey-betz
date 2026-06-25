"""Session 1234 D15 — similarity_threshold default lowered to 0.4.

Surfaced by Chris's verification of D13 (#2622) after D14 (#2623): the
autofill bug was fixed but kb_tool action=semantic_search still
returned 0 results. Direct ORM check showed the system was finding the
right content (Daily-CoS arc handoffs at similarities 0.567-0.630) —
the 0.6 default threshold was cutting almost all real signal because
text-embedding-3-small puts related-but-not-identical content in the
0.4-0.7 band.

D15 lowers the default from 0.6 → 0.4 at all three layers:
- core/services/td_handlers_ops.py: kb_tool action=semantic_search
- core/rag_integration.py: search_embeddings function signature
- core/rag_integration.py: get_rag_context call site

These tests are regression guards for the default; the contract
itself (clamping, override, etc.) is covered by D13/D14 tests.

Run::

    python manage.py test core.tests.test_d15_similarity_threshold_default -v2
"""

import inspect
from unittest.mock import MagicMock, patch

from django.test import TestCase

from core.rag_integration import search_embeddings
from core.services.tool_dispatcher import ToolDispatcher


class SimilarityThresholdDefaultD15Tests(TestCase):
    """Regression guards for the D15 default of 0.4."""

    def test_search_embeddings_default_is_0_4(self):
        """Function signature default must be 0.4 (D15)."""
        sig = inspect.signature(search_embeddings)
        param = sig.parameters['similarity_threshold']
        self.assertEqual(
            param.default, 0.4,
            f"search_embeddings similarity_threshold default must be 0.4 "
            f"per D15 (was {param.default}). text-embedding-3-small "
            f"clusters related content in 0.4-0.7."
        )

    def test_semantic_search_default_threshold_passes_0_4_to_search(self):
        """When the PA caller doesn't pass similarity_threshold,
        kb_tool action=semantic_search must use 0.4."""
        dispatcher = ToolDispatcher()
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            dispatcher._handle_kb_browse(
                tool_name='kb_tool',
                payload={'action': 'semantic_search', 'query': 'x'},
                user_id=None,
                trace_id=None,
            )

        self.assertEqual(captured.get('similarity_threshold'), 0.4)

    def test_semantic_search_explicit_threshold_overrides(self):
        """D15 only changes the default — explicit override still wins."""
        dispatcher = ToolDispatcher()
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            dispatcher._handle_kb_browse(
                tool_name='kb_tool',
                payload={
                    'action': 'semantic_search',
                    'query': 'x',
                    'similarity_threshold': 0.75,
                },
                user_id=None,
                trace_id=None,
            )

        self.assertEqual(captured.get('similarity_threshold'), 0.75)

    def test_semantic_search_applied_filters_echoes_0_4(self):
        dispatcher = ToolDispatcher()

        with patch(
            'core.rag_integration.search_embeddings',
            return_value=[],
        ):
            out = dispatcher._handle_kb_browse(
                tool_name='kb_tool',
                payload={'action': 'semantic_search', 'query': 'x'},
                user_id=None,
                trace_id=None,
            )

        self.assertEqual(out['applied_filters']['similarity_threshold'], 0.4)

    def test_get_rag_context_call_site_uses_0_4(self):
        """Source-level guard: get_rag_context must pass 0.4 to
        search_embeddings (was 0.6 pre-D15). Cheap to verify via
        source inspection so we don't depend on the embedding service
        in this test."""
        src = inspect.getsource(__import__('core.rag_integration', fromlist=['get_rag_context']).get_rag_context)
        # The threshold appears as a literal kwarg
        self.assertIn('similarity_threshold=0.4', src,
                      "get_rag_context must call search_embeddings with "
                      "similarity_threshold=0.4 per D15.")
        self.assertNotIn('similarity_threshold=0.6', src,
                         "Pre-D15 0.6 threshold must be replaced.")

    def test_search_embeddings_signature_does_not_carry_0_6_or_0_7(self):
        """Belt-and-suspenders: the function signature must not still
        carry the old 0.6 (post-D14 noise) or 0.7 (pre-D12 default)."""
        src = inspect.getsource(search_embeddings)
        # The function-default declaration line
        self.assertIn('similarity_threshold: float = 0.4', src)

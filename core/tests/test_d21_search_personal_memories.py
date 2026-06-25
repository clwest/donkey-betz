"""Session 1234 D21 — search_personal_memories pivot tests.

Pre-D21 the function connected to a non-existent `ai_unified_platform`
database and queried a non-existent `unified_embeddings` table. Every
call silently returned [] — same dead-table issue D12 fixed for
search_embeddings.

D21 pivots to Django ORM against `UserEmbedding` (the actual
user-scoped embedding store, populated by chat memory injection on
Railway). Cosine similarity computed in Python because the field is
JSONField, not pgvector VectorField (fine for the expected corpus
size; migrate to native pgvector when usage grows).

D21 also narrows the broad except to env errors only (matches
D17-D20 discipline) and lowers similarity_threshold default 0.7 →
0.4 to match D15 (text-embedding-3-small puts related content in
0.4-0.7 band).

Run::

    python manage.py test core.tests.test_d21_search_personal_memories -v2
"""

import inspect
from unittest.mock import patch

from django.test import TestCase

from core.rag_integration import (
    search_personal_memories,
    _cosine_similarity_python,
    _PERSONAL_MEMORY_ENV_ERRORS,
)


class CosineSimilarityHelperTests(TestCase):
    """`_cosine_similarity_python` is pure-math; cheap to test directly."""

    def test_identical_vectors_returns_1(self):
        v = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(_cosine_similarity_python(v, v), 1.0)

    def test_orthogonal_vectors_returns_0(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        self.assertAlmostEqual(_cosine_similarity_python(a, b), 0.0)

    def test_opposite_vectors_returns_negative(self):
        a = [1.0, 2.0, 3.0]
        b = [-1.0, -2.0, -3.0]
        self.assertAlmostEqual(_cosine_similarity_python(a, b), -1.0)

    def test_empty_vector_returns_0(self):
        self.assertEqual(_cosine_similarity_python([], [1.0]), 0.0)
        self.assertEqual(_cosine_similarity_python([1.0], []), 0.0)
        self.assertEqual(_cosine_similarity_python(None, [1.0]), 0.0)

    def test_zero_vector_returns_0(self):
        self.assertEqual(_cosine_similarity_python([0, 0, 0], [1, 2, 3]), 0.0)

    def test_mismatched_lengths_returns_0(self):
        self.assertEqual(_cosine_similarity_python([1.0, 2.0], [1.0]), 0.0)


class SignatureAndDefaultsTests(TestCase):
    """Post-D21 contract: signature and default values."""

    def test_default_similarity_threshold_is_0_4(self):
        """D21 lowered the default from 0.7 → 0.4 to match D15."""
        sig = inspect.signature(search_personal_memories)
        self.assertEqual(sig.parameters['similarity_threshold'].default, 0.4)

    def test_no_user_id_returns_empty_list(self):
        """Strict access control: no user_id → no memories."""
        self.assertEqual(search_personal_memories('q', user_id=None), [])
        self.assertEqual(search_personal_memories('q', user_id=0), [])


class NarrowExceptShapeTests(TestCase):
    """`_PERSONAL_MEMORY_ENV_ERRORS` matches the D17-D20 shape."""

    def test_allowlist_contains_required_env_errors(self):
        from django.db.utils import DatabaseError
        self.assertIn(DatabaseError, _PERSONAL_MEMORY_ENV_ERRORS)
        self.assertIn(ConnectionError, _PERSONAL_MEMORY_ENV_ERRORS)
        self.assertIn(OSError, _PERSONAL_MEMORY_ENV_ERRORS)

    def test_allowlist_does_NOT_contain_exception(self):
        self.assertNotIn(Exception, _PERSONAL_MEMORY_ENV_ERRORS)

    def test_allowlist_matches_d17_d20_shape(self):
        """`_PERSONAL_MEMORY_ENV_ERRORS` must contain the same classes
        as the D17-D20 `_RETRIEVAL_ENV_ERRORS` allowlists. The constant
        name differs (this is rag_integration, not a retrieval-helper
        file) but the shape MUST stay aligned so future audits don't
        find divergence between modules."""
        from core.services.scoped_retrieval import (
            _RETRIEVAL_ENV_ERRORS as D17_LIST,
        )
        self.assertEqual(
            set(_PERSONAL_MEMORY_ENV_ERRORS), set(D17_LIST),
            "D21 _PERSONAL_MEMORY_ENV_ERRORS must contain the same "
            "exception classes as the D17-D20 retrieval allowlist.",
        )


class FunctionPivotTests(TestCase):
    """Verify the pivot — function now uses UserEmbedding ORM."""

    def test_function_source_no_longer_imports_psycopg2(self):
        """Pre-D21 raw psycopg2 connection to a dead database. Post-D21
        pure Django ORM."""
        src = inspect.getsource(search_personal_memories)
        self.assertNotIn(
            'psycopg2.connect',
            src,
            "D21 must remove the raw psycopg2 connection to the dead "
            "ai_unified_platform database.",
        )

    def test_function_source_no_longer_executes_dead_table_query(self):
        """Look for actual SQL usage patterns of the dead table,
        not docstring mentions explaining the pre-D21 state."""
        src = inspect.getsource(search_personal_memories)
        for pattern in (
            'FROM unified_embeddings',
            'from unified_embeddings',
            'INTO unified_embeddings',
            '.unified_embeddings',
        ):
            self.assertNotIn(
                pattern, src,
                f"D21 must remove the SQL query pattern '{pattern}' "
                f"that targets the dead unified_embeddings table.",
            )

    def test_function_source_uses_user_embedding_model(self):
        src = inspect.getsource(search_personal_memories)
        self.assertIn(
            "apps.get_model('core', 'UserEmbedding')",
            src,
            "D21 must look up UserEmbedding via apps.get_model "
            "(lazy import to avoid the model_unified_system import "
            "graph at module load).",
        )

    def test_returns_empty_when_no_rows_for_user(self):
        """Empty UserEmbedding table → graceful empty result."""
        # Mock create_embedding so we don't hit OpenAI in tests
        with patch(
            'core.rag_integration.create_embedding',
            return_value=[0.1] * 1536,
        ):
            result = search_personal_memories('q', user_id=99999)
        self.assertEqual(result, [])

    def test_filters_by_user_id_for_access_control(self):
        """Source-level guard: function must filter on user_id to
        prevent cross-user memory leakage."""
        src = inspect.getsource(search_personal_memories)
        self.assertIn('user_id=user_id', src,
                      "Must filter UserEmbedding by user_id for "
                      "access control.")
        self.assertIn('is_active=True', src,
                      "Must filter on is_active=True to skip "
                      "retired memories.")

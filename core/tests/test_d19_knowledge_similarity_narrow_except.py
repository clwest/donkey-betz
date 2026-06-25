"""Session 1234 D19 — knowledge_similarity narrow-except regression tests.

Single-site continuation of D17/D18 narrow-except sweep across
retrieval-domain files. `core/services/knowledge_similarity.py` had
1 site (the embedding service call) using the same anti-pattern.

D19 narrows that site to `_RETRIEVAL_ENV_ERRORS = (DatabaseError,
ConnectionError, OSError)` and extends the cross-file invariant
test to cover all 3 retrieval-domain files (D17 + D18 + D19).

The cross-file invariant is the discipline lock: any future PR
adding a 4th file (knowledge_router companions, views_rag_embeddings,
search_personal_memories) that picks a different allowlist shape
fails the test — surfacing drift to a reviewer rather than letting
it accumulate silently.

Run::

    python manage.py test core.tests.test_d19_knowledge_similarity_narrow_except -v2
"""

import inspect

from django.db.utils import DatabaseError
from django.test import TestCase

from core.services import knowledge_similarity
from core.services.knowledge_similarity import (
    _RETRIEVAL_ENV_ERRORS,
)


class ExceptionAllowlistShapeTests(TestCase):
    """Source-level guards on the D19 allowlist."""

    def test_allowlist_constant_exists(self):
        self.assertIsInstance(_RETRIEVAL_ENV_ERRORS, tuple)
        self.assertGreater(len(_RETRIEVAL_ENV_ERRORS), 0)

    def test_allowlist_contains_required_env_errors(self):
        self.assertIn(DatabaseError, _RETRIEVAL_ENV_ERRORS)
        self.assertIn(ConnectionError, _RETRIEVAL_ENV_ERRORS)
        self.assertIn(OSError, _RETRIEVAL_ENV_ERRORS)

    def test_allowlist_does_NOT_contain_exception(self):
        self.assertNotIn(
            Exception, _RETRIEVAL_ENV_ERRORS,
            "_RETRIEVAL_ENV_ERRORS must NOT include bare Exception.",
        )

    def test_no_bare_except_exception_remains_in_file(self):
        src = inspect.getsource(knowledge_similarity)
        for line in src.split('\n'):
            stripped = line.strip()
            if stripped.startswith('except Exception'):
                self.fail(
                    f"Bare 'except Exception' still present in "
                    f"knowledge_similarity.py — D19 must replace the "
                    f"1 site.\nLine: {line!r}"
                )

    def test_all_except_clauses_use_allowlist(self):
        src = inspect.getsource(knowledge_similarity)
        except_lines = [
            line.strip() for line in src.split('\n')
            if line.strip().startswith('except ')
        ]
        narrowed = sum(
            1 for ln in except_lines
            if '_RETRIEVAL_ENV_ERRORS' in ln
        )
        self.assertEqual(
            narrowed, 1,
            f"Expected 1 except clause using _RETRIEVAL_ENV_ERRORS, "
            f"got {narrowed}. All except clauses:\n  {except_lines}",
        )


class CrossFileAllowlistInvariantTests(TestCase):
    """The discipline lock: D17 + D18 + D19 all narrow-except
    retrieval files MUST share the same allowlist shape.

    Any future PR adding a 4th file with a different exception tuple
    fails these tests — forces drift to be reviewed explicitly.
    """

    def test_d17_d19_allowlists_have_same_shape(self):
        from core.services.scoped_retrieval import (
            _RETRIEVAL_ENV_ERRORS as D17_LIST,
        )
        self.assertEqual(
            set(_RETRIEVAL_ENV_ERRORS), set(D17_LIST),
            "D17 (scoped_retrieval) and D19 (knowledge_similarity) "
            "_RETRIEVAL_ENV_ERRORS must contain the same classes.",
        )

    def test_d18_d19_allowlists_have_same_shape(self):
        from core.services.knowledge_first_router import (
            _RETRIEVAL_ENV_ERRORS as D18_LIST,
        )
        self.assertEqual(
            set(_RETRIEVAL_ENV_ERRORS), set(D18_LIST),
            "D18 (knowledge_first_router) and D19 (knowledge_similarity) "
            "_RETRIEVAL_ENV_ERRORS must contain the same classes.",
        )

    def test_all_three_allowlists_have_same_shape(self):
        """Transitive guarantee: any 2 of {D17, D18, D19} share the
        same shape, so all 3 do."""
        from core.services.scoped_retrieval import (
            _RETRIEVAL_ENV_ERRORS as D17_LIST,
        )
        from core.services.knowledge_first_router import (
            _RETRIEVAL_ENV_ERRORS as D18_LIST,
        )
        shapes = {
            'D17 scoped_retrieval': frozenset(D17_LIST),
            'D18 knowledge_first_router': frozenset(D18_LIST),
            'D19 knowledge_similarity': frozenset(_RETRIEVAL_ENV_ERRORS),
        }
        unique_shapes = set(shapes.values())
        self.assertEqual(
            len(unique_shapes), 1,
            f"All 3 narrow-except retrieval files must share the same "
            f"allowlist shape. Found {len(unique_shapes)} distinct "
            f"shapes:\n  " + '\n  '.join(
                f"{name}: {sorted(c.__name__ for c in classes)}"
                for name, classes in shapes.items()
            ),
        )

"""Session 1234 D18 — knowledge_first_router narrow-except regression tests.

Mirror of D17 for `core/services/knowledge_first_router.py`. Pre-D18
the 6 sub-query methods caught `Exception` and returned the
accumulated matches list (or None for the embedding helper) — same
anti-pattern as D16 / D17. Logic errors (TypeError from
sliced-then-filtered QS, AttributeError on missing fields, KeyError
on schema drift) were silently swallowed as "no matches found."

D18 narrows all 6 sites to `_RETRIEVAL_ENV_ERRORS = (DatabaseError,
ConnectionError, OSError)`. Logic errors now propagate so tests +
production logs surface them.

Run::

    python manage.py test core.tests.test_d18_knowledge_router_narrow_except -v2
"""

import inspect

from django.db.utils import DatabaseError
from django.test import TestCase

from core.services import knowledge_first_router
from core.services.knowledge_first_router import (
    _RETRIEVAL_ENV_ERRORS,
)


class ExceptionAllowlistShapeTests(TestCase):
    """Source-level guards on the D18 allowlist."""

    def test_allowlist_constant_exists(self):
        self.assertIsInstance(_RETRIEVAL_ENV_ERRORS, tuple)
        self.assertGreater(
            len(_RETRIEVAL_ENV_ERRORS), 0,
            "_RETRIEVAL_ENV_ERRORS must include at least one exception class.",
        )

    def test_allowlist_contains_database_error(self):
        self.assertIn(DatabaseError, _RETRIEVAL_ENV_ERRORS,
                      "DB connection drops must remain gracefully handled.")

    def test_allowlist_contains_connection_error(self):
        self.assertIn(ConnectionError, _RETRIEVAL_ENV_ERRORS,
                      "Network failures (embedding service) must stay graceful.")

    def test_allowlist_contains_os_error(self):
        self.assertIn(OSError, _RETRIEVAL_ENV_ERRORS,
                      "OS-level errors must stay graceful.")

    def test_allowlist_does_NOT_contain_exception(self):
        """The whole point of D18: don't catch the umbrella class."""
        self.assertNotIn(
            Exception, _RETRIEVAL_ENV_ERRORS,
            "_RETRIEVAL_ENV_ERRORS must NOT include bare Exception — "
            "that's the pre-D18 bug we're fixing.",
        )

    def test_no_bare_except_exception_remains_in_file(self):
        """Source guard: D18 must replace every `except Exception` in
        knowledge_first_router.py with the narrow allowlist."""
        src = inspect.getsource(knowledge_first_router)
        for line in src.split('\n'):
            stripped = line.strip()
            if stripped.startswith('except Exception'):
                self.fail(
                    f"Bare 'except Exception' still present in "
                    f"knowledge_first_router.py — D18 must replace all "
                    f"6 sites.\nLine: {line!r}"
                )

    def test_all_except_clauses_use_allowlist(self):
        """Every `except` in real code uses _RETRIEVAL_ENV_ERRORS."""
        src = inspect.getsource(knowledge_first_router)
        except_lines = [
            line.strip() for line in src.split('\n')
            if line.strip().startswith('except ')
        ]
        narrowed = sum(
            1 for ln in except_lines
            if '_RETRIEVAL_ENV_ERRORS' in ln
        )
        self.assertEqual(
            narrowed, 6,
            f"Expected 6 except clauses using _RETRIEVAL_ENV_ERRORS, "
            f"got {narrowed}. All except clauses:\n  {except_lines}",
        )

    def test_d17_d18_allowlists_have_same_shape(self):
        """Cross-file invariant: D17 + D18 must share the same
        allowlist tuple so the pattern stays consistent across
        retrieval-domain files."""
        from core.services.scoped_retrieval import (
            _RETRIEVAL_ENV_ERRORS as D17_LIST,
        )
        # Use set-equality so order doesn't trip the assertion
        self.assertEqual(
            set(_RETRIEVAL_ENV_ERRORS), set(D17_LIST),
            "D17 and D18 _RETRIEVAL_ENV_ERRORS must contain the same "
            "exception classes — keeps the narrow-except discipline "
            "consistent across retrieval-domain modules.",
        )

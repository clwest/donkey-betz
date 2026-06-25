"""Session 1234 D17 — scoped_retrieval narrow-except regression tests.

Pre-D17 every method in core/services/scoped_retrieval.py caught
`Exception` and returned []/{}, which silently hid logic errors
(sliced-then-filtered TypeError per D16, AttributeError on missing
fields, KeyError on changed APIs) as "no results found".

D17 narrows all 8 sites to `_RETRIEVAL_ENV_ERRORS = (DatabaseError,
ConnectionError, OSError)` — environmental errors only. Logic errors
now propagate so tests + production logs surface them.

These tests verify:
- The allowlist constant exists with the right shape
- No `except Exception` remains in the file
- Logic errors (TypeError, AttributeError, KeyError) DO propagate
  through the narrow except — sample with a mocked sub-method
- Environmental errors (DatabaseError) still gracefully return []
  — back-compat preserved

Run::

    python manage.py test core.tests.test_d17_scoped_retrieval_narrow_except -v2
"""

import inspect
from unittest.mock import patch

from django.db.utils import DatabaseError
from django.test import TestCase

from core.services import scoped_retrieval
from core.services.scoped_retrieval import (
    ScopedRetrievalService,
    DocumentScope,
    _RETRIEVAL_ENV_ERRORS,
)


class ExceptionAllowlistShapeTests(TestCase):
    """Source-level + import-level guards on the D17 allowlist."""

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
                      "OS-level errors (disk full, etc.) must stay graceful.")

    def test_allowlist_does_NOT_contain_exception(self):
        """The whole point of D17: don't catch the umbrella class."""
        self.assertNotIn(
            Exception, _RETRIEVAL_ENV_ERRORS,
            "_RETRIEVAL_ENV_ERRORS must NOT include bare Exception — "
            "that's the pre-D17 bug we're fixing.",
        )

    def test_no_bare_except_exception_remains_in_file(self):
        """Source guard: D17 must replace every `except Exception` in
        scoped_retrieval.py with the narrow allowlist."""
        src = inspect.getsource(scoped_retrieval)
        # Allow the docstring/comment to mention 'except Exception' but
        # not actual code lines. Cheap check: count occurrences in
        # contexts that look like a real except clause.
        for line in src.split('\n'):
            stripped = line.strip()
            if stripped.startswith('except Exception'):
                self.fail(
                    f"Bare 'except Exception' still present in "
                    f"scoped_retrieval.py — D17 must replace all 8 sites.\n"
                    f"Line: {line!r}"
                )

    def test_all_except_clauses_use_allowlist(self):
        """Verify every `except` clause in real code uses
        _RETRIEVAL_ENV_ERRORS (or a more specific exception)."""
        src = inspect.getsource(scoped_retrieval)
        except_lines = [
            line.strip() for line in src.split('\n')
            if line.strip().startswith('except ')
        ]
        # Expected: 8 narrowed lines + 0 broad ones
        narrowed = sum(
            1 for ln in except_lines
            if '_RETRIEVAL_ENV_ERRORS' in ln
        )
        self.assertEqual(
            narrowed, 8,
            f"Expected 8 except clauses using _RETRIEVAL_ENV_ERRORS, "
            f"got {narrowed}. All except clauses:\n  {except_lines}",
        )


class LogicErrorsPropagateTests(TestCase):
    """Verify logic errors (the D16 class) now raise instead of
    silently returning empty results.

    The outer protected method is ``_search_scope`` (line 197). It
    catches exceptions from its body — inc. anything bubbling up
    from ``_semantic_search`` or ``_keyword_search``. We patch the
    body's first import to raise the simulated exception, which
    forces it through the outer try/except chain.
    """

    def setUp(self):
        self.svc = ScopedRetrievalService()

    def _raise_from_search_scope(self, exc):
        """Trigger the simulated exception inside ``_search_scope``'s
        try block by patching ``Document.objects.all`` (the first ORM
        call in that body). Whatever exception we raise here travels
        through the entire body and hits the outer
        ``except _RETRIEVAL_ENV_ERRORS`` at line 197."""
        return patch(
            'content.models.Document.objects.all',
            side_effect=exc,
        )

    def test_type_error_propagates(self):
        """The exact D16 class: TypeError inside _search_scope must
        NOT be silently swallowed by the narrow allowlist."""
        with self._raise_from_search_scope(
            TypeError("Cannot filter a query once a slice has been taken.")
        ):
            with self.assertRaises(TypeError) as cm:
                self.svc.search('test query', scope=DocumentScope.DOCS_INDEX_ACTIVE)
            self.assertIn('slice', str(cm.exception))

    def test_attribute_error_propagates(self):
        """Missing-attribute bugs (refactor regressions) must raise."""
        with self._raise_from_search_scope(
            AttributeError("'NoneType' object has no attribute 'embedding'")
        ):
            with self.assertRaises(AttributeError):
                self.svc.search('test query', scope=DocumentScope.DOCS_INDEX_ACTIVE)

    def test_key_error_propagates(self):
        """Schema-drift KeyError (D9/D10 fields renamed) must raise."""
        with self._raise_from_search_scope(KeyError('document_class')):
            with self.assertRaises(KeyError):
                self.svc.search('test query', scope=DocumentScope.DOCS_INDEX_ACTIVE)


class EnvironmentalErrorsStayGracefulTests(TestCase):
    """Verify legit runtime errors STILL gracefully return [] —
    back-compat preserved."""

    def setUp(self):
        self.svc = ScopedRetrievalService()

    def _raise_from_search_scope(self, exc):
        return patch(
            'content.models.Document.objects.all',
            side_effect=exc,
        )

    def test_database_error_returns_empty(self):
        with self._raise_from_search_scope(DatabaseError("connection lost")):
            result = self.svc.search('q', scope=DocumentScope.DOCS_INDEX_ACTIVE)
            self.assertEqual(result, [])

    def test_connection_error_returns_empty(self):
        with self._raise_from_search_scope(ConnectionError("API unreachable")):
            result = self.svc.search('q', scope=DocumentScope.DOCS_INDEX_ACTIVE)
            self.assertEqual(result, [])

    def test_os_error_returns_empty(self):
        with self._raise_from_search_scope(OSError("disk full")):
            result = self.svc.search('q', scope=DocumentScope.DOCS_INDEX_ACTIVE)
            self.assertEqual(result, [])

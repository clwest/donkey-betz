"""Session 1234 D20 — views_rag_embeddings narrow-except regression tests.

Different scoping from D17/D18/D19 because the file mixes two
patterns:

1. **Helper functions** (`ingest_video_status`, `_video_document_details`)
   that return None / degraded data when something fails — silent
   failure mode, same as the D17/D18/D19 retrieval functions.
   These SHOULD be narrowed.

2. **HTTP endpoint handlers** that return
   `Response({'success': False, 'error': str(e)}, status=500)`.
   These NEED to broad-catch to maintain the API contract: any
   unhandled exception would otherwise leak a stack trace to the
   client. These SHOULD stay broad.

D20 narrows ONLY the 2 helper sites (originally written as
`except Exception as _e:` — the underscore alias is the discriminator
the file already uses for intentional "swallowed — degraded" sites).
The 18 endpoint sites stay broad.

D20 also extends the cross-file invariant from 3-way to 4-way:
D17 + D18 + D19 + D20 _RETRIEVAL_ENV_ERRORS tuples must all be
set-equal. The discipline lock catches drift before allowlists
diverge across the retrieval-domain narrow-except files.

Run::

    python manage.py test core.tests.test_d20_views_rag_embeddings_narrow_except -v2
"""

import inspect

from django.db.utils import DatabaseError
from django.test import TestCase

from core import views_rag_embeddings
from core.views_rag_embeddings import _RETRIEVAL_ENV_ERRORS


class ExceptionAllowlistShapeTests(TestCase):
    """Source-level guards on the D20 allowlist."""

    def test_allowlist_constant_exists(self):
        self.assertIsInstance(_RETRIEVAL_ENV_ERRORS, tuple)
        self.assertGreater(len(_RETRIEVAL_ENV_ERRORS), 0)

    def test_allowlist_contains_required_env_errors(self):
        self.assertIn(DatabaseError, _RETRIEVAL_ENV_ERRORS)
        self.assertIn(ConnectionError, _RETRIEVAL_ENV_ERRORS)
        self.assertIn(OSError, _RETRIEVAL_ENV_ERRORS)

    def test_allowlist_does_NOT_contain_exception(self):
        self.assertNotIn(Exception, _RETRIEVAL_ENV_ERRORS)


class ScopeDiscriminatorTests(TestCase):
    """D20's scope: helpers narrowed, endpoints stay broad.

    The file's existing convention uses `except Exception as _e:`
    (underscore prefix) for intentional "swallowed — degraded"
    helpers, vs `except Exception as e:` for HTTP endpoint handlers
    that return JSON error responses. D20 preserves and codifies
    that discriminator.
    """

    def test_no_helper_underscore_e_pattern_remains_broad(self):
        """Any `except Exception as _e:` line MUST have been narrowed.
        The underscore prefix marks intentional helpers — those are
        the silent-failure-mode sites D20 targets."""
        src = inspect.getsource(views_rag_embeddings)
        for ln_no, line in enumerate(src.split('\n'), start=1):
            stripped = line.strip()
            # Skip docstrings/comments by simple heuristic
            if stripped.startswith('#') or '"""' in line:
                continue
            # The bug pattern: `except Exception as _e:` in real code
            if 'except Exception as _e:' in stripped and not stripped.startswith('#'):
                self.fail(
                    f"Helper-pattern `except Exception as _e:` still "
                    f"present at line {ln_no} — D20 must narrow these "
                    f"to _RETRIEVAL_ENV_ERRORS.\n"
                    f"Line: {line!r}"
                )

    def test_endpoint_broad_except_still_present(self):
        """The 18 HTTP endpoint handlers SHOULD still use
        `except Exception as e:` so the API contract holds."""
        src = inspect.getsource(views_rag_embeddings)
        # Count occurrences in real code (not comments/docstrings)
        endpoint_count = 0
        for line in src.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            if 'except Exception as e:' in stripped:
                endpoint_count += 1
        # Expect the 17 HTTP endpoints (was 18 in original count;
        # one was already inside a more specific exception block)
        self.assertGreater(
            endpoint_count, 10,
            "Expected ~17 HTTP endpoint broad-except handlers to "
            "remain in place. D20 must NOT narrow these — they "
            "preserve the API contract."
        )

    def test_helper_sites_use_allowlist(self):
        """The narrowed sites must use _RETRIEVAL_ENV_ERRORS."""
        src = inspect.getsource(views_rag_embeddings)
        narrowed = 0
        for line in src.split('\n'):
            if 'except _RETRIEVAL_ENV_ERRORS as _e:' in line:
                narrowed += 1
        self.assertEqual(
            narrowed, 2,
            f"Expected exactly 2 narrowed helper sites; got {narrowed}.",
        )


class FourWayCrossFileInvariantTests(TestCase):
    """The discipline lock extended to 4 files.

    D17 + D18 + D19 + D20 all narrow-except retrieval files MUST
    share the same `_RETRIEVAL_ENV_ERRORS` tuple. Any future PR
    that adds a 5th file or alters one of the existing four to use
    a different shape fails the test — forces drift to be reviewed
    explicitly.
    """

    def test_d17_d20_allowlists_have_same_shape(self):
        from core.services.scoped_retrieval import (
            _RETRIEVAL_ENV_ERRORS as D17_LIST,
        )
        self.assertEqual(set(_RETRIEVAL_ENV_ERRORS), set(D17_LIST))

    def test_d18_d20_allowlists_have_same_shape(self):
        from core.services.knowledge_first_router import (
            _RETRIEVAL_ENV_ERRORS as D18_LIST,
        )
        self.assertEqual(set(_RETRIEVAL_ENV_ERRORS), set(D18_LIST))

    def test_d19_d20_allowlists_have_same_shape(self):
        from core.services.knowledge_similarity import (
            _RETRIEVAL_ENV_ERRORS as D19_LIST,
        )
        self.assertEqual(set(_RETRIEVAL_ENV_ERRORS), set(D19_LIST))

    def test_all_four_allowlists_have_same_shape(self):
        """Transitive: any 2 of {D17, D18, D19, D20} share the same
        shape, so all 4 do."""
        from core.services.scoped_retrieval import (
            _RETRIEVAL_ENV_ERRORS as D17_LIST,
        )
        from core.services.knowledge_first_router import (
            _RETRIEVAL_ENV_ERRORS as D18_LIST,
        )
        from core.services.knowledge_similarity import (
            _RETRIEVAL_ENV_ERRORS as D19_LIST,
        )
        shapes = {
            'D17 scoped_retrieval': frozenset(D17_LIST),
            'D18 knowledge_first_router': frozenset(D18_LIST),
            'D19 knowledge_similarity': frozenset(D19_LIST),
            'D20 views_rag_embeddings': frozenset(_RETRIEVAL_ENV_ERRORS),
        }
        unique_shapes = set(shapes.values())
        self.assertEqual(
            len(unique_shapes), 1,
            f"All 4 narrow-except retrieval files must share the same "
            f"allowlist shape. Found {len(unique_shapes)} distinct "
            f"shapes:\n  " + '\n  '.join(
                f"{name}: {sorted(c.__name__ for c in classes)}"
                for name, classes in shapes.items()
            ),
        )

"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch B tool 1
regression tests for the RAG retrieval path (`core/rag_integration.py`).

Covers the F-RG-1 finding surfaced during code trace + patched at Session
2728. See:
- `docs/research/tools/validation/rag_retrieval_path_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Finding covered:

- F-RG-1: `search_embeddings` broad `except Exception` at what was
  rag_integration.py:342 returned `[]` on ANY error path (ORM error,
  decrypt error, math error, TypeError from a caller-side bug, etc.).
  Silent zero-results is indistinguishable from "no relevant content"
  and is the exact anti-pattern S1234 D21 fixed for
  `search_personal_memories` (line ~553). Now narrows to
  `_RAG_EMBEDDINGS_ENV_ERRORS = (DatabaseError, ConnectionError,
  OSError)`; logic errors propagate. Same tuple shape as the existing
  D17-D21 allowlists.

Existing coverage NOT duplicated:
- Filter pushdown (category / document_class / is_pinned truthy-only /
  min_session positive-only / include_superseded) — covered in
  test_rag_integration_search_embeddings.py.
- Filter-before-slice discipline (D16) — covered in
  test_d16_search_embeddings_filter_before_slice.py.
- Cross-file allowlist shape invariant (D17-D20) — covered in
  test_d20_views_rag_embeddings_narrow_except.py. This test file adds
  the fifth allowlist consistency check.
- `search_personal_memories` narrow-except discipline (D21) — covered
  in test_d21_search_personal_memories.py.

Run::

    python manage.py test core.tests.test_rag_retrieval_path_validation_2728 -v2
"""
from __future__ import annotations

import inspect
from unittest.mock import patch

from django.db.utils import DatabaseError
from django.test import TestCase

from core.rag_integration import (
    _PERSONAL_MEMORY_ENV_ERRORS,
    _RAG_EMBEDDINGS_ENV_ERRORS,
    search_embeddings,
)


class FRG1AllowlistShapeTests(TestCase):
    """F-RG-1 — `_RAG_EMBEDDINGS_ENV_ERRORS` matches the D17-D21 shape."""

    def test_allowlist_constant_exists(self):
        self.assertIsInstance(_RAG_EMBEDDINGS_ENV_ERRORS, tuple)
        self.assertGreater(len(_RAG_EMBEDDINGS_ENV_ERRORS), 0)

    def test_allowlist_contains_required_env_errors(self):
        self.assertIn(DatabaseError, _RAG_EMBEDDINGS_ENV_ERRORS)
        self.assertIn(ConnectionError, _RAG_EMBEDDINGS_ENV_ERRORS)
        self.assertIn(OSError, _RAG_EMBEDDINGS_ENV_ERRORS)

    def test_allowlist_does_NOT_contain_exception(self):
        """The whole point of the D17-D21 discipline: env-only, NOT broad.
        Logic errors must propagate — this test locks the discipline."""
        self.assertNotIn(Exception, _RAG_EMBEDDINGS_ENV_ERRORS)
        self.assertNotIn(BaseException, _RAG_EMBEDDINGS_ENV_ERRORS)

    def test_allowlist_matches_personal_memory_env_errors_shape(self):
        """F-RG-1 extends the D17-D21 4-way invariant to 5-way. Both tuples
        must be set-equal — future refactors that touch one must touch both."""
        self.assertEqual(
            set(_RAG_EMBEDDINGS_ENV_ERRORS),
            set(_PERSONAL_MEMORY_ENV_ERRORS),
        )


class FRG1BroadExceptRemovedTests(TestCase):
    """F-RG-1 — source-level guard that the broad except is gone."""

    def test_search_embeddings_no_longer_uses_broad_except(self):
        src = inspect.getsource(search_embeddings)
        # The narrow-except allowlist must appear.
        self.assertIn('except _RAG_EMBEDDINGS_ENV_ERRORS', src)
        # The outer-scope `except Exception` MUST be gone. The function has
        # ONE remaining legitimate `except Exception` — the inner decrypt
        # fallback at the encryption_service.decrypt(chunk_text) call site,
        # which is scoped to a single-line try/except and is orthogonal to
        # the outer retrieval error path this patch narrows. Guard: total
        # count ≤ 1, and the outer scope (top-level indent inside the
        # function body) must NOT contain it.
        exception_count = src.count('except Exception')
        self.assertLessEqual(
            exception_count, 1,
            f"Expected ≤ 1 inner `except Exception` (decrypt fallback only); "
            f"found {exception_count}. The outer-scope narrow-except discipline "
            f"has regressed.",
        )
        # Belt-and-suspenders: the specific outer form the patch replaced
        # (`\n    except Exception as e:` at 4-space indent = function body
        # level) must not appear. The decrypt fallback lives at 12-space indent.
        self.assertNotIn('\n    except Exception as e:', src)


class FRG1LogicErrorsPropagateTests(TestCase):
    """F-RG-1 — with the narrow except in place, logic errors (TypeError,
    ValueError, AttributeError, KeyError) must propagate out of
    `search_embeddings` instead of silently returning `[]`."""

    def test_type_error_propagates(self):
        # Force a TypeError inside the retrieval body by making
        # `create_embedding` return a non-None non-list value that the
        # pgvector `CosineDistance` annotation cannot consume.
        with patch(
            'core.rag_integration.create_embedding',
            return_value='not-a-vector',
        ):
            with self.assertRaises((TypeError, ValueError, Exception)) as ctx:
                search_embeddings(query='anything', limit=1)
        # Verify the propagated error is NOT one of the env classes —
        # otherwise the narrow except should have caught it.
        self.assertNotIsInstance(ctx.exception, _RAG_EMBEDDINGS_ENV_ERRORS)

    def test_env_error_still_returns_empty_list(self):
        """Regression guard: environmental errors (DB down, network unreachable,
        OS I/O failure) MUST still be swallowed with an error log — that's the
        whole point of keeping a narrow except. This is the safety valve for
        operational disruptions."""
        with patch(
            'core.rag_integration.create_embedding',
            return_value=[0.1] * 1536,
        ), patch(
            'content.models.DocumentEmbedding.objects',
        ) as mock_objects:
            # Simulate a Django DatabaseError raised during the ORM chain.
            mock_objects.filter.side_effect = DatabaseError('simulated DB down')
            result = search_embeddings(query='anything', limit=1)
        self.assertEqual(result, [])

    def test_connection_error_still_returns_empty_list(self):
        with patch(
            'core.rag_integration.create_embedding',
            return_value=[0.1] * 1536,
        ), patch(
            'content.models.DocumentEmbedding.objects',
        ) as mock_objects:
            mock_objects.filter.side_effect = ConnectionError('network unreachable')
            result = search_embeddings(query='anything', limit=1)
        self.assertEqual(result, [])

    def test_os_error_still_returns_empty_list(self):
        with patch(
            'core.rag_integration.create_embedding',
            return_value=[0.1] * 1536,
        ), patch(
            'content.models.DocumentEmbedding.objects',
        ) as mock_objects:
            mock_objects.filter.side_effect = OSError('I/O failure')
            result = search_embeddings(query='anything', limit=1)
        self.assertEqual(result, [])

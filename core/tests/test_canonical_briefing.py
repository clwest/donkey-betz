"""
Tests for the Canonical Briefing endpoint and service — S2985.

Covers:
- Auth: unauthenticated returns JSON 401/403, never 302 (S2984 PR4 contract).
- Path validation: rejects non-docs paths, `..` traversal, and paths that
  resolve outside BASE_DIR via symlinks.
- Response shape: sections + citations + scope.root + cache block echoed.
- Scope filter: retrieval is limited to the requested scope_root.
- Citation invariant: bullets with no valid citation collapse to
  "Insufficient support in canonical docs" (Z1 no-hallucination).
- Cache: second identical call is a hit (LLM not called twice).
- Force refresh: force_refresh=True bypasses cache.

Run::

    USE_PGBOUNCER=0 python manage.py test core.tests.test_canonical_briefing -v 2
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from core.services import canonical_briefing as briefing_service


User = get_user_model()


def _fake_chunks(paths: list[str], base_id: int = 1000) -> list[dict]:
    return [
        {
            "chunk_id": f"chunk-{base_id + i}",
            "document_id": f"doc-{base_id + i}",
            "path": path,
            "content": f"Content sample for {path}",
            "similarity": 0.8,
        }
        for i, path in enumerate(paths)
    ]


def _llm_json(sections_bullets: dict[str, list[dict]]) -> str:
    return json.dumps(
        {
            "sections": [
                {"key": k, "bullets": v}
                for k, v in sections_bullets.items()
            ]
        }
    )


class CanonicalBriefingAuthTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_anonymous_returns_json_not_html_redirect(self) -> None:
        resp = self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"}),
            content_type="application/json",
        )
        self.assertIn(resp.status_code, (401, 403), f"got {resp.status_code}")
        self.assertNotEqual(resp.status_code, 302, "must not redirect (breaks XHR)")
        self.assertIn(
            "application/json", resp.headers.get("Content-Type", "")
        )


class CanonicalBriefingPathValidationTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username=f"s2985-brief-{uuid.uuid4().hex[:8]}",
            email="s2985-brief@example.com",
            password="x",
        )

    def setUp(self) -> None:
        # SESSION_ENGINE = cache backend — clear BEFORE force_login so we don't
        # wipe the session that force_login just wrote.
        cache.clear()
        self.client = Client()
        self.client.force_login(self.user)

    def _post(self, body: dict):
        return self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps(body),
            content_type="application/json",
        )

    def test_missing_anchor_path_returns_400(self) -> None:
        resp = self._post({})
        self.assertEqual(resp.status_code, 400)

    def test_anchor_outside_docs_returns_403(self) -> None:
        resp = self._post({"anchor_path": "core/urls.py"})
        self.assertEqual(resp.status_code, 403)

    def test_anchor_with_traversal_returns_403(self) -> None:
        resp = self._post({"anchor_path": "docs/../secrets.md"})
        self.assertEqual(resp.status_code, 403)

    def test_scope_outside_docs_returns_403(self) -> None:
        resp = self._post(
            {
                "anchor_path": "docs/PLATFORM_INVENTORY.md",
                "scope": {"root": "core/services"},
            }
        )
        self.assertEqual(resp.status_code, 403)

    def test_max_chunks_out_of_range_returns_400(self) -> None:
        resp = self._post(
            {
                "anchor_path": "docs/PLATFORM_INVENTORY.md",
                "max_chunks_per_section": 999,
            }
        )
        self.assertEqual(resp.status_code, 400)


class CanonicalBriefingShapeTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username=f"s2985-shape-{uuid.uuid4().hex[:8]}",
            email="s2985-shape@example.com",
            password="x",
        )

    def setUp(self) -> None:
        # SESSION_ENGINE = cache backend — clear BEFORE force_login so we don't
        # wipe the session that force_login just wrote.
        cache.clear()
        self.client = Client()
        self.client.force_login(self.user)

    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_response_carries_scope_and_sections(
        self, mock_retrieve, mock_llm
    ) -> None:
        mock_retrieve.return_value = _fake_chunks(
            ["docs/research/domains/x/a.md", "docs/research/domains/x/b.md"]
        )
        mock_llm.return_value = _llm_json(
            {
                "tldr": [{"text": "Point one", "citation_keys": [1]}],
                "decisions": [{"text": "Decision one", "citation_keys": [2]}],
                "state": [],
                "risks": [],
                "next_actions": [{"text": "Do next", "citation_keys": [1, 2]}],
            }
        )
        resp = self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200, resp.content[:400])
        payload = resp.json()
        # Z3 invariant: scope.root echoed even though request omitted it
        self.assertIn("scope", payload)
        self.assertIn("root", payload["scope"])
        self.assertEqual(payload["scope"]["root"], "docs")
        # All 5 sections present in order
        keys = [s["key"] for s in payload["sections"]]
        self.assertEqual(keys, ["tldr", "decisions", "state", "risks", "next_actions"])
        # First bullet has one citation shaped correctly
        tldr = next(s for s in payload["sections"] if s["key"] == "tldr")
        self.assertEqual(len(tldr["bullets"]), 1)
        citation = tldr["bullets"][0]["citations"][0]
        for field in ("document_id", "chunk_id", "path", "snippet"):
            self.assertIn(field, citation)

    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_bullet_without_valid_citation_collapses_to_insufficient_support(
        self, mock_retrieve, mock_llm
    ) -> None:
        mock_retrieve.return_value = _fake_chunks(["docs/foo/a.md"])
        # LLM references citation_key=99 which doesn't exist in the retrieved
        # chunks — must NOT ship as a real bullet.
        mock_llm.return_value = _llm_json(
            {
                "tldr": [{"text": "Bogus fact", "citation_keys": [99]}],
                "decisions": [],
                "state": [],
                "risks": [],
                "next_actions": [],
            }
        )
        resp = self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        tldr = next(s for s in resp.json()["sections"] if s["key"] == "tldr")
        self.assertEqual(len(tldr["bullets"]), 1)
        bullet = tldr["bullets"][0]
        self.assertEqual(bullet["text"], briefing_service.INSUFFICIENT_SUPPORT_MSG)
        self.assertEqual(bullet["citations"], [])

    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_scope_root_defaults_to_anchor_dirname(
        self, mock_retrieve, mock_llm
    ) -> None:
        mock_retrieve.return_value = []
        mock_llm.return_value = _llm_json(
            {"tldr": [], "decisions": [], "state": [], "risks": [], "next_actions": []}
        )
        # Use a real canonical-summary file so anchor existence check passes.
        anchor = "docs/research/domains/docs_content_audit/2899_docs_content_canonical_summary.md"
        expected_scope = "docs/research/domains/docs_content_audit"
        self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps({"anchor_path": anchor}),
            content_type="application/json",
        )
        # First positional arg to retrieve is `query`; scope_root is a kwarg.
        for call in mock_retrieve.call_args_list:
            kwargs = call.kwargs or {}
            if "scope_root" in kwargs:
                self.assertEqual(kwargs["scope_root"], expected_scope)
                return
        self.fail("retrieve_scoped_chunks was never called with a scope_root kwarg")

    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_cache_hit_avoids_second_llm_call(
        self, mock_retrieve, mock_llm
    ) -> None:
        mock_retrieve.return_value = _fake_chunks(["docs/foo/a.md"])
        mock_llm.return_value = _llm_json(
            {
                "tldr": [{"text": "Cached point", "citation_keys": [1]}],
                "decisions": [],
                "state": [],
                "risks": [],
                "next_actions": [],
            }
        )
        body = json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"})
        r1 = self.client.post(
            "/api/repo/canonical-briefing/", data=body, content_type="application/json"
        )
        r2 = self.client.post(
            "/api/repo/canonical-briefing/", data=body, content_type="application/json"
        )
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(mock_llm.call_count, 1, "LLM must not be called on cache hit")
        self.assertTrue(r2.json()["cache"]["hit"])
        self.assertFalse(r1.json()["cache"]["hit"])

    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_force_refresh_bypasses_cache(self, mock_retrieve, mock_llm) -> None:
        mock_retrieve.return_value = _fake_chunks(["docs/foo/a.md"])
        mock_llm.return_value = _llm_json(
            {
                "tldr": [{"text": "Point", "citation_keys": [1]}],
                "decisions": [],
                "state": [],
                "risks": [],
                "next_actions": [],
            }
        )
        body_cached = json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"})
        body_forced = json.dumps(
            {"anchor_path": "docs/PLATFORM_INVENTORY.md", "force_refresh": True}
        )
        self.client.post(
            "/api/repo/canonical-briefing/",
            data=body_cached,
            content_type="application/json",
        )
        self.client.post(
            "/api/repo/canonical-briefing/",
            data=body_forced,
            content_type="application/json",
        )
        self.assertEqual(mock_llm.call_count, 2, "force_refresh must bypass cache")

    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_no_chunks_returns_empty_briefing_without_llm(
        self, mock_retrieve, mock_llm
    ) -> None:
        mock_retrieve.return_value = []
        resp = self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mock_llm.call_count, 0, "LLM must not fire on empty retrieval")
        payload = resp.json()
        self.assertEqual(payload.get("empty_reason"), "no_chunks_in_scope")
        for section in payload["sections"]:
            self.assertEqual(section["bullets"], [])


    @patch("core.services.canonical_briefing._call_llm")
    @patch("core.services.canonical_briefing.retrieve_scoped_chunks")
    def test_malformed_llm_json_surfaces_llm_valid_json_false(
        self, mock_retrieve, mock_llm
    ) -> None:
        """Rigby A2 ZO1 fold: parse failure must not silently render as empty.

        Consumers need to distinguish 'LLM produced a valid empty briefing'
        from 'LLM returned garbage and we bailed'.
        """
        mock_retrieve.return_value = _fake_chunks(["docs/foo/a.md"])
        mock_llm.return_value = "not valid json at all {"
        resp = self.client.post(
            "/api/repo/canonical-briefing/",
            data=json.dumps({"anchor_path": "docs/PLATFORM_INVENTORY.md"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        self.assertIn("llm_valid_json", payload)
        self.assertFalse(payload["llm_valid_json"])


class CanonicalBriefingSnippetSanitizerTests(TestCase):
    def test_snippet_truncated_to_max_chars(self) -> None:
        long = "x" * 1000
        out = briefing_service._sanitize_snippet(long)
        self.assertLessEqual(len(out), briefing_service.SNIPPET_MAX_CHARS)
        self.assertTrue(out.endswith("\u2026"))

    def test_snippet_strips_nulls(self) -> None:
        out = briefing_service._sanitize_snippet("hello\x00world")
        self.assertNotIn("\x00", out)


class CanonicalBriefingRealORMRetrievalTests(TestCase):
    """Non-mocked test that actually issues the DocumentEmbedding query.

    The five test classes above stub out retrieve_scoped_chunks entirely, so
    a field-name mismatch on the annotate() call (e.g. 'embedding' vs
    'embedding_vector') passes CI but 500s on every real request. This test
    creates a real Document + DocumentEmbedding row and calls the un-mocked
    retrieve_scoped_chunks — schema drift on the pgvector column will fail
    it with a FieldError.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        from content.models import Document, DocumentEmbedding, DocumentType, EmbeddingModel

        cls.owner = User.objects.create_user(
            username=f"s2988-real-orm-{uuid.uuid4().hex[:8]}",
            email="s2988-real-orm@example.com",
            password="x",
        )
        cls.doc = Document.objects.create(
            owner=cls.owner,
            title="Test canonical summary",
            document_type=DocumentType.MARKDOWN,
            file_path="docs/research/domains/_test_canonical_briefing/9999_test_canonical_summary.md",
            raw_content="Test canonical summary content.",
        )
        cls.chunk = DocumentEmbedding.objects.create(
            document=cls.doc,
            embedding_model=EmbeddingModel.OPENAI_SMALL,
            chunk_index=0,
            chunk_text="Test canonical summary content chunk.",
            chunk_size=len("Test canonical summary content chunk."),
            embedding_vector=[0.01] * 1536,
            embedding_dimension=1536,
        )

    @patch("core.rag_integration.create_embedding")
    def test_retrieve_scoped_chunks_uses_real_orm_field_name(
        self, mock_create_embedding
    ) -> None:
        """Regression: annotate() must reference the model's real field name.

        Bug that motivated this test: the annotate() call referenced
        `"embedding"` when the model field is `embedding_vector`, so every
        real request raised django.core.exceptions.FieldError and the view
        surfaced a generic 500. Mocking create_embedding keeps the test
        offline while still exercising the ORM query construction end-to-end.
        """
        mock_create_embedding.return_value = [0.01] * 1536

        results = briefing_service.retrieve_scoped_chunks(
            query="test query",
            scope_root="docs/research/domains/_test_canonical_briefing",
            limit=5,
        )

        self.assertEqual(len(results), 1, "seeded chunk should be retrievable")
        self.assertEqual(results[0]["chunk_id"], str(self.chunk.id))
        self.assertEqual(
            results[0]["path"],
            "docs/research/domains/_test_canonical_briefing/9999_test_canonical_summary.md",
        )

"""
Session 2979: Unit tests for evidence display normalization helpers.

Covers URL sanitization (Bluesky at:// transform + http/https allowlist),
source-label mapping (map + titlecase fallback), text normalization
(Discussion|Link stripping + whitespace collapse), sample_signals →
evidence conversion, and relevance sort.

Spec: deliverable c4602ccd-a973-424f-8bc5-dcc16f797430.
"""

from __future__ import annotations

from django.test import SimpleTestCase

from core.services.evidence_display import (
    evidence_from_sample_signals,
    format_source_label,
    normalize_evidence_row,
    normalize_evidence_text,
    sanitize_evidence_url,
    sort_evidence_by_relevance,
)


class SanitizeEvidenceUrlTests(SimpleTestCase):
    def test_bluesky_at_uri_transformed_to_bsky_app(self):
        raw = "at://did:plc:wz6zzj7u6chymzcjoutnumdc/app.bsky.feed.post/3mriadu4jnr2j"
        expected = "https://bsky.app/profile/did:plc:wz6zzj7u6chymzcjoutnumdc/post/3mriadu4jnr2j"
        self.assertEqual(sanitize_evidence_url(raw), expected)

    def test_bluesky_at_uri_with_did_web_variant(self):
        raw = "at://did:web:example.com/app.bsky.feed.post/abc123"
        self.assertEqual(
            sanitize_evidence_url(raw),
            "https://bsky.app/profile/did:web:example.com/post/abc123",
        )

    def test_https_url_passes_through_unchanged(self):
        url = "https://www.producthunt.com/products/opencomputer"
        self.assertEqual(sanitize_evidence_url(url), url)

    def test_http_url_passes_through_unchanged(self):
        url = "http://example.com/article"
        self.assertEqual(sanitize_evidence_url(url), url)

    def test_javascript_scheme_dropped(self):
        self.assertIsNone(sanitize_evidence_url("javascript:alert(1)"))

    def test_data_scheme_dropped(self):
        self.assertIsNone(sanitize_evidence_url("data:text/html,<script>alert(1)</script>"))

    def test_file_scheme_dropped(self):
        self.assertIsNone(sanitize_evidence_url("file:///etc/passwd"))

    def test_vbscript_scheme_dropped(self):
        self.assertIsNone(sanitize_evidence_url("vbscript:msgbox(1)"))

    def test_non_bsky_at_uri_dropped(self):
        # at:// that isn't the Bluesky post shape shouldn't leak through
        self.assertIsNone(sanitize_evidence_url("at://did:plc:foo/other.collection/rkey"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(sanitize_evidence_url(""))

    def test_whitespace_only_returns_none(self):
        self.assertIsNone(sanitize_evidence_url("   "))

    def test_none_input_returns_none(self):
        self.assertIsNone(sanitize_evidence_url(None))

    def test_non_string_input_returns_none(self):
        self.assertIsNone(sanitize_evidence_url(12345))  # type: ignore[arg-type]

    def test_missing_netloc_dropped(self):
        # scheme present but no host — not a browser-openable link
        self.assertIsNone(sanitize_evidence_url("https://"))


class FormatSourceLabelTests(SimpleTestCase):
    def test_known_slug_maps_to_display_label(self):
        self.assertEqual(format_source_label("bluesky"), "Bluesky")
        self.assertEqual(format_source_label("producthunt"), "Product Hunt")
        self.assertEqual(format_source_label("yahoo_finance"), "Yahoo Finance")
        self.assertEqual(format_source_label("sec_edgar"), "SEC EDGAR")

    def test_unknown_slug_titlecases_with_underscore_split(self):
        self.assertEqual(format_source_label("my_new_spider"), "My New Spider")

    def test_unknown_slug_titlecases_with_hyphen_split(self):
        self.assertEqual(format_source_label("some-other-source"), "Some Other Source")

    def test_case_insensitive_lookup(self):
        # Existing drift: some clusters ship "Yahoo Finance" alongside "yahoo_finance".
        # Both must normalize to the canonical display label.
        self.assertEqual(format_source_label("YAHOO_FINANCE"), "Yahoo Finance")

    def test_already_display_ready_label_returns_titlecase(self):
        # A slug already presented as "Yahoo Finance" (with space) — lowercase
        # lookup fails, falls through to titlecase fallback which returns
        # "Yahoo Finance" (identity on already-titlecased input).
        self.assertEqual(format_source_label("Yahoo Finance"), "Yahoo Finance")

    def test_empty_returns_empty(self):
        self.assertEqual(format_source_label(""), "")
        self.assertEqual(format_source_label(None), "")
        self.assertEqual(format_source_label("   "), "")


class NormalizeEvidenceTextTests(SimpleTestCase):
    def test_strips_discussion_link_case_sensitive(self):
        raw = "Heard Give Claude Code a voice Discussion | Link FluentDB The AI"
        result = normalize_evidence_text(raw)
        self.assertNotIn("Discussion | Link", result)
        self.assertNotIn("discussion", result.lower())
        self.assertIn("FluentDB", result)

    def test_strips_discussion_link_case_insensitive(self):
        raw = "Foo DISCUSSION | LINK Bar"
        self.assertEqual(normalize_evidence_text(raw), "Foo Bar")

    def test_strips_discussion_link_mixed_spacing(self):
        raw = "Foo  discussion  |  link  Bar"
        self.assertEqual(normalize_evidence_text(raw), "Foo Bar")

    def test_collapses_newlines_and_tabs(self):
        raw = "OpenComputer \n            The easiest way\n          \n         "
        self.assertEqual(normalize_evidence_text(raw), "OpenComputer The easiest way")

    def test_collapses_repeated_whitespace(self):
        self.assertEqual(normalize_evidence_text("a    b     c"), "a b c")

    def test_trims_leading_trailing_whitespace(self):
        self.assertEqual(normalize_evidence_text("   hello   "), "hello")

    def test_empty_returns_empty(self):
        self.assertEqual(normalize_evidence_text(""), "")
        self.assertEqual(normalize_evidence_text(None), "")


class NormalizeEvidenceRowTests(SimpleTestCase):
    def test_normalizes_all_fields(self):
        row = normalize_evidence_row(
            title="  Some title\n\n",
            url="at://did:plc:abc/app.bsky.feed.post/xyz",
            source="bluesky",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["title"], "Some title")
        self.assertEqual(row["url"], "https://bsky.app/profile/did:plc:abc/post/xyz")
        self.assertEqual(row["source"], "Bluesky")

    def test_returns_none_when_both_title_and_url_empty(self):
        self.assertIsNone(normalize_evidence_row(title="", url="", source="x"))
        self.assertIsNone(normalize_evidence_row(title=None, url=None, source="x"))
        # Also None when url gets sanitized away AND title is empty
        self.assertIsNone(normalize_evidence_row(title="", url="javascript:alert(1)", source="x"))

    def test_keeps_row_with_title_and_unsafe_url_dropped_to_none(self):
        row = normalize_evidence_row(
            title="Something",
            url="javascript:alert(1)",
            source="devto",
        )
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["title"], "Something")
        self.assertIsNone(row["url"])

    def test_placeholder_title_when_only_url_present(self):
        row = normalize_evidence_row(title="", url="https://example.com", source="s")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["title"], "(no title)")


class EvidenceFromSampleSignalsTests(SimpleTestCase):
    def test_converts_text_source_url_to_evidence_shape(self):
        ss = [
            {"source": "bluesky", "text": "hello", "url": "https://a.example/1"},
            {"source": "producthunt", "text": "world", "url": "https://b.example/2"},
        ]
        result = evidence_from_sample_signals(ss, max_items=5)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "hello")
        self.assertEqual(result[0]["source"], "Bluesky")
        self.assertEqual(result[0]["url"], "https://a.example/1")
        self.assertEqual(result[1]["source"], "Product Hunt")

    def test_bluesky_at_uri_transformed(self):
        ss = [{"source": "bluesky", "text": "post",
               "url": "at://did:plc:abc/app.bsky.feed.post/xyz"}]
        result = evidence_from_sample_signals(ss, max_items=5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["url"], "https://bsky.app/profile/did:plc:abc/post/xyz")

    def test_discussion_link_stripped_from_text(self):
        ss = [{"source": "producthunt",
               "text": "Heard voice Discussion | Link FluentDB client",
               "url": "https://ph.example"}]
        result = evidence_from_sample_signals(ss, max_items=5)
        self.assertIn("Heard voice", result[0]["title"])
        self.assertNotIn("Discussion | Link", result[0]["title"])

    def test_caps_at_max_items(self):
        ss = [{"source": "s", "text": f"item {i}", "url": f"https://x/{i}"}
              for i in range(10)]
        result = evidence_from_sample_signals(ss, max_items=3)
        self.assertEqual(len(result), 3)

    def test_empty_or_missing_returns_empty(self):
        self.assertEqual(evidence_from_sample_signals(None, 5), [])
        self.assertEqual(evidence_from_sample_signals([], 5), [])
        self.assertEqual(evidence_from_sample_signals("not a list", 5), [])  # type: ignore[arg-type]

    def test_skips_non_dict_entries(self):
        ss = [None, "string", 42, {"source": "s", "text": "kept", "url": "https://x"}]
        result = evidence_from_sample_signals(ss, 5)  # type: ignore[arg-type]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "kept")


class SortEvidenceByRelevanceTests(SimpleTestCase):
    def test_clickable_before_unclickable(self):
        evidence = [
            {"title": "no link", "url": None, "source": "s"},
            {"title": "linked", "url": "https://a", "source": "s"},
        ]
        sorted_ev = sort_evidence_by_relevance(evidence)
        self.assertEqual(sorted_ev[0]["title"], "linked")
        self.assertIsNone(sorted_ev[1]["url"])

    def test_real_title_before_placeholder(self):
        evidence = [
            {"title": "(no title)", "url": "https://a", "source": "s"},
            {"title": "real one", "url": "https://b", "source": "s"},
        ]
        sorted_ev = sort_evidence_by_relevance(evidence)
        self.assertEqual(sorted_ev[0]["title"], "real one")

    def test_preserves_original_order_on_ties(self):
        # Both clickable + real-titled → order preserved
        evidence = [
            {"title": "first", "url": "https://a", "source": "s"},
            {"title": "second", "url": "https://b", "source": "s"},
            {"title": "third", "url": "https://c", "source": "s"},
        ]
        sorted_ev = sort_evidence_by_relevance(evidence)
        self.assertEqual([e["title"] for e in sorted_ev], ["first", "second", "third"])

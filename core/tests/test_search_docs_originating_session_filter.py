"""Tests for the Session 1145 P2 ``originating_session`` filter on
``search_docs``.

The filter is implemented as a pure function in
``core.services.td_handlers_ops._filter_chunks_by_originating_session``
so we can test the contract without mocking the corpus, Django auth, or
the tool dispatcher.

Contract (per Rigby spec):
1) Chunks whose source doc has a matching ``originating_session`` are kept.
2) Chunks whose source doc has a different ``originating_session`` are
   excluded and counted in ``excluded_mismatch``.
3) Chunks whose source doc is **missing** from the provenance index are
   excluded and counted in ``excluded_missing_provenance`` — we can't
   claim a doc belongs to a session if we don't know its origin.
4) Chunks lacking a ``file`` key are excluded as missing-provenance.
"""

import unittest

from core.services.td_handlers_ops import _filter_chunks_by_originating_session


# Realistic provenance shape (subset of docs/_provenance.json's "docs" block).
_PROV_DOCS = {
    "docs/handoffs/SESSION_1142_DOCS_HYGIENE.md": {
        "originating_session": 1142,
        "confidence": "HIGH",
        "match_source": "subject",
    },
    "docs/topics/personal-assistant.md": {
        "originating_session": 1142,
        "confidence": "MEDIUM",
        "match_source": "body",
    },
    "docs/architecture/SYSTEM_MAP.md": {
        "originating_session": 128,
        "confidence": "MEDIUM",
        "match_source": "body",
    },
    "docs/PLATFORM_INVENTORY.md": {
        "originating_session": 84,
        "confidence": "MEDIUM",
        "match_source": "body",
    },
}


def _chunk(path: str, chunk_id: str = "c0", text: str = "lorem ipsum") -> dict:
    """Build a minimal search_docs chunk dict."""
    return {
        "file": path,
        "chunk_id": chunk_id,
        "citation": f"[{path}#{chunk_id}]",
        "text": text,
    }


class FilterChunksByOriginatingSessionTests(unittest.TestCase):
    def test_keeps_chunks_with_matching_session(self):
        chunks = [
            _chunk("docs/handoffs/SESSION_1142_DOCS_HYGIENE.md"),
            _chunk("docs/topics/personal-assistant.md"),
        ]
        kept, mismatch, missing = _filter_chunks_by_originating_session(
            chunks, 1142, _PROV_DOCS
        )
        self.assertEqual(len(kept), 2)
        self.assertEqual(mismatch, 0)
        self.assertEqual(missing, 0)
        self.assertEqual(
            [c["file"] for c in kept],
            [
                "docs/handoffs/SESSION_1142_DOCS_HYGIENE.md",
                "docs/topics/personal-assistant.md",
            ],
        )

    def test_excludes_mismatching_session_into_mismatch_bucket(self):
        chunks = [
            _chunk("docs/handoffs/SESSION_1142_DOCS_HYGIENE.md"),  # match
            _chunk("docs/architecture/SYSTEM_MAP.md"),              # session 128
            _chunk("docs/PLATFORM_INVENTORY.md"),                   # session 84
        ]
        kept, mismatch, missing = _filter_chunks_by_originating_session(
            chunks, 1142, _PROV_DOCS
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["file"], "docs/handoffs/SESSION_1142_DOCS_HYGIENE.md")
        self.assertEqual(mismatch, 2)
        self.assertEqual(missing, 0)

    def test_missing_provenance_is_excluded_when_filter_active(self):
        chunks = [
            _chunk("docs/never-tracked.md"),       # not in provenance at all
            _chunk("docs/topics/personal-assistant.md"),  # matches session 1142
        ]
        kept, mismatch, missing = _filter_chunks_by_originating_session(
            chunks, 1142, _PROV_DOCS
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0]["file"], "docs/topics/personal-assistant.md")
        self.assertEqual(mismatch, 0)
        self.assertEqual(missing, 1)

    def test_chunk_without_file_key_counted_as_missing(self):
        chunks = [
            {"chunk_id": "c0", "text": "stray"},  # no 'file' key
            _chunk("docs/topics/personal-assistant.md"),
        ]
        kept, mismatch, missing = _filter_chunks_by_originating_session(
            chunks, 1142, _PROV_DOCS
        )
        self.assertEqual(len(kept), 1)
        self.assertEqual(missing, 1)
        self.assertEqual(mismatch, 0)

    def test_empty_provenance_excludes_everything(self):
        chunks = [
            _chunk("docs/handoffs/SESSION_1142_DOCS_HYGIENE.md"),
            _chunk("docs/topics/personal-assistant.md"),
        ]
        kept, mismatch, missing = _filter_chunks_by_originating_session(
            chunks, 1142, {}
        )
        self.assertEqual(len(kept), 0)
        self.assertEqual(mismatch, 0)
        self.assertEqual(missing, 2)

    def test_filter_to_unknown_session_returns_nothing(self):
        chunks = [
            _chunk("docs/handoffs/SESSION_1142_DOCS_HYGIENE.md"),
            _chunk("docs/topics/personal-assistant.md"),
        ]
        kept, mismatch, missing = _filter_chunks_by_originating_session(
            chunks, 99999, _PROV_DOCS
        )
        self.assertEqual(len(kept), 0)
        self.assertEqual(mismatch, 2)
        self.assertEqual(missing, 0)

"""S2818 pilot — discovery-layer authority boost for DOC_LIFECYCLE §2c.

Ratifies the AUTHORITY_FILE_BONUS mechanism in core.rag.top_k:
- exact-path match against corpus file field
- applied unconditionally (independent of boost_hints)
- PLATFORM_INVENTORY.md gets +20 (pilot scope: 1 doc)

Regression baseline for the T3 C5 finding: `search_docs("How many spiders
do we have")` at Group 2700 arc close returned archived Oct 2025 morning
report as top-1 with PLATFORM_INVENTORY.md absent from returned set. The
integration test simulates that shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase

import core.rag as core_rag
from core.rag import AUTHORITY_FILE_BONUS, _authority_bonus, top_k


class AuthorityBonusUnitTests(SimpleTestCase):
    def test_exact_path_match_bonus(self):
        expected = AUTHORITY_FILE_BONUS["PLATFORM_INVENTORY.md"]
        self.assertEqual(_authority_bonus("PLATFORM_INVENTORY.md"), expected)

    def test_docs_prefix_normalized(self):
        expected = AUTHORITY_FILE_BONUS["PLATFORM_INVENTORY.md"]
        self.assertEqual(_authority_bonus("docs/PLATFORM_INVENTORY.md"), expected)

    def test_non_authority_file_returns_zero(self):
        self.assertEqual(_authority_bonus("archive/morning-report-2025-10-02.md"), 0)
        self.assertEqual(_authority_bonus("PLATFORM_WHAT_IT_IS.md"), 0)

    def test_empty_path_returns_zero(self):
        self.assertEqual(_authority_bonus(""), 0)

    def test_pilot_scope_is_one_doc(self):
        # Guard against silent scope creep. Expanding the list is intentional
        # and requires a fresh SIGN cycle per 2799 §8 item #1.
        self.assertEqual(list(AUTHORITY_FILE_BONUS.keys()), ["PLATFORM_INVENTORY.md"])


class AuthorityBonusIntegrationTests(SimpleTestCase):
    def _write_corpus(self, output: Path, rows: list[dict]) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def test_c5_shape_boost_lifts_platform_inventory_into_top_3(self):
        """T3 C5 regression: given a corpus where an archived doc has high
        token overlap with a counts query but PLATFORM_INVENTORY.md has low
        overlap, the authority boost should still lift the inventory into
        top-3."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            # Archived morning report — 4 exact query-token matches, mimics
            # the actual T3 C5 top-1 chunk that surfaces the wrong answer.
            archive_text = (
                "How many spiders do we have registered in Redis? "
                "1550 spiders registered. Many spiders. Many many spiders."
            )
            # Two additional decoys mimicking T3 C5 top-2/top-3 (audit doc
            # + handoff doc) that reference the query intent.
            decoy_a = "How many spiders — see T3 audit for the answer many"
            decoy_b = "How many spiders reference in handoff many many"
            # PLATFORM_INVENTORY.md chunk — LOW token overlap with the
            # query (only 'spiders' matches). Without the authority boost,
            # this would score 1 and rank below the decoys.
            inventory_text = "80 spiders across 41 categories per registry snapshot"
            self._write_corpus(
                output,
                [
                    {"file": "archive/morning-report-2025-10-02.md", "chunk_id": 0, "text": archive_text},
                    {"file": "audits/T3_audit.md", "chunk_id": 0, "text": decoy_a},
                    {"file": "handoffs/SESSION_2813.md", "chunk_id": 0, "text": decoy_b},
                    {"file": "PLATFORM_INVENTORY.md", "chunk_id": 0, "text": inventory_text},
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("How many spiders do we have", k=3, boost_hints=False)

            top_files = [h["file"] for h in hits]
            self.assertIn(
                "PLATFORM_INVENTORY.md",
                top_files,
                f"S2818 pilot success criterion: PLATFORM_INVENTORY.md must "
                f"appear in top-3 for counts query. Got: {top_files}",
            )

    # Note on non-counts-query regression: the authority boost applies
    # unconditionally, so PLATFORM_INVENTORY.md can outrank a genuinely
    # relevant doc on unrelated queries whose text happens to overlap
    # weakly (e.g., substring-matching "in" against "inventory"). This
    # is the known coupling risk Rigby flagged in the S2818 SIGN Q4
    # zoom-out. Rather than encode a synthetic threshold here, the pilot
    # verifies the actual regression risk empirically via live
    # search_docs on a non-counts query (T3 B1 shape: "add a new spider
    # to the network"). Post-pilot amendments would move authority
    # weighting into the embedding-based retrieval layer where semantic
    # relevance can gate the boost.

    def test_authority_bonus_applies_when_boost_hints_false(self):
        """Explicit check: PA search_docs passes boost_hints=False. The
        authority boost must still fire in that path — that's the whole
        pilot rationale."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # Only the authority doc, with zero token overlap. Must
                    # still be returned because the bonus lifts base>0.
                    {"file": "PLATFORM_INVENTORY.md", "chunk_id": 0, "text": "unrelated"},
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("zero overlap query", k=1, boost_hints=False)

            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["file"], "PLATFORM_INVENTORY.md")

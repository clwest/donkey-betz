"""S2820 — orientation-doc exclusion for the lexical `top_k` ranker.

Last lexical policy in the discovery-layer pilot chain
S2818 (unconditional authority boost) → S2819 (query-intent gating) →
S2820 (orientation-doc exclusion). Chris declared the lexical pilot
"feature complete" at S2820 close; S2821+ evaluates embedding-based
retrieval against the benchmark corpus this arc built.

Validates: `_EXCLUDED_FILE_PATHS` skip inside `top_k` unconditionally
removes matching rows from scoring, regardless of query text or gate
state. Contamination scenario from S2819 §5.2 is covered by an
integration test that mirrors the pain shape.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase

import core.rag as core_rag
from core.rag import _EXCLUDED_FILE_PATHS, top_k


class ExcludedFilePathsUnitTests(SimpleTestCase):
    def test_pilot_scope_is_orientation_doc_only(self):
        # Guard against silent expansion. Handoffs empirically did NOT
        # contaminate at S2820 baseline; expanding requires fresh SIGN.
        self.assertEqual(_EXCLUDED_FILE_PATHS, frozenset({"00-START-NEXT-SESSION.md"}))

    def test_excluded_set_is_frozen(self):
        # frozenset makes it a value, not a mutation surface.
        self.assertIsInstance(_EXCLUDED_FILE_PATHS, frozenset)


class TopKExclusionIntegrationTests(SimpleTestCase):
    def _write_corpus(self, output: Path, rows: list[dict]) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def test_excluded_doc_never_appears_even_when_best_match(self):
        """S2819 §5.2 contamination shape: 00-START chunk has verbatim
        overlap with a query, high base score. Without S2820 exclusion,
        it would rank #1. With exclusion, it must not appear at all —
        and a genuinely-competing lower-overlap doc wins."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # 00-START chunk — 5/5 query-token match (would win pre-S2820).
                    {
                        "file": "00-START-NEXT-SESSION.md",
                        "chunk_id": 3,
                        "text": "add a new spider to the network — example queued item",
                    },
                    # Tutorial doc — 3/5 token match.
                    {
                        "file": "topics/spider-network.md",
                        "chunk_id": 0,
                        "text": "spider network add configuration guide",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("add a new spider to the network", k=3, boost_hints=False)

            top_files = [h["file"] for h in hits]
            self.assertNotIn(
                "00-START-NEXT-SESSION.md",
                top_files,
                f"S2820 exclusion violated. Got: {top_files}",
            )
            self.assertIn("topics/spider-network.md", top_files)

    def test_exclusion_holds_even_with_authority_gate_forced_on(self):
        """The excluded doc is skipped BEFORE the authority-gate branch,
        so no gate override or boost can rescue it."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # 00-START would normally win with authority_gate=True
                    # forcing the +8 bonus even on unrelated queries. It
                    # must still be excluded.
                    {
                        "file": "00-START-NEXT-SESSION.md",
                        "chunk_id": 0,
                        "text": "queued items and pilot descriptions",
                    },
                    {
                        "file": "PLATFORM_INVENTORY.md",
                        "chunk_id": 0,
                        "text": "80 spiders across 41 categories",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k(
                    "how many spiders",
                    k=3,
                    boost_hints=False,
                    authority_gate=True,
                )

            top_files = [h["file"] for h in hits]
            self.assertNotIn("00-START-NEXT-SESSION.md", top_files)

    def test_non_excluded_docs_still_scored_normally(self):
        """Regression check: exclusion mechanism only affects excluded
        paths. Other paths still score via token overlap + boosts + gate."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    {
                        "file": "topics/spider-network.md",
                        "chunk_id": 0,
                        "text": "add a new spider to the network guide",
                    },
                    {
                        "file": "docs/other.md",
                        "chunk_id": 0,
                        "text": "unrelated content",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("add a new spider to the network", k=2, boost_hints=False)

            self.assertEqual(hits[0]["file"], "topics/spider-network.md")

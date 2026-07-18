"""S2819 Shape C — query-intent gating for AUTHORITY_FILE_BONUS.

Follow-on from S2818 pilot per envelope §6. S2818 shipped an unconditional
per-chunk +8 authority boost on PLATFORM_INVENTORY.md that fixed the T3
C5 counts-query failure but degraded the T3 B1 non-counts scenario
("add a new spider to the network") via result-set monoculture. Shape C
gates the boost on query intent via a count/inventory-listing pattern
check — preserving counts-query success while eliminating the non-counts
regression.

Success criterion (from S2818 envelope §6 + handoff §6):
- Q1-Q4 counts queries STILL return PLATFORM_INVENTORY.md in top-3
- Q5 "add a new spider to the network" returns tutorial doc to top-3
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import SimpleTestCase

import core.rag as core_rag
from core.rag import _COUNT_INTENT_PATTERNS, _looks_like_count_query, top_k


class LooksLikeCountQueryUnitTests(SimpleTestCase):
    def test_how_many_matches(self):
        self.assertTrue(_looks_like_count_query("How many spiders do we have"))

    def test_how_much_matches(self):
        self.assertTrue(_looks_like_count_query("How much memory does the worker use"))

    def test_number_of_matches(self):
        self.assertTrue(_looks_like_count_query("Number of celery tasks registered"))

    def test_count_of_matches(self):
        self.assertTrue(_looks_like_count_query("count of agents in registry"))

    def test_total_matches(self):
        self.assertTrue(_looks_like_count_query("total agents currently enabled"))

    def test_list_all_matches(self):
        # Per Rigby SIGN Q2 empirical evidence: PLATFORM_INVENTORY.md
        # already dominates "list all spiders" today post-S2818; the
        # pattern set includes "list all" to preserve that behavior
        # rather than regress it via too-narrow count gating.
        self.assertTrue(_looks_like_count_query("list all spiders in the registry"))

    def test_case_insensitive(self):
        self.assertTrue(_looks_like_count_query("HOW MANY spiders"))
        self.assertTrue(_looks_like_count_query("How Many spiders"))

    def test_non_count_query_does_not_match(self):
        self.assertFalse(_looks_like_count_query("add a new spider to the network"))
        self.assertFalse(_looks_like_count_query("what is the personal assistant"))
        self.assertFalse(_looks_like_count_query("explain the spider architecture"))

    def test_empty_query_does_not_match(self):
        self.assertFalse(_looks_like_count_query(""))
        self.assertFalse(_looks_like_count_query(None))

    def test_pattern_set_is_pilot_scope(self):
        # Guard against silent pattern expansion. Expanding the set is
        # intentional and requires a fresh SIGN cycle.
        self.assertEqual(
            _COUNT_INTENT_PATTERNS,
            (
                "how many",
                "how much",
                "number of",
                "count of",
                "total",
                "list all",
            ),
        )


class TopKIntentGatingIntegrationTests(SimpleTestCase):
    def _write_corpus(self, output: Path, rows: list[dict]) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    def test_gate_auto_fires_for_count_query(self):
        """Default `authority_gate=None` computes gate from question.
        Count query → boost fires → authority doc wins."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # Archive doc mimicking T3 C5 top-1 chunk with high overlap.
                    {
                        "file": "archive/morning-report.md",
                        "chunk_id": 0,
                        "text": "How many spiders do we have? 1550 spiders registered. Many many spiders.",
                    },
                    # Authority doc with weak overlap — bonus is what lifts it.
                    {
                        "file": "PLATFORM_INVENTORY.md",
                        "chunk_id": 0,
                        "text": "80 spiders across 41 categories in registry",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("How many spiders do we have", k=3, boost_hints=False)

            top_files = [h["file"] for h in hits]
            self.assertIn(
                "PLATFORM_INVENTORY.md",
                top_files,
                f"Count-intent query should fire auto-gate. Got: {top_files}",
            )

    def test_gate_auto_skips_for_non_count_query(self):
        """Default `authority_gate=None` computes gate from question.
        Non-count query → boost does NOT fire → the tutorial doc with
        high overlap outranks the authority doc. This is the S2818 Q5
        regression eliminated."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # Tutorial doc — high token overlap with non-count query.
                    {
                        "file": "topics/spider-network.md",
                        "chunk_id": 0,
                        "text": "To add a new spider to the network, register it in the spider registry",
                    },
                    # Authority doc — weak overlap; would win at +8 if gate fires.
                    {
                        "file": "PLATFORM_INVENTORY.md",
                        "chunk_id": 0,
                        "text": "spider registry snapshot",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k(
                    "add a new spider to the network register in registry",
                    k=2,
                    boost_hints=False,
                )

            # Success criterion: authority doc must NOT outrank the tutorial
            # for a non-count query. This is the T3 B1 case the S2818 pilot
            # regressed and S2819 Shape C is designed to fix.
            self.assertEqual(
                hits[0]["file"],
                "topics/spider-network.md",
                f"Non-count query should NOT auto-fire authority gate. Got top-1: {hits[0]['file']}",
            )

    def test_gate_force_true_overrides_intent_detection(self):
        """Explicit `authority_gate=True` fires boost even for non-count
        queries. Allows future intent-aware layers to override."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    {
                        "file": "PLATFORM_INVENTORY.md",
                        "chunk_id": 0,
                        "text": "unrelated to any query terms",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k(
                    "explain the spider architecture",
                    k=1,
                    boost_hints=False,
                    authority_gate=True,
                )

            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["file"], "PLATFORM_INVENTORY.md")

    def test_gate_force_false_suppresses_boost_for_count_query(self):
        """Explicit `authority_gate=False` suppresses boost even for count
        queries. Useful for A/B experiments or debugging."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # High-overlap archive; wins without boost.
                    {
                        "file": "archive/morning-report.md",
                        "chunk_id": 0,
                        "text": "How many spiders — 1550 spiders many spiders",
                    },
                    # Authority doc with weak overlap; loses without boost.
                    {
                        "file": "PLATFORM_INVENTORY.md",
                        "chunk_id": 0,
                        "text": "80 spiders",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k(
                    "How many spiders",
                    k=1,
                    boost_hints=False,
                    authority_gate=False,
                )

            # Without the gate, high-overlap archive wins.
            self.assertEqual(hits[0]["file"], "archive/morning-report.md")

    def test_list_all_intent_fires_gate(self):
        """Per Rigby SIGN Q2: PLATFORM_INVENTORY.md already dominates
        "list all spiders" today post-S2818. Adding "list all" to the
        pattern set preserves that behavior under the gate."""
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / ".rag" / "corpus.jsonl"
            self._write_corpus(
                output,
                [
                    # Tutorial doc — moderate overlap with "list all spiders".
                    {
                        "file": "topics/spider-network.md",
                        "chunk_id": 0,
                        "text": "spiders are listed all together in the registry",
                    },
                    # Authority doc with weak overlap; boost lifts it.
                    {
                        "file": "PLATFORM_INVENTORY.md",
                        "chunk_id": 0,
                        "text": "80 spiders in the registry",
                    },
                ],
            )

            with patch.object(core_rag, "CORPUS_PATH", output):
                hits = top_k("list all spiders", k=2, boost_hints=False)

            top_files = [h["file"] for h in hits]
            self.assertIn("PLATFORM_INVENTORY.md", top_files)

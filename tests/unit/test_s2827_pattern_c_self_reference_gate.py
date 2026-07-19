# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
"""S2827 Pattern C — SELF_REFERENCE candidate injection gate unit tests.

Validates the pure-regex intent gate (`_detect_self_reference_intent`)
+ pattern-to-anchor map wiring. DB-heavy injection composition is
smoke-covered by the S2827 handoff §6 measurement report + full 18-row
Phase-0.5 re-measurement (in-conversation evidence attached to the S2827
close cascade). This file focuses on the regex-narrowness invariant that
Chris D-Q1 acceptance depends on: gate must fire on the 4 intended
Phase-0.5 SELF_REFERENCE rows, NOT fire on non-target queries, and
NOT overlap with the future Pattern D literal-filename policy class per
Chris D5 + Chris D-Q4.
"""
import pytest

from core.rag_integration import (
    _detect_self_reference_intent,
    _SELF_REFERENCE_ANCHORS,
    _SELF_REFERENCE_PATTERN_TO_ANCHOR,
    _SELF_REFERENCE_INTENT_PATTERNS,
)


class TestSelfReferenceGatePositives:
    """Gate MUST fire on the 4 Phase-0.5 SELF_REFERENCE queries + return
    the correct anchor key mapping. These are the Chris D-Q1 acceptance
    conversions ratified 2026-07-19 (Q14/Q15/Q16/Q17)."""

    @pytest.mark.parametrize("query,expected_anchor_key", [
        # Q14 — "the next session start doc" (v2-tightened: file-context word required)
        ("the next session start doc", "start_doc"),
        # Q15 — "where do I start"
        ("where do I start", "start_doc"),
        # Q15 case variation
        ("Where do I START?", "start_doc"),
        # Q16 — "start here"
        ("start here", "start_doc"),
        # Q17 — "project rules"
        ("project rules", "project_rules"),
        # v2 singular acceptance per Rigby Q1 refinement
        ("project rule", "project_rules"),
        # Q14 variations
        ("session start file", "start_doc"),
        ("session start page", "start_doc"),
        ("the session start doc", "start_doc"),
        ("next session start md", "start_doc"),
        # Q16 v2 tightening: `next session` / `new session` explicit
        ("start next session", "start_doc"),
        ("start new session", "start_doc"),
    ])
    def test_gate_fires_and_maps_correctly(self, query, expected_anchor_key):
        matches = _detect_self_reference_intent(query)
        assert matches, f"Gate did not fire on positive query: {query!r}"
        anchor_keys = [key for key, _ in matches]
        assert expected_anchor_key in anchor_keys, (
            f"Expected anchor {expected_anchor_key!r} not in matched anchors "
            f"{anchor_keys!r} for query {query!r}"
        )


class TestSelfReferenceGateNegatives:
    """Gate MUST NOT fire on non-target queries. Enforces Chris D5
    distinct-mechanism-per-class discipline (no COUNT / literal-filename
    / DISCOVERY overlap) + Chris D-Q4 Pattern D forward-carry (literal
    filenames explicitly out-of-scope for Pattern C)."""

    @pytest.mark.parametrize("query,reason", [
        # N1 — spider ops query, no SELF_REFERENCE regex match
        ("add a new spider", "no self_reference regex"),
        # N2 — COUNT domain (Pattern B territory)
        ("how many spiders", "COUNT domain"),
        # N3 — no self_reference regex
        ("morning brief workflow", "no self_reference regex"),
        # N5 — `start` alone is NOT gated (context word required)
        ("start the celery worker", "start alone requires here/next session/new session"),
        ("start the worker", "start alone"),
        ("start over", "start alone"),
        # N7 — DISCOVERY class
        ("what does the platform inventory list", "DISCOVERY class"),
        # N8 — literal filename → Pattern D
        ("PLATFORM_INVENTORY", "literal filename → Pattern D"),
        # N9 — v2 tightening: `session start reflection` no longer fires
        ("session start reflection", "v2 tightening required file-context word"),
        ("session start notes", "v2 tightening"),
        ("the session start went well", "v2 tightening"),
        # N10 — literal Q20 → Pattern D
        ("00-START-NEXT-SESSION", "literal filename → Pattern D per Chris D-Q4"),
        # N11 — literal CLAUDE.md → Pattern D
        ("CLAUDE.md", "literal filename → Pattern D per Chris D-Q4"),
        ("claude.md", "literal filename lowercase → Pattern D"),
        # empty / whitespace
        ("", "empty query"),
        ("   ", "whitespace-only"),
    ])
    def test_gate_does_not_fire(self, query, reason):
        matches = _detect_self_reference_intent(query)
        assert not matches, (
            f"Gate spuriously fired on negative query {query!r} "
            f"(reason: {reason}) — matched {matches!r}"
        )


class TestSelfReferenceGateWiringInvariants:
    """Structural invariants — pattern tuple, anchor map, and
    pattern-to-anchor tuple must remain in sync. Enforces Chris D-Q3
    forward-carry: if this file ever gets refactored into a shared
    "pointer-intent registry" (post-Pattern D), these invariants become
    the primary contract."""

    def test_pattern_count_matches_pattern_to_anchor_count(self):
        assert len(_SELF_REFERENCE_INTENT_PATTERNS) == len(_SELF_REFERENCE_PATTERN_TO_ANCHOR), (
            "Every pattern must have an anchor-key mapping"
        )

    def test_all_pattern_anchors_exist_in_anchor_map(self):
        for anchor_key in _SELF_REFERENCE_PATTERN_TO_ANCHOR:
            assert anchor_key in _SELF_REFERENCE_ANCHORS, (
                f"Pattern maps to anchor {anchor_key!r} not defined in "
                f"_SELF_REFERENCE_ANCHORS ({sorted(_SELF_REFERENCE_ANCHORS.keys())})"
            )

    def test_anchor_paths_are_repo_root_not_docs_prefixed(self):
        """Chris D-Q2 corpus label correction: anchors MUST be repo-root
        real paths, not `docs/…` (which was the S2825 corpus label
        defect). Enforces that a future author cannot silently reintroduce
        the drift class."""
        for key, path in _SELF_REFERENCE_ANCHORS.items():
            assert not path.startswith('docs/'), (
                f"Anchor {key!r} maps to `{path!r}` — repo-root paths "
                "MUST NOT have `docs/` prefix per Chris D-Q2 ground-truth "
                "invariant"
            )

    def test_gate_returns_tuple_not_list(self):
        """Return-type invariant — tuple is immutable so downstream
        callers cannot mutate the matched-anchor sequence in place."""
        assert isinstance(_detect_self_reference_intent("where do I start"), tuple)
        assert isinstance(_detect_self_reference_intent("no match"), tuple)

    def test_gate_deduplicates_when_multiple_patterns_map_to_same_anchor(self):
        """If a query matches multiple patterns that map to the SAME
        anchor (e.g., both `start here` + `session start doc`), the anchor
        key must appear only ONCE in the matched tuple — otherwise the
        composition loop would apply the bonus twice."""
        # "start here" fires pattern 1 (start_doc); "session start doc" fires pattern 2 (start_doc)
        matches = _detect_self_reference_intent("start here — where do I session start doc")
        anchor_keys = [key for key, _ in matches]
        assert anchor_keys.count("start_doc") == 1, (
            f"start_doc appeared {anchor_keys.count('start_doc')} times in "
            f"{anchor_keys!r} — dedup broken"
        )

    def test_gate_returns_multiple_anchors_when_query_matches_distinct_classes(self):
        """Rigby SIGN Q1 edge case — if a single query matches BOTH
        start_doc and project_rules patterns (hypothetical; not in
        Phase-0.5 corpus), gate returns BOTH anchor keys."""
        matches = _detect_self_reference_intent("where do I start with project rules")
        anchor_keys = {key for key, _ in matches}
        assert anchor_keys == {"start_doc", "project_rules"}, (
            f"Multi-anchor gate broken: got {anchor_keys!r}"
        )

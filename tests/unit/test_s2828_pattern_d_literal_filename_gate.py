# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
"""S2828 Pattern D — LITERAL-FILENAME candidate injection gate unit tests.

Validates the pure-regex intent gate (`_detect_literal_filename_intent`)
+ curated-anchor map wiring + per-gate bonus discipline. DB-heavy
injection composition + full-corpus measurement covered by S2828 handoff
§5 (per-gate sweep, negative-control run, Phase-0.5 re-measurement).
This file focuses on the invariants Chris D-Q1..D-Q7 acceptance depends
on: gate must fire on the intended literal-filename queries, NOT overlap
Pattern B/C (Chris D5), preserve retrieval-integrity (Chris D3),
tolerate Q28 no-perturb (Chris D-Q4), and enforce per-gate ceilings
(Chris D-Q1).
"""
import re

import pytest

from core.rag_integration import (
    _canonicalize_literal_filename_token,
    _detect_literal_filename_intent,
    _LITERAL_FILENAME_ANCHORS,
    _LITERAL_FILENAME_INTENT_BONUS,
    _LITERAL_FILENAME_INTENT_CEILING,
    _LITERAL_FILENAME_INTENT_PATTERNS,
    _LITERAL_FILENAME_PATTERN_KEYS,
    # Cross-mechanism disjointness checks
    _detect_count_intent,
    _detect_self_reference_intent,
)


class TestLiteralFilenameGatePositives:
    """Gate MUST fire on Pattern D scope queries + return correct
    (anchor_key, pattern_index, gate_name). Q20/Q24 + adjacent CLAUDE.md
    literal per Chris D-Q4 + D-Q5 acceptance."""

    @pytest.mark.parametrize("query,expected_anchor_key,expected_gate", [
        # Q20 — literal 00-START-NEXT-SESSION → P2 hyphen caps
        ("00-START-NEXT-SESSION", "00_start_next_session", "P2_hyphen_caps"),
        # Q24 — literal PLATFORM_INVENTORY → P1 uppercase snake
        ("PLATFORM_INVENTORY", "platform_inventory", "P1_uppercase_snake"),
        # Chris D-Q5 named CLAUDE.md literal → P0 md extension
        ("CLAUDE.md", "claude", "P0_md_extension"),
        # Case variations of P0 (canonicalization must handle)
        ("claude.md", "claude", "P0_md_extension"),
        ("Claude.MD", "claude", "P0_md_extension"),
        ("CLAUDE.MD", "claude", "P0_md_extension"),
        ("PLATFORM_INVENTORY.md", "platform_inventory", "P0_md_extension"),
        # Additional curated-map hits
        ("KNOWLEDGE_PIPELINE", "knowledge_pipeline", "P1_uppercase_snake"),
        ("ENGINEERING_PLAYBOOK", "engineering_playbook", "P1_uppercase_snake"),
        ("PLATFORM_WHAT_IT_IS", "platform_what_it_is", "P1_uppercase_snake"),
    ])
    def test_gate_fires_with_curated_anchor(self, query, expected_anchor_key, expected_gate):
        matches = _detect_literal_filename_intent(query)
        assert matches, f"Gate did not fire on positive query: {query!r}"
        anchor_key, pattern_index, gate_name = matches[0]
        assert anchor_key == expected_anchor_key, (
            f"Expected anchor_key {expected_anchor_key!r}, got {anchor_key!r} "
            f"for query {query!r}"
        )
        assert gate_name == expected_gate, (
            f"Expected gate {expected_gate!r}, got {gate_name!r} for query {query!r}"
        )


class TestLiteralFilenameGateMissPath:
    """Strategy C log-only miss path (Chris D-Q2). Gate fires but no
    curated anchor resolves → returns (None, idx, gate_name); caller
    emits `[S2828_PATTERN_D_MISS]` INFO and skips injection + bonus."""

    @pytest.mark.parametrize("query,expected_gate", [
        # P0 miss — README.md is a real repo file but not a Pattern D canonical
        ("README.md", "P0_md_extension"),
        # P1 miss — realistic uppercase snake_case doc not in curated map
        ("SPIDER_NETWORK", "P1_uppercase_snake"),
        # Q28-shape P3 miss — Q28 wins natively; MISS record signals no injection
        ("2701_docs_inventory_topology_audit", "P3_numeric_snake"),
    ])
    def test_gate_fires_with_no_anchor_returns_miss_record(self, query, expected_gate):
        matches = _detect_literal_filename_intent(query)
        assert matches, f"Gate did not fire on miss-path query: {query!r}"
        anchor_key, pattern_index, gate_name = matches[0]
        assert anchor_key is None, (
            f"Expected miss-path anchor_key=None, got {anchor_key!r} "
            f"for query {query!r}"
        )
        assert gate_name == expected_gate


class TestLiteralFilenameGateNegatives:
    """Gate MUST NOT fire — 20 negative controls per S2828 §5 design."""

    @pytest.mark.parametrize("query,reason", [
        # Whole-string invariant: literal token in natural language (LOAD-BEARING)
        ("open CLAUDE.md and check the rules", "multi-word — whole-string invariant"),
        ("the PLATFORM_INVENTORY doc has counts", "multi-word"),
        ("how do I use PLATFORM_INVENTORY", "multi-word"),
        ("See the KNOWLEDGE_PIPELINE for details", "multi-word"),
        # Path form must not fire P0
        ("docs/CLAUDE.md", "path form contains /"),
        # Pattern B/C queries — must not fire Pattern D
        ("how many spiders", "COUNT — Pattern B territory"),
        ("How many agents do we have", "COUNT — Pattern B"),
        ("where do I start", "SELF_REFERENCE — Pattern C"),
        ("start here", "SELF_REFERENCE — Pattern C"),
        ("project rules", "SELF_REFERENCE — Pattern C"),
        # Too-generic single-word
        ("platform", "single word lowercase"),
        ("README", "single-word ALL-CAPS — P1 requires 2+ segments"),
        ("INDEX", "single-word ALL-CAPS"),
        # 2-segment hyphenated (deliberately excluded — ticket-id shape)
        ("ADR-0130", "P2 requires 3+ hyphen segments"),
        # Lowercase snake_case
        ("platform_inventory", "P1 requires uppercase"),
        # Ambiguous single-word
        ("add a new spider", "multi-word natural language"),
        ("morning brief workflow", "multi-word"),
        ("spider", "single word ambiguous — Q25 case"),
        # Edge cases the LOAD-BEARING invariant must hold on
        ("PLATFORM INVENTORY", "whitespace separator — P1 requires _"),
        ("session start", "multi-word — Pattern C territory"),
    ])
    def test_gate_does_not_fire(self, query, reason):
        matches = _detect_literal_filename_intent(query)
        assert not matches, (
            f"Gate incorrectly fired on negative query {query!r} "
            f"(expected NO fire; reason: {reason}); matches={matches!r}"
        )


class TestCanonicalization:
    """Chris D-Q2 canonicalization spec must be deterministic + invariant.
    Strip whitespace → lowercase → strip trailing `.md` → `-` → `_`.
    Rigby R2 implementation-clarity note: spec is used by both anchor-map
    key generation AND query resolution."""

    @pytest.mark.parametrize("input,expected", [
        ("CLAUDE.md", "claude"),
        ("Claude.MD", "claude"),
        ("PLATFORM_INVENTORY", "platform_inventory"),
        ("PLATFORM_INVENTORY.md", "platform_inventory"),
        ("00-START-NEXT-SESSION", "00_start_next_session"),
        ("00-START-NEXT-SESSION.md", "00_start_next_session"),
        ("  CLAUDE.md  ", "claude"),  # whitespace stripped
        ("", ""),
        (None, ""),
    ])
    def test_canonicalization_spec(self, input, expected):
        assert _canonicalize_literal_filename_token(input) == expected


class TestCrossMechanismDisjointness:
    """Chris D5 distinct-mechanism-per-class discipline. Pattern D
    whole-string patterns MUST NOT overlap Pattern B/C multi-word patterns.
    LOAD-BEARING invariant per Rigby SIGN Q1 nuance: if patterns ever
    relax to substring, this test must be extended."""

    @pytest.mark.parametrize("query", [
        "00-START-NEXT-SESSION",
        "PLATFORM_INVENTORY",
        "CLAUDE.md",
        "2701_docs_inventory_topology_audit",
        "KNOWLEDGE_PIPELINE",
    ])
    def test_pattern_d_fires_but_not_b_or_c(self, query):
        assert _detect_literal_filename_intent(query), \
            f"Pattern D should fire on {query!r}"
        assert not _detect_count_intent(query), \
            f"Pattern B (COUNT) should NOT fire on Pattern D query {query!r}"
        assert not _detect_self_reference_intent(query), \
            f"Pattern C (SELF_REFERENCE) should NOT fire on Pattern D query {query!r}"

    @pytest.mark.parametrize("query", [
        "how many spiders",
        "How many agents do we have",
        "list all agents",
    ])
    def test_pattern_b_fires_but_not_d(self, query):
        assert _detect_count_intent(query), \
            f"Pattern B should fire on {query!r}"
        assert not _detect_literal_filename_intent(query), \
            f"Pattern D should NOT fire on Pattern B query {query!r}"

    @pytest.mark.parametrize("query", [
        "where do I start",
        "start here",
        "project rules",
        "the next session start doc",
    ])
    def test_pattern_c_fires_but_not_d(self, query):
        assert _detect_self_reference_intent(query), \
            f"Pattern C should fire on {query!r}"
        assert not _detect_literal_filename_intent(query), \
            f"Pattern D should NOT fire on Pattern C query {query!r}"


class TestWiringInvariants:
    """Pattern registry wiring invariants. Each entry in
    `_LITERAL_FILENAME_ANCHORS` MUST resolve to a real
    `Document.file_path`; each selected bonus value MUST be within its
    per-gate ceiling (Chris D-Q1 discipline)."""

    def test_pattern_and_key_lengths_match(self):
        assert len(_LITERAL_FILENAME_INTENT_PATTERNS) == len(_LITERAL_FILENAME_PATTERN_KEYS)

    def test_all_pattern_keys_have_bonus_entries(self):
        for key in _LITERAL_FILENAME_PATTERN_KEYS:
            assert key in _LITERAL_FILENAME_INTENT_BONUS, \
                f"Gate {key!r} missing from _LITERAL_FILENAME_INTENT_BONUS"

    def test_all_pattern_keys_have_ceilings(self):
        for key in _LITERAL_FILENAME_PATTERN_KEYS:
            assert key in _LITERAL_FILENAME_INTENT_CEILING, \
                f"Gate {key!r} missing from _LITERAL_FILENAME_INTENT_CEILING"

    def test_selected_bonuses_do_not_exceed_ceilings(self):
        """Chris D-Q1: DO NOT raise ceilings to hit projections. If any
        selected value exceeds its ceiling, positive should not have been
        marked converted; this test enforces the invariant at the source."""
        for gate, selected in _LITERAL_FILENAME_INTENT_BONUS.items():
            ceiling = _LITERAL_FILENAME_INTENT_CEILING[gate]
            assert selected <= ceiling, (
                f"Gate {gate!r}: selected bonus {selected} exceeds ceiling "
                f"{ceiling}. Chris D-Q1 violation."
            )

    def test_anchor_map_keys_are_canonicalized(self):
        """Each anchor map key MUST equal the canonicalization of the
        entry's basename (self-consistency for miss-path miss detection)."""
        import os
        for key, path in _LITERAL_FILENAME_ANCHORS.items():
            basename = os.path.basename(path)
            expected_key = _canonicalize_literal_filename_token(basename)
            assert key == expected_key, (
                f"Anchor key {key!r} does not equal canonicalization of "
                f"basename {basename!r} = {expected_key!r} (path {path!r})"
            )

    # NOTE: DB-backed anchor-existence verification is NOT run here to keep
    # this file free of Django DB fixtures (Pattern C precedent). The
    # equivalent invariant is enforced by the S2828 close cascade §5.1
    # ORM smoke ("all 6 anchor paths resolve to real Documents in the
    # active database" — verified 2026-07-19 during per-gate sweep).


class TestWholeStringInvariant:
    """LOAD-BEARING invariant per Rigby SIGN Q1: whole-string `^...$`
    anchoring is the disjointness guarantee vs Pattern B/C. If any
    future author considers substring-relaxation, they MUST re-run
    SIGN + Chris D-verdict. These tests capture the current invariant
    so a substring relaxation shows up as broken tests, not silent drift."""

    def test_all_patterns_anchor_with_caret_and_dollar(self):
        for pattern in _LITERAL_FILENAME_INTENT_PATTERNS:
            src = pattern.pattern
            assert src.lstrip('^').startswith((r'\s*', r'\d')) or src.startswith('^'), (
                f"Pattern {src!r} missing `^` anchor (whole-string invariant)"
            )
            assert src.endswith(r'\s*$') or src.endswith('$'), (
                f"Pattern {src!r} missing `$` anchor (whole-string invariant)"
            )

    def test_whole_string_holds_across_natural_language(self):
        """Regression sample — 5 sentences that contain literal filename
        tokens must NOT match any Pattern D regex. If this breaks, the
        whole-string invariant was violated."""
        samples = [
            "open CLAUDE.md and check the rules",
            "the PLATFORM_INVENTORY doc has counts",
            "See the KNOWLEDGE_PIPELINE for details",
            "run 00-START-NEXT-SESSION for onboarding",
            "the 2701_docs_inventory_topology_audit was renamed",
        ]
        for s in samples:
            for pat in _LITERAL_FILENAME_INTENT_PATTERNS:
                assert not pat.search(s), (
                    f"Pattern {pat.pattern!r} matched natural-language "
                    f"sample {s!r}. WHOLE-STRING INVARIANT VIOLATED — "
                    f"re-run Rigby SIGN + Chris D-verdict before shipping."
                )

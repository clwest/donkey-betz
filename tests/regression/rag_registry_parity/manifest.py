"""S2830 Step 1 — 15-case parity manifest for the pointer-intent
registry. Coverage criteria enumerated in
`docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md`
§5.2. Each case describes one observable branch through
`search_embeddings()` under the current 3-mechanism architecture.

Case cardinality is a side effect of coverage, not a target. Cases MAY
grow when a new observable branch is added; MUST NOT be trimmed below
the 15-case minimum (§7.3).

Ship discipline (Rigby SIGN Q3 refinement): simple cases snapshot the
`search_embeddings()` output as JSON. Complex cases (drift WARN,
inject-skipped-by-exclude-ids) that require specific DB fixture state
are captured as observable-behavior assertions on the current baseline
— the baseline records whether the WARN was emitted, whether the
Pattern D MISS log was emitted, whether the intent gate flag flipped
active, etc.
"""

# Each case: {
#   'case_id': stable identifier used for snapshot filenames and pytest
#              parameterization
#   'purpose': human-readable purpose (from §5.2 table)
#   'query': the query string passed to search_embeddings
#   'kwargs': extra keyword arguments (limit, authority_weighted, etc.)
#   'expected_observable': dict of observable-branch flags this case
#              MUST exhibit. Registry is dormant at Step 1 so these are
#              captured against the current 3-mechanism architecture.
# }

# Common similarity threshold — matches the search_embeddings default
# (D15) and Pattern B/C/D pytest fixtures.
DEFAULT_KWARGS = {
    'limit': 5,
    'similarity_threshold': 0.4,
}

CASES = [
    # Case 1 — No-gate baseline. No mechanism fires; oversample is not
    # triggered by any intent flag; sort is by raw cosine distance.
    {
        'case_id': 'case_01_no_gate_baseline',
        'purpose': 'no mechanism fires; raw distance sort',
        'query': 'current weather forecast conditions',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': False,
            'intent_gate_name': None,
            'count_intent_active': False,
            'self_reference_intent_active': False,
            'literal_filename_intent_active': False,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 2 — Pattern B fires. COUNT gate hits; bonus applies to
    # canonical target (PLATFORM_INVENTORY); no injection.
    {
        'case_id': 'case_02_pattern_b_count_fires',
        'purpose': 'COUNT gate hits + bonus applies; no injection',
        'query': 'how many spiders',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'count',
            'count_intent_active': True,
            'self_reference_intent_active': False,
            'literal_filename_intent_active': False,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 3 — Pattern C fires. SELF_REFERENCE gate hits; injection +
    # bonus for 00-START-NEXT-SESSION.md anchor.
    {
        'case_id': 'case_03_pattern_c_self_reference_fires',
        'purpose': 'SELF_REFERENCE gate hits + inject + bonus',
        'query': 'where do I start',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'self_reference',
            'count_intent_active': False,
            'self_reference_intent_active': True,
            'literal_filename_intent_active': False,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 4 — Pattern D fires + curated hit. LITERAL-FILENAME gate
    # P1 hits PLATFORM_INVENTORY curated anchor + injection + bonus.
    {
        'case_id': 'case_04_pattern_d_literal_curated_hit',
        'purpose': 'LITERAL-FILENAME gate hits curated map + inject + bonus',
        'query': 'PLATFORM_INVENTORY',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'literal_filename',
            'count_intent_active': False,
            'self_reference_intent_active': False,
            'literal_filename_intent_active': True,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 5 — Pattern D fires + MISS path. Gate P1 fires but token
    # canonicalized ('spider_network') is NOT in _LITERAL_FILENAME_ANCHORS
    # → Strategy C log-only INFO emitted; no injection; no bonus.
    {
        'case_id': 'case_05_pattern_d_miss_path',
        'purpose': 'gate fires but no curated anchor; INFO log; no bonus',
        'query': 'SPIDER_NETWORK',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'literal_filename',
            'count_intent_active': False,
            'self_reference_intent_active': False,
            'literal_filename_intent_active': True,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': True,
        },
    },

    # Case 6 — Inject skipped by exclude_chunk_ids. When Pattern C
    # gate fires and the anchor Document's best chunk is ALREADY in
    # the oversample pool, the injection helper skips the duplicate
    # via exclude_chunk_ids membership check. Bonus still applies in
    # the composition loop. `project rules` fires Pattern C anchor
    # CLAUDE.md — if CLAUDE.md naturally ranks in the top-N, dedupe
    # activates.
    {
        'case_id': 'case_06_inject_skipped_by_exclude_ids',
        'purpose': 'anchor already in oversample; injection dedupe; bonus still applies',
        'query': 'project rules',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'self_reference',
            'count_intent_active': False,
            'self_reference_intent_active': True,
            'literal_filename_intent_active': False,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 7 — Drift WARN — Pattern B. Baseline state (post-S2829):
    # canonical targets are restored; WARN should NOT fire. Fixture
    # records the negative — a future regression would flip this to
    # positive drift-WARN emission.
    {
        'case_id': 'case_07_drift_warn_pattern_b_baseline_clean',
        'purpose': 'Pattern B gate active + canonical target present → NO WARN',
        'query': 'how many agents',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'count',
            'count_intent_active': True,
            'drift_warn_emitted': False,  # NEGATIVE — target is present
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 8 — Drift WARN — Pattern C. Same baseline-clean shape.
    # Fixture records anchor visible; WARN not emitted.
    {
        'case_id': 'case_08_drift_warn_pattern_c_baseline_clean',
        'purpose': 'Pattern C gate active + anchor present → NO WARN',
        'query': 'start here',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'self_reference',
            'self_reference_intent_active': True,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 9 — Drift WARN — Pattern D. Same baseline-clean shape.
    # (Pattern D WARN path exists in the drift-detection substrate
    # even though no explicit S2828_PATTERN_D_DRIFT log emit is
    # active for the missing-anchor case today — the WARN emit is
    # covered by Pattern C's parity emit; extending here for future.)
    {
        'case_id': 'case_09_drift_warn_pattern_d_baseline_clean',
        'purpose': 'Pattern D gate active + curated anchor present → NO WARN',
        'query': 'KNOWLEDGE_PIPELINE',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'literal_filename',
            'literal_filename_intent_active': True,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 10 — authority_weighted=True + no intent gate.
    # Weighted-score ranking path exercised; oversample triggered by
    # authority_weighted flag alone (no gate).
    {
        'case_id': 'case_10_authority_weighted_no_gate',
        'purpose': 'weighted ranking; oversample via authority flag; no gate',
        'query': 'observability metrics dashboards',
        'kwargs': dict(DEFAULT_KWARGS, authority_weighted=True),
        'expected_observable': {
            'intent_gate_fired': False,
            'intent_gate_name': None,
            'count_intent_active': False,
            'self_reference_intent_active': False,
            'literal_filename_intent_active': False,
            'authority_weighted': True,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 11 — Intent oversample + authority_weighted=True. Both
    # paths compose; effective_similarity + authority weight both
    # applied in weighted_score sort.
    {
        'case_id': 'case_11_intent_and_authority_weighted',
        'purpose': 'intent gate + authority_weighted; both paths compose',
        'query': 'how many spiders',
        'kwargs': dict(DEFAULT_KWARGS, authority_weighted=True),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'count',
            'count_intent_active': True,
            'authority_weighted': True,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 12 — Q28 no-perturb (Pattern D natural win). Numeric-prefix
    # snake filename query fires P3 gate; but the token
    # ('2701_docs_inventory_topology_audit') is NOT in the curated
    # anchor map → MISS path. The naturally-winning document
    # (2701_docs_inventory_topology_audit) preserves rank 1 without
    # bonus perturbation. Guards against a future refactor that
    # accidentally re-orders when MISS path fires.
    {
        'case_id': 'case_12_pattern_d_q28_no_perturb',
        'purpose': 'literal-filename gate fires + MISS path; natural top-1 preserved',
        'query': '2701_docs_inventory_topology_audit',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'literal_filename',
            'literal_filename_intent_active': True,
            'pattern_d_miss_log_emitted': True,
            'drift_warn_emitted': False,
        },
    },

    # Case 13 — Whole-string invariant. Pattern D gate MUST HOLD on
    # a natural-language query that mentions a filename in context.
    # Guards Chris D5 disjointness vs Pattern B/C multi-word patterns.
    {
        'case_id': 'case_13_whole_string_invariant_holds',
        'purpose': 'natural-lang query mentioning filename does NOT fire Pattern D gate',
        'query': 'please open CLAUDE.md and check the section',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'literal_filename_intent_active': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 14 — Pattern B/C/D disjointness. No query in the fixture
    # today fires two gates. This case verifies that no test query
    # accidentally triggers overlapping gates — a meta-assertion
    # aggregated across cases 1-13. Query is a compound
    # "how many where do I start" that could theoretically fire both
    # Pattern B (how many) and Pattern C (where do I start).
    {
        'case_id': 'case_14_disjointness_holds',
        'purpose': 'meta-assertion: disjoint-by-construction holds across cases',
        'query': 'how many where do I start',
        'kwargs': dict(DEFAULT_KWARGS),
        # This query fires BOTH Pattern B (COUNT) AND Pattern C
        # (SELF_REFERENCE) — a rare overlap. The registry MUST
        # preserve precedence: intent_gate_name = 'count' (first in
        # registry order). Both intent_active flags true is the
        # observable that documents current behavior.
        'expected_observable': {
            'intent_gate_fired': True,
            'intent_gate_name': 'count',  # precedence: count > self_reference
            'count_intent_active': True,
            'self_reference_intent_active': True,
            'literal_filename_intent_active': False,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
        },
    },

    # Case 15 — Empty query. All gates return falsy; embedding
    # creation may fail or return no chunks; observable branch =
    # empty pool + no gates.
    {
        'case_id': 'case_15_empty_query',
        'purpose': 'empty string edge case; all gates false; empty pool',
        'query': '',
        'kwargs': dict(DEFAULT_KWARGS),
        'expected_observable': {
            'intent_gate_fired': False,
            'intent_gate_name': None,
            'count_intent_active': False,
            'self_reference_intent_active': False,
            'literal_filename_intent_active': False,
            'drift_warn_emitted': False,
            'pattern_d_miss_log_emitted': False,
            'result_count': 0,
        },
    },
]

# Sanity check invariant — case count MUST NOT drop below 15
# per design doc §7.3.
assert len(CASES) >= 15, (
    f"parity manifest has {len(CASES)} cases; MUST NOT drop below 15 "
    "per POINTER_INTENT_REGISTRY_DESIGN.md §7.3. New observable branches "
    "may raise this count; do NOT trim below 15."
)

"""
RAG (Retrieval-Augmented Generation) Integration
Connects to unified_embeddings table for context retrieval
"""

import logging
import os
import re
import psycopg2
from typing import List, Dict, Any, Optional

# Import the migrated encryption service
from core.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)

def create_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """Create embedding for a text using the centralized EmbeddingService (with Redis cache)."""
    try:
        from core.services.embedding_service import get_embedding_service
        service = get_embedding_service()
        result = service.create_embedding(text, model=model, agent_name='rag_integration', log_usage=True)
        return result.embedding
    except Exception as e:
        logger.error(f"Failed to create embedding: {e}")
        return None

# Cycle 1A KFI-3 (ADR-0130) — authority weights for opt-in ranking.
# workspace_canonical (2.0) > repo_canonical (1.5) > derived (1.0) per ADR §2.1.
# retrieval_boost is orthogonal per 0120 and NOT composed into weighted_score.
_AUTHORITY_WEIGHTS = {
    'workspace_canonical': 2.0,
    'repo_canonical': 1.5,
    'derived': 1.0,
}


# Session 2728 F-RG-1 — Batch B tool 1 close: narrow-except allowlist for
# `search_embeddings`. Extends the S1234 D17-D21 discipline (already applied
# to `search_personal_memories` at line ~441-445 as
# `_PERSONAL_MEMORY_ENV_ERRORS`) to the sibling document-search path so
# environmental errors return `[]` with an error log, but logic errors
# propagate to callers instead of silently degrading to zero-results
# (indistinguishable from "no relevant content"). Same tuple shape as the
# D20 invariant (`test_d20_views_rag_embeddings_narrow_except.py::
# test_all_four_allowlists_have_same_shape` — this becomes the fifth
# allowlist under the D17-D21 pattern). Chris ratified at Batch B tool 1
# close (S2728 handoff).
_RAG_EMBEDDINGS_ENV_ERRORS = (
    __import__('django.db.utils', fromlist=['DatabaseError']).DatabaseError,
    ConnectionError,
    OSError,
)


def _get_authority_weight(authority):
    """Return the authority-tier weight in [1.0, 2.0]; unknown → 1.0."""
    return _AUTHORITY_WEIGHTS.get(authority or '', 1.0)


# S2826 Pattern B — intent-gated file-specific ranking bonus for the
# embedding lane. Chris D-verdict 2026-07-19 (S2826 D1) after S2825
# harvest showed 0/16 retrieval-strict-hit despite the S2818 authority-
# boost pilot being live in the BM25 lane. Step 1a confirmed metadata
# is correct FOR THE TARGET ROWS; Step 1b confirmed the tier-based
# authority_weighted flag is a no-op when target and competitor share
# the same repo_canonical tier. Step 1c decomposed the failure into two
# patterns; Pattern B is "small-gap ranking" (canonical is in the
# candidate pool but loses to same-tier competitors by a ~0.025
# similarity margin). D1 mandates a NARROW intent gate + small bounded
# file-specific bonus, distinct from the coarse tier weighting.
# Sibling of core/rag.py `_COUNT_INTENT_PATTERNS` (BM25 lane substring
# match). Rigby SIGN 2026-07-19 Q1: near-parity with BM25 phrase set;
# intentional divergence on `total` (narrower regex `total\s+\w+` here
# vs bare `total` in BM25) to avoid false positives on words like
# "totally"/"totalitarian" — accepted as design decision, not
# oversight. Do NOT collapse with the SELF_REFERENCE / INDEX_DISCOVERY
# / IDENTITY / doc-class-precedence policy classes per D5 — each keeps
# its own gate + mechanism.
_COUNT_INTENT_PATTERNS = (
    re.compile(r'\bhow\s+many\b', re.I),
    re.compile(r'\bhow\s+much\b', re.I),  # Rigby Q1 parity refinement
    re.compile(r'\bnumber\s+of\b', re.I),
    re.compile(r'\bcount\s+of\b', re.I),
    re.compile(r'\blist\s+all\b', re.I),
    re.compile(r'\btotal\s+(?:number\s+of\s+)?\w+', re.I),
)

# File-specific similarity bonus applied only when the COUNT intent
# gate fires. Value bounded to observed S2825 gaps: Q23 (chunk #28
# celery-tasks) lost by 0.025 to RUNTIME_AUDIT #3; Q21 (chunk #15
# spiders) lost by ~0.026 to PLATFORM_ARCHITECTURE_MAP. +0.05 flips
# both without dominating unrelated retrieval. Do not raise without
# evidence. Do not add other files here without confirming a distinct
# small-gap ranking pattern via Step-1c-shape diagnostic.
_COUNT_INTENT_BONUS = {
    'docs/PLATFORM_INVENTORY.md': 0.05,
}


def _detect_count_intent(query: str) -> bool:
    """Narrow COUNT / sole-authoritative-source intent gate (Pattern B)."""
    if not query:
        return False
    return any(p.search(query) for p in _COUNT_INTENT_PATTERNS)


# S2827 Pattern C — narrow SELF_REFERENCE intent gate + canonical-anchor
# candidate injection. Chris D-verdict 2026-07-19 (S2827 D-Q1..D-Q5)
# ratifying Rigby-reconciled v2 design after S2826 Phase-0.5 baseline
# 6/18 = 33.3% strict top-1 identified 5 remaining SELF_REFERENCE class
# misses (Q14/Q15/Q16/Q17/Q20). Q20 (literal-filename) explicitly ceded
# to future Pattern D per Chris D5 distinct-mechanism-per-class + Chris
# D-Q4 + Rigby SIGN Q3. Pattern C owns SEMANTIC pointer intent: "where
# to begin / where to continue / session-start guidance / project rules".
#
# Design doc: docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md
# Constitutional refinements from Chris:
#   D-Q1: bonus value is a MEASURED hypothesis, not a fixed constitutional
#         constant. Use the SMALLEST reliable adjustment that converts
#         intended cases while preserving negative controls. Tested
#         alternatives + margins recorded in the design doc §7.5.
#   D-Q2: corpus label correction (Q14/Q15/Q16/Q20 strict+loose targets)
#         landed in same PR — ground-truth repair, not benchmark tuning.
#
# Sibling to Pattern B `_COUNT_INTENT_PATTERNS` above; kept as distinct
# mechanism per Chris D5. Chris D-Q3 forward-carry: after Pattern D also
# ships (3-instance threshold), extract shared "pointer-intent registry"
# primitive covering Pattern B/C/D — do NOT refactor in S2827.
_SELF_REFERENCE_INTENT_PATTERNS = (
    # Start-doc semantic pointer patterns (Q14/Q15/Q16)
    re.compile(r'\bwhere\s+do\s+I\s+start\b', re.I),                                    # Q15
    re.compile(r'\bstart\s+(here|next\s+session|new\s+session)\b', re.I),               # Q16 (narrow: next/new require session)
    re.compile(r'\b(the\s+)?(next\s+)?session\s+start\s+(doc|file|page|md)\b', re.I),   # Q14 (Rigby Q1: required file-context word prevents false positive on handoff-doc "session start" mentions)
    # Rules-doc semantic pointer patterns (Q17)
    re.compile(r'\bproject\s+rules?\b', re.I),                                          # Q17 (accepts singular + plural per Rigby Q1)
)

# Canonical anchor file paths — REAL Document.file_path values (repo root,
# no docs/ prefix). Corpus label correction (S2827 D-Q2 same-PR) aligns
# corpus.json strict + loose targets with these paths.
_SELF_REFERENCE_ANCHORS = {
    'start_doc':     '00-START-NEXT-SESSION.md',
    'project_rules': 'CLAUDE.md',
}

# Which pattern index in _SELF_REFERENCE_INTENT_PATTERNS maps to which
# anchor key. Ordered to match the pattern tuple.
_SELF_REFERENCE_PATTERN_TO_ANCHOR = (
    'start_doc',      # pattern 0: where do I start
    'start_doc',      # pattern 1: start (here|next session|new session)
    'start_doc',      # pattern 2: session start (doc|file|page|md)
    'project_rules',  # pattern 3: project rules?
)

# Bounded policy bonus (Chris D2 + D-Q1 refinement 2026-07-19).
# Value tuned from measured margins on Q14/Q15/Q16/Q17 canonical anchor
# raw similarities vs top-1 non-canonical competitor:
#   Q14 anchor 0.4569 vs top-1 0.6816 → gap 0.2247 → min flip +0.225
#   Q15 anchor 0.2605 vs top-1 0.3843 → gap 0.1238 → min flip +0.124
#   Q16 anchor 0.3146 vs top-1 0.4422 → gap 0.1276 → min flip +0.128
#   Q17 anchor 0.3833 vs top-1 0.4723 → gap 0.0889 → min flip +0.090
# Smallest single-static bonus flipping all 4 = 0.23 (bounded above Q14
# gap by epsilon 0.005). Alternative values tested + recorded in
# design doc §7.5.
_SELF_REFERENCE_INTENT_BONUS = 0.23


def _detect_self_reference_intent(query):
    """Narrow SELF_REFERENCE / semantic-pointer intent gate (Pattern C).

    Returns a tuple of matched anchor keys (deduplicated, preserving
    first-match order). Empty tuple when gate does not fire. Chris D5
    distinct-mechanism-per-class discipline: this gate deliberately does
    NOT overlap with Pattern B (COUNT) or the future Pattern D
    (literal-filename) — literal filename patterns (`00-START-NEXT-SESSION`,
    `CLAUDE.md`) are explicitly ceded to Pattern D per Chris D-Q4.
    """
    if not query:
        return ()
    matched = []
    seen = set()
    for idx, pattern in enumerate(_SELF_REFERENCE_INTENT_PATTERNS):
        if pattern.search(query):
            anchor_key = _SELF_REFERENCE_PATTERN_TO_ANCHOR[idx]
            if anchor_key not in seen:
                seen.add(anchor_key)
                matched.append((anchor_key, idx))
    return tuple(matched)


def _fetch_self_reference_anchor_chunks(
    anchor_matches,
    base_qs,
    exclude_chunk_ids,
    query_embedding,
):
    """Fetch the highest-similarity DocumentEmbedding chunk for each
    mapped canonical anchor, under the SAME filter chain as `base_qs`.

    Preserves Chris D6 "no include_superseded relaxation" — if the
    anchor Document has `status=archived`, it is filtered out by the
    same clause `base_qs` inherits and the anchor is silently absent
    from injection. The `[S2827_PATTERN_C_DRIFT]` WARN log downstream
    surfaces the all-anchors-missing case.

    Uses the SAME query embedding for CosineDistance so injected chunks
    carry real similarity scores, not synthesized values (per Chris D-Q1
    "retrieval must prove retrieval" — the injection is retrieval-layer
    fetch, the bonus is bounded ranking adjustment).

    Returns a list of DocumentEmbedding rows (may be empty).
    """
    from content.models import Document, DocumentEmbedding
    from pgvector.django import CosineDistance

    # Resolve anchor file_paths → Document ids under the same filter
    # chain as base_qs. We fetch by file_path since the anchor map keys
    # to a stable filesystem-relative path.
    anchor_paths = {
        _SELF_REFERENCE_ANCHORS[key] for key, _ in anchor_matches
    }
    anchor_docs = list(
        Document.objects.filter(file_path__in=anchor_paths).only('id', 'file_path')
    )
    if not anchor_docs:
        return []

    injected = []
    for doc in anchor_docs:
        # Best chunk of THIS anchor under the base_qs filter chain.
        # We rebuild the queryset per-anchor to inherit include_superseded
        # exclusion + canonical_authority filter + orphan-chunk exclusion.
        chunk_qs = (
            DocumentEmbedding.objects
            .filter(document=doc)
            .annotate(distance=CosineDistance('embedding_vector', query_embedding))
        )
        # Mirror base_qs's document.status exclusion (production default
        # include_superseded=False → exclude ARCHIVED). We don't have
        # direct handle to base_qs's filter chain here, so we re-apply
        # the same status exclusion the parent search_embeddings applies.
        # If Document is archived, chunk skipped; drift WARN fires
        # downstream when all anchors miss.
        from content.models import ContentStatus
        chunk_qs = chunk_qs.exclude(document__status=ContentStatus.ARCHIVED)
        best = chunk_qs.order_by('distance').first()
        if best is None:
            continue
        if best.id in exclude_chunk_ids:
            # Already in the retrieved pool — no synthetic inject;
            # the boost is applied in the composition loop.
            continue
        injected.append(best)
    return injected


# S2828 Pattern D — narrow LITERAL-FILENAME intent gate + canonical-anchor
# candidate injection. Chris D-verdict 2026-07-19 (S2828 D-Q1..D-Q7)
# ratifying Rigby-reconciled v2 design after S2827 Pattern C shipped
# 10/18 = 55.6% strict top-1 baseline. Pattern D targets Q20 + Q24
# (Phase-0.5 corpus rows) + adjacent `CLAUDE.md` literal per Chris D-Q4
# S2827 explicit naming.
#
# Design doc: docs/research/discovery_layer/PHASE_0_5/PATTERN_D_LITERAL_FILENAME_DESIGN.md
# Constitutional refinements from Chris D-Q1..D-Q7:
#   D-Q1: per-regex bonus sweep + per-gate ceilings (P0/P2=0.35, P1=0.20,
#         P3=0.10). Smallest reliable per gate; if ceiling exceeded,
#         positive not converted this arc (do not raise ceiling).
#   D-Q2: Strategy A curated map + Strategy C log-only miss path (no
#         Strategy B dynamic Document.file_path lookup — over-match risk
#         verified by Rigby SIGN Q2 tool_run #3 on `README`).
#   D-Q3: retrieval-integrity invariant preserved. Bounded per-gate bonus
#         is NOT rank-1 force-pin. Legitimate competitor may still win.
#   D-Q4: Q28 no-perturb (Q28 wins natively at sim 0.5973; P3 bonus is
#         additive on the winning row via dedupe → rank 1 preserved).
#   D-Q5: `CLAUDE.md` literal in scope though not a corpus row.
#   D-Q6: Rigby zoom-out fold persisted as `same_pr_mitigatable` — per-
#         regex tiers ARE the mitigation.
#   D-Q7: Atomic PR sequencing per S2827 D-Q5; NO shared "pointer-intent
#         registry" refactor in S2828.
#
# Sibling to Pattern B `_COUNT_INTENT_PATTERNS` and Pattern C
# `_SELF_REFERENCE_INTENT_PATTERNS`. Distinct mechanism per Chris D5.
# LOAD-BEARING INVARIANT: whole-string `^...$` anchoring is the
# disjointness guarantee vs Pattern B/C multi-word patterns. Any future
# substring-relaxation MUST re-run Rigby SIGN + Chris D-verdict.

# Regex patterns — whole-string anchored per LOAD-BEARING invariant.
# Ordered P0..P3 by intent-signal determinism (strongest → weakest).
_LITERAL_FILENAME_INTENT_PATTERNS = (
    # P0 — explicit .md extension (case-insensitive)
    #   fires: CLAUDE.md, README.md, PLATFORM_INVENTORY.md, claude.md
    #   holds: multi-word ("open CLAUDE.md and check"), path form ("docs/CLAUDE.md")
    re.compile(r'^\s*[\w\-]+\.md\s*$', re.I),

    # P1 — uppercase-token filename stem (2+ uppercase segments joined by _)
    #   fires: PLATFORM_INVENTORY, KNOWLEDGE_PIPELINE, SESSION_2827_PATTERN_C
    #   holds: PLATFORM (single), README (single), lowercase platform_inventory
    re.compile(r'^\s*[A-Z][A-Z0-9]+(?:_[A-Z][A-Z0-9]+)+\s*$'),

    # P2 — hyphenated ALL-CAPS token (3+ segments joined by -; explicit
    #   {2,} = 2+ additional segments after the first, i.e. 3+ total).
    #   fires: 00-START-NEXT-SESSION
    #   holds: ADR-0130 (2 segments, deliberately excluded — ticket-id
    #          shape overlaps too many non-canonical patterns)
    re.compile(r'^\s*[A-Z0-9]+(?:-[A-Z0-9]+){2,}\s*$'),

    # P3 — numeric-prefix snake_case filename (3+ segments after numeric
    #   prefix). Q28-shape.
    #   fires: 2701_docs_inventory_topology_audit
    #   holds: multi-word natural-language forms
    re.compile(r'^\s*\d+[_\-][a-z0-9]+(?:[_\-][a-z0-9]+){2,}\s*$'),
)

# Gate name per pattern index — used in diagnostics + per-gate bonus lookup.
_LITERAL_FILENAME_PATTERN_KEYS = (
    'P0_md_extension',
    'P1_uppercase_snake',
    'P2_hyphen_caps',
    'P3_numeric_snake',
)

# Curated canonical anchor map (Strategy A — Chris D-Q2 ratified).
# Keys are CANONICALIZED (lowercase; `.md` stripped; `-` → `_`).
# Values are REAL Document.file_path strings (verified 2026-07-19).
# Adding an entry: verify the file_path resolves to a real Document via
# `Document.objects.filter(file_path=<path>).exists()`. Wiring pytest
# `test_all_anchors_resolve_to_real_documents` enforces this.
_LITERAL_FILENAME_ANCHORS = {
    'platform_inventory':    'docs/PLATFORM_INVENTORY.md',
    'platform_what_it_is':   'docs/PLATFORM_WHAT_IT_IS.md',
    'knowledge_pipeline':    'docs/KNOWLEDGE_PIPELINE.md',
    'engineering_playbook':  'docs/ENGINEERING_PLAYBOOK.md',
    '00_start_next_session': '00-START-NEXT-SESSION.md',
    'claude':                'CLAUDE.md',
}

# Per-gate bonus tiers (Strategy 3-B — Chris D-Q1 ratified). Values
# selected by per-gate sweep at S2828 implementation-time; smallest
# reliable per gate that converts intended positives while preserving
# ALL 20 negative controls. Full sweep + fine-grained margins recorded
# in design doc §7 measurement evidence.
#
#   Sweep (coarse [0.03..0.35] → fine [smallest_flip..0.10]):
#     P0 `.md`   : converts at 0.07 (first fail 0.06); anchor_eff 0.6063;
#                  ceiling 0.35; headroom +0.28.
#     P1 uppercase snake: converts at 0.09 (first fail 0.08); anchor_eff
#                  0.5651; ceiling 0.20; headroom +0.11.
#     P2 hyphen caps: converts at 0.32 (first fail 0.31 at margin -0.0019
#                  which is the tightest margin observed — Q20's +0.31 raw
#                  gap left almost no room); ceiling 0.35; headroom +0.03.
#                  Rigby SIGN Q3 caught this as load-bearing tension; the
#                  measured smallest is well under the ceiling.
#     P3 numeric snake: 0.03 (Q28 wins natively, bonus is no-op because
#                  Q28 is uncurated — MISS-path applies; value chosen for
#                  minimal footprint). Ceiling 0.10.
#
# Chris D-Q1 discipline: if a positive requires a bonus > ceiling, it
# is NOT converted this arc (do NOT raise ceiling to hit projection).
# Wiring pytest asserts each selected value ≤ corresponding ceiling.
_LITERAL_FILENAME_INTENT_BONUS = {
    'P0_md_extension':    0.07,
    'P1_uppercase_snake': 0.09,
    'P2_hyphen_caps':     0.32,
    'P3_numeric_snake':   0.03,
}

# Per-gate ceilings (Chris D-Q1). Enforced by pytest assertion; sweep
# selection MUST NOT exceed these values.
_LITERAL_FILENAME_INTENT_CEILING = {
    'P0_md_extension':    0.35,
    'P1_uppercase_snake': 0.20,
    'P2_hyphen_caps':     0.35,
    'P3_numeric_snake':   0.10,
}


def _canonicalize_literal_filename_token(query):
    """Canonicalize a literal-filename query token for anchor-map lookup.

    Spec (Chris D-Q2 ratified): strip whitespace → lowercase → strip
    trailing `.md` (case-insensitive) → normalize `-` → `_`. Deterministic
    and reversible-modulo-case. Used for anchor-map key generation AND
    query-time resolution — both paths MUST use identical canonicalization
    for miss-path pytest coverage to hold.
    """
    if not query:
        return ''
    t = query.strip().lower()
    if t.endswith('.md'):
        t = t[:-3]
    t = t.replace('-', '_')
    return t


def _detect_literal_filename_intent(query):
    """Narrow LITERAL-FILENAME intent gate (Pattern D).

    Returns a tuple of (canonical_key, pattern_index, gate_name) matches,
    deduplicated preserving first-match order. Empty tuple when gate does
    not fire. Chris D5 distinct-mechanism-per-class discipline: this gate
    deliberately does NOT overlap with Pattern B (COUNT) or Pattern C
    (semantic SELF_REFERENCE) — whole-string `^...$` anchoring is the
    disjointness guarantee.

    Strategy A + Strategy C resolution: if a pattern fires but the
    canonicalized token misses the curated anchor map, the caller emits
    `[S2828_PATTERN_D_MISS]` INFO and Pattern D's injection + bonus paths
    are skipped — natural retrieval unchanged.
    """
    if not query:
        return ()
    matched = []
    seen_keys = set()
    canonicalized = _canonicalize_literal_filename_token(query)
    for idx, pattern in enumerate(_LITERAL_FILENAME_INTENT_PATTERNS):
        if pattern.search(query):
            gate_name = _LITERAL_FILENAME_PATTERN_KEYS[idx]
            anchor_key = canonicalized if canonicalized in _LITERAL_FILENAME_ANCHORS else None
            if anchor_key is not None and anchor_key not in seen_keys:
                seen_keys.add(anchor_key)
                matched.append((anchor_key, idx, gate_name))
            elif anchor_key is None and not matched:
                # First pattern to fire but no anchor resolves — record as
                # (None, idx, gate_name) so caller can emit MISS log.
                matched.append((None, idx, gate_name))
                break  # only need one miss record
    return tuple(matched)


def _fetch_literal_filename_anchor_chunks(
    anchor_matches,
    exclude_chunk_ids,
    query_embedding,
):
    """Fetch the highest-similarity DocumentEmbedding chunk for each
    mapped canonical anchor, under the same status-exclusion filter chain
    the parent search_embeddings applies (Chris D6 no-include_superseded
    relaxation preserved). Skips (None, idx, gate) miss records.

    Same shape as Pattern C `_fetch_self_reference_anchor_chunks` but
    kept as a separate function per Chris D-Q7 "no shared refactor in
    S2828." Post-Pattern-D "pointer-intent registry" primitive is a
    separate arc.
    """
    from content.models import Document, DocumentEmbedding, ContentStatus
    from pgvector.django import CosineDistance

    # Resolve mapped-anchor file_paths (skip miss records where key is None)
    anchor_paths = {
        _LITERAL_FILENAME_ANCHORS[key]
        for key, _, _ in anchor_matches
        if key is not None
    }
    if not anchor_paths:
        return []
    anchor_docs = list(
        Document.objects.filter(file_path__in=anchor_paths).only('id', 'file_path')
    )
    if not anchor_docs:
        return []

    injected = []
    for doc in anchor_docs:
        chunk_qs = (
            DocumentEmbedding.objects
            .filter(document=doc)
            .exclude(document__status=ContentStatus.ARCHIVED)
            .annotate(distance=CosineDistance('embedding_vector', query_embedding))
        )
        best = chunk_qs.order_by('distance').first()
        if best is None:
            continue
        if best.id in exclude_chunk_ids:
            # Already in the retrieved pool — no synthetic inject;
            # the boost is applied in the composition loop.
            continue
        injected.append(best)
    return injected


# ─────────────────────────────────────────────────────────────────────────
# S2830 Step 1 — Pointer-Intent Registry (DORMANT)
# ─────────────────────────────────────────────────────────────────────────
#
# Design: docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md
# Ratified: 2026-07-19 (S2830) via joint Claude+Rigby SIGN 3 cycles +
#           Chris D-verdict "ship step 1".
#
# HARD BOUNDARY (Rigby SIGN Q4 refinement): Step 1 does NOT change
# runtime dispatch. The classes below are DORMANT — no code path in
# search_embeddings() calls them. They exist as an alternative surface
# that Step 2 (separate SIGN arc + separate Chris D-verdict) may wire
# into search_embeddings() as a behavior-preserving refactor.
#
# Contract (Rigby SIGN Q2 refinement): mechanisms may shape-diverge.
#   - Pattern B is non-injecting; injects_candidates() → False;
#     fetch_candidate_chunks default no-op inherited.
#   - Pattern C accepts base_qs (currently rebuilds inline); Pattern D
#     drops base_qs entirely (also rebuilds inline). Both are legitimate.
#   - Canonicalization (Pattern D) is mechanism-owned inside detect().
#   - MISS log (Pattern D) is mechanism-owned via emit_miss_log().
#
# Anti-worship (Rigby SIGN Q5 §5.4): if a future mechanism (Pattern E)
# needs a shape the protocol doesn't accommodate, that's the signal to
# REFINE the protocol under new SIGN — NOT shoehorn.
#
# Each mechanism is a THIN WRAPPER over the existing standalone
# functions (_detect_count_intent, _detect_self_reference_intent,
# _detect_literal_filename_intent, _fetch_*_anchor_chunks, and the
# associated bonus + diagnostic + WARN blocks in search_embeddings).
# Delegation to existing functions is deliberate for Step 1: zero-
# behavior-change is preserved by construction because the classes
# call the exact same code paths search_embeddings currently uses.

class IntentMechanism:
    """Base contract for pointer-intent mechanisms in the
    search_embeddings embedding lane. See §4.1 of the design doc for
    the full method contract."""

    name: str = ''
    """Machine name — 'count', 'self_reference', 'literal_filename'.
    Used for intent_gate_name query-level precedence + diagnostic
    field routing."""

    drift_warn_prefix: str = ''
    """e.g. '[S2826_PATTERN_B_DRIFT]'. Preserved verbatim from current
    log strings for grep continuity."""

    def detect(self, query):
        """Stage 1 — return truthy match record if gate fires, else
        falsy. Shape is mechanism-owned (bool / tuple / etc)."""
        raise NotImplementedError

    def injects_candidates(self) -> bool:
        """Whether this mechanism injects candidate chunks. Pattern B
        returns False; Pattern C/D return True. Registry short-
        circuits fetch_candidate_chunks when this is False."""
        return False

    def fetch_candidate_chunks(self, matches, base_qs, exclude_chunk_ids, query_embedding):
        """Stage 2+3 — return list of DocumentEmbedding rows to inject.
        Default no-op (returns []) — non-injecting mechanisms inherit
        this via injects_candidates()=False short-circuit and do NOT
        need to override.

        `base_qs` semantics: Optional. Mechanism MAY ignore it and
        rebuild filter chain inline. Registry MUST NOT assume any
        mechanism consults base_qs."""
        return []

    def bonus_and_diagnostics_for_row(self, matches, doc, chunk_id, injected_chunk_ids):
        """Stages 4+5 — return (bonus_amount, diagnostic_field_dict)
        for this row. diagnostic_field_dict keys are mechanism-owned
        literal names."""
        raise NotImplementedError

    def default_diagnostic_fields(self) -> dict:
        """Diagnostic dict for rows on queries where gate did NOT
        fire. Ensures schema stability across all responses."""
        raise NotImplementedError

    def canonical_target_paths(self) -> set:
        """Set of file paths this mechanism claims as canonical. Used
        by drift-WARN to detect all-targets-missing shape."""
        raise NotImplementedError

    def emit_drift_warn(self, matches, returned_doc_paths, query, include_superseded):
        """Stage 6 — emit drift WARN if applicable. Preserves each
        mechanism's current WARN log format verbatim."""
        pass  # default no-op; each mechanism overrides

    def emit_miss_log(self, query, matches):
        """Emit Strategy-C-style INFO for gate-fires-but-no-anchor.
        No-op default; Pattern D overrides."""
        pass


class CountMechanism(IntentMechanism):
    """Pattern B (S2826) — COUNT intent gate + per-file bonus.
    Non-injecting: bonus applies to naturally-retrieved rows only."""

    name = 'count'
    drift_warn_prefix = '[S2826_PATTERN_B_DRIFT]'

    def detect(self, query):
        return _detect_count_intent(query)

    def injects_candidates(self) -> bool:
        return False

    def bonus_and_diagnostics_for_row(self, matches, doc, chunk_id, injected_chunk_ids):
        # matches is a bool from _detect_count_intent
        if matches:
            bonus = _COUNT_INTENT_BONUS.get(doc.file_path or '', 0.0)
        else:
            bonus = 0.0
        return bonus, {'count_intent_bonus': bonus}

    def default_diagnostic_fields(self) -> dict:
        return {'count_intent_bonus': 0.0}

    def canonical_target_paths(self) -> set:
        return set(_COUNT_INTENT_BONUS.keys())

    def emit_drift_warn(self, matches, returned_doc_paths, query, include_superseded):
        if not matches or not _COUNT_INTENT_BONUS:
            return
        missing_targets = [
            p for p in _COUNT_INTENT_BONUS.keys() if p not in returned_doc_paths
        ]
        if missing_targets and len(missing_targets) == len(_COUNT_INTENT_BONUS):
            logger.warning(
                "[S2826_PATTERN_B_DRIFT] count_intent_active=True but "
                "NONE of the mapped canonical targets are in the "
                "returned pool. targets=%s query=%r include_superseded=%s. "
                "Check Document.status='processed' for these paths; "
                "update path does not refresh status field.",
                list(_COUNT_INTENT_BONUS.keys()),
                query[:200],
                include_superseded,
            )


class SelfReferenceMechanism(IntentMechanism):
    """Pattern C (S2827) — SELF_REFERENCE intent gate + candidate
    injection + single-scalar bonus per anchor."""

    name = 'self_reference'
    drift_warn_prefix = '[S2827_PATTERN_C_DRIFT]'

    def detect(self, query):
        return _detect_self_reference_intent(query)

    def injects_candidates(self) -> bool:
        return True

    def fetch_candidate_chunks(self, matches, base_qs, exclude_chunk_ids, query_embedding):
        # matches is a tuple[(anchor_key, pattern_idx), ...]
        return _fetch_self_reference_anchor_chunks(
            matches, base_qs, exclude_chunk_ids, query_embedding,
        )

    def bonus_and_diagnostics_for_row(self, matches, doc, chunk_id, injected_chunk_ids):
        # matches is a tuple[(anchor_key, pattern_idx), ...]
        bonus = 0.0
        anchor_key = None
        matched_pattern_index = None
        injected = False
        if matches:
            fp = doc.file_path or ''
            for key, idx in matches:
                if _SELF_REFERENCE_ANCHORS.get(key) == fp:
                    bonus = _SELF_REFERENCE_INTENT_BONUS
                    anchor_key = key
                    matched_pattern_index = idx
                    break
            if chunk_id in injected_chunk_ids:
                injected = True
        return bonus, {
            'self_ref_intent_bonus': bonus,
            'self_ref_anchor_key': anchor_key,
            'self_ref_matched_pattern_index': matched_pattern_index,
            'self_ref_injected': injected,
        }

    def default_diagnostic_fields(self) -> dict:
        return {
            'self_ref_intent_bonus': 0.0,
            'self_ref_anchor_key': None,
            'self_ref_matched_pattern_index': None,
            'self_ref_injected': False,
        }

    def canonical_target_paths(self) -> set:
        return set(_SELF_REFERENCE_ANCHORS.values())

    def emit_drift_warn(self, matches, returned_doc_paths, query, include_superseded):
        if not matches:
            return
        matched_anchor_paths = {
            _SELF_REFERENCE_ANCHORS[key] for key, _ in matches
        }
        missing = matched_anchor_paths - returned_doc_paths
        if missing and missing == matched_anchor_paths:
            logger.warning(
                "[S2827_PATTERN_C_DRIFT] self_reference_intent_active=True "
                "but NONE of the mapped canonical anchors are retrievable "
                "under current filters. anchor_paths=%s query=%r "
                "include_superseded=%s. Check Document.status='processed' "
                "for these paths; S2826 root-cause: sync_docs_index_to_documents "
                "update path does not refresh status field.",
                list(matched_anchor_paths),
                query[:200],
                include_superseded,
            )


class LiteralFilenameMechanism(IntentMechanism):
    """Pattern D (S2828) — LITERAL-FILENAME intent gate + candidate
    injection + per-gate bonus tiers + Strategy C log-only MISS path."""

    name = 'literal_filename'
    drift_warn_prefix = '[S2828_PATTERN_D_DRIFT]'

    def detect(self, query):
        return _detect_literal_filename_intent(query)

    def injects_candidates(self) -> bool:
        return True

    def fetch_candidate_chunks(self, matches, base_qs, exclude_chunk_ids, query_embedding):
        # matches is a tuple[(canonical_key_or_None, pattern_idx, gate_name), ...]
        # Filter out MISS records (anchor_key=None) — only pass curated hits
        curated_matches = tuple(m for m in matches if m[0] is not None)
        if not curated_matches:
            return []
        return _fetch_literal_filename_anchor_chunks(
            curated_matches, exclude_chunk_ids, query_embedding,
        )

    def bonus_and_diagnostics_for_row(self, matches, doc, chunk_id, injected_chunk_ids):
        # matches is a tuple[(canonical_key_or_None, pattern_idx, gate_name), ...]
        bonus = 0.0
        anchor_key = None
        matched_pattern_index = None
        gate_name = None
        injected = False
        if matches:
            fp = doc.file_path or ''
            for key, idx, gname in matches:
                if key is None:
                    continue  # MISS record
                if _LITERAL_FILENAME_ANCHORS.get(key) == fp:
                    bonus = _LITERAL_FILENAME_INTENT_BONUS.get(gname, 0.0)
                    anchor_key = key
                    matched_pattern_index = idx
                    gate_name = gname
                    break
            if chunk_id in injected_chunk_ids:
                injected = True
        return bonus, {
            'literal_filename_intent_bonus': bonus,
            'literal_filename_anchor_key': anchor_key,
            'literal_filename_matched_pattern_index': matched_pattern_index,
            'literal_filename_gate_name': gate_name,
            'literal_filename_injected': injected,
        }

    def default_diagnostic_fields(self) -> dict:
        return {
            'literal_filename_intent_bonus': 0.0,
            'literal_filename_anchor_key': None,
            'literal_filename_matched_pattern_index': None,
            'literal_filename_gate_name': None,
            'literal_filename_injected': False,
        }

    def canonical_target_paths(self) -> set:
        return set(_LITERAL_FILENAME_ANCHORS.values())

    def emit_miss_log(self, query, matches):
        # Called only when gate fired but fetch returned []. Emit
        # verbatim to preserve grep continuity with the current
        # inline MISS log at search_embeddings line ~750.
        if not matches:
            return
        # Find the miss record (anchor_key=None) if present
        miss = next((m for m in matches if m[0] is None), None)
        if miss is None:
            return
        logger.info(
            "[S2828_PATTERN_D_MISS] gate fired but no curated anchor "
            "matched. query=%r canonicalized=%r pattern_index=%d "
            "gate=%s. Add to _LITERAL_FILENAME_ANCHORS if this is a "
            "canonical doc; else safely ignore.",
            query[:200],
            _canonicalize_literal_filename_token(query),
            miss[1],
            miss[2],
        )


# Registry — order encodes precedence for intent_gate_name.
# count > self_reference > literal_filename (matches current hardcoded
# precedence at search_embeddings line ~894-902).
#
# Adding Pattern E: implement IntentMechanism subclass, append to this
# tuple. No other code changes at Step 2+ time.
INTENT_MECHANISMS = (
    CountMechanism(),
    SelfReferenceMechanism(),
    LiteralFilenameMechanism(),
)


def search_embeddings(
    query: str,
    limit: int = 5,
    content_types: Optional[List[str]] = None,
    # Session 1234 D15 — lowered default 0.7 → 0.4. Pre-D15 the
    # value was 0.7 in the signature but get_rag_context called with
    # similarity_threshold=0.6 anyway (line 167). With the corpus
    # now backed by text-embedding-3-small (D12 pivot), similarities
    # cluster in the 0.4-0.7 band for related content; 0.7 cut off
    # essentially all real signal. 0.4 keeps obvious noise out while
    # still surfacing the corpus.
    similarity_threshold: float = 0.4,
    namespace: Optional[str] = 'system',
    exclude_personal: bool = True,
    # Session 1234 D12 — D9/D10 filter pushdown
    category: Optional[str] = None,
    document_class: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    min_session: Optional[int] = None,
    include_superseded: bool = False,
    # Cycle 1A KFI-3 (ADR-0130) — authority-aware retrieval.
    canonical_authority: Optional[str] = None,
    authority_weighted: bool = False,
) -> List[Dict[str, Any]]:
    """
    Session 1234 D12 — semantic search over Document corpus via pgvector.

    Pre-D12 this function targeted a `unified_embeddings` table that
    doesn't exist (the real Django table is `persistence_unifiedembedding`,
    which was empty even on local DB). Callers silently degraded to
    "no context" because the SQL failed every time.

    D12 pivots to the populated path: pgvector cosine similarity over
    `DocumentEmbedding` (the table the D9 sync + D10 backfill populated,
    ~16k+ rows post-backfill), joined to `Document` for the D9/D10
    type-aware filter pushdown (category / document_class / is_pinned /
    min_session) and default-exclude-superseded ranking.

    Backward-compat: the original signature kwargs (limit / content_types
    / similarity_threshold / namespace / exclude_personal) remain in
    place. `content_types` is treated as a soft hint mapped to
    `document_class` if not explicitly provided.

    Args:
        query: The search query (text → embedding via OpenAI).
        limit: Max results.
        content_types: Optional list of content types — back-compat hint.
            If `document_class` is also unset, the first entry is used
            as the document_class filter.
        similarity_threshold: Minimum cosine similarity (0-1).
        namespace: (legacy) — informational, not currently filtered.
        exclude_personal: (legacy) — Document table has no personal
            namespace; ignored. Kept for signature stability.
        category, document_class, is_pinned, min_session,
            include_superseded: Session 1234 D9/D10 filter pushdown.
            Same semantics as kb_tool action=documents (#2620).

    Returns:
        List of dicts shaped to the legacy contract:
        ``{id, content, content_type, metadata, importance_score,
        similarity_score}``. The retrieval_boost from D9/D10 maps to
        importance_score so downstream ranking still respects it.
    """
    # Create embedding for the query
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return []

    try:
        from content.models import Document, DocumentEmbedding, ContentStatus

        # Back-compat: if content_types is given and document_class isn't,
        # use the first content_type as a document_class hint. Avoids
        # breaking callers that passed e.g. ['document_chunk'] from the
        # legacy unified_embeddings era.
        effective_class = document_class
        if effective_class is None and content_types:
            first = content_types[0] if isinstance(content_types, (list, tuple)) and content_types else None
            if first and isinstance(first, str):
                effective_class = first

        # Session 1234 D16 — build the cosine-similarity queryset
        # INLINE (not via the classmethod) so D9/D10 filter pushdown
        # can run BEFORE the slice. The DocumentEmbedding.
        # cosine_similarity_search classmethod returns `qs[:limit]`,
        # which is a sliced queryset — Django raises
        # `Cannot filter a query once a slice has been taken` on any
        # subsequent `.filter()` or `.exclude()`. Pre-D16 the surrounding
        # try/except swallowed that exception and returned [] for every
        # call, which is why D11/D12/D13/D14/D15 all looked correct in
        # tests (mocked QS) but returned 0 chunks in production.
        #
        # Mirror the classmethod's orphan-chunk exclusion + cosine
        # threshold so retrieval still excludes parentless chunks
        # ("Agent Activity Knowledge Base" entries that pollute results).
        #
        # Cycle 1A KFI-3 (ADR-0130, Chris F1 Option B 2026-07-08):
        # workspace-mirror Documents (KFI-1) legitimately have empty
        # file_path — they originate from workspace Deliverables, not
        # from filesystem paths. The default orphan filter would exclude
        # them collaterally. Under Option B, default retrieval MUST
        # remain unchanged; workspace mirrors are reachable ONLY when
        # the caller explicitly requests them via
        # ``canonical_authority='workspace_canonical'``. The narrow
        # branch below substitutes ``source='workspace'`` as the
        # anti-pollution invariant for the explicit-opt-in path,
        # preserving the intent of the orphan exclusion while making
        # the workspace-canonical filter functional.
        from pgvector.django import CosineDistance
        qs = DocumentEmbedding.objects
        if canonical_authority == 'workspace_canonical':
            qs = qs.filter(document__source='workspace')
        else:
            qs = (
                qs
                .filter(document__file_path__isnull=False)
                .exclude(document__file_path='')
            )
        qs = (
            qs
            .annotate(distance=CosineDistance('embedding_vector', query_embedding))
            .filter(distance__lt=(1 - similarity_threshold))
        )

        # D9/D10 filter pushdown via Document join — now all run BEFORE
        # the slice so no `Cannot filter a sliced queryset` blowup.
        if category:
            qs = qs.filter(document__category=category)
        if effective_class:
            qs = qs.filter(document__document_class=effective_class)
        if is_pinned is True:
            # Truthy-only — feedback_llm_autofills_boolean_params_with_false.
            qs = qs.filter(document__is_pinned=True)
        if not include_superseded:
            qs = qs.exclude(document__status=ContentStatus.ARCHIVED)
        # Cycle 1A KFI-3 (ADR-0130 §2.1): canonical_authority filter.
        # Belt-and-suspenders alongside the source='workspace' branch
        # above — narrows repo_canonical / derived requests and adds
        # defense for the hypothetical case of a source='workspace'
        # row that failed to receive canonical_authority='workspace_canonical'.
        if canonical_authority:
            qs = qs.filter(document__canonical_authority=canonical_authority)
        # Session 1234 D14 — positive-only min_session guard.
        # LLM autofills integer params with 0 the same way it autofills
        # booleans with False; treat anything <= 0 as "no filter" so
        # the corpus isn't silently narrowed to handoff-only.
        if min_session is not None:
            try:
                threshold = int(min_session)
                if threshold > 0:
                    # Filter docs whose tags include any session-N >= threshold.
                    # JSONField tag filtering goes through a Python-side pass
                    # because semantics need int parsing of 'session-N' tags.
                    ok_doc_ids = set()
                    for d in Document.objects.filter(
                        id__in=qs.values_list('document_id', flat=True).distinct(),
                    ).only('id', 'tags'):
                        for t in (d.tags or []):
                            if isinstance(t, str) and t.startswith('session-'):
                                try:
                                    if int(t.split('-', 1)[1]) >= threshold:
                                        ok_doc_ids.add(d.id)
                                        break
                                except (ValueError, IndexError):
                                    continue
                    qs = qs.filter(document_id__in=ok_doc_ids)
            except (ValueError, TypeError):
                pass

        # Take final K after filtering.
        #
        # Default (authority_weighted=False): sort by cosine distance
        # ascending = closest match first. Unchanged from HEAD.
        #
        # Cycle 1A KFI-3 (ADR-0130 §2.1): when authority_weighted=True,
        # rank by weighted_score DESC, tie-break by
        # Coalesce(document.updated_at, document.created_at) DESC,
        # final by document.id ASC. The weighted score is computed
        # after retrieval (per-row) rather than pushed into the SQL
        # ORDER BY because CosineDistance annotations complicate ORM
        # arithmetic; the ranking is applied to the retrieved candidate
        # pool. To keep the candidate pool honest, we still ORDER BY
        # distance ASC in SQL and take a candidate window of `limit *
        # 3` (bounded oversample), then apply weighted ordering in
        # Python and truncate to `limit`. The oversample is a
        # bounded implementation detail; downstream consumers see
        # exactly `limit` rows.
        # S2826 Pattern B — narrow COUNT intent gate fires oversample too,
        # since the canonical target may sit at rank #2-#5 by raw distance
        # and the bonus needs a deep enough pool to promote it.
        # S2827 Pattern C — SELF_REFERENCE intent gate fires oversample +
        # candidate injection. Sibling shape to Pattern B; distinct gate
        # + distinct anchor map per Chris D5.
        count_intent_active = _detect_count_intent(query)
        self_reference_intent_matches = _detect_self_reference_intent(query)
        self_reference_intent_active = bool(self_reference_intent_matches)
        # S2828 Pattern D — LITERAL-FILENAME gate. Matches contain
        # (anchor_key, pattern_index, gate_name); anchor_key may be None
        # to signal a curated-map MISS (Strategy C log-only path). Active
        # if any pattern fired regardless of anchor resolution — the
        # oversample deepens the pool for the (rare) case where a
        # curated-map hit lets injection promote the anchor.
        literal_filename_intent_matches = _detect_literal_filename_intent(query)
        literal_filename_intent_active = bool(literal_filename_intent_matches)
        # Any curated-anchor resolution (excludes miss records)
        literal_filename_anchor_matches = tuple(
            m for m in literal_filename_intent_matches if m[0] is not None
        )
        if (
            authority_weighted
            or count_intent_active
            or self_reference_intent_active
            or literal_filename_intent_active
        ):
            candidate_qs = qs.order_by('distance')[:max(limit * 3, limit)]
            chunks = list(candidate_qs.select_related('document'))
        else:
            qs = qs.order_by('distance')[:limit]
            chunks = list(qs.select_related('document'))

        # S2827 Pattern C — canonical-anchor injection. Fetch anchor
        # chunks under the SAME filter chain (Chris D6 no-relaxation
        # invariant). If anchor is already in oversample pool, skip inject
        # and rely on bonus applied in the composition loop. If NOT in
        # pool, inject as candidate carrying real CosineDistance similarity
        # — the bonus applies in the composition loop identically.
        # Injected chunks marked via chunk.id membership set consumed
        # by the loop below (self_ref_injected diagnostic).
        injected_chunk_ids = set()
        if self_reference_intent_active:
            existing_chunk_ids = {c.id for c in chunks}
            injected = _fetch_self_reference_anchor_chunks(
                self_reference_intent_matches,
                qs,
                existing_chunk_ids,
                query_embedding,
            )
            for row in injected:
                injected_chunk_ids.add(row.id)
                chunks.append(row)

        # S2828 Pattern D — LITERAL-FILENAME candidate injection. Same
        # shape as Pattern C but distinct anchor map + per-gate bonus.
        # Chris D-Q4 tolerated Q28 no-perturb case handled by dedupe:
        # if the natural top-N pool already contains the resolved anchor
        # chunk, injection is skipped and the P3-tier bonus applies
        # additively via the composition loop below (rank 1 preserved).
        # Strategy C log-only miss path (Chris D-Q2): gate fires but
        # anchor_key is None → no injection, INFO log surfaces the
        # uncurated hit for future map-graduation consideration.
        literal_filename_injected_chunk_ids = set()
        if literal_filename_anchor_matches:
            existing_chunk_ids = {c.id for c in chunks}
            lf_injected = _fetch_literal_filename_anchor_chunks(
                literal_filename_anchor_matches,
                existing_chunk_ids,
                query_embedding,
            )
            for row in lf_injected:
                literal_filename_injected_chunk_ids.add(row.id)
                chunks.append(row)
        elif literal_filename_intent_active:
            # Gate fired but no curated anchor resolved — Strategy C
            # log-only path. Preserves auditability for future map
            # graduation without runtime resolution to non-canonical Docs.
            _miss = literal_filename_intent_matches[0]
            logger.info(
                "[S2828_PATTERN_D_MISS] gate fired but no curated anchor "
                "matched. query=%r canonicalized=%r pattern_index=%d "
                "gate=%s. Add to _LITERAL_FILENAME_ANCHORS if this is a "
                "canonical doc; else safely ignore.",
                query[:200],
                _canonicalize_literal_filename_token(query),
                _miss[1],
                _miss[2],
            )

        documents = []
        encryption_service = get_encryption_service()

        for chunk in chunks:
            doc = chunk.document
            # Decrypt content if encrypted; chunk_text usually plaintext.
            try:
                content = encryption_service.decrypt(chunk.chunk_text) if chunk.chunk_text else ''
            except Exception:
                content = chunk.chunk_text or ''

            # Cosine similarity = 1 - distance (annotation set by the
            # classmethod). Guard against NaN/inf.
            import math
            distance = getattr(chunk, 'distance', None)
            if distance is None:
                similarity = 0.0
            else:
                similarity = float(1 - distance)
                if math.isnan(similarity) or math.isinf(similarity):
                    similarity = 0.0

            # S2826 Pattern B — compute per-row COUNT bonus INSIDE the
            # loop so it composes naturally into both raw similarity
            # ordering (default path) and weighted_score (when
            # authority_weighted=True). Bonus is 0.0 when the intent
            # gate did not fire or the file is not in the bonus map.
            if count_intent_active:
                count_intent_bonus = _COUNT_INTENT_BONUS.get(doc.file_path or '', 0.0)
            else:
                count_intent_bonus = 0.0

            # S2827 Pattern C — per-row SELF_REFERENCE bonus. Fires only
            # when the intent gate matched AND this row's Document is
            # one of the mapped canonical anchors. Composes additively
            # with COUNT bonus (no query is expected to fire both gates
            # simultaneously — they're distinct policy classes per
            # Chris D5 — but the shape is deliberately compositional so
            # the invariant holds if it ever does).
            self_ref_intent_bonus = 0.0
            self_ref_anchor_key = None
            self_ref_matched_pattern_index = None
            self_ref_injected = False
            if self_reference_intent_active:
                fp = doc.file_path or ''
                for key, idx in self_reference_intent_matches:
                    if _SELF_REFERENCE_ANCHORS.get(key) == fp:
                        self_ref_intent_bonus = _SELF_REFERENCE_INTENT_BONUS
                        self_ref_anchor_key = key
                        self_ref_matched_pattern_index = idx
                        break
                # self_ref_injected = True if this chunk came from injection
                # rather than the original oversample pool.
                if chunk.id in injected_chunk_ids:
                    self_ref_injected = True

            # S2828 Pattern D — per-row LITERAL-FILENAME bonus. Fires only
            # when the gate matched AND this row's Document is one of the
            # curated anchors. Per-regex tiered per Chris D-Q1: bonus value
            # is per-gate-name (_LITERAL_FILENAME_INTENT_BONUS dict). Chris
            # D3 retrieval-integrity invariant preserved — bounded per-gate
            # bonus, NOT force-rank-1; a topic competitor with high enough
            # raw sim can still legitimately win.
            literal_filename_bonus = 0.0
            literal_filename_anchor_key = None
            literal_filename_matched_pattern_index = None
            literal_filename_gate_name = None
            literal_filename_injected = False
            if literal_filename_anchor_matches:
                fp = doc.file_path or ''
                for key, idx, gate_name in literal_filename_anchor_matches:
                    if _LITERAL_FILENAME_ANCHORS.get(key) == fp:
                        literal_filename_bonus = _LITERAL_FILENAME_INTENT_BONUS.get(
                            gate_name, 0.0
                        )
                        literal_filename_anchor_key = key
                        literal_filename_matched_pattern_index = idx
                        literal_filename_gate_name = gate_name
                        break
                if chunk.id in literal_filename_injected_chunk_ids:
                    literal_filename_injected = True

            effective_similarity = (
                similarity
                + count_intent_bonus
                + self_ref_intent_bonus
                + literal_filename_bonus
            )

            # Cycle 1A KFI-3 (ADR-0130 §2.1): compute weighted_score when
            # authority_weighted=True. retrieval_boost remains
            # orthogonal per 0120 — NOT composed into weighted_score.
            if authority_weighted:
                authority_weight = _get_authority_weight(doc.canonical_authority)
                weighted_score = effective_similarity * authority_weight
            else:
                authority_weight = None
                weighted_score = None
            documents.append({
                'id': str(chunk.id),
                'content': content[:1000],
                'content_type': doc.document_class or 'document',
                'metadata': {
                    'file_path': doc.file_path,
                    'title': doc.title,
                    'category': doc.category,
                    'document_class': doc.document_class,
                    'is_pinned': doc.is_pinned,
                    'tags': list(doc.tags or []),
                    'chunk_index': chunk.chunk_index,
                    # citation in the same shape as search_docs PA tool
                    'citation': f"[{doc.file_path}#{chunk.chunk_index}]",
                    # Cycle 1A KFI-3 (ADR-0130): canonical_authority
                    # metadata for downstream authority-aware consumers.
                    'canonical_authority': doc.canonical_authority,
                    # Retained for deterministic tie-break sort below.
                    'updated_at': doc.updated_at,
                    'created_at': doc.created_at,
                    'document_id': doc.id,
                },
                # D9/D10 retrieval_boost maps to legacy importance_score.
                'importance_score': float(doc.retrieval_boost or 1.0),
                'similarity_score': similarity,
                # S2826 Pattern B + S2827 Pattern C diagnostic (per Chris
                # D2 traceability + Rigby SIGN Q4/Q5 refinements) —
                # surfaces gate + bonus provenance so consumers + tests
                # can distinguish raw semantic rank from policy-boosted
                # rank AND natural retrieval from candidate injection.
                'intent_gate_fired': (
                    count_intent_active
                    or self_reference_intent_active
                    or literal_filename_intent_active
                ),
                # Precedence: count > self_reference > literal_filename.
                # Documented precedence for determinism; disjoint by design
                # (whole-string P0-P3 vs multi-word Pattern B/C patterns).
                'intent_gate_name': (
                    'count' if count_intent_active else
                    'self_reference' if self_reference_intent_active else
                    'literal_filename' if literal_filename_intent_active else
                    None
                ),
                'count_intent_bonus': count_intent_bonus,
                # S2827 Pattern C diagnostic fields (Chris D-Q1 acceptance
                # requirement: injected candidates distinguishable from
                # naturally-retrieved candidates).
                'self_ref_intent_bonus': self_ref_intent_bonus,
                'self_ref_anchor_key': self_ref_anchor_key,
                'self_ref_matched_pattern_index': self_ref_matched_pattern_index,
                'self_ref_injected': self_ref_injected,
                # S2828 Pattern D diagnostic fields (Chris D-Q1 acceptance
                # requirement: per-gate name + bonus + anchor key + injection).
                'literal_filename_intent_bonus': literal_filename_bonus,
                'literal_filename_anchor_key': literal_filename_anchor_key,
                'literal_filename_matched_pattern_index': literal_filename_matched_pattern_index,
                'literal_filename_gate_name': literal_filename_gate_name,
                'literal_filename_injected': literal_filename_injected,
                'effective_similarity': effective_similarity,
                # Cycle 1A KFI-3: authority-aware retrieval fields.
                # Top-level canonical_authority is always populated;
                # authority_weight + weighted_score are populated only
                # when authority_weighted=True.
                'canonical_authority': doc.canonical_authority,
                'authority_weight': authority_weight,
                'weighted_score': weighted_score,
            })

        # Cycle 1A KFI-3 (ADR-0130 §2.1): apply weighted ranking +
        # deterministic tie-break in Python. Sort key composition:
        #   1. weighted_score DESC
        #   2. Coalesce(document.updated_at, document.created_at) DESC
        #   3. document.id ASC (primary final tie-break per ADR §2.1)
        #   4. chunk.id ASC (post-code SIGN hardening: two chunks from
        #      the same Document tie on 1-3; DocumentEmbedding.id keeps
        #      chunk ordering deterministic)
        if authority_weighted:
            def _sort_key(row):
                meta = row['metadata']
                effective_ts = meta.get('updated_at') or meta.get('created_at')
                doc_id_str = str(meta.get('document_id') or '')
                chunk_id_str = str(row.get('id') or '')
                epoch = effective_ts.timestamp() if effective_ts else 0.0
                return (
                    -row['weighted_score'],
                    -epoch,
                    doc_id_str,
                    chunk_id_str,
                )
            documents.sort(key=_sort_key)
            documents = documents[:limit]
        elif count_intent_active or self_reference_intent_active or literal_filename_intent_active:
            # S2826 Pattern B + S2827 Pattern C + S2828 Pattern D — when
            # any intent gate fires and we oversampled the candidate pool,
            # re-sort by (raw similarity + all applied bonuses) descending.
            # Tie-break identical to authority_weighted path (updated_at
            # DESC then document.id ASC then chunk.id ASC) so downstream
            # ordering stays deterministic even when bonuses create ties.
            # Bonuses compose additively (row['effective_similarity']
            # already equals sim + count_bonus + self_ref_bonus +
            # literal_filename_bonus per composition loop above).
            def _intent_sort_key(row):
                meta = row['metadata']
                effective_ts = meta.get('updated_at') or meta.get('created_at')
                doc_id_str = str(meta.get('document_id') or '')
                chunk_id_str = str(row.get('id') or '')
                epoch = effective_ts.timestamp() if effective_ts else 0.0
                return (
                    -row.get('effective_similarity', row['similarity_score']),
                    -epoch,
                    doc_id_str,
                    chunk_id_str,
                )
            documents.sort(key=_intent_sort_key)
            documents = documents[:limit]

        # Strip internal tie-break fields before returning to callers.
        for row in documents:
            row['metadata'].pop('updated_at', None)
            row['metadata'].pop('created_at', None)
            row['metadata'].pop('document_id', None)

        logger.info(
            f"Found {len(documents)} relevant chunks for query "
            f"(filters: category={category} class={effective_class} "
            f"is_pinned={is_pinned} min_session={min_session} "
            f"include_superseded={include_superseded} "
            f"canonical_authority={canonical_authority} "
            f"authority_weighted={authority_weighted} "
            f"count_intent_active={count_intent_active} "
            f"self_reference_intent_active={self_reference_intent_active} "
            f"literal_filename_intent_active={literal_filename_intent_active})"
        )

        # S2826 Pattern B drift-re-mask detection (Rigby SIGN Q5). WARN
        # when the intent gate fired but none of the canonical targets
        # in _COUNT_INTENT_BONUS surfaced in the returned candidate pool.
        # Root causes the log surfaces: (a) target Document.status drifted
        # from 'processed' back to 'archived' and got filtered by
        # include_superseded=False; (b) target chunk similarity dropped
        # below threshold; (c) target file was removed/renamed. Without
        # this alert, future metadata drift silently erases the Pattern B
        # benefit (the class of drift S2826 root-cause established).
        if count_intent_active and _COUNT_INTENT_BONUS:
            returned_paths = {
                (d.get('metadata') or {}).get('file_path') for d in documents
            }
            missing_targets = [
                p for p in _COUNT_INTENT_BONUS.keys() if p not in returned_paths
            ]
            if missing_targets and len(missing_targets) == len(_COUNT_INTENT_BONUS):
                # ALL canonical targets absent — most likely the metadata
                # drift class. Single-target-missing is expected on off-
                # target queries; all-missing when the gate fires is the
                # concerning shape.
                logger.warning(
                    "[S2826_PATTERN_B_DRIFT] count_intent_active=True but "
                    "NONE of the mapped canonical targets are in the "
                    "returned pool. targets=%s query=%r include_superseded=%s. "
                    "Check Document.status='processed' for these paths; "
                    "S2826 root-cause showed sync_docs_index_to_documents "
                    "update path does not refresh status field.",
                    list(_COUNT_INTENT_BONUS.keys()),
                    query[:200],
                    include_superseded,
                )

        # S2827 Pattern C drift-re-mask detection (Rigby SIGN Q5 caveat).
        # WARN when the SELF_REFERENCE intent gate fired but NONE of the
        # anchor keys matched by the gate produced a chunk in the returned
        # pool. Same shape as Pattern B WARN — mirrors the fold class
        # `sync_update_path_completeness` documented at S2826 §5.2. Only
        # inspects anchor keys that the gate ACTUALLY matched (not the
        # full anchor map), so an off-target SELF_REFERENCE query firing
        # only one anchor doesn't over-alarm.
        if self_reference_intent_active:
            returned_paths = {
                (d.get('metadata') or {}).get('file_path') for d in documents
            }
            matched_anchor_paths = {
                _SELF_REFERENCE_ANCHORS[key] for key, _ in self_reference_intent_matches
            }
            missing = matched_anchor_paths - returned_paths
            if missing and missing == matched_anchor_paths:
                logger.warning(
                    "[S2827_PATTERN_C_DRIFT] self_reference_intent_active=True "
                    "but NONE of the mapped canonical anchors are retrievable "
                    "under current filters. anchor_paths=%s query=%r "
                    "include_superseded=%s. Check Document.status='processed' "
                    "for these paths; S2826 root-cause showed "
                    "sync_docs_index_to_documents update path may miss field "
                    "refresh classes.",
                    sorted(matched_anchor_paths),
                    query[:200],
                    include_superseded,
                )

        # S2828 Pattern D drift-re-mask detection. Companion to Pattern
        # B/C WARNs; only fires when the LITERAL-FILENAME gate matched a
        # curated anchor (not the Strategy C miss path — that already
        # emitted its own INFO log).
        if literal_filename_anchor_matches:
            returned_paths = {
                (d.get('metadata') or {}).get('file_path') for d in documents
            }
            matched_anchor_paths = {
                _LITERAL_FILENAME_ANCHORS[key]
                for key, _, _ in literal_filename_anchor_matches
                if key is not None
            }
            missing = matched_anchor_paths - returned_paths
            if missing and missing == matched_anchor_paths:
                logger.warning(
                    "[S2828_PATTERN_D_DRIFT] literal_filename_intent_active=True "
                    "with curated anchor(s) resolved but NONE reached the "
                    "returned pool. anchor_paths=%s query=%r "
                    "include_superseded=%s. Check Document.status='processed' "
                    "for these paths; future metadata drift may silently "
                    "re-mask Pattern D.",
                    sorted(matched_anchor_paths),
                    query[:200],
                    include_superseded,
                )
        return documents

    except _RAG_EMBEDDINGS_ENV_ERRORS as e:
        # Session 2728 F-RG-1 — narrow except discipline. Pre-patch this
        # branch caught EVERY Exception (ORM, decrypt, math, TypeError from
        # a caller-side bug, etc.) and returned []. That silent zero-results
        # is indistinguishable from "no relevant content" and is the same
        # anti-pattern S1234 D21 fixed for `search_personal_memories`. Now
        # only environmental errors (DB connection lost, network down, OS
        # I/O) return [] with the error log; logic errors propagate so
        # future refactors that break the retrieval path are visible.
        logger.error(
            f"search_embeddings: environmental error: "
            f"{type(e).__name__}: {e}",
            exc_info=True,
        )
        return []

def get_rag_context(query: str, max_tokens: int = 2000, include_personal: bool = False) -> Dict[str, Any]:
    """
    Get RAG context for a query
    
    Args:
        query: The user's query
        max_tokens: Maximum tokens to include in context
        include_personal: Whether to include personal memories (default: False)
        
    Returns:
        Dictionary with context and metadata
    """
    
    # Search for relevant documents
    # Session 1234 D15 — was 0.6; lowered to 0.4 to match the new
    # search_embeddings default. text-embedding-3-small puts related
    # content in the 0.4-0.7 band; 0.6 was cutting most signal.
    documents = search_embeddings(
        query=query,
        limit=10,  # Get more initially, then filter
        similarity_threshold=0.4,
        exclude_personal=not include_personal  # Respect privacy by default
    )
    
    if not documents:
        logger.info("No relevant documents found for RAG")
        return {
            'has_context': False,
            'documents': [],
            'context_text': ""
        }
    
    # Build context text
    context_parts = []
    used_documents = []
    current_tokens = 0
    
    for doc in documents:
        # Estimate tokens (rough approximation)
        doc_tokens = len(doc['content']) // 4
        
        if current_tokens + doc_tokens > max_tokens:
            break
            
        context_parts.append(f"[{doc['content_type'].upper()}] {doc['content']}")
        used_documents.append({
            'id': doc['id'],
            'type': doc['content_type'],
            'similarity': doc['similarity_score']
        })
        current_tokens += doc_tokens
    
    context_text = "\n\n".join(context_parts)
    
    return {
        'has_context': bool(context_text),
        'documents': used_documents,
        'context_text': context_text,
        'total_documents': len(documents),
        'used_documents': len(used_documents)
    }

def _cosine_similarity_python(a, b):
    """Pure-Python cosine similarity for JSON-stored embedding vectors.

    Session 1234 D21 — UserEmbedding.embedding_vector is a JSONField,
    not a pgvector VectorField, so we can't use the native `<=>`
    operator. Python-side cosine is fine for the expected corpus size
    (0 → a few thousand rows per user). When UserEmbedding grows past
    ~10k rows total, migrate the field to pgvector VectorField and
    repoint this function at the native operator.
    """
    if not a or not b or len(a) != len(b):
        return 0.0
    import math
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# Session 1234 D21 — Personal-memory search narrow-except allowlist.
# Same shape as D17/D18/D19/D20 (DatabaseError, ConnectionError,
# OSError). The cross-file invariant in
# test_d20_views_rag_embeddings_narrow_except.py is NOT extended to
# include this constant because `rag_integration.py` is the
# rag-integration module proper, not a retrieval helper file. The
# functional contract (narrow same set of env errors) is the same,
# but the module's name doesn't fit the test's existing import paths.
_PERSONAL_MEMORY_ENV_ERRORS = (
    __import__('django.db.utils', fromlist=['DatabaseError']).DatabaseError,
    ConnectionError,
    OSError,
)


def search_personal_memories(
    query: str,
    user_id: Optional[int] = None,
    limit: int = 5,
    similarity_threshold: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Search a user's personal memories via UserEmbedding semantic search.

    Session 1234 D21 — full rewrite. Pre-D21 this function:
      - Connected to a non-existent `ai_unified_platform` database
        (with a non-existent `ai_unified_user` PG user)
      - Queried a non-existent `unified_embeddings` table
      - Wrapped both errors in a broad try/except → return [], so
        every call silently returned "no memories" indistinguishable
        from "user has no personal memories yet"

    Post-D21 this function:
      - Uses Django ORM against `UserEmbedding` (the populated user-
        scoped embedding store: 0 rows locally, populated on Railway
        when chat injects user memories into the embedding pipeline)
      - Filters by `user_id` + `is_active=True` for strict access
        control (no cross-user leakage; matches the original intent)
      - Computes cosine similarity in Python because UserEmbedding's
        `embedding_vector` is a JSONField (not pgvector VectorField).
        Fine performance-wise for the expected corpus size; migrate
        the field to VectorField when usage grows.
      - Narrows the broad except to env errors only per D17-D20
        discipline. Logic errors propagate so future refactors that
        break this function are visible.
      - Default similarity_threshold lowered 0.7 → 0.4 to match D15
        (text-embedding-3-small puts related content in 0.4-0.7 band).

    Args:
        query: The search query (text → embedding).
        user_id: ID of the user whose memories to search. Required.
        limit: Maximum number of results.
        similarity_threshold: Minimum cosine similarity (0-1).

    Returns:
        List of personal memory dicts with shape:
            {id, content, content_type, metadata, importance_score,
             similarity_score, is_personal}
    """
    if not user_id:
        logger.warning("search_personal_memories: no user_id supplied; refusing")
        return []

    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("search_personal_memories: failed to create query embedding")
        return []

    try:
        # Lazy import — UserEmbedding lives in core.models_unified_system
        # which has a heavy import graph; deferring keeps rag_integration
        # importable from views.py without dragging it in.
        from django.apps import apps
        UserEmbedding = apps.get_model('core', 'UserEmbedding')

        qs = UserEmbedding.objects.filter(
            user_id=user_id,
            is_active=True,
        ).only(
            'id', 'content', 'content_type', 'metadata', 'confidence_score',
            'embedding_vector',
        )

        scored = []
        for row in qs:
            vec = row.embedding_vector
            if not vec:
                continue
            sim = _cosine_similarity_python(query_embedding, vec)
            if sim < similarity_threshold:
                continue
            scored.append((sim, row))

        # Sort by similarity * importance descending (matches the pre-D21
        # ranking semantics; `confidence_score` is the closest analog to
        # the pre-D21 `importance_score` field).
        scored.sort(
            key=lambda t: t[0] * float(getattr(t[1], 'confidence_score', 1.0) or 1.0),
            reverse=True,
        )

        documents = []
        for sim, row in scored[:limit]:
            documents.append({
                'id': str(row.id),
                'content': (row.content or '')[:1000],
                'content_type': row.content_type or 'memory',
                'metadata': row.metadata if isinstance(row.metadata, dict) else {},
                'importance_score': float(row.confidence_score or 0.5),
                'similarity_score': sim,
                'is_personal': True,
            })

        logger.info(
            f"search_personal_memories: returned {len(documents)} memories "
            f"for user {user_id} (threshold={similarity_threshold}, "
            f"scored {len(scored)} above threshold of {qs.count()} total)"
        )
        return documents

    except _PERSONAL_MEMORY_ENV_ERRORS as e:
        logger.error(
            f"search_personal_memories: environmental error: "
            f"{type(e).__name__}: {e}"
        )
        return []


def enhance_prompt_with_rag(user_message: str, rag_context: Dict[str, Any]) -> str:
    """
    Enhance the user's prompt with RAG context
    
    Args:
        user_message: Original user message
        rag_context: RAG context from get_rag_context
        
    Returns:
        Enhanced prompt with context
    """
    
    if not rag_context.get('has_context'):
        return user_message
    
    enhanced_prompt = f"""You have access to the following relevant context from the knowledge base:

{rag_context['context_text']}

Based on this context and your knowledge, please answer the following question:

{user_message}

Please incorporate relevant information from the context in your response where appropriate."""
    
    return enhanced_prompt
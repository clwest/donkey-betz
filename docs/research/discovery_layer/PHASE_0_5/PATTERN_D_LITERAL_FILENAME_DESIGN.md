---
title: "Pattern D — LITERAL-FILENAME Candidate Injection Design"
session: 2828
authored: 2026-07-19
status: draft — awaiting Rigby joint SIGN
authority: engineering
scope: |
  Convert the 2 remaining literal-filename Phase-0.5 corpus misses
  (Q20 `00-START-NEXT-SESSION`, Q24 `PLATFORM_INVENTORY`) by injecting
  canonical anchor documents into the retrieval candidate pool when a
  narrow LITERAL-FILENAME intent gate fires. Adjacent literal query
  `CLAUDE.md` also in scope even though not a corpus row (Chris D-Q4
  S2827 named it explicitly: "literal-filename queries (Q20 + explicit
  CLAUDE.md / 00-START-NEXT-SESSION literal) belong in Pattern D").
  Q28 (`2701_docs_inventory_topology_audit`) is a literal-filename
  query but already wins at rank 1 natively (baseline sim 0.5973 at
  rank 1); Pattern D must not perturb Q28. Design mirrors Pattern C
  shape (S2827) while owning a distinct policy class per Chris D5
  distinct-mechanism-per-class discipline.
predecessor: docs/research/discovery_layer/PHASE_0_5/PATTERN_C_SELF_REFERENCE_DESIGN.md
governing_envelope: docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md
---

# Pattern D — LITERAL-FILENAME Candidate Injection Design

## §0 — Rigby joint SIGN reconciliation summary (2026-07-19)

Five SIGN questions routed with anti-rubber-stamp directive; Rigby
returned 10 tool_runs (`repo_tool.read_file` ×2 on `core/rag_integration.py`
+ this design doc; `kb_tool.semantic_search` ×6 on README /
00-START-NEXT-SESSION / PLATFORM_INVENTORY / CLAUDE.md /
00-START-NEXT-SESSION.md / KNOWLEDGE_PIPELINE; `kb_tool.documents` ×1;
`search_docs` ×1). Verdicts + refinements applied:

| SIGN Q | Rigby verdict | Refinement applied in v2 | Section |
|---|---|---|---|
| Q1 gate disjointness | AGREE with load-bearing nuance | Explicit invariant callout: whole-string `^...$` anchoring is Chris D5 boundary; any future substring-relaxation MUST re-run SIGN before shipping | §4.1 |
| Q2 anchor resolution | AGREE Strategy A + small Strategy C | Adopt Strategy A curated map; add lightweight Strategy C "structured miss log" for gate-fires-but-no-anchor-match (diagnostic-only, does NOT resolve to random Documents) | §4.2 |
| Q3 bonus sizing (Q20 +0.31 gap) | DISAGREE with 3-A flat bonus | **Adopt Strategy 3-B: per-regex bonus tiers.** P0 (`.md` ext) = highest determinism; P1/P2 (uppercase snake / hyphenated CAPS) = mid-high; P3 (numeric-prefix snake) = lowest. Sweep + smallest reliable per gate; Chris D-Q1 discipline extends to per-pattern | §4.3 |
| Q4 retrieval integrity for literal queries | DISAGREE with "force rank 1" | Bounded discipline preserved. Rigby's tool_run #4 evidence: even literal `00-START-NEXT-SESSION` has a genuine topic-competitor at 0.7098 that talks about the target. Pattern D "advantages" the canonical; does NOT unconditionally pin | §4.3, §5 |
| Q5 zoom-out | AGREE (a) refactor after; caution (b) expand negatives; YES (c) persist fold | (a) 3-instance-then-refactor discipline preserved; (b) negative controls expanded with README, INDEX, natural-lang-with-filename cases; (c) Rigby fold persisted BELOW in §0.1 as `same_pr_mitigatable` per PLAYBOOK-6.10.8 | §5, §0.1 |

**Post-reconciliation joint agreement**: Claude + Rigby AGREE on
R1/R2/R3/R4/R5 (all refinements landed). Ready for Chris D-verdict per
S2753 "reach agreement before Chris yes/no" discipline.

### §0.1 — Zoom-out fold persisted BEFORE ship (per PLAYBOOK-6.10.8)

**Rigby-proposed fold (Q5c)**, classified `same_pr_mitigatable`:

> Literal-filename intent is not the same as "no competitor legitimately
> wins" in embedding space; it is only "high confidence of a canonical
> target existing." Therefore Pattern D must treat *gate certainty* as the
> knob that earns a higher bonus ceiling, not treat "literal" as an
> unconditional pin.

**Mitigation in same PR**: adoption of Strategy 3-B per-regex bonus
tiers (§4.3 below) IS this fold's mitigation — bonus size is
proportional to gate certainty (P0 strongest, P3 weakest). Fold is
therefore recorded here + in `logs/zoom_out_classifications.jsonl` at
close-cascade time; no future-trigger carry required.

---

## §1 — Purpose

Convert **2 measured Phase-0.5 corpus rows** and **1 explicitly named
adjacent query** from Pattern D LITERAL-FILENAME candidate injection:

- **Q20** (`00-START-NEXT-SESSION`) — intended family SELF-REFERENCE,
  but the query IS a literal filename token (`has_literal_identifier: true`
  in corpus.json). Ceded to Pattern D per Chris D-Q4 S2827 and Rigby
  SIGN Q3 DISAGREE S2827.
- **Q24** (`PLATFORM_INVENTORY`) — intended family IDENTITY, literal
  uppercase-token filename stem (`has_literal_identifier: true`).
- **`CLAUDE.md`** literal (not a corpus row, but named explicitly by
  Chris D-Q4 S2827 as Pattern D territory).

The mechanism shape was sequenced by Chris D-Q5 S2827: "sequential arc
order (Pattern C → close → Pattern D)." Pattern C shipped 2026-07-19
as PR #3267 (SHA `47f3650d1`). This design opens the Pattern D arc as
S2828's default lean per `00-START-NEXT-SESSION.md`.

Expected outcome: **10/18 → 12/18 = 66.7% strict top-1** (per S2828
brief projection). The bonus discipline (Chris D-Q1 "smallest reliable
adjustment") will govern actual mechanism parameters; the projection is
an upper bound assuming both intended positives convert cleanly.

---

## §2 — Chris constitutional constraints preserved

| # | Constraint | Source | Compliance in this design |
|---|---|---|---|
| C1 | "Retrieval must prove retrieval. Runtime injection cannot be used to erase a retrieval-layer failure." | Chris D3 first cycle S2826; reaffirmed S2827 §Pattern C boundary summary | Pattern D injects INTO the candidate pool at retrieval-layer time (inside `search_embeddings`), BEFORE ranking — not at PA runtime after retrieval returns. Same shape as Pattern C. |
| C2 | Distinct mechanism per policy class | Chris D5 first cycle S2826; reaffirmed Chris D-Q4/D-Q5 S2827 | Pattern D is scoped to LITERAL-FILENAME queries. Gate patterns designed to NOT overlap Pattern B (COUNT) or Pattern C (semantic SELF_REFERENCE phrases). |
| C3 | Metadata layer inspection first | Chris D7 first cycle S2826 | §3.1 records the metadata layer state verification performed 2026-07-19 before authoring this design. |
| C4 | No `include_superseded=False` default relaxation | Chris D6 second cycle S2826; unchanged S2827 | Injection composes WITH the `include_superseded=False` filter — injected candidates fetched under the same filter chain (mirrors Pattern C `_fetch_self_reference_anchor_chunks`). |
| C5 | No universal runtime injection at PA level | Chris D3 first cycle S2826 | Design lives entirely inside `search_embeddings`; no PA-side change. |
| C6 | Bounded policy bonus with diagnostic surface | Chris D2 first cycle S2826 + Chris D-Q1 refinement S2827 ("smallest reliable adjustment; record tested alternatives + margins") | §4.3 defines the bonus sweep methodology mirroring Pattern C §7.5.2. Actual value TBD post-sweep. |
| C7 | Negative controls verified | Chris D4 first cycle S2826 | §5 defines negative-control queries with expected non-fire behavior. Includes Q28 (naturally-winning literal-filename) as a critical no-perturb control. |
| C8 | Post-Pattern-D 3-instance threshold for shared "pointer-intent registry" extraction | Chris D-Q3 S2827 | Pattern D is deliberately built as a distinct third mechanism; refactor to shared primitive deferred to POST-Pattern-D per Chris D-Q3 forward-carry. |
| C9 | No collapse of Pattern C + D into generic canonical gate | Chris D5 + Chris D-Q3/D-Q4 S2827 | §4.1 patterns are disjoint from Pattern C `_SELF_REFERENCE_INTENT_PATTERNS`; no shared regex; separate anchor map. |
| C10 | Corpus label ground-truth repair as ground-truth, not tuning | Chris D-Q2 S2827 | Corpus labels for Q20/Q24 already correct post-S2827 corpus repair (Q20 target `00-START-NEXT-SESSION.md` matches real repo-root path). No further corpus edit anticipated. |

---

## §3 — Pre-design evidence

### §3.1 — Metadata layer state (verified 2026-07-19 via ORM direct query)

Both canonical anchors are healthy in the Document table (already
confirmed at S2826 and S2827; re-verified 2026-07-19):

| file_path | status | canonical_authority | retrieval_boost | Document present |
|---|---|---|---|---|
| `00-START-NEXT-SESSION.md` | `processed` | `repo_canonical` | 1.5 | ✅ (used by Pattern C) |
| `docs/PLATFORM_INVENTORY.md` | `processed` | `repo_canonical` | 1.5 | ✅ |
| `CLAUDE.md` | `processed` | `repo_canonical` | 1.5 | ✅ (used by Pattern C) |

Both `docs/PLATFORM_INVENTORY.md` and `CLAUDE.md` are already in the
Pattern B `_COUNT_INTENT_BONUS` map (PLATFORM_INVENTORY) or Pattern C
`_SELF_REFERENCE_ANCHORS` map (CLAUDE.md). Pattern D shares the same
Document rows but fires on a different intent gate.

### §3.2 — Baseline retrieval evidence (2026-07-19, post-Pattern-C)

Direct `search_embeddings` query for each Pattern D candidate, production
settings (`similarity_threshold=0.4`, `include_superseded=False`, no bypass
flags), top-5 candidate pool:

| qid | query | Canonical anchor in top-5? | Top-1 file | Top-1 sim | Anchor raw sim | Gap |
|---|---|:-:|---|:-:|:-:|:-:|
| Q20 | `00-START-NEXT-SESSION` | ❌ | `docs/handoffs/SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md` | 0.7098 | 0.3979 | **+0.3119** |
| Q24 | `PLATFORM_INVENTORY` | ❌ | `docs/research/platform/platform_constitutional_transition_review.md` | 0.5570 | 0.4751 | +0.0819 |
| Q17-literal | `CLAUDE.md` | ❌ | `docs/handoffs/SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md` | 0.5967 | 0.5363 | +0.0604 |
| Q28 (control) | `2701_docs_inventory_topology_audit` | ✅ (rank 1) | `docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md` | 0.5973 | 0.5973 | 0.0 (self) |

**Conclusion 1**: Q20/Q24/CLAUDE.md-literal anchors are absent from the
natural candidate pool. Candidate injection is genuinely necessary
(same shape as Pattern C).

**Conclusion 2**: Q28 is a naturally-winning literal-filename query.
Pattern D must not perturb Q28's rank-1 outcome. This informs §5
negative controls.

**Conclusion 3 — Q20 gap is a design tension**: Q20's gap of **+0.31**
is 40% larger than Pattern C's Q14 limiting case (+0.22). A "smallest
reliable adjustment" static bonus would need to be ≥+0.32 to flip Q20
under injection — notably larger than Pattern C's shipped +0.23. Design
questions this raises:
- Is +0.32 acceptable as a bounded bonus per Chris D-Q1 discipline?
- Or is Pattern D's mechanism *different enough* from Pattern C to
  justify a distinct approach (e.g., higher-signal intent gate → larger
  ceiling)?
- Or should Q20 be treated as an exception (converts only if the
  measurement report shows the bonus does not over-fire in negatives)?

**Routed as SIGN Q3 below.**

### §3.3 — Q28 self-match natural win — do not perturb

Q28's query text `2701_docs_inventory_topology_audit` is the exact
basename (extension-stripped) of the target Document's file_path.
Embedding similarity is high enough that the target self-matches at
rank 1 naturally. If Pattern D's intent gate fires on Q28 AND applies a
bonus AND the target is already in the pool, the effect is neutral
(bonus is applied to the row that would win anyway). If the injection
mechanism fetches the same chunk that's already in the pool, we must
dedupe (mirrors Pattern C `injected_chunk_ids` set — S2827 line ~470).

Design principle: **gate over-firing on Q28 is TOLERABLE as long as
Q28's rank-1 outcome is preserved** (S2827 Pattern C dedup + inject-only-
if-missing invariant handles this cleanly).

### §3.4 — Post-Pattern-C 10/18 baseline (authoritative going forward)

Per Chris D-Q2 S2827 rule: post-corpus-correction 18-row corpus IS the
authoritative baseline. Pattern D re-measurement compares against this
baseline, not against S2825 (0/16) or S2826 (6/18):

| Session | Strict top-1 hits |
|---|:-:|
| S2825 (pre-Pattern-B) | 0/16 |
| S2826 (post-Pattern-B + metadata repair) | 6/18 |
| S2827 (post-Pattern-C + corpus repair) | 10/18 = 55.6% |
| **S2828 target (post-Pattern-D)** | **12/18 = 66.7%** (Q20 + Q24 conversion) |

---

## §4 — Mechanism design (mirrors Pattern B/C shape from `core/rag_integration.py:60-217`)

### §4.1 — Narrow LITERAL-FILENAME intent gate (`_detect_literal_filename_intent`) — v1

**Design principle**: detect queries that look like a filename token,
not natural language. Regex-narrow; require structural signal (no
whitespace + high identifier-density + case OR extension OR
snake/kebab-case) to avoid over-firing on natural queries.

Proposed regex patterns (compiled `re.I` where noted):

```python
_LITERAL_FILENAME_INTENT_PATTERNS = (
    # P0 — explicit .md extension (case-insensitive)
    #   matches: CLAUDE.md, README.md, PLATFORM_INVENTORY.md
    #   does not match: "CLAUDE md file", "read the .md docs"
    re.compile(r'^\s*[\w\-]+\.md\s*$', re.I),

    # P1 — uppercase-token filename stem (2+ uppercase segments joined by _)
    #   matches: PLATFORM_INVENTORY, KNOWLEDGE_PIPELINE, MISSION_CONTROL
    #   does not match: PLATFORM (single word, too short), "how many PLATFORM_INVENTORY docs"
    re.compile(r'^\s*[A-Z][A-Z0-9]+(?:_[A-Z][A-Z0-9]+)+\s*$'),

    # P2 — hyphenated ALL-CAPS token (3+ segments joined by -)
    #   matches: 00-START-NEXT-SESSION (4 segments)
    #   does not match: ADR-0130 (2 segments — deliberately excluded to
    #     avoid firing on ticket-id patterns), START (single), "the
    #     00-START-NEXT-SESSION file" (has whitespace)
    #   Note: {2,} means 2+ additional segments after the first, i.e.
    #     3+ total segments. Verified 2026-07-19 via regex probe.
    re.compile(r'^\s*[A-Z0-9]+(?:-[A-Z0-9]+){2,}\s*$'),

    # P3 — numeric-prefix snake_case filename (kebab-case-with-numeric-lead)
    #   matches: 2701_docs_inventory_topology_audit
    #   does not match: "docs inventory audit"
    re.compile(r'^\s*\d+[_\-][a-z0-9]+(?:[_\-][a-z0-9]+){2,}\s*$'),
)
```

**Gate semantics**: query matches ANY pattern → gate fires. Anchor
resolution mechanism (§4.2) then attempts to resolve the token to a
canonical anchor.

**Deliberate exclusions**:
- Bare lowercase words (`spider`, `agent`) — Q25 case, too ambiguous.
- Multi-word natural language (`how many spiders`, `where do I start`) —
  handled by Pattern B (COUNT) or Pattern C (semantic SELF_REFERENCE)
  or handled correctly by natural embedding.
- Filenames embedded in longer queries (`please open CLAUDE.md`) —
  requires whole-string match via `^` and `$` anchors.

**Overlap check with Pattern C**:
- Pattern C `\bwhere\s+do\s+I\s+start\b` — multi-word, natural language.
  Never matches Pattern D's whole-string patterns.
- Pattern C `\bproject\s+rules?\b` — multi-word. Never matches.
- Pattern C `\b(the\s+)?(next\s+)?session\s+start\s+(doc|file|page|md)\b` —
  multi-word. Never matches.
- No regex overlap. Chris D5 distinct-mechanism preserved.

**Overlap check with Pattern B**:
- Pattern B `\bhow\s+many\b`, `\bhow\s+much\b`, `\bnumber\s+of\b`,
  `\bcount\s+of\b`, `\blist\s+all\b`, `\btotal\s+...` — all multi-word.
  Never match Pattern D whole-string patterns. Disjoint.

**LOAD-BEARING INVARIANT (Rigby SIGN Q1 nuance):** Disjointness of
Pattern D vs B/C is guaranteed by the `^...$` whole-string anchoring in
P0-P3. If a future author considers relaxing to substring matching
(e.g., "please open CLAUDE.md" as a Pattern D-firing query), overlap
risk immediately rises because Pattern B/C patterns can co-occur with
filename tokens in natural sentences. Any relaxation of the whole-string
invariant MUST re-route the design through Rigby SIGN + Chris D-verdict.

**Gate fires on Pattern D targets:**
- Q20 `00-START-NEXT-SESSION` — matches P2 (hyphenated ALL-CAPS ≥3 segments)
- Q24 `PLATFORM_INVENTORY` — matches P1 (uppercase snake_case ≥2 segments)
- `CLAUDE.md` — matches P0 (.md extension)
- Q28 `2701_docs_inventory_topology_audit` — matches P3 (numeric-prefix
  snake_case ≥3 segments); tolerable per §3.3

**Gate does NOT fire on Pattern C targets:**
- Q14 `the next session start doc` — multi-word natural language ✓
- Q15 `where do I start` — multi-word ✓
- Q16 `start here` — multi-word ✓
- Q17 `project rules` — multi-word ✓

**Gate does NOT fire on Pattern B targets:**
- Q21 `How many spiders` — multi-word ✓
- Q23 `How many agents do we have` — multi-word ✓
- Q26 `How many spiders do we have` — multi-word ✓

### §4.2 — Anchor resolution mechanism — v2 (Rigby SIGN Q2 reconciled)

**Post-SIGN decision**: **Strategy A curated map + Strategy C log-only
miss fallback**. Rigby Q2 verified via `kb_tool.semantic_search`(README):
short/common filename stems (README, INDEX) surface across many
non-canonical Documents, so Strategy B (dynamic Document.file_path
lookup) has a real over-match risk — a bare `README` query cannot be
uniquely resolved to a canonical doc. Strategy A + log-only miss preserves
auditability + Chris D5 distinct-mechanism per class.

**Strategy A curated map (`_LITERAL_FILENAME_ANCHORS`)** — initial 6 entries:

```python
_LITERAL_FILENAME_ANCHORS = {
    # Canonical-key → file_path
    # Keys are canonicalized (lowercase, `-` → `_`, `.md` stripped)
    'platform_inventory':       'docs/PLATFORM_INVENTORY.md',
    'platform_what_it_is':      'docs/PLATFORM_WHAT_IT_IS.md',
    'knowledge_pipeline':       'docs/KNOWLEDGE_PIPELINE.md',
    'engineering_playbook':     'docs/ENGINEERING_PLAYBOOK.md',
    '00_start_next_session':    '00-START-NEXT-SESSION.md',
    'claude':                   'CLAUDE.md',
}
```

**Canonicalization** (`_canonicalize_literal_filename_token`):
1. `strip()` whitespace
2. `.lower()`
3. `re.sub(r'\.md$', '', ...)` — strip trailing `.md`
4. `.replace('-', '_')` — normalize hyphens to underscores

Resolution: input query → canonicalize → look up in
`_LITERAL_FILENAME_ANCHORS` → if hit, return canonical `file_path`; if
miss, return `None` (Strategy C log-only path).

**Strategy C — structured "miss" log**:

```python
if not resolved:
    logger.info(
        "[S2828_PATTERN_D_MISS] gate fired but no curated anchor "
        "matched. token=%r canonicalized=%r pattern_index=%d. "
        "Add to _LITERAL_FILENAME_ANCHORS if this is a canonical doc.",
        query[:200], canonicalized, matched_pattern_index,
    )
```

This log surfaces frequent-but-uncurated hits so future arcs can
graduate them into the map deliberately — no runtime resolution to
random Documents (avoids Strategy B's over-match risk).

**Anchor map wiring invariants** (per pytest):
- Every entry's `file_path` value MUST resolve to a real
  `Document.file_path` (mirrors Pattern C anchor-defect prevention).
- Every entry's canonicalized key MUST match a canonicalization of the
  entry's basename (self-consistency).

**Post-Pattern-D refactor note**: Strategy C's log-only path is a
minimal artifact; the shared "pointer-intent registry" primitive (Chris
D-Q3 forward-carry) will subsume this when it lands. Do NOT extend
Strategy C into runtime resolution mid-arc.

### §4.3 — Per-regex bonus tiers + composition — v2 (Rigby SIGN Q3/Q4 reconciled)

**Post-SIGN decision**: **Strategy 3-B — per-regex bonus tiers with
per-pattern Chris D-Q1 sweep discipline.** Rigby Q3 DISAGREED with the
v1 flat-bonus approach (3-A) on the grounds that a single +0.32ish
bonus is a "big hammer" that can dominate legitimate content on false
fires; gate patterns do not carry equal deterministic-intent signal.
Rigby Q4 additionally rejected "force rank 1 for literal queries" on
tool-run evidence that even literal `00-START-NEXT-SESSION` has a
0.7098-similarity topic competitor (handoff talking about the target)
that COULD be a legitimate winner in embedding space.

**Adopted mechanism**: bonus size is proportional to gate certainty; per
each of P0-P3 pattern types, run a per-gate sweep + pick the smallest
value that converts intended positives while preserving negative controls.

**Per-regex bonus tiers (`_LITERAL_FILENAME_INTENT_BONUS`)** — values
TBD post-implementation-time sweep. Design shape:

```python
_LITERAL_FILENAME_INTENT_BONUS = {
    # Ordered by intent-signal determinism (strongest → weakest)
    'P0_md_extension':   None,  # sweep-derived; upper ceiling ~0.35
    'P1_uppercase_snake': None,  # sweep-derived; upper ceiling ~0.20
    'P2_hyphen_caps':     None,  # sweep-derived; upper ceiling ~0.35 (Q20 case)
    'P3_numeric_snake':   None,  # sweep-derived; upper ceiling ~0.10 (Q28 already wins natively; low bonus is neutral)
}
```

**Design rationale for per-regex tiers**:
- **P0** (`.md` extension) — user typed a full filename with extension.
  Strongest intent signal. Bonus ceiling ~0.35 to convert CLAUDE.md-literal
  (gap +0.06) with safe headroom.
- **P1** (uppercase snake_case ≥2 segs) — Q24-shape query
  (`PLATFORM_INVENTORY`). Small gap +0.08 → smallest reliable will be
  under +0.15.
- **P2** (hyphenated ALL-CAPS ≥3 segs) — Q20-shape query
  (`00-START-NEXT-SESSION`). Large gap +0.31 → per-gate ceiling might
  be up to ~0.35 to convert Q20, but this MUST NOT fire on P1-shape
  false positives. Whole-string anchoring is load-bearing here.
- **P3** (numeric-prefix snake_case ≥3 segs) — Q28-shape query
  (`2701_docs_inventory_topology_audit`). Q28 already wins natively;
  bonus is neutral (applied to already-winning row). Lowest ceiling
  keeps false-fires on other numeric-prefix docs bounded.

**Sweep methodology per gate** (implementation-time, extends Chris D-Q1
S2827 discipline):

1. Instrument `search_embeddings` to accept a per-gate bonus override
   dict for testing.
2. For each `Pn` in `[P0, P1, P2, P3]`, sweep bonus values
   `[0.03, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]`:
   - Run each intended positive for this gate (Q20 → P2; Q24 → P1;
     CLAUDE.md → P0; Q28 → P3).
   - Run all 14 documented negative controls (§5 below).
   - Record per-value: positive conversion count, negative gate over-fire
     count.
3. Per gate, select the **smallest value** where:
   - All intended positives for this gate convert to rank 1 (or, for
     Q28: preserve rank 1).
   - No negative control causes a gate over-fire OR (if gate correctly
     fires on a negative-adjacent query) no rank-1 misattribution.
4. If the smallest reliable value for a gate exceeds a design ceiling
   (P0/P2: 0.35; P1: 0.20; P3: 0.10), the design ceiling wins and the
   corresponding intended positive is NOT converted this arc — report the
   actual outcome per Chris D-Q1 discipline (do not tune to hit projected
   number).
5. Record full per-gate sweep tables + margins in §7 measurement
   evidence (post-implementation).

**Chris D3 retrieval-integrity preserved (Rigby Q4)**: bounded bonus is
NOT rank-1 force-pin. The anchor is INJECTED into the pool at the
retrieval layer (same as Pattern C), and the bonus is capped per gate.
If a topic competitor has raw similarity high enough to still win under
the capped bonus (e.g., 0.7098 top-1 vs 0.3979 anchor + 0.35 = 0.7479
still just wins), Pattern D does not override. This is architecturally
identical to Pattern C's N4 case (topic competitor legitimately wins).

**Composition** (mirrors Pattern C additive stack at
`core/rag_integration.py:539`):

```python
effective_similarity = (
    similarity
    + count_intent_bonus       # Pattern B (0.0 unless Pattern B fires)
    + self_ref_intent_bonus    # Pattern C (0.0 unless Pattern C fires)
    + literal_filename_bonus   # Pattern D — per-gate value (0.0 unless Pattern D fires)
)
```

Three bonuses are architecturally orthogonal by design — Pattern D
whole-string anchoring makes it disjoint from Pattern B/C multi-word
patterns. Additive shape preserves compositional invariant per Pattern
C S2827 §6.

**Zero-inflation of Q28**: when Pattern D gate fires on Q28 AND anchor
resolution succeeds AND the anchor chunk is already in the natural
oversample pool (Q28 wins natively at sim 0.5973), the injection
dedupe (mirrors Pattern C `injected_chunk_ids` set) skips synthetic
injection; the P3-tier bonus applies to the naturally-retrieved row
which was already at rank 1. Effect: rank 1 preserved; effective
similarity increases by P3 bonus; no false-rank promotion of unrelated
docs. This is the tolerated "gate over-fires on Q28" case (§3.3).

### §4.4 — Drift re-mask WARN (`[S2828_PATTERN_D_DRIFT]`)

Mirrors S2826 Pattern B + S2827 Pattern C drift discipline. Emitted when:
- LITERAL-FILENAME intent gate fires
- Anchor resolution succeeds (map hit)
- BUT resolved anchor's Document is not in the returned pool AND not in
  the injected chunks (either `status=archived` filter drop, or missing
  Document row entirely).

Log line:
```
[S2828_PATTERN_D_DRIFT] literal_filename_intent_active=True but
resolved anchor is not in the returned pool.
resolved=<file_path> query=%r include_superseded=%s.
Check Document.status='processed' for this path;
future metadata drift may silently re-mask Pattern D.
```

Companion to `[S2826_PATTERN_B_DRIFT]` + `[S2827_PATTERN_C_DRIFT]`. Same
`sync_docs_index_to_documents` drift root cause per S2826 §5.2 fold; the
v0.9 Playbook candidate (sync-update-path-completeness) protects all 3
mechanisms simultaneously.

### §4.5 — Diagnostic contract (mirrors Pattern C)

Per-row response dict additions (post-composition, alongside existing
Pattern B/C fields at `core/rag_integration.py:580-594`):

```python
'literal_filename_intent_bonus': <float>,   # 0.0 unless this row is anchor
'literal_filename_anchor_key':   <str|None>,  # curated map key
'literal_filename_matched_pattern_index': <int|None>,  # 0..3
'literal_filename_injected': <bool>,  # True if fetched via anchor injection
```

Top-level fields updated:
- `intent_gate_name`: extended to `'literal_filename'` when Pattern D fires
- `intent_gate_fired`: True when any of {count, self_reference,
  literal_filename} fires

**Ordering when multiple gates might fire simultaneously**: per §4.1
overlap analysis, no query hits >1 gate. If a future regex change
introduces overlap, `intent_gate_name` follows precedence order:
`count > self_reference > literal_filename` (arbitrary; documented for
determinism). Bonuses still compose additively regardless.

### §4.6 — Pytest coverage (mirrors `test_s2827_pattern_c_self_reference_gate.py`)

New test file: `tests/unit/test_s2828_pattern_d_literal_filename_gate.py`.

Cases:
- **Positive gate-fire** (10 cases): Q20, Q24, CLAUDE.md,
  PLATFORM_INVENTORY.md, KNOWLEDGE_PIPELINE, ENGINEERING_PLAYBOOK,
  claude.md (lowercase), Claude.MD (mixed case), ADR-0130,
  2701_docs_inventory_topology_audit
- **Negative gate-hold** (14 cases): Pattern C queries (Q14-Q17),
  Pattern B queries (Q21/Q23/Q26), natural-language filename mentions
  (`open CLAUDE.md`, `the PLATFORM_INVENTORY doc`), single-word
  ambiguous (`spider`, `agent`), Pattern C literal-fallout (`start`,
  `where do I start`), semantic-general (`add a new spider`)
- **Q28 no-perturb invariant** (1 case): gate fires, but natural
  rank-1 winner is preserved
- **Wiring invariants** (6 cases): pattern↔anchor sync check,
  anchor path defect prevention (all mapped paths resolve in Document),
  return-type tuple, dedup on injection, multi-pattern-anchor consistency,
  Pattern C/D gate exclusion (mutual disjoint check)

Target coverage: ≥30 cases.

---

## §5 — Negative controls — v2 (Rigby SIGN Q5b expanded coverage)

Rigby Q5b caution flag: negative controls must expand proportionally
with mechanism accretion. v2 expands from 11 rows to 20 rows explicitly
covering (a) filename-like-but-not-canonical tokens (Rigby's tool_run #3
evidence: `README` surfaces across many non-canonical docs) and (b) literal
filenames embedded in natural language (existing whole-string `^...$`
invariant load-bearing).

| id | query | expected gate | expected behavior |
|---|---|---|---|
| N1 | `add a new spider` | none | natural rank (Pattern C precedent N1) |
| N2 | `how many spiders` | count (Pattern B) | Pattern B behavior unchanged |
| N3 | `morning brief workflow` | none | natural rank |
| N4 | `where do I start` | self_reference (Pattern C) | Pattern C behavior unchanged |
| N5 | `project rules for spiders` | self_reference (Pattern C) | Pattern C behavior unchanged |
| N6 | `spider` | none | ambiguous — natural rank (Q25 case) |
| N7 | `open CLAUDE.md and check the rules` | none | multi-word — must NOT fire (whole-string invariant) |
| N8 | `the PLATFORM_INVENTORY doc has counts` | none | multi-word — must NOT fire |
| N9 | `how do I use PLATFORM_INVENTORY` | none | multi-word — must NOT fire |
| N10 | `platform` | none | too generic — must NOT fire |
| N11 | `README` | none (single-word ALL-CAPS ≤1 seg) | P1 requires 2+ segments — must NOT fire |
| N12 | `docs/CLAUDE.md` (path-form) | none | P0 whole-string requires bare filename, no `/` — must NOT fire |
| N13 | `2701_docs_inventory_topology_audit` (Q28 no-perturb) | literal_filename fires (P3) | Gate fires; anchor already at rank 1 natively; P3 bonus applied additively; **rank 1 preserved** |
| N14 | `SESSION_2827` (curated-map miss) | literal_filename fires (P1) | Gate fires; anchor resolution MISSES (not in curated map); **Strategy C log-only path — no synthetic resolution**; natural retrieval unchanged |
| N15 | `INDEX` (Rigby-flagged filename stem — README-shape) | none | P1 requires 2+ segments — must NOT fire |
| N16 | `README.md` (Rigby-flagged common stem) | literal_filename fires (P0) | Gate fires (`.md` extension P0); curated-map has NO `readme` entry (README is not a Pattern D canonical target); **Strategy C log-only path**; natural retrieval unchanged. Verifies README does not incorrectly resolve to a non-canonical Document. |
| N17 | `See the KNOWLEDGE_PIPELINE for details` | none | multi-word — must NOT fire (whole-string invariant) |
| N18 | `ADR-0130` (2-segment hyphenated) | none | P2 requires 3+ hyphen segments — must NOT fire |
| N19 | `platform_inventory` (lowercase snake_case) | none | P1 requires uppercase — must NOT fire; user should type canonical case OR use Pattern C semantic pointer |
| N20 | `SESSION_2827_PATTERN_C` (uppercase snake_case ≥2 segs, curated miss) | literal_filename fires (P1) | Gate fires; anchor resolution MISSES; **Strategy C log-only path**; natural retrieval unchanged. Common case: user typos a handoff name — verifies non-map fires do not degrade retrieval. |

**Chris D3 retrieval-integrity check**: for N7/N8/N9/N12/N17, natural
language OR path-form that INCLUDES a filename token must NOT trigger
Pattern D. Whole-string `^`/`$` anchors in P0-P3 handle this. Any
future author considering substring-relaxation must re-route through
Rigby SIGN + Chris D-verdict (§4.1 load-bearing invariant).

**Strategy C log-only coverage**: N14/N16/N20 verify the "gate fires
but curated map misses" path. Design invariant: Strategy C NEVER
resolves to a non-canonical Document; the log line is diagnostic-only.
Pytest asserts natural retrieval order is UNCHANGED between
gate-fires-with-miss and gate-does-not-fire cases.

---

## §6 — Measurement plan

### §6.1 — Pre-implementation (this doc, §3.2)

Recorded above:
- Q20 anchor sim 0.3979 vs top-1 0.7098 → gap +0.3119
- Q24 anchor sim 0.4751 vs top-1 0.5570 → gap +0.0819
- CLAUDE.md-literal anchor sim 0.5363 vs top-1 0.5967 → gap +0.0604
- Q28 anchor at rank 1 natively (0.5973)

### §6.2 — Post-implementation

Following S2827 §5 shape:

**§6.2.1 Per-gate bonus sweep tables (Strategy 3-B Rigby-reconciled)** —
for EACH of P0/P1/P2/P3 gates, sweep bonus values
`[0.03, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]`, record:
- Positive conversions specific to that gate: P0 → CLAUDE.md; P1 → Q24;
  P2 → Q20; P3 → Q28 (no-perturb).
- Negative gate over-fires across all 20 negative controls (§5).
- Per-gate margins (smallest bonus that flips + max non-flip).

Select smallest reliable value per gate. If per-gate design ceiling
(P0/P2: 0.35, P1: 0.20, P3: 0.10) is exceeded, ceiling wins + intended
positive is NOT converted (Chris D-Q1 discipline).

**§6.2.2 Per-query positive evidence** — for each converted case,
record: anchor natural in pool?, injected?, orig sim, bonus, effective
sim, final rank.

**§6.2.3 Negative controls** — 14 rows from §5 with gate-fire outcome.

**§6.2.4 Pattern B + C regression check** — smoke test `How many
spiders` + `where do I start` post-Pattern-D; must return same rank-1
files.

**§6.2.5 Full 18-row Phase-0.5 re-measurement** — expected 10/18 →
12/18 = 66.7%. If measurement diverges from projection, report actual
(per Chris D-Q1 discipline; do not retune to match projection).

**§6.2.6 Pytest coverage** — full run of `test_s2828_pattern_d_literal_filename_gate.py` + Pattern B/C tests as regression.

### §6.3 — Corpus baseline preservation

Per Chris D-Q2 S2827: post-corpus-correction 18-row corpus is the
authoritative baseline. Pattern D re-measurement MUST NOT rewrite corpus
labels. Q20/Q24 labels are already correct post-S2827 repair; no further
corpus edit anticipated.

---

## §7 — Chris D-verdict routing (post-Rigby-reconciliation v2)

Structure mirrors Pattern C §7 D-questions. Rigby joint SIGN cycle
COMPLETED 2026-07-19; refinements applied to §0/§4.1/§4.2/§4.3/§5.
Joint Claude+Rigby AGREE on R1/R2/R3/R4/R5 per S2753 discipline.
Route the following D-questions to Chris:

- **D-Q1** Ratify per-regex bonus sweep methodology + per-gate design
  ceilings (P0/P2: 0.35, P1: 0.20, P3: 0.10)? Chris D-Q1 S2827 discipline
  ("smallest reliable adjustment; record margins; do not tune to hit
  projected numbers") extended to per-gate scope in v2 per Rigby Q3
  reconciliation.
- **D-Q2** Ratify Strategy A curated map + Strategy C log-only-miss
  fallback (§4.2)? Confirm no Strategy B dynamic Document.file_path
  lookup.
- **D-Q3** Ratify preserving Chris D3 "retrieval must prove retrieval"
  invariant for literal-filename queries per Rigby Q4 reconciliation
  (bounded per-gate bonus; NOT rank-1 force-pin)?
- **D-Q4** Ratify tolerating Pattern D gate over-firing on Q28
  (`2701_docs_inventory_topology_audit`) since Q28 wins natively and
  the P3-tier bonus is applied additively without perturbation?
- **D-Q5** Ratify shipping CLAUDE.md-literal (not a Phase-0.5 corpus
  row) as an in-scope Pattern D target, per Chris D-Q4 S2827 explicit
  naming ("literal-filename queries (Q20 + explicit CLAUDE.md /
  00-START-NEXT-SESSION literal) belong in Pattern D")?
- **D-Q6** Ratify Rigby fold persisted BEFORE ship (§0.1) as
  `same_pr_mitigatable`, with per-regex tiers as the mitigation? Or
  reclassify as `future_trigger`?
- **D-Q7** Ratify atomic PR sequencing per S2827 D-Q5 pattern:
  implement + measure → atomic PR → close S2828 → open post-Pattern-D
  "pointer-intent registry" primitive extraction as separate Chris
  D-Q3 forward-carry evaluation arc?

---

## §7.5 — Post-implementation measurement evidence (2026-07-19, verbatim)

### §7.5.1 — Chris D-Q1 per-gate sweep (coarse [0.03..0.35] → fine [smallest..0.10])

Sweep applied one gate at a time (other gates held at 0.0). Positive =
target anchor at rank 1 in top-5 with production settings
(`similarity_threshold=0.3`, `include_superseded=False`). Negatives = all
20 rows from §5 checked for regression at each sweep value.

**Coarse per-gate sweep** — bonus values `[0.03, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]`:

| Gate | v=0.03 | v=0.05 | v=0.10 | v=0.15 | v=0.20 | v=0.25 | v=0.30 | v=0.35 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| P0 `.md` (CLAUDE.md) | ✗ | ✗ (rank 4) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| P1 uppercase snake (PLATFORM_INVENTORY) | ✗ | ✗ | ✓ | ✓ | ✓ | (over ceiling) | (over) | (over) |
| P2 hyphen caps (00-START-NEXT-SESSION) | ✗ | ✗ | ✗ | ✗ | ✗ (rank 4) | ✗ (rank 3) | ✗ (rank 2) | ✓ |
| P3 numeric snake (Q28) | ✓ (natural) | ✓ | ✓ | (over) | (over) | (over) | (over) | (over) |

All values checked against 20 negative controls: **0 regressions at every
tested value**. The regex-narrow whole-string gate is the primary
guardrail; bonus size does not cause over-fires.

**Fine-grained per-gate sweep** — narrowed to the smallest-flip vicinity:

| Gate | v=0.03 | v=0.05 | v=0.06 | v=0.07 | v=0.08 | v=0.09 | v=0.10 | v=0.31 | v=0.32 | v=0.33 | v=0.35 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| P0 CLAUDE.md — anchor rank | — | 4 | 2 | **1** | 1 | 1 | 1 | — | — | — | — |
| P0 CLAUDE.md — anchor eff sim | — | 0.5863 | 0.5963 | **0.6063** | 0.6163 | 0.6263 | 0.6363 | — | — | — | — |
| P1 PLATFORM_INVENTORY — anchor rank | — | — | — | 4 | 2 | **1** | 1 | — | — | — | — |
| P1 PLATFORM_INVENTORY — anchor eff sim | — | — | — | 0.5451 | 0.5551 | **0.5651** | 0.5751 | — | — | — | — |
| P2 00-START-NEXT-SESSION — anchor rank | — | — | — | — | — | — | — | 2 (margin −0.0019) | **1** | 1 | 1 |
| P2 00-START-NEXT-SESSION — anchor eff sim | — | — | — | — | — | — | — | 0.7079 | **0.7179** | 0.7279 | 0.7479 |

### §7.5.2 — Selected values + margins (Chris D-Q1 acceptance evidence)

| Gate | Selected | First failing below | Ceiling | Headroom | Neg regs at sr | Notes |
|---|:-:|:-:|:-:|:-:|:-:|---|
| P0 `.md` | **0.07** | 0.06 (rank 2) | 0.35 | +0.28 | 0/20 | CLAUDE.md converts cleanly; large headroom |
| P1 uppercase snake | **0.09** | 0.08 (rank 2) | 0.20 | +0.11 | 0/20 | PLATFORM_INVENTORY converts cleanly |
| P2 hyphen caps | **0.32** | 0.31 (rank 2, margin −0.0019) | 0.35 | **+0.03** | 0/20 | Q20's +0.31 raw gap is the tightest observed; sits close to ceiling |
| P3 numeric snake | **0.03** | — (Q28 wins natively; bonus is no-op via curated-map MISS path) | 0.10 | +0.07 | 0/20 | Selected as smallest tested value; effectively neutral |

**Chris D-Q1 compliance**:
- Smallest reliable per gate recorded ✓
- Winning margin (headroom to ceiling) recorded ✓
- First failing value below sr recorded ✓
- Highest tested value = 0.35 across all gates ✓
- No ceiling raised to achieve conversion ✓
- All selected values ≤ their ceiling; enforced by pytest
  `test_selected_bonuses_do_not_exceed_ceilings`

### §7.5.3 — Negative control run at selected values

All 20 controls per §5 — 0 regressions:

- Pattern B queries preserved: `how many spiders` / `How many agents do we have` → `docs/PLATFORM_INVENTORY.md` at rank 1 (gate=count).
- Pattern C queries preserved: `where do I start` / `start here` /
  `project rules` → correct anchors at rank 1 (gate=self_reference).
- Whole-string invariant holds: `open CLAUDE.md and check the rules`,
  `the PLATFORM_INVENTORY doc has counts`, `See the KNOWLEDGE_PIPELINE
  for details`, `docs/CLAUDE.md` — gate=None, natural retrieval.
- Curated-map MISS path proven: `SPIDER_NETWORK` and `README.md` both
  fire `gate=literal_filename` with `[S2828_PATTERN_D_MISS]` INFO log
  and natural retrieval unchanged (no anchor injection).
- Single-word / lowercase / 2-seg-hyphen: `README`, `INDEX`, `ADR-0130`,
  `platform_inventory` — gate=None, natural retrieval.
- Q28 no-perturb (Chris D-Q4): `2701_docs_inventory_topology_audit`
  fires P3, MISS path (no curated map entry), rank 1 preserved
  natively.

### §7.5.4 — Full 18-row Phase-0.5 re-measurement (post-Pattern-D)

| qid | query | expected strict | top-1 | gate | hit |
|---|---|---|---|---|:-:|
| Q9 | Can routing be inferred from the query alone? | PHASE_0/RECOMMENDATION_PHASE0_SUMMARY.md | PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md | None | ✗ (CONCEPTUAL — future arc) |
| Q10 | What does Documentation currently include? | docs/canon/INDEX.md | 2001_event_integration_architecture… | None | ✗ (DISCOVERY — future arc) |
| Q11 | Which tools already support it? | docs/PLATFORM_INVENTORY.md | handoffs/PA_LAYER1_SURFACE_MAP.md | None | ✗ (DISCOVERY — future arc) |
| Q12 | Which recurring tasks should belong to Documentation? | docs/topics/employee-os.md | 1901_authority_enforcement… | None | ✗ (CONCEPTUAL — future arc) |
| Q13 | How do we determine WHICH retrieval substrate… | PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md | SESSION_2821_SEMANTIC_RETRIEVAL_EVAL… | None | ✗ (CONCEPTUAL — future arc) |
| **Q14** | the next session start doc | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | self_reference | **✓** (Pattern C) |
| **Q15** | where do I start | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | self_reference | **✓** (Pattern C) |
| **Q16** | start here | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | self_reference | **✓** (Pattern C) |
| **Q17** | project rules | CLAUDE.md | CLAUDE.md | self_reference | **✓** (Pattern C) |
| Q18 | add a new spider to the network | docs/AGENTS_REFERENCE.md | docs/plans/CLAUDE_CONTEXT_SYSTEM_PACK.md | None | ✗ (PROCEDURAL — future arc) |
| **Q19** | Group 2700 T1 audit | 2701_docs_inventory_topology_audit.md | 2701_docs_inventory_topology_audit.md | None | **✓** (natural) |
| **Q20** | 00-START-NEXT-SESSION | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | **literal_filename** | **✓** (Pattern D P2, S2828 conversion) |
| **Q21** | How many spiders | docs/PLATFORM_INVENTORY.md | docs/PLATFORM_INVENTORY.md | count | **✓** (Pattern B) |
| **Q22** | Phase-0.5 router advisory-only pilot | PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md | PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md | None | **✓** (natural) |
| **Q23** | How many agents do we have | docs/PLATFORM_INVENTORY.md | docs/PLATFORM_INVENTORY.md | count | **✓** (Pattern B) |
| **Q24** | PLATFORM_INVENTORY | docs/PLATFORM_INVENTORY.md | docs/PLATFORM_INVENTORY.md | **literal_filename** | **✓** (Pattern D P1, S2828 conversion) |
| **Q26** | How many spiders do we have | docs/PLATFORM_INVENTORY.md | docs/PLATFORM_INVENTORY.md | count | **✓** (Pattern B) |
| **Q28** | 2701_docs_inventory_topology_audit | 2701_docs_inventory_topology_audit.md | 2701_docs_inventory_topology_audit.md | **literal_filename** | **✓** (natural + Pattern D no-perturb via P3 MISS path) |

**STRICT TOP-1: 12/18 = 66.7%** (up from S2827's 10/18 = 55.6%; +2
conversions from Pattern D). Matches projection.

### §7.5.5 — Pattern B + Pattern C regression check

| Query | Expected | Top-1 | Status |
|---|---|---|---|
| How many spiders | docs/PLATFORM_INVENTORY.md | docs/PLATFORM_INVENTORY.md | ✓ Pattern B unchanged |
| How many agents do we have | docs/PLATFORM_INVENTORY.md | docs/PLATFORM_INVENTORY.md | ✓ Pattern B unchanged |
| where do I start | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | ✓ Pattern C unchanged |
| start here | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | ✓ Pattern C unchanged |
| the next session start doc | 00-START-NEXT-SESSION.md | 00-START-NEXT-SESSION.md | ✓ Pattern C unchanged |
| project rules | CLAUDE.md | CLAUDE.md | ✓ Pattern C unchanged |

No regression. Pattern B COUNT bonus and Pattern C SELF_REFERENCE
injection/bonus compose additively without perturbing each other.

### §7.5.6 — Pytest coverage

**95/95 PASSING** (`tests/unit/test_s2828_pattern_d_literal_filename_gate.py`
61 tests + `tests/unit/test_s2827_pattern_c_self_reference_gate.py` 34
tests, run together as regression):
- 10 positive gate-fire cases (Q20/Q24/CLAUDE.md + curated map coverage)
- 3 miss-path cases (README.md, SPIDER_NETWORK, Q28)
- 20 negative gate-hold cases (mirror §5)
- 9 canonicalization spec cases (Chris D-Q2 spec)
- 13 cross-mechanism disjointness cases (Pattern B/C/D exclusion)
- 5 wiring invariants (pattern↔key sync, ceilings not exceeded,
  canonicalized keys, whole-string anchoring)
- 6 whole-string invariant regression samples (LOAD-BEARING)
- Pattern C regression: 34/34 continues to pass

### §7.5.7 — Injection diagnostics summary

All Pattern D positives that flip to rank 1 have full diagnostic
provenance in the returned dict:
- `intent_gate_name='literal_filename'`
- `literal_filename_gate_name` = P0/P1/P2/P3 identifier
- `literal_filename_anchor_key` = curated-map key
- `literal_filename_matched_pattern_index` = 0..3
- `literal_filename_injected` = True/False (injection vs already-in-pool)
- `literal_filename_intent_bonus` = per-gate selected bonus

Rigby fold (§0.1) is IN THE MECHANISM: gate certainty (P0 highest → P3
lowest) drives the per-gate bonus ceiling, not "literal" as a blanket
force-pin.

## §8 — Provenance

- **Predecessor**: Pattern C SELF_REFERENCE Candidate Injection
  (S2827, PR #3267, SHA `47f3650d1`)
- **Governing envelope**: `docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md`
- **Session brief**: `00-START-NEXT-SESSION.md` §S2828 Candidates
- **Anti-collapse guarantee**: Chris D5 + Chris D-Q3 S2827 — distinct
  mechanism per class; shared "pointer-intent registry" primitive
  extraction deferred to POST-Pattern-D when 3 shipped instances exist.

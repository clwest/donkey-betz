---
title: "Pattern C — SELF_REFERENCE Candidate Injection Design (Chris-ratified v2, measured)"
status: implemented + measured — awaiting merge
authority: DESIGN + IMPLEMENTATION + MEASUREMENT
session: 2827
generated: 2026-07-19
supersedes: none
merge_pr: (filled at merge)
merge_sha: (filled at merge)
related:
  - docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md   # Chris D1-D7 first cycle ratifying Pattern C shape
  - core/rag_integration.py                                                       # Pattern B sibling implementation (S2826)
  - docs/research/discovery_layer/PHASE_0_5/measurement_report.md                 # S2825 0/16 baseline, Chris R1 §2.1 metric
  - docs/research/discovery_layer/PHASE_0_5/corpus.json                           # 20 P1 rows; SELF_REFERENCE rows Q14/Q15/Q16/Q17/Q20
scope: |
  Design for Pattern C — narrow SELF_REFERENCE intent gate + canonical-anchor
  candidate injection into the embedding-lane retrieval pool. Sibling of
  Pattern B (COUNT) shipped at S2826 (`9c53ab880`); distinct mechanism per
  Chris D5. Targets 4 of 5 remaining SELF_REFERENCE misses on the unchanged
  16-row Phase-0.5 corpus (Q14/Q15/Q16/Q17 — Q20 deferred to Pattern D per
  Rigby SIGN Q3). Design routed through Rigby joint SIGN before implementation
  per Chris D6 sequence; SIGN reconciled v2 2026-07-19.
---

## §0 — Rigby joint SIGN reconciliation summary (2026-07-19)

Five SIGN questions routed; four DISAGREE + one AGREE-with-caveat.
Reconciled refinements applied to §4/§5/§6 below:

| SIGN Q | Rigby verdict | Refinement applied | Section |
|---|---|---|---|
| Q1 gate scope | DISAGREE | Removed 2 literal-filename patterns (→ Pattern D); tightened `session start` gate to require file-context word; accept singular/plural `rules?` | §4.1 |
| Q2 composition | DISAGREE | Dropped Strategy B (deterministic re-rank); adopted Strategy A (bounded +0.15 bonus + injection-if-missing, mirrors Pattern B) | §4.4 |
| Q3 Q20 boundary | DISAGREE | Q20 (literal-filename) removed from Pattern C scope → Pattern D backlog | §1, §6 |
| Q4 corpus defect | DISAGREE-framing-AGREE | Blocker; surfaced to Chris as D-verdict — recommend corpus label correction | §3.3, §7 |
| Q5 zoom-out | AGREE-with-caveat | Ship as-designed; extract shared "pointer-intent registry" primitive after Pattern D also ships; diagnostics include gate name + injection-fired boolean | §4.5, §7 |

Post-reconciliation joint agreement: Claude + Rigby AGREE on R1/R2/R3/R5;
AGREE on R4 framing (surface to Chris; recommend corpus label correction
as the lighter-touch resolution given the absence of a discoverable
strict-hit scoring script normalizing paths).

# Pattern C — SELF_REFERENCE Candidate Injection Design

## §1 — Purpose (post-reconciliation)

Convert **4 of the 5** SELF_REFERENCE Phase-0.5 corpus misses (Q14, Q15,
Q16, Q17) by injecting canonical anchor documents into the retrieval
candidate pool when a narrow SELF_REFERENCE intent gate fires. **Q20
(literal-filename `00-START-NEXT-SESSION`) is deferred to Pattern D
(literal-filename policy class) per Rigby SIGN Q3 + Chris D5 distinct-
mechanism-per-class discipline.**

The mechanism shape was approved by Chris D2 first cycle at S2826 and
sequenced by Chris D6: "Pattern C candidate-injection design routed
through Rigby SIGN before implementation."

## §2 — Chris constitutional constraints preserved

| # | Constraint | Source | Compliance in this design |
|---|---|---|---|
| C1 | "Retrieval must prove retrieval. Runtime injection cannot be used to erase a retrieval-layer failure." | Chris D3 first cycle S2826 | Pattern C injects INTO the candidate pool at retrieval-layer time (inside `search_embeddings`), BEFORE ranking — not at PA runtime after retrieval returns. |
| C2 | Distinct mechanism per policy class (COUNT / SELF_REFERENCE / INDEX_DISCOVERY / literal-filename / doc-class-precedence) | Chris D5 first cycle S2826 | Pattern C is scoped to SELF_REFERENCE; does not overlap Pattern B (COUNT) or Pattern D (INDEX_DISCOVERY / literal-filename). |
| C3 | Metadata layer inspection first | Chris D7 first cycle S2826 | §3.1 records the metadata layer state verification performed 2026-07-19 before authoring this design. |
| C4 | No `include_superseded=False` default relaxation | Chris D6 second cycle S2826 | Injection composes WITH the `include_superseded=False` filter — injected candidates are fetched under the same filter. |
| C5 | No universal runtime injection at PA level | Chris D3 first cycle S2826 | Design lives entirely inside `search_embeddings`; no PA-side change. |
| C6 | Bounded policy bonus with diagnostic surface | Chris D2 + Rigby Q4 refinement S2826 | §4.4 bounds the bonus with evidence; §4.5 defines the diagnostic contract mirroring Pattern B. |
| C7 | Negative controls verified | Chris D4 first cycle S2826 | §5 defines negative-control queries with expected non-fire behavior. |

## §3 — Pre-design evidence

### §3.1 — Metadata layer state (verified 2026-07-19 via ORM direct query)

Both canonical anchors are healthy in the Document table:

| file_path | status | class | canonical_authority | retrieval_boost | embeddings | Document.id |
|---|---|---|---|---|---|---|
| `00-START-NEXT-SESSION.md` | `processed` | `session_start` | `repo_canonical` | 1.5 | 16 | `cfcb7af1-2990-4669-8cc9-21a422692e10` |
| `CLAUDE.md` | `processed` | `system_config` | `repo_canonical` | 1.5 | 20 | `b2f2f3b1-e537-488b-b516-7ec8c7761c03` |
| `docs/00-START-NEXT-SESSION.md` | — | — | — | — | — | **NOT FOUND** |

Both real canonical anchors pass the S2826 metadata correctness bar. The
`docs/00-START-NEXT-SESSION.md` row is absent because the file lives at
repo root (`00-START-NEXT-SESSION.md`), not under `docs/`.

### §3.2 — Baseline retrieval evidence (post-metadata-repair, 2026-07-19)

Direct `search_embeddings` query for each of the 5 SELF_REFERENCE rows,
production settings (`similarity_threshold=0.4`, `include_superseded=False`,
no bypass flags), top-5 candidate pool:

| qid | query | Canonical anchor in top-5? | Top-1 file | Top-1 sim |
|---|---|:---:|---|:---:|
| Q14 | `the next session start doc` | ❌ | `docs/handoffs/SESSION_1187_UTILIZATION_RECON.md` | 0.682 |
| Q15 | `where do I start` | ❌ (empty top-5) | (none — all below 0.4) | — |
| Q16 | `start here` | ❌ | `docs/docs-pattern/05_start_here.md` | 0.442 |
| Q17 | `project rules` | ❌ | `docs/EOS_RULES.md` | 0.472 |
| Q20 | `00-START-NEXT-SESSION` | ❌ | `docs/handoffs/SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md` | 0.710 |

**Conclusion:** None of the 5 SELF_REFERENCE canonical anchors are present
in the candidate pool at production settings. A Pattern B-shape ranking
bonus alone cannot fix these — the target is not in the pool to boost.
Pattern C candidate injection is genuinely necessary, not a
"scorecard-optimization against a broken candidate layer" (per §5.1 fold
of S2826).

### §3.3 — Corpus path-label defect surfaced (§10.4 methodology candidate)

Q14/Q15/Q16/Q20 label their `known_correct_target_strict` as
`docs/00-START-NEXT-SESSION.md` — a path that does not exist. The actual
canonical file is `00-START-NEXT-SESSION.md` at repo root. Q17 correctly
labels `CLAUDE.md` (no `docs/` prefix), consistent with its actual
location. Q20 (literal-filename query) labels `docs/00-START-NEXT-SESSION.md`
strictly.

Implication for measurement: unless the strict-target check normalizes
paths (e.g., basename match or leading-directory tolerance), a Pattern C
injection of the real anchor (`00-START-NEXT-SESSION.md`) will NOT be
credited as a strict hit against the corpus label
`docs/00-START-NEXT-SESSION.md` for Q14/Q15/Q16/Q20.

This is either:
- (a) a corpus-label defect requiring Chris §10.4 methodology-back-to-SIGN
  ratification of a corpus correction (change `docs/00-START-NEXT-SESSION.md`
  → `00-START-NEXT-SESSION.md` in 4 rows), OR
- (b) a measurement-code normalization we haven't spotted; if the
  measurement matches on basename or normalizes leading directory, the
  design is unaffected.

Chris D5 sequence rule from S2826 open protocol step 20: "Preserve
unchanged 16-row corpus for re-measurement per Chris D5." This forbids
silent corpus edits. If (a) is the case, we need explicit Chris
ratification for the corpus correction before implementation.

**Routed as SIGN Q4 below.**

## §4 — Mechanism design (mirrors Pattern B shape from `core/rag_integration.py:60-100 + 242-296`)

### §4.1 — Narrow SELF_REFERENCE intent gate (`_detect_self_reference_intent`) — v2 (Rigby-reconciled)

Regex patterns (compiled `re.I`) — narrow, context-required:

```python
_SELF_REFERENCE_INTENT_PATTERNS = (
    # Start-doc pointer patterns (Q14, Q15, Q16)
    re.compile(r'\bwhere\s+do\s+I\s+start\b', re.I),                                    # Q15
    re.compile(r'\bstart\s+(here|next\s+session|new\s+session)\b', re.I),               # Q16 (tightened — `next`/`new` require `session`)
    re.compile(r'\b(the\s+)?(next\s+)?session\s+start\s+(doc|file|page|md)\b', re.I),   # Q14 (v2 — REQUIRED file-context word per Rigby Q1)
    # Rules-doc pointer patterns (Q17)
    re.compile(r'\bproject\s+rules?\b', re.I),                                          # Q17 (v2 — accepts singular + plural per Rigby Q1)
)
```

**v2 changes from v1 (per Rigby SIGN Q1 DISAGREE):**
- **REMOVED:** `\b00[-_]?start[-_]?next[-_]?session\b` (literal filename → Pattern D backlog)
- **REMOVED:** `\bclaude\.?md\b` (literal filename → Pattern D backlog)
- **TIGHTENED:** `session\s+start` now requires trailing file-context word (`doc|file|page|md`) — prevents false positive on generic "session start" mentions in handoff docs
- **BROADENED:** `project\s+rules` → `project\s+rules?` — accepts both singular and plural
- Result: 4 gate patterns (down from 6); scope reduced to Q14/Q15/Q16/Q17

**Design decisions preserved:**
- `\bstart\b` alone is deliberately NOT gated (false positive on any "start" verb). Required context: `here`/`next session`/`new session` or preceded by `where do I`.

### §4.2 — Canonical anchor map (`_SELF_REFERENCE_ANCHORS`) — v2

Pattern → anchor file_path mapping:

```python
_SELF_REFERENCE_ANCHORS = {
    'start_doc':     '00-START-NEXT-SESSION.md',   # real repo-root path (root, no docs/ prefix)
    'project_rules': 'CLAUDE.md',                  # real repo-root path (root, no docs/ prefix)
}

# Which pattern index maps to which anchor key
_PATTERN_TO_ANCHOR = {
    0: 'start_doc',      # where do I start
    1: 'start_doc',      # start (here|next session|new session)
    2: 'start_doc',      # session start (doc|file|page|md)
    3: 'project_rules',  # project rules?
}
```

**Path decision:** anchors are the REAL Document.file_path values. Corpus
label defect (§3.3) surfaces to Chris D-verdict; recommendation is corpus
label correction (change Q14/Q15/Q16/Q20 strict targets from
`docs/00-START-NEXT-SESSION.md` → `00-START-NEXT-SESSION.md` — 4-row
label-only edit; corpus content otherwise unchanged).

### §4.3 — Injection mechanism (fetch-and-merge)

Inside `search_embeddings` after existing filter chain and before
`order_by('distance')`:

```python
self_ref_intent_fires = _detect_self_reference_intent(query)  # returns tuple of matched anchor_keys
if self_ref_intent_fires:
    candidate_qs = qs.order_by('distance')[:max(limit * 3, limit)]
    chunks = list(candidate_qs.select_related('document'))
    # Fetch canonical anchor chunks by file_path, under the same qs filter chain
    injected_chunks = _fetch_self_reference_anchors(
        self_ref_intent_fires,          # tuple of matched anchor keys
        qs,                              # SAME filtered queryset (preserves include_superseded=False)
        exclude_chunk_ids={c.id for c in chunks},  # dedup
    )
    chunks = injected_chunks + chunks                    # injected first
elif authority_weighted or count_intent_active:
    # (existing S2826 Pattern B path)
    candidate_qs = qs.order_by('distance')[:max(limit * 3, limit)]
    chunks = list(candidate_qs.select_related('document'))
else:
    qs = qs.order_by('distance')[:limit]
    chunks = list(qs.select_related('document'))
```

`_fetch_self_reference_anchors(anchor_keys, qs, exclude_chunk_ids)`
returns 0-N DocumentEmbedding rows: for each anchor key, take the
highest-similarity chunk of the mapped file whose `document.status` +
`document.canonical_authority` pass the `qs` filter chain. Uses the SAME
query embedding for similarity (piggybacks on `pgvector.CosineDistance`
annotation) so the injected chunk carries a real similarity score, not a
synthesized one.

**Key invariant:** if an anchor's Document has `status='archived'` or is
otherwise filtered by `qs`, it is NOT injected. This preserves Chris D6
"no include_superseded relaxation" and mirrors the Pattern B drift-re-mask
protection.

### §4.4 — Bounded ranking composition — v2 (Strategy A per Rigby Q2 DISAGREE)

**Adopted: Strategy A — bounded bonus + injection-if-missing, mirrors
Pattern B shape.** Strategy B (deterministic re-rank) was rejected by
Rigby Q2 DISAGREE on the grounds that "retrieval is still a similarity
contest, nudged under gate, not replaced" — deterministic re-rank
overreaches Chris D2 "bounded policy bonus" language.

Mechanism:

```python
_SELF_REFERENCE_INTENT_BONUS = 0.15  # bounded; evidence-based initial
```

Composition (parallels Pattern B):
1. If `self_ref_intent_fires` returns non-empty:
   a. Oversample candidate pool via existing Pattern B code path
      (`limit * 3`) to give injected anchors room to compete on merit.
   b. For each mapped anchor key, fetch its highest-similarity
      DocumentEmbedding chunk under the SAME `qs` filter chain
      (`_fetch_self_reference_anchors`) using CosineDistance annotation
      against the query embedding.
   c. If the anchor chunk is already in the oversample pool: apply
      `+0.15` bonus to that row.
   d. If NOT in pool: inject as candidate with the real cosine similarity
      + `+0.15` bonus, marked `self_ref_injected=True`.
2. Sort final pool by `(similarity_score + self_ref_intent_bonus)` DESC,
   tie-break identical to Pattern B (`updated_at` DESC, `document.id`
   ASC, `chunk.id` ASC).
3. Truncate to `limit`.

**Bound rationale (v2):** §3.2 baseline shows top-1 non-canonical
similarities range 0.44–0.71 across Q14/Q15/Q16/Q17. Canonical anchor
raw similarities not yet measured (Rigby SIGN did not request pre-impl
measurement); +0.15 initial is a defensible starting point that
mirrors Pattern B's evidence-based +0.05 discipline (scaled up because
Pattern C's gate is narrower and the small-gap phenomenon is larger). If
implementation shows +0.15 insufficient for one or more Q14–Q17 rows,
tuning follows Pattern B's discipline: raise with evidence, not
speculation.

**Guard-rail for multi-anchor fires:** if a query matches both
`start_doc` and `project_rules` patterns (edge case; not observed in
Q14–Q17), inject both; sort by (sim + bonus); no artificial cap or bias.

### §4.5 — Diagnostic contract — v2 (per Chris D2 + Rigby Q5 caveat)

Per-row fields on each returned candidate:

| Field | Value on injected candidate | Value on non-injected |
|---|---|---|
| `intent_gate_fired` | `True` | `False` |
| `intent_gate_name` | `'self_reference'` | `None` |
| `self_ref_injected` | `True` | `False` |
| `self_ref_anchor_key` | e.g. `'start_doc'` | `None` |
| `self_ref_matched_pattern_index` | int 0-3 | `None` |
| `self_ref_intent_bonus` | `+0.15` (applied) | `0.0` |
| `original_pool_rank` | `None` (was not in original top-N) | int 1..N |

**Rigby Q5 caveat compliance:** the `intent_gate_fired`, `intent_gate_name`,
and `self_ref_injected` fields together let downstream consumers + tests
detect false-positive gate firing (gate fires but Q14–Q17 canonical NOT
retrieved) AND injection frequency (how often we inject vs boost-in-place).
This complements the drift-re-mask WARN (§4.6) which alerts only on the
"all anchors missing" boundary case.

### §4.6 — Drift re-mask WARN (mirror Pattern B `[S2826_PATTERN_B_DRIFT]`)

When `self_ref_intent_fires` fires but `_fetch_self_reference_anchors`
returns 0 candidates for ALL matched anchor keys:

```
[S2827_PATTERN_C_DRIFT] self_reference intent gate fired but NONE of the
mapped canonical anchors are retrievable under current filters.
anchor_keys=%s query=%r include_superseded=%s.
Check Document.status='processed' for %s; S2826 root-cause showed
sync_docs_index_to_documents update path may miss field refresh classes.
```

Protects Pattern C benefit from silent erosion via future metadata drift.

## §5 — Negative controls (per Chris D4) — v2

Queries that MUST NOT fire the SELF_REFERENCE intent gate (or, if the
gate fires, must NOT inject if anchors don't match the query intent):

| # | Query | Expected gate behavior | Reason |
|---|---|---|---|
| N1 | `add a new spider` | Gate does not fire | No SELF_REFERENCE regex match |
| N2 | `how many spiders` | Gate does not fire (COUNT domain — Pattern B territory) | No SELF_REFERENCE regex match |
| N3 | `morning brief workflow` | Gate does not fire | No SELF_REFERENCE regex match |
| N4 | `where do I start with a new spider` | **Gate FIRES** on `where do I start` — injects start_doc anchor as intended | Ambiguous case: query IS a start-doc pointer under most interpretations; anchor injection appropriate |
| N5 | `start the celery worker` | Gate does NOT fire on `start` alone (context required) | Pattern `\bstart\s+(here\|next\s+session\|new\s+session)\b` narrow gate |
| N6 | `project rules for spiders` | **Gate FIRES** on `project rules` — injects CLAUDE.md | Intended: `project rules` is pointer intent regardless of trailing "for X" |
| N7 | `what does the platform inventory list` | Gate does not fire | Distinct policy class (DISCOVERY / literal-filename per Chris D5) |
| N8 | `PLATFORM_INVENTORY` (literal filename) | Gate does not fire | Distinct policy class (literal-filename per Chris D5) |
| N9 | `session start reflection` | Gate does NOT fire (v2 — tightened `session start` requires `doc/file/page/md`) | Prevents false positive on "session start reflection" mentions in handoff docs |
| N10 | `00-START-NEXT-SESSION` (literal-filename Q20) | Gate does NOT fire in Pattern C (v2 — literal-filename pattern removed → Pattern D backlog) | Chris D5 distinct mechanism per class; Q20 = Pattern D target |
| N11 | `CLAUDE.md` (literal filename) | Gate does NOT fire in Pattern C (v2 — literal-filename pattern removed → Pattern D backlog) | Chris D5 distinct mechanism per class; = Pattern D target |

All negative controls codified as pytest cases before merge.

## §6 — Measurement plan — v2

1. Implement §4.1–§4.6 in `core/rag_integration.py` mirroring Pattern B
   structure.
2. Re-run baseline retrieval on Q14/Q15/Q16/Q17 — confirm each returns the
   canonical anchor at rank 1. (Q20 excluded from Pattern C scope; Pattern
   D target.)
3. Re-run negative controls N1–N11 — confirm no over-injection.
4. Re-run Pattern B smoke test — confirm no regression on COUNT queries.
5. Full 16-row Phase-0.5 corpus re-measurement.
6. Expected outcome (Chris ratifies R4 corpus label correction — RECOMMENDED
   path per joint Claude+Rigby agreement):
   6/18 → **10/18 = 55.6%** strict top-1 (4 Pattern C conversions:
   Q14/Q15/Q16/Q17).
7. Expected outcome (Chris rejects R4 corpus correction and does not ratify
   measurement-normalization as valid):
   6/18 → **7/18 = 38.9%** (only Q17 converts strictly because Q14/Q15/Q16
   corpus labels remain `docs/00-START-NEXT-SESSION.md` non-existent path).
8. Q20 conversion depends on Pattern D (future arc) + same corpus label
   correction as Q14/Q15/Q16.

## §7 — Chris D-verdict routing

### §7.1 — Joint Claude+Rigby recommendation

**Ship Pattern C v2 (this document post-reconciliation) + ratify corpus
label correction in same PR.**

Pattern C v2 refinements (all Rigby-AGREE'd):
- 4 narrow gate patterns (Q14/Q15/Q16/Q17); no literal-filename patterns
- Strategy A bounded bonus (+0.15) + injection-if-missing
- Anchor map: 2 real repo-root files (`00-START-NEXT-SESSION.md`,
  `CLAUDE.md`)
- Full diagnostic contract per Chris D2 + Rigby Q5 caveat
- Drift-re-mask WARN per Rigby Q5 refinement

Corpus label correction:
- Change Q14/Q15/Q16/Q20 `known_correct_target_strict[0]` from
  `docs/00-START-NEXT-SESSION.md` → `00-START-NEXT-SESSION.md`
- Same for `known_correct_target_loose[0]`
- Q17 unchanged (already `CLAUDE.md` root-path)
- 4-row label-only edit; other corpus fields untouched
- Rationale: cleaner than relying on unfound strict-hit scoring script's
  path normalization; documents corpus label defect as §10.4-shape
  methodology repair; preserves S2825/S2826 measurement integrity going
  forward

Expected outcome: 6/18 → 10/18 = 55.6% strict top-1 (4 Pattern C conversions:
Q14/Q15/Q16/Q17).

### §7.2 — Chris D-verdict questions

Requesting yes/no verdicts on 5 discrete decisions:

**D-Q1:** Ratify Pattern C v2 design as authored (§4.1–§4.6 + §5 negative
controls + §6 measurement plan)? — implementation follows this design.

**D-Q2:** Ratify corpus label correction (Q14/Q15/Q16/Q20 strict + loose
targets change `docs/00-START-NEXT-SESSION.md` → `00-START-NEXT-SESSION.md`)
in same PR as Pattern C implementation? — alternative is to leave corpus
labels defective, in which case Pattern C converts Q17 only (1 row, not 4).

**D-Q3:** Ratify §7.1 forward-carry note re: extracting shared
"pointer-intent registry" primitive (Pattern B/C/D shared shape) as a
Playbook-v0.9-candidate discipline observation — trigger for codification
after Pattern D also ships (3 instances = §14.2 default two-trigger
threshold; would be third instance)?

**D-Q4:** Ratify §7.3 explicit forward-carry that Q20 (SELF_REFERENCE with
literal_identifier=True) belongs in future Pattern D scope + Q17's
`CLAUDE.md` literal query also belongs in Pattern D, preserving Chris D5
distinct-mechanism-per-class discipline?

**D-Q5:** Merge order — implement + ratify Pattern C first, then extract
shared registry primitive after Pattern D also ships, or refactor Pattern
B in same PR as Pattern C (scope creep; NOT recommended by joint
Claude+Rigby)?

### §7.3 — Pattern D forward-carry (documented per Chris D5)

Explicitly ceded from Pattern C to future Pattern D (literal-filename
policy class):
- Q20 corpus target (query `00-START-NEXT-SESSION`, literal_identifier=True)
- CLAUDE.md literal-filename queries (not present in current 16-row corpus
  but conventionally-adjacent)
- General literal-filename intent gate + anchor-by-name mechanism

Do NOT design Pattern D here. Design it in its own arc after Pattern C
implementation + measurement close.

<!-- §7 SIGN questions consolidated into §7.1/§7.2 above post-reconciliation;
Rigby verdicts recorded in §0 table + design body annotations. -->

## §7.5 — Chris D-verdicts + measured implementation evidence (2026-07-19)

### §7.5.1 — Chris D-verdicts (all RATIFIED with refinements)

- **D-Q1 YES** — with refinement: `+0.15` in the draft was a hypothesis, not a constitutional constant. Use the SMALLEST reliable adjustment that converts intended cases while preserving negative controls. Record tested alternatives + margins.
- **D-Q2 YES** — corpus label correction (Q14/Q15/Q16/Q20 `docs/00-START-NEXT-SESSION.md` → `00-START-NEXT-SESSION.md`) applied in same PR. Ground-truth repair, not benchmark tuning. Post-correction corpus is the authoritative baseline. Do NOT describe re-measurement as "unchanged-corpus."
- **D-Q3 YES** — forward-carry only; shared "pointer-intent registry" primitive documented as post-Pattern-D observation, not built in S2827.
- **D-Q4 YES** — literal-filename queries (Q20 + explicit `CLAUDE.md` / `00-START-NEXT-SESSION` literal) belong in Pattern D. Pattern C owns semantic pointer intent: "where to begin / where to continue / session-start guidance / project rules."
- **D-Q5 YES** — merge order: implement + measure Pattern C → atomic PR (Pattern C + corpus repair + design doc + tests) → close S2827 → open Pattern D as separate arc → NO Pattern B refactor in S2827.

### §7.5.2 — Bonus tuning evidence (Chris D-Q1 discipline — record tested alternatives + margins)

Baseline anchor-vs-competitor gaps measured 2026-07-19 22:25 PT:

| qid | query | anchor | anchor raw sim | top-1 non-anchor sim | gap |
|---|---|---|:-:|:-:|:-:|
| Q14 | `the next session start doc` | `00-START-NEXT-SESSION.md` | 0.4569 | 0.6816 (`SESSION_1187_UTILIZATION_RECON.md`) | +0.2247 |
| Q15 | `where do I start` | `00-START-NEXT-SESSION.md` | 0.2605 | 0.3843 | +0.1238 |
| Q16 | `start here` | `00-START-NEXT-SESSION.md` | 0.3146 | 0.4422 (`docs-pattern/05_start_here.md`) | +0.1276 |
| Q17 | `project rules` | `CLAUDE.md` | 0.3833 | 0.4723 (`docs/EOS_RULES.md`) | +0.0889 |

Static-bonus sweep — positive conversions + negative-control fire count for each tested value (production settings, `similarity_threshold=0.4`, `include_superseded=False`):

| Bonus | Q14 | Q15 | Q16 | Q17 | Positive conversions | Negative gate over-fires (self_reference on 8 non-target queries) |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0.05 | ✗ | ✓ | ✗ | ✗ | 1/4 | 0/8 |
| 0.10 | ✗ | ✓ | ✗ | ✓ | 2/4 | 0/8 |
| 0.15 | ✗ | ✓ | ✓ | ✓ | 3/4 | 0/8 |
| 0.20 | ✗ | ✓ | ✓ | ✓ | 3/4 | 0/8 |
| **0.23** | **✓** | **✓** | **✓** | **✓** | **4/4** | **0/8** |
| 0.25 | ✓ | ✓ | ✓ | ✓ | 4/4 | 0/8 |

**Selected value: `_SELF_REFERENCE_INTENT_BONUS = 0.23`** — smallest reliable adjustment meeting Chris acceptance (all 4 intended SELF_REFERENCE rows convert; all negative controls preserve at every tested value; gate narrowness makes bonus size irrelevant to negative control fires).

Note on N9/N10/N11 (`session start reflection`, `00-START-NEXT-SESSION`, `CLAUDE.md`): all 3 negative controls hold at every tested bonus because they are **regex-blocked at the gate**, not bonus-dependent — the gate genuinely does not fire, so the bonus value is a no-op for these queries.

### §7.5.3 — Per-query positive evidence (Chris acceptance requirement)

| qid | query | orig top-1 file | orig top-1 sim | anchor natural? | anchor injected? | orig sim | bonus | eff sim | final rank | gate name |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|
| Q14 | `the next session start doc` | `00-START-NEXT-SESSION.md` (after injection+bonus) | 0.4569 | False | True | 0.4569 | +0.23 | 0.6869 | **1** | self_reference |
| Q15 | `where do I start` | `00-START-NEXT-SESSION.md` (after injection+bonus) | 0.2605 | False | True | 0.2605 | +0.23 | 0.4905 | **1** | self_reference |
| Q16 | `start here` | `00-START-NEXT-SESSION.md` (after injection+bonus) | 0.3146 | False | True | 0.3146 | +0.23 | 0.5446 | **1** | self_reference |
| Q17 | `project rules` | `CLAUDE.md` (after injection+bonus) | 0.3833 | False | True | 0.3833 | +0.23 | 0.6133 | **1** | self_reference |

All 4 rows: anchor was ABSENT from natural top-5 (natural=False), anchor was INJECTED via `_fetch_self_reference_anchor_chunks` (injected=True), original cosine similarity carried through un-mutated, bounded +0.23 bonus applied, final rank 1.

### §7.5.4 — Negative-control results

| id | query | top-1 file | gate name | fired | injected? | verdict |
|---|---|---|---|:-:|:-:|:-:|
| N1 | `add a new spider` | `SESSION_1243_AUDIT_METHOD_4X_VALIDATED...` | None | False | False | ✓ |
| N2 | `how many spiders` | `docs/PLATFORM_INVENTORY.md` | count | True | False | ✓ (count gate expected — Pattern B) |
| N3 | `morning brief workflow` | `SESSION_1233_DAILY_COS_ARC_BUILD_OUT.md` | None | False | False | ✓ |
| N4 | `where do I start with a new spider` | `docs/roadmap/06-SPIDER-HEALTH.md` | self_reference | True | False | ✓ (semantic ambiguous case; gate fires as designed; SPIDER-HEALTH's raw similarity outranks anchor's raw+bonus — retrieval integrity preserved) |
| N5 | `start the celery worker` | `SESSION_1211_PHASE_B_EXTENSION_THREE_AGENTS.md` | None | False | False | ✓ |
| N6 | `project rules for spiders` | `CLAUDE.md` | self_reference | True | True | ✓ (semantic ambiguous case; pointer intent wins — user asking about project rules gets project rules doc) |
| N7 | `what does the platform inventory list` | `docs/PLATFORM_INVENTORY.md` | None | False | False | ✓ |
| N8 | `PLATFORM_INVENTORY` | `docs/research/platform/platform_constitutional_transition_review.md` | None | False | False | ✓ |
| N9 | `session start reflection` | `SESSION_2102_RAG_DOCUMENT_LOADING_INGESTION_CHUNKING_EMBEDDING_PIPELINE_AUDIT.md` | None | False | False | ✓ (v2 tightening — required file-context word) |
| N10 | `00-START-NEXT-SESSION` (literal) | `SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md` | None | False | False | ✓ (Pattern D forward-carry — literal filename NOT gated in Pattern C) |
| N11 | `CLAUDE.md` (literal) | `SESSION_2813_GROUP_2700_T3_HUMAN_PAIN.md` | None | False | False | ✓ (Pattern D forward-carry) |

**Injection frequency across all 15 tested queries:** gate fired 6× (Q14/Q15/Q16/Q17 + N4/N6); actual anchor injection performed 5× (anchor was not in original oversample pool). N4 injection returned anchor but topic-specific competitor outranked at +0.23 bonus — desired behavior per Chris "retrieval must prove retrieval" invariant.

### §7.5.5 — Full 18-row Phase-0.5 re-measurement (post-corpus-correction)

Corpus-correction denominator: 18 measurable rows (unchanged from S2825 harvest; Q27/Q28 aborted at T2 integrity stop; Q25 has strict target `null` — AMBIGUOUS excluded).

Corpus labels changed for Q14/Q15/Q16/Q20 strict + loose targets: `docs/00-START-NEXT-SESSION.md` → `00-START-NEXT-SESSION.md` (8 label edits total; content otherwise unchanged). This corpus is now the authoritative baseline going forward.

| Session | Strict top-1 hits | Delta | Mechanism |
|---|:-:|:-:|---|
| S2825 baseline (pre-metadata-repair) | 0/16 = 0.0% | — | none |
| S2826 (post-Pattern-B + metadata repair) | 6/18 = 33.3% | +6 | 3× Pattern B (COUNT) + 3× metadata repair alone |
| **S2827 (post-Pattern-C + corpus repair)** | **10/18 = 55.6%** | **+4** | **4× Pattern C (SELF_REFERENCE)** |

**Attribution of the 10 conversions:**

| qid | family | target | mechanism |
|---|---|---|---|
| Q14 | SELF-REFERENCE | `00-START-NEXT-SESSION.md` | **Pattern C** |
| Q15 | SELF-REFERENCE | `00-START-NEXT-SESSION.md` | **Pattern C** |
| Q16 | SELF-REFERENCE | `00-START-NEXT-SESSION.md` | **Pattern C** |
| Q17 | SELF-REFERENCE | `CLAUDE.md` | **Pattern C** |
| Q19 | IDENTITY | `2701_docs_inventory_topology_audit.md` (basename) | metadata repair (S2826) |
| Q21 | COUNT | `docs/PLATFORM_INVENTORY.md` | Pattern B (S2826) |
| Q22 | DISCOVERY | `ROUTER_SCAFFOLDING_DESIGN.md` (basename) | metadata repair (S2826) |
| Q23 | COUNT | `docs/PLATFORM_INVENTORY.md` | Pattern B (S2826) |
| Q26 | COUNT | `docs/PLATFORM_INVENTORY.md` | Pattern B (S2826) |
| Q28 | IDENTITY | `2701_docs_inventory_topology_audit.md` (basename) | metadata repair (S2826) |

Remaining 8 misses (deferred to future arcs per Chris D5 distinct-mechanism-per-class):

| Class | Rows | Deferred to |
|---|---|---|
| CONCEPTUAL | Q9, Q12, Q13 | Semantic-general (future arc) |
| DISCOVERY | Q10, Q11 | DISCOVERY policy class (future arc) |
| PROCEDURAL | Q18 | Semantic-general (future arc) |
| SELF-REFERENCE (literal-filename) | Q20 | **Pattern D** (next arc per Chris D-Q5) |
| IDENTITY (literal-filename) | Q24 | **Pattern D** (next arc per Chris D-Q5) |

Pattern B COUNT smoke test — no regression: `How many spiders` → top-1 `docs/PLATFORM_INVENTORY.md`, sim=0.5577, effective=0.6077, count_bonus=0.05, gate=count.

### §7.5.6 — Pytest coverage

New file: `tests/unit/test_s2827_pattern_c_self_reference_gate.py` — 34 tests, all PASSING.

Coverage:
- 12 positive gate-fire cases (Q14/Q15/Q16/Q17 verbatim + variations)
- 16 negative gate-hold cases (N1/N3/N5/N7/N8/N9/N10/N11 + variations + empty/whitespace)
- 6 wiring invariants (pattern↔anchor sync; anchor path defect prevention; return-type tuple; dedup; multi-anchor)

## §7.4 — Rigby SIGN verdicts (verbatim record, 2026-07-19)

- **Q1 (intent gate scope):** DISAGREE — remove literal-filename patterns; tighten `session start`; broaden `project rules?`. Applied → §4.1 v2.
- **Q2 (Strategy A vs B):** DISAGREE — Strategy B overreaches Chris D2; adopt Strategy A (bounded bonus + injection). Applied → §4.4 v2.
- **Q3 (Q20 boundary):** DISAGREE — Q20 belongs in Pattern D; CLAUDE.md literal same. Applied → §1, §5 N10/N11, §7.3.
- **Q4 (corpus defect):** DISAGREE-framing-AGREE — surface to Chris; recommend corpus label correction (lighter-touch than authoring a strict-hit scorer). Applied → §7.1/§7.2 D-Q2.
- **Q5 (zoom-out):** AGREE-with-caveat — ship as-designed; extract shared primitive after Pattern D also ships; ensure diagnostics detect false-positive gate firing AND injection frequency. Applied → §4.5 v2 + §7.1 forward-carry note.

Rigby tool_runs used to verify design claims: `search_docs` (3 calls),
`repo_tool.read_file` + `search` (multiple calls to S2826 handoff §6),
`kb_tool.semantic_search` (multiple calls verifying §3.2 baseline
retrieval on Q14–Q20 — confirmed canonical anchors absent from
production-settings candidate pool). Anti-rubber-stamp
`tool_runs`-non-empty check per S2777 rule PASSED.

## §8 — Provenance

- **Author:** Claude Code S2827
- **Ratification target:** Rigby joint SIGN → Claude+Rigby agreement →
  Chris D-verdict
- **Design references:**
  - `core/rag_integration.py:60-100` (Pattern B intent gate + patterns)
  - `core/rag_integration.py:242-296` (Pattern B composition + sort)
  - `core/rag_integration.py:397-427` (Pattern B drift-re-mask WARN)
  - S2826 handoff §4 (Chris D-verdicts)
  - S2826 handoff §7 (retrieval-failure diagnosis order — architectural
    conclusion)
  - S2825 measurement_report.md §2 (Chris R1 §2.1 metric definition)
- **Metadata evidence:** ORM direct query 2026-07-19 22:04 PT (§3.1
  table)
- **Baseline retrieval evidence:** live `search_embeddings` smoke
  2026-07-19 22:05 PT (§3.2 table)
- **Repo HEAD at design authoring:** `69162c819`

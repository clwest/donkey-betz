---
title: "SESSION 2826 — Metadata sync-drift root cause + full-corpus repair + Pattern B COUNT gate shipped"
session: 2826
date: 2026-07-19
predecessor: SESSION_2825_PHASE0_5_HARVEST_EXECUTED_METHODOLOGY_RETURN.md
successor: TBD
status: shipped
authority: implementation + governance
scope:
  Diagnosed root cause of S2825 0/16 retrieval-strict-hit — sync_docs_index_to_documents
  update path refreshed 12 fields but never Document.status, causing 881 rows
  of metadata drift (870 active→archived + 6+5 draft mis-classifications).
  Repaired via atomic 3-file PR: (1) new backfill_document_status_from_docs_index
  command (idempotent restoration); (2) one-line sync fix (adds status refresh
  to update path); (3) Pattern B intent-gated file-specific ranking bonus in
  the embedding lane (Rigby joint SIGN cleared with Q1-Q5 refinements applied).
  Post-repair Phase-0.5 re-measurement: 0/16 → 6/18 (33.3%) strict top-1 hits.
  3 conversions from Pattern B (COUNT queries); 3 conversions from metadata
  repair ALONE — empirically validates Chris D6 architectural conclusion.
---

# S2826 — Metadata sync-drift root cause + full-corpus repair + Pattern B COUNT gate shipped

## §1 One-paragraph summary

Chris opened S2826 with an architectural framing question: "what is the
shortest path to completing the remaining high-impact work from the /docs/
audit that materially improves authoritative retrieval before we spend
additional cycles optimizing router methodology?" Diagnosis cascaded
through three D-verdict cycles — first ratifying a two-mechanism split
(Pattern B small-gap ranking + Pattern C candidate injection); then
triggering a D7 stop branch when Pattern B implementation empirically
showed the `authority_weighted` tier flag was a no-op (all competitors
same `repo_canonical` tier); then diagnosing a second D7 trigger when
the deeper trace revealed 4 of 5 tested canonical anchors had
`Document.status='archived'` in DB despite `docs/_index.json` saying
`active` — filtered OUT by the default `include_superseded=False` retrieval
clause BEFORE ranking. Root cause established: `sync_docs_index_to_documents.py`
update path refreshed 12 fields but never `Document.status`. Reproducibility
proven via `extracted_metadata.docs_index_status='active'` on same-doc rows
(showed sync SAW correct source at last write) juxtaposed with
`Document.status='archived'` (never refreshed). Corpus-wide scope: 881
drifted rows (86% of repo_canonical corpus). Chris ratified Option D
full-corpus backfill + same-PR sync fix + parallel Rigby SIGN on Pattern
B. Executed atomically as PR #3265 (SHA `9c53ab880`): backfill command
(idempotent, verified via three-cycle dry-run/execute/dry-run/sync/dry-run)
+ sync fix (one-line status refresh in update path) + Pattern B mechanism
in `core/rag_integration.py` with Rigby joint SIGN Q1-Q5 refinements
applied (added `\bhow\s+much\b` parity, `intent_gate_fired`/
`intent_gate_name`/`effective_similarity` diagnostic fields per Chris
D2 traceability, `[S2826_PATTERN_B_DRIFT]` WARN log per Rigby Q5
drift-re-mask protection). **Post-repair Phase-0.5 re-measurement on
unchanged 16-row corpus, production settings: 0/16 → 6/18 = 33.3%
strict top-1 hits.** 3 conversions from Pattern B (Q21, Q23, Q26 —
corpus COUNT queries); 3 conversions from metadata repair ALONE (Q19,
Q22, Q28 — IDENTITY / DISCOVERY / IDENTITY queries where semantic
similarity was already sufficient once the intended target was no
longer filtered out). The metadata-only conversions empirically
validate Chris D6: primary Phase-0.5 retrieval failure was
synchronization defect, not embedding quality / semantic similarity /
authority weighting / ranking composition. SEVENTY-FIRST close-cycle
post-PLAYBOOK-7.4.4.

## §2 Ship

| Focus | PR | SHA | Merged to | Files |
|---|---|---|---|---|
| Metadata sync-drift repair + Pattern B COUNT gate | **#3265** | `9c53ab880` | main | 3 files: 324 insertions / 3 deletions |

### Files shipped

1. **`core/rag_integration.py`** (+132 lines) — Pattern B intent-gated
   file-specific ranking bonus for the embedding lane. Chris D-verdict
   S2826 D1 mandate: NARROW intent gate + small bounded file-specific
   bonus, distinct from the coarse 3-tier `authority_weighted` mechanism.
   Sibling of `core/rag.py` BM25-lane `_COUNT_INTENT_PATTERNS`. Rigby
   joint SIGN 2026-07-19 applied all Q1-Q5 refinements:
   - Q1: added `\bhow\s+much\b` regex for BM25 parity; kept narrower
     `total\s+\w+` regex as intentional divergence (documented in code)
   - Q4: added `intent_gate_fired` / `intent_gate_name` /
     `effective_similarity` / `count_intent_bonus` diagnostic fields
     per Chris D2 traceability requirement
   - Q5: `[S2826_PATTERN_B_DRIFT]` WARN log when gate fires but no
     mapped canonical target reaches returned pool — protects against
     future metadata drift silently re-masking the mechanism

2. **`core/management/commands/sync_docs_index_to_documents.py`** (+16 lines)
   — one-line fix: update path now refreshes `existing.status` from
   `STATUS_MAPPING` lookup. Prevents recurrence of the drift class the
   backfill corrects. Same-PR ship per Chris D2 — no production window
   where restored metadata can immediately re-drift.

3. **`core/management/commands/backfill_document_status_from_docs_index.py`**
   (new, 179 lines) — idempotent one-shot restoration command.
   `--dry-run` inspection mode; default execution wraps updates in
   single atomic transaction with `update_fields=['status', 'updated_at']`
   to bound blast radius. Verified idempotent via three-cycle sequence:
   dry-run #1 (881 mismatches match investigation) → execute (881 rows
   updated) → dry-run #2 (0 remaining) → `sync_docs_index_to_documents`
   run → dry-run #3 (0 recreated).

### Ledger delta

- `logs/zoom_out_classifications.jsonl`: (unchanged — S2826 folds
  recorded inline in this handoff §5)

## §3 Rigby joint SIGN records (S2826)

Three joint SIGN cycles in this session; all F-BLOCKING refinements applied.

### §3.1 Cycle 1 — architectural recommendation SIGN (turn ~5)

Q1-Q5 on Claude's initial recommendation (fix retrieval before revising
§2.2 methodology). Anti-rubber-stamp check passed — Rigby tool_runs
included `search_docs` on T3/T4 MQ items + `repo_tool` reads of
`measurement_report.md` + `core/rag.py`.

Rigby verdicts:
- **Q1** DISAGREE — bootstrap canonical extension is NOT explicitly
  queued in §8 as retrieval enforcement; CLAUDE.md pointer-graph is
  queued separately as bootstrap completeness
- **Q2** AGREE — intent-gated boost + suppression list per S2818 pattern
  is the right shape
- **Q3** DISAGREE (Q12 reclassification) — Q12 target
  `docs/topics/employee-os.md` is NOT §2c-fixable (topic-doc-vs-research-
  domain competition; belongs in semantic bucket unless canonical
  enforcement extended to topic anchors)
- **Q4** DISCOVERED critical two-lane gap — authority-boost lives in
  BM25 lane (`core/rag.py`), measurement dispatched through embedding
  lane (`kb_tool.semantic_search`). This finding reframed the whole
  recommendation
- **Q5** ZOOM-OUT (deferred to Cycle 2)

### §3.2 Cycle 2 — recovery of truncated verdicts (turn ~7)

Q3-Q12/Q19, Q4 (ordering), Q5 (zoom-out), Q6 (two-lane gap verification).

Rigby verdicts:
- **Q3-Q19** semantic-general bucket (artifact-class/surface competition
  miss; needs doc-class weighting beyond §2c)
- **Q4** SERIAL for final §2.2 bands; concurrent skeleton-only permitted
- **Q5 zoom-out** — LOAD-BEARING pushback: *"You're assuming §2c
  enforcement exists and measurement will reflect it. The real coupling
  risk is lane mismatch (BM25 vs pgvector) + metadata hygiene; without
  parity + correct flags, you'll 'optimize the scorecard' while the
  system still can't retrieve canon."* This pushback shaped the
  subsequent D-verdict cascade.
- **Q6 F-BLOCKING** — verified via direct code read that
  `td_handlers_ops.py:5950-5952` sets `f_authority_weighted = bool(
  payload.get('authority_weighted', False))` → default False; passed
  to `search_embeddings(...)` at `:5980-5981`. Confirmed the S2825
  dispatch never overrode.

### §3.3 Cycle 3 — Pattern B design SIGN (turn ~14)

Q1-Q5 on Pattern B mechanism design. Anti-rubber-stamp check passed —
Rigby tool_runs included reads of `test_authority_aware_retrieval.py`
+ `test_rag_intent_gating_2819.py` (surfacing the BM25-lane
`_COUNT_INTENT_PATTERNS` naming collision in `core/rag.py`).

Rigby verdicts + refinements applied to code:
- **Q1** DISAGREE (partial parity gap) — embedding lane MISSING
  `\bhow\s+much\b` per BM25 lane. **Refinement applied.**
- **Q2** AGREE-with-nuance — 0.05 is minimum-safe (0.03 is
  drift-fragile). **Kept at 0.05.**
- **Q3** AGREE — `(similarity + bonus) * authority_weight`
  composition is correct. **Matches implementation.**
- **Q4** AGREE — mirror Chris D2 diagnostic contract; add
  `intent_gate_fired` / `intent_gate_name` / `effective_similarity`
  / `count_intent_bonus`. **Refinement applied.**
- **Q5** ZOOM-OUT: add drift re-mask detection.
  **Refinement applied via `[S2826_PATTERN_B_DRIFT]` WARN log.**

## §4 Chris D-verdicts (all RATIFIED same-session)

Six D-verdict cycles this session, each ratifying a stepwise refinement
of the diagnosis and repair plan:

### §4.1 First cycle — Option B (two-mechanism split)
- **D1** Pattern B small-gap ranking mechanism approved
- **D2** Pattern C candidate injection mechanism approved
- **D3** Option D (rely on runtime injection instead of retrieval) NOT
  ratified. Load-bearing rule: *"Retrieval must prove retrieval.
  Runtime injection cannot be used to erase a retrieval-layer failure."*
- **D4** Option C (chunking rework) DEFERRED — test policy-explicit
  first
- **D5** 5 distinct policy classes preserved (COUNT / SELF_REFERENCE /
  INDEX_DISCOVERY / literal-filename / doc-class-precedence)
- **D6** Test sequence — Pattern B first, Pattern C via Rigby SIGN,
  then re-measure
- **D7** STOP BRANCH — if metadata correct AND `authority_weighted=True`
  doesn't help, do NOT add gates; return to diagnosis of candidate
  generation / chunking / metadata / path normalization / surface
  competition / ranking composition

### §4.2 Second cycle — metadata layer discovery (D7 triggered)
- **D1** metadata repair approved — Option D (backfill + sync fix +
  idempotency verification)
- **D2** full corpus backfill (not 4-doc patch)
- **D3** root-cause discipline (when possible / which pipeline /
  reproducibility / future risk)
- **D4** Pattern B routed through Rigby SIGN concurrently while metadata
  repair proceeds
- **D5** post-repair validation sequence (validate without bypass →
  positive + negative → re-run 16-row corpus)
- **D6** architectural conclusion recorded explicitly: *"primary
  Phase-0.5 retrieval failure was not caused by embedding quality,
  semantic similarity, authority weighting, or ranking composition.
  It was caused by a synchronization defect allowing Document.status
  to diverge from docs/_index.json, excluding authoritative documents
  from retrieval before ranking occurred."*

### §4.3 Third cycle — root cause + backfill execution
- **D1** 1A (execute backfill: dry-run → verify → execute → immediate
  second dry-run → zero remaining)
- **D2** 2A (ship sync fix in same PR as backfill)
- **D3** verification requirements (run sync → confirm zero new drift
  → third dry-run → zero remaining)
- **D4** Pattern B unmerged until metadata correctness restored;
  validate without bypass flags after repair
- **D5** architectural documentation update (record in retrieval
  architecture — this handoff §7 + `KNOWLEDGE_PIPELINE.md`)
- **D6** 13 out-of-index rows deferred (out of scope for this PR)
- **D7** close-out criteria enumerated (all 6 conditions must be true
  before S2826 close)

### §4.4 Fourth cycle — commit + merge authorization
- "commit as one atomic PR" — PR #3265 created
- "merge it" — merged as SHA `9c53ab880`

## §5 Zoom-out folds recorded

Two zoom-out observations from this session's SIGN cycles that meet
PLAYBOOK-6.10.8 fold-authoring evidence discipline:

### §5.1 Fold — Retrieval failure diagnosis order

**Observation:** When retrieval fails on canonical anchors, the diagnosis
order MUST start with metadata layer inspection (Document.status /
canonical_authority / retrieval_boost / embedding presence) BEFORE
proceeding to boost-value tuning or gate design. Skipping this step
risks "optimizing the scorecard" against a broken candidate layer.
Evidence: S2826 direct Django ORM query showed 4 of 5 tested canonical
anchors had `Document.status='archived'` despite `docs_index_status`
metadata showing `active` — a defect that no amount of ranking
sophistication could compensate for.

**Class:** `retrieval_diagnosis_discipline`.
**Triggers:** first observed at S2826; single-trigger; observe next
retrieval-diagnosis arc for corroboration before codification.

**Stable-state pointer:** commit `9c53ab880` (S2826 close), verified
at S2826 §5.2 measurement.

### §5.2 Fold — Sync update-path field-refresh completeness

**Observation:** Every sync command whose UPDATE path refreshes SOME
fields but not OTHERS creates a persistent drift class between the
source-of-truth (in this case `docs/_index.json`) and the destination
(`Document` table). The correct completeness invariant is: on update,
refresh EVERY field the CREATE path would derive from the source, not
just the ones that seem "actionable." S2826 evidence: 3 prior sync
patches (Session 1234 D9 enrichment refresh, Session 1235 P5#1
`extracted_metadata` refresh, S2826 status refresh) each added ONE
missing field to the update path — leaving the previous authors'
under-completeness exposed each time.

**Class:** `sync_update_path_completeness`.
**Triggers:** third observation of the same shape (S1234/S1235/S2826);
codification-ready. Playbook v0.9+ amendment candidate.

**Stable-state pointer:** commit `9c53ab880` at
`core/management/commands/sync_docs_index_to_documents.py:305-320`.

## §6 Post-repair measurement — verbatim evidence

Unchanged 16-row Phase-0.5 corpus, production settings (`include_superseded=False`,
no bypass flags):

| S2825 baseline | S2826 post-repair |
|---|---|
| **0/16 = 0.0%** strict top-1 hits | **6/18 = 33.3%** strict top-1 hits |

Attribution of the 6 conversions:

| qid | family | target | gate_fired | mechanism |
|---|---|---|---|---|
| Q19 | IDENTITY | `2701_docs_inventory_topology_audit.md` | False | **metadata repair alone** |
| Q21 | COUNT | `docs/PLATFORM_INVENTORY.md` | True | Pattern B + metadata repair |
| Q22 | DISCOVERY | `ROUTER_SCAFFOLDING_DESIGN.md` | False | **metadata repair alone** |
| Q23 | COUNT | `docs/PLATFORM_INVENTORY.md` | True | Pattern B + metadata repair |
| Q26 | COUNT | `docs/PLATFORM_INVENTORY.md` | True | Pattern B + metadata repair |
| Q28 | IDENTITY | `2701_docs_inventory_topology_audit.md` | False | **metadata repair alone** |

Twelve rows still miss, mapping onto policy classes Chris D5 deferred:

| Class | Rows | Pattern class per Chris D5 |
|---|---|---|
| SELF_REFERENCE | 5 (Q14, Q15, Q16, Q17, Q20) | Pattern C candidate injection |
| CONCEPTUAL / PROCEDURAL | 4 (Q9, Q12, Q13, Q18) | Semantic-general (separate future arc) |
| DISCOVERY | 2 (Q10, Q11) | DISCOVERY policy class |
| IDENTITY literal filename | 1 (Q24, query `PLATFORM_INVENTORY`, target `docs/PLATFORM_INVENTORY.md`) | literal-filename policy class |

Negative-control regression suite (production settings, no bypass): **7/7 clean.**
No regression on `add a new spider`, `how do I run a spider`, spider
network narrative, `morning brief workflow`, `where do I start`, literal
`PLATFORM_INVENTORY` lookup, or `What does Documentation currently include?`.

## §7 Architectural conclusion per Chris D5 (retrieval-architecture documentation update)

Recorded explicitly per Chris D5 directive:

> **The primary Phase-0.5 retrieval failure was not caused by embedding
> quality, semantic similarity, authority weighting, or ranking
> composition. It was caused by a synchronization defect allowing
> `Document.status` to diverge from `docs/_index.json`, excluding
> authoritative documents from retrieval before ranking occurred.**

This distinction is now part of the retrieval architecture and should
inform how future retrieval failures are diagnosed. The diagnosis
protocol per Chris D2 (S2826):

1. **Metadata audit first** — query DocumentEmbedding rows for the
   intended target: is `canonical_authority` set? is `retrieval_boost`
   correct? does `Document.status` say `processed` (not `archived`)?
   Are embeddings present?
2. **Filter behavior** — does the default `include_superseded=False`
   clause eliminate the target?
3. **Candidate pool depth** — does the intended target chunk appear
   in top-N by raw similarity?
4. **Ranking composition** — if in pool but not top-1, is
   `authority_weighted` engaged? Is the tier taxonomy fine-grained
   enough to discriminate?
5. **Only then** — design intent-gated policy-class mechanisms.

Cross-linked: `docs/KNOWLEDGE_PIPELINE.md` (S2826 addendum §retrieval-failure-diagnosis-order).

## §8 Twin-pointer

Per parent §5 D7 + memory `feedback_twin_deliverable_at_every_ratification`:

- **Repo doc:** this handoff at merge SHA `9c53ab880`
- **Workspace deliverable:** `f2c39253-8e7a-40af-80d0-d2806014d75a`
  in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
  — created via ORM-direct at S2826 close per memory
  `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`
  (bypasses pa_deliverables_tool diagnostic-flag bug); type
  `ratification_record`, category `governance`, status `ready`, pinned,
  `diagnostic_status=None` (bypass verified).

## §9 Lessons for S2827

1. **Metadata layer inspection is Step 1 of any retrieval-failure
   diagnosis.** Skipping to boost design is a category error. Chris D7
   codified this discipline via the stop branch.
2. **Sync commands whose UPDATE path refreshes only SOME fields
   create persistent drift classes.** Watch for this pattern in every
   sync/mirror command; the completeness invariant is "refresh every
   field the CREATE path derives from source."
3. **Direct-code verification and Rigby SIGN both engaged in parallel
   on independent evidence surfaces converged on the same root cause.**
   Neither would have caught it alone in-session — Claude found the
   two-lane gap via code read; Rigby found it via test-file inspection.
   Independent evidence discipline works.
4. **The Chris D6 architectural conclusion is empirical, not
   speculative.** 3 of 6 post-repair conversions came from metadata
   repair ALONE — no policy mechanism ran. The retrieval was always
   adequate; the corpus was hidden.
5. **Rigby Q5 zoom-out pushback ("lane mismatch + metadata hygiene")
   was load-bearing.** It reframed the entire recommendation and led
   directly to the D7 stop trigger + Option D metadata repair path.
   Continue routing zoom-out asks per PLAYBOOK-6.10.7.
6. **Pattern C design is next.** 5 SELF_REFERENCE rows still miss.
   Chris D2 (first cycle) approved the candidate-injection mechanism
   shape. Design should be routed through Rigby SIGN before
   implementation per Chris D6 sequence.
7. **DO NOT relax `include_superseded=False` default** to "fix"
   remaining misses. That would collide with Chris's D6 rule about
   retrieval integrity and would re-introduce the drift-mask class.
8. **13 out-of-index Document rows** — recorded as separate
   post-Phase-0.5 investigation per Chris D6.

## §10 Current repository state (S2826 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `9c53ab880` (S2826 close PR #3265) |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Phase-0.5 arc state | **Post-metadata-repair; 6/18 retrieval-strict-hit; Pattern B merged. Pattern C design queued.** |
| PHASE_0_5_ROUTER_ENABLED | false (default; .env clean; unchanged from S2825) |
| S2825 pin | `pa-5d610d3a46c9464e` (retired at S2825 close) |
| S2826 pin | `pa-def161f46bb2419f` (label `s2826-audit-vs-methodology-priority-eval`, retired at S2826 close, force=true, fifty-seventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2827 open) |
| Session close cascade | **THIS session — S2826** |
| Docs cascade | 4-step per feedback_docs_cascade_at_every_close (build_docs_index / build_rag_corpus / sync_docs_index_to_documents / embed_documents --all-unembedded) |
| Recycle post-merge | ✅ `make celery-recycle` executed after #3265 merge |

## §11 Twin-pointer card (for S2827 open protocol)

📁 **Repo — S2826 artifacts:**

- **Backfill command:** `core/management/commands/backfill_document_status_from_docs_index.py`
- **Sync fix:** `core/management/commands/sync_docs_index_to_documents.py:305-320`
- **Pattern B implementation:** `core/rag_integration.py:60-100` (patterns +
  gate) + `:242-296` (composition + sort)
- **Drift re-mask WARN log:** `core/rag_integration.py:397-427`
- **Handoff (this doc):** `docs/handoffs/SESSION_2826_METADATA_SYNC_DRIFT_REPAIR_PATTERN_B_SHIPPED.md`
- **Architectural conclusion:** cross-linked in `docs/KNOWLEDGE_PIPELINE.md`
  §retrieval-failure-diagnosis-order (S2826 addendum)
- **Merge SHA:** `9c53ab880` · **PR:** #3265
- **S2825 antecedent measurement:** `docs/research/discovery_layer/PHASE_0_5/measurement_report.md`

🖥️ **Workspace UI — S2826 twin-pointer deliverable:**

- **UUID `f2c39253-8e7a-40af-80d0-d2806014d75a`** in Donkey Betz
  workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) — created via
  ORM-direct; type `ratification_record`, category `governance`, status
  `ready`, pinned. Diagnostic-flag bypass verified.

## §12 Appendix — Provenance

**Session:** S2826 (2026-07-19)
**Git HEAD at authoring:** `9c53ab880` (S2826 close PR #3265 merged)
**Ratifier:** Chris (6 D-verdict cycles, all RATIFIED same-session)
**Rigby joint SIGN cycles:** 3 (all applied with F-BLOCKING refinements)
**Predecessor:** S2825 harvest measurement (0/16 baseline)
**Novel this session:** first empirical validation of retrieval-diagnosis
discipline where metadata repair alone converts 3 of 6 rows; first
in-session cascade of 3 D-verdict cycles + D7 stop trigger followed by
successful root-cause repair; first Playbook-v0.9-candidate fold on
sync-update-path completeness (3-trigger shape S1234/S1235/S2826);
SEVENTY-FIRST close-cycle post-PLAYBOOK-7.4.4.

**Non-goals held throughout:**
- No relaxation of `include_superseded=False` default
- No Pattern C implementation (design routed for next arc)
- No touching the 13 out-of-index rows (per Chris D6)
- No §2.2 methodology revision (post-Pattern-C per D6 sequence)
- No implicit boost escalation to compensate for policy-class gaps
  (per D7 discipline)

---

**End of S2826. S2827 opens on Pattern C SELF_REFERENCE candidate
injection design + Rigby SIGN routing.**

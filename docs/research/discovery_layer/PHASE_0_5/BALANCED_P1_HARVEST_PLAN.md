---
title: "Phase-0.5 — Balanced Operator-Style P1 Harvest Plan (Rigby SIGN cleared — routes to Chris for D-verdict)"
status: post-Rigby-SIGN-refined (Rigby AGREE-with-refinements across Q1/Q2/Q3/Q5 + AGREE-clean on Q4; 0 F-BLOCKING; 11 refinements applied same-session; routes to Chris D-verdict via Chat UI)
authority: draft — LOAD-BEARING once Chris ratifies
session: 2823
generated: 2026-07-18
supersedes: none
related:
  - docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md   # §11 Phase-0.5 arc direction (parent)
  - docs/research/discovery_layer/PHASE_0/field_dictionary.md   # v0 schema (frozen) — Phase-0.5 corpus adheres to this
  - docs/research/discovery_layer/PHASE_0/corpus.json   # 33 existing rows (5 P1 + 10 P2 + 18 P3) — Phase-0.5 appends new P1 rows
  - docs/research/discovery_layer/PHASE_0/analyze.py   # existing measurement harness — reused for Phase-0.5 re-measurement
  - docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md   # §5.3 B1 concrete harvest source list
scope:
  Defines the balanced-operator-style P1 corpus harvest for Phase-0.5. Objective, sources, execution steps, validation discipline, output format, and Rigby SIGN routing.
non_goals:
  - Executing the harvest before Rigby SIGN clears + Chris ratifies scope
  - Fixing DISCOVERY family performance (Chris R3 preserve directive)
  - Building the advisory-only router (Track B B2 — separate task)
  - Authoring the abstain-policy proposal (Track B B3 — separate task)
  - Substrate code changes (measurement-only, per S2822 close)
---

# Phase-0.5 Balanced Operator-Style P1 Harvest Plan

**Draft — routes to Rigby joint SIGN via pin `pa-d63796dde6404d0f` label `s2823-phase0-5-dual-track` before any harvest execution begins.**

## §1 — Objective (Chris verbatim)

> "Determine whether routing-from-query-text transfers from synthetic benchmarks to real operational work."

Phase-0 evidence (S2822) established a 60-point P1-vs-P3 accuracy gap (20% vs 89%). The scientific question Phase-0.5 answers: does that gap hold, narrow, or collapse once the P1 sample is **balanced across operator dialects** at n≥20?

## §2 — Success + stop-condition (Rigby-endorsed default, Chris ratification pending)

### §2.1 Scoring Definition (FROZEN for Phase-0.5 — per Rigby SIGN Q5 Concern 1)

**Authoritative go/no-go metric (frozen):** **top-1 correct intended_family AND top-1 correct `known_correct_target_strict`**, applied per row. A row is "correct" iff (a) Classifier A predicts `intended_family` correctly, AND (b) the retrieval substrate the router selects returns at least one member of `known_correct_target_strict` in top-1.

**Secondary metrics reported but non-authoritative:**
- Top-3 hit against `known_correct_target_loose` (per-row loose accuracy)
- Family-only accuracy (classifier standalone)
- Wrong-but-plausible catalog (per Phase-0 §7 analyze.py output)

**Refinement rationale:** Rigby Q5 Concern 1 flagged that "per-tier accuracy" is under-specified and drift-prone (correct family vs correct target strict vs loose match; top-1 vs top-3). Freezing the authoritative metric prevents band-boundary manipulation (improving accuracy by changing scoring criteria rather than routing behavior).

### §2.2 Stop-condition bands (per authoritative metric)

| Condition | Interpretation | Extension rule |
|---|---|---|
| Balanced P1 n≥20 with per-tier accuracy ≤40% | Routing-from-text-alone NOT viable — Phase-1 dogfood pilot findings dispositive; Phase-1 production router shelved. | Decisive floor — no extension. |
| Balanced P1 n≥20 with per-tier accuracy 40-60% | Signal ambiguous — **automatic extension to n≥30** UNLESS Chris explicitly ratifies "partial-router (HIGH-consequence families only)". | Automatic extension (per Rigby SIGN Q1 refinement); Chris-override allowed. |
| Balanced P1 n≥20 with per-tier accuracy ≥60% | Original Phase-0 gap likely artifact of P1 sample size (n=5); Phase-1 dogfood pilot continues per OPTION A-DUAL. | No extension required. |

**Refinement rationale:** Rigby Q1 refinement 2 — the middle band was doing two jobs (statistical uncertainty at n≈20 + genuine partial-viability); made the middle-band interpretation deterministic (auto-extend OR Chris partial-router ratification) rather than either-or menu.

Chris ratifies §2.1 metric + §2.2 stop-condition bands explicitly before harvest execution.

## §3 — Balance targets

**Operator-style balance (equally weighted for scientific validity — with two-view reporting per §3.3):**

| Operator | Hard minimum | Preferred target | Rationale |
|---|:---:|:---:|---|
| Chris | 5 | 8 | Directive shape — mixes bare noun phrases, uppercase-identifier queries, question-shape queries. Sparse per session but load-bearing (final ratification queries). |
| Claude | 5 | 8 | Grep / rg / search_docs invocation shape — often literal-identifier queries + POINT-vs-LOCATE mix. Frequent per session. |
| Rigby | 5 | 8 | Tool-dispatch shape — semantic_search / search_docs / deliverable_tool.search + conversation_tool.search + repo_tool.search. Frequent per session; captures operator-in-tool-loop query dialect. |
| **Total minimum** | **15** | **24** | Balance floor. Preferred n≥24 (~n≥8 per style) delivers per-style stabilization; hard floor n≥15 admits harvest completion in-session. |

### §3.1 Stabilization intuition (per Rigby SIGN Q2 refinement)

Per-style accuracy rates begin to stabilize around **n≈8-10**; **n=5 per style is treated as directional only** and does not support strong per-style verdicts. Phase-0.5 aggregate n≥20 target holds; per-style n≥8 preferred but not blocking.

**Family-shape balance (secondary — not blocking):** aim for ≥1 row per family (COUNT, PROCEDURAL, IDENTITY, SELF-REFERENCE, CONCEPTUAL, DISCOVERY) if organic distribution supports. Do NOT synthesize to fill family gaps — that reintroduces P3.

### §3.2 Extraction discipline (mandatory)

Every harvested row is annotated with the **original operator-context** (session number when available, timestamp if available, surrounding intent) so it can be validated as genuinely P1 (a real search someone actually ran) and not backfilled or rehearsed.

### §3.3 Two-view accuracy reporting (per Rigby SIGN Q5 Concern 4)

Rigby flagged that forcing quotas across Chris/Claude/Rigby can overweight rare styles and underweight dominant ones, distorting representativeness. Phase-0.5 measurement report reports TWO views:

- **Balanced-set accuracy** — equal weight per style; primary view for dialect-robustness verdict.
- **Frequency-weighted accuracy** — approximate operational-frequency weighting per style (rough weights sufficient; e.g., ~10% Chris / ~45% Claude / ~45% Rigby based on session-open observation).

**Go/no-go decision uses balanced-set accuracy for viability** (dialect robustness is the harder bar); frequency-weighted accuracy reported as sanity check for "does this actually match real operational load?" answer.

## §4 — Harvest sources per operator style

### §4.1 Chris-originated queries

**Primary source: handoffs.**
- Grep `docs/handoffs/SESSION_*.md` for patterns like `Chris asked`, `Chris directive`, `Chris said`, `Chris: `, `Chris "` and extract the natural-language question shape.
- Grep `docs/handoffs/*.md` for quoted Chris directives that contain a lookup shape (e.g., "How many spiders", "Where is X").
- Filter for questions that would result in a doc-retrieval query if asked to Rigby fresh.

**Secondary source: Chat UI conversation history.**
- Rigby-executed lookup via `conversation_tool.search q="<candidate>" k=10` on prior conversation pins.
- Extract the Chris-authored question turn (not the assistant response).

**Tertiary source: Chris D-verdict envelopes.**
- Grep `docs/research/implementation/RATIFICATION_*.md` for Chris-authored question shapes inline in §9 D-verdicts.

### §4.2 Claude-originated queries

**Primary source: handoffs.**
- Grep `docs/handoffs/*.md` for `rg "` , `grep "` , `search_docs`, `kb_tool.semantic_search` invocations authored by Claude (not Rigby).
- Extract the query text.

**Secondary source: PR descriptions + commit messages.**
- Grep `git log` messages for `searched for`, `found via rg`, `grep`.

**Tertiary source: Claude tool_calls recorded in Rigby's conversation logs.**
- Rigby-executed lookup for `claude_code_tool` invocations that include search-shape queries.

### §4.3 Rigby-originated queries (expanded per Rigby SIGN Q3 refinements)

**Primary source: handoffs (Rigby tool_runs annotations).**
- Grep handoffs for `[PA_TASK_SUMMARY]`, `search_docs`, `kb_tool.semantic_search`, `deliverable_tool.search`, **`conversation_tool.search`, `repo_tool.search`** annotations that include the specific query text Rigby chose.
- Extract Rigby's chosen query string, not Chris's or Claude's directive that prompted it.

**Secondary source: Rigby's conversation-history tool-call inspection.**
- Rigby-executed self-lookup: `conversation_tool.search` for her own tool-call turns containing search-shape invocations across ALL retrieval-intent tools (semantic_search, search_docs, deliverable_tool.search, conversation_tool.search, repo_tool.search).

**Tertiary source: PA-worker logs / LLMCallEvent write-side.**
- `logs/pa_worker.log` (if retained) or Rigby's `LLMCallEvent` records. **DEMOTED per Rigby Q3 R3 discipline:** admissible ONLY if the log entry contains the exact `query_text` string verbatim AND a stable pointer. If the log only contains reconstructed / paraphrased / normalized-tokenization query text, REJECT the candidate.

### §4.4 Internal-paraphrase guard (per Rigby SIGN Q3 R2)

Rigby-originated queries are P1 ONLY when the actual query text Rigby issued to the tool is explicitly visible. Rigby sometimes paraphrases Chris/Claude's ask when constructing her internal tool call (e.g., turns "catch me up" into "rigby shift brief tool"); those internal paraphrases are NOT P1 unless the tool call itself received the exact string.

**Reject candidates that fail this check:**
- Handoff text says "Rigby searched for X" but doesn't show the literal string
- LLMCallEvent shows the intent but not the query_text field verbatim
- Tool-run summary paraphrases the query without preserving the argument literal

## §5 — Row-labeling discipline (matches Phase-0 field_dictionary v0)

Every harvested row MUST include all 16 fields from `field_dictionary.md` v0, with these additional Phase-0.5 discipline conventions:

- **`provenance_tier=P1`** — this is the required tier for all Phase-0.5 harvest.
- **`provenance_source`** — **v0 controlled-vocab preserved (per Rigby SIGN Q5 Concern 2 refinement).** Use `"other"` for Phase-0.5 harvest sources and put the specific sublabel in `label_rationale` (e.g., `label_rationale: "sublabel=handoff_grep_chris. Extracted from SESSION_2815_..."`), OR use the explicit non-canonical-enum prefix convention: `provenance_source: "other:handoff_grep_chris"`. Do NOT mint new bare enum values — that would silently fork the v0 schema.
- **`provenance_pointer`** — MUST include a stable auditable pointer: source doc path + line range, OR conversation_id + turn, OR deliverable_id + section, OR PR ref + commit sha. Precise enough to replay-audit.
- **`origin_session`** — **PREFERRED, NOT REQUIRED (per Rigby SIGN Q5 Concern 3 refinement).** Some legitimate P1 queries lack a clean single-session pointer (e.g., tool-driven retrieval spanning multiple sessions, or standing in-loop tool calls). If `origin_session` is unknown, `provenance_pointer` MUST be strong (per prior bullet) so replay-audit remains possible.
- **`gap_filled`** — EMPTY (P1 rows are not gap-fills).
- **`observed_live_result_target`** — populate if the source doc mentions what retrieval returned; else null. This is baseline observation, NOT truth.
- **`known_correct_target_strict`** — MANUAL LABELING REQUIRED per Rigby Q4 discipline. Do NOT substitute `observed_live_result_target` for truth.

**Reject candidates that fail these discipline checks:**
- Query text is a paraphrase (case-fold, whitespace-normalize, punctuation edits, minor cleanup) — the exact string the operator issued must be preserved verbatim (per Rigby SIGN Q4 AGREE)
- Both `origin_session` unknown AND `provenance_pointer` too weak to replay-audit
- Truth label is uncertain (single-target family) — either resolve manually or set `secondary_family` = AMBIGUOUS + populate `known_correct_target_loose`
- Query never actually appeared in operator work (backfilled based on what "would have been asked")
- Rigby-originated query fails §4.4 internal-paraphrase guard (tool-call literal not preserved)

## §6 — Execution steps (post-Rigby-SIGN, post-Chris-ratification)

1. **Author `PHASE_0_5/corpus.json`** — clone Phase-0 `corpus.json` structure; leave `rows: []` for new P1 additions (do NOT edit Phase-0 rows in place).
2. **Chris harvest (Claude-authored, Rigby-verified):** run §4.1 primary + secondary until n≥5 admitted; log all rejected candidates with reject-reason.
3. **Claude harvest (Claude-authored, Rigby-verified):** run §4.2 primary + secondary until n≥5 admitted; log all rejected candidates.
4. **Rigby harvest (Rigby-authored via tool-call inspection, Claude-verified):** run §4.3 primary until n≥5 admitted; log all rejected candidates.
5. **Balance check:** verify n≥20 total with n≥5 per operator style; if under, extend §4 tertiary sources.
6. **Family-shape balance report:** count rows per family; note gaps (do NOT synthesize).
7. **Re-run Phase-0 analyze.py** against extended corpus: `python docs/research/discovery_layer/PHASE_0/analyze.py --corpus docs/research/discovery_layer/PHASE_0_5/corpus.json` (or combined) — produce `PHASE_0_5/measurement_report.md` with per-tier + per-operator + per-family accuracy.
8. **Zoom-out ledger fold** for corpus decisions that surface during harvest (any judgment call — reject reason, family-vs-secondary-family choice, etc.).

## §7 — Non-goals (Chris R3+R6 preserved)

- NO DISCOVERY fixes during harvest (measure only)
- NO taxonomy constitutionalization (working taxonomy stays working)
- NO routing implementation as production decision path (advisory-only per Chris R2)
- NO RRF or global fusion (per Chris R6)
- NO patch to frozen lexical top_k policy
- NO auto-adopt semantic default flip

## §8 — Output artifacts

At harvest close (before Phase-0.5 close cascade):

- `PHASE_0_5/corpus.json` — n≥20 P1 rows, R1-provenance-tagged, field_dictionary v0 compliant
- `PHASE_0_5/harvest_log.md` — accepted + rejected candidates with reject reasons + operator-style balance count
- `PHASE_0_5/measurement_report.md` — per-tier + per-operator + per-family accuracy vs Phase-0 baseline
- `PHASE_0_5/harvest_verdict.md` — falls into §2 stop-condition band; recommends Phase-1 disposition

## §9 — Rigby joint SIGN — CLEARED (11 refinements applied same-session, 0 F-BLOCKING)

**SIGN cycle executed via pin `pa-d63796dde6404d0f` at S2823 turn ~10.** Anti-rubber-stamp check per S2822 §2.2 pattern: PASSED — Rigby returned 8 `tool_runs` (5 explicit `repo_tool.read_file` probes covering `field_dictionary.md`, envelope §11, `corpus.json`, bridge §5.3 B1, this plan draft; plus 2 `repo_tool.search` probes on section anchors).

### §9.1 Question-by-question verdicts

| Q | Subject | Verdict | Refinements |
|---|---|---|:---:|
| Q1 | §2 stop-condition bands | AGREE-with-refinements-2 | 2 |
| Q2 | §3 balance targets | AGREE-with-refinements-2 | 2 |
| Q3 | §4 harvest sources | AGREE-with-refinements-3 | 3 |
| Q4 | §5 labeling discipline (reject-if-paraphrase) | AGREE (as written) | 0 |
| Q5 | zoom-out (PLAYBOOK-6.10.7) | AGREE-with-refinements-4 | 4 |
| — | **Total** | **AGREE-with-refinements across 4/5 Qs; 0 F-BLOCKING** | **11** |

### §9.2 Refinements applied (11 same-session per S2822 precedent)

- **Q1 R1** — added §2.1 Scoring Definition (FROZEN) block pinning authoritative metric = top-1 correct intended_family AND top-1 correct known_correct_target_strict; secondary metrics reported but non-authoritative for go/no-go
- **Q1 R2** — middle band 40-60% now binds to automatic extension (n≥30) OR Chris-explicit partial-router ratification — no more either-or menu
- **Q2 R1** — §3 balance targets now show hard-minimum (n≥5 per style) AND preferred target (n≥8 per style) as separate columns
- **Q2 R2** — added §3.1 Stabilization intuition block ("per-style rates stabilize around n≈8-10; n=5 directional only")
- **Q3 R1** — §4.3 expanded to include `conversation_tool.search` + `repo_tool.search` as Rigby-originated retrieval-intent tools (previously only kb_tool.semantic_search / search_docs / deliverable_tool.search)
- **Q3 R2** — added §4.4 Internal-paraphrase guard section explicitly rejecting Rigby-internal paraphrases of Chris/Claude asks unless tool-call literal is preserved
- **Q3 R3** — §4.3 tertiary source (PA-worker logs / LLMCallEvent) DEMOTED: admissible only if log entry contains exact query_text verbatim + stable pointer
- **Q5 C1** — same as Q1 R1 (Scoring Definition FROZEN block addresses this)
- **Q5 C2** — §5 provenance_source now enforces v0 controlled-vocab preservation: use `"other"` + sublabel in label_rationale, OR `"other:handoff_grep_chris"` non-canonical prefix. Do NOT mint new bare enum values.
- **Q5 C3** — §5 origin_session field now PREFERRED (not REQUIRED); strong `provenance_pointer` acts as substitute when session pointer unavailable
- **Q5 C4** — added §3.3 Two-view accuracy reporting — Balanced-set accuracy (primary, go/no-go) + Frequency-weighted accuracy (secondary, sanity check for operational representativeness)

### §9.3 Q4 optional micro-exception NOT taken

Rigby offered an optional micro-exception permitting trimming of accidental leading/trailing whitespace with explicit `label_rationale` note. Per her follow-up guidance ("if you want maximum cleanliness: don't even do this — just reject") the plan does NOT adopt this micro-exception. Verbatim-only remains absolute.

### §9.4 Ready for Chris D-verdict

All 11 refinements applied to §2.1, §2.2, §3, §3.1, §3.3, §4.3, §4.4, §5. Plan status: `post-Rigby-SIGN-refined`. Routes to Chris via Chat UI for D-verdict per §10.

## §10 — Chris D-verdict RATIFIED (2026-07-18 S2823 turn ~14)

**Verdict:** **RATIFY** — all three ratifications accepted as the constitutional gate for Phase-0.5 harvest execution.

### §10.1 R1 — §2.1 Scoring Definition: RATIFIED as written

- Authoritative viability metric frozen: **top-1 correct `intended_family` AND top-1 correct `known_correct_target_strict` per harvested row**.
- All secondary metrics (family-only, loose target, top-3, etc.) are explicitly OBSERVATIONAL and MUST NOT influence the Phase-0.5 go/no-go decision.

### §10.2 R2 — §2.2 Stop-Condition Bands: RATIFIED as written

- **≤40% → NOT viable.** Decisive floor.
- **40-60% → Automatic extension to n≥30 before any viability conclusion** UNLESS Chris explicitly ratifies a partial-router interpretation limited to HIGH-consequence families. No discretionary interpretation inside the middle band.
- **≥60% → Continue to Phase-1 advisory dogfood only.**

### §10.3 R3 — §3 Balance Targets: RATIFIED as written

- **n≥5 per operator style = hard admission minimum.**
- **n≥8 per style = preferred target** where operational evidence naturally exists.
- Report BOTH: (1) Balanced-set accuracy (primary constitutional metric), (2) Frequency-weighted accuracy (operational sanity check).
- **If natural operational evidence cannot satisfy preferred balance, record the limitation rather than synthesizing examples.** Do NOT reintroduce P3 to fill balance gaps.

### §10.4 Additional Chris directive — evidence-integrity discipline (LOAD-BEARING)

> "Phase-0.5 remains an evidence-gathering phase. If execution uncovers findings that materially challenge any of these ratified assumptions, **stop, document the evidence, and route the methodology back for SIGN rather than silently adapting the experiment.**"

**Operational triggers for methodology-back-to-SIGN routing:**
- Scoring metric edge case not covered by §2.1 (e.g., row where strict target is genuinely dual-valued and the top-1 discipline breaks down)
- Stop-condition band shape empirically wrong (e.g., harvested rows cluster tightly around 40% or 60%, suggesting the band boundaries are noise-vs-signal ambiguous)
- Balance targets unachievable via §4 harvest sources (e.g., Chris-originated queries are too sparse to reach n≥5 hard minimum without reaching to backfill)
- Provenance discipline violation surfaced during harvest (e.g., a candidate that seemed P1 is actually a paraphrase; a whole harvest source turns out to be systematically paraphrased)
- Router advisory-only guardrail breach candidate (e.g., an instrumentation decision that would let router output influence retrieval)

When triggered: **stop execution → document evidence → route back to Rigby joint SIGN → then Chris D-verdict** on whether methodology adjusts or scope holds. Silent adaptation is a constitutional violation of the ratified plan.

### §10.5 Ratification status: LOAD-BEARING

Plan §2.1 + §2.2 + §3 are now the ratified constitutional gate. Execution proceeds per §6 execution steps, gated on:
- ABSTAIN_POLICY_PROPOSAL Chris D-verdict RATIFY (Track B B3)
- ROUTER_SCAFFOLDING_DESIGN Chris D-verdict RATIFY (Track B B2)

Both queued for Rigby joint SIGN → Chris routing per envelope §11.2 sequence.

---

**End of harvest plan. B1 D-RATIFIED at S2823 turn ~14. Chris additional directive §10.4 elevates evidence-integrity discipline to LOAD-BEARING. NEXT: Rigby joint SIGN on ABSTAIN_POLICY_PROPOSAL (Track B B3).**

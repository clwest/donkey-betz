---
title: "Arc I-0200 — RAG Corpus Substrate Maturity Gradient (Stage 1; contingency-gated seed with Authority per-plane posture fallback)"
status: active
authority: implementation-scoping
arc_id: I-0200
arc_slug: rag_corpus_substrate_maturity
fallback_arc_slug: authority_per_plane_posture
stage: 1
stage_state: active
session_opened: 2701
opened: 2026-07-07
ratifier: chris
first_arc_override: false
second_arc_selection_via: rigby-sign-then-chris-agree-all (per IOS §11.2 Step 6 default routing + §11.3 subsequent-arc extension of first-arc-override discipline)
seed_type: contingency-gated (default IB-2199-T0-01 IF Stage 1 confirms severability from IB-2199-BOR-01; ELSE auto-switch to IB-1999-T0-01)
default_intake_seed: [IB-2199-T0-01]
fallback_intake_seed: [IB-1999-T0-01]
default_companion_evaluation: [IB-2199-T1-01, IB-CXP10-T1-03]
fallback_companion_evaluation: [IB-1999-T1-01, IB-1999-T1-02, IB-1999-T1-03, IB-CXP10-T1-01]
severability_gate: IB-2199-BOR-01 (RAG search_docs + kb_tool retrieval end-to-end verification; audit §2.5; BLOCKED_ON_RESEARCH per BACKLOG:346)
arc_pin: pa-1b76ee75adbf4031
arc_pin_label: ios-arc-open-I-0200
arc_pin_minted: 2026-07-07
paused_research_pin: pa-44a6eb70d8814e34 (T4 Group 1700 Observability — preserved as tools/pa_local.sh comment above --conversation line per §15.14)
retired_pin_prior: pa-6a4e2eff5594486b (ios-arc-open-I-0200-sign-review; retired at Chris Agree-All 2026-07-07 per RATIFICATION_2026-07-07 §3 lifecycle)
selection_sign_summary: Rigby SIGN-with-edits MED confidence; 8 folds F1-F8 ratified via Chris Agree-All 2026-07-07
adr_corpus_precondition: SATISFIED (docs/adr/ + ADR-0001-establish-adr-corpus.md status=accepted on main via Arc I-0100 PR #2948)
ratification_record: docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md
ios_status_at_open: active v1.5 (v1.5 shipped 2026-07-06 via PR #2952 — design-prep first-class artifact rule)
companion_docs:
  - docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md
  - docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md
  - docs/research/domains/rag_document_loading/2103_rag_document_loading_retrieval_authority_framework_corpus_governance_design.md
  - docs/research/domains/rag_document_loading/2104_rag_document_loading_behavior_substrate_structured_observation_integration.md
  - docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md
  - docs/research/implementation/BACKLOG.md
  - docs/research/implementation/IMPLEMENTATION_DEBT.md
  - docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md
  - docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md
  - docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md
  - docs/research/OPEN_ARCS.md
  - docs/topics/personal-assistant.md
verifier_loop: |
  Stage 1 (2026-07-07): drafted by Claude Code following Chris's directive
  "Open Stage 1 scoping for I-0200 using this ratified contingency structure."
  Draft consumed: RATIFICATION_2026-07-07 §2 Axis 2–5 (Chris Agree-All on
  Rigby's SIGN-with-edits card); 2199 xx99 canonical summary §1 + §5 canonical
  seam statement + §8 T-slot follow-on queue; 1999 xx99 §17.1 per-plane posture
  map (fallback path); BACKLOG.md IB-2199-T0-01 + IB-2199-T1-01 + IB-CXP10-T1-03
  + IB-2199-BOR-01 + IB-1999-T0-01 + IB-1999-T1-01/-02/-03 + IB-CXP10-T1-01
  rows; IMPLEMENTATION_DEBT.md IDBT-0001 resolution paths (2199 slice for
  default path, 1999 slice for fallback path).
  Routed to Rigby SIGN Cycle 1 on fresh arc-scoped pin pa-1b76ee75adbf4031
  per IOS §7.2 single-batch × 4-Q cadence 2026-07-07. Rigby returned
  SIGN-with-edits MED-HIGH overall (Q1 SIGN-with-edits 0.83 + Q2 SIGN-with-edits
  0.78 + Q3 SIGN-clean 0.86 + Q4 SIGN-with-edits 0.80). Six concrete folds
  F9-F14 landed pre-Chris-ratification (F9 §3.1 rename timing; F10 §3.1
  grep/replace repo-wide; F11 §9.3 UNKNOWN operational criterion; F12 §9.3
  evidence floor one-citation-per-YES; F13 §10 CURRENT_STAGE token; F14
  §7.2 executable rollback commands). No BLOCKED verdicts; Cycle 2 not
  requested.
  Anti-context-drift: this doc is authored by session slug
  `claude-arc-i0200-stage1-open`; if a future session remembers different
  fold semantics than what appears here, this doc is truth per IOS §15.7.
---

# Arc I-0200 — RAG Corpus Substrate Maturity Gradient

**Stage 1 — status `active`; current `stage: 1, stage_state: active` (Stage 1 opened 2026-07-07 via arc-open bundle PR per Chris directive following Rigby SIGN-with-edits ratification via "Agree All" 2026-07-07). This scoping doc encodes a Rigby-ratified contingency-gated seed — the arc EITHER proceeds with `IB-2199-T0-01` (RAG corpus substrate maturity gradient) IF Stage 1 confirms severability from `IB-2199-BOR-01`, OR automatically switches to `IB-1999-T0-01` (Authority per-plane posture) as the fallback seed per RATIFICATION_2026-07-07 §2 Axis 2 + Axis 5.**

Template: Playbook §11.1 9-section parent-scoping template with IOS v1.5 §4.3 substitutions (§3 taxonomy → intake items; §5 child mission → PR sequence; §7 anti-scope → anti-scope + reversibility + risks; §9 next step → next step + ADR checkpoint + severability determination method; §10 added Stage checklist snapshot).

---

## 1. Why this arc

Five signals converge, drawn from `2199_rag_document_loading_canonical_summary.md` §1 canonical verdict at HEAD `5d16a662` and the 1799 → 2199 → 2699 sequence:

1. **RAG corpus is design-complete + execution-pending.** 2199 xx99 §1 canonical seam statement: *"Rigby's RAG corpus IS a design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots — in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete."* This is a **CX-P10** SPEC_COMPLETE + runtime-scaffolding pattern per IOS §3.1.b. The maturity classification IS the posture ADR.

2. **Rigby's usability depends on it.** MEMORY rules `feedback_docs_cascade_at_every_close`, `feedback_cascade_pr_must_include_embed_step`, and `feedback_docs_pipeline_4_step_cascade` all bind RAG corpus freshness to Rigby's search + research-continuity quality — Chris's ratified top-line goal per RATIFICATION_2026-07-06 §1.

3. **A live-incident is already captured.** 2199 xx99 §14 F5 (in P4 audit) documents a live retrieval-surface disagreement between `search_docs` (returned 0 chunks with `excluded_missing_provenance: 7`) and `kb_tool.semantic_search` (returned 12 chunks on the same query) — captured DURING S2104 arc-open verifier probe 2026-07-05. This is the same subject as `IB-2199-BOR-01` and the severability gate this arc must adjudicate.

4. **Second-arc selection ratified via SIGN → Chris Agree-All.** Per RATIFICATION_2026-07-07 §2, Chris ratified Rigby's SIGN-with-edits recommendation. Rigby's meta-argument at Q5 flagged that `IB-1999-T0-01` (Authority per-plane posture) is a "sneak-strong" fallback — enforceable posture ADR reducing blast radius across every downstream system including RAG/tooling. The contingency structure captures both outcomes without requiring re-ratification if Stage 1 severability determination flips the seed.

5. **T4 Group 1700 Observability research arc remains paused.** Per IOS §15.3 phase-transition supersession. No same-surface research conflict at arc-open. Per §9.1, if T4 opens mid-Arc-I-0200, Arc I-0200 pauses at its current stage.

---

## 2. Existing inventory tells us

### 2.1 Default path (IB-2199-T0-01 RAG corpus substrate maturity)

- **`docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md`** (canonical, `status: active` at HEAD `5d16a662`; Rigby SIGN CLEAN 2 STRENGTHEN + 2 CLEAN Q1-Q4; Chris "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05): §1 canonical seam statement; §5.1 canonical seam verbatim; §8 T-slot follow-on queue (T22 + T13 + 6 T1 + 9 T2 + 2 T3).
- **`docs/research/domains/rag_document_loading/2103_...retrieval_authority_framework_corpus_governance_design.md`**: 8-axis retrieval authority framework (D2100.8, RATIFIED-BY-PARENT); 3-part conflict-resolution rule (D2100.9 metadata contract 9 core-required + 2 core-available + 3 doc-type profiles); 5-state artifact lifecycle model (F7); two-employee ownership shape (F6 Rigby EXECUTE + CoS RECOMMEND).
- **`docs/research/domains/rag_document_loading/2104_...behavior_substrate_structured_observation_integration.md`**: D2100.7 ELEVATE hypothesis → provisional contract on 3-incident diversity+actionability criterion (S1234 + S1802 + F5 live-incident); D2100.10 Corpus Health Score = **(c) standing metric with phased rollout** (14 dimensions per §14.3).
- **`docs/topics/personal-assistant.md`**: RAG surfaces (`search_docs` + `kb_tool.semantic_search`) live in PA turn-context enrichment (Cat F ↔ Cat D boundary per 1399 §6.3 open).
- **`docs/KNOWLEDGE_PIPELINE.md`**: existing narrative on 4-step cascade + provenance emphasis.
- **`PLATFORM_INVENTORY.md`** at `e617af59` 2026-07-05: PA tools 113 schemas + 156 registered handlers; 585 concrete models; Documents + DocumentEmbedding as the substrate spine.

### 2.2 Fallback path (IB-1999-T0-01 Authority per-plane posture)

- **`docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md`** §17.1: per-plane posture map — 5 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN. Design-state SPEC_COMPLETE (per BACKLOG:106).
- **`docs/AUDIT_FINDINGS.md`** — authority-enforcement patterns tracked in §14.6 CX-P10 inventory.
- **`docs/topics/employee-os.md`**: `JobContract` runtime-owner assignments; `MissionRunner` orchestrator; `OpsRun(domain='mission')` + `OpsRunEvent` audit rows. Authority enforcement runs inside the Employee OS mission substrate.
- **`docs/EMPLOYEE_OS_PRIMITIVES.md`**: canonical anti-duplication rules that constrain fallback-path ADR authoring.

### 2.3 Selection SIGN + Chris Agree-All (both paths)

- **`RATIFICATION_2026-07-06_first_queue.md`**: tier-band ratification + Arc I-0100 first-arc override precedent.
- **`RATIFICATION_2026-07-07_second_arc_I-0200.md`**: this arc's ratification record. §2 Axis 2 default seed; Axis 5 automatic contingency; Axis 3 + Axis 6 +2 bump withdrawal; Axis 4 companion-row admission rules.
- **`BACKLOG.md`** at HEAD 678a7595: rows enumerated in §3 below.

### 2.4 Cross-domain audit (both paths)

- **`docs/research/platform/cross_domain_integration_audit.md` §14** current through §14.17 refresh (2026-07-06); §2.5 hosts IB-2199-BOR-01 (RAG retrieval verification) rows.
- Arc I-0200 close (Stage 6) MUST append §14.N delta per IOS D10 hard gate — matching Arc I-0100's discipline.

---

## 3. Intake items admitted to this arc (§4.3 substitution for §3)

### 3.1 Ratified seed rows — CONTINGENCY-GATED (RATIFICATION_2026-07-07 §2 Axis 2 + Axis 5)

Chris ratified TWO parallel seed rows via "Agree All" — exactly one becomes the arc's IN_ARC seed at Stage 1 severability determination time.

| Path | intake_id | title | source_ref | risk_class | design_state | affected_surfaces | expected_ship_size |
|------|-----------|-------|-----------|-----------|--------------|------------------|--------------------|
| **Default** | `IB-2199-T0-01` | Ratify RAG corpus substrate maturity gradient (spec-complete/execution-pending) | 2199 §1 + §5.1 canonical seam statement + §8 T-slot queue | `NEEDS_ADR` (routes via §3.1.b downgrade path — `spec_ref` absent in BACKLOG row schema) | `SPEC_COMPLETE` | `docs/adr/ADR-000N-rag-corpus-substrate-maturity-gradient.md` (new); `docs/topics/knowledge-pipeline.md` (potential refresh at close); no code change (ADR is spec-only maturity classification) | S (docs-only ADR ~200–400 LOC) |
| **Fallback** | `IB-1999-T0-01` | Ratify Authority Enforcement per-plane posture (5 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN) | 1999 §17.1 | `NEEDS_ADR` (routes via §3.1.b downgrade path) | `SPEC_COMPLETE` | `docs/adr/ADR-000N-authority-per-plane-posture.md` (new); `docs/topics/employee-os.md` (potential refresh at close); no runtime code change (ADR is posture-only) | S (docs-only ADR ~200–400 LOC) |

**Severability gate (Stage 1 exit condition):** Stage 1 MUST determine whether `IB-2199-T0-01` is severable from `IB-2199-BOR-01` (RAG `search_docs` + `kb_tool` retrieval end-to-end verification; BACKLOG:346; audit §2.5). Severability determination method is at §9.3 below.

- **If severable:** `IB-2199-T0-01` flips `TRIAGED → IN_ARC (I-0200)` at Stage 1 close; `IB-1999-T0-01` remains `TRIAGED` for a future arc.
- **If not severable:** `IB-2199-T0-01` reclassifies `TRIAGED → BLOCKED_ON_RESEARCH` at Stage 1 close (with cross-reference to `IB-2199-BOR-01`); `IB-1999-T0-01` flips `TRIAGED → IN_ARC (I-0200)`; arc folder renames `rag_corpus_substrate_maturity/ → authority_per_plane_posture/`; scoping doc frontmatter flips `arc_slug: rag_corpus_substrate_maturity → authority_per_plane_posture`.

**F9 clarification (Rigby SIGN Cycle 1 fold):** Folder rename happens **only after** P1 severability determination is Chris-ratified — not at Stage 1 exit and not during Stage 1 SIGN Cycle 1. Mid-review churn is prevented by strict ordering: (a) P1 severability determination drafted; (b) Rigby SIGN on determination; (c) Chris ratifies; (d) rename executes as a discrete PR-1-close commit. Until step (d) commits, the arc folder remains `rag_corpus_substrate_maturity/` regardless of the determination's leaning.

**F10 clarification (Rigby SIGN Cycle 1 fold):** If rename executes at step (d), rename requires a **repo-wide grep/replace of `rag_corpus_substrate_maturity/` path references** across `docs/research/OPEN_ARCS.md`, `00-START-NEXT-SESSION.md`, `docs/research/implementation/BACKLOG.md` (arc-open history + companion rows), any newly-added I-0200 docs, any cross-arc references in `docs/research/domains/`, and the frontmatter `arc_slug` + `title` of this scoping doc. Grep/replace committed as part of the same PR that ships the folder rename; cross-references verified via `rg 'rag_corpus_substrate_maturity' docs/` returning zero matches post-rename.

### 3.2 Candidate companion rows — Default path (evaluated in Stage 1, NOT auto-admitted per Axis 4)

| intake_id | title | source_ref | evaluation posture |
|-----------|-------|-----------|--------------------|
| `IB-2199-T1-01` | Implement retrieval-authority framework governance (spec-complete; execution pending) | 2199 §1 + §8 T-slot (T18/T19) | Stage 1 evaluates whether T22 metadata contract validation prerequisite is Stage-2-admissible OR post-arc. Companion admit only if T22 is deemed in-arc-schema-work (no runtime execution per Chris directive "No runtime code" — pure schema-shape addition). |
| `IB-CXP10-T1-03` | Wire RAG design-complete runtime scaffold | audit §14.6 CX-P10 (2199 §1) | Stage 1 evaluates whether scaffold code IS runtime code (which Chris explicitly disallowed at ratification) OR pure config/wiring (admissible). Default posture: HOLD OUT (Chris directive is explicit — "No runtime code"). |

**Companion admission binary outcome (per Axis 4):**
- **Admit into arc:** row becomes in-arc scope; enters Stage 2 sequence.
- **Hold out:** row remains backlog; may be re-tiered post-arc.

### 3.3 Candidate companion rows — Fallback path (evaluated in Stage 1, NOT auto-admitted per Axis 4)

| intake_id | title | source_ref | evaluation posture |
|-----------|-------|-----------|--------------------|
| `IB-1999-T1-01` | Implement `enforce_authority_mode` field toggle (ABSENT at HEAD; blocks enforcement dispatch) | 1999 §14.3 P4 F5 + CX-P10 | **F8 blocker-type classification MANDATORY (per Axis 4).** Stage 1 must classify: (a) posture-clarity blocker → discharged by `IB-1999-T0-01` ratification → admit in-arc; (b) unknown-fact blocker → remains BOR-blocked → hold out (future research arc required). |
| `IB-1999-T1-02` | Wire KillSwitch dispatch enforcement across 4 REQUIRED insertion boundaries | 1999 §1 + P3 §7.4.1 | Companion admit posture: TRIAGED, `NEEDS_ADR`. Stage 1 evaluates whether cross-arc coordination with Group 1900 CX-P10 spec is Stage-2-admissible or post-arc; runtime code exclusion may force hold-out. |
| `IB-1999-T1-03` | Establish authority constraint at PublishGate composition | 1999 T1 R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION | Stage 1 evaluates whether this is spec-only (admit) OR spans code (hold out per Chris "No runtime code" directive). |
| `IB-CXP10-T1-01` | Wire Authority Enforcement runtime binding (post-1999 spec-complete) | audit §14.6 CX-P10 (1999 §1) | Default posture: HOLD OUT (explicit runtime wiring — Chris "No runtime code" directive). |

### 3.4 Deferred (NOT admitted to Arc I-0200 under either path)

- **`IB-2199-T1-01`** (default path evaluation): if T22 dependency chain forces runtime work, hold out.
- **`IB-CXP10-T1-03`** (default path): scaffold execution work; hold out per Chris "No runtime code."
- **`IB-1999-T1-02` + `IB-1999-T1-03` + `IB-CXP10-T1-01`** (fallback path evaluation): if any spans runtime code, hold out per Chris directive.
- **`IB-2199-BOR-01`** severability outcome: if determined not severable, it remains BLOCKED_ON_RESEARCH pending a research arc; does NOT enter this arc's scope regardless of default-vs-fallback path taken.
- **T22 D2100.9 metadata contract validation (from 2199 §8 T-slot Track B)**: pure schema-shape gate; separate arc candidate. Named here only because default path evaluation must decide admission.
- **T-D2100.11 F2 retrofill AFTER PROD probe**: LOCAL-only guardrail forbids prod probes without Chris path. Hold out under either path.
- **Any Cat A/B/C/D drift refresh from 2199 §8 (T26a Detect-and-Flag; T27 SIGN preamble gate; T29 Corpus Health Score dashboard)**: runtime code + observability substrate — hold out per Chris directive AND LOCAL-only guardrail.

### 3.5 IDBT-0001 discharge scope

Per IMPLEMENTATION_DEBT.md IDBT-0001 resolution_path Option 2 (arc-scoped incremental), Arc I-0200 discharges either:
- **The 2199 slice** (default path — if severable): documents which 2199 §8 T-slot rows are candidate companions (§3.2), which are held out (§3.4), and which are 3rd-tier debt requiring separate arc.
- **The 1999 slice** (fallback path — if not severable): documents which 1999 §8 T-slot rows are candidate companions (§3.3), which are held out (§3.4).

Discharge in either case marks known-un-enumerated rows in the affected domain as CROSS-REFERENCED-NOT-ADMITTED at Stage 6 close.

---

## 4. Arc-vs-single-PR recommendation

**Arc recommended** (not single-PR) — under EITHER path. Rationale:

- **NEEDS_ADR + SPEC_COMPLETE + spec-only-in-arc scope** is a shape that maps to: P0 Stage 1 arc-open bundle (this PR) → P1 severability determination + Stage 1 exit-gate ratification → P2 ADR authoring PR (default: RAG maturity ADR; fallback: Authority per-plane posture ADR) → P3 Stage 6 close bundle (docs cascade + audit §14.N delta + BACKLOG flips).
- Single-PR path cannot accommodate the Stage 1 severability determination discipline — it must produce evidence + Chris ratification of the determination before ADR authoring opens.
- Rollback is one-toggle simple: revert the ADR PR reverts the substrate maturity claim (default) or the posture claim (fallback). No migration; no data change; no fleet-key surface.
- Regression risk is bounded: docs-only content, no runtime execution.

**Estimated arc runtime:** 2–4 sessions.

- Stage 1 = 1 session (this doc + Rigby SIGN Cycle 1 + Chris Agree-All ratification).
- Stage 2 = 1–2 sessions (severability determination first; then ADR authoring per §4.3.a design-prep first-class artifact rule; Rigby SIGN + Chris "agree all" on ADR).
- Stage 3 = SKIPPED (docs-only ADR has no runtime pre-flight).
- Stage 4 = merged into Stage 2 (ADR PR IS the shipping vehicle).
- Stage 5 = light verify (Rigby exercises the corpus per the ratified maturity claim OR authority posture — read-only probe).
- Stage 6 = 1 session (close doc + cascade + audit §14.N delta).

---

## 5. Planned PR sequence (§4.3 substitution for §5)

Sequenced by dependency + ADR gate. All PRs cite `intake_id` + xx99 §N in body. All PRs pass §5.2 pre-merge gates.

| PR # | Discharges | Depends on | Size | Files touched (est.) | ADR gate | Rollout |
|------|-----------|------------|------|---------------------|---------|---------|
| **P0** | Stage 1 arc-open bundle (this PR): scoping doc + RATIFICATION record + BACKLOG.md contingent flips + OPEN_ARCS.md In-progress row + 00-START-NEXT-SESSION.md refresh + `tools/pa_local.sh` rotation. NOT an intake row; state-plumbing. | none | S (~500 LOC docs + state) | `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` (new), `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md` (new), `docs/research/implementation/BACKLOG.md` (arc-open history + contingent-status rows), `docs/research/OPEN_ARCS.md` (In-progress row insert), `00-START-NEXT-SESSION.md` (overwrite), `tools/pa_local.sh` (rotation) | none | Straight ship (docs+state); pre-PR cascade co-located per §12.5 |
| **P1** | Stage 1 severability determination + Stage 1 exit-gate ratification. Produces `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md` (default path) OR triggers auto-switch to fallback path (rename folder + flip frontmatter). | P0 merged | S (~300 LOC docs) | Severability determination doc + scoping frontmatter `stage_state: active → exit-gate-cleared` + BACKLOG contingent-row resolution (2199-T0-01 IN_ARC or BLOCKED_ON_RESEARCH; 1999-T0-01 flipped inverse). | none | Straight ship (docs); Rigby SIGN on severability determination; Chris Agree-All ratifies |
| **P2** | ADR authoring per severability outcome. **Default:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md` per IOS v1.5 §4.3.a mandatory design-prep + `docs/adr/ADR-000N-rag-corpus-substrate-maturity-gradient.md`. **Fallback:** `docs/research/implementation/authority_per_plane_posture/I-0200_design_prep_authority_per_plane_posture.md` + `docs/adr/ADR-000N-authority-per-plane-posture.md`. | P1 merged + Stage 1 exit ratified | S (~400–800 LOC docs) | ADR + design-prep + potential topic doc refresh (`docs/topics/knowledge-pipeline.md` default OR `docs/topics/employee-os.md` fallback) | ADR authored per §4.3 Stage 2; SIGN cycle 1 4-Q single-batch per §7.2 | Straight ship (docs); Rigby SIGN + Chris Agree-All ratifies ADR-N accepted |
| **P3** | Arc canonical close doc `I-020099_..._implementation_close.md` (default: `I-020099_rag_corpus_substrate_maturity_implementation_close.md`; fallback: `I-020099_authority_per_plane_posture_implementation_close.md`) + `cross_domain_integration_audit.md §14.N` refresh (D10 hard gate) + 5-step docs cascade + BACKLOG rows flip `IN_ARC → SHIPPED` + `pr_refs` populated + IMPLEMENTATION_DEBT.md discharge record + `OPEN_ARCS.md` row flip In-progress → Closed. | P2 merged + Stage 5 light verify complete | M (docs only) | 5–10 docs | none | Straight ship (docs); §12.5.d cascade evidence block in PR body |

**Not shipped in this arc (routed elsewhere) — DEFAULT PATH:**

- **T22 D2100.9 metadata contract validation runtime enforcement** — 2199 §8 Track B canonical schema gate. Pure schema-shape gate; if the ADR's execution-pending clause names T22 as prerequisite, T22 routes to a separate downstream arc.
- **T18 axis-scoring service + T19 conflict-resolution rule engine + T21 lifecycle state machine + T29 Corpus Health Score dashboard** — 2199 §8 T1/T2 runtime items; runtime work; Chris "No runtime code" directive precludes.
- **T26a/T26b retrieval-surface consistency Detect-and-Flag / Guarded Auto-Remediate + T27 SIGN preamble corpus-hygiene gate** — 2199 §8 T1 items; runtime work; hold out.

**Not shipped in this arc — FALLBACK PATH:**

- **`IB-1999-T1-01` runtime toggle implementation** — F8 blocker-type classification may admit as spec-only companion (if posture-clarity) but runtime code remains post-arc.
- **`IB-CXP10-T1-01` Authority Enforcement runtime binding** — explicit runtime wiring; post-arc follow-on.

---

## 6. Parked candidate issues

- **Severability determination method precedent.** Whether Stage 1 severability determination should be a codified IOS §4.3 Stage 1 exit-checklist item (single trigger from this arc) is deferred to a dedicated IOS-patch session. Awaiting second trigger before v1.6 §4.3 proposal.
- **Contingency-gated arc seed pattern.** Whether contingency-gated arc opens (two-outcome seed determined at Stage 1) should be a codified IOS §4.3 pattern is deferred to a dedicated IOS-patch session. Single trigger from this arc; awaiting second.
- **Rigby's second consecutive stronger-than-Claude first-arc argument.** RATIFICATION_2026-07-06 §6 flagged this as single-trigger. RATIFICATION_2026-07-07 §6 promotes this to TWO-trigger. IOS §11.3 amendment candidate (name Rigby's arc recommendation as a required accompaniment to Claude's ranking). Codification proposal deferred to a dedicated IOS-patch session — do NOT bundle into Arc I-0200 scope.
- **Bump-withdrawal discipline (F5).** Positive evidence citation as prerequisite for §3.3 +2 cross-domain bump. Single trigger; awaiting second.
- **`IB-2199-BOR-01` research-arc scope.** If severability determination flips to "not severable," a future research arc must discharge BOR-01. Not scoped here.
- **Follow-on RAG runtime execution arc.** Whichever way severability determines, 2199 §8 T1/T2 runtime items (T18/T19/T21/T22/T26a/T26b/T27/T29) remain post-arc. Candidate for a distinct future implementation arc (`I-0300_rag_runtime_execution` or similar) once Chris ratifies scope.
- **Follow-on Authority runtime binding arc.** For CX-P10 T1-01 discharge; post-arc follow-on.

---

## 7. Anti-scope + reversibility guardrails + risks (§4.3 substitution for §7)

### 7.1 Anti-scope — this arc does NOT touch

1. **No runtime code changes.** Chris directive at RATIFICATION_2026-07-07 §2 Axis 7 ratification comment: *"No runtime code. No Stage 2 ADR. No companion-row admission until Stage 1 proves it."* Interpretation: docs-only ADR is Stage 2's shape; "No Stage 2 ADR" means no ADR authoring OPENS until Stage 1 severability determination closes. All runtime code is anti-scope for this arc regardless of path.
2. **No prod verification.** PR #2972 LOCAL-only operating-model guardrail in force. Any prod-touching work requires Chris explicitly providing a live prod access path.
3. **No BOR-01 research work.** Severability determination is Stage 1's job; discharging BOR-01 is a research task requiring a separate research arc (T4-tier or Research OS re-entry). Arc I-0200 does not perform the discharge, only the determination.
4. **No cross-arc T-slot enrollment.** 2199 §8 T-slots (T18/T19/T21/T22/T26a/T26b/T27/T29) or 1999 §8 tail rows do NOT auto-enroll under either path unless companion evaluation explicitly admits them.
5. **No Employee OS mission substrate changes.** Fallback path Authority posture ADR is spec-only; does NOT change `JobContract` / `MissionRunner` / `OpsRun` at runtime.
6. **No PA tool surface changes.** RAG search surfaces (`search_docs` + `kb_tool.semantic_search`) or Authority binding surfaces stay untouched at runtime.
7. **No cascade lifecycle event emission.** F7 zero-EventBus-emission from 2199 §14 does NOT get remediated in this arc; separate cross-arc coordination with Group 2000+ Event/Integration required.
8. **No provenance-index or lru_cache changes.** S1304 T-slot descendants (provenance-index rebuild cadence + lru_cache staleness) remain research-side.
9. **No cross-arc reconciliation-layer ownership decision (Group 2600 PA §9.1a).** T4 Group 1700 Observability paused-research scope; not touched.
10. **No Discord / frontend / mobile / fleet-federation surface changes.** Arc scope is documentation + ADR only.

### 7.2 Reversibility per PR

**F14 clarification (Rigby SIGN Cycle 1 fold) — executable rollback commands per PR** (replaces prose "Revert commit" with literal commands + toggle sequences):

| PR | Rollout pattern | Rollback command / toggle (executable) |
|----|-----------------|----------------------------------------|
| P0 | Straight ship (docs+state) | `git revert <P0_merge_commit_sha>` (produces revert PR); THEN: `bash tools/pa_local.sh "session_tool retire conversation_id='pa-1b76ee75adbf4031' force=true"`; THEN: manual edit of `tools/pa_local.sh` to restore `--conversation pa-44a6eb70d8814e34` + flip PRESERVED-AS-COMMENT block back to ACTIVE; THEN: manual edit of `BACKLOG.md` rows to unflip contingent-status annotations on `IB-2199-T0-01` (line 121) + `IB-1999-T0-01` (line 109). |
| P1 | Straight ship (docs) | `git revert <P1_merge_commit_sha>` — undoes severability determination doc; contingency restored to pending; `IB-2199-T0-01` + `IB-1999-T0-01` status unchanged (both remain TRIAGED-with-contingent-annotation from P0). |
| P2 | Straight ship (ADR) | `git revert <P2_merge_commit_sha>` — ADR unaccepted (ADR-N frontmatter flips `accepted → superseded`); `BACKLOG.md` row for whichever seed shipped unflips `IN_ARC → TRIAGED`; if fallback path taken, folder rename reverts via `git mv authority_per_plane_posture rag_corpus_substrate_maturity` + repo-wide grep/replace per F10 discipline in the revert PR. |
| P3 | Docs-only close PR; standard revert | `git revert <P3_merge_commit_sha>` — reopens arc; `OPEN_ARCS.md` row flips Closed → In-progress; `BACKLOG.md` rows flip `SHIPPED → IN_ARC`; cascade artifacts (`docs/INDEX.md` + `docs/_provenance.json`) require re-run via `python manage.py build_docs_index && python manage.py build_rag_corpus && python manage.py sync_docs_index_to_documents && python manage.py embed_documents --all-unembedded && python manage.py build_docs_provenance`. |

### 7.3 Risk register (per Arc I-0100 §7.3 F8 fold precedent — 3+ risks + mitigations + rollback triggers)

| Risk # | Risk | Severity | Mitigation | Rollback trigger |
|--------|------|----------|-----------|------------------|
| R1 | **Severability determination is subjective — Rigby SIGN disagrees with Claude's read** — the F3 fold says Stage 1 must "explicitly classify" BOR-01 as in-arc enabling vs external blocker, but the classification method itself has judgment risk. | MEDIUM | Method encoded at §9.3 below (three-question test with evidence citations); Rigby SIGN Cycle 1 on the determination MANDATORY before Chris ratification; if SIGN returns BLOCKED, run Cycle 2 with tighter method. Fallback path already ratified — determination outcome does not stall the arc. | If Rigby returns BLOCKED verdict twice, escalate to Chris directive to force one path. |
| R2 | **RAG BOR-01 live-incident (2199 §14 F5) is already-captured evidence that severability is FALSE** — the retrieval-surface disagreement is a real observed defect. A defensible reading is that any RAG maturity ADR that doesn't address it is paper posture. | HIGH | Per Rigby SIGN F1 + F3 folds: if the ADR-authored ratifies maturity classification WITHOUT committing to verification method, mark it PROVISIONAL; add "BOR-01 discharge is a Stage-2-post-ratification requirement" clause. If Stage 1 severability determination concludes NOT severable, auto-switch to fallback ratifies without harm. | Auto-switch to fallback triggers automatically per Axis 5. No manual rollback required. |
| R3 | **Fallback ADR authors Authority per-plane posture without addressing 5/8 PERMEABLE-BROKEN planes** — the fallback ADR could ratify posture without committing to remediation timelines, becoming paper posture. | MEDIUM | Per Rigby SIGN F8 fold: Stage 1 must classify `IB-1999-T1-01` blocker type (posture-clarity vs unknown-fact). If posture-clarity, admit as spec-only companion; ADR authoring pairs remediation posture with per-plane discharge timing (docs-only naming, not code). If unknown-fact, hold out; ADR ratifies posture-only with explicit "unknown-fact research-first" clause. | Chris directive on individual plane if posture proves under-specified. |
| R4 | **Chris "No runtime code" directive misinterpreted as blocking Stage 1 severability discipline itself** — Stage 1 might feel like "research work" and get held out. | LOW | Stage 1 severability determination IS documentation work (produces a determination doc). Not runtime code. Chris directive does not preclude it. | N/A — directive-scope check only. |
| R5 | **T4 Group 1700 Observability research arc re-opens mid-Arc-I-0200** | LOW | Per §4.4 + §9.1, Arc I-0200 pauses at current stage; Chris directive triggers | Arc-state pause; no rollback |
| R6 | **Rigby SIGN worker instability on Stage 1 severability determination SIGN routing** | LOW | Batch SIGN into ≤4 findings per prompt per MEMORY `feedback_rigby_sign_worker_instability_recovery`; fresh arc-scoped pin already minted (this arc's pin) reduces poisoning risk. If two consecutive fresh pins jam, fall back to Claude verifier-loop per RATIFICATION_2026-07-07 §2 Axis 2 precedent. | Retire jammed pin; mint fresh; batch-shrink per recovery playbook |

---

## 8. Decisions recorded (Chris-ratified 2026-07-07 at Stage 1 arc-open per Agree All)

- **Second-arc identity:** Arc `I-0200` per IOS §4.2 (`I-NNNN` prefix; sequential after `I-0100`).
- **Contingency-gated seed pattern:** Ratified default `IB-2199-T0-01` with automatic fallback to `IB-1999-T0-01` per RATIFICATION_2026-07-07 §2 Axis 2 + Axis 5.
- **Severability gate:** Ratified — Stage 1 must determine severability from `IB-2199-BOR-01` before Stage 2 opens.
- **F1 (Rigby SIGN cycle 1 fold, Chris ratified):** Treat `IB-2199-T0-01` as provisional pending severability; demote to BLOCKED_ON_RESEARCH if not severable.
- **F2 (Rigby SIGN cycle 1 fold, Chris ratified):** Re-score without contested boosts; do not let bumps decide arc identity.
- **F3 (Rigby SIGN cycle 1 fold, Chris ratified):** Stage 1 must classify `IB-2199-BOR-01` as in-arc enabling vs external blocker.
- **F4 (Rigby SIGN cycle 1 fold, Chris ratified):** If BOR is required, immediately switch seed to `IB-1999-T0-01` (no limbo).
- **F5 (Rigby SIGN cycle 1 fold, Chris ratified):** Withdraw §3.3 +2 bump unless positive cross-domain dependency evidence is cited.
- **F6 (Rigby SIGN cycle 1 fold, Chris ratified):** Deterministic fallback — if 2199 becomes blocked, 1999 becomes seed by mechanical rank.
- **F7 (Rigby SIGN cycle 1 fold, Chris ratified):** If severable but bump removed, re-rank; if 1999 outranks, seed = 1999 unless Chris overrides.
- **F8 (Rigby SIGN cycle 1 fold, Chris ratified):** For `IB-1999-T1-01`, Stage 1 must classify blocker type (posture-clarity vs unknown-fact) to decide admission.
- **F9 (Rigby SIGN Cycle 1 on Stage 1 scoping, Chris ratified via "Agree All" 2026-07-07):** Folder rename happens only after P1 severability determination is Chris-ratified; no mid-review churn.
- **F10 (Rigby SIGN Cycle 1 on Stage 1 scoping, Chris ratified via "Agree All" 2026-07-07):** Rename requires repo-wide grep/replace of `rag_corpus_substrate_maturity/` path references; committed as part of the same rename PR.
- **F11 (Rigby SIGN Cycle 1 on Stage 1 scoping, Chris ratified via "Agree All" 2026-07-07):** UNKNOWN operational criterion in §9.3 — cannot answer Q-Sev without runtime probe or BOR harness reference.
- **F12 (Rigby SIGN Cycle 1 on Stage 1 scoping, Chris ratified via "Agree All" 2026-07-07):** Evidence floor per Q-Sev YES — one direct quote OR file:line OR ADR-N section pointer required; absent citation → UNKNOWN → not severable.
- **F13 (Rigby SIGN Cycle 1 on Stage 1 scoping, Chris ratified via "Agree All" 2026-07-07):** §10 CURRENT_STAGE / CURRENT_GATE / CURRENT_STATUS single-line grep tokens added at top of checklist.
- **F14 (Rigby SIGN Cycle 1 on Stage 1 scoping, Chris ratified via "Agree All" 2026-07-07):** §7.2 rollback commands replaced with executable git + tools/pa_local.sh + management-command sequences.
- **Companion-row admission rule:** Ratified — companion rows evaluated in Stage 1, NOT auto-admitted; binary outcome (admit into arc / hold out).
- **Runtime scope exclusion:** Ratified — "No runtime code. No Stage 2 ADR. No companion-row admission until Stage 1 proves it." (Chris directive text.)
- **ADR corpus precondition (per IOS v1.5 §4.3):** SATISFIED via `docs/adr/` + `ADR-0001-establish-adr-corpus.md` on main from Arc I-0100 PR #2948.
- **LOCAL-only operating model:** Ratified — PR #2972 guardrail carries forward; no prod verification without Chris explicitly providing live prod access path.
- **Pin lifecycle:** Ratified — `pa-6a4e2eff5594486b` retired 2026-07-07 post-Chris-Agree-All; `pa-1b76ee75adbf4031` (this arc's arc-scoped SIGN pin) minted 2026-07-07 and covers Stage 1 → Stage 6 lifecycle.

---

## 9. Next step + ADR checkpoint + severability determination method (§4.3 substitution for §9)

### 9.1 Next step

**Post-P0-merge sequence:**

1. **Rigby SIGN Cycle 1 on this scoping doc** routed on arc-scoped pin `pa-1b76ee75adbf4031` per IOS §7.2 single-batch × 4-Q cadence. Q1-Q4 pressure-test the contingency structure + companion-row rules + severability determination method + §10 checklist snapshot. Rigby returns SIGN-clean / SIGN-with-edits / BLOCKED verdict per Q + overall confidence + concrete fold edits if needed.
2. **Apply any Rigby folds** to this doc in-branch (verifier-loop pattern per MEMORY `feedback_verifier_loop_pattern`).
3. **Present Rigby SIGN response to Chris** for Stage 1 exit-gate ratification via "Agree All" or explicit fold-by-fold response.
4. **Post-Chris-ratification:** frontmatter flips `status: draft → active`; scoping doc committed to `main` via arc-open PR merge.
5. **Stage 1 → Stage 2 gate:** Stage 1 exit-gate cleared triggers **P1 severability determination session** (next session; not this session). Severability determination method executed per §9.3 below.

### 9.2 ADR checkpoint (per §4.3 substitution)

Two paths — either single ADR authored in Stage 2:

- **Default (severable):** `ADR-000N-rag-corpus-substrate-maturity-gradient.md` — ratifies the 2199 §5.1 canonical seam statement as platform ADR. `NEEDS_ADR` per BACKLOG:118; requires design-prep artifact per IOS v1.5 §4.3.a. Design-prep doc: `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md`.
- **Fallback (not severable):** `ADR-000N-authority-per-plane-posture.md` — ratifies the 1999 §17.1 per-plane posture map (5 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN) as platform ADR. `NEEDS_ADR` per BACKLOG:106; requires design-prep artifact per IOS v1.5 §4.3.a. Design-prep doc: `docs/research/implementation/authority_per_plane_posture/I-0200_design_prep_authority_per_plane_posture.md`.

**ADR corpus precondition** SATISFIED at Arc I-0200 open (Arc I-0100 PR #2948 shipped `docs/adr/` + `ADR-0001-establish-adr-corpus.md status=accepted`).

### 9.3 Severability determination method (Stage 1 exit-gate content)

Stage 1 severability determination against `IB-2199-BOR-01` uses a **three-question test** with evidence citations. All three must be answerable "YES" for severability to hold; ANY "NO" or "UNKNOWN" triggers auto-switch to fallback path.

**Q-Sev-1: Can the maturity classification ADR be authored WITHOUT depending on BOR-01's verification results?**
- Evidence for YES: 2199 §1 canonical seam statement is already ratified via Rigby SIGN CLEAN + Chris "agree all" 2026-07-05. Its content ("spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots") does not depend on BOR-01. The ADR would simply CODIFY the ratified seam statement as platform ADR.
- Evidence for NO: BOR-01 audits the `search_docs` vs `kb_tool` retrieval-surface disagreement live-captured at 2199 §14 F5. If the maturity classification depends on ONE-OR-BOTH surfaces being trustworthy, then BOR-01 is a prerequisite.
- **Determination method:** Read 2199 §5.1 canonical seam statement verbatim; check whether the ADR claim relies on BOR-01-dependent surfaces OR merely classifies the DESIGN gradient. If pure design gradient → YES; if runtime surface trust → NO.

**Q-Sev-2: Would ratifying the maturity ADR without BOR-01 discharge produce enforceable posture?**
- Evidence for YES: The ADR would ratify a design-only maturity claim; enforcement is post-arc runtime work (T18/T19/T21/T22 tracked in 2199 §8). Ratification is a spec-completion checkpoint; enforcement is a separate PR sequence.
- Evidence for NO: If the ADR must ratify runtime enforcement claims (e.g., "the maturity gradient IS enforced at retrieval-time"), then BOR-01 is prerequisite because the surfaces must be verified as returning consistent results.
- **Determination method:** Draft one paragraph of the proposed ADR "Consequences" section; check whether any enforceable claim requires runtime verification. If enforceability is post-arc → YES; if enforceability is at-ratification → NO.

**Q-Sev-3: Is the audit-log evidence chain from Group 2100 xx99 sufficient to defend the ADR at Stage 5 Rigby-exercise?**
- Evidence for YES: 2199 §14 F5 live-incident + S1234 + S1802 form a 3-incident evidence chain that Chris ratified as the D2100.7 ELEVATION criterion. The evidence chain is durable + independently verifiable at ORM/git-log level. Rigby-exercise at Stage 5 would exercise the ADR's ratified maturity claim, not BOR-01's verification harness.
- Evidence for NO: The Rigby-exercise pattern for a maturity ADR is unclear absent a verification harness. If Stage 5 verify requires running the actual retrieval-surface consistency check, that IS BOR-01's discharge.
- **Determination method:** Draft one sentence of Stage 5 verification method for the proposed ADR; check whether it maps to a documentation cite OR to a runtime probe. If cite → YES; if probe → NO.

**F11 clarification (Rigby SIGN Cycle 1 fold) — UNKNOWN operational criterion:** UNKNOWN means the Stage 1 determination author cannot produce the required evidence artifact for that Q-Sev without referencing a runtime probe OR the BOR-01 verification harness. Concretely: if drafting the answer requires "we would need to run `manage.py <something>`" or "we would need to verify against a live index," that Q-Sev is UNKNOWN, not YES. Vibes-based YES answers are not admissible.

**F12 clarification (Rigby SIGN Cycle 1 fold) — evidence floor:** Each Q-Sev "YES" answer MUST cite ONE of the following as evidence:
- A direct verbatim quote from 2199 xx99 §N (or 2100/2101/2102/2103/2104 child audits) with section pointer, OR
- A file:line reference from `docs/KNOWLEDGE_PIPELINE.md`, `docs/topics/personal-assistant.md`, or another currently-`status: active` doc, OR
- A specific ADR-N section pointer from `docs/adr/` (currently only ADR-0001 through ADR-0003 exist).

Absent one of these citation types for a Q-Sev answer, the answer defaults to UNKNOWN → not severable per the outcome codification rule. This keeps the determination method non-hand-wavy.

**Outcome codification:**
- **All three YES:** Severable. Default path holds. Stage 1 exits with `IB-2199-T0-01` seed confirmed; Stage 2 opens on RAG maturity ADR authoring.
- **Any NO or UNKNOWN:** Not severable. Auto-switch to fallback path per Axis 5. `IB-2199-T0-01` reclassifies BLOCKED_ON_RESEARCH; `IB-1999-T0-01` becomes seed. Arc folder renames per F9 timing + F10 grep/replace discipline.

**Ratification of severability determination:** Determination doc drafted (per PR P1); Rigby SIGN Cycle 1 on the determination; Chris ratifies via "Agree All" or explicit override. If Chris overrides the mechanical outcome, Chris's directive supersedes the three-question test.

---

## 10. Stage checklist snapshot (per IOS v1.5 §4.3 substitution — added by IOS, NOT in Playbook §11.1)

Grep-friendly enumeration of every exit-gate item for every planned stage. One line each. A future Claude session can grep this section to determine current stage without interpretation.

**F13 clarification (Rigby SIGN Cycle 1 fold) — canonical cold-resume tokens** (single-line grep target so `grep CURRENT_STAGE docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` returns arc state without reading the checklist):

```
CURRENT_STAGE=1
CURRENT_GATE=P1_SEVERABILITY_DETERMINED_SEVERABLE_pending_Chris_directive_to_open_Stage_2
CURRENT_STATUS=P1-SIGN-with-edits-MED-HIGH-F15-F16-Chris-Agree-All-2026-07-07-IB-2199-T0-01-flipped-IN_ARC-I-0200
```

```
[STAGE 1 SCOPING] — status: exit-gate-cleared 2026-07-07 (Chris "Agree All" ratified all 7 axes + folds F9-F14)
  [x] Scoping doc drafted per IOS v1.5 §4.3 template + substitutions
  [x] Playbook §11.1 sections present: §1 + §2 + §3 + §4 + §5 + §6 + §7 + §8 + §9 + Appendix
  [x] §4.3 substitution §3 applied (intake items; contingency-gated seed pattern)
  [x] §4.3 substitution §5 applied (PR sequence P0/P1/P2/P3)
  [x] §4.3 substitution §7 applied (anti-scope + reversibility + risks)
  [x] §4.3 substitution §9 applied (next step + ADR checkpoint + severability determination method §9.3)
  [x] §4.3 substitution §10 added (Stage checklist snapshot — this section)
  [x] Contingency structure encoded (default IB-2199-T0-01 + fallback IB-1999-T0-01 with severability gate)
  [x] Companion-row evaluation rules encoded (Axis 4)
  [x] Fold list F1-F8 encoded in §8 Decisions recorded
  [x] Fresh arc-scoped SIGN pin minted (`session_tool.create_fresh label='ios-arc-open-I-0200'` → `pa-1b76ee75adbf4031`)
  [x] Selection SIGN pin `pa-6a4e2eff5594486b` retired via `session_tool.retire force=true`; retired=true; updated_count=4
  [x] `tools/pa_local.sh --conversation` rotated to `pa-1b76ee75adbf4031`; paused-research T4 pin preserved as `# PRESERVED AS COMMENT` block
  [x] Rigby SIGN Cycle 1 routed (single-batch × 4-Q per IOS §7.2) on pin pa-1b76ee75adbf4031 2026-07-07
  [x] Rigby SIGN Cycle 1 verdict recorded: SIGN-with-edits MED-HIGH overall (Q1 0.83 / Q2 0.78 / Q3 0.86 SIGN-clean / Q4 0.80); 6 folds F9-F14
  [x] Folds F9-F14 applied to scoping doc in-branch (F9 §3.1 rename timing + F10 §3.1 grep/replace note + F11 §9.3 UNKNOWN operational criterion + F12 §9.3 evidence floor + F13 §10 CURRENT_STAGE token + F14 §7.2 executable rollback)
  [x] Chris "Agree All" ratified all 7 axes + folds F9-F14 wholesale 2026-07-07 — Stage 1 exit-gate cleared
  [x] Scoping doc frontmatter flipped `status: draft → active` at Chris ratification 2026-07-07
  [x] §10 CURRENT_GATE token flipped to `Stage_1_EXIT_CLEARED_pending_P1_severability_determination`
  [ ] `OPEN_ARCS.md#In-progress` gains Arc I-0200 row (this bundle)
  [ ] BACKLOG rows contingent-flip encoded (IB-2199-T0-01 + IB-1999-T0-01 marked as contingency-gated seed candidates)
  [ ] BACKLOG arc-open history row added for I-0200
  [ ] 00-START-NEXT-SESSION.md overwritten to reflect Stage 1 in-progress + next SIGN cycle
  [ ] Cascade co-located per IOS v1.3 §12.5.a: build_docs_index + build_rag_corpus + sync_docs_index_to_documents + embed_documents --all-unembedded + build_docs_provenance run locally BEFORE arc-open PR
  [ ] §12.5.d PR-body cascade evidence block included
  [x] Scoping doc `status: draft → active` (frontmatter updated at Chris ratification 2026-07-07)

[STAGE 2 DESIGN-PREP + ADR (parameterized on severability outcome)]
  [x] Stage 1 exit-gate cleared (all above [x])
  [x] IOS v1.5 §4.3 Stage 2 Entry gate satisfied — ADR corpus precondition SATISFIED (Arc I-0100 PR #2948 shipped docs/adr/ + ADR-0001)
  [x] P1 severability determination doc drafted (`I-0200_severability_determination.md`); Q-Sev-1 + Q-Sev-2 + Q-Sev-3 answered with evidence
  [x] P1 Rigby SIGN Cycle 1 on severability determination — SIGN-with-edits MED-HIGH; F15 (Stage 5 verification scope documentation-cross-check-only lock) + F16 (companion outcomes not re-ratified by P1) applied
  [x] P1 Chris ratifies severability determination outcome via "Agree All" 2026-07-07
  [x] Path branch executed (SEVERABLE outcome): BACKLOG IB-2199-T0-01 TRIAGED → IN_ARC (I-0200); IB-1999-T0-01 remains TRIAGED for future arc
  [ ] Companion-row admission decisions recorded per Axis 4 (binary admit/hold-out per candidate row) — DEFERRED per Chris directive "Do not admit companion rows"; happens as a distinct Stage 2 opening event (or explicit Chris directive), not as part of P1
  [ ] P2 design-prep doc authored per IOS v1.5 §4.3.a mandatory design-prep rule — NOT STARTED per Chris directive "Do not author the ADR yet"
  [ ] P2 ADR authored (`ADR-000N-rag-corpus-substrate-maturity-gradient.md`) — MUST be PROVISIONAL per §6 required ADR shape from I-0200_severability_determination.md (Option a `status: accepted` + `provisional: true` + `provisional_reason: "BOR-01 undischarged"` OR Option b `status: provisional` with explicit ADR §1 definition)
  [ ] P2 Rigby SIGN Cycle 1 on ADR
  [ ] P2 Chris "agree all" or explicit ratification of ADR; ADR frontmatter flips to `status: accepted`
  [ ] P2 PR merged; BACKLOG row flips `IN_ARC → SHIPPED` with `pr_refs` populated + `adr_ref` populated per IOS §2.2 v1.4 Discipline B inline syntax

[STAGE 3 PRE-FLIGHT]
  [ ] SKIPPED (docs-only ADR has no runtime pre-flight; explicit note in close doc §7 rationale)

[STAGE 4 BUILD]
  [ ] MERGED INTO STAGE 2 (ADR PR IS the shipping vehicle; no separate build stage)

[STAGE 5 VERIFY]
  [ ] Rigby exercises the ratified ADR (read-only probe: corpus maturity claim OR authority posture map)
  [ ] Claude independently verifies via ORM / git log / file Read per MEMORY `feedback_claude_directs_rigby_then_verifies`
  [ ] Any regressions → route back to Stage 2 with fix plan
  [ ] Local-only guardrail respected — no prod probes

[STAGE 6 CLOSE]
  [ ] Canonical close doc authored (`I-020099_rag_corpus_substrate_maturity_implementation_close.md` OR `I-020099_authority_per_plane_posture_implementation_close.md`)
  [ ] `cross_domain_integration_audit.md §14.N` refresh entry appended (D10 hard gate)
  [ ] 4-step docs cascade run: `build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`
  [ ] `build_docs_provenance` run
  [ ] `embed_documents --all-unembedded` run; PR body cites chunk count as evidence per MEMORY `feedback_cascade_pr_must_include_embed_step`
  [ ] `OPEN_ARCS.md` row flipped In-progress → Closed
  [ ] BACKLOG rows flipped `IN_ARC → SHIPPED` with populated `pr_refs` + `adr_ref`
  [ ] IMPLEMENTATION_DEBT.md IDBT-0001 discharge slice recorded (2199 slice for default path OR 1999 slice for fallback path)
  [ ] Arc-scoped SIGN pin `pa-1b76ee75adbf4031` retired via `session_tool.retire force=true` (§7.2 isolation-pin discipline)
  [ ] `tools/pa_local.sh --conversation` restored to paused-research pin `pa-44a6eb70d8814e34` per IOS §15.14 restoration rule
  [ ] Chris "commit it" for Stage 6 exit
```

---

## Appendix — Frontmatter provenance

- **Second-arc identity ratification:** RATIFICATION §2 Axis 2 —
  `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
- **IOS text:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`
  v1.5 §4.3 Stage 1 template + substitutions + exit gate + ADR corpus
  precondition; §7.2 Stage 1 SIGN discipline; §11.2 Step 6 Rigby routing;
  §11.3 first-arc override + reversibility; §15.14 pin lifecycle.
- **xx99 sources:**
  - Default path: `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md`
    §1 canonical verdict + §5.1 canonical seam statement + §8 T-slot follow-on queue.
  - Fallback path: `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md`
    §17.1 per-plane posture map (5 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN).
- **Backlog seed:** `docs/research/implementation/BACKLOG.md`
  IB-2199-T0-01 (line 118) + IB-2199-T1-01 (line 238) + IB-2199-BOR-01 (line 346) + IB-CXP10-T1-03 (line 275) + IB-1999-T0-01 (line 106) + IB-1999-T1-01/-02/-03 (lines 216-218) + IB-CXP10-T1-01 (line 273).
- **Debt discharge:** `docs/research/implementation/IMPLEMENTATION_DEBT.md`
  IDBT-0001 resolution_path Option 2 (arc-scoped incremental discharge of 2199 OR 1999 slice depending on severability outcome).
- **Rigby SIGN selection record:** routed on pin `pa-6a4e2eff5594486b`
  2026-07-07 (retired same day); SIGN-with-edits MED overall confidence;
  8 folds F1-F8 applied to this scoping doc.
- **Chris Agree-All ratification of selection:** 2026-07-07 via Chat UI;
  captured verbatim in RATIFICATION_2026-07-07_second_arc_I-0200.md §2
  Axis 0-7.
- **MEMORY rules bound to this arc:** `feedback_docs_cascade_at_every_close`,
  `feedback_cascade_pr_must_include_embed_step`, `feedback_docs_pipeline_4_step_cascade`,
  `feedback_rigby_sign_worker_instability_recovery`,
  `feedback_verifier_loop_pattern`, `feedback_claude_directs_rigby_then_verifies`,
  `feedback_session_tool_retire_works`, `feedback_pa_local_verify_ownership`,
  `feedback_no_parallel_research_arcs`, `feedback_llm_autofills_boolean_params_with_false`
  (Q-Sev-3 evidence-chain analysis for QuerySet-heavy pattern applicability),
  `feedback_verify_before_deleting_dead_code` (Stage 2 ADR consequences section
  discipline), `feedback_content_presence_vs_quality` (ADR content vs runtime
  quality distinction is a Stage 2 discipline).

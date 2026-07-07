# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0200 STAGE 2 DESIGN-PREP RATIFIED; ADR-0004 BODY DEFERRED UNTIL DESIGN-PREP PR MERGES

**Refreshed 2026-07-07 (Stage 2 opened; design-prep authored; Rigby SIGN-with-edits MED-HIGH + Chris "Agree All" ratified; design-prep PR in flight).**

### What just happened (session-scope summary)

1. **Arc I-0100 closed** 2026-07-07 under LOCAL operating model (PR #2976 + #2977 + #2978 + #2979 all merged).
2. **Second-arc selection SIGN → Chris Agree-All** 2026-07-07. Selection SIGN pin `pa-6a4e2eff5594486b` retired. Ratification record at `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
3. **Arc I-0200 Stage 1 opened + merged** 2026-07-07 as `87dbd95a` via PR #2980. Rigby SIGN-with-edits MED-HIGH; folds F9-F14; Chris "Agree All". Arc-scoped pin `pa-1b76ee75adbf4031`.
4. **P1 severability determination CLOSED SEVERABLE + merged** 2026-07-07 as `c39db4394` via PR #2982 (superseded auto-closed #2981 post-#2980 base-branch-deletion). All three Q-Sev YES with F12 evidence citations from 2199 xx99 §1 lines 74/84/76. Rigby SIGN-with-edits MED-HIGH; folds F15-F16; Chris "Agree All". `IB-2199-T0-01` flipped `TRIAGED → IN_ARC (I-0200)`. Fallback path not triggered.
5. **Stage 2 opened + Design-Prep authored + Rigby SIGN + Chris Agree-All** 2026-07-07. Design-prep at `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md` per IOS v1.5 §4.3.a + Chris-directed arc-scoped IOS §14.2 workflow refinement (SIGN design-prep BEFORE ADR body — deviates from §4.3.a default; recorded in design-prep §9.2 Provenance). Rigby SIGN Cycle 1 SIGN-with-edits MED-HIGH (Q1 SIGN-clean 0.86 + Q2 SIGN-with-edits 0.78 + Q3 SIGN-clean 0.88 + Q4 SIGN-with-edits 0.74); folds F17 (C9 downgrade to recommended-ops-constraint) + F18 (Stage 5 verification interface tool-realistic — replaced `deliverable_tool.list` with `repo_tool.search` + `search_docs` + `kb_tool` + `repo_tool.read_file`) applied. Chris "Agree All" ratified Option 1 (verbatim 2199 §5.1 seam statement + two-field PROVISIONAL frontmatter + per-slot enumerated T-slots T22/T13/T18/T19/T21/T26a/T27/T29). Design-prep PR in flight.

### Phase

**`implementation`.** IOS `active v1.5` on `main`. **Active arc: I-0200 (Stage 2 `stage_state: design-prep-in-flight`; design-prep ratified; ADR-0004 body deferred until design-prep PR merges).**

### Active arc

**Arc I-0200 — RAG Corpus Substrate Maturity Gradient (default path locked; design-prep Option 1 ratified).**

### CURRENT_STAGE / CURRENT_GATE / CURRENT_STATUS (§10 cold-resume tokens)

```
CURRENT_STAGE=2
CURRENT_GATE=Stage_2_design_prep_RATIFIED_pending_design_prep_PR_merge_then_ADR-0004_body_drafting
CURRENT_STATUS=Design-prep-Rigby-SIGN-with-edits-MED-HIGH-F17-F18-Chris-Agree-All-2026-07-07-ADR-0004-body-DEFERRED-until-design-prep-PR-merges
```

### Ratified ADR-0004 shape (do NOT deviate without Chris directive)

- **Content:** verbatim 2199 xx99 §1 line 74 seam statement — "design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots — in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete."
- **Frontmatter (Option 1a):** `status: accepted` + `provisional: true` + `provisional_reason: "IB-2199-BOR-01 (RAG search_docs + kb_tool retrieval end-to-end verification) undischarged; post-ratification discharge required per Arc I-0200 P1 severability determination §6 constraint 2"`.
- **T-slot naming:** per-slot enumeration in Consequences section — T22 D2100.9 metadata contract validation (Track B); T13 dual-cascade F3 R3.5 resolution (Track A); T18 axis-scoring ranker; T19 conflict-resolution rule engine; T21 lifecycle state machine; T26a retrieval-surface consistency Detect-and-Flag; T27 SIGN preamble corpus-hygiene gate; T29 Corpus Health Score dashboard. Order per 2199 xx99 §1 line 82.
- **No runtime enforcement claims.** Docs-only classification ADR.
- **Stage 5 verification interface (per F15 lock + F18):** `search_docs` + `kb_tool.semantic_search` + `repo_tool.search` (frontmatter field patterns) + `repo_tool.read_file`. No `manage.py` execution. No live-index query. No `deliverable_tool.list`.
- **File:** `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md`.
- **Sub-option 1(iv):** ADR corpus schema extension (`provisional: bool` + `provisional_reason: str`) does NOT require companion PR to `ADR-0001-establish-adr-corpus.md` (additive frontmatter fields permitted per ADR-0001 §3.2 pattern). If Rigby SIGN flags this at ADR body SIGN, escalate to Chris.

### Guardrails (still in force)

- **LOCAL-only operating model** per PR #2972.
- **Chris directives carried forward:**
  - "No runtime code."
  - "Do not admit companion rows."
  - "Do not change feature flags."
  - "Do not draft ADR-0004 until the design-prep PR is merged." (added 2026-07-07 at design-prep ratification)

### Next executable action

**Await design-prep PR merge.** Once merged:
1. Fresh branch off `main` for ADR-0004 body PR.
2. Draft `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md` per ratified Option 1 shape.
3. Route ADR-0004 to Rigby SIGN Cycle 1 on `pa-1b76ee75adbf4031` per IOS §7.2 single-batch × 4-Q cadence.
4. Apply any folds pre-Chris-ratification.
5. Present to Chris for "Agree All" ratification of ADR-0004 body.
6. On Chris ratification: run cascade; commit + push + open PR with §12.5.d evidence block.
7. On PR merge: BACKLOG.md `IB-2199-T0-01` flips `IN_ARC → SHIPPED` with `pr_refs` + `adr_ref: ADR-0004` per IOS §2.2 v1.4 Discipline B inline syntax.

### Deferred (not blocking, not urgent)

- **IOS §14.2 codification candidates surfaced by Arc I-0200:**
  - CC-1 arc-scoped workflow overrides — first live trigger via design-prep SIGN before ADR body (Chris §14.2 refinement-authority); awaiting second arc.
  - CC-2 PROVISIONAL ADR pattern selection (Option 1a two-field pattern ratified as design-prep-side template); awaiting second PROVISIONAL ADR.
  - CC-3 docs-only ADR "code state" definition per design-prep §1.2 — single trigger.
  - Rigby's second-consecutive-stronger-than-Claude first-arc argument at TWO-trigger threshold for IOS §11.3 amendment.
  - Contingency-gated arc seed pattern first live application via P1 SEVERABLE outcome.
  - Severability-gate as Stage 1 first-class exit condition — Rigby Q3 non-contradiction cross-check pattern.
  - PROVISIONAL ADR frontmatter taxonomy (Option a vs b).
- **`project_deployment_state_between_merged_and_active.md`** — 2/4 triggers from Arc I-0100.

### Read as background

- **Design-prep:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md` (357 lines; F17+F18 applied; Chris Agree-All 2026-07-07).
- **P1 severability determination:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md` (SEVERABLE; F15+F16+Q2/Q3).
- **Scoping doc:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` (Stage 2 in-flight; §10 checklist updated).
- **Ratification record:** `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
- **RAG xx99 canonical:** `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 seam statement + §5.1 verbatim + §8 T-slot queue.
- **Arc I-0100 ADR-B design-prep reference:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_design_prep_adr_b_pa_write_shape.md`.
- **ADR corpus schema:** `docs/adr/ADR-0001-establish-adr-corpus.md`.
- **IOS canonical:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 §4.3 + §4.3.a + §4.3.0 stage-state enum + §7.2 SIGN routing + §14.2 Chris refinement-authority + §15.14 pin lifecycle.
- **BACKLOG at HEAD:** `docs/research/implementation/BACKLOG.md` — arc-open history rows for I-0100 close + I-0200 open + P1 close + Stage 2 open/design-prep ratification.

### Session ready check (before next action)

1. **First tool call:** `context-kit orient`.
2. Verify design-prep PR merged: `gh pr view <design-prep-PR-num> --json state` — expect `MERGED`.
3. Verify wrapper pin: `grep 'conversation pa-' tools/pa_local.sh | tail -1` — expect `pa-1b76ee75adbf4031`.
4. Verify service_context via `platform_config_tool overview` on `pa-1b76ee75adbf4031` — expect `service_context=local`.
5. Verify runtime flags: `grep -E 'PA_AGENT_EXECUTION_WRITE_ENABLED|RIGBY_DELEGATION_ENABLED' core/settings.py` — both env-driven `false`.
6. Read the design-prep §7 recommendation + §7.1 sub-options + P1 determination §6 required ADR shape.
7. Follow "Next executable action" sequence above.

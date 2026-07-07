# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0200 ADR-0004 ACCEPTED PROVISIONAL; STAGE 3 SKIPPED; STAGE 6 CLOSE DOC PENDING CHRIS DIRECTIVE

**Refreshed 2026-07-07 (ADR-0004 authored + Rigby SIGN-with-edits MED-HIGH + Chris "Agree All" + ADR-0004 PR merged; `IB-2199-T0-01` flipped `IN_ARC → SHIPPED`; Stage 3 SKIPPED per docs-only scope; Stage 6 close doc drafting authorized on separate Chris directive).**

### What just happened (session-scope summary)

1. **Arc I-0100 closed** 2026-07-07 under LOCAL operating model (PR #2976 + #2977 + #2978 + #2979 all merged).
2. **Second-arc selection SIGN → Chris Agree-All** 2026-07-07. Selection SIGN pin `pa-6a4e2eff5594486b` retired. Ratification record at `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
3. **Arc I-0200 Stage 1 opened + merged** 2026-07-07 as `87dbd95a` via PR #2980. Rigby SIGN-with-edits MED-HIGH; folds F9-F14. Arc-scoped pin `pa-1b76ee75adbf4031`.
4. **P1 severability CLOSED SEVERABLE + merged** 2026-07-07 as `c39db4394` via PR #2982 (superseded auto-closed #2981). Rigby SIGN-with-edits MED-HIGH; folds F15-F16. `IB-2199-T0-01` flipped `TRIAGED → IN_ARC (I-0200)`.
5. **Stage 2 opened + Design-Prep authored + Rigby SIGN + Chris Agree-All + merged** 2026-07-07 as `c87878dd` via PR #2983. Rigby SIGN-with-edits MED-HIGH; folds F17-F18. Chris-directed arc-scoped IOS §14.2 workflow refinement recorded in design-prep §9.2.
6. **ADR-0004 body authored + Rigby SIGN + Chris Agree-All + merged** 2026-07-07 as `<TBD-populated-post-merge>` via PR #<TBD>. Rigby SIGN-with-edits MED-HIGH (Q1 SIGN-with-edits 0.84 + Q2 SIGN-clean 0.86 + Q3 SIGN-with-edits 0.77 + Q4 SIGN-with-edits 0.74); folds F19 (§3.1 strict-verbatim seam) + F20 (§4.4 forward-compat rule) + F21 (§6 rollback step 4 de-speculate cleanup command). Chris "Agree All" ratified Option 1 exactly as ratified in design-prep + all three folds + successor-trigger policy. `IB-2199-T0-01` flipped `IN_ARC → SHIPPED` with `adr_ref: ADR-0004`.

### Phase

**`implementation`.** IOS `active v1.5` on `main`. **Active arc: I-0200 (Stage 2 ADR-0004 accepted PROVISIONAL; Stage 3 SKIPPED per docs-only scope; Stage 6 close doc drafting deferred to explicit Chris directive).**

### Active arc

**Arc I-0200 — RAG Corpus Substrate Maturity Gradient (default path locked; ADR-0004 accepted PROVISIONAL).**

### CURRENT_STAGE / CURRENT_GATE / CURRENT_STATUS (§10 cold-resume tokens)

```
CURRENT_STAGE=2
CURRENT_GATE=ADR-0004_RATIFIED_and_MERGED_IB-2199-T0-01_flipped_SHIPPED_pending_Stage_3_pre_flight_SKIPPED_and_Stage_6_close
CURRENT_STATUS=ADR-0004-Chris-Agree-All-2026-07-07-Rigby-SIGN-with-edits-MED-HIGH-F19-F21-applied-IB-2199-T0-01-SHIPPED-Stage-3-SKIPPED-per-docs-only-scope-Stage-6-close-doc-next
```

### Guardrails (still in force)

- **LOCAL-only operating model** per PR #2972.
- **Chris directives carried forward:**
  - "No runtime code."
  - "Do not admit companion rows."
  - "Do not change feature flags."

### Next executable action

**Await Chris explicit directive to open Stage 6 close for Arc I-0200.** Per IOS §4.3 Stage 6 canonical close doc discipline (mirroring Playbook §11.3 xx99 template + Arc I-0100 `I-010099_observability_spine_implementation_close.md` PR #2976 pattern):

1. Fresh branch off `main` for Stage 6 close bundle.
2. Draft `docs/research/implementation/rag_corpus_substrate_maturity/I-020099_rag_corpus_substrate_maturity_implementation_close.md`.
3. Append `cross_domain_integration_audit.md §14.N` refresh entry (D10 hard gate per IOS §4.3 Stage 6).
4. Flip scoping doc `stage: 2 → 6`, `stage_state: active → awaiting-close` per IOS §4.3.0 v1.5 discipline.
5. Retire arc-scoped SIGN pin `pa-1b76ee75adbf4031` per §7.2 isolation-pin discipline (mirror Arc I-0100 PR #2977 + #2978 pattern).
6. Rotate `tools/pa_local.sh --conversation` back to paused-research T4 pin `pa-44a6eb70d8814e34` per §15.14 restoration rule.
7. Run 5-step cascade + commit + push + open PR + admin-merge.
8. Fast-forward main + verify.

**Stage 3 explicitly SKIPPED** per docs-only ADR scope + F15 lock (Stage 5 verification bounded to documentation cross-check; no runtime pre-flight; no `manage.py` execution; no live-index query). Rationale documented in scoping doc §10 + will be documented in Stage 6 close doc §7.

**Stage 4 (Build) is MERGED INTO STAGE 2** per scoping doc §5 P2 row (ADR PR IS the shipping vehicle for docs-only ADR). No separate Build stage.

**Stage 5 (Verify) — LIGHT VERIFY at Stage 6 close** per F15 lock: Rigby exercises the ratified maturity classification via read-only documentation cross-check (search_docs / kb_tool.semantic_search / repo_tool.search / repo_tool.read_file per F18); Claude independently verifies via git-log + file Read + BACKLOG.md status column checks. No runtime probes.

### Deferred (not blocking, not urgent)

- **IOS §14.2 codification candidates surfaced by Arc I-0200:**
  - **CC-1** Arc-scoped workflow overrides — SECOND application via ADR body SIGN following design-prep SIGN; SIGN-both-independently pattern (rather than §4.3.a default of design-prep pressure-tested BY ADR SIGN). Awaiting second arc for §4.3.a amendment proposal.
  - **CC-2** PROVISIONAL ADR pattern — FIRST live ratification of two-field pattern (`status: accepted` + `provisional: true`) in ADR corpus. Awaiting second PROVISIONAL ADR.
  - **CC-3** Docs-only ADR "code state" definition per design-prep §1.2 — single trigger.
  - **CC-4 (NEW — from F20)** Additive-frontmatter forward-compat rule: ADR corpus consumers MUST ignore unknown frontmatter keys. Could codify as ADR-0001 §3.3 companion amendment if Chris directs. Single trigger.
  - **CC-5 (NEW — from F19)** §3.1 research→ADR strict-verbatim discipline: ADR body must present source-ratified content in strict-verbatim form without ADR-side re-quoting or paraphrase drift. Single trigger.
  - Rigby's second-consecutive-stronger-than-Claude first-arc argument at TWO-trigger threshold for IOS §11.3 amendment.
  - Contingency-gated arc seed pattern first live application via P1 SEVERABLE outcome.
  - Severability-gate as Stage 1 first-class exit condition — Rigby Q3 non-contradiction cross-check pattern.
- **`project_deployment_state_between_merged_and_active.md`** — 2/4 triggers from Arc I-0100.

### Read as background

- **ADR-0004:** `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md` (accepted PROVISIONAL; Chris Agree-All 2026-07-07; F19-F21 applied).
- **Design-prep:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md`.
- **P1 severability determination:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md`.
- **Scoping doc:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md`.
- **Ratification record:** `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
- **Arc I-0100 close reference (Stage 6 canonical pattern):** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_observability_spine_implementation_close.md`.
- **RAG xx99 canonical:** `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md`.
- **IOS canonical:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5.

### Session ready check (before next action)

1. **First tool call:** `context-kit orient`.
2. Verify ADR-0004 merged: `git log --oneline main | grep -i 'ADR-0004' | head -3`.
3. Verify wrapper pin: `grep 'conversation pa-' tools/pa_local.sh | tail -1` — expect `pa-1b76ee75adbf4031` (rotates back to `pa-44a6eb70d8814e34` at Stage 6 close).
4. Verify service_context via `platform_config_tool overview` on `pa-1b76ee75adbf4031` — expect `service_context=local`.
5. Verify runtime flags: `grep -E 'PA_AGENT_EXECUTION_WRITE_ENABLED|RIGBY_DELEGATION_ENABLED' core/settings.py` — both env-driven `false`.
6. Read Arc I-0100 close doc as Stage 6 template reference.
7. Await Chris directive to open Stage 6 or take any other next action.

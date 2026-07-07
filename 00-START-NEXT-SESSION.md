# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0200 P1 CLOSED SEVERABLE; STAGE 2 OPENS ON SEPARATE CHRIS DIRECTIVE

**Refreshed 2026-07-07 (P1 severability determination CLOSED SEVERABLE per Chris "Agree All" 2026-07-07; both Stage 1 arc-open PR + P1 determination PR in flight).**

### What just happened (session-scope summary)

1. **Arc I-0100 closed** 2026-07-07 under LOCAL operating model (PR #2976 + #2977 + #2978 + #2979 all landed).
2. **Second-arc selection SIGN → Chris Agree-All** 2026-07-07 via selection SIGN pin `pa-6a4e2eff5594486b` (retired same day). Rigby SIGN-with-edits MED with 8 folds F1-F8. Ratification record at `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
3. **Arc I-0200 Stage 1 opened** 2026-07-07. Arc-scoped SIGN pin `pa-1b76ee75adbf4031` minted. Scoping doc drafted at `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md`. Rigby SIGN Cycle 1 SIGN-with-edits MED-HIGH with 6 folds F9-F14 applied pre-Chris-ratification. Chris ratified via "Agree All" 2026-07-07. Stage 1 arc-open bundle PR **#2980** open at https://github.com/clwest/donkey-betz-platform/pull/2980.
4. **P1 severability determination CLOSED SEVERABLE** 2026-07-07. All three Q-Sev YES with verbatim F12 evidence citations (2199 xx99 §1 lines 74/84/76). F11 UNKNOWN operational check clean under PROVISIONAL ADR shape. Rigby SIGN Cycle 1 SIGN-with-edits MED-HIGH with 2 folds F15-F16 applied pre-Chris-ratification. Chris ratified via "Agree All" 2026-07-07. `IB-2199-T0-01` flipped `TRIAGED → IN_ARC (I-0200)`. Fallback path not triggered. Determination doc at `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md`. P1 close PR (stacked on #2980) opening as next action.

### Phase

**`implementation`.** IOS `active v1.5` on `main`. **Active arc: I-0200 (Stage 1 exit-gate cleared; P1 CLOSED SEVERABLE; Stage 2 opens on separate Chris directive).**

### Active arc

**Arc I-0200 — RAG Corpus Substrate Maturity Gradient (DEFAULT PATH LOCKED).** SEVERABLE determination Chris-ratified 2026-07-07. `IB-2199-T0-01` is now the ratified `IN_ARC (I-0200)` seed. `IB-1999-T0-01` remains `TRIAGED` (fallback not triggered).

### CURRENT_STAGE / CURRENT_GATE / CURRENT_STATUS (§10 cold-resume tokens)

```
CURRENT_STAGE=1
CURRENT_GATE=P1_SEVERABILITY_DETERMINED_SEVERABLE_pending_Chris_directive_to_open_Stage_2
CURRENT_STATUS=P1-SIGN-with-edits-MED-HIGH-F15-F16-Chris-Agree-All-2026-07-07-IB-2199-T0-01-flipped-IN_ARC-I-0200
```

### Stage 2 authoring constraints (ratified 2026-07-07 — do NOT relax without Chris directive)

Any Stage 2 ADR authoring session MUST honor:

1. **ADR marked PROVISIONAL.** Frontmatter Option (a) `status: accepted` + `provisional: true` + `provisional_reason: "BOR-01 undischarged"` OR Option (b) `status: provisional` with explicit ADR §1 Context definition.
2. **Explicit "BOR-01 discharge is a Stage-2-post-ratification requirement" clause** in Consequences section.
3. **T-slot execution PRs named as post-arc requirements** — T18 axis-scoring, T19 conflict-resolution, T21 lifecycle state-machine, T22 metadata contract validation, T13 dual-cascade resolution, T26a retrieval-surface consistency Detect-and-Flag, T27 SIGN preamble corpus-hygiene gate, T29 Corpus Health Score dashboard.
4. **No runtime enforcement claims** — ADR ratifies design-layer classification only.
5. **Stage 5 verification scope = documentation cross-check only** (per F15 lock). No `manage.py` execution. No live-index query. No runtime disagreement probing. Runtime probes = BOR-01 discharge and are OUT-OF-SCOPE for the ADR.

### Guardrails (still in force)

- **LOCAL-only operating model** per PR #2972.
- **Chris directives** carried forward from RATIFICATION_2026-07-07 §2 Axis 7 + P1 ratification:
  - "No runtime code."
  - "Do not open Stage 2 until the P1 PR is merged."
  - "Do not author the ADR yet."
  - "Do not admit companion rows."

### Next executable action

**Await Chris directive to open Stage 2** after both PR #2980 (Stage 1 arc-open) + P1 close PR are merged. Stage 2 does NOT auto-open on P1 PR merge per Chris directive.

Once Chris directs Stage 2 open:
1. Verify IOS §4.3 Stage 2 Entry gate satisfied (ADR corpus precondition already met via Arc I-0100 PR #2948; scoping doc `stage: 1 → 2` + `stage_state: exit-gate-cleared → active` flip).
2. Author `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_design_prep_rag_corpus_substrate_maturity.md` per IOS v1.5 §4.3.a mandatory design-prep first-class artifact rule.
3. Author `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md` (or next available ADR number) per §4.3 Stage 2 discipline honoring the 5 authoring constraints above.
4. Route ADR to Rigby SIGN Cycle 1 on arc-scoped pin `pa-1b76ee75adbf4031`.
5. Present to Chris for "Agree All" ratification of ADR-N.

### Deferred (not blocking, not urgent)

- **IOS §14.2 codification candidates surfaced by Arc I-0200:**
  - (a) Contingency-gated arc seed pattern — first live application via P1 SEVERABLE outcome; awaiting second independent arc for §4.3 amendment proposal.
  - (b) Severability-gate as Stage 1 first-class exit condition — Rigby Q3 negative-check discipline hardens to §5.1 template pattern; single trigger.
  - (c) Rigby's second-consecutive-stronger-than-Claude first-arc argument at TWO-trigger threshold for IOS §11.3 amendment — deferred to dedicated IOS-patch session.
  - (d) PROVISIONAL ADR frontmatter taxonomy (Rigby SIGN Q2 fold on P1) — Option (a) two-field vs Option (b) single-field pattern; single trigger.
- **`project_deployment_state_between_merged_and_active.md`** — 2/4 triggers from Arc I-0100.

### Read as background

- **Arc I-0200 scoping doc:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` (updated post-F15/F16 folds + P1 close status).
- **Arc I-0200 P1 severability determination:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_severability_determination.md` (256 lines; SEVERABLE; F15+F16+Q2/Q3 refinements applied).
- **Arc I-0200 ratification record:** `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md` (166 lines; second-arc selection ratification).
- **RAG xx99 canonical:** `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 seam statement + §5.1 verbatim + §8 T-slot queue.
- **Arc I-0100 close reference:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_observability_spine_implementation_close.md` (PR #2976).
- **First-queue ratification precedent:** `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md`.
- **IOS canonical:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 §3.1 + §3.1.b + §3.2 + §3.3 + §4.3 + §5.1 + §7.2 + §11.2 + §11.3 + §11.4 + §15.14.
- **BACKLOG at HEAD:** `docs/research/implementation/BACKLOG.md` — arc-open history rows for I-0100 close + I-0200 open + I-0200 P1 close; IB-2199-T0-01 flipped `IN_ARC (I-0200)`.

### Session ready check (before next action)

1. **First tool call:** `context-kit orient`.
2. Verify Arc I-0200 in-flight: `grep -A2 '^## In-progress' docs/research/OPEN_ARCS.md | head -6` — should show I-0200 row with P1 SEVERABLE annotation.
3. Verify wrapper pin: `grep 'conversation pa-' tools/pa_local.sh | tail -1` — expect `pa-1b76ee75adbf4031`.
4. Verify service_context via `platform_config_tool overview` on `pa-1b76ee75adbf4031` — expect `service_context=local` + `database_name=unified_donkey_betz` + `default_llm_provider=openai`.
5. Verify runtime flags (unchanged from Arc I-0100 close): `grep -E 'PA_AGENT_EXECUTION_WRITE_ENABLED|RIGBY_DELEGATION_ENABLED' core/settings.py` — both env-driven `false` defaults.
6. Read this doc + Arc I-0200 severability determination §6 required ADR shape (5 authoring constraints).
7. Check merge status of PR #2980 (Stage 1 arc-open) + P1 close PR. Both must merge before Stage 2 opens.
8. If Chris directs Stage 2 open, follow "Next executable action" sequence above.

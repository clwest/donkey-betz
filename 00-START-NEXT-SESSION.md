# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0200 STAGE 1 IN-PROGRESS (SEVERABILITY DETERMINATION PENDING)

**Refreshed 2026-07-07 (Stage 1 arc-open bundle drafted; Rigby SIGN Cycle 1 on scoping doc pending; Chris Agree-All ratified selection).**

### What just happened (session-scope summary)

1. **Arc I-0100 closed** 2026-07-07 under LOCAL operating model (all 3 T1 intakes terminal; PR #2976 close doc merged; #2977 + #2978 + #2979 close-out cascade all landed).
2. **Second-arc selection SIGN → Chris Agree-All 2026-07-07.** Claude produced IOS-methodology-only ranking; routed to Rigby via selection SIGN pin `pa-6a4e2eff5594486b`. Rigby returned SIGN-with-edits MED confidence with 8 folds F1-F8 and a 7-axis contingency-gated ratification card. Chris ratified via "Agree All" — default seed `IB-2199-T0-01` (RAG corpus substrate maturity gradient) IF Stage 1 confirms severability from `IB-2199-BOR-01`; ELSE auto-switch to `IB-1999-T0-01` (Authority per-plane posture). Selection SIGN pin retired same day. Ratification record committed at `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md`.
3. **Arc I-0200 Stage 1 opened** 2026-07-07. Arc-scoped SIGN pin `pa-1b76ee75adbf4031` (label `ios-arc-open-I-0200`) minted; `tools/pa_local.sh --conversation` rotated; paused-research T4 pin (`pa-44a6eb70d8814e34`) preserved as `# PRESERVED AS COMMENT` block per §15.14 phase-transition supersession. Stage 1 scoping doc drafted at `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md`.

### Phase

**`implementation`.** IOS `active v1.5` on `main`. **Active arc: I-0200 (Stage 1, `stage_state: active`).**

### Active arc

**Arc I-0200 — RAG Corpus Substrate Maturity Gradient (default) / Authority per-plane Posture (fallback).** Contingency-gated seed per Rigby-SIGN-with-edits-then-Chris-Agree-All 2026-07-07. Neither seed row flipped `IN_ARC` at arc-open — flip pending Stage 1 severability determination outcome.

### Contingency structure (Rigby-ratified, Chris Agree-All 2026-07-07)

| Path | Seed | Slug | Trigger |
|------|------|------|---------|
| **Default** | `IB-2199-T0-01` (RAG corpus substrate maturity gradient; 2199 §1 canonical seam) | `rag_corpus_substrate_maturity` | Stage 1 severability determination concludes `IB-2199-T0-01` IS severable from `IB-2199-BOR-01` (RAG `search_docs` + `kb_tool` retrieval end-to-end verification; audit §2.5) |
| **Fallback (auto-switch)** | `IB-1999-T0-01` (Authority per-plane posture; 1999 §17.1) | `authority_per_plane_posture` | Stage 1 severability determination concludes `IB-2199-T0-01` is NOT severable → reclassifies to `BLOCKED_ON_RESEARCH`; `IB-1999-T0-01` auto-flips `IN_ARC`; arc folder renames |

**Auto-switch mechanic per RATIFICATION_2026-07-07 §2 Axis 5:** No re-ratification required. Chris "Agree All" ratifies the outcome-conditional mechanic itself. Only a Chris-explicit override of the auto-switch requires a separate directive at Stage 1 severability determination time.

### Fold list ratified via "Agree All" (F1–F8)

- **F1** Treat `IB-2199-T0-01` as provisional pending severability; otherwise demote to `BLOCKED_ON_RESEARCH`.
- **F2** Re-score without contested boosts; don't let bumps decide arc identity.
- **F3** Stage 1 must classify `IB-2199-BOR-01` as in-arc enabling vs external blocker.
- **F4** If BOR is required, immediately switch seed to `IB-1999-T0-01` (no limbo).
- **F5** Withdraw §3.3 +2 cross-domain bump unless positive cross-domain dependency evidence is cited.
- **F6** Deterministic fallback — if 2199 blocked, 1999 becomes seed by mechanical rank.
- **F7** If 2199 severable but bump removed, re-rank; if 1999 outranks, seed = 1999 unless Chris overrides.
- **F8** For `IB-1999-T1-01`, Stage 1 must classify blocker type (posture-clarity vs unknown-fact) to decide admission.

### Guardrails (still in force)

- **LOCAL-only operating model** carried forward from PR #2972. No Railway/prod verification unless Chris explicitly provides a live prod access path.
- **No runtime code** in Arc I-0200 per Chris directive 2026-07-07 at ratification. Arc scope is documentation + ADR only.
- **No Stage 2 ADR authoring opens** until Stage 1 severability determination closes with Chris ratification.
- **No companion-row admission until Stage 1 proves it** per Chris directive + Axis 4.

### Next executable action

**Route Stage 1 scoping doc to Rigby SIGN Cycle 1** on arc-scoped pin `pa-1b76ee75adbf4031` per IOS §7.2 single-batch × 4-Q cadence. SIGN Q1-Q4 pressure-test:

- Q1 Contingency structure encoding (is the severability gate mechanic sound?)
- Q2 §9.3 severability determination method (three-question test — sufficient?)
- Q3 Companion-row evaluation rules (Axis 4 encoding — captures the binary admit/hold-out shape?)
- Q4 §10 Stage checklist snapshot (is the stage-transition mechanic greppable + reversible?)

After Rigby SIGN response: apply folds in-branch, present to Chris for Stage 1 exit-gate ratification via "Agree All" or explicit fold-by-fold response. Merge arc-open PR with §12.5.d cascade evidence block. Then next session opens Stage 1 severability determination (P1 PR).

### Deferred (not blocking, not urgent)

- **IOS §14.2 codification candidates surfaced by this arc** (per RATIFICATION_2026-07-07 §6):
  - Contingency-gated arc seed pattern (single trigger; awaiting second before IOS v1.6 §4.3 proposal).
  - Severability-gate as Stage 1 first-class exit condition (single trigger).
  - Rigby's second-consecutive-stronger-than-Claude first-arc argument reaches TWO-trigger threshold for IOS §11.3 amendment — deferred to a dedicated IOS-patch session (do NOT bundle into Arc I-0200 scope).
  - Bump-withdrawal discipline (F5) as §3.3 hardening (single trigger).
- **`project_deployment_state_between_merged_and_active.md`** — 2/4 triggers from Arc I-0100. Do NOT propose IOS v1.6 until pattern surfaces in 2+ more independent arcs.

### Read as background

- **Arc I-0200 scoping doc:** `docs/research/implementation/rag_corpus_substrate_maturity/I-0200_scoping.md` (441 lines).
- **Arc I-0200 ratification record:** `docs/research/implementation/RATIFICATION_2026-07-07_second_arc_I-0200.md` (166 lines).
- **RAG xx99 canonical:** `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` §1 seam statement + §5.1 verbatim + §8 T-slot queue.
- **Authority xx99 canonical:** `docs/research/domains/authority_enforcement/1999_authority_enforcement_canonical_summary.md` §17.1 per-plane posture map.
- **Arc I-0100 close reference:** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_observability_spine_implementation_close.md` (PR #2976).
- **First-queue ratification precedent:** `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md`.
- **IOS canonical:** `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` v1.5 §3.1 + §3.1.b + §3.2 + §3.3 + §4.3 + §5.1 + §7.2 + §11.2 + §11.3 + §11.4 + §15.14.
- **BACKLOG at HEAD:** `docs/research/implementation/BACKLOG.md` — arc-open history rows for I-0100 close + I-0200 open; contingent-status flags on IB-2199-T0-01 + IB-1999-T0-01.
- **Paused research pin context:** `tools/pa_local.sh:20-34` (comment header for the arc-scoped pin) + `tools/pa_local.sh:463-472` (paused-research T4 preservation block).

### Session ready check (before next action)

1. **First tool call:** `context-kit orient`.
2. Verify Arc I-0200 in-flight: `grep -A2 '^## In-progress' docs/research/OPEN_ARCS.md | head -6` — should show I-0200 row.
3. Verify wrapper pin: `grep 'conversation pa-' tools/pa_local.sh | tail -1` — expect `pa-1b76ee75adbf4031`.
4. Verify service_context via `platform_config_tool overview` on `pa-1b76ee75adbf4031` — expect `service_context=local` + `database_name=unified_donkey_betz` + `default_llm_provider=openai`.
5. Verify runtime flags (unchanged from Arc I-0100 close): `grep -E 'PA_AGENT_EXECUTION_WRITE_ENABLED|RIGBY_DELEGATION_ENABLED' core/settings.py` — both env-driven `false` defaults.
6. Read this doc + Arc I-0200 scoping doc §9.3 severability determination method.
7. If Rigby SIGN Cycle 1 not yet routed, route it. If routed and returned, apply folds + present to Chris.

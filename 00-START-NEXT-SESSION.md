# Next Session — Start Here

---

## READ THIS FIRST — ARC I-0200 FULLY CLOSED (LOCAL); NO ACTIVE ARC; AWAITING CHRIS DIRECTIVE

**Refreshed 2026-07-07 (post Stage 6 close: canonical close doc drafted + cross_domain_integration_audit §14.18 appended + arc-scoped SIGN pin retired + wrapper rotated back to paused-research T4 pin + close-doc PR in flight).**

### What just happened (arc-scope summary)

Arc I-0200 (`rag_corpus_substrate_maturity`) — the SECOND production implementation arc under IOS active v1.5 — is **FULLY CLOSED under the LOCAL operating model**. The sole T0 intake is in a terminal `SHIPPED` disposition; ADR-0004 landed accepted PROVISIONAL; all Stage 6 close ritual actions are discharged in the close PR bundle.

| Intake | ADR | Terminal Disposition | Merge SHA | PR |
|--------|-----|----------------------|-----------|-----|
| **`IB-2199-T0-01`** (RAG corpus substrate maturity gradient) | ADR-0004 (accepted PROVISIONAL) | **SHIPPED (I-0200)** | `84b45a11` | #2984 |

**Canonical close doc:** `docs/research/implementation/rag_corpus_substrate_maturity/I-020099_rag_corpus_substrate_maturity_implementation_close.md` (in this Stage 6 close PR).

**Operating model:** LOCAL-only, per Arc I-0100 PR #2972 guardrail. No prod endpoint responded during the arc; no prod DB was touched; no prod flag was flipped. Arc I-0200 was docs-only from Stage 2 through Stage 6.

**Flag defaults (unchanged throughout the arc):**
- `RIGBY_DELEGATION_ENABLED` — env-driven `false` at `core/settings.py:138-140`.
- `PA_AGENT_EXECUTION_WRITE_ENABLED` — env-driven `false` at `core/settings.py:173-174`.

### Arc I-0200 close-out actions — DISCHARGED

All Stage 6 ritual steps per IOS §4.3 Stage 6 items 1-7 are complete in this close PR:

1. **Canonical close doc drafted** — 9 sections per Playbook §11.3 xx99 mirror + §10 Stage 6 housekeeping section. Records 4 drift items per Chris directive (scoping stage_state fix + design-prep §7.1(iv) mis-citation record + CC-1 two-application-within-arc ambiguity + CC-4 ADR-0001 forward-compat candidate) + notes Arc I-0100 §14 audit-refresh gap for future backfill.
2. **`cross_domain_integration_audit.md §14.18` appended** — first implementation-arc §14 entry (all prior §14.2-§14.17 entries are research-arc closes).
3. **5-step docs cascade** run locally before close PR + `docs/INDEX.md` + `docs/_provenance.json` diffs co-committed + §12.5.d evidence block in PR body.
4. **`OPEN_ARCS.md` update** — I-0200 row moved from `In-progress` to `Closed`; wrapper-pin note updated.
5. **Backlog cleanup** — new arc-open history row for Stage 6 close; `IB-2199-T0-01` unchanged (already `SHIPPED` from PR #2984).
6. **Implementation debt** — no new IDBT entry authored; 5 drift items recorded in close doc §6 for audit trail.
7. **Rigby SIGN on close doc** — mandatory per IOS §4.3 Stage 6 item 7 + §7.2 Table (Stage 6 requires full SIGN); routed on arc-scoped pin `pa-1b76ee75adbf4031`; folds applied pre-Chris-ratification; pin retires post-Chris-ratification per §15.14.

**Arc-scoped SIGN pin retired.** `pa-1b76ee75adbf4031` (label `ios-arc-open-I-0200`) retired via `session_tool.retire force=true` at close-PR merge time (SECOND fresh arc-scoped implementation-pin retirement after `pa-c5b235f7b15f45be` from Arc I-0100 close PR #2977).

**Wrapper rotation confirmed.** `tools/pa_local.sh --conversation` flipped from `pa-1b76ee75adbf4031` back to paused-research T4 pin `pa-44a6eb70d8814e34` per §15.14 restoration rule (mirrors Arc I-0100 PR #2978 pattern).

### Phase

**`implementation` (transitioning to no-active-arc).** IOS `active v1.5` on `main`. No active arc post-Stage-6-close-PR merge.

### Active arc

**None.** Arc I-0200 closed via this Stage 6 close PR merge; no successor opened.

### Guardrail (still in force — carried forward from Arc I-0100 PR #2972)

**Do not attempt Railway/prod verification unless Chris explicitly provides a live prod access path.** Historical guardrail unchanged since Arc I-0100 close. If any future arc needs prod validation, that path opens with Chris naming the environment (URL + auth token, or `railway link` + `railway run …`, or a read-only prod `DATABASE_URL`).

### Next executable action

**Chris sequencing directive determines the next arc.** No admin cleanup remains for Arc I-0200. The next session's work opens one of these paths:

- **(c) Open a new implementation arc.** Candidates already-triaged in `docs/research/implementation/BACKLOG.md`:
  - `IB-1399-T1-*` — memory arc T1 rows
  - `IB-1499-T1-*` — revenue arc T1 rows
  - `IB-1599-T1-*` — sports arc T1 rows
  - `IB-1699-T1-*` — content arc T1 rows
  - Any T0/gate row from the register requiring individual Chris gate at Stage 2 entry
  - `IB-1999-T0-01` (Authority per-plane posture) — Arc I-0200 fallback candidate now available as standalone T0 arc if Chris directs
  - Any of the 8 T-slot execution PRs named in ADR-0004 §4.1 (T22 / T13 / T18 / T19 / T21 / T26a / T27 / T29) can be opened as a future implementation arc
  - Any of the 5 codification candidates (CC-1 through CC-5) can open a dedicated IOS-patch arc if Chris directs
- **(d) Return to research phase.** T4 Group 1700 Observability is the currently-paused research thread (`tools/pa_local.sh` now routes to `pa-44a6eb70d8814e34`). Load-bearing inputs are documented in the wrapper's comment block.
- **(e) Optional companion PR to ADR-0001 §3.3.** If Chris directs, open a companion ADR-0001 amendment to codify the F20 forward-compat rule ("consumers MUST ignore unknown frontmatter keys") platform-wide. Currently ADR-0004-scoped only.
- **(f) Arc I-0100 §14 audit-refresh backfill.** Optional cleanup to add the missing §14 entry for Arc I-0100 close (gap noted in Arc I-0200 close doc §6.5).

**My read:** No default — this is a Chris sequencing decision. Do not open (c) or advance (d) without an explicit directive. If Chris is silent at session open, ask before touching either lane.

### Deferred (not blocking, not urgent)

- **IOS §14.2 codification candidates from Arc I-0200 (5 total; all single-trigger unless noted):**
  - CC-1 arc-scoped workflow overrides — two-application-within-arc; ambiguity per close doc §6.3 (whether that counts as two triggers or one for §14.2 threshold).
  - CC-2 PROVISIONAL ADR two-field pattern — first live ratification.
  - CC-3 docs-only ADR "code state" definition.
  - CC-4 additive-frontmatter forward-compat rule — candidate ADR-0001 §3.3 companion amendment.
  - CC-5 research→ADR strict-verbatim discipline.
- **From Arc I-0100:** `project_deployment_state_between_merged_and_active.md` — 2/4 triggers. Do NOT propose IOS v1.6 until pattern surfaces in 2+ more independent arcs.

### Read as background

- **Arc I-0200 canonical close:** `docs/research/implementation/rag_corpus_substrate_maturity/I-020099_rag_corpus_substrate_maturity_implementation_close.md`.
- **Arc I-0200 ADR:** `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md`.
- **Arc I-0200 supporting artifacts:** scoping / severability determination / design-prep / RATIFICATION_2026-07-07 all in `docs/research/implementation/rag_corpus_substrate_maturity/` or `docs/research/implementation/`.
- **Arc I-0100 canonical close (Stage 6 template reference):** `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_observability_spine_implementation_close.md` (PR #2976).
- **First-queue ratification precedent:** `docs/research/implementation/RATIFICATION_2026-07-06_first_queue.md`.
- **BACKLOG:** `docs/research/implementation/BACKLOG.md` — T0/T1/T2/T3/DEFER rows for next-arc selection under (c). Post-I-0200 close, `IB-2199-T0-01` is `SHIPPED`; all Arc I-0100 rows terminal.
- **T4 paused research pin context:** `tools/pa_local.sh` header comment block.
- **Cross-domain audit §14.18 (Arc I-0200 delta):** `docs/research/platform/cross_domain_integration_audit.md`.

### Session ready check (before next action)

1. **First tool call:** `context-kit orient`.
2. Verify no in-flight arc: `grep -A2 '^## In-progress' docs/research/OPEN_ARCS.md | head -20` — table should be empty of live rows.
3. Verify wrapper pin restored: `grep 'conversation pa-' tools/pa_local.sh | tail -1` — expect `pa-44a6eb70d8814e34`.
4. Verify runtime flags OFF: `grep -E 'PA_AGENT_EXECUTION_WRITE_ENABLED|RIGBY_DELEGATION_ENABLED' core/settings.py` — both env-driven `false` defaults.
5. Read Chris sequencing directive from the current session.
6. If directive names any of (c) / (d) / (e) / (f), execute per that path's discipline. If ambiguous or absent, ask.

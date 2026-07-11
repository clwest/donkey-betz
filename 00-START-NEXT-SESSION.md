# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2748 CLOSED — SUB-PHASE 3 AUTHORIZED FOR S2749

**Refreshed 2026-07-10 (SESSION 2748 CLOSED. 4 PRs merged: Phase 4 Sub-phase 0 substrate (@ops_aggregate_allowed decorator + §11 ledger + architecture doc), Sub-phase 1 (golden fixture + matrix runner 5 cells), §5.1.b hotfix (3 destructive-mutation sites), Sub-phase 2 (hybrid B+C matrix expansion + F1A cross-tenant fixture + §5.1.b extended to 5 sites incl. anonymous content leak on get_deliverable). Harness caught real security bugs during Rigby SIGN Q2 Edit 2 tightening cycles. §14 two-triggers-plus threshold MET decisively (5 instances of Http404-swallow pattern in views_deliverables.py). Sub-phase 3 opens with §14 codification + AST scan module + intentional-immutability contract + endpoint sentinels + coverage-gap report. Full session substance in `docs/handoffs/SESSION_2748_I0302_PHASE_4_SUB_PHASE_0_1_2_COMPLETE.md`.**

Session anchors (read in order):

1. [`docs/handoffs/SESSION_2748_I0302_PHASE_4_SUB_PHASE_0_1_2_COMPLETE.md`](docs/handoffs/SESSION_2748_I0302_PHASE_4_SUB_PHASE_0_1_2_COMPLETE.md) — S2748 delivery ledger, §5.1.b 5-site table, §14 threshold codification, Sub-phase 3 opening protocol
2. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture doc; §6 implementation order + §6.a Sub-phase 3 research inputs
3. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — §5.1.b 5-site amendment (D1 sweep gaps + Http404-swallow pattern) + §11 `@ops_aggregate_allowed` substrate + §14 threshold tally
4. [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](docs/research/implementation/real_user_readiness/CAMPAIGN.md) — RUR parent program (RUR-C1 parent invariant: I-0301 CLOSED + I-0302 Phase 4 in progress + I-0303 not yet opened)
5. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)

**Prior sessions (background context):** S2747 (Phase 3 wiring COMPLETE — 10 PRs, 144 sites); S2746 (Phase 2 predicate module RATIFIED); S2745 (engineering-pivot directive + cost threshold observation opened); S2742 (Playbook v0.4.1 + RUR CAMPAIGN parent doc + I-0301 CLOSED).

---

## P0 — COST THRESHOLD OBSERVATION CHECK-IN (actionable 2026-07-11+)

**Do this FIRST before candidate selection.** Deferred at S2746, S2747, S2748 per memory rule `project_p0_cost_threshold_check_deferred_to_20260711.md` — **actionable on 2026-07-11 sessions onward.**

**State at open:**
- `month: $500.00` (~2× the $246/mo baseline from S2743)
- `enforce_mode: monitor` (no enforcement — passive accumulation only)
- Set locally on Chris's dev DB via `python manage.py cost_thresholds --set month 500`
- Observation period started 2026-07-10 07:35 MDT (accumulating ~24-48+ hours at S2749 open depending on session timing)

**Report to Chris at session open:**

1. **Current threshold config** — run `python manage.py cost_thresholds`; confirm `month: $500.00` still set and mode still `monitor`. Flag any drift.
2. **Accumulation** — query `LLMCallLog` (or the equivalent cost-accumulation surface used by the beat task) for the period since 2026-07-10 07:35 MDT. Report: total accumulated $, % of $500 ceiling, top 3 cost drivers by model/service.
3. **Anomalies** — any single-hour spike >$20, any new provider showing up, any `[COST_MONITOR]` log lines showing near-threshold behavior. If clean, say so explicitly.
4. **Advance recommendation** — based on observation-period data, is 24+ hours of clean observation enough to advance to `--set-mode freeze` (shadow mode), or does Chris want to observe longer? Rigby SIGN on the recommendation before proposing to Chris.

**Do NOT flip to freeze mode without explicit Chris D-verdict.** Per S2735 P1 gate discipline.

Cross-visibility: Rigby workspace deliverable `06f04b41-91e1-4a00-8b8e-0905502e7d83` ("Rigby: Cost threshold observation period — opened 2026-07-10 (S2744)"). Ask Rigby about the observation and she has full context.

---

## PRIMARY WORK — I-0302 Phase 4 Sub-phase 3 (harness completion + §14 codification)

**Sub-phase 3 authorized by Sub-phase 2 close ratification 2026-07-10.** Session close-out routed §14 codification design SIGN through Rigby (F1 = 0.80, F2 = 0.74, F3 = 0.76). All folds match Claude's leans. No Chris ratification needed for the design itself.

### Sub-phase 3 opening moves (per I-030203 §6 steps 10-15 + Rigby §14 SIGN)

Recommended sequence (adjust per Chris directive at S2749 open):

1. **§14 codification substrate** — per Rigby F1 SIGN `C` (extend Phase 4 harness AST scan module):
   - Ship `tests/security/test_i0302_p4_ast_conformance.py` — one canonical "security conformance AST" pytest module
   - Includes both `@ops_aggregate_allowed` recognition AND Http404-swallow anti-pattern detection
   - Per Rigby F2 SIGN `B`: scope = all Django view files (`core/views*.py` + `apps/*/views*.py` + DRF viewsets). Define path allowlist heuristics in the ledger.
   - Per Rigby F3 SIGN `A`: retroactive sweep FIRST (report-only mode) → dedicated batch-fix PR → flip to enforcing mode. Zero-known-violations at enable time.
   - **Rigby offered to propose the exact AST rule definition** — capture at Sub-phase 3 open by routing "please propose the concrete AST rule for the Http404-swallow anti-pattern"

2. **Intentional-immutability contract for Initiative + ChatConversation** (Chris D-verdict at S2748 close):
   - Assert unsafe methods (PUT/PATCH/DELETE) return 405/404 as absence-contract
   - Add cells to matrix runner
   - Update I-030203 §7 close criteria

3. **Endpoint sentinels** (I-030203 §1.2 per Rigby SIGN F1 hybrid substrate):
   - Route to Rigby: "propose 10-30 hand-picked view-layer risk endpoints per app area based on Phase 3 wiring evidence + view files touched in PRs #3100-#3109"
   - Focus categories: custom actions, nested routes, bulk endpoints, `/me/` endpoints, exports
   - Ship as `tests/security/test_i0302_p4_endpoint_sentinels.py`

4. **Deferred-surface coverage-gap report** (I-030203 §4.2):
   - JSON emit at `test_reports/i0302_p4_coverage_gaps.json`
   - Per §5.3.b (C2, ~126 sites) + §5.1.a (D non-view) + §5.5.a (Document WebSocket)
   - Cheap posture probes (HEAD/OPTIONS or minimal auth check) where feasible

5. **VIP-scope carve-out coverage on `get_deliverable`** — extend fixture with VIP membership row; test the VIP-workspace read path currently deferred in Sub-phase 2 GET-item cell

### Sub-phase 3 research inputs (bounded docs-only passes; per I-030203 §6.a)

Run BEFORE code lands (they inform the endpoint sentinel choices + matrix expansion decisions):

- **AgentExecution mutation semantics** — confirm no user-facing UPDATE/DELETE (likely per S2748 Initiative + ChatConversation finding); if any exist, add absence-contract cells
- **Document `user` vs `owner` field question** — investigate `views_rag_embeddings.py:470/836` uses `Document.objects.get(id=..., user=user)` on a model whose FK is named `owner`; dual-field, legacy alias, or runtime bug?
- **CREATE-parent-binding endpoint map** — inventory which endpoints create rows across the 5 canonical models + identify the parent-binding field per endpoint
- **AGGREGATE endpoint inventory** — enumerate true aggregates vs stats-with-nested-shape endpoints (extend §3.8 canonical JSON path table)
- **Non-canonical model follow-on** — scope decision on `LegalDocument` / `LitigationDocument` / `ReviewDocument` unscoped `.objects.get(id=...)` findings from §5.1.b sweep (in I-0302 scope or separate arc?)

### Phase 4 close criteria (unchanged from I-030203 §7)

Phase 4 closes when ALL of:

1. Matrix runner exists and passes for all applicable 5 × 7 cells (minus explicit deferred skips)
2. Endpoint sentinels exist for 10+ hand-picked risk endpoints, 4 roles each
3. AST scan module wired; harness fails collection on `@ops_aggregate_allowed` contract violation OR Http404-swallow violation
4. Deferred-surface coverage-gap report emits structured JSON
5. `security-conformance.yml` runs the harness on every relevant PR
6. Rigby SIGN-PASS on shipped harness
7. Chris D-verdict ratifying Phase 4 close
8. Phase 4 close doc appended (amend I-030203 §8 close statement OR create `I-030204_phase4_close.md`)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `5637dcd6` (PR #3114 merged; Sub-phase 2 complete + §5.1.b extended to 5 sites) |
| Playbook version | v0.4.1 (unchanged since S2742) |
| Playbook rule count | 196 |
| Constitutional Debt | Zero outstanding |
| Session pin | `pa-59d27abadeed4411` (active — carry-forward from S2748) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-59d27abadeed4411` (rotated at S2748 open) |
| Live infra state | `SystemConfiguration cost_threshold_month = 500`, mode = `monitor` (observation period accumulating since 2026-07-10 07:35 MDT) |
| RUR arc state | I-0301 CLOSED · I-0302 Phases 1-3 CLOSED · Phase 4 Sub-phases 0/1/2 CLOSED · Phase 4 Sub-phase 3 AUTHORIZED · Phase 4 close pending · Phase 5 (arc close) not yet opened · I-0303 not yet opened · RUR-C1 parent OPEN |

---

## What S2748 shipped (4 PRs)

Full delivery ledger in `docs/handoffs/SESSION_2748_I0302_PHASE_4_SUB_PHASE_0_1_2_COMPLETE.md` §1. Compressed:

| PR | Sub-phase / Class | HEAD |
|---|---|---|
| #3111 | Sub-phase 0 — decorator substrate + §11 ledger + architecture doc | `0edc85cc` |
| #3112 | Sub-phase 1 — golden fixture + 5-cell matrix (20 tests) | `df4e94e6` |
| #3113 | §5.1.b hotfix (3 destructive-mutation sites) | `41c8d458` |
| #3114 | Sub-phase 2 hybrid B+C (21 tests) + F1A fixture + §5.1.b extended to 5 sites (5th = anonymous content leak on `get_deliverable` caught by Rigby Q2 Edit 2) | `5637dcd6` |

**§14 two-triggers-plus threshold MET decisively** — Http404-swallow pattern documented in 5 sites in `views_deliverables.py`; Sub-phase 3 opening MUST codify AST check per Rigby final SIGN.

---

## Candidate queue for S2749 — Sub-phase 3 is primary

Per Chris close directive S2748: PR #3114 merged; §14 codification design SIGN routed and complete. S2749 opens with Sub-phase 3 authorized as primary work.

### PRIMARY — I-0302 Phase 4 Sub-phase 3

See "Sub-phase 3 opening moves" above. §14 codification substrate is the natural first move (Rigby F1-F3 SIGN pre-ratified); intentional-immutability contract + endpoint sentinels + coverage-gap report follow.

### CLASS 1 — NET-NEW ENGINEERING (secondary options)

Per S2745 engineering-bias rule, always propose 1-3 net-new candidates every session:

1. **New Employee OS employee (4th)** — vertical slice: new `AIEmployee` + `JobContract` + MissionRunner steps + admin visibility
2. **Betting dashboard new feature** — 9-tab dashboard needs Chris to name the gap
3. **New spider on Chris-named data gap** — spider class + fixture + test + registry entry + signal wiring
4. **New UI page on Command Center** — 61 routes; requires Chris naming the workflow
5. **Discord bot new command** — bounded Cog + slash-command slice

### CLASS 4 — Meta-methodology / Codification candidates

**Per pivot rule: propose only if Chris explicitly asks for methodology work.**

- **§14 codification pattern from S2748** — Http404-swallow tally reached 5 sites; Rigby SIGN'd F1-F3 substrate; NO Chris ratification needed for design but ratification WOULD be needed if scope widens to non-view files. Track for future playbook integration if the pattern (harness surfaces bug → Rigby tightens → codify) repeats.
- **"Rigby SIGN-WITH-EDITS surfaces production bug" workflow pattern** — S2748 Q2 Edit 2 (content-leak invariant on get_deliverable anonymous) caught real bug. Watch for 2nd instance to trigger playbook memory codification.
- **"Chris scope-expansion pattern"** — "A — expand this PR" applied twice this session on same-class bugs from same discovery. Watch for 3rd instance to trigger candidate playbook rule.

### External signal-driven

- **Production observation** — `would_freeze` shadow live from S2739; `[COST_MONITOR] startup:` line live from S2743; CLI live from S2744; observation period live from S2745. The P0 check-in above is the current forward motion here.

---

## Recommended session-open protocol (S2749)

1. `context-kit orient`
2. Read `docs/handoffs/SESSION_2748_I0302_PHASE_4_SUB_PHASE_0_1_2_COMPLETE.md` in full — §1 delivery ledger + §3 5-site hotfix table + §4 Chris directives + §5 what's next
3. Verify runtime state: `git log --oneline -5`, `celery inspect ping`
4. **P0 check** (per top-of-file callout, now actionable): run the observation check-in; report accumulation, anomalies, advance recommendation to Chris
5. `pa_local.sh` pin already carry-forward at `pa-59d27abadeed4411` — verify with `python tools/pa_chat.py "ping — verify pin active" --tools`
6. **Confirm Sub-phase 3 as primary work** with Chris; propose §14 codification substrate as opening move (Rigby offered to propose AST rule definition)
7. **On acceptance:** route to Rigby "propose the concrete AST rule for the Http404-swallow anti-pattern" → implement → sweep → enforce
8. **Alternative:** if Chris wants to interleave a Class 1 net-new build, pause Sub-phase 3 explicitly. Do NOT default to Sub-phase 3 without confirmation.

---

## Reference documents

Ordered by frequency of use:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (L7 anchor v0.4.1)
2. [`docs/EOS_RULES.md`](docs/EOS_RULES.md) — R1/R2/R3
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — ratified v0.4.1 body (196 rules)
4. [`docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md`](docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md) — Phase 4 architecture (§6 + §6.a)
5. [`docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md`](docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md) — Phase 1 ledger with §5.1.b 5-site amendment + §11 substrate + §14 tally
6. [`docs/research/platform/platform_capability_graph.md`](docs/research/platform/platform_capability_graph.md) — capability chains + append-only refreshes

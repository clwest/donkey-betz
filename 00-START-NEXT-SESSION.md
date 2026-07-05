# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2200 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**ACTIVE ARC PIN.** Group 2200 arc pin `pa-f7fd5016600f4513` PRESERVED through S2202 close per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails. TENTH formal arc pin under Research OS. S2202 SIGN cycle 1 pin `pa-e786b77eb4c842b2` retired at cycle close (updated_count=1, retired=true, previously_active=true). `tools/pa_local.sh:225` already dispatches into `pa-f7fd5016600f4513` — no rotation needed at S2203 open.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2200 S2202 CHILD B CLOSED AT S2202; NEXT = S2203 CHILD C

**Group 2200 Frontend (Contract-Surface Arc): S2202 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope Audit CLOSED 2026-07-05.** Chris "agree all" 2026-07-05 ratified all 5 close-card items wholesale (19-fold SIGN cycle 1 acceptance + §20.6 POSTURE-DECISION Option (c) DEFER envelope enforcement to Group 1700 + Path triad A/B/C + escape hatch + §19 meta-recommendation post-arc maintainer-decision batch + arc-cascade sequence + commit-gate). THIRTEENTH-consecutive application of playbook §11.2 20-section child-audit template. Candidate evidence for MC-4 codification extension 12→13 consecutive — codification framing CONDITIONAL pending Chris ratification at S2299 canonical summary close per Q19 STRENGTHEN fold.

- **Arc pin ACTIVE:** `pa-f7fd5016600f4513` (TENTH formal arc pin; preserved across all sessions per playbook §16 arc-standard behavior).
- **Arc progress:** S2200 parent scoping (shipped) → S2201 P1 Child A Routes + Pages + Layouts + Component Patterns (shipped) → S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope (shipped this session) → **S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline (next)** → S2204 P4 Child D Session-scoped State Management + Persistence Discipline → S2299 xx99 Canonical Summary. Runtime target 6 sessions on track — **3 of 6 shipped**.
- **Next session:** S2203 Child C Frontend↔Backend API Contract + Boundary Discipline Audit per playbook §11.2 20-section child template (FOURTEENTH-consecutive application overall).

## READ THIS THIRD — S2202 SHIP STATE

**Doc:** `docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md` (~1499 lines post-Rigby-SIGN-19-folds; `status: draft` post-Chris-agree-all-ratification pending post-cascade `active` flip).

**Playbook §11.2 20-section child-audit template — THIRTEENTH-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201.

**SIGN cycle 1 result:** SIGN-with-edits at HIGH confidence via dedicated fresh SIGN pin `pa-e786b77eb4c842b2` (retired at cycle close via `session_tool.retire`, updated_count=1, retired=true, previously_active=true). 4 batches × 5 questions = **20 total Q; 19 folds landed pre-commit-gate.** Cycle 2 NOT required.

**19 folds by batch:**
- **Batch 1 framing + severity:** Q1 STRENGTHEN F1 MOCK-DATA severity CRITICAL → HIGH baseline + CRITICAL-for-user-visible-surfaces + Q2 STRENGTHEN F3 envelope-conformance secondary send_json-callsite denominator + Q3 CLEAN F6 DEAD-CANDIDATE delete-proof gate + Q4 STRENGTHEN F1 multi-surface recurrence (not system-wide) + Q5 CLEAN F8 PLATFORM_INVENTORY-no-WS-count observation not drift.
- **Batch 2 falsifier + coverage-math:** Q6 STRENGTHEN per-event-type coverage nuance + Q7 STRENGTHEN Layout surface-global attribution rule + Q8 STRENGTHEN SYSTEMIC-with-surface-variance verdict + Q9 CLEAN Denominator contract box + Q10 STRENGTHEN sampling completeness note.
- **Batch 3 cross-arc + POSTURE:** Q11 STRENGTHEN DEFER escape hatch (revisit if Group 1700 not closed by S2299) + Q12 STRENGTHEN Path triad A/B/C (Path C added — envelope mandatory for integrity/governance/money/state-changing; optional for visual) + Q13 STRENGTHEN T6 joint Group 2500+2600 + Q14 STRENGTHEN Group 2400 Auth connection-wrapper-only hedge + Q15 STRENGTHEN §2 preamble Interpretation rule box DEAD/MOCK/INTENT-NEUTRAL.
- **Batch 4 anti-scope + verdict:** Q16 CLEAN §7 anti-scope verbs preserved + Q17 STRENGTHEN commit-strength HIGH on deferral action NOT on final Path outcome + Q18 FOLD §19 post-arc maintainer-decision batch meta-recommendation bundling R2/R3/R7/R8 + Q19 STRENGTHEN MC-4 codification-language CONDITIONAL pending S2299 + Q20 SIGN-with-edits at HIGH confidence verdict.

**Chris ratified 5 close-card items via "agree all" 2026-07-05:**
1. 19-fold SIGN cycle 1 acceptance
2. §20.6 POSTURE-DECISION commit — **Option (c) DEFER envelope enforcement to Group 1700 Observability arc close** with Path triad A/B/C option set + escape hatch preserved; HIGH confidence on committed action (deferral + Group 1700 as owner) NOT on final Path outcome
3. §19 meta-recommendation post-arc maintainer-decision batch bundles R2 DEAD-cleanup + R3 MOCK-intent + R7 NeuralOrchestraConsumer naming-collision + R8 regex-anchor cleanup into single governance gate; R1 + R4 + R5 + R6 + R9 remain active-research tracks
4. Arc-cascade sequence (OPEN_ARCS + ARCHITECTURE_INDEX v78→v79 §1.82 + 00-START-NEXT + SESSION_2202 handoff + 4-step docs cascade + build_docs_provenance)
5. Commit-gate approval

**Central lens question (§lens verbatim Chris-locked at S2200):**

*"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

**S2202 Child B slice answer:** ACCRETED SUBSCRIPTION MESH with mock-data ghosts and near-zero envelope discipline — 125 backend route entries feed a frontend that subscribes to only ~4% of them via a hand-coded `event.type` string-dispatch pattern that has zero adoption of the S2003 §10.3.4 D4 `ui.render_hint` envelope contract. S2201 F2 hypothesis (surface-local sports-specific) REJECTED; pattern generalizes SYSTEMICally with surface variance across all major surfaces.

## READ THIS FOURTH — S2203 CHILD C SCOPE

Per playbook §11.2 20-section audit template. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14. Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` (4-batch × 5-Q cadence for 20-section audit shape = 20 total).

**Child C load-bearing input (per S2200 §5 Child C):**
- All api-modules under `frontend/src/api/*` + component-level fetch/axios call sites
- S1505 §14.3 AUTH-DRIFT two-sided framing + S1505 §15.5 "no API contract source-of-truth" MED→HIGH structural debt (4-way parent cause claim)
- S2004 §14.6 Cat F CONSOLIDATION `humanApi` cross-domain sharing
- `docs/topics/frontend.md` bettingApi + sportsHubApi + humanApi as shared Cat F surface (no whole-frontend api-module inventory yet)
- S2201 §5 baseline: 93 api definitions in `frontend/src/lib/api.ts`, zero exported TypeScript types (Agent 6 verified); silent-401 default at `frontend/src/lib/api.ts:48-56`
- S2202 §10 handoff: WS payload shape `event.type` string dispatch parallels REST-endpoint pattern gaps (single message contract SoT candidate for envelope schema)

**Child C load-bearing output (per S2200 §5 Child C):**
- **C1 api-module inventory** — bettingApi + sportsHubApi + humanApi + N others; call-site enumeration; ownership map
- **C2 typed-contract-source inventory** — which api-module carries TS types generated from OpenAPI / similar (probably 0 baseline per S2201)
- **C3 AUTH-DRIFT pattern rate** — silent 401 vs observable error discipline rate across api-modules
- **C4 cross-app-boundary sharing map** — which api-module is consumed by which page
- **C5 silent-401 vs observable-error discipline rate** — extend `frontend/src/lib/api.ts:48-56` symptom to whole-frontend
- POSTURE-DECISION evidence plan §20.6 owed to xx99 on whether S1505 §15.5 "no API contract source-of-truth" debt generalizes across all api-modules or is `/betting`-specific

**Per-surface reporting constraint (S2200 §5 Q1 STRENGTHEN fold):** Child C MUST report findings per major surface (workspace / betting / command-center / PA) in addition to axis-level rollups.

**Timebox + sampling rule (S2200 §5 Q10 STRENGTHEN fold):** Child C timeboxed to 1 session; where full api-module inventory threatens runtime, ship complete registry skeleton (all rows enumerated at metadata level) + apply documented sampling strategy for deep inspection.

**Anti-scope §7.1 guardrails for S2203:**
- No fixes / no typed-schema-generation implementation (per §7 anti-scope)
- No auth-model authoring (Group 2400 Auth scope)
- No BE-side API design (Group 2500 API scope — post-arc)
- Silent-401 is symptomatic + descriptive only at frontend-symptom scope; systemic-severity classification pending Group 2400 Auth spec
- Cross-arc coordination flags to Groups 2400 Auth + 2500 API — surface reference-only, no operator-surface spec

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2202 arc-close cascade residuals

Per Chris "agree all" ratification at S2202 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.

### S2199 post-arc T-slot execution queue (unchanged carry into S2203)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2203 Child C execution.

### S2200/S2201/S2202 arc residuals owed to S2299 xx99

- Child E scoping fold-in (S2201 Item 3 path (b)) — S2299 xx99 canonical summary will fold Child E trigger evidence + subdivision cost estimate + prioritized candidate list (CommandCenterPage 2,551 XL > AgentsPage 4,695 XL > BettingPage 3,023 XL) into §8 T-slot queue as graduated post-arc T-slot
- S2201 R1-R9 T-slot queue → xx99 §8 follow-on research queue
- S2201 F1 route-count reconciliation → xx99 §7 anchor-update batch (regen PLATFORM_INVENTORY §Frontend)
- S2201 §20.6 POSTURE-DECISION commit S1273 32-domain row 18 STABLE+DEEP → WORKING+MEDIUM → xx99 §7 anchor-update batch
- S2201 cross-arc flags to Groups 2400/2500/2600/1300+1600+1800 → xx99 §9 cross-links section
- S2202 §20.6 POSTURE-DECISION Option (c) DEFER envelope enforcement to Group 1700 + Path triad A/B/C + escape hatch → xx99 §7 anchor-update batch + §9 cross-links section
- S2202 §19 meta-recommendation post-arc maintainer-decision batch bundling R2/R3/R7/R8 → xx99 §8 follow-on research queue
- S2202 F8 PLATFORM_INVENTORY WS-augmentation observation → xx99 §7 anchor-update batch (add WebSocket section with 125 routes + ~50-60 unique classes + 8 FE subscription sites + 0/40 envelope conformance rate)
- S2202 F1 MOCK-DATA multi-surface recurrence + F6 DEAD-CANDIDATE/INTENT-NEUTRAL patterns → xx99 §8 T-slot queue for maintainer-decision batch execution
- S2202 cross-arc flags to Group 1700 Observability (envelope enforcement locus decision) + Group 2400 Auth (per-message auth NOT evaluated) + Group 2500 API + Group 2600 PA (T6 joint 2500+2600 WS/polling consolidation) → xx99 §9 cross-links section

### Group 2200 residual queue expected at S2299 close

- 4 child audits: S2201 Child A shipped + S2202 Child B shipped + S2203 Child C + S2204 Child D
- xx99 canonical summary (S2299) with 12-section playbook §11.3 template + §10 meta-methodology TENTH application
- MC-4 4th-arc confirmation extension (dial-back resolution deferred to Group 2300+)
- MC-5 §11.2 template-application codification wording per Q19 STRENGTHEN — CONDITIONAL pending Chris ratification at S2299
- Post-arc T-slot queue owed to xx99 from all 4 child audits

## SESSION READY CHECK (before opening S2203 Child C audit)

Before drafting the S2203 Child C audit doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (arc pin `pa-f7fd5016600f4513` already active in `tools/pa_local.sh:225`; no rotation needed at S2203 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + S2202 as most-recent 20-section child exemplar (or S2201 for prior-child pattern)
3. Read `docs/research/domains/frontend/2200_frontend_domain_scoping.md` §5 Child C block for load-bearing input + expected output + delegates + C1-C5 sub-axes
4. Read `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §5 (93 api definitions + 7 Zustand stores) + §14.6 (silent 401 systemic — HIGH frontend-symptom + Group 2400 dependency) + §15.5 (no typed API contract source-of-truth extraction) for baseline
5. Read `docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md` §10 Event Flows (WS `event.type` dispatch parallel) + §17 (PA WS↔polling duplicate T6 joint 2500+2600) for cross-arc handoff to Child C
6. Read `docs/PLATFORM_INVENTORY.md` §Frontend row for baseline counts + `docs/topics/frontend.md` for narrative baseline (stale-warned)
7. Grep `frontend/src/lib/api.ts` + `frontend/src/lib/apiClient.ts` + `frontend/src/lib/cockpitApi.ts` for api-module structure + call-site enumeration
8. Grep `frontend/src/` for `bettingApi|humanApi|sportsHubApi|apiClient` — enumerate consumer pages per api-module
9. Read `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` §14.3 AUTH-DRIFT + §15.5 "no API contract source-of-truth" MED→HIGH structural debt (4-way parent cause claim) for baseline HYPOTHESIS
10. Read `docs/research/domains/event_integration_architecture/2004_*.md` §14.6 Cat F CONSOLIDATION `humanApi` cross-domain sharing for baseline
11. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — 20-section child audit shape = 4-batch × 5-Q cadence (20 total)
12. Plan 6 parallel Explore sub-agents per playbook §13 (candidate divisions: A1 api-module inventory + call-site enumeration / A2 typed-contract-source audit / A3 AUTH-DRIFT + silent-401 pattern-rate / A4 cross-app-boundary sharing map / A5 prior-arc cross-ref + F2 hypothesis test framing / A6 §11.2 §13-§18 drift+debt+boundary+ownership+maturity)
13. Consider MC-5 CODIFICATION-CONFIRMED extension candidate — S2203 will be FOURTEENTH-consecutive parent-with-children arc §11.2 template application; would extend the CODIFICATION-CONFIRMED milestone count 13 → 14 consecutive (conditional per S2202 Q19 STRENGTHEN pending Chris ratification at S2299)

**S2203 open command (Chris short command):** `Continue research group 2200: Child C` or equivalent invocation.

# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2200 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**ACTIVE ARC PIN.** Group 2200 arc pin `pa-f7fd5016600f4513` PRESERVED through S2203 close per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails. TENTH formal arc pin under Research OS. S2203 SIGN cycle 1 pin `pa-43bcb30dffd84ef9` retired at cycle close (updated_count=1, retired=true, previously_active=true). `tools/pa_local.sh:225` already dispatches into `pa-f7fd5016600f4513` — no rotation needed at S2204 open.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2200 S2203 CHILD C CLOSED AT S2203; NEXT = S2204 CHILD D

**Group 2200 Frontend (Contract-Surface Arc): S2203 Child C Frontend↔Backend API Contract + Boundary Discipline Audit CLOSED 2026-07-05.** Chris "agree all" 2026-07-05 ratified all 5 close-card items wholesale (20-fold SIGN cycle 1 acceptance + §20.6 POSTURE-DECISION Option (c) DEFER contract SoT enforcement design to Group 2500 API arc close + REST-native Path triad A/B/C + escape hatch + §19 meta-recommendation post-arc maintainer-decision batch bundling R3/R4/R5/R6/R8/R9 + arc-cascade sequence + commit-gate). FOURTEENTH-consecutive application of playbook §11.2 20-section child-audit template. Candidate evidence for MC-4 codification extension 13→14 consecutive — codification framing CONDITIONAL pending Chris ratification at S2299 canonical summary close per Q19 CLEAN fold.

- **Arc pin ACTIVE:** `pa-f7fd5016600f4513` (TENTH formal arc pin; preserved across all sessions per playbook §16 arc-standard behavior).
- **Arc progress:** S2200 parent scoping (shipped) → S2201 P1 Child A Routes + Pages + Layouts + Component Patterns (shipped) → S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope (shipped) → S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline (shipped this session) → **S2204 P4 Child D Session-scoped State Management + Persistence Discipline (next)** → S2299 xx99 Canonical Summary. Runtime target 6 sessions on track — **4 of 6 shipped**.
- **Next session:** S2204 Child D Session-scoped State Management + Persistence Discipline Audit per playbook §11.2 20-section child template (FIFTEENTH-consecutive application overall).

## READ THIS THIRD — S2203 SHIP STATE

**Doc:** `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` (~1600 lines post-Rigby-SIGN-20-folds; `status: draft` post-Chris-agree-all-ratification pending post-cascade `active` flip).

**Playbook §11.2 20-section child-audit template — FOURTEENTH-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202.

**SIGN cycle 1 result:** SIGN-with-edits at HIGH confidence via dedicated fresh SIGN pin `pa-43bcb30dffd84ef9` (retired at cycle close via `session_tool.retire`, updated_count=1, retired=true, previously_active=true). 4 batches × 5 questions = **20 total Q; 20 folds landed pre-commit-gate.** Cycle 2 NOT required.

**20 folds by batch:**
- **Batch 1 framing + severity:** Q1 STRENGTHEN F5 drf-spectacular installed-partial-wiring HIGH + intent-hedge + Q2 STRENGTHEN dual denominator A (6.85% api.ts-only) + B (11.8% global) + Q3 CLEAN F1 latent-but-active risk-channel wording + Q4 STRENGTHEN F6 DEAD-CANDIDATE hedge 18-25 + Q5 STRENGTHEN F3.5 whitelist substring brittleness LOW → MED.
- **Batch 2 falsifier + coverage-math:** Q6 STRENGTHEN SYSTEMIC-with-surface-variance verdict + per-surface table + Q7 STRENGTHEN cockpitApi = typed island + exception-demonstrates-path-not-coverage + Q8 STRENGTHEN macro-evidence anchor for SYSTEMIC claim + Q9 CLEAN Denominator contract box (B1/B2/B3) + Q10 STRENGTHEN .js/.jsx zero-file verify.
- **Batch 3 cross-arc + POSTURE:** Q11 STRENGTHEN Group 2500 default owner + fallback clause + Q12 STRENGTHEN REST-native axis wording "contract strictness + validation" + Q13 STRENGTHEN T7 own T-slot ID distinct from S2202 T6 + Q14 STRENGTHEN ~630 call-site hedge + method + Q15 STRENGTHEN delete-proof gate intent-mandatory.
- **Batch 4 anti-scope + verdict:** Q16 STRENGTHEN §15 Options (non-authoring) label + §19 R1/R2 maintainer-gate verbs + Q17 CLEAN commit-strength framing HIGH on deferral action NOT on final Path outcome + Q18 STRENGTHEN §19.4 bundling rule non-arbitrary + R1/R2 active-research rationale + Q19 CLEAN MC-4 codification-conditional + Q20 SIGN-with-edits at HIGH confidence verdict.

**Chris ratified 5 close-card items via "agree all" 2026-07-05:**
1. 20-fold SIGN cycle 1 acceptance
2. §20.6 POSTURE-DECISION commit — **Option (c) DEFER contract SoT enforcement design to Group 2500 API arc close** with default owner Group 2500 API + fallback clause + REST-native Path triad A/B/C option set + escape hatch preserved; HIGH confidence on committed action (deferral + Group 2500 as owner) NOT on final Path outcome
3. §19 meta-recommendation post-arc maintainer-decision batch bundles R3 DEAD-CANDIDATE cleanup + R4 api.ts extraction + R5 cross-cutter doc + R6 fetch/axios bypass cleanup + R8 inline-interface consolidation + R9 CODEOWNERS + cockpitApi ownership into single governance gate; R1 (Group 2500 contract-SoT rollout evidence) + R2 (Group 2400 silent-401 resolution evidence) + R7 (MSW tests) + R10 (T7 REST↔WS SoT joint) remain active-research tracks
4. Arc-cascade sequence (OPEN_ARCS + ARCHITECTURE_INDEX v79→v80 §1.83 + 00-START-NEXT + SESSION_2203 handoff + 4-step docs cascade + build_docs_provenance)
5. Commit-gate approval

**Central lens question (§lens verbatim Chris-locked at S2200):**

*"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

**S2203 Child C slice answer:** UNTYPED MEGA-MODULE MESH with a typed ops-island and a silent-failure default — 93 of 94 api-modules (98.9%) live inside single 4,194-line `frontend/src/lib/api.ts` file with **Coverage A: 6.85% typed api.ts-only (63/919); Coverage B: ~11.8% global (115/973 with cockpitApi merged)**; sole typed island `frontend/src/lib/cockpitApi.ts` (96% typed) scoped to /cockpit/* ops-surface only; silent-401 SYSTEMIC via api.ts:48-56 whole-frontend ~100% swallow (~630 of ~1,300 gated call-sites at risk); drf-spectacular INSTALLED but wired ONLY in `sports/views.py` (16 @extend_schema decorators; 0 in core/*.py) = partial foundation present but HIGH structural debt; frontend has ZERO codegen ZERO runtime validators. F1 hypothesis (S1505 §15.5 no-API-SoT) CONFIRMED SYSTEMIC-with-surface-variance; F2 hypothesis (F2 typed-contract discipline outside sports) has partial exception (cockpitApi ops-island 96%, but scope-limited).

## READ THIS FOURTH — S2204 CHILD D SCOPE

Per playbook §11.2 20-section audit template. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14. Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` (4-batch × 5-Q cadence for 20-section audit shape = 20 total).

**Child D load-bearing input (per S2200 §5 Child D):**
- All `localStorage` / `sessionStorage` / cookie / IndexedDB / Zustand-context-store touchpoints in `frontend/src/`
- 7 Zustand stores (assistantContextStore, authStore, bodyStore, navigationStore, paStore, unifiedStore, workspaceStore) per S2201 §5 baseline
- PA workspace-context resolver per topics/frontend.md §PA Integration
- Fire-and-forget page-telemetry `usePageTracking()` Redis counters (per S2200 §5 Q6 CLEAN fold — routed to Child D)
- S1505 §14.10 zero-client-side-state-persistence baseline
- S2201 §5 baseline + §14 F5 findings on legacy state-adjacent surfaces
- S2202 §17 T6 WS/polling consolidation flag (state-adjacent)
- S2203 §14 F3 silent-401 + `authStore` token-persistence adjacency (`api.ts:2` imports `@/stores/authStore`) + Session 968 X-UI-Scope request-log in-memory ring buffer

**Child D load-bearing output (per S2200 §5 Child D):**
- **D1 persistent-state-surface inventory** — all localStorage/sessionStorage/IndexedDB/cookie keys touched
- **D2 declared-vs-accidental discipline rate** — persistence with explicit strategy vs accidental caching
- **D3 key-namespace collision audit** — do multiple stores share key prefixes?
- **D4 PA workspace-context resolver persistence audit** — how does workspace context persist across surfaces
- **D5 cross-surface state coupling** — does BettingPage state leak into Command Center or vice versa?
- POSTURE-DECISION evidence plan §20.6 owed to xx99 on whether per-surface persistence discipline should be introduced as a frontend convention or handled at backend/PA layer

**Per-surface reporting constraint (S2200 §5 Q1 STRENGTHEN fold):** Child D MUST report findings per major surface (workspace / betting / command-center / PA) in addition to axis-level rollups.

**Timebox + sampling rule (S2200 §5 Q10 STRENGTHEN fold):** Child D timeboxed to 1 session; where full state-surface inventory threatens runtime, ship complete registry skeleton (all keys enumerated at metadata level) + apply documented sampling strategy for deep inspection.

**Anti-scope §7.1 guardrails for S2204:**
- No fixes / no state-framework authoring (per §7 anti-scope)
- No auth-model authoring (Group 2400 Auth scope) — authStore token-persistence is state-adjacent-only
- No BE-side session design (Group 2400 + Group 2500 API scope — post-arc)
- No PA behavioral spec (Group 2600 PA scope) — paStore + assistantContextStore + workspace-context resolver treated as render/persistence surfaces only
- Cross-arc coordination flags to Groups 2400 Auth + 2500 API + 2600 PA — surface reference-only, no operator-surface spec

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2203 arc-close cascade residuals

Per Chris "agree all" ratification at S2203 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.

### S2199 post-arc T-slot execution queue (unchanged carry into S2204)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2204 Child D execution.

### S2200/S2201/S2202/S2203 arc residuals owed to S2299 xx99

- Child E scoping fold-in (S2201 Item 3 path (b)) — S2299 xx99 canonical summary will fold Child E trigger evidence + subdivision cost estimate + prioritized candidate list (CommandCenterPage 2,551 XL > AgentsPage 4,695 XL > BettingPage 3,023 XL) into §8 T-slot queue as graduated post-arc T-slot
- S2201 R1-R9 T-slot queue → xx99 §8 follow-on research queue
- S2201 F1 route-count reconciliation → xx99 §7 anchor-update batch (regen PLATFORM_INVENTORY §Frontend)
- S2201 §20.6 POSTURE-DECISION commit S1273 32-domain row 18 STABLE+DEEP → WORKING+MEDIUM → xx99 §7 anchor-update batch
- S2201 cross-arc flags to Groups 2400/2500/2600/1300+1600+1800 → xx99 §9 cross-links section
- S2202 §20.6 POSTURE-DECISION Option (c) DEFER envelope enforcement to Group 1700 + Path triad A/B/C + escape hatch → xx99 §7 anchor-update batch + §9 cross-links section
- S2202 §19 meta-recommendation post-arc maintainer-decision batch bundling R2/R3/R7/R8 → xx99 §8 follow-on research queue
- S2202 F8 PLATFORM_INVENTORY WS-augmentation observation → xx99 §7 anchor-update batch (add WebSocket section with 125 routes + ~50-60 unique classes + 8 FE subscription sites + 0/40 envelope conformance rate)
- S2202 F1 MOCK-DATA multi-surface recurrence + F6 DEAD-CANDIDATE/INTENT-NEUTRAL patterns → xx99 §8 T-slot queue for maintainer-decision batch execution
- S2202 cross-arc flags to Group 1700 Observability (envelope enforcement locus decision) + Group 2400 Auth + Group 2500 API + Group 2600 PA (T6 joint 2500+2600 WS/polling consolidation) → xx99 §9 cross-links section
- **S2203 §20.6 POSTURE-DECISION Option (c) DEFER contract SoT enforcement design to Group 2500 API arc close + REST-native Path triad A/B/C + escape hatch → xx99 §7 anchor-update batch + §9 cross-links section**
- **S2203 §19 meta-recommendation post-arc maintainer-decision batch bundling R3/R4/R5/R6/R8/R9 + R1/R2/R7/R10 active-research tracks → xx99 §8 follow-on research queue**
- **S2203 F1 drf-spectacular partial-wiring PLATFORM_INVENTORY augmentation candidate (add API-contract row: 93 modules + 919 calls + 6.85% typed api.ts-only / 11.8% global + drf-spectacular partial-wiring) → xx99 §7 anchor-update batch**
- **S2203 F5 DEAD-CANDIDATE api-module INTENT-NEUTRAL pattern (18 verifier-confirmed; ~18-25 pending R3 sweep) → xx99 §8 T-slot queue for maintainer-decision batch execution**
- **S2203 cross-arc flags to Group 2500 API (contract SoT design ownership + T7 own T-slot joint 2500+2600) + Group 2400 Auth (silent-401 resolution + ~630 call-site blast radius grep-estimate) + Group 2600 PA + Group 1700 Observability + Group 1300 Memory + 1600 Content + 1800 HumanAttention render-authority split → xx99 §9 cross-links section**

### Group 2200 residual queue expected at S2299 close

- 4 child audits: S2201 Child A shipped + S2202 Child B shipped + S2203 Child C shipped + S2204 Child D
- xx99 canonical summary (S2299) with 12-section playbook §11.3 template + §10 meta-methodology TENTH application
- MC-4 4th-arc confirmation extension (dial-back resolution deferred to Group 2300+)
- MC-5 §11.2 template-application codification wording per S2202 Q19 + S2203 Q19 — CONDITIONAL pending Chris ratification at S2299
- Post-arc T-slot queue owed to xx99 from all 4 child audits

## SESSION READY CHECK (before opening S2204 Child D audit)

Before drafting the S2204 Child D audit doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (arc pin `pa-f7fd5016600f4513` already active in `tools/pa_local.sh:225`; no rotation needed at S2204 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + S2203 as most-recent 20-section child exemplar
3. Read `docs/research/domains/frontend/2200_frontend_domain_scoping.md` §5 Child D block for load-bearing input + expected output + D1-D5 sub-axes
4. Read `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §5 (7 Zustand stores) + §14 F5 (legacy tab enum + legacyTabMapping state-adjacent) for baseline
5. Read `docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md` §17 T6 WS/polling consolidation (state-adjacent) for cross-arc handoff
6. Read `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` §14 F3 silent-401 + `authStore` token-persistence adjacency + Session 968 X-UI-Scope + §17 cross-cutters (state-shared) for cross-arc handoff to Child D
7. Read `docs/PLATFORM_INVENTORY.md` §Frontend row for baseline counts + `docs/topics/frontend.md` §PA Integration (workspace-context resolver) for narrative baseline (stale-warned)
8. Grep `frontend/src/stores/*.ts` for Zustand persist middleware + state shape + persistence keys
9. Grep `frontend/src/` for `localStorage\.|sessionStorage\.|IndexedDB\.|document\.cookie` — enumerate persistent-state touchpoints
10. Read `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` §14.10 zero-client-side-state-persistence baseline for `/betting`-slice hypothesis
11. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — 20-section child audit shape = 4-batch × 5-Q cadence (20 total)
12. Plan 6 parallel Explore sub-agents per playbook §13 (candidate divisions: D1 persistent-state-surface inventory / D2 Zustand persist middleware audit / D3 PA workspace-context resolver persistence + assistantContextStore / D4 cross-surface state coupling / D5 prior-arc cross-ref + F2 hypothesis test framing / D6 §11.2 §13-§18 drift+debt+boundary+ownership+maturity)
13. Consider MC-5 CODIFICATION-CONFIRMED extension candidate — S2204 will be FIFTEENTH-consecutive parent-with-children arc §11.2 template application; would extend the CODIFICATION-CONFIRMED milestone count 14 → 15 consecutive (conditional per S2202 Q19 + S2203 Q19 pending Chris ratification at S2299)

**S2204 open command (Chris short command):** `Continue research group 2200: Child D` or equivalent invocation.

---
session: 2203
status: closed (S2203 Group 2200 P3 Cat C Frontend↔Backend API Contract + Boundary Discipline Audit CLOSED — FOURTEENTH-consecutive playbook §11.2 20-section child-audit template application per S2202 handoff; Rigby SIGN cycle 1 SIGN-with-edits at HIGH confidence via dedicated fresh SIGN pin `pa-43bcb30dffd84ef9` retired via `session_tool.retire` updated_count=1 retired=true previously_active=true; 4 batches × 5 questions = 20 total Q with **20 folds landed pre-commit-gate**; Cycle 2 NOT required per Rigby cycle-1 HIGH confidence + all 20 folds landable; Chris "agree all" 2026-07-05 ratified 5-item close card wholesale — 20-fold SIGN cycle 1 acceptance + §20.6 POSTURE-DECISION Option (c) DEFER contract SoT enforcement design to Group 2500 API arc close with REST-native Path triad A/B/C + escape hatch commit + post-arc maintainer-decision batch meta-recommendation bundling R3/R4/R5/R6/R8/R9 + arc-cascade sequence + commit-gate approval; arc pin `pa-f7fd5016600f4513` PRESERVED through S2203 per playbook §16 arc-standard behavior; ARCHITECTURE_INDEX v79 → v80 with §1.83 registration; OPEN_ARCS Group 2200 In-progress row updated with S2203 P3 shipped; Runtime target 6 sessions on track — 4 of 6 shipped)
date: 2026-07-05
arc: Research Group 2200 (Frontend — Contract-Surface Arc) — S2203 P3 Cat C third-child audit
head_commit_before: 0ce569f6
arc_pin: pa-f7fd5016600f4513 (PRESERVED through S2203 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — TENTH formal arc pin under Research OS; retirement at S2299 close)
sign_pin: pa-43bcb30dffd84ef9 (RETIRED at S2203 SIGN cycle 1 close via `session_tool.retire` per playbook §15 SIGN-isolation discipline — updated_count=1, retired=true, previously_active=true)
---

# Session 2203 — Group 2200 Cat C — Frontend↔Backend API Contract + Boundary Discipline Audit

## What shipped

**Doc:** `docs/research/domains/frontend/2203_frontend_api_contract_boundary_discipline_audit.md` (~1600 lines post-Rigby-SIGN-20-folds; `status: draft` post-Chris-agree-all-ratification pending post-cascade `active` flip).

**Playbook §11.2 20-section child-audit template — FOURTEENTH-consecutive application** per S2202 handoff (prior applications across S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202; specific §11.2 skipped-child identification within the 14 prior sessions deferred to S2299 close if load-bearing).

**Rigby SIGN cycle 1 result: SIGN-with-edits at HIGH confidence via dedicated fresh SIGN isolation pin `pa-43bcb30dffd84ef9`** (retired at cycle close via `session_tool.retire`, updated_count=1, retired=true, previously_active=true). **4 batches × 5 questions = 20 total Q; 20 folds landed pre-commit-gate.** Cycle 2 NOT required per Rigby cycle-1 HIGH confidence + all 20 folds landable.

**20 SIGN folds landed pre-commit by batch:**

- **Batch 1 (Q1-Q5): framing + severity calibration.**
  - **Q1 STRENGTHEN** — §14 F5 drf-spectacular installed-but-partial-wired kept HIGH structural debt + intent-hedge added: "Partial foundation present; current wiring is sports-only (16 decorators), core has 0 — treat as HIGH debt unless an explicit 'sports-only' decision exists." Prevents false-confidence framing.
  - **Q2 STRENGTHEN** — §1 + §5.3 dual denominator adopted: **Coverage A (api.ts-only) = 6.85% (63/919); Coverage B (global with cockpitApi merged) = ~11.8% (115/973)**. Report both views to prevent conflation.
  - **Q3 CLEAN + micro-fold** — §14 F1 severity kept HIGH-baseline + CRITICAL-for-money-path; risk-channel wording refined to **"latent-but-active risk channel: silent auth failures + untyped contracts on critical flows"** — no current-incident-rate claim required to sustain severity.
  - **Q4 STRENGTHEN** — §14 F6 DEAD-CANDIDATE count hedged **"18 identified; expect ~18-25 pending R3 full TSX import/usage sweep"**; marked as candidate list not final inventory.
  - **Q5 STRENGTHEN** — §14 F3.5 auth-endpoint whitelist substring brittleness **LOW → MEDIUM** ("substring whitelists in auth are classic footgun that scales badly under route evolution"; OAuth callbacks, password-reset flows, hypothetical /2fa/ endpoints amplify risk).
- **Batch 2 (Q6-Q10): falsifier + coverage-math + F4 verdict.**
  - **Q6 STRENGTHEN** — §1 F4 verdict reframed **"SYSTEMIC" → "SYSTEMIC-with-surface-variance"** — per-surface table added (Betting 0/25, Workspace 0/18, Command-Center partial via platformApi, PA 5/22, cockpit 52/54, Other ~0%); all surfaces below acceptable-bar threshold (~25%); variance is real but doesn't move any surface above bar.
  - **Q7 STRENGTHEN** — §1 + §5.1 + §14 F4 cockpitApi labeled **"typed island"** (ops-surface scoped), NOT "cross-surface exception"; **"exception demonstrates path, not coverage"** wording added — cockpit is existence proof that typing is feasible, not a falsifier for SYSTEMIC untypedness of core product surfaces.
  - **Q8 STRENGTHEN** — §1 sampling sufficiency note added: 3-module pathology replication rate = "observed in all sampled non-sports modules"; SYSTEMIC claim **anchored to macro-evidence** (api.ts centralization + 919 calls + 6.85% typed rate = structural evidence at whole-file scale); 3-module sample = strong-signal corroboration, not sole proof.
  - **Q9 CLEAN + micro-fold** — §1 Denominator contract box added: **B1 typed-coverage → 63/919 api.ts-only (Coverage A) OR 115/973 global (Coverage B); B2 silent-401 → ~630/1300 gated call-sites; B3 cross-cutter → 4/94 modules**. Each rate declares unit of analysis + scope + sampling method to prevent reader conflation.
  - **Q10 STRENGTHEN** — §20.4 sampling-completeness note added covering `.js`/`.jsx` falsifier: verifier ran `Glob frontend/src/**/*.{js,jsx}` = **0 files**. Blind-spot foreclosed.
- **Batch 3 (Q11-Q15): cross-arc + POSTURE-DECISION defense.**
  - **Q11 STRENGTHEN** — §20.6 default-owner = **Group 2500 API** (concrete routing) + fallback clause added: **"or the next arc explicitly owning backend API contract design if ownership shifts"**. Preserves accountability without brittleness against post-S2299 queue reordering.
  - **Q12 STRENGTHEN** — §17.3 T7 + §20.6 Path triad language reframed **REST-native**: axis phrased as **"contract strictness + validation" (OpenAPI schema, typed clients, runtime validators, error envelopes)** rather than "envelope" alone. Path C spirit preserved.
  - **Q13 STRENGTHEN** — §17.3 T7 assigned **own T-slot ID** (distinct from S2202 T6) while marked **"joint 2500+2600"** to preserve shared ownership routing. "Pattern echoes S2202 T6 but is distinct enough (REST client contract discipline vs WS subscription discipline) to avoid conflation."
  - **Q14 STRENGTHEN** — §14 F3 ~630-call-site quantification hedged **"~630 of ~1,300 (~48% estimate, grep-based, may overcount wrappers/duplicates)"** + explicit method + hedge label. Preserves descriptive/symptomatic posture per §7.1 Group 2400 guardrail.
  - **Q15 STRENGTHEN** — §14 F6 delete-proof gate tightened: triad now (a) no imports/usages [primary], (b) no runtime route hits in recent telemetry [supporting; noisy/missing telemetry doesn't count as absence], (c) **MANDATORY explicit maintainer-intent statement**.
- **Batch 4 (Q16-Q20): anti-scope + POSTURE + verdict.**
  - **Q16 STRENGTHEN** — §15 remediation options labeled **"Options (non-authoring)"** + disclaimer added: "No code changes proposed in this doc; enforcement locus owned by Group 2500/maintainers." §19 R1/R2 language reworked to **"open maintainer gate / request decision / queue follow-on arc"** verbs — no "implement/change/refactor/enforce/wire" verbs in remediation-adjacent text.
  - **Q17 CLEAN** — §20.6 commit-strength framing matches S2202 §20.6 Q17 fold precedent: **HIGH confidence in (a) deferral action + (b) ownership routing to Group 2500 API; NOT claiming HIGH confidence on final Path A/B/C outcome.**
  - **Q18 STRENGTHEN** — §19.4 post-arc maintainer-decision batch bundling rule made non-arbitrary: **"Maintainer signoff batch = any item that deletes/renames APIs, changes auth/permission semantics, or redefines contract SoT."** R1 + R2 stay active-research with explicit rationale.
  - **Q19 CLEAN** — MC-4 codification-language framing preserved per S2202 Q19 STRENGTHEN precedent: S2203 registered as **candidate evidence 13→14 consecutive**; final codification wording CONDITIONAL pending Chris ratification at S2299 canonical summary close.
  - **Q20 verdict** — **SIGN-with-edits at HIGH confidence.** Minimum edits pre-commit-gate landed via the 20 folds above. Critical residuals: none blocking SIGN. Confidence rationale: issues were calibration + rubric-math + scope-guarding + cross-arc-handoff-ownership + REST-native axis wording, not foundational errors.

**Chris ratified 5 close-card items via "agree all" 2026-07-05:**

1. **20-fold SIGN cycle 1 acceptance** — all 20 folds landed pre-commit; status advanced `active-post-Rigby-SIGN` → `active-post-Chris-ratification` (via post-cascade `active` flip).
2. **§20.6 POSTURE-DECISION commit — Option (c) DEFER contract SoT enforcement design to Group 2500 API arc close** (default owner Group 2500 API + fallback clause "or the next arc explicitly owning backend API contract design if ownership shifts" per Q11 STRENGTHEN) with **REST-native Path triad A/B/C** (axis = "contract strictness + validation" via OpenAPI schema + typed clients + runtime validators + error envelopes) + escape hatch to S2299 preserved. HIGH confidence on committed action (deferral + Group 2500 as owner) — NOT claiming HIGH confidence on final Path A/B/C outcome. Chris D-gate at S2299 canonical summary close.
3. **Post-arc maintainer-decision batch (§19 meta-recommendation)** — bundle R3 (DEAD-CANDIDATE cleanup) + R4 (api.ts extraction) + R5 (cross-cutter doc) + R6 (fetch/axios bypass cleanup) + R8 (inline-interface consolidation) + R9 (CODEOWNERS + cockpitApi ownership) into single post-arc governance gate. R1 (Group 2500 contract-SoT rollout evidence) + R2 (Group 2400 silent-401 resolution evidence) remain CRITICAL active-research tracks. R7 (MSW integration tests) + R10 (REST↔WS message contract SoT unified proposal joint 2500+2600) also active-research.
4. **Arc-cascade sequence** — (i) commit audit doc; (ii) OPEN_ARCS §In-progress row Group 2200 updated with S2203 P3 shipped; (iii) ARCHITECTURE_INDEX v79 → v80 with §1.83 S2203 registration; (iv) 00-START-NEXT-SESSION.md overwrite with S2204 Child D Session-scoped State Management + Persistence Discipline priorities; (v) SESSION_2203 handoff at `docs/handoffs/SESSION_2203_FRONTEND_API_CONTRACT_BOUNDARY_DISCIPLINE_AUDIT.md`; (vi) 4-step docs cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
5. **Commit-gate approval** — proceed with commit + PR + arc-cascade + docs cascade in one merge sequence.

**MC-4 codification note (Chris-acknowledged):** 13 → 14 consecutive is valid as *candidate evidence*; codification language remains **conditional** pending S2299 wording / ratification per SIGN Q19 CLEAN fold (mirrors S2202 Q19 STRENGTHEN precedent).

## Central lens question — S2203 Child C slice answer

Per S2200 central lens question verbatim: *"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

**S2203 Child C slice answer:** The frontend↔backend REST API surface at HEAD `0ce569f6` is **an untyped mega-module mesh with a typed ops-island and a silent-failure default** — 93 of 94 api-modules (98.9%) live inside a single 4,194-line `frontend/src/lib/api.ts` file with **6.85% typed-response coverage locally within api.ts (Coverage A: 63/919); ~11.8% typed-coverage globally across the whole frontend API surface (Coverage B: 115/973)** — while the sole typed **island** `frontend/src/lib/cockpitApi.ts` (54 functions, 96% typed via `@/types/cockpit`) is scoped to the `/cockpit/*` ops-surface only and **demonstrates the achievable discipline path, not coverage**; auth-drift is inherited from a single global silent-401 interceptor that swallows any non-`/auth/` non-`/login` 401 across ~1,300 downstream call sites; contract source-of-truth infrastructure (drf-spectacular) is INSTALLED but wired in only 1 of ~25 Django apps (**`sports/views.py` 16 `@extend_schema` decorators** — partial foundation present; core has 0 decorators — treat as HIGH debt unless an explicit "sports-only" wiring decision exists in history); typed-schema client codegen is ABSENT from the frontend package.json; runtime response validation (zod / io-ts / valibot) is ABSENT.

## Post-arc T-slot follow-on queue (10 R-items)

Owed to S2299 xx99 canonical summary:

**CRITICAL tier (active-research):**
- R1 — [Group 2500 API arc] Whole-platform contract SoT rollout evidence (extend sports/views.py 16-decorator drf-spectacular wiring pattern platform-wide; evaluate OpenAPI 3.0 emission at build-time; evaluate openapi-typescript/orval consumption in frontend; evaluate 93 api-module retrofit; evaluate zod runtime validation at api.ts boundary)
- R2 — [Group 2400 Auth arc] Silent-401 resolution evidence (three option-space paths: uniform IsAuthenticated + client-side auth-gate + observable-error surfacing; uniform AllowAny for reads + IsAuthenticated for writes + client-side auth-check-on-write; per-endpoint permission registry)

**HIGH tier (post-arc maintainer-decision batch — bundled per Q18 STRENGTHEN):**
- R3 — 18-25 DEAD-CANDIDATE api-module maintainer signoff + delete-proof + cleanup PR
- R4 — Post-arc api.ts extraction into domain-scoped api-*.ts files
- R5 — Cross-cutter documentation (docs/topics/api-contract.md)
- R6 — Component-level fetch/axios bypass cleanup (~9 sites wrapped into api-modules)

**MEDIUM tier:**
- R7 — MSW integration tests for top-10 highest-traffic endpoints (active-research; not bundled)
- R8 — Consolidate inline `interface *Response` declarations across pages/ + components/ into shared `frontend/src/types/*.ts` (post-R1 rollout)
- R9 — cockpitApi ownership documentation + CODEOWNERS entry for `frontend/src/lib/*.ts`
- R10 — Cross-arc joint 2500+2600 T7 — REST↔WS message contract SoT unified proposal (active-research)

## Cross-arc coordination flags (preserved for S2299)

- **Group 2500 API** — Contract SoT design ownership per §7.1 Child C → Group 2500 guardrail; **T7 joint REST/WS message contract strictness gets own T-slot ID** distinct from S2202 T6 (Q13 STRENGTHEN).
- **Group 2400 Auth** — Silent-401 pattern FE-symptom + Group 2400 owns session-model resolution; blast radius ~630 call-sites (grep-estimate, hedged for wrapper duplicates per Q14 STRENGTHEN).
- **Group 2600 PA** — assistantApi partial-typing pattern + `/pa/chat/*` WS/polling consolidation joint 2500+2600 extends S2202 T6.
- **Group 1700 Observability** — cockpitApi typed island + platformApi observability instrumentation — envelope enforcement locus decision joins REST-side.
- **Group 1300 Memory + 1600 Content + 1800 HumanAttention** — render-authority split per parent §7.1; cross-cutters `humanApi` + `contentApi` share render surface across these domains.

## Arc pin discipline

- **Arc pin `pa-f7fd5016600f4513` PRESERVED through S2203** per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails. TENTH formal arc pin under Research OS; retirement at S2299 close.
- **SIGN pin `pa-43bcb30dffd84ef9` RETIRED** at S2203 SIGN cycle 1 close per playbook §15 SIGN-isolation discipline via `session_tool.retire` (updated_count=1, retired=true, previously_active=true).
- **`tools/pa_local.sh:225` already dispatches into `pa-f7fd5016600f4513`** — no rotation needed at S2204 open.

## Meta-methodology milestones

- **MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails** — S2203 registers candidate evidence for template-application count extension **13 → 14 consecutive**; codification framing CONDITIONAL pending Chris ratification / final wording at S2299 canonical summary close per Q19 CLEAN fold (mirrors S2202 Q19 STRENGTHEN precedent).
- **MC-5 §11.2 template-application** — FOURTEENTH-consecutive application observation; extends baseline for codification-confirmed extension at S2299.

## Runtime target status

Group 2200 runtime target 6 sessions on track:
- ✅ S2200 parent scoping (shipped 2026-07-05)
- ✅ S2201 P1 Child A Routes + Pages + Layouts + Component Patterns (shipped 2026-07-05)
- ✅ S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope (shipped 2026-07-05)
- ✅ **S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline (shipped this session)**
- → S2204 P4 Child D Session-scoped State Management + Persistence Discipline (next)
- → S2299 xx99 canonical summary

**4 of 6 shipped.**

## Next session priority

**S2204 P4 Child D Session-scoped State Management + Persistence Discipline** per parent §5.4. Load-bearing inputs per parent §5 Child D block:

- All `localStorage` / `sessionStorage` / cookie / IndexedDB / Zustand-context-store touchpoints in `frontend/src/`
- 7 Zustand stores (assistantContextStore, authStore, bodyStore, navigationStore, paStore, unifiedStore, workspaceStore) per S2201 §5 baseline
- PA workspace-context resolver per topics/frontend.md §PA Integration
- Fire-and-forget page-telemetry `usePageTracking()` Redis counters (per S2200 §5 Q6 CLEAN fold — routed to Child D)
- S1505 §14.10 zero-client-side-state-persistence baseline
- S2201 §5 baseline + §14 F5 findings on legacy state-adjacent surfaces
- S2202 §17 T7 WS/polling consolidation flag (state-adjacent)
- S2203 §14 F3 silent-401 + `authStore` token-persistence adjacency + Session 968 X-UI-Scope request-log persistence adjacency

Per-surface reporting constraint (workspace / betting / command-center / PA / other) + timebox + sampling rule apply per S2200 §5. Child D T0/Gate = persistent-state-surface inventory + declared-vs-accidental discipline rate + key-namespace collision audit + PA workspace-context resolver persistence audit + cross-surface state coupling map + POSTURE-DECISION evidence plan §20.6 owed to xx99 on whether per-surface persistence discipline should be introduced as frontend convention or handled at backend/PA layer.

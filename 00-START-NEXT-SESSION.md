# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2200 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**ACTIVE ARC PIN.** Group 2200 arc pin `pa-f7fd5016600f4513` PRESERVED through S2204 close per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails. TENTH formal arc pin under Research OS. S2204 SIGN cycle 1 pin `pa-62c03c4844454e99` retired at cycle close (updated_count=6, retired=true, previously_active=true). `tools/pa_local.sh:234` already dispatches into `pa-f7fd5016600f4513` — no rotation needed at S2299 open. **Arc pin retirement scheduled at S2299 xx99 close** per playbook §16 arc-close discipline.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2200 S2204 CHILD D CLOSED AT S2204; NEXT = S2299 xx99 CANONICAL SUMMARY

**Group 2200 Frontend (Contract-Surface Arc): S2204 Child D Session-scoped State Management + Persistence Discipline Audit CLOSED 2026-07-05.** Chris "agree all" 2026-07-05 ratified all 5 close-card items wholesale (20-fold SIGN cycle 1 acceptance + §20.6 POSTURE-DECISION triad Path A DECLARE naming convention + Path B EXTEND version+migrate authStore+navigationStore HIGH + Path C REJECTED framework authoring + Path D1 workspace-persistence-policy Group 2600 PA MED + Path D2 focused-entity-persistence Group 2600 PA MED + escape hatch preserved + §19 R4/R5/R6/R7 maintainer-decision batch bundling + R1/R2/R3/R8/R9/R10 active-research/post-arc T-slot tracks + arc-cascade sequence + commit-gate approval + MC-4 14→15 CONDITIONAL pending S2299 ratification). FIFTEENTH-consecutive application of playbook §11.2 20-section child-audit template. Candidate evidence for MC-4 codification extension 14→15 consecutive — codification framing CONDITIONAL pending Chris ratification at S2299 canonical summary close per Q19 CLEAN fold mirroring S2202 Q19 + S2203 Q19 precedent.

- **Arc pin ACTIVE:** `pa-f7fd5016600f4513` (TENTH formal arc pin; preserved across all sessions per playbook §16 arc-standard behavior; retirement at S2299 close).
- **Arc progress:** S2200 parent scoping (shipped) → S2201 P1 Child A Routes+Pages+Layouts+Component Patterns (shipped) → S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope (shipped) → S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline (shipped) → S2204 P4 Child D Session-scoped State Management + Persistence Discipline (shipped this session) → **S2299 xx99 Canonical Summary (next)**. Runtime target 6 sessions on track — **5 of 6 shipped**.
- **Next session:** S2299 xx99 canonical summary for Group 2200 Frontend arc per playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology TENTH application.

## READ THIS THIRD — S2204 SHIP STATE

**Doc:** `docs/research/domains/frontend/2204_frontend_session_state_persistence_discipline_audit.md` (~1650 lines post-Rigby-SIGN-20-folds; `status: active` post-Chris-agree-all-ratification pending post-cascade final `active` flip).

**Playbook §11.2 20-section child-audit template — FIFTEENTH-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201+S2202+S2203.

**SIGN cycle 1 result:** SIGN-with-edits at HIGH confidence via dedicated fresh SIGN pin `pa-62c03c4844454e99` (retired at cycle close via `session_tool.retire`, updated_count=6, retired=true, previously_active=true). 4 batches × 5 questions = **20 total Q; 20 folds landed pre-commit-gate.** Cycle 2 NOT required.

**20 folds by batch:**
- **Batch 1 framing + severity:** Q1 CLEAN F2 verdict + Q2 STRENGTHEN F5 workspaceStore MED-HIGH-borderline-HIGH-conditional-Group-2600 + Q3 CLEAN 12+3=15 reconciliation + Q4 STRENGTHEN 6-DECLARED/6-ACCIDENTAL 4-criteria rubric formalized + Q5 STRENGTHEN Zustand ^4.4.0 verifier-loop resolves U1.
- **Batch 2 falsifier + per-surface rollup:** Q6 STRENGTHEN "14/15 outside /betting" denominator + Q7 STRENGTHEN "key-level incidence by surface" language cross-surface averaging FORBIDDEN + Q8 REJECT STABLE+DEEP→WORKING+MODERATE downgrade defer to xx99 rollup + Q9 STRENGTHEN dependency-scan verification-scope statement + Q10 CLEAN sampling-waived-per-full-registry-fit.
- **Batch 3 cross-arc + POSTURE:** Q11 STRENGTHEN R1 two-sided framing FE-symptom-vs-BE-model-contract mirror S2203 §14 F3 + Q12 STRENGTHEN R2-vs-R3 dependency graph justification + Q13 CLEAN F5 severity hedge + Q14 STRENGTHEN §16.1 unchanged-at-HEAD-8fbf17eb re-verification + Q15 STRENGTHEN R5 depends-on-R1-logout-semantics tag.
- **Batch 4 anti-scope + verdict:** Q16 STRENGTHEN R4 anti-scope guardrail "registry not framework not wrapper API" + Q17 STRENGTHEN Path D sub-split D1 workspace-persistence + D2 focused-entity + Q18 CLEAN R4/R5/R6/R7 bundling + Q19 CLEAN MC-4 14→15 codification-conditional + Q20 SIGN-with-edits verdict HIGH confidence + Cycle 2 NOT required.

**Chris ratified 5 close-card items via "agree all" 2026-07-05:**
1. 20-fold SIGN cycle 1 acceptance
2. §20.6 POSTURE-DECISION triad Path A DECLARE naming convention + Path B EXTEND version+migrate HIGH + Path C REJECTED framework authoring + Path D1/D2 workspace-context resolver + focused-entity persistence Group 2600 PA-owned MED + escape hatch preserved
3. §19 meta-recommendation post-arc maintainer-decision batch bundling R4/R5/R6/R7 (R5 tagged depends-on-R1); R1/R2/R3/R8/R9/R10 active-research/post-arc T-slot tracks
4. Arc-cascade sequence (OPEN_ARCS + ARCHITECTURE_INDEX v80→v81 §1.84 + 00-START-NEXT + SESSION_2204 handoff + 4-step docs cascade + build_docs_provenance)
5. Commit-gate approval

**Central lens question (§lens verbatim Chris-locked at S2200):**

*"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

**S2204 Child D slice answer:** Structurally INTENTIONAL at Zustand-persist boundary (3 of 7 stores persist; paStore uniquely has v3+migrate) + structurally ACCRETED at direct-localStorage-caller boundary (12 keys scattered across 9 files with 6 DECLARED / 6 ACCIDENTAL per formalized 4-criteria rubric C1 constant / C2 typed accessor / C3 graceful fallback / C4 template disciplined). **15 total persistent surfaces** (3 Zustand persist + 12 direct localStorage) + 0 sessionStorage + 0 IndexedDB + 1 cookie read (paStore.ts:241 sessionid) + 1 in-memory ring buffer (Session 968 X-UI-Scope, dev-only, 200-entry cap). F5 F2 hazard: workspaceStore.activeWorkspace in-memory-only creates PA-context-loss on refresh across 144 consumer sites (12 PA-side) — severity MED-HIGH (borderline HIGH conditional on Group 2600 PA correctness disposition). **F2 hypothesis test verdict SURFACE-LOCAL + DOMAIN-SPECIFIC HYBRID** — S1505 §14.10 CONFIRMED for /betting slice (0 of 15 persisted keys inside betting; 14 of 15 outside); does NOT generalize whole-frontend.

## READ THIS FOURTH — S2299 xx99 CANONICAL SUMMARY SCOPE

Per playbook §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology TENTH application (after S1399 first + S1499 second + S1599 third + S1699 fourth + S1799 fifth + S1899 sixth + S1999 seventh + S2099 eighth + S2199 ninth).

**S2299 load-bearing input:**
- S2200 parent scoping (arc frame + central lens + 4-children shape)
- S2201 Child A audit (routes + pages + layouts + components — 61-route surface + god-components + CODEOWNERS gap + STABLE+DEEP→WORKING+MEDIUM downgrade + Child E fold-in)
- S2202 Child B audit (WebSocket consumer surface + `ui.render_hint` envelope — 125 routes + 0/40 envelope conformance + F1 MOCK-DATA multi-surface + F2 SYSTEMIC-with-variance + Option (c) DEFER envelope enforcement to Group 1700)
- S2203 Child C audit (API contract SoT + boundary discipline — 93 api-modules + 6.85% typed + silent-401 SYSTEMIC + F1 drf-spectacular partial-wiring + Option (c) DEFER contract SoT to Group 2500)
- S2204 Child D audit (session-scoped state + persistence discipline — 15 total persistent surfaces + F2 SURFACE-LOCAL+DOMAIN-SPECIFIC HYBRID + Path A registry + Path B version+migrate + Path D1/D2 deferred Group 2600)

**S2299 load-bearing output (per playbook §11.3 12-section template):**
- **§1** Executive Summary (500-800 words on what arc shipped + domain understanding change + open items)
- **§2** What This Arc Answered (per-child rollup: canonical questions each child answered)
- **§3** Consolidated Domain Shape (single map / diagram — reader's mental model of frontend as contract surface)
- **§4** Cross-Cutting Patterns (themes visible across multiple children — no-typed-contracts + silent-failure defaults + inline-string-persistence + no-CODEOWNERS + god-components)
- **§5** Resolved Contradictions (where children disagreed; canonical verdict)
- **§6** Unresolved Unknowns (S2202 partial coverage + S2203 R2 blast radius method + S2204 Path D1/D2 Group 2600 disposition)
- **§7** Anchor-Update Recommendations (PLATFORM_INVENTORY §Frontend augmentation: state persistence row + WebSocket row + API contract row; PLATFORM_WHAT_IT_IS.md frontend section update; ARCHITECTURE_INDEX v81→v82 + §3 domain map row 18 STABLE+DEEP → WORKING+MODERATE downgrade; topics/frontend.md refresh from stale-warned to fresh)
- **§8** Follow-On Research Queue (Ranked T-slot queue: R-items from S2201 + S2202 + S2203 + S2204 into single ordered queue; maintainer-decision batches distinguished from active-research tracks; Chris D-verdict on Path selections)
- **§9** Cross-Links to Delegated Arcs (Group 2400 Auth for R1 session lifecycle + R6 logout hygiene; Group 2500 API for R3 canonical User + workspace_id contract + contract SoT rollout; Group 2600 PA for R2 workspace-context resolver + Path D1/D2 + T6 WS/polling consolidation; Group 1700 Observability for envelope enforcement locus + Session 968 X-UI-Scope; Group 1300 Memory + 1600 Content + 1800 HumanAttention render-authority split preserved; Group 2300 Mobile excluded per §7 anti-scope)
- **§10** What This Research Taught Us About How to Do Research (TENTH meta-methodology application per S1399 established discipline; 5 subsections: 10.1 what worked / 10.2 codify to playbook v3 / 10.3 anti-patterns to avoid / 10.4 suggestions for playbook / 10.5 suggestions for future canonical summaries; verifier-loop-catching-sub-agent-errors from S2204 as pattern candidate)
- **§11** Arc Change Log (which child, which session, which Rigby verdict, which fold edits)
- **§12** Appendix (every child's file path, evidence provenance, verifier-loop history)

**S2299 runtime target: 1 session** per canonical-summary shape.

**MC-4 CODIFICATION-CONFIRMED extension resolution at S2299 close:**
- S2204 candidate evidence for template-application count extension 14 → 15 consecutive (§11.2 20-section child-audit template application) — CONDITIONAL pending Chris ratification at S2299 close-card per Q19 CLEAN fold + S2202 Q19 + S2203 Q19 precedent
- Group 2200 is FOURTH-consecutive parent-with-4-children arc (per §4 table arithmetic); Group 2200 close extends MC-4 3 → 4 at Group 2200 close per D6 arithmetic correction — S2199 Q3 STRENGTHEN dial-back resolution ("contingent on 5th arc or materially different stress condition") DOES NOT resolve at Group 2200 close; requires Group 2300+ arc as 5th confirming arc
- MC-4 4th-arc-confirmation Chris-ratified wording at S2299 close-card TBD (pending Chris decision on codification framing)

**Arc pin retirement at S2299 close:** `pa-f7fd5016600f4513` retired via `session_tool.retire` per playbook §16 arc-close discipline. TENTH formal arc-pin retirement in Research OS (after S1399 + S1499 + S1599 + S1699 + S1799 + S1899 + S1999 + S2099 + S2199 prior).

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2204 arc-close cascade residuals

Per Chris "agree all" ratification at S2204 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.

### S2199 post-arc T-slot execution queue (unchanged carry into S2299)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2299 xx99.

### S2200/S2201/S2202/S2203/S2204 arc residuals owed to S2299 xx99

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
- S2203 §20.6 POSTURE-DECISION Option (c) DEFER contract SoT enforcement design to Group 2500 API arc close + REST-native Path triad A/B/C + escape hatch → xx99 §7 anchor-update batch + §9 cross-links section
- S2203 §19 meta-recommendation post-arc maintainer-decision batch bundling R3/R4/R5/R6/R8/R9 + R1/R2/R7/R10 active-research tracks → xx99 §8 follow-on research queue
- S2203 F1 drf-spectacular partial-wiring PLATFORM_INVENTORY augmentation candidate (add API-contract row: 93 modules + 919 calls + 6.85% typed api.ts-only / 11.8% global + drf-spectacular partial-wiring) → xx99 §7 anchor-update batch
- S2203 F5 DEAD-CANDIDATE api-module INTENT-NEUTRAL pattern (18 verifier-confirmed; ~18-25 pending R3 sweep) → xx99 §8 T-slot queue for maintainer-decision batch execution
- S2203 cross-arc flags to Group 2500 API (contract SoT design ownership + T7 own T-slot joint 2500+2600) + Group 2400 Auth (silent-401 resolution + ~630 call-site blast radius grep-estimate) + Group 2600 PA + Group 1700 Observability + Group 1300 Memory + 1600 Content + 1800 HumanAttention render-authority split → xx99 §9 cross-links section
- **S2204 §20.6 POSTURE-DECISION triad Path A DECLARE naming convention + Path B EXTEND version+migrate authStore+navigationStore HIGH + Path D1/D2 workspace-context + focused-entity persistence Group 2600 PA-owned MED + Path C REJECTED framework authoring + escape hatch → xx99 §7 anchor-update batch + §9 cross-links section**
- **S2204 §19 meta-recommendation post-arc maintainer-decision batch bundling R4/R5/R6/R7 (R5 depends on R1 logout semantics) + R1/R2/R3/R8/R9/R10 active-research/post-arc T-slot tracks → xx99 §8 follow-on research queue**
- **S2204 F1 15-total-persistent-surfaces observation** (12 direct localStorage + 3 Zustand persist + 0 sessionStorage + 0 IndexedDB + 1 cookie + 1 in-memory ring buffer dev-only) PLATFORM_INVENTORY augmentation candidate → xx99 §7 anchor-update batch
- **S2204 F5 naming-convention drift** (6 kebab + 3 snake + 3 camel across 12 direct keys) → xx99 §8 T-slot queue for maintainer-decision batch execution
- **S2204 cross-arc flags to Group 2400 Auth (R1 session lifecycle + cleanup contract) + Group 2500 API (R3 canonical User + workspace_id contract) + Group 2600 PA (R2 workspace-context resolver + Path D1/D2) + Group 1700 Observability (Session 968 X-UI-Scope) + Group 1300 Memory + 1600 Content + 1800 HumanAttention render-authority split preserved → xx99 §9 cross-links section**
- **S2204 §14.4 verifier-loop corrections** (Explore 5 navigationStore not-DEAD + unifiedStore CC-consumer correction + parent-memo 15-direct-key off-by-3 correction) — process improvement observation for xx99 §10 meta-methodology retrospective as sub-agent-claim-triage-before-draft pattern

### Group 2200 residual queue expected at S2299 close

- 4 child audits shipped: S2201 Child A + S2202 Child B + S2203 Child C + **S2204 Child D**
- xx99 canonical summary (S2299) with 12-section playbook §11.3 template + §10 meta-methodology TENTH application
- MC-4 4th-arc confirmation extension (dial-back resolution deferred to Group 2300+)
- MC-5 §11.2 template-application codification wording per S2202 Q19 + S2203 Q19 + **S2204 Q19** — CONDITIONAL pending Chris ratification at S2299
- Post-arc T-slot queue owed to xx99 from all 4 child audits

## SESSION READY CHECK (before opening S2299 xx99 canonical summary)

Before drafting the S2299 xx99 canonical summary:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (arc pin `pa-f7fd5016600f4513` already active in `tools/pa_local.sh:234`; no rotation needed at S2299 open; retirement scheduled at S2299 close)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.3 12-section canonical-summary template + §11.3 §10 meta-methodology TENTH application + prior 9 xx99 canonical summaries (S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199) for exemplar shape
3. Read `docs/research/domains/frontend/2200_frontend_domain_scoping.md` (parent scoping) + `2201_...` + `2202_...` + `2203_...` + `2204_...` (all 4 children) for load-bearing input
4. Read `docs/PLATFORM_INVENTORY.md` §Frontend + `docs/topics/frontend.md` + `docs/research/platform_architecture_inventory.md` row 18 for anchor-update baselines
5. Plan §7 anchor-update batch: PLATFORM_INVENTORY §Frontend augmentation (state persistence row + WebSocket row + API contract row); PLATFORM_WHAT_IT_IS.md frontend section update; ARCHITECTURE_INDEX v81→v82 + §3 domain map row 18 STABLE+DEEP → WORKING+MODERATE downgrade Chris-ratified via S2201 close but deferred; topics/frontend.md refresh from stale-warned to fresh
6. Plan §8 T-slot queue merge: R-items from S2201 (9 items) + S2202 (9 items) + S2203 (10 items) + S2204 (10 items) into unified ranked queue; maintainer-decision batches distinguished from active-research tracks
7. Plan §9 cross-links: Group 2400 Auth + Group 2500 API + Group 2600 PA + Group 1700 Observability + Group 1300/1600/1800 render-authority split + Group 2300 Mobile excluded per §7 anti-scope
8. Plan §10 meta-methodology retrospective (TENTH application per S1399 discipline; 5 subsections): what worked (SIGN cycle 1 4-batch × 5-Q cadence + per-surface reporting + falsifier framework); what to codify (verifier-loop-catches-sub-agent-errors S2204 pattern; per-key rubric formalization); anti-patterns to avoid; suggestions for playbook v3; suggestions for future canonical summaries
9. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — canonical summary shape is smaller than child audits; may fit single-batch 4-question cadence per S2099/S2199 precedent
10. Plan arc pin retirement sequence: `session_tool.retire` for `pa-f7fd5016600f4513` at S2299 close post-Chris-ratification per playbook §16 arc-close discipline; TENTH formal arc-pin retirement
11. Consider MC-4 CODIFICATION-CONFIRMED extension resolution — S2204 registers candidate evidence 14→15 CONDITIONAL; Chris ratifies wording at S2299 close-card
12. Consider MC-5 codification note — 4 consecutive parent-with-4-children arc close (Groups 1900 + 2000+ + 2100 + Group 2200) EXTENDS consecutive-count 3→4; MC-5 dial-back resolution requires Group 2300+ arc as 5th confirming

**S2299 open command (Chris short command):** `Continue research group 2200: xx99 canonical summary` or `Close research group 2200` or equivalent invocation.

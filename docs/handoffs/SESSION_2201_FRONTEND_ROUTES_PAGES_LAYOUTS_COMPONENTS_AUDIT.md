---
session: 2201
status: closed (S2201 Group 2200 P1 Cat A Routes + Pages + Layouts + Component Patterns Audit CLOSED — TWELFTH-consecutive playbook §11.2 20-section child-audit template application per S2199 handoff; Rigby SIGN cycle 1 SIGN-with-edits at HIGH confidence via dedicated fresh SIGN pin `pa-8d60e999e01c40e4` retired via `session_tool.retire` updated_count=5 retired=true previously_active=true; 4 batches × 5 questions = 20 total Q with **19 folds landed pre-commit-gate**; Cycle 2 NOT required per Rigby cycle-1 HIGH confidence + all 19 folds landable; Chris "agree all" 2026-07-05 ratified 5-item close card wholesale — 19-fold SIGN cycle 1 acceptance + §20.6 POSTURE-DECISION S1273 32-domain row 18 STABLE+DEEP → WORKING+MEDIUM commit + Child E path (b) fold-into-S2299-xx99 + graduate-as-post-arc-T-slot + arc-cascade sequence + commit-gate approval; arc pin `pa-f7fd5016600f4513` PRESERVED through S2201 per playbook §16 arc-standard behavior; ARCHITECTURE_INDEX v77 → v78 with §1.81 registration; OPEN_ARCS Group 2200 In-progress row updated with S2201 P1 shipped; Runtime target 6 sessions on track — 2 of 6 shipped)
date: 2026-07-05
arc: Research Group 2200 (Frontend — Contract-Surface Arc) — S2201 P1 Cat A first-child audit
head_commit_before: 04ee0964
arc_pin: pa-f7fd5016600f4513 (PRESERVED through S2201 per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails — TENTH formal arc pin under Research OS; retirement at S2299 close)
sign_pin: pa-8d60e999e01c40e4 (RETIRED at S2201 SIGN cycle 1 close via `session_tool.retire` per playbook §15 SIGN-isolation discipline — updated_count=5, retired=true, previously_active=true)
---

# Session 2201 — Group 2200 Cat A — Routes + Pages + Layouts + Component Patterns Audit

## What shipped

**Doc:** `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` (~730 lines post-fold; `status: active` post-Chris-agree-all-ratification).

**Playbook §11.2 20-section child-audit template — TWELFTH-consecutive application** per S2199 handoff (prior applications across S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104; specific §11.2 skipped-child identification within the 12 prior sessions deferred to S2299 close if load-bearing).

**Rigby SIGN cycle 1 result: SIGN-with-edits at HIGH confidence via dedicated fresh SIGN isolation pin `pa-8d60e999e01c40e4`** (retired at cycle close via `session_tool.retire`, updated_count=5, retired=true, previously_active=true). **4 batches × 5 questions = 20 total Q; 19 folds landed pre-commit-gate.** Cycle 2 NOT required per Rigby cycle-1 HIGH confidence + all 19 folds landable.

**19 SIGN folds landed pre-commit by batch:**

- **Batch 1 (Q1-Q5): framing + severity calibration.**
  - **Q1 CLEAN with micro-fold** — §14.1 F1 route-count delta (59 counted vs PLATFORM_INVENTORY 61) reclassified `observation` (inventory semantics delta), NOT `drift`.
  - **Q2 STRENGTHEN** — §15.2 F2 god-component severity tightened: severity scales by blast radius + churn + defect history, not by LOC alone. HIGH baseline; CRITICAL for CommandCenterPage + BettingPage.
  - **Q3 STRENGTHEN** — §15.1 F3 zero-test-coverage downgraded CRITICAL → HIGH baseline + CRITICAL for payments / auth / billing / betting / ledger-like surfaces. Single-operator solo-build caveat added.
  - **Q4 STRENGTHEN** — §18.1 F4 CODEOWNERS-absent downgraded CRITICAL → HIGH with single-operator caveat.
  - **Q5 CLEAN with micro-fold** — §14.2 F5 legacy sub-tab enum reclassified `legacy_compatibility_debt`, NOT `drift`.
- **Batch 2 (Q6-Q10): 4-falsifier + criteria scoring.**
  - **Q6 STRENGTHEN** — §1 F1 composite %-rate ("~65% non-betting violation rate") replaced with per-axis rubric (denominators independent: test files vs pages vs api-modules); labeled "violation-index" not "violation rate."
  - **Q7 STRENGTHEN** — §1 F2 tagged **PENDING-CHILD-B-CONFIRMATION** with explicit Child A vs Child B scope statement.
  - **Q8 STRENGTHEN** — §1 F4 SYSTEMIC verdict hedged with "no evidence found in sampled surfaces" language; sampling scope acknowledged.
  - **Q9 FOLD** — §1 Criterion 1 UNMET → **PARTIAL** (route ownership map exists in App.tsx; what is UNMET is the declared durable contract source-of-truth).
  - **Q10 FOLD** — §1 Criterion 5 UNMET → **PARTIAL** (6 of 38 pages god-components; 32 below threshold — criterion violated in aggregate but not uniform failure).
- **Batch 3 (Q11-Q15): Child E + cross-arc coordination.**
  - **Q11 STRENGTHEN** — §15.2 surface attribution reframed: surface = top-level product area; 3 Command-Center pages counted as multiple loci within one surface, not 3 separate surfaces. Trigger MET across 4 top-level product surfaces (Agents/AI + Command-Center + Betting + Content-Studio).
  - **Q12 CLEAN** — §15.2 workspace tab god-components labeled "intra-route tab components" as supplement not trigger-critical; Child E trigger met on page-level alone.
  - **Q13 STRENGTHEN** — §15.5 silent-401 severity reframed: HIGH at frontend-symptom scope; systemic-severity classification pending Group 2400 Auth spec. Language softened from "systemic default" to "frontend default behavior + cross-arc dependency."
  - **Q14 STRENGTHEN** — no new §14 drift entry for API types; dependency note added inline; Child C S2203 owns the full audit.
  - **Q15 FOLD** — §17.2 PA-adjacent overlap reframed from DIFFERENT-CONCERNS to **PARTIAL-DUPLICATE / intentional multi-locus** with Group 2600 PA consolidation-decision handoff.
- **Batch 4 (Q16-Q20): anti-scope + posture + verdict.**
  - **Q16 STRENGTHEN** — §14.5 GlobalPADock recommendation reframed as option-space (route metadata / layout-level feature flag / centralized visibility policy); concrete PA implementation deferred to Group 2600.
  - **Q17 FOLD** — §20.6 POSTURE-DECISION committed to single recommendation: **WORKING + MEDIUM** (route + layout STABLE; contract surface blocks whole-frontend STABLE; PARTIAL + LIGHT deemed too pessimistic).
  - **Q18 STRENGTHEN** — §19 R1/R2 ordering: R2 leads execution sequence; R1 parallel gating safety track. Deep refactors deferred until minimal test harness exists.
  - **Q19 CLEAN with micro-fold** — §14.6 betting-tab-count doc drift labeled "handoff note, not core audit finding"; tracked by doc-cascade + verify_doc_claims discipline.
  - **Q20 verdict** — **SIGN-with-edits at HIGH confidence.** Minimum edits pre-commit-gate landed. Critical residuals: none blocking SIGN. Confidence rationale: issues were calibration + rubric-math + scope-guarding, not foundational errors.

**Chris ratified 5 close-card items via "agree all" 2026-07-05:**

1. **19-fold SIGN cycle 1 acceptance** — all 19 folds landed pre-commit; status advanced `active-post-Rigby-SIGN` → `active-post-Chris-ratification`.
2. **§20.6 POSTURE-DECISION commit** — DOWNGRADE S1273 32-domain row 18 Frontend/Workspace UI from **STABLE+DEEP → WORKING+MEDIUM** at S2299 anchor edit. HIGH confidence (multi-axis corroboration from 6 Explore agents + 4-falsifier SYSTEMIC + Rigby SIGN HIGH).
3. **Child E spin-out decision** — path (b) **fold Child E scoping + trigger evidence into S2299 xx99 canonical summary + graduate as post-arc T-slot**. Preserves Group 2200 arc runtime target 6 sessions + preserves §7 anti-scope discipline (subdivision execution stays post-arc, no S2205 spin-out).
4. **Arc-cascade sequence** — (i) commit audit doc; (ii) OPEN_ARCS §In-progress row Group 2200 updated with S2201 P1 shipped; (iii) ARCHITECTURE_INDEX v77 → v78 with §1.81 S2201 registration + §8 timeline S2201 row; (iv) 00-START-NEXT-SESSION.md overwrite with S2202 Child B WebSocket + envelope priorities; (v) SESSION_2201 handoff at `docs/handoffs/SESSION_2201_FRONTEND_ROUTES_PAGES_LAYOUTS_COMPONENTS_AUDIT.md`; (vi) 4-step docs cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
5. **Commit-gate approval** — proceed with commit + PR + arc-cascade + docs cascade in one merge sequence.

## Central lens question — S2201 Child A slice answer

Per S2200 central lens question verbatim: *"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

**S2201 Child A slice answer:** The frontend at HEAD `04ee0964` is **structurally healthy at the route + auth-wrapper + layout boundary** (single `ProtectedRoute` wrapper, single `Layout.tsx`, clean public/private split, deliberate cockpit consolidation across S971b/S1035/S1078/S1083/S1240) but **structurally under-specified at the page-component + consumer-contract boundary** — no route-ownership map exists (until this audit's §3 extracted the 59-row registry as a durable artifact for the first time), no page ↔ route consumer contract is declared, and page-component complexity has generalized into 6 confirmed god-components >1,500 LOC across 4 top-level product surfaces.

## 5 headline findings

- **F1 — Route inventory delta.** Audit counts 59 `<Route>` entries in App.tsx:64-149; PLATFORM_INVENTORY §Frontend row (2026-07-02) claims 61. Delta hypothesis: inventory-generator semantics for "route" differ from Child A's distinct `path=` counter (may include nested/parent Route wrappers or `Navigate` element instances). **Class: `observation` — inventory semantics delta, NOT `drift`** (Rigby SIGN cycle 1 Q1 CLEAN with micro-fold). Reconcile at xx99. Severity: LOW.

- **F2 — God-component pathology generalizes to 6 pages >1,500 LOC across 4 top-level product surfaces.** AgentsPage 4,695 LOC (Agents/AI), IntelligencePage 3,546 LOC (Command-Center), BettingPage 3,023 LOC (Betting; S1505 baseline), CommandCenterPage 2,551 LOC (Command-Center), VideoStudioPage 1,930 LOC (Content-Studio), StockIntelligencePage 1,575 LOC (Command-Center). Additional 3 workspace tabs >2,500 LOC (InitiativesTab 3,277 + ContentStudioTab 3,167 + OrchestrationTab 2,985) as intra-route tab components supplement per Q12 CLEAN. **Child E spin-out trigger MET on page-level alone** per S2200 §5 Q4 STRENGTHEN threshold (≥3 god-components across ≥2 top-level product surfaces). Severity: **HIGH baseline; CRITICAL for CommandCenterPage + BettingPage** where blast-radius + churn + high-coupling profile amplifies risk.

- **F3 — Zero test coverage across `frontend/src/pages/**`.** 0 `*.test.tsx` files. **Severity: HIGH baseline; CRITICAL for payments / auth / billing / betting / ledger-like flows** (BillingPage, BettingPage, `/portfolio`, `/wager*` endpoints, `/api/v1/odds/bankroll*`) per Q3 STRENGTHEN — CRITICAL platform-wide over-severe for single-operator solo-build context.

- **F4 — CODEOWNERS file absent + 22/38 pages lack session-annotation ownership trail.** No repo-root `CODEOWNERS`, no `.github/CODEOWNERS`. **Severity: HIGH with single-operator caveat** (Rigby SIGN cycle 1 Q4 STRENGTHEN — becomes CRITICAL the moment a second contributor exists; today it is future-scale hardening debt rather than active governance failure).

- **F5 — Legacy sub-tab enum + `legacyTabMapping` object are load-bearing backward-compat surface.** 19 legacy sub-tab values in `WorkspaceTab` type + 25 mappings in `legacyTabMapping` at WorkspacePageNew.tsx:159-196 are RISKY to delete (all still map to active primary+sub routes via URL auto-redirect at WorkspacePageNew.tsx:791-816). `normalizeWorkspaceTab()` NOT FOUND (superseded, though parent scoping §5 Child A referenced it). **Class: `legacy_compatibility_debt`** — not `drift`; the surface works as intended, but carries maintenance burden + hidden coupling + future migration hazard. Severity: MED.

## 4-falsifier verdict SYSTEMIC (with sampling caveat)

Per S2200 §2.4 four-falsifier framing on inherited S1505 §14 findings:

- **F1 sports-outlier test:** **FAILS.** Per-axis rubric (Q6 STRENGTHEN fold — composite %-rate replaced): test coverage = 0% of `frontend/src/pages/**` files carry `*.test.tsx`; god-components = 6 of 38 pages ≥1,500 LOC (16%); state persistence = 4 of ~80 page-adjacent surfaces use localStorage/sessionStorage (~5%); typed API contracts = 0 of 93 api-module definitions carry exported TS types (0%). Fails on 4 of 4 sampled axes.
- **F2 surface-local test:** **PENDING-CHILD-B-CONFIRMATION** (Q7 STRENGTHEN). Child A page-level evidence: non-sports pages (CommandCenter, WorkspacePageNew, AgentsPage, IntelligencePage) subscribe to WS; sports registers 3 routes with zero frontend subscriber (S1505 §14.5). Full envelope-conformance rate + subscriber matrix is Child B S2202 scope.
- **F3 domain-specific test:** **PASSES.** Zero Signal Engine emission is backend-architecture concern, not frontend-visible pattern.
- **F4 systemic test:** **FAILS with sampling scope hedge** (Q8 STRENGTHEN — "no evidence found in sampled surfaces"). Non-betting surfaces show identical patterns in god-components + zero-test + zero-persistence + no-typed-API.

**Verdict:** S1505 §14 findings graduate from single-route slice to whole-frontend governance concerns. Governance urgency at S2299 xx99 elevates accordingly.

## Contract-surface criteria scoring (Child A's 3 in-scope criteria)

- **Criterion 1** (every route maps to owned page + layout with declared consumer contract) — **PARTIAL** (Q9 FOLD; route ownership map exists in App.tsx, declared durable typed contract source-of-truth missing).
- **Criterion 5** (component/page/layout boundaries + no god-component pathologies) — **PARTIAL** (Q10 FOLD; 6 of 38 pages god-components; criterion violated in aggregate but not uniform failure).
- **Criterion 6** (failure-mode + boundary behavior standardized + observable) — **UNMET** (no error boundaries; silent 401 default at `frontend/src/lib/api.ts:48-56`; per-arc handoff to Group 2400 Auth for session-model resolution).

## §20.6 POSTURE-DECISION Chris-ratified

**DOWNGRADE S1273 32-domain row 18 Frontend/Workspace UI posture from "STABLE + DEEP" to "WORKING + MEDIUM"** (Q17 FOLD single-posture commit). HIGH confidence (multi-axis corroboration from 6 Explore agents + 4-falsifier SYSTEMIC verdict + Rigby SIGN HIGH). Anchor edit deferred to S2299 xx99 close per playbook §11.3.

## §19 T-slot follow-on queue (9 items)

- **R1** — frontend test-framework establishment (HIGH priority; parallel gating-safety per Q18 STRENGTHEN)
- **R2** — Child E component-pattern deep dive (Chris D-gate — path (b) fold-into-S2299-xx99 + graduate-as-post-arc-T-slot per Item 3 close-card ratification; subdivision cost estimate CommandCenterPage 2,551 XL > AgentsPage 4,695 XL > BettingPage 3,023 XL)
- **R3** — Route ownership map extraction to `routes.config.ts` source-of-truth (cross-arc Group 2500 coordination)
- **R4** — CODEOWNERS establishment
- **R5** — Cockpit route retirement decision (Chris-gated; requires external inbound-link audit)
- **R6** — Error-boundary framework establishment (cross-arc Group 2400 + Group 2500)
- **R7** — Session-annotation retrofit for 22 unlabeled pages
- **R8** — PLATFORM_INVENTORY route-count reconciliation (xx99 close cascade)
- **R9** — Parent-scoping doc correction — replace `normalizeWorkspaceTab()` reference with `legacyTabMapping` + `resolveFromUrl`

## Cross-arc handoffs

- **To S2202 Child B:** sports 3-WS-routes-zero-frontend-subscriber baseline + F2 falsifier PENDING-CHILD-B-CONFIRMATION resolution + 7 pages with `useWebSocket` inventory (CommandCenterPage, WorkspacePageNew via useSystemEvents, AgentsPage, IntelligencePage, Layout, HeartWidget, useWebSocket.ts hook itself)
- **To S2203 Child C:** 93 api-modules zero-typed-contracts baseline + silent-401 discipline audit + AUTH-DRIFT pattern rate + `frontend/src/lib/{api,apiClient,cockpitApi}.ts` inventory
- **To S2204 Child D:** 7 Zustand stores (authStore, paStore, bodyStore, navigationStore, unifiedStore, workspaceStore, assistantContextStore) + 5 hooks + only 4/80 pages persist state baseline
- **To S2299 xx99:** POSTURE-DECISION WORKING+MEDIUM commit + Child E path-b fold-in + §19 R1-R9 T-slot queue + cross-arc flags to Groups 2400/2500/2600/1300+1600+1800
- **To Group 2400 Auth (future arc):** silent-401 systemic + cockpit two-stage auth MINOR-DRIFT
- **To Group 2500 API (future arc):** no typed API contract source-of-truth (93 api-modules zero exported TS types); no error boundaries
- **To Group 2600 PA (future arc):** GlobalPADock visibility route-coupling (§14.5 option-space per Q16 STRENGTHEN); PA-adjacent 3-surface PARTIAL-DUPLICATE (§17.2 per Q15 FOLD)
- **To Group 1300 Memory / 1600 Content / 1800 HumanAttention:** content standalone-vs-workspace surface overlap (§17.1); render-authority split per S2200 §7.1 already-designed

## Verifier-loop discipline

Six parallel Explore sub-agents fired per playbook §13:
- **Agent 1** — Route inventory (59-row map) + auth-wrapper hygiene (single ProtectedRoute wrapper; 4 public unauthenticated + 50 authenticated + 16 cockpit redirects two-stage auth MINOR-DRIFT)
- **Agent 2** — Page component structure + god-component detection (12 pages >1,000 LOC; 6 pages >1,500 LOC; Child E trigger MET; subdivision cost ranking)
- **Agent 3** — Layout parent audit (Layout.tsx 76 LOC clean separation; CockpitLayout.tsx 67 LOC DEAD CODE; Sidebar 366 LOC; Header 62 LOC; GlobalPADock hidden on `/`)
- **Agent 4** — Legacy tab / normalization deletion candidates (19 legacy sub-tab values load-bearing; `normalizeWorkspaceTab()` already deleted; 16 cockpit redirects UNKNOWN-deletion pending inbound-link audit)
- **Agent 5** — Prior-arc cross-ref + 4-falsifier criteria application (SYSTEMIC verdict; per-axis rubric produced)
- **Agent 6** — Drift + debt + boundary + ownership + maturity per §13-§18 (composite maturity WORKING; drift signals; ownership gaps)

Parent-Claude verifier-loop applied per playbook §14 on load-bearing pre-Explore claims (route count 61 claimed vs 59 counted; god-component threshold via `wc -l` sweep; test coverage via glob; CODEOWNERS via find; normalizeWorkspaceTab() via grep). Rigby SIGN cycle 1 caught + folded 19 calibration/rubric/scope-guarding edits pre-commit at HIGH confidence.

## Distinguishing property

**First Group 2200 child audit — first library child audit to enumerate whole-frontend routes+pages+layouts+components at contract level.** **First child audit to apply S2200 §2.4 four-falsifier framing** on inherited hypothesis findings; produces SYSTEMIC verdict via per-axis rubric replacing composite %-rate arithmetic (Q6 STRENGTHEN fold — first-time per-axis-rubric methodology). **First library child audit under the 4th-consecutive-parent-with-4-children arc's FIRST child slot** — extends the pattern's execution baseline into the 4-child implementation. **First child audit to explicitly downgrade a 32-domain map posture claim (row 18 STABLE+DEEP → WORKING+MEDIUM)** with Chris-ratified single-posture commit per Q17 FOLD — commit-not-fence-sitting discipline validated. **First child audit to meet a Child E spin-out trigger at page level (S2200 §5 Q4 STRENGTHEN threshold) AND fold Child E scoping into xx99 per Chris D-gate path (b)** — preserves arc runtime target 6 sessions + preserves §7 anti-scope discipline (subdivision execution stays post-arc T-slot).

Runtime target on track — **2 of 6 shipped** (S2200 parent + S2201 P1 Child A this session).

## Next-session priority

**S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope Audit** per playbook §11.2 20-section child-audit template (THIRTEENTH-consecutive application overall).

See `00-START-NEXT-SESSION.md` for full priorities + SESSION READY CHECK.

# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2200 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**ACTIVE ARC PIN.** Group 2200 arc pin `pa-f7fd5016600f4513` PRESERVED through S2201 close per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails. TENTH formal arc pin under Research OS. S2201 SIGN cycle 1 pin `pa-8d60e999e01c40e4` retired at cycle close (updated_count=5). `tools/pa_local.sh:225` already dispatches into `pa-f7fd5016600f4513` — no rotation needed at S2202 open.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2200 S2201 CHILD A CLOSED AT S2201; NEXT = S2202 CHILD B

**Group 2200 Frontend (Contract-Surface Arc): S2201 Child A Routes + Pages + Layouts + Component Patterns Audit CLOSED 2026-07-05.** Chris "agree all" 2026-07-05 ratified all 5 close-card items wholesale (19-fold SIGN cycle 1 acceptance + POSTURE-DECISION WORKING+MEDIUM commit + Child E path (b) fold-into-S2299-xx99 + arc-cascade sequence + commit-gate). TWELFTH-consecutive application of playbook §11.2 20-section child-audit template.

- **Arc pin ACTIVE:** `pa-f7fd5016600f4513` (TENTH formal arc pin; preserved across all sessions per playbook §16 arc-standard behavior).
- **Arc progress:** S2200 parent scoping (shipped) → S2201 P1 Child A Routes + Pages + Layouts + Component Patterns (shipped this session) → **S2202 P2 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope (next)** → S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline → S2204 P4 Child D Session-scoped State Management + Persistence Discipline → S2299 xx99 Canonical Summary. Runtime target 6 sessions on track — **2 of 6 shipped**.
- **Next session:** S2202 Child B WebSocket Consumer Surface + `ui.render_hint` Envelope Audit per playbook §11.2 20-section child template (THIRTEENTH-consecutive application overall).

## READ THIS THIRD — S2201 SHIP STATE

**Doc:** `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` (~730 lines post-Rigby-SIGN-19-folds; `status: active` post-Chris-agree-all-ratification).

**Playbook §11.2 20-section child-audit template — TWELFTH-consecutive application** after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104.

**SIGN cycle 1 result:** SIGN-with-edits at HIGH confidence via dedicated fresh SIGN pin `pa-8d60e999e01c40e4` (retired at cycle close via `session_tool.retire`, updated_count=5, retired=true). 4 batches × 5 questions = **20 total Q; 19 folds landed pre-commit-gate.** Cycle 2 NOT required.

**19 folds by batch:**
- **Batch 1 framing + severity:** Q1 CLEAN F1 route-count-delta reclassified `observation` (not `drift`) + Q2 STRENGTHEN F2 severity scales blast+churn+defect (HIGH baseline; CRITICAL for CommandCenterPage + BettingPage) + Q3 STRENGTHEN F3 zero-test-coverage CRITICAL → HIGH baseline + CRITICAL-for-specific-surfaces + single-op caveat + Q4 STRENGTHEN F4 CODEOWNERS-absent CRITICAL → HIGH + single-op caveat + Q5 CLEAN F5 legacy sub-tab enum `legacy_compatibility_debt` (not `drift`).
- **Batch 2 falsifier + criteria:** Q6 STRENGTHEN F1 composite %-rate → per-axis rubric (violation-index not violation-rate) + Q7 STRENGTHEN F2 → PENDING-CHILD-B-CONFIRMATION + Q8 STRENGTHEN F4 sampling-scope hedge ("no evidence found in sampled surfaces") + Q9 FOLD Criterion 1 UNMET → PARTIAL (map exists in App.tsx; durable typed contract SoT missing) + Q10 FOLD Criterion 5 UNMET → PARTIAL (6/38 god-components; not uniform failure).
- **Batch 3 Child E + cross-arc:** Q11 STRENGTHEN surface = top-level product area (Command-Center counted 3× reframed to loci-within-surface; trigger MET across 4 surfaces) + Q12 CLEAN workspace-tab god-components labeled intra-route tab components (supplement not trigger-critical) + Q13 STRENGTHEN silent-401 softened to frontend-symptom + Group 2400 handoff + Q14 STRENGTHEN no new §14 drift entry for API types (Child C S2203 owns) + Q15 FOLD PA-adjacent overlap DIFFERENT-CONCERNS → PARTIAL-DUPLICATE / intentional multi-locus (Group 2600 decides).
- **Batch 4 anti-scope + verdict:** Q16 STRENGTHEN GlobalPADock recommendation as option-space (Group 2600 owns concrete mechanism) + Q17 FOLD POSTURE-DECISION commit **WORKING + MEDIUM** (not fence-sit) + Q18 STRENGTHEN R2 leads R1 in execution sequence + R1 parallel gating safety + Q19 CLEAN §14.6 doc-drift labeled handoff note + Q20 SIGN-with-edits at HIGH confidence verdict.

**Chris ratified 5 close-card items via "agree all" 2026-07-05:**
1. 19-fold SIGN cycle 1 acceptance
2. §20.6 POSTURE-DECISION commit — DOWNGRADE S1273 32-domain row 18 Frontend/Workspace UI from **STABLE+DEEP → WORKING+MEDIUM** at S2299 anchor edit
3. Child E path (b) — fold Child E scoping + trigger evidence into S2299 xx99 canonical summary + graduate as post-arc T-slot (preserves arc runtime target 6 sessions + §7 anti-scope discipline)
4. Arc-cascade sequence (OPEN_ARCS + ARCHITECTURE_INDEX v77→v78 §1.81 + 00-START-NEXT + SESSION_2201 handoff + 4-step docs cascade + build_docs_provenance)
5. Commit-gate approval

**Central lens question (§lens verbatim Chris-locked at S2200):**

*"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

**S2201 Child A slice answer:** structurally healthy at route + auth-wrapper + layout boundary; structurally under-specified at page-component + consumer-contract boundary. S1505 hypothesis CONFIRMED SYSTEMIC via 4-falsifier per-axis rubric — findings graduate from single-route slice to whole-frontend governance concerns.

## READ THIS FOURTH — S2202 CHILD B SCOPE

Per playbook §11.2 20-section audit template. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14. Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` (4-batch × 5-Q cadence for 20-section audit shape = 20 total).

**Child B load-bearing input (per S2200 §5 Child B):**
- ~33+ WebSocket consumer classes registered across `*/routing.py` files (`core/routing.py`, `sports/routing.py`, `intelligence/routing.py`, `ai_core/routing.py`, `ai_core/intelligence/routing.py`)
- `frontend/src/hooks/useWebSocket.ts` — 7 pages subscribe (CommandCenterPage, WorkspacePageNew, AgentsPage, IntelligencePage, Layout via useSystemEvents, HeartWidget, IntelligencePage)
- S1505 §14.1 MOCK-DATA-CONSUMER `/ws/dbao/` + §14.5 zero-WS-subscription for 3 sports routes
- S2003 §10.3.4 D4 + S2099 §14.3.4 `ui.render_hint` envelope unadopted
- S2104 §17.3 §20.1 retrieval-surface counter operator-surface — Group 1700 cross-arc coordination flag
- S2201 F2 PENDING-CHILD-B-CONFIRMATION handoff — surface-local sports-specific WS subscription-completeness hypothesis awaiting Child B empirical test

**Child B load-bearing output (per S2200 §5 Child B):**
- **B1 subscription surface:** consumer registry (33+ rows) + frontend subscription map + DEAD-CONSUMER inventory (registered backend consumer with zero frontend subscribers) + MOCK-DATA-CONSUMER inventory (S1505 §14.1 pattern class)
- **B2 envelope surface:** `ui.render_hint` envelope conformance rate + enforcement-locus recommendation (registration-time vs runtime vs defer)
- T0/Gate at Child B = decision + measurement gate NOT implementation gate per S2200 §5 D8 (no envelope schema authorship; no enforcement wiring during arc per §7 anti-scope)
- POSTURE-DECISION evidence plan §20.6 owed to xx99 on `ui.render_hint` envelope enforcement locus

**Per-surface reporting constraint (S2200 §5 Q1 STRENGTHEN fold):** Child B MUST report findings per major surface (workspace / betting / command-center / PA) in addition to axis-level rollups.

**Timebox + sampling rule (S2200 §5 Q10 STRENGTHEN fold):** Child B timeboxed to 1 session; where full 33+ consumer + FE-subscription deep-inspection threatens runtime, ship complete registry skeleton (33+ rows enumerated at metadata level) + apply documented sampling strategy for deep inspection.

**Anti-scope §7.1 guardrails for S2202:**
- No fixes / no new envelope schema (per §7 anti-scope)
- No enforcement wiring (T0/Gate = decision + measurement gate, NOT implementation gate)
- Consumer registry is FE + BE inventory; **envelope schema authorship** is out-of-arc regardless of measured adoption rate
- Cross-arc coordination flag to Group 1700 Observability (S2104 §17.3 §20.1) — surface reference-only, no operator-surface spec

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2201 arc-close cascade residuals

Per Chris "agree all" ratification at S2201 close:

- **Post-commit docs cascade** — 4-step cascade (`build_docs_index` + `build_rag_corpus` + `sync_docs_index_to_documents` + `sync_docs_index_to_documents --embed`) + `build_docs_provenance` per `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`. Execute post-merge.

### S2199 post-arc T-slot execution queue (unchanged carry into S2202)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8. All post-arc execution, NOT blocking S2202 Child B execution.

### S2200/S2201 arc residuals owed to S2299 xx99

- Child E scoping fold-in (S2201 Item 3 path (b)) — S2299 xx99 canonical summary will fold Child E trigger evidence + subdivision cost estimate + prioritized candidate list (CommandCenterPage 2,551 XL > AgentsPage 4,695 XL > BettingPage 3,023 XL) into §8 T-slot queue as graduated post-arc T-slot
- S2201 R1-R9 T-slot queue → xx99 §8 follow-on research queue
- S2201 F1 route-count reconciliation → xx99 §7 anchor-update batch (regen PLATFORM_INVENTORY §Frontend)
- S2201 §20.6 POSTURE-DECISION commit S1273 32-domain row 18 STABLE+DEEP → WORKING+MEDIUM → xx99 §7 anchor-update batch
- S2201 cross-arc flags to Groups 2400/2500/2600/1300+1600+1800 → xx99 §9 cross-links section

### Group 2200 residual queue expected at S2299 close

- 4 child audits: S2201 Child A shipped + S2202 Child B + S2203 Child C + S2204 Child D
- xx99 canonical summary (S2299) with 12-section playbook §11.3 template + §10 meta-methodology TENTH application
- MC-4 4th-arc confirmation extension (dial-back resolution deferred to Group 2300+)
- Post-arc T-slot queue owed to xx99 from all 4 child audits

## SESSION READY CHECK (before opening S2202 Child B audit)

Before drafting the S2202 Child B audit doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (arc pin `pa-f7fd5016600f4513` already active in `tools/pa_local.sh:225`; no rotation needed at S2202 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + S2201 as most-recent 20-section child exemplar
3. Read `docs/research/domains/frontend/2200_frontend_domain_scoping.md` §5 Child B block for load-bearing input + expected output + delegates + B1/B2 sub-axes
4. Read `docs/research/domains/frontend/2201_frontend_routes_pages_layouts_components_audit.md` §5 (Zustand stores + hooks + useWebSocket page inventory) + §9 (integration table WS subscription strength per surface) + F2 PENDING-CHILD-B-CONFIRMATION baseline
5. Read `docs/PLATFORM_INVENTORY.md` §Frontend row for baseline counts + `docs/topics/frontend.md` for narrative baseline (stale-warned)
6. Grep `*/routing.py` files across `core/`, `sports/`, `intelligence/`, `ai_core/` for ~33+ consumer classes + enumerate registry
7. Grep `frontend/src` for `useWebSocket`, `new WebSocket`, `wss:`, `ws:` — 7 confirmed pages at S2201 close; verify + inventory subscription hooks
8. Read S2003 §10.3.4 D4 + S2099 §14.3.4 + S2104 §17.3 §20.1 for `ui.render_hint` envelope context
9. Read `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` §14.1 (`/ws/dbao/` MOCK-DATA-CONSUMER) + §14.5 (zero-WS-subscription for 3 sports routes) for baseline HYPOTHESIS
10. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — 20-section child audit shape = 4-batch × 5-Q cadence (20 total)
11. Plan 6 parallel Explore sub-agents per playbook §13 (candidate divisions: A1 consumer registry + backend inventory / A2 FE subscription map + hook usage / A3 MOCK-DATA-CONSUMER + DEAD-CONSUMER classification / A4 `ui.render_hint` envelope conformance rate + enforcement-locus recommendation / A5 prior-arc cross-ref + F2 PENDING-CHILD-B-CONFIRMATION resolution / A6 §11.2 §13-§18 drift+debt+boundary+ownership+maturity)
12. Consider MC-5 CODIFICATION-CONFIRMED extension candidate — S2202 will be THIRTEENTH-consecutive parent-with-children arc §11.2 template application; would extend the CODIFICATION-CONFIRMED milestone count 12 → 13 consecutive

**S2202 open command (Chris short command):** `Continue research group 2200: Child B` or equivalent invocation.

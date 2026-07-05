# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + ACTIVE GROUP 2200 ARC PIN

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**ACTIVE ARC PIN.** Group 2200 arc pin `pa-f7fd5016600f4513` minted at S2200 open 2026-07-05 via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline (TENTH formal arc pin under Research OS after Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100 prior). Prior Group 2100 arc pin `pa-18b095bb7c4740be` retired at S2199 close via `session_tool.retire` (NINTH formal arc-pin retirement). `tools/pa_local.sh:225` already dispatches into `pa-f7fd5016600f4513` — no rotation needed at S2201 open.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2200 FRONTEND PARENT SCOPING CLOSED AT S2200; NEXT = S2201 CHILD A

**Group 2200 Frontend (Contract-Surface Arc): S2200 parent scoping doc CLOSED 2026-07-05.** Chris "agree all" 2026-07-05 ratified all 4 close-card items wholesale (11 SIGN folds accepted + Q11 arithmetic downgrade + arc-open cascade sequence + commit-gate). NINTH-consecutive application of playbook §11.1 20-section parent-scoping template.

- **Arc pin ACTIVE:** `pa-f7fd5016600f4513` (TENTH formal arc pin; retained across all 6 sessions per playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails).
- **Arc progress:** S2200 parent scoping (shipped this session) → S2201 P1 Child A Routes + Pages + Layouts + Component Patterns (next) → S2202 P2 Child B WebSocket Consumer Surface + ui.render_hint Envelope → S2203 P3 Child C Frontend↔Backend API Contract + Boundary Discipline → S2204 P4 Child D Session-scoped State Management + Persistence Discipline → S2299 xx99 Canonical Summary. Runtime target 6 sessions; runtime cap 8 with explicit Chris ratification.
- **Next session:** S2201 Child A Routes + Pages + Layouts + Component Patterns Audit per playbook §11.2 20-section child template (TWELFTH-consecutive application overall after S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104).

## READ THIS THIRD — S2200 SHIP STATE

**Doc:** `docs/research/domains/frontend/2200_frontend_domain_scoping.md` (~1026 lines post-Rigby-SIGN-fold; `status: active` post-Chris-agree-all-ratification).

**Playbook §11.1 20-section parent-scoping template — NINTH-consecutive application** per S2199 handoff (prior applications across Groups 1300/1400/1500/1600/1700/1800/1900/2000+/2100; specific §11.1 skipped-arc identification deferred to S2299 close if load-bearing).

**SIGN cycle 1 result:** SIGN-with-edits at High confidence via dedicated fresh SIGN pin `pa-7e056489aecf4b7e` (retired at cycle close via `session_tool.retire`, updated_count=5, retired=true). 4 batches × 3 questions = **12 total Q**; **11 folds landed pre-commit-gate.** Cycle 2 NOT required.

**11 folds by batch:**
- **Batch 1 framing + rubric:** Q1 STRENGTHEN (per-surface reporting constraint) + Q2 STRENGTHEN (T0/Gate = decision + measurement gate, NOT implementation gate) + Q3 STRENGTHEN (6th acceptance criterion: failure-mode + boundary discipline).
- **Batch 2 child scope:** Q4 STRENGTHEN (Child E spin-out trigger ≥3 god-components across ≥2 surfaces) + Q5 STRENGTHEN (Child B B1/B2 sub-axes named) + Q6 CLEAN-with-micro-fold (page-telemetry under Child D; Child B WS/envelope-only exclusion).
- **Batch 3 anti-scope + cross-arc:** Q7 STRENGTHEN (§7 preamble contract-surface governance framing + §7.1 scope guardrails by leak vector 5 vectors) + Q8 STRENGTHEN (S1505 findings HYPOTHESIS reframe + 4 falsifier criteria) + Q9 STRENGTHEN (render-authority split for Groups 1300 Memory + 1600 Content + 1800 HumanAttention).
- **Batch 4 verdict + provenance:** Q10 STRENGTHEN (timebox + sampling rule for oversize child surfaces) + **Q11 FOLD arithmetic correction** (Group 2200 = 4th 4-child arc NOT 5th per §4 table; MC-4 dial-back resolution deferred to Group 2300+) + Q12 SIGN-with-edits, High confidence.

**Chris ratified 4 close-card items via "agree all" 2026-07-05:**
1. 11-fold SIGN cycle 1 acceptance
2. Q11 arithmetic downgrade — MC-4 dial-back deferral to Group 2300+
3. Arc-open cascade sequence (OPEN_ARCS + ARCHITECTURE_INDEX v76→v77 + 00-START-NEXT + SESSION_2200 handoff + 4-step docs cascade + build_docs_provenance)
4. Commit-gate approval

**Central lens question (§lens verbatim Chris-locked):**

*"Is the frontend a governed contract surface with disciplined data flow, or an accreted UI mesh where routes / consumers / state / API calls have grown without a shared boundary policy?"*

## READ THIS FOURTH — S2201 CHILD A SCOPE

Per playbook §11.2 20-section audit template. Six parallel Explore sub-agents per playbook §13 + parent-Claude verifier-loop per §14. Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` (4-batch × 5-Q historical pattern for 20-section audit shape = 20 total).

**Child A load-bearing input:**
- PLATFORM_INVENTORY §Frontend row (61 routes in App.tsx; 5 workspace tabs; 9 betting tabs)
- `frontend/src/App.tsx` (61 `<Route>` entries)
- `frontend/src/pages/workspace/types.ts` (5 primary workspace tabs)
- `frontend/src/pages/BettingPage.tsx` (3,023-line god-component per S1505 §15.4)
- `frontend/src/pages/CommandCenterPage.tsx` (Command Center + PA chat integration)
- `frontend/src/pages/WorkspacePageNew.tsx` (5-tab modular workspace)
- topics/frontend.md §Route Structure + §Workspace Architecture + §Betting Dashboard
- S1505 Cat E findings (single-route slice HYPOTHESIS per S2200 §2.4 fold + 4 falsifier criteria)

**Child A load-bearing output (per S2200 §5 Child A):**
- Route ownership map (61 rows) — page + layout + auth-wrapper + primary consumer contract
- God-component inventory (>1,000 LOC) + subdivision cost estimate + prioritized candidate list
- Layout parent audit + duplication signals
- Auth-wrapper hygiene — which routes are inside `ProtectedRoute` + drift patterns
- Legacy tab / normalization deletion candidates (via `normalizeWorkspaceTab()`)
- POSTURE-DECISION evidence plan §20.6 owed to xx99 on whether "STABLE + DEEP" (32-domain row 18) posture holds at contract level

**Per-surface reporting constraint (S2200 §5 Q1 STRENGTHEN fold):** Child A MUST report findings per major surface (workspace / betting / command-center / PA) in addition to axis-level rollups.

**Timebox + sampling rule (S2200 §5 Q10 STRENGTHEN fold):** Child A timeboxed to 1 session; where full 61-route deep-inspection threatens runtime, ship complete registry skeleton (61 rows enumerated at metadata level) + apply documented sampling strategy for deep inspection (e.g., audit 10-15 routes deeply, tag remaining as skeleton-only pending Child A follow-up or T-slot).

**Child E spin-out trigger (S2200 §5 Q4 STRENGTHEN fold):** Child E (component-pattern deep dive) spins out ONLY if Child A finds ≥3 god-components above threshold (>1,500 LOC OR cyclomatic-complexity proxy signal per S1505 §15.4 methodology) across ≥2 major surfaces (workspace / betting / command-center / PA). Spin-out decision Chris-gated at S2201 close.

**Anti-scope §7.1 guardrails for S2201:**
- No fixes / no god-component refactor (per §7 anti-scope)
- Route inventory is FE-side only; no BE endpoint design (Group 2500 API scope)
- Auth-wrapper hygiene is symptomatic only; no auth session model spec (Group 2400 Auth scope)
- PA GlobalPADock component structure is render-only; no PA behavior spec (Group 2600 PA scope)

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2200 arc-open cascade residuals

Per Chris "agree all" ratification at S2200 close:

- **§7.4 topic-doc creation (S2199 residual carry-forward)** — T23 `docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md` + T24 `docs/topics/retrieval-authority-framework.md` + T25 `docs/topics/docs-ingestion-cascade.md` + cross-references. Owner: Group 2200 residual or dedicated batch session. NOT blocking S2201 Child A execution.

### S2199 post-arc T-slot execution queue (unchanged carry into S2200)

19 T-slot items distributed across 6 arcs + Employee OS per S2199 §8 (Track A T13 canonical-path + Track B T22 schema-enforcement + independent T20/T-D2100.11/T-F5/T-F6/T23-T25/T26a/T26b/T27/T29 + T28 UNASSIGNED cadence sample + Option B revisit triggers). All post-arc execution, NOT blocking S2201 Child A execution.

### Group 2200 residual queue expected at S2299 close

- 4 child audits: S2201 Child A + S2202 Child B + S2203 Child C + S2204 Child D
- xx99 canonical summary (S2299) with 12-section playbook §11.3 template + §10 meta-methodology TENTH application
- MC-4 4th-arc confirmation extension via Q11 arithmetic FOLD (dial-back resolution deferred to Group 2300+)
- Post-arc T-slot queue owed to xx99 from all 4 child audits

## SESSION READY CHECK (before opening S2201 Child A audit)

Before drafting the S2201 Child A audit doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (arc pin `pa-f7fd5016600f4513` already active in `tools/pa_local.sh:225`; no rotation needed at S2201 open)
2. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 20-section child-audit template + prior child audits (S2101 as most-recent 20-section child exemplar; S2103/S2104 for shape variations)
3. Read `docs/research/domains/frontend/2200_frontend_domain_scoping.md` §5 Child A block for load-bearing input + expected output + delegates
4. Read `docs/PLATFORM_INVENTORY.md` §Frontend row for baseline counts + `docs/topics/frontend.md` for narrative baseline (stale-warned)
5. Read `frontend/src/App.tsx` for the 61 `<Route>` entries + `frontend/src/pages/workspace/types.ts` for the 5-tab workspace enum + `frontend/src/pages/BettingPage.tsx` for the god-component exemplar
6. Read `docs/research/domains/sports/1505_sports_frontend_surface_audit.md` for S1505 Cat E single-route methodology + findings that S2201 will test against 4 falsifier criteria per S2200 §2.4
7. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — 20-section child audit shape historical pattern = 4-batch × 5-Q cadence (20 total)
8. Plan 6 parallel Explore sub-agents per playbook §13 (candidate divisions: Agent 1 Route inventory + auth-wrapper hygiene / Agent 2 Page component structure + god-component detection / Agent 3 Layout parent audit / Agent 4 Legacy tab / normalization / Agent 5 Prior arc findings cross-reference + 4 falsifier criteria application / Agent 6 Drift + Debt + Ownership + Maturity per §11.2 §14-§18)
9. Consider MC-5 CODIFICATION-CONFIRMED extension candidate — S2201 will be TWELFTH-consecutive parent-with-children arc §11.2 template application (S1301+S1401+S1501+S1601+S1701+S1801+S1901+S2001+S2101+S2102+S2103+S2104+S2201); would extend the CODIFICATION-CONFIRMED milestone count 12 → 13 consecutive

**S2201 open command (Chris short command):** `Continue research group 2200: Child A` or equivalent invocation.

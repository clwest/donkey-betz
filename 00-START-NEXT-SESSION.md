# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP + NO ACTIVE ARC PIN (POST-GROUP-2100 CLOSE)

`tools/pa_chat.py:41` has `DEFAULT_BASE_URL = "http://localhost:8000"` (already local by default as of S1249 PR #2712). The `.env` file's `PA_API_TOKEN` is the **production** token — if you call `pa_chat.py` bare against local without a local-token override, you'll get 401. Always use `tools/pa_local.sh` (sets URL + local token).

**NO ACTIVE ARC PIN.** Group 2100 arc pin `pa-18b095bb7c4740be` RETIRED at S2199 close 2026-07-05 via `session_tool.retire` per playbook §16 arc-close discipline (NINTH formal arc-pin retirement after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099). `tools/pa_local.sh:215` currently dispatches into `pa-18b095bb7c4740be` — **rotate to fresh Group 2200 arc pin at S2200 formal arc open** via `session_tool.create_fresh` per playbook §16 arc-open fresh-thread discipline (TENTH formal arc pin). Prior arc pin ledger updated with S2199 retirement + S2200 open transition per S1900/S2000/S2100 documentation pattern.

### The correct LOCAL invocation
```bash
tools/pa_local.sh "message"
```

**Before your first `pa_local.sh` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

## READ THIS SECOND — GROUP 2100 RAG / DOCUMENT LOADING (KNOWLEDGE LOOP) CLOSED AT S2199; NEXT ARC = GROUP 2200 FRONTEND PER CHRIS D-OVERRIDE

**Group 2100 RAG / Document Loading (Knowledge Loop) arc: S2199 xx99 canonical summary CLOSED 2026-07-05.** Chris "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05 ratified all 6 close-card items wholesale + selected Group 2200 Frontend as next-arc D-override per post-S2099 project memory queue ranking.

- **Arc pin RETIRED:** `pa-18b095bb7c4740be` retired via `session_tool.retire` at S2199 close (NINTH formal arc-pin retirement).
- **Arc progress FINAL:** S2100 parent scoping (shipped) → S2101 P1 Corpus State (shipped) → S2102 P2 Ingestion Pipeline (shipped) → S2103 P3 Retrieval Authority Framework + Governance Design (shipped) → S2104 P4 Behavior Substrate Structured Observation + Integration (shipped) → S2199 xx99 Canonical Summary (shipped this session). Runtime target 6 sessions ACHIEVED — 6 of 6 shipped.
- **Next arc:** Group 2200 Frontend per Chris D-override 2026-07-05 (post-S2099 draft queue: 2200 Frontend / 2300 Mobile / 2400 Auth / 2500 API / 2600 PA).

## READ THIS THIRD — S2199 SHIP STATE

**Doc:** `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` (~525 lines post-fold; `status: active` post-Rigby-SIGN + post-Chris-ratification).

**Playbook §11.3 12-section canonical-summary template + §10 meta-methodology — NINTH-consecutive application** after S1399 first + S1499 second + S1599 third + S1699 fourth + S1799 fifth + S1899 sixth + S1999 seventh + S2099 eighth.

**SIGN cycle 1 result:** CLEAN with 2 STRENGTHEN + 2 CLEAN + 0 FOLD + 0 REJECT across single-batch Q1-Q4 canonical-summary cadence. Both STRENGTHEN folds landed pre-commit at §4.1 + §5.2 + §10.1 + §12.5. Cycle 2 NOT required per canonical-summary shape single-batch discipline. D48 arm CLEAN → MC-2 40 → 41.

**Chris ratified 6 close-card items via "agree all + (6)=(a) Group 2200 Frontend" 2026-07-05:**
1. Canonical seam statement §5.1 verbatim + N_observed=3 vs N_evidence_items=14 methodology-note carry-forward discipline
2. §7 anchor-update batch scope as single atomic follow-up PR (7.1 PLATFORM_INVENTORY subsection + 7.2 PLATFORM_WHAT_IT_IS Current State Honesty + 7.3 ARCHITECTURE_INDEX v75→v76 + §1.79 + §3 domain map row Closed + 7.4 create T23 docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md + T24 docs/topics/retrieval-authority-framework.md + T25 docs/topics/docs-ingestion-cascade.md + cross-references)
3. 19 T-slot follow-on queue two-track structure (T22 Track B + T13 Track A + 6 T1 + 9 T2 + 2 T3)
4. Meta-methodology milestone updates: MC-2 40→41 + MC-3 8→9 + MC-4 3→4 with dial-back + MC-5 8→12 + 4 new CANDIDATES MC-7/MC-8/MC-9/MC-10
5. Arc-close cascade sequence (commit + ARCHITECTURE_INDEX v75→v76 + OPEN_ARCS Closed + 00-START-NEXT + 4-step docs cascade + SESSION_2199 handoff + arc pin retirement)
6. Next-arc D-override selection = (a) Group 2200 Frontend

**Canonical seam statement (§5.1 verbatim):**

*"Rigby's RAG corpus IS a design-governed corpus substrate — spec-complete via P3, evidence-supported via P4, execution-pending via post-arc T-slots — in transition toward runtime-governed institutional knowledge layer along the maturity gradient passive → spec-complete → execution-complete."*

## READ THIS FOURTH — GROUP 2200 FRONTEND ARC OPEN SCOPE

Per Chris D-override at S2199 close 2026-07-05 + post-S2099 project memory queue ranking (draft):

**Provisional Group 2200 arc scope (Chris-directed refinement pending at S2200 parent scoping open):** Frontend architecture arc covering:
- React app in `frontend/` (~61 routes in App.tsx + Command Center + 5-tab workspace + 9-tab betting dashboard)
- WebSocket consumer surface across ~33+ consumer classes + `ui.render_hint` envelope adoption gaps (per S2003 §10.3.4 D4 + S2099 §14.3.4 unenforced)
- Frontend↔backend API contract inventory + boundary discipline
- Session-scoped state management + persistence discipline
- Component vs page vs layout architecture patterns

**Playbook application:** §11.1 20-section parent-scoping template NINTH application (after S1300 first + S1400 second + S1500 third + S1600 fourth + S1700 fifth + S1800 sixth + S1900 seventh + S2000 eighth + S2100 ninth) — NINTH-consecutive parent-with-children arc. §16 arc-open fresh-thread discipline: mint fresh arc pin at S2200 open via `session_tool.create_fresh` (TENTH formal arc pin).

**Post-arc queue backlog (per S2199 project memory ranking, NOT ratified in OPEN_ARCS.md §22 yet):**
- Group 2300 Mobile
- Group 2400 Auth
- Group 2500 API
- Group 2600 PA

## READ THIS FIFTH — OUTSTANDING RESIDUALS

### S2199 arc-close cascade residuals

Per Chris item 2 ratification + item 5 arc-close cascade sequence at S2199 close:

- **§7 anchor-update batch as single atomic follow-up PR** (per S2099 §7 pattern) — includes 7.1 PLATFORM_INVENTORY subsection for RAG Corpus Governance; 7.2 PLATFORM_WHAT_IT_IS Current State Honesty subsection; 7.3 ARCHITECTURE_INDEX v75 → v76 + §1.79 registration + §3 domain map row Closed (executed at S2199 close); 7.4 T23 docs/00-START-HERE/RAG_CORPUS_GOVERNANCE.md + T24 docs/topics/retrieval-authority-framework.md + T25 docs/topics/docs-ingestion-cascade.md creation + cross-references to KNOWLEDGE_PIPELINE + EMPLOYEE_OS_PRIMITIVES + CLAUDE.md. Owner: Group 2200 residual or dedicated batch session. NOT blocking Group 2200 arc open.

### S2199 post-arc T-slot execution queue

Enumerated at S2199 §8 T-slot table + §12.5 milestone counts. Track A T13 canonical-path + Track B T22 → T18/T19/T21 schema-enforcement + independent T20/T-D2100.11/T-F5/T-F6/T23-T25/T26a/T26b/T27/T29 + T28 UNASSIGNED cadence sample + Option B revisit triggers. **Total 19 T-slot items** distributed across 6 arcs + Employee OS. All post-arc execution, NOT blocking Group 2200 arc open.

### S2104 post-arc T-slot execution queue (unchanged from S2104 close carry into S2199)

Absorbed into S2199 §8 T-slot queue above.

## SESSION READY CHECK (before opening S2200 Group 2200 Frontend parent scoping)

Before drafting the S2200 parent scoping doc:
1. `tools/pa_local.sh "platform_config_tool action=overview"` → confirm `service_context: local` (**note:** Group 2100 arc pin `pa-18b095bb7c4740be` retired at S2199 close; `tools/pa_local.sh:215` needs rotation to fresh Group 2200 arc pin)
2. Mint fresh Group 2200 arc pin at S2200 open via `session_tool.create_fresh` (TENTH formal arc pin) per playbook §16 arc-open fresh-thread discipline
3. Update `tools/pa_local.sh:215` with new Group 2200 arc pin + header ledger entry for S2199 retirement + S2200 open transition per S1900/S2000/S2100 documentation pattern
4. Read `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.1 20-section parent-scoping template + prior parent-scoping docs (S1300 first + S1400 second + S1500 third + S1600 fourth + S1700 fifth + S1800 sixth + S1900 seventh + S2000 eighth + S2100 ninth) for template shape
5. Read `docs/research/domains/rag_document_loading/2199_rag_document_loading_canonical_summary.md` for Group 2100 arc close context + cross-arc coordination flags (i) cascade lifecycle-event + (ii) retrieval-surface counter
6. Read `docs/PLATFORM_INVENTORY.md` frontend row + `docs/PLATFORM_WHAT_IT_IS.md` frontend narrative + `docs/topics/frontend.md` for existing frontend research coverage baseline
7. Plan Rigby SIGN cycle 1 batching per `feedback_rigby_sign_worker_instability_recovery` — parent-scoping shape historically = 4-batch × 3-Q cadence (12 total)
8. Consider MC-4 CODIFICATION-CONFIRMED milestone extension candidate — Group 2200 will be FIFTH-consecutive parent-with-4-children arc IF opened + closed with 4 children; would trigger Rigby SIGN cycle 1 Q3 STRENGTHEN dial-back → "fully generalized" removal per S2199 dial-back "contingent on 5th arc or materially different stress condition"

**S2200 open command (Chris short command):** `Start research group 2200: Frontend` or equivalent invocation.

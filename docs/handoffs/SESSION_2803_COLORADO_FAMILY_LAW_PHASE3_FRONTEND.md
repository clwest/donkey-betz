# Session 2803 — Colorado Family Law Phase 3.0 (frontend polish MVP + audit substrate)

**Date:** 2026-07-17
**Session:** S2803
**Branch/PR:** **PR #3222** · `1d94f8765` (merged with `--admin`)
**Predecessor:** [SESSION_2802 Colorado Family Law P0 hardening](SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** post-PR-3222 clean recycle + close-cascade recycle

---

## §1 — Ship summary

**Colorado Family Law arc, Phase 3.0** — first real user-facing surface for the Pro Se Legal Assistant. Before this session: drafting was Rigby-chat-only, no discoverability, no disclaimer in UI, no audit trail. After: full draft flow accessible at `/legal` with disclaimer banner, "Draft New Motion" button, modal with acknowledgement checkbox, live polling, and per-dispatch compliance audit log.

**Ship (PR #3222): +1,002 / −25 across 11 files. 9 tests pass in 0.722s.**

**Backend (7 files):**
- NEW `core/models_legal_audit.py` — `LegalDocumentDispatchLog` compliance-audit model
- NEW migration `0386_s2803_legal_document_dispatch_log.py` — **scope-only** (deliberately does NOT include the 15+ unrelated pending schema changes that makemigrations would have bundled from other pending model drift)
- NEW `core/services/legal_dispatch.py` — `dispatch_legal_draft(...)` shared helper; enforces `disclaimer_acknowledged=True`; writes audit row; used by BOTH new UI endpoint AND Rigby PA path (closes disclaimer-bypass loophole)
- NEW endpoints in `core/views_legal.py`:
  - `POST /api/legal/draft/` — IsAuthenticated
  - `GET /api/legal/draft-status/<task_id>/` — user-scoped poll (404 on cross-user)
- Refactored `core/services/td_handlers_agents.py:_handle_legal_agent` to route through shared helper
- `core/tasks.py:draft_legal_document_task` — writes terminal state back to DispatchLog on completion/failure
- `core/models/__init__.py` — registered new model

**Frontend (2 files):**
- `frontend/src/lib/api.ts` — `legalApi.draftMotion` + `legalApi.draftStatus`
- `frontend/src/pages/LegalPage.tsx` — non-dismissable disclaimer banner + "Draft New Motion" button + full modal with polling

**Tests (1 new file, 9 tests):**
- `core/tests/test_legal_draft_endpoint.py` — T1-T6 covering all critical paths

---

## §2 — P0 CARRY-FORWARD FOR S2804 — AGENT DRAFTING RELIABILITY

**LIVE-BROWSER TEST BY CHRIS AT S2803 CLOSE revealed a critical Phase 3.0 gap:**

- Chris submitted a real drafting request via the new UI: `"Draft a motion to modify visitation to every weekend from every other weekend"`
- Modal showed live drafting state and reached completion successfully
- Dispatch log verified: `f41d9090-0dd6-49… · user=chris · status=completed · disclaimer=True · doc=None`
- **`resulting_document=None`** — no `LegalDocument` row was persisted
- Documents tab shows nothing new

**Root cause:** the agent's `execute()` at `core/agents/legal/legal_doc_drafter_agent.py:1224-1234` only calls `_save_legal_document` when GPT returns a `tool_call` with a `document` payload. For Chris's real-user phrasing, GPT either:
1. Returned a content-only response (line 1257 fallback path — no persistence), or
2. Chose a tool that returned `info`/`explanation` rather than `document`

Phase 0 verification passed only because the explicit test prompt (`"Please invoke the LegalDocDrafterAgent to draft a Colorado Motion to Modify Parenting Time (JDF 1220-style)..."`) reliably steered GPT into the motion_drafter tool. Real user phrasing doesn't.

**This is P0 for S2804 Phase 3.1** — before adding a case wizard, the agent MUST reliably persist a `LegalDocument` for user-natural drafting requests. Options:
- (a) Tighten the GPT tool-selection prompt so `_call_openai` almost always returns a motion_drafter tool_call for drafting requests
- (b) Add a fallback: if `_call_openai` returns content-only for a task that looks like a drafting request, coerce it into a motion document + save
- (c) Add post-hoc detection: if `AgentResult.success=True` but `documents_generated=0` for a drafting-shaped task, warn + save the content as a doc

Recommend investigation → likely (a) + (c) combined.

**Symptom pattern:** dispatch log status=completed, resulting_document=None, no LegalDocument row created. Detectable via one Django query.

---

## §3 — Novel-precedent moments

**A. First arc where Phase 0 verification passed but Phase 3.0 browser test surfaced a Phase 4-blocking substrate reliability issue.** The disciplined dispatch-plus-audit surface Phase 3.0 shipped is what made the reliability gap detectable — before Phase 3.0, no one could tell whether drafting produced a document because the flow was Rigby-chat-only + user had to check DB manually. Now the audit log makes the gap surface visible: dispatch completed vs document produced diverge, and we know it.

**B. First same-session engineering + real-browser-verification loop.** Chris opened `/legal`, dispatched a real motion, observed the completion state, then reported "don't see it anywhere." That closed the loop from PR merge → recycle → live test in <10 min and produced actionable Phase 3.1 scope. Contrast with prior sessions where browser verification happened next-session.

**C. Model unification decision ratified pre-Phase-3.1.** Chris chose `CaseProfile` unification (vs `LegalCase` or bridge) at S2803 open, before scoping Phase 3.0. Prevented Phase 3.0 from making the decision by default via case-wizard scope. Case wizard now deferred to Phase 3.2 after Phase 3.1 unification lands.

**D. Migration scope-guard applied.** `makemigrations` output bundled 15+ unrelated pending schema changes (Narrative*, HAIDispatchLog renames, RigbyWorkItem renames, FleetPAChatAuditRow docs, etc.) with my new model. Recognized as pollution; hand-wrote a clean scope-only migration containing only `LegalDocumentDispatchLog`. Other pending changes remain queued for their own arcs' PRs. Novel pattern worth codifying: **auto-generated migrations are NOT trustworthy as-scope-signals — always audit output for cross-arc pollution.**

**E. Seventh-consecutive same-day multi-ship session** — S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803. Discipline held across engineering + research/scoping shifts + Phase-3 UI-heavy work.

---

## §4 — Rigby joint SIGN

**Phase 3.0 SIGN:** SIGN-WITH-EDITS. Rigby tool_runs non-empty (7+ real `repo_tool` reads verifying all 5 pre-authoring asks — disclaimer strip location, existing IP-capture helper, modal patterns, dispatch endpoint absence, postrun signal presence). Anti-rubber-stamp check PASSED. Notable substantive edits integrated:

- **B6 (Fold 2 mitigation):** shared helper for BOTH UI + Rigby PA paths — closes disclaimer-bypass loophole. Would have been F-BLOCKING if not caught.
- **B1 extended fields:** `completed_at`, `error_message`, `client_session_pin` added to audit-log model for 6-month compliance evidence.
- **T5 split:** separate completion + failure test coverage.

**3 zoom-out folds persisted (rows 102-104):**

1. `same_pr_mitigatable` — UI disclaimer vs document provenance (respect Session 404D intent; store in audit + UI badge, don't embed in content)
2. `same_pr_actionable` — Two dispatch paths → shared helper in same PR (drove B6)
3. `future_trigger` — Full tool-call trace logging (Phase 3.5+; trigger = first real-external-scrutiny filing)

**Fold 3 mandatory floor honored:** disclaimer banner + audit-log ship together. Non-dismissable banner enforced.

---

## §5 — Session-open infra story

**S2803 opened with S2802 pin retired.** Wrapper `tools/pa_local.sh` line 563 pointed at `pa-b83fbf23da724c65` (retired at S2802 close). First-action fresh mint: `python manage.py session_lifecycle open --label s2803-colorado-family-law-phase3-frontend` minted `pa-d736030d6de844be`. Wrapper auto-rotated; freshness FRESH · SHA-match `f574386edf02` at S2802 close-cascade; 0/5 stale workers.

**Test iteration story (5 iterations to green):**
1. First run: 4 fail + 4 error. Root causes: `_memory_service` + `_mythology_enforcer` missing in `__new__` bypass; `generation_context` empty-dict rejected by `full_clean()` for M3/M4.
2. Iteration 2: 2 errors — `--keepdb` reused stale test DB missing `learning_bridges_advisorconsultationfeedback` migration.
3. Iteration 3: EOF error — Django prompted to destroy test DB non-interactively.
4. Iteration 4: 2 errors — `AsyncResult` used wrong patch target (module-level import didn't exist because import is inside function).
5. Iteration 5: 2 errors — `on_task_postrun` signal handler called `close_old_connections()` mid-TestCase-transaction; fixed by disconnecting the signal for T5a/T5b.

Pattern: each iteration produced a specific, traceable failure signature. No mysterious failures. Fixed at root each time.

---

## §6 — Twin-pointer card

📁 **Repo — S2803 artifacts:**

- **Substrate:** `core/models_legal_audit.py` + migration 0386 + `core/services/legal_dispatch.py` + `core/views_legal.py` (2 new endpoints) + `core/urls.py` (2 new routes) + `core/services/td_handlers_agents.py` (refactored) + `core/tasks.py` (completion update) + `core/models/__init__.py` (registered) + `frontend/src/lib/api.ts` (2 new methods) + `frontend/src/pages/LegalPage.tsx` (banner + button + modal + polling)
- **Test file (1 new):** `core/tests/test_legal_draft_endpoint.py` (9 tests)
- **Handoff:** `docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **104 rows** (rows 102-104 are S2803)
- **Merge SHA:** `1d94f8765` (post-PR #3222 merge)

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — Legal Assistant page: disclaimer banner (yellow/amber, top), "Draft New Motion" button (blue, header right), Documents/Cases/Litigation tabs
- **Live test artifact:** Dispatch log `f41d9090…` for user chris — status=completed but resulting_document=None (the S2804 P0 bug)
- **Prior Phase 0 test doc still in DB:** `LegalDocument 475d83a1…` — visible in Documents tab

---

## §7 — Next session (S2804) — Phase 3.1

**Chris ratified at S2803 close (2026-07-17):** "close-cascade the docs so we can begin the next session" → **Phase 3.1 is S2804 P0 default.**

**Phase 3.1 REVISED scope (in priority order):**

### P0 — Agent drafting reliability (uncovered by S2803 browser test)

Fix the agent-completed-but-no-document-persisted pattern. Options:
- (a) Tighten GPT tool-selection prompt so drafting requests reliably route to `motion_drafter`
- (b) Add fallback: if `_call_openai` returns content-only for a drafting-shaped task, coerce content into a motion document
- (c) Add post-hoc detection: if `AgentResult.success=True` but `documents_generated=0`, warn/save

**Test coverage requirement:** new regression test that dispatches a natural-user phrasing (like Chris's) and asserts a `LegalDocument` row was created. Without this, Phase 3.1 can't ship.

### P1 — CaseProfile/LegalCase unification (originally P0 for 3.1, downgraded)

- Add nullable `LegalDocument.case_profile` FK to `CaseProfile`
- Backfill logic (skip for now if no `LegalCase` rows exist in prod)
- Refactor `LegalDocDrafterAgent._save_legal_document` to bind `case_profile`
- Deprecate `LegalCase.case` FK (leave nullable for grandfathered rows)

### P2 — Case creation wizard on frontend (was Phase 3.2; now blocked on P1)

- `POST /api/legal/case-profiles/` — create endpoint (currently only list/detail exists)
- Wizard modal on `LegalPage` — case_number + type + county + court + parties
- Wire draft dispatch to link to active case

**Do NOT ship Phase 3.1 without P0 fix.** The audit substrate reveals the gap; users see "Draft ready!" and then find nothing. This breaks trust.

---

## §8 — Chris D-verdict queue

All Phase 3.0 D-verdicts recorded in-session:
- Model reconciliation ratified: unify around CaseProfile
- Phase 3.0 scope approved (slim, no case wizard)
- Phase 3.0 SIGN-WITH-EDITS routed to Rigby; all 3 edits integrated
- All 3 D-verdict asks approved (revised scope + same-PR gate + new-file `models_legal_audit.py`)
- Merge/recycle approved
- Post-browser-test: close-cascade approved

**No unresolved F-BLOCKING items at close.**

**Standing owed after Phase 3.1:**
- Phase 3.2: case wizard (blocked on 3.1 unification)
- Phase 3.5+: full per-tool-call trace logging (per Rigby Fold 3 future_trigger)
- Phase 4: statute-citation content quality (C.R.S. § 14-10-129 + standards language)
- Phase 5: monthly beat schedule for `colorado_family_law_spider`
- Small follow-ups: `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening; `LegalDocument.generation_context` add `blank=True`; PA→Celery E2E integration test; 7,829-line agent file split

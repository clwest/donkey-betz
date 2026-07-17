# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2803 CLOSED — Colorado Family Law Phase 3.0 SHIPPED (Phase 3.1 P0 = agent drafting reliability, uncovered by live browser test)

**Refreshed 2026-07-17 (SESSION 2803 CLOSED — seventh consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803). Phase 3.0 shipped as PR #3222 (`1d94f8765`): draft-new-motion UI + non-dismissable disclaimer banner + `LegalDocumentDispatchLog` compliance audit + shared `dispatch_legal_draft` helper closing the Rigby PA disclaimer-bypass loophole + live polling + 9 tests. First real user-facing surface for the Pro Se Legal Assistant. Chris live-browser tested at close; dispatch worked but revealed a P0 substrate reliability gap — dispatch completes but no `LegalDocument` persists for real-user phrasing. Phase 3.1 P0 = fix agent reliability BEFORE case wizard. Model unification (CaseProfile) ratified at S2803 open, now downgraded to P1 for Phase 3.1. FORTYSEVENTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2803 ship:**

**PR #3222 · `1d94f8765`** — 11 files, +1,002 / −25. Backend audit substrate + shared dispatch helper + 2 new API endpoints; frontend disclaimer banner + draft modal + polling. 9 tests, 0.722s.

**Handoff:** `docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **104 rows** (rows 102-104 Phase 3.0 folds).

**Arc state:** Colorado Family Law — Phases 0/1/2/2.1/3.0 ✅; **Phase 3.1 P0 = agent drafting reliability (uncovered by live test)**; Phase 3.1 P1 = CaseProfile unification; Phase 3.2 = case wizard; Phase 3.5+ = full trace logging; Phase 4 = statute-citation quality; Phase 5 = spider beat schedule.

---

## SESSION-OPEN INFRA STORY (S2803)

**First arc where Phase 0 verification passed but Phase 3.0 live-browser test surfaced a Phase 4-blocking substrate reliability gap.** The disciplined dispatch-plus-audit surface Phase 3.0 shipped is what made the gap DETECTABLE. Before Phase 3.0, no one could tell whether drafting produced a `LegalDocument` because the flow was Rigby-chat-only + user had to check DB manually. Now: audit log shows dispatch completed vs document produced diverging, and we know it.

**Chris live-browser test at S2803 close:**
- Submitted `"Draft a motion to modify visitation to every weekend from every other weekend"` via the new UI
- Modal reached completion state successfully
- Documents tab: nothing new visible
- DB check: `LegalDocumentDispatchLog f41d9090… status=completed disclaimer=True resulting_document=None`
- Root cause: agent's `execute()` only calls `_save_legal_document` when GPT returns a `tool_call` with a `document` payload. Real-user phrasing doesn't reliably steer GPT into that path.

**First same-session engineering + real-browser-verification loop.** Chris closed the loop from PR merge → recycle → live test in <10 min and produced actionable Phase 3.1 scope. Contrast with prior sessions where browser verification happened next-session.

**Migration scope-guard applied.** `makemigrations` bundled 15+ unrelated pending schema changes (Narrative*, HAIDispatchLog renames, RigbyWorkItem renames, FleetPAChatAuditRow docs, etc.) with the new model. Recognized as pollution; hand-wrote a clean scope-only migration. **Codification candidate: auto-generated migrations are NOT trustworthy as-scope-signals — always audit output for cross-arc pollution before committing.**

**Model unification decision ratified pre-Phase-3.0.** Chris chose `CaseProfile` unification (vs `LegalCase` or bridge) at S2803 open. Prevented Phase 3.0 from making the decision by default via case-wizard scope. Case wizard now deferred to Phase 3.2 after Phase 3.1 unification.

---

## S2804 CANDIDATES — PHASE 3.1 P0 IS AGENT RELIABILITY

### ⭐ Phase 3.1 P0 — Agent drafting reliability (default candidate)

**Bug:** `LegalDocDrafterAgent.execute()` at `core/agents/legal/legal_doc_drafter_agent.py:1224-1234` only calls `_save_legal_document` when GPT returns a `tool_call` with a `document` payload. For natural-user phrasing, GPT frequently returns content-only or picks a non-drafter tool → no `LegalDocument` row created → user sees "Draft ready!" and finds nothing.

**Symptom pattern (detectable via one Django query):**
```
LegalDocumentDispatchLog: status=completed, resulting_document=None
LegalDocument: no new row for the user around the dispatch time
```

**Reproduction:** dispatch via `POST /api/legal/draft/` with `task_description="Draft a motion to X"`. If no `LegalDocument` appears within 5 min, bug reproduced.

**Options for fix (recommend investigation → likely (a) + (c) combined):**
- **(a) Tighten GPT prompt** — modify `_build_legal_prompt` to more strongly steer drafting requests into `motion_drafter` tool
- **(b) Add fallback** — if `_call_openai` returns content-only for a drafting-shaped task (heuristic: keywords "draft", "motion", "declaration" in task), coerce the content into a document + save
- **(c) Add post-hoc detection** — if `AgentResult.success=True` but `documents_generated=0` for a drafting-shaped task, log a warning + optionally save content as a fallback doc

**Mandatory test coverage:** new regression test dispatches natural-user phrasing (Chris's exact wording) and asserts a `LegalDocument` row was created. Without this, Phase 3.1 does not ship.

### Phase 3.1 P1 — CaseProfile/LegalCase unification

**Deferred from P0 status.** Originally Phase 3.1 opened for this; the browser bug bumped it to P1.

- Add nullable `LegalDocument.case_profile` FK to `CaseProfile`
- Backfill for any existing rows (Phase 0 test doc `475d83a1…` is only known row)
- Refactor `LegalDocDrafterAgent._save_legal_document` to bind `case_profile` (not `case=LegalCase`)
- Deprecate `LegalCase.case` FK (leave nullable for grandfathered rows)
- Eventually delete `LegalCase` model

### Phase 3.1 P2 — Case creation wizard on frontend

**Blocked on P1 unification.** Cannot ship until we've decided which model backs the wizard.

- `POST /api/legal/case-profiles/` create endpoint (currently only list/detail wired)
- Wizard modal on `LegalPage`: case_number + type + county + court + parties
- Wire draft dispatch to link to active case

### Alternate candidates (if Chris deprioritizes Phase 3.1)

- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129 + standards language for common Colorado family motions)
- **Phase 5** — monthly beat schedule for `colorado_family_law_spider`
- **Small follow-ups** (single small PRs each):
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening
  - `LegalDocument.generation_context` add `blank=True` (Phase 2 model quirk)
  - PA→Celery E2E integration test (Rigby Phase 2 SIGN Fold 4)
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split into submodules (Rigby Phase 2 SIGN Fold 3)

- **Group 2700 docs restructuring arc** (T1 = 2701 inventory audit; queued since S2801 but blocked behind Colorado arc)
- **BettingPage** (pre-existing pre-S2802 default; still owed after Colorado arc closes)
- **Stock Intelligence** (first non-betting revenue play)

---

## SESSION PIN — S2803 RETIRED (fresh mint required at S2804 open)

**Pin history (S2803):**

- `pa-d736030d6de844be` (label `s2803-colorado-family-law-phase3-frontend`) minted S2803 open; **retired at S2803 close (`force=true`, thirtyfourth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-d736030d6de844be` (retired)** — intended failure mode forces S2804 first-action fresh mint.

**S2804 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2803 handoff — §2 P0 CARRY-FORWARD (agent drafting reliability) + §7 Phase 3.1 scope
# Read core/agents/legal/legal_doc_drafter_agent.py:1180-1290 (execute() flow — where GPT tool_call is consumed)
# Read core/agents/legal/legal_doc_drafter_agent.py:1343-1500 (_build_legal_prompt — tool-steering prompt)
# Read core/tasks.py:5716-5780 (draft_legal_document_task terminal-state update)

# Freshness check. Should be FRESH · SHA-match at S2803 close-cascade SHA.
bash tools/pa_local.sh "S2804 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 104-row baseline survived S2803 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==104, r
print('OK — 104 rows, counts:', r['counts_by_classification'])
"

# Reproduce the P0 bug FIRST — dispatch a natural drafting request, wait 5 min,
# verify LegalDocumentDispatchLog shows completed + resulting_document=None
# (this is the concrete failure the fix must eliminate)

# Mint fresh pin scoped to Phase 3.1 P0
python manage.py session_lifecycle open --label s2804-colorado-family-law-phase3.1-agent-reliability

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2804 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; concrete code-state claims MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline.

**S2803 lessons to carry:**

1. **Live browser verification catches substrate bugs that unit tests miss.** T1-T9 in Phase 3.0 all passed — but the real-user-phrasing bug only surfaced when Chris typed a natural request. Add browser-verify to close-cycle discipline for user-facing arcs.
2. **Audit substrate is the visibility that makes bugs debuggable.** Phase 3.0 audit-log surface let us diagnose the P0 in one Django query. Without it: nothing to grep.
3. **Auto-generated migrations bundle unrelated pending schema drift.** Always audit `makemigrations` output before committing. Hand-write scope-only migrations for cross-arc-clean PRs.
4. **Shared helper for parallel dispatch codepaths.** The `dispatch_legal_draft` pattern (UI + PA both route through one function) is reusable for any feature with multiple entry points that need shared enforcement + audit.
5. **Phased UI shipping works when Rigby's mandatory floor is codified.** Fold 3 pre-committed disclaimer + audit-log as non-negotiable; Phase 3.0 shipped both. No case wizard yet — clean scope hold.

---

## Twin-pointer card

📁 **Repo — S2803 artifacts:**

- **PR (1, merged):** #3222 (`1d94f8765`)
- **Substrate changes:** `core/models_legal_audit.py` (new) + migration 0386 (new) + `core/services/legal_dispatch.py` (new) + `core/views_legal.py` (2 endpoints) + `core/urls.py` (2 routes) + `core/services/td_handlers_agents.py` (refactored) + `core/tasks.py` (completion update) + `core/models/__init__.py` (registered)
- **Frontend:** `frontend/src/lib/api.ts` + `frontend/src/pages/LegalPage.tsx`
- **Test file (new):** `core/tests/test_legal_draft_endpoint.py` (9 tests)
- **Handoff:** `docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **104 rows**
- **Merge SHA:** `1d94f8765` (post-PR #3222)
- **Predecessor:** S2802 Colorado Family Law P0 hardening (3 PRs shipped)

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — Legal Assistant page. Disclaimer banner (always visible). "Draft New Motion" button in header. Modal with textarea + disclaimer ack checkbox + live polling.
- **Live P0 bug artifact:** `LegalDocumentDispatchLog f41d9090…` for user chris — status=completed but resulting_document=None. Concrete regression target for Phase 3.1 P0.
- **Prior Phase 0 test doc:** `LegalDocument 475d83a1…` — visible in Documents tab (the only successful drafting artifact so far).
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2803 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0 ✅; Phase 3.1 P0 = agent drafting reliability (uncovered by live test) |
| Group 2700 docs arc | Still queued (blocked behind Colorado arc) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-d736030d6de844be` (retired at S2803 close, force=true, thirtyfourth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-d736030d6de844be` (retired; forces fresh mint at S2804 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2803 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 events during S2803 (post-merge + close-cascade) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **104 rows** |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ❌ persistence unreliable for natural phrasing (P0 for S2804) |
| Frontend `/legal` | ✅ Draft flow live; ⚠️ result invisibility for natural phrasing (same P0) |
| Next move | Phase 3.1 P0 (agent reliability) per S2803 close ratification |

---

## Recommended session-open protocol (S2804)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2803 handoff §2 (P0 carry-forward) + §3 (novel-precedent moments) + §7 (Phase 3.1 scope)
4. **Read `core/agents/legal/legal_doc_drafter_agent.py:1180-1290`** (execute() flow — where GPT tool_call is consumed; where the persistence gap lives)
5. **Read `core/agents/legal/legal_doc_drafter_agent.py:1343-1500`** (_build_legal_prompt — tool-steering prompt)
6. **Read `core/tasks.py:5716-5780`** (draft_legal_document_task terminal-state update — my Phase 3.0 addition)
7. **Freshness + ledger 104 verify** — see S2804 open sequence above
8. **REPRODUCE THE BUG FIRST** — dispatch a natural drafting request via PA or curl, wait 5 min, verify `LegalDocumentDispatchLog` shows completed + resulting_document=None. Without a live reproduction, you can't verify the fix.
9. If `staleness_verdict != FRESH` → escalate
10. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
11. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
12. **Default candidate: Phase 3.1 P0 agent reliability**
13. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
14. Chris directs S2804 P0 selection (Phase 3.1 P0 unless override)
15. Mint fresh pin scoped `s2804-colorado-family-law-phase3.1-agent-reliability`
16. Route Phase 3.1 scope through Rigby joint SIGN before authoring
17. **Non-negotiable regression test:** dispatch natural-user phrasing (Chris's `"Draft a motion to modify visitation to every weekend from every other weekend"`) → assert `LegalDocument` row created. Without this, Phase 3.1 P0 fix cannot ship.
18. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
19. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
20. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2804:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md`](docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md) — **S2803 handoff (current)**
3. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — Phase 3.1 P0 target (7,829 lines; execute() at 1130; _save_legal_document at 2217; _detect_denied_motion_mode at 2503)
4. [`core/models_legal_audit.py`](core/models_legal_audit.py) — S2803 new — `LegalDocumentDispatchLog` compliance-audit model (P0 diagnosis surface)
5. [`core/services/legal_dispatch.py`](core/services/legal_dispatch.py) — S2803 new — shared dispatch helper
6. [`core/views_legal.py`](core/views_legal.py) — 2 S2803 new endpoints at end of file
7. [`core/tasks.py`](core/tasks.py) — `draft_legal_document_task` at 5716 (S2803 completion update)
8. [`frontend/src/pages/LegalPage.tsx`](frontend/src/pages/LegalPage.tsx) — S2803 draft modal + disclaimer + polling
9. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
11. [`docs/handoffs/SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md`](docs/handoffs/SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md) — S2802 predecessor
12. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 104 rows at S2803 close

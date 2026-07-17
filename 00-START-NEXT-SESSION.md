# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2804 CLOSED — Colorado Family Law Phase 3.1 P0 + 3.1a SHIPPED (Phase 3.1 P1 unification is S2805 default; Phase 4a form-selection is NEW Chris-raised arc)

**Refreshed 2026-07-17 (SESSION 2804 CLOSED — eighth consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804). Phase 3.1 P0 shipped (PR #3224 `007054b1b`) — two-layer defense (forced tool_choice + fallback save) fixes the S2803 close-of-session bug where dispatch completed but no LegalDocument persisted for natural-user phrasing; 12 tests, 0.924s. Phase 3.1a shipped (PR #3225 `d84f2079f`) — view-document modal on LegalPage after Chris live-browser reported "document is created but I don't have a way to view it on the UI"; landed the Rigby Fold 3 anticipated "Auto-recovered draft" badge early. NEW arc-level requirement raised by Chris mid-Phase-3.1: **form-selection intelligence** (user describes situation → agent picks correct JDF form + procedural knowledge) — sized as standalone **Phase 4a candidate**, queued behind P1 unification. FORTYEIGHTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2804 ships (2 PRs, both merged with --admin):**

| Phase | PR | Merged to | Focus |
|---|---|---|---|
| 3.1 P0 | **#3224** · `007054b1b` | main | Two-layer defense: BaseAgent tool_choice threading + LegalDocDrafterAgent _classify_task_intent (verb+noun + denylist) + forced tool_choice + Layer B fallback save with recovery marker |
| 3.1a | **#3225** · `d84f2079f` | main | View-document modal on LegalPage; clicks any doc row → full content + "Auto-recovered draft" badge + copy-to-clipboard |

**Handoff:** `docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **108 rows** (rows 105-108 Phase 3.1 P0 folds).

**Arc state:** Colorado Family Law — Phases 0/1/2/2.1/3.0/**3.1 P0**/**3.1a** ✅; Phase 3.1 P1 = CaseProfile unification (S2805 default); Phase 3.2 = case wizard; Phase 4a = form-selection intelligence (NEW); Phase 4 = statute-citation quality; Phase 5 = spider beat schedule.

---

## SESSION-OPEN INFRA STORY (S2804)

**First same-session end-to-end substrate + UX regression + UI-fix loop.** Chris browser-tested Phase 3.1 P0 immediately after merge → surfaced "can't view" gap → 30-min Phase 3.1a fix shipped + merged same session. Session-local browser verification (introduced at S2803 close) is now paying compounding dividends.

**First arc where Rigby SIGN Fold anticipated a future badge that landed early.** Fold 3 (Phase 3.1 P0 SIGN) said `phase3_1_fallback_used` should surface via Phase 3.5 "Auto-recovered draft" badge. Phase 3.1a's view modal shipped that badge ~1 hour after the fold was written because the data marker already existed. Novel: **future_trigger fold shortened to same-session actionable when the enabling substrate landed sooner than expected.**

**Two-layer defense pattern (forced choice + fallback) proved out.** Both layers shipped in the same PR per Rigby recommendation. Codification candidate: **"GPT-mediated flow reliability = forced-tool + fallback-synthesizer + measurement-marker."** Pattern reusable for any GPT-mediated flow where output shape reliability matters.

**First mid-execution scope-addition without derailing in-flight work.** Chris raised form-selection requirement mid-Phase-3.1 P0 test-writing. Acknowledged → continued to green on P0 → flagged in PR body + handoff → preserved momentum. Contrast with prior sessions where mid-arc scope changes have paused progress.

---

## S2805 CANDIDATES — PHASE 3.1 P1 IS THE DEFAULT

### ⭐ Phase 3.1 P1 — CaseProfile/LegalCase unification (default candidate)

**Ratified at S2803 open:** unify around `CaseProfile` (richer model with case_number, court, district, division, parties as first-class rows). Deprecate `LegalCase` eventually.

**Scope:**
1. Add nullable `LegalDocument.case_profile` FK to `CaseProfile` — new migration
2. Backfill (only 2 known rows: Phase 0 test doc `475d83a1…` + Chris's Phase 3.1 P0 test docs)
3. Refactor `LegalDocDrafterAgent._save_legal_document` at `legal_doc_drafter_agent.py:2217-2330` to bind `case_profile` (not `case=LegalCase`)
4. Deprecate `LegalCase.case` FK (leave nullable for grandfathered rows; do NOT drop yet)
5. Regression tests

**Non-goals:**
- Do NOT drop `LegalCase` model this PR (grandfathered rows still reference it)
- Do NOT touch the case wizard (Phase 3.2, blocked on this)

### Phase 3.2 — Case creation wizard (blocked on P1)

`POST /api/legal/case-profiles/` create endpoint + wizard modal on `LegalPage` + wire draft dispatch to link to active case.

### ⭐ Phase 4a (NEW) — Form-selection intelligence

**Chris raised this mid-Phase-3.1 P0 (2026-07-17):**

> "not only fill out the form but know what form to file when it's needed and not just guessing. So if I need to file a motion for emergency services I need to be able to explain the issue and the Agent know which form to fill out and how to do it"

**Requirement:** user describes situation in plain language → agent picks correct JDF form + procedural knowledge (fee, filing location, hearing schedule, service requirements).

**Existing substrate to build on:**
- `_draft_motion` tool has `motion_type` enum: `continuance, modify_parenting_time, modify_child_support, enforce_order, reconsideration, other` — **incomplete for real Colorado family law practice** (missing emergency, protection order, restraining, contempt, etc.)
- `JDF_FORM_MAPPING` in `legal_doc_drafter_agent.py` — narrow scope; needs expansion
- `_get_form_info` / `_get_curated_family_law_resources` from Colorado spider — potential knowledge source

**Sized as standalone arc.** Not blocking P1 unification. Chris may re-prioritize.

### Phase 4 — Statute-citation content quality

C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language.

### Phase 5 — Spider beat schedule

Monthly refresh for `colorado_family_law_spider`.

### Alternate candidates

- **Small follow-up PRs owed:**
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening (Phase 2 punt)
  - `LegalDocument.generation_context` add `blank=True` (Phase 2 model quirk)
  - PA→Celery E2E integration test (Rigby Phase 2 SIGN Fold 4)
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split into `agents/legal/` submodules (Rigby Phase 2 SIGN Fold 3)

- **Group 2700 docs restructuring arc** (still queued since S2801; blocked behind Colorado arc)
- **BettingPage first-user trace** (pre-Colorado default)
- **Stock Intelligence** (first non-betting revenue play)

---

## SESSION PIN — S2804 RETIRED (fresh mint required at S2805 open)

**Pin history (S2804):**

- `pa-c8b5f2dc9d344c78` (label `s2804-colorado-family-law-phase3.1-agent-reliability`) minted S2804 open; **retired at S2804 close (`force=true`, thirtyfifth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-c8b5f2dc9d344c78` (retired)** — intended failure mode forces S2805 first-action fresh mint.

**S2805 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2804 handoff — §2 (NEW Phase 4a candidate + Chris quote) + §3 (novel-precedent moments) + §7 (Phase 3.1 P1 scope)
# Read core/agents/legal/legal_doc_drafter_agent.py:2217-2330 (_save_legal_document — Phase 3.1 P1 refactor target)
# Read core/models_legal.py CaseProfile (lines 15-100) + core/models_unified_system.py:17114 LegalCase + :17252 LegalDocument
# Read frontend/src/pages/LegalPage.tsx — Cases tab (blocked on P1) + view modal (Phase 3.1a landed)

# Freshness check
bash tools/pa_local.sh "S2805 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 108-row baseline survived S2804 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==108, r
print('OK — 108 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to Phase 3.1 P1
python manage.py session_lifecycle open --label s2805-colorado-family-law-phase3.1-p1-unification

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2805 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2804 lessons to carry:**

1. **Session-local browser verification is a P0 pattern** — Chris testing Phase 3.1 P0 immediately after merge caught the "can't view" gap same-session. Add browser-verify to close-cycle for user-facing arcs.
2. **Two-layer defense (forced + fallback) for GPT-mediated flows** — codification candidate. Reusable for any output-shape-reliability problem.
3. **Future_trigger folds can land early when substrate readies** — Fold 3 badge was future-tagged for Phase 3.5; landed in Phase 3.1a because the data marker existed. Don't over-defer.
4. **Mid-execution scope-additions can be acknowledged without derailing** — pattern: acknowledge → flag in PR body + handoff → continue to green → preserve momentum.
5. **`_save_legal_document` fixed-key generation_context is under-designed for extension** — needed inline patch for `phase3_1_fallback_used` marker. Broader refactor (accept `extra_context` dict) is a Phase 3.5 candidate when trace-logging lands.

---

## Twin-pointer card

📁 **Repo — S2804 artifacts:**

- **PRs (2, merged):** #3224 (Phase 3.1 P0 · `007054b1b`) + #3225 (Phase 3.1a · `d84f2079f`)
- **Substrate changes:** `core/agents/base_agent.py` (tool_choice param) + `core/agents/legal/legal_doc_drafter_agent.py` (classifier + Layer A + Layer B + marker propagation in `_save_legal_document`) + `frontend/src/pages/LegalPage.tsx` (view modal)
- **Test file (new):** `core/tests/test_legal_agent_drafting_reliability.py` (12 tests, 0.924s)
- **Handoff:** `docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **108 rows**
- **Merge SHAs:** `007054b1b` (Phase 3.1 P0) → `d84f2079f` (Phase 3.1a) → close-cascade filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — Legal Assistant page. Dispatch reliably produces viewable `LegalDocument`. Click any doc row → modal with full content + "Auto-recovered draft" badge if fallback fired.
- **Chris live-verified end-to-end** at S2804 close.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2804 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a ✅; Phase 3.1 P1 NEXT (S2805) |
| NEW arc candidate | Phase 4a form-selection intelligence (Chris mid-execution requirement) |
| Group 2700 docs arc | Still queued (blocked behind Colorado arc) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-c8b5f2dc9d344c78` (retired at S2804 close, force=true, thirtyfifth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-c8b5f2dc9d344c78` (retired; forces fresh mint at S2805 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2804 open |
| Recycle log | `logs/recycle_events.jsonl` — +3 events during S2804 (2 post-merge + 1 close-cascade) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **108 rows** |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable (Phase 3.1 P0 two-layer defense); ✅ visible in UI (Phase 3.1a modal) |
| Frontend `/legal` | ✅ Draft + view flow both live |
| Next move | Phase 3.1 P1 (CaseProfile unification) per S2804 close ratification |

---

## Recommended session-open protocol (S2805)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2804 handoff §2 (NEW Phase 4a candidate + Chris quote) + §3 (novel-precedent moments) + §7 (Phase 3.1 P1 scope)
4. **Read `core/agents/legal/legal_doc_drafter_agent.py:2217-2330`** (`_save_legal_document` — Phase 3.1 P1 refactor target for `case=LegalCase → case_profile=CaseProfile`)
5. **Read `core/models_legal.py` `CaseProfile`** (lines 15-100) — the model to unify around
6. **Read `core/models_unified_system.py:17114` `LegalCase`** + `:17252` `LegalDocument` — what's being deprecated + the FK to migrate
7. **Read `frontend/src/pages/LegalPage.tsx`** Cases tab (~line 332-383) — currently shows CaseProfile rows but "New Case" is stub; wire will happen in Phase 3.2 after P1 lands
8. **Freshness + ledger 108 verify** — see S2805 open sequence above
9. If `staleness_verdict != FRESH` → escalate
10. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
11. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
12. **Default candidate: Phase 3.1 P1 CaseProfile unification** (or Chris redirect)
13. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
14. Chris directs S2805 P0 selection
15. Mint fresh pin scoped `s2805-colorado-family-law-phase3.1-p1-unification`
16. Route Phase 3.1 P1 scope through Rigby joint SIGN before authoring
17. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
18. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
19. **Backfill discipline:** Phase 3.1 P1 will add nullable `case_profile` FK; only 2 known LegalDocument rows exist (`475d83a1…` + Chris's fallback doc); safe to script backfill inline in the migration
20. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2805:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md`](docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md) — **S2804 handoff (current)**
3. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — `_save_legal_document` at 2217-2330 (P1 refactor target); `_classify_task_intent` at 2500-2565 (Phase 3.1 P0 landing site)
4. [`core/models_legal.py`](core/models_legal.py) — `CaseProfile` (unify target)
5. [`core/models_unified_system.py`](core/models_unified_system.py) — `LegalCase` at 17114 (deprecate); `LegalDocument` at 17252 (FK migrate)
6. [`core/models_legal_audit.py`](core/models_legal_audit.py) — S2803 `LegalDocumentDispatchLog` (compliance-audit; Phase 3.5 trace-logging expansion target)
7. [`frontend/src/pages/LegalPage.tsx`](frontend/src/pages/LegalPage.tsx) — Phase 3.0/3.1a modals; Cases tab (Phase 3.2 target)
8. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
9. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
10. [`docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md`](docs/handoffs/SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md) — S2803 predecessor
11. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 108 rows at S2804 close

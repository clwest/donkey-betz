# Session 2808 — Colorado Family Law Phase 4a (Form-selection intelligence)

**Date:** 2026-07-17 (late-night close; tomorrow re-opens as S2809)
**Session:** S2808
**PRs shipped:** 1 — **PR #3233** (Phase 4a · `e2f33cecd8fd`)
**Predecessor:** [SESSION_2807 Phase 3.1 P1.b](SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +712 / −0 LOC across 7 files.**

### PR #3233 — Phase 4a: Form-selection intelligence

First user-facing intelligence surface of the Colorado arc. Adds a "Pick a Form" affordance on `/legal` that takes a plain-English situation description ("she moved to Denver with the kids without telling me") and returns the recommended JDF form plus alternates, criteria, required attachments, and filing notes.

**Anchor-verify insight that reshaped scope:** `JDF_FORM_MAPPING` (8 relief-type entries), `COLORADO_FAMILY_LAW_FORMS` (10 forms categorized), and `STATUTORY_CRITERIA` **already exist** in `core/agents/legal/legal_doc_drafter_agent.py:79-212` since Session 404, AND the catalog is already injected into the drafter's system prompt at `:1434-1441` (Session 1035). Phase 4a is therefore **not "build intelligence"** — it's "build the missing dedicated surface." Rigby SIGN Q4 formalized this as fold row 114 (`same_pr_actionable`); mitigation applied in-arc by scoping to (1) rule-based deterministic classifier — no LLM cost — and (2) treating `JDF_FORM_MAPPING` as read-only substrate.

**Backend:**
- `core/agents/legal/legal_doc_drafter_agent.py` — new `RELIEF_TYPE_KEYWORDS` module const (7 relief types with `primary` scored 3× and `signals` scored 1×); new `_recommend_form(situation, context=None)` method — pure function, no LLM, no DB writes; returns `{top_match, alternates (top 2), confidence (high/medium/low/none), clarifying_questions, disclaimer}`
- `core/views_legal.py` — `POST /api/legal/select-form/` DRF view (`IsAuthenticated`, no DB writes)
- `core/urls.py` — endpoint registered under existing legal URL block

**Frontend:**
- `frontend/src/lib/api.ts` — `legalApi.selectForm({situation, case_type?})` mutation
- `frontend/src/pages/legal/FormPickerModal.tsx` *(new, 280 LOC)* — self-contained modal component (props `{open, onClose}`) with textarea + optional case-type + result card + alternates + clarifying-question hints + disclaimer
- `frontend/src/pages/LegalPage.tsx` — new "Pick a Form" button in the header (next to "Draft New Motion") + modal render

**Tests (`core/tests/test_legal_form_selection.py`, new 170 LOC):**
- F1 — emergency phrasing → `emergency_parenting` + high/medium confidence
- F2 — modify parenting time phrasing → `JDF 1220`
- F3 — enforcement/contempt phrasing → `enforce_order`
- F4 — child support phrasing → `modify_child_support`
- F5 — ambiguous "help me with my case" → low/none confidence + clarifying questions
- F6 — empty situation → 400 error
- F7 — no keyword hit → `top_match=None` + confidence `'none'` + clarifying questions
- E1 — authenticated happy path → 200 + recommendation JSON
- E2 — missing situation → 400 + error
- E3 — unauthenticated → 401/403
- **Full legal suite: 71 tests OK in 202.83s** (61 pre-existing + 10 new)

---

## §2 — Rigby joint SIGN cycle

**Pin:** `pa-468038b5c9764cc3` (S2808 open-ceremony first-action fresh mint)
**Verdict:** **AGREE-WITH-EDITS** on all 4 questions (no F-BLOCKING deadlock; sent to Chris as joint recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`)

**Anti-rubber-stamp check:** **PASSED** — Rigby's `tool_runs` included multiple `repo_tool.read` invocations (form catalog at lines 79-100, JDF_FORM_MAPPING at 105-162, drafter prompt injection at 1434-1441, `_get_form_info` at 2002, view file) plus 3 `repo_tool.search` calls (`select-form`, `select_form`, `api/legal`) that confirmed no prior endpoint existed. Tool-grounded verification of every scope claim before signing.

**4 SIGN questions + verdicts:**

1. **Q1 (SHAPE): AGREE — Option C (UI-first).** Agent method + endpoint + LegalPage UI + tests; skip PA tool. Matches recent Phase 3.2 wizard pattern; avoids Celery worker restart cost for PA tool registration.
2. **Q2 (CLASSIFIER): AGREE — rule-based/keyword-match first.** Deterministic, testable, no LLM cost. Include "ambiguous → top-2 candidates + clarifying questions" fallback. GPT fallback deferred.
3. **Q3 (BLAST RADIUS): AGREE — `JDF_FORM_MAPPING` read-only.** The 5 existing internal consumers (drafting logic at lines 1435/5723/5797/6134/6341) untouched.
4. **Q4 (ZOOM-OUT): AGREE — Phase 4a is partially shipped.** Focus on missing surface + thin deterministic selector; avoid rebuilding LLM-based intelligence that already exists in the drafter's prompt injection path.

**1 zoom-out fold persisted (ledger row 114) per PLAYBOOK-6.10.8 (BEFORE Chris-facing recommendation), 6.10.9-compliant with stable-state-pointer SHA `3a774d19ed29` + file:line evidence + verified-state outcome inline:**

- Row 114 (`same_pr_actionable`) — Phase 4a redundancy risk: form catalog + statutory framework already exist AND are already injected into drafter system prompt. Rebuilding LLM-based situation intelligence would duplicate work. **Mitigation APPLIED IN-ARC** by scoping to Option C + rule-based keyword-match; JDF_FORM_MAPPING treated as read-only substrate.

**Persistence mechanism:** `python manage.py record_zoom_out_concern` (Claude Code); Rigby's tool surface remains read-only for `zoom_out_tool.list`.

---

## §3 — Novel-precedent moments

**A. First arc where Rigby's SIGN Q shape ("A/B/C — which shape?") drove the scope, not just refined it.** Prior arcs presented a single scope + folded edits into it. Phase 4a presented three shapes (A full-vertical / B chat-first / C UI-first) and let Rigby pick. She picked C (matching Phase 3.2 pattern) with reasoning grounded in Chris's prior sessions (regularly opens `/legal`, rarely chats Rigby for legal help). **Substrate lesson:** when scope has multiple valid shapes, ASK the shape as a menu — Rigby's grounded tool-runs can pick better than Claude's single default.

**B. First user-facing intelligence surface of the Colorado arc (not correctness or plumbing).** Previous arcs shipped correctness substrate (P0/P1/P1.b) + one wizard capability (Phase 3.2). Phase 4a is the first arc where the user does something intelligent through the platform — describes a situation and gets an actionable recommendation. Arc has crossed from "make things work" to "make things smart."

**C. First same-arc surface addition that was 100% additive (no touch to existing internal callers of the underlying data).** The 5 existing `JDF_FORM_MAPPING` internal consumers were explicitly left alone per Rigby SIGN Q3 (blast-radius discipline). Additive surface, not refactor.

**D. Twelfth-consecutive same-day multi-ship session** — S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → S2806 → S2807 → **S2808**. Multi-day run wraps here for the night; tomorrow's session opens as S2809 with the Colorado arc's correctness substrate closed + wizard live + form-selection live.

**E. Seventh-consecutive session where anchor-verify at open shaped scope.** S2807 handoff described Phase 4a as "user describes situation → agent picks form + procedural knowledge — verify JDF form catalog exists." Anchor-verify at S2808 open converted "verify catalog exists" into "catalog exists AND is already injected — scope reduces to standalone-surface." Trend line: anchor-verify is now the load-bearing step in scope framing, not a formality.

---

## §4 — Session-open infra story

**S2808 opened with S2807 pin retired.** Wrapper `tools/pa_local.sh` pointed at `pa-a6578b35e0244cea` (retired per S2807 close-cascade). First-action fresh mint: `pa-468038b5c9764cc3` labeled `s2808-colorado-family-law-phase4a-form-selection`. Freshness FRESH · head `3a774d19ed29` · 0/5 stale workers. Ledger 113 rows verified at open (45 same_pr_actionable + 39 same_pr_mitigatable + 29 future_trigger).

**Code anchor sweep (before Rigby SIGN dispatch):**

- `COLORADO_FAMILY_LAW_FORMS` at `legal_doc_drafter_agent.py:79-100` — 10 forms across 4 categories (`divorce_with_children`, `parenting`, `child_support`, `general`)
- `JDF_FORM_MAPPING` at `:105-162` — 8 relief types with `{primary_form, official_title, required_attachments, criteria, filing_notes}` (Session 404 addition)
- `STATUTORY_CRITERIA` at `:167-212` — 3 statutory categories with `required_elements` + `best_interest_factors` + `NOT_sufficient` guardrails
- Catalog injection into system prompt at `:1434-1441` (Session 1035) — GPT already sees form data during drafting
- 5 existing internal consumers of `JDF_FORM_MAPPING` (lines 1435 injection + 5723/5797/6134/6341 drafting logic)
- `_get_form_info` at `:2002` — reverse-direction lookup (form-number → description); different pattern from what Phase 4a needs
- Zero existing `select-form` / `select_form` / `/api/legal/select-form/` — confirmed via `repo_tool.search` (Rigby)
- Zero PA tool for form-lookup in dispatcher — confirmed via grep

**Test iteration:** Single-shot to green. `pytest core/tests/test_legal_form_selection.py` = 10/10 first run. Full legal suite 71 tests OK.

**Frontend build:** `npm run build` clean (2290 modules, 3.46s). `make frontend-ship` deployed cleanly (`index-BR0blsIo.js` serves). Bundle grep-verified: `"Pick the right JDF form"` and `"select-form"` both present.

---

## §5 — Twin-pointer card

📁 **Repo — S2808 artifacts:**

- **PR (1, merged):** #3233 (Phase 4a · `e2f33cecd8fd`)
- **Substrate changes:**
  - `core/agents/legal/legal_doc_drafter_agent.py` — `RELIEF_TYPE_KEYWORDS` (7 entries) + `_recommend_form` method
  - `core/views_legal.py` — `select_legal_form` DRF view
  - `core/urls.py` — endpoint registered
  - `frontend/src/lib/api.ts` — `legalApi.selectForm`
  - `frontend/src/pages/legal/FormPickerModal.tsx` — **new** 280-LOC self-contained modal
  - `frontend/src/pages/LegalPage.tsx` — button + modal render
- **Test files:** `core/tests/test_legal_form_selection.py` (**new**, 170 LOC, 10 tests)
- **Handoff:** `docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (row 114 P4a fold: redundancy risk `same_pr_actionable`, mitigated in-arc)
- **Merge SHA:** `e2f33cecd8fd` (Phase 4a) → close-cascade filled at cascade PR merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — new "Pick a Form" button in the page header. Click → modal → describe situation → recommendation card renders with confidence badge, form number/title, criteria, required attachments, filing notes, alternates (top 2), and clarifying questions if confidence is low.
- **Twin workspace deliverable:** N/A this session; substrate ships directly (feature ship, not a ratifiable engineering artifact).

---

## §6 — Next session (S2809, fresh day) — candidates

**Colorado arc state at S2808 close:**
- All backend correctness substrate closed (P0, P1, P1.b)
- One case-management capability shipped (Phase 3.2 wizard)
- One user-facing intelligence surface shipped (Phase 4a form-selection)
- 12 consecutive same-day multi-ships (S2797 → S2808)

### Candidates for S2809

**Small / mechanical:**
- **P1-back-port test hardening**: retrofit T6b (LegalDocument path) with `assertLogs('WARNING')` to codify S2805 Lesson 3 observably (matching T7b delta shipped at S2807). Small; ~30 LOC.
- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **`LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening** (Phase 2 punt)

**Medium:**
- **Phase 4 — Statute-citation content quality**: C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language quality
- **Phase 5 — Spider beat schedule**: monthly refresh for `colorado_family_law_spider`
- **Attorney sub-form on Case Wizard** when `!is_pro_se` (row-112 emergent from Phase 3.2)
- **GPT fallback for form-selection** when keyword-match is low-confidence (row-114 emergent from Phase 4a)

**Large:**
- **Phase 4b — LLM-based situation intelligence** (upgrade Phase 4a rule-based classifier with GPT for ambiguous descriptions; possibly consolidate with the drafter's existing prompt-injection path)
- **Wizard extraction to `/legal/cases/new` route** (row-112 emergent; triggers: deep-link, draft-persistence, browser-back)
- **7,829-line `legal_doc_drafter_agent.py` mechanical split** into `agents/legal/` submodules

**Non-Colorado arcs (still queued):**
- **Group 2700 docs restructuring arc** (queued since S2801)
- **BettingPage first-user trace** (pre-Colorado default)
- **Stock Intelligence** (first non-betting revenue play)

**Recommended default:** Chris picks direction fresh at S2809 open. The Colorado arc has natural "next" candidates in every size class; no scope pressure to continue one over another. If Chris wants a low-friction warm-up shipping small-and-clean, **P1-back-port test hardening** is the tightest.

---

## §7 — Cross-day resume notes (S2808 → S2809)

Since Chris is closing for the night and re-opening tomorrow morning:

**Overnight state to expect on re-open:**
- Local `postgresql@15` (July DB) is `brew launchd started` — should survive overnight unless macOS reboots. If freshness check fails at S2809 open, check `brew services list | grep postgres` FIRST per `feedback_post_travel_port_collision_triage` (fossil pg16 could grab port).
- Daphne, Celery, Redis all started by S2808 close-cascade `make recycle-all`; may still be running tomorrow. If not, `make restart` re-brings them up.
- Session pin `pa-468038b5c9764cc3` retired; wrapper still points at it (intended failure mode — first S2809 action mints fresh).
- Zoom-out ledger at 114 rows; freshness log has +1 from S2808 open; recycle log has +2 from S2808 (post-merge + close-cascade).
- HEAD advances at close-cascade PR merge (this document commits to `docs/s2808-close-cascade` branch → PR → merge → HEAD advances).

**Bootstrap sequence tomorrow (S2809):**

```
context-kit orient

# Read 00-START-NEXT-SESSION.md end-to-end
# Read this file (S2808 handoff) §3 (novel-precedent), §6 (S2809 candidates), §7 (cross-day notes)

# Freshness — first Rigby dispatch will fail because wrapper points at retired pin
# Immediately mint fresh:
python manage.py session_lifecycle open --label s2809-<Chris's-chosen-direction>

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

# If services aren't running: make restart
# If freshness FRESH: proceed to Chris's direction
```

---

## §8 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Open ceremony + refined P4a scope acknowledged ("yes proceed with Option C")
- Merge P4a after joint SIGN with all 4 Rigby AGREE verdicts + row-114 mitigation ("merge it")
- Close-cascade S2808 → ratified inline via close-ceremony execution ("Let's wrap up for the night and pick up again tomorrow. Make sure everything is updated and cascaded")

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** GPT fallback for form-selection (row-114 trigger); attorney sub-forms on wizard (row-112 trigger); wizard-route extraction (row-112 trigger); P1-back-port test hardening (S2807 lesson); Phase 4b LLM upgrade (P4a natural progression).

**Sleep well; S2809 is ready.**

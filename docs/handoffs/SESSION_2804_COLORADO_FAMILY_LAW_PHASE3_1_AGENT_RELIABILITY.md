# Session 2804 — Colorado Family Law Phase 3.1 (agent drafting reliability + view modal)

**Date:** 2026-07-17
**Session:** S2804
**PRs shipped:** 2 — **PR #3224** (Phase 3.1 P0 · `007054b1b`) + **PR #3225** (Phase 3.1a · `d84f2079f`)
**Predecessor:** [SESSION_2803 Phase 3.0 frontend](SESSION_2803_COLORADO_FAMILY_LAW_PHASE3_FRONTEND.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 2 post-PR clean recycles + 1 close-cascade recycle

---

## §1 — Ship summary

**Two PRs shipped, both merged with `--admin`. +539 / −13 LOC across 4 files.**

### PR #3224 — Phase 3.1 P0: agent drafting reliability (two-layer defense)

Fixes the S2803 close-of-session live-browser bug: dispatch completed but no `LegalDocument` persisted for natural-user phrasing.

**Layer A — Classifier + forced tool_choice:**
- `BaseAgent._call_openai` gained optional `tool_choice=None` param (backward-compat; default preserves `"auto"`). Pattern precedent verified at `core/agents/business/base_business_research_agent.py:215-248` (not net-new for codebase).
- New `LegalDocDrafterAgent._classify_task_intent(task, context) → (intent, target)` requires **verb+noun** co-occurrence (drafting verbs: draft/write/generate/create/prepare/compose; document nouns: motion/email/declaration/letter/meet-and-confer). Info-phrase denylist (`'deadline', 'what is', 'how do I', 'where do I file', …`) overrides even verb+noun matches per Rigby Fold 1.
- `execute()` forces `tool_choice={'type':'function','function':{'name':f'draft_{target}'}}` when intent is HIGH-confidence drafting.

**Layer B — Fallback save (safety net):**
- After the tool-call loop, if `intent=='drafting'` AND `documents_generated == 0` AND response has content, synthesize a `motion` document + save via `_save_legal_document`.
- Fallback docs tagged with `generation_context.phase3_1_fallback_used=True` (Rigby Fold 3 anticipates Phase 3.5 "Auto-recovered draft" badge + fallback-rate telemetry when trace-logging arc opens).
- `motion_type='other'` (Fold 2 — don't mislabel a specific motion type we didn't actually classify).
- Warning logged so ops can measure fallback rate today.

**Tests (12 in `core/tests/test_legal_agent_drafting_reliability.py`, 0.924s):**
- T2a-f — classifier truth table (Chris regression phrasing, noun-only info, denylist, ambiguous, email, declaration)
- T3/T3b — `BaseAgent._call_openai` `tool_choice` propagation + default preserves `"auto"`
- T1 — Chris end-to-end regression: content-only GPT → `LegalDocument` row + `phase3_1_fallback_used=True`
- T4 — fallback fires for drafting + no doc
- T5/T5b — fallback does NOT fire for info or unknown

### PR #3225 — Phase 3.1a: view-document modal

Fixes the visibility gap Chris hit right after Phase 3.1 P0 landed: drafts now persist reliably, but there was no way to READ the content in the UI. Documents tab showed metadata only; click did nothing.

- Frontend-only change; reuses existing `GET /api/legal/case-files/<id>/` endpoint
- Click any document row (Overview OR Documents tab) → modal opens with full content
- Modal badges: type, status, word_count, created_at, and **"Auto-recovered draft"** when `generation_context.phase3_1_fallback_used === true` (landing the Rigby Fold 3 anticipated badge early since the marker exists in the data)
- Copy-to-clipboard button
- Content rendered as `<pre>` preserving newlines + spacing (Colorado motions have structured whitespace that matters)

---

## §2 — NEW arc-level requirement — Phase 4a candidate

**Chris mid-execution during Phase 3.1 P0 build (2026-07-17):**

> "not only fill out the form but know what form to file when it's needed and not just guessing. So if I need to file a motion for emergency services I need to be able to explain the issue and the Agent know which form to fill out and how to do it"

**This is a NEW arc-level requirement, not addressed by Phase 3.1 P0 or 3.1a.** Current classifier only maps to broad type (motion/email/declaration). Chris's requirement is finer:

1. **Form selection** — user describes situation in plain language → agent picks the correct JDF form (e.g. JDF 1420 emergency vs JDF 1109 standard modification vs JDF 1401 support)
2. **Procedural knowledge** — not just the form but HOW to file (fee, filing location, hearing schedule, service requirements)
3. **Situation understanding** — the agent must comprehend real-world urgency signals ("emergency", "immediate", "restrain") and severity ("modify", "adjust") to pick correct forms

Existing substrate that Phase 4a can build on:
- `_draft_motion` tool has `motion_type` enum: `continuance, modify_parenting_time, modify_child_support, enforce_order, reconsideration, other` — **incomplete for real Colorado family law practice**
- `JDF_FORM_MAPPING` in the agent already exists but is scoped narrowly (see `_build_legal_prompt:1367`)
- `_get_form_info` / `_get_curated_family_law_resources` from Colorado spider — could be repurposed as a knowledge source

**Sized as standalone Phase 4a arc.** Not blocking, not urgent enough to derail Phase 3.1 P1 unification. Chris will use platform for real cases regardless of form-selection intelligence; today's fallback creates a "motion (other)" doc that Chris can edit manually. Phase 4a raises the ceiling from "generic template" to "Colorado-appropriate form".

Ordering recommendation for post-3.1 arcs: **3.1 P1 (unification) → 3.2 (case wizard) → 4a (form selection) → 4 (statute citation) → 5 (spider beat)**. Chris may re-order — the P0-blocking-nothing has been shipped.

---

## §3 — Novel-precedent moments

**A. First same-session end-to-end substrate + UX regression + UI-fix loop.** Chris browser-tested Phase 3.1 P0 immediately after merge → surfaced the "can't view" gap → 30-min Phase 3.1a fix shipped + merged in the same session. Contrast with prior sessions where UI gaps carried to next session. Session-local browser verification (started at S2803 close) is now paying off.

**B. First arc where Rigby SIGN Fold anticipated a future badge that landed early.** Fold 3 (Phase 3.1 P0 SIGN) said `phase3_1_fallback_used` should surface via Phase 3.5 "Auto-recovered draft" badge. Phase 3.1a's view modal shipped that badge already (~1 hour after the fold was written) because the data marker already exists. Novel: **future_trigger fold shortened to same-session actionable when the enabling substrate landed sooner than expected.**

**C. Two-layer defense pattern (forced choice + fallback) proved out.** Layer A (forced tool_choice) is the primary fix; Layer B (fallback save) is the safety net. Both were shipped in the same PR per Rigby recommendation. The pattern is reusable for any GPT-mediated flow where output shape reliability matters — codification candidate: **"GPT-mediated flow reliability = forced-tool + fallback-synthesizer + measurement-marker."**

**D. First mid-execution scope-addition without derailing in-flight work.** Chris raised the form-selection requirement mid-Phase-3.1 P0 test-writing. I acknowledged, continued to green on P0, flagged the requirement in the PR body + handoff, and preserved momentum. Contrast with sessions where mid-arc scope changes have paused progress.

**E. Eighth-consecutive same-day multi-ship session** — S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804. Discipline held through UI + backend + tests + close-cascade repeatedly.

---

## §4 — Rigby joint SIGN (Phase 3.1 P0 only; 3.1a shipped without SIGN)

**Phase 3.1 P0 SIGN:** SIGN-WITH-EDITS. Rigby tool_runs non-empty (6+ real `repo_tool` reads verifying 5 pre-authoring asks). Anti-rubber-stamp check PASSED. Substantive discovery: pattern precedent for `_call_openai_with_retry(..., tool_choice=..., ...)` exists at `core/agents/business/base_business_research_agent.py:215-248` — my BaseAgent extension is consistent with existing internal discipline, not alien.

**4 zoom-out folds persisted (rows 105-108):**

1. `same_pr_actionable` — false-positive intent classification (drove verb+noun requirement + info-phrase denylist)
2. `same_pr_mitigatable` — fallback mislabeling (drove `motion_type='other'` + high-confidence-only)
3. `future_trigger` — silent success mask (Phase 3.5 needs badge + fallback-rate telemetry; Phase 3.1a landed the badge early via view-modal marker)
4. `same_pr_mitigatable` — BaseAgent signature blast radius (drove backward-compat default + T3b test)

**Phase 3.1a:** No dedicated SIGN cycle. Small pure-UI change; reuses existing backend endpoint; landed Fold 3 badge early. Shipped directly per Chris approval.

---

## §5 — Session-open infra story

**S2804 opened with S2803 pin retired.** Wrapper pointed at `pa-d736030d6de844be` (retired). First-action fresh mint: `pa-c8b5f2dc9d344c78` labeled `s2804-colorado-family-law-phase3.1-agent-reliability`. Freshness FRESH · SHA-match `ef8517b365e0` at S2803 close-cascade; 0/5 stale workers.

**Test iteration (2 iterations to green for Phase 3.1 P0):**
1. First run: 11/12 pass, 1 failure — T1 recovery marker assertion failed because `_save_legal_document` builds `generation_context` from a fixed key set (didn't preserve arbitrary context flags).
2. Fix: patched `_save_legal_document` to include `phase3_1_fallback_used` in `generation_context` when present in either `document` dict or `context` dict.
3. Second run: 12/12 pass, 0.924s.

Root cause pattern: **`_save_legal_document` was under-designed for extension** — arbitrary metadata flags couldn't propagate. Patched inline for the marker Phase 3.1 needs; broader refactor (e.g. accept `extra_context` dict) is a candidate for Phase 3.5 when trace-logging lands and richer per-doc context becomes routine.

---

## §6 — Twin-pointer card

📁 **Repo — S2804 artifacts:**

- **PRs (2, both merged):** #3224 (Phase 3.1 P0 · `007054b1b`) + #3225 (Phase 3.1a · `d84f2079f`)
- **Substrate changes:** `core/agents/base_agent.py` (`_call_openai` tool_choice param) + `core/agents/legal/legal_doc_drafter_agent.py` (`_classify_task_intent` + forced tool_choice + Layer B fallback + `_save_legal_document` marker propagation) + `frontend/src/pages/LegalPage.tsx` (view modal)
- **Test files (1 new):** `core/tests/test_legal_agent_drafting_reliability.py` (12 tests, 0.924s)
- **Handoff:** `docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **108 rows** (rows 105-108 Phase 3.1 P0 folds)
- **Merge SHAs:** `007054b1b` (Phase 3.1 P0) → `d84f2079f` (Phase 3.1a)

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — Legal Assistant page: disclaimer banner + "Draft New Motion" button + Documents tab with clickable rows opening full-content modal. Fallback-generated docs show "Auto-recovered draft" badge.
- **Chris live-verified:** dispatch now reliably produces a viewable `LegalDocument`.
- **Live P0 bug from S2803 close:** was `LegalDocumentDispatchLog f41d9090…` with `resulting_document=None`. NOW FIXED — subsequent dispatches produce a doc every time.

---

## §7 — Next session (S2805) — Phase 3.1 P1 default

**Chris ratified at S2804 close:** close-cascade S2804 → Phase 3.1 P1 (unification) as S2805 P0 default. Phase 4a (form selection) queued behind — the P0-blocking-nothing has been shipped, so ordering discipline holds.

### Phase 3.1 P1 — CaseProfile/LegalCase unification (S2805 P0 default)

Ratified at S2803 open: unify around `CaseProfile` (the richer model with case_number/court/division/parties). Deprecate `LegalCase` eventually.

**Scope:**
1. Add nullable `LegalDocument.case_profile` FK to `CaseProfile`
2. Backfill (only 2 known rows: Phase 0 test doc `475d83a1…` + Chris's Phase 3.1 P0 test doc)
3. Refactor `LegalDocDrafterAgent._save_legal_document` to bind `case_profile` (not `case=LegalCase`)
4. Deprecate `LegalCase.case` FK (leave nullable for grandfathered rows)
5. Add regression tests

### Phase 3.2 — Case creation wizard (blocked on P1)

`POST /api/legal/case-profiles/` create endpoint + wizard modal on `LegalPage` + wire draft dispatch to link to active case.

### Phase 4a (NEW) — Form-selection intelligence

Chris's mid-Phase-3.1 requirement. User describes situation → agent picks correct JDF form + procedural knowledge. Standalone arc; not urgent enough to derail P1/3.2 ordering unless Chris re-prioritizes.

### Phase 4 — Statute-citation content quality

C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language for common Colorado family motions.

### Phase 5 — Spider beat schedule

Monthly refresh for `colorado_family_law_spider`.

### Standing follow-ups

- Small PRs owed:
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening (Phase 2 punt)
  - `LegalDocument.generation_context` add `blank=True` (Phase 2 model quirk)
  - PA→Celery E2E integration test (Rigby Phase 2 SIGN Fold 4)
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split (Rigby Phase 2 SIGN Fold 3)

- Group 2700 docs restructuring arc (still queued from S2801; blocked behind Colorado arc)
- BettingPage first-user trace (pre-Colorado default)
- Stock Intelligence (first non-betting revenue play)

---

## §8 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Phase 3.1 P0 two-layer defense approved
- Route to Rigby SIGN before build → approved
- Approve all 3 SIGN edits (revised scope + keyword-first MVP + no schema change) → approved
- Merge + recycle Phase 3.1 P0 → approved (standing pattern)
- Phase 3.1a build after live-browser feedback → approved
- Merge + recycle Phase 3.1a → approved (standing pattern)
- Close-cascade S2804 → approved

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** Phase 4a form-selection intelligence (Chris mid-execution requirement).

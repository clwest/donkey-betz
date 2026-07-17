# Session 2806 — Colorado Family Law Phase 3.2 (Case-creation wizard)

**Date:** 2026-07-17
**Session:** S2806
**PRs shipped:** 1 — **PR #3229** (Phase 3.2 · `52fd9aa55`)
**Predecessor:** [SESSION_2805 Phase 3.1 P1](SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +524 / −10 LOC across 3 files (all frontend).**

### PR #3229 — Phase 3.2: Case-creation wizard on LegalPage

Wires the previously-placeholder "New Case" button on the Cases tab to a self-contained wizard modal that POSTs to `/api/legal/cases/` and then sets the resulting case as active via `/api/legal/active-case/`. Backend endpoints already existed (verified at session open — see §3 novel-precedent A); this arc adds only the frontend surface.

**Files (`feat/legal-phase-3-2-case-wizard` → main):**

- `frontend/src/lib/api.ts` — `legalApi.createCase(payload)` + `legalApi.setActiveCase(caseId)` mutations added (3 LOC delta)
- `frontend/src/pages/legal/CreateCaseWizardModal.tsx` — **new file, 439 LOC.** Self-contained modal; props `{open, onClose, onSubmit, submitting}` — page-agnostic per Rigby SIGN Fold C mitigation. Single long form with sections Case Info → Petitioner → Respondent → Children (optional, dynamic add/remove). Field-name discipline: `full_name` / `date_of_birth` / `zip_code` match backend DTO exactly.
- `frontend/src/pages/LegalPage.tsx` — wire "New Case" button; `handleCreateCase` runs `createCase` → `setActiveCase` sequence with retry-toast fallback if only set-active fails (Rigby SIGN edit 1); refresh `LegalCase` interface + Cases-tab rendering + Overview mini-list to use actual backend fields (`case_title` / `case_number` / `case_type_display` / `documents_count` / `children_count`) instead of non-existent `title` / `name` (Rigby SIGN edit 3 — fold-in bug fix).

**Build:** `npm run build` = 2290 modules OK; `make frontend-ship` deployed `index-vbHFIYDZ.js`; distinctive strings ("Representing self (pro se)", "Case created") grep-verified present in served bundle.

---

## §2 — Rigby joint SIGN cycle

**Pin:** `pa-3c492806c55149e9` (S2806 open-ceremony first-action fresh mint after S2805 pin `pa-b9dc1af5c7b04afd` retired)
**Verdict:** **SIGN-WITH-EDITS** (3 F-BLOCKING edits folded; no unresolved deadlock; sent to Chris as joint recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`)

**Anti-rubber-stamp check:** **PASSED** — Rigby returned non-empty `tool_runs` (4× `repo_tool.read` real invocations on `frontend/src/lib/api.ts`, `frontend/src/pages/LegalPage.tsx`, and `core/views_legal_cases.py` at both the create endpoint 1-221 and the active-case endpoint 600-641). Independently verified endpoint signatures, cases-list rendering, and API surface. No rubber-stamp signal.

**3 F-BLOCKING edits (all folded into scope):**

1. **Retry-toast pattern for split failure** — if `createCase` succeeds but `setActiveCase` fails, still invalidate `['legal-cases']` and toast "Case created — could not set as active. Select the case from the list to activate it." (Recoverable via manual selection; no lost work.)
2. **Field-name alignment (correctness)** — children payload uses `full_name` + `date_of_birth` (not `name` / `dob`); parties use `zip_code` (not `zip`). Backend contract at `core/views_legal_cases.py:99-169`.
3. **Cases-list display bug fix (fold-in)** — pre-existing bug: `LegalPage.tsx:494` rendered `legalCase.title || legalCase.name` neither of which exists in the backend list DTO. Updated to `case_title || case_number`; refreshed `LegalCase` interface; applied same fix to Overview mini-list.

**1 zoom-out fold persisted (ledger row 112) per PLAYBOOK-6.10.8 (BEFORE Chris-facing recommendation), 6.10.9-compliant with stable-state-pointer SHA `28a12303ef59` + file:line evidence + verified-state outcome inline:**

- Row 112 (`same_pr_mitigatable`) — LegalPage coupling: wizard modal lives on LegalPage.tsx alongside multiple tabs+mutations+toasts; deep-link (`/legal/cases/new`), draft persistence, browser-back are future extractions. **Mitigation applied in-PR** by placing `CreateCaseWizardModal` in its own file with page-agnostic props (`open` / `onClose` / `onSubmit` / `submitting`).

**Persistence mechanism:** `python manage.py record_zoom_out_concern` (Claude Code); Rigby's tool surface is read-only for `zoom_out_tool.list`.

---

## §3 — Novel-precedent moments

**A. Second consecutive arc where anchor-verify at session open collapsed handoff scope.** S2805 handoff §6 listed Phase 3.2 as "5-step scope: (1) verify or add POST endpoint (2) wizard modal (3) session write (4) frontend integration (5) tests." At S2806 open, live-read of `core/views_legal_cases.py:70-178` + `:618-641` confirmed both create + active-case endpoints already exist with full functionality (created Session 406). Refined scope collapsed step 1 entirely; steps 3+4 unified into a single mutation handler; step 5 became bundle-level string-grep verification since no frontend test framework exists yet. Fifth-consecutive session with substantial anchor-verify tightening (S2802 → S2803 → S2804 → S2805 → **S2806**).

**B. First fold-in fix ship where the pre-existing bug was flagged BY Rigby (not surfaced by Claude Code).** Cases-list display bug at `LegalPage.tsx:494` (`title || name` referencing non-existent fields) had been latent since the tab was authored. Rigby's tool-grounded review of the rendering vs. backend DTO caught it as SIGN edit 3, tagged as "fix while you're here." Substrate lesson: tool-grounded SIGN can promote latent pre-existing bugs into scope for adjacent PRs at zero additional user-facing coordination cost.

**C. Tenth-consecutive same-day multi-ship session** — S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → **S2806**. Streak now spans backend refactor + migration + frontend + P1 latent-bug-fix + frontend wizard shapes. First arc entirely in the frontend layer since the S2801 LandingPage arc.

**D. First time PR was 100% additive from a UX perspective** — Phase 3.2 unlocks a real user-facing capability (case creation) rather than continuing internal substrate refactor. Previous 9 sessions were all backend correctness (P0/P1/P1.b substrate) or narrow UI wiring (draft/view modals). Wizard is the first S2797-arc frontend deliverable that is a net-new user affordance.

---

## §4 — Session-open infra story

**S2806 opened with S2805 pin retired.** Wrapper `tools/pa_local.sh` pointed at `pa-b9dc1af5c7b04afd` (retired per S2805 close-cascade). First-action fresh mint: `pa-3c492806c55149e9` labeled `s2806-colorado-family-law-phase3.2-case-wizard`. Freshness FRESH · head `28a12303ef59` · 0/5 stale workers. Ledger 111 rows verified at open (44 same_pr_actionable + 38 same_pr_mitigatable + 29 future_trigger).

**Live-DB / endpoint anchor sweep (before Rigby SIGN dispatch):**

- `POST /api/legal/cases/` at `core/views_legal_cases.py:70-178` — accepts full case + petitioner + respondent + attorneys + children in one payload; requires authenticated user
- `POST /api/legal/active-case/` at `core/views_legal_cases.py:618-641` — writes `session['active_case_id']`
- `case_profiles_list` GET DTO at `:47-66` — returns `{id, case_number, case_type, case_type_display, case_title, county, state, status, status_display, petitioner_name, respondent_name, children_count, documents_count, created_at, updated_at}`
- `legalApi.cases()`/`activeCase()` present in `frontend/src/lib/api.ts:1551-1554` but NO `createCase`/`setActiveCase` mutations existed
- Cases tab "New Case" button at `LegalPage.tsx:470-476` was placeholder toast (`'Create case coming soon!'`)
- No wizard modal component existed anywhere in `frontend/src/`

**Build iteration:** Single-shot to green — no failing builds during authoring. `npm run build` clean; `make frontend-ship` deployed cleanly; served bundle grep-verified.

---

## §5 — Twin-pointer card

📁 **Repo — S2806 artifacts:**

- **PR (1, merged):** #3229 (Phase 3.2 · `52fd9aa55`)
- **Substrate changes:**
  - `frontend/src/lib/api.ts` — `legalApi.createCase` + `legalApi.setActiveCase` added
  - `frontend/src/pages/legal/CreateCaseWizardModal.tsx` — **new** self-contained wizard component
  - `frontend/src/pages/LegalPage.tsx` — wire button + create→set-active flow + fold-in fix for Cases-list rendering (Overview + Cases tab)
- **Handoff:** `docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **112 rows** (row 112 P3.2 fold: LegalPage coupling, `same_pr_mitigatable`)
- **Merge SHA:** `52fd9aa55` (Phase 3.2) → close-cascade filled at cascade PR merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — Cases tab "New Case" button now opens the wizard. Wizard submits create + active-case in one flow. Success toast; failure of set-active step surfaces recoverable message + case still appears in list.
- **Twin workspace deliverable:** N/A this session; substrate ships directly (feature ship, not a ratifiable engineering artifact per `feedback_twin_deliverable_at_every_ratification`).

---

## §6 — Next session (S2807) — candidates

**Standing follow-ups (unchanged from S2805 handoff §6):**

- **Phase 3.1 P1.b — LegalResearchResult unification** *(default candidate)*: `save_legal_research` at `core/models_unified_system.py:17612` still uses LegalCase-based `case_id` param with silent `DoesNotExist` swallowing. Same latent-bug class P1 just fixed for `LegalDocument`. Small PR; ships standalone.
- **Phase 4a — Form-selection intelligence** (Chris mid-Phase-3.1 requirement): user describes situation → agent picks correct JDF form + procedural knowledge.
- **Phase 4 — Statute-citation content quality**: C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language.
- **Phase 5 — Spider beat schedule**: monthly refresh for `colorado_family_law_spider`.
- **Small PRs owed** (from S2803/S2804):
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening (Phase 2 punt)
  - `LegalDocument.generation_context` add `blank=True` (Phase 2 model quirk)
  - PA→Celery E2E integration test (Rigby Phase 2 SIGN Fold 4)
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split (Rigby Phase 2 SIGN Fold 3)
- **Group 2700 docs restructuring arc** (queued from S2801)
- **BettingPage first-user trace** (pre-Colorado default)
- **Stock Intelligence** (first non-betting revenue play)

**New emerging candidate from Phase 3.2 ship:**

- **Wizard extraction to `/legal/cases/new` route** — deferred per row-112 mitigation. Trigger conditions per zoom-out fold: (i) deep-link demand, (ii) draft-persistence requirement, (iii) browser-back navigation friction. Not urgent; ship if any of the three surface.
- **Attorney fields in wizard** — MVP wizard defaults `is_pro_se=true` for both parties and omits attorney sub-forms. Backend accepts attorney nested data (`views_legal_cases.py:113-128, 147-160`). If Chris needs to enter opposing counsel via wizard rather than case-edit endpoint, add optional attorney sections gated on `!is_pro_se` toggle.

---

## §7 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Open ceremony + refined P3.2 scope acknowledged ("yes proceed with refined scope")
- Merge P3.2 after joint SIGN with 3 folded F-BLOCKING edits ("merge it")
- Close-cascade S2806 → ratified inline via close-ceremony execution ("close cascade")

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** wizard route extraction (triggered by 3 conditions listed §6); attorney sub-forms (conditional on Chris needing them).

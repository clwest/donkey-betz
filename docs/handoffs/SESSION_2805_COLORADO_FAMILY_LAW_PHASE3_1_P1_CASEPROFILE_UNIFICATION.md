# Session 2805 — Colorado Family Law Phase 3.1 P1 (CaseProfile/LegalCase unification)

**Date:** 2026-07-17
**Session:** S2805
**PRs shipped:** 1 — **PR #3227** (Phase 3.1 P1 · `0376a0b33`)
**Predecessor:** [SESSION_2804 Phase 3.1 P0 + 3.1a](SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +221 / −34 LOC across 7 files (incl. migration 0387).**

### PR #3227 — Phase 3.1 P1: CaseProfile/LegalCase unification

Unifies `LegalDocument` case linkage around `CaseProfile` (Session 406, the richer model with case_number/court/district/division and parties as first-class rows). Fixes a latent silent bug where the drafter agent's `_save_legal_document` did `LegalCase.objects.get(id=self.case_id)` but `self.case_id` was actually a **CaseProfile** UUID (sourced from `request.session['active_case_id']` per Session 406). The `LegalCase.DoesNotExist` was swallowed and `case` remained `None` on every save.

**Migration (`core/migrations/0387_legal_document_case_profile_fk.py`):**
- Adds nullable `LegalDocument.case_profile = ForeignKey(CaseProfile, SET_NULL, null=True, blank=True, related_name='legal_documents')`
- Zero backfill (`LegalDocument` had 1 row at S2805 open, `case=None` already; `LegalCase` = 0 rows; `CaseProfile` = 0 rows)
- Preserves legacy `case` FK for grandfathering per S2803/S2804 ratification (do NOT drop)
- **Scoped by hand** — Django's `makemigrations` detected ~43 unrelated model-drift operations (narrative/haidispatchlog/index renames) that belong to their own migrations; those were deliberately NOT smuggled into this P1 change

**Agent refactor (`core/agents/legal/legal_doc_drafter_agent.py`):**
- Rename ctor kwarg + attr `case_id` → `case_profile_id` (Rigby SIGN edit 3 — prevents UUID-meaning-drift regression). Legacy `case_id=` kwarg accepted as compat alias in `__init__` (mapped to same internal attribute).
- Rename `current_case` property → `current_case_profile`; now resolves `CaseProfile` (0 external callers found before removing the compat alias).
- `_save_legal_document` now looks up `CaseProfile` and binds only `case_profile=cp`. **NEVER populates legacy `case` FK** (agent-writes-case-profile-only invariant per Rigby SIGN edit 1).
- Removed the `case.document_count = case.documents.count()` denorm refresh block (Rigby SIGN edit 2).
- `_save_legal_research` passes `case_id=None` explicitly with a comment — `LegalResearchResult` still uses the LegalCase-based helper; migrating that model is a Phase 3.1 P1.b follow-up (blast-radius discipline).

**Model (`core/models_legal.py`):**
- Adds `CaseProfile.document_count` as a live `@property` returning `self.legal_documents.count()`. No denormalized field; matches read-side pattern.

**Tests (`core/tests/test_legal_agent_drafting_reliability.py` 17 → 22; `test_legal_agent_execution.py` helper rename):**
- T6a — save with `case_profile_id` binds `LegalDocument.case_profile`
- T6b — unknown `case_profile_id` → `case_profile` stays `None` (no crash)
- T6c — no `case_profile_id` → both case FKs None
- T6d — INVARIANT: agent NEVER writes legacy `case` FK on new saves (agent-writes-case-profile-only)
- T6e — `CaseProfile.document_count` @property reflects live count
- Full legal suite: **56 tests OK in 4.722s** (drafting_reliability + agent_execution + models + draft_endpoint + cross_user_access)

---

## §2 — Rigby joint SIGN cycle

**Pin:** `pa-b9dc1af5c7b04afd` (S2805 open-ceremony first-action fresh mint)
**Verdict:** **SIGN-WITH-EDITS** (all 3 F-BLOCKING items folded into scope — no unresolved deadlock; sent to Chris as joint recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`)

**Anti-rubber-stamp check:** **PASSED** — Rigby returned non-empty `tool_runs` (2× `repo_tool.read` + 3× `db_health_tool` real invocations). Independently verified `/api/legal/cases/` routing to `case_profiles_list`, `_save_legal_document` LegalCase.get pattern, absence of `document_count` on CaseProfile, and `LegalCase` row count = 0. No rubber-stamp signal.

**3 F-BLOCKING edits (all folded into P1 scope):**
1. Explicit "agent writes only `case_profile`, never `case`" invariant + T6d test locking it
2. `CaseProfile.document_count` as `@property` (recommended over denormalized field — no writes required)
3. Rename `case_id` → `case_profile_id` in agent to prevent UUID-meaning-drift regression class

**3 zoom-out folds persisted (ledger rows 109-111) per PLAYBOOK-6.10.8 (BEFORE Chris-facing recommendation), all 6.10.9-compliant with stable-state-pointer SHA `8412d6352` + file:line evidence + verified-state outcome inline:**
1. Row 109 (`same_pr_actionable`): UUID meaning drift across layers
2. Row 110 (`same_pr_actionable`): Denormalized counter coupling to retired model
3. Row 111 (`same_pr_mitigatable`): Dual-FK ambiguity risk post-P1

**Persistence mechanism:** `python manage.py record_zoom_out_concern` (Claude Code); Rigby noted her tool surface has read-only access to `zoom_out_tool.list` but no write mechanism — persistence fell to Claude Code, which used the management command directly.

---

## §3 — Novel-precedent moments

**A. First arc where live-DB counts fully overrode a handoff claim.** S2804 handoff §7 said "only 2 known rows: Phase 0 test doc + Chris's Phase 3.1 P0 test doc". Live query at S2805 open: 1 row (Phase 0 doc only). Chris's P0 test doc had disappeared between S2804 close and S2805 open (recycle wipe? different user? unclear). The refined P1 scope shipped with **0-backfill migration** on the basis of live-DB evidence, not the handoff prose. **Substrate lesson:** at session open, verify handoff data claims via live query before authoring scope — cheap and prevents scope drift.

**B. First same-session end-to-end substrate loop where refined scope was tighter than the handoff scope.** S2804 handoff §7 laid out P1 as "5-step scope with backfill code". Live-evidence refinement collapsed 3 of those 5 steps: no backfill code needed, no frontend churn (endpoint already CaseProfile-backed), the "silent lookup mismatch" (latent bug) became the load-bearing motivation for P1 rather than the "prepare for Phase 3.2" prospective framing.

**C. First `makemigrations` output rejection in the arc.** Django's automigration for `LegalDocument.case_profile` generated a 679-line migration containing 44 operations (43 unrelated to P1: narrative/haidispatchlog/index renames). Discarded the auto-generated file and hand-wrote a 43-line scoped migration containing only the single `AddField`. Blast-radius discipline — those other model drifts belong to their own migrations, not smuggled into P1. **Substrate lesson:** `makemigrations` output is a starting point, not a commit target, when significant drift exists.

**D. Ninth-consecutive same-day multi-ship session** — S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805. Streak holds even on refactor+migration+test work (previously the streak had been UI + backend + tests).

---

## §4 — Session-open infra story

**S2805 opened with S2804 pin retired.** Wrapper `tools/pa_local.sh` pointed at `pa-c8b5f2dc9d344c78` (retired per S2804 close-cascade). First-action fresh mint: `pa-b9dc1af5c7b04afd` labeled `s2805-colorado-family-law-phase3.1-p1-unification`. Freshness FRESH · head `8412d6352d72` · 0/5 stale workers. Ledger 108 rows verified at open (42 same_pr_actionable + 37 same_pr_mitigatable + 29 future_trigger).

**Live-DB anchor sweep (before Rigby SIGN dispatch):**
- `LegalDocument.objects.count()` = 1 (case=None; not 2 as S2804 handoff claimed)
- `LegalCase.objects.count()` = 0
- `CaseProfile.objects.count()` = 0
- `/api/legal/cases/` at `core/urls.py:3912` routed to `case_profiles_list` (CaseProfile, not LegalCase — no frontend churn needed)
- `LegalDocDrafterAgent` production callers pass no `case_id` (`views_legal.py:531`, `discord_bot.py:10204/10277`)
- `_save_legal_document` at `legal_doc_drafter_agent.py:2298-2314` — silent `LegalCase.DoesNotExist` swallowed (latent bug)

**Test iteration (2 iterations to full-legal-suite green):**
1. First P1 test run: 17/17 in `test_legal_agent_drafting_reliability.py` OK; then ran sibling `test_legal_agent_execution.py` → 5 failures with `'LegalDocDrafterAgent' object has no attribute 'case_profile_id'`
2. Root cause: sibling test file's `_make_agent` helper still bypassed `__init__` and set old attr `agent.case_id`. Renamed helper's attr to match. Full legal suite green (56 tests, 4.722s).

---

## §5 — Twin-pointer card

📁 **Repo — S2805 artifacts:**

- **PR (1, merged):** #3227 (Phase 3.1 P1 · `0376a0b33`)
- **Substrate changes:**
  - `core/models_unified_system.py` — `LegalDocument.case_profile` FK added
  - `core/models_legal.py` — `CaseProfile.document_count` @property added
  - `core/agents/legal/legal_doc_drafter_agent.py` — `_save_legal_document` refactor, `case_id`→`case_profile_id` rename, `current_case_profile` property, `_save_legal_research` compat comment
  - `core/migrations/0387_legal_document_case_profile_fk.py` — scoped hand-written migration
- **Test files (2 modified):**
  - `core/tests/test_legal_agent_drafting_reliability.py` (17 → 22 tests, +5 T6 P1 tests)
  - `core/tests/test_legal_agent_execution.py` (helper rename only)
- **Handoff:** `docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **111 rows** (rows 109-111 P1 folds)
- **Merge SHA:** `0376a0b33` (Phase 3.1 P1) → close-cascade filled at cascade PR merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — no user-facing changes this arc. Backend refactor only; the Phase 3.1a view modal still renders whatever's in `LegalDocument`. Post-P1, new drafter dispatches with an `active_case_id` in session will bind `case_profile` correctly (currently no wizard writes `active_case_id` — arrives with Phase 3.2 case-creation wizard).
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## §6 — Next session (S2806) — Phase 3.2 default or Chris redirect

**Chris ratified at S2804 close:** post-P1 ordering is Phase 3.2 (case-creation wizard). P1 unblocks 3.2 because CaseProfile now has a live FK path from LegalDocument.

### Phase 3.2 — Case creation wizard (S2806 P0 default)

**Scope:**
1. `POST /api/legal/case-profiles/` create endpoint (CaseProfile model already exists; may already have a create endpoint — verify at open)
2. Wizard modal on LegalPage — case_number, court, county, district, division, case_type, parties (petitioner + respondent) as first-class rows
3. `active_case_id` session write on wizard submit (so subsequent draft dispatches bind `case_profile` correctly per P1)
4. Frontend: "New Case" button in Cases tab → wizard modal → save → CaseProfile visible in list

### Phase 4a (NEW, queued) — Form-selection intelligence

Chris's mid-Phase-3.1 requirement: user describes situation → agent picks correct JDF form + procedural knowledge. Standalone arc. Not urgent enough to derail 3.2 ordering unless Chris re-prioritizes.

### Phase 4 — Statute-citation content quality

C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language.

### Phase 5 — Spider beat schedule

Monthly refresh for `colorado_family_law_spider`.

### Standing follow-ups

- **Phase 3.1 P1.b — LegalResearchResult unification**: `save_legal_research` at `models_unified_system.py:17612` still uses LegalCase-based `case_id` param with silent `DoesNotExist` swallowing. Same latent-bug class as the LegalDocument one P1 just fixed. Small PR; can pair with 3.2 or ship standalone.
- Small PRs owed (still open from S2803/S2804):
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening (Phase 2 punt)
  - `LegalDocument.generation_context` add `blank=True` (Phase 2 model quirk)
  - PA→Celery E2E integration test (Rigby Phase 2 SIGN Fold 4)
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split (Rigby Phase 2 SIGN Fold 3)
- Group 2700 docs restructuring arc (still queued from S2801; blocked behind Colorado arc)
- BettingPage first-user trace (pre-Colorado default)
- Stock Intelligence (first non-betting revenue play)

---

## §7 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Open ceremony + refined P1 scope acknowledged ("Proceed")
- P1 build after Rigby joint SIGN with 3 folded F-BLOCKING edits ("yes")
- Merge + recycle P1 ("standing pattern" per S2799+ close ratifications)
- Close-cascade S2805 → ratified inline via close-ceremony execution

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** Phase 4a form-selection (Chris mid-execution requirement at S2804), Phase 3.1 P1.b LegalResearchResult unification (surfaced during P1 refactor).

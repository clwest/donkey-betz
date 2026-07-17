# Session 2807 — Colorado Family Law Phase 3.1 P1.b (LegalResearchResult unification)

**Date:** 2026-07-17
**Session:** S2807
**PRs shipped:** 1 — **PR #3231** (Phase 3.1 P1.b · `65dd02106abd`)
**Predecessor:** [SESSION_2806 Phase 3.2](SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +197 / −19 LOC across 5 files (incl. migration 0388).**

### PR #3231 — Phase 3.1 P1.b: LegalResearchResult unification

Mechanical mirror of S2805 Phase 3.1 P1 (LegalDocument) applied to `LegalResearchResult`. Fixes the same latent silent-bug class in `save_legal_research` (`LegalCase.get(id=case_id)` swallowed `DoesNotExist`, research rows silently saved with `case=None`) and removes the parallel denorm coupling (`LegalCase.research_count` integer field maintained by hand). Zero-row backfill.

**Migration (`core/migrations/0388_legalresearchresult_case_profile_fk.py`):**
- Adds nullable `LegalResearchResult.case_profile = ForeignKey(CaseProfile, SET_NULL, null=True, blank=True, related_name='legal_research_results')`
- Zero backfill (`LegalResearchResult` had 1 row at S2807 open, `case=None` already; `LegalCase` = 0 rows; `CaseProfile` = 0 rows)
- Preserves legacy `case` FK for grandfathering per S2803/S2804 policy
- Scoped by hand — same discipline as 0387 (rejected auto-generated cross-model drift)

**Model (`core/models_unified_system.py`):**
- `case_profile` FK added below existing `case` FK (grandfathered explicit comment)
- `save_legal_research` classmethod refactored:
  - Kwarg renamed `case_id` → `case_profile_id` (legacy `case_id` accepted as compat alias mapped to same lookup)
  - `CaseProfile.get()` with `logger.warning` on `DoesNotExist` (S2805 Lesson 3 — no silent swallow)
  - Binds only `case_profile=case_profile`; **NEVER populates legacy `case` FK** (agent-writes-case-profile-only invariant)
  - Denorm block removed (`case.research_count = case.research_results.count()`)

**Model (`core/models_legal.py`):**
- Adds `CaseProfile.research_result_count` as live `@property` returning `self.legal_research_results.count()`. Mirrors `document_count` from P1.

**Agent (`core/agents/legal/legal_doc_drafter_agent.py:2403`):**
- `_save_legal_research` now passes `case_profile_id=self.case_profile_id` (drafter already had this attr from S2805 P1 rename)
- Removed the S2805 P1 compat comment about "Phase 3.1 P1.b deferred"

**Tests (`core/tests/test_legal_agent_drafting_reliability.py`):**
- T7a — save with `case_profile_id` binds `LegalResearchResult.case_profile`
- T7b — unknown `case_profile_id` → `assertLogs('WARNING')` fires with the missing id string + `case_profile` stays None (**delta from T6b** which only tolerated silent None — locks in observable non-silent behavior)
- T7c — no `case_profile_id` → both case FKs None
- T7d — INVARIANT: helper NEVER writes legacy `case` FK on new saves
- T7e — `CaseProfile.research_result_count` @property reflects live count
- **Full legal suite: 61 tests OK in 199.81s** (56 pre-existing + 5 new T7)

---

## §2 — Rigby joint SIGN cycle

**Pin:** `pa-a6578b35e0244cea` (S2807 open-ceremony first-action fresh mint)
**Verdict:** **AGREE-WITH-EDITS** on all 3 questions (no F-BLOCKING deadlock; sent to Chris as joint recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`)

**Anti-rubber-stamp check:** **PASSED** — Rigby returned non-empty `tool_runs` (verified `db_health_tool` schema check on LegalResearchResult, `execution_history_tool` recent listings, multiple `repo_tool.read` on `models_unified_system.py` + `legal_doc_drafter_agent.py`). Independently verified endpoint signatures, model shape, callers, and current DB counts before signing.

**3 SIGN questions + verdicts:**

1. **Q1 (Scope + T7b logger.warning assertion): AGREE.** T7b's `assertLogs('WARNING')` delta from T6b is the right encoding of S2805 Lesson 3 — assert observable failure signal, not tolerate silent None.
2. **Q2 (@property naming): AGREE with `research_result_count`.** Preferred over `research_count` — matches relation name `legal_research_results` (parallel to `document_count`/`legal_documents`).
3. **Q3 (zoom-out mechanical-mirror-risk fold): mitigation via pre-scan.** Row 113 persisted.

**1 zoom-out fold persisted (ledger row 113) per PLAYBOOK-6.10.8 (BEFORE Chris-facing recommendation), 6.10.9-compliant with stable-state-pointer SHA `674ea25535ff` + file:line evidence + verified-state outcome inline:**

- Row 113 (`same_pr_actionable`) — Pattern-replication risk: mechanical mirror of P1 could copy the same data-contract-ambiguity mistake twice. **Mitigation SATISFIED IN-ARC by pre-scan** on head `674ea25535ff`: only 2 `LegalCase.objects.get(id=)` matches in the codebase (both in the target `save_legal_research` method); zero other `save_legal_*` classmethods on models; zero other FKs to `LegalCase` remain (grep `LegalCase, on_delete` yields only the target). No third latent-bug class exists.

**Persistence mechanism:** `python manage.py record_zoom_out_concern` (Claude Code); Rigby's tool surface remains read-only for `zoom_out_tool.list`.

---

## §3 — Novel-precedent moments

**A. First mechanical-mirror ship with pre-scan mitigation folded into the SIGN cycle.** Prior P1 (S2805) shipped without pre-scanning for related helpers because no prior instance existed to establish the class. P1.b's Rigby SIGN Q3 explicitly asked "what pattern do we accrete by mechanical-mirror?" — driving a pre-scan that confirmed the LegalDocument/LegalResearchResult pair is the complete inventory of the latent-bug class. This closes the class rather than just fixing one more instance. **Substrate lesson:** when applying a mechanical mirror, explicitly ask what makes THIS the last mirror needed; if the answer is "we don't know," pre-scan.

**B. First test file where a T7b delta from T6b codifies a mid-arc lesson learned in a previous session.** S2805 Lesson 3 said "never silent-swallow" but T6b only tolerated silent None (which is what the P1 pattern shipped). P1.b's T7b actually asserts `logger.warning` fires — the test file now embodies the lesson AS test-executable code, not just prose in a handoff. Consider a P1 back-port: retrofit T6b with the same `assertLogs` assertion so P1's tests also enforce the observable-non-silent-swallow discipline (small follow-up PR).

**C. Sixth-consecutive session where anchor-verify at open collapsed handoff scope.** S2806 handoff §6 described P1.b as "small PR; ships standalone or paired with 3.2." At open, live anchor-verify + Rigby's pre-scan tightened this further: not just "small PR" but "closes the latent-bug class." Scope framing changed from "ship one more fix" to "prove no more fixes needed."

**D. Eleventh-consecutive same-day multi-ship session** — S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → S2806 → **S2807**. Streak now spans latent-bug fix + wizard + latent-bug closure — the arc has completed both its correctness substrate (P0/P1/P1.b) and one user-facing capability (P3.2) within this run.

---

## §4 — Session-open infra story

**S2807 opened with S2806 pin retired.** Wrapper `tools/pa_local.sh` pointed at `pa-3c492806c55149e9` (retired per S2806 close-cascade). First-action fresh mint: `pa-a6578b35e0244cea` labeled `s2807-colorado-family-law-phase3.1-p1b-legalresearchresult`. Freshness FRESH · head `674ea25535ff` · 0/5 stale workers. Ledger 112 rows verified at open (44 same_pr_actionable + 39 same_pr_mitigatable + 29 future_trigger).

**Live-DB / codebase anchor sweep (before Rigby SIGN dispatch):**

- `LegalResearchResult` model at `models_unified_system.py:17455` — `case` FK to LegalCase at `:17476-17482`
- `save_legal_research` classmethod at `:17612-17667` — confirmed silent `LegalCase.get + except DoesNotExist: pass` at `:17635-17638`; denorm block at `:17660-17662`
- `LegalCase.research_count` IntegerField at `:17207` (parallel to `LegalCase.document_count` from pre-P1)
- **Only 1 external caller:** `legal_doc_drafter_agent.py:2403` (drafter's own `_save_legal_research` helper) — already passing `case_id=None`
- Live DB counts: `LegalResearchResult=1` (case=null), `LegalCase=0`, `LegalResearchResult with non-null case=0` → **zero-backfill migration**
- Pre-scan for other `save_legal_*` helpers: none found. Pre-scan for other `LegalCase.objects.get(id=)`: only in the target method. Pre-scan for other FKs to LegalCase: none remain outside `LegalDocument.case` (P1-migrated) and `LegalResearchResult.case` (target of this arc).

**Test iteration:** Single-shot to green. `python manage.py migrate` applied 0388 cleanly. `pytest core/tests/test_legal_agent_*` = 61 tests OK first run (5 new + 56 preserved).

---

## §5 — Twin-pointer card

📁 **Repo — S2807 artifacts:**

- **PR (1, merged):** #3231 (Phase 3.1 P1.b · `65dd02106abd`)
- **Substrate changes:**
  - `core/migrations/0388_legalresearchresult_case_profile_fk.py` — **new** scoped migration
  - `core/models_unified_system.py` — `case_profile` FK + `save_legal_research` refactor
  - `core/models_legal.py` — `CaseProfile.research_result_count` @property
  - `core/agents/legal/legal_doc_drafter_agent.py` — drafter now passes `case_profile_id=self.case_profile_id`
- **Test files:** `core/tests/test_legal_agent_drafting_reliability.py` (33→38 tests; 5 new T7 including T7b assertLogs delta)
- **Handoff:** `docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **113 rows** (row 113 P1.b fold: pattern-replication risk `same_pr_actionable`, mitigated in-arc via pre-scan)
- **Merge SHA:** `65dd02106abd` (Phase 3.1 P1.b) → close-cascade filled at cascade PR merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — no user-facing changes this arc. Backend refactor only. Post-P1.b: legal-research dispatches (via drafter agent) will bind `case_profile` correctly whenever `active_case_id` is set in session (which is populated by the Phase 3.2 wizard). Full loop closed: wizard writes session → agent reads session → both LegalDocument and LegalResearchResult bind to CaseProfile.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## §6 — Next session (S2808) — candidates

### ⭐ Phase 4a — Form-selection intelligence (natural default candidate)

**Chris's mid-Phase-3.1 requirement** (surfaced at S2804 handoff §2). User describes situation → agent picks correct JDF form + procedural knowledge. **All backend correctness prerequisites now closed** by the P1/P1.b arc. Phase 3.2 wizard provides the session `active_case_id` write path. This is the next natural user-facing capability.

**Scope sketch (verify at open):**
- Ingest JDF form catalog into a queryable structure (may already exist via `colorado_family_law_spider` — verify)
- Add form-selection tool/method to `LegalDocDrafterAgent` (situation → form_number + procedural summary)
- Wire a "help me pick the right form" surface — new PA intent OR new endpoint that dispatches to the agent OR new UI affordance on `/legal`

### Alternate S2808 candidates

- **Phase 4 — Statute-citation content quality**: C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language
- **Phase 5 — Spider beat schedule**: monthly refresh for `colorado_family_law_spider`
- **P1-back-port test hardening (small)**: retrofit T6b with `assertLogs('WARNING')` mirroring T7b delta — codifies the observable-non-silent-swallow discipline in the P1 test file too
- **Wizard-related follow-ups** (from Phase 3.2 fold row 112):
  - Wizard extraction to `/legal/cases/new` route (triggers: deep-link, draft-persistence, browser-back)
  - Attorney sub-form when `!is_pro_se`
- **Small follow-up PRs owed** (S2803/S2804):
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening
  - `LegalDocument.generation_context` add `blank=True`
  - PA→Celery E2E integration test
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split
- **Group 2700 docs restructuring arc** (queued behind Colorado)
- **BettingPage first-user trace** (pre-Colorado)
- **Stock Intelligence** (first non-betting revenue play)

---

## §7 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Open ceremony + refined P1.b scope acknowledged ("yes proceed")
- Merge P1.b after joint SIGN with pre-scan mitigation folded ("merge it")
- Close-cascade S2807 → ratified inline via close-ceremony execution ("close cascade")

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** P1-back-port test hardening (small; codifies mid-arc lesson); Phase 4a form-selection (Chris mid-P3.1 requirement now unblocked).

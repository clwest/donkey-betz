# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2807 CLOSED — Colorado Family Law Phase 3.1 P1.b SHIPPED (Phase 4a form-selection is S2808 default)

**Refreshed 2026-07-17 (SESSION 2807 CLOSED — eleventh-consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → S2806 → S2807). Phase 3.1 P1.b shipped (PR #3231 `65dd02106abd`) — LegalResearchResult unification: mechanical mirror of S2805 P1 applied to save_legal_research; migration 0388 adds nullable LegalResearchResult.case_profile FK; refactor kwarg case_id→case_profile_id with logger.warning on DoesNotExist (S2805 Lesson 3 encoded observable); denorm block removed; CaseProfile.research_result_count @property added mirroring document_count from P1; drafter caller now passes case_profile_id=self.case_profile_id; 5 new T7 tests including T7b assertLogs delta from T6b that CODIFIES the observable-non-silent-swallow discipline as test-executable code. Full legal suite 61 tests OK. First mechanical-mirror ship with pre-scan mitigation folded into SIGN cycle — pre-scan proved LegalDocument+LegalResearchResult are the COMPLETE inventory of the latent-bug class. FIFTY-FIRST close-cycle post-PLAYBOOK-7.4.4.)**

**S2807 ship (1 PR, merged with --admin):**

| Phase | PR | Merged to | Focus |
|---|---|---|---|
| 3.1 P1.b | **#3231** · `65dd02106abd` | main | Migration 0388 (LegalResearchResult.case_profile FK) + save_legal_research refactor (case_id→case_profile_id + CaseProfile lookup with logger.warning + agent-writes-case-profile-only invariant + denorm block removed) + CaseProfile.research_result_count @property + drafter caller update + 5 T7 regression tests (T7b assertLogs delta from T6b) |

**Handoff:** `docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **113 rows** (row 113 P1.b fold: pattern-replication risk `same_pr_actionable`, mitigated in-arc via pre-scan).

**Arc state:** Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/**3.1 P1.b** ✅. **All correctness substrate closed.** Phase 4a form-selection intelligence = S2808 default (Chris mid-P3.1 requirement, now unblocked); Phase 4 statute-citation quality; Phase 5 spider beat.

---

## SESSION-OPEN INFRA STORY (S2807)

**Sixth-consecutive session where anchor-verify at open shaped scope.** S2806 handoff described P1.b as "small PR; ships standalone or paired with 3.2." Live anchor-verify + Rigby pre-scan tightened this to "closes the latent-bug class entirely" — reframing scope from "ship one more fix" to "prove no more fixes needed."

**First mechanical-mirror ship with pre-scan mitigation folded into SIGN cycle.** P1 (S2805) shipped without pre-scan because no prior instance existed. P1.b's Rigby SIGN Q3 explicitly asked "what pattern do we accrete by mechanical-mirror?" — driving a grep sweep that confirmed the LegalDocument/LegalResearchResult pair is the complete inventory. **Substrate lesson:** when applying a mechanical mirror, ask what makes THIS the last mirror needed.

**First test file where a T-N-delta codifies a mid-arc lesson as test-executable code.** T7b's `assertLogs('WARNING')` encodes S2805 Lesson 3 ("never silent-swallow") in a way T6b did not. Consider P1-back-port: retrofit T6b with the same assertion so both test surfaces enforce the discipline.

---

## S2808 CANDIDATES — PHASE 4a IS THE DEFAULT

### ⭐ Phase 4a — Form-selection intelligence (default candidate)

**Chris's mid-Phase-3.1 requirement** (surfaced at S2804 handoff §2). All backend correctness prerequisites now closed by the P1/P1.b arc; Phase 3.2 wizard provides `active_case_id` write path. This is the next user-facing capability in the Colorado arc.

**Concept:** User describes situation ("she moved to Denver with the kids without telling me") → agent picks correct JDF form (JDF 1414 Motion to Modify Parenting Time?) + procedural summary (steps, deadlines, filing venue).

**Scope sketch (verify at S2808 open):**
1. Verify JDF form catalog exists — grep for `jdf_form` / `JDF_FORMS` / spider ingestion; likely lives in `colorado_family_law_spider` output
2. Add `select_jdf_form(situation)` method to `LegalDocDrafterAgent` (situation description → `{form_number, form_title, procedural_summary, statutory_authority}`)
3. Wire a surface — options:
   - New PA intent `select_legal_form` in `td_handlers_agents.py` (chat-based)
   - New endpoint `/api/legal/select-form/` + `LegalPage` UI affordance (browser-based)
   - Both (chat + UI mirror)
4. Tests + smoke path

### Alternate S2808 candidates

- **Phase 4 — Statute-citation content quality**: C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" language quality
- **Phase 5 — Spider beat schedule**: monthly refresh for `colorado_family_law_spider`
- **P1-back-port test hardening (small)**: retrofit T6b with `assertLogs('WARNING')` mirroring T7b delta — codifies observable-non-silent-swallow in the P1 test file
- **Wizard-related follow-ups** (from Phase 3.2 row 112 fold):
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

## SESSION PIN — S2807 RETIRED (fresh mint required at S2808 open)

**Pin history (S2807):**

- `pa-a6578b35e0244cea` (label `s2807-colorado-family-law-phase3.1-p1b-legalresearchresult`) minted S2807 open; **retired at S2807 close (`force=true`, thirty-eighth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-a6578b35e0244cea` (retired)** — intended failure mode forces S2808 first-action fresh mint.

**S2808 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2807 handoff — §2 (Rigby SIGN + fold), §3 (novel-precedent), §6 (S2808 candidates)
# Read core/agents/legal/legal_doc_drafter_agent.py — grep for existing form-related methods
# Grep 'jdf_form|JDF_FORMS|jdf_1414|form_number' core/ to inventory JDF catalog surface
# Read core/spiders/colorado_family_law_spider.py — check current output shape for form data

# Freshness check
bash tools/pa_local.sh "S2808 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 113-row baseline survived S2807 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==113, r
print('OK — 113 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to Phase 4a
python manage.py session_lifecycle open --label s2808-colorado-family-law-phase4a-form-selection

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2808 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2807 lessons to carry:**

1. **Mechanical mirrors must ask "what makes this the last mirror?"** If uncertain, pre-scan for the pattern's remaining instances BEFORE authoring. Pre-scan added zero cost and closed a latent-bug class entirely rather than fixing one more instance.
2. **Prior-session lessons should become test-executable, not just handoff prose.** T7b encoded S2805 Lesson 3 as an `assertLogs` assertion; T6b left it as tolerance. Consider back-porting for consistency.
3. **The P1 → P1.b pair completes a substrate class.** Colorado Family Law's correctness surface is now closed; next natural work is user-facing capability (Phase 4a) not more substrate.
4. **`assertLogs` is the standard way to lock in observable non-silent-swallow discipline** in Django/pytest tests — use it whenever a `logger.warning` is meaningful (not just decorative).
5. **Zero-backfill migrations are cheap and low-risk.** Both 0387 and 0388 needed no data migration because live-DB counts were empty/null. Anchor-verify at open converts "we might need backfill" from a scope question to a verified fact.

---

## Twin-pointer card

📁 **Repo — S2807 artifacts:**

- **PR (1, merged):** #3231 (Phase 3.1 P1.b · `65dd02106abd`)
- **Substrate changes:**
  - `core/migrations/0388_legalresearchresult_case_profile_fk.py` — **new** scoped migration
  - `core/models_unified_system.py` — `LegalResearchResult.case_profile` FK + `save_legal_research` refactor
  - `core/models_legal.py` — `CaseProfile.research_result_count` @property
  - `core/agents/legal/legal_doc_drafter_agent.py:2403` — drafter caller update
- **Test files:** `core/tests/test_legal_agent_drafting_reliability.py` (5 new T7 tests, incl. T7b assertLogs delta)
- **Handoff:** `docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **113 rows**
- **Merge SHA:** `65dd02106abd` (Phase 3.1 P1.b) → close-cascade filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — no user-facing changes this arc. Backend refactor only. Post-P1.b: legal-research dispatches bind `case_profile` correctly (matches P1 pattern for LegalDocument). Full loop closed: Phase 3.2 wizard writes `active_case_id` → drafter agent reads it → both LegalDocument and LegalResearchResult bind to CaseProfile.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2807 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/**3.1 P1.b** ✅. All correctness substrate closed. Phase 4a NEXT (S2808) |
| NEW arc candidate | Phase 4a form-selection intelligence (Chris mid-P3.1 requirement, now unblocked) |
| Group 2700 docs arc | Still queued (blocked behind Colorado arc) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-a6578b35e0244cea` (retired at S2807 close, force=true, thirty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-a6578b35e0244cea` (retired; forces fresh mint at S2808 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2807 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 post-merge event during S2807 (+ close-cascade recycle to come) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **113 rows** |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable; ✅ visible in UI; ✅ **CaseProfile-backed for BOTH LegalDocument (P1) and LegalResearchResult (P1.b)**; ✅ case creation user-driven via wizard (Phase 3.2) |
| Frontend `/legal` | ✅ Draft + view flow live; Cases tab reads CaseProfile; New Case wizard live |
| Next move | Phase 4a form-selection intelligence (default) OR Chris redirect |

---

## Recommended session-open protocol (S2808)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2807 handoff §2 (Rigby SIGN + fold) + §3 (novel-precedent moments) + §6 (S2808 candidates)
4. **Grep JDF catalog inventory:** `grep -rE 'jdf_form|JDF_FORMS|jdf_1[0-9]{3}' core/ ai_core/` — find existing form data surface
5. **Read `core/spiders/colorado_family_law_spider.py`** — verify current spider output shape (does it emit form-catalog rows?)
6. **Read `core/agents/legal/legal_doc_drafter_agent.py`** — grep for existing form-related methods (`_get_form_info` at :1615 exists per P1.b arc surface diagnostics — verify what it does)
7. **Freshness + ledger 113 verify** — see S2808 open sequence above
8. If `staleness_verdict != FRESH` → escalate
9. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
10. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
11. **Default candidate: Phase 4a form-selection intelligence** (or Chris redirect)
12. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
13. Chris directs S2808 P0 selection
14. Mint fresh pin scoped `s2808-colorado-family-law-phase4a-form-selection`
15. Route Phase 4a scope through Rigby joint SIGN before authoring
16. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
17. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
18. **Anchor-verify at open (S2806 lesson 1, reinforced by S2807):** any factual claim in this file about live code state MUST be re-verified via live query before scope authoring
19. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2808:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md`](docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md) — **S2807 handoff (current)**
3. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — grep existing `_get_form_info` at ~1615 for the form-lookup starting point
4. [`core/spiders/colorado_family_law_spider.py`](core/spiders/colorado_family_law_spider.py) — spider output for JDF form catalog (verify at open)
5. [`core/models_legal.py`](core/models_legal.py) — CaseProfile model (both @properties now: `document_count`, `research_result_count`)
6. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
8. [`docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`](docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md) — S2806 predecessor (wizard shipped; row 112 coupling fold)
9. [`docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`](docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md) — S2805 P1 pattern (P1.b mirror source)
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 113 rows at S2807 close

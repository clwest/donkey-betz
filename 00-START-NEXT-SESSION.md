# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2805 CLOSED — Colorado Family Law Phase 3.1 P1 SHIPPED (Phase 3.2 case-creation wizard is S2806 default)

**Refreshed 2026-07-17 (SESSION 2805 CLOSED — ninth consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805). Phase 3.1 P1 shipped (PR #3227 `0376a0b33`) — CaseProfile/LegalCase unification: added nullable `LegalDocument.case_profile` FK, refactored `_save_legal_document` to bind CaseProfile (fixes latent silent bug where `active_case_id` session UUID was being resolved via `LegalCase.get()` and swallowed as DoesNotExist), renamed agent attr `case_id` → `case_profile_id` (Rigby SIGN edit), added `CaseProfile.document_count` as live `@property`, added T6a-e regression tests. Full legal suite 56 tests OK in 4.722s. First arc where live-DB counts fully overrode a handoff claim (S2804 handoff said "2 rows"; live query = 1). First `makemigrations` rejection — auto-generated 679-line/44-op migration discarded, hand-wrote scoped 43-line migration. FORTYNINTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2805 ship (1 PR, merged with --admin):**

| Phase | PR | Merged to | Focus |
|---|---|---|---|
| 3.1 P1 | **#3227** · `0376a0b33` | main | Migration 0387 (LegalDocument.case_profile FK) + agent refactor (case_id→case_profile_id + CaseProfile lookup + agent-writes-case-profile-only invariant) + CaseProfile.document_count @property + 5 T6 regression tests |

**Handoff:** `docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **111 rows** (rows 109-111 P1 folds: UUID meaning drift · denorm counter coupling · dual-FK ambiguity).

**Arc state:** Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/**3.1 P1** ✅; Phase 3.2 = case-creation wizard (S2806 default); Phase 4a = form-selection intelligence (NEW, queued); Phase 4 = statute-citation quality; Phase 5 = spider beat schedule.

---

## SESSION-OPEN INFRA STORY (S2805)

**First arc where live-DB counts fully overrode a handoff claim.** S2804 handoff §7 said "2 rows"; live query at S2805 open = 1 (Phase 0 doc only). Refined scope shipped with 0-backfill migration on live-DB evidence, not handoff prose. Substrate lesson: verify handoff data claims via live query at session open — cheap and prevents scope drift.

**First `makemigrations` rejection in the Colorado arc.** Auto-generated 679-line migration contained 44 operations, only 2 lines were P1-relevant. Discarded and hand-wrote a 43-line scoped migration. Blast-radius discipline — unrelated model drift belongs to its own migrations.

**Same-session end-to-end refined scope: tighter than the handoff scope.** S2804 handoff §7 laid out 5-step P1; live-evidence refinement collapsed 3 of those 5 (no backfill code, no frontend churn, silent-bug-fix became load-bearing motivation).

---

## S2806 CANDIDATES — PHASE 3.2 IS THE DEFAULT

### ⭐ Phase 3.2 — Case creation wizard (default candidate)

**Chris ratified at S2804 close** as post-P1 next step. P1 now unblocks 3.2 because CaseProfile has a live FK path from LegalDocument (verified post-recycle: `core_legaldocument.case_profile_id` column present).

**Scope:**
1. Verify or add `POST /api/legal/case-profiles/` create endpoint (CaseProfile model exists; a create surface may already exist under a different name — verify at open)
2. Wizard modal on LegalPage — fields: case_number, court, county, district, division, case_type; parties as first-class rows (petitioner + respondent)
3. `active_case_id` session write on wizard submit (so subsequent draft dispatches bind `case_profile` correctly per P1)
4. Frontend: "New Case" button in LegalPage Cases tab → wizard modal → save → CaseProfile visible in list

**Non-goals:**
- Do NOT touch drafter agent (P1 already correct)
- Do NOT drop `LegalCase` model or `LegalDocument.case` FK (grandfathered per S2803/S2804)

### Phase 3.1 P1.b — LegalResearchResult unification (small companion)

`save_legal_research` at `core/models_unified_system.py:17612` still uses LegalCase-based `case_id` param with silent `DoesNotExist` swallowing — same latent-bug class as the LegalDocument one P1 just fixed. Small PR. Can ship standalone or pair with 3.2.

### Phase 4a (NEW, queued) — Form-selection intelligence

Chris's mid-Phase-3.1 requirement (`docs/handoffs/SESSION_2804…md` §2). User describes situation → agent picks correct JDF form + procedural knowledge. Standalone arc.

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

## SESSION PIN — S2805 RETIRED (fresh mint required at S2806 open)

**Pin history (S2805):**

- `pa-b9dc1af5c7b04afd` (label `s2805-colorado-family-law-phase3.1-p1-unification`) minted S2805 open; **retired at S2805 close (`force=true`, thirtysixth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-b9dc1af5c7b04afd` (retired)** — intended failure mode forces S2806 first-action fresh mint.

**S2806 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2805 handoff — §2 (Rigby SIGN + folds), §3 (novel-precedent moments), §6 (Phase 3.2 scope)
# Read core/models_legal.py CaseProfile (lines 15-75) — the model to wire wizard against
# Read core/urls.py — grep for 'case-profiles' to find existing create/detail endpoints
# Read frontend/src/pages/LegalPage.tsx — Cases tab render (~332-388) — "New Case" button lands here

# Freshness check
bash tools/pa_local.sh "S2806 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 111-row baseline survived S2805 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==111, r
print('OK — 111 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to Phase 3.2
python manage.py session_lifecycle open --label s2806-colorado-family-law-phase3.2-case-wizard

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2806 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2805 lessons to carry:**

1. **Verify handoff data claims via live query at session open** — S2804 handoff said "2 rows"; live query = 1. Cheap and prevents scope drift. Extend to every handoff-data-referenced claim.
2. **`makemigrations` output is a starting point, not a commit target when significant drift exists** — auto-generated 679-line P1 migration was 98% unrelated. Hand-write scoped migrations when drift is present; those other model changes belong to their own migrations.
3. **Silent `DoesNotExist` swallowing is a bug-hiding pattern** — the LegalCase.get pattern hid the mismatch for months. When refactoring lookup code, prefer explicit failure signal (logger.warning at minimum) over `except: pass`. Applied to P1; consider audit sweep for other instances.
4. **Refined scope tighter than handoff scope is the healthy outcome** — 5-step scope collapsed to 3 (no backfill, no frontend churn). Trust the anchor-verify step at session open more than the retrospective handoff prose.
5. **Rigby's tool surface has read-only zoom-out ledger access** — persistence via `manage.py record_zoom_out_concern` falls to Claude Code. Note for future: consider adding `zoom_out_tool.record` to Rigby's write surface as a Phase 3.5 candidate.

---

## Twin-pointer card

📁 **Repo — S2805 artifacts:**

- **PR (1, merged):** #3227 (Phase 3.1 P1 · `0376a0b33`)
- **Substrate changes:** `core/models_unified_system.py` (LegalDocument.case_profile FK) + `core/models_legal.py` (CaseProfile.document_count @property) + `core/agents/legal/legal_doc_drafter_agent.py` (agent refactor + case_id→case_profile_id rename) + `core/migrations/0387_legal_document_case_profile_fk.py` (scoped migration)
- **Test files (2 modified):** `test_legal_agent_drafting_reliability.py` (17→22 tests, 5 T6 P1 tests) + `test_legal_agent_execution.py` (helper rename)
- **Handoff:** `docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **111 rows**
- **Merge SHA:** `0376a0b33` (Phase 3.1 P1) → close-cascade filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — unchanged this session (P1 is backend-only). Post-P1: new drafter dispatches with `active_case_id` in session bind `case_profile` correctly. Wizard (Phase 3.2) provides the write path for `active_case_id`.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2805 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/**3.1 P1** ✅; Phase 3.2 NEXT (S2806) |
| NEW arc candidate | Phase 4a form-selection intelligence (Chris mid-execution requirement, unchanged from S2804) |
| Group 2700 docs arc | Still queued (blocked behind Colorado arc) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-b9dc1af5c7b04afd` (retired at S2805 close, force=true, thirtysixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-b9dc1af5c7b04afd` (retired; forces fresh mint at S2806 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2805 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 post-merge event during S2805 (+ close-cascade recycle to come) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **111 rows** |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable (Phase 3.1 P0 two-layer defense); ✅ visible in UI (Phase 3.1a modal); ✅ CaseProfile-backed on save (Phase 3.1 P1) |
| Frontend `/legal` | ✅ Draft + view flow both live; Cases tab reads CaseProfile; "New Case" wizard is Phase 3.2 stub |
| Next move | Phase 3.2 case-creation wizard per S2804/S2805 close ratification |

---

## Recommended session-open protocol (S2806)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2805 handoff §2 (Rigby SIGN + folds) + §3 (novel-precedent moments) + §6 (Phase 3.2 scope)
4. **Read `core/models_legal.py`** `CaseProfile` (lines 15-75) — the model to wire wizard against; `Party` model below it for petitioner/respondent
5. **`Grep 'case-profiles' core/urls.py`** — find existing CaseProfile URL patterns (likely litigation-* endpoints; verify if `POST` create exists)
6. **Read `frontend/src/pages/LegalPage.tsx`** Cases tab render (~332-388) — "New Case" button lands here as wizard modal
7. **Freshness + ledger 111 verify** — see S2806 open sequence above
8. If `staleness_verdict != FRESH` → escalate
9. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
10. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
11. **Default candidate: Phase 3.2 case-creation wizard** (or Chris redirect)
12. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
13. Chris directs S2806 P0 selection
14. Mint fresh pin scoped `s2806-colorado-family-law-phase3.2-case-wizard`
15. Route Phase 3.2 scope through Rigby joint SIGN before authoring
16. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
17. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
18. **Anchor-verify at open:** any factual claim in this file about live DB state (row counts, FK presence, endpoint routing) MUST be re-verified via live query before scope authoring — S2805 lesson 1 codified
19. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2806:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`](docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md) — **S2805 handoff (current)**
3. [`core/models_legal.py`](core/models_legal.py) — `CaseProfile` (lines 15-75, wizard target) + `Party` (below) + `Attorney` + `LitigationDocument`
4. [`core/urls.py`](core/urls.py) — grep `case-profiles` for existing endpoints (~3910-3930)
5. [`frontend/src/pages/LegalPage.tsx`](frontend/src/pages/LegalPage.tsx) — Cases tab render for wizard modal insertion point
6. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — P1 refactor landing site (case_profile_id, current_case_profile, _save_legal_document at ~2298-2361); do NOT touch this arc
7. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
9. [`docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md`](docs/handoffs/SESSION_2804_COLORADO_FAMILY_LAW_PHASE3_1_AGENT_RELIABILITY.md) — S2804 predecessor
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 111 rows at S2805 close

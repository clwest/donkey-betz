# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2806 CLOSED — Colorado Family Law Phase 3.2 SHIPPED (Phase 3.1 P1.b or Phase 4a is S2807 default)

**Refreshed 2026-07-17 (SESSION 2806 CLOSED — tenth-consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → S2806). Phase 3.2 shipped (PR #3229 `52fd9aa55`) — case-creation wizard: new self-contained `CreateCaseWizardModal` component (Case Info / Petitioner / Respondent / Children sections), wired to previously-placeholder "New Case" button on `/legal` Cases tab, POSTs `/api/legal/cases/` → `/api/legal/active-case/` in one flow with retry-toast fallback. Backend endpoints already existed (verified live at open — fifth-consecutive session where anchor-verify tightened handoff scope; scope collapsed from 5 steps to 3). Frontend-only PR: +524/−10 LOC across 3 files. First fold-in fix promoted BY Rigby (cases-list display bug at `LegalPage.tsx:494` renderd `title||name` neither of which exist in backend DTO — updated to `case_title||case_number` while adjacent). First S2797-arc frontend deliverable that is a net-new user affordance (previous 9 all backend or narrow UI wiring). FIFTIETH close-cycle post-PLAYBOOK-7.4.4.)**

**S2806 ship (1 PR, merged with --admin):**

| Phase | PR | Merged to | Focus |
|---|---|---|---|
| 3.2 | **#3229** · `52fd9aa55` | main | `CreateCaseWizardModal.tsx` (new, 439 LOC) + `legalApi.createCase`/`setActiveCase` + `LegalPage.tsx` wiring + Cases-list DTO alignment fold-in fix |

**Handoff:** `docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **112 rows** (row 112 P3.2 fold: LegalPage coupling `same_pr_mitigatable` mitigated in-PR via self-contained component file).

**Arc state:** Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/**3.2** ✅; Phase 3.1 P1.b = LegalResearchResult unification (S2807 default candidate); Phase 4a = form-selection intelligence (queued); Phase 4 = statute-citation quality; Phase 5 = spider beat schedule.

---

## SESSION-OPEN INFRA STORY (S2806)

**Fifth-consecutive session where anchor-verify at open collapsed handoff scope.** S2805 handoff said "5-step scope with (1) verify or add POST endpoint" — live-read at open confirmed both `POST /api/legal/cases/` (`views_legal_cases.py:70-178`) and `POST /api/legal/active-case/` (`:618-641`) exist with full functionality from Session 406. Scope collapsed from 5 steps to 3; Phase 3.2 became a frontend-only PR.

**First fold-in bug fix promoted BY Rigby, not Claude Code.** Rigby's tool-grounded SIGN caught latent Cases-list rendering bug (`LegalPage.tsx:494` referenced non-existent `title`/`name` fields; had been broken since tab was authored). Promoted from "future cleanup" to "fix while you're here" as SIGN edit 3. Substrate lesson: tool-grounded SIGN can surface latent pre-existing bugs adjacent to scope at near-zero coordination cost.

**First fully-additive user-affordance PR of the S2797 streak.** Previous 9 sessions were backend correctness or narrow UI wiring (draft modal / view modal / agent reliability / migration). Phase 3.2 is the first arc that ships a net-new capability (case creation) users can immediately exercise.

---

## S2807 CANDIDATES

### ⭐ Phase 3.1 P1.b — LegalResearchResult unification (default candidate)

Same latent-bug class as P1 fixed for LegalDocument. `save_legal_research` at `core/models_unified_system.py:17612` uses LegalCase-based `case_id` param with silent `DoesNotExist` swallowing. Small PR; ships standalone or paired with Phase 4a.

**Scope:**
1. Read `save_legal_research` at `models_unified_system.py:17612` + verify current `case_id` semantics
2. Refactor to CaseProfile-based `case_profile_id` param (mirror P1 pattern from `legal_doc_drafter_agent.py:2298-2314`)
3. Migration if `LegalResearchResult` needs a `case_profile` FK (verify at open — may already have one)
4. Test coverage matching T6a-e pattern from P1

### Phase 4a — Form-selection intelligence (queued, Chris mid-P3.1 requirement)

User describes situation → agent picks correct JDF form + procedural knowledge. Standalone arc. Larger scope than P1.b; could be S2807 P0 if Chris wants to prioritize user-facing intelligence over substrate cleanup.

### Alternate S2807 candidates

- **Wizard-related follow-ups** (Phase 3.2 emergent):
  - Wizard extraction to `/legal/cases/new` route (deferred per row-112 fold; triggers: deep-link, draft-persistence, browser-back)
  - Attorney sub-form when `!is_pro_se` (backend accepts; wizard MVP defaults `is_pro_se=true`)
- **Phase 4 — Statute-citation content quality**: C.R.S. § 14-10-129 language
- **Phase 5 — Spider beat schedule**: monthly refresh for `colorado_family_law_spider`
- **Small follow-up PRs owed** (still open from S2803/S2804):
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening
  - `LegalDocument.generation_context` add `blank=True`
  - PA→Celery E2E integration test
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split into `agents/legal/` submodules
- **Group 2700 docs restructuring arc** (still queued behind Colorado arc)
- **BettingPage first-user trace** (pre-Colorado default)
- **Stock Intelligence** (first non-betting revenue play)

---

## SESSION PIN — S2806 RETIRED (fresh mint required at S2807 open)

**Pin history (S2806):**

- `pa-3c492806c55149e9` (label `s2806-colorado-family-law-phase3.2-case-wizard`) minted S2806 open; **retired at S2806 close (`force=true`, thirty-seventh consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-3c492806c55149e9` (retired)** — intended failure mode forces S2807 first-action fresh mint.

**S2807 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2806 handoff — §2 (Rigby SIGN + folds), §3 (novel-precedent moments), §6 (S2807 candidates)
# Read core/models_unified_system.py around line 17612 — save_legal_research (P1.b target)
# Grep 'LegalResearchResult' in core/ to find all usages
# Verify handoff data claim: does LegalResearchResult already have a case_profile FK, or is one needed?

# Freshness check
bash tools/pa_local.sh "S2807 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 112-row baseline survived S2806 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==112, r
print('OK — 112 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to P1.b (or Phase 4a per Chris)
python manage.py session_lifecycle open --label s2807-colorado-family-law-phase3.1-p1b-legalresearchresult

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2807 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2806 lessons to carry:**

1. **Anchor-verify at open ≠ optional — it is scope-shaping.** Fifth consecutive session where the live-code check collapsed 30-100% of a handoff's stated steps. Read live code / hit endpoints / query DB before authoring scope; treat handoff scope as a prior draft, not a work order.
2. **Trust tool-grounded SIGN to promote latent bugs.** Rigby's read of the actual backend DTO vs. frontend rendering caught a latent field-mismatch bug that had been silently rendering "Untitled Case" for every case since the tab was authored. Fold-in fix cost near-nothing; expect this pattern on adjacent rendering code.
3. **Self-contained component files pre-empt future extraction pain.** Wizard modal in its own file with page-agnostic props avoided any coupling to LegalPage state; future extraction to `/legal/cases/new` route is a mechanical import change, not a refactor.
4. **Recycle-before-commit is unnecessary for pure frontend PRs.** `make frontend-ship` (build + collectstatic + daphne restart) is the deploy step for frontend-only changes; no worker recycle needed pre-merge. `make recycle-all` post-merge per PLAYBOOK-7.4.4 still applies.
5. **Ledger persistence is Claude-Code-only.** Rigby's `zoom_out_tool.list` is read-only; `record_zoom_out_concern` management command is the write path. Include row persistence in the pre-Chris-recommendation phase per PLAYBOOK-6.10.8.

---

## Twin-pointer card

📁 **Repo — S2806 artifacts:**

- **PR (1, merged):** #3229 (Phase 3.2 · `52fd9aa55`)
- **Substrate changes:**
  - `frontend/src/pages/legal/CreateCaseWizardModal.tsx` — **new** 439-LOC self-contained wizard
  - `frontend/src/lib/api.ts` — `createCase` + `setActiveCase` mutations
  - `frontend/src/pages/LegalPage.tsx` — button wiring + Cases-list DTO alignment fold-in fix
- **Handoff:** `docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **112 rows**
- **Merge SHA:** `52fd9aa55` (Phase 3.2) → close-cascade filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — Cases tab "New Case" button now opens the wizard. Post-merge post-recycle: create case → set as active in one flow; subsequent drafter dispatches will bind `case_profile` correctly per P1.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2806 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/**3.2** ✅; Phase 3.1 P1.b NEXT candidate (S2807) |
| NEW arc candidate | Wizard route extraction (deferred per row-112 fold; 3 trigger conditions); attorney sub-forms (conditional) |
| Group 2700 docs arc | Still queued (blocked behind Colorado arc) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-3c492806c55149e9` (retired at S2806 close, force=true, thirty-seventh consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-3c492806c55149e9` (retired; forces fresh mint at S2807 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2806 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 post-merge event during S2806 (+ close-cascade recycle to come) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **112 rows** |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable; ✅ visible in UI; ✅ CaseProfile-backed; ✅ **case creation now user-driven via wizard (Phase 3.2)** |
| Frontend `/legal` | ✅ Draft + view flow live; Cases tab reads CaseProfile with corrected DTO; **New Case wizard live** |
| Next move | Phase 3.1 P1.b LegalResearchResult unification (default) OR Phase 4a form-selection (Chris redirect) |

---

## Recommended session-open protocol (S2807)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2806 handoff §2 (Rigby SIGN + folds) + §3 (novel-precedent moments) + §6 (S2807 candidates)
4. **Read `core/models_unified_system.py` around line 17612** — `save_legal_research` (P1.b target)
5. **`Grep 'LegalResearchResult' core/`** — enumerate all usages + check for existing `case_profile` FK on the model
6. **Freshness + ledger 112 verify** — see S2807 open sequence above
7. If `staleness_verdict != FRESH` → escalate
8. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
9. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
10. **Default candidate: Phase 3.1 P1.b LegalResearchResult unification** (or Chris redirect to Phase 4a form-selection intelligence)
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
12. Chris directs S2807 P0 selection
13. Mint fresh pin scoped `s2807-<label>`
14. Route P1.b scope through Rigby joint SIGN before authoring
15. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
16. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
17. **Anchor-verify at open (S2806 lesson 1):** any factual claim in this file about live code state MUST be re-verified via live query before scope authoring
18. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2807:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`](docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md) — **S2806 handoff (current)**
3. [`core/models_unified_system.py`](core/models_unified_system.py) — `save_legal_research` at ~17612 (P1.b target)
4. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — reference P1 pattern for P1.b mirror (`_save_legal_document` at ~2298-2361)
5. [`core/models_legal.py`](core/models_legal.py) — CaseProfile model (unchanged since P1)
6. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
8. [`docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md`](docs/handoffs/SESSION_2805_COLORADO_FAMILY_LAW_PHASE3_1_P1_CASEPROFILE_UNIFICATION.md) — S2805 predecessor (P1 pattern)
9. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 112 rows at S2806 close

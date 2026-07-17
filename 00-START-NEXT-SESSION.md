# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2802 CLOSED — Colorado Family Law P0 arc IN-FLIGHT (Phases 0/1/2/2.1 shipped; Phase 3 frontend polish is S2803 default)

**Refreshed 2026-07-16 (SESSION 2802 CLOSED — sixth consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802). Shape shift back to engineering after S2801's research/scoping ship. Chris directive at S2802 open 2026-07-16: `"Before we begin we need to redirect. We need that Colorado Family Law Agent working. That is the newest priority, not only does it work we need it to be perfect and that's you and Rigby's main task."` — overrode the S2801-queued Group 2700 docs arc (still queued, not cancelled). Chris scope at Phase 0 close: `"production-ready with tests security and polish"` → 5-phase plan. Three PRs shipped this session (Phase 1 IDOR-hardening + Phase 2 test coverage + Phase 2.1 service-boundary invariants); 34 new tests all pass in <2s; two OVERSTATED Phase 0 claims caught in joint-SIGN loop BEFORE substrate work (Celery AsyncResult wire + CeleryTaskEvent gap — both NO-OPs). Ledger 93 → 101 (rows 94-97 Phase 1; 98-101 Phase 2). Anti-rubber-stamp check PASSED both SIGN cycles. FORTYSIXTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2802 ships (3 PRs merged, all `--admin`):**

| Phase | PR | Merged to | Tests | Focus |
|---|---|---|---|---|
| 1 — security | **#3218** · `affe40a0b` | `336cd757d` | 8 | 4 view + 2 service unscoped-query refactors → `.filter(id=X, case_profile__user=user).first()` |
| 2 — test coverage | **#3219** · `2f60abc88` | `c9ec280f9` | 22 | Agent execution + models (T1-T9 + M1-M5) |
| 2.1 — service invariants | **#3220** · `27c0b4ee5` | `8e11b92b5` | 4 | Services fail-fast on raw IDs (IDOR contract) |

**Handoff:** `docs/handoffs/SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **101 rows** (rows 94-97 Phase 1 folds; rows 98-101 Phase 2 folds).

**Arc state:** Colorado Family Law production-hardening — **Phases 0/1/2/2.1 ✅**; Phase 3 (frontend polish + disclaimer + audit-log gate) **NEXT**; Phase 4 (statute-citation quality) queued; Phase 5 (spider beat schedule) queued.

---

## SESSION-OPEN INFRA STORY (S2802)

**Sixth consecutive same-day multi-ship session; shape-shift back to engineering.** Discipline held cleanly across the S2801 research/scoping ship → S2802 engineering ship boundary. PLAYBOOK-6.10.7/6.10.8/6.10.9 applied identically. Recycle-after-merge discipline (PLAYBOOK-7.4.4) held across three consecutive same-session PR merges.

**First arc where Phase 0 verification caught two overstated Phase 0 claims BEFORE substrate work.** Both were extrapolations from single-query timing races (Celery AsyncResult wire + CeleryTaskEvent gap). Direct DB query + own follow-up read (not just Rigby SIGN) proved both were NO-OPs. Would have shipped fixes for non-bugs otherwise. Reinforces `feedback_verify_rigby_tool_runs_before_trusting_sign` — but also reinforces the value of direct-verification alongside SIGN.

**First OpenAI network-outage recovery mid-arc.** Three consecutive Responses API `Connection error` failures killed Phase 1 Rigby SIGN follow-up. Network isolation probe (curl to api.openai.com + api.anthropic.com + google.com + DNS) confirmed local network outage. Chris switched to phone hotspot; connectivity restored; SIGN retry succeeded.

**Rigby joint SIGN substantive both cycles.** Phase 1: 7+ tool_runs; SIGN-WITH-EDITS; surfaced bonus `views_legal.py:1281` + `litigation_brain.py:869` finding + service-boundary Fold 1 that drove A scope expansion. Phase 2: 11+ tool_runs; SIGN-WITH-EDITS; surfaced `_detect_denied_motion_mode` paths 3+4 broadness (false-positive risk) + T9 addition (upgraded Fold 1 from mitigatable to actionable). Both cycles: anti-rubber-stamp check PASSED per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

**Three-consecutive same-arc PRs in one session.** Small, focused, reviewable. Full `make recycle-all` between each per PLAYBOOK-7.4.4. Fortythird → fortyfourth → fortyfifth clean recycles.

---

## S2803 CANDIDATES — PHASE 3 FRONTEND POLISH IS THE DEFAULT

### ⭐ Phase 3 — Frontend polish + disclaimer + audit-log gate (default candidate)

**Shape:** Colorado Family Law production-hardening arc, Phase 3 (frontend). Chris ratified at S2802 close (2026-07-16): fresh session for Phase 3 = better for context (Phase 3 is bigger than Phase 1/2/2.1 combined).

**Scope (mandatory floor per Rigby Phase 0 SIGN Fold 3 — dogfood-vs-productize risk):**

1. **Draft-new-motion button** on `LegalPage.tsx` — currently NO discoverability; only Rigby-chat can trigger drafting. Adds a top-level "New Motion" button on `/legal` overview tab.
2. **Case creation wizard** — currently no way to create a `LegalCase` from UI; Phase 0 verification proved documents pile up ungrouped (`case_id=None`). Add wizard: case number + type + county + court + petitioner/respondent parties.
3. **Disclaimer banner** displayed in UI — currently only in Python docstrings; Session 404D stripped from generated content itself (per `core/agents/legal/legal_doc_drafter_agent.py:1260-1261`). MUST be surfaced in UI as "This is general legal information, not legal advice. Consult a licensed attorney."
4. **Live drafting state** — "Drafting… (typically 1-3 min)" spinner while Celery task runs; poll `cockpit_tool.task_status` OR new dedicated `/api/legal/draft-status/<task_id>/` endpoint.
5. **Audit-log of document generation** — every draft dispatch logged with `{user_id, task_id, task_description, timestamp, ip, user_agent}` for compliance. **Non-negotiable for real-user deployment per Rigby Fold 3.**
6. **User-profile pre-fill** of template placeholders — `[PETITIONER NAME]` → user's full name; `[Address]` → user profile address; etc. Requires extending User profile schema (may punt to Phase 3.1).

**Anti-goal:** do NOT ship Phase 3 UI without disclaimer + audit-log gate. Rigby Fold 3 codifies this as a floor.

**Recommended S2803 flow:**
1. Fresh mint of pin scoped `s2803-colorado-family-law-phase3-frontend`
2. Read parent Phase 0 verification artifact (`LegalDocument 475d83a1-df74-49b1-bb06-b04b63bd4ea8` still in local DB)
3. Read `LegalPage.tsx` end-to-end + `legalApi` surface + `CaseProfile`/`LegalCase` model shapes
4. Scope proposal to Chris → Rigby joint SIGN with zoom-out
5. Iterate on components (Draft button → Case wizard → Disclaimer → Live state → Audit log)
6. Cypress or Playwright E2E test if practical
7. Merge with `--admin`; recycle; verify in browser
8. Close-cascade

### Alternate candidates (if Chris deprioritizes Phase 3)

- **Phase 4** (statute-citation content quality) — smaller; agent-side content fix, no frontend
- **Phase 5** (monthly beat schedule for `colorado_family_law_spider`) — small; ops-side only
- **Small follow-ups** (single small PRs each):
  - `LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening
  - `LegalDocument.generation_context` add `blank=True` (model quirk from Phase 2)
  - PA→Celery E2E integration test (per Rigby Phase 2 SIGN Fold 4)
  - 7,829-line `legal_doc_drafter_agent.py` mechanical split into `agents/legal/` submodules (per Rigby Phase 2 SIGN Fold 3)

- **BettingPage** (pre-existing S2802-pre default; still owed after Colorado arc closes)
- **Stock Intelligence** (first non-betting revenue play; behind BettingPage)
- **Group 2700 docs restructuring arc** (T1 = 2701 inventory audit; queued but not cancelled)

---

## SESSION PIN — S2802 RETIRED (fresh mint required at S2803 open)

**Pin history (S2802):**

- `pa-b83fbf23da724c65` (label `s2802-colorado-family-law-prod-hardening`) minted S2802 open; **retired at S2802 close (`force=true`, thirtythird consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-b83fbf23da724c65` (retired)** — intended failure mode forces S2803 first-action fresh mint.

**S2803 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2802 handoff — §2 novel-precedent moments + §3 Rigby SIGN cycles + §4 Phase 0 findings + §7 Phase 3 scope
# Read core/agents/legal/legal_doc_drafter_agent.py:1260-1261 (Session 404D disclaimer strip — critical context for Phase 3)
# Read frontend/src/pages/LegalPage.tsx end-to-end
# Read frontend/src/lib/api.ts:1539-1568 (legalApi surface)
# Read core/models_legal.py — CaseProfile shape (Phase 3 wizard target)

# Freshness check. Should be FRESH · SHA-match at S2802 close-cascade SHA.
bash tools/pa_local.sh "S2803 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 101-row baseline survived S2802 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==101, r
print('OK — 101 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to Phase 3
python manage.py session_lifecycle open --label s2803-colorado-family-law-phase3-frontend

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2803 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; concrete code-state claims MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline.

**S2802 lessons to carry:**

1. **Two overstated Phase 0 claims caught in loop.** Extrapolating from a single query timing → assuming defect. Always verify with direct DB query / own read BEFORE proposing a fix. Both SIGN + own-verification are complementary; neither alone is sufficient.
2. **Multi-PR same-session shape works cleanly** with `--admin` merge + `make recycle-all` between each. Small, focused, reviewable PRs beat one mega-PR.
3. **Rigby's tool-grounded verification caught 2 bonus findings** the initial scope missed (unscoped `views_legal.py:1281` + `litigation_brain.py:869`). Route real verification asks, not summary asks.
4. **OpenAI network outage is diagnosable** with curl/dig/ping in ~30s. Don't assume upstream; verify network first.
5. **Phase 0 (live E2E verification) is a load-bearing pattern** — informs Phase 1+ scope with concrete artifacts (`LegalDocument 475d83a1…`), not hypothetical shape.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2802 artifacts:**

- **Substrate changes:** `core/views_legal.py` + `core/services/litigation_brain.py`
- **Test files (4 new):**
  - `core/tests/test_legal_cross_user_access.py`
  - `core/tests/test_legal_agent_execution.py`
  - `core/tests/test_legal_models.py`
  - `core/tests/test_legal_service_boundary.py`
- **Handoff:** `docs/handoffs/SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 101 rows
- **Merge SHAs:** Phase 1=`affe40a0b`→`336cd757d`; Phase 2=`2f60abc88`→`c9ec280f9`; Phase 2.1=`27c0b4ee5`→`8e11b92b5`; close-cascade=filled at merge
- **Predecessor:** S2801 (Group 2700 docs restructuring arc parent scoping — queued, not cancelled)

🖥️ **Workspace UI — `/workspaces` surface:**

- **`/legal` LegalPage.tsx** — visible; renders `LegalDocument 475d83a1…` for chris (Phase 0 verification artifact); has NO drafting UI (Phase 3 target)
- **Twin workspace deliverable:** N/A this session; substrate ships directly
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **101 rows**
  - `logs/recycle_events.jsonl` — +4 events during S2802 (3 post-merge + 1 close-cascade)
  - `http://localhost:8000/legal` — LegalPage, functional, no drafting UI

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2802 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law P0 hardening — Phases 0/1/2/2.1 shipped; Phase 3 NEXT |
| Group 2700 docs arc | Still queued (parent-scoping shipped at S2801 PR #3216); children 2701..2706 not-started |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-b83fbf23da724c65` (retired at S2802 close, force=true, thirtythird consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-b83fbf23da724c65` (retired; forces fresh mint at S2803 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2802 open |
| Recycle log | `logs/recycle_events.jsonl` — +4 events during S2802 |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **101 rows** |
| Rigby signposts | 14 tools routed via `unified_pa_entrypoint.py:2799` (unchanged since S2799) |
| Worker reap metric | `[CELERY_WORKER_STARTUP_REAP]` continues logging every restart (S2800 handler stable) |
| Colorado Family Law agent status | ✅ Works E2E; security hardened; 34 tests |
| Frontend `/legal` | Functional; renders documents; **NO drafting UI** (Phase 3 target) |
| Next move | Phase 3 default per S2802 close ratification (Chris: "fresh session for 3") |

---

## Recommended session-open protocol (S2803)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2802 handoff §2 (novel-precedent moments) + §3 (Rigby SIGN cycles) + §4 (Phase 0 findings) + §7 (Phase 3 scope)
4. **Read `core/agents/legal/legal_doc_drafter_agent.py:1260-1261`** (Session 404D disclaimer strip — critical Phase 3 context)
5. **Read `frontend/src/pages/LegalPage.tsx`** end-to-end (Phase 3 substrate target)
6. **Read `frontend/src/lib/api.ts:1539-1568`** (`legalApi` surface — what's already wired)
7. **Read `core/models_legal.py` `CaseProfile` class** (Phase 3 case-wizard target)
8. **Freshness + ledger 101 verify** — see S2803 open sequence above
9. **Watch for** ledger 101-row baseline surviving cascade merge; freshness FRESH · SHA-match
10. If `staleness_verdict != FRESH` → escalate
11. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
12. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
13. **Default candidate: Phase 3 frontend polish** (draft button + case wizard + disclaimer + live state + audit log + user-profile pre-fill). Full instructions in `## S2803 CANDIDATES` section above.
14. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
15. Chris directs S2803 P0 selection (Phase 3 unless override)
16. Mint fresh pin scoped `s2803-colorado-family-law-phase3-frontend`
17. Route Phase 3 scope through Rigby joint SIGN before authoring
18. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
19. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
20. **Phase 3 non-negotiables (Rigby Phase 0 SIGN Fold 3):** disclaimer banner + audit-log MUST ship together with the draft-new-motion button. Do NOT ship the UI without them.
21. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2803:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md`](docs/handoffs/SESSION_2802_COLORADO_FAMILY_LAW_P0_HARDENING.md) — **S2802 handoff (current)**
3. [`frontend/src/pages/LegalPage.tsx`](frontend/src/pages/LegalPage.tsx) — Phase 3 substrate target
4. [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts) — `legalApi` at line 1539-1568
5. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — agent (7,829 lines; disclaimer strip at :1260-1261)
6. [`core/views_legal.py`](core/views_legal.py) — API surface (Phase 1-hardened at 4 view sites)
7. [`core/models_legal.py`](core/models_legal.py) — `CaseProfile` (case wizard target)
8. [`core/models_unified_system.py`](core/models_unified_system.py) — `LegalCase` line 17114 + `LegalDocument` line 17252
9. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
10. [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) — **anchor for user-ready reasoning**
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
12. [`docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md`](docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md) — S2801 predecessor (Group 2700 docs arc parent scoping)
13. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 101 rows at S2802 close

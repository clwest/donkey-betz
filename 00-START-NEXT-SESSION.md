# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2808 CLOSED (late-night close 2026-07-17; picks up tomorrow as S2809) — Colorado Family Law Phase 4a SHIPPED

**Refreshed 2026-07-17 late-night (SESSION 2808 CLOSED — twelfth-consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → S2806 → S2807 → S2808). Phase 4a shipped (PR #3233 `e2f33cecd8fd`) — first user-facing intelligence surface of the Colorado arc: "Pick a Form" button on /legal opens self-contained modal (`FormPickerModal.tsx` 280 LOC); user describes situation → rule-based keyword classifier scores against RELIEF_TYPE_KEYWORDS (7 relief types, primary 3× + signals 1×); returns top match + top-2 alternates + confidence band (high/medium/low/none) + clarifying questions when low + disclaimer. Backend `_recommend_form` method — no LLM, no DB writes. `POST /api/legal/select-form/` endpoint. Full legal suite 71 tests OK (10 new). Anchor-verify at open reduced scope from 'build intelligence' to 'build missing surface' — JDF_FORM_MAPPING catalog + statutory framework + drafter prompt injection already existed since Sessions 404/1035. Rigby SIGN Q4 fold row 114 (`same_pr_actionable`) mitigated in-arc. FIFTY-SECOND close-cycle post-PLAYBOOK-7.4.4. **Chris wrapping for the night; S2809 is a fresh-morning re-open.**)**

**S2808 ship (1 PR, merged with --admin):**

| Phase | PR | Merged to | Focus |
|---|---|---|---|
| 4a | **#3233** · `e2f33cecd8fd` | main | RELIEF_TYPE_KEYWORDS + `_recommend_form` rule-based method + POST /api/legal/select-form/ + FormPickerModal.tsx (new, 280 LOC) + LegalPage "Pick a Form" button + 10 F/E regression tests |

**Handoff:** `docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (row 114 P4a fold: redundancy risk `same_pr_actionable`, mitigated in-arc via rule-based + read-only substrate scoping).

**Arc state at S2808 close:** Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/**4a** ✅. **All correctness substrate + one wizard capability + one intelligence surface shipped.** Phase 4 (statute-citation quality) + Phase 4b (LLM upgrade for form-selection) + Phase 5 (spider beat) all queued.

---

## CROSS-DAY RESUME NOTES (S2808 → S2809)

**Overnight state to expect on re-open:**

- Local `postgresql@15` (July DB) is `brew launchd started` — should survive overnight unless macOS reboots. If freshness check fails at S2809 open, check `brew services list | grep postgres` FIRST per `feedback_post_travel_port_collision_triage` (fossil pg16 could grab port).
- Daphne, Celery, Redis all started by S2808 close-cascade `make recycle-all`; may still be running tomorrow. If not, `make restart` re-brings them up.
- Session pin `pa-468038b5c9764cc3` retired; wrapper still points at it (intended failure mode — first S2809 action mints fresh).
- Zoom-out ledger at **114 rows**; freshness log has +1 from S2808 open; recycle log has +2 from S2808 (post-merge + close-cascade).
- HEAD advances at close-cascade PR merge (this cycle).

---

## S2809 CANDIDATES — CHRIS PICKS FRESH

**No default candidate this time.** Colorado arc has natural "next" options in every size class; no scope pressure to continue one over another. Chris picks direction fresh at S2809 open.

### Small / mechanical

- ⭐ **P1-back-port test hardening**: retrofit T6b (LegalDocument path) with `assertLogs('WARNING')` to codify S2805 Lesson 3 observably (matching T7b delta shipped at S2807). Small; ~30 LOC. Cleanest warm-up if Chris wants low-friction morning ship.
- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **`LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening** (Phase 2 punt)

### Medium

- **Phase 4 — Statute-citation content quality**: C.R.S. § 14-10-129 + "substantial and continuing change of circumstances" standard language quality
- **Phase 5 — Spider beat schedule**: monthly refresh for `colorado_family_law_spider`
- **Attorney sub-form on Case Wizard** when `!is_pro_se` (row-112 emergent from Phase 3.2)
- **GPT fallback for form-selection** when keyword-match is low-confidence (row-114 emergent from Phase 4a)

### Large

- **Phase 4b — LLM-based situation intelligence** (upgrade Phase 4a rule-based classifier with GPT for ambiguous descriptions; possibly consolidate with the drafter's existing prompt-injection path)
- **Wizard extraction to `/legal/cases/new` route** (row-112 emergent; triggers: deep-link, draft-persistence, browser-back)
- **7,829-line `legal_doc_drafter_agent.py` mechanical split** into `agents/legal/` submodules

### Non-Colorado arcs (still queued)

- **Group 2700 docs restructuring arc** (queued since S2801)
- **BettingPage first-user trace** (pre-Colorado default)
- **Stock Intelligence** (first non-betting revenue play)

---

## SESSION PIN — S2808 RETIRED (fresh mint required at S2809 open)

**Pin history (S2808):**

- `pa-468038b5c9764cc3` (label `s2808-colorado-family-law-phase4a-form-selection`) minted S2808 open; **retired at S2808 close (`force=true`, thirty-ninth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-468038b5c9764cc3` (retired)** — intended failure mode forces S2809 first-action fresh mint.

**S2809 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2808 handoff — §3 (novel-precedent), §6 (candidates), §7 (cross-day notes)
# Chris picks direction; label pin accordingly

# If services aren't running from overnight: make restart
# Check freshness FIRST if anything looks off:
brew services list | grep postgres   # confirm pg15 started, not pg16

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to Chris's direction
python manage.py session_lifecycle open --label s2809-<direction>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2809 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2808 lessons to carry:**

1. **When scope has multiple valid shapes, ASK the shape as a menu (A/B/C).** Phase 4a's Rigby SIGN Q1 offered three shapes; her grounded pick (Option C, matching Phase 3.2) was better than defaulting to any one. Substrate lesson: don't pick the shape for Rigby — let her pick with tool-grounded reasoning.
2. **Anchor-verify continues to be the load-bearing scope-shaping step, not a formality.** Seventh consecutive session where live-code check materially reduced or reframed handoff scope. Trend line: budget time for anchor-verify at every session open.
3. **Rule-based deterministic classifiers ship faster than LLM classifiers AND are more testable.** Phase 4a's keyword-match got to 10/10 tests green first-run in single-shot. GPT fallback deferrable to when the rule-based approach demonstrably misses.
4. **"Additive-only" scope discipline works.** Phase 4a touched 7 files but zero existing consumers of the underlying data. Read-only substrate treatment (Rigby SIGN Q3) kept blast radius bounded.
5. **`make frontend-ship` is the correct local deploy step for frontend-only PRs.** Skip celery recycle when no PA tool / model / handler / task changed. Post-merge `make recycle-all` still runs per PLAYBOOK-7.4.4 for consistency.

---

## Twin-pointer card

📁 **Repo — S2808 artifacts:**

- **PR (1, merged):** #3233 (Phase 4a · `e2f33cecd8fd`)
- **Substrate changes:**
  - `core/agents/legal/legal_doc_drafter_agent.py` — `RELIEF_TYPE_KEYWORDS` + `_recommend_form`
  - `core/views_legal.py` — `select_legal_form` DRF view
  - `core/urls.py` — endpoint registered
  - `frontend/src/lib/api.ts` — `legalApi.selectForm`
  - `frontend/src/pages/legal/FormPickerModal.tsx` — **new** self-contained modal
  - `frontend/src/pages/LegalPage.tsx` — "Pick a Form" button + modal render
- **Test files:** `core/tests/test_legal_form_selection.py` (**new**, 10 tests, 170 LOC)
- **Handoff:** `docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows**
- **Merge SHA:** `e2f33cecd8fd` (Phase 4a) → close-cascade filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — new "Pick a Form" button in the header (next to "Draft New Motion"). Click → modal with textarea + optional case-type → submit → recommendation card renders with confidence badge, form number/title, criteria, required attachments, filing notes, alternates (top 2), and clarifying questions if confidence is low.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state (S2808 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2808 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/**4a** ✅. **Correctness + case wizard + form-selection all shipped.** |
| Emergent candidates | GPT fallback for form-selection (row-114); attorney sub-forms on wizard (row-112); wizard route extraction (row-112); Phase 4b LLM upgrade (P4a natural progression) |
| Group 2700 docs arc | Still queued (blocked behind Colorado arc) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-468038b5c9764cc3` (retired at S2808 close, force=true, thirty-ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-468038b5c9764cc3` (retired; forces fresh mint at S2809 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2808 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 during S2808 (post-merge + close-cascade) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable; ✅ visible in UI; ✅ CaseProfile-backed (both LegalDocument P1 + LegalResearchResult P1.b); ✅ case creation user-driven via wizard (Phase 3.2); ✅ **form-selection user-driven via Pick-a-Form (Phase 4a)** |
| Frontend `/legal` | ✅ Draft + view + wizard + form-picker all live |
| Next move | Chris picks direction fresh at S2809 open |

---

## Recommended session-open protocol (S2809, fresh morning)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2808 handoff §3 (novel-precedent) + §6 (candidates) + §7 (cross-day notes)
4. **Overnight sanity check:** `brew services list | grep postgres` — confirm pg15 started
5. **Services check:** `curl -s http://localhost:8000/health/ping/` — if not OK, `make restart`
6. **Freshness + ledger 114 verify** — see S2809 open sequence above
7. If `staleness_verdict != FRESH` → escalate (post-travel triage per `feedback_post_travel_port_collision_triage`)
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. **Chris picks direction** — see §S2809 CANDIDATES above; ⭐ suggests P1-back-port test hardening as smallest warm-up
10. Mint fresh pin scoped `s2809-<Chris's-direction>`
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
12. Route scope through Rigby joint SIGN before authoring
13. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
15. **Anchor-verify at open (S2806-S2808 lesson, now 7-session trend):** any factual claim in this file about live code state MUST be re-verified via live query before scope authoring
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2809:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md`](docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md) — **S2808 handoff (current)**
3. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — main legal agent (RELIEF_TYPE_KEYWORDS + `_recommend_form` now live; JDF_FORM_MAPPING catalog still read-only)
4. [`core/tests/test_legal_form_selection.py`](core/tests/test_legal_form_selection.py) — 10 P4a regression tests
5. [`core/tests/test_legal_agent_drafting_reliability.py`](core/tests/test_legal_agent_drafting_reliability.py) — T6/T7 pattern for reference (T6b back-port candidate)
6. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
8. [`docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md`](docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md) — S2807 P1.b predecessor
9. [`docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md`](docs/handoffs/SESSION_2806_COLORADO_FAMILY_LAW_PHASE3_2_CASE_WIZARD.md) — S2806 wizard predecessor
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2808 close

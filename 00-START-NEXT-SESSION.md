# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2810 CLOSED (mid-afternoon close 2026-07-18; picks up as S2811) — Attorney sub-form on Case Wizard SHIPPED

**Refreshed 2026-07-18 mid-afternoon (SESSION 2810 CLOSED — fourteenth-consecutive same-day multi-ship session and FIRST back-to-back same-day multi-ship pair (S2809 + S2810 both closed on 2026-07-18). Attorney sub-form on Case Wizard (row-112 emergent) shipped as PR #3237 `7de622f24` — inline expand under the pro-se checkbox in `CreateCaseWizardModal.tsx`; 9 attorney fields; frontend-only patch (+129/-2 LOC). Backend at `core/views_legal_cases.py:96-160` already handled the payload — this shipped 90%-built substrate that was only missing wizard input. Value unlock: attorney data flows into (a) motion drafting via `respondent_counsel_*` prompt injection at `legal_doc_drafter_agent.py:4612-4620`, (b) `CaseProfile.get_conferral_recipient()` for correctly-addressed conferral emails. THREE anchor-verify catches this session including a mid-session scope pivot: audit clean → Phase 5 spider beat scoped → Rigby AGREE → anchor-verify catch (spider is hardcoded static list per Session 534 punt) → Phase 5 rejected → attorney sub-form picked → anchor-verify catch (backend already handles) → scope reduced to frontend-only → Rigby AGREE → ship. FIFTY-FOURTH close-cycle post-PLAYBOOK-7.4.4.**

**S2810 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Attorney sub-form | **#3237** · `7de622f24` | main | `frontend/src/pages/legal/CreateCaseWizardModal.tsx` (+129/-2) — AttorneyForm interface + AttorneySection component + PartySection inline expand + payload guard |

**Handoff:** `docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged; no folds persisted this session).

**Arc state at S2810 close:** Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 **(+attorney sub-form)** /3.1 P1.b/4a ✅. Correctness substrate + wizard capability with attorney intake + form-selection all shipped.

**Anti-Lesson-3 audit finding (folded into S2810 handoff §4):** `core/agents/legal/**` sweep clean after S2809 back-port. Only one `except X: pass` hit (`legal_doc_drafter_agent.py:3836` ValueError in date parser — legitimate feature-detection). No further PR needed; scope closed.

---

## S2811 CANDIDATES — CHRIS PICKS FRESH

### Small / mechanical

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **`LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening** (Phase 2 punt)

### Medium

- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129 standard language)
- **⭐ NEW: Phase 5.1 — un-punt Session 534.** Restore live scraping in `colorado_family_law_spider.fetch_data` (currently returns hardcoded static list). AJAX wrangling with unknowable time budget; treat as its own arc.
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)

### Large

- **Phase 4b** — LLM-based situation intelligence (P4a natural upgrade)
- **Wizard extraction to `/legal/cases/new`** route (row-112 emergent; deep-link + draft-persistence + browser-back)
- **7,829-line `legal_doc_drafter_agent.py`** mechanical split

### Non-Colorado (queued)

- **Group 2700 /docs restructuring** (directed S2800 close; 14 sessions bumped)
- **BettingPage first-user trace**
- **Stock Intelligence**

---

## SESSION PIN — S2810 RETIRED (fresh mint required at S2811 open)

**Pin history (S2810):**

- `pa-8199cbf50c6e44ac` (label `s2810-legal-doesnotexist-bareexcept-audit` — kept original label despite mid-session pivot) minted at S2810 open; **retired at S2810 close (`force=true`, forty-first consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-8199cbf50c6e44ac` (retired)** — intended failure mode forces S2811 first-action fresh mint.

**S2811 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2810 handoff — §3 (novel-precedent), §6 (candidates)
# Chris picks direction; label pin accordingly

# If services aren't running: make restart
# Check freshness FIRST if anything looks off:
brew services list | grep postgres

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2811-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2811 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2810 lessons to carry:**

1. **Anchor-verify can trigger MID-SESSION scope pivots, not just at open.** The Colorado Family Law spider `fetch_data` hardcoded-list finding surfaced only when I dug into `max_results=20` after Rigby's Q3 zoom-out. Substrate rule: anchor-verify isn't a session-open-only ritual — verify at every scope decision point during the session too.
2. **Predicate substrate + missing surface is a high-leverage ship shape.** Attorney sub-form: backend was 90% built (payload handling, drafter consumer, conferral-recipient logic) but zero wizard input. 129 LOC of frontend flipped on two backend consumers that had been waiting. Watch for this shape more often — "the plumbing exists; the tap is missing."
3. **Rigby's tool-grounded SIGN found the value chain I missed.** I framed the attorney sub-form as "collect attorney data." Her Q3 zoom-out tool_runs surfaced the drafter-prompt-injection consumer at line 4612-4620 that I hadn't checked. The joint SIGN pattern earns its keep at exactly these moments — she sees consumers I don't.
4. **Warm-up cascades stack.** S2809 (P1 back-port ~54 LOC) → S2810 audit (null result → recorded) → S2810 attorney sub-form (129 LOC). Two feature ships + one governance record + two full close cascades in one day, all warm-up-scale. Session cost per ship stays low.
5. **Session 534's punts are recoverable.** The Colorado Family Law spider had complete Playwright infrastructure (`start_browser`, `fetch_forms_page`, `search_forms`) — Session 534 walked away from all of it and shipped the hardcoded fallback. A future Phase 5.1 arc can un-punt with fresh eyes and modern Playwright selectors.

---

## Twin-pointer card

📁 **Repo — S2810 artifacts:**

- **PR (1, merged):** #3237 (attorney sub-form · `7de622f24`)
- **Substrate change:**
  - `frontend/src/pages/legal/CreateCaseWizardModal.tsx` — +129/-2 LOC (AttorneyForm interface + EMPTY_ATTORNEY + AttorneySection component + PartySection inline-expand + handleSubmit validation + payload guard)
- **Handoff:** `docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged; no folds persisted this session)
- **Merge SHA:** `7de622f24` (feature) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — click "New Case" → wizard opens → uncheck "Representing self (pro se)" on Petitioner or Respondent → attorney sub-form inline expands with 9 fields (full_name required, others optional including bar_number with placeholder "e.g. 12345 (if known)") → submit creates both Party + Attorney rows in one round-trip.
- **Downstream visibility:** Motion drafts for cases with attached attorneys now include correctly-named opposing counsel + firm + address via `respondent_counsel_*` prompt injection. Conferral-recipient emails route to opposing counsel when represented.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state (S2810 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2810 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. Anti-Lesson-3 audit clean. Phase 5 as originally scoped rejected (spider is hardcoded); Phase 5.1 (un-punt Session 534) queued. |
| Emergent candidates | Phase 5.1 (un-punt Session 534 AJAX scraping); wizard extraction to /legal/cases/new (row-112); all prior S2808/S2809 candidates still queued |
| Group 2700 docs arc | Still queued (14 sessions bumped since S2800 directive) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-8199cbf50c6e44ac` (retired at S2810 close, force=true, forty-first consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-8199cbf50c6e44ac` (retired; forces fresh mint at S2811 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2810 open |
| Recycle log | `logs/recycle_events.jsonl` — +4 today across S2809+S2810 (2 per session: post-merge + close-cascade) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged) |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable; ✅ visible in UI; ✅ CaseProfile-backed (P1 Lesson-3 hardened + P1.b); ✅ case creation user-driven via wizard (Phase 3.2 + **attorney sub-form**); ✅ form-selection user-driven via Pick-a-Form (Phase 4a) |
| Frontend `/legal` | ✅ Draft + view + wizard (+attorney) + form-picker all live |
| Next move | Chris picks direction fresh at S2811 open |

---

## Recommended session-open protocol (S2811, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2810 handoff §3 (novel-precedent) + §6 (candidates)
4. **Sanity check:** `brew services list | grep postgres`
5. **Services check:** `curl -s http://localhost:8000/health/ping/`
6. **Freshness + ledger 114 verify** — see S2811 open sequence above
7. If `staleness_verdict != FRESH` → escalate (post-travel triage per `feedback_post_travel_port_collision_triage`)
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. **Chris picks direction** — see §S2811 CANDIDATES above
10. Mint fresh pin scoped `s2811-<Chris's-direction>`
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
12. Route scope through Rigby joint SIGN before authoring
13. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
15. **Anchor-verify at open AND at every scope decision point (S2806-S2810 lesson, now 9-session trend; S2810 corollary: mid-session pivots need it too):** any factual claim about live code state MUST be re-verified via live query before scope decisions
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2811:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md`](docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md) — **S2810 handoff (current)**
3. [`frontend/src/pages/legal/CreateCaseWizardModal.tsx`](frontend/src/pages/legal/CreateCaseWizardModal.tsx) — Case Wizard modal (now with AttorneySection)
4. [`core/views_legal_cases.py`](core/views_legal_cases.py) — Case creation endpoint (line 96-160 handles Party + Attorney payload)
5. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — Motion drafter (line 4612-4620 consumes `respondent.attorney` for prompt injection)
6. [`core/models_legal.py`](core/models_legal.py) — Party (line 143+), Attorney (line 208+), `get_conferral_recipient` (line 107-121)
7. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
9. [`docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md`](docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md) — S2809 predecessor (same-day)
10. [`ai_core/spiders/specialized/colorado_family_law_spider.py`](ai_core/spiders/specialized/colorado_family_law_spider.py) — hardcoded static list at `fetch_data` (Session 534 punt; Phase 5.1 candidate to un-punt)
11. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2810 close (unchanged)

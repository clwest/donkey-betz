# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2809 CLOSED (mid-day close 2026-07-18; picks up as S2810) — P1-back-port Lesson-3 hardening SHIPPED

**Refreshed 2026-07-18 mid-day (SESSION 2809 CLOSED — thirteenth-consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801 → S2802 → S2803 → S2804 → S2805 → S2806 → S2807 → S2808 → S2809). Warm-up ship from the S2808 candidate menu: **P1 back-port** (PR #3235 `1f8b3ea4e5d2`) extracts a shared `_resolve_case_profile(id)` helper at module scope in `core/models_unified_system.py`. Both legal save paths — `save_legal_research` (S2807 P1.b) AND `_save_legal_document` (S2805 P1) — now call the same get-or-warn helper. Closes a live S2805-Lesson-3 violation in the document path (`except CaseProfile.DoesNotExist: pass` → helper call). T6b retrofit with `assertLogs('core.models_unified_system', 'WARNING')` + body assertions on `'CaseProfile'` + missing id, mirroring T7b exactly. Full T6+T7 classes 10/10 OK. Anchor-verify at open FLIPPED framing from "test-only ~30 LOC" to "code+test ~54 LOC" — first anchor-verify catch that inverted the CLASS of change, not just the size. Rigby SIGN Q3 zoom-out surfaced a **third** `except CaseProfile.DoesNotExist:` site at `legal_doc_drafter_agent.py:4579` (already warns, different context — active_case_id from session, not method-arg) with a proposed scoped audit of `DoesNotExist:pass` / bare-except patterns across `core/agents/legal/**` as future work. FIFTY-THIRD close-cycle post-PLAYBOOK-7.4.4.**

**S2809 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| P1 back-port | **#3235** · `1f8b3ea4e5d2` | main | `models_unified_system.py` (+helper, refactor P1.b block) · `legal_doc_drafter_agent.py` (helper call replaces silent-swallow) · `test_legal_agent_drafting_reliability.py` (T6b assertLogs retrofit) |

**Handoff:** `docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged; no folds persisted this session — Q3 zoom-out hit is a future-arc trigger, not a same-session fold).

**Arc state at S2809 close:** Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (**Lesson-3 hardened**)/3.2/3.1 P1.b/4a ✅. Correctness substrate + wizard capability + form-selection all shipped; anti-Lesson-3 substrate now reusable via `_resolve_case_profile` helper.

---

## S2810 CANDIDATES — CHRIS PICKS FRESH

### Small / mechanical

- **⭐ NEW: Scoped audit of `DoesNotExist:pass` / bare-except in `core/agents/legal/**`** — Rigby Q3 zoom-out hit from S2809. Small hitlist first, remediation PRs as follow-up per finding. Natural continuation of the anti-Lesson-3 arc thread.
- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **`LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening** (Phase 2 punt)

### Medium

- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5** — spider beat schedule for `colorado_family_law_spider`
- **Attorney sub-form on Case Wizard** (row-112 emergent)
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)

### Large

- **Phase 4b** — LLM-based situation intelligence (P4a natural upgrade)
- **Wizard extraction to `/legal/cases/new`** route (row-112 emergent)
- **7,829-line `legal_doc_drafter_agent.py`** mechanical split

### Non-Colorado (queued)

- **Group 2700 /docs restructuring** (directed S2800 close; now 13 sessions bumped)
- **BettingPage first-user trace**
- **Stock Intelligence**

---

## SESSION PIN — S2809 RETIRED (fresh mint required at S2810 open)

**Pin history (S2809):**

- `pa-126c19b80e504be2` (label `s2809-p1-back-port-hardening`) minted S2809 open; **retired at S2809 close (`force=true`, fortieth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-126c19b80e504be2` (retired)** — intended failure mode forces S2810 first-action fresh mint.

**S2810 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2809 handoff — §3 (novel-precedent), §6 (candidates)
# Chris picks direction; label pin accordingly

# If services aren't running: make restart
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
python manage.py session_lifecycle open --label s2810-<direction>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2810 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2809 lessons to carry:**

1. **Anchor-verify can invert the CLASS of change, not just size.** S2807 handoff framed P1 back-port as "test-only ~30 LOC". Live code check found the P1 document codepath still had `except DoesNotExist: pass` — flipping scope to code+test. Budget time for anchor-verify at every open; don't trust the predecessor's framing when the queued item is a code claim.
2. **Extract-shared-helper is the right shape when a get-or-warn pattern lives in >1 codepath.** Cost: +1 file. Value: unified logger namespace across tests (T6b + T7b both assert `'core.models_unified_system'`), DRY, one place to enforce the discipline. Next `case_profile_id` consumer inherits Lesson-3 for free.
3. **Rigby's zoom-out Q hit on real substrate again — third consecutive session.** Q3 found `legal_doc_drafter_agent.py:4579` as a third DoesNotExist site (already warns, different context). Substrate rule holding: when the zoom-out ask is grounded in tool_runs (not general prose), it finds real work every time.
4. **Warm-up ships work as warm-ups.** Chris opened S2809 with "let's start with the warm-up" from a menu that flagged the P1 back-port as ⭐. Shipped in ~1.5 hrs including full close cascade. Menu-with-⭐ at close is doing its job.

---

## Twin-pointer card

📁 **Repo — S2809 artifacts:**

- **PR (1, merged):** #3235 (P1 back-port · `1f8b3ea4e5d2`)
- **Substrate changes:**
  - `core/models_unified_system.py` — new `_resolve_case_profile()` module-level helper (before `class LegalResearchResult` line 17455)
  - `core/agents/legal/legal_doc_drafter_agent.py` — helper call replaces silent-swallow at lines 2520-2525
  - `core/tests/test_legal_agent_drafting_reliability.py` — T6b renamed + assertLogs + body assertions
- **Handoff:** `docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged; no folds persisted this session)
- **Merge SHA:** `1f8b3ea4e5d2` (P1 back-port) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible surface change.** Internal save-path behavior only. Observable via server logs: any `_save_legal_document` or `save_legal_research` call with an unknown `case_profile_id` now emits `WARNING core.models_unified_system CaseProfile id=<uuid> not found; caller will save with case_profile=None`.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## Current repository state (S2809 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2809 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Colorado Family Law — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (**Lesson-3 hardened**)/3.2/3.1 P1.b/4a ✅. Anti-Lesson-3 substrate now reusable via `_resolve_case_profile` helper. |
| Emergent candidates | Scoped audit of `DoesNotExist:pass` / bare-except across `core/agents/legal/**` (Rigby Q3 zoom-out); all prior S2808 candidates still queued |
| Group 2700 docs arc | Still queued (13 sessions bumped since S2800 directive) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-126c19b80e504be2` (retired at S2809 close, force=true, fortieth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-126c19b80e504be2` (retired; forces fresh mint at S2810 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2809 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 during S2809 (post-merge + close-cascade) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged) |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable; ✅ visible in UI; ✅ CaseProfile-backed (both LegalDocument P1 **now Lesson-3 hardened** + LegalResearchResult P1.b); ✅ case creation user-driven via wizard (Phase 3.2); ✅ form-selection user-driven via Pick-a-Form (Phase 4a) |
| Frontend `/legal` | ✅ Draft + view + wizard + form-picker all live (unchanged from S2808) |
| Next move | Chris picks direction fresh at S2810 open |

---

## Recommended session-open protocol (S2810, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2809 handoff §3 (novel-precedent) + §6 (candidates)
4. **Sanity check:** `brew services list | grep postgres` — confirm pg15 started
5. **Services check:** `curl -s http://localhost:8000/health/ping/` — if not OK, `make restart`
6. **Freshness + ledger 114 verify** — see S2810 open sequence above
7. If `staleness_verdict != FRESH` → escalate (post-travel triage per `feedback_post_travel_port_collision_triage`)
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. **Chris picks direction** — see §S2810 CANDIDATES above; ⭐ suggests scoped audit of `DoesNotExist:pass` if continuing the anti-Lesson-3 thread
10. Mint fresh pin scoped `s2810-<Chris's-direction>`
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
12. Route scope through Rigby joint SIGN before authoring
13. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
15. **Anchor-verify at open (S2806-S2809 lesson, now 8-session trend):** any factual claim in this file (or the predecessor handoff) about live code state MUST be re-verified via live query before scope authoring
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2810:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md`](docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md) — **S2809 handoff (current)**
3. [`core/models_unified_system.py`](core/models_unified_system.py) — `_resolve_case_profile` helper now lives here (line ~17455, before `class LegalResearchResult`)
4. [`core/agents/legal/legal_doc_drafter_agent.py`](core/agents/legal/legal_doc_drafter_agent.py) — main legal agent (lines 2520-2525 now call the helper; line 4579 is a still-independent DoesNotExist site, different context)
5. [`core/tests/test_legal_agent_drafting_reliability.py`](core/tests/test_legal_agent_drafting_reliability.py) — T6b now asserts `'core.models_unified_system'` warning + body strings
6. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
8. [`docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md`](docs/handoffs/SESSION_2808_COLORADO_FAMILY_LAW_PHASE4A_FORM_SELECTION.md) — S2808 P4a predecessor
9. [`docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md`](docs/handoffs/SESSION_2807_COLORADO_FAMILY_LAW_PHASE3_1_P1B_LEGALRESEARCHRESULT.md) — S2807 P1.b predecessor
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2809 close (unchanged from S2808)

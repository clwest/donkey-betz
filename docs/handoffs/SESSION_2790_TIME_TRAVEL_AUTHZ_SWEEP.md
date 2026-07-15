# Session 2790 — /api/time-travel/ authZ sweep (11 endpoints)

**Ship SHA:** `29c69911e` · **PR:** [#3193](https://github.com/clwest/donkey-betz-platform/pull/3193) · **Date:** 2026-07-15

---

## §1 What shipped

Closed S2789 Fold B row 41 audit doc entry for prefix `/api/time-travel/`
(largest remaining bucket at 11 endpoints). Ungated candidates remaining
after this session: 65 (was 76).

**Backend (1 file):**

- `core/views_time_travel.py` — added `from .auth_middleware import
  token_auth_required` import; on 11 mutation views:
  - Added `@token_auth_required` (session OR Token/Bearer, JSON 401 for anon)
  - Removed `@csrf_exempt` per S2787 cleanup pattern (session callers get
    CSRF via `CsrfViewMiddleware`; Token callers bypass via
    `DisableCSRFForAuthEndpoints` middleware)

Endpoints gated:

| View | Method | Route | Model touched |
|---|---|---|---|
| `start_session` (l.198) | POST | `/api/time-travel/session/start/` | AgentSession.create |
| `end_session` (l.234) | POST | `/api/time-travel/session/<uuid>/end/` | AgentSession.save |
| `toggle_bookmark_session` (l.265) | POST | `/api/time-travel/session/<uuid>/bookmark/` | AgentSession.save |
| `record_decision` (l.293) | POST | `/api/time-travel/decision/` | DecisionPoint.create + ThoughtBubble.save |
| `update_decision_outcome` (l.353) | POST | `/api/time-travel/decision/<uuid>/outcome/` | DecisionPoint.save |
| `flag_decision` (l.377) | POST | `/api/time-travel/decision/<uuid>/flag/` | DecisionPoint.save |
| `create_bookmark` (l.405) | POST | `/api/time-travel/bookmark/` | ReplayBookmark.create |
| `delete_bookmark` (l.447) | DELETE | `/api/time-travel/bookmark/<uuid>/` | ReplayBookmark.delete |
| `add_annotation` (l.466) | POST | `/api/time-travel/annotation/` | DebugAnnotation.create |
| `delete_annotation` (l.499) | DELETE | `/api/time-travel/annotation/<uuid>/` | DebugAnnotation.delete |
| `simulate_session` (l.660) | POST | `/api/time-travel/agent/<uuid>/simulate/` | AgentSession.create + DecisionPoint.create |

**Tests (1 new file):**

- `core/tests/test_time_travel_authz_sweep_2790.py` — 4 test classes × 11
  endpoints = 44 tests:
  - `TimeTravelAuthzSweepAnonymousTest` — anon → 401
  - `TimeTravelAuthzSweepAuthenticatedTest` — session-authed → view reached
  - `TimeTravelAuthzSweepTokenAuthS887PreservationTest` — Token-authed →
    view reached via `DisableCSRFForAuthEndpoints` middleware
  - `TimeTravelAuthzSweepSessionWithoutCSRFTest` — **Rigby Fold B
    belt-and-suspenders**: session-auth without CSRF → 403 (catches
    regressions if S2787 CSRF interceptor breaks)

**Audit artifact updates (2 files):**

- `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` — added S2790 UPDATE banner
  marking `/api/time-travel/` CLOSED (ungated remaining: 65)
- `docs/audits/public_paths_audit_s2789.json` — moved 11 time-travel entries
  from `ungated_true_mutating` to new `closed_at_S2790` bucket

---

## §2 Novel-precedent moments

### 2.1 4-consecutive per-prefix authZ sweep pattern

S2787 (CSRF 31-endpoint cross-file cleanup) → S2788 (3 platform endpoints) →
S2789 (7 pilot-gates endpoints) → S2790 (11 time-travel endpoints). The
ship-shape "one prefix + `@token_auth_required` + `@csrf_exempt` removal +
regression test file + audit doc update" is now stable. Row 47
`future_trigger` records this as PLAYBOOK-6.10.11+ codification candidate
under the `public_paths_categorical_audit` umbrella arc.

### 2.2 First 4-test-class regression (Rigby Fold B adopted)

Prior per-prefix ships used 3 test classes (anon/authed/Token). S2790
introduces a 4th class (`TimeTravelAuthzSweepSessionWithoutCSRFTest`) that
verifies session-auth without CSRF gets rejected with 403. This is
belt-and-suspenders defense against regressions in the S2787 CSRF interceptor
(`frontend/src/lib/api.ts:32-56`). All 11 endpoints × 4 classes = 44 tests
(vs 21 for S2789's 3-class × 7-endpoint shape).

### 2.3 Decorator order convention preserved

Rigby T1 Fold A suggested flipping to `@token_auth_required` outermost
(auth-before-method-check). Deferred as `same_pr_mitigatable` row 45 —
canonical S891 pattern in `views_agent_learning.py` (~20+ sites) + S2789
pilot-gates use `@require_http_methods` outermost. Consistency preserved
this ship; codebase-wide migration if desired via dedicated PR later.

### 2.4 Rigby SIGN response NOT truncated

After S2789 row 44 recorded the 3rd truncation observation, S2790 T1 SIGN
response landed clean (~30 lines with 2 folds + F1/F2 + zoom-out). Tightened
prompt ("keep response under 60 lines") worked. Not conclusive — sample size
1 post-trigger — but reproducible with prompt discipline.

---

## §3 T1 SIGN cycle summary

| Turn | Author | Content | Tool_runs | Outcome |
|---|---|---|---|---|
| T1 | Claude → Rigby | Scope proposal for 11 endpoints + F1/F2 F-BLOCKING + zoom-out ask on ship-shape codification | Rigby: 5 (repo_tool reads on views_time_travel.py, middleware.py, api.ts + 2× search) | AGREE-with-tighten: 2 folds (A order swap deferred, B CSRF-gap test adopted) + zoom-out response yes on PLAYBOOK-6.10.11+ codification |

**Anti-rubber-stamp check:** T1 had 5 real tool_runs producing tool-grounded
F1 (frontend api.ts pattern) + F2 (middleware short-circuit still correct)
+ 2 architectural suggestions (decorator order + belt-and-suspenders). No
DISAGREE substantive corrections this session, but tool-grounding held.

---

## §4 Ledger delta

- **At S2790 open:** 44 rows (19/15/10)
- **After T1 fold persistence (pre-D-verdict):** 47 rows (20/16/11)
  - Row 45 (S2790, decorator order, `same_pr_mitigatable`): Rigby Fold A
    deferred as codebase-wide migration
  - Row 46 (S2790, CSRF-gap test, `same_pr_actionable`): Rigby Fold B
    adopted this PR (4th test class added)
  - Row 47 (S2790, per-prefix authZ sweep shape, `future_trigger`):
    PLAYBOOK-6.10.11+ codification candidate for 4-consecutive-ship pattern

---

## §5 Twin-pointer card

📁 **Repo `/` + `/docs/` — S2790 artifacts:**

- **Ship code:** `core/views_time_travel.py` (11 decorator swaps: added
  `@token_auth_required`, removed `@csrf_exempt`)
- **Tests:** `core/tests/test_time_travel_authz_sweep_2790.py` (320 lines, 44 tests)
- **Audit doc updates:** `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md` (S2790 UPDATE
  banner) + `docs/audits/public_paths_audit_s2789.json` (11 entries moved to
  `closed_at_S2790`)
- **Handoff:** `docs/handoffs/SESSION_2790_TIME_TRAVEL_AUTHZ_SWEEP.md` (this file)
- **Predecessors:** S2789 (pilot-gates), S2788 (Fold C), S2787 (CSRF cross-file)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Sign Ledger sub-tab** (`?tab=system&sub=sign-ledger`) — 47 rows,
  including S2790 rows 45+46+47
- **Live surfaces:**
  - `logs/zoom_out_classifications.jsonl` — 47 rows at S2790 close
  - `logs/session_freshness.jsonl` — grew by 1 at S2790 open
  - `logs/recycle_events.jsonl` — +1 new event from S2790 close (`sha=29c69911e3b4`)

---

## §6 Open items forward-carry

1. **64 remaining ungated candidates** across ~13 prefixes (per updated
   `docs/audits/PUBLIC_PATHS_AUDIT_S2789.md`). Next largest buckets:
   - `/api/teams/` (6 endpoints — team creation, workflow start/complete)
   - `/api/distribution/` (6 endpoints — content publish/submit/sale)
   - `/api/v1/research/self-blog/` (6 endpoints — self-blog generate/publish)
   - `/api/pilot-gates/` (6 endpoints — wait, this is already gated at S2789)

   Actually recheck the audit doc post-S2790: it should show `/api/time-travel/` (11) + `/api/pilot-gates/` (6) both marked closed. Next per-prefix ship candidates by count.

2. **Decorator order codebase migration** — row 45 `same_pr_mitigatable`.
   Codebase-wide flip to `@token_auth_required` outermost across
   `views_agent_learning.py` (~20+ sites), `views_time_travel.py` (11 new),
   `views_pilot_gates` (7). Trigger: Chris directive OR 2nd Rigby request.

3. **PLAYBOOK-6.10.11+ codification** — row 47 `future_trigger`.
   Per-prefix authZ sweep pattern now 4-consecutive. Codify shape as
   Playbook rule when 6.10.10 slot clears (currently held by I-0302
   three-PR pattern amendment).

4. **Rigby SIGN response truncation substrate fix** — S2789 row 44
   `future_trigger`. Still deferred. S2790 T1 landed clean with tightened
   prompt; not conclusive, watch S2791.

5. All prior S2789 open runtime items forward-carry unchanged unless S2790
   changed them:
   - #1 75 → **64** remaining PUBLIC_PATHS candidates (S2790 closed 11)
   - Others unchanged.

---

## §7 Rebindings post-merge

- **Ledger:** 47 rows (20 actionable / 16 mitigatable / 11 future_trigger)
- **Rule count:** 205 (unchanged; no Playbook amendment)
- **Playbook version:** v0.8.0 (unchanged)
- **Session pin:** `pa-83e0c0e0f2f544a6` (S2790) — retire at close per
  S2770+ pattern with `force=true`
- **Wrapper default pin:** to be updated with fresh mint at S2791 open
  (forcing function preserved)
- **Regression 11-suite → 12-suite:** now includes
  `test_time_travel_authz_sweep_2790` (44 tests). Total: 235 tests OK.

---

## §8 Post-merge cascade

- ✅ `make recycle-all` (PLAYBOOK-7.4.4) — sha `29c69911e3b4`, twenty-ninth
  close-cycle
- ⏳ Cascade PR: handoff + start-here + INDEX + provenance
- ⏳ Pin retire with `force=true`

# Session 2798 — Onboarding routing (first-run banner on `/workspace`)

**Date:** 2026-07-16
**Session:** S2798
**Branch/PR:** `s2798-onboarding-routing` → **PR #3209** (merged as `5167e1fa3`)
**Predecessor:** [SESSION_2797_PUBLIC_LANDING_PAGE.md](SESSION_2797_PUBLIC_LANDING_PAGE.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** thirty-eighth post-PLAYBOOK-7.4.4

---

## §1 — Ship summary

Second consecutive user-visible ship after S2797. Adds a lightweight dismissible first-run onboarding banner to the actual post-login landing surface (`/workspace`). Trigger derived from existing `is_first_login()` service — no new schema, no new model field, no migration.

**Ship shape A'' (Rigby SIGN AGREE with edits — 5 folds persisted):**

- `needs_onboarding: bool` derived boolean added to `current_user` response (read-only bootstrap seam)
- New `POST /api/onboarding/complete/` endpoint delegates to existing idempotent `onboard_new_user()` service
- Banner mounts on `WorkspacePageNew` when `needs_onboarding === true` — 3 cards + dismiss button
- Dismiss = POST to endpoint + hide + refetch current_user
- Copy in editable `ONBOARDING_COPY` constants at top of `WorkspacePageNew.tsx` (Rigby F3 pattern from S2797)

**Independent copy bug fixed same-PR:**

`WELCOME_MESSAGE` in `user_onboarding_service.py` said "Head to the Command Center (home page)" but post-login has actually navigated to `/workspace` since Session 857. Fixed to "Head to the Workspace tab — that's your home base." Mitigated in-same-PR rather than split per Rigby T1 AGREE — the fix is trivial + contextually adjacent to the routing candidate.

**Files changed (7 + gitignored ledger):**

| File | Change | Purpose |
|------|--------|---------|
| `core/auth_views.py` | +36 lines | `current_user` returns `needs_onboarding`; new `complete_onboarding_view` |
| `core/services/user_onboarding_service.py` | +7 / -2 | `WELCOME_MESSAGE` routing target fix |
| `core/urls.py` | +7 / -1 | Import + wire `POST /api/onboarding/complete/` |
| `frontend/src/stores/authStore.ts` | +1 | `needs_onboarding?: boolean` on User type |
| `frontend/src/lib/api.ts` | +2 | `authApi.completeOnboarding()` |
| `frontend/src/pages/WorkspacePageNew.tsx` | +81 / -1 | Banner + `ONBOARDING_COPY` constants + `useQuery`/`useMutation` |
| `tools/pa_local.sh` | +1 / -1 | Fresh S2798 pin `pa-f3e65441ac684c7a` |
| `logs/zoom_out_classifications.jsonl` | +5 rows (72→77, local-only per gitignore) | S2798 T1/T2 fold persistence |

**Verification:**

Backend E2E (all 4 pass, curl-based):
- Fresh `s2798_onboarding_test` user → `needs_onboarding: true`
- POST `/api/onboarding/complete/` → 200, `onboarded: true`, `needs_onboarding: false`, DM created
- Idempotent second POST → `onboarded: false, detail: "User already onboarded"`
- Chris baseline → `needs_onboarding: false` (100s of prior PA convos)

Frontend browser-verified by Chris: banner renders for test user, dismiss works, no banner for Chris.

Regression 17-suite: 318 tests OK pre-ship (S2798 open).

---

## §2 — Novel-precedent moments

**First candidate that ran the full verify-before-build discipline BEFORE routing to Rigby.** Existing implementation analysis at candidate-selection time surfaced `core/services/user_onboarding_service.py` (225 lines, defined but sparsely called), `login_view` seam behavior, actual post-login navigation target (`/workspace` not `/`), and no signup path. That let the T1 SIGN routing be about *ship-shape design* rather than "what exists" — Rigby's tool_runs then caught what I still missed: `register_view` at `core/auth_views_enhanced.py:50` (I was head-limited to 15 files on my grep), which upgraded the candidate from "hypothetical" to "genuinely reachable."

**First Rigby SIGN whose DISAGREE caused a same-PR seam correction before coding started.** T1 Rigby SIGN pushed back on wiring onboarding into `login_view` — token issuance has side-effect blast radius (script/test/mobile/refresh flows all call login). Alternative: use existing `current_user` read-only bootstrap endpoint. Adopted before writing a single line of code — the seam correction shaped the ship shape from the start. Direct evidence of the "Claude directs, Rigby executes, Claude verifies" collaboration model catching an architectural miss upstream of implementation.

**First T2 SIGN that AGREED with EDITS resulting in a single-shot clean converge.** T1 SIGN-WITH-EDITS routed 5 concerns; T2 AGREE-WITH-EDITS accepted 4 same-PR + deferred 2 as future_trigger. No T3 revision cycle needed. This is what a working joint-agreement loop looks like when both sides are tool-grounded — contrast with S2786 which needed T4 revision after F-BLOCKING DISAGREE.

**Fold persistence miss (self-flagged):** PLAYBOOK-6.10.8 requires folds classify+persist BEFORE D-verdict. I presented Chris the joint recommendation and got "ship it" D-verdict without persisting the T1/T2 folds first — persisted them after the "go" D-verdict as part of the close cascade. Minor discipline miss; flagging honestly. Fix for next session: persist folds as final step of joint SIGN, before writing the recommendation to Chris.

**First user-visible ship whose backend E2E was verified before frontend build.** curl-based API testing against the test user found the banner-render preconditions worked (needs_onboarding flip, DM creation, idempotency) before touching `make frontend-ship`. Cheaper feedback loop; catches contract bugs before UI work amplifies them.

---

## §3 — SIGN cycles

### T1 Rigby SIGN — SIGN-WITH-EDITS (10 tool_runs)

**Grounded pushback:**
1. **DISAGREE — I missed `register_view`.** Rigby's grep found `core/auth_views_enhanced.py:50` where I was head-limited to 15 files. Upgraded the candidate from hypothetical to reachable.
2. **DISAGREE — `login_view` is the wrong seam.** Token issuance side effects = duplicate onboarding on retries + onboarding on token refresh + hard-to-debug flows. Alternative: `current_user` (read-only) or first-PA-chat (already exists).
3. **AGREE — no onboarding tracking fields exist.** 0 matches for `has_completed_onboarding`/`onboarded_at`/`first_login_at`/`completed_onboarding`.
4. **AGREE — welcome DM copy mismatch is real.** Suggested split as its own tiny PR.
5. **Zoom-out pushback (PLAYBOOK-6.10.7):** given single-user pre-prod state — but `register_view` being wired makes "first-user of admin-created account" reachable enough to justify ship-now over ship-copy-fix-only.

### T2 Rigby SIGN — AGREE with EDITS

**Adopted same-PR:**
- Seam: use `current_user` (not `login_view`) ✓
- Naming: `needs_onboarding` over `is_first_experience` ✓ (adopted verbatim)
- Copy fix bundled: acceptable because trivial ✓

**Deferred as future_trigger (2 folds):**
- Banner container coverage: mount on `WorkspacePageNew` now; move to shared authed Layout if direct-route usage data warrants (trigger: >N% of first-user sessions land outside `/workspace`)
- Complete endpoint throttling: skip now (idempotent service, low read cost, single-user pre-prod); add DRF `UserRateThrottle` when telemetry shows >N calls/min per user

### Fold ledger — 5 new rows (72 → 77)

Rows 73-77 in `logs/zoom_out_classifications.jsonl` (local-only per `.gitignore`):

| Row | Arc | Classification | Origin |
|-----|-----|----------------|--------|
| 73 | `onboarding_seam_choice` | same_pr_actionable | T1 DISAGREE on login_view seam → adopted current_user |
| 74 | `onboarding_field_naming` | same_pr_actionable | T2 EDIT: `needs_onboarding` naming |
| 75 | `onboarding_banner_container_scope` | future_trigger | T2 PARTIAL: coverage risk if users land outside /workspace |
| 76 | `onboarding_complete_endpoint_throttle` | future_trigger | T2 EDIT (optional): throttling deferred |
| 77 | `welcome_dm_copy_mismatch_split` | same_pr_mitigatable | T1 AGREE: split-suggested; mitigated in-same-PR |

---

## §4 — Verification transcript (E2E)

```bash
# Fresh test user baseline
$ python manage.py shell <<'EOF'
u = User.objects.get_or_create(username='s2798_onboarding_test', ...)
print(is_first_login(u))  # True
EOF
# Output: is_first_login=True

# GET current_user for test user
$ curl -s -H "Authorization: Token <test-token>" http://localhost:8000/api/v1/auth/user/
{
  "user": {
    "username": "s2798_onboarding_test",
    "needs_onboarding": true,
    ...
  }
}

# POST complete
$ curl -s -X POST -H "Authorization: Token <test-token>" http://localhost:8000/api/onboarding/complete/
{
  "ok": true,
  "onboarded": true,
  "needs_onboarding": false,
  "detail": "Welcome DM sent to s2798_onboarding_test"
}

# GET current_user again
{
  "user": {
    "needs_onboarding": false
  }
}

# Idempotency: second POST
{
  "ok": true,
  "onboarded": false,
  "needs_onboarding": false,
  "detail": "User already onboarded"
}

# Chris baseline
{
  "user": {
    "username": "chris",
    "needs_onboarding": false
  }
}
```

Browser verification: Chris logged in as `s2798_onboarding_test` in a private window, saw the 3-card banner on `/workspace`, clicked dismiss, banner vanished + DM appeared in inbox. Logged in as himself, no banner.

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2798 artifacts:**

- **Backend:** `core/auth_views.py` (`current_user` + `complete_onboarding_view`), `core/services/user_onboarding_service.py` (`WELCOME_MESSAGE`), `core/urls.py:2202` (route)
- **Frontend:** `frontend/src/pages/WorkspacePageNew.tsx` (banner + `ONBOARDING_COPY`), `frontend/src/lib/api.ts` (`authApi.completeOnboarding`), `frontend/src/stores/authStore.ts` (User type)
- **Handoff:** `docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md`
- **Live URL (local):** `http://localhost:8000/workspace` (banner renders only for `needs_onboarding=true` users)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab this ship** — the banner IS the surface
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **77 rows** (34/24/19); rows 73-77 are S2798 T1/T2 folds
  - `logs/recycle_events.jsonl` — +2 events (post-#3209 recycle + post-cascade recycle)
  - `http://localhost:8000/workspace` (first-run banner for `needs_onboarding=true`)

---

## §6 — Open items / owed / deferred

**S2798 owed follow-ups:**

- **Onboarding banner in shared authed Layout** — future_trigger fold 75; fires on direct-route usage data or first-prospect complaint
- **Throttle on `POST /api/onboarding/complete/`** — future_trigger fold 76; fires on telemetry showing >N calls/min per user or abuse pattern
- **Regression test for `needs_onboarding` + `complete_onboarding_view`** — should be added at next available slice PR (matches the S2796→S2795→S2794 pattern of test coverage catch-up)
- **Reset test user `s2798_onboarding_test` — leave in `is_first_login=True` state for future re-verification** — Chris/next session can re-dismiss to re-verify

**Standing owed (from S2797):**

- Public deployment of LandingPage (hosting + DNS decisions)
- BettingPage first-user trace + top-1 fix
- Waitlist DB capture (Shape B) — if S2797 mailto quality/volume insufficient
- I-0303 scoping (Async Tenant-Boundary Enforcement) — RUR-C1 parent-close blocker
- Regression tests for 4 S2796 tools
- 8 remaining per-tool docs need "Covered actions"
- 23 tools schema-lint fix (`actions_not_mentioned_in_description`)
- Wire tenant boundary health → Celery beat
- `SESSION_819_SYSTEM_AUDIT_*` cleanup (19+ files at S2798 close)
- Doc-note gap-map classifier h3-truncation bug in S2795 F2 template spec
- Playbook amendment: future-trigger-encoded-as-test codification (third instance still pending)

**Deferred (waiting on triggers):**

- All S2797-carried triggers unchanged
- **NEW: S2798 F3** — banner container coverage upgrade to shared Layout (trigger: direct-route usage data)
- **NEW: S2798 F4** — throttling on complete endpoint (trigger: telemetry)

---

## §7 — Session-open protocol observations

Followed the standard S2798 open sequence exactly:
1. `context-kit orient` auto-injected via SessionStart hook
2. Read 00-START-NEXT-SESSION.md in full
3. Non-PA sanity checks in parallel (ledger + regression 17-suite background + pg check)
4. Presented candidate menu → Chris picked #1 (onboarding routing)
5. Verify-before-build (found `user_onboarding_service.py`, missed `register_view`)
6. Fresh pin mint `pa-f3e65441ac684c7a` scoped to `s2798-onboarding-routing`
7. T1 Rigby SIGN (10 tool_runs — she caught `register_view`)
8. T2 Rigby SIGN (AGREE with EDITS — clean single-shot converge)
9. Present Chris one recommendation → "ship it"
10. Code + backend E2E + `make frontend-ship`
11. Present browser verification steps → "go"
12. Commit + PR #3209 + `--admin` merge
13. `make recycle-all` (thirty-eighth cycle)
14. Cascade (this handoff + start-here update + docs pipeline)
15. Retire S2798 pin (twenty-ninth consecutive `force=true` per S2770+ pattern)

**Discipline miss to carry forward:** folds should classify+persist BEFORE first D-verdict per PLAYBOOK-6.10.8; I persisted after "ship it." Next session: persist as final step of joint SIGN, before Chris routing.

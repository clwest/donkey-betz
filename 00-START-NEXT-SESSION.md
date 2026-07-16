# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2798 CLOSED — first-run onboarding banner on `/workspace` (second user-visible ship in a row)

**Refreshed 2026-07-16 (SESSION 2798 CLOSED — engineering-first session #12 in row, second user-visible / market-shipping ship in a row after S2797 landing page. Ship: first-run onboarding banner on `/workspace` — the actual post-login landing surface. Trigger derived from existing `is_first_login()` service (no prior PA convos + no prior onboarding DM); dismiss delegates to existing idempotent `onboard_new_user()`. Same PR fixes independent WELCOME_MESSAGE routing mismatch bug (predates S877): copy said "Head to Command Center" while LoginPage actually navigates to /workspace since Session 857. NOVEL — first candidate that ran full verify-before-build discipline BEFORE routing to Rigby; existing `user_onboarding_service.py` (225 lines, sparsely called) surfaced upfront let T1 SIGN be about ship-shape design not "what exists"; Rigby's tool_runs caught what I still missed — `register_view` at `core/auth_views_enhanced.py:50` (I was head-limited on grep). T1 DISAGREE on `login_view` seam drove same-PR correction to `current_user` bootstrap seam BEFORE any code was written — direct evidence of "Claude directs, Rigby executes, Claude verifies" catching architectural misses upstream of implementation. T2 AGREE single-shot converge with 5 folds persisted (4 same-PR + 1 mitigated + 2 future_trigger). Discipline miss self-flagged: folds classify+persist AFTER first D-verdict rather than before per PLAYBOOK-6.10.8 — carry forward. Rigby T1 SIGN 10 tool_runs. THIRTY-EIGHTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2798 ship:**

**PR #3209 · `5167e1fa3`** — 7 files, +133 / -7. `core/auth_views.py` (`current_user` + new `complete_onboarding_view`) + `core/services/user_onboarding_service.py` (WELCOME_MESSAGE copy fix) + `core/urls.py` (POST /api/onboarding/complete/) + `frontend/src/pages/WorkspacePageNew.tsx` (banner + editable ONBOARDING_COPY constants at top-of-file) + `frontend/src/lib/api.ts` (`authApi.completeOnboarding`) + `frontend/src/stores/authStore.ts` (`needs_onboarding?: boolean` on User type) + fresh session pin.

**Handoff:** `docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-eighth cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **77 rows** (34 same_pr_actionable / 24 same_pr_mitigatable / 19 future_trigger); rows 73-77 are S2798 T1/T2 folds.

**Live URL:** `http://localhost:8000/workspace` — banner renders only for `needs_onboarding=true` users (fresh accounts, no prior PA convos).

---

## SESSION-OPEN INFRA STORY (S2798)

Engineering-first session #12 in row. **Second user-visible market-shipping ship in a row** — S2797 landed the public LandingPage (prospects), S2798 lands the first-run banner (fresh users' first authenticated view).

**Verify-before-build ran end-to-end for the first time.** At candidate-selection time I read `user_onboarding_service.py` (225 lines) — found `is_first_login()`, `onboard_new_user()`, `onboard_to_workspace()`. Found the sole caller (`views_personal_assistant.py:881` — trigger on first PA chat). Found the routing mismatch (`WELCOME_MESSAGE` said Command Center; `LoginPage.tsx:24` goes to `/workspace`). That let T1 SIGN routing be about *design decisions*, not "what exists" — meta-alignment with `feedback_cycle_1a_verify_before_build`.

**Rigby STILL caught more than I did.** My repo grep for `def register` was head-limited to 15 files. Rigby's tool_run got 40 files back, including `core/auth_views_enhanced.py:50 def register_view(request):`. I verified via urls.py:2203 — registration IS wired at `POST /api/v1/auth/register/`. Upgraded the candidate from "hypothetical (Chris = single user)" to "genuinely reachable (register flow exists)." Direct payoff of the "verify Rigby tool_runs before trusting SIGN" rule extended backward: Rigby's tool_runs also *catch* what Claude misses.

**Same-PR seam correction BEFORE coding started.** T1 Rigby SIGN DISAGREE'd on wiring onboarding into `login_view` — token issuance side effects on scripts/tests/mobile/refresh. Alternative: `current_user` read-only bootstrap endpoint. Adopted before writing a line of code. This is the design shape at its cleanest — the collaboration model corrects course *upstream* of implementation, so the diff never has to be re-worked.

**T2 single-shot AGREE converge.** T2 Rigby SIGN AGREE-WITH-EDITS accepted 4 same-PR corrections + deferred 2 as future_trigger. No T3 revision cycle. Contrast with S2786 which needed T4 revision after F-BLOCKING DISAGREE. Both loops work; single-shot is faster when the T1 pushback maps cleanly to a resolvable alternative.

**Discipline miss self-flagged.** PLAYBOOK-6.10.8 requires folds classify+persist BEFORE first D-verdict. I presented Chris one recommendation, got "ship it" D-verdict, then persisted folds during close cascade — after D-verdict, not before. Carry-forward correction: at next joint SIGN, persist folds as the last step before writing the Chris-facing recommendation.

---

## S2799 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2798 close); freshness should be FRESH · SHA-match at S2798 close SHA (`5167e1fa3` or cascade PR merge SHA).
**Ledger baseline:** 77 rows expected (34/24/19). Any drift = investigate.
**Regression 17-suite:** 318 tests OK at S2798 open.

### Net-new engineering (⭐ user-visible / market-shipping leans first per `project_market_shipping_priority`)

**⭐ Onboarding follow-ups (from S2798):**
- **Regression test for `complete_onboarding_view` + `needs_onboarding` flag** — inline with S2794-S2797 test-catchup arc; ~30 lines APITestCase. ~1 slice.
- **Second banner container** — move onboarding banner to shared authed Layout (see fold row 75) IF Chris signals direct-route users are missing it. Trigger-based, not calendar-based.
- **First-user quick-tour post-dismiss** — the DM currently says "there's a Getting Started guide" — build the actual guide (link to deliverable?) or a `/getting-started` tour route. Multi-session arc.

**⭐ Continuing S2797 owed:**
- **BettingPage first-user trace** — 9-tab, 3023-line surface; unknown state for a first user (now especially relevant since S2798 banner directs first users to "open a workspace tab" — BettingPage adjacent). ~1 session.
- **Public deployment** — LandingPage is local-only. Hosting + DNS decisions.
- **Waitlist DB capture (Shape B)** — if S2797 mailto quality/volume insufficient.

**User-visible / UX leans:**
- **Copy iteration on LandingPage or ONBOARDING_COPY constants** — Chris edits + rebuilds via `make frontend-ship`. No PR needed.
- **AdvisorsPage / NeuralOrchestraPage / MythologyLabPage state** — audit what's live vs half-connected in the "differentiated IP" surfaces.

**Substrate leans (with explicit user-visible payoff):**
- **Next `td_handlers_ops` sub-slice** — 9 untested tools remain. Options unchanged from S2798.
- **Regression tests for the 4 S2796 tools** — deferred per "validation quickest"
- **Add "Covered actions" flat-list sections to 8 existing `validated_doc_exists_unknown` docs** — cheap gap-map upgrade
- **Fix 23 tools flagged `actions_not_mentioned_in_description`** — zero-code, description-only PR
- **Open I-0303 (Async Tenant-Boundary Enforcement)** — RUR-C1 parent-close direct blocker. Multi-session arc.
- **Wire tenant boundary health umbrella → Celery beat** — S2794 follow-up (~1 PR)
- **Playbook amendment PR — future-trigger-encoded-as-test codification** — third instance still pending
- **Doc-note the gap-map classifier h3-truncation bug** — annotate the S2795 F2 6-section template spec
- **`SESSION_819_SYSTEM_AUDIT_*` cleanup (19+ files at S2798 close)** — housekeeping PR

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke).

**Still owed:** P0.5 cost-threshold, P0.75 CI billing.

### Deferred (waiting on triggers, not calendar)

- All S2797-carried triggers unchanged (root-domain discoverability F4, first prospect email, etc.)
- **NEW: S2798 F3** — banner container coverage upgrade to shared Layout (trigger: direct-route usage data OR first-prospect complaint about missing banner)
- **NEW: S2798 F4** — throttling on `POST /api/onboarding/complete/` (trigger: telemetry showing >N calls/min per user OR abuse pattern)
- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **N22 v3 timestamp-based windows** — trigger: session-int windows prove insufficient
- **Second non-Rigby consumer of `zoom_out_tool`** — still awaited
- **Second consumer of `pa_tools_gap_map` service** — trigger for factor-out abstraction test
- **First autonomous Rigby invocation of `tenant_boundary_health`** — S2794 dogfood was prompted
- **First autonomous Rigby invocation of `build_pa_tool_audit`** — S2795 + S2796 dogfoods were prompted
- **F4 (telemetry-backed complaints) future_trigger** — fires when `tool_call_error_rate` query surface exists
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **Third instance of future_trigger-encoded-as-test pattern** — still standing
- **`status_snapshot_tool` version-source parity trigger**
- **First real prospect email via S2797 mailto CTAs** — first data point on funnel quality

### Post-S2798 owed

- **Regression test for `complete_onboarding_view` + `needs_onboarding`**
- **First-user quick-tour follow-up** (DM currently promises a guide that doesn't exist as a linkable resource)
- **Public deployment of LandingPage** — hosting + DNS decisions
- **BettingPage first-user trace + top-1 fix**
- **Waitlist DB capture (Shape B)** — if mailto is insufficient
- **I-0303 scoping** — RUR-C1 parent-close direct blocker
- **Regression tests for 4 S2796 tools**
- **8 remaining per-tool docs need "Covered actions"**
- **23 tools schema-lint fix**
- **Wire tenant boundary health → Celery beat**
- **`diagnostics_tool` PR-2 placeholders**
- **`SESSION_819_SYSTEM_AUDIT_*` cleanup** (19+ files)
- **Doc-note gap-map classifier h3-truncation bug** in S2795 F2 template spec

---

## SESSION PIN — S2798 RETIRED (fresh mint required at S2799 open)

**Pin history (S2798):**

- `pa-f3e65441ac684c7a` (label `s2798-onboarding-routing`) minted S2798 open; **retired at S2798 close (`force=true`, twenty-ninth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-f3e65441ac684c7a` (retired)** — intended failure mode forces S2799 first-action fresh mint.

**S2799 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2798 handoff §2 (novel-precedent moments) + §3 (T1/T2 SIGN cycles) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2798 close SHA (or cascade PR SHA).
bash tools/pa_local.sh "S2799 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 77-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==77, r
print('OK — 77 rows, counts:', r['counts_by_classification'])
"

# Regression 17-suite (unchanged; S2798 was pure feature — no new regression suite entries required)
python manage.py test \
  core.tests.test_ops_auth_regression_2772 \
  core.tests.test_ops_query_param_allowlist_2773 \
  core.tests.test_pa_wrapper_ownership_2776 \
  core.tests.test_zoom_out_classifications_2777 \
  core.tests.test_zoom_out_tool_2780 \
  core.tests.test_governance_auth_regression_2780 \
  core.tests.test_platform_auth_regression_2784 \
  core.tests.test_decision_approve_auth_regression_2785 \
  core.tests.test_csrf_enforcement_2787 \
  core.tests.test_platform_authz_sweep_2788 \
  core.tests.test_pilot_gates_authz_sweep_2789 \
  core.tests.test_time_travel_authz_sweep_2790 \
  core.tests.test_zoom_out_aggregations_2791 \
  core.tests.test_zoom_out_tool_aggregations_2792 \
  core.tests.test_zoom_out_time_window_2793 \
  core.tests.test_tenant_boundary_health_2794 \
  core.tests.test_pa_tools_gap_map_2795 \
  --noinput

# Mint fresh pin scoped to selected S2799 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2799 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

**S2798 lesson to carry:** persist folds as the FINAL STEP of joint SIGN, BEFORE writing the Chris-facing recommendation. I got the joint SIGN right and persisted folds during close cascade — technically after Chris's "ship it" D-verdict. Small discipline miss; fix by making fold persistence the very last SIGN step before Chris routing.

**S2797 lesson still to carry:** BEFORE writing any user-facing copy, marketing, or narrative content, READ `docs/PLATFORM_WHAT_IT_IS.md`. Source #1 in `context-kit orient` for a reason.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2798 artifacts:**

- **Backend:** `core/auth_views.py:97` (`current_user` + `needs_onboarding`); `core/auth_views.py:143` (`complete_onboarding_view`); `core/urls.py:2202` (route); `core/services/user_onboarding_service.py:36` (`WELCOME_MESSAGE`)
- **Frontend:** `frontend/src/pages/WorkspacePageNew.tsx` (banner + `ONBOARDING_COPY` constants at top-of-file per Rigby F3); `frontend/src/lib/api.ts:99` (`completeOnboarding`); `frontend/src/stores/authStore.ts:9` (User type)
- **Handoff:** `docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md`
- **Live URL (local):** `http://localhost:8000/workspace` — banner for `needs_onboarding=true` users only
- **Predecessors:** S2797 (public LandingPage), S2796 (market-shipping directive)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab this ship** — the banner IS the surface
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **77 rows** (34/24/19); rows 73-77 are S2798 T1/T2 folds
  - `logs/recycle_events.jsonl` — +2 events (post-#3209 recycle + post-cascade recycle)
  - `http://localhost:8000/workspace` — first-run banner surface
  - `http://localhost:8000/welcome` — public LandingPage (unchanged since S2797)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2798 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-f3e65441ac684c7a` (retired at S2798 close, force=true, twenty-ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-f3e65441ac684c7a` (retired; forces fresh mint at S2799 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2798 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 events during S2798 close |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **77 rows** (34 actionable / 24 mitigatable / 19 future_trigger) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — unchanged (no PA tool changes this ship) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` — unchanged (last regen at S2796 close) |
| **First-run banner surface** | **`http://localhost:8000/workspace` — LIVE (local, banner for needs_onboarding=true users)** |
| **Public marketing surface** | **`http://localhost:8000/welcome` — LIVE (local)** |
| Test user for onboarding demo | `s2798_onboarding_test` / `test-onboard-s2798!` — state re-armed at S2798 close for future re-verification |
| Next move | Chris selects at S2799 open (fresh tomorrow) |

---

## Recommended session-open protocol (S2799)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2798 handoff §2 (novel-precedent moments) + §3 (T1/T2 SIGN cycles) + §6 (open items)
4. **Freshness + regression 17-suite + ledger verify** — see S2799 open sequence above
5. **Watch for** ledger 77-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — user-visible / UX leans FIRST per `project_market_shipping_priority`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2799 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.8 constitutional at v0.8.0 (S2798 discipline carry):** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation — not during close cascade after D-verdict
15. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2799:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) — **anchor for anything user-facing** (S2797/S2798 lesson)
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
4. [`docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md`](docs/handoffs/SESSION_2798_ONBOARDING_ROUTING.md) — **S2798 handoff (current)**
5. [`docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md`](docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md) — S2797 predecessor
6. [`core/services/user_onboarding_service.py`](core/services/user_onboarding_service.py) — onboarding predicates + welcome DM
7. [`frontend/src/pages/WorkspacePageNew.tsx`](frontend/src/pages/WorkspacePageNew.tsx) — first-run banner + `ONBOARDING_COPY` at top
8. [`frontend/src/pages/LandingPage.tsx`](frontend/src/pages/LandingPage.tsx) — public landing page (unchanged)
9. [`docs/audits/PA_TOOLS_GAP_MAP_S2796.md`](docs/audits/PA_TOOLS_GAP_MAP_S2796.md) — PA tools gap map
10. [`docs/PA_TOOL_AUDIT.md`](docs/PA_TOOL_AUDIT.md) — runtime PA tool audit
11. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 77 rows at S2798 close (rows 73-77 are S2798)

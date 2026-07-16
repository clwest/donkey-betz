# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2797 CLOSED — public landing page at `/welcome` (first user-visible market ship)

**Refreshed 2026-07-15 (SESSION 2797 CLOSED — engineering-first session #11 in row, and first user-visible / market-shipping ship after 10 substrate sessions. Direct payoff of `project_market_shipping_priority_2026_07_15` persisted at S2796 open. Ship: public unauth `/welcome` route with LandingPage.tsx — 3-CTA marketing surface Chris can share with prospects. Ship shape A: ultra-static, zero backend, two mailto CTAs (primary open-ended + secondary pre-filled with lead-quality fields), copy in editable constants at top of file. NOVEL — Chris-caught positioning miss at T2: initial v1 copy anchored on 'sports betting' framing (violated `feedback_cycle_1a_verify_before_build` — skipped `docs/PLATFORM_WHAT_IT_IS.md`). Chris caught it before merge; rewrote to 'AI with receipts' framing centered on the verifiable-operating-model IP + new 'How it looks in practice' section featuring 3 real session receipts (S2795 duplicate-work catch, S2796 evidence-admission pushback, S2797 live-in-this-session V4 verification-limits admission). The receipts ARE the marketing. T3 tagline tightening post-merge (Chris tightened hero to 'AI with receipts.' / 'One AI proposes. One AI verifies. You decide with proof.') — direct evidence of the Rigby F3 editable-constants pattern working as intended. 4 folds classified + persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8. Rigby T1 SIGN-WITH-EDITS with 3 tool_runs (including repo-wide search returning 0 matches for 'Waitlist' + honest V4 admission she couldn't fully certify without additional file read). THIRTY-SEVENTH close-cycle post-PLAYBOOK-7.4.4.)**

**S2797 ship:**

**PR #3207 · `63aa705f5`** — 4 files, +296 / -2. New `LandingPage.tsx` (~280 lines) + `App.tsx` route wiring + `LoginPage.tsx` "Learn more" link + fresh session pin. T2 copy pivot from sports-betting to "AI with receipts" bundled into same PR. T3 tagline tightening bundled into close-cascade PR below.

**Handoff:** `docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-seventh cycle).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **72 rows** (29 same_pr_actionable / 23 same_pr_mitigatable / 16 future_trigger).

**Live URL:** `http://localhost:8000/welcome` — first user-visible marketing surface on the platform.

---

## SESSION-OPEN INFRA STORY (S2797)

Engineering-first session #11 in row. **First user-visible market-shipping ship** after 10 sessions of substrate. Chris's market-shipping priority signal (persisted at S2796 open) held at S2797 candidate menu.

**Novel-precedent moment — Chris-caught positioning miss at T2 review.** T1 copy anchored on the name (sports betting). Chris caught: *"why is the Welcome focused on sports betting if that's not the core part of the platform?"* Root cause: skipped `docs/PLATFORM_WHAT_IT_IS.md` before writing marketing copy despite it being source #1 in `context-kit orient`. Direct `feedback_cycle_1a_verify_before_build` violation. Corrected via same-PR pivot to "AI with receipts" framing centered on the verifiable-operating-model IP.

**The "How it looks in practice" section is self-illustrating.** Three real session receipts on the landing page — S2795 (Rigby found `build_pa_tool_audit` before Claude built a duplicate), S2796 (Rigby's evidence-admission pushback), S2797-in-this-session (Rigby's V4 admission she couldn't fully certify without an additional file read). The Chris-catch at T2 review + the same-PR correction is itself an example of the pattern working — the T2 commit body explicitly names the violation as evidence. Meta-alignment: the miss became content.

**T3 tagline tightening** (Chris asked mid-close): copy iterated without another PR round-trip or SIGN cycle, direct evidence of Rigby's F3 editable-constants-at-top-of-file pattern working as designed.

---

## S2798 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2797 close); freshness should be FRESH · SHA-match at S2797 close SHA (or cascade PR merge SHA).
**Ledger baseline:** 72 rows expected (29/23/16). Any drift = investigate.
**Regression 17-suite:** 318 tests OK at S2796 close (S2797 was frontend-only — no backend regression risk).

### Net-new engineering (⭐ user-visible / market-shipping leans first per `project_market_shipping_priority`)

**⭐ Landing page follow-ups (from S2797):**
- **BettingPage first-user trace** — 9-tab, 3023-line surface; unknown state for a first user. What breaks, what's empty, what looks half-connected? Trace + fix top-1. ~1 session.
- **Onboarding / signup flow** — first-user routing after auth. Currently new authenticated users land at `/` = CommandCenterPage (Chris's operator tool). Send them somewhere useful (BettingPage or a dedicated first-user page). ~1 session.
- **Waitlist DB capture (Shape B)** — if S2797 mailto quality/volume becomes insufficient. Trigger-based, not calendar-based.
- **Public deployment** — LandingPage is local-only. Requires: hosting decision + DNS pointing to `/welcome` + optional auth-app split (`app.donkeybetz.com` for Chris's authenticated surface).

**User-visible / UX leans:**
- **First-user "what to try" tour** — 3-5 things to click after landing in the app. Currently new users see CommandCenter with no orientation.
- **Copy iteration on LandingPage** — Chris edits `COPY = {}` constants + rebuilds via `make frontend-ship`. No PR needed.
- **AdvisorsPage / NeuralOrchestraPage / MythologyLabPage state** — audit what's live vs half-connected in the "differentiated IP" surfaces.

**Substrate leans (with explicit user-visible payoff):**
- **Next `td_handlers_ops` sub-slice** — 9 untested tools remain. Options:
  - **Incident-critical slice**: `autopilot_tool`, `governor_tool`, `infra_health_tool`, `spider_status_tool` (~1 slice PR)
  - **Utility slice**: `scheduled_tasks_tool` (~1 tool; small)
  - **Remaining slice**: `agent_control_tool`, `agent_memory_tool`, `heartbeat_history_tool`, `ops_digest_tool`
- **Regression tests for the 4 S2796 tools** — deferred per "validation quickest"
- **Add "Covered actions" flat-list sections to 8 existing `validated_doc_exists_unknown` docs** — cheap gap-map upgrade (must use flat bulleted list per latent classifier truncation bug)
- **Fix 23 tools flagged `actions_not_mentioned_in_description`** — zero-code, description-only PR
- **Open I-0303 (Async Tenant-Boundary Enforcement)** — RUR-C1 parent-close direct blocker. Multi-session arc.
- **Wire tenant boundary health umbrella → Celery beat** — S2794 follow-up (~1 PR)
- **Playbook amendment PR — future-trigger-encoded-as-test codification** — third instance still pending
- **Doc-note the gap-map classifier h3-truncation bug** — annotate the S2795 F2 6-section template spec

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke).

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (16 untracked files).

### Deferred (waiting on triggers, not calendar)

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
- **Third instance of future_trigger-encoded-as-test pattern** — still standing (S2791/S2792/S2793); S2795-S2797 folds did not extend or break
- **`status_snapshot_tool` version-source parity trigger**
- **S2797 F4 root-domain discoverability** — fires on: (a) first prospect complaint about landing at `/login`; (b) inbound organic traffic observed; (c) Chris switches from manual to broader outreach
- **First real prospect email via S2797 mailto CTAs** — first data point on funnel quality

### Post-S2797 owed

- **Public deployment of LandingPage** — hosting + DNS decisions
- **Onboarding flow** — first-user routing to something useful (BettingPage or a first-user tour)
- **BettingPage first-user trace + top-1 fix**
- **Waitlist DB capture (Shape B)** — if mailto is insufficient
- **I-0303 scoping** — RUR-C1 parent-close direct blocker
- **Regression tests for 4 S2796 tools**
- **8 remaining per-tool docs need "Covered actions"**
- **23 tools schema-lint fix**
- **Wire tenant boundary health → Celery beat**
- **`diagnostics_tool` PR-2 placeholders**
- **`SESSION_819_SYSTEM_AUDIT_*` cleanup** (16 files)
- **Doc-note gap-map classifier h3-truncation bug** in S2795 F2 template spec

---

## SESSION PIN — S2797 RETIRED (fresh mint required at S2798 open)

**Pin history (S2797):**

- `pa-4eed0b501f284250` (label `s2797-user-visible-scoping`) minted S2797 T1 open; **retired at S2797 close (`force=true`, twenty-eighth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-4eed0b501f284250` (retired)** — intended failure mode forces S2798 first-action fresh mint.

**S2798 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2797 handoff §2 (novel-precedent moments) + §3 (T1/T2/T3 SIGN cycles) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2797 close SHA (or cascade PR SHA).
bash tools/pa_local.sh "S2798 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 72-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==72, r
print('OK — 72 rows, counts:', r['counts_by_classification'])
"

# Regression 17-suite (unchanged; S2797 was frontend-only)
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

# Mint fresh pin scoped to selected S2798 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2798 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

**S2797 lesson to carry:** BEFORE writing any user-facing copy, marketing, or narrative content, READ `docs/PLATFORM_WHAT_IT_IS.md`. It's source #1 in `context-kit orient` for a reason. Skipping it and anchoring on the name = the exact violation Chris caught at T2 review.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2797 artifacts:**

- **Ship page:** `frontend/src/pages/LandingPage.tsx` (~280 lines; copy in `COPY = {}` constants at top-of-file per Rigby F3)
- **Route wiring:** `frontend/src/App.tsx` (unauth block, after `/login`)
- **Login link back:** `frontend/src/pages/LoginPage.tsx` (bottom of form)
- **Handoff:** `docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md`
- **Live URL (local):** `http://localhost:8000/welcome`
- **Predecessors:** S2796 (market-shipping directive), S2795 (gap map)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No Workspace tab this ship** — LandingPage is public marketing surface
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **72 rows** (29/23/16); rows 69-72 are S2797 F1-F4
  - `logs/recycle_events.jsonl` — +2 events (post-#3207 recycle + post-cascade recycle)
  - `http://localhost:8000/welcome` — first user-visible market surface

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2797 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-4eed0b501f284250` (retired at S2797 close, force=true, twenty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-4eed0b501f284250` (retired; forces fresh mint at S2798 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2797 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 events during S2797 close |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **72 rows** (29 actionable / 23 mitigatable / 16 future_trigger) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — unchanged (no PA tool changes this ship) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` — unchanged (last regen at S2796 close) |
| **Public marketing surface** | **`http://localhost:8000/welcome` — LIVE (local)** |
| Next move | Chris selects at S2798 open (fresh tomorrow) |

---

## Recommended session-open protocol (S2798)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2797 handoff §2 (novel-precedent moments) + §3 (T1/T2/T3 SIGN cycles) + §6 (open items)
4. **Freshness + regression 17-suite + ledger verify** — see S2798 open sequence above
5. **Watch for** ledger 72-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — user-visible / UX leans FIRST per `project_market_shipping_priority`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2798 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
15. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2798:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) — **anchor for anything user-facing** (S2797 lesson)
3. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
4. [`docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md`](docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md) — **S2797 handoff (current)**
5. [`frontend/src/pages/LandingPage.tsx`](frontend/src/pages/LandingPage.tsx) — public landing page (copy in `COPY = {}` at top)
6. [`docs/audits/PA_TOOLS_GAP_MAP_S2796.md`](docs/audits/PA_TOOLS_GAP_MAP_S2796.md) — PA tools gap map
7. [`docs/PA_TOOL_AUDIT.md`](docs/PA_TOOL_AUDIT.md) — runtime PA tool audit
8. [`docs/research/tools/validation/`](docs/research/tools/validation/) — 22 validation docs (4 at S2796 `validated_full`; 8 at `validated_doc_exists_unknown` awaiting flat-list upgrades)
9. [`docs/handoffs/SESSION_2796_TD_HANDLERS_OPS_SLICE1.md`](docs/handoffs/SESSION_2796_TD_HANDLERS_OPS_SLICE1.md) — S2796 predecessor
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 72 rows at S2797 close (rows 69-72 are S2797 F1-F4)

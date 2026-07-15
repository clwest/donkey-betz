# Session 2794 — Tenant Boundary Health surface + cross-tenant regression umbrella

**Date:** 2026-07-15
**Session:** S2794
**Branch/PR:** `s2794-tenant-boundary-health` → **PR #3201** (merged as `b0fef5d3c`)
**Predecessor:** [SESSION_2793_ZOOM_OUT_TIME_WINDOW.md](SESSION_2793_ZOOM_OUT_TIME_WINDOW.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** thirty-third post-PLAYBOOK-7.4.4 (sha=`b0fef5d3c271`)

---

## §1 — Ship summary

First S2794 ship — genuine net-new engineering (not substrate iteration) aimed directly at Chris's ask "prepare the platform for real world users" while staying inside the RUR-C1 Tenant Boundary Lockdown parent arc.

Adds an operator-facing **Tenant Boundary Health** Workspace sub-tab that renders the RUR-C1 cross-tenant regression readiness surface, backed by:
- A new unified umbrella harness (`tests/security/test_cross_tenant_regression.py`) — the canonical name CAMPAIGN.md §5.2 has called for since 2026-07-10
- A shared runner service (`core/services/cross_tenant_regression_service.py`) — subprocess+JUnit XML for correctness under pytest-django DB fixture semantics
- A durable `TenantBoundaryHealthReport` model + migration + REST endpoint
- A management command (`python manage.py run_cross_tenant_regression`) callable by CLI, CI, or Celery

Advisory-not-gate posture repeated on three surfaces (F1 belt-and-braces): REST envelope, UI banner, model docstring.

**Files changed (12):**

| File | Change | Purpose |
|------|--------|---------|
| `core/models_tenant_boundary_health.py` | new | `TenantBoundaryHealthReport` model (env/git_sha/runner_identity/counts/failing_ids/coverage/summary_json + overall_status advisory property) |
| `core/migrations/0385_s2794_tenant_boundary_health_report.py` | new | Scoped migration (deliberately excludes unrelated pre-existing Narrative drift) |
| `core/services/cross_tenant_regression_service.py` | new | Runner service — CROSS_TENANT_TEST_PATHS + COVERAGE_METADATA + KNOWN_GAPS + subprocess+JUnit XML runner |
| `core/management/commands/run_cross_tenant_regression.py` | new | CLI wrap (`--persist` DB row; `--json` stdout; `--verbose-pytest` unmute) |
| `core/views_governance.py` | +101 | `tenant_boundary_health` view — staff-gated, advisory envelope, F1 no-toggle shape |
| `core/urls.py` | +3 | `/api/governance/tenant-boundary-health/` route |
| `core/models/__init__.py` | +3 | Re-export + `__all__` addition |
| `frontend/src/pages/workspace/tabs/TenantBoundaryHealthSection.tsx` | new | Sub-tab — F1 banner + policy line, F2 coverage matrix + gaps, F3 provenance strip |
| `frontend/src/pages/WorkspacePageNew.tsx` | +2 | Wire new sub-tab under System primary |
| `tests/security/test_cross_tenant_regression.py` | new | CAMPAIGN.md canonical umbrella — locks LABELS non-empty + on-disk + tests/security/ scope + coverage-metadata + gaps |
| `core/tests/test_tenant_boundary_health_2794.py` | new (283 lines) | 16 tests × 3 classes locking runner JUnit parse + advisory-status property + REST F1/F2/F3 |
| `tools/pa_local.sh` | +1 / -1 | Fresh pin refresh (`pa-1519703289af41fa`) |

**Full 16-suite regression:** 295 tests OK (279 prior + 16 new, 4.3s).

**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **59 rows** (24 `same_pr_actionable` / 20 `same_pr_mitigatable` / 15 `future_trigger`). Rows 57/58/59 are S2794's own SIGN folds.

---

## §2 — Novel-precedent moments

**First RUR-C1 substrate ship after both child arcs closed.** I-0301 closed S2742, I-0302 closed S2751, I-0303 still not opened. Between the two closed children and Chris's ask, this ship threaded the needle by building the shared cross-tenant regression umbrella + operator surface — the two RUR-C1 parent-close prerequisites that neither child arc individually shipped.

**First operator-facing readiness surface with F1 no-gate contract locked in tests.** The tab is code-shape read-only (no toggle controls exist), the endpoint envelope explicitly carries `is_gate: false`, and the contract test suite locks all three surfaces of the advisory framing. A future PR that adds a toggle button to this tab must also break at least one contract test.

**First subprocess+JUnit XML runner in the platform.** Prior test-composition uses `python manage.py test`; the umbrella runner shells out to `python -m pytest tests/security/ --junit-xml=…` and parses the XML because pytest-django's DB fixture wiring collides with a live Django process (250+ setup errors observed in the pytest.main-in-process approach). Subprocess isolation + JUnit XML parse is the reliable pattern; documented in service module docstring.

**First bundling of B and C-lite from Rigby SIGN into a single ship.** Rigby's SIGN-with-edits explicitly upgraded from B-or-C to "B fused with C-lite as its data source". Single-PR full stack per Chris D-verdict "Got with i."

**Continued Rigby SIGN response non-truncation.** S2790/S2791/S2792/S2793/S2794 all clean = sample size **5** post-Row 44 tightened-prompt pattern. Trend claim now carries weight.

---

## §3 — T1 SIGN cycle detail

**Pin:** `pa-1519703289af41fa` (label `s2794-rur-c1-new-surface-exploration`), minted at S2794 open via `session_lifecycle open`. Retired at close, force=true, twenty-fifth consecutive.

**Dispatch 1 — joint scoping (tool-grounded):**
Presented 4 candidates (A open I-0303 / B Workspace tab / C umbrella / D user accounts) with my B lean + explicit zoom-out ask. Rigby returned SIGN-with-edits **upgrading** the recommendation to "B fused with C-lite" — build the umbrella as the tab's data source in one PR, not two options.

**3 folds classified + persisted BEFORE D-verdict per PLAYBOOK-6.10.8/9:**

| # | Ledger row | Class | Fold title | Disposition |
|---|-----------|-------|-----------|-------------|
| F1 | 57 | `same_pr_mitigatable` | `tenant_boundary_health_advisory_not_gate` — read-only tile drifts into de-facto launch gate | ✅ Adopted — advisory banner + policy line + code-shape no-toggle |
| F2 | 58 | `same_pr_mitigatable` | `tenant_boundary_health_partial_coverage_honesty` — green suite ≠ platform safe if async uncovered | ✅ Adopted — coverage matrix + explicit Known gaps section |
| F3 | 59 | `same_pr_actionable` | `tenant_boundary_health_result_source_provenance` — ad-hoc results = non-reproducible signals | ✅ Adopted — env/SHA/runner/timestamp fields in model + REST + tab |

**Dispatch 2 — Chris D-verdict:** "yes go" for option 1 branch, then "Got with i." for option i single-PR full stack.

**Dispatch 3 — post-merge dogfood:** Rigby invoked `GET /api/governance/tenant-boundary-health/` via `http_smoke_test` PA tool. `tool_runs` non-empty. HTTP 200. F1/F2/F3 all verified live:
- `advisory` present + `is_gate: false` + `policy.launch_approval: "Manual (Chris)"` (F1)
- `coverage_metadata` = 15 entries; 3 `not_yet_covered` (async WS, signed URL, admin audit) (F2)
- `latest_report` present with env=`development` + git_sha=`b0fef5d3c271…` + runner=`donkeyking` + created_at + overall_status=`green` (F3)
- 324 tests, all green, from the first persisted row

---

## §4 — Constitutional posture

- **Playbook v0.8.0 (205 rules)** — unchanged
- **PLAYBOOK-6.10.7** zoom-out ask: ✅ 1 explicit ask drove all 3 folds
- **PLAYBOOK-6.10.8** fold classify+persist BEFORE D-verdict: ✅ rows 57/58/59 persisted before Chris "Got with i."
- **PLAYBOOK-6.10.9** evidence admission: ✅ stable-state pointer `3cc0b67a3` + file+line evidence for RUR-C1 arc state claims + verified outcome inline
- **PLAYBOOK-7.4.4** recycle-after-merge: ✅ `make recycle-all` completed post-merge (thirty-third cycle, sha=`b0fef5d3c271`)
- **RUR-C1 parent invariant**: ✅ this ship does NOT close RUR-C1 parent; I-0303 (async tenant boundary) still not opened; coverage matrix + known gaps surface the gap
- **`feedback_engineering_bias_over_audit`**: ✅ net-new engineering candidate (engineering-first session #8 in row)
- **`feedback_workspace_over_command_center_for_new_ui`**: ✅ shipped as Workspace System sub-tab, not Command Center
- **`feedback_verify_rigby_tool_runs_before_trusting_sign`**: ✅ tool_runs verified (Rigby http_smoke_test dispatch)
- **`feedback_claude_rigby_agree_first_chris_yes_no`**: ✅ Claude+Rigby joint recommendation to Chris; Chris yes/no on both branch selection and PR shape
- **`feedback_zoom_out_ask_per_rigby_sign`**: ✅ 1 explicit zoom-out ask; drove F1+F2+F3

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2794 artifacts:**

- **Ship model:** `core/models_tenant_boundary_health.py` + migration `0385`
- **Ship runner:** `core/services/cross_tenant_regression_service.py` (constants + subprocess+JUnit XML runner)
- **Ship CLI:** `python manage.py run_cross_tenant_regression` (`--persist` / `--json` / `--verbose-pytest`)
- **Ship REST:** `core/views_governance.py:tenant_boundary_health` + `/api/governance/tenant-boundary-health/`
- **Ship UI:** `frontend/src/pages/workspace/tabs/TenantBoundaryHealthSection.tsx` under System → Tenant Boundary sub-tab
- **Ship umbrella:** `tests/security/test_cross_tenant_regression.py` (CAMPAIGN.md canonical name, 4 contract locks)
- **Ship contract tests:** `core/tests/test_tenant_boundary_health_2794.py` (283 lines, 16 tests, 3 classes)
- **Handoff:** `docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md` (this file)
- **PR:** [#3201](https://github.com/clwest/donkey-betz-platform/pull/3201) merged as `b0fef5d3c`
- **Predecessors:** S2793 (zoom-out time window), S2792 (aggregations parity), S2751 (I-0302 close), S2742 (I-0301 close + RUR-C1 parent ratification)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Tenant Boundary sub-tab** (`?tab=system&sub=tenant-boundary`) — new (this PR)
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **59 rows** (24/20/15)
  - `logs/session_freshness.jsonl` — grew by 1 at S2794 open
  - `logs/recycle_events.jsonl` — +1 event (post-#3201, sha=`b0fef5d3c271`)
  - `core_tenantboundaryhealthreport` DB table — **1 row** (green, 324 tests, `id=57acaed0-d93e-4ea9-bbf3-99561c109775`)

---

## §6 — Open items / follow-ups

- **Periodic Celery task wiring the umbrella** — deliberately NOT in scope this PR; the runner exists + CLI works + endpoint reads latest. Beat schedule can add a periodic invocation later without touching this substrate. Trigger: Chris wants the tab to auto-refresh on a cadence, or CI GitHub Action needs a shared invocation contract.
- **I-0303 arc open (Async Tenant-Boundary Enforcement)** — the last RUR-C1 child arc. Only after this opens + closes can RUR-C1 parent close. Coverage matrix surfaces the gap; tab makes the ask visible.
- **CI GitHub Action wiring the umbrella** — future PR; the ship intentionally left CI wiring off-scope. `.github/workflows/` addition + persistence to a shared artifact location.
- **Beat schedule + Slack/Discord notification on red** — post-alpha; not urgent.
- **F3 future_trigger for autonomy creep at Playbook amendment gate** — if a sibling PR wires any status→flag auto-flip, F1 mitigation is broken; fires PLAYBOOK-6.10.10 slot candidate.
- **Encoding-future-triggers-as-tests pattern — third instance still standing** (S2791 F3 + S2792 F3 + S2793 F3). Playbook amendment candidate. This PR did NOT use the encoded-as-test pattern for its F3 (which was actionable, not deferred), so the streak neither extends nor breaks.
- **Second non-Rigby consumer of `zoom_out_tool`** — trigger for factor-out abstraction test (still awaited).
- **Model drift arc** — 38+ auto-migrations queued (grew by ~1 during S2794 — narrative model changes still un-migrated; scoped migration 0385 deliberately excluded them).
- **`SESSION_819_SYSTEM_AUDIT_*` cleanup** — 15 untracked files from webhook cron (grew from 13 during S2794).
- **Autonomous Rigby invocation of `tenant_boundary_health` endpoint** — S2794 dogfood was prompted at post-merge. First autonomous invocation is next trigger.
- **Rigby SIGN response truncation follow-up** — S2790/S2791/S2792/S2793/S2794 all clean; sample size 5.

---

## §7 — Repo state at close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `b0fef5d3c` (S2794 ship #3201) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Substrate advanced — shared regression umbrella + operator readiness surface shipped; parent CLOSE gated on I-0303 open + all-3-children pass |
| Session pin | `pa-1519703289af41fa` (retired at close, force=true, twenty-fifth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-1519703289af41fa` (retired; forces fresh mint at S2795 open) |
| Live infra state | S2755→S2793 substrate + S2794 tenant boundary health + first persisted health report row |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2794 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3201, sha=`b0fef5d3c271`) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **59 rows** (24/20/15) |
| TenantBoundaryHealthReport | **1 row** at close (green, 324/324, env=development, git=`b0fef5d3c271`) |

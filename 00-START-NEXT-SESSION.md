# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2794 CLOSED — Tenant Boundary Health surface + cross-tenant regression umbrella (RUR-C1 substrate)

**Refreshed 2026-07-15 (SESSION 2794 CLOSED — engineering-first session #8 in row per `feedback_engineering_bias_over_audit`. First genuine net-new user-facing surface in the S2788→S2793 substrate streak. Aimed at Chris's ask "prepare the platform for real world users" while staying inside RUR-C1 Tenant Boundary Lockdown parent arc. Shipped shared cross-tenant regression umbrella (`tests/security/test_cross_tenant_regression.py` — CAMPAIGN.md §5.2 canonical name), runner service + management command + Celery-ready CLI, `TenantBoundaryHealthReport` model + REST endpoint + migration, and operator-facing "Tenant Boundary" Workspace System sub-tab. Rigby T1 SIGN-with-edits upgraded my B-or-C proposal to "B fused with C-lite" — build umbrella as tab's data source in one PR. 3 folds classified + persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8: 57 `same_pr_mitigatable` (F1 read-only tile → de-facto gate — adopted via banner + policy line + code-shape no-toggle), 58 `same_pr_mitigatable` (F2 coverage honesty — adopted via matrix + gaps section), 59 `same_pr_actionable` (F3 result provenance — adopted via env/SHA/runner/timestamp fields). Full 16-suite regression: 295 tests OK (279 prior + 16 new). Post-merge dogfood: Rigby invoked `GET /api/governance/tenant-boundary-health/` via `http_smoke_test` — HTTP 200, F1/F2/F3 all verified live. First persisted health report row: 324/324 green in 269s. Rigby SIGN response non-truncated (sample size 5 — pattern now carries weight). THIRTY-THIRD close-cycle post-PLAYBOOK-7.4.4 codification.)**

**S2794 ship:**

**PR #3201 · `b0fef5d3c`** — 12 files, +1554 / -1. New `TenantBoundaryHealthReport` model (`0385` migration) + runner service + management command + REST endpoint + Workspace sub-tab + umbrella test + 283-line contract test file. CAMPAIGN.md canonical umbrella name shipped. First operator-facing readiness surface with F1 no-gate contract locked in tests + code shape.

**Handoff:** `docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md`
**Post-merge:** `make recycle-all` per PLAYBOOK-7.4.4 completed (thirty-third cycle, sha=`b0fef5d3c271`).
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **59 rows** (24 same_pr_actionable / 20 same_pr_mitigatable / 15 future_trigger).

---

## SESSION-OPEN INFRA STORY (S2794)

Engineering-first session #8 in row. Chris chose option 2 ("something entirely new") from the S2794 candidate menu with the frame "what would stay in the parent [RUR-C1] and help prep for real world users?". Verified RUR-C1 state before routing to Rigby: I-0301 CLOSED S2742, I-0302 CLOSED S2751, I-0303 NOT YET OPENED, `tests/security/test_cross_tenant_regression.py` (CAMPAIGN.md canonical umbrella) missing from disk, cross-tenant SLO not built.

Routed 4 candidates (A open I-0303 / B Workspace tab / C umbrella / D user accounts) with my B lean to Rigby with zoom-out ask. **Rigby SIGN-with-edits upgraded to "B fused with C-lite"** — build umbrella as tab's data source in ONE PR, not two options. Persisted 3 folds (57/58/59). Chris D-verdicted the branch ("let's do option 2") then the PR shape ("Got with i.").

Runner service design pivot: initial pytest.main-in-process approach hit 255 test-DB fixture setup errors (pytest-django + live Django process collision). Refactored to subprocess+JUnit XML parse — reliable pattern, ~5s startup overhead, matches CI invocation. Documented in service module docstring.

---

## THE PIVOTS — WHY THIS SHIP MATTERS

**First RUR-C1 substrate ship since I-0302 close (S2751).** Between closed children and Chris's ask, this ship threaded the needle — built the two parent-close prerequisites (shared regression umbrella + operator readiness surface) that neither child arc shipped.

**First operator-facing readiness surface with F1 no-gate contract locked at three layers.** REST envelope contract (`is_gate: false` + `policy.launch_approval: "Manual (Chris)"`) + UI code-shape (no toggle controls exist in TSX) + model docstring (advisory posture repeated). A future PR that adds a toggle button breaks at least one contract test.

**First subprocess+JUnit XML runner in the platform.** pytest.main-in-process collides with pytest-django DB fixtures inside a live Django process. Subprocess isolation + JUnit XML parse is the reliable pattern; documented for future runners.

**First single-PR full-stack ship threading Rigby SIGN B+C upgrade.** Rigby proposed folding B (tab) and C-lite (umbrella) — Chris D-verdicted the fusion via "Got with i.". Single-PR full stack: model + migration + service + command + REST + URL + tests + umbrella + frontend section + wire.

**Rigby SIGN response non-truncation streak sample size now 5.** S2790→S2794 all clean. Tightened-prompt pattern now carries weight as a claim.

**Zoom-out ask (PLAYBOOK-6.10.7) load-bearing for fourth consecutive session.** All 3 S2794 folds surfaced by the zoom-out ask, none by direct claim scan. Same pattern as S2791/S2792/S2793.

---

## S2795 CANDIDATES (Chris selects at open)

### First — freshness/regression sanity

**Post-cascade freshness check:** wrapper pin retired (S2794 close); freshness should be FRESH · SHA-match at S2794 close SHA `b0fef5d3c` (or cascade PR merge SHA).
**Ledger baseline:** 59 rows expected (24/20/15). Any drift = investigate.
**Regression 16-suite:** 295 tests OK at S2794 close.
**TenantBoundaryHealthReport table:** 1 row (green baseline) at close — additional rows persist across sessions as CLI `--persist` is invoked.

### Net-new engineering (⭐ recommended per `feedback_engineering_bias_over_audit`)

- **Open I-0303 (Async Tenant-Boundary Enforcement)** — the ONLY unopened RUR-C1 child arc. RUR-C1 parent closes only when I-0303 lands + all-3 pass umbrella. This is the direct RUR-C1 parent-close-unblock lever. Scoping doc first; may be a multi-session arc.
- **Wire the umbrella runner into a Celery beat schedule** — the runner + management command shipped; only the periodic invocation is missing. Small (~1 PR). Trigger the F3 provenance chain end-to-end without operator manual invocation.
- **Wire the umbrella runner into a CI GitHub Action** — same substrate, different trigger. Small.
- **Playbook amendment PR — codify future-trigger-encoded-as-test pattern** (third-instance trigger fired at S2793 F3; still standing). Candidate slot `PLAYBOOK-6.10.10`.
- **Continue Workspace-tab extension pattern** per `feedback_workspace_over_command_center_for_new_ui` — pick another underweight tab (Deliverables / Initiatives / Files / OpsConsole) and add a triage feature.
- **Next PUBLIC_PATHS prefix ship** (64 remaining across ~13 prefixes per S2789 audit doc).
- **Decorator order codebase migration** — row 45 `same_pr_mitigatable` (S2790).
- **N24 anti-rubber-stamp SIGN codification** — 5 F-BLOCKING-equivalent triggers.
- **AudioAgent completion-flip verification** — awaiting next timeout.
- **Model drift arc** — 38+ auto-migrations queued (grew by 1 during S2794).
- **Frontend raw-fetch consolidation** — 30 files with fetch(); deferrable.
- **Something entirely new** — fresh spider / agent capability / pipeline / dashboard.

**Still gated by S2774 ops-surface pause:** N9, N20, Candidate 1 (S2761 smoke), 30+ `core/urls.py` lambda-`__import__` sites.

**Still owed:** P0.5 cost-threshold, P0.75 CI billing, `SESSION_819_SYSTEM_AUDIT_*` cleanup (15 untracked files from webhook cron — grew from 13 during S2794).

### Deferred (waiting on triggers, not calendar)

- **N10** — partial-recycle UI badge (gated on real partial-recycle event)
- **First real N11 PARTIAL_RECYCLE tile fire** (watching)
- **Q3 #5** (health_summary / ops_tool.overview overlap)
- **N22 v3 timestamp-based windows** — trigger: session-int windows prove insufficient OR consumer joins ledger against wall-clock artifacts
- **Second non-Rigby consumer of `zoom_out_tool`** — still awaited
- **N17 smart-command-box creep** — row 21 `future_trigger`
- **First autonomous Rigby invocation of `tenant_boundary_health` endpoint** — S2794 dogfood was prompted at post-merge; first unprompted is next trigger
- **First graceful-degradation clause activation on PLAYBOOK-6.10.8** — pending
- **Third served-artifact-freshness trigger** — PLAYBOOK-7.4.4 amendment candidate
- **S2783 Fold 1 same-PR mitigation** — GovernanceTab subtitle
- **S2784 Fold 29 automation identity trigger** — pre-prod → non-staff automation deploy
- **`@public_endpoint` opt-in decorator ADR** — 263-entry PUBLIC_PATHS wrong-pattern candidate
- **Rigby SIGN response truncation follow-up** — sample size 5 across S2790→S2794; pattern claim now carries weight
- **S2791 Row 50 aggregation drift trigger** — fires if `test_aggregations_block_repeats_advisory_markers` needs to change
- **S2792 Row 53 aggregation scope mismatch trigger** — fires at ~200 ledger rows OR first user complaint
- **S2793 Row 56 aggregation scope divergence trigger** — fires at user complaint OR timestamp windows added
- **S2794 Row 57 autonomy creep trigger** — fires if a sibling PR wires any status→flag auto-flip on the tenant boundary health surface (F1 mitigation break signal)
- **Third instance of future_trigger-encoded-as-test pattern** — TRIGGER HIT at S2793 F3; still standing at S2794 close (S2794 F3 was actionable-not-deferred, so pattern streak neither extends nor breaks). Playbook amendment candidate.

### Post-S2794 owed

- **I-0303 scoping open** — RUR-C1 parent-close direct blocker
- **Celery beat wire for the umbrella runner** — periodic invocation of the shipped runner
- **CI GitHub Action wire for the umbrella runner** — CI-blessed reports for provenance
- **Playbook amendment PR — future-trigger-encoded-as-test codification** (candidate; competes with I-0302 for `PLAYBOOK-6.10.10` slot)
- **I-0302 three-PR pattern amendment** → PLAYBOOK-6.10.10 slot when opened (re-slotted forward again)
- **64 remaining PUBLIC_PATHS candidates** across ~13 prefixes
- **Decorator order codebase migration** (S2790 row 45)
- **PLAYBOOK-6.10.11+ per-prefix authZ sweep codification** (S2790 row 47)
- **N24 anti-rubber-stamp SIGN codification** — 5 triggers
- **AudioAgent completion-flip verification**
- **Ledger split drift audit** — now 24/20/15
- **`SESSION_819_SYSTEM_AUDIT_*` untracked file cleanup** (15 files)

---

## SESSION PIN — S2794 RETIRED (fresh mint required at S2795 open)

**Pin history (S2794):**

- `pa-1519703289af41fa` (label `s2794-rur-c1-new-surface-exploration`) minted S2794 open; **retired at S2794 close (`force=true`, twenty-fifth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-1519703289af41fa` (retired)** — intended failure mode forces S2795 first-action fresh mint.

**S2795 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2794 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)

# Freshness check. Should be FRESH · SHA-match at S2794 close SHA (b0fef5d3c or cascade PR SHA) — THIRTY-THIRD close-cycle after PLAYBOOK-7.4.4.
bash tools/pa_local.sh "S2795 open — freshness check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5"

# Ledger check: confirm 59-row baseline survived close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==59, r
print('OK — 59 rows, counts:', r['counts_by_classification'])
"

# Regression 16-suite (S2793 15-suite + S2794 tenant boundary health)
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
  --noinput

# Optional — verify the umbrella runner is still working (subprocess+JUnit)
DJANGO_LOG_LEVEL=WARNING python manage.py run_cross_tenant_regression --json 2>/dev/null | python -c "
import json, sys
r = json.loads(sys.stdin.read())
assert r['overall_status'] in {'green','red','unknown'}
print('umbrella:', r['overall_status'], '·', r['total_tests'], 'tests ·', r['elapsed_secs'], 's')
"

# Mint fresh pin scoped to selected S2795 candidate.
python manage.py session_lifecycle open --label <candidate-scoped-label>
python manage.py session_lifecycle history --limit 5

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2795 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — every joint SIGN routing MUST include ≥1 zoom-out ask; folds MUST be classified + persisted BEFORE D-verdict; folds asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2794 artifacts:**

- **Ship model:** `core/models_tenant_boundary_health.py` + migration `0385`
- **Ship runner:** `core/services/cross_tenant_regression_service.py`
- **Ship CLI:** `python manage.py run_cross_tenant_regression`
- **Ship REST:** `core/views_governance.py:tenant_boundary_health` + `/api/governance/tenant-boundary-health/`
- **Ship UI:** `frontend/src/pages/workspace/tabs/TenantBoundaryHealthSection.tsx` (System → Tenant Boundary sub-tab)
- **Ship umbrella:** `tests/security/test_cross_tenant_regression.py` (CAMPAIGN.md canonical name)
- **Ship contract tests:** `core/tests/test_tenant_boundary_health_2794.py`
- **Handoff:** `docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md`
- **Predecessors:** S2793 (zoom-out time window), S2792 (aggregations parity), S2751 (I-0302 close), S2742 (I-0301 close + RUR-C1 parent ratification)

🖥️ **Workspace UI — `/workspaces` surface:**

- **System / Tenant Boundary sub-tab** (`?tab=system&sub=tenant-boundary`) — NEW at this session
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **59 rows** (24/20/15)
  - `logs/session_freshness.jsonl` — grew by 1 at S2794 open
  - `logs/recycle_events.jsonl` — +1 event from S2794 close (`sha=b0fef5d3c271`)
  - `core_tenantboundaryhealthreport` — **1 row** at close (green baseline)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `b0fef5d3c` (S2794 ship) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Substrate advanced — shared regression umbrella + operator readiness surface shipped; parent CLOSE gated on I-0303 open + all-3 pass. |
| RUR-C1 child arcs | I-0301 CLOSED (S2742) · I-0302 CLOSED (S2751) · **I-0303 NOT YET OPENED** |
| Session pin | `pa-1519703289af41fa` (retired at S2794 close, force=true, twenty-fifth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-1519703289af41fa` (retired; forces fresh mint at S2795 open) |
| Live infra state | S2755→S2793 substrate + S2794 tenant boundary health + first health report row |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Postgres pg16 | Parked (April fossil) |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2794 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3201, sha=`b0fef5d3c271`) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **59 rows** (24 actionable / 20 mitigatable / 15 future_trigger) |
| `TenantBoundaryHealthReport` | **1 row** (green baseline at close) |
| Next move | Chris selects at S2795 open |

---

## Recommended session-open protocol (S2795)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2794 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §6 (open items)
4. **Freshness + regression 16-suite + ledger verify** — see S2795 open sequence above
5. **Watch for** ledger 59-row baseline surviving cascade merge; freshness FRESH · SHA-match
6. If `staleness_verdict != FRESH` → escalate
7. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. Present candidate menu — engineering leans first per `feedback_engineering_bias_over_audit`; Workspace-tab leans preferred per `feedback_workspace_over_command_center_for_new_ui`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Chris directs S2795 P0 selection
12. Mint fresh pin with candidate-scoped label
13. Route work through Rigby joint agreement before coding
14. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist

---

## Reference documents

Ordered by frequency of use at S2795:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
3. [`docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md`](docs/handoffs/SESSION_2794_TENANT_BOUNDARY_HEALTH.md) — **S2794 handoff (current)**
4. [`docs/handoffs/SESSION_2793_ZOOM_OUT_TIME_WINDOW.md`](docs/handoffs/SESSION_2793_ZOOM_OUT_TIME_WINDOW.md) — S2793 predecessor
5. [`docs/research/implementation/real_user_readiness/CAMPAIGN.md`](docs/research/implementation/real_user_readiness/CAMPAIGN.md) — RUR-C1 parent doc
6. [`docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md`](docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md) — RUR-C1 parent ratification (Chris Q1-Q9 D-verdicts)
7. [`docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030199_tenant_boundary_lockdown_implementation_close.md) — I-0301 arc close
8. [`docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md`](docs/research/implementation/tenant_boundary_lockdown/I-030299_i0302_arc_close.md) — I-0302 arc close
9. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 59 rows at S2794 close (rows 57/58/59 are S2794 F1+F2 adopted + F3 adopted)

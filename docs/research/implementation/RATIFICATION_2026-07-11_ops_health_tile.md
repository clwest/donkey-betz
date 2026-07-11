---
title: "Ops Health Command Center Tile Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2761
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (design + implementation) + Chris D-verdict + live browser verify
scope: S2761 — net-new Command Center tile surfacing S2755→S2760 diagnostic infra into one operator surface
serves_arc: RUR-C1 last-mile UI
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md (S2760 — query endpoint this tile consumes)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md (S2758 — query endpoint this tile consumes)
  - docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md (S2759 — verdict source)
ratified_documents:
  - core/views_ops_console.py (amended — health_summary view + composed _handle_ops dispatch)
  - core/urls.py (amended — /api/ops/health-summary/ route)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — Ops Health section + axios-routed query)
  - tools/pa_local.sh (amended — PA_API_TOKEN refresh to current chris token)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2761 diagnostic SIGN (pre-implementation) — Rigby F1/F2/F3 PASS on classification-of-7-findings + net-new engineering pivot
  - S2761 implementation SIGN (post-code) — Rigby F1/F2/F3/F4 PASS; recommendation "merge as-is"
  - S2761 live browser verify — Chris "it works!!" post axios-fix
frozen: true
---

# Ops Health Command Center Tile Ratification Record

Frozen canonical record of Chris's ratification of the Ops Health tile on 2026-07-11. Ships the S2755→S2760 diagnostic infra into an always-visible operator surface at Workspace → System → Ops. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** net-new Command Center tile + backend composition endpoint. Not an arc phase-close but a last-mile-UI ship per `feedback_last_mile_ui.md`.
- **Motivation:** S2755→S2760 built 3 diagnostic surfaces (`ops_tool.version` freshness verdict + `tenant_boundary_violations` for I-0303 findings + `staleness_warnings` for S2759 warning history). Each is queryable via Rigby but has no browser UI. Chris asked at S2761 open for a candidate that "connects what's built" — this tile bundles the three into one always-visible surface answering "is anything currently misfiring?"
- **Ratifier:** Chris (D-verdict against joint Claude+Rigby recommendation, plus live browser verification)

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py` — `health_summary` view

New endpoint `GET /api/ops/health-summary/` returning a compact aggregate suitable for a dashboard tile:

```json
{
  "window": "24h",
  "verdict": "FRESH" | "STALE_DAPHNE" | "STALE_CELERY" | "STALE_BOTH" | "UNKNOWN",
  "head_commit_sha_short": "<12ch>",
  "tenant_boundary_violations": {
    "total": <int>,
    "by_task_name": {<task>: <count>, ...},
    "by_failure_kind": {<kind>: <count>, ...}
  },
  "staleness_warnings": {
    "total": <int>,
    "by_verdict": {<verdict>: <count>, ...}
  }
}
```

**Implementation approach:** Reuses `OpsHandlersMixin._handle_ops` dispatch via inline `_Proxy` class (same pattern as sibling `slo_status`, `failure_signatures` endpoints in the same file). Three `_handle_ops` calls composed:

1. `{'action': 'version'}` → extract `staleness_verdict` + `head_commit_sha`
2. `{'action': 'tenant_boundary_violations', 'window': '24h', 'limit': 0}` → extract `total_count` + `by_task_name` + `by_failure_kind`
3. `{'action': 'staleness_warnings', 'window': '24h', 'limit': 0}` → extract `total_count` + `by_verdict`

Fail-soft: each sub-call wrapped in try/except returning `{'error': str(e), '_source': ...}` on failure. Overall endpoint still returns 200 with best-effort data — dashboard tile degrades gracefully rather than empty-stating on partial backend failure.

**Auth:** `@require_GET + @login_required` matching sibling ops endpoints.

### §2.2 `core/urls.py` — route registration

New line at line 2395:

```python
path('api/ops/health-summary/', lambda r: __import__('core.views_ops_console', fromlist=['health_summary']).health_summary(r), name='ops-health-summary'),
```

Late-import lambda pattern matches the 3 sibling ops endpoints registered on adjacent lines.

### §2.3 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Health tile

New section prepended to the return tree, above SLO Status. Structure:

- **Header row:** `<Activity />` icon + "Ops Health (24h)" title + verdict badge (green FRESH / gray UNKNOWN / red anything else) + verdict text + short SHA (7 chars).
- **2-column grid** (`grid-cols-1 sm:grid-cols-2`):
  - **Tenant Boundary Violations card** — Shield icon + count + by_failure_kind breakdown (top 4) when count > 0. Amber border when > 0, neutral when 0.
  - **Staleness Warnings card** — Clock icon + count + by_verdict breakdown (top 4) when count > 0. Red border when > 0, neutral when 0.

**Data fetching:** `useQuery` with `refetchInterval: 30000` (30s). Routed through the axios `api` instance imported from `@/lib/api` (not raw `fetch`) so the request interceptor attaches `Authorization: Token <token>` from `useAuthStore`. Empty catch returns `null` → tile hidden until first successful response.

### §2.4 `tools/pa_local.sh` — token refresh

Line 348: `PA_API_TOKEN` updated from stale `4b458900...` (rejected mid-session) to current chris token `8c0f1563...`. Verified via `Token.objects.filter(user=chris)`.

---

## §3. Root-Cause Pivot Recorded

**Initial implementation shipped with raw `fetch()`**, mirroring the sibling SLO/failure-signatures/blocked-agents queries already in the file. Chris hard-refreshed → tile did not render. Network tab showed `/api/ops/health-summary/` returning **401 Unauthorized** — plus all 3 sibling ops endpoints ALSO 401'd (visible in the same screenshot).

**Diagnosis chain:**

1. First hypothesis: session invalidated by Daphne restart. Confirmed by ORM check: `Session.objects.filter(session_key=<sessionid>)` returned None. Recommended Chris log out + log back in.
2. Second hypothesis (correct): raw `fetch({credentials: 'include'})` sends the session cookie but does NOT attach `Authorization: Token <token>`. The `UnifiedTokenAuthenticationMiddleware.process_request` in `core/auth_middleware.py:563` requires EITHER session-authenticated user OR Token header — Chris's browser had a stale session cookie (not in DB) AND no Authorization header, so 401. But axios calls in the same page (via `api.ts`) attached the token via request interceptor → 200.

**Fix:** Import `api` from `@/lib/api` and swap `fetch('/api/ops/health-summary/', {credentials: 'include'})` → `api.get<OpsHealthSummary>('/ops/health-summary/')`. Rebuilt → Chris confirmed "it works!!" — tile renders live with `FRESH · 70a233b · TBV=7 · STW=0`.

**Sibling bug not fixed here (out of scope):** The 3 pre-existing raw-fetch queries in the same file (SLO/failure-signatures/blocked-agents) have the same 401 bug. Filed as S2762 follow-up candidate.

---

## §4. Rigby SIGN

### §4.1 Diagnostic SIGN (pre-implementation, pin `pa-c89d8b2c8dc74985`)

F1 (classification of 7 findings): **PASS.** Category X = 2 test artifacts (correctly surfacing substrate exercise). Category Y = 5 stale-Daphne pre-recycle historical emissions. No live bug post-20:22 UTC Daphne start.

F2 leans: **D1 = (b) no filter · D2 = (a) wait for 24h window to age out · D3 = (a) dashboard tile.**

F3 joint recommendation to Chris: "Treat X+Y as non-bugs; don't filter or add repair — just let the 24h window age out. If we want an S2761 improvement, ship a small Command Center tile that shows tenant-boundary violations alongside staleness warnings so we can instantly distinguish test-noise vs stale-process artifacts next time."

### §4.2 Implementation SIGN (post-code, live-verified)

F1 endpoint shape: **Signed.** Small, cacheable, decision-ready. Reuses `_handle_ops` for semantic consistency with `ops_tool`.

F2 axios routing / auth: **Signed.** Correct fix; raw `fetch` 401 is the known footgun. 30s refetch reasonable.

F3 test coverage gap: **Signed / acceptable defer.** Low-risk read-only glue. Minimal follow-up: one API smoke test asserting 200 + keys present.

F4 merge recommendation: **Recommend merge as-is** with tiny follow-up PR to add a smoke test.

---

## §5. Chris D-Verdict

Sequence:
1. **Session-open direction:** "Lets do A" (chose fix-batch candidate)
2. **Pivot ratification:** "yes ship the tile" (accepted pivot from fix-batch to tile after classification)
3. **Live browser verification:** "it works!!" (post axios-routing fix)

Zero unresolved decisions routed per S2753 agree-first rule.

**Effect:** Ops Health tile now visible always at Workspace → System → Ops. Answers "is anything currently misfiring?" in one glance. Completes the S2755→S2760 diagnostic arc as an operator-visible surface.

---

## §6. Operational Follow-Up

- **First real use:** at S2762 open (or any future session open), Chris navigates to Workspace → System → Ops as the freshness+findings check UI companion to the Rigby round-trip protocol.
- **S2762 candidate — smoke test:** one integration test asserting `/api/ops/health-summary/` returns 200 + all top-level keys present.
- **S2762 candidate — sibling fetch fix:** same axios routing for SLO / failure-signatures / blocked-agents queries in `OpsConsoleTab.tsx`.

---

## §7. Provenance Chain

- **Predecessor sessions:** S2755 (I-0303 Phase 3 REPORT-ONLY) → S2756 (batch-fix substrate) → S2757 (batch-fix first pass) → S2758 (ops_tool.tenant_boundary_violations) → S2759 (stale-Daphne warning system) → S2760 (ops_tool.staleness_warnings) → **S2761 (this tile)**
- **PA tool data sources:** `ops_tool.version` (S2759), `ops_tool.tenant_boundary_violations` (S2758), `ops_tool.staleness_warnings` (S2760)
- **Engineering Playbook v0.5.0:** PLAYBOOK-7.4.1 (close-ceremony 1-PR bundle) + PLAYBOOK-7.6.1 (SIGN watchpoint attestation, applied twice this session)
- **Memory rules applied:** `feedback_last_mile_ui.md` (never make Chris ask "where do I see this?" — took 4 attempts to find the right surface Workspace→System→Ops) + `feedback_chris_discoverability_visibility.md` + `feedback_local_truth_no_production.md` (local pass = shipped, verified via live browser hard-refresh)

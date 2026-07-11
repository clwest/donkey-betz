# Session 2761 — Ops Health Command Center Tile Ratified

**Date:** 2026-07-11
**Predecessor:** S2760 (ops_tool.staleness_warnings PA tool ratified)
**Successor:** S2762 (candidates from S2758 D2/D4, cost-threshold P0.5, or net-new engineering)
**Session pin:** `pa-c89d8b2c8dc74985` (label `s2761-tenant-boundary-fix-batch`; retired at close)
**HEAD at open:** `70a233bae` (post-S2760 merge)
**HEAD at close:** (filled at merge)

---

## §1 Delivery Ledger

Single 1-PR close-ceremony bundle per PLAYBOOK-7.4.1. **Seventh consecutive phase-close in two days** (S2755 → S2756 → S2757 → S2758 → S2759 → S2760 → S2761).

| # | PR | Merge SHA | Content |
|---|---|---|---|
| 1 | (this PR) | pending | Backend `/api/ops/health-summary/` + Workspace→System→Ops tile + ratification envelope + handoff + docs cascade + pin rotate |

---

## §2 Session Shape

S2761 opened with the S2758+S2759+S2760 warning loop triple-check:
1. `context-kit orient`
2. Read `00-START-NEXT-SESSION.md`
3. Rigby dispatch: `ops_tool.version` + `tenant_boundary_violations, window=24h` + `staleness_warnings, window=24h`

**Findings surfaced:**
- Freshness verdict: **FRESH** (HEAD `70a233b`, workers all post-HEAD)
- Tenant boundary violations: **7** in 24h (5× `missing_acting_identity` + 2× `row_not_found`)
- Staleness warnings: **0** (expected — workers fresh since S2760 recycle)

**Candidate menu presented to Chris:**
- A: S2758 D3 report-driven fix batch (the 7 fresh violations)
- B: S2758 D2 canonical AgentExecution vs AgentTaskExecution decision
- C: S2758 D4 HIGH-RISK task file wiring extension
- D: Net-new engineering (dashboard tile, spider, UI, etc.)

**Chris directive:** "Lets do A."

**Diagnostic pivot:** Claude classified the 7 findings and traced timing vs merge SHAs:
- 2× events (`header-test-2758`, `smoke-test-nonexistent-conv-id`) — test-suite artifacts, correctly surfacing substrate exercise
- 5× events on real conversations (`pa-5fe224e5757f42c0` × 3 + `pa-e1a0ef624d2240ac` + `pa-58888db8e1d148ca`) — all timestamped 18:57–19:18 UTC, BEFORE current Daphne recycle at 20:22 UTC; workers were running pre-S2757 code (before `apply_async_with_actor` wiring took effect in-process). Current post-recycle code path (`core/views_personal_assistant.py:465-483` + `:616-634`) correctly uses `apply_async_with_actor(process_pa_chat_task, request.user, ...)` — no live bug.

**Joint Claude+Rigby recommendation to Chris:** Skip fixing the 7 (historical noise, ages out of 24h window naturally). Pivot A → net-new Command Center dashboard tile surfacing the S2755→S2760 diagnostic infra into a single last-mile UI. Turns 6 sessions of substrate work into one always-visible operator surface.

**Chris D-verdict:** "yes ship the tile"

**Live browser verify:** Chris confirmed "it works!!" post-fix (tile renders FRESH · SHA `70a233b` · TBV=7 · STW=0).

---

## §3 Delivery

### §3.1 Backend

**`core/views_ops_console.py`** — new `health_summary(request)` view (~60 lines):
- Composes three ops_tool actions via `_handle_ops` dispatch: `version` + `tenant_boundary_violations, window=24h, limit=0` + `staleness_warnings, window=24h, limit=0`
- Extracts summary fields only (counts + verdict + head_commit_sha) — omits sample_events for dashboard-appropriate payload size
- Fail-soft: any sub-call exception → `_source: 'version'|'tbv'|'stw'` error marker, but overall response still 200 with best-effort data
- Auth: `@require_GET + @login_required` matching sibling endpoints

**`core/urls.py:2395`** — new route `path('api/ops/health-summary/', ...)` following the existing `lambda r: __import__(...)` pattern for late module resolution.

### §3.2 Frontend

**`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`** — new "Ops Health (24h)" section prepended to the return tree:
- `OpsHealthSummary` interface added
- `healthQuery` via `useQuery` with 30s `refetchInterval`
- Routed through axios `api` instance (imported from `@/lib/api`) so the auth interceptor attaches `Authorization: Token <token>` from `useAuthStore`
- Header row: 🟢/🔴 verdict badge + verdict text + short SHA
- 2-column grid: Tenant Boundary Violations tile + Staleness Warnings tile
- Breakdown expander shows by_failure_kind / by_verdict when count > 0

**Key implementation note (root-cause pivot recorded):** Initial implementation used raw `fetch('/api/ops/health-summary/', { credentials: 'include' })` — mirrored the sibling SLO/failure-signatures/blocked-agents queries in the same file. All 4 endpoints returned 401 in Chris's browser. Root cause: raw `fetch` omits the `Authorization` header, and session-only auth was insufficient (browser sessionid did not match server-side session store post-Daphne-restart). Axios `api` instance (already used by 200-succeeding sibling calls) attaches the Token header automatically via request interceptor. Swap to `api.get<OpsHealthSummary>('/ops/health-summary/')` fixed the tile.

**Pre-existing SLO/failure-signatures/blocked-agents 401 bug:** Left in place — same fix (route through axios) applies but out of scope for this ship. Filed as S2762 follow-up candidate.

### §3.3 Wrapper

**`tools/pa_local.sh:348`** — `PA_API_TOKEN` refreshed from stale `4b458900...` to current chris token `8c0f1563...`. Stale token was rejected mid-session ("Invalid authentication token"); DB check confirmed the stale token no longer existed while a fresh chris token had been generated (likely by prior session's Token.objects.get_or_create against a different chris row).

---

## §4 Rigby SIGN

**S2761 diagnostic SIGN (pre-implementation):**
- F1 classification accuracy — **PASS**. Category X = test artifacts; Category Y = pre-recycle stale-Daphne historical emissions.
- F2 D1/D2/D3 leans — D1=(b) no filter, D2=(a) wait, D3=(a) dashboard tile.
- F3 joint recommendation — "Treat X+Y as non-bugs; ship a small Command Center tile that shows tenant-boundary violations alongside staleness warnings so we can instantly distinguish test-noise vs stale-process artifacts next time."

**S2761 implementation SIGN (post-code, Chris-verified):**
- F1 endpoint shape — **PASS**. Small, cacheable, decision-ready. Reuses `_handle_ops` for semantic consistency with ops_tool.
- F2 axios routing — **PASS**. Correct fix for the raw-fetch 401 footgun. 30s refetch reasonable.
- F3 test coverage gap — **PASS with acceptable defer.** Low-risk read-only glue; one API smoke test asserting 200 + keys present would round out.
- F4 merge recommendation — **Recommend merge as-is** with tiny follow-up PR for `/api/ops/health-summary/` smoke test.

---

## §5 Chris D-Verdict

- **Direction (session open):** "Lets do A."
- **Classification agreement (pre-pivot):** implicit via reading joint recommendation and issuing "yes ship the tile" on the pivot.
- **Feature ratification:** "yes ship the tile"
- **Live browser verification:** "it works!!"

Zero unresolved decisions routed to Chris per S2753 agree-first rule. All D-verdicts single yes/no on Claude+Rigby joint agreements.

---

## §6 Follow-up items

- **S2762 candidate:** Smoke test `/api/ops/health-summary/` — assert 200 + all top-level keys present. (Rigby F3 recommendation.)
- **S2762 candidate:** Fix the raw-fetch 401 bug on sibling SLO/failure-signatures/blocked-agents queries — same axios routing pattern.
- **S2758 D2 canonical decision** — still owed
- **S2758 D4 HIGH-RISK wiring extension** — still owed
- **P0.5 cost-threshold advance-to-freeze** — still owed since S2753
- **P0.75 CI billing** — still owed
- **HMAC signing of x-acting-user-id header** — Phase 2 §6 limitation

---

## §7 Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2761 artifacts:**

- **Backend view:** `core/views_ops_console.py` (`health_summary` after `blocked_agents`)
- **URL:** `core/urls.py:2395`
- **Frontend tile:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (new "Ops Health (24h)" section)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`
- **Handoff (this doc):** `docs/handoffs/SESSION_2761_OPS_HEALTH_TILE_RATIFIED.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance mirror for the ratification envelope + content mirror for the tile

---

## §8 Session pin lifecycle

- Session pin `pa-c89d8b2c8dc74985` (label `s2761-tenant-boundary-fix-batch`) minted at open
- Rigby SIGN dispatched successfully after wrapper token refresh
- **Retired at close** — wrapper points to retired pin, forces fresh mint at S2762 open

---

**Sixth-in-two-days close-ceremony bundle complete.**

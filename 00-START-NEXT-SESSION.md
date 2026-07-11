# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2761 CLOSED — OPS HEALTH COMMAND CENTER TILE RATIFIED

**Refreshed 2026-07-11 (SESSION 2761 CLOSED — Chris "it works!!" live-verified in browser. Seventh phase-close in 2 days. First last-mile UI ship since the S2755→S2760 diagnostic infra arc.).**

**S2761 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Backend** (`core/views_ops_console.py`): new `health_summary` view composing `_handle_ops` dispatch × 3 (`version` + `tenant_boundary_violations` + `staleness_warnings`) into a compact tile payload
- **URL** (`core/urls.py:2395`): `/api/ops/health-summary/` route registered
- **Frontend** (`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`): new "Ops Health (24h)" section at TOP of Workspace → System → Ops with verdict badge + SHA + 2-card grid (Tenant Boundary + Staleness) with breakdown; 30s auto-refetch via axios `api` instance
- **Wrapper** (`tools/pa_local.sh:348`): PA_API_TOKEN refreshed from stale to current chris token
- Ratification envelope: `RATIFICATION_2026-07-11_ops_health_tile.md`
- Docs cascade: 4-step complete (index → corpus → sync → embed 14 chunks) + provenance rebuild
- Handoff: `SESSION_2761_OPS_HEALTH_TILE_RATIFIED.md`

---

## THE PIVOT — WHY THIS SHIP MATTERS

S2761 opened with the S2758+S2759+S2760 warning loop triple-check surfacing 7 tenant boundary findings. Claude+Rigby diagnosed all 7 as **historical stale-Daphne artifacts + test noise** (no live bug post-20:22 UTC recycle). Instead of chasing dead findings, we pivoted to net-new engineering: a Command Center tile that answers "is anything currently misfiring?" in one glance — consuming all three S2755→S2760 diagnostic surfaces.

**Root-cause pivot recorded:** Initial raw `fetch({credentials: 'include'})` returned 401 in Chris's browser. Diagnosis chain: (1) session invalidation hypothesis wrong; (2) real cause = raw fetch omits `Authorization: Token` header. Fix: route through axios `api` instance (already used by 200-succeeding sibling calls). **Sibling SLO/failure-signatures/blocked-agents queries have the same bug (out of scope for this ship; filed as S2762 follow-up).**

---

## S2762 CANDIDATES (Chris selects at open)

### Candidate 1 — S2761 follow-ups (~30 min each)

- (a) **Smoke test** `/api/ops/health-summary/` — assert 200 + all top-level keys present (Rigby F3 recommendation)
- (b) **Fix sibling 401 bug** — route SLO / failure-signatures / blocked-agents in `OpsConsoleTab.tsx` through axios `api` instance (same pattern as S2761 tile). Un-breaks 3 pre-existing broken cards on the same page.

### Candidate 2 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive.

### Candidate 3 — S2758 D4 HIGH-RISK task file wiring extension

REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`.

### Candidate 4 — Net-new engineering

Per S2745 engineering-bias directive. Chris's pattern the last 2 days = pick candidates that ship visible operator surfaces + short close-ceremonies.

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2761 RETIRED (fresh mint required at S2762 open)

**Pin history (S2761):**

- `pa-c89d8b2c8dc74985` (label `s2761-tenant-boundary-fix-batch`) minted S2761 open; **retired at S2761 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-c89d8b2c8dc74985` (retired)** — intended failure mode forces S2762 first-action fresh mint.

**S2762 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check + findings check + tile eyeball (single Rigby + browser round-trip)
bash tools/pa_local.sh "S2762 open — three quick tool invocations: (1) ops_tool.version report staleness_verdict + head_commit_sha (2) ops_tool.tenant_boundary_violations window=24h limit=5 (3) ops_tool.staleness_warnings window=24h limit=5"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops — Ops Health tile shows same numbers

# If verdict != FRESH → run make recycle-all before continuing

# Mint fresh pin scoped to selected S2762 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2761 close)

1. **S2761 smoke test + sibling 401 fix** — Candidate 1 above
2. **S2758 D2 canonical decision** — Candidate 2 above
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3 above
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
8. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
9. **S2758 D3 report-driven fix batch** — CLOSED via S2761 diagnostic classification (findings are historical stale-Daphne noise; no code fix needed)
10. **S2758 D5 local shim retirement** — depends on D2 canonical decision
11. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2761 artifacts:**

- **Backend view:** `core/views_ops_console.py` (`health_summary` after `blocked_agents`)
- **URL:** `core/urls.py:2395`
- **Frontend tile:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`
- **Handoff:** `docs/handoffs/SESSION_2761_OPS_HEALTH_TILE_RATIFIED.md`
- **Prior handoffs (7-in-2-days chain):**
  - `SESSION_2761_OPS_HEALTH_TILE_RATIFIED.md` (this session)
  - `SESSION_2760_OPS_TOOL_STALENESS_WARNINGS_RATIFIED.md`
  - `SESSION_2759_STALE_DAPHNE_WARNING_SYSTEM_RATIFIED.md`
  - `SESSION_2758_OPS_TOOL_TENANT_BOUNDARY_VIOLATIONS_RATIFIED.md`
  - `SESSION_2757_I0303_PHASE3_BATCH_FIX_RATIFIED.md`
  - `SESSION_2756_I0303_PHASE3_REPORT_ONLY_RATIFIED.md`
  - `SESSION_2755_I0303_PHASE2_TASK_ENFORCEMENT_RATIFIED.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2761 (pending post-merge)
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **NEW: Ops Health tile** live at `localhost:8000/workspace?tab=system&sub=ops` — always-visible operator surface for S2755→S2760 diagnostic infra

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2761 tile merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2758+S2759+S2760 diagnostic infra CLOSED · **S2761 last-mile UI CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-c89d8b2c8dc74985` (retired at S2761 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-c89d8b2c8dc74985` (retired; forces fresh mint at S2762 open) |
| Live infra state | S2755→S2760 diagnostic infra + S2761 tile operational; process freshness FRESH at close |
| Next move | Chris selects at S2762 open — see Candidates above |

---

## Recommended session-open protocol (S2762)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2761 envelope `RATIFICATION_2026-07-11_ops_health_tile.md` §2 (ratified deliverables) + §6 (operational follow-up)
4. **Freshness + findings + tile eyeball (single-round-trip)** — see S2762 open sequence in §SESSION PIN above
5. If `staleness_verdict != FRESH` → `make recycle-all` before continuing
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris
8. Chris directs S2762 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2762:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md) — S2761 envelope
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md) — S2760 (tile data source)
4. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md) — S2758 (tile data source)
5. `core/services/td_handlers_ops.py` — 3 diagnostic actions (version + tenant_boundary_violations + staleness_warnings)
6. `core/views_ops_console.py` — NEW health_summary composed endpoint
7. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — NEW Ops Health tile
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0

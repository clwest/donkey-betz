# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2762 CLOSED — OPS CONSOLE SIBLING 401 FIX RATIFIED

**Refreshed 2026-07-11 (SESSION 2762 CLOSED — three broken cards on the Ops Console page un-broken via mechanical mirror of the S2761 `api.get` pattern. Eighth consecutive phase-close in two days.).**

**S2762 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Frontend** (`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`): swap raw `fetch({credentials: 'include'})` → `api.get()` for `sloQuery` / `sigQuery` / `blockedQuery` (3 sibling queries below the S2761 tile). Mirror of the ratified S2761 `healthQuery` pattern; adds `Authorization: Token <token>` via axios interceptor.
- Ratification envelope: `RATIFICATION_2026-07-11_ops_sibling_401_fix.md`
- Docs cascade: 4-step complete (index → corpus → sync → embed) + provenance rebuild
- Handoff: `SESSION_2762_OPS_SIBLING_401_FIX_RATIFIED.md`

---

## THE PIVOT — WHY THIS SHIP MATTERS

S2761 closed with three broken cards on the same page Chris just live-verified — filed as an out-of-scope follow-up in S2761 §6. S2762 ships that follow-up as candidate 1b (Claude's top lean, Chris "go with your recommendation"). Un-breaks SLO Status grid + Failure Signatures list + Blocked Agents list without touching the freshly ratified S2761 tile above them.

**Verify-before-build was cheap here** — reference pattern was 10 lines above the broken siblings, in the same file. No new abstraction. Total analysis = one Read call.

---

## S2763 CANDIDATES (Chris selects at open)

### Candidate 1 — S2761 smoke test (~20 min)

Smoke test `/api/ops/health-summary/` — assert 200 + all top-level keys present (Rigby F3 recommendation from S2761).

### Candidate 2 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive.

### Candidate 3 — S2758 D4 HIGH-RISK task file wiring extension

REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`.

### Candidate 4 — Net-new engineering

Per S2745 engineering-bias directive. Chris's 8-in-2-days pattern favors visible operator surfaces + short close-ceremonies. Standing proposals from S2762 menu:

- **N1** — Ops Health tile v2: add SLO summary panel (now that the SLO query works)
- **N2** — New PA tool `ops_tool.recent_recycles` — surface last N `make recycle-all` events + auth-refresh events
- **N3** — Workspace tab card "Session close-ceremony ledger" — read-only view of last 10 handoffs + ratification envelopes as clickable cards

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2762 RETIRED (fresh mint required at S2763 open)

**Pin history (S2762):**

- `pa-572f3ba386964005` (label `s2762-ops-sibling-401-fix`) minted S2762 open; **retired at S2762 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-572f3ba386964005` (retired)** — intended failure mode forces S2763 first-action fresh mint.

**S2763 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check + findings check + tile eyeball (single Rigby + browser round-trip)
bash tools/pa_local.sh "S2763 open — three quick tool invocations: (1) ops_tool.version report staleness_verdict + head_commit_sha (2) ops_tool.tenant_boundary_violations window=24h limit=5 (3) ops_tool.staleness_warnings window=24h limit=5"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops — All FOUR sections (Health tile + SLO grid + Signatures + Blocked) render without 401

# If verdict != FRESH → run make recycle-all before continuing (watch for corroboration of the S2762 post-merge recycle rule)

# Mint fresh pin scoped to selected S2763 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2762 close)

1. **S2761 smoke test** — Candidate 1 above
2. **S2758 D2 canonical decision** — Candidate 2 above
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3 above
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
8. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
9. **S2758 D5 local shim retirement** — depends on D2 canonical decision
10. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation
11. **`recycle-all AFTER merge` rule codification watch** — S2762 followed it; if S2763 opens FRESH not STALE_BOTH, that's corroboration to codify into playbook

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2762 artifacts:**

- **Frontend fix:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (sloQuery/sigQuery/blockedQuery)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md`
- **Handoff:** `docs/handoffs/SESSION_2762_OPS_SIBLING_401_FIX_RATIFIED.md`
- **Precedent envelope (canonical pattern):** `docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2762 (pending post-merge)
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Health tile + newly-working SLO / Signatures / Blocked cards

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2762 sibling 401 fix merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2761 diagnostic infra + tile CLOSED · **S2762 sibling 401 fix CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-572f3ba386964005` (retired at S2762 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-572f3ba386964005` (retired; forces fresh mint at S2763 open) |
| Live infra state | S2755→S2761 diagnostic infra + tile + sibling cards operational; process freshness FRESH at close |
| Next move | Chris selects at S2763 open — see Candidates above |

---

## Recommended session-open protocol (S2763)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2762 envelope `RATIFICATION_2026-07-11_ops_sibling_401_fix.md` §2 (ratified deliverables) + §6 (operational follow-up)
4. **Freshness + findings + tile eyeball (single-round-trip)** — see S2763 open sequence in §SESSION PIN above
5. If `staleness_verdict != FRESH` → `make recycle-all` before continuing (watch for corroboration signal)
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris
8. Chris directs S2763 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2763:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md) — S2762 envelope (this session)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md) — S2761 (canonical `api.get` pattern)
4. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Console page
5. `frontend/src/lib/api.ts` — axios instance with token-attaching interceptor
6. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0

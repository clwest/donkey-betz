# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2765 CLOSED — `ops_tool.recent_recycles` PA TOOL RATIFIED

**Refreshed 2026-07-11 (SESSION 2765 CLOSED — new operator-action timeline. Eleventh consecutive phase-close in two days. **FOURTH data point / THIRD independent close-cycle** for recycle-after-merge rule — codification threshold met, N5 amendment queued for S2766.).**

**S2765 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Makefile**: `recycle-all` target now appends JSONL to `logs/recycle_events.jsonl` post-restart (POSIX-atomic; single-user local).
- **PA tool** (`core/services/td_handlers_ops.py` + `pa_tool_schemas.py`): new `ops_tool.recent_recycles` action + `_ops_recent_recycles` handler with defensive tail-first parse (Rigby's atomic-append/malformed-line risk addressed).
- **REST endpoint** (`core/views_ops_console.py` + `core/urls.py:2397`): `GET /api/ops/recent-recycles/?limit=<N>` thin wrapper.
- **Frontend** (`OpsConsoleTab.tsx`): new "Recent Recycles" section between Blocked Agents and Recent Close-Ceremonies, with `<RotateCw />` icon + short-SHA badges + relative-time labels.
- Ratification envelope: `RATIFICATION_2026-07-11_ops_tool_recent_recycles.md`
- Docs cascade: 4-step complete (index → corpus → sync → embed) + provenance rebuild
- Handoff: `SESSION_2765_OPS_TOOL_RECENT_RECYCLES_RATIFIED.md`

---

## THE PIVOT — WHY THIS SHIP MATTERS

Stale-Daphne diagnoses (S2758→S2761) all cited "post-20:22 UTC recycle" as the demarcation for classifying historical findings — but that timestamp came from `daphne_started_at` inference, not a first-party emitter. S2765 closes the gap: the Makefile emits an event every time `make recycle-all` runs; the PA tool + REST surface expose the timeline. Ops Console now has the full observability trilogy for stale-process triage: **live snapshot (Ops Health tile) + post-hoc detection (Staleness Warnings) + operator-action timeline (Recent Recycles)**.

**Codification threshold met:** three independent close-cycles (S2762/S2763/S2764) all showed FRESH · SHA match at next-session-open post-recycle. S2766 candidate N5 = author Playbook §7.4.1 amendment.

---

## S2766 CANDIDATES (Chris selects at open)

### Candidate 1 — S2761 smoke test (~20 min)

Smoke test `/api/ops/health-summary/` — assert 200 + all top-level keys present (verdict + tenant_boundary_violations + staleness_warnings + slo_status).

### Candidate 2 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive.

### Candidate 3 — S2758 D4 HIGH-RISK task file wiring extension

REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`.

### Candidate 4 — **N5: Playbook §7.4.1 amendment (recycle-after-merge codification)** ⭐

Threshold met per §4.1 above. Draft amendment adding a new sub-clause to PLAYBOOK-7.4.1 requiring **`make recycle-all` as the final step of every close-ceremony bundle** (not just as a "cleanup before E2E" step per pre-S2762 convention). Precedent: 3 independent close-cycle corroborations + memory rule `feedback_recycle_after_merge.md`. This would be the first PATCH amendment to Playbook v0.5.0 → v0.5.1.

### Candidate 5 — More net-new engineering

- **N4** — Close-Ceremony Ledger v2: hover-preview + docs viewer navigation
- **N6** — Command Center home tile mirror of Ops Health (3-card grid at Workspace Home)
- **N7** *(new S2765)* — extend `recycle-all` emitter with worker PIDs before/after; use this to detect partial recycles

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2765 RETIRED (fresh mint required at S2766 open)

**Pin history (S2765):**

- `pa-a11f652a75b94ad3` (label `s2765-ops-tool-recent-recycles`) minted S2765 open; **retired at S2765 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-a11f652a75b94ad3` (retired)** — intended failure mode forces S2766 first-action fresh mint.

**S2766 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check + tile eyeball. If Chris picks N5 (Playbook amendment), the corroboration is now sealed at 3 cycles.
bash tools/pa_local.sh "S2766 open — quick check: ops_tool.version verdict + head_commit_sha; ops_tool.recent_recycles limit=5 (should show S2765 close + optional S2764 close if the emitter was retroactively invoked)"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops — SIX sections: Ops Health tile (3 cards) + SLO grid + Signatures + Blocked + Recent Recycles + Recent Close-Ceremonies

# If verdict != FRESH → run make recycle-all (but this would be a rule-violation signal; escalate to Chris).

# Mint fresh pin scoped to selected S2766 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2765 close)

1. **S2761 smoke test** — Candidate 1
2. **S2758 D2 canonical decision** — Candidate 2
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
8. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
9. **S2758 D5 local shim retirement** — depends on D2 canonical decision
10. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation
11. **N5 recycle-after-merge Playbook amendment** — **threshold met; ready to draft. Highest-value housekeeping candidate.**

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2765 artifacts:**

- **Makefile:** `Makefile:91-94` (recycle-all + emitter)
- **PA tool + schema:** `core/services/td_handlers_ops.py::_ops_recent_recycles` + `pa_tool_schemas.py` enum
- **REST view + URL:** `core/views_ops_console.py::recent_recycles` + `core/urls.py:2397`
- **Frontend:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (Recent Recycles section)
- **Data (operator-local; gitignored):** `logs/recycle_events.jsonl`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md`
- **Handoff:** `docs/handoffs/SESSION_2765_OPS_TOOL_RECENT_RECYCLES_RATIFIED.md`
- **Precedent envelopes:** S2761 tile, S2762 sibling fix, S2763 ledger, S2764 tile v2
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2765
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Health tile (3 cards) + SLO grid + Signatures + Blocked + **Recent Recycles (new)** + Recent Close-Ceremonies

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2765 merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2764 diagnostic infra + tile + sibling fix + ledger + tile v2 CLOSED · **S2765 recent_recycles CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-a11f652a75b94ad3` (retired at S2765 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-a11f652a75b94ad3` (retired; forces fresh mint at S2766 open) |
| Live infra state | S2755→S2764 substrate + Recent Recycles section + first-ever `logs/recycle_events.jsonl` entry (dogfooded at S2765 close); process freshness FRESH at close |
| Next move | Chris selects at S2766 open — see Candidates above |

---

## Recommended session-open protocol (S2766)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2765 envelope `RATIFICATION_2026-07-11_ops_tool_recent_recycles.md` §3 (concurrency defense) + §4.1 (corroboration ladder)
4. **Freshness + findings + tile eyeball (single-round-trip)** — see S2766 open sequence in §SESSION PIN above
5. If `staleness_verdict != FRESH` → **this would be a rule-violation signal; escalate to Chris**
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris (highlight N5 amendment as highest-value)
8. Chris directs S2766 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2766:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_recent_recycles.md) — S2765 envelope (this session)
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md) — S2764
4. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md) — S2763
5. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md) — S2762
6. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md) — S2761
7. `core/services/td_handlers_ops.py` — PA tool handler bank
8. `core/views_ops_console.py` — Ops Console REST endpoints (6 views now)
9. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Console page (6 sections; tile is 3-card wide)
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0 (**candidate for v0.5.1 PATCH amendment at S2766**)

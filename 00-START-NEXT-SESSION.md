# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2764 CLOSED — OPS HEALTH TILE v2 (SLO CARD) RATIFIED

**Refreshed 2026-07-11 (SESSION 2764 CLOSED — Ops Health tile now 3-card wide with SLO breach summary. Tenth consecutive phase-close in two days. Second independent close-cycle corroboration of the recycle-after-merge rule; one arc-close away from Playbook amendment proposal.).**

**S2764 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Backend** (`core/views_ops_console.py`): extended `health_summary` view with a 4th `_safe_call({'action': 'slo_status', 'window': '24h'})`; new `_summarize_slos()` helper reducing the SLO list to `{total, breach_count, healthy_count, worst_breach}` with polarity-aware direction guard (`target` = lower-is-worse; `target_max` = upper-is-worse).
- **Frontend** (`frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx`): `OpsHealthSummary` type extended; tile grid `sm:grid-cols-2` → `sm:grid-cols-3`; new SLO Breaches card with `<Zap />` icon (previously unused import — now consumed), green when 0 / red with worst-breach preview when > 0.
- Ratification envelope: `RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md`
- Docs cascade: 4-step complete (index → corpus → sync → embed) + provenance rebuild
- Handoff: `SESSION_2764_OPS_HEALTH_TILE_V2_SLO_RATIFIED.md`

---

## THE PIVOT — WHY THIS SHIP MATTERS

The S2761 tile answered "are tenant boundaries being violated?" + "are workers stale?" in 2 cards. The detailed SLO Status grid below required visual scanning across 8 SLO cards to answer "is anything actively breaching?" S2764 compresses that answer to a single number + worst-breach preview at the tile level. Ops Health tile is now the operator's canonical single-glance answer to "is the platform currently healthy?"

**Rigby's SIGN callout on direction polarity was legit** — SLOs are a mix of lower-is-worse (`target` field, e.g. 99.9% success rate floor) and upper-is-worse (`target_max` field, e.g. 0.2% timeout rate ceiling). Naive gap math would mis-rank. Guard applied pre-code.

---

## S2765 CANDIDATES (Chris selects at open)

### Candidate 1 — S2761 smoke test (~20 min)

Smoke test `/api/ops/health-summary/` — assert 200 + all top-level keys present (Rigby F3 recommendation from S2761). Now four keys to check: verdict + tenant_boundary_violations + staleness_warnings + slo_status.

### Candidate 2 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive.

### Candidate 3 — S2758 D4 HIGH-RISK task file wiring extension

REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`.

### Candidate 4 — Net-new engineering

Per S2745 engineering-bias directive. Standing proposals:

- **N2** — New PA tool `ops_tool.recent_recycles` — surface last N `make recycle-all` events + auth-refresh events
- **N4** — Close-Ceremony Ledger v2: render title/date/one-liner previews when a card is hovered/clicked; navigate to a `/docs/*` viewer route
- **N5** — Playbook amendment proposal for the recycle-after-merge rule (**one more independent close-cycle corroboration required first**)
- **N6** *(new S2764)* — Command Center home tile for Ops Health — thumbnail version of the 3-card grid at Workspace Home, so freshness/breach state is visible even when not on the System→Ops tab

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2764 RETIRED (fresh mint required at S2765 open)

**Pin history (S2764):**

- `pa-4594e726e18e4ccf` (label `s2764-ops-health-tile-v2-slo`) minted S2764 open; **retired at S2764 close**

**Wrapper `tools/pa_local.sh:539` still points at `pa-4594e726e18e4ccf` (retired)** — intended failure mode forces S2765 first-action fresh mint.

**S2765 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check + tile eyeball (single Rigby + browser round-trip). Watch for FRESH — that's the THIRD independent close-cycle corroboration point.
bash tools/pa_local.sh "S2765 open — three quick tool invocations: (1) ops_tool.version report staleness_verdict + head_commit_sha (2) ops_tool.tenant_boundary_violations window=24h limit=5 (3) ops_tool.staleness_warnings window=24h limit=5"

# Browser eyeball: hard-refresh localhost:8000/workspace?tab=system&sub=ops — Ops Health tile shows 3 cards (Tenant Boundary / Staleness / SLO Breaches) + Recent Close-Ceremonies at bottom

# If verdict != FRESH → run make recycle-all before continuing (would be a negative signal — escalate to Chris before codifying).

# Mint fresh pin scoped to selected S2765 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2764 close)

1. **S2761 smoke test** — Candidate 1 above (now covers 4 top-level keys)
2. **S2758 D2 canonical decision** — Candidate 2 above
3. **S2758 D4 HIGH-RISK wiring extension** — Candidate 3 above
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
8. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
9. **S2758 D5 local shim retirement** — depends on D2 canonical decision
10. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation
11. **`recycle-all AFTER merge` rule codification watch** — **S2762 + S2763 closes both corroborated (2 independent close-cycles). Third independent arc-close → propose Playbook §7.4.1 amendment.**

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` + `/frontend/` — S2764 artifacts:**

- **Backend:** `core/views_ops_console.py` (`health_summary` extension + `_summarize_slos`)
- **Frontend:** `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` (tile 3rd card + type extension)
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md`
- **Handoff:** `docs/handoffs/SESSION_2764_OPS_HEALTH_TILE_V2_SLO_RATIFIED.md`
- **Precedent envelopes:** S2761 tile v1, S2762 sibling fix, S2763 ledger
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — governance + content mirrors for S2764
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program
- **Live surface:** `localhost:8000/workspace?tab=system&sub=ops` — Ops Health tile now 3-card wide + Recent Close-Ceremonies at bottom

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2764 tile v2 merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 Phase 3 stage 2 first pass CLOSED · S2755→S2763 diagnostic infra + tile v1 + sibling fix + ledger CLOSED · **S2764 tile v2 SLO card CLOSED** · RUR-C1 parent OPEN |
| Session pin | `pa-4594e726e18e4ccf` (retired at S2764 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-4594e726e18e4ccf` (retired; forces fresh mint at S2765 open) |
| Live infra state | S2755→S2763 diagnostic infra + tile v1 + sibling cards + ledger + tile v2 SLO card operational; process freshness FRESH at close |
| Next move | Chris selects at S2765 open — see Candidates above |

---

## Recommended session-open protocol (S2765)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2764 envelope `RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md` §3 (direction guard) + §4 (SIGN + corroboration ladder)
4. **Freshness + findings + tile eyeball (single-round-trip)** — see S2765 open sequence in §SESSION PIN above
5. If `staleness_verdict != FRESH` → `make recycle-all` before continuing (escalate — negative signal for the recycle-after-merge rule)
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris
8. Chris directs S2765 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2765:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile_v2_slo.md) — S2764 envelope
3. [`docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md`](docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md) — S2763
4. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md) — S2762
5. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md) — S2761
6. `core/views_ops_console.py` — Ops Console REST endpoints (5 views; health_summary now composes 4 dispatches)
7. `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Console page (5 sections; tile is 3-card wide)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0

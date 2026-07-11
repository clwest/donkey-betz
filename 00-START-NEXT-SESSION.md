# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2760 CLOSED — `ops_tool.staleness_warnings` PA TOOL RATIFIED

**Refreshed 2026-07-11 (SESSION 2760 CLOSED — Chris D-verdict "approved, ship it" on the S2759-warning-loop-completing PA tool. Sixth phase-close today.).**

**S2760 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Schema** (`core/services/pa_tool_schemas.py`): `staleness_warnings` added to ops_tool action enum (24th) + description cross-referencing `check_process_staleness` Beat task + `make recycle-all` fix pointer
- **Handler** (`core/services/td_handlers_ops.py`): new elif branch + `_ops_staleness_warnings` method (~110 lines) — parallel-shape lift from S2758 `_ops_tenant_boundary_violations`; aggregates by verdict + by head_commit_sha (**operational money bucket**: which merge did we forget to recycle after?); full process detail in sample_events; empty-state note cross-references `ops_tool.version`
- **Test suite** — 9 new tests (9/9 passing, 189s runtime)
- **E2E verified live** post `make recycle-all` — Rigby dispatched `ops_tool.staleness_warnings, window=24h` → 10ms server-side, empty-state note returned
- Ratification envelope: `RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md`
- Session-open pin rotation on `tools/pa_local.sh:539`
- Handoff + docs cascade + close bookmark

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_ops_tool_staleness_warnings` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |
| `ops_tool.staleness_warnings PA Tool (mirror)` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |

---

## S2759+S2760 WARNING LOOP NOW COMPLETE

The stale-Daphne detection system Chris asked for at S2759 open is fully wired end-to-end:

- **Live check** (S2759): `ops_tool.version` returns `staleness_verdict` in real time
- **Passive detection** (S2759): `check_process_staleness` Beat task every 30 min emits `OpsRunEvent(label='staleness_warning')` when verdict != FRESH
- **Query surface** (S2760): `ops_tool.staleness_warnings` reads accumulated warning history with aggregates by verdict + by head_commit_sha

**S2761 open protocol** — a single Rigby round-trip now covers freshness + both findings surfaces:

```
bash tools/pa_local.sh "S2761 open — three checks: (1) ops_tool.version staleness_verdict (2) ops_tool.tenant_boundary_violations window=24h (3) ops_tool.staleness_warnings window=24h"
```

---

## S2761 CANDIDATES (Chris selects at open)

### Candidate 1 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive:
- (a) Add `execution_id` field to `AgentExecution`, migrate writers, deprecate `AgentTaskExecution`. Multi-PR.
- (b) Reaffirm `AgentTaskExecution` as domain-distinct canonical. Retire shim by promoting predicate to `object_authz.py`.
- (c) Defer decision to a dedicated arc; keep Phase 3 REPORT-ONLY shim.

### Candidate 2 — S2758 D4 HIGH-RISK task file wiring extension

Follow-up REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`. Same discipline as S2756 REPORT-ONLY.

### Candidate 3 — Net-new engineering item

Per S2745 engineering-bias directive. Examples:
- Command Center dashboard tile (tenant_boundary_violations count, staleness_warnings count, or both)
- New PA tool for another operational-diagnostic surface
- New spider / UI page / capability

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2760 RETIRED (fresh mint required at S2761 open)

**Pin history (S2760 arc):**

- `pa-ff2e72598c034b6d` (label `s2760-direction-consult`) minted at S2760 open for direction ask; retired via atomic rotate to C3-scoped pin
- `pa-01bb57dafdb743f0` (label `s2760-ops-tool-staleness-warnings`) minted S2760 C3 execution; **retired at S2760 close** (`updated_count=<n>`)

**Wrapper `tools/pa_local.sh:539` still points at `pa-01bb57dafdb743f0` (retired)** — intended failure mode forces S2761 first-action fresh mint.

**S2761 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check + findings check in ONE Rigby round-trip (S2759+S2760 loop complete)
bash tools/pa_local.sh "S2761 open — three quick tool invocations: (1) ops_tool version report staleness_verdict + head_commit_sha (2) ops_tool tenant_boundary_violations window=24h limit=5 (3) ops_tool staleness_warnings window=24h limit=5"

# If verdict != FRESH → run make recycle-all before continuing

# Mint fresh pin scoped to selected S2761 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until wrapper is repointed.

---

## OPEN RUNTIME ITEMS (from S2760 close)

1. **S2758 D2 canonical decision** — Candidate 1 above
2. **S2758 D4 HIGH-RISK wiring extension** — Candidate 2 above
3. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no
4. **P0.75 CI billing** — status check
5. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
6. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1
7. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
8. **S2758 D3 report-driven fix batch** — findings accumulating via S2758 tool
9. **S2758 D5 local shim retirement** — depends on D2 canonical decision
10. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2760 artifacts:**

- **Schema:** `core/services/pa_tool_schemas.py` (ops_tool.staleness_warnings action)
- **Handler:** `core/services/td_handlers_ops.py` (`_ops_staleness_warnings` method after `_ops_tenant_boundary_violations`)
- **Test suite (9/9 passing):** `tests/security/test_ops_tool_staleness_warnings.py`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md`
- **Prior handoffs (6-in-a-day chain):**
  - `docs/handoffs/SESSION_2760_OPS_TOOL_STALENESS_WARNINGS_RATIFIED.md` (this session)
  - `docs/handoffs/SESSION_2759_STALE_DAPHNE_WARNING_SYSTEM_RATIFIED.md`
  - `docs/handoffs/SESSION_2758_OPS_TOOL_TENANT_BOUNDARY_VIOLATIONS_RATIFIED.md`
  - `docs/handoffs/SESSION_2757_I0303_PHASE3_BATCH_FIX_RATIFIED.md`
  - `docs/handoffs/SESSION_2756_I0303_PHASE3_REPORT_ONLY_RATIFIED.md`
  - `docs/handoffs/SESSION_2755_I0303_PHASE2_TASK_ENFORCEMENT_RATIFIED.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **21 deliverables** after S2760 close (19 pre-existing + 2 new)
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2760 tool merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 through Phase 3 stage 2 first pass CLOSED · **S2758 + S2759 + S2760 operational infrastructure loop complete** · RUR-C1 parent OPEN |
| Session pin | `pa-01bb57dafdb743f0` (retired at S2760 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-01bb57dafdb743f0` (retired; forces fresh mint at S2761 open) |
| Live infra state | S2759 warning system + S2760 query action operational; process freshness verified FRESH at close |
| Next move | Chris selects at S2761 open — see Candidates above |

---

## Recommended session-open protocol (S2761)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2760 envelope `RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md` §2 (ratified deliverables) + §5 (operational follow-up)
4. **Freshness + findings check (single Rigby round-trip per S2759+S2760 loop)** — see S2761 open sequence in §SESSION PIN above
5. If `staleness_verdict != FRESH` → `make recycle-all` before continuing
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris
8. Chris directs S2761 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2761:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_staleness_warnings.md) — S2760 envelope
3. [`docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md`](docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md) — S2759 warning system
4. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md) — S2758 sibling tool
5. `core/services/td_handlers_ops.py` — all 3 diagnostic actions (version + tenant_boundary_violations + staleness_warnings)
6. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0

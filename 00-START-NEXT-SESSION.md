# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2759 CLOSED — STALE-DAPHNE WARNING SYSTEM RATIFIED

**Refreshed 2026-07-11 (SESSION 2759 CLOSED — Chris D-verdict "approved, ship it" on the stale-Daphne / stale-Celery warning system. Fifth phase-close today; codifies a 3-incident class regression that silently affected S2755/S2756/S2757 view-layer merges.).**

**S2759 shipped in 1-PR close-ceremony bundle (per PLAYBOOK-7.4.1):**

- **Root cause analysis** — S2758 tool's real finding traced empirically to stale Daphne (started Jun 30, 11 days pre-merge). `make celery-recycle` bounces only Celery workers; Daphne holds ASGI-served view code separately.
- **`make recycle-all`** Makefile target (aliases `restart`, S2759-explicit docstring)
- **`ops_tool.version` staleness detection** — new response fields: `staleness_verdict` (FRESH / STALE_DAPHNE / STALE_CELERY / STALE_BOTH / UNKNOWN), `head_commit_sha`, `head_commit_timestamp`, `daphne_pid_age_seconds`, `celery_workers_status[]`, `staleness_fix`. Uses `psutil.process_iter()` cross-platform.
- **`check_process_staleness`** Beat task — every 30 min via `crontab(minute='*/30')`. Emits `OpsRunEvent(label='staleness_warning')` when verdict != FRESH.
- **Test suite** — 10 new tests (10/10 passing, 190s runtime)
- **Memory rule update** — `feedback_local_truth_no_production` extended: `make recycle-all` is canonical deploy step, trigger list broadened to ASGI-served surfaces + Celery-served, freshness check at close
- **E2E verified live** post `make recycle-all` — `staleness_verdict=FRESH`, all 6 processes reporting `started_before_head_commit=false`
- Ratification envelope: `RATIFICATION_2026-07-11_stale_daphne_warning_system.md`
- Session-open pin rotation on `tools/pa_local.sh:539` (S2759 protocol)
- Handoff + docs cascade + close bookmark

**Workspace deliverables created this session:**

| Deliverable | UUID | Workspace |
|---|---|---|
| `RATIFICATION_20260711_stale_daphne_warning_system` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |
| `Stale-Daphne Warning System (mirror)` | (filled at create) | RUR-C1 Tenant Boundary Lockdown |

---

## S2760 CANDIDATES (Chris selects at open)

### Candidate 1 — S2758 D2 canonical AgentExecution vs AgentTaskExecution decision

Design SIGN required. Three approaches (a/b/c) need Chris directive:
- (a) Add `execution_id` field to `AgentExecution`, migrate writers, deprecate `AgentTaskExecution`. Multi-PR.
- (b) Reaffirm `AgentTaskExecution` as domain-distinct canonical (task-execution-tracking distinct from AgentExecution orchestration-tracking). Retire shim by promoting predicate to `object_authz.py`.
- (c) Defer decision to a dedicated arc; keep Phase 3 REPORT-ONLY shim.

### Candidate 2 — S2758 D4 HIGH-RISK task file wiring extension

Follow-up REPORT-ONLY-shape PR for `tasks_initiatives.py` + `tasks_content.py` + `tasks_media.py` + `tasks_misc.py`. Same discipline as S2756 REPORT-ONLY.

### Candidate 3 — S2759 L2 follow-up: `ops_tool.staleness_warnings` query action

New ops_tool action parallel to `tenant_boundary_violations` (S2758). Queries `OpsRunEvent(label='staleness_warning')` rows for warning history. Cheap; only worth building if Beat task warnings actually accumulate.

### Candidate 4 — Net-new engineering item

Per S2745 engineering-bias directive. Examples:
- New Command Center tile: staleness dashboard tile OR tenant_boundary_violations dashboard tile
- New PA tool for another operational-diagnostic surface
- New spider / UI page / capability

### Housekeeping (still owed)

- **P0.5** — Cost-threshold advance-to-freeze routing (owed since S2753)
- **P0.75** — CI billing status check

---

## SESSION PIN — S2759 RETIRED (fresh mint required at S2760 open)

**Pin history (S2759 arc):**

- `pa-58888db8e1d148ca` (label `s2759-rigby-dispatch-conversion` — stale label after mid-session scope pivot away from dispatch conversion toward the codified stale-Daphne warning system) minted S2759 open; **retired at S2759 close** (`updated_count=<n>`)

**Wrapper `tools/pa_local.sh:539` still points at `pa-58888db8e1d148ca` (retired)** — intended failure mode forces S2760 first-action fresh mint.

**S2760 open sequence:**

```
context-kit orient

# Read this file end-to-end

# Freshness check at open (per S2759 codified rule)
bash tools/pa_local.sh "invoke ops_tool version, report staleness_verdict"
# Expect FRESH. If STALE_*, run `make recycle-all` before continuing.

# Try the S2758 tool — check for new tenant_boundary_violation findings
bash tools/pa_local.sh "Show me tenant_boundary_violations in the last 24h"

# Check for accumulated staleness_warning events (new S2759 output)
python manage.py shell -c "
from core.models_ops_runs import OpsRunEvent
n = OpsRunEvent.objects.filter(label='staleness_warning').count()
print(f'staleness_warning events accumulated: {n}')
"

# Mint fresh pin scoped to selected S2760 candidate
python manage.py session_lifecycle open --label <candidate-scoped-label>

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

Rigby will not dispatch until the wrapper is repointed to the new pin.

---

## OPEN RUNTIME ITEMS (from S2759 close)

1. **S2758 D2 canonical decision** — Candidate 1 above
2. **S2758 D4 HIGH-RISK wiring extension** — Candidate 2 above
3. **S2759 L2 staleness_warnings query action** — Candidate 3 (opt-in)
4. **P0.5 cost-threshold advance-to-freeze** — Claude+Rigby joint recommendation → Chris yes/no (still owed since S2753)
5. **P0.75 CI billing** — status check
6. **PA celery worker bounce** — Rigby stall fix #3119 still not activated
7. **RUR-C2 open eligible** — Wave 1 staged-overlap per Chris Q1 (I-0301 safety contract signed)
8. **S2758 D1 process_pa_chat_task payload strip** — deferred (HTTP-side bootstrap refactor)
9. **S2758 D3 report-driven fix batch** — findings accumulating via S2758 tool
10. **S2758 D5 local shim retirement** — depends on D2 canonical decision
11. **HMAC signing of `x-acting-user-id` header** — Phase 2 §6 limitation

---

## Twin-pointer card

📁 **Repo `/docs/` + `/core/` — S2759 artifacts:**

- **`make recycle-all`:** `Makefile:80-91`
- **Staleness detection:** `core/services/td_handlers_ops.py` (`_ops_version` + `_compute_process_staleness`)
- **Beat task:** `core/tasks_beat_health.py` (`check_process_staleness`) + `core/celery.py:868` (schedule)
- **Schema description:** `core/services/pa_tool_schemas.py` (ops_tool.version)
- **Test suite (10/10 passing):** `tests/security/test_process_staleness_detection.py`
- **Memory rule updated:** `~/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/feedback_local_truth_no_production.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md`
- **Prior handoffs (5-in-a-day chain):**
  - `docs/handoffs/SESSION_2759_STALE_DAPHNE_WARNING_SYSTEM_RATIFIED.md` (this session)
  - `docs/handoffs/SESSION_2758_OPS_TOOL_TENANT_BOUNDARY_VIOLATIONS_RATIFIED.md`
  - `docs/handoffs/SESSION_2757_I0303_PHASE3_BATCH_FIX_RATIFIED.md`
  - `docs/handoffs/SESSION_2756_I0303_PHASE3_REPORT_ONLY_RATIFIED.md`
  - `docs/handoffs/SESSION_2755_I0303_PHASE2_TASK_ENFORCEMENT_RATIFIED.md`
- **Playbook v0.5.0:** `docs/ENGINEERING_PLAYBOOK.md`

🖥️ **Workspace UI — `/workspaces` surface:**

- **RUR-C1 Tenant Boundary Lockdown** (`fcd7e683-3bfe-4d35-9704-0e54dd587ea1`) — **19 deliverables** after S2759 close (17 pre-existing + 2 new)
  - Governance-truth ratifications (Phase 2 + Phase 3 REPORT-ONLY + Phase 3 BATCH-FIX + S2758 tool + S2759 warning system)
  - Engineering-truth mirrors
- **Architecture & Research** (`a9a16593-e0a4-44dc-8256-efc65d524b3c`) — governance / Playbook ratifications
- **Real User Readiness Campaign** (`638e9e90-47b4-4bd4-a872-bf16181cf3b5`) — parent program workspace

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | (filled at merge — post-S2759 stale-Daphne warning system merge) |
| Playbook version | v0.5.0 (RATIFIED S2753) |
| RUR-C1 state | I-0301 CLOSED · I-0302 CLOSED · I-0303 through Phase 3 stage 2 first pass CLOSED · S2758 tool + S2759 warning system operational · RUR-C1 parent OPEN |
| Session pin | `pa-58888db8e1d148ca` (retired at S2759 close) |
| Wrapper default pin | `tools/pa_local.sh:539` — `pa-58888db8e1d148ca` (retired; forces fresh mint at S2760 open) |
| Live infra state | Local-only per Chris S2758 directive; S2759 stale-Daphne warning system live |
| Process freshness at close | FRESH (all 6 processes started_before_head_commit=false at HEAD fd21d4bae) |
| I-0303 next move | Chris selects at S2760 open — see Candidates above |

---

## Recommended session-open protocol (S2760)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2759 envelope `RATIFICATION_2026-07-11_stale_daphne_warning_system.md` §2 (root cause) + §5 (E2E verification)
4. **First move — freshness check per S2759 codified rule:** `bash tools/pa_local.sh "invoke ops_tool version, report staleness_verdict"`. Expect FRESH.
5. **Second move — accumulated findings check:** S2758 tool + S2759 staleness_warning count (see S2760 open sequence in §SESSION PIN)
6. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
7. Present candidate menu to Chris
8. Chris directs S2760 P0 selection
9. Mint fresh pin with candidate-scoped label
10. Route work through Rigby joint agreement before coding

---

## Reference documents

Ordered by frequency of use at S2760:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol
2. [`docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md`](docs/research/implementation/RATIFICATION_2026-07-11_stale_daphne_warning_system.md) — S2759 envelope
3. [`docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md`](docs/research/implementation/RATIFICATION_2026-07-11_ops_tool_tenant_boundary_violations.md) — S2758 envelope (sibling operational infrastructure)
4. `core/services/td_handlers_ops.py` — S2758 + S2759 handler code
5. [`docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md`](docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase3_batch_fix.md) — S2757 (open D2/D4 backlog)
6. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.5.0

# `agent_capability_drift_tool` — Validation Report (S3044)

**Tool:** `agent_capability_drift_tool`
**Schema:** `core/services/pa_tool_schemas.py:6072`
**Handler:** `core/services/td_handlers_agents.py:6977` (`_handle_agent_capability_drift`)
**Register site:** `core/services/tool_dispatcher.py` (agent-drift registration)
**Session:** S3044 (Path B systematic sweep FINISH — Batch 1)
**HEAD at validation:** `eb38187ec` (2026-07-30)
**Ship shape:** Doc-only (S2796 shape).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S3044 A1 SIGN AGREE (11 tool_runs) — see §Related.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** analyzed
**Mutation safety:** dry_run_supported

---

## 1. Purpose / when-to-use

Run the agent capability drift scanner (read-only) to answer "do we know what agents we have and whether they still work?" before answering a customer question. Same codepath as the `scan_agent_capability_drift` management command — one source of truth (S2953 Rigby SIGN refinement).

Checks four invariants:
1. Every `AGENT_MAP` entry has a matching `Agent` DB row.
2. Every non-internal agent has enum + mapping + dispatcher-handler coverage.
3. Every 'supported'-tier agent has ≥1 successful execution in the recent window (default 30 days).
4. `capabilities_exceptions.yaml` allowlist can suppress findings per tier: internal-only / legacy / rerouted / experimental.

Use `summary` for a totals-only dashboard read. Use `scan` for the full finding-by-finding report (includes suppressed findings for audit).

Distinct from `agent_control_tool` (which manages Agent DB rows) and `execution_history_tool` (which queries individual execution rows). This tool is the invariant-audit surface.

## Covered actions

- `summary` — read — verified analyzed. Returns `{ok, action: 'summary', scanned_at, totals, has_active_failures, has_active_warnings}`. Totals include `agent_map_entries`, `active_findings`, `suppressed_findings` counts. Cheap default for status-check dispatches.
- `scan` — read — verified analyzed. Returns `{ok, action: 'scan', scanned_at, totals, has_active_failures, has_active_warnings, findings[], suppressed_findings[]}`. Full report; each finding carries `invariant`, `severity`, `agent_name`, `details`.

## 3. Schema notes

- **Required:** `action` (enum: `scan, summary`).
- **Optional:** `recent_window_days` (int, default 30 from `agent_capability_drift.DEFAULT_RECENT_WINDOW_DAYS`), `invariant` (enum: `all, agent_map_to_db, exposure_completeness, recent_execution` — default `all`).
- **Invariant filter:** when `invariant != 'all'`, both `findings` and `suppressed_findings` lists are filtered to matching entries (handler line 7002-7008).
- **Default action:** when caller omits `action`, handler defaults to `summary` (handler line 6994).

## 4. Golden-path examples

**"Any capability drift right now?"**

```
agent_capability_drift_tool  action=summary
```

**"Show me the full report, but only for the recent-execution invariant:"**

```
agent_capability_drift_tool  action=scan  invariant=recent_execution
```

**"Show me drift with a 7-day recency window instead of 30:"**

```
agent_capability_drift_tool  action=summary  recent_window_days=7
```

## 5. Failure / empty-state / pagination notes

- **Unknown action** — dispatcher-layer `unknown_action` error envelope (schema-enforced enum).
- **Empty findings** — `{ok: true, action, totals, findings: [], suppressed_findings: []}` — normal state when platform is clean.
- **`recent_window_days=0`** — coerced to int; scanner treats as 0-day window (all supported-tier agents fail invariant 3). Not clamped.
- **No pagination** — full findings list returned in one payload. `scan` may return large payload on drift-heavy platforms.

## 5c. Contract ↔ Implementation Consistency

### 5c.1 Handler / module header claims match action reality

**PASS.** Schema `description` names the 4 invariants + the suppression allowlist. Handler at 6977-7019 wraps `AgentCapabilityDriftScanner.run_all()` — same codepath as the management command per S2953 refinement.

### 5c.2 Gating truth matches runtime behavior

**PASS.** No feature flag gates this tool. Runtime behavior always reflects live `AGENT_MAP` + `Agent` table + recent `AgentExecution` window.

### 5c.3 Shared handler-file coupling noted

Shared module: `td_handlers_agents.py`. Adjacent tools include `agent_control_tool` (Agent-row CRUD), `agent_memory_tool` (Agent memory rows), and `agent_job_status` (also authored in S3044 Batch 1).

## 6. Evidence

**Analyzed-mode validation.** Handler at `td_handlers_agents.py:6977-7019` read line-by-line; behavior verified against schema at `pa_tool_schemas.py:6072-6106` and against `core/services/agent_capability_drift.py` (`AgentCapabilityDriftScanner.run_all` + `to_dict`).

**Zero mutation surface** — this tool wraps a scanner that reads Agent + AgentMap + AgentExecution rows and returns a dict. No writes; no Celery dispatch; no external I/O.

## Related

- **Codepath twin:** `scan_agent_capability_drift` management command (`core/management/commands/scan_agent_capability_drift.py`) — Rigby SIGN-refined single-codepath rule ratified S2953.
- **Adjacent audit surface:** `agent_introspection_tool` (Batch 2 target — `td_handlers_ops.py`).
- **Suppression rules source:** `capabilities_exceptions.yaml`.
- **Shared handler module:** `td_handlers_agents.py`.
- **Path B FINISH plan:** `docs/audits/pa_tools/substrate/S3044_path_b_finish_plan.md`.
- **S3044 Rigby A1 SIGN cycle:** 11 tool_runs; AGREE on Q1-Q4; Q5 zoom-out folded.

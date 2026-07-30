# `ops_tool` — Validation Report (S2796)

**Tool:** `ops_tool`
**Schema:** `core/services/pa_tool_schemas.py:2437`
**Handler:** `core/services/td_handlers_ops.py:184` (`_handle_ops`)
**Register site:** `core/services/tool_dispatcher.py:500`
**Session:** S2796 (Slice 1 of `td_handlers_ops` validation — cheapest 4-tool subslice from S2795 gap map)
**HEAD at validation:** `0c38718b0`
**Ship shape:** Doc-only (per S2796 Chris directive "validation quickest"). Regression tests deferred to a follow-up PR.
**Category upgrade target:** `untested` → `validated_full` (per `core/services/pa_tools_gap_map.py` classifier)
**Rigby SIGN:** S2796 T1 SIGN-WITH-EDITS; 6-section template per Rigby Z3; evidence-section per Rigby Z1 edit A (F1 mitigation, ledger row 65).

---

## 1. Purpose / when-to-use

`ops_tool` is the production operations surface for reliability + deployment observability. It's the workhorse of session-open freshness checks + post-merge recycle verification + SLO drift detection. Every session's freshness gate at open+close touches `ops_tool.version` + `ops_tool.recent_recycles`; SLO-adjacent audits and incident triage touch `slo_status`, `failure_signatures`, and `staleness_warnings`.

Distinct from `diagnostics_tool` — `diagnostics_tool` is per-component inventory/audit telemetry (advisors, LLM providers, beat schedules); `ops_tool` is production reliability + deploy state. When the user asks "is the stack fresh?" or "did the last recycle land?" → `ops_tool.version` / `ops_tool.recent_recycles`. When asked "which advisor personas are dead?" → `diagnostics_tool.advisor_invocations`.

## Covered actions

All 20 schema-declared actions enumerated as a flat list for the S2795 gap-map classifier. Per-action admission class inlined per Rigby SIGN Z1 edit A (F1) — either observed evidence (see §Evidence) or explicit `runtime-not-executed` marker.

- `version` — **in scope this ship** — verified live at S2796 T1 freshness check. Returns `staleness_verdict` (FRESH / STALE_DAPHNE / STALE_CELERY / STALE_BOTH / UNKNOWN) + `head_commit_sha` + per-process ages.
- `recent_recycles` — **in scope this ship** — verified live at S2796 T1. Reads tail of `logs/recycle_events.jsonl`. Includes SHA + label + `seconds_ago` per event.
- `overview` — runtime-not-executed. One-shot ops snapshot (version + slo_status + top failure_signatures + noise_metrics).
- `slo_status` — runtime-not-executed. 8 SLOs with breach detection.
- `failure_signatures` — runtime-not-executed. Top error signatures by frequency.
- `tool_migration_report` — runtime-not-executed. Legacy-vs-gateway tool usage.
- `timeout_config_read` — runtime-not-executed. Agent wall-clock timeout config.
- `proof_bundle` — runtime-not-executed. Timeout config + agent control audit log + initiative details.
- `noise_metrics` — runtime-not-executed. North Star coverage (revenue/content/sports vs noise).
- `conversation_metrics` — runtime-not-executed. Topic clustering + zombie rate.
- `focus_mode_status` — runtime-not-executed. Read Focus Mode config.
- `focus_mode_update` — runtime-not-executed. **Mutating action — regression test priority for follow-up PR.**
- `celery_task_history` — runtime-not-executed. Recent Celery runs by task name.
- `execution_detail` — runtime-not-executed. Single AgentExecution by ID.
- `execution_search` — runtime-not-executed. Recent AgentExecutions by filters.
- `memory_pressure` — runtime-not-executed. Per-worker RSS vs `--max-memory-per-child`.
- `top_consumers` — runtime-not-executed. Per-task_name aggregation over `CeleryTaskEvent`.
- `zombie_thread_rate` — runtime-not-executed. Per-agent per-hour wall-clock-timeout spawns.
- `tenant_boundary_violations` — runtime-not-executed. I-0303 REPORT-ONLY substrate query.
- `staleness_warnings` — runtime-not-executed. S2759 staleness_warning envelope query.
- `recent_bridge_calls` — runtime-not-executed. Recent bridge-call activity (read).
- `bridge_activity_digest` — runtime-not-executed. Aggregated bridge activity summary (read).

## 3. Schema notes

- **Required:** `action` (enum, 20 values).
- **Optional common params:**
  - `window` — enum `1h/6h/24h/7d/30d`; default `24h`. Used by SLO, failure signatures, migration report. Ignored by non-window actions.
  - `since` — ISO-8601 timestamp cutoff; overrides `window`.
  - `limit` — pagination (default varies by action; `recent_recycles` default 10 max 50; `staleness_warnings` default 20 max 100; `top_consumers` default 20 max 50).
  - `include_breakdowns` — for `slo_status`; default `false`.
  - `agent_name` / `task_name` — filters (`zombie_thread_rate`, `celery_task_history`).
  - `execution_id` — required for `execution_detail`.
- **Schema description lint (per S2795 F5):** none flagged for `ops_tool` currently. Description length + actions-mentioned ratio both pass.

## 4. Golden-path examples

**Freshness check at session open (S2796 T1 usage):**

```
ops_tool action=version                    # returns staleness_verdict + head_commit_sha
ops_tool action=recent_recycles limit=5    # returns last 5 recycle events with SHAs
```

**Incident triage (deferred — runtime-not-executed):**

```
ops_tool action=overview window=1h          # one-shot: version + SLOs + failures + noise
ops_tool action=slo_status include_breakdowns=true window=24h
ops_tool action=failure_signatures window=6h
```

**Deploy audit (deferred — runtime-not-executed):**

```
ops_tool action=staleness_warnings verdict=STALE_CELERY limit=20
ops_tool action=tenant_boundary_violations failure_kind=predicate_rejected
```

## 5. Failure / empty-state / pagination notes

- **Fail-soft on missing log files:** `recent_recycles` returns `items: []` + diagnostic note when `logs/recycle_events.jsonl` is absent. Same pattern for `staleness_warnings` (returns `sample_events: []` when no matching OpsRunEvent rows).
- **Empty state:** `slo_status` returns `slo_status: {}` when no telemetry exists in the window. `failure_signatures` returns empty `signatures: []`.
- **Unknown action fallback:** returns `{'error': 'Unknown ops_tool action: <name>'}` per handler entry.
- **Pagination:** `recent_recycles` and `staleness_warnings` accept `limit`. No offset param — reads TAIL of log/queryset.
- **Read vs mutate:** All actions are read-only except `focus_mode_update` (writes Focus Mode config to persistent store). Read/write distinction not surfaced in a category field; caller MUST know from action name.

## 6. Evidence

### 6.1 Observed runs — this ship

**S2796 T1 open freshness check** (dispatched via `bash tools/pa_local.sh` → PA → Rigby `ops_tool` invocation via chat UI):

`ops_tool.version` output (extracted from S2796 T1 PA response):

```json
{
  "staleness_verdict": "FRESH",
  "head_commit_sha": "0c38718b0492",
  "daphne_pid": 69125,
  "daphne_pid_age_seconds": 453,
  "daphne_started_before_head_commit": false,
  "celery_workers": [
    {"hostname": "default@%h", "pid": 69154, "started_before_head_commit": false},
    {"hostname": "pa@%h", "pid": 69163, "started_before_head_commit": false},
    {"hostname": "long_running@%h", "pid": 69174, "started_before_head_commit": false},
    {"hostname": "broadcast@%h", "pid": 69181, "started_before_head_commit": false},
    {"hostname": "code_jobs@%h", "pid": 69208, "started_before_head_commit": false}
  ]
}
```

`ops_tool.recent_recycles limit=5` output (extracted from same S2796 T1 response):

```json
{
  "action": "recent_recycles",
  "log_exists": true,
  "log_path": "logs/recycle_events.jsonl",
  "items": [
    {
      "timestamp": "2026-07-16T02:08:30Z",
      "sha": "0c38718b04920e2dd20b635c921216549069aa7c",
      "sha_short": "0c38718b0492",
      "label": "recycle-all",
      "seconds_ago": 443,
      "partial_recycle": false
    },
    {
      "timestamp": "2026-07-16T02:01:43Z",
      "sha": "5ec09d625e855b31d2bb9c943b44b6c52a92b555",
      "sha_short": "5ec09d625e85",
      "label": "recycle-all",
      "seconds_ago": 850,
      "partial_recycle": false
    }
  ]
}
```

**Both invocations returned in <10ms and match expected response shape.** No error envelopes observed. `staleness_verdict=FRESH` + `head_commit_sha` matches `git rev-parse HEAD` short form — round-trip verified.

### 6.2 Runtime-not-executed — this ship

The 18 remaining actions listed in §2 "Deferred" are admitted as runtime-not-executed for the S2796 doc-only ship. Follow-up PR (planned as next `td_handlers_ops` sub-slice per S2796 Fold 4) will exercise + regression-test them.

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` — origin of the untested-13-in-`td_handlers_ops` finding.
- **S2795 handoff:** `docs/handoffs/SESSION_2795_PA_TOOLS_GAP_MAP.md`.
- **S2796 zoom-out folds:** ledger rows 65-68 (`logs/zoom_out_classifications.jsonl`) — F1 (evidence admission), F2 (template), F3 (5th-tool deferred), F4 (next-slice named).
- **Next `td_handlers_ops` sub-slice candidates** (per S2796 F3 + F4): `autopilot_tool`, `governor_tool`, `infra_health_tool`, `spider_status_tool` (incident-critical); `scheduled_tasks_tool` (Rigby's Z2 utility pick).

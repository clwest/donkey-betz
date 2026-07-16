# `diagnostics_tool` — Validation Report (S2796)

**Tool:** `diagnostics_tool`
**Schema:** `core/services/pa_tool_schemas.py:2365`
**Handler:** `core/services/td_handlers_ops.py:6203` (`_handle_diagnostics`)
**Register site:** `core/services/tool_dispatcher.py:507`
**Session:** S2796 (Slice 1 of `td_handlers_ops` validation)
**HEAD at validation:** `0c38718b0`
**Ship shape:** Doc-only (per S2796 Chris directive "validation quickest"). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (per gap-map classifier)
**Rigby SIGN:** S2796 T1 SIGN-WITH-EDITS; 6-section template per Rigby Z3; evidence per Rigby Z1 edit A.

---

## 1. Purpose / when-to-use

`diagnostics_tool` is per-subsystem audit/inventory telemetry — surfaces per-component invocation counts + inventory state so Rigby can grade whether registered components are actually being used (advisors, LLM providers, beat schedules, workspaces). Read-only, no mutations. Introduced Session 1202 §A.2.

Distinct from `ops_tool` — `ops_tool` is SRE/SLO-focused on production reliability (deploy version, timeout rates, failure signatures); `diagnostics_tool` surfaces "is this registered component alive / being called?" per component class. When asked "are all advisors being used?" → `diagnostics_tool.advisor_invocations`. When asked "how healthy are the beat schedules?" → `diagnostics_tool.beat_schedule_health`.

## Covered actions

All 7 schema-declared actions enumerated as a flat list for gap-map classifier. Per-action admission class inlined per Rigby SIGN Z1 edit A (F1) — 3 of 7 are documented in schema as `[PR-2 placeholder — not yet implemented]`.

- `advisor_invocations` — **in scope this ship** — verified live at S2796 T1 (see §Evidence). Returns per-advisor N-day invocation count from `AgentExecution`; surfaces zero-invocation advisors so dead personas are visible.
- `provider_calls` — runtime-not-executed. Per-LLM-provider call count + success/cost rollup over `window`. Source `LLMCallLog`.
- `beat_schedule_health` — runtime-not-executed. `PeriodicTask` sorted by `last_run_at ASC` (stalest first). **Priority for follow-up PR — this is the "why isn't my beat firing?" answer.**
- `workspace_metrics` — runtime-not-executed. Per-`ProjectWorkspace` last_operation_at + deliverable_count + is_active + allow_autonomous_writes.
- `schema_handler_diff` — runtime-not-executed. **Schema declares `[PR-2 placeholder — not yet implemented]`** per `pa_tool_schemas.py:2397`. Programmatic schema-vs-handler gap detection. Live invocation before PR-2 lands will return not-implemented error.
- `learning_bridge_writes` — runtime-not-executed. **Schema PR-2 placeholder** per `pa_tool_schemas.py:2400`. Per-bridge 30d write counts.
- `discord_health` — runtime-not-executed. **Schema PR-2 placeholder** per `pa_tool_schemas.py:2401`. Bot uptime + 7d invocation counts + error rate.

**DOC-note follow-up:** either implement the 3 PR-2 placeholder actions OR remove them from the schema enum. Deferred to next `td_handlers_ops` sub-slice PR (per S2796 F4).

## 3. Schema notes

- **Required:** `action` (enum, 7 values — including 3 PR-2 placeholders).
- **Optional params:**
  - `window` — enum `1d/7d/14d/30d/90d`; default `7d`. Used by `advisor_invocations`, `provider_calls`.
  - `limit` — integer; default 50, max 200. Pagination for `beat_schedule_health`, `workspace_metrics`.
  - `offset` — integer; default 0. Pagination for same actions.
  - `include_disabled` — boolean; default `true`. For `beat_schedule_health`.
  - `include_inactive` — boolean; default `true`. For `workspace_metrics`.
- **Schema description lint (per S2795 F5):** none flagged. Description length passes; action verbs mentioned in description.

## 4. Golden-path examples

**Advisor liveness audit (S2796 T1 usage):**

```
diagnostics_tool action=advisor_invocations window=7d
# → surfaces zero_invocation_advisors count + full advisor list
```

**Beat schedule health check (deferred — runtime-not-executed):**

```
diagnostics_tool action=beat_schedule_health include_disabled=false limit=25
```

**LLM provider spend rollup (deferred — runtime-not-executed):**

```
diagnostics_tool action=provider_calls window=30d
```

## 5. Failure / empty-state / pagination notes

- **Empty state:** `advisor_invocations` with no invocations in window returns `total_invocations_in_window: 0` + full advisor list with `invocations_in_window: 0` per row (verified live — see §6.1). Zero-invocation advisors surfaced explicitly via `zero_invocation_advisors` count. Fail-loud on inactivity is the intended pattern.
- **Pagination:** `beat_schedule_health` and `workspace_metrics` support `limit`/`offset`. Default 50 rows per page; hard max 200.
- **Placeholder actions:** 3 of 7 enum values are documented placeholders (`schema_handler_diff`, `learning_bridge_writes`, `discord_health`). Live invocation of any of these is expected to return an error envelope. **Not verified this ship — placeholder-error behavior deferred.**
- **Window param ignored by non-window actions:** `beat_schedule_health`, `workspace_metrics`, and the 3 placeholders ignore `window`. Schema description states this.
- **Read-only:** all actions are read-only per schema description ("Read-only — no mutations"). No mutating action surface.

## 6. Evidence

### 6.1 Observed run — this ship

**S2796 T1 evidence-capture dispatch** (`bash tools/pa_local.sh` → Rigby `diagnostics_tool action=advisor_invocations window=7d` invocation):

```json
{
  "gateway": "diagnostics_tool",
  "action": "advisor_invocations",
  "window_days": 7,
  "since": "2026-07-09T02:36:20.948305+00:00",
  "total_advisors": 25,
  "zero_invocation_advisors": 25,
  "total_invocations_in_window": 0,
  "advisors": [
    {"id": "3a681e3b-...", "name": "Bill Gates", "category": "tech", "is_active": true, "last_consultation": null, "invocations_in_window": 0},
    {"id": "20547a68-...", "name": "Cathie Wood", "category": "investment", "is_active": true, "last_consultation": null, "invocations_in_window": 0},
    {"id": "4d04843f-...", "name": "Christine Lagarde", "category": "finance", "is_active": true, "last_consultation": null, "invocations_in_window": 0},
    ... (25 advisors total — Bill Gates through Yuval Noah Harari)
  ]
}
```

**Response returned in 7ms** (from `Tool Runs (verbose)` block). Response fields verified: `gateway`, `action`, `window_days`, `since` (ISO-8601 UTC), `total_advisors=25`, `zero_invocation_advisors=25`, `total_invocations_in_window=0`, and full 25-row `advisors` array. Every advisor row has: `id` (UUID), `name`, `category`, `is_active` (bool), `last_consultation` (null when never consulted), `invocations_in_window`.

**Observed signal:** `total_invocations_in_window=0` over the last 7 days — the advisor surface has been dormant this window. Consistent with the platform's current single-user pre-prod operating context (per project memory `single_user_pre_prod_operating_context`); this is the "fail-loud on inactivity" pattern working correctly, not a defect.

### 6.2 Runtime-not-executed — this ship

- `provider_calls` — not exercised; handler behavior + response shape unverified.
- `beat_schedule_health` — not exercised.
- `workspace_metrics` — not exercised.
- `schema_handler_diff` / `learning_bridge_writes` / `discord_health` — declared as PR-2 placeholders in schema; live error-envelope behavior not verified.

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2796 zoom-out folds:** ledger rows 65-68.
- **Related tools:** `ops_tool` (SRE/SLO-focused counterpart), `agent_introspection_tool` (agent-side inventory).
- **Follow-up debt:** 3 PR-2 placeholder actions — implement or remove.

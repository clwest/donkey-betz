# `gates_tool` — Validation Report (S2905)

**Tool:** `gates_tool`
**Schema:** `core/services/pa_tool_schemas.py:243`
**Handler:** `core/services/td_handlers_agents.py:5059` (`_handle_gates`)
**Register site:** `core/services/tool_dispatcher.py:420`
**Session:** S2905 (Path B systematic sweep — Slice 2 batch 1 of `td_handlers_agents`, first accelerated batch post-substrate arc close)
**HEAD at validation:** `6188e2d10`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised via T1a harness).
**Rigby SIGN:** S2905 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only surface over `PilotReadinessGate` rows — the quality-gate substrate that fronts pilot execution. Answers "what gates exist, what's their status/risk breakdown, what does gate X specifically look like?" Use when the user asks about quality gates, publish gates, or pass/fail history on a pilot decision.

Distinct from `pilots_tool` (which reads `PilotExecution` rows — the outcome side) and from `governance_tool` (which reads governance-scoped policy state, not gate history). `gates_tool` is the read-only inspection surface for gate rows themselves.

## Covered actions

- `list` — **in scope this ship** — verified live via T1a harness (19ms). Returns `{action, count, gates[]}`; each gate carries `id, summary, status, risk_level, created_at, topic`. Summary truncated at 200 chars (S1057). Registry union not applicable; ORM select_related on `decision`.
- `stats` — **in scope this ship** — verified live via T1a harness (14ms). Returns `{action, total, by_status, by_risk_level}` — aggregate counts across all `PilotReadinessGate` rows.
- `detail` — **in scope this ship** — verified via T1a harness error path (6ms, `error_code=TOOL_EXCEPTION`, `msg="id is required for detail action"`). Requires `id` payload; returns `{action, found, gate}` on hit or `{action, found: false, id}` on miss. Not exercised with a real gate id in this sweep — see §5.

## 3. Schema notes

- **Required:** `action` (enum: `list, stats, detail`).
- **Conditional required:** `id` at handler level for `detail` (schema declares as optional string). Recurring S2892/S2893 pattern of handler-required-but-schema-optional args.
- **Optional:** `limit` (default 10, applies to `list` only).
- **Action alias:** handler accepts `details` and rewrites to `detail` (line 5076).

## 4. Golden-path examples

**"What gates exist recently?"**

```
gates_tool  action=list
```

**Aggregate breakdown by status + risk:**

```
gates_tool  action=stats
```

**Full detail on one gate:**

```
gates_tool  action=detail  id=<PilotReadinessGate UUID>
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — `list` returns a single page bounded by `limit` (default 10). No `has_more/offset` cursor; not a S2868 Ledger #1 pagination surface.
- **`detail` without `id` raises ValueError** — surfaced as `TOOL_EXCEPTION` error envelope by the dispatcher (verified via T1a harness). Not a defect; handler is fail-loud on required arg.
- **`detail` miss returns `found: false`** — not exercised live this ship (no gate id sampled), but handler contract at `td_handlers_agents.py:5103` is explicit.
- **Empty-state on `list`** — returns `count: 0, gates: []` when no gates exist. Not exercised live (real gates present).
- **Summary truncation** — S1057 fix caps `summary` at 200 chars + "..." suffix for GPT-5.2 rendering safety. Silent (no `truncated` field).
- **No latency outliers** — 6-19ms observed.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Entire tool is read-only.
- **Containment protocol:** N/A — no state modification possible.
- **Safety metadata:** `gates_tool` seeded in `TOOL_DEFAULTS` at S2905 with `default_safety_class='READ_ONLY'`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`python manage.py pa_tool_validate_harness gates_tool` at HEAD `6188e2d10` (2026-07-23):

- **`list` (19ms):** `response_shape_keys=['action', 'count', 'gates']` — `success`.
- **`stats` (14ms):** `response_shape_keys=['action', 'by_risk_level', 'by_status', 'total']` — `success`.
- **`detail` (6ms):** `error_captured` — `error_code=TOOL_EXCEPTION`, `msg="id is required for detail action"`. Expected: handler is fail-loud on required arg; harness dispatched with only `{action: 'detail'}` per minimal-safe-args v1 profile.

Artifact: `docs/audits/pa_tools/harness_output/gates_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **`detail` with a real gate id** — not exercised. Would confirm the `{found, gate}` positive path.
- **`limit > 10`** — not exercised. Handler passes `limit` straight to `[:limit]` slice — no observed cap.
- **`action='details'` alias** — not exercised. Handler alias at line 5076 rewrites to `detail`.

---

## Related

- **Ledger candidates surfaced this ship** — none unique to this tool. Handler is small (line 5059-5129) and has been in place since S933 audit fix; no new drift observed.
- **Adjacent tools:** `pilots_tool` (this batch — outcome side of pilot lifecycle), `governance_tool` (untested, next slice), `deliberation_tool` (validated).
- **Substrate context:** first opt-in to T1b `Template version: v1` — this doc's shape validates the ratchet-and-warn lint transition from `warn` (advisory) to `pass` in the gap map.
- **Batch peers:** `pilots_tool`, `cost_telemetry_tool`, `revenue_tracker_tool` (Slice 2 batch 1).

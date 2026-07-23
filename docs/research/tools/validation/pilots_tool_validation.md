# `pilots_tool` — Validation Report (S2905)

**Tool:** `pilots_tool`
**Schema:** `core/services/pa_tool_schemas.py:267`
**Handler:** `core/services/td_handlers_agents.py:5131` (`_handle_pilots`)
**Register site:** `core/services/tool_dispatcher.py:421`
**Session:** S2905 (Path B systematic sweep — Slice 2 batch 1 of `td_handlers_agents`, first accelerated batch post-substrate arc close)
**HEAD at validation:** `6188e2d10`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised via T1a harness).
**Rigby SIGN:** S2905 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only surface over `PilotExecution` rows — the outcome side of pilot lifecycle. Answers "which pilots exist, what are their status/outcome breakdowns, what's currently running, what does pilot X specifically look like?" Use when the user asks about experiments, A/B tests, or pilot outcomes.

Distinct from `gates_tool` (this batch — quality-gate substrate that fronts pilots) and from `deliberation_tool` (which reads decision-making state, not pilot outcomes). `pilots_tool` is the read-only inspection surface for pilot rows themselves.

## Covered actions

- `list` — **in scope this ship** — verified live via T1a harness (17ms). Returns `{action, count, pilots[]}`; each pilot carries `id, name, status, outcome, created_at`. Name truncated at 150 chars (S1057). Default `limit=10`.
- `stats` — **in scope this ship** — verified live via T1a harness (14ms). Returns `{action, total, by_status, by_outcome}` — aggregate counts across all `PilotExecution` rows.
- `detail` — **in scope this ship** — verified via T1a harness error path (6ms, `error_code=TOOL_EXCEPTION`, `msg="id is required for detail action"`). Requires `id` payload; returns `{action, found, pilot}` on hit or `{action, found: false, id}` on miss. Not exercised with a real pilot id in this sweep — see §5.

## 3. Schema notes

- **Required:** `action` (enum: `list, stats, detail`).
- **Conditional required:** `id` at handler level for `detail` (schema declares as optional string). Recurring S2892/S2893 pattern of handler-required-but-schema-optional args.
- **Optional:** `limit` (default 10, applies to `list` only).
- **Action alias:** handler accepts `details` and rewrites to `detail` (line 5143).
- **Undeclared handler action `running`:** the handler at line 5181 accepts `action='running'` (returns `PilotExecution.filter(status='running')`) but this value is NOT in the schema `action` enum. Doc-vs-code drift — see §5.

## 4. Golden-path examples

**"What pilots exist recently?"**

```
pilots_tool  action=list
```

**Aggregate breakdown by status + outcome:**

```
pilots_tool  action=stats
```

**Full detail on one pilot:**

```
pilots_tool  action=detail  id=<PilotExecution UUID>
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — `list` returns a single page bounded by `limit` (default 10). No `has_more/offset` cursor.
- **`detail` without `id` raises ValueError** — surfaced as `TOOL_EXCEPTION` error envelope by the dispatcher (verified via T1a harness). Not a defect; handler is fail-loud on required arg.
- **`detail` miss returns `found: false`** — not exercised live this ship (no pilot id sampled).
- **`running` action reachable but undeclared** — handler at line 5181 accepts `action='running'` but schema enum lists only `list, stats, detail`. Rigby's dispatch via schema-typed function call cannot reach this path; only a callsite that bypasses schema validation could. Deferred as a Rigby Tool Gap Ledger candidate — see §Related.
- **Name truncation** — S1057 fix caps `name` at 150 chars + "..." suffix for GPT-5.2 rendering safety. Silent (no `truncated` field).
- **Empty-state on `list`** — returns `count: 0, pilots: []` when no pilots exist. Not exercised live (real pilots present).
- **No latency outliers** — 6-17ms observed.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Entire tool is read-only.
- **Containment protocol:** N/A — no state modification possible.
- **Safety metadata:** `pilots_tool` seeded in `TOOL_DEFAULTS` at S2905 with `default_safety_class='READ_ONLY'`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`python manage.py pa_tool_validate_harness pilots_tool` at HEAD `6188e2d10` (2026-07-23):

- **`list` (17ms):** `response_shape_keys=['action', 'count', 'pilots']` — `success`.
- **`stats` (14ms):** `response_shape_keys=['action', 'by_outcome', 'by_status', 'total']` — `success`.
- **`detail` (6ms):** `error_captured` — `error_code=TOOL_EXCEPTION`, `msg="id is required for detail action"`. Expected: handler is fail-loud on required arg; harness dispatched with only `{action: 'detail'}` per minimal-safe-args v1 profile.

Artifact: `docs/audits/pa_tools/harness_output/pilots_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **`detail` with a real pilot id** — not exercised. Would confirm the `{found, pilot}` positive path.
- **`running` schema-hidden action** — not exercised. Only reachable by callsite that bypasses schema validation.
- **`action='details'` alias** — not exercised. Handler alias at line 5143 rewrites to `detail`.

---

## Related

- **Ledger candidate surfaced this ship:** handler accepts undeclared `action='running'` but schema enum omits it. Two remediation options — (a) drop the `running` branch from the handler if unused, (b) add `running` to the schema enum. Deferred pending Rigby SIGN; note that Rigby cannot reach the branch today via function-call dispatch, so operator impact is zero at HEAD.
- **Adjacent tools:** `gates_tool` (this batch — quality-gate side of pilot lifecycle), `deliberation_tool` (validated), `governance_tool` (untested, next slice).
- **Substrate context:** first opt-in to T1b `Template version: v1` — this doc's shape validates the ratchet-and-warn lint transition from `warn` (advisory) to `pass` in the gap map.
- **Batch peers:** `gates_tool`, `cost_telemetry_tool`, `revenue_tracker_tool` (Slice 2 batch 1).

# `revenue_tracker_tool` — Validation Report (S2905)

**Tool:** `revenue_tracker_tool`
**Schema:** `core/services/pa_tool_schemas.py:188`
**Handler:** `core/services/td_handlers_agents.py:1605` (`_handle_revenue_tracker`)
**Register site:** `core/services/tool_dispatcher.py:397`
**Session:** S2905 (Path B systematic sweep — Slice 2 batch 1 of `td_handlers_agents`, first accelerated batch post-substrate arc close)
**HEAD at validation:** `6188e2d10`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (2 of 3 actions exercised live via T1a harness; `create` is MUTATION — deferred per T1a MVP scope).
**Rigby SIGN:** S2905 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read + write surface over `core.models.Revenue` rows — the platform revenue ledger. Answers "what's total revenue, how does it break down by source/status, what are recent revenue events?" (read side) and "record a new revenue event" (write side). Use when the user asks about earnings, income progress, financial totals, or wants to log a real revenue event.

Distinct from `cost_telemetry_tool` (this batch — spend side of P&L) and from `check_resource_budget` (planned-operation gate, not historical revenue). `revenue_tracker_tool` is the ONE mixed-safety tool in this batch — the metadata pattern used here is the per-action `TOOL_ACTION_METADATA` map, not the tool-level `TOOL_DEFAULTS` used by the other three peers.

## Covered actions

- `stats` — **in scope this ship** — verified live via T1a harness (24ms). Returns `{action, total_revenue, revenue_last_30_days, by_source, by_status, record_count}`. All monetary values serialized as strings (Decimal safe). `by_source` returns dict of `{source_type: total_str}`; `by_status` returns dict of `{status: count}`.
- `list` — **in scope this ship** — verified live via T1a harness (11ms). Returns `{action, count, revenues[]}`; each revenue row carries `id, amount, source_type, status, created_at, description`. Default `limit=20`.
- `create` — **mutation — deferred to Slice 1.5b-style mutation session** — see §5a. Handler at line 1676 writes a new `Revenue` row via `Revenue.objects.create(...)`. Requires `user_id` context (raises `ValueError` when absent). Validated by T1a harness as `skipped_mutation` outcome per T1a §3 MVP scope.

## 3. Schema notes

- **Required:** `action` (enum: `stats, list, create`).
- **Conditional required:** `amount` at handler level for `create` (Decimal-parsed, must be positive; raises `ValueError` on invalid or non-positive input). Schema declares as optional number.
- **Optional:** `source` (enum: `quick_apply, freelance, consulting, ai_project, content, trading, sports_betting, affiliate, other`; default `other`), `description` (string), `status` (enum: `potential, pending, received, cancelled`; default `confirmed` at handler line 1690 — DIVERGES from schema enum which lists `received` not `confirmed`), `limit` (default 20, applies to `list`).
- **`status` default divergence** — schema enum: `[potential, pending, received, cancelled]`; handler default: `'confirmed'`. `'confirmed'` is not in the schema enum. Doc-vs-code drift — see §5.

## 4. Golden-path examples

**"What's our total revenue?"**

```
revenue_tracker_tool  action=stats
```

**"Show me the last 50 revenue events":**

```
revenue_tracker_tool  action=list  limit=50
```

**"Record a $500 consulting revenue" (write — requires user context):**

```
revenue_tracker_tool  action=create  amount=500  source=consulting  description="Client X retainer"
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — `list` returns a single page bounded by `limit` (default 20). No `has_more/offset` cursor.
- **`create` requires user_id** — raises `ValueError("User context required to create revenue record")` when dispatched without a user context. Not exercised live in this sweep — MUTATION action skipped per T1a MVP.
- **`create` amount validation** — Decimal-parsed via `Decimal(str(payload.get('amount', 0)))`. Non-numeric raises `InvalidOperation → ValueError`. `amount <= 0` raises `ValueError`. Handler line 1680-1686.
- **`status` default drift** — handler default `'confirmed'` is not in the schema enum. If a caller omits `status` on `create`, the resulting `Revenue` row is written with a status value that doesn't match the schema-declared set. Ledger candidate — see §Related.
- **Empty-state on `stats`** — returns `total_revenue: "0", by_source: {}, by_status: {}, record_count: 0` when no rows exist. Not exercised (real revenue rows present).
- **Empty-state on `list`** — returns `count: 0, revenues: []`. Not exercised.
- **`stats` uses `str()` on Decimal totals** — safe for GPT-5.2 rendering + JSON serialization. Callers who need arithmetic must parse back to Decimal.
- **No latency outliers** — 11-24ms observed on read actions.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating action:** `create` — writes a new `Revenue` row (blast-radius: single row per invocation, no cascade). Classified `MUTATION` in `TOOL_ACTION_METADATA` at S2905.
- **Containment protocol:** T1a MVP skips MUTATION dispatch. `create` will be swept in a future mutation-slot session (analogous to Slice 1.5b for `autopilot_tool` mutations).
- **Safety metadata:** per-action records in `TOOL_ACTION_METADATA` (not `TOOL_DEFAULTS`) because the tool is mixed-safety. `stats` + `list` = READ_ONLY; `create` = MUTATION.
- **Pre-mutation-sweep prerequisites:** (1) synthetic user context for the user_id validation, (2) `dry_run` flag consideration (no such flag today — full write is the only path), (3) blast-radius bound is one row per dispatch (acceptable canary shape).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`python manage.py pa_tool_validate_harness revenue_tracker_tool` at HEAD `6188e2d10` (2026-07-23):

- **`stats` (24ms):** `response_shape_keys=['action', 'by_source', 'by_status', 'record_count', 'revenue_last_30_days', 'total_revenue']` — `success`. `resolution_source='action'` (per-action metadata precedence over any tool-default).
- **`list` (11ms):** `response_shape_keys=['action', 'count', 'revenues']` — `success`. `resolution_source='action'`.
- **`create`:** `skipped_mutation` — `notes="MUTATION — not exercised at T1a MVP"`. Not dispatched; safety class enforced pre-dispatch.

Artifact: `docs/audits/pa_tools/harness_output/revenue_tracker_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **`create` with user context** — deferred to mutation-slot session per T1a MVP.
- **`create` validation error paths** — negative amount + non-numeric amount + missing user_id all raise `ValueError` per handler contract. Not exercised.
- **`status='confirmed'` default drift** — not exercised. Would write a Revenue row with a status value not in the schema enum.
- **`stats` empty-state** — not exercised (real rows present).

---

## Related

- **Ledger candidates surfaced this ship:**
  1. `status` default divergence — handler default `'confirmed'` is not in schema enum `[potential, pending, received, cancelled]`. Two remediation options: (a) update handler default to `'potential'` or `'pending'` (schema-conformant), (b) extend schema enum to include `'confirmed'`. Deferred pending Rigby SIGN.
- **Adjacent tools:** `cost_telemetry_tool` (this batch — spend side), `check_resource_budget` (planning gate), `revenue_dashboard_tool` (untested — different tool).
- **Substrate context:** first opt-in to T1b `Template version: v1` — this doc's shape validates the ratchet-and-warn lint transition from `warn` (advisory) to `pass` in the gap map. This is also the FIRST post-substrate doc using per-action `TOOL_ACTION_METADATA` (as opposed to tool-level `TOOL_DEFAULTS`) for a mixed-safety tool — validates the metadata pattern's ergonomics.
- **Batch peers:** `gates_tool`, `pilots_tool`, `cost_telemetry_tool` (Slice 2 batch 1).

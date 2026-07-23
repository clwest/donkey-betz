# `task_manager_tool` — Validation Report (S2911)

**Tool:** `task_manager_tool`
**Schema:** `core/services/pa_tool_schemas.py:138`
**Handler:** `core/services/td_handlers_agents.py:1384` (`_handle_task_manager`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2911 (Path B systematic sweep — Slice 2 batch 6a of `td_handlers_agents`)
**HEAD at validation:** `5d79d8431` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 3 MUTATION + 1 IRREVERSIBLE actions explicitly excluded — see §5a).
**Rigby SIGN:** S2911 T0 SIGN AGREE-with-edits (batch 6a shape ratified; Q4 zoom-out surfaced HIDDEN MUTATION on `task_manager.create` — documented in §5a below). S2911 T1 SIGN AGREE-with-edits (Q1 verified HIDDEN MUTATION metadata note against handler lines 1444-1464; Q4a same-PR mitigation applied: schema description at `pa_tool_schemas.py:139-147` now warns planner about implicit-Opportunity creation when `opportunity_id` is omitted).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Manage the task/to-do items that live under an opportunity — list, view stats, and (via excluded write actions) create/update/complete/delete tasks. Answers "what's on my to-do list?", "what's my task status/priority breakdown?", and drives the "mark task done" flow (via excluded `complete` action → status='won' domain semantics).

Distinct from `opportunity_manager_tool` (parent Opportunity rows) — every `OpportunityTask` has a required FK to an `Opportunity`. When `task_manager.create` is invoked without `opportunity_id`, the handler implicitly creates a standalone Opportunity to satisfy the FK constraint (see §5a HIDDEN MUTATION note). Distinct from `execution_history_tool` (which surfaces `AgentExecution` rows) — this tool is user-facing action items, not agent-execution traces.

## Covered actions

**READ_ONLY actions covered only (2 of 6 total actions).** 3 MUTATION + 1 IRREVERSIBLE actions (excluded — see §5a Mutation containment for named actions, deferral rationale, HIDDEN MUTATION on `create`, and planned coverage slice) are out of scope for this ship.

- `list` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 19 ms). Returns `{action, count, tasks}` — user-scoped `OpportunityTask` rows with optional `status` + `priority` filters.
- `stats` — **in scope this ship** — verified live via T1a harness (`success`, 13 ms). Returns `{action, total, by_status, by_priority}` — aggregate over user-scoped tasks.
- `create` — **mutation — deferred (HIDDEN MUTATION: implicitly creates parent Opportunity)** — see §5a
- `update` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `complete` — **mutation — deferred (domain semantics: status='won')** — see §5a
- `delete` — **irreversible — deferred** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `list, stats, create, update, complete, delete`).
- **Conditional required (handler-enforced, per action):**
  - `id` for `update` / `complete` / `delete` — fail-loud via `ValueError`.
  - `title` (non-empty after strip) for `create` — fail-loud via `ValueError`.
  - `user_id` context for `create` — fail-loud via `ValueError`.
- **Optional:** `status` (filter for `list`; new status for `update`), `priority` (filter for `list`; new priority for `update`), `limit` (default 20 for `list`), `title` / `description` / `priority` / `opportunity_id` (all `create` params).
- **Status enum (`update` + `complete` domain values):** `pending, accepted, in_progress, applied, waiting, won (=completed), lost, expired, cancelled`. `complete` action hard-sets status to `'won'` regardless of prior value.
- **Session 1228 PR-A key-in-payload guard** (handler line 1506): `update` uses `payload.get('description')` truthy-guard so an LLM autofill of `''` doesn't silently clear an existing description. Empty-clear requires explicit UX.

## 4. Golden-path examples

**"What's on my to-do list?"**

```
task_manager_tool  action=list
```

**"Show high-priority open tasks:"**

```
task_manager_tool  action=list  status=pending  priority=high
```

**"What's my task status breakdown?"**

```
task_manager_tool  action=stats
```

## 5. Failure / empty-state / pagination notes

- **`list` empty result** — returns `{action: 'list', count: 0, tasks: []}`. Consistent shape.
- **`stats` with zero tasks** — returns `{action: 'stats', total: 0, by_status: {}, by_priority: {}}`. Consistent shape.
- **`list` / `stats` with anonymous caller (no user_id)** — base queryset returns all rows unfiltered (no user scoping applied). Documented handler behavior — callers should not rely on user-scope filtering when the harness runs anonymously.
- **`list` pagination** — `limit` param (default 20); no offset/cursor. `count` field on response echoes returned row count. No `has_more` flag.
- **`update` with unknown task id** — raises `ValueError(f'Task {task_id} not found')` → `TOOL_EXCEPTION`. Excluded this ship.
- **`delete` with unknown task id** — returns inline `{action: 'delete', success: False, error: 'Task {id} not found'}` (does NOT raise). Envelope-shape mismatch with the raise-based error path on other actions. Excluded this ship — potential Ledger candidate on future MUTATION-coverage exercise.
- **Unknown action** — raises `ValueError('Unknown action: {action}. Valid: list, stats, create, update, complete, delete')` at handler line 1556 → `TOOL_EXCEPTION`.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating actions excluded this ship:**
  - `create` — creates an `OpportunityTask` row (handler line 1466) with FK to an `Opportunity`. **HIDDEN MUTATION**: when payload lacks `opportunity_id`, the handler implicitly creates a standalone `Opportunity` (handler lines 1452-1464) with `opportunity_type='task'`, `source='pa'`, `potential_revenue=0`, `status='active'` — solely to satisfy the FK constraint. Callers get back only `opportunity_id` (silent creation, no explicit flag). Classified `MUTATION`.
  - `update` — writes `OpportunityTask` fields (`status | priority | title | description`) via `save(update_fields=...)`. Session 1228 PR-A key-in-payload guard prevents autofill-clear. Classified `MUTATION`.
  - `complete` — hard-sets `OpportunityTask.status='won'` regardless of prior value (domain-specific "task done" semantics). Classified `MUTATION`.
  - `delete` — destroys `OpportunityTask` row via `task.delete()`. No cascade (task is a leaf). Classified `IRREVERSIBLE` (no confirm flag, no soft-delete, aligned with `media_tool.delete` + `opportunity_manager.delete` precedents).
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` / `'IRREVERSIBLE'`; harness skips via `resolve_safety()` (`expected_outcome=skipped_mutation` / `skipped_irreversible` — verified in artifact §6.1).
- **dependency_surface note:** `internal` — Django ORM against `OpportunityTask` + implicit `Opportunity` creation on `create`. No external bridge.
- **Deferral rationale:** all 4 write actions require live user/session context. `create`'s HIDDEN MUTATION on the parent Opportunity is a real hazard for automated testing — a doc-only sweep run against a real user could silently accrete parent-Opportunity rows without operator awareness. Deferred to a future MUTATION-coverage batch pairing with explicit `dry_run` semantics or seeded-parent-Opportunity harness pattern.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness task_manager_tool` at HEAD `5d79d8431` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list` | `success` | 200 | 19 ms | `action, count, tasks` |
| `stats` | `success` | 200 | 13 ms | `action, by_priority, by_status, total` |
| `create` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `update` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `complete` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `delete` | `skipped_irreversible` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/task_manager_tool.json`.

**Envelope-shape observation:** both dispatched READ_ONLY actions return `{action, ...}` prefix consistently. No `bridge` field — pure ORM, no S2909 T2 bridge preflight needed.

### 6.2 Runtime-not-executed — this ship

- **`list` with populated `status` / `priority` filters** — not exercised against a real task corpus (would confirm filter propagation + row-shape stability).
- **`stats` with populated tasks** — not exercised (would confirm `by_status` / `by_priority` count semantics).
- **All 4 write actions** — MUTATION/IRREVERSIBLE-skipped (see §5a).
- **`delete` inline-`{ok: false}` envelope drift on unknown-id path** — not exercised (Ledger candidate — envelope-shape inconsistency vs raise-based error paths on other actions).

---

## Related

- **Ledger candidates surfaced this ship:**
  - **Envelope-shape inconsistency on `delete` unknown-id path**: `delete` returns inline `{action, success: False, error}` while all other error paths raise `ValueError` → `TOOL_EXCEPTION`. Same class as S2907's `orm_inspect_tool` FT-5 candidate. Not urgent (delete is IRREVERSIBLE-skipped), but should be tracked for future MUTATION-coverage batch.
  - **HIDDEN MUTATION on `create` when `opportunity_id` absent**: silent implicit-Opportunity creation is a real hazard for automated dry_run testing. Documented in §5a; may warrant explicit callout in the tool schema description.
- **Adjacent tools:**
  - `opportunity_manager_tool` — parent Opportunity rows; same-batch peer this ship. `task.opportunity_id` FK enforcement is the source of the HIDDEN MUTATION concern above.
  - `initiatives_tool` — initiative-stage workflow (distinct pipeline from opportunity/task workflow).
  - `execution_history_tool` — agent-execution trace rows (not user-facing task items).
- **Substrate context:** second tool in Slice 2 batch 6a. Peers: `opportunity_manager_tool` (parent Opportunity model, same batch), `pipeline_orchestrator_tool` (single R action), `video_history_tool` (async Celery MUTATION).
- **Metadata seed:** 6 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (Pattern C — per-action records; no `TOOL_DEFAULTS` entry).

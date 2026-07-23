# `opportunity_manager_tool` — Validation Report (S2911)

**Tool:** `opportunity_manager_tool`
**Schema:** `core/services/pa_tool_schemas.py:91`
**Handler:** `core/services/td_handlers_agents.py:1178` (`_handle_opportunity_manager`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2911 (Path B systematic sweep — Slice 2 batch 6a of `td_handlers_agents`, first mixed-safety scoped-to-READ_ONLY-subset ship of the remaining Slice 2 tools)
**HEAD at validation:** `5d79d8431` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 2 MUTATION + 1 IRREVERSIBLE actions explicitly excluded — see §5a).
**Rigby SIGN:** S2911 T0 SIGN AGREE-with-edits (batch 6a composition + scoped-to-READ_ONLY subset shape ratified; Q4 zoom-out surfaced 4 tracked concerns — see §Related). S2911 T1 SIGN AGREE-with-edits (all Q1-Q3 substantive with 8+ handler/doc tool_runs cross-checks; **Q3 additional catch**: `opportunity_manager.delete` has same inline `{success: False}` envelope drift on unknown-id path at handler line 1366 — documented in §Related Ledger candidates. Q4 same-PR mitigations: task_manager schema description warning applied; reasoning_engine drift deferred to separate pre-req PR before batch 6b opens per Rigby preserve-ratified-batch-boundary directive).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Manage the user's opportunity pipeline — list, inspect, and (via excluded write actions) create/update/delete opportunities. Answers "what opportunities are in my pipeline?", "what's the aggregate value + status breakdown?", and "show me this one opportunity by id".

Distinct from `task_manager_tool` (which surfaces action items linked to opportunities via FK) and `autopilot_tool` (which surfaces the platform-wide revenue pipeline including spider-ingested unattributed leads). `opportunity_manager_tool` is user-scoped by default via the `scope` param — the ~2,600-row platform-wide lead pool is accessible only via `scope='all'` explicit opt-in (Session 1222 P4, audit C1).

## Covered actions

**READ_ONLY actions covered only (3 of 6 total actions).** 2 MUTATION + 1 IRREVERSIBLE actions (excluded — see §5a Mutation containment for named actions, deferral rationale, and planned coverage slice) are out of scope for this ship.

- `list` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 26 ms). Returns `{action, count, opportunities}` — paginated list of user-scoped Opportunity rows filtered by optional `status`.
- `get` — **in scope this ship** — verified live via T1a harness error path (`expected_outcome=error_captured`, requires `opportunity_id | id`). Raises `ValueError('opportunity_id is required for get action')` at handler line 1237.
- `stats` — **in scope this ship** — verified live via T1a harness (`success`, 20 ms). Returns `{action, scope, scope_note, total, by_status, by_type, total_potential_revenue}` — aggregate over user-scoped opportunities (adds `owner_breakdown` when `scope='all'`).
- `update_status` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `create` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `delete` — **irreversible — deferred (CASCADE-deletes linked tasks)** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `list, get, stats, update_status, create, delete`).
- **Conditional required (handler-enforced, per action):**
  - `opportunity_id` (or `id` alias) for `get` / `update_status` / `delete` — fail-loud via `ValueError`.
  - `title` (non-empty after strip) for `create` — fail-loud via `ValueError`.
  - `user_id` context for `create` — fail-loud via `ValueError`.
  - `status` (in `active|pending|applied|accepted|rejected|expired`) for `update_status` — fail-loud via `ValueError`.
- **Scope param (`list` / `stats` only):** `scope='mine'` (default) filters by caller `user_id`; `scope='all'` opts into the platform-wide pool (Session 1222 P4 — surfaces spider-ingested unattributed leads owned by the system user). Invalid values coerce to `'mine'`.
- **Optional:** `status` (filter for `list`), `limit` (default 20 for `list`), `title` / `description` / `opportunity_type` / `source` / `potential_revenue` (all `create` params).

## 4. Golden-path examples

**"What opportunities are in my pipeline?"**

```
opportunity_manager_tool  action=list
```

**"Show me my pipeline stats (default: caller-scoped 'mine'):"**

```
opportunity_manager_tool  action=stats
```

**"How many opportunities has the platform ingested overall?"**

```
opportunity_manager_tool  action=stats  scope=all
```

Response includes `owner_breakdown` — top 10 owners (username → count) so the ~2,600-row spike is immediately interpretable as system-pool vs human-owned attribution.

**"Get details of one opportunity by id:"**

```
opportunity_manager_tool  action=get  opportunity_id=<uuid>
```

## 5. Failure / empty-state / pagination notes

- **`list` empty result** — returns `{action: 'list', count: 0, opportunities: []}`. Consistent shape.
- **`stats` with zero opportunities** — returns `{action: 'stats', scope, scope_note, total: 0, by_status: {}, by_type: {}, total_potential_revenue: '0'}`. Consistent shape; `owner_breakdown` present when `scope='all'`.
- **`get` missing `opportunity_id`** — raises `ValueError` → dispatcher wraps as `TOOL_EXCEPTION` at HTTP 500. Fail-loud, not silent. Same envelope shape as `brainstorm_tool` (S2910 clean-exception-path baseline).
- **`get` UUID not found** — raises `ValueError(f'Opportunity {opp_id} not found')` → `TOOL_EXCEPTION`. No inline `{ok: false}` envelope.
- **`list` pagination** — `limit` param (default 20); no offset/cursor. `count` field on response echoes returned row count. Response is bounded — no `has_more` flag. For > 20 rows callers need to raise `limit`.
- **Unknown action** — raises `ValueError('Unknown action: {action}. Valid actions: list, get, stats, update_status, create, delete')` at handler line 1381 → `TOOL_EXCEPTION`.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating actions excluded this ship:**
  - `update_status` — writes `Opportunity.status` field via `save(update_fields=['status'])` at handler line 1316. Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship.
  - `create` — creates a new `Opportunity` row via `Opportunity.objects.create(...)` at handler line 1341. Requires `user_id` context. Classified `MUTATION`.
  - `delete` — **CASCADE-deletes linked `OpportunityTask` rows** at handler line 1371 (`opp.delete()` triggers Django's FK cascade). Counts linked tasks pre-delete so response reports `tasks_deleted`. Classified `IRREVERSIBLE` (aligned with `media_tool.delete` precedent from S2908; no confirm flag, no soft-delete).
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` / `'IRREVERSIBLE'` at `tool_action_metadata.py`; harness resolves via `resolve_safety()` and skips at dispatch (`expected_outcome=skipped_mutation` / `skipped_irreversible` — verified in artifact §6.1).
- **dependency_surface note:** `internal` — Django ORM against `Opportunity` + cascade to `OpportunityTask`. No external bridge.
- **Deferral rationale:** all 3 write actions require live user/session context + tolerance for real ORM writes. `delete` in particular has blast radius (cascade). Doc-only sweep cannot exercise them safely. Deferred to a future MUTATION-coverage batch that pairs with a `dry_run` / seeded-opportunity harness pattern — Rigby T1 SIGN can pressure-test whether MUTATION-coverage needs a dedicated sub-arc.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness opportunity_manager_tool` at HEAD `5d79d8431` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list` | `success` | 200 | 26 ms | `action, count, opportunities` |
| `get` | `error_captured` | 500 | 7 ms | — (`error_code=TOOL_EXCEPTION; msg=opportunity_id is required for get action`) |
| `stats` | `success` | 200 | 20 ms | `action, by_status, by_type, scope, scope_note, total, total_potential_revenue` |
| `update_status` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `create` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `delete` | `skipped_irreversible` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/opportunity_manager_tool.json`.

**Envelope-shape observation:** `get` required-arg miss raises `ValueError` → dispatcher wraps at `TOOL_EXCEPTION` (HTTP 500) → `error_captured`. Behaviorally clean fail-loud, same shape as `brainstorm_tool` (S2910). NOT the inline `{ok: false}` envelope pattern that produced the S2907 `orm_inspect_tool` residual `soft_error` cases (FT-5 substrate candidate). No `bridge` field on the metadata — pure ORM, no bridge preflight needed.

### 6.2 Runtime-not-executed — this ship

- **`list` with populated `status` filter** — not exercised against a populated pipeline (would confirm filter propagation + row shape).
- **`stats` with `scope='all'` + populated pool** — not exercised (would confirm `owner_breakdown` shape + attribution semantics for the platform-wide lead pool).
- **`get` with a real opportunity UUID** — not exercised (would confirm full-detail response shape).
- **All 3 write actions (`update_status` / `create` / `delete`)** — MUTATION/IRREVERSIBLE-skipped (see §5a).

---

## Related

- **Ledger candidates surfaced this ship:**
  - **Envelope-shape inconsistency on `delete` unknown-id path**: `delete` returns inline `{action, success: False, error}` at handler line 1366 (not raise). Same envelope-drift class as `task_manager_tool.delete` (this batch) + S2907 `orm_inspect_tool` FT-5 candidate. Not urgent (delete is IRREVERSIBLE-skipped this ship), but should be tracked for future MUTATION-coverage batch. Surfaced by Rigby T1 SIGN Q3 additional catch.
- **Adjacent tools:**
  - `task_manager_tool` — action items linked to opportunities via FK; same-batch peer this ship.
  - `autopilot_tool` — platform-wide revenue pipeline (spider-ingested pool total surface).
  - `revenue_tracker_tool` — realized revenue records (mixed READ_ONLY + MUTATION, `create` covered S2905).
- **Substrate context:** first tool in Slice 2 batch 6a. Peers: `task_manager_tool` (mixed R/M/IRREVERSIBLE), `pipeline_orchestrator_tool` (single R action), `video_history_tool` (mixed R/M w/ async Celery MUTATION). All 4 tools pure ORM — no bridge dependencies (S2909 T2 preflight not exercised).
- **Metadata seed:** 6 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (Pattern C — no `TOOL_DEFAULTS` entry; per-action records are the safety source, mirroring `brainstorm_tool` / `session_tool` / `revenue_tracker_tool` precedent). Batch-uniform per-action pattern chosen over mixed-pattern to avoid incrementing the S2905 metadata-pattern-selection lint counter.
- **Scope semantics (Session 1222 P4, audit C1):** `scope='mine'` default vs `scope='all'` opt-in for the platform-wide pool. Response `scope` + `scope_note` fields document which view is returned. `owner_breakdown` (scope='all' only) surfaces the top-10 owner attribution so the ~2,600-row spike is interpretable.

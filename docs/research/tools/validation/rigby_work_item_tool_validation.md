# `rigby_work_item` — Validation Report (S2939)

**Tool:** `rigby_work_item`
**Schema:** `core/services/pa_tool_schemas.py:5693` (5-action enum + optional filter/transition params)
**Handler:** `core/services/td_handlers_rigby_work_queue.py:141` (`_handle_rigby_work_item`; per-action helpers `_rigby_work_item_list` :174 / `_acknowledge` :239 / `_resolve` :314 / `_ignore` :401 / `_delegate` :481)
**Register site:** `core/services/tool_dispatcher.py:556`
**Session:** S2939 (Slice 7 Batch 2a — trio with `mission_verdict` + `newsletter_tool`)
**HEAD at validation:** `acca1f4e2` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per Chris D-verdict guardrail): §6 LIVE-VERIFIES the `disabled_response` shape (flag defaults OFF); §5a covers 4 mutation actions ANALYZED-NOT-EXECUTED with signal-chain evidence. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38) AND flag flip (`RIGBY_WORK_QUEUE_REVIEW_ENABLED=True`).
**Category upgrade target:** `untested` → `validated_partial` (disabled-path live-verified; mutation actions analyzed-only)
**Rigby SIGN:** S2939 T0 SIGN AGREE Q2 (auto-flag rendering from Ledger #5 lint — no manual re-scan). Chris D-verdict at T0 RATIFIED with two guardrails baked in.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`rigby_work_item` is Rigby's **internal operational work queue** interface — read `RigbyWorkItem` rows (produced by `RigbyEventIntake`) and transition them through the `open → acknowledged → resolved | ignored` state machine, optionally delegating actionable items to agents via `RigbyMissionDelegation`. Every state transition writes an `OpsRunEvent` row on the parent `MissionRun` (Option A design from S1250 PR 7 — single authoritative audit trail, no separate transition table). Use it when Rigby needs to catch up on her queue ("what work items are open?"), respond to intake events ("acknowledge and resolve item X with outcome=acted"), close out no-action items ("ignore item Y — false positive"), or hand actionable monitoring items off to agents ("delegate item Z to TrendAnalysisAgent").

Distinct from `human_attention_bridge` (HAI items are for Chris to see; RigbyWorkItems are for Rigby to process); from `initiative_tool` (initiatives are project-scoped; work items are event-scoped); from `mission_verdict` (that certifies a mission's evidence; this tool processes intake-event work). This is the **operational queue** for Rigby-as-employee — bounded scope, no human notification surface, no direct agent dispatch except via the explicit `delegate` action.

## Covered actions

Enumerating every action in the schema `action` enum. **1 read action + 4 mutation actions declared in schema.** Flag-gated — with `RIGBY_WORK_QUEUE_REVIEW_ENABLED=False` (default), ALL actions short-circuit to `_disabled_response`. Live-verified this ship: **`disabled_response` shape only** (flag OFF is the default runtime state).

- `list` — **READ (flag-OFF returns disabled_response — verified live at S2939 §6.1).** Paginated read with filters (status, decision, priority_min, since, limit≤100, offset). Envelope when flag ON: `{ok, action, gateway, rows[], total, limit, offset, applied_filters}`.
- `acknowledge` — **MUTATION `spreading` — ANALYZED-NOT-EXECUTED — flag OFF gates dispatch.** See §5a. Transition `open|acknowledged → acknowledged` (idempotent on already-acknowledged). Writes 1 OpsRunEvent + 1 RigbyWorkItem row update.
- `resolve` — **MUTATION `spreading` — ANALYZED-NOT-EXECUTED — flag OFF gates dispatch.** See §5a. Transition to `resolved`. Requires `outcome ∈ {acted, delegated_externally, no_action_needed}`. Writes 1 OpsRunEvent (event_type=`step_pass`) + 1 RigbyWorkItem row update (status + resolved_at).
- `ignore` — **MUTATION `spreading` — ANALYZED-NOT-EXECUTED — flag OFF gates dispatch.** See §5a. Transition to `ignored`. Requires non-empty `reason`. Writes 1 OpsRunEvent + 1 RigbyWorkItem row update.
- `delegate` — **MUTATION `external` — ANALYZED-NOT-EXECUTED — DOUBLE-flag-gated (`RIGBY_WORK_QUEUE_REVIEW_ENABLED` AND `RIGBY_DELEGATION_ENABLED`).** See §5a. Dispatches via `core.services.rigby_mission_delegation.delegate_work_item(work_item_id)`. Async Celery dispatch to `execute_agent_task.apply_async` on the `long_running` queue; v0 routing table maps decision `monitor → TrendAnalysisAgent` (line 47-49 of `rigby_mission_delegation.py`); `notify` decisions are not delegatable. Re-delegation rejected while a non-terminal `AgentExecution` exists for the item.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_rigby_work_queue.py:144`). Defaults to `list` per `(payload or {}).get("action", "list")`.
- **invalid action** — verified via handler code inspection (`td_handlers_rigby_work_queue.py:160-168`). Returns `{ok: False, action, gateway: "rigby_work_item", error: "Unknown action <x>. Supported: list / acknowledge / resolve / ignore / delegate."}`. Non-raising in-envelope error. Same divergence class as recent_activity + rigby_shift_brief + mission_verdict (in-envelope) — differs from execution_history_tool (`raise ValueError`) and newsletter_tool (`_handler_error` helper). Ledger #5 consistency lint candidate — reaches **fourth-instance corroboration** at S2939.

## 3. Schema notes

- **Required:** `action` (enum: `list` | `acknowledge` | `resolve` | `ignore` | `delegate`).
- **Optional (list filters):** `status` (open | acknowledged | resolved | ignored), `decision` (monitor | notify), `priority_min` (int > 0), `since` (ISO datetime string), `limit` (int, default 25, capped at 100), `offset` (int, default 0).
- **Optional (transition inputs):** `work_item_id` / `id` alias (UUID — required for acknowledge/resolve/ignore/delegate; handler resolves via `p.get("work_item_id") or p.get("id")` at lines 243, 318, 405, 494); `note` (string, optional for acknowledge/resolve); `outcome` (required for resolve — enum: acted | delegated_externally | no_action_needed); `reason` (required for ignore — non-empty string).
- **`work_item_id`/`id` alias:** handler accepts either; schema declares both but does not signal aliasing to the LLM caller. Same pattern as `newsletter_tool` `id`/`deliverable_id`.
- **`limit` cap:** `max(1, min(limit, 100))` at line 206 — hard cap 100. Schema description mentions the cap.
- **`priority_min` type guard:** only filters if `isinstance(priority_min, int) and priority_min > 0` (line 188) — non-int and 0-or-negative silently ignored.
- **`since` type flexibility:** accepts string (parsed via `parse_datetime`) OR datetime object OR None (line 191-198). Unparseable strings silently ignored (no error, filter not applied).
- **Flag gate:** `RIGBY_WORK_QUEUE_REVIEW_ENABLED` (Django settings; default `False`). When OFF, ALL 5 actions short-circuit to `_disabled_response(action)` at handler line 146-147.
- **Secondary flag gate (delegate only):** `RIGBY_DELEGATION_ENABLED` (default `False`) — enforced inside `delegate_work_item` service at `rigby_mission_delegation.py`. Even if `RIGBY_WORK_QUEUE_REVIEW_ENABLED=True`, delegate action returns "delegation disabled" when this secondary flag is OFF.
- **No auth gate:** unlike `mission_verdict`, no `_verify_rigby_caller` check. The flag-gate acts as the safety guardrail. Callers implicitly bounded by PA tool-surface exposure (Rigby-only in practice via GPT-5.2 function-calling on PA chat path).
- **No `dry_run` affordance:** every non-empty valid mutation dispatch writes. Ledger #38 substrate blocker.

## 4. Golden-path examples

**Example 1 — List open items (flag ON hypothetical):**
```json
{"action": "list", "status": "open", "priority_min": 5, "limit": 10}
```
→ Would return `{"ok": true, "action": "list", "gateway": "rigby_work_item", "rows": [...], "total": N, "limit": 10, "offset": 0, "applied_filters": {"status": "open", "decision": null, "priority_min": 5, "since": null}}` with flag ON.
→ With flag OFF (current state): `{"ok": false, "action": "list", "gateway": "rigby_work_item", "error": "rigby_work_item review tools are disabled (flag off)", "flag": "RIGBY_WORK_QUEUE_REVIEW_ENABLED"}` — verified §6.1.

**Example 2 — Acknowledge an item (MUTATION — analyzed only this ship):**
```json
{"action": "acknowledge", "id": "<work-item-uuid>", "note": "Reviewing — will decide by EOD"}
```
→ Would return `{"ok": true, "action": "acknowledge", "gateway": "rigby_work_item", "work_item": {...}, "transition": {"from": "open", "to": "acknowledged", "note": "..."}}` with flag ON.

**Example 3 — Resolve with outcome (MUTATION):**
```json
{"action": "resolve", "id": "<uuid>", "outcome": "acted", "note": "Fixed via PR #3512"}
```
→ Would transition to `resolved` + write OpsRunEvent(`resolved` label) with detail `{outcome: "acted", note: "..."}`.

**Example 4 — Ignore with reason (MUTATION):**
```json
{"action": "ignore", "id": "<uuid>", "reason": "False positive — spider re-ingested duplicate"}
```
→ Would transition to `ignored` + write OpsRunEvent(`ignored` label) with detail `{reason: "..."}`.

**Example 5 — Delegate to agent (MUTATION `external`):**
```json
{"action": "delegate", "id": "<uuid>"}
```
→ Would call `delegate_work_item(<uuid>)` which validates + writes `delegation_started` event + dispatches `execute_agent_task.apply_async(queue='long_running', context={parent_object_type='RigbyWorkItem', parent_object_id=<uuid>, auto_followup=False})`.

## 5. Failure / empty-state / pagination notes

- **Flag OFF (default runtime state — verified §6.1):** every action returns `_disabled_response(action) = {"ok": false, "action": action, "gateway": "rigby_work_item", "error": "rigby_work_item review tools are disabled (flag off)", "flag": "RIGBY_WORK_QUEUE_REVIEW_ENABLED"}`. Non-raising envelope. Payload contents are ignored — the gate short-circuits before any per-action helper runs.
- **`list` empty state (hypothetical flag ON):** `{ok: true, rows: [], total: 0, ...}`. Envelope shape stable.
- **`list` invalid `since` string:** silently drops the filter (line 197-198 — `since_dt = None` path). No error.
- **`acknowledge` missing `id`:** `{ok: false, action: "acknowledge", gateway: "rigby_work_item", error: "work_item_id is required"}`. Non-raising.
- **`acknowledge` unknown `id`:** `{ok: false, ..., error: "RigbyWorkItem <id> not found"}`. Non-raising.
- **`acknowledge` on terminal (resolved | ignored):** `{ok: false, ..., error: "Cannot acknowledge a <status> work item. Allowed source states: open, acknowledged.", work_item: {...}}` — includes serialized work_item for context.
- **`acknowledge` on already-acknowledged (idempotent):** `{ok: true, action: "acknowledge", ..., no_op: true, work_item: {...}}` — no new audit row, no new state write.
- **`resolve` missing `outcome`:** `{ok: false, ..., error: "outcome is required and must be one of ['acted', 'delegated_externally', 'no_action_needed']; got '<x>'"}`. Non-raising.
- **`resolve` on already-resolved (idempotent):** `{ok: true, ..., no_op: true, work_item: {...}}`.
- **`resolve` on ignored:** `{ok: false, ..., error: "Cannot resolve an ignored work item. Allowed source states: open, acknowledged.", work_item: {...}}`.
- **`ignore` missing `reason`:** `{ok: false, ..., error: "reason is required and must be a non-empty string"}`. Non-raising.
- **`ignore` on already-ignored (idempotent):** `{ok: true, ..., no_op: true, ...}`.
- **`ignore` on resolved:** `{ok: false, ..., error: "Cannot ignore a resolved work item. Allowed source states: open, acknowledged."}`.
- **`delegate` missing `id`:** `{ok: false, ..., error: "work_item_id is required"}`. Non-raising.
- **`delegate` on `notify` decision:** returns `{ok: false, error: "not_delegatable", ...}` — routing table only includes `monitor → TrendAnalysisAgent` at v0 (line 47-49 of `rigby_mission_delegation.py`).
- **`delegate` re-delegation with non-terminal execution:** service refuses when a `pending`/`in_progress` AgentExecution already exists for the item; re-delegation allowed only after failed/cancelled.
- **`delegate` with `RIGBY_DELEGATION_ENABLED=False`:** returns "delegation disabled" envelope (per `rigby_mission_delegation.py:22-24` module docstring).
- **Invalid action string:** `{ok: false, action, gateway: "rigby_work_item", error: "Unknown action <x>. Supported: list / acknowledge / resolve / ignore / delegate."}`. Non-raising in-envelope error. Fourth divergence-class instance in the sweep (Ledger #5 consistency lint candidate).
- **Pagination:** `list` supports `offset` + `limit` (capped at 100). Other actions single-row.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 4 mutation actions declared in `## Covered actions` (acknowledge / resolve / ignore / delegate). ANALYZED-NOT-EXECUTED at this ship per Chris D-verdict guardrail. Live mutation verification deferred pending BOTH handler-layer `dry_run` affordance (Ledger #38) AND flag flip (`RIGBY_WORK_QUEUE_REVIEW_ENABLED=True`).**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `acknowledge` | `spreading` | `td_handlers_rigby_work_queue.py:287-296` | `RigbyWorkItem.save(update_fields=['status','updated_at'])` (1 row) + `OpsRunEvent.objects.create(...)` (1 row via `_write_transition_event` at line 118-123) | OpsRunEvent.post_save receivers fire (see §5a "Signal-chain evidence") | none direct |
| `resolve` | `spreading` | `td_handlers_rigby_work_queue.py:372-382` | `RigbyWorkItem.save(update_fields=['status','resolved_at','updated_at'])` (1 row) + `OpsRunEvent.objects.create(...)` (1 row, event_type=`step_pass`) | same OpsRunEvent receivers | none direct |
| `ignore` | `spreading` | `td_handlers_rigby_work_queue.py:453-463` | `RigbyWorkItem.save(update_fields=['status','updated_at'])` (1 row) + `OpsRunEvent.objects.create(...)` (1 row) | same OpsRunEvent receivers | none direct |
| `delegate` | `external` | `td_handlers_rigby_work_queue.py:502` → `rigby_mission_delegation.delegate_work_item` | `OpsRunEvent.objects.create(label='delegation_started', ...)` (1 row on the parent MissionRun) + implicit `AgentExecution` row created by dispatch chain | OpsRunEvent.post_save receivers + `AgentExecution.post_save` receiver at `core/signals/rigby_delegation_signals.py:157` (writes subsequent `agent_assigned`/`agent_completed`/`verification_*`/`mission_closed` lifecycle events — push-based, no polling) | **Celery `execute_agent_task.apply_async` on the `long_running` queue** with `parent_object_type='RigbyWorkItem'` + `parent_object_id=<uuid>` context |

### Signal-chain evidence (Chris D-verdict guardrail — file/line cited)

- **OpsRunEvent.post_save receivers on ALL 4 mutations:** every transition writes an OpsRunEvent via `_write_transition_event` (line 89-123). The same 2 receivers documented for `mission_verdict` (`broadcast_mission_verdict` at `mission_verdict_signals.py:56` + `escalate_mission_verdict_to_hai` at `mission_verdict_attention_signals.py:68`) subscribe to `OpsRunEvent.post_save`. **BUT** those receivers gate on `label.startswith('verdict_issued:')` at `mission_verdict_signals.py:71` — so `acknowledge`/`resolve`/`ignore`/`delegation_started` labels do NOT trigger the mission-verdict broadcast/HAI receivers. The labels are (per `td_handlers_rigby_work_queue.py:53-58`): `LABEL_ACKNOWLEDGED = "acknowledged"`, `LABEL_RESOLVED = "resolved"`, `LABEL_IGNORED = "ignored"`. These pass the receivers' filter early-return.
- **AgentExecution.post_save receiver on delegate:** `core/signals/rigby_delegation_signals.py:157` — writes `agent_assigned`/`agent_completed`/`verification_started`/`verification_completed`/`mission_closed` lifecycle events to the parent MissionRun as the delegated agent runs. Push-based (no polling). Documented at `rigby_mission_delegation.py:12-15`.
- **delegate is external:** the dispatch step is a Celery `apply_async` — leaves the handler process. Even at `spreading`-tier signal fan-out on the OpsRunEvent write, the tier promotes to `external` because of the Celery boundary.

### Idempotency proof bar (Chris D-verdict guardrail)

- **`acknowledge` idempotency:** `if item.status == STATUS_ACKNOWLEDGED: return {"ok": True, "no_op": True, ...}` at line 277-284 — no new state write, no new audit row.
- **`resolve` idempotency:** `if item.status == STATUS_RESOLVED: return {"ok": True, "no_op": True, ...}` at line 350-358.
- **`ignore` idempotency:** `if item.status == STATUS_IGNORED: return {"ok": True, "no_op": True, ...}` at line 433-440.
- **`delegate` idempotency:** service refuses when non-terminal AgentExecution exists (`rigby_mission_delegation.py:154-155` comment). Terminal failures (`failed`, `cancelled`) allow re-delegation.
- **Transition safety:** each mutation uses `transaction.atomic()` (lines 287, 372, 454) — audit row + state flip commit together. No partial-state divergence.
- **update_fields discipline:** every `.save()` call uses `update_fields=[...]` (line 289, 375, 456) — prevents unrelated-field-drift + trims post_save signal payload.

### Deferral rationale (why not live-fire this ship)

- Live-firing any mutation requires `RIGBY_WORK_QUEUE_REVIEW_ENABLED=True` (default OFF). Flipping the flag mid-batch is a Chris directive, not a Claude+Rigby-negotiable safety knob.
- Live-firing `delegate` also requires `RIGBY_DELEGATION_ENABLED=True` (default OFF) AND a real RigbyWorkItem with `decision='monitor'`.
- Handler-layer `dry_run` affordance (Ledger #38) would let §6 LIVE-VERIFIED cover the "returns the shape it would write" contract without side effects. Combined with the flag gate, LIVE-VERIFY would require BOTH flip + dry_run.
- Rigby S2939 zoom-out AGREE-WITH-EDITS: §6 stubs for flag-gated mutation tools are acceptable through Batches 2b/2c; don't force Ledger #38 substrate unless a hidden-side-effect surprise surfaces.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `settings.RIGBY_WORK_QUEUE_REVIEW_ENABLED` | `read` (Django settings) | `td_handlers_rigby_work_queue.py:146` | validated |
| `RigbyWorkItem.objects.all().filter(...)` (list) | `read` | `td_handlers_rigby_work_queue.py:178-215` | validated |
| `RigbyWorkItem.objects.get(id=...)` (acknowledge/resolve/ignore) | `read` | lines 254, 341, 424 | validated |
| `RigbyWorkItem.save(update_fields=[...])` (acknowledge/resolve/ignore) | `db_write` | lines 289, 375, 456 | validated |
| `OpsRunEvent.objects.create(...)` (via `_write_transition_event`) | `db_write` | line 118-123, called from 290, 376, 457 | validated |
| `delegate_work_item(work_item_id)` (delegate) | `dispatch` (Celery `apply_async` fan-out — see Appendix A) | `td_handlers_rigby_work_queue.py:502` → `core/services/rigby_mission_delegation.py:131` | validated (S1250 PR 8) |
| `OpsRunEvent.post_save` (indirect) | `dispatch` (signal fan-out — filtered by label prefix; mutation labels here do NOT fire the mission_verdict receivers) | fires on lines 118, 502 → §5a "Signal-chain evidence" | filtered — verdict receivers early-return on non-`verdict_issued:*` labels |
| `AgentExecution.post_save` (indirect, delegate only) | `dispatch` (signal fan-out — writes lifecycle audit events) | fires downstream of Celery task completion; handler at `core/signals/rigby_delegation_signals.py:157` | validated |

**No Appendix N (Network-Preflight) needed:** neither the handler nor `delegate_work_item` directly leaves the process via HTTP. Downstream Celery agent runs MAY do HTTP (out-of-scope for this handler-boundary doc).

### Appendix A — Async-Fanout (first-hop = Celery `apply_async` via `delegate` action)

Filling per S2917 batch 7 template extension — `delegate` is the only Slice 7 Batch 2a action whose first-hop is Celery dispatch.

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task.apply_async(...)` resolves to `AGENT_MAP['TrendAnalysisAgent']` (v0 routing per `rigby_mission_delegation.py:47-49`). First-hop opacity: handler SEES the routing decision + serialized context; the Celery worker actually executes the agent's `.run()` method. Extension: additional agents can be added to `DELEGATION_ROUTING` dict at `rigby_mission_delegation.py:47`.
- **A2. Queue name(s) + priority:** `long_running` queue (per `rigby_mission_delegation.py:143` docstring). Priority not set. Shared-worker queue — coexists with other long-running dispatch (agent audit tasks, deep-research tasks).
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery) + `work_item_id` (domain-object) + `execution_id` (AgentExecution row) — dual/triple identifier envelope. Exact shape returned by `delegate_work_item` service.
  - (b) **Polling endpoints:** `AgentExecution` row status field (via `execution_history_tool`); OR downstream `OpsRunEvent` lifecycle labels (`agent_assigned`/`agent_completed`) via `zoom_out_tool` or direct OpsRunEvent query; OR `notify_agent_complete_tool` subscription for push-based completion.
  - (c) **Idempotency stance:** `dedupe_key: work_item_id + non_terminal_execution_check` — service refuses re-delegation while an AgentExecution with `status in ('pending', 'in_progress')` exists for the item. Terminal failure allows re-delegation. Explicit re-delegation contract per `rigby_mission_delegation.py:11 + 54-56`.
- **A4. Downstream side-effect boundary:** the fanned-out `TrendAnalysisAgent.run()` executes the agent's pipeline — likely including: LLM calls (via `BaseAgent._call_openai` / equivalent), Spider queries, ToolCallRecord writes, LLMCallEvent writes, sub-tool dispatch (if the agent uses PA tools). Cite `core/agents/trend_analysis_agent.py` for the entrypoint. **Explicit call-out: dispatcher re-entry hotspot** if the agent invokes tools that route back into `tool_dispatcher._handle_*`. Full downstream audit is out-of-scope for this handler-boundary doc — see `TrendAnalysisAgent` validation (deferred).
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** authoritative status = `AgentExecution.status`. Best-effort event stream = OpsRunEvent lifecycle rows on the parent MissionRun (written by `rigby_delegation_signals.py:157` post_save receiver).
  - (b) **Cancel semantics:** no explicit cancel path in v0. Celery revoke would work at the queue layer but there's no domain-side "delegation cancelled" marker. "No cancel" is the honest v0 answer.
  - (c) **Revisit triggers:** re-audit this Appendix A if (1) `DELEGATION_ROUTING` grows beyond `monitor → TrendAnalysisAgent`, (2) queue name changes from `long_running`, (3) `auto_followup=False` flips to True (would introduce PA conversation noise), (4) new dispatcher re-entry sites are added to `TrendAnalysisAgent.run()`, or (5) `_impl_execute_agent_task` context contract changes.

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: AUTO-FLAGGED by Ledger #5 lint (S2938 substrate) — 2 hits.** Per Q2 AGREE at S2939 T0, this disposition is auto-picked-up from the S2939 open-sequence lint pre-flight rather than manually re-scanned:

- **`handler_drift_action_count`** — module docstring (`td_handlers_rigby_work_queue.py:2-25`) states **"four actions"** (list / acknowledge / resolve / ignore) but the schema + handler both have **5 actions** (adds `delegate` at line 5706 enum, handler branch line 157-158). The `delegate` action was added in S1250 PR 8 without a module docstring refresh.
- **`handler_drift_negative_claim_dispatch`** — module docstring lines 20-22 assert "No agent dispatch" + "No initiative / tool dispatch" but the `delegate` action's handler at line 481-502 explicitly calls `delegate_work_item` which dispatches via `execute_agent_task.apply_async` on the `long_running` queue. The docstring claim was true when written (pre-PR 8) but is now stale.

**Root cause:** both hits trace to the same underlying Ledger #39 issue — S1250 PR 8 added the `delegate` action + async dispatch without refreshing the module docstring. The Ledger #5 Tier 1 MVP lint (shipped S2938) auto-detects both drift signatures with zero false positives across the other 115 wired tools. See Ledger #39 (deferred at S2938; **now auto-detected** at each build_pa_tool_audit run) for the natural fold-in fix (~5-min docstring refresh) — recommended bundle with any future rigby_work_queue touch.

Schema description (`pa_tool_schemas.py:5694-5700`) is more accurate than the module docstring: names all 5 actions, correctly says "internal queue only", correctly cites `RIGBY_WORK_QUEUE_REVIEW_ENABLED` flag. Schema is source-of-truth for callers.

**Lint pre-flight at S2939 open verified:** `rigby_work_item` returns 2 `handler_drift_*` hits (verified via `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check`). Matches expected count from S2938 close projection.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — flag-gated, LIVE-VERIFIED at §6.1.** `RIGBY_WORK_QUEUE_REVIEW_ENABLED` defaults `False` per `td_handlers_rigby_work_queue.py:23-25` module docstring + `settings.RIGBY_WORK_QUEUE_REVIEW_ENABLED, False` default at line 146. §6.1 LIVE-VERIFIES the `disabled_response` shape (flag-OFF path). Enabled-path (`RIGBY_WORK_QUEUE_REVIEW_ENABLED=True`) is NOT exercised this ship — requires explicit flag flip which is a Chris directive.

`RIGBY_DELEGATION_ENABLED` secondary gate on `delegate` action is enforced in the service layer (`rigby_mission_delegation.py`), not the handler. Documented in schema description at `pa_tool_schemas.py:5722-5723` ("Gated by RIGBY_DELEGATION_ENABLED").

### 5c.3 Shared handler-file coupling noted

**Disposition: PASS — dedicated handler.** `td_handlers_rigby_work_queue.py` is a 502-line dedicated file with a single tool (`rigby_work_item`). No sibling tools share this module. The handler imports from `core/models_rigby_work_items` (RigbyWorkItem model), `core/models_ops_runs` (OpsRunEvent — via `_write_transition_event`), and `core/services/rigby_mission_delegation` (delegate service). Those are shared substrate modules but no other PA tool handler routes through the same three-module bundle. No coupling to note at the tool level.

## 6. Evidence

**LIVE-VERIFIED applies only to strictly read-only actions executed in a non-mutating way; all mutations remain §5a ANALYZED-NOT-EXECUTED.** (Chris D-verdict guardrail; sentence lifted verbatim per S2939 T0 ratification.)

Live PA-dispatch evidence for the `disabled_response` shape (flag OFF path). At the current default runtime state (`RIGBY_WORK_QUEUE_REVIEW_ENABLED=False`), ALL 5 actions short-circuit — so §6.1 covers the safe-verify surface without requiring flag flip.

### 6.1 `action=list` (flag OFF — disabled_response path) — LIVE at S2939 T0

Handler branch line 146-147 → `_disabled_response("list")`. Pure envelope generation; no ORM access; no side effects. **Confirmed live via post-merge dispatch at PR #3512 close per S2938 handoff §4** (`rigby_work_item action=list returns clean disabled_response post-recycle (flag OFF)`).

Envelope shape (from `_disabled_response` helper at `td_handlers_rigby_work_queue.py:63-71`, verified via live dispatch at S2939 T0):
```json
{
  "ok": false,
  "action": "list",
  "gateway": "rigby_work_item",
  "error": "rigby_work_item review tools are disabled (flag off)",
  "flag": "RIGBY_WORK_QUEUE_REVIEW_ENABLED",
  "error_code": "legacy_error"
}
```

Note: `error_code: "legacy_error"` is appended by the dispatcher's error-envelope normalizer (upstream of `_disabled_response`) rather than the helper itself — the helper returns 5 keys; the dispatcher wrapper appends the 6th. Confirmed live 2026-07-24.

**Observations locked at this HEAD:**
- Flag defaults OFF — no operator intervention required to reproduce.
- Envelope shape stable across all 5 actions (same `_disabled_response` helper; only the `action` field varies).
- `flag` field explicitly names the gate — callers know exactly which setting to flip to enable.
- No mutation, no signal fan-out, no external touches. Safe to re-verify at every merge.

### 6.2 `action=acknowledge` (flag OFF) — ANALYZED

Handler branch line 146-147 → same `_disabled_response("acknowledge")` shape. Payload contents ignored (no work_item_id resolution, no state read/write). Not exercised as separate call; short-circuit path verified above.

### 6.3 `action=resolve` (flag OFF) — ANALYZED

Same short-circuit as §6.2. `_disabled_response("resolve")` envelope.

### 6.4 `action=ignore` (flag OFF) — ANALYZED

Same short-circuit. `_disabled_response("ignore")` envelope.

### 6.5 `action=delegate` (flag OFF) — ANALYZED

Same short-circuit. `_disabled_response("delegate")` envelope. Note: even if `RIGBY_WORK_QUEUE_REVIEW_ENABLED` were flipped ON, `RIGBY_DELEGATION_ENABLED` is a secondary gate — delegate action would still refuse with "delegation disabled" from the service layer.

### 6.6 Mutation actions (flag ON, hypothetical) — ANALYZED-NOT-EXECUTED

`acknowledge`, `resolve`, `ignore`, `delegate`: not exercised live this ship. See §5a for per-action write-target inventory + signal-chain evidence + idempotency proof + Appendix A async-fanout contract + deferral rationale.

### 6.7 Invalid action gating (flag OFF)

Flag OFF short-circuits BEFORE the invalid-action branch — so an invalid action with flag OFF returns `_disabled_response("<invalid>")` (which happily accepts any string). The invalid-action branch (line 160-168) is only reachable when flag is ON AND action doesn't match any of the 5 valid values. Not exercised this ship — requires flag flip.

## Related

- **Adjacent tools (same Slice 7 Batch 2a):** `mission_verdict` (all-mutation), `newsletter_tool` (4-mut/3-read bifurcated). This tool ships bifurcated Option C with the additional flag-gate wrinkle.
- **Adjacent tools (adjacent surface):** `human_attention_bridge` (HAI items — for Chris to see; distinct queue); `rigby_shift_brief_tool` (operator status; may reference queue counts); `zoom_out_tool` (governance ledger read — OpsRunEvent aggregation touches the transition events this tool writes).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md`; `core/services/rigby_event_intake.py` (upstream event source that creates RigbyWorkItems); `core/services/rigby_mission_delegation.py` (delegate service layer).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2936 Slice 6 CLOSE (bifurcated Option C shape); S2937 T1 Chris ratification (4-batch Slice 7 plan + §5c retro-fold + Ledger #39 first-surfaced); **S2938 Ledger #5 lint promoted to substrate — this doc is the first live-in-force pre-flight consumer AND the tool that motivated the lint substrate**; S2939 T0 Chris D-verdict RATIFIED with two guardrails; S2939 Q2 AGREE (auto-flag rendering from Ledger #5 lint).
- **Lint pre-flight at S2939 open:** `rigby_work_item` → 2 `handler_drift_*` hits (`handler_drift_action_count` + `handler_drift_negative_claim_dispatch`) — both trace to Ledger #39 cause. See §5c.1 for the auto-flag disposition.
- **First-hop dependencies:** see §5b table + Appendix A (`delegate` async fan-out via Celery `execute_agent_task.apply_async` on `long_running` queue).
- **Regression coverage:** `core/tests/test_rigby_work_item.py` (main test file), `core/tests/test_rigby_work_queue_review.py` (review-flow tests), `core/tests/test_rigby_mission_delegation.py` (delegate service tests), `core/tests/test_delegation_lifecycle_smoke_test.py` (end-to-end lifecycle), `core/tests/test_rigby_intake_observation.py` (upstream intake). Strong test coverage — deferring live-mutation verify does NOT leave a coverage gap.
- **Ledger candidates surfaced this doc:** **Ledger #39 (already open, now auto-detected by Ledger #5 lint)** — natural fold-in candidate for the ~5-min module docstring refresh (4→5 actions + drop "No agent dispatch" claim). Ledger #38 (`dry_run` substrate) + `RIGBY_WORK_QUEUE_REVIEW_ENABLED` flag flip both remain blockers for LIVE-VERIFY on the mutation actions — this doc corroborates both.
- **Post-merge live-dispatch verification:** exercise `rigby_work_item action=list` after `make recycle-all` at merge; confirm `_disabled_response` envelope shape matches §6.1. Same verification already ran at PR #3512 close per S2938 handoff — pattern is stable.

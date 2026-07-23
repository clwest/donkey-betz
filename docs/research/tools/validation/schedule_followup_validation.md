# `schedule_followup` — Validation Report (S2910)

**Tool:** `schedule_followup`
**Schema:** `core/services/pa_tool_schemas.py:5622`
**Handler:** `core/services/td_handlers_agents.py:6389` (`_handle_schedule_followup`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2910 (Path B systematic sweep — Slice 2 batch 5 of `td_handlers_agents`)
**HEAD at validation:** `e642c7aa8` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression test for PA-context invariant added this ship — see §Related.
**Category upgrade target:** `untested` → `validated_full` (actionless — no schema `action` enum; single-verb subscribe surface with load-bearing PA-context invariant covered by evidence + new test).
**Rigby SIGN:** S2910 T0 SIGN AGREE-with-edits + Q4 zoom-out asked for PA-context invariant assertion (this ship honors that request via new regression test — see §5a + §Related). S2910 T1 SIGN pending.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Subscribe the current PA conversation to a completion notification for a previously-dispatched async agent task (Session 1174 PR-2b-1). Answers "notify me here when X finishes" for long-running agent executions dispatched from a PA conversation (`run_agent` / `workflow_orchestration_agent` / etc.). When the agent's `AgentExecution` reaches a terminal state (`completed` / `failed` / `cancelled`), a signal handler fires `fire_agent_followup_subscriptions()` which broadcasts back into the same PA conversation.

Idempotent by design: unique constraint on `(execution, conversation_id)` means duplicate subscribes return the existing row (`mode='already_subscribed'`) rather than crashing. Subscribe-after-terminal is handled specially — if the execution finished before subscribe, the notification fires immediately (`mode='delivered_immediately'`) rather than creating an armed-but-doomed subscription.

Distinct from `agent_control_tool` (which surfaces execution state on demand — the pull surface) and from `execution_history_tool` (row lookup). `schedule_followup` is the *push* surface: subscribe once, get notified once.

## Covered actions

**This tool is actionless by schema design** — `schema_action_count=0` per T1a harness artifact (`docs/audits/pa_tools/harness_output/schedule_followup.json`), no `action` enum declared at `pa_tool_schemas.py:5636-5653`. The dispatch surface is a single implicit `subscribe` call parameterized by `execution_id | task_id` + optional `after_seconds`.

Therefore `## Covered actions` is intentionally empty. S2910 batch 5 validates actionless-shape via `TOOL_DEFAULTS` seed (`WRITE_GATED` — writes an `AgentFollowupSubscription` row; gated on PA-context conversation_id promotion, not on caller-supplied auth). Behavior is exercised through §6.2 handler trace + the new regression test in §Related.

## 3. Schema notes

- **Required (declared):** none — schema `required: []` at line 5652. The tool's real invariants are handler-side (context-promoted `conversation_id` + at least one of `execution_id | task_id`).
- **Optional (declared):**
  - `execution_id` (string; canonical UUID of `AgentExecution`).
  - `task_id` (string; Celery task_id — fallback lookup via `AgentExecution.objects.filter(input_data__celery_task_id=task_id).order_by('-created_at').first()`).
  - `after_seconds` (integer; TTL window; default 60 per `AgentFollowupSubscription.DEFAULT_TTL_SECONDS`; capped at 600 per `.MAX_TTL_SECONDS`).
- **Load-bearing implicit param — `conversation_id`:** pulled from the PA context at handler line 6425, either `payload.get('conversation_id')` (promoted into payload root by `unified_pa_entrypoint`) or `(payload.get('context') or {}).get('conversation_id')` (promoted into `payload.context` by `_CONTEXT_PROMOTE_KEYS` in `tool_dispatcher`). **Absence → fail-loud** (`{success: false, error: 'schedule_followup requires a PA conversation context (no conversation_id available).'}`).
- **Stable 11-key response contract:** `_make_followup_response` at handler line 6357 (Session 1175 PR-2b-2). Every return path — success or error — emits `{success, mode, subscription_id, execution_id, execution_status, state, expires_at, fired_at, after_seconds, message, error}` with `None` where not applicable. Rigby's PR-2b-1 review ask: "callers can treat the shape as fixed."

## 4. Golden-path examples

**"Notify me when this execution finishes":**

```
schedule_followup  execution_id=<AgentExecution.uuid>
```

**"Notify me when this task_id finishes, waiting up to 5 minutes":**

```
schedule_followup  task_id=<celery.task_id>  after_seconds=300
```

**"Subscribe idempotently (safe to call twice)":** same call twice returns `mode='subscribed'` first time, `mode='already_subscribed'` second time.

**Terminal-at-subscribe path:** if the execution has already transitioned to `completed` / `failed` / `cancelled` by the time the tool is called, response `mode='delivered_immediately'` — the follow-up broadcast fires atomically before returning.

## 5. Failure / empty-state / pagination notes

- **Missing PA context** — returns `{success: false, ...11-key contract... , error: 'schedule_followup requires a PA conversation context (no conversation_id available).'}` at handler line 6430. **This is the invariant Rigby Q4 flagged in her T0 SIGN zoom-out — the tool only works when the caller is the PA. See regression test in §Related.**
- **Missing both `execution_id` and `task_id`** — returns `{success: false, ..., error: 'schedule_followup requires execution_id OR task_id.'}` at line 6451.
- **`execution_id` doesn't match any AgentExecution** — returns `{success: false, ..., error: 'No AgentExecution found with execution_id=<uuid>.'}` at line 6460.
- **`task_id` doesn't match any AgentExecution.input_data.celery_task_id** — returns `{success: false, ..., error: 'No AgentExecution found with celery task_id=<id>.'}` at line 6469.
- **Non-PA-dispatched execution (NULL `conversation_id`)** — returns `{success: false, execution_id, execution_status, ..., error: 'Cannot subscribe: execution ... was not dispatched from a PA conversation (conversation_id is NULL). Follow-up requires a PA-originated dispatch.'}` at line 6478. Rationale: the signal handler's scope-rules invariant means non-PA executions can't fire follow-up; subscribing to one is nonsense.
- **Cross-conversation subscribe** — returns `{success: false, execution_id, execution_status, ..., error: 'Cross-conversation subscription rejected: execution ... was dispatched from ..., but this call is from .... Subscribe from the same conversation that dispatched.'}` at line 6493. Rationale: signal handler fires only on matching `conversation_id`; cross-conversation subscribes would silently never fire.
- **`after_seconds` out of range** — clamped at line 6440-6443: `after_seconds <= 0` → default (60); `after_seconds > 600` → cap (600). No error envelope.
- **`after_seconds` unparseable** — coerced to default at line 6438 (except-clause on `TypeError`/`ValueError`).
- **IntegrityError on subscribe** — returns `{success: false, execution_id, execution_status, ..., error: 'Subscription create failed: <exc>'}` at line 6555. Should be rare given `get_or_create` semantics; caught as a defensive branch.
- **Terminal-at-subscribe (already `completed`/`failed`/`cancelled`)** — creates the subscription row (or fetches existing), calls `fire_agent_followup_subscriptions(execution)` atomically, refreshes from DB, returns `mode='delivered_immediately'`, `state` = current subscription state (fired), `fired_at` populated.
- **Normal path** — creates armed subscription with TTL, returns `mode='subscribed'` or `mode='already_subscribed'`, `state='armed'`, `expires_at` populated, `fired_at=None`.

## 5a. Mutation containment

- **Mutating actions:** the entire tool is mutating in the platform sense — writes `AgentFollowupSubscription` row via `get_or_create` and, in the terminal-at-subscribe path, atomically fires the broadcast helper.
- **Safety metadata:** seeded in `TOOL_DEFAULTS` at S2910 with `default_safety_class='WRITE_GATED'`, `applicability='conditional'`. Notes: `deps: AgentFollowupSubscription get_or_create (idempotent); gate: pa_context (conversation_id promoted by unified_pa_entrypoint) + execution_id|task_id; actionless schema`.
- **Idempotency mitigates blast radius:** duplicate subscribes deduplicate via unique constraint on `(execution, conversation_id)`. No cost of accidental double-call.
- **Cost surface:** subscription rows are small; TTL bounded at 600s; state machine has terminal states (`armed → fired`, `armed → expired`). Not a "growing surface" concern.
- **Deferral rationale:** actionless tools are not dispatched by the T1a MVP harness regardless of safety class — the class is doc-primary here. WRITE_GATED classification is the correct label because the tool *does* write to the DB (not READ_ONLY), but the write is gated on a runtime context invariant (PA promotion) rather than an auth boundary — so `applicability='conditional'` captures the shape.

## 6. Evidence

### 6.1 T1a harness artifact — this ship

`docs/audits/pa_tools/harness_output/schedule_followup.json` at HEAD `e642c7aa8` (harness run 2026-07-23):

```json
{
  "actions": [],
  "harness_version": "v2",
  "schema_action_count": 0,
  "tool_name": "schedule_followup"
}
```

Expected shape for actionless tools — zero rows.

### 6.2 Handler-trace evidence — this ship

Handler at `td_handlers_agents.py:6389-6576`:

- Line 6421-6428: PA-context conversation_id resolution via payload root OR `payload.context` promotion.
- Line 6429: fail-loud on missing conversation_id (Rigby Q4 invariant).
- Line 6436-6443: `after_seconds` parse + clamp `[0, 600]`.
- Line 6448-6472: `execution_id` primary path OR `task_id` fallback lookup via `input_data__celery_task_id`.
- Line 6477: reject non-PA execution (NULL conversation_id).
- Line 6493: reject cross-conversation subscribe.
- Line 6509-6541: terminal-at-subscribe path — atomic `get_or_create` + `fire_agent_followup_subscriptions` + return `mode='delivered_immediately'`.
- Line 6543-6561: normal path — armed subscription with TTL.
- Line 6357: `_make_followup_response` stable 11-key contract enforced across all return paths.

### 6.3 Runtime-not-executed — this ship

- **Terminal-at-subscribe path** — not exercised (would require a completed AgentExecution + a PA-context dispatch).
- **Normal path (armed subscription created)** — not exercised (same context requirement).
- **Signal handler fire path** — out of scope for tool-surface validation; covered by `core/tasks_agents.py` tests for `fire_agent_followup_subscriptions`.
- **Fully-live E2E** — well-worn since Session 1174; not re-exercised for this doc-only ship.

**PA-context invariant regression test added this ship** — see §Related. The `no conversation_id → fail-loud` path is the Rigby-Q4-load-bearing invariant; the new test asserts it in isolation so a future refactor of PA-context promotion cannot silently break the tool.

---

## Related

- **Rigby T0 SIGN Q4 zoom-out ask honored:** "targeted tests/assertions for context-dependent tools like schedule_followup." This ship adds a new test class `ScheduleFollowupPAContextInvariantTests` to the existing `core/tests/test_schedule_followup_response_shape.py`, covering the missing-conversation_id fail-loud path + the nested-context promotion path + root-vs-nested equivalence. Rationale: `schedule_followup` is the only PA-context-load-bearing tool in batch 5; if the handler-side OR-fallback at `td_handlers_agents.py:6425-6428` ever collapses to only-root, PA callers that route through `payload['context']` silently break. **Coverage limit** (Rigby T1 SIGN Q3 fold): these tests exercise the handler-side contract only. A refactor of the entrypoint-side injection at `unified_pa_entrypoint.py:2262-2264` (the `arguments.setdefault('conversation_id', self.conversation_id)` line) would NOT be caught by these tests — that requires a higher-level PA-entrypoint test. Follow-up candidate; not this ship's scope.
- **Ledger candidates surfaced this ship:** none new. The tool has been through Session 1174-1178 hardening cycles; behavior is well-specified.
- **Adjacent tools:**
  - `agent_control_tool` — pull-surface for execution state (see S2892+ validation doc when it lands).
  - `execution_history_tool` — row lookup (returns `execution_id` values suitable for this tool).
  - `run_agent` / `workflow_orchestration_agent` / other agent-dispatch tools — the *producers* of the `execution_id` this tool subscribes to.
- **Substrate context:** part of S2910 batch 5. Uniform-safety actionless tool with PA-context invariant — the Rigby-Q4-flagged surface. Batch 5 peers: `web_fetch_tool` (READ_ONLY actionless), `legal_doc_drafter_agent` (MUTATION actionless, disclaimer gate), `brainstorm_tool` (mixed 6+1 per-action).
- **Related design docs:** Session 1174 PR-2a signal handler design; Session 1175 PR-2b-2 stable-11-key contract review; Session 1178 shared TTL constants.
- **Metadata seed:** `TOOL_DEFAULTS` entry at `core/services/tool_action_metadata.py` this ship (Pattern A — uniform safety class + actionless).

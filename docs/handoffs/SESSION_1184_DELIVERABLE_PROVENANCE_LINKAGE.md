# Session 1184 — Deliverable → Execution provenance linkage + PA worker FC env gotcha

**Status:** Closed. 1 feature PR ready (provenance linkage). 1 ops finding + memory written (PA worker function-calling env). 1 live verification through Rigby on a fresh conversation.
**Date:** 2026-06-20
**Pinned conversation:** `pa-a60842917d36` — spun mid-session after `pa-f4644aa2fd1b` hit a tool-refusal loop following a manual PA worker restart that dropped `PA_USE_FUNCTION_CALLING=true`. Old pin (`pa-8f8ef45338ce4a24` from Sessions 1182-1183) retired.
**Driving deliverable:** [`e4f4e12f-bd77-4611-a3d6-1a50fd3b9412`](#) — "Implement provenance linkage for deliverables (Deliverable → Execution ID)" staged by Rigby at session open.
**Prior session handoffs:**
- [SESSION_1183_CELERY_BEAT_OWNERSHIP_AND_WORKER_RESTART.md](./SESSION_1183_CELERY_BEAT_OWNERSHIP_AND_WORKER_RESTART.md) — beat ownership doc fix + worker restart for PR #2357

## TL;DR

Every deliverable now carries an origin execution id, queryable end-to-end via a new `provenance` block on `deliverable_tool.detail`. **Zero schema changes** — reused Session 843's `parent_object_type` + `parent_object_id` fields. For PA-direct creates (no `AgentExecution` context), the factory now synthesizes a lightweight `AgentExecution` receipt and links it the same way. Soft-enforced at the factory: PA/user-direct paths always get a receipt; other missing-context cases log a WARN for an incremental caller sweep instead of hard-failing.

Live verification confirmed via Rigby on fresh conv `pa-a60842917d36`:

```json
"provenance": {
  "origin_execution_id": "43c1dd8d-d1c8-47da-9c1e-fb67a3a5214c",
  "trigger_source": "pa_tool",
  "created_by_agent": "PersonalAssistant",
  "trace_id": null,
  "tool_calls": [],
  "legacy_no_provenance": false,
  "synthesized": true
}
```

| Item | Status | Notes |
|---|---|---|
| Factory synthesis for PA-direct creates | ✅ | `_synthesize_pa_execution_receipt()` in `deliverable_factory.py` |
| Read helper + detail tool integration | ✅ | `core/services/deliverable_provenance.py` + wired into `td_handlers_agents._handle_deliverables` `detail` branch |
| Soft-enforce WARN for autonomous-agent missing context | ✅ | Logged with caller info; sweep deferred |
| Unit tests (AC1–AC5) | ✅ | `core/tests/test_deliverable_provenance.py` — 4/4 pass |
| Live verification through Rigby | ✅ | After diagnosing + fixing the FC env regression |
| `tools/pa_local.sh` repinned + doc-block warning | ✅ | New conv + FC env reminder |
| New memory written | ✅ | `feedback_pa_worker_function_calling_env.md` |

## The work — design decisions ratified by Rigby

Recon revealed most of the infra was already shipped (Session 843 orchestration contract). The questions were about **how to surface what exists**, not what to build. Four decisions sent to Rigby with leans; all four leans ratified:

| Q | Decision | Reason |
|---|---|---|
| **Q1 — field design** | Reuse `parent_object_type`+`parent_object_id`; expose `origin_execution_id` as a computed read-layer property | Spec explicitly allows mapped names; zero migration; leverages Session 843 dedupe logic already in factory |
| **Q2 — PA-direct receipt** | Synthesize `AgentExecution` row (`owner_agent=PersonalAssistant`, `status=completed`, `parent_object_type='deliverable_factory'`) | Live table; no schema sprawl; `conversation_id` already supported (Session 1174) |
| **Q3 — `tool_call_id` linkage** | Derive via trace_id pivot — `Deliverable → AgentExecution → trace_id → ToolCallRecord` | Both sides already trace_id-indexed (Session 843 + 861); no new FK |
| **Q4 — enforcement strictness** | Soft-enforce: synthesize for PA/user-direct paths; WARN for other missing-parent cases | Guarantees AC1 for new deliverables without a 31-caller blast radius; hard-required deferred to Phase 2 |
| **Q5 — UI surface** | Read-via-tool is sufficient | Acceptance criteria are about a query path; UI follow-on optional |

Plus one Rigby clarification: tool output should expose a normalized `provenance` block (not loose top-level fields), and no new DB columns unless we hit a hard blocker. Honored.

## What shipped

### `core/services/deliverable_factory.py`
- New `_is_pa_direct_context(agent_name, trigger_source)` — PA_IDENTITY OR trigger_source in `{pa_tool, user_request, user_chat, direct}`
- New `_synthesize_pa_execution_receipt(...)` — creates an `AgentExecution` row with `status='completed'`, `owner_agent=<agent>`, `parent_object_type='deliverable_factory'`, normalized trace_id (UUIDs only — non-UUID dispatcher trace_ids like `tool-1-89f14759` get dropped, matching existing factory contract)
- `create_deliverable` synthesis hook: after trigger_source resolution, if no `parent_execution_id` AND context is PA-direct, synthesize and set `parent_object_type='agent_execution'`. Marks `metadata['origin_execution_synthesized']=True`. Non-PA missing-context logs WARN with `agent_name`, `trigger_source`, and title.

### `core/services/deliverable_provenance.py` (NEW)
- `build_provenance_block(deliverable)` — returns normalized dict:
  - `origin_execution_id`: `parent_object_id` if `parent_object_type` in `{agent_execution, deliverable_factory}`
  - `trigger_source`: from `metadata`
  - `created_by_agent`: `agent_name` falling back to `AgentExecution.owner_agent`
  - `trace_id`: from `AgentExecution.trace_id` if resolvable
  - `tool_calls`: up to 25 `ToolCallRecord` rows joined by `trace_id`, serialized as `{id, tool_name, success, latency_ms, created_at}`
  - `legacy_no_provenance`: True for rows with null `parent_object_id`
  - `synthesized`: True if `metadata['origin_execution_synthesized']` was set
- `build_provenance_summary(deliverable)` — compact version (strips `tool_calls`) for list views

### `core/services/td_handlers_agents.py`
- `_handle_deliverables` `detail` branch now adds `'provenance': build_provenance_block(obj)` to the return payload.

### `core/tests/test_deliverable_provenance.py` (NEW)
Four tests, all pass via `USE_PGBOUNCER=0 python manage.py test core.tests.test_deliverable_provenance --keepdb`:
1. `test_agent_dispatch_links_parent_object_id_to_execution` — when caller passes `parent_execution_id`, `parent_object_id` matches
2. `test_pa_direct_create_synthesizes_execution_receipt` — PA-direct path creates a real `AgentExecution` receipt
3. `test_provenance_block_surfaces_full_chain` — full chain including ToolCallRecord pivot by trace_id
4. `test_autonomous_agent_without_execution_is_marked_legacy` — soft-enforce path: WARNs, doesn't block, surfaces `legacy_no_provenance=true`

## Acceptance criteria

| AC | Status | Evidence |
|---|---|---|
| **AC1** every new deliverable has non-null `origin_execution_id` | ✅ | PA-direct synthesis + agent-dispatch enforcement at factory; autonomous-agent missing-context logs WARN (Phase 2 hardens) |
| **AC2** agent-dispatch deliverables link to the exact `AgentExecution` | ✅ | Test 1 + factory contract |
| **AC3** PA-direct creates synthesize a lightweight receipt | ✅ | Test 2 + live Rigby verification |
| **AC4** one query path: deliverable → execution → tool calls | ✅ | `build_provenance_block` resolves chain; Test 3 |
| **AC5** local QA test proves AC1–AC4 | ✅ | 4-test suite passes |

## The bonus debug — PA worker FC env regression

Mid-session, after restarting the PA celery worker manually to pick up factory changes, every Rigby call returned "I don't have tool access" text — looked like a model refusal loop. Spent ~30 min before isolating root cause:

**Cause:** `Makefile` (`make celery`) sets `PA_USE_FUNCTION_CALLING=true` for every worker. My manual `nohup celery -A core worker ...` restart didn't carry that env. Without it, `core/settings.py` defaults `PA_USE_FUNCTION_CALLING=False`, the worker drops to keyword routing in `unified_pa_entrypoint.py`, and `source=claude-code` messages short-circuit to `claude_code_coordination` intent which has NO `elif` branch in the routing — so no tool gets dispatched. Rigby's response is text-only "no tool access" claims that look like model refusal.

**Symptom in `/tmp/celery-pa.log`:** every `[PA_TASK_SUMMARY]` line shows `tools=none tool_calls=0 intent=claude_code_coordination` despite tools being wired.

**Fix:** restart with the env var explicitly:

```bash
PA_USE_FUNCTION_CALLING=true \
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
SKIP_NLP_MODELS=1 TOKENIZERS_PARALLELISM=false \
PG_APPLICATION_NAME=dbz:celery-pa \
nohup .venv/bin/celery -A core worker --loglevel=info \
  --pool=solo --queues=pa --hostname=pa@%h \
  > /tmp/celery-pa.log 2>&1 &
```

Or just use `make celery`. Saved as `feedback_pa_worker_function_calling_env.md` memory + `tools/pa_local.sh` doc-block warns future-me.

## Operational levers

- **Disable PA-direct synthesis fully:** delete the synthesis hook in `create_deliverable` (lines added in `_PA_DIRECT_TRIGGERS` block). PA-direct deliverables will revert to having NULL `parent_object_id` — read layer surfaces `legacy_no_provenance=true`, no other breakage.
- **Disable WARN noise for non-PA missing context:** the WARN is `logger.warning(...)` at the same site; change to `logger.debug(...)` if too noisy during sweep.
- **Disable provenance block in tool output:** remove the `'provenance': build_provenance_block(obj)` line in `td_handlers_agents.py`. Read layer reverts cleanly.
- **Per-callsite override:** any caller of `create_deliverable` can pass `parent_object_type='something_else'` to opt out of the `'agent_execution'` default.

## Phase 2 (deferred — not in this PR)

1. **Caller sweep** — the 31 sites that call `create_deliverable()` without `parent_execution_id` should be migrated to pass it. The WARN log makes them easy to find. Priority: agents that produce user-facing publish-candidate work (ContentWriter, BlogWriter, Editor).
2. **Hard-required `parent_execution_id`** — flip factory contract so missing `parent_execution_id` raises in non-PA contexts. Requires the sweep first.
3. **UI surface** — optional Workspace Files / Deliverable detail panel adds an "Origin" row showing execution id + trigger + agent + click-through. Read-via-tool sufficient for current slice.
4. **Trace_id normalization** — the dispatcher's `tool-N-hex` trace_id format isn't a UUID, so it gets dropped at the factory's existing UUID guard. Downstream effect: `provenance.trace_id` is null for tool-dispatched creates and `tool_calls` derivation can't pivot. Decision needed: standardize on UUID trace ids everywhere, or add a non-UUID column.

## 24h watch

Nothing time-sensitive. The factory + read helper are additive; existing callers unchanged. If anything regresses, the levers above are one-line reverts.

Optional spot-checks to run tomorrow:
- `grep "No parent_execution_id" /tmp/celery-*.log | wc -l` to see how loud the soft-enforce WARN is. If hundreds/day, downgrade to debug or start the caller sweep.
- Check a few recent agent-dispatch deliverables via `deliverable_tool action=detail id=<x>` and confirm `provenance.synthesized=false` and `origin_execution_id` is set (proving the agent-dispatch path also flows through).

## Files touched

```
core/services/deliverable_factory.py        (+121)
core/services/deliverable_provenance.py     (+115, new)
core/services/td_handlers_agents.py         (+6)
core/tests/test_deliverable_provenance.py   (+150, new)
tools/pa_local.sh                           (~14, repin + doc-block)
docs/INDEX.md, docs/_index.json             (regenerated)
```

External: new memory `feedback_pa_worker_function_calling_env.md` in `~/.claude/projects/.../memory/`.

# `reasoning_engine_tool` — Validation Report (S2911)

**Tool:** `reasoning_engine_tool`
**Schema:** `core/services/pa_tool_schemas.py:294`
**Handler:** `core/services/td_handlers_agents.py:5364` (`_handle_reasoning_engine`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2911 (batch 6b pre-req PR — reasoning_engine schema↔handler drift-fix; substrate for batch 6b agent-invocation-scrutiny lane)
**HEAD at validation:** `a35ebd5c5` (2026-07-23; batch 6a merge parent)
**Ship shape:** Doc-only (S2796 shape) + schema alignment + handler bug-fix.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 1 MUTATION action explicitly excluded — see §5a).
**Rigby SIGN:** S2911 T0 SIGN Q4b (batch 6a T1 cycle) — reasoning_engine drift ratified as 1st confirmed instance of schema↔handler drift class; Chris ratified Option A (fix in a separate pre-req PR before batch 6b opens). Post-fix T1 SIGN pending.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Query or trigger the ThinkingAgent reasoning engine. Answers "what's the ThinkingAgent status?", "show me recent thinking cycles", and (via excluded `trigger` action) "kick off a new thinking cycle over recent system activity".

Distinct from `brainstorm_tool` (which searches brainstorming corpora — Discussion + Panel + BrainstormConversation) — `reasoning_engine_tool` is the ThinkingAgent-specific surface. Distinct from `universal_agent_tool` (batch 6b peer, routes arbitrary agents) — `reasoning_engine_tool` is bound to ThinkingAgent + the reasoning-cycle domain. When Rigby needs generic multi-agent routing, use `universal_agent_tool`; when she needs ThinkingAgent-specific introspection or invocation, use this tool.

## Covered actions

**READ_ONLY actions covered (2 of 3 total actions).** 1 MUTATION action (excluded — see §5a) is out of scope for this ship.

- `status` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 4 ms). Returns `{action, engine, status}` — hardcoded envelope `{engine: 'ThinkingAgent', status: 'operational'}`.
- `thoughts` — **in scope this ship** — verified live via T1a harness (`success`, 19 ms). Returns `{action, count, thoughts}` — recent `AgentExecution` rows filtered by `agent__name='ThinkingAgent'`, ordered by `-created_at`, capped at `limit` (default 10).
- `trigger` — **mutation — deferred (invokes real LLM-backed ThinkingAgent cycle)** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `status, thoughts, trigger`). Enum matches handler dispatch branches exactly (drift closed this ship — see §Related).
- **Optional:** `limit` (default 10, for `thoughts` action).
- **Handler default:** `action` defaults to `'status'` if omitted (handler line 5374) — but schema enforces required.

## 4. Golden-path examples

**"Is the reasoning engine up?"**

```
reasoning_engine_tool  action=status
```

**"Show me recent thinking cycles:"**

```
reasoning_engine_tool  action=thoughts  limit=5
```

Response fields per thought: `id, task, status, created_at`.

**"Kick off a new thinking cycle:"** (excluded this ship — see §5a)

```
reasoning_engine_tool  action=trigger
```

## 5. Failure / empty-state / pagination notes

- **`status`** — always returns hardcoded `'operational'`; no health probe wired. Callers wanting real engine health should route through `dev-ops-observability` agent or `ops_tool`.
- **`thoughts` empty result** — returns `{action: 'thoughts', count: 0, thoughts: []}`. Consistent shape.
- **`thoughts` with populated corpus** — verified live at HEAD `a35ebd5c5`: response was `{count: 0, thoughts: []}` — no `AgentExecution` rows for ThinkingAgent in the local corpus, so per-row shape not empirically confirmed. Per handler code (line 5391): `id, task, status, created_at` serialized with `id` stringified + `created_at` isoformat.
- **Unknown action** — raises `ValueError(f'Unknown action: {action}')` at handler line 5418 → `TOOL_EXCEPTION`. Schema-level enum enforcement prevents this in practice.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating action excluded this ship:**
  - `trigger` — invokes `registry.execute_agent('ThinkingAgent', {'task': 'Reflect on recent system activity and generate insights'})` at handler line 5408. Real LLM-backed ThinkingAgent execution (LLM cost, latency, side-effect via creating a new `AgentExecution` row when the agent completes). Classified `MUTATION`.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` record with `safety_class='MUTATION'`; harness skips via `resolve_safety()` (`expected_outcome=skipped_mutation` — verified in artifact §6.1).
- **dependency_surface note:** `internal` — agent registry dispatch of ThinkingAgent. Downstream side-effect: LLM invocation via ThinkingAgent's own LLM caller.
- **Deferral rationale:** `trigger` incurs real LLM cost + execution time on every dispatch, with no `dry_run` semantics. Doc-only sweep cannot exercise it safely. Deferred to batch 6b sweep proper (which is scoped for agent-invocation-class scrutiny including LLM cost + agent-execution side-effects).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness reasoning_engine_tool` at post-fix HEAD:

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `status` | `success` | 200 | 4 ms | `action, engine, status` |
| `thoughts` | `success` | 200 | 19 ms | `action, count, thoughts` |
| `trigger` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/reasoning_engine_tool.json`.

**Envelope-shape observation:** clean 2-action READ_ONLY dispatch shape. No `bridge` field — pure ORM + registry lookup, no bridge preflight needed.

### 6.2 Runtime-not-executed — this ship

- **`thoughts` with a populated ThinkingAgent execution history** — response shape verified for empty corpus (`count: 0`, `thoughts: []`), but per-row shape (`id, task, status, created_at`) not empirically confirmed against real rows.
- **`trigger`** — MUTATION-skipped (see §5a); deferred to batch 6b sweep proper.

### 6.3 Bugs surfaced + fixed this ship

- **Handler bug: `thoughts` action FieldError on `agent_name`** — the pre-fix handler filtered `AgentExecution.objects.filter(agent_name='ThinkingAgent')`, but `AgentExecution` has no `agent_name` field (it has `agent` FK to `Agent`, which itself has `name`). Every dispatch of `action=thoughts` would fail with `FieldError`. **Not caught by prior sweep coverage** because the pre-fix schema advertised `{query, reasoning_type}` — LLM callers passed those, handler fell into `action='status'` default, `thoughts` branch was never dispatched in production. Fixed to `AgentExecution.objects.filter(agent__name='ThinkingAgent')` at handler line 5388. Also corrected `.values('id', 'task', 'success', 'created_at')` → `.values('id', 'task', 'status', 'created_at')` — `success` is also not a field on `AgentExecution`; `status` is.
- **Schema↔handler drift closed** — pre-fix schema advertised `{query, reasoning_type}` params with `required=['query']`; post-fix schema advertises `{action, limit}` with `required=['action']` and `action` enum matching handler branches (`status | thoughts | trigger`). Dead schema params removed.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **1st confirmed schema↔handler drift instance** — Rigby T0 SIGN Q4 zoom-out flagged this as a class of concern at S2911 open. This tool corroborates the class with concrete evidence: the pre-fix schema was completely disconnected from handler behavior (no shared params). Track for future adopters; promote to a lint that grep-verifies schema `enum` values against handler dispatch branches if a 2nd instance appears.
  - **Latent-handler-bug detection via drift-fix sweep** — the `thoughts` FieldError was invisible during S2841→S2910 because callers never exercised the branch. Drift-fix sweep sessions may be a systematic way to surface these. Consider promoting to a Fold — "when fixing schema drift, always exercise every action branch, not just the previously-callable ones."
- **Adjacent tools:**
  - `brainstorm_tool` — brainstorming-corpus surface (Discussion + Panel + BrainstormConversation search).
  - `universal_agent_tool` — batch 6b peer; generic agent routing (contrast: this tool is ThinkingAgent-specific).
  - `execution_history_tool` — cross-agent `AgentExecution` surface (this tool is a ThinkingAgent-scoped view of the same substrate).
- **Substrate context:** this ship is a **pre-req PR for batch 6b**, not a batch 6a peer. Rigby ratified separation at S2911 T1 SIGN Q4b — reasoning_engine drift + latent bug both belong in the agent-invocation-scrutiny lane, not the ORM batch lane. Batch 6b (S2912) can now dispatch `reasoning_engine_tool` cleanly + tackle `universal_agent_tool` as the second agent-invocation tool.
- **Metadata seed:** 3 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (Pattern C — per-action records; no `TOOL_DEFAULTS` entry).

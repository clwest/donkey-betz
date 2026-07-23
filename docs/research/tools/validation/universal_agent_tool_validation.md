# `universal_agent_tool` — Validation Report (S2912)

**Tool:** `universal_agent_tool`
**Schema:** `core/services/pa_tool_schemas.py:853`
**Handler:** `core/services/td_handlers_agents.py:1771` (`_handle_universal_agent`)
**Register site:** `core/services/tool_dispatcher.py:401`
**Session:** S2912 (Slice 2 batch 6b — Slice 2 close; agent-invocation-class dispatcher peer of `reasoning_engine_tool` shipped as batch 6b pre-req at S2911).
**HEAD at validation:** `2ba026c4d` (2026-07-23; S2911 close-cascade merge parent).
**Ship shape:** Doc-only (S2796 shape) + `TOOL_DEFAULTS` metadata seed. Post-merge verification is contract-level + worker recycle freshness per PLAYBOOK-7.4.4; NO live dispatch (see §5a).
**Category upgrade target:** intent `validated_partial` (contract-level alignment verified; live-fire dispatch explicitly excluded — see §5a). **Classifier ceiling reached:** `validated (full)` — actionless tools with any `## Covered actions` heading auto-classify as full per `core/services/pa_tools_gap_map.py:439-442` (no downgrade path exists for no-live-fire actionless tools without a `dry_run` infra add). Same precedent as `legal_doc_drafter_agent`, `web_fetch_tool`, `schedule_followup`.
**Rigby SIGN:** S2912 T0 SIGN Q1 AGREE (solo-ship 1-tool batch) + Q2 AGREE-with-edits (`TOOL_DEFAULTS` MUTATION conditional, tighten applicability to `conditional`) + Q3 AGREE-with-edits (contract-only; reject `task='noop'` — no handler-side noop path) + Q4(a) uniformity claim ratified with error-envelope caution + Q4(b) methodology assumption validated. Chris ratified Option A (contract-only; no `dry_run` add) at S2912 open.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Route a task to a specific agent by name or auto-route to the best-fit agent from the AGENT_MAP registry. Answers "have <AgentName> do <task>" and "have someone handle <task>" (when no other specialized PA tool fits the request).

Distinct from `reasoning_engine_tool` (batch 6b pre-req peer) which is bound to `ThinkingAgent` + the reasoning-cycle domain. `universal_agent_tool` is the generic router into all 74 enabled AGENT_MAP entries. Distinct from `agent_tool` (`_handle_agent_tool` in `tool_dispatcher.py`) — this handler is the "no schema constraint on `agent_name` value" variant that GPT-5.2 keyword-routes to when no other tool fits. When Rigby has an explicit agent target, prefer this tool for its uniform substitution envelope (`agent_name_requested/effective/substituted`).

## Covered actions

**Actionless schema** — no `action` enum. Single dispatch verb (async agent invocation via Celery). Coverage is at the tool level, not per-action.

- `<dispatch>` — **contract-level in scope; live dispatch NOT executed** — schema/handler/metadata alignment verified statically. Live-fire excluded because handler always enqueues a real Celery task (see §5a). Ship claim: contract-uniform substitution envelope + async task_id envelope + MUTATION safety classification.

## 3. Schema notes

- **Required:** `task` (string).
- **Optional (schema-declared):** `agent_name` (string; specific AGENT_MAP class name), `context` (object; passed through to agent).
- **Optional (promoted at handler layer, not declared in schema):**
  - `content` (string) — promoted into `context['content']` if not already present (`td_handlers_agents.py:1797-1799`). Session 1094 pattern — GPT-5.2 unreliable at packing arbitrary fields inside `context` blob.
  - `workspace_id` (string) — promoted into `context['workspace_id']` (`:1800-1802`).
  - `conversation_id` (string) — promoted into `context['conversation_id']` (`:1810-1812`). Session 1174 PR-1 — without this promotion `AgentExecution.conversation_id` persists NULL and follow-up-wake design silently opts out.
  - `auto_followup` (bool) — promoted into `context['auto_followup']` if present (`:1818-1819`). Session 1178 Phase 2. False is meaningful (skip auto-sub); membership-tested rather than truthiness.
- **Auto-substitution behavior** (`:1831-1866`):
  - `agent_name` with `_` → snake-case tool name detected → converted via `self._tool_to_agent_name(agent_name)`.
  - `agent_name` not in `router.AGENT_MAP` → scan `task_text` for any AGENT_MAP name → substitute if found (WARN log + envelope surfaces `substitution_reason`); else fall back to `ResearchAgent`.
  - Empty `agent_name` → auto-route from `task_text`; ultimate fallback `ResearchAgent`.
- **No `action` enum** — schema is actionless; do not add per-action `TOOL_ACTION_METADATA` records. Seed uses `TOOL_DEFAULTS` (`core/services/tool_action_metadata.py` batch 6b block).

## 4. Golden-path examples

**"Have ContentStrategyAgent write a blog post about X:"**

```
universal_agent_tool  agent_name=ContentStrategyAgent  task="Write a blog post about X"
```

Response shape:
```json
{
  "task_id": "<uuid>",
  "mode": "async",
  "agent": "ContentStrategyAgent",
  "agent_name_requested": "ContentStrategyAgent",
  "agent_name_effective": "ContentStrategyAgent",
  "agent_substituted": false,
  "auto_routed": false,
  "auto_followup": true,
  "follow_up_will_fire": false,
  "message": "ContentStrategyAgent dispatched (task <uuid>). Use job_status to check progress."
}
```

**"Have someone handle this analysis:"** (auto-route from task text)

```
universal_agent_tool  task="Analyze recent Bitcoin price movements"
```

Response shape: `auto_routed=true`; `agent_name_effective` extracted from AGENT_MAP by task-text scan (or `ResearchAgent` fallback).

**"Have research_agent look into Y:"** (snake-case name coerced)

```
universal_agent_tool  agent_name=research_agent  task="Look into Y"
```

Handler applies `_tool_to_agent_name()` → `ResearchAgent`. `agent_substituted` behavior: FALSE if the coerced name matches (`_agent_name_requested` still holds `research_agent`, `agent_name_effective` = `ResearchAgent`; the equality check at `:1886-1889` compares raw request against effective and flags TRUE). NOTE: this is the current handler contract; per-invocation truth of `agent_substituted` depends on whether the coercion produces a string-identical result to the requested name.

## 5. Failure / empty-state / pagination notes

- **Empty `task`** — raises `ValueError("task is required")` at `:1821-1823`. Maps to standard `TOOL_EXCEPTION` envelope via outer dispatcher.
- **Unknown `agent_name` with no task-text match** — WARN-logged; `agent_name_effective='ResearchAgent'`; `substitution_reason` populated on envelope with detail. Dispatch proceeds (not an error state).
- **Celery queue unavailable** — `apply_async` failure would surface as broker exception; not handler-caught. Requires `long_running` queue active per `Procfile`. Local: `make celery` or `make recycle-all`.
- **Downstream agent failure** — this handler returns synchronously with the `task_id`; agent execution result is NOT part of this tool's response envelope. Callers should poll `job_status` (or subscribe via `schedule_followup` when `conversation_id` is available).
- **No pagination** — single-verb dispatch.

## 5a. Mutation containment (per Rigby T0 SIGN Q3 — mandatory §5a)

- **Mutating behavior:** every dispatch with a non-empty `task` unconditionally enqueues `execute_agent_task.apply_async(agent_name, task_text, context, queue='long_running')` at handler `:1872`. No `dry_run`, no `noop` fast-path, no cost gate.
- **Blast radius:** dispatch resolves through the full agent execution path — LLM invocations, potential DB writes, potential spider dispatches, potential external API calls. Exact side effects depend on the resolved agent's implementation. Fan-out surface: all 74 enabled AGENT_MAP entries reachable through this single tool.
- **Containment mechanism:** `TOOL_DEFAULTS` entry with `default_safety_class='MUTATION'`, `default_applicability='conditional'` (`core/services/tool_action_metadata.py` batch 6b block). Harness `resolve_safety()` classifies dispatches as `skipped_mutation` (metadata-driven skip) rather than executing.
- **Deferral rationale for live-fire test:** Rigby T0 SIGN Q3 confirmed there is no runtime input that guarantees "no expensive downstream work" for this tool — the handler always enqueues (`:1821-1823` + `:1872`). The only genuine no-work path is either (a) mocking `apply_async` in a test harness (not a live-dispatch check), or (b) adding a `dry_run` schema/handler flag (a behavior change — Chris ratified NOT adding it at S2912 open). Post-merge verification is therefore contract-level (schema/handler/metadata alignment) + worker recycle freshness per PLAYBOOK-7.4.4, NOT live dispatch.
- **Note on adding `dry_run` later:** ~10-line same-shape mitigation available if a future session wants live-fire testability: (i) add `dry_run: bool` to schema properties; (ii) wrap the `apply_async` call at `:1872` behind `if not payload.get('dry_run'):`; (iii) return the envelope with a stub `task_id` (e.g., `'dry-run'`) when `dry_run=True`. Not in scope this ship.

## 6. Evidence

### 6.1 Contract-level alignment — this ship

Static verification (no live dispatch — see §5a):

| Contract layer | Verified | Evidence |
|---|---|---|
| Schema `required=['task']` | ✓ | `pa_tool_schemas.py:866` |
| Schema properties = `{task, agent_name, context}` (actionless) | ✓ | `pa_tool_schemas.py:861-865` |
| Handler dispatch is actionless (no `payload.get('action')`) | ✓ | `td_handlers_agents.py:1771-1907` |
| Handler enqueues unconditionally on non-empty task | ✓ | `:1821-1823` (guard) + `:1872` (apply_async) |
| Substitution envelope surfaces `agent_name_requested/effective/substituted, auto_routed, substitution_reason` | ✓ | `:1890-1907` |
| Async envelope surfaces `task_id, mode='async', message` | ✓ | `:1890-1904` |
| `TOOL_DEFAULTS` seed `safety_class='MUTATION'`, `applicability='conditional'` | ✓ | `tool_action_metadata.py` batch 6b block |
| Register site invokes `_handle_universal_agent` | ✓ | `tool_dispatcher.py:401` |

### 6.2 Runtime-not-executed — this ship

- **Live agent dispatch** — MUTATION-skipped per §5a; contract-level classification instead. Not planned under the current sweep without a `dry_run` mitigation first landing (future planning is scope-dependent, not enumerated here).
- **Substitution path exercise** — auto-route + snake-case coercion + AGENT_MAP-miss paths verified in handler code by grep + read (`:1831-1866`); no live invocation.

### 6.3 Post-merge verification (per PLAYBOOK-7.4.4)

- `make recycle-all` after merge (rebooted workers pick up TOOL_DEFAULTS seed; validation doc is not code-loaded).
- Grep verification: `grep -n "'universal_agent_tool'" core/services/tool_action_metadata.py` returns the new TOOL_DEFAULTS entry.
- Gap-map refresh: `PA_TOOL_AUDIT.md` regenerates with `universal_agent_tool` moved from `untested` to `validated_partial` (contract-only).

---

## Related

- **Slice 2 close:** this ship closes `td_handlers_agents.py` sweep at 25/25 tools. Slice 3 (`td_handlers_core`, 22 tools) opens next.
- **Rigby T0 SIGN Q4(a) coherence claim ratified (with caution):** all 25 handlers in `td_handlers_agents.py` now have auditable safety classification entries + uniform substitution transparency for dispatch-style tools. **Caution:** do not overclaim "uniform error envelopes across all 25 tools" without separately verifying the outer dispatcher's exception normalization — this handler only raises `ValueError("task is required")` at `:1821-1823`; envelope normalization is upstream.
- **Rigby T0 SIGN Q4(b) methodology assumption validated (contract-only close) with limit exposed:** small-file slices (<30 tools) closable at ~8-11-session accelerated pace with trustworthy harness holds true *for contract-level closure*. This close does NOT extend the validation to live-fire coverage of mutation-class dispatchers — that remains an open limit. `universal_agent_tool` was the highest-risk stress test in Slice 2 (fan-out to 74 agents; async dispatch; no dry_run); methodology handled it via contract-level SIGN close + explicit runtime-not-validated statement, and the ship itself surfaces the "no safe live-fire without dry_run or infra" gap for future planning. If invalidated in a subsequent slice, the harness would need either (i) dry_run flag additions across mutation-class dispatchers, or (ii) queue blackhole / worker-side dispatch-but-don't-run infrastructure.
- **Adjacent tools:**
  - `reasoning_engine_tool` (S2911 pre-req PR) — ThinkingAgent-specific batch 6b peer; contrast this generic router.
  - `agent_tool` (`_handle_agent_tool` in `tool_dispatcher.py`) — sister dispatcher with `_CONTEXT_PROMOTE_KEYS` (this handler doesn't share; promotes `content, workspace_id, conversation_id, auto_followup` explicitly instead — `:1791-1819`).
  - `execution_history_tool` — read side of the AgentExecution substrate this handler writes to.
- **Ledger candidates surfaced this ship:**
  - Contract-only validation shape for mutation-class dispatchers with no dry_run — Rigby T0 SIGN Q3 established this as the current default. If a future mutation dispatcher lands without dry_run + Chris wants live-fire testability, promote the `dry_run` add-flag pattern (§5a note) into a same-PR mitigation rule.
- **Metadata seed:** 1 `TOOL_DEFAULTS` entry at `core/services/tool_action_metadata.py` batch 6b block (actionless — no per-action `TOOL_ACTION_METADATA` records).

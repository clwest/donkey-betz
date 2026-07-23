# `persona_tool` — Validation Report (S2913)

**Tool:** `persona_tool`
**Schema:** `core/services/pa_tool_schemas.py:1426`
**Handler:** `core/services/td_handlers_core.py:1189` (`_handle_persona`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 1 of `td_handlers_core`)
**HEAD at validation:** `cff587f50` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 1 MUTATION action `invoke` explicitly excluded — see §5a).
**Rigby SIGN:** S2913 T0 SIGN AGREE-with-edits (batch 1 composition ratified). S2913 T1 SIGN AGREE-with-edits (V1 side-effect-free scan clean + V2 explicit `action="list"` pinning applied to defend against default-drift risk).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Access 139 DB-only persona agents (as of Session 1088) across ~14 categories — income, career, job_search, content, marketing, finance, investment, ai_ml, business, analytics, creative, automation, consulting, research. `list` browses; `invoke` delegates a task to a specific named persona.

Distinct from `agent_control_tool` / `agent_introspection_tool` (which manage the ~74-enabled AGENT_MAP core agents). `persona_tool` explicitly *excludes* AGENT_MAP names from the `list` result via `qs.exclude(name__in=AgentRouter.AGENT_MAP.keys())` — it surfaces the DB-only long tail (specialized personas without a hand-rolled AGENT_MAP class), which route through the `DynamicPersonaAgent` fallback.

## Covered actions

**READ_ONLY actions covered only (1 of 2 total actions).** 1 MUTATION action (`invoke` — excluded — see §5a) is out of scope for this ship.

- `list` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 14 ms). Returns `{action, filter, count, personas, categories}` — top-50 DB personas sorted by `(agent_type, name)` with descriptions truncated to 150 chars, plus a `Counter` over all `agent_type` values as `categories` summary.
- `invoke` — **mutation — deferred to future MUTATION-coverage batch** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `list, invoke`).
- **Conditional required (handler-enforced, per action):**
  - `persona_name` for `invoke` — inline `{error}` if missing.
  - `task` for `invoke` — inline `{error}` if missing.
- **Optional (`list`):** `category` (enum: `income, career, job_search, content, marketing, finance, investment, ai_ml, business, analytics, creative, automation, consulting, research`) — filters personas by `agent_type` field.
- **Optional (`invoke`):** `context` (dict, passed to `AgentRouter.route`).
- **Category count of 14** is enum-declared in the schema; the runtime `categories` summary reflects actual DB `agent_type` distribution and may be smaller if some categories are unpopulated.
- **AGENT_MAP exclusion is a HANDLER-LEVEL filter, not schema-level.** The `list` handler at `td_handlers_core.py:1207-1208` always applies `qs.exclude(name__in=map_names)` — this exclusion is behavioral, not a param.

## 4. Golden-path examples

**"What personas can I invoke?"**

```
persona_tool  action=list
```

Returns top-50 personas + full `categories` count summary.

**"Show me AI/ML personas:"**

```
persona_tool  action=list  category=ai_ml
```

**"Invoke a specific persona:"** *(NOT exercised this ship — see §5a)*

```
persona_tool  action=invoke  persona_name="<name from list results>"  task="<task description>"
```

## 5. Failure / empty-state / pagination notes

- **`list` with unpopulated category** — returns `{action, filter, count: 0, personas: [], categories}`. Consistent shape; empty persona list.
- **`list` result cap** — always top-50 by `(agent_type, name)`. There is NO `limit` param + NO pagination cursor + NO `has_more` flag. Callers wanting the full 139-row list cannot get it in one call — this is a documented limit, not a bug. Description truncation at 150 chars is also applied to keep response payload bounded for LLM context.
- **`invoke` missing `persona_name`** — returns `{'error': 'persona_name is required for invoke action'}`. Inline `{error}` envelope, not raise.
- **`invoke` missing `task`** — returns `{'error': 'task is required for invoke action'}`. Inline `{error}` envelope.
- **`invoke` unknown or inactive persona** — returns `{'error': f'Persona "{persona_name}" not found or inactive'}`. Inline `{error}` envelope.
- **Unknown action** — returns `{'error': f'Unknown persona action: {action}'}` at handler line 1270. Inline `{error}` envelope, not raise.

## 5a. Mutation containment (per Rigby T0/T1 SIGN — explicit action pinning)

- **Mutating actions excluded this ship:**
  - `invoke` — routes through `AgentRouter.route(persona_name, task, context)` which invokes real LLM-backed persona execution via the `DynamicPersonaAgent` fallback. LLM cost per call; may trigger downstream side effects depending on the specific persona's implementation (some personas write to DB via their agent class). Classified `MUTATION` in `TOOL_ACTION_METADATA` seed this ship. Not classified `IRREVERSIBLE` because a single `invoke` does not destroy state; but repeat invokes accrete LLM cost and potentially agent-side-effect rows.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` record with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch (`expected_outcome=skipped_mutation`).
- **dependency_surface note:** `internal + LLM` — `AgentRouter` is in-process; the LLM call is external OpenAI-family; individual persona agent classes may have their own dependencies (spider dispatch, ORM writes, etc.) — surfaced-as-black-box until per-persona validation.
- **Deferral rationale:** live LLM cost + fan-out to any of 139 personas + potential downstream side effects. Doc-only sweep cannot exercise safely. Deferred to a future MUTATION-coverage batch that pairs with a `dry_run` / cost-cap harness pattern (peer to `universal_agent_tool` §5a at S2912). Actionless-tool overlap: `universal_agent_tool` covers arbitrary AGENT_MAP dispatch; `persona_tool.invoke` covers the AGENT_MAP-EXCLUDED subset — the two together cover the full agent-invocation surface.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness persona_tool` at HEAD `cff587f50` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list` | `success` | 200 | 14 ms | `action, filter, count, personas, categories` |
| `invoke` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/persona_tool.json` — 1 READ_ONLY dispatched + 1 MUTATION skipped.

**Envelope-shape observation:** `list` returns clean success at HTTP 200 with the full 5-key response envelope. `invoke` cleanly metadata-skipped without handler invocation. No inline `{ok: false}` envelope drift observed on the READ_ONLY subset — invoke's error paths (missing `persona_name` / `task` / inactive persona) DO use inline `{error}` envelopes (see §5), which is the drift-shape flagged as a broader ledger candidate but NOT specific to this tool.

### 6.2 Runtime-not-executed — this ship

- **`list` with a specific `category` filter** — not exercised (would confirm category filter passes to the `agent_type` filter).
- **`list` with real persona rows** — the harness ran against the local DB; `count` and `personas` echo whatever's currently populated. Real-world persona shape (specialization + effectiveness_score + total_executions) exercised via the DB state at test time.
- **`invoke`** — MUTATION-skipped (see §5a). Full LLM+`AgentRouter` execution path not exercised.

---

## Related

- **Adjacent tools:**
  - `universal_agent_tool` (S2912) — arbitrary AGENT_MAP dispatch (74 enabled agents); the AGENT_MAP-INCLUDED counterpart to persona_tool.
  - `agent_control_tool` / `agent_introspection_tool` — control-plane operations on AGENT_MAP agents (start/stop/status); different concern from persona-level invocation.
  - `platform_awareness_tool.tool_registry` (batch 1 peer) — enumerates PA tool schemas; different concern from persona enumeration.
- **Substrate context:** batch 1 peer of `paid_interest_status` (actionless), `platform_awareness_tool` (7 actions), `platform_config_tool` (5 actions). All 4 tools no-network, no-Celery, no-writes on selected actions; siblings excluded via per-action `TOOL_ACTION_METADATA`.
- **Metadata seed:** 2 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (mirrors S2911 batch 6a shape; no `TOOL_DEFAULTS` entry). Batch-uniform per-action pattern per Rigby T1 V2 explicit-action-pinning directive.
- **Session 1088 provenance:** the 139 DB-only persona count + AgentRouter.DynamicPersonaAgent fallback + the 14-category taxonomy are all Session 1088 arc.
- **AgentRouter.AGENT_MAP boundary:** this tool's `list` handler explicitly excludes AGENT_MAP names via `qs.exclude(name__in=AgentRouter.AGENT_MAP.keys())` at `td_handlers_core.py:1207-1208` — the exclusion is the semantic distinction from AGENT_MAP-facing agent tools. If AGENT_MAP grows or shrinks, the visible persona set changes with no code edit here.

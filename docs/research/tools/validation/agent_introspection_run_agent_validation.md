# `agent_introspection_tool` + `run_agent` — Validation Report

**Tools:** `agent_introspection_tool` + `run_agent` (meta-tool).
**Schemas:**
- `agent_introspection_tool` → `core/services/pa_tool_schemas.py:581-603`
- `run_agent` → `core/services/pa_tool_schemas.py:1069-1211`

**Register site:** `core/services/tool_dispatcher.py:418` (`agent_introspection_tool`); `run_agent` is a **meta-tool** intercepted at PA entrypoint level.

**Main handlers:**
- `_handle_agent_introspection` → `core/services/td_handlers_ops.py:4012-4300+`
- `_handle_agent_tool` (per-agent dispatch, invoked after run_agent → actual_tool_name rewrite) → `core/services/tool_dispatcher.py:1079-1223`

**Meta-tool interception:** `core/services/unified_pa_entrypoint.py:2067-2070` — pops `agent_name` from payload; dispatches under that name via `ToolDispatcher.execute(tool_name=actual_tool_name, ...)`.

**Downstream:**
- `execute_agent_task` (Celery) → `core/tasks_agents.py`
- `create_implicit_followup_subscription` → `core/tasks_agents.py:263` — the `auto_followup=False` gate lives here.

**Session validated:** S2728 (Batch A tool 5 of 5).
**HEAD at validation:** `9d158805` + Batch A tools 1-4 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (regression tests suffice).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch A tool 5 of 5). Trace + 3 patches (F-RA-1 across two handlers, F-RA-2/F-RA-3, F-AI-2) + regression tests complete; 13 new regression tests + 23 existing auto_followup tests + 211 Batch A cross-tool regression tests all passing.

---

## 1. Intended purpose

- **`agent_introspection_tool`** — describe the platform's agent surface: list registered agents, view capabilities, aggregate stats, list all PA tool schemas.
- **`run_agent`** — meta-tool for delegating a task to a specialized agent. Rigby's primary route for dispatching any of the 58 enumerated agents across 10 domains.

## Covered actions

Coverage for `agent_introspection_tool` (5 actions in schema enum). `run_agent` is meta-tool (no `action` enum; dispatched via `agent_name` rewrite at PA entrypoint) — see §3.2 for its call shape.

- `list` — read — enumerates registered agents from `AGENT_MAP`. Returns `{agents, total_count, filters_applied}`.
- `stats` — read — aggregate agent counts + status breakdown across AGENT_MAP + Agent DB rows.
- `details` — read — full detail for one agent (name required). Returns capability listing + provenance + recent-execution stats.
- `capabilities` — read — enumerates capability tags across the agent registry.
- `tools` — read — enumerates all PA tool schemas registered in `PA_TOOL_SCHEMAS`. Used by Rigby to introspect her own tool surface.

## 2. Rigby's belief (per MEMORY + prior conversations)

Rigby's load-bearing beliefs from MEMORY:

- **`feedback_auto_followup_false_suppresses_banner`** — when Rigby passes `auto_followup: False` on `run_agent`, no `AgentFollowupSubscription` arms and no completion banner appears in the Chat UI. Correct for forensic dispatches; wrong for normal conversation. The MEMORY rule specifically calls out: *"Before chasing WS/daphne/consumer issues on 'missing banner' reports, check `AgentExecution.input_data['context']['auto_followup']` — Session 1184 lost ~30min on this."*
- **`feedback_llm_autofills_boolean_params_with_false`** — general LLM autofill pattern. `auto_followup` is a boolean; declared default is `True` in schema; but LLM may autofill `False` when caller didn't specify.

## 3. Schema claim (verbatim capture)

### 3.1 `agent_introspection_tool`

- **Required:** `action` (enum: `list`, `stats`, `details`, `capabilities`, `tools`).
- **Optional:** `agent_name`, `limit` (default 20).

### 3.2 `run_agent`

- **Required:** `agent_name` (58-value enum), `task`.
- **Optional:** `workspace_id`, `content`, `context` (object), `auto_followup` (boolean, default `True`).

## 4. Handler behavior (traced)

### 4.1 `_handle_agent_introspection` (td_handlers_ops.py:4012-4300+)

- Line 4029: `action = payload.get('action', 'inspect')` — **DEFAULT `'inspect'`** despite schema `required` (**F-AI-1**, batch-close class).
- Line 4031-4032: `ACTION_ALIASES = {'detail': 'details', 'inspect': 'details'}` — Session G3 alias normalization. `'inspect'` and `'detail'` both fold to `'details'`. Schema declares only `'details'` — aliases undocumented (**F-AI-BC-1**, batch-close).
- Line 4033: `agent_query = payload.get('agent_name', '').strip().lower()`.

**Action: `tools`** (line 4036-4056) — lists all PA tool schemas. Response has `total_tool_schemas` + `tools[]`.

**Action: `list` / `stats`** (line 4059-4158) — aggregate + optional top-50 preview.
- Line 4076-4081: `active_last_7d` computed from `AgentExecution` last 7 days, excluding `PersonalAssistant` (Arc I-0100 P4 §4.2 F1 fold).
- Line 4089-4129: **Robust try/except** — S1083 fix. If AGENT_MAP/blocked-list import fails, logs warning; response shows zero counts. Not silent — the log fires.
- Line 4133: **Reconciliation invariant** — `blocked + rerouted + fully_enabled = router_routable_total`.
- Line 4135-4148: response includes `requested_action`, `effective_action`, `total_agents_db`, `active_last_7d`, `router_routable_total`, `blocked_count`, `blocked_agents`, `rerouted_count`, `rerouted_agents`, `fully_enabled_count`, `reconciliation` (string), `by_agent_type`. Good surface.
- Line 4151-4156: `list` action adds `.order_by('-effectiveness_score', 'name')[:50]` — **HARD CAP AT 50**. Ignores `limit` schema param (default 20). **F-AI-2** (analog of F-KB-1, F-D-5, F-S-3). MEDIUM.

**Action: `details` / `capabilities`** (line 4162+):
- Line 4167-4176: fuzzy-search agent by name — exact, contains, cleaned (strip "agent" suffix).
- Line 4178-4190: not-found path returns `found: False, query, message, suggestions` — good typed shape, no `ok: false`.
- Line 4196-4210+: reads recent execution stats + agent class metadata. Well-structured.

### 4.2 `_handle_agent_tool` (tool_dispatcher.py:1079-1223)

Invoked when `run_agent` → `actual_tool_name` rewrite dispatches to a per-agent tool (e.g., `research_agent`, `content_writer_agent`).

- Line 1105: `agent_name = self._tool_to_agent_name(tool_name)` — maps tool name to canonical Agent class name.
- Line 1107: task extracted from `task` / `prompt` / `query` — 3-alias fallback (like claude_code_tool F-CC-1). **F-RA-BC-1** batch-close.
- Line 1108-1116: `context` extracted; `_CONTEXT_PROMOTE_KEYS` includes `auto_followup` (line 1076) — promoted from payload root into `context` if not already there.
- Line 1120-1133: EditorAgent synthesis-reroute (S1098 Fix A).
- Line 1150-1181: EditorAgent content-gather + provenance capture. S1177 F3 (C1+C2) provenance discipline is IN PLACE. Good.
- Line 1188-1200: ContentWriterAgent research injection.
- Line 1208-1209: `apply_smoke_allowlist(context)` — S1213 smoke-context minimization.
- Line 1213: `celery_task = execute_agent_task.apply_async(args=[...], queue='long_running')`.
- **Line 1215-1223: response = `{'task_id', 'mode', 'agent', 'message'}`** — **NO `auto_followup` echo. NO `follow_up_will_fire` signal.** **F-RA-1** — the MEMORY-crystallized silent behavior. Analog of F-CC-3. MEDIUM.

### 4.3 Meta-tool interception (`run_agent`, unified_pa_entrypoint.py:2067-2070)

```python
actual_tool_name = tool_name
if tool_name == 'run_agent':
    actual_tool_name = arguments.pop('agent_name', tool_name)
```

- If `agent_name` missing from arguments, `actual_tool_name` stays as `'run_agent'` — which has NO registered handler → dispatch fails with `TOOL_NOT_FOUND` (typed error).
- Schema-required `agent_name` enum enforcement is at LLM boundary only; direct-dispatch bypass has no defense. But typed-error at dispatch is a reasonable safety net.

### 4.4 `_handle_universal_agent` alternate path (td_handlers_agents.py:988+)

This is `universal_agent_tool` (not the same as run_agent), but shares the response shape family:
- Line 1021-1022: promotes `auto_followup` from payload to context (S1178 Phase 2).
- Line 1035-1047: **Silent agent-name substitution** — if provided agent_name isn't in AGENT_MAP AND task-text-extraction fails, defaults to `'ResearchAgent'` (line 1046-1047). Warn log fires, response is silent. **F-RA-2** (analog of F-D-2/F-D-4 silent inference).
- Line 1050-1056: When no `agent_name` provided, auto-routes by task-text keyword match, falling back to `'ResearchAgent'`. **F-RA-3** (same silent-substitution class).
- Line 1069: **DOES include `auto_routed: not payload.get('agent_name')`** in response. Rigby can detect auto-routing. **BUT does not surface the substitution when a name WAS provided but was corrected.**

### 4.5 Follow-up subscription gate (tasks_agents.py:258-264)

```python
if execution_record is None:
    return
conv_id = getattr(execution_record, 'conversation_id', None)
if not conv_id:
    return  # Non-PA dispatch; PR-1 gate.
if context.get('auto_followup', True) is False:
    return  # Explicit per-call opt-out.
```

**Truthy-check is defensive** — line 263 uses `is False` (not falsy) to distinguish explicit False from None/missing. This preserves the "auto_followup defaults to True" invariant even if LLM autofills None. Good — matches S1178 P2 design. Verified in `test_auto_followup_subscription.py::test_opt_out_only_triggers_on_false_not_falsy`.

But: the dispatch response doesn't surface WHICH state we're in, so Rigby can't diagnose ex-post.

## 5. Defaults inventory

### `agent_introspection_tool`

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `action` | required | defaults to `'inspect'`, aliased to `'details'` | schema violation — F-AI-1 |
| `agent_name` | Optional | `.strip().lower()`; safe | matches |
| `limit` | default 20 | `list` action ignores; hard-coded `[:50]` slice | **F-AI-2** silent divergence |

### `run_agent` (via `_handle_agent_tool`)

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `agent_name` | required, 58-enum | validated against AGENT_MAP downstream; direct-dispatch bypass typed-errors | matches ✓ (LLM-side) |
| `task` | required | 3-alias fallback (`task`/`prompt`/`query`) | partial divergence (F-RA-BC-1 batch-close) |
| `workspace_id` | Optional | PA entrypoint auto-injects; handler promotes to context | matches |
| `content` | Optional | promoted to `context.content` | matches |
| `context` | Optional | default `{}`; promoted keys added | matches |
| `auto_followup` | boolean, default `True` | promoted to `context.auto_followup`; `is False` check (not falsy) | matches, BUT not echoed in response — **F-RA-1** |

## 6. Hidden filters

- **`agent_introspection_tool.list`** — hard cap 50 (F-AI-2).
- **`agent_introspection_tool.stats.active_last_7d`** — excludes `PersonalAssistant` per Arc I-0100 P4 §4.2 F1 fold. Documented in code comment; not surfaced in response.

## 7. Limits inventory

- `agent_introspection_tool.list` — hard cap 50 (**F-AI-2**).
- `agent_introspection_tool.details.suggestions` — hard cap 20 (line 4183). Not surfaced.
- `run_agent` — no limits at handler; Celery task has queue-side timeouts.

## 8. Silent-truncation test

- **F-AI-2** confirmed via code trace. Test target.

## 9. Silent-filter test

- `active_last_7d` PersonalAssistant exclusion — documented in code, not surfaced. Batch-close observation.

## 10. Silent-fallback test

- **F-RA-2 / F-RA-3** — silent substitution to `'ResearchAgent'` when agent_name unknown or task-text extraction fails. `universal_agent_tool` response has `auto_routed` field for the no-name case but NOT for the substituted-name case.
- Direct `_handle_agent_tool` response (invoked via run_agent → actual_tool_name rewrite) has NO substitution surface — but that handler dispatches to a specific agent tool name that was already routed by the schema enum. The substitution branch is `_handle_universal_agent`-only.

## 11. Staleness test

- `active_last_7d` counts based on rolling window. Freshness is inherent.

## 12. Freshness signal

- Response includes `active_last_7d` — window-based freshness surface. Good.

## 13. Provenance signal

- `_handle_agent_tool` response has `task_id`, `agent`, `mode` — sufficient to trace via `execution_history_tool`.
- **Does not surface `auto_followup` state** — the MEMORY-crystallized diagnostic gap. **F-RA-1.**

## 14. Authority / workspace assumptions

- PA entrypoint auto-injects `workspace_id` at dispatch time (unified_pa_entrypoint.py:2101-2113). `_handle_agent_tool` promotes to context.
- `_bound_conversation_id` sentinel injected by entrypoint but not read by these handlers.

## 15. Runtime dependencies

- Django ORM: `Agent`, `AgentExecution`, `AgentFollowupSubscription`.
- Celery `long_running` queue for agent execution.
- `AgentRouter.AGENT_MAP` registry.
- `PA_TOOL_SCHEMAS` for `tools` action.

## 16. Recoverable failure modes

- Unknown agent name → default to `'ResearchAgent'` with warn log (silent — F-RA-2).
- Empty task on `_handle_agent_tool` → NOT caught in the handler I read (line 1107 accepts empty). Let me re-check — actually the handler passes the empty task to `celery_task.apply_async` and the downstream agent handles the empty-task path.
- Unknown action on introspection → falls through to details path or returns not-found.

## 17. STOP-and-report failure modes

- Django DB exception → bubbles as `TOOL_EXCEPTION`.
- AgentRouter import failure → logs warning + shows zero counts (S1083 fix — no longer bare `pass`).

## 18. Operator-action failure modes

- `long_running` queue worker down → dispatches queue silently forever (analog of claude_code_tool queue-parity concern). Cross-checked: Procfile + Makefile — need to verify.

## 19. Existing test coverage

- `test_auto_followup_subscription.py` — 23 tests covering the subscription lifecycle (S1178 Phase 2 + S1180 P1 TTL); explicitly tests `context={'auto_followup': False}` opt-out AND the `is False` (not falsy) check. Task-side coverage is strong.
- **No test for the dispatch-response side of `auto_followup` visibility (F-RA-1).**
- **No test for `agent_introspection_tool.list` hard-cap 50 (F-AI-2).**

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/tool_dispatcher.py` | 1215-1240 | F-RA-1 | `_handle_agent_tool` dispatch response now echoes `auto_followup` (effective value) and `follow_up_will_fire: bool` mirroring F-CC-3 pattern; task-side gate logic replicated (conversation_id truthy AND auto_followup not-False). |
| `core/services/td_handlers_agents.py` | 1024-1030, 1039-1059, 1076-1109 | F-RA-1 + F-RA-2 + F-RA-3 | `_handle_universal_agent`: (a) tracks `_agent_name_requested` at handler entry; (b) captures `_substitution_reason` string in the AGENT_MAP-miss branches; (c) adds `agent_name_requested`, `agent_name_effective`, `agent_substituted: bool`, optional `substitution_reason`, plus F-RA-1 `auto_followup` + `follow_up_will_fire` fields to dispatch response. Preserves existing `auto_routed` and `agent` fields for back-compat. |
| `core/services/td_handlers_ops.py` | 4157-4180 | F-AI-2 | `_handle_agent_introspection` list branch declares `_AGENT_LIST_HARD_MAX = 50`, honors caller's `limit` (schema default 20) up to the cap, surfaces `limit_capped/requested_limit/effective_limit/hard_max` envelope + always-present `limit` field. Preserves prior ordering (`-effectiveness_score, name`). |

**Test files added:**

- `core/tests/test_agent_introspection_run_agent_validation_2728.py` — 13 regression tests across 3 test classes: `_handle_agent_tool` auto_followup echo (4 tests), `_handle_universal_agent` substitution + auto_followup (4 tests), `agent_introspection_tool.list` limit envelope (5 tests).

**MEMORY.md:**

- No new rules added. `feedback_auto_followup_false_suppresses_banner` remains VALID at HEAD — the MEMORY rule is about task-side subscription-gate behavior which is unchanged; the F-RA-1 patch adds a dispatch-time diagnostic so Rigby doesn't need to inspect `AgentExecution.input_data['context']['auto_followup']` after the fact.

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- Schema descriptions in `pa_tool_schemas.py` — pending Batch A close doc pass. All patches are additive to the response shape only; schemas unchanged.
- `docs/topics/personal-assistant.md` — pending Batch A close.

**Test verification:**

- `python manage.py test core.tests.test_agent_introspection_run_agent_validation_2728 core.tests.test_auto_followup_subscription --keepdb --noinput` → **36/36 pass** (2.917s).
- Full Batch A cross-tool regression sweep alongside tool 5 patches: **211/211 pass** (12.507s). Zero cross-tool interference.

---

## Findings

### F-RA-1 — `run_agent` dispatch response does not surface `auto_followup` state (MEDIUM)
- **Class:** DEFECT-CLASS-D2 (silent behavioral consequence). MEMORY-crystallized.
- **Evidence:** `tool_dispatcher.py:1215-1223`. Response has `task_id`/`mode`/`agent`/`message` — no `auto_followup` echo, no `follow_up_will_fire` boolean. MEMORY rule `feedback_auto_followup_false_suppresses_banner` documents ~30min lost on missing-banner debugging in Session 1184.
- **Severity:** MEDIUM. Rigby (and Chris) cannot detect at dispatch time whether the completion banner will fire.
- **Action:** PATCH — mirror F-CC-3 shape (Chris-approved at Batch A tool 4). Add `auto_followup: bool` (the effective state) + `follow_up_will_fire: bool` (composite of `conversation_id` truthy AND `auto_followup` not-False) to dispatch response. Regression test.

### F-AI-2 — `agent_introspection_tool.list` silently caps at 50 (MEDIUM)
- **Class:** DEFECT-CLASS-D10 (analog of F-D-5, F-KB-1, F-S-3).
- **Evidence:** `td_handlers_ops.py:4152-4156` — hard-coded `[:50]` slice; `limit` schema param ignored.
- **Severity:** MEDIUM. Rigby's list action responses were bounded at 50 with no cap signal.
- **Action:** PATCH — apply the same `limit_capped/requested_limit/effective_limit/hard_max` envelope pattern approved for F-D-5. Also honor caller's `limit` up to the cap. Regression test.

### F-RA-2 — `_handle_universal_agent` silent substitution to `'ResearchAgent'` (LOW-MEDIUM)
- **Class:** DEFECT-CLASS-D2 (silent action substitution — analog of F-D-2/F-D-4).
- **Evidence:** `td_handlers_agents.py:1035-1047` (unknown agent_name), `1050-1056` (no agent_name). WARN log fires but response does not surface the substitution.
- **Severity:** LOW-MEDIUM. `universal_agent_tool` DOES have `auto_routed` field for the no-name case; substitution-of-provided-name is uncovered.
- **Action:** BATCH-CLOSE observation OR Chris-decision candidate. Not urgent — WARN log gives operator signal; but response-side visibility is missing. Deferred to Batch A close unless Chris directs a per-tool patch.

### F-AI-1 — Handler defaults `action='inspect'` despite schema `required` (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED schema violation (analog of F-D-1, F-S-2, F-KB action default).
- **Action:** BATCH-CLOSE cross-tool observation.

### F-AI-BC-1 — Undocumented action aliases (`detail`→`details`, `inspect`→`details`) (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED alias set. Schema declares only `details` in enum.
- **Action:** BATCH-CLOSE doc-only pass.

### F-RA-BC-1 — `_handle_agent_tool` 3-alias task extraction (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED schema-vs-handler divergence (analog of F-CC-1).
- **Action:** BATCH-CLOSE cleanup.

---

## Rigby-safe assessment (post-patch)

- **R1 (no dangerous defaults):** MOSTLY CLEARED. Introspection action default violates schema (LOW — batch-close). `auto_followup` default `True` matches schema.
- **R2 (no silent action substitution):** CLEARED. F-RA-2/F-RA-3 patched — `agent_name_requested/effective` and `agent_substituted: bool` surface every substitution; `substitution_reason` string names the cause. F-AI-1 aliases remain batch-close.
- **R3 (no silent truncation):** CLEARED. F-AI-2 patched — list `limit` honored up to hard cap; `limit_capped` envelope fires above cap.
- **R4 (hidden filters surfaced):** PARTIAL (batch-close only — `PersonalAssistant` exclusion documented in code, worth surfacing at Batch A close).
- **R5 (workspace/authority carriage):** CLEARED.
- **R6 (freshness surface):** CLEARED.
- **R7 (provenance surface):** CLEARED. F-RA-1 patched — `auto_followup` + `follow_up_will_fire` echoed on both `_handle_agent_tool` (primary run_agent path) and `_handle_universal_agent` paths.
- **R8 (worker/env preconditions):** N/A at handler; deferred to Batch D.

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** both schemas (verbatim); `_handle_agent_introspection` all actions (list, stats, details, capabilities, tools); `_handle_agent_tool` full path including context promotion + EditorAgent gather + ContentWriter research injection + smoke-context minimization; `_handle_universal_agent` full path with silent-substitution branches; meta-tool interception at `unified_pa_entrypoint.py:2067-2070`; task-side auto-follow-up gate at `core/tasks_agents.py:258-264`.

**Findings summary:**

- **Valid at HEAD → patched:** F-RA-1 (auto_followup silent on both dispatch paths), F-RA-2/F-RA-3 (silent agent substitution), F-AI-2 (list hard-cap silent).
- **MEMORY rule status:** `feedback_auto_followup_false_suppresses_banner` remains VALID — task-side gate unchanged; F-RA-1 patch adds dispatch-time diagnostic so the ex-post `AgentExecution.input_data['context']['auto_followup']` inspection is no longer necessary.
- **Batch-close cleanup observations (deferred per Chris):** F-AI-1 (action default `'inspect'` vs schema `required`), F-AI-BC-1 (undocumented action aliases `detail`→`details`), F-RA-BC-1 (`_handle_agent_tool` 3-alias task extraction).

**Regression sweep at HEAD:**

- 13 new regression tests in `test_agent_introspection_run_agent_validation_2728.py`: **13/13 pass**.
- Existing auto_followup tests (23 in `test_auto_followup_subscription.py`): **23/23 pass** (2.917s combined 36-test suite).
- Full Batch A cross-tool sweep (tools 1-5 combined regression): **211/211 pass** (12.507s). Zero cross-tool interference.

**Rigby cross-check (§10.1 step 12):** deferred. All 3 patches are exercised by 13 deterministic regression tests using the exact PA dispatch paths with mocked Celery `.apply_async(...)`.

**Follow-ups filed:**

- Batch-close observations for cross-tool consistency (schema-required-vs-handler-default drift; multi-alias task extraction; error envelope `ok:` field consistency).

**Tool closure statement:** `agent_introspection_tool` + `run_agent` are VERIFIED at HEAD `9d158805` + 2728 patches. Rigby's agent-dispatch discipline is now diagnosable at dispatch time: she can detect (a) whether the auto-completion banner will fire, (b) whether the agent she requested is the one actually running, and (c) whether her `list` request was bounded by the hard cap. The MEMORY-crystallized `feedback_auto_followup_false_suppresses_banner` diagnostic gap (30min lost in S1184) is closed.

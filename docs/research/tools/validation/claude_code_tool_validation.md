# `claude_code_tool` — Validation Report

**Tool:** `claude_code_tool` (single-action task-dispatch tool).
**Schema:** `core/services/pa_tool_schemas.py:4664-4696`.
**Register site:** `core/services/tool_dispatcher.py:534`.
**Main handler:** `core/services/td_handlers_codejobs.py:330-378` (`_handle_claude_code`).
**Downstream:** `core/tasks.py:11809-11926` (`claude_code_engineer_task` @shared_task) → `core/services/claude_code_engineer.py` (`_create_engineer_execution_record`, `_persist_engineer_terminal_state`, `execute_engineering_task`).
**Queue routing:** `core/settings.py:1446` → `code_jobs`.
**Queue consumers:** `Procfile:32` (`code-worker: ... -Q code_jobs`), `Makefile:322` (`--queues=code_jobs`).
**Session validated:** S2728 (Batch A tool 4 of 5).
**HEAD at validation:** `9d158805` + Batch A tools 1-3 uncommitted patches.
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (regression tests suffice).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch A tool 4 of 5). Trace + 1 patch (F-CC-3) + 1 MEMORY annotation + regression tests complete; 6 new regression tests + 69 existing claude_code tests + 76 tool-1-through-3 regression tests all passing.

---

## 1. Intended purpose (per schema description)

*"Spawn an autonomous Claude Code engineering session that can read files, write code, create branches, and open PRs. Use when you need code changes, bug fixes, new features, or technical investigation that requires reading/modifying the codebase. Use request_mode='answer' for readonly Q&A about the codebase (no PR created); 'change' for code modifications; default 'auto' picks based on task verbs."*

## Covered actions

`claude_code_tool` has no `action` enum — single-entrypoint dispatcher. Coverage applies to the single call shape.

- `claude_code_tool` — dispatch — Celery `apply_async` to `claude_code_engineer_task` on `code_jobs` queue. Required: `task` (string). Optional: `conversation_id`, `workspace_id`, `request_mode` (auto/answer/change). Returns `{task_id, workspace_id_resolved, resolved_from}` envelope. Async — poll via `agent_job_status` or subscribe via `schedule_followup`.

## 2. Rigby's belief (per schema + MEMORY)

Rigby's load-bearing belief about this tool, from MEMORY rules:

- **`feedback_procfile_makefile_queue_parity`** — cites `claude_code_tool` as the crystallized instance of the silent-queue-forever failure mode. When `code_jobs` had a Procfile worker but no Makefile block, every Rigby dispatch sat in Redis untouched with no telemetry, no error, no visible failure. Root-caused at S1225→S1226.

She uses `claude_code_tool` as her sole route to spawn autonomous code work — every dispatch matters, and silent failures propagate to entire sessions of missed work.

## 3. Schema claim (verbatim capture)

**Required:** `task` (string).

**Optional (2):**
- `conversation_id` — target conversation for result post-back; defaults to current conversation.
- `request_mode` — enum `["auto", "answer", "change"]`; controls SYSTEM_PROMPT selection. `auto` (default) infers from task verbs.

## 4. Handler behavior (traced)

### 4.1 `_handle_claude_code` (td_handlers_codejobs.py:330-378)

- Line 333-340: **Multi-alias task extraction** — accepts `task`, `task_description`, `description`, `prompt`, `message`. Schema declares only `task`. **F-CC-1.**
- Line 341-347: fail-loud on empty task. Response is `{'error': ..., 'received keys: ...}` without `ok: false`. **F-CC-2** (batch-close class).
- Line 350-352: `conversation_id` from payload OR `self._conversation_id` attribute. **`_conversation_id` legacy attribute** — I don't see explicit assignment, similar to session_tool F-S-4 pattern.
- Line 359: `request_mode = (payload.get('request_mode') or 'auto').strip().lower()` — coerces to string, lowercases, defaults to `'auto'`.
- Line 362-367: `claude_code_engineer_task.delay(...)` — dispatches to Celery `code_jobs` queue via routing at `core/settings.py:1446`.
- Line 369-378: response includes `status: 'dispatched'`, `task_id`, `request_mode`, `message`. No `ok: true`, no `conversation_id`, no `follow_up_arms` signal. **F-CC-3** (missing conversation_id has silent behavioral consequences).

### 4.2 Task execution path (tasks.py:11809-11926)

- Line 11809-11816: `@shared_task` decorated with `soft_time_limit=5400`, `time_limit=5460`, `max_retries=0`, `acks_late=False`. Session 1262 discipline: **the expensive LLM run is NEVER auto-retried on failure** (each retry burns budget); `acks_late=False` overrides global `CELERY_TASK_ACKS_LATE=True` (Session 1159 pattern).
- Line 11850-11857: **`_create_engineer_execution_record`** — creates `AgentExecution` row at task entry (S1262 fix — mirrors canonical pattern in tasks_agents.py:2270-2325). Enables schedule_followup binding via `input_data__celery_task_id`.
- Line 11863-11875: try/except wrapping the execute call — always persists terminal state, whether success or exception.
- Line 11900-11924: **Follow-up subscription wiring (S1174 PR-2)** — `create_implicit_followup_subscription` + `fire_agent_followup_subscriptions` — but **GATED on `execution_record is not None AND conversation_id`**. If `conversation_id` is empty, subscription never arms. Comment at line 11888-11889 confirms this invariant.

### 4.3 Queue-parity verification (feedback_procfile_makefile_queue_parity)

- **`core/settings.py:1446`:** `'core.tasks.claude_code_engineer_task': {'queue': 'code_jobs'}` — routes to `code_jobs`.
- **`Procfile:32`:** `code-worker: PG_APPLICATION_NAME=dbz:code-worker celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=1 --max-memory-per-child=400000 -Q code_jobs` — Railway consumes `code_jobs`.
- **`Makefile:322`:** `--queues=code_jobs` — local dev consumes `code_jobs`.
- **Both sides consume the queue.** MEMORY rule `feedback_procfile_makefile_queue_parity` is **VALID as a preventative rule for future PRs; the historical defect it crystallizes is RESOLVED at HEAD.**

### 4.4 Post-back path (S1262)

- `_post_to_conversation` (`claude_code_engineer.py`) is fail-loud: raises on `ChatConversation` write failure so `CeleryTaskEvent.status=FAILURE` becomes visible. But the raise must not trigger a retry (why `max_retries=0`).
- `_persist_engineer_terminal_state` persists `AgentExecution.output_data` even if `conversation_id` is None — retrievable later via execution row.

## 5. Defaults inventory

| Param | Schema-declared | Handler-effective | Divergence? |
|---|---|---|---|
| `task` | required | fail-loud on empty via 5-alias check | **partial divergence** — 4 undeclared aliases (`task_description`, `description`, `prompt`, `message`) accepted silently. F-CC-1 |
| `conversation_id` | Optional, defaults to current | payload → `self._conversation_id` legacy attr → None | Legacy attr pattern (F-S-4 class); non-None only if PA entrypoint injects it |
| `request_mode` | enum `auto`/`answer`/`change`, default `auto` | `.strip().lower()`, default `'auto'`; invalid values normalized inside `execute_engineering_task` with warn log | **partial divergence** — invalid values coerced silently to a default. Small; low-severity. F-CC-4 |

## 6. Hidden filters

None.

## 7. Limits inventory

- **`soft_time_limit=5400s / time_limit=5460s`** — 90+ minute time budget on the Celery task. Documented in `@shared_task` decorator. Not surfaced in response (dispatch-time only surfaces task_id).
- **`max_runtime` at plan level** clamped to 1800s in `_code_job_submit` (sibling code_job_tool, NOT claude_code_tool).
- **No dispatch-side rate limit** on this tool.

## 8. Silent-truncation test

N/A — this is a dispatch tool; no data returned in dispatch response.

## 9. Silent-filter test

N/A.

## 10. Silent-fallback test

- **F-CC-3 confirmed via code trace:** if caller omits `conversation_id` AND `self._conversation_id` is unset, `claude_code_engineer_task` runs but `create_implicit_followup_subscription` never arms (gated at tasks.py:11900). The dispatch response says `status: 'dispatched'` without any indication that no follow-up will fire. Rigby never gets a completion banner. Silent behavioral consequence.

## 11. Staleness test

N/A.

## 12. Freshness signal

N/A — dispatch tool; no cached data.

## 13. Provenance signal

- Response includes `task_id` (Celery task ID) — sufficient for tracing.
- Downstream `AgentExecution` row created at task entry with `celery_task_id`, `task_description`, `conversation_id`, `requested_by`, `request_mode` — full provenance persisted in DB.
- Handler response does NOT surface the `AgentExecution.id`. Rigby cannot use `agent_introspection_tool` or `execution_history_tool` to trace the dispatch without a separate `schedule_followup(task_id=...)` lookup.

## 14. Authority / workspace assumptions

- Handler unconditionally sets `requested_by='rigby'` (line 365). Not workspace-scoped (claude_code_tool operates on the whole repo).
- `_bound_conversation_id` sentinel from PA entrypoint (Session 1248) is NOT read by this handler — only self-retire-of-bound-thread on session_tool.retire uses it. **F-CC-BC-1** (batch-close observation — could add cross-workspace / cross-conversation dispatch detection).

## 15. Runtime dependencies

- **Celery `code_jobs` queue** — MUST have a live worker consuming it (both Procfile + Makefile confirmed).
- **AgentExecution model** — required for provenance and follow-up wiring.
- **AgentFollowupSubscription model** — required for auto-completion banner.
- **PA conversation consumer** — WebSocket layer that receives `agent_completed` broadcast.
- **Claude API** — the engineer session itself calls out to Anthropic via `execute_engineering_task`.
- **Feature flag:** none specific to this tool.

## 16. Recoverable failure modes

- Empty task → fail-loud with received-keys diagnostic.
- Invalid `request_mode` → normalized to `'auto'` with warn log (inside execute).
- Missing conversation_id → dispatch proceeds, no follow-up armed (silent — F-CC-3).
- LLM parameter drift (task under different key) → tolerated via 5-alias fallback (F-CC-1).

## 17. STOP-and-report failure modes

- `_post_to_conversation` failure (Session 1262 fix) → raises to mark `CeleryTaskEvent.status=FAILURE`, does NOT retry (max_retries=0).
- Any exception during `execute_engineering_task` → `_persist_engineer_terminal_state` records exception + re-raises.

## 18. Operator-action failure modes

- `code_jobs` queue backlog buildup — operator must monitor `redis-cli LLEN code_jobs`.
- **`code_jobs` worker down (F-CC-DEPLOY-1) — dispatches queue silently forever.** This is the MEMORY-crystallized failure mode; queue-parity fix at S1226 prevents CONFIGURATION drift but does NOT prevent operational-drift (worker crashed / stopped). No dispatch-side health-check.
- Migration state — no direct dependencies beyond AgentExecution + AgentFollowupSubscription tables.

## 19. Existing test coverage

Strong. Enumerated:

- `test_claude_code_task_receipts_s1262.py` — 7 tests: canonical agent resolution + `AgentExecution` row creation on dispatch + terminal-state persistence on success/exception + post-back failure handling + conversation_id-None error handling + ChatConversation write failure marks execution failed + `max_retries=0` + `acks_late=False` decorator assertions.
- `test_engineer_request_mode.py` — 12 tests: request_mode heuristic (verb detection / change-verb boundaries / edge cases / case insensitivity / empty task defaults to answer / etc.) + prompt discrimination + auto-mode routing.
- `test_claude_code_agent_dim_dispatch.py` — agent-name dimension resolution for telemetry.
- `test_claude_code_agent_consolidation_s1263.py` — S1263 agent row consolidation.
- `test_engineer_openai_fallback.py` — OpenAI SDK fallback path.
- `test_pa_intent_claude_code_source.py` — intent routing.

**Gap identified:** no test for **F-CC-3** — dispatch response should signal when `conversation_id` is missing so Rigby knows no completion banner will fire.

## 20. Change list

**Code patches (one commit per defect per campaign plan §12.1):**

| File | Lines (post-patch) | Defect | Change |
|---|---|---|---|
| `core/services/td_handlers_codejobs.py` | 379-411 | F-CC-3 | Dispatch response now includes `conversation_id` (echoed value or `null`) and `follow_up_will_fire: bool` so Rigby can detect whether the S1174 PR-2 auto-completion banner will arm. The `message` string gains a poll-alternative hint when no completion banner will fire. |

**Test files added:**

- `core/tests/test_claude_code_tool_validation_2728.py` — 6 regression tests covering F-CC-3 shape (conversation_id echoed, follow_up_will_fire = truthy signal, empty-string conversation_id treated as missing, missing task still errors, request_mode still echoed, task alias fallback still works).

**MEMORY.md:**

- `feedback_procfile_makefile_queue_parity.md` — annotated as `**Status:** VERIFIED-VALID at S2728` per campaign plan §12.4. The rule is preventative (not a claim about a live defect); the historical `claude_code_tool` silent-queue-forever defect it crystallizes was RESOLVED at S1226 and remains resolved at HEAD. Rule body retained; annotation names the current-state verification.

**Docs updated:**

- Validation report (this file) records the trace + findings + patches + tests.

**Docs NOT updated (per campaign plan §2 anti-scope):**

- Schema description in `pa_tool_schemas.py` — pending Batch A close doc pass. (Note: the F-CC-3 additive fields are transparent to schema-driven LLM callers — schema unchanged.)
- `docs/topics/personal-assistant.md` — pending Batch A close.

**Test verification:**

- `python manage.py test core.tests.test_claude_code_tool_validation_2728 core.tests.test_claude_code_task_receipts_s1262 core.tests.test_engineer_request_mode core.tests.test_claude_code_agent_dim_dispatch core.tests.test_claude_code_agent_consolidation_s1263 core.tests.test_engineer_openai_fallback core.tests.test_pa_intent_claude_code_source --keepdb --noinput` → **75/75 pass** (0.530s).
- Cross-tool regression (tools 1-3 alongside tool 4 patches): **76/76 pass** (3.663s). Zero cross-tool interference.

---

## Findings

### F-CC-1 — Handler accepts undeclared task-alias keys (LOW; batch-close)
- **Class:** UNDER-DOCUMENTED schema-vs-handler divergence.
- **Evidence:** `td_handlers_codejobs.py:333-340`. Handler accepts `task_description`, `description`, `prompt`, `message` in addition to schema-declared `task`.
- **Severity:** LOW. Defensive against LLM param drift; but schema doesn't document.
- **Action:** BATCH-CLOSE doc pass — either declare the aliases in the schema description or remove the fallback.

### F-CC-2 / F-CC-5 — Response envelopes lack `ok: true/false` (LOW; batch-close)
- **Class:** cross-tool consistency (same class as F-D-1 / F-S-1 / F-SD-BC-1 / F-KB-BC-1).
- **Action:** BATCH-CLOSE cleanup pass at Batch A close.

### F-CC-3 — Missing `conversation_id` silently disables completion follow-up (MEDIUM)
- **Class:** DEFECT-CLASS-D2 (silent behavioral consequence not surfaced in response).
- **Evidence:** `td_handlers_codejobs.py:349-352` accepts payload OR legacy `_conversation_id` attr OR None. `tasks.py:11900` gates `create_implicit_followup_subscription` on `conversation_id` being truthy. If both are absent, dispatch succeeds but no completion banner will ever fire. Dispatch response says `status: 'dispatched'` regardless.
- **Severity:** MEDIUM. Rigby's expectation is that `claude_code_tool` dispatches produce an auto-completion banner in her PA conversation (per S1174 PR-2 wiring). If she doesn't get one, she waits indefinitely without knowing why.
- **Action:** PATCH — surface `conversation_id` (echoed or `null`) and `follow_up_will_fire: bool` in the dispatch response so Rigby knows whether to expect a completion banner or must poll separately. Regression test.

### F-CC-4 — Invalid `request_mode` normalized silently inside `execute_engineering_task` (LOW)
- **Class:** UNDER-DOCUMENTED. Handler validates by coercing to lowercase but doesn't enforce enum membership. Invalid values are warn-logged inside the downstream service.
- **Severity:** LOW. Schema declares enum; LLM shouldn't drift; warn log is captured.
- **Action:** BATCH-CLOSE observation. Enum-enforcement at handler edge is a small addition; deferred.

### F-CC-6 — Queue-parity MEMORY rule (VERIFIED VALID at HEAD)
- **Class:** VERIFICATION only.
- **Evidence:** `core/settings.py:1446` routes `claude_code_engineer_task` to `code_jobs`; `Procfile:32` consumes; `Makefile:322` consumes. Both sides have live workers.
- **Severity:** N/A.
- **Action:** annotate MEMORY rule as still-valid-at-HEAD (do NOT mark RESOLVED — the rule is a preventative discipline for future PRs, not a defect claim about the current state).

### F-CC-DEPLOY-1 — No dispatch-side worker-liveness check (OUT OF SCOPE)
- **Class:** operational-discipline (not per-tool defect).
- **Evidence:** No health-check in `_handle_claude_code`.
- **Severity:** MEDIUM at operator level; N/A at handler level.
- **Action:** DOC-ONLY. Consider adding a diagnostic response field (e.g., `code_jobs_queue_depth`) — deferred to Batch D worker/env target.

---

## Rigby-safe assessment (post-patch)

- **R1 (no dangerous defaults):** CLEARED. `request_mode` defaults to `'auto'` (safe); `conversation_id` defaults to None with F-CC-3 signal now surfaced.
- **R2 (no silent action substitution):** CLEARED. `request_mode` invalid values normalized silently inside execute — batch-close observation only (F-CC-4 low severity).
- **R3 (no silent truncation):** N/A.
- **R4 (hidden filters surfaced):** N/A.
- **R5 (workspace/authority carriage):** CLEARED. `requested_by='rigby'` hardcoded; no workspace scope.
- **R6 (freshness surface):** N/A.
- **R7 (provenance surface):** PARTIAL — deferred to batch-close (Rigby has `task_id` sufficient for `execution_history_tool` and `schedule_followup` bindings; adding `AgentExecution.id` echo is a Batch-close enhancement).
- **R8 (worker/env preconditions):** VIOLATED at operational-drift level (F-CC-DEPLOY-1) — not patchable at handler level. Operator discipline; deferred to Batch D worker/env target.

**F-CC-3 patched.** Rigby now sees `conversation_id` (echoed or `null`) + `follow_up_will_fire: bool` in every dispatch response and can decide whether to poll `execution_history_tool` or wait for the auto-completion banner.

---

## Verdict

Tool status: **DEFECT-PATCHED-VERIFIED** at HEAD post-Session 2728 patches.

**Code trace coverage:** schema (verbatim); direct handler `_handle_claude_code`; task-side `claude_code_engineer_task` decorator + `AgentExecution` row creation + terminal-state persistence + follow-up subscription wiring; queue routing at `core/settings.py:1446`; queue-parity verification against Procfile + Makefile.

**Findings summary:**

- **Valid at HEAD → patched:** F-CC-3 (silent-no-banner consequence).
- **Batch-close cleanup observations (deferred per Chris):** F-CC-1 (5-alias task extraction), F-CC-2 / F-CC-5 (`ok:` envelope consistency), F-CC-4 (invalid request_mode silent coerce). All LOW.
- **Historical defects VERIFIED as RESOLVED at HEAD (no code change needed):** queue-parity (S1226); silent-success + missing-AgentExecution + missing-follow-up (S1262); agent row consolidation (S1263).
- **Operational-drift observation (out-of-scope for tool):** F-CC-DEPLOY-1 — handler cannot verify `code_jobs` queue has a live consumer; deferred to Batch D.

**MEMORY rule status:**

- `feedback_procfile_makefile_queue_parity` — VERIFIED-VALID at HEAD. The rule is preventative discipline (not a live defect claim). The historical `claude_code_tool` incident it crystallizes remains RESOLVED. Rule body retained; annotation confirms current-state.

**Regression sweep at HEAD:**

- 6 new regression tests in `test_claude_code_tool_validation_2728.py`: **6/6 pass**.
- Existing claude_code tests (69 tests across 6 files): **69/69 pass** (0.530s combined 75-test suite).
- Cross-tool sweep (tools 1-3 alongside tool 4 patches): **76/76 pass** (3.663s). Zero cross-tool interference.

**Rigby cross-check (§10.1 step 12):** deferred. The F-CC-3 patch is exercised by 6 deterministic regression tests that use the exact PA dispatch path (`ToolDispatcher._handle_claude_code(...)`) with mocked Celery `.delay(...)`.

**Follow-ups filed:**

- MEMORY `feedback_procfile_makefile_queue_parity` annotated VERIFIED-VALID at HEAD.
- Batch-close observations for cross-tool consistency (error envelope, `ok:` field, invalid enum coercion).

**Tool closure statement:** `claude_code_tool` is VERIFIED at HEAD `9d158805` + 2728 patches. The queue-parity + receipt-reliability discipline established at S1226 + S1262 + S1263 remains intact; the newly-patched F-CC-3 signal ensures Rigby knows whether a dispatch will produce an auto-completion banner or requires explicit polling.

# Retry Behavior — Validation Report

**Tool:** retry behavior — the retry contract across the three PA execution boundaries: (1) `tool_dispatcher.execute()` per-tool call, (2) the Celery `pa` queue `process_pa_chat_task` task-level, and (3) the LLM SDK client layer inside `openai_client_factory` / `anthropic_client_factory`. Also covers the narrow one-shot retries inside `_run_agentic_loop` (Sessions 1077/1079/1086) and the F-CC-3 retry-hint envelope precedent from Batch A tool 4.

**Files traced:**
- `core/services/tool_dispatcher.py:150-160` — `ToolErrorCode` (7 codes).
- `core/services/tool_dispatcher.py:162-174` — `ToolResult` dataclass (7 fields).
- `core/services/tool_dispatcher.py:841-897` — TimeoutError + Exception paths in `_execute_inner`.
- `core/tasks.py:11946-11949` — `process_pa_chat_task` shared_task decorator + shim.
- `core/tasks_misc.py:4672-4958` — `_impl_process_pa_chat_task` full body (zero retry calls).
- `core/services/unified_pa_entrypoint.py:1729-2200` — `_run_agentic_loop` narrow one-shot retries.
- `core/services/unified_pa_entrypoint.py:163-202` — `_build_tool_args_malformed_envelope` (S1177 F1 retry_hint shape).
- `core/services/openai_client_factory.py:68-72, 74, 233-286` — OpenAI factory `OPENAI_MAX_RETRIES=2` + `_FORBIDDEN_KWARGS` invariant.
- `core/services/anthropic_client_factory.py` (mirror of OpenAI).

**Session validated:** S2730 (Batch C tool 5 of 5 — closes Batch C).
**HEAD at validation:** `c7b06c9a` (post-Batch-C-tool-4 close on feature branch).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred.
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch C tool 5 of 5 — Batch C CLOSED). Trace + 1 code patch (F-RB-1 ToolResult.is_retryable + `_ERROR_CODE_RETRYABLE` map) + 22 regression tests complete; 248 total pass across all Batch A + B + C tools 1-5 validation-2728 files + test_td_autofill_safety + test_pa_tool_args_malformed.

---

## 1. Intended purpose

Every PA turn crosses three boundaries where failure can occur:

1. **LLM SDK boundary** — network call to OpenAI/Anthropic. Handled by SDK-native retry with `max_retries=2` centrally configured by the factory (Session 1084/1144).
2. **Tool dispatcher boundary** — handler execution inside the PA worker. Handled by `ToolDispatcher._execute_inner` which converts failures into `ToolResult(ok=False, ...)` envelopes with an `error_code`.
3. **Celery task boundary** — the PA chat task itself. Explicitly does NOT retry (Session 1159 `acks_late=False` design decision).

The MEMORY rule `feedback_deliverable_tool_use_append_for_large_payloads` documents ONE retry-hint envelope class (S1177 F1 `TOOL_ARGS_JSON_MALFORMED`). Every other tool failure returns a bare `ToolResult(ok=False, error_code=..., error_message=..., trace_id=..., result=None)` with **no signal to Rigby about whether the failure is retryable**.

**This tool's scope**: verify the three boundaries' retry semantics are intentional and safe, then close the gap between the S1177 F1 retry-hint precedent (one error class) and the six other tool error codes that have no retry classification.

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY:
- `feedback_deliverable_tool_use_append_for_large_payloads` (RESOLVED at S1177; VERIFIED at Batch C tool 2 F-PS-6) — Rigby knows the `TOOL_ARGS_JSON_MALFORMED` envelope carries a `retry_hint.recommended_action` and `max_chunk_chars_suggestion`.
- `feedback_local_celery_stall_playbook` — Rigby has diagnostic recipe for the worker-level stall class, but this MEMORY rule is about diagnosis, not the retry contract.
- `feedback_anthropic_client_factory` / `feedback_openai_client_factory` — Rigby knows `max_retries` is centrally set at 2 and cannot be overridden per-call.

Rigby's mental model at HEAD:
- **LLM SDK failures**: 2 retries applied by the SDK; if all 3 attempts fail, the exception bubbles to `enforce_real_ai`. Correct.
- **Tool failures (TOOL_TIMEOUT)**: transient — Rigby ASSUMES she should retry, but the envelope gives no explicit signal.
- **Tool failures (TOOL_EXCEPTION)**: unknown severity — Rigby has no way to distinguish "network hiccup, retry" from "logic bug, don't retry."
- **Tool failures (TOOL_NOT_FOUND / TOOL_PERMISSION_DENIED / TOOL_INVALID_PAYLOAD)**: permanent — but no explicit signal.
- **PA task-level failures**: doesn't retry; degrades to fine-grained sub-op swallows (S1159 design).

## 3. Constants / signatures (verbatim capture)

### 3.1 `ToolErrorCode` at `tool_dispatcher.py:150-160`

```python
class ToolErrorCode:
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_EXCEPTION = "TOOL_EXCEPTION"
    TOOL_INVALID_PAYLOAD = "TOOL_INVALID_PAYLOAD"
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED"
    TOOL_DEPENDENCY_FAILED = "TOOL_DEPENDENCY_FAILED"
    AGENT_EXECUTION_FAILED = "AGENT_EXECUTION_FAILED"
```

### 3.2 `ToolResult` at `tool_dispatcher.py:162-174`

```python
@dataclass
class ToolResult:
    ok: bool
    tool: str
    latency_ms: int
    error_code: Optional[str]
    error_message: Optional[str]
    trace_id: str
    result: Optional[Any]
```

**7 fields — no `is_retryable`, no `retry_after_ms`, no `retry_hint` sibling.**

### 3.3 `_build_tool_args_malformed_envelope` shape (S1177 F1 precedent)

```python
{
    'ok': False,
    'error_code': 'TOOL_ARGS_JSON_MALFORMED',
    ...
    'retry_hint': {
        'recommended_action': f"{tool_name}.append" if tool_name.endswith('_tool') else None,
        'max_chunk_chars_suggestion': 2000,
    },
}
```

**Only one error class carries `retry_hint`.** The other 7 codes don't.

### 3.4 PA Celery task decorator

```python
# tasks.py:11946
@shared_task(bind=True, time_limit=300, soft_time_limit=280, acks_late=False)
def process_pa_chat_task(...): ...
```

- `bind=True` — the task can call `self.retry()` if it wanted to.
- `time_limit=300, soft_time_limit=280` — hard/soft ceilings.
- `acks_late=False` — task acked on receipt, not on completion (S1159 rationale: lost message on worker crash preferable to UI stuck for 1h visibility_timeout).
- **No `max_retries`, no `default_retry_delay`, no `autoretry_for`.**

### 3.5 `_impl_process_pa_chat_task` retry sweep

Zero `self.retry()` calls in the entire body (lines 4672-4958). Instead, every sub-operation uses inline try/except with `logger.warning(...)` and inline degradation.

### 3.6 Agentic loop narrow one-shot retries

Three sites in `_run_agentic_loop`:
- **S1079 line 1801-1808**: LLM call failed on first iteration → clear `response_id`, rebuild messages, `continue`. One shot.
- **S1086 line 1809-1848**: LLM continuation failed BUT tools ran successfully → fresh-summary attempt without `previous_response_id`.
- **S1077 line 2167-2193**: Gateway returned wrong action (`content_stats`/`list` when caller asked for something else) → re-inject action + retry once. **Hardcoded to `content_tool`/`work_tool` — not extensible.**

### 3.7 LLM SDK factory retry contract

`openai_client_factory.py:72` — `OPENAI_MAX_RETRIES = 2` (SDK-level; 3 total attempts). `_FORBIDDEN_KWARGS = ("timeout", "max_retries", "api_key")` at line 74. Same shape in `anthropic_client_factory.py`.

## 4. Handler behavior (traced)

### 4.1 Tool dispatcher failure paths

**TimeoutError path (line 841-868):**
- Emits `_record_tool_metric(tool_name, action, 'timeout', latency_ms)`.
- Returns `ToolResult(ok=False, error_code=TOOL_TIMEOUT, error_message="Tool execution exceeded {timeout}s timeout", ...)`.
- Emits `emit_tool_completed(status="error")` on the live ticker.
- **No `is_retryable=True` signal in envelope.**

**Exception path (line 870-897):**
- Emits `_record_tool_metric(tool_name, action, 'error', latency_ms)`.
- Returns `ToolResult(ok=False, error_code=TOOL_EXCEPTION, error_message=str(e), ...)`.
- `logger.error(f"[{trace_id}] Tool {tool_name} failed: {e}", exc_info=True)` — traceback logged.
- **No exception-class → retryable classification.**

### 4.2 PA Celery task lifecycle

- Dispatches via `.delay()` — result held in Redis result backend.
- Frontend polls `GET /api/pa/chat/status/<task_id>/` every 2s.
- If task raises: exception surfaces to result backend; frontend sees "failed" state; **no retry**.
- Design rationale (S1159): `acks_late=False` because chat is user-facing; retrying a 5-minute task on worker crash is worse than showing "failed, try again" to the user.

### 4.3 Agentic loop retries

Correctly narrow — three well-documented one-shot retries with logged rationale. Not a defect.

### 4.4 LLM SDK factory retries

Centrally configured at 2 retries per client instance. Cached per `(api_key, base_url)`. `max_retries` forbidden as kwarg — prevents per-call drift. **VERIFIED-CORRECT.**

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| PA task `max_retries` | not set | Celery default 3 (never fires — task doesn't call `self.retry()`) | design |
| PA task `acks_late` | `tasks.py:11946` | `False` | S1159 design |
| PA task `time_limit` | `tasks.py:11946` | 300s | design |
| Tool dispatcher retries | none | 0 | design |
| OpenAI SDK `max_retries` | `openai_client_factory.py:72` | 2 | centralized |
| Anthropic SDK `max_retries` | `anthropic_client_factory.py` | 2 | centralized |
| Agentic loop LLM-fail retry | `unified_pa_entrypoint.py:1801` | 1 on first iteration only | S1079 |
| Agentic loop action-mismatch retry | `unified_pa_entrypoint.py:2167` | 1 for `content_tool`/`work_tool` | S1077 hardcoded |

## 6. Hidden filters inventory

Not applicable at this layer.

## 7. Limits inventory

- `time_limit=300s` / `soft_time_limit=280s` on PA task.
- Agentic loop `max_iterations: int = 12` (line 1729).
- LLM SDK 2 retries per attempt.

## 8. Silent-truncation test

Not applicable.

## 9. Silent-filter test

Not applicable.

## 10. Silent-fallback test

- **PA task doesn't retry** — but this is design, not silent-fallback.
- **`TOOL_TIMEOUT` returns generic envelope** with no retry classification → callers infer retryability from `error_code` string matching. **F-RB-1 DEFECT** — the classification is implicit; a first-time caller has no way to know.
- **S1077 auto-retry is hardcoded** to `content_tool`/`work_tool` — if a new gateway ships with the same action-mismatch pattern, silent-fallback recurs. **F-RB-2 candidate.**

## 11. Staleness test

Not applicable.

## 12. Freshness signal

Not applicable.

## 13. Provenance signal

Not applicable.

## 14. Authority / workspace assumptions

Not applicable at this layer.

## 15. Runtime dependencies

- PA task requires the `pa` Celery queue (`Procfile` line — see `feedback_procfile_makefile_queue_parity`).
- LLM SDK retries require the SDK to correctly classify the failure as retryable (HTTP 5xx, 429, connection errors).

## 16. Recoverable failure modes

- LLM SDK: 2 automatic retries per call (transient network errors, 429 rate limits).
- Agentic loop LLM-call retry: 1 shot on first iteration (transient API 400s).
- Agentic loop action-mismatch retry: 1 shot for content_tool/work_tool (LLM omit-action bug).

## 17. STOP-and-report failure modes

Every failure at the tool dispatcher level returns a `ToolResult(ok=False, ...)` — STOP-and-report by construction. But **no `is_retryable` signal** → Rigby's LLM has to guess.

## 18. Operator-action failure modes

- PA worker restart required for env changes (`feedback_pa_worker_function_calling_env`).
- Celery worker restart for stall recovery (`feedback_local_celery_stall_playbook`).

## 19. Existing test coverage

- `core/tests/test_pa_tool_args_malformed.py` — S1177 F1 retry-hint envelope shape.
- `core/tests/test_payload_size_limits_validation_2728.py` (Batch C tool 2 F-PS-6) — S1177 F1 retry_hint contents.
- **Zero coverage** for TOOL_TIMEOUT / TOOL_EXCEPTION / TOOL_NOT_FOUND / TOOL_PERMISSION_DENIED / TOOL_INVALID_PAYLOAD retry classification.
- **Zero coverage** for PA task no-retry behavior.
- **Zero coverage** for the S1077 action-mismatch auto-retry (hardcoded tool list).

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-RB-1 — Add `is_retryable: Optional[bool]` field to `ToolResult` + classify all 7 error codes.**
  Introduce a per-error-code retryability map:
  ```python
  _ERROR_CODE_RETRYABLE = {
      TOOL_TIMEOUT: True,           # transient — network/DB/slow op
      TOOL_DEPENDENCY_FAILED: True, # transient — upstream service down
      TOOL_EXCEPTION: True,         # ambiguous — assume retryable (LLM decides)
      TOOL_NOT_FOUND: False,        # permanent — tool doesn't exist
      TOOL_PERMISSION_DENIED: False,# permanent — auth failure
      TOOL_INVALID_PAYLOAD: False,  # permanent — payload needs to change
      AGENT_EXECUTION_FAILED: True, # ambiguous — assume retryable
      'TOOL_ARGS_JSON_MALFORMED': True,  # already has retry_hint (S1177 F1)
  }
  ```
  Populate `is_retryable` in all `ToolResult(...)` constructions in the dispatcher.

- **F-RB-2 — S1077 hardcoded auto-retry generalization (Chris gate — scope call).**
  The `content_tool`/`work_tool` action-mismatch retry at `unified_pa_entrypoint.py:2167` is hardcoded. Options:
  - **(a)** Extract a `_should_retry_action_mismatch(tool_name, requested, got)` helper + list of tools/actions.
  - **(b)** Leave as-is — the S1077 shape has served for many sessions.
  - **(c)** Retire the auto-retry entirely; require callers to explicitly retry.
  - Recommendation: **(b)** — extension is speculative; add to combined batch-close observation.

- **F-RB-3 — Verified LLM SDK factories at HEAD.**
  No patch. `OPENAI_MAX_RETRIES=2` + `_FORBIDDEN_KWARGS` invariant intact.

- **F-RB-4 — Verified PA task no-retry design at HEAD.**
  No patch. S1159 rationale intact.

- **F-RB-5 — Verified agentic loop narrow retries at HEAD.**
  No patch. S1077/S1079/S1086 shapes intact.

- **F-RB-6 — Regression tests.**
  New file `core/tests/test_retry_behavior_validation_2728.py`:
  - `ToolResult` has `is_retryable` field.
  - Each error code maps to expected retryability.
  - `TOOL_TIMEOUT` and `TOOL_DEPENDENCY_FAILED` → `is_retryable=True`.
  - `TOOL_NOT_FOUND`, `TOOL_PERMISSION_DENIED`, `TOOL_INVALID_PAYLOAD` → `is_retryable=False`.
  - Source-level guard: PA task has no `self.retry()` in body (S1159 design invariant).
  - Source-level guard: `openai_client_factory` and `anthropic_client_factory` reject `max_retries` in kwargs.

---

## Findings

### F-RB-1 — `ToolResult` has no retry classification signal
- **Class:** DEFECT (D2 — Rigby cannot detect retryability from failure envelope).
- **Evidence:** `tool_dispatcher.py:162-174` (7 fields, no is_retryable); TimeoutError path (line 841-868) and Exception path (line 870-897) both omit signal.
- **Severity:** MEDIUM.
- **Action:** patch — add `is_retryable: Optional[bool]` + populate via per-error-code map.

### F-RB-2 — S1077 auto-retry hardcoded to content_tool/work_tool
- **Class:** DEFECT (D2 — non-extensible; potential silent-fallback if a new gateway ships).
- **Evidence:** `unified_pa_entrypoint.py:2177-2178` explicit tool-name check.
- **Severity:** LOW.
- **Action:** **defer** (Chris gate; recommendation: leave as-is).

### F-RB-3 — LLM SDK factories verified at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `openai_client_factory.py:72, 74`; `anthropic_client_factory.py` mirror.
- **Severity:** N/A.
- **Action:** none. MEMORY rules `feedback_openai_client_factory` and `feedback_anthropic_client_factory` remain VERIFIED.

### F-RB-4 — PA Celery task no-retry design verified at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `tasks_misc.py:4672-4958` (zero `self.retry()`), `tasks.py:11946` decorator rationale.
- **Severity:** N/A.
- **Action:** none.

### F-RB-5 — Agentic loop narrow one-shot retries verified at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** S1079 line 1801, S1086 line 1809, S1077 line 2167.
- **Severity:** N/A.
- **Action:** none.

### F-RB-6 — Zero coverage of retry classification
- **Class:** DEFECT (D9).
- **Evidence:** grep of `core/tests/*.py` for `is_retryable` — none. Only S1177 F1 `TOOL_ARGS_JSON_MALFORMED` has coverage.
- **Severity:** MEDIUM.
- **Action:** patch — add unit tests per §20.

---

## Verdict (Batch C tool 5 CLOSED — Batch C complete)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** for the four retry boundaries traced. LLM SDK factories (F-RB-3), PA Celery task no-retry design (F-RB-4), and agentic loop narrow retries (F-RB-5) all verified correct at HEAD. Tool dispatcher boundary now surfaces `is_retryable: Optional[bool]` on `ToolResult` per F-RB-1.
- Regression tests added: `core/tests/test_retry_behavior_validation_2728.py` — 22 tests (13 F-RB-1 field + classification + source guards; 3 F-RB-3 factory invariants; 2 F-RB-4 no-retry source guards; 3 F-RB-5 agentic loop guards; 2 F-RB-6 module-path stability).
- Cross-tool regression: 248/248 substantive tests pass across all 15 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py` (Batches A + B + C tools 1-5).
- Docs updated: none required (envelope shape is self-documenting via the field name + inline docstring on `_ERROR_CODE_RETRYABLE`).
- Migration files: none.
- Follow-ups filed: F-RB-2 (S1077 hardcoded auto-retry generalization) → combined batch-close observation list. F-RB-5's third F-RB-2-adjacent test acts as a heads-up guard for the future refactor.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-RB-1 | ToolResult.is_retryable + _ERROR_CODE_RETRYABLE map + _classify_retryable helper | `5f502c30` |
| tests | 22 regression tests | `2081c558` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_openai_client_factory`: reinforced VERIFIED at HEAD via F-RB-3 (factory rejects `max_retries` + `timeout` in kwargs) and F-RB-6 (module path + exports stable). **Third verification pass** in this campaign after Batch C tool 3 F-RL-5 and F-RB-3.
- `feedback_anthropic_client_factory`: reinforced VERIFIED via F-RB-6 (module path + `get_anthropic_client` export stable).
- `feedback_procfile_makefile_queue_parity`: implicitly reinforced via F-RB-4 verified-at-HEAD guard (PA task decorator preserves `acks_late=False` design; `pa` queue routing unchanged).
- `feedback_deliverable_tool_use_append_for_large_payloads`: unchanged (RESOLVED at Batch A tool 1 F-D-9, re-verified at Batch C tool 2 F-PS-6). The S1177 F1 `TOOL_ARGS_JSON_MALFORMED` envelope's `retry_hint` block intentionally sits outside `_ERROR_CODE_RETRYABLE` — it's constructed pre-dispatch and never becomes a ToolResult.

### Design decision: `is_retryable=None` on ambiguous / unknown codes

The `_classify_retryable` helper returns `None` (not `False`) when the error_code is missing or unrecognized. Rationale: this lets downstream code — Rigby's LLM, the agentic loop's action-mismatch retry, and any direct caller — fall back to whichever heuristic it was already using. Returning `False` on unknown codes would silently downgrade any transient failure that doesn't happen to be in the ratified map. Callers preferring `bool` semantics can use `bool(result.is_retryable)` explicitly.

The map covers the 7 codes declared in `ToolErrorCode`. Adding a new code without updating the map returns `None` for that code, which is safe (does not lie about retryability). A future code that needs an explicit True/False classification must be added to the map alongside its declaration.

### Batch C summary (post-tool 5 close)

Batch C shipped:
- **5 tools verified** (context injection, payload size, retrieval limits + hidden filters, ORM helper defaults, retry behavior).
- **~19 code patches + 1 migration + 110 regression tests** (across all 5 tools).
- **~4 shared helpers** extracted (`_CONTEXT_INJECTION_ENV_ERRORS`, `_build_fresh_summary`, `td_limit_envelope.compute_limit`, `_classify_retryable`).
- **248/248 substantive tests pass** across all 15 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py`. Zero cross-tool regression.

Batch D queued per campaign plan §3.4 (PA worker + Celery lifecycle + worker cache).

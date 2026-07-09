# PA_USE_FUNCTION_CALLING Env Flag — Validation Report

**Tool:** `PA_USE_FUNCTION_CALLING` env flag — the single feature gate that decides whether the PA worker offers tools to GPT-5.2 (function-calling path) or falls through to the 506-line pre-Session-1036 keyword router. When misconfigured, Rigby's entire tool surface silently disappears, and she produces text-only responses that look like model refusal ("I don't have tool access") but are actually the system never offering tools in the first place.

**Files traced:**
- `core/settings.py:1662` — env-read + Python-bool coercion.
- `core/services/unified_pa_entrypoint.py:989` — main FC-vs-keyword branch at `_process_message`.
- `core/services/unified_pa_entrypoint.py:1230` — FC-specific `_sanitize_fc_response` gate.
- `core/services/unified_pa_entrypoint.py:1084-1214` — keyword-router fallback path.
- `core/services/unified_pa_entrypoint.py:1288-1297` — `[PA_TASK_SUMMARY]` telemetry line.
- `core/services/unified_pa_entrypoint.py:3127-3177` — `_detect_intent_and_route` claude-code short-circuit to `('claude_code_coordination', None)`.
- `Procfile:23-30` — production celery worker declarations (no PA_USE_FUNCTION_CALLING).
- `Makefile:250, 262, 277, 288, 319` — local celery worker recipes (all set PA_USE_FUNCTION_CALLING=true).
- `tools/pa_local.sh:341` — inline env-var reminder for hand-restarted workers.
- `docs/narratives/PERSONAL_ASSISTANT.md:86, 498` — narrative claim about the flag default.

**Session validated:** S2731 (Batch D tool 1 of 3 — opens Batch D).
**HEAD at validation:** `763bf9a1` (post-Batch-C S2731 handoff merge).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred.
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch D tool 1 of 3). Trace + 4 code/config patches (F-WF-1 code default + doc rewrite; F-WF-2 Procfile belt-and-suspenders; F-WF-3 startup log; F-WF-4 routing_path field) + 10 regression tests complete; 258 total pass across all Batch A + B + C + D tool 1 validation-2728 files + `test_td_autofill_safety` + `test_pa_tool_args_malformed`.

---

## 1. Intended purpose

`PA_USE_FUNCTION_CALLING` is the single feature gate for the Session-1036 architectural watershed (docs/narratives/PERSONAL_ASSISTANT.md line 100): when True, PA uses GPT-5.2 Responses-API function calling with all 106 tool schemas visible to the model; when False, PA falls back to the pre-1036 keyword router which routes on `_detect_intent_and_route` (506 lines of if/elif).

**Both paths exist in code** — the flag chooses which fires at `unified_pa_entrypoint.py:989`. The Session-1094 change added a hard short-circuit to `_detect_intent_and_route`: for `source='claude-code'` messages (which `pa_chat.py` always sets), the router returns `('claude_code_coordination', None)`. The keyword-routing fallback has **NO branch** for `claude_code_coordination` — it falls to `_generate_direct_response`, producing text-only output with no tool calls.

This means: **if the PA worker is running with PA_USE_FUNCTION_CALLING False when Rigby dispatches a claude-code message, no tools get offered and Rigby's LLM emits a plausible-looking "I don't have tool access" text response.** The failure is silent from Rigby's perspective — the system responded, but with the wrong path.

**This tool's scope**: verify the env flag is correctly read, verify Makefile + docs still match code, sweep for observability gaps, and patch the silent-failure surfaces so a future S1184-class incident is detectable in ≤30 seconds via log tail.

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY:
- `feedback_pa_worker_function_calling_env` — Rigby knows manually-restarted workers must have `PA_USE_FUNCTION_CALLING=true` in env. `make celery` sets it; ad-hoc `celery -A core worker` does not.
- Smoking-gun signal per MEMORY: `[PA_TASK_SUMMARY]` line showing `tools=none tool_calls=0 intent=claude_code_coordination` for a Rigby request that should have called tools.

Rigby's mental model at HEAD:
- `make celery` → flag set → FC path → tools work. ✓
- Ad-hoc restart without env → keyword router → claude-code coordination → no tools. ✗
- Production (Railway) → flag "default true" per docs → tools work. **Ambiguous** — the code default is `'false'`, not `'true'`.

## 3. Constants / signatures (verbatim capture)

### 3.1 `core/settings.py:1662`

```python
# Session 1036: LLM-driven function calling for PA (replaces keyword router)
# When True, PA uses GPT-5.2 function calling to route messages instead of
# the 506-line _detect_intent_and_route() keyword matching chain.
PA_USE_FUNCTION_CALLING = os.environ.get('PA_USE_FUNCTION_CALLING', 'false').lower() == 'true'
```

**Code default: `'false'`.** Not `'true'` as docs suggest.

### 3.2 `core/services/unified_pa_entrypoint.py:989`

```python
if getattr(settings, 'PA_USE_FUNCTION_CALLING', False):
    # ── New path: GPT-5.2 function calling ──────────────────────
    content, tool_runs_raw, fc_meta, response_id = await self._run_agentic_loop(...)
else:
    # ── Existing path: keyword routing ──────────────
    detected_intent, routed_to = self._detect_intent_and_route(
        message, source=context.get('source') if context else None,
    )
    intent = detected_intent or 'general'
    ...
    if routed_to:
        # Execute via ToolDispatcher
        tool_result = await self.tool_dispatcher.execute(...)
    else:
        # No tool needed - direct LLM response
        content = await self._generate_direct_response(message, full_context, trace_id)
```

**When keyword router returns `routed_to=None` (claude-code source), the fallback is `_generate_direct_response` — no tool dispatch.**

### 3.3 `Procfile:23-30` (production celery workers)

```
celery-worker: PG_APPLICATION_NAME=dbz:celery-worker celery -A core worker ...
celery-pa: PG_APPLICATION_NAME=dbz:celery-pa celery -A core worker -l info --pool=prefork -c 1 --max-tasks-per-child=10 --max-memory-per-child=200000 -Q pa
celery-content: PG_APPLICATION_NAME=dbz:celery-content celery -A core worker ...
celery-long-running: PG_APPLICATION_NAME=dbz:celery-long-running celery -A core worker ...
celery-long-running-2: PG_APPLICATION_NAME=dbz:celery-long-running-2 celery -A core worker ...
celery-broadcast: PG_APPLICATION_NAME=dbz:celery-broadcast celery -A core worker ...
```

**No `PA_USE_FUNCTION_CALLING=true` on ANY line.** Production relies on Railway dashboard env-var config.

### 3.4 `Makefile:250, 262, 277, 288, 319` (local dev)

All 5 celery worker recipes explicitly set `PA_USE_FUNCTION_CALLING=true`. Consistent.

### 3.5 `[PA_TASK_SUMMARY]` log line (`unified_pa_entrypoint.py:1288-1297`)

```python
logger.info(
    "[PA_TASK_SUMMARY] trace_id=%s latency_ms=%d llm_iterations=%d "
    "tool_calls=%d tools=%s history_turns=%d intent=%s "
    "silent_fallback=%s",
    trace_id, latency_ms,
    len(tool_call_metadata) if tool_call_metadata else 1,
    len(tool_names), ','.join(tool_names) or 'none',
    len(self._conversation_history), intent,
    'true' if silent_fallback else 'false',
)
```

**No `routing_path` field.** Can't tell FC-vs-keyword from this log alone; only via `tools=none` heuristic which isn't specific to path choice (a legitimate no-tool-turn also shows `tools=none`).

### 3.6 `docs/narratives/PERSONAL_ASSISTANT.md:86, 498`

> **`PA_USE_FUNCTION_CALLING` flag** | Env var. `true` (default on Railway) → GPT-5.2 function calling path. `false` → falls back to the pre-Session-1036 506-line keyword router.

> `PA_USE_FUNCTION_CALLING` default | Env var; default is `true` on Railway + locally

**"Default true on Railway + locally" conflates infrastructure config (Railway dashboard env vars + Makefile recipes) with code default (`'false'`).** A reader inferring "the code defaults to true" is wrong.

## 4. Handler behavior (traced)

### 4.1 Flag True path (F-WF-VERIFIED-CORRECT)

- `unified_pa_entrypoint.py:989` → `_run_agentic_loop` at line 1729.
- Loop offers all 106 tool schemas via GPT-5.2 Responses API.
- Tool calls dispatched via `tool_dispatcher.execute` (Batch C tool 5's `is_retryable` envelope applies).
- `[PA_TASK_SUMMARY]` shows `tools=<name1>,<name2>,...`.
- **VERIFIED-CORRECT at HEAD.**

### 4.2 Flag False path — keyword router

- `unified_pa_entrypoint.py:1084` → `_detect_intent_and_route(message, source=context.get('source'))`.
- Line 1132: `if routed_to:` → tool dispatch.
- Line 1206: `else:` → `_generate_direct_response`.
- For `source='claude-code'`: `_detect_intent_and_route` hard-short-circuits to `('claude_code_coordination', None)` at line 3127. `routed_to=None`. Falls to line 1206.
- **`_generate_direct_response` never offers tools** — text-only.
- `[PA_TASK_SUMMARY]` shows `intent=claude_code_coordination tools=none tool_calls=0`.
- **DEFECT** — silent failure from Rigby's perspective.

### 4.3 Flag misconfig detection

Zero startup log line declares the current flag state. Zero test coverage exists. The only way to detect misconfig is:
1. Reproduce a Rigby-tool-request-with-no-tools-fired incident.
2. Grep `[PA_TASK_SUMMARY]` for `tools=none intent=claude_code_coordination`.
3. `ps -p <pid> -o command` to confirm env not set.

S1184 spent 30 minutes on this diagnosis. Root cause: **observability gap**.

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| `PA_USE_FUNCTION_CALLING` code default | `settings.py:1662` | `'false'` (Python-bool `False`) | **F-WF-1 CODE-DEFAULT** |
| Documented "default" | `PERSONAL_ASSISTANT.md:86` | claims `'true'` on Railway + locally | **F-WF-1 DOC-CLAIM MISMATCH** |
| Local dev enforcement | `Makefile:250, 262, 277, 288, 319` | `PA_USE_FUNCTION_CALLING=true` | correct |
| Production enforcement | `Procfile:23-30` | **NONE** — relies on Railway env config | **F-WF-2 PROCFILE GAP** |
| Startup log declaration | none | none | **F-WF-3 OBSERVABILITY GAP** |
| `[PA_TASK_SUMMARY]` routing_path field | `unified_pa_entrypoint.py:1288` | not present | **F-WF-4 OBSERVABILITY GAP** |

## 6. Hidden filters inventory

Not applicable — flag is binary, no filter axis.

## 7. Limits inventory

Not applicable at this layer.

## 8. Silent-truncation test

Not applicable.

## 9. Silent-filter test

Not applicable at the flag layer. The DOWNSTREAM silent-failure at `_generate_direct_response` is the class-of-defect this tool addresses.

## 10. Silent-fallback test

- **F-WF-1** (code default `'false'` vs doc claim `'true'`): silent-fallback risk if Railway env var ever cleared. Symptom: silent drop to keyword router.
- **F-WF-2** (Procfile gap): silent-fallback if Railway env var is not set — belt-and-suspenders would defend.
- **F-WF-3** + **F-WF-4** (observability gaps): silent-diagnosis gap when the fallback fires.

**DEFECT class (D2 + D4 — MEMORY rule crystallized failure still reproducible at HEAD without patch).**

## 11. Staleness test

Not applicable.

## 12. Freshness signal

Not applicable.

## 13. Provenance signal

Not applicable.

## 14. Authority / workspace assumptions

Not applicable at this layer.

## 15. Runtime dependencies

- Env var at worker start (Django reads on module import; can't be flipped live).
- Requires `pa` Celery queue configured (Procfile `celery-pa` line).
- Requires `unified_pa_entrypoint._run_agentic_loop` (Batch C tool 1 traced this).

## 16. Recoverable failure modes

- Flag-false with source='web': keyword router works for most intents (has if/elif branches for boardroom, content_review, etc.). Only `claude-code` short-circuit is broken.
- Flag-false with source='claude-code': **no recovery** — `_generate_direct_response` is text-only.

## 17. STOP-and-report failure modes

None at HEAD. F-WF-3 + F-WF-4 patches would introduce a STOP-and-observe surface via `[PA_TASK_SUMMARY].routing_path`.

## 18. Operator-action failure modes

- Misconfigured worker: requires operator restart with correct env (per MEMORY recipe).
- Docs-vs-code drift: requires either code default change or doc rewrite.

## 19. Existing test coverage

**Zero.** Verified via:

```bash
grep -l "PA_USE_FUNCTION_CALLING" core/tests/*.py  # → empty
```

The single feature gate for PA's entire tool surface has no test coverage.

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-WF-1 — Reconcile code default with documented default.**
  Two options:
  - **(a)** Flip code default from `'false'` to `'true'` in `settings.py:1662`.
    - Aligns with doc claim.
    - Behavior change on any deploy where the env var is unset: transitions to FC path.
    - Rigby-safe: FC path is the intended default per S1036.
  - **(b)** Keep code default `'false'` and rewrite the doc claim to say "Railway's env-var config sets it to true; there is no code default of true".
    - No behavior change.
    - Rigby-facing docs stay accurate.
  - **(c)** Both: flip code default AND update docs.
  - Recommendation: **(c)** — S1036 was the architectural watershed; keyword router is the intentional fallback, not the intentional default.

- **F-WF-2 — Add `PA_USE_FUNCTION_CALLING=true` to every celery-* line in Procfile.**
  Belt-and-suspenders against Railway env-var drift. Zero behavior change on correctly-configured deploys; defends against a silent regression if Railway env is ever cleared.

- **F-WF-3 — Startup-time flag-state log at `UnifiedPAEntrypoint` module scope.**
  ```python
  logger.info(
      "[PA_ROUTING_INIT] PA_USE_FUNCTION_CALLING=%s (function_calling=%s)",
      os.environ.get('PA_USE_FUNCTION_CALLING', 'unset'),
      settings.PA_USE_FUNCTION_CALLING,
  )
  ```
  Emitted once per worker at import time. A misconfigured worker is visible in the first ~50 lines of the worker log instead of only via `[PA_TASK_SUMMARY]` after a Rigby request fires.

- **F-WF-4 — Add `routing_path=fc|keyword` field to `[PA_TASK_SUMMARY]` log.**
  Same log line at `unified_pa_entrypoint.py:1288`; adds one field. Downstream log-parsers get the definitive signal without inferring from `tools=none intent=X`.

- **F-WF-5 — Regression tests.**
  New file `core/tests/test_pa_use_function_calling_env_validation_2728.py`:
  - Source-level guard: settings.py env-read default is exactly `'false'` (documents current state; future change requires opt-in).
  - Source-level guard: `Procfile` sets `PA_USE_FUNCTION_CALLING=true` on every celery-* line (after F-WF-2 patch).
  - Source-level guard: Makefile sets it on every celery target (verified-at-HEAD).
  - Behavior: with settings.PA_USE_FUNCTION_CALLING=False, `_process_message` for `source='claude-code'` takes the `_generate_direct_response` branch (source-inspection).
  - Log-shape guard: `[PA_TASK_SUMMARY]` format string includes `routing_path=%s` (after F-WF-4 patch).
  - Startup log guard: `[PA_ROUTING_INIT]` log emitted at module load (after F-WF-3 patch).

---

## Findings

### F-WF-1 — Code default `'false'` conflicts with doc claim `'true'`
- **Class:** DEFECT (D3 — documented behavior contradicts observed).
- **Evidence:** `settings.py:1662` default `'false'`; `docs/narratives/PERSONAL_ASSISTANT.md:86, 498` claims `'true'`.
- **Severity:** MEDIUM.
- **Action:** patch — flip code default AND update docs (Chris gate; recommendation (c)).

### F-WF-2 — Procfile lacks `PA_USE_FUNCTION_CALLING=true` on every celery-* line
- **Class:** DEFECT (D6 — worker/env dependency required at runtime but not declared).
- **Evidence:** `Procfile:23-30` — no line sets it. `Makefile:250, 262, 277, 288, 319` — every celery line sets it. Inconsistent between local and prod.
- **Severity:** HIGH — silent regression if Railway env-var ever cleared.
- **Action:** patch — add belt-and-suspenders env prefix to Procfile.

### F-WF-3 — No startup log declares flag state
- **Class:** DEFECT (D2 — silent config; requires reproducing a bad turn to diagnose).
- **Evidence:** grep confirms only the 2 read-sites and 1 declare-site.
- **Severity:** MEDIUM.
- **Action:** patch — emit `[PA_ROUTING_INIT]` log at UnifiedPAEntrypoint module scope.

### F-WF-4 — `[PA_TASK_SUMMARY]` doesn't include routing_path
- **Class:** DEFECT (D2 — S1184 diagnostic gap).
- **Evidence:** `unified_pa_entrypoint.py:1288-1297` — no `routing_path` field.
- **Severity:** MEDIUM.
- **Action:** patch — add `routing_path=fc|keyword` field.

### F-WF-5 — Zero test coverage
- **Class:** DEFECT (D9).
- **Evidence:** grep of `core/tests/*.py` for `PA_USE_FUNCTION_CALLING` — none.
- **Severity:** MEDIUM.
- **Action:** patch — add regression tests per §20.

### F-WF-6 — MEMORY rule accurate at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `feedback_pa_worker_function_calling_env` matches `settings.py:1662` + `unified_pa_entrypoint.py:989` + `Makefile` recipes at HEAD.
- **Severity:** N/A.
- **Action:** none. MEMORY rule remains VERIFIED.

---

## Verdict (Batch D tool 1 CLOSED)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** post-patch. Flag-True path was already verified-correct pre-patch (Batch C tool 5's `is_retryable` envelope applies). Flag-False path — the S1184-class silent-failure surface — is now (a) less likely to fire (code default flipped to `'true'`, Procfile declares explicitly on every celery-* line) and (b) detectable in ≤30 seconds via `[PA_ROUTING_INIT]` startup log or `[PA_TASK_SUMMARY].routing_path` telemetry.
- Regression tests added: `core/tests/test_pa_use_function_calling_env_validation_2728.py` — 10 tests (2 F-WF-1 code+doc guards; 1 F-WF-2 Procfile parity; 2 F-WF-3 startup log; 2 F-WF-4 task-summary field; 3 F-WF-6 MEMORY rule accuracy).
- Cross-tool regression: 258/258 substantive tests pass across all 16 validation-2728 files + `test_td_autofill_safety.py` + `test_pa_tool_args_malformed.py` (Batches A + B + C + D tool 1). Zero regressions.
- Docs updated: `docs/narratives/PERSONAL_ASSISTANT.md:86, 498` — 2 references to `F-WF-1` naming the current code default explicitly.
- Migration files: none.
- Follow-ups filed: none. F-WF-6 verifies the MEMORY rule at 3rd-verification-pass level.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-WF-1 | code default flipped to 'true' + narrative doc rewrite | `501a0669` |
| F-WF-2 | Procfile PA_USE_FUNCTION_CALLING=true on every celery-* line | `a649bc62` |
| F-WF-3 + F-WF-4 | [PA_ROUTING_INIT] startup log + [PA_TASK_SUMMARY].routing_path field | `79ab9173` |
| tests | 10 regression tests | `cf720ad0` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_pa_worker_function_calling_env`: **VERIFIED at HEAD post-patch**. The MEMORY rule accurately describes the residual failure surface (env-var-cleared workers still drop to keyword router) but the new patches make the incident-recovery diagnosis trivial. Rule remains VERIFIED — no annotation needed. F-WF-6 tests pin the Makefile + settings.py + unified_pa_entrypoint.py shape claims that the rule rests on.

### Design decision: code default `'true'` vs infra-only

Chris chose Option (c) — flip code default AND update docs AND declare in Procfile. Rationale:
- Session 1036 was the architectural watershed. Keyword router is the intentional fallback, not the intentional default.
- Code default `'true'` closes the doc-vs-code drift class F-WF-1 named.
- Procfile declaration (F-WF-2) keeps the intent visible in infra config so a future operator reading the Procfile doesn't have to trace to settings.py.
- Together the two changes are belt-and-suspenders: neither one silently regresses the other if a future refactor moves the default around.

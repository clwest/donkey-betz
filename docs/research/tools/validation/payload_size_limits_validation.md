# Payload-Size Limits — Validation Report

**Tool:** payload-size limits — the collection of cap thresholds, silent-truncation surfaces, and silent-fallback root causes across the PA dispatch pipeline that mediate the flow of large content payloads between Rigby's LLM, the tool_dispatcher, individual handlers, and the ToolCallRecord audit substrate.

**Files traced:**
- `core/services/unified_pa_entrypoint.py:85` — `TOOL_ARGS_MALFORMED_ERROR_CODE` constant.
- `core/services/unified_pa_entrypoint.py:163-202` — `_build_tool_args_malformed_envelope` (S1177 F1 fix).
- `core/services/unified_pa_entrypoint.py:2056-2102` — LLM tool-args JSON parse + typed-error envelope + skip-handler-dispatch.
- `core/services/unified_pa_entrypoint.py:2309-2379` — `_truncate_tool_output` smart JSON-aware truncator.
- `core/services/unified_pa_entrypoint.py:1821-1826, 1879-1883, 2026-2030` — fresh-summary block naive `[:4000]` truncations (F-PS-1 candidate).
- `core/services/unified_pa_entrypoint.py:2229` — main tool result envelope truncation (uses smart truncator; correct).
- `core/services/tool_dispatcher.py:937-984` — `_record_tool_call_sync` ToolCallRecord persistence (F-PS-2 candidate).
- `core/services/td_handlers_content.py:3355-3370` — content_tool 8000-char truncation with `_truncated: True` + `_full_size_bytes` envelope (verified correct).
- `core/services/td_handlers_content.py:4656, 4694` — `_handle_content` doc detail 5000-char truncation (F-PS-3 candidate).
- `core/settings.py:1102` — `DATA_UPLOAD_MAX_MEMORY_SIZE = 100MB` (Django HTTP request cap; not implicated).
- `core/tests/test_pa_tool_args_malformed.py` — S1177 F1 regression coverage.

**Downstream / upstream call sites:**
- Rigby's GPT-5.2 function-calling → arguments JSON string → `json.loads(arguments)` (unified_pa_entrypoint.py:2057).
- On parse failure → `_build_tool_args_malformed_envelope` + `continue` past dispatch (line 2102).
- On success → `tool_dispatcher.execute(payload=arguments)` (line 2192 for retry, elsewhere for main dispatch).
- Dispatch → handler → response → `_truncate_tool_output(json.dumps(result), 16000)` (line 2229).
- All dispatches → `_record_tool_call_sync(payload, result, ...)` → ToolCallRecord ORM row.
- Fresh-summary path (degenerate response + successful tool runs) → naive `[:4000]` truncation of tool_summary.

**Session validated:** S2730 (Batch C tool 2 of 5).
**HEAD at validation:** `1c09d7dc` (post-Batch-C-tool-1 close on feature branch).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (S1177 F1 regression suite already exists; new patches will add their own).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch C tool 2 of 5). Trace + 4 patches (F-PS-1 helper + F-PS-2a/2b migration + F-PS-3 envelope) + 21 regression tests complete; 161 total pass across all Batch A + B + C tools 1-2 validation-2728 files.

---

## 1. Intended purpose

The PA pipeline carries content payloads through five boundary layers:

1. **LLM → PA (arguments)** — GPT-5.2 emits tool-call arguments as a JSON string that must be parseable.
2. **PA → dispatcher (payload dict)** — parsed arguments become the dispatcher's `payload` argument.
3. **Dispatcher → handler (payload dict)** — payload is passed through the dispatcher unchanged.
4. **Handler → PA (result dict)** — handler returns a dict that becomes `ToolResult.result`.
5. **PA → LLM (output string)** — result is JSON-encoded and injected into the next LLM turn.

At each boundary, size caps and truncation semantics differ. The MEMORY rule `feedback_deliverable_tool_use_append_for_large_payloads` crystallized around a specific silent-fallback pattern at boundary 1→2: LLM output-token-budget truncation of `arguments` produced malformed JSON, the old `except: arguments = {}` fallback let an empty dict flow into the handler, and `deliverable_tool.update` silently defaulted to `action='list'`. S1177 F1 root-cause-fixed this at boundary 1.

**This tool's scope:** verify the S1177 F1 fix is intact at HEAD, sweep the remaining four boundaries for silent-truncation / silent-fallback surfaces, and patch the ones that violate §Ch6 D2 defect definition (silent-fallback without a `truncated: true` / `_truncated: bool` envelope signal).

## 2. Rigby's belief (per MEMORY + prior tool context)

Load-bearing MEMORY rules:
- `feedback_deliverable_tool_use_append_for_large_payloads` (RESOLVED at S1177; verified stale-at-HEAD Batch A tool 1 F-D-9) — Rigby was previously trained to prefer `*_append` over `update` for large writes.
- Historical rule preserved: "For deliverable_tool writes where the resulting total content size will exceed ~6kB, use `deliverable_tool append` instead of `deliverable_tool update`."

Rigby's current belief per the annotated MEMORY rule (RESOLVED status):
- Malformed args now produce a first-class `TOOL_ARGS_JSON_MALFORMED` envelope with `ok=False`, retry-hint pointing at `*_append`, and `args_len` telemetry — Rigby sees a loud typed error, not a silent list.
- **Silent-truncation surfaces beyond boundary 1 have NOT been swept.** Rigby's mental model is that the pipeline preserves fidelity at boundaries 2-5.

## 3. Constants / signatures (verbatim capture)

### 3.1 `_build_tool_args_malformed_envelope` (line 163-202)

```
{
    'ok': False,
    'error_code': 'TOOL_ARGS_JSON_MALFORMED',
    'tool_name': tool_name,
    'message': 'Tool-call arguments JSON could not be parsed (likely
                truncated by the LLM output token budget). Retry with
                a smaller payload — for large content writes prefer
                the *_append action over update.',
    'meta': {
        'arguments_len': args_len,
        'parse_error': parse_err_str,
        'arguments_excerpt_tail': raw_args[-200:],
    },
    'retry_hint': {
        'recommended_action': f"{tool_name}.append" if tool_name.endswith('_tool') else None,
        'max_chunk_chars_suggestion': 2000,
    },
}
```

### 3.2 `_truncate_tool_output(output: str, limit: int = 8000)` (line 2309-2379)

- Under-limit fast path: returns as-is.
- Parses JSON; finds main list field (`items`, `results`, `data`, `entries`, `records` OR first list-valued field with >1 items).
- Binary search for max item count that fits under `limit`.
- Adds `_truncated: {shown: int, total: int}` marker to the returned envelope.
- Fallback to raw slice if JSON parsing fails.
- **Called with `limit=16000` at line 2229** (main tool_result_inputs path).

### 3.3 `_record_tool_call_sync` size handling (`tool_dispatcher.py:937-984`)

- `result_str = json.dumps(result.result, default=str) if result.result is not None else ''`.
- `result_size = len(result_str.encode('utf-8', errors='replace'))`.
- `parameters=payload` (JSONField — no size cap on write path; Postgres JSONB no practical limit).
- `result_summary=result_str[:4096]` — **silent 4096-char truncation, no flag.**
- `result_hash=sha256(result_str)` — full hash even if truncated.
- `full_result=result_str if result_size <= 65536 else ''` — **silent drop-to-empty at 64kB, no flag.**
- `result_size_bytes=result_size` — canonical size marker preserved.
- `task_summary=f"[{trace_id}] dispatcher.execute"[:500]` — trace_id short in practice; never hits cap.

### 3.4 Fresh-summary block naive truncation (three sites)

- Line 1821-1826 (LLM-failed-with-successful-runs recovery):
  ```python
  tool_summary = json.dumps(
      [{'tool': ..., 'ok': ..., 'result': str(r.get('result', ''))[:4000]}
       for r in tool_runs],
      default=str
  )[:4000]
  ```
- Line 1879-1883 (degenerate text response recovery): identical pattern.
- Line 2026-2030 (duplicate-tool-call-sig degenerate loop break): identical pattern.

Each site truncates per-result at 4000 chars, then truncates the JSON-serialized summary AGAIN at 4000 chars. Silent double-truncation, no `_truncated` flag, can break JSON mid-object.

### 3.5 `_handle_content` doc content silent truncation

- Line 4656: `'content': doc.full_text[:5000]` — silent truncation, no `truncated: true` / `original_length: int` field.
- Line 4694: `'content': (doc.full_text[:5000] if doc else '')` — same pattern (second branch of same handler).
- Line 4677: `'document_preview': (s.document.full_text[:300] if s.document else '')` — 300-char "preview" is semantically explicit; NOT a defect.

## 4. Handler behavior (traced)

### 4.1 Boundary 1 → 2 (LLM → PA) — S1177 F1 fix verification

`unified_pa_entrypoint.py:2056-2102`:

```python
try:
    arguments = json.loads(fn.get('arguments', '{}'))
except (json.JSONDecodeError, TypeError) as parse_err:
    raw_args = fn.get('arguments', '') or ''
    error_envelope = _build_tool_args_malformed_envelope(...)
    logger.warning(f"[{trace_id}] tool args JSON parse failed: ...")
    fc_metadata.append({'name': tool_name, 'arguments': {}, 'call_id': call_id, 'ok': False})
    tool_result_inputs.append({
        'type': 'function_call_output',
        'call_id': call_id,
        'output': json.dumps(error_envelope),
    })
    tool_runs.append({'ok': False, ...})
    continue  # ← critical: skips handler dispatch
```

- **`continue` at line 2102 is the load-bearing invariant.** Without it, the handler would run with `arguments = {}` and default `action='list'` — recreating the S1176 silent fallback.
- **Test coverage:** `core/tests/test_pa_tool_args_malformed.py` pins the envelope shape + skip-handler behavior.
- **Verdict:** VERIFIED-CORRECT at HEAD.

### 4.2 Boundary 2 → 3 (PA → dispatcher) — no truncation

- Dispatcher accepts `payload: Dict[str, Any]` unchanged.
- No size cap on dispatcher input path.
- `parameters=payload` in `_record_tool_call_sync` writes the full payload to JSONField (no cap on write).
- **Verdict:** no defect.

### 4.3 Boundary 3 → 4 (dispatcher → handler) — handler-specific caps

Sweep of `td_handlers_*.py` for silent-truncation without envelope signal:

| Site | Cap | Semantic name | Envelope signal | Verdict |
|---|---|---|---|---|
| `td_handlers_content.py:3355-3370` | 8000 | `_truncated: True` + `_full_size_bytes` | YES | correct |
| `td_handlers_content.py:4656` | 5000 | `content` (no signal) | NO | **F-PS-3** |
| `td_handlers_content.py:4694` | 5000 | `content` (no signal) | NO | **F-PS-3** |
| `td_handlers_content.py:4677` | 300 | `document_preview` | implicit | correct |
| `td_handlers_core.py:305` | 200 | `content_preview` | implicit | correct |
| `td_handlers_core.py:2547` | 1000 | `chunk_text` | NO | **F-PS-3b candidate** |
| `td_handlers_core.py:2793, 2797, 2800, 3198` | 500 | `summary` / `error_message` | implicit | correct (semantic) |
| `td_handlers_core.py:3494` | 500 | `content_preview` | implicit | correct |

The pattern for "correct" is: field is named `*_preview` / `*_summary` — Rigby's mental model is that these are truncated. The pattern for defect is: field is named `content` / `chunk_text` — Rigby expects the full value.

### 4.4 Boundary 4 → 5 (handler → LLM output injection)

- `tool_result_inputs.append({'output': self._truncate_tool_output(output, 16000)})` at line 2229.
- Smart JSON-aware truncator with `_truncated: {shown, total}` envelope — the F-D-5 pattern predecessor.
- **Verdict:** VERIFIED-CORRECT.

### 4.5 Boundary 5 → 5 (fresh-summary re-summarization loops)

- Three sites at 1821, 1879, 2026 use naive `str(r.get('result', ''))[:4000]` per-result + `[:4000]` on the JSON-serialized summary.
- **F-PS-1**: naive slicing can break JSON mid-object (the exact anti-pattern `_truncate_tool_output` was designed to fix per S1065 docstring at line 2313). These blocks are used ONLY when the LLM has already degraded (empty response, degenerate content, duplicate-signature loop) so they're not on the happy path, but degraded turns are also the turns where operators most need fidelity.

### 4.6 Boundary orthogonal (ToolCallRecord audit substrate)

`tool_dispatcher.py:966-984`:

- **F-PS-2a** — `result_summary=result_str[:4096]` at line 972: silent truncation, no `summary_truncated: bool` field on the ToolCallRecord row. Since `result_size_bytes` is preserved and `result_hash` covers the full result, an operator CAN compute truncation from `len(result_summary) < result_size_bytes and result_size_bytes > 4096`. Effort required is above the "Rigby-safe" bar per §Ch8 R3.
- **F-PS-2b** — `full_result=result_str if result_size <= 65536 else ''` at line 977: silent drop-to-empty at 64kB. **No `full_result_dropped: bool` field.** An operator sees `result_size_bytes=100000, full_result=''` and cannot immediately tell if the result was genuinely empty (`None` upstream) vs blanked-for-size. This is a genuine analytics defect.

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| LLM arg parse fallback | `unified_pa_entrypoint.py:2057` | `'{}'` (default_str for `.get`) | dispatch-time |
| `_truncate_tool_output` limit | `unified_pa_entrypoint.py:2310` | 8000 | silent-truncation with `_truncated` envelope (safe) |
| Main tool_result_inputs limit | `unified_pa_entrypoint.py:2229` | 16000 (override) | silent-truncation with `_truncated` envelope (safe) |
| Fresh-summary per-result cap | `unified_pa_entrypoint.py:1823, 1880, 2027` | 4000 | **silent-truncation, no envelope** (F-PS-1) |
| Fresh-summary total cap | `unified_pa_entrypoint.py:1826, 1883, 2030` | 4000 | **silent-truncation, no envelope** (F-PS-1) |
| ToolCallRecord `result_summary` cap | `tool_dispatcher.py:972` | 4096 | **silent-truncation, no envelope** (F-PS-2a) |
| ToolCallRecord `full_result` drop-threshold | `tool_dispatcher.py:977` | 65536 (64kB) | **silent-drop-to-empty, no envelope** (F-PS-2b) |
| ToolCallRecord `task_summary` cap | `tool_dispatcher.py:983` | 500 | silent-truncation (never hits) |
| `_handle_content` doc content cap | `td_handlers_content.py:4656, 4694` | 5000 | **silent-truncation, no envelope** (F-PS-3) |
| Django HTTP body cap | `core/settings.py:1102` | 100MB | not implicated |
| Postgres JSONB / TEXT | ORM | no practical limit | not implicated |
| Celery Redis broker msg size | default | 512MB | not implicated |

## 6. Hidden filters inventory

None specific to payload-size (this tool is about caps, not filters). See Batch C tool 3 for hidden-filter sweep.

## 7. Limits inventory

Comprehensive; see §5.

## 8. Silent-truncation test

**Observable:**

- **F-PS-1** (fresh-summary blocks): three sites; naive `[:4000]` on both per-result content and total JSON summary; no `_truncated` flag; can break JSON mid-object.
- **F-PS-2a** (ToolCallRecord `result_summary`): 4096-char silent truncation, no `summary_truncated: bool` field on row.
- **F-PS-2b** (ToolCallRecord `full_result`): 64kB silent drop-to-empty, no `full_result_dropped: bool` field.
- **F-PS-3** (`_handle_content` doc detail): 5000-char silent truncation of `doc.full_text`, no `truncated: bool` / `original_length: int` field.

**Verdict:** four DEFECT sites (all D2 class per §Ch6). Contrasts with `_truncate_tool_output` (line 2229 call site) which properly surfaces `_truncated: {shown, total}`.

## 9. Silent-filter test

Not applicable — see Batch C tool 3.

## 10. Silent-fallback test

- **S1176 root cause** (deliverable_tool.update → action=list): **VERIFIED-RESOLVED-AT-HEAD.** S1177 F1 catches at line 2102 (`continue` past dispatch) + Batch A F-D-2/F-D-4 consolidated action inference in `td_handlers_content.py`.
- **Handler-default fallbacks** (missing action → `_default`): Batch A F-D-6/F-D-7 surface typed errors instead of defaulting. VERIFIED at HEAD.
- **No new silent-fallback surfaces** identified in this batch.

## 11. Staleness test

Not applicable — payload-size limits are static thresholds, not data freshness.

## 12. Freshness signal

Not applicable.

## 13. Provenance signal

Not applicable.

## 14. Authority / workspace assumptions

Not applicable at this layer. Payload-size caps do not scope by workspace.

## 15. Runtime dependencies

- No worker/env preconditions specific to this tool.
- `test_pa_tool_args_malformed.py` runs standalone via `SimpleTestCase`.

## 16. Recoverable failure modes

- LLM arg parse failure → typed envelope + retry hint (`recommended_action` → `*_append`; `max_chunk_chars_suggestion: 2000`). Rigby's LLM sees a first-class recoverable error.
- Fresh-summary block fires ONLY when the LLM has already degraded. Truncation there is a cost, not a failure per se.

## 17. STOP-and-report failure modes

- S1177 F1's `TOOL_ARGS_JSON_MALFORMED` envelope IS the STOP-and-report surface. `continue` skips dispatch; Rigby's LLM sees the failure verbatim.
- The remaining silent-truncation sites (F-PS-1/2/3) do NOT STOP-and-report. Post-patch: envelope signals to the caller so it CAN report.

## 18. Operator-action failure modes

- ToolCallRecord `full_result` drop (F-PS-2b): operator must reproduce the tool call to see the full result. Post-patch: `full_result_dropped: True` field makes this discoverable via analytics query.

## 19. Existing test coverage

- `core/tests/test_pa_tool_args_malformed.py` — 4 tests covering the S1177 F1 envelope shape + skip-handler behavior. **VERIFIED.**
- `_truncate_tool_output` — **zero unit tests.** The smart JSON-aware truncator has no coverage.
- `_record_tool_call_sync` — **zero unit tests.** ToolCallRecord persistence has no coverage.
- Fresh-summary blocks — **zero unit tests.** Degraded-turn recovery has no coverage.
- `_handle_content` doc content 5000-char cap — **zero unit tests.**

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-PS-1 — fresh-summary blocks switch to `_truncate_tool_output`.**
  Three sites use naive `[:4000]` slicing that can break JSON mid-object. The smart truncator was purpose-built for exactly this shape (S1065 docstring). Options:
  - **(a)** Replace each `str(r.get('result', ''))[:4000]` with `self._truncate_tool_output(json.dumps(r.get('result', ''), default=str), 4000)` per-result, and drop the outer `[:4000]`.
  - **(b)** Introduce a helper `_build_fresh_summary(tool_runs, per_result_limit=4000, total_limit=8000)` and call it from all three sites.
  - Recommendation: **(b)** — three sites is enough duplication to justify a helper; also raises total to 8000 (matches `_truncate_tool_output` default).

- **F-PS-2a — ToolCallRecord `result_summary` truncation signal.**
  Add a `summary_truncated: bool` computed field on the ORM write (True when `result_size > 4096`). No schema migration required if we surface via existing fields (`result_size_bytes > len(result_summary)` is derivable — but that's non-obvious). Options:
  - **(a)** Add `summary_truncated: bool` column via migration.
  - **(b)** Rely on derived comparison; document in the model docstring.
  - Recommendation: **(a)** minimal migration; unambiguous.

- **F-PS-2b — ToolCallRecord `full_result` drop signal.**
  Add a `full_result_dropped: bool` column. When `result_size > 65536` and `full_result=''`, flag it. Options:
  - **(a)** Column via migration + set at write time.
  - **(b)** Derived from `result_size_bytes > 65536 AND full_result = ''`. But `full_result` can also be legitimately empty (result is None). Ambiguous without the flag.
  - Recommendation: **(a)**.

- **F-PS-3 — `_handle_content` doc detail 5000-char truncation surface.**
  Two sites in `_handle_content` (lines 4656, 4694). Options:
  - **(a)** Add `content_truncated: bool` + `content_original_length: int` fields to the return dict when `len(doc.full_text) > 5000`.
  - **(b)** Rename `content` → `content_preview` + document the 5000-char cap in the schema description. Semantic rename; breaks Rigby's mental model less than a boolean flag.
  - **(c)** Remove the cap entirely; let downstream `_truncate_tool_output` handle overall response fidelity.
  - Recommendation: **(a)** — preserves field name Rigby expects + adds signal.

- **F-PS-4 — Additional handler-level content silent truncations (`td_handlers_core.py:2547` `chunk_text[:1000]`, others).**
  Scope call — Chris gate. Recommendation: **defer to a future batch-close doc pass** given this batch is targeting the specific "payload-size limits" scope. Log to combined batch-close observation list. **Not patching this batch.**

- **F-PS-5 — Add unit coverage for `_truncate_tool_output`, `_record_tool_call_sync`, fresh-summary helper, S1177 F1 skip-handler-dispatch invariant, `_handle_content` doc detail truncation.**
  These paths had zero coverage before this batch. First-coverage-at-HEAD analog to Batch B tools 2/3 and Batch C tool 1.

**Tests to add:** `core/tests/test_payload_size_limits_validation_2728.py` covering:
- `_build_tool_args_malformed_envelope` shape (extends existing coverage).
- `_truncate_tool_output` — under limit, over limit with `items` field, over limit with no known list key, non-JSON fallback, `_truncated` envelope shape.
- `_record_tool_call_sync` — small result (both fields populated), oversize summary (F-PS-2a signal), oversize full_result (F-PS-2b signal).
- Fresh-summary helper (F-PS-1 patch) — per-result truncation, total-summary truncation, JSON-integrity preservation.
- `_handle_content` doc detail — under-cap (no truncation signal), over-cap (F-PS-3 signal).
- Source-level guard: no `[:4000]` naive slicing remaining in fresh-summary blocks.

---

## Findings

### F-PS-1 — Fresh-summary blocks use naive `[:4000]` that can break JSON mid-object
- **Class:** DEFECT (D2).
- **Evidence:** `unified_pa_entrypoint.py:1821-1826, 1879-1883, 2026-2030`. S1065 docstring at `_truncate_tool_output:2313` explicitly documents this anti-pattern.
- **Severity:** MEDIUM (degraded-turn-only path; but degraded turns are when fidelity matters most).
- **Action:** patch — extract helper; switch to smart truncator.

### F-PS-2a — ToolCallRecord `result_summary` silent truncation, no signal
- **Class:** DEFECT (D2).
- **Evidence:** `tool_dispatcher.py:972` — `result_summary=result_str[:4096]`.
- **Severity:** MEDIUM.
- **Action:** patch — add `summary_truncated: bool` column.

### F-PS-2b — ToolCallRecord `full_result` silent drop-to-empty, no signal
- **Class:** DEFECT (D2 + D10).
- **Evidence:** `tool_dispatcher.py:977` — `full_result=result_str if result_size <= 65536 else ''`.
- **Severity:** MEDIUM.
- **Action:** patch — add `full_result_dropped: bool` column.

### F-PS-3 — `_handle_content` doc detail silent 5000-char truncation, no signal
- **Class:** DEFECT (D2).
- **Evidence:** `td_handlers_content.py:4656, 4694`.
- **Severity:** MEDIUM.
- **Action:** patch — add `content_truncated: bool` + `content_original_length: int` fields.

### F-PS-4 — Other handler-level content truncations across td_handlers_core (~5 sites)
- **Class:** DEFECT (D2) — sweep.
- **Evidence:** `td_handlers_core.py:2547` `chunk_text[:1000]` + adjacent sites.
- **Severity:** LOW-MEDIUM (semantically ambiguous field names).
- **Action:** **defer** to combined batch-close observation list (out of scope for this batch's "payload-size limits" target).

### F-PS-5 — Zero coverage of the payload-size machinery
- **Class:** DEFECT (D9).
- **Evidence:** grep of `core/tests/*.py` — only `_build_tool_args_malformed_envelope` has coverage.
- **Severity:** MEDIUM (the S1177 fix is well-tested; the surrounding surfaces are not).
- **Action:** patch — add unit test coverage per §20.

### F-PS-6 — S1177 F1 fix verified intact at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `unified_pa_entrypoint.py:2056-2102` with `continue` at 2102 preserved; `_build_tool_args_malformed_envelope` shape intact.
- **Severity:** N/A.
- **Action:** none. Update MEMORY rule `feedback_deliverable_tool_use_append_for_large_payloads` — already annotated RESOLVED at S1177; reinforce with this second-verification.

### F-PS-7 — `_truncate_tool_output` smart truncator verified correct at HEAD
- **Class:** VERIFIED-CORRECT.
- **Evidence:** `unified_pa_entrypoint.py:2309-2379` — smart JSON-aware truncator with `_truncated: {shown, total}` envelope.
- **Severity:** N/A.
- **Action:** none. Add unit coverage (see F-PS-5).

---

## Verdict (Batch C tool 2 CLOSED)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** (post-patch). Boundary 1 (LLM → PA args) verified Rigby-safe post-S1177. Boundaries 3, 4, and audit substrate now surface first-class truncation signals via envelope fields (F-PS-3 content signal) or dedicated ORM columns (F-PS-2a/2b).
- Regression tests added: `core/tests/test_payload_size_limits_validation_2728.py` — 21 tests covering F-PS-1/2a/2b/3/6/7 branches + envelope shape guards + source-level guards on removed anti-patterns.
- Cross-tool regression: 161/161 substantive tests pass across all 11 validation-2728 files (Batches A + B + C tools 1-2). Zero regressions.
- Docs updated: none (existing MEMORY rule `feedback_deliverable_tool_use_append_for_large_payloads` already annotated RESOLVED at Batch A tool 1 F-D-9; this batch verifies the fix is still in place at HEAD and hardens surrounding surfaces).
- Migration: `core/migrations/0379_toolcallrecord_truncation_signals.py` — adds `summary_truncated` + `full_result_dropped` boolean columns to `ToolCallRecord`, both indexed for analytics. Applied cleanly to local DB.
- Follow-ups filed: F-PS-4 (other td_handlers_core content silent-truncation surfaces) → combined batch-close observation list.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-PS-1 | fresh-summary helper + JSON-aware truncation | `0a85a492` |
| F-PS-2a + F-PS-2b | ToolCallRecord truncation signals + migration 0379 | `da7d4f62` |
| F-PS-3 | _handle_content doc detail envelope | `904f3857` |
| tests + envelope wrap | 21 regression tests + `{'runs': [...]}` envelope | `e943fc3b` |

### MEMORY rules reinforcement (per campaign plan §12.4)

- `feedback_deliverable_tool_use_append_for_large_payloads`: reinforced RESOLVED status. First verified stale-at-HEAD at Batch A tool 1 F-D-9; second verification at Batch C tool 2 F-PS-6 confirms the S1177 F1 fix (skip-handler-dispatch on malformed args + retry_hint at `*_append`) is intact and now has regression coverage on the source-level guard.

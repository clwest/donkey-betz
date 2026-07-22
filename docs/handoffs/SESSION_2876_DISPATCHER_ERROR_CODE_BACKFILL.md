# Session 2876 — Dispatcher-layer `error_code` backfill wrapper (Ledger #22.2 shipped)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-f515aa3ca81545d3` (labeled `s2876-cross-tool-error-envelope` per S2875 close's mint)
**Slate label:** S2876 — Rigby Tool Gap Ledger #22.2 (promoted from S2875 close 1st-trigger zoom-out fold)
**PRs:** #3375 (`1f0882d0a`) + `<docs cascade>` at close
**Combined regression:** 117/117 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876)

---

## Shipped

**PR #3375 `1f0882d0a` — S2876 slate (2 files, +262/-0)**

Adds a temporary compatibility bridge in `ToolDispatcher._execute_inner` that backfills `error_code='legacy_error'` on handler responses matching `{'error': msg}` without an `error_code`. Consumers now have a stable contract across the whole PA tool surface without every legacy tool being migrated first.

### Injection point

`core/services/tool_dispatcher.py` :: `ToolDispatcher._execute_inner`, between:
- L836-842 — Session 1085 PII scrub (`scrub_dict`)
- L843 — `logger.info(f"[{trace_id}] Tool {tool_name} completed in {latency_ms}ms")`
- L875 — `result_obj = ToolResult(ok=True, ..., result=result)` wrap

### Wrapper logic (5 lines + rate-limited breadcrumb)

```python
if (
    isinstance(result, dict)
    and result.get('error')
    and 'error_code' not in result
):
    result['error_code'] = 'legacy_error'
    _now = time.monotonic()
    _last = _last_legacy_backfill_warning.get(tool_name, 0.0)
    if _now - _last >= _LEGACY_BACKFILL_WARN_INTERVAL:
        _last_legacy_backfill_warning[tool_name] = _now
        logger.warning(
            "legacy_handler_error_envelope_missing_error_code — "
            "tool=%s action=%s trace=%s (backfilled with "
            "error_code='legacy_error'; migrate handler to "
            "S2874 structured envelope to eliminate backfill)",
            tool_name, action, trace_id,
        )
```

### Design refinements (Rigby pre-code SIGN, 5 tool_runs, all grounded via `repo_tool.read_file` + `repo_tool.search`)

| Question | Verdict | Resolution |
|---|---|---|
| F1: backfill value | F-BLOCKING | `'legacy_error'` (not `'unknown_error'` — distinct from future "truly unknown in migrated taxonomy") |
| F2: falsy error guard | F-BLOCKING | truthy `.get('error')` (not presence-of-key — safer default; skips success dicts that reserve `error` as nullable) |
| F3: non-dict guard | F-VERIFIED | `isinstance(result, dict)` matches existing dispatcher scrub behavior |
| F4: nested error scope | F-VERIFIED | Top-level only — nested `{result: {error: ...}}` is handler-domain shape |
| F5: outer envelope collision | F-VERIFIED | Outer `ToolResult.error_code` is dispatcher-level (`TOOL_TIMEOUT`/etc); inner `result['error_code']` is handler-level — two planes, no collision |

### Zoom-out fold — three mitigations shipped same-PR (anti-compat-blanket)

Rigby zoom-out ask surfaced entrenchment risk: backfill can become permanent compatibility layer that removes migration pressure. Mitigations:

1. **Rate-limited (60s per-tool) WARNING breadcrumb** — structured `legacy_handler_error_envelope_missing_error_code` message with `tool_name`, `action`, `trace_id`
2. **Combined into #1** — log serves as visibility counter; skip separate Redis counter to avoid `_global_total` pollution (single WARNING is greppable via `grep legacy_handler_error_envelope_missing_error_code` in logs)
3. **Inline sunset criteria** — module-level comment near `_last_legacy_backfill_warning` documents removal criteria: (a) all registered tools emit `error_code` on error envelopes, OR (b) breadcrumb fires < 1% of total dispatches for 14 consecutive days

### Test coverage

**`core/tests/test_s2876_dispatcher_error_code_backfill.py` — 13 tests across 4 test classes**

- `LegacyBackfillCoreCases` (5) — backfill fires / idempotence on migrated / success dict untouched / falsy `None` skipped / falsy `''` skipped
- `LegacyBackfillScopeCases` (2) — non-dict returns (str/list/int) untouched / nested error unmutated
- `OuterEnvelopeIsolationCases` (1) — outer `ToolResult.error_code` stays `None` while inner backfilled
- `BreadcrumbLoggingCases` (5) — WARNING emits once / rate-limited per-tool / per-tool independence / silent on migrated handler / silent on success dict

### Live E2E verification (Rigby post-code SIGN on live PA surface after `make recycle-all` to sha `1f0882d0a`)

Dispatched via live PA surface:
- `bpaas_tool.generate_close_pack {packet:{}}` → returned `{"success": false, "error": "packet is required", "error_code": "legacy_error"}` ✓

**F-VERIFIED**: backfill wrapper firing end-to-end on legacy handler.

---

## New observations from S2876 post-code live SIGN (1st trigger — do NOT auto-promote)

### #22.3 — Orthogonal contract axes in handler error responses

**What:** Some handlers return `{success: false, error: msg}`. Post-S2876 the `error_code` is now backfilled, but `success: false` was already there. Three orthogonal contract axes now live:
- outer `ToolResult.ok` (dispatcher-level)
- inner `result.success` (handler convention)
- inner `result.error_code` (S2874 + S2876 contract)

**Why it matters:** Consumers may key on one and ignore others; ambiguity increases as more tools migrate.

**Candidate resolutions:**
- **(A)** standardize handler errors on `{error, error_code, ...}` and drop `success: false` convention entirely
- **(B)** explicitly document `success` as legacy/noise while outer envelope + inner error fields are authoritative

**Trigger:** 1st (S2876 post-code SIGN, live PA surface via `bpaas_tool.generate_close_pack`) — do NOT auto-promote until 2nd independent trigger.

---

## Working loop observations at S2876

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 5 real `repo_tool` reads (not rubber-stamp); post-code SIGN Rigby ran 1 real live PA dispatch (F-VERIFIED end-to-end)
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code fold yielded 3 shipped mitigations (rate-limited warning, sunset criteria, structured log fields); post-code fold surfaced #22.3 orthogonal-contract-axes as new 1st-trigger observation
- `feedback_claude_rigby_agree_first_chris_yes_no` — reached agreement pre-code with 2 F-BLOCKING fold-ins (F1 `legacy_error`, F2 truthy guard); shipped without Chris re-routing
- `feedback_engineering_bias_over_audit` — net-new engineering ship, not audit
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=1f0882d0a49a, surviving=none`)
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response was 36.7KB, targeted continuation to fetch truncated zoom-out fold tail
- `feedback_local_truth_no_production` — 117/117 local pass IS the deploy step per Chris directive
- `feedback_rigby_writes_workspace_deliverables` — routed ledger #22.2 SHIPPED update + #22.3 candidate to Rigby PA (she executed `deliverable_tool.append`, verified via detail tail read); no ORM-direct write
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3375 with `--admin` flag
- **Candidate feedback rule (2nd trigger candidate — 1st was S2875):** Rigby will refuse destructive `deliverable_tool.update` operations on large content deliverables when the prior read was truncated; she asks explicitly for `Use append` or `Force update`. Watch for 3rd trigger before promoting as a Rigby-tool-surface UX pattern.

---

## Rigby Tool Gap Ledger updates

Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — Rigby-executed via `deliverable_tool.append` (2,861 chars, total 27,999 chars post-append; verified via `deliverable_tool.detail` tail slice at offset 25200 limit 3200):

- **#22.2 (dispatcher-layer error_code backfill wrapper)** → `shipped_in_pr_S2876` (2 files / +262 lines / 13 new tests / 117/117 combined regression / live F-VERIFIED via `bpaas_tool.generate_close_pack`)
- **#22.3 (orthogonal-contract-axes in handler error responses)** → new observation, 1st trigger, do NOT auto-promote

---

## Session pin lifecycle

- **S2876 open (this session):** used pin `pa-f515aa3ca81545d3` (labeled `s2876-cross-tool-error-envelope` — mint carried over from S2875 close ceremony via `chore(session): S2876 open — wrapper pin bump (#3374)` at `5ab2a9e36`)
- **S2876 close:** pin retires; fresh mint required at S2877 open per `feedback_session_open_atomic_mint_before_pa_dispatch`

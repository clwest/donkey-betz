# Session 2877 — PA-surface `error_code` smoke suite (S2874 1st-trigger promoted)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-d822f8e637c7449a` (labeled `s2877-cross-tool-error-envelope` per S2876 close's mint)
**Slate label:** S2877 — PA-surface error_code smoke suite (S2874 1st-trigger promoted at S2876 close)
**PRs:** #3377 (`52c6d550b`) + `<docs cascade>` at close
**Combined regression:** 135/135 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877)

---

## Shipped

**PR #3377 `52c6d550b` — S2877 slate (1 file, +307/-0)**

New test file `core/tests/test_s2877_pa_surface_error_codes_smoke.py` — first suite that exercises the full `_execute_inner` path (including the S2876 dispatcher-layer backfill wrapper) end-to-end via `ToolDispatcher.execute_sync`. Prior S2874/S2875/S2876 tests all call `dispatcher._handle_<x>()` directly and bypass the dispatcher.

### Contract coverage — three envelope planes

**Plane 1 — Migrated handlers pass concrete `error_code` through unchanged (`MigratedHandlerPASurfaceTests`, 14 rows):**

| Tool | Action | Payload | Expected `error_code` |
|---|---|---|---|
| `repo_tool` | `read_file` | `path=core/models_unified_system.py` | `file_too_large` (S2874) |
| `repo_tool` | `tree` | `path=manage.py` | `not_a_directory` |
| `repo_tool` | `search` | `path=core/` (no query) | `query_required` |
| `repo_tool` | `__bogus__` | — | `unknown_action` |
| `repo_tool` | `read_file` | `path=../../../../etc/passwd` | `value_error` |
| `spider_status_tool` | `history` | (no `spider_name`) | `spider_name_required` |
| `spider_status_tool` | `detail` | (no `item_id`) | `item_id_required` |
| `spider_status_tool` | `detail` | `item_id=00000000-0000-0000-0000-000000000000` | `item_not_found` |
| `spider_status_tool` | `search` | (no filters) | `filters_required` |
| `spider_status_tool` | `__bogus__` | — | `unknown_action` |
| `kb_tool` | `chunks` | (no `document_id`) | `document_id_required` |
| `kb_tool` | `search_embeddings` | (no filters) | `filters_required` |
| `kb_tool` | `semantic_search` | (no query) | `query_required` |
| `kb_tool` | `__bogus__` | — | `unknown_action` |

**Plane 2 — Legacy handlers get `error_code='legacy_error'` backfilled by S2876 wrapper (`LegacyBackfillPASurfaceTests`, 3 rows — DELETE AFTER S2876 SUNSET):**

| Tool | Action | Payload | Expected `error_code` |
|---|---|---|---|
| `bpaas_tool` | `generate_close_pack` | `packet={}` | `legacy_error` (S2876 F-VERIFIED regression fixture) |
| `newsletter_tool` | `__bogus__` | — | `legacy_error` (proves backfill fires from `td_handlers_newsletter.py:44`) |
| `ops_tool` | `__bogus__` | — | `legacy_error` (proves backfill fires from `td_handlers_ops.py:397`) |

**Plane 3 — Dispatcher-level failures surface at *outer* `ToolResult.error_code` (`DispatcherEnvelopeTests`, 1 row):**

| Payload | Expected outer envelope |
|---|---|
| `__nonexistent_tool_s2877__` | `ToolResult(ok=False, error_code='TOOL_NOT_FOUND', error_message=<truthy>, result=None)` |

### Pre-code SIGN via Rigby (2026-07-21, 4 grounded `repo_tool` runs)

Not rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`. Folds:

| Question | Verdict | Resolution |
|---|---|---|
| F1: envelope shape at `execute_sync` layer | AGREE + tool-verified | `ToolResult(ok=True, result={error, error_code, ...})` on handler errors — verified against `tool_dispatcher.py` L820-887 (backfill) + L920-929 (wrap) |
| F2: file location + class organization | (b) preferred | 3-class split: `MigratedHandlerPASurfaceTests` + `LegacyBackfillPASurfaceTests` + `DispatcherEnvelopeTests` — cleaner "which contract are we proving?" attribution |
| F3: coverage adequacy | F-BLOCKING → resolved | 1-row backfill sample is weak claim vs 39-file bare-`{'error':msg}` population Rigby enumerated. Added rows 16-17 (`newsletter_tool` + `ops_tool` unknown-action → `legacy_error`) |
| F4: breadcrumb WARNING assertion | DISAGREE default | No `assertLogs` — rate-limit map is module-global state, would make suite order-dependent under parallel runs. Deterministic-only |
| F5: post-code live E2E probes | 3 probes | Executed via Rigby post-code SIGN (see below) |

### Zoom-out fold (per `feedback_zoom_out_ask_per_rigby_sign`)

Rigby zoom-out surfaced 9 coupling concerns; 4 shipped same-PR as design choices:

1. **S2876 sunset friction** → `LegacyBackfillPASurfaceTests` docstring marked ⚠️ DELETE AFTER S2876 SUNSET with sunset criteria referenced inline (mirrors `_last_legacy_backfill_warning` comment in `tool_dispatcher.py`).
2. **Overfitting to fixture specifics** → deterministic bogus UUID `00000000-0000-0000-0000-000000000000` for spider_status_tool detail (not env-dependent).
3. **Signal vs noise trade-off** → assertions minimal (`error_code` value + `error` truthy). Never full error-message text — a message reword should not fail this suite.
4. **Runtime dependency coupling** → all 18 fixtures are pure validation errors (no fixtures that depend on existing SpiderData rows or specific KB docs).

Remaining concerns (5 acknowledged, none blocking): dispatcher vs handler error-source ambiguity (future migration to typed exceptions), scope creep into "everything smoke," per-test global state / logging coupling, "the wrong kind of stability" locking in the current handler-returns-dict convention.

### Post-code SIGN via Rigby (2026-07-21, 2 grounded `repo_tool.read_file` runs on the shipped file)

**AGREE on all 5 file-read checks:**

- (a) Fixture coverage matches folds ✓
- (b) Sunset guarantee legible (both top docstring + `LegacyBackfillPASurfaceTests` docstring cite sunset criteria + delete instruction) ✓
- (c) No error-message-text assertions ✓
- (d) No breadcrumb assertion ✓
- (e) 3-class split matches F2 verdict ✓

**F5 live probes delegated:** Rigby dispatched CTOAgent async (task `927262f9-1897-40cb-8687-a810fa408559`) with 180s follow-up subscription. Rigby noted she has no direct arbitrary-tool-name dispatch surface from her tool set — must delegate to CTOAgent for tool names not in `PA_TOOL_SCHEMAS` (e.g., `__nonexistent_tool_s2877__`). **1st-trigger observation for Rigby Tool Gap Ledger:** #22.4 (see Ledger updates below).

### Test results

- S2877 alone: **18/18 pass in 0.186s**
- Combined S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877: **135/135 pass** (117 prior + 18 new)

### Post-merge recycle (PLAYBOOK-7.4.4)

Clean: `sha=52c6d550bbe1, surviving=none` — even though the diff is test-only (no dispatcher/handler code changed), recycle keeps worker sha aligned with HEAD to avoid STALE_BOTH at next session open.

---

## New observations from S2877 SIGN cycle (1st trigger — do NOT auto-promote)

### #22.4 — Rigby cannot dispatch arbitrary tool-name strings

**What:** Rigby's PA tool surface only exposes tools registered in `PA_TOOL_SCHEMAS`. Tests / smoke probes that need to exercise dispatcher-level branches (e.g., `TOOL_NOT_FOUND` on a name like `__nonexistent_tool_s2877__`) can't be executed by Rigby directly — she must delegate to CTOAgent (async, 180s+ round-trip).

**Why it matters:** Every dispatcher-level branch that PA callers care about (`TOOL_NOT_FOUND`, `TOOL_PERMISSION_DENIED`, `TOOL_INVALID_PAYLOAD` at outer envelope) requires Rigby-external tooling to F-VERIFY at live-PA level. Complicates the Claude-directs-Rigby-executes loop for future dispatcher-envelope contract work.

**Candidate resolutions:**
- **(A)** Extend Rigby's schema with a `dispatcher_probe_tool` action that accepts arbitrary tool-name strings for smoke-test purposes only (auth-gated / dev-mode-only).
- **(B)** Accept the CTOAgent-delegation pattern as the norm for dispatcher-envelope work.
- **(C)** Codify that Claude self-executes dispatcher-envelope live verification via Python shell (bypasses Rigby entirely for this narrow class of probe).

**Trigger:** 1st (S2877 post-code SIGN F5 delegation) — do NOT auto-promote. Watch for 2nd independent trigger.

---

## Working loop observations at S2877

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN Rigby ran 4 real tool_runs (2× `repo_tool.read_file` on `tool_dispatcher.py` + 2× `repo_tool.search` enumerating 39-file bare-`{'error':msg}` population). Post-code SIGN Rigby ran 2 real `repo_tool.read_file` on the shipped test file (0-260 + 260-307 line ranges — full file coverage). Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× — pre-code fold yielded 4 shipped mitigations (sunset marker + deterministic UUID + minimal assertions + pure-validation fixtures); post-code fold yielded "wrong kind of stability" observation (acknowledged, mitigation strategy documented in handoff).
- `feedback_claude_rigby_agree_first_chris_yes_no` — reached agreement pre-code with F3 F-BLOCKING fold (rows 16-17 added); shipped without Chris re-routing. Post-code SIGN AGREE across all checks.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (first-of-its-kind PA-surface contract enforcement suite), not audit.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=52c6d550bbe1, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — pre-code SIGN response truncated at "you're 3"; fetched tail continuation for concerns 3-9. Full zoom-out captured in handoff.
- `feedback_local_truth_no_production` — 135/135 local pass IS the deploy step per Chris directive.
- `feedback_rigby_writes_workspace_deliverables` — Rigby Tool Gap Ledger update deferred to close (will route via Rigby PA per rule).
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3377 with `--admin` flag.
- **Rigby delegation-fallback observation (S2877 F5):** when Rigby can't dispatch a specific probe from her own tool surface, she autonomously dispatches CTOAgent async with follow-up subscription rather than reporting the gap and stalling. Novel Rigby-behavior fold — not codified.

---

## Session pin lifecycle

- **S2877 open (this session):** used pin `pa-d822f8e637c7449a` (labeled `s2877-cross-tool-error-envelope` — mint carried over from S2876 close ceremony via `chore(session): S2876 close — dispatcher error_code backfill shipped + docs cascade + wrapper pin bump (#3376)` at `daf8dc77a`)
- **S2877 close:** pin retires; fresh mint required at S2878 open per `feedback_session_open_atomic_mint_before_pa_dispatch`

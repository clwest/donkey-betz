# Session 2874 — repo_tool.read_file large-file paging (Ledger #2 promote)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-54eed7894ce845ed` (labeled `s2874-repo-tool-read-file-paging`)
**Slate label:** S2874 — Rigby Tool Gap Ledger #2 (promoted from 2nd trigger at S2873)
**PR shipped:** #3369 (SHA `cc889af1f`)
**Combined regression suite:** S2869 + S2870 + S2871 + S2872 + S2873 + S2874 → **86/86 pass**
**Moratorium status:** D6 in force (no new strategic discovery arcs)

---

## What shipped

Extended `repo_tool.read_file` at `core/services/td_handlers_gateway.py:182-284` with an `allow_large=True` opt-in that lifts the 500KB soft cap for paged reads. Prior behavior: the hard byte cap short-circuited BEFORE the existing `start_line`/`max_lines` paging params fired, leaving files like `core/models_unified_system.py` (~760KB) unreachable via `read_file` at all.

### Response-shape changes

**Default over-cap path — new structured envelope:**

```json
{
  "error": "File too large: 760983 bytes (soft max 500000). Set allow_large=true to opt into paged read (start_line + max_lines still apply), or use search instead.",
  "error_code": "file_too_large",
  "path": "core/models_unified_system.py",
  "file_size_bytes": 760983,
  "size_hard_max": 500000,
  "narrowing_hint": {"set_allow_large": true, "suggested_max_lines": 200}
}
```

**`allow_large=true` paged path (large file):**

```json
{
  "action": "read_file",
  "path": "core/models_unified_system.py",
  "file_size_bytes": 760983,
  "start_line": 100,
  "end_line": 125,
  "lines": 25,
  "total_lines_known": false,
  "truncated": true,
  "content": "101: ..."
}
```

**Small-file path (below soft max) — preserved + shape parity:**

```json
{
  "action": "read_file",
  "path": "core/services/tool_dispatcher.py",
  "file_size_bytes": 63271,
  "start_line": 0, "end_line": 200, "lines": 200,
  "total_lines": 1360,
  "total_lines_known": true,
  "truncated": true,
  "content": "1: ..."
}
```

**Error envelope consistency:** local `_read_file_error(code, message, **fields)` helper unifies `path_required` / `file_not_found` / `file_too_large` under a single `{error, error_code, ...}` shape.

**Warning path:** 0-line responses (past EOF or empty file) carry `warning_code='start_line_past_eof_or_empty_file'` — soft field, not a hard error, so scripts can branch on shape instead of exception class.

### Schema

`core/services/pa_tool_schemas.py:4379` adds `allow_large: boolean` to `repo_tool` with a description that documents opt-in intent + the `total_lines_known=false` perf tradeoff.

### Test coverage

New file `core/tests/test_s2874_repo_tool_read_file_paging.py` — **13 tests across 4 test classes**:

- `RepoReadFileLargeFileDefaultTests` × 3 — structured error envelope on a 760KB file (`error_code`, `path`, `file_size_bytes`, `size_hard_max`, `narrowing_hint`).
- `RepoReadFileLargeFilePagingTests` × 4 — first-page read, mid-file paging (`start_line=500, max_lines=50`), `max_lines` hard cap still enforced, `start_line` past EOF returns `warning_code`.
- `RepoReadFileSmallFileTests` × 3 — default behavior preserved, `file_size_bytes` present, `allow_large=True` is a no-op below the soft max.
- `RepoReadFileEnvelopeShapeTests` × 3 — missing path, file not found, `file_too_large` all use the same envelope shape.

---

## Discovery arc — 2 SIGN cycles

### Pre-code SIGN

**F-AGREE ×4** — 4 refinements folded in before writing code:

- **Q1:** default remains `allow_large=False`; over-cap responses gain structured envelope with `path` (Rigby's minor add for log context).
- **Q2:** skip the `total_lines` second-pass **unconditionally** when `size > 500_000`, even in opt-in mode. No operator should pay double I/O for metadata. Distinct `total_lines_known` bool (don't overload `truncated`).
- **Q3:** `start_line` past EOF → soft `warning_code`, not a hard error. Script-friendly empty result. Rigby DISAGREED with Claude's "distinct error_code" option.
- **Q4:** local `_read_file_error` helper for envelope consistency. **Do NOT retrofit `tree`** — different failure modes need different knobs (fanout, recursion, symlinks).

### Post-code SIGN (first attempt caught stale worker)

**Initial dispatch FAILED all 3 executable Qs** — Rigby's live surface returned the pre-S2874 string error `{"error": "File too large: 760983 bytes. Use search instead."}`. Root cause: PA workers ran from `/Users/donkeyking/development/unified-donkey-betz/` at pre-merge SHA `4931b40b0`, not from the checkout where I merged. Fix: `cd /Users/donkeyking/development/unified-donkey-betz && git pull --ff-only && make restart` (Daphne + 5 Celery workers + Beat all recycled).

### Post-code SIGN (retry after recycle) — **F-AGREE ×4** all live tool_run outputs match spec

- **Q1 PASS:** `error_code='file_too_large'`, `file_size_bytes=760983`, `size_hard_max=500000`, `narrowing_hint.set_allow_large=true`, message mentions `allow_large=true` explicitly.
- **Q2 PASS:** exactly 25 lines, `start_line=100`, `end_line=125`, `total_lines_known=false`, `truncated=true`, first line prefix `101:`.
- **Q3 PASS:** `total_lines=1360`, `total_lines_known=true`, no `warning_code`, `file_size_bytes=63271` present.
- **Q4 zoom-out:** 4 candidate folds surfaced — see below.

---

## Zoom-out folds observed (per `feedback_zoom_out_ask_per_rigby_sign`)

All logged for future ledger review; **none shipped this slate**.

1. **Cross-tool structured-error-envelope migration (2nd trigger).** Fold #2 from pre-code SIGN ("structured error envelopes over string errors") now has 2 data points — this ship as reference implementation + the observation that most other tool handlers still return `{"error": "..."}` strings without machine-actionable codes. Candidate ledger entry: "Tool error envelope standardization across `td_handlers_gateway` actions." Minimal scope: read-path handlers first (`repo_tool.tree/search`, `kb_tool`, `spider_status_tool.search/detail`).

2. **Extract `td_error.py` shared helper.** Once a 2nd tool adopts the structured-envelope pattern, promote `_read_file_error` from local to a gateway-layer helper `tool_error(error_code, message, **fields)` with an optional `narrowing_hint` convention. Waiting for the 2nd adopter before extracting.

3. **PA-surface-level smoke test.** The stale-worker false negative I just hit (unit tests pass + merge complete + live surface still stale until recycle) is a repeatable failure mode. A lightweight smoke suite that dispatches through the PA tool surface (not just handler unit tests) would catch it immediately. **1st trigger — high signal, worth watching for a 2nd.**

4. **`max_chars` cap + `binary_mode` guardrail.** Future refinements to `read_file` for pathological one-huge-line files and accidental binary reads. Neither has a live trigger — parked as awaiting-signal.

Also noted (not a new ledger entry — clarification): the `truncated` + `total_lines_known` pairing is now the canonical shape for tools that add paging later. Worth mentioning if a 2nd tool needs it.

---

## Working-loop observations

- **`feedback_verify_rigby_tool_runs_before_trusting_sign`** — fired 1× (first post-code SIGN dispatch showed stale surface; verified against live tool_runs, caught the discrepancy immediately, drove the recycle).
- **`feedback_read_full_rigby_response_not_just_tail`** — fired 2× (initial pre-code SIGN response truncated at Q4 tail; retry-SIGN Q4 also truncated). Both times fetched full response by explicit re-ask.
- **`feedback_zoom_out_ask_per_rigby_sign`** — fired 2× (both SIGN cycles). Yielded 4 candidate folds; 1 has 2nd trigger (structured envelopes cross-tool), rest are 1st trigger.
- **`feedback_claude_rigby_agree_first_chris_yes_no`** — presented Chris one recommendation ("ship #2 alone") + one implementation approval ("proceed with Rigby refinements folded in"). Both approved.
- **`feedback_recycle_after_merge`** (PLAYBOOK-7.4.4) — post-merge recycle **did NOT happen automatically** because the running services live in a different checkout (`development/`) than the one Claude was merging in (`Donkey_Betz/`). Recycle completed via `git pull --ff-only && make restart` in the `development/` checkout — this crossed the "shared state" gate but is the standing pattern per prior handoffs. `sha=cc889af1f, surviving=none`.
- **`feedback_engineering_bias_over_audit`** — net-new engineering ship. No audit lean.
- **`feedback_rigby_writes_workspace_deliverables`** — Rigby Tool Gap Ledger update executed by Rigby via PA `deliverable_tool.append` at close (see below).

**New working-loop observation (candidate for future feedback rule):** the running-services-in-different-checkout situation makes `feedback_recycle_after_merge` a 2-step operation (pull the OTHER checkout, then recycle). Watching for a 2nd trigger before formalizing.

---

## Rigby Tool Gap Ledger updates

- **Deliverable ID:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` ("Rigby Tool Gap Ledger")
- **New section:** "S2874 slate close — #2 promoted + shipped" (planned to append at close)
- **Route:** Rigby via `deliverable_tool.append` per `feedback_rigby_writes_workspace_deliverables`

---

## Session pin lifecycle

- **Pin at S2874 open:** `pa-54eed7894ce845ed` (labeled `s2874-repo-tool-read-file-paging`)
- **Pin retires at S2874 close.** Fresh mint required at S2875 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.
- **Wrapper (`tools/pa_local.sh`) bump:** committed in the docs cascade PR at close per `feedback_commit_wrapper_pin_bump_at_close`.

---

## For S2875 open

See `00-START-NEXT-SESSION.md` refreshed at S2874 close. Ledger #2 cleared; observations surfaced above are 1st-trigger only (except structured-envelope cross-tool migration at 2nd trigger).

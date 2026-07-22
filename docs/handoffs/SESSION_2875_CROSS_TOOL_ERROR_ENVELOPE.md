# Session 2875 — Cross-tool structured-error-envelope migration (Ledger #2 shipped)

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-158b00decda0491d` (labeled `s2875-cross-tool-error-envelope`)
**Slate label:** S2875 — Rigby Tool Gap Ledger #2 (promoted from 2nd trigger at S2874 close)
**PRs:** #3372 (`a89dc0a001e4`) + `<docs cascade>` at close
**Combined regression:** 104/104 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875)

---

## Shipped

**PR #3372 `a89dc0a001e4` — S2875 slate (4 files, +405/-17)**

Extends S2874's structured-error-envelope shape (`{error, error_code, ...optional_fields}`) from `repo_tool.read_file` to 3 sibling read-path handlers. **17 migration sites** across the 3 handlers:

### `repo_tool` (`core/services/td_handlers_gateway.py`) — 5 sites

| Line | Path | Error code |
|---|---|---|
| 126 | tree not-a-directory | `not_a_directory` |
| 286 | search query missing | `query_required` |
| 428 | shared unknown-action catcher | `unknown_action` |
| 431 | shared ValueError catcher | `value_error` |
| 449 | shared generic-exception catcher | `internal_error` |

### `spider_status_tool` (`core/services/td_handlers_ops.py` `_handle_spider_status`) — 6 sites

| Line | Path | Error code |
|---|---|---|
| 6490 | history missing spider_name | `spider_name_required` |
| 6514 | detail missing item_id | `item_id_required` |
| 6518 | detail item not found | `item_not_found` |
| 6536 | search missing all filters | `filters_required` |
| 6581 | shared unknown-action catcher | `unknown_action` |
| 6585 | shared generic-exception catcher | `internal_error` |

### `kb_tool` (`core/services/td_handlers_ops.py` `_handle_kb_browse`) — 6 sites

| Line | Path | Error code |
|---|---|---|
| 7164 | chunks missing document_id | `document_id_required` |
| 7183 | search_embeddings missing filters | `filters_required` |
| 7222 | semantic_search missing query | `query_required` |
| 7418 | shared unknown-action catcher | `unknown_action` |
| 7422 | shared generic-exception catcher | `internal_error` |

**Envelope contract (matches S2874 exactly):**
```json
{"error": "<human-readable>", "error_code": "<machine-readable>", "...optional_fields": "..."}
```

No `success: false` key. Original proposal was corrected in-flight after Rigby Q2 verified S2874's actual shape.

**Helper design (Q3=A DEFER extraction):**
- One module-level `_tool_error(code: str, message: str, **fields)` helper per file (`td_handlers_gateway.py` + `td_handlers_ops.py`).
- Do NOT extract to shared `td_error.py` gateway helper until 6+ adopters stable — signature-churn risk if extracted before shapes empirically settle.
- S2874's local `_read_file_error` left in place (zero retrofit).

**Test file:** `core/tests/test_s2875_cross_tool_error_envelope.py` — **18 tests across 4 test classes** (repo_tool 5 + spider_status_tool 6 + kb_tool 4 + cross-tool envelope-shape parity 3).

---

## Discovery arc — 3 SIGN cycles

### Pre-code SIGN (Rigby, 12 real tool_runs across 3 turns)

**Q1 [F-BLOCKING if wrong]** — verify current error shapes at 5 target handlers.
- Turn 1: Rigby delivered evidence for repo_tool.tree + repo_tool.search only (window limit). kb_tool + spider_status_tool marked as F-blocking incomplete.
- Turn 2: continuation for kb_tool + spider_status_tool. **Discovery: 5 within-handler sites Rigby's initial pass missed** — kb.chunks, kb.search_embeddings, kb.semantic_search, spider_status.history. Scope expanded 11 → 17 for internal consistency.

**Q2 [F-BLOCKING if wrong]** — verify S2874 reference implementation shape.
- Rigby confirmed S2874's `_read_file_error` returns `{error, error_code, ...}` — NO `success: false` key. Proposal envelope corrected in-flight (dropped `success: false` from the plan).

**Q3 [F-AGREE — design call]** — extract `td_error.py` helper this slate or defer?
- Rigby verdict = **A (DEFER)**. Reasoning: signature churn risk real (kb_tool may need extra structured fields like `filters_applied` / `session_resolution_hints`); locality proven in S2874; lower refactor blast radius. Extract when 6+ real adopters stable + shape is empirically confirmed.

**Q4 [ZOOM-OUT — mandatory]** folded 3 concerns:
- **(a) Downstream consumers:** Adding `error_code` is additive-safe; wording changes in `error` message are the real risk. Preserved exact error message text at all 17 sites per this fold.
- **(b) Coupling risk without shared contract test:** Entropy tax + unreviewable "consistency" claims + hard-to-debug regressions. Mitigated via `CrossToolEnvelopeShapeParityTests` — 3 tests assert every migrated site returns the shape (error present + error_code snake_case + no success key).
- **(c) Envelope adequacy:** S2874 shape is adequate for HARD-FAIL migration in this slate. Partial-success `warnings:[]`/`errors:[]` convention deferred until first real trigger (spider_status with per-spider filter rejections, or kb multi-collection search with per-source errors).

### Post-code SIGN (Rigby, live PA tool surface)

- ✅ **`repo_tool.tree` path=manage.py**: `{error: "Not a directory: manage.py", error_code: "not_a_directory", path: "manage.py"}` — F-VERIFIED
- ✅ **`spider_status_tool.detail`** (missing item_id): `{error: "item_id required for detail action", error_code: "item_id_required"}` — F-VERIFIED
- ✅ **`repo_tool.search`** (missing query): `{error: "query is required for search", error_code: "query_required"}` — F-VERIFIED
- ⚠️ **`kb_tool` unknown_action**: F-BLOCKED at schema validation layer — kb_tool's `action` param is enum-constrained in the PA tool schema, so GPT-5.2 cannot dispatch an invalid action string; handler's `unknown_action` branch is unreachable via the PA tool surface. **New finding: schema-level dead branches** (1st trigger — see below).

**Q_ZOOM post-code fold:** mixed-mode consumer friction. Once some tools emit `error_code` reliably, consumers may branch on it and hit sibling tools still returning string-only errors. Rigby recommended a dispatcher-layer wrapper that backfills `error_code='unknown_error'` on legacy `{error}` responses to give consumers a stable contract during mid-migration. **New 1st-trigger candidate** — see below.

---

## Working loop observations at S2875

- `feedback_verify_rigby_tool_runs_before_trusting_sign` fired 3× (12 tool_runs total, all grounded).
- `feedback_zoom_out_ask_per_rigby_sign` yielded 2 usable folds — 1 applied inline (Q4b contract test), 1 promoted to ledger candidate (dispatcher backfill wrapper).
- `feedback_claude_rigby_agree_first_chris_yes_no` — presented Chris one recommendation with envelope-shape correction (dropped `success: false`).
- `feedback_engineering_bias_over_audit` — net-new engineering ship, not audit.
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge in `development/` checkout (`sha=a89dc0a001e4, surviving=none`).
- `feedback_read_full_rigby_response_not_just_tail` — hit stdout truncation TWICE (mid-Q3 + mid-Q4b); re-fetched via targeted continuation asks. No `### Important note` prose was hidden — genuine tool-response length overflow.
- `feedback_local_truth_no_production` — 104/104 local pass IS the deploy step per Chris directive.
- **New candidate rule (1st trigger):** stdout-truncation-forces-continuation is a Claude execution-context tax that inflates SIGN cycle count. Watch for 2nd trigger before formalizing.

---

## New Rigby-observed tool-surface gaps (candidates for future ledger entries)

1. **Schema-level dead branches** (1st trigger). Handlers with enum-constrained `action` params in PA tool schema — `kb_tool` (5 valid actions), `repo_tool` (4 valid actions), `spider_status_tool` — cannot have their `unknown_action` branches exercised via the PA tool surface (GPT-5.2 rejects at schema validation). Migration is correct per unit tests, but the branch is unreachable in the live path. Not necessarily dead code (batch callers, buggy code, direct handler invocation still hit it), but worth documenting reachability class.
2. **Dispatcher-layer `error_code` backfill wrapper** (1st trigger, Rigby zoom-out). A lightweight dispatcher wrapper could backfill `error_code='unknown_error'` on any tool response that has `error` but no `error_code`, giving consumers a stable contract during mid-migration. Would eliminate the "hit sibling tool with old shape, crash on assumed key" failure mode.

## Rigby Tool Gap Ledger update (via Rigby PA per `feedback_rigby_writes_workspace_deliverables`)

- Deliverable ID `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **#2 (structured-error envelope migration)** → `shipped_in_pr_S2875` (17 sites / 3 files / 18 tests / 104/104 combined regression)
- Two new zoom-out observations logged (schema-level dead branches + dispatcher backfill wrapper)

---

## What's NOT shipped (deferred to S2876+)

- **Extract `td_error.py` gateway helper** — 6 adopters stable now (S2874 + 3 handlers × 5 codes ≈), but Rigby Q3=A said wait until "shapes empirically settle." Watch for a surprising new envelope shape before extracting.
- **Dispatcher-layer backfill wrapper** (Rigby zoom-out 1st trigger).
- **Schema-level dead branches investigation** (1st trigger).
- **PA-surface-level smoke test** (still 1st trigger from S2874 close).
- **`feedback_recycle_after_merge` multi-checkout extension** (still 1st trigger from S2874 close).
- All prior deferred items from S2871/S2868/S2867/S2866/S2862/S2861/etc still carried.

---

## Files changed

```
core/services/td_handlers_gateway.py               | 45 ++++++++++++++++---
core/services/td_handlers_ops.py                   | 84 +++++++++++++++++++++++++++++++-----
core/tests/test_s2875_cross_tool_error_envelope.py | 291 +++++++++++++++++++++
tools/pa_local.sh                                  |  2 +-
4 files changed, 405 insertions(+), 17 deletions(-)
```

---

## Next session

**Fresh session (S2876) opens with:**
1. Session-open atomic mint per `feedback_session_open_atomic_mint_before_pa_dispatch`
2. Net-new engineering slate pick (per `feedback_engineering_bias_over_audit`)
3. D6 moratorium still in force

**Top slate candidates for S2876:**
1. **Dispatcher-layer `error_code` backfill wrapper** (Rigby zoom-out 1st trigger — highest signal from S2875).
2. **PA-surface-level smoke test** (1st trigger from S2874; would catch stale-worker false negatives immediately + verify migrated envelopes end-to-end).
3. **Schema-level dead-branch investigation** (1st trigger — audit which handler branches are unreachable via the PA schema layer).

See `00-START-NEXT-SESSION.md` for the full deferred queue.

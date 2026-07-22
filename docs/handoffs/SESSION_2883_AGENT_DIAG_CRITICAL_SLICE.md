# Session 2883 — agent-diag family critical-slice structured error-envelope migration

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-5b237166eeb34070` (labeled `s2882-ops-execution-auth-critical-slice`; minted during S2882 docs cascade PR #3389, carried into S2883 open per steady-cadence shape)
**Prior pin retired at S2882 open:** `pa-aae31b596346411e`
**Slate label:** S2883 — agent-diag family critical-slice error-envelope migration (Slate 3)
**PRs:** #3390 (`ca61c7725`) + `<docs cascade>` at close
**Combined regression:** 200/200 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + S2880 + S2881 + S2882 + **S2883** + `test_zoom_out_tool_2780`)

---

## Shipped

### PR #3390 `ca61c7725` — S2883 slate (2 files, +396/-10)

- **`core/services/td_handlers_ops.py`** (+59/-10) — 10 sites migrated across 4 handler methods / 4 tool surfaces. Reused the S2879 `_handler_error` helper at L48 for 6 sites; reused the S2875 `_tool_error` helper at L28 for 4 broad-except sites. No new helper introduced.
- **`core/tests/test_s2883_agent_diag_error_envelope.py`** (NEW, 337 lines) — 10 test rows exercising full `ToolDispatcher.execute_sync` path via all 4 tool surfaces. Reuses the S2879 `_assert_migrated_envelope` helper for 6 rows; local `_assert_internal_error_envelope` helper for the 4 broad-except rows (matches the S2875 `_tool_error` shape).

### Migration diff — 10 sites × 4 codes × 4 handlers × 4 dispatched tools

| Handler | Site | Prior return shape | New `error_code` | Helper | Dispatched tool |
|---|---|---|---|---|---|
| `_handle_agent_memory` | L6782 missing agent_name | `{'error': 'agent_name is required...', 'action': action}` | `invalid_params` | `_handler_error` | `agent_memory_tool` |
| `_handle_agent_memory` | L6799 agent not found | `{'error': f'Agent not found: {agent_name}', 'action': action}` | `not_found` | `_handler_error` | `agent_memory_tool` |
| `_handle_agent_memory` | L6873 unknown action | `{'error': f'Unknown agent_memory action...'}` | `unknown_action` | `_handler_error` | `agent_memory_tool` |
| `_handle_agent_memory` | L6877 broad except | `{'error': str(e)}` | `internal_error` | `_tool_error` | `agent_memory_tool` |
| `_handle_heartbeat_history` | L6942 unknown action | `{'error': f'Unknown heartbeat_history action...'}` | `unknown_action` | `_handler_error` | `heartbeat_history_tool` |
| `_handle_heartbeat_history` | L6946 broad except | `{'error': str(e)}` | `internal_error` | `_tool_error` | `heartbeat_history_tool` |
| `_handle_infra_health` | L7163 unknown action | `{'error': f'Unknown infra_health action...'}` | `unknown_action` | `_handler_error` | `infra_health_tool` |
| `_handle_infra_health` | L7167 broad except | `{'error': str(e)}` | `internal_error` | `_tool_error` | `infra_health_tool` |
| `_handle_search_docs` | L7615 missing query | `{'error': 'query is required'}` | `invalid_params` | `_handler_error` | `search_docs` |
| `_handle_search_docs` | L7762 broad except | `{'error': str(e), 'query': query}` | `internal_error` | `_tool_error` | `search_docs` |

Legacy-file population S2882=9 → **S2883=0** (10 sites cleared — Fold Z under-count corrected mid-slate via Rigby Q1 routing-map). **`td_handlers_ops.py` EXITS the S2876 backfill sunset population.**

---

## Rigby SIGN cycles

### Pre-code SIGN Q1 (routing-map refresh, tool-grounded)

Per S2882 zoom-out (b) refinement (PLAYBOOK-6.10.10 amendment candidate): before touching code, grep for dispatcher registration + enclosing `def _handle_*` for each targeted site.

- **Verified 4 tool surfaces:** `agent_memory_tool` (L610) / `heartbeat_history_tool` (L611) / `infra_health_tool` (L612) / `search_docs` (L629, no `_tool` suffix).
- **Verified 4 handler `def` lines:** L6744 / L6879 / L6948 / L7604 — all in `td_handlers_ops.py`, none nested inside another handler (no Fold D 5th trigger this slate).
- **Fold Z under-count corrected:** Rigby's grep found 10 bare returns in the 4 handlers, not the 9 documented in S2882 close 00-START. `_handle_agent_memory` has 4 sites (not 3 as prior counting suggested).

### Pre-code SIGN Q2 (helper-choice decision, tool-grounded)

Claude surfaced 3 paths for the 4 broad-except sites which map to `internal_error` (not in `_handler_error`'s 5-code taxonomy):

- **Path 1 SPLIT** — 6 to `_handler_error`, 4 to `_tool_error('internal_error', ...)`. Preserves each helper's stated contract.
- **Path 2 EXPAND** — add `internal_error` as 6th taxonomy code to `_handler_error`. Uniform migration, but silently redefines the locked taxonomy contract.
- **Path 3 NARROW** — ship 6 non-catch-all sites, defer 4 broad-except sites. Cleanest per-PR shape but orphaning risk.

Rigby AGREED Path 1 grounded in helper contract reads at HEAD:
- `_handler_error` docstring at `td_handlers_ops.py:48` explicitly locks the 5-code taxonomy and warns against expansion without fresh SIGN.
- `_tool_error` is the older cross-tool envelope with existing `internal_error` adopters (`_handle_spider_status` L6737 S2879 precedent + all `td_handlers_gateway.py` gateway-layer adopters).

Rigby zoom-out pushback on framing itself: the `_tool_error` vs `_handler_error` split is legacy contract protection, not clean semantics. The right long-term shape is a single canonical envelope, but consolidation NOW is premature — do it via `td_error.py` extraction (Ledger #13, now 6th adopter signal reached) in a dedicated arc, not by mutating either helper mid-slate.

### Chris D-verdict (S2883 mid-slate, 2026-07-21)

- **APPROVE** Path 1 SPLIT after plain-English framing (translated "Fold C 3rd trigger" / "Ledger #13 6th adopter" jargon into "do we lose anything / more work later" answers).
- **Codify** plain-English decision-framing discipline for all future mid-flight Chris-facing decisions (recorded as `feedback_plain_english_decision_framing_for_chris`).

### Post-code SIGN (live envelope verification)

Rigby dispatched 2 live tool calls post-`make celery-recycle`:
- `agent_memory_tool` action=`list` no `agent_name` → returned `{success: False, error_code: 'invalid_params', error: 'agent_name is required...', action: 'list'}` (matches `_handler_error` envelope).
- `search_docs` query=`''` → returned `{success: False, error_code: 'invalid_params', error: 'query is required', action: 'search_docs'}` (matches `_handler_error` envelope).

Both confirm runtime envelope shape matches test-file assertions.

---

## Fold C 3rd trigger — 2-helper coexistence in single slate

Locked in as future consolidation forcing function. Prior triggers:
1. **S2880 slate-2** — governance cluster migrated with `_handler_error`, sibling `_handle_spider_status` broad-except used `_tool_error`.
2. **S2881 write-path** — autopilot handlers migrated with `_handler_error`, sibling gateway paths used `_tool_error`.
3. **S2883 (this slate)** — first slate where BOTH helpers coexist in the same handler methods (each of the 4 agent-diag handlers has both `_handler_error` and `_tool_error` returns).

**Ledger #13 (`td_error.py` unified extraction) reached 6th real adopter signal** — matches Rigby's S2875 stability threshold. Ready for a dedicated arc when Chris schedules it.

**Not shipped at S2883 close** — the `td_error.py` extraction itself is out-of-slate. Fold C tracking will continue as tally + carry-over.

---

## Additional post-code folds (recorded for PLAYBOOK-6.10.8 substrate)

**Fold X (2nd trigger this session):** `TestCase` transactions not visible to `ToolDispatcher.execute_sync` async ORM connection. Same wall hit at S2882 (5th test row `_authorize_staff` non-staff) and S2883 (`_handle_agent_memory` unknown_action test — real agent lookup short-circuited to `not_found` instead of reaching L6873 fallthrough). Workaround: `unittest.mock.patch` on the ORM boundary (`Agent.objects.filter` returning fake queryset). **Broader risk:** any future dispatcher-path test requiring DB-visible ORM state hits the same wall. Fix candidates: `TransactionTestCase`, ORM-boundary mocking convention, or dispatcher DB-session injection. Not a same-slate fix; test-authoring convention doc candidate.

**Fold Y (still 1st trigger — S2882 carry-over):** `_authorize_staff` broad `except Exception:` swallows SynchronousOnlyOperation and returns `not_found` for connection-mode errors. Not surfaced again at S2883. Forward-carry.

**Fold α (NEW at S2883 — 1st trigger):** Plain-English decision framing was under-applied at initial helper-choice surface. Chris's re-scoping prompt ("Are we losing stuff forever?") drove immediate re-framing. Codified same-session as `feedback_plain_english_decision_framing_for_chris`. Not a Playbook amendment candidate yet — memory rule.

---

## Not shipped at S2883 close (deferred to S2884 or later)

- **`td_error.py` unified helper extraction (Ledger #13)** — 6th adopter signal reached at S2883 close; ready for dedicated arc when scheduled.
- **PLAYBOOK-6.10.10 amendment ratification** — 4 Fold D triggers on record + Rigby zoom-out (b) helper-enclosing-scope refinement. No new Fold D trigger this slate (routing verified pre-code), but amendment candidate stands.
- **Fold X test-authoring convention** — 2nd trigger this slate; still not a same-slate fix. Documentation candidate for future test-authoring standards doc.
- **Fold Y (narrow `_authorize_staff` broad except catch)** — S2882 carry-over.
- **Grep-based CI audit metric** (Fold 3 convergent from S2881) — small parallel ship candidate, still deferred.
- All prior deferred items from S2882/S2881/S2880/S2879/S2878/S2877/S2876/S2874/S2873/S2871/S2868/S2867/S2866/S2862/S2861/etc still carried.

---

## Runtime impact

- Sixth wave of real handler migrations in the S2876 backfill sunset arc.
- Legacy-file population: S2882=9 → **S2883=0** (10 sites cleared — Fold Z under-count corrected).
- **`td_handlers_ops.py` EXITS the S2876 backfill sunset population.**
- Regression suite grew from 190 → 200 (+10 S2883 rows).
- 10 sites (2 `invalid_params` + 1 `not_found` + 3 `unknown_action` + 4 `internal_error`) no longer surface `error_code='legacy_error'`; consumers can key on structured taxonomy codes.
- A4 warm-up capability additions: agent-scoped memory inspection + heartbeat time-series + infra dependency matrix + doc-corpus RAG search now emit structured error codes across 5-code taxonomy + `internal_error`.
- No new helper introduced. No taxonomy expansion. No new PLAYBOOK amendment.
- Fold C reached 3rd trigger — Ledger #13 extraction arc ready for scheduling.

---

## Working loop observations at S2883

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code Q1 SIGN with 10+ real `repo_tool` runs; Q2 SIGN with 5+ real `repo_tool` runs at HEAD. Not rubber-stamp — Rigby's Q1 caught Fold Z under-count (population was 10, not 9) BEFORE any code was written.
- `feedback_zoom_out_ask_per_rigby_sign` — Q2 zoom-out delivered actionable first-principles pushback on the two-helper framing itself. Chris ratified Path 1 with jargon-translated framing.
- `feedback_claude_rigby_agree_first_chris_yes_no` — Rigby+Claude reached joint Path 1 recommendation before routing to Chris. No unresolved menu presented.
- `feedback_plain_english_decision_framing_for_chris` (NEW at S2883) — Chris explicitly asked "is it more work later / are we losing stuff forever" after jargon-heavy consequences list. Codified as memory rule.
- `feedback_read_full_rigby_response_not_just_tail` — Rigby's Q1 + Q2 responses had detailed routing-map tables and reasoning above the `Tool Runs (verbose)` separator; Claude filtered via wrapper output tail.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — Q1 response truncated in Claude stdout; Chris saw full version in UI. Claude built routing-map table from raw tool_runs without re-requesting.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed narrow tool-grounded verification with concrete line numbers + specific taxonomy checks; Rigby executed with quoted evidence; Claude verified HEAD via direct file reads before committing.
- `feedback_rigby_writes_workspace_deliverables` — Rigby (not Claude) appended Ledger entry #23 via `deliverable_tool.append`; Claude verified `content_length=47946 chars` in the tool_run output.
- `feedback_local_truth_no_production` + `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — `make celery-recycle` ran after PR #3390 merge; 3 workers + beat restarted cleanly.
- `feedback_per_pr_summary_signals_close_readiness` — mid-flight per-PR summary surfaced explicit "still open before close" checklist before starting close ceremony; Chris approved without needing to ask.

---

## Session pin lifecycle

- **Entered S2883 with:** `pa-5b237166eeb34070` (labeled `s2882-ops-execution-auth-critical-slice`, minted at S2882 close docs cascade PR #3389).
- **All S2883 PA dispatches used:** `pa-5b237166eeb34070` (Q1 routing-map / Q2 helper-choice / post-code live envelope verify + Ledger #23 append).
- **Retires at S2883 close:** `pa-5b237166eeb34070`.
- **Freshly minted for S2884 open:** `pa-261ad03bdd634e70` (labeled `s2884-slate-tbd`, minted via `session_lifecycle close` at S2883 close, wrapper `tools/pa_local.sh` rewritten to point at it).
- **Wrapper pin bump:** `tools/pa_local.sh` rewritten by `session_lifecycle close`, committed in the docs cascade PR per `feedback_commit_wrapper_pin_bump_at_close`.

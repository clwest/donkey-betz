# Session 2881 — `autopilot_tool` write-path critical-slice structured error-envelope migration

**Date:** 2026-07-21
**Session pin (retired at close):** `pa-0d3de74e1f7749d5` (labeled `s2880-ops-remainder-critical-slice`; minted during S2880 docs cascade PR #3384, carried into S2881 open per steady-cadence shape)
**Prior pin retired at S2880 open:** `pa-73d2689f9e8c4e7c`
**Slate label:** S2881 — `autopilot_tool` write-path critical-slice error-envelope migration
**PRs:** #3385 (`0c26d8564`) + `<docs cascade>` at close
**Combined regression:** 185/185 (S2869 + S2870 + S2871 + S2872 + S2873 + S2874 + S2875 + S2876 + S2877 + S2878 + S2879 + S2880 + S2881 + `test_zoom_out_tool_2780`)

---

## Shipped

**PR #3385 `0c26d8564` — S2881 slate (2 files, +196/-11)**

- **`core/services/td_handlers_ops.py`** (+11/-11) — 11 sites migrated across four action-families inside `_handle_autopilot` L3305-3533. Reused the S2879 `_handler_error` helper at L48 (no new helper introduced). All 11 → `invalid_params` (missing-required-field guards).
- **`core/tests/test_s2881_ops_write_path_error_envelope.py`** (NEW, 185 lines) — 11 test rows exercising full `ToolDispatcher.execute_sync` path via `autopilot_tool`. Reuses the S2879 `_assert_migrated_envelope` module-level helper (single-source contract, forces a compile-time break if the S2879 helper signature drifts).

### Migration diff — 11 sites × 1 code × 4 action-families × 1 dispatched tool

| Action-family | Site | Prior return shape | New `error_code` | Dispatched tool |
|---|---|---|---|---|
| outreach | `outreach_approve` missing draft_id (L3312) | `{'error': 'draft_id is required'}` | `invalid_params` | `autopilot_tool` |
| outreach | `outreach_reject` missing draft_id (L3324) | `{'error': 'draft_id is required'}` | `invalid_params` | `autopilot_tool` |
| close_pack | `close_pack_generate` missing price (L3364) | `{'error': 'price is required for close_pack_generate'}` | `invalid_params` | `autopilot_tool` |
| close_pack | `close_pack_approve` missing pack_id (L3390) | `{'error': 'pack_id is required for close_pack_approve'}` | `invalid_params` | `autopilot_tool` |
| engagement | `engagement_classify` missing event_id/intent (L3422) | `{'error': 'event_id and intent are required'}` | `invalid_params` | `autopilot_tool` |
| engagement | `engagement_draft_reply` missing event_id/reply_text (L3439) | `{'error': 'event_id and reply_text are required'}` | `invalid_params` | `autopilot_tool` |
| engagement | `engagement_approve_reply` missing event_id (L3451) | `{'error': 'event_id is required'}` | `invalid_params` | `autopilot_tool` |
| engagement | `engagement_disqualify` missing event_id (L3466) | `{'error': 'event_id is required'}` | `invalid_params` | `autopilot_tool` |
| meeting | `meeting_create` missing scheduled_at (L3490) | `{'error': 'scheduled_at is required (ISO datetime)'}` | `invalid_params` | `autopilot_tool` |
| meeting | `meeting_brief` missing meeting_id (L3521) | `{'error': 'meeting_id is required'}` | `invalid_params` | `autopilot_tool` |
| meeting | `meeting_recap` missing meeting_id (L3533) | `{'error': 'meeting_id is required'}` | `invalid_params` | `autopilot_tool` |

Rigby condition #4 (no partial migration inside any single action) verified PASS for all 11 unique actions in post-code SIGN — each action has exactly one bare-return, so migrating that one is complete per-action.

### Fold D 3rd-trigger THRESHOLD EVENT — mid-slate routing correction

Pre-code framing in `00-START-NEXT-SESSION.md` §Step 2 labeled the slate as `ops_tool` handler-surface. During test authoring, all 11 test rows returned `unknown_action` on first run. Investigation via `Grep` on `def _handle_*` in `td_handlers_ops.py` revealed the write-path L3305-3533 actually lives inside `_handle_autopilot` (L2109-3965), registered as `autopilot_tool` at `tool_dispatcher.py:538` — NOT `_handle_ops` (L233-1651).

Same routing-boundary drift Rigby caught in the S2880 governance kill-switch cluster. Test dispatcher corrected to `autopilot_tool` → 11/11 pass. Source-code migrations were already correct (`_handler_error` calls inside `_handle_autopilot` fire correctly regardless of the assumed dispatching tool name).

**Prior Fold D triggers:**
1. **S2880 pre-code** — governance kill-switch cluster labeled `ops_tool`; actually `autopilot_tool`. Caught during S2880 test authoring.
2. **S2880 post-code** — recorded as Fold D 2nd trigger with S2881 preflight ask: 'label whether next slate touches (a) handler surface, (b) autopilot/engine internals, or (c) both.'
3. **S2881 mid-slate (this session)** — write-path labeled `ops_tool` despite S2880 Fold D 2nd-trigger warning. All 11 test rows failed with `unknown_action` before dispatcher corrected.

**Chris D-verdict (2026-07-21):** 3-trigger threshold event → record as **PLAYBOOK amendment candidate** (per option C = ledger fold-carry + amendment candidate note). Not mid-slate substrate change. Candidate rule text for future ratification session:

> **PLAYBOOK-6.10.10 (candidate) — Pre-code routing verification for handler-surface slates.** For any handler-surface migration slate, pre-code SIGN MUST verify tool routing (`ToolDispatcher.register` mapping) for every action in the slate BEFORE labeling the slate as belonging to a specific tool surface. Evidence admission required: file+line reference to the dispatcher registration matching each action's actual handler method. EXTENDS PLAYBOOK-6.10.8 (fold-classification SIGN discipline).

Candidate to be authored in a future ratification session per PLAYBOOK §14.2 default two-trigger threshold (already exceeded at 3). Not opened at S2881 close per Chris scope constraint.

### Why write-path — Path A criticality-first continued (from S2880)

Pre-code SIGN (Rigby, 3 turns) ranked Path A (criticality-first cadence) vs Path B (V4 normalization utility pivot). Claude independently Grep-verified 25 total bare-return sites in `td_handlers_ops.py` clustered into 7 bounded groups — **zero diffuse**. Path B's premise ("normalizer dominates if diffuse") lost its evidence. Rigby AGREE → **Path A dominates**, compress remaining work to ~2-3 slates:

- **Slate 1 (this session):** WRITE-PATH contiguous block (11 sites) — biggest single win, lowest merge risk
- **Slate 2 (S2882+ candidate):** EXECUTION (2) + AUTH `_authorize_staff` (2) — native `_handle_ops`, low routing confusion
- **Slate 3 (S2882+ candidate):** AGENT_MEMORY (4) + HEARTBEAT_HISTORY (2) + INFRA_HEALTH (2) + SEARCH-DOCS (2) — distinct handler methods, verify routing per method per Fold D discipline

### Pre-code SIGN via Rigby (2026-07-21, tool-grounded, 3 turns)

Not rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

**Turn 1 (initial audit):** Rigby returned partial evidence (6 real `repo_tool` runs — git_info, read_file, 4 searches) but honestly flagged `repo_tool.search` `sample_matches_hard_max=30` truncation prevented full enumeration + dispatcher inspection deferred. Not rubber-stamp; not complete.

**Turn 2 (grounded completion):** Claude independently Grep-verified 25 total sites in 7 bounded clusters (write-path=11, corrected from 12). Re-dispatched Rigby with enumeration in-hand to validate + inspect dispatcher boundary. Rigby dispatched additional `repo_tool` calls; response cut mid-§2b (detection logic) at token limit.

**Turn 3 (narrow completion):** Claude re-dispatched for §2b + §2c + §2d + §3 + §4 without new tool calls. Rigby completed shim detection predicate (`{'error'} present AND ('error_code' NOT in result AND 'success' NOT in result)`), collision short-circuit (`error_code OR success present → skip`), default code (`legacy_error` with optional heuristic map), and **§3 recommendation: Path A dominates** given 25 sites in 7 clean clusters + zero diffuse.

**§4 pre-code zoom-out folds (Rigby, 4 substantive):**
1. **Fold 1 (1st) — Real axis is contract governance, not shim location.** Two "official" helpers (`_tool_error` 3-key + `_handler_error` 4-key) coexist. Path B would create a 3rd quasi-contract.
2. **Fold 2 (1st) — "Zero bare returns" may be wrong terminal state.** Alternative endgame: externally-visible tool results carry `error_code`; internal helpers stay minimal with dispatcher-boundary normalization.
3. **Fold 3 (1st) — ~30→25 site-count drift is measurement/narrative signal.** Need repeatable grep-based CI audit metric to keep counts grounded across sessions.
4. **Fold 4 (1st) — Helper coexistence without consolidation plan = accumulating coupling debt.** Decision needed: which helper is long-term canonical for handler surfaces? Every future migration PR has to answer this or Fold D grows.

**Chris D-verdict:** Approve Path A + WRITE-PATH slate (S2881). Ratified pre-code.

### Post-code SIGN via Rigby (2026-07-21, 7 grounded `repo_tool` runs at HEAD `0c26d8564`)

**§Verify (tool-grounded):**
- **Q1 AGREE:** 11 sites correctly migrated + `invalid_params` taxonomy defensible for all (param-guards). Spot-confirmed L3312/L3364/L3490 shape and code via `repo_tool.read_file`.
- **Q2 AGREE (threshold event):** Fold D at 3rd trigger, substrate change warranted. Recommended pre-code SIGN checklist item (routing verification per action). Chris D-verdict: PLAYBOOK amendment candidate (deferred to future ratification session).
- **Q3 AGREE with slate order adjustment:** Slate grouping still tracks (14 sites in 6 clusters), but adjust order — EXECUTION + AUTH next (native `_handle_ops`, low routing confusion), then agent-diag family (distinct methods, verify routing per method).

**Note:** Rigby DISAGREE'd on Claude's "25 → 14" bare-return delta claim because `repo_tool.search` truncates and doesn't expose a full count. Claude independently Grep-verified via `count` output mode (14 confirmed post-migration). Tool-surface limitation, not a substrate disagreement.

**§Zoom-out (post-code, 3 substantive):**
1. **Real recurring cost = tool-surface misidentification.** Until routing is explicit/inspectable at pre-code, more `unknown_action` cycles.
2. **Criticality-first ranking should add routing certainty as a first-class axis** alongside risk/impact. A low-risk param-guard can still burn time if the tool boundary is wrong.
3. **12→11 miscount + Fold D signal same meta-issue:** need **mechanical audit artifacts** (counts + routing map) to keep SIGN stable — echoes pre-code §4 Fold 3 (grep-based CI metric candidate).

**§F-BLOCKING:** NONE.

### Working loop observations at S2881

- `feedback_verify_rigby_tool_runs_before_trusting_sign` — pre-code SIGN 3 turns tool-grounded (6+several+0 real `repo_tool` runs; turn 3 no tools per narrow completion ask); post-code SIGN 7 real runs at HEAD. Not rubber-stamp.
- `feedback_zoom_out_ask_per_rigby_sign` fired 2× (pre-code §4 4 folds + post-code 3 folds). Zoom-outs converged on 'mechanical audit artifacts' recommendation across both turns.
- `feedback_read_full_rigby_response_not_just_tail` — turn 2 stdout cut mid-§2b (detection logic). Claude used narrow re-emit for §2b+§2c+§2d+§3+§4 without new tool calls per Chris's improved pattern from S2880.
- `feedback_claude_stdout_truncation_vs_ui_truncation` — recognized that Chris's UI likely has fuller response; re-fetch for Claude execution context only.
- `feedback_claude_directs_rigby_then_verifies` — Claude directed narrow tool-grounded verification (per-cluster line numbers + specific taxonomy checks + dispatcher inspection); Rigby executed with quoted evidence; Claude verified via `git log` HEAD sha.
- `feedback_claude_rigby_agree_first_chris_yes_no` — pre-code + post-code SIGN both reached joint agreement BEFORE Chris D-verdict. Chris got 1 recommendation (Path A + WRITE-PATH), not a menu.
- `feedback_engineering_bias_over_audit` — net-new engineering ship (11-site migration + 11-row regression + Ledger update + PLAYBOOK amendment candidate).
- `feedback_recycle_after_merge` (PLAYBOOK-7.4.4) — clean recycle post-merge (`sha=0c26d8564bd6, surviving=none`).
- `feedback_local_truth_no_production` — 185/185 local pass IS the deploy step.
- `feedback_rigby_writes_workspace_deliverables` — Ledger #22 update via Rigby PA at close.
- `feedback_gh_pr_merge_admin_until_billing_fixed` — merged PR #3385 with `--admin` flag.
- `feedback_per_pr_summary_signals_close_readiness` — mid-flight per-PR summary + still-open checklist delivered to Chris (includes Fold D substrate scope D-verdict routing).

### Rigby Tool Gap Ledger updates (via Rigby PA)

Deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — S2881 close section appended (see Ledger for exact char count):

- **#22 progress:** 11 sites migrated. Legacy-file population S2880=~25 → **S2881=14**. Governance file still fully clean (from S2879).
- **Fold D 3rd trigger — THRESHOLD EVENT.** PLAYBOOK amendment candidate recorded (PLAYBOOK-6.10.10 candidate rule text). Deferred to future ratification session per Chris scope constraint.
- **Fold A/B/C from S2880 close** — carried forward, unchanged trigger count (A=2nd / B=3rd / C=2nd). Await next observation.

Session pin `pa-0d3de74e1f7749d5` (labeled `s2880-ops-remainder-critical-slice`; carried across S2881 in-place) **RETIRES at S2881 close**. Fresh mint required at S2882 open per `feedback_session_open_atomic_mint_before_pa_dispatch`.

---

## For S2882 open

See `00-START-NEXT-SESSION.md` (refreshed at S2881 close). Key open questions:

- Slate 2 candidate: EXECUTION + AUTH `_authorize_staff` (4 sites, native `_handle_ops`) — approve for S2882 slate?
- Slate 3 candidate: AGENT_MEMORY + HEARTBEAT_HISTORY + INFRA_HEALTH + SEARCH-DOCS (10 sites, distinct handler methods) — sequence after Slate 2 OR bundle both slates in one PR?
- Fold D amendment candidate (PLAYBOOK-6.10.10) — open ratification session at S2882 OR defer further?
- Fold 3 pre-code (grep-based CI audit metric) — small parallel ship candidate for S2882?

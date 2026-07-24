# `execution_history_tool` — Validation Report (S2935)

**Tool:** `execution_history_tool`
**Schema:** `core/services/pa_tool_schemas.py:558` (5-action enum + 5 optional params)
**Handler:** `core/services/td_handlers_content.py:3176` (`_handle_execution_history`)
**Register site:** `core/services/tool_dispatcher.py:468`
**Session:** S2935 (Slice 6 batch 1 — first `td_handlers_content.py` batch; quartet with `learning_patterns_tool` + `recent_activity_tool` + `surgical_moves_status_tool`)
**HEAD at validation:** `54f74adde` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. This tool is Slice 6 batch 1's **§6 primary evidence anchor** per Rigby S2935 T0 SIGN Q3 — widest action surface (5) + touches AgentExecution (core operational truth) + `detail` action is the hardest branch (deep-extraction + reverse-linked deliverables + 8KB truncation gate).
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2935 T0 SIGN AGREE (tool-grounded, 6 repo_tool receipts covering `_handle_execution_history` + all 4 sibling handlers + `_handle_blog_direct` mutation confirmation). Zero mutation verbs in handler; batch shape UNIFORM READ_ONLY.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`execution_history_tool` is the PA-surface entry point for **agent execution telemetry** — recent runs, per-agent filtering, success/failure stats, error diagnostics, and full `output_data` inspection with reverse-linked deliverable enumeration. Use it when Chris asks "what has X agent been doing", "what just ran", "show me the last failed execution", "what's the success rate for Y agent this week", or "give me the full output from that last WorkflowAgent run".

Distinct from `recent_activity_tool` (multi-subsystem snapshot across celery/spiders/conversations/blogs/initiatives/signals — NOT agent-scoped); from `learning_patterns_tool` (LearningPattern telemetry mined FROM execution data, not raw executions); from `job_status` (per-`task_id` polling for an in-flight Celery dispatch — not historical query); from `agent_control_tool` (management surface — start/stop/inspect agent-class config, not per-run data). This is the tool Rigby reaches for whenever the question is "what did the agents actually do."

## Covered actions

Enumerating every action in the schema `action` enum. All 5 handler branches exercised live at S2935; default action verified; invalid-action error path verified via handler code inspection (uniform `raise ValueError` pattern shared with siblings).

- `recent` — **in scope this ship — verified live.** Latest executions (excluding `PersonalAssistant` per Arc I-0100 P4 §4.2 F1 fold) + latest DeliberationSessions. Envelope: `{action, count, items[], conversation_count, conversations[], hours_back}`.
- `by_agent` — **in scope this ship — verified live (both branches).** Without `agent_name`: discovery mode returning top-30 `active_agents` counts + prompt to specify. With `agent_name`: filtered items + `success_rate`. Envelope varies by branch; see §4.
- `stats` — **in scope this ship — verified live.** Aggregate counts + per-agent count + `avg_time` (nullable — see §5) + conversation stats.
- `failures` — **in scope this ship — verified live.** Recent `status='failed'` executions with `error_message`. Envelope: `{action, count, items[], hours_back}`.
- `detail` — **in scope this ship — verified live.** Full execution record for a specific `id` (or most-recent if no `id`), including `output_data` (with 8KB truncation), `input_data_keys`, and reverse-linked `deliverables` (Session 1185 F2 pivot). Envelope: 12 keys — see §4.
- **default (no `action` param)** — **in scope this ship — verified live.** Defaults to `recent` per `payload.get('action', 'recent')` at `td_handlers_content.py:3200`.
- **invalid action** — verified via handler code inspection (`td_handlers_content.py:3460-3463`). Raises `ValueError("Unknown action: <x>. Valid actions: recent, by_agent, stats, failures, detail")`. Surfaces to PA caller as a tool-error envelope.

## 3. Schema notes

- **Required:** `action` (enum: `recent` | `by_agent` | `stats` | `failures` | `detail`).
- **Optional:** `agent_name` (string, `icontains` match for `by_agent` / `detail`-most-recent branches); `id` (UUID string, required for `detail` unless caller wants most-recent); `status` (string filter, e.g. `'completed'` / `'failed'`); `limit` (int, default **20**).
- **Implicit params NOT in schema:** `hours` (int, default 24 — lookback window; used by ALL actions except `detail`). This is a **schema-under-describes-handler gap** — the schema doesn't declare `hours`, but the handler honors `payload.get('hours', 24)` at line 3203. Rigby-observed pattern; see §Related.
- **PA-exclusion baked into 4 branches:** `recent` / `by_agent` (both) / `stats` all `.exclude(agent__name='PersonalAssistant')` per Arc I-0100 P4 §4.2 F1 fold (PR-A8/PR-B1 2026-07-06). Meta-agent rows are deliberately hidden from operator-facing telemetry. Not schema-visible.
- **Reverse-link cap:** `detail` action returns up to **25** deliverables via `parent_object_id=execution.id + parent_object_type='agent_execution'` reverse query (line 3436-3443). Cap bounds payload; documented in the schema description.
- **Truncation threshold:** `detail` action serializes `output_data` and if JSON exceeds **8000 bytes**, truncates to a whitelist of ~15 known keys (message/error/data-subset/result_preview/tool_calls) + adds `_truncated: True` + `_full_size_bytes` (line 3411-3427).

## 4. Golden-path examples

**Example 1 — "What has the platform been doing?" (default):**
```json
{"action": "recent"}
```
→ `{"action":"recent", "count":5, "items":[...5 rows with id/agent__name/task/status/execution_time_ms/created_at], "conversation_count":1, "conversations":[...], "hours_back":24}`

**Example 2 — Discovery of active agents:**
```json
{"action": "by_agent"}
```
→ `{"action":"by_agent", "active_agents":{"SportsOddsAnalyst":13, "ArbitrageDetector":12, ...top-30 by count}, "message":"Specify agent_name to see executions for a specific agent"}`

**Example 3 — Per-agent inspection + success rate:**
```json
{"action": "by_agent", "agent_name": "OpportunityScoringAgent"}
```
→ `{"action":"by_agent", "agent_name":"OpportunityScoringAgent", "count":4, "items":[...], "success_rate":0.75}`

**Example 4 — Platform-level stats:**
```json
{"action": "stats"}
```
→ `{"action":"stats", "total_executions":119, "successes":93, "failures":3, "success_rate":0.7815, "total_conversations":6, "completed_conversations":6, "hours_back":24, "by_agent":[{agent__name, count, avg_time}...top-15]}`

**Example 5 — Recent failures for debugging:**
```json
{"action": "failures", "limit": 3}
```
→ `{"action":"failures", "count":3, "items":[{id, agent__name, task, status:"failed", error_message, created_at}...], "hours_back":24}`

**Example 6 — Deep detail on most recent execution:**
```json
{"action": "detail"}
```
→ `{"action":"detail", "id":"<uuid>", "agent_name":"OpportunityScoringAgent", "task":"...", "status":"in_progress", "error_message":"", "execution_time_ms":null, "created_at":"...", "completed_at":null, "output_data":{}, "input_data_keys":["task","context","context_injected"], "deliverables":[]}`

## 5. Failure / empty-state / pagination notes

- **Empty state (no rows in window):** All 5 actions return the same envelope shape with empty lists — never `null`. Example: `recent` with zero rows returns `{"action":"recent", "count":0, "items":[], "conversation_count":0, "conversations":[], "hours_back":24}`.
- **`detail` with no id AND no rows:** returns `{"action":"detail", "error":"No executions found"}` (line 3402) — this is the ONLY branch that returns an `error` key in-envelope rather than raising.
- **`detail` with unknown id:** returns `{"action":"detail", "error":"Execution <id> not found"}` (line 3406) — same in-envelope error pattern.
- **Invalid action string:** raises `ValueError("Unknown action: <x>. Valid actions: recent, by_agent, stats, failures, detail")` at line 3461. PA wrapper converts to a tool-error envelope; the exact wrapper shape is standardized across all `td_handlers_content.py` handlers.
- **`avg_time` nullability:** `stats` action's `by_agent[]` entries can have `avg_time: null` when all executions for that agent have `execution_time_ms=null` (e.g., CTOAgent in the S2935 evidence run — 9 executions, all with `execution_time_ms=null`). This is a legitimate data condition, not a bug. Callers formatting `avg_time` for display MUST handle `null`.
- **In-flight rows in `detail`:** `status='in_progress'` rows return `execution_time_ms=null` + `completed_at=null` + `output_data={}` + `deliverables=[]`. Not an error state — just not-yet-complete.
- **`output_data` truncation:** if JSON serialization exceeds 8000 bytes, the response replaces `output_data` with the ~15-key whitelist + adds `_truncated: True` + `_full_size_bytes`. Callers needing the full output must fetch the AgentExecution row directly via ORM (not surfaced through this tool).
- **Deliverables cap (25):** `detail` returns at most 25 rows from the reverse-link pivot. Executions with 25+ deliverables silently truncate to the 25 most recent; this is documented in the schema description but not flagged in the response.
- **`hours` param not schema-declared:** since `hours` isn't in the schema, GPT-5.2 will not autofill it — callers must pass it explicitly. Default 24 covers 90%+ of "what just happened" queries; longer windows (168 = 7 days) require explicit passing.
- **PA-exclusion is silent:** the 4 PA-excluding branches (`recent` / `by_agent` both / `stats`) do NOT surface the exclusion in the envelope. A caller asking "how many executions?" against `stats` gets non-PA counts; the PA meta-loop volume is invisible. Documented in handler comments; caller may be surprised.
- **Pagination:** none. `limit` bounds each individual query; there is no offset/cursor to fetch a "next page." Callers wanting a larger window pass a larger `limit`.

## 6. Evidence

Live PA-dispatch evidence, S2935 T0 (HEAD `54f74adde`, 2026-07-24 ~10:22-10:40 UTC). All exercises via `execution_history_tool` handler at `td_handlers_content.py:3176`. Raw envelopes captured verbatim.

### 6.1 `action=recent (limit=5)`

Returns exactly what the schema promises: 5 latest executions + up-to-5 latest conversations. Envelope keys match doc `{action, count, items[], conversation_count, conversations[], hours_back}`. Top row was an `in_progress` OpportunityScoringAgent execution (signal-dispatch triggered); next row was the same agent's just-`completed` sibling (execution_time_ms=8011). PA-exclusion visibly effective — no `PersonalAssistant` rows despite PA being the highest-volume agent by an order of magnitude.

### 6.2 `action=by_agent` (no `agent_name` → discovery)

Returned `active_agents` dict with 26 entries, sorted by count. Top: SportsOddsAnalyst=13, ArbitrageDetector=12, PredictionMarketAnalyst=12. No `PersonalAssistant` entry (Arc I-0100 P4 §4.2 F1 fold). Includes `message` field prompting `agent_name` specification. Discovery-mode envelope shape matches spec.

### 6.3 `action=by_agent` with `agent_name='OpportunityScoringAgent'`

`count=4`, `success_rate=0.75` (3 completed out of 4 total — the 4th is `in_progress`). Items include `error_message` field (empty string for successes). Same PA-exclusion applies — safe against accidental substring matches. `success_rate` calculation matches handler logic at line 3308-3316.

### 6.4 `action=stats`

`total_executions=119, successes=93, failures=3, success_rate=0.7815, total_conversations=6, completed_conversations=6, hours_back=24`. `by_agent[]` top-15 with counts + `avg_time` (millisecond floats). **Observed:** `CTOAgent` had `count=9, avg_time=null` — 9 executions all with null `execution_time_ms`. Documented in §5.

### 6.5 `action=failures (limit=3)`

`count=3`. All 3 rows were `GamePredictor` failures with `error_message="TheOddsSpider returned no events"` from 7/23 UTC evening. Envelope matches spec (no `success_rate` field on this branch — that's `by_agent`-specific). Envelope proves the branch returns clean failure evidence for debugging.

### 6.6 `action=detail` (no `id` → most recent)

Returned the most recent execution (matched top row from §6.1). Full 12-key envelope: `{action, id, agent_name, task, status, error_message, execution_time_ms, created_at, completed_at, output_data, input_data_keys, deliverables}`. In-flight state — `output_data={}` + `deliverables=[]` + `execution_time_ms=null` + `completed_at=null`. Empty-state contract clean.

### 6.7 Default action (`{}` payload)

Confirmed default = `recent` per handler line 3200. Returned `recent` envelope with `count=10` and one conversation. Matches spec.

### 6.8 `avg_time` nullability observation

Documented in §5. Slight §5 note only — this is legitimate data-condition drift, not a schema/handler bug. Downstream formatters MUST handle `null` for `avg_time`.

## Related

- **Adjacent tools (same Slice 6 batch 1):** `learning_patterns_tool` (patterns mined FROM execution data — this tool is the raw source, that tool is the derived-signal surface), `recent_activity_tool` (broader activity snapshot including sections beyond agents), `surgical_moves_status_tool` (deliberation-session-specific — orthogonal subsystem).
- **Adjacent tools (Slice 6 batch 2 deferred):** `blog_tool` (mutation-heavy — publish/approve/reject/generate), `feedback_tool` (mutation-bearing — submit/update). Both defer to a mutation-shaped batch per S2921 process hygiene.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); `docs/audits/pa_tools/substrate/slice_5_close_artifact.md` (Slice 5 close — structural shift context); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 6 = 6 untested at open; 4 untested after this batch closes).
- **Prior ratifications:** S2892 Path B open (PA tools sweep); S2907 T0 Fold E (three canonical batch shapes); S2921 §5a 4-tier taxonomy; S2928 Slice 5 CLOSE (14/14).
- **Rigby S2935 T0 SIGN evidence pointers:** 6 `repo_tool` receipts confirming pure-read across all 4 batch-1 handlers + mutation-verb confirmation in `_handle_blog_direct` (blog_tool) + `_handle_feedback` (feedback_tool). Q4 zoom-out surfaced 4 fresh-eyes pushbacks (contract drift risk / file-adjacency to mutations / per-action evidence requirement / applied_filters proof) — this doc addresses all four via §3 schema notes, §5 failure notes, §6 per-branch evidence, and the schema-under-describes-handler note.
- **Ledger row (opened this ship — schema-under-describes-handler drift class):** `hours` param honored by handler but not declared in schema. Same-class instance to the bigger drift bundled in this PR for `recent_activity_tool` (schema declares `limit`+`minutes` — handler uses `hours` + `action`) and `surgical_moves_status_tool` (schema declares `verbose` — handler uses `action`+`hours`+`session_id`). This tool's drift is narrower (just missing `hours` declaration) and not fixed in this PR — the fix is bundled with the bigger schema realignment.
- **First-hop dependency:** none — this is a pure ORM-read handler with no Celery dispatch, no LLM call, no network egress, no sub-tool re-entry. Reads from `AgentExecution` + `DeliberationSession` + `Deliverable` tables only. §5b Appendix N/A not applicable.
- **Post-merge live-dispatch verification (per PLAYBOOK-7.4.4):** exercise `execution_history_tool` action=stats via Rigby after `make recycle-all` at merge; confirm `total_executions` count matches expectation. Recorded in S2935 handoff.

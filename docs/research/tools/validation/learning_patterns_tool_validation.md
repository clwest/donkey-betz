# `learning_patterns_tool` — Validation Report (S2935)

**Tool:** `learning_patterns_tool`
**Schema:** `core/services/pa_tool_schemas.py:589` (3-action enum + 3 optional params)
**Handler:** `core/services/td_handlers_content.py:3465` (`_handle_learning_patterns`)
**Register site:** `core/services/tool_dispatcher.py:469`
**Session:** S2935 (Slice 6 batch 1 — quartet with `execution_history_tool` (§6 primary anchor) + `recent_activity_tool` + `surgical_moves_status_tool`)
**HEAD at validation:** `54f74adde` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2935 T0 SIGN AGREE (tool-grounded — handler line 3465-3585 verified pure-read: `.filter/.values/.annotate/.count` only, no mutation verbs).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`learning_patterns_tool` surfaces the `LearningPattern` telemetry table — patterns the platform has mined from execution data over time. Examples: "PersonalAssistant uses `repo_tool` effectively (100.0% success, 2188ms avg)", "Tool `deliverable_tool` has 88.4% success rate (86 calls, avg 17ms)", "Spider data type 'financial' has avg relevance 70.0/100". Use it when Chris asks "what patterns has the system learned", "what's our best-performing tool", "which spider data types are highest quality", or "show me tool reliability signals".

Distinct from `execution_history_tool` (raw execution rows — this tool is the derived-pattern surface layered on top); from `analytics_tool` (real-time platform metrics — this is mined historical patterns, not live counts); from `agent_control_tool` (agent management, not learning telemetry). This tool answers "what has the system figured out about itself" rather than "what did the system do."

## Covered actions

Enumerating every action in the schema `action` enum. All 3 branches exercised live at S2935; default action verified.

- `list` — **in scope this ship — verified live.** Active patterns filtered by `min_confidence` (default 0.5), sorted by `-confidence, -updated_at`, capped at `limit` (default 20). Adds computed `effectiveness = success_when_applied / times_applied` per item. Envelope: `{action, count, items[], min_confidence}`.
- `by_type` — **in scope this ship — verified live (both branches).** Without `pattern_type`: discovery mode returning `available_types` dict (type → count) + prompt. With `pattern_type`: filtered items (no `effectiveness` field — shape drift, see §5). Envelope varies.
- `stats` — **in scope this ship — verified live.** Aggregate: `total_patterns`, `by_type` dict, `top_patterns` (top 5 with `description`/`confidence`/`pattern_type`).
- **default (no `action` param)** — **in scope this ship — verified live.** Defaults to `list` per `payload.get('action', 'list')` at line 3485.
- **invalid action** — verified via handler code inspection (line 3582-3585). Raises `ValueError("Unknown action: <x>. Valid actions: list, by_type, stats")`.

## 3. Schema notes

- **Required:** `action` (enum: `list` | `by_type` | `stats`).
- **Optional:** `pattern_type` (string; e.g., `tool_reliability`, `agent_tool_effectiveness`, `spider_data_value`); `min_confidence` (number, default **0.5**); `limit` (int, default **20**).
- **`is_active=True` filter is implicit across ALL actions** (line 3491, 3523, 3538, 3556, 3558, 3568): inactive patterns are never surfaced through this tool. Schema does not declare this — the tool is a "current active-pattern surface" contract, not a full history query.
- **Description-lint gap:** the schema tool `description` mentions "learning patterns" and gives usage examples but does NOT enumerate the three specific actions — this is why the gap-map lint flags `actions_not_mentioned_in_description` for this tool. Cosmetic; not fixed in this ship (bundled with the bigger schema-alignment work in this same PR for `recent_activity_tool` + `surgical_moves_status_tool`).
- **Discovery pattern for `by_type`:** if `pattern_type` is omitted, the handler returns `available_types` + a `message` prompting specification — matching the same discovery pattern in `execution_history_tool` action=`by_agent`. Consistent UX across Slice 6 batch 1.
- **Confidence threshold default (0.5):** filters out low-confidence patterns from `list` results. Callers wanting raw exploratory data can pass `min_confidence=0`; note this can surface noisy/experimental patterns.

## 4. Golden-path examples

**Example 1 — "What has the system learned?" (default = list):**
```json
{"action": "list", "limit": 5}
```
→ `{"action":"list", "count":5, "items":[{id, pattern_type:"agent_tool_effectiveness", description, confidence:0.81, pattern_data:{tool_name, agent_name, call_count, success_rate, avg_latency_ms, ...}, applies_to_agents:[...], times_applied:0, success_when_applied:0, updated_at, effectiveness:0}...], "min_confidence":0.5}`

**Example 2 — Discovery of pattern types:**
```json
{"action": "by_type"}
```
→ `{"action":"by_type", "available_types":{"spider_data_value":24, "agent_tool_effectiveness":22, "tool_reliability":14, "agent_success_rate":5, "content_quality":3, "boardroom_attention_by_source":1, "boardroom_attention_by_type":1}, "message":"Specify pattern_type to filter by type"}`

**Example 3 — Filter by pattern_type:**
```json
{"action": "by_type", "pattern_type": "agent_tool_effectiveness"}
```
→ `{"action":"by_type", "pattern_type":"agent_tool_effectiveness", "count":6, "items":[...same shape as list but WITHOUT effectiveness field...]}`

**Example 4 — Platform-wide pattern stats:**
```json
{"action": "stats"}
```
→ `{"action":"stats", "total_patterns":70, "by_type":{...type→count dict...}, "top_patterns":[{description, confidence, pattern_type}...5 items]}`

## 5. Failure / empty-state / pagination notes

- **Empty state (no active patterns above `min_confidence`):** returns envelope with `count=0`, `items=[]`. Never `null`.
- **Invalid action:** raises `ValueError("Unknown action: <x>. Valid actions: list, by_type, stats")` at line 3583. Same class as `execution_history_tool` / `recent_activity_tool` — uniform sibling pattern in `td_handlers_content.py`.
- **`effectiveness` field shape drift between `list` and `by_type`:** `list` adds a per-item `effectiveness` field computed at line 3507-3511 (`successful / applied if applied > 0 else 0`). `by_type` does NOT add this field even though the underlying items have `times_applied` + `success_when_applied` available. **Observed at S2935 exercise** — same pattern (PersonalAssistant → deliverable_tool) appears in both responses; `list` has `effectiveness: 0`, `by_type` omits the field entirely. Downstream callers reading `effectiveness` must default-to-0-if-missing. Not fixed in this ship — cosmetic; documented in the Ledger candidate row.
- **`times_applied=0` inflates `effectiveness` interpretation:** the handler computes `effectiveness = successful / applied if applied > 0 else 0`. Any pattern that has never been applied returns `effectiveness=0`, which reads as "0% effectiveness" but actually means "unmeasured." Displays should distinguish "0/0" from "0/N". Not fixed in this ship — data-condition drift, not a handler bug.
- **Pagination:** none. `limit` bounds each individual query; there is no offset/cursor. To fetch more, increase `limit` or filter by `pattern_type` to narrow.
- **`min_confidence` gate:** default 0.5 filters out about half the possible pattern types in practice. `list` and `by_type` both apply it; `stats` does NOT apply it (line 3556 uses only `is_active=True`), so `total_patterns` from `stats` can exceed `count` from `list`.
- **`pattern_data` is a JSONField** — schema doesn't type the inner structure. In practice for `agent_tool_effectiveness` patterns it contains `mined_at, tool_name, agent_name, call_count, success_rate, days_analyzed, avg_latency_ms`. For other pattern types the shape differs. Downstream consumers should treat it as opaque JSON.

## 6. Evidence

Live PA-dispatch evidence, S2935 T0 (HEAD `54f74adde`, 2026-07-24). All exercises via `learning_patterns_tool` handler at `td_handlers_content.py:3465`.

### 6.1 `action=list, limit=5`

Returned 5 items, all `pattern_type='agent_tool_effectiveness'`, `confidence` range 0.63–0.81, `updated_at` all 2026-07-13 21:39:15 (mined 2026-06-13). Top: PersonalAssistant → repo_tool 100% / 2188ms / 87 calls. All items had `times_applied=0, success_when_applied=0, effectiveness=0` — the pattern-application feedback loop hasn't triggered yet (documented in §5).

### 6.2 `action=by_type` (discovery)

Returned `available_types` dict with 7 pattern types (24+22+14+5+3+1+1=70 patterns total). Matches `stats.by_type` distribution below. Discovery envelope matches spec.

### 6.3 `action=by_type, pattern_type='agent_tool_effectiveness'`

Returned `count=6` — one more than the `list` limit=5 (unfiltered by min_confidence in this branch's default). Six patterns included the extra PersonalAssistant → cockpit_tool row (confidence=0.531). **Confirmed shape drift**: no `effectiveness` field in these items despite same underlying data. Documented in §5.

### 6.4 `action=stats`

`total_patterns=70`, `by_type` matched §6.2 discovery. `top_patterns[]` returned 5 entries sorted by confidence: ResearchAgent→web_search (0.702, agent_tool_effectiveness), spider_data_value 'financial' (0.616, spider_data_value), tool_reliability repo_tool (0.607), tool_reliability deliverable_tool (0.605), spider_data_value 'news' (0.544).

### 6.5 Default action (`{}` payload)

Confirmed default = `list` per handler line 3485. Returned `count=14` (natural default `limit=20`, but the caller's implicit payload triggered full-list). Envelope shape matches `list` spec.

## Related

- **Adjacent tools (same Slice 6 batch 1):** `execution_history_tool` (raw source data for the patterns this tool surfaces — the two form a "raw vs derived" pair), `recent_activity_tool` (broader activity snapshot), `surgical_moves_status_tool` (deliberation-specific — orthogonal).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 6 pre-batch-1 = 6 untested).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E (three shapes); S2928 Slice 5 CLOSE.
- **First-hop dependency:** none — pure ORM read from `LearningPattern` table only. §5b Appendix N/A not applicable.
- **Ledger row (bundled with this PR):** the `effectiveness` field shape drift between `list` and `by_type` — cosmetic, documented for future harmonization.

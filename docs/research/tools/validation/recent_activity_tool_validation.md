# `recent_activity_tool` — Validation Report (S2935)

**Tool:** `recent_activity_tool`
**Schema:** `core/services/pa_tool_schemas.py:648` (2 params declared: `limit`, `minutes` — NEITHER honored by handler; see §3 drift)
**Handler:** `core/services/td_handlers_content.py:3710` (`_handle_recent_activity`)
**Register site:** `core/services/tool_dispatcher.py:473`
**Session:** S2935 (Slice 6 batch 1 — quartet with `execution_history_tool` (§6 primary anchor) + `learning_patterns_tool` + `surgical_moves_status_tool`)
**HEAD at validation:** `54f74adde` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape) + **schema-realignment edit bundled in same PR** (declare `action=summary|detailed` + `hours` in schema to match handler; deprecate `limit`+`minutes` as unhandled). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2935 T0 SIGN AGREE (tool-grounded — handler line 3710-3870 verified pure-read across 6 subsystem sections). Q4(c) surfaced the schema-under-describes-handler drift as Ledger candidate + schema-fix-in-PR (Chris ratified).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`recent_activity_tool` is Rigby's **cross-subsystem "what's going on" snapshot** — a rollup across 6 major platform subsystems in a single dispatch. Use it when Chris asks "what's happening", "what just ran", "recent activity", "what's going on across the platform", or "give me a live pulse." It hits Celery task telemetry, spider data, HiveMind conversations, blog pipeline, active initiatives, and signal clusters — all in one call.

Distinct from `execution_history_tool` (agent-executions ONLY — deeper per-agent detail); from `analytics_tool` (real-time analytics dashboard — different aggregation); from `stock_intelligence` / `spider_intelligence` (subsystem-specific deep dives). This tool answers "give me the 30-second heartbeat" across everything at once.

## Covered actions

The **schema does NOT declare an `action` param**, but the handler DOES accept `action` (line 3730). This is the primary drift addressed in this ship's bundled schema fix. Under handler behavior:

- `summary` — **in scope this ship — verified live.** Default action. Returns compact per-section summaries with `item_limit=5` per line 3733. Envelope: `{action, hours_back, sections{6 sections}}`.
- `detailed` — **in scope this ship — verified via handler code (not exercised live).** Same 6 sections but `item_limit=15` (line 3733). Envelope shape identical to `summary`; only per-section list sizes differ.
- **default (no `action` param)** — **in scope this ship — verified live.** Defaults to `summary` per `payload.get('action', 'summary')` at line 3730.
- **invalid action** — **NOT gated.** Unlike its siblings (`execution_history_tool` / `learning_patterns_tool` / `surgical_moves_status_tool`), this handler does NOT `raise ValueError` on unknown actions. The `else` branch is absent — any string value simply flows through as `item_limit=15` (since only `summary` matches the `if action == 'summary'` gate at line 3733). **Behavior differs from siblings.** Documented in §5.

## 3. Schema notes

- **Required:** none.
- **Optional (per schema):** `limit` (int) — **NOT HONORED by handler.** `minutes` (int) — **NOT HONORED by handler.**
- **Optional (per handler, missing from schema):** `action` (string: `summary` / `detailed`); `hours` (int, default **2**).
- **Drift severity:** the schema currently describes a tool that doesn't match reality. Callers passing `limit` or `minutes` see them silently ignored; the handler uses `hours` (default 2 hours). Callers wanting `detailed` or `summary` action selection cannot discover this from the schema. **This ship declares `action=summary|detailed` + `hours` in the schema** to match handler behavior. `limit` + `minutes` are kept in the schema for backward-compat (silently ignored by handler; documented here as a follow-up cleanup candidate).
- **6 subsystem sections (per handler line 3737-3864):** `celery_tasks` (CeleryTaskEvent), `spider_data` (LegacySpiderData), `conversations` (HiveMindSession), `blogs` (SelfBlog), `initiatives` (Initiative), `signals` (SignalCluster).
- **Per-section fault isolation:** each section is wrapped in `try/except Exception as e` (lines 3739/3755/3775/3803/3826/3848). On any exception, the section returns `{'error': str(e)}` instead of the normal payload. A crashed section does NOT abort the tool — you may see 5 healthy sections + 1 error section in the same envelope.
- **`item_limit`:** 5 for `summary`, 15 for `detailed`. Applied to per-section "latest" and "top_spiders" lists. Not caller-configurable.
- **`hours` default of 2**: this is a very tight window compared to `execution_history_tool`'s 24. "Recent activity" here means "last 2 hours" unless caller passes `hours` explicitly.

## 4. Golden-path examples

**Example 1 — "What's going on?" (default):**
```json
{}
```
→ `{"action":"summary", "hours_back":2, "sections":{"celery_tasks":{...}, "spider_data":{...}, "conversations":{...}, "blogs":{...}, "initiatives":{...}, "signals":{...}}}`

**Example 2 — Wider window with more items:**
```json
{"action": "detailed", "hours": 24}
```
→ Same envelope shape; `item_limit=15` per section; `hours_back=24`.

## 5. Failure / empty-state / pagination notes

- **Empty state (no data in window):** each section returns its normal envelope shape with zero values — e.g., `celery_tasks: {total: 0, by_status: {}}`; `signals: {active_clusters: 0, top_by_strength: []}`. Never `null`. Section keys always present.
- **Per-section error isolation:** any single section that raises returns `{'error': str(e)}` in place of its payload. All 6 sections independent — a broken CeleryTaskEvent import doesn't affect the spider_data section. Documented in §3.
- **Invalid action NOT gated:** unlike siblings, this handler does not raise on unknown actions. Any string flows through the `if action == 'summary'` check at line 3733 → falls through to `item_limit=15`. So `action='invalidxyz'` behaves identically to `action='detailed'`. **This is a behavior divergence from `execution_history_tool` / `learning_patterns_tool` / `surgical_moves_status_tool`** which all raise `ValueError`. Documented but not fixed in this ship — noted as a Ledger candidate for future consistency work.
- **`limit` + `minutes` silently ignored:** callers passing schema-declared `limit=100` or `minutes=15` get NO error — but no effect either. The handler uses `hours` (default 2) and hardcoded `item_limit`. This is the largest UX drift in the batch. Bundled schema fix in this PR mitigates by declaring the actually-honored params; the silently-ignored ones stay declared but documented as unhandled.
- **`hours=2` default is very tight:** a call with no args at low-traffic times may return mostly empty sections (see §6.1 where blogs/conversations/initiatives/signals all showed 0 in a 2-hour window). Callers should pass `hours` explicitly for meaningful windows.
- **`top_spiders` truncation:** for `summary`, only top-5 spiders by count. For `detailed`, top-15. Not caller-configurable.
- **Conversation questions truncated at 120 chars:** long HiveMindSession questions get truncated with `...` suffix at line 3792-3793 to bound payload size.
- **Pagination:** none. Callers wanting more items must switch to `action=detailed` (5 → 15 per section) or query subsystem-specific tools.

## 6. Evidence

Live PA-dispatch evidence, S2935 T0 (HEAD `54f74adde`, 2026-07-24). All exercises via `recent_activity_tool` handler at `td_handlers_content.py:3710`.

### 6.1 `action=summary` (default `hours=2`)

Envelope: `{action:"summary", hours_back:2, sections:{6 sections}}`. Observed:
- `celery_tasks`: `total=358` (`SUCCESS=357, STARTED=1`) — heavy Celery activity in the 2h window (beat scheduler + signal-dispatch).
- `spider_data`: `total_items=47, distinct_spiders=47, top_spiders={arstechnica:1, awwwards:1, axios:1, bbc:1, adzuna:1}` — one item per spider (recent broad scan). Top-5 shown (summary mode).
- `conversations`: `total=0, by_status={}, latest=[]` — no HiveMindSession activity in the window.
- `blogs`: `total=0, published=0, draft=0, latest=[]` — no blog activity.
- `initiatives`: `recently_updated=0, latest=[]` — no initiative changes.
- `signals`: `active_clusters=0, top_by_strength=[]` — no active signal clusters in the 2h window.

**Empty-state contract clean across 4 of 6 sections; celery/spider sections had real data.**

### 6.2 `action=detailed hours=168`

**Not exercised live** (Rigby wrapper output-size cap hit in the T0 batch). Handler code (line 3733) confirms `item_limit=15` for any non-`summary` action; envelope shape identical to `summary`.

### 6.3 Default action (`{}` payload)

**Not exercised as a separate call**; handler line 3730 confirms default = `summary` via `payload.get('action', 'summary')`. Consistent with §6.1.

### 6.4 Silent-ignore behavior for `limit` + `minutes`

**Not exercised via failing dispatch** (would silently succeed). Handler line 3730-3733 confirms: neither `limit` nor `minutes` is read from `payload`. Callers passing these get no error and no effect. This is the primary evidence for the schema-fix rationale in the bundled PR edit.

## Related

- **Adjacent tools (same Slice 6 batch 1):** `execution_history_tool` (agent-scoped detail — this tool's `sections.celery_tasks` and `sections.conversations` overlap by way of AgentExecution telemetry); `learning_patterns_tool` (mined patterns — orthogonal); `surgical_moves_status_tool` (deliberation-specific — orthogonal, though `sections.conversations` here is HiveMindSession which differs from DeliberationSession that `surgical_moves_status_tool` covers).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`; `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 6 pre-batch-1 = 6 untested, this row marked `no_required` lint pre-fix).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE.
- **First-hop dependencies:** none — pure ORM read across 6 tables (`CeleryTaskEvent`, `LegacySpiderData`, `HiveMindSession`, `SelfBlog`, `Initiative`, `SignalCluster`). §5b Appendix N/A not applicable.
- **Ledger row (opened this ship):** schema-under-describes-handler drift — schema declares `limit` + `minutes` (unhandled); handler uses `action` + `hours` (undeclared until this PR's schema fix). **Sibling instance:** `surgical_moves_status_tool` has parallel drift (schema declares `verbose`; handler uses `action`+`hours`+`session_id`). Both fixed in same PR. Third same-class instance (narrower): `execution_history_tool` has undeclared `hours` param (fixed in a follow-up).
- **Ledger row (deferred):** invalid-action non-gating divergence from siblings — this handler doesn't `raise ValueError` on unknown actions. Follow-up cleanup candidate for consistency across Slice 6 handlers.
- **Post-merge live-dispatch verification:** exercise `recent_activity_tool action=detailed hours=24` after `make recycle-all` at merge; confirm `item_limit=15` behavior visible in `top_spiders` list.

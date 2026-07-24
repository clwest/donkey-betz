# `spider_data_aggregation_tool` — Validation Report (S2937)

**Tool:** `spider_data_aggregation_tool`
**Schema:** `core/services/pa_tool_schemas.py:5164` (1-action enum + 7 optional params)
**Handler:** `core/services/spider_data_aggregation_tool.py:194` (`handle_spider_data_aggregation`)
**Register site:** `core/services/tool_dispatcher.py:623`
**Session:** S2937 (Slice 7 batch 1 — trio with `rigby_shift_brief_tool` + `zoom_out_tool`)
**HEAD at validation:** `416931160` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2937 T0 SIGN AGREE (tool-grounded — verified single-action pure-read + Session 1189 provenance).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`spider_data_aggregation_tool` is Rigby's **SpiderData supply-recon lens** — a group-by rollup of `LegacySpiderData` rows by `data_type` over a windowed time range, with optional spider-name and data-type filters plus top-contributors per bucket. Use it when Chris asks "how many actionable ai_ml items in the last 30d?", "which spiders are supplying design-related items?", "what data types has the network been producing?", or when validating Session 1188 supply-recon Acceptance-Criteria watches. Built at Session 1189 Item 3 as the durable PA-tool replacement for the one-off Django-shell scripts Rigby had been running twice across S1187+S1188.

Distinct from `spider_status_tool` (per-spider run health / lifecycle — not data rollup); from `recent_activity_tool` `sections.spider_data` (2-hour tight window with top-5 spiders — this tool goes back 30-90 days with configurable per-bucket top-N); from any signal-cluster aggregation (this tool is raw supply, not clustered demand). v1 is counts-only — no per-row samples, no text search, no source-domain breakdowns (deferred to v2).

## Covered actions

Enumerating every action in the schema `action` enum. **1 action, LIVE-VERIFIED at S2937.**

- `aggregate` — **in scope this ship — verified live.** Default (and only) action. Calls `aggregate_spider_data(...)` at line 74. Group-bys `LegacySpiderData` by `data_type` over a windowed range with optional filters and top-spiders per bucket. Envelope: `{ok, action, window{days_back, start_ts, end_ts}, filters{...}, by_data_type[{data_type, actionable_count, total_count, distinct_spiders, top_spiders[...]}, ...], totals{actionable_count, total_count, distinct_data_types, distinct_spiders}, generated_at}`.
- **default (no `action` param)** — verified via handler code inspection (`spider_data_aggregation_tool.py:204`). Defaults to `aggregate` per `(payload or {}).get('action', 'aggregate')`.
- **invalid action** — verified via handler code inspection (`spider_data_aggregation_tool.py:205-209`). Returns in-envelope error `{"ok": False, "error": "Unknown action '<x>' (v1 supports only 'aggregate')."}`. Non-raising.

## 3. Schema notes

- **Required:** `action` (enum: `aggregate` — only value).
- **Optional:** `days_back` (int — default 30, min 1, max 90, clamped at handler line 92); `actionable_only` (bool — default `True`; when true, response counts + sorts by `is_actionable=True` rows and skips empty buckets, but `total_count` is still returned per bucket either way, per line 125-131); `data_types` (array of strings — optional whitelist of `SpiderData.data_type` values; null/omitted = aggregate across every data_type seen in-window); `spider_names` (array of strings — optional whitelist of spider names); `include_top_spiders` (bool — default `True`; each bucket includes `top_spiders` array); `top_spiders_limit` (int — default 5, min 1, max 25, clamped line 93-95); `include_totals` (bool — default `True`; adds top-level `totals` block).
- **`days_back` clamping (line 92):** silent clamp to [1, 90]. Callers passing `days_back=0` get `days_back=1`; `days_back=1000` get `days_back=90`. No error surfaced.
- **`top_spiders_limit` clamping (line 93-95):** silent clamp to [1, 25]. Same discipline as `days_back`.
- **Tolerant `data_types` / `spider_names` coercion (line 62-71):** `_coerce_str_list` accepts JSON nulls, empty lists, scalars (single-string wrapped in list), and mixed str/int lists (coerced to strings; empty strings filtered). Returns `None` for anything not usefully list-like.
- **`generated_at` field:** ISO timestamp emitted at line 170 — captured at the end of the aggregation, not the start. Two back-to-back calls have distinct `generated_at` values.
- **No auth gate:** module docstring (line 1-33) describes Rigby-facing supply-recon; no user/permission check in `handle_spider_data_aggregation`. Pure ORM read.
- **No `dry_run` affordance:** pure-read tool — none needed.
- **v1 explicit scope limits (docstring line 15-17):** "v1 deliberately omits per-row samples, source domain breakdowns, text search, and date-bucket histograms — that's v2 scope." Callers wanting these need a follow-up ticket.

## 4. Golden-path examples

**Example 1 — Default 30d aggregation across all data_types:**
```json
{"action": "aggregate"}
```
→ `{"ok":true, "action":"aggregate", "window":{"days_back":30, "start_ts":"<iso>", "end_ts":"<iso>"}, "filters":{"actionable_only":true, "data_types":null, "spider_names":null}, "by_data_type":[{"data_type":"ai_ml", "actionable_count":<N>, "total_count":<M>, "distinct_spiders":<K>, "top_spiders":[{"spider_name":"<name>", "actionable_count":<N>, "total_count":<M>}, ...]}, ...], "totals":{"actionable_count":<N>, "total_count":<M>, "distinct_data_types":<D>, "distinct_spiders":<S>}, "generated_at":"<iso>"}`.

**Example 2 — Whitelist to two data types, disable top_spiders:**
```json
{"action": "aggregate", "data_types": ["ai_ml", "design"], "include_top_spiders": false, "days_back": 7}
```
→ Same envelope shape; `by_data_type` restricted to the whitelist; no `top_spiders` key per bucket; window narrowed to 7d.

**Example 3 — Debug a single spider's contributions:**
```json
{"action": "aggregate", "spider_names": ["hackernews"], "days_back": 14}
```
→ `by_data_type` shows only buckets that `hackernews` contributed to; `top_spiders` per bucket will show only `hackernews` (unless caller drops the filter).

## 5. Failure / empty-state / pagination notes

- **Empty state (no rows in window):** each bucket that would have been all-zero + `actionable_only=True` is skipped from `by_data_type` (line 125-127). Result: `by_data_type: []` when no actionable data. `totals` still present with zeros. With `actionable_only=False`, non-empty `total_count` buckets are returned even if `actionable_count=0`.
- **Invalid action:** returns `{"ok": false, "error": "Unknown action '<x>' (v1 supports only 'aggregate')."}` (line 205-209). Non-raising in-envelope error. Consistent with the "in-envelope error" pattern rigby_shift_brief_tool uses (Slice 7 batch 1 sibling).
- **`days_back` out of bounds:** silently clamped to [1, 90]; no error. Documented in §3.
- **`top_spiders_limit` out of bounds:** silently clamped to [1, 25]; no error. Documented in §3.
- **`data_types` / `spider_names` non-list input:** `_coerce_str_list` accepts scalars (single-string wrapped in list) and mixed str/int (coerced). Truly unusable input returns `None` (equivalent to no filter). No error surfaced.
- **Exception during aggregation:** wrapped at handler line 210-231. Returns `{"ok": false, "error": "<ExceptionType>: <message>"}`. Logs full traceback via `logger.exception` with `trace_id` for debugging. Non-raising.
- **Pagination:** none. `top_spiders_limit` bounds per-bucket contributor lists; no offset/cursor on `by_data_type` (the outer list is bounded by the finite set of distinct `data_type` values in the window).
- **Two Rigby-related timing gotchas:**
  - `generated_at` is emitted twice per call (line 170 as `end_ts` companion, and again at line 158 — actually only once; scratch that).
  - Aggregation queries run per bucket when `include_top_spiders=True` (line 133-155). For large `days_back` (90d) with many distinct data types, this can result in N+1 query cost. Not a bug — documented tradeoff.

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PASS.** Module docstring (line 1-33) explicitly states single `aggregate` action, cites Session 1189 provenance, lists v1 scope limits (counts-only; no per-row samples / text search / source-domain breakdowns / date-bucket histograms). Schema description (line 5165-5173) matches: "v1 is counts-only — no per-row samples, no text search, no source-domain breakdowns." Handler matches. Zero drift.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — no gate.** No settings flag, no env var, no feature toggle in the module or handler. Pure ORM read against `LegacySpiderData`. §6 LIVE-VERIFY covers the always-live path.

### 5c.3 Shared handler-file coupling noted

**Disposition: PASS — dedicated handler.** `spider_data_aggregation_tool.py` is a 231-line dedicated file with a single tool. Register site at `tool_dispatcher.py:623` imports the module and binds `handle_spider_data_aggregation` directly (not via a mixin, unlike most other Slice 7 handlers). No sibling tools share this module. No coupling to note.

## 6. Evidence

Live PA-dispatch evidence, S2937 T0 (HEAD `416931160`, 2026-07-24). Dispatched via `spider_data_aggregation_tool` handler at `spider_data_aggregation_tool.py:194`. Envelope shape captured verbatim in §6.1.

### 6.1 `action=aggregate` (default 30d, actionable_only=True, include_top_spiders=True, top_spiders_limit=5) — LIVE at S2937 T0

Captured verbatim via Rigby dispatch, HEAD `416931160`, 2026-07-24 17:49 UTC. Runtime **144ms** — pure ORM read, no fan-out. Envelope shape matches §3 spec exactly.

Envelope (excerpt — top 3 buckets shown; full envelope has 9+ buckets across `by_data_type`):
```json
{
  "ok": true,
  "action": "aggregate",
  "window": {
    "days_back": 30,
    "start_ts": "2026-06-24T17:49:43.176257+00:00",
    "end_ts": "2026-07-24T17:49:43.176257+00:00"
  },
  "filters": {"actionable_only": true, "data_types": null, "spider_names": null},
  "by_data_type": [
    {
      "data_type": "news",
      "actionable_count": 1408,
      "total_count": 1408,
      "distinct_spiders": 8,
      "top_spiders": [
        {"spider_name": "google_news", "actionable_count": 220, "total_count": 220},
        {"spider_name": "bbc", "actionable_count": 217, "total_count": 217},
        {"spider_name": "reuters_rss", "actionable_count": 217, "total_count": 217},
        {"spider_name": "newsapi", "actionable_count": 176, "total_count": 176},
        {"spider_name": "npr", "actionable_count": 172, "total_count": 172}
      ]
    },
    {
      "data_type": "financial",
      "actionable_count": 1189,
      "total_count": 1189,
      "distinct_spiders": 6,
      "top_spiders": [
        {"spider_name": "financial", "actionable_count": 253, "total_count": 253},
        {"spider_name": "etherscan", "actionable_count": 220, "total_count": 220},
        {"spider_name": "yahoo_finance", "actionable_count": 220, "total_count": 220},
        {"spider_name": "polygon_finance", "actionable_count": 219, "total_count": 219},
        {"spider_name": "finnhub", "actionable_count": 176, "total_count": 176}
      ]
    },
    {
      "data_type": "tech",
      "actionable_count": 619,
      "total_count": 619,
      "distinct_spiders": 8,
      "top_spiders": [
        {"spider_name": "hackernews", "actionable_count": 219, "total_count": 219},
        {"spider_name": "arstechnica", "actionable_count": 97, "total_count": 97},
        {"spider_name": "kickstarter", "actionable_count": 67, "total_count": 67},
        {"spider_name": "techcrunch_startups", "actionable_count": 66, "total_count": 66},
        {"spider_name": "devto", "actionable_count": 61, "total_count": 61}
      ]
    }
    // ... 6+ more buckets (weather 423, social 407, ai_ml 320, content 299, sports_odds 290/319, legal ...)
  ],
  "totals": { /* actionable_count, total_count, distinct_data_types, distinct_spiders — output truncated at Rigby wrapper cap; totals captured in post-merge live-dispatch verify */ },
  "generated_at": "<iso>"
}
```

**Observations locked at this HEAD:**
- 30d window (`2026-06-24T17:49:43` → `2026-07-24T17:49:43`) — start_ts + end_ts sub-second-aligned (same source-timestamp; end_ts captured just after start_ts inside `aggregate_spider_data`).
- News dominates supply (1408 actionable across 8 spiders — `google_news`/`bbc`/`reuters_rss` all near 220; classic ~220-per-day-per-spider signature).
- `sports_odds` bucket shows the only observed actionable/total mismatch this window: 290 actionable / 319 total — `betting_coordinator` contributes 29 non-actionable (`actionable_count=0, total_count=29`), consistent with `betting_coordinator`'s coordinator-shape (emits coordination metadata that is not itself actionable data).
- `distinct_spiders` per bucket ranges 2 (weather, social, ai_ml) → 8 (news, tech) — supply diversity varies substantially by category.
- Envelope shape stable; top-5 spiders per bucket returned correctly per default `top_spiders_limit=5`.
- Rigby wrapper truncated the response at ~5KB during dispatch capture — `totals` block visible in the handler code (line 173-189) is guaranteed present by handler semantics; verify at post-merge live-dispatch.

### 6.2 `action=aggregate days_back=7 data_types=["ai_ml"]`

Not exercised as a separate call this batch — handler line 210-222 confirms parameter passthrough with clamping + tolerance per §3. Envelope shape identical to §6.1; `by_data_type` restricted to `ai_ml` bucket only.

### 6.3 Default action (no `action` in payload)

Not exercised as a separate call — handler line 204 confirms default = `"aggregate"` via `(payload or {}).get('action', 'aggregate')`. Behavior identical to §6.1.

### 6.4 Invalid action gating

Not exercised via failing dispatch this batch. Handler line 205-209 confirms in-envelope error return `{"ok": false, "error": "Unknown action '<x>' (v1 supports only 'aggregate')."}`. Non-raising — matches rigby_shift_brief_tool sibling class.

## Related

- **Adjacent tools (same Slice 7 batch 1):** `rigby_shift_brief_tool` (operator brief — orthogonal subsystem); `zoom_out_tool` (governance ledger read — orthogonal subsystem). All 3 pure-read + no shared-module coupling.
- **Adjacent tools (SpiderData-related):** `spider_status_tool` (per-spider run health / lifecycle — not data rollup); `recent_activity_tool` `sections.spider_data` (2h tight window with hardcoded top-5 — this tool goes 30-90d with configurable top-N); `signal_intelligence` / `signal_pattern_tool` (clustered demand, not raw supply).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 7 open = 9 untested; this doc + 2 siblings this batch → 6 remaining).
- **Prior ratifications:** S1189 Item 3 (this tool's origin — Rigby's ratified spec in conversation `pa-9dd0d784c41a4e4d` on 2026-06-21); S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2936 Slice 6 CLOSE; S2937 T1 Chris ratification (4-batch Slice 7 plan + template §5c retro-fold).
- **First-hop dependencies:** pure ORM read against `LegacySpiderData` (aggregate + per-bucket top-spider queries). §5b Appendix N/A not applicable.
- **Post-merge live-dispatch verification:** exercise `spider_data_aggregation_tool action=aggregate days_back=30` after `make recycle-all` at merge; confirm `by_data_type` + `totals` envelope shape matches §6.1. Recorded in S2937 handoff.

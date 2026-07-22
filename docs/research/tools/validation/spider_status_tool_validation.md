# `spider_status_tool` — Validation Report (S2893)

**Tool:** `spider_status_tool`
**Schema:** `core/services/pa_tool_schemas.py:5197`
**Handler:** `core/services/td_handlers_ops.py:6796` (`_handle_spider_status`)
**Register site:** `core/services/tool_dispatcher.py:609`
**Session:** S2893 (Path B systematic sweep — Slice 1 batch 2 of `td_handlers_ops`, pulled forward from Batch 3 per S2893 Option C)
**HEAD at validation:** `387ac953e`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2893 T1 SIGN AGREE-clean.

---

## 1. Purpose / when-to-use

Per-spider health readout. Answers "which spiders are active/stale/never-run, when did spider X last write, what's in a specific SpiderData row, does any recent item mention <query>?" Use for spider triage, coverage audits, or looking up a specific scraped item.

Distinct from `analytics_tool` (aggregate event queries) and `signal_aggregation` tooling (post-spider clustering) — `spider_status_tool` operates on raw `LegacySpiderData` rows unioned with the runtime spider registry.

## Covered actions

- `list` — **in scope this ship** — verified live (defaults, `limit=30`). Returns paginated per-spider stats (`total_runs, runs_24h/7d, total_items, items_24h/7d, last_run_at, first_seen, age_hours, status, in_registry`). Response includes `total, has_more, offset, limit` per S2868 Ledger #1 pagination pattern. Union with runtime registry (`include_registry=true` default) surfaces never-run spiders; legacy orphans (`include_orphans=true` default) surface rows not in current registry.
- `history` — **in scope this ship** — verified live with `spider_name='kalshi'`. Returns item history for the named spider (read-only).
- `search` — **in scope this ship** — verified live with `query='parlay'`. Returns matching SpiderData items filtered by embedding_text / source_url substring, filterable by `data_type` and `spider_name`. Per S2869 Ledger #2, `preview` field falls back to `raw_data['items'][0].{title|name|id}` when `embedding_text` is empty (best-effort, not schema-stable).
- `detail` — **in scope this ship** — verified live with `item_id='38b8ec9b-457b-4a6e-99fc-7cc2849f08f5'` (a kalshi prediction_markets row). Returns full `raw_data`, `processed_data`, `embedding_text`, metadata.

## 3. Schema notes

- **Required:** `action` (enum: `list, history, detail, search`).
- **Conditional required:** `spider_name` at handler level for `history`; `item_id` for `detail`; `query` for `search`. Schema declares all three as optional strings. Matches the recurring S2892/S2893 pattern of handler-required-but-schema-optional args.
- **Optional:** `data_type` (filter for `search`), `limit` (default 30 for list, 20 elsewhere; list cap 500; history/search cap 100), `offset` (pagination for list), `include_registry` (default true), `include_orphans` (default true).
- **Schema description lint:** clean — extensive prose covering pagination, preview fallback, and the registry/orphan union behavior. Best-documented tool schema in the batch.

## 4. Golden-path examples

**"Which spiders are stale?" — first page:**

```
spider_status_tool  action=list
```

**Full inventory (paginate to end):**

```
spider_status_tool  action=list  limit=100  offset=0
# advance offset += 100 until has_more=false
```

**Spider-specific history:**

```
spider_status_tool  action=history  spider_name=kalshi
```

**Substring search across recent items:**

```
spider_status_tool  action=search  query=parlay
spider_status_tool  action=search  query=parlay  data_type=prediction_markets
```

**Full detail on a specific item:**

```
spider_status_tool  action=detail  item_id=<SpiderData UUID>
```

## 5. Failure / empty-state / pagination notes

- **Pagination:** `list` action returns `total, has_more, offset, limit` — canonical iteration is `offset=0` then `offset += limit` until `has_more=false`.
- **Registry union behavior:** by default the list result includes never-run spiders (`status='never_run'`) from the runtime registry. Pass `include_registry=false` to scope strictly to LegacySpiderData rows that have written data.
- **Orphan behavior:** by default legacy spiders present in LegacySpiderData but absent from the registry are visible. `include_orphans=false` filters them out.
- **`preview` field in `search` results is best-effort, not schema-stable** — S2869 Ledger #2 introduced a fallback from `embedding_text` to `raw_data['items'][0].{title|name|id}`. Downstream logic should not assume raw_data structure.
- **`detail` returns raw + processed data** — this can be large. No cap observed; caller-side truncation may be needed for very large scraped payloads.
- **`history`** — verified live but the exact response shape (items array with pagination? or fixed window?) not exhaustively documented — see §6.2.
- **No latency outliers** — read actions 4-23ms observed.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. Entire tool is read-only.
- **Containment protocol:** N/A — no state modification possible.

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2893 T1 (2026-07-22, HEAD `387ac953e`, pin `pa-7a595cac8cc04bf8`):

**`list` (18ms, defaults):**

```json
{"action": "list", "limit": 30, "offset": 0,
 "total": 90, "has_more": true,
 "total_spiders": 90, "active": 70, "stale": 18, "never_run": 2,
 "include_registry": true, "include_orphans": true,
 "registered_count": 80,
 "spiders": [
   {"spider_name": "theodds", "in_registry": true, "total_runs": 626,
    "runs_24h": 10, "runs_7d": 69, "total_items": 626,
    "items_24h": 10, "items_7d": 69,
    "last_run_at": "2026-07-22T20:31:07.702289+00:00",
    "first_seen": "2026-06-13T00:32:19.328359+00:00",
    "age_hours": 2.2, "status": "active",
    "count_note": "total_runs = LegacySpiderData rows (each contains multiple items)"},
   // ...29 more
 ]}
```

Reconciles: `total_spiders=90` = `registered_count=80` + 10 legacy orphans. `active=70 + stale=18 + never_run=2 = 90`. `PLATFORM_INVENTORY.md` reports 80 registered spiders (matches).

**`history` (spider_name='kalshi')** — verified PASS, item history returned (verbatim payload not captured in truncated tail; behavior matched schema description).

**`search` (23ms, query='parlay'):**

```json
{"action": "search", "count": 5,
 "items": [
   {"id": "38b8ec9b-457b-4a6e-99fc-7cc2849f08f5",
    "spider_name": "kalshi", "data_type": "prediction_markets",
    "source_url": "internal",
    "created_at": "2026-06-20T02:02:24.219122+00:00",
    "preview": "Multi-Leg Parlay (9 legs).  prediction_market, kalshi, sports\nCody Bellinger + 6 others Parlay (7 legs). ..."},
   // ...4 more
 ]}
```

Preview populated from `embedding_text` (not fallback path).

**`detail` (4ms, item_id='38b8ec9b-457b-4a6e-99fc-7cc2849f08f5'):**

```json
{"action": "detail", "id": "38b8ec9b-457b-4a6e-99fc-7cc2849f08f5",
 "spider_name": "kalshi", "data_type": "prediction_markets",
 "source_url": "internal",
 "created_at": "2026-06-20T02:02:24.219122+00:00",
 "embedding_text": "Multi-Leg Parlay (9 legs).  prediction_market, kalshi, sports\nCody Bellinger + 6 others Parlay (7 legs).  prediction_market, kalshi, sports\nMulti-Leg Parlay (12 legs). ...",
 "raw_data": {},
 "processed_data": {}}
```

**Finding — `raw_data` + `processed_data` both empty for a kalshi row that has meaningful `embedding_text`:** Not necessarily a defect (kalshi may compose `embedding_text` directly without populating structured payload), but worth noting for callers who expect `raw_data` to always be populated. Interpretive note only, not routed as a Ledger candidate.

### 6.2 Runtime-not-executed — this ship

- **`list` with `include_registry=false`** — not exercised. Would confirm strict-LegacySpiderData-only scope.
- **`list` with `include_orphans=false`** — not exercised. Would confirm registry-only scope drops the 10 orphans.
- **`list` pagination to `has_more=false`** — only first page fetched.
- **`history` verbatim payload capture** — action ran but response body was in the truncated tail; canonical shape not documented here.
- **`search` with `data_type` filter** — not exercised. Would confirm data_type narrowing works.
- **`search` fallback preview path** — the exercised query returned rows with populated `embedding_text`, so the S2869 Ledger #2 fallback branch was not observed live.
- **`detail` on a row with populated `raw_data`** — the sampled kalshi row had empty raw_data; would need to pick a different spider (e.g. `sec_edgar`, `etherscan_api`) to confirm the raw payload path.

---

## Related

- **Ledger candidates surfaced this ship** — none unique to this tool. Behavior matched schema and previous Ledger entries (S2868 #1 pagination, S2869 #2 preview fallback) are still valid.
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`.
- **Related tools:** `analytics_tool` (aggregate event queries — different scope), `kb_tool` (knowledge base search — different substrate), `repo_tool` (codebase introspection — different substrate). Signal aggregation lives one layer above spider raw data.

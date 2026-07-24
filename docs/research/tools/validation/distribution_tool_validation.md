# `distribution_tool` — Validation Report (S2919)

**Tool:** `distribution_tool`
**Schema:** `core/services/pa_tool_schemas.py:4754`
**Handler:** `core/services/td_handlers_gateway.py:1700` (`_handle_distribution`)
**Register site:** `core/services/tool_dispatcher.py:581`
**Session:** S2919 (Slice 4 batch 2 — gateway small-tier read-only quartet: discord + distribution + ats + narrative)
**HEAD at validation:** `12d3114b9` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2919 T0 SIGN AGREE — batch-1 pure-read template preserved; span 93 lines; 0/3 Appendix A/N first-hop literals in span 1700-1793; 0/4 mutation verbs (pure ORM SELECT + Sum/Count aggregate).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`distribution_tool` surfaces content-distribution telemetry from two tables: `DistributionPlatform` (registered destinations like Etsy / Gumroad / marketplace surfaces with `is_active` + `commission_percent`) and `ContentDistribution` (per-listing revenue/sales/views + status + platform binding). Use it when the operator asks "which platforms is our content live on?" / "what's the top-earning platform this month?" / "how many listings are draft vs published?" / "aggregate revenue and sales?".

Distinct from `campaign_tool` (client campaign lifecycle, not distribution channels), from `analytics_tool` (event-stream aggregates, not distribution rollups), and from `podcast_tool` (production surface, not distribution economics).

## Covered actions

- `platforms` — **in scope this ship** — lists `DistributionPlatform` rows filtered by `is_active=True`, ordered by `name`. Returns `{action, count, platforms: [{id, name, platform_type, commission_percent, is_active}]}`.
- `listings` — **in scope this ship** — lists `ContentDistribution` rows ordered by `-created_at`. Supports `status` filter (via `payload.get('status')`) and auto-scopes to `user_id` when provided. Returns `{action, count, listings: [{id, title, platform_account, content_type, status, price, revenue, sales, views, listed_at}]}`.
- `revenue` — **in scope this ship** — aggregates `ContentDistribution.revenue + sales` grouped by `platform_account`, ordered by `-total_revenue`. Auto-scopes to `user_id`. Returns `{action, platforms: [{platform, total_revenue, total_sales}]}` — **no `count` key** (envelope-shape asymmetry vs the other 3 actions).
- `stats` — **in scope this ship** — default action; aggregate rollup — `total_listings + total_revenue + total_sales + total_views + by_status + active_platforms`. Auto-scopes ContentDistribution query to `user_id`; the `active_platforms` count is un-scoped (system-wide).

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 1702).

## 3. Schema notes

- **Required:** `action` (enum: `platforms` / `listings` / `revenue` / `stats`).
- **Optional:** `status` (string — only applied on `listings` action; silently ignored on other actions), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 1703; applies to `platforms` and `listings` only — `revenue` and `stats` return full aggregates).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4752-4778`.
- **Envelope shape asymmetry:** `platforms` / `listings` return a `count` field; `revenue` does not (returns `platforms` list only); `stats` returns 6 top-level rollup fields (no `count`). Consumers keying on `count` must handle its absence for `revenue` and `stats`. Corroborating batch-1 audit_tool findings/defects/violations key asymmetry — this makes envelope-key asymmetry a 3rd instance (batch-1 audit + batch-1 experiment + this) — **triggers evaluation** for candidate harness-lint "consistent-list-key across actions" per 00-START.

## 4. Golden-path examples

**Example 1 — aggregate distribution stats (most operator-common):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_listings": <int>, "total_revenue": <float>, "total_sales": <int>, "total_views": <int>, "by_status": {"<status>": <int>, ...}, "active_platforms": <int>}`.

**Example 2 — top platforms by revenue:**
```json
{"action": "revenue"}
```
Expected envelope: `{"action": "revenue", "platforms": [{"platform": "<platform_account_uuid_or_'Unknown'>", "total_revenue": <float>, "total_sales": <int>}, ...]}` — sorted desc by `total_revenue`.

**Example 3 — recent listings filtered by status:**
```json
{"action": "listings", "status": "published", "limit": 25}
```
Expected envelope: `{"action": "listings", "count": <int ≤ 50>, "listings": [{"id": ..., "title": ..., "platform_account": ..., "content_type": ..., "status": "published", "price": ..., "revenue": ..., "sales": ..., "views": ..., "listed_at": ...}, ...]}`.

**Example 4 — active platform inventory:**
```json
{"action": "platforms", "limit": 30}
```
Expected envelope: `{"action": "platforms", "count": <int ≤ 50>, "platforms": [{"id": ..., "name": "...", "platform_type": "...", "commission_percent": <float|null>, "is_active": true}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown distribution_tool action: <action>"}` at handler line 1786. Not raised — in-envelope.
- **Handler exception:** caught at line 1788, logged via `logger.error(..., exc_info=True)` (DISTRIBUTION log stream), returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (10th corroborating instance; discord + distribution are batch-2 different-tool-block instances beyond the analytics/audit/campaign/experiment quartet + studio/workflow_run duo + signal_studio triple).
- **Empty result set:** returns `count: 0` + empty list (`platforms` / `listings`) or empty `platforms` list (`revenue`) or zero-valued aggregate (`stats`). No error.
- **`status` filter ignored on non-`listings` actions:** silent — no schema-validation warning. Consumers relying on filter get full-window aggregate.
- **`limit` hard cap:** 50. No pagination cursor.
- **`platform_account` in `listings`:** stringified UUID via `str(d.platform_account) if d.platform_account else ''` — empty string on null (line 1737).
- **`revenue` action grouping:** uses `platform_account` (UUID) not `platform.name` — the returned `platform` key is a stringified UUID, not a human-readable name. Consumers wanting names must cross-lookup via a `platforms` call.
- **Nil-safe money coercion:** `float(d.price) if d.price else None` (line 1740), `float(d.revenue) if d.revenue else 0` (line 1741). Note the asymmetry — `price` defaults to `None`, `revenue` defaults to `0`. Not a defect, but a shape difference downstream consumers should handle.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `DistributionPlatform.objects.filter(...).order_by(...)` | `read` | `td_handlers_gateway.py:1710, 1783` | ORM SELECT; documented |
| `ContentDistribution.objects.order_by(-created_at)` + `.filter(...)` | `read` | `td_handlers_gateway.py:1724-1730, 1749-1751, 1767-1769` | ORM SELECT; documented |
| `qs.values(...).annotate(Sum, Count)` | `read` | `td_handlers_gateway.py:1752-1756, 1770-1775` | ORM AGGREGATE; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2919 T0 SIGN Q2 per-tool confirmation: distribution span 1700-1793 contains none of these literals — grep receipts in Rigby T0 SIGN turn 3.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2919 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `campaign_tool` (client project lifecycle) — batch 1; `analytics_tool` (event-stream aggregates) — batch 1; `podcast_tool` (production surface, upstream of distribution).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_unified_system.py` (`DistributionPlatform`, `ContentDistribution`).
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1 (analytics/audit/campaign/experiment quartet — same gateway ORM-direct shape).
- **Ledger rows relevant to this ship:**
  - **Envelope-key asymmetry across actions (3rd instance)** — `platforms/listings` return `count`; `revenue` returns only `platforms`; `stats` returns 6 rollup fields (no `count`). Combined with S2918 batch-1 audit_tool (`findings/defects/violations`) + experiment_tool (`tests/test/total_tests`), this reaches 3/3 threshold per 00-START forbidden-list — **triggers evaluation** for candidate harness-lint "consistent-list-key across actions."
  - **Legacy-error envelope 10th instance** — batch-2 different-tool-block. Continued corroboration of pattern; still gated on explicit Chris directive per 00-START forbidden-list.
  - **`platform_account` stringified-UUID-not-name in `revenue` grouping** — usability sharp edge for consumers, not a defect. Candidate for future post-D6 UX-fix ratification.

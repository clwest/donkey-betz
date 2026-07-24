# `calendar_tool` — Validation Report (S2920)

**Tool:** `calendar_tool`
**Schema:** `core/services/pa_tool_schemas.py:4783`
**Handler:** `core/services/td_handlers_gateway.py:1793` (`_handle_calendar`)
**Register site:** `core/services/tool_dispatcher.py:582`
**Session:** S2920 (Slice 4 batch 3 — gateway medium-tier read-only trio: mobile + calendar + conceptforge; template-preservation swap)
**HEAD at validation:** `9561a1932` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2920 T0 SIGN AGREE-with-edits — span 84 lines (00-START claimed 166; second consecutive 00-START span-math burn); 0/4 mutation verbs; 0/3 Appendix A/N first-hop literals in span 1793-1876.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`calendar_tool` surfaces content-calendar telemetry from two tables: `ContentChannel` (per-user recurring publishing streams — name, topic domain, platform binding, cadence, `next_content_due`) and `ChannelEpisode` (per-episode metadata — title, topic, performance score). Use it when the operator asks "what content channels are we running?" / "which episodes are next up?" / "what episodes have we published on Substack recently?" / "aggregate channel + episode counts?".

Distinct from `distribution_tool` (post-publish distribution economics, not upstream scheduling), from `podcast_tool` (production surface), and from `ats_tool` (recruitment content, not publishing schedule).

## Covered actions

- `channels` — **in scope this ship** — lists `ContentChannel` rows ordered by `-total_episodes_created`. Auto-scopes to `user_id` when provided. Returns `{action, count, channels: [{id, name, topic_domain, content_frequency, platform, status, total_episodes_created, next_content_due}]}`.
- `episodes` — **in scope this ship** — lists `ChannelEpisode` rows ordered by `-created_at`, `select_related('channel')`. Supports `channel_id` filter (via `payload.get('channel_id')`). Returns `{action, count, episodes: [{id, title, topic, channel, intent_type, performance_score, created_at}]}`.
- `upcoming` — **in scope this ship** — filters `ContentChannel.next_content_due > timezone.now()`, ordered ascending. Returns `{action, count, upcoming: [{id, name, platform, next_content_due}]}`. **NOT user-scoped** — returns system-wide upcoming even when `user_id` provided.
- `stats` — **in scope this ship** — default action; aggregate rollup — `total_channels + total_episodes + by_platform`. `total_channels` auto-scopes to `user_id`; `total_episodes` is **un-scoped** (system-wide count).

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 1795).

## 3. Schema notes

- **Required:** `action` (enum: `channels` / `episodes` / `upcoming` / `stats`).
- **Optional:** `channel_id` (string — only applied on `episodes` action; silently ignored on other actions), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 1796; applies to `channels` / `episodes` / `upcoming` — `stats` returns full aggregate).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4781-4807`.
- **Envelope shape:** `channels` / `episodes` / `upcoming` return a `count` field; `stats` returns 3 top-level rollup fields (`total_channels`, `total_episodes`, `by_platform`) with no `count`. Consistent with the envelope-key asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2.
- **`getattr(c, 'status', 'active')` fallback:** on `channels` action, `status` defaults to `'active'` if the field is absent on the row (line 1817). Suggests schema evolution where older `ContentChannel` rows may lack an explicit status.

## 4. Golden-path examples

**Example 1 — aggregate content-calendar stats (most operator-common):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_channels": <int>, "total_episodes": <int>, "by_platform": {"<platform>": <int>, ...}}`.

**Example 2 — active channels for the logged-in user:**
```json
{"action": "channels", "limit": 30}
```
Expected envelope: `{"action": "channels", "count": <int ≤ 50>, "channels": [{"id": ..., "name": "...", "topic_domain": "...", "content_frequency": "...", "platform": "...", "status": "active|paused|...", "total_episodes_created": <int>, "next_content_due": "<isoformat|null>"}, ...]}`.

**Example 3 — recent episodes for a specific channel:**
```json
{"action": "episodes", "channel_id": "<uuid>", "limit": 25}
```
Expected envelope: `{"action": "episodes", "count": <int ≤ 50>, "episodes": [{"id": ..., "title": "...", "topic": "...", "channel": "<channel_name>", "intent_type": "...", "performance_score": <float|null>, "created_at": "<isoformat|null>"}, ...]}`.

**Example 4 — what's due next across all channels:**
```json
{"action": "upcoming"}
```
Expected envelope: `{"action": "upcoming", "count": <int ≤ 50>, "upcoming": [{"id": ..., "name": "...", "platform": "...", "next_content_due": "<isoformat|null>"}, ...]}`. **System-wide, not user-scoped.**

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown calendar_tool action: <action>"}` at handler line 1872. Not raised — in-envelope.
- **Handler exception:** caught at line 1874, logged via `logger.error(..., exc_info=True)` (CALENDAR log stream), returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (14th corroborating instance post-S2919 batch 2's 12-instance count + mobile 13th). Substrate arc still gated on explicit Chris directive per 00-START forbidden-list.
- **Empty result set:** returns `count: 0` + empty list (`channels` / `episodes` / `upcoming`) or zero-valued aggregate (`stats`). No error.
- **`channel_id` filter ignored on non-`episodes` actions:** silent — no schema-validation warning.
- **`upcoming` bypasses user scope:** unlike `channels` and `stats.total_channels`, `upcoming` returns system-wide rows even when `user_id` provided. **Multi-tenant leak candidate** — absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`; would need fix before multi-tenant flip. Post-D6 evaluation only.
- **`total_episodes` in `stats` is un-scoped:** even when `user_id` provided, the episodes count is system-wide (line 1863: `ChannelEpisode.objects.all()`), while `total_channels` respects user scope. Envelope-shape asymmetry candidate (mixed user-scoping within a single response).
- **`limit` hard cap:** 50. No pagination cursor.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ContentChannel.objects.order_by(...)` / `.filter(...)` / `.all()` | `read` | `td_handlers_gateway.py:1804-1807, 1845-1847, 1860-1862` | ORM SELECT; documented |
| `ChannelEpisode.objects.select_related(...).order_by(...)` / `.all()` | `read` | `td_handlers_gateway.py:1824-1828, 1863` | ORM SELECT; documented |
| `qs.values_list(...).annotate(Count).values_list(...)` | `read` | `td_handlers_gateway.py:1864` | ORM AGGREGATE; documented |
| `timezone.now()` | `read` | `td_handlers_gateway.py:1844` | Clock read; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2920 T0 SIGN Q2 per-tool confirmation: calendar span 1793-1876 contains none of these literals — grep receipts in Rigby T0 SIGN turn 1.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2920 handoff. Expected shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `distribution_tool` (batch 2 — same gateway ORM shape; downstream of publishing schedule); `podcast_tool` (production surface, upstream of episode records); `ats_tool` (batch 2 — recruitment-side content, not publishing calendar).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_autonomous_studio.py` (`ContentChannel`, `ChannelEpisode`).
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1, S2919 Slice 4 batch 2 (discord/distribution/ats/narrative — same gateway ORM-direct shape).
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 14th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list.
  - **Multi-tenant leak on `upcoming` action** — 3rd such instance in gateway (batch 1 campaign_tool.detail + experiment_tool.results + this). Absorbed by single-user pre-prod context; post-D6 evaluation only.
  - **Mixed user-scoping within single response (`stats`)** — 1st instance of this shape. `total_channels` respects `user_id`; `total_episodes` is system-wide. Distinct from cross-action asymmetry. 2nd instance triggers evaluation.
  - **00-START span-math burn (2nd consecutive session)** — S2919 caught calendar=86-claimed vs 166-actual; S2920 caught calendar=166-claimed vs 84-actual. 00-START source likely stale/re-copied. Recommend source-of-truth regen at close.

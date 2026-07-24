# `podcast_tool` — Validation Report (S2922)

**Tool:** `podcast_tool`
**Schema:** `core/services/pa_tool_schemas.py:4841`
**Handler:** `core/services/td_handlers_gateway.py:1959` (`_handle_podcast`)
**Register site:** `core/services/tool_dispatcher.py:584`
**Session:** S2922 (Slice 4 batch 5 — mixed pair: `podcast` pure-READ + `vip_invite` `spreading` mutation; batch shipped per Chris ratification of Claude+Rigby joint recommendation (a) mixed batch)
**HEAD at validation:** `5983f5a23` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full` (all 4 actions in scope this ship — all pure-READ)
**Rigby SIGN:** S2922 T0 SIGN AGREE — 2-turn cycle grounded in 21 `repo_tool` receipts (8 turn 1 + 13 turn 2); zero rubber-stamp; verified handler span 1959–2045 contains no mutation verbs (0/4 `.save()` / `.create()` / `.update()` / `.delete()`) and no first-hop-literal outbound tool dispatch; also verified span-math regen (00-START had claimed 251 lines at S2920 close; actual 87-line body — 162-line drift caught this session via live-evidence regen, per Chris Q5(b) close-ceremony commitment now permanent).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`podcast_tool` surfaces the platform's podcast-studio content substrate: `PodcastShow` (per-show metadata + roll-ups — participant_count, episode_count, total_listens) and `PodcastEpisode` (per-episode rows with title/topic/status/progress/audio_duration/listen_count/script). Use it when the operator asks "which shows exist?" / "what episodes are in flight?" / "give me the script for episode X" / "podcast rollup stats".

Distinct from `campaign_tool` (production campaigns, no audio semantics), from `content_tool` family (blog/social posts, not audio scripts), and from `mobile_tool` (mobile-app introspection — podcast-listener client lives there but the tool doesn't touch it).

## Covered actions

- `shows` — **in scope this ship** — lists `PodcastShow` rows ordered by `-episode_count`. Envelope: `{action, count, shows: [{id, name, format, participant_count, episode_count, total_listens}]}`. User-scoped when `user_id` present (`qs.filter(user_id=user_id)` at handler line 1971).
- `episodes` — **in scope this ship** — lists `PodcastEpisode` rows ordered by `-created_at`. Envelope: `{action, count, episodes: [{id, title, topic, show, status, progress_percent, audio_duration_seconds, listen_count, created_at}]}`. Optional filters: `show_id`, `status`. **Not user-scoped** (see §5).
- `scripts` — **in scope this ship** — returns single episode script (truncated to 3000 chars at handler line 2022). Requires `episode_id`. Envelope: `{action, episode_id, title, script}`.
- `stats` — **in scope this ship** — default action per `payload.get('action', 'stats')` at handler line 1961. Aggregate rollup — `total_shows + total_episodes + total_listens + by_status`. User-scoped when `user_id` present (`shows.filter(user_id=user_id)` + `episodes.filter(user_id=user_id)` at handler lines 2029–2030).

Default action = `stats` (per `payload.get('action', 'stats')` at handler line 1961).

## 3. Schema notes

- **Required:** `action` (enum: `shows` / `episodes` / `scripts` / `stats`).
- **Optional:** `show_id` (str; filters `episodes`), `episode_id` (str; required for `scripts`), `status` (str; filters `episodes`), `limit` (int; default 20, hard cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 1962).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4839-4867`.
- **Envelope shape:** `shows` / `episodes` return a `count` field + list. `scripts` returns single-episode rollup (no `count`). `stats` returns 4 top-level rollup fields (`total_shows`, `total_episodes`, `total_listens`, `by_status`) with no `count`. Consistent with the envelope-key-asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2 (still Chris-gated; no new distinct sub-pattern this batch).
- **`limit` default matches gateway norm:** default 20, cap 50 — same as `campaign_tool` / `experiment_tool` / most gateway tools. Not divergent (contrast with `self_awareness_tool`'s default 10 / cap 30 flagged S2921 as first divergence instance).

## 4. Golden-path examples

**Example 1 — aggregate podcast stats (most operator-common; default action):**
```json
{"action": "stats"}
```
Expected envelope: `{"action": "stats", "total_shows": <int>, "total_episodes": <int>, "total_listens": <int>, "by_status": {"<status>": <int>, ...}}`.

**Example 2 — list shows (ordered by episode_count desc):**
```json
{"action": "shows", "limit": 10}
```
Expected envelope: `{"action": "shows", "count": <int ≤ 50>, "shows": [{"id": "<uuid>", "name": "<str>", "format": "<str>", "participant_count": <int>, "episode_count": <int>, "total_listens": <int>}, ...]}`.

**Example 3 — episodes for a specific show + status filter:**
```json
{"action": "episodes", "show_id": "<uuid>", "status": "published", "limit": 20}
```
Expected envelope: `{"action": "episodes", "count": <int ≤ 50>, "episodes": [{"id": "<uuid>", "title": "<str>", "topic": "<str>", "show": "<show name>", "status": "<str>", "progress_percent": <int>, "audio_duration_seconds": <int|null>, "listen_count": <int>, "created_at": "<isoformat|null>"}, ...]}`.

**Example 4 — episode script (truncated to 3000 chars):**
```json
{"action": "scripts", "episode_id": "<uuid>"}
```
Expected envelope: `{"action": "scripts", "episode_id": "<uuid>", "title": "<str>", "script": "<str ≤ 3000 chars>"}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown podcast_tool action: <action>"}` at handler line 2041. Not raised — in-envelope.
- **Handler exception:** caught at line 2043, logged via `logger.error("[PODCAST] {action} error: {e}", exc_info=True)`, returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (17th corroborating instance post-S2921's 16-instance count). Substrate arc still gated on explicit Chris directive per 00-START forbidden-list; Rigby S2920 Q4(a) semantic-nuance refresh deferred post-D6 per S2921 Q5(c).
- **`scripts` missing `episode_id`:** returns `{"error": "Provide episode_id for scripts"}` at handler line 2014.
- **`scripts` episode not found:** returns `{"error": f"PodcastEpisode {episode_id} not found"}` at handler line 2017.
- **Script hard-truncation:** 3000 chars at line 2022 via `(ep.script or '')[:3000]`. No pagination cursor, no `has_more` flag. Callers wanting full script must query DB directly.
- **Empty result sets:** `shows` / `episodes` return `count: 0` + empty list. `stats` returns zero-valued aggregate + empty `by_status: {}`.
- **`limit` hard cap:** 50 (matches gateway norm).
- **Mixed user-scoping ACROSS actions:** `shows` + `stats` filter by `user_id` when present (handler lines 1971, 2029–2030); `episodes` does **NOT** filter by `user_id` (only by `show_id` / `status` at lines 1988–1993). An operator querying `episodes` sees system-wide rows regardless of their identity. **Candidate 2nd instance of the "mixed user-scoping" Fold** (1st was S2920 `calendar_tool.stats` — same-response field-level mix; podcast case is cross-action within same tool, a related but distinct sub-pattern). Absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`; recorded for post-D6 evaluation.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `PodcastShow.objects.order_by(...).filter(...)[:limit]` | `read` | `td_handlers_gateway.py:1969, 1971-1972, 2026, 2029` | ORM SELECT; documented |
| `PodcastEpisode.objects.select_related('show').order_by(...).filter(...)[:limit]` | `read` | `td_handlers_gateway.py:1987-1994, 2027, 2030` | ORM SELECT with JOIN; documented |
| `PodcastEpisode.objects.filter(id=episode_id).first()` | `read` | `td_handlers_gateway.py:2015` | ORM SELECT by PK; documented |
| `episodes.aggregate(total_listens=Sum('listen_count'))` | `read` | `td_handlers_gateway.py:2031` | ORM aggregate; documented |
| `episodes.values_list('status').annotate(c=Count('id')).values_list('status', 'c')` | `read` | `td_handlers_gateway.py:2032` | ORM group-by; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2922 T0 SIGN Q2 per-tool confirmation: podcast span 1959–2045 contains none of these literals — grep receipts in Rigby T0 SIGN turn 2 (`repo_tool.read_file` on the handler span; `search` for `"podcast_tool"` returned 0 matches inside `td_handlers_gateway.py`; no outbound first-hop-literal dispatch).

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification on all 4 actions appended to the S2922 handoff. Expected envelope shapes documented in §4 golden-path examples.

## Related

- **Adjacent tools:** `campaign_tool` (batch 1 — same gateway ORM shape, campaigns not podcasts); `experiment_tool` (batch 1 — same shape, A/B tests); `mobile_tool` (batch 3 — filesystem-read shape); `vip_invite_tool` (this batch — spreading mutation shape).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1 — §5a 4-tier blast-radius taxonomy amended S2921); models at `core/models_podcast_studio.py` (`PodcastShow`, `PodcastEpisode`).
- **Prior ratifications:** S2892 Path B open, S2918–S2921 Slice 4 batches 1–4.
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 17th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list.
  - **Mixed user-scoping ACROSS actions within a single tool** — candidate 2nd instance of the "mixed user-scoping" Fold pattern (1st was S2920 calendar_tool.stats intra-response mix). Cross-action variant is a related-but-distinct sub-pattern; recorded for post-D6 evaluation.
  - **Script hard-truncation without pagination cursor** — 3000-char cap at handler line 2022 with no `has_more` flag. Recorded as authoring detail; not a defect. Absorbed by single-user pre-prod (Chris rarely reads full scripts through Rigby); may resurface post-D6.
  - **00-START span-math regen validated a 2nd time** — podcast 251-claim vs 89-actual (162-line drift). Per S2921 Q5(b) Chris ratification, close-ceremony span-math regen is now a permanent step; this session's live-evidence regen surfaced the drift for this ship.

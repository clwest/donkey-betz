# `video_history_tool` — Validation Report (S2911)

**Tool:** `video_history_tool`
**Schema:** `core/services/pa_tool_schemas.py:1212`
**Handler:** `core/services/td_handlers_agents.py:4551` (`_handle_video_history`)
**Register site:** `core/services/tool_dispatcher.py` (via `AgentHandlersMixin`)
**Session:** S2911 (Path B systematic sweep — Slice 2 batch 6a of `td_handlers_agents`)
**HEAD at validation:** `5d79d8431` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 2 MUTATION actions explicitly excluded — see §5a).
**Rigby SIGN:** S2911 T0 SIGN AGREE-with-edits (batch 6a shape ratified; async Celery dispatch shape for `transcribe` + `content_pack` documented in §5a). S2911 T1 SIGN AGREE-with-edits (Q1 verified transcribe idempotent-guard against handler lines 4678-4683; Q2 all 4 required-arg-error handler lines 4602/4613/4653/4711 spot-checked and match doc citations).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Search, browse, and process the user's video history — the `VideoHistory` model surface. Answers "what videos do I have?", "find my video called X", "get metadata for this video by UUID or sequential-number", "start transcription", "check transcript progress", "generate a content pack from a transcript".

Distinct from `media_tool` (which spans images + videos + audio — S2908 batch 4 tool with `delete` IRREVERSIBLE) — `video_history_tool` is video-only and adds the video-processing workflow (transcribe → transcript_status → content_pack chain). Distinct from `obs_tool` (which POSTs video-upload from OBS recording bridge) — `video_history_tool` operates on already-persisted `VideoHistory` rows.

## Covered actions

**READ_ONLY actions covered only (5 of 7 total actions).** 2 MUTATION actions (excluded — see §5a Mutation containment for named actions, Celery-dispatch semantics, and planned coverage slice) are out of scope for this ship.

- `list` — **in scope this ship** — verified live via T1a harness (`status_code=200`, `expected_outcome=success`, 27 ms). Returns `{action, count, videos}` — user-scoped `VideoHistory` rows filtered by optional `video_type` + defaulted `status='completed'`; limit capped at 50.
- `search` — **in scope this ship** — verified live via T1a harness error path (`error_captured`, requires `query`). Raises `ValueError('query parameter required for search action')` at handler line 4602.
- `detail` — **in scope this ship** — verified live via T1a harness error path (`error_captured`, requires `id | sequential_number`). Raises `ValueError` at handler line 4613.
- `resolve` — **in scope this ship** — verified live via T1a harness error path (`error_captured`, requires `id | sequential_number | query (as URL)`). Raises `ValueError` at handler line 4653.
- `transcript_status` — **in scope this ship** — verified live via T1a harness error path (`error_captured`, requires `transcript_id | id | sequential_number`). Raises `ValueError` at handler line 4711.
- `transcribe` — **mutation — deferred (dispatches Celery Whisper task)** — see §5a
- `content_pack` — **mutation — deferred (dispatches Celery content-pack task)** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `list, search, detail, resolve, transcribe, transcript_status, content_pack`).
- **Conditional required (handler-enforced, per action):**
  - `query` for `search` — fail-loud via `ValueError`.
  - `id | sequential_number` for `detail` / `transcribe` / `content_pack` — fail-loud via `ValueError`.
  - `id | sequential_number | query (as URL)` for `resolve` — fail-loud via `ValueError`.
  - `transcript_id | id | sequential_number` for `transcript_status` — fail-loud via `ValueError` (`transcript_id` preferred; if missing, latest-by-video lookup fires).
- **Optional:** `video_type` (filter for `list`), `status` (filter for `list`; defaults to `'completed'`), `limit` (default 10, cap 50 for `list` / `search`), `language` (default `'en'` for `transcribe`).
- **Sequential-number semantics:** `sequential_number` is computed (`get_sequential_number()`), not a stored DB field. Handler resolves it via full user-scoped `order_by('created_at').values_list('id', flat=True)` then indexes — O(N) on user video count. Documented at handler line 4617.

## 4. Golden-path examples

**"Show me my recent videos:"**

```
video_history_tool  action=list  limit=10
```

**"Find videos about 'onboarding':"**

```
video_history_tool  action=search  query="onboarding"
```

**"Get full metadata for video #3:"**

```
video_history_tool  action=detail  sequential_number=3
```

**"Check transcript progress:"**

```
video_history_tool  action=transcript_status  transcript_id=<uuid>
```

Alternate: `action=transcript_status  sequential_number=3` (latest transcript for that video).

**"Resolve any reference to full metadata:"**

```
video_history_tool  action=resolve  id=<uuid>
```

## 5. Failure / empty-state / pagination notes

- **`list` empty result** — returns `{action: 'list', count: 0, videos: []}`. Consistent shape.
- **`search` with no matches** — returns `{action: 'search', query, count: 0, videos: []}`. Consistent shape.
- **`detail` sequential_number out-of-bounds** — falls into "video not found" branch (handler line 4622: `v = None`), raises `ValueError('Video not found')` → `TOOL_EXCEPTION`.
- **`detail` / `resolve` UUID not found** — raises `ValueError('Video not found')` → `TOOL_EXCEPTION`.
- **`transcript_status` with only `id`/`sequential_number` (no `transcript_id`)** — fallback path fires: `resolve_video()` → latest `VideoTranscript.filter(video_id).order_by('-created_at').first()`. If no transcript exists, raises `ValueError('Provide transcript_id, or id/sequential_number of the video')` at handler line 4711 (fallback failed to find a transcript). This is a `error_captured` shape.
- **`transcript_status` when `status='completed'`** — response adds `text` (truncated 3000 chars), `text_length`, `segment_count`, `duration_seconds`, plus `truncated: True` when text > 3000 chars.
- **All required-arg-missing paths** — raise `ValueError` → `TOOL_EXCEPTION` (HTTP 500) → `error_captured`. Fail-loud, not silent. Same clean-exception shape as `brainstorm_tool` (S2910) + `opportunity_manager_tool.get` (this batch).
- **Unknown action** — raises `ValueError(f'Unknown video_history_tool action: {action}')` at handler line 4764 → `TOOL_EXCEPTION`.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating actions excluded this ship:**
  - `transcribe` — creates a `VideoTranscript` row via `VideoTranscript.objects.create(...)` at handler line 4684, then dispatches `transcribe_video_task.delay(str(transcript.id))` to Celery (Whisper transcription — async, LLM/CPU cost). **Idempotent-guarded**: pre-check at handler line 4678 returns the existing queued/running transcript instead of creating a duplicate. Classified `MUTATION`.
  - `content_pack` — dispatches `generate_video_content_pack_task.delay(resolved.id, str(user_id), language)` to Celery at handler line 4752 (LLM-heavy content-pack generation — titles + summary + chapters + YT description). Pre-requires a completed `VideoTranscript` (raises `ValueError('No completed transcript. Transcribe the video first.')` at line 4751 if missing). Classified `MUTATION`.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'`; harness skips via `resolve_safety()` (`expected_outcome=skipped_mutation` — verified in artifact §6.1).
- **dependency_surface note:** `internal` — Celery async dispatch (existing `transcribe_video_task` + `generate_video_content_pack_task`). No external bridge. `transcribe_video_task` internally calls Whisper (external LLM); `generate_video_content_pack_task` calls LLM for content-pack shape.
- **Deferral rationale:** both actions require a real `VideoHistory` row + real user context + tolerance for real Celery task-queue accrual + real LLM cost (Whisper transcription latency + content-pack LLM tokens). Doc-only sweep cannot exercise them safely. Deferred to a future MUTATION-coverage batch pairing with a seeded-video harness pattern + `dry_run` semantics (candidate — Rigby T1 SIGN can pressure-test whether MUTATION-coverage needs a dedicated sub-arc, especially given the video/audio-processing pipeline complexity).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness video_history_tool` at HEAD `5d79d8431` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list` | `success` | 200 | 27 ms | `action, count, videos` |
| `search` | `error_captured` | 500 | 7 ms | — (`error_code=TOOL_EXCEPTION; msg=query parameter required for search action`) |
| `detail` | `error_captured` | 500 | 1 ms | — (`error_code=TOOL_EXCEPTION; msg=id or sequential_number required for detail action`) |
| `resolve` | `error_captured` | 500 | 3 ms | — (`error_code=TOOL_EXCEPTION; msg=Provide id, sequential_number, or query (URL) for resolve`) |
| `transcribe` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `transcript_status` | `error_captured` | 500 | 2 ms | — (`error_code=TOOL_EXCEPTION; msg=Provide transcript_id, or id/sequential_number of the video`) |
| `content_pack` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/video_history_tool.json`.

**Envelope-shape observation:** all 4 required-arg misses raise `ValueError` → dispatcher wraps at `TOOL_EXCEPTION` (HTTP 500) → `error_captured`. Behaviorally clean fail-loud, matching `brainstorm_tool` (S2910) + `opportunity_manager_tool` (this batch) baseline. NOT the inline `{ok: false}` envelope pattern (no FT-5 candidate contribution). No `bridge` field — pure ORM + Celery-dispatch, no bridge preflight needed.

### 6.2 Runtime-not-executed — this ship

- **`list` with populated video corpus** — not exercised against real videos (would confirm the 13-key serialized row shape from `_serialize()` at handler line 4571 — id, sequential_number, title, original_filename, video_url, thumbnail_url, video_type, source_type, status, duration, resolution, file_size_bytes, created_at).
- **`list` with `video_type` filter** — not exercised (would confirm filter propagation).
- **`search` with a real query + matches** — not exercised (would confirm Q-filter propagation on `prompt` vs `original_filename` icontains matches).
- **`detail` with a real UUID / sequential-number** — not exercised (would confirm full-detail-shape expansion: adds model_used, tags, user_notes, is_favorite, view_count, download_count, fps, codec, ratio, view_url).
- **`resolve` with a real ref** — not exercised (would confirm `ResolvedVideo.to_dict()` shape from `core/video_resolver.py`).
- **`transcript_status` with a completed transcript** — not exercised (would confirm text/segment/duration expansion + `truncated` flag for text > 3000 chars).
- **Both MUTATION actions (`transcribe` / `content_pack`)** — MUTATION-skipped (see §5a).

---

## Related

- **Ledger candidates surfaced this ship:** none new for this tool. Clean fail-loud shape on all required-arg-missing paths. `transcribe` idempotent-guard is a good pattern to consider promoting elsewhere.
- **Adjacent tools:**
  - `media_tool` — cross-media (image + video + audio) with `delete` IRREVERSIBLE (S2908 batch 4); overlaps this tool's list/detail surface on the video slice.
  - `obs_tool` — OBS bridge POST /v1/recording/upload_last (uploads OBS recording → creates `VideoHistory` row); upstream data source for this tool.
  - `davinci_tool` — DaVinci Resolve render surface; produces videos consumed by this tool downstream.
- **Substrate context:** fourth tool in Slice 2 batch 6a. Most complex tool in the batch (7 actions, mixed R + async-Celery-MUTATION). Async-dispatch MUTATION pattern (Celery `.delay()` returning `task_id`) is distinct from ORM-write MUTATION patterns in the other batch-6a tools (opportunity_manager.create, task_manager.update, etc.) — future MUTATION-coverage batch may want to split by dispatch-shape.
- **Metadata seed:** 7 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (Pattern C — per-action records; no `TOOL_DEFAULTS` entry).

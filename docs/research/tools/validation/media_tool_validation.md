# `media_tool` — Validation Report (S2908)

**Tool:** `media_tool`
**Schema:** `core/services/pa_tool_schemas.py:1074`
**Handler:** `core/services/td_handlers_agents.py:4161` (`_handle_media`)
**Register site:** `core/services/tool_dispatcher.py:405`
**Session:** S2908 (Path B systematic sweep — Slice 2 batch 4 of `td_handlers_agents`, first mixed-tool-scoped-to-READ_ONLY-subset batch per Fold A shape-break commitment ratified at S2907 close)
**HEAD at validation:** `03ee92d5f`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; IRREVERSIBLE mutation action explicitly excluded — see §5a).
**Rigby SIGN:** S2908 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Cross-model media library browser — spans `ImageHistory`, `VideoHistory`, and `AudioHistory` under one uniform surface. Introspection actions expose user-scoped listings (optionally filtered by media type or content subtype), single-asset detail lookups by UUID, and aggregate counts. Mutation action `delete` is out of scope for this validation ship — see §5a.

Use `list` when the caller needs a recent-media view across all three models (or a single-type slice). Use `detail` when the caller has a UUID and needs the full metadata payload for one asset. Use `stats` for aggregate counts by type (dashboards, "how much have I made?" queries).

## 2. Covered actions

**READ_ONLY actions covered only (3 of 4 total actions).** Mutation action (1 excluded, classified IRREVERSIBLE — see §5a Mutation containment for the named action, deferral rationale, and planned coverage slice) is out of scope for this ship.

- `list` — **in scope this ship** — verified live via T1a harness. Returns `{action, count, items}` — cross-model iteration through `ImageHistory / VideoHistory / AudioHistory`, user-scoped by `user_id`, sorted by `created_at` desc, limit-capped at 50 (default 10).
- `detail` — **in scope this ship** — verified live via T1a harness error path (requires `id`). Returns `{action, id, media_type, created_at, ...extra_fields}` for the matching asset across all 3 models. Raises `ValueError` when `id` missing.
- `stats` — **in scope this ship** — verified live via T1a harness. Returns `{action, images, videos, audio, total}` — user-scoped aggregate counts per media type.
- `delete` — **mutation — deferred to Slice 2 write batch** — see §5a. Classified `IRREVERSIBLE` in `TOOL_ACTION_METADATA`; harness reports `expected_outcome=skipped_mutation`. Hard-deletes the matching `ImageHistory` / `VideoHistory` / `AudioHistory` row + associated Cloudinary asset (irreversible).

## 3. Schema notes

- **Required:** `action` (enum: `list, detail, stats, delete`).
- **Conditional required (handler-enforced):**
  - `id` for `detail` — fail-loud via `ValueError` when missing.
  - `id` for `delete` — fail-loud via `ValueError` when missing (out of scope this ship).
- **Optional:** `media_type` (enum: `image, video, audio, all` — default `all`), `content_type` (string — filters `image_type` / `video_type` / `audio_type`), `limit` (int — default 10, hard-capped at 50 in handler line 4174).
- **No required args** for `list` and `stats`.
- **User scoping:** all queries pass through `_qs(model)` helper (handler line 4177) which applies `user_id` filter when present; anonymous callers get unfiltered results (existing pattern — not this ship's scope to relitigate).

## 4. Golden-path examples

**"Show me my recent media (all types):"**

```
media_tool  action=list
```

**"Show me my last 20 videos only:"**

```
media_tool  action=list  media_type=video  limit=20
```

**"Filter by generated images:"**

```
media_tool  action=list  media_type=image  content_type=generated
```

**"How many assets do I have total?"**

```
media_tool  action=stats
```

**"Get full metadata for one asset:"**

```
media_tool  action=detail  id=<uuid>
```

## 5. Failure / empty-state / pagination notes

- **`list` empty result** — returns `{action: 'list', count: 0, items: []}` when the user has no media matching the filter. Same shape as populated result.
- **`stats` with zero media** — returns `{action: 'stats', total: 0, ...}` with per-type counts all zero. Consistent shape.
- **`detail` fail-loud on missing `id`** — raises `ValueError('id parameter required for detail action')` at handler line 4240 → `TOOL_EXCEPTION` at HTTP 500. Standard `ValueError`-raise pattern (contrast the inline `{ok: false}` envelope pattern of `davinci_tool.health` + `obs_tool.health` this batch).
- **`detail` with UUID not matching any model row** — iterates all 3 models; when none match, raises `ValueError(f'Media asset {mid} not found')` → `TOOL_EXCEPTION` at HTTP 500.
- **Unknown action** — raises `ValueError('Unknown action: {action}')` at handler line 4310 → `TOOL_EXCEPTION` at HTTP 500.
- **Limit clamp** — `list` clamps `limit` at 50 via `min(payload.get('limit', 10), 50)` on line 4174. Handler-side hard cap; schema description says "max 50" and handler enforces.
- **Cross-model result sort** — after cross-model gather, list is re-sorted by `created_at` desc and truncated to `limit` again (handler line 4233-4234). Guarantees stable temporal ordering across mixed types.
- **No `handler_exception` catch** — unlike `bpaas_tool` (structured envelope) and `orm_inspect_tool` (inline envelope), `_handle_media` does NOT wrap raised exceptions; they propagate to the dispatcher-layer `TOOL_EXCEPTION` wrapper.

## 5a. Mutation containment (per Rigby T0 SIGN edit — mandatory §5a)

- **Mutating action excluded this ship:**
  - `delete` — destroys the target row via `obj.delete()` (handler line 4301) across `ImageHistory / VideoHistory / AudioHistory`. Classified `IRREVERSIBLE` in `TOOL_ACTION_METADATA` seed this ship — no soft-delete, no confirm flag, no undo path. Row destruction is immediate and unrecoverable from within the platform surface.
- **Containment mechanism:** `TOOL_ACTION_METADATA` per-action record with `safety_class='IRREVERSIBLE'` this ship (only IRREVERSIBLE classification in the 20-record batch); harness resolves via `resolve_safety()` and skips at dispatch (see harness artifact `expected_outcome=skipped_irreversible`).
- **dependency_surface note:** `internal` — all 4 actions read/write against Django ORM models only. No external bridge, no third-party API.
- **Deferral rationale:** `delete` requires (a) a dedicated deletion-flow validation shape that this doc-only sweep pattern does not currently accommodate + (b) a confirmation-flow design decision (should the tool grow a `confirm=true` gate before shipping mutation coverage?). Both concerns escalate beyond a doc-only ship. Deferred to a mutation-coverage batch that pairs with a confirmation-flow design ADR (candidate — Rigby T1 SIGN can pressure-test whether this should escalate to Chris).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness media_tool` at HEAD `03ee92d5f` (2026-07-23):

- **`list`:** `response_shape_keys=[action, count, items]`, `status_code=200`, `expected_outcome=success`. Clean shape — cross-model gather + sort worked.
- **`detail`:** `response_shape_keys=[]`, `status_code=500`, `expected_outcome=error_captured`, `notes=error_code=TOOL_EXCEPTION; msg=id parameter required for detail action`. Correct fail-loud.
- **`stats`:** `response_shape_keys=[action, audio, images, total, videos]`, `status_code=200`, `expected_outcome=success`. Clean shape — 4 per-type counts + total.
- **`delete`:** `expected_outcome=skipped_irreversible`, `input_profile=skipped_no_dispatch`. Correctly skipped per S2908 seed (only IRREVERSIBLE skip this batch).

Artifact: `docs/audits/pa_tools/harness_output/media_tool.json`.

**Envelope-shape observation:** `media_tool` uses the `ValueError`-raise-into-`TOOL_EXCEPTION` pattern for validation failures (via HTTP 500) rather than the inline `{ok: false, error, error_code}` envelope pattern of `orm_inspect_tool` (S2907) and this batch's `davinci_tool.health/jobs` + `obs_tool.health/status/last`. No classification drift on `media_tool` this ship — the 500-status-code error branch correctly maps to `error_captured` outcome.

### 6.2 Runtime-not-executed — this ship

- **`list` with a real populated media library** — not exercised (would confirm the item shape per media type + the cross-model sort ordering).
- **`detail` with a real UUID** — not exercised (would confirm the type-specific `extra_fields` shape for each of `image` / `video` / `audio`).
- **`list` with `content_type` filter** — not exercised (would confirm the content-subtype filter propagates correctly across models).
- **`list` limit clamp** — not exercised with limit >50 (would confirm the handler-side `min(..., 50)` clamp fires).
- **`delete`** — not exercised (IRREVERSIBLE-skipped).

---

## Related

- **Ledger candidates surfaced this ship:**
  - **Confirmation-flow gap on IRREVERSIBLE delete** — `media_tool.delete` destroys media rows with no confirm flag, no soft-delete, no undo path. Only IRREVERSIBLE-classified action across the 4-tool batch. Candidate for a confirmation-flow ADR before mutation coverage ships; T1 SIGN can pressure-test whether this escalates to Chris. Substrate/design-arc scope; deferred.
- **Adjacent tools:** `bpaas_tool`, `davinci_tool`, `obs_tool` (this batch peers). `video_history_tool` (untested — video-specific sibling with transcribe/content_pack surface).
- **Substrate context:** T1b `Template version: v1` sweep variant. First mixed-scoped-to-READ_ONLY-subset ship per Fold A commitment; Rigby T0 SIGN AGREE-with-edits ratified 4-tool batch composition + §5a mandatory rule + dependency_surface doc note. First IRREVERSIBLE-classified action in the sweep corpus (all prior mutation-class seeds have been `MUTATION` or `WRITE_GATED`).
- **Metadata seed:** `TOOL_ACTION_METADATA` per-action records for all 4 actions added at `core/services/tool_action_metadata.py` this ship (Pattern C — no `TOOL_DEFAULTS` entry; per-action records are the safety source).

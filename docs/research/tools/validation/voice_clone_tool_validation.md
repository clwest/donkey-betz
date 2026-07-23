# `voice_clone_tool` — Validation Report (S2907)

**Tool:** `voice_clone_tool`
**Schema:** `core/services/pa_tool_schemas.py:1107`
**Handler:** `core/services/td_handlers_agents.py:4312` (`_handle_voice_clone`)
**Register site:** `core/services/tool_dispatcher.py:406`
**Session:** S2907 (Path B systematic sweep — Slice 2 batch 3 of `td_handlers_agents`, second accelerated batch post-substrate arc close, first small-actionful all-READ_ONLY stress test per S2906 T0 SIGN Fold A commitment)
**HEAD at validation:** `b02f08016`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised via T1a harness).
**Rigby SIGN:** S2907 T1 SIGN (pending) — see §Related.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only inspection surface over `VoiceProfile` + `VoiceCloneRequest` rows — the voice-cloning marketplace substrate. Answers "what voices has the user cloned, what does voice X look like, what's the clone-request history, what's available in the public marketplace, what are the voice stats?" Use when the user asks about their cloned voices, the voice marketplace, or clone-request history.

**Not a cloning surface.** Voice cloning from audio files is done via the web UI (`/workspace > Voice Marketplace > Clone Voice`) or the Discord `/voice clone` command. `voice_clone_tool` is the read-only inspection sibling — no cloning, no purchases, no marketplace listings created through this tool.

Distinct from `media_tool` (browses AI-generated audio/video/images generally) and from `video_history_tool` (video-specific browse + transcription). `voice_clone_tool` is specifically the voice-profile inspection surface.

## Covered actions

- `list` — **in scope this ship** — verified live via T1a harness. Returns `{action, count, voices[]}`; each voice carries `id, name, elevenlabs_voice_id, gender, creation_method, is_public, total_uses, average_rating, created_at`. Filtered to the calling user's owned voices when `user_id` is set (owner-scoped queryset via `_user_qs` helper). Ordered by `-created_at`. Hard-capped at 20 rows (handler-side, not schema-declared).
- `detail` — **in scope this ship** — verified via T1a harness error path (handler is fail-loud on required `id`). Requires `id` payload; returns full voice metadata including description, style_tags, primary_use_case, price_display, owner username. Not exercised with a real voice id in this sweep — see §5.
- `clone_requests` — **in scope this ship** — verified live via T1a harness. Returns `{action, count, requests[]}`; each request carries `id, status, recording_duration, voice_id, error, created_at`. Filtered to caller's requests via `user_id`. Ordered by `-created_at`. Hard-capped at 10 rows (handler-side).
- `marketplace` — **in scope this ship** — verified live via T1a harness. Returns `{action, count, voices[]}` filtered to `is_public=True, is_active=True`. Ordered by `-is_featured, -average_rating`. Supports `search` param (Q-object over `name` + `description`). **Silent limit clamp at 30** — see §5 drift finding.
- `stats` — **in scope this ship** — verified live via T1a harness. Returns `{action, my_voices, marketplace_total, my_total_uses, my_total_revenue}` — aggregate counts + revenue sum across the user's voices. Revenue rendered as string (Decimal serialization).

## 3. Schema notes

- **Required:** `action` (enum: `list, detail, clone_requests, marketplace, stats`).
- **Conditional required:** `id` at handler level for `detail` (schema declares as optional). Recurring S2892/S2893 pattern of handler-required-but-schema-optional args.
- **Optional:** `search` (marketplace only), `limit` (default 10 in schema — clamped to 30 in handler for marketplace; NOT respected for list/clone_requests which use hard-coded caps at 20 and 10).
- **Handler-side hard caps:** `list` capped at 20 (line 4333, silent slice); `clone_requests` capped at 10 (line 4382, silent slice); `marketplace` capped at 30 via `min(payload.get('limit', 10), 30)` (line 4397). None declared in schema.

## 4. Golden-path examples

**"What voices have I cloned?"**

```
voice_clone_tool  action=list
```

**Full detail on one voice:**

```
voice_clone_tool  action=detail  id=<VoiceProfile UUID>
```

**Clone-request history:**

```
voice_clone_tool  action=clone_requests
```

**Browse public marketplace, keyword search:**

```
voice_clone_tool  action=marketplace  search=narrator  limit=20
```

**Aggregate voice + revenue stats:**

```
voice_clone_tool  action=stats
```

## 5. Failure / empty-state / pagination notes

- **No pagination on any action** — every action returns a single page bounded by hard-coded caps (20 / 10 / 30) or the schema `limit` (marketplace only, but silently clamped). No `has_more/offset` cursor.
- **`detail` without `id` raises ValueError** — surfaced as `TOOL_EXCEPTION` error envelope by the dispatcher (verified via T1a harness). Handler fail-loud on required arg. Same class as `pilots_tool` / `gates_tool` / `ml_analysis`.
- **`detail` with non-existent id raises ValueError** — handler at line 4355 raises `ValueError(f"Voice {voice_id} not found")` when the queryset misses. Surfaced as `TOOL_EXCEPTION`. Not exercised with a synthetic bad id in this sweep.
- **Silent limit clamp at 30 on marketplace** — handler at line 4397 does `min(payload.get('limit', 10), 30)` without a `truncated` field or response signal. If Rigby asks for `limit=100`, she gets 30 with no indication. Same F-RT-2 silent-truncation class as `cost_telemetry_tool` (`limit` capped at 50) and `repo_tool` (F-RT-2 pattern). **Ledger candidate — see §Related.**
- **Silent hard caps on list/clone_requests** — 20 and 10 respectively. Not tunable via schema. Rigby cannot ask for more even if she wanted to; the schema-declared `limit` param is silently ignored for these actions.
- **Empty-state on all list-shaped actions** — returns `count: 0` + empty list. No exception; safe fall-through.
- **Anonymous user (`user_id=None`) defense-in-depth note** — `_user_qs` helper falls back to unfiltered queryset when `user_id` is falsy. In the PA dispatch path today `user_id` is passed by the dispatcher and expected non-null; this fall-back is defense-in-depth against a caller that bypasses the standard path. Not verified end-to-end this ship; treat as a "would need audit before opening this tool to un-authenticated callsites," not a documented live regression.
- **Unknown action raises ValueError** — surfaces as `TOOL_EXCEPTION`. Consistent fail-loud with `pilots_tool`/`gates_tool`.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** none. All 5 actions are pure ORM reads against `VoiceProfile` + `VoiceCloneRequest`. Actual voice cloning is done via a separate Web UI / Discord path — this tool never triggers a clone request.
- **Containment protocol:** N/A — no state modification possible via this tool's dispatch surface.
- **Safety metadata:** `voice_clone_tool` seeded in `TOOL_DEFAULTS` at S2907 with `default_safety_class='READ_ONLY'`.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness voice_clone_tool` at HEAD `b02f08016` (2026-07-23):

- **`list` (22ms):** `response_shape_keys=['action', 'count', 'voices']` — `success`. Empty-state exercised (harness runs against test DB with no voices for the harness user); `count: 0, voices: []` returned cleanly.
- **`detail` (6ms):** `error_captured` — `error_code=TOOL_EXCEPTION`, `msg="id parameter required for detail action"`. Expected: handler is fail-loud on required arg.
- **`clone_requests` (14ms):** `response_shape_keys=['action', 'count', 'requests']` — `success`. Empty-state exercised.
- **`marketplace` (4ms):** `response_shape_keys=['action', 'count', 'voices']` — `success`. Empty-state exercised (no public voices in test DB).
- **`stats` (6ms):** `response_shape_keys=['action', 'marketplace_total', 'my_total_revenue', 'my_total_uses', 'my_voices']` — `success`. Aggregate counts + Decimal-serialized revenue string returned.

Artifact: `docs/audits/pa_tools/harness_output/voice_clone_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **`detail` with a real voice id** — not exercised. Would confirm the full-metadata positive path + verify all declared fields render.
- **`marketplace` with `search` and `limit > 30`** — not exercised. Would confirm the silent clamp visibly + verify the Q-object OR-search behavior across name + description.
- **`stats` with real voice ownership** — harness dispatch confirms shape; revenue-Decimal serialization edge cases not stress-tested with high-precision values.

## 6a. Next batch shape (per Rigby S2907 T0 SIGN zoom-out E)

Per Rigby T0 SIGN zoom-out E (2026-07-23), the S2907 batch composition sustains a **uniform READ_ONLY multi-action** shape (batch 2 was uniform actionless; batch 3 is uniform small-actionful). Repeated uniform-only batches risk three couplings: (1) T1b template v1 gets implicitly optimized for the easy shape; (2) drift-find rate becomes selection-biased curation rather than ecosystem truth; (3) the hard governance muscle for mixed-safety and gated-write tools stays unexercised.

**S2908 commitment (Chris ratified 2026-07-23):** batch 4 MUST break the uniform pattern. Two acceptable shapes:

- **Mixed-tool scoped to READ_ONLY subset:** pick a tool with both READ_ONLY and WRITE actions, cover only the READ_ONLY actions in this doc, document the scoping explicitly in `## Covered actions`. Tests Template v1's mixed-pattern representation without taking write risk.
- **Gated-write dry_run-only:** pick a tool with a dry_run path (e.g., autopilot_tool, security_containment_plan), cover only the dry_run branch. Tests schema/handler gating and metadata correctness without mutations.

Do NOT open S2908 with another uniform-READ_ONLY multi-action batch.

---

## Related

- **Ledger candidates surfaced this ship:**
  - **`marketplace` silent `limit` clamp at 30** (`td_handlers_agents.py:4397`). Same silent-truncation class as `cost_telemetry_tool` `limit` cap at 50 (S2905 ledger candidate) and `repo_tool` F-RT-2/F-RT-5 patterns. Recommended remediation: return `truncated: true` + `original_limit_requested` fields when the clamp fires. Deferred (batch-scope discipline).
  - **`list` + `clone_requests` schema-declared-but-hard-capped in handler** (`td_handlers_agents.py:4333` = 20 and `:4382` = 10). Schema-declared-but-handler-ignored `limit`. Same class as S2906 `get_system_alerts` schema-declared `limit`. Deferred.
  - Contributes to S2906 Fold B systemic drift trend candidate — data point #3 this batch. If sustained across batches 4-5, promote to Playbook amendment or dedicated cleanup arc.
- **Adjacent tools:** `media_tool` (untested — general AI-generated media browse), `video_history_tool` (untested — video-specific, includes async transcribe/content_pack mutations).
- **Substrate context:** T1b `Template version: v1` sweep variant. Small-actionful stress test of `## Covered actions` handler-trace-evidence claim under 5-action enumeration.
- **Batch peers:** `ml_analysis`, `orm_inspect_tool` (Slice 2 batch 3).

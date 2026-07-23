# `studio_tool` — Validation Report (S2917)

**Tool:** `studio_tool`
**Schema:** `core/services/pa_tool_schemas.py:1549`
**Handler:** `core/services/td_handlers_core.py:951` (`_handle_studio`)
**Register site:** `core/services/tool_dispatcher.py:493`
**Session:** S2917 (Path B systematic sweep — Slice 3 batch 7 of `td_handlers_core`, async duo)
**HEAD at validation:** `d884d9c8c` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Live-exercise deferred per §5a for the 4 async-MUTATION actions; §6 covers the 2 READ_ONLY actions.
**Category upgrade target:** `untested` → `validated_partial` (2 READ_ONLY actions validated + documented; 4 MUTATION actions documented but not live-exercised — MIXED-safety per-action seed).
**Rigby SIGN:** S2917 T0 SIGN AGREE (Q1 ship-both) + AGREE-WITH-EDITS on Appendix A shape (Q2). Rigby Q1 tool-probe count: ~8 distinct callees over 237 lines (`_handle_studio` :951→:1187). Rigby Q4 pushback adopted: fan-out presence is itself an opacity flag regardless of callee count.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Unified creative-media studio. Dispatches AI generation jobs (image / video / audio / talking-video) into Celery workers and exposes read-side surfaces to poll job state and list generation history. This is the tool Rigby picks when a user says "generate an image / create a video / make audio / do TTS / turn this into a talking character."

Distinct from `intelligence_tool` (RAG/desk composite reader), from `research_and_create_tool` (single actionless research-and-write chain), from `davinci_tool` (external DaVinci Resolve render bridge, no AI generation), from `obs_tool` (OBS recording bridge), and from `media_tool` (post-generation history CRUD across `ImageHistory`/`VideoHistory`/`AudioHistory` — this tool creates those rows via downstream agents; `media_tool` deletes and reads them).

## Covered actions

Six actions in the schema `action` enum (`pa_tool_schemas.py:1561-1565`), all handled inside `_handle_studio` (`td_handlers_core.py:951-1187`). Composition is **MIXED — 4 MUTATION (async fan-out) + 2 READ_ONLY**. Per-action safety seeded in `TOOL_ACTION_METADATA` this ship (no `TOOL_DEFAULTS` entry — mixed composition per revenue_tracker_tool / session_tool / batch-4 precedent).

- `generate_image` — **MUTATION, deferred to Slice X.Yb** — see §5a. Celery fan-out via `execute_agent_task.apply_async(['ImageAgent', task_text, ctx], queue='long_running')` at `td_handlers_core.py:978-980`. Returns `{task_id, mode='async', agent='ImageAgent', message}`.
- `generate_video` — **MUTATION, deferred to Slice X.Yb** — see §5a. Same fan-out shape, `VideoAgent` at `:1002-1004`. Returns same envelope.
- `generate_audio` — **MUTATION, deferred to Slice X.Yb** — see §5a. Same shape, `AudioAgent` at `:1063-1065`. Returns same envelope.
- `create_talking_video` — **MUTATION, deferred to Slice X.Yb** — see §5a. Distinct task: `create_talking_video_task.apply_async([image_prompt, script, ctx], queue='long_running')` at `:1039-1041`. Returns `{task_id, mode='async', agent='ImageAgent → TalkingCharacterAgent', message}`. Two-stage pipeline (image → talking video) in one task; validates `prompt` + `script` required.
- `job_status` — **in scope this ship** — reads `CeleryTaskEvent` then falls through to `AsyncResult` if no telemetry row, enriches via `self._get_agent_execution_output(job_id, exec_id)` when the task result carries an `execution_id`. Return shape varies by branch: telemetry-first (`{job_id, status, started_at, finished_at, duration_ms, ...enriched}`) vs celery-fallback (`{job_id, status: pending|queued|running|completed|failed, [error|content|agent|execution_time_ms]}`). Terminal `{job_id, status: 'unknown'}` if both paths fail.
- `list_jobs` — **in scope this ship** — reads `ImageHistory` + `VideoHistory` + `AudioHistory` (user-scoped by ORM default order), merges, sorts by `created_at desc`, caps at `min(limit, 50)`. Returns `{count, jobs: [{id, type, prompt, created_at}]}`. Each history-table read is wrapped in a `try/except` that logs a `swallowed (...) — degraded` warning and continues — a missing table or ORM error degrades that media-type silently instead of failing the whole action.

## 3. Schema notes

- **Required:** `action` (must be one of the 6 enum values). Schema at `pa_tool_schemas.py:1617` declares `required: ['action']`.
- **Generation params (used by generate_image/video/audio + create_talking_video):**
  - `prompt` (str) — generation prompt. Handler prefixes `"Generate image: "` / `"Generate video: "` / `"Generate audio: "` if the raw prompt doesn't already start with a generation verb (see the `raw_prompt.lower().startswith(...)` guards at `:966`, `:992`, `:1057`). This prefix is what triggers `_is_media_task_blocked()` recognition downstream.
  - `style` (str) — passed through in `context` (image/video only).
  - `model` (str) — image-only; picks the generation model (dall-e-3, stability-ai, etc).
  - `width` / `height` (int) — image-only; passed via context.
  - `duration` (int, enum `[4,5,6,8,10]`) — video-only, default 10 for talking video.
  - `ratio` (str, enum) — video aspect ratio; not applied to talking-video.
  - `voice` (str, enum 12 ElevenLabs voices) — audio + talking-video TTS voice.
- **Talking-video-specific params:**
  - `script` (str) — dialogue text; **required by handler** at `:1027-1028` (schema doesn't mark it required, but the handler returns `{error}` if missing).
  - `mode` (str, enum `[loop, multi_clip]`) — default `multi_clip` per handler (`:1033`). "loop = fast/cheap but visible seams; multi_clip = unique clips, 3-6x cost" per schema description.
  - `sync_mode` (str, enum `[loop, cut_off, bounce]`) — default `cut_off` per handler (`:1034`).
  - `lipsync_model` (str, enum `[auto, latentsync, sync_labs]`) — default `auto` per handler (`:1032`).
  - `color_grade` (str, enum 9 preset names) — optional post-lip-sync grade applied via DaVinci Resolve; schema description explicitly recommends surfacing this to the user for talking-video generation.
  - `image_url` (str) — legacy field for the removed `generate_talking_video` action; **unused by `create_talking_video`** (which always generates the image via ImageAgent as stage 1). Session 1222 P2 removed the caller.
- **Read-side params:**
  - `job_id` (str) — required for `job_status` (handler `:1075-1076`).
  - `limit` (int) — `list_jobs` only; capped at `min(int(limit), 50)` per media type (`:1136`). Default 10 per schema description.
- **Handler-side defaults not in schema:**
  - `voice` for talking-video defaults to `'Rachel'` (`:1030`).
  - `duration` for talking-video defaults to `10` (`:1031`).
- **Removed action (schema history):** `generate_talking_video` (existing-image entry point) was removed at Session 1222 P2 because `TalkingCharacterAgent` had zero `AgentExecution` rows all-time. `create_talking_video` (the from-prompt pipeline) is the canonical talking-video entry point.

## 4. Golden-path examples

**"Generate a photorealistic image of a golden retriever surfing."** (HYPOTHETICAL — MUTATION gated this batch)

```
# studio_tool  action=generate_image  prompt="photorealistic golden retriever surfing at sunset"  model=dall-e-3
# → {task_id: 'abc-…', mode: 'async', agent: 'ImageAgent',
#    message: 'Image generation dispatched (task abc-…). Use job_status to check progress.'}
# Downstream: ImageAgent runs on long_running queue, writes ImageHistory row on completion.
```

**"Check on that image job."**

```
# studio_tool  action=job_status  job_id="abc-…"
# → {job_id: 'abc-…', status: 'completed', success: true, agent: 'ImageAgent',
#    execution_time_ms: 14200, content: '...', image_url: '...'}  (enriched via _get_agent_execution_output)
```

**"Show me my last 10 generated media."**

```
# studio_tool  action=list_jobs  limit=10
# → {count: 10, jobs: [{id, type: 'image|video|audio', prompt, created_at}, ...]}
# Merged from ImageHistory + VideoHistory + AudioHistory, sorted by created_at desc.
```

**"Create a talking character saying my quarterly numbers."** (HYPOTHETICAL — MUTATION gated this batch)

```
# studio_tool  action=create_talking_video  prompt="professional woman in business attire"
#              script="Q3 revenue up 22 percent…"  voice="Rachel"  color_grade="cinematic_warm"
# → {task_id: 'def-…', mode: 'async', agent: 'ImageAgent → TalkingCharacterAgent', message: '…'}
# Downstream: create_talking_video_task on long_running queue runs 2-stage pipeline.
```

## 5. Failure / empty-state / pagination notes

- **Unknown action:** `return {'error': f'Unknown studio action: {action}'}` at `td_handlers_core.py:1187`. Fallthrough for anything outside the 6-enum.
- **Missing job_id on job_status:** `return {'error': 'job_id is required for job_status'}` at `:1076`. Handler bails before any ORM/Celery read.
- **CeleryTaskEvent lookup failure:** wrapped in `try/except` at `:1079-1097`; exception is logged as `swallowed ... — degraded` and handler falls through to the AsyncResult path.
- **AsyncResult lookup failure:** wrapped in `try/except` at `:1100-1131`; on any exception the handler returns `{job_id, status: 'unknown'}` at `:1133`.
- **AsyncResult state mapping** (`:1108-1128`): `SUCCESS`→`completed`, `FAILURE`→`failed`, `STARTED`→`running`, `PENDING`→`queued`; other states (`RETRY`, `REVOKED`) surface as lowercased Celery state names.
- **list_jobs per-media-type degradation:** each of the 3 history-table reads is wrapped independently (`:1138-1179`); a missing table / import error / query error in one media type silently degrades that type while the other two still return. Log emits `swallowed (%s: %s) — degraded`.
- **list_jobs sort behavior:** `created_at` field is coerced to isoformat string for comparison at `:1181`; rows without `created_at` sort as `''` (last after descending sort).
- **generate_* pattern — required prompt not validated at handler:** `raw_prompt = payload.get('prompt', '')` at `:964`, `:991`, `:1056` — empty prompt still dispatches to the agent with just the prefix (`"Generate image: "`). No handler-side pre-validation.
- **create_talking_video — required-field checks at handler:** `prompt` (`:1025-1026`) and `script` (`:1027-1028`) both return `{error}` before dispatch. This is the one generate-*-family action that pre-validates.
- **generate_talking_video** (removed): any caller sending `action='generate_talking_video'` falls through to the unknown-action branch (`:1187`). Documented in schema description as removed at Session 1222 P2.

## 5a. Mutation containment / async-fanout gate

**Four MUTATION actions (async fan-out).** Each dispatches into a Celery worker on `queue='long_running'` and returns an envelope containing `task_id` + `mode='async'`. The handler itself performs **no ORM writes**; all downstream side effects live inside the Celery task (which may write agent-execution rows, history rows, and generated media artifacts).

| Action | Task | Queue | Envelope | Side-effect surface |
|---|---|---|---|---|
| `generate_image` | `execute_agent_task(['ImageAgent', task_text, ctx])` | `long_running` | `{task_id, mode, agent='ImageAgent', message}` | Downstream: ImageAgent → generation API → ImageHistory row + AgentExecution row |
| `generate_video` | `execute_agent_task(['VideoAgent', task_text, ctx])` | `long_running` | `{task_id, mode, agent='VideoAgent', message}` | Downstream: VideoAgent → generation API → VideoHistory row + AgentExecution row |
| `generate_audio` | `execute_agent_task(['AudioAgent', task_text, ctx])` | `long_running` | `{task_id, mode, agent='AudioAgent', message}` | Downstream: AudioAgent → TTS API → AudioHistory row + AgentExecution row |
| `create_talking_video` | `create_talking_video_task([image_prompt, script, ctx])` | `long_running` | `{task_id, mode, agent='ImageAgent → TalkingCharacterAgent', message}` | Downstream: 2-stage pipeline — ImageAgent (image gen) → TalkingCharacterAgent (lipsync) → optional DaVinci color-grade → VideoHistory row |

**Containment mechanism (audit metadata):** classified per-action via `TOOL_ACTION_METADATA` this ship (see §Related). Read actions (`job_status`, `list_jobs`) are `READ_ONLY`; the 4 generate-* actions are `MUTATION`. Harness respects the classification via `skipped_mutation` for MUTATION actions.

**Containment mechanism (runtime):** none at the handler layer. Per S2914 batch 4 doc-fix PR #3458, `TOOL_ACTION_METADATA` is **descriptive audit metadata**, not a runtime enforcement gate. Live PA runtime WILL dispatch the generate-* actions and fire Celery tasks on every invocation.

**Deferral rationale for live-exercise:** each generate-* dispatch enqueues a real generation job on `long_running` (which is spend-bearing: image API + video API + TTS API cost per call). Not appropriate to burn on a doc-only sweep session. First-live-exercise deferred to a dedicated media-generation session where the artifact IS the point of the invocation.

**Boilerplate (Rigby S2916 T0 SIGN Q3 tightening rule):** _This tool's safety class per action tracks DB + Celery-dispatch side effects, not semantic intent; async-fanout behavior is documented in Appendix A._

## 5b. First-hop dependency proof (S2915 shape + Appendix A introduction)

**S2917 batch 7 introduces Appendix A (Async-Fanout)** as the sibling appendix to the S2916 Appendix N (Network-Preflight), per Rigby T0 SIGN Q2 AGREE-with-edits + Chris ratification. Row #38 (standardized-appendices Fold) promoted at this batch — 2nd adoption trigger reached (Network-Preflight batch 6 + Async-Fanout batch 7).

Verdict scheme (see `task_breakdown_tool_validation.md` §5b for legend): `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.

### Path: `generate_image` / `generate_video` / `generate_audio` (agent-task-wrapper fan-out)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `execute_agent_task.apply_async(args=[<Agent>, task_text, ctx], queue='long_running')` | dispatch (async) | `td_handlers_core.py:978-980, 1002-1004, 1063-1065` | firm — imports from `core.tasks`; queue is `long_running`; task_id captured into return envelope |
| `execute_agent_task(...)` task body (downstream, opaque at handler) | opaque | `core/tasks.py:1131` (`def execute_agent_task(...)` — verified via Rigby T0 grep) | opaque — resolves an AGENT_MAP entry by name (`ImageAgent` / `VideoAgent` / `AudioAgent`) then runs the agent's execute loop; agent-side side effects (generation API + AgentExecution row + `<Media>History` row) not enumerated this ship |

### Path: `create_talking_video` (workflow-task fan-out)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `create_talking_video_task.apply_async(args=[image_prompt, script, ctx], queue='long_running')` | dispatch (async) | `td_handlers_core.py:1039-1041` | firm — imports from `core.tasks`; distinct from `execute_agent_task` (two-stage pipeline task, not agent-wrapper) |
| `create_talking_video_task(...)` task body (downstream, opaque at handler) | opaque | `core/tasks.py` (task definition — not enumerated this ship) | opaque — two-stage pipeline: ImageAgent generates character image → TalkingCharacterAgent runs lipsync → optional DaVinci color-grade; multi-service downstream chain |

### Path: `job_status`

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `CeleryTaskEvent.objects.filter(task_id=job_id).first()` | read | `td_handlers_core.py:1080-1081` | firm — telemetry row read; wrapped in try/except; degrades to AsyncResult path on failure |
| `celery.result.AsyncResult(job_id)` | read | `td_handlers_core.py:1101-1102` | firm — Celery backend state lookup; wrapped in try/except; degrades to `{status: 'unknown'}` on failure |
| `self._get_agent_execution_output(job_id, exec_id)` | read | `td_handlers_core.py:1091, 1118` | firm — enriches with AgentExecution content/media; helper defined on the dispatcher class |

### Path: `list_jobs`

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ImageHistory.objects.order_by('-created_at')[:limit]` | read | `td_handlers_core.py:1139-1140` | firm — ORM queryset, wrapped in try/except with degrade-and-continue |
| `VideoHistory.objects.order_by('-created_at')[:limit]` | read | `td_handlers_core.py:1153-1154` | firm — same shape |
| `AudioHistory.objects.order_by('-created_at')[:limit]` | read | `td_handlers_core.py:1167-1168` | firm — same shape |

**No-hidden-cost verdict:**
- ✓ at DB layer for the 2 READ actions (`job_status` + `list_jobs` are pure reads).
- ✗ at Celery-dispatch layer for the 4 MUTATION actions (each `apply_async` enqueues a spend-bearing generation job).
- Downstream side effects (agent-side ORM writes, generation-API spend, media artifact writes) are opaque at the handler layer and enumerated in Appendix A field A4 below.

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

**Introduced at S2917 batch 7 per Rigby T0 SIGN Q2 AGREE-with-edits (Fold row #38 standardized-appendices — 2nd adoption).**

| Field | Declaration | Evidence (file:line) | Notes / constraints |
|---|---|---|---|
| **A1. Dispatch target type(s)** | `agent_task_wrapper` (3 actions: image/video/audio dispatch `execute_agent_task`, which resolves to an AGENT_MAP entry by name argument) + `workflow_task` (1 action: talking-video dispatches `create_talking_video_task`, a bespoke two-stage pipeline task). Handler SEES only the Celery task entrypoint + args; the AGENT_MAP lookup + agent execute loop are opaque at handler layer. | `td_handlers_core.py:963, 978-980` (execute_agent_task import + dispatch); `:1022, 1039-1041` (create_talking_video_task) | Handler layer does NOT know which agent will run — Rigby T0 SIGN Q4 pushback applies: fan-out presence is itself an opacity flag regardless of visible callee count. |
| **A2. Queue name(s) + priority** | Both target types dispatch to `queue='long_running'`. Priority not set by this handler. | `td_handlers_core.py:979, 1003, 1040, 1064` (all `queue='long_running'`) | Shared long-running queue (not a dedicated pool). No priority declaration → default queue priority. |
| **A3. Task_id envelope + polling contract** | (a) **Identifiers returned:** single `task_id` (Celery task UUID). No domain-object id (unlike `workflow_run_tool` which returns dual `run_id`+`task_id`). (b) **Polling endpoint:** `studio_tool.job_status` action itself is the polling surface — reads `CeleryTaskEvent` (telemetry-first) then falls through to `AsyncResult` (Celery backend). Enriches via `AgentExecution` lookup when the task result carries `execution_id`. (c) **Idempotency stance:** `none` — no dedupe key, no safe-re-run guarantee. Duplicate submissions produce duplicate generation jobs + duplicate spend. | `td_handlers_core.py:981-986, 1005-1010, 1042-1051, 1066-1071` (envelope shape); `:1073-1133` (polling); idempotency: absent by inspection | Contract asymmetry vs `workflow_run_tool`: no domain-object row is created at dispatch time. If the Celery task never emits a `CeleryTaskEvent` or `AgentExecution` row (e.g. worker crash before start), `job_status` returns `{status: 'unknown'}` — the dispatch is effectively lost from the polling surface's perspective. |
| **A4. Downstream side-effect boundary** | Fanned-out work performs: (i) generation-API calls (OpenAI / Stability / Runway / ElevenLabs / etc — spend-bearing external network), (ii) media artifact writes (image/video/audio blobs to storage), (iii) `<Media>History` ORM row creation (`ImageHistory` / `VideoHistory` / `AudioHistory` — `content/models.py`), (iv) `AgentExecution` ORM row creation for telemetry (`core/models_agent_telemetry.py` or equivalent). Talking-video adds a 2nd agent hop (ImageAgent → TalkingCharacterAgent) + optional DaVinci Resolve color-grade (external bridge). **No dispatcher re-entry observed at handler layer**; downstream agents may invoke sub-services but do not call `tool_dispatcher._handle_*` at the layer read this ship. | Handler-layer opacity: `td_handlers_core.py:978-980, 1002-1004, 1039-1041, 1063-1065`. Task-body implementations at `core/tasks.py:1131+` (`execute_agent_task`) not fully enumerated. | **Rigby Q4 broadening applied:** this pattern is opaque-side-effecting-chain via Celery fan-out (analogous to but distinct from the actionless-side-effecting-chain pattern observed at http_smoke_test S2916). See §Related. |
| **A5. Observability + cancel semantics + revisit triggers** | (a) **Observability contract:** `CeleryTaskEvent` (telemetry row created by the task's own start/complete hooks — best-effort; may be missing if the task crashes before emitting) + `AsyncResult.state` (Celery backend, authoritative for Celery-level status: PENDING/STARTED/SUCCESS/FAILURE/RETRY/REVOKED) + `AgentExecution` (authoritative for agent-level content/output when populated). Handler prefers telemetry-first, falls through to Celery-backend, enriches from AgentExecution. (b) **Cancel semantics:** **none exposed** — `studio_tool` has no `cancel` action. Once dispatched, the caller cannot revoke via this tool. (Compare `workflow_run_tool.cancel` which uses `celery_app.control.revoke(...terminate=True)`.) (c) **Revisit triggers:** — any change to `execute_agent_task` signature, AGENT_MAP entries for Image/Video/Audio/TalkingCharacter agents, the `long_running` queue routing, or introduction of a new generate-* action; also revisit if `create_talking_video_task` two-stage pipeline structure changes; also revisit if any generate-* task path starts calling back into `tool_dispatcher._handle_*` (dispatcher re-entry, per Rigby Q4 audit hotspot). | `td_handlers_core.py:1078-1133` (polling); cancel absence: no `action='cancel'` in schema enum at `pa_tool_schemas.py:1561-1565` | Cancel-absence is intentional contract surface, not an oversight — media-generation jobs are typically short (<60s) and cheap-to-cancel-late; the design chose "no cancel" over "partial-cancel semantics." |

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness studio_tool` at HEAD `d884d9c8c`:

Expected harness shape: 6 actions declared → 2 READ_ONLY dispatched live (`job_status`, `list_jobs`), 4 MUTATION reported `skipped_mutation` per per-action `TOOL_ACTION_METADATA`. `job_status` requires a real Celery `job_id`; on synthesized/missing job_id, harness output should surface `{status: 'unknown'}` (terminal branch at `:1133`) — not a failure, an intended empty-state. `list_jobs` with default `limit=10` should return `{count, jobs: [...]}` shaped envelope even for a fresh DB (count may be 0).

Artifact target: `docs/audits/pa_tools/harness_output/studio_tool.json` (produced by harness run).

### 6.2 Runtime-not-executed — this ship

- **4 MUTATION generate-* actions** — deferred per §5a rationale (each dispatch enqueues a spend-bearing generation job on `long_running`). Not exercised live this batch per D6 moratorium on new mutation-class execution during sweep + spend-lane discipline.
- **No `dry_run` fast-path** exists at the handler layer. A `dry_run` for generate-* would require the agents themselves to accept a `record: bool` flag through `execute_agent_task` context — not proposed this batch per D6 moratorium on `dry_run` infrastructure arcs.

---

## Related

- **Adjacent tools:**
  - `workflow_run_tool` (Slice 3 batch 7 async-duo sibling) — general workflow dispatcher via `run_source_pack_workflow.apply_async(queue='content')`; also introduces Appendix A this batch.
  - `intelligence_tool` (Slice 3 batch 4) — RAG/desk composite reader, no generation dispatch.
  - `research_and_create_tool` (Slice 3 batch 5) — actionless research-and-write chain, TOOL_DEFAULTS MUTATION.
  - `media_tool` (Slice 2 batch 4) — post-generation history CRUD across `ImageHistory` / `VideoHistory` / `AudioHistory`; `studio_tool` produces the rows `media_tool` deletes/reads.
  - `davinci_tool` (Slice 2 batch 4) — external DaVinci Resolve render bridge; `create_talking_video`'s optional `color_grade` param dispatches DaVinci downstream.
  - `obs_tool` (Slice 2 batch 4) — OBS recording bridge, separate concern.
- **Substrate context:** Slice 3 batch 7 async duo; introduces §5b **Appendix A (Async-Fanout)** as the sibling to S2916 batch 6's Appendix N (Network-Preflight). Row #38 (standardized-appendices Fold) 2nd adoption trigger → promoted at Slice 3 CLOSE per Rigby T0 SIGN Q4 + Chris ratification.
- **Metadata seed:** 6 `TOOL_ACTION_METADATA` entries this ship — 4 MUTATION (generate_image/video/audio + create_talking_video) + 2 READ_ONLY (job_status + list_jobs). No `TOOL_DEFAULTS` entry (MIXED composition per revenue_tracker_tool / session_tool / batch-4 precedent).
- **Session provenance:** Session 1077 (video async dispatch), 1088 (image + audio async dispatch — matches video pattern), 1222 P2 (removed `generate_talking_video` existing-image entry point after zero-execution audit).
- **Ledger candidates raised this batch (studio_tool-specific):**
  - **Contract asymmetry with `workflow_run_tool`:** studio returns single `task_id`; workflow_run returns dual `run_id` + `task_id`. Rigby's Q2 A3 edit (dual-identifier declaration) captures this. If a future PA tool wraps studio-style single-identifier dispatch + wants domain-object polling, it will hit this asymmetry. 1st instance.
  - **Cancel-absence as intentional contract:** studio has no `cancel` action; workflow_run does. If a future generate-* action needs mid-flight revoke, this design decision reverses. 1st instance.
  - **Dispatcher-re-entry audit hotspot (Rigby Q4):** watch for any downstream `execute_agent_task` agent path calling back into `tool_dispatcher._handle_*`. Not observed this ship (studio's agent-side implementations not fully enumerated); flagged for revisit if AgentMAP entries add tool-dispatch calls.
- **Related ratifications:** S2915 batch 5 (§5b first-hop dependency proof shape), S2916 batch 6 (Appendix N introduction), S2917 batch 7 (Appendix A introduction + row #38 Fold promotion).

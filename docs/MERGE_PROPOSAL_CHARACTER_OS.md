<!-- DOC-POINTER-V2 (Session 1146) -->
> **Status:** Parked backlog item
> **Deprecated:** Session 1146 (2026-05-25)
> **Authoritative parking statement:** [`docs/handoffs/CURRENT.md`](handoffs/CURRENT.md) — *"Character OS merge — parked: [`MERGE_PROPOSAL_CHARACTER_OS.md`](MERGE_PROPOSAL_CHARACTER_OS.md) (sidecar) and [`MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) (native) stay in tree as v2 backlog. **Unpark only if a paying customer asks for an avatar.**"*
> **Companion (counter-proposal):** [`docs/MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md`](MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md) — read both before deciding.
> **Preserved because:** documents the sidecar-app integration approach for the Character OS merge; useful as design history when (and if) Chris reopens the merge in response to customer demand. Do NOT execute the proposal as-written without explicit unpark signal.
> **Related canon:** [`docs/24_7_GLOBAL_AI_APP_ATLAS.md`](24_7_GLOBAL_AI_APP_ATLAS.md) — Atlas v1 explicitly defers Character OS merge to Phase 4+.

# Character OS → unified-donkey-betz: Merge Proposal

**Author:** Claude Code, Session 1116-merge-planning
**Date:** 2026-05-12
**Status:** Proposal — no code touched, decisions still open
**Source brief:** [`runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md`](../../runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md)
**Related u-d-b docs:** [`PLATFORM_WHAT_IT_IS.md`](PLATFORM_WHAT_IT_IS.md), [`PLATFORM_INVENTORY.md`](PLATFORM_INVENTORY.md)

> **Scope.** This is an architecture proposal, not a green-light. The numbers in
> here describe the *current* state of both repos as inspected on 2026-05-12;
> the recommended structure is for Chris to accept, redirect, or reject.
> Nothing was written outside of `docs/`.

---

## A. TL;DR

**Where Character OS lives in u-d-b.** As a sub-package
`core/services/spokesperson/` (services + render clients + memory adapters)
plus one new agent `core/agents/spokesperson_agent.py`, one new app
`spokesperson/` for the new Django models, and one new workspace tab
`frontend/src/pages/workspace/tabs/SpokespersonTab.tsx`. Character OS's
FastAPI surface gets re-implemented as Django REST + Channels; its React
frontend gets ported tab-by-tab into the existing workspace shell, not
embedded as an iframe.

**Three-bucket adoption matrix:**

| Bucket | Subsystems | Rationale |
|---|---|---|
| **Adopt as-is (lift module, swap I/O)** | The 10 finishing-layer ffmpeg clients (`aleph_client`, `polish_client`, `pip_client`, `backdrop_client`, `cohost_client`, `music_bed_client`, `broll_client`, `animated_pip_client`, `scene_composite_client`), the Aleph chunker, the realtime tool catalog, the loudnorm audio pipeline, the migration-script pattern | Pure-ffmpeg / pure-Runway logic with no FastAPI dependencies. Drop the modules in, swap their JSON-store calls for Django ORM. |
| **Rewrite to u-d-b patterns** | Memory subsystem (kill `JsonMemoryStore`, target `AgentMemory` + pgvector via `MemoryContextService`), the realtime broker (move under Channels + the existing PA tool dispatcher so Rigby can opt in), the campaign creation flow (operator-named "wrong" — re-design as workspace-tab actions) | u-d-b already has these patterns implemented at scale; Character OS's versions are smaller and lossier. |
| **Retire** | `cached_video_url` legacy field, the `/legacy` route, `CinematicLane`/`SpokespersonLane`/`DialogueLane` shell triplet, the `activeMode` localStorage labyrinth, the brief wizard | Already named for retirement in the merge brief. |

**Three biggest risks.**

1. **Concept drift on `Character`.** u-d-b's `Advisor` model (line 828 of
   `core/models_unified_system.py`) is a thin metadata record (32 named figures
   with `name / title / expertise / wisdom JSON`). Character OS's `Character`
   is a render-grade asset (`portrait_url / runway_avatar_id /
   voice_preset / personality / knowledge_sources`). **They are NOT the same
   thing** — collapsing them would either pollute Advisor with rendering
   plumbing or starve Spokesperson of advisor-grade context. Recommended:
   keep them separate; introduce a `Spokesperson` model that *can* link
   to an Advisor (1:0..N) for personality grounding.
2. **Render-time blocking under Celery's 512MB ceiling.** Character OS's
   atomic `scene-composite` and `add-animated-pip` routes synchronously
   poll Runway for up to 5 minutes inside FastAPI. u-d-b's `celery-long-running`
   workers run `-c 2 --max-tasks-per-child=2 --max-memory-per-child=150MB`
   — three concurrent renders + 200MB parent already pushed into OOM
   territory in Session 1063 (PR #1413). Render pipelines must become
   stage-decomposed Celery tasks, not 5-minute blocking Celery tasks.
3. **Act-Two requires human face geometry.** PR EX validated empirically that
   the Runway character_performance probe rejects anthropomorphic-mascot
   portraits. u-d-b's 32 advisors are all real humans, so Act-Two is
   genuinely the "merge thesis" capability — but the merge story is *one
   spokesperson archetype unlocks one Runway primitive*, not "every
   character gets every feature." The proposal calls this out so it doesn't
   silently get marketed as universal.

---

## B. Concept-mapping table

| Character OS concept | u-d-b mapping | Verdict |
|---|---|---|
| `Character` (subject + portrait + voice + personality + knowledge_sources) | **New `Spokesperson` model** in a new `spokesperson/` Django app. NOT the same as `Advisor`. | New model. See § D for schema. |
| `Advisor` link from a Spokesperson | `Spokesperson.advisor = ForeignKey(Advisor, null=True)` so a Spokesperson can be backed by Buffett's wisdom + Buffett's portrait OR a synthetic mascot with no Advisor. | Optional link. |
| `Campaign` (business + product + audience + tone + variants + outputs) | **New `SpokespersonCampaign` model** in the same app. NOT the same as `Initiative` (which is a 5-stage *document* lifecycle in `core/models_document_registry.py:37`, not a render unit). | New model. See § D. |
| `OutputRecord` (append-only artefact log with `kind` discriminator) | **New `SpokespersonOutput` model**, NOT a reuse of `VideoHistory` (`content/models.py:2219`). VideoHistory is per-user video gallery; SpokespersonOutput is per-campaign render lineage with `parent_output_id` chains. We sync the final-clip URL into VideoHistory for surfacing in Media tab, but the canonical render record stays in SpokespersonOutput. | New model + one-way mirror to VideoHistory. |
| `OutputKind` enum (19 values) | Django `TextChoices` on `SpokespersonOutput.kind`. Same 19 values, additive, no semantic change. | Direct port. |
| 10 finishing-layer ffmpeg services | **Direct lift** to `core/services/spokesperson/finishing/{aleph,polish,pip,backdrop,cohost,music_bed,broll,animated_pip,scene_composite}.py` | Lift, swap JSON-store I/O for Django ORM, wrap each in a Celery task. |
| `realtime_avatar_client.py` + 9-tool catalog | **`core/services/spokesperson/realtime/avatar_session.py`** + tool catalog registered alongside the existing PA tool catalog. The realtime *tools* live in PA's tool dispatcher; the *session broker* stays a separate service called from a Channels consumer. | Adapt — see § G. |
| Pluggable `MemoryStore` / `MemorySource` / `MemoryComposer` | **Replace with u-d-b primitives.** `MemoryStore` → `AgentMemory` (pgvector). `MemorySource` → adapt the existing `MemoryContextService` providers (transcripts, knowledge sources, spider feed). `MemoryComposer` → keep as a thin Markdown renderer; u-d-b doesn't have an equivalent. | Mostly retire; preserve `MemoryComposer` and the orchestrator API shape. |
| `auto_ingest` hook on transcript save | Django `post_save` signal on a new `SpokespersonTranscript` model → enqueues an `ingest_spokesperson_transcript` Celery task. | Adapt to signal pattern. |
| `JsonMemoryStore` JSON file | Retire. `AgentMemory` rows in Postgres. | Retire. |
| `character_store.py` / `campaign_store.py` (threading.Lock + `.tmp + replace` JSON writes) | Retire. Django ORM with `select_for_update` where atomicity matters. | Retire. |
| `runway_client.py` (httpx + base64 upload + polling) | **Lift as-is** to `core/services/spokesperson/runway_client.py`. Already pure-Python. The `maybe_to_data_uri` helper is recoverable for any future image-pass-through scenario. | Direct lift. |
| `scripts/migrate-cinematic-outputs.py` (backfill pattern) | **Lift the pattern**, not the script. Write a `migrate_spokesperson_outputs` Django management command for Phase 2 backfill. | Pattern reuse. |
| FastAPI router `app/routers/campaigns.py` (~50 routes) | Re-implement as Django REST + Channels under `core/api/spokesperson/`. ~30 of the routes collapse into one `outputs/` endpoint via the `OutputKind` discriminator. | Rewrite, not lift. |
| Vite frontend `CampaignWorkspace.jsx` + 8 picker modals | Port to React 18 + the existing u-d-b workspace tab pattern. Lazy-load each modal. The "ten finishing tiles" UI is the differentiator — keep it 1:1 visually. | Port, don't iframe (see § E). |
| `/api/runway/image/<id>` → `data:URI` server-side resolution | Stays in `runway_client`. u-d-b's Cloudinary `MediaCloudinaryStorage` already serves CDN URLs, but the `maybe_to_data_uri` helper still applies for Runway's "no public callback" workflow. | Lift verbatim. |
| Local-only `backend/data/{host,videos,finished,images,characters}/` JSON tree | Retire. u-d-b uses Cloudinary by default (`DEFAULT_FILE_STORAGE=MediaCloudinaryStorage`). For dev, `default_storage` falls back to local FS. | Retire local data tree. |
| Top-bar `🦙 Ollama` chip + DaVinci Resolve subprocess | u-d-b already has `resolve_node` Procfile entry + `ResolveNodeClient` (Session 1063). The Polish-in-DaVinci button maps directly. Ollama LLM (`llama3:latest`) becomes one more provider in `LLMProviderRegistry` (already 6 providers). | Direct overlap — reuse u-d-b's Resolve, register Ollama as 7th provider. |
| Mock-mode chip (`MOCK MODE` banner when no Runway key) | u-d-b doesn't have an equivalent banner. Add one to the SpokespersonTab header that mirrors `runway_provider_status`. | New, small. |

---

## C. Architecture proposal — by subsystem

### C.1 Directory layout (u-d-b side)

```
core/
├── agents/
│   └── spokesperson_agent.py            # NEW — agent-callable surface, BaseAgent subclass
├── services/
│   └── spokesperson/                    # NEW sub-package
│       ├── __init__.py
│       ├── runway_client.py             # LIFT from Character OS app/services/runway_client.py
│       ├── character_studio.py          # avatar bind / portrait regen / voice clone wrappers
│       ├── memory/                      # ADAPT — composer + orchestrator only
│       │   ├── composer.py              # LIFT — Markdown rendering
│       │   ├── orchestrator.py          # ADAPT — calls AgentMemory, not JsonMemoryStore
│       │   └── sources.py               # ADAPT — adapters for AgentMemory / spider feeds / transcripts
│       ├── realtime/
│       │   ├── avatar_session.py        # LIFT — broker
│       │   ├── transcript_client.py     # LIFT
│       │   └── tool_catalog.py          # ADAPT — 9 tools registered with PA dispatcher
│       └── finishing/                   # LIFT — the 10 finishing layers
│           ├── aleph_client.py          # + chunker
│           ├── polish_client.py
│           ├── pip_client.py
│           ├── backdrop_client.py
│           ├── cohost_client.py
│           ├── music_bed_client.py
│           ├── broll_client.py
│           ├── animated_pip_client.py
│           ├── scene_composite_client.py
│           └── kind_sets.py             # NEW — single canonical source for *_SOURCE_KINDS
core/
├── tasks_spokesperson.py                # NEW — Celery wrappers for finishing layers
└── api/
    └── spokesperson/                    # NEW — DRF + Channels endpoints
        ├── views.py
        ├── consumers.py                 # WebSocket for realtime + render-progress
        ├── serializers.py
        └── urls.py

spokesperson/                            # NEW Django app
├── apps.py
├── models.py                            # Spokesperson, SpokespersonCampaign, SpokespersonOutput, etc.
├── migrations/
└── admin.py

frontend/
└── src/pages/workspace/tabs/
    └── SpokespersonTab.tsx              # NEW — replaces Character OS frontend wholesale
        + components/spokesperson/       # ported from runway-hackathon/frontend/src/components/
```

**Why a new Django app `spokesperson/` instead of dumping models into `core/models_*`:** Character OS introduces ~6 new models with their own migration history. Isolating them into a dedicated app keeps the migration graph clean and makes it possible to feature-flag the entire subsystem off in a deployment if Runway integration is broken. Per CLAUDE.md gotchas, all models will set `app_label = 'spokesperson'` in `Meta`.

### C.2 The 10 finishing layers

Each existing client maps 1:1 to a service module under
`core/services/spokesperson/finishing/`. The signature shape stays roughly:

```python
def add_polish(
    *,
    source_video_path: str,           # local FS or default_storage path
    script: str,                      # for caption generation
    output_kind: SpokespersonOutput.Kind,
    parent_output: SpokespersonOutput,
) -> SpokespersonOutput:
    """Returns the appended output record."""
```

**Three things change vs. the FastAPI version:**

1. **Storage.** Instead of writing to `backend/data/finished/<id>.mp4`,
   write to `default_storage` so the file lives on Cloudinary in prod
   and on local FS in dev. Per the CLAUDE.md gotcha: never call
   `default_storage.path()` after upload — Cloudinary backend can't
   resolve absolute paths. Use the returned URL.
2. **Atomicity.** Wrap the polling loop in
   `transaction.atomic()` only for the final record append; do the
   ffmpeg / Runway poll outside the transaction so we don't hold a
   row lock for 5 minutes.
3. **Celery decomposition.** See § F for why the synchronous "fire +
   poll + persist" atomic-route pattern needs to be broken into
   stage tasks.

**`kind_sets.py`** is one single module whose constants are imported by
both the backend service modules and (via a `/api/spokesperson/kind-sets`
endpoint) the frontend modals. The merge brief flagged that today the
sets exist in two places that drift — consolidate before the lift.

### C.3 Realtime + memory

The realtime pipeline has two halves:

- **Session broker** (`avatar_session.py`) — issues `POST /v1/realtime_sessions`
  to Runway, holds the `sessionId` + JWT, surfaces it to the frontend over
  WebSocket. Lives in `core/services/spokesperson/realtime/`. Triggered by
  a new `SpokespersonRealtimeConsumer` under `core/api/spokesperson/consumers.py`.
- **Tool dispatch** (`tool_catalog.py`) — the 9 realtime tools become
  *first-class entries in the existing `tool_dispatcher.py`* so they
  inherit Rigby's logging / retry / governance rails. They're tagged
  `realtime_only=True` so the regular PA chat doesn't try to call them.

**Key adapter:** Character OS calls its tools over the WebRTC data channel.
u-d-b's tool dispatcher is request-response. The bridge is the
`SpokespersonRealtimeConsumer`: when Runway emits a tool invocation over
the WebRTC channel (proxied through the broker), the consumer
synthesises a normal tool-dispatch call, runs it through
`tool_dispatcher.dispatch(tool_name, payload, user_id, trace_id)`, then
echoes the result back over the data channel.

### C.4 Memory subsystem — the rewrite

Character OS's three-class abstraction
(`MemoryStore` / `MemorySource` / `MemoryComposer`) is well-designed
but solves a problem u-d-b already solved differently:

| Character OS layer | What it does | u-d-b equivalent |
|---|---|---|
| `JsonMemoryStore` | Persistence | `AgentMemory` (pgvector) — `core/models_unified_system.py` line ~3700-area |
| `MemorySource` | Pull from knowledge_sources / past transcripts / external feeds | `MemoryContextService.get_*_context` in `core/services/memory_context_service.py` + adapters |
| `MemoryComposer` | Render entries → Markdown for Runway document body | **No u-d-b equivalent.** Keep as-is. |
| `MemoryOrchestrator` | Coordinate the three | New thin coordinator over `MemoryContextService` + `MemoryComposer` |

So the merge isn't a swap, it's a **migration**: drop the JSON store,
drop the source class hierarchy, keep the composer + orchestrator as
the public API surface. Phase 3 in the merge brief assumed
"swap one class for another" — actually we replace two classes and
keep two. Worth re-validating with the operator.

The `auto_ingest` hook becomes a Django `post_save` signal on
`SpokespersonTranscript`. The signal handler enqueues
`ingest_spokesperson_transcript` to the `pa` Celery queue (small,
fast — embeddings + AgentMemory write). This matches the existing
pattern for conversation memory ingestion.

### C.5 Output serving

Character OS's unified output route `GET /api/campaigns/{id}/output/{output_id}`
collapses 19 OutputKind variants behind one URL. Port verbatim:

```
GET /api/spokesperson/campaigns/<uuid>/outputs/<uuid>/
```

Behind the scenes it dispatches on `SpokespersonOutput.kind` to either
return a Cloudinary CDN URL (prod) or stream from `default_storage` (dev).
The legacy per-format routes (`/host-video`, `/storyboard-video`, etc.)
are NOT ported — they're the same pattern Character OS already wanted
to retire.

### C.6 What gets retired during the lift

These are the brief's RETIRE table, restated as concrete deletions:

| Don't lift | Replace with |
|---|---|
| `cached_video_url` field on Campaign | Already replaced by OutputRecord — just don't add the field to `SpokespersonCampaign` |
| `/legacy` route | Don't include |
| `CinematicLane.jsx`, `SpokespersonLane.jsx`, `DialogueLane.jsx` | One unified `RenderLane.tsx` parameterised on mode |
| `activeMode` localStorage convention | Per-tile actions on the campaign tile, like the FB-FI finishing buttons |
| Brief wizard | A scaffolded "new campaign" form with the four required fields and the variant grid as the *primary* surface, not a 4-step flow |
| Concept-flow `/api/concepts` POST | Drop — operator validated the wizard UX is wrong |

---

## D. Data migration plan

### D.1 Schema mapping

```python
# spokesperson/models.py

class Spokesperson(UnifiedBaseModel):  # UnifiedBaseModel = u-d-b's UUIDField PK base
    id = UUIDField(...)                              # was Character.id (str → uuid)
    name = CharField(max_length=120)                 # was Character.name
    subject = TextField()                            # was Character.subject (visual prompt)
    personality = TextField(blank=True)              # was Character.personality
    voice_preset = CharField(max_length=64, blank=True)
    portrait_url = URLField(blank=True)
    runway_avatar_id = CharField(max_length=128, blank=True)
    runway_voice_id = CharField(max_length=128, blank=True)
    portrait_drift_from_avatar = BooleanField(default=False)  # PR EP guard

    # NEW — the bridge to u-d-b
    advisor = ForeignKey('core.Advisor', null=True, blank=True, on_delete=SET_NULL,
                         related_name='spokespersons')
    workspace = ForeignKey('core.Workspace', null=True, blank=True, on_delete=SET_NULL)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    metadata = JSONField(default=dict, blank=True)
    knowledge_sources = JSONField(default=list, blank=True)  # was Character.knowledge_sources
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = 'spokesperson'

class SpokespersonCampaign(UnifiedBaseModel):
    id = UUIDField(...)
    spokesperson = ForeignKey(Spokesperson, on_delete=CASCADE, related_name='campaigns')
    business = CharField(max_length=200)
    product = CharField(max_length=200, blank=True)
    audience = CharField(max_length=200, blank=True)
    tone = CharField(max_length=120, blank=True)

    runway_prompt = TextField(blank=True)
    commercial_script = TextField(blank=True)
    reference_image_url = URLField(blank=True)
    brand_voice_id = CharField(max_length=128, blank=True)
    brand_color = CharField(max_length=9, blank=True)         # PR AK

    realtime_document_id = CharField(max_length=128, blank=True)

    workspace = ForeignKey('core.Workspace', null=True, blank=True, on_delete=SET_NULL)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    metadata = JSONField(default=dict, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = 'spokesperson'

class AdVariant(UnifiedBaseModel):
    campaign = ForeignKey(SpokespersonCampaign, on_delete=CASCADE, related_name='variants')
    title = CharField(max_length=200, blank=True)             # PR EU LLM-titled
    script = TextField(blank=True)                            # short ad
    long_script = TextField(blank=True)                       # PR EV long ad
    order = IntegerField(default=0)
    metadata = JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'spokesperson'
        ordering = ['order']

class SpokespersonOutput(UnifiedBaseModel):
    """The append-only render record. Composability backbone."""
    class Kind(TextChoices):
        SPOKESPERSON_AD = 'spokesperson_ad', 'Spokesperson Ad'
        SPOKESPERSON_REELS = 'spokesperson_reels', 'Spokesperson Reels'
        CINEMATIC_VIDEO = 'cinematic_video', 'Cinematic Video'
        VOICED_COMMERCIAL = 'voiced_commercial', 'Voiced Commercial'
        STORYBOARD = 'storyboard', 'Storyboard'
        STORYBOARD_VOICED = 'storyboard_voiced', 'Voiced Storyboard'
        DIALOGUE_SCENE = 'dialogue_scene', 'Dialogue Scene'
        DIALOGUE_SCENE_REELS = 'dialogue_scene_reels', 'Dialogue Scene Reels'
        LONG_SPOKESPERSON_AD = 'long_spokesperson_ad', 'Long Spokesperson Ad'
        AD_RESOLVE = 'spokesperson_ad_resolve', 'Resolve-polished Ad'
        AD_DUBBED = 'spokesperson_ad_dubbed', 'Dubbed Ad'
        AD_REMIX = 'spokesperson_ad_remix', 'Remixed Ad'
        AD_POLISHED = 'spokesperson_ad_polished', 'Polished Ad'
        AD_WITH_PIP = 'spokesperson_ad_with_pip', 'Ad + PiP'
        AD_WITH_BACKDROP = 'spokesperson_ad_with_backdrop', 'Ad + Backdrop'
        AD_WITH_COHOST = 'spokesperson_ad_with_cohost', 'Ad + Co-Host'
        AD_WITH_MUSIC = 'spokesperson_ad_with_music', 'Ad + Music'
        AD_WITH_BROLL = 'spokesperson_ad_with_broll', 'Ad + B-Roll'
        AD_WITH_ANIMATED_PIP = 'spokesperson_ad_with_animated_pip', 'Ad + Animated PiP'

    id = UUIDField(...)
    campaign = ForeignKey(SpokespersonCampaign, on_delete=CASCADE, related_name='outputs')
    kind = CharField(max_length=64, choices=Kind.choices)
    video_url = URLField()
    cache_filename = CharField(max_length=255, blank=True)
    script = TextField(blank=True)
    task_id = CharField(max_length=128, blank=True)            # Runway task id
    mock_mode = BooleanField(default=False)

    parent_output = ForeignKey('self', null=True, blank=True, on_delete=SET_NULL,
                               related_name='derived_outputs')
    variant = ForeignKey(AdVariant, null=True, blank=True, on_delete=SET_NULL)

    # Discriminator-specific (sparse JSON to keep the schema flat)
    discriminator = JSONField(default=dict, blank=True)
    # holds: dub_lang, remix_style, motion_id, cast_names, line_count,
    #        chunk_count, stitched_from_output_ids

    duration_estimate = FloatField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True, db_index=True)

    # Mirror to u-d-b's existing video gallery (one-way, set on first save)
    video_history = ForeignKey('content.VideoHistory', null=True, blank=True,
                               on_delete=SET_NULL)

    class Meta:
        app_label = 'spokesperson'
        ordering = ['-created_at']
```

Two more models for the realtime + memory paths:

```python
class SpokespersonTranscript(UnifiedBaseModel):
    campaign = ForeignKey(SpokespersonCampaign, on_delete=CASCADE,
                          related_name='transcripts')
    runway_session_id = CharField(max_length=128, db_index=True)
    turns = JSONField(default=list)            # per-turn payload
    started_at = DateTimeField()
    ended_at = DateTimeField(null=True, blank=True)
    runway_status = CharField(max_length=32)   # ok / failed / empty / pending
    failure_code = CharField(max_length=64, blank=True)

class SpokespersonMemoryEntry(UnifiedBaseModel):
    """Optional thin wrapper over AgentMemory for spokesperson scope queries."""
    spokesperson = ForeignKey(Spokesperson, on_delete=CASCADE, related_name='memory_entries')
    agent_memory = ForeignKey('core.AgentMemory', on_delete=CASCADE)
    source = CharField(max_length=64)          # 'transcript' | 'knowledge' | 'spider' | 'manual'
    created_at = DateTimeField(auto_now_add=True)
```

### D.2 One-time migration script

Character OS data lives at:

- `runway-hackathon/backend/data/characters.json`
- `runway-hackathon/backend/data/campaigns.json`
- `runway-hackathon/backend/data/host/*.mp4`
- `runway-hackathon/backend/data/finished/*.mp4`
- `runway-hackathon/backend/data/videos/*.mp4`

Migration command: `python manage.py import_character_os_corpus --root <path>`.
It does:

1. Load both JSON files.
2. For each Character: create a `Spokesperson` row (system-owned user
   for now — Phase 1; assign to an actual user in Phase 2). Upload the
   portrait PNG to `default_storage`, store the URL.
3. For each Campaign: create a `SpokespersonCampaign` row. For each
   `ad_variant`: create an `AdVariant`. For each `output` in
   `outputs[]`: create a `SpokespersonOutput`, upload the cached MP4
   if present (else leave `video_url` referencing the Runway URL —
   it will 404 once expired, OK for archive).
4. Backfill `parent_output` FKs in a second pass after all rows
   exist (referencing `parent_output_id` strings).
5. Emit a `--dry-run` summary first; require `--commit` to actually write.

**Backfilling existing u-d-b advisors** with Spokesperson fields:

For each of the 32 Advisor rows, run `python manage.py
seed_advisor_spokespersons` which:

1. For each Advisor without a linked `Spokesperson`, generate a
   portrait via `gen4_image_turbo` from a prompt template like
   `"professional headshot of {advisor.name}, {advisor.title}, ..."`.
2. Bind a Runway avatar via `POST /v1/avatars`.
3. Create a `Spokesperson` row with `advisor=advisor`, copying the
   Advisor's `name` / `title` and an LLM-generated `personality`
   from the Advisor's `wisdom` JSON.
4. Skip Act-Two probe — that's an operator-driven decision per
   Spokesperson. Surface a "Test Act-Two" CTA in the workspace tab.

Cost estimate: 32 portraits × $0.05 + 32 avatar binds × $0.50 = ~$18.
Should run as a one-shot, gated behind `--commit`, with manual portrait
review per advisor for legal/likeness reasons.

### D.3 Rollback strategy

The `spokesperson` app is fully isolated — no other app FKs into it
(only the reverse: it FKs into `core.Advisor`, `core.Workspace`,
`auth.User`, `content.VideoHistory`). Rollback is:

```bash
python manage.py migrate spokesperson zero
```

Followed by removing `spokesperson` from `INSTALLED_APPS`. The
`SpokespersonOutput.video_history` FK is `SET_NULL`, so VideoHistory
rows survive. Cloudinary uploads are not deleted — accept the leak;
they're cheap.

For the Advisor backfill, store a `migrated_from = 'character_os'`
flag on each new `Spokesperson` so a `python manage.py
unseed_advisor_spokespersons --confirm` command can find and remove
them cleanly.

### D.4 What we deliberately do NOT migrate

- `cached_video_url` on Campaign — operator-flagged retire candidate.
- The 4-step brief wizard concept history (`/api/concepts` outputs
  before they became saved campaigns) — UX validated as wrong.
- Anything in `runway-hackathon/backend/data/storyboard/` /
  `dialogue/` per-shot intermediaries — they're regenerable via the
  storyboard / dialogue stitch flows.

---

## E. Frontend strategy

**Recommendation: port to u-d-b's existing React frontend as a new workspace tab.** Not iframe, not separate app.

### E.1 Why not iframe

- u-d-b is one Daphne process serving Django templates + DRF + WebSockets +
  the React SPA via the existing `frontend/` build. An embedded Vite app
  would require either a second build pipeline or shipping a bundled `dist/`
  inside u-d-b — both add deploy complexity (Procfile + Railway worker)
  for no UX gain.
- The merge brief explicitly says the campaign-creation UX needs rework.
  An iframe locks us into Character OS's existing flow forever.
- WebSocket auth (cookie-based in u-d-b, JWT in Character OS) doesn't
  cross iframe boundaries cleanly.

### E.2 Why not "shared backend, separate frontends"

- Two SPAs duplicates the auth, CSRF, theme, Tailwind config. Operator
  uses one product, not two.
- The existing workspace shell already has 5 modular tabs and 9 betting
  dashboard tabs (see `frontend/src/pages/workspace/tabs/`) — adding a
  Spokesperson tab is the pattern.

### E.3 Port plan

```
frontend/src/pages/workspace/tabs/
└── SpokespersonTab.tsx                                # NEW top-level tab
└── components/spokesperson/
    ├── SpokespersonLibrary.tsx                        # tile grid (was /)
    ├── SpokespersonWorkspace.tsx                      # per-character (was /spokespeople/:id)
    ├── CampaignWorkspace.tsx                          # per-campaign (was /spokespeople/:id/campaigns/:cid) — THE differentiator
    ├── IdentityPanelV2.tsx                            # ported
    ├── KnowledgePanel.tsx                             # ported
    ├── ConversationsHistory.tsx                       # ported
    ├── MemoryPanel.tsx                                # ported, calls u-d-b memory endpoints
    ├── RealtimeSpokesperson.tsx                       # ported (Channels WebSocket instead of WebRTC broker URL)
    ├── OutputsGallery.tsx                             # ported
    ├── modals/
    │   ├── DubLanguagePicker.tsx
    │   ├── RemixStylePicker.tsx
    │   ├── BackdropPicker.tsx
    │   ├── CohostPicker.tsx
    │   ├── MusicBedPicker.tsx
    │   ├── BrollPicker.tsx
    │   ├── AnimatedPipMotion.tsx
    │   ├── SceneComposite.tsx
    │   └── ActTwoProbe.tsx
    └── api/
        └── spokesperson.ts                            # SWR / TanStack Query hooks
```

**What we DON'T port:**

- `lanes/{Spokesperson,Cinematic,Dialogue}Lane.jsx` — the three-lane
  shell triplet. Replace with a single `RenderLane.tsx` parameterised
  on `kind: 'spokesperson' | 'cinematic' | 'dialogue'`.
- `CampaignLanes.jsx` mode-picker shell.
- `/legacy` route.
- Top-bar `🦙 Ollama` chip — it becomes one indicator inside
  the existing platform health / model selector.

**What we add net-new:**

- A `MOCK MODE` indicator chip in the SpokespersonTab header that
  reads `GET /api/spokesperson/runway-status` (mirrors Character OS's
  `/health` mock-mode signals).
- Wire the existing u-d-b workspace selector so Spokesperson is
  workspace-scoped (mirrors how every other deliverable is — see
  feedback memory `feedback_deliverable_workspace.md`).

### E.4 Migration of the brief wizard

The merge brief flagged the brief wizard as the longest-standing
legacy. Replacement design (open question for Chris):

> A campaign card grid is the home view. New-campaign affordance is a
> single primary button that opens a single-page form with four fields
> (business / product / audience / tone) plus an optional "scaffold from
> existing brief" hint. Variant grid populates immediately on save with
> two empty variant slots ready for `+ LLM Ad` or `+ LLM Long Ad`.
> No multi-step wizard. The 10 finishing-tile pattern from the
> CampaignWorkspace becomes the only creative-action affordance —
> per-tile, never per-session.

---

## F. Celery integration

### F.1 Why the existing atomic routes can't stay synchronous

Character OS's `generate-cinematic-output`, `add-animated-pip`, and
`scene-composite` routes do:

```
1. POST to Runway image_to_video
2. Poll task_id every 5s for up to 60 attempts (~5 min)
3. Download MP4
4. ffmpeg compose
5. Persist OutputRecord
6. Return composite URL
```

In u-d-b's Celery, that's a single 5-minute task pinned to
`celery-long-running` (which has `-c 2 --max-tasks-per-child=2
--max-memory-per-child=150MB`). Three concurrent atomic calls would
exceed the 512MB ceiling — the same OOM pattern Session 1063 fixed
in PR #1413. Plus the operator can't cancel mid-poll.

### F.2 Stage-decomposed task chain

Each compositor becomes a Celery `chain`:

```python
# core/tasks_spokesperson.py
@app.task(queue='content', max_retries=3)
def fire_runway_image_to_video(payload): ...

@app.task(queue='content', bind=True, max_retries=10)
def poll_runway_task(self, task_id):
    """Polls every 30s; if still PENDING, retries via countdown=30.
    Avoids holding a worker for 5 min."""
    ...

@app.task(queue='content')
def download_runway_artefact(task_id, dest_kind): ...

@app.task(queue='content')
def ffmpeg_composite(source_path, overlay_path, mode, **kwargs): ...

@app.task(queue='pa')
def append_spokesperson_output(campaign_id, kind, video_url, parent_id, ...): ...
```

The "atomic" route becomes:

```python
chain(
    fire_runway_image_to_video.s(payload),
    poll_runway_task.s(),
    download_runway_artefact.s(dest_kind='cinematic_video'),
    ffmpeg_composite.s(mode='backdrop', overlay_path=avatar_path),
    append_spokesperson_output.s(campaign_id=cid, kind=kind, parent_id=parent),
).apply_async()
```

WebSocket consumer subscribes on the chain's task group id and
streams stage-completion events to the frontend. The "atomic feel"
is preserved on the operator side (one click → one progress bar →
one final URL) without the worker holding for 5 minutes.

### F.3 Queue assignments

| Task class | Queue | Why |
|---|---|---|
| `fire_runway_*` (HTTP POST, fast) | `content` | Quick API calls |
| `poll_runway_task` (loop with countdown retries) | `content` | Workers free between polls |
| `download_runway_artefact` (network + disk) | `long_running` | I/O-heavy |
| `ffmpeg_composite` (CPU + disk) | `long_running` | CPU-heavy, fits the 150MB ceiling |
| `append_spokesperson_output` (DB write) | `pa` | Lightweight, signal-firing |
| `ingest_spokesperson_transcript` (embeddings) | `pa` | Existing pattern |
| `aleph_chunker_dispatch` (fans out N parallel renders) | `long_running` | One-shot orchestrator |
| `act_two_transcode` (ffmpeg `-preset slow -crf 18`) | `long_running` | CPU-heavy |
| `scene_composite_full_chain` (compose orchestrator) | `long_running` | Composes the chain |

### F.4 What u-d-b code-health patterns apply

The merge benefits directly from the Session 1115 refactors:

- **LearningBridge ABC.** Spokesperson outcomes feed back into
  agent learning. Add `SpokespersonOutcomeBridge(LearningBridge)`
  with the four abstract methods (extract_pattern / score / route /
  apply) so render success/failure rates feed agent decisions.
- **`verify_doc_claims` discipline.** Once Spokesperson lands,
  add three runtime claims to the verification registry: number
  of Spokespersons (claim), number of finishing-layer service
  modules (claim), Runway provider status (claim). When the merge
  PR ships, the doc-vs-reality verifier catches drift early.
- **Forward-drift guards.** `scripts/verify_repo_guardrails.py`
  should learn about the `spokesperson/` app's expected layout
  (e.g. all models must declare `app_label='spokesperson'`).

### F.5 Memory ceilings

The atomic-decomposition above means the **maximum RSS** in any
single Celery child during a render chain is ~150MB (parent baseline
~100MB) + ~50MB ffmpeg subprocess + ~80MB requests/responses for
Runway artefact download = ~280MB peak per task. Stays well under
the 512MB ceiling. Per-task RSS telemetry from Session 1066
(`CeleryTaskEvent.rss_mb_*` fields) will catch any drift.

---

## G. PA / Rigby integration

The CLAUDE.md rule is "Claude Code routes decisions through Rigby via
`python tools/pa_chat.py`." That covers the human↔Claude side. The
question here is how the **realtime avatar tools** (operator voice →
avatar invokes a tool) integrate with Rigby's tool dispatcher.

### G.1 The two surfaces are NOT the same channel

Rigby is text-channel: HTTP POST `/api/pa/chat/`, returns task_id, polls
for the result. The realtime avatar is voice/WebRTC-channel: tools fire
over the data channel, results are echoed back asynchronously via
`client_event` (which is one-way per the merge brief).

**Both channels should resolve through the same tool dispatcher.**
Recommended:

```python
# core/services/spokesperson/realtime/tool_catalog.py
SPOKESPERSON_REALTIME_TOOLS = [
    {
        "name": "render_short_ad",
        "description": "...",  # ≤1024 chars, see PR EW guard
        "handler": "core.services.tool_dispatcher.dispatch",  # same handler
        "realtime_only": True,
    },
    # ... 8 more
]
```

The `dispatch` call fans out to either the existing tool handler
(if the action exists in u-d-b) or a new handler in
`core/services/tool_dispatcher.py` that wraps the spokesperson Celery
chain.

### G.2 New PA tools (extending studio_tool)

`pa_tool_schemas.py` already has `studio_tool` with actions including
`generate_talking_video` (which routes to `talking_character_agent`).
Add 10 finishing-layer actions to `studio_tool`:

```python
{
    "name": "studio_tool",
    "actions": [
        # existing
        "generate_talking_video", "list_videos", ...
        # new
        "polish_spokesperson_ad",
        "dub_spokesperson_ad",
        "remix_spokesperson_ad",
        "add_pip", "add_backdrop", "add_cohost",
        "add_music", "add_broll", "add_animated_pip",
        "scene_composite",
    ],
}
```

So Rigby can reply to *"polish that talking-head video Buffett did
yesterday"* by calling `studio_tool(action='polish_spokesperson_ad',
output_id=...)` directly.

Tool description budget: per PR EW, every realtime tool description
≤1024 chars. The defensive truncation in `_wire_tool_entries` is
load-bearing — port it to u-d-b's tool dispatcher's realtime path.

### G.3 Where Rigby learns about Spokespersons

Add `spokesperson_tool` as a new gateway tool (parallel to
`profile_tool`, `media_tool`, `davinci_tool` from Session 1063):

```python
{
    "name": "spokesperson_tool",
    "actions": [
        "list",                 # all spokespersons in workspace
        "detail",               # one spokesperson + recent campaigns
        "create_campaign",      # new campaign for spokesperson
        "list_campaigns",       # campaigns for spokesperson
        "campaign_detail",      # campaign + outputs
        "open_realtime_session",  # voice command for Rigby to open a session
        "outputs",              # list outputs for spokesperson or campaign
        "stats",                # render counts / Runway credit usage
    ],
}
```

This is the "Rigby knows about Spokespersons" surface — when the
operator says *"what does Buffett's brand voice sound like in
Spanish?"*, Rigby can find the cached Spanish dub in
`Spokesperson.advisor=Buffett` → recent `SpokespersonOutput` with
`kind=AD_DUBBED` and `discriminator.dub_lang='es'`.

### G.4 Rigby workspace ownership

Per memory `feedback_deliverable_workspace.md`, every deliverable
is workspace-scoped. Spokesperson + SpokespersonCampaign + SpokespersonOutput
all carry the optional `workspace` FK, defaulting to the user's
default workspace (Donkey Betz). The realtime session belongs to
the campaign which belongs to a workspace — Rigby's workspace-mode
queries see only spokespersons in scope.

---

## H. Migration phases

### Phase 1 — Lift-and-shift (1-2 weeks)

**Goal:** Character OS lives inside u-d-b as an isolated subsystem,
indistinguishable in behaviour from the standalone version.

- New `spokesperson/` Django app + migrations 0001..0005
- Lift the 10 finishing service modules + `runway_client` + `realtime_client`
  + memory composer to `core/services/spokesperson/`
- New `core/agents/spokesperson_agent.py` registered in `AGENT_MAP`
- New `core/api/spokesperson/` DRF + Channels endpoints
- New `core/tasks_spokesperson.py` with stage-decomposed Celery chains
- Port `SpokespersonTab.tsx` + components (1:1 visual fidelity, just
  re-routed API calls)
- One-time `import_character_os_corpus` management command
- Add `spokesperson_tool` to PA dispatcher (read-only first: list /
  detail / outputs / stats)
- Inventory verifier + handoff updated

**Independently shippable:** yes. Behind a feature flag
`SPOKESPERSON_ENABLED` defaulting to False; tab hidden when off.

**Out of scope for Phase 1:** Advisor backfill, brief-wizard rewrite,
realtime tool decomposition into Rigby's dispatcher (still bound to
Channels consumer only).

### Phase 2 — Advisor integration (1 week)

**Goal:** the 32 advisors become Spokespersons.

- `seed_advisor_spokespersons` management command (gated, $18 cost)
- Add `advisor` FK from `Spokesperson` to `Advisor` (Phase 1 wired the
  schema; Phase 2 backfills)
- Personality-from-wisdom auto-generation (one LLM call per advisor)
- "Test Act-Two" CTA on each advisor's spokesperson tab — surfaces
  the human-portrait constraint cleanly
- Add `studio_tool` finishing-layer actions (write-side) for Rigby
- Workspace assignment: each advisor's spokesperson lands in the
  Donkey Betz workspace by default

**Independently shippable:** yes, after Phase 1.

### Phase 3 — Memory unification (1 week)

**Goal:** retire `JsonMemoryStore`, route all spokesperson memory
through `AgentMemory`.

- Implement `SpokespersonMemoryEntry` + `MemoryOrchestrator` over
  `MemoryContextService`
- Migrate any imported memory entries from Phase 1 backfill
- Wire the `auto_ingest` post_save signal on `SpokespersonTranscript`
- Add the 9 realtime tools to `tool_dispatcher` (write-side); the
  `SpokespersonRealtimeConsumer` calls them
- Spider feeds: wire `SpiderData` events into a `MemorySource` adapter
  so financial spiders feed Buffett's spokesperson memory automatically

**Independently shippable:** yes — but depends on Phase 1.

### Phase 4 — UX rewrite (1-2 weeks)

**Goal:** replace the brief wizard, retire mode-picker, kill
`cached_video_url`.

- Drop the `RenderLane.tsx` unified component, retire the three lane
  shells
- Single-page new-campaign form
- Per-tile creative actions, no `activeMode` localStorage
- Remove `cached_video_url` field via Django migration; backfill any
  remaining rows into `SpokespersonOutput.kind=CINEMATIC_VIDEO` first
- Drop `/legacy` route

**Independently shippable:** yes, but only after operator validates
Phase 1 UX.

### Phase 5 — Deprecation of standalone repo (post-merge)

**Goal:** `runway-hackathon/` becomes a read-only archive.

- Final `import_character_os_corpus` re-run (delta migration)
- Tag `runway-hackathon` `v-final-pre-merge` and archive
- Update u-d-b INVENTORY claims: `Spokespersons: N`, `Campaigns: M`,
  `Outputs: K`
- Run `verify_doc_claims --only-drift` to confirm no regressions

**Independently shippable:** yes.

---

## I. Open questions for the operator

These are the things this Claude can't decide unilaterally. Surface
to Chris via Rigby per CLAUDE.md, batched as one PA chat message.

### I.1 Brand identity — sub-product or absorbed feature?

> Should Character OS retain a brand inside u-d-b ("the Spokesperson
> Studio" with its own identity / marketing surface) or fully absorb
> as just "spokesperson features" with no separate brand?
>
> Tradeoff: sub-product preserves the hackathon-validated UX cohesion
> + standalone marketing story. Full absorption simplifies the
> workspace and aligns with the "campaign is the unit of work" pivot.
>
> Recommendation: full absorption. The 10 finishing-tile UX is the
> compelling part — it should be visible everywhere campaigns are
> visible, not gated behind a sub-brand.

### I.2 Advisor ↔ Spokesperson coupling

> One Advisor → one Spokesperson, or one Advisor → many Spokespersons?
>
> e.g. Buffett-Advisor could have a "Buffett-Founder Spokesperson" (suit,
> office, gravitas) AND a "Buffett-Casual Spokesperson" (open collar,
> coffee shop, conversational) — both backed by the same wisdom JSON.
>
> Recommendation: one-to-many (`Advisor.spokespersons` reverse manager).
> Cheap to support, opens the "same advisor in different visual contexts"
> creative space. Default is 1:1 in seeding.

### I.3 Should the 10 finishing layers stay 10, or reorganise?

> The brief preserves them as 10 discrete tiles. u-d-b's content pipeline
> (`docs/topics/content-pipeline.md`) has a more compositional model
> (ClaimsPack → Deliberation → Reviewers → PublishGate). Should the
> finishing tiles eventually expose themselves as a configurable
> creative pipeline (operator drags Polish → Backdrop → Music into
> a saved recipe), or stay as discrete one-click actions?
>
> Recommendation: keep them discrete in Phases 1-4. Only consider a
> pipeline-builder UI in Phase 5+ once we see how operators stack them.

### I.4 Runway API cost ownership

> Renders cost real money — Aleph chunker can hit 10+ credits on a
> single "Remix Long Ad" call. u-d-b has no per-user / per-workspace
> Runway-credit budget primitive today.
>
> Question: do we add `RunwayCreditEvent` tracking now (Phase 1) and
> gate renders with budget checks, or defer to Phase 5+?
>
> Note: per memory `project_current_state_2026_04`, Chris is out of
> OpenAI credits and money to replenish. Adding a render-credit-spend
> surface NOW (gated behind a per-workspace budget config) would
> prevent the same exhaustion pattern with Runway.

### I.5 Standalone repo — keep alive or freeze?

> Phase 5 says archive `runway-hackathon/`. Do we:
>
> (a) Freeze immediately after Phase 1 lift, accept any new Character
>     OS work happens directly in u-d-b
> (b) Keep both alive in parallel through Phase 4, with the brief's
>     "what's safe to keep building" rules as the divergence guardrail
> (c) Stop work on Character OS as soon as Phase 1 ships
>
> Recommendation: (a). Single source of truth from day 1 of the merge.
> The brief's "safe to keep building" list is friendly to a freeze
> because it's all additive subsystems that don't touch the
> creation-flow rewrite.

### I.6 Rigby's involvement in render decisions

> Should Rigby be allowed to *autonomously* fire Runway renders (via
> `studio_tool` write-actions) when the operator says *"make a
> spokesperson ad about X"*, or should every render require explicit
> operator confirmation in the chat?
>
> Cost angle: ad render = $1-3 in Runway credits. Without confirmation
> Rigby could spend $50/day chatting.
>
> Recommendation: render write-actions require operator confirmation
> in the PA chat (existing pattern for Rigby tool execution). Rigby
> can *propose* renders freely; only confirmation fires `apply_async`.

---

## Appendix: read order for the next session

If Chris approves this proposal in part or in whole, the next session
should read in this order before starting Phase 1:

1. This doc
2. `runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md` (sections C, D, the
   patterns table)
3. `core/services/tool_dispatcher.py` (to know where the realtime tools land)
4. `core/agents/talking_character_agent.py` (to model the
   Spokesperson agent shell on it)
5. `content/models.py:2219` (`VideoHistory`) to understand the mirror target
6. `core/models_unified_system.py:828` (`Advisor`) to confirm the
   FK target schema is what's expected
7. `core/celery.py` + `Procfile` for queue placement
8. `core/services/memory_context_service.py` for the memory adapter
   surface

---

**End of proposal.** No code touched. Awaiting operator decision via
Rigby on § I.

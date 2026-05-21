# Character OS → u-d-b: Native Integration Counter-Proposal

**Author:** Claude Code, Session 1116-merge-planning (counter-proposal)
**Date:** 2026-05-12
**Status:** Counter-proposal to [`MERGE_PROPOSAL_CHARACTER_OS.md`](MERGE_PROPOSAL_CHARACTER_OS.md) — read both before deciding
**Source brief:** [`runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md`](../../runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md)

> **Why a counter-proposal exists.** The first proposal took the safe
> path: a sidecar Spokesperson app with its own models, tab, and API.
> When the operator asked *"now that you've seen Character OS, what's
> the best way to actually implement this?"* — the honest answer was
> different. This doc is that answer.

---

## A. TL;DR

**Recommendation: native integration.** No `spokesperson/` Django app. No
new top-level tab. No `Spokesperson` model. Instead:

1. **The Advisor model gains 6 fields.** Portrait, Runway avatar id,
   voice preset, voice id, personality cue, drift flag. The Advisor
   *is* the Character. There is no second model.
2. **The 10 finishing layers become general-purpose `VideoHistory` ops.**
   Lifted to `core/services/video_finishing/`. They operate on **any**
   video u-d-b has ever produced, not just spokesperson ads. Massive
   leverage from one lift.
3. **A new `SpokespersonAgent` is one `BaseAgent` subclass.** It takes
   `(advisor, script) → VideoHistory row`. Plugs into the existing
   `ContentWriterAgent → EditorAgent → SpokespersonAgent` chain.
4. **The realtime avatar fires Rigby's tools.** Same `tool_dispatcher`,
   same 166 handlers. Operator can voice-control the entire platform
   through any advisor.
5. **Initiative deliverables gain a video kind.** Stage 5 (PublishGate)
   can now ship a video deliverable. The distribution agent already
   publishes — it just publishes video too.

**Five slices, each independently shippable.** Total estimated effort:
6-8 weeks. First slice ships in 1-2 days and immediately benefits every
existing surface that touches Advisor.

**Tradeoff vs. the sidecar proposal.**

| | Sidecar proposal | Native (this doc) |
|---|---|---|
| Risk | Low — isolated app, trivial rollback | Higher — modifies Advisor schema, Initiative deliverables |
| New code | ~6 new models, new Django app, new tab, new API namespace | 6 fields on Advisor, no new app, no new tab |
| Velocity long-term | Slower (two systems coexisting) | Faster (one system) |
| Spider → advisor memory | Phase 3+ | Slice 1 enables it natively |
| First visible win | Phase 1 (~2 weeks) | Slice 1 (~2 days) |
| Rollback if you change your mind | Trivial | Painful (schema migration) |

**Choose this proposal if:** you want Character OS's primitives to be
universally available across the platform's existing agents, content
pipeline, and Rigby — not gated behind a sub-product.

**Choose the sidecar proposal if:** you want the option to feature-flag
Character OS off in production, or you anticipate the spokesperson
work pausing and don't want it polluting the Advisor model long-term.

---

## B. Why "sidecar" is overengineered for u-d-b's reality

The sidecar proposal reasoned by analogy with Character OS's own structure
(`Character` → new `Spokesperson` model). Three things make that wrong here:

### B.1 u-d-b already has the agent shell

`core/agents/talking_character_agent.py` already exists. It's a
`BaseAgent` subclass that pipelines TTS (ElevenLabs) → image-to-video
(Runway) → lip-sync (Replicate). It's registered in
`core/agent_router.py:284` and dispatched via `studio_tool` action
`generate_talking_video` (`core/services/pa_tool_schemas.py:913`).

We're not building from zero. The Character OS realtime agent → Rigby
tool surface is already partially scaffolded. The merge fills it in
rather than parallel-creating a sibling agent.

### B.2 u-d-b has 30 advisors who are real humans

Character OS has 3 mascots (Miles=sloth, Riggs=raccoon, Donny=donkey).
PR EX in the brief proved Act-Two requires human face geometry —
*every* mascot fails the Runway face detector.

u-d-b's 30 advisors are Buffett, Wood, Dalio, Altman, Musk,
Vaynerchuk, MrBeast, Voss, Beane, Voulgaris + 20 specialists — every
one a human. **Every one is an Act-Two candidate the moment they have
a portrait bound.** The merge thesis is "Character OS's primitives unlock
when you have human spokespersons" — and u-d-b *only* has human
spokespersons. There's no value in keeping a separate `Spokesperson`
model that wraps `Advisor`. The Advisor IS the spokesperson.

### B.3 u-d-b has VideoHistory + the spider network already

The sidecar proposal recommended creating `SpokespersonOutput` as a new
model with a one-way mirror to `VideoHistory`. That's two sources of
truth for the same thing. **VideoHistory is already the canonical video
record in u-d-b** (`content/models.py:2219`). Just use it.

The 80 spiders feed `SpiderData`. The `MemoryContextService` already
ingests from spider feeds. If Buffett's portrait + voice + memory all
live on the Advisor row, then a financial spider's market data feeds
straight into Buffett's AgentMemory through the existing pipeline —
no adapter, no new MemorySource hierarchy.

---

## C. Schema changes — small, additive

### C.1 Advisor fields

```python
# core/models_unified_system.py — extend existing Advisor at line 828

class Advisor(models.Model):
    # ... existing fields (name, title, expertise, category, wisdom, etc.) ...

    # NEW — spokesperson rendering fields (Slice 1)
    portrait_url = models.URLField(blank=True)
    runway_avatar_id = models.CharField(max_length=128, blank=True)
    runway_voice_id = models.CharField(max_length=128, blank=True)
    voice_preset = models.CharField(max_length=64, blank=True)
    personality_cue = models.TextField(
        blank=True,
        help_text='Late-injected into realtime system prompt — heaviest weight signal',
    )
    portrait_drift_from_avatar = models.BooleanField(
        default=False,
        help_text='True when portrait regenerates after avatar bind — needs rebuild',
    )

    # NEW — Slice 4
    realtime_session_count = models.IntegerField(default=0)
    last_realtime_session_at = models.DateTimeField(null=True, blank=True)
```

One migration. No new model. Reverse-rollback is `migrate core <prev>`
+ removing the field declarations — painful but bounded.

### C.2 VideoHistory fields

```python
# content/models.py — extend existing VideoHistory at line 2219

class VideoHistory(UnifiedBaseModel):
    # ... existing fields ...

    # NEW — Slice 2
    advisor = models.ForeignKey(
        'core.Advisor', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='spokesperson_videos',
    )
    initiative = models.ForeignKey(
        'core.Initiative', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='spokesperson_videos',
    )
    spokesperson_kind = models.CharField(
        max_length=64, blank=True, db_index=True,
        help_text='spokesperson_ad / dialogue_scene / cinematic_video / etc.',
    )
    parent_video = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='derived_videos',
    )
    finishing_chain = models.JSONField(
        default=list, blank=True,
        help_text='Ordered list of finishing layers applied: ["polish", "backdrop", "music"]',
    )
    runway_task_id = models.CharField(max_length=128, blank=True)
    runway_metadata = models.JSONField(default=dict, blank=True)
```

The `parent_video` self-FK is the composability backbone (sidecar
proposal called this `parent_output_id` on a separate model — same
pattern, native field). The `finishing_chain` JSON makes "what's been
done to this video" a one-query answer.

### C.3 No new model, but two new lightweight tables

```python
# core/models_unified_system.py — new models, same file as Advisor

class AdvisorScript(models.Model):
    """A reusable script for an advisor — replaces Character OS's AdVariant."""
    id = UUIDField(...)
    advisor = ForeignKey(Advisor, on_delete=CASCADE, related_name='scripts')
    initiative = ForeignKey('Initiative', null=True, blank=True, on_delete=SET_NULL)
    title = CharField(max_length=200)
    short_script = TextField(blank=True)
    long_script = TextField(blank=True)
    metadata = JSONField(default=dict, blank=True)
    created_by = CharField(max_length=100, default='system')  # 'rigby' / 'editor_agent' / etc.
    created_at = DateTimeField(auto_now_add=True)


class AdvisorRealtimeSession(models.Model):
    """A single realtime session with an advisor — for transcripts + memory."""
    id = UUIDField(...)
    advisor = ForeignKey(Advisor, on_delete=CASCADE, related_name='realtime_sessions')
    initiative = ForeignKey('Initiative', null=True, blank=True, on_delete=SET_NULL)
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    runway_session_id = CharField(max_length=128, db_index=True)
    runway_status = CharField(max_length=32)  # ok / failed / empty / pending
    failure_code = CharField(max_length=64, blank=True)
    started_at = DateTimeField()
    ended_at = DateTimeField(null=True, blank=True)
    turns = JSONField(default=list)
    workspace = ForeignKey('Workspace', null=True, blank=True, on_delete=SET_NULL)
```

Two new models for sessions + scripts; both attach to existing Advisor.
No `Campaign` model — Character OS's campaign concept maps to **Initiative**
in u-d-b (already 5-stage document lifecycle), and `AdvisorScript` is the
variant primitive that hangs off either an Advisor or an Initiative.

**Total schema delta:** 6 fields on Advisor, ~7 fields on VideoHistory,
2 new lightweight models. Vs. the sidecar proposal's 6 new models in
a new app.

---

## D. Slice plan — 5 independently shippable PRs

### Slice 1 — Advisor gets a face (1-2 days)

**Scope:**
- Add 6 fields to `Advisor` (one migration)
- Lift `runway_client.py` from `runway-hackathon/backend/app/services/`
  to `core/services/runway_client.py`
- Lift `character_studio_client.py` patterns into
  `core/services/advisor_avatar_service.py` (portrait gen + avatar bind +
  voice clone + drift detection)
- New `seed_advisor_avatars` management command (`--commit` gated, ~$18
  in Runway calls — 30 portrait + avatar binds)
- Frontend: AdvisorsPage gets an Avatar panel per advisor with
  "Generate Portrait" / "Bind Avatar" / "Test Act-Two" CTAs

**Immediate wins:**
- Boardroom (`/api/boardroom/...`) can now show advisor portraits
- Strategic Memory + Decision Records gain visual identity per source
- The "Test Act-Two" CTA validates the merge thesis with one click

**Does NOT include:** Spokesperson agent, finishing layers, realtime sessions.

### Slice 2 — SpokespersonAgent + studio_tool render action (1 week)

**Scope:**
- New `core/agents/spokesperson_agent.py` — `BaseAgent` subclass
  ```python
  class SpokespersonAgent(BaseAgent):
      """Renders an advisor delivering a script as a talking-head video."""
      name = 'SpokespersonAgent'
      tools = [{
          'function': {
              'name': 'render_spokesperson_ad',
              'parameters': {
                  'advisor_id': 'string',
                  'script': 'string',
                  'mode': 'short | long',
                  'initiative_id': 'string (optional)',
              },
          },
      }]
  ```
- Register in `AGENT_MAP` (`core/agent_router.py`)
- New Celery task `core/tasks_spokesperson.py::render_spokesperson_ad`
  on `long_running` queue, decomposed into stage-chain (see § F)
- Output goes to `VideoHistory` with `advisor=...`, `spokesperson_kind='spokesperson_ad'`
- Extend `studio_tool` (in `pa_tool_schemas.py`) with new actions:
  - `render_spokesperson_ad` — the headline
  - `list_spokesperson_videos` — by advisor / by initiative / by kind
- WORKSPACE_AWARE_AGENTS gets `SpokespersonAgent` added (epa_handlers_tools.py)

**Rigby use case unlocked:**
> *"Rigby, render Buffett explaining today's S&P 500 movement as a 30-second ad."*
>
> Rigby calls: `studio_tool(action='render_spokesperson_ad',
> advisor='warren_buffett', script=<auto-written by ContentWriterAgent
> from spider data>, mode='short')`. Returns VideoHistory id + URL when
> done.

### Slice 3 — 10 finishing layers as general-purpose video ops (1-2 weeks)

**This is the leverage slice.** The 10 finishing layers in Character OS
operate on `OutputRecord` (per-campaign). In u-d-b, lift them to operate
on **any VideoHistory row**.

**Scope:**
- New `core/services/video_finishing/` sub-package
  - `aleph.py` (Aleph remix + chunker — pattern from PR FA-2)
  - `polish.py` (captions + lower-third + cards)
  - `pip.py`
  - `backdrop.py`
  - `cohost.py`
  - `music_bed.py` (loudnorm pipeline preserved per PR FF)
  - `broll.py`
  - `animated_pip.py`
  - `scene_composite.py`
  - `dub.py` (29-language voice_dubbing)
  - `kind_sets.py` (single source of truth for source/foreground kinds)
- One Celery task per layer on `long_running` queue
- New `studio_tool` actions:
  - `polish_video(video_id)` → returns new VideoHistory row
  - `add_backdrop(video_id, backdrop_video_id)`
  - `add_music(video_id, music_bed_id)`
  - `add_pip(video_id, image_url)`
  - `add_cohost(video_id, cohost_video_id)`
  - `add_broll(video_id, broll_video_id)`
  - `add_animated_pip(video_id, source_image_url, motion_id)`
  - `scene_composite(video_id, scene_prompt, motion_id)`
  - `dub_video(video_id, target_language)`
  - `remix_video(video_id, style_preset)`
- Each writes a new VideoHistory row with `parent_video=<source>`,
  appends the layer name to `finishing_chain`
- Frontend: Media tab gains a "Finish" action menu on every video tile
  (mirrors Character OS's CampaignWorkspace tile menu — 10 buttons)

**Critical reframe:** these are no longer spokesperson-specific. Any
video in u-d-b — `talking_character_agent` outputs, ContentWriterAgent
clips, Initiative deliverables — gets the 10 finishing buttons. **Hundreds
of existing videos inherit them overnight.**

**Why this is the killer slice:** the value is decoupled from the
spokesperson concept. Even if Slice 4 (realtime) and Slice 5 (Initiative)
never ship, Slices 1-3 alone justify the merge.

### Slice 4 — Realtime avatar sessions (2 weeks)

**Scope:**
- Lift `realtime_avatar_client.py` to `core/services/runway_realtime_client.py`
- New Channels consumer `core/consumers/advisor_realtime_consumer.py`
- New `AdvisorRealtimeSession` model gets per-session lifecycle
- **Tool dispatch goes through `tool_dispatcher.py`** — same 166 handlers
  Rigby uses, with a new `realtime_only=True` tag on the realtime tool
  catalog entries
- Port the 9 Character OS realtime tools to `tool_dispatcher` entries:
  - `render_short_ad` → wraps SpokespersonAgent
  - `render_long_ad` → wraps SpokespersonAgent (long mode)
  - `recall_recent_conversations` → wraps strategic_memory_service
  - `attach_memory_to_campaign` → adapt to `attach_memory_to_initiative`
  - `recall_knowledge` → wraps memory_context_service
  - `handoff_to_advisor` → opens a new realtime session with another advisor
  - `navigate_ui` → frontend echo
  - + 2 more
- Port the PR EW defensive truncation guard (`_wire_tool_entries`) — every
  realtime tool description ≤1024 chars. **This guard is load-bearing —
  do not lose it in the lift.**
- Frontend: AdvisorsPage gets a "Talk to <advisor>" CTA per advisor
- New URL: `/advisors/<id>/talk` opens the realtime session inline

**Magic unlock:**
> The operator can talk to Buffett. Buffett can call any of u-d-b's 166
> tools (gated by `realtime_only` whitelist). When Buffett wants to
> "look up that initiative we discussed last week," he calls the same
> `initiative_tool` Rigby calls. **Every advisor becomes a voice-driven
> Rigby with a face.**

### Slice 5 — Initiative deliverables get a video kind (1 week)

**Scope:**
- Extend `Deliverable.publish_intent` enum (Session 1095) with a
  `video` discriminator on `Deliverable.content_type` or similar
- Extend Stage 5 PublishGate to accept video deliverables
- Wire `Initiative → SpokespersonAgent`: a new initiative action
  "Render as Spokesperson Ad" picks the right advisor (or asks)
  and triggers the render chain
- Distribution agent already publishes — extend it with video
  publication targets (YouTube Shorts, Instagram Reels, TikTok)
- Frontend: InitiativesTab gets a "Render as ad" button per stage-5
  initiative

**Full pipeline operational:**
> Spider sees S&P move → Initiative auto-created (TRIAGE) → operator
> approves → ContentWriterAgent writes ad script → SpokespersonAgent
> renders Buffett delivering it → finishing chain (polish + music) →
> PublishGate review → DistributionAgent posts to YouTube Shorts.
>
> **End-to-end, automatic, with a human face.**

---

## E. Frontend — extend, don't add a tab

### E.1 No SpokespersonTab.tsx

The sidecar proposal added a top-level workspace tab. This proposal
**does not.** Reasoning: spokesperson features should appear *inside*
the surfaces they enhance, not in a parallel tab.

| Existing surface | What it gains |
|---|---|
| `AdvisorsPage.tsx` | Avatar panel per advisor (Slice 1), "Talk to" CTA (Slice 4), realtime session history |
| `MediaPage.tsx` / Media tab | "Finish" action menu on every video tile (Slice 3) — 10 buttons |
| `InitiativesTab.tsx` | "Render as ad" button per stage-5 initiative (Slice 5) |
| `CommandCenterPage.tsx` (Rigby) | Realtime session is one of Rigby's tool outputs — opens inline |
| `BoardroomPage.tsx` | Advisor portraits visible per consultation |

**One new component lifted from Character OS:**
`frontend/src/components/spokesperson/CampaignWorkspace.tsx` becomes
**`frontend/src/components/advisor/AdvisorVideoStudio.tsx`** — opens
inline when you click "Render an ad with Buffett" from any surface.
The 10 finishing tile menu lives here. Operator-validated UX preserved
1:1.

### E.2 Modals lifted as-is

The 8 picker modals (Dub / Remix / Backdrop / Cohost / Music / Broll /
Animated PiP / Scene) become standalone reusable components under
`frontend/src/components/video_finishing/`. They're invocable from
**any** "Finish" action menu, not just spokesperson video.

### E.3 What we DON'T port

- The brief wizard (operator validated wrong, see § H of merge brief)
- `CampaignLanes.jsx` mode-picker shell
- `CinematicLane / SpokespersonLane / DialogueLane` triplet
- `IdentityPanelV2.jsx` — replaced by Advisor avatar panel directly on
  `AdvisorsPage.tsx`
- `/legacy` route

---

## F. Celery — same stage-decomposition as sidecar proposal

The atomic-decomposition reasoning from the sidecar proposal § F applies
here unchanged. Render chains exceed 5 minutes and would OOM
`celery-long-running` if kept as a single task.

```python
# core/tasks_spokesperson.py
@app.task(queue='content', max_retries=3)
def fire_runway_render(payload): ...

@app.task(queue='content', bind=True)
def poll_runway_task(self, task_id):
    """Polls every 30s; if still PENDING, retries via countdown=30."""

@app.task(queue='long_running')
def download_runway_artefact(task_id, dest_kind): ...

@app.task(queue='long_running')
def ffmpeg_finishing_op(source_video_id, op_name, **kwargs): ...

@app.task(queue='pa')
def append_video_history(video_id, **fields): ...
```

A "render Buffett delivering this script with polish + music" call becomes:

```python
chain(
    fire_runway_render.s({'advisor': advisor_id, 'script': script}),
    poll_runway_task.s(),
    download_runway_artefact.s(dest_kind='spokesperson_ad'),
    append_video_history.s(advisor_id=advisor_id, kind='spokesperson_ad'),
    ffmpeg_finishing_op.s(op_name='polish'),
    ffmpeg_finishing_op.s(op_name='add_music', music_bed_id=bed_id),
).apply_async()
```

WebSocket consumer streams stage events → frontend shows progress.

**Per-task RSS budget per Session 1066:** parent ~100MB + ffmpeg subprocess
~50MB + Runway artefact download ~80MB = ~280MB peak. Stays under 512MB.

---

## G. PA / Rigby — extend `studio_tool`, no new gateway

### G.1 studio_tool action additions

Per `pa_tool_schemas.py:1152`, `studio_tool` already exists with 20+
actions including `generate_talking_video`. Add (Slices 2-5):

```
# Slice 2
render_spokesperson_ad
list_spokesperson_videos

# Slice 3 (general video ops, not spokesperson-specific)
polish_video
add_pip
add_backdrop
add_cohost
add_music
add_broll
add_animated_pip
scene_composite
dub_video
remix_video

# Slice 4
open_realtime_session    # opens session, returns connection params for frontend
list_realtime_sessions
get_realtime_transcript

# Slice 5
render_initiative_as_ad   # convenience composer
```

That's it for new tools. No `spokesperson_tool` gateway. The render-an-ad
verbs are at the same level as `generate_image` / `generate_talking_video`
because spokesperson-ad-rendering is just one more video op.

### G.2 Realtime tools fire through tool_dispatcher

Critical architectural choice: **the 9 realtime avatar tools route through
the same `tool_dispatcher.py:dispatch()` Rigby uses.** They get tagged
`realtime_only=True` so the regular PA chat catalog filters them out, but
the dispatch path is shared.

This means an advisor in a realtime session has access to Rigby's brain.
Buffett calls `initiative_tool(action='detail', initiative_id=...)` over
WebRTC; the data channel routes the call into `tool_dispatcher.dispatch`;
the result echoes back. **Same governance, same logging, same retry, same
workspace scoping.**

### G.3 Editor → Spokesperson autocompose

A natural follow-on (post-Slice 5): when `EditorAgent` finishes a blog
post, it can optionally trigger `SpokespersonAgent` to render a
"Buffett summarizes this post in 30 seconds" video. The text deliverable
ships with a video companion. PublishGate gates both.

---

## H. Risk + rollback

### H.1 The 3 real risks

1. **Advisor schema migration is a one-way door.** Once those 6 fields
   land and 30 advisors have portraits + avatar IDs, removing them later
   means orphaning the renders in `VideoHistory.advisor`. Mitigation:
   feature-flag `ADVISOR_AVATAR_ENABLED` initially; only run
   `seed_advisor_avatars --commit` once the operator green-lights.
2. **Runway credit cost grows without per-workspace budgets.** Per
   memory `project_current_state_2026_04`, Chris is out of OpenAI
   credits and money to replenish. Render renders cost $1-3 each. **The
   first slice that needs render budgets is Slice 2** — Rigby firing
   renders. Build `RunwayCreditEvent` tracking + per-workspace budget
   gate as part of Slice 2, not later.
3. **Tool-description ≤1024 char drift in Slice 4.** The PR EW defensive
   truncation guard is critical and must be ported verbatim. If a
   future tool description silently exceeds 1024, Runway 400s the entire
   tools array and every realtime session is tool-less. Add a CI test:
   `assert all(len(t['description']) <= 1024 for t in REALTIME_TOOLS)`.

### H.2 Per-slice rollback

| Slice | Rollback | Cost |
|---|---|---|
| 1 (Advisor fields) | Migrate down + remove field declarations + delete portrait Cloudinary uploads | 1-2 hrs |
| 2 (SpokespersonAgent) | Remove agent from AGENT_MAP + studio_tool actions; orphan VideoHistory rows survive | 30 min |
| 3 (Finishing layers) | Remove studio_tool actions + delete `core/services/video_finishing/`; old VideoHistory rows untouched | 30 min |
| 4 (Realtime) | Remove Channels consumer + frontend CTA; AdvisorRealtimeSession rows survive | 1 hr |
| 5 (Initiative video) | Roll back PublishGate enum extension; existing video deliverables survive as orphans | 2 hrs |

**Total rollback to pre-merge state: ~5 hrs.** Higher than sidecar's
`migrate spokesperson zero` (~5 min), but bounded.

### H.3 What can't roll back

- Cloudinary uploads (advisor portraits, generated videos) — accept the leak
- Runway-bound avatar IDs — they persist on Runway's side, no UI for cleanup
- Render credits already spent — sunk cost

---

## I. Open questions for the operator

Native integration introduces a few questions the sidecar proposal
sidestepped. **Three new ones, three carried over.**

### I.1 (NEW) Advisor model precedent

> Adding 6 spokesperson-rendering fields to `Advisor` means future
> advisor concepts inherit them whether or not they need them. e.g. if
> a "synthetic advisor" mascot type ever lands, it carries portrait +
> avatar fields it doesn't use.
>
> Alternatives:
> (a) Accept the precedent — Advisor IS spokesperson, every Advisor has
>     these fields, future synthetic advisors just don't populate them
> (b) Add a `kind: human | synthetic` discriminator and gate the fields
> (c) Move the fields into a 1:1 OneToOneField sidecar
>     `AdvisorSpokesperson` model (compromise between this proposal and the sidecar)
>
> Recommendation: (a). Simplicity wins; nullable fields cost nothing;
> the discriminator approach is YAGNI today.

### I.2 (NEW) Per-workspace render budget

> Slice 2 lets Rigby fire $1-3 Runway renders. Without budget, a 50-message
> Rigby session = $50 in renders silently spent.
>
> Option: ship `RunwayCreditEvent` tracking + a per-workspace daily budget
> as part of Slice 2 (not later). Default budget: $5/workspace/day,
> override per workspace. Renders fail with a clear error when budget
> exhausted.
>
> Recommendation: ship as part of Slice 2. Per memory
> `project_current_state_2026_04`, you're already credit-conscious; add
> the rails before the spend can run away.

### I.3 (NEW) Editor-to-Spokesperson auto-compose

> When EditorAgent finishes a blog post, should it auto-trigger
> SpokespersonAgent to render a video companion? Or stay opt-in per
> operator request?
>
> Auto-compose unlocks "every blog post gets a 30-second Buffett
> companion video" out of the box. But it also means every
> ContentWriterAgent run silently triggers ~$2 in renders.
>
> Recommendation: opt-in. Add an `auto_render_spokesperson: false`
> default to Initiative metadata; operator flips per initiative when
> they want the companion.

### I.4 (CARRIED) Advisor ↔ Spokesperson coupling

> One Advisor → one rendered persona, or one Advisor → many?
>
> e.g. Buffett-Founder (suit, office) AND Buffett-Casual (open collar,
> coffee shop), both backed by the same wisdom JSON.
>
> In the sidecar proposal: solved via `Spokesperson.advisor` FK (1:N).
> In this proposal: harder — there's no Spokesperson model.
>
> Three options:
> (a) Strictly 1:1 — one portrait per advisor, ever
> (b) Add `AdvisorPortrait` 1:N child model (lightweight, only
>     `advisor / portrait_url / runway_avatar_id / voice_id /
>     subject_prompt`); the Advisor's "active" persona is one of these
> (c) Defer — start 1:1, add (b) only if operators request multiple
>     personas
>
> Recommendation: (c). Ship 1:1 now. The brief flagged advisor lookalikes
> as nice-to-have but not load-bearing.

### I.5 (CARRIED) Standalone repo lifecycle

> Same as sidecar proposal § I.5. After Slice 1 lands clean, freeze
> `runway-hackathon` immediately and do all future work in u-d-b.
>
> Recommendation: freeze after Slice 1.

### I.6 (CARRIED) Rigby render autonomy

> Should Rigby fire Runway renders without operator confirmation?
>
> $1-3 per render × tool-call frequency = real money fast.
>
> Recommendation: render write-actions require operator confirm in PA
> chat (existing pattern). Rigby can *propose* renders freely; only
> confirmation fires `apply_async`. Pair with the budget rail in § I.2.

---

## J. Decision checklist

Before greenlighting this proposal, the operator should be comfortable with:

- [ ] **Advisor schema mutation.** 6 fields added. Once shipped, removal is
      schema-breaking.
- [ ] **Native VideoHistory extension.** 7 fields added. Same constraint.
- [ ] **First-week spend.** Slice 1 portrait + avatar binds = ~$18 one-time.
- [ ] **Slice 2 spend rails.** Per-workspace render budget shipped *before*
      Rigby gets the render tool.
- [ ] **Realtime tool guard.** PR EW's ≤1024 char defensive truncation
      ported verbatim, with a CI test asserting the invariant.
- [ ] **Operator UX validation per slice.** Don't ship Slice 3 until Slice 2
      is operator-validated; don't ship Slice 4 until Slice 3 is.

If any of those is a "no," default to the sidecar proposal instead.

---

## Appendix A: comparison summary

| Dimension | Sidecar proposal | This proposal |
|---|---|---|
| New Django apps | 1 (`spokesperson/`) | 0 |
| New models | 6 | 2 (lightweight) |
| Field additions to existing models | 0 | ~13 (Advisor +6, VideoHistory +7) |
| New top-level frontend tab | 1 (SpokespersonTab) | 0 |
| New top-level routes | 1 namespace (`/api/spokesperson/`) | 0 (extend `/api/advisors/`, `/api/videos/`) |
| New PA gateway tools | 1 (`spokesperson_tool`) | 0 (extend `studio_tool`) |
| First visible win | Phase 1 (~2 weeks) | Slice 1 (~1-2 days) |
| 10 finishing layers operate on | SpokespersonOutput only | Any VideoHistory row |
| Rollback time to pre-merge | ~5 minutes | ~5 hours |
| Long-term system count | 2 (u-d-b + spokesperson) | 1 (u-d-b extended) |

---

## Appendix B: read order if this proposal is chosen

1. This doc
2. [`MERGE_PROPOSAL_CHARACTER_OS.md`](MERGE_PROPOSAL_CHARACTER_OS.md) for
   the alternative perspective
3. `runway-hackathon/docs/MERGE_HANDOFF_BRIEF.md` (sections C, the patterns
   table, and the RETIRE list)
4. `core/agents/talking_character_agent.py` — the existing agent shell to
   model `SpokespersonAgent` on
5. `core/services/pa_tool_schemas.py:1152` — `studio_tool` definition
6. `core/agent_router.py` — `AGENT_MAP` registration pattern
7. `content/models.py:2219` — `VideoHistory` schema to extend
8. `core/models_unified_system.py:828` — `Advisor` schema to extend
9. `core/celery.py` + `Procfile` for queue placement
10. `core/services/tool_dispatcher.py` for realtime tool integration

---

**End of counter-proposal.** No code touched. Awaiting operator decision
between this and [`MERGE_PROPOSAL_CHARACTER_OS.md`](MERGE_PROPOSAL_CHARACTER_OS.md)
via Rigby.

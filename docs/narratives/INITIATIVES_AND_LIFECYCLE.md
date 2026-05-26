---
title: "Initiatives and lifecycle — narrative (batch Q, draft)"
status: draft (batch Q of Session 1162 corpus-narrative program — Chris/Rigby review pending)
last_updated: 2026-05-26
session: 1162
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158) + EDITING_GUARDRAILS v1
companion_docs:
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/narratives/DECISION_COMMAND.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/topics/initiative-pipeline.md
  - docs/DREAM_INITIATIVE_WORKFLOW.md
  - docs/PLATFORM_INVENTORY.md
  - docs/narratives/EDITING_GUARDRAILS.md
provenance_confidence: HIGH (anchored to code paths + PLATFORM_INVENTORY 2026-05-26 + named session handoffs + 23 prior session handoffs)
provenance_note: Companion to SIGNAL_INTELLIGENCE (batch C) — that narrative covers the signal → cluster → topic → HiveMind → Initiative arc (the *upstream* creation path). This narrative covers the Initiative entity itself, the 5-status state machine, the 5-stage execution pipeline, every NON-signal creation path (Dream materialization / Decision conversion / PA tool / agent-initiated / management command), lifecycle (closure / archival / ON_HOLD), and the operator surface (PA work_tool actions + 18+ URL routes). Counts anchored to PLATFORM_INVENTORY 2026-05-26 (git HEAD `dc027f4f`). Status is "draft pending Rigby review" per Session 1124 co-authored doc pattern. Naming "AND_LIFECYCLE" reflects that the entity + state machine + 5-stage pipeline + closure mechanics are the focus.
---

# Initiatives and lifecycle

> **What this doc is.** An Initiative is the platform's unit of
> tracked, multi-stage work. It carries strategic metadata
> (purpose, program, priority inputs), executes through 5
> structured stages (Research Brief → Pilot Execution), and
> moves through a 5-status state machine (TRIAGE / ACTIVE /
> ON_HOLD / COMPLETED / ARCHIVED). Most operator-visible work
> on the platform lives inside an initiative — content goes
> through one, agent-recommended experiments go through one,
> Dream → product materialization goes through one.
>
> This narrative covers what an Initiative IS, every way one
> gets created (8 distinct entry points; only one is the
> signal-driven path covered in narrative C), how the
> 5-stage pipeline actually advances (it's NOT beat-scheduled
> — important gap from prior docs), how Dream materialization
> works (`AgentDream` is a real model, not a concept), the
> closure / archival mechanics, and the PA `work_tool` +
> URL surface for operator action.
>
> **Companion to SIGNAL_INTELLIGENCE (C).** Narrative C covers
> the signal → cluster → topic → HiveMind → Initiative arc —
> the *upstream* path that auto-creates initiatives from data.
> This doc covers the *downstream* surface — the Initiative
> entity itself, its lifecycle, and the 6 non-signal creation
> paths C doesn't cover. Where they meet (the TRIAGE intake
> state, circuit breaker, similarity dedup, quality gate),
> C is canonical and this doc points to it.

---

## §1 What this is

An Initiative is the platform's unit of multi-stage work. It
carries:

1. **Identity + strategic metadata** — name, description,
   `purpose` (revenue / stability / learning / expansion /
   maintenance), `program` (10 program enums), priority inputs
   (impact, urgency, confidence, revenue_potential), and an
   origin trace (signal_cluster + auto_topic FKs for
   signal-driven, source_decision_id for decision-converted,
   etc.).

2. **A 5-status state machine** — `TRIAGE` (queued for human
   review), `ACTIVE` (default for promoted work), `ON_HOLD`
   (paused), `COMPLETED`, `ARCHIVED`. Default on direct creation
   is `ACTIVE`; signal-driven auto-creation lands in `TRIAGE`
   per the quality-gate path (see narrative C).

3. **A 5-stage execution pipeline** — Research Brief → Prototype
   Plan → Evaluation Protocol → Technical Design → Pilot
   Execution. Each stage produces a structured document; each
   has an `InitiativeStage` row with its own status enum
   (PENDING / DRAFT / IN_REVIEW / APPROVED / REJECTED /
   SUPERSEDED / BLOCKED) plus drift detection (Session 914.3).
   See §3M3 for advance mechanics.

4. **Ownership + execution intent** — human `owner` FK or
   agent `owner_agent` CharField; `execution_speed` (fast /
   balanced / thorough), `risk_tolerance` (low / medium / high);
   `founder_intent_set` boolean indicating Chris has approved
   the execution shape.

5. **Linked artifacts** — `InitiativeActionItem` rows (extracted
   from HiveMind `=== DecisionSummary ===` sections — see
   narrative C), `Deliverable` rows (FK from Deliverable side
   with `publish_intent` enum from Session 1095), and stage
   documents (FK to `SelfBlog` via `InitiativeStage.document`).

**The narrative-shift this doc makes vs prior docs:** earlier
content treats "the initiative pipeline" as a single
signal-driven flow. Reality 2026-05-26 — initiatives have **8
creation entry points** (only one is signal-driven), the
5-stage pipeline advance task is **NOT beat-scheduled** (it
runs on-demand via API only, see §3M4), and there is **no
automatic completion** (initiatives can sit in TRIAGE
indefinitely until a human promotes or cleanup archives them).
The §6 Open Questions list flags these as deliberate-or-drift
calls for Rigby.

---

## §2 Vocabulary

| Term | Definition |
|---|---|
| **`Initiative`** | The core Django model (`core/models_document_registry.py:37-262`). Carries identity, strategic metadata, status, current_stage (1-5), priority inputs, ownership, and origin-trace FKs. Lives in the **document registry** module (not models_unified_system.py — surprising; worth knowing for grep). |
| **5-status state machine** | `TRIAGE` / `ACTIVE` / `ON_HOLD` / `COMPLETED` / `ARCHIVED`. Canonical values defined on the model (`core/models_document_registry.py:47-52`). Default on direct creation is `ACTIVE`; signal-driven auto-creation lands in `TRIAGE`. |
| **`current_stage`** | IntegerField 1-5 on Initiative. Tracks which of the 5 stages the initiative is on. Default 1 on creation. |
| **5-stage pipeline** | Research Brief → Prototype Plan → Evaluation Protocol → Technical Design → Pilot Execution. Stage names canonical at `core/models_document_registry.py:1230-1235`. Each stage has its own InitiativeStage row. |
| **`InitiativeStage`** | Per-stage tracking model (`core/models_document_registry.py:1262-1410`). Links Initiative ↔ stage document with approval workflow, audit fields, and drift detection (Session 914.3). Hard invariant: cannot set `status=APPROVED` without `document` set (enforced in `clean()` + `save()` per Session 916). |
| **InitiativeStage status enum** | Stage-level state machine (separate from Initiative status). See the StageStatus field definition in `core/models_document_registry.py:1262-1410` for canonical values; treat the model as the source of truth. |
| **`InitiativeActionItem`** | Structured task model (`core/models_document_registry.py:1841-1950`). Extracted from `=== DecisionSummary ===` sections in HiveMind conversation conclusions by `core/services/action_item_parser.py` (Session 902). Carries status, priority, timeline (parsed from text like "Week 0-1"), agent + user assignment, dependencies M2M, plus a `source_stage` FK back to which stage doc generated this (Session 1058). See narrative C for the upstream extraction flow. |
| **`AgentDream`** | A real model (`core/models_unified_system.py:9144-9340`), not a concept. Carries scoring fields (vividness, creativity, actionability, relevance, composite), promotion state, origin enum (serious / speculative / probe / joke), and an FK to `Initiative`. Promoted dreams materialize into initiatives via `promote_to_initiative()` (see §3M5). |
| **Dream → Initiative materialization** | The pipeline: agents dream while idle → `score_and_promote_dreams` scores → high-scoring dreams go to Boardroom → if approved, `promote_to_initiative()` creates an Initiative in `TRIAGE` with Stage 1 `DRAFT` and the dream content threaded through. See §3M5. |
| **`advance_initiative_pipeline`** | The Celery task that progresses initiatives through stages (`core/tasks.py:3107-3113`, impl in `core/tasks_initiatives.py:1921-2120`). Queue: `content`. **NOT in beat schedule as-of 2026-05-26** — runs on-demand only via `/api/initiatives/trigger/`. See §3M4. |
| **`founder_intent_set`** | Boolean on Initiative. `True` means Chris has explicitly set `execution_speed` + `risk_tolerance` for this initiative. The execution-track classifier (Fast Track vs Institutional, narrative C milestone 4) uses this. |
| **`execution_speed` / `risk_tolerance`** | Pair of enum fields capturing the execution shape Chris signed off on. Used by the Fast Track / Institutional Track classifier. See narrative C for the classifier logic. |
| **`source_decision_id`** | UUIDField (nullable) on Initiative. Set when the initiative was created from a Boardroom Decision via the `/api/platform/decision-summary/<uuid>/create-initiative/` endpoint (Session 852). One of the 8 creation paths. |
| **`target_workspace`** | FK on Initiative to `ProjectWorkspace`. Scopes deliverables produced by this initiative to a specific workspace. See narrative on workspaces (WORKSPACES_AND_SCOPING) for the workspace concept. |
| **`Deliverable.initiative`** | The reverse-direction FK on the Deliverable model (`core/models_deliverables.py:176-182`). Lets a stage doc / agent output point back to which initiative produced it (Session 862). |
| **`publish_intent`** | Enum on `Deliverable` (`core/models_deliverables.py:58-81`). Session 1095 architecture: separates "what is this artifact" from "what's its workflow state." Canonical values at the model field; treat the enum as authoritative. See narrative B (CONTENT_PIPELINE) for the publication mechanics. |
| **Circuit breaker** | Backlog throttle (Sessions 884, 994, 1020). When ACTIVE + TRIAGE initiatives without recent activity exceed a threshold, new creation is blocked. Bypassable per-call (`bypass_circuit_breaker=True` for manual PA creation — see §3M6). Canonical implementation: `core/services/initiative_circuit_breaker.py`. See narrative C for the threshold + dedup rules. |
| **TRIAGE intake state (Session 994)** | The pre-active state for auto-created initiatives. PA's `work_tool update_status` promotes TRIAGE → ACTIVE. Prevents auto-generated work from polluting the active pipeline. See narrative C milestone 3. |
| **Stage drift detection (Session 914.3)** | InitiativeStage carries `drift_score`, `similarity_score`, `drift_flagged`, `drift_override`. Detects when an agent regenerates a stage doc that's significantly different from prior drafts. Operator can override; without override, the platform flags for human review. |

---

## §3 Milestone timeline

### Milestone 1 — `Initiative` model and the 5-status state machine

**Code anchor:** `core/models_document_registry.py:37-262`. Status enum at lines 47-52.

The model carries the strategic metadata (purpose, program,
priority inputs), the state (status + current_stage),
ownership, and origin-trace FKs. A reader unfamiliar with the
codebase looks for "Initiative" and expects it in
`models_unified_system.py` (where most cross-cutting models
live); it's actually in `models_document_registry.py`. That
naming choice reflects the Session 695-era decision that
initiatives are *document-producing* work — every stage emits a
document, every action item lands in a document, every
deliverable is a document.

The 5-status state machine is simpler than it looks. The
non-obvious transitions:

- **Default on direct creation**: `ACTIVE`. Manual creation
  (via PA tool, decision conversion, agent-initiated) lands
  here.
- **Signal-driven auto-creation**: `TRIAGE`. Per Session 994
  + narrative C, the quality-gate path puts auto-created
  initiatives in `TRIAGE` so humans can review before they
  enter the active pipeline.
- **`ON_HOLD`**: Pause state. Set manually via PA
  `work_tool update_status`. Resume via the `promote` action
  (TRIAGE / ON_HOLD → ACTIVE).
- **`COMPLETED`**: No automatic transition exists.
  Initiatives reach `COMPLETED` only via manual status update;
  there's no "all stages approved → mark complete" auto-flow
  as-of 2026-05-26. See §6 Open Questions.
- **`ARCHIVED`**: Set by the `cleanup_junk_initiatives` task
  for stale items (no Stage 1 doc after a window of days); also
  set manually for explicit archival.

### Milestone 2 — `InitiativeStage` as the per-stage tracking layer (Session 916 hard invariant)

**Code anchor:** `core/models_document_registry.py:1262-1410`. Stage names dict at lines 1230-1235.

Each Initiative has up to 5 `InitiativeStage` rows (one per
stage 1-5). The stage row carries its own status enum, FK to
the produced document (a `SelfBlog` row), approval audit
fields (`approved_by`, `approved_at`, `rejection_reason`), and
the Session 914.3 drift-detection fields (`drift_score`,
`similarity_score`, `drift_flagged`, `drift_override`).

The Session 916 hard invariant: a stage **cannot be marked
APPROVED without `document` set**. Enforced both in `clean()`
and in `save()`. The reason: a prior bug-class let agents
"approve" stages without producing the document, leaving the
pipeline with phantom-approved stages no human ever saw.

### Milestone 3 — Stage names + canonical mapping

**Code anchor:** `STAGE_NAMES` dict at `core/models_document_registry.py:1230-1235`.

The 5 stages and the questions they answer:

1. **Research Brief** — *Why does this matter?*
2. **Prototype Plan** — *How would we build this?*
3. **Evaluation Protocol** — *Should we proceed?* (PASS / LEARN / FAIL)
4. **Technical Design** — *Exactly what to build*
5. **Pilot Execution** — *What happened and what did we learn?*

These question framings are the operator mental model. The
agent that generates the stage document
(`TechnicalDocumentAgent` for most stages) uses the framing
to scope what each document contains.

**Fast Track vs Institutional Track** — narrative C milestone 4
covers this. Short version: Fast Track stops at Stage 2
awaiting founder decision (`founder_intent_set` boolean);
Institutional Track runs all five with approval gates and
content-flag triggers.

### Milestone 4 — `advance_initiative_pipeline` is NOT beat-scheduled

**Code anchor:** Task definition at `core/tasks.py:3107-3113`; impl at `core/tasks_initiatives.py:1921-2120`; **absence** verified against `core/celery.py:app.conf.beat_schedule` (no entry).

This is the milestone most operator docs miss. The task
that progresses initiatives through stages is registered as a
Celery `@shared_task` on the `content` queue, but **as-of
2026-05-26 it is not in the beat schedule**. It runs only
on-demand, triggered by:

- `POST /api/initiatives/trigger/` (Session 880, called from
  the UI's "Advance Pipeline" action)
- Direct `.delay()` invocation from another task or service
- Operator running it via `python manage.py shell`

What the task does each run:
1. Finds ACTIVE initiatives with PENDING or DRAFT stages
   lacking documents.
2. Ensures the prior stage is APPROVED before generating the
   next (Session 1021: no skip-ahead).
3. Generates the stage document via `TechnicalDocumentAgent`.
4. Auto-approves the stage + advances `current_stage += 1` if
   `auto_approve=True` (default; per Session 880).
5. Returns `{processed, documents_created, stages_approved, errors}`.

**If pipeline feels stalled** — the first diagnostic question
is "did anyone trigger advance?" not "is the worker broken?"
The pipeline doesn't self-advance.

### Milestone 5 — Dream → Initiative materialization (Session 862)

**Code anchor:** `AgentDream` model at `core/models_unified_system.py:9144-9340`. Promotion path at `promote_to_initiative()` line 9490-9577. Impl flow at `core/tasks_initiatives.py:_impl_process_approved_dreams` (1227-1429).

Dreams are a real model. Agents dream continuously when idle
(originally Session 247, un-deprecated Session 366). Each
dream carries five scores (vividness, creativity,
actionability, relevance, composite) and an origin enum
(serious / speculative / probe / joke) that weights its
promotion likelihood.

The materialization pipeline:

1. **Generate** — agents emit `AgentDream` rows during idle
   cycles.
2. **Score** — `score_and_promote_dreams` task
   (`core/tasks_initiatives.py:973-1225`) calculates composite
   scores.
3. **Promote-to-Decision** — dreams above the promotion
   threshold (operator-tunable; defaults to roughly 0.85)
   go to the Boardroom as `AgentDecisionSummary` rows for
   human review.
4. **Approval** — if the Boardroom decision approves the
   dream, `promote_to_initiative()` runs.
5. **Materialize** — creates an `Initiative` row in `TRIAGE`
   with `current_stage=1`, `owner_agent` auto-assigned from
   the dream creator, and an `InitiativeStage` row for Stage 1
   in `DRAFT` with the dream content threaded through.

**Dedup** — Session 1020 added `find_similar_initiative()` to
the path. Before creating a new Initiative from an approved
dream, the platform Jaccard-checks against existing ACTIVE +
TRIAGE initiatives. If similarity is above the threshold
(see narrative C for the value + tuning), the dream is linked
to the existing initiative instead of creating a duplicate.

**Common confusion** — the `Dream` model is named
`AgentDream`, not `Dream`. The `DreamImplementation` wrapper
tracks execution. Grep `class AgentDream` to find the model.

### Milestone 6 — The 6 non-signal creation paths

**Code anchors:** see table.

Signal-driven creation (path 1 — covered in narrative C) is
the most visible but represents one of eight entry points.
The other seven:

| # | Path | Trigger | Code anchor |
|---|---|---|---|
| 2 | **PA `work_tool` (action=initiative_create)** | Operator asks Rigby "create an initiative for X" | `core/services/td_handlers_content.py:2322-2381` (action='create' handler). `bypass_circuit_breaker=True` for manual paths. |
| 3 | **Dream → Initiative materialization** | Approved Boardroom dream | `AgentDream.promote_to_initiative()` — `core/models_unified_system.py:9490-9577` |
| 4 | **Decision → Initiative** | Boardroom decision conversion | `POST /api/platform/decision-summary/<uuid>/create-initiative/` — `core/urls.py:4513` |
| 5 | **Agent-initiated** | An autonomous agent executes work that materializes into an initiative | `core/services/autonomous_action_executor.py:_link_to_initiative` |
| 6 | **Management command** | `extract_initiatives_from_survey` materializes structured survey responses | `core/management/commands/extract_initiatives_from_survey.py` |
| 7 | **HiveMind start-conversation** | An initiative gets a HiveMind conversation attached (creates an `InitiativeActionItem` chain, not always a new Initiative — see narrative C for the bridge) | `POST /api/initiatives/<uuid>/start-conversation/` — Session 928 |
| 8 | **Signal-driven** | Narrative C — *covered there, not here* | See narrative C milestone 3 |

**The gap:** there is **no direct manual UI form** for creating
an initiative outside the PA tool path. Operators who want a
plain "New Initiative" button file the request through Rigby
or use the management command. See §6 Open Questions for the
deliberate-or-oversight call.

### Milestone 7 — `InitiativeActionItem` extraction and the action-item lifecycle

**Code anchor:** Model at `core/models_document_registry.py:1841-1950`. Parser at `core/services/action_item_parser.py:66-86`.

`InitiativeActionItem` is the structured-task layer. Each
item carries:

- `initiative` FK (CASCADE delete on Initiative removal)
- `title`, `description`
- `status` (PENDING / IN_PROGRESS / COMPLETED / BLOCKED /
  CANCELLED)
- `priority` (CRITICAL / HIGH / MEDIUM / LOW)
- `assigned_agent` (CharField) + `assigned_user` (FK)
- `timeline_text` (raw parsed text) + `due_date`
- `source_conversation` FK to `HiveMindSession`
- `source_stage` FK to `InitiativeStage` (Session 1058 — which
  stage doc generated this)
- `source_text` (the original parser input)

**Extraction** — the parser scans HiveMind conversation
conclusions for sections labeled "next steps", "action items",
"follow-up", "to do", "tasks", "deliverables", or
"recommendations". Within those sections it recognizes three
patterns: `AGENT_TASK_PATTERN` (e.g., "ResearchAgent: Do X"),
`NUMBERED_TASK_PATTERN` (e.g., "1. Do Y"), and timeline
extraction (`WEEK_PATTERN`, `DAY_PATTERN`, `IMMEDIATE_PATTERN`).

**Operator surface** — PA `work_tool` actions for action
items: `action_item_list`, `action_item_start`,
`action_item_complete`, `action_item_cleanup`, `bulk_cleanup`.
See §3M9 for the action catalog.

### Milestone 8 — `Deliverable.initiative` FK and `publish_intent` enum (Session 1095)

**Code anchor:** `Deliverable.initiative` FK at `core/models_deliverables.py:176-182`. `publish_intent` field at lines 58-81.

The reverse direction of the initiative ↔ artifact link.
Deliverables (blog posts, podcasts, code, generated documents)
carry an optional `initiative` FK with
`on_delete=models.SET_NULL` — deleting an initiative does NOT
cascade-delete its deliverables; they survive as orphans for
audit purposes.

The Session 1095 architecture decision: separate "what is this
artifact" from "what's its workflow state." `publish_intent`
is a 3-value enum (canonical values + meanings on the model
field; treat the enum as authoritative) distinguishing
internal artifacts (agent analysis, intermediate stage docs)
from publishable artifacts (must publish or it's an incident)
from gated artifacts (publication subject to review).

The COO diagnostic gates work against the `publish_intent`
field (see narrative A milestone 7 for the anti-spam rails),
not `Initiative.status`. The two state spaces are
deliberately orthogonal.

### Milestone 9 — Closure, archival, and cleanup

**Code anchors:** `cleanup_junk_initiatives` at `core/tasks_initiatives.py:41-229`; `cleanup_stale_dreams` at 1430-1523. Both daily at 04:00 wall-clock per `core/celery.py` beat schedule.

A reader asking "when do initiatives go away?" needs to know:

- **No automatic completion** — there is no path that marks
  an Initiative `COMPLETED` based on all stages reaching
  APPROVED. Completion is always a manual status update via
  PA `work_tool update_status` or admin.

- **`cleanup_junk_initiatives`** (daily, 04:00) — identifies
  initiatives with junk names (fragments, auto-generated
  placeholders) created more than ~7 days ago. Tries to fix
  the name via the title-generator service first. If
  unfixable, deletes the row. If a fixable-name initiative
  has been stale (no Stage 1 doc, no activity), it gets moved
  to `ARCHIVED`.

- **`cleanup_stale_dreams`** (separate daily task) — cleans
  up dangling `DreamImplementation` records for dreams
  approved-but-pending-execution for more than ~72h. Doesn't
  archive the Initiative; just removes the dangling promotion
  record.

- **No explicit TRIAGE timeout** — a TRIAGE initiative not
  promoted to ACTIVE will sit there indefinitely. The only
  cleanup is the junk-name path. See §6 Open Questions for
  whether this is intentional or a missing piece.

### Milestone 10 — PA `work_tool` initiative action catalog

**Code anchor:** Handler at `core/services/td_handlers_content.py:1417-2388` (`_handle_initiative` method). Routed via `work_tool` at `core/services/td_handlers_core.py:2220-2370`.

The operator surface through Rigby. Action names + what they
do (file: line ranges in `td_handlers_content.py`):

| Action | Purpose | Lines |
|---|---|---|
| `list` | Filter initiatives by status/stage/purpose/program/owner/workspace, paginate | 1442-1573 |
| `details` | Full details by ID/name/human_id | 1699-1800 |
| `stats` | Pipeline overview — totals + by_status + by_stage + by_purpose + by_program + action items count | 1645-1697 |
| `audit` | Surface duplicates, stalled, noise, classification issues | 1575-1643 |
| `create` | Create or get-or-create initiative (manual paths bypass circuit breaker) | 2322-2381 |
| `update_status` | Transition ACTIVE ↔ ON_HOLD ↔ COMPLETED ↔ ARCHIVED | 1929-1974 |
| `promote` | Move TRIAGE / ON_HOLD → ACTIVE | 2075-2113 |
| `flow_metrics` | Creation rate, backlog, stage distribution, circuit breaker status, completion rate | 2115-2173 |
| `action_items` | List pending action items across initiatives | (varies) |
| `start_action_item` / `complete_action_item` | Per-item status transitions | (varies) |
| `cleanup_action_items` / `bulk_cleanup` | Stale + completed item cleanup | (varies) |

Via `work_tool` (the Session 1078 consolidation), Rigby
exposes these as: `initiative_list`, `initiative_create`,
`initiative_promote`, `initiative_update_status`, plus the
action-item variants. See narrative D (PERSONAL_ASSISTANT) for
the tool-consolidation pattern.

### Milestone 11 — URL route catalog

**Code anchor:** `core/urls.py:3230-3257` for the main initiative API surface; `core/urls.py:4513` for the decision-conversion endpoint.

As-of 2026-05-26 (git HEAD `dc027f4f`), the initiative-related
URL routes are listed in `core/urls.py` and grouped by Session
they were added in. Rather than enumerate them here (rule 3),
the canonical home is the urls.py block lines 3230-3257 plus
the platform decision-summary endpoint at line 4513. Treat
the urls.py block as the source of truth.

Notable routes worth knowing by name:

- `/api/initiatives/trigger/` — manually fire `advance_initiative_pipeline`.
- `/api/initiatives/<uuid>/start-conversation/` — attach a HiveMind conversation.
- `/api/initiatives/<uuid>/origin-trace/` — full provenance chain.
- `/api/initiatives/<uuid>/founder-intent/` — set execution-shape fields.
- `/api/platform/decision-summary/<uuid>/create-initiative/` — Decision → Initiative conversion.
- `/api/initiatives/pipeline-health/` — real-time pipeline health snapshot.

The number and shape of these routes drifts as features land;
the file is the truth.

---

## §4 What came of it

Initiatives gave the platform a clean answer to four problems
that earlier versions handled implicitly:

- **Where does multi-stage work live?** Before initiatives,
  the platform tracked agent execution + content production
  + experiments in disjoint subsystems. Initiatives unified
  them — every multi-stage workflow now has one home.

- **How does Chris see the queue?** The 5-status state
  machine plus the PA `work_tool flow_metrics` action gives
  the answer to "what's queued, what's active, what's
  stuck?" without per-subsystem queries.

- **How do dreams become work?** The `AgentDream` →
  `promote_to_initiative()` path closes the loop between
  agent idle thinking and tracked execution. Before Session
  862 these were independent streams.

- **How do we trace provenance?** Every initiative carries
  origin-trace FKs (`signal_cluster`, `auto_topic`,
  `source_decision_id`, `parent_topic`). A reader can
  follow any initiative back to whichever upstream signal,
  decision, dream, or human request created it.

The pattern that matters across all four: initiatives are
*named, tracked, multi-stage work*. The platform doesn't
treat work as ephemeral execution because the Initiative row
persists across stages + status transitions.

---

## §5 Current state snapshot

As-of PLATFORM_INVENTORY 2026-05-26 (git HEAD `dc027f4f`):

- **Status state machine:** 5 values
  (`core/models_document_registry.py:47-52`).
- **Stage pipeline:** 5 stages
  (`core/models_document_registry.py:1230-1235`).
- **Creation entry points:** 8 distinct paths (see §3M6).
- **Advance task scheduling:** on-demand only — NOT in beat
  schedule (§3M4).
- **Cleanup tasks:** `cleanup_junk_initiatives` (daily 04:00),
  `cleanup_stale_dreams` (daily, separate time). Both via
  `app.conf.beat_schedule` in `core/celery.py`.
- **Operator surface (PA):** `work_tool` exposes ~11+ initiative
  actions (handler `_handle_initiative` in
  `td_handlers_content.py`).
- **URL surface:** 18+ initiative-related routes in
  `core/urls.py` (treat the file as canonical).
- **Linked models:** `Initiative`, `InitiativeStage`,
  `InitiativeActionItem`, `AgentDream`, `Deliverable`
  (via FK back).

---

## §6 Open questions

Each item below is a *gap* in the implementation or in the
docs, flagged per EDITING_GUARDRAILS rule 5 ("should not; if
it does, check ___").

### 6.1 No automatic completion path

As-of 2026-05-26, there is no code path that marks an
Initiative `COMPLETED` based on all 5 stages reaching
APPROVED. The only paths to `COMPLETED` are manual status
updates (via PA `work_tool` or admin). **If you observe an
Initiative auto-transition to COMPLETED**, that's the path
you should look for in code — it doesn't exist now and adding
it would be a real change worth a separate PR.

**Possible deliberation:** is the absence intentional (Chris
wants to keep humans-in-the-loop on closure) or an oversight
(no one ever wrote the "all stages approved → mark complete"
hook)? Rigby's call.

### 6.2 No TRIAGE timeout / auto-cleanup

A TRIAGE initiative not promoted to ACTIVE will sit in
TRIAGE indefinitely. `cleanup_junk_initiatives` handles
junk-named items but doesn't time-bound TRIAGE specifically.
A TRIAGE initiative with a real-looking name could persist
for months.

**Possible deliberation:** add a Session-N task that archives
TRIAGE items older than N days, or document why the absence
is correct? Rigby's call.

### 6.3 No direct manual UI form for Initiative creation

All 8 creation paths are programmatic — PA tool, mgmt command,
Dream/Decision/Signal materialization, agent-initiated. There
is no plain "New Initiative" form route in the frontend.
**If an operator says "I can't find the create-initiative
button"**, the answer is "ask Rigby" or "use the mgmt command"
— there isn't one to find.

### 6.4 `advance_initiative_pipeline` is not beat-scheduled

This is named throughout the code as the pipeline-advancing
task, but it only runs on demand. **If you observe an ACTIVE
initiative whose `current_stage` hasn't moved in days**, check
whether anyone triggered advance — they likely didn't.

**Possible deliberation:** is on-demand-only the right
shape (the task is expensive and shouldn't fire continuously),
or should there be a low-frequency beat entry (every 6h?
daily?) for safety? Rigby's call.

### 6.5 Stage-doc generator can lag the model

`TechnicalDocumentAgent` is the default generator for stage
documents (Session 880). If the agent fails or the platform
content-deliberation pipeline (narrative B) is paused, stages
get stuck at `DRAFT` without a `document` FK set — at which
point the Session 916 invariant blocks approval. The fix is
to invoke `advance_initiative_pipeline` again (which will
retry the generation) or to backfill documents via the
`/api/initiatives/backfill-documents/` endpoint (Session 915).
**If you see Stage 1 stuck for many initiatives at once**, the
upstream is probably the content pipeline, not the initiative
subsystem.

---

## §7 Source index

Sessions that shaped this subsystem (chronological):

- **Session 247** — `AgentDream` model added (later
  un-deprecated Session 366).
- **Session 695** — initiatives moved into the document
  registry; `current_stage` field added.
- **Session 847-849, 860** — initiative pipeline early
  hardening.
- **Session 862** — Dream → Initiative materialization
  formalized; `Deliverable.initiative` FK added.
- **Session 866** — research-report improvements (stage
  documents).
- **Session 871** — initiative list/details API surface
  (`/api/initiatives/` etc.).
- **Session 880** — `/api/initiatives/trigger/`; auto-advance
  with `auto_approve=True` default.
- **Session 884** — circuit breaker added; stuck-stage
  diagnostic endpoints.
- **Session 898** — origin-trace endpoint.
- **Session 902** — `=== DecisionSummary ===` extraction →
  `InitiativeActionItem` rows.
- **Session 905, 916** — title generator; Session 916 hard
  invariant on InitiativeStage approval.
- **Session 913** — signal-cluster + auto-topic FK origin
  tracking on Initiative.
- **Session 914.3** — stage drift detection fields.
- **Session 915** — backfill-documents endpoint.
- **Session 920** — reset-premature-completed endpoint.
- **Session 921** — pipeline-health + diagnose-stuck.
- **Session 928** — initiative ↔ HiveMind conversation
  start-conversation endpoint.
- **Session 994** — TRIAGE intake state; quality gate.
- **Session 996** — `PROGRAM_OWNER_MAP` auto-ownership.
- **Session 1018-1021** — pipeline integrity sweeps; Session
  1020 similarity dedup; Session 1021 no-skip-ahead rule.
- **Session 1058** — `InitiativeActionItem.source_stage` FK.
- **Session 1078** — `work_tool` consolidation (initiative
  actions surfaced through it).
- **Session 1083** — marathon session covering pipeline
  + content + agent improvements.
- **Session 1091** — ops hardening + workspace flow.
- **Session 1095** — `Deliverable.publish_intent` enum.
- **Session 1098, 1099** — handoffs that touched pipeline
  observability (search_docs originating_session filter
  cache, COO diagnostic, etc.).
- **Session 1158-1162** — narrative pilot established the
  template + EDITING_GUARDRAILS that this doc follows.

---

## §8 Canonical sources

This narrative is authoritative for:
- The vocabulary table in §2 (Initiative-entity terms).
- The 8-path creation taxonomy in §3M6.
- The "advance is on-demand, not beat-scheduled" finding in §3M4.
- The 5-status state machine in §1 + §3M1.
- The Dream → Initiative materialization mechanics in §3M5.
- The closure / cleanup gap analysis in §3M9 + §6.

This narrative is NOT authoritative for:
- **Signal-driven creation arc** (spider → cluster → topic →
  HiveMind → Initiative) — see narrative C
  (SIGNAL_INTELLIGENCE).
- **Circuit breaker threshold + dedup rules** — see narrative
  C.
- **TRIAGE intake state mechanics + quality gate** — see
  narrative C milestone 3.
- **`InitiativeActionItem` extraction parser rules** — see
  narrative C (this doc names the model; C names the
  extraction logic).
- **Fast Track vs Institutional Track classifier** — see
  narrative C milestone 4.
- **PA tool consolidation pattern + `work_tool` design** —
  see narrative D (PERSONAL_ASSISTANT).
- **Anti-spam rails + COO diagnostic gates against
  `publish_intent`** — see narrative A milestone 7.
- **Content deliberation pipeline (where stage documents
  actually get generated)** — see narrative B
  (CONTENT_PIPELINE).
- **Counts** (initiative totals, action item counts, etc.) —
  see `PLATFORM_INVENTORY.md`.
- **Canonical enum values** (status, stage status, action
  item status, publish_intent) — see the respective model
  field definitions in `core/models_document_registry.py` +
  `core/models_deliverables.py`.

---

## Draft notes (remove on lock)

- First-draft pending Chris + Rigby review per the Session
  1124 co-authored doc pattern. Claude scaffolded structure +
  anchored to code; Rigby's review will check voice, audience
  framing, and §6 Open Questions framing.
- Companion to SIGNAL_INTELLIGENCE intentionally — explicit
  scoping discipline in §8 to avoid duplication. Where the
  two narratives meet (TRIAGE state, circuit breaker, action
  item extraction parser), C is canonical; this doc points.
- Naming: `INITIATIVES_AND_LIFECYCLE.md` picks up entity +
  state machine + 5-stage pipeline + closure mechanics. Open
  to renaming per Rigby's call.
- Letter assignment: batch Q (next after batch P /
  WORKSPACES_AND_SCOPING).
- Five Open Questions in §6 (no auto-completion, no TRIAGE
  timeout, no manual UI form, advance task not beat-scheduled,
  stage-doc generator lag). All are deliberate-or-drift calls
  worth Rigby's verdict before lock.

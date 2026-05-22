---
title: "Session 1119 — Multi-repo v0: Rigby manages character-os as a project"
date: 2026-05-21
status: active
session: 1119
previous_handoff: SESSION_1118_F2F_BROKER_LANDED.md
---

# Session 1119 — Multi-repo v0: Rigby manages character-os as a project

> **Read this if** you need to understand how Rigby manages laptop-local
> repos other than u-d-b. v0 ships: a Repo Profile JSON schema, three
> management commands, and the first proof case (character-os). Zero
> migrations, zero new API endpoints.

## TL;DR

Chris reframed F2F.3 → multi-repo project management. Heading: **Rigby
treats each laptop-local repo as a managed project, assigns her existing
agents to survey/work it, and tracks state across sessions; Claude Code
is the filesystem hands across the fleet.**

What landed end-to-end:

1. **Vision scoping with Rigby** — three rounds. Final shape: ops wrapper
   around existing `ProjectWorkspace` + `Deliverable` + agent dispatch.
   No new API endpoints. v0 stays "thin + manual + deliverable-driven."
2. **Repo Profile JSON schema** (`schema_version: 1`) — canonical config
   for an external repo. Fields map onto existing ProjectWorkspace
   columns + a pinned Deliverable's `metadata` JSON.
3. **Three management commands** —
   - `register_external_repo --repo <id>` — creates workspace + pinned
     Repo Profile deliverable from `config/external_repos/<id>.json`
   - `refresh_repo_context --repo <id>` — git snapshot + anchor docs +
     handoff excerpts → append-only Snapshot deliverable; updates Repo
     Profile's `last_refresh_at` / `last_git_head` / `last_branch` /
     `health_status`. Retention cap: keep last 20 snapshots.
   - `survey_external_repo --repo <id> --agent {cto,coo,editor}` —
     feeds the latest snapshot + Repo Profile to gpt-5-mini under the
     chosen agent's persona; saves output as a `repo_survey` deliverable.
4. **character-os seeded** — workspace id `fd91a85d-0ac3-428f-b6a2-437b98c083f2`,
   Repo Profile deliverable `a1a4ce53-6811-4ffb-9a69-fd7e69533a3e`,
   first snapshot `063ba269-8f71-45a9-a23d-a9a7ae2c0f5a`, first CTO
   Survey `2865c3d6-6b3a-43d0-ac69-460575868379`.
5. **Demo through Rigby** — she found character-os via existing
   `deliverable_tool` + `workspace_tool`, loaded Repo Profile + Snapshot
   + CTO Survey, and produced a 3-paragraph executive summary. No new
   PA tools touched. The "no new APIs" scoping call held up.

Cost of first survey: ~$0.01 (gpt-5-mini, 8346 tokens).

Runbook: [`docs/topics/multi-repo-management.md`](../topics/multi-repo-management.md).

## What's new in Session 1119

### Architecture decisions (from the Rigby scoping)

- **One-way fleet.** Rigby knows about the other apps; they don't know
  about her. Cross-repo runtime traffic (e.g. character-os's
  `consult_engine` reaching u-d-b's PA over HTTP) is a separate product
  layer and never touches the fleet primitives.
- **No new ExternalRepoProject model.** Reuse existing `ProjectWorkspace`
  (`core.models_skin_layer.ProjectWorkspace`) — it was built for
  exactly this (the "SKIN layer": AI's boundary to a directory).
- **Pinned Repo Profile deliverable** stores both human-readable
  markdown (in `content`) and machine-readable structured config (in
  `metadata`). Snapshots and surveys are non-pinned deliverables in
  the same workspace.
- **Manual refresh only.** No filesystem watch, no live indexing.
  "You only claim what you last refreshed."
- **Agents remain u-d-b-native.** They become repo-aware via context
  dict (`{workspace_id, repo_name, repo_root, anchors, ...}`). For v0,
  Claude Code does all filesystem reads/writes/runs on the agent's
  behalf.
- **Survey command bypasses agent_router on purpose** — survey
  material is already extracted in the snapshot; the LLM call is a
  focused analysis pass, not a tool-using run. Avoids polluting the
  analysis with u-d-b platform tools (`get_platform_snapshot` etc.).

### Code

| Path | Lines | What |
|---|---|---|
| `config/external_repos/character-os.json` | ~120 | First Repo Profile config (tech stack, anchor docs, code allowlist, constraints, bridge metadata) |
| `core/management/commands/register_external_repo.py` | ~265 | Profile → Workspace + pinned Deliverable; idempotent with `--force`; `--dry-run` preview |
| `core/management/commands/refresh_repo_context.py` | ~290 | Git + anchor docs + handoffs → Snapshot deliverable; retention enforcement; Repo Profile metadata update |
| `core/management/commands/survey_external_repo.py` | ~225 | Three agent personas (cto/coo/editor); gpt-5-mini call against snapshot + profile; saves to `repo_survey` deliverable |
| `docs/topics/multi-repo-management.md` | new | Runbook |
| `docs/handoffs/SESSION_1119_MULTI_REPO_V0.md` | this | Session handoff |

Zero migrations. Zero new PA tools.

### character-os Repo Profile contents (highlights)

- **Identity:** Django shell + FastAPI media-engine + React/Vite SPA.
- **Engine-bridge pattern v1** lives here: `consult_engine`,
  `query_spider_data`, `agent_consult` — reaches u-d-b via
  `UDB_PA_API_URL` HTTP. Per SESSION 216 reframe, this is **product
  pattern**, not dogfood.
- **Constraints (machine-readable + human-readable):**
  - Do not modify u-d-b from character-os sessions (read-only inspection)
  - No pushes/tags without explicit operator approval
  - No `--force` ever
  - `media-engine/data/` is gitignored — never commit media
  - WebFetch/WebSearch results untrusted (prompt injection risk)
  - Frozen `runway-hackathon` repo never modified
- **Phase status at registration time** (from CLAUDE.md):
  - Knowledge layer: K1-K7+K4.1+K4.2+K6.2 shipped
  - Video composition: V0-V15+V16 complete (18 starter compositions)
  - Realtime avatar: R0-R10+R6.1 complete (R-arc closed SESSION 157)
  - Workspace fabric: F0-F10 complete
  - Voiceover: VO.0-VO.2 shipped, VO.3-VO.6 queued

### CTO Survey of character-os (first findings)

The first CTO survey caught real signal beyond what was in CLAUDE.md:

- **Latest commits show engine-bridge per-workspace work in flight** —
  `7773016 feat(engine-bridge): EB.1 — EngineConnection model + migration + admin`
  and `2c87c88 docs(engine-bridge): EB.0 scope lock`. These post-date
  the SESSION 216 reframe and are the natural next slice.
- **Priority decision flagged as gating** — character-os SESSION 217
  needs Chris to pick: continue per-workspace engine config (ENGINE_BRIDGE_V1)
  vs advance VO.3 (`cta_swap`) to close the voiceover arc.
- **Recurring risk:** mock/real embedding-cache namespace collisions
  (SESSION 214) — already a regression class; needs a regression test
  before further integration work.
- **Architecture risk:** "feature belongs in the other repo" drift when
  bridging concerns blur — repeated theme in SESSION 215/216 handoffs.
- **Recommended next actions** include: lock the design doc (proposed
  `docs/design/ENGINE_BRIDGE_V1.md`), run inventory regen + doctor as
  a baseline pass, fix mock/real cache namespace, then proceed with the
  chosen slice.

Full survey: `Deliverable` id `2865c3d6-6b3a-43d0-ac69-460575868379`
in character-os workspace.

## What this session deliberately did NOT do

Per Rigby's "v0 stays thin" scoping:

- No live file-watching / auto-indexing
- No cross-repo semantic search / embedding aggregation
- No remote pgvector access (character-os's K2 stays isolated)
- No new PA tools — `deliverable_tool` already covers read access
- No retrofit of the 101 existing PA tools with a `repo=` param
- No portfolio dashboard

Each of these is on the v0 → v1 graduation list and is gated on v0
proving useful.

Also intentionally **paused** earlier in the session:

- **F2F.3** (HeyGen + Cartesia wiring) — Chris pulled back on adding
  new APIs until what's built is working. F2F.3 stays parked until
  spend justification is clear; F2F.0-F2F.2 mock-mode is still the
  state of that arc.

## Second repo: context-kit (added end of session)

Right after the character-os proof, context-kit got seeded as the
second repo to validate the schema isn't character-os-specific.

- Workspace id: `2ba6ee3b-2d45-4bdf-b02e-4e50fc979ba5`
- Repo Profile: `ba0f492a-6c50-45b9-abbf-eac40c57fb15`
- First snapshot: `fa17cd2e-125d-4f86-b61d-98071b93c734`
- First CTO Survey: `1b5762a2-6aec-4df9-944f-2901c0364661`
- Config: `config/external_repos/context-kit.json`

**Shape differs from character-os in useful ways** — proves the
schema generalizes:

- `repo_type: cli_tool` (not Django+SPA)
- `distribution: pypi, pypi_name: contextkit-ai, current_version: 0.15.0`
- Anchor docs follow the same pattern (`CONTEXT_KIT_WHAT_IT_IS.md` /
  `CONTEXT_KIT_INVENTORY.md` mirror the `PLATFORM_*` and
  `CHARACTER_OS_*` shape), plus the public-contract pattern guide at
  `cli/_pattern/0[1-8]_*.md`
- `bridge_relationship: null` (context-kit is a tool, not an engine
  with HTTP callers)
- New `fleet_role` block in metadata: `master_pattern_repo`,
  `consumed_by: [unified-donkey-betz, character-os, future apps]`
- New `constraints_rules` entry:
  `{type: "treat_as_public_contract", globs: ["cli/_pattern/0[1-8]_*.md"]}`
  — those files propagate to every adopting repo via `cp -r` or
  `context-kit init`. Captured as machine-readable so future tooling
  can enforce.
- Inventory command **ran successfully** end-to-end (`rc=0`) —
  context-kit is stdlib-only, so no venv-activation wrapper needed.
  Confirms the inventory cross-venv issue is repo-specific (character-os
  hit it because of Django/Celery deps), not a v0 design defect.

**CTO Survey of context-kit caught real signal** that wasn't obvious
from CLAUDE.md alone:

- 5 sessions in a row (SESSION_015 → 019) have deferred the same two
  pending docs (`CONTEXT_KIT_PIPELINE.md`, `CONTEXT_KIT_BEHAVIOR_LAYER.md`).
  The survey flagged this as accumulating handoff overhead and
  recommended a binary decision: write them now, or document the
  deliberate opt-out + teach doctor to suppress.
- Both spokesperson-corpus (SESSION_018) and fleet-network (SESSION_019)
  ship as **bundle pattern only** — CLI subcommand implementations
  are intentionally gated on a "second worked instance" before
  promotion. That gating decision is the canonical example of "don't
  promote a pattern to CLI until you've used it twice."
- Inventory ↔ git SHA drift check is queued: the inventory regen
  block doesn't embed the current HEAD, so `doctor` can't detect
  inventory staleness. Survey recommended low-friction fix.
- INVENTORY block currently reports 25 CLI subcommands, 30 test files,
  1076 tests collected, version 0.15.0.

Schema friction observed during seeding (folded into the runbook):

- The pattern guide files live at `cli/_pattern/` in context-kit
  itself, not `docs/docs-pattern/` as they do in adopting projects.
  Captured as `entry_points.pattern_guide_dir` +
  `entry_points.pattern_guide_files` rather than forcing all repos
  into the same anchor convention.
- The `bridge_relationship` field cleanly handled `null` (context-kit
  has no engine to reach). Confirms it's correctly optional.
- The `fleet_role` block is a context-kit-specific extension. The
  schema allows arbitrary keys in `repo_profile_metadata`, so this
  generalises naturally — each repo can declare its own role-shaped
  metadata.

Cost of context-kit survey: ~$0.01 (8217 tokens, gpt-5-mini).

## Loose ends for next session

> **Note on u-d-b:** u-d-b is *not* a fleet member and should not be
> registered as one. Rigby IS u-d-b's PA — its CLAUDE.md / PLATFORM_*
> anchors / handoffs are already injected into her system context.
> Registering u-d-b as a fleet repo would just duplicate native context.
> The fleet is for repos Rigby otherwise wouldn't have context for.

1. ~~**Inventory command needs the repo's own venv**~~ RESOLVED
   (follow-up commit, same session). `refresh_repo_context` now
   supports `inventory_venv` + `inventory_env_file` entry-points.
   When set, the command is wrapped in `bash -c "unset
   DJANGO_SETTINGS_MODULE PYTHONPATH PYTHONHOME VIRTUAL_ENV && source
   <env_file> && source <venv> && cd <cwd> && <cmd>"`. The unset is
   load-bearing: u-d-b's worker process exports its own Django state
   into subprocesses, which a sibling Django repo (character-os)
   inherits and fails on. character-os now runs inventory end-to-end
   (rc=0) with `inventory_venv=shell/.venv/bin/activate` +
   `inventory_env_file=.env` declared in its profile. Bare command
   path still works for stdlib-only repos (context-kit).
2. **COO + Editor surveys** — only CTO ran in v0. Worth running COO
   and Editor surveys against character-os to confirm the personas
   produce useful, distinct lenses.
3. **Initiatives.** v0 surveys produce `repo_survey` deliverables but
   don't yet auto-create Initiatives or Action Items in u-d-b's
   pipeline. The scoping target was "tasks land as Initiatives";
   that's a v0.5 follow-up.
4. **Active-repo conversation context.** Right now Claude Code's
   handshake is explicit ("we're in character-os now"). The
   conversation doesn't persist that pointer. v1 graduation item #1.
5. ~~**Re-run the character-os CTO survey after fixing inventory
   ingestion.**~~ DONE (follow-up commit, same session). Fresh CTO
   survey `c71aa5a4-819f-4f69-b002-1a4dd51d6f87` runs with live
   inventory output via the venv wrapper.

## Session 1119 close — full PR list + live UI verification

Nine PRs landed in this session, all on `main`:

| PR | Commit | What |
|---|---|---|
| #2104 | `8b9f7c27` | v0 framework — Repo Profile schema + register/refresh/survey commands |
| #2105 | `ce090a85` | inventory_venv + inventory_env_file wrapper |
| #2106 | `bac3f07e` | 10-repo catalog seed + Editor persona fix |
| #2107 | `ee486be0` | `extract_initiatives_from_survey` (read-only deliverable → actionable Initiative rows) |
| #2108 | `537d57a6` | doc state update — loose-ends matrix |
| #2109 | `445e5b56` | `active_repo_tool` PA tool (set/get/clear, 7-day Redis TTL) |
| #2110 | `6cf8fc0a` | auto-inject active repo context into PA system prompt (v1 graduation) |
| #2111 | `65014ad5` | lock fleet port allocation across 11 profiles |
| #2112 | `a58ba8ff` | vite dev base `/` so React Router matches |

Live UI test results (browser → React Command Center → PA chat):

| Step | Expected | Got |
|---|---|---|
| Set active repo to character-os | Confirm pointer | ✅ `Workspace fd91a85d-...` cached, 7-day TTL |
| Cold ask "what's urgent" | Cite top TRIAGE | ✅ `[character-os] Decide SESSION_217 priority: engine-config or VO.3` (urgency 0.95) |
| Multi-turn "30-min win" | Different TRIAGE without re-state | ✅ `[character-os] Regenerate and commit CHARACTER_OS_INVENTORY.md at HEAD` (urgency 0.85, impact 0.6) |
| Switch to mentorforge | Pointer moves | ✅ `Workspace 560c4125-...` |
| Clear scope | Drop pointer | ✅ confirmed |
| Cold u-d-b question after clear | Default platform tools, not deliverable_tool | ✅ status_snapshot + cockpit + ops |

The full multi-repo workflow is **live and working through the production React UI**. Rigby autonomously uses `active_repo_tool` when the user mentions scoping; pulls Repo Profile + Snapshot + TRIAGE Initiatives via the auto-injected system context; switches and clears scope cleanly.

### One pre-existing u-d-b bug Rigby surfaced

During the final cold-u-d-b-question test, Rigby reported 2 failures in `core.tasks.process_pa_chat_task` with `ProgrammingError`:

- `column chat_conversations.platform does not exist`
- `column chat_conversations.discord_user_id does not exist`

`ChatConversation` model declares both fields (Session 455 — cross-platform tracking) but the live DB is missing them — migration drift. **Queued as the first item for Session 1120.**

## How to use this

Runbook lives at [`docs/topics/multi-repo-management.md`](../topics/multi-repo-management.md).
Quick start:

```bash
# Register a new repo
$EDITOR config/external_repos/<repo_id>.json
.venv/bin/python manage.py register_external_repo --repo <repo_id>

# Refresh state
.venv/bin/python manage.py refresh_repo_context --repo <repo_id>

# Ask an agent persona to survey it
.venv/bin/python manage.py survey_external_repo --repo <repo_id> --agent cto
```

Ask Rigby for the latest state: she uses her existing `deliverable_tool`
with filters `workspace__name=<repo_id>` + `category` in
`{repo_profile, repo_snapshot, repo_survey}` to find everything.

## Cost ledger

| Operation | Tokens | $ |
|---|---:|---:|
| register character-os | 0 | $0.00 (no LLM) |
| refresh character-os (skip-inventory) | 0 | $0.00 (no LLM) |
| CTO survey character-os | 8,346 | ~$0.01 |
| register context-kit | 0 | $0.00 |
| refresh context-kit (full inventory) | 0 | $0.00 |
| CTO survey context-kit | 8,217 | ~$0.01 |
| COO survey character-os | ~7,500 | ~$0.01 |
| Editor survey character-os | 9,432 | ~$0.01 |
| Fresh CTO survey character-os (post-venv fix) | 8,727 | ~$0.01 |
| CTO survey mentorforge | ~8,000 | ~$0.01 |
| Extract initiatives (character-os CTO) | ~3,500 | ~$0.01 |
| Register × 10 new repos | 0 | $0.00 |
| Refresh × 10 new repos | 0 | $0.00 |
| Live UI test sequence (6 turns) | ~25,000 | ~$0.08 |
| **Total session 1119** | **~87,000** | **~$0.15** |

## Provenance

- Scoping rounds: 3 (file-federation v0 → asymmetric fleet → ops-wrapper
  multi-repo)
- Schema lock: with Rigby, pinned to deliverable metadata + workspace
  fields
- Conversation: `pa-d19c1674b936`
- Survey LLM: gpt-5-mini via `core.services.openai_client_factory.get_openai_client`
- Models touched: zero migrations
- Tests added: zero (v0 is end-to-end-tested manually via the demo)

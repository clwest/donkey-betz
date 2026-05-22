# Multi-Repo Management (Rigby's Project Fleet) — v0

**Session:** 1119
**Status:** v0 shipped 2026-05-21. Character-os is the first proof case.
**Scope lock:** [Rigby's scoping conversation](../handoffs/SESSION_1119_MULTI_REPO_V0.md)

> Rigby manages a fleet of laptop-local repos as projects. Each repo gets a
> ProjectWorkspace, a pinned Repo Profile deliverable, and append-only
> Snapshot + Survey deliverables. Agents work via context dict; Claude Code
> is the filesystem hands. No new API endpoints in v0 — everything reuses
> existing primitives.

---

## TL;DR

```bash
# 1. Author the repo profile JSON (one-time per repo)
$EDITOR config/external_repos/<repo_id>.json

# 2. Register the workspace + pinned Repo Profile deliverable
.venv/bin/python manage.py register_external_repo --repo <repo_id>

# 3. Refresh the snapshot (run at session boundaries or after big changes)
.venv/bin/python manage.py refresh_repo_context --repo <repo_id>

# 4. Run an agent survey against the latest snapshot
.venv/bin/python manage.py survey_external_repo --repo <repo_id> --agent cto
```

Rigby surfaces the result via her existing `deliverable_tool` —
filter by `workspace__name=<repo_id>` and `category` in
`{repo_profile, repo_snapshot, repo_survey}`.

---

## Why this exists

Rigby's existing `ProjectWorkspace` model was built as the "SKIN layer":
the boundary between AI and a real directory it operates on. It already
has `root_path`, `tech_stack` JSON, `entry_points` JSON, `protected_paths`,
and a full permission surface. Multi-repo v0 simply uses it for repos
other than u-d-b itself.

Constraint Chris locked: **no new APIs, just extend what u-d-b already has.**
This v0 ships:

- A canonical JSON schema for "Repo Profile" data
- Three management commands that wire profiles → workspaces → snapshots
  → surveys
- Zero migrations (everything maps onto existing fields)
- Zero new PA tools (Rigby's `deliverable_tool` + `workspace_tool` already
  cover read access)

The asymmetric architecture from the scoping conversation:
**Rigby knows about character-os, context-kit, and other apps;
they do not know about her.** Federation is one-way (Rigby reads outward
via file system); cross-repo runtime traffic (e.g. character-os's
`consult_engine` reaching u-d-b's PA over HTTP) is a separate product
layer and never touches the fleet primitives.

**u-d-b is not a fleet member.** Rigby IS u-d-b's PA — she runs inside
this repo, and CLAUDE.md / PLATFORM_WHAT_IT_IS / PLATFORM_INVENTORY /
the handoffs are already injected into her system context on every
conversation. The fleet is specifically for repos Rigby would not
otherwise have context for. Don't register u-d-b as a fleet member;
it's redundant and would just duplicate context she already has
natively.

## Current fleet members

As of the v0 seed batch (Session 1119), the fleet covers the laptop-local
code repos behind the 24/7 Global AI public catalog
(`src/lib/products.ts` in the `24-7-ai-global` repo):

| Repo | Role | Shape |
|---|---|---|
| `character-os` | Lab IX (Broadcast / Character OS) | Django + FastAPI + React monorepo |
| `context-kit` | Lab VIII (master pattern repo) | Python CLI tool (stdlib only) |
| `mentorforge` | Suite I (Mentor) | FastAPI + React (income lane) |
| `pitchdeckforge` | Suite II (Pitch) | FastAPI + React |
| `contract-concierge` | Suite III (Execute) | FastAPI + React |
| `dealflowtracker` | Suite IV (Grow) | FastAPI + React |
| `ai-content-studio` | Vertical V (Create) | Django + React + RN (39K LOC web) |
| `norman-handyman-mvp` | Vertical VII (Dispatch / JobFlow) | Django + Next.js + Expo + Neon |
| `sellerpilot` | Lab X (Optimize) | FastAPI + React (founder toolkit triplet) |
| `signal-studio` | Lab XI (Scout) | FastAPI + React (founder toolkit triplet) |
| `compliancesentinel` | Lab XII (Guard) | FastAPI + React (founder toolkit triplet) |
| `24-7-ai-global` | public marketing site | Next.js 16 + pnpm (canonical taxonomy) |

Not yet in the fleet (intentionally):

- **u-d-b** itself — Rigby's home; covered natively.
- **vehicle-match** — repo not present locally (`/Users/donkeyking/development/vehicle-match` missing). Has a GitHub remote at `clwest/vehicle-match`.
- **Engine-internal sub-products** in 24-7's `LAB` section that don't
  have their own repo: advisor-council, spider-network, rigby, boardroom,
  atelier — these all live INSIDE u-d-b and are surfaced publicly via
  product cards. Don't register them.
- **Channel publications** (Operator Edge, The Wire, The Dossier, The
  Almanac, Council Sessions) — these are publication products, not
  separate code repos.

---

## Concepts

### Repo Profile JSON

Lives at `config/external_repos/<repo_id>.json`. The canonical config for
an external repo: where it is, what tools it uses, what code Rigby is
allowed to read, what's protected, what constraints apply.

Required keys (validated by `register_external_repo`):

- `schema_version` — currently `1`
- `repo_id` — stable slug (e.g. `character-os`)
- `name` — workspace name (usually the same as repo_id)
- `description` — what the repo is
- `root_path` — absolute path to the repo
- `workspace_type` — `local` for filesystem repos
- `tech_stack` — JSON with `primary_language`, `backend`, `frontend`,
  `package_managers`, etc.
- `entry_points` — JSON with anchor doc paths, code/docs allowlists,
  inventory/health/start/test commands. Optional inventory wrapper
  fields:
  - `inventory_venv` — relative path to a venv activate script. If
    set, `refresh_repo_context` wraps the inventory command in
    `bash -c "unset DJANGO_SETTINGS_MODULE PYTHONPATH PYTHONHOME
    VIRTUAL_ENV && source <venv> && cd <cwd> && <cmd>"` so a sibling
    Django/FastAPI repo doesn't inherit u-d-b's Python state.
  - `inventory_env_file` — relative path to a `.env` file to source
    before activating the venv. Use when the target repo's
    `manage.py` depends on env vars (DJANGO_SETTINGS_MODULE,
    DATABASE_URL, etc.). Sources via `set -a && source <file> && set +a`.
  - Bare command (no venv, no env file) fits stdlib-only repos like
    context-kit.
- `protected_paths` — list of glob patterns Rigby/agents must not write
- `permissions` — `allow_file_write`, `allow_file_delete`,
  `allow_command_execution`, `allow_git_operations`,
  `allow_autonomous_writes`, `require_human_review`
- `repo_profile_metadata` — `constraints_text` (human-readable),
  `constraints_rules` (machine-readable), `bridge_relationship` (informational),
  `phase_status`, `session_log_pointer`, etc.

See `config/external_repos/character-os.json` for the canonical example.

### ProjectWorkspace (existing model)

`core.models_skin_layer.ProjectWorkspace`. Already shaped for "AI operates
on this directory." For external repos:

- `workspace_type='local'`
- `root_path=<absolute>` (must exist and be a git repo)
- `tech_stack`, `entry_points`, `protected_paths` populated from the
  Repo Profile JSON
- `is_active=False` — u-d-b's own workspace stays the user's active one;
  external-repo workspace_ids are passed explicitly via context

### Pinned Repo Profile deliverable

`category='repo_profile'`, `is_pinned=True`. Stores:

- Human-readable markdown in `content` (rendered from the JSON)
- Machine-readable structured config in `metadata`
- `last_refresh_at`, `last_git_head`, `last_branch`, `health_status`
  updated by `refresh_repo_context`

### Repo Snapshot deliverables (append-only)

`category='repo_snapshot'`, `is_pinned=False`. Created on each refresh.
Each row captures point-in-time state:

- Git HEAD, branch, dirty flag, recent commits
- Anchor doc head+tail
- Latest 1-2 handoff excerpts
- Inventory command output (if not skipped)

Retention: keep last 20 snapshots per workspace; older ones get
`status='archived'`. Never deleted.

### Survey deliverables

`category='repo_survey'`. Created by `survey_external_repo`. Bypasses
the u-d-b-aware agent_router tool loop on purpose — the survey is a
focused analysis pass over already-extracted snapshot + profile material,
not a new tool-using run.

Agent personas live in `core/management/commands/survey_external_repo.py`
as a dict: `cto`, `coo`, `editor` ship in v0. Add more personas by
editing that dict.

### Initiatives from survey findings

`extract_initiatives_from_survey` turns a survey's "Recommended next
actions" section into structured `Initiative` rows in u-d-b's existing
pipeline. Each Initiative is:

- `status=TRIAGE` (auto-created, awaiting operator review per Session 994)
- `target_workspace=<external repo's workspace>` — Rigby's existing
  initiative tools surface them scoped to that repo
- `created_by='multi-repo-survey'`
- `owner_agent=<survey persona, e.g. CTOAgent>`
- `parent_topic='repo:<repo_id>'`
- scored on `impact_score`, `urgency`, `confidence` (LLM-estimated 0-1
  from survey text; defaults to 0.5 when survey gives no signal)
- name format: `[<repo_id>] <action title> — <YYYY-MM-DD>` for uniqueness

The extract command makes one gpt-5-mini call in JSON-object mode
against the survey's `content` and parses the result. The survey's
`metadata.auto_extracted` field is updated with the created Initiative
IDs for traceability.

```bash
# Extract from a specific survey deliverable
python manage.py extract_initiatives_from_survey --deliverable <uuid>

# Or by repo + agent (uses latest survey)
python manage.py extract_initiatives_from_survey --repo <repo> --agent cto

# Preview without writing
python manage.py extract_initiatives_from_survey --repo <repo> --agent cto --dry-run

# Cap how many to create (defaults to 7)
python manage.py extract_initiatives_from_survey --repo <repo> --agent cto --max 5
```

---

## Adding a new repo

1. **Author the profile JSON.** Copy
   `config/external_repos/character-os.json` and edit:
   - `repo_id`, `name`, `description`, `root_path`
   - `tech_stack` — match the repo's actual stack
   - `entry_points.anchor_*` — point at the repo's narrative + runtime
     anchors (CHARACTER_OS_WHAT_IT_IS / PLATFORM_WHAT_IT_IS pattern)
   - `entry_points.code_allowlist` — directories Rigby/agents can read
   - `entry_points.inventory_command` + `inventory_cwd` — how to
     regenerate the runtime anchor
   - `entry_points.inventory_venv` + `inventory_env_file` (optional)
     — if the inventory command needs a venv activate or `.env`
     sourcing (Django/FastAPI/etc.), declare them and the refresh
     command will wrap with `bash -c`. Skip both for stdlib-only repos.
   - `entry_points.test_commands` / `start_commands` — runbook helpers
   - `protected_paths` — env files, secrets, node_modules, .git, etc.
   - `permissions` — typically `allow_file_write=true`,
     `allow_file_delete=false`, `allow_autonomous_writes=false`
   - `repo_profile_metadata.constraints_text` + `constraints_rules` —
     repo-specific rules (e.g. "do not modify u-d-b from this repo")
   - `repo_profile_metadata.bridge_relationship` — set if the repo
     reaches u-d-b (or any other engine) via HTTP; informational only

2. **Register.** Validates the JSON, the root path, and the git repo.
   Creates workspace + pinned Repo Profile deliverable.

   ```bash
   .venv/bin/python manage.py register_external_repo --repo <repo_id>
   .venv/bin/python manage.py register_external_repo --repo <repo_id> --dry-run  # preview
   .venv/bin/python manage.py register_external_repo --repo <repo_id> --force    # update existing
   ```

3. **First refresh.** Captures git state + anchor docs + handoffs.

   ```bash
   .venv/bin/python manage.py refresh_repo_context --repo <repo_id>
   .venv/bin/python manage.py refresh_repo_context --repo <repo_id> --skip-inventory  # if the repo's venv isn't active
   ```

4. **First survey.** Optional but recommended. Costs ~$0.01 per survey.

   ```bash
   .venv/bin/python manage.py survey_external_repo --repo <repo_id> --agent cto
   ```

---

## Routine workflow

### At the start of a session in u-d-b

If you're working on something that touches an external repo's
expectations of u-d-b:

```bash
# Refresh that repo's context so Rigby sees today's state
.venv/bin/python manage.py refresh_repo_context --repo character-os
```

### At the start of a session in another repo (e.g. character-os)

Tell Rigby explicitly:

> "We're in `character-os` (root `/Users/donkeyking/development/character-os`)
> for this conversation. Load the workspace's Repo Profile + latest
> Snapshot + open initiatives."

Rigby uses her existing `workspace_tool` + `deliverable_tool` to load
the context. The active workspace stays "Donkey Betz" globally; the
"working repo" is a soft context for this conversation only.

### When something major changes in an external repo

Refresh the snapshot before continuing the session. Snapshots are
cheap (no LLM cost — just git + file reads).

### When you want fresh agent analysis

```bash
.venv/bin/python manage.py survey_external_repo --repo <repo_id> --agent cto
.venv/bin/python manage.py survey_external_repo --repo <repo_id> --agent coo
.venv/bin/python manage.py survey_external_repo --repo <repo_id> --agent editor
```

Each survey is a separate deliverable in the workspace; Rigby can read
them all.

---

## Constraints + safety

- **No remote pgvector queries.** Each repo's pgvector (if any) stays
  isolated. v0 federates at the file layer only.
- **No symlink following.** Reads/greps that hit a symlink are rejected.
- **No write primitives shipped.** Claude Code is the only filesystem
  writer; Rigby orchestrates but never writes.
- **`allow_autonomous_writes=False`** for external repos by default —
  only explicit Claude Code sessions should produce deliverables for them,
  never scheduled agent rotations.
- **Cross-repo write boundaries** are repo-declared. character-os's
  Repo Profile records the "do not modify u-d-b" rule as both
  `constraints_text` (markdown for prompts) and `constraints_rules`
  (machine-readable for future enforcement).

---

## What v0 deliberately does NOT do

Per Rigby's scoping (the v0 → v1 graduation list):

1. **No live file-watching / auto-indexing.** Manual refresh only.
2. **No cross-repo semantic search.** No embeddings of anchor docs into
   pgvector yet.
3. **No remote pgvector access.** Each repo's vector store stays isolated.
4. **No new PA tools.** `deliverable_tool` + `workspace_tool` already
   cover read access; v0 ships only management commands.
5. **No retrofit of the 101 PA tools** with `repo=` params.
6. **No portfolio dashboard.** Not worth building until 3+ repos are
   actively managed.

Anything from that list graduates when v0 proves it's worth scaling up.

---

## v0 → v1 graduation triggers

Rigby's locked list:

1. Per-repo conversation threads + auto-context switching
2. Standardized JSON refresh runbook with structured outputs
3. Safe read-only repo file access tool for agents (still no writes)
4. Workspace-linked doc embedding (RAG) for anchors
5. Typed repo metadata columns on ProjectWorkspace
6. Constraint enforcement / governance
7. Portfolio view across repos

---

## File map

| Path | Purpose |
|---|---|
| `config/external_repos/<repo>.json` | Repo Profile config (canonical) |
| `core/management/commands/register_external_repo.py` | Profile → Workspace + pinned Deliverable |
| `core/management/commands/refresh_repo_context.py` | Snapshot + Repo Profile metadata refresh |
| `core/management/commands/survey_external_repo.py` | Agent persona over latest snapshot |
| `core/management/commands/extract_initiatives_from_survey.py` | Survey → Initiative rows (TRIAGE, target_workspace scoped) |
| `core/models_skin_layer.py` | `ProjectWorkspace` (existing — no migrations) |
| `core/models_deliverables.py` | `Deliverable` (existing — no migrations) |
| `core/services/deliverable_factory.py` | `create_deliverable` (the only deliverable creation path) |

---
title: "Workspaces and scope — narrative (batch P, draft)"
status: draft (batch P of Session 1162 corpus-narrative program — Chris/Rigby review pending)
last_updated: 2026-05-26
session: 1162
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158) + EDITING_GUARDRAILS v1
companion_docs:
  - docs/topics/frontend.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/FRONTEND.md
  - docs/narratives/STRATEGY_247_GLOBAL_AI.md
  - docs/PLATFORM_INVENTORY.md
  - docs/narratives/EDITING_GUARDRAILS.md
provenance_confidence: HIGH (anchored to code paths + PLATFORM_INVENTORY 2026-05-26 + named session handoffs)
provenance_note: First-draft narrative addressing the workspace coverage gap identified by Chris in Session 1162. Prior narratives reference "workspace" 60+ times across 9 files but no single doc covers what a workspace IS (the model), how one gets created (5 paths), what scoping means (mode discriminator, FK propagation), or the lifecycle (is_active boolean + WorkspaceConfig status enum — two separate state machines). Two drifts surfaced by the survey are flagged inline as Open Questions §6 rather than restated as canonical. Counts anchored to PLATFORM_INVENTORY 2026-05-26 (git HEAD 25b2198a). Status is "draft pending Rigby review" per the co-authored doc pattern from Session 1124.
---

# Workspaces and scope

> **What this doc is.** Workspaces are the platform's primary
> unit of scope. They bound which files an agent can write to,
> which initiatives a PA query returns, which deliverables show
> up in a list, and which `LLMCallLog` rows (in the planned
> future, see §6) attribute their cost. They also define what
> "workspace mode" means for Rigby. Yet no single doc explains
> what a workspace *is* — the existing narratives treat it as
> assumed vocabulary.
>
> This narrative covers: the underlying model (`ProjectWorkspace`,
> not `Workspace` — naming drift worth knowing), the separate
> `WorkspaceContext` cache, how AssistantProfile attaches PA to a
> workspace, every code path that creates one, the two distinct
> lifecycle state machines, and how `workspace_id` flows through
> a request from the frontend down to a tool argument. The point
> is to let future-Claude or future-Chris answer "where does
> workspace scope come from?" without code spelunking.
>
> **Companion to FRONTEND (G), PERSONAL_ASSISTANT (D), and
> AGENTS_AND_AUTONOMY (A).** FRONTEND covers the 5-tab UI shell
> built on top of a workspace; D covers Rigby's global-vs-workspace
> mode discriminator; A covers what "workspace-aware" means for
> agents. This doc covers the substrate underneath all three.

---

## §1 What this is

A workspace is a per-user, optionally-active scope. It carries:

1. A **filesystem boundary** (`root_path`) where agents are
   allowed to write code or content.
2. A **permission grid** (four boolean gates — `allow_file_write`,
   `allow_file_delete`, `allow_command_execution`,
   `allow_git_operations`) that the executor checks before any
   destructive action.
3. A **PA scoping hook** — when `AssistantProfile.workspace` is
   set, the PA operates in workspace mode and workspace-scoped
   tools (initiative_list, deliverable_list, file_tool) only
   return rows tied to that workspace.
4. A **context-injection key** — `workspace_id` threads through
   request → PA → agent context → tool argument so downstream
   work knows what scope to honor.

Workspaces are **opt-in**. There is no signal that auto-creates a
workspace on user signup; a user remains in "global mode" until
they create one (via a template, a PA tool call, an agent service
handler, or a backfill mgmt command). The "Donkey Betz" workspace
referenced in operator memory is a **convention**, not a
hardcoded singleton — it's the default parameter on the backfill
command (`backfill_deliverable_workspaces --workspace "Donkey Betz"`)
and a brand-identity reference, not a row guaranteed to exist.

The platform also caches a separate `WorkspaceContext` per
workspace — a read-only snapshot of the project's file tree, key
files, coding patterns, and dependencies. Agents use it to know
*where* to write generated code (Session 695). `WorkspaceContext`
is rebuilt from disk on rescan; `ProjectWorkspace` persists user
intent.

---

## §2 Vocabulary

| Term | Definition |
|---|---|
| **`ProjectWorkspace`** | The Django model that backs the concept (`core/models_skin_layer.py:31`). Fields include `user` FK, `root_path`, `workspace_type`, the four permission booleans, statistics counters, and `is_active`. Despite the prose-level naming "workspace," the code class is `ProjectWorkspace` — keep this in mind when grepping. |
| **`WorkspaceContext`** | The companion cache model (`core/models_skin_layer.py:516`). `OneToOneField` to `ProjectWorkspace`. Carries `file_tree`, `key_files`, `coding_patterns`, `dependencies`, `import_aliases`, `directory_purposes`, statistics, and scan metadata. Read-only from the agent's perspective; rebuilt on rescan. |
| **`AssistantProfile.workspace`** | The optional FK on `AssistantProfile` (`core/models_assistant_profile.py`) that scopes Rigby to a single workspace when set. `null=True` — most profiles are workspace-free and PA operates in global mode. |
| **Workspace mode (PA)** | The PA mode discriminator. `global` = no workspace_id; `workspace` = explicit context (workspace_id from request, `AssistantProfile.workspace`, or a workspace-aware UI store). Workspace-scoped tools honor it. Covered in narrative D's vocabulary table. |
| **`workspace_type`** | Enum on `ProjectWorkspace`: `local`, `git_remote`, `sandbox`, `container`. Distinguishes "a local-disk project I own" from "a sandboxed scratch area" from "a containerized environment." Permission gates default differently per type. |
| **Permission grid** | The four boolean fields on `ProjectWorkspace` (`allow_file_write`, `allow_file_delete`, `allow_command_execution`, `allow_git_operations`) plus `allow_autonomous_writes` (Session 327, controls whether autonomous agents can target this workspace as fallback). The executor checks these before acting. |
| **`is_active` (Session-1034 self-healing)** | Single-active-per-user constraint. `unique_active_workspace_per_user` index on `(user, is_active)`. `ProjectWorkspace.save()` deactivates all other rows for the same user when one is set active. Session 1034 added path self-healing for the case where a developer syncs DB from prod and the macOS path no longer resolves. |
| **`WORKSPACE_AWARE_AGENTS`** | The constant tuple in `core/epa_handlers_tools.py:~3873` listing the agents that can write files into a user workspace via `BaseAgent.execute_with_workspace()`. As-of PLATFORM_INVENTORY 2026-05-26: 20 agents. Treat the constant as canonical; this prose may drift. |
| **`WorkspaceConfig` status** | A separate model (`core/models_workspace_templates.py:125`) attached to `ProjectWorkspace`. Carries `status` enum: `setup`, `active`, `paused`, `archived`. Distinct from `ProjectWorkspace.is_active` — see §3 milestone 4 for why two state machines exist. |
| **`WorkspaceTemplate`** | The provisioning shape (`core/models_workspace_templates.py:97`). `.provision(user, name, description)` creates a `ProjectWorkspace` + `WorkspaceConfig` pair. Triggered by template-driven onboarding (e.g., "Create Newsletter Business"). |
| **`workspace_id` propagation** | The string-key flow: HTTP request → PA entry point → user_context → agent context → tool arguments. Five representative call sites are listed in §3 milestone 5. PA *injects* `workspace_id` into tool calls if the tool needs it and the caller didn't include it. |
| **Workspace path self-healing (Session 1034)** | `_get_workspace_for_skin_layer()` (`core/services/...`) auto-detects stale macOS paths in the DB, recomputes from `__file__`, and updates the row. Handles the Railway-vs-local mismatch when a developer's DB gets synced from prod. Covered in narrative N. |

---

## §3 Milestone timeline

### Milestone 1 — `ProjectWorkspace` model and the permission grid

**Code anchor:** `core/models_skin_layer.py:31-225`.

The foundational decision was to express workspace boundaries as
*data*, not policy buried in code. `ProjectWorkspace` carries
`root_path` (filesystem boundary), `workspace_type` (intent),
and four explicit permission booleans (`allow_file_write`,
`allow_file_delete`, `allow_command_execution`,
`allow_git_operations`) plus `allow_autonomous_writes` (the
Session 327 add for "treat this as fallback write target when an
agent has no explicit workspace context"). An executor that
wants to do anything destructive must first consult this grid.

The `Meta` block carries the `unique_active_workspace_per_user`
constraint — only one row per user can be `is_active=True`. The
custom `save()` enforces it: setting one row active deactivates
all others. This is the simplest possible answer to "which
workspace is current?" — there's exactly one.

### Milestone 2 — `WorkspaceContext` as a cached project understanding (Session 695)

**Code anchor:** `core/models_skin_layer.py:516-723`.

The original `ProjectWorkspace` row tells you the boundary; it
doesn't tell you anything about *what's inside*. Session 695 added
`WorkspaceContext` as a cached snapshot of the project structure
itself — file tree, key files agents should know about, coding
patterns (naming conventions, framework detection), dependencies
by framework, import aliases (`@/` → `src/`-style mappings), and
semantic directory purposes (`models/` = "Django models live
here").

The separation is intentional: `ProjectWorkspace` persists user
intent (permissions, identity); `WorkspaceContext` is regenerable
from disk on rescan. An agent generating a new component reads
`WorkspaceContext.directory_purposes` to figure out where the
component should land. The cache becomes stale; the rescan command
exists to refresh it.

### Milestone 3 — `AssistantProfile.workspace` as the PA scoping hook

**Code anchor:** `core/models_assistant_profile.py:90-200`, FK at lines 122-129.

Before this hook existed, the PA's "workspace mode" was inferred
from request payload alone. Attaching workspace as an `AssistantProfile`
FK made it a *persistent* per-user preference: a user with a default
workspace gets workspace-mode automatically without needing to set
the context per turn.

The FK is `null=True`. Most profiles are workspace-free; PA stays
in global mode. When set, `AssistantProfile.has_workspace_scope()`
returns `True` and tools honor it. Per narrative D's rule (rule 5
in EDITING_GUARDRAILS: should not infer scope from text, only from
explicit context), the PA never derives workspace_id from prompt
content — only from this FK, the request payload, or a frontend
workspace-aware UI store.

### Milestone 4 — Two lifecycle state machines (`is_active` boolean and `WorkspaceConfig.status` enum)

**Code anchor:** `ProjectWorkspace.is_active` at `core/models_skin_layer.py`; `WorkspaceConfig.status` at `core/models_workspace_templates.py:155-160`.

A reader debugging "is this workspace alive?" needs to know there
are *two* state machines.

- **`ProjectWorkspace.is_active`** (boolean) — the "is this the
  one workspace I'm using right now?" toggle. There's no
  `archived_at` timestamp; no soft-delete. Either it's currently
  active for the user, or it isn't.

- **`WorkspaceConfig.status`** (enum: `setup`, `active`, `paused`,
  `archived`) — the business-state enum for template-provisioned
  workspaces. A workspace can be `is_active=True` (the user's
  current focus) while its `WorkspaceConfig.status='paused'`
  (paused as a business unit). The two are orthogonal.

The drift trap: someone writes a query that filters
`ProjectWorkspace.is_active=True` and expects "non-archived"
workspaces — but the `WorkspaceConfig` archival state isn't on
that field. The remediation: name which state machine you mean.
If you can't, check `core/models_workspace_templates.py:125-248`
to confirm which one belongs to your case.

### Milestone 5 — `workspace_id` propagation through a request

The string `workspace_id` threads through five layers. Each is a
debugging entry point when scope feels wrong:

1. **HTTP request** — `core/views_personal_assistant.py:71`:
   `workspace_id = request.data.get('workspace_id') or workspace_id`.
   Frontends can pass `workspace_id` in the PA chat JSON body.

2. **PA context extraction** —
   `core/services/unified_pa_entrypoint.py:1052-1078`:
   `_extract_workspace_id_from_context(user_context)`. The PA
   verifies the workspace belongs to the user and injects
   `context['workspace_id']` for the rest of the request.

3. **Agent context threading** — workflow/sub-task delegations
   copy `workspace_id` into `subtask_context` when delegating. A
   parent agent's workspace flows to its children.

4. **Tool argument injection** —
   `core/services/unified_pa_entrypoint.py:1550-1567`: the PA
   *silently* injects `workspace_id` into tool calls (e.g.,
   `deliverable_tool`, `work_tool`) when the model omitted it
   but the workspace scope is known. The tool author doesn't
   need to plumb the arg manually.

5. **Per-agent retrieval** — `distribution_agent.py` and the
   workspace-aware agents call
   `ProjectWorkspace.objects.filter(workspace_id=...)` to load
   workspace-specific tone/audience/permissions for their LLM
   pipeline.

**When scope feels wrong** — debug in this order: did the
frontend send `workspace_id`? Did the PA extract it into
`user_context`? Did the agent receive it in `subtask_context`?
Did the tool receive it as an argument? At each layer, the
field is named `workspace_id` consistently.

### Milestone 6 — `WORKSPACE_AWARE_AGENTS` and `BaseAgent.execute_with_workspace()`

**Code anchor:** `core/epa_handlers_tools.py:~3873-3907` (constant); `core/agents/base_agent.py` (method).

Most agents do not write files to a workspace; they return
answers, generate content, or update DB rows. The agents that
*do* write — full-stack developers, code generators, content
writers, technical document agents, etc. — are listed in
`WORKSPACE_AWARE_AGENTS`. As-of PLATFORM_INVENTORY 2026-05-26 the
constant carries 20 entries. The constant is canonical; this
narrative will not list them (rule 3 of EDITING_GUARDRAILS).

The pattern: a workspace-aware agent inherits `BaseAgent`, which
provides `execute_with_workspace(task, workspace_id, …)`. This
method resolves the workspace, checks the permission grid,
executes the agent's normal `execute()`, then writes the produced
artifacts to `workspace.root_path` while honoring the permission
booleans. Agents not in the list have no such method; calling it
on them is a programming error.

### Milestone 7 — Frontend `workspaceStore` and the 5-tab UI shell

**Code anchor:** `frontend/src/stores/workspaceStore.ts` (Zustand store); `frontend/src/pages/WorkspacePageNew.tsx` (5-tab orchestrator).

The browser side of workspace context is a single-field Zustand
store: `activeWorkspace: WorkspaceInfo | null`. `WorkspacePageNew`
sets it when the user picks a workspace; `GlobalPADock` reads it
to include in PA chat context. The store has no persistence layer
— state survives only the tab session. Persistent default is
`AssistantProfile.workspace` on the backend.

Narrative G (FRONTEND) covers the 5-tab structure
(`home / work / build / intelligence / system`); this milestone
exists to name the *store* as the canonical frontend handle for
workspace identity. Components that need to know "which workspace
am I rendering?" subscribe to `workspaceStore.activeWorkspace`,
not to per-component props.

### Milestone 8 — Creation paths (5 of them)

**Code anchors:** see table.

| Path | Trigger | Entry point |
|---|---|---|
| **Template provision** | User selects a template (e.g., "Newsletter Business") | `WorkspaceTemplate.provision(user, name, description)` — `core/models_workspace_templates.py:97-122` |
| **PA tool / service handler** | PA tool call (`td_handlers_agents` action='create') or agent request | `core/services/td_handlers_agents.py:1183-1200` |
| **Engineering scaffold** | An agent is asked to operate on / scaffold a new project | `core/services/claude_code_engineer.py:338` |
| **Backfill management command** | Operator runs `python manage.py backfill_deliverable_workspaces --workspace "Donkey Betz"` | `core/tasks.py:12556-12579` |
| **User signup** | (not implemented) — there is *no* signal that auto-creates a workspace on registration. Users start in global mode. | n/a |

Sessions tied to these paths: 327 (`allow_autonomous_writes`),
695 (`WorkspaceContext`), 1034 (path self-healing), 1100 (5-tab
UI consolidation), 1091 (`SESSION_1091_OPS_HARDENING_AND_WORKSPACE_FLOW.md`).

---

## §4 What came of it

Workspaces gave the platform a clean answer to four problems
that earlier versions handled implicitly:

- **What can an agent write to?** Before workspaces, agents had
  ambient file-system access scoped only by the process. The
  permission grid + `root_path` made the answer explicit and
  auditable.

- **Which initiatives / deliverables does PA return?** Before
  the `AssistantProfile.workspace` hook, every PA query was
  effectively global. Setting a default workspace narrows the
  list to "what's mine in this scope" without per-turn config.

- **Where does generated code land?** `WorkspaceContext`'s
  `directory_purposes` map lets an agent that's writing, say, a
  Django view, pick the right `views_*.py` file without a
  human spelling out the convention.

- **Who pays for the LLM call?** *Currently aspirational.*
  Session 1137 Decision 9 names per-workspace cost-attribution
  rules; the matching code (a `workspace` FK on `LLMCallLog`)
  does not exist as of 2026-05-26 — see §6 Open Questions.

The pattern that matters across all four: workspace is *named
context*. The platform doesn't have to guess "which scope is
this?" because the user, the PA, and the agents are all
referencing the same `ProjectWorkspace.id`.

---

## §5 Current state snapshot

As-of PLATFORM_INVENTORY 2026-05-26 (git HEAD `25b2198a`):

- **Models:** 3 core — `ProjectWorkspace`, `WorkspaceContext`,
  `WorkspaceConfig`, plus the `AssistantProfile.workspace` FK.
- **Creation paths:** 4 implemented + 1 explicitly absent (no
  auto-create on signup).
- **Workspace-aware agents:** 20 in `WORKSPACE_AWARE_AGENTS`
  (constant is canonical; the count may move).
- **Frontend store:** `workspaceStore` carries `activeWorkspace`
  only; no persistence.
- **PA mode discriminator:** `global` vs `workspace` resolved
  from explicit context — request payload, profile FK, or a
  workspace-aware UI surface. Never inferred from prompt text
  (rule from narrative D).
- **Permission grid:** 4 boolean fields + `allow_autonomous_writes`.
  Defaults differ by `workspace_type`.

---

## §6 Open questions

Each item below is a *gap* in the implementation or in the docs,
flagged here per EDITING_GUARDRAILS rule 5 ("should not; if it
does, check ___").

### 6.1 `LLMCallLog.workspace` FK — claimed in STRATEGY but not implemented

The STRATEGY_247_GLOBAL_AI narrative (Session 1137 Decision 9)
names "`LLMCallLog.workspace` FK + `ExternalAPICallLog`" as part
of the per-workspace cost-attribution mechanism. Verified
2026-05-26: `core/models_llm_routing.py` has zero workspace
references. The cost-attribution rule is **aspirational** —
correctly anchored in Decision 9 but not yet plumbed into the
data model.

**Remediation pointer:** if you're debugging cost-by-workspace
and the data isn't there, the FK hasn't been added. The current
correlation path is `LLMCallLog.agent_name + user + trace_id` →
PA request → `request.user_context['workspace_id']`. That works
for forensic audit; it does not work for runtime per-workspace
budget enforcement.

### 6.2 Fleet "scoped workspace bootstrap" per persona slug — also aspirational

STRATEGY narrative references "scoped workspace bootstrap" as
part of the soft-cut persona-slug model. Code survey 2026-05-26:
no implementation found. `FleetServiceIdentity` /
`FleetServiceKey` handle HMAC identity only;
`WorkspaceTemplate.provision()` handles template-based setup but
not per-persona bootstrapping.

**Remediation pointer:** if a future PR adds fleet-persona →
workspace bootstrap, the natural home is `core/services/` next
to `fleet_routing.py`. Update this section + the STRATEGY
narrative when it lands.

### 6.3 No auto-workspace on signup — intentional or oversight?

There is no signal that creates a workspace on
`User.post_save`. Users land in global mode by default. This
might be intentional (users opt into projects via templates),
or it might be an oversight from the era when workspaces were
template-only. The narrative records the absence; the policy
call is open.

### 6.4 "Donkey Betz" workspace — convention vs row

Operator memory says "always assign workspace — default: Donkey
Betz." But there's no code that guarantees a Donkey Betz
workspace exists; the name is a backfill-command default and a
brand reference. If a fresh DB is bootstrapped and "Donkey Betz"
doesn't exist, the backfill will create one *if* invoked. Otherwise
no.

**Remediation pointer:** if you're following the memory rule and
the workspace lookup returns null, run
`python manage.py backfill_deliverable_workspaces` to materialize.

### 6.5 Two state machines (`is_active` vs `WorkspaceConfig.status`)

The orthogonality of `ProjectWorkspace.is_active` (boolean) and
`WorkspaceConfig.status` (enum) is correct but easy to miss. A
query that filters one and ignores the other will give the wrong
answer for half the cases. Possible cleanup: collapse to a single
state machine, or document why the split is permanent. Either
needs a Rigby call.

---

## §7 Source index (current handoffs)

- **Session 327** — `allow_autonomous_writes` added; workspaces
  as fallback write target.
- **Session 695** — `WorkspaceContext` cache model introduced
  (file tree + key files + coding patterns).
- **Session 1034** — workspace path self-healing
  (`_get_workspace_for_skin_layer()`).
- **Session 1091** — `SESSION_1091_OPS_HARDENING_AND_WORKSPACE_FLOW.md`,
  workspace flow hardening pass.
- **Session 1100** — 9-tab → 5-tab consolidation in the frontend
  workspace shell.
- **Session 1137** — Decision 9 names per-workspace cost-attribution
  as a constraint for SaaS launch. The `LLMCallLog.workspace` FK
  named here remains aspirational (§6.1).
- **Session 1158-1161** — narrative pilot established the
  template + EDITING_GUARDRAILS that this doc follows.

---

## §8 Canonical sources

This narrative is authoritative for:
- The vocabulary table in §2.
- The 5-path creation taxonomy in §3 milestone 8.
- The two-state-machine drift trap in §3 milestone 4.
- The two flagged drifts in §6.

This narrative is NOT authoritative for:
- **Counts** (workspace-aware agent count, total ProjectWorkspace
  rows, etc.) — see `PLATFORM_INVENTORY.md`. If an inventory
  count disagrees with prose here, inventory wins.
- **5-tab UI structure** — see narrative G (FRONTEND).
- **PA workspace mode discriminator** — see narrative D
  (PERSONAL_ASSISTANT).
- **Workspace-aware agent list** — see
  `core/epa_handlers_tools.py:WORKSPACE_AWARE_AGENTS` (constant
  is canonical).
- **Permission grid defaults per workspace_type** — see
  `core/models_skin_layer.py:31` (model definition is canonical).

---

## Draft notes (remove on lock)

- This is a **first draft** pending Chris + Rigby review per the
  Session 1124 co-authored doc pattern. Claude scaffolded the
  structure + anchored claims to code; Rigby's review will check
  voice, audience framing, and whether §6 drifts need separate
  PRs to fix vs. leave as Open Questions.
- Two STRATEGY narrative claims are flagged as drift in §6.1 +
  §6.2. If Rigby ratifies, the STRATEGY narrative should get a
  follow-on edit to mark those claims aspirational rather than
  current.
- Naming: "WORKSPACES_AND_SCOPE" picks up the framing that this
  doc is about *both* the concept (workspace) and the propagation
  pattern (scope). Open to renaming.
- Letter assignment: batch P (next available after the 15
  Session 1158 narratives A-O).

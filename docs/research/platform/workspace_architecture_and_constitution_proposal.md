# Workspace Architecture & Constitutional Placement — Proposal

**Session:** 2709 (architecture research only)
**Date:** 2026-07-08
**Status:** Research proposal — awaiting Chris's review
**Predecessor:** SESSION 2708 (`docs/research/platform/engineering_playbook_architecture_proposal.md`) — this proposal supersedes 2708's L1-L5 model with a workspace-first model surfaced by deeper evidence
**Author:** Claude (Opus 4.7, 1M context)
**Scope constraints:** Architecture research only. No code changes. No ADRs. No workspace deliverables. No Playbook authoring. This document is the sole artifact of the session.

---

## Executive Summary

**Question:** What is the Workspace intended to become?

**Answer surfaced by primary evidence:** The Workspace is intended to become **the multi-tenant creator/operator OS boundary** of Donkey Betz. Every organizational unit — a person's practice, a team's project, a customer's business, a domain of work (like Architecture & Research), a session-scoped experiment — is a Workspace. Each workspace is a self-contained *AI-augmented operating unit* with its own agents, spiders, pipelines, code, content, decisions, governance, and audit trail.

**Governance is not a workspace category. Governance is a capability that operates inside every workspace.** The Cycle 0/1 constitutional content living in the "Architecture & Research" workspace is not a special governance-workspace — it is a workspace whose active use-pattern is governance-only. In the multi-tenant future, every customer workspace will need its own governance surface (customer's ADRs, customer's ratification records, customer's constitution).

**Consequence for the Engineering Playbook:** The Playbook is not a document that "lives in the workspace vs repo" — it is a **workspace-level constitutional artifact** for the Donkey Betz operating workspace (currently `a9a16593-…` for Architecture & Research; conceptually distinct from Donkey Betz's own operating workspace `b4503364-…`). Its physical storage (workspace deliverable + RAG mirror + repo anchor) is a solved question once the architectural framing is right. The novel question the Playbook raises is: **which workspace owns it?** — because different answers imply radically different multi-tenant futures.

**Recommendation:** Adopt the *Workspace-as-Operator-OS* model. Treat Deliverables (including governance ones) as workspace-owned outputs. Treat the repository as the shared substrate (code, deployment, cross-workspace platform primitives, and Layer-2 operational documentation). Treat RAG as the derived retrieval layer with authority-aware precedence. Adopt one hybrid pattern (KFI-5 anchor) for every workspace-canonical L1 artifact — *including* the Engineering Playbook. But before that placement question can be settled, resolve: **is the Playbook a platform-wide artifact (belongs to no customer workspace, sits at repo layer under governance-aware retrieval) or a per-workspace artifact (each customer gets their own)?** Evidence favors *platform-wide with per-workspace forks* (see §10.5).

---

## Table of contents

1. [Evidence base](#1-evidence-base)
2. [Current state — what a Workspace actually is](#2-current-state--what-a-workspace-actually-is-today)
3. [Architectural analysis — what problem is it solving?](#3-architectural-analysis--what-problem-is-the-workspace-actually-solving)
4. [Knowledge layer model](#4-knowledge-layer-model)
5. [Workspace object model — what belongs inside?](#5-workspace-object-model--what-belongs-inside)
6. [Workspace vs Repository](#6-workspace-vs-repository)
7. [Governance model](#7-governance-model)
8. [Future evolution — multi-tenant, multi-workspace](#8-future-evolution--multi-tenant-multi-workspace)
9. [Playbook relationship (deferred, per session mission)](#9-playbook-relationship-deferred-per-session-mission)
10. [Self-critique](#10-self-critique)
11. [Risks](#11-risks)
12. [Unknowns](#12-unknowns)
13. [Recommendation](#13-recommendation)
14. [Implementation implications (no steps — implications only)](#14-implementation-implications-no-steps--implications-only)

---

## 1. Evidence base

Sources for this proposal are exclusively primary — repository code, ORM introspection, DB counts, existing runtime, and Cycle 1A ratified artifacts. Every claim in this document is traceable to one of the queries recorded in §1.1–§1.4 below.

### 1.1 Repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `309f85ee` (post-2707 close cascade) |
| Working tree | clean |
| Recent activity | Session 2708 delivered `docs/research/platform/engineering_playbook_architecture_proposal.md` (previous proposal); no code or workspace changes since. |

### 1.2 Model-layer evidence (ORM introspection)

**Critical discovery:** there is no model literally named `Workspace`. The workspace concept is decomposed across 8 models in the `core` app:

| Model | Table | Role |
|---|---|---|
| `core.ProjectWorkspace` | `core_project_workspaces` | The workspace entity (47 fields; owns everything below) |
| `core.WorkspaceConfig` | `workspace_configs` | Per-workspace config: template, pipeline, agents, spiders, deliverable categories, quotas, governance_mode |
| `core.WorkspaceContext` | `workspace_contexts` | Per-workspace codebase snapshot: file_tree, key_files, dependencies, LOC |
| `core.WorkspaceTemplate` | `workspace_templates` | Reusable workspace shape (newsletter/leadgen/research/custom) |
| `core.WorkspaceOperation` | `core_workspace_operations` | Audit log: every AI file write, command exec, git op |
| `core.WorkspaceTrigger` | `core_workspace_triggers` | Pub/sub events routed into workspace-scoped agent actions |
| `core.WorkspaceTriggerConfig` | `core_workspace_trigger_configs` | Trigger match/route rules |
| `core.WorkspaceProject` | `core_workspace_projects` | Sub-projects within a workspace (repo, envs, preview envs) |

**ProjectWorkspace fields (47 total, grouped):**

- **Identity**: `id`, `name`, `description`, `workspace_type`, `is_active`, `user (FK→UnifiedUser)`, `created_at`, `updated_at`
- **Code home**: `root_path`, `git_remote_url`, `tech_stack (JSON)`, `entry_points (JSON)`, `current_branch`, `protected_paths (Array)`
- **Autonomy gates**: `allow_file_write`, `allow_file_delete`, `allow_command_execution`, `allow_git_operations`, `require_human_review`, `allow_autonomous_writes`
- **Telemetry**: `last_operation_at`, `total_operations`, `total_files_written`, `total_commits`
- **Reverse relations (23 total)**: `chat_conversations`, `opportunities`, `opportunity_tasks`, `blogs`, `content_channels`, `podcast_shows`, `initiatives`, `agent_initiative_affinities`, `deliverables`, `content_packets`, `conceptforge_runs`, `f2f_sessions`, `vip_invites`, `assistant_profiles`, `config` (1:1), `pipeline_runs`, `operations`, `context` (1:1), `triggers`, `projects`, `images`, `videos`, `audio`

**Every one of these 23 relations means "belongs to a workspace" is the multi-tenant boundary of the entire platform.** Not just docs. Not just governance. Every creative artifact, every AI execution, every audit row, every trigger, every media asset.

### 1.3 Runtime state (12 workspaces exist)

| # | Name | Type | Root | Active | Owner | Total ops |
|---|---|---|---|---|---|---|
| 1 | chris-personal | local | `/Users/donkeyking/development/unifi…` | ❌ | chris | 414 |
| 2 | System Autonomous Workspace | local | `/Users/donkeyking/development/unifi…` | ✅ | system_autonomous | 688 |
| 3 | Agent-Testing | sandbox | `/app/workspaces/agent-testing` | ❌ | chris | 33 |
| 4 | Session 1171 — ML Queue Flood + Auth Middleware | sandbox | `/app/workspaces/session-1171-…` | ❌ | chris | 18 |
| 5 | Session 1172 — Rigby Live Status in Chat UI | sandbox | `/app/workspaces/session-1172-…` | ❌ | chris | 44 |
| 6 | Session 1173 — PgBouncer in front of Postgres | sandbox | `/app/workspaces/session-1173-…` | ❌ | chris | (few) |
| 7 | Local QA — Platform Test Pass 1 (Session 1174…) | sandbox | `/app/workspaces/local-qa-…` | ❌ | chris | 467 |
| 8 | Donkey Betz | sandbox | `/Users/donkeyking/development/unifi…` | ❌ | chris | 2,545 |
| 9 | Session 1231 E2E — business_research verification | sandbox | `/app/workspaces/session-1231-e2e-…` | ❌ | chris | 370 |
| 10 | Morning Brief | local | `/morning-brief` | ❌ | chris | (few) |
| 11 | Rigby Capability Assessment & Market Readiness | sandbox | `/app/workspaces/rigby-capability-…` | ❌ | chris | 648 |
| 12 | **Architecture & Research** | sandbox | `/app/workspaces/architecture-&-research` (fake) | ✅ | chris | 469 |

Ownership: 11/12 owned by user `chris`; 1 by `system_autonomous`.

**Live-usage observation:** only 2 of 12 workspaces are marked `is_active=True` — Architecture & Research (governance repository) and System Autonomous (platform automation). The other 10 are stale project/session/experiment containers. This confirms workspaces are used as *long-lived scopes* but no lifecycle mechanism reaps them.

**Session-scoped workspaces (4/12):** Sessions 1171/1172/1173/1231 were per-session sandboxes — evidence that the workspace has also been used as ephemeral experiment scope.

### 1.4 Configuration state — templates and governance modes

| Field | Value |
|---|---|
| WorkspaceTemplates defined | 4 (`newsletter`, `leadgen`, `research`, `custom`) |
| Templates in use (workspaces with `config.template != None`) | **0** |
| Workspaces with `config.governance_mode != None` | **0** |
| Workspaces with a non-empty `agent_pool` | 0 |
| Workspaces with a non-empty `spider_subscriptions` | 0 |
| Workspaces with a non-empty `deliverable_categories` | 0 |
| Workspaces with a non-empty `pipeline_config` | 0 |

**Every workspace's `WorkspaceConfig` row exists but is empty of intent.** The template/config system is *complete infrastructure* that is *entirely unused* — a "ghost architecture" waiting for someone to declare a workspace's shape.

**Template details** (unused but designed): each template pre-declares pipeline_stages (with agent per stage), agent_pool, spider_subscriptions, and deliverable_categories. E.g., the `research` template declares 5 stages (Signal Collection → Analysis → Synthesis → Review → Deliver) with 8 deliverable categories (`Research Brief`, `Market Analysis`, `Competitive Landscape`, `Trend Report`, `Due Diligence Pack`, `Strategic Memo`, `Dossier`, `Intelligence Summary`). The Architecture & Research workspace *conceptually matches* this template but has never been bound to it.

### 1.5 Content state — where the outputs actually live

| Model / table | Count | Notes |
|---|---|---|
| `Deliverable` total | 524 | Across 12 workspaces; 0 unassigned |
| `Deliverable` types (12 declared, 15 actual) | `document` 226, `analysis` 129, `research` 102, `report` 10, `adr` 5, `ratification_record` 5, `spec` 4, plus 8 more | Declared enum undercounts real values |
| `Deliverable.category` (uncontrolled vocabulary) | ~40 distinct values | Top: Research 96, Executive Operations 32, Platform Diagnostics 29 |
| `Deliverable` per top workspace | Donkey Betz 384, Morning Brief 41, Rigby Assessment 35, Session 1231 26, Architecture & Research 25 | Governance content (25) is a *tiny fraction* of total workspace-owned deliverables (524) |
| `WorkspaceOperation.operation_type` | `command_exec` 5,631; `file_create` 74; `file_modify` 2 | Almost all audit is command execution, not file mutation |
| `WorkspaceOperation` per workspace | Donkey Betz 2,545; System Autonomous 688; Rigby 648; Architecture 469; Local QA 467 | Distribution shows workspaces are execution-heavy environments |
| `content.Document.source` | `imported` 2,988; `workspace` 7; `api` 3 | RAG is 99.7% repo-mirrored today; workspace-source is the minority |
| `content.Document.canonical_authority` | `repo_canonical` 2,986; `workspace_canonical` 7; `derived` 5 | Matches the source distribution; ADR-0120 field is live but sparingly used |

**Insight from these counts:** the governance content Chris cares about most (5 ADRs, 5 ratification records) represents ~2% of workspace content and ~0.2% of RAG content. Everything else in the workspace is *creative operational output* — the workspace is a creator/operator's studio, and governance is one cabinet in it.

### 1.6 Interface surface — the UI's story

The workspace UI (`frontend/src/pages/WorkspacePageNew.tsx`) mounts **32 tab components** in `frontend/src/pages/workspace/tabs/`:

`WorkspaceOverviewTab`, `HomeTab`, `FilesTab`, `GitTab`, `OperationsTab`, `OpsConsoleTab`, `TriggersTab`, `InitiativesTab`, `DeliverablesTab`, `KnowledgeTab`, `GovernanceTab`, `InfrastructureTab`, `IntelligenceTab`, `OrchestrationTab`, `ContentStudioTab`, `CampaignTab`, `ConceptForgeTab`, `BoardroomTab`, `LaunchpadTab`, `CareerTab`, `DataIntelTab`, `DataSourcesTab`, `ToolCallAnalyticsTab`, `OutreachInboxTab`, `VoiceMarketplaceTab`, `ClosePackViewer`, `BuildPacketWizard`, `Stage3EvaluationTab`, `AIConsciousnessTab`, `AppTab`, `WorkTab`

**Two implications:**

1. There is already a first-class `GovernanceTab` — governance is a UI-level capability *inside every workspace*, not a separate app.
2. The workspace is the site where creative operations, code work, orchestration, campaigns, career/personal work, opsconsole, launchpad, boardroom, and knowledge management all cohabit. This is the shape of an **operator's operating system**.

### 1.7 Service surface — what workspace_manager.py actually does

- **`core/services/workspace_manager.py` = 2,381 lines** across four classes: `FileWriter`, `GitIntegrator`, `WorkspaceScanner`, `WorkspaceManager`.
- The PA `workspace_tool` (`core/services/pa_tool_schemas.py:820`) exposes 13 actions: `list, get, status, create, delete, scan, read, write, git_status, git_commit, git_branch, operations, rollback`.
- Method-level: `write_file`, `read_file`, `create_branch`, and (in classes below `WorkspaceManager`) commit/git integration.

**This is a full AI-managed-repository abstraction.** The workspace is not a metaphor — it's an executable environment where AI agents can safely write code, run commands, commit, and roll back, under per-workspace autonomy gates (`allow_file_write`, `allow_autonomous_writes`, `require_human_review`).

### 1.8 The Architecture & Research workspace is a facade

Direct ORM inspection of workspace `a9a16593-…`:

| Field | Value | Signal |
|---|---|---|
| `workspace_type` | `sandbox` | Ephemeral by design |
| `root_path` | `/app/workspaces/architecture-&-research` | Fake path — ampersand break, directory doesn't exist |
| `git_remote_url` | `""` | No repo |
| `tech_stack` | `{}` | Empty |
| `entry_points` | `{}` | Empty |
| `current_branch` | `""` | Empty |
| `total_files_written` | 0 | No files ever written |
| `total_commits` | 0 | No commits ever made |
| `total_operations` | 469 | All `command_exec` with `trigger=unknown` (audit instrumentation, not real work) |
| `WorkspaceConfig.template` | `None` | Not templated |
| `WorkspaceConfig.governance_mode` | `None` | Governance-mode not declared even though it holds governance content |
| `WorkspaceConfig.agent_pool` / `.spider_subscriptions` / `.deliverable_categories` / `.pipeline_config` / `.workspace_brief` / `.settings` / `.quotas` | `[]` / `[]` / `[]` / `[]` / `[]` / `[]` / `{}` | Fully unconfigured |
| `WorkspaceContext` | **does not exist** | Never scanned (no code to scan) |
| Reverse-relation usage | 2/23 (Deliverables: 25; WorkspaceOperations: 469) | Uses 8.7% of workspace capabilities |

**Conclusion:** the Architecture & Research workspace uses the ProjectWorkspace model as a bare **Deliverable container**. It does not exercise 91% of the workspace's designed capabilities. This is not a criticism — it's an important data point: **when you need to store organizational governance content, you overload a workspace to be your governance repository.** The model is elastic enough to serve; the model was not designed for that.

---

## 2. Current state — what a Workspace actually is today

Synthesizing the evidence from §1.2–§1.8, a Workspace *today* is:

**(a) A multi-tenant boundary.** Every creative and operational artifact belongs to exactly one workspace. Workspace is the *first-class* tenant key across 23 models.

**(b) A user-scoped operating environment.** Each workspace has a `user` FK. There is no `Organization` model between user and workspace. Multi-tenant today ≈ multi-user. Multi-org tomorrow requires a `WorkspaceGroup` or `Organization` layer that does not yet exist.

**(c) An AI-managed dev environment abstraction.** The model was designed around: (root_path, git_remote_url, tech_stack, protected_paths, autonomy gates, autonomous writes with per-op audit trail, rollback). Real workspaces (Donkey Betz, chris-personal, session sandboxes) exercise this. Governance workspaces (Architecture & Research) don't.

**(d) An orchestration container.** Templates + pipelines + agent pools + spider subscriptions + trigger/rule configs → declarative "shape of an org." Currently 0% adopted (all 12 workspaces have empty configs), but the infrastructure is complete.

**(e) An operational memory.** WorkspaceOperation (5,707 rows across 12 workspaces) captures every file write, command execution, and git op with rollback capability. Workspaces remember what happened inside them.

**(f) A UI cockpit.** 32 UI tabs. Governance, files, git, operations, triggers, initiatives, deliverables, knowledge, campaigns, boardroom, content studio, launchpad. The workspace has already been designed as an operator's dashboard.

**(g) A publishing site.** Deliverables land in workspaces, get statuses via PublishGate, get mirrored into RAG (KFI-1) with `canonical_authority='workspace_canonical'` (KFI-2). Rigby retrieves workspace content authority-aware (KFI-3, ADR-0130).

**(h) An audit surface.** `total_operations`, `total_files_written`, `total_commits` on the workspace; `WorkspaceOperation` audit rows; `Deliverable.metadata`, `Deliverable.trace_id`. Everything the workspace does is (in principle) traceable.

**What the Workspace is NOT today:**

- Not a document folder — 32 UI tabs, 23 reverse relations, 47 fields on the model, 2,381 lines of workspace_manager.py service code contradict that framing.
- Not a governance system per se — governance is a *use pattern* (Architecture & Research); no workspace has `governance_mode` set.
- Not an organization primitive — user-scoped, not org-scoped. Multi-org requires an unbuilt layer above.
- Not an execution context in the runtime sense — Celery/Beat don't scope to workspace; workspace is the *result* container, not the executor.

---

## 3. Architectural analysis — what problem is the Workspace actually solving?

### 3.1 What problem was it originally solving?

The **oldest visible intent** in the code is: *an AI-controlled dev environment*. Fields like `root_path`, `git_remote_url`, `allow_file_write`, `allow_autonomous_writes`, `protected_paths`, and the whole `FileWriter/GitIntegrator/WorkspaceScanner/WorkspaceManager` service class hierarchy were designed to let AI agents *safely code inside a customer repo*. Historic session sandboxes (Sessions 1171–1174, 1231) exist as forensic evidence — engineers spun up per-session workspaces to reproduce/test issues in isolated environments.

The **second-order intent**, layered on top, was: *a templated pipeline environment*. Templates like `newsletter` and `leadgen` codify entire agent-driven content-shop shapes (topic mining → research → strategy → draft → edit → fact-check → SEO → distribution). This is the *AI startup-in-a-box* framing — declare what the workspace does, and the platform assembles the agents, spiders, categories, and quotas to make it happen.

### 3.2 What problem is it solving today?

Today's actual usage tells a different story:

- **~50% governance repository** — Architecture & Research is the only actively-used single-purpose workspace, and it hosts constitutional content, not code.
- **~25% platform-wide operational scratchpad** — Donkey Betz (2,545 ops, 384 deliverables) and System Autonomous (688 ops) hold the platform's own operational outputs.
- **~15% personal work** — chris-personal, Morning Brief.
- **~10% session sandboxes** — historical experiments, largely dormant.

The dominant emergent pattern: **Workspace = "a scope within which AI-augmented outputs are produced and attributed."** Governance content, operational content, personal content, creative content — all fit the same shape.

### 3.3 What is it evolving toward?

Direction of travel visible in the evidence:

- **Cycle 1A (KFI-1/2/5) elevated workspaces to canonical-authority for governance.** This is a *significant* upgrade — it says "workspace content can win over repo content in retrieval." That opens the door for workspaces to be treated as first-class sources of truth for *any* domain, not just code.
- **32 UI tabs and 23 model relations** suggest the workspace is evolving toward "the app" — the primary front-door where the user does everything.
- **Templates + pipeline_config + agent_pool** suggest the workspace is evolving toward "declare your operation, we instantiate it" — the SaaS-shaped operator OS.

**My reading:** the Workspace is intended to become **the operator's OS boundary**. Each workspace is a self-contained, AI-augmented "unit of operation" — a person, a team, a customer, a domain of work — with its own agents, its own data, its own decisions, its own audit, and its own governance. The multi-tenant future is not "customer per user" but "customer per workspace, users share workspaces via team membership."

### 3.4 Which of the framings from the mission questions holds up?

| Framing | Verdict | Rationale |
|---|---|---|
| Document folder | ✗ | 47 fields, 23 relations, 32 UI tabs; docs are ~2% of workspace content |
| Project | Partial | `WorkspaceProject` is a *sub-project* inside a workspace; workspace is *bigger* than a project |
| Knowledge base | Partial | Workspace-canonical retrieval (KFI-2/3) makes workspace a knowledge source, but knowledge is one output not the container |
| Governance system | ✗ | Governance is a use-pattern, not a workspace category; no workspace declares `governance_mode` |
| Operating system | ✓✓ | Best fit. Autonomy gates, agent pool, pipeline, triggers, audit trail, publishing gate — this IS an operator OS |
| Organizational memory | ✓ | True, but incomplete framing — memory is a consequence of the OS, not the primary purpose |
| Execution context | Partial | Workspace scopes *outputs* of execution but doesn't drive Celery/Beat scheduling |
| Something else | Contains all of the above under "Operator OS" | The Workspace is the tenant-scoped AI-augmented operator's OS |

**Best-supported framing:** **Workspace = a tenant-scoped, AI-augmented operator's OS.** Every other framing is a projection of one facet.

---

## 4. Knowledge layer model

The layered model I proposed in the 2708 report was correct in *direction* but underspecified the workspace's role. Refined model:

### Layer 0 — Human intent

The ratifier (Chris; later a customer). Source of ALL truth in the platform. Every ratified fact ultimately traces to a human directive.

### Layer 1 — Constitutional knowledge (per-workspace, workspace-canonical)

**What lives here:** ADRs, ratification records, cycle open/close records, evidence ledgers, engineering playbook, customer-facing constitutions, engineering standards.

**Storage:** As `Deliverable` rows inside a workspace, with `deliverable_type ∈ {adr, cycle_open, cycle_close, ratification_record}`, `status='completed'` (immutable-on-write), and mirrored into `content.Document` with `canonical_authority='workspace_canonical'`.

**Ownership:** The workspace's user (multi-tenant: the workspace's team).

**Immutability:** Enforced at content-completion via PublishGate; policy per 0010 §6. Enforcement is currently policy-based, not ORM-blocked (opportunity from 2708 §R7).

**Key insight the 2708 report missed:** L1 is *not* a global layer — it is workspace-scoped. Every workspace has (or can have) its own constitutional layer. Donkey Betz's constitution lives in workspace `a9a16593-…`. A future customer's constitution lives in *their* workspace. The engineering playbook that governs *how* Donkey Betz builds is a Donkey-Betz-constitutional artifact; a customer's playbook is *their* constitutional artifact.

### Layer 2 — Operational documentation (per-workspace, workspace-editable; plus per-repo, repo-editable)

**What lives here:**
- Workspace-scoped: brief, roadmap, runbook, session handoffs, working notes, live plans.
- Repo-scoped: `CLAUDE.md`, `MEMORY.md`, `00-START-NEXT-SESSION.md`, `docs/topics/*`, `docs/handoffs/*`, developer onboarding, runbook.

**Storage:**
- Workspace-scoped L2 → Deliverable rows with non-constitutional types (`document`, `research`, `report`, etc.).
- Repo-scoped L2 → files in the git repository.

**Ownership:** Multi-source. Workspace owns workspace-scoped L2; repo owns repo-scoped L2. The 2708 report conflated these two — the correction here is important.

**Editability:** Both editable. Workspace L2 has PublishGate lifecycle (`draft` → `ready` → `completed` → `archived`); repo L2 is PR-gated.

### Layer 3 — Repository / substrate

**What lives here:** Code (all Python, TS, migrations, tests), platform infrastructure (Docker, Procfile, Makefile), shared L2 documentation, cross-workspace primitives (models, services, PA tool schemas), platform-level constitutional artifacts that are *the platform itself* (not per-workspace).

**Ownership:** Engineering team. In multi-tenant future: Donkey Betz's engineering team owns the platform substrate.

### Layer 4 — Runtime

**What lives here:** PostgreSQL rows (Deliverables, Documents, everything), Redis (broker, cache, PA sessions), Celery workers, Beat scheduler, live processes.

**Ownership:** Platform automation.

**Note on scope:** Runtime is *global* — one Celery cluster, one Postgres, one Redis. Workspaces are logical partitions inside these shared resources. **The workspace does not scope Celery queues today.** Multi-tenant scaling will require workspace-scoped or workspace-priority queues.

### Layer 5 — RAG / retrieval

**What lives here:** `content.Document` + `content.DocumentEmbedding`. Mirror of L1 + L2 sources. Authority-aware retrieval (ADR-0130) picks the highest-authority match.

**Ownership:** Platform automation via cascade jobs. **Cascade steps are global** — one cascade run refreshes both workspace-source (L1) and repo-source (L2 + L3 docs) mirrors.

**Correction from 2708:** the 2708 report described RAG as "derived — no truth here." That is correct, but understated: RAG is also **the shared search plane** across workspaces. Right now (2,986 imported vs 7 workspace) it is >99% repo-mirrored. In a multi-tenant future, RAG would need per-workspace filtering (which Rigby likely does via `source='workspace'` filter, but this needs verification).

### Layer 6 — Agent / execution

**What lives here:** 83 AGENT_MAP agents + BaseAgent + agent_router. Agents run against a workspace context (via `workspace_id` on execution) and can be *workspace-aware* (WORKSPACE_AWARE_AGENTS constant, though its import location has drifted per §1 evidence).

**Ownership:** Platform. Multi-tenant future: agents remain a platform primitive; workspace declares which agents it uses via `agent_pool`.

### Layered relationships (updated diagram)

```
Layer 0: Human (Chris; later customer)
    │
    ▼
Layer 1 (Constitutional; per-workspace, workspace-canonical)
    │  [ADRs, ratifications, cycle_open/close, playbook, evidence ledgers]
    │  content_tool.content_complete → immutable
    │
    ▼
Layer 2 (Operational)
    │  Workspace-scoped L2         Repo-scoped L2
    │  (workspace deliverables)    (CLAUDE.md, MEMORY.md, 00-START,
    │                               docs/topics, docs/handoffs)
    │
    ▼
Layer 3 (Repository / substrate)
    │  Code, migrations, PA tool schemas, cross-workspace primitives
    │
    ▼
Layer 4 (Runtime)
    │  Postgres, Redis, Celery, Beat — SHARED across all workspaces
    │
    ▼
Layer 5 (RAG / retrieval)
    │  content.Document w/ canonical_authority
    │  Authority-aware retrieval (ADR-0130)
    │
    ▼
Layer 6 (Agent execution)
    │  83 agents; workspace-aware via workspace_id in execution context
```

**Truth ownership**:
- **L0 owns intent.** Ratifier's directive is authoritative.
- **L1 owns constitution.** Immutable post-ratification.
- **L2 owns operations.** Both workspace-scoped and repo-scoped, editable through their respective gates.
- **L3 owns platform.** The code IS the platform; source of behavior truth.
- **L4 owns state.** Whatever is in Postgres/Redis right now is what's true.
- **L5 owns nothing — pure derivation.**
- **L6 owns nothing — pure execution.**

**Which layers are immutable?** L1 (post-completion); parts of L3 (release tags in git).

**Which layers are editable?** L2 (both flavors), L3 (main branch under PR gate), L4 (writes constantly, subject to PublishGate for governance).

**Which layers are disposable?** L5 (RAG can be rebuilt from L1+L2+L3), parts of L4 (Redis cache, Celery task events — non-durable subsets).

---

## 5. Workspace object model — what belongs inside?

Restating the evidence: 23 reverse relations already point at ProjectWorkspace. This is a *large* object model. The question is not "what fits in a workspace?" — the model has already accepted almost every kind of AI output. The question is: **what SHOULD belong** and **what should NOT**.

### 5.1 Belongs inside a workspace

**Governance layer (Layer 1) — one workspace's constitution:**

| Class | Storage today | Belongs? |
|---|---|---|
| ADRs | `Deliverable(type='adr')` | ✓ |
| Ratification records | `Deliverable(type='ratification_record')` | ✓ |
| Cycle open/close records | `Deliverable(type='cycle_open'|'cycle_close')` | ✓ |
| Evidence ledgers | `Deliverable(type='document')` today; should be typed | ✓ |
| Engineering playbook | Undecided (proposal target) | ✓ |
| Research OS / RAR methodology | `Deliverable` in workspace already | ✓ |
| Manifests | `Deliverable(type='document')` today | ✓ |
| Constitution (customer-facing standards) | Not yet built | ✓ |

**Operational layer (Layer 2 — workspace-scoped):**

| Class | Storage today | Belongs? |
|---|---|---|
| Workspace brief | `WorkspaceConfig.workspace_brief` JSONField | ✓ |
| Runbooks / SOPs | Deliverables | ✓ |
| Working notes / session handoffs | Currently `docs/handoffs/*` in repo; could migrate to workspace | ✓ (with caveats — see §5.3) |
| Live plans / roadmaps | Deliverables | ✓ |
| Meeting notes | Not yet built | ✓ |

**Creative outputs (already established):**

| Class | Belongs? |
|---|---|
| Content (blogs, podcasts, newsletters, campaigns) | ✓ |
| Media (images, videos, audio) | ✓ |
| Research briefs / market analysis / dossiers | ✓ |
| ConceptForge runs (idea generation) | ✓ |
| Outreach / opportunities / tasks | ✓ |
| Initiatives / stages / approvals | ✓ (via `target_workspace`, currently) |

**Execution outputs:**

| Class | Belongs? |
|---|---|
| Workspace operations (audit trail) | ✓ (essential) |
| Pipeline runs | ✓ |
| Tool call analytics | ✓ |
| Chat conversations | ✓ (but see §5.3) |

**Configuration:**

| Class | Belongs? |
|---|---|
| Template binding | ✓ |
| Agent pool declaration | ✓ |
| Spider subscriptions | ✓ |
| Deliverable categories | ✓ |
| Quotas | ✓ |
| Governance mode | ✓ (should be used, currently null everywhere) |
| Autonomy gates | ✓ |
| Protected paths | ✓ |

### 5.2 Does NOT belong inside a workspace

**Platform primitives (Layer 3):**

- Agent code (`core/agents/`) — one platform, not per-workspace.
- Spider code (`ai_core/spiders/`) — same reasoning.
- Model definitions (`core/models*.py`).
- Cross-workspace services (`core/services/*`).
- PA tool schemas (`core/services/pa_tool_schemas.py`) — cross-workspace surface.

**Platform-wide L2 documentation:**

- `CLAUDE.md`, `MEMORY.md`, `00-START-NEXT-SESSION.md` — orientation for Claude across all sessions and all workspaces, not any single workspace.
- `docs/PLATFORM_INVENTORY.md`, `docs/PLATFORM_WHAT_IT_IS.md` — describe the platform, not a workspace.
- `docs/topics/*` — describe subsystems, not workspaces.

**Runtime shared state:**

- Beat schedule, Celery queue definitions, Redis config, Postgres schema. Global by definition.

**Multi-workspace primitives (cross-cutting):**

- `WorkspaceTemplate` catalog — shared across all workspaces, defines *shapes*.
- Registered Rigby PA session pins for cross-workspace operators.
- Fleet-level artifacts (audit rows across the whole fleet).

### 5.3 Belongs inside a workspace with caveats

**Chat conversations.** Currently workspace-attributable via `ChatConversation.workspace` FK, but in practice the Rigby "global" chat is not workspace-scoped. There is a mode toggle (per CLAUDE.md L7 context: "Rigby modes: `global` and `workspace`"). This dual mode is architecturally correct — some chats are cross-workspace operator commands; some are inside a workspace's scope.

**Session handoffs.** Currently `docs/handoffs/*` (repo L2). Could migrate to workspace L2. Arguments for migration: workspace-scoped context makes handoffs discoverable by workspace consumers. Arguments against: session handoffs are also artifacts of the *platform's* history (Chris tracks all sessions across all workspaces), which is a repo-native pattern. **Recommendation: leave handoffs in repo L2 for now; add a `HandoffCollection` reference from workspace deliverables to relevant handoff files as needed.**

**Initiatives.** Currently uses `target_workspace` FK (not `workspace`). This naming suggests initiatives are cross-workspace *proposals* that get targeted at a workspace. Belongs where it is.

### 5.4 Object model summary

**The workspace should hold:**

1. **L1 governance content** (workspace-canonical constitution: ADRs, ratifications, cycle records, playbook, evidence ledgers) — Deliverable rows with governance types.
2. **L2 operational content** (workspace-scoped runbooks, briefs, plans, session notes) — Deliverable rows with operational types.
3. **Creative outputs** (content, media, research briefs, campaigns) — Deliverable rows with creative types.
4. **Execution audit** (operations, pipeline runs, tool call analytics) — dedicated tables (`WorkspaceOperation`, `PipelineRun`).
5. **Configuration** (template binding, agent pool, spider subs, categories, quotas, autonomy gates) — `WorkspaceConfig` + `ProjectWorkspace` fields.
6. **Context** (codebase snapshot when applicable) — `WorkspaceContext`.

**The workspace should NOT hold:**

1. Platform primitives (agents/spiders/models/services/PA tool schemas as code).
2. Platform-wide L2 documentation (`CLAUDE.md`, `MEMORY.md`, `00-START`, `docs/PLATFORM_*`, `docs/topics/*`).
3. Shared runtime state (Postgres schema, Celery queues, Beat schedule).
4. Cross-workspace catalogs (`WorkspaceTemplate` shapes).

---

## 6. Workspace vs Repository

This is the section the mission called "most important." I'll answer directly and defend from evidence.

### 6.1 What belongs ONLY in Git?

- **All executable code** (Python, TS, migrations, tests).
- **Deployment / infra config** (Procfile, Makefile, Docker, requirements, package.json).
- **Cross-workspace L2 documentation** describing the *platform* — CLAUDE.md, MEMORY.md, 00-START-NEXT-SESSION.md, docs/PLATFORM_*, docs/topics/*, docs/DATABASE_MODEL_REFERENCE.md, etc.
- **Cross-workspace L2 handoffs** for now (`docs/handoffs/*`).
- **Guardrail infrastructure** (`scripts/verify_repo_guardrails.py`, autogen indexes like `docs/INDEX.md`).
- **Repo-anchor pointer files** to workspace-canonical artifacts (CLAUDE.md L7 blockquote; future Playbook anchor).

**Rationale:** Git provides code integrity, PR review, tag/hash lineage, and cross-workspace visibility. Anything that describes *the platform itself* (not a specific workspace's use of the platform) belongs in git.

### 6.2 What belongs ONLY in the Workspace?

- **The workspace's constitutional content** (its own ADRs, ratifications, cycle open/close, playbook, evidence ledgers) — L1 workspace-canonical.
- **The workspace's operational content** (brief, runbooks, plans) — L2 workspace-scoped.
- **The workspace's creative outputs** (content, media, campaigns) — always.
- **The workspace's audit trail** (WorkspaceOperation, PipelineRun) — always.
- **The workspace's configuration** (template binding, agent pool, spider subscriptions, quotas, autonomy gates, governance_mode) — always.
- **The workspace's context** (WorkspaceContext codebase snapshot when applicable) — always.

**Rationale:** These are *the workspace's own OS state*. In a multi-tenant future, a customer's workspace content must not leak into another's or into the platform's git. Even in single-tenant today, keeping workspace-owned state in the workspace (DB) rather than the platform-owned git enforces separation-of-concerns.

### 6.3 What should exist in BOTH (mirrored)?

- **L1 governance artifacts.** Workspace-canonical body; repo-side pointer anchor (KFI-5 pattern). Direction: **workspace → repo** for the pointer (repo file is autogen from workspace body). Never edit the pointer by hand.
- **RAG mirror of L1 + L2.** Workspace deliverables → `content.Document` with `source='workspace'` and `canonical_authority='workspace_canonical'` (KFI-1 + KFI-2). Repo docs → `content.Document` with `canonical_authority='repo_canonical'`.

### 6.4 Direction of canonicality

For each mirrored class:

| Content class | Canonical source | Mirror direction | Mirror consumers |
|---|---|---|---|
| L1 governance (ADRs, ratifications, playbook body) | Workspace | Workspace → RAG; Workspace → repo pointer anchor | RAG search; session-open bootstrap |
| L2 workspace-scoped (workspace brief, runbooks) | Workspace | Workspace → RAG | RAG search; workspace UI |
| L2 repo-scoped (CLAUDE.md, docs/topics) | Repo | Repo → RAG | RAG search; Claude session open |
| L3 code | Repo | (Repo internally) | Runtime execution |
| L5 RAG rows | (derived) | ← from all above | Rigby queries |

**Never repo → workspace for L1 content.** This is the direction Cycle 1A explicitly established (KFI-1 mirror, KFI-2 canonical_authority). Any reverse migration undermines that.

### 6.5 Cycle 1A evidence weighs in

- **KFI-1 (Deliverable→Document mirror)** proved workspace content can flow into RAG safely and enrich search with workspace-canonical authority.
- **KFI-2 (canonical_authority)** gave the retrieval system a way to *rank* by authority.
- **KFI-3/ADR-0130 (authority-aware retrieval)** wired the ranking into search.
- **KFI-5 (CLAUDE.md L7 blockquote)** proved that a repo file can point at workspace-canonical truth without duplicating it.

**Cycle 1A did not accidentally establish this pattern — it explicitly ratified it.** The Workspace-vs-Repo distinction is: repo owns *what the platform is*; workspace owns *what the user does with it*. Mirror where necessary, in that direction.

---

## 7. Governance model

### 7.1 What governance means at each layer

- **L0 governance:** the ratifier's directive. Chris today. In multi-tenant future: workspace owner (customer's designated ratifier).
- **L1 governance:** the workspace's ratified constitution. ADRs, cycle records, playbook. Immutable-on-write after ratification.
- **L2 governance:** the workspace's editable operational documentation. No ratification requirement.
- **L3 governance:** the repo's PR review + merge gates. Cross-workspace, applies to platform substrate.
- **L4 governance:** PublishGate state machine (Deliverable status transitions), signals, ORM constraints.
- **L5 governance:** authority-aware retrieval — RAG's ranking preference for workspace-canonical over repo-canonical over derived.

### 7.2 The under-used `governance_mode` field

Every `WorkspaceConfig` row has a `governance_mode` CharField. All 12 rows are null. This field is the *natural home* for declaring the level of governance a workspace applies. Candidate values might include:

- `none` — no governance layer (personal or ephemeral workspaces).
- `lightweight` — L2 operational only, no ratification cycle.
- `constitutional` — full L1 + L2 (ADRs, ratifications, playbook binding).

The 2708 proposal recommended keeping enum discipline via a Playbook rule. This proposal makes the same recommendation but sharpens it: **`governance_mode` should be the field that determines whether a workspace is expected to hold L1 constitutional content.** The Architecture & Research workspace should be tagged `governance_mode='constitutional'`. Session sandboxes should be tagged `governance_mode='none'`.

### 7.3 Governance-flow contract (proposed)

For a workspace with `governance_mode='constitutional'`:

1. New governance artifact drafted as `Deliverable(status='draft', deliverable_type ∈ {adr, cycle_open, cycle_close, playbook_version, ...})`.
2. SIGN cycle applied (per Cycle 1A methodology).
3. Corrections via ORM (or repaired `deliverable_tool.update` post-Cycle-2 fix).
4. Ratifier directive.
5. `content_tool.content_complete` fires PublishGate → `status='completed'`.
6. Ratification record created (of `deliverable_type='ratification_record'`) naming the parent by UUID.
7. `content_hash` populated (Cycle 2 remediation — not enforced today).
8. RAG mirror fires cascade → `content.Document(source='workspace', canonical_authority='workspace_canonical')`.
9. Repo anchor regenerated (if applicable — Cycle 2 tooling).
10. Immutable-on-write; further edits require a new versioned artifact.

**This flow already works today** for steps 1–6 and 8. Steps 7 (content_hash), 9 (repo anchor), and ORM-level immutability enforcement are Cycle 2 code work.

---

## 8. Future evolution — multi-tenant, multi-workspace

The mission asked how Workspaces should evolve if Donkey Betz eventually serves multiple organizations.

### 8.1 Types of workspace in a multi-org future

| Workspace type | Owner | Purpose | Governance mode |
|---|---|---|---|
| **Platform workspace (Donkey Betz)** | Donkey Betz eng team | The platform's own operation | `constitutional` |
| **Personal workspace** | Individual user | Solo AI-augmented work | `none` or `lightweight` |
| **Customer workspace** | Customer org | Customer's AI-augmented operation (their business) | Customer's choice |
| **Customer governance workspace** | Customer org | Customer's constitutional layer | `constitutional` |
| **Research workspace** | Any owner | Domain research (like Architecture & Research today) | `constitutional` (research is treated as constitutional-adjacent) |
| **Engineering workspace** | Team | Engineering-org-scoped work | Depends |
| **Session sandbox** | Any owner | Ephemeral experiment | `none` |
| **Legal workspace** | Legal team | Regulatory/compliance artifacts | `constitutional` (high-stakes governance) |
| **Enterprise workspace** | Enterprise customer | Multi-team enterprise operation | Customer's choice |

### 8.2 Constitutional knowledge — platform vs per-workspace

The critical distinction for a multi-tenant future:

**Platform-level constitutional knowledge** (belongs to Donkey Betz, applies to all workspaces):

- Donkey Betz's Engineering Playbook (how the platform is built).
- Platform ADRs (0110–0150 today; 0200+ tomorrow) — decisions about the platform itself.
- Ratification records for platform decisions.
- Cycle records for platform releases.

**Per-workspace constitutional knowledge** (belongs to *this* workspace):

- Customer's business playbook.
- Customer's decision records.
- Customer's ratification records.
- Customer's governance.

**The Engineering Playbook is platform-level.** It describes how *Donkey Betz* engineers. Every customer workspace *reads* it (via RAG or explicit anchor); no customer workspace *owns* it.

### 8.3 Missing layer — Organization / WorkspaceGroup

Today's workspace is user-scoped (`ProjectWorkspace.user` FK to `UnifiedUser`). Multi-org requires a layer above:

- `Organization` — a customer entity.
- `WorkspaceMembership` — user's role in an organization's workspace(s).
- Per-organization `governance_mode` defaults.

This layer does not exist in the codebase (verified: no `Organization` model exists in the multi-app inventory).

### 8.4 RAG in a multi-org future

RAG is *global today* — one `content.Document` table, one embedding index. For multi-org:

- Per-workspace `source='workspace'` filtering (Rigby likely uses this today; verify Cycle 2).
- Per-organization tenant isolation (workspace mirror rows would need workspace FK; today they don't per §1.5 evidence).
- Authority-aware retrieval extended to prefer *your workspace's* canonical over *any workspace's* canonical.

Cycle 1A's `canonical_authority` field is the right substrate; multi-org just needs a `workspace_id` field on Document to complete the picture.

### 8.5 Runtime in a multi-org future

Today: one Celery cluster, one broker. Workspaces are logical partitions of the output; they don't scope the execution.

For multi-org:

- Per-workspace priority queues (fair sharing).
- Per-workspace quotas (already modeled in `WorkspaceConfig.quotas` — currently empty).
- Per-workspace agent pool (already modeled — currently empty).

**Every field for this future exists today; none is populated.** The infrastructure is present; the operationalization has not begun.

---

## 9. Playbook relationship (deferred, per session mission)

The mission instructed: *"Only AFTER answering every previous question, determine where the Engineering Playbook belongs."*

Now that the architecture is answered, the Playbook's placement is a consequence:

### 9.1 The Playbook is a platform-level constitutional artifact

- It describes how Donkey Betz engineers (methodology surfaced during Cycle 1A: PIC-1..10).
- It is **not** a per-workspace artifact — it does not belong to Architecture & Research alone. It applies to every workspace where Donkey Betz engineering happens.
- It is **not** a repo artifact in the L3 substrate sense — it is not code; it is constitutional methodology.
- It is **not** a repo-L2 artifact either — L2 is *operational* (CLAUDE.md, MEMORY.md are Claude-orientation tools); L1 is *constitutional*.

**Placement per the layer model:** L1 platform-level constitutional.

### 9.2 Two candidate homes at L1 platform-level

Given the architecture, two candidates emerge:

**Candidate 1 — Donkey Betz platform workspace.** There is not currently a dedicated "Donkey Betz Platform Governance" workspace. Architecture & Research (`a9a16593-…`) is *acting* as this. If it is renamed / re-scoped / declared `governance_mode='constitutional'` to explicitly be the platform governance workspace, the Playbook belongs there.

**Candidate 2 — a new workspace dedicated to the platform's constitutional layer.** Create a "Donkey Betz Platform" workspace (distinct from the existing `Donkey Betz` workspace `b4503364-…`, which is currently used as a scratchpad with 384 deliverables and 2,545 ops). The new workspace would be the constitutional home for the platform. Architecture & Research would remain for domain-research arcs.

**Third possibility surfaced by the evidence:** the current `Donkey Betz` workspace itself becomes the platform's constitutional home (with cleanup of its 384 deliverables to segregate operational-scratch from constitutional-canon). This is the *cheapest* path but has hygiene risk.

### 9.3 Recommendation on Playbook home

**Adopt Candidate 1: Architecture & Research becomes explicitly the Donkey Betz Platform Constitutional Workspace.** Reasoning:

1. It already holds Cycle 0 + Cycle 1A + 0100 + 0199 + all ratification records for the platform. Every existing L1 platform artifact is there.
2. Its name (`Architecture & Research`) is *close to* but not *exactly* right for the role. Renaming to `Donkey Betz Platform` or `Donkey Betz Governance` clarifies intent. Renaming does not disturb data.
3. Tagging it `governance_mode='constitutional'` in its WorkspaceConfig makes the workspace's role explicit at the schema level for the first time.
4. Every future L1 platform artifact (Engineering Playbook, Cycle 2 ADRs, PICs codified into standards) lands there naturally.

### 9.4 Storage pattern for the Playbook (from 2708, refined)

Once the home workspace is settled: the storage pattern is the Cycle 1A KFI-1/2/5 hybrid (2708 Option C). Playbook body as workspace-canonical Deliverable; repo anchor file for cheap Phase-0 bootstrap; RAG mirror with `canonical_authority='workspace_canonical'`. Version chain via `parent_object_id`.

**But now this pattern generalizes:** *every* L1 platform artifact — playbook, future ADRs, cycle records — follows this pattern. The Playbook is not a special case. It is the second application of a uniform L1-hybrid pattern.

### 9.5 What if the mission implies "the Playbook should live in git after all"?

The mission asked: *"If the architecture says the Playbook belongs somewhere unexpected, follow the evidence."*

Steel-manning "Playbook in git":

- Git has PR review, version control, human-diff, GitHub search.
- If the Playbook is the platform's most-often-referenced doc, cheap access matters.
- Every developer clones the repo; not every developer has Rigby access.

Rebuttal from evidence:

- Cycle 1A explicitly moved constitutional artifacts *out* of git into workspace-canonical.
- KFI-5 (CLAUDE.md L7 anchor) demonstrated the *anchor pattern* solves the access problem without moving the truth.
- Deliverable's `metadata` JSONField natively supports PIC-10 provenance classification; markdown-in-git would require inventing YAML front-matter conventions.
- Multi-tenant future: putting the Playbook in git means every customer sees Donkey Betz's own constitutional artifact through the same lens as their own code. Workspace-canonical with retrieval-authority makes the platform's constitution *visible but not privileged* — the right shape.

**The evidence continues to favor workspace-canonical with repo pointer anchor.**

---

## 10. Self-critique

The mission required attacking my own recommendation and steelmanning alternatives. Here are the strongest cases against Workspace-as-Operator-OS.

### 10.1 Alternative: Workspace-only (extreme concentration)

**Steelman:** everything moves into workspaces. Code — via `WorkspaceProject`'s `ProjectRepo` model. Docs — as workspace deliverables. Even `CLAUDE.md` becomes workspace-scoped Claude orientation. The workspace becomes the *only* boundary; git becomes a substrate detail.

**Why it looks attractive:** clean model. Everything belongs somewhere obvious. Multi-tenant is trivial.

**Attack (why it fails):**

- Code has to be running *somewhere* — the platform Python code powers all workspaces. If it moves into a workspace, you get infinite recursion (which workspace holds the code that runs the workspace?).
- Git primitives (PR review, tag chain, cryptographic hash lineage) are hard-earned engineering practice; abandoning them for workspace-only reinvents version control badly.
- The 2,988 imported docs in RAG — you'd have to migrate all of them into workspaces, and pick a workspace for each. Absurd for platform-level docs like `docs/PLATFORM_INVENTORY.md`.

**Verdict:** rejected.

### 10.2 Alternative: Repository-only (revert Cycle 1A)

**Steelman:** git is *proven* engineering practice. Constitutional docs as markdown, versioned via git tags, PR-reviewed. Cycle 1A's KFI-1/2/5 were speculative; roll them back for simplicity.

**Attack:**

- Cycle 1A shipped, was ratified, and materially improved authority-aware retrieval. Rolling back destroys the pattern *and* the ratified artifacts.
- Immutable-on-write via PublishGate is stronger governance than git tags (a tag can be moved; a git-tag-based ratification has no equivalent to "ratifier's directive verbatim" recorded alongside).
- Multi-tenant future: putting all constitutional content in a *single* git repo is exactly what multi-tenant blocks. Every customer would need write access to your repo, or a fork per customer.

**Verdict:** rejected.

### 10.3 Alternative: Knowledge Graph as primary layer

**Steelman:** the deep truth is a knowledge graph — nodes for ADRs, ratifications, evidence, PICs, decisions; edges for supersedes/references/ratifies/challenges. Workspace, repo, RAG are all just projections of the graph.

**Attack:**

- No knowledge graph exists in the codebase today. Building one is a multi-month greenfield effort.
- The evidence in §1 shows the platform has *already* accumulated substantial value in the existing model. Migrating to a graph substrate abandons that.
- Knowledge graphs are excellent for *cross-referencing* but poor for *content storage* (blob-in-node is worse than blob-in-Deliverable).

**Verdict:** interesting future direction (as an *additional* layer for cross-workspace L1 relationships), but not a replacement for the workspace-owned L1 substrate. **Deferred to Cycle 3+.**

### 10.4 Alternative: Workspace-as-Constitutional-Layer-only (constrain the workspace's scope)

**Steelman:** the workspace is over-scoped. It has 32 UI tabs, 23 model relations, 2,381 lines of service code. Simplify: workspace = constitutional layer only. Move creative operational work (blogs, podcasts, opportunities, initiatives, content, media) out of workspace attribution.

**Attack:**

- The 23-relation multi-tenant boundary is *the* platform architecture. Extracting it wrecks tenant isolation.
- The evidence in §1.5 shows 522/524 deliverables are non-constitutional. Removing them from workspace attribution creates the "unassigned" bucket at scale — exactly what the "always assign workspace" memory rule (feedback_deliverable_workspace.md) forbids.

**Verdict:** rejected — but a *related* proposal to segregate workspaces by role (governance workspace vs operational workspace vs personal workspace) IS strong and is embedded in my §8 multi-org proposal.

### 10.5 Alternative: Workspace-as-Enterprise-Layer (move governance up, out of workspace)

**Steelman:** the workspace is user-scoped; governance is org-scoped. Governance should not live in workspaces at all — it should live in an `Organization` model or a dedicated `Governance` root. Workspaces are execution scopes; governance is above them.

**Attack:**

- No `Organization` model exists today (§8.3 evidence). Building it is Cycle 2+ scope.
- But **this steelman has a real point:** treating governance as workspace-scoped in a multi-tenant future creates a philosophical bind. Whose governance? Customer A's workspace can't govern the platform's rules. The platform's ADR-0110 governs *all* workspaces; a customer's ADR governs *only their own*.

**Consequence I accept:** the Playbook (§9) belongs to the *platform-level constitutional* workspace, not to any customer workspace. This is compatible with the workspace-as-OS framing but requires acknowledging *two tiers*: platform-constitutional workspace and customer-workspace-constitutional layer. Both use the same L1 primitives; they differ in scope of applicability.

**Verdict on this steelman: partially accepted.** It sharpens §8: the missing `Organization` layer needs to be built for true multi-tenant governance; until then, "platform workspace holds platform constitution" is the pragmatic bridge.

### 10.6 Alternative: Hybrid, but repo-primary for Playbook specifically

**Steelman:** even accepting the L1 workspace-canonical framing generally, the Playbook is *uniquely* Claude-consumed at session start. Optimizing for that consumption pattern — repo file, cheap Read, no auth — is worth breaking the pattern.

**Attack:**

- KFI-5 already solved this: anchor file in repo (cheap Read) + workspace body (canonical). The Playbook does not need to break the pattern; it needs to *use* the pattern.
- Every argument for Playbook-in-repo also applies to CLAUDE.md L7's target — and Cycle 1A ratified that pointing at workspace is correct.

**Verdict:** rejected. The steelman doesn't survive the KFI-5 evidence.

### 10.7 Which alternative survives?

None of the alternatives fully survives. The strongest partial survivor is 10.5 (enterprise/org layer for governance) — its critique that governance is org-scoped, not workspace-scoped, is philosophically correct and should shape the multi-tenant Cycle-3 architecture. In the interim, "platform workspace holds platform constitution" is the right bridge.

**Final architecture verdict:** Workspace-as-Operator-OS survives. It absorbs the concerns of every alternative and remains consistent with all Cycle 1A evidence.

---

## 11. Risks

| # | Risk | Severity | Notes |
|---|---|---|---|
| R1 | Workspace-as-Operator-OS framing outstrips current implementation (12 workspaces exist, all with empty configs, governance_mode null everywhere) | Med | Evidence of intent-vs-usage gap. Cycle 2+ has to close it or the framing is aspirational only. |
| R2 | User-scoped tenancy blocks true multi-org until `Organization` model exists | High | Blocks scaling to customer-facing multi-tenant. Cycle 3 candidate. |
| R3 | RAG's `content.Document` lacks `workspace_id` — cross-workspace leakage possible in retrieval | Med | Verify Rigby's filtering; possibly a Cycle 2 field addition. |
| R4 | Playbook placement in Architecture & Research workspace risks conflating "domain research" (child scoping) with "platform constitution" (Playbook) | Med | Rename or re-scope workspace to distinguish. |
| R5 | 12 workspaces, 10 dormant — no lifecycle mechanism (archive/purge) | Low | Workspaces accumulate; sandbox rot. |
| R6 | Governance content is 25/524 deliverables (5%) — workspace-canonical retrieval could miss governance under naive similarity search | Med | ADR-0130 authority-aware retrieval should mitigate; validate. |
| R7 | Immutability policy-only (no ORM enforcement); a workspace deliverable's `save()` doesn't check `status=completed` | Med (unchanged from 2708 R7) | Cycle 2 candidate. |
| R8 | `governance_mode` field exists but is null everywhere — infrastructure lag | Low | Populating it is a small change; unblocks per-workspace governance discipline. |
| R9 | `WorkspaceTemplate` inventory (4 templates) is unused (0 workspaces bound); if unused, the ghost architecture may confuse contributors | Low | Either use them or archive them. Cycle 3 candidate. |
| R10 | `workspace_manager.py` (2,381 lines) suggests significant infra that's underused for governance-only workspaces | Low | Not a defect — just a signal that the workspace was designed for a bigger use than governance-only. |
| R11 | Session-scoped sandboxes (Sessions 1171–1174, 1231) show workspaces used as ephemeral experiments; if this pattern grows, workspace inventory bloats | Low | Consider a `session_sandbox` workspace_type with auto-archive. |
| R12 | Bootstrap paradox for the Playbook: Playbook proposes how to write ADRs, but the Playbook itself must be ratified using pre-Playbook methodology | Med | Same as 2708 R4; handled by drafting v0.9 in workspace with `status=draft`, iterating, ratifying. |

## 12. Unknowns

| # | Unknown | Why it matters | How to resolve |
|---|---|---|---|
| U1 | Whether Rigby's RAG retrieval currently filters by workspace | Multi-tenant leakage risk | Read Rigby's retrieval code path in `unified_pa_entrypoint.py` + `tool_dispatcher.py`. |
| U2 | Whether `workspace_id` is populated on `content.Document` mirror rows (or if governance-workspace-source is only detectable via `source='workspace'`) | Determines whether cross-workspace queries are possible | ORM inspect the 7 workspace-source Document rows. |
| U3 | Whether `WORKSPACE_AWARE_AGENTS` constant still exists at `core.epa_handlers_tools` (import failed during evidence gathering) | CLAUDE.md L14 references it as 20 agents; may have moved | Grep for the constant definition; update CLAUDE.md if moved. |
| U4 | Where `workspace_type` values are defined (declared choices?) | Determines whether adding new types (`session_sandbox`, `constitutional`) requires a migration | Grep `workspace_type = ` and the field definition on ProjectWorkspace. |
| U5 | Whether `Initiative.target_workspace` vs `Deliverable.workspace` distinction implies a decision-flow architecture (initiatives *target* workspaces; deliverables *live in* workspaces) | Affects §7 governance flow contract | Read the Initiative model and lifecycle in `docs/DREAM_INITIATIVE_WORKFLOW.md`. |
| U6 | Whether the previously-designed `WorkspaceTemplate` catalog is intended to grow (constitutional template, engineering template, legal template) | Determines whether §8 multi-org typology is codified in code | Check the templates for a `constitutional` slot. |
| U7 | Whether `content_hash` is populated on any deliverable (Cycle 1A 0199 showed null; sample size 2 in 2708 report) | If any deliverable has it, immutability enforcement is partly in place | ORM query `Deliverable.objects.exclude(content_hash='').count()`. |
| U8 | Whether the `governance` category value on `Deliverable` (uncontrolled today) should become the field that carries L1 vs L2 distinction | Simpler alternative to `deliverable_type` enum expansion | Cycle 2 discussion — not resolved here. |

---

## 13. Recommendation

**Adopt the Workspace-as-Operator-OS framing.** Formalize the following architecture:

1. **Workspace = tenant-scoped AI-augmented operator's OS.** Every organizational unit (person, team, customer, domain, session experiment) is a workspace.
2. **L1 governance is workspace-owned but tiered.** Platform-level constitutional artifacts (Engineering Playbook, platform ADRs, platform cycle records) live in a designated *platform constitutional workspace*. Customer-level constitutional artifacts (customer's own ADRs) live in customer workspaces. The tiering is *by scope of applicability*, not by workspace type.
3. **L2 documentation splits.** Workspace-scoped L2 lives as Deliverables in the workspace. Platform-wide L2 (CLAUDE.md, MEMORY.md, 00-START, docs/topics, docs/handoffs) lives in the repo.
4. **L3 code is repo-owned.** Platform primitives (agents, spiders, models, services, PA tool schemas) are cross-workspace; they live in git and describe the platform itself.
5. **L4 runtime is shared.** Postgres, Redis, Celery, Beat. Workspaces are logical partitions; scaling to multi-org will require workspace-aware queues and quotas (Cycle 3+).
6. **L5 RAG is derived.** `content.Document` with `canonical_authority` — never written to as truth. Multi-org will require `workspace_id` filtering.
7. **L6 agents are platform primitives.** Bound to workspaces via `agent_pool` config and workspace-aware execution context.

**Playbook placement:** L1 platform-level constitutional. Home workspace: Architecture & Research (`a9a16593-…`) rebranded / re-declared / tagged as the Donkey Betz Platform Constitutional Workspace with `governance_mode='constitutional'`. Storage: KFI-1/2/5 hybrid pattern (2708 Option C generalized). Body: workspace deliverable. Anchor: repo file, autogen. RAG: mirror with `canonical_authority='workspace_canonical'`.

**The Engineering Playbook is the SECOND application of the workspace-canonical + repo-anchor pattern.** CLAUDE.md L7 was the first. Every future platform-level L1 artifact follows this template.

**Do NOT re-open the L1/L2 boundary question per artifact.** Once the pattern is settled: adopt it uniformly.

---

## 14. Implementation implications (no steps — implications only)

The mission specified: *"Do NOT write implementation steps."* The following are architectural *implications* of the recommendation, presented as consequences the platform must accommodate before the Playbook or Cycle 2 begins.

### 14.1 Immediate implications (before Playbook v1.0)

- **The Architecture & Research workspace's role must be explicit.** Its `WorkspaceConfig.governance_mode` should be populated. Its `WorkspaceConfig.deliverable_categories` should declare the governance category set. Its name may need rebranding to reflect its platform-constitutional role. Without this, the Playbook lands in a workspace whose intent is ambiguous.
- **The `deliverable_type` enum must formally include governance types.** Currently `adr`, `cycle_open`, `cycle_close`, `ratification_record` work at DB level but are undeclared in Python. Cycle 2 code work.
- **The pattern must be stated.** Even without codifying the Playbook itself, the pattern "workspace-canonical body + repo anchor + RAG mirror" needs to be an explicit architectural commitment before it is applied to a second artifact.

### 14.2 Cycle 2 implications

- **`content_hash` should be populated on all completed governance deliverables.** Immutability attestation moves from external (handoff SHA) to on-row.
- **`Deliverable.save()` should raise on `status=completed` rows.** Immutability moves from policy to enforcement.
- **`parent_object_id` should be used for version chains.** Playbook v1.1 points at v1.0.
- **Playbook anchor regeneration cascade step** should extend the existing 4-step docs cascade.
- **`verify_repo_guardrails.py`** should protect the Playbook anchor file as autogen.
- **CLAUDE.md L7 should be joined by a Playbook-anchor pointer.**

### 14.3 Cycle 3 implications

- **Introduce `Organization` model.** Multi-org tenancy requires an entity above `user`. Add `WorkspaceMembership` for user-to-workspace roles.
- **Extend `content.Document` with `workspace_id`.** Enables cross-workspace filtering; extends authority-aware retrieval to be workspace-aware.
- **Populate `WorkspaceTemplate` with a `constitutional` slot.** Templated instantiation of governance workspaces.
- **Workspace lifecycle (archive/reap).** Dormant sandboxes and completed sessions need a graceful path out of active inventory.

### 14.4 Cycle 4+ implications

- **Workspace-scoped Celery queues and quotas.** True multi-org runtime isolation.
- **Cross-workspace knowledge graph (§10.3 alternative promoted here).** Once workspaces multiply, cross-workspace L1 relationships become a first-class concern.

---

## Closing

The Workspace is intended to become **the multi-tenant AI-augmented operator's OS** of Donkey Betz. Every organizational unit gets one. Each workspace owns its constitution, its operations, its outputs, its audit, and its configuration. The repository owns the platform substrate: code, cross-workspace L2, and pointer anchors to workspace-canonical L1 truth. RAG mirrors both, with authority-aware retrieval.

The Engineering Playbook is one artifact — the platform-level constitutional codification of Donkey Betz's methodology. It belongs to the platform-constitutional workspace (Architecture & Research, once tagged), stored as a workspace-canonical Deliverable with a repo anchor and a RAG mirror. This is not novel — it is the second application of the KFI-1/2/5 pattern.

The mission's deeper question — *what is a Workspace intended to become?* — is answered by the evidence. The Playbook question resolves as a consequence.

Awaiting Chris's review.

---

_End of Session 2709 architecture proposal. No implementation performed. No workspace deliverables created. No ADRs opened. No Playbook authoring begun._

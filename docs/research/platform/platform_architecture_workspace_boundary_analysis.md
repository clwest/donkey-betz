# Platform Architecture & Workspace Boundary Analysis

**Session:** 2710 (architecture research only — Phase 2 of the platform-boundary discovery)
**Date:** 2026-07-08
**Status:** Research proposal — awaiting Chris's review
**Predecessors:**
- Session 2708: `docs/research/platform/engineering_playbook_architecture_proposal.md` (Playbook placement Option A/B/C)
- Session 2709: `docs/research/platform/workspace_architecture_and_constitution_proposal.md` (Workspace-as-Operator-OS framing)

**Scope constraints:** Architecture research only. No code changes. No migrations. No ADRs. No workspace deliverables. No Playbook authoring. No constitutional edits. No ratifications. No implementation planning. Repository ends clean (only this document + two untracked prior proposals). This document is the sole artifact of the session.

**Explicit intent per mission:** *"If, during the research, you discover that the previous Workspace report should be revised, document that explicitly with evidence. Do not force consistency with prior conclusions."* This report **does revise** two structural claims from 2709. Corrections are surfaced explicitly in §4.4 and §14.

---

## 1. Executive Summary

**Question:** What is the Platform intended to become?

**Answer from evidence:** Donkey Betz-the-platform is **an app inside a federated Fleet of ~7 sibling apps**, providing a *tenant-billed, user-owned, workspace-scoped AI-operator OS* to its users. The Platform is not the top of the stack. Above it sits **Fleet** — an already-modeled but partially-activated federation layer (`FleetServiceIdentity`, `FleetServiceKey`, `FleetEvent`, `FleetPAChatAuditRow`, `FleetArtifact`, `FleetPaidInterest`). Beneath the Platform sits **Tenant** — a modeled but 0-row SaaS-billing tier (`Tenant.subscription_tier`, `Tenant.monthly_cost_limit`, `Tenant.features`) with `CostTracking` (10,892 rows) and `Budget` (6 rows) infrastructure already flowing. Beneath Tenant sits **User** (9 rows, 201 user-scoped models). Beneath User sits **Workspace** (12 rows, 23 workspace-scoped models).

The Platform is therefore best described as: **a federated multi-tenant AI-operator-OS host — one node of the Fleet, running one Django/Celery/PostgreSQL/Redis stack, serving many Tenants, each with many Users, each with many Workspaces.**

**Key correction to Session 2709:** the 2709 report claimed *"no Organization model exists"* and that *"workspace = tenant boundary."* Both are wrong. A `Tenant` model exists in production code (0 rows). `AgentExecution.tenant`, `CostTracking.tenant`, `Budget.tenant`, and `UnifiedUser.tenant` FKs are all live. The **tenant boundary is UnifiedUser + Tenant, not Workspace.** Workspaces live *inside* a user's territory. `ProjectWorkspace` has no `tenant` FK. This changes the multi-tenant story significantly. Details in §4.4 and §12.

**Consequence for the Engineering Playbook:** the Playbook is a **platform-app-level constitutional artifact** — it governs how *donkey-betz-the-app* is engineered. It is not fleet-scoped (doesn't apply to signal-studio, mentorforge, character-os) and not workspace-scoped (doesn't belong inside a user's operator-OS territory). The recommended placement therefore *may need to shift* from 2708/2709's "workspace-canonical body + repo pointer" to a new pattern: **repo-canonical body + workspace-canonical ratification envelope.** This section is §14. It survives self-critique in §15.

**Recommendation:** Adopt the Platform-as-Fleet-Member framing. Formalize the six-layer stack (Fleet → Platform → Tenant → User → Workspace → Deliverable). Publish the Engineering Playbook as repo-canonical (in `docs/`) with workspace-canonical ratification records that name the git commit + tag. Cycle 1A's KFI-1/2/5 patterns are **preserved and reinforced** — they establish workspace-canonical as one of *two* first-class authority classes. The Playbook is repo-canonical because it governs the app, not the workspace.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Evidence base](#2-evidence-base)
3. [What the Platform actually is today](#3-what-the-platform-actually-is-today)
4. [Platform vs Workspace](#4-platform-vs-workspace)
5. [Platform responsibility model](#5-platform-responsibility-model)
6. [Workspace responsibility model](#6-workspace-responsibility-model)
7. [Repository responsibility model](#7-repository-responsibility-model)
8. [Runtime responsibility model](#8-runtime-responsibility-model)
9. [Layered architecture](#9-layered-architecture)
10. [Ownership matrix](#10-ownership-matrix)
11. [Dependency graph](#11-dependency-graph)
12. [Multi-tenant evolution](#12-multi-tenant-evolution)
13. [Missing architectural layers](#13-missing-architectural-layers)
14. [Engineering Playbook implications](#14-engineering-playbook-implications)
15. [Self-critique](#15-self-critique)
16. [Risks](#16-risks)
17. [Unknowns](#17-unknowns)
18. [Recommendation](#18-recommendation)
19. [Architectural consequences](#19-architectural-consequences)
20. [Closing assessment](#20-closing-assessment)

---

## 2. Evidence base

All claims in this report trace to one of the primary-evidence queries recorded here. Every count is ORM-derived. Every model relationship was confirmed by direct field introspection. Every classification is labeled **Verified / Likely / Inference / Unknown** at point-of-use.

### 2.1 Model census (Verified)

Query: iterate every registered Django model; classify by presence of `ProjectWorkspace` FK, `UnifiedUser` FK, or neither.

| Class | Count |
|---|---|
| Workspace-scoped models (have a `workspace` FK to `ProjectWorkspace`) | **23** |
| User-scoped but not workspace-scoped models | **201** |
| Global (neither user nor workspace) models — platform primitives | **333** |

**Immediate implication:** the workspace is the multi-tenant *scoping* boundary for a *minority* of the platform's models (23/557 = 4.1%). The overwhelming bulk of the platform is either user-attributed or platform-global.

### 2.2 Tenancy census (Verified — this is the 2709 revision)

Query: which models FK to `core.Tenant`?

| Model | Field | Row count | Notes |
|---|---|---|---|
| `core.UnifiedUser` | `.tenant` | 9 users, all `.tenant=None` | Users are modeled as tenant-scoped but no tenant is assigned |
| `core.EnhancedUserProfile` | `.tenant` | (not enumerated) | Extended profile carries tenancy |
| `core.AgentExecution` | `.tenant` | 1,494 rows; **0 with tenant filled** | Agent execution is designed for tenant attribution; not activated |
| `core.CostTracking` | `.tenant` | **10,892 rows;** tenant field per row | Every LLM call already recorded through the tenant lens |
| `core.Budget` | `.tenant` | 6 rows; all `.tenant=None` | Provider budgets ($20 Anthropic, $30 OpenAI, etc.) + system budgets; none tenant-scoped |

**`ProjectWorkspace` has NO `.tenant` FK.** Workspaces exist inside a user's account, not directly under a tenant. To trace a workspace to a tenant today, you must go workspace → user → tenant. But since `user.tenant=None` on all 9 users, the trace is broken; the platform is effectively single-tenant.

**0 `core.Tenant` rows exist in production.** The billing infrastructure is complete in code but has never been populated.

### 2.3 Fleet census (Verified — federation architecture)

Query: models containing `Fleet` in the class name.

| Model | Row count | Purpose |
|---|---|---|
| `core.FleetServiceIdentity` | 0 | Cross-app service identity (donkey-betz, signal-studio, mentorforge, etc.) |
| `core.FleetServiceKey` | 0 | HMAC signing keys per service |
| `core.FleetServiceRotation` | 0 | Key rotation events |
| `core.FleetAuthAuditLog` | 0 | Cross-service auth audit |
| `core.FleetArtifact` | 0 | Cross-app artifact exchange with SHA256 integrity + expiry |
| `core.FleetEvent` | **194** | Cross-app event bus — currently only `signal-studio` publishes (`signal.cluster_promoted` 144, `signal.curated_published` 25, `signal.curated_actions_ready` 25) |
| `core.FleetPAChatAuditRow` | **2,305** | Every `/api/pa/chat/` request logged with claimed vs verified app_slug — all rows show `auth_mode='bearer_only'`, `verified_app_slug=''`, `claimed_app_slug=''` (Fleet auth surface exists, is not gated) |
| `core.FleetPaidInterest` | 0 | Cross-app marketplace interest capture (`email`, `use_case`, `willing_pay`, `workspace_size`) — dormant |

**Conclusions from Fleet census:**

- **Verified:** Donkey Betz is a member of a fleet of federated apps. Cross-app identity (HMAC signing, key rotation, audit) is fully modeled but dormant.
- **Verified:** The Fleet event bus is *actively used* — `signal-studio` publishes 194 events; donkey-betz consumes them.
- **Verified:** The Fleet PA chat surface has 2,305 audited requests to `/api/pa/chat/`. None carry fleet identity claims. Fleet auth is observed but not enforced.
- **Likely:** The fleet includes at least donkey-betz + signal-studio. MEMORY.md (`feedback_fleet_caller_verification_before_celery_deletes`) references *"all 7 fleet apps + character-os"*, and `feedback_cross_repo_research_federated_rigby.md` names *mentorforge* and *character-os*. So the fleet is ≥3 apps and likely 7-8.
- **Inference:** `FleetPaidInterest.workspace_size` field suggests a cross-app SaaS marketplace where users express interest in workspaces sized to their use case.

### 2.4 Cost / Budget census (Verified)

| Field | Value |
|---|---|
| `CostTracking` rows | 10,892 |
| `CostTracking.provider` distribution | `openai`: 10,892 (100%) |
| `CostTracking.service` top | `gpt-5.2`: 10,459; `gpt-5-mini`: 433 |
| `Budget` rows | 6 |
| `Budget` scopes | 4 provider-scoped (Anthropic $20/day, DeepSeek $5/day, OpenAI $30/day, Together AI $10/day); 2 system-scoped (System $50/day, System $500/month) |
| `Budget.tenant` populated | 0/6 |

**Inference:** The Budget/Cost architecture supports tenant-scoped and workspace-scoped spend limits *by schema*, but no such rows exist today. Current active budgeting is by provider and by system (whole-installation). The "activate tenants → enforce per-tenant hard limits" path is one migration + one config change away.

### 2.5 User/Auth census (Verified)

| Field | Value |
|---|---|
| Total `UnifiedUser` rows | 9 |
| Users: | `chris`, `system`, `system_autonomous`, `dbg-bg`, `shell-test-a1`, `verify_regular_s1265`, `pr10-ex-d148af61`, `pr10-exercise-02ef6e23`, `pr11-ex-cea3f452` |
| MRO of `UnifiedUser` | `AbstractUser` → `AbstractBaseUser` → `PermissionsMixin` → `Model` — Django standard-plus-tenant |
| `UnifiedUser.tenant` populated | 0/9 |

Effective operational state: 1 real user (`chris`), 2 system accounts (`system`, `system_autonomous`), 6 test/exercise accounts.

### 2.6 Agent / Execution census (Verified — cross-referencing 2709)

| Field | Value |
|---|---|
| `core.Agent` DB rows | 91 (from CLAUDE.md live-count block: matches PLATFORM_INVENTORY figure of "83 in AGENT_MAP; 90 in Agent table" — 91 vs 90 is +1 drift, likely same-day) |
| `core.AgentExecution` rows | 1,494 |
| `.tenant` filled | 0 |
| `.user` filled | 542 (36%) |
| `.workspace` FK | **does NOT exist** |
| `.project` FK | present, → `PartnershipProject` |

**Critical:** AgentExecution has no direct workspace linkage. It is attributed via `.user`, `.tenant`, `.project` — but not `.workspace`. This confirms that workspace is not the multi-tenant boundary for the platform's compute layer.

### 2.7 Chat / PA scope (Verified — this is another 2709 revision)

| Field | Value |
|---|---|
| `ChatConversation` total | 2,538 |
| `.workspace` filled | **0 / 2,538** |
| `.user` filled | (nearly all — chris + system automation) |

**All 2,538 chat conversations have `workspace=None`.** The `ChatConversation.workspace` FK exists (2709 reported this correctly) but is **completely unused in production data.** Every Rigby PA conversation is user-scoped, not workspace-scoped. The CLAUDE.md guidance *"Rigby modes: `global` and `workspace`"* is aspirational at the model level; the DB shows only `global`.

### 2.8 Platform-primitive models (Global category, categorized — Verified)

Query: models with neither workspace nor user FK, categorized by name pattern.

| Category | Count | Examples |
|---|---|---|
| Agent primitives | 40 | AgentCategory, AgentControlEntry, AgentSpiderConnection, AgentKnowledgeSource, AgentTeam, AgentTeamMembership, TeamWorkflow, TeamWorkflowStep, AgentRole, AgentLifecycle, AgentCollaboration, … |
| Spider primitives | 11 | SpiderCategory, LegacySpiderData, SpiderDataAnnotation, SpiderItemHash, SpiderAnalytics, … |
| LLM primitives | 3 | `LLMProvider`, `LLMModel`, `LLMCallEvent` |
| Signal primitives | 4 | UserBehaviorSignal, SignalCluster, CuratedSignalSnapshot, CuratedSignalEntry |
| Memory primitives | 6 | MemoryConnection, MemoryPalaceRoom, MemoryCluster (30 rows), MemoryClusterMembership (162 rows), ClusterEvolution |
| RAG primitives | 8 | CaseDocument, LitigationDocument, DocumentRelationship, `ai_intelligence.LearningDocument`, LearningEmbedding, … (n.b. `content.Document` + `content.DocumentEmbedding` — the primary RAG surface — carry a `source` field but no direct `.workspace` FK) |
| Infra primitives | 10 | `django_celery_beat.*` (SolarSchedule, IntervalSchedule, CrontabSchedule, PeriodicTask, PeriodicTasks, ClockedSchedule), `django_celery_results.*` |
| Other platform primitives | 247 | `UnifiedUser`, `DiscordServerChannel`, `DiscordClient`, `Tenant`, `Budget`, `CostTracking`, and 241 more |

**Inference:** the *shape* of the platform is heavily tilted toward **cross-workspace primitives**. Only 23 of ~557 models are workspace-scoped. The workspace is a *thin* multi-tenant partition riding on a *deep* shared platform.

### 2.9 RAG census — canonical authority (Verified)

| `content.Document.canonical_authority` value | Count | Notes |
|---|---|---|
| `repo_canonical` | 2,986 | All have `source_reference=''` — data-quality anomaly |
| `workspace_canonical` | 7 | `0005`, `0010`, `0100`, `0110`, `0120`, `0130`, `MANIFEST_v20260707` |
| `derived` | 5 | Downstream / summary artifacts |

**Immediate discovery worth flagging (not scope of this session, but recorded):** `0140_ADR_DOCS_CASCADE_AUTOMATION`, `0150_ADR_CLAUDE_MD_BOOTSTRAP_POINTER`, and `0199_CYCLE_1_CLOSEOUT` — three ratified Cycle 1A artifacts — do **not** appear in the workspace_canonical Document set. The mirror cascade appears to have missed the tail of Cycle 1A. Non-scope, but reported.

**`content.Document` has no direct `.workspace` FK** — cross-workspace filtering happens via `source='workspace'` + `source_reference=<deliverable_id>` chain. This is thin. Multi-tenant will require strengthening.

### 2.10 Repository state (Verified)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `309f85ee` |
| Working tree | clean; two untracked prior-session proposals (`docs/research/platform/engineering_playbook_architecture_proposal.md`, `workspace_architecture_and_constitution_proposal.md`) |

---

## 3. What the Platform actually is today

Synthesizing the evidence:

### 3.1 The Platform's operational identity

- **Verified:** Donkey Betz is one Django+Celery+PostgreSQL+Redis+Daphne stack.
- **Verified:** It hosts 91 Agent DB rows + 83 AGENT_MAP agents + 80 spiders + 6 LLM providers + 96 Beat tasks.
- **Verified:** It exposes a PA (Rigby) function-calling surface via `/api/pa/chat/` — the most heavily-hit surface (2,305 fleet-audit rows for that path alone).
- **Verified:** It is a member of a Fleet (≥ donkey-betz + signal-studio; likely 7-8 apps total per external references).
- **Verified:** It has been designed for multi-tenant SaaS (`Tenant` model, `Budget` model, `CostTracking` per-tenant) but has not activated multi-tenancy (0 Tenant rows).
- **Verified:** It carries an operator-OS abstraction (`ProjectWorkspace` + 23 scoped models + 32 UI tabs + templates/pipelines) but 12/12 workspaces have empty `WorkspaceConfig`.

### 3.2 The Platform's architectural nature — attacking the mission's alternatives

The mission asked whether the Platform is: **Infrastructure? Operating System? Runtime? Network? Service Mesh? Federation? Control Plane? Something else?**

Attacking each in turn against the evidence:

**Infrastructure?** *Partial.* The Platform provides Postgres/Redis/Celery/Daphne — infrastructure. But it also provides agents, spiders, LLM routing, PA — these are not infrastructure primitives, they are higher-order services. Infrastructure alone under-describes.

**Operating System?** *Partial.* The 32-tab workspace UI + workspace_manager.py + autonomy gates + operations audit + rollback suggest "operator's OS at the workspace level." But that's a *workspace* framing, not a *Platform* framing. The Platform hosts the OS abstractions; it is not itself the OS.

**Runtime?** *Partial.* The Platform is a runtime for agents + tasks + PA. But it is *more* than a runtime — it has data, orchestration, governance, publishing.

**Network?** *No.* No routing/networking primitives at the platform level. Rejected.

**Service Mesh?** *Partial for Fleet layer.* The FleetServiceIdentity + FleetServiceKey + FleetEvent + FleetArtifact + FleetAuthAuditLog are exactly a service-mesh architecture. But this describes the *Fleet layer*, not the Platform. The Platform sits *inside* the mesh as one node.

**Federation?** *Yes for the Fleet layer.* Donkey Betz is one member of a federation. But again, this describes Fleet, not Platform.

**Control Plane?** *Partial.* Donkey Betz's PA + Beat + AgentExecution do resemble a control plane over a data plane. But the data plane (workspaces, deliverables, cost tracking) lives inside the same Postgres — not a real control/data split.

**Something else entirely?** *Yes — closest to:* **a federated multi-tenant AI-operator-OS host.** A single-app node inside a Fleet, providing tenant-billed user accounts, each user owning workspace-scoped AI-operator OSes, with an internal control plane (PA + Beat + agents) that coordinates workspace-scoped and cross-workspace work.

### 3.3 The direction of travel visible in the code

- **Verified:** Cycle 1A elevated workspace content to first-class canonical authority (KFI-1/2/5). Direction of travel: workspace is becoming a stronger source-of-truth for its own content.
- **Verified:** Fleet identity + PA chat auth surface is being *observed but not enforced.* Direction: readiness to lock down cross-app auth when needed.
- **Verified:** Tenant + Budget + CostTracking is *observing costs but not gating them.* Direction: readiness to activate SaaS multi-tenancy when a paying customer arrives (`FleetPaidInterest` schema suggests this is the exact expected path).
- **Verified:** WorkspaceTemplate defines 4 template shapes (newsletter, leadgen, research, custom) but 0 workspaces are template-bound. Direction: readiness for SaaS-templated workspace instantiation.
- **Inference:** The platform is being built as *if it will one day* run as a SaaS, but is currently operated as a single-user power tool.

---

## 4. Platform vs Workspace

The mission asked this to be answered rigorously. Here is the boundary as the evidence shows it.

### 4.1 The Platform is above the Workspace

- **Verified:** ProjectWorkspace has no `.tenant` FK; it inherits tenancy through `user.tenant`. The Platform is the multi-tenant container; the Workspace lives *inside* a tenant slice.
- **Verified:** 91% of models are NOT workspace-scoped. The Platform runs a substantial cross-workspace domain (LLM providers, agents, spiders, memory clusters, signal clusters, RAG documents, Fleet layer, budgets) that has nothing to do with any single workspace.
- **Verified:** Runtime (Celery workers, Beat schedule) is shared across all workspaces. Workspace does not scope compute.

### 4.2 The Workspace is above the Deliverable

- **Verified:** Deliverables (524 rows, all with `workspace` set) belong to exactly one workspace. There is no cross-workspace Deliverable.
- **Verified:** WorkspaceOperation (5,707 rows) is fully workspace-scoped. Audit belongs inside the workspace.
- **Verified:** Media (ImageHistory, VideoHistory, AudioHistory) is workspace-scoped.

### 4.3 The Platform-vs-Workspace tension is diagonal, not vertical

The prior sessions framed this as a strict vertical stack. Evidence shows a **diagonal** relationship:

| Domain | Workspace-owned | Platform-owned |
|---|---|---|
| Content (Deliverables, media) | ✓ | ✗ |
| Audit trail | ✓ | ✗ |
| Configuration (template, autonomy gates) | ✓ | ✗ |
| Governance content (ADRs) | ✓ (per Cycle 1A) | ✗ (in principle) |
| Chat conversations | *modeled ✓; actual usage all user-global (0/2,538 workspace-attributed)* | *effective ✓* |
| Agent code | ✗ | ✓ |
| Agent DB rows (persona registry) | ✗ | ✓ |
| Agent execution records | *no workspace FK* | ✓ (routed via user + tenant + project) |
| Spider crawls | ✗ | ✓ |
| LLM providers/models | ✗ | ✓ |
| Signal/memory clusters | ✗ | ✓ |
| RAG documents + embeddings | *thin `source='workspace'` link* | ✓ effectively |
| Cost tracking | ✗ (per-user, per-tenant) | ✓ |
| Budgets | ✗ (per-provider, per-tenant) | ✓ |
| Beat schedule | ✗ | ✓ |
| Fleet identity | ✗ | ✓ |
| Repository (code) | ✗ | ✓ |

**Verified pattern:** the workspace owns the *creative/operational outputs* of one AI-operator; the platform owns *everything that operates.* This is a *producer-vs-substrate* split, not a top-vs-bottom stack.

### 4.4 What Session 2709 got wrong (evidence-based corrections)

**Correction 1 — On the existence of an Organization/Tenant layer.**

Session 2709 §8.3 stated: *"This layer does not exist in the codebase (verified: no Organization model exists in the multi-app inventory)."*

**This is factually wrong.** The `core.Tenant` model exists at `core.Tenant (table=core_tenant)` with fields `owner (→UnifiedUser)`, `subscription_tier`, `monthly_cost_limit`, `monthly_cost_used`, `features (JSON)`, `is_active`, plus reverse relations from `UnifiedUser`, `EnhancedUserProfile`, `AgentExecution`, `CostTracking`, `Budget`. Zero rows exist in production, but the model is fully defined and integrated.

**Root cause of the 2709 error:** the previous inventory queried by class name filtering for `'organization' / 'tenant' / 'workspace'`; the class *is* named `Tenant` but the previous query iterated only workspace-focused models. This was a scoping bug in the evidence gathering, not a modeling gap in the platform.

**Impact on 2709 conclusions:**
- 2709's §8.3 "missing Organization / WorkspaceGroup" recommendation is **partly wrong**: `Tenant` already exists as the org layer. The remaining gap is workspace-to-tenant linkage (no `ProjectWorkspace.tenant` FK) and team-workspace membership (no `WorkspaceMembership` model — `AgentTeam`/`AgentTeamMembership` exist for agent teams, not user teams).
- 2709's §5.3 recommendation that Playbook "belongs to the platform-constitutional workspace" needs to be re-examined against the correct tenancy chain.

**Correction 2 — On workspace as tenant boundary.**

Session 2709 §2(a) stated: *"Workspace is the first-class tenant key across 23 models."*

**Verified refinement:** Workspace is a scoping *boundary* for 23 models, but the *tenant key* is `UnifiedUser` + `Tenant`. The workspace does not scope compute (Celery, Beat), cost (CostTracking), or governance-of-the-platform-itself (Fleet, Tenant, Budget). Workspace is a scoping boundary for **workspace-owned outputs**, not for the platform's tenant model.

**Impact:** the "workspace = tenant" framing led 2709 to place platform-level constitution (the Playbook) inside a workspace. That may be architecturally inverted — see §14.

**Correction 3 — On Fleet.**

Session 2709 made no mention of Fleet. This is a significant gap: donkey-betz is a member of a Fleet, and Fleet cross-cuts everything above the Platform. The Playbook question needs to consider whether the Playbook is app-scoped (donkey-betz-only) or fleet-scoped (all 7 apps).

---

## 5. Platform responsibility model

The Platform (donkey-betz-the-app) is responsible for:

**Primitives it provides:**

- **Authentication** — via UnifiedUser (Django AbstractUser); fleet identity via FleetServiceIdentity (dormant).
- **Messaging** — Discord bot (48 slash + 48 prefix commands), PA chat (`/api/pa/chat/`), FleetEvent bus consumption.
- **Memory** — MemoryCluster (30 rows), MemoryClusterMembership (162), SignalCluster (653), ClusterEvolution. Cross-workspace knowledge accumulation.
- **Agents** — 83 AGENT_MAP + 91 DB rows + BaseAgent (5,575 LOC). Platform-owned; per-execution attribution to (user, tenant, project) — not workspace.
- **Tool routing** — 152 tool handlers + 109 tool schemas via unified_pa_entrypoint.
- **Execution** — Celery workers (7 queues per Procfile), agent_router, task orchestration.
- **Scheduling** — 96 Beat tasks (91 enabled + 5 disabled).
- **Knowledge (retrieval)** — `content.Document` (2,998 rows) + `content.DocumentEmbedding` (58,532 rows) + authority-aware retrieval (ADR-0130).
- **Publishing** — Deliverable model + PublishGate state machine + `content_tool.content_complete`.
- **Governance surface** — Deliverable types (ADR, ratification_record, cycle_open, cycle_close) + workspace-canonical mirror.
- **Observability** — 9 body systems (HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN), OpsRun audit, FleetEvent bus.
- **Infrastructure abstraction** — WorkspaceProject / PreviewEnvironment / ProjectRepo / ProjectEnvVar for per-workspace project management.
- **Workspace lifecycle** — WorkspaceManager service (2,381 LOC) with FileWriter / GitIntegrator / WorkspaceScanner.
- **Cost & budgeting** — CostTracking (10,892 rows) + Budget model (6 rows, provider- and system-scoped).
- **Fleet membership** — FleetPAChatAuditRow (2,305) + FleetEvent (194 consumed).
- **Multi-tenant billing (dormant)** — Tenant model + tenant-scoped Budget schema.

**Platform is responsible for these; workspaces consume them.** The Playbook (§14) governs *how the Platform builds these primitives* — this is a platform-level concern, not a workspace-level one.

**Platform is NOT responsible for:**

- Workspace content (Deliverables, media, chat within a workspace).
- Workspace-specific configuration (template binding, autonomy gates, deliverable categories, quotas per workspace).
- Workspace-specific audit (WorkspaceOperation).
- Individual users' AI-augmented decisions (governance content *inside* a workspace).

---

## 6. Workspace responsibility model

The Workspace (each `ProjectWorkspace` row) is responsible for:

- **Its own content lifecycle** — Deliverables it holds (all 524 in the system are workspace-attributed; 25 in Architecture & Research).
- **Its own audit** — WorkspaceOperation (5,707 rows total, all workspace-attributed).
- **Its own configuration** — WorkspaceConfig (template, agent_pool, spider_subscriptions, deliverable_categories, quotas, governance_mode) — presently null across all 12 rows.
- **Its own codebase context** — WorkspaceContext (`file_tree`, `key_files`, `total_lines_of_code`) when applicable. 3 rows exist (not all workspaces).
- **Its own triggers / automations** — WorkspaceTrigger (0 rows).
- **Its own creative outputs** — blogs, podcasts, campaigns, content packets, initiatives (via `target_workspace`).
- **Its own governance** — ADRs, ratification records, cycle open/close records ARE workspace-owned (per Cycle 1A KFI-1/2/5) *for artifacts that govern the workspace itself.* The distinction between workspace-scoped-governance and platform-scoped-governance was not previously drawn; §14 draws it now.

**Workspace is NOT responsible for:**

- Platform primitives it consumes (agents, spiders, LLM providers, memory, RAG, Beat).
- Runtime resources (Celery, Redis) — shared across all workspaces.
- Cost tracking of its own compute — CostTracking is (user, tenant)-scoped, not workspace-scoped.
- Fleet-level identity or event participation.
- Platform-level governance (e.g., "how the platform is engineered") — this is Playbook territory, and see §14.

---

## 7. Repository responsibility model

The Repository (git) is responsible for:

- **All executable code** — Python, TypeScript, migrations, tests.
- **All infrastructure config** — Procfile, Makefile, Docker, requirements, package.json.
- **Platform-substrate documentation** — CLAUDE.md, MEMORY.md, 00-START-NEXT-SESSION.md, `docs/PLATFORM_INVENTORY.md`, `docs/PLATFORM_WHAT_IT_IS.md`, `docs/topics/*`, `docs/handoffs/*`, `docs/DATABASE_MODEL_REFERENCE.md`.
- **Cross-workspace guardrails** — `scripts/verify_repo_guardrails.py`, autogen index guards.
- **Repo-canonical L1 constitution about the Platform itself** — this is a category proposed here for the first time (§14). Includes:
  - Engineering Playbook (governing how the app is engineered).
  - Platform-level ADRs about repo structure, code patterns, migration discipline.
  - Anything that governs the *substrate* rather than the *tenant workspaces*.

**Repository is NOT responsible for:**

- Any workspace's own governance artifacts (customer's ADRs, per-workspace policies).
- Per-tenant configuration.
- Per-user data.
- Anything mutable at runtime (all mutable state lives in Postgres/Redis).

**Repository IS responsible for:**

- Providing a **stable substrate** the platform runs on. Whatever the repo says at `HEAD` is *what the platform is*.

---

## 8. Runtime responsibility model

Runtime (Postgres + Redis + Celery + Beat + Daphne) is responsible for:

- **State** — everything that changes between deploys lives here.
- **Cross-workspace execution** — Celery workers process tasks across all workspaces without workspace-scoping.
- **Cross-tenant compute** — no tenant-partitioned queues today.
- **Scheduling** — 96 Beat tasks span workspace and platform concerns.

Runtime is **shared substrate**. It has no workspace or tenant awareness at the queue level. Multi-tenant scaling requires adding this awareness (workspace-priority queues, tenant-scoped quotas — infrastructure not yet built; per §12).

---

## 9. Layered architecture

The evidence supports **six layers** (revised from 2709's five-layer + L0 human):

### Layer 0 — Human intent

The ratifier. Chris today. Every ratified decision traces back to a human directive.

### Layer 1 — Fleet

**Verified:** ≥2 apps (donkey-betz, signal-studio); likely 7-8 apps total.

- Cross-app identity (FleetServiceIdentity, FleetServiceKey, FleetServiceRotation — 0 rows; dormant).
- Cross-app event bus (FleetEvent — 194 rows; active, one-direction).
- Cross-app PA chat surface (FleetPAChatAuditRow — 2,305 rows; observed).
- Cross-app artifact exchange (FleetArtifact — 0 rows; dormant).
- Cross-app auth audit (FleetAuthAuditLog — 0 rows; dormant).
- Cross-app marketplace (FleetPaidInterest — 0 rows; dormant).

**Owns:** federation identity, cross-app protocol, cross-app trust.

**Home:** Fleet-level models in each member app; possibly a Fleet control plane (unknown — see §17 U-2).

### Layer 2 — Platform (Donkey Betz app)

The Django+Celery+Postgres+Redis+Daphne stack running as the donkey-betz fleet member.

**Owns:** all primitives from §5.

**Home:** repository + running processes.

### Layer 3 — Tenant (SaaS billing tier)

`Tenant` model. Dormant (0 rows) but modeled.

**Owns:** subscription tier, monthly cost limit, feature flags per tenant, budgets scoped to tenant.

**Home:** Postgres + `Tenant` model.

### Layer 4 — User (`UnifiedUser`)

The individual person. 9 rows.

**Owns:** identity, authentication, session, all 201 user-scoped models (personal profile, preferences, extended profile, conversation memory, resume, job applications, custom workflows, shared projects, applications, budgets, revenue, etc.).

**Home:** Postgres + `UnifiedUser` model.

### Layer 5 — Workspace (AI-operator OS)

`ProjectWorkspace`. 12 rows.

**Owns:** what 2709 correctly described — an operator's OS boundary. 23 workspace-scoped models.

**Home:** Postgres + `ProjectWorkspace` model.

### Layer 6 — Deliverable / Content / Media / Chat

Workspace-scoped outputs.

**Owns:** the specific ratified/published/draft content of the workspace.

**Home:** Postgres.

### Ancillary layer — RAG (retrieval)

Not a stack layer; a **derived indexing plane** over L2 (repo docs) + L5/L6 (workspace content). Governed by `canonical_authority` (workspace_canonical / repo_canonical / derived).

### Visual

```
Layer 0: Human intent (Chris; future: customer tenant admin)
    │
    ▼
Layer 1: Fleet (donkey-betz + signal-studio + mentorforge + character-os + ~3 more)
    │  FleetServiceIdentity/Key/Event/Artifact — cross-app federation
    │
    ▼
Layer 2: Platform (this app — donkey-betz)
    │  Agents, spiders, LLM providers, memory clusters, signal clusters
    │  RAG index, PA function-calling, Beat scheduler, Celery workers
    │  Tenant model, Budget, CostTracking — SaaS-billing infrastructure
    │  Repository = source-of-truth for the platform's own definition
    │
    ▼
Layer 3: Tenant (SaaS-billing tier — MODELED but 0 rows)
    │  Subscription tier, cost limits, feature flags
    │
    ▼
Layer 4: User (UnifiedUser — 9 rows)
    │  Person identity, 201 user-scoped models
    │  Owns Workspaces
    │
    ▼
Layer 5: Workspace (ProjectWorkspace — 12 rows)
    │  AI-operator OS; 23 workspace-scoped models
    │  Constitutional-mode possible per workspace (Architecture & Research)
    │
    ▼
Layer 6: Deliverable / Content / Chat / Media
    │  Workspace-scoped outputs
    │
    ═══════════════════════════════════
    RAG (derived, indexes L2 repo docs + L5/L6 workspace content)
    Governed by canonical_authority (repo_canonical vs workspace_canonical)
```

---

## 10. Ownership matrix

| Concern | Owner Layer | Owner Model | Notes |
|---|---|---|---|
| Federation identity | Fleet (L1) | `FleetServiceIdentity` | Dormant |
| Cross-app events | Fleet (L1) | `FleetEvent` | 194 published by signal-studio |
| Cross-app PA surface | Fleet (L1) | `/api/pa/chat/` + `FleetPAChatAuditRow` | Observed, not enforced |
| Executable code | Platform (L2) | Git repo | Repo-canonical |
| Agents (persona) | Platform (L2) | `Agent` DB rows + AGENT_MAP | Cross-workspace |
| Spiders | Platform (L2) | Spider registry + `SpiderItemHash` | Cross-workspace |
| LLM providers | Platform (L2) | `LLMProvider`, `LLMModel`, `LLMCallEvent` | Cross-workspace |
| Memory clusters | Platform (L2) | `MemoryCluster` (30) | Cross-workspace |
| Signal clusters | Platform (L2) | `SignalCluster` (653) | Cross-workspace |
| RAG index | Platform (L2) | `content.Document` + `content.DocumentEmbedding` | Derived from L2 + L5/L6 |
| Celery / Beat / Redis | Platform (L2) | Runtime | Shared; not workspace-scoped |
| Discord bot | Platform (L2) | 25 Cogs, 144 commands | Cross-workspace |
| SaaS billing | Tenant (L3) | `Tenant`, `Budget`, `CostTracking` | Infrastructure ready; 0 tenants |
| Person identity | User (L4) | `UnifiedUser` | 9 users |
| Person's data | User (L4) | 201 user-scoped models | Includes profile, preferences, resume, applications, custom workflows |
| Workspace config | Workspace (L5) | `WorkspaceConfig` | 12 rows; all empty |
| Workspace context | Workspace (L5) | `WorkspaceContext` | 3 rows |
| Workspace operations audit | Workspace (L5) | `WorkspaceOperation` (5,707) | Fully workspace-scoped |
| Deliverables | Workspace (L5)→(L6) | `Deliverable` (524) | Includes ratified governance |
| Media (image/video/audio) | Workspace (L5)→(L6) | `ImageHistory`, `VideoHistory`, `AudioHistory` | 14 rows total |
| Chat conversations | *modeled workspace-scoped; actually user-global* | `ChatConversation` (2,538, 0 workspace-attributed) | Data anomaly / evolving pattern |
| Agent execution | Platform (L2) with User (L4) + Tenant (L3) attribution | `AgentExecution` (1,494) | **No workspace linkage** |

---

## 11. Dependency graph

The evidence supports these directions of dependency:

```
Fleet (L1)
  └── depends on multiple Platforms (L2) as members
        │
        │  (donkey-betz is one member)
        ▼
Platform (L2)
  ├── depends on Repository (git) for its own code
  ├── depends on Runtime (Postgres, Redis, Celery, Beat, Daphne) for state + execution
  ├── depends on RAG for retrieval
  ├── depends on Agents / Spiders / LLM providers as internal primitives
  ├── provides Tenant (L3) as billing surface
  ├── provides User (L4) as identity/auth
  ├── provides Workspace (L5) as operator-OS
  └── provides Deliverable/Content/Chat/Media (L6) as scoped outputs

Tenant (L3)
  ├── hosts Users (L4)
  └── consumes Platform (L2) primitives, billed against tenant budget

User (L4)
  ├── belongs to Tenant (L3)
  ├── owns Workspaces (L5)
  ├── carries 201 user-scoped models (identity, prefs, resume, apps, memory, etc.)
  └── consumes Platform (L2) primitives (agents, PA, RAG)

Workspace (L5)
  ├── owned by User (L4)
  ├── binds a WorkspaceTemplate for shape
  ├── declares WorkspaceConfig (agent_pool, spiders, categories, quotas, governance_mode)
  ├── holds Deliverables (L6) + WorkspaceOperations audit
  └── consumes Platform (L2) primitives via workspace-aware execution context

Deliverable (L6)
  ├── belongs to Workspace (L5)
  ├── mirrors into RAG (content.Document) via KFI-1 cascade
  ├── governed by PublishGate state machine
  └── ratified via workspace-canonical ratification records
```

**Verified:** dependencies flow *down* (Fleet at top, Deliverable at bottom). No layer depends on the layer below it, except for Workspace-owning-Deliverables (which is a containment, not a dependency).

**Verified:** the Platform *provides primitives that Workspaces compose*, matching the mission's third framing ("Platform provides primitives that Workspaces compose"). Neither "Platform owns Workspace" nor "Workspace builds Platform" is quite right — the Platform is the *substrate*; Workspaces are *compositions on the substrate*.

---

## 12. Multi-tenant evolution

### 12.1 At 10 tenants

- **What changes:** Activate the `Tenant` model — create 10 Tenant rows. Assign `UnifiedUser.tenant`. Attach `AgentExecution.tenant` at every call. Enforce `Budget.tenant` hard limits.
- **What remains platform-wide:** All 82 categorized platform primitives (agents, spiders, LLM providers, memory, signal, RAG, infra). The repo itself.
- **What becomes workspace-local:** Nothing new — workspaces are already local. But *tenants* now scope users.
- **Missing infrastructure:** Workspace-to-tenant linkage (add `ProjectWorkspace.tenant` FK OR treat workspace-owner's tenant as authoritative).

### 12.2 At 100 tenants

- **What changes:** Per-tenant quotas actually get enforced. Cost per tenant gets displayed to tenant admins. Feature flags on `Tenant.features` gate access to expensive primitives (agents, spiders).
- **What remains platform-wide:** Fleet layer; runtime; agent code; spider code; RAG index; Beat scheduling *core* (though some tasks may need tenant-partitioning).
- **What becomes workspace-local:** Per-workspace agent_pool binding starts to matter — tenants pay for capabilities they use.
- **Missing infrastructure:** Workspace-priority queues in Celery (all 100 tenants share the same queue today — noisy-neighbor risk). Beat needs tenant awareness for tenant-scoped scheduled tasks.

### 12.3 At 1,000 tenants

- **What changes:** RAG index needs per-tenant filtering (Document.workspace_id or Document.tenant_id — neither exists today). Rigby retrieval must respect tenant boundaries (no leakage of Tenant A's data to Tenant B's queries).
- **What remains platform-wide:** Agent + spider code; LLM provider list; Fleet layer.
- **What becomes workspace-local:** More templated instantiation. WorkspaceTemplate finally gets used at scale (currently 0 use).
- **What cannot become workspace-local:** Global RAG requires strong per-tenant enforcement. Fleet identity. Platform-level constitution (the Playbook). Beat schedules for platform-wide health checks.
- **Missing infrastructure:** Per-tenant sharding or partitioning of Postgres. Per-tenant RAG isolation.

### 12.4 At 10,000 tenants

- **What changes:** Single-Postgres instance is likely inadequate. Redis needs per-tenant memory partitioning. Celery needs per-tenant priority classes.
- **What remains platform-wide:** Fleet; repo; core substrate.
- **What becomes workspace-local:** Nearly all data-plane concerns. Every read/write is tenant-scoped.
- **What cannot become workspace-local:** The repository. The Fleet layer. The Playbook (still governs how *donkey-betz-the-app* is engineered).
- **Missing infrastructure:** Everything that would make this operate as a real multi-tenant SaaS at 10K scale. Session 2710 is not that plan.

### 12.5 The load-bearing observation

**At every scale from 10 to 10,000, the Repository and the Fleet layer remain platform-wide.** The Playbook, if it governs the Platform, is repository-scoped. It never becomes workspace-local because *there is not one Playbook per workspace* — the Playbook is what makes the Platform *the* platform.

This is the load-bearing observation for §14.

---

## 13. Missing architectural layers

The mission asked whether a missing layer is emerging. Evidence review:

### 13.1 Layer verified as PRESENT (contra 2709)

- **Fleet (L1) — VERIFIED PRESENT.** 8 Fleet-named models. Cross-app auth + event bus + audit. Not missing.
- **Tenant (L3) — VERIFIED PRESENT.** `Tenant` model. Not missing.

### 13.2 Layer verified as MISSING

- **Team / WorkspaceMembership between User and Workspace — MISSING.**
  - `AgentTeam` (0 rows) and `AgentTeamMembership` (0 rows) exist for *agent* teams, not user teams.
  - `SharedProject` + `ProjectCollaborator` exists but scopes a `SharedProject`, not a `ProjectWorkspace`.
  - No `WorkspaceMembership` model links a `ProjectWorkspace` to multiple users.
  - Consequence: at multi-tenant scale, workspaces cannot be shared across users on a team. This is a genuine architectural gap.

- **Workspace-to-tenant direct linkage — MISSING.**
  - `ProjectWorkspace` has no `.tenant` FK.
  - Workspace-tenant relationship is inferred through `workspace.user.tenant`.
  - Consequence: tenant-scoped queries against workspaces require a JOIN through UnifiedUser.

- **Domain / Mission — NOT NEEDED.**
  - The mission asked if a `Domain` or `Mission` layer should be introduced. Evidence does not support this. The existing `WorkspaceTemplate` category field + `WorkspaceConfig.governance_mode` are sufficient for expressing workspace domain / mission. No new layer required.

### 13.3 The "should Platform be a Workspace?" question

The mission demanded this be pressure-tested. Attacking three positions:

**Position A — Platform should be its own Workspace.**

*Steelman:* Just create a `donkey-betz-platform` ProjectWorkspace. Put the Playbook there. Use the same governance surface Cycle 1A ratified.

*Attack:*
- Recursive ownership problem — the Platform *contains* Workspaces. A workspace inside itself is a category error.
- The Platform runs the runtime; a workspace does not run runtime. The Platform is a level *above* workspaces.
- Which user owns this workspace? `chris` (personal) or `system_autonomous` (platform automation)? Neither correctly captures "the Platform itself."
- 91% of the Platform's models are outside the workspace-scoped set. Even if you created a `platform` workspace, most of what the Platform IS wouldn't live in it.

*Verdict:* rejected.

**Position B — Platform exists ABOVE all workspaces (own layer).**

*Steelman:* Platform is Layer 2 in the six-layer stack. It provides primitives. Its constitutional artifacts (Playbook, platform ADRs) live at the Platform layer, in the repository (its source of truth for its own definition).

*Attack:*
- Contradicts Cycle 1A's workspace-canonical direction? Partially — but Cycle 1A defined *two* first-class authorities (workspace_canonical + repo_canonical). It never said workspace beats repo *always*; it said workspace beats repo *when both mirror the same content*. Repo-canonical is legitimate for repo-native content.
- Where do platform ADRs get ratified? — In a workspace, as governance envelopes (ratification records) that name the git commit/tag. The body lives in git; the ratification envelope lives in workspace.

*Verdict:* survives.

**Position C — Platform itself is NOT a Workspace.**

*Steelman:* the Platform is a different kind of thing — a running app, not a scoped output-container. Trying to represent it as a workspace forces the wrong shape.

*Attack:*
- Doesn't preclude Position B.
- Position C is a *negative* claim; positive claim needs to identify where Platform-level constitution *does* live.

*Verdict:* consistent with Position B.

**Combined verdict:** Position A rejected; Positions B + C are effectively the same and survive. **The Platform is a distinct layer above all workspaces; the Platform is NOT itself a workspace.**

---

## 14. Engineering Playbook implications

Now the deferred question, revisited with the new architecture.

### 14.1 Which layer does the Playbook govern?

- **NOT Fleet (L1).** The Playbook does not govern signal-studio, mentorforge, character-os. It governs donkey-betz-the-app.
- **NOT User (L4).** Doesn't belong to Chris personally or a customer's user account.
- **NOT Workspace (L5).** Doesn't belong to any user's operator-OS.
- **NOT Deliverable (L6).** It's not a workspace output.
- **NOT Tenant (L3).** A tenant's SaaS billing is orthogonal.
- **YES Platform (L2).** The Playbook governs how the Platform is engineered — which is exactly what L2 encompasses.

### 14.2 Where do L2 (Platform) constitutional artifacts live?

The Platform's source of truth for its own definition is the **repository (git)**. This is uncontroversial: `main` is what the Platform *is*. Every deploy is `git checkout <sha>; run migrations; restart`.

Therefore: **the Platform's own constitution is repo-canonical.**

This is not new. `CLAUDE.md` at repo root is already a de-facto constitutional file (session-open orientation contract). `MEMORY.md` at repo root is a de-facto behavioral-standards file. `docs/DOC_LIFECYCLE.md`, `docs/AUDIT_FINDINGS.md`, `docs/EMPLOYEE_OS_PRIMITIVES.md` are all repo-canonical governance-adjacent artifacts.

The Playbook joins this set as the *first-class* codification of platform engineering standards.

### 14.3 Comparison: 2709 recommendation vs 2710 evidence

| Question | 2708 answer | 2709 answer | 2710 evidence-based answer |
|---|---|---|---|
| Where does the Playbook body live? | Workspace (Option C hybrid) | Workspace (Architecture & Research) | **Repository (`docs/`)** |
| Where does the Playbook ratification record live? | Workspace | Workspace | Workspace (unchanged) |
| Does the Playbook mirror to RAG? | Yes | Yes | Yes (repo→RAG) |
| Repo anchor file needed? | Yes | Yes | N/A — body IS in repo |
| Retrieval authority | `workspace_canonical` | `workspace_canonical` | `repo_canonical` |
| Immutability substrate | PublishGate + `status=completed` | PublishGate + `status=completed` | git tag + commit hash + workspace ratification-record envelope naming both |

The 2710 shift is: **from workspace-canonical body with repo pointer, TO repo-canonical body with workspace ratification envelope.**

### 14.4 Why the shift is architecturally coherent (attack + defense)

**Attack: "But Cycle 1A moved constitution INTO the workspace! Aren't we reversing that?"**

- No. Cycle 1A moved *workspace-level* constitution (ADRs about how workspace deliverable/mirror/authority works) into the workspace. That's the correct place for governance content that *governs the workspace subsystem*.
- The Playbook is different — it governs how *the platform-as-a-whole* is engineered. Different scope. Different natural home.
- ADRs 0110/0120/0130/0140/0150 all address workspace-adjacent subsystems (mirror, authority, retrieval, cascade, CLAUDE.md pointer). They belong workspace-canonical because they're workspace-scoped concerns. Future platform-scope ADRs (e.g., "how the Celery queue architecture works" or "how Fleet auth is enforced") would be *repo-canonical*.

**Attack: "Why does Playbook need a workspace ratification envelope? If it lives in git, git tags are enough."**

- Git tags encode "v1.0 exists" but not "v1.0 was ratified by Chris on 2026-XX-YY with directive '…'". Cycle 1A explicitly established that the *ratification directive* is part of the historical record and must be preserved verbatim in a first-class artifact.
- Workspace ratification records already handle this pattern. Making the ratification-record's *parent* be a git commit/tag rather than a workspace deliverable is a small pattern extension, not a category shift.

**Attack: "But this breaks the KFI-5 anchor pattern uniformity."**

- KFI-5 established that a repo file can *point at* workspace-canonical truth. It didn't establish that all L1 content must be workspace-canonical.
- KFI-2's `canonical_authority` field explicitly encodes *two* authorities. Both are first-class. Choosing repo_canonical for the Playbook exercises the pattern, doesn't undermine it.

**Attack: "Doesn't this make session-open orientation harder?"**

- No. Repo-canonical `docs/ENGINEERING_PLAYBOOK.md` is a `Read` at session-open — cheaper than the KFI-5 anchor pattern.

**Attack: "What if Chris wants immutable-on-write for the Playbook?"**

- Workspace ratification record provides the governance envelope (immutable status=completed).
- Git tag provides the immutable body (commit hash is cryptographic).
- Amendment: to change the Playbook, cut a new git tag AND create a new ratification record. Same discipline as before, different substrate.

### 14.5 The refined placement pattern for the Playbook

**Refined placement (2710):**

- **Body:** `docs/ENGINEERING_PLAYBOOK.md` in the repo. Managed as a first-class documentation artifact. Version-tagged (`playbook-v1.0`, `playbook-v1.1`).
- **Ratification envelope:** Workspace deliverable in Architecture & Research workspace, of type `ratification_record`, whose body names:
  1. The git tag being ratified (`playbook-v1.0`).
  2. The commit SHA at that tag (immutable).
  3. Chris's verbatim ratification directive.
  4. Provenance classification per PIC-10.
- **RAG:** Playbook is mirrored into `content.Document` with `canonical_authority='repo_canonical'`. Rigby retrieves it authority-aware.
- **CLAUDE.md linkage:** L7 blockquote extends to reference the Playbook: *"Engineering standards: `docs/ENGINEERING_PLAYBOOK.md` (currently ratified at git tag `playbook-v1.X`)."*

**Amendment lifecycle:**

1. Draft revisions on a branch.
2. Apply SIGN cycle (per Cycle 1A methodology).
3. PR merge → new commit SHA.
4. Tag as `playbook-vX.Y`.
5. Chris ratification directive.
6. Workspace ratification record created naming the tag + SHA + directive.
7. RAG cascade includes new tag content.
8. CLAUDE.md L7 blockquote is regenerated to reference the new tag.

**This is a new pattern.** It reuses Cycle 1A primitives without breaking them.

---

## 15. Self-critique

The mission demanded ≥6 serious alternatives, steelmanned, then rejected only with evidence.

### 15.1 Alternative A — Playbook as workspace-canonical (2709 recommendation)

**Steelman:** the pattern established by Cycle 1A. Uniformity across all L1 artifacts (ADRs + Playbook). PIC-10 provenance classification natively maps to `Deliverable.metadata` JSONField. `parent_object_id` for version chain. Consistent narrative from KFI-1/2/5.

**Attack:**
- Wrong-scope container: the Playbook governs the platform, not any single workspace or user's territory. Placing it inside a user-owned workspace inverts the ownership relation.
- The 12 workspaces are all user-owned. There is no *platform-owned* workspace. Even proposing to rename Architecture & Research doesn't fix this — the User FK is set to `chris`, not to the platform.
- Multi-tenant future: if the Playbook lives in chris's user account's workspace, transferring platform ownership requires transferring a user-owned artifact. Wrong direction.

**Verdict:** rejected. Evidence about tenancy chain (§4.4 correction) undermines this option.

### 15.2 Alternative B — Playbook as repo-canonical with workspace ratification envelope (2710 recommendation)

**Steelman:** Matches the actual ownership scope (Platform → repo). Reuses Cycle 1A ratification primitives without breaking the workspace-owned pattern for genuinely workspace-scoped content. Reuses git-native immutability + cryptographic hashes for body. Ratification envelope carries the governance narrative.

**Attack:**
- Introduces a new pattern (repo body + workspace ratification envelope). Cycle 1A trained one pattern; introducing a second creates cognitive load.
- Anchor semantics diverge: KFI-5 was workspace→repo pointer; the new pattern is workspace→repo *ratification of body*.
- Requires new cascade tooling.

**Defense:** the pattern IS the natural symmetric complement to KFI-5. `canonical_authority` already encodes both — this exercises the KFI-2 architecture rather than adding to it.

**Verdict:** survives. Recommended.

### 15.3 Alternative C — Playbook as fleet-canonical (living in a Fleet-level constitutional store)

**Steelman:** if the Playbook governs *engineering standards for AI-augmented product apps*, it might apply to all 7 fleet apps, not just donkey-betz. That would make it fleet-scoped.

**Attack:**
- Evidence contradicts: PIC-1..10 (the Playbook's raw material) is derived from Cycle 1A's donkey-betz-specific implementation experience. Not fleet-general.
- The Fleet layer (L1) is dormant — no fleet-scoped constitutional artifact exists today. Creating one for the Playbook prematurely activates a layer.
- Signal-studio, mentorforge, character-os likely have their own engineering standards.

**Verdict:** rejected. Playbook is app-scoped (donkey-betz), not fleet-scoped.

### 15.4 Alternative D — Playbook as tenant-canonical (per-tenant Playbook)

**Steelman:** each customer defines their own engineering standards. Multi-tenant SaaS futures might allow customers to customize.

**Attack:**
- The Playbook governs *donkey-betz-the-app*, not what customers do inside it. It's platform-authored, not tenant-authored.
- Confuses "how the platform is built" with "how a tenant uses the platform." Only the latter is per-tenant.

**Verdict:** rejected. Distinguish platform-authoring-Playbook from tenant-usage-guidance (which could be per-tenant, but that's a different artifact).

### 15.5 Alternative E — No Playbook; ADRs alone suffice

**Steelman:** ADRs already encode individual decisions. Aggregating them into a Playbook adds a layer of abstraction that might drift from the source ADRs.

**Attack:**
- The 10 PICs in 0199 Appendix D are cross-cutting methodology, not per-decision facts. ADRs don't naturally aggregate.
- Chris explicitly deferred Playbook authoring pending architecture (00-START-NEXT-SESSION.md §Current governance state) — proposing to skip it now overrides that plan.
- Sessions 1234, 1802 etc. surfaced repeated methodology patterns that are exactly what a Playbook codifies. Without it, the methodology remains folk knowledge.

**Verdict:** rejected. Playbook is needed.

### 15.6 Alternative F — Playbook as `CLAUDE.md` extension

**Steelman:** `CLAUDE.md` is already a repo-canonical file that governs Claude's behavior. Extend it to include Playbook content.

**Attack:**
- `CLAUDE.md` is a *behavioral prompt* for Claude Code, not an *engineering standards document* for the platform. Different audiences (Claude vs Chris/engineers/customers), different immutability contract, different structure.
- Mixing them makes the file too long for effective session-open reading.
- MEMORY.md warning already fires at 423 lines; this compounds the problem.

**Verdict:** rejected. Playbook stays separate, but the two coexist as repo-canonical L2/L1 hybrid.

### 15.7 Alternative G — Playbook as knowledge-graph node

**Steelman:** cross-cutting methodology naturally maps to a knowledge graph with edges to ADRs, PICs, ratifications.

**Attack:**
- No knowledge graph exists in the codebase (2709 §10.3 established this).
- Building one adds Cycle 3+ scope to Cycle 2 territory.

**Verdict:** deferred. Interesting future architecture; premature now.

### 15.8 Alternative H — Playbook lives BOTH in repo AND in workspace (dual-canonical)

**Steelman:** duplicate to maximize discoverability. Repo for git-native access; workspace for governance-native immutability.

**Attack:**
- Cycle 1A explicitly rejected dual-canonical because it creates drift. `canonical_authority` field enforces single-canonical per artifact.
- Introduces a governance defect: which is *the* canonical version?

**Verdict:** rejected. Single-canonical (repo) with ratification-envelope-in-workspace is not dual-canonical — it's separation of body and governance metadata.

### 15.9 Alternatives that survived attack

Only Alternative B (Playbook repo-canonical with workspace ratification envelope) survives full attack. Alternative A (2709's recommendation) fails on tenancy-chain evidence. All others fail on other structural grounds.

---

## 16. Risks

| # | Risk | Severity | Notes |
|---|---|---|---|
| R1 | 2709 report is now partly wrong (Tenant model exists; workspace ≠ tenant boundary). Downstream sessions may still cite it. | Med | This document is the corrective; needs to be discoverable by future sessions. |
| R2 | Introducing the new "repo body + workspace ratification envelope" pattern requires Cycle 2 tooling. | Low | Additive; not a rollback. |
| R3 | Fleet layer is dormant but real. Any future work that touches PA chat auth or FleetEvent needs to consider fleet identity. | Med | Increases scope of any auth-related change. |
| R4 | Tenant model has zero rows in prod. Activating it requires migration of existing chat/deliverable/execution records to a "default tenant." | Med | Cycle 3+ concern. |
| R5 | `ChatConversation.workspace` is 0/2,538. Either the field should be removed or the linkage should be populated retroactively. | Low | Data-quality anomaly. Cycle 2 candidate. |
| R6 | `AgentExecution` has no workspace linkage — governance queries cannot ask "which workspace's agents ran?" | Med | Multi-tenant future must resolve. |
| R7 | Cycle 1A cascade appears to have missed 0140/0150/0199 workspace-canonical mirror rows. | Low (already ratified; RAG drift) | Non-scope but reported. |
| R8 | RAG has no direct workspace_id / tenant_id filtering. Multi-tenant leak risk. | High (at scale) | Cycle 3+ scope. |
| R9 | Playbook v1.0 authored using pre-Playbook methodology (bootstrap paradox). | Med | Same as 2708 R4 / 2709 R12. |
| R10 | Playbook body-in-repo means changes go through PR review, which is faster than SIGN cycle — could bypass governance if not disciplined. | Med | Cycle 2 tooling should require SIGN cycle before tag creation. |
| R11 | Session-scoped workspaces (Sessions 1171/1172/1173/1231) show workspace-as-ephemeral pattern. If this grows, workspace inventory bloats. | Low | 2709 R11 unchanged. |
| R12 | Repository-Playbook approach introduces a new pattern; Cycle 1A trained one. Cognitive load risk. | Low | Mitigated by explicit doc + Playbook itself explaining both patterns. |

---

## 17. Unknowns

| # | Unknown | Why it matters | How to resolve (not this session) |
|---|---|---|---|
| U1 | Whether Fleet has a control-plane or is peer-to-peer | Determines whether donkey-betz is fleet-central or fleet-member | Grep for a "fleet controller" / "fleet coordinator" service; check the other fleet apps (mentorforge/character-os) |
| U2 | Whether other fleet apps have their own Playbook-like artifacts | Determines if the pattern is shareable | Cross-repo research (per `feedback_cross_repo_research_federated_rigby`) |
| U3 | Whether `Tenant.subscription_tier` values are enumerated (free/pro/enterprise) | Determines multi-tenant feature-gate design | Read `Tenant` model field-choice metadata |
| U4 | Whether `WorkspaceTemplate` catalog is planned to grow (constitutional / engineering / legal) | Determines whether the Playbook itself becomes a template | Check open GitHub issues / research OS |
| U5 | Whether `ChatConversation.workspace=null` is a bug or intentional | Determines whether workspace-scoping is a design axis | Grep `ChatConversation` write paths; check the PA session model |
| U6 | Whether `AgentExecution` should acquire a `.workspace` FK | Determines whether Cycle 2 governance queries can be workspace-scoped | Design discussion (Cycle 2 candidate) |
| U7 | Whether Beat tasks can be tenant-scoped | Determines multi-tenant scheduling isolation | Beat schema (`django_celery_beat.PeriodicTask`) — likely no tenant field, would need custom addition |
| U8 | Whether the 2,986 repo_canonical Documents' empty `source_reference` is a data-quality bug or by design | RAG debuggability | Read `sync_docs_index_to_documents` source |
| U9 | Whether MemoryCluster + SignalCluster carry any workspace / tenant scope | Cross-tenant memory leakage risk | ORM introspect |
| U10 | Whether `Deliverable.workspace` being non-null on 524/524 is enforced or coincidental | Data integrity contract | Check `Deliverable` model field constraints |

---

## 18. Recommendation

### 18.1 Architectural framing

Adopt the six-layer stack (§9) as the canonical Platform architecture:

**Fleet → Platform → Tenant → User → Workspace → Deliverable/Content.**

Adjunct: RAG as derived indexing plane over Platform (L2 repo) + Workspace (L5/L6) content, governed by `canonical_authority` per KFI-2.

### 18.2 Platform-vs-Workspace boundary

**Platform (L2) owns:** everything cross-workspace — agents, spiders, LLM, memory, signal, RAG, runtime, Fleet layer, Tenant/Budget/CostTracking infrastructure, repository as source-of-truth for its own definition.

**Workspace (L5) owns:** its own outputs, config, context, audit, and workspace-scoped governance (ADRs about the workspace subsystem, per Cycle 1A).

**Repository owns:** all Platform-level executable + configurable + constitutional content. This includes the Engineering Playbook.

### 18.3 Engineering Playbook placement

**Adopt Alternative B (§15.2):** Playbook body lives in the repository (`docs/ENGINEERING_PLAYBOOK.md`); workspace ratification records name the git tag + commit SHA + Chris's ratification directive.

**This is a revision from Sessions 2708 and 2709.** The revision is justified by the tenancy-chain evidence in §4.4 (Tenant model exists; workspace = user-scoped, not tenant-scoped) and the platform-vs-workspace layering evidence in §4.3 (Platform is a distinct layer above Workspace, and the Playbook governs the Platform).

**Both prior sessions remain useful:**
- 2708 correctly enumerated the Option A/B/C tradeoff space.
- 2709 correctly identified the Workspace-as-Operator-OS framing.
- 2710 adds the Platform layer above the Workspace and corrects the tenancy-chain error.

**KFI-1/2/5 is preserved and reinforced:**
- KFI-1 mirror remains valid for workspace-canonical content.
- KFI-2 canonical_authority remains the correct governance-vocabulary field, with *both* values first-class.
- KFI-5 CLAUDE.md L7 anchor remains valid for workspace-canonical artifacts pointed at from repo.
- The Playbook uses the *symmetric complement* — repo body + workspace ratification envelope.

### 18.4 Do NOT (yet)

- **Do not create the Playbook.** Architecture research only.
- **Do not open new ADRs.** No 0200-series.
- **Do not activate the Tenant model.** Multi-tenant readiness is Cycle 3+ scope.
- **Do not populate `ChatConversation.workspace`** retroactively. Data-quality concern for Cycle 2.
- **Do not touch Cycle 1A ratified artifacts.** Immutable.
- **Do not modify the untracked prior-session proposals.** They stand as-authored.

---

## 19. Architectural consequences

If the recommendation is accepted, the following architectural consequences follow. **Not implementation steps** — architectural implications.

### 19.1 Immediate (before Playbook v1.0)

- The Platform layer becomes explicit in the layer model. Future docs should reference L2 = Platform, distinct from L5 = Workspace.
- The tenancy chain becomes explicit: Fleet → Platform → Tenant → User → Workspace. Any multi-tenant discussion cites this chain.
- The 2709 correction (Tenant exists) must be discoverable — this document is the correction.
- The Playbook placement pattern must be stated in the Playbook itself as a §0 architectural framing: "This document lives repo-canonical; ratification records live workspace-canonical."

### 19.2 Cycle 2 candidates (from architectural implications)

- Introduce a management command to reconcile ratification records with git tags (governance envelope creation).
- Extend `verify_repo_guardrails.py` to check the Playbook has an active ratification record naming the current git tag.
- Consider adding `.workspace` FK on `ChatConversation` writes (or removing the field if truly unused).
- Consider whether the Cycle 1A cascade should catch 0140/0150/0199 mirror-drift (evidence in §2.9).

### 19.3 Cycle 3+ candidates (multi-tenant activation)

- Populate `Tenant` rows for known users (default tenant per user, or single "self" tenant for Chris).
- Activate `Budget.tenant` scope for per-tenant hard limits.
- Add `ProjectWorkspace.tenant` FK (or accept transitivity through user.tenant).
- Add `content.Document.workspace_id` or `.tenant_id` for RAG multi-tenant isolation.
- Introduce `WorkspaceMembership` for shared-user workspaces (fills the gap identified in §13.2).

### 19.4 Cycle 4+ candidates (fleet-scale readiness)

- Activate `FleetServiceIdentity` for donkey-betz self-identity.
- Sign PA chat requests with fleet HMAC.
- Consume FleetEvent bus more broadly.
- Publish donkey-betz events into the fleet bus.

---

## 20. Closing assessment

**The Platform is intended to become — and already partially is — a federated multi-tenant AI-operator-OS host.**

- **Fleet-member** (donkey-betz is one of ~7 apps sharing identity + event + PA chat surface).
- **Multi-tenant** (Tenant model exists; SaaS billing infrastructure is complete but dormant).
- **User-owned** (9 users, 201 user-scoped models — deep personal-productivity substrate).
- **Workspace-scoping** (12 operator-OS containers, 23 workspace-scoped models — creative output surface).
- **Substrate-first** (91% of the code is platform-primitive, not workspace-scoped — the Platform is a lot bigger than any single workspace).

The **Engineering Playbook** is a platform-level constitutional artifact. Its natural home is the repository. Its ratification story reuses Cycle 1A primitives (workspace ratification records) applied to a new substrate (git commits/tags). This is a symmetric complement to KFI-5, not a departure from Cycle 1A.

**Session 2709 was wrong on tenancy structure but right on Workspace-as-Operator-OS.** This session corrects the tenancy layer while preserving the workspace framing.

**Session 2710 was necessary.** Without it, the Playbook would have landed inside a user-owned workspace container that does not match its actual scope of governance. That was going to be a governance defect, not a governance improvement.

**Session 2711 (next) — architecture-review only:** should verify:
1. Whether Chris accepts the six-layer framing.
2. Whether Chris accepts the tenancy-chain correction (2709 →2710).
3. Whether Chris accepts the Playbook-in-repo placement OR wants further evidence before shifting.
4. Whether Chris wants to close the architecture-research phase and begin Playbook authoring, or extend research further.

**Do not** begin Playbook implementation without this decision. The wrong home is worse than delay.

---

_End of Session 2710 architecture research. No implementation performed. No workspace deliverables created. No ADRs opened. No Playbook authoring begun. Repository ends clean (this document + two untracked prior proposals only)._

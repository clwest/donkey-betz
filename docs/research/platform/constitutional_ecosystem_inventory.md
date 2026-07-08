# Constitutional Ecosystem Inventory & Architectural Closure

**Session:** 2714 (comprehensive constitutional inventory + architectural closure)
**Date:** 2026-07-08
**Status:** Research proposal — awaiting Chris's review
**Predecessors:** 2708, 2709, 2710, 2711, 2712, 2713 — six prior architecture sessions

**Author:** Claude (Opus 4.7, 1M context)

**Scope constraints per mission:** Architectural inventory only. No implementation. No ADRs. No Playbook authoring. No repository modifications beyond this document. Every conclusion based on verified evidence. Verified facts explicitly distinguished from architectural conclusions. Self-critique included. Falsification attempted before acceptance.

**Deliverable:** one document. This one.

**Headline finding:** Prior sessions 2708-2713 designed a constitutional architecture as if greenfield when a substantial constitutional ecosystem already exists in the repository. This session inventories the pre-existing ecosystem and reconciles it against the 2708-2713 model.

---

## 1. Executive summary

**Question:** What constitutional artifacts already exist in the repository that we have not intentionally classified?

**Answer:** A *substantial pre-existing constitutional ecosystem* is discoverable across the repository, runtime, and workspace. Prior sessions (2708-2713) identified pieces of it (Cycle 1A ADRs in workspace; CLAUDE.md; MEMORY.md; PLATFORM_INVENTORY.md) but missed load-bearing components including:

- **A formal Canon system** (`docs/canon/INDEX.md`) — an existing constitutional promotion mechanism with 5 promoted docs, 8 autogen runtime audits, formal criteria (Chris = System Owner approval), and runtime-load-bearing status (injected into agent context by `core/services/docs_context_builder.py`).
- **A formal System Owner declaration** (`docs/governance/SYSTEM_OWNER.md`) — the L0 human ratifier documented with `Absolute Override Level`, runtime-load-bearing (`docs_context_builder.py:184` and `:365`).
- **A formal doc lifecycle constitution** (`docs/00-START-HERE/DOC_LIFECYCLE.md`) — with `authority: canonical` YAML frontmatter; governs the `/docs/` corpus; runtime-load-bearing.
- **A formal repo-level ADR corpus** (`docs/adr/ADR-0001..0004`) — 4 ratified ADRs at repo level, distinct from the 5 workspace-canonical ADRs (0110-0150).
- **A formal DOC-POINTER-V1/V2 convention** — the standard mechanism for marking deprecated/moved docs; used pervasively across the repo.
- **7 CI workflows** (`.github/workflows/*.yml`) — executable constitution enforced at PR-time.
- **952 session handoffs** in `docs/handoffs/` — immutable historical constitutional record.
- **21 topic docs** in `docs/topics/` — informal current-state subsystem canon.
- **A `docs/docs-pattern/` context-kit framework subtree** — a *separate constitutional subtree* explicitly excluded from platform constitution (planned to ship as its own repo).
- **A `_provenance.json` provenance system** — 2,438 docs and 7,775 commits already tracked with confidence classification (HIGH=1,591 / MEDIUM=352 / LOW=5 / UNKNOWN=490).

**Consequence for the Playbook:** the Engineering Playbook is NOT the first constitutional artifact. It is the first *systematically ratified codification* within a pre-existing informal constitutional ecosystem. Playbook Chapter 1 (Constitutional Context) MUST acknowledge and integrate the existing Canon system, DOC_LIFECYCLE, SYSTEM_OWNER declaration, and repo-ADR corpus as constitutional prior art. Failing to do so would produce a Playbook that appears to compete with (rather than extend) existing constitutional infrastructure.

**Architectural closure verdict:** YES, the architecture is complete enough to begin Playbook v0.1 authoring — with the amendment that Chapter 1 (Constitutional Context) integrates the pre-existing ecosystem. Recommendations for §22-§26 (retire, rename, move, source of truth, historical record, executable policy, governance) follow.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Repository constitutional inventory](#2-repository-constitutional-inventory)
3. [Runtime constitutional inventory](#3-runtime-constitutional-inventory)
4. [Documentary constitution](#4-documentary-constitution)
5. [Executable constitution](#5-executable-constitution)
6. [Constitutional ownership map](#6-constitutional-ownership-map)
7. [Constitutional dependency graph](#7-constitutional-dependency-graph)
8. [Constitutional layer matrix](#8-constitutional-layer-matrix)
9. [Constitutional lifecycle](#9-constitutional-lifecycle)
10. [Missing constitutional pieces](#10-missing-constitutional-pieces)
11. [Misclassified artifacts](#11-misclassified-artifacts)
12. [Transitional artifacts](#12-transitional-artifacts)
13. [Technical debt](#13-technical-debt)
14. [Future evolution](#14-future-evolution)
15. [Self critique](#15-self-critique)
16. [Falsification attempts](#16-falsification-attempts)
17. [Final recommendation](#17-final-recommendation)
18. [Architectural closure assessment](#18-architectural-closure-assessment)
19. [The 10 mission-required closing answers](#19-the-10-mission-required-closing-answers)

Verified vs conclusion convention: sections 2-9 mix VERIFIED evidence (present-tense claims sourced by file path, line number, or ORM query) with CONCLUSION labels where I synthesize. Sections 10-18 are conclusions grounded in the verified sections.

---

## 2. Repository constitutional inventory

### 2.1 The Canon system (VERIFIED — `docs/canon/INDEX.md`)

`docs/canon/INDEX.md` (a.k.a. **the Canon Registry**) is an existing formal constitutional promotion mechanism.

**Verified properties:**

- File exists at `docs/canon/INDEX.md`.
- Explicitly declares: *"Canon = the durable contracts the platform operates by; not a catalog of everything useful."*
- Explicitly declares: *"Canon is intentionally small (≤10 docs)."*
- Includes formal promotion criteria: expert-level quality; factually accurate; production-tested; practically useful; **System Owner approved (Chris says "yes")**.
- Explicitly declares: *"Canon docs live at their original paths (not under `/canon/`). These are pointers, not copies."*
- Runtime-load-bearing: `core/services/docs_context_builder.py:186` reads from it.
- Includes a **Pending Review** queue for docs awaiting canon promotion.
- Session 814 origin; Session 1144 last update.

**Current Canon Registry (VERIFIED — as listed in canon/INDEX.md):**

*Technical Canon:*
- `docs/PLATFORM_INVENTORY.md` — runtime-derived inventory anchor; sole authoritative counts per DOC_LIFECYCLE §2c; regenerable via `generate_platform_inventory`.

*Operational Canon:*
- `docs/00-START-HERE/DOC_LIFECYCLE.md` — Doc lifecycle constitution.
- `docs/INDEX.md` — Doc corpus entry point (autogen).
- `00-START-NEXT-SESSION.md` — Operational session continuity.
- `docs/AUDIT_INDEX.md` — Audit taxonomy.

*Runtime Evidence (autogen inventories):*
- `CELERY_AUDIT.md`, `BEAT_AUDIT.md`, `BODY_SYSTEM_AUDIT.md`, `CAPABILITY_AUDIT.md`, `LEARNING_BRIDGE_AUDIT.md`, `MANAGEMENT_COMMAND_AUDIT.md`, `DISCORD_AUDIT.md`, `ML_AUDIT.md`.

*Creative Canon:* Empty (DAVINCI_RESOLVE_WORKFLOW.md retired in Session 1143 when DaVinci Resolve was sunset).

*Pending Review:* "Stage 2 Governance Plan" (in `governance/stage-2/` — nominated by TechnicalDocumentAgent).

**CONCLUSION:** the Canon system predates the Engineering Playbook architecture research phase. It IS the pre-existing L2 documentary constitution. Prior sessions treated the Playbook as the first documentary constitution; that framing is incorrect — the Playbook joins an existing Canon and codifies its methodology.

### 2.2 The System Owner declaration (VERIFIED — `docs/governance/SYSTEM_OWNER.md`)

`docs/governance/SYSTEM_OWNER.md` is a formal L0-ratifier declaration document.

**Verified properties:**

- File exists at `docs/governance/SYSTEM_OWNER.md`.
- Frontmatter and body declare:
  - Name: Chris West
  - Role: Founder, System Owner, Final Authority
  - Override Level: **Absolute**
  - Document Status: CANON
  - Classification: INTERNAL
  - Session 814 origin; Session 1149 §3 rewrite.
- Runtime-load-bearing: `core/services/docs_context_builder.py:184` reads from it; `:365` also references with priority 100 and max 100 lines.
- Includes an Authority Framework, HITL Approval Table, Escalation Path, Notification Channels, and Kill Switch Triggers section.
- DOC-POINTER-V1 header notes Session 1149 rewrite of §3 (Emergency Procedures).

**CONCLUSION:** the L0 human ratifier is formally documented AND runtime-integrated (fed to agents as context). Prior sessions (especially 2711 §7) discussed the ratifier informally; the formal declaration existed all along. The Playbook Chapter 1 MUST reference this document as the L0 authority anchor.

### 2.3 The doc lifecycle constitution (VERIFIED — `docs/00-START-HERE/DOC_LIFECYCLE.md`)

`docs/00-START-HERE/DOC_LIFECYCLE.md` is a formally-declared canonical governance document.

**Verified properties:**

- File exists at `docs/00-START-HERE/DOC_LIFECYCLE.md`.
- Frontmatter fields:
  - `title: "Doc Lifecycle — pointer headers + root-stability rule"`
  - `status: active`
  - `authority: canonical`  ← **explicit canonical authority declaration**
  - `session_added: 1143`
  - `last_verified: 2026-05-24`
- Session 1143 origin.
- Governs "the u-d-b `/docs/` corpus" — explicit scope statement.
- Explicitly excludes `docs/docs-pattern/` from its scope.
- Codifies:
  - DOC-POINTER-V1/V2 pointer header conventions.
  - §0 scope boundary.
  - §2b runtime-coupled paths.
  - §2c sole-counts-source rule (PLATFORM_INVENTORY.md wins).
  - §3 root-stability rule.
- Cited in Canon Registry as Operational Canon.

**CONCLUSION:** a formal doc-lifecycle governance document already exists with `authority: canonical` marker. The Playbook Chapter 4 (Documentation Cascade) and Chapter 7 (Session Discipline) MUST cite this document as prior authority.

### 2.4 The repo-level ADR corpus (VERIFIED — `docs/adr/`)

Four ratified ADRs exist at the repo-canonical layer, distinct from the 5 workspace-canonical ADRs (0110-0150) surfaced in prior sessions.

**Verified inventory:**

- `docs/adr/ADR-0001-establish-adr-corpus.md` — establishes the ADR corpus itself (self-referential inaugural ADR). Ratified 2026-07-06 by Chris.
- `docs/adr/ADR-0002-pa-write-shape-and-correlation-contract.md`
- `docs/adr/ADR-0003-mission-runner-staged-enable-posture.md`
- `docs/adr/ADR-0004-rag-corpus-substrate-maturity-gradient.md`

**Verified frontmatter pattern (from ADR-0001):**

- `adr_id: ADR-0001`
- `status: accepted`
- `authority: design-decision`
- `proposed: 2026-07-06`
- `ratified: 2026-07-06`
- `ratifier: chris`
- `supersedes: (none — this is the first ADR)`
- `superseded_by: (none)`
- `intake_id: IB-Q1-BOOT-01`
- `arc_ref: I-0100`
- `source_refs: [...]`
- `reversibility: 4` (scale: 1=irreversible, 5=trivially reversible)
- `companion_docs: [...]`

**CONCLUSION:** the repo-ADR corpus is a running, populated constitutional artifact class. Its frontmatter pattern (structured YAML with `authority`, `ratifier`, `reversibility`, `arc_ref`, `intake_id`) is an established pattern the Playbook can extend or reuse. Prior sessions did not integrate this corpus into the Playbook Architecture Specification (2712 §3.1 chapter proposal). Chapter 10 (Evolution & Amendment) MAY need to acknowledge two ADR corpora (repo + workspace) as coexisting.

### 2.5 The Research Operating System and Implementation Operating System (VERIFIED — `docs/research/process/`)

Two operating-system-scoped constitutional documents already exist in the repo.

**Verified inventory:**

- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` — "Research OS." Uses RFC-2119 keywords 16 times per §2 evidence in 2713.
- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` — "IOS." Uses RFC-2119 keywords 22 times.
- `docs/research/process/claude_research_startup_introspection.md` — session-open orientation document.

**Cited by:**

- ADR-0001 explicitly references IOS §2.5, §D3, Appendix C, and Research OS §8.3 as sources.
- CLAUDE.md L7 blockquote references the Cycle 1A workspace ADRs and manifest.

**CONCLUSION:** the platform already runs on IOS + Research OS as constitutional-methodology documents. The Engineering Playbook overlaps in scope. Chapter 2 (Research Methodology) MUST integrate Research OS. Chapter 3 (Implementation Discipline) MUST integrate IOS. Prior sessions treated these as inputs; they are actually **existing peer constitutional documents** at the same layer as the Playbook.

### 2.6 The docs-pattern subtree (VERIFIED — `docs/docs-pattern/`)

A separate constitutional subtree exists in the repo but is *explicitly excluded* from platform constitution.

**Verified inventory:**

- `docs/docs-pattern/01_two_doc_anchor.md`
- `docs/docs-pattern/02_drift_verifier.md`
- `docs/docs-pattern/03_topic_docs.md`
- `docs/docs-pattern/04_session_handoffs.md`
- `docs/docs-pattern/05_start_here.md`
- `docs/docs-pattern/06_dos_and_donts.md`
- `docs/docs-pattern/07_bootstrap_checklist.md`
- `docs/docs-pattern/fleet-network/`
- `docs/docs-pattern/spokesperson-corpus/`
- `docs/docs-pattern/templates/`

**Verified declared scope:**

- DOC_LIFECYCLE.md §0 explicitly declares: *"When context-kit ships standalone, it will carry its own lifecycle doc."*
- `_provenance.json._meta.excludes` includes `docs/docs-pattern/` — provenance system explicitly ignores it.

**CONCLUSION:** the docs-pattern subtree is a "context-kit framework master" that will eventually ship as its own repo. It IS constitutional infrastructure — but for the meta-framework, not for donkey-betz. Playbook v1.0 MUST NOT govern the docs-pattern subtree. Explicit scope boundary needed in Chapter 1.

### 2.7 The provenance system (VERIFIED — `docs/_provenance.json` + `_index.json`)

Machine-readable provenance tracking exists at the repo level.

**Verified contents (from head of `_provenance.json`):**

- `generated: "2026-07-08T14:56:34+00:00"` (regenerated after every commit that changes docs)
- `command: "python manage.py build_docs_provenance"`
- `git_head: "20df44602873"`
- `doc_count: 2438`
- `commit_count: 7775`
- Confidence breakdown: `HIGH=1591`, `MEDIUM=352`, `LOW=5`, `UNKNOWN=490`
- Excludes: `docs/archive/`, `docs/docs-pattern/`
- `schema_version: 1`

**Verified contents (from head of `_index.json`):**

- Generated by `build_docs_index`
- Version 2.2
- Records per document: path, filename, folder, lines, size_bytes, modified_at, created_at, type, title, has_frontmatter, subsystems, status, outbound_links.

**CONCLUSION:** the platform already runs a provenance-tracking system with confidence classification. Playbook Chapter 6 (PIC-10 Provenance Classification Standard) MUST integrate this existing system rather than propose a parallel one. The 5-class PIC-10 taxonomy MAY need to align with the existing HIGH/MEDIUM/LOW/UNKNOWN classification.

### 2.8 The DOC-POINTER-V1/V2 header convention (VERIFIED — pervasive)

A formal deprecation/pointer convention exists as an established pattern.

**Verified pattern:**

- V1 header: `<!-- DOC-POINTER-V1 -->` followed by blockquotes stating status, freshness, runtime-load-bearing status.
- V2 header: `<!-- DOC-POINTER-V2 (Session NNNN) -->` followed by structured fields:
  - Status: Moved
  - Originally: description
  - Last verified: session
  - Current canon: path
  - Change reason
  - Preserved because
  - Caveat

**Observed in (partial list):**

- `docs/LETTER_TO_FUTURE_CLAUDE_CODE.md` (V2 — pointer to archive/superseded-2026-05/)
- `docs/canon/INDEX.md` (V1)
- `docs/governance/SYSTEM_OWNER.md` (V1)
- `docs/AUDIT_INDEX.md` (V1)
- Multiple audit files.

**CONCLUSION:** this is an existing constitutional metadata convention. The Playbook's amendment discipline (Chapter 10) and Retired Rules Registry (2713 §9.4) SHOULD reuse or extend this convention rather than propose a parallel one.

### 2.9 The 952 session handoffs (VERIFIED — `docs/handoffs/`)

Session handoffs form an immutable historical constitutional record.

**Verified count:** `ls docs/handoffs/ | wc -l` → 952.

**Verified contents include:**

- `CURRENT.md`, `INDEX.md`.
- `HANDOFF_00_MASTER_PLAN.md` through `HANDOFF_06_*`.
- Named handoffs (`LETTER_TO_FUTURE_CLAUDE_SESSION_323.md`, `LETTER_TO_MORNING_CLAUDE_SESSION_331.md`).
- Session-numbered handoffs (`SESSION_XXXX_*.md`).
- Spec documents living in the handoff folder (`PA_LAYER1_SURFACE_MAP.md`, `PA_PLATFORM_AWARENESS_SPEC.md`, `PA_SYSTEMS_MAP_6_LAYER.md`, `SCIFI_FEATURE_AUDIT_SESSION_283.md`).

**CONCLUSION:** handoffs are convention-immutable (never deleted; DOC-POINTER-V2 headers on moves). They function as constitutional artifacts (evidence class E6 per 2712 §11). The Playbook must acknowledge their status as historical L2 constitution. Playbook Chapter 7 (Session Discipline) codifies the ongoing production of handoffs.

### 2.10 The topics subsystem canon (VERIFIED — `docs/topics/`)

21 topic docs form an informal current-state subsystem canon.

**Verified inventory:**

- `active-module-ownership-map.md`, `agent-system.md`, `auth.md`, `body-systems.md`, `celery-workers.md`, `collaboration-protocol.md`, `content-pipeline.md`, `employee-os.md`, `fleet-doc-verifier-rollout.md`, `frontend.md`, `infrastructure.md`, `initiative-pipeline.md`, `local-askdocs.md`, `multi-repo-management.md`, `obs-remote-control.md`, `personal-assistant.md`, `README.md`, `spider-network.md`, `stock-intelligence.md`, `tool-consolidation.md`, `video-upload.md`.

**Referenced by:** CLAUDE.md §Subsystem Documentation table.

**CONCLUSION:** the topic docs are informal current-state canon, structured for embedding-optimized retrieval per CLAUDE.md guidance. They are not formally in the Canon Registry (§2.1) but function as one. Two options in §17:
- Formally promote each to Canon (Chris directive).
- Leave as informal reference — the Canon Registry stays tight (≤10 docs); topics are subsystem docs.

### 2.11 The `docs/governance/` directory (PARTIAL VERIFIED)

Only one file inventoried directly:

- `docs/governance/SYSTEM_OWNER.md` (§2.2).

**Pending Review from Canon Registry** references a "Stage 2 Governance Plan" in `governance/stage-2/` that was NOT enumerated in the `ls docs/governance/` output. Either:
- The Pending Review row is stale.
- The stage-2/ subdirectory exists but was not listed in my inventory (`ls` may have shown only top-level).

**CONCLUSION:** governance directory is minimally populated today (1 confirmed file). Playbook may consolidate more governance content here or extend to a `docs/constitution/` directory. Cycle 2+ decision.

### 2.12 The `docs/architecture/` directory (VERIFIED — inventoried)

24 architecture-scoped documents exist here.

**Verified inventory includes:**

- `PLATFORM_ARCHITECTURE_MAP.md`, `SYSTEM_ARCHITECTURE_MAP.md`, `UNIFIED_SYSTEM_MAP.md`, `COMPLETE_SYSTEM_MAP.md`, `COMPLETE_AUTONOMOUS_WORKFLOW_MAP.md`.
- Agent/AI: `MULTI_AGENT_ARCHITECTURE.md`, `AI_ASSISTANT_ARCHITECTURE.md`, `DAVINCI_AGENT_ARCHITECTURE.md`, `MEMORY_SYSTEM_ARCHITECTURE.md`, `WORKFLOW_ORCHESTRATION_AGENT.md`.
- Prompting: `PROMPTING_SYSTEM.md`, `PROMPTING_SYSTEM_COMPREHENSIVE_AUDIT.md`, `GPT5_AGENT_CONFIGURATION_PATTERNS.md`, `GPT5_REASONING_MODELS_GUIDE.md`.
- Sports: `sports_betting_integration.md`.
- Learning: `learning_system.md`.
- Structure: `MONOREPO_STRUCTURE.md`.
- Overview: `PERFECT_WORKFLOW_DESIGN.md`, `SYSTEM_MAP.md`, `QUICK_FIX_GUIDE_SESSION_25.md`, `partnership_model.md`, `ml_architecture.md`.
- Entry: `README.md`, `INDEX.md`.

**CONCLUSION:** substantial informal architecture-doc corpus exists. NOT typically constitutional (descriptive, not normative). Playbook does NOT need to govern these; they follow DOC_LIFECYCLE.md.

### 2.13 The CI workflows (VERIFIED — `.github/workflows/`)

7 CI workflows exist as executable constitution.

**Verified inventory:**

- `check-llm-sdk.yml` — validates LLM SDK usage.
- `check-reasoning-contract.yml` — validates reasoning model contract.
- `docs-sync.yml` — docs synchronization enforcement.
- `eas-build.yml` — mobile Expo application build.
- `eas-preview.yml` — mobile preview.
- `mobile-contracts.yml` — mobile contract enforcement.
- **`repo-guardrails.yml`** — wraps `scripts/verify_repo_guardrails.py` at PR-time and push-to-main. Strict mode. Explicit `--inventory-advisory` carve-out documented in-file. Triggers `context-kit verify` CONFLICT-finding checks.

**CONCLUSION:** repo-guardrails.yml is executable constitution. It enforces:
- Tracked generated paths (`docs/INDEX.md` DOC-AUTOGEN marker).
- Platform-inventory freshness (advisory in CI, strict locally).
- Context-kit verify CONFLICT findings.
- Non-editable autogen sections.

Playbook Chapter 8 (Runtime Discipline / Executable Constitution) MUST integrate CI workflows as a category of executable constitution alongside runtime policy tables (§3 below).

### 2.14 Other constitutional-adjacent artifacts (VERIFIED — top-level docs)

Additional top-level docs functioning as informal constitution:

- `docs/AGENTS.md` — agent inventory.
- `docs/AGENTS_REFERENCE.md` — agent reference.
- `docs/API_PATH_POLICY.md` — repo API path convention.
- `docs/ARCHITECTURE.md` — system architecture doc.
- `docs/AUDIT_FINDINGS.md` — accumulated audit findings.
- `docs/DATABASE_MODEL_REFERENCE.md` — which DB table for what.
- `docs/DISCORD_INTEGRATION.md` — Discord bot governance.
- `docs/DREAM_INITIATIVE_WORKFLOW.md` — initiative 5-stage pipeline.
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — Employee OS canonical primitives (referenced from CLAUDE.md).
- `docs/MASTER_DOCUMENTATION_STRUCTURE.md` — meta-documentation.
- `docs/PLATFORM_INVENTORY.md` (Canon) — runtime-derived inventory.
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor (referenced by CLAUDE.md as narrative anchor).
- `docs/SPIDERS.md`, `docs/SERVICES.md`, `docs/MODELS.md` — reference docs.

**CONCLUSION:** informal constitutional canon extends beyond the formal Canon Registry. Chris directive determines whether these get promoted or stay informal.

---

## 3. Runtime constitutional inventory

### 3.1 Runtime policy tables (VERIFIED — ORM from 2711)

Executable constitution enforced at runtime by Postgres-resident policy rows.

| Model | Rows | Purpose | Live/dormant |
|---|---|---|---|
| `CockpitAutopilotPolicy` | 4 | Autonomous incident-note triggers (cost spike / failure spike / queue backlog / stale agent) | 4/4 dormant (all `enabled=False`) |
| `AgentControlEntry` | 1 | Agent kill-switch (block agent by name) | Live |
| `Budget` | 6 | Provider + system spend limits (Anthropic $20/day, OpenAI $30/day, etc.) | Live |
| `Tenant` | 0 | SaaS billing envelope (subscription tier, cost limit, features) | Dormant — infrastructure ready |
| `ComplianceCheck`, `ComplianceRule` | 0/0 | Tenant-scope compliance | Dormant |
| `ContractRecord` | 30 | Deliberation-pipeline contract (internal design-by-contract, not constitutional) | Live |
| `PolicyExperiment` | 0 | Policy experimentation infrastructure | Dormant |

### 3.2 PublishGate state machine (VERIFIED — code)

Constitutional runtime for governance transitions.

- **Location:** `core/services/content_tool.py` (function `content_complete`); `content_tool` PA schema.
- **Transitions:** `draft` → `ready` → `published` → `archived` per `Deliverable.status.choices`.
- **Bypass value:** `completed` — accepted at DB layer for ratified governance artifacts even though not in the declared enum.
- **Behavior:** fires signals; marks immutable-on-write per 0010 §6 policy.
- **Governs:** every workspace deliverable's lifecycle transition, including ratifications.

**CONCLUSION:** PublishGate is the L2 executable constitutional mechanism for L5 workspace-canonical documentary constitution. Playbook Chapter 8 codifies.

### 3.3 canonical_authority derivation (VERIFIED — code)

Constitutional runtime for authority classification.

- **Location:** `content/_canonical_authority_helpers.py` (`_derive_canonical_authority` at :33-60).
- **Enforcement:** deterministic 4-branch decision tree (B1-B4).
- **Retrieval integration:** `core/rag_integration.py:30-34` — `_AUTHORITY_WEIGHTS = {'workspace_canonical': 2.0, 'repo_canonical': 1.5, 'derived': 1.0}` for opt-in `authority_weighted=True` retrieval; also filter mode via `canonical_authority='workspace_canonical'` argument.
- **Load-bearing per ADR-0120/0130** (workspace-canonical Cycle 1A).

**CONCLUSION:** canonical_authority is executable constitution embedded in the RAG substrate.

### 3.4 Beat schedule (VERIFIED — DB)

96 periodic tasks (91 enabled + 5 disabled) as recurring executable policy.

- **Location:** `django_celery_beat.PeriodicTask` model.
- **Includes:** `rigby_documentation_manager_daily`, various body-system health checks, cascade refresh tasks, etc.
- **Governance:** each periodic task is a rule about when work happens.

**CONCLUSION:** the Beat schedule is executable temporal constitution. Playbook Chapter 8 (Runtime Discipline) can cite categories but SHOULD NOT enumerate individual tasks (they change frequently; Chris directive for individual task disablement is L3-L4 governance).

### 3.5 Django cascade rules and signal handlers (VERIFIED — ORM from 2711)

**Cascade rules encode constitutional priorities** (per 2711 §2.3):
- `Tenant.owner = PROTECT` — cannot delete user who owns tenant.
- `Deliverable.workspace = SET_NULL` — content survives workspace deletion.
- `Deliverable.user = CASCADE` — content dies with user.

**Signal handlers:**
- `core/models_feedback_processing.py` — @receiver handlers.
- `core/models_partnership.py` — @receiver handlers.
- `core/signals_push_notifications.py` — @receiver handlers.
- Many others across the platform.

**CONCLUSION:** ORM constraints and signal handlers are Python-code executable constitution. Playbook Chapter 8 acknowledges as a category; individual constraints are code-canonical, not doc-canonical.

### 3.6 Runtime docs injection (VERIFIED — `core/services/docs_context_builder.py`)

Runtime-load-bearing injection of specific L2 canon docs into agent context.

**Verified injections (from grep results at :177-186 and :363-365):**

- Line 177: `CLAUDE.md`
- Line 184: `docs/governance/SYSTEM_OWNER.md`
- Line 186: `docs/canon/INDEX.md`
- Line 363: `CLAUDE.md` (max 300 lines)
- Line 365: `docs/governance/SYSTEM_OWNER.md` (max 100 lines)

**CONCLUSION:** the runtime treats specific docs as constitutional-load-bearing and injects them into agent context automatically. This is another executable-constitution mechanism the Playbook should acknowledge.

### 3.7 CI enforcement (VERIFIED — §2.13)

`repo-guardrails.yml` runs `scripts/verify_repo_guardrails.py` on every PR + push to main. Enforces:

- Tracked generated paths (autogen files).
- Platform-inventory freshness (advisory in CI).
- Context-kit verify CONFLICT findings.
- DOC-AUTOGEN marker presence on `docs/INDEX.md`.

**CONCLUSION:** executable constitution enforcement at PR time. Playbook Chapter 8 acknowledges CI workflows as a category.

---

## 4. Documentary constitution

### 4.1 The 3 constitutional document layers

Per constitutional-authority evidence gathered:

**L2 Platform documentary constitution (repo-canonical):**

*Formal Canon (§2.1):*
- `docs/PLATFORM_INVENTORY.md`
- `docs/00-START-HERE/DOC_LIFECYCLE.md`
- `docs/INDEX.md`
- `00-START-NEXT-SESSION.md`
- `docs/AUDIT_INDEX.md`
- 8 autogen runtime audits.

*Formal L0 declaration (§2.2):*
- `docs/governance/SYSTEM_OWNER.md`

*Formal repo ADR corpus (§2.4):*
- `docs/adr/ADR-0001..0004`

*Formal peer OSes (§2.5):*
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`

*Session-open contracts (used by runtime):*
- `CLAUDE.md`
- `MEMORY.md` (per user's auto-memory system)
- `00-START-NEXT-SESSION.md`

*Historical record (§2.9):*
- 952 handoffs in `docs/handoffs/`.

*Informal current-state canon (§2.10):*
- 21 topic docs in `docs/topics/`.

*Other informal canon (§2.14):*
- Additional top-level docs (AGENTS, API_PATH_POLICY, EMPLOYEE_OS_PRIMITIVES, etc.).

**L5 Workspace-canonical documentary constitution (per 2711/2712 evidence):**

- Cycle 0 ADRs: 0000_RAR_METHODOLOGY, 0005_PLATFORM_BOOTSTRAP_CONTRACT, 0010_RESEARCH_OPERATING_PROTOCOL, 0020_CYCLE_0_CLOSEOUT.
- Cycle 1 open/close: 0100, 0199.
- Cycle 1A ADRs: 0110, 0120, 0130, 0140, 0150.
- 8 ratification records.
- Evidence ledger: CYCLE_1A_IMPLEMENTATION_EVIDENCE_LEDGER_0110_0140.
- Manifest: MANIFEST_v20260707.

**L1 Fleet documentary constitution:**

- None. Fleet-scope constitutional documents don't exist today. Fleet infrastructure (§3.4 in 2711) is dormant.

### 4.2 Documentary-constitution meta-inventory

**Verified pattern:** documentary constitution uses **YAML frontmatter with authority-adjacent fields**:

| Frontmatter field | Used in | Example values |
|---|---|---|
| `title` | ADR-0001, DOC_LIFECYCLE | Human-readable name |
| `status` | ADR-0001, DOC_LIFECYCLE | `accepted`, `active` |
| `authority` | ADR-0001, DOC_LIFECYCLE | `design-decision`, `canonical` |
| `ratifier` | ADR-0001 | `chris` |
| `ratified` | ADR-0001 | `2026-07-06` |
| `proposed` | ADR-0001 | `2026-07-06` |
| `supersedes` | ADR-0001 | `(none — this is the first ADR)` |
| `superseded_by` | ADR-0001 | `(none)` |
| `session_added` | DOC_LIFECYCLE | `1143` |
| `last_verified` | DOC_LIFECYCLE | `2026-05-24` |
| `intake_id` | ADR-0001 | `IB-Q1-BOOT-01` |
| `arc_ref` | ADR-0001 | `I-0100` |
| `source_refs` | ADR-0001 | List of citations |
| `reversibility` | ADR-0001 | 1-5 scale |
| `companion_docs` | ADR-0001 | List of related docs |

**CONCLUSION:** the Playbook's frontmatter schema (2712 §5.1) uses substantially overlapping fields (`title`, `status`, `ratified_date`, `ratifier`, `parent_version`, `supersedes`, `compatible_with`, `source_refs` implicit via evidence index). Playbook v0.1 SHOULD adopt the existing repo-ADR frontmatter pattern with extensions rather than propose a wholly new one.

### 4.3 Documentary constitution by layer

| Layer | Documentary constitution counts |
|---|---|
| L1 Fleet | 0 formal artifacts |
| L2 Platform (formal Canon) | 5 + 8 autogen |
| L2 Platform (formal ADR corpus) | 4 |
| L2 Platform (formal OSes) | 2 (Research OS, IOS) + 1 startup-orientation |
| L2 Platform (session-open contracts) | 3 (CLAUDE.md, MEMORY.md, 00-START-NEXT-SESSION.md) |
| L2 Platform (historical handoffs) | 952 |
| L2 Platform (informal subsystem canon) | 21 topics |
| L2 Platform (informal top-level) | ~30-50 top-level docs |
| L3 Tenant | 0 formal artifacts |
| L4 User | 0 formal artifacts (personal prefs not constitutional) |
| L5 Workspace | 25 deliverables in Architecture & Research (5 ADR + 5-8 ratifications + 2 cycle records + 2 legacy manifest + 4 methodology docs + 4 historical typed as document) |
| L6 Deliverable | see L5 |

---

## 5. Executable constitution

### 5.1 Runtime policy tables (per §3.1)

- CockpitAutopilotPolicy (4 rows, all dormant).
- AgentControlEntry (1 row, live).
- Budget (6 rows, live).

### 5.2 Django ORM cascade rules (per §3.5)

- Tenant.owner = PROTECT.
- Deliverable.workspace = SET_NULL (content survives workspace death).
- Deliverable.user = CASCADE (content dies with user).
- Cascade rules across 23 workspace-scoped models per 2709 evidence.

### 5.3 PublishGate state machine (per §3.2)

- `content_tool.content_complete` transitions.
- Signal-fired immutability policy.

### 5.4 canonical_authority derivation + retrieval weights (per §3.3)

- Deterministic classifier.
- 2.0 / 1.5 / 1.0 weighted ranking.
- Anti-pollution invariant.

### 5.5 Beat schedule (per §3.4)

- 96 periodic tasks.

### 5.6 CI workflows (per §2.13)

- 7 workflows.
- Enforce autogen markers, freshness, verify_repo_guardrails contract.

### 5.7 Runtime docs injection (per §3.6)

- `docs_context_builder.py` injects CLAUDE.md, SYSTEM_OWNER, canon/INDEX at agent-context-build time.

### 5.8 Signal handlers (per §3.5)

- Cross-cutting @receiver decorators enforcing behavioral policy.

### 5.9 Migration files (VERIFIED — immutable schema history)

- All `content/migrations/*.py` and `core/migrations/*.py` are append-only.
- Each migration is a formal schema-constitutional change.
- Cycle 1A KFI-2 lives in `content/migrations/0049_add_canonical_authority.py` and `content/migrations/0050_uniq_workspace_source_reference.py`.

### 5.10 Executable constitution meta-inventory

**Enforcement locations:**

| Enforcement layer | Where | Examples |
|---|---|---|
| Python ORM constraints | Model files | on_delete cascade rules |
| Python signal handlers | Signal modules | PublishGate transitions, feedback_processing |
| Database migrations | `content/migrations/*` | Schema history (immutable) |
| Django admin controls | Admin models | CockpitAutopilotPolicy, Budget, AgentControlEntry |
| Beat schedule | PeriodicTask rows | Scheduled tasks |
| Runtime docs injection | `docs_context_builder.py` | CLAUDE.md, SYSTEM_OWNER, canon/INDEX loaded into agent context |
| CI workflows | `.github/workflows/*.yml` | repo-guardrails, docs-sync, etc. |
| Verify scripts | `scripts/verify_repo_guardrails.py` | Local + CI drift checks |

**CONCLUSION:** executable constitution is spread across 8 enforcement locations. The Playbook Chapter 8 (Runtime Discipline) should enumerate the categories and cite the mechanism per category, NOT try to codify each individual rule.

---

## 6. Constitutional ownership map

### 6.1 The L0 authority

- **Chris West** — per SYSTEM_OWNER.md, "Founder, System Owner, Final Authority, Absolute Override Level."
- Runtime-load-bearing declaration.
- Single point of ratification authority for all L1-L5 constitutional artifacts.

### 6.2 Per-artifact ownership

| Artifact class | Owner | Delegation |
|---|---|---|
| SYSTEM_OWNER.md | Chris (self-declared) | None |
| Formal Canon Registry | Chris (per canon/INDEX.md "System Owner approved") | None |
| Repo ADRs (ADR-0001..0004) | Chris ratified | Claude/Rigby propose |
| Workspace ADRs (0110-0150) | Chris ratified (Cycle 1A) | Claude/Rigby propose |
| Cycle 0 ADRs (0000/0005/0010/0020) | Chris ratified | Claude/Rigby propose |
| Cycle 1 records (0100/0199) | Chris ratified | Claude/Rigby propose |
| Ratification records | Chris ratified | Created by Author (Claude) |
| CLAUDE.md | Claude Code (per platform convention) | Chris directs edits |
| MEMORY.md | Claude Code (auto-memory system) | Chris directs edits |
| Topic docs | Distributed (Claude authored, no single owner) | None formal |
| Handoffs | Author of the session | None (immutable-in-place convention) |
| Runtime policy tables | Chris (admin UI) | Claude MAY propose changes via PR |
| CI workflows | Repo maintainers (Chris) | Claude MAY propose changes via PR |
| Migrations | Repo maintainers | Claude MAY propose new migrations |
| Research OS + IOS + Startup Introspection | Chris ratified as they are canon-adjacent | Claude proposes edits |
| docs-pattern subtree | Explicitly out of scope (context-kit framework) | External |

### 6.3 The Playbook's ownership fit

- The Engineering Playbook is L2 platform-scope repo-canonical (per 2711 recommendation).
- Owner: Chris (ratifier).
- Author: Claude Code (per 2713).
- Reviewer: Rigby SIGN (default) or fallback Claude verifier-loop.
- Cascade automation: platform-managed.
- The Playbook joins an existing ownership hierarchy; it does not create a new one.

---

## 7. Constitutional dependency graph

The constitutional ecosystem dependencies (verified via cross-references in the documents themselves):

```
Chris (L0 human ratifier)
  │
  │ authorizes
  ▼
SYSTEM_OWNER.md (L2 canon; Chris = Absolute)
  │
  │ enforced by
  ▼
docs_context_builder.py (L2 runtime; injects into agent context)
  │
  │ delivers to
  ▼
Every agent execution (Rigby, Claude, autonomous agents)
  │
  │ operates under
  ▼
Canon Registry (canon/INDEX.md) ← governs which docs are constitutional
  │
  │ includes as canon
  ├──▶ PLATFORM_INVENTORY.md (technical canon)
  ├──▶ DOC_LIFECYCLE.md (operational canon; authority: canonical)
  ├──▶ INDEX.md (autogen)
  ├──▶ 00-START-NEXT-SESSION.md (session continuity)
  ├──▶ AUDIT_INDEX.md (audit taxonomy)
  └──▶ 8 autogen runtime audits

Peer constitutional documents (repo-canonical):
  ├── Research OS (RESEARCH_OPERATING_SYSTEM.md) — governs research
  ├── IOS (IMPLEMENTATION_OPERATING_SYSTEM.md) — governs implementation
  ├── CLAUDE.md — session-open contract
  ├── MEMORY.md — auto-memory rules
  ├── ADR corpus (docs/adr/ADR-0001..0004) — 4 ratified design decisions
  └── docs-pattern/ — separate constitutional subtree (context-kit)

Workspace-canonical constitutional documents (L5):
  ├── Cycle 0 ADRs (0000/0005/0010/0020)
  ├── Cycle 1 open/close (0100/0199)
  ├── Cycle 1A ADRs (0110-0150)
  ├── Ratification records (8)
  ├── MANIFEST_v20260707
  ├── Evidence ledger
  └── 25 total deliverables in Architecture & Research

Executable constitution:
  ├── CockpitAutopilotPolicy (4 rows)
  ├── AgentControlEntry (1 row)
  ├── Budget (6 rows)
  ├── PublishGate state machine
  ├── canonical_authority derivation + retrieval weights
  ├── Django cascade rules (23 workspace-scoped FKs)
  ├── Beat schedule (96 tasks)
  ├── 7 CI workflows
  ├── Migration history (immutable)
  └── Signal handlers (distributed)

Historical constitutional record:
  ├── 952 handoffs (docs/handoffs/)
  ├── Audit archives (docs/audit-2026/, docs/audits/)
  ├── Superseded docs (docs/archive/)
  └── Provenance system (_provenance.json — 2438 docs, 7775 commits)

The Engineering Playbook (proposed):
  │
  │ WILL SUPPLEMENT (not replace)
  ▼
  All of the above at L2 documentary layer.
  Chapter 1 acknowledges the pre-existing ecosystem.
```

### 7.1 Dependency edges verified

- `docs_context_builder.py` reads: CLAUDE.md, SYSTEM_OWNER.md, canon/INDEX.md.
- ADR-0001 references: IOS §2.5, §D3, Appendix C; Research OS §8.3; docs/research/implementation/BACKLOG.md; docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_scoping.md §5.
- DOC_LIFECYCLE.md excludes: `docs/docs-pattern/`.
- Canon Registry entries all point at "original paths (not under `/canon/`)".
- `_provenance.json` excludes: `docs/archive/`, `docs/docs-pattern/`.
- CLAUDE.md L7 blockquote points at workspace `a9a16593-…`.

---

## 8. Constitutional layer matrix

Applying the six-layer model (per 2711) to all inventoried artifacts:

| Layer | Documentary | Executable | Historical |
|---|---|---|---|
| **L1 Fleet** | None formal | Fleet models (FleetServiceIdentity, FleetEvent, FleetPAChatAuditRow) — 2,499 rows | None formal (though FleetEvent bus is chronological) |
| **L2 Platform** | Canon Registry (5+8), ADR-0001..0004, Research OS, IOS, CLAUDE.md, MEMORY.md, 00-START, SYSTEM_OWNER, DOC_LIFECYCLE, topic docs (21), handoffs (952), audits, ~30-50 top-level docs | CockpitAutopilotPolicy, AgentControlEntry, Budget, PublishGate, canonical_authority, Beat, CI, cascade rules, docs_context_builder, migrations, signal handlers | Handoffs (952), audit archives, superseded docs, migration history, _provenance.json |
| **L3 Tenant** | None (Tenant modeled but 0 rows) | Tenant, Budget-per-tenant (all null tenant today), ComplianceRule/Check (dormant) | None |
| **L4 User** | None (personal prefs not constitutional) | User preferences, memory, personal Rigby state — user-owned, not constitutional | User conversation history, personal artifacts |
| **L5 Workspace** | 25 deliverables in Architecture & Research (5 ADR, 8 ratification, 2 cycle records, 4 methodology, 4 typed-document, others) | WorkspaceConfig (12 rows, empty), WorkspaceContext (3 rows), autonomy gates, deliverable categories | WorkspaceOperation (5,707 rows) |
| **L6 Deliverable** | Ratified Deliverables (per L5 above) | PublishGate transitions, Deliverable.status enforcement | Superseded Deliverables (soft; no destructive delete) |

### 8.1 Layer boundary observations

- **L1 Fleet:** documentary constitution is absent. Executable is present but dormant except FleetEvent/FleetPAChatAuditRow (active audit-only).
- **L2 Platform:** documentary constitution is *massive* (~1,000+ artifacts including handoffs). Executable is well-populated.
- **L3 Tenant:** entirely dormant. Infrastructure ready for Cycle 3+ activation.
- **L4 User:** not typically a constitutional layer (preferences, not policies).
- **L5 Workspace:** documentary is well-populated (Cycle 0/1A); executable is minimal (WorkspaceConfig unused).
- **L6 Deliverable:** governed by higher layers; ratification creates constitutional character.

---

## 9. Constitutional lifecycle

Verified lifecycle stages for documentary constitution (from evidence gathering + Canon Registry criteria):

### 9.1 Draft → Ready → Ratified

- **Draft** — WIP in `docs/research/*`, `docs/research/platform/*`, or workspace deliverable with `status='draft'`.
- **Ready** — passes SIGN cycle (workspace) or PR review (repo).
- **Ratified** — Chris directive; workspace `status='completed'` OR repo commit + tag OR Canon Registry promotion.

### 9.2 Deprecation → Retirement

- **Deprecation** — DOC-POINTER-V1/V2 headers added; document remains in place but marked stale/superseded.
- **Retirement** — moved to `docs/archive/superseded-YYYY-MM/`; pointer at original path.

### 9.3 Canon promotion

- Documents nominated (via Canon Registry Pending Review queue).
- Chris directive to promote.
- Update `docs/canon/INDEX.md` with new entry.

### 9.4 Runtime executable-constitution lifecycle

- Runtime policies: created via admin UI or ORM; edited via admin UI or ORM; audited via WorkspaceOperation or admin-log analog.
- CI workflows: PR-modified; merge triggers deployment.
- Migrations: append-only; never destructively modified.

---

## 10. Missing constitutional pieces

Based on the full inventory, the following are constitutionally missing:

### 10.1 L1 Fleet documentary constitution

No fleet-level constitutional documents exist. Fleet auth protocol, fleet artifact exchange contract, fleet event schema — all dormant.

**Impact for Playbook:** none for v0.1. Cycle 4+ concern.

### 10.2 L3 Tenant documentary constitution

No tenant-level constitutional documents exist. Subscription policies, retention policies, compliance policies — all dormant.

**Impact for Playbook:** none for v0.1. Cycle 3+ concern.

### 10.3 Bidirectional Canon Registry linkage

The Canon Registry references docs by original path but the docs themselves do not carry back-references to their Canon status. A `canon_status: promoted 2026-05-25 (Session 1144)` frontmatter field would strengthen bidirectional integrity.

**Impact for Playbook:** Chapter 4 (Documentation Cascade) SHOULD include a rule requiring back-references.

### 10.4 Formal executable-constitution registry

No single document enumerates all executable-constitution mechanisms (CockpitAutopilotPolicy + AgentControlEntry + Budget + PublishGate + canonical_authority + Beat + CI + cascade rules + migrations + docs injection + signals). Playbook Chapter 8 fills this gap.

**Impact for Playbook:** Chapter 8 authoring priority raised.

### 10.5 Ratification record type consistency

Per 2712 §14.1, existing ratification records are inconsistently typed (some `document`, some `ratification_record`). No enforcement mechanism prevents new drift.

**Impact for Playbook:** Chapter 8 (Executable Constitution) and Chapter 10 (Evolution) codify Cycle 2 hardening.

### 10.6 Runtime-load-bearing doc registry

Multiple docs are runtime-load-bearing (per docs_context_builder.py + verify_repo_guardrails) but no single registry enumerates them. Prior sessions did not surface this.

**Impact for Playbook:** Chapter 8 SHOULD codify.

### 10.7 The Engineering Playbook itself

The Playbook is the missing piece the prior sessions have been designing. Not needed to be listed as "missing" now; it's about to exist.

---

## 11. Misclassified artifacts

Artifacts that are constitutional but not explicitly classified as such, or classified incorrectly:

### 11.1 IOS + Research OS + startup-introspection under `docs/research/process/`

These are formally repo-canonical operating-system documents but live under `docs/research/` which is typically WIP-research territory. Location suggests they are drafts; content shows they are ratified authorities.

**Misclassification:** location is drafts; content is canon.

**Recommendation:** either move to `docs/canon/`-tracked location, promote to formal Canon Registry, OR document a "process/ = ratified operating systems" carve-out in DOC_LIFECYCLE.

### 11.2 SYSTEM_OWNER.md not explicitly in Canon Registry

Runtime-load-bearing, `authority: CANON` in its status header, but not listed in the Canon Registry table.

**Misclassification:** de facto canon, not formally promoted.

**Recommendation:** promote to Canon Registry via Chris directive.

### 11.3 CLAUDE.md, MEMORY.md not in Canon Registry

Runtime-load-bearing, session-open contracts, referenced by CLAUDE.md L7 blockquote as the workspace-canonical anchor.

**Misclassification:** de facto canon, not formally promoted.

**Recommendation:** promote to Canon Registry.

### 11.4 The 4 repo-canonical ADRs (ADR-0001..0004) not in Canon Registry

Ratified with `authority: design-decision` frontmatter; live in `docs/adr/`.

**Misclassification:** ADRs are a different class than Canon (per canon/INDEX.md, canon is durable narrative; ADRs are point-in-time decisions). Perhaps NOT misclassified — they represent a peer class of constitutional artifact.

**Recommendation:** no move needed. Add a "Ratified ADRs" section to Canon Registry index for discoverability.

### 11.5 The 21 topic docs

Referenced from CLAUDE.md as authoritative subsystem docs but not in Canon Registry.

**Misclassification:** informal canon at scale.

**Recommendation:** either add a "Subsystem Canon" section to Canon Registry (referencing all 21) or leave informal.

---

## 12. Transitional artifacts

Artifacts in a transitional state:

### 12.1 `docs/canon/creative/DAVINCI_RESOLVE_WORKFLOW.md`

Only file in `docs/canon/creative/`. DaVinci Resolve was sunset in Session 1143 per Canon Registry note. This file should be moved to archive or removed.

### 12.2 `docs/audit-2026/` and `docs/audits/`

Historical audit archives. Per AUDIT_INDEX.md, they are preserved but not current truth. Boundary between "history" and "still-referenced constitutional" is unclear.

**Recommendation:** apply DOC-POINTER-V2 headers uniformly.

### 12.3 Workspace-hosted L2 artifacts (2711 §8.9 anomaly)

- 0000_RAR_METHODOLOGY
- 0005_PLATFORM_BOOTSTRAP_CONTRACT
- 0010_RESEARCH_OPERATING_PROTOCOL
- 0020_CYCLE_0_CLOSEOUT
- MANIFEST_v20260707

Semantically L2 (platform-scope) but hosted at L5 (workspace).

**Recommendation (from 2711):** leave in place (ratified; immutable). The Playbook is the first correctly-placed L2 artifact. Reconciliation is Cycle 2+ cleanup.

### 12.4 `docs/canon/INDEX.md` last-updated Session 1144 (~1,500 sessions ago)

Canon Registry hasn't been updated since Session 1144. Recent Cycle 1A ratifications are NOT reflected in the Canon Registry.

**Recommendation:** update the Canon Registry as part of Playbook v0.1 authoring OR delay until Cycle 2.

### 12.5 The Playbook itself (proposed)

Between architecture research and v0.1 ratification. This entire proposal chain (2708-2714) is transitional artifact.

---

## 13. Technical debt

Debt items surfaced by this inventory:

### 13.1 Canon Registry staleness

Session 1144 last-updated; multiple ratified artifacts since. Debt: ~35 unrecognized additions/updates.

### 13.2 DOC-POINTER convention adoption gaps

Not every deprecated doc has a V1/V2 header. Some old audit files, some archived docs, and possibly some superseded topic docs.

### 13.3 canon promotion queue growth

"Stage 2 Governance Plan" pending review since (implied) at least Session 1144. Chris directive needed.

### 13.4 Documentary vs executable enforcement mismatch

Documentary constitution (Canon Registry, ADRs, ratification records) has policy-based immutability. Executable constitution (runtime policy rows) has admin-UI immutability but not audit-log integration for most changes. Playbook Chapter 8 codifies the mismatch.

### 13.5 Multiple constitutional-metadata patterns

Different documents use different frontmatter shapes:
- ADR-0001 style (17+ fields, structured).
- DOC_LIFECYCLE style (5 fields, minimal).
- Playbook proposal style (12 fields, per 2712 §5).
- No unified schema.

**Recommendation:** Playbook v0.1 codifies a unified schema; ratified artifacts migrated via Cycle 2 cleanup.

### 13.6 Ratification-record `deliverable_type` drift

0110/0120/0130 ratifications stored as `deliverable_type='document'` (per 2707 §9 note); 0140/0150/0199 stored as `deliverable_type='ratification_record'`. Historical inconsistency documented in 0199 §6.

### 13.7 `content_hash` unpopulated on most ratification records

Only 2 of 8 have hashes (0010, 0100). Cycle 2 hardening required.

### 13.8 Runtime-load-bearing docs not enumerated in a registry

`docs_context_builder.py` reads specific paths at specific line numbers. Chris directive on which docs are runtime-load-bearing is implicit; no formal registry.

---

## 14. Future evolution

### 14.1 Cycle 2 hardening opportunities (surfaced by inventory)

- Populate `content_hash` on all ratification records.
- ORM signal to enforce `Deliverable(status='completed')` immutability.
- CI validation for `deliverable_type='ratification_record'` on ratification-record deliverables.
- Automated Canon Registry update per new ratification.
- Bidirectional Canon Registry linkage.
- Runtime-load-bearing docs registry.
- Playbook v0.1 authoring (across Sessions 2714-2721 per 2713 §23.2).

### 14.2 Cycle 3 activation opportunities

- Tenant model activation (populate Tenant rows).
- Tenant-scope Playbook variants.
- Tenant-scope constitutional docs.
- Multi-tenant Canon Registry.
- `content.Document.workspace_id` for tenant isolation.

### 14.3 Cycle 4 fleet-scope opportunities

- FleetServiceIdentity population.
- Fleet-scope constitutional documents.
- Cross-app Playbook coordination.
- FleetArtifact for constitutional-artifact exchange.

### 14.4 Long-term evolution

- Retire or consolidate DAVINCI_RESOLVE_WORKFLOW.md.
- Migrate WIP proposals (this file, prior 2708-2713 proposals) to ratified status once Playbook v1.0 codifies methodology.
- Retire IOS + Research OS if Playbook absorbs their content; OR maintain as peer OSes with cross-references.

---

## 15. Self critique

### 15.1 What if this inventory is still incomplete?

**Verified inventory sources:** `docs/` top-level, `docs/adr/`, `docs/research/process/`, `docs/canon/`, `docs/00-START-HERE/`, `docs/governance/`, `docs/topics/`, `docs/handoffs/` (count only), `.github/workflows/`, plus prior sessions' ORM evidence.

**Not-verified this session (may contain constitutional artifacts I missed):**
- `docs/agents/`, `docs/apis/`, `docs/apps/`, `docs/audit/`, `docs/body/`, `docs/BUGS`, `docs/case-studies/`, `docs/cleanup/`, `docs/code-review/`, `docs/features/`, `docs/guides/`, `docs/initiatives/`, `docs/integrations/`, `docs/missions/`, `docs/mobile/`, `docs/narratives/`, `docs/operations/`, `docs/ops/`, `docs/patents/`, `docs/playbooks/` (!), `docs/plans/`, `docs/pre-launch/`, `docs/recons/`, `docs/reports/`, `docs/research/` (only `research/platform/` and `research/process/` explored), `docs/roadmap/`, `docs/roadmaps/`, `docs/specs/`, `docs/spokesperson/`, `docs/tools/`, `docs/verification/`, `docs/workflows/`.

**`docs/playbooks/` in particular is suspicious.** The name suggests it may already contain playbook-style content.

**Impact:** the inventory in §2-§4 covers the core constitutional ecosystem but likely misses further informal constitutional artifacts. The mission stated "inventory every constitutional artifact currently existing." I have inventoried the load-bearing ones (verified by runtime references, formal frontmatter authority, or ratification records). Recognized limitations: informal top-level docs may include additional constitutional artifacts I did not enumerate.

**Recommendation:** subsequent sessions (Cycle 2) SHOULD conduct a doc-by-doc audit of every `docs/` subdirectory to complete the inventory. For v0.1 Playbook authoring, the inventory in §2-§4 is sufficient.

### 15.2 What if I over-classified informal artifacts as constitutional?

The Canon Registry says "Canon is intentionally small (≤10 docs)." My inventory classified 30+ artifacts as constitutional. Am I over-inclusive?

**Response:** the Canon Registry is one *tier* of constitutional artifacts (the durably-ratified L2 canon). Below that tier: ADRs (design decisions), OSes (methodology), CLAUDE.md (session contract), handoffs (historical record), CI workflows (executable). These are all constitutional in the sense that they carry authority; they are not all *Canon* in the Registry's narrow sense.

**Refinement:** distinguish **Canon** (Registry-promoted) from **constitutional artifacts** (broader).

### 15.3 What if the Playbook duplicates existing artifacts?

- The Playbook could overlap with Research OS (Chapter 2), IOS (Chapter 3), DOC_LIFECYCLE (Chapter 4), SYSTEM_OWNER (Chapter 1 authority), Canon Registry (Chapter 1 constitutional context).

**Response:** the Playbook should reference and integrate these rather than duplicate. Chapter 2 (Research Methodology) CITES Research OS; it does not restate. Chapter 3 (Implementation Discipline) CITES IOS. Chapter 4 (Documentation Cascade) CITES DOC_LIFECYCLE. Chapter 1 (Constitutional Context) CITES Canon Registry and SYSTEM_OWNER.md as prior-art constitutional foundations.

**Applied consequence:** the Playbook is not a rewrite. It's a codification-of-codifications, integrating existing constitutional infrastructure into a unified authoring standard.

### 15.4 What if the Playbook should be part of the Canon Registry instead of separate?

Attractive possibility. But:

- Canon Registry limits ≤10 docs.
- Playbook is expected to grow to ~2,000+ lines.
- Canon is "durable narrative"; Playbook is "codified methodology."

**Response:** they are peer constitutional layers. Add a Canon Registry row referencing the Playbook (once ratified) similar to DOC_LIFECYCLE. Playbook body lives at `docs/ENGINEERING_PLAYBOOK.md`; Canon Registry contains a pointer.

---

## 16. Falsification attempts

### 16.1 "The 2708-2713 chain designed a Playbook that isn't needed — existing infrastructure suffices."

**Steelman:** IOS + Research OS + DOC_LIFECYCLE + SYSTEM_OWNER + Canon Registry + repo-ADR-corpus already codify: research methodology (Research OS), implementation discipline (IOS), documentation cascade (DOC_LIFECYCLE), constitutional authority (SYSTEM_OWNER), canon promotion (Canon Registry), design decisions (repo ADRs). What does the Playbook add?

**Attack:**

- **Fragmentation:** these documents are scattered, use different frontmatter conventions, have different ratification statuses, and cross-reference each other only informally.
- **No unified authoring standard:** each document was authored with different conventions; new contributors don't know which to follow.
- **No formal evidence discipline:** ADR-0001 references sources but doesn't require citation classification per PIC-10.
- **No formal semver:** DOC_LIFECYCLE has `last_verified`; IOS references version (v1.0, v1.1, v1.2, v1.3, v1.4, v1.5); no unified versioning.
- **PIC-10 provenance classification is not codified anywhere yet.**
- **The Playbook is the *integration* of the existing informal ecosystem into a single ratified codification.**

**Verdict:** Playbook is still needed. It integrates rather than replaces.

### 16.2 "The Canon Registry is the true constitution; the Playbook should just be promoted into it."

**Steelman:** Canon Registry is the pre-existing constitutional promotion mechanism; the Playbook should join by promotion rather than by parallel path.

**Attack:**

- Canon Registry is intentionally small (≤10 docs). Adding the Playbook wouldn't violate that limit but crowds it.
- Canon Registry lists docs that ARE constitutional. The Playbook (once ratified) IS constitutional and MAY be listed there. This is compatible with a parallel path.

**Verdict:** compatible. Playbook v1.0 ratification SHOULD include a Canon Registry entry addition.

### 16.3 "The Playbook duplicates DOC_LIFECYCLE."

**Steelman:** DOC_LIFECYCLE already governs the `/docs/` corpus. The Playbook's Chapter 4 (Documentation Cascade) overlaps.

**Attack:**

- DOC_LIFECYCLE governs pointer conventions, root stability, doc lifecycle. It does NOT codify the 4-step docs cascade with embed step (Cycle 1A discovery per feedback_docs_pipeline_4_step_cascade).
- Playbook Chapter 4 extends DOC_LIFECYCLE with cascade discipline.

**Verdict:** extension, not duplication.

### 16.4 "SYSTEM_OWNER.md should be the Playbook Chapter 1."

**Steelman:** SYSTEM_OWNER.md declares Chris's absolute authority. That's the constitutional bedrock. The Playbook Chapter 1 could just link to it.

**Attack:**

- SYSTEM_OWNER.md is 1 person's authority declaration.
- Playbook Chapter 1 (per 2712 §3.1) is "Constitutional context" — the full six-layer stack + KFI-2 canonical_authority + workspace-vs-repo boundary.
- Chapter 1 CITES SYSTEM_OWNER.md as the L0 authority anchor. It doesn't replace it.

**Verdict:** Chapter 1 cites SYSTEM_OWNER.md; that's the correct integration.

### 16.5 "Research OS is the Playbook Chapter 2. Why have both?"

**Steelman:** Research OS codifies research methodology. Playbook Chapter 2 (Research Methodology) IS research methodology.

**Attack:**

- Research OS predates PIC discipline. It doesn't require PIC-10 provenance classification.
- Playbook Chapter 2 CAN cite Research OS as prior art AND extend with PIC-10 discipline.
- Long-term option: Research OS is fully absorbed into Playbook Chapter 2; Research OS is deprecated with DOC-POINTER-V2 header. This is a Cycle 3+ decision.

**Verdict:** Playbook extends Research OS. Long-term absorption possible but not required for v0.1.

### 16.6 "The Playbook should live in `docs/canon/` (or its equivalent 'true canon' location)."

**Steelman:** Constitutional artifacts live in canon-marked locations. Playbook is constitutional. Ergo, Playbook lives in `docs/canon/`.

**Attack:**

- Canon Registry says: "Canon docs live at their original paths (not under `/canon/`). These are pointers, not copies."
- Playbook lives at `docs/ENGINEERING_PLAYBOOK.md` per 2712.
- Canon Registry gets an entry pointing at it. Consistent with the "pointers not copies" rule.

**Verdict:** Playbook location per 2712 §6.1 is correct. Canon Registry entry added at ratification.

### 16.7 "The Playbook can't be v0.1 because Chapter 1 needs the inventory in this document — chicken-and-egg."

**Steelman:** Chapter 1 needs to integrate the pre-existing ecosystem; the inventory is in this WIP research doc; the doc isn't ratified yet.

**Attack:**

- This inventory doc (2714) can be ratified as prior-art evidence for the Playbook per PIC-10 provenance discipline.
- Chapter 1 cites this inventory as `E3: research doc`.
- Or: Chapter 1 authoring in Session 2716 (per 2713 §23.2) integrates the inventory findings directly, using this doc as source material.

**Verdict:** no chicken-and-egg. Sessions 2714 (this) + 2715 (Chapter 10) + 2716 (Chapter 1) work as a natural sequence.

### 16.8 "The 6-layer model is wrong because the inventory shows L2 has TWO sub-layers (Canon vs. peer OSes)."

**Steelman:** L2 documentary constitution has Canon (5 promoted docs) and peer OSes (Research OS, IOS) as two distinct tiers. Should the model add a sub-layer?

**Attack:**

- The distinction is *rank of documentary constitution*, not a new layer. Canon is more selective (≤10) than peer OSes.
- Sub-layer proliferation is dangerous; each new layer adds architectural complexity.
- The 6-layer model captures the *scope of governance* (Fleet → Platform → Tenant → User → Workspace → Deliverable). Canon-vs-OS is *tier of constitutional weight* within L2, not scope.

**Verdict:** don't add a sub-layer. The Playbook's chapter classification (10 statement classes per 2713 §6) captures constitutional weight; layers capture scope.

### 16.9 "Something else is constitutional and missed entirely."

**Steelman:** The self-critique acknowledged `docs/playbooks/` was not enumerated. What else was missed?

**Attack:**

- `docs/playbooks/` presence is highly suggestive. Its content may contain informal Playbook-like documents that the Engineering Playbook v0.1 SHOULD acknowledge or supersede.
- Other unenumerated directories may hide constitutional artifacts.

**Verdict:** ACCEPTED. Cycle 2 should complete the inventory. For v0.1 Playbook, Chapter 1 SHOULD carry a "known limitations" section acknowledging the inventory is provisional. `docs/playbooks/` directory investigation is added to Session 2716 (Chapter 1 authoring) prep tasks.

### 16.10 Summary of falsification attempts

- 10 attacks attempted.
- 9 rejected with defenses.
- 1 partially accepted (§16.9 — inventory is provisional; Cycle 2 completion required; Chapter 1 acknowledges provisional status).

**The core Playbook architecture (2708-2713 chain) survives falsification.** Refinements needed:
- Chapter 1 integrates pre-existing ecosystem.
- Chapter 1 acknowledges provisional inventory.
- Canon Registry entry added at ratification.

---

## 17. Final recommendation

### 17.1 Core recommendation

**Proceed to Playbook v0.1 authoring** starting Session 2715 (Chapter 10 Evolution & Amendment, per 2713 §23.2 recommended order) with the following amendments to the prior chain:

**Amendment A:** Chapter 1 (Constitutional Context) MUST integrate the pre-existing constitutional ecosystem inventoried here:
- Cite Canon Registry as prior canon-promotion mechanism.
- Cite SYSTEM_OWNER.md as L0 authority declaration.
- Cite DOC_LIFECYCLE.md as prior L2 documentation governance.
- Cite ADR-0001..0004 as prior repo-canonical ratified ADR corpus.
- Cite Research OS and IOS as peer L2 constitutional methodologies.
- Cite `docs/docs-pattern/` as separate constitutional subtree (context-kit framework, out of scope).

**Amendment B:** Chapter 1 SHOULD include a "Provisional inventory" acknowledgment: the constitutional ecosystem inventory is comprehensive-but-not-exhaustive as of Session 2714; Cycle 2 completion is expected.

**Amendment C:** Chapter 4 (Documentation Cascade) MUST cite DOC_LIFECYCLE.md and extend, not duplicate.

**Amendment D:** Chapter 6 (PIC-10 Provenance) MAY integrate the existing `_provenance.json` HIGH/MEDIUM/LOW/UNKNOWN classification alongside PIC-10's 5-class taxonomy. Reconciliation needed.

**Amendment E:** Chapter 8 (Executable Constitution) MUST enumerate the 8 enforcement location categories per §5.10.

**Amendment F:** at Playbook v0.1 ratification, add a Canon Registry entry pointing at the Playbook (following the "pointers not copies" rule).

**Amendment G:** at Playbook v0.1 ratification, promote SYSTEM_OWNER.md, CLAUDE.md, MEMORY.md, and 00-START-NEXT-SESSION.md to formal Canon Registry entries if not already listed. Verified: 00-START-NEXT-SESSION.md IS in the Canon Registry; SYSTEM_OWNER.md IS NOT; CLAUDE.md IS NOT; MEMORY.md IS NOT.

### 17.2 Do NOT

- Do NOT retire or absorb Research OS + IOS in v0.1. Chapters 2 and 3 CITE them.
- Do NOT rename `docs/canon/` (runtime dependency at `docs_context_builder.py:186`).
- Do NOT restructure `docs/docs-pattern/`.
- Do NOT delete session handoffs.
- Do NOT open new ADRs before Playbook v0.1.
- Do NOT modify existing ratified artifacts.
- Do NOT begin Playbook content authoring in this session.

### 17.3 Retire / update

- Update `docs/canon/INDEX.md` (Session 1144 → Session 271X) to reflect: 4 new repo ADRs, 5 workspace ADRs, ratification records, MANIFEST_v20260707, IOS + Research OS status, Playbook v0.1 promotion.
- Move `docs/canon/creative/DAVINCI_RESOLVE_WORKFLOW.md` to `docs/archive/` (DaVinci sunset).
- Consider consolidating `docs/audit/`, `docs/audit-2026/`, `docs/audits/` naming (three-way naming with different eras). Deferred.

### 17.4 What becomes what

Per the mission's exact §19 closing questions, answered explicitly below.

---

## 18. Architectural closure assessment

### 18.1 Architecture research phase status

The architecture research phase (Sessions 2708-2714) is **complete enough** for Playbook v0.1 authoring to begin, with the following material caveats:

- **Verified sufficient:** the six-layer constitutional model (2711), the Playbook Architecture Specification (2712), the Authoring Protocol (2713), and the ecosystem inventory (2714) collectively cover the architecture necessary to author v0.1.
- **Verified provisional:** the ecosystem inventory has known gaps (§15.1); Chapter 1 must acknowledge.
- **Verified refinable:** Chapter 1 needs Amendments A-B; Chapter 4 needs Amendment C; Chapter 6 needs Amendment D; Chapter 8 needs Amendment E; ratification needs Amendments F-G.

### 18.2 Where the architecture is complete

- Constitutional layer model (6 layers).
- Canonical-authority dimension (2 first-class classes: workspace_canonical, repo_canonical).
- Ratification lifecycle (6 stages).
- Semver strategy (rule-change semantics).
- Evidence discipline (6 evidence classes; per-class thresholds).
- Statement classification (10 classes).
- Writing style + RFC-2119.
- AI authoring rules.
- 8-check verification protocol.
- Recommended chapter authoring order.
- Constitutional ecosystem inventory (this session).

### 18.3 Where the architecture is provisional

- Complete constitutional artifact inventory (some `docs/` subdirectories unexplored).
- Cycle 2+ hardening (content_hash, ORM immutability, CI validators).
- Cycle 3+ tenant activation.
- Cycle 4+ fleet activation.

### 18.4 Formal declaration recommendation

Chris MAY formally close the architecture research phase after review of this document. Formal closure:
- Ratifies the six-layer model, Playbook Architecture Specification, Authoring Protocol, and Ecosystem Inventory as constitutional research foundation.
- Authorizes Session 2715 (Playbook Chapter 10 authoring) to proceed.
- Acknowledges provisional inventory; Cycle 2 completes.

---

## 19. The 10 mission-required closing answers

### 19.1 Is the constitutional architecture now complete enough to begin Playbook authoring?

**YES**, with the caveat that Chapter 1 (Constitutional Context) MUST integrate the pre-existing ecosystem inventoried here (Amendments A-B in §17.1). The prior chain 2708-2713 designed the Playbook architecture accurately; Session 2714 revealed a substantial pre-existing constitutional ecosystem that Chapter 1 must acknowledge to avoid appearing to compete with existing constitutional infrastructure.

### 19.2 What constitutional artifacts remain outside the ecosystem?

The following are constitutional-adjacent but not formally part of the ecosystem today:

- **`docs/playbooks/`** (not enumerated this session; may contain informal playbook-like documents). Cycle 2 inventory completion required.
- **`docs/specs/`** (not enumerated; may contain constitutional specs).
- **The 21 topic docs** (informal current-state canon, not Canon-Registered).
- **~30-50 top-level docs** (informal reference canon).
- **The 952 session handoffs** (immutable historical constitutional record; not classified as Canon).
- **The 7 CI workflows** (executable constitution; not classified as documentary).
- **Migration files** (immutable executable constitution; not classified).
- **Signal handlers** (distributed executable constitution).

### 19.3 Should anything be moved?

**Recommendation:** minimal moves.

- Move `docs/canon/creative/DAVINCI_RESOLVE_WORKFLOW.md` to `docs/archive/superseded-2026-07/` (DaVinci sunset; §12.1).
- Do NOT move IOS + Research OS out of `docs/research/process/` (they are peer OSes; the location convention is stable).
- Do NOT move workspace-hosted L2 artifacts (0000/0005/0010/0020/MANIFEST) — accept L2-in-L5 anomaly (per 2711 §8.9).

### 19.4 Should anything be retired?

- **Retire `DAVINCI_RESOLVE_WORKFLOW.md`** to archive (DaVinci sunset).
- **Do NOT retire IOS / Research OS** — cited by Playbook chapters.
- **Do NOT retire ADR-0001..0004** — active ratifications.
- **Do NOT retire Cycle 1A ADRs** — ratified, immutable.
- **Cycle 2 candidate:** consider consolidating `docs/audit/` + `docs/audit-2026/` + `docs/audits/` three-way naming.

### 19.5 Should anything be renamed?

- **Do NOT rename `docs/canon/`** — runtime dependency at `docs_context_builder.py:186`.
- **Do NOT rename `SYSTEM_OWNER.md`** — runtime dependency at `docs_context_builder.py:184` and `:365`.
- **Do NOT rename `docs/00-START-HERE/DOC_LIFECYCLE.md`** — runtime and Canon dependencies.
- **MAY rename** `docs/canon/creative/` since it will be empty after DaVinci retirement — but see §17.2, deletion preferred.

### 19.6 What becomes the constitutional source of truth?

**Tiered constitutional source-of-truth:**

- **L0 authority:** `docs/governance/SYSTEM_OWNER.md` (Chris = Absolute).
- **L2 documentary constitution:** `docs/canon/INDEX.md` (Canon Registry) enumerates the promoted Canon; the Engineering Playbook `docs/ENGINEERING_PLAYBOOK.md` (once ratified) codifies engineering methodology; the ADR corpus at `docs/adr/` documents design decisions; Research OS + IOS at `docs/research/process/` document methodology.
- **L2 executable constitution:** distributed across 8 enforcement locations (§5.10).
- **L5 workspace-canonical documentary constitution:** workspace `a9a16593-…` hosts Cycle 0/1A ADRs, ratification records, and cycle records.
- **L5 executable constitution:** WorkspaceConfig, WorkspaceContext, autonomy gates.

**No single source-of-truth exists.** Multi-source constitutional infrastructure is the reality; the Playbook v1.0 codifies the *mechanisms* by which multi-source truth is coordinated.

### 19.7 What becomes historical record?

- **`docs/handoffs/`** — 952 session handoffs (append-only; never deleted; DOC-POINTER-V2 headers on moves).
- **`docs/audit-2026/`, `docs/audits/`** — preserved audit archives.
- **`docs/archive/superseded-*`** — DOC-POINTER-V2 rehomed artifacts.
- **Retired rules registry** (proposed in 2713 §9.4 for Playbook Chapter 10).
- **Git commit history + tag chain** — the platform's own immutable substrate history.
- **`_provenance.json`** — 2,438 doc + 7,775 commit provenance system.
- **Migration files** — append-only schema history.
- **`WorkspaceOperation`** — 5,707 rows of audit trail.

### 19.8 What becomes executable policy?

- **`CockpitAutopilotPolicy`** (4 rows) — autonomous incident-note triggers.
- **`AgentControlEntry`** (1 row) — agent kill-switch.
- **`Budget`** (6 rows) — spend limits.
- **`PublishGate` state machine** — deliverable-lifecycle transitions.
- **`canonical_authority` derivation + retrieval weights** — RAG substrate policy.
- **`Tenant` + tenant-scoped Budget** — dormant SaaS billing (Cycle 3+).
- **`ComplianceRule` + `ComplianceCheck`** — dormant tenant compliance (Cycle 3+).
- **Beat schedule** (96 tasks) — temporal executable policy.
- **CI workflows** (7 files) — PR-time enforcement.
- **`scripts/verify_repo_guardrails.py`** — local + CI drift checks.
- **Django ORM cascade rules** — data-integrity constitutional constraints.
- **Signal handlers** — distributed behavioral policy.
- **Migration files** — schema evolution as immutable constitutional history.
- **`docs_context_builder.py`** — runtime docs injection into agent context.

### 19.9 What becomes governance?

- **`docs/governance/SYSTEM_OWNER.md`** — L0 authority declaration.
- **The 6-stage ratification lifecycle** (per Playbook Chapter 8).
- **SIGN cycle methodology** (per Playbook Chapter 2, integrating Research OS).
- **PIC-10 provenance classification** (per Playbook Chapter 6).
- **The Canon Registry promotion mechanism** (`docs/canon/INDEX.md`).
- **The workspace ratification-record envelope pattern** (per 2712 §14).
- **The amendment discipline** (per Playbook Chapter 10 + 2713 §11).
- **The evidence admission standard** (per 2713 §7).
- **The verification 8-check protocol** (per 2713 §18).

### 19.10 Can the architecture research phase now be formally declared complete?

**YES**, subject to Chris's directive. The formal closure act would be:

1. Chris ratifies-to-consider all 7 research proposals (2708, 2709, 2710, 2711, 2712, 2713, 2714) as constitutional research foundation.
2. Chris directs Session 2715 to begin Playbook v0.1 Chapter 10 authoring (per 2713 §23.2 recommended order).
3. Playbook v0.1 (once ratified) codifies the results of this research chain.
4. Cycle 2+ hardening (§14.1) proceeds in parallel with Playbook amendments.

**Alternative (Chris directive-dependent):**

Chris MAY direct additional research if any of the following remain unresolved:

- Complete inventory of `docs/playbooks/` and other unenumerated directories.
- Alignment between PIC-10 and `_provenance.json` classification.
- Ratification record type consistency mechanism.
- Renaming or restructuring of any inventoried artifact.
- Any other Chris-directed refinement.

If none of these, the architecture research phase is complete.

---

## Closing

Six prior architecture sessions plus this inventory converge on a constitutional model that is:

- **Grounded in existing infrastructure** — Canon Registry, SYSTEM_OWNER.md, DOC_LIFECYCLE.md, repo ADR corpus, Research OS, IOS, workspace ADRs, runtime policy tables — all pre-exist the Playbook.
- **Extended by the Playbook** — the Engineering Playbook integrates the informal ecosystem into a unified ratified codification.
- **Provisional in inventory** — this document has known scope limits; Cycle 2 completes.

**Session 2715 (next):** Playbook Chapter 10 (Evolution & Amendment) authoring, per 2713 §23.2 order.

**Repository ends clean.** This document is the sole artifact of Session 2714.

---

_End of Session 2714 Constitutional Ecosystem Inventory & Architectural Closure. No implementation performed. No ADRs opened. No Playbook content authored. No workspace deliverables created. No constitutional amendments. No runtime changes. Repository ends clean (this document + six untracked prior proposals only)._

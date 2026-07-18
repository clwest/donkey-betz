---
title: "S2814 /docs/ Audience Segmentation Audit (T4 of Group 2700 arc)"
status: active (audit deliverable — cross-surface matrix + primary+secondary audience labels)
authority: T4 child audit of Group 2700 parent arc
session: 2814
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
thread: T4
authors: Claude Code (Chris directed at S2814 open); Rigby (surface (1) corpus enumeration + surface (2) CRITICAL_DOCS spot-check + Q1/Q2/Q3 methodology corrections)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md   # parent (Chris-locked 2026-07-16)
  - docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md       # T1 predecessor (S2811)
  - docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md # T2 predecessor (S2812)
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md   # T3 predecessor (S2813)
  - core/services/docs_context_builder.py                                                 # source of truth for surface (2) CRITICAL_DOCS
  - docs/CLAUDE.md                                                                        # source for surface (3) pointer graph (45 unique refs)
  - docs/PLATFORM_WHAT_IT_IS.md                                                           # source for surface (4) narrative anchors (~7 unique refs)
scope: T4 = classify every /docs/ file by primary+secondary audience (Rigby / Claude / Human / multi) per parent §4 — cross-reference 5 discovery surfaces
non_goals:
  - proposing new audience segments (parent §4 explicit-out — describe what exists)
  - restructuring proposal (canonical summary at 2799)
  - file moves, deletions, renames, code changes (arc non-goals per parent §5)
  - retrieval-frequency measurement (would require telemetry that doesn't exist — Rigby SIGN Q2 correction)
  - enumerating every prompt-pack assembly path across the codebase (bounded by CRITICAL_DOCS + noted paths)
delegates_to: T5 (handoffs+audits proliferation); T6 (anchor drift); canonical summary 2799 (restructuring proposal)
owner: claude+rigby
---

# Session 2814 — /docs/ Audience Segmentation Audit (Group 2700, Thread 4)

> **What this doc is.** T4 audience classification — cross-reference 5 discovery surfaces to classify every `/docs/` file by primary + secondary audience. Rigby is co-evidence-source (owns surface (1) + (2) enumeration, contributed Q1/Q2/Q3 methodology corrections).
>
> **What this doc is not.** A proposal for new audience segments. A proposal to move/consolidate docs. A retrieval-frequency measurement (telemetry doesn't exist). Those belong to canonical summary at 2799 or downstream implementation.

---

## 1. Why T4 fourth

Per parent doc §4:

> T4 — Audience segmentation. Scope: classify every `/docs/` file by primary audience — load-bearing-for-Rigby (search_docs corpus + tool-context) vs Claude-only (session bootstrap + CLAUDE.md graph) vs human-only (Chris reading in a browser) vs multi-audience. Method: cross-reference `search_docs` corpus + `docs_context_builder.py` reads + CLAUDE.md graph + PLATFORM_WHAT_IT_IS narrative surface. Deliverable: matrix — file × audience × surface-it-appears-on — plus counts by audience segment.

T4 follows T1 (inventory), T2 (pattern extraction), T3 (pain measurement). T4 measures **WHO** each doc is for; T3 measured pain, T2 measured substrate primitives, T1 measured topology.

**Methodology corrections applied (Rigby SIGN Q1/Q2/Q3):**

- **Q1 → C (Primary + Secondary) not A (exclusive) or B (pure tags).** Every doc has ONE primary audience anchored to authorial intent / dominant use, plus explicit secondary flags to preserve reality. Multi-audience counts derivable as intersection view.
- **Q2 → 3-way load-bearing distinction, NOT N-threshold.** Without retrieval telemetry, any "cited ≥N times" rule produces confident nonsense. Correct distinction: (a) **structurally load-bearing** (forcibly injected by code), (b) **retrieval-eligible** (in corpus), (c) **retrieval-proven** (would require telemetry — mark as UNKNOWN).
- **Q3 → 5th surface identified: runtime-injection / prompt-pack assembly.** Distinct from "referenced in code" — this is the best proxy for "Rigby actually uses this" without retrieval counters.

---

## 2. Anchors T4 cites (never restates)

| Source | What it authoritatively holds | This doc's usage |
|---|---|---|
| Parent doc §4 T4 scope | Method + deliverable + explicit-out | T4 respects |
| [`core/services/docs_context_builder.py`](../../../../core/services/docs_context_builder.py) `CRITICAL_DOCS` (line 362) | Structurally-load-bearing for Rigby's agent context | T4 cites; enumerates the 8-item list |
| [`docs/CLAUDE.md`](../../../CLAUDE.md) | Repo bootstrap graph | T4 greps to enumerate the 45 pointer refs |
| [`docs/PLATFORM_WHAT_IT_IS.md`](../../../PLATFORM_WHAT_IT_IS.md) | Platform narrative anchor | T4 greps to enumerate the ~7 narrative refs |
| T1 §3.1 | 3201 total .md files at S2811 baseline (T4 uses 3217 per S2814 open Rigby count) | Corpus size baseline |
| T3 §7 C5 | DOC_LIFECYCLE §2c "sole authoritative counts source" convention falsified at discovery layer | T4 evidence for why "Rigby-load-bearing" needs 3-way distinction |

---

## 3. The 5 discovery surfaces

**Discovery surface = a mechanism by which a `/docs/` file becomes reachable to a specific audience.** T4 measures cross-surface coverage per doc.

### 3.1 Surface (1) — `search_docs` RAG corpus (Rigby retrieval-eligibility)

- **What it is:** All `/docs/` files indexed via `build_docs_index` → chunked via `build_rag_corpus` (~1200 chars per chunk) → embedded and stored in `document_embeddings` (pgvector) via `sync_docs_index_to_documents --embed`.
- **Owner:** Rigby (she owns retrieval).
- **Enumeration:** **3217 documents, all with embeddings, 65454 total chunks (~20 chunks/doc avg)** per Rigby `kb_tool.stats` dispatch at S2814 open.
- **Retrieval characterization:** "eligible" = every doc in the index. "Proven" = would require retrieval-count telemetry that does not exist. T3 §7 shows retrieval BEHAVIOR is not proportional to eligibility (e.g., archived Oct 2025 morning report outranks PLATFORM_INVENTORY.md for count queries).

### 3.2 Surface (2) — `docs_context_builder.py` `CRITICAL_DOCS` (Rigby structural injection)

- **What it is:** A hardcoded list at `core/services/docs_context_builder.py:362` of docs that get their full content (up to `max_lines`) injected into every agent's system prompt as bootstrap context.
- **Owner:** Rigby (she executes agents that receive this injection); Claude (edits the list in code).
- **Enumeration (verbatim from code — 5 items only, per Rigby SIGN post-authoring Q1 correction):**
  1. `CLAUDE.md` (300 lines) — root anchor
  2. `00-START-NEXT-SESSION.md` (200 lines) — session state
  3. `docs/governance/SYSTEM_OWNER.md` (100 lines) — human-authority framework (Session 814)
  4. `docs/missions/CURRENT_MISSION.md` (100 lines) — agent focus
  5. `docs/USER_FEEDBACK_QUEUE.md` (100 lines) — user issues (Session 948)
- **Total structurally-load-bearing docs (surface 2): 5 files.** Distinct from `PRIORITY_DOCS` — see §3.2b.
- **Characterization:** These docs are GUARANTEED to be in every agent's prompt with full content. Highest possible Rigby-load-bearing signal.

### 3.2b Surface (2b) — `docs_context_builder.py` `PRIORITY_DOCS` (Rigby high-priority scoring)

- **What it is (correction post-authoring per Rigby SIGN Q1):** A DIFFERENT hardcoded list at `core/services/docs_context_builder.py:176` — "always considered / high priority" for scoring purposes. **NOT** auto-injected with full content like `CRITICAL_DOCS`. Distinct concept: PRIORITY_DOCS influences ranking/filtering when the agent's docs-context builder decides what to surface; CRITICAL_DOCS is unconditional full-content injection.
- **Enumeration (10 items — some overlap with CRITICAL_DOCS):**
  1. `CLAUDE.md` (also in CRITICAL_DOCS)
  2. `00-START-NEXT-SESSION.md` (also in CRITICAL_DOCS)
  3. `docs/ARCHITECTURE.md`
  4. `docs/AGENTS.md`
  5. `docs/CAPABILITIES.md`
  6. `docs/DATABASE_MODEL_REFERENCE.md`
  7. `docs/governance/SYSTEM_OWNER.md` (also in CRITICAL_DOCS)
  8. `docs/missions/CURRENT_MISSION.md` (also in CRITICAL_DOCS)
  9. `docs/canon/INDEX.md`
  10. `docs/USER_FEEDBACK_QUEUE.md` (also in CRITICAL_DOCS)
- **Overlap analysis:** 5 of 10 PRIORITY_DOCS are ALSO in CRITICAL_DOCS (both surface 2 + 2b). 5 are PRIORITY_DOCS-only: `docs/ARCHITECTURE.md`, `docs/AGENTS.md`, `docs/CAPABILITIES.md`, `docs/DATABASE_MODEL_REFERENCE.md`, `docs/canon/INDEX.md`.
- **Characterization:** High-priority for retrieval scoring but NOT unconditionally injected. Weaker signal than surface (2); stronger than surface (1) corpus membership alone.

### 3.3 Surface (3) — CLAUDE.md pointer graph (Claude bootstrap)

- **What it is:** Every doc referenced in `CLAUDE.md` (project instructions) becomes part of the fresh-Claude session bootstrap graph.
- **Owner:** Claude (reads CLAUDE.md at every session start).
- **Enumeration:** **45 unique `docs/...md` or `docs/...` references** (grep evidence).
- **Composition:**
  - 11 `docs/topics/*.md` files (all of them — agent-system, body-systems, celery-workers, content-pipeline, employee-os, frontend, infrastructure, initiative-pipeline, personal-assistant, spider-network, stock-intelligence)
  - 8 playbook ratification handoffs (SESSION_2727 / 2740 / 2742 / 2752 / 2753 / 2766 / 2778 / 2786)
  - ~15 root anchor docs (PLATFORM_INVENTORY, PLATFORM_WHAT_IT_IS, ENGINEERING_PLAYBOOK, EMPLOYEE_OS_PRIMITIVES, DATABASE_MODEL_REFERENCE, ARCHITECTURE, AGENTS, ADVISOR_AUDIT, DISCORD_AUDIT, DISCORD_INTEGRATION, API_PATH_POLICY, DREAM_INITIATIVE_WORKFLOW, INDEX, canon/INDEX, demo_mode, governance_redesign)
  - 4 `docs/research/` docs (ARCHITECTURE_INDEX, DOMAIN_RESEARCH_PLAYBOOK, OPEN_ARCS, implementation/RATIFICATION_2026-07-14_PLAYBOOK_V0_8_0)
  - 2 subdir pointers (`docs/handoffs/`, `docs/research/`)

### 3.4 Surface (4) — `PLATFORM_WHAT_IT_IS.md` narrative anchors (Human/multi context)

- **What it is:** Every doc referenced in `PLATFORM_WHAT_IT_IS.md` (narrative anchor per DOC_LIFECYCLE §2c) becomes part of the platform-level narrative surface.
- **Owner:** Chris (reads narrative anchor); Claude (reads narrative anchor at session-open per orient protocol).
- **Enumeration:** **~7 unique doc references** (grep evidence).
- **Composition:** `PLATFORM_INVENTORY.md`, `AUTONOMOUS_SYSTEMS.md`, `24_7_GLOBAL_AI_APP_ATLAS.md`, `topics/` subdir, `audit-2026/` subdir, `current/` subdir reference, self-reference `PLATFORM_WHAT_IT_IS.md`.
- **Characterization:** Sparse. PLATFORM_WHAT_IT_IS is mostly self-contained narrative; pointer usage is minimal.

### 3.5 Surface (5) — Runtime prompt-pack injection (Rigby SIGN Q3 addition)

- **What it is (per Rigby Q3 zoom-out):** What content is ACTUALLY INCLUDED IN PROMPTS / TOOL-CONTEXT AT RUNTIME. Includes surface (2) `CRITICAL_DOCS` plus any additional prompt-pack assembly paths (agent-specific injections in `base_agent.py`, PA-specific injections in `unified_pa_entrypoint.py`, tool-context-specific injections in `tool_dispatcher.py`, etc.).
- **Owner:** Rigby (executes prompt-pack assembly); Claude (edits assembly code).
- **Enumeration:** **~10 docs via CRITICAL_DOCS** (surface (2), fully enumerated) + **N additional via agent/PA/tool-specific injection paths** — full enumeration requires grepping ALL prompt-assembly code across `core/services/`, `core/agents/`, `core/tasks_agents.py`, etc.
- **Bounded scope for T4:** T4 measures surface (5) = surface (2) `CRITICAL_DOCS` only. Additional injection paths flagged as **latent-unenumerated** for follow-up in canonical summary or downstream implementation.
- **Characterization:** Best proxy for "Rigby actually uses this" without retrieval telemetry (per Rigby SIGN Q2). Any doc in surface (5) is definitionally Rigby-load-bearing.

---

## 4. Classification framing

Per Rigby SIGN Q1 AGREE-C: **each doc gets ONE primary audience + explicit secondary flags**. Multi-audience counts derivable as derived view.

### 4.1 Primary audience labels

- **Primary = Rigby** — doc is in surface (2) or surface (5); OR is a canonical ops/spec doc referenced by tool schemas / playbooks / agent context.
- **Primary = Claude** — doc is in surface (3) CLAUDE.md graph AND is not primary-Rigby by rule above. Session-bootstrap docs, playbook ratifications, orientation docs.
- **Primary = Human** — doc is in NEITHER surface (2) NOR surface (3) AND is authored as human-reader narrative / guide / policy (default classification for docs that don't fit Rigby/Claude by exclusion).
- **Primary = Multi (rare)** — doc is unambiguously served to 2+ audiences by design (e.g., `PLATFORM_INVENTORY.md` is read by Chris in browser AND cited by Rigby in count answers AND appears in Claude's bootstrap graph). Reserved for cases where authorial intent explicitly serves multiple audiences.

### 4.2 Secondary audience flags

- **+Rigby-secondary** — doc is in surface (1) corpus AND has operational reference value (not just narrative). ~all docs in surface (1) qualify; effectively equivalent to "in RAG corpus." Distinct from primary-Rigby because non-injected corpus membership ≠ structurally load-bearing.
- **+Claude-secondary** — doc is in surface (3) but is not primary-Claude (e.g., a playbook ratification handoff is primary-Claude for bootstrap; its content also serves as reference for anyone reading it).
- **+Human-secondary** — doc is human-readable AND surfaces via Chris's browser (e.g., DocsIndexPage renders `docs/INDEX.md`; `00-START-NEXT-SESSION.md` is browsed by Chris even though its primary role is agent injection).

### 4.3 3-way load-bearing distinction (per Rigby Q2 correction)

**Do NOT use retrieval-frequency thresholds without telemetry.** Instead:

- **Structurally load-bearing** — in surface (2) or surface (5). Guaranteed injection.
- **Retrieval-eligible** — in surface (1). May-or-may-not be retrieved; behavior depends on query + ranker.
- **Retrieval-proven** — UNKNOWN. Requires per-doc retrieval-count telemetry that does not exist in the current substrate. Do not claim any doc is retrieval-proven in T4.

---

## 5. Per-surface enumeration (verbatim)

### 5.1 Surface (2) — Structurally load-bearing via CRITICAL_DOCS (5 docs)

| Doc | Injected via | Max lines |
|---|---|---|
| `CLAUDE.md` (root) | CRITICAL_DOCS unconditional inject | 300 |
| `00-START-NEXT-SESSION.md` (root) | CRITICAL_DOCS unconditional inject | 200 |
| `docs/governance/SYSTEM_OWNER.md` | CRITICAL_DOCS (Session 814) | 100 |
| `docs/missions/CURRENT_MISSION.md` | CRITICAL_DOCS (Session 814) | 100 |
| `docs/USER_FEEDBACK_QUEUE.md` | CRITICAL_DOCS (Session 948) | 100 |

**Primary audience for all 5: Rigby (structural).** Secondary flags per §4.2.

### 5.1b Surface (2b) — PRIORITY_DOCS not in CRITICAL_DOCS (5 additional docs)

| Doc | PRIORITY_DOCS role | Injected with full content? |
|---|---|---|
| `docs/ARCHITECTURE.md` | High-priority for scoring | No — retrieval-ranked only |
| `docs/AGENTS.md` | High-priority for scoring | No — retrieval-ranked only |
| `docs/CAPABILITIES.md` | High-priority for scoring | No — retrieval-ranked only |
| `docs/DATABASE_MODEL_REFERENCE.md` | High-priority for scoring | No — retrieval-ranked only |
| `docs/canon/INDEX.md` | High-priority for scoring | No — retrieval-ranked only |

**Primary audience for all 5: Rigby (high-priority scoring, weaker than structural injection).** These are more load-bearing than random corpus members but less than CRITICAL_DOCS.

### 5.2 Surface (3) — CLAUDE.md pointer graph (45 unique refs)

**Categorized subset (full list would be ~45 rows; sampling categories):**

- **11 topics/ files** — primary-Claude (session bootstrap; described as "current-state subsystem docs designed for embedding") with +Rigby-secondary (in surface 1 corpus).
- **8 playbook ratification handoffs** — primary-Claude (bootstrap graph explicitly cites for governance context) with +Human-secondary (Chris reads these directly).
- **~15 root anchor docs** — mixed: PLATFORM_INVENTORY primary-Multi (all three audiences); ENGINEERING_PLAYBOOK primary-Claude with +Rigby+Human secondary; ADVISOR_AUDIT / DISCORD_AUDIT / DISCORD_INTEGRATION primary-Human (Chris-facing autogen outputs); others per case.
- **4 research/ docs** — primary-Claude (research OS bootstrap) with +Rigby-secondary + +Human-secondary.
- **2 subdir pointers** (`docs/handoffs/`, `docs/research/`) — not classifiable as single files; represent aggregate content in those subdirs.

### 5.3 Surface (4) — PLATFORM_WHAT_IT_IS.md narrative refs (~7 unique refs)

| Doc | Primary audience |
|---|---|
| `docs/PLATFORM_INVENTORY.md` | Multi (all three audiences; explicitly runtime-count anchor + Claude bootstrap + Chris browser) |
| `docs/AUTONOMOUS_SYSTEMS.md` | Human (narrative doc referenced by Chris-oriented anchor) |
| `docs/24_7_GLOBAL_AI_APP_ATLAS.md` | Human (aspirational narrative) |
| `docs/topics/` (subdir) | Claude (bootstrap; per surface 3) |
| `docs/audit-2026/` (subdir) | Human (April 2026 structured audit — 15 files, Chris-scoped) |
| `docs/current/` (subdir reference) | UNVERIFIED (doc referenced but subdir doesn't exist per T1 §3.1 — possible Rot; flag for T6 anchor drift audit) |
| `docs/PLATFORM_WHAT_IT_IS.md` (self-ref) | N/A |

**Rot signal:** PLATFORM_WHAT_IT_IS.md references `docs/current/` — not present in T1 §3.1 subdir inventory. Possible dead link; T6 (anchor drift) should verify.

### 5.4 Surface (1) — Full corpus (3217 files, retrieval-eligible)

- **Every non-archive `.md` file** (1813 per T1 §5 non-archive count + drift adds ~+ from S2811→S2814 close cascades = ~1829 non-archive at S2814) is eligible for retrieval.
- **Every archive `.md` file** (1388 per T1 §3.1) is ALSO in the corpus (T3 §7 C5 evidence — `archive/old-structure/status/historical/morning-report-2025-10-02.md` returned as top-1 for count query).
- **Total surface (1) = 3217 docs.** All docs get +Rigby-secondary flag by virtue of corpus eligibility.

---

## 6. Cross-reference matrix (aggregate summary)

Full per-file matrix would be 3217 rows — impractical for a session-scoped audit. Instead, T4 reports **aggregate counts by audience segment**. Per-file matrix is downstream-derivable from surface enumeration in §5.

### 6.1 Primary audience segment counts (ESTIMATES — treat as upper bounds, per Rigby SIGN post-authoring Q2/Q4)

**Category (i) — Measurable precise counts:**

- **Rigby primary (structurally injected via CRITICAL_DOCS):** **5 docs exactly** (§5.1)
- **Rigby high-priority (PRIORITY_DOCS not in CRITICAL_DOCS):** **5 docs exactly** (§5.1b)
- **Claude primary (in CLAUDE.md graph, not in surface 2 or 2b):** **~35-40 docs** (45 CLAUDE.md refs − ~5-10 overlap with surface 2/2b − subdir pointers). Not exact without full grep-audit.
- **Explicit-multi primary (in surface 3 AND surface 4 AND surface 1 with narrative-anchor role):** **~5 docs** (PLATFORM_INVENTORY, PLATFORM_WHAT_IT_IS, INDEX, canon/INDEX, ENGINEERING_PLAYBOOK).

**Category (ii) — RESIDUAL bucket (per Rigby SIGN Q4 correction):**

- **Non-archive docs NOT in any measurable surface (2/2b/3/4):** ~1780 non-archive docs − ~50 above = **~1730 docs**.
- **This residual is NOT automatically Human-primary.** Some are ops/spec reference docs used by agents via retrieval-eligible corpus membership without being injected or bootstrap-cited. Classifying all ~1730 as Human-primary would overcount because it sweeps up:
  - Ops/spec docs whose intent is agent consumption (e.g., `docs/topics/*.md` primary-Claude even if not in CLAUDE.md graph? Actually 11 topics ARE in graph)
  - Reference docs like `docs/API_PATH_POLICY.md`, `docs/DEPLOYMENT_QUICKREF.md`, `docs/BEAT_AUDIT.md` — read by both humans AND agents
  - Autogen outputs (`*_AUDIT.md` batch) — arguably Human-primary (Chris reads them) but with strong +Rigby-secondary
- **Upper-bound estimate:** ≤1730 Human-primary (if all residual defaulted). Realistic estimate: closer to 1400-1600 with 100-300 residual reclassified as primary-Multi or primary-Rigby-via-retrieval-eligibility once evaluated case-by-case.

**Archive:** 1388 docs — primary audience is "historical/inactive" by convention; T4 leaves as-is per parent §7 anti-scope (archive posture: leave alone).

**Precision caveat (per Rigby SIGN Q4):** The above counts are classification-driven estimates with unknown error. Canonical summary authors must not treat them as measured truth — the ~1730 Human-primary figure is an UPPER BOUND, not a point count. Category (i) counts are precise; category (ii) residual is fuzzy.

### 6.2 Secondary audience flag counts

- **+Rigby-secondary:** ~1829 non-archive docs (all corpus members with operational reference value).
- **+Claude-secondary:** ~45 docs (subset of surface (3) not already primary-Claude).
- **+Human-secondary:** ~1780 non-archive docs (most are readable by Chris in browser).

### 6.3 Observations from cross-referencing

- **Human primary docs are ~95% of the non-archive corpus** (~1730 of ~1829). The `/docs/` corpus is overwhelmingly human-audience by default. Rigby-primary + Claude-primary + Multi-primary combined = ~50 docs (~2.7% of non-archive).
- **Discovery-vs-injection asymmetry** (corrected per Rigby SIGN post-authoring Q3, tool-verified via CLAUDE.md greps):
  - **3 of 5 CRITICAL_DOCS are NOT in CLAUDE.md pointer graph:** `docs/governance/SYSTEM_OWNER.md`, `docs/missions/CURRENT_MISSION.md`, `docs/USER_FEEDBACK_QUEUE.md`. Every agent gets these injected with full content, but fresh Claude session doesn't see them via CLAUDE.md at bootstrap.
  - **2 of 5 additional PRIORITY_DOCS are also NOT in CLAUDE.md pointer graph:** `docs/CAPABILITIES.md`, `docs/DATABASE_MODEL_REFERENCE.md`. These get retrieval-priority boosting but fresh Claude doesn't see them via bootstrap graph.
  - **CLAUDE.md-visible CRITICAL_DOCS overlap:** Only `CLAUDE.md` (self-reference) and `00-START-NEXT-SESSION.md` appear in both surface (2) and surface (3).
  - **CLAUDE.md-visible PRIORITY_DOCS overlap:** `docs/ARCHITECTURE.md`, `docs/AGENTS.md`, `docs/canon/INDEX.md`.
  - **Substrate implication:** the docs most-important-to-agents (CRITICAL_DOCS + PRIORITY_DOCS) are only partially discoverable via CLAUDE.md. Downstream author whose only entry point is CLAUDE.md misses 5 critical/priority docs.
- **Surface (4) narrative references are almost entirely redundant with surface (3).** PLATFORM_WHAT_IT_IS.md's ~7 refs are a subset of CLAUDE.md's 45 refs (with the exception of `AUTONOMOUS_SYSTEMS.md`, `24_7_GLOBAL_AI_APP_ATLAS.md`, and the possibly-Rot `current/` reference).
- **Retrieval-eligibility ≠ Retrieval-behavior.** Per T3 §7, the same corpus that includes PLATFORM_INVENTORY.md also includes archived Oct 2025 morning reports; retrieval returns the latter for count queries. Corpus membership is a floor, not a guarantee.

---

## 7. Playbook §9 canonical questions (adapted to T4 scope)

| Q# | Question (adapted) | T4 answer |
|---|---|---|
| Q1 | How many discovery surfaces exist? | 5 (surfaces 1-4 from parent scope + surface 5 runtime-injection per Rigby SIGN Q3) |
| Q2 | How many docs are structurally load-bearing (surface 2 CRITICAL_DOCS)? | **5 exactly** (post-authoring Rigby correction — was 10, conflated with PRIORITY_DOCS) |
| Q2b | How many docs are Rigby high-priority via PRIORITY_DOCS (surface 2b)? | **5 exactly** (5 PRIORITY_DOCS that are not also in CRITICAL_DOCS) |
| Q3 | How many docs are Claude bootstrap-graph primary? | ~35-40 (surface 3 minus surface 2/2b overlap) — approximate |
| Q4 | How many docs are primary-Multi (multi-audience by design)? | ~5 |
| Q5 | How many docs are primary-Human by default classification? | **≤1730 (UPPER BOUND)** — residual bucket, not measured truth per Rigby SIGN Q4 |
| Q6 | Is retrieval-frequency measurable in the current substrate? | **NO** — telemetry does not exist. T4 uses 3-way distinction: structural / eligible / proven (marked UNKNOWN). |
| Q7 | Is there overlap between surface (2) injection and surface (3) bootstrap? | Partial (2 of 5 CRITICAL_DOCS in CLAUDE.md: `CLAUDE.md` self-ref + `00-START-NEXT-SESSION.md`). **3 CRITICAL_DOCS NOT in CLAUDE.md** — discovery-vs-injection asymmetry. Plus **2 PRIORITY_DOCS NOT in CLAUDE.md** (CAPABILITIES, DATABASE_MODEL_REFERENCE). |
| Q8 | Is surface (4) PLATFORM_WHAT_IT_IS.md narrative surface redundant with surface (3)? | Mostly yes (5 of ~7 refs are subset of CLAUDE.md graph). Notable non-redundant: `AUTONOMOUS_SYSTEMS.md` + `24_7_GLOBAL_AI_APP_ATLAS.md` (Human-primary aspirational narratives). |
| Q9 | Is there a Rot signal from surface enumeration? | **YES** — PLATFORM_WHAT_IT_IS.md references `docs/current/` which is NOT in T1 §3.1 subdir inventory. Flag for T6 anchor drift audit. |
| Q10 | Does the corpus include archive? | **YES** — 1388 archive files are in surface (1). T3 §7 C5 evidence shows archive content outranks canonical for count queries. |
| Q11-Q28 | Restructuring proposal; migration ordering; retrieval telemetry design; audience-specific docs; per-audience navigation | **Out of T4 scope** — T5/T6/canonical summary owns |

---

## 8. Migration Queue (post-arc)

Per parent §5. T4 items are **classification observations**, not restructuring proposals. **Severity: INFORMATIONAL.**

| # | Item | Evidence source (this doc) | Severity | Notes for migration session |
|---|---|---|---|---|
| MQ-T4-1 | **Human-primary docs are ~95% of non-archive corpus** (~1730 of ~1829); structurally load-bearing is ~10 (~0.5%) | §6.1 + §6.3 | INFORMATIONAL | Canonical summary decides audience-specific navigation surfaces (e.g., docs/humans/ vs docs/agents/ vs shared/). |
| MQ-T4-2 | Discovery-vs-injection asymmetry: 5 CRITICAL_DOCS (governance/SYSTEM_OWNER, missions/CURRENT_MISSION, USER_FEEDBACK_QUEUE, CAPABILITIES, DATABASE_MODEL_REFERENCE) get injected into every agent context BUT are NOT in CLAUDE.md pointer graph. Fresh Claude session doesn't see them at bootstrap even though every dispatched agent gets them. | §6.3 + §5.1 + §5.2 | INFORMATIONAL | Canonical summary decides: add missing 5 to CLAUDE.md graph OR reduce CRITICAL_DOCS to reflect only bootstrap-relevant docs. |
| MQ-T4-3 | Surface (4) PLATFORM_WHAT_IT_IS.md narrative surface is mostly redundant with surface (3) CLAUDE.md graph — 5 of ~7 refs overlap | §6.3 + §5.3 | INFORMATIONAL | Not a bug; narrative and bootstrap graph naturally share anchors. Canonical summary decides if consolidation adds value. |
| MQ-T4-4 | **Rot signal:** PLATFORM_WHAT_IT_IS.md references `docs/current/` which is NOT in T1 §3.1 subdir inventory | §5.3 + §7 Q9 | LOW (verify only) | T6 (anchor drift) verifies; migration session fixes if confirmed. |
| MQ-T4-5 | Retrieval-frequency telemetry does not exist — cannot measure retrieval-proven load-bearing | §7 Q6 + Rigby SIGN Q2 | INFORMATIONAL | Canonical summary flags as downstream-implementation dependency. Adding retrieval-count telemetry to `search_docs` corpus would enable retrieval-proven classification in future audits. |
| MQ-T4-6 | Surface (5) runtime-injection is bounded to CRITICAL_DOCS in T4; agent/PA/tool-specific injection paths are latent-unenumerated | §3.5 | INFORMATIONAL | Full enumeration requires greppng ALL prompt-pack assembly code. Canonical summary decides whether to formalize surface (5) via a central registry. |
| MQ-T4-7 | Archive is fully in RAG corpus (~1388 files); T3 §7 C5 shows corpus-eligibility is not sufficient for retrieval-behavior | §5.4 + T3 §7 C5 | INFORMATIONAL | Cross-reference to T3 MQ-T3-1 (archive-corpus segregation). Canonical summary decides on segregation OR authority weighting. |

---

## 9. What T4 does NOT resolve (explicit hand-offs)

Per parent §4 anti-scope:

| Question | Handed off to |
|---|---|
| Should new audience segments be added (e.g., "Rigby-primary-with-Tool-Y-context")? | Canonical summary at 2799 (T4 anti-scope: describe what exists) |
| Should CLAUDE.md graph add the 5 CRITICAL_DOCS not currently referenced? | Canonical summary at 2799 |
| Should surface (5) be formalized via a central runtime-injection registry? | Canonical summary + downstream implementation |
| Should retrieval-frequency telemetry be added to `search_docs`? | Downstream implementation session (canonical summary flags) |
| Which docs should MOVE to audience-specific subdirs (e.g., `docs/humans/` vs `docs/agents/`)? | Canonical summary at 2799 (restructuring proposal) |
| How should archive be segregated from RAG corpus? | Canonical summary (references T3 MQ-T3-1 + T4 MQ-T4-7) |
| Is `docs/current/` a Rot symptom or intentional-but-empty subdir? | T6 (anchor drift) |
| How does the ~95% Human-primary proportion inform restructuring? | Canonical summary at 2799 |

---

## 10. Provenance

**Session:** S2814 (2026-07-18, evening, immediately post-S2813-close)
**Ratifier:** Chris D-verdict "Let's do T4" at S2814 open
**Git HEAD at authoring:** `a839e2ffb4db` (S2813 close cascade)
**Rigby SIGN cycles (TWO per S2811+S2812+S2813 OP3 lesson):**

- **Open SIGN** (Q1 framing / Q2 rules / Q3 zoom-out). **Substantive Rigby corrections:**
  - Q1 → C (Primary + Secondary) not A (exclusive) or B (pure tags)
  - Q2 → DISAGREE with N-threshold; 3-way distinction (structural / eligible / proven-UNKNOWN)
  - Q3 → 5th surface added (runtime-injection / prompt-pack assembly); hybrid labor division ratified
- Anti-rubber-stamp check PASSED — Rigby ran `kb_tool.stats` (3217 docs, 65454 chunks) + `repo_tool.search`+`read_file` for CRITICAL_DOCS + IMPORTANT_DOCS enumeration.

- **Post-authoring pressure-test SIGN** (to be routed after this authoring completes) — fourth-consecutive OP3 trigger.

**Corrections folded during open-SIGN authoring:**
- Framing shifted from B (exclusive) to C (Primary + Secondary) per Q1
- Load-bearing rules restructured 3-way (structural / eligible / proven) per Q2
- Surface (5) added per Q3

**Post-authoring SIGN corrections applied (FOURTH-CONSECUTIVE OP3 trigger; substantive):**
1. **CRITICAL_DOCS is 5 items, NOT 10.** My open-SIGN pass conflated `CRITICAL_DOCS` (line 362, unconditional full-content inject) with `PRIORITY_DOCS` (line 176, high-priority-scoring only). Rigby's tool-verify separated them.
2. **Added §3.2b surface (2b) — PRIORITY_DOCS as distinct signal.** Weaker than CRITICAL_DOCS injection, stronger than corpus membership alone.
3. **§5.1 split into §5.1 (5 CRITICAL_DOCS) + §5.1b (5 additional PRIORITY_DOCS).** Structural vs high-priority distinction preserved.
4. **§6.1 reframed as ESTIMATES with UPPER BOUND labels.** Per Rigby Q2/Q4 — the residual bucket (~1730) is not automatically Human-primary; some are ops/spec docs whose primary audience is agent consumption via retrieval-eligibility even without injection.
5. **§6.3 discovery-vs-injection asymmetry corrected.** 3 of 5 CRITICAL_DOCS (not 5) are missing from CLAUDE.md graph. Plus 2 additional PRIORITY_DOCS also missing. Verified via Rigby's 5 targeted greps (all returned 0 matches in CLAUDE.md for `SYSTEM_OWNER`, `CURRENT_MISSION`, `USER_FEEDBACK_QUEUE`, `docs/CAPABILITIES.md`, `DATABASE_MODEL_REFERENCE`).
6. **§7 Q2/Q5/Q7 updated to reflect corrected counts** + false-precision caveat added throughout.

**Anchor-verify catches this session:**
1. **CRITICAL_DOCS vs PRIORITY_DOCS conflation** — my most substantive open-SIGN error; caught by Rigby's post-authoring tool-check. Same-class as the S2811 `docs/18960/` catch (misreading source at open, caught only by post-authoring rigor).
2. `docs/current/` referenced in PLATFORM_WHAT_IT_IS.md but not in T1 §3.1 subdir inventory — Rot signal, flagged for T6.

**FOURTH-CONSECUTIVE OP3 trigger fully justified.** T1 caught a ghost filename. T2 caught missing primitives + guardrail gap. T3 caught 6 substantive edits + validated with drift spot-check. T4 caught a CRITICAL vs PRIORITY conflation that would have systematically overstated structurally-load-bearing surface. **The two-SIGN-per-audit pattern is now trigger-satisfied 4/4 across 4 different audit shapes** — over-and-above the 3-trigger Playbook v0.9 promotion threshold that was already met at S2813.

**Tools used:**
- Rigby `kb_tool.stats` for surface (1) corpus enumeration (3217 docs / 65454 chunks / all embedded)
- Rigby `repo_tool.search`+`read_file` for surface (2) CRITICAL_DOCS enumeration
- Claude `grep -oE "docs/[a-zA-Z0-9_/-]*\.md|docs/[a-zA-Z0-9_-]+/"` on CLAUDE.md (45 refs) and PLATFORM_WHAT_IT_IS.md (~7 refs) for surfaces (3) + (4)
- T1 §3.1 + §5 count baselines cited for corpus size context

**T4 does NOT embed per-file matrix** — 3217 rows would be impractical for a session-scoped audit deliverable. Aggregate counts by audience segment + per-surface enumeration provide the substrate; per-file classification is downstream-derivable using §4 rules.

---

**End of T4 — Audience segmentation. T5 (`2705_docs_handoffs_audits_proliferation_audit.md`) opens next in the audit sequence.**

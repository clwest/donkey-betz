---
title: "S2811 /docs/ Inventory & Topology Audit (T1 of Group 2700 arc)"
status: active (audit deliverable — measurements, no judgment on movement)
authority: T1 child audit of Group 2700 parent arc
session: 2811
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
thread: T1
authors: Claude Code (Chris directed at S2811 open)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md   # parent (Chris-locked 2026-07-16)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                             # process framework
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                   # §2b runtime-coupled + §2c counts anchor + §3 root-stability
  - docs/PLATFORM_INVENTORY.md                                                            # runtime counts (cited, not restated)
  - docs/INDEX.md                                                                         # docs corpus counts (cited, not restated)
  - docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md                                  # prior /docs/ audit precedent
scope: T1 = what's IN /docs/ — measurements only, per parent §4 T1 scope
non_goals:
  - judgment on what should MOVE (T5 handoffs+audits; T6 anchor drift)
  - restructuring proposal (canonical summary at 2799)
  - file moves, deletions, renames, code changes (arc non-goals per parent §5)
  - restating counts that live in PLATFORM_INVENTORY.md or docs/INDEX.md (anti-duplicate per parent §4)
  - archive/ deep analysis (already partitioned; noted in scope table only)
delegates_to: T2 (research pattern extraction); T3 (human pain); T4 (audience segmentation); T5 (handoffs+audits proliferation); T6 (anchor drift)
owner: claude+rigby
---

# Session 2811 — /docs/ Inventory & Topology Audit (Group 2700, Thread 1)

> **What this doc is.** T1 measurements — ground-truth inventory of `/docs/` shape (dir tree, file counts, autogen distribution, freshness, size, subdir purpose). Every later thread references this as evidence.
>
> **What this doc is not.** Any proposal about restructuring, moves, deletes, renames. Any judgment about which subdirs should merge. Any policy recommendation. Those belong to T5/T6/canonical summary per parent §4.

---

## 1. Why T1 first

Per parent doc §4:

> T1 — Inventory & topology. Scope: what's IN /docs/ (dir tree, file counts, auto-gen vs hand-written distribution, freshness histogram, size distribution, subdir purpose taxonomy). Deliverable: ground-truth inventory that later threads reference. First to run.

T1 was queued as "next session opens the audit sequence" at parent-doc §11 (S2801, 2026-07-16). That "next session" was bumped 14 times by the Colorado Family Law arc. S2811 opens T1 fresh.

**Baseline evidence at S2800 (parent doc §3):** 2618 docs indexed, 1443 active / 11 draft / 1733 superseded, 676+ handoffs. **Baseline evidence at S2811 (this session):** 3201 total `.md` files under `docs/` — +580 files in 14 sessions. Drift confirmed; T1 measurements below reflect current state, not the S2800 baseline.

---

## 2. Existing anchors T1 cites (never restates)

Per parent §4 anti-duplicate rule:

| Source | What it authoritatively holds | This doc's usage |
|---|---|---|
| [`docs/PLATFORM_INVENTORY.md`](../../../PLATFORM_INVENTORY.md) | Runtime counts (agents 83/90, spiders 80, tasks 415, models 585, etc.) | T1 cites; never restates |
| [`docs/INDEX.md`](../../../INDEX.md) | Docs corpus counts (3197 docs indexed / 1453 active / 11 draft / 1733 superseded per S2810 cascade) | T1 cites; never restates |
| [`docs/00-START-HERE/DOC_LIFECYCLE.md`](../../../00-START-HERE/DOC_LIFECYCLE.md) §2b | Runtime-coupled paths (canon/, governance/SYSTEM_OWNER.md, missions/CURRENT_MISSION.md, decisions/ADR-*, ops/) — NEVER-MOVE | T1 flags these in §8 taxonomy |
| Parent doc §2 | 9 arc-wide constraints (root-stability, canon ≤10, DOC-POINTER-V1/V2, autogen-not-hand-edited, twin-pointer, Playbook v0.8.0) | T1 respects all |

---

## 3. Top-level topology

**48 directories + 99 loose `.md` files at `docs/` root** as of `git HEAD e9e4876ffb38` (S2810 close cascade).

### 3.1 Categorized subdir inventory

Grouped by inferred role (T1 does not judge — see §8 for detail):

**Research substrate (working pattern per parent §4 T2):**
| Subdir | MD files | Total files | First-line hint |
|---|---:|---:|---|
| `research/` | 226 | 226 | Domain-scoped arcs + platform-scoped audits + process OS + tools |

**Active handoff/audit accumulators:**
| Subdir | MD files | Total files | First-line hint |
|---|---:|---:|---|
| `handoffs/` | 1033 | 1033 | Session-N handoff docs (write-once, read-rarely per T5 scope) |
| `audits/` | 93 | 94 | Ad-hoc audit reports (largest of 3 parallel audit dirs) |
| `audit-2026/` | 15 | 15 | Numbered `00-AUDIT-PLAN.md` + `01-celery.md` … structured April 2026 attempt |
| `audit/` | 10 | 10 | `AUDIT_V1.md` + `CLEANUP_PLAN.md` + `README.md` — first-attempt substrate |

**Reference/inventory categories:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `topics/` | 21 | Per-subsystem narrative docs (agents, celery, spiders, etc.) |
| `architecture/` | 24 | Architecture diagrams + system-level design |
| `features/` | 18 | Per-feature capability docs |
| `guides/` | 18 | How-to guides |
| `narratives/` | 19 | Long-form narrative docs |
| `agents/` | 8 | Per-agent documentation |
| `apis/` | 8 | API contract docs |
| `apps/` | 9 | Per-app documentation |

**Governance / decision surfaces:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `adr/` | 4 | Architecture Decision Records |
| `decisions/` | 2 | `ADR-0001-execution-per-run-ephemeral-containers.md` + one other |
| `canon/` | 2 | INDEX.md (registry, ≤10 cap) + creative/ |
| `governance/` | 1 | `SYSTEM_OWNER.md` (runtime-coupled per DOC_LIFECYCLE §2b) |
| `missions/` | 1 | `CURRENT_MISSION.md` (runtime-coupled per DOC_LIFECYCLE §2b) |
| `ops/` | 1 md + 1 json | `integration_inventory_2026-01-28.json` snapshot |
| `operations/` | 1 | `pa-claude-code-collaboration.md` |
| `initiatives/` | 9 | Initiative-scoped work docs |

**Planning surfaces:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `roadmap/` | 10 | Structured numbered `00-GAP-ANALYSIS.md` + `01-AUTONOMOUS-DASHBOARD.md` … |
| `roadmaps/` | 2 | `INDEX.md` + `INTEGRATION_ROADMAP_2026.md` |
| `plans/` | 13 | Ad-hoc plan docs |
| `specs/` | 10 | Technical specifications |
| `designs/` | 5 | Design proposals |
| `pre-launch/` | 8 | Pre-launch checklist docs |

**Domain-specific surfaces:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `spokesperson/` | 11 | Spokesperson persona/content |
| `patents/` | 17 | Patent draft/reference docs |
| `mobile/` | 1 | `WEB_API_CONTRACTS.md` |
| `discord/` | 1 | `command_audit.md` |
| `body/` | 6 | Body systems docs |
| `case-studies/` | 1 | `donkey-betz-codex-audit.md` |

**Content generation:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `playbooks/` | 6 | 4 subdirs (creator/development/devops/marketing) |
| `context-packets/` | 1 | `obs-remote-control.md` |

**Process/orientation:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `00-START-HERE/` | 3 | Onboarding docs incl. `DOC_LIFECYCLE.md` |
| `docs-pattern/` | 22 | Context-kit framework (excluded from arc per DOC_LIFECYCLE §0) |
| `workflows/` | 2 | `INDEX.md` + one workflow |
| `tools/` | 2 | `pa-tool-manifest.md` + one other |
| `integrations/` | 2 | `BLENDER_API_INTEGRATION.md` + one other |

**Ad-hoc / small surfaces:**
| Subdir | MD files | Notable contents |
|---|---:|---|
| `BUGS/` | 2 | Bug tracker (only 2 files despite the name) |
| `verification/` | 1 | `VERIFY_REPORT.md` |
| `testing/` | 1 | `RUNTIME_INTEGRATION_TESTS.md` |
| `recons/` | 1 | `REPORTS_PATENTS_RECON_2026_05_25.md` |
| `reports/` | 33 | Report deliverables |
| `code-review/` | 24 | Code review outputs + remediation |
| `cleanup/` | 6 | Historical cleanup notes |

**Archived (leave alone per parent §7):**
| Subdir | MD files | Total files | Structure |
|---|---:|---:|---|
| `archive/` | 1388 | 1396 | 20+ dated subdirs (2025-09/, 2025-10/, handoffs-pre-800/, session_notes/, superseded-*/, etc.) |

### 3.2 Loose files at root

**99 `.md` files sit directly at `docs/` root.** Categorized by pattern:

| Pattern | Count (approx) | Examples |
|---|---:|---|
| `*_AUDIT.md` | 20 | `ADVISOR_AUDIT.md`, `PA_TOOL_AUDIT.md`, `BEAT_AUDIT.md`, `CELERY_AUDIT.md`, `RUNTIME_AUDIT.md`, `RAILWAY_WORKER_CONSOLIDATION_AUDIT.md` … |
| `*_INVENTORY.md` | ~7 | `PLATFORM_INVENTORY.md` (anchor), `CONTEXT_KIT_INVENTORY.md`, `BACKEND_INVENTORY.md`, `UI_INVENTORY.md`, `EVENT_SYSTEM_INVENTORY.md` |
| `*_REFERENCE.md` | ~4 | `AGENTS_REFERENCE.md`, `BACKEND_REFERENCE.md`, `DATABASE_MODEL_REFERENCE.md` |
| Anchors + governance | ~10 | `CLAUDE.md` (at repo root, not docs/), `PLATFORM_WHAT_IT_IS.md`, `PLATFORM_INVENTORY.md`, `ENGINEERING_PLAYBOOK.md`, `DOC_LIFECYCLE.md` (in 00-START-HERE/), `KNOWLEDGE_PIPELINE.md`, `UDB_BEHAVIOR_LAYER.md`, `UDB_TRANSLATION_LAYER.md`, `EOS_RULES.md`, `EMPLOYEE_OS_PRIMITIVES.md` |
| Session-loose | ~2 | `SESSION_780_PLATFORM_STATUS.md`, `SESSION_1251_CLAUDE_STARTUP_CONTEXT_PROPOSAL.md` (would normally go in handoffs/) |
| `MERGE_PROPOSAL_*.md` | 3 | `MERGE_PREP_TIER_4.md`, `MERGE_PROPOSAL_CHARACTER_OS.md`, `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` |
| Feature/spec at root | ~15 | `AI_PIXAR_IMPLEMENTATION_PLAN.md`, `AGENT_OUTPUT_TO_UI_MAPPING.md`, `24_7_GLOBAL_AI_APP_ATLAS.md`, `MORNING_BRIEF_SPEC.md`, `SCIFI_FEATURES.md`, `UI_COMPREHENSIVE_AUDIT.md` … |
| Duplication signals | ~5 | `AGENTS.md` vs `AGENTS_REFERENCE.md` vs `agents/` subdir; `ARCHITECTURE.md` vs `architecture/`; `MODELS.md` vs `DATABASE_MODEL_REFERENCE.md`; `SPIDERS.md` vs `SPIDER_AUDIT.md` vs `spiders_*` |
| Other | remainder | Miscellaneous docs |

Target from context-kit pattern: ≤~10 loose files at root (anchors + INDEX + a few generated manifests). Current 99 is **~10× target**.

---

## 4. Autogen vs handwritten distribution

**~70 files** carry an autogen marker (`DOC-AUTOGEN`, `<!-- Auto-generated`, `<!-- AUTOGEN`, `<!-- Generated by`, `autogenerated`) out of 1813 non-archive `.md` files = **~4% autogen / ~96% handwritten**.

Autogen files include:
- **Anchors + governance** — `DOC_LIFECYCLE.md`, `canon/INDEX.md`, `AGENTS_REFERENCE.md` (autogen from AGENT_MAP)
- **All root-level `*_AUDIT.md`** — `BEAT_AUDIT.md`, `CELERY_AUDIT.md`, `DISCORD_AUDIT.md`, `PA_TOOL_AUDIT.md`, `BODY_SYSTEM_AUDIT.md`, `CAPABILITY_AUDIT.md`, `CONNECTION_CENSUS_2026_05.md`, `ADVISOR_AUDIT.md`, `AUDIT_FINDINGS.md`, `CONTEXT_KIT_INVENTORY.md`, `DISCORD_INTEGRATION.md`
- **Session handoffs from a phase in S1102-1107** — these appear to be autogen from a handoff-materialization command that shipped that week
- **A few `audits/` docs** — `PA_TOOLS_GAP_MAP_S2795.md`, `PA_TOOLS_GAP_MAP_S2796.md`

**Flag only (T6 owns detailed enumeration):** autogen source paths and destination paths are coupled to their generator commands (e.g. `build_docs_index`, `refresh_doc_inventory_blocks`). Any migration proposal must coordinate generator updates with output moves. T1 flags the coupling; T6 enumerates the generator↔output map.

---

## 5. Size distribution

**1813 non-archive `.md` files:**

| LOC bucket | Count | % |
|---|---:|---:|
| <50 LOC (stub/short reference) | 604 | 33% |
| 50-200 LOC (short doc) | 572 | 31% |
| 200-1000 LOC (medium) | 530 | 29% |
| 1000-5000 LOC (long-form) | 107 | 5% |
| >5000 LOC | 0 | 0% |

**Top 15 largest non-archive `.md` files:**

| LOC | Path |
|---:|---|
| 4885 | `docs/research/ARCHITECTURE_INDEX.md` |
| 3814 | `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` |
| 3524 | `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` |
| 3207 | `docs/research/platform_architecture_inventory.md` |
| 2911 | `docs/research/platform/cross_domain_integration_audit.md` |
| 2896 | `docs/research/domains/event_integration_architecture/2002_event_integration_architecture_cat_b_hai_event_contract_design_child_audit.md` |
| 2416 | `docs/CAPABILITIES.md` |
| 2339 | `docs/research/authority_enforcement_design_space.md` |
| 2334 | `docs/research/domains/auth/2402_authorization_permission_floor_uniformity_audit.md` |
| 2304 | `docs/research/domains/rag_document_loading/2104_rag_document_loading_behavior_substrate_structured_observation_integration.md` |
| 2263 | `docs/EVENT_SYSTEM_INVENTORY.md` |
| 2252 | `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md` |
| 2241 | `docs/research/domains/sports/1599_sports_canonical_summary.md` |
| 2144 | `docs/PLATFORM_INVENTORY.md` |
| 2140 | `docs/PA_TOOL_AUDIT.md` |

**Observation:** 10 of the top 15 are in `docs/research/`. The long-form structured-document pattern lives almost exclusively in the research substrate. Other subdirs skew toward short (<200 LOC) documents. Whether this is a good split or a symptom of underused long-form patterns elsewhere is **out-of-scope for T1** — flagged for T2 (research pattern extraction) and canonical summary.

---

## 6. Freshness histogram

**Last-modified timestamp per file via `git log -1 --format=%at`, 1794 non-archive `.md` files:**

| Age bucket | Count | % |
|---|---:|---:|
| <7 days | 98 | 5% |
| 7-30 days | 462 | 25% |
| 30-90 days | 1077 | 60% |
| 90-365 days | 157 | 8% |
| >365 days | 0 | 0% |

**Observations:**
- **Zero files older than 365 days** — every non-archive doc has been git-touched in the last year. Likely explained by (a) high session cadence (14 same-day multi-ship pattern lately) + (b) frequent docs cascade PRs touching many files at once via INDEX regen.
- **60% in the 30-90d bucket** overlaps with the Colorado Family Law arc window (S2803+ started 2026-04-something? — verify against arc timeline in T3). Suggests a significant share of docs were touched by cascade PRs during Colorado ships without being conceptually updated.
- **8% in the 90-365d bucket** = ~157 candidate "genuinely stale" files. T1 does not adjudicate; T3 (human pain) + T5 (handoffs+audits) may find these.

**Methodology warning (strengthened per Rigby SIGN Q4):** "Last git touch" ≠ "last conceptually updated." A cascade PR that regenerates `INDEX.md` counts as a "touch" for `INDEX.md` even though its content was not authored. A commit that touches many files at once (mass-move, autogen re-run, cascade PR) inflates the recency signal for every file it touches without any conceptual review of those files. **Downstream authors (T2-T6, canonical summary) MUST NOT use §6 freshness numbers as a proxy for "this doc is still accurate."** For semantic recency, T3 or T5 need author-attribution analysis (last non-cascade commit that touched the body of the doc, filtered by author + commit message pattern) or explicit human review.

---

## 7. Arc-restart candidates

Chris directive at S2811 open (2026-07-18): "There's no telling how many times we have started something and then either something happens in real life or we did it late at night and I woke up the next day and was distracted and we started something else and never finished what we were working on." Recorded to auto-memory as `project_half_finished_arcs_from_life_interruptions`.

**T1 surfaces the visible evidence; T3 (human pain) + T5 (handoffs+audits) + T6 (anchor drift) adjudicate:**

### 7.1 Parallel-named subdir pairs/triples

| Group | Members | Content shape | Interpretation candidate (NOT resolved here) |
|---|---|---|---|
| `audit/` + `audit-2026/` + `audits/` | 10 + 15 + 93 = 118 files | `audit/AUDIT_V1.md` (labeled V1) → `audit-2026/00-AUDIT-PLAN.md` (structured Apr 2026) → `audits/*` (ad-hoc accumulator, 93 files) | Three attempts, likely V1 → structured → ad-hoc. Detailed diagnosis: T5. |
| `roadmap/` + `roadmaps/` | 10 + 2 files | `roadmap/00-GAP-ANALYSIS.md` + 9 numbered vs `roadmaps/INDEX.md` + `INTEGRATION_ROADMAP_2026.md` | Two parallel roadmap accumulators. |
| `operations/` + `ops/` | 1 + 1 md (+ 1 json) | `operations/pa-claude-code-collaboration.md` vs `ops/integration_inventory_2026-01-28.json` + README | Two singletons; possibly split by intent (ops = infra vs operations = process). |
| `handoffs/` + `archive/handoffs-pre-800/` + `archive/old-sessions/` | 1033 + [archive] + [archive] | Live handoffs vs partitioned archive | Working partitioning per S1143 audit cleanup; T5 may reevaluate. |

### 7.2 Loose root files that look like doubled/parallel effort

| Root file | Related subdir | Pattern |
|---|---|---|
| `AGENTS.md` + `AGENTS_REFERENCE.md` | `agents/` (8 files) | Same subject, 3 locations |
| `ARCHITECTURE.md` | `architecture/` (24 files) | Root anchor + subdir |
| `MODELS.md` + `DATABASE_MODEL_REFERENCE.md` | (no subdir) | Two references, same subject |
| `SPIDERS.md` + `SPIDER_AUDIT.md` | (no subdir) | Ref + audit at root |
| `SERVICES.md` | (no subdir) | Root ref, no subdir |
| `MERGE_PREP_TIER_4.md` + `MERGE_PROPOSAL_CHARACTER_OS.md` + `MERGE_PROPOSAL_CHARACTER_OS_NATIVE.md` | (no subdir) | Three related MERGE_* docs at root |
| `ROADMAP_IDEAS.md` | `roadmap/` + `roadmaps/` | Third roadmap-related location |
| `SESSION_780_PLATFORM_STATUS.md` + `SESSION_1251_CLAUDE_STARTUP_CONTEXT_PROPOSAL.md` | `handoffs/` (1033 files) | Session-named files loose at root, not in handoffs/ |

**T1 does not judge whether any of the above should merge or split.** T1 documents the visible-from-inventory evidence of the arc-restart pattern Chris described.

### 7.3 Orphan artifacts (none confirmed)

No numeric-named or unlabeled orphan directories confirmed at `docs/` root at authoring HEAD `e9e4876ffb38`. (Retracted from earlier draft: `docs/18960/` was a misread of the `total 18960` block-count line in `ls -la` output, not an actual directory. Rigby SIGN spot-check caught before ship.)

---

## 8. Subdir purpose taxonomy (short version)

Full per-subdir purpose inference is out-of-scope for T1 (T3 owns discoverability judgment). This section is the **short one-line inference from filename patterns** — evidence, not conclusion.

### 8.1 Runtime-coupled subdirs (NEVER-MOVE per DOC_LIFECYCLE §2b)

| Subdir | File | Runtime consumer (per DOC_LIFECYCLE §2b) |
|---|---|---|
| `canon/` | `INDEX.md` | Read by Python at runtime — registry contract |
| `governance/` | `SYSTEM_OWNER.md` | Read at runtime |
| `missions/` | `CURRENT_MISSION.md` | Read at runtime |
| `decisions/` | `ADR-*.md` | ADR-scan may read pattern |
| `ops/` | (json + readme) | Ops-tooling reads |

### 8.2 Autogen output subdirs (output only; source is a management command)

Not identified as whole-subdir autogen from the ~4% autogen distribution — autogen files are scattered across subdirs, not concentrated in dedicated output subdirs. Notable exceptions live at root (`docs/*_AUDIT.md` autogen batch).

### 8.3 Substrate subdirs (working pattern)

| Subdir | Pattern |
|---|---|
| `research/` | 5 subdirs (`domains/`, `implementation/`, `platform/`, `process/`, `tools/`) + top-level narratives. NNxx numbering convention in `domains/`. |
| `topics/` | Per-subsystem narrative (21 docs; matches PLATFORM_WHAT_IT_IS pointer set) |
| `docs-pattern/` | Context-kit framework — EXCLUDED from arc per DOC_LIFECYCLE §0 |
| `00-START-HERE/` | Onboarding entry point (3 docs including DOC_LIFECYCLE) |
| `handoffs/` | 1033 session-N handoff docs |
| `adr/` | 4 ADR-numbered decisions |

### 8.4 Ambiguous / mixed-purpose subdirs

| Subdir | Ambiguity |
|---|---|
| `plans/` vs `specs/` vs `designs/` vs `roadmap/` vs `roadmaps/` vs `pre-launch/` | 6 subdirs each holding some form of forward-looking design/plan work. Merging or partitioning is T3/T5 judgment. |
| `audit/` vs `audit-2026/` vs `audits/` vs 20 loose `*_AUDIT.md` | 4 audit surfaces. T5 territory. |
| `operations/` vs `ops/` | Split intent unclear from single files present. |
| `narratives/` vs `case-studies/` vs `spokesperson/` | 3 narrative-style subdirs. |

---

## 9. Playbook §9 canonical questions (adapted to inventory scope)

The Domain Research Playbook §9 lists 28 canonical questions. Per parent §4, T1 adapts where inventory scope makes a question inapplicable. Adapted for T1:

| Q# | Question (adapted) | T1 answer |
|---|---|---|
| Q1 | How big is the corpus? | 3201 total `.md` files (1813 non-archive + 1388 archive) |
| Q2 | How much is autogen? | ~70 files with autogen markers = ~4% of non-archive |
| Q3 | What's the size distribution? | See §5 |
| Q4 | What's the freshness distribution? | See §6 |
| Q5 | How much is at root vs partitioned? | 99 loose `.md` at root (~5% of non-archive) + 48 top-level subdirs holding the rest |
| Q6 | Are there parallel/duplicated subdirs? | Yes — see §7.1 (audit×3, roadmap×2, operations×2) |
| Q7 | Are there loose-root doublings of subdir content? | Yes — see §7.2 |
| Q8 | Runtime-coupled paths inventory? | 5 subdirs per DOC_LIFECYCLE §2b — see §8.1 |
| Q9 | Autogen output subdirs? | None concentrated; scattered across handoffs/root/audits — see §8.2 |
| Q10 | Substrate subdirs (working pattern)? | 6 subdirs — see §8.3 |
| Q11 | Ambiguous / mixed-purpose subdirs? | ≥4 categories — see §8.4 |
| Q12 | Orphan/anonymous subdirs? | None confirmed at HEAD — see §7.3 |
| Q13-Q28 | Discoverability, audience segmentation, citation graph, human pain, restructure proposal, migration risk, aliasing/redirects, autogen coordination, canon inflation risk, twin-pointer, cross-arc coordination, etc. | **Out of T1 scope** — belongs to T2/T3/T4/T5/T6/canonical summary |

---

## 10. Migration Queue (post-arc)

Per parent §5, each child audit ships a Migration Queue section for the follow-on migration session to consume. **T1's queue is measurement-derived only — no restructuring proposal. Severity: informational.**

| # | Item | Evidence source (this doc) | Severity | Notes for migration session |
|---|---|---|---|---|
| MQ-T1-1 | Three parallel audit dirs (`audit/`, `audit-2026/`, `audits/`) + 20 loose `*_AUDIT.md` at root — 138 files across 4 surfaces | §3.1 + §7.1 + §7.2 | INFORMATIONAL | Do not move during arc. T5 designs. |
| MQ-T1-2 | Two parallel roadmap dirs (`roadmap/`, `roadmaps/`) + `ROADMAP_IDEAS.md` at root | §7.1 + §7.2 | INFORMATIONAL | Do not move during arc. T5 designs. |
| MQ-T1-3 | Two singleton subdirs (`operations/`, `ops/`) | §7.1 | INFORMATIONAL | Do not move during arc. T5 designs. |
| MQ-T1-4 | 99 loose files at `docs/` root vs context-kit target ~10 | §3.2 | INFORMATIONAL | Do not move during arc. T3 measures human pain from this; T5/canonical summary designs. |
| MQ-T1-5 | Loose session-named files at root (`SESSION_780_*`, `SESSION_1251_*`) | §7.2 | INFORMATIONAL | Do not move during arc. T5 may propose relocation to handoffs/. |
| MQ-T1-6 | Mixed-purpose forward-planning cluster (`plans/` 13 + `specs/` 10 + `designs/` 5 + `roadmap/` 10 + `roadmaps/` 2 + `pre-launch/` 8 + root `ROADMAP_IDEAS.md`) — 6 subdirs + 1 loose file for forward-looking design/plan work | §3.1 + §8.4 | INFORMATIONAL | Do not move during arc. T3 measures human pain from the split; T5/canonical summary designs consolidation target. |
| MQ-T1-7 | Autogen files (~70) scattered across handoffs/root/audits — generator paths coupled to output paths | §4 | INFORMATIONAL | T6 enumerates; migration session updates generators alongside any autogen output moves. |
| MQ-T1-8 | Doubled root files vs subdir content (`AGENTS.md`/`AGENTS_REFERENCE.md`/`agents/`, `ARCHITECTURE.md`/`architecture/`, `MODELS.md`/`DATABASE_MODEL_REFERENCE.md`, `SPIDERS.md`/`SPIDER_AUDIT.md`) | §7.2 | INFORMATIONAL | T5/canonical summary designs. |
| MQ-T1-9 | 3 MERGE_PROPOSAL_* docs at root — historical artifacts from a possibly-abandoned character-os merge arc | §7.2 | LOW (verify only) | Migration session spot-checks whether merge shipped or was abandoned; move to archive/ if abandoned. |

---

## 11. What T1 does NOT resolve (explicit hand-offs)

Per parent §4 anti-duplicate:

| Question | Handed off to |
|---|---|
| What should MOVE, MERGE, or SPLIT? | T5 (handoffs+audits) + T6 (anchor drift) + canonical summary at 2799 |
| Which primitives from `docs/research/` transfer to other subdirs? | T2 (research pattern extraction) |
| Where does discoverability break for humans? | T3 (human pain) |
| Which audience is each file for? | T4 (audience segmentation) |
| Which duplicated rules across playbook/CLAUDE.md/memory drift? | T6 (anchor drift) |
| What's the citation graph on handoffs? Which get read months later? | T5 (handoffs+audits) |
| Should CURRENT_MISSION.md / SYSTEM_OWNER.md / canon/INDEX.md have their own top-level partitioning? | Canonical summary at 2799 (under DOC_LIFECYCLE §2b constraint) |
| Design of the target `/docs/` tree | Canonical summary at 2799 |

---

## 12. Provenance

**Session:** S2811 (2026-07-18, mid-afternoon open)
**Ratifier:** Chris D-verdict "Approved!" at S2811 T1 open
**Git HEAD at authoring:** `e9e4876ffb38` (S2810 close cascade)
**Rigby SIGN cycle:** Q1/Q2/Q3/Q4 (dir placement / session scope / thread taxonomy / zoom-out) — AGREE across all 4 with refinements. Anti-rubber-stamp check PASSED — tool_runs included `repo_tool.search`/`read_file` verifying (a) `docs/research/domains/` existing shape, (b) `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` v2 pattern, (c) downstream systems that read from `docs/` (`build_docs_index` → `_index.json` → `.rag/corpus.jsonl` → `unified_embeddings` chain + hardcoded `/docs/X.md` help-URLs in `core/error_messages.py`).

**Anchor-verify catches at S2811 open (3):**
1. Parent scoping doc (`2700_docs_restructuring_domain_scoping.md`) already exists and is LOCKED at S2801 with 6-thread package — Rigby correctly noted "already exists"; Claude verified 20307-byte body with Chris-locked decisions.
2. 6-thread scope in parent doc corrects the 4-thread number I had in auto-memory (`project_docs_restructuring_arc_queued`) — memory note is stale on that specific detail; will update at S2811 close.
3. Baseline evidence drift: parent §3 cites 2618 docs at S2800; current is 3201 (+583 in 14 sessions). T1 uses current state; parent §3 kept as-authored per no-restructure-during-arc rule.

**Tools used to gather T1 measurements:**
- `find docs -type d/f -name '*.md'` for tree + counts
- `git log -1 --format=%at -- <f>` for last-modified timestamps
- `wc -l` for LOC counts
- `grep -l 'DOC-AUTOGEN\|<!-- Auto-generated\|<!-- AUTOGEN'` for autogen distribution
- `ls docs/<subdir>/` for first-line-of-subdir hints

**T1 does not embed live counts** — all counts are timestamped at authoring (git HEAD `e9e4876ffb38`). Regeneration by re-running the queries above; not automated.

---

**End of T1 — Inventory & topology. T2 (`2702_docs_research_pattern_extraction_audit.md`) opens next in the audit sequence.**

# Engineering Playbook Architecture Specification

**Session:** 2712 (Playbook architecture specification — not Playbook content)
**Date:** 2026-07-08
**Status:** Specification — awaiting Chris's review
**Predecessors:**
- 2708: `engineering_playbook_architecture_proposal.md` (Option A/B/C placement analysis)
- 2709: `workspace_architecture_and_constitution_proposal.md` (Workspace-as-Operator-OS)
- 2710: `platform_architecture_workspace_boundary_analysis.md` (Fleet→Platform→Tenant→User→Workspace stack)
- 2711: `platform_constitutional_architecture.md` (Tiered ratification model; documentary vs executable constitution)

**Author:** Claude (Opus 4.7, 1M context)

**Scope constraints per mission:** Design the *architecture* of the Engineering Playbook. Not the content. Not the implementation. No ADRs. No workspace deliverables. No Playbook chapters authored. Repository ends clean (this document + four untracked prior proposals only).

**Constitutional architecture assumed accepted:** per 2711 §18. The six-layer stack (Fleet→Platform→Tenant→User→Workspace→Deliverable) and the tiered ratification-based authority model are load-bearing inputs. This specification does not re-derive them.

**Deliverable:** one document. This one.

---

## 0. How to read this specification

This specification treats the Playbook as a production subsystem. Every design decision below is intended to survive from Playbook v0.1 (initial draft) through Playbook v2.x (mature amendment cycles) without restructuring.

The specification is dense; sections are independently readable. If you have only 5 minutes, read §1 (Executive Summary) + §5 (Frontmatter schema) + §7 (Semver strategy) + §17 (Recommendation).

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Design principles](#2-design-principles)
3. [Document architecture](#3-document-architecture)
4. [Ownership model](#4-ownership-model)
5. [Frontmatter and version metadata schema](#5-frontmatter-and-version-metadata-schema)
6. [Repository placement](#6-repository-placement)
7. [Semantic versioning strategy](#7-semantic-versioning-strategy)
8. [Ratification lifecycle](#8-ratification-lifecycle)
9. [Update workflow](#9-update-workflow)
10. [Supersession model](#10-supersession-model)
11. [Evidence and traceability model](#11-evidence-and-traceability-model)
12. [Source mapping strategy](#12-source-mapping-strategy)
13. [Git integration](#13-git-integration)
14. [Workspace ratification envelope specification](#14-workspace-ratification-envelope-specification)
15. [Release process](#15-release-process)
16. [Extension points — from v0.1 through v2.x](#16-extension-points--from-v01-through-v2x)
17. [Pressure test / falsification](#17-pressure-test--falsification)
18. [Risks](#18-risks)
19. [Unknowns](#19-unknowns)
20. [Recommendation](#20-recommendation)
21. [Closing](#21-closing)

---

## 1. Executive summary

The Engineering Playbook is designed as **L2 platform-level constitutional infrastructure** with the following architectural shape:

- **Physical form:** a single Markdown file `docs/ENGINEERING_PLAYBOOK.md` in the repository, with an evidence-index sidecar `docs/research/playbook/evidence_index_v<X_Y_Z>.md` per ratified version.
- **Canonical authority:** `repo_canonical` per KFI-2 (source_reference is the file path; `_derive_canonical_authority` B3 branch classifies it automatically once mirrored into `content.Document`).
- **Version metadata:** YAML frontmatter carrying 12 fields (§5). Machine-readable; cross-referenceable by CI + verify_repo_guardrails.
- **Semantic versioning:** `MAJOR.MINOR.PATCH` with rule-change semantics (§7). Playbook v0.1 → v0.5 → v1.0 → v2.x supported without restructuring.
- **Ratification lifecycle:** 6-stage (Propose → Author → SIGN → Correct → Ratify → Mirror). Every ratification produces a workspace-canonical ratification record naming the git tag + commit SHA + Chris's verbatim directive.
- **Immutability:** git tag (cryptographic) + workspace `status=completed` (governance) + optional content_hash (Cycle 2 hardening).
- **Update workflow:** amendment PR on branch `playbook/vX.Y.Z-<slug>` → SIGN → Chris directive → merge → tag → workspace ratification → cascade.
- **Supersession:** parent-chain via `parent_object_id` on ratification records + `Supersedes` frontmatter field on Playbook itself. Prior versions preserved via git tags AND ratification record chain.
- **Traceability:** every normative claim in the Playbook must cite one of six evidence classes (§11) at the paragraph level. Evidence index sidecar enumerates all citations.
- **Extension points:** chapter-level extensibility (new chapters slot in without renumbering), frontmatter extensibility (JSON-safe additions), symbolic cross-references (no chapter-number hard-coding).

**The specification survives all 9 pressure-test categories (§17)** with no unresolved falsification. Three areas require Cycle 2 hardening (content_hash population, ORM-level immutability enforcement, CI-level frontmatter validation) but none blocks v0.1 authoring.

**Recommendation (§20):** adopt this specification as the architectural foundation for Playbook v0.1 authoring in Session 2713. Cycle 2 hardening (three items) can proceed in parallel with Playbook drafting.

---

## 2. Design principles

Four design principles constrain every downstream decision in this specification. They are stated here so they can be audited independently.

### 2.1 Constitutional first, documentary second

The Playbook is not a document that *describes* how work is done. It is a *governing artifact* that *declares* how work must be done, subject to ratification. Every architectural decision below prefers governance integrity over documentary convenience.

**Applied consequence:** version metadata is machine-readable and CI-verifiable, not just human-readable. Ratification records are ORM-queryable, not just narrative claims. Supersession is a first-class relation, not just a text reference.

### 2.2 Evidence-cited or absent

Every normative claim in the Playbook must cite evidence from one of the six evidence classes enumerated in §11. If no such evidence exists, the claim is not yet Playbook-ready. It stays in a WIP research doc until evidence catches up.

**Applied consequence:** the Playbook cannot codify opinion. It can only codify observed-and-agreed patterns.

### 2.3 Semver reflects rule change, not text change

`MAJOR.MINOR.PATCH` semantics tracked in the Playbook are about *rule change*, not text volume. A 50-line typo fix is PATCH. A one-sentence rule addition is MINOR. A one-sentence rule removal is MAJOR.

**Applied consequence:** semver is meaningful for downstream consumers (Claude sessions must know if their expectations are still valid) rather than a text-diff metric.

### 2.4 Ratification is the governance seam; git is the substrate seam

Git tags provide cryptographic immutability of the body. Workspace ratification records provide governance immutability of the act. Both are load-bearing. Neither can substitute for the other.

**Applied consequence:** ratification records name the git tag AND commit SHA AND ratifier directive verbatim; git tags name the SHA and (via message) the ratification record UUID. Cross-linking is bidirectional.

---

## 3. Document architecture

The Playbook is designed as a **single markdown file** with chapter-level structure. Chapters can be split into per-file chapters (`docs/playbook/chapter_XX_*.md`) if the master file exceeds ~10k lines in a future version, but the physical layout stays single-file through v2.x.

### 3.1 Chapter organization — 10-chapter proposal

Chapters below are proposed as a stable organizing structure. Chapter numbers are STABLE across versions (renumbering is forbidden — new chapters go into reserved slots or appendices). Chapter titles may evolve (title changes are MINOR unless they change scope).

| Ch. | Title | Scope | Extension policy |
|---|---|---|---|
| 0 | Preamble & how to read this Playbook | Meta — reader orientation | Editable each MINOR; renumber-safe |
| 1 | Constitutional context | The tiered ratification model this Playbook itself sits within (per 2711) | Rarely changes; MAJOR-only |
| 2 | Research methodology (RAR / SIGN / research OS) | How research is conducted, closed, ratified | Extends via new sub-sections per new methodology |
| 3 | Implementation discipline (verify-before-build, ADR authoring) | How platform code changes happen | Extends per new ADR pattern |
| 4 | Documentation cascade | 4-step cascade + embed + workspace mirror discipline | Extends per new cascade step |
| 5 | PA / Rigby collaboration protocol | Claude / Rigby / Chris interaction discipline | Extends per new tool-surface pattern |
| 6 | Provenance classification standard (PIC-10) | Statement classes required for immutable artifacts | Extends per new evidence class |
| 7 | Session discipline | Session open, close, handoff, cascade | Extends per new session pattern |
| 8 | Runtime discipline (executable constitution) | CockpitAutopilotPolicy, AgentControlEntry, Budget, PublishGate | Extends per new runtime-policy class |
| 9 | Recovery & incident playbooks | Worker instability, cascade failure, ratification defects | Extends per new recovery pattern |
| 10 | Evolution & amendment | This meta-chapter — how the Playbook evolves | Reserved for meta-changes only |

**Two reserved chapter slots** at 11 and 12 for future MINOR additions without renumbering. Slots 13-19 reserved for future chapters. Slot 20+ reserved for appendices (§3.4).

### 3.2 Per-chapter template

Every chapter uses this template so the reader always knows where to look:

```markdown
## Chapter N — <title>

### N.0 Chapter frontmatter
- Purpose: <one sentence — the rule this chapter codifies>
- Scope: <which layer / which artifact class this governs>
- Introduced: <version — the Playbook version this chapter was introduced in>
- Last substantive change: <version — most recent non-PATCH change>
- Evidence anchor: <link into evidence_index_vX.Y.Z.md>

### N.1 <primary rule>
### N.2 <secondary rule>
### ...
### N.M Cross-references
- To Chapter N-of-related
- To ADR nnnn
- To ratification record RATIFICATION_YYYYMMDD_...
- To evidence_index §N.M

### N.M+1 Extension points
- <named slots for future MINOR additions>
```

**Applied to every chapter without exception.** Consistency itself is a constitutional discipline.

### 3.3 Per-chapter 8-question analysis (from mission)

The mission required Purpose / Scope / Inputs / Outputs / Authoritative sources / Ratification requirements / Dependencies / Future extension points for each major section. The template above collapses these into 5 mandatory fields (Purpose, Scope, Introduced, Last-changed, Evidence anchor) plus the natural body (inputs/outputs/dependencies show up as citations). Below, per-chapter answers to all 8 questions.

#### Chapter 0 — Preamble & how to read this Playbook

- **Purpose:** orient the reader; declare version metadata visibility; state authorial voice.
- **Scope:** meta — governs the reader experience of the Playbook itself.
- **Inputs:** frontmatter; §21 Closing; last handoff for currently-referenced Cycle.
- **Outputs:** reader knows where to look for what.
- **Authoritative sources:** this specification (§0, §3.1).
- **Ratification requirements:** MINOR-editable; PATCH for typos; MAJOR only if the entire chapter organization changes.
- **Dependencies:** none.
- **Extension points:** new "how to read" sections per new reader class (e.g., new-hire onboarding subsection).

#### Chapter 1 — Constitutional context

- **Purpose:** locate the Playbook within the six-layer stack; declare Playbook = L2 artifact.
- **Scope:** the tiered authority model, per 2711.
- **Inputs:** 2711 constitutional architecture; ADR 0000/0005/0010/0100; Cycle 1A ratifications.
- **Outputs:** reader can locate this Playbook's scope against workspace-canonical vs repo-canonical artifacts.
- **Authoritative sources:** 2711 §18 (formal constitutional architecture answer); this spec §1.
- **Ratification requirements:** MAJOR only — constitutional context should be stable across normal amendments.
- **Dependencies:** Cycle 0 ratifications (0000/0005/0010/0020), Cycle 1A ratifications.
- **Extension points:** new layers (Fleet, Tenant activation) → new subsections at 1.6+ (reserved).

#### Chapter 2 — Research methodology

- **Purpose:** codify SIGN cycle, arc open/close discipline, evidence gathering standards.
- **Scope:** all research arcs; all Cycle open/close events.
- **Inputs:** 0000_RAR_METHODOLOGY; 0010_RESEARCH_OPERATING_PROTOCOL; SESSION_2705/2706/2707 SIGN precedents; feedback_rigby_sign_worker_instability_recovery.md.
- **Outputs:** consistent SIGN outputs; ratifiable arc close records.
- **Authoritative sources:** 0000; 0010; PIC-9 (SIGN recovery); PIC-7 (SIGN discipline).
- **Ratification requirements:** MINOR-extensible per new SIGN pattern; MAJOR if the SIGN cycle itself is redesigned.
- **Dependencies:** Chapter 1 (constitutional context).
- **Extension points:** SIGN cycle variants for research classes not yet enumerated in 0010 §5.

#### Chapter 3 — Implementation discipline

- **Purpose:** codify the verify-before-build rule; ADR authoring template; Cycle 1A implementation lessons.
- **Scope:** every code change that would qualify for an ADR.
- **Inputs:** feedback_cycle_1a_verify_before_build.md; ADRs 0110-0150 as exemplars; 0199 §2 implementation ledger.
- **Outputs:** consistent ADR authoring; reduced parallel-surface duplication.
- **Authoritative sources:** MEMORY.md `feedback_cycle_1a_verify_before_build`; Cycle 1A ADRs.
- **Ratification requirements:** MINOR for new discipline additions.
- **Dependencies:** Chapter 2 (research methodology feeds implementation).
- **Extension points:** stricter thresholds (e.g., §14.2 Chris refinement-authority prerogative) codified into IOS versions.

#### Chapter 4 — Documentation cascade

- **Purpose:** codify the 4-step docs cascade with embed step; PR discipline.
- **Scope:** every docs-modifying PR; every arc close.
- **Inputs:** feedback_docs_pipeline_4_step_cascade.md; feedback_docs_cascade_at_every_close.md; feedback_cascade_pr_must_include_embed_step.md; ADR 0140 (docs cascade automation).
- **Outputs:** RAG corpus stays fresh across sessions.
- **Authoritative sources:** MEMORY.md cascade rules; ADR 0140; SESSION 1802 close forensics.
- **Ratification requirements:** MINOR per new cascade step; MAJOR for cascade re-architecture.
- **Dependencies:** Chapter 3 (implementation discipline); ADR 0140.
- **Extension points:** per-workspace cascade variants (Cycle 3+ multi-tenant).

#### Chapter 5 — PA / Rigby collaboration protocol

- **Purpose:** codify the "Claude directs, Rigby executes, Claude verifies" default shape.
- **Scope:** all agent-mediated work; all PA tool calls; all Rigby SIGN sessions.
- **Inputs:** feedback_claude_directs_rigby_then_verifies.md; feedback_verifier_loop_pattern.md; feedback_rigby_tool_verification.md; PA_TASK_SUMMARY logs.
- **Outputs:** consistent tool-surface exercise; verified deliverables.
- **Authoritative sources:** MEMORY.md rigby rules; PA tool schema catalog.
- **Ratification requirements:** MINOR per new PA tool pattern.
- **Dependencies:** Chapter 3 (implementation), Chapter 4 (cascade).
- **Extension points:** new PA tool surface additions; multi-user Rigby coordination (Cycle 3+).

#### Chapter 6 — Provenance classification standard (PIC-10)

- **Purpose:** codify the 5 statement classes (verified primary evidence, verified repository/runtime fact, verified quoted source, historical reconstruction, engineering conclusion) for every immutable artifact.
- **Scope:** every ratification record; every immutable artifact; every SIGN batch report.
- **Inputs:** 0199 Appendix D PIC-10 candidate; 0199 §8 G1 correction (Rigby FAIL verbatim + provenance-honest reconciliation).
- **Outputs:** ratification records that survive future forensic queries.
- **Authoritative sources:** 0199 Appendix D; 0199 §8; ratification record `c883ebef-…`.
- **Ratification requirements:** MAJOR for statement-class changes; MINOR for new evidence subclasses.
- **Dependencies:** Chapter 1 (constitutional context); Chapter 8 (executable constitution — provenance rules apply to runtime policy too).
- **Extension points:** classification for cross-repo (mentorforge / character-os) evidence.

#### Chapter 7 — Session discipline

- **Purpose:** codify session-open orientation; session-close cascade; handoff completeness.
- **Scope:** every Claude Code session against unified-donkey-betz.
- **Inputs:** feedback_session_open_with_orient.md; docs/handoffs/SESSION_XXXX_*; SESSION 1246 bedtime-framing correction; CLAUDE.md startup checklist.
- **Outputs:** sessions open cleanly; sessions close cleanly; handoffs are complete.
- **Authoritative sources:** CLAUDE.md startup checklist; MEMORY.md session rules; 00-START-NEXT-SESSION patterns.
- **Ratification requirements:** MINOR per new session pattern.
- **Dependencies:** Chapter 4 (cascade discipline at session close).
- **Extension points:** multi-Claude-session coordination (parallel sessions).

#### Chapter 8 — Runtime discipline (executable constitution)

- **Purpose:** codify the documentary-vs-executable constitution split; policy discipline for CockpitAutopilotPolicy, AgentControlEntry, Budget.
- **Scope:** every runtime-policy row in Postgres governance tables.
- **Inputs:** 2711 §2.4 evidence; CockpitAutopilotPolicy 4-row inventory; AgentControlEntry 1-row; Budget 6-row; PublishGate state machine.
- **Outputs:** consistent runtime policy authoring; auditable executable constitution.
- **Authoritative sources:** 2711 §2.4; code paths (`core/models*.py` for the tables); admin UI.
- **Ratification requirements:** MAJOR if runtime governance mechanism changes.
- **Dependencies:** Chapter 6 (provenance applies to runtime policy authors).
- **Extension points:** per-tenant executable constitution (Cycle 3+); fleet-level executable constitution (Cycle 4+).

#### Chapter 9 — Recovery & incident playbooks

- **Purpose:** codify recovery flows for known failure classes.
- **Scope:** worker stalls, SIGN worker instability, cascade drift, ratification defects.
- **Inputs:** feedback_local_celery_stall_playbook.md; feedback_rigby_sign_worker_instability_recovery.md; SESSION 1226 verifier-loop pattern; SESSION 2707 §4-§6 correction discipline.
- **Outputs:** consistent recovery patterns; reduced MTTR for known failures.
- **Authoritative sources:** MEMORY.md recovery-labeled feedback; SESSION handoffs with recovery sections.
- **Ratification requirements:** MINOR per new recovery pattern; MAJOR for methodology-inverting recovery.
- **Dependencies:** Chapter 4 (cascade fixes are recovery); Chapter 5 (PA-mediated recovery).
- **Extension points:** cross-app recovery (fleet incidents); Cycle 3+ tenant-scoped recovery.

#### Chapter 10 — Evolution & amendment

- **Purpose:** meta-chapter. Codifies how THIS Playbook evolves (semver, ratification, supersession).
- **Scope:** every amendment PR; every version bump; every supersession record.
- **Inputs:** this specification §7-§10, §14-§15.
- **Outputs:** consistent amendment lifecycle; auditable supersession chain.
- **Authoritative sources:** this specification; workspace ratification records for prior Playbook versions.
- **Ratification requirements:** MAJOR for evolution mechanism changes (this chapter is stable by design).
- **Dependencies:** Chapter 1 (constitutional context); Chapter 6 (provenance for amendment records).
- **Extension points:** multi-tenant amendment coordination; fleet-shared amendment coordination.

### 3.4 Appendices

Appendices are numbered 20+ (leaving room for chapters 11-19). Proposed:

| App. | Title | Purpose |
|---|---|---|
| A | Evidence index (per-version) | Full citation list; usually externalized to `docs/research/playbook/evidence_index_v<X_Y_Z>.md` |
| B | Glossary | Terms of art (SIGN, PIC, cascade, workspace-canonical, etc.) |
| C | Source map | Per-chapter source-class requirements (from §12) |
| D | Prior-version change log | Table of every version with git tag + SHA + ratification record UUID |
| E | Extension slot inventory | Reserved slots + when to use them |

Appendices are re-generatable from primary data; treat them as autogen-safe.

### 3.5 Cross-reference conventions

To make renumbering safe (§16), cross-references use **symbolic anchors**, not chapter numbers:

- ✓ `See Chapter "Documentation cascade" §"Four-step contract"` — survives chapter renumbering
- ✗ `See §4.2` — breaks if Chapter 4 becomes Chapter 5

**Applied consequence:** chapter titles become part of the constitutional surface. Renaming a chapter title is at least a MINOR bump because it breaks cross-references.

### 3.6 Autogen sub-sections

Certain chapters have subsections that should be auto-generated from primary evidence (Chapter 8's runtime policy inventory, Appendix A's evidence index, Appendix D's version chain). Autogen subsections are wrapped in `<!-- DOC-AUTOGEN start:section_key -->` … `<!-- DOC-AUTOGEN end:section_key -->` markers per existing convention (`docs/INDEX.md`).

**verify_repo_guardrails.py must reject hand-edits between the markers** — same discipline as `docs/INDEX.md` today.

---

## 4. Ownership model

Ownership is decomposed into 5 roles. Each role has explicit authority. No role can perform actions outside its authority.

### 4.1 Ratifier (Chris)

- **Authority:** the sole source of ratification directives. Only Chris can authorize `content_tool.content_complete` on a Playbook ratification record.
- **Cannot:** author the Playbook body himself (though he can propose amendments). Enforcement of role separation.
- **Delegation:** L0 human ratifier. Multi-tenant future (Cycle 3+) may add tenant admins as ratifiers for tenant-scope playbooks; the Donkey Betz Playbook ratifier remains Chris.

### 4.2 Author (Claude / Rigby)

- **Authority:** propose Playbook drafts, amendments, SIGN reports, correction passes.
- **Cannot:** ratify; publish without SIGN.
- **Discipline:** every draft or amendment must be evidence-cited per §11 before entering SIGN.

### 4.3 Reviewer (SIGN cycle)

- **Authority:** perform adversarial SIGN review; identify F-BLOCKING findings; recommend correction passes.
- **Executor of role:** Rigby (per feedback_claude_directs_rigby_then_verifies.md); Claude verifies findings.
- **Cannot:** ratify; author.

### 4.4 Cascade automation

- **Authority:** mirror the ratified Playbook body into `content.Document` with `canonical_authority='repo_canonical'`; regenerate autogen appendices; refresh CLAUDE.md L7 anchor to reference the newly-ratified version.
- **Cannot:** modify Playbook body; create ratification records.
- **Discipline:** cascade must run as step 4 of the docs cascade (feedback_cascade_pr_must_include_embed_step.md).

### 4.5 Reader / consumer

- **Authority:** consult the Playbook; obey its rules.
- **Cannot:** modify; propose amendments without going through Author role.

### 4.6 Role separation summary

| Role | Propose | Author | SIGN | Correct | Ratify | Mirror | Consult |
|---|---|---|---|---|---|---|---|
| Ratifier (Chris) | ✓ | — | — | ✓ (directive) | ✓ | — | ✓ |
| Author (Claude) | ✓ | ✓ | — | ✓ (execution) | — | — | ✓ |
| Reviewer (Rigby SIGN) | — | — | ✓ | — | — | — | ✓ |
| Cascade automation | — | — | — | — | — | ✓ | — |
| Consumer (all others) | ✓ (via Chris) | — | — | — | — | — | ✓ |

**Applied consequence:** the Playbook has explicit role separation. This prevents pathological outcomes like "Claude ratified its own draft" or "Rigby corrected without SIGN pressure."

---

## 5. Frontmatter and version metadata schema

The Playbook begins with YAML frontmatter carrying 12 fields. Every field is required for `status=ratified`; optional fields are marked. The frontmatter is machine-readable — `verify_repo_guardrails.py` validates it; CI can validate it; PA tools can query it.

### 5.1 Full schema

```yaml
---
# Identity
title: "Donkey Betz Engineering Playbook"
scope: "platform (L2)"       # Enum: platform (L2) | workspace (L5) | fleet (L1) | tenant (L3)

# Versioning
version: "1.0.0"             # Semver MAJOR.MINOR.PATCH per §7
version_status: "ratified"   # Enum: draft | signing | correction | ratified | superseded
parent_version: null         # Prior semver of this Playbook; null for v1.0.0 inaugural
supersedes:                  # List of prior versions this one deprecates
  - "0.9.0"
compatible_with:             # Other artifacts this version acknowledges as valid
  cycle_1a_adrs: ["0110", "0120", "0130", "0140", "0150"]
  cycle_0_adrs:  ["0000", "0005", "0010", "0020"]
  cycle_open_close: ["0100", "0199"]
  research_os: "0010"
  rar_methodology: "0000"

# Ratification
ratified_date: "2026-07-XX"                                                # ISO date
ratifier: "chris"                                                          # UnifiedUser.username
ratification_directive: "Ratification is authorized. …verbatim…"           # Verbatim ratifier directive
ratification_record:
  workspace_id: "a9a16593-e0a4-44dc-8256-efc65d524b3c"                    # Architecture & Research
  deliverable_id: "<uuid-of-workspace-ratification-record>"
  title: "RATIFICATION_20260XXX_PLAYBOOK_v1_0_0"

# Git binding
git_tag: "playbook-v1.0.0"        # Annotated tag pointing at the merge commit
commit_sha: "abc123def456..."     # Full 40-char SHA of the merge commit
branch_authored: "playbook/v1.0.0-inaugural"  # Branch used for the amendment

# Substrate
repository_path: "docs/ENGINEERING_PLAYBOOK.md"
canonical_authority: "repo_canonical"    # Per KFI-2 B3 derivation
evidence_index: "docs/research/playbook/evidence_index_v1_0_0.md"

# Optional but recommended
content_hash: "sha256:81ff5547aa86..."   # SHA-256 of the file body excluding frontmatter, populated post-Cycle-2 hardening (R7)
last_regen_at: "2026-07-XX 12:00:00Z"    # Autogen block last-refreshed timestamp
schema_version: "1"                       # Schema version for the frontmatter itself
---
```

### 5.2 Field-by-field rationale

**`title`** — human-readable. Rarely changes; changes require MAJOR bump.

**`scope`** — declares the constitutional layer. For this Playbook, always `"platform (L2)"`. If a future Cycle 3+ adds tenant-scope playbooks, the same schema is reused with `scope: "tenant (L3)"`.

**`version` / `version_status`** — the running-state fields. `draft`/`signing`/`correction` are pre-ratification; `ratified` is the terminal state; `superseded` is set on prior versions when a new one is ratified.

**`parent_version` / `supersedes`** — supersession chain. `parent_version` is the immediate predecessor; `supersedes` is the (typically 1-item) list of versions this one replaces. `null` `parent_version` marks the inaugural version.

**`compatible_with`** — a structured statement of *which other constitutional artifacts this Playbook version acknowledges as still-in-force*. If a future Playbook version supersedes some ADRs, this list is updated.

**`ratified_date` / `ratifier` / `ratification_directive`** — the governance envelope. `ratification_directive` is the verbatim ratifier statement (per PIC-10 provenance requirement).

**`ratification_record`** — workspace pointer to the full envelope. `workspace_id` + `deliverable_id` + `title`. The workspace ratification record body carries the extended evidence and provenance classification; the frontmatter just points at it.

**`git_tag` / `commit_sha` / `branch_authored`** — the git binding. `git_tag` is the annotated tag. `commit_sha` is the exact merge commit. `branch_authored` is provenance for the amendment provenance chain.

**`repository_path`** — self-reference for cascade discovery.

**`canonical_authority`** — always `"repo_canonical"` for this Playbook (per 2711). Included explicitly so retrieval tooling doesn't have to re-derive.

**`evidence_index`** — pointer to the sidecar evidence index. This is a separate `.md` file per §11.

**`content_hash` (optional today, mandatory post-Cycle-2)** — SHA-256 of the file body excluding frontmatter. Populated post-ratification. Verifies immutability on retrieval.

**`last_regen_at`** — timestamp of last autogen-section refresh. Non-content field; refreshed by cascade automation.

**`schema_version`** — schema versioning for the frontmatter itself. Prevents Playbook schema evolution from being confused with content evolution.

### 5.3 Frontmatter validation

`verify_repo_guardrails.py` (or a new dedicated script) should validate:

1. All required fields present.
2. `version` matches semver regex.
3. `git_tag` matches `playbook-v<version>` pattern.
4. `commit_sha` is a valid 40-char hex.
5. `ratification_record.workspace_id` and `.deliverable_id` are valid UUIDs.
6. If `version_status='ratified'`, `content_hash` is present (post-Cycle-2 hardening).
7. If `version_status='ratified'`, `parent_version` is either null (inaugural) or a prior ratified version present in Appendix D.
8. `canonical_authority` is `"repo_canonical"`.
9. `scope` is a member of the declared enum.
10. `compatible_with.cycle_1a_adrs` includes all currently-ratified Cycle 1A ADRs unless explicitly deprecated.

**These validations should run in CI** as a required check on any PR modifying `docs/ENGINEERING_PLAYBOOK.md`.

### 5.4 Extension policy

The frontmatter schema itself is versioned (`schema_version`). Adding a new field is a schema-MINOR change. Removing or renaming a field is a schema-MAJOR change. Consumers must ignore unknown fields (forward-compat).

---

## 6. Repository placement

### 6.1 The body

```
docs/
  ENGINEERING_PLAYBOOK.md            # THE Playbook body — single canonical file
```

**Rationale:**
- Top-level `docs/` prefix satisfies `_derive_canonical_authority` B3 branch (source == 'imported' AND file_path.startswith('docs/') → repo_canonical). Automatic classification.
- Filename discoverable by casual grep and by any developer opening the repo.
- Path stability: repository_path in the frontmatter matches the literal file location for CI verification.

### 6.2 Evidence indexes

```
docs/research/playbook/
  evidence_index_v0_1_0.md
  evidence_index_v0_5_0.md
  evidence_index_v1_0_0.md
  evidence_index_v1_0_1.md          # PATCH
  evidence_index_v1_1_0.md          # MINOR
  ...
```

**Rationale:**
- Under `docs/research/playbook/` because evidence indexes are supporting research artifacts, not the ratified body itself.
- One index per ratified version — indexes are immutable per version (per §11.3).
- Naming: `evidence_index_v<major>_<minor>_<patch>.md`. Semver-stable ordering.

### 6.3 Amendment proposals

```
docs/research/playbook/proposals/
  proposal_2026XXXX_<slug>.md       # Pre-SIGN draft
```

**Rationale:**
- Amendment proposals live under `proposals/` until SIGN completes.
- After ratification, the proposal is preserved for provenance but is no longer authoritative.
- Naming: date + slug for chronology.

### 6.4 Ratification records

Ratification records live in the workspace (per §14), not in the repo. The repo pointer is `frontmatter.ratification_record.deliverable_id` (a UUID). If future tooling wants a repo-side mirror of ratification records, it can be autogen'd into `docs/research/playbook/ratification_records/` — but the workspace is the source of truth for the envelope.

### 6.5 The CLAUDE.md anchor

`CLAUDE.md` L7 blockquote (per KFI-5) should be extended (as a MINOR change, not part of Playbook v1.0 itself) to include:

```
Engineering Playbook: docs/ENGINEERING_PLAYBOOK.md — currently ratified at playbook-v1.0.0 (workspace ratification record <uuid>). Session-open orientation includes reading Chapter 0.
```

**This is not part of the Playbook itself.** It's a KFI-5 anchor extension.

### 6.6 The docs/INDEX.md autogen entry

`docs/INDEX.md` is autogen'd. When the Playbook is added, it should surface in that index. The autogen script (`build_docs_index`) will handle this automatically because the file lives at `docs/ENGINEERING_PLAYBOOK.md`.

---

## 7. Semantic versioning strategy

Semver semantics for the Playbook track **rule change**, not text volume.

### 7.1 PATCH — X.Y.z

**Triggers PATCH:**

- Typo, grammar, or formatting fix.
- Broken evidence link repair.
- Autogen section refresh (autogen alone should NOT bump PATCH; only if intended).
- Adding a clarifying example that does not introduce a new rule.
- Cross-reference update after a chapter title change elsewhere.

**Does NOT trigger PATCH:**

- Anything that changes what a rule DOES or WHO must follow it.
- Adding a new evidence citation for an existing rule (that's automatically part of the same version's evidence index).

**Backwards compatibility:** PATCH is 100% backwards-compatible. A Claude session running against v1.0.5 rules should get identical behavior to one running against v1.0.0 for any rule shared between them.

**Ratification burden:** LIGHT. PATCH still requires ratifier directive (Chris) and workspace ratification record, but the SIGN cycle can be lightweight — typically a single-batch review.

### 7.2 MINOR — X.y.0

**Triggers MINOR:**

- Adding a new chapter to a reserved slot (per §3.1).
- Adding a new sub-section to an existing chapter that codifies a new rule.
- Extending an existing rule with a new sub-case (e.g., "the 4-step cascade now includes a fifth step for cross-workspace mirror").
- Codifying a new PIC (PIC-11, PIC-12, etc.).
- New autogen section addition.
- Chapter title change (see §3.5 — cross-references break).
- Frontmatter schema-MINOR (new optional field).

**Does NOT trigger MINOR:**

- Removing or replacing a rule (that's MAJOR).
- Reversing a compatibility statement.

**Backwards compatibility:** MINOR is backwards-compatible AT THE RULE LEVEL. A caller writing to v1.0's rules will still get correct behavior against v1.1 — but they may miss new rules.

**Ratification burden:** STANDARD. Full SIGN cycle; single or dual-batch depending on scope.

### 7.3 MAJOR — x.0.0

**Triggers MAJOR:**

- Removing an existing rule.
- Replacing a rule with a different-behavior rule (e.g., "SIGN cycles are now 2-batch instead of 4-batch").
- Reorganizing the chapter structure (chapters renumbered).
- Frontmatter schema-MAJOR (field removal or rename).
- Any change that invalidates prior compatibility statements.

**Backwards compatibility:** MAJOR is NOT backwards-compatible. Prior version's ratification records remain valid for the artifacts they covered; new artifacts must follow new rules.

**Ratification burden:** HEAVY. Full SIGN cycle; likely multi-batch; explicit consideration of transition path; likely a Cycle-open/close event associated.

### 7.4 v0.y.z pre-release strategy

Playbook versions v0.y.z (pre-ratification of v1.0.0) follow the same semver rules with reduced ratification burden. Every v0.y.z is a formally-published draft.

- **v0.1.0** — inaugural draft. Chapter 0-2 present; other chapters may be stubs.
- **v0.2.0 through v0.9.0** — evolutionary drafts.
- **v0.9.z** — release candidate stage.
- **v1.0.0** — first officially-ratified stable version.

**Amendment burden during v0.y.z:** lighter. SIGN can be single-batch. Chris can compress the ratification cycle. Once v1.0.0 lands, full ratification discipline applies.

### 7.5 Version bump determination

Every amendment PR must include a **version bump justification** in its description:

```
## Playbook version bump
- Current: v1.0.0
- Proposed: v1.1.0 (MINOR)
- Rationale: adds Chapter 11 "Cross-workspace federation methodology" (new chapter, previously reserved slot)
- Diff class: additive; no rule removal; backwards-compatible
- Compatibility statement change: adds fleet:0 acknowledgment
```

**verify_repo_guardrails.py should reject PRs missing this justification.**

### 7.6 The "no-bump" special case

Some changes to `docs/ENGINEERING_PLAYBOOK.md` should NOT bump the version:

- `last_regen_at` timestamp refreshes from autogen cascade.
- Trivial evidence-index sidecar link updates when only the sidecar's own version tag changes.

These are handled by a `[playbook-nobump]` PR title marker. CI validates that only the specified no-bump fields are modified.

---

## 8. Ratification lifecycle

The lifecycle from proposal to ratified is 6 stages. Each stage has entry criteria, exit criteria, and role assignment.

### 8.1 Stage 1 — Propose

- **Trigger:** Chris directive OR Claude/Rigby proposal via workspace deliverable.
- **Role:** Ratifier (Chris) OR Author.
- **Artifact:** proposal deliverable in workspace with `status='draft'`, or a proposal file in `docs/research/playbook/proposals/`.
- **Entry criteria:** none.
- **Exit criteria:** proposal is written, evidence-cited per §11, and Chris has acknowledged.

### 8.2 Stage 2 — Author

- **Trigger:** Chris's directive on the proposal.
- **Role:** Author (Claude).
- **Artifact:** amendment PR on branch `playbook/vX.Y.Z-<slug>` modifying `docs/ENGINEERING_PLAYBOOK.md` with the amendment applied. Evidence sidecar drafted or updated.
- **Entry criteria:** approved proposal from Stage 1.
- **Exit criteria:** PR is committed, evidence index is drafted for the target version, frontmatter is provisional (version_status: signing).

### 8.3 Stage 3 — SIGN

- **Trigger:** Chris directive: "begin SIGN Phase N for playbook amendment".
- **Role:** Reviewer (Rigby); Author (Claude) supports.
- **Artifact:** SIGN report — findings classified per PIC-10 (BLOCKING / non-BLOCKING / recommended edits).
- **Entry criteria:** Authored PR from Stage 2.
- **Exit criteria:** SIGN report returns SIGN-WITH-EDITS, SIGN, or F-BLOCKING classification.

### 8.4 Stage 4 — Correct (conditional)

- **Trigger:** SIGN findings that are BLOCKING or F-BLOCKING; Chris directive to correct.
- **Role:** Author (Claude); Chris makes correction-priority calls.
- **Artifact:** correction pass PR (usually the same PR from Stage 2, updated).
- **Entry criteria:** SIGN findings.
- **Exit criteria:** all BLOCKING findings resolved; frontmatter `version_status: correction` if mid-cycle, else `signing` or advance.
- **Note:** repeat SIGN if the correction is substantial.

### 8.5 Stage 5 — Ratify

- **Trigger:** SIGN passes; Chris directive: "ratification authorized".
- **Role:** Ratifier (Chris) via verbatim directive; Author (Claude) executes the mechanics.
- **Artifact:**
  1. Merge PR to `main` (produces new commit SHA).
  2. Create annotated git tag `playbook-vX.Y.Z` pointing at merge commit; tag message includes ratification record UUID (to be filled after step 3).
  3. Create workspace ratification record deliverable (per §14).
  4. Update Playbook frontmatter: `version_status: ratified`, `commit_sha`, `git_tag`, `ratification_record.*`, `ratified_date`, `ratifier`, `ratification_directive`. This is a post-tag commit — see §8.6 for the handling.
- **Entry criteria:** SIGN passes; Chris ratifies.
- **Exit criteria:** git tag exists; workspace ratification record `status=completed`; frontmatter fully populated.

### 8.6 Stage 6 — Mirror

- **Trigger:** Ratification complete.
- **Role:** Cascade automation.
- **Artifact:**
  1. Run 4-step docs cascade (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `sync_docs_index_to_documents --embed`).
  2. Verify `content.Document(source_reference='docs/ENGINEERING_PLAYBOOK.md')` exists with `canonical_authority='repo_canonical'`.
  3. Regenerate CLAUDE.md L7 blockquote (if it references the Playbook version).
  4. Update `docs/INDEX.md` (autogen — happens as part of cascade step 1).
  5. Refresh 00-START-NEXT-SESSION.md.
- **Entry criteria:** Stage 5 complete.
- **Exit criteria:** RAG has the ratified content; anchors reference the new version; session-open orientation carries it.

### 8.7 The bootstrap paradox — v1.0's own ratification

Playbook v1.0 codifies rules that include how the Playbook itself is ratified. But those rules must be applied to v1.0's own ratification.

**Resolution:** v0.9 is drafted using pre-v1.0 methodology (i.e., existing Cycle 1A discipline). v0.9 → v1.0 promotion uses the v0.9 methodology to ratify v1.0 (which will then codify the methodology going forward). The bootstrap is handled by using the *prior* Playbook version to ratify the *next*, seeded with pre-Playbook Cycle 1A discipline for the very first cycle.

**Applied consequence:** every Playbook version ratifies its own successor. The very first version (v1.0) is ratified using the Cycle 1A discipline that produced it.

### 8.8 Frontmatter update after tag creation — the post-ratification commit

Frontmatter fields `commit_sha`, `git_tag`, `ratification_record.*`, `content_hash` cannot be known until AFTER the merge commit and tag are created. This is a chicken-and-egg problem: the frontmatter needs to reference the SHA that includes it.

**Two-step handling:**

1. **Ratification commit** — the merge commit that IS `commit_sha`. Frontmatter has `version_status: signing`, `commit_sha` unset, `git_tag` unset.
2. **Post-ratification commit** (small follow-up PR) — updates frontmatter to `version_status: ratified` and fills the deferred fields (`commit_sha`, `git_tag`, `ratification_record.*`, `content_hash`). This commit is tagged `playbook-vX.Y.Z-frontmatter` (or the main tag can be moved — but moving is destructive, so append is preferred).

**Applied consequence:** the ratification tag points at the ratification commit; a follow-up frontmatter commit is separately tagged and referenced from the ratification record for full provenance.

**Alternative considered:** frontmatter can carry `commit_sha_placeholder` at ratification and be updated in a separate no-bump commit. Less clean but simpler operationally. Choice deferred to §17 pressure test discussion.

---

## 9. Update workflow

The end-to-end amendment workflow for post-v1.0 amendments.

### 9.1 Amendment triggers

- Chris directive.
- Claude/Rigby proposal (via workspace deliverable) that Chris ratifies-to-consider.
- Rigby-observed drift (a rule no longer matches practice) reported via ops surface.
- Cascade of a new ADR (some ADRs may imply Playbook amendments).
- Cycle close (some closes may imply Playbook codification of new PICs).

### 9.2 Amendment types

- **Rule addition** — MINOR bump.
- **Rule extension** — MINOR bump.
- **Rule removal or replacement** — MAJOR bump.
- **Text-only fix** — PATCH bump.
- **Structural reorganization** — MAJOR bump.

### 9.3 Standard amendment workflow

1. **Propose:** author a proposal deliverable in workspace OR a proposal file. Include: motivation, scope, evidence citations, proposed version bump.
2. **Approve to author:** Chris directive.
3. **Branch:** `git checkout -b playbook/vX.Y.Z-<slug>` off `main`.
4. **Author:** edit `docs/ENGINEERING_PLAYBOOK.md`. Update evidence index sidecar. Update frontmatter fields settable pre-tag.
5. **PR:** open PR with Playbook version bump justification (§7.5).
6. **SIGN:** dispatch to Rigby (per Chapter 5 collaboration protocol).
7. **Correct:** iterate correction passes until SIGN passes.
8. **Chris ratifies:** verbatim directive captured in workspace deliverable.
9. **Merge:** merge PR to `main`.
10. **Tag:** annotated `git tag playbook-vX.Y.Z` on merge commit.
11. **Ratification record:** create workspace deliverable per §14.
12. **Frontmatter update:** post-ratification commit filling deferred fields.
13. **Cascade:** 4-step docs cascade + embed.
14. **Anchor refresh:** CLAUDE.md L7 blockquote update; 00-START refresh.

### 9.4 Fast-path for PATCH

For PATCH-only changes (typo, broken link):

- Steps 1, 2 collapse into "PATCH directive" from Chris.
- Step 6 SIGN can be single-batch or waived (Chris discretion).
- Steps 8, 11 preserve provenance but can be combined into a single lightweight ratification record.

**Rationale:** PATCH changes carry no rule change; heavyweight ratification overhead is disproportionate.

### 9.5 Rejected amendment handling

If SIGN rejects an amendment or Chris withholds ratification:

- The branch is preserved (not deleted). Rejected proposals become part of the history.
- The proposal file is moved to `docs/research/playbook/proposals/rejected/`.
- Future amendments can reference the rejection for provenance.
- Rejected proposals are NOT part of any Playbook version's `supersedes` list.

### 9.6 Emergency amendment

**No fast-path for MAJOR amendments.** If a serious platform issue requires immediate rule change, the normal workflow applies. Temporary policy can be posted to CLAUDE.md or MEMORY.md as an operational directive (L2 documentary; NOT the Playbook itself) while the Playbook amendment goes through normal ratification.

**Applied consequence:** the Playbook is stable by design. Fast-path policy changes belong in operational documentation, not the constitutional Playbook.

---

## 10. Supersession model

Versions relate via a chain. Multiple mechanisms record the relation.

### 10.1 Chain mechanisms

| Mechanism | Location | Direction | Purpose |
|---|---|---|---|
| `parent_version` frontmatter field | Playbook body | Points backward | Immediate predecessor |
| `supersedes` frontmatter field | Playbook body | Points backward | Explicit list of versions replaced |
| Workspace ratification record `parent_object_id` | Workspace deliverable | Points backward | Ratification-record chain |
| Git tag chain | Git | Forward-reachable via tag order | Substrate immutability |
| Appendix D "Prior-version change log" | Playbook body (autogen) | Table of all versions | Reader-facing chain |

### 10.2 What "supersedes" means

- The new version's rules take effect immediately upon ratification.
- The prior version's ratification record remains valid (immutable).
- Prior version's rules are NOT invalidated for artifacts they governed at the time (retroactively applied rules would break Cycle 1A ratifications).
- Prior versions of `docs/ENGINEERING_PLAYBOOK.md` remain accessible via git tags.

### 10.3 Retroactive vs prospective rule application

**Rule of thumb:** rule changes are prospective by default (apply to future artifacts). Retroactive application requires explicit statement in the ratification directive.

**Applied consequence:** a ratified ADR authored under Playbook v1.0 remains valid even if Playbook v2.0 removes the rule that authorized it. Retroactive invalidation is a separate governance act.

### 10.4 The `superseded` frontmatter status

Once a Playbook version is superseded:

- The old file's frontmatter (via a post-supersession commit) is updated: `version_status: superseded`.
- `superseded_by: X.Y.Z` field is added (schema-MINOR field).
- The old file itself is NOT deleted; git history preserves it.
- RAG's `canonical_authority` for the old version is set to `derived` (deprecated) via a cascade step.

**Applied consequence:** RAG retrieval for the Playbook naturally returns the current version (highest weight); superseded versions are still findable but demoted.

### 10.5 Long-range chain integrity

Every 5th or 10th ratification cycle should include a **chain integrity audit** — verify:

- All prior-version frontmatter has `version_status: superseded` (not accidentally still `ratified`).
- All git tags exist.
- All workspace ratification records exist.
- Appendix D reflects all versions.
- No orphaned `parent_version` references.

Cadence: Cycle-level (every arc close).

---

## 11. Evidence and traceability model

Every normative claim in the Playbook must be traceable to primary evidence. The evidence model is what makes the Playbook a *constitutional* artifact rather than an *opinion* document.

### 11.1 Six evidence classes

Every citation in the Playbook must be one of:

| Class | Definition | Example citation form |
|---|---|---|
| **E1 — ADR** | Ratified workspace-canonical ADR authorizing a platform-substrate decision | `ADR-0140 §2.1` |
| **E2 — Ratification record** | Workspace ratification record naming a specific decision act | `RATIFICATION_20260707_0140 (deliverable c883ebef-…)` |
| **E3 — Research doc** | Ratified or WIP research document under `docs/research/` | `docs/research/platform/platform_constitutional_architecture.md §5.9` |
| **E4 — Runtime evidence** | Observable behavior in production data (Postgres queries, DB counts, log signatures) | `SELECT count(*) FROM core_projectworkspace WHERE is_active=true` → 2 rows |
| **E5 — Platform evidence** | Code path, migration, or config file demonstrating implementation | `core/rag_integration.py:30-34 (_AUTHORITY_WEIGHTS)` |
| **E6 — Session handoff** | Ratified session handoff from `docs/handoffs/` | `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md §5` |

### 11.2 Citation discipline

Every rule stated in the Playbook cites at least one evidence source. Multi-source citations are preferred. Citation is inline: `[E1: ADR-0140 §2.1; E5: core/tasks.py:refresh_doc_inventory_blocks]`.

**Where no evidence exists** (a rule about a not-yet-observed pattern): the rule is NOT Playbook-ready. It stays in a WIP research doc or a proposal file until evidence catches up.

**Applied consequence:** the Playbook cannot codify prospective wishlist rules. Only rules that reflect observed practice.

### 11.3 Evidence index sidecar

Each Playbook version has an evidence index sidecar (`docs/research/playbook/evidence_index_v<X_Y_Z>.md`) that enumerates every citation used in the Playbook body. Structure:

```markdown
# Playbook v1.0.0 Evidence Index

## E1 — ADRs cited
- ADR-0110 — Deliverable→Document mirror; cited in Chapter 4 §4.2
- ADR-0120 — canonical_authority attribute; cited in Chapter 1 §1.3, Chapter 4 §4.3
- ...

## E2 — Ratification records cited
- RATIFICATION_20260707_0110 (c883ebef-…); cited in Chapter 6 §6.1
- ...

## E3 — Research docs cited
- docs/research/platform/platform_constitutional_architecture.md §5.9; cited in Chapter 1
- ...

## E4 — Runtime evidence
- SELECT count(*) FROM core_projectworkspace ... (as of commit 309f85ee, 2026-07-08); cited in Chapter 4 §4.2
- ...

## E5 — Platform evidence
- core/rag_integration.py:30-34 (as of commit 309f85ee); cited in Chapter 1
- ...

## E6 — Session handoffs cited
- SESSION_2707_0199_RATIFICATION_HANDOFF.md §5; cited in Chapter 9 §9.1
- ...
```

**Immutability:** the evidence index for version X.Y.Z is created at ratification and frozen. Future versions have their own indexes. This ensures the citations behind ratified rules remain audit-verifiable.

### 11.4 Evidence-index drift check

A Cycle 2 tool should verify (at cascade time):

1. Every citation in the Playbook body resolves to a source that still exists.
2. Every citation's referenced section/line still exists (structural drift).
3. Every citation's substance is still present (semantic drift is harder — Rigby-mediated SIGN can catch this).

**Applied consequence:** Cycle 2 tooling can automate structural evidence-index verification. Semantic verification remains a SIGN-cycle responsibility.

### 11.5 The provenance classification appendix

Chapter 6 (Provenance classification standard, PIC-10) codifies:

- Verified primary evidence (E4, E5).
- Verified repository/runtime fact (E5, E6).
- Verified quoted source (E1, E2, E3, E6).
- Historical reconstruction (E6, E3).
- Engineering conclusion (must be labeled explicitly; not preferred).

Every ratification record and Playbook citation must classify statements. The evidence index also classifies each citation.

---

## 12. Source mapping strategy

Per the mission: every chapter identifies **Required ADRs / Ratification Records / Research / Runtime Evidence / Platform Evidence**. Source mapping is a per-chapter table in Appendix C.

### 12.1 Per-chapter source requirements

| Ch. | Required ADRs | Required Ratification Records | Required Research | Required Runtime | Required Platform |
|---|---|---|---|---|---|
| 0 Preamble | — | — | This spec | — | — |
| 1 Constitutional context | 0000, 0005, 0010, 0100, 0110, 0120, 0130, 0140, 0150, 0199 | All corresponding ratification records | 2708, 2709, 2710, 2711 | Layer census (ORM) | Deliverable model schema |
| 2 Research methodology | 0000, 0010 | RATIFICATION_20260707_0010 | 0000_RAR_METHODOLOGY body | SIGN session count | `content_tool.content_complete` code |
| 3 Implementation discipline | 0110-0150 | Corresponding | 2711 §11 (evidence) | Cycle 1A code merges (git log) | Cycle 1A ADR code paths |
| 4 Documentation cascade | 0110, 0140 | 0110, 0140 | feedback_docs_pipeline_4_step_cascade.md | Document mirror row count | `build_docs_index`, `sync_docs_index_to_documents`, `embed_documents` |
| 5 PA / Rigby collaboration | — (methodology) | — | feedback_claude_directs_rigby_then_verifies.md | ChatConversation count; workspace attribution | PA tool schema catalog |
| 6 Provenance (PIC-10) | 0199 §11, Appendix D | 0199 ratification record | 2711 §11 | Provenance metadata on Deliverable | `Deliverable.metadata` JSONField |
| 7 Session discipline | — | — | 00-START patterns; SESSION handoffs | Session count; cascade PR merges | context-kit skill orientation |
| 8 Runtime discipline | — | — | 2711 §2.4 | CockpitAutopilotPolicy, AgentControlEntry, Budget rows | Their model schemas |
| 9 Recovery playbooks | — | — | feedback_local_celery_stall_playbook.md, feedback_rigby_sign_worker_instability_recovery.md | SESSION incident handoffs | Worker + celery config |
| 10 Evolution & amendment | 0120 (canonical_authority framing) | This Playbook version's ratification record (self-reference) | This spec | Version chain history | Frontmatter validation script |

### 12.2 Source mapping enforcement

`verify_repo_guardrails.py` (or dedicated `verify_playbook_evidence.py`) should check:

- Every chapter has an evidence anchor in its frontmatter pointing to a section of the evidence index.
- Every evidence-anchor section in the index has ≥1 citation.
- Every citation resolves to a live source.

### 12.3 Source coverage completeness

Playbook v1.0 aims for coverage of Cycle 0 + Cycle 1A methodology. Later versions extend to newer cycles.

**Missing source scenarios:**

- If a Chapter requires an ADR that doesn't exist yet, the chapter is a stub with a "PENDING" marker.
- If a Chapter cites a research doc that hasn't been ratified, the citation notes "WIP" status.

**Applied consequence:** the Playbook can ship v0.1 with stub chapters (evidence-gaps explicitly flagged). Stubs are converted to full chapters via MINOR amendments as evidence accumulates.

---

## 13. Git integration

Git is the substrate for L2 constitutional artifacts. The Playbook exercises git carefully.

### 13.1 Branch model

- **`main`** — the canonical branch. All ratified Playbook versions are reachable from `main` via tags.
- **`playbook/vX.Y.Z-<slug>`** — amendment branches. Format: `playbook/<target-version>-<short-slug>`. Example: `playbook/v1.1.0-cross-workspace-mirror`.
- **`playbook/proposal-<slug>`** — pre-authored proposal branches. Rare — usually proposals live in `docs/research/playbook/proposals/` on `main`.
- **`playbook/rejected/vX.Y.Z-<slug>`** — preserved-for-history rejected amendments. Never merged.

### 13.2 Merge policy

- **Amendment PRs merge to `main` via squash-and-merge** (single commit for clean SHA-per-ratification).
- **Post-ratification frontmatter commits merge to `main` via regular merge** (no squash needed).
- **No force-push to `main`, ever.**
- **No rebase of `main`** (destroys ratification SHAs).

### 13.3 Tag policy

- **All ratified versions get an annotated tag** `playbook-vX.Y.Z`.
- **Tag messages include** the ratification record UUID: `Ratified by Chris on 2026-07-XX. Ratification record: <uuid>.`.
- **Tags are never moved or deleted.**
- **Tag signing** (GPG) is optional today; recommended once Chris has GPG signing set up (Cycle 3+).

### 13.4 Special tags for post-ratification updates

- **`playbook-vX.Y.Z-frontmatter`** — post-ratification frontmatter fill (§8.6). Points at the follow-up commit.
- **`playbook-vX.Y.Z-supersession`** — commit that marks a prior version's status as `superseded` when a new version is ratified. Points at the follow-up commit modifying the prior file's frontmatter.

### 13.5 History integrity

The Playbook's history is auditable via `git log docs/ENGINEERING_PLAYBOOK.md`. Every change should be attributable:

- To a ratification act (amendment).
- To a post-ratification frontmatter fill.
- To a supersession status update.
- To a `[playbook-nobump]` autogen refresh.
- To a security or hosting infrastructure change.

**Applied consequence:** any commit modifying `docs/ENGINEERING_PLAYBOOK.md` without matching one of the above five patterns is a discipline violation. CI can enforce this.

### 13.6 Pre-commit guardrails

A Cycle 2 pre-commit hook (or CI check) should:

1. Reject commits to `docs/ENGINEERING_PLAYBOOK.md` on `main` without an accompanying tag (except post-ratification frontmatter commits).
2. Validate frontmatter YAML syntactically.
3. Validate frontmatter semantically (per §5.3 rules).
4. Verify `git_tag` frontmatter matches an actual annotated tag (if `version_status: ratified`).
5. Reject deletion of any prior-version tag.

---

## 14. Workspace ratification envelope specification

Every ratified Playbook version has a corresponding workspace ratification record. This is the governance envelope.

### 14.1 Deliverable properties

```python
Deliverable(
    id=<uuid-generated>,
    workspace_id="a9a16593-e0a4-44dc-8256-efc65d524b3c",  # Architecture & Research
    title="RATIFICATION_20260XXX_PLAYBOOK_v1_0_0",
    deliverable_type="ratification_record",  # NOT "document" — enforce correct type
    category="governance",
    status="completed",  # PublishGate; must transition via content_tool.content_complete
    content=<envelope body — see §14.2>,
    metadata={
        "playbook_version": "1.0.0",
        "git_tag": "playbook-v1.0.0",
        "commit_sha": "abc123def456...",
        "parent_ratification_record_id": null,  # First version's record
        "provenance_classification": "verified primary evidence",  # Per PIC-10
    },
    parent_object_type="deliverable",
    parent_object_id=null,  # First version — no parent record
    content_hash=<sha256-of-body-post-Cycle-2>,  # Populated when Cycle 2 hardening lands
    user_id=<chris-user-id>,
    trace_id=<uuid-of-session-ratifying>,
)
```

### 14.2 Envelope body structure

The envelope body is Markdown. Structure:

```markdown
# RATIFICATION_20260XXX_PLAYBOOK_v1_0_0

## 1. Identity
- Ratifier: chris
- Date: 2026-07-XX
- Playbook version: 1.0.0 (inaugural)
- Playbook path: docs/ENGINEERING_PLAYBOOK.md
- Git tag: playbook-v1.0.0
- Commit SHA: abc123def456...
- Repository canonical authority: repo_canonical

## 2. Ratification directive (verbatim)
> "…"

## 3. Provenance classification per PIC-10
- The ratification directive: verified quoted source (Chris chat pin <pin-uuid> turn N at <timestamp>)
- The Playbook body: verified repository fact (git tag <tag>, SHA <sha>)
- Compatibility statements: verified primary evidence (via ratification records enumerated below)

## 4. Compatibility acknowledgments
- Cycle 0 ADRs (0000, 0005, 0010, 0020): acknowledged and unchanged
- Cycle 1A ADRs (0110-0150): acknowledged and unchanged
- Cycle Open/Close records (0100, 0199): acknowledged and unchanged
- All prior ratification records: preserved
- Compatible with: <list>

## 5. Supersession (if applicable)
- Supersedes: <prior version, or "none — inaugural">
- Prior ratification record: <uuid, or "none">
- Prior version's status flip to "superseded": commit <sha>, tag <tag>

## 6. Evidence anchor
- Evidence index: docs/research/playbook/evidence_index_v1_0_0.md
- Primary research pack: docs/research/platform/{engineering_playbook_architecture_specification.md, platform_constitutional_architecture.md, platform_architecture_workspace_boundary_analysis.md, workspace_architecture_and_constitution_proposal.md, engineering_playbook_architecture_proposal.md}
- Session provenance: SESSION_2708 through SESSION_271N handoffs

## 7. Post-ratification actions completed
- [ ] Merge commit: <sha>
- [ ] Git tag: playbook-v1.0.0 (annotated)
- [ ] Frontmatter update commit: <sha>
- [ ] Post-ratification tag: playbook-v1.0.0-frontmatter
- [ ] Workspace ratification record: this deliverable
- [ ] Docs cascade completed: <cascade run trace_id>
- [ ] CLAUDE.md L7 refresh: <commit sha>
- [ ] 00-START-NEXT-SESSION refresh: <commit sha>

## 8. Signature / attestation
- Ratifier: chris (via chat pin <pin>)
- Author: Claude Code, session <session-id>
- SIGN cycle: Rigby (pin <pin>), <N> batches, <M> findings
```

### 14.3 Content hash population

Post-Cycle-2 (R7), the `content_hash` field on the ratification record is populated with SHA-256 of the body. This is done at the moment `content_tool.content_complete` fires.

Today: `content_hash` may remain null; the SHA-256 is recorded in the envelope body §7 or a separate handoff for external attestation.

### 14.4 Deletion protection

`Deliverable.workspace=SET_NULL` means the ratification record survives workspace deletion. `Deliverable.user=CASCADE` means it dies with Chris's account deletion.

**This is a known risk.** In multi-tenant / long-lifecycle scenarios (Cycle 3+), the ratification record's persistence should be strengthened. Options for Cycle 3+:

- Add `parent_object_type='playbook_version'` protection.
- Migrate ratification records to a dedicated table with stronger deletion protection.
- Duplicate ratification-record body into git for full redundancy.

For v1.0: current cascade rules accepted; risk documented.

### 14.5 Bidirectional linkage

- Playbook frontmatter → workspace ratification record via `ratification_record.deliverable_id`.
- Workspace ratification record → Playbook version via `metadata.playbook_version` + `metadata.git_tag` + `metadata.commit_sha`.
- Both sides reference each other. If either link is broken, the pair is inconsistent — CI check.

---

## 15. Release process

The end-to-end release process, from proposal to session-open availability.

### 15.1 Checklist form

```
=== Playbook vX.Y.Z release ===

# Pre-authoring
- [ ] Chris directive: propose Playbook amendment (or Chris ratifies-to-consider a proposal)
- [ ] Version bump determined (PATCH/MINOR/MAJOR) with justification
- [ ] Evidence sources identified per §11

# Authoring
- [ ] Amendment branch created: playbook/vX.Y.Z-<slug>
- [ ] Playbook body edited
- [ ] Evidence index sidecar created/updated
- [ ] Frontmatter fields updated (except deferred fields)
- [ ] Cross-references updated (symbolic anchors per §3.5)
- [ ] Autogen sections regenerated

# Review
- [ ] PR opened with version-bump justification
- [ ] CI checks pass (frontmatter validation, evidence check, etc.)
- [ ] SIGN cycle dispatched (Rigby)
- [ ] SIGN report received and classified

# Correction (conditional)
- [ ] Corrections applied per SIGN findings
- [ ] Re-SIGN if substantial correction

# Ratification
- [ ] Chris ratification directive captured verbatim
- [ ] PR merged to main
- [ ] Merge commit SHA recorded
- [ ] Annotated git tag playbook-vX.Y.Z created
- [ ] Workspace ratification record created via ORM (bypasses 6-7kB tool defect)
- [ ] content_tool.content_complete fired on ratification record

# Post-ratification
- [ ] Frontmatter follow-up commit (deferred fields filled)
- [ ] playbook-vX.Y.Z-frontmatter tag created
- [ ] Prior version's frontmatter marked superseded (if applicable)
- [ ] playbook-vX.Y.Z-supersession tag on prior version (if applicable)

# Cascade
- [ ] build_docs_index
- [ ] build_rag_corpus
- [ ] sync_docs_index_to_documents
- [ ] sync_docs_index_to_documents --embed
- [ ] Verify RAG mirror: content.Document with source_reference='docs/ENGINEERING_PLAYBOOK.md' has canonical_authority='repo_canonical'

# Anchor refresh
- [ ] CLAUDE.md L7 blockquote references new version
- [ ] docs/INDEX.md autogen refresh
- [ ] 00-START-NEXT-SESSION.md notes new ratification

# Session provenance
- [ ] Session handoff includes release ledger
- [ ] MEMORY.md rule for any newly-codified pattern

# Sign-off
- [ ] Chris acknowledged release complete
```

### 15.2 Automation opportunities

The checklist is automatable via a `make playbook-release VERSION=1.1.0` target (Cycle 2 candidate). Not built now, but the specification is designed to support automation.

### 15.3 Rollback

If a ratified Playbook version is discovered to be materially defective:

1. **No hard rollback.** The version stays ratified; git tag is not moved.
2. **Errata amendment.** A PATCH amendment adds an errata section acknowledging the defect.
3. **Or MAJOR amendment.** If the defect requires rule change, a MAJOR version supersedes with corrected rules.
4. **Retroactive invalidation** is a Chris directive and is explicit in the new version's ratification record.

**Applied consequence:** ratified is ratified. Errors are corrected forward, not backward.

---

## 16. Extension points — from v0.1 through v2.x

The Playbook must support 20+ ratification cycles without restructuring. Extension points below.

### 16.1 Chapter-level extensibility

- **Reserved chapter slots 11-19** (§3.1) are available for MINOR-added chapters.
- **New chapters take a slot from the reserved pool; no renumbering of existing chapters.**
- **When slot 11 fills** (Playbook v2.x or later), slot 12 opens. When all reserved slots fill, Cycle 3+ evaluates whether to add slots 20-29 (MAJOR bump).

### 16.2 Sub-section extensibility

- **Every chapter's `N.M+1 Extension points` section (§3.2 template)** identifies where new sub-sections can slot.
- **Cross-references use symbolic names** (§3.5), so sub-section insertion is safe.

### 16.3 Frontmatter extensibility

- **Frontmatter schema-MINOR** (adding a new optional field) via `schema_version` field.
- **Frontmatter schema-MAJOR** (removing/renaming) is discouraged and requires MAJOR bump.

### 16.4 Autogen section extensibility

- **New autogen sections** are added between DOC-AUTOGEN markers.
- **Older autogen sections are never removed** without a MAJOR bump.

### 16.5 Evidence-class extensibility

- **New evidence classes (E7+)** can be added with a MINOR bump.
- **Each new class extends** the evidence index sidecar schema.

### 16.6 Supersession chain extensibility

- **`supersedes` can be a multi-item list** — one Playbook version can replace multiple prior versions (rare; happens if a Cycle 2 consolidation collapses several versions).

### 16.7 Version 2.x scenarios

- **v2.0.0** — a MAJOR rule change. Example: SIGN methodology re-designed. Chapter structure may reorganize.
- **v2.1.0 through v2.9.0** — normal MINOR/PATCH cycle.
- **v3.0.0** — multi-tenant activation might drive this. Example: a chapter about tenant-scope Playbook coordination is added; scope enum extended.

### 16.8 What breaks compatibility

Only these changes break compatibility with prior versions:

- Rule removal.
- Rule replacement.
- Frontmatter schema-MAJOR.
- Chapter reorganization.
- Evidence-class removal.

All other changes are backward-compatible and preserve the extension model.

### 16.9 Version 1.0 minimum viable chapter set

To ship v1.0, the following chapters MUST exist as fully-evidence-cited content (not stubs):

- Chapter 0 (Preamble).
- Chapter 1 (Constitutional context).
- Chapter 6 (Provenance classification standard).
- Chapter 10 (Evolution & amendment).

Other chapters (2, 3, 4, 5, 7, 8, 9) can ship as stubs in v0.9, filled in as evidence accumulates in v1.1, v1.2, etc.

**Applied consequence:** v1.0's authoring workload is bounded. Full chapters 0, 1, 6, 10 (~2000-3000 lines) plus stubs for the rest.

---

## 17. Pressure test / falsification

Nine categories per mission. Attacking every dimension.

### 17.1 Versioning problems

**Attack:** semver doesn't map cleanly to rule change. "Adding an example" is neither a rule nor a typo — is it PATCH or MINOR?

**Response:** the specification says PATCH for "adding a clarifying example that does not introduce a new rule" (§7.1). The rule-vs-example test is: "does a downstream consumer's behavior change?" If not → PATCH. Ambiguity is expected and the specification tolerates it (Chris adjudicates in unclear cases via ratification directive).

**Attack:** version bump is manual — Claude/Rigby could get it wrong.

**Response:** §7.5 requires a version bump justification in every PR. `verify_repo_guardrails.py` rejects PRs missing it. Chris reviews as part of ratification.

**Attack:** rapid amendment cycles could exhaust MINOR numbers (v1.99.0 → v2.0.0 forced).

**Response:** semver doesn't cap MINOR at 99. Cycle-close amendment consolidation is a natural rhythm. v1.99 → v2.0 as a natural MAJOR is fine.

**Verdict:** versioning problems survivable.

### 17.2 Governance problems

**Attack:** ratifier is a single point of failure (Chris personally).

**Response:** true; Cycle 3+ delegation is a documented extension point (§4.1). Today: single-Chris ratification. Risk accepted for v1.0.

**Attack:** SIGN cycle could produce SIGN-with-EDITS forever; ratification never happens.

**Response:** SIGN report must classify findings. If findings are all non-blocking, ratification proceeds. If BLOCKING, correction applies. If SIGN is deadlocked, Chris directive breaks it (per Cycle 1A pattern).

**Attack:** ratification directive could be paraphrased instead of verbatim.

**Response:** PIC-10 (Chapter 6) explicitly forbids this. The ratification record schema (§14.2) requires verbatim capture with provenance classification.

**Attack:** ratification record could be created with the wrong `deliverable_type` (per historical drift on 0110/0120/0130).

**Response:** the workspace ratification specification (§14.1) explicitly requires `deliverable_type='ratification_record'`. CI check on the workspace deliverable (Cycle 2 hardening) catches this.

**Verdict:** governance problems addressed.

### 17.3 Repository problems

**Attack:** the file at `docs/ENGINEERING_PLAYBOOK.md` could be force-pushed over.

**Response:** GitHub branch protection on `main` prevents force-push. Additional CI check on any commit modifying the Playbook.

**Attack:** the file could be renamed, breaking `repository_path` frontmatter.

**Response:** `verify_repo_guardrails.py` checks that `frontmatter.repository_path` matches the file's actual path. Rename requires a MAJOR bump.

**Attack:** git tags could be moved or deleted.

**Response:** tag protection settings + CI check. Tag deletion is a discipline violation.

**Attack:** the `docs/` mirror (2,986 repo_canonical Documents) might miss the Playbook if the cascade fails.

**Response:** cascade PR discipline (per feedback_cascade_pr_must_include_embed_step) requires the embed step. Session-close cascade sweep catches drift.

**Verdict:** repository problems addressed.

### 17.4 Ratification weaknesses

**Attack:** ratification is currently policy-based, not ORM-enforced.

**Response:** Cycle 2 R7 hardening (add ORM signal to block `save()` on `status=completed` Deliverable). Playbook v1.0 codifies this as a Cycle 2 target.

**Attack:** content_hash is not populated on most ratification records today.

**Response:** Cycle 2 R7 hardening; Playbook v1.0's ratification record IS the first place to populate content_hash by default.

**Attack:** the workspace ratification record could be deleted or edited by anyone with ORM access.

**Response:** Django admin access is restricted. Cycle 2 could add signals to lock immutable rows.

**Attack:** the ratification directive could be forged (Claude claims Chris said something he didn't).

**Response:** the directive is captured in a Rigby chat pin (a ChatConversation row). If the pin is recoverable (per 2707 §4 — Chris's KFI-4 reconciliation was NOT recoverable, driving PIC-10), the directive is verifiable. If not recoverable, the ratification record uses provenance-honest attribution ("engineering rationale recorded during authoring rather than a provenance-guaranteed verbatim quotation" — per 2707 §4 pattern).

**Verdict:** ratification weaknesses acknowledged; Cycle 2 hardening addresses.

### 17.5 Future scaling issues

**Attack:** v5.0 Playbook body could exceed 10k lines and be unwieldy.

**Response:** §3 supports per-file chapter split (`docs/playbook/chapter_XX_*.md`) via `@include` mechanism (Cycle 3+ extension). Playbook v1.0 through v2.x expected to fit in single file.

**Attack:** evidence index sidecars could accumulate to hundreds of files.

**Response:** per-version indexes are immutable. Old indexes stay in git; only current index actively updated. RAG cascade only mirrors the current version.

**Attack:** the `supersedes` chain could grow unbounded.

**Response:** `supersedes` is a list of *immediate predecessors* typically (1 item). Chain is walked via `parent_version` field. Full chain is Appendix D. No unbounded list.

**Verdict:** future scaling addressed.

### 17.6 Multi-tenant issues

**Attack:** in a multi-tenant future, tenants may want to customize the Playbook for their own use.

**Response:** the Playbook stays platform-scoped (governs *donkey-betz-the-app*, not tenants). Tenants get their own tenant-scoped playbook (Cycle 3+ scope) using the same specification pattern with `scope: "tenant (L3)"` frontmatter.

**Attack:** ratification record home (Architecture & Research workspace) is chris's user-owned workspace; if chris ever transfers ownership, records don't transfer cleanly.

**Response:** documented as R2 for Cycle 3+ (per 2710). Ratification records for platform-scope Playbook should move to a dedicated table or a system-owned workspace in Cycle 3+.

**Attack:** RAG retrieval for the Playbook could return the wrong tenant's version.

**Response:** for the platform Playbook (only one), this is fine. For future tenant-scope playbooks: `canonical_authority` extension to `tenant_canonical` + workspace_id filtering (per 2711 §12) is a Cycle 3 requirement.

**Verdict:** multi-tenant issues deferred to Cycle 3+; not blocking for v1.0.

### 17.7 Fleet implications

**Attack:** other fleet apps (mentorforge, character-os, signal-studio) may want to consume the Playbook.

**Response:** the Playbook is repo-canonical in donkey-betz. Other apps can subscribe to git tags via cross-repo mirror if they choose. The Playbook remains donkey-betz-authored.

**Attack:** cross-repo research (per feedback_cross_repo_research_federated_rigby) may generate Playbook-relevant insights that require ratification.

**Response:** insights would come through as amendment proposals via normal amendment workflow. The Playbook still is L2 platform-scope; fleet-scope insights inform but don't dictate.

**Verdict:** fleet implications deferred.

### 17.8 Agent implementation issues

**Attack:** Claude at session-open must read the Playbook. That's a large `Read` call.

**Response:** Chapter 0 (Preamble) is ~200 lines and is what session-open reads. Full chapters are consulted on-demand or via RAG. CLAUDE.md L7 anchor points at the Playbook and includes a summary.

**Attack:** Rigby retrieval for Playbook content could be slow if the Playbook is large.

**Response:** RAG retrieval is chunked (per DocumentEmbedding structure). Only relevant chunks retrieved per query. Not slow at v1.0-v2.x sizes.

**Attack:** the `authority_weighted=True` retrieval mode is opt-in. Default retrieval might not weight the Playbook higher.

**Response:** Rigby's retrieval for governance queries should use `authority_weighted=True`. Documented as a rule in Chapter 5.

**Verdict:** agent implementation addressable.

### 17.9 Human workflow issues

**Attack:** Chris shouldn't have to write branch names and PR titles by hand.

**Response:** amendment workflow can be PA-orchestrated (Claude authors on Chris's behalf, per feedback_claude_directs_rigby_then_verifies).

**Attack:** the ratification directive is verbatim — Chris might not want to write formal English every time.

**Response:** Chris's directive can be casual English ("Ratification is authorized, ship it"). The formality is optional. The verbatim requirement is about what's recorded, not how Chris speaks.

**Attack:** the release process (§15) has 30+ checklist items.

**Response:** for PATCH releases, the fast-path (§9.4) collapses most steps. For MINOR/MAJOR, the full checklist reflects real complexity of Cycle 1A + PIC-10 discipline. Automation opportunity (§15.2).

**Verdict:** human workflow addressed.

### 17.10 Summary

All 9 categories survive pressure test with defenses. Three items are deferred to Cycle 2 (content_hash population, ORM immutability enforcement, CI-level frontmatter validation). Three items are deferred to Cycle 3+ (delegation, per-tenant playbook, cross-repo consumption). None block v1.0 authoring.

---

## 18. Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Playbook v0.1 authoring exceeds scope; team tries to codify prospective rules (rule-not-yet-observed) | Med | §11.2 discipline: cite-or-omit; use stubs in v0.1 for gaps |
| R2 | Ratification bootstrap paradox (v1.0 codifies its own ratification rules) | Low | §8.7 explicit resolution |
| R3 | Post-ratification frontmatter fill introduces a second commit that could be forgotten | Med | §15.1 checklist explicit step; CI check for `version_status: ratified` requiring populated deferred fields |
| R4 | Chapter renaming breaks cross-references | Med | §3.5 symbolic anchors; MINOR bump for title changes |
| R5 | Autogen section drift (last_regen_at not refreshed) | Low | Cascade automation refresh at every session close |
| R6 | Rigby SIGN worker instability during Playbook SIGN | Med | Chapter 9 recovery playbook covers this; §17.4 fall-back to parent-Claude verifier-loop |
| R7 | Frontmatter schema evolution without `schema_version` bump | Low | CI check on schema_version increment |
| R8 | Prior-version frontmatter not marked `superseded` when new version ratifies | Med | Post-ratification checklist; Cycle 2 automation |
| R9 | Evidence index sidecar becomes stale | Low | Per-version index is immutable; drift check catches structural mismatch |
| R10 | `verify_repo_guardrails.py` may not exist or may not be extended to Playbook | Med | Cycle 2 tooling; not blocking for v0.1/v0.9 |
| R11 | Playbook could be edited on `main` without a PR (direct commit) | Med | GitHub branch protection + CI check |
| R12 | The workspace ratification record's home workspace could be renamed or deleted | Med | 2710 R2 acknowledged; Cycle 3+ hardening; interim: pin workspace name in specification |
| R13 | Multi-tenant future may want to fork the Playbook per tenant, contradicting the "platform-scope" framing | Low | Chapter 1 constitutional context makes scope explicit; tenant-scope playbooks are separate artifacts |
| R14 | Version bump justification could be gamed (Claude/Chris say MINOR when it's actually MAJOR) | Low | SIGN cycle should catch this; version-bump discipline is Chapter 10 content |
| R15 | RAG mirror could contain both current and superseded versions with `canonical_authority='repo_canonical'` | Med | Cascade step 4 must set superseded versions to `canonical_authority='derived'` |

---

## 19. Unknowns

| # | Unknown | Why it matters | How to resolve |
|---|---|---|---|
| U1 | Whether `verify_repo_guardrails.py` currently exists or is planned | Frontmatter validation depends on it | Grep the codebase; Cycle 2 tooling |
| U2 | Whether GitHub branch protection is enabled on `main` today | Force-push risk | Check repo settings via `gh api` |
| U3 | Whether annotated git tags are used elsewhere in the repo for versioning | Consistency with existing patterns | `git tag -l` and inspect |
| U4 | Whether the workspace's `governance_mode` field will be populated by Cycle 2 | If populated, "constitutional" workspaces can be discovered | Chris directive |
| U5 | Whether `deliverable_type='ratification_record'` is enum-declared or free string | Historical drift risk | Grep model definition |
| U6 | Whether `content_tool.content_complete` currently populates `content_hash` | R7 acknowledgment: probably not | Read PublishGate source |
| U7 | Whether `deliverable_tool.append` handles frontmatter YAML cleanly | Amendment tool workflow depends on it | Test in a sandbox workspace |
| U8 | Whether Chris wants v0.1 to include stubs for chapters 2-9 or just chapters 0, 1, 6, 10 | Authoring scope for Session 2713+ | Chris directive |
| U9 | Whether the "cascade PR includes embed step" discipline is CI-enforced or manual | Ratification cascade reliability | Grep CI config |
| U10 | Whether existing cascade automation handles new autogen sections in the Playbook automatically | Cascade completeness | Read `refresh_doc_inventory_blocks` |
| U11 | Whether `docs/research/playbook/` directory should be created before v0.1 authoring or lazily during | Directory hygiene | Non-blocking; can be created at first use |

---

## 20. Recommendation

### 20.1 Adopt this specification as the architectural foundation for Engineering Playbook v0.1

Every downstream Playbook authoring session (2713 and beyond) should reference this specification for:

- Chapter structure (§3).
- Frontmatter schema (§5).
- Semver strategy (§7).
- Ratification lifecycle (§8).
- Evidence discipline (§11).
- Release process (§15).

### 20.2 Author v0.1 with the minimum viable chapter set

Per §16.9: Chapters 0, 1, 6, 10 are full content. Chapters 2, 3, 4, 5, 7, 8, 9 are stubs with evidence-pending markers.

Rationale: v0.1 establishes the architectural pattern; content fills in through MINOR amendments as evidence catches up.

### 20.3 Ship v0.1 via the existing Cycle 1A workflow

- Draft in workspace with `status=draft`.
- SIGN via Rigby (or lightweight self-review).
- Chris ratification directive.
- Merge, tag, workspace ratification record.
- Cascade.

Use the pre-Playbook Cycle 1A methodology. The Playbook itself codifies the go-forward pattern.

### 20.4 Establish v1.0 target after 3-6 amendments

Ratify v1.0 when:

- All 10 chapters have content (not stubs).
- The frontmatter schema has stabilized.
- The release process has been exercised end-to-end at least twice.

Do NOT rush v1.0. Better to have a stable v0.9 than a fragile v1.0.

### 20.5 Cycle 2 tooling to accompany Playbook

Cycle 2 should deliver (in parallel with Playbook amendments):

- `verify_playbook_evidence.py` (or extend `verify_repo_guardrails.py`).
- ORM signal to enforce `Deliverable(status='completed')` immutability.
- Automation of `content_hash` population at content_complete.
- `make playbook-release VERSION=<v>` release automation.
- CI checks for frontmatter validity, tag correspondence, evidence-index freshness.

### 20.6 Do NOT

- Do NOT author Playbook content in this session. Only the architecture specification.
- Do NOT create workspace deliverables. Ratification records come after v0.1 is drafted.
- Do NOT open new ADRs.
- Do NOT modify existing constitutional artifacts.
- Do NOT rush v1.0 — let it emerge from stable amendment cycles.

---

## 21. Closing

Four sessions of architecture research (2708, 2709, 2710, 2711) converged on the constitutional model. Session 2712 has translated that model into a production-grade specification for the Engineering Playbook subsystem.

**The Playbook, per this specification, is:**

- Single markdown file at `docs/ENGINEERING_PLAYBOOK.md`.
- Repo-canonical body per KFI-2 B3 derivation.
- 10-chapter structure with reserved slots for future growth.
- YAML frontmatter with 12 required fields; machine-readable; CI-verifiable.
- Semver-versioned with rule-change semantics.
- Ratified via workspace-canonical ratification records naming git tag + commit SHA + verbatim Chris directive.
- Evidence-cited at the paragraph level from 6 evidence classes.
- Supports v0.1 through v2.x without restructuring.

**Session 2713 (next): Playbook v0.1 authoring** using this specification as architectural blueprint. Chris ratifies-to-proceed, then Chapter 0 + 1 + 6 + 10 get authored to full content; Chapters 2-9 land as stubs; SIGN + Chris ratification directive + workspace envelope + cascade → v0.1 shipped.

**Estimated authoring effort for v0.1:** 2-4 sessions (Chapter 0 + 1 + 6 + 10 are content-heavy; stubs are lightweight; SIGN adds a session; ratification cycle adds a session).

Every downstream question — how to author, what to cite, how to version, when to ratify — has an answer in this specification. Cross-references are symbolic; the specification survives its own future amendments.

**Repository ends clean.** This document is the sole artifact of Session 2712.

---

_End of Session 2712 Engineering Playbook Architecture Specification. No implementation performed. No workspace deliverables created. No ADRs opened. No Playbook content authored. No existing constitutional artifacts modified. Repository ends clean (this document + four untracked prior proposals only)._

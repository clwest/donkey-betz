---
title: "Donkey Betz Engineering Playbook"
version: "0.3.0"
version_status: ratified
scope: platform
parent_version: "0.2.0"
supersedes: []
compatible_with: ["0.1.0", "0.2.0"]
ratifier: chris
ratified_date: 2026-07-10
ratification_record:
  workspace_id: a9a16593-e0a4-44dc-8256-efc65d524b3c
  deliverable_id: PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION
canonical_authority: repo_canonical
repository_path: docs/ENGINEERING_PLAYBOOK.md
branch_authored: playbook/v0.3.0-cd48-cd49-codification
commit_sha: PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION
content_hash: PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION
git_tag: PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION
schema_version: 1
prior_ratification:
  version: "0.2.0"
  ratified_date: 2026-07-09
  deliverable_id: fbcfcfde-9da9-48b1-8bd8-187885382521
  commit_sha: ab3c88fa1ddc689a3fbe4cb59d13a5f5fb71cb9b
  content_hash: sha256:ae3228d9b9673dec672300b56b2076790b1548d946852fe08f594c3a37b46938
  git_tag: playbook-v0.2.0
authoring_sessions: [2716, 2718, 2719, 2720, 2721, 2736, 2738]
correction_sessions: [2723, 2725, 2727]
audit_sessions: [2722, 2724, 2725, 2727, 2738]
ratification_package_session: 2726
ratification_session: 2727
v0_2_0_authoring_session: 2736
v0_2_0_ratification_session: 2736
v0_3_0_authoring_session: 2738
v0_3_0_ratification_session: 2738
rule_count: 195
rules_added_v0_2_0: [PLAYBOOK-5.2.2, PLAYBOOK-2.2.2, PLAYBOOK-3.2.2]
rules_added_v0_3_0: [PLAYBOOK-6.6.14, PLAYBOOK-6.10.5]
evidence_manifest: docs/research/platform/engineering_playbook_evidence_manifest.md
---

# Donkey Betz Engineering Playbook v0.3.0

# Chapter 0 — Preamble and How to Read This Playbook

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-0
**Purpose:** Orient the reader to the Playbook's role and scope; declare the interpretation of normative language; anchor version metadata visibility.
**Scope:** Meta — this chapter governs the reader experience of the Engineering Playbook itself. It does not codify engineering rules for the platform substrate.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [GR], [DR], [EP]
**Rule ID range:** PLAYBOOK-0.3.1 through PLAYBOOK-0.6.1

---

## 0.1 What this document is

The Engineering Playbook (hereafter "the Playbook") is the platform-level constitutional codification of the engineering methodology by which Donkey Betz is built. It sits at Layer 2 of the six-layer constitutional stack established in Chapter Constitutional Context §The Six-Layer Stack. Its authority derives from the ratification act of the System Owner recorded in the workspace ratification envelope named in the current version's frontmatter.

The Playbook records rules whose existence is demonstrated by ratified prior evidence. Its language is legislative rather than descriptive. Every normative statement in the Playbook cites at least one source in the frozen evidence manifest for the Playbook version being read.

> **Commentary:** The Playbook is authored under the drafting protocol established in Session 2713 (`docs/research/platform/engineering_playbook_authoring_protocol.md`) and consumes the evidence set frozen in Session 2715 (`docs/research/platform/engineering_playbook_evidence_manifest.md`).

## 0.2 What this document is not

The Playbook is not a design proposal. Proposals live in `docs/research/*` and are ratified through the amendment discipline codified in Chapter Evolution and Amendment.

The Playbook is not a tutorial. Tutorial content lives in `docs/guides/` and `docs/topics/*`.

The Playbook is not a reference. Reference material lives in `docs/PLATFORM_INVENTORY.md`, `docs/topics/*`, and the autogen inventories enumerated in `docs/canon/INDEX.md` under Runtime Evidence.

The Playbook is not an operational runbook. Runbook content lives in `docs/handoffs/*` and the cascade automation defined in Chapter Documentation Cascade.

The Playbook is not an implementation plan. Implementation is governed by Architecture Decision Records recorded in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` and in `docs/adr/`.

The Playbook contains rules. It does not contain history except where history is required to anchor a rule; historical statements appear under the `> **History:**` blockquote convention defined in §0.4.

## 0.3 Interpretation of normative language

**[EP] PLAYBOOK-0.3.1** The key words interpreted as normative in the Playbook body are those enumerated in RFC 2119 (Bradner 1997) and BCP 14. They are to be interpreted as described in those referenced documents when, and only when, they appear in all capitals as shown in this Playbook. [E3: 2713 §5.1 — part of the convergent 2708-2714 research chain per manifest §2.3]

> **Commentary:** RFC 2119 keyword usage was already an emerging convention in the repository at the time of this Playbook's inaugural ratification. Session 2713 catalogued 71 uses of these keywords across 15 documents. This rule codifies the emerging convention as constitutional.

**[EP] PLAYBOOK-0.3.2** Every normative sentence in the Playbook body MUST contain exactly one capitalized RFC 2119 keyword. Sentences requiring multiple normative directives MUST be split into separate sentences. [E3: 2713 §5.3 — part of the convergent 2708-2714 research chain]

**[EP] PLAYBOOK-0.3.3** Every normative sentence in the Playbook body MUST carry a statement-class marker (per Chapter Provenance Classification §Statement Classification) and a stable rule identifier (per Chapter Evolution and Amendment §Rule Identifiers). [E3: 2713 §3.1, §6.1, §9.1 — part of the convergent 2708-2714 research chain]

**[EP] PLAYBOOK-0.3.4** Every normative sentence in the Playbook body MUST cite at least one evidence source drawn from the frozen evidence manifest for the Playbook version in force. [E3: 2713 §7.1 — part of the convergent 2708-2714 research chain; E3: 2715 evidence manifest §2.2]

The following table restates the RFC 2119 keyword strengths:

| Keyword group | Interpretation |
|---|---|
| `MUST`, `SHALL`, `REQUIRED` | Absolute requirement. |
| `MUST NOT`, `SHALL NOT` | Absolute prohibition. |
| `SHOULD`, `RECOMMENDED` | Strong recommendation. Deviation is permitted where circumstances warrant, but the deviation MUST be documented with a rationale. |
| `SHOULD NOT`, `NOT RECOMMENDED` | Strong dissuasion. Deviation is permitted with documented rationale. |
| `MAY`, `OPTIONAL` | Truly optional. Neither compliance nor non-compliance carries obligation. |

**[EP] PLAYBOOK-0.3.5** Lowercase occurrences of RFC 2119 keywords in the Playbook body carry ordinary English meaning and MUST NOT be treated as normative. [E3: 2713 §5.4 — part of the convergent 2708-2714 research chain]

> **Example:** *"The evidence index sidecar MUST enumerate every citation used in the chapter body"* is a normative statement. *"Every author must eventually stop editing and commit"* uses lowercase `must` as ordinary emphasis; it carries no constitutional weight.

**[EP] PLAYBOOK-0.3.6** Synonyms for RFC 2119 keywords MUST NOT appear in normative sentences. Prohibited phrasings include `has to`, `is required to`, `is expected to`, `needs to`, `it is essential that`, and `it is important that`. Rewrite each such phrasing using the appropriate RFC 2119 keyword. [E3: 2713 §5.5 — part of the convergent 2708-2714 research chain]

## 0.4 Reading conventions

Normative content appears in bold with a class marker prefix and a rule identifier. Informative content appears as ordinary prose or within one of four blockquote conventions.

**[EP] PLAYBOOK-0.4.1** Informative content within the Playbook body MUST be visually distinguishable from normative content using one of four blockquote prefixes: `> **Commentary:**` for explanation of a rule's purpose; `> **Example:**` for illustrative usage; `> **History:**` for historical context motivating a rule; `> **Future:**` for forward-pointers to possible later work. [E3: 2713 §4.4 — part of the convergent 2708-2714 research chain]

> **Commentary:** These four prefixes are the only visual conventions for informative content. Authors who wish to add a note that does not fit any of these categories MUST elevate the note into a normative rule with an appropriate class marker OR remove it.

**[EP] PLAYBOOK-0.4.2** A single paragraph MUST NOT combine normative and informative content. Paragraphs mixing a rule and a `Commentary:` block MUST be split. [E3: 2713 §4.3]

> **Example:** *"[GR] PLAYBOOK-0.3.1 The key words MUST … are to be interpreted as described in RFC 2119. For example, `MUST` is stronger than `SHOULD`."* mixes a normative rule with an example inside a single paragraph. The example belongs in a separate blockquote below the rule.

## 0.5 Reader intent and reading depth

Different reader intents require different reading depths. The following table records the recommended reading path for common intents.

| Reader intent | Recommended reading |
|---|---|
| Session-open orientation for Claude Code | Chapter 0 in full, plus Chapter 1 §Purpose and Premise |
| Session-open orientation for a human contributor new to the platform | Chapters 0 and 1 in full |
| Authoring or amending the Playbook | Chapter 6 and Chapter 10 in full, with Chapter 1 as context |
| Codifying an implementation decision | Chapter 3 and Chapter 6 |
| Codifying a documentation cascade issue | Chapter 4 |
| Debugging a session-open failure | Chapter 7 and Chapter 9 |

The Playbook is designed to be read in whole by a senior engineering audience at approximately 90 to 120 minutes at v1.0. This v0.1.0 draft is substantially shorter because chapters 2 through 9 are stubs pending later minor amendments.

## 0.6 Version metadata visibility and the reader's contract

**[EP] PLAYBOOK-0.6.1** A reader who acts on Playbook content MUST treat the currently-ratified Playbook version as authoritative and superseded Playbook versions as historical. Retroactive rule application MUST NOT be assumed. [E3: 2712 §10.3 — part of the convergent 2708-2714 research chain]

> **Commentary:** Rule changes are prospective by default. Artifacts ratified under a prior Playbook version remain valid even if the current Playbook version has changed or removed the rules that authorized them at the time of their ratification.

The frontmatter of every ratified Playbook version records the fields specified in the Playbook Architecture Specification (Session 2712 §5.1). Readers determine the current Playbook version, the ratification date, the git tag, and the commit SHA from the frontmatter alone.

> **Example:** A well-formed reference from a session handoff to a specific Playbook rule takes the form `PLAYBOOK-4.2.1 (v1.3.0)`, naming both the rule identifier and the Playbook version in force at the time of the citation.

## 0.7 Cross-references

- Chapter Constitutional Context §The Six-Layer Stack.
- Chapter Provenance Classification §Statement Classification.
- Chapter Evolution and Amendment §Rule Identifiers.
- Chapter Evolution and Amendment §Semver Strategy.
- 2712 `engineering_playbook_architecture_specification.md` — structural blueprint.
- 2713 `engineering_playbook_authoring_protocol.md` — drafting protocol.
- 2715 `engineering_playbook_evidence_manifest.md` — frozen evidence set for this version.

## 0.8 Extension points

- Additional reader intents MAY be added to the reader-intent table under a MINOR amendment.
- Additional prohibited synonyms for RFC 2119 keywords MAY be enumerated under a MINOR amendment when authorship experience reveals new prohibited phrasings.
- The visual conventions for informative content (§0.4.1) are stable through the v1.x line; any change is a MAJOR amendment.

---

# Chapter 1 — Constitutional Context

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-1
**Purpose:** Locate the Engineering Playbook within the platform's six-layer constitutional stack; establish the two orthogonal dimensions of canonicality and ratification; enumerate the pre-existing constitutional ecosystem the Playbook joins; acknowledge Cycle 0 and Cycle 1A ratifications as prior art; state the rule-origin discipline that governs every Playbook rule.
**Scope:** The tiered constitutional authority model as it exists in the platform's code, data, and ratified documents at the time of the Playbook version being read.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [AC], [EP], [GR], [RS]
**Rule ID range:** PLAYBOOK-1.1.1 through PLAYBOOK-1.10.3

---

## 1.1 Purpose and premise

The Engineering Playbook does not create the platform's constitutional architecture. That architecture already exists in the repository, in the runtime, and in ratified workspace deliverables. The Playbook codifies methodology within this pre-existing constitutional context.

**[EP] PLAYBOOK-1.1.1** The Playbook is one of several constitutional artifacts at Layer 2 (Platform) of the platform's constitutional stack. The Playbook MUST NOT be treated as superseding any prior constitutional artifact unless a supersession is explicitly recorded via the mechanism defined in Chapter Evolution and Amendment §Supersession Model. [E3: 2711 §18; E3: 2714 §17.1]

> **Commentary:** Prior sessions in the architectural research chain treated the Playbook's introduction as potentially competing with pre-existing constitutional infrastructure. Session 2714 established that the correct posture is joining and integration rather than competition. This chapter names the pre-existing ecosystem explicitly so that the Playbook's scope of authority is unambiguous.

**[EP] PLAYBOOK-1.1.2** The Playbook's authority is bounded to Layer 2 platform-scope concerns. Rules in the Playbook body MUST NOT purport to govern artifacts at other layers unless the rule explicitly names the layer whose behavior it constrains. [E3: 2710 §5.2; E3: 2711 §18]

## 1.2 The six-layer stack

The platform's constitutional architecture organizes into six vertical layers of authority scope, with Layer 0 reserved for human intent as the origin of all constitutional authority.

**[EP] PLAYBOOK-1.2.1** The platform recognizes six architectural layers of authority scope: Fleet (L1), Platform (L2), Tenant (L3), User (L4), Workspace (L5), and Deliverable (L6). [E3: 2710 §9 — part of the convergent 2708-2714 research chain; E3: 2711 §18 — part of the convergent chain; E4: ORM census at commit 309f85ee 2026-07-08 confirming workspace, tenant, and fleet models exist]

**[EP] PLAYBOOK-1.2.2** Constitutional authority flows downward through the six layers. Higher layers MUST constrain lower layers by inheritance, and lower layers MUST NOT unilaterally override higher-layer authority within the substrate. [E3: 2711 §10.1, §10.3 — part of the convergent 2708-2714 research chain]

**[EP] PLAYBOOK-1.2.3** Ratification envelopes MAY name artifacts at their own layer or at higher layers. A ratification envelope authored at Layer 5 MAY ratify an artifact whose canonical body lives at Layer 2. [E3: 2712 §14 — part of the convergent 2708-2714 research chain; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT (`c883ebef-baa7-43c7-a6f0-dd8f3f22106d`)]

> **Commentary:** The upward-ratification pattern is what makes the Playbook's placement possible. The Playbook body is repository-canonical (Layer 2 substrate), but its ratification envelope lives in workspace `a9a16593-…` (Layer 5). The envelope names the git tag and commit SHA; the workspace's ratification-record model provides the immutability and provenance discipline; the git substrate provides the cryptographic body integrity.

### 1.2.1 Layer 1 — Fleet

Layer 1 is the federation of related applications of which Donkey Betz is one member. The fleet substrate exists in the platform's ORM through the models `FleetServiceIdentity`, `FleetServiceKey`, `FleetServiceRotation`, `FleetAuthAuditLog`, `FleetEvent`, `FleetPAChatAuditRow`, `FleetArtifact`, and `FleetPaidInterest`. The fleet documentary constitution is empty at the time of this Playbook version's ratification.

**[EP] PLAYBOOK-1.2.4** The Engineering Playbook is a Layer 2 (Platform) artifact. It MUST NOT be treated as authoritative for other members of the fleet. [E3: 2710 §5.2 — part of the convergent 2708-2714 research chain; E3: 2714 §16.2 — part of the convergent chain]

> **Future:** A future fleet-level Playbook coordination scheme MAY be introduced when the fleet-scope constitutional layer is activated. Fleet-scope activation is expected in Cycle 4 or later and is not a v0.1 concern.

### 1.2.2 Layer 2 — Platform

Layer 2 is the platform itself: the running application; the git repository; and the runtime infrastructure that operates on the platform's own definition. Constitutional artifacts at Layer 2 govern how the platform is built and operated.

**[EP] PLAYBOOK-1.2.5** Layer 2 constitutional artifacts SHALL include, but are not limited to, the Engineering Playbook, the ratified Architecture Decision Records at `docs/adr/`, the Canon Registry at `docs/canon/INDEX.md`, the System Owner declaration at `docs/governance/SYSTEM_OWNER.md`, the Doc Lifecycle constitution at `docs/00-START-HERE/DOC_LIFECYCLE.md`, the Research Operating System and Implementation Operating System at `docs/research/process/`, and the session-open contracts `CLAUDE.md`, `MEMORY.md`, and `00-START-NEXT-SESSION.md`. [E3: 2714 §2 — part of the convergent 2708-2714 research chain; E5: file existence verified at commit 309f85ee]

### 1.2.3 Layer 3 — Tenant

Layer 3 is the SaaS billing envelope for one or more users. The `Tenant` model exists in the platform's ORM with fields `owner`, `subscription_tier`, `monthly_cost_limit`, `monthly_cost_used`, and `features`. Zero `Tenant` rows exist at the time of this Playbook version's ratification.

**[EP] PLAYBOOK-1.2.6** The Engineering Playbook MUST NOT depend on the Tenant layer being active in production data. Rules pertaining to multi-tenant governance MUST specify Cycle 3 or later applicability. [E4: `Tenant.objects.count()` = 0 at commit 309f85ee — runtime evidence; E3: 2710 §2.2 — part of the convergent 2708-2714 research chain]

### 1.2.4 Layer 4 — User

Layer 4 is the individual user identity, expressed through the `UnifiedUser` model. Nine `UnifiedUser` rows exist at the time of this Playbook version's ratification. User preferences and personal memory are stored at Layer 4 through models such as `UserProfile`, `UserPreferences`, `ConversationMemory`, and `UserAgentLearning`.

**[EP] PLAYBOOK-1.2.7** User preferences at Layer 4 are not typically constitutional. The Engineering Playbook governs Layer 2 concerns and MUST NOT purport to govern individual user preferences. [E3: 2711 §7.5]

### 1.2.5 Layer 5 — Workspace

Layer 5 is the AI-operator workspace scope, expressed through the `ProjectWorkspace` model. Twelve `ProjectWorkspace` rows exist at the time of this Playbook version's ratification. Workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture and Research) hosts the Layer 5 documentary constitution at this time.

**[AC] PLAYBOOK-1.2.8** Layer 5 constitutional artifacts include workspace-scope Architecture Decision Records, workspace ratification records, workspace cycle open and close records, and workspace evidence ledgers. Workspace-scope artifacts are canonicality-classified `workspace_canonical` per the classifier at `content/_canonical_authority_helpers.py`. [E1: workspace ADRs 0110–0150; E2: eight Cycle 1A workspace ratification records; E5: `content/_canonical_authority_helpers.py:33-60`]

### 1.2.6 Layer 6 — Deliverable

Layer 6 is the individual output artifact stored as a `Deliverable` row within a workspace. Deliverables acquire constitutional character through the combination of ratification, a governance-typed `deliverable_type`, and a mirror row in `content.Document`.

**[EP] PLAYBOOK-1.2.9** A Deliverable acquires constitutional character only through the combination of `deliverable_type` in `{adr, cycle_open, cycle_close, ratification_record}`; `status='completed'` reached via the PublishGate transition initiated by `content_tool.content_complete`; and a mirror row in `content.Document` with `canonical_authority` in `{workspace_canonical, repo_canonical}`. [E5: `content_tool.content_complete`; E5: `content/_canonical_authority_helpers.py`; E1: workspace ADRs 0110–0150; E2: eight Cycle 1A workspace ratification records]

> **Commentary:** The three conditions compose. A `deliverable_type='adr'` row that has not reached `status='completed'` is a draft, not a constitutional artifact. A ratified deliverable whose mirror row has `canonical_authority='derived'` retains its ratification act but does not participate in authority-weighted retrieval as a governance source.

## 1.3 The two orthogonal dimensions of constitutional identity

Every constitutional artifact is characterized along two independent dimensions.

**[EP] PLAYBOOK-1.3.1** Canonicality expresses which layer's substrate owns the truth of the artifact. It MUST be recorded as the `canonical_authority` value on the artifact's mirror row in `content.Document`. [E5: `content/_canonical_authority_helpers.py:33-60`; E3: 2711 §3.1 — part of the convergent 2708-2714 research chain]

**[EP] PLAYBOOK-1.3.2** Ratification expresses the act by which a scope's owner has declared the artifact immutable and load-bearing for future work. It MUST be recorded through a workspace ratification-record envelope that names the artifact. [E3: 2711 §3.2 — part of the convergent 2708-2714 research chain; E2: eight Cycle 1A workspace ratification records]

**[EP] PLAYBOOK-1.3.3** An artifact is constitutional when it is both canonical (has an authoritative source layer) and ratified (has a governance envelope). The two dimensions compose orthogonally: an artifact MAY be repo-canonical and workspace-ratified; workspace-canonical and workspace-ratified; or repo-canonical and unratified (in which case it is authoritative for its subject but does not carry ratification-bound immutability). [E3: 2711 §3.3]

> **Example:** The Engineering Playbook body is `repo_canonical` because its authoritative source is the git repository (a Layer 2 substrate). It is ratified through a workspace ratification record that names the git tag and commit SHA. This combination — repository-canonical body plus workspace-canonical ratification envelope — is the pattern established by Session 2710 §14 and confirmed by Session 2714 §17.1 Amendment A.

> **Example:** The five Cycle 1A workspace Architecture Decision Records (0110 through 0150) are `workspace_canonical` because their authoritative source is the workspace deliverable substrate (Layer 5). Each has an accompanying workspace ratification record. This combination — workspace-canonical body plus workspace-canonical ratification envelope — is the pattern established by Cycle 1A KFI-1, KFI-2, and KFI-5.

## 1.4 Canonical authority

The `canonical_authority` field on `content.Document` classifies the authoritative source layer for the mirrored artifact. The classifier and its retrieval integration are both load-bearing.

### 1.4.1 The three-value enumeration

**[AC] PLAYBOOK-1.4.1** The `canonical_authority` enumeration recognizes exactly three values: `workspace_canonical`, `repo_canonical`, and `derived`. [E5: `content/_canonical_authority_helpers.py:33-60`; E1: workspace ADR-0120]

The interpretations are as follows:

| Value | Interpretation |
|---|---|
| `workspace_canonical` | The source of the mirrored artifact is a workspace `Deliverable` row (`source='workspace'`). Authority is workspace-scope. |
| `repo_canonical` | The source is a repository file under the `docs/` prefix (`source='imported'` AND `file_path.startswith('docs/')`). Authority is repository-scope. |
| `derived` | Any other source. Safe under-classification. Applied when the classifier cannot determine an authoritative source. |

**[EP] PLAYBOOK-1.4.2** The `canonical_authority` enumeration MAY be extended in a future Playbook version to accommodate additional constitutional layers (for example, a `tenant_canonical` value when the Tenant layer is activated). Extension is a MAJOR Playbook amendment and requires a coordinated schema migration. [E3: 2711 §12.1, §12.2]

### 1.4.2 Derivation

**[EP] PLAYBOOK-1.4.3** The `canonical_authority` value MUST be derived by the classifier `_derive_canonical_authority` in `content/_canonical_authority_helpers.py`. [E5: `content/_canonical_authority_helpers.py:33-60`; E3: 2713 §7 — part of the convergent 2708-2714 research chain]

The classifier evaluates a four-branch decision tree in order:

1. If `source == 'workspace'`, return `workspace_canonical`.
2. Otherwise, if `extracted_metadata` contains a `workspace_source_uuid` key, return `derived`.
3. Otherwise, if `source == 'imported'` and `file_path` starts with `docs/`, return `repo_canonical`.
4. Otherwise, return `derived`.

**[EP] PLAYBOOK-1.4.4** The derivation MUST remain deterministic and side-effect-free. Callers of the classifier MUST be able to invoke it repeatedly for the same input without observing different results and without triggering signal handlers or writes. [E5: `content/_canonical_authority_helpers.py` module docstring (SIGN-1 F3 disposition note preserving signal-safety contract); E3: 2711 platform_constitutional_architecture.md §2.1 (canonical_authority derivation as deterministic 4-branch decision tree; also §11 line 229 "deterministic classifier") — part of the convergent 2708-2714 research chain per manifest §2.3]

**[EP] PLAYBOOK-1.4.5** Backfill of `canonical_authority` values across the corpus MUST bypass `post_save` signal handlers. [E5: `content/_canonical_authority_helpers.py:63-102`; E3: 2711 §2.1 (canonical_authority derivation code discussion; helpers.py referenced as the enforcement mechanism) — part of the convergent 2708-2714 research chain per manifest §2.3]

**[EP] PLAYBOOK-1.4.5a** Callers implementing backfill MUST use `QuerySet.update()` (or equivalent) rather than per-row `instance.save()`, matching the pattern established by `run_backfill()` in `content/_canonical_authority_helpers.py`. [E5: `content/_canonical_authority_helpers.py:63-102`; E3: 2711 §2.1 (canonical_authority derivation code discussion; deterministic classifier per §11 line 229) — part of the convergent 2708-2714 research chain per manifest §2.3]

> **Commentary:** The signal-safety rule reflects a discovered performance and correctness constraint. Per-row `instance.save()` triggers `update_knowledge_base_stats` on every eligible row, cascading into a full `KnowledgeBase.update_statistics()` recompute per row. At corpus scale this multiplies query count by approximately 4 for the backfill.

### 1.4.3 Retrieval integration

**[AC] PLAYBOOK-1.4.6** Retrieval against the `content.Document` corpus (via `search_embeddings` in `core/rag_integration.py`) MAY accept an authority-weighted mode. When authority-weighted retrieval is active, the weights are `workspace_canonical=2.0`, `repo_canonical=1.5`, and `derived=1.0`. [E5: `core/rag_integration.py:30-34` (`_AUTHORITY_WEIGHTS`); E1: workspace ADR-0130]

**[AC] PLAYBOOK-1.4.7** Retrieval callers MAY filter to a specific `canonical_authority` value. When filtering to `workspace_canonical`, callers MUST also observe the anti-pollution invariant `source='workspace'`. [E5: `core/rag_integration.py:151-184`; E1: workspace ADR-0130]

> **Commentary:** The anti-pollution invariant is a defensive posture. It ensures that a hypothetical mis-classified workspace mirror row (one whose `canonical_authority` was set to `workspace_canonical` but whose `source` is not `workspace`) is not surfaced under the workspace-canonical filter without being source-verified. The redundant filter reflects the SIGN-tested design intent of ADR-0130.

**[EP] PLAYBOOK-1.4.8** Default retrieval (with neither an explicit `canonical_authority` filter nor `authority_weighted=True`) MUST NOT apply the authority weights. [E5: `core/rag_integration.py:63-65`; E3: 2711 §2.1 (explicit statement: "Default retrieval (authority_weighted=False, canonical_authority=None): no weighting, all authorities mixed by cosine similarity alone") — part of the convergent 2708-2714 research chain per manifest §2.3]

> **Commentary:** Opt-in weighting reflects a policy choice made during Cycle 1A: retrieval should surface the closest semantic match by default and elevate authority only when the caller explicitly requests it. Callers building governance-aware queries opt in; callers building general semantic search do not.

## 1.5 The System Owner

Constitutional authority in the platform terminates at a single named human ratifier.

**[RS] PLAYBOOK-1.5.1** The System Owner of the platform is Chris West. The System Owner's authority is defined in `docs/governance/SYSTEM_OWNER.md` and is characterized in that document as "Absolute Override Level." [E5: `docs/governance/SYSTEM_OWNER.md`; E5: `core/services/docs_context_builder.py:184`]

**[EP] PLAYBOOK-1.5.2** No Playbook amendment MAY be ratified without an explicit directive from the System Owner. The directive MUST be preserved verbatim in the amendment's workspace ratification record body. [E3: 2712 §14.2 — part of the convergent 2708-2714 research chain; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification directive verbatim]

**[RS] PLAYBOOK-1.5.3** The `docs/governance/SYSTEM_OWNER.md` document is runtime-load-bearing. The runtime service `core/services/docs_context_builder.py` MUST inject the document into agent context at line 184 with maximum 100 lines at priority 100 via line 365. Renaming, moving, or removing the file MUST NOT be attempted through documentation amendment alone. [E5: `core/services/docs_context_builder.py:184, 365`]

> **Commentary:** The System Owner declaration is not merely a document; it is a constitutional input to every agent execution. Every agent context assembled by `docs_context_builder.py` includes the System Owner declaration in the first hundred lines. Modifications to the file that break either the load path or the content shape have runtime consequences.

**[EP] PLAYBOOK-1.5.4** The System Owner's ratification directive MAY take any form the System Owner chooses (formal or casual English). The obligation MUST be verbatim preservation of the directive text, not the form in which the directive is spoken. [E3: 2712 §17.9 — part of the convergent 2708-2714 research chain]

## 1.6 The pre-existing constitutional ecosystem

At the time of this Playbook version's ratification, the platform hosts a substantial constitutional ecosystem that pre-dates the Engineering Playbook. The Playbook joins this ecosystem; it does not replace it.

### 1.6.1 The Canon Registry

**[RS] PLAYBOOK-1.6.1** The Canon Registry at `docs/canon/INDEX.md` enumerates the platform's promoted Layer 2 canon documents. Promotion criteria are expert-level quality, factual accuracy, production testing, practical utility, and System Owner approval. Every promotion MUST satisfy all five criteria. [E5: `docs/canon/INDEX.md`; E5: `core/services/docs_context_builder.py:186`]

**[RS] PLAYBOOK-1.6.2** The Canon Registry MUST remain intentionally small (approximately ten primary documents at scale). Canon documents live at their original repository paths; the Registry contains pointers, not copies. [E5: `docs/canon/INDEX.md`]

**[EP] PLAYBOOK-1.6.3** The Engineering Playbook v0.1.0 MUST be nominated for Canon Registry inclusion as part of its ratification cascade. [E3: 2714 §17.1 Amendment F — part of the convergent 2708-2714 research chain]

> **Commentary:** Canon Registry inclusion is a lightweight administrative act relative to Playbook ratification itself. It ensures the Playbook is discoverable through the same channel as other operational canon and is injected into agent context alongside the Registry.

### 1.6.2 The Doc Lifecycle constitution

**[RS] PLAYBOOK-1.6.4** The document at `docs/00-START-HERE/DOC_LIFECYCLE.md` is the pre-existing constitutional governance for the `/docs/` corpus. It MUST NOT be duplicated by any subsequent Playbook chapter. [E5: `docs/00-START-HERE/DOC_LIFECYCLE.md`]

**[EP] PLAYBOOK-1.6.5** Chapter Documentation Cascade MUST cite `DOC_LIFECYCLE.md` as prior authority. Extensions to documentation discipline MUST be additive relative to `DOC_LIFECYCLE.md`. [E3: 2714 §17.1 Amendment C — part of the convergent 2708-2714 research chain]

> **Commentary:** PENDING — resolves once Chapter 4 stub-body-file references DOC_LIFECYCLE.md.

> **Commentary:** The Doc Lifecycle constitution already governs the `/docs/` corpus at repository level. The Engineering Playbook Chapter Documentation Cascade extends this governance with the four-step docs cascade and the workspace-mirror discipline established by Cycle 1A KFI-1 and KFI-4. The two documents cooperate; neither replaces the other.

### 1.6.3 The repository Architecture Decision Record corpus

**[RS] PLAYBOOK-1.6.6** The repository MUST host a formal Architecture Decision Record corpus at `docs/adr/`. As of this Playbook version the corpus contains four ratified records: `ADR-0001-establish-adr-corpus.md`; `ADR-0002-pa-write-shape-and-correlation-contract.md`; `ADR-0003-mission-runner-staged-enable-posture.md`; `ADR-0004-rag-corpus-substrate-maturity-gradient.md`. [E5: `docs/adr/` directory listing at commit 309f85ee]

**[AC] PLAYBOOK-1.6.7** The repository ADR corpus MUST operate alongside the workspace-canonical ADR corpus hosted in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`. Both corpora carry constitutional authority for the decisions they record. [E1: workspace ADRs 0110–0150; E5: `docs/adr/ADR-0001..0004`]

**[EP] PLAYBOOK-1.6.8** Which ADR corpus hosts a given decision is determined by the scope of the decision. Decisions about platform substrate (repository structure, code patterns, cross-workspace primitives) SHOULD be recorded in the repository ADR corpus at `docs/adr/`. Decisions about workspace subsystems (deliverable-to-document mirror, canonical authority attribute, authority-aware retrieval, cascade automation, session-open pointer) SHOULD be recorded as workspace-canonical ADRs in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`. [E3: 2714 §2.4; E1: ADR-0001..0004 and workspace ADRs 0110–0150 as exemplars of the split]

> **Commentary:** The two ADR corpora do not compete. The choice of corpus follows the scope of the decision being recorded. A hypothetical future decision to change how the Playbook itself is amended would live in one of the two corpora (repository, since amendment discipline is a repository-substrate concern); a hypothetical future decision to add a new deliverable type to `Deliverable.deliverable_type` would live in the other (workspace, since deliverable schema is a workspace-subsystem concern).

### 1.6.4 The peer operating systems

**[RS] PLAYBOOK-1.6.9** The Research Operating System at `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` and the Implementation Operating System at `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` MUST be treated as peer constitutional documents relative to the Engineering Playbook. [E5: files exist at commit 309f85ee]

**[EP] PLAYBOOK-1.6.10** Chapter Research Methodology MUST cite the Research Operating System as prior art. Chapter Implementation Discipline MUST cite the Implementation Operating System as prior art. [E3: 2714 §17.1 Amendment A — part of the convergent 2708-2714 research chain]

> **Commentary:** PENDING — resolves once Chapters 2 and 3 stub-body-files reference the peer OSes.

> **Commentary:** The peer OS documents were the platform's methodology substrate before the Engineering Playbook. Their absorption into Playbook chapters is a design question, not a default. At v0.1 the Playbook cites and extends; it does not absorb.

### 1.6.5 The session-open contracts

**[RS] PLAYBOOK-1.6.11** The repository MUST enumerate its session-open contract documents in `core/services/docs_context_builder.py`. Two mechanisms cooperate: `CRITICAL_DOCS` (guaranteed injection with per-doc line caps) covers `CLAUDE.md` (300 lines), `00-START-NEXT-SESSION.md` (200 lines), `docs/governance/SYSTEM_OWNER.md` (100 lines), `docs/missions/CURRENT_MISSION.md` (100 lines), and `docs/USER_FEEDBACK_QUEUE.md` (100 lines); `PRIORITY_DOCS` (retrieval scoring boost of +100) additionally elevates `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `docs/ARCHITECTURE.md`, `docs/AGENTS.md`, `docs/CAPABILITIES.md`, `docs/DATABASE_MODEL_REFERENCE.md`, `docs/governance/SYSTEM_OWNER.md`, `docs/missions/CURRENT_MISSION.md`, `docs/canon/INDEX.md`, and `docs/USER_FEEDBACK_QUEUE.md`. [E5: `core/services/docs_context_builder.py:176-192` (PRIORITY_DOCS); E5: `core/services/docs_context_builder.py:362-369` (CRITICAL_DOCS); E5: `core/services/docs_context_builder.py:282-283` (PRIORITY_DOCS scoring boost)]

**[RS] PLAYBOOK-1.6.12** The `00-START-NEXT-SESSION.md` file at the repository root is a session-open contract loaded through a mechanism separate from `docs_context_builder.py`. Its content MUST be treated as authoritative for the session behavior it governs. [E5: `00-START-NEXT-SESSION.md` at repository root (verified present at commit 309f85ee); E5: `docs/research/process/RESEARCH_OPERATING_SYSTEM.md:853` (A3 lists `00-START-NEXT-SESSION.md` among REQUIRED session-open absorptions); E3: 2714 §14.5 — part of the convergent 2708-2714 research chain]

**[RS] PLAYBOOK-1.6.13** Modifications to any runtime-injected session-open contract MUST preserve the file's load path. Such modifications MUST NOT exceed the maximum-lines constraint imposed by the runtime injector. [E5: `core/services/docs_context_builder.py:363-365`]

## 1.7 Cycle 0 and Cycle 1A ratifications

> **History:** The platform's constitutional history includes two ratified cycles at the time of this Playbook version's ratification. Cycle 0 established foundational methodology; Cycle 1A established the workspace-canonical governance mechanism through which the Playbook itself is ratified.

Cycle 0 produced the following workspace-hosted artifacts in workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c`:

- `0000_RAR_METHODOLOGY` (deliverable UUID `754cff78-473b-4822-bd54-af1b45ed5988`).
- `0005_PLATFORM_BOOTSTRAP_CONTRACT` (UUID `7cbbf2d3-ad55-44f7-bb33-0f4cc91133ca`).
- `0010_RESEARCH_OPERATING_PROTOCOL` (UUID `5e2aa38d-8bd8-4d4f-88a8-6117e9f4d232`).
- `0020_CYCLE_0_CLOSEOUT` (UUID `e6e123a8-0b2f-41e1-8120-2c7961699d41`).
- `MANIFEST_v20260707` (UUID `4b2a655a-35f6-48de-9db8-3afcffc80476`).
- Corresponding workspace ratification records for each of the five artifacts above.

Cycle 1A produced the following workspace-hosted artifacts in the same workspace:

- `0100_CYCLE_1_OPEN` (UUID `462c5837-c454-4ad4-a8ed-8e836524ffbe`) with ratification `RATIFICATION_20260707_0100_CYCLE_1_OPEN` (UUID `89e2bfd7-1dcb-47fe-9b56-0a8fb299134c`).
- `0110_ADR_DELIVERABLE_TO_DOCUMENT_MIRROR` (UUID `f2614585-ff53-4624-8ade-10539f8dc028`) with ratification (UUID `7deae4de-0d7f-4629-bd4a-b283b02a2a0e`).
- `0120_ADR_CANONICAL_AUTHORITY_ATTRIBUTE` (UUID `5e492574-c54a-42ce-ad19-ed9e255ebb98`) with ratification (UUID `e69ec80c-c9e8-4a95-b5b8-bd23813eed45`).
- `0130_ADR_AUTHORITY_AWARE_RETRIEVAL` (UUID `52ce8c9c-dc37-4a66-b9b2-9952cff9d570`) with ratification (UUID `cccefae5-efda-4248-9735-23ce1b8fc218`).
- `0140_ADR_DOCS_CASCADE_AUTOMATION` (UUID `ceb9d355-3d5c-45cd-8cf4-6371864d798f`) with ratification `RATIFICATION_20260707_0140_ADR_DOCS_CASCADE_AUTOMATION` (UUID `5f81e0cc-f878-46fd-a890-9126cf4ce8bc`).
- `0150_ADR_CLAUDE_MD_BOOTSTRAP_POINTER` (UUID `ca5eef6e-c7a2-4a56-91fc-ac0f6d10ebab`) with ratification `RATIFICATION_20260707_0150_ADR_CLAUDE_MD_BOOTSTRAP_POINTER` (UUID `624c45fc-29d2-49a8-aaf5-290e42c0227b`).
- `CYCLE_1A_IMPLEMENTATION_EVIDENCE_LEDGER_0110_0140` (UUID `5cbd8110-b963-49ab-86d3-6e222ef68944`).
- `0199_CYCLE_1_CLOSEOUT` (UUID `53756b1c-3867-428b-8003-084604526591`) with ratification `RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT` (UUID `c883ebef-baa7-43c7-a6f0-dd8f3f22106d`).

[E2: workspace ORM census on 2026-07-08 at commit 309f85ee; E6: `docs/handoffs/SESSION_2701_CYCLE_1A_IMPLEMENTATION_HANDOFF.md`; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md`]

**[EP] PLAYBOOK-1.7.1** The Cycle 0 and Cycle 1A ratifications are immutable historical record. Playbook amendments MUST NOT modify their content. Playbook amendments MUST NOT alter their status. Playbook amendments MUST NOT attempt retroactive re-classification of their canonical authority. [E3: 2711 §10.4 — part of the convergent 2708-2714 research chain; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Immutability]

**[AC] PLAYBOOK-1.7.2** The five Cycle 1A Architecture Decision Records govern workspace-adjacent subsystems (deliverable-to-document mirror; canonical authority attribute; authority-aware retrieval; docs cascade automation; and CLAUDE.md bootstrap pointer). Their scope MUST remain Layer 5 workspace-subsystem governance binding on the platform's workspace substrate. [E1: workspace ADRs 0110–0150; E5: `content/_canonical_authority_helpers.py:33-60` (the substrate the ADRs govern); E2: five corresponding workspace ratification records]

**[EP] PLAYBOOK-1.7.3** The Cycle 1A ratification pattern — SIGN cycle, correction pass, System Owner directive, workspace ratification record naming the parent artifact — is the pattern that governs future workspace-canonical ratifications. Chapter Evolution and Amendment MUST codify the extension of this pattern to repository-canonical artifacts. [E6: SESSION_2707 §5 SIGN findings; E6: SESSION_2707 §7 Ratification ledger; E3: 2712 §8 — part of the convergent 2708-2714 research chain]

## 1.8 The Layer-2-in-Layer-5 anomaly

> **History:** During Cycle 0 and the early portion of Cycle 1A, no Layer 2 constitutional home existed for the Engineering Playbook or its precursors. As a consequence, several Layer 2 constitutional artifacts were hosted in Layer 5 (workspace `a9a16593-…`) as a matter of necessity. The affected artifacts are `0000_RAR_METHODOLOGY`, `0005_PLATFORM_BOOTSTRAP_CONTRACT`, `0010_RESEARCH_OPERATING_PROTOCOL`, `0020_CYCLE_0_CLOSEOUT`, and `MANIFEST_v20260707`. Session 2711 §8.9 and Session 2714 §12.3 formalized this observation as the "Layer-2-in-Layer-5 anomaly."

**[EP] PLAYBOOK-1.8.1** The pre-existing Layer 2 artifacts hosted in Layer 5 remain in Layer 5 hosting under this Playbook version. The Playbook MUST NOT move them. The Playbook MUST NOT re-canonicalize them. The Playbook MUST NOT attempt to re-ratify them under new Layer 2 hosting. Their ratifications stand; their canonicality classification stands. [E3: 2711 §8.9; E3: 2714 §12.3]

**[EP] PLAYBOOK-1.8.2** The Engineering Playbook is the first Layer 2 constitutional artifact placed at its natural Layer 2 host (the repository at `docs/ENGINEERING_PLAYBOOK.md`). Future Layer 2 constitutional artifacts SHOULD follow the Playbook's hosting pattern rather than the Layer-2-in-Layer-5 anomaly. [E3: 2711 §8.9; E3: 2712 §6.1]

> **Commentary:** The Layer-2-in-Layer-5 anomaly is not a governance defect. It is a historical artifact of the platform's ratification maturity at the time the affected artifacts were authored. Migration of the anomalous artifacts to repository hosting is out of scope for Playbook v0.1 and remains a Cycle 2 or later concern.

## 1.9 Provisional inventory

**[EP] PLAYBOOK-1.9.1** The constitutional ecosystem inventory referenced by this Playbook version is provisional. Session 2714 established that not every directory under `docs/` was enumerated at inventory time; directories including but not limited to `docs/playbooks/`, `docs/specs/`, `docs/plans/`, `docs/roadmap/`, and `docs/roadmaps/` were not fully inspected. Constitutional artifacts discovered after Playbook v0.1 ratification MUST be addressed by MINOR amendment when they materially affect any Playbook rule. [E3: 2714 §15.1, §17.1 Amendment B]

> **Commentary:** Provisional inventory does not degrade the Playbook's constitutional force. It acknowledges a scope limit at authoring time. Discovery of new constitutional artifacts is treated exactly as any other rule-relevant evidence: through amendment.

## 1.10 Rule origin discipline

The Engineering Playbook does not create rules. It records rules whose existence is demonstrated by ratified prior evidence.

**[EP] PLAYBOOK-1.10.1** Every normative statement in the Playbook body MUST derive from at least one source enumerated in the frozen evidence manifest for the Playbook version in force. [E3: 2713 §2.3, §7.1 — part of the convergent 2708-2714 research chain; E3: 2715 — part of the convergent chain]

**[EP] PLAYBOOK-1.10.2** New rules introduced by an amendment MUST cite evidence that exists at the time of the amendment. Prospective rules — rules about not-yet-observed practice — MUST NOT be introduced into the Playbook body. [E3: 2713 §2.3 — part of the convergent 2708-2714 research chain; E3: 2715 §2.2 — part of the convergent chain]

**[EP] PLAYBOOK-1.10.3** When the drafting protocol requires two or more evidence sources for a rule of a given statement class and only one qualifying source exists, the rule MUST be omitted from the Playbook body. [E3: 2713 §7.1 — part of the convergent 2708-2714 research chain]

> **Commentary:** These three rules establish the Playbook's authorial discipline. Together they mean that the Playbook is an *expression* of ratified constitutional decisions, not a proposal for what constitutional decisions ought to be. Amendments that appear to introduce new policy must in fact be codifying policy already demonstrated by ratified evidence.

## 1.11 Cross-references

- Chapter Provenance Classification §Statement Classification — the ten statement classes and their evidence thresholds.
- Chapter Provenance Classification §Evidence Admission Standard — per-class evidence bars.
- Chapter Evolution and Amendment §Amendment Discipline — what triggers PATCH, MINOR, and MAJOR bumps.
- Chapter Evolution and Amendment §Supersession Model — the parent-version chain.
- 2708 through 2715 research chain — convergent research foundation for this chapter.
- 2711 `platform_constitutional_architecture.md` — full constitutional architecture.
- 2714 `constitutional_ecosystem_inventory.md` — ecosystem inventory.
- 2715 `engineering_playbook_evidence_manifest.md` — frozen evidence set for v0.1.0.
- `docs/canon/INDEX.md` — Canon Registry.
- `docs/governance/SYSTEM_OWNER.md` — System Owner declaration.
- `docs/00-START-HERE/DOC_LIFECYCLE.md` — Doc Lifecycle constitution.
- `docs/adr/ADR-0001..0004` — repository ADR corpus.
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` — Research OS.
- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` — Implementation OS.
- Workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` — Layer 5 constitutional home.

## 1.12 Extension points

- New constitutional layers introduced by future evolution (see Chapter Evolution and Amendment §Extension Points).
- Additional `canonical_authority` values (per §1.4.2, subject to MAJOR amendment).
- Formal ratifier delegation (deferred to Cycle 3 or later).
- Cross-repository constitutional artifact coordination (deferred to Cycle 4 or later).
- Reconciliation of the Layer-2-in-Layer-5 anomaly (Cycle 2 or later).

---

# Chapter 2 — Research Methodology (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-2
**Purpose:** Establish constitutional scope for research methodology as it applies to Playbook amendments and platform decisions. Reference the peer Research Operating System.
**Scope:** Research work conducted under the Research Operating System; SIGN cycle discipline for Playbook amendments; convergent research patterns supporting new rules; Capability Discovery Record discipline for engineering campaigns.
**Status:** STUB (v0.1). Partial normative content added in v0.2.0 MINOR (PLAYBOOK-2.2.2). Further content deferred to future MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.2.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [GR]
**Rule ID range:** PLAYBOOK-2.1.1 through PLAYBOOK-2.3.1

---

## 2.1 Purpose and premise

**[EP] PLAYBOOK-2.1.1** Chapter 2 codifies research methodology by reference to the Research Operating System hosted at `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`. This chapter MUST NOT be interpreted as superseding the Research Operating System; it defers substantive research methodology to that peer document and codifies only its integration with Playbook amendment discipline. [E5: `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`; E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §2.5]

## 2.2 Substantive discipline

**[GR] PLAYBOOK-2.2.1** Research work that supports a Playbook amendment MUST follow the SIGN cycle discipline codified in the Research Operating System. The SIGN cycle exercised during Cycle 1A ratification is the canonical exemplar for the discipline as applied to Playbook amendments. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT (`c883ebef-baa7-43c7-a6f0-dd8f3f22106d`) §Timeline (4-batch SIGN cycle exercised); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (SIGN findings table)]

**[GR] PLAYBOOK-2.2.2** When a Category A investigation for a proposed engineering campaign materially changes the campaign scope — through deletion of substrate work already shipped, discovery of substrate satisfying the majority of the intended behavior, invalidation of prior scope claims, or expansion beyond the originally-scoped budget — a Capability Discovery Record MUST be authored before any implementation code lands for the campaign. The System Owner MUST ratify the Capability Discovery Record before any implementation code lands for the campaign. Capability Discovery Records MUST be located at `docs/research/platform/CDR_<NNN>_<slug>.md` with monotonically-increasing three-digit identifiers `<NNN>` across the platform's lifetime. The Capability Discovery Record body MUST contain at minimum the eleven sections established by the first two ratified Capability Discovery Records: §1 Original assumptions; §2 Repository evidence discovered; §3 Assumptions proven false; §4 Existing substrate identified; §5 New capability score; §6 Engineering work deleted; §7 Remaining work; §8 Whether the Capability Graph should be updated; §9 Ratification path; §10 Scope of the document; §11 Lessons Learned (permanent). Sections beyond §11 MUST be append-only. [E2: RATIFICATION_20260708_PLAYBOOK_v0_1_0 (`b083c034-5aba-4dc3-9758-57eba29b4bf2`) §Cycle 1A precedent (workspace ADRs 0110-0150 as the pre-CDR "discovery-artifact-before-code" pattern the rule generalizes to campaigns); E6: `docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md` §1.1 (CDR-001 + CDR-002 as first two ratified Capability Discovery Records establishing the 11-section template); E3: `docs/research/platform/CDR_001_notification_fanout_receiver_driven_pattern.md` §0-§11 (canonical structure exemplar — §16 "MISSING NotificationFanoutService" claim refuted by evidence of 3 shipped receiver-driven adapters, campaign downgraded from L-effort to wrap-up bundle before code landed); E3: `docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md` §0-§11 (canonical structure exemplar — §12 "PA turn does NOT auto-invoke either lane" claim refuted by evidence of `_build_context` line 3031 S943 auto-invocation, campaign scope reshaped from greenfield to extension of shipped substrate before code landed)]

> **Commentary:** PLAYBOOK-2.2.2 codifies the discipline that engineering campaigns begin with an evidence-first investigation against the current repository, not with the campaign-scope hypothesis embedded in planning artifacts. The rule fires only when the investigation *materially* changes scope — an investigation that confirms the planning hypothesis does not produce a Capability Discovery Record. The rule's evidence base is two consecutive Category A investigations at Session 2736 close (§16 Notification Fanout and §12 Knowledge Retrieval) which both discovered material scope changes; the Capability Discovery Record primitive absorbed both discoveries and produced audit trails between planning and implementation. The three-digit monotonic identifier ensures no ambiguity in cross-reference. The eleven-section template is drawn from the first two ratified instances; future amendments MAY extend the template but MUST NOT reduce the required minimum.

## 2.3 Extension deferred

**[EP] PLAYBOOK-2.3.1** Full authoring of Chapter 2's constitutional treatment of research methodology is deferred to a future MINOR amendment when experience with Playbook amendments produces sufficient evidence to codify additional rules. Until then, the Research Operating System remains the sole authoritative source for research methodology. [E3: 2712 engineering_playbook_architecture_specification.md §16.9 (stub chapters permitted for v0.1; converted to full via MINOR amendments as evidence accumulates — "the Playbook can ship v0.1 with stub chapters, evidence-gaps explicitly flagged") — part of the convergent 2708-2714 research chain per manifest §2.3]

## 2.4 Cross-references (informative)

- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` — peer constitutional document (authoritative).
- Chapter Provenance Classification §Statement Classification.
- Chapter Provenance Classification §Verification of Provenance.
- Chapter Evolution and Amendment §The Amendment Lifecycle.

## 2.5 Extension points (informative)

- SIGN cycle expectations for MAJOR Playbook amendments.
- Convergent research documentation patterns.
- Research arc closure discipline.
- Provenance classification of research outputs.

---

# Chapter 3 — Implementation Discipline (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-3
**Purpose:** Establish constitutional scope for implementation discipline as it applies to platform code changes and ADR authoring. Reference the peer Implementation Operating System.
**Scope:** Platform code changes with ADR intent; ADR authoring discipline; verify-before-build patterns; acceptance-tests-first discipline for engineering campaigns.
**Status:** STUB (v0.1). Partial normative content added in v0.2.0 MINOR (PLAYBOOK-3.2.2). Further content deferred to future MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.2.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [GR]
**Rule ID range:** PLAYBOOK-3.1.1 through PLAYBOOK-3.3.1

---

## 3.1 Purpose and premise

**[EP] PLAYBOOK-3.1.1** Chapter 3 codifies implementation discipline by reference to the Implementation Operating System hosted at `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` and to the repository Architecture Decision Record corpus at `docs/adr/`. This chapter MUST NOT be interpreted as superseding either the Implementation Operating System or the ADR corpus; it defers substantive implementation methodology to those peer surfaces and codifies only their integration with Playbook amendment discipline. [E5: `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`; E5: `docs/adr/` directory; E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §2.4, §2.5]

## 3.2 Substantive discipline

**[GR] PLAYBOOK-3.2.1** Platform code changes with ADR intent MUST follow the Implementation Operating System. Cycle 1A implementation exercised across five workspace Architecture Decision Records is the canonical exemplar of the discipline. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (Cycle 1A implementation exercised under IOS discipline); E6: `docs/handoffs/SESSION_2701_CYCLE_1A_IMPLEMENTATION_HANDOFF.md` (Cycle 1A implementation ledger)]

**[GR] PLAYBOOK-3.2.2** Before implementation code lands for an engineering campaign, the acceptance tests that will prove the capability MUST be authored. Acceptance tests MUST be written prior to the implementation they exercise. Acceptance tests MUST NOT be reverse-engineered from the implementation after the fact. Each acceptance test MUST assert an observable property of the capability under test — a file:line-cited code path, an ORM query result, a log-line format, a latency bound, or a runtime effect. Each acceptance test MUST be verifiable at HEAD once the capability lands. A test authored to match what an implementation happens to do rather than what the capability specification requires MUST NOT be admitted as an acceptance test for the campaign. Amendment of an acceptance test's specification after implementation lands MUST be preceded by a Capability Discovery Record amendment that ratifies the specification change. [E2: RATIFICATION_20260708_PLAYBOOK_v0_1_0 (`b083c034-5aba-4dc3-9758-57eba29b4bf2`) §Timeline (SIGN cycle as pre-ratification testing precedent — every rule was verified before entering the corpus, analogous to acceptance-testing-first for capabilities); E6: `docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md` §6.5 (acceptance-tests-first pattern documented as reusable and cited as EOS Rule R3); E5: `core/tests/test_pa_knowledge_retrieval_capability.py:1-35` (23-test AT harness authored pre-implementation across AT-1 through AT-11, `@expectedFailure` markers removed at each phase close, module docstring codifying "Do NOT rewrite these tests to match an implementation. If an implementation cannot satisfy a test, either the implementation is wrong or the test needs a governance amendment via CDR-003+ before the test changes.")]

> **Commentary:** PLAYBOOK-3.2.2 prevents the "assumed gap" failure mode named in the first two ratified Capability Discovery Records. Without acceptance tests written pre-implementation, an engineering campaign can drift into reorganization of shipped substrate rather than delivering new capability — the campaign satisfies its own assumptions rather than the capability specification. The rule's mechanism is the same discipline that produced 51/51 passing tests at Session 2736 close with zero regression across six sequential phases: define the observable property, write the test that asserts it, then ship the implementation until the test passes. The `@expectedFailure` marker convention preserves the test-authorship provenance across the phase boundary; a reviewer inspecting the diff observes both the test-body edit and the marker-removal as separate signals, closing the reverse-engineering loophole.

## 3.3 Extension deferred

**[EP] PLAYBOOK-3.3.1** Full authoring of Chapter 3's constitutional treatment of implementation discipline is deferred to a future MINOR amendment when experience with the discipline produces sufficient evidence to codify additional rules. Until then, the Implementation Operating System and the repository ADR corpus remain the authoritative sources for implementation methodology. [E3: 2712 §16.9 (stub-chapter deferral discipline) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 3.4 Cross-references (informative)

- `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md` — peer constitutional document (authoritative).
- `docs/adr/ADR-0001..0004` — repository Architecture Decision Record corpus.
- Workspace Architecture Decision Records 0110–0150 — workspace-canonical corpus.
- Chapter Provenance Classification §Statement Classification.
- Chapter Evolution and Amendment §The Amendment Lifecycle.

## 3.5 Extension points (informative)

- Verify-before-build discipline codification.
- ADR authoring templates and conventions.
- Reversibility scoring for implementation decisions.
- Cross-corpus consistency between repository and workspace ADRs.

---

# Chapter 4 — Documentation Cascade (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-4
**Purpose:** Establish constitutional scope for documentation cascade discipline as it applies to Playbook body updates and documentation-corpus synchronization. Reference the pre-existing Doc Lifecycle constitution.
**Scope:** Documentation modifications, four-step cascade discipline, RAG synchronization, workspace mirror discipline.
**Status:** STUB (v0.1). Full content deferred to v0.2+ MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [DR]
**Rule ID range:** PLAYBOOK-4.1.1 through PLAYBOOK-4.3.1

---

## 4.1 Purpose and premise

**[EP] PLAYBOOK-4.1.1** Chapter 4 codifies documentation cascade discipline by reference to the Doc Lifecycle constitution hosted at `docs/00-START-HERE/DOC_LIFECYCLE.md` and the workspace Architecture Decision Record 0140 (`ceb9d355-3d5c-45cd-8cf4-6371864d798f`). This chapter MUST NOT duplicate the rules codified in the Doc Lifecycle constitution; it extends them with Playbook-amendment-specific cascade discipline. [E5: `docs/00-START-HERE/DOC_LIFECYCLE.md`; E1: workspace ADR-0140 (`ceb9d355-3d5c-45cd-8cf4-6371864d798f`); E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §2.3, §17.1 Amendment C]

## 4.2 Substantive discipline

**[DR] PLAYBOOK-4.2.1** Documentation modifications that affect the RAG-mirrored corpus MUST run the four-step cascade codified by workspace Architecture Decision Record 0140: build the docs index; build the RAG corpus; sync docs to the Document table; embed unembedded rows. The cascade MUST run before an amendment PR is considered ready for the mirror stage of ratification. [E1: workspace ADR-0140 (`ceb9d355-3d5c-45cd-8cf4-6371864d798f`); E4: `content.Document.objects.count() = 2998` verified 2026-07-08 at commit 309f85ee]

## 4.3 Extension deferred

**[EP] PLAYBOOK-4.3.1** Full authoring of Chapter 4's constitutional treatment of documentation cascade is deferred to a future MINOR amendment when the cascade discipline evolves or new cascade steps are added. Until then, the Doc Lifecycle constitution and workspace ADR-0140 remain the authoritative sources for cascade methodology. [E3: 2712 §16.9 (stub-chapter deferral discipline) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 4.4 Cross-references (informative)

- `docs/00-START-HERE/DOC_LIFECYCLE.md` — pre-existing peer constitutional document.
- Workspace ADR-0140 (`ceb9d355-3d5c-45cd-8cf4-6371864d798f`) — Docs Cascade Automation.
- Workspace ADR-0110 (`f2614585-ff53-4624-8ade-10539f8dc028`) — Deliverable to Document Mirror.
- Chapter Evolution and Amendment §The Amendment Lifecycle Stage 6 Mirror.

## 4.5 Extension points (informative)

- Autogen section handling during cascade.
- DOC-POINTER-V1/V2 header propagation.
- Workspace-source mirror row lifecycle.
- Cascade drift detection and recovery.

---

# Chapter 5 — PA / Rigby Collaboration (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-5
**Purpose:** Establish constitutional scope for Personal Assistant collaboration discipline. Reference the collaboration protocol codified in the auto-loaded MEMORY rules.
**Scope:** Agent-mediated authoring work; PA tool call discipline; verifier-loop patterns.
**Status:** STUB (v0.1). Partial normative content added in v0.2.0 MINOR (PLAYBOOK-5.2.2). Further content deferred to future MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.2.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [GR]
**Rule ID range:** PLAYBOOK-5.1.1 through PLAYBOOK-5.3.1

---

## 5.1 Purpose and premise

**[EP] PLAYBOOK-5.1.1** Chapter 5 codifies Personal Assistant collaboration discipline by reference to the auto-loaded MEMORY rules at `MEMORY.md` in the repository root. This chapter MUST NOT duplicate the collaboration rules codified in MEMORY.md; it references them and identifies their integration with Playbook amendment discipline. [E5: `MEMORY.md`; E3: 2712 §16.9 (stub chapters reference authoritative sources rather than duplicating them; MINOR-amendment path preserved) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 5.2 Substantive discipline

**[EP] PLAYBOOK-5.2.1** The collaboration protocol adopted for agent-mediated authoring work is: the author directs; the Personal Assistant executes; the author verifies. This protocol is codified in the MEMORY.md rule `feedback_claude_directs_rigby_then_verifies` and the verifier-loop pattern is codified in the MEMORY.md rule `feedback_verifier_loop_pattern`. [E5: `MEMORY.md` (`feedback_claude_directs_rigby_then_verifies`); E5: `MEMORY.md` (`feedback_verifier_loop_pattern`); E3: 2714 constitutional_ecosystem_inventory.md §6.3 (explicit statement: "Owner: Chris (ratifier). Author: Claude Code (per 2713). Reviewer: Rigby SIGN (default) or fallback Claude verifier-loop.") — part of the convergent 2708-2714 research chain per manifest §2.3]

**[GR] PLAYBOOK-5.2.2** When the author dispatches a verification objective to the Personal Assistant, the author MUST state the verification objective. The author MUST state the expected return format. The author MAY state methodology-required constraints such as read-only verification, no mutations, runtime validation against a specific SHA, or convergent-evidence requirements. The author MUST NOT enumerate the platform tools the Personal Assistant is required to use to satisfy the objective. The Personal Assistant MUST select tools autonomously from its available surface to satisfy the objective. [E2: RATIFICATION_20260708_PLAYBOOK_v0_1_0 (`b083c034-5aba-4dc3-9758-57eba29b4bf2`) §Timeline (SIGN dispatch pattern the rule generalizes); E6: `docs/handoffs/SESSION_2736_KNOWLEDGE_RETRIEVAL_CAMPAIGN_CLOSED.md` §3 (Rigby SIGN checkpoint record demonstrating the rule producing substrate discoveries a tool-prescribed dispatch would have suppressed); E3: `docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md` §12.6 (the ratified precedent — the rule's initial codification in `docs/EOS_RULES.md` as R1 and its production exercise on the CDR-002 Rigby SIGN dispatch that discovered `PAKnowledgeInjector` S773 as a fifth substrate Claude's grep had missed)]

> **Commentary:** PLAYBOOK-5.2.2 prevents two failure modes. When the author under-instructs the Personal Assistant, verification is superficial. When the author over-instructs the Personal Assistant, the author's tool assumptions become verification blind-spots — the Personal Assistant cannot apply its operational knowledge of tool correctness, coverage, or dedup characteristics. Rule 5.2.2 codifies the discipline that the author defines the *what*, the Personal Assistant chooses the *how*. The methodology-required exception preserves cases where the verification approach itself is a rule (for example, read-only verification against a specific SHA).

## 5.3 Extension deferred

**[EP] PLAYBOOK-5.3.1** Full authoring of Chapter 5's constitutional treatment of Personal Assistant collaboration is deferred to a future MINOR amendment. Until then, MEMORY.md remains the authoritative source for the collaboration protocol. [E3: 2712 §16.9 (stub-chapter deferral discipline) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 5.4 Cross-references (informative)

- `MEMORY.md` at repository root — auto-loaded collaboration rules.
- Chapter Evolution and Amendment §The Amendment Lifecycle Stage 2 Author and Stage 4 Correct.
- Chapter Provenance Classification §Verification of Provenance.

## 5.5 Extension points (informative)

- PA tool call discipline codification.
- Verifier-loop pattern extensions for cross-workspace work.
- Placeholder-stall recovery discipline.
- Multi-agent authoring coordination.

---

# Chapter 6 — Provenance Classification Standard

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-6
**Purpose:** Codify the provenance classification standard (PIC-10) that governs how evidence is classified, how normative statements are typed, and what evidence admission thresholds apply to each statement class.
**Scope:** Every citation in the Playbook body, every rule in the Playbook body, and every amendment that adds, modifies, or retires rules.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [GR]
**Rule ID range:** PLAYBOOK-6.1.1 through PLAYBOOK-6.10.4

---

## 6.1 Purpose and premise

The Provenance Classification Standard (hereafter *PIC-10*, after its Process Improvement Candidate origin in Cycle 1A) defines the vocabulary by which the Playbook classifies both the content of citations and the shape of rules. It exists so that a reader confronted with any Playbook rule can determine, without external context, what kind of evidence supports the rule and what kind of authority the rule carries.

> **History:** PIC-10 was surfaced during the SIGN cycle of the Cycle 1A closeout deliverable (0199) in Session 2707. Batch 4 of the SIGN cycle identified that the reconciling System Owner Directive in the §8 content could not be recovered verbatim from the platform's chat corpus, forcing the introduction of provenance-honest attribution as a first-class discipline. The five content provenance classes originally proposed in the 0199 Appendix D forwarded PIC candidates are codified in this chapter.

**[EP] PLAYBOOK-6.1.1** The Provenance Classification Standard is the sole authority for classifying citations and rules within the Playbook body. Amendments MUST classify every new citation using the classes in §6.3. Amendments MUST classify every new rule using the classes in §6.4. [E3: 2712 §11 — part of the convergent 2708-2714 research chain; E3: 2713 §6, §7 — part of the convergent chain; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification]

> **Commentary:** Because PIC-10 is codified as a chapter of the Playbook itself, amendments to the Playbook are subject to the discipline the chapter codifies. This creates a bootstrapping intent that any future amendment to Chapter 6 must satisfy the very classification it defines.

**[EP] PLAYBOOK-6.1.2** The Playbook's provenance classification is dual: content provenance classes (§6.3) classify what kind of source a citation refers to; statement classes (§6.4) classify what kind of rule cites the source. Every normative rule MUST carry both classifications. [E3: 2711 §11 — part of the convergent 2708-2714 research chain; E3: 2713 §6.1 — part of the convergent chain]

## 6.2 The two concepts

The classification system separates two orthogonal concerns: the nature of a source, and the shape of a rule that cites the source.

**[EP] PLAYBOOK-6.2.1** Content provenance classes describe the nature of a citation. They answer the question: what kind of evidence is being invoked? A single citation MUST carry exactly one content provenance class as defined in §6.3. [E3: 2711 §11 — part of the convergent 2708-2714 research chain; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification]

**[EP] PLAYBOOK-6.2.2** Statement classes describe the shape of a normative rule. They answer the question: what kind of rule is this? A single rule MUST carry exactly one statement class as defined in §6.4. [E3: 2713 §6.1 — part of the convergent 2708-2714 research chain]

> **Commentary:** The distinction matters because a single rule may cite multiple sources whose content provenance classes differ. A rule of statement class `[AC]` Architectural Constraint may cite E5 platform evidence, E1 Architecture Decision Record, and E6 session handoff — each of those citations carrying its own content provenance class. Confusing the two dimensions produces citations that appear to satisfy the admission threshold when they do not, or rules that appear stronger than their underlying evidence supports.

## 6.3 Content provenance classes

The Playbook recognizes exactly five content provenance classes. The classes were surfaced by the SIGN cycle of the Cycle 1A closeout and ratified as PIC-10 in the corresponding ratification record.

| Class | Description |
|---|---|
| Verified primary evidence | A source whose content can be re-produced by direct fetch from the substrate on which it was originally recorded. |
| Verified repository or runtime fact | An observable property of the platform's code, runtime data, or configuration that can be reproduced by repeating a specified observation. |
| Verified quoted source | A specific speech act — a directive, a proposal, or a verbatim excerpt — preserved verbatim with speaker and moment identified. |
| Historical reconstruction | A claim about past events assembled from partial sources when no single source records the full event. |
| Engineering conclusion | A claim reached through reasoning about verified evidence, where the conclusion itself is not directly verifiable but the underlying sources are. |

**[GR] PLAYBOOK-6.3.1** The Playbook recognizes exactly the five content provenance classes enumerated in the preceding table. Additional content provenance classes MUST NOT be introduced without a MAJOR Playbook amendment. [E2: `0199_CYCLE_1_CLOSEOUT` Appendix D (PIC-10); E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification]

**[GR] PLAYBOOK-6.3.2** A citation of the class *verified primary evidence* MUST identify the substrate location — a git commit SHA, a workspace deliverable UUID, or a database observation timestamp — precisely enough for the source to be re-fetched by a reader with substrate access. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification directive verbatim (which identifies substrate SHA `81ff5547aa86f86fbb973d51a4fd7d658146832cd8d2c90fe9a486eb1a51d305`); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §7]

**[GR] PLAYBOOK-6.3.3** A citation of the class *verified repository or runtime fact* MUST identify the observation method — a file path with line range, an ORM query, or a configuration key — precisely enough for the observation to be repeated by a reader with runtime access. [E5: `content/_canonical_authority_helpers.py:33-60` as an exemplar citation of this class; E3: 2712 §11.1 (E5 evidence class definition)]

**[GR] PLAYBOOK-6.3.4** A citation of the class *verified quoted source* MUST preserve the verbatim text of the quoted content. Such a citation MUST identify the speaker or authoring role. Such a citation MUST identify the moment of the speech act. Such a citation MUST NOT paraphrase the quoted content. [E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4 timeline; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification directive verbatim]

> **Commentary:** The verbatim requirement is what distinguishes *verified quoted source* from *historical reconstruction*. A quoted source that has been re-worded, however faithfully, ceases to be a verified quoted source. If the verbatim text is unavailable, the citation MUST be re-classified as historical reconstruction (§6.3.5) rather than presented as if verbatim.

**[GR] PLAYBOOK-6.3.5** A citation of the class *historical reconstruction* MUST be explicitly labeled with the phrase "historical reconstruction," "reconstructed from partial sources," or an equivalent marker, and MUST NOT be presented as if it were a verbatim quotation or a verified primary source. [E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4 (the reconciling System Owner Directive was preserved substantively but not verbatim, and the Playbook records that fact rather than pretending otherwise)]

**[GR] PLAYBOOK-6.3.6** A citation of the class *engineering conclusion* MUST be explicitly labeled as an engineering conclusion. Such a citation MUST identify at least one underlying verified evidence source from which the conclusion was reached. Engineering conclusions cited without underlying-source identification MUST NOT be treated as evidence. [E3: 2711 §11; E3: 2713 §11]

> **Commentary:** The five classes form a strength gradient. Verified primary evidence is the strongest form because the substrate can be re-fetched. Verified quoted source and verified repository or runtime fact are next in strength because a specific artifact or observation can be identified. Historical reconstruction is weaker because it acknowledges assembled provenance. Engineering conclusion is the weakest because it declares that reasoning was applied on top of underlying evidence. A rule that relies solely on engineering-conclusion citations carries less constitutional weight than one supported by verified primary evidence.

## 6.4 Statement classes

The Playbook recognizes exactly ten statement classes, each carrying an authority level, an evidence admission threshold defined in §6.6, and a versioning implication recorded in Chapter Evolution and Amendment.

| Marker | Name | Purpose |
|---|---|---|
| `[AC]` | Architectural Constraint | An inviolable structural rule about the platform's constitutional architecture. |
| `[GR]` | Governance Rule | A rule about how the Playbook or related governance artifacts are authored, amended, ratified, or preserved. |
| `[OR]` | Operational Rule | A rule about day-to-day procedural discipline for how work on the platform is performed. |
| `[EP]` | Engineering Principle | A high-level engineering value from which specific rules derive. |
| `[IP]` | Implementation Pattern | A recommended code shape or code discipline demonstrated by prior implementation. |
| `[RS]` | Repository Standard | A rule about repository file structure, naming, layout, or conventions. |
| `[RP]` | Runtime Policy | A rule about executable governance embedded in runtime data. |
| `[RC]` | Recovery Procedure | A documented sequence for responding to a specific class of incident. |
| `[DR]` | Documentation Rule | A rule about the production, maintenance, mirroring, or cascade of documentation. |
| `[RM]` | Research Methodology | A rule about how research is conducted, evaluated, or ratified. |

**[GR] PLAYBOOK-6.4.1** The Playbook recognizes exactly the ten statement classes enumerated in the preceding table. Additional statement classes MUST NOT be introduced without a MAJOR Playbook amendment. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.2** Every normative sentence in the Playbook body MUST carry exactly one statement-class marker drawn from the ten classes enumerated in §6.4.1. Sentences without a marker MUST NOT be treated as normative. [E3: 2713 §4.1; E3: 2713 §6.1]

The following rules further specify each class.

**[GR] PLAYBOOK-6.4.3** A rule marked `[AC]` (*Architectural Constraint*) states an inviolable structural rule about the platform's constitutional architecture. Violation of an Architectural Constraint MUST be treated as a corruption of the platform's constitutional integrity requiring immediate remediation. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.4** A rule marked `[GR]` (*Governance Rule*) states a rule about how the Playbook or related governance artifacts are authored, amended, ratified, or preserved. Governance Rules bind the authoring process itself and MUST be observed by every author of amendments. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.5** A rule marked `[OR]` (*Operational Rule*) states day-to-day procedural discipline for how work on the platform is performed. Operational Rules bind the platform's contributors during ordinary work and MUST be observed unless a Recovery Procedure explicitly authorizes deviation. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.6** A rule marked `[EP]` (*Engineering Principle*) states a high-level engineering value from which specific rules derive. Engineering Principles articulate the reason a body of rules exists and MAY be cited by downstream rules that extend the principle. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.7** A rule marked `[IP]` (*Implementation Pattern*) states a recommended code shape or code discipline demonstrated by prior implementation. Implementation Patterns are prescriptive but scoped to the technical substrate and MAY be extended without a MAJOR amendment. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.8** A rule marked `[RS]` (*Repository Standard*) states a rule about repository file structure, naming, layout, or conventions. Repository Standards bind the shape of the repository itself and MUST be enforced by continuous integration checks where practicable. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.9** A rule marked `[RP]` (*Runtime Policy*) states a rule about executable governance embedded in runtime data — autopilot policies, budgets, agent controls, and PublishGate transitions. Runtime Policies bind live enforcement rather than documentary declaration and MUST identify the runtime substrate on which they take effect. [E3: 2713 §6.1; E3: 2714 §5]

**[GR] PLAYBOOK-6.4.10** A rule marked `[RC]` (*Recovery Procedure*) states a documented sequence for responding to a specific class of incident. Recovery Procedures MUST cite at least one prior successful application before ratification. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.11** A rule marked `[DR]` (*Documentation Rule*) states a rule about the production, maintenance, mirroring, or cascade of documentation. Documentation Rules bind documentation discipline and MUST be observed by every author who modifies documentation artifacts. [E3: 2713 §6.1]

**[GR] PLAYBOOK-6.4.12** A rule marked `[RM]` (*Research Methodology*) states a rule about how research is conducted, evaluated, or ratified. Research Methodology rules bind research work performed under the Research Operating System and MUST cite the peer Research OS document as prior art where applicable. [E3: 2713 §6.1; E3: 2711 §2.2 (existence of Research OS)]

> **Commentary:** The ten classes are not all equal in constitutional weight. Architectural Constraint, Governance Rule, Engineering Principle, Runtime Policy, Documentation Rule, and Research Methodology carry higher weight because they govern the substrate on which the Playbook operates. Operational Rule, Implementation Pattern, Repository Standard, and Recovery Procedure carry lower weight because they govern application within an already-established substrate. The evidence admission thresholds in §6.6 reflect this weighting.

## 6.5 Evidence classes

The Playbook recognizes six primary evidence classes plus one auxiliary class. Every citation in the Playbook body identifies its evidence class alongside its content provenance class.

| Class | Name | Substrate |
|---|---|---|
| E1 | Architecture Decision Record | Workspace deliverable of type `adr`, or repository file at `docs/adr/`. |
| E2 | Ratification Record | Workspace deliverable of type `ratification_record`. |
| E3 | Research Document | Repository file under `docs/research/*`. |
| E4 | Runtime Evidence | Reproducible ORM query, database row count, or observable runtime behavior. |
| E5 | Platform Evidence | Specific location in platform code, configuration, or infrastructure files. |
| E6 | Session Handoff | Repository file under `docs/handoffs/*`. |
| M (auxiliary) | MEMORY.md rule | Auto-loaded behavioral rule at repository root `MEMORY.md`. |

**[GR] PLAYBOOK-6.5.1** The Playbook recognizes exactly the six primary evidence classes E1 through E6 and the one auxiliary class M enumerated in the preceding table. Additional evidence classes MUST NOT be introduced without a MAJOR Playbook amendment. Every citation in the Playbook body MUST identify its evidence class. [E3: 2712 §11.1; E3: 2713 §7; E3: 2715 §0]

**[GR] PLAYBOOK-6.5.2** A citation of class *E1 Architecture Decision Record* MUST identify the ADR by workspace deliverable UUID (for workspace-canonical ADRs) or by repository file name (for repository-canonical ADRs). [E1: workspace ADRs 0110–0150 as exemplars of workspace-canonical E1 citations; E1: `docs/adr/ADR-0001..0004` as exemplars of repository-canonical E1 citations; E3: 2714 §2.4]

**[GR] PLAYBOOK-6.5.3** A citation of class *E2 Ratification Record* MUST identify the ratification record by workspace deliverable UUID and SHOULD identify its parent artifact by UUID or by canonical short-name. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT (`c883ebef-baa7-43c7-a6f0-dd8f3f22106d`) naming its parent `0199_CYCLE_1_CLOSEOUT` (`53756b1c-3867-428b-8003-084604526591`); E2: the eight Cycle 1A workspace ratification records]

**[GR] PLAYBOOK-6.5.4** A citation of class *E3 Research Document* MUST identify the research document by file path relative to the repository root and SHOULD identify the specific section by number or by symbolic anchor. [E3: 2708 through 2717 research chain under `docs/research/platform/` as exemplars; E3: 2711 §11]

**[GR] PLAYBOOK-6.5.5** A citation of class *E4 Runtime Evidence* MUST identify the observation method. Such a citation MUST identify the timestamp or version identifier at which the observation was verified. [E4: ORM query `Deliverable.objects.filter(workspace_id='a9a16593-…').count() = 25` verified 2026-07-08 at commit 309f85ee; E3: 2711 §2.3]

**[GR] PLAYBOOK-6.5.6** A citation of class *E5 Platform Evidence* MUST identify the file path relative to the repository root and SHOULD identify the specific line range or function name. [E5: `core/rag_integration.py:30-34`; E5: `content/_canonical_authority_helpers.py:33-60`; E5: `core/services/docs_context_builder.py:184`]

**[GR] PLAYBOOK-6.5.7** A citation of class *E6 Session Handoff* MUST identify the handoff by filename relative to `docs/handoffs/` and SHOULD identify the specific section. [E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5; E6: `docs/handoffs/SESSION_2701_CYCLE_1A_IMPLEMENTATION_HANDOFF.md`]

**[GR] PLAYBOOK-6.5.8** A citation of the auxiliary class *M* — MEMORY.md rule — MUST NOT satisfy an evidence admission threshold on its own. Every M citation MUST be paired with at least one citation of a primary evidence class E1 through E6. [E3: 2715 §0 (M-class shorthand); E5: `MEMORY.md` at repository root]

> **Commentary:** M-class citations are useful because MEMORY.md rules preserve institutional knowledge about behavioral patterns that have been observed across sessions but are not directly ratified as workspace-canonical or repository-canonical artifacts. Pairing an M citation with a primary evidence citation preserves the institutional memory while ensuring the rule is grounded in ratified or reproducible evidence.

## 6.6 Evidence admission standard

Every normative rule in the Playbook body is subject to an evidence admission threshold determined by the rule's statement class. Rules whose cited evidence does not meet the applicable threshold MUST NOT enter the ratified corpus.

**[GR] PLAYBOOK-6.6.1** Evidence admission is the minimum evidence a rule MUST cite before ratification as part of the Playbook. A rule MAY be ratified only after satisfying its evidence admission threshold. [E3: 2713 §7]

**[GR] PLAYBOOK-6.6.2** A rule of class `[AC]` Architectural Constraint MUST cite at least two evidence sources. At least one MUST be of class E1. At least one MUST be of class E5. Class E2 MAY additionally be cited but MUST NOT substitute for E1. [E3: 2713 §7.1 (Architectural Constraint threshold); E3: 2715 §2.2 (frozen manifest confirming E1 + E5 required)]

**[GR] PLAYBOOK-6.6.3** A rule of class `[GR]` Governance Rule MUST cite at least two evidence sources, at least one of which is of class E1 or E2 and at least one of which is of class E6. [E3: 2713 §7.1 (Governance Rule threshold)]

**[GR] PLAYBOOK-6.6.4** A rule of class `[OR]` Operational Rule MUST cite at least two evidence sources drawn from any of the evidence classes, at least one of which is of class E3 or E6. [E3: 2713 §7.1 (Operational Rule threshold)]

**[GR] PLAYBOOK-6.6.5** A rule of class `[EP]` Engineering Principle MUST cite at least one evidence source of class E1. As an alternative, a single citation to an E3 research document that itself synthesizes convergent findings from two or more independent research arcs MAY satisfy the threshold in accordance with the convergent-research exception in §6.6.12. [E3: 2713 §7.1 (Engineering Principle threshold); E3: 2713 §7.2 (convergent-research exception); E3: 2715 §2.2 (frozen manifest confirming E1 or convergent E3 required)]

**[GR] PLAYBOOK-6.6.6** A rule of class `[IP]` Implementation Pattern MUST cite at least two evidence sources, at least one of which is of class E5 and at least one of which is of class E6. [E3: 2713 §7.1 (Implementation Pattern threshold)]

**[GR] PLAYBOOK-6.6.7** A rule of class `[RS]` Repository Standard MUST cite at least one evidence source drawn from class E5 or class E3. [E3: 2713 §7.1 (Repository Standard threshold)]

**[GR] PLAYBOOK-6.6.8** A rule of class `[RP]` Runtime Policy MUST cite at least two evidence sources, at least one of which is of class E4 and at least one of which is of class E5. [E3: 2713 §7.1 (Runtime Policy threshold)]

**[GR] PLAYBOOK-6.6.9** A rule of class `[RC]` Recovery Procedure MUST cite at least one E6 evidence source that documents a successful application of the procedure. [E3: 2713 §7.1 (Recovery Procedure threshold)]

**[GR] PLAYBOOK-6.6.10** A rule of class `[DR]` Documentation Rule MUST cite at least two evidence sources, at least one of which is of class E1 or E3 and at least one of which is of class E4. [E3: 2713 §7.1 (Documentation Rule threshold)]

**[GR] PLAYBOOK-6.6.11** A rule of class `[RM]` Research Methodology MUST cite at least two evidence sources, at least one of which is of class E3 and at least one of which is of class E2. [E3: 2713 §7.1 (Research Methodology threshold)]

**[GR] PLAYBOOK-6.6.12** The convergent-research exception permitted by PLAYBOOK-6.6.5 applies only to rules of class `[EP]` Engineering Principle. Rules of other classes MUST meet their full evidence bars regardless of the presence of convergent research documents. [E3: 2713 §7.2]

**[GR] PLAYBOOK-6.6.14** A document that catalogs, describes, or enumerates a constitutional evidence chain MUST NOT be cited as a chain-member evidence source for the chain it catalogs. A document catalog MAY be cited for its own independent claims about the chain — freeze semantics, admissibility rules, or version boundaries. [E2: v0.1.0 ratification record body §6 Constitutional debt disposition (deliverable `b083c034-5aba-4dc3-9758-57eba29b4bf2`); E3: `docs/research/platform/playbook_constitutional_correction_session_2725.md` (CD-48 principle extraction); E3: `docs/research/platform/platform_constitutional_transition_review.md` §5.6 (F-C1(a)+(b) required form); E5: `docs/canon/INDEX.md` §Constitutional Canon (F-C1(b) guarantee-in-context linkage); E6: `docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md` (CD-48 disposition anchored in v0.1.0 ratification handoff)]

> **Commentary:** The thresholds reflect the observed constitutional-weight gradient. Higher-weight classes ([AC], [GR], [RP], [DR], [RM]) require at least two evidence sources with at least one high-strength primary source. Lower-weight classes ([RS], [RC]) require fewer sources. The convergent-research exception applies only to [EP] because Engineering Principles express foundational values whose evidence commonly lives in the intersection of multiple research arcs — a form of evidence that no single source records but that convergent research documents synthesize.

## 6.7 Provenance-honest attribution

Provenance-honest attribution is the discipline applied when a citation would ordinarily be classified as *verified quoted source* (§6.3.4) but the verbatim text of the quoted source cannot be recovered from platform substrate. The pattern was surfaced during Cycle 1A's closeout SIGN cycle when the reconciling System Owner Directive in the 0199 §8 content proved unrecoverable via exhaustive ORM search of the platform's chat corpus.

> **History:** Provenance-honest attribution was introduced as a first-class discipline in Session 2707. Batch 4 of the 0199 SIGN cycle classified the reconciling System Owner Directive as F-BLOCKING when its provenance could not be recovered. The correction pass replaced the paraphrased directive with a substantively-preserved paragraph explicitly labeled "engineering rationale recorded during authoring rather than a provenance-guaranteed verbatim quotation." Chapter 6 §6.7 codifies the pattern.

**[GR] PLAYBOOK-6.7.1** When an author intends to preserve the substance of a speech act whose verbatim text cannot be recovered from platform substrate, the author MUST use provenance-honest attribution rather than presenting the paraphrase as a verified quoted source. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT (`c883ebef-baa7-43c7-a6f0-dd8f3f22106d`) §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (G1 F-BLOCKING classification)]

**[GR] PLAYBOOK-6.7.2** A provenance-honest attribution MUST be explicitly labeled with a phrase that identifies the attribution as non-verbatim — for example, "engineering rationale recorded during authoring rather than a provenance-guaranteed verbatim quotation" or an equivalent formulation. The label MUST appear on or immediately adjacent to the attributed content. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification (the specific labeling formulation ratified in Session 2707); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §6 (correction pass 1 delta ledger)]

**[GR] PLAYBOOK-6.7.3** A provenance-honest attribution MUST NOT invoke the *verified quoted source* content provenance class (§6.3.4). It MUST be classified as *historical reconstruction* (§6.3.5) or as *engineering conclusion* (§6.3.6) as appropriate to the attribution's shape. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (G1 finding + resolution)]

**[GR] PLAYBOOK-6.7.4** Before using provenance-honest attribution, the author MUST attempt substrate-recovery per the mechanisms described in §6.8. The author MUST record the recovery attempt. Attribution based on absent recovery attempts MUST NOT be labeled as provenance-honest. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4]

> **Commentary:** Provenance-honest attribution is not a fallback that authors invoke to avoid the discipline of finding verbatim sources. It is a formal declaration made after recovery has been attempted and has failed. The recovery attempt itself becomes part of the amendment's provenance record. An author who invokes provenance-honest attribution without prior recovery attempt has produced an under-supported attribution that MUST be either strengthened or omitted.

## 6.8 Provenance recovery

Provenance recovery is the family of substrate-search techniques an author employs to locate the verbatim text of a speech act before invoking provenance-honest attribution. The mechanisms available to authors are constrained by the runtime substrate the platform provides.

**[GR] PLAYBOOK-6.8.1** Before an author invokes historical reconstruction (§6.3.5) or provenance-honest attribution (§6.7.1) for a speech act, the author MUST attempt substrate-recovery of the speech act's verbatim text. Recovery attempts MUST precede reconstruction in every case where verbatim substance is claimed. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4 (recovery-before-reconstruction timeline)]

**[GR] PLAYBOOK-6.8.2** Substrate-recovery MUST search at minimum the `ChatConversation` rows for the relevant time window, the workspace deliverable content field for the relevant workspace and deliverable class, and the git commit history for the relevant repository files. Additional substrates MAY be searched when the speech act is expected to reside in them. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4 (successful recovery from `ChatConversation` pin `pa-e308b1e6dcd444d2` turn 5 at 2026-07-08 08:30:20 UTC and unsuccessful search for the reconciling directive)]

**[GR] PLAYBOOK-6.8.3** The substrate-recovery attempt MUST be recorded in the amendment provenance record. The record MUST identify the search method, the substrate locations queried, and the timestamp at which the search was performed. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4 (search timeline records substrate + timestamp)]

**[GR] PLAYBOOK-6.8.4** If substrate-recovery returns no verbatim match after searching every required substrate location, the author MUST explicitly declare the provenance unrecoverable. The author MUST cite the exhaustion of substrate locations in the amendment provenance record. Declarations of unrecoverability without cited exhaustion MUST NOT be treated as satisfying §6.7.4. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4]

> **Commentary:** The recovery discipline is asymmetric by design. Speech acts that occurred in platform substrate that the author has queryable access to (chat conversations, workspace deliverables, git history) MUST be searched. Speech acts that occurred in platform substrate the author cannot access (external services, transient session state, verbal exchanges) MAY be declared unrecoverable without exhaustive search, provided the declaration explains the reason substrate is unavailable. The 0199 SIGN cycle established the asymmetric pattern: `ChatConversation` rows were searched exhaustively because they were queryable; the reconciling directive delivered outside chat substrate was declared unrecoverable without further search.

## 6.9 Reconciliation with `docs/_provenance.json`

The platform hosts a corpus-tracking system at `docs/_provenance.json` that classifies documents in the `/docs/` corpus into four confidence tiers (HIGH, MEDIUM, LOW, UNKNOWN). PIC-10's five-class content provenance taxonomy (§6.3) and the corpus-tracking system serve different purposes and coexist independently.

**[GR] PLAYBOOK-6.9.1** The Provenance Classification Standard defined in §6.3 through §6.6 is the sole authoritative classification for citations within the Playbook body and for citations within any workspace-canonical ratification record produced under the Playbook's amendment discipline. Alternative classification systems MUST NOT be substituted for PIC-10 within these substrates. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification (PIC-10 established as authoritative classification for governance-artifact provenance); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (PIC-10 codified as the classification standard for governance envelopes)]

**[EP] PLAYBOOK-6.9.2** The `docs/_provenance.json` corpus-tracking system remains authoritative for its own scope — the confidence classification of documents in the broader `/docs/` corpus. Amendments to `_provenance.json` MUST NOT be treated as reclassifying citations governed by PIC-10 within the Playbook body. [E5: `docs/_provenance.json` `_meta.command = build_docs_provenance` (evidence of the system maintaining its own scope); E5: `docs/_provenance.json` `_meta.excludes = ['docs/archive/', 'docs/docs-pattern/']` (evidence of scope boundaries maintained by the tracking system itself); E3: 2714 constitutional_ecosystem_inventory.md §17.1 Amendment D (integration of _provenance.json HIGH/MEDIUM/LOW/UNKNOWN classification with PIC-10 5-class taxonomy — "the two systems coexist independently") — part of the convergent 2708-2714 research chain per manifest §2.3]

**[EP] PLAYBOOK-6.9.3** Bidirectional mapping between the PIC-10 five-class content provenance taxonomy and the `docs/_provenance.json` four-tier confidence system is NOT REQUIRED. The two systems answer different questions — PIC-10 classifies the nature of a citation's underlying source; `_provenance.json` classifies the platform's confidence in the tracked document as a whole — and MAY evolve independently. [E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §17.1 Amendment D (design decision that PIC-10 and `_provenance.json` co-exist independently); E5: `docs/_provenance.json` `_meta.schema_version = 1` (evidence that the tracking system versions its own schema independently)]

> **Commentary:** Two independent classification systems is not a governance defect; it is a recognition that different questions require different vocabularies. PIC-10 asks "what kind of evidence does this citation invoke?" The corpus-tracking system asks "how confident is the platform in this document's stated attribution?" A single document may carry HIGH corpus-tracking confidence while its citations invoke a mix of verified primary evidence, historical reconstruction, and engineering conclusion. The two views do not compete; they refract the same substrate through different lenses.

## 6.10 Verification of provenance

Verification is the discipline of establishing, before an amendment is dispatched to SIGN, that every rule in the amendment satisfies its evidence admission threshold, that every citation resolves, and that the amendment's provenance is coherent. Verification is a joint responsibility split between the author and the SIGN reviewer.

**[GR] PLAYBOOK-6.10.1** Before an amendment to the Playbook is dispatched to SIGN, the author MUST run the eight-check verification protocol enumerated below. The verification result MUST be recorded in the amendment provenance. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger summary (verification recorded as part of the ratification act); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §6 (correction passes 1 and 2 applied following verification-driven findings)]

The eight verifications are the following:

| # | Verification | Responsibility |
|---|---|---|
| 1 | Evidence resolution — every citation resolves to a source enumerated in the frozen evidence manifest | Author |
| 2 | Terminology consistency — every new term defined at first use; no term redefined | Author |
| 3 | Constitutional consistency — no rule contradicts another; chapter dependency discipline preserved | Author |
| 4 | Cross-reference integrity — symbolic anchors and rule identifiers resolve | Author |
| 5 | Citation completeness — every normative sentence carries at least one citation | Author |
| 6 | Version consistency — frontmatter version fields match the proposed amendment | Author |
| 7 | Semantic review — SIGN reviewer confirms the amendment's meaning against ratified prior evidence | SIGN reviewer |
| 8 | SIGN attestation — SIGN reviewer records findings and disposition | SIGN reviewer |

**[GR] PLAYBOOK-6.10.2** The author of an amendment MUST be responsible for verifications 1 through 6. The verification results for these six checks MUST be recorded in the amendment provenance before SIGN is dispatched. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger summary (author-side verification checks recorded); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §4 (Claude-side independent verifier-loop pre-SIGN)]

**[GR] PLAYBOOK-6.10.3** The SIGN reviewer MUST be responsible for verifications 7 and 8. SIGN attestation MUST classify findings as F-BLOCKING, non-blocking, or informational per the SIGN methodology inherited from the Research Operating System. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger summary (SIGN attestation recorded); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (SIGN findings classified F1 BLOCKING, G1 BLOCKING, and non-blocking classes)]

**[GR] PLAYBOOK-6.10.4** If verification 1 identifies a broken citation — a citation whose target does not resolve — the author MUST either repair the citation with a resolving source or omit the rule that depends on the broken source. Broken citations MUST NOT be dispatched to SIGN unresolved. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger summary (correction pass 1 repaired the F1 broken-SHA citation); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §6 (F1 correction: KFI-2 cascade SHA `8acdc6f0` → `5a878768` in three locations)]

**[GR] PLAYBOOK-6.10.5** A SIGN reviewer verifying a rule that cites workspace-canonical E1 or E2 evidence MUST have `deliverable_tool` access provisioned within the SIGN conversation before rendering a verdict on that rule. A verdict rendered without provisioned workspace access MUST be classified as partial pending workspace-provisioned re-verification. [E2: v0.1.0 ratification record body §6 Constitutional debt disposition (deliverable `b083c034-5aba-4dc3-9758-57eba29b4bf2`); E3: `docs/research/platform/platform_constitutional_transition_review.md` (expanded SIGN methodology finding); E6: `docs/handoffs/SESSION_2727_PLAYBOOK_V0_1_0_RATIFIED.md` (CD-49 origin — expanded SIGN pass)]

> **Commentary:** The eight-check protocol is a discipline, not a bureaucracy. Its cost is proportional to the amendment's scope. A PATCH amendment (typo fix, broken-link repair) that touches one rule may complete all six author verifications in minutes. A MAJOR amendment (rule removal, chapter restructuring) that touches many rules requires proportional verification effort. The discipline scales with the amendment; the amendment does not scale with the discipline.

## 6.11 Cross-references

The following cross-references are informative. They aid discovery of related content within and outside the Playbook body.

- Chapter Preamble §Interpretation of Normative Language — defines the RFC 2119 keyword vocabulary that Chapter 6 rules use.
- Chapter Preamble §Reading Conventions — defines the `> **Commentary:**`, `> **History:**`, and related informative-content conventions that Chapter 6 uses.
- Chapter Constitutional Context §The Two Orthogonal Dimensions — establishes canonicality and ratification as the two dimensions this chapter's provenance classification extends.
- Chapter Constitutional Context §Rule Origin Discipline — establishes the principle that Chapter 6 §6.6 operationalizes as evidence admission thresholds.
- Chapter Evolution and Amendment (not yet authored) — will codify the amendment discipline whose 8-check verification protocol is referenced in §6.10.
- `docs/research/platform/engineering_playbook_authoring_protocol.md` §6.1 — the drafting protocol from which Chapter 6's statement-class enumeration is drawn.
- `docs/research/platform/engineering_playbook_authoring_protocol.md` §7.1 — the drafting protocol's per-class evidence admission matrix, which Chapter 6 §6.6 codifies as ratified rules.
- `docs/research/platform/engineering_playbook_evidence_manifest.md` §9 — the frozen evidence set for Chapter 6.
- `docs/research/platform/constitutional_ecosystem_inventory.md` §17.1 Amendment D — the design decision that PIC-10 and `_provenance.json` coexist independently.
- Workspace deliverable `0199_CYCLE_1_CLOSEOUT` (`53756b1c-3867-428b-8003-084604526591`) Appendix D — the verbatim PIC catalog including PIC-10.
- Workspace ratification record `RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT` (`c883ebef-baa7-43c7-a6f0-dd8f3f22106d`) — the governance envelope that ratified PIC-10 as a constitutional discipline.

## 6.12 Extension points

The following extension points are informative. They identify where a future MINOR or MAJOR amendment MAY augment Chapter 6 without renumbering existing rules.

- New content provenance classes — additional classes MAY be added to §6.3 under a MAJOR amendment per PLAYBOOK-6.3.1. Reserved rule identifiers `PLAYBOOK-6.3.7` and beyond are available.
- New statement classes — additional classes MAY be added to §6.4 under a MAJOR amendment per PLAYBOOK-6.4.1. Reserved rule identifiers `PLAYBOOK-6.4.13` and beyond are available.
- New evidence classes — additional classes MAY be added to §6.5 under a MAJOR amendment per PLAYBOOK-6.5.1. Reserved rule identifiers `PLAYBOOK-6.5.9` and beyond are available.
- New per-class evidence thresholds — thresholds for newly-added statement classes MUST be added to §6.6 concurrent with the class addition. Reserved rule identifiers `PLAYBOOK-6.6.13` and beyond are available.
- Alternative recovery substrates — as the platform gains new queryable substrates (for example, structured session-attribution logs), §6.8.2's minimum-substrate list MAY be expanded via a MINOR amendment.
- Tenant-scope reconciliation — should the platform activate multi-tenant governance in a future cycle, §6.9 MAY be extended with tenant-scope provenance classification per a MAJOR amendment.
- Automation of verification — verifications 1 through 6 (§6.10) are candidates for continuous-integration automation. Automation is not codified by Chapter 6; the checks remain author responsibility until the Playbook explicitly ratifies automated substitution.

---

# Chapter 7 — Session Discipline (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-7
**Purpose:** Establish constitutional scope for session-open and session-close discipline as it applies to Playbook authoring sessions.
**Scope:** Every Playbook-authoring session; session-open orientation; session-close handoff production; cascade sequencing at session boundaries.
**Status:** STUB (v0.1). Full content deferred to v0.2+ MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [GR]
**Rule ID range:** PLAYBOOK-7.1.1 through PLAYBOOK-7.3.1

---

## 7.1 Purpose and premise

**[EP] PLAYBOOK-7.1.1** Chapter 7 codifies session discipline by reference to `CLAUDE.md` at the repository root, `00-START-NEXT-SESSION.md` at the repository root, and the handoff corpus under `docs/handoffs/`. This chapter MUST NOT duplicate rules codified in those documents; it references them and identifies their integration with Playbook amendment discipline. [E5: `CLAUDE.md`; E5: `00-START-NEXT-SESSION.md`; E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §2.9]

## 7.2 Substantive discipline

**[GR] PLAYBOOK-7.2.1** A Playbook-authoring session MUST perform session-open orientation before authoring begins. Session-open orientation MUST include reading `00-START-NEXT-SESSION.md`, absorbing `CLAUDE.md` and `MEMORY.md`, and reading the most-recent session handoff. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (session-open orientation exercised across the SIGN sessions); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §2 timeline (`context-kit orient` recorded as the first tool call)]

## 7.3 Extension deferred

**[EP] PLAYBOOK-7.3.1** Full authoring of Chapter 7's constitutional treatment of session discipline is deferred to a future MINOR amendment. Until then, CLAUDE.md, 00-START-NEXT-SESSION.md, and the handoff corpus remain the authoritative sources for session methodology. [E3: 2712 §16.9 (stub-chapter deferral discipline) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 7.4 Cross-references (informative)

- `CLAUDE.md` — session-open contract at repository root.
- `00-START-NEXT-SESSION.md` — per-session priorities.
- `docs/handoffs/` — historical session record.
- Chapter Evolution and Amendment §The Amendment Lifecycle.

## 7.5 Extension points (informative)

- Session-close handoff completeness discipline.
- Session-open orientation extension for cross-repository work.
- Multi-session amendment coordination.
- Session-provenance integration with amendment provenance records.

---

# Chapter 8 — Runtime Discipline (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-8
**Purpose:** Establish constitutional scope for runtime discipline — the executable constitution embedded in platform runtime tables, code paths, and infrastructure files.
**Scope:** Runtime policy rows (CockpitAutopilotPolicy, AgentControlEntry, Budget); PublishGate state machine; canonical_authority derivation and retrieval; continuous integration workflows; cascade rules encoded in ORM.
**Status:** STUB (v0.1). Full content deferred to v0.2+ MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP]
**Rule ID range:** PLAYBOOK-8.1.1 through PLAYBOOK-8.3.1

---

## 8.1 Purpose and premise

**[EP] PLAYBOOK-8.1.1** Chapter 8 codifies runtime discipline by reference to the executable constitution inventory recorded in the Constitutional Ecosystem Inventory. This chapter MUST NOT duplicate the enumeration of runtime policy locations; it references them and identifies their integration with Playbook amendment discipline. [E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §5; E3: `docs/research/platform/platform_constitutional_architecture.md` §2.4]

## 8.2 Substantive discipline

**[EP] PLAYBOOK-8.2.1** The distinction between documentary constitution (rules recorded in ratified documents) and executable constitution (rules enforced by runtime data or code) MUST be preserved. Amendments to the Playbook MUST NOT purport to reclassify executable constitutional artifacts as documentary constitutional artifacts, and MUST NOT purport to reclassify documentary constitutional artifacts as executable constitutional artifacts, without an explicit MAJOR amendment. [E3: `docs/research/platform/platform_constitutional_architecture.md` §2.4; E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §5]

## 8.3 Extension deferred

**[EP] PLAYBOOK-8.3.1** Full authoring of Chapter 8's constitutional treatment of runtime discipline is deferred to a future MINOR amendment. Until then, the Constitutional Ecosystem Inventory §5 remains the authoritative enumeration of executable constitution categories. [E3: 2712 §16.9 (stub-chapter deferral discipline) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 8.4 Cross-references (informative)

- Constitutional Ecosystem Inventory (`docs/research/platform/constitutional_ecosystem_inventory.md`) §5.
- Platform Constitutional Architecture (`docs/research/platform/platform_constitutional_architecture.md`) §2.4.
- `.github/workflows/repo-guardrails.yml` — continuous integration enforcement.
- `core/services/docs_context_builder.py` — runtime docs injection service.

## 8.5 Extension points (informative)

- Runtime policy amendment discipline (as distinct from Playbook amendment).
- CI workflow amendment discipline.
- Executable constitution audit trail integration.
- Runtime docs injection contract stability.

---

# Chapter 9 — Recovery Playbooks (stub)

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-9
**Purpose:** Establish constitutional scope for recovery discipline in response to known incident classes. Reference the recovery-labeled MEMORY rules.
**Scope:** Recovery procedures for worker instability, cascade failure, ratification defects, and provenance-recovery failure.
**Status:** STUB (v0.1). Full content deferred to v0.2+ MINOR amendments.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP]
**Rule ID range:** PLAYBOOK-9.1.1 through PLAYBOOK-9.2.1

---

## 9.1 Purpose and premise

**[EP] PLAYBOOK-9.1.1** Chapter 9 codifies recovery discipline by reference to the recovery-labeled MEMORY rules at `MEMORY.md` in the repository root. This chapter MUST NOT duplicate the recovery rules codified in MEMORY.md; it references them and identifies their integration with Playbook amendment discipline. [E5: `MEMORY.md`; E3: 2712 §16.9 (stub chapters reference authoritative sources rather than duplicating them) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 9.2 Extension deferred

**[EP] PLAYBOOK-9.2.1** Full authoring of Chapter 9's constitutional treatment of recovery discipline is deferred to a future MINOR amendment when specific recovery procedures require constitutional codification. Until then, MEMORY.md remains the authoritative source for recovery patterns. [E3: 2712 §16.9 (stub-chapter deferral discipline) — part of the convergent 2708-2714 research chain per manifest §2.3]

## 9.3 Cross-references (informative)

- `MEMORY.md` at repository root — auto-loaded recovery rules.
- Chapter Provenance Classification §Provenance-Honest Attribution and §Provenance Recovery.
- Chapter Evolution and Amendment §The Amendment Lifecycle Stage 4 Correct.

## 9.4 Extension points (informative)

- Worker instability recovery codification.
- Cascade failure recovery codification.
- Ratification defect recovery codification.
- Provenance-recovery failure escalation codification.

---

# Chapter 10 — Evolution and Amendment

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-10
**Purpose:** Codify the amendment lifecycle, version semantics, rule identifier discipline, supersession model, retirement mechanism, cross-version compatibility guarantees, ratification sequencing, Canon Registry interaction, and Constitutional Debt handling for the Engineering Playbook.
**Scope:** Every amendment to the Playbook body, every version transition, every rule addition, modification, retirement, or supersession, and every interaction between the Playbook and the Canon Registry.
**Introduced in:** v0.1.0
**Last substantive change:** v0.1.0
**Evidence anchor:** `docs/research/platform/engineering_playbook_evidence_manifest.md`
**Statement classes present:** [EP], [GR]
**Rule ID range:** PLAYBOOK-10.1.1 through PLAYBOOK-10.13.4

---

## 10.1 Purpose and premise

The Engineering Playbook is expected to evolve across many versions. Chapter 10 codifies the discipline by which every evolution is proposed, reviewed, ratified, and preserved. Every amendment to any Playbook rule is subject to the discipline in this chapter, including future amendments to this chapter itself.

**[EP] PLAYBOOK-10.1.1** Chapter 10 is the authoritative source for the amendment discipline that governs the Playbook. Every amendment to any Playbook rule MUST follow the discipline codified in this chapter. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §8-§10; E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §11-§12]

**[EP] PLAYBOOK-10.1.2** The amendment discipline codified in Chapter 10 applies uniformly to every chapter of the Playbook body, including Chapter 10 itself. Future amendments to Chapter 10 MUST invoke this chapter's own lifecycle to accomplish the amendment. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §8.7 (bootstrap paradox handling)]

**[GR] PLAYBOOK-10.1.3** The System Owner is the sole ratifier of Playbook amendments. No amendment MAY be considered ratified without an explicit System Owner Directive recorded in the workspace ratification record for that amendment. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification directive verbatim; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §7]

> **Commentary:** The bootstrap intent codified in PLAYBOOK-10.1.2 is intentional. Chapter 10 governs its own future amendments through the same lifecycle it defines for other chapters. This is not circular authority; the amendment discipline is stable, and applying it to itself simply means Chapter 10 uses its own rules to change its own rules. The stability is enforced by the immutability of ratified prior versions, not by external authority.

## 10.2 The amendment lifecycle

Every amendment progresses through six sequential stages: Propose, Author, SIGN, Correct, Ratify, and Mirror. Each stage has entry criteria, exit criteria, and role assignment.

| Stage | Trigger | Executor | Exit criterion |
|---|---|---|---|
| 1. Propose | System Owner Directive or author-initiated proposal | System Owner or author | Written proposal exists; System Owner acknowledges |
| 2. Author | Approved proposal | Author (Claude, Rigby, or human contributor) | Amendment PR authored with evidence citations |
| 3. SIGN | Authored PR ready for review | SIGN reviewer | SIGN report produced with findings classification |
| 4. Correct | SIGN identifies BLOCKING findings | Author, System Owner adjudicates | All BLOCKING findings resolved |
| 5. Ratify | SIGN passes; System Owner Directive | System Owner via `content_tool.content_complete` | Workspace ratification record created; git tag applied |
| 6. Mirror | Ratification complete | Cascade automation | RAG updated; anchors refreshed; Canon Registry updated |

**[GR] PLAYBOOK-10.2.1** Every Playbook amendment MUST progress through the six stages defined in the preceding table in sequential order. Skipping stages is prohibited. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §8; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §2 timeline (which records the six-stage progression exercised for the 0199 ratification)]

**[GR] PLAYBOOK-10.2.2** Stage 1 (Propose) MUST produce a written proposal identifying the intended amendment, the version bump class (PATCH, MINOR, or MAJOR), and the evidence sources on which the proposed rules will rely. The proposal MAY be authored as a workspace deliverable in `status='draft'` or as a research document under `docs/research/platform/`. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (Stage 1 exercised by Chris directive to begin SIGN); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §2 (proposal-to-SIGN progression)]

**[GR] PLAYBOOK-10.2.3** Stage 2 (Author) MUST produce an amendment PR on a branch of the form `playbook/vX.Y.Z-<slug>`. The PR MUST modify the Playbook body file, MUST update the evidence index sidecar, and MUST include a version bump justification in the PR description. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (author-side correction pass exercised); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §6 (corrections delta ledger records author-side work)]

**[GR] PLAYBOOK-10.2.4** Stage 3 (SIGN) MUST produce a SIGN report classifying findings as F-BLOCKING, non-blocking, or informational per Chapter Provenance Classification §Verification of Provenance. The SIGN report MUST be attached to the amendment PR. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger (SIGN cycle documented); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (SIGN findings table)]

**[GR] PLAYBOOK-10.2.5** Stage 4 (Correct) is conditional. If SIGN identifies F-BLOCKING findings, the author MUST apply corrections until every F-BLOCKING finding is resolved. Correction passes MAY require re-SIGN of the corrected content. Amendments with unresolved F-BLOCKING findings MUST NOT proceed to ratification. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (correction passes 1 and 2 exercised); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §6 (correction passes 1 and 2 delta ledgers)]

**[GR] PLAYBOOK-10.2.6** Stage 5 (Ratify) requires an explicit System Owner Directive authorizing ratification. The System Owner Directive MUST be preserved verbatim in the workspace ratification record body. The ratification act itself MUST be performed via `content_tool.content_complete` on the ratification record deliverable. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification directive verbatim + §Ratification ledger summary; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §7 (ratification ledger)]

**[GR] PLAYBOOK-10.2.7** Stage 6 (Mirror) MUST run the four-step documentation cascade defined in Chapter Documentation Cascade, MUST update the Playbook's Canon Registry entry per §10.12, and MUST refresh runtime-injected anchor documents (`CLAUDE.md`) that reference the Playbook version. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Post-ratification actions (cascade completion recorded); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §11 (open work references cascade)]

> **History:** The six-stage lifecycle was exercised in full during Session 2707 to ratify workspace deliverable `0199_CYCLE_1_CLOSEOUT`. The timeline recorded in SESSION_2707 §2 documents each stage's entry and exit, and the ratification record `c883ebef-…` §Post-ratification actions records the Stage 6 mirror activities.

## 10.3 Version semantics

The Playbook uses semantic versioning (`vMAJOR.MINOR.PATCH`) in which bump semantics are determined by *rule change*, not by text change or elapsed time.

**[GR] PLAYBOOK-10.3.1** The Playbook's version identifier MUST take the form `vMAJOR.MINOR.PATCH` where each component is a non-negative integer. Version identifiers MUST appear in the Playbook body frontmatter under the `version` field. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §5.1 (frontmatter schema) + §7 (semver strategy); E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger summary (versioned artifacts exercised)]

**[GR] PLAYBOOK-10.3.2** Every amendment PR MUST declare its intended version bump (PATCH, MINOR, or MAJOR) in the PR description under a section titled "Playbook version bump justification." The justification MUST cite the specific §10.4, §10.5, or §10.6 rule triggering the bump. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §11.3; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Post-ratification actions (versioned ratification exercised)]

**[GR] PLAYBOOK-10.3.3** The Playbook's version bump class MUST reflect the strongest applicable trigger. If a proposed amendment includes both PATCH-triggering and MINOR-triggering changes, the amendment is a MINOR. If a proposed amendment includes MINOR-triggering and MAJOR-triggering changes, the amendment is a MAJOR. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7]

## 10.4 PATCH amendments

A PATCH amendment carries no rule change. Its scope is limited to corrections, clarifications, and non-normative adjustments.

**[GR] PLAYBOOK-10.4.1** A PATCH amendment MUST NOT introduce, modify, remove, or reclassify any rule. PATCH amendments are limited to typographical corrections, broken citation repairs, autogen section refreshes, and clarifying examples that do not introduce new normative content. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.1; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Corrections (correction pass 2 example — count-consistency updates without rule change)]

**[GR] PLAYBOOK-10.4.2** A PATCH amendment MAY be dispatched to a lightweight SIGN cycle at the System Owner's discretion. When the System Owner waives SIGN for a PATCH amendment, the waiver MUST be recorded verbatim in the amendment's workspace ratification record. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §18.6 (lightweight verification for PATCH); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (SIGN discipline exercised, defining what waiver would depart from)]

**[GR] PLAYBOOK-10.4.3** A PATCH amendment MUST preserve backward compatibility. A reader observing behavior against Playbook `v1.0.0` MUST observe identical behavior against `v1.0.1`, `v1.0.2`, and every subsequent PATCH within the same MINOR line. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.1; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Post-ratification actions (immutability guarantee exercised on ratified content)]

**[GR] PLAYBOOK-10.4.4** A PATCH amendment MUST NOT modify the Playbook's stated compatibility declarations in frontmatter. Compatibility changes are MINOR at minimum. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §5.1 (frontmatter schema); E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification ledger summary]

## 10.5 MINOR amendments

A MINOR amendment adds new normative content in a backward-compatible manner. Existing rules retain their meaning; new rules extend or augment.

**[GR] PLAYBOOK-10.5.1** A MINOR amendment MAY introduce new rules, new sub-sections within existing sections, new chapters into reserved slots, new evidence classes, new statement classes, new content provenance classes, or clarify existing rules without changing their behavior. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.2; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification (PIC-10 addition exercised as a MINOR-scale extension)]

**[GR] PLAYBOOK-10.5.2** A MINOR amendment MUST NOT remove any existing rule. A MINOR amendment MUST NOT modify the behavior of any existing rule. Rules that appear altered by a MINOR amendment MUST NOT change their downstream applicability. [E3: 2712 §7.2; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification]

**[GR] PLAYBOOK-10.5.3** A MINOR amendment MUST progress through a full SIGN cycle per the SIGN discipline codified in Chapter Research Methodology. Lightweight SIGN is permitted only for PATCH amendments. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (full 4-batch SIGN cycle exercised for MINOR-scope content); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (SIGN findings table exercising the discipline)]

**[GR] PLAYBOOK-10.5.4** A MINOR amendment MUST preserve backward compatibility at the rule level. A reader relying on rules ratified in Playbook `v1.0.0` MUST observe those same rules in effect in `v1.1.0` and every subsequent MINOR within the same MAJOR line. New rules introduced by the MINOR amendment need not be observed by readers targeting the prior MINOR. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.2; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Post-ratification actions (immutability guarantee)]

## 10.6 MAJOR amendments

A MAJOR amendment introduces breaking change. Existing rules MAY be removed, replaced, or reclassified. Existing chapters MAY be reorganized.

**[GR] PLAYBOOK-10.6.1** A MAJOR amendment MAY remove existing rules, replace existing rules with different-behavior rules, reorganize chapter structure, or make any other change that is not backward-compatible at the rule level. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.3; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Timeline (which records that rule removal has not yet been exercised at Cycle 1A scope; MAJOR discipline is prospectively codified)]

**[GR] PLAYBOOK-10.6.2** A MAJOR amendment MUST include an explicit rationale in the amendment PR description explaining what backward-compatibility guarantee is being broken, why the break is necessary, and what migration guidance applies to consumers of the prior version. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.3; E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §11.2 (MAJOR triggers)]

**[GR] PLAYBOOK-10.6.3** A MAJOR amendment MUST progress through a full SIGN cycle with heightened adversarial scrutiny. The SIGN cycle for a MAJOR amendment SHOULD run at least three adversarial batches. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §18.5; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5 (4-batch SIGN exercised for the smaller 0199 scope, establishing the discipline for larger scopes)]

**[GR] PLAYBOOK-10.6.4** A MAJOR amendment MAY declare that specific rules ratified in prior versions are superseded per §10.8, retired per §10.9, or relocated per §10.7. The declarations MUST appear both in the amendment PR description and in the amendment's ratification record body. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §10 (supersession model); E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Provenance Classification]

**[GR] PLAYBOOK-10.6.5** A MAJOR amendment MUST NOT retroactively invalidate artifacts ratified under prior Playbook versions. Prior ratifications remain valid for the artifacts they covered; MAJOR-scoped rule changes apply prospectively to future artifacts. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §10.3; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Immutability (immutability guarantee applies to prior ratifications regardless of subsequent MAJOR amendments)]

## 10.7 Rule identifiers

Every normative rule in the Playbook body carries a stable rule identifier. Identifier stability is load-bearing: cross-references and downstream citations depend on identifiers not moving.

**[GR] PLAYBOOK-10.7.1** Every normative rule MUST carry an identifier of the form `PLAYBOOK-N.M.K` where `N` is the chapter number of the chapter under which the rule was originally ratified, `M` is the section number under which the rule was originally ratified, and `K` is a monotonically-increasing integer assigned when the rule enters the Playbook body. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §9.1]

**[GR] PLAYBOOK-10.7.2** Rule identifiers MUST NOT change once the rule is ratified. Chapter renumbering, section restructuring, and chapter title changes MUST NOT alter existing rule identifiers. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §9.2]

**[GR] PLAYBOOK-10.7.3** A rule identifier records the chapter and section under which the rule was *originally* ratified. After a MAJOR amendment that restructures chapters or splits sections, existing rules retain their original identifiers even when they physically appear under a different section number. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.3; E3: `docs/research/platform/playbook_authoring_validation_and_chapter6_preparation.md` §2.1]

**[GR] PLAYBOOK-10.7.4** Cross-references from one rule to another SHOULD use the target rule's identifier rather than the target's section number. Section numbers are subject to restructuring; rule identifiers are stable. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §9.5; E3: `docs/research/platform/playbook_authoring_validation_and_chapter6_preparation.md` §2.1]

**[GR] PLAYBOOK-10.7.5** New rules within a section MUST be assigned the next unused integer in the section's rule identifier sequence. Gaps in the sequence — from prior deletions or from earlier rules moving to different physical locations after restructuring — MUST NOT be filled by newly-authored rules. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §9.3]

**[GR] PLAYBOOK-10.7.6** A retired rule identifier MUST NOT be reassigned to a new rule. Retired identifiers persist in the Retired Rules Registry per §10.9. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §9.3, §9.4]

> **Commentary:** The distinction in PLAYBOOK-10.7.3 between "originally ratified section" and "physical location" is essential. When Chapter 4 is restructured in a MAJOR amendment, rule `PLAYBOOK-4.2.1` retains its identifier even if the physical section it appears under is renumbered to `4.3` in the amended chapter. Readers use the identifier to reference the rule; the physical section number is a rendering convenience.

## 10.8 Rule supersession

Supersession is the mechanism by which one rule takes the place of another. Both rules retain their identifiers; the superseded rule is preserved as historical record.

**[GR] PLAYBOOK-10.8.1** A rule is *superseded* when a MAJOR amendment ratifies a replacement rule that provides different-behavior guidance in the same scope as the original rule. Supersession applies only within a MAJOR amendment; MINOR and PATCH amendments MUST NOT cause supersession. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §10; E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §12]

**[GR] PLAYBOOK-10.8.2** A superseded rule MUST have its status changed to *superseded* in the Playbook body. The superseding rule MUST cite the superseded rule by identifier under the citation form `[supersedes PLAYBOOK-N.M.K]`. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §12.1]

**[GR] PLAYBOOK-10.8.3** The superseded rule's original text MUST remain in the Playbook body under a `> **Superseded:**` blockquote convention that identifies the superseding rule and the amendment version in which supersession occurred. The superseded rule's original identifier MUST NOT be removed from the corpus. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §12.1]

**[GR] PLAYBOOK-10.8.4** Supersession is prospective. Artifacts ratified under the superseded rule remain valid; new artifacts MUST comply with the superseding rule. Retroactive application requires an explicit System Owner Directive recorded in the amendment ratification record. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §10.3; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Immutability]

## 10.9 Rule retirement

Retirement is the mechanism by which a rule is removed from active application. The rule's identifier persists in the Retired Rules Registry; the rule's text remains available as historical record.

**[GR] PLAYBOOK-10.9.1** A rule is *retired* when a MAJOR amendment ratifies its removal from active application without providing a superseding rule. Retirement applies only within a MAJOR amendment; MINOR and PATCH amendments MUST NOT cause retirement. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §12; E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §7.3]

**[GR] PLAYBOOK-10.9.2** A retired rule MUST have its status changed to *retired* in the Playbook body. The retirement MUST cite the amendment version in which retirement occurred and MUST cite the rationale under a `> **Retired:**` blockquote. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §12.1]

**[GR] PLAYBOOK-10.9.3** A retired rule's identifier and original text MUST be recorded in the Retired Rules Registry, which lives in an appendix or a dedicated file discoverable from the Playbook. Retired identifiers MUST NOT be reused for new rules. [E3: `docs/research/platform/engineering_playbook_authoring_protocol.md` §9.4]

**[GR] PLAYBOOK-10.9.4** Retired rules MUST retain historical validity for artifacts ratified under them. Retirement MUST NOT remove the rule from historical applicability; retirement only removes the rule from prospective application. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Immutability (immutability guarantee applies to artifacts ratified under superseded/retired rules); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §5]

## 10.10 Cross-version compatibility

The Playbook makes explicit compatibility declarations in each version's frontmatter. Readers rely on these declarations to determine whether their tooling and ratifications remain valid across version transitions.

**[GR] PLAYBOOK-10.10.1** Every Playbook version MUST declare its compatibility posture in the frontmatter field `compatible_with`. The declaration MUST enumerate the specific prior versions, ADRs, ratification records, and peer constitutional documents with which the current version is compatible. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §5.1 (frontmatter schema); E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §5.2 (compatible_with field rationale)]

**[GR] PLAYBOOK-10.10.2** Backward compatibility means that behavior expected against a prior Playbook version remains observable against the current version at the rule level. A PATCH or MINOR amendment MUST preserve backward compatibility. A MAJOR amendment MAY break backward compatibility subject to the rationale rule in §10.6.2. [E3: 2712 §7]

**[EP] PLAYBOOK-10.10.3** Forward compatibility is not guaranteed. A reader targeting Playbook version `v1.0.0` MUST NOT assume that behavior in a future version will be identical, even under a PATCH bump. Forward-looking rules (Extension Points sections) inform authors about probable future evolution but do not constitute forward-compatibility guarantees. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §16 — part of the convergent 2708-2714 research chain per manifest §2.3]

## 10.11 Ratification sequencing

Ratification produces multiple coordinated artifacts: a merged commit, an annotated git tag, a workspace ratification record, and a documentation cascade. The sequence in which these artifacts are produced is load-bearing.

**[GR] PLAYBOOK-10.11.1** Ratification MUST begin with an explicit System Owner Directive authorizing the ratification act. The directive MUST be captured verbatim before any ratification artifact is produced. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Ratification directive verbatim; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §7]

**[GR] PLAYBOOK-10.11.2** After the System Owner Directive is captured, the ratification sequence MUST proceed: merge the amendment PR to `main`; apply an annotated git tag of the form `playbook-vX.Y.Z` to the merge commit; create the workspace ratification record deliverable; fire `content_tool.content_complete` on the ratification record; run the four-step documentation cascade; update the Canon Registry entry; refresh runtime-injected anchor documents. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Post-ratification actions; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §7 (ratification ledger summary)]

**[GR] PLAYBOOK-10.11.3** The workspace ratification record body MUST name the ratified Playbook version, the git tag, the commit SHA, the verbatim System Owner Directive, and the parent ratification record identifier (or `null` for the inaugural version). [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §14; E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT (which itself demonstrates the required fields)]

**[GR] PLAYBOOK-10.11.4** Frontmatter fields that cannot be populated until after the merge commit exists — specifically `commit_sha`, `git_tag`, `ratification_record.deliverable_id`, `ratified_date`, and `ratifier` — MAY be populated in a follow-up commit tagged `playbook-vX.Y.Z-frontmatter`. The follow-up commit MUST reference the primary ratification tag. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §8.6 (post-ratification frontmatter fill mechanism)]

**[EP] PLAYBOOK-10.11.5** Ratification MUST be treated as complete only when the workspace ratification record's `status` field is `completed` (via PublishGate transition) AND the git tag has been applied to the merge commit. Partial completion of the ratification sequence MUST NOT be treated as ratification. [E3: 2712 §15.1 (two-commit ratification pattern) — part of the convergent 2708-2714 research chain per manifest §2.3; E5: `content_tool.content_complete` (PublishGate transition mechanism); E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT `status` field]

## 10.12 Canon Registry interaction

The Playbook is included in the Canon Registry maintained at `docs/canon/INDEX.md`. Every ratified Playbook version MUST be reflected in the Registry.

**[GR] PLAYBOOK-10.12.1** Every ratified Playbook version MUST have an entry in the Canon Registry under the Operational Canon section. The entry MUST include a pointer to the Playbook body at its repository path, the version, the git tag, and the ratification date. [E5: `docs/canon/INDEX.md` §Canon Registry (Registry structure); E3: `docs/research/platform/constitutional_ecosystem_inventory.md` §17.1 Amendment F]

**[GR] PLAYBOOK-10.12.2** The Canon Registry entry for the Playbook MUST be added, updated, or renewed as part of every ratification's Stage 6 mirror. The update MUST occur before the ratification is considered fully mirrored. [E3: `docs/research/platform/engineering_playbook_architecture_specification.md` §8; E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §7]

**[EP] PLAYBOOK-10.12.3** The Canon Registry MUST NOT hold the Playbook body itself. The Registry contains a pointer to the body at its repository path. The body remains at `docs/ENGINEERING_PLAYBOOK.md`. [E5: `docs/canon/INDEX.md` §Canon Registry (documents live at original paths); E3: 2712 §6.1 — part of the convergent 2708-2714 research chain per manifest §2.3]

## 10.13 Constitutional Debt handling

The Constitutional Debt Register records items intentionally deferred by prior authoring sessions. It is a shared reference between authors and reviewers.

**[GR] PLAYBOOK-10.13.1** The Constitutional Debt Register MUST be maintained as a running record of items intentionally deferred from ratified Playbook content. Each debt entry MUST include a unique identifier of the form `CD-NN`, a description, a rationale for deferral, an earliest version at which the item is eligible for resolution, and a blocking status. [E2: RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT §Post-ratification actions (evidences deferred-item tracking discipline); E6: `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` §11 open work section (evidences the debt-tracking pattern)]

**[GR] PLAYBOOK-10.13.2** New debt entries MUST be appended to the Register. Existing debt entries MUST NOT be modified or renumbered. A debt entry that is resolved MUST have its resolution recorded as an addendum to the entry, not by editing the original entry text. [E3: `docs/research/platform/playbook_authoring_session_2719.md` §8]

**[GR] PLAYBOOK-10.13.3** A debt entry marked as blocking for a specific version MUST be resolved before that version is ratified. A debt entry marked as non-blocking MAY be resolved in the specified earliest-eligible version or later, at the author's discretion. [E3: `docs/research/platform/playbook_authoring_session_2719.md` §8 (CD-15 example: blocking for v0.1 ratification)]

**[EP] PLAYBOOK-10.13.4** Resolution of a debt entry MUST occur through the amendment lifecycle. Debt entries are candidates for future amendments; they do not carry independent authority. [E3: 2713 §11 — part of the convergent 2708-2714 research chain per manifest §2.3; E3: `docs/research/platform/playbook_authoring_session_2719.md` §8]

> **Commentary:** The Constitutional Debt Register is a bridge between the authoring sessions and future amendments. It records deferrals that are architecturally intentional (not implementation defects) and gives future authors and reviewers a shared reference for what has been consciously left for later.

## 10.14 Cross-references

- Chapter Preamble §Interpretation of Normative Language.
- Chapter Constitutional Context §Rule Origin Discipline.
- Chapter Provenance Classification §Statement Classification.
- Chapter Provenance Classification §Evidence Admission Standard.
- Chapter Provenance Classification §Verification of Provenance.
- Chapter Research Methodology (stub in v0.1; SIGN discipline codified there).
- Chapter Documentation Cascade (stub in v0.1; four-step cascade codified there).
- `docs/research/platform/engineering_playbook_architecture_specification.md` §7–§10, §14.
- `docs/research/platform/engineering_playbook_authoring_protocol.md` §9, §11–§12, §18.
- `docs/research/platform/playbook_authoring_session_2719.md` §8 (Constitutional Debt Register).
- Workspace deliverable `RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT` (`c883ebef-baa7-43c7-a6f0-dd8f3f22106d`) — the primary exemplar of the amendment lifecycle applied to a substantive scope.
- `docs/handoffs/SESSION_2707_0199_RATIFICATION_HANDOFF.md` — the session handoff documenting the amendment lifecycle in operation.

## 10.15 Extension points

- Ratifier delegation MAY be codified in a future MAJOR amendment when Cycle 3 or later activates additional constitutional layers. This chapter presupposes a single System Owner.
- Cross-repository amendment coordination MAY be codified in a future MAJOR amendment when the fleet-scope constitutional layer is activated.
- Automated version bump validation MAY be codified as a future extension. This chapter presupposes manual version bump justification per §10.3.2.
- Emergency amendment procedures MAY be codified in a future MAJOR amendment. This chapter presupposes that no fast-path exists for MAJOR amendments and that operational directives requiring rapid change live in `CLAUDE.md` and `MEMORY.md` rather than in the Playbook.
- Automated Retired Rules Registry generation MAY be codified as a future extension. This chapter presupposes the Registry is a manually-maintained appendix or file.

---

# Appendix A — Evidence index sidecar reference

**Evidence index sidecar:** `docs/research/playbook/evidence_index_v0_1_0.md` (to be created in a follow-up MINOR amendment or PATCH). For v0.1.0, citations reference the frozen evidence manifest at `docs/research/platform/engineering_playbook_evidence_manifest.md` directly.

---

# Appendix D — Version chain

| Version | Parent version | Supersedes | Ratification date | Git tag | Notes |
|---|---|---|---|---|---|
| v0.1.0 | null | [] | PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION | PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION | Inaugural version. |
| v0.2.0 | v0.1.0 | [] | 2026-07-09 | playbook-v0.2.0 | MINOR — codify R1/R2/R3 EOS rules as PLAYBOOK-5.2.2 (Tool Autonomy), PLAYBOOK-2.2.2 (CDR discipline), PLAYBOOK-3.2.2 (Acceptance-tests-first). |
| v0.3.0 | v0.2.0 | [] | PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION | PLACEHOLDER_TO_BE_FILLED_POST_RATIFICATION | MINOR — codify CD-48 (catalog admission) as PLAYBOOK-6.6.14 and CD-49 (SIGN workspace tool provisioning) as PLAYBOOK-6.10.5. Discharges Constitutional Debt CD-48 + CD-49 carried from v0.1.0. |

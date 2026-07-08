# Engineering Playbook Authoring Protocol

**Session:** 2713 (legislative drafting standard for the Engineering Playbook)
**Date:** 2026-07-08
**Status:** Research proposal — awaiting Chris's review
**Predecessors:**
- 2708: `engineering_playbook_architecture_proposal.md`
- 2709: `workspace_architecture_and_constitution_proposal.md`
- 2710: `platform_architecture_workspace_boundary_analysis.md`
- 2711: `platform_constitutional_architecture.md`
- 2712: `engineering_playbook_architecture_specification.md`

**Author:** Claude (Opus 4.7, 1M context)

**Scope constraints per mission:** Design *only* the authoring protocol. Do NOT author Playbook content. Do NOT modify repository beyond this one research document. No ADRs. No workspace deliverables. Repository ends clean (this document + five untracked prior proposals only).

**Architectural inputs assumed accepted:**
- The six-layer constitutional model (2711 §18).
- The Playbook Architecture Specification (2712) as structural blueprint: single file at `docs/ENGINEERING_PLAYBOOK.md`, YAML frontmatter with 12 fields, 10-chapter proposal, semver by rule-change semantics, workspace-canonical ratification envelopes, 6 evidence classes.
- Repo-canonical sibling ecosystem: `docs/adr/ADR-0001..0004`, `docs/research/process/IMPLEMENTATION_OPERATING_SYSTEM.md`, `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`.

**Deliverable:** one document. This one.

---

## 0. How to read this protocol

This protocol is the **legislative drafting standard** for the Engineering Playbook. It governs the *how* of Playbook authoring, distinct from 2712 which governs the *what* (structure). Authors of Playbook chapters — human or AI — MUST consult this protocol before drafting.

Meta-recursion note: this document is itself NOT a Playbook chapter. It is a research proposal for the drafting standard that will be codified into Chapter 10 (Evolution & Amendment) of Playbook v1.0. Once the Playbook adopts this protocol formally (via Chapter 10 codification), the Playbook itself governs the protocol; until then, this document is authoritative.

Read time: dense; ~35 minutes end-to-end. Fast path: §1 (Executive summary) + §5 (RFC-2119 keywords) + §6 (Statement classification) + §7 (Evidence admission) + §22 (Chapter authoring order). Everything else is reference.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Design principles](#2-design-principles)
3. [Constitutional language standards](#3-constitutional-language-standards)
4. [Normative vs informative content](#4-normative-vs-informative-content)
5. [RFC-2119 keyword usage](#5-rfc-2119-keyword-usage)
6. [Constitutional statement classification](#6-constitutional-statement-classification)
7. [Evidence admission standard](#7-evidence-admission-standard)
8. [Writing style](#8-writing-style)
9. [Rule identifiers and stability](#9-rule-identifiers-and-stability)
10. [Section and chapter formatting](#10-section-and-chapter-formatting)
11. [Amendment discipline](#11-amendment-discipline)
12. [Deprecation and historical note handling](#12-deprecation-and-historical-note-handling)
13. [Internal consistency rules](#13-internal-consistency-rules)
14. [Cross-reference discipline](#14-cross-reference-discipline)
15. [Terminology and glossary discipline](#15-terminology-and-glossary-discipline)
16. [AI authoring rules](#16-ai-authoring-rules)
17. [Provenance preservation](#17-provenance-preservation)
18. [Verification strategy](#18-verification-strategy)
19. [Future automation opportunities](#19-future-automation-opportunities)
20. [Pressure test / falsification](#20-pressure-test--falsification)
21. [Risks](#21-risks)
22. [Unknowns](#22-unknowns)
23. [Sufficiency assessment and chapter authoring order](#23-sufficiency-assessment-and-chapter-authoring-order)
24. [Closing](#24-closing)

---

## 1. Executive summary

**Question:** How should the Engineering Playbook be written?

**Answer:** The Playbook is authored under a **legislative drafting protocol** with four load-bearing disciplines:

1. **Language discipline** — RFC-2119 keywords (`MUST`, `SHOULD`, `MAY`, `MUST NOT`, `SHOULD NOT`, `REQUIRED`, `RECOMMENDED`, `OPTIONAL`) carry constitutional weight when capitalized. Lowercase usage is ordinary English. Every normative sentence uses exactly one keyword. Ambiguity is a defect, not a style choice.
2. **Statement classification** — every rule is one of 10 categories (§6): Architectural Constraint, Governance Rule, Operational Rule, Engineering Principle, Implementation Pattern, Repository Standard, Runtime Policy, Recovery Procedure, Documentation Rule, Research Methodology. Category determines evidence threshold and versioning implications.
3. **Evidence discipline** — every normative statement MUST cite ≥1 evidence source from the 6 evidence classes (per 2712 §11). Statements without qualifying evidence are not Playbook-ready.
4. **Stability discipline** — rule identifiers (like `PLAYBOOK-4.2.1`) are stable across versions; chapter numbers are stable; cross-references are symbolic; deprecated rules move to Appendix but retain their IDs. Renumbering is FORBIDDEN.

**Key architectural decisions:**

- Adopt RFC 2119 formally as the normative-language convention. The repository already uses these keywords 71 times across 15 docs but has never cited RFC 2119 by reference — the Playbook is the first ratified artifact to declare the convention.
- Introduce statement-level classification (§6). Every Playbook rule declares its class inline via a small badge (`[AC]`, `[OR]`, `[GR]`, etc.).
- Introduce rule IDs (§9). Every rule has a stable ID surviving amendments. Deleted rules retire their IDs; IDs are never reused.
- Introduce a rule-level evidence threshold matrix (§7). Different statement classes require different evidence strengths.
- Restrict AI-autonomous authoring scope (§16). AI MAY draft; AI MUST NOT ratify. Provenance MUST be preserved.
- Design 8-check verification protocol (§18): evidence / terminology / consistency / cross-reference / citation / version / semantic / SIGN.

**Sufficiency assessment (§23):** yes, this protocol is sufficient to begin Playbook v0.1 authoring in Session 2714. No further architectural work is required.

**Recommended chapter authoring order for v0.1:** Chapter 6 (Provenance) → Chapter 10 (Evolution & Amendment) → Chapter 1 (Constitutional Context) → Chapter 0 (Preamble) — full content. Chapters 2, 3, 4, 5, 7, 8, 9 — stubs with `PENDING` markers.

---

## 2. Design principles

Four principles constrain every downstream decision in this protocol. They are stated here so they can be audited independently.

### 2.1 Machine-parseable is not machine-only

The Playbook MUST be readable by humans first. Machine-parseability (frontmatter, rule IDs, statement badges) is a consequence of clean structure, not a substitute for readable prose. Every downstream rule in this protocol prefers "clear enough that a human can read it AND a lint can check it" over "clear enough for a lint alone."

**Applied consequence:** RFC-2119 keywords appear in prose (`The Playbook MUST cite evidence for every normative statement.`), not just in metadata. A human reads it correctly; a linter parses it deterministically.

### 2.2 Constitutional weight is signaled, not inferred

A reader MUST be able to tell whether a sentence is normative or informative *from the sentence itself*, not from paragraph context. Every normative sentence carries an RFC-2119 keyword; every informative sentence does not.

**Applied consequence:** informative content that *sounds* like a rule but isn't a rule is a defect. Reword to remove the keyword-adjacent phrasing OR promote it to a real rule with a citation.

### 2.3 Evidence-attached or absent

Restated from 2712 §2.2. Zero unattached rules. If evidence does not exist yet, the rule stays in a WIP research doc or a proposal file until evidence catches up. This principle is why chapters may ship as stubs (§23) — a stub with `PENDING` markers is honest; an unattached rule pretending to be ratified is a defect.

**Applied consequence:** every rule in v0.1 has ≥1 citation in the evidence index sidecar. Un-citable rules are omitted or stubbed.

### 2.4 Stability over convenience

Rule IDs, chapter numbers, and symbolic cross-references outlive text amendments. Renaming a chapter is a MINOR bump. Renumbering rules is FORBIDDEN. Amendment work is more expensive than authoring work — design for stability first.

**Applied consequence:** rule ID `PLAYBOOK-4.2.1` in Playbook v1.0 refers to the same conceptual rule in v2.0 even if the surrounding text has been rewritten. Deleted rules retire (their ID goes to an Appendix "Retired Rules" registry) but the ID is never reused.

---

## 3. Constitutional language standards

The Playbook uses **legislative-style English**: precise, active, present-indicative for normative statements; declarative for informative ones. Rules follow.

### 3.1 Statement categories (from mission §1)

The mission enumerated 10 categories for statement types the Playbook contains. This protocol codifies them.

| Category | Marker | Definition | Language shape |
|---|---|---|---|
| Requirement | `[REQ]` | An outcome that MUST be achieved. Non-negotiable. | *"The Playbook body MUST live at `docs/ENGINEERING_PLAYBOOK.md`."* |
| Rule | `[RULE]` | A specific behavior/action MUST or MUST NOT be performed. | *"Rule authors MUST cite ≥1 evidence source per normative statement."* |
| Principle | `[PRIN]` | A high-level engineering value from which rules derive. | *"Evidence-attached or absent."* |
| Recommendation | `[REC]` | SHOULD be followed unless there is a specific reason not to. | *"Amendment PRs SHOULD include a version-bump justification in the description."* |
| Guideline | `[GUIDE]` | MAY be followed; provides suggested defaults. | *"Chapter section headings MAY use the format `Chapter N — Title` for readability."* |
| Example | `[EX]` | Illustrative content only. NOT normative. | *"For example, `PLAYBOOK-4.2.1` refers to Chapter 4, section 2, rule 1."* |
| Commentary | `[NOTE]` | Explanation of a rule's purpose. NOT normative. | *"This rule prevents the drift observed in Sessions 1802 and 2705."* |
| Historical Context | `[HIST]` | Reason a rule exists, referencing specific past events. | *"PIC-10 was surfaced during 0199 SIGN Batch 3 — see 2707 handoff §5."* |
| Informative Note | `[INFO]` | Descriptive content aiding understanding. NOT normative. | *"The Playbook body is stored in Markdown for portability."* |
| Future Work | `[FUTURE]` | Non-binding forward pointer. NOT a rule. | *"Future automation MAY validate frontmatter YAML at commit time — see §19."* |

**Convention:** the marker MAY appear as a small bracketed prefix on the sentence's line. Alternative: statement-class badges collected in the chapter's frontmatter with paragraph anchors. Choice deferred to Playbook v0.1 authoring.

**Rationale:** every sentence in the Playbook can be classified as one of the 10. If a sentence resists classification, it is malformed and MUST be rewritten before ratification.

### 3.2 Distinction: Requirement vs Rule vs Principle

- **Requirement** describes an *outcome or state* that MUST hold. It's non-agentive. Example: *"The Playbook body MUST be repo-canonical."*
- **Rule** describes an *action or behavior* that MUST or MUST NOT be performed by some agent. Example: *"Authors MUST cite evidence in-line."*
- **Principle** describes a *value* from which requirements and rules derive. Example: *"Evidence discipline."* Principles are stated in chapter headers and imply downstream rules; they are not themselves enforceable.

### 3.3 Distinction: Recommendation vs Guideline

- **Recommendation** carries SHOULD-strength normativity. Follow it unless you can justify not following it. Non-compliance requires a documented rationale.
- **Guideline** carries MAY-strength normativity. Follow it as a sensible default. Non-compliance requires no justification.

### 3.4 Distinction: Example vs Commentary vs Informative Note

- **Example** shows how a rule is applied concretely. Purely illustrative.
- **Commentary** explains why a rule exists. Rationale-focused.
- **Informative Note** provides background not tied to a specific rule. Context-focused.

None of these three carry authority. All three MUST be visually distinguishable from normative statements (§8 formatting).

### 3.5 Distinction: Historical Context vs Future Work

- **Historical Context** cites past events (sessions, incidents, prior ratifications) that motivated a current rule. Anchors a rule to observed evidence.
- **Future Work** is a forward-pointer for possible future extensions. Not a rule. Not a commitment.

---

## 4. Normative vs informative content

Every paragraph in the Playbook is either NORMATIVE or INFORMATIVE. There is no in-between.

### 4.1 Normative content

- Contains ≥1 RFC-2119 capitalized keyword (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`, `REQUIRED`, `RECOMMENDED`, `OPTIONAL`, `SHALL`, `SHALL NOT`).
- Classifiable under one of the 10 statement categories.
- Cites ≥1 evidence source (inline or via chapter's evidence anchor).
- Carries a rule ID (see §9).

### 4.2 Informative content

- Contains NO RFC-2119 capitalized keywords (or only in the mode of illustrating another rule).
- Classified as Example, Commentary, Historical Context, Informative Note, or Future Work.
- Cites evidence when helpful but not required.
- Does NOT carry a rule ID.

### 4.3 Mixed content is forbidden

A single paragraph MUST NOT combine normative and informative content. If a paragraph contains a MUST and a "for example", split into two paragraphs.

**Rationale:** downstream verification tools MUST be able to identify normative content unambiguously.

### 4.4 Visual distinction

Normative content and informative content MUST be visually distinguishable in rendered Markdown. Recommended patterns:

- Normative rules use the pattern `**[CLASS] [ID]** Rule text with MUST/SHOULD/MAY.`
- Informative content uses ordinary paragraphs without the bold marker.
- Examples use `> Example:` blockquote prefix.
- Commentary uses `> Commentary:` blockquote prefix.
- Historical context uses `> History:` blockquote prefix.
- Future work uses `> Future:` blockquote prefix.

**Applied consequence:** a reader scanning a chapter can identify all normative content by looking at bolded rule markers and skimming for capitalized RFC-2119 keywords.

---

## 5. RFC-2119 keyword usage

RFC 2119 (a.k.a. BCP 14) defines conventions for the words `MUST`, `SHOULD`, `MAY`, and their negations. The Playbook adopts these formally.

### 5.1 Formal adoption

The Playbook's Chapter 0 (Preamble) MUST include a **normative-language declaration** of the following form:

> The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY, and OPTIONAL in this document are to be interpreted as described in RFC 2119 when, and only when, they appear in all capitals as shown here.

This declaration codifies what is already emerging as practice: 71 uses of these keywords across 15 repo docs today without a formal declaration. Playbook v0.1 is the first ratified artifact to make the convention explicit.

### 5.2 Keyword definitions (adopted from RFC 2119, restated for the Playbook)

| Keyword | Meaning |
|---|---|
| `MUST` / `SHALL` / `REQUIRED` | Absolute requirement. No conforming implementation may deviate. |
| `MUST NOT` / `SHALL NOT` | Absolute prohibition. |
| `SHOULD` / `RECOMMENDED` | Strong recommendation. Deviation requires understanding the full implications and documenting justification. |
| `SHOULD NOT` / `NOT RECOMMENDED` | Strong dissuasion. Deviation requires documented justification. |
| `MAY` / `OPTIONAL` | Truly optional. Neither compliance nor non-compliance carries obligation. |

### 5.3 One keyword per sentence

Every normative sentence uses **exactly one** RFC-2119 keyword. Multiple keywords per sentence create ambiguity about which is authoritative.

**Rationale:** parseability. Verification tools MUST be able to identify the sentence's requirement strength deterministically.

**Example (compliant):** *"The evidence index sidecar MUST enumerate every citation used in the chapter body."*

**Example (non-compliant):** *"The evidence index sidecar MUST be present and SHOULD be reviewed before ratification."* — Split into two sentences.

### 5.4 Keyword capitalization discipline

- Capitalized keyword → constitutional meaning per §5.2.
- Lowercase keyword → ordinary English usage; carries no constitutional weight.

**Example (constitutional):** *"Amendment PRs MUST cite the version bump class."*

**Example (ordinary):** *"Every author must eventually stop editing and commit."* — The lowercase "must" is ordinary emphasis, not a constitutional rule.

**Rationale:** the lowercase-vs-capitalized discipline prevents accidental rule creation from casual prose.

### 5.5 Prohibited synonyms

The following are FORBIDDEN in normative sentences: `has to`, `is required to`, `is expected to`, `needs to`, `it is essential that`, `it is important that`. Use `MUST` instead.

**Rationale:** synonyms erode the parseability discipline.

### 5.6 Passive-voice restriction

Normative sentences SHOULD use active voice with an explicit agent (`Authors MUST cite ...`) rather than passive voice (`Citations MUST be provided`). Passive voice obscures who bears the obligation.

Exception: when the agent is universal (`The Playbook MUST live at ...`), passive is acceptable.

### 5.7 Negative construction discipline

`MUST NOT` and `SHALL NOT` express absolute prohibitions. Do NOT use `MUST NOT` for weaker forms of discouragement — that's `SHOULD NOT`.

**Example (correct):** *"Rule IDs MUST NOT be reused."* — This is an absolute; violating it corrupts the corpus.

**Example (would be wrong):** *"Rules MUST NOT contradict earlier chapters."* — Actually a `MUST` positive: *"Rules MUST be consistent with earlier chapters."* Or, if truly a prohibition, spell out what "contradict" means concretely.

---

## 6. Constitutional statement classification

The mission requires categorization of Playbook statements. This protocol defines 10 categories with authority, evidence, and versioning attributes.

### 6.1 The 10 statement classes

For each class: purpose, authority level, evidence requirement (mapping to 2712 §11 classes), versioning implications on change.

| # | Class | Marker | Purpose | Authority | Evidence required | Change → semver |
|---|---|---|---|---|---|---|
| 1 | **Architectural Constraint** | `[AC]` | Inviolable structural rule about system architecture. Cannot be violated without breaking the platform's constitutional integrity. | Highest | Ratified ADR (E1) + Ratification record (E2) + Platform evidence (E5) | MAJOR to remove/change |
| 2 | **Governance Rule** | `[GR]` | Rule about how the Playbook itself (or related governance artifacts) is authored/amended/ratified. | Highest | Ratified ADR (E1) OR ratification of this Protocol (E2) + Session handoff (E6) | MAJOR to remove/change |
| 3 | **Operational Rule** | `[OR]` | Day-to-day procedural discipline. How work is done. | High | ≥2 evidence classes; typically Research doc (E3) + Session handoff (E6) or MEMORY.md feedback rule | MINOR to add; MAJOR to remove |
| 4 | **Engineering Principle** | `[EP]` | High-level engineering value from which specific rules derive. | High | Convergent research (E3) across ≥2 arcs OR ratified ADR (E1) | MAJOR to change (removing invalidates derived rules) |
| 5 | **Implementation Pattern** | `[IP]` | Recommended code shape or code discipline. | Medium | Platform evidence (E5) + Session handoff (E6) demonstrating pattern | MINOR to add; MINOR to change; MAJOR to remove |
| 6 | **Repository Standard** | `[RS]` | File structure, naming, layout convention. | Medium | Platform evidence (E5) OR consistent Research doc (E3) reference | MINOR to add; MAJOR to change |
| 7 | **Runtime Policy** | `[RP]` | Executable-constitution rule (e.g., about CockpitAutopilotPolicy, Budget, AgentControlEntry). | High | Platform evidence (E5) + Runtime evidence (E4) | MAJOR to remove |
| 8 | **Recovery Procedure** | `[RC]` | Incident-response playbook. | Medium | ≥1 Session handoff (E6) documenting successful recovery | MINOR to add; MINOR to update; MAJOR to remove |
| 9 | **Documentation Rule** | `[DR]` | Discipline for producing/maintaining docs (cascade, mirror, etc.). | Medium | ≥1 ADR (E1) OR Research doc (E3) + Runtime evidence (E4) | MINOR to add; MAJOR to remove |
| 10 | **Research Methodology** | `[RM]` | Rule about how research is conducted (SIGN, arcs, evidence). | High | Research OS or RAR reference (E3) + Ratification record (E2) | MAJOR to remove/change (research foundation) |

**Applied consequence:** every rule in the Playbook carries its class marker either inline (`[AC] PLAYBOOK-1.2.3` bold prefix) or in the evidence index sidecar. The marker determines evidence-verification depth and amendment permissibility.

### 6.2 Per-class evidence threshold examples

**Architectural Constraint (`[AC]`) — highest evidence bar:**

Example: *"[AC] PLAYBOOK-1.4.1 The Playbook body MUST be repo-canonical per KFI-2. [E1: ADR-0120 §2.1; E5: `content/_canonical_authority_helpers.py:33-60`]"*

- Requires ratified ADR-0120 (E1).
- Requires platform evidence (the code path).
- Optional but recommended: E2 ratification record UUID.

**Operational Rule (`[OR]`) — standard evidence bar:**

Example: *"[OR] PLAYBOOK-4.2.1 Cascade PRs MUST include the embed step. [E3: `docs/research/platform/platform_constitutional_architecture.md §Risks R7`; E6: SESSION_1802 close forensics]"*

- Requires research doc citation.
- Requires session-handoff citation demonstrating the pattern.

**Recovery Procedure (`[RC]`) — evidence-of-successful-recovery bar:**

Example: *"[RC] PLAYBOOK-9.2.3 On Rigby SIGN worker instability at turn 2, retire the pin and mint fresh. [E6: SESSION_1405; MEMORY.md `feedback_rigby_sign_worker_instability_recovery`]"*

- Requires evidence that this pattern has worked before.

### 6.3 Insufficient-evidence cases

A statement fails admission when:

- Only 1 evidence class cited AND the required threshold is ≥2.
- Cited evidence does not exist (broken reference).
- Cited evidence does not substantively support the rule (SIGN-cycle finding).
- Rule is prospective (about a future pattern not yet observed).

**Applied consequence:** insufficient-evidence statements MUST be omitted from the Playbook body. They MAY appear in `docs/research/playbook/proposals/` for future codification.

### 6.4 Evidence class references

Full evidence class definitions live in 2712 §11.1:

- E1: ADR (workspace or repo)
- E2: Ratification record
- E3: Research doc under `docs/research/`
- E4: Runtime evidence (ORM query, DB count)
- E5: Platform evidence (code path with file:line)
- E6: Session handoff

Playbook Chapter 6 (PIC-10 provenance) will further classify each citation as: verified primary evidence, verified repository/runtime fact, verified quoted source, historical reconstruction, or engineering conclusion.

---

## 7. Evidence admission standard

The **admission threshold** is the minimum evidence required before a statement earns constitutional status.

### 7.1 Per-class admission matrix

| Statement class | Min evidence sources | Required classes | Optional but preferred | If missing |
|---|---|---|---|---|
| `[AC]` Architectural Constraint | 2 | E1 (ADR) + E5 (code) | E2 (ratification record) | STUB with `PENDING_EVIDENCE` marker; not ratifiable |
| `[GR]` Governance Rule | 2 | E1 or E2 + E6 | E3 (research) | STUB or WIP |
| `[OR]` Operational Rule | 2 | Any of {E3, E6} + one other | E1, E5 | STUB or WIP |
| `[EP]` Engineering Principle | 1 OR convergent | E1 OR convergent E3 across ≥2 arcs | E2 | STUB |
| `[IP]` Implementation Pattern | 2 | E5 + E6 | E1 | STUB |
| `[RS]` Repository Standard | 1 | E5 OR E3 | E6 | STUB |
| `[RP]` Runtime Policy | 2 | E4 + E5 | E1 | STUB |
| `[RC]` Recovery Procedure | 1 | E6 (successful recovery) | E4, E5 | STUB or omit |
| `[DR]` Documentation Rule | 2 | E1 OR E3 + E4 | E6 | STUB |
| `[RM]` Research Methodology | 2 | E3 (Research OS or RAR) + E2 | E1 | Cannot be authored without |

### 7.2 Convergent-research special case

An Engineering Principle (`[EP]`) MAY be admitted with a single citation IF the citation is a research document that itself synthesizes convergent findings from ≥2 independent research arcs.

Example: this authoring protocol references 2708 through 2712 as convergent research. Playbook v1.0's Chapter 1 (Constitutional Context) may cite the 5-session research pack as a single evidence bundle representing convergent research.

### 7.3 What makes evidence "sufficient"

Evidence is sufficient when:

1. It exists at the cited location.
2. It structurally supports the rule (the cited section addresses the same subject).
3. It semantically supports the rule (SIGN-cycle verification).
4. It has not been superseded by a later contradicting artifact.

### 7.4 Historical evidence handling

Historical citations (E6 session handoffs from prior cycles) remain valid indefinitely for the RULE they support, even if newer sessions rewrite the context around them. The rule may be REVISED via amendment, but the historical evidence for the original rule stays cited.

**Applied consequence:** the Playbook accumulates evidence over versions; it does not discard prior evidence.

### 7.5 Evidence rejection cases

An evidence source is REJECTED when:

- It cannot be located.
- It exists but does not address the claimed subject.
- It exists and addresses the subject but contradicts the claim.
- It is unratified opinion (e.g., a draft research doc that has not passed SIGN).

Rejected evidence disqualifies the rule from admission UNTIL evidence is provided.

---

## 8. Writing style

Consistency in style is enforced not for aesthetics but for verifiability — visually consistent chapters can be linted and cross-referenced by tools.

### 8.1 Voice and tense

- **Voice:** active voice for normative statements. Passive voice only when the agent is universal (see §5.6).
- **Tense:** present indicative for normative statements ("The Playbook lives at ...", "Authors MUST cite ..."). Future tense (`will`, `shall in the future`) is FORBIDDEN in normative content — the Playbook describes present rules, not future promises.
- **Historical statements** use past tense ("Cycle 1A ratified 5 ADRs in workspace `a9a16593-…`").

### 8.2 Person

- The Playbook writes in third person (`Authors MUST ...`, `The ratifier MUST ...`).
- Second person (`You MUST ...`) is FORBIDDEN — obscures which agent is bound.
- First person (`We recommend ...`) is FORBIDDEN.

**Rationale:** the Playbook governs multiple agents (human, Claude, Rigby, Cascade automation). Third-person with named agent reduces ambiguity.

### 8.3 Grammar and punctuation

- Sentences MUST be complete sentences with subject + verb + object.
- Sentence fragments are FORBIDDEN in normative statements.
- Bullet lists MAY use fragments provided each fragment is a rule referenced by an ID (§9) or a listed example.
- Oxford comma is REQUIRED. Ambiguity from comma omission is a defect.
- One space after periods; no double spaces.

### 8.4 Capitalization

- Chapter titles: Title Case ("Constitutional Language Standards").
- Section headings: Sentence case ("Statement categories").
- Terms of art on first use in a chapter: bold or italicized (`*canonical authority*`, `**PublishGate**`).
- RFC-2119 keywords: `ALL CAPS` in normative sentences.
- Proper nouns: capitalize per English conventions (`Claude Code`, `Rigby`, `Chris`).
- Code identifiers: use inline code formatting (`Deliverable.status`, `_AUTHORITY_WEIGHTS`).

### 8.5 Lists

- **Numbered lists** for sequential steps or ordered enumerations.
- **Bullet lists** for unordered enumerations (examples, categories, cross-references).
- Each list item is either a full sentence or a fragment following the parent sentence.
- List items MAY carry their own rule IDs if each is independently normative.

### 8.6 Code blocks

- Use fenced code blocks with language identifiers (` ```python `, ` ```yaml `, ` ```markdown `).
- Include a short caption above or below when the code is normative content (e.g., a required frontmatter schema).
- Un-fenced inline code for identifiers.

### 8.7 Cross-references

Cross-references use **symbolic anchors**, not chapter/section numbers. See §14 for full discipline.

**Example (correct):** *"See Chapter Constitutional Context §Six-Layer Stack."*

**Example (fragile):** *"See §1.3."* — Breaks if Chapter 1 becomes Chapter 2.

Exception: cross-references to the *current chapter's own* sections MAY use numeric anchors (`§4.2`) because they cannot break from external renumbering.

### 8.8 Citations

Citations appear in-line at the end of the sentence they support:

- Format: `[EN: source]` where N is the evidence class (1-6).
- Multiple citations: `[E1: ADR-0120 §2.1; E5: `path/file.py:33-60`; E6: SESSION_1802 close forensics]`.

Detailed citation format lives in the evidence index sidecar (§8.9).

### 8.9 Evidence index citation format

The evidence index sidecar `docs/research/playbook/evidence_index_v<X_Y_Z>.md` uses this format per citation:

```markdown
## E1 — ADRs cited

### ADR-0120
- **Title:** Canonical authority attribute
- **Location:** workspace deliverable `5e492574-c54a-42ce-ad19-ed9e255ebb98`
- **Status:** ratified 2026-07-07
- **Ratification record:** `RATIFICATION_20260707_0120_ADR_CANONICAL_AUTHORITY_ATTRIBUTE`
- **Cited in Playbook chapters:** 1 (§Six-Layer Stack), 4 (§Cascade Discipline), 6 (§Authority Classification)
- **Provenance class:** verified quoted source (per PIC-10)
```

### 8.10 Normative-vs-informative formatting

Normative content: rule marker + rule ID + RFC-2119 keyword.

Informative content: no marker; blockquote prefix per §4.4.

**Applied consequence:** a reader scans normative content by looking at bolded markers; a reader scans informative content by looking at blockquote prefixes.

### 8.11 Length discipline

- Chapter length: 100-500 lines of substantive content in v0.1; extensible per amendment.
- Section length: focused; if a section exceeds ~50 rules, split into sub-sections.
- Sentence length: prefer 30 words or fewer. Longer sentences with multiple clauses are DEFECTS to review.

### 8.12 The "chatty prose" prohibition

Playbook prose MUST NOT include:

- Marketing language (`world-class`, `game-changing`, `revolutionary`).
- Uncertainty hedges in normative statements (`perhaps`, `probably`, `might`).
- Author voice (`we believe`, `in our view`).
- Non-substantive filler (`Note that`, `It is important to note`).

**Rationale:** the Playbook is legislation. Style follows function.

---

## 9. Rule identifiers and stability

Rule IDs give the Playbook long-term traceability and safe amendment.

### 9.1 ID format

`PLAYBOOK-<chapter>.<section>.<rule>` where:

- `<chapter>` is the chapter number (0-19 for content chapters, 20+ for appendices).
- `<section>` is a section number within the chapter.
- `<rule>` is a monotonically-increasing integer for the rule's position within the section.

**Examples:**
- `PLAYBOOK-4.2.1` — Chapter 4 (Documentation cascade), Section 4.2, Rule 1.
- `PLAYBOOK-6.1.3` — Chapter 6 (PIC-10 Provenance), Section 6.1, Rule 3.

### 9.2 Stability rule

Rule IDs MUST NOT change once ratified. Even if a chapter or section is renamed (a MINOR bump), the ID for the rule persists.

### 9.3 Rule ID allocation

- New rules within a section get the next integer (`4.2.1`, `4.2.2`, `4.2.3`, ...).
- **New rules do not renumber existing rules.**
- **Deletion of a rule leaves a gap.** `PLAYBOOK-4.2.2` deleted → next new rule in that section is `4.2.4`, not `4.2.2`.

### 9.4 Deletion registry

Every deleted rule is recorded in Appendix E (or a dedicated "Retired Rules Registry"). Format:

```markdown
### PLAYBOOK-4.2.2 (retired vX.Y.Z)
- **Original text:** "..."
- **Reason for retirement:** superseded by [new-rule-ID]; or "obsolete"; or "corrected error".
- **Superseded by:** PLAYBOOK-4.2.4 (if applicable).
```

### 9.5 Rule ID reference discipline

Cross-references to specific rules MUST use the rule ID, not text:

**Example (correct):** *"See PLAYBOOK-4.2.1."*

**Example (fragile):** *"See the four-step cascade rule."* — Breaks if rule wording changes.

### 9.6 Rule ID discoverability

Every ratified Playbook version includes an appendix (or autogen section) mapping rule ID → chapter section for programmatic navigation.

---

## 10. Section and chapter formatting

### 10.1 Chapter frontmatter template (per 2712 §3.2, extended)

```markdown
## Chapter N — <Title>

<!-- Chapter frontmatter — machine-readable -->

**Chapter ID:** PLAYBOOK-CH-N
**Purpose:** <one-sentence rule this chapter codifies>
**Scope:** <which constitutional layer / which artifact class this governs>
**Introduced in:** vX.Y.Z
**Last substantive change:** vX.Y.Z
**Evidence anchor:** docs/research/playbook/evidence_index_vX_Y_Z.md#chapter-N
**Statement classes present:** [AC, GR, OR, ...]
**Rule ID range:** PLAYBOOK-N.1.1 through PLAYBOOK-N.M.K

---
```

### 10.2 Section structure

```markdown
### N.M — <Section title>

<Section overview paragraph — INFORMATIVE only, no RFC-2119 keywords.>

**[CLASS] PLAYBOOK-N.M.1** <rule text with RFC-2119 keyword>. [E: citations]

**[CLASS] PLAYBOOK-N.M.2** <rule text>. [E: citations]

> **Commentary:** <explanation of purpose>.

> **Example:** <concrete illustrative usage>.

> **History:** <historical context linking the rule to observed events>.
```

### 10.3 Chapter closing sections

Every chapter ends with:

```markdown
### N.X — Cross-references

- To Chapter <name> §<name>
- To ADR-<nnnn>
- To RATIFICATION_YYYYMMDD_<name>
- To evidence_index_vX_Y_Z.md#chapter-N

### N.X+1 — Extension points

- <named slot 1 for future MINOR additions>
- <named slot 2>
```

### 10.4 The autogen zone

Some chapter subsections are auto-generated (per 2712 §3.6). They MUST be wrapped in DOC-AUTOGEN markers:

```markdown
<!-- DOC-AUTOGEN start:runtime_policy_inventory -->
<autogen content — do not edit by hand>
<!-- DOC-AUTOGEN end:runtime_policy_inventory -->
```

`verify_repo_guardrails.py` (or extension) MUST reject hand-edits between the markers.

---

## 11. Amendment discipline

Amendment discipline is codified in the Playbook itself (Chapter 10 Evolution & Amendment). This protocol pre-specifies the required rules Chapter 10 MUST contain.

### 11.1 When constitutional text may be modified

Existing constitutional text MAY be modified only via the **amendment workflow** defined in 2712 §9. Direct commits to `docs/ENGINEERING_PLAYBOOK.md` on `main` outside the amendment workflow are FORBIDDEN.

### 11.2 Semver bump triggers (restated from 2712 §7, formalized here)

| Change type | Bump | Example |
|---|---|---|
| Typo / grammar / broken link fix | PATCH | Correcting "cascase" → "cascade" |
| Autogen refresh (usually no bump; may be PATCH if triggered by MINOR content) | (none) or PATCH | `last_regen_at` update |
| Cross-reference update after chapter title change elsewhere | PATCH | Updating "See Chapter Documentation Cascade" text |
| Adding a clarifying Example that does not introduce a rule | PATCH | Adding an Example block below an existing rule |
| Adding a new rule to an existing section | MINOR | New `PLAYBOOK-4.2.5` under existing section |
| Adding a new section within an existing chapter | MINOR | New `PLAYBOOK-4.3` after existing 4.2 |
| Adding a new chapter to a reserved slot | MINOR | Chapter 11 (previously reserved) added |
| Extending an existing rule's applicability (backward-compatible) | MINOR | Extending 4.2.1 to cover a new artifact class |
| Codifying a new PIC | MINOR | Adding PIC-11 to Chapter 6 |
| Frontmatter schema-MINOR (new optional field) | MINOR | Adding an optional `commit_message_style` field |
| Chapter title change | MINOR | "Documentation cascade" → "Documentation cascade automation" |
| Removing a rule | MAJOR | Retiring PLAYBOOK-4.2.2 |
| Replacing a rule with different-behavior content | MAJOR | PLAYBOOK-4.2.1 changed such that consumers must adapt |
| Structural reorganization (chapters renumbered) | MAJOR | Chapter 4 becomes Chapter 5 |
| Frontmatter schema-MAJOR (field removal/rename) | MAJOR | Removing `compatible_with` field |
| Retroactive rule change | MAJOR + explicit directive | Rare; requires Chris directive |

### 11.3 Semver justification requirement

Every amendment PR MUST include a **version bump justification** in the PR description with the form:

```
## Playbook version bump justification

- Current version: vX.Y.Z
- Proposed version: vX.Y.Z+1 (PATCH | MINOR | MAJOR)

### Diff class
[Describe the change: rule added, rule removed, typo fix, etc.]

### Applied semver rule
[Cite the table row from §11.2 that applies.]

### Backward compatibility statement
[Is the change backward-compatible? If not, what breaks?]
```

`verify_repo_guardrails.py` (or dedicated Cycle 2 check) SHOULD reject PRs missing this section.

### 11.4 Amendment rate limiting

There is NO hard rate limit on Playbook amendments, but the following patterns SHOULD be observed:

- Multiple related amendments SHOULD be bundled into one MINOR bump (avoid churn).
- PATCH amendments MAY ship rapidly.
- MAJOR amendments SHOULD align with a Cycle open/close event.

### 11.5 Amendment cadence expectation

Historical baseline (from Cycle 1A discipline): Playbook is expected to see ~1-3 MINOR amendments per year and ~1 MAJOR every 2-3 years. PATCH cadence is opportunistic.

---

## 12. Deprecation and historical note handling

### 12.1 Deprecation lifecycle

A rule that is being retired follows this lifecycle:

1. **Deprecation warning** (MINOR bump): existing rule stays in place; adjacent rule marker (`[DEPRECATING vX.Y.Z]`) appears; deprecation reason stated.
2. **Retirement** (MAJOR bump, N+1 versions later): rule text moves to Retired Rules Registry (§9.4).

Optional: rules MAY skip deprecation warning if immediate retirement is authorized by Chris directive.

### 12.2 Deprecated rule text format

While a rule is in "deprecation warning" state:

```markdown
**[OR] PLAYBOOK-4.2.2** [DEPRECATING v1.3.0] Original rule text.

> **Deprecation note:** superseded by PLAYBOOK-4.2.5 as of v1.3.0. Rule will be retired in v2.0.0.
```

### 12.3 Historical notes MUST remain

Every retired rule's original text and reason for retirement MUST remain findable in the Retired Rules Registry. Rules are not "deleted" in the destructive sense; they are moved to the registry.

**Rationale:** future forensics may need to reconstruct why a decision was made and when it changed.

### 12.4 Historical notes in chapter bodies

Historical Context (`[HIST]`) statements MAY be inline in chapter bodies when they anchor a rule to observed evidence. They are informative, not normative, but they MUST remain across amendments unless the rule they anchor is itself retired.

### 12.5 Conflict resolution between rules

When two Playbook rules appear to conflict:

1. **Specificity rule:** the more specific rule wins over the more general rule.
2. **Version rule:** the more recently ratified rule wins if both are equally specific.
3. **Explicit override:** a Chris directive MAY declare which rule is authoritative (recorded in a ratification record).
4. **If unresolvable:** the conflict is a governance defect; a MAJOR amendment MUST resolve it.

**Applied consequence:** authors SHOULD check for conflicting rules before adding new ones. SIGN cycles SHOULD explicitly test for conflicts.

---

## 13. Internal consistency rules

Consistency is enforced across chapters via structural discipline.

### 13.1 Chapter dependency discipline

Chapters MAY depend on lower-numbered chapters (Chapter 4 may cite Chapter 1). Chapters MUST NOT depend on higher-numbered chapters (Chapter 1 MUST NOT cite Chapter 4).

**Rationale:** prevents circular reasoning where Chapter 1 requires Chapter 4 which requires Chapter 1.

**Exception:** Chapter 0 (Preamble) is a summary and MAY reference all chapters.

**Exception:** Chapter 10 (Evolution & Amendment) governs amendment; other chapters cite it inversely (they cite Chapter 10 as authority).

### 13.2 Terminology consistency

Every term of art has exactly one canonical definition. Definitions live in **Appendix B (Glossary)**. Terms MUST be used consistently:

- On first use in a chapter, terms are italicized: *canonical authority*.
- Subsequent uses in the same chapter appear unstyled.
- Definitions in the glossary MUST match the term's use throughout the Playbook.

### 13.3 Definition ownership

The chapter that FIRST introduces a term OWNS the definition (has the right to expand or refine it). Other chapters MAY use the term but MUST NOT REDEFINE it.

**Applied consequence:** if a chapter needs to override a definition, it MUST propose an amendment to the owning chapter's definition instead.

### 13.4 Duplicate rule detection

A new rule MUST NOT duplicate an existing rule. Duplicate detection is a SIGN-cycle responsibility.

**Detection heuristic:** two rules are duplicates if they have the same subject (target agent) and the same normative direction (both MUST or both SHOULD or both MAY).

**Applied consequence:** SIGN cycles SHOULD scan for near-duplicates using semantic search (Rigby-mediated).

### 13.5 Cross-chapter contradiction

A new rule MUST NOT contradict an existing rule (per §12.5 conflict resolution).

**Detection responsibility:** author drafts the rule; SIGN cycle verifies no contradiction; Chris ratifies knowing the contradiction check has run.

### 13.6 Evidence sync

Every citation in a chapter body MUST appear in the evidence index sidecar. Every citation in the evidence index MUST be cited somewhere in a chapter body. Orphaned citations (either direction) are defects.

**Applied consequence:** cascade tooling (Cycle 2) SHOULD verify evidence sync.

### 13.7 Glossary sync

Every term of art used in a chapter body MUST have a glossary entry. Every glossary entry MUST be used in at least one chapter body.

**Applied consequence:** authors MUST update the glossary alongside chapter authoring.

---

## 14. Cross-reference discipline

### 14.1 Symbolic anchors (from 2712 §3.5)

Cross-references between chapters MUST use symbolic anchors, not numeric anchors:

**Correct:** *"See Chapter Documentation Cascade §Four-Step Contract."*

**Fragile (FORBIDDEN):** *"See Chapter 4 §4.2."* — Breaks under chapter renumbering.

### 14.2 Anchor stability

Anchors survive:

- Chapter renumbering (uses chapter title, not number).
- Section reordering within a chapter (uses section title, not number).
- Rule ID changes (rule IDs themselves are stable — §9).

### 14.3 Rule reference format

References to specific rules use the rule ID:

**Correct:** *"See PLAYBOOK-4.2.1."*

### 14.4 External artifact references

References to workspace artifacts, git commits, and ratification records use structured citations:

- Workspace deliverable: `deliverable <uuid>` OR `RATIFICATION_YYYYMMDD_<title>`.
- Git tag: `playbook-vX.Y.Z`.
- Git commit: `commit <sha>` (short hex).
- ADR: `ADR-<nnnn>` (workspace or repo — the reader can disambiguate via workspace UUID vs `docs/adr/` path).

### 14.5 Broken reference handling

If a referenced artifact is deleted or moved:

- If the reference is in the Playbook body: the reference becomes stale; a PATCH amendment MUST update it.
- If the reference is in a retired rule: the reference remains as historical.
- If the referenced artifact is a ratification record and it has been deleted: this is a governance defect (ratification records SHOULD NOT be deleted); SIGN escalates.

### 14.6 Cross-reference audit

Every amendment SIGN cycle MUST verify:

1. All cross-references in modified sections resolve.
2. No new orphan references were introduced.
3. Rule ID references match rule IDs actually in the corpus.

---

## 15. Terminology and glossary discipline

### 15.1 The Glossary as authoritative source

Appendix B is the authoritative glossary. Every term of art:

1. Has an entry in the glossary.
2. Has exactly ONE definition.
3. Has a "First introduced in" pointer to the owning chapter.
4. Optionally has "See also" cross-references to related terms.

### 15.2 Glossary entry format

```markdown
### <Term>

- **Definition:** <one-sentence canonical definition>
- **First introduced in:** Chapter <name> §<name>
- **Related terms:** <term>, <term>
- **Evidence:** <citation>
```

### 15.3 Terms of art vs common words

A term of art is:

- A word or phrase specific to this platform / this domain (`workspace_canonical`, `PublishGate`, `Rigby`, `SIGN cycle`, `PIC-10`).
- Or a common English word given a specific technical meaning in this Playbook (`ratifier`, `cascade`, `mirror`).

Common words used in their ordinary meaning are NOT terms of art and do NOT require glossary entries.

### 15.4 New term admission

A new term of art is introduced via:

1. Add glossary entry in the same amendment PR that first uses the term.
2. Italicize the term on first use in the chapter body.
3. Cite the entry from the chapter body.

**Applied consequence:** authors MUST NOT introduce a term without a glossary entry in the same PR.

### 15.5 Term retirement

If a term becomes obsolete:

1. Mark the glossary entry as `[DEPRECATED vX.Y.Z]`.
2. Update all chapter uses to a replacement term (via MINOR amendment).
3. In the version that retires the term, move the glossary entry to a Retired Terms section within the glossary.

### 15.6 Synonym prohibition

Two glossary entries MUST NOT define the same concept. If two terms are truly synonymous, the glossary MUST declare one canonical and cross-reference the other.

---

## 16. AI authoring rules

The Playbook will be authored primarily by AI (Claude Code) with Chris ratifying. This protocol codifies AI authoring boundaries.

### 16.1 AI autonomous scope

AI MAY autonomously (without explicit per-action human approval):

- Draft new chapters or sections in a WIP research doc.
- Draft amendment proposals in `docs/research/playbook/proposals/`.
- Populate frontmatter (except deferred fields — see §16.2).
- Cite evidence from established sources.
- Run SIGN cycles (self-review OR dispatching to Rigby).
- Apply correction passes per SIGN findings.
- Regenerate autogen sections.
- Update evidence index sidecars.
- Create workspace deliverables of type `draft` for pre-ratification review.

### 16.2 AI requires human approval

AI MUST obtain explicit human (Chris) approval before:

- Merging any amendment PR to `main`.
- Creating a git tag.
- Creating a workspace ratification record.
- Firing `content_tool.content_complete` on a ratification record.
- Publishing any Playbook version transition.
- Modifying `content_hash` on ratified artifacts.
- Deleting any Playbook-related workspace deliverable.
- Reorganizing chapter structure (MAJOR bumps).

### 16.3 AI requires SIGN

AI MUST NOT ratify a Playbook amendment without a SIGN cycle. SIGN MAY be:

- Rigby-mediated (default per feedback_claude_directs_rigby_then_verifies).
- Fallback: parent-Claude verifier-loop when Rigby SIGN worker is unstable (per feedback_rigby_sign_worker_instability_recovery).

Chris MAY waive SIGN for PATCH amendments at his discretion (documented in the ratification directive).

### 16.4 AI requires ratification

AI-authored content MAY appear in the repository at:

- WIP research docs — no ratification required.
- Proposal docs under `docs/research/playbook/proposals/` — no ratification required.
- Amendment branches — no ratification required until merge.

AI-authored content MUST NOT appear in `docs/ENGINEERING_PLAYBOOK.md` on `main` without:

- Amendment PR passing SIGN.
- Chris's verbatim ratification directive.
- Workspace ratification record created via `content_tool.content_complete`.

### 16.5 AI MUST NEVER

AI MUST NEVER:

- Ratify content on its own.
- Force-push to `main`.
- Move an existing git tag.
- Delete a git tag.
- Modify a ratified Deliverable (status=completed) via ORM or PA tools.
- Delete a workspace ratification record.
- Falsify a Chris directive quotation (per PIC-10 provenance rule).
- Skip SIGN for non-PATCH amendments.
- Cite evidence that does not exist.
- Introduce a rule without a valid classification and citation.
- Rename or delete a rule ID.
- Reuse a retired rule ID.
- Bypass the amendment workflow.

### 16.6 Multi-agent authoring

When multiple AI agents (parallel Claude sessions, cross-fleet Claude sessions) author simultaneously:

- Each amendment MUST occupy its own branch.
- Merges to `main` MUST be sequential; parallel merges are FORBIDDEN.
- If two amendments race, second amendment rebases on first.

### 16.7 AI verification of own output

Every AI-authored amendment MUST be verified against §18 (verification strategy) BEFORE dispatching to SIGN. AI SHOULD run:

1. Evidence verification: every citation resolves.
2. Terminology verification: no new terms without glossary entries.
3. Cross-reference verification: symbolic anchors resolve.
4. Rule ID verification: no ID reuse or renumbering.
5. Classification verification: every rule has a classification badge.
6. Version bump justification: present in PR description.

---

## 17. Provenance preservation

Provenance is the audit trail of authorship, review, and ratification. It MUST be preserved unimpaired.

### 17.1 Authorship provenance

Every amendment PR carries:

- Commit trailer: `Authored-by: claude-code (session <id>)` when AI-authored.
- Commit trailer: `Authored-by: <username>` when human-authored.
- Multi-author trailers when SIGN corrections apply.

### 17.2 Review provenance

SIGN cycle output is recorded:

- SIGN report authored by Rigby (or fallback Claude): saved as workspace deliverable OR PR comment.
- SIGN pin UUID: preserved in the amendment PR description.
- SIGN batches: enumerated in PR description.
- Findings classification (BLOCKING / non-blocking / recommended edits): stored per finding.

### 17.3 Ratification provenance

Ratification records (per 2712 §14) preserve:

- Chris's verbatim directive.
- Timestamp of `content_tool.content_complete` firing.
- Git tag and commit SHA at ratification.
- content_hash of ratified body.

### 17.4 Session provenance

The session that produced an amendment is captured in:

- SESSION_XXXX_*.md handoff (in `docs/handoffs/`).
- Ratification record body §Post-ratification actions.
- Playbook frontmatter `branch_authored` field.

### 17.5 Provenance recovery discipline

If provenance for a ratified artifact cannot be recovered (per 2707 §5 G1 finding):

1. The artifact stays ratified.
2. The ratification record MUST use provenance-honest attribution ("engineering rationale recorded during authoring rather than a provenance-guaranteed verbatim quotation").
3. The gap is documented in a follow-up ratification record correction.

### 17.6 Provenance is immutable-on-write

Once a ratification record is `status=completed`, its provenance sections MUST NOT be edited. Corrections are ADDITIVE via follow-up records, not destructive.

---

## 18. Verification strategy

Verification is the process by which a proposed Playbook amendment earns readiness for ratification.

### 18.1 The 8-check verification protocol

Every amendment MUST pass all 8 checks before dispatch to Chris for ratification:

**Check 1 — Evidence verification.**
- Every citation resolves to an existing source.
- Every source substantively supports the rule.
- No superseded evidence remains cited without acknowledgment.

**Check 2 — Terminology verification.**
- Every new term has a glossary entry.
- Every glossary entry is used in ≥1 chapter body.
- Existing term definitions have not silently drifted.

**Check 3 — Constitutional consistency.**
- No new rule contradicts an existing rule.
- No new rule duplicates an existing rule.
- Chapter dependency discipline holds (no forward dependencies).

**Check 4 — Cross-reference integrity.**
- Symbolic anchors resolve.
- Rule ID references match live rule IDs.
- External artifact references (ADRs, git tags, workspace UUIDs) resolve.

**Check 5 — Citation completeness.**
- Every normative statement carries ≥1 citation.
- Every citation appears in the evidence index sidecar.
- Every evidence index entry is cited in the body.

**Check 6 — Version consistency.**
- Frontmatter `version` matches the proposed bump.
- Frontmatter `parent_version` matches the immediate predecessor.
- Frontmatter `compatible_with` is accurate.
- Version bump justification present in PR description.

**Check 7 — Semantic review.**
- SIGN cycle finds no BLOCKING defects.
- Non-blocking findings are documented for future amendment.

**Check 8 — SIGN attestation.**
- SIGN report attached to the amendment PR.
- SIGN pin UUID recorded.
- SIGN batch results enumerated.
- Reviewer identity recorded (Rigby OR fallback verifier-loop).

### 18.2 Check ownership

- Checks 1-6: AI (Claude) verifies pre-SIGN.
- Check 7: Rigby SIGN (or fallback Claude verifier-loop).
- Check 8: SIGN itself.

### 18.3 Failed check handling

- Check 1-6 failure: AI corrects the amendment before SIGN.
- Check 7 (BLOCKING) failure: correction pass applied; re-SIGN.
- Check 7 (non-blocking) failure: recorded; MAY proceed; deferred to future amendment.
- Check 8 failure: re-run SIGN.

### 18.4 Manual override

Chris MAY, at his discretion, override any check failure via explicit directive. Override MUST be recorded in the ratification record body with rationale.

### 18.5 SIGN expectations

SIGN review for Playbook amendments SHOULD be:

- Adversarial (per Cycle 1A discipline; SIGN attempts to falsify the amendment).
- Batch-organized (2-4 batches for MINOR; 4+ batches for MAJOR).
- Provenance-classified (per PIC-10).
- Documented with per-finding classification.

### 18.6 Verification for PATCH

PATCH amendments MAY use lightweight verification:

- Check 1 required (evidence still resolves).
- Check 4 required (cross-references still resolve).
- Check 6 required (version bump justified).
- Others OPTIONAL for pure PATCH.

**Rationale:** PATCH amendments carry no rule change; heavyweight verification is disproportionate.

---

## 19. Future automation opportunities

The protocol identifies opportunities. Implementation is out of scope for this session.

### 19.1 Linting

- **RFC-2119 keyword linter:** verify every normative sentence has exactly one capitalized keyword.
- **Sentence-length linter:** flag sentences >40 words for review.
- **Passive-voice linter:** flag passive voice in normative sentences.
- **Prohibited-phrase linter:** flag `has to`, `is required to`, etc.
- **Rule ID format linter:** verify `PLAYBOOK-<ch>.<sec>.<rule>` pattern.

### 19.2 CI validation

- **Frontmatter YAML schema check:** validate on every PR modifying `docs/ENGINEERING_PLAYBOOK.md`.
- **Version bump justification check:** reject PRs missing the justification section.
- **Rule ID uniqueness check:** reject if any rule ID is duplicated.
- **Retired rule ID reuse check:** reject if any retired rule ID is reused.

### 19.3 Citation validation

- **Evidence resolves check:** for every citation, verify the target source exists.
- **Line-number stability check:** for E5 platform-evidence citations that reference `path:line`, verify line still exists (soft check — may drift).
- **Evidence index sync check:** verify body citations ↔ evidence index entries match.

### 19.4 Normative language detection

- **Normative-vs-informative classifier:** detect paragraphs mixing both.
- **Statement-class-marker check:** every normative paragraph has a classification badge.
- **Un-marked normative language:** flag paragraphs with RFC-2119 keywords lacking a rule ID or marker.

### 19.5 Cross-reference validation

- **Symbolic anchor resolver:** for every symbolic cross-reference, verify the target section exists.
- **Rule ID cross-reference validator:** verify `PLAYBOOK-N.M.K` references match actual rule IDs.
- **External reference validator:** verify referenced ADRs, workspace UUIDs, git tags exist.

### 19.6 Evidence completeness scoring

- **Per-chapter score:** ratio of citations to normative rules; flag chapters with low scores.
- **Per-rule score:** number of evidence sources cited; flag rules below threshold.
- **Evidence class diversity:** flag rules citing only one class when 2+ are required.

### 19.7 Version bump verification

- **Diff classifier:** analyze diff between two Playbook versions; predict semver bump; flag if PR claim mismatches.
- **Rule-change detection:** identify rule additions, removals, and modifications.
- **Breaking change detection:** identify MAJOR-triggering changes.

### 19.8 Terminology enforcement

- **Glossary consistency check:** terms defined in glossary are used consistently in body.
- **Undefined-term flagger:** italicized terms with no glossary entry.
- **Unused-term flagger:** glossary entries with no body citations.

### 19.9 Automation delivery approach

Each of the above is a small, focused Cycle 2+ tooling investment. None is architecturally load-bearing for v0.1. All are complementary to the human-verified 8-check protocol (§18).

---

## 20. Pressure test / falsification

Nine categories per mission. Attacking every dimension.

### 20.1 Ambiguous language

**Attack:** RFC-2119 keywords still allow ambiguity in edge cases (`SHOULD` allows for "reasonable" deviation — who defines reasonable?).

**Response:** the protocol explicitly requires deviation from `SHOULD` to be documented with justification (§5.2). Undocumented `SHOULD` non-compliance is a defect caught in verification.

**Attack:** the distinction between `[REC]` and `[GUIDE]` (§3.1) is subjective.

**Response:** the discriminator is the strength of the RFC-2119 keyword. `SHOULD` → `[REC]`; `MAY` → `[GUIDE]`. Explicit in §3.3.

**Verdict:** ambiguous language addressed.

### 20.2 Insufficient evidence

**Attack:** the evidence thresholds (§7.1) are set arbitrarily. Why 2 sources for `[AC]` and not 3?

**Response:** the thresholds come from observed Cycle 1A practice. 0110-0150 ratifications cited ≥2 evidence sources each. The thresholds match empirical baseline; they can be raised via MINOR amendment if evidence accumulates that 2 is insufficient.

**Attack:** what if evidence exists but is contested?

**Response:** contested evidence triggers SIGN escalation. Chris directive resolves.

**Verdict:** insufficient evidence handled.

### 20.3 AI misuse

**Attack:** AI could game the citation check by citing evidence that superficially matches but doesn't substantively support the rule.

**Response:** SIGN cycle (Check 7 in §18) is specifically adversarial and verifies substantive support. Human verifier (Chris) reviews SIGN report before ratification.

**Attack:** AI could invent a plausible-sounding rule and cite evidence to support it, gaming the verification.

**Response:** Chris's ratification directive is the final gate. AI cannot ratify autonomously (§16.5). The Playbook's authority comes from Chris; AI can only draft.

**Verdict:** AI misuse mitigated via role separation.

### 20.4 Governance failures

**Attack:** ratifier (Chris) unavailable indefinitely.

**Response:** the protocol does not solve indefinite ratifier unavailability. This is a Cycle 3+ delegation problem. For v0.1 through v2.x, ratifier availability is assumed.

**Attack:** SIGN deadlock (SIGN always finds new BLOCKING defects).

**Response:** SIGN report is a snapshot. If SIGN finds a defect, correct it. If SIGN finds a new defect after correction, correct that too. SIGN converges because each finding is discrete. Chris directive breaks any deadlock.

**Attack:** ratification record could be corrupted (e.g., ORM write failure mid-transaction).

**Response:** Cycle 2 hardening should add ORM-level constraints. For v0.1, discrepancies caught by post-ratification verification checklist (2712 §15.1).

**Verdict:** governance failures addressable within protocol boundaries.

### 20.5 Human workflow failures

**Attack:** Chris might not want to write formal ratification directives.

**Response:** the directive can be casual English (per 2712 §17.9 pressure-test response). What matters is verbatim capture, not formal phrasing.

**Attack:** Chris might want to skip SIGN entirely.

**Response:** Chris MAY waive SIGN for PATCH per §18.6. For MINOR and MAJOR, SIGN is REQUIRED. If Chris wants to waive for higher bumps, that's a directive; the ratification record documents it as an explicit override (§18.4).

**Attack:** Chris might want to author directly (not just ratify).

**Response:** the protocol permits Chris to author. Chris is a valid author-role holder (§4). The Playbook's role separation is about the RATIFICATION step, not the author step.

**Verdict:** human workflow addressed.

### 20.6 Scaling concerns

**Attack:** the 8-check verification will not scale to a 20-chapter Playbook with 500 rules.

**Response:** the 8-check protocol scales linearly with chapter count. Automation (§19) reduces marginal cost per amendment. 500 rules at v2.x is expected timeframe of several years; ample time to build Cycle 2 tooling.

**Attack:** rule ID stability breaks if the chapter organization ever needs deep restructuring.

**Response:** deep restructuring is a MAJOR bump and is explicitly permitted (§11.2). Rule IDs are preserved via mapping table in Appendix (or new chapter). Restructuring costs are real but bounded.

**Verdict:** scaling addressed.

### 20.7 Multi-agent authoring concerns

**Attack:** two Claude sessions could produce contradictory amendments in parallel.

**Response:** §16.6 explicitly forbids parallel merges. Second amendment rebases on first. Sequential ratification is enforced.

**Attack:** a Claude session in a different repo (character-os) could propose amendments.

**Response:** cross-repo amendment coordination is out of scope for v0.1. Only donkey-betz sessions may propose amendments to the donkey-betz Playbook. Cross-repo research feeds informative proposals; codification requires local session.

**Verdict:** multi-agent authoring addressed.

### 20.8 Long-term maintainability

**Attack:** in 10 years, the Playbook may accumulate hundreds of retired rules, cluttering the Retired Registry.

**Response:** the Retired Registry is autogen'd; retired rules don't clutter chapter bodies. Chris directive MAY consolidate the Retired Registry into archival cycles.

**Attack:** evidence index sidecars may accumulate hundreds of files.

**Response:** each ratified version has one sidecar. Historical sidecars stay in git. Search remains linear in current version.

**Verdict:** long-term maintainability addressed.

### 20.9 Cross-repository portability

**Attack:** other fleet apps (mentorforge, character-os) may want to fork this Playbook.

**Response:** the Playbook is donkey-betz-scoped. Other apps MAY reference it as prior art but MUST author their own. The protocol itself may be adopted verbatim by sibling apps; the Playbook itself is app-specific.

**Attack:** an amendment to the protocol (this document) needs its own governance.

**Response:** the protocol is a research doc today. Once codified into Playbook Chapter 10 (Evolution & Amendment), amendments to the protocol ARE Playbook amendments. Before codification, this document is authoritative research; Chris ratifies changes to it as needed.

**Verdict:** cross-repository portability handled.

### 20.10 Summary

All 9 categories survive pressure test. Three areas (Cycle 3+ delegation, cross-repo governance, mass Retired Registry consolidation) are deferred out-of-scope. None block v0.1 authoring.

---

## 21. Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Statement classification (§6) is fine-grained; authors may misclassify | Med | SIGN cycle catches misclassification; classification badges are visible in the body |
| R2 | Evidence thresholds (§7.1) may not match specific use cases | Low | Chris directive can override |
| R3 | Rule ID gaps accumulate over versions (many `4.2.2 (retired)` entries) | Low | Retired Registry autogen; readers only see live IDs in body |
| R4 | Symbolic anchors (§14) require chapter titles that are unique and stable | Med | Chapter title changes are MINOR bumps and update anchors |
| R5 | Glossary drift (§15) — a term's meaning evolves without updating the entry | Med | SIGN cycle Check 2 catches |
| R6 | AI could game verification (§16) by producing content that passes automated checks but is subtly wrong | Med | Chris's ratification is the final gate; SIGN is adversarial |
| R7 | Multi-author amendments create commit-trailer merge conflicts | Low | Standard git-merge tooling handles |
| R8 | Cycle 2 automation may lag behind protocol requirements; some checks stay manual | Med | Manual 8-check protocol works; automation is enhancement |
| R9 | Playbook v0.1 authored under this protocol; if the protocol has an unforeseen defect, v0.1 could inherit it | Med | v0.1 is inaugural and light on rules; SIGN cycle catches; PATCH amendments correct |
| R10 | Prohibited-phrase list (§5.5) may lag colloquial drift | Low | MINOR amendment updates list |
| R11 | The 8-check protocol requires Rigby SIGN, which has known instability (per feedback_rigby_sign_worker_instability_recovery) | Med | Fallback verifier-loop protocol acknowledged |
| R12 | Amendment PR justification (§11.3) requires disciplined authorship | Low | CI check rejects PRs missing it |
| R13 | The Retired Rules Registry could contain sensitive historical context Chris wants to redact | Low | Chris directive can move entries to a private appendix |
| R14 | Cross-references to external artifacts (workspace UUIDs) go stale if the target is deleted | Med | Cycle 2 tooling verifies external references; SIGN escalates broken references |
| R15 | Evidence Class E4 (Runtime evidence) drifts as production data evolves; historical citation may not reproduce | Low | E4 citations are anchored to a snapshot moment (per 0199 §4 snapshot qualifier discipline) |

---

## 22. Unknowns

| # | Unknown | Why it matters | How to resolve |
|---|---|---|---|
| U1 | Whether Chris wants the classification badges (`[AC]`, `[GR]`, etc.) inline in the body OR in the sidebar | Aesthetic and parseability | Chris directive during v0.1 authoring |
| U2 | Whether Chris wants the RFC-2119 formal citation (RFC 2119 / BCP 14) referenced by URL or by name only | Convention consistency | Chris directive |
| U3 | Whether the Retired Rules Registry lives in Appendix E OR its own file | Playbook length management | v0.1 authoring decision |
| U4 | Whether AI amendment PRs should use a bot commit author OR Claude's session identity | Authorship provenance clarity | Chris directive |
| U5 | Whether the glossary should be autogen'd from term-first-uses in chapters OR hand-maintained | Consistency vs authorial control | v0.1 authoring decision |
| U6 | Whether `content_hash` verification is a hard block for ratification OR a warning | Cycle 2 hardening scope | Cycle 2 planning |
| U7 | Whether the SIGN report is stored as workspace deliverable OR as PR comment | Provenance visibility | v0.1 authoring decision |
| U8 | Whether existing repo ADRs (`docs/adr/ADR-0001..0004`) should be referenced by the Playbook as prior art | Cross-corpus consistency | v0.1 Chapter 1 authoring |
| U9 | Whether the IOS + Research OS docs should be renamed under the Playbook's naming discipline | Existing artifact hygiene | Cycle 2 candidate; not blocking for v0.1 |
| U10 | Whether the Playbook itself should carry the `[HIST]` classification for its own Chapter 0 § "How we got here" | Meta-recursion elegance | v0.1 authoring decision |

---

## 23. Sufficiency assessment and chapter authoring order

### 23.1 Is this protocol sufficient to begin Playbook v0.1?

**Yes.** This protocol is sufficient.

The following architectural elements are in place:

- Six-layer constitutional stack (2711 §18) — accepted.
- Playbook Architecture Specification (2712) — accepted.
- This authoring protocol (2713) — proposed for acceptance.

No further architectural work is required before v0.1 authoring begins. The pieces cohere:

- 2712 tells the author WHERE the Playbook lives (repo `docs/ENGINEERING_PLAYBOOK.md`), WHAT structure it has (10 chapters), HOW it versions (semver by rule change), HOW it ratifies (workspace envelope).
- 2713 tells the author HOW to write each rule (RFC-2119 keywords, classification badges, evidence citations, rule IDs, symbolic anchors, verification checks).

### 23.2 Recommended chapter authoring order for v0.1

The four chapters that MUST be full content in v0.1 (per 2712 §16.9) are 0, 1, 6, 10. Authoring order recommendation:

**Session 2714: Chapter 6 (Provenance Classification Standard, PIC-10)** — full content.

*Rationale:* Chapter 6 defines the provenance classification that every subsequent chapter uses when citing evidence. Authoring Chapter 6 first means every subsequent chapter has the classification vocabulary available. Chapter 6 also acts as a self-contained exercise of the authoring protocol — writing it verifies whether §3-§18 of this protocol are operationally sound.

**Session 2715: Chapter 10 (Evolution & Amendment)** — full content.

*Rationale:* Chapter 10 codifies how the Playbook itself evolves. Authoring it second means the amendment discipline that applies to all future amendments is in place before non-meta chapters land. Chapter 10 is largely a codification of 2712 §7-§9 + this protocol §11-§17.

**Session 2716: Chapter 1 (Constitutional Context)** — full content.

*Rationale:* Chapter 1 grounds the Playbook in the six-layer stack (2711). It's the "why this document exists" chapter. Its evidence base is 2708 through 2712 as convergent research. Authoring it third means the meta-discipline (6, 10) is authored first; readers arriving at Chapter 1 see a document that already exists constitutionally.

**Session 2717: Chapter 0 (Preamble)** — full content.

*Rationale:* Chapter 0 is the reader's entry point. It summarizes the other three full chapters and stubs. It includes the RFC-2119 declaration (per §5.1) and reader orientation. Authoring it last ensures it accurately summarizes the completed content.

**Session 2718: Stub chapters 2, 3, 4, 5, 7, 8, 9** — placeholder content with `PENDING_EVIDENCE` markers.

Each stub is a small chapter with just:

- Chapter frontmatter (per §10.1).
- Purpose statement.
- Scope statement.
- `PENDING_EVIDENCE` marker with expected evidence classes.
- Extension points (empty).

**Session 2719: v0.1 SIGN cycle** — Rigby-mediated, 4-batch, adversarial.

**Session 2720: v0.1 correction pass** (if SIGN finds BLOCKING defects).

**Session 2721: v0.1 ratification** — Chris directive; PR merge; git tag `playbook-v0.1.0`; workspace ratification record; cascade.

**Estimated total effort:** 4-8 sessions from Session 2714 through v0.1 ratification. Depends on:

- Rigby SIGN worker stability (per feedback_rigby_sign_worker_instability_recovery).
- Chris's directive cadence.
- Whether Chris amends the authoring order.

### 23.3 What's NOT part of v0.1

- Chapters 2-9 as full content (deferred to v0.2 through v0.9 MINOR amendments).
- Cycle 2 automation (linters, CI validators, evidence completeness scoring) — parallel work stream.
- Retroactive migration of `0000_RAR_METHODOLOGY`, `0005_PLATFORM_BOOTSTRAP_CONTRACT`, `0010_RESEARCH_OPERATING_PROTOCOL`, `0020_CYCLE_0_CLOSEOUT`, `MANIFEST_v20260707` from workspace to repo — accepted L2-in-L5 anomaly per 2711 §8.9.
- Tenant-scope or fleet-scope Playbook variants — Cycle 3+ and Cycle 4+ respectively.

### 23.4 Deferred to Chris's directive

Before Session 2714 begins, Chris SHOULD indicate:

- Acceptance of this protocol as authoring standard.
- Preferred classification badge display (inline vs sidebar; U1).
- Preferred glossary maintenance (autogen vs hand; U5).
- Any deviation from the recommended chapter authoring order.

If Chris has no specific directive, the default order and defaults apply.

---

## 24. Closing

The Engineering Playbook Authoring Protocol translates the constitutional architecture into a legislative drafting standard. It codifies:

- Language discipline via RFC-2119 keyword usage.
- Classification discipline via 10 statement classes.
- Evidence discipline via 6 evidence classes and a per-class admission matrix.
- Stability discipline via rule IDs, symbolic anchors, and deletion registries.
- Verification discipline via an 8-check protocol.
- Amendment discipline via semver-by-rule-change and role separation.
- AI-authoring boundaries via explicit MAY/MUST NOT rules.
- Provenance preservation via commit trailers, SIGN records, ratification envelopes.

**Every downstream Playbook amendment session (2714 and beyond) references this protocol as authoring standard.**

**Session 2714 (next):** Chapter 6 (PIC-10 Provenance Classification Standard) authoring. Full content. Approximately 300-500 lines of substantive chapter body plus frontmatter and evidence anchor.

**Repository ends clean.** This document is the sole artifact of Session 2713.

---

_End of Session 2713 Engineering Playbook Authoring Protocol. No Playbook content authored. No ADRs opened. No workspace deliverables created. No constitutional amendments. No runtime changes. Repository ends clean (this document + five untracked prior proposals only)._

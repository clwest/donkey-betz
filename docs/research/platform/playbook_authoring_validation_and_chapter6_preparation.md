# Playbook Authoring Validation and Chapter 6 Preparation

**Session:** 2717 (methodology validation + Chapter 6 preparation)
**Date:** 2026-07-08
**Status:** Validation report — awaiting Chris's review
**Predecessors:** 2708–2715 architecture research chain; 2716 Chapters 0 and 1 draft

**Author:** Claude (Opus 4.7, 1M context)

**Role:** Editor-in-Chief. Validating whether the authoring methodology itself scales.

**Scope constraints per mission:** Frozen evidence manifest only. No new research. No policy invention. No SIGN. No modifications to `docs/ENGINEERING_PLAYBOOK.md` (not yet created). No Chapter 6 authoring. Repository ends clean.

**Repository state at session open:** branch `main`, HEAD `309f85ee`. Working tree clean save for nine untracked prior research proposals (2708 through 2716).

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Methodology validation](#2-methodology-validation)
3. [Structural findings](#3-structural-findings)
4. [Rule architecture findings](#4-rule-architecture-findings)
5. [Authoring improvements](#5-authoring-improvements)
6. [Reusable templates](#6-reusable-templates)
7. [Risks](#7-risks)
8. [Unknowns](#8-unknowns)
9. [Chapter 6 preparation package](#9-chapter-6-preparation-package)
10. [Recommendation](#10-recommendation)

---

## 1. Executive summary

**Question:** Is the authoring methodology used in Session 2716 (Chapters 0 and 1 draft) sustainable through many future versions?

**Answer:** Substantially yes, with **four required refinements** before Chapter 6 authoring begins.

**Refinements required:**

1. **Rule-ID interpretation:** rule IDs are stable per 2713 §9.2 but the section number *embedded in* the ID can become divorced from the section the rule physically lives in after a section split. Session 2716 authoring did not encounter this, but Chapter 6 (projected 40-50 rules across 9-10 sections) is likely to. The Playbook needs an explicit interpretation rule saying that IDs identify rules, not physical locations, and cross-references MUST use rule IDs rather than section numbers when precision matters.

2. **Citation format:** the inline verbose form used in Session 2716 (`[E5: `content/_canonical_authority_helpers.py:33-60`; E1: workspace ADR-0120]`) is readable at 8 rules per chapter but will not scale to 500+ rules across the Playbook. A **citation-key shorthand backed by the evidence index sidecar** should be adopted before Chapter 6.

3. **Reference table for recurring artifacts:** UUIDs, workspace IDs, and session handoff paths were repeated multiple times in Chapter 1. A single **Appendix A: Reference Registry** should hold canonical short-names; chapter body cites short-names.

4. **History-versus-rule discipline:** Session 2716 §1.7 uses `> **History:**` blockquotes correctly but Chapter 1 rules PLAYBOOK-1.7.1 and PLAYBOOK-1.8.1 fuse historical assertion with normative rule in a single sentence. This is not a defect in the draft but a pattern to avoid at scale. A stricter separation guideline should be adopted.

**Structural verdict:** the 37 rules authored in Chapters 0 and 1 are constitutionally sound. The four refinements are process-level, not policy-level. No rules require rewording. No architecture change is triggered.

**Chapter 6 preparation:** the Chapter 6 outline is complete and includes 8 major sections with an estimated 40-50 rules. Evidence coverage from 2715 §9 is sufficient with zero blocking gaps. **Chapter 6 should be authored across two sessions** given its size (see §9.7). Session 2718 authors §6.1–§6.6 (rule classification + evidence classes + admission standard); Session 2719 authors §6.7–§6.12 (provenance-honest attribution + recovery + reconciliation).

**Recommendation (§10):** apply the four refinements as a small pre-Chapter-6 preparation pass; then begin Chapter 6 §6.1–§6.6 in the next session.

---

## 2. Methodology validation

Answers to the 15 primary-mission questions.

### 2.1 Does the rule numbering system scale through many future versions?

**Substantially yes, with one important interpretation gap.**

The `PLAYBOOK-N.M.K` scheme (chapter N, section M, rule K) is defensible for the current chapter count and rule density. Verified via 2716 draft:

- Chapter 0: 8 rules across 4 sections (§0.3, §0.4, §0.6). Density ≈ 2 rules per section.
- Chapter 1: 29 rules across 10 sections. Density ≈ 3 rules per section.

At v2.x with ~500 rules across 15 chapters, average density becomes ~5-6 rules per section — well within a scheme with three-digit `K` values (999 rules per section).

**Interpretation gap:** if a section splits during a MAJOR amendment (e.g., §1.6 grows large and is split into §1.6 + §1.7), rules that were `PLAYBOOK-1.6.11` cannot renumber. Per 2713 §9.2, IDs are permanent. Consequence: after the split, some rules with section-`6` in their ID physically live in a section renumbered `7`. Cross-references by rule ID resolve correctly; cross-references by section number would be wrong.

This is not a bug; it is a scheme property. The Playbook needs to state it explicitly so authors do not confuse "the section a rule was born in" with "the section a rule currently lives under."

**Recommendation:** add PLAYBOOK-10.x.y in Chapter 10 §Rule Identifiers stating: *"A rule's identifier records the chapter and section under which the rule was **originally** ratified. Later chapter restructuring MUST NOT modify rule identifiers. Cross-references intended to survive restructuring MUST use rule identifiers rather than section numbers."*

### 2.2 Will chapter boundaries remain stable through years of amendments?

**Yes at chapter-title level; not fully at content-scope level.**

Chapter titles are stable per 2712 §3.1 (chapter numbers are stable; renaming is MINOR). Session 2716 draft shows chapter titles used symbolically in cross-references (§0.7, §1.11).

Content-scope drift IS observable, however. Two examples from the 2716 draft:

- Chapter 0 §0.6.1 (reader's contract on version applicability) reads as governance of amendment lifecycle — closer in spirit to Chapter 10.
- Chapter 1 §1.10 (rule origin discipline) is nearly a Chapter 6 rule; it describes the same evidence-admission concept.

The overlap is minor and defensible for v0.1 because Chapters 6 and 10 do not yet exist. Once they are authored, some of these rules may be candidates for MINOR-amendment relocation (via the standard supersession mechanism per 2713 §12).

**Recommendation:** accept minor scope overlap in v0.1. Document in Chapter 10 §Extension Points that scope-refinement amendments may relocate rules across chapters after full-chapter authoring is complete.

### 2.3 Are any rules duplicated between Chapters 0 and 1?

**Two rule pairs are near-duplicates.**

Pair 1 — evidence citation discipline:
- PLAYBOOK-0.3.4: *"Every normative sentence in the Playbook body MUST cite at least one evidence source drawn from the frozen evidence manifest."*
- PLAYBOOK-1.10.1: *"Every normative statement in the Playbook body MUST derive from at least one source enumerated in the frozen evidence manifest for the Playbook version in force."*

These are NOT identical: 0.3.4 is about the **authorial obligation to cite**; 1.10.1 is about the **existence of evidentiary basis for the rule**. But they are close.

**Distinction analysis:** 0.3.4 says citations must appear in the text. 1.10.1 says the underlying claim must be evidence-based. A rule could theoretically satisfy 0.3.4 by citing something and violate 1.10.1 if the cited source does not substantively support the rule. So both are needed.

**Recommendation:** keep both. Consider adding a `> **Commentary:**` block on 1.10.1 clarifying the distinction from 0.3.4.

Pair 2 — no other significant duplicates observed.

### 2.4 Are any rules misplaced and better suited for Chapter 6 or Chapter 10?

**Yes — five candidates for eventual relocation.**

| Rule | Current chapter | Better chapter | Rationale |
|---|---|---|---|
| PLAYBOOK-0.6.1 (reader's contract on version applicability) | 0 | 10 | Governs how versions relate to actions |
| PLAYBOOK-1.5.4 (System Owner directive form) | 1 | 10 | Procedural, about ratification form |
| PLAYBOOK-1.6.3 (Canon Registry inclusion during cascade) | 1 | 10 | Procedural, about ratification cascade |
| PLAYBOOK-1.6.5 (Chapter 4 must cite DOC_LIFECYCLE) | 1 | 4 | Meta-rule about a specific chapter |
| PLAYBOOK-1.6.10 (Chapter 2 must cite Research OS; Chapter 3 must cite IOS) | 1 | 2 and 3 | Same |
| PLAYBOOK-1.10.1 through 1.10.3 (rule origin discipline) | 1 | 6 | Provenance/evidence discipline |

Relocation is NOT a v0.1 blocker. Rule IDs stay stable; only physical position moves. Relocation is a MINOR amendment executed once all target chapters exist. **No action for v0.1**; note candidates in Chapter 10 §Extension Points.

### 2.5 Is the balance between informative and normative content appropriate?

**Appropriate for Chapter 0 (preamble-shaped); marginal for Chapter 1 (heavy informative preambles).**

Chapter 0:
- ~40% normative, ~60% informative.
- Appropriate for a preamble.

Chapter 1:
- ~55% normative, ~45% informative.
- Slightly informative-heavy in §1.4 (canonical authority) and §1.6 (pre-existing ecosystem) because those sections need to describe the ecosystem before ruling on it.

At v2.x with many more chapters, an informative:normative ratio of 30:70 becomes typical for governance chapters and 60:40 for reference chapters (like Chapter 1's ecosystem enumeration). The current draft is within acceptable bounds.

**Recommendation:** hold current ratio. If any specific chapter tips beyond 70% informative, consider splitting reference content into an Appendix.

### 2.6 Is the current amount of commentary sustainable?

**Yes for high-authority rules; excessive for lower-authority rules.**

Session 2716 used `> **Commentary:**` blockquotes on ~50% of rules. This adds ~30% to chapter length. Rules with high downstream impact (PLAYBOOK-1.2.3 upward-ratification pattern; PLAYBOOK-1.4.6 authority-weighted retrieval) benefit from commentary. Rules with self-evident meaning (PLAYBOOK-0.3.5 lowercase-keyword rule) do not.

**Recommendation:** commentary is REQUIRED for `[AC]` Architectural Constraint rules and `[EP]` Engineering Principle rules; OPTIONAL for `[GR]`, `[DR]`, `[OR]`; usually OMITTED for procedural rules. Document this as a §5 authoring improvement.

### 2.7 Does the current evidence citation style remain readable at scale?

**No, not at scale.**

Current inline verbose form: `[E5: `content/_canonical_authority_helpers.py:33-60`; E1: workspace ADR-0120; E3: 2711 §11]`

- Works fine at 1-3 citations per rule.
- Becomes unwieldy at 4+.
- Repetition problem: `content/_canonical_authority_helpers.py:33-60` is cited in 4 different rules in the 2716 draft with slightly different line ranges.

Two problems compound:
1. Long verbose citations reduce readability of the rule text.
2. Repeated citations bloat the chapter and complicate cross-reference maintenance.

**Recommendation:** adopt a citation-key shorthand backed by the evidence index sidecar (see §5.3 for the format). Preserve full source detail in the evidence index; use short keys in the Playbook body.

### 2.8 Should citations eventually become footnotes, endnotes, inline references, or remain unchanged?

**Inline references using citation keys** is the recommended form.

Options weighed:

- **Inline verbose (current):** poor scale, high recency drift risk when line numbers move.
- **Footnotes:** disrupts reading flow in the constitutional body; scattered rendering on GitHub.
- **Endnotes:** requires readers to jump; also disrupts reading.
- **Inline citation keys** (e.g., `[E5-cah33]`, `[E1-w0120]`, `[E3-2711§11]`): compact; preserves reading flow; scales cleanly.

Recommendation is the inline citation-key form. Full citation resolution lives in the evidence index sidecar `docs/research/playbook/evidence_index_v0_1_0.md` (per 2712 §11 and 2715).

Concrete format proposed in §5.3.

### 2.9 Are there opportunities to reduce repetition without weakening constitutional precision?

**Yes — four patterns of repetition were observed and each has a mitigation.**

| Repeated pattern | Occurrences (2716 draft) | Mitigation |
|---|---|---|
| "at the time of this Playbook version's ratification" | 4+ | Adopt shorthand "as of v0.1.0" once the version is established |
| Full workspace UUID `a9a16593-e0a4-44dc-8256-efc65d524b3c` | 5+ | Use "the Constitutional Workspace" once introduced; UUID in Appendix A |
| "workspace ratification records" (repeated phrase) | 10+ | Fine to keep; canonical term |
| Full deliverable UUIDs in §1.7 recital | 15+ | Move recital table to Appendix A: Reference Registry; chapter body cites short-names |

Precision is preserved because the Appendix table is authoritative.

### 2.10 Does the Playbook currently read like legislation rather than research?

**Mostly yes, with one exception.**

Legislative markers present:
- Consistent RFC 2119 usage.
- Third-person voice throughout.
- Present-indicative tense.
- Rule IDs on every normative statement.
- Class markers on every normative statement.
- No author voice, no marketing language, no uncertainty hedges.

Exception:
- §1.7 (Cycle 0 and Cycle 1A ratifications) reads like an archival recital rather than legislation. The list of 15+ deliverable UUIDs is descriptive, not normative. Legislative form would say "prior ratifications are enumerated in Appendix A; they remain immutable per PLAYBOOK-1.7.1."

**Recommendation:** move the §1.7 UUID recital to Appendix A: Reference Registry. Keep §1.7.1 through §1.7.3 (the normative rules) in-chapter. Chapter body becomes crisper legislation; archive lives in the appendix (a normal legislative form).

### 2.11 Could another Editor-in-Chief continue writing years from now without Claude's context?

**Partially, with three gaps.**

An Editor-in-Chief arriving fresh has access to:
- The Playbook body (with its chapters and rules).
- The evidence index sidecar (with citations resolved).
- The frontmatter (with version metadata).
- The prior-session research chain (2708–2715 as untracked or committed proposals).
- The frozen evidence manifest (2715).

Gaps a new Editor-in-Chief would face:

1. **The Playbook's authorial context** — the entire narrative logic of "why the six-layer stack" and "why workspace-canonical is beat by repo-canonical for the Playbook body but ratified from workspace" lives in the 2708-2715 chain but is not inside the Playbook itself. A new author would need to read 8 research documents totaling ~10,000 lines to catch up.

2. **The authoring protocol vs the drafting protocol** — 2713 codifies the drafting protocol. A future Editor-in-Chief needs to know 2713 is authoritative for how to write rules. This should be codified in Chapter 6 or Chapter 10.

3. **Session context conventions** — the practice of writing session-numbered handoffs (e.g., SESSION_2716), the practice of writing research proposals into `docs/research/platform/`, and the practice of using Claude to draft the Playbook are institutional knowledge, not documented rules.

**Recommendation:** Chapter 6 or Chapter 10 must include a `> **History:**` block or a rule that codifies the 2708-2715 research chain as canonical prior art. This makes the chain discoverable to a future Editor-in-Chief without prior context.

### 2.12 Are there hidden assumptions embedded in the writing style that future authors would not recognize?

**Yes — four significant hidden assumptions were observed.**

1. **"The Playbook" = "The Engineering Playbook".** The abbreviation is established in §0.1 parenthetical but easy to overlook. A future author might read "the Playbook" and wonder if it refers to a different playbook.

2. **RFC 2119 keyword strength is context-independent.** Actually RFC 2119 permits nuanced application ("MUST" can mean "MUST unless force majeure"). The Playbook implicitly treats them as absolute per 2713 §5.2. A future author might read this less strictly than intended.

3. **"MUST NOT be attempted through documentation amendment alone" (§1.5.3)** — this rule declares an obligation with no runtime enforcement mechanism. It relies on authors self-policing. A future author might not realize this rule cannot be automatically checked.

4. **"The System Owner is Chris West"** — hardcoded to a specific person. A future scenario where Chris is temporarily unavailable, permanently unavailable, or transfers ownership is not addressed. Chapter 10 or Chapter 8 should include a rule about delegation (deferred to Cycle 3+ per 2712 §12).

**Recommendation:** the hidden assumptions are acknowledged in this validation; three should become explicit rules in a future amendment (delegation especially). No v0.1 action.

### 2.13 Is the distinction between historical explanation and constitutional rule always obvious?

**Not always — one pattern of concern was observed.**

Session 2716 uses `> **History:**` blockquotes correctly in §1.7 and §1.8. This is the right pattern.

However, two rules FUSE historical assertion with normative content in a single sentence:

- PLAYBOOK-1.7.1: *"The Cycle 0 and Cycle 1A ratifications are immutable historical record. Playbook amendments MUST NOT modify their content, alter their status, or attempt retroactive re-classification..."*
  - First sentence is a historical/definitional statement; second is normative.

- PLAYBOOK-1.8.1: same pattern.

This is not incorrect — the normative rule follows from the historical fact — but the fusion is not the cleanest legislative form. Clean form would separate the historical assertion into a `> **History:**` block and state only the normative sentence as the rule.

**Recommendation:** for Chapter 6 authoring, adopt the discipline that a rule contains **only** normative content. Historical context lives in `> **History:**` blockquotes immediately preceding the rule. Document this as §5.5 authoring improvement.

### 2.14 Is there anything that should become a global authoring convention before additional chapters are written?

**Yes — four global conventions should be adopted.**

1. **Citation-key shorthand** (per Q7-Q8; §5.3 below).
2. **History-versus-rule separation discipline** (per Q13; §5.5 below).
3. **Fixed timepoint phrase** (per Q9; use "as of v0.1.0" or "at ratification of v0.1.0").
4. **Reference Registry appendix** (per Q9; §5.4 below).

Applying these before Chapter 6 begins reduces the retrofit cost of applying them later. Cost of applying now: ~30 minutes of pre-chapter pass. Cost of applying later: proportional to accumulated body size.

### 2.15 Is there anything that should become a reusable template before Chapter 6 begins?

**Yes — seven templates recommended (§6 below).**

Templates recommended:
1. Rule template.
2. Chapter frontmatter template.
3. Commentary template.
4. Example template.
5. History block template.
6. Future block template.
7. Cross-reference template.

Details in §6.

---

## 3. Structural findings

### 3.1 Rule ID uniqueness holds

Verified: all 37 rule IDs in the 2716 draft are unique. No ID collisions. Format `PLAYBOOK-N.M.K` consistently applied.

### 3.2 Section numbering gaps are normal

Chapter 0 has rules only in §0.3, §0.4, §0.6. Sections §0.1, §0.2, §0.5, §0.7, §0.8 are informative-only.

This is aesthetically imperfect (readers wonder "why does 0.5 have no rules?") but structurally correct. Informative-only sections are legitimate chapter content.

**No action.** Note in §5 as accepted convention.

### 3.3 Chapter closing sections use consistent structure

Chapter 0 and Chapter 1 both close with:
- Cross-references.
- Extension points.

Structure is per 2713 §10.3. Consistent.

### 3.4 Frontmatter template is under-tested

Only two chapters authored. Some frontmatter fields (`Rule ID range`, `Statement classes present`) were only manually computed. At scale, these should be autogen'd.

**Recommendation:** flag as Cycle 2 automation opportunity (per 2712 §17 CI validation).

### 3.5 Chapter length is uneven

- Chapter 0: 8 rules, ~400 lines of markdown.
- Chapter 1: 29 rules, ~700 lines of markdown.

Ratio is 3.6:1 rules and 1.75:1 lines. Chapter 1 will grow further as informative content is refined. Chapter 6 will likely be ~1000 lines.

**No action.** Length variance is fine; the Playbook is not required to have uniform chapters.

---

## 4. Rule architecture findings

### 4.1 Statement-class distribution is unbalanced

| Class | Chapter 0 | Chapter 1 | Total |
|---|---|---|---|
| `[AC]` | 0 | 20 | 20 |
| `[EP]` | 1 | 5 | 6 |
| `[GR]` | 7 | 4 | 11 |

Observations:
- Chapter 0 has 7/8 rules as `[GR]` (governance/procedural). Appropriate for a preamble.
- Chapter 1 has 20/29 rules as `[AC]`. Appropriate for constitutional context (structural rules).
- No `[OR]` (Operational Rule), `[IP]` (Implementation Pattern), `[RS]` (Repository Standard), `[RP]` (Runtime Policy), `[RC]` (Recovery Procedure), `[DR]` (Documentation Rule), `[RM]` (Research Methodology) rules yet.

Chapter 6 (per §9 below) will introduce many `[GR]` rules. Chapter 10 (Evolution & Amendment) will also be `[GR]`-heavy. Distribution will remain skewed until Chapters 2-9 are authored with `[OR]`, `[IP]`, `[RS]`, `[RP]`, `[RC]`, `[DR]`, `[RM]` content.

**No action.** Skew is expected during minimum-viable authoring.

### 4.2 Forward-reference dependency is manageable

Forward references in the 2716 draft:
- To Chapter 6 (Provenance Classification): 4 rules (PLAYBOOK-0.3.3, 0.3.4, 1.6.5 indirectly, 1.9.1 indirectly).
- To Chapter 10 (Evolution and Amendment): 5 rules (PLAYBOOK-0.6.1, 1.4.2, 1.6.5, 1.7.1, 1.9.1).
- To Chapters 2, 3, 4 (stub chapters): 3 rules (PLAYBOOK-1.6.5, 1.6.10 × 2).

Total forward references: ~12.

Once Chapters 6 and 10 are authored, each forward reference should be verified. This is a standard SIGN Check 4 (cross-reference integrity per 2713 §18).

**No action.** Forward references are normal during out-of-order authoring; SIGN cycle catches them.

### 4.3 Rule verbosity varies

- Shortest rule: PLAYBOOK-0.3.5 (~22 words).
- Longest rule: PLAYBOOK-1.7.1 (~40 words including two sentences).

Long rules risk being unmemorable and hard to reference in commentary. The 2713 §8.11 recommends 30 words or fewer per sentence.

Session 2716 mostly complies. A few rules approach or exceed 30 words. Adjusting is stylistic, not blocking.

**Recommendation:** for Chapter 6, aim for 25-30 word rules. Split multi-clause rules using rule sub-numbering (e.g., PLAYBOOK-1.7.1a, PLAYBOOK-1.7.1b) if needed — though this convention was not defined in 2713.

Actually, sub-numbering is NOT defined. Splitting means allocating new sequential rule IDs. Recommendation is: split into 2 separate rules with sequential IDs (PLAYBOOK-1.7.1 and PLAYBOOK-1.7.2).

---

## 5. Authoring improvements

Four global conventions to adopt before Chapter 6.

### 5.1 Fixed timepoint phrase

**Convention:** the phrase *"at the time of this Playbook version's ratification"* is replaced by *"as of v0.1.0"* (or the appropriate version).

**Rationale:** shorter; explicit about which version defines the point; unambiguous across future readings.

**Applied to future authoring.** No retrofit to 2716 draft; the 4 occurrences are acceptable.

### 5.2 Reference Registry appendix

**Convention:** introduce an appendix (Appendix A: Reference Registry) that lists canonical short-names for recurring artifacts:

- `WS-ARCH` = workspace `a9a16593-e0a4-44dc-8256-efc65d524b3c` (Architecture and Research).
- `ADR-W0110` = workspace deliverable `f2614585-…` (0110_ADR_DELIVERABLE_TO_DOCUMENT_MIRROR).
- `RATIF-0199` = workspace deliverable `c883ebef-…` (RATIFICATION_20260708_0199_CYCLE_1_CLOSEOUT).
- (etc.)

Chapter body cites short-names; Appendix A maps to full UUIDs + descriptions.

**Rationale:** reduces UUID repetition; centralizes reference maintenance; readable in the chapter body.

**Applied to Chapter 6 authoring.** Populate Appendix A concurrently with Chapter 6 content.

### 5.3 Citation-key shorthand

**Convention:** replace inline verbose citations with citation keys backed by the evidence index sidecar.

Verbose form (2716):
```
[E5: `content/_canonical_authority_helpers.py:33-60`; E1: workspace ADR-0120; E3: 2711 §11]
```

Shorthand form (proposed for Chapter 6):
```
[E5-CAH33; E1-W0120; E3-S2711§11]
```

Where:
- `E5-CAH33` = evidence class 5, source `content/_canonical_authority_helpers.py:33-60` (mapped in evidence index).
- `E1-W0120` = evidence class 1, workspace ADR 0120 (mapped in evidence index).
- `E3-S2711§11` = evidence class 3, Session 2711 §11 (mapped in evidence index).

**Rationale:** shorter, still readable; single-source-of-truth in the evidence index sidecar; line-number drift caught by evidence-index refresh rather than by chapter-wide edit.

**Applied to Chapter 6 authoring.** The evidence index sidecar for v0.1.0 acts as the authoritative citation dictionary. Chapter body uses shorthand.

**Retrofit:** the 2716 draft may be retrofitted at v0.2 (a PATCH bump) or left as-is (verbose citations are still valid — the shorthand is an alternative, not a replacement).

**Recommendation:** retrofit at v0.2 to unify style. Not blocking for Chapter 6.

### 5.4 History-versus-rule separation discipline

**Convention:** a `[AC]`, `[EP]`, or `[GR]` rule contains only normative content. Historical assertions live in a `> **History:**` blockquote immediately preceding the rule.

Non-compliant (2716):
```
**[AC] PLAYBOOK-1.7.1** The Cycle 0 and Cycle 1A ratifications are immutable historical record. Playbook amendments MUST NOT modify their content...
```

Compliant (proposed):
```
> **History:** The Cycle 0 and Cycle 1A ratifications are the platform's immutable prior constitutional record.

**[AC] PLAYBOOK-1.7.1** Playbook amendments MUST NOT modify the content of the Cycle 0 and Cycle 1A ratifications, alter their status, or attempt retroactive re-classification of their canonical authority.
```

**Rationale:** cleaner legislative form; rule sentence is standalone; history is discoverable but separated.

**Applied to Chapter 6 authoring.** Not retrofitted to 2716 draft.

**Retrofit:** consider at v0.2 (PATCH bump). Not blocking.

---

## 6. Reusable templates

Seven templates recommended before Chapter 6 authoring begins.

### 6.1 Rule template

```
**[CLASS] PLAYBOOK-N.M.K** <rule text with exactly one RFC-2119 keyword>. [<citation-key-1>[; <citation-key-2>]...]

> **Commentary:** <one-paragraph explanation>. (OPTIONAL — REQUIRED for [AC] and [EP])
```

Fields:
- `[CLASS]` = one of `[AC]`, `[GR]`, `[OR]`, `[EP]`, `[IP]`, `[RS]`, `[RP]`, `[RC]`, `[DR]`, `[RM]`.
- `PLAYBOOK-N.M.K` = stable rule identifier.
- Rule text = exactly one RFC-2119 keyword; ≤30 words; active voice; third person.
- Citation keys = per §5.3 shorthand backed by evidence index sidecar.
- Commentary = optional; required for `[AC]` and `[EP]` classes.

### 6.2 Chapter frontmatter template

```
## Chapter N — <Title in Title Case>

<!-- Chapter frontmatter -->

**Chapter ID:** PLAYBOOK-CH-N
**Purpose:** <one-sentence declaration of the chapter's role>
**Scope:** <what the chapter's rules govern>
**Introduced in:** vX.Y.Z
**Last substantive change:** vX.Y.Z
**Evidence anchor:** docs/research/playbook/evidence_index_vX_Y_Z.md#chapter-N
**Statement classes present:** [<class markers>]
**Rule ID range:** PLAYBOOK-N.a.b through PLAYBOOK-N.x.y

---
```

### 6.3 Commentary template

```
> **Commentary:** <explanation of the rule's purpose, motivation, or nuance>. <optional link to a specific piece of evidence>.
```

**Recommended length:** 1-3 sentences. Longer commentary indicates the rule may need to be split.

### 6.4 Example template

```
> **Example:** <illustrative usage of the rule>. <optional identification of a real prior occurrence>.
```

**When to use:** when the rule's application is non-obvious. Examples are informative only.

### 6.5 History block template

```
> **History:** <historical event or state that motivates the rule>. <optional link to session handoff or ratification record>.
```

**When to use:** when a rule exists only because of a specific past incident or state.

### 6.6 Future block template

```
> **Future:** <possible future extension or deferred concern>. <optional cycle target: Cycle N+, or specific version>.
```

**When to use:** when a rule points forward to work not yet in scope. Future blocks are informative and non-binding.

### 6.7 Cross-reference template

```
- Chapter <Symbolic Name> §<Symbolic Section Name>.
- Rule PLAYBOOK-N.M.K.
- Session <NNNN> §<section>.
- Workspace deliverable `WS-ARCH:<slug>` (per Appendix A: Reference Registry).
- Repository ADR `<name>`.
- Git tag `playbook-vX.Y.Z`.
```

**Format rule:** symbolic anchors (chapter titles + section titles) for cross-chapter references; rule IDs for specific rules; short-names from Appendix A for artifacts.

---

## 7. Risks

| # | Risk | Severity | Notes / mitigation |
|---|---|---|---|
| R1 | Chapter 6 authoring exceeds one session capacity | Med | Split across 2 sessions per §9.7 |
| R2 | Chapter 6 statement-class definitions drift from those used in Chapters 0 and 1 | Med | Chapter 6 authoring MUST match the 10 statement classes already used; any drift requires retrofitting Chapters 0 and 1 |
| R3 | Citation-key shorthand introduces a new maintenance surface (evidence index becomes load-bearing) | Low | Cycle 2 automation catches; low if evidence index is well-maintained |
| R4 | Reference Registry (Appendix A) drifts from workspace / repo state | Med | Autogen candidate for Cycle 2 |
| R5 | Retrofit of 2716 draft (from verbose to shorthand citations) risks introducing subtle citation errors | Low | Retrofit at v0.2 PATCH; SIGN catches |
| R6 | Rule relocation candidates (§2.4) may become MINOR amendments that fragment the review record | Low | Bundle relocations into a single MINOR amendment after Chapters 6 and 10 land |
| R7 | Forward references (§4.2) may resolve incorrectly once Chapters 6 and 10 exist | Med | SIGN Check 4 catches |
| R8 | History-vs-rule fusion (§5.5) may recur if authors are not disciplined | Low | Codify as §5.5 authoring improvement; SIGN reviewers watch for it |
| R9 | `_provenance.json` reconciliation with PIC-10 5-class taxonomy remains an open design question | Med | Chapter 6 §6.9 (per §9.4 below) resolves; no dependency on external decision |
| R10 | Chapter 6 length (projected 40-50 rules) creates SIGN batch pressure | Med | SIGN cycle across 3-4 batches per 2712 §7.3 |

---

## 8. Unknowns

| # | Unknown | Why it matters | How to resolve |
|---|---|---|---|
| U1 | Whether Chris prefers citation-key shorthand or verbose citations | Determines whether §5.3 convention is adopted | Chris directive at v0.1 SIGN or v0.2 PATCH planning |
| U2 | Whether the §1.7 UUID recital should be moved to Appendix A | Determines whether Chapter 1 is retrofitted | Chris directive |
| U3 | Whether the rule-relocation candidates in §2.4 should be executed at v0.1 or deferred | Determines v0.1 body finalization timing | Chris directive; recommendation is defer |
| U4 | Whether Chapter 6 should be authored in one session or two | Determines Session 2718 scope | §9.7 recommendation; Chris directive to accept or adjust |
| U5 | Whether the `> **Future:**` block convention (§6.6) has already been used elsewhere in the ecosystem | Consistency with prior repo conventions | Spot-check `docs/adr/ADR-0001..0004` frontmatter and body — not blocking |
| U6 | Whether the projected 40-50 rule count for Chapter 6 is accurate | Determines authoring effort | Actual authoring will refine; not blocking |
| U7 | Whether commentary requirements (§2.6) should be codified as a Chapter 10 rule | Consistency of commentary usage | Chris directive; recommendation to codify |
| U8 | Whether the citation-key shorthand affects RAG retrieval quality | Whether shorter citations lose semantic weight in embeddings | Cycle 2 empirical test; not blocking |

---

## 9. Chapter 6 preparation package

Complete package to permit Chapter 6 authoring to begin without further architectural discussion.

### 9.1 Chapter 6 outline

Proposed structure:

**Chapter 6 — Provenance Classification Standard**

- §6.1 Purpose and premise
- §6.2 The two concepts: content provenance classes and statement classes
- §6.3 Content provenance classes — the 5 PIC-10 classes
  - §6.3.1 Verified primary evidence
  - §6.3.2 Verified repository/runtime fact
  - §6.3.3 Verified quoted source
  - §6.3.4 Historical reconstruction
  - §6.3.5 Engineering conclusion
- §6.4 Statement classes — the 10 rule types
  - §6.4.1 [AC] Architectural Constraint
  - §6.4.2 [GR] Governance Rule
  - §6.4.3 [OR] Operational Rule
  - §6.4.4 [EP] Engineering Principle
  - §6.4.5 [IP] Implementation Pattern
  - §6.4.6 [RS] Repository Standard
  - §6.4.7 [RP] Runtime Policy
  - §6.4.8 [RC] Recovery Procedure
  - §6.4.9 [DR] Documentation Rule
  - §6.4.10 [RM] Research Methodology
- §6.5 Evidence classes — the 6 evidence classes E1–E6
- §6.6 Evidence admission standard — per-class thresholds
- §6.7 Provenance-honest attribution
- §6.8 Provenance recovery
- §6.9 Reconciliation with the `_provenance.json` 4-class system
- §6.10 Verification of provenance
- §6.11 Cross-references
- §6.12 Extension points

### 9.2 Estimated rule inventory

Estimates based on 2711 §11, 2712 §11, 2713 §6–§7, 2714 §2.7, 2715 §9:

| Section | Rules (est.) | Class distribution |
|---|---|---|
| §6.1 | 2-3 | [EP] |
| §6.2 | 2 | [EP] |
| §6.3 | 5 (one per PIC class) | [GR] |
| §6.4 | 11 (one per statement class + aggregate) | [GR] |
| §6.5 | 6 (one per evidence class) | [GR] |
| §6.6 | 11 (one per class threshold + convergent-research exception) | [GR] |
| §6.7 | 3-4 | [GR] |
| §6.8 | 3-4 | [GR] |
| §6.9 | 2-3 | [EP] |
| §6.10 | 2-3 | [DR] |

**Total estimate:** 47-50 rules.

**Complexity signal:** Chapter 6 is the second-largest chapter projected (Chapter 10 comparable at ~40 rules). Chapter 6 is denser (more rules per section).

### 9.3 Expected statement-class distribution

| Class | Count (est.) |
|---|---|
| `[GR]` Governance Rule | 35-38 |
| `[EP]` Engineering Principle | 6-9 |
| `[DR]` Documentation Rule | 2-3 |
| `[AC]` | 1-2 |

Chapter 6 is heavily `[GR]`. This is the meta-chapter about how rules are classified; nearly every rule in it governs authorial behavior.

### 9.4 Expected evidence mapping

Evidence sources per section (drawn from 2715 §9):

**§6.1 Purpose:**
- E3: 2712 §11 (evidence classes).
- E3: 2713 §6 (statement classes).
- E3: 2713 §7 (evidence admission).

**§6.2 Two concepts:**
- E3: 2711 §11 (canonicality vs authority analysis, adapted here).
- E3: 2712 §11 (evidence classes).

**§6.3 Content provenance classes:**
- E2: RATIF-0199 (Cycle 1A ratification, per Appendix A short-name) — the PIC-10 definitional origin.
- E2: workspace deliverable `0199_CYCLE_1_CLOSEOUT` Appendix D — PIC catalog.
- E6: SESSION_2707 §5 (G1 finding forcing PIC-10).

**§6.4 Statement classes:**
- E3: 2713 §6.1 (the 10 classes with authority, evidence requirement, versioning implications).

**§6.5 Evidence classes:**
- E3: 2712 §11.1 (E1–E6 taxonomy).
- E3: 2713 §7.1 (per-class matrix).

**§6.6 Evidence admission standard:**
- E3: 2713 §7 (thresholds, convergent-research exception).

**§6.7 Provenance-honest attribution:**
- E6: SESSION_2707 §4 (Chris's reconciling directive unrecoverable → provenance-honest attribution pattern).
- E4: `ChatConversation` pin `pa-e308b1e6dcd444d2` turn 5 recovery.

**§6.8 Provenance recovery:**
- E6: SESSION_2707 §4 timeline (Rigby FAIL verbatim recovery via ORM).
- E3: 2712 §11.4 (evidence-index drift check).

**§6.9 Reconciliation with `_provenance.json`:**
- E5: `docs/_provenance.json` `_meta.confidence_breakdown` (`HIGH=1591`, `MEDIUM=352`, `LOW=5`, `UNKNOWN=490` as of 2026-07-08).
- E5: `docs/_provenance.json` `_meta.command`, `_meta.excludes`, `_meta.schema_version`.
- E3: 2714 §17.1 Amendment D.

**§6.10 Verification of provenance:**
- E3: 2712 §11.4 (drift check).
- E3: 2713 §18 (8-check protocol).

**Total unique evidence sources cited in Chapter 6 (est.):** 20-25.

**No new evidence gathering required.** All sources are in the frozen manifest.

### 9.5 Expected cross-references

Chapter 6 cross-references:

- **To Chapter 0:** §0.3 (RFC 2119 interpretation) — Chapter 6 statement-class markers require RFC 2119 in every rule.
- **To Chapter 1:** §1.3 (canonicality vs ratification) — Chapter 6 §6.2 explicitly extends the two-orthogonal-dimensions concept.
- **To Chapter 1:** §1.10 (rule origin discipline) — Chapter 6 §6.6 supersedes 1.10.1 through 1.10.3 as the fuller treatment.
- **To Chapter 10:** §Amendment Discipline (chapter to be authored later).
- **To Chapter 10:** §Rule Identifiers (chapter to be authored later).

### 9.6 Dependencies on Chapters 0 and 1

Chapter 6 depends on:

- The definition of RFC 2119 (Chapter 0 §0.3).
- The definition of `canonical_authority` and its three-value enum (Chapter 1 §1.4).
- The definition of ratification and workspace ratification records (Chapter 1 §1.3).
- The layer model (Chapter 1 §1.2) — for identifying the correct evidence class for platform-scope vs workspace-scope evidence.

Forward references from Chapters 0 and 1 that Chapter 6 must resolve:

- PLAYBOOK-0.3.3: "per Chapter Provenance Classification §Statement Classification."
- PLAYBOOK-0.3.4: "drawn from the frozen evidence manifest" — Chapter 6 §6.6 defines "drawn from."
- PLAYBOOK-1.6.5, PLAYBOOK-1.6.10: "per Chapter [name] §[section]."
- PLAYBOOK-1.10.1 through 1.10.3: implicitly depend on Chapter 6 defining what a source is.

Chapter 6 authoring MUST populate these forward-referenced sections with content that matches the citing rules' expectations.

### 9.7 Recommended authoring sequence

Given projected 47-50 rules, Chapter 6 authoring in a single session is possible but risks fatigue-induced quality drop. Recommendation:

**Session 2718 (proposed):** author §6.1–§6.6 (approximately 30 rules, covering purpose, two concepts, PIC classes, statement classes, evidence classes, and admission standard). This is the "foundations" half.

**Session 2719 (proposed):** author §6.7–§6.12 (approximately 15-20 rules, covering provenance-honest attribution, recovery, `_provenance.json` reconciliation, and verification). This is the "operational" half plus closing sections.

**SIGN target:** after Session 2719, Chapter 6 is complete. SIGN cycle can be dispatched.

Alternative: single session with acknowledged length (~1200-1500 lines of markdown; 47-50 rules). Feasible but risks time overrun. Chris directive.

### 9.8 Risks before Chapter 6 authoring begins

Risks specific to Chapter 6 (adding to §7 risks):

**R11 (Chapter 6-specific):** the §6.9 reconciliation with `_provenance.json` is an open design question at the time of this validation. Chapter 6 §6.9 authoring MUST resolve it. Two options are viable:

  1. **PIC-10 as canonical for governance artifacts; `_provenance.json` as a broader corpus-tracking system.** PIC-10's 5 classes are for ratified artifacts and their citations; `_provenance.json`'s 4 confidence tiers are for the broader documentation corpus. The two systems co-exist because they answer different questions.

  2. **Bidirectional mapping.** PIC-10 classes are richer; each `_provenance.json` tier maps to one PIC-10 class or is derivable from PIC-10 classification.

Recommendation (adopted here as a preliminary decision to be codified in Chapter 6 §6.9): Option 1. Rationale: PIC-10 exists for governance-envelope discipline; `_provenance.json` is a separate corpus-tracking artifact that predates PIC-10 and serves a different purpose. Attempting bidirectional mapping introduces coupling that constrains both systems.

**R12 (Chapter 6-specific):** the statement-class definitions and evidence thresholds must match those already used in Chapters 0 and 1. Divergence would require retrofit of the 2716 draft. This risk is mitigated by using 2713 §6.1 and §7.1 as the direct source.

**R13 (Chapter 6-specific):** the SIGN cycle for Chapter 6 will be dense (many rules; many forward-reference resolutions). Recommend 3-4 SIGN batches for adequate adversarial coverage.

---

## 10. Recommendation

### 10.1 Pre-Chapter-6 preparation pass

Before authoring Chapter 6 begins, complete a short preparation pass that:

1. **Establishes Appendix A: Reference Registry** as a stub file (`docs/research/playbook/appendix_a_reference_registry_v0_1_0.md`). Populate with the short-names surfaced in Chapter 1 (WS-ARCH, ADR-W0110 through ADR-W0150, RATIF-0100, RATIF-0140, RATIF-0150, RATIF-0199, and the Cycle 0 short-names). Full UUIDs and titles live here.

2. **Establishes the evidence index sidecar stub** (`docs/research/playbook/evidence_index_v0_1_0.md`). Populate with the citation keys used by Chapters 0 and 1 (retrofit-ready) and reserve keys for Chapter 6 evidence. This becomes the authoritative citation dictionary per §5.3.

3. **Documents §5 conventions** (citation shorthand, Reference Registry short-names, history-vs-rule discipline, fixed timepoint phrase) as an authorial addendum to 2713. This can live in the session-2717 output document (this file); it will be codified formally in Chapter 6 §6.11 or Chapter 10.

Preparation pass estimated effort: 30-60 minutes.

### 10.2 Chapter 6 authoring

Begin Chapter 6 authoring in Session 2718. Author §6.1–§6.6 in Session 2718. Author §6.7–§6.12 in Session 2719. SIGN cycle after Session 2719.

Use the templates in §6 of this report.

Cite from the frozen evidence manifest only (§9.4 mapping).

### 10.3 Non-actions (v0.1)

- Do NOT retrofit the 2716 draft to shorthand citations (defer to v0.2 PATCH).
- Do NOT relocate the misplaced-rule candidates from §2.4 (defer to a post-v0.1 MINOR amendment).
- Do NOT restructure §1.7 to move UUIDs to Appendix (defer to v0.2 PATCH; the UUID recital is acceptable at v0.1).
- Do NOT modify `docs/ENGINEERING_PLAYBOOK.md` (file not created yet; the 2716 draft continues to live in `docs/research/platform/`).
- Do NOT begin SIGN on the 2716 draft (per 2713 §23.2 sequence; SIGN comes after all v0.1 content is drafted).

### 10.4 Repository state at close

Branch `main`, HEAD `309f85ee`. Working tree clean save for ten untracked research proposals (2708 through 2717).

The Playbook body file at `docs/ENGINEERING_PLAYBOOK.md` remains uncreated; Chapters 0 and 1 draft continues to live in `docs/research/platform/playbook_authoring_session_2716.md`; validation and Chapter 6 prep live in this document.

---

_End of Session 2717 Playbook Authoring Validation and Chapter 6 Preparation. No Playbook content authored. No SIGN cycle dispatched. No repository files modified outside `docs/research/platform/`. No architectural research performed. Repository ends clean._

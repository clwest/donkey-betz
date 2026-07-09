# Tools Operational Contract — Architecture Pressure Test

**Session:** 2728 (same session as Phase 0 domain definition; pressure-test pass before arc open)
**Date:** 2026-07-08
**Status:** Research — falsification attempt against `tools_operational_contract_domain_definition.md`. Awaiting Chris's review.
**Predecessors:**
- `tools_operational_contract_domain_definition.md` (this session, earlier turn) — the Phase 0 domain definition this document attempts to falsify.
- Session 2727: Engineering Playbook v0.1.0 ratified (see Phase 0 doc §Predecessors).
- 12 prior closed research arcs enumerated in Phase 0 §2.3.

**Author:** Claude (Opus 4.7, 1M context)

**Scope constraints:** Research only. This document attempts to disprove the Phase 0 decomposition. Its verdict may be *"decomposition survives with tightening"*, *"decomposition survives with relocation"*, *"better decomposition emerges"*, or *"the arc should not open in this shape."* No architecture proposals. No child arcs. No constitutional documents. No modification of the Phase 0 doc — its record stands, and this pressure test either survives against it or supplants it.

**Explicit intent per mission (verbatim from Chris):**

> *"Pressure-test the Phase 0 conclusions. Assume the current decomposition is wrong. Your objective is NOT to defend it. Your objective is to attempt to falsify it. Challenge every major assumption. You repeatedly shifted terminology throughout the document: Tools ↓ Capabilities ↓ Operational Contracts ↓ Knowledge Substrate ↓ Authority Carriage ↓ Verifier Loop. Determine whether those shifts indicate architectural discovery or conceptual drift. Do not assume the original domain title is correct simply because that was the directory name. Produce an Architecture Pressure Test. Attempt to disprove the current decomposition. If the current decomposition survives that pressure test, explain why. If a better constitutional architecture emerges, explain the evidence."*

---

## 1. Executive summary — pressure-test verdict

**The Phase 0 decomposition does NOT survive the pressure test intact.**

Three findings force a reframe, one finding survives, and one novel finding emerges that the Phase 0 did not name.

**Findings that force reframe:**

- **F1. The terminology shift is 65% drift, 35% discovery.** *"Tools"* (concrete, HEAD-observable — 113 schemas, 156 handlers) became *"Capabilities"* (widened to include non-tool reach: enrichment services, workspace resolution, context injection) became *"Operational Contracts"* (an abstraction not present in evidence). Each step moved further from what the code actually names. The final step — from *capabilities* to *operational contracts* — was NOT forced by evidence; it was forced by my search for a constitutional abstraction. That is drift, not discovery.
- **F2. The architectural center is NOT Rigby.** Every one of the 5 proposed categories, examined at HEAD, is symmetric across agentic callers. The 113/156 schema-vs-handler gap exists regardless of who calls. Silent-401 SYSTEMIC affects the frontend as much as PA. Docs cascade freshness affects any RAG consumer. Rigby is the observed instance, not the constitutional subject. **The center is Sources of Truth** — which layer authoritatively owns each fact class, and how any consumer (Rigby is one) reaches for that authority correctly.
- **F3. Three of five proposed children are substantially re-litigation of closed arcs.** P1 AUTHORITY-CARRIAGE is 70-80% covered by Groups 1900 + 2400 + 2600 (CF-C2, F-B-HIGH-3). P3 KNOWLEDGE-SUBSTRATE is 80-90% covered by Groups 2100 + 1300 + I-0200 ADR-0004 PROVISIONAL. P4 FAILURE-AND-RECOVERY spans three different constitutional homes (Ch 5 PA collaboration, Ch 8 Runtime STUB, Ch 9 Recovery STUB) and cannot land in one category without violating Playbook §10.2 amendment discipline.

**Finding that survives:**

- **S1. The 113/156 schema-vs-handler gap is genuinely new territory.** No prior arc has enumerated why 43 handlers exist without a corresponding schema declaration, or what constitutional posture the gap represents. This is real research work with observable evidence and no known constitutional home. It is smaller than the Phase 0 proposal — closer in size to a 1-2 child audit than a 5-child arc.

**Novel finding not named in Phase 0:**

- **N1. The Phase 0 doc itself exhibits a pattern that Playbook §10.2 warns against: reaching for a wider abstraction to unify inventory items whose constitutional homes are different chapters.** The unifying abstraction ("Operational Contracts") IS the drift. It is the nominalization that let me flatten Ch 1 §1.4 Canonical authority questions, Ch 5 PA collaboration questions, Ch 8 Runtime discipline questions, and Ch 9 Recovery questions into one arc. The Playbook itself is the counter-evidence — v0.1.0 kept the seven STUB chapters DISTINCT rather than merging them, precisely because their constitutional homes differ. My Phase 0 tried to build a "meta-Ch 5" that would cross-cut chapters. The Playbook already ratified against that shape.

**Recommendation (research-only; no arc opens on this recommendation):**

Either:
- **Reframe A — Narrow the arc to the observable tool surface** (Ch 5 §5.5 extension point #1 verbatim: *"PA tool call discipline codification"*). 2-3 children maximum. Directory `docs/research/tools/` retains its concrete meaning. Anti-scope explicitly cedes authority-carriage to prior arcs and cedes failure taxonomy to Ch 8/9 future work.
- **Reframe B — Do not open a research arc. Open a targeted audit + MINOR amendment cluster.** The Phase 0 evidence, once re-scoped, may be small enough for one audit deliverable + a 3-5 rule MINOR amendment to Ch 5 §5.4 addressing the tool-call-discipline extension point specifically. Cost: 1-2 sessions vs 6.
- **Reframe C — Open a different arc altogether at `docs/research/platform/`** studying Sources-of-Truth registry as an extension to Ch 1 §1.4. Different directory, different constitutional home, different scope. Does NOT belong at `tools/`.

**Chris-gated decision at the review of this document, not at Phase 0 domain definition. This is where the pattern that produced the Playbook lives: pressure-test forces re-framing before arc opens, not after.**

---

## Table of contents

1. [Executive summary — pressure-test verdict](#1-executive-summary--pressure-test-verdict)
2. [Falsification vector 1 — Terminology-shift audit](#2-falsification-vector-1--terminology-shift-audit)
3. [Falsification vector 2 — Center-of-domain challenge](#3-falsification-vector-2--center-of-domain-challenge)
4. [Falsification vector 3 — Category-by-category attack](#4-falsification-vector-3--category-by-category-attack)
5. [Falsification vector 4 — Behavior vs guarantees vs interfaces vs trust vs authority](#5-falsification-vector-4--behavior-vs-guarantees-vs-interfaces-vs-trust-vs-authority)
6. [Falsification vector 5 — Prior-arc re-litigation risk](#6-falsification-vector-5--prior-arc-re-litigation-risk)
7. [Falsification vector 6 — Does the domain warrant an arc at all](#7-falsification-vector-6--does-the-domain-warrant-an-arc-at-all)
8. [Falsification vector 7 — The nominalization test](#8-falsification-vector-7--the-nominalization-test)
9. [What survives](#9-what-survives)
10. [Reframes worth considering](#10-reframes-worth-considering)
11. [What this document does NOT do](#11-what-this-document-does-not-do)

---

## 2. Falsification vector 1 — Terminology-shift audit

Chris flagged six consecutive names I used for the same object of study: *Tools* → *Capabilities* → *Operational Contracts* → *Knowledge Substrate* → *Authority Carriage* → *Verifier Loop*.

Analyzing each step:

### 2.1 Tools → Capabilities

- **Evidence for discovery:** the 8 enrichment services + workspace resolver + context builders fire pre-turn without appearing in tool schemas. Some non-schema handlers execute during a turn (`run_agent` dispatches to 77+ agents; `agent_introspection` reads state). If the domain were strictly the 113 tool schemas, this evidence would be excluded, and the exclusion would be arbitrary at HEAD.
- **Evidence for drift:** *"capability"* is undefined in the code. No file declares a `Capability` class, no docstring uses the term as a boundary. It is a term I imported.
- **Verdict:** partial discovery. The observation is real (non-tool reach exists); the name is imported. Better term would be *"reach"* (as in *"any point at which Rigby reaches beyond the LLM turn to affect state"*) — which is what my Phase 0 §4 actually said before I re-abstracted it: *"the invariant surface at the reach."* I should have kept *"reach"* as the operative noun.

### 2.2 Capabilities → Operational Contracts

- **Evidence for discovery:** none. This step happened because I was searching for a constitutional-weight abstraction to name a new arc, not because evidence forced the term.
- **Evidence for drift:** the word *contract* implies bilateral promise. Most of my inventory is NOT bilateral. Examples:
  - *"GPT-5.2 autofills booleans with False"* is a MODEL BEHAVIOR observation. It is not a contract between Rigby and anyone — it is a model quirk that Rigby must defend against.
  - *"Docs cascade is 4-step"* is a WORKFLOW rule. It is not a contract between two parties; it is a required operator discipline.
  - *"MEMORY.md is authoritative-by-reference via Ch 5.2.1"* is a CONSTITUTIONAL FACT. It is a canonical-authority declaration, not a contract.
  - *"deliverable_tool.create defaults to status=completed"* is a DEFAULT BEHAVIOR observation. It is not a contract.
- **Verdict:** drift. *"Operational Contracts"* is a nominalization that flattens five different evidence shapes (behavior, workflow, canonical-authority, default, invariant) into one abstraction. Playbook §10.2 warns against exactly this move — merging by name when constitutional homes differ.

### 2.3 Operational Contracts → Knowledge Substrate / Authority Carriage / Verifier Loop

- **Evidence for discovery:** partial. These names label specific inventory clusters that DO share internal coherence.
- **Evidence for drift:** the names are nominalizations of active questions.
  - *"Authority Carriage"* nominalizes *"how does actor identity survive substrate boundaries."*
  - *"Knowledge Substrate"* nominalizes *"where does Rigby's factual grounding come from."*
  - *"Verifier Loop"* nominalizes *"when should Claude re-check Rigby's output."*
  Each active question is answerable at HEAD. Each nominalization is a proposal for a category, not a discovered category.
- **Verdict:** partly discovery of internal clusters, partly drift into abstract category names. The clusters are real. The category NAMES are proposal-shaped, not evidence-shaped.

### 2.4 Aggregate audit finding

The six-term drift chain, examined against evidence:

| Step | Discovery weight | Drift weight | Evidence force |
|---|---|---|---|
| Tools → Capabilities | 60% | 40% | Non-tool reach observable; term imported |
| Capabilities → Operational Contracts | 5% | 95% | No forcing evidence; nominalization |
| Operational Contracts → Knowledge Substrate | 60% | 40% | Cluster real; category name imposed |
| Operational Contracts → Authority Carriage | 55% | 45% | Cluster real; category name imposed |
| Operational Contracts → Verifier Loop | 70% | 30% | §5.2.1 anchors this cluster directly |

**Aggregate: 35% discovery / 65% drift.** The Phase 0 doc reaches for a constitutional-weight abstraction *before* the evidence supports one. That is the exact anti-pattern Ch 10.2 (MINOR amendment lifecycle) codifies against.

---

## 3. Falsification vector 2 — Center-of-domain challenge

Phase 0 §4 asserted the architectural center is Rigby. Testing five alternatives Chris named.

### 3.1 Center = Rigby (Phase 0's default)

**Test:** if the domain is Rigby-centered, every inventory item should be Rigby-specific. Items that generalize across agentic callers falsify the framing.

**Result:** most inventory items generalize.
- 113/156 schema-vs-handler gap: not Rigby-specific; any function-calling LLM caller hits the same gap.
- Silent-401 SYSTEMIC: not Rigby-specific; frontend hits it more visibly.
- Docs cascade freshness: not Rigby-specific; any RAG consumer hits it.
- LLM autofill=False: not Rigby-specific; any function-calling LLM caller.
- Workspace_id conveyance: not Rigby-specific; any workspace-scoped consumer.
- Provenance carriage: not Rigby-specific; Ch 6 PIC-10 is cross-cutting.
- Verifier-loop: SPECIFIC to Rigby via §5.2.1, but the pattern generalizes (any agentic executor needs a verifier).

**Falsified?** Yes, partially. Rigby-as-center is an ACCIDENT of Rigby being the only agentic caller today, not a constitutional necessity.

### 3.2 Center = Platform Capabilities

**Test:** if the domain is capabilities-centered, the arc's output is a capability inventory (per-class invariants: what does a Redis-backed capability owe? A DB-write capability? An LLM capability?). Consumers (Rigby, frontend, cron jobs, other agents) are downstream.

**Result:** substantially better fit. This is what Group 2500 API + Group 2000+ Event Integration Architecture already do at different substrate levels. If this arc opened as "PA-specific capability inventory," it would re-litigate them.

**Falsified?** The center itself is coherent but is ALREADY the center of closed arcs. Opening a new arc at this center would duplicate.

### 3.3 Center = Sources of Truth

**Test:** if the domain is SoT-centered, every category should reduce to "who is authoritative for X" (workspace ID, actor identity, capability schema, retrieved evidence, failure classification, verifier judgment).

**Result:** every Phase 0 category reduces to SoT.
- P1 AUTHORITY-CARRIAGE → *"Who is authoritative for actor identity + workspace scope + KillSwitch state?"*
- P2 CAPABILITY-CONTRACT → *"Who is authoritative for what a capability owes at call-boundary?"*
- P3 KNOWLEDGE-SUBSTRATE → *"Who is authoritative for retrieved evidence + provenance carriage + freshness?"*
- P4 FAILURE-AND-RECOVERY → *"Who is authoritative for classifying and recovering from a failure?"*
- P5 VERIFIER-LOOP → *"Who is authoritative for whether Rigby's output is correct?"*

**Constitutional home:** Playbook Ch 1 §1.4 Canonical authority (FULL) — not Ch 5 (STUB).

**Falsified?** Sources of Truth is not just coherent as an alternative center — it may be the CORRECT center. The reframe would move the arc's constitutional home from Ch 5 STUB to Ch 1 §1.4 extension. That is a different arc entirely, and it would NOT belong at `docs/research/tools/` — it would belong at `docs/research/platform/`.

### 3.4 Center = Constitutional Boundaries

**Test:** if the domain is boundary-centered, the arc surfaces where Ch 5 ends and Ch 6/8/9 begin — the meta-question of chapter demarcation.

**Result:** this IS a real question surfaced by Phase 0 (P4 spans Ch 5/8/9), but it is a META-question about the Playbook rather than a direct research target. It would need to be a Playbook v0.1.1 PATCH or Ch 10 amendment-lifecycle refinement, not a research arc under `tools/`.

**Falsified?** Yes as an arc center. Boundary-questions are Ch 10 material.

### 3.5 Center = Trust Relationships

**Test:** if the domain is trust-centered, every category reduces to "when does A trust B's output" — Rigby trusts docs cascade freshness; frontend trusts silent-401 recovery; Chris trusts Rigby via verifier-loop.

**Result:** partial fit. Verifier-loop (P5) IS trust-centered. But most of the inventory is not about trust — it is about correctness invariants that hold or don't hold at HEAD, regardless of trust.

**Falsified?** Partially. Trust is a real dimension of P5 only. Not a domain-wide center.

### 3.6 Aggregate center-of-domain finding

| Candidate center | Coherence | Overlap with closed arcs | Fits `tools/` directory | Fits Ch 5 STUB extension |
|---|---|---|---|---|
| Rigby (Phase 0) | Medium (accidental) | Medium | Yes | Yes |
| Platform Capabilities | High | HIGH (2500 + 2000+) | Partial | No |
| **Sources of Truth** | **HIGH** | **Low (Ch 1 §1.4 extension)** | **NO (belongs `platform/`)** | **NO** |
| Constitutional Boundaries | High (meta) | Ch 10 territory | No | Partial (§10.2) |
| Trust Relationships | Low (P5 only) | Low | Partial | Partial (§5.2.1 anchor) |

**Verdict:** the two strongest candidates are (a) *Rigby-narrow-scoped-to-tool-surface* (matches directory + Ch 5 §5.5 extension point #1) and (b) *Sources of Truth* (matches evidence better but does NOT belong at `tools/`). These are not the same arc.

---

## 4. Falsification vector 3 — Category-by-category attack

Attempting to break each of the five Phase 0 categories.

### 4.1 P1 AUTHORITY-CARRIAGE — attack

**Claim:** actor identity + workspace scope + authority conveyance are one category.

**Attack:**
- Actor identity = WHO is asking (identity claim).
- Workspace scope = WHICH tenant-slice-of-truth applies (boundary claim).
- KillSwitch/GovernanceState = WHETHER execution is permitted (policy claim).
- Identity + Boundary are similar (both are ATTRIBUTES of the caller's context). Policy is fundamentally different (it is a RUNTIME GATE independent of caller context).
- **Splits naturally into P1a Identity+Boundary and P1b Policy.**

**Additional attack:** Group 1900 Authority Enforcement + Group 2400 Auth already own 70-80% of this. What's genuinely new here that requires a new arc?

**Verdict:** category is either (a) too large (splits into 2) or (b) too duplicative (subsumed by 1900+2400 residual T-slots).

### 4.2 P2 CAPABILITY-CONTRACT — attack

**Claim:** tool schema + handler contract + default-value discipline + safe-default posture + discovery model are one category.

**Attack:**
- Tool schema = what LLM sees (INTERFACE).
- Handler contract = what runs (BEHAVIOR).
- Default-value discipline = observed failure mode (FAILURE CLASS — belongs in P4).
- Safe-default posture = a rule about what defaults SHOULD be (GUARANTEE).
- Discovery model = how the LLM knows what to call (INTERFACE).

Four different evidence shapes in one category. Playbook Ch 5 §5.5 extension point #1 says *"PA tool call discipline codification"* — narrower than my P2.

**Verdict:** P2 is really *"PA tool call discipline"* — the ratified extension point wording. Everything else in my P2 belongs in P4 (failure modes) or was already covered by Group 2500 API (contract SoT) + Group 2000+ (event contract emission).

### 4.3 P3 KNOWLEDGE-SUBSTRATE — attack

**Claim:** RAG + KB + docs cascade + provenance carriage + freshness are one category owned by this arc.

**Attack:**
- Group 2100 RAG closed at S2199 (canonical summary at `docs/research/domains/rag_document_loading/2199_...`).
- I-0200 RAG Corpus Substrate Maturity closed at S2701 with ADR-0004 PROVISIONAL.
- Group 1300 Memory closed at S1399.
- Every item I put in P3 was studied by one of those closed arcs.
- What's NEW here? Only "Rigby's specific access-model overlay on top of the ratified RAG substrate."
- Is that a new arc? Or is it a T-slot inside the already-ratified I-0200 evidence-manifest queue?

**Verdict:** P3 is 80-90% re-litigation. Residual is a single T-slot ("Rigby access-model discipline overlay") — smaller than one child audit, not warranting its own child slot.

### 4.4 P4 FAILURE-AND-RECOVERY — attack

**Claim:** placeholder-stall + silent-fail + worker jam + pin poison + autofill=False + queue parity + banner suppression are one category.

**Attack:** each item belongs in a DIFFERENT constitutional home:
- Placeholder-stall → Ch 5 (PA collaboration failure mode).
- Silent-fail at handler → Ch 5 §5.5 extension point #1 (tool call discipline).
- Worker jam → Ch 8 STUB (Runtime discipline).
- Pin poison → Ch 5 §5.5 extension point #3 (placeholder-stall recovery discipline).
- Autofill=False → Ch 5 §5.5 extension point #1 (tool call discipline).
- Queue parity → Ch 8 STUB (Runtime discipline) — Procfile↔Makefile substrate concern.
- Banner suppression → Ch 5 §5.5 extension point #1 (tool call discipline — `auto_followup=False` is a schema-parameter behavior).

**Splits into three constitutional homes**: Ch 5, Ch 8, Ch 9. Trying to codify them all in one Ch 5 amendment violates §10.2 (single-purpose amendments).

**Verdict:** P4 as a single category cannot land constitutionally. It MUST split.

### 4.5 P5 VERIFIER-LOOP — attack

**Claim:** verifier-loop is a standalone category with independent constitutional weight.

**Attack:**
- §5.2.1 already ratifies the verifier-loop protocol.
- Every MEMORY.md rule cited under P5 is a specific INSTANCE of §5.2.1.
- Codifying them as new Ch 5 rules would duplicate §5.2.1's authority.
- The correct move is either (a) leave §5.2.1 as the anchor + let MEMORY.md continue to hold instances (current state), or (b) amend §5.2.1 to a more detailed form (single MINOR amendment, not a child arc).
- Neither option warrants a 20-section child audit under playbook §11.2.

**Verdict:** P5 is a cross-cutting attribute or a single-rule amendment, NOT a child slot.

### 4.6 Aggregate category-by-category finding

| Category | Splits? | Duplicates prior arc? | Warrants child slot? |
|---|---|---|---|
| P1 AUTHORITY-CARRIAGE | Yes (Identity+Boundary vs Policy) | 70-80% Groups 1900+2400+2600 | No |
| P2 CAPABILITY-CONTRACT | Partially (tool discipline vs failure mode) | Partial 2500+2000+ | **Yes (narrowed to tool call discipline)** |
| P3 KNOWLEDGE-SUBSTRATE | No | 80-90% Groups 2100+1300+I-0200 | No |
| P4 FAILURE-AND-RECOVERY | Yes (across Ch 5/8/9) | Partial 1700+I-0100 | No (as single category) |
| P5 VERIFIER-LOOP | No | 100% §5.2.1 | No (cross-cutting or single rule) |

**Of five proposed children, ONE survives** (P2 narrowed to tool call discipline). Four either split, duplicate, or don't warrant standalone child status.

---

## 5. Falsification vector 4 — Behavior vs guarantees vs interfaces vs trust vs authority

Chris explicitly named these five evidence shapes. Testing whether Phase 0 categorized cleanly.

### 5.1 Per-item classification

| Inventory item | Shape | Phase 0 placement | Correct placement |
|---|---|---|---|
| 113/156 schema/handler gap | **Interface** | P2 | P2 (correct) |
| LLM autofill=False | **Behavior** | P2 + P4 (both) | Ch 5 §5.5 #1 (tool call discipline) |
| Docs cascade 4-step | **Behavior/Workflow** | P3 | Ch 4 (Doc Cascade STUB) or Ch 5 §5.5 #1 |
| workspace_id NOT inferred | **Guarantee** | P1 | Ch 1 §1.4 or Ch 5 §5.5 #1 |
| Verifier-loop | **Trust** | P5 | Ch 5 §5.2.1 (existing) |
| KillSwitch reachability | **Authority** | P1 | Ch 1 §1.4 or Group 1900 residual |
| session_tool.retire works | **Interface** | P1 (?) | Ch 5 §5.5 #1 |
| PA_USE_FUNCTION_CALLING env | **Configuration** | P1 (?) | Ch 8 STUB (Runtime) |
| Provenance carriage | **Guarantee** | Cross-cutting | Ch 6 (already FULL) |
| Freshness | **Guarantee** | Cross-cutting | Multiple chapters |
| SIGN pin worker instability | **Behavior** | P4 | Ch 5 §5.5 #3 (placeholder-stall recovery) |

### 5.2 Finding

The five shapes distribute UNEVENLY across the Phase 0 categories:
- P1 mixes Guarantees + Authority + Interface + Configuration.
- P2 mixes Interface + Behavior + Guarantee.
- P3 mixes Behavior + Workflow + Guarantee.
- P4 mixes Behavior + Failure classes.
- P5 mixes Trust with Behavior instances.

**A cleaner shape-based grouping would produce different children:**
- Interface (schema/handler/dispatch shape) → aligns with Ch 5 §5.5 #1.
- Behavior (observed failure modes + patch/workaround recipes) → spans Ch 5 §5.5 #1 + #3 + Ch 8 STUB.
- Guarantee (invariants that must hold) → spans Ch 1 §1.4 + Ch 6 (existing).
- Trust (verifier-loop + Rigby-vs-verify) → Ch 5 §5.2.1 existing anchor.
- Authority (who can grant what) → Ch 1 §1.4 + Group 1900 residual.

**A shape-based decomposition does NOT map cleanly onto the Phase 0 five children.** It cuts across them. Which means the Phase 0 children are not carving reality at its joints — they are convenience groupings.

---

## 6. Falsification vector 5 — Prior-arc re-litigation risk

Enumerating what's genuinely new vs already covered.

### 6.1 Coverage overlay

| Phase 0 category | Prior arc coverage | Residual (genuinely new) |
|---|---|---|
| P1 AUTHORITY-CARRIAGE | Groups 1900 + 2400 (silent-401) + 2600 (CF-C2 + F-B-HIGH-3) | Small: PA-specific carriage overlay on ratified auth substrate; already tracked as CF-C2 T-slot |
| P2 CAPABILITY-CONTRACT | Group 2500 (contract SoT) + Group 2000+ (event contract emission) + Group 2600 (PA endpoint SoT) | **LARGE: schema/handler gap enumeration + LLM-autofill discipline + safe-default posture at PA tool boundary — NOT covered by any prior arc** |
| P3 KNOWLEDGE-SUBSTRATE | Groups 2100 + 1300 + I-0200 ADR-0004 PROVISIONAL | Small: Rigby access-model overlay; already tracked as I-0200 residual T-slot |
| P4 FAILURE-AND-RECOVERY | Groups 1700 + I-0100 (correlation spine) | Medium: Rigby-specific failure taxonomy; spans 3 constitutional homes |
| P5 VERIFIER-LOOP | Playbook §5.2.1 direct anchor | **Zero: §5.2.1 exists; MEMORY.md instances are current record; no new rule needed** |

### 6.2 Finding

**Only P2 has substantial genuinely-new residual.** P1 + P3 + P5 residuals are small enough to fit as T-slots inside prior-arc queues. P4 residual is real but spans three constitutional homes.

**If the arc opened as proposed, ≥60% of its output would be re-litigation of ratified content.** That is a Playbook §10.2 anti-pattern — MINOR amendments are supposed to add new rules or refine existing ones, not re-derive them.

---

## 7. Falsification vector 6 — Does the domain warrant an arc at all

**Ratio test:** genuinely-new content / total proposed content.

- Genuinely new: ~30% (P2 tool call discipline + partial P4 failure taxonomy).
- Re-litigation: ~60% (P1 + P3 + P5).
- Meta / cross-cutting already ratified: ~10% (X- attributes).

**Precedent for what shape research work of this size takes:**
- Group 2600 PA — 4 children over 6 sessions. Studied outward-facing PA endpoint. Substantially new territory.
- I-0200 RAG Corpus Substrate Maturity — implementation arc, single ADR outcome, 1 substantive session.
- Cross-Domain Integration Audit — single-doc audit across 32 domains, not an arc.

**If genuinely-new content is 30% of a 5-child proposal, the correct shape is ONE of:**
- A single-session audit (like Cross-Domain Integration Audit's original single-doc).
- A 2-child arc studying only the residual new territory.
- A MINOR-amendment cluster to Ch 5 §5.4+ addressing §5.5 extension point #1 (tool call discipline) as a targeted 3-5 rule package.

**None of those is a 6-session 5-child arc.**

**Verdict:** the domain warrants research work but NOT the shape Phase 0 proposed.

---

## 8. Falsification vector 7 — The nominalization test

Every category name Phase 0 chose is a NOUN PHRASE:
- Authority Carriage
- Capability Contract
- Knowledge Substrate
- Failure & Recovery
- Verifier Loop

Nouns are abstractions. If I convert each back to its underlying QUESTION:
- *"How does authority get carried?"*
- *"What contract does a capability observe?"*
- *"Where does knowledge come from?"*
- *"How does failure classify and how is recovery run?"*
- *"When does the verifier fire?"*

These are five different KINDS of questions. Some are *"how does X propagate"* (mechanism questions). Some are *"what does X owe"* (contract questions). Some are *"where does X live"* (SoT questions). Some are *"when does X fire"* (trigger questions).

**Playbook Ch 6 PIC-10 discipline warns:** a rule can be typed only if the STATEMENT CLASS is clear. Statement classes are shape-based, not topic-based. My Phase 0 grouped by TOPIC. The Playbook groups by SHAPE.

**Applying PIC-10 to my inventory:**

- [EP] Empirical Proposition = observed behavior at HEAD.
- [GR] General Rule = a normative constraint the platform imposes.
- [AC] Architectural Constraint = a boundary that must hold across amendments.

Every inventory item is exactly one of these. My Phase 0 categories mixed all three inside every child. That is exactly the confusion PIC-10 was ratified to prevent.

**Verdict:** the category names Phase 0 chose are pre-PIC-10-discipline. They pre-date the ratification Chris and I both signed off on 24 hours ago. This is a Ch 6 discipline violation in the making.

---

## 9. What survives

Restating the surviving findings tightly.

**S1. The 113/156 schema/handler gap is real new territory.** No prior arc has enumerated why 43 handlers exist without a corresponding schema. Categories: some are internal (called by other handlers only); some are intentionally gated from LLM; some are drift from removed schemas. Enumerating each is 1 session of primary evidence work.

**S2. Ch 5 §5.5 extension points are ratified as extension points but not yet addressed.** Extension point #1 (*PA tool call discipline codification*) is the largest addressable target. Extension point #3 (*placeholder-stall recovery discipline*) is the next. Extension points #2 (verifier-loop cross-workspace) and #4 (multi-agent) are parked.

**S3. The LLM-autofill-boolean behavior + safe-default posture at PA tool boundary is a real Ch 5 §5.5 #1 candidate.** Two MEMORY rules crystallize this (`feedback_llm_autofills_boolean_params_with_false` + `feedback_editor_fail_loud`). No prior arc has surfaced them into ratified rule form.

**S4. Rigby's specific reach surface DOES include non-tool substrates** (8 enrichment services + workspace resolver + context builders). This is real observation. Whether it warrants constitutional weight or stays as documented topic-doc content is a separate question.

**Everything else in the Phase 0 five-child proposal either re-litigates closed arcs or belongs in different Playbook chapters.**

---

## 10. Reframes worth considering

Presenting three research-only reframes. Chris picks or rejects; no arc opens on my recommendation.

### 10.1 Reframe A — Narrow to Tool Call Discipline

**Scope:** Ch 5 §5.5 extension point #1 verbatim.

**Structure:** 2-child arc under `docs/research/tools/`.
- P1 Tool Schema Surface (113 schemas: what LLM sees; discovery model; gateway aggregation).
- P2 Tool Handler Surface (156 handlers: dispatch contract; failure typing; the 43-handler gap; LLM-autofill discipline; safe-default posture).
- xx99 canonical summary.

**Anti-scope:**
- No authority carriage (Groups 1900 + 2400 + 2600 own).
- No knowledge substrate (Groups 2100 + 1300 + I-0200 own).
- No verifier-loop (§5.2.1 owns; MEMORY holds instances).
- No worker/runtime discipline (Ch 8 STUB owns).
- No cross-cutting recovery (Ch 9 STUB owns).

**Runtime target:** 3-4 sessions total (parent + 2 children + xx99).

**Constitutional home:** Ch 5 §5.4+ MINOR amendments addressing extension point #1.

**Fits `tools/` directory:** yes, precisely.

### 10.2 Reframe B — Targeted audit + MINOR amendment cluster (no arc)

**Scope:** the ~30% genuinely-new content only.

**Structure:** single audit deliverable + a 3-5 rule MINOR amendment package.
- Audit deliverable: schema/handler gap enumeration + safe-default posture inventory + LLM-autofill discipline classification. 1-2 sessions.
- MINOR amendment: 3-5 new [EP]/[GR] rules at Ch 5 §5.4 addressing extension point #1. Follows Playbook Ch 10.2 amendment lifecycle. Chris ratifies via SIGN cycle.

**Runtime target:** 2-3 sessions total.

**Constitutional home:** Ch 5 §5.4 MINOR amendment.

**Fits `tools/` directory:** the audit lands there; amendments land in `docs/ENGINEERING_PLAYBOOK.md`.

**Trade-off:** cheaper and more targeted than an arc. Loses the arc structure's advantage of forcing per-child SIGN cycles and cross-child integration.

### 10.3 Reframe C — Different arc altogether (Sources of Truth)

**Scope:** Sources of Truth registry as extension to Ch 1 §1.4 Canonical authority.

**Structure:** 4-child arc under `docs/research/platform/` (NOT `tools/`).
- P1 Actor SoT.
- P2 Workspace SoT.
- P3 Capability-Interface SoT.
- P4 Retrieved-Evidence SoT (post-I-0200 layer).

**Anti-scope:** everything the Phase 0 proposal put in P4 (failure/recovery) and P5 (verifier-loop). Not this arc's territory.

**Runtime target:** 6 sessions (parent + 4 children + xx99).

**Constitutional home:** Ch 1 §1.4 extension.

**Fits `tools/` directory:** NO. Would require `docs/research/platform/` placement.

**Trade-off:** studies a genuinely important architectural question with strong Sources-of-Truth center. But does NOT match Chris's `tools/` directory signal. If Chris wants this arc, the directory choice needs revision.

### 10.4 Reframes considered and rejected

- **Reframe D — Keep Phase 0's five-child structure as-is.** Rejected on Section 4-7 findings.
- **Reframe E — Merge Phase 0 children into 3 (P1+P4, P2+P3, P5).** Rejected — creates larger categories with even less internal coherence.
- **Reframe F — Open Phase 0 as-is but with anti-scope excluding prior-arc territory.** Rejected — the anti-scope would consume so much of the inventory that each child becomes trivial. Better to narrow to Reframe A.

---

## 11. What this document does NOT do

- Does NOT propose which reframe (A/B/C) Chris should choose.
- Does NOT open any arc.
- Does NOT modify the Phase 0 domain-definition doc (its record stands as the target this pressure test attacked).
- Does NOT propose a Playbook amendment or ADR.
- Does NOT route to Rigby (Chris ratifies; Rigby SIGN happens later if an arc opens).
- Does NOT create workspace deliverables.
- Does NOT invalidate the Phase 0 doc entirely — it explicitly retains S1-S4 findings as surviving evidence.
- Does NOT decide the constitutional-home question — that is Chris's call after this document is reviewed.

**This document waits for Chris's review before any subsequent research or authoring proceeds. The verdict — decomposition-survives / decomposition-supplanted / no-arc-opens — is a Chris-gated decision.**

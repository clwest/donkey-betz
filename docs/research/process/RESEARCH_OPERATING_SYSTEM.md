---
title: "Research Operating System — the OS every Claude Code session executes in Donkey Betz"
status: draft
authority: process
version: v2.1
session_added: 1277
last_verified: 2026-07-01
domain_slug: process
research_group: 1277
child_slot: standalone
companion_anchors:
  - CLAUDE.md
  - 00-START-NEXT-SESSION.md
  - MEMORY.md   # Claude Code auto-memory
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/claude_research_startup_introspection.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md   # specialization of §8 Research contract
  - docs/research/process/claude_research_startup_introspection.md  # evidence base
verifier_loop: |
  v2.1 (2026-07-02, S1278 finalization): Ratification pass. Playbook
  §-ref cascade artifact cleanup: 13 in-text bugs corrected (playbook
  §5 phase discipline → §3; playbook §4 STAGE 0 → §2; playbook §17.4
  → §11.4; playbook §19 sub-agents → §13; playbook §12 canonical Qs
  → §9; playbook §8 metadata → §6; playbook §9 cross-ref → §7;
  playbook §17.1 template → §11.1; playbook §9 templates → §11).
  §20 finalization section added (12 subsections): fresh-Claude
  confusion audit, missing-layer verdict, documentation ecosystem
  diagram, knowledge lifecycle mapping, research lifecycle
  completeness, quick-start verdict, graduation verdict, P0/P1/P2
  debt sort, ratification recommendation READY-WITH-MINOR-FOLLOW-UP,
  migration checklist, Context-Kit boundary re-evaluation, session
  close. No new architecture; no new mandatory contracts; no
  structural change to §1-§19. §20 is additive assessment.
  Ratification pass Rigby SIGN pending on final architectural
  recommendation only (per S1278 mission spec: "Route ONLY the
  final architectural recommendation to Rigby. Do not ask Rigby
  to redesign the OS.").
  v2 (2026-07-01, S1277 re-issue): Chris re-issued S1277 with expanded
  scope naming 16 parts + 14 deliverables (up from 10 + 6). Six new
  parts added: Part 1 Research Philosophy (defines purpose + stop
  condition + anti-pattern); Part 2 Context-Kit Integration (ownership
  boundary + drift prevention + do-not-duplicate list); Part 11
  Documentation Ownership (matrix per doc class + update triggers);
  Part 13 Research Contract (8 required fields; mandatory session-
  open framing); Part 14 Completion Contract (10-item close checklist
  + Rigby/commit/index/handoff discipline); Part 15 Research Debt
  (new concept + measurement + lifecycle + escalation). Existing
  Parts 1-10 (v1.1) renumbered to Parts 3-12 and 16-19 to match
  spec ordering. In-text §-references cascade-renumbered via
  replace_all. Cross-reference audit at v2 close: Rigby grep-verified
  playbook §-refs in the six new parts (§2/§9/§15/§16/§20/§21 all
  match playbook v2 §-numbers). DOC_LIFECYCLE §2c refs corrected.
  Second Rigby SIGN routed on fresh isolation pin pa-117d3edf9d7b80f8;
  SIGN-with-edits verdict returned with 12 must-fix folds (§1.2
  enforcement rule; §1.5 anti-patterns; §2.3 ownership rows; §2.7.1
  operational cadence; §2.9 do-not-duplicate additions; §11.1 owner
  tightening; §11.4 anti-patterns; §13.1 field format; §14.7 handoff
  risks; §15.1.1 debt categories; §15.3 priority formula replaced;
  §15.6 debt-vs-follow-on clarification). All 12 folded in place.
  See §19.7 for full fold record. Status remains draft until Chris
  ratifies. This session's Research Contract retained: Why =
  reduce uncertainty until Chris can ratify the Research OS;
  Deliverable = this doc; Expected Decision = "Ratify OS v2 as
  canonical"; Ratifier = Chris; By = end-of-session;
  Stop Condition = 16 parts + 14 deliverables satisfied + Rigby
  SIGN resolved. Stop reached at v2 with edits folded.
  v1.1 (2026-07-01, S1277): Rigby SIGN-with-edits folded from fresh
  isolation pin pa-95ce3cbf0a2aa0cc (Medium confidence). 15 must-fix
  edits folded in place: (1) TL;DR bootstrap Level A/B split; (2)
  minimal-context capture (branch/SHA + change-vs-explain + repro
  path); (3) prescriptive vs observational labeling convention; (4)
  §4.1 Level A success-criterion column per step; (5) §4.2 Level B
  class-scoped bootstrap; (6) §5.1 class 11 OPS/DEPLOY/INCIDENT; (7)
  §5.1 class-boundary rules (Design-Prep vs ADR, Review vs Meta,
  Bug vs Ops); (8) §6.6 state surface reconciliation ritual; (9)
  §7.1 Tier 1 split into 1a generated / 1b measured ops snapshots;
  (10) §7.1 Tier 5 vs Tier 6 disambiguator rule (`verifier_loop` +
  file:line); (11) §7.1 Tier 9 vs Tier 10 "never used for synthesis"
  boundary; (12) §8.9 NAVIGATION QUERY explicit output format; (13)
  §8.10 META-PROCESS inverse-grep + drift-scan; (14) Investigation
  Log template promoted to P1 + registered in §9.1; (15) §8.11 new
  OPS/DEPLOY/INCIDENT contract + Ops Incident Report template
  registered. Two Rigby asks partially folded with deferred rationale
  (DESIGN-PREP + ADR merge; router determinism vs ASK CHRIS
  fallback) — see §19.5. Status remains draft until Chris ratifies.
  v1 (2026-07-01, S1277): drafted after the S1276 playbook v2 commit
  and S1276 startup introspection landed. Evidence base: (a) direct
  observation of my own S1276 + S1277 startup behavior; (b) grep
  audits of CLAUDE.md, 00-START-NEXT-SESSION, START-HERE README
  showing what fresh Claude cannot discover today; (c) playbook v2
  §21 opening sequence + §15 SIGN table + §17 graduation criteria
  as the research-class specialization; (d) DOC_LIFECYCLE.md §2c
  inventory-wins-on-conflict rule as the authority backbone; (e)
  S1300 Memory scoping as the first parent-with-children exemplar;
  (f) failure modes catalogued in the S1276 introspection §6.
  Rigby SIGN routing: MANDATORY per S1277 mission spec. Fresh
  isolation pin generated at session open (pa-95ce3cbf0a2aa0cc);
  arc pin pa-aa54193f240f4846 reserved for Memory research and not
  cross-contaminated with this meta-mission. Pressure-test payload
  in §19.
owner: claude (drafted S1277 v1; Rigby SIGN-with-edits folded S1277 v1.1)
---

# Research Operating System (Research OS)

> **What this is.** The operating system every Claude Code session
> executes when working in `unified-donkey-betz`. It defines how a
> fresh Claude — one that knows nothing except what exists in the
> repository — becomes productive across every class of work:
> research, design, implementation, bugs, feature specs,
> navigation queries, and meta-process.
>
> **What this is not.** A platform architecture doc. An
> implementation plan. A cleanup pass. Zero runtime changes.
> Research and documentation only.
>
> **Positioning.** The Research OS is the *superset*. The
> `DOMAIN_RESEARCH_PLAYBOOK.md` (v2, S1276) is the specialization
> for research-class requests. `ARCHITECTURE_INDEX.md` is the
> library map. `PLATFORM_INVENTORY.md` is the runtime anchor.
> This doc names the contract that binds all of them together.
>
> **The success condition** (from S1277 mission): a brand-new
> Claude Code reads this document, executes bootstrap, classifies
> the user request, runs the matching startup contract, and begins
> contributing — **without Chris having to write a 4,000-word
> prompt.**

---

## 60-second TL;DR for a fresh Claude

If you have just been dropped into this repository, do this in
this order:

1. **Bootstrap Level A (always).** Run `context-kit orient`.
   Read `CLAUDE.md`. Read `00-START-NEXT-SESSION.md`. Read this
   document §0–§5 (skim § 4 → §9 headings). Record repo state
   (branch + last commit SHA + `git status` — any uncommitted
   changes?). This is ~5 minutes and identical across all
   request classes.
2. **Capture request context.** Note: (a) is the user asking me
   to **change** something or **explain** something? (b) for
   bugs: repro path + observed vs expected. (c) explicit
   constraints (no commits / no PR / no runtime / etc.). Write
   these down before doing anything else.
3. **Classify the request.** Route via §5 Research Router. What
   *class* of work is the user asking for?
4. **Bootstrap Level B (class-scoped).** Load the docs the
   matching §8 contract requires. Not every session needs the
   full playbook or full research library. Level B is bounded
   by the contract.
5. **Verify pin + service_context.** If the work touches
   `pa_chat.py` / Rigby: confirm `service_context: local` via
   `platform_config_tool overview`. Verify pin ownership per
   MEMORY.md rule `feedback_pa_local_verify_ownership`.
6. **Execute the contract.** Reads → checks → work → verification →
   Rigby routing (if class calls for it) → completion.
7. **Do not commit** unless Chris says so. Draft-first is the
   default (playbook §16, this doc §8).
8. **Close cleanly.** Update `00-START-NEXT-SESSION.md` with
   next priorities. Update `OPEN_ARCS.md` if arc state changed.
   Write a handoff to `docs/handoffs/`.

If any step is unclear, the failure is in this document, not in
you. Read §10 (Navigation) for what fresh Claude currently
*cannot* find, and route the ambiguity to Chris — do NOT guess.

**Convention.** Prescriptive statements (rules the OS defines)
are written in normative language ("MUST", "shall", "requires").
Observational statements (things I saw at S1276/S1277 open) are
written in past tense with explicit citation. When you see a
rule stated without a citation, treat it as an OS design
choice — not an observed invariant — and challenge it if it
does not fit your context.

---

## Table of contents

- **Positioning and scope** (intro)
- **Part 1** — Research philosophy
- **Part 2** — Context-kit integration
- **Part 3** — How fresh Claude thinks (decision tree)
- **Part 4** — Bootstrap startup sequence
- **Part 5** — Research Router (11 request classes)
- **Part 6** — Repo state surfaces
- **Part 7** — Documentation authority hierarchy
- **Part 8** — Startup contracts (per class)
- **Part 9** — Thinking templates registry
- **Part 10** — Navigation and discoverability
- **Part 11** — Documentation ownership
- **Part 12** — Repeatability — reducing Chris's prompt burden
- **Part 13** — Research Contract (mandatory session-open framing)
- **Part 14** — Completion Contract (mandatory session-close discipline)
- **Part 15** — Research Debt
- **Part 16** — Long-term vision
- **Part 17** — Required new documents
- **Part 18** — Migration plan (P0/P1/P2)
- **Part 19** — Rigby SIGN record
- **Appendix** — Evidence provenance + verifier notes

---

# Positioning and Scope

## 0.1 What "Research OS" means

Chris named this doc "AI Research Operating System" because
research is the arc that motivated its creation — the S1268–S1276
research library grew large enough that the *how to do research
in this repo* pattern had to be formalized (`DOMAIN_RESEARCH_PLAYBOOK.md`
v2, S1276). But the OS Chris asked for is broader than research.
It governs how Claude Code approaches **every** class of work in
the repo.

Keep the name; understand the scope.

## 0.2 Relationship to other governance docs

| Doc | Role | Relationship to OS |
|-----|------|-------------------|
| `CLAUDE.md` | Session instructions, injected every session | The OS extends CLAUDE.md — until the P0 CLAUDE.md pointer lands (§18), CLAUDE.md alone cannot make fresh Claude find this doc. |
| `MEMORY.md` (auto-memory) | Persistent user + workflow preferences | Feedback rules refine OS behavior over time; OS defines the surfaces those rules mutate. |
| `00-START-NEXT-SESSION.md` | Per-session priorities | Session-scoped state. OS provides the *durable* framework session state assumes. |
| `docs/00-START-HERE/DOC_LIFECYCLE.md` | Rules for `/docs/` corpus governance | Foundational — OS honors DOC_LIFECYCLE §2c (inventory wins on conflict). |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` | Rules for primitive re-use / anti-duplication | Foundational — OS honors §4 anti-duplication for docs (never build a new doc when a wrapper suffices). |
| `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` v2 | Research-class specialization | Called by the OS §8 Research contract. Playbook governs research; OS calls the playbook. |
| `docs/research/ARCHITECTURE_INDEX.md` | Research library navigation | Referenced by §5 router for research-class requests. |
| `PLATFORM_INVENTORY.md` | Runtime anchor | Truth-authority Tier 1 in §7 hierarchy. |
| `PLATFORM_WHAT_IT_IS.md` | Narrative anchor | Truth-authority Tier 3 in §7. |

## 0.3 Non-goals

- **Not a re-inventory of the platform.** The 32-domain map
  already lives at `docs/research/platform_architecture_inventory.md`.
  This doc references it; does not duplicate.
- **Not a rewrite of the playbook.** The playbook v2 governs
  research-class contracts. The OS integrates them.
- **Not runtime code.** No CLI, no wrapper, no `manage.py`
  additions. When runtime automation is possible, this doc names
  the automation opportunity but does not implement.
- **Not a Chris manual.** This doc is for Claude Code. Chris
  reads it to review; he does not have to consult it during
  normal collaboration.

---

# Part 1 — Research Philosophy

Before we design a research operating system, we have to agree
on what research *is*. The philosophy in this part is the
foundation everything downstream stands on.

## 1.1 What is the purpose of research?

**Research reduces uncertainty until a decision can be made.**

That is the entire purpose. Not documentation. Not exploration
for exploration's sake. Not proving intellectual rigor. Research
exists because uncertainty is expensive — it stalls
implementation, invites premature commitment, and produces
rework when the wrong path gets chosen.

Every research artifact this OS produces must be traceable back
to a decision it enables. If a doc cannot answer *"which
decision does this unblock?"*, it should not have been written.

## 1.2 When is research finished?

**Research is finished when additional evidence would not
change the decision.**

This is the stop condition. Not "when everything is
understood." Not "when the doc is beautiful." Not "when Rigby
finds no more gaps." Research ends when the marginal cost of
gathering more evidence exceeds the marginal reduction in
decision risk.

Three concrete stop signals:

1. **The decision is now safely reversible.** A wrong choice
   is cheap enough to undo. Continue only if reversibility
   costs would sink the project.
2. **All 28 canonical questions** (playbook §9) are answered
   with cite, reference, or explicit `UNKNOWN`. UNKNOWNs
   remaining is legitimate; guessing to fill them is not.
3. **Chris has enough to ratify.** The named decision
   (§13 Research Contract) can be made. Rigby SIGN
   status is resolved.

Any research session that continues past all three signals is
producing waste, not evidence.

**Enforcement rule (Rigby SIGN v2 fold, S1277).** Once the
stop condition is met, further evidence-gathering requires
either (a) modifying the Research Contract (§13) with Chris
ratification, or (b) opening a new research group. Continuing
under the same contract past the stop signal is a §13.5
contract violation. This makes the stop condition operational,
not aspirational.

## 1.3 What problem is research trying to solve?

Research prevents three failure modes:

1. **Premature commitment.** Implementing before the shape is
   understood. The rework cost dominates the research cost by
   an order of magnitude, at minimum. S1270 Symbol Mapping's
   design-space enumeration prevented committing to Option A
   before Option E's reversibility became visible.
2. **Cognitive load hoarding.** Every unresolved unknown lives
   rent-free in Chris's head until it is either researched or
   punted. Research externalizes the load into artifacts that
   future sessions can consume without re-derivation.
3. **Repetitive re-discovery.** Without a canonical research
   library, every fresh Claude re-inventories the same
   subsystem. The 32-domain map (S1273) was the moment this
   cost became visible and legible.

## 1.4 What research produces

Research is not the end. Research produces:

```
     Evidence (raw)
          │
          ▼
     Findings (research doc)
          │
          ▼
     Recommendation (design-preparation doc)
          │
          ▼
     Decision (ADR — Chris ratifies)
          │
          ▼
     Implementation (runtime PR)
          │
          ▼
     Verification (test + telemetry + Rigby check)
          │
          ▼
     Learning (fold back into research library as
              superseded doc + updated findings)
```

Each arrow can fail. Research produces evidence, but if that
evidence never converts to a decision, research has failed
regardless of how thorough the doc is. This is why the OS
mandates a "Decision this unblocks" field in every research
contract (§13).

## 1.5 The anti-pattern: research-for-its-own-sake

The single most dangerous anti-pattern this OS must prevent:

> Research produced beautifully. No decision followed. The
> author moved to the next research question because it was
> more interesting than gating the current one on Chris.

Symptoms:
- Doc landed as `status: active` but no design-preparation or
  implementation follow-on ever queued.
- Rigby SIGN clean; verifier_loop pristine; six months later,
  no one has looked at it.
- Follow-on research queue in the canonical summary lists 15
  items but no priority order.
- Same domain gets re-researched two years later because
  nobody remembers what the first pass concluded.

Related anti-patterns (Rigby SIGN v2 fold, S1277):

- **Cite theater.** Doc contains dozens of file:line citations
  and looks rigorous, but never synthesizes them into a
  finding. Evidence density is not a substitute for a
  conclusion.
- **UNKNOWN laundering.** UNKNOWNs that are researchable
  within budget get marked UNKNOWN to avoid doing the work.
  Legitimate UNKNOWNs are evidence; researchable ones marked
  UNKNOWN are debt (§15).
- **Decision-free recommendations.** Design-preparation docs
  that end with *"it depends"* without bounding the decision
  tree. If Chris cannot pick, the recommendation failed. Force
  the decision by narrowing options.
- **Curiosity hijack.** Session drifts into an interesting
  sub-question that is technically in scope but sinks the
  budget. Enforce the Research Contract's out-of-scope
  section.

The OS treats research-for-its-own-sake as **research debt**
(§15). Every research artifact has a stop condition, a decision
it unblocks, and a follow-on either enqueued or explicitly
deferred.

## 1.6 The research philosophy in one paragraph

Research on Donkey Betz exists to reduce uncertainty until a
Chris-ratifiable decision can be made. It stops when additional
evidence would not change that decision. Every research artifact
declares which decision it unblocks, when it is finished, and
what happens next. The library is not an end in itself; it is
scaffolding for implementation. When implementation lands, the
research retires into the corpus as evidence for the decision
that was made, not as active state.

## 1.7 What this philosophy implies for the OS

Given this philosophy, the OS enforces four rules on every
research session:

1. **§13 Research Contract** at session open. State the
   decision, the stop condition, the deliverable, the future
   research.
2. **§14 Completion Contract** at session close. Verify the
   stop condition was reached; log any remaining research
   debt.
3. **§15 Research Debt** tracked as a first-class concept.
   Debt accrues; debt is paid down or explicitly retired.
4. **Design-preparation and Implementation contracts** (§8.2
   and §8.4) are downstream of research. Research does not
   substitute for design; design does not substitute for
   implementation. Each phase has its own artifact.

Everything the rest of this OS specifies is grounded in this
philosophy. Anything that violates it — a research doc without
a decision, an infinite audit, a canonical summary that opens
new questions instead of closing old ones — should be pushed
back on.

---

# Part 2 — Context-Kit Integration

This OS lives inside a repo that uses a broader documentation
framework called **context-kit**. Understanding what is
context-kit's job vs what is Donkey Betz's job is critical for
preventing drift between the two.

## 2.1 What Context-Kit is

Context-kit is a documentation framework — a *pattern*, not a
project. It provides:

- **A skill** (`.claude/skills/context-kit/SKILL.md`) that
  every Claude Code session invokes at open. The skill runs
  `context-kit orient`, teaches the "runtime wins" rule, and
  reminds the agent to write a handoff at session close.
- **A framework master** (in this repo at `docs/docs-pattern/`)
  that documents the load-bearing pieces of the pattern: the
  two-doc anchor, the drift verifier, embeddable topic docs,
  session handoffs, the start-here doc. Chris's plan (per
  DOC_LIFECYCLE.md §0) is that this subtree eventually ships
  as its own repo.
- **A set of commands** — `orient`, `seed`, `doctor`,
  `hotpath`, `recommend-stack`, `refactor track`,
  `translation-init`, `adopt` — that operate on any
  context-kit-shaped repo.

Context-kit is **generic**. It works on any repo where the
pattern applies. It knows nothing about agents, spiders,
Celery workers, Rigby, or research groups. That is by design.

## 2.2 What Donkey Betz is (from the Context-Kit lens)

Donkey Betz is a **specific instance** of the context-kit
pattern. Instance-specific artifacts:

- `docs/PLATFORM_INVENTORY.md` — instance's runtime anchor
  (framework calls it `*_INVENTORY.md`).
- `docs/PLATFORM_WHAT_IT_IS.md` — instance's narrative anchor
  (framework calls it `*_WHAT_IT_IS.md`).
- `docs/topics/*.md` — instance's subsystem docs.
- `docs/handoffs/SESSION_*.md` — instance's handoffs.
- `00-START-NEXT-SESSION.md` — instance's start-here doc.
- `CLAUDE.md` — instance's session instructions.
- Everything else under `docs/` — instance content.
- `docs/research/` (the research library, the playbook, this
  OS) — instance's specialization for architectural research.

Context-kit provides the *shape*; Donkey Betz fills the shape
with content.

## 2.3 The ownership boundary — recommended model

| Concept | Owner | Location |
|---------|-------|----------|
| `orient` command semantics | Context-Kit | `.claude/skills/context-kit/SKILL.md` |
| Two-doc anchor pattern | Context-Kit | `docs/docs-pattern/01_two_doc_anchor.md` |
| Drift verifier concept | Context-Kit | `docs/docs-pattern/02_drift_verifier.md` |
| Topic docs pattern | Context-Kit | `docs/docs-pattern/03_topic_docs.md` |
| Session handoff pattern | Context-Kit | `docs/docs-pattern/04_session_handoffs.md` |
| Start-here doc pattern | Context-Kit | `docs/docs-pattern/05_start_here.md` |
| "Runtime wins" rule | Context-Kit | Skill + docs-pattern |
| Bootstrap checklist (framework-level) | Context-Kit | `docs/docs-pattern/07_bootstrap_checklist.md` |
| Rigby-first comms | Donkey Betz | CLAUDE.md |
| Playbook (research-class specialization) | Donkey Betz | `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` |
| Research OS (this doc) | Donkey Betz | `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` |
| ARCHITECTURE_INDEX | Donkey Betz | `docs/research/ARCHITECTURE_INDEX.md` |
| Rigby SIGN process | Donkey Betz | Playbook §15 + OS §8 contracts |
| Employee OS primitives | Donkey Betz | `docs/EMPLOYEE_OS_PRIMITIVES.md` |
| Doc lifecycle rules (V1/V2 banners, root-stability, never-delete) | Donkey Betz | `docs/00-START-HERE/DOC_LIFECYCLE.md` |
| Specific inventory content (agent counts, model counts) | Donkey Betz | `PLATFORM_INVENTORY.md` |
| Specific narrative content | Donkey Betz | `PLATFORM_WHAT_IT_IS.md` |
| Specific topic docs | Donkey Betz | `docs/topics/*.md` |
| Specific handoffs | Donkey Betz | `docs/handoffs/*.md` |

**Rule of thumb.** If it would work identically on any other
context-kit repo (fleet, mentorforge, spokesperson), it belongs
to Context-Kit. If it is specific to Donkey Betz's subsystems,
domains, personas, or operational choices, it belongs here.

## 2.4 What belongs in CLAUDE.md vs Context-Kit

| Content | Belongs in | Rationale |
|---------|-----------|-----------|
| "Run `context-kit orient` at open" | Context-Kit skill | Universal to all context-kit repos |
| Two-doc anchor discipline | Context-Kit docs-pattern | Same |
| Handoff-at-close requirement | Context-Kit skill | Same |
| "Rigby-first comms" | CLAUDE.md | Donkey Betz specific (Rigby is our PA) |
| PA pin management | CLAUDE.md | Donkey Betz specific |
| Live counts autoblock | CLAUDE.md | Regenerated from Donkey Betz runtime |
| Subsystem doc pointers table | CLAUDE.md | Points to Donkey Betz topic docs |
| Research library entry point | CLAUDE.md (proposed in §18 P0) | Donkey Betz has a research library; other context-kit instances may not |
| Employee OS primitives pointer | CLAUDE.md | Donkey Betz specific |

**Anti-pattern.** Duplicating a Context-Kit rule into CLAUDE.md
means both must be kept in sync. When Context-Kit's rule
updates, CLAUDE.md drifts. **Don't duplicate — reference.** If
Context-Kit's rule needs Donkey Betz commentary, add the
commentary as an inline note next to the reference:

> Rigby-first comms rule (Donkey Betz specialization): Context-Kit's
> "push back when the framing looks wrong" rule applies with
> extra force for Rigby-mediated conversations because Rigby's
> health-score depends on tool exercise. See MEMORY rule
> `feedback_rigby_scope.md` for the split.

## 2.5 What belongs in START-HERE vs Context-Kit

`docs/00-START-HERE/` today contains:

- `README.md` — orientation-chain pointers
- `INDEX.md` — same, shorter
- `DOC_LIFECYCLE.md` — V1/V2 banner rules + root-stability +
  never-delete rule

The `README.md` and `INDEX.md` are Donkey Betz specializations
of the Context-Kit "start-here" pattern. Their content
overlaps ~80% with what Context-Kit's `05_start_here.md`
template recommends. This is legitimate — Donkey Betz has more
docs than a fresh context-kit project, so the entry points are
richer.

`DOC_LIFECYCLE.md` is genuinely Donkey Betz-owned:
- The DOC-POINTER-V1 / V2 banner conventions were designed for
  this repo's 600+ file corpus.
- The never-delete rule is Chris's decision, not
  Context-Kit's.
- The root-stability rule is a Donkey Betz operational choice.

Context-Kit *could* absorb generic versions of these rules
into `docs-pattern/`, but Chris's Session 1143 decision was to
keep them Donkey Betz-specific. Respect that until Chris says
otherwise.

## 2.6 What belongs in the Research Library vs Context-Kit

The Research Library (`docs/research/`) is entirely Donkey
Betz-owned. Context-Kit does not have a research-library
pattern today. Research is a Donkey Betz specialization.

Speculative future move: if Context-Kit adds a "canonical
research library" pattern, Donkey Betz's playbook and OS could
be promoted as reference exemplars — the way `docs-pattern/`
already promotes the two-doc anchor and drift verifier.

For now:
- **Research OS** (this doc) is Donkey Betz-owned.
- **DOMAIN_RESEARCH_PLAYBOOK** is Donkey Betz-owned.
- **ARCHITECTURE_INDEX** is Donkey Betz-owned.
- **Research artifacts** (domain audits, canonical summaries,
  design-prep docs) are Donkey Betz-owned.

If any of these evolve into patterns worth generalizing (e.g.,
the parent-with-children arc shape is transferable), the
promotion path is: (a) doc is stable for 3+ research groups
here, (b) Chris ratifies extraction, (c) generalize into
`docs/docs-pattern/`, (d) Context-Kit ships the pattern.

## 2.7 Drift prevention model

Context-Kit and Donkey Betz can drift apart if there is no
active reconciliation. Rules:

1. **When Context-Kit adds a feature** (new command, new
   pattern), the Donkey Betz orient output shows it. The OS
   §4 (bootstrap) treats the orient output as authoritative
   — if orient surfaces a new command, we adopt it.
2. **When Donkey Betz creates a pattern that generalizes**
   (like §13 Research Contract, or the parent-with-children
   arc), it stays Donkey Betz-owned until 3+ research groups
   use it. Then it becomes eligible for extraction to
   `docs-pattern/` per playbook §20 evolution triggers.
3. **When Context-Kit's rule changes** in a way that affects
   Donkey Betz behavior (e.g., orient starts printing a new
   section), CLAUDE.md's Research Library subsection may need
   a companion note. Handle as §10 META-PROCESS.
4. **When Donkey Betz's rule contradicts Context-Kit's**, one
   of them is drift. Resolution: whichever has the more
   recent commit + explicit rationale wins. Update the other
   or add an explicit note explaining the intentional
   divergence.

### 2.7.1 Operational cadence (Rigby SIGN v2 fold, S1277)

Rules alone are policy, not operations. The drift prevention
model runs on this cadence:

- **Every session close.** The context-kit orient output is
  the source of truth for framework state. If the current
  session's orient output diverges from what the prior
  session recorded (i.e., context-kit updated), note the
  divergence in the closing handoff.
- **Monthly.** A §10 META-PROCESS session sweeps: (a) does
  CLAUDE.md still cite Context-Kit correctly? (b) do the
  Context-Kit patterns cited in `docs/docs-pattern/` still
  match the framework master? (c) are any Donkey Betz-owned
  patterns (playbook, OS, INDEX) candidates for promotion to
  Context-Kit? Log outcome in `docs/research/process/`.
- **On any Context-Kit change**, the next Donkey Betz session
  opens with a mandatory drift-check as the first work item
  after bootstrap.

**Ownership of reconciliation.** Meta-process sessions own
reconciliation PRs. Default cadence maintainer: whichever
Claude session runs the META-PROCESS contract next. Chris
gates the reconciliation commit.

**Verification artifact.** Each drift-check produces a
one-paragraph note in the closing handoff or in a dedicated
META-PROCESS handoff. If the note says "no divergence found,"
that is the evidence.

## 2.8 Recommended Context-Kit changes (from Donkey Betz OS lens)

Not commits Chris needs to make in Context-Kit today — but
things Context-Kit *could* absorb as Donkey Betz proves them:

- **Research Contract template** (this OS §13) as a first-class
  Context-Kit pattern for research-heavy repos.
- **Completion Contract template** (this OS §14) as a
  companion to the handoff pattern.
- **Research Debt** as a first-class concept (this OS §15).
- **Parent-with-children arc** as an optional shape when a
  research group covers multiple subsystems (playbook §2).
- **Fresh-isolation-pin default** (playbook §15) as a
  Context-Kit rule for multi-agent scenarios.

None of these are urgent. They will surface as promotion
candidates over time, per the drift prevention model.

## 2.9 What must NEVER be duplicated

Concrete list of do-not-duplicate:

- **The "runtime wins" rule.** Lives in Context-Kit skill.
  DOC_LIFECYCLE.md §2c references it — never restates it.
- **The `orient` command semantics.** Lives in Context-Kit
  skill. CLAUDE.md must not restate the steps orient takes.
- **The two-doc anchor pattern.** Lives in
  `docs-pattern/01_two_doc_anchor.md`. Donkey Betz's
  PLATFORM_INVENTORY + PLATFORM_WHAT_IT_IS are instances,
  not restatements.
- **The handoff-at-close rule.** Lives in Context-Kit skill.
  Playbook + this OS reference it; do not restate.
- **The bootstrap checklist template.** Lives in
  `docs-pattern/07_bootstrap_checklist.md`. Donkey Betz's
  session-open FIRST-THING checklist in
  `00-START-NEXT-SESSION.md` is an instance.
- **DOC_LIFECYCLE rules** (V1/V2 banner conventions, root-
  stability, never-delete). Live in
  `docs/00-START-HERE/DOC_LIFECYCLE.md`. Every doc that
  interacts with lifecycle rules cites the rule; never
  restates it. Added Rigby SIGN v2 fold, S1277.
- **Playbook templates** (parent doc / child audit /
  canonical summary). Live in
  `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11. Never
  re-copy templates into any downstream doc; cite playbook
  §11 instead. Added Rigby SIGN v2 fold, S1277.

If you find yourself typing content that already exists in
Context-Kit or another Donkey Betz canonical source, stop and
cite instead. Every duplication is a future drift.

---

# Part 3 — How Fresh Claude Thinks (Decision Tree)

The question the OS answers first is not *"what should I do?"*
but *"what class of work is this?"* Classification determines
everything downstream — which docs to load, which checks to run,
whether Rigby reviews, whether commits happen.

## 3.1 The classification tree

```
                    User request arrives
                            │
                            ▼
              ┌──────────────────────────────┐
              │ Is it a short command        │
              │ matching a known pattern?    │
              │   "Start research group…"    │
              │   "Continue research group…" │
              │   "Close research group…"    │
              │   "Fix bug X"                │
              │   "Review PR #N"             │
              └──────────────┬───────────────┘
                             │
                YES ─────────┴────────── NO
                 │                        │
                 ▼                        ▼
     ┌───────────────────┐      ┌───────────────────────┐
     │ Route to the      │      │ Classify by intent:   │
     │ matching contract │      │  1. Question about    │
     │ (§5, §8)          │      │     state/docs?       │
     └─────────┬─────────┘      │     → NAVIGATION      │
               │                │  2. Question about    │
               │                │     code behavior?    │
               │                │     → INVESTIGATION   │
               │                │  3. "How should we…"  │
               │                │     → DESIGN          │
               │                │  4. "Why doesn't X    │
               │                │     work?"            │
               │                │     → BUG             │
               │                │  5. "Add / change     │
               │                │     feature X"        │
               │                │     → IMPLEMENTATION  │
               │                │  6. "Audit / map / …" │
               │                │     → RESEARCH        │
               │                │  7. Meta (docs,       │
               │                │     process, OS)      │
               │                │     → META-PROCESS    │
               │                │  8. Ambiguous /       │
               │                │     multi-class       │
               │                │     → ASK CHRIS       │
               │                └───────────┬───────────┘
               │                            │
               └─────────────┬──────────────┘
                             │
                             ▼
                ┌─────────────────────────────┐
                │  Load matching startup      │
                │  contract from §8           │
                └─────────────┬───────────────┘
                              │
                              ▼
                ┌─────────────────────────────┐
                │  Execute:                   │
                │   1. Required reads         │
                │   2. Verification steps     │
                │   3. Work                   │
                │   4. Rigby routing (if any) │
                │   5. Commit gate (Chris)    │
                │   6. Handoff + START-NEXT   │
                └─────────────────────────────┘
```

## 3.2 Classification rules

**When the request matches a short command exactly** (playbook
§21 vocabulary), route deterministically. Do not re-classify.

**When intent is ambiguous**, ask Chris. Do not guess. This is
one of the highest-value rules in the OS: the cost of
misclassification (running a research contract on a bug-fix
request, or vice versa) is high, and Chris resolving it in
30 seconds is cheap.

**When intent spans multiple classes** — e.g., *"Fix the RAG
provenance filter and document why"* is BUG + RESEARCH — the
default is to run the *higher-authority* class first. Research
before implementation. Investigation before fix. Design before
code. Then the follow-on class runs after the first completes.

**When Chris explicitly names the class** — *"quick fix, don't
research, just patch"* — honor the override. Chris's classification
wins over the router's.

## 3.3 What "thinking" means in this context

*Thinking* here is not open-ended reasoning. It is:

1. **Absorb the bootstrap layer** (§4).
2. **Classify.** One of 10 classes (§5).
3. **Load the contract** (§8).
4. **Execute the contract's required reads BEFORE doing work.**
5. **Perform work under the contract's rules.**
6. **Route to Rigby / Chris per the contract.**

The OS is deterministic by design. There is very little
free-form reasoning happening between "user request arrives"
and "contract executes." The reasoning happens *inside* the
contract, bounded by the contract's rules.

---

# Part 4 — Bootstrap Startup Sequence

Bootstrap runs in two levels. **Level A** is universal and
class-agnostic — every session runs it. **Level B** is
class-scoped — the §5 router picks it. The split matters
because reading the entire OS + playbook + research library at
every session open is expensive; class-scoping keeps bootstrap
bounded.

## 4.1 Level A — universal bootstrap (always)

Level A runs regardless of what Chris asked for. It is ~5
minutes, mostly cached, and mandatory. Every step has a
**success criterion** — you can tell whether you actually did
the step or just skimmed.

| # | Action | Required? | Success criterion (how you know it worked) |
|---|--------|-----------|-------------------------------------------|
| A1 | `context-kit orient` | **REQUIRED** | Output shows source-of-truth chain + START-NEXT block + anchor previews + latest handoff. If any section is empty, the project's context-kit is misconfigured — flag to Chris. |
| A2 | Absorb `CLAUDE.md` | **REQUIRED** | You can name the active Rigby pin + the current arc + the 3 most recent PR conventions without re-opening the file. |
| A3 | Absorb `MEMORY.md` | **REQUIRED** | You can name at least 5 feedback rules relevant to the pending request class. |
| A4 | Read `00-START-NEXT-SESSION.md` in FULL | **REQUIRED** | You have identified the FIRST-THING checklist, active pin, any open decisions, and any explicit constraints Chris flagged. |
| A5 | Read this document §0–§5 (skim §6–§9 headings) | **REQUIRED** | You can name the request class you will route to (§5.1) before opening any other doc. |
| A6 | Record repo state | **REQUIRED** | Current branch, HEAD SHA, uncommitted-changes status noted. Any unfamiliar branch/state flagged BEFORE work begins. |
| A7 | Capture request context | **REQUIRED** | You have written down: (a) change vs explain, (b) explicit constraints, (c) for bugs: repro path + observed vs expected. |
| A8 | Reconcile state surfaces | **REQUIRED** if arc-adjacent | Cross-check `OPEN_ARCS.md` arc status against `00-START-NEXT-SESSION.md` session priorities against the latest handoff's declared ship state. See §6.6 for the reconciliation rule. |
| A9 | Verify `service_context: local` if PA calls will happen | **CONDITIONAL** | `platform_config_tool overview` returned `service_context: local`. If PA calls are not needed this session, skip. |

## 4.2 Level B — class-scoped bootstrap

After Level A completes AND the request is classified via §5,
run Level B. This loads only the docs the §8 contract requires.

| Class | Level B reads |
|-------|--------------|
| RESEARCH | Playbook v2 §3–§9 + ARCHITECTURE_INDEX §9 + target domain §5.N + cross-domain §4.N + OPEN_ARCS.md |
| DESIGN-PREPARATION | Prior research input premises + playbook §3 phase discipline + EMPLOYEE_OS_PRIMITIVES §4 |
| DESIGN-DECISION (ADR) | The design-prep doc being ratified + prior related decisions |
| IMPLEMENTATION | Target subsystem `docs/topics/*.md` + PLATFORM_INVENTORY row + EMPLOYEE_OS_PRIMITIVES §4 + AUDIT_FINDINGS §18 (if Celery) |
| BUG INVESTIGATION | Handoff of incident + subsystem topic doc + MEMORY rules for topic + AUDIT_FINDINGS §18 (if Celery) + EVENT_SYSTEM_INVENTORY (if observability) |
| BUG FIX | §8.5 investigation output + IMPLEMENTATION class reads |
| ARCHITECTURE REVIEW | Doc under review + companion_anchors + related research library entries |
| DOC CLEANUP | DOC_LIFECYCLE.md + target topic doc |
| NAVIGATION QUERY | PLATFORM_INVENTORY autoblock + target topic doc + ARCHITECTURE_INDEX §9 |
| META-PROCESS | This doc + playbook + INDEX + prior process docs + inverse-grep for duplicated sections (§8.10) |
| OPS / DEPLOY / INCIDENT | Runtime health surfaces + docs/topics/celery-workers.md + docs/topics/infrastructure.md + AUDIT_FINDINGS §18 + latest deploy handoff |

Level B ends when the required reads are complete. Execute the
§8 contract next.

## 4.3 Why this order

- **Step 1 (orient)** produces the source-of-truth chain that
  every downstream step depends on. Skipping it means guessing.
- **Steps 2–4** are already auto-injected or trivially cheap;
  the discipline is *reading them, not skimming.*
- **Step 5 is currently the weakest link.** This doc is
  invisible from CLAUDE.md today (S1276 introspection §5.2).
  The P0 fix in §18 makes CLAUDE.md reference the OS. Until
  then, fresh Claude discovers the OS via 00-START-NEXT or
  via ARCHITECTURE_INDEX §3.11 — both indirect.
- **Step 6** is cheap and prevents the wrong-pin class (S1098,
  S1249 failure history).
- **Steps 7–8 branch** based on request class. Universal
  bootstrap ends at step 6; step 7+ is contract-scoped.
- **Step 9** is recommended, not required. Handoff-reading
  discipline is high-value but not fatal to skip.

## 4.4 What bootstrap does NOT include

- Reading the full `PLATFORM_INVENTORY.md`. It is a lookup
  surface, not an orientation read (2,100+ lines).
- Reading the full `PLATFORM_WHAT_IT_IS.md`. Orient gives the
  preview; full read is on-demand.
- Reading every `docs/topics/*.md`. On-demand per contract.
- Reading `docs/archive/`. Never at bootstrap; only when a
  specific old artifact is referenced.

Bootstrap is bounded — 5 minutes of reading, mostly cached from
`system-reminder` injection. The moment it turns into a
scavenger hunt, the OS has failed.

## 4.5 Bootstrap failure modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Skipped `context-kit orient` | Uses stale mental model of prior session | MEMORY rule enforces it; Skill definition mandates it |
| Missed `00-START-NEXT-SESSION.md` FIRST-THING block | Starts wrong contract or wrong arc | Read the file, do not just read the orient preview |
| Missed `service_context: local` check | Rigby calls hit prod | P0 in §18: add wrapper self-check to `pa_local.sh` (out of scope for this doc's implementation, in scope for its recommendation) |
| Did not find this doc | Runs pre-OS behavior (Chris writes long prompts) | P0 in §18: CLAUDE.md pointer |
| Skipped latest handoff | Repeats last session's work or misses its outputs | Handoff read is RECOMMENDED not REQUIRED; add a canonical "session close pointer" so orient's tail always names the next-mission entry point clearly |

---

# Part 5 — Research Router (11 Request Classes)

Once bootstrap Level A completes, the OS routes the request to
one of 11 classes. Each class has a startup contract (§8). This
section defines the routing rules; §8 defines each contract in
full.

## 5.1 The 11 classes

| # | Class | Trigger examples | Contract §8.N |
|---|-------|------------------|---------------|
| 1 | **RESEARCH** | *"Start research group NNNN"*, *"audit X"*, *"map integration between A and B"*, *"inventory the LLM callers"* | §8.1 |
| 2 | **DESIGN-PREPARATION** | *"pick between options A and B"*, *"draft the event schema"*, *"recommend a v0"* | §8.2 |
| 3 | **DESIGN-DECISION (ADR)** | *"ratify the decision"*, *"write the ADR for X"* | §8.3 |
| 4 | **IMPLEMENTATION** | *"add feature X"*, *"wire Y to Z"*, *"add a PA tool for A"* | §8.4 |
| 5 | **BUG INVESTIGATION** | *"why doesn't X work"*, *"debug Y"*, *"users report Z failing"* | §8.5 |
| 6 | **BUG FIX** | Follow-on from §8.5 with a known root cause + agreed fix | §8.6 |
| 7 | **ARCHITECTURE REVIEW** | *"is design X consistent"*, *"pressure-test proposal Y"* | §8.7 |
| 8 | **DOC CLEANUP** | *"remove drift from X"*, *"apply DOC-POINTER-V2 to Y"*, *"reorganize dir Z"* | §8.8 |
| 9 | **NAVIGATION QUERY** | *"what is the current X"*, *"where does Y live"*, *"what did session N ship"* | §8.9 |
| 10 | **META-PROCESS** | *"extend the playbook"*, *"write the OS doc"*, *"reorganize the research library"* | §8.10 |
| 11 | **OPS / DEPLOY / INCIDENT** | *"is prod healthy"*, *"did the deploy succeed"*, *"why did Rigby go down"*, *"celery workers stuck"*, *"queue backlog investigation"* | §8.11 |

**Class boundary notes (Rigby SIGN fold, S1277):**

- **DESIGN-PREPARATION vs DESIGN-DECISION.** Today the split is
  aspirational — no ADR corpus exists (§17.2 P1). Until the ADR
  corpus lands, route Chris's "ratify X" requests to §8.2 with
  a note that ratification is verbal, and open a §8.3 contract
  only when the ADR file gets written. Once ADR corpus is
  established, the hard boundary is: **DESIGN-PREPARATION =
  Chris has not ratified**; **DESIGN-DECISION = a committed ADR
  file exists**.
- **ARCHITECTURE REVIEW vs META-PROCESS.** If the review target
  is a research doc, use §8.7 REVIEW. If the review causes an
  edit to a governance / process doc (playbook, this OS,
  INDEX), the follow-on is §8.10 META-PROCESS. Rule: reviews
  produce *verdicts + fold recommendations*; the fold itself is
  META-PROCESS.
- **BUG INVESTIGATION vs OPS/DEPLOY/INCIDENT.** BUG is
  code-behavior investigation ("why doesn't feature X work").
  OPS is runtime-health investigation ("is prod up? did the
  deploy break something?"). If the OPS class investigation
  discovers a code root cause, chain to §8.5 BUG INVESTIGATION.

## 5.2 Per-class summary table

| Class | Required docs | Optional docs | Checks | Known pitfalls | Expected outputs | Commit rule | Rigby routing | Isolation pin |
|-------|--------------|---------------|--------|----------------|------------------|-------------|---------------|---------------|
| **1. RESEARCH** | Playbook, ARCHITECTURE_INDEX §9, target domain §5.N + §7, cross-domain §4.N | Prior topic docs, handoffs | 28 canonical Q's; anti-duplication scan; UNKNOWN honesty | Domain ambiguity → force Phase 0; binary classifications; skipping Rigby SIGN | Parent + N children + xx99 summary (arc) OR single audit; INDEX bump | Draft-first; Chris says "commit" | Required per playbook §15 stage | Fresh per group open (playbook §15 promoted rule) |
| **2. DESIGN-PREPARATION** | Prior research (input premises), playbook §3 phase discipline | Prior design-prep in the arc | Recommendation ≠ decision; Chris-gated; graduation triggers | Skipping "Chris gates" language; conflating with ADR | Doc with `authority: design-preparation`; §16 recommendation + graduation triggers | Draft-first | Required | Continue arc pin unless arc-open |
| **3. DESIGN-DECISION** | Design-prep doc + Chris ratification | Related research | Explicit ratification; ADR format | Silent "decisions" without ADR record | ADR (future — `docs/adr/`); no ADR corpus yet — flag as P1 gap | Chris ratifies IN the ADR | Chris IS the SIGN | Chris-directed |
| **4. IMPLEMENTATION** | Target subsystem topic doc, PLATFORM_INVENTORY row, EMPLOYEE_OS_PRIMITIVES §4 anti-duplication matrix if new model | Related research + ARCHITECTURE_INDEX §9 decision matrix | Anti-duplication scan; factory usage (OpenAI/Anthropic); typed exceptions on gates; verify before deleting "dead" code | Silent None from factory; in-function import shadowing; payload field as filter AND value; auto_followup=False suppressing banner; queue routing without Procfile+Makefile parity | Runtime PR with tests; handoff + verify_doc_claims | Standard PR gate; Chris approves | Not required unless design-adjacent | N/A (runtime work) |
| **5. BUG INVESTIGATION** | Handoff of the incident, relevant subsystem topic doc, related MEMORY rules, `docs/AUDIT_FINDINGS.md` §18 (Celery), `docs/EVENT_SYSTEM_INVENTORY.md` (observability) | Prior research | Reproduce; instrument; grep for stringified refs; verify with ORM; fail-loud-first PR arc | Deleting "dead" code before verifying callers; declaring root cause before reproducing; skipping visibility PR | Repro + root cause + fix plan (Investigation output) | No commits during investigation | Optional | N/A |
| **6. BUG FIX** | §8.5 investigation output, minimal-diff plan | — | 3-PR arc: visibility → root cause fix → telemetry cleanup; regression tests | Amending vs creating new commits after pre-commit failure; bypassing hooks | Runtime PR + test + handoff | Standard PR gate | Not required unless architectural | N/A |
| **7. ARCHITECTURE REVIEW** | Doc under review + its companion_anchors + related research | Prior Rigby SIGN records | Grep-verify binary claims; check anti-duplication; check anchor drift | Confirmation bias; skipping evidence verification | Review notes; SIGN-with-edits recommendations | If review triggers a doc edit, follow §8.10 | Optional (this IS a review) | Fresh if crossing arcs |
| **8. DOC CLEANUP** | `docs/00-START-HERE/DOC_LIFECYCLE.md` (V1/V2 banner rules, root-stability rule, never-delete rule) | Target subsystem topic doc | Never delete; use V2 pointer; check downstream link-rot | Deleting archived docs; moving root docs without pointer | Renamed/banner-flagged files + INDEX regeneration via `build_docs_index` | Chris approves per PR | Optional | N/A |
| **9. NAVIGATION QUERY** | Anchor pair (PLATFORM_INVENTORY + PLATFORM_WHAT_IT_IS), target-topic doc | ARCHITECTURE_INDEX §9 | Cite the source; do not synthesize from memory | Answering from priors when a lookup is 3 seconds away | Answer with cites | No commits (unless answer surfaces a drift → §8.8) | N/A | N/A |
| **10. META-PROCESS** | This doc + playbook + ARCHITECTURE_INDEX + relevant prior process docs + inverse-grep of docs that reference the target (drift-scan) | S1276 introspection, prior process arcs | Additive-first evolution (playbook §20); do not delete rules; version bumps; **inverse-grep sweep**: identify docs that currently duplicate content in target, to prevent post-edit drift | Rewriting rules older docs cite by number; skipping evolution changelog; forgetting the inverse-grep (edit lands but the duplicate elsewhere goes stale) | Process doc update; INDEX v-bump; drift-scan report | Draft-first; Chris ratifies | Optional per playbook §15 | Fresh isolation per meta-mission (this session pattern) |
| **11. OPS / DEPLOY / INCIDENT** | Runtime health surfaces (`context-kit orient` output, `make status` if available), `docs/topics/celery-workers.md`, `docs/topics/infrastructure.md`, latest deploy handoff, `docs/AUDIT_FINDINGS.md` §18 | MEMORY rule `feedback_local_celery_stall_playbook`; recent PR context; ARCHITECTURE_INDEX §9 for the affected surface | Reproduce symptom locally if possible; use 6-step diag sequence for Celery stalls; verify `service_context` before making calls; check queue depths + worker inspect ping | Blaming code before checking infra; killing workers without checking Redis broker; using `inspect ping` while another Claude is inspecting (contention) | Ops note or incident handoff; root-cause classification (infra vs code vs config vs external); action items | No commits during ops investigation; ops-triggered fixes route to §8.6 BUG FIX or §8.8 DOC CLEANUP | Optional | N/A |

## 5.3 Router fallbacks

**Ambiguous class** — ask Chris. Do not guess. Present the two
most likely classifications and let Chris pick.

**Multi-class request** — decompose into ordered contracts.
Research before design; design before implementation;
investigation before fix. The router chains contracts; each
runs to completion before the next begins.

**Class not listed** — should not happen. If it does, the OS
has a gap; run §8.10 META-PROCESS to add the class.

**Class override by Chris** — always honored. Chris can say
*"just answer, don't run the contract"* and the OS collapses
to a §8.9 NAVIGATION QUERY response.

## 5.4 What the router does NOT do

- **Does not decide whether to commit.** Every contract has a
  Chris-gate for commits. The router chooses the class; Chris
  approves the commit.
- **Does not decide business priority.** If two classes could
  run, Chris picks which first.
- **Does not skip Rigby SIGN when the contract requires it.**
  Skipping SIGN is a Chris-directed override, not a router
  choice.

---

# Part 6 — Repo State Surfaces

The OS needs to know the state of the repo. There are three
scopes of state, each answered by a different surface.

## 6.1 The three scopes

| Scope | Answers | Current surface | Status |
|-------|---------|-----------------|--------|
| **Runtime state** | What does the platform actually contain? Counts of agents, tools, tasks, models, routes. | `PLATFORM_INVENTORY.md` (auto-generated) | ✓ Exists |
| **Session state** | What is the current session's priority? What is the next mission? | `00-START-NEXT-SESSION.md` (overwritten per session) | ✓ Exists |
| **Arc state** | Which research groups are open? Which are in progress? Which are stalled? | *None today.* | ✗ **Missing — P0** |

## 6.2 Session state — `00-START-NEXT-SESSION.md`

**Role.** Session-scoped state. Overwritten every session close.
**Owner.** Session-closing Claude Code + Chris.
**Lifetime.** One session (until next session close).
**Contents.**

- FIRST-THING checklist (bootstrap gate)
- Active PA pin + retirement history
- Current arc status
- Open decisions
- Anti-scope reminders

**What belongs.** Anything time-scoped to "the next session's
open behavior." Not architectural facts. Not long-lived state.

**What does not belong.** Runtime counts (inventory owns them).
Doc-authority rules (DOC_LIFECYCLE owns them). Multi-session
plans (playbook + ARCHITECTURE_INDEX own them).

**Maintenance.** Overwrite at every session close. Follow the
implicit template established in S1200+ handoffs.

## 6.3 Arc state — proposed new file: `OPEN_ARCS.md`

**Role.** Cross-session state. Which research groups are
active. Which children are open. Which pins are claimed.
**Owner.** OS-managed (Claude writes; Chris ratifies).
**Lifetime.** Persistent. Never truncated. Groups closed via
playbook §17 flip state from `in-progress` → `closed` but
remain in the manifest.

**Proposed shape** (manual initially; runtime-generation is
P1):

```markdown
---
title: "Open Arcs — cross-session manifest of in-flight research"
status: active
authority: state
last_updated: 2026-07-01
maintainer: OS-managed (per §16 commit gate)
---

# Open Arcs

## Currently in-progress

| Group | Domain | State | Owner pin | Open child | Last activity | Notes |
|-------|--------|-------|-----------|------------|---------------|-------|
| 1300 | Memory | in-progress | pa-aa54193f240f4846 | S1301 RAG Retrieval Lanes | 2026-07-01 | Parent locked; D6 + D7 unresolved |

## Awaiting summary

*(none)*

## Stalled

*(none)*

## Closed (historical)

| Group | Domain | Closed session | Canonical summary |
|-------|--------|---------------|-------------------|
| — | Employee OS (pre-v1 arc) | S1272 | (no formal xx99 — pre-playbook) |
| — | Symbol Mapping arc | S1275 | (no formal xx99 — pre-playbook) |
| 1273 | Whole-Platform Inventory | S1273 | (single doc, no summary) |
| 1274 | Cross-Domain Integration | S1274 | (single doc, no summary) |
| 1276 | Playbook v2 | S1276 | (process doc, no summary) |
| 1277 | Research OS | S1277 | (this doc, no summary) |
```

**What belongs.** Group state + pin claim + last activity.
**What does not.** Findings (research docs own them). Prose
justifications (this doc owns them). Runtime state (inventory
owns it).

**Maintenance.** Every research group open OR close appends
or updates a row. Playbook §16 commit-when-Chris-says-so
extends to OPEN_ARCS updates.

**Manual vs generated.** Manual initially. Runtime automation
(generated from `grep -rH "^status:" docs/research/domains/`
+ frontmatter parse) is a P1 upgrade. Start manual.

## 6.4 Corpus state — existing

The corpus itself has three navigational surfaces already:

| Surface | Role |
|---------|------|
| `docs/INDEX.md` | Auto-generated file listing (via `manage.py build_docs_index`). Not hand-editable. Machine-readable directory. |
| `docs/research/ARCHITECTURE_INDEX.md` | Research library navigation (v10, S1276). Governance for docs/research/. |
| `docs/PLATFORM_INVENTORY.md` autoblock | Runtime counts. Authoritative per DOC_LIFECYCLE §2c. |

The gap is arc-state visibility. OPEN_ARCS.md fills it.

## 6.5 Should any additional state surfaces exist?

Considered and rejected:

- **CURRENT_WORLD.md** — snapshot of running services. Runtime
  concern, not doc concern. `context-kit orient` + local dev
  ops answer this.
- **CURRENT_RESEARCH.md** — redundant with OPEN_ARCS.md.
- **ACTIVE_STATE.md** — redundant with 00-START-NEXT-SESSION.md.

One arc-state surface (OPEN_ARCS.md) plus the three existing
state surfaces is the minimum viable set. Adding more increases
maintenance burden without covering new failure modes.

## 6.6 State surface reconciliation ritual (Rigby SIGN fold, S1277)

The three state surfaces (`00-START-NEXT-SESSION.md`,
`OPEN_ARCS.md`, latest handoff) can drift. Rules:

1. **`OPEN_ARCS.md` wins for arc status.** If session state
   says a group is `in-progress` but OPEN_ARCS shows `closed`,
   trust OPEN_ARCS. Fix session state.
2. **`00-START-NEXT-SESSION.md` wins for today's priorities.**
   Session state is authored at the end of each session and
   reflects Chris's most recent intent. It supersedes any
   OPEN_ARCS "next action" hint.
3. **Latest handoff wins for what shipped.** If either
   OPEN_ARCS or START-NEXT claims a session shipped X and the
   handoff shows the session shipped Y, trust the handoff. Fix
   the other two.
4. **Conflict rule.** When the three surfaces disagree at
   session open, write a one-line reconciliation note to
   `OPEN_ARCS.md` (top-of-file "Recent reconciliations"
   subsection) AND to the current handoff. Do NOT silently pick
   a winner; explicit rewrites prevent recurring drift.
5. **Trigger.** Level A step A8 runs this reconciliation
   check. If the surfaces agree, skip. If they disagree, apply
   rules 1–3, then note under rule 4.

The reconciliation ritual is what makes the state surfaces
usable across parallel Claude sessions — see §10.3 multi-Claude
risk.

---

# Part 7 — Documentation Authority Hierarchy

The mission's suggested hierarchy is *close* but conflates two
dimensions: (a) **truth authority** (who wins on conflict), and
(b) **read priority** (who to read first for orientation). This
section separates them.

## 7.1 Truth authority — who wins on conflict

```
┌────────────────────────────────────────────────────────────────┐
│  TIER 0 — Runtime (code + database + Redis + Celery)           │
│    Ultimate truth. All other layers are derivations or claims. │
└─────────────────────────┬──────────────────────────────────────┘
                          │ (re-derivation)
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 1a — Generated inventories (derived from runtime)        │
│    PLATFORM_INVENTORY.md (regenerable via                      │
│    generate_platform_inventory), docs/INDEX.md (regenerable    │
│    via build_docs_index). Auto-derived from Tier 0.            │
│    WINS OVER any narrative claim on counts, per                │
│    DOC_LIFECYCLE.md §2c.                                       │
│                                                                │
│  TIER 1b — Measured ops snapshots (observations of runtime)    │
│    Ops digests, SLO snapshots, incident postmortems, telemetry │
│    reports, deploy verification notes. Manually authored but   │
│    describe live runtime state at a point in time. Wins over   │
│    narrative on operational-state claims for its snapshot      │
│    window; loses to Tier 1a when snapshot is older than the    │
│    latest inventory regeneration.                              │
└─────────────────────────┬──────────────────────────────────────┘
                          │ (governance)
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 2 — Governance                                           │
│    DOC_LIFECYCLE.md (banner rules, root-stability, never       │
│    delete), EMPLOYEE_OS_PRIMITIVES.md (anti-duplication +      │
│    reuse matrix), API_PATH_POLICY.md (API conventions).        │
│    Rules that other docs follow. Do not violate.               │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 3 — Narrative anchors                                    │
│    PLATFORM_WHAT_IT_IS.md, KNOWLEDGE_PIPELINE.md,               │
│    EVENT_SYSTEM_INVENTORY.md, UDB_BEHAVIOR_LAYER.md,           │
│    UDB_TRANSLATION_LAYER.md.                                   │
│    Canonical prose descriptions. Wins over topic/narrative     │
│    subsystem docs on shape questions; loses to Tier 1 on       │
│    counts.                                                     │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 4 — Process framework                                    │
│    RESEARCH_OPERATING_SYSTEM.md (this doc),                    │
│    DOMAIN_RESEARCH_PLAYBOOK.md v2, ARCHITECTURE_INDEX.md v10.  │
│    Rules for how research + design happens. Consumed by the    │
│    OS; not itself a source of runtime truth.                   │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 5 — Research library                                     │
│    docs/research/ — audits, inventories, design-space          │
│    research, design-preparation, canonical summaries, parent   │
│    scoping docs. Grounded in file:line cites; UNKNOWN honesty. │
│    Wins over Tier 6+ on architectural claims. Older research   │
│    superseded by newer research within the same arc.           │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 6 — Reference documentation                              │
│    Root-level docs/*.md (ARCHITECTURE.md, AGENTS.md,           │
│    SPIDERS.md, SERVICES.md, DATABASE_MODEL_REFERENCE.md,       │
│    API.md, BACKEND_REFERENCE.md, etc.).                        │
│    Traditional engineering references. Many carry              │
│    DOC-POINTER-V1 stats-drift banners. When banner is          │
│    present, prose is authoritative, counts are not.            │
│                                                                │
│  ▶ Tier 5 vs Tier 6 disambiguator (Rigby SIGN fold, S1277):    │
│    If the doc has file:line citations AND a `verifier_loop`    │
│    frontmatter field, treat as Tier 5. Otherwise Tier 6.       │
│    Some docs currently at root are architecturally load-       │
│    bearing (ARCHITECTURE.md) but pre-verifier-loop era —       │
│    they read as Tier 6 for now; a future doc-cleanup pass      │
│    can promote them to Tier 5 by adding evidence citations     │
│    + verifier_loop.                                            │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 7 — Subsystem docs                                       │
│    docs/topics/*.md (embedding-optimized, current state),      │
│    docs/narratives/*.md (long-form platform narratives).       │
│    Best for Rigby RAG. Loses to Tier 5 research on              │
│    architectural claims; loses to Tier 1 on counts.            │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 8 — Session state                                        │
│    00-START-NEXT-SESSION.md, latest handoff.                   │
│    Current work state. Highest recency but NOT authority —     │
│    can contradict Tier 5 research and lose (research wins).    │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 9 — Historical docs (usable for context)                 │
│    docs/handoffs/, docs/audits/, docs/reports/,                │
│    docs/audit-2026/, docs/plans/, docs/roadmap/.               │
│    Build history. Cite for context ("why did we decide X?");   │
│    may be used for retrospective synthesis. Not authoritative  │
│    for current state.                                          │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────────────┐
│  TIER 10 — Archive (preservation only)                         │
│    docs/archive/ (1,388 files, 18 MB).                         │
│    Never deleted per policy. Historical corpus material.       │
│    NEVER used for synthesis. Cite ONLY when a specific         │
│    archived doc is named by the user; do not surface via       │
│    grep-driven "related reading" recommendations.              │
│                                                                │
│  ▶ Tier 9 vs Tier 10 boundary (Rigby SIGN fold, S1277):        │
│    Tier 9 is ok as evidence for "how did this state come to    │
│    be." Tier 10 is white-paper corpus preservation only. If    │
│    a synthesis is drawing on Tier 10, ask whether the source   │
│    should be promoted to Tier 9 (recategorized out of          │
│    archive). Default: leave in archive; cite only if user      │
│    explicitly names it.                                        │
└────────────────────────────────────────────────────────────────┘
```

## 7.2 Conflict resolution rules

1. **Runtime beats everything.** If code says X and any doc
   says Y, X wins. Docs get flagged as drift; code stays.
2. **Generated inventory beats prose on counts.** Never
   handwrite a count in a doc without citing
   `PLATFORM_INVENTORY.md` autoblock; when writing anyway, add
   DOC-POINTER-V1 banner.
3. **Governance beats content.** DOC_LIFECYCLE + primitives
   matrix rules over doc-body claims about lifecycle or model
   choice.
4. **Newer research beats older research** within the same
   arc, per playbook §16 status-transition rule. Older docs
   flip to `status: superseded` and cite the successor.
5. **Research beats topic doc.** If a topic doc says a
   subsystem works X way and a research doc verified Y at
   file:line, research wins. Topic doc gets a drift banner or
   update.
6. **Prose wins over prose on drift-free surfaces.** Two topic
   docs disagreeing without a research doc to arbitrate → the
   one with more recent `last_verified` frontmatter wins.
7. **Session state does NOT beat research.** 00-START-NEXT-
   SESSION.md is transient; a research finding it contradicts
   is drift in the session state.
8. **Archive beats nothing.** Historical only. Never
   authoritative.

## 7.3 Read priority — a separate dimension

Read priority is *not* authority. It is *what to load first for
a given task*. Determined by the §5 router and §8 contract.

Universal bootstrap (§4) reads Tiers 1, 2, 3, 4 in miniature.
Per-contract reads are class-scoped.

Example: NAVIGATION QUERY class reads Tier 1 (inventory) + Tier
7 (topics) first. RESEARCH class reads Tier 4 (playbook) + Tier
5 (prior research) + Tier 3 (anchors) first.

## 7.4 Rules the hierarchy implies

- Every new doc must self-classify by tier (via
  `authority:` frontmatter and physical location).
- Cross-tier citation always points *up* — a Tier 7 doc cites
  Tier 3 anchors, not vice versa.
- Drift banners exist because Tier 6 canonical docs cannot
  keep up with Tier 1 auto-generated counts. That is expected;
  the banner is the fix.
- When a Tier 5 research doc supersedes a Tier 6 root doc, the
  root doc gets DOC-POINTER-V2 (supersession) pointing to the
  research doc.

## 7.5 Where this hierarchy lives

This §7 is the canonical hierarchy statement. When other docs
need to cite it, they cite `RESEARCH_OPERATING_SYSTEM.md §7`.
Do not duplicate the hierarchy elsewhere; drift risk is high.

---

# Part 8 — Startup Contracts

One contract per class. Each contract specifies: required
reads, optional reads, verification, work rules, completion
criteria, Rigby routing, commit rules, isolation pin.

## 8.1 RESEARCH contract

**Trigger.** *"Start research group NNNN: X"* or
*"Continue research group NNNN: <slot>"* or *"Close research
group NNNN"* or any request explicitly scoped as
audit / inventory / discovery.

**Delegates to.** `DOMAIN_RESEARCH_PLAYBOOK.md` v2 as
authoritative specialization. The OS routes *to* the playbook;
the playbook governs the work.

**Required reads.**

1. `DOMAIN_RESEARCH_PLAYBOOK.md` v2 (§3–§9 minimum; §21
   Standard opening sequence for the current stage)
2. `ARCHITECTURE_INDEX.md` §3.N for target domain (or the
   §3.11 playbook if no domain-specific row exists yet) + §5
   domain map + §7 gaps + §9 decision matrix + §10 timeline
3. `platform_architecture_inventory.md` §5.N + any §7 overlap
4. `cross_domain_integration_audit.md` §4.N + relevant §5–§16
5. Target domain's `docs/topics/*.md` (if it exists)
6. Target domain's `docs/narratives/*.md` (if it exists)
7. `OPEN_ARCS.md` — is this group already open? Who claimed it?

**Optional reads.** Prior handoffs from the arc; other domain
research groups if cross-dependencies exist.

**Verification.**

- Bootstrap complete (§4).
- `service_context: local` confirmed if Rigby will be routed.
- Fresh isolation pin generated (playbook §15 promoted rule).
- Pin ownership verified per MEMORY rule
  `feedback_pa_local_verify_ownership`.

**Work rules.**

- Parent-vs-single decision per playbook §2 STAGE 0 verdict
  procedure (defaults to parent if any ambiguity).
- 6 parallel Explore sub-agents per playbook §13 for child
  audits (not for parents, not for canonical summaries).
- All 28 canonical questions per playbook §9 answered — cite,
  reference, or explicit `UNKNOWN`.
- Frontmatter per playbook §6 metadata standard.
- Cross-reference policy per playbook §7 (never duplicate,
  always reference).

**Completion criteria** (per playbook §17 graduation criteria).

**Rigby routing** (per playbook §15 stage table):
- Parent scoping: optional light SIGN
- Child audit: **required** full SIGN
- Canonical summary: **required** full SIGN

**Commit rule.** Draft-first. Chris says "commit it" per
playbook §16.

**Isolation pin.** Fresh per group open by default. Retire at
session close.

**Expected outputs.**
- Arc: parent doc + N children + xx99 canonical summary + N+2
  INDEX bumps
- Single-audit: one audit + 1 INDEX bump

---

## 8.2 DESIGN-PREPARATION contract

**Trigger.** *"Recommend v0 for X"*, *"pick between options"*,
*"draft the schema for Y"*, *"scope the migration"*.

**Required reads.**
1. Prior research input premises (the "what" doc)
2. Prior actor-role research if actors are involved
3. `DOMAIN_RESEARCH_PLAYBOOK.md` §5 (Research vs Design vs
   Implementation phase discipline)
4. `EMPLOYEE_OS_PRIMITIVES.md` §4 (anti-duplication)

**Optional reads.** Other arcs' design-preparation docs for
pattern reuse (e.g., Symbol Mapping arc §3.10 → §3.12
progression).

**Verification.**
- Frontmatter has `authority: design-preparation`.
- Recommendation includes explicit Chris-gate language.
- Graduation triggers documented (§16.3.1 of Symbol Mapping
  Option Selection as canonical example).

**Work rules.**
- Recommend; do not decide.
- Enumerate rejected options with rationale.
- Name explicit out-of-scope items.

**Completion criteria.**
- Recommendation is reversible (or its irreversibility is
  documented).
- Every prior research doc's finding cited if relevant.
- Rigby SIGN folded.

**Rigby routing.** Required (playbook §15).

**Commit rule.** Draft-first.

**Isolation pin.** Continue arc pin.

**Expected outputs.**
- Design-preparation doc with `authority: design-preparation`
- INDEX §3.N row + §10 timeline + phase update

---

## 8.3 DESIGN-DECISION (ADR) contract

**Trigger.** *"Ratify the recommendation from X"*, *"write the
ADR for Y"*.

**Status of ADR corpus today.** **No formal ADR corpus
exists.** The research library's design-preparation docs (§3.10,
§3.12) leave decisions to Chris verbally. **This is a P1 gap
called out in §17.**

**Required reads (once ADR corpus exists).**
1. The design-preparation doc being ratified
2. Prior related decisions
3. `DOC_LIFECYCLE.md` for canonical location conventions

**Verification.**
- Chris ratification explicit.
- ADR references design-preparation as input.
- Prior options + rejected options documented.

**Work rules.** ADR format (to be defined when corpus is
established). Recommended sections:
- Context
- Decision
- Consequences
- Alternatives considered
- Reversibility
- Status (proposed / accepted / superseded)

**Completion criteria.** Chris explicit "ratified" statement.

**Rigby routing.** Chris ratification IS the SIGN.

**Commit rule.** Chris ratifies IN the ADR commit message.

**Isolation pin.** Chris-directed.

**Expected outputs.** ADR file in `docs/adr/` (proposed
location — see §17).

---

## 8.4 IMPLEMENTATION contract

**Trigger.** *"Add feature X"*, *"wire Y to Z"*, *"add PA tool
for A"*, *"implement recommendation from research doc B"*.

**Required reads.**
1. Target subsystem `docs/topics/*.md`
2. `PLATFORM_INVENTORY.md` §row for affected surfaces
3. `EMPLOYEE_OS_PRIMITIVES.md` §4 anti-duplication matrix if
   any new model / handler / tool is proposed
4. `AUDIT_FINDINGS.md` §18 canonical Celery deferred list if
   any new task or beat entry is proposed
5. `ARCHITECTURE_INDEX.md` §9 decision matrix for the affected
   surface
6. If implementing recommendation from a design-preparation
   doc: that doc, ratified.

**Optional reads.** Prior handoffs of similar features.

**Verification.**
- `service_context: local` if the work touches PA.
- Anti-duplication scan complete.
- Factory usage confirmed for LLM callers (Anthropic /
  OpenAI factories mandatory per MEMORY rules).
- Typed exceptions on gates; no silent None returns.
- Pre-commit hooks pass; no `--no-verify`.

**Work rules.**
- Verify before deleting "dead" code (grep callers +
  stringified refs + docs + last 5–10 handoffs).
- Follow the fail-loud → root-cause → telemetry-cleanup 3-PR
  arc for masked bugs.
- Test on real DB, not mocks, for QuerySet-heavy features.
- Match Procfile ↔ Makefile queue parity for any new queue
  routing.
- Never `context.get('user')` as FK — always `getattr(self,
  'user', None)`.
- `gpt-5*` calls need `max_completion_tokens ≥ 4000`.

**Completion criteria.**
- PR merged.
- Tests pass.
- Feature visible in UI (per MEMORY rule
  `feedback_vertical_slice`).
- Handoff written.
- If docs affected: run `verify_doc_claims --only-drift`.

**Rigby routing.** Not required unless design-adjacent.

**Commit rule.** Standard PR gate. Chris approves.

**Isolation pin.** N/A (runtime work).

**Expected outputs.**
- Runtime PR(s)
- Test coverage
- Handoff
- Doc updates if scope crosses `docs/topics/*.md`

---

## 8.5 BUG INVESTIGATION contract

**Trigger.** *"Why doesn't X work"*, *"debug Y"*, *"users
report Z failing"*.

**Required reads.**
1. Handoff of the reported incident
2. Relevant subsystem `docs/topics/*.md`
3. Related MEMORY rules (search MEMORY.md for topic keywords)
4. `docs/AUDIT_FINDINGS.md` §18 (if Celery-adjacent)
5. `docs/EVENT_SYSTEM_INVENTORY.md` (if observability-adjacent)
6. Related audit rows in `docs/audits/`

**Optional reads.** Prior research if the bug touches a
researched subsystem.

**Verification.**
- Reproduction attempted before root-cause hypothesis.
- Local repro if possible; describe steps.
- Instrumentation added before deletion of suspected code.

**Work rules.**
- **Do not delete "dead" code without the 3-axis sweep**
  (grep + docs + handoffs).
- **Fail-loud first.** Populate error fields + greppable logs
  BEFORE fixing.
- **Reproduce before you diagnose.** Do not accept the
  reported symptom as the root cause without independent repro.
- **Verifier loop.** Every claim in the investigation output
  gets a file:line cite.
- **UNKNOWN honesty.** If evidence is thin, mark UNKNOWN.

**Completion criteria.**
- Root cause identified with evidence.
- Fix plan drafted (3-PR arc if masking is involved).
- Regression test named.

**Rigby routing.** Optional.

**Commit rule.** No commits during investigation. Investigation
output is a note or a handoff, not code.

**Isolation pin.** N/A.

**Expected outputs.**
- Investigation note (in handoff or a `docs/BUGS/*.md`)
- Repro steps
- Root cause + evidence
- Fix plan → routes to §8.6

---

## 8.6 BUG FIX contract

**Trigger.** Follow-on from §8.5 with a Chris-approved root
cause + fix plan.

**Required reads.**
1. The §8.5 investigation output
2. Everything §8.4 IMPLEMENTATION requires for the affected
   subsystem

**Verification.**
- Repro reproduced under the fix (i.e., fix actually addresses
  the root cause).
- Regression test added.
- No `--no-verify`.
- Amend-vs-new-commit discipline per MEMORY rule (create new
  after pre-commit failure, don't amend).

**Work rules.** All §8.4 IMPLEMENTATION rules + fail-loud-first
3-PR arc for masking bugs.

**Completion criteria.** Same as §8.4 IMPLEMENTATION.

**Rigby routing.** Not required unless architectural.

**Commit rule.** Standard PR gate.

**Isolation pin.** N/A.

**Expected outputs.** Fix PR + test + handoff.

---

## 8.7 ARCHITECTURE REVIEW contract

**Trigger.** *"Review doc X"*, *"pressure-test proposal Y"*,
*"second opinion on Z"*.

**Required reads.**
1. The doc / proposal under review
2. Its `companion_anchors` frontmatter (load all)
3. Related research library entries (via ARCHITECTURE_INDEX
   §3.N)
4. Prior Rigby SIGN records if present in `verifier_loop`

**Verification.**
- Grep-verify every binary claim ("X is dormant / absent /
  missing") before agreeing with it.
- Cross-check anchor drift.
- Confirm anti-duplication.

**Work rules.**
- Do not conflate intentional separation with missing
  integration (S1274 EventBus lesson).
- Do not use binary language for continuous reality.
- Cite file:line for every counter-claim.

**Completion criteria.**
- Verdict: SIGN-clean / SIGN-with-edits / NEEDS-MORE.
- Fold recommendations returned to author.

**Rigby routing.** Optional (this contract IS a review).

**Commit rule.** If review triggers a doc edit, follow §8.10
META-PROCESS.

**Isolation pin.** Fresh if crossing arcs.

**Expected outputs.**
- Review notes
- Verdict
- Fold recommendations

---

## 8.8 DOC CLEANUP contract

**Trigger.** *"Remove drift from X"*, *"apply DOC-POINTER-V2 to
Y"*, *"reorganize directory Z"*.

**Required reads.**
1. `docs/00-START-HERE/DOC_LIFECYCLE.md` — banner rules,
   root-stability, never-delete
2. Target subsystem `docs/topics/*.md` if the cleanup crosses
   a subsystem

**Optional reads.** `PLATFORM_INVENTORY.md` for drift checks.

**Verification.**
- Never delete — rename, banner, or archive.
- V1 banner for stats drift.
- V2 banner for supersession / relocation.
- Regenerate `docs/INDEX.md` via `build_docs_index` after
  moves.

**Work rules.**
- Root-stability: root-level docs stay at root unless
  DOC_LIFECYCLE explicitly permits move.
- Preserve superseded content — mark, don't delete.

**Completion criteria.**
- Banners applied consistently.
- INDEX regenerated.
- `verify_doc_claims --only-drift` re-run.

**Rigby routing.** Optional.

**Commit rule.** Chris approves per PR.

**Isolation pin.** N/A.

**Expected outputs.**
- Renamed / banner-flagged files
- INDEX regeneration

---

## 8.9 NAVIGATION QUERY contract

**Trigger.** *"What is the current X"*, *"where does Y live"*,
*"what did session N ship"*, *"how many agents"*, *"is X
canonical"*.

**Required reads.**
1. Bootstrap complete (§4).
2. For counts: `PLATFORM_INVENTORY.md` autoblock (direct
   lookup).
3. For subsystem shape: `docs/topics/<subsystem>.md`.
4. For architectural claims: `ARCHITECTURE_INDEX.md` §9
   decision matrix → target doc.
5. For session history: `docs/handoffs/SESSION_<N>_*.md`.

**Optional reads.** Related narratives.

**Verification.**
- Cite the source (file:line or §N.M).
- Do not synthesize from memory when a lookup is 3 seconds
  away.

**Work rules.**
- Direct answer with cite.
- If lookup surfaces drift: route to §8.8 DOC CLEANUP as
  follow-on (do not silently fix in-place).
- If Chris framed the query as personal ("who am I", "am I
  logged in"), that is a PA / auth question not covered by
  this contract — route through Rigby.

**Output format (Rigby SIGN fold, S1277).** Every NAVIGATION
QUERY response follows this shape unless the query is
open-ended enough to warrant discussion:

```
<one-line direct answer>
Cite: <file:line or §N.M>
Next: <optional pointer for follow-on read; omit if none>
```

Example:
```
Currently 83 agents in AGENT_MAP (74 enabled, 9 rerouted).
Cite: docs/PLATFORM_INVENTORY.md autoblock "Agents" row (S1276 refresh).
Next: docs/topics/agent-system.md for the routing shape.
```

Multi-part queries produce N such blocks. Do not synthesize
prose paragraphs when the deterministic format suffices.

**Completion criteria.**
- Answer given with cite.
- Drift (if found) routed forward.

**Rigby routing.** N/A (unless the query IS a PA query).

**Commit rule.** No commits.

**Isolation pin.** N/A.

**Expected outputs.** Answer + cites.

---

## 8.10 META-PROCESS contract

**Trigger.** *"Extend the playbook"*, *"write the OS doc"*,
*"reorganize the research library"*, any change to
governance-tier docs (§7 Tier 2 / Tier 4).

**Required reads.**
1. The doc being changed (in full)
2. All docs that reference it (**forward-grep** for the
   filename)
3. **Inverse-grep** (Rigby SIGN fold, S1277): docs that the
   changed doc references, to identify which of them may now
   contain duplicated content post-edit. This catches
   drift-creation at edit time rather than after.
4. `DOMAIN_RESEARCH_PLAYBOOK.md` §20 architecture evolution
   policy (if the playbook is being extended)
5. `RESEARCH_OPERATING_SYSTEM.md` (this doc) if the OS is
   being extended
6. `ARCHITECTURE_INDEX.md` §3.N + §10 for the affected doc

**Verification.**
- Additive-first evolution (§20 playbook rule).
- Do not rename sections older research groups cite by
  number.
- Version bump if the change is substantive.
- Backwards compatibility preserved.
- **Drift-scan report** (Rigby SIGN fold, S1277): for every
  doc surfaced by the inverse-grep in step 3, note whether the
  edit created a duplicate section. If yes, plan the drift-fix
  as a follow-on PR (do NOT bundle unless the fix is a
  one-line pointer update).

**Work rules.**
- Version-bump the frontmatter.
- Append to `verifier_loop`; never truncate.
- Add a changelog row.
- Update ARCHITECTURE_INDEX per playbook §16 index-bump rules.

**Completion criteria.**
- Change committed with Chris approval.
- INDEX v-bump applied.
- Changelog updated.

**Rigby routing.** Optional per playbook §15 for
`authority: process` docs. Chris gates directly.

**Commit rule.** Draft-first. Chris ratifies.

**Isolation pin.** Fresh isolation pin per meta-mission (this
session's pattern — `pa-95ce3cbf0a2aa0cc` for S1277).

**Expected outputs.**
- Process doc update
- INDEX v-bump
- Changelog entry
- Drift-scan report

---

## 8.11 OPS / DEPLOY / INCIDENT contract (Rigby SIGN fold, S1277)

**Trigger.** *"Is prod healthy?"*, *"Did the deploy succeed?"*,
*"Why did Rigby go down?"*, *"Celery workers stuck"*, *"Queue
backlog investigation"*, *"Redis broker slow"*, *"WebSocket
disconnects"*, incident response.

**Required reads.**
1. Latest deploy handoff (if the trigger is deploy-related)
2. `docs/topics/celery-workers.md` (if worker / queue
   involved)
3. `docs/topics/infrastructure.md` (if infra involved)
4. `docs/AUDIT_FINDINGS.md` §18 canonical Celery deferred
   list (if the concern is task-fire behavior)
5. `docs/EVENT_SYSTEM_INVENTORY.md` (if observability layer
   involved)
6. MEMORY rule `feedback_local_celery_stall_playbook` (if
   worker stall)
7. MEMORY rule `feedback_docker_force_recreate` (if new code
   seems missing after deploy)

**Optional reads.** Recent PR context; ARCHITECTURE_INDEX §9
decision matrix for the affected surface.

**Verification.**
- Reproduce symptom locally if possible.
- Verify `service_context` matches the environment being
  investigated (do NOT run `platform_config_tool overview`
  against prod when investigating a local issue).
- For Celery stalls: use the 6-step diag sequence per MEMORY
  playbook (CeleryTaskEvent → queue depths → `inspect ping` →
  log grep for `mutex.cc` → purge stale queues → restart
  without beat).
- For worker-inspect contention: coordinate with other Claude
  sessions before running `inspect ping` (§10.3
  multi-Claude risk).

**Work rules.**
- **Do not blame code before checking infra.** Redis, Postgres,
  Celery broker, deploy config, environment variables are
  first-check targets.
- **Do not kill workers without checking Redis broker state.**
  Killing a healthy worker under a broker issue makes the
  incident worse.
- **Classify root cause explicitly.** One of: infra (Redis /
  Postgres / broker / DNS), code (bug newly deployed), config
  (env var / feature flag), external (LLM provider outage / rate
  limit / third-party API), unknown.
- **Fail-loud over fail-quick.** If the trigger is "did the
  deploy succeed?", capture the deploy verification signals
  (health endpoint, migration status, worker startup logs)
  before answering.
- **Timeline the incident.** Note what happened, when, in what
  order. Timeline drives post-mortem quality.

**Completion criteria.**
- Symptom reproduced OR marked "cannot reproduce; cite
  observations."
- Root cause classified.
- Action items named:
  - If code root cause → route to §8.5 BUG INVESTIGATION.
  - If doc drift surfaced → route to §8.8 DOC CLEANUP.
  - If runbook gap → route to §8.10 META-PROCESS to update
    the relevant subsystem topic doc.
- Ops note or incident handoff written.

**Rigby routing.** Optional. If the incident is Rigby-facing
(PA down, tool broken), route AFTER she's back up; use
`pa_local.sh` with fresh isolation pin if uncertain about her
own conversation state.

**Commit rule.** No commits during ops investigation.
Fixes route to §8.6 BUG FIX contract with a normal PR gate.

**Isolation pin.** N/A for the investigation itself. If the
investigation involves calling Rigby for information, fresh
isolation pin to prevent conversation pollution.

**Expected outputs.**
- Ops note or incident handoff
- Timeline
- Root cause classification
- Action items with §8.N routing
- (Optional) postmortem document classified as Tier 1b in §7

---

# Part 9 — Thinking Templates Registry

Templates are canonical *shapes* for research outputs. Each
template names section order, frontmatter shape, and required
metadata. Using a template prevents section-drift across the
library.

## 9.1 Template registry

| Template | Location | Governed by | Exemplar |
|----------|----------|-------------|----------|
| **Domain parent scoping** | Playbook §17.1 | `authority: parent-doc` | `1300_memory_domain_scoping.md` (S1300) |
| **Domain child audit** | Playbook §17.2 (20 sections) | `authority: research` | Every §3.1–§3.9 doc |
| **Canonical summary (xx99)** | Playbook §17.3 | `authority: research` | *None yet — S1399 will be first* |
| **Architectural inventory** | Established S1273; not yet in playbook as formal template | `authority: research` | `platform_architecture_inventory.md` (32 domains) |
| **Cross-domain integration audit** | Established S1274 | `authority: research` | `cross_domain_integration_audit.md` |
| **Design-space enumeration** | Established S1272 | `authority: research` | `authority_enforcement_design_space.md` |
| **Design preparation (option selection)** | Established S1274 | `authority: design-preparation` | `symbol_mapping_option_selection_design.md` |
| **Design preparation (schema design)** | Established S1275 | `authority: design-preparation` | `symbol_mapping_event_schema_design.md` |
| **Design decision (ADR)** | *Not yet formalized — P1 gap in §17* | `authority: design-decision` | *None* |
| **Failure analysis / substrate audit** | Established S1268 | `authority: research` | `employee_os_communication_substrate_audit.md` |
| **Process document** | Established S1274 (playbook) | `authority: process` | Playbook, this OS doc |
| **Investigation log / repro notebook** (Rigby SIGN fold, S1277) | *Not yet formalized — P1 gap in §17.2* | `authority: investigation` | *None yet* |
| **Ops incident report** (Rigby SIGN fold, S1277) | *Not yet formalized — P1 gap in §17.2* | `authority: ops-snapshot` (Tier 1b per §7) | *None yet* |
| **Research question (short note)** | *Not yet formalized* — small note format for one-question scoping deliverables | `authority: scoping` | *None* |
| **Implementation review** | *Not yet formalized* | `authority: review` | *None* |

## 9.2 Rules for templates

1. **New templates are formalized via §8.10 META-PROCESS.**
   Do not invent per-session template shapes.
2. **Playbook §17 owns the three research-arc templates.**
   Others live in the exemplar doc and get promoted to the
   playbook when a third instance ships (playbook §20
   evolution-trigger rule).
3. **Frontmatter shape is standardized in playbook §6.**
   Every template uses that shape; template-specific fields
   are additions, not replacements.
4. **Templates are additive.** Older instances stay under
   their version; new instances use the current template.

## 9.3 Should more templates be formalized?

Recommend formalizing before Group 1400:

- **ADR / Design Decision template** (**P1**). Symbol Mapping
  arc will need it once Chris ratifies Option E as canonical.
- **Investigation Log / Repro Notebook template** (**P1** —
  promoted from P2 per Rigby SIGN fold, S1277). Prevents
  per-session drift for Bug Investigation and Architecture
  Review classes. Canonical structure:
  - Symptom (observed vs expected)
  - Repro steps (executable)
  - Environment (branch + SHA + `service_context` + dirty
    status)
  - Hypotheses tested (with elimination evidence)
  - Files touched during investigation (read-only vs
    modified)
  - Remaining unknowns
  - Recommended next contract (§8.6 fix / §8.8 cleanup /
    §8.10 process update)
  Prevents investigations sprawling into
  non-reusable-scratchpads.
- **Ops Incident Report template** (**P1** — new per Rigby
  SIGN fold, S1277 §8.11). Structure:
  - Timeline (UTC timestamps)
  - Root cause classification (infra / code / config /
    external / unknown)
  - Blast radius
  - Action items (routed to §8.N)
  - Follow-on runbook update (if any)
  Lands under Tier 1b in §7 (measured ops snapshot).
- **Research Question / Scoping Note** (**P2**). Short 1-page
  format for single-question research (e.g., "should X be
  extracted?"). Would have been useful for §7.11 focus mode
  inventory.
- **Implementation Review template** (**P2**). For post-merge
  reviews of implemented recommendations (e.g., after Group
  1300 Memory recommendations become PRs).

---

# Part 10 — Navigation and Discoverability

## 10.1 What fresh Claude can find today

| Surface | Fresh Claude finds it via | Discovery cost |
|---------|--------------------------|----------------|
| CLAUDE.md | Auto-injected | Zero |
| MEMORY.md | Auto-injected | Zero |
| 00-START-NEXT-SESSION.md | `context-kit orient` | Zero |
| PLATFORM_INVENTORY.md | CLAUDE.md + orient anchor preview | Zero |
| PLATFORM_WHAT_IT_IS.md | CLAUDE.md + orient anchor preview | Zero |
| DOC_LIFECYCLE.md | Referenced by CLAUDE.md governance discipline | Low |
| Subsystem topic docs | CLAUDE.md "Subsystem Documentation" table | Low |
| Root reference docs (ARCHITECTURE.md, AGENTS.md, etc.) | CLAUDE.md "Reference Documentation" table | Low |

## 10.2 What fresh Claude cannot find today

Per S1276 introspection §5.2 + this doc's investigation:

| Surface | Missing discoverability | Cost |
|---------|-------------------------|------|
| `RESEARCH_OPERATING_SYSTEM.md` (this doc) | Zero mentions in CLAUDE.md, START-HERE, or auto-loaded MEMORY | **HIGH — makes this doc invisible** |
| `DOMAIN_RESEARCH_PLAYBOOK.md` | Zero mentions in CLAUDE.md; only surfaces via `00-START-NEXT-SESSION.md` (session-specific) or `ARCHITECTURE_INDEX.md` §3.11 (circular) | **HIGH** |
| `ARCHITECTURE_INDEX.md` | Not in CLAUDE.md reference table | HIGH |
| `ARCHITECTURE_INDEX.md` §9 decision matrix | Buried at line ~1725 of ~2100 | HIGH |
| `OPEN_ARCS.md` (proposed) | Does not exist yet | HIGH once created |
| Whether a doc is canonical vs drifted vs archived | Requires opening the doc + reading frontmatter | MEDIUM |
| Cross-arc dependencies | Requires reading playbook §18 + inspecting frontmatter | MEDIUM |
| Multi-Claude session risk | Named only in MEMORY + playbook §15 fresh-isolation-pin rule | MEDIUM |
| Active PA pin | 00-START-NEXT-SESSION.md — but manual to verify ownership | MEDIUM |
| `tools/pa_local.sh` ownership | MEMORY rule enforces verification but requires manual check | MEDIUM |
| Whether service_context is local vs prod | Requires PA call; not surfaced at bootstrap | MEDIUM |

## 10.3 Discoverability failure catalog

Every unfindable surface above became a real failure at some
point in the S1200s:

- **Playbook / INDEX not read early enough** — S1268–S1272 pre-
  playbook sessions (retroactive validation).
- **Wrong pin** — S1098 admin/donkeyking mixup; S1249 prod URL.
- **Numbering context-crossing** — S1273/S1274 shared pin risk.
- **Domain ambiguity** — S1300 Memory a-f card ambiguity caught
  by Chris.
- **Handoff drift** — recurring across S1200s.
- **RAG provenance filter dropping relevant chunks** — S1300
  open (8 pre-filter → 0 returned).

The through-line: every failure could have been prevented by
better discoverability, either via CLAUDE.md pointers or via
runtime helpers (pa_local.sh self-check, service_context
auto-verify).

## 10.4 Fixes required for full discoverability

See §17 (Required New Documents) and §18 (Migration Plan).
Bullet form here:

1. **CLAUDE.md gets a "Research Library" subsection** pointing
   to this OS doc + playbook + INDEX.
2. **CLAUDE.md gets a "Startup checklist" subsection** with
   the §4 bootstrap sequence.
3. **`docs/00-START-HERE/README.md`** points to the research
   library.
4. **`OPEN_ARCS.md`** created and referenced from CLAUDE.md.
5. **ARCHITECTURE_INDEX §9 decision matrix** promoted to
   earlier in the doc (currently at line 1725; should be §3 or
   §4).
6. **`pa_local.sh` self-check** on first invocation each
   session (runtime — flagged as P1 in §18).

---

# Part 11 — Documentation Ownership

Every document must have a named owner — the party responsible
for keeping it accurate. Without ownership, docs drift silently.
This section defines ownership for every load-bearing surface
in and around the repo.

## 11.1 Ownership matrix

| Doc / Surface | Owner | Who updates | When | Verification |
|---------------|-------|-------------|------|--------------|
| Context-Kit skill (`.claude/skills/context-kit/SKILL.md`) | Context-Kit | Context-Kit maintainer (Chris upstream) | When Context-Kit ships a change | `context-kit orient` output changes |
| Context-Kit framework master (`docs/docs-pattern/`) | Context-Kit | Context-Kit maintainer | When framework evolves | Downstream instances (this repo + others) inherit |
| `CLAUDE.md` | Chris (ratifies) | Claude drafts via §10 META-PROCESS; Chris ratifies commits | When session norms change or new stats land | Session-open successful discovery |
| `MEMORY.md` (Claude auto-memory) | Claude Code (auto) | Claude, per user feedback | On feedback / correction events | Feedback rule reused successfully next session |
| `00-START-NEXT-SESSION.md` | Session-closing Claude | Session-closing Claude writes; Chris may edit but does not own | Every session | Next session's bootstrap reads it correctly |
| `docs/00-START-HERE/DOC_LIFECYCLE.md` | Donkey Betz (Chris ratifies) | On lifecycle rule change | Rarely | V1/V2 banner conventions applied consistently |
| `docs/00-START-HERE/README.md` + `INDEX.md` | Donkey Betz | On new load-bearing doc landing | Sporadic | Fresh Claude discovers research library |
| `docs/PLATFORM_INVENTORY.md` | Runtime (auto-generated) | `manage.py generate_platform_inventory` | On PR-merge cadence | `verify_doc_claims` returns empty |
| `docs/PLATFORM_WHAT_IT_IS.md` | Donkey Betz | Claude drafts, Chris ratifies | On subsystem-shape change | Anchor refresh notes in top of doc |
| `docs/EMPLOYEE_OS_PRIMITIVES.md` | Donkey Betz | Claude drafts, Chris ratifies | On new primitive or matrix update | Anti-duplication matrix applied at PR review |
| `docs/topics/*.md` | Donkey Betz | Claude drafts per subsystem session | On subsystem behavior change | Embedded in Rigby RAG; search-hits validate content |
| `docs/narratives/*.md` | Donkey Betz | Claude drafts on narrative refresh | On major subsystem-narrative shift | Human reader can absorb top-to-bottom |
| `docs/handoffs/SESSION_*.md` | Session-closing Claude | Every session close | Every session | Read at session open by orient |
| Root reference docs (`docs/*.md`) | Donkey Betz | Claude drafts + banner-tags | On subsystem change or on cleanup | DOC-POINTER-V1 banner reflects current drift status |
| `docs/research/ARCHITECTURE_INDEX.md` | Donkey Betz | OS-managed (Claude drafts; Chris ratifies) | Every research doc commit | Version bump + §1.N row + §8 timeline row |
| `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` | Donkey Betz | OS §10 META-PROCESS contract | On evolution trigger (§20 rule) | Version bump + changelog row |
| `docs/research/RESEARCH_OPERATING_SYSTEM.md` (this doc) | Donkey Betz | OS §10 META-PROCESS contract | On evolution trigger | Version bump + verifier_loop append |
| Research library parent docs (`domains/*/NN00_*.md`) | Donkey Betz | Author of parent-scoping session (Claude) | On group open | Chris ratifies locked child sequence |
| Research library child audits (`domains/*/NNNN_*_audit.md`) | Donkey Betz | Author of child audit session (Claude) | On child session close | Rigby SIGN + Chris commit |
| Research library canonical summaries (`domains/*/NN99_*_summary.md`) | Donkey Betz | Author of summary session (Claude) | On group close | Rigby SIGN + Chris commit + anchor-update applied |
| Cross-domain integration audit (`docs/research/platform/*.md`) | Donkey Betz | On new whole-platform audit | Sporadic (~every 12 months) | Rigby SIGN + Chris commit |
| ADR corpus (`docs/adr/`) — future | Donkey Betz | On design-decision ratification | Per decision | Chris ratifies IN the ADR |
| `docs/research/OPEN_ARCS.md` (proposed) | OS-managed | Every group open / close | Every group state change | State-reconciliation ritual (§6.6) passes |
| Runtime-generated docs (`docs/INDEX.md`) | Runtime | `manage.py build_docs_index` | Post-doc-add cadence | `verify_repo_guardrails.py` catches drift |
| Runtime factory helpers (`anthropic_client_factory.py` etc.) | Runtime | On client library change | Rarely | Test suite validates timeout contract |
| Drift tooling (`verify_doc_claims`, `build_docs_provenance`) | Donkey Betz | Runtime — Claude edits when adding new claim registrations | On new claim registration | Command exits clean on scheduled runs |
| Start-here entrypoint pattern (`docs/00-START-HERE/`) | Split — pattern is Context-Kit; instances (README/INDEX) are Donkey Betz | Context-Kit maintainer for pattern; Claude for instance | On pattern evolution or entrypoint addition | Fresh Claude bootstrap succeeds |

## 11.2 Sub-ownership within the research library

The research library has internal ownership rules on top of the
matrix above. See playbook §16 commit rules for the full flow.
Summary:

- **Draft ownership**: the session author (Claude) owns the
  draft until it lands as `status: active`.
- **Active ownership**: the arc's parent doc (or the doc's own
  frontmatter) names the ongoing maintainer. For most
  research docs, `owner: claude` means "the OS maintains this
  via §10 META-PROCESS contract."
- **Superseded ownership**: superseded docs retain the
  original author in frontmatter; the superseding doc names
  itself via `supersedes:`.

## 11.3 Update triggers

Every ownership row has a *trigger* — when the update must
happen. The three most common triggers:

1. **Runtime change trigger.** Runtime code changed → inventory
   regenerates → `verify_doc_claims` catches drift → topic
   doc / root reference doc / narrative gets updated.
2. **Research trigger.** New research finding → ARCHITECTURE_INDEX
   bumps → any affected topic doc or narrative gets a
   pointer.
3. **Governance trigger.** Playbook or OS rule changes → §10
   META-PROCESS contract runs → INDEX + affected docs get
   references updated.

If a trigger fires and the owner does not act, that is
**documentation debt** (companion concept to research debt in
§15). It surfaces via `verify_doc_claims --only-drift`.

## 11.4 Ownership anti-patterns

- **Anonymous ownership.** No `owner:` frontmatter field means
  no one is on the hook. Prohibited for Tier 3–5 docs.
- **Wrong-owner attribution.** Runtime-generated docs must not
  claim a human owner in frontmatter (they are `owner: runtime`
  or `owner: manage.py generate_platform_inventory`).
- **Cascade ownership.** Documents that say *"owner: whoever
  edits this next"* are unmaintained by design. Every doc has
  a specific named owner or no one owns it.
- **Chris as global owner.** Chris ratifies; Claude drafts.
  Listing Chris as owner of every doc obscures the actual
  authorship. Use `owner: claude (drafted SNNNN)` for
  Claude-authored docs.
- **Zombie ownership** (Rigby SIGN v2 fold, S1277). Owner is
  named but update triggers never cause action. Every
  ownership row must have a matching *verification* mechanism
  so drift is detectable. If no verification exists, the
  ownership is theatrical.
- **Shared ownership without a tie-break** (Rigby SIGN v2
  fold, S1277). Listings like *"Donkey Betz + Claude Code"*
  or *"team-owned"* create no accountability. Pick one owner
  (even if updater is a different party). Composite listings
  are an anti-pattern.
- **Owner without verification** (Rigby SIGN v2 fold, S1277).
  Same as zombie ownership stated inversely: ownership must
  be paired with a verification signal. If the owner cannot
  answer *"how do you know the doc is still current?"*, the
  ownership is broken.

---

# Part 12 — Repeatability — Reducing Chris's Prompt Burden

The target: *"Start Research Group 1700"* is enough. Every
downstream decision either is codified in this OS + the playbook,
or explicitly deferred to Chris as a decision he must make.

## 12.1 What Chris currently supplies verbally

| Item | Currently | Should become |
|------|-----------|---------------|
| Session ID | Chris types the number | Next open slot in playbook §22 queue → §6 OPEN_ARCS.md lookup |
| Domain slug | Chris implies from queue | Playbook §7 rule + queue table |
| Parent vs single | Chris often catches ambiguity | Playbook §4 STAGE 0 verdict procedure runs first, before scope commitment |
| Which pin to use | 00-START-NEXT-SESSION.md hardcodes | Fresh isolation pin default per playbook §15 promoted rule (S1276 §7.3) |
| Rigby routing | Playbook §15 table | Already documented; needs prominence |
| Commit approval | Chris explicit "commit it" | **Must remain Chris** — this is the gate |
| Cross-arc delegation ratification | Chris verbal at parent open | **Must remain Chris** — this is an architectural call |
| Domain naming | Chris implicit | **Must remain Chris** for new domains not in queue |
| Anti-scope ratification | Chris verbal | Parent doc drafts, Chris ratifies |
| Follow-on queue ordering | Chris preference | Draft ranks by uncertainty × risk × unblocked; Chris re-orders |
| Naming a new failure mode | Chris flags in-session | Router §5.4 gap; add to playbook if pattern emerges |
| Design ratification | Chris "commit as canonical" | **Must remain Chris** — this is the design gate |

## 12.2 What MUST remain Chris

The short list:

1. **Commit approval.** Every doc lands via Chris "commit it."
   Playbook §16 default is do-not-commit.
2. **Design ratification.** Design-preparation → design-decision
   requires Chris. The ADR corpus (§8.3 + §17) formalizes this.
3. **Cross-arc delegation.** Parent doc's `delegates_to:`
   entries need Chris's OK — this is architectural taxonomy,
   not evidence-gathering.
4. **New domain naming.** For queue additions not yet in
   playbook §22.
5. **Override of any codified rule.** Chris can override the
   router, override the SIGN routing, override the pin default.
   The OS honors overrides.

Everything else is codifiable and should be codified before
Group 1400 opens.

## 12.3 The "Start Group NNNN" target

After the P0 fixes in §18 land, this is the target execution:

```
Chris: "Start research group 1700: Observability"

Claude (silently):
  1. Bootstrap (§4)
  2. Classify: RESEARCH class (§5.1 row 1)
  3. Load §8.1 RESEARCH contract
  4. Required reads:
     - Playbook v2
     - ARCHITECTURE_INDEX §9 (which is now findable — §18 P0)
     - platform_architecture_inventory.md §5.25 Observability
     - cross_domain_integration_audit.md §4.25 Observability
     - docs/topics/celery-workers.md + docs/topics/agent-system.md
     - OPEN_ARCS.md (P0) — confirm 1700 not already claimed
  5. Verification:
     - service_context: local
     - Fresh isolation pin generated
     - Update OPEN_ARCS.md with row for Group 1700
  6. Parent-vs-single verdict per playbook §2 STAGE 0.
     Observability has 5+ execution telemetry layers (per
     S1274 §18.6) — verdict: PARENT-WITH-CHILDREN. Draft
     parent doc.
  7. Draft parent per playbook §11.1 template.
  8. Return summary to Chris:
     "Group 1700 parent draft at
      docs/research/domains/observability/1700_observability_domain_scoping.md.
      Suggested child sequence: P1 CeleryTaskEvent, P2 LLMCallEvent,
      P3 AgentExecution, P4 ToolCallRecord, P5 OpsRunEvent,
      P6 Event vs Observability separation, S1799 summary.
      Need your D1 ratify parent shape; D2 delegate boundary
      with event architecture arc (Group 1900); D3 launch
      cadence."

Chris (60 seconds later): "D1 yes. D2 delegate event bus to 1900.
   D3 immediate — begin S1701 CeleryTaskEvent audit."

Claude: (executes S1701 per §8.1 contract)
```

Nine words of prompt from Chris produced 30–60 minutes of
autonomous work under the OS + playbook contract. That is the
target rhythm.

## 12.4 What repeatability does NOT mean

- **Not autonomous commits.** Chris still gates commits.
- **Not autonomous design decisions.** Chris ratifies.
- **Not skipping Rigby SIGN.** Contracts specify SIGN routing.
- **Not skipping Chris for ambiguity.** When the router hits
  §5.3 ambiguity, ask.

Repeatability is *predictable execution*, not *Chris removal*.

---

# Part 13 — Research Contract

Every research session begins by declaring a **Research
Contract**. Without it, sessions drift into research-for-its-
own-sake (§1.5 anti-pattern).

## 13.1 The 8 required fields

Every research session MUST answer these 8 questions BEFORE any
Explore sub-agent sweeps run, BEFORE any 28-question audit
begins, and BEFORE any Rigby routing:

| Field | What it answers | Failure if missing |
|-------|-----------------|--------------------|
| **1. Why** | The problem this research addresses. In one sentence. Cites the failure mode or decision that motivates the work. | Research becomes solution-in-search-of-a-problem. |
| **2. Deliverable** | The concrete artifact this session produces. Doc path + expected §-section shape. | Session sprawls; no crisp "done" state. |
| **3. Out of scope** | What this research explicitly does NOT cover. Delegates named. | Scope creep; parent-vs-single ambiguity. |
| **4. Dependencies** | Prior research groups, canonical docs, or runtime state this session inherits. Cited by path or §. | Author reinvents context; misses relevant prior work. |
| **5. Expected Decision** | What decision does this research unblock? Named as concretely as possible. Format: *"Decision: <text>. Ratifier: <Chris / Chris+Claude / other>. By: <deadline or end-of-session>."* (Rigby SIGN v2 fold, S1277) | Research-for-its-own-sake. §1.5 anti-pattern. Decision without ratifier = orphaned recommendation. |
| **6. Completion Criteria** | Objective checklist for "this session is done." Not "when it feels done." | Session ends prematurely OR runs forever. |
| **7. Stop Condition** | When additional evidence would not change the decision. Signal Rigby uses to say "you've done enough." | Session runs forever. |
| **8. Future Research** | What did this session identify as follow-on? Queued for §15 Research Debt log. | Findings evaporate; future sessions rediscover them. |

## 13.2 Where the contract is recorded

Two locations:

1. **Frontmatter of the session's primary deliverable.** New
   frontmatter fields required (playbook §6 metadata standard
   should absorb these in a future evolution):

   ```yaml
   research_contract:
     why: "..."
     deliverable: "docs/research/domains/<slug>/<N>_<slug>_audit.md"
     out_of_scope:
       - "..."
     dependencies:
       - path: "docs/research/..."
         role: "input premise for X"
     expected_decision: "..."
     completion_criteria:
       - "..."
     stop_condition: "..."
     future_research:
       - "..."
   ```

2. **Session-open handoff addition.** The session's opening
   handoff (either the prior session's `00-START-NEXT-SESSION.md`
   or a new `docs/handoffs/SESSION_NNNN_OPEN.md` if the arc
   warrants it) restates the contract in prose so Chris can
   ratify before work starts.

## 13.3 When the contract is written

- **For research-class sessions:** BEFORE the 6 parallel
  Explore sub-agents fire. Contract → Chris ratifies → sweeps
  launch.
- **For parent-scoping sessions:** DURING §8 STAGE 0 verdict
  work. The parent doc contains the contract in its own
  frontmatter + intro section.
- **For canonical summary sessions:** BEFORE synthesizing.
  The summary's contract is the synthesis scope, not the
  underlying findings.
- **For non-research-class sessions:** OS §8 contract's
  "Required reads" already partially serves this role. Full
  Research Contract is optional but recommended for large
  design or implementation sessions.

## 13.4 Ratification

Chris ratifies the Research Contract before work begins. Options:

- **Full ratify.** Contract stands as written.
- **Modify.** Chris rewrites a field. Author updates in place.
- **Reject.** Contract is wrong-scoped. Author redrafts.

If Chris is not immediately available, Claude proceeds under
the drafted contract but flags any subsequent divergence — do
NOT silently expand scope mid-session.

## 13.5 Contract violations

A session violates its Research Contract when:

- Scope expands beyond declared boundaries without a modify
  cycle.
- Deliverable landed in a different file than declared.
- Expected Decision is unnamed at close (no decision
  unblocked).
- Stop Condition is not verified — Rigby did NOT confirm
  research is finished.

Violations should be flagged in the session's Completion
Contract report (§14). Repeated violations trigger a playbook
§20 evolution — the contract shape may need adjusting.

## 13.6 Why this is mandatory (not optional)

Rigby SIGN caught the risk explicitly in the S1276
introspection review: research sessions without an explicit
decision-to-unblock become research-for-its-own-sake. The
Research Contract is the enforcement mechanism. Without it,
the §1 Research Philosophy is aspirational.

---

# Part 14 — Completion Contract

If Research Contracts prevent sessions from starting wrong,
Completion Contracts prevent sessions from ending wrong.
Current observation: **startup discipline is high in the S1200s
arc; completion discipline is weaker.** This part formalizes
the missing side.

## 14.1 The 10-item completion checklist

Every session — research or otherwise — must complete this
checklist before closing:

- [ ] **1. Deliverable landed at declared path.** Cross-check
      against Research Contract §13 (if applicable) or against
      OS §8 contract (all classes).
- [ ] **2. Frontmatter complete.** All required fields per
      playbook §6 metadata standard + Research Contract fields
      if research-class.
- [ ] **3. Verifier_loop updated.** Rigby SIGN status
      resolved (SIGN-clean, SIGN-with-edits folded, or
      NEEDS-MORE with next-step plan). Never leave
      NEEDS-MORE open.
- [ ] **4. Stop Condition verified.** For research: additional
      evidence would not change the decision. Rigby confirms
      or Chris confirms.
- [ ] **5. Expected Decision named** (research) OR
      **acceptance criteria met** (implementation).
- [ ] **6. Cross-references landed.** Any ARCHITECTURE_INDEX
      bump drafted (not necessarily committed). Any §11
      Ownership matrix update noted.
- [ ] **7. Future work captured.** Follow-on items queued in
      canonical summary follow-on queue OR §15 Research Debt
      log OR next session's `00-START-NEXT-SESSION.md`.
- [ ] **8. Research debt logged.** §15 Research Debt for any
      known-unaddressed items.
- [ ] **9. Handoff written.** `docs/handoffs/SESSION_NNNN_*.md`
      landed with the session's ship state, decisions, and
      next-mission pointer.
- [ ] **10. `00-START-NEXT-SESSION.md` updated.** Overwrites
      prior priorities with next session's FIRST-THING
      checklist.

## 14.2 Rigby routing at close

Not all sessions require Rigby SIGN at close. See OS §8 per-
class routing. For research-class sessions:

- **Parent scoping:** Optional light SIGN per playbook §15.
- **Child audit:** REQUIRED SIGN before close.
- **Canonical summary:** REQUIRED SIGN before close.
- **Design-preparation:** REQUIRED SIGN before close.
- **Meta-process (this OS, playbook edits):** Optional per
  playbook §15; Chris gates directly.

Sessions that require SIGN do NOT close until SIGN is
resolved. NEEDS-MORE verdict blocks close.

## 14.3 Commit gate at close

Every session's close involves a commit-or-defer decision:

- **Chris says "commit it"** → apply playbook §16 commit
  rules; ARCHITECTURE_INDEX bump; single atomic commit.
- **Chris says "hold for review"** → draft stays uncommitted.
  Next session opens with the draft still in place. Ownership
  passes to the next session's Claude.
- **Chris silent** → default: do not commit. Log in the
  handoff as awaiting Chris ratification.

## 14.4 Index updates

If the session produced a research doc that lands, INDEX §1.N
row is drafted (whether or not committed) as part of close.
Playbook §16 index-bump rules govern:

- New §1.N row for the doc
- §8 timeline row
- §3 domain map update if applicable
- §5 gap closure or opening
- §9 roadmap advancement

Not landing these is a completion violation (§14.1 item 6).

## 14.5 Cross-references

Every doc cited by the session's deliverable needs verification
that the citation is still current:

- File:line cites: was the code recently refactored? If so,
  the cite may be stale.
- §-cites to other docs: did those docs' sections renumber?
- Playbook cross-refs: are they consistent with playbook v2
  numbering?

Stale cross-references are a form of research debt (§15).

## 14.6 Future work capture

Sessions almost always surface work they cannot complete.
Rules for capture:

- **Named + prioritized + assigned scope.** Not just "we
  should look at X later" — must include *why*, *when*, *what
  scope*.
- **Correct location.** Options:
  - Canonical summary follow-on queue (for arc-scoped work)
  - Research Debt log (§15) for unresolved research
  - `00-START-NEXT-SESSION.md` for the immediate next session
  - ARCHITECTURE_INDEX §5 gap for library-level gaps
- **Not everything is worth capturing.** Speculation that
  didn't survive the session is dropped, not logged.

## 14.7 Handoff requirements

`docs/handoffs/SESSION_NNNN_*.md` template:

```markdown
---
title: "Session NNNN — <slug>"
session: NNNN
date: YYYY-MM-DD
status: closed | ended-early | stalled
---

## What shipped
- <deliverables>

## What did not ship
- <deferred / cut items>

## Decisions ratified this session
- <if any>

## Research debt accrued
- <link to §15 log entries>

## Open risks / landmines
<Any known-fragile assumptions, deferred verifications, or
external dependencies that could bite the next session. Better
to over-flag than under-flag. Added Rigby SIGN v2 fold, S1277.>

## Next mission
<one-paragraph pointer to next session's FIRST-THING>
```

Handoffs are the arc's oral history. Skipping the handoff at
close is a completion violation that costs the next session's
Claude 30+ minutes of re-derivation.

## 14.8 Session state versus arc state at close

At close, the state surfaces must be reconciled per §6.6:

- **`00-START-NEXT-SESSION.md`** overwritten with next
  priorities.
- **`OPEN_ARCS.md`** (proposed) updated if arc state changed.
- **Latest handoff** is source of truth for what shipped.

Reconciliation ritual (§6.6) runs at close, not just at open.

## 14.9 Why completion discipline matters

Startup discipline (context-kit orient + CLAUDE.md + START-NEXT +
this OS) is well-formed in S1200s. Completion discipline is
weaker — handoffs drift; ARCHITECTURE_INDEX bumps get deferred;
future work items land in scratch notes; research debt
accumulates without tracking.

Every unfinished close costs the next session cognitive load.
Completion discipline makes the arc navigable.

---

# Part 15 — Research Debt

Research debt is the concept this OS introduces to name a
recurring failure mode: work that *looked* complete but left
questions, dependencies, or decisions unresolved. Companion to
Technical Debt; distinct in scope.

## 15.1 Definition

**Research Debt** exists whenever:

1. **Research questions remain** that block a downstream
   design or implementation decision.
2. **Design decisions are deferred** without a scheduled
   resolution.
3. **Dependencies remain unresolved** — the artifact cites a
   prerequisite that is not yet shipped.
4. **Future implementation cannot safely begin** because
   research is incomplete or the recommendation is
   ambivalent.

Research debt is NOT:
- Legitimate UNKNOWNs marked honestly (per playbook §14).
  Those are evidence, not debt.
- Deferred future research explicitly scoped for a later group
  (§14.6 future work capture is not debt).
- Follow-on ADRs Chris explicitly deferred with a "not yet"
  note.

Research debt IS:
- UNKNOWNs that block a Chris-ratifiable decision.
- Missing Rigby SIGN on required-SIGN docs.
- Findings surfaced but never routed to their proper location.
- Contradictions between research docs that were never
  reconciled.
- Cross-references that are stale and were never fixed.

### 15.1.1 Debt categories (Rigby SIGN v2 fold, S1277)

Every debt item classifies into exactly one category. Categories
drive routing and prioritization:

| Category | Definition | Payoff mechanism |
|----------|-----------|------------------|
| **DEBT-BLOCKING-UNKNOWN** | UNKNOWN in a research doc that blocks a downstream decision | Continue research; convert to answer |
| **DEBT-MISSING-RATIFICATION** | Design-preparation recommendation Chris has not ratified | Chris review + ratify (or explicitly defer with rationale) |
| **DEBT-CROSS-REF-DRIFT** | §-references stale after playbook or INDEX renumber | Doc cleanup (§8.8 contract) |
| **DEBT-MISSING-SIGN** | Required Rigby SIGN never routed | Route Rigby; fold verdict |
| **DEBT-INDEX-DRIFT** | Doc committed but ARCHITECTURE_INDEX §1.N row missing | Index bump PR |
| **DEBT-CONTRADICTION** | Two research docs disagree; neither is superseded | Author reconciliation note; supersede the wrong one |
| **DEBT-ORPHAN-FINDING** | Finding surfaced but never routed to its proper location (audit, ADR, follow-on queue) | Route to correct location |

Follow-on work captured in §14.6 is NOT automatically debt.
Debt requires the item to be *blocking* + *unowned or
unscheduled*. Explicitly deferred future work with an owner
and target session is NOT debt.

## 15.2 How research debt accrues

- **Session runs out of budget** before completion criteria
  are met.
- **Rigby SIGN skipped** when required.
- **Ambivalent recommendation** in a design-preparation doc
  that Chris cannot ratify.
- **Cross-reference drift** from playbook or INDEX renumbers.
- **Delegated to another arc** but never picked up.

## 15.3 How to measure research debt

Debt has three dimensions:

- **Blocking-count**: how many downstream decisions are stuck
  on this item? *Blocking* means: a specific
  design-preparation, ADR, implementation PR, or research
  session cannot proceed without this item resolving. Not
  "useful to have" — actually blocking.
- **Severity weight**: category-specific weight (Rigby SIGN
  v2 fold, S1277):
  - `DEBT-BLOCKING-UNKNOWN`: **weight 3**
  - `DEBT-MISSING-RATIFICATION`: **weight 3**
  - `DEBT-CROSS-REF-DRIFT`: **weight 1**
  - `DEBT-MISSING-SIGN`: **weight 2**
  - `DEBT-INDEX-DRIFT`: **weight 1**
  - `DEBT-CONTRADICTION`: **weight 3**
  - `DEBT-ORPHAN-FINDING`: **weight 2**
- **Age**: how long since the debt was logged (in days).

**Priority formula** (Rigby SIGN v2 fold, S1277 — replaces the
v2 draft's `blocking_count × log(age_in_days)` formula, which
scored day-0 items at zero):

```
priority = severity_weight * blocking_count * (1 + age_in_days / 30)
```

Properties:
- Day-0 debt is not zero-scored (base multiplier = 1).
- Age matters but linearly, not logarithmically — the graph
  is behavior-shaping, not fragile.
- Severity dominates for high-weight categories.

Higher priority = pay down first.

## 15.4 How to track

**Proposed new file: `docs/research/RESEARCH_DEBT.md`.** Manual
manifest initially; runtime-generated later (grep frontmatter
`research_debt:` fields across the library).

Shape:

```markdown
---
title: "Research Debt Log — cross-arc manifest"
status: active
authority: state
last_updated: YYYY-MM-DD
maintainer: OS-managed (per §14 close)
---

# Research Debt Log

## Active debt

| ID | Origin session | Origin doc | Item | Blocks | Age (days) | Priority | Owner |
|----|---------------|-----------|------|--------|-----------|----------|-------|
| RD-001 | S1275 | symbol_mapping_event_schema_design.md §17 | ADR corpus does not exist | Option E ratification | 1 | HIGH | Chris |
| RD-002 | S1274 | cross_domain_integration_audit.md §11 | Sports/DBAO island question unresolved | Group 1500 design | 1 | MEDIUM | Chris |

## Retired debt

| ID | Retired session | Origin | Item | How retired |
|----|----------------|--------|------|-------------|
| — | — | — | — | — |
```

Every session close (§14) checks whether any of its work
retired active debt. If yes, move the row to "Retired debt"
with the retiring session's ID.

## 15.5 Lifecycle

```
   Session close
        │
        ▼
   Debt accrues → RESEARCH_DEBT.md active row
        │
        ▼
   Later session addresses it
        │
        ▼
   Debt retired → moved to retired section
```

**Debt never disappears.** Retired debt is preserved as
historical record (never-delete rule applies).

## 15.6 Relationship to Technical Debt

| Dimension | Technical Debt | Research Debt |
|-----------|----------------|---------------|
| Scope | Runtime code + tests | Research corpus + design |
| Symptoms | Slow tests, brittle code, TODO comments | Deferred decisions, unresolved UNKNOWNs, stale cross-refs |
| Payoff | Refactor, tests, cleanup | Continue research, ratify decisions, sync cross-refs |
| Tracking | `docs/AUDIT_FINDINGS.md`, code comments, TODO backlog | Proposed `RESEARCH_DEBT.md`, canonical summary follow-on queue |
| Payment agent | Runtime PR | Research doc + Chris ratification |

The two are related. Research debt CAN become technical debt
if the missing research leads to a suboptimal implementation
that then requires runtime cleanup. Example: Symbol Mapping
Option E ratification is deferred → implementation happens
under Option E-provisional → later shift to Option B causes
migration cost = technical debt.

## 15.7 Debt paydown vs new research

Every research session must reserve some capacity for debt
paydown. Rule of thumb: if `RESEARCH_DEBT.md` has 5+ active
items in the same domain, the NEXT session in that domain
should prioritize paydown over new work.

This prevents debt spiral. Without the rule, new research
generates new debt faster than old debt retires.

## 15.8 Escalation

If a debt item ages past 90 days AND has blocking-count ≥ 2,
the OS flags it in `00-START-NEXT-SESSION.md` as a
must-consider item. Chris ratifies whether to pay it down or
explicitly retire the debt with rationale.

Items retired with rationale become historical record; items
paid down move to the retired section.

## 15.9 Anti-pattern: silent debt

The failure mode this section prevents: a session ships a
"complete" doc with hidden dependencies never called out.
Later sessions rediscover the dependency and pay the cost with
no memory of the original context.

Making debt explicit ends the recurring cost.

---

# Part 16 — Long-Term Vision

## 16.1 One-year state

After a year (call it S1500–S2500), the repo looks like this:

- **10+ research groups completed** (Memory 1300, Revenue 1400,
  Sports 1500, Content 1600, Observability 1700, Human
  Attention 1800, Event Architecture 1900, plus 3+ new
  domains that surface during the year).
- **Each group has parent + N children + xx99 summary**
  registered in ARCHITECTURE_INDEX.
- **`OPEN_ARCS.md` shows the live manifest** — most rows
  `closed`; 1–2 `in-progress` at any time.
- **ADR corpus (`docs/adr/`) established** — 20+ decisions
  ratified; every implementation PR cites its ADR.
- **CLAUDE.md is thin.** It points to the OS; OS routes
  everything. The 200-line CLAUDE.md today shrinks to ~80
  lines of pointers + top-level system stats.
- **Playbook is at v3 or v4** — additive evolution via
  §20 rule.
- **The OS is at v2 or v3** — same additive evolution.
- **Zero doc drift on counts.** `verify_doc_claims --only-drift`
  returns empty. Every root canonical doc carries a live V1
  banner or has been superseded.
- **Fresh Claude opens the repo, runs bootstrap, reads OS §0–§5,
  classifies user request, executes contract. Chris ratifies
  major decisions.**

## 16.2 What breaks without this OS document

- Every fresh Claude re-derives orientation from CLAUDE.md +
  scavenger hunt. Discovery cost stays high.
- Domain research groups continue to require 4,000-word
  prompts from Chris.
- Multi-Claude collisions on session IDs / pins / branches
  remain possible.
- New failure modes accumulate as folklore, not codified
  rules.
- The research library's structure calcifies without a
  governance layer.

## 16.3 Success criteria

The OS is successful when:

1. **A brand-new Claude reads only** `CLAUDE.md` + `MEMORY.md`
   + `00-START-NEXT-SESSION.md` + this OS doc — and executes
   the correct contract without Chris intervention.
2. **Chris's session-open prompts are ≤ 20 words** for
   in-queue research groups.
3. **`verify_doc_claims --only-drift`** returns empty for all
   Tier 1–4 docs.
4. **No new failure modes surface** that the OS could have
   prevented but didn't.
5. **Every research doc registered in ARCHITECTURE_INDEX**
   has SIGN status resolved and frontmatter complete.
6. **Multi-Claude collisions are extinct.** OPEN_ARCS.md +
   fresh-isolation-pin default make the collision class
   impossible.

## 16.4 Failure signs to watch for

- Chris's prompts growing longer for research opens.
- Recurring session-scoped instructions Chris types (e.g.,
  *"remember to use the local pin"*).
- Fresh Claude asking Chris questions the OS should answer.
- Rigby catching the same class of error twice.
- New docs landing without proper frontmatter or SIGN.

Each of these is a §20 evolution trigger for the playbook or
the OS.

---

# Part 17 — Required New Documents

Concrete list of documents that need to exist before the OS is
"complete" enough to support Group 1400 with minimum prompt
burden.

## 17.1 P0 — Must land before Group 1400

| # | File | Purpose | Approx. lines |
|---|------|---------|---------------|
| 1 | `docs/research/OPEN_ARCS.md` | Cross-session arc manifest (§6.3). Manually maintained; runtime-generated later. | 50 |
| 2 | CLAUDE.md addition (not a new file — extension) | "Research Library" subsection pointing to OS + playbook + INDEX + OPEN_ARCS. Startup checklist subsection. | +30 to existing |
| 3 | `docs/00-START-HERE/README.md` addition | Point to research library + OS + playbook. | +10 to existing |
| 4 | `docs/00-START-HERE/INDEX.md` addition | Same as above. | +5 to existing |

## 17.2 P1 — Should land soon

| # | File | Purpose |
|---|------|---------|
| 5 | `docs/adr/README.md` + first ADR template | Establish ADR corpus for §8.3 DESIGN-DECISION contract. First ADR: ratify Option E from Symbol Mapping arc if Chris chooses. |
| 6 | Investigation Log / Repro Notebook template (Rigby SIGN fold, S1277) | Canonical structure for Bug Investigation + Architecture Review classes. Formalize in playbook §11.4 or as its own template file. |
| 7 | Ops Incident Report template (Rigby SIGN fold, S1277) | Structure for §8.11 OPS/DEPLOY/INCIDENT contract outputs. Lands under Tier 1b in §7. |
| 8 | `docs/research/process/` topic docs for Bug Investigation + Doc Cleanup contracts | Optional — the OS §8 tables suffice for MVP. Only formalize if patterns diverge. |
| 9 | `.claude/skills/pa_local_selfcheck.md` (or wrapper enhancement) | Runtime helper — pa_local.sh self-verifies pin owner + service_context. Named as runtime work; not in this session's scope. |
| 10 | Playbook v3 addition | Fold OS §7 hierarchy into playbook cross-references. Version-bump per §20 evolution. |

## 17.3 P2 — Nice to have

| # | File | Purpose |
|---|------|---------|
| 11 | `docs/research/HISTORY.md` | Extract playbook §23 (relationship to existing research) + INDEX §10 timeline into a stand-alone history doc. Reduces load on playbook + INDEX. |
| 12 | Research Question / Scoping Note template | Short 1-page format for single-question research. Formalize in playbook §11.4 or here. |
| 13 | Implementation Review template | Post-merge review shape. Formalize when the first implementation review ships. |
| 14 | `docs/research/process/failure_modes.md` | Consolidate the S1200s failure catalog (from S1276 introspection §6 + this OS §10.3) into a single reference. |

---

# Part 18 — Migration Plan

Ordered, dependency-aware plan for landing the OS's
recommendations. **Chris ratifies before any of this
executes.**

## 18.1 P0 — Order of operations before Group 1400

1. **OS doc ratification.** Chris reads this doc. SIGN
   status resolved. Commit.
2. **OPEN_ARCS.md created.** Row for Group 1300 (in-progress)
   + closed history rows for pre-v1 arcs. Commit.
3. **CLAUDE.md extension.** Add "Research Library" subsection
   + "Startup checklist" subsection. Commit.
4. **START-HERE README/INDEX extension.** Add pointers to
   research library. Commit.
5. **ARCHITECTURE_INDEX §9 decision matrix promoted.** Move
   it earlier in the doc (§4 or §5) so fresh Claude
   discovers it. INDEX v10 → v11. Commit.
6. **Verify.** New Claude session opens, runs bootstrap,
   discovers OS via CLAUDE.md pointer, discovers playbook
   via OS §8.1, discovers ARCHITECTURE_INDEX §9 without
   scavenger hunt.

Estimated total effort: one focused session. Docs-only. No
runtime changes.

## 18.2 P1 — Before Q4 2026

7. **ADR corpus established.** First ADR: ratify Symbol
   Mapping Option E if Chris chooses.
8. **`pa_local.sh` self-check.** Runtime enhancement:
   verify pin owner + service_context on first invocation
   each session. This is runtime work — separate session,
   separate PR.
9. **Playbook v3.** Fold OS §7 hierarchy + evolution
   changelog updates. Additive per §20.

## 18.3 P2 — When triggered

10. **HISTORY.md extraction** when playbook + INDEX grow
    unwieldy.
11. **Research Question template** first time a single-Q
    research is needed.
12. **Implementation Review template** first time an
    implemented recommendation needs review.

## 18.4 Dependencies

```
OS ratified (P0.1)
   │
   ▼
OPEN_ARCS created (P0.2) ── depends on OS §6.3 shape
   │
   ▼
CLAUDE.md extended (P0.3) ── depends on OS + OPEN_ARCS existing
   │
   ▼
START-HERE extended (P0.4) ── depends on OS + CLAUDE.md
   │
   ▼
ARCHITECTURE_INDEX §9 promoted (P0.5) ── independent, can run parallel
   │
   ▼
Verification (P0.6) ── depends on all P0 above
   │
   ▼
Group 1400 open ── depends on P0 verification
```

P1 items depend on P0.6 verification.

P2 items depend on P1 triggers.

## 18.5 Risk of not migrating

- Group 1400 opens under the S1273 / S1274 / S1300 pattern
  (4,000-word prompts from Chris) — the OS's benefit does not
  materialize.
- The playbook v2 + OS v1 remain load-bearing but invisible.
- Multi-Claude collision risk persists.

## 18.6 Reversibility

Every P0 change is a doc edit. Reverting is `git revert`. No
runtime state involved. Low blast radius.

---

# Part 19 — Rigby SIGN Record

## 19.1 Routing decision

**Routed.** Per S1277 mission spec: *"This document MUST
receive a pressure-test."* Playbook §15 marks `authority:
process` docs as "optional" Rigby SIGN, but the mission
overrides — process doc governing the OS deserves independent
pressure-test.

## 19.2 Isolation pin

**Fresh isolation pin generated: `pa-95ce3cbf0a2aa0cc`.**

Reasoning: S1300 Memory arc pin (`pa-aa54193f240f4846`) is
reserved for Group 1300 continuity. S1277 is meta-process.
Cross-contamination risk if S1277 conversation lands on the
Memory arc pin. Playbook §15 "fresh isolation pin default for
research group opens" applies analogously to meta-mission
opens.

Pin retirement: at S1277 session close, retire in
`00-START-NEXT-SESSION.md`.

## 19.3 Pressure-test payload

Sent to Rigby via `tools/pa_local.sh --conversation
pa-95ce3cbf0a2aa0cc` at S1277 close of drafting phase.

```
Meta-research S1277 — Research Operating System draft ready for pressure test.

Doc: docs/research/process/RESEARCH_OPERATING_SYSTEM.md (v1 draft)

Scope: Designs the operating system every future Claude Code session
executes in unified-donkey-betz. Defines request classification,
bootstrap sequence, 10 startup contracts (one per work class),
documentation authority hierarchy (Tier 0 Runtime → Tier 10 Archive),
repo state surfaces, thinking template registry, discoverability
audit, repeatability targets, one-year vision. Positioned as the
superset containing DOMAIN_RESEARCH_PLAYBOOK v2 (research contract
specialization).

Please pressure-test.

Questions:
1.  Is any startup step (§4) unnecessary?
2.  Is any startup step missing?
3.  Can startup be simplified?
4.  Is any documentation authority tier ambiguous?
5.  Are the 10 request classes (§5.1) the right split? Missing classes?
    Overlapping classes?
6.  Are the 10 startup contracts (§8) correct? Any missing checks,
    pitfalls, or completion criteria?
7.  Can routing become deterministic without Chris intervention?
8.  Does this OS actually reduce Chris's prompt burden or does it just
    document what already happens?
9.  What would still require human intervention that this OS does not
    name?
10. What would make a brand-new Claude successful with this doc alone?
11. Is OPEN_ARCS.md the right shape (§6.3)?
12. Is the authority hierarchy (§7) correct? Should any tier merge, split,
    or reorder?
13. Are the thinking templates (§9) the right set? Any missing template
    that would prevent per-session drift?
14. Is the migration plan (§18) the right sequencing?
15. Is anything in this OS a duplicate of the playbook, INDEX, or
    CLAUDE.md that would create drift?

Response format:
Overall confidence: High / Medium / Low
Most accurate part:
Weakest part:
Biggest missing process step:
Biggest multi-session risk:
Most important documentation change:
Templates missing:
Authority tiers to merge / split / reorder:
Contracts to add / remove / change:
What Claude got wrong:
What must change before canonical:
Final verdict: SIGN-clean / SIGN-with-edits / NEEDS-MORE
```

## 19.7 Second-round Rigby SIGN (v2, S1277)

**Routed.** After v2 six-part extension, pressure-tested on
fresh isolation pin `pa-117d3edf9d7b80f8`. Rigby confirmed
`service_context: local`, read all six new parts via
`repo_tool`, grep-verified playbook cross-references in the
new content, produced verdict.

**Verdict.** **SIGN-with-edits (Medium confidence). Chris's
decision unblocked with edits.**

**Cross-reference bugs found in the six new parts.** None.
Playbook §-refs cited by the new parts (§2, §9, §15, §16, §20,
§21) all match actual playbook v2 §-numbers. One unverified
alignment risk: OS §2.7 rule 2 cites playbook §20 evolution
triggers with a "3+ research groups" threshold; Rigby did not
verify the exact threshold wording in playbook §20.

**12 must-fix edits folded (v2 → v2 with edits):**

1. §1.2 explicit enforcement rule — stop condition met ⇒
   continuing requires contract modification + Chris ratify.
2. §1.5 three additional anti-patterns — cite theater, UNKNOWN
   laundering, decision-free recommendations, curiosity
   hijack.
3. §2.3 two new ownership rows — drift tooling +
   start-here entrypoint pattern split.
4. §2.7 operational cadence — §2.7.1 added with per-session /
   monthly / on-context-kit-change cadence + reconciliation
   ownership + verification artifact.
5. §2.9 two new do-not-duplicate entries — DOC_LIFECYCLE rules
   + playbook §11 templates.
6. §11.1 owner-column tightening — CLAUDE.md single-owner =
   Chris (ratifies); 00-START-NEXT-SESSION single-owner =
   session-closing Claude.
7. §11.4 three additional ownership anti-patterns — zombie
   ownership, shared-without-tie-break, owner-without-
   verification.
8. §13.1 field 5 format update — Expected Decision now
   includes ratifier + deadline explicit format.
9. §14.7 handoff template — "Open risks / landmines" section
   added.
10. §15.1.1 debt categories — 7 explicit categories with
    payoff mechanism.
11. §15.3 priority formula replaced — new formula
    `severity_weight * blocking_count * (1 + age_in_days/30)`
    replaces broken `log(age)` formula.
12. §15.6 clarified — "Future work captured" is NOT
    automatically debt; debt requires blocking + unowned.

**Partial folds / deferred.** Rigby's response was cut off
during question 8 answer. Partial coverage of pressure-test
questions 9–20 was inferred from her overall verdict + fold
recommendations. Any residual v2 edits surface as v2.1
follow-on if Chris flags them.

**Post-fold verdict.** Draft is v2 (edits folded). Status
remains draft until Chris ratifies. Rigby SIGN status:
**SIGN-with-edits folded (12 must-fixes; 1 unverified
alignment note captured for follow-on).**

## 19.4 Rigby response (verbatim, S1277)

Received on pin `pa-95ce3cbf0a2aa0cc`. Rigby confirmed
`service_context: local` via `platform_config_tool overview`
before answering. She read the full 1,783-line draft in four
`repo_tool.read_file` chunks. Full verdict:

```
Overall confidence: Medium

Most accurate part:
- Part 5 authority hierarchy is the strongest and most
  operationally useful section. It correctly separates *truth
  authority* vs *read priority* and explicitly encodes
  "inventory wins on conflict" via Tier 1 / DOC_LIFECYCLE.

Weakest part:
- The request-class taxonomy + router is directionally good but
  not yet tight enough to be "OS-level deterministic." Admits
  "ASK CHRIS" for ambiguous/multi-class work — honest, but means
  the OS does not deliver the "<20 words" promise unless classes
  become more mutually exclusive and contracts encode clearer
  completion gates.

Biggest missing process step:
- A "minimal reproducible context" capture step early in
  bootstrap/contracts: repo branch/SHA + dirty status; is the
  user asking to change or explain?; for bugs: repro path +
  observed vs expected. Missing bridge between orientation and
  work.

Biggest multi-session risk:
- State scattering + drift between "session state" and "arc
  state." OPEN_ARCS.md + 00-START-NEXT-SESSION.md need a
  reconciliation rule.

Most important documentation change:
- Make this doc discoverable via CLAUDE.md immediately.

Templates missing:
- Investigation Log / Repro Notebook (P0/P1, not P2). Prevents
  investigation sprawl.

Authority tiers to merge / split / reorder:
- Split Tier 1 into 1a generated inventories + 1b measured ops
  snapshots.
- Merge Tier 9 + 10 OR define enforceable behavioral difference.
- Add Tier 5 vs Tier 6 disambiguator.

Contracts to add / remove / change:
- Add first-class Ops/Deploy/Incident Response contract.
- NAVIGATION QUERY: deterministic output format.
- META-PROCESS: inverse-grep for drift-scan.
- DESIGN-PREP vs ADR: hard boundary or merge.

What Claude got wrong:
- Claims "Nothing is asserted without a cite" (Appendix A.1) —
  aspirationally true, but several items are OS prescriptions
  not observations. Label them.

What must change before canonical:
1. Bootstrap sequence must be concretely checkable with success
   criteria per step.
2. Router/classes must cover ops/reliability/deploy.
3. OPEN_ARCS.md needs a concrete inline schema.

Final verdict: SIGN-with-edits
```

## 19.5 Folded edits (S1277)

All 15 must-fixes folded in place. Fold locations:

| # | Rigby ask | Fold location |
|---|-----------|---------------|
| 1 | Bootstrap read scope by class | §0 TL;DR steps 1 + 4 (Level A / Level B distinction) |
| 2 | Bootstrap concretely checkable | §4.1 Level A success-criterion column per step |
| 3 | Bootstrap Level A / Level B split | §4.1 Level A + §4.2 Level B |
| 4 | Minimal-context capture (branch/SHA, change-vs-explain, repro path) | §4.1 steps A6 + A7 |
| 5 | Prescriptive vs observational labeling | §0 TL;DR "Convention" callout |
| 6 | Add OPS / DEPLOY / INCIDENT class | §5.1 class 11 + §5.2 row 11 + §8.11 full contract |
| 7 | Class boundary rules | §5.1 "Class boundary notes" callout (Design-Prep vs ADR; Review vs Meta-Process; Bug vs Ops) |
| 8 | State reconciliation ritual | §6.6 "State surface reconciliation ritual" |
| 9 | Tier 1a / 1b split | §7.1 Tier 1a + Tier 1b (generated vs ops snapshots) |
| 10 | Tier 5 vs Tier 6 disambiguator | §7.1 Tier 6 callout with `verifier_loop` + file:line rule |
| 11 | Tier 9 vs Tier 10 boundary | §7.1 Tier 10 callout with "never used for synthesis" rule |
| 12 | NAVIGATION QUERY output format | §8.9 explicit format block with example |
| 13 | META-PROCESS inverse-grep | §8.10 Required reads step 3 + drift-scan verification |
| 14 | Investigation Log template promoted to P1 | §9.1 registry row + §9.3 P1 promotion + §17.2 row 6 |
| 15 | Ops Incident Report template as P1 | §9.1 registry row + §9.3 P1 addition + §17.2 row 7 |

**Not folded** (explicitly deferred with rationale):

- **DESIGN-PREP + ADR merge or hard boundary.** Rigby's ask.
  Folded partially via §5.1 "Class boundary notes" — hard
  boundary rule stated ("Design-Prep = Chris has not ratified;
  Design-Decision = a committed ADR file exists"). Full merge
  deferred until ADR corpus lands (§17.2 P1 item 5). If ADR
  corpus never materializes, the merge becomes the right call
  in a future OS version.
- **Router determinism vs "ASK CHRIS" fallback.** Rigby's ask
  was tightening classes to eliminate the fallback. Folded
  partially via §5.1 class-boundary rules (which resolve
  several ambiguous cases). Fully deterministic routing is a
  v2 OS goal — needs empirical evidence from 3+ research
  groups to see which classes actually get requested.

## 19.6 Post-fold verdict

**Draft is v1.1** (edits folded from Rigby SIGN-with-edits).
`verifier_loop` in frontmatter updated. Status remains `draft`
until Chris ratifies. Rigby SIGN status: **SIGN-with-edits
folded (15 must-fixes + 2 partial folds documented)**.

---

# Part 20 — S1278 Finalization and Ratification

## 20.1 What this section is

The closure section for the Research OS. S1278 is the final
architecture session before the OS transitions from **built**
to **used**. This section names the completeness assessment,
documentation ecosystem, graduation verdict, and Chris's
ratification decision. Additive only — no §1–§19 content
modified.

## 20.2 Fresh-Claude confusion audit (mission Part 1)

*"If I joined this repository tomorrow, what would still
confuse me?"* Concrete confusions still present at v2.1 close:

| Confusion | Blocking? | Fix location |
|-----------|-----------|--------------|
| CLAUDE.md doesn't reference the OS | **Blocking for discoverability** | §17 P0.1 + §18 P0.3 |
| START-HERE README doesn't reference research library | **Blocking for discoverability** | §17 P0.3 + §18 P0.4 |
| `OPEN_ARCS.md` doesn't exist yet | **Blocking for §6.6 reconciliation ritual** | §17 P0.1 + §18 P0.2 |
| ARCHITECTURE_INDEX §7 decision matrix buried at line ~1725 | Non-blocking (discoverable via OS §5 router) | §18 P0.5 |
| Playbook cross-refs in renumbered v1.1 content shifted by cascade | **Was blocking; fixed this session** (13 corrections) | Done S1278 |
| ADR corpus doesn't exist | Non-blocking (§5.1 boundary rule + §8.3 handling) | §17 P1.5 |
| Investigation Log template not formalized | Non-blocking (§8.5/§8.7 contracts suffice) | §17 P1.6 |
| Ops Incident Report template not formalized | Non-blocking (§8.11 covers) | §17 P1.7 |
| `pa_local.sh` self-check runtime helper | Non-blocking (MEMORY rule + §4.1 A9 gate) | §17 P1.9 |

**Blocking count: 3.** All three are documentation additions
that do NOT change the OS architecture. Fixable in a follow-up
migration session. See §20.11 for the checklist.

## 20.3 Missing architectural layer? (mission Part 3)

**Answer: No missing architectural layer.**

Chris's proposed stack (`Platform → Research Library → OS →
Context-Kit → Startup → Implementation`) is fully covered by
the §7 tier system:

- **Platform** → PLATFORM_INVENTORY + PLATFORM_WHAT_IT_IS +
  subsystem docs (Tiers 1a, 3, 7)
- **Research Library** → ARCHITECTURE_INDEX + playbook +
  `docs/research/` corpus (Tiers 4, 5)
- **Research OS** → this doc (Tier 4)
- **Context-Kit** → §2
- **Claude Startup** → §4
- **Implementation** → §8.4

Runtime state, verification, human ratification, Rigby SIGN
are **transversal axes**, not missing vertical layers. The
Employee OS runtime is a distinct product (not a docs layer).

## 20.4 Documentation Ecosystem Diagram (mission deliverable)

Canonical relationships across every documentation surface:

```
                     ┌───────────────────────────────────────┐
                     │        RUNTIME (Tier 0)               │
                     │  code + database + Redis + Celery     │
                     └────────────────┬──────────────────────┘
                                      │ generate
                                      ▼
                     ┌───────────────────────────────────────┐
                     │  GENERATED INVENTORIES (Tier 1a)      │
                     │  PLATFORM_INVENTORY.md · INDEX.md     │
                     └────────────────┬──────────────────────┘
                                      │ instrument
                                      ▼
                     ┌───────────────────────────────────────┐
                     │  MEASURED OPS SNAPSHOTS (Tier 1b)     │
                     │  ops digests · SLO snapshots          │
                     │  incident postmortems                 │
                     └────────────────┬──────────────────────┘
                                      │ govern
                                      ▼
                     ┌───────────────────────────────────────┐
                     │  GOVERNANCE (Tier 2)                  │
                     │  DOC_LIFECYCLE.md ·                   │
                     │  EMPLOYEE_OS_PRIMITIVES.md            │
                     └────────────────┬──────────────────────┘
                                      │ anchor
                                      ▼
                     ┌───────────────────────────────────────┐
                     │  NARRATIVE ANCHORS (Tier 3)           │
                     │  PLATFORM_WHAT_IT_IS.md               │
                     │  KNOWLEDGE_PIPELINE.md                │
                     │  EVENT_SYSTEM_INVENTORY.md            │
                     └────────────────┬──────────────────────┘
                                      │
                                      ▼
   ┌─────────────────────────────────────────────────────────────┐
   │              PROCESS FRAMEWORK (Tier 4)                      │
   │                                                              │
   │   CONTEXT-KIT (generic framework — SEPARATE REPO)            │
   │     ↓ specialized by                                         │
   │   RESEARCH OPERATING SYSTEM (this doc)                       │
   │     ↓ calls                                                  │
   │   DOMAIN_RESEARCH_PLAYBOOK v2 (§8.1 host)                    │
   │     ↓ navigates                                              │
   │   ARCHITECTURE_INDEX v11 (research library map)              │
   └─────────────────────────────────┬────────────────────────────┘
                                     │ registers
                                     ▼
              ┌────────────────────────────────────────┐
              │    RESEARCH LIBRARY (Tier 5)           │
              │                                        │
              │  docs/research/domains/<slug>/         │
              │    NN00 parent · NN01–NN98 children    │
              │    NN99 canonical summary              │
              │  Whole-platform arc: platform/         │
              │  Employee OS arc: legacy top-level     │
              └───────┬───────────────────────┬────────┘
                      │                       │
                      ▼                       ▼
      ┌────────────────────────┐  ┌──────────────────────────┐
      │  DESIGN PREPARATION    │  │  DESIGN DECISION (ADR)   │
      │  option selection ·    │  │  Chris ratifies          │
      │  schemas               │  │  docs/adr/ (future P1)   │
      └───────────┬────────────┘  └──────────┬───────────────┘
                  │                          │
                  └────────────┬─────────────┘
                               │ implements
                               ▼
              ┌───────────────────────────────────────┐
              │  IMPLEMENTATION (runtime PRs)         │
              │  §8.4 contract                        │
              └───────────────┬───────────────────────┘
                              │ verifies
                              ▼
              ┌───────────────────────────────────────┐
              │  VERIFICATION                         │
              │  tests · telemetry · verify_doc_claims │
              └───────────────┬───────────────────────┘
                              │ maintains
                              ▼
              ┌───────────────────────────────────────┐
              │  MAINTENANCE                          │
              │  §11 Documentation Ownership          │
              │  DOC-POINTER-V1/V2 banners            │
              └───────────────┬───────────────────────┘
                              │ preserves
                              ▼
              ┌───────────────────────────────────────┐
              │  HISTORICAL PRESERVATION              │
              │  docs/handoffs/ (Tier 9)              │
              │  docs/archive/ (Tier 10)              │
              │  never-delete rule                    │
              └───────────────────────────────────────┘


              ─── SIDE CHANNELS (always active) ───

  REPO STATE (transversal):
      00-START-NEXT-SESSION.md  (session state)
      OPEN_ARCS.md              (arc state — P0)
      latest handoff            (ship state)
      RESEARCH_DEBT.md          (debt state — P2)

  REFERENCE DOCS (transversal, Tier 6):
      docs/topics/*.md · docs/narratives/*.md · docs/*.md

  CLAUDE STARTUP:
      context-kit orient · CLAUDE.md · MEMORY.md
      → §4 Level A → §5 classification → §4.2 Level B

  RIGBY SIGN LAYER (per §8 contract):
      §15 stage table · fresh isolation pins
      grep-verify + pressure-test

  CHRIS RATIFICATION LAYER:
      §16 commit gate · §8.3 ADR ratification
      §20 evolution triggers
```

## 20.5 Knowledge lifecycle (mission Part 5)

**Answer: No new ledger needed.** The 5 knowledge lifecycle
events map cleanly to existing surfaces:

| Event | Existing surface |
|-------|------------------|
| **Created** | Research doc content + `session_added` frontmatter |
| **Modified** | `supersedes:` chain + `verifier_loop` append |
| **Invalidated** | DOC-POINTER-V1 drift banners + V2 supersession |
| **Deferred** | §14.6 future work + canonical summary follow-on queue |
| **Debt** | §15 Research Debt (7 categories, formula, escalation) |

The §14.1 close-checklist item 8 ("research debt logged")
implicitly covers the full knowledge delta. No architectural
change needed.

## 20.6 Research lifecycle completeness (mission Part 6)

Chris's proposed lifecycle
(`Research → Design Prep → Decision → Implementation →
Verification → Maintenance → Historical Preservation`) is
complete.

Only one genuinely-missing artifact: **Implementation Review**
template (§9.3 P2 today). Sits between Verification and
Maintenance: *"was the recommendation right? did implementation
solve the problem?"* Not blocking; formalize when the first
implementation review ships.

## 20.7 Quick Start doc? (mission Part 7)

**Answer: No.** The §0 TL;DR (30 lines) is the Quick Start.
Playbook §21 Short Start Commands covers research-class entry.
Adding another Quick Start creates a drift surface without
solving a real problem.

## 20.8 Graduation verdict (mission Part 8)

**Verdict: GRADUATED.**

- v1 → v1.1 → v2 → v2.1 iterations landed real improvements
  with slowing convergence.
- v2 SIGN-with-edits was folded (Medium confidence — on
  measurement details, not architecture).
- Every mission part has a concrete answer.
- Further sessions would produce more anti-patterns and more
  templates — but the ARCHITECTURE itself would not change.
- Diminishing returns has begun.

Further OS work should be **operational refinement**, not
architectural redesign.

## 20.9 Debt sort (mission Part 9)

Consolidated from S1276 introspection, OS v2 §17, playbook v2,
INDEX v10:

### P0 — Blockers before Group 1400

| # | Item | Status |
|---|------|--------|
| 1 | CLAUDE.md "Research Library" subsection + Startup checklist | Follow-up session (S1279+) |
| 2 | `OPEN_ARCS.md` created + initial content | Follow-up session |
| 3 | START-HERE README + INDEX pointers to research library | Follow-up session |
| 4 | ARCHITECTURE_INDEX v10 → v11: register OS §1.14 + introspection §1.15 + timeline rows | **This session** |
| 5 | Playbook §-ref cascade cleanup in OS | **Done this session (13 fixes)** |

### P1 — Should land soon (before Group 1500)

| # | Item |
|---|------|
| 6 | ADR corpus (`docs/adr/README.md` + first ADR template) |
| 7 | Investigation Log / Repro Notebook template |
| 8 | Ops Incident Report template |
| 9 | Playbook v3: fold OS §7 hierarchy + §11 ownership matrix references |
| 10 | ARCHITECTURE_INDEX §7 decision matrix promoted earlier |
| 11 | `pa_local.sh` self-check runtime helper (runtime work) |

### P2 — Nice to have

| # | Item |
|---|------|
| 12 | `docs/research/HISTORY.md` extraction |
| 13 | Research Question / Scoping Note template |
| 14 | Implementation Review template (formalizes §20.6 gap) |
| 15 | `docs/research/process/failure_modes.md` |
| 16 | `RESEARCH_DEBT.md` cross-arc manifest |

### Future

| # | Item |
|---|------|
| 17 | Promote OS patterns to Context-Kit (post 3-group threshold) |
| 18 | Automated OPEN_ARCS.md generation |
| 19 | Automated `verify_doc_claims` extension for OS claims |

## 20.10 Ratification recommendation (mission Part 10)

**Verdict: READY WITH MINOR FOLLOW-UP.**

Rationale:
- Architecture complete (§20.8 graduation).
- 3 blocking items remain (§20.9 P0.1–P0.3), all documentation
  migration (not architectural).
- P0.4 (INDEX bump) is being executed this session.
- P0.5 (playbook cross-refs) is done this session.
- P0.1–P0.3 are ~30 minutes of focused work in a follow-up
  session.

Once P0.1–P0.3 land, the OS is **CANONICAL**.

**What Chris ratifies at S1278 close:**
1. The OS architecture as documented (v2 + S1278 cleanup +
   §20 finalization).
2. The graduation verdict (§20.8).
3. The P0/P1/P2 debt sort (§20.9).
4. The next-session mandate: execute P0.1–P0.3, then open
   Group 1400.

## 20.11 Migration checklist for follow-up session

Docs-only work that lands P0.1–P0.3:

1. **CLAUDE.md.** "Research Library" subsection (~15 lines)
   pointing to OS + playbook + INDEX + OPEN_ARCS. "Startup
   checklist" subsection (~10 lines) with §4 Level A
   sequence.
2. **`docs/research/OPEN_ARCS.md`.** Create with §6.3 shape:
   in-progress row for Group 1300 (Memory), closed rows for
   pre-v1 arcs.
3. **`docs/00-START-HERE/README.md` + `INDEX.md`.** Add
   pointers to `docs/research/` + this OS.
4. **Verify.** Fresh Claude session discovers OS via CLAUDE.md
   pointer, discovers playbook via OS §8.1, discovers
   ARCHITECTURE_INDEX §7 without scavenger hunt.

One-session effort. No runtime changes.

## 20.12 Context-Kit boundary re-evaluation (mission secondary)

**Boundary is stable at v2.** No promotion candidates ready
for Context-Kit this session:

**Remain Donkey Betz specific** (unchanged):
- RESEARCH_OPERATING_SYSTEM.md
- DOMAIN_RESEARCH_PLAYBOOK.md
- ARCHITECTURE_INDEX.md
- All research library content
- CLAUDE.md · MEMORY.md feedback rules

**Candidates for Context-Kit promotion** (over time — needs
3+ research groups using them first):
- Research Contract pattern (§13)
- Completion Contract pattern (§14)
- Research Debt concept (§15)
- Parent-with-children arc shape (playbook §2)
- Fresh isolation pin default (playbook §15)

Promotion triggers post Groups 1300/1400/1500 usage.

## 20.13 Rigby SIGN — S1278 final ratification pressure-test

**Routed.** Fresh isolation pin `pa-30278fb65295e74c`. Narrow
scope per S1278 mission: final architectural recommendation
only, no redesign asked.

**Rigby confirmed** `service_context: local`.

**Verdict:**
- Overall confidence: **High**
- Is OS complete: **with-follow-up**
- Remaining issues blockers: **no** — *"blockers to 'canonical',
  not blockers to 'use'"*
- Diminishing returns reached: **yes**
- Graduate verdict correct: **yes**
- Ratification verdict correct: **yes**
- Factual errors to fix: **none**
- Final verdict: **SIGN-with-edits** — where "edits" =
  the three P0 doc-pointer follow-up items already flagged.

**Interpretation.** No architectural changes required. No
factual corrections. Rigby's "SIGN-with-edits" refers to the
follow-up migration session (P0.1–P0.3). That session is out
of scope for S1278.

**Rigby quote:** *"Land the three P0 doc-pointer fixes you
flagged as blocking 'canonical' status. No architecture
changes recommended; this is strictly to make the ratification
state factually true and discoverability-consistent."*

## 20.14 Session close

S1278 delivers:
1. Playbook cross-ref cleanup (13 fixes)
2. §20 finalization section (assessment, ecosystem diagram,
   graduation, P0/P1/P2 sort, ratification)
3. ARCHITECTURE_INDEX v11 registration (companion commit)
4. Single research-documentation commit (all above bundled)
5. Rigby SIGN-with-edits (follow-up scope only)

**No new architecture. No new contracts. No §1–§19
structural change.**

**Next session opens with:** *"Start migration session:
CLAUDE.md pointer + OPEN_ARCS.md + START-HERE."* That
executes §20.11, then Group 1400 opens per §12.3 target
rhythm.

---

# Appendix — Evidence Provenance + Verifier Notes

## A.1 Evidence base

Every claim in this doc is grounded in one of:

1. **Direct observation** of Claude Code's actual behavior at
   S1276 open + S1277 open (self-report).
2. **Grep audits** of CLAUDE.md, 00-START-NEXT-SESSION.md,
   START-HERE README/INDEX — cited via `docs/research/process/claude_research_startup_introspection.md`
   (S1276) Appendix.
3. **Playbook v2** — direct citation of §N sections.
4. **ARCHITECTURE_INDEX v10** — direct citation of §N sections.
5. **S1300 Memory Domain Scoping doc** — parent-with-children
   exemplar.
6. **S1276 introspection doc** — failure catalog + gap
   analysis.
7. **DOC_LIFECYCLE.md §2c** — inventory-wins-on-conflict rule.
8. **EMPLOYEE_OS_PRIMITIVES.md §4** — anti-duplication rule.
9. **Corpus tour** delivered in the same S1276/S1277 arc —
   real numbers (2,789 files, 862 handoffs, 1,388 archive).

Nothing in this doc is asserted without a cite, a direct
observation, or explicit UNKNOWN.

## A.2 What this doc does NOT verify

- Claims about what "runtime automation" would look like are
  speculative. Runtime work is out of scope; this doc names
  opportunities but does not verify feasibility.
- Long-term vision (§16.1) is aspirational, not observed. Cited
  as a target, not a claim about current state.
- Rigby SIGN verdict (§19.4) is pending at draft time.

## A.3 UNKNOWNs

- **Whether Chris ratifies the 10-class split.** Router
  taxonomy is proposed, not ratified. Chris may re-scope.
- **Whether OPEN_ARCS.md becomes runtime-generated or stays
  manual.** Proposed manual for MVP; runtime is P1.
- **Whether ADR corpus lands at `docs/adr/` or elsewhere.**
  Proposed location; not ratified.
- **Whether Symbol Mapping arc's canonical summary happens.**
  The arc predates the xx99 convention. Retroactive summary
  is optional.

## A.4 What must be true for this doc to be canonical

1. Chris SIGN.
2. Rigby SIGN folded (per §19).
3. P0 migration items (§18.1) either complete OR explicitly
   deferred with rationale.
4. INDEX §3.N row added.
5. Frontmatter `status: active` after Chris ratifies.

## A.5 What this doc supersedes

Nothing. This is v1 of a new document.

## A.6 What this doc anticipates being superseded by

- v2 evolution after 3+ research groups have exercised the OS
  (playbook §20 evolution-trigger rule).
- Runtime automation of currently-manual surfaces (OPEN_ARCS
  generation, pa_local.sh self-check) may reduce the OS's
  scope over time.

---

**Status.** OS v2.1 finalized (S1278). Playbook cross-ref
cascade cleanup applied. §20 finalization section added.
Awaiting Chris ratification for the commit.

**Verdict.** **READY WITH MINOR FOLLOW-UP** (§20.10). Three
docs-only P0 items (CLAUDE.md pointer, OPEN_ARCS.md,
START-HERE additions) land in a follow-up session; then OS
becomes **CANONICAL**.

**Next action.** Chris ratifies. Commit landing: OS v2.1 +
claude_research_startup_introspection.md +
ARCHITECTURE_INDEX v11 (§1.14 + §1.15 + timeline). Single
atomic commit per S1278 mission spec. Then PR merges.

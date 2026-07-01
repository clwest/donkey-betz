---
title: "Domain Research Playbook — canonical framework for every Donkey Betz architectural research group"
status: active
authority: process
version: v2
session_added: 1274
last_verified: 2026-07-01 (v2 — S1276)
companion_anchors:
  - docs/research/ARCHITECTURE_INDEX.md                # library navigation (v8+)
  - docs/research/platform_architecture_inventory.md   # 32-domain map (S1273)
  - docs/research/platform/cross_domain_integration_audit.md  # integration gaps (S1274)
  - docs/research/domains/memory/1300_memory_domain_scoping.md  # parent-with-children exemplar (S1300)
  - docs/PLATFORM_INVENTORY.md                          # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                         # narrative anchor
  - docs/EMPLOYEE_OS_PRIMITIVES.md                     # anti-duplication matrix
  - docs/00-START-HERE/DOC_LIFECYCLE.md                # doc governance
verifier_loop: |
  v2 (2026-07-01, S1276): playbook restructured into seven parts to
  formalize the methodology that emerged after v1 shipped. v1 codified
  what worked across S1268–S1274 for single-audit research groups.
  Between v1 (S1274 close) and v2 (S1276 open) two additional patterns
  proved themselves: (a) parent-with-children arc shape — S1300 Memory
  Domain Scoping made the pattern explicit; Chris locked it as the
  standard for multi-subsystem domains; (b) the research → design
  preparation → design decision → implementation phase separation —
  Symbol Mapping arc (§1.6 → §1.10 → §1.12 → §5.2e) proved this shape
  end-to-end. v2 adds fifteen formalized areas (§2 lifecycle, §3 phase
  separation, §4 numbering with xx99, §5 folder structure, §6 metadata
  standard, §7 cross-reference policy, §8 parent responsibilities, §10
  canonical summary responsibilities, §15 stage-scoped Rigby routing,
  §17 graduation criteria, §18 dependency mapping, §19 generalization
  requirements, §20 architecture evolution policy). v1 content
  preserved in place; §9 child audit checklist, §12 classifications,
  §13 sub-agent sweeps, §14 evidence rules, and §22 initial queue are
  unchanged. No routing to Rigby — this is process documentation, not
  a research finding (per §15's own rule for `authority: process`).
  v1 (2026-07-01, S1274): playbook drafted to codify the research
  methodology developed across S1268-S1274. No new methodology
  invented; playbook standardized what worked.
owner: claude (drafted S1274 v1; extended S1276 v2)
---

# Domain Research Playbook

> **What this is.** The canonical process framework for every future
> Donkey Betz architectural research group. It codifies the
> methodology developed across Sessions 1268–1276 so a fresh Claude
> Code session can start a domain research arc from a short
> instruction like *"Start Group 1400: Revenue"* without a
> 4,000-word prompt.
>
> **What this is not.** A domain audit itself. A rewrite proposal. A
> methodology innovation. Everything here is what has already
> worked; the playbook makes it repeatable and defends it against
> drift.
>
> **How to use.** When Chris says *"Start research group NNNN: X"*
> (see §21), Claude reads this playbook first, then executes the
> standard mission shape without further prompting.
>
> **Structural note (v2 additions).** v2 formalizes: the
> parent-with-children arc shape (§2, §8), the xx99 canonical
> summary convention (§4, §10), the research → design →
> implementation phase discipline (§3), the metadata standard (§6),
> cross-reference policy (§7), stage-scoped Rigby routing (§15),
> graduation criteria (§17), dependency mapping (§18),
> generalization requirements (§19), and the framework's own
> evolution policy (§20).

---

## Table of Contents

- **Part 1: Purpose & Lifecycle**
  - §1. Purpose
  - §2. Research Group Lifecycle
  - §3. Research vs Design vs Implementation — Phase Discipline
- **Part 2: Structural Standards**
  - §4. Session Numbering Convention
  - §5. Research Folder Structure
  - §6. Research Group Metadata Standard
  - §7. Cross-Reference Policy
- **Part 3: Document Responsibilities**
  - §8. Parent Document Responsibilities
  - §9. Child Audit Requirements (28 canonical questions)
  - §10. Canonical Summary Responsibilities
  - §11. Standard Document Templates
- **Part 4: Execution Standards**
  - §12. Classification Rules
  - §13. Standard Explore-Agent Sweeps
  - §14. Standard Evidence Rules
- **Part 5: Review & Governance**
  - §15. Rigby Review Policy — Per Stage
  - §16. Commit Policy — Draft → Canonical
  - §17. Graduation Criteria
- **Part 6: Framework Discipline**
  - §18. Domain Dependency Mapping
  - §19. Generalization Requirements
  - §20. Architecture Evolution Policy
- **Part 7: Application**
  - §21. Short Start Commands
  - §22. Initial Domain Queue
  - §23. Relationship to Existing Research
  - §24. Final Self-Check

---

# Part 1 — Purpose & Lifecycle

## 1. Purpose

This playbook standardizes deep domain audits across Donkey Betz.
The platform has 32 documented architectural domains (per
`docs/research/platform_architecture_inventory.md` §2). Most are
under-researched. Every domain deserves at least one focused audit
before decisions get made about it — before extraction is
proposed, before enforcement is added, before wiring is changed.

The methodology proven across S1268–S1275:

1. **Read first.** Load the domain's existing docs + research
   library + parent inventory row before touching code.
2. **Decide arc shape.** Single audit or parent-with-children?
   (See §2 lifecycle for the decision procedure.)
3. **Sweep with parallel Explore sub-agents.** Six parallel
   sub-agents per child audit (see §13).
4. **Synthesize into one document per stage.** Follow the
   templates in §11.
5. **Verifier loop.** Every claim gets a file:line cite or an
   explicit `UNKNOWN` / `SPECULATIVE` (see §14).
6. **Rigby SIGN review.** Independent pressure-test on a fresh
   isolation pin (see §15).
7. **Fold edits.** SIGN-with-edits verdicts fold into the doc
   before it's considered publishable.
8. **Chris gates commits.** Nothing lands in `main` without
   Chris's explicit "commit it" instruction (see §16).
9. **Close the arc with a canonical summary.** For
   parent-with-children arcs, an `xx99` session produces the
   cross-cutting synthesis (see §10).
10. **Update the index.** ARCHITECTURE_INDEX version bumps on
    every commit (see §16).

The playbook exists because this loop is expensive to re-derive
each session. Chris typed roughly 4,000 words for S1273 and
S1274 combined. The v1 playbook shrunk future starts to eight
words. The v2 additions make the arc closable — Chris can now
say *"Close research group 1300"* and get the canonical summary.

---

## 2. Research Group Lifecycle

Every research group follows the same five-stage lifecycle. The
shape is fixed; only the number of children varies.

```
        ┌───────────────────────────────────────────┐
        │  STAGE 0 — Parent Scoping (xx00)          │
        │  Decide: single-audit vs parent-with-     │
        │  children. Lock child slots. Delegate     │
        │  cross-arc subdomains. Define anti-scope. │
        └────────────────────┬──────────────────────┘
                             │
                             ▼
        ┌───────────────────────────────────────────┐
        │  STAGE 1 — Child Audits (xx01 … xx98)     │
        │  One session per child; 6 parallel        │
        │  Explore sub-agents; 20-section audit;    │
        │  Rigby SIGN; Chris commit gate.           │
        │  Iterate over locked slots in order       │
        │  (or Chris re-sequences between).         │
        └────────────────────┬──────────────────────┘
                             │
                             ▼
        ┌───────────────────────────────────────────┐
        │  STAGE 2 — Canonical Summary (xx99)       │
        │  Cross-cutting synthesis. Consolidated    │
        │  domain shape. Anchor-update              │
        │  recommendations. Follow-on queue.        │
        │  Cross-links to delegated arcs. NOT a     │
        │  re-audit.                                │
        └────────────────────┬──────────────────────┘
                             │
                             ▼
        ┌───────────────────────────────────────────┐
        │  STAGE 3 — Architecture Index Update      │
        │  §1.N rows registered; §8 timeline row;   │
        │  §3 domain map bumped; §5 gap entries     │
        │  closed/opened; §9 roadmap advanced.      │
        └────────────────────┬──────────────────────┘
                             │
                             ▼
        ┌───────────────────────────────────────────┐
        │  STAGE 4 — Research Group Complete        │
        │  Graduation criteria met (§17). Group     │
        │  transitions from `in-progress` to        │
        │  `closed`. Follow-on queue lives on;      │
        │  the arc itself is done.                  │
        └───────────────────────────────────────────┘
```

**Why each stage exists.**

- **STAGE 0 (parent)** protects against scoping errors. Without
  it, single-domain missions balloon into multi-subsystem work
  (or, worse, collapse three inventory rows into one and lose
  fidelity). S1300 Memory made the parent stage explicit after
  Chris caught the "one memory or many?" ambiguity in the
  a-f scope card.
- **STAGE 1 (children)** is where the work happens. One session
  per child keeps each audit tractable and Rigby's SIGN review
  focused on a bounded surface.
- **STAGE 2 (canonical summary)** prevents the arc from ending
  in mid-air. Without it, the last child audit closes the last
  slot but no synthesized cross-cutting picture exists — future
  readers have to reassemble it themselves.
- **STAGE 3 (index update)** keeps the library navigable.
  Unregistered docs become invisible.
- **STAGE 4 (complete)** is a hard graduation, not a fade-out.
  §17 defines the objective criteria.

**Single-audit arcs skip STAGE 0 and STAGE 2.** A domain that
genuinely fits one audit runs STAGE 1 (one session), STAGE 3,
STAGE 4. Most of the S1268–S1275 arc predates the parent shape
(S1269 governance, S1270 symbol mapping, S1271 actor identity,
S1272 authority enforcement design space) — each was a
single-audit group. That is legitimate; the playbook accommodates
both shapes.

**Deciding shape at STAGE 0.** Use the parent-vs-single verdict
procedure in §8. Default to parent-with-children when any of the
following holds:

- The domain maps to 2+ rows in `platform_architecture_inventory.md`
  §3 (S1273 32-domain map).
- The S1273 §5 duplicate/overlap section already flags the
  domain as a multi-store or multi-substrate concern.
- The domain has a subsystem with NO inventory row of its own
  (child audit will add the row).
- Two or more of the 28 audit questions in §9 clearly need
  independent evidence gathering to answer well.

Otherwise default to single-audit.

**Arc rhythm.** The S1268–S1275 rhythm was one substantive
research doc per session. Parent-with-children arcs preserve that
rhythm: parent + N children + canonical summary = N + 2
sessions. The S1300 Memory arc is planned at 7 sessions (parent
+ 5 children + xx99). The Employee OS arc was 8 sessions across
6 group ranges — legitimate, because pre-v1 the pattern was
implicit.

---

## 3. Research vs Design vs Implementation — Phase Discipline

Research, design, and implementation are three distinct phases.
They must not mix in a single document. The `authority`
frontmatter field distinguishes them:

| Phase | `authority:` value | Purpose | Chris gate? |
|-------|-------------------|---------|-------------|
| **Research** | `research` | Discover what exists / what fails / what is missing. Enumerate options; do not pick. | Approves scope; ratifies findings |
| **Research (parent)** | `parent-doc` | Scope a research group. Decide arc shape. Lock child slots. | Locks child sequence + anti-scope |
| **Design Preparation** | `design-preparation` | Take research + inventory as input; produce an evidence-based recommendation with tradeoffs. May carry a specific option, schema, or field spec. Still Chris-gated before implementation. | Ratifies recommendation |
| **Design Decision** | `design-decision` | Chris ratifies a specific choice; produces an ADR (architecture decision record). | Yes — the point of the phase |
| **Process** | `process` | Rules for other docs. This playbook. | Yes — version bump |
| **Navigation** | `navigation` | ARCHITECTURE_INDEX.md and similar. | Not per-update |
| **Implementation** | (out of library) | Runtime PR. Lives in the codebase, cited by research/design docs. | Standard PR gate |

**The four-phase Symbol Mapping arc as canonical exemplar:**

```
   S1270 §1.6  Symbol Mapping Architecture         [authority: research]
                (enumerate 5 options neutrally)
                          │
                          ▼
   S1274 §1.10 Symbol Mapping Option Selection     [authority: design-preparation]
                (recommend Option E as v0)
                          │
                          ▼
   S1275 §1.12 Symbol Mapping Event Schema Design  [authority: design-preparation]
                (pin schema + emitters + confidence enum)
                          │
                          ▼
   S1276+     Symbol Mapping v0 Implementation     [runtime PRs]
                (P0–P5 rollout per §1.12 §15)
```

**Rules.**

1. Research docs enumerate; they do not recommend. If a research
   doc catches itself recommending, split — the recommendation
   becomes a separate `design-preparation` doc.
2. Design preparation docs recommend; they do not decide. Chris
   is the only ratifying voice. If a `design-preparation` doc
   catches itself asserting a decision, downgrade language to
   *"Recommendation:"* and note the Chris gate explicitly.
3. Design decisions produce ADRs. Not part of the research
   library today; live under `docs/adr/` or `docs/decisions/`
   (out of scope for this playbook; framework accommodates the
   future).
4. Implementation lives in the codebase. Research/design docs
   cite runtime PRs by number after the fact; they never contain
   implementation code.
5. **Never mix phases within one document.** A research doc
   that ends with a recommendation is a category error — either
   the recommendation is unwarranted (drop it), or it deserves
   its own doc (split).
6. **Phase transitions are visible.** When a research group
   advances from `research` to `design-preparation`, the
   ARCHITECTURE_INDEX §1.N row records both docs and their
   relationship. Do not delete the prior research doc — it
   remains the evidence base.

**Anti-pattern to avoid.** A single "audit" doc that inventories
the domain AND recommends the design AND sketches the migration.
That doc will be wrong at three levels. Split it into
research + design-preparation + (future) implementation-PR.

---

# Part 2 — Structural Standards

## 4. Session Numbering Convention

Session IDs are grouped into planning ranges. **The ranges are
labels for what the research is about — not runtime identifiers,
not code enforcement, not project keys.** They exist so the
research library's timeline (`ARCHITECTURE_INDEX.md` §8) reads as
a coherent narrative.

| Range | Theme | Rationale |
|---|---|---|
| **1200s** | Employee OS / Authority / Platform inventory foundation | Sessions 1268–1275: 8 research docs + integration audit + playbook. Foundation. |
| **1300s** | Memory / Knowledge / Embeddings | S1300 parent locked 2026-07-01; children S1301–S1305 + canonical summary S1399. |
| **1400s** | Revenue / Outreach / Engagement | Rigby-caught missed domain from S1273 SIGN; highest business-value under-researched domain. |
| **1500s** | Sports / DBAO / Intelligence | Structural question: island vs integrated (S1274 §12.3). |
| **1600s** | Content / Deliverables / Publishing | Well-inventoried but integration analysis needed (S1274 §5.3, §7.4). |
| **1700s** | Observability / Telemetry / SLOs | 5-layer execution telemetry dedup audit named by S1273 §5.13 + S1274 §12.6. |
| **1800s** | HumanAttention / Feedback / Learning | Only round-trip learning loop today (S1274 §2.5); ripe for scope expansion. |
| **1900s** | Event / Integration / Runtime Architecture | Downstream of S1274 §12.1 EventBus Adoption + Contract Verification. |
| **2000s+** | Reserved for future domains not yet identified | Free slots — Chris allocates when a new domain surfaces. |

### The intra-range structure

Within any research group range `NN00`–`NN99`:

| Session ID | Role |
|-----------|------|
| **NN00** | **Parent scoping session** — required for parent-with-children arcs; skipped for single-audit arcs. Produces `<slug>_domain_scoping.md`. |
| **NN01 … NN98** | **Child audit sessions** — one audit per session. Ordered by parent's locked P1–P? sequence. Produces `<session_id>_<slug>_<child_topic>_audit.md`. |
| **NN99** | **Canonical summary session** — required for parent-with-children arcs; skipped for single-audit arcs. Produces `<session_id>_<slug>_canonical_summary.md`. |

### Why the xx99 buffer exists

The 98-slot buffer between parent and canonical summary is
deliberate. Real research groups fit inside it comfortably:

- S1300 Memory planned at 5 child slots (S1301–S1305) → 93 free
  slots for follow-up, extension, or side missions.
- Even the Employee OS arc (which spanned 5 sessions across
  multiple ranges pre-v1) would fit in a single range's buffer
  with room to spare.

The `NN99` slot is reserved specifically so a fresh Claude Code
can always know where the canonical summary lives: *last two
digits are `99`*. Do not deviate.

### Rules for numbering

1. A "research group" is a set of related audits, not a single
   session. Group 1300 spans S1300–S1305 + S1399.
2. The first session in a group is the group's parent audit (for
   arcs) or the sole audit (for single-audit groups).
3. Session IDs are assigned in mission order, not calendar order.
   If mission S1302 depends on findings from S1301, S1302 runs
   after S1301 completes, even if calendar days pass between.
4. If the domain is bigger than expected, splitting into
   sub-groups is fine. Do not force a single session to cover a
   multi-subsystem domain (see §2 STAGE 0 verdict procedure).
5. If a research group needs more than 98 child slots, promote it
   to a multi-range arc. This has never happened; treat as
   theoretical.
6. Ranges are targets, not caps. Group 1300 could bleed into the
   1400 range only if Chris explicitly re-allocates. Default is
   to stay within range.

---

## 5. Research Folder Structure

The canonical layout scales as new domains are added:

```
docs/research/
├── ARCHITECTURE_INDEX.md                         # navigation, versioned
├── DOMAIN_RESEARCH_PLAYBOOK.md                   # this doc, versioned
│
├── platform/                                     # whole-platform-scope research
│   ├── platform_architecture_inventory.md        # S1273 (32-domain map)
│   └── cross_domain_integration_audit.md         # S1274 (integration lens)
│
├── domains/                                      # per-domain deep research
│   ├── memory/
│   │   ├── 1300_memory_domain_scoping.md         # parent (P0)
│   │   ├── 1301_memory_rag_retrieval_lanes_audit.md   # child P1
│   │   ├── 1302_memory_persistence_architecture_audit.md   # child P2
│   │   ├── 1303_memory_conversational_thread_audit.md  # child P3
│   │   ├── 1304_memory_docs_rag_boundary_audit.md  # child P4
│   │   ├── 1305_memory_runtime_correctness_audit.md  # child P5
│   │   └── 1399_memory_canonical_summary.md      # canonical summary
│   ├── revenue/
│   │   └── ...                                   # populates as Group 1400 runs
│   ├── sports/
│   │   └── ...                                   # populates as Group 1500 runs
│   ├── content/
│   ├── observability/
│   ├── human-attention/
│   └── event-architecture/
│
└── (legacy S1268-S1272 docs)                     # top-level for now
    ├── employee_os_communication_substrate_audit.md
    ├── employee_os_communication_protocol_sketch.md
    ├── employee_os_collaboration_patterns.md
    ├── governance_authority_evolution.md
    ├── symbol_mapping_architecture.md
    ├── actor_identity_attribution_architecture.md
    ├── authority_enforcement_design_space.md
    ├── symbol_mapping_option_selection_design.md
    └── symbol_mapping_event_schema_design.md
```

### Rules

1. **Domain subdirectory required.** Every research group with a
   dedicated domain gets its own `docs/research/domains/<slug>/`
   directory. Create it as part of STAGE 0; do not batch
   directory creation into a separate PR.
2. **Platform-scope docs live in `docs/research/platform/`.**
   Only whole-platform inventories or cross-domain audits belong
   here. Single-domain research goes under `domains/<slug>/`.
3. **Legacy docs are grandfathered.** The S1268–S1275 docs
   currently live at `docs/research/` top-level. They do not need
   to be relocated to `domains/<slug>/`. Future extensions of
   those docs land under their canonical domain slug (e.g., a
   future symbol mapping doc goes under `domains/authority/` or
   `domains/symbol-mapping/`).
4. **Domain slug rules.** Lower-case, single word or
   hyphen-joined. Match the S1273 domain name where possible.
   Preferred slugs for the initial queue: `memory`, `revenue`,
   `sports`, `content`, `observability`, `human-attention`,
   `event-architecture`.
5. **File naming.** `<session_id>_<slug>_<optional_child_topic>_<type>.md`
   where `<type>` ∈ {`domain_scoping`, `audit`, `canonical_summary`}.
   Session ID is a numeric prefix, not a version. If a follow-up
   session extends an audit, it creates a new file with its own
   session ID; the new file adds a `## 0. Supersedes` header
   referencing the prior file. Do not overwrite prior files.
6. **Non-research files stay out.** ARCHITECTURE_INDEX.md and
   this playbook are the only non-research files in
   `docs/research/`. Design decision records (ADRs) live
   elsewhere (`docs/adr/` if that convention is adopted).
   Implementation plans do NOT live in `docs/research/`.

---

## 6. Research Group Metadata Standard

Every research doc carries YAML frontmatter that makes the group
self-describing. Fresh Claude Code can reconstruct the arc's
state, dependencies, and history from frontmatter alone.

### Canonical frontmatter template

```yaml
---
title: "<Domain Name> — <Doc Purpose>"
status: draft | active | superseded | archived
authority: research | parent-doc | design-preparation | design-decision | process | navigation
version: v1 | v2 | ...            # process/navigation docs only
session_added: NNNN
research_group: NNNN              # required for arcs; the parent's session_id
child_slot: P0 | P1 | ... | canonical-summary   # arcs only
domain_slug: memory | revenue | ...             # domain-scoped docs only
date: YYYY-MM-DD                  # doc first drafted
last_verified: YYYY-MM-DD         # last time content was reviewed against reality
supersedes: none | <path>         # prior doc that this one replaces
related:
  - <path>                        # peer docs in the same arc or dependency chain
companion_anchors:
  - <path>                        # load-bearing anchors this doc grounds itself in
dependencies_on:                  # research groups whose findings this group inherits
  - group: NNNN
    slug: <domain_slug>
    role: <how it's used>
delegates_to:                     # subdomains this group hands off to another arc
  - group: NNNN
    slug: <domain_slug>
    scope: <what is delegated>
delegated_from:                   # subdomains this group inherits from another arc
  - group: NNNN
    slug: <domain_slug>
    scope: <what is inherited>
verifier_loop: |
  <multiline description of how evidence was gathered, what was
  verified, what Rigby SIGN status is, what edits were folded>
owner: claude | rigby-and-claude | <specific handoff>
---
```

### Required fields by doc type

| Field | Parent (P0) | Child audit (P1–P?) | Canonical summary (NN99) | Process (this playbook) | Navigation (INDEX) |
|-------|-------------|---------------------|-------------------------|-------------------------|---------------------|
| `title` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `status` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `authority` | ✓ (`parent-doc`) | ✓ (`research`) | ✓ (`research`) | ✓ (`process`) | ✓ (`navigation`) |
| `version` | — | — | — | ✓ | ✓ |
| `session_added` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `research_group` | ✓ | ✓ | ✓ | — | — |
| `child_slot` | ✓ (`P0`) | ✓ (`P1`–`P?`) | ✓ (`canonical-summary`) | — | — |
| `domain_slug` | ✓ | ✓ | ✓ | — | — |
| `date` | ✓ | ✓ | ✓ | — | — |
| `last_verified` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `supersedes` | ✓ (usually `none`) | ✓ (usually `none`) | ✓ | — | — |
| `related` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `companion_anchors` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `dependencies_on` | ✓ | If applicable | ✓ | — | — |
| `delegates_to` | ✓ (from anti-scope) | If applicable | ✓ | — | — |
| `delegated_from` | If applicable | If applicable | ✓ | — | — |
| `verifier_loop` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `owner` | ✓ | ✓ | ✓ | ✓ | ✓ |

### Status lifecycle

| Value | Meaning |
|-------|---------|
| `draft` | Content complete or in progress; not yet Chris-ratified. Uncommitted or committed but not canonical. |
| `active` | Chris-ratified; canonical for its scope. |
| `superseded` | Replaced by a newer doc; kept for provenance. `supersedes:` in the newer doc names this one. |
| `archived` | Historical only; content no longer accurate. Do not delete; note the archival reason in a top-of-file callout. |

### `verifier_loop` field discipline

`verifier_loop` is the load-bearing accountability field. It
must include (at minimum):

- Version and date the current content reflects.
- What evidence-gathering method was used (parallel Explore
  sub-agents count, sweep scope, sample size for spot-checks).
- Rigby SIGN status: `not routed` / `SIGN-clean` /
  `SIGN-with-edits (N folded)` / `NEEDS-MORE (unresolved)`.
- Which edits were folded and why (for SIGN-with-edits).
- Prior version notes preserved when the doc has evolved.

Truncating or overwriting prior `verifier_loop` history is
forbidden. The field is append-only.

---

## 7. Cross-Reference Policy

Docs reference each other constantly. The policy prevents
duplication and drift.

### Rules

1. **Cite runtime counts to `PLATFORM_INVENTORY.md`.** Every
   count claim (agents, tools, tasks, models) must cite the
   inventory autoblock — never a hand-written narrative. When
   inventory disagrees with any other doc, inventory wins per
   `DOC_LIFECYCLE.md` §2c.
2. **Cite code by file:line.** Load-bearing claims that could
   affect a downstream decision must include a `path:line`
   citation. Do not paraphrase code without a cite.
3. **Cite research findings by §N.M.** When referencing prior
   research, cite the specific section — e.g., *"per S1273 §3.13
   §5.4"* not *"per the S1273 audit."* This keeps references
   surgical and lets readers jump directly to the evidence.
4. **Cite other groups via ARCHITECTURE_INDEX §1.N.** For
   cross-arc references, cite the index row rather than the raw
   file path — the index row lists purpose, status, and
   dependencies without forcing a full file open.
5. **Never duplicate content.** If a fact is already in
   `PLATFORM_INVENTORY.md` §3.13, quote or paraphrase with a
   cite. Do not restate. Duplicated content drifts.
6. **Companion anchors declare load-bearing dependencies.** The
   `companion_anchors:` frontmatter field lists docs the current
   doc grounds itself in. Reading the current doc without
   reading the companion anchors first will produce
   misunderstanding.
7. **Related links declare peer connections.** The `related:`
   field lists sibling docs in the same arc or dependency chain.
   These are useful-to-read but not required-to-read.
8. **Cross-arc references use `dependencies_on` / `delegates_to`
   / `delegated_from`.** These frontmatter fields formalize the
   inter-group relationships that `related:` cannot express
   structurally. See §18 for the dependency mapping semantics.
9. **Parent registers all children.** Every parent's `related:`
   field lists all locked child slots (even before the child
   sessions run). Every child's `related:` field cites its
   parent's session_id.
10. **Canonical summary registers everything.** The `xx99`
    summary lists all children, the parent, the cross-arc
    delegations, and the follow-on queue. It is the arc's
    single-page index.

### Anti-pattern to avoid

**Copy-paste of inventory rows into a research doc.** If a
research doc copies §3.13 from `platform_architecture_inventory.md`
verbatim, the copy will go stale the moment the inventory
regenerates. Always reference, never restate. If the reader needs
the row visible, quote a single line with a cite arrow: *"§3.13
Memory / Knowledge / Embeddings — DEEP coverage / STABLE core +
PARTIAL edges (see `platform_architecture_inventory.md:1073`)."*

---

# Part 3 — Document Responsibilities

## 8. Parent Document Responsibilities

The parent document (session `NN00`) opens the research group
and defines its scope. It is the arc's charter.

### What belongs INSIDE the parent

1. **Domain purpose.** One-sentence definition of what the
   research group is about.
2. **Why Phase 0 was needed.** The scoping question that
   triggered the parent doc (e.g., "is Memory one domain or
   several?").
3. **Existing inventory evidence.** Cite the S1273 domain rows
   that map to this group. Do not re-inventory — reference.
4. **Candidate subdomain taxonomy.** Categories A / B / C / … of
   the domain, each with:
   - Primary systems in scope
   - Anchor to S1273 §3.N row (if any)
   - Known drift already flagged
   - Explicit "not covered by any S1273 row" call-out if adding
     a new inventory row is needed
5. **Parent-vs-single verdict.** With evidence for both
   directions. Explicit "verdict:" line.
6. **Locked child mission sequence.** Table of P0–P? slots with:
   - Session ID (planned)
   - Child audit title
   - Priority rationale
   - Category letters mapped
7. **Canonical summary slot.** Explicit `xx99` reservation with
   the summary's expected deliverables.
8. **Cross-arc delegations.** Subdomains handed off to other
   research groups. Explicit `delegates_to:` frontmatter entry
   and prose rationale.
9. **Anti-scope.** What is out of Group NNNN even under the
   parent shape. Prevents scope creep into adjacent domains.
10. **Recorded decisions.** Numbered table of Chris-locked
    decisions with date recorded, so future sessions can trace
    the arc's history.
11. **Open decisions still needed.** Non-blocking questions
    Chris needs to answer before specific child missions launch.
12. **Anchor-update recommendations queued for canonical
    summary.** If child audits will likely propose changes to
    `PLATFORM_INVENTORY.md` §3, name the candidates so the
    canonical summary doesn't have to rediscover them.

### What does NOT belong in the parent

- **The audits themselves.** Children own the audits.
- **Answers to the 28 audit questions (§9).** Those go in
  children.
- **Design proposals.** Parent is `authority: parent-doc`, not
  `design-preparation`.
- **Implementation plans.** Runtime code decisions belong to
  later PRs.
- **Deep evidence sweeps.** Six-parallel-Explore sweeps run per
  child, not per parent. Parent doc does taxonomy work only.
- **Recommendations about how the domain should work.** Parent
  is scoping, not designing.

### Parent document exemplar

`docs/research/domains/memory/1300_memory_domain_scoping.md`
(S1300, Chris-locked 2026-07-01) is the canonical exemplar. Use
its structure as the template for future parents:

- §1 Why Phase 0
- §2 What existing inventory already tells us
- §3 Candidate subdomain taxonomy (with categories A–H)
- §4 Parent-vs-single recommendation
- §5 Child mission sequence (Chris-locked)
- §6 Parked candidate issues (for future child audits)
- §7 Anti-scope
- §8 Decisions recorded (Chris-locked)
- §9 Next step

### When to skip the parent

Single-audit research groups skip the parent entirely and run
one audit at session `NN00`. Legitimate skip criteria:

- Domain maps to exactly one S1273 §3.N row.
- No overlap flags in S1273 §5 touch this domain.
- All 28 audit questions can be answered from one evidence sweep.
- Chris explicitly says *"single audit"* at open.

Any doubt → parent shape. Cheap to write; safe default.

---

## 9. Child Audit Requirements

Every child audit answers the same 28 canonical questions. Some
questions may be answered `UNKNOWN` or `not applicable` — that is
acceptable per §14. Every question requires either a file:line
cite, a documented reference, or an honest `UNKNOWN`.

### The 28 canonical questions

1. What is this domain for? *(one-sentence purpose)*
2. What problem does it solve? *(the business or platform
   problem, distinct from #1)*
3. What are the canonical entry points? *(files, URLs, PA tools,
   management commands)*
4. What are the major models? *(with file:line)*
5. What are the major services? *(with file:line)*
6. What are the major APIs? *(REST, WebSocket, PA tools)*
7. What are the major Celery tasks? *(with beat schedule if
   applicable)*
8. What are the major management commands? *(with file:line)*
9. What are the major runtime flows? *(sequence diagrams or
   step-by-step)*
10. What existing documentation exists? *(topic docs, handoffs,
    narratives)*
11. What research already exists? *(research library entries in
    ARCHITECTURE_INDEX §1)*
12. What is the architecture maturity? *(§12 classification)*
13. What is the research coverage? *(§12 classification)*
14. What integrations does it have? *(with which of the 32
    domains — reference S1273 §2)*
15. What integrations are missing? *(reference S1274 §3 gaps)*
16. What data does it own? *(models exclusive to this domain)*
17. What data does it consume? *(from other domains)*
18. What data does it produce? *(for other domains)*
19. What events does it emit? *(with file:line producers)*
20. What events should it emit? *(gaps — reference S1274 §6)*
21. What other domains depend on it? *(inbound consumers)*
22. What domains does it depend on? *(outbound dependencies)*
23. What models overlap with other domains? *(reference S1274 §5
    duplicate/overlap analysis)*
24. What services violate boundaries? *(reference S1274 §7
    boundary violations)*
25. What ownership is unclear? *(reference S1274 §10)*
26. What is technical debt? *(with severity per §12)*
27. What is drift? *(with evidence)*
28. What should be researched next? *(recommended follow-on
    missions, not implementation plans)*

**Ordering rationale.** Questions 1–2 set frame. 3–9 inventory
what exists. 10–13 assess research state. 14–22 handle
integration lens (the S1274 discipline). 23–27 identify problems.
28 opens the next mission.

### Anti-duplication rule for child audits

If a sibling child audit already answered question N for its
scope, the current child cites the sibling and moves on. Do not
re-answer for overlapping surface area. Example: if child P1
(Memory RAG Retrieval Lanes) already inventoried the
`DocumentEmbedding` model, child P2 (Memory Persistence
Architecture) cites P1 §4 rather than restating.

The canonical summary (`xx99`) is responsible for reconciling
answers that legitimately differ across children (e.g., P1 rated
maturity `PARTIAL` while P4 rated the same surface `STABLE` from
a different viewpoint).

---

## 10. Canonical Summary Responsibilities

The canonical summary (session `NN99`) closes the arc. It is
required for parent-with-children groups; skipped for
single-audit groups.

### What belongs INSIDE the canonical summary

1. **Cross-cutting patterns.** Findings that recur across
   children (e.g., "provenance-filter drift class appears in
   P1, P4, and P5"). The summary is the first place these
   patterns become visible.
2. **Consolidated domain shape.** A single map showing all
   subdomains, their durability tier, ownership, integration
   points. This is what a fresh reader needs to understand the
   whole domain at a glance.
3. **Resolved contradictions.** Where children disagreed on
   maturity, ownership, or classification, the summary picks the
   canonical answer and notes why.
4. **Unresolved unknowns.** Explicit list of what the arc did
   not answer, promoted to the follow-on queue.
5. **Anchor-update recommendations.** Specific proposed edits to
   `PLATFORM_INVENTORY.md` §3 (subdivision, consolidation, new
   rows), `PLATFORM_WHAT_IT_IS.md` (narrative additions),
   `ARCHITECTURE_INDEX.md` (§1.N registrations for each child +
   canonical summary itself, plus §3 domain map + §5 gap + §7
   decision matrix + §9 roadmap edits).
6. **Follow-on research queue.** What deserves later attention.
   Ranked by architectural uncertainty × risk × unblocked flows.
7. **Cross-links to delegated arcs.** Subdomains the parent
   delegated to other research groups. Cite the delegated arc's
   parent (or planned parent) so future readers can trace the
   full picture.
8. **Change log of the arc.** Which children shipped, in what
   order, what Rigby SIGN verdict each carried, what edits were
   folded. This becomes the arc's provenance record.

### What does NOT belong in the canonical summary

- **Another audit.** Children own the audits. Summary
  synthesizes, does not re-enumerate.
- **New evidence sweeps.** The summary consumes child outputs;
  it does not launch new Explore sub-agents.
- **Recommendations that require child-level detail.** Those
  belong in a follow-on child audit or a design-preparation
  doc.
- **Implementation plans.** Runtime work is not the summary's
  job.
- **Design decisions.** Summary is `authority: research`, not
  `design-preparation` or `design-decision`.

### Rationale for the xx99 slot

Without a canonical summary, arcs end in mid-air. The last child
audit closes the last locked slot but no cross-cutting picture
exists — future readers have to reassemble the arc from
individual child docs, which is expensive and error-prone.

The `xx99` slot is bounded work: it consumes P1–P? outputs, it
does not re-open scope. Estimated size: half the length of a
child audit. Runtime: one session.

### Canonical summary template outline

See §11.3 for the full template. Executive summary + 8 major
sections + appendix.

---

## 11. Standard Document Templates

Three templates: parent, child audit, canonical summary. Section
headings are exact — do not rename. Section order is fixed. If a
section has no findings, keep the heading and note the reason.

### 11.1 Parent document template

```markdown
# <Domain Name> Domain Taxonomy Proposal (Phase 0)

## 1. Why Phase 0
## 2. What existing inventory already tells us
## 3. Candidate subdomain taxonomy
   ### A — <Subdomain 1>
   ### B — <Subdomain 2>
   ...
   ### Explicit non-candidates
## 4. Parent-vs-single recommendation
## 5. Child mission sequence (Chris-locked <date>)
## 6. Parked candidate issues
## 7. Anti-scope
## 8. Decisions recorded (Chris-locked <date>)
## 9. Next step
## Appendix — Frontmatter provenance
```

Exemplar: `docs/research/domains/memory/1300_memory_domain_scoping.md`.

### 11.2 Child audit template (20-section skeleton, from v1)

```markdown
# <Domain / Child Topic> Architecture Audit

## 1. Executive Summary
## 2. Domain Purpose
## 3. Canonical Entry Points
## 4. Major Models
## 5. Major Services
## 6. Major APIs and Interfaces
## 7. Runtime Flows
## 8. Data Ownership and Lifecycle
## 9. Integrations With Other Domains
## 10. Event Flows
## 11. Existing Documentation
## 12. Research Coverage
## 13. Architecture Maturity
## 14. Known Drift
## 15. Known Technical Debt
## 16. Boundary Violations
## 17. Duplicate or Overlapping Systems
## 18. Ownership Gaps
## 19. Recommended Future Research
## 20. Appendix
```

Section requirements (from v1 §5):

- **§1 Executive Summary** — Answer: what is this domain, what
  are the biggest gaps, what should be researched next.
  300–500 words maximum.
- **§2 Domain Purpose** — Questions #1 + #2 from §9.
- **§3 Canonical Entry Points** — Question #3 with file:line.
- **§4–§8** — Questions #4–#9.
- **§9 Integrations With Other Domains** — Questions #14 + #17 +
  #18 + #21 + #22. Table format preferred.
- **§10 Event Flows** — Questions #19 + #20.
- **§11–§13** — Questions #10–#13.
- **§14–§18** — Questions #23–#27.
- **§19 Recommended Future Research** — Question #28. Rank by
  architectural uncertainty × risk × unblocked flows.
- **§20 Appendix** — Files inspected, docs inspected, grep
  patterns used, unresolved unknowns, conflicts between sources,
  verifier-loop corrections (Rigby SIGN fold notes go here).

Exemplar: multiple in the S1268–S1275 arc (see
ARCHITECTURE_INDEX §1.1–§1.12).

### 11.3 Canonical summary template

```markdown
# Group NNNN <Domain Name> — Canonical Summary

## 1. Executive Summary
## 2. What This Arc Answered
## 3. Consolidated Domain Shape
## 4. Cross-Cutting Patterns
## 5. Resolved Contradictions
## 6. Unresolved Unknowns
## 7. Anchor-Update Recommendations
   ### 7.1 PLATFORM_INVENTORY.md
   ### 7.2 PLATFORM_WHAT_IT_IS.md
   ### 7.3 ARCHITECTURE_INDEX.md
   ### 7.4 Other affected docs
## 8. Follow-On Research Queue
## 9. Cross-Links to Delegated Arcs
## 10. Arc Change Log
## 11. Appendix — Provenance
```

- **§1 Executive Summary** — 500–800 words. What did the arc
  ship, what changed about the domain understanding, what
  remains open.
- **§2 What This Arc Answered** — Per-child rollup: which of
  the 28 canonical questions each child answered.
- **§3 Consolidated Domain Shape** — A single map or diagram.
  This is the reader's mental model.
- **§4 Cross-Cutting Patterns** — Themes visible only across
  multiple children.
- **§5 Resolved Contradictions** — Where children disagreed;
  canonical verdict + rationale.
- **§6 Unresolved Unknowns** — Explicit list; promotes to §8.
- **§7 Anchor-Update Recommendations** — Concrete proposed
  edits. Do NOT edit anchors in the summary itself; the
  ARCHITECTURE_INDEX v-bump commit applies them.
- **§8 Follow-On Research Queue** — Ranked next-mission list.
- **§9 Cross-Links to Delegated Arcs** — Every `delegates_to:`
  entry from the parent gets a callout.
- **§10 Arc Change Log** — Which child, which session, which
  Rigby verdict, which fold edits.
- **§11 Appendix** — Every child's file path, evidence
  provenance, verifier-loop history.

The `xx99` summary is bounded work. Runtime: one session.

### 11.4 Frontmatter templates

Every doc leads with the frontmatter block from §6. Do not
skip fields; use `not applicable` sentinel values where a field
is genuinely unused.

---

# Part 4 — Execution Standards

## 12. Classification Rules

Reuse the classifications developed across S1268–S1275. Do not
invent new classifications per audit.

### Research Coverage

- **NONE** — no meaningful docs beyond code/comments.
- **LIGHT** — some docs or handoffs exist, but no dedicated
  architecture research.
- **MODERATE** — at least one focused doc or meaningful canonical
  documentation exists.
- **DEEP** — multiple focused docs, audits, or research docs
  exist.
- **CANONICAL** — clear source-of-truth docs exist and are
  actively maintained.

### Architecture Maturity

- **EXPERIMENTAL** — prototype, unstable, unclear ownership.
- **PARTIAL** — works in places but not cohesive or fully wired.
- **WORKING** — operational, used, but with gaps or drift.
- **STABLE** — operational, tested, documented, few known gaps.
- **CANONICAL** — stable, documented, verified, treated as
  source of truth.

### Risk

- **LOW**
- **MEDIUM**
- **HIGH**
- **CRITICAL**
- **UNKNOWN**

### Finding Type

Use the exact strings from S1274 §11 for cross-audit
consistency:

- `missing_connection`
- `overcoupling`
- `duplicate_model`
- `event_gap`
- `boundary_violation`
- `circular_dependency`
- `unclear_owner`
- `drift`
- `technical_debt`
- `extraction_candidate`
- `mature_primitive`
- `dead_code`
- `unknown`

### Integration Strength (S1274 pair classification)

For domain-to-domain pairs:

- **STRONG** — explicit, verified, well-observed connection.
- **WEAK** — connection exists but partial, spotty, or
  under-instrumented.
- **MISSING** — should exist per architectural logic but does
  not.
- **OVERCOUPLED** — connection exists but violates boundary
  discipline (e.g., inline import of one domain's internals
  from another).
- **UNKNOWN** — insufficient evidence to classify. Flag
  explicitly; do not silently omit.

**Binary language is forbidden for continuous reality.** The
S1274 EventBus lesson: "dormant" was wrong; "partially
adopted" was right. If reality is continuous, classification
must be continuous too.

---

## 13. Standard Explore-Agent Sweeps

Every child audit spawns exactly six parallel Explore sub-agents.
Sequential sweeps waste context and slow the mission down;
parallel sweeps have been the proven S1268–S1275 pattern.

Send all 6 in a single message with 6 tool-use blocks (parallel
tool calls). Do not batch sequentially.

Parent-scoping sessions (`NN00`) do NOT spawn sub-agents.
Canonical summaries (`NN99`) do NOT spawn sub-agents. Both
consume prior child outputs.

### Agent 1 — Models and Persistence

**Focus:** Django models owned by this domain, foreign-key graph
to models outside the domain, migration lineage,
retention/lifecycle policies, unique constraints, indexes.

**Deliverable:** Model inventory with file:line, ownership
classification (this-domain vs shared vs foreign), overlap flags
that cross-reference S1273 §5 (duplicate/overlapping systems).

### Agent 2 — Services and Runtime Flows

**Focus:** Service layer (`core/services/*`, `core/agents/*` if
domain has agents, `core/employees/*` if domain has employees),
runtime flow diagrams, lazy imports, dependency chains,
god-service checks (line count + cross-domain imports).

**Deliverable:** Service inventory with file:line, runtime flow
step-by-step, god-service ranking if any exceed 3000 lines.

### Agent 3 — APIs, Tools, Tasks, Commands

**Focus:** REST endpoints, WebSocket consumers, PA tools
(td_handlers), Celery tasks (with beat schedule if applicable),
management commands. Cross-reference `docs/PLATFORM_INVENTORY.md`
autoblock for counts.

**Deliverable:** External-facing surface inventory with file:line,
beat-schedule cadence, tool schemas if applicable.

### Agent 4 — Integrations and Cross-Domain Dependencies

**Focus:** Which of the 32 domains this domain talks to or should
talk to. Reference `docs/research/platform/cross_domain_integration_audit.md`
§2 (integration map) as starting point. Verify current wiring vs
what's documented.

**Deliverable:** Inbound + outbound integration map, missing
connections, overcoupled surfaces, event flow analysis.

### Agent 5 — Documentation and Prior Research

**Focus:** Existing docs about this domain — topic docs
(`docs/topics/`), handoffs (`docs/handoffs/`), narratives
(`docs/narratives/`), any prior research library entries
(`docs/research/`). Explicit gap analysis: what does existing
documentation NOT cover?

**Deliverable:** Documentation inventory, research coverage
classification, explicit "already covered by X" pointers to avoid
duplication in the new audit.

### Agent 6 — Drift, Debt, Ownership, and Maturity

**Focus:** Known drift (docs say X, runtime says Y), technical
debt (with severity), ownership gaps, maturity assessment
(EXPERIMENTAL/PARTIAL/WORKING/STABLE/CANONICAL).

**Deliverable:** Drift matrix, debt matrix with severity,
ownership row per §9 question #25, maturity verdict with
evidence.

### Parent Agent (Claude) Synthesis

After all 6 sub-agents return:

1. Merge duplicate findings.
2. Resolve conflicts by direct file:line reads (verifier loop —
   trust but verify).
3. Spot-check load-bearing claims with independent grep/read.
4. Mark UNKNOWNs honestly (§14).
5. Write the 20-section audit per §11.2.
6. Route to Rigby per §15.

---

## 14. Standard Evidence Rules

- **File:line citations for load-bearing claims.** Every claim
  that could affect a downstream decision must cite the source.
  Do not paraphrase code without a cite.
- **Direct source verification for important findings.** If a
  sub-agent asserts something load-bearing, the parent agent
  verifies by reading the cited file:line before including it.
  This is the "trust but verify" rule from the S1273 Rigby
  reviews.
- **Unknowns marked honestly.** `UNKNOWN` is a valid finding.
  Guessing is not. When you infer intent from code without a
  documented rationale, flag as `SPECULATIVE`.
- **No speculation presented as fact.** If Rigby will grep and
  catch a wrong claim, better to flag it as `SPECULATIVE` now.
  (S1274 v1 mis-classified EventBus as "dormant"; Rigby caught
  it by direct grep. That's the failure mode this rule
  prevents.)
- **Count conflicts resolved against runtime inventory.** When
  two sources disagree on a count (agent count 83 vs 90, PA
  tools 104 vs 113), `PLATFORM_INVENTORY.md` autoblock wins per
  `DOC_LIFECYCLE.md` §2c. Cite the winner; flag the drift.
- **No implementation during research.** Research is research.
  Do not open PRs, do not modify runtime code, do not create
  migrations, do not "fix while you're in there." The whole
  point of the research library is that PRs come later and
  reference research.
- **Grep-verify binary claims before shipping to Rigby.** Any
  claim of the form "X is dormant / absent / missing / never
  used" invites a Rigby grep. Front-run it: run the grep
  yourself first. If the grep finds evidence, downgrade the
  language.

---

# Part 5 — Review & Governance

## 15. Rigby Review Policy — Per Stage

Every research doc routes to Rigby for a human-style architecture
review. Rigby is not a rubber stamp — she independently greps the
codebase and catches factual errors (S1274 EventBus lesson).

### Stage-scoped routing

| Stage | Rigby SIGN routing | Rationale |
|-------|-------------------|-----------|
| **Parent scoping (`NN00`)** | **Optional light SIGN** — Chris decides | Parent is a scoping deliverable, not a research finding. Full SIGN attaches per child audit. A light SIGN may pressure-test the taxonomy boundaries + child sequence when Chris wants a second read. |
| **Child audit (`NN01`–`NN98`)** | **Required full SIGN** | Full audit with load-bearing claims → Rigby pressure-tests. This is the pattern proven across S1268–S1275. |
| **Canonical summary (`NN99`)** | **Required full SIGN** | Synthesizes findings; independent review protects against wave misreads. |
| **Design preparation** | **Required full SIGN** | Downstream commits use this as the design. Wrong recommendation → wrong PR. |
| **Design decision (ADR)** | **Required full SIGN** — Chris ratifies | The ratification IS the SIGN outcome. |
| **Process document** (this playbook) | **Optional** — Chris gates directly | Rules for other docs; Chris is the primary reviewer. Route to Rigby if pressure-testing the rules themselves matters. |
| **Navigation (INDEX)** | **Not per-update** | Index maintenance is mechanical; SIGN only for structural changes. |

### Fresh isolation pin

Per S1273/S1274/S1275 practice, use a **fresh isolation pin** if
the current arc pin might be shared with another Claude Code
session. Generate via:

```bash
python3 -c "import secrets; print(f'pa-{secrets.token_hex(8)}')"
```

Invoke `pa_chat.py` with explicit `--conversation` override; do
**not** modify `tools/pa_local.sh` if other Claude Code sessions
depend on the shared pin. Retire the isolation pin at session
close.

### Standard Rigby pressure-test questions

```
1. Did Claude miss any major parts of this domain?
2. Did Claude overstate maturity?
3. Did Claude understate maturity?
4. Did Claude confuse intentional separation with missing
   integration?
5. Did Claude identify the right technical debt?
6. What is the riskiest finding?
7. What is the most important future research?
8. What did Claude get wrong?
9. What must change before canonical?
```

For canonical summaries, add:

```
10. Did Claude resolve the child contradictions correctly?
11. Are the anchor-update recommendations complete?
12. Did Claude miss any cross-cutting pattern?
13. Are the follow-on queue rankings defensible?
```

For design-preparation docs, add:

```
14. Is the recommendation reversible?
15. Are the graduation triggers real, or cope-defenses?
16. Which failure modes are unaddressed?
```

### Response format Rigby uses

```
Overall confidence: High / Medium / Low

Most accurate part:

Weakest part:

Missing area:

Overstated maturity:

Understated maturity:

Biggest architectural risk:

Most important next research:

What Claude got wrong:

What must change before canonical:

Final verdict: SIGN-clean / SIGN-with-edits / NEEDS-MORE
```

### Folding edits

- **SIGN-clean** — no changes needed. Update frontmatter
  `verifier_loop` with "Rigby SIGN-clean" note. Move on.
- **SIGN-with-edits** — fold every substantive edit into the doc
  before it's considered publishable. Update frontmatter
  `verifier_loop` field with fold summary (what was changed +
  why). Preserve the v1 note.
- **NEEDS-MORE** — Rigby thinks the doc isn't ready. Do not
  publish. Address her concerns, re-audit if needed, re-route.

### Rigby's grep-verification pattern

Rigby regularly verifies claims by direct `repo_tool.search` +
`repo_tool.read_file`. If your audit contains a factual claim
that will fail a 3-second grep, expect her to catch it.
Especially: **binary "X is dormant / absent / missing" claims.**
The S1274 EventBus lesson: "wiring dormant" was wrong;
"partially adopted" was right. Rigby found 5 publisher wrappers
+ 3 consumer tasks by direct grep in under a minute.

---

## 16. Commit Policy — Draft → Canonical

**Default: do not commit.** Every research doc lands as a
`status: draft` document in an uncommitted state. Chris reviews,
then explicitly says "commit it" (or similar). Only then does the
commit happen.

### Draft-first workflow

1. Draft the doc during the session; land on local filesystem.
2. Route to Rigby per §15.
3. Fold SIGN-with-edits edits.
4. Return summary to Chris.
5. Wait for explicit "commit it" instruction.

### When Chris says commit

1. Update `docs/research/ARCHITECTURE_INDEX.md`:
   - Add a new §1.N row for the doc (see the S1273 §1.9 or
     S1274 addition pattern).
   - Update §8 timeline with a new row.
   - Update §3 domain map row if this doc changes the maturity
     or coverage rating for the domain.
   - Update §5 gap entries if this doc closes any prior gap or
     opens new ones.
   - Update §7 decision matrix if this doc adds a new class of
     work worth flagging.
   - Update §9 roadmap lateral research list if this doc
     changes what's queued next.
   - Bump frontmatter `last_verified` and `owner` fields.
   - Bump the ARCHITECTURE_INDEX version (v8 → v9, etc.).
   - Add Appendix pass notes for the version bump.
2. If the doc is a canonical summary, apply the anchor-update
   recommendations from §7 of that summary in the same commit
   or an immediately-following commit.
3. Register the doc's file in a new commit.
4. Stage **only** `docs/research/` files unless Chris explicitly
   approves other changes.
5. Commit message format:

   ```
   docs(research): add <domain> <doc type> (S<session_id>)

   <one-paragraph summary of biggest findings + Rigby SIGN status>

   Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
   ```

### Status transition from `draft` → `active`

The `status` frontmatter field flips from `draft` to `active`
when Chris explicitly ratifies the doc. For most child audits,
"commit it" implies ratification. For design-preparation docs,
Chris may say "commit as draft" to preserve the recommendation
without ratifying it (see Symbol Mapping §1.10 handling).

### Never commit without

- Explicit Chris instruction.
- Rigby SIGN status resolved (SIGN-clean or SIGN-with-edits
  folded — not NEEDS-MORE).
- All frontmatter fields populated.
- `verifier_loop` note current.

### Never modify

- Runtime code (`core/*.py` outside `core/services/pa_tool_schemas.py`
  as a docs edge case).
- Migrations.
- Generated inventories (`docs/PLATFORM_INVENTORY.md`,
  `docs/INDEX.md`) — those come from
  `manage.py generate_platform_inventory` or
  `manage.py build_docs_index`, not hand edits.
- Anything in `tools/` unless it's a research-only tool.

### Handling drafts during active research

Multiple draft docs may exist in the working tree during a
long-running arc. This is fine. Discipline:

- Each draft carries `status: draft` in frontmatter.
- Each draft is uncommitted OR committed with an explicit
  `status: draft` value (Chris-approved intermediate commit).
- Draft docs must not claim canonical facts elsewhere. If a
  child doc under draft is cited by another new doc, the citing
  doc must acknowledge the draft status.

---

## 17. Graduation Criteria

A research group is **complete** when all of the following are
objectively true:

### For single-audit groups

- [ ] The audit file exists at
      `docs/research/<location>/<session_id>_<slug>_audit.md`.
- [ ] Frontmatter carries `status: active` and `authority:
      research`.
- [ ] `verifier_loop` records Rigby SIGN status: `SIGN-clean` or
      `SIGN-with-edits (N folded)`. Never `NEEDS-MORE`.
- [ ] All 28 canonical questions (§9) answered — with cite,
      reference, or explicit `UNKNOWN`.
- [ ] Doc is committed to the branch.
- [ ] `ARCHITECTURE_INDEX.md` bumped: new §1.N row + §8
      timeline row + §3 domain map update + §5 gap update +
      §7/§9 as applicable.
- [ ] Follow-on research queue captured in §19 of the audit.

### For parent-with-children groups

- [ ] Parent doc committed with `status: active`,
      `authority: parent-doc`.
- [ ] Every locked child slot (P1–P?) has a committed audit
      file that meets the single-audit criteria above.
- [ ] Every child audit has Rigby SIGN status resolved.
- [ ] Canonical summary (`xx99`) committed with `status:
      active`, `authority: research`.
- [ ] Canonical summary's anchor-update recommendations either
      applied in a companion commit or explicitly deferred with
      rationale.
- [ ] All UNKNOWNs from child audits either resolved in the
      summary or promoted to the follow-on queue (§8 of the
      canonical summary).
- [ ] Cross-arc delegations (`delegates_to:`) named in parent
      have companion pointers in the receiving arc (or a queued
      research group).
- [ ] `ARCHITECTURE_INDEX.md` bumped for parent + every child +
      canonical summary. Multiple version bumps may happen
      during a long arc; each commit's bump is legitimate.
- [ ] No open Rigby "NEEDS-MORE" verdicts on any doc in the
      arc.

### Group states

| State | Definition |
|-------|-----------|
| `not-started` | Parent doc not yet drafted. Range NNNN unclaimed. |
| `in-progress` | Parent drafted OR children shipping. Some criteria unmet. |
| `awaiting-summary` | All children shipped and SIGN-resolved; `xx99` not yet written. |
| `closed` | All graduation criteria met. Group is done. |
| `stalled` | Group has open `NEEDS-MORE` verdicts or blocked children. Chris intervention needed. |

If any criterion is unmet, the group is **not** `closed`. Mark
as `in-progress`, `awaiting-summary`, or `stalled` per the
table.

### Post-closure lifecycle

After a group closes:

- The follow-on queue is Chris's next-mission menu.
- New evidence about the domain gets a **new** research group
  (e.g., a future memory-adjacent finding opens Group 2300, not
  Group 1300 amendments).
- The closed group's docs stay `status: active`. They are
  historical for the group but canonical for their scope.
- Superseded findings mark `status: superseded` and cite the
  replacing doc.

Closure is measurable. It is not a subjective assessment.

---

# Part 6 — Framework Discipline

## 18. Domain Dependency Mapping

Domains are not independent. Findings in one group inform
questions in another. The framework formalizes three
relationships.

### The three relationships

| Frontmatter field | Semantics |
|-------------------|-----------|
| `dependencies_on:` | Research groups whose findings this group inherits. Reading this group without reading dependencies produces gaps. Non-blocking — a session can open Group 1500 before Group 1300 completes; the shape is informational. |
| `delegates_to:` | Subdomains this group hands off to another arc. The receiving arc owns them. Preserves scope discipline. |
| `delegated_from:` | Subdomains this group inherits from another arc. The originating arc named the boundary. |

### Example dependency chain

```
Employee OS (Group 1200s)
    ↓ dependencies_on: none (foundation)
    ↓ delegates_to: Memory (Category G Mission Memory to Group 1300)
    │
    ▼
Memory (Group 1300)
    ↓ dependencies_on: Employee OS (for Mission Memory semantics)
    ↓ delegates_to: Employee OS (Category G Mission Memory)
    │
    ▼
Knowledge (subset of Memory Group 1300)
    ↓ dependencies_on: Memory Group 1300
    │
    ▼
Governance (Group 1200s)
    ↓ dependencies_on: Employee OS + Memory (for cross-employee state)
    ↓ delegates_to: Human Interface (HAI lifecycle to Group 1800s)
    │
    ▼
Human Interface (Group 1800s)
    ↓ dependencies_on: Governance (for auto-approve gate semantics)
```

### Rules

1. **Dependencies do not block execution.** A session can open
   Group 1500 (Sports) before Group 1300 (Memory) completes.
   Dependencies are informational: the reader should know what
   findings to load first.
2. **Delegations are explicit.** Every `delegates_to:` entry
   must name the target group, the delegated slug, and the
   scope of delegation. Vague delegations breed drift.
3. **Delegations appear in anti-scope.** The parent doc's
   anti-scope section explains why the subdomain is delegated,
   not just that it is.
4. **The receiving arc acknowledges delegations.** When a group
   receives a delegation, its parent doc lists the
   `delegated_from:` entry. The receiving arc's canonical
   summary cites the originating arc.
5. **Dependencies are DAG-shaped by convention.** Circular
   dependencies (Group A depends on Group B AND Group B depends
   on Group A) are a smell. If it happens, resolve via a
   canonical summary that owns the joint boundary — or by
   splitting one of the groups.
6. **Cross-arc citations use ARCHITECTURE_INDEX §1.N.** Cite
   the specific research doc via its index row, not via file
   path.

### Dependency-map maintenance

The ARCHITECTURE_INDEX §4 (dependency graph) shows the visible
Employee OS + platform-inventory arcs. As new groups close,
extend §4 with new nodes. The dependency graph is the arc-scale
version of the file:line citation discipline.

---

## 19. Generalization Requirements

The framework must work equally well for **every** domain, not
just the domain that motivated its creation. This section
codifies the check.

### Verification list

For any of the following domains, the framework must produce a
sensible arc without domain-specific patches:

- Memory ✓ (S1300 exemplar)
- Revenue
- Employee OS (retroactively — S1268–S1275 covered under
  pre-v1 conventions; would fit v2 if restarted)
- Governance ✓ (S1269 single-audit example)
- AI Studio
- Sports / DBAO
- Knowledge (currently a subset of Memory Group 1300)
- Notifications
- Human Interface
- Platform (whole-scope)
- Content / Deliverables
- Observability / Telemetry
- Event / Integration / Runtime Architecture

### Anti-domain-specific-language rules

1. **Never write "memory-persistence" as a general concept.**
   Prefer "domain-persistence" or "subsystem-persistence" in
   the playbook. Reserve domain-specific vocabulary for
   domain-specific docs.
2. **Verb-level neutrality.** Prefer domain-neutral verbs:
   *audit, inventory, integrate, classify, delegate, ratify.*
   Avoid domain-flavored verbs like *embed, escalate,
   deliberate* in the playbook body.
3. **Example choice.** When illustrating a rule with a concrete
   example, cite two different domains where possible. Single
   examples read as generalizations from that domain.
4. **Template heading generality.** Section headings in §11
   templates must be generic (*"Major Models"*, not *"Memory
   Stores"*). Domain-specific subheadings live in the docs
   using the templates, not the templates themselves.
5. **Classification neutrality.** §12 classifications must work
   for every domain. If a new domain surfaces a classification
   gap, extend §12 via §20 evolution policy — do not per-doc
   patch.

### The pre-audit generalization check

Before running any new research group, run a five-minute mental
test:

1. Does the domain map to at least one S1273 §3.N row? *(If no,
   flag as "add new inventory row" — see §8 parent
   responsibility 4.)*
2. Do the 28 canonical questions in §9 apply to this domain?
   *(If any don't, note as `not applicable` in the audit — do
   not skip silently.)*
3. Do the 6 Explore sub-agents (§13) map to this domain? *(If
   Agent 1 Models doesn't apply because the domain has no
   Django models, substitute the analogous surface — e.g.,
   config schemas, Redis keys — but justify the swap in the
   audit appendix.)*
4. Do the classifications in §12 fit? *(If the domain's maturity
   isn't reachable by EXPERIMENTAL/PARTIAL/WORKING/STABLE/
   CANONICAL, propose a §12 extension via §20 before running
   the audit.)*
5. Does the folder structure in §5 fit? *(If not, propose a
   layout change via §20 before running.)*

If any check fails, patch the playbook FIRST (via §20). Do not
run an audit under a playbook that doesn't fit — the audit will
drift from methodology and future arcs will inherit the drift.

---

## 20. Architecture Evolution Policy

This playbook is itself a living architectural artifact. Rules
for how it evolves — how proposals get made, how versions are
tracked, how older research groups remain valid — matter as much
as the platform-architecture rules the playbook governs.

### Versioning

- **Frontmatter `version:` field.** Bumped on every substantive
  change: `v1` → `v2` → `v3` → …
- **`session_added:` field is immutable.** Records when the
  playbook was FIRST created. Does not bump with version.
- **`last_verified:` field bumps every version.** Records the
  session ID and date of the latest verification against
  reality.
- **`verifier_loop:` appended, never truncated.** Each version's
  entry records what changed and why. Prior version entries
  stay in place.

### ARCHITECTURE_INDEX registration

The playbook's §1.11 row (in ARCHITECTURE_INDEX.md) cites the
current version. On version bump:

- Update the §1.11 row's version reference.
- Add a §8 timeline row for the version bump.
- Bump ARCHITECTURE_INDEX's own version (playbook v2 might
  land as INDEX v9, or split — depends on other changes in
  the same commit).

### Additive-first evolution

**New sections may be added. Existing sections may be extended.
Renaming or removing existing sections requires an explicit
migration note in §20's changelog subsection.**

Rationale: research groups closed under a prior version
reference §N by number. Renaming §4 to something else breaks
those references.

### Backwards compatibility

Older research groups that were closed under a prior version
STAY under that version. They do not retroactively conform to
v2+ additions.

- A canonical summary written under v1 does not have to add
  §7 anchor-update-recommendations to conform to v2 — it
  conformed when it was written.
- A future canonical summary MAY reference v1's rules
  explicitly by version: *"Per playbook v1 §10, this arc's
  commit policy was …"*
- Cross-arc dependencies are version-agnostic. Group 1300
  under v2 depends on Employee OS Group 1200s under v1 without
  needing translation.

### Evolution triggers

A pattern is eligible for playbook formalization when any of
the following holds:

- **Three independent research groups have used it.** Below
  three uses, the pattern is still emergent — codifying it too
  early risks over-fitting.
- **A pattern would have caught a real drift.** Example:
  S1300's parent-with-children shape would have caught the
  scoping ambiguity even without Chris's intervention. That
  makes it a canonical trigger.
- **A user-directed override.** Chris says *"formalize this."*
  That is a canonical trigger by itself.
- **Rigby catches the same class of error twice.** Two
  independent SIGN reviews flag the same drift pattern → the
  playbook probably needs a rule to prevent it.
- **A new domain surfaces a classification, folder, or
  metadata gap.** Extend §12/§5/§6 rather than per-doc patching.

### Deprecation

Sections may be marked deprecated but never deleted. Deprecated
sections carry a callout at the top:

```markdown
## §N. Section Title

> **DEPRECATED (v3).** Superseded by §M in v3 because <reason>.
> Older research groups that reference §N by number remain
> valid — the section is preserved for their sake.
```

### Change proposal workflow

1. A user or agent identifies a pattern worth formalizing.
2. Draft the addition/extension in a working-tree copy of the
   playbook. Do not commit.
3. Increment the version in frontmatter (`v2` → `v3-draft`).
4. Route to Rigby per §15 if desired (optional for
   `authority: process`).
5. Chris reviews. When Chris approves, drop the `-draft`
   suffix, commit, and update ARCHITECTURE_INDEX §1.11 + §8.

### Reality wins over the playbook

If a proven pattern conflicts with a playbook rule, reality
wins. The playbook is patched to match. This is the same
discipline as `PLATFORM_INVENTORY.md` autoblock winning over
narrative anchors per `DOC_LIFECYCLE.md` §2c.

Example: if Chris directs an arc to skip Rigby SIGN on child
audits and the arc closes cleanly, that is evidence the SIGN
rule may be over-strict for a class of arc. The next playbook
version records the exception explicitly rather than pretending
it did not happen.

### Changelog

Every version bump adds a row here.

| Version | Session | Date | Summary |
|---------|---------|------|---------|
| v1 | S1274 | 2026-07-01 | Playbook drafted. Codified numbering (1300–1900), output paths, 27→28 audit questions (v2 fold), 20-section template, 6 parallel Explore sweeps, classification rules, Rigby SIGN pattern, commit rules. Chris explicit direction at close: *"register it now and commit."* |
| v2 | S1276 | 2026-07-01 | Restructured into 7 parts, 24 sections. Formalized: research group lifecycle (§2), phase discipline (§3), xx99 canonical summary convention (§4, §10), folder structure (§5), metadata standard (§6), cross-reference policy (§7), parent responsibilities (§8), canonical summary responsibilities (§10), stage-scoped Rigby routing (§15), graduation criteria (§17), dependency mapping (§18), generalization requirements (§19), evolution policy (§20). All v1 content preserved semantically. |

---

# Part 7 — Application

## 21. Short Start Commands

Chris uses these to open, continue, or close a research session:

### Opening

```
Start research group 1300: Memory
Start research group 1400: Revenue
Start research group 1500: Sports Intelligence
Start research group 1600: Content and Publishing
Start research group 1700: Observability
Start research group 1800: HumanAttention and Learning
Start research group 1900: Event Architecture
```

**What happens.** Claude reads this playbook + ARCHITECTURE_INDEX
+ the target group's S1273 §3.N inventory row(s) + S1274 §2.N
cross-domain rows. Then decides parent-vs-single per §8.
Executes STAGE 0 (parent scoping) if arc; STAGE 1 (single
audit) if not.

### Continuing

```
Continue research group 1300: <child slot letter or topic>
Continue research group 1300: P2 memory persistence
```

**What happens.** Claude re-reads the parent doc + prior child
audits + this playbook. Runs STAGE 1 for the named child slot.
Launches 6 parallel Explore sweeps per §13.

### Closing an arc

```
Close research group 1300
```

**What happens.** Claude confirms all children have `status:
active` + Rigby SIGN resolved. If yes, opens the `xx99`
canonical summary session per §10. If not, reports which
children remain open.

### How Claude infers the mission shape

Given a command like `Start research group 1300: Memory`, Claude
extracts:

- **`session_id`** — the numeric prefix (e.g., `1300`). If Chris
  wants to number differently within the range, he'll specify.
  Otherwise default to the range's first slot.
- **`domain_slug`** — lowercase single-word or hyphenated form of
  the domain name.
- **`output_path`** —
  `docs/research/domains/<domain_slug>/<session_id>_<domain_slug>_domain_scoping.md`
  (for arcs) OR
  `docs/research/domains/<domain_slug>/<session_id>_<domain_slug>_architecture_audit.md`
  (for single-audit groups).
- **Standard doc structure** — per §11 templates.
- **Sub-agent sweeps** — 6 parallel Explore agents per §13 (for
  child audits only).
- **Rigby review** — per §15 stage-scoped table. Generate a
  fresh isolation pin if the shared arc pin might be crossed.

### Standard opening sequence for an arc

1. Read this playbook (`DOMAIN_RESEARCH_PLAYBOOK.md`).
2. Read `ARCHITECTURE_INDEX.md` §1.N + §3 + §5 rows for the
   target domain.
3. Read `platform_architecture_inventory.md` §3.N and any
   §5.N overlap rows.
4. Read `cross_domain_integration_audit.md` §2.N (integration
   map) + any relevant §3–§10 findings for this domain.
5. Read existing docs for the domain (topic docs, handoffs,
   narratives). Do not duplicate their content in the audit;
   cite them.
6. If arc: draft the parent doc per §11.1.
7. If single-audit: launch 6 parallel Explore sub-agents per §13.
8. Synthesize per §11.
9. Route to Rigby per §15.
10. Fold SIGN-with-edits into the doc.
11. Return summary to Chris per §24.
12. **Do not commit** unless Chris asks (§16).

---

## 22. Initial Domain Queue

The following research groups are planned. Order is a
recommendation; Chris can pick any of them next.

| Range | Domain | S1273 §3 Row | Coverage | Priority Rationale |
|---|---|---|---|---|
| 1300 | Memory / Knowledge / Embeddings | §3.13 | DEEP inventory / LIGHT integration | Foundation for cross-domain feedback loops; two RAG lanes need call-time selector research. **Arc opened S1300; parent locked 2026-07-01.** |
| 1400 | Revenue / Outreach / Engagement | §3.32 | LIGHT | Rigby-caught missed domain (S1273 v2); business-value highest under-researched domain |
| 1500 | Sports / DBAO / Intelligence | §3.10 | LIGHT | Resolves platform's biggest structural question (island vs integrated per S1274 §12.3) |
| 1600 | Content / Deliverables / Publishing | §3.11 | MODERATE | Well-inventoried; integration analysis needed (S1274 §5.3, §7.4) |
| 1700 | Observability / Telemetry / SLOs | §3.25 | DEEP | 5-layer telemetry dedup audit named by S1273 §5.13 + S1274 §12.6 |
| 1800 | HumanAttention / Feedback / Learning | §3.16 | MODERATE | Only round-trip learning loop today; scope expansion research |
| 1900 | Event / Integration / Runtime Architecture | §3.31 | LIGHT | Downstream of S1274 §12.1 EventBus Adoption + Contract Verification |

**Note on ordering.** The queue above is default; Chris can pick
any of them next. If Chris opens `Start research group 1500`
before Group 1300 closes, Claude executes the sports mission
without requiring the memory mission to land first. The ranges
are labels, not dependencies (see §18 for the actual
dependency semantics — which are informational, not blocking).

**Cross-references to existing research.** Each group inherits
the findings from S1268–S1275 relevant to its domain. See §23.

---

## 23. Relationship to Existing Research

This playbook does not create new methodology — it standardizes
what already worked across S1268–S1275. Reference these prior
missions when starting any new domain audit:

- **S1268 — Employee OS Communication Substrate Audit + Protocol
  Sketch + Collaboration Patterns.** Established the reuse-first
  discipline (do not build a new model when a wrapper suffices)
  + the 64-row primitives inventory pattern + the failure-modes
  inventory pattern.
- **S1269 — Governance / Authority Evolution.** Established the
  4-plane inventory pattern (per-plane inventory + composition
  gap analysis) + the "35 gates" enumeration style.
- **S1270 — Symbol Mapping Architecture.** Established the
  design-space enumeration style (5 options with tradeoffs, no
  selection) + the "F-finding" numbering.
- **S1271 — Actor Identity & Attribution Architecture.**
  Established the multi-role vocabulary pattern (executor_actor /
  sponsor_actor / principal_user) + the "22 attribution
  surfaces" grid.
- **S1272 — Authority Enforcement Design Space.** Established
  the design-space-only maintenance note + the 6-options-A-F
  pattern + the DAG-of-prerequisites style.
- **S1273 — Whole-Platform Architecture Inventory.** Established
  the 32-domain map + 9 cross-domain flows + Maturity Matrix +
  Coverage Map + 11-mission roadmap pattern. Rigby-caught missed
  domain (Revenue) taught: *"if a real domain is missing,
  sub-agent sweeps didn't cover it — trust Rigby's independent
  grep."*
- **S1274 — Cross-Domain Integration Audit.** Established the
  integration-lens shape (not another inventory) + the
  "producer/consumer registry" style + the "STRONG/WEAK/
  MISSING/OVERCOUPLED/UNKNOWN" pair classification. Rigby-caught
  binary-classification error ("EventBus dormant" → "partially
  adopted") taught: **do not use binary language for continuous
  reality**.
- **S1274 (concurrent) — Symbol Mapping Option Selection
  Design.** Established the design-preparation shape (first
  mission producing an evidence-based Chris-gated recommendation)
  + the graduation-trigger guardrail pattern (prevent
  "E-forever cope").
- **S1274 (playbook draft) — DOMAIN_RESEARCH_PLAYBOOK v1.**
  This document, first draft.
- **S1275 — Symbol Mapping Event Schema Design.** Established
  the implementation-ready-schema shape (first mission shipping
  concrete field spec + emitter/consumer contract) while
  remaining `authority: design-preparation`. Rigby SIGN caught 8
  must-fixes + bonus #9 including the two-surface unification
  pattern.
- **S1300 — Memory Domain Scoping.** Established the
  parent-with-children arc shape as a first-class pattern. Chris
  explicitly locked the shape + child sequence + `xx99`
  canonical summary convention. Basis for v2 additions §2, §8,
  §10.
- **S1276 — DOMAIN_RESEARCH_PLAYBOOK v2.** This version. No new
  domain research — the arc is the playbook itself becoming
  self-describing.

**The library's shape** (per `ARCHITECTURE_INDEX.md` v8+):

- Employee OS deep arc: `§1.1 → §1.2/§1.3 → §1.4 → §1.6 → §1.7 →
  §1.8 → §1.10 → §1.12`.
- Whole-platform sibling arc: `§1.9` (inventory) →
  `cross_domain_integration_audit.md` (integration audit).
- Process arc: `§1.11 v1` → v2 (this doc).
- Domain research groups: `docs/research/domains/<slug>/` populates
  as each research group runs. Group 1300 Memory opened S1300.

**Anchor discipline** (from S1268 onward): every audit lists
`companion_anchors` in frontmatter. The load-bearing anchors are:

- `docs/PLATFORM_INVENTORY.md` — runtime counts (autoblock wins
  on conflict).
- `docs/PLATFORM_WHAT_IT_IS.md` — narrative anchor (glossary).
- `docs/EMPLOYEE_OS_PRIMITIVES.md` — canonical primitives +
  anti-duplication matrix.
- `docs/00-START-HERE/DOC_LIFECYCLE.md` — doc governance rules
  including the inventory-wins-on-conflict rule (§2c).
- `docs/research/ARCHITECTURE_INDEX.md` — library navigation.
- `docs/research/platform_architecture_inventory.md` — 32-domain
  map.
- `docs/research/platform/cross_domain_integration_audit.md` —
  integration gap map.
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (this doc) — the
  process itself.

Any audit that misses these anchors is broken at the root.

---

## 24. Final Self-Check

Before returning a mission summary, verify:

- [ ] The mission executed exactly the arc shape the playbook
      calls for (parent per §2 STAGE 0, or single audit; child
      per §2 STAGE 1; canonical summary per §2 STAGE 2).
- [ ] The mission does **not** start a domain audit unless
      Chris said `"Start research group NNNN: X"` or a
      continuation/close variant per §21.
- [ ] The mission does **not** make runtime changes. Zero
      touches to `core/*.py` (runtime), migrations, or
      generated inventories.
- [ ] Every doc produced carries the frontmatter fields from §6
      with the correct `authority`, `status`, `research_group`,
      `child_slot`, `domain_slug`, and `verifier_loop`.
- [ ] Cross-references cite per §7 (file:line for code, §N.M
      for sections, ARCHITECTURE_INDEX §1.N for cross-arc).
- [ ] Companion anchors declared correctly in frontmatter.
- [ ] For child audits: all 28 canonical questions (§9)
      answered — cite, reference, or `UNKNOWN`.
- [ ] For parents: parent-vs-single verdict explicit; locked
      child sequence with rationale; anti-scope named;
      delegations explicit.
- [ ] For canonical summaries: cross-cutting patterns
      identified; contradictions resolved; anchor-update
      recommendations concrete; follow-on queue ranked;
      delegated-arc cross-links present.
- [ ] Rigby SIGN routing correct per §15 stage-scoped table.
      Fresh isolation pin used per S1273/S1274/S1275 practice.
- [ ] Rigby SIGN-with-edits fully folded before summary
      returned to Chris.
- [ ] `verifier_loop` frontmatter reflects current SIGN status.
- [ ] Commit rules honored per §16. Default: do not commit.
      Only commit on Chris's explicit instruction.
- [ ] If commit lands: `ARCHITECTURE_INDEX.md` bumped per §16
      (§1.N row + §8 timeline + §3/§5/§7/§9 as applicable +
      version bump).
- [ ] For arc closure: graduation criteria per §17 verified.
      Group state (`in-progress` / `awaiting-summary` /
      `closed`) explicit.
- [ ] Domain dependency mapping per §18 documented if the
      group has cross-arc relationships.
- [ ] Generalization check per §19 passed (or a §20 playbook
      extension proposed).
- [ ] Playbook version cited if the arc references playbook
      rules by number.

Return summary to Chris including:

- File(s) created or updated with paths.
- Summary of what section content was written.
- Whether `docs/research/ARCHITECTURE_INDEX.md` needs update
  now, at commit time, or after canonical summary.
- Any playbook §20 extension proposals surfaced during the
  arc.
- Any questions before Chris commits.

---

**Status.** Playbook v2 active. No routing to Rigby (this is
process documentation, not a research finding — per §15's own
rule for `authority: process`). Do not commit unless Chris
explicitly asks (§16).

**Next version trigger.** v3 will fire when one of §20's
evolution triggers surfaces — most likely candidate: a Group
1400/1500/1600 arc surfaces a classification, template, or
folder gap the current playbook does not cover.

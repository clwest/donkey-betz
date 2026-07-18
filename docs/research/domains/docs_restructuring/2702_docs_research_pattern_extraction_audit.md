---
title: "S2812 /docs/research/ Pattern Extraction & Transferability Audit (T2 of Group 2700 arc)"
status: active (audit deliverable — extraction + inline transferability challenge per primitive)
authority: T2 child audit of Group 2700 parent arc
session: 2812
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
thread: T2
authors: Claude Code (Chris directed at S2812 open)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md   # parent (Chris-locked 2026-07-16)
  - docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md       # T1 predecessor (S2811)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                              # source of primitives being extracted
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                                     # source of process primitives
  - docs/research/ARCHITECTURE_INDEX.md                                                    # source of decision-matrix primitive
  - docs/research/OPEN_ARCS.md                                                             # source of state-ledger primitive
  - docs/research/domains/memory/1300_memory_domain_scoping.md                             # parent-scoping frontmatter exemplar
  - docs/research/domains/auth/2400_auth_domain_scoping.md                                 # SIGN-isolation-pin discipline exemplar
  - docs/research/domains/api/2500_api_domain_scoping.md                                   # xx01-xx98 as design_prep_audit exemplar
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                    # §2b runtime-coupled + §2c counts anchor + §3 root-stability (arc-wide constraints)
scope: T2 = reverse-engineer transferable primitives from docs/research/ per parent §4 — extraction + inline transferability challenge, no application proposal
non_goals:
  - applying primitives to the rest of /docs/ (that's canonical summary at 2799)
  - restructuring proposal
  - file moves, deletions, renames, code changes (arc non-goals per parent §5)
  - restating what the source primitives DO (that's the source docs' job — T2 extracts + challenges)
  - re-authoring DOMAIN_RESEARCH_PLAYBOOK.md v2 shape (T2 uses it as evidence, does not modify)
delegates_to: T3 (human pain); T4 (audience segmentation); T5 (handoffs+audits proliferation); T6 (anchor drift); canonical summary 2799 (synthesis)
owner: claude+rigby
---

# Session 2812 — /docs/research/ Pattern Extraction & Transferability Audit (Group 2700, Thread 2)

> **What this doc is.** T2 primitive extraction — enumerate the transferable primitives that make `/docs/research/` work as a research substrate. Each primitive is scored inline for load-bearing rationale, transferability challenge (where it does NOT fit outside research/), and a per-primitive transferability verdict (WHOLE / CORE-ONLY / REJECT). Every later thread + canonical summary references this taxonomy.
>
> **What this doc is not.** A proposal to apply any primitive elsewhere. A rewrite of DOMAIN_RESEARCH_PLAYBOOK. A recommendation about the target `/docs/` shape. Those belong to T5/T6/canonical summary per parent §4.

---

## 1. Why T2 second

Per parent doc §4:

> T2 — What makes `/docs/research/` work. Reverse-engineer the transferable primitives from `/docs/research/`. **Anti-pattern to actively challenge (Rigby fold 91, mitigatable):** "the /docs/research/ pattern is load-bearing therefore off-limits." T2 must produce CHALLENGE candidates — where does the pattern NOT fit outside `/docs/research/`? Which primitives are load-bearing FOR RESEARCH but wrong for reference/operational/narrative docs?

T2 executes that mandate. It follows T1 (inventory & topology) which measured **what's in** `/docs/`. T2 measures **why the working substrate works** so the canonical summary can distinguish "extend this primitive" from "leave it inside `/docs/research/`."

**Discipline for reading T2:** every primitive has three cells — Load-bearing rationale, Challenge (where it breaks), Transferability verdict. **The verdict is more important than the primitive.** Anyone using T2 to justify "let's put frontmatter everywhere" or "let's number all subdirs xx00-xx99" is misreading; check the challenge cell first.

---

## 2. Anchors T2 cites (never restates)

| Source | What it authoritatively holds | This doc's usage |
|---|---|---|
| [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](../../DOMAIN_RESEARCH_PLAYBOOK.md) v2 | 7-part methodology + 15 formalized areas | Source of primitives being extracted |
| [`docs/research/process/RESEARCH_OPERATING_SYSTEM.md`](../../process/RESEARCH_OPERATING_SYSTEM.md) | 11-class request router + 14-section completion contract | Source of process primitives |
| [`docs/research/ARCHITECTURE_INDEX.md`](../../ARCHITECTURE_INDEX.md) | Library navigation + decision matrix | Source of decision-matrix primitive |
| [`docs/research/OPEN_ARCS.md`](../../OPEN_ARCS.md) | Cross-session arc-state manifest | Source of state-ledger primitive |
| [`docs/research/domains/`](../../domains/) | 14 domain slugs with xx00/xx99/xxNN children | Source of structural + naming primitives |
| Parent doc §2 | 9 arc-wide constraints | T2 respects all |

---

## 3. Enumeration framing

Primitives categorized per Rigby SIGN Q1 AGREE-B: transferability is category-dependent. Some primitives port cleanly (naming/structure); some only port as "core + extensions" (frontmatter); some should often be rejected outside research arcs (process/operational). A flat list would hide those boundary conditions.

**Categories (6):**

- §4 Structural primitives (SP1-SP4)
- §5 Naming primitives (NP1-NP4)
- §6 Frontmatter primitives (FP1-FP7)
- §7 Body primitives (BP1-BP5)
- §8 Process primitives (PP1-PP6)
- §9 Operational primitives (OP1-OP3)

**Verdict scale (per primitive):**

- **WHOLE** — transfers as-is to non-research subdirs
- **CORE-ONLY** — transfers as a pattern; specific implementation must be adapted per audience
- **REJECT** — load-bearing for research but wrong for the target audience; do not extend
- **RESEARCH-ONLY BY DESIGN** — the primitive exists precisely because research arcs need it; extending would break the source domain

**Applicability boundary (per Rigby SIGN Q4 post-authoring edit):** every non-REJECT verdict below carries an implicit applicability boundary. Challenge cells use one of these standard qualifiers when the primitive doesn't extend uniformly across audiences: **"human-authored only"** (excludes autogen), **"excludes runtime anchors"** (does not touch DOC_LIFECYCLE §2b never-move paths), **"requires tooling support"** (extension is safe only if a validator/generator exists), **"safe default not mandate"** (WHOLE-transferable but not a required contract). Downstream authors should re-read the challenge cell before extending any primitive — the verdict alone is insufficient.

**Total primitives: 31 across 6 categories.**

---

## 4. Structural primitives

### SP1 — Namespace docs at `research/` root

- **What:** Three flat namespace docs live at `docs/research/` root (`ARCHITECTURE_INDEX.md`, `DOMAIN_RESEARCH_PLAYBOOK.md`, `OPEN_ARCS.md`) — no subdir owns them because they span all domains.
- **Load-bearing rationale:** Discovery contract. A fresh Claude session reads `ARCHITECTURE_INDEX` to know what exists and `OPEN_ARCS` to know what's in-flight; no subdir walk needed.
- **Challenge:** Would only work outside `research/` if there's a well-defined "spans all subdirs" doc set. For reference docs, per-subject index files (`agents/INDEX.md`) probably serve better than root-level cross-cutting anchors.
- **Verdict: CORE-ONLY.** Extend as "each subject-area subdir may have a small root-index" rather than "put more docs at `docs/` root."

### SP2 — Per-domain slug subdirs (`domains/<slug>/`)

- **What:** 14 domain slugs (`api`, `auth`, `authority_enforcement`, `content`, `docs_restructuring`, `event_integration_architecture`, `frontend`, `human_attention`, `memory`, `observability`, `pa`, `rag_document_loading`, `revenue`, `sports`) each owning their arc docs.
- **Load-bearing rationale:** Clear ownership + colocation of parent + children + summary per domain. Rigby's `search_docs` scoring can boost by slug.
- **Challenge:** Domains here are RESEARCH arcs; the rest of `/docs/` has different partitioning axes (audience, doc type, lifecycle). Copying `domains/` naming outside research would confuse readers about what qualifies as a "domain."
- **Verdict: CORE-ONLY.** Extend as "subject-area subdir per top-level topic" — but use audience-appropriate slugs (e.g. `agents/`, `spiders/`, not `research_domains/`).

### SP3 — Cross-cutting subdirs (`process/`, `platform/`, `implementation/`, `tools/`)

- **What:** Four non-domain subdirs at `research/` root hold cross-cutting content (methodology, platform-scoped audits, IOS implementation, tools).
- **Load-bearing rationale:** Prevents cross-cutting docs from being forced into a wrong domain slug. `RESEARCH_OPERATING_SYSTEM.md` isn't about any one domain; putting it in `domains/api/` would break discovery.
- **Challenge:** These specific subdir names (`process/`, `platform/`) are meaningful in a research context. Outside research, "process" and "platform" have different meanings (Ops? Governance? Runtime?). Not portable as-is.
- **Verdict: REJECT (as verbatim names).** The pattern "have a cross-cutting escape hatch" is CORE-ONLY-transferable, but the specific slug names don't port.

### SP4 — Loose namespace docs at `research/` root (~10 files)

- **What:** ~10 loose docs at `research/` root that aren't in any subdir (e.g. `authority_enforcement_design_space.md`, `platform_architecture_inventory.md`, `symbol_mapping_*.md`, `employee_os_*.md`).
- **Load-bearing rationale:** Author-time convenience — a doc that doesn't clearly belong in `domains/<slug>/` or `platform/` gets a root slot. Fast to author, avoids premature categorization.
- **Challenge:** This IS the sprawl anti-pattern the whole Group 2700 arc exists to solve at `/docs/` scale. Even `research/` accumulates uncategorized loose files (10 is small; if `research/` doubles in size, will still be 10 or will be 40?).
- **Verdict: RESEARCH-ONLY BY DESIGN (with warning).** Small research substrate can tolerate ~10 uncategorized files; at `/docs/` scale this exact pattern produced the 99-loose-file mess T1 measured. Do NOT extend.

### SP5 — Runtime-coupled anchor stability contract (Rigby zoom-out post-authoring Q1a)

- **What:** Some `/docs/` paths are read by Python code at runtime (per `DOC_LIFECYCLE.md` §2b: `docs/canon/INDEX.md`, `docs/governance/SYSTEM_OWNER.md`, `docs/missions/CURRENT_MISSION.md`, `docs/decisions/ADR-*.md`, `docs/ops/`). Others are runtime-count anchors (`docs/PLATFORM_INVENTORY.md`, `docs/INDEX.md`). These obey a DIFFERENT stability/ownership contract than research docs — moving them breaks production or drifts counts silently.
- **Load-bearing rationale:** The stability contract IS what makes them runtime-safe. A research doc gets `verifier_loop:` versioning; a runtime-coupled doc gets a "NEVER MOVE without V2-stub" requirement. Distinct primitive.
- **Challenge:** Research docs and runtime-coupled docs cannot share a single stability/ownership vocabulary. A canonical summary that tries to normalize "all docs use `status:` the same way" will break either research authority chains or runtime consumers.
- **Verdict: CORE-ONLY (applicability boundary: excludes conflating with research-doc stability).** Extend as "each `/docs/` subdir declares its stability contract in a `<subdir>/README.md` or top-level frontmatter field"; do NOT extend research's `authority:` semantics to runtime-coupled docs.

---

## 5. Naming primitives

### NP1 — `xx00` parent-scoping doc per domain

- **What:** Every domain in `domains/<slug>/` has an `xx00_<slug>_domain_scoping.md` that opens the arc. Number range = research-group ID (1300 for memory, 1400 for revenue, 2400 for auth, 2700 for docs restructuring).
- **Load-bearing rationale:** Predictable entry point for reading an arc. Fresh reader knows "start at xx00" without needing an index.
- **Challenge:** Numeric identifiers only make sense when there's a sequence of arcs. Reference docs like `PLATFORM_INVENTORY.md` have no "arc number" concept.
- **Verdict: RESEARCH-ONLY BY DESIGN.** The pattern "predictable entry point per subject area" is CORE-ONLY-transferable (see NP4), but the xx00 numbering is arc-specific.

### NP2 — `xx99` canonical-summary doc per domain (arc close)

- **What:** Every closed arc has an `xx99_<slug>_canonical_summary.md` that consolidates decisions + Migration Queue + provenance.
- **Load-bearing rationale:** Post-arc reader gets one doc that captures the whole arc without re-reading xx00 + all xxNN children.
- **Challenge:** Only meaningful for finite-lifetime work. Reference docs (spider docs, agent docs, autogen outputs) don't have "arc close."
- **Verdict: RESEARCH-ONLY BY DESIGN.** The pattern "single-page summary of a completed project" transfers to ADRs or completed initiatives, not to reference docs.

### NP3 — `xx01-xx98` child doc numbering per domain

- **What:** Child docs numbered `xx01` upward. Some slots labeled `audit`, others `design_prep_audit`, others `design_decision`, etc. — see D-verdict below.
- **Load-bearing rationale:** Preserves authoring order (Q: which came first? A: lower number) + gives Rigby a sortable index.
- **Challenge (from Rigby zoom-out D):** The numbering is an **indexing affordance, not a strict type system**. Child slots can be audits, design preps, bugs, ops notes — the numbering doesn't enforce type. Downstream author who assumes "xx01 = first audit" will be wrong for arcs like Auth 2400 (2401-2404 are audits) vs API 2500 (2501-2504 are `design_prep_audit`).
- **Verdict: RESEARCH-ONLY BY DESIGN (as slot allocator).** The pattern "sortable per-subject sequence" is CORE-ONLY-transferable via date-prefix or ADR-style numbering; the xxNN slot allocation is arc-specific.

### NP4 — `snake_case` slug naming for subdirs

- **What:** `human_attention`, `rag_document_loading`, `docs_restructuring` — all snake_case.
- **Load-bearing rationale:** Filesystem-safe + terminal-tab-completable + consistent with Python module naming (research/ subdir names sometimes appear in code as string constants).
- **Challenge:** Convention mismatch with existing `/docs/` subdirs that use `kebab-case` (`code-review/`, `case-studies/`, `context-packets/`, `pre-launch/`) OR TitleCase (`BUGS/`) OR camelCase-ish (`00-START-HERE/`). No consistent parent-wide convention.
- **Verdict: WHOLE (if `/docs/` picks a convention and migrates).** Snake_case works; kebab-case works. Mixing is the actual anti-pattern. Do not extend snake_case as-is; canonical summary chooses.

---

## 6. Frontmatter primitives

### FP-META — Frontmatter as extensible control-plane header (Rigby zoom-out A)

- **What:** Every research doc opens with a YAML frontmatter block. Stable **core keys** (title/status/authority/session/date) appear on every doc. **Extension keys** (research_group/domain_slug/decisions_locked/verifier_loop/companion_anchors) appear when the doc is part of an arc; **arc-specific keys** (like Auth 2400's inline SIGN-cycle status block) appear when a specific audit needs them.
- **Load-bearing rationale:** The pattern is "stable core + extensible schema," not "one canonical key list." Lets each doc surface what matters without polluting a global schema.
- **Challenge:** Reference docs may not need the whole extension set. Requiring `research_group:` on a spider doc is nonsense. But the CORE (title/status/date/authority) is universally useful. **HARD guardrail (Rigby SIGN post-authoring Q2):** universal-core frontmatter is safe for **human-authored** docs; extending it to **autogen artifacts** (`docs/*_AUDIT.md` batch, `docs/INDEX.md`, `docs/canon/INDEX.md`) or **runtime-coupled paths** (per SP5) will either break the generator OR create the illusion of consistency without the reality. Autogen outputs either (a) skip frontmatter entirely, (b) let the generator write a minimal frontmatter as part of its output template, or (c) live with metadata in a sidecar file — do NOT force human-frontmatter semantics on machine-generated content.
- **Verdict: CORE-ONLY (applicability boundary: human-authored only; excludes autogen; excludes runtime anchors unless the runtime consumer explicitly parses frontmatter).** Extend `title/status/authority/date/last_verified/related` as a **universal core for human-authored docs**; extension keys stay opt-in per doc-type. Highest-leverage primitive T2 identifies, but the applicability boundary is the difference between "clean adoption" and "silent breakage."

### FP1 — `title:` field

- **Load-bearing:** Distinct from filename + supports human-readable titles.
- **Challenge:** None — universal.
- **Verdict: WHOLE.**

### FP2 — `status:` field (`active` / `draft` / `superseded` / `deprecated`)

- **Load-bearing:** `docs/INDEX.md` filters by status. Rigby's `search_docs` deprioritizes superseded.
- **Challenge:** Runtime-coupled docs (`canon/INDEX.md`, `governance/SYSTEM_OWNER.md`) may need additional status vocabulary (`load-bearing-do-not-modify`).
- **Verdict: CORE-ONLY.** Extend the 4-value status enum; extend vocabulary per audience.

### FP3 — `authority:` field

- **Load-bearing:** Distinguishes "parent-doc" from "child-audit" from "process framework." Reader knows what supersedes what.
- **Challenge:** Reference docs don't have supersession relationships in the same way. `authority: reference` would be meaningless in `PLATFORM_INVENTORY`.
- **Verdict: CORE-ONLY.** Extend for docs that CAN supersede each other; not needed for autogen or single-purpose reference docs.

### FP4 — `related:` companion pointers

- **Load-bearing:** Discovery — reader sees "these 5 docs are the neighborhood of this one." Prevents re-searching.
- **Challenge:** Manually maintained. As `/docs/` scales, `related:` lists drift (targets get renamed, deleted). Maintenance cost.
- **Verdict: WHOLE (with tooling caveat).** Extend to all doc types; canonical summary should consider a `related:` link-graph validator command.

### FP5 — `scope:` + `non_goals:` + `owner:` (scope discipline block)

- **Load-bearing:** Prevents scope creep during authoring; explicit hand-offs to other docs; identifies who owns the doc for updates.
- **Challenge:** Overkill for a spider doc that just describes what a spider does. Genuinely load-bearing for scoping docs / audits.
- **Verdict: CORE-ONLY.** Extend for scoping / audit / proposal doc types; not needed for reference.

### FP6 — `verifier_loop:` (multi-line versioning + methodology-drift log)

- **Load-bearing:** Playbook v1→v2 diff visible inline. Reader knows when and why the doc changed.
- **Challenge:** Assumes the doc has a "methodology version." Reference docs and autogen outputs don't; a `verifier_loop` on `AGENTS_REFERENCE.md` would be meaningless.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Do not extend to reference/autogen. Consider extension only for governance docs (playbook, DOC_LIFECYCLE) that have real versioning.

### FP7 — `supersedes:` / `decisions_locked:` (chain-of-authority fields)

- **Load-bearing:** Explicit provenance chain. When multiple versions of a doc exist, `supersedes:` names the predecessor.
- **Challenge:** Reference docs don't chain like this — they get updated in place. Autogen outputs are replaced whole, no chain.
- **Verdict: RESEARCH-ONLY BY DESIGN (mostly).** Chain-of-authority is meaningful for governance docs; extend selectively.

### FP8 — `companion_anchors:` (playbook-only, cross-doc invariant list)

- **What:** `DOMAIN_RESEARCH_PLAYBOOK.md` frontmatter has a `companion_anchors:` block listing 8 anchor docs the playbook expects readers to know.
- **Load-bearing:** Playbook's "these are the always-load docs" contract.
- **Challenge:** Only meaningful for a doc that governs many other docs. Most reference docs don't need this.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Do not extend broadly.

---

## 7. Body primitives

### BP1 — "> What this doc is." + "> What this doc is not." framing block

- **What:** Every parent-scoping and canonical-summary doc opens with an explicit is/is-not block above the fold.
- **Load-bearing rationale:** Reader knows in 30 seconds whether this doc will answer their question. Prevents re-reading.
- **Challenge:** Overkill for a spider doc that's obviously "here's what this spider does." Load-bearing for anything with scope ambiguity.
- **Verdict: CORE-ONLY.** Extend for docs where "what this is" isn't obvious from the filename alone.

### BP2 — Numbered § sections with descriptive titles

- **What:** `§1 Why Phase 0`, `§2 What existing inventory tells us`, etc. — not `Introduction`, `Background`.
- **Load-bearing rationale:** Table-of-contents readability + section citation (e.g. "per parent §4 T2").
- **Challenge:** None — universal.
- **Verdict: WHOLE.**

### BP3 — Chris's exact wording as quoted evidence

- **What:** When a decision comes from Chris, quote his exact wording in a block quote with attribution.
- **Load-bearing rationale:** Removes interpretation ambiguity. Future reader (or self) can't drift from "what Chris said" if it's quoted verbatim.
- **Challenge:** Requires a single stakeholder. Multi-stakeholder docs would need attribution per quote, which gets noisy.
- **Verdict: RESEARCH-ONLY BY DESIGN (single-stakeholder assumption).** For multi-stakeholder docs, attribute all decisions but don't over-quote.

### BP4 — Cross-reference by session number + § anchor (`S1273 §3.13`)

- **What:** In-body cite pattern like `per S1273 §3.13` or `per Rigby fold 91` — session number + section anchor.
- **Load-bearing rationale:** Precise + stable citation. Reader can `grep` for the referent.
- **Challenge:** Assumes reader has access to the referenced session context. New reader may need to look up S1273 first.
- **Verdict: CORE-ONLY.** Extend by pairing session-cite with hyperlink to the source doc.

### BP5 — Explicit epistemic labeling + re-verify-at-HEAD discipline (Rigby zoom-out B)

- **What:** Docs mark counts/claims as of specific SHA + require re-verification at read time. Parent 2700 §3 cites "2618 docs at S2800"; T1 measured 3201 at S2811; drift documented not suppressed.
- **Load-bearing rationale:** Prevents research docs from becoming stale silent-truth. Reader knows the count was true THEN, not necessarily NOW.
- **Challenge:** Autogen outputs handle staleness by regenerating whole. Reference docs may want live-truth (via `<!-- DOC-AUTOGEN -->` markers).
- **Verdict: CORE-ONLY.** Extend as "any doc citing counts includes a timestamp + verifier command." Universal principle; implementation varies by doc type.

---

## 8. Process primitives

### PP1 — Parent-with-children arc shape

- **What:** Multi-subsystem domains open a parent scoping doc (xx00) + Chris picks scope + child audits get authored (xx01-xx98) + arc closes with canonical summary (xx99). Group 1300 memory made the pattern explicit.
- **Load-bearing rationale:** Prevents single-audit sprawl when a domain has 4+ subsystems that need their own analysis.
- **Challenge:** Reference doc updates don't have "arcs." Applying this shape to reference maintenance would be ceremony.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Extend only when a domain has multi-subsystem scope that needs partitioning.

### PP2 — Research → design preparation → design decision → implementation phase separation

- **What:** Symbol Mapping arc proved this: an arc has research phase, design-prep phase, design-decision phase, implementation phase. Each phase gets its own doc(s).
- **Load-bearing rationale:** Explicit phase boundaries prevent conflating "we don't know yet" with "we've decided."
- **Challenge:** Reference docs and autogen outputs don't have phases. Applying phase-separation to a spider doc would be nonsense.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Extend to ADRs / initiatives / long-running features; NOT to reference or autogen.

### PP3 — Playbook §9 28 canonical questions template

- **What:** DOMAIN_RESEARCH_PLAYBOOK §9 lists 28 canonical questions every arc audit should answer (adapted where inapplicable, e.g. T1 answered Q1-Q12 and marked Q13-Q28 as future-thread).
- **Load-bearing rationale:** Prevents "what should the audit cover?" drift. Author picks from a stable checklist.
- **Challenge:** The 28 questions are designed for domain audits. Applying them to reference doc updates would be waste.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Extend to any audit-shape work; NOT to reference maintenance.

### PP4 — Rigby joint SIGN cycle (with anti-rubber-stamp check)

- **What:** Every scope decision routes through Rigby via PA chat with tool-grounded framing; `tool_runs` must be non-empty on reply (anti-rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign`). Multiple cycles per audit doc (open + post-authoring — S2811 lesson).
- **Load-bearing rationale:** Second-order review by an agent with access to different tools (repo_tool, scheduled_tasks_tool, diagnostics_tool). Catches errors human-Claude misses.
- **Challenge:** SIGN adds latency to every scope decision. Overkill for reference doc updates that don't have scope decisions.
- **Verdict: RESEARCH-ONLY BY DESIGN (as ceremony).** The underlying "second-order review" principle is CORE-ONLY-transferable to any high-stakes decision; the SIGN mechanics are arc-specific.

### PP5 — SIGN isolation-pin discipline as first-class process artifact (Rigby zoom-out C)

- **What:** Auth 2400 parent doc explicitly names `pa-32400781523b4d5b` as its dedicated fresh isolation pin; retired via `session_tool.retire` at cycle close. Playbook §15 codifies this as SIGN-isolation discipline.
- **Load-bearing rationale:** Prevents SIGN context bleed between arcs — a fresh Rigby thread can't accidentally reference prior arc's folds.
- **Challenge:** Compliance overhead. Forcing every doc change to use a fresh SIGN pin would slow ops iteration.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Do not extend to non-SIGN work. Recognize as a research-arc primitive.

### PP6 — OPEN_ARCS as narrative state ledger (Rigby zoom-out E)

- **What:** `OPEN_ARCS.md` tracks in-flight research arcs — current snapshot at top + preserved prior snapshots as it evolves.
- **Load-bearing rationale:** Cross-session state visibility. Fresh Claude session at S2812 open can see "Group 2700 in flight, T1 shipped, T2 next" without reading 12 handoffs.
- **Challenge:** Reference docs should be **current-state-only** — no historical snapshot preservation. Extending OPEN_ARCS shape to reference docs would balloon their size.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Extend the "cross-session state ledger" pattern to arc/initiative tracking; do NOT extend to reference docs.

---

## 9. Operational primitives

### OP1 — Chris short commands (`Start research group NNNN: <topic>` / `Continue research group NNNN: <slot>` / `Close research group NNNN`)

- **What:** Predictable command grammar Chris uses to open/continue/close arcs. Fires the corresponding startup contract per Research OS §5.
- **Load-bearing rationale:** Reduces open-ceremony friction. Chris types 6 words; agent runs a whole session-open sequence.
- **Challenge:** Only works if there's a corresponding operational contract. Reference doc updates don't need a start-command grammar.
- **Verdict: RESEARCH-ONLY BY DESIGN.** Do not extend as a general grammar.

### OP2 — ARCHITECTURE_INDEX §7 decision matrix (route by intent)

- **What:** ARCHITECTURE_INDEX has a decision matrix that routes a reader "I want to X → read Y." Bootstrap-once, decide-fast.
- **Load-bearing rationale:** Removes browsing-vs-searching cost. Reader with a specific intent finds the target doc in one hop.
- **Challenge:** Requires a defined intent taxonomy. Ad-hoc doc collections don't have intents to route by.
- **Verdict: CORE-ONLY.** Extend as "top-level subdirs may have their own decision matrix in `<subdir>/INDEX.md`" — canonical summary decides.

### OP3 — Two SIGN cycles per audit doc (open-scope + post-authoring, S2811 lesson)

- **What:** New pattern proven at S2811 T1: SIGN once at open (scope shape) + SIGN again post-authoring (factual accuracy + coverage + zoom-out risk). Post-authoring SIGN caught the `docs/18960/` ghost at S2811.
- **Load-bearing rationale:** Author-Claude blind spots differ from framing-Claude blind spots. Second SIGN catches what open SIGN's scope-focus misses.
- **Challenge:** Adds a full SIGN cycle latency per doc. Overkill for non-audit content.
- **Verdict: RESEARCH-ONLY BY DESIGN (currently).** Watch for 3+ triggers before Playbook amendment; if consistent value across T2-T6, promote to Playbook v0.9. **S2812 update:** T2 post-authoring SIGN caught 2 missing primitives (SP5, OP4) + FP-META guardrail gap — second trigger observed. One more (T3 authoring) needed before amendment consideration.

### OP4 — Registration/visibility mechanics (Rigby zoom-out post-authoring Q1b)

- **What:** A doc becomes "discoverable" by being registered in one of: (a) `ARCHITECTURE_INDEX.md` §7 decision matrix (research), (b) `docs/INDEX.md` auto-generated corpus index (all), (c) `search_docs` RAG corpus (all embedded), (d) `companion_anchors:` frontmatter reference from a governance doc, (e) `related:` reference from any doc in scope. **Unregistered docs are effectively invisible** — even if the file exists at a known path, Rigby cannot find it via `search_docs`, and fresh Claude sessions won't navigate to it without an explicit pointer.
- **Load-bearing rationale:** Discoverability is not automatic — it's a substrate action. Every research doc lands in `ARCHITECTURE_INDEX` at close-cascade time; every doc lands in `docs/INDEX.md` via `build_docs_index`; every embedded doc lands in RAG via the 4-step docs cascade. Skipping any of these makes the doc a ghost.
- **Challenge:** The specific registration paths are `/docs/`-scoped. External docs (external URLs, private notes, personal memory files) live outside this substrate and have their own visibility mechanics. Also — heavy registration ceremony discourages small ephemeral docs; if every scratch note needs INDEX + RAG registration, authors will skip authoring altogether.
- **Verdict: CORE-ONLY (applicability boundary: requires tooling support).** The registration/visibility principle IS universal — every doc that matters must be discoverable. But the specific mechanics (ARCHITECTURE_INDEX bump, INDEX cascade, RAG embed) are `/docs/`-scoped. Canonical summary should ensure per-doc-type registration paths are explicit; extending "you must be in ARCHITECTURE_INDEX" to reference docs would break the substrate that keeps research navigable.

---

## 10. Playbook §9 canonical questions (adapted to T2 scope)

Per parent §4, T2 adapts the 28 questions where extraction-scope makes a question inapplicable:

| Q# | Question (adapted) | T2 answer |
|---|---|---|
| Q1 | How many primitives were enumerated? | 31 across 6 categories (§4-§9) — added SP5 (runtime-coupled anchor stability contract) + OP4 (registration/visibility mechanics) at post-authoring SIGN |
| Q2 | How many are WHOLE-transferable? | 5-6 (NP4, FP1, FP2, FP4, BP2, with FP4 carrying a "tooling caveat") |
| Q3 | How many are CORE-ONLY? | ~15 (SP1, SP2, SP5, FP-META, FP3, FP5, BP1, BP3, BP4, BP5, PP4 partial, OP2, OP4) |
| Q4 | How many are REJECT or RESEARCH-ONLY BY DESIGN? | ~10 (SP3, SP4, NP1, NP2, NP3, FP6, FP7, FP8, PP1-PP6 partial, OP1, OP3) |
| Q5 | What's the highest-leverage transferable primitive? | FP-META (frontmatter as extensible control-plane header) + FP1/FP2/FP4 (title/status/related as universal core). Every doc could adopt these tomorrow. |
| Q6 | What's the biggest "load-bearing but wrong outside research" trap? | Numbering (NP1-NP3). Copying xx00/xx99 or xxNN slots outside research would break the pattern by disconnecting it from arc semantics. |
| Q7 | Which primitive is BOTH universally applicable AND currently under-adopted? | BP5 (epistemic labeling + re-verify-at-HEAD). T1 practiced it; most non-research docs don't. Canonical summary should consider making this universal. |
| Q8 | What primitive is emergent (not yet in the playbook)? | OP3 (two SIGN cycles per audit doc). Only 1 trigger so far (S2811); needs 2+ more before Playbook amendment per Chris's four-trigger threshold. |
| Q9 | What primitives are Rigby-side (not visible from repo alone)? | PP4-PP6 (SIGN mechanics + isolation pin + OPEN_ARCS). Extraction required Rigby's tool_runs to surface. |
| Q10-Q28 | Application to specific `/docs/` subdirs; migration ordering; canon expansion; audience segmentation; discoverability trace | **Out of T2 scope** — T3/T4/T5/T6/canonical summary owns |

---

## 11. Migration Queue (post-arc)

Per parent §5. T2 items are **structural insights**, not restructuring proposals. **Severity: informational.**

| # | Item | Evidence source (this doc) | Severity | Notes for migration session |
|---|---|---|---|---|
| MQ-T2-1 | FP-META extension: adopt universal core frontmatter (`title/status/authority/date/last_verified/related`) across **human-authored** `/docs/` docs; EXCLUDE autogen (`docs/*_AUDIT.md` batch, `docs/INDEX.md`, `docs/canon/INDEX.md`) and EXCLUDE runtime-coupled paths (per SP5 + DOC_LIFECYCLE §2b) unless their runtime consumer explicitly parses frontmatter | §6 FP-META + SP5 challenge | INFORMATIONAL | Highest-leverage primitive. Canonical summary decides scope + tooling (linter/validator). **HARD guardrail:** do NOT force frontmatter on machine-generated content — either skip, let generator write minimal, or use sidecar file. |
| MQ-T2-2 | BP5 extension: add epistemic labeling + re-verify command to any doc citing counts | §7 BP5 | INFORMATIONAL | Universal principle; implementation varies by doc type (autogen vs handwritten). |
| MQ-T2-3 | SP1 caveat: do NOT put more docs at `docs/` root — subject-area index files (`agents/INDEX.md`) instead | §4 SP1 challenge | INFORMATIONAL | Directly contradicts a naïve "extend the pattern" reading. Explicit anti-pattern for canonical summary. |
| MQ-T2-4 | NP4 caveat: `/docs/` has 3 naming conventions (snake_case / kebab-case / TitleCase); pick one + migrate | §5 NP4 challenge | INFORMATIONAL | Canonical summary picks; migration session executes. |
| MQ-T2-5 | OP2 extension: top-level subdirs get their own decision matrix `<subdir>/INDEX.md` if content justifies | §9 OP2 | INFORMATIONAL | Per-subdir; not mandatory. |
| MQ-T2-6 | OP3 elevation: if 2 more sessions confirm two-SIGN-per-audit pattern value, promote to Playbook v0.9 | §9 OP3 | INFORMATIONAL | Chris four-trigger threshold; do NOT propose amendment until S2814+ if pattern holds. |
| MQ-T2-7 | Primitives explicitly OFF-LIMITS for non-research-arc **verbatim** extension: PP1-PP6, OP1, OP3, NP1-NP3, FP6-FP8, SP3-SP4 (13 primitives). **Clarification per Rigby SIGN post-authoring Q3:** the underlying CONCEPTS may transfer even when MECHANISMS do not — e.g., BP1 (What-this-doc-is/is-not framing) generalizes the "explicit scope framing" idea from PP2 phase separation; BP5 (epistemic labeling) generalizes the "verifier loop" idea from FP6. Extract IDEAS, reject MECHANISMS. | §4-§9 REJECT/RESEARCH-ONLY verdicts | INFORMATIONAL | Anti-scope guardrail — canonical summary must not accidentally extend research MECHANISMS (SIGN pin discipline, xx00/xx99 numbering, 28-question template) even when the underlying IDEA (second-order review, predictable entry point, comprehensive coverage) is universal. |

---

## 12. What T2 does NOT resolve (explicit hand-offs)

Per parent §4 anti-scope:

| Question | Handed off to |
|---|---|
| Which specific `/docs/` subdirs should adopt FP-META core frontmatter? | Canonical summary at 2799 |
| What's the migration order for extending the ~5-6 WHOLE + ~14 CORE-ONLY primitives? | Canonical summary at 2799 |
| Which existing loose root files at `docs/` root would benefit from `topics/`-style consolidation? | T3 (human pain) + T5 (handoffs+audits) |
| Which audience (Claude / Rigby / Chris / all) benefits most from each primitive? | T4 (audience segmentation) |
| How do we reconcile the 4 audit surfaces (audit / audit-2026 / audits / loose *AUDIT.md) with T2 primitives? | T5 (handoffs+audits proliferation) |
| Which duplicated rules across playbook / CLAUDE.md / memory drift, and how does this relate to FP-META extensibility? | T6 (anchor drift) |
| Playbook v0.9 amendment for two-SIGN-per-audit (OP3) | Deferred — needs 2+ more triggers |
| Whether SP3 subdir names (`process/`, `platform/`) should be RENAMED for `docs/`-wide clarity | Canonical summary at 2799 |

---

## 13. Provenance

**Session:** S2812 (2026-07-18, mid-afternoon, immediately post-S2811-close)
**Ratifier:** Chris D-verdict "let's start T2" at S2812 open
**Git HEAD at authoring:** `152c69c7bdba` (S2811 close cascade)
**Rigby SIGN cycles (TWO per S2811 lesson OP3):**

Open SIGN (Q1 enumeration framing / Q2 challenge encoding / Q3 zoom-out missing primitives). AGREE-B on Q1, AGREE-(i) on Q2, AGREE-with-additions on Q3. Anti-rubber-stamp check PASSED — tool_runs included `repo_tool.tree` for `research/domains/` depth-3 + `repo_tool.read_file` on memory 1300 + revenue 1400 + auth 2400 parents + OPEN_ARCS.md.

Post-authoring pressure-test SIGN (Q1 primitive completeness / Q2 verdict calibration / Q3 MQ integrity / Q4 verdict-scale calibration). AGREE-WITH-EDITS on all 4. Anti-rubber-stamp check PASSED — tool_runs re-read T2 body + `DOMAIN_RESEARCH_PLAYBOOK.md` + `RESEARCH_OPERATING_SYSTEM.md` + `api/2500_api_domain_scoping.md` + `MQ-T2-7` line lookup.

**Rigby open-SIGN zoom-out additions folded (5 primitives originally missed):**
- **A** → FP-META (frontmatter as extensible control-plane header; the primitive is the pattern, not the key list)
- **B** → BP5 (explicit epistemic labeling + re-verify-at-HEAD discipline)
- **C** → PP5 (SIGN isolation-pin discipline as first-class process artifact)
- **D** → NP3 challenge cell strengthened (xx01-xx98 is indexing affordance, not strict type system)
- **E** → PP6 (OPEN_ARCS as narrative state ledger)

**Rigby post-authoring SIGN additions folded (2 more primitives + 3 guardrail tightenings):**
- **Q1a** → SP5 (runtime-coupled anchor stability contract — distinct stability/ownership vocabulary from research docs)
- **Q1b** → OP4 (registration/visibility mechanics — ARCHITECTURE_INDEX bump + `build_docs_index` + RAG embed as substrate action; unregistered = invisible)
- **Q2** → FP-META challenge cell + MQ-T2-1 hardened with "human-authored only; excludes autogen; excludes runtime anchors" applicability boundary (prevents silent breakage of `docs/*_AUDIT.md` autogen batch + `docs/INDEX.md` + runtime-coupled paths)
- **Q3** → MQ-T2-7 clarified: OFF-LIMITS applies to MECHANISMS not CONCEPTS. Underlying ideas (second-order review, predictable entry point) may transfer even when specific implementations (SIGN pin, xx00 numbering) do not.
- **Q4** → §3 verdict scale gained "applicability boundary" language — challenge cells use standard qualifiers (human-authored only / excludes autogen / excludes runtime anchors / requires tooling / safe default not mandate)

**Second-trigger observation for OP3 (two-SIGN-per-audit pattern):** T2 post-authoring SIGN caught 2 missing primitives + 3 substantive guardrails that open-SIGN did not surface. Value confirmed; pattern held at S2811 (`docs/18960/` ghost catch) and now S2812. **One more consistent trigger (T3 or T4 authoring) satisfies the pattern's promotion threshold** to Playbook v0.9 amendment consideration.

**Anchor-verify catches this session:**
1. `research/` root has ~10 loose docs (SP4) — same sprawl pattern the whole arc exists to solve, at smaller scale. Documented as challenge, not extended.
2. Naming convention mismatch across `/docs/` — snake_case (research), kebab-case (code-review), TitleCase (BUGS), numeric-prefix (00-START-HERE). Documented; canonical summary picks.

**Tools used:**
- `ls docs/research/` + `find docs/research/domains -maxdepth 2 -name "??00_*.md"` for structural + naming enumeration
- `head -25 <file>` for frontmatter primitive extraction
- `wc -l <file>` for LOC context
- Rigby `repo_tool` for cross-verification of 14 slug list + xx00 exemplars across 3 arcs

**T2 does not embed live counts** — primitives are stable across git HEAD; only counts of primitives-per-category are timestamped at authoring. Regeneration by re-running the primitive enumeration (deterministic given source docs).

---

**End of T2 — Research pattern extraction. T3 (`2703_docs_human_user_pain_points_audit.md`) opens next in the audit sequence.**

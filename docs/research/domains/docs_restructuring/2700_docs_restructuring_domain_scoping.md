---
title: "S2801 /docs/ Restructuring — Parent Architecture Scoping (Group 2700 mission plan)"
status: active (parent — Chris decisions locked 2026-07-16)
authority: parent-doc for Group 2700 research arc
session: 2801
date: 2026-07-16
decisions_locked: 2026-07-16
domain_slug: docs_restructuring
research_group: 2700
authors: Claude Code (Chris directed at S2800 close)
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md              # process framework (S1274/S1276)
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md    # session-open OS the arc uses on itself
  - docs/research/domains/memory/1300_memory_domain_scoping.md  # parent-scoping exemplar
  - docs/research/OPEN_ARCS.md                              # arc-state manifest
  - docs/research/ARCHITECTURE_INDEX.md                     # library navigation
  - docs/00-START-HERE/DOC_LIFECYCLE.md                    # §2b runtime-coupled + §2c sole-counts-source + §3 root-stability
  - docs/canon/INDEX.md                                     # canon registry (10-doc cap)
  - docs/PLATFORM_INVENTORY.md                             # runtime anchor (regenerable)
  - docs/PLATFORM_WHAT_IT_IS.md                            # narrative anchor
  - docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md   # prior /docs/ audit + move discipline
  - CLAUDE.md                                               # repo bootstrap + Rigby collaboration protocol
  - 00-START-NEXT-SESSION.md                                # session-scoped state
scope: Phase 0 domain-scoping — design proposal + migration plan for the u-d-b `/docs/` corpus using the `/docs/research/` pattern as the audit apparatus
non_goals:
  - the audits themselves (Threads 1-6 own those)
  - answering the 28 playbook questions (T1-T6 own those, adapted)
  - any file moves, deletions, or renames during the arc
  - any code changes during the arc
  - redesigning DOC_LIFECYCLE §2b/§2c/§3 constraints (arc designs UNDER them, not around them)
  - migration execution (post-arc-close, separate sessions)
delegates_to: none
owner: claude+rigby (Chris ratified 6-thread package at S2801 open 2026-07-16)
---

# Session 2801 — /docs/ Restructuring Domain Scoping (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any child audit begins. Chris ratified at S2800 close: `"Before we do anything else I want you and Rigby to do a deep audit of the /docs/."` Ratified shape: parent-scoped research arc using the `/docs/research/` pattern as the audit apparatus on `/docs/` itself. This doc names the arc's charter — six threads, non-goals, existing constraints honored, canonical-summary slot.
>
> **What this doc is not.** The audits themselves (T1-T6 own those). A rewrite proposal. A recommendation about *how* `/docs/` should be organized. Everything here is scoping.

---

## 1. Why Phase 0

Chris's exact directive at S2800 close (2026-07-16):

> Before we do anything else I want you and Rigby to do a deep audit of the /docs/.

Follow-on ratification at S2801 open:

- **Research/audit, NOT implementation.** Chris: `"I don't want this to be a session of work we are doing but it's something we need to do."` Deliverable = design proposal + migration plan. No file moves, no code changes during the arc.
- **Fresh session; parent-scoping through Rigby.** Ratified 6-thread package via joint Claude+Rigby SIGN → Chris D-verdict "go ahead with the 6-thread package" at S2801 T1.

The arc exists because `/docs/` has grown organically to a scale where fresh-Claude discoverability breaks:

- **2618 docs indexed** at S2800 cascade output (1443 active / 11 draft / 1733 superseded)
- **676+ handoff docs** in `docs/handoffs/`
- **Growing `docs/audits/`** cruft — 19 `SESSION_819_SYSTEM_AUDIT_*` files currently untracked at S2801 open
- **Duplicated governance surfaces** — SIGN mechanics, pin rotation, anchor discipline copied across playbook / `00-START-NEXT-SESSION.md` / memory rules / `DOC_LIFECYCLE.md` §2c / `ARCHITECTURE_INDEX §6.6` (per Rigby fold 90, evidence: `docs/research/process/claude_research_startup_introspection.md#12`)
- **`docs/research/` works well** as a research substrate; `/docs/` overall does not exhibit the same structure — the arc reverse-engineers what transferred

---

## 2. Existing constraints we honor (Cycle 1A verify-before-build)

Per Rigby fold 93 (`same_pr_actionable`) — end-state constraints already exist. Arc DESIGN operates UNDER them, not around them:

| Constraint | Source | What it locks |
|---|---|---|
| Sole authoritative counts | `DOC_LIFECYCLE.md` §2c | `PLATFORM_INVENTORY.md` + `docs/INDEX.md` are the ONLY counts sources. Never duplicate agent/spider/task/model counts elsewhere. |
| Runtime-coupled paths (NEVER MOVE) | `DOC_LIFECYCLE.md` §2b | `docs/canon/INDEX.md`, `docs/governance/SYSTEM_OWNER.md`, `docs/missions/CURRENT_MISSION.md`, `docs/decisions/ADR-*.md`, `docs/ops/` are read by Python at runtime. Even a "harmless" subdir move breaks production. |
| Root-stability | `DOC_LIFECYCLE.md` §3 | Anything referenced by `CLAUDE.md` / `00-START-NEXT-SESSION.md` / any `*_AUDIT.md` MUST stay at cited path or leave a permanent V2 stub. |
| Canon size | `docs/canon/INDEX.md` | Canon is intentionally ≤10 docs. Restructuring must not inflate canon. |
| Context-kit scope boundary | `DOC_LIFECYCLE.md` §0 | `docs/docs-pattern/` is context-kit framework, excluded from u-d-b instance restructuring. |
| DOC-POINTER-V1 / V2 pointer headers | `DOC_LIFECYCLE.md` §1 | Any relocation in follow-on migration sessions uses V2 stubs; any stats-drifting doc gets V1 banner. |
| Autogen docs are not hand-edited | Various | Files with `<!-- DOC-AUTOGEN -->` are regenerable — restructuring proposals name the generator, not the output. |
| Twin-pointer discipline | Memory `feedback_twin_deliverable_at_every_ratification` | Arc-close canonical summary needs both repo doc + workspace deliverable mirror. |
| Playbook v0.8.0 governance | `docs/ENGINEERING_PLAYBOOK.md` | PLAYBOOK-6.10.7 (zoom-out ask), 6.10.8 (fold-before-D-verdict), 6.10.9 (evidence admission), 7.4.4 (recycle-after-merge) apply to every SIGN cycle in the arc. |

Arc scope is **DESIGN of restructuring under these constraints, not redesign of the constraints themselves.** Any proposal that violates one of these rows is out-of-scope and must be re-shaped to comply, or explicitly escalated to Chris as a constraint-modification proposal (separate arc).

---

## 3. Baseline evidence — what `/docs/` looks like at arc open

**S2800 cascade output (2026-07-16):**

- 2618 docs indexed by `build_docs_index`
- 1443 active / 11 draft / 1733 superseded
- 676+ handoffs in `docs/handoffs/`
- `docs/audits/` growing (19 `SESSION_819_SYSTEM_AUDIT_*` files untracked at S2801 open — cruft candidate but defer per §7 anti-scope)

**Docs subsystem shape (from `docs/topics/` narrative + PLATFORM_INVENTORY per DOC_LIFECYCLE §2c):**

- Anchors: `PLATFORM_WHAT_IT_IS.md` (narrative), `PLATFORM_INVENTORY.md` (runtime-derived; authoritative counts)
- Behavior/translation layers: `UDB_BEHAVIOR_LAYER.md`, `UDB_TRANSLATION_LAYER.md`, `KNOWLEDGE_PIPELINE.md`
- Runtime-coupled load-bearing (never-move list): 5 rows per `DOC_LIFECYCLE.md` §2b
- Canon: 7 rows in `docs/canon/INDEX.md` Registry (under the ≤10 cap)
- Research library: `docs/research/` with the pattern this arc dogfoods
- Topic docs: `docs/topics/*` (embedding-optimized subsystem narratives; some drift from PLATFORM_INVENTORY per §2c)
- Historical: `docs/handoffs/`, `docs/audits/`, `docs/audit-2026/`, `docs/archive/`

**Prior /docs/ audit context:** `docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md` locked DOC_LIFECYCLE.md conventions during a corpus walk-through (2026-05-24). This arc extends the S1143 discipline forward with a full-scope audit; it does not redo S1143's lock.

---

## 4. Thread taxonomy (Chris-locked 6-thread package)

Six threads. Each is a child audit at `2701..2706`. Canonical summary at `2799`. Playbook §9's 28 canonical questions apply, adapted where the child scope makes a question inapplicable.

### T1 — Inventory & topology (`2701_docs_inventory_topology_audit.md`)

- **Scope:** what's IN `/docs/` (dir tree, file counts, auto-gen vs hand-written distribution, freshness histogram, size distribution, subdir purpose taxonomy).
- **Deliverable:** ground-truth inventory that later threads reference. First to run.
- **Anti-duplicate:** cite `PLATFORM_INVENTORY.md` for runtime counts (never restate); cite `docs/INDEX.md` for corpus counts.
- **Explicitly out:** any judgment on what should MOVE — that's T5/T6's job. T1 measures.

### T2 — What makes `/docs/research/` work (`2702_docs_research_pattern_extraction_audit.md`)

- **Scope:** reverse-engineer the transferable primitives from `/docs/research/`: `RESEARCH_OPERATING_SYSTEM.md`, `OPEN_ARCS.md` manifest, `ARCHITECTURE_INDEX.md` decision matrix, `DOMAIN_RESEARCH_PLAYBOOK.md`, xx00 parent-scoping / xx99 canonical-summary shape, per-domain slugs, `verifier_loop:` frontmatter.
- **Deliverable:** enumerated list of primitives + evidence for why each one carries load + which are candidate for extension to the rest of `/docs/`.
- **Anti-pattern to actively challenge (Rigby fold 91, mitigatable):** "the /docs/research/ pattern is load-bearing therefore off-limits." T2 must produce CHALLENGE candidates — where does the pattern NOT fit outside `/docs/research/`? Which primitives are load-bearing FOR RESEARCH but wrong for reference/operational/narrative docs?
- **Explicitly out:** applying the primitives to the rest of `/docs/` — that's the canonical summary's synthesis. T2 extracts + challenges only.

### T3 — Human-user pain points (`2703_docs_human_user_pain_points_audit.md`)

- **Scope:** where discoverability breaks for Chris (single human user in single-user pre-prod per `project_single_user_pre_prod_operating_context`) and for fresh-Claude sessions. Chris/Claude/Rigby workflow friction. Convention collisions across `DOC_LIFECYCLE` / `PLATFORM_WHAT_IT_IS` / `CLAUDE.md` / `docs/topics/`.
- **Method:** trace concrete user journeys (a) "Chris asks 'where do I see X?'" (b) "fresh Claude asked to fix Y" (c) "Rigby asked to search for Z"; measure how many hops until they land on the right doc.
- **Deliverable:** ranked pain catalog + concrete-scenario evidence.
- **Explicitly out:** audience segmentation (that's T4).

### T4 — Audience segmentation (`2704_docs_audience_segmentation_audit.md`)

- **Scope:** classify every `/docs/` file by primary audience — load-bearing-for-Rigby (search_docs corpus + tool-context) vs Claude-only (session bootstrap + CLAUDE.md graph) vs human-only (Chris reading in a browser) vs multi-audience.
- **Method:** cross-reference `search_docs` corpus + `docs_context_builder.py` reads + CLAUDE.md graph + PLATFORM_WHAT_IT_IS narrative surface.
- **Deliverable:** matrix — file × audience × surface-it-appears-on — plus counts by audience segment.
- **Why separate from T3:** T3 measures pain; T4 measures WHO the doc is for. Different questions; both feed the canonical summary's restructuring proposal.
- **Explicitly out:** proposing new segments — describe what exists.

### T5 — Handoffs + audits proliferation (`2705_docs_handoffs_audits_proliferation_audit.md`)

- **Scope:** 676+ handoffs + growing `docs/audits/` + `docs/audit-2026/` (April historical) + `docs/archive/`. Write-once-read-rarely triage. Should handoffs age out to archive? What's the read-rate on `SESSION_NNNN_*` files older than N sessions? What's the citation-graph? Do any handoffs get cited months later (load-bearing) vs never-again?
- **Method:** grep the corpus for handoff citations; measure decay curve; classify handoff files by "cited later" vs "never cited after own session."
- **Deliverable:** proposal for handoff lifecycle (with severity tags: keep-in-place / archive-after-N / eligible-for-deletion), NOT executed during arc (per §7).
- **Substrate integrity check (Rigby fold 92, future_trigger):** handoffs previously mass-moved and chunk IDs reset per `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8`. T5 MUST include a 10-doc citation-integrity spot-check — do old `[docs/handoffs/SESSION_NNN.md#K]` citations still resolve to the intended chunk? If not, migration must include an identity-stabilization step BEFORE any further moves.

### T6 — Anchor & drift audit (`2706_docs_anchor_drift_audit.md`)

- **Scope:** identify duplicated rules across playbook / `00-START-NEXT-SESSION` / memory / `DOC_LIFECYCLE.md` §2c / `ARCHITECTURE_INDEX §6.6` — SIGN mechanics, fresh isolation pin instructions, anchor discipline (inventory-wins-on-conflict), pin rotation policy, close-cascade steps. Measure the drift risk on each.
- **Method:** grep + fingerprint each rule statement across surfaces; classify (a) identical / (b) drifted-but-compatible / (c) drifted-and-inconsistent.
- **Deliverable:** rule-inventory table + drift severity + single-source-of-truth proposal per rule.
- **Ties to Rigby fold 90 (mitigatable):** SIGN mechanics 3-copy drift already documented. T6 quantifies scope; canonical summary proposes fix.

### `2799` — Canonical summary (arc close)

- **Scope:** cross-cutting synthesis + ratified restructuring plan + migration queue.
- **Deliverable:** the ratified `/docs/` restructuring proposal, twinned as a workspace deliverable per `feedback_twin_deliverable_at_every_ratification`.
- **Ship shape:** migration executes in follow-up sessions, NOT during this arc.

---

## 5. Non-goals discipline (hard-line defer)

Per §7 anti-scope + Rigby fold on ASK 4:

- **NO file moves during arc.** Even obvious cruft (`SESSION_819_SYSTEM_AUDIT_*` 19-file backlog) stays in place. Note + defer.
- **NO deletions during arc.** Same rule.
- **NO renames during arc.** Same rule.
- **NO code changes during arc.** No `manage.py` command changes, no `docs_context_builder.py` edits, no `search_docs` corpus rebuilds triggered by arc discoveries (regular close-cascade runs are fine, but not arc-driven rebuilds).
- **Each child audit ships a `## Migration Queue (post-arc)` section** — severity + exact paths + rationale for the follow-on migration session to consume.
- **PLAYBOOK-6.10.8 discipline preserved:** in-arc zoom-out folds MAY classify as `same_pr_mitigatable` for the CHILD DOC (e.g. "rephrase §3 to cite T1 not restate"), never for `/docs/` file moves.

---

## 6. Recorded decisions (Chris-locked 2026-07-16)

| # | Decision | Rationale |
|---|---|---|
| D1 | Parent-with-children arc, not single audit | Scope is 2618-doc corpus + 676+ handoffs; multi-thread required |
| D2 | Arc group number = `2700` | Next-unused-integer per playbook analogy; do not consume `2300` (Mobile hole) |
| D3 | Folder = `docs/research/domains/docs_restructuring/` | Matches existing NNxx domains convention; `docs/research/platform/` uses named docs (no NNxx numbering) |
| D4 | 6 threads (T1 inventory / T2 pattern-extraction / T3 human-pain / T4 audience-segmentation / T5 handoffs-audits / T6 anchor-drift) | Rigby split original T3, added T6 anchor-drift; joint recommendation ratified |
| D5 | Non-goals hard-line defer (no moves / deletes / renames / code changes during arc) | Chris directive: research/audit not implementation |
| D6 | Canonical summary at `2799` = ratified restructuring plan | Migration ships as follow-up sessions post arc-close |
| D7 | Twin-pointer discipline for arc close | Content doc + workspace deliverable per `feedback_twin_deliverable_at_every_ratification` |

---

## 7. Anti-scope

Out of Group 2700 even under the parent shape:

- **Context-kit framework** (`docs/docs-pattern/`) — separate domain per `DOC_LIFECYCLE.md` §0. Do not audit.
- **Runtime-coupled path movement** — `DOC_LIFECYCLE.md` §2b's 5 rows are never-move under any restructuring proposal.
- **Playbook governance surfaces** — `docs/ENGINEERING_PLAYBOOK.md` and its ratification records are constitutional. Arc may propose reference-linking clean-up but cannot propose content rewrites.
- **PLATFORM_INVENTORY.md counts editing** — sole authoritative counts source per §2c; arc cites, never rewrites.
- **`/docs/research/` restructuring** — this arc dogfoods the pattern but does not propose changes to it. T2 CHALLENGES it as a substrate-fitness question; changes queue as separate future arc.
- **Migration execution** — no file moves during arc. Ships post-close.

---

## 8. Open decisions still needed (non-blocking; queue as they surface)

Non-blocking questions Chris may need to answer during T1-T6 execution:

- **O1** — For T5 handoff-lifecycle proposal: what's Chris's tolerance for handoff aging-out to archive? All in place forever vs archive-after-N-sessions vs eligible-for-deletion?
- **O2** — For T6 anchor-drift SSOT proposal: which surface WINS when SIGN mechanics drift across playbook / `00-START-NEXT-SESSION` / memory? Constitutional (playbook) or operational (`00-START-NEXT-SESSION`)?
- **O3** — For canonical summary migration queue: does Chris want a single monster migration PR or split into per-thread migration sessions?
- **O4** — Should T2's CHALLENGE candidates surface a v2 of `RESEARCH_OPERATING_SYSTEM.md` (separate arc), or fold into `/docs/` restructuring's canonical summary?

None block T1 open. Chris ratifies as they surface.

---

## 9. Anchor-update recommendations queued for canonical summary

Candidate `PLATFORM_INVENTORY.md` / `PLATFORM_WHAT_IT_IS.md` / `CLAUDE.md` edits the canonical summary may need to propose:

- **PLATFORM_INVENTORY** — potential new subsystem row for "Docs Corpus Governance" if T4 audience-segmentation surfaces enough surface area
- **CLAUDE.md** — potential subsection updates for the new docs-restructuring pattern (if canonical summary produces new conventions)
- **`docs/canon/INDEX.md`** — potential canon-registry updates if the ratified restructuring plan promotes a new operational doc to canon (constrained by ≤10 cap)

Explicitly parked to the canonical summary. Do NOT touch during T1-T6.

---

## 10. Zoom-out folds recorded at parent-scoping (rows 90-93)

Per PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9. Persisted to `logs/zoom_out_classifications.jsonl` BEFORE Chris D-verdict on parent shape.

| Row | Arc | Classification | Evidence |
|-----|-----|----------------|----------|
| 90 | governance surfaces drift (SIGN mechanics 3-copy) | same_pr_mitigatable | `docs/research/process/claude_research_startup_introspection.md#12` |
| 91 | dogfooding self-referential lock-in | same_pr_mitigatable | `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md#68` |
| 92 | substrate identity discontinuities (handoff citation drift) | future_trigger | `docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8` |
| 93 | end-state constraints already exist (DOC_LIFECYCLE §2c) | same_pr_actionable | `docs/canon/INDEX.md#2` + `docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8` |

Row 91 (dogfooding lock-in) is load-bearing for T2 — T2 audit MUST include a CHALLENGE section per row 91's mitigation.

---

## 11. Next step

- **T1 opens next session (S2802+)** — inventory & topology audit. Load this parent doc + `DOMAIN_RESEARCH_PLAYBOOK.md §9` (28 questions). First-action fresh mint of pin scoped to T1.
- **OPEN_ARCS.md updated** at close-cascade to reflect arc `2700` in-progress + `2701..2706` awaiting-open + `2799` awaiting-summary.
- **No commits yet on this doc.** Chris ratifies parent scope before commit per `PLAYBOOK-16` draft-first default.

---

## 12. Provenance

- **Session pin:** `pa-9e641d91391f40d8` (label `s2801-docs-restructuring-parent-scoping`) — minted S2801 open; retire at close per S2770+ pattern (force=true expected)
- **Rigby T1 SIGN:** verdict SIGN-WITH-EDITS; tool_runs verified non-empty (`ops_tool`, `search_docs`, `kb_tool`); anti-rubber-stamp check per `feedback_verify_rigby_tool_runs_before_trusting_sign` PASSED
- **Chris D-verdict:** `"go ahead with the 6-thread package"` at S2801 T1 (2026-07-16)
- **Playbook version at parent-scoping:** v0.8.0 (205 rules)
- **HEAD at parent-scoping author time:** `cc3e23c10709` (S2800 close addendum PR #3215)

---

**End of parent-scoping. T1 (`2701_docs_inventory_topology_audit.md`) opens the audit sequence in the next session.**

---
title: "Ratification — Group 2800 /docs/ Content Audit parent scoping (D1-D9 locked)"
date: 2026-07-19
session: 2833
subject: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md (parent scoping, D1-D9)
ratifier: Chris
scope: full parent scoping — 6-thread taxonomy, ≥6-session estimate, machine-consumable per-file YAML classification schema, cross-arc consumption contract with future §3 target-tree migration arc
deferred_from_ratification: none (full parent locked at ratification; child audit rubrics still author-defined per playbook §9 adaptation)
successor_arc: T1 anchor & canonical-doc content audit — opens at S2834 as `2801_docs_content_anchors_audit.md`
predecessor: docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md
---

# Ratification — 2800 /docs/ Content Audit parent scoping

## §1 What was ratified

**Full parent scoping** of `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md` — decisions D1-D9.

Chris D-verdict verbatim: **"ratify D1-D9, open T1 next session"** (S2833, 2026-07-19).

### §1.1 Ratified decisions (D1-D9)

| # | Decision | What it locks |
|---|---|---|
| D1 | Content-audit arc opens at S2833 | Chris D-verdict S2832 ("open file-level audit arc") executes here |
| D2 | Arc group number = `2800` | Adjacent to Group 2700 structural sibling for navigation coherence |
| D3 | Folder = `docs/research/domains/docs_content_audit/` | Standard NNxx domains convention |
| D4 | 6 threads: T1 anchors / T2 refs / T3a duplicates / T3b orphans / T4 handoff-cite+retrieval-harm / T5 reports+audits triage | Severity-batched; handoffs quarantined to citation-integrity + narrow retrieval-harm banner only |
| D5 | Non-goals hard-line defer: no moves / deletes / renames / edits / code changes during arc | Classification only; migration is a separate arc |
| D6 | Canonical summary at `2899` | Ratified content-audit output; migration executes as follow-up sessions |
| D7 | Twin-pointer discipline at arc close | Content doc + workspace deliverable |
| D8 | Session-count estimate ≥ 6 sessions | Realistic given T3a manual-confirm on top-100 dup pairs + T3b reachability grade-work + T5 triage + canonical summary each ≥1 session |
| D9 | Output = machine-consumable per-file YAML classification schema (§10 locks row shape, severity taxonomy P0..P3, action taxonomy, cross-arc consumption contract with §3 migration) | Prevents §3 migration PRs from re-litigating "what action per file?"; keeps §3 execution mechanical |

### §1.2 Ratified guardrails

- **Classification only** — no fixes, moves, deletions, or content rewrites during the arc (per D5).
- **Per-file finding schema is YAML-parseable** — child audits MUST emit findings as YAML blocks per §10.1 shape; enforced at each child ratification.
- **Handoffs quarantined** — T4 does NOT do per-file content review of all 1056 handoffs; scope is citation-integrity + narrow retrieval-harm banner list only (per D4 refinement, Rigby cycle-1 Q2 evidence).
- **Cross-arc consumption contract with §3 execution arc** — canonical summary `2899` is the input to the future migration arc; per-file `recommended_action` values map 1:1 to migration-PR classes (per §10.4).
- **In-flight children exempt from cross-audit** — audit closed arcs only; Group 2700 children (2701-2706) and Group 2800 children (2801-2805) audited only after their own arcs close (per §7 anti-scope).

### §1.3 Ratified exclusions (per §7 anti-scope)

- `docs/docs-pattern/**` (22 files) — context-kit framework per DOC_LIFECYCLE §0
- `docs/archive/**` (1388 files) — already-partitioned historical per Group 2700 parent §7
- Per-handoff content review (T4 quarantined)
- Runtime-coupled path movement (DOC_LIFECYCLE §2b invariants preserved)
- §3 target-tree execution (separate arc; consumes this arc's output)
- Playbook governance surface content rewrites

## §2 What was explicitly NOT ratified today

Nothing at parent-scoping level. All 9 decisions locked. Deferred to child audits (author-defined per playbook §9 adaptation):

- **T1..T5 in-thread detection methodology** — child audits pick own detection approaches (parent locks OUTPUT schema not INPUT methodology)
- **P0/P1 severity threshold for specific anchor set** — T1 authors that judgment
- **Cross-arc reconciliation when T1 and T2 both flag same target** — canonical summary `2899` resolves
- **Post-arc migration arc number** — opens after `2899` closes

## §3 Successor: T1 opens at S2834

Chris directed T1 (anchor & canonical-doc content audit) opens next session. Scope reminder from §4 T1:

- Corpus: ~30 load-bearing docs (anchors PLATFORM_WHAT_IT_IS + PLATFORM_INVENTORY + KNOWLEDGE_PIPELINE + UDB_BEHAVIOR_LAYER + UDB_TRANSLATION_LAYER; canon rows; governance rows; root-README; `docs/00-START-HERE/**`; `CLAUDE.md`)
- Method: per-file, walk each concrete claim (file path, function name, line range, count) and verify against HEAD
- Output: YAML findings per §10.1 schema
- First to run: highest-impact, smallest-corpus; validates the per-file schema before T2/T3a/T3b scale it up

## §4 Rigby SIGN status — 3 cycles, all tool-grounded

Rigby SIGN routed at S2833 on fresh pin `pa-cc1dbcb7d18c4502` (label `s2833-docs-content-audit-scoping`).

**Cycle 1** — 5 pressure-test questions on original 5-thread draft:
- Q1 scope split: STRENGTHEN — split T3 → T3a duplicates + T3b orphans/reachability (evidence: original T3 bundled two orthogonal full-corpus passes)
- Q2 T4 quarantine: STRENGTHEN — add retrieval-harm banner sub-loop for handoffs surfacing in `search_docs` top-K (evidence: `search_docs "in-progress arc"` returned `SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md#2` + `docs/archive/handoffs-pre-800/SESSION_368_DREAM_VALIDATION_UI.md#6` as top hits)
- Q3-Q5: CONDITIONAL (tool_runs not yet completed; anti-rubber-stamp honored — refused to sign without evidence)

**Cycle 2** — Q3/Q4/Q5 finalized with explicit tool commands:
- Q3 T5 scope: STRENGTHEN — move `docs/reports/` (33 files) into T5 (evidence: `3D_GENERATION_VERIFICATION_REPORT.md` has DOC-POINTER-V2 supersession banner, reads as one-shot snapshot); keep `docs/code-review/` in T3 (evidence: `00-REVIEW-ORCHESTRATOR.md` reads as standing process/template)
- Q4 session-count: DISAGREE — 4-session estimate unrealistic; revised to ≥6 (evidence: 2701 exemplar not a per-file 700-file throughput model)
- Q5 zoom-out: STRENGTHEN — parent under-designs machine-consumable per-file classification schema that §3 execution will consume (evidence: 2799 §3 target tree + RATIFICATION_2026-07-19_2799 successor arc calls for per-file audit + amendment queue)

**Cycle 3** — confirmation after 5 refinements applied:
- Verified 3/5 refinements landed (T3 split, T4 sub-loop, T5 reports scope) via `repo_tool.read` of refined doc
- 2/5 refinements (§6 D8, §10 schema) unverified in Rigby's cycle-3 read window due to display truncation at line 158 of 306-line doc; verified locally at close ceremony
- Rigby carry-forward fold `future_trigger`: schema MUST be explicitly machine-readable — addressed inline in §10.1 title (`"MUST emit findings as YAML block, one row per finding; parseable by downstream tooling"`)

Anti-rubber-stamp discipline honored throughout — no empty tool_runs; Rigby refused CONDITIONAL to AGREE promotion without evidence at cycle 1 Q3/Q4/Q5; Rigby's DISAGREE on Q4 session-count materially changed D8 from 4 to ≥6.

## §5 References

- **Parent scoping being ratified**: `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md` (D1-D9)
- **Sibling structural arc (RATIFIED destination)**: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` §3
- **Preceding governance envelope**: `docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md`
- **Preceding session handoff**: `docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`
- **Governance canonical**: `docs/00-START-HERE/DOC_LIFECYCLE.md` §0 (exclusion) + §2b (runtime-coupled) + §2c (sole counts source) + §3 (root stability)
- **Twin-pointer deliverable**: minted at close cascade (workspace `b4503364-2573-4401-9e28-61a739e0ce50`, ORM-direct per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`; category `governance`; deliverable_type `ratification_record`)

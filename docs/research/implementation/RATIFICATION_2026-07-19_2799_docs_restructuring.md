---
title: "Ratification — Group 2700 /docs/ Restructuring §3 target tree (2799 canonical summary)"
date: 2026-07-19
session: 2832
subject: docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md §3
ratifier: Chris
scope: §3 target /docs/ tree ratified as PROPOSED (structural destination; NOT a move-script; compatibility-first per-PR gating preserved)
deferred_from_ratification:
  - §7 anchor-update recommendations (bucket A auto-actionable + bucket B separate-arc)
  - §8 follow-on queue ordering (item #1 already done via S2818-S2831 discovery-layer arc)
successor_arc: file-content-level audit (per-file read + flag stale/broken/duplicate/orphan) — opens as separate arc; NOT scoped by this ratification
predecessor: docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md
---

# Ratification — 2799 /docs/ Restructuring §3 target tree

## §1 What was ratified

**Only §3 target `/docs/` tree** of `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`.

Chris D-verdict verbatim: **"ratify §3 today, open file-level audit arc"** (S2832, 2026-07-19).

### §1.1 Ratified content — the target tree

The `docs/` corpus MOVES TOWARD the layout in 2799 §3.1:

- Anchors + INDEX + generated manifests at root (~10 loose files, down from 99)
- `00-START-HERE/` for onboarding
- `canon/` `governance/` `missions/` `decisions/` `ops/` — **NEVER MOVE** (DOC_LIFECYCLE §2b runtime-coupled)
- `research/` — kept as-is (working pattern)
- `topics/` — kept as-is (per-subsystem narrative)
- `handoffs/` — no bulk moves; per-doc `citation_health` + `is_superseded` tagging post-arc
- `audits/` — CONSOLIDATED (absorbs `audit/` + `audit-2026/` per §3.2; `legacy/` subdir preserves 25 pre-consolidation files)
- `plans/` — CONSOLIDATED (absorbs `specs/` + `designs/` + `roadmap/` + `roadmaps/` + `pre-launch/` per §3.3)
- `narratives/` `guides/` `features/` `architecture/` `code-review/` `reports/` `patents/` — kept as-is
- `docs-pattern/` — context-kit framework, EXCLUDED per DOC_LIFECYCLE §0 (never touched by consolidation)
- `archive/` — 1388 files already-partitioned; leave alone per parent §7

Per §3.4 miscellaneous resolution:
- `docs/adr/` (4) → `docs/decisions/` (contract preserved: `ADR-*.md` filename stays at `docs/decisions/ADR-*.md`)
- `docs/operations/` (1) → `docs/ops/` (with V2-stub redirect)
- Root anchors keep pointer role; substance in subdirs
- Doubled root files (`AGENTS.md` + `AGENTS_REFERENCE.md`; etc.) → per-file merge review
- Session-loose at root (`SESSION_780_PLATFORM_STATUS.md`, `SESSION_1251_...`) → `docs/handoffs/`

### §1.2 Ratified guardrails

- **Canonical structure is the destination, migration is STAGED** — this ratification does NOT authorize bulk moves
- **Compatibility-first for generator/runtime paths** — no move ships without per-PR verification of DOC_LIFECYCLE §2b (runtime-coupled path contracts) + T2 FP-META guardrails (frontmatter mandates)
- **Runtime-coupled scoping** (per Rigby SIGN post-authoring Q2): DOC_LIFECYCLE §2b applies to the SPECIFIC PATH CONTRACT (e.g., `docs/decisions/ADR-*.md`), not entire subdirs — merging `docs/adr/` → `docs/decisions/` is safe IF the `ADR-*` filename contract stays at `docs/decisions/ADR-*.md`
- **Generator/automation coordination BLOCKS §3.4 root-file reduction** — per §8 item #8 (Rigby SIGN post-authoring Q3 addition); management commands writing to `docs/*_AUDIT.md` root paths must be enumerated + updated before those root files can be moved
- **Item #1 of §8 (discovery-layer enforcement) is ALREADY DONE** via S2818-S2831 arc (Pattern B/C/D + DORMANT pointer-intent registry + RAG intent-gate diagnostics tab). No follow-up work needed on that item.

## §2 What was explicitly NOT ratified today

Per Chris D-verdict scope ("§3 today"):

- **§7 anchor-update recommendations** — split into bucket A (auto-actionable low-risk) and bucket B (defer to separate arcs). Ratifiable at future session; not decided today.
- **§8 follow-on queue ordering** — 7 remaining items (item #1 already done); ratifiable at future session.
- **Any actual file moves** — this ratification is destination-shape only. Every migration PR needs its own verification of DOC_LIFECYCLE §2b + generator coordination.

## §3 Successor arc — file-content-level audit (opens at S2833)

Chris clarified at S2832: Group 2700 arc did **structural/statistical** audit (counts, patterns, subdir shapes, sample-based). It did **NOT** do a **file-content-level** walk (read every .md file, flag stale/broken/duplicate/orphan by content).

That gap opens as a separate arc at S2833. Scoping is NOT decided by this ratification — the arc opens with its own parent-scoping session per DOMAIN_RESEARCH_PLAYBOOK.

Rough shape (advisory, not binding):

- 3247 files in `/docs/` (per T1 inventory)
- File-content audit reads each file and flags: stale (facts drifted from HEAD), broken (references dead paths / retired IDs), duplicate (content duplication across surfaces), orphan (no incoming references + not runtime-coupled)
- Deliverable: audit output (per-file classification) + amendment queue
- Likely arc shape: parent scoping + N child audits by subdir batch + xx99 canonical summary
- Estimated size: proportional to 3247 files; likely multi-session
- Numbering: unclaimed as of 2026-07-19; S2833 parent scoping picks the arc number

## §4 Rigby SIGN status

Rigby SIGN was routed at S2832 open on fresh pin `pa-d10f64b5624c43c9` with 5 pressure-test questions on the ratification shape. Substantive tool_runs recorded (`repo_tool` searches for `docs/adr` codebase references, management commands writing to root `*_AUDIT.md`, `DOC_LIFECYCLE.md` §2c content, `MQ-T5-8` cross-references, parent §4 T5 clause). Verdicts were not extracted before Chris D-verdict arrived — Chris's clarification (whole-tree audit was structural, not content-level) reframed the ratification from a Rigby-agreement-needed decision into a Chris-scope-clarification decision. Tool_runs preserved in Rigby conversation `pa-d10f64b5624c43c9` for future reference.

Anti-rubber-stamp discipline honored: tool_runs were substantive (multiple repo_tool file reads + searches) BEFORE the SIGN cycle was superseded by Chris's scope clarification.

## §5 References

- **Canonical summary being ratified**: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` §3
- **Predecessor handoff**: `docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md`
- **Governance canonical**: `docs/00-START-HERE/DOC_LIFECYCLE.md` §2b/§2c/§3
- **Parent scoping**: `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`
- **Twin-pointer deliverable (2799 content mirror)**: workspace `b4503364-2573-4401-9e28-61a739e0ce50`, deliverable `37d6ca76-89c3-4966-8f4c-decc52ce8169`
- **This ratification's twin-pointer deliverable**: minted at close cascade (workspace `b4503364-...`, ORM-direct per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`)

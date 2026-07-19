---
title: "Ratification envelope — S2835 T2 reference-graph & broken-refs content audit (child 2802)"
date: 2026-07-19
session: 2835
ratifier: Chris
verbatim_directive: "ratify T2 as-folded"
target_doc: docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md
research_group: 2800
thread: T2
parent_arc: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
predecessor_child: docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
sign_pin: pa-0de182aaedcf43f0
sign_cycles: 2
category: governance
deliverable_type: ratification_record
---

# S2835 — T2 reference-graph & broken-refs content audit RATIFICATION

## 1. Ratification statement

Chris D-verdict at S2835 close (2026-07-19):

> ratify T2 as-folded

**Scope of ratification:**

- Full T2 audit doc (`2802_docs_content_reference_audit.md`) as authored + folded per Rigby cycle-1 refinements + cycle-2 fold-gap fix.
- Mechanical grep + resolver methodology over 791 non-handoff in-scope
  source files across 4 reference classes (md_link, session, adr, file_cite).
- Parent §10.1 schema **v1.1 UNCHANGED**. v1.2 `coverage_refs`/`coverage_claims`
  split proposal recorded as §5.7 future_trigger for 2899 close consideration —
  NOT applied at T2 ratification (respects S2834 "no schema mod without fresh
  SIGN + D-verdict" boundary).
- Migration queue frozen; routed to future §3 execution arc post-2899.
- **ADR-0000 disposition escalation** surfaced to Chris in T2 §4.1 row 2
  (workspace enumeration by Rigby cycle-1 Q1 confirmed 5 of 6 Cycle 1A ADRs
  resolve; ADR-0000 does not — real broken until located or explicitly
  resolved).

## 2. Joint Claude+Rigby SIGN provenance (2 cycles)

### Cycle 1 — 2026-07-19 (5 pressure-test questions)

**Rigby tool_runs (verified non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`):**
10+ substantive tool calls:

1. `deliverable_tool.list workspace_id=a9a16593-e0a4-44dc-8256-efc65d524b3c show_all=true` — Q1 workspace ADR enumeration
2. `repo_tool.read docs/HANDOFF_NUMBERING_GAPS.md` — Q2 gap-catalog verification
3. `repo_tool.read docs/PLATFORM_WHAT_IT_IS.md:38-78` — Q3 SESSION_1099 context
4. `repo_tool.read 00-START-NEXT-SESSION.md:66-106` — Q3 WorkspacePageNew typo context
5. `repo_tool.search "§1.4"` + `repo_tool.read` on T2 §1.4/§2.3/§6.1 — Q4 coverage semantics
6-10. Additional `repo_tool.read` calls verifying T2 draft sections

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q1 FP-1 ADR verification | **DISAGREE** | Workspace confirmed 5 of 6 Cycle 1A ADRs (0110/0120/0130/0140/0150 resolve; ADR-0000 does NOT). Fold: split §2.3 FP-1 to keep ADR-0000 active P1 + escalate_to_chris (§4.1 row 2); 36 raw ADR BROKEN_404 → `finding_state: resolved` |
| Q2 SESSION catalog completeness | **STRENGTHEN** | HANDOFF_NUMBERING_GAPS.md documents ONLY SESSION_198→205 gap. Fold: 2 raw SESSION BROKEN_404 (198, 205) → `finding_state: resolved`; other 13 unique missing SESSION_NNNNs → active real broken, entered migration queue |
| Q3 anchor P0 severity | **DISAGREE** | Both would-be P0s misclassified per cited context. Fold: SESSION_1099 (PLATFORM_WHAT_IT_IS.md:46) → P1 (refresh-block already carries counts-drift disclaimer); WorkspacePageNew typo (00-START-NEXT-SESSION.md:73) → P2 (D-bucket candidate list, not authoritative bug tracker). **Net effect: 0 real P0s in T2** — §10.4(b) root-stability P0 gate does NOT trigger for this arc |
| Q4 coverage honesty | **DISAGREE** | Labeling 789 files `full_claim_walk` overstates coverage (T2 scans REF existence, not semantic line-range claims per §1.4 anti-pattern). Fold: relabel ALL 791 files as `coverage: structural_only` under CURRENT v1.1 semantics. v1.2 split proposal (`coverage_refs` + `coverage_claims`) recorded as §5.7 future_trigger — NOT applied at T2 (S2834 schema-mod boundary) |
| Q5 zoom-out anti-worship | **STRENGTHEN** | Ship T2 now with loud resolver limitations; smarter-resolver re-run only if per-defect precision needed later. No body-fold; records "ship-with-loud-limitations" as ratification input |

### Cycle 2 — 2026-07-19 (3 fold-verification questions)

**Rigby tool_runs:** 5+ substantive `repo_tool.read` calls into
§2.3 FP-1 + §4.1 row 2 + §2.8 + §3 histogram + §4.1 rows 1 & 3 +
§3 coverage + §2.9 YAML samples + §5.7 future_trigger.

**Verdicts:**

| Q | Verdict | Fold-gap |
|---|---|---|
| Q6 (Q1 ADR fold verification) | **AGREE** | None — §2.3 FP-1 correctly splits ADR-0000 active vs 5 workspace-canonical resolved; §4.1 row 2 escalate_to_chris recorded |
| Q7 (Q3 severity fold verification) | **DISAGREE (initial) → AGREE (post-fix)** | Rigby caught real fold-gap: §2.9 YAML sample rows still showed `severity: P0` on PLATFORM_WHAT_IT_IS.md + 00-START-NEXT-SESSION.md samples despite §2.8/§3/§4.1 text downgrades. Fixed same-turn: sample severities → P1/P2 with Q3 citation in notes. Re-verified AGREE |
| Q8 (Q4 coverage fold verification) | **AGREE** | None — §3 states `structural_only: 791 files, full_claim_walk: 0` with ref-graph-only rationale; §2.9 YAML samples uniformly `coverage: structural_only`; §5.7 records v1.2 split future_trigger WITHOUT bumping schema_version |

### Convergence

Cycle 2 verdicts: Q6 AGREE + Q7 AGREE (post-fix) + Q8 AGREE = 3 AGREE, 0
DISAGREE at convergence. Joint Claude+Rigby agreement per
`feedback_claude_rigby_agree_first_chris_yes_no` reached.

**Anti-rubber-stamp caught 2 real F-BLOCKING refinements:**
- Cycle 1 Q1: ADR-0000 workspace-absent split from FP-1 sweep (Rigby's
  `deliverable_tool.list` evidence).
- Cycle 2 Q7: §2.9 YAML sample severity fold lag (Rigby's `repo_tool.read`
  lines 430-490 caught the P0 stragglers).

Both would have shipped incorrect artifacts had Rigby rubber-stamped.

## 3. Real drifts caught + migration queue routing

Post-Rigby-fold defect population:

| Sev | Class | Count | Notes |
|---|---|---:|---|
| P0 | — | **0** | §10.4(b) root-stability P0 gate NOT triggered for this arc |
| P1 | Real BROKEN | ~9 | SESSION_1099 (PLATFORM_WHAT_IT_IS refresh-block, Q3 fold) + ADR-0000 (workspace-absent, Q1 fold, escalate_to_chris) + 4 md_link RENAMED path-depth errors (playbook_v0_1 docs — `../ENGINEERING_PLAYBOOK.md` should be `../../ENGINEERING_PLAYBOOK.md`) + ~3 additional research_os_anchor / playbook_adr_ratification real BROKEN |
| P2 | Real BROKEN | ~30-50 | WorkspacePageNew.ts typo (D-bucket, Q3 fold) + 13 NEW SESSION_NNNN gaps (SESSION_184, 960, 962, 963, 1075, 1077, 2705, 2708, 2716, 2719, 2725, 2726 — post-Q2 fold; 2 raw at HANDOFF_NUMBERING_GAPS.md resolved) + closed_research_arc + audits_reports BROKEN_404 |
| P3 | Info + `ok` rows + FP-downgraded | remainder | Includes 36 FP-1 ADR resolutions + ~6,000 FP-2 bare-basename RENAMED + ~unknown FP-3 regex over-matches |

**Coverage distribution (v1.1 schema):**
- `structural_only`: 791 files (all — post-Q4 fold under current v1.1 semantic)
- `full_claim_walk`: 0
- `deferred`: 0

**Migration queue frozen post-D-verdict. Routing target:** future §3
execution arc that opens after Group 2800 canonical summary (`2899`)
ratifies. Not this arc's execution job (parent §5 non-goals).

**Chris escalation from §4.1 row 2:** ADR-0000 disposition — is it a
numbering placeholder never intended to ship, was it authored elsewhere,
or was the workspace deliverable archived/deleted? Awaits Chris directive.

## 4. Schema state

**Parent §10.1 schema UNCHANGED at v1.1.** T2 inherits from S2834's frontmatter
`schema_version: 1.1` and does not modify.

**v1.2 candidate future_trigger recorded** in T2 §5.7:
- Split `coverage` into `coverage_refs` + `coverage_claims` orthogonal
  dimensions. Rigby cycle-1 Q4 proposal. Evaluate at 2899 close alongside
  other arc-level schema-refinement candidates.

## 5. Arc registration

Group 2800 arc state after S2835 T2 close:

- ✅ Parent scoping RATIFIED at S2833 (D1-D9)
- ✅ T1 anchor content audit RATIFIED at S2834 (schema v1.1 locked)
- ✅ **T2 reference-graph audit RATIFIED at S2835 (§10.1 schema unchanged; v1.2 future_trigger recorded)**
- ⏳ T3a duplicate audit — pre-scan hint recorded (§4.1a topics count_dense tagging per S2834); next child target
- ⏳ T3b orphan audit — RENAMED map available as pre-clustering signal per T2 §5.6
- ⏳ T4 handoff citation-integrity + retrieval-harm audit
- ⏳ T5 reports + audits triage
- ⏳ 2899 canonical summary (arc close; consolidates v1.2 coverage-split proposal + ADR-0000 disposition)

**Arc registered:** `docs/research/OPEN_ARCS.md` Group 2800 row advanced
from "T1 RATIFIED; T2 next" to "T2 RATIFIED; T3a next" (3 of 6 shipped).

## 6. Twin-pointer artifacts

**Repo:**

- Content: `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`
- Envelope: this file
- Handoff: `docs/handoffs/SESSION_2835_T2_REFERENCE_GRAPH_AUDIT.md`
- Scanner tool: `tools/audit_2802_reference_graph.py` (preserved as audit artifact)
- Arc manifest: `docs/research/OPEN_ARCS.md` (Group 2800 In-progress row updated 2→3 of 6)

**Workspace UI (per `feedback_twin_deliverable_at_every_ratification` +
NEW rule `feedback_rigby_writes_workspace_deliverables`):**

- Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
- Twin: content mirror + ratification envelope
- **Rigby creates the workspace deliverables via PA `deliverable_tool.create`**,
  NOT Claude via ORM-direct. Claude routes explicit instruction post-merge;
  Claude verifies tool_runs + ORM cross-check. Any post-create diagnostic-status
  fix (per known bug `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`)
  is post-Rigby-tool-surface exercise, not primary create path.

## 7. Provenance

- **Session:** 2835
- **Pin:** `pa-0de182aaedcf43f0` (label `s2835-t2-reference-graph-audit`; retired at S2835 close with `force=true`, sixty-sixth consecutive per S2770+ pattern)
- **HEAD at draft:** `288259386b3a` (S2834 close cascade)
- **HEAD at ratification:** filled at close cascade PR merge
- **Playbook version:** v0.8.0 (unchanged; 205 rules)
- **Anti-rubber-stamp:** verified non-empty tool_runs across both SIGN cycles; caught 2 real F-BLOCKING refinements (ADR-0000 split; §2.9 YAML sample severity fold lag)
- **Joint agreement:** reached per `feedback_claude_rigby_agree_first_chris_yes_no`
- **Rigby-writes-workspace-deliverables rule:** established at S2835 open per `feedback_rigby_writes_workspace_deliverables`; T2 close is first exercise of the new pattern
- **Post-merge recycle:** `make recycle-all` per PLAYBOOK-7.4.4 (eighty-first consecutive close-cycle)

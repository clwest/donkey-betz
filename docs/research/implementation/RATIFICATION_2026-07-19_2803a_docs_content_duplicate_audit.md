---
title: "Ratification envelope — S2836 T3a duplicate-content audit (child 2803a)"
date: 2026-07-19
session: 2836
ratifier: Chris
verbatim_directive: "Continue on but let's defer the two issue and any others like it until we have the /docs/ audit completed incase other issues come up"
target_doc: docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md
research_group: 2800
thread: T3a
parent_arc: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
predecessor_child:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md
sign_pin: pa-90ea529a09234d57
sign_cycles: 2
category: governance
deliverable_type: ratification_record
---

# S2836 — T3a duplicate-content audit RATIFICATION

## 1. Ratification statement

Chris D-verdict at S2836 close (2026-07-19):

> Continue on but let's defer the two issue and any others like it until we have the /docs/ audit completed incase other issues come up

**Scope of ratification:**

- Full T3a audit doc (`2803a_docs_content_duplicate_audit.md`) as authored + folded per Rigby cycle-1 refinements + cycle-2 fold-verification.
- Token-shingling + inverted-index Jaccard scanner methodology over 792
  non-handoff in-scope files. Scanner tool: `tools/audit_2803a_duplicate_content.py`.
- Parent §10.1 schema **v1.1 UNCHANGED**. Three v1.2 candidates recorded
  as `future_trigger` for 2899 close (`coverage_content_dup` third axis /
  `template_family` field / `judgment_state` field). Acceptance criteria
  (i)-(iv) codified in §5.3 for any future v1.2 amendment.
- **NEW ARC-LEVEL POLICY established:** all `escalate_to_chris` rows
  across T3a/T3b/T4/T5 DEFER to arc close (`2899` canonical summary),
  NOT resolved child-by-child. Judgment on canonical designation benefits
  from cross-child context; `2899` MUST include consolidated "Chris
  judgment queue" section for single-session workshop resolution.
- **T3a↔T5 boundary rule adopted** (§5.6): T3a MUST NOT finalize
  disposition for `docs/audits/**` + `docs/reports/**` files; §4.1 rows
  carry `t5_may_override: YES`.
- Migration queue frozen; routed to future §3 execution arc post-2899.

## 2. Joint Claude+Rigby SIGN provenance (2 cycles)

### Cycle 1 — 2026-07-19 (5 pressure-test questions)

**Rigby tool_runs (verified non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`):**

- `repo_tool.read` — `docs/00-START-HERE/DOC_LIFECYCLE.md` §1 (V2 pointer pattern)
- `repo_tool.read` — 3 sample V2 stubs (`docs/features/AUDIO_GENERATION.md`, `docs/guides/DAVINCI_PHASE_3_PLAN.md`, `docs/agents/INDEX.md`), lines 1-8 each
- `repo_tool.search "SESSION_819"` in `core/management/commands/` → **zero matches** (runner-independence proof)
- `repo_tool.read` — parent 2800 §4 T3a rubric text
- `search_docs "schema v1.1 locked"` → 5 chunks including 2801 §10.1 lock language
- `repo_tool.read` — 2801 §10.1 + 2800 §4 T5 spec

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q1 V2-stub classification | **AGREE** | No change — DOC-POINTER-V2 stubs are load-bearing per DOC_LIFECYCLE §1; 110-file scale is corpus-shape signal not consolidate signal |
| Q2 SESSION_819 archive-vs-runner-fix ordering | **STRENGTHEN** | §2.1 runner-independence proof added (Rigby zero-match grep); §4.1 archive/runner-fix parallel-track note added |
| Q3 escalate_to_chris as own severity class | **STRENGTHEN** | §2.4-§2.5 flagged with `needs-judgment` sub-classification; §5.7 records v1.2 candidate (Option C: `judgment_state: known | ambiguous` field, most additive) |
| Q4 v1.2 schema mid-arc amendment | **STRENGTHEN** | §5.3 acceptance criteria (i)-(iv) codified: additive + backward-compat + parser-compat plan + deprecation path; deferral-default explicit |
| Q5 zoom-out — scope creep + T3a↔T5 coupling | **STRENGTHEN** | §5.6 T3a↔T5 boundary rule added; §4.1 rows carry `t5_may_override: YES`; scope-creep guard against merge-planning added |

### Cycle 2 — 2026-07-19 (4 fold-verification questions)

**Rigby tool_runs:** substantive `repo_tool.read` of §2.1 (lines 232-246),
§4.1 (lines 600-610), §2.10 (lines 467-555), §3 (lines 564-569),
§2.4 (lines 331-349), §2.5 (lines 354-370), §5.3 (lines 682-695),
§5.6 (lines 734-746), §5.7 (lines 774-785).

**Verdicts:**

| Q | Verdict | Fold-gap |
|---|---|---|
| Q6 (Q2 fold verification) | **AGREE** | Runner-independence proof + parallel-track framing + T5-may-override annotation all present |
| Q7 (Q3 fold + YAML sample sync) | **AGREE** | YAML sample severity labels align with §3 histogram; SYSTEM_ARCHITECTURE_MAP needs-judgment sample present matching §2.4 text (per S2835 Q7 sync discipline) |
| Q8 (Q4 fold verification) | **AGREE** | §5.3 (i)-(iv) all four criteria stated; deferral safer-default explicit |
| Q9 (Q5 fold verification) | **AGREE** | §5.6 T3a↔T5 boundary complete; §5.7 Option C preference stated |

### Convergence

Cycle 2 verdicts: 4/4 AGREE at convergence. Joint Claude+Rigby agreement
per `feedback_claude_rigby_agree_first_chris_yes_no` reached.

**Anti-rubber-stamp verification:** Rigby's cycle-1 STRENGTHEN
refinements each landed on tool-grounded evidence (V2 stub reads +
runner grep + parent rubric text + schema-lock chunks + T5 spec text).
Cycle 2 verdicts cited exact line numbers from the folded doc. Neither
cycle rubber-stamped.

**Real F-BLOCKING refinements Rigby caught:**
- Cycle 1 Q2: runner-independence needed proof — grep zero-match was
  the concrete evidence that unblocked parallel-track framing.
- Cycle 1 Q3: `escalate_to_chris` conflates known-canonical vs
  canonical-ambiguous. Without this fold, §4.2 would ship as a single
  bucket obscuring workflow structure.
- Cycle 1 Q5: T3a might have shipped without T3a↔T5 boundary language.
  §4.1 audits-triage recommendations would have preempted T5's
  disposition authority — a real inter-child coupling failure.

## 3. Real drifts caught + migration queue routing

Post-Rigby-fold + manual-classification defect population:

| Sev | Class | Count | Notes |
|---|---|---:|---|
| P0 | — | **0** | §10.4(b) root-stability P0 gate NOT triggered (no root-stable/NEVER-MOVE anchor appears in any pair above Jaccard 0.10) |
| P1 | Real duplicate | **~2 classes / ~172 pair rows** | (a) SESSION_819_SYSTEM_AUDIT_* cluster 19 files × 171 pair combinations → `archive` to `docs/archive/2026-07/audits/session_819_snapshots/` + parallel runner-fix ticket (Rigby zero-match grep proves archive can ship independently); (b) PA_TOOLS_GAP_MAP_S2795/S2796 pair Jaccard 0.912 → `consolidate_into S2796` |
| P2 | Needs-judgment (DEFERRED) | **2 classes** | SYSTEM_ARCHITECTURE_MAP vs SYSTEM_MAP + CLAUDE_CONTEXT_SYSTEM_PACK vs SYSTEM_FULL_ACTIVATION_PLAN → both `escalate_to_chris` with `needs-judgment` sub-classification; **DEFERRED to `2899` per S2836 D-verdict new policy** |
| P3 | Load-bearing-both | **~1,800 pairs** | V2-stub cluster (110 files × 1,770 pair combos); playbook vs authoring-sessions; sibling phase/ratification envelopes; app-brief template family; cross-domain audit siblings. All `keep_as_is`. |

**Coverage distribution (v1.1 schema):**
- `structural_only`: 792 files (all — pairwise similarity walk, not per-claim walk)
- `full_claim_walk`: 0
- `deferred`: 0

**Migration queue frozen post-D-verdict. Routing target:** future §3
execution arc that opens after Group 2800 canonical summary (`2899`)
ratifies. Not this arc's execution job (parent §5 non-goals).

**Chris judgment queue (accumulating for 2899):** the 2 P2 needs-judgment
rows from T3a are the FIRST entries in the Group 2800 arc-close judgment
queue. T3b/T4/T5 will contribute additional rows; 2899 canonical summary
consolidates for single-session workshop resolution.

## 4. Schema state

**Parent §10.1 schema UNCHANGED at v1.1.** T3a inherits from S2834's
frontmatter `schema_version: 1.1` and does not modify.

**v1.2 candidates recorded as future_trigger for 2899 close** (three
witnesses across children):

- T3a §5.3 — `coverage_content_dup` third axis for pairwise-similarity
  coverage semantics (extending T2 §5.7 `coverage_refs`/`coverage_claims`
  proposal). **Three-witness signal now confirmed** — the parent §10.1
  schema-modification threshold recorded for 2899 close deliberation.
- T3a §5.5 — `template_family: <slug>` field for load-bearing-both rows
  sharing a common origin template (app-brief cluster, ratification
  envelope siblings).
- T3a §5.7 — `judgment_state: known | ambiguous` field for
  `duplicate_content` rows requiring canonical designation. **Option C**
  preferred as most additive (backward-compat with v1.1).

**Acceptance criteria for any 2899 v1.2 amendment (§5.3 (i)-(iv)):**
- (i) Purely additive
- (ii) Backward-compatible (unknown-key parser tolerance)
- (iii) Parser-compat plan (consumer scripts smoke-tested)
- (iv) Documented deprecation path

Absent any of (i)-(iv), deferral to a later close is the safer default.

## 5. Arc registration

Group 2800 arc state after S2836 T3a close:

- ✅ Parent scoping RATIFIED at S2833 (D1-D9)
- ✅ T1 anchor content audit RATIFIED at S2834 (schema v1.1 locked)
- ✅ T2 reference-graph audit RATIFIED at S2835 (§10.1 schema unchanged; v1.2 future_trigger recorded)
- ✅ **T3a duplicate-content audit RATIFIED at S2836 (§10.1 schema unchanged; NEW arc-level deferral policy for `escalate_to_chris` rows; T3a↔T5 boundary rule adopted)**
- ⏳ T3b orphan & reachability audit — V2-stub file list from T3a §2.3 available as reachable-only-from-search skip-list
- ⏳ T4 handoff citation-integrity + retrieval-harm audit
- ⏳ T5 reports + audits triage (T3a's SESSION_819 + PA_TOOLS_GAP_MAP recommendations subject to T5 override per §5.6)
- ⏳ 2899 canonical summary — accumulating Chris judgment queue starts here; v1.2 amendment consolidation

**Arc registered:** `docs/research/OPEN_ARCS.md` Group 2800 row advanced
from "T2 RATIFIED; T3a next" to "T3a RATIFIED; T3b next" (4 of 6 shipped).

## 6. Twin-pointer artifacts

**Repo:**

- Content: `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
- Envelope: this file
- Handoff: `docs/handoffs/SESSION_2836_T3A_DUPLICATE_CONTENT_AUDIT.md`
- Scanner tool: `tools/audit_2803a_duplicate_content.py` (preserved as audit artifact)
- Scanner output (raw top-2000): `/tmp/t3a_dup_scan_out_full.json`
- Scanner output (V2-stub-filtered): `/tmp/t3a_dup_scan_substantive.json`
- T2 pre-clustering seed consumed: `/tmp/t2_scan_out.json`
- Arc manifest: `docs/research/OPEN_ARCS.md` (Group 2800 In-progress row updated 3→4 of 6)

**Workspace UI (per `feedback_twin_deliverable_at_every_ratification` +
`feedback_rigby_writes_workspace_deliverables` established at S2835):**

- Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
- Twin: content mirror + ratification envelope
- **Rigby creates the workspace deliverables via PA `deliverable_tool.create`**,
  NOT Claude via ORM-direct. Claude routes explicit instruction post-merge;
  Claude verifies tool_runs + ORM cross-check. Any post-create diagnostic-status
  fix (per known bug `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`)
  is post-Rigby-tool-surface exercise, not primary create path. **Second
  exercise of the new pattern** (T2 close was first at S2835).

## 7. New governance patterns established at S2836

1. **Cross-child `escalate_to_chris` deferral to arc close** — per
   Chris D-verdict, all `escalate_to_chris` rows across T3a/T3b/T4/T5
   accumulate to `2899`, not resolved child-by-child. This generalizes
   as a POLICY for multi-child audit arcs where subject-matter judgment
   benefits from cross-child context.

2. **T3a↔T5 boundary rule** — for multi-child arcs where child N's
   scope territorially overlaps with child M's, child N MUST NOT
   finalize disposition on M-territory files; classification only,
   with `<M>_may_override: YES` annotation on affected rows.

3. **v1.2 acceptance criteria (i)-(iv)** — codified pre-conditions for
   any schema amendment mid-arc or at arc close: additive +
   backward-compatible + parser-compat plan + deprecation path.
   Absent any, deferral to a later close is safer.

Recorded for parent §5 non-goals refinement + memory candidate
promotion at 2899 close.

## 8. Provenance

- **Session:** 2836
- **Pin:** `pa-90ea529a09234d57` (label `s2836-t3a-duplicate-content-audit`; retired at S2836 close with `force=true`, sixty-seventh consecutive per S2770+ pattern)
- **HEAD at draft:** `13e0cc52b7e3` (S2835 close cascade)
- **HEAD at ratification:** filled at close cascade PR merge
- **Playbook version:** v0.8.0 (unchanged; 205 rules)
- **Anti-rubber-stamp:** verified non-empty tool_runs across both SIGN cycles; caught 3 real F-BLOCKING refinements (runner-independence proof; needs-judgment sub-classification; T3a↔T5 boundary rule)
- **Joint agreement:** reached per `feedback_claude_rigby_agree_first_chris_yes_no`
- **Rigby-writes-workspace-deliverables rule:** second exercise (T2 close at S2835 was first)
- **Post-merge recycle:** `make recycle-all` per PLAYBOOK-7.4.4 (eighty-second consecutive close-cycle)

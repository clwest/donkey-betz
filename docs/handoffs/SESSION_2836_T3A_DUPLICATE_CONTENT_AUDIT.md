---
title: "S2836 — T3a duplicate-content audit RATIFIED (child audit 2803a · schema v1.1 unchanged · escalate_to_chris deferral policy established)"
session: 2836
date: 2026-07-19
status: shipped
research_group: 2800
thread: T3a
sign_pin: pa-90ea529a09234d57
sign_cycles: 2
ratifier: Chris
verbatim_directive: "Continue on but let's defer the two issue and any others like it until we have the /docs/ audit completed incase other issues come up"
---

# S2836 — /docs/ Content Audit · T3a duplicate-content audit RATIFIED

## 1. Session opener

Chris opened S2836 with "Please begin" per session brief. Per
`context-kit orient` + S2835 close pointer, this session had a ratified
default direction from Chris's S2835 D-verdict pointer: *"T3a opens at
S2836."* Sanity checks all green at open:

- pg15 (donkeyking) started + owns port 5432
- HEAD `13e0cc52b7e3` (S2835 close cascade merged as PR #3283)
- Backfill: 0 mismatches (13 out-of-scope per Chris D6, unchanged)
- Pattern C top-1: `00-START-NEXT-SESSION.md` → `self_reference` ✅
- Pattern B top-1: `docs/PLATFORM_INVENTORY.md` → `count` ✅
- Parity harness + registry + diagnostics: 47 passed in 193.71s ✅

Candidate menu presented per `feedback_engineering_bias_over_audit` —
listed net-new engineering pivots alongside the ratified T3a default
from S2835 close pointer. Chris picked B (ratified default): open T3a
duplicate-content audit.

Fresh pin minted at first-action: `pa-90ea529a09234d57` (label
`s2836-t3a-duplicate-content-audit`).

## 2. What shipped

| Focus | Artifact | Location |
|---|---|---|
| T3a child audit (792-file scan; MinHash-style token-shingling; consumed T2 §5.6 pre-clustering seed) | New | `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md` (~944 lines, status ratified) |
| T3a scanner tool | New | `tools/audit_2803a_duplicate_content.py` |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 4/6 shipped) |
| S2836 handoff | New | THIS FILE |
| S2837 pointer | Updated | `00-START-NEXT-SESSION.md` — recommended default = T3b orphan & reachability audit |
| New memory candidate | Recorded | `escalate_to_chris` cross-child deferral policy (generalized pattern for multi-child audit arcs) |

## 3. Scanner method + real signal

`tools/audit_2803a_duplicate_content.py` — 5-word overlapping token
shingles as sets; inverted-index build; pairwise Jaccard scoring;
containment_A / containment_B for subset-overlap; consumed T2's
`/tmp/t2_scan_out.json` RENAMED map as free basename pre-clustering
signal per T2 §5.6. Run cost ~3 seconds over 792 files.

**Raw scan output** (`/tmp/t3a_dup_scan_out_full.json`):
- 7,246 pairs above Jaccard 0.10 threshold
- Top-2000 breakdown:
  - 171 SESSION_819 intra-cluster (Jaccard 0.928-0.960)
  - 1,828 V2-pointer-stub-vs-V2-stub pairs (Jaccard ~0.86)
  - 1 substantive non-cluster pair (PA_TOOLS_GAP_MAP_S2795/S2796)

**Post-manual-classification defect population:**

| Sev | Files/pairs | Class | Action |
|---|---|---|---|
| **P0** | 0 | — | §10.4(b) root-stability gate NOT triggered |
| **P1** | 19 files / 171 pairs | SESSION_819_SYSTEM_AUDIT_* cluster | `archive` to `docs/archive/2026-07/audits/session_819_snapshots/`; runner-independence proven (Rigby zero-match grep in `core/management/commands/`); parallel runner-fix ticket |
| **P1** | 2 files / 1 pair | PA_TOOLS_GAP_MAP_S2795/S2796 | `consolidate_into S2796` (or `retrofit_v2_pointer`) |
| **P2** | 2 pairs | Needs-judgment (canonical-ambiguous) | **DEFERRED to `2899` per S2836 D-verdict new policy** |
| **P3** | 110 files / ~1,770 pairs | DOC-POINTER-V2 stub cluster | `keep_as_is` — DOC_LIFECYCLE §1 intentional link-rot forwarders |
| **P3** | ~10 pairs | Playbook vs authoring / sibling phase docs / app briefs / cross-domain audits | `keep_as_is` — orthogonal-purpose pairs |

## 4. Rigby SIGN

### Cycle 1 — 1 AGREE + 4 STRENGTHEN

**Anti-rubber-stamp verified** per
`feedback_verify_rigby_tool_runs_before_trusting_sign` — Rigby's
tool_runs were substantive and non-empty across every verdict:

- `repo_tool.read` DOC_LIFECYCLE.md §1 + 3 sample V2 stubs (lines 1-8 each)
- `repo_tool.search "SESSION_819"` in `core/management/commands/` → **zero matches** (runner-independence proof)
- `repo_tool.read` parent 2800 §4 T3a rubric text
- `search_docs "schema v1.1 locked"` → 5 chunks
- `repo_tool.read` 2801 §10.1 + 2800 §4 T5 spec

| Q# | Verdict | Refinement folded into 2803a |
|---|---|---|
| Q1 V2-stub classification | AGREE | No change — DOC-POINTER-V2 stubs load-bearing per DOC_LIFECYCLE §1 |
| Q2 SESSION_819 archive-vs-runner-fix ordering | STRENGTHEN | §2.1 runner-independence proof + §4.1 parallel-track note |
| Q3 escalate_to_chris as own severity class | STRENGTHEN | §2.4-§2.5 `needs-judgment` sub-classification + §5.7 v1.2 Option C candidate |
| Q4 v1.2 schema mid-arc amendment | STRENGTHEN | §5.3 acceptance criteria (i)-(iv) codified |
| Q5 zoom-out — scope creep + T3a↔T5 coupling | STRENGTHEN | §5.6 T3a↔T5 boundary rule + `t5_may_override` annotations |

### Cycle 2 — 4/4 AGREE (fold verification)

Cycle 2 re-read §2.1 (lines 232-246), §4.1 (lines 600-610),
§2.10 (lines 467-555), §3 (lines 564-569), §2.4 (lines 331-349),
§2.5 (lines 354-370), §5.3 (lines 682-695), §5.6 (lines 734-746),
§5.7 (lines 774-785).

| Q# | Fold verified | Verdict |
|---|---|---|
| Q6 | Q2 fold (runner-independence + parallel tracks + T5-may-override) | AGREE |
| Q7 | Q3 fold + YAML sample sync-with-text (per S2835 Q7 lesson) | AGREE |
| Q8 | Q4 fold (§5.3 (i)-(iv) criteria) | AGREE |
| Q9 | Q5 fold (§5.6 boundary + §5.7 Option C) | AGREE |

Convergence at cycle 2 = 4/4 AGREE with cited line evidence.

### Anti-rubber-stamp real F-BLOCKING catches

1. **Cycle 1 Q2 runner-independence proof.** Without Rigby's zero-match
   grep in `core/management/commands/`, §4.1 would have framed archive
   as sequentially blocked on runner-fix determination — the fold makes
   the two tracks parallel.
2. **Cycle 1 Q3 needs-judgment sub-classification.** Without this fold,
   §4.2 would ship as a single `escalate_to_chris` bucket obscuring
   the difference between known-canonical-target and canonical-ambiguous
   workflow states.
3. **Cycle 1 Q5 T3a↔T5 boundary.** T3a might have shipped preempting
   T5's disposition authority over `docs/audits/**` files. §5.6 codifies
   the child-boundary rule; §4.1 rows carry `t5_may_override: YES`.

## 5. Chris D-verdict + NEW ARC-LEVEL POLICY

Chris D-verdict verbatim: *"Continue on but let's defer the two issue
and any others like it until we have the /docs/ audit completed incase
other issues come up."*

**Interpretation applied:** all `recommended_action: escalate_to_chris`
rows across Group 2800 child audits (T3a, T3b, T4, T5) **DEFER** to
arc close (`2899` canonical summary session), NOT resolved child-by-
child.

**Rationale:** judgment on canonical designation benefits from
cross-child context that only emerges AFTER T3b/T4/T5 complete their
scans. Batch resolution at `2899` = single "Chris judgment session
workshop" ratifying all deferred rows together.

**Effect on T3a's own findings:**

- §2.4 SYSTEM_ARCHITECTURE_MAP vs SYSTEM_MAP → `escalate_to_chris` DEFERRED to 2899
- §2.5 CLAUDE_CONTEXT_SYSTEM_PACK vs SYSTEM_FULL_ACTIVATION_PLAN → `escalate_to_chris` DEFERRED to 2899

**Effect on future child authors:** T3b/T4/T5 authors do NOT loop Chris
in mid-arc on canonical-ambiguous findings; accumulate into the
Chris judgment queue for arc close.

**Effect on 2899 canonical summary:** MUST include consolidated Chris
judgment queue section listing all deferred rows across all T-threads
with cross-child context, ready for a single-session workshop.

Recorded in T3a §4.4 (this arc) + envelope §7 (new governance
patterns) + `feedback_arc_close_deferral_for_escalate_to_chris.md`
memory candidate (generalized pattern for multi-child audit arcs).

## 6. Follow-up carry

**For T3b (S2837 recommended default):**

- Pre-clustering skip-list from T3a §2.3 — 110 V2-stub files that are
  intentionally reachable-only-from-search; expected orphan candidates
  under naïve check; classify separately per §5.4.
- SESSION_819 cluster (19 files, from T3a §2.1) — inherited archive
  disposition; T3b should treat as pre-classified, not re-analyze.
- Cross-child `escalate_to_chris` deferral policy applies to T3b
  findings starting at first authoring — accumulate into 2899
  judgment queue, not resolved mid-arc.

**For T5 (T3a-produced audits-triage input):**

- SESSION_819 archive recommendation carries `t5_may_override: YES` —
  T5 MAY prefer rotate-and-retain-latest-N over full archive
- PA_TOOLS_GAP_MAP consolidation carries `t5_may_override: YES` — T5
  MAY prefer `retrofit_v2_pointer` over `consolidate_into` based on
  external-citation analysis

**For 2899 canonical summary:**

- Three v1.2 schema candidates recorded across T2/T3a: `coverage`
  split (T2 §5.7 + T3a §5.3 = third witness); `template_family` field
  (T3a §5.5); `judgment_state` field (T3a §5.7). §5.3 (i)-(iv)
  acceptance criteria gate any amendment.
- Chris judgment queue starts with T3a §2.4/§2.5 rows; grows with
  T3b/T4/T5 additions.

**Escalations recorded (deferred, not routed):**

- 2 T3a P2 needs-judgment rows (arch maps + system-pack docs)
- 1 potential SESSION_819 runner-fix follow-up (Chris directive on
  overwrite-vs-append policy)
- 3 v1.2 schema-refinement candidates

## 7. Lessons for next session

1. **`escalate_to_chris` accumulates to arc close** in multi-child
   audit arcs — do NOT route mid-arc unless the deferral cost outweighs
   the cross-child-context benefit.
2. **Rigby's grep-based zero-match** is a first-class runner-independence
   proof — cheaper and stronger than "we assume no dependency."
3. **Boundary rules between adjacent child audits** matter more than
   in-child rigor when arcs have territorial overlap (T3a↔T5 pattern).
4. **YAML sample sync-with-text discipline** (S2835 Q7 lesson) held —
   cycle 2 Q7 caught the SYSTEM_ARCHITECTURE_MAP sample gap during
   review and it was folded pre-D-verdict.
5. **Three-witness threshold for schema amendment** now reached for
   `coverage` axis split. 2899 close is the natural amendment
   window; acceptance criteria (i)-(iv) apply.
6. **Rigby writes workspace deliverables** — second exercise of the
   S2835-established pattern; ORM-direct fallback only if Rigby's
   tool surface fails.

## 8. Twin-pointer card

📁 **Repo — S2836 artifacts:**

- **T3a audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md`
- **Handoff:** THIS FILE
- **Scanner tool:** `tools/audit_2803a_duplicate_content.py`
- **Scanner output (raw):** `/tmp/t3a_dup_scan_out_full.json`
- **Scanner output (V2-stub-filtered):** `/tmp/t3a_dup_scan_substantive.json`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 4/6 shipped)
- **Rigby SIGN conversation:** `pa-90ea529a09234d57` (2 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2836 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope**: **Rigby creates** in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create` per `feedback_rigby_writes_workspace_deliverables` (second exercise); category `governance`; `deliverable_type=ratification_record`. Claude routes explicit instruction post-merge with content body + envelope body + workspace ID + create spec; Claude verifies tool_runs + ORM cross-check.

## 9. Provenance

- **Session:** 2836
- **Pin:** `pa-90ea529a09234d57` (label `s2836-t3a-duplicate-content-audit`; retired at close force=true, sixty-seventh consecutive)
- **HEAD at open:** `13e0cc52b7e3` (S2835 cascade)
- **HEAD at close:** filled at PR merge
- **Playbook version:** v0.8.0 (unchanged; 205 rules)
- **Rigby SIGN cycles:** 2 (cycle 1: 1 AGREE + 4 STRENGTHEN; cycle 2: 4/4 AGREE)
- **Anti-rubber-stamp:** verified — tool_runs non-empty across both cycles; 3 real F-BLOCKING refinements caught
- **Joint agreement:** reached per `feedback_claude_rigby_agree_first_chris_yes_no`
- **Post-merge recycle:** `make recycle-all` per PLAYBOOK-7.4.4 (eighty-second consecutive)
- **Close-cascade PR:** filled at merge

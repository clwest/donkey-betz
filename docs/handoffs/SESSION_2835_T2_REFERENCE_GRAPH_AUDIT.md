---
title: "S2835 — T2 reference-graph audit RATIFIED (child audit 2802 · §10.1 v1.1 schema unchanged · ADR-0000 disposition escalation surfaced)"
session: 2835
date: 2026-07-19
status: shipped
research_group: 2800
thread: T2
sign_pin: pa-0de182aaedcf43f0
sign_cycles: 2
ratifier: Chris
verbatim_directive: "ratify T2 as-folded"
---

# S2835 — /docs/ Content Audit · T2 reference-graph & broken-refs audit RATIFIED

## 1. Session opener

Chris opened S2835 with "Please begin" per session brief. Per
`context-kit orient` + S2834 close pointer, this session had a ratified
default direction from Chris's S2834 D-verdict (S2834 handoff §5:
"T2 opens at S2835"). Sanity checks all green at open:

- pg15 (donkeyking) started + owns port 5432
- HEAD `288259386b3a` (S2834 close cascade merged as PR #3281)
- Backfill: 0 mismatches (13 out-of-scope per Chris D6, unchanged)
- Pattern C top-1: `00-START-NEXT-SESSION.md` → `self_reference` ✅
- Pattern B top-1: `docs/PLATFORM_INVENTORY.md` → `count` ✅
- Parity harness + registry + diagnostics: **47 passed in 192.06s** ✅

Candidate menu presented per `feedback_engineering_bias_over_audit` —
listed net-new engineering pivots (BettingPage first-user trace / Colorado
Phase 4 statute-citation pass / new Workspace tab or PA tool) alongside
the ratified T2 default. Chris picked T2.

**S2835 open memory addition** (Chris directive mid-session): established
`feedback_rigby_writes_workspace_deliverables` — the twin workspace mirror
at arc close is Rigby's job via PA `deliverable_tool.create`, NOT Claude's
ORM-direct create. Corrects the S2834 pattern where Claude bypassed
Rigby's tool surface. Extends `feedback_twin_deliverable_at_every_ratification`
on WHO does the create.

## 2. Ship

| Focus | Artifact | Location |
|---|---|---|
| T2 child audit (791-file / 4-class ref-graph scan + Rigby-folded findings + v1.1 schema unchanged) | New | `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md` (~950 lines post-folds, status ratified) |
| T2 scanner tool | New | `tools/audit_2802_reference_graph.py` (preserved as audit artifact) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 2→3 of 6 shipped) |
| S2835 handoff | New | This file |
| S2836 pointer | Updated | `00-START-NEXT-SESSION.md` — recommended default = T3a duplicate-content audit |
| Memory addition | New | `feedback_rigby_writes_workspace_deliverables.md` + `MEMORY.md` index update |

## 3. What T2 caught

### 3.1 Scan aggregate

| Ref class | Total refs | PASS | BROKEN_404 | RENAMED | AMBIGUOUS |
|---|---:|---:|---:|---:|---:|
| md_link | 1,225 | 92.5% | 0.6% (7 raw) | 0.3% (4 raw) | 6.6% (81 raw) |
| session | 128 | 86.7% | 13.3% (17 raw) | 0 | 0 |
| adr | 130 | 71.5% | 28.5% (37 raw) | 0 | 0 |
| file_cite | 25,417 | 58.1% | 9.6% (2,441 raw) | 27.8% (7,060 raw) | 4.6% (1,160 raw) |
| **Total** | **26,900** | **59.8%** | **9.3%** | **26.3%** | **4.6%** |

Files with ≥1 defect: 551 of 791 (69.7% raw defect rate; heavily reduced
post-Rigby-fold FP-1/FP-2/FP-3 disposition).

### 3.2 Post-Rigby-fold defect population

| Sev | Class | Count | Notes |
|---|---|---:|---|
| **P0** | — | **0** | Both would-be P0s downgraded per Rigby cycle-1 Q3 DISAGREE; §10.4(b) root-stability P0 gate NOT triggered |
| P1 | Real BROKEN | ~9 | SESSION_1099 (PLATFORM_WHAT_IT_IS refresh-block, Q3 fold) + ADR-0000 (workspace-absent per Q1 DISAGREE, escalate_to_chris) + 4 md_link RENAMED playbook path-depth errors + ~3 additional research_os_anchor/playbook_adr_ratification BROKEN |
| P2 | Real BROKEN | ~30-50 | WorkspacePageNew.ts typo (D-bucket, Q3 fold) + 13 NEW real broken SESSION_NNNN gaps (per Q2 STRENGTHEN — beyond HANDOFF_NUMBERING_GAPS.md's SESSION_198/205 catalog) + closed_research_arc + audits_reports |
| P3 | Info + `ok` + FP-downgraded | remainder | 36 FP-1 ADR resolutions + ~6,000 FP-2 bare-basename RENAMED + FP-3 regex over-matches |

### 3.3 Schema state

Parent §10.1 schema **UNCHANGED at v1.1**. Rigby cycle-1 Q4 DISAGREE
proposed v1.2 `coverage_refs`/`coverage_claims` split — NOT applied at T2
per S2834 "no schema mod without fresh SIGN + D-verdict" boundary.
Recorded as §5.7 future_trigger for 2899 close.

All 791 files uniformly labeled `coverage: structural_only` under
current v1.1 semantics (T2 scans REFERENCE existence, not semantic
line-range claims per §1.4 anti-pattern).

### 3.4 Chris escalation surfaced

**ADR-0000 disposition** (§4.1 row 2): Rigby cycle-1 Q1 workspace
enumeration confirmed 5 of 6 Cycle 1A ADRs resolve as workspace deliverables
(0110/0120/0130/0140/0150) but **ADR-0000 was NOT found**. Cited by ≥1
source doc. Disposition options for Chris:
- (a) numbering placeholder never intended to ship as deliverable
- (b) authored elsewhere (repo doc, external system) — identify canonical location
- (c) authored but workspace deliverable archived/deleted — reconstruct or annotate

Awaits Chris directive.

## 4. Rigby SIGN provenance (2 cycles)

| Cycle | Q# | Tool_runs verified? | Verdicts |
|---|---|---|---|
| 1 | Q1..Q5 | ✅ 10+ substantive (`deliverable_tool.list` workspace enumeration + `repo_tool.read` on HANDOFF_NUMBERING_GAPS.md, PLATFORM_WHAT_IT_IS.md, 00-START-NEXT-SESSION.md, T2 §1.4/§2.3/§6.1) | 3 DISAGREE (Q1/Q3/Q4) + 2 STRENGTHEN (Q2/Q5) |
| 2 | Q6..Q8 | ✅ 5+ substantive `repo_tool.read` on fold-target sections | Q6 AGREE + Q7 DISAGREE-→-AGREE-post-fix + Q8 AGREE |

Anti-rubber-stamp discipline verified across both cycles per
`feedback_verify_rigby_tool_runs_before_trusting_sign`. **Anti-rubber-stamp
caught 2 real F-BLOCKING refinements:**
- Cycle 1 Q1: ADR-0000 workspace-absent split from FP-1 sweep (Rigby's
  `deliverable_tool.list` evidence over workspace `a9a16593-...`)
- Cycle 2 Q7: §2.9 YAML sample severity fold lag caught (Rigby's
  `repo_tool.read` lines 430-490 verified P0 stragglers on both PLATFORM_WHAT_IT_IS
  + 00-START-NEXT-SESSION samples despite §2.8/§3/§4.1 text downgrades)

Both would have shipped incorrect artifacts had Rigby rubber-stamped.

Joint Claude+Rigby agreement reached per
`feedback_claude_rigby_agree_first_chris_yes_no` before Chris D-verdict.
Rigby final verdict: *"YES — cycle 1 concerns are folded and cycle 2
verification is all AGREE with tool-backed evidence, so it's ready for
Chris D-verdict."*

## 5. Arc state at S2835 close

- **Group 2800 /docs/ content audit arc**: **3 of 6 shipped** (parent + T1 + T2).
  T3a opens at S2836.
- **Group 2700 /docs/ restructuring arc**: CLOSED at S2817; §3 target
  tree RATIFIED at S2832; §7 anchor updates + §8 follow-on queue
  DEFERRED. (Unchanged.)
- **Discovery-layer arc (S2818-S2831)**: unchanged. Pattern B/C/D +
  DORMANT registry Step 1 + user-facing diagnostics tab all intact.
- **Metadata layer**: ✅ 0 mismatches (S2829 substrate intact).
- **Colorado Family Law**: Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1/3.2/3.1 P1.b/4a ✅ (unchanged).

## 6. Follow-up work carried

### 6.1 T3a opens at S2836 (recommended default)

- Author `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
- Scope: ~810-file corpus (786 non-handoff + 24 code-review); token-shingling / MinHash near-dup detection
- Method: mechanical shingle → top-K pair candidates → manual severity review on top ~100 pairs
- Emit v1.1 findings per §10.1 schema locked at S2834 (all rows inherit `schema_version: 1.1`)
- **Pre-scan hint inherited from S2834 §4.1a:** topics tagged `count_dense` vs `narrative` before dup detection
- **Pre-clustering signal from T2 §5.6:** basename RENAMED map from T2 output identifies files sharing basenames — free duplicate-candidate seed
- Rigby joint SIGN + Chris D-verdict

### 6.2 Alternatives available at S2836 open (per engineering-bias rule)

Same net-new engineering candidates as S2835 open still available:
- BettingPage first-user trace — Chris IS the first user; real capability
- Colorado Phase 4 statute-citation quality pass — personal legal work
- New Workspace tab / PA tool — pick a concrete gap

### 6.3 Migration queue (deferred to future §3 execution arc post-2899)

Per §10.1 v1.1 schema, batched by `migration_pr_batch_hint`:

- `ref_graph_repair` batch (T2-originated): SESSION_1099 P1 in PLATFORM_WHAT_IT_IS.md:46 + ADR-0000 P1 escalate_to_chris + 4 playbook_v0_1 path-depth P1 (2 files × 2 lines each) + WorkspacePageNew.tsx typo P2 in 00-START-NEXT-SESSION.md:73 + 13 real broken SESSION_NNNN gaps P2 across 6 playbook-authoring + closed-research docs + ~600-1,000 file_cite BROKEN_404 real defects (preserved in `/tmp/t2_scan_out.json` scanner output)
- `schema_validation` batch (T2-originated): 3 resolver methodology enhancement items (workspace-aware ADR + repo-root-relative + bare-basename discrimination) recorded in T2 §4.7

Existing S2834 T1 batches unchanged (`anchor_docs` batch for CLAUDE.md line 262 P0 discord count fix + KNOWLEDGE_PIPELINE line 25 P1 spider count + AGENTS/SPIDERS V1 banner retrofit + DISCORD_INTEGRATION line 321 P2 slash-commands count).

### 6.4 Chris directives requested

- **ADR-0000 disposition** (surfaced from T2 §4.1 row 2 escalate_to_chris)
- v1.2 `coverage_refs`/`coverage_claims` schema split — evaluate at 2899 close

## 7. Lessons to carry

1. **Anti-rubber-stamp discipline caught 2 real F-BLOCKING refinements
   across the arc.** Both would have shipped defect artifacts had Rigby
   rubber-stamped. Substantive tool_runs are a GATE, not a check-box.
2. **`deliverable_tool.list` workspace enumeration IS the ADR resolver
   for Cycle 1A ADRs.** A filesystem-only mechanical grep will always
   miss workspace-canonical governance artifacts. Future T2-follow-up
   resolver must query workspace.
3. **YAML sample sync-with-text fold discipline.** When a table / prose /
   histogram downgrades a severity, the YAML sample rows ARE part of the
   fold surface. Cycle 2 Q7 caught this. Next audit's cycle-2 verification
   MUST re-read sample rows.
4. **Coverage semantics under v1.1 are load-bearing** — `structural_only`
   for T1 (claim-walk of load-bearing claims only) vs T2 (ref-graph walk
   only) both fit the label but overload it. v1.2 split is a real refinement
   candidate for 2899.
5. **Rigby writes workspace deliverables** (new memory established at
   S2835 open per Chris directive). Claude writes repo files + routes
   explicit instruction to Rigby + verifies via tool_runs + ORM cross-check.
   First exercise: T2 close (this cascade). Watch for drift.
6. **Ship-with-loud-limitations is a valid audit stance.** Rigby Q5
   STRENGTHEN validated: T2's honest FP-1/FP-2/FP-3 catalog + §6 residual
   line-range risk is MORE valuable to migration-arc consumers than a
   cleaner defect list that hides methodology gaps.

## 8. DO NOTs to carry to S2836

Per parent §7 anti-scope + child inheritance + S2834 DO NOTs + new S2835
additions:

1. **DO NOT execute any /docs/ file operations during Group 2800.**
2. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.**
   Locked at S2834; v1.2 candidate recorded as §5.7 future_trigger, NOT applied.
3. **DO NOT collapse T3a/T3b back into single T3** — S2833 Rigby cycle-1
   Q1 STRENGTHEN evidence stands.
4. **DO NOT expand T4 into per-handoff content review.**
5. **DO NOT reduce §10 P0..P3 severity or 8-action taxonomy.**
6. **DO NOT audit in-flight arc children** (per parent §7 anti-scope).
7. **DO NOT wire `INTENT_MECHANISMS` into `search_embeddings()` without
   fresh SIGN + fresh Chris D-verdict** — S2830 Step 2 hard boundary.
8. **DO NOT couple new observability surfaces to log capture** — S2831
   Rigby Q2 substrate rule.
9. **DO NOT relax hard-caps on the S2831 endpoint** — server-side DOS boundary.
10. **DO NOT relax `--apply` guard on backfill** — S2829 stop-writer contract.
11. **DO NOT relax sync skip-branch status refresh** — S2829 2nd-order defect closure.
12. **DO NOT collapse Pattern B/C/D anchor maps / bonuses / gate patterns** — design §3 anti-collapse invariant.
13. **DO NOT touch 13 out-of-index rows** — Chris D6 deferred.
14. **DO NOT relax whole-string `^...$` invariant on Pattern D patterns** — pytest guards.
15. **DO NOT populate `_parallel_both` in Phase-0.5** — advisory-only-vs-execution boundary.
16. **DO NOT add numeric confidence fields anywhere** — categorical-only per Chris R4/§10.4.
17. **DO NOT bypass Rigby for workspace deliverable creation** — new
    S2835 rule per `feedback_rigby_writes_workspace_deliverables`. Fall
    back to ORM only if Rigby genuinely cannot execute; state the reason
    in the handoff.

## 9. Twin-pointer artifacts

📁 **Repo — S2835 artifacts:**

- T2 audit doc (RATIFIED): `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`
- Ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md`
- Handoff: this file
- Scanner artifact: `tools/audit_2802_reference_graph.py`
- Arc registration: `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 3/6 shipped)
- Rigby SIGN conversation: `pa-0de182aaedcf43f0` (2 cycles preserved before retirement)
- Merge SHA: filled at close-cascade PR merge

🖥️ **Workspace UI — S2835 twin-pointer workspace deliverables:**

- **NEW RULE PER `feedback_rigby_writes_workspace_deliverables`:**
  Rigby creates the twin workspace deliverables in Donkey Betz workspace
  (`b4503364-2573-4401-9e28-61a739e0ce50`) via `deliverable_tool.create`.
  NOT Claude via ORM-direct. Claude routes explicit instruction post-merge
  with content mirror + ratification envelope body + workspace ID + category
  + deliverable_type spec. Claude verifies Rigby's tool_runs + ORM
  cross-check post-create. Any known-bug diagnostic-status fix per
  `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` is
  post-Rigby-exercise, not primary create path.

## 10. Provenance

- **Session:** 2835
- **Author:** Claude Code + Rigby (joint SIGN 2 cycles) + Chris D-verdict
- **Pin history (S2835):**
  - `pa-0de182aaedcf43f0` (label `s2835-t2-reference-graph-audit`) minted at S2835 open turn 1; served as session pin + arc SIGN pin (2 cycles preserved); retired at S2835 close with `force=true` (sixty-sixth consecutive per S2770+ pattern)
- **HEAD at author time:** `288259386b3a`; HEAD at ratification: filled at cascade merge
- **Playbook version:** v0.8.0 (unchanged; 205 rules)
- **Post-merge recycle:** `make recycle-all` per PLAYBOOK-7.4.4 (eighty-first consecutive close-cycle)

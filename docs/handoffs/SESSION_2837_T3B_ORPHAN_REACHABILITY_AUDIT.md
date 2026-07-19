---
title: "S2837 — T3b orphan-and-reachability audit RATIFIED (child audit 2803b · schema v1.1 unchanged · escalate deferral carries over from S2836)"
session: 2837
date: 2026-07-19
status: shipped
research_group: 2800
thread: T3b
sign_pin: pa-7ebe273640e14691
sign_cycles: 3
ratifier: Chris
verbatim_directive: "ratify T3b as-folded"
---

# S2837 — /docs/ Content Audit · T3b Orphan-and-Reachability Audit RATIFIED

## 1. Session opener

Chris opened S2837 with "Please begin" per session brief. Per
`context-kit orient` + S2836 close pointer, this session had a
ratified default direction from Chris's S2836 D-verdict pointer:
*"T3b opens at S2837."* Sanity checks all green at open:

- pg15 (donkeyking) started + owns port 5432
- HEAD `be7af72159ec` (S2836 close cascade merged as PR #3285)
- Backfill: 0 mismatches (13 out-of-scope per Chris D6, unchanged)
- Pattern C top-1: `00-START-NEXT-SESSION.md` self_reference ✓
- Pattern B top-1: `docs/PLATFORM_INVENTORY.md` count ✓
- Parity harness: 47/47 in 192.72s ✓

Per `feedback_engineering_bias_over_audit`, presented candidate menu
with net-new engineering pivots FIRST plus ratified T3b default.
Chris picked B (ratified default): open T3b orphan-and-reachability
audit.

## 2. Fresh SIGN pin minted

`session_lifecycle open --label s2837-t3b-orphan-reachability-audit`:

- Old pin retired: `pa-90ea529a09234d57` (S2836; T3a)
- New pin: `pa-7ebe273640e14691` (label `s2837-t3b-orphan-reachability-audit`)
- Wrapper `tools/pa_local.sh` updated to point at fresh pin
- Freshness: FRESH · head=be7af72159ec · celery_stale=0/5
- **Sixty-eighth consecutive fresh-mint at session open** per S2770+ pattern

## 3. Scanner build + run

**Tool authored:** `tools/audit_2803b_orphan_reachability.py` (~570 lines
post cycle-2 folds; consumes T3a §5.4 V2-stub direct-marker scan +
T2 §5.6 RENAMED basename map).

**Method per parent §4 T3b:**
- Graph (a) CLAUDE.md link-BFS through markdown-link + backtick-path syntax → **491 files reachable from anchor graph**
- Graph (b) `docs/INDEX.md` autogen refs flat-list → **106 files cited from docs/INDEX.md**
- Graph (c) `content.Document.file_path` corpus-inclusion → **792/3261 in-scope rows corpus-included**
- Top-K retrieval frequency for probe queries → deferred as `future_trigger` (§6.1(1) limitation; corpus-inclusion is load-bearing subset)

**Scanner outputs:** `/tmp/t3b_orphan_scan_out.json` (793 corpus rows, JSON emit for downstream §10.1 v1.1 YAML consumption).

**Corpus enumeration:** 793 non-handoff in-scope files (T3a had 792; +1 drift = one new file since S2835 close; no scope mutation).

## 4. Findings — 4 severity classes

**Positive headline:** ZERO unreachable-from-all-3-graphs files across the 793-file corpus. §10.4(b) root-stability P0 gate NOT triggered.

| severity_class | count | severity | recommended_action |
|---|---:|---|---|
| cited-multi-graph-OK | 490 | P3 | keep_as_is |
| reachable-from-search-only | 302 | P3 (most) / P2 (76 unclassified) | keep_as_is / escalate_to_chris |
| cited-but-search-invisible | 1 | P1 | escalate_to_chris (README.md) |
| unreachable-from-all-3-graphs | 0 | — | — |

**Sub-classification of 302 search-only-reachable** (reduces escalate volume ~4x via known-benign patterns):

| search_only_kind | count | disposition |
|---|---:|---|
| v2_pointer_stub | 74 | P3 keep_as_is (DOC_LIFECYCLE §1 pattern) |
| unclassified | 76 | P2 escalate_to_chris (2899 queue) |
| t5_territory | 41 | P3 keep_as_is + `t5_may_override: YES` |
| ratification_envelope | 38 | P3 keep_as_is (governance archives) |
| closed_arc_pack | 30 | P3 keep_as_is (docs/cleanup/ + docs/code-review/) |
| closed_research_arc_tool | 21 | P3 keep_as_is (docs/research/tools/validation/ ONLY) |
| implementation_arc_artifact | 13 | P3 keep_as_is |
| closed_research_arc_child | 9 | P3 keep_as_is |

**V2-stub direct-marker scan: 170 total** (stronger evidence than T3a §2.3 shingle-inference "110+" bound; 96 are anchor-cited AND search-reachable = healthy, 74 are search-only = still P3 by design).

## 5. Joint Claude+Rigby SIGN 3 cycles

### Cycle 1 — 5 pressure-test questions

**Tool_runs verified non-empty per anti-rubber-stamp rule.** Rigby ran `repo_tool.search "<!-- DOC-POINTER-V2"` (633 matches), read 3 sample V2 stubs (all first-1KB marker confirmed), `repo_tool.tree docs/research/tools` (27 entries), read `tools_validation_engineering_campaign_plan.md` line 5 ("awaiting Chris's review"), read scanner code.

- **Q1** V2-stub cluster shape: STRENGTHEN — repo-wide grep (633) inflated ~4x vs first-1KB scan (170); §1.5 warning added
- **Q2** SEARCH_ONLY_BENIGN_PATTERNS rigor: STRENGTHEN — narrow `docs/research/tools/` → `docs/research/tools/validation/` only; 4 top-level `tools_*.md` route to `unclassified` (Rigby real leak-catch: campaign plan is NOT closed)
- **Q3** T1 counter-signal ratification: DISAGREE-pending (honest failure to verify; anti-rubber-stamp working)
- **Q4** README build_docs_index sync boundary: DISAGREE-pending (honest failure to verify)
- **Q5** zoom-out: STRENGTHEN (truncated at Q5(a))

### Cycle 1b — Q3+Q4 verification with Claude-gathered evidence + Q5 completion

**Claude gathered evidence in parallel (grep + build_docs_index inspection + ORM query); routed to Rigby for independent tool-verification.**

Rigby ran `repo_tool.tree docs/topics depth=2` (21 topic files enumerated), `repo_tool.search "collaboration-protocol"` (4 total matches, ZERO anchor-graph citations), `repo_tool.search "video-upload"` (3 total, ZERO anchor citations), `repo_tool.read_file core/management/commands/build_docs_index.py:190-270` (line 200 root_doc list `['CLAUDE.md', '00-START-NEXT-SESSION.md']` — README.md NOT listed).

- **Q3** T1 counter-signal: AGREE `same_pr_mitigatable` — real T1 gap confirmed; §2.7 tail fold added with Rigby verification substrate
- **Q4** README P1: AGREE `same_pr_actionable` — 1-line fix-scope oversight, not intentional; §5.5 tail fold added with cited `build_docs_index.py:200` + ORM confirmation
- **Q5(a)** corpus-inclusion vs top-K: STRENGTHEN `future_trigger` — §6.1(1) limitation records deferral

### Cycle 2 — Q5(b)/Q5(c) completion + fold verification

- **Q5(b)** pattern-list false-negative-leak: STRENGTHEN `future_trigger`+`same_pr_mitigatable` — §5.7 sub-fold added: `implementation_arc_artifact` + `closed_research_arc_child` broad-prefix risk; two mitigation options (closed-arc sentinel marker OR arc-slug allowlist) as `future_trigger` for 2899
- **Q5(c)** T3a↔T5 coupling risk: STRENGTHEN — §5.4 fold added: T5 (2805) SHOULD ingest `/tmp/t3b_orphan_scan_out.json` at authoring, not re-derive graphs; `future_trigger` for 2805 spec

### Cycle 3 — 7/7 explicit AGREE + Q5(d) close-out

Rigby read all 7 fold-target sections with cited line numbers and returned **7/7 AGREE**. Q5(d) STRENGTHEN `future_trigger` on §6.1(7) — usage/salience metric NOT measured; histogram is structural, not behavioral; follow-up sub-arc could rank search-only files by probe-query top-K frequency or retrieval-log hit count.

**Anti-rubber-stamp discipline VERIFIED across all 3 cycles.** ~30+ substantive tool_runs (repo_tool.read_file × 15+, repo_tool.search × 8+, repo_tool.tree × 3). Rigby caught 3 real F-BLOCKING issues (Q1 grep-inflation risk, Q2 tools/ campaign-plan false-benign leak, Q5(d) salience blind spot).

## 6. Chris D-verdict (S2837)

> ratify T3b as-folded

**Ratified shape:**

- Full T3b audit doc (1213 lines post-fold at ratification) + all Rigby-folded refinements
- Schema §10.1 v1.1 UNCHANGED (three v1.2 candidates recorded as `future_trigger` for 2899)
- S2836 deferral policy carries over: 77 escalate rows (1 P1 + 76 P2) accumulate to 2899 workshop
- T3a↔T5 boundary rule GENERALIZED (§5.4)
- Migration queue frozen; routed to future §3 execution arc post-2899
- **5 of 6 Group 2800 threads shipped** (parent + T1 + T2 + T3a + T3b)

## 7. Lessons for S2838 T4 opening

1. **Cross-child pre-clustering consumption is now first-class pattern** — T3a consumed T2 §5.6 RENAMED map; T3b consumed T3a §5.4 V2-stub direct-marker scan. T4 SHOULD consume T3b's `/tmp/t3b_orphan_scan_out.json` for handoff reachability signal (per T3b §5.4 T5 workflow directive generalized).
2. **Anti-rubber-stamp discipline holds under pressure.** Rigby honestly declined Q3+Q4 when tool_runs were pending; not fake-AGREE. Route again with evidence + require independent verification.
3. **Sub-classification against known-benign patterns is ~4x escalate volume reduction.** T4 SHOULD sub-classify handoff citations by staleness + retrieval-harm class before flooding Chris judgment queue.
4. **Rigby's zoom-out routinely catches issues cycle 1 doesn't.** Continue including at least one zoom-out ask per SIGN cycle per `feedback_zoom_out_ask_per_rigby_sign`.
5. **Direct-marker scan > shingle-pair-inference for stub detection.** T3b's 170 direct hits beat T3a's "110+" shingle-inferred lower bound. T4 SHOULD prefer direct signal detection where feasible.

## 8. Ship artifacts (S2837 close)

| Focus | Artifact | Location |
|---|---|---|
| T3b child audit (793-file scan + 3-graph reachability + sub-classification) | New | `docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md` (~1213 lines post-fold, status ratified) |
| T3b scanner tool | New | `tools/audit_2803b_orphan_reachability.py` (~570 lines) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 5/6 shipped) |
| S2837 handoff | This file | `docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md` |
| S2838 pointer | Updated | `00-START-NEXT-SESSION.md` (recommended default = T4 handoff audit) |

## 9. Twin-pointer workspace deliverables (per `feedback_rigby_writes_workspace_deliverables`)

**Post-merge action for S2837 close:** Rigby creates BOTH content mirror
AND ratification envelope in Donkey Betz workspace
(`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create`.
Category `governance`; `deliverable_type=ratification_record` for the
envelope. Claude routes explicit instruction post-merge; Claude
verifies tool_runs + ORM cross-check.

---
title: "Ratification envelope — S2837 T3b orphan-and-reachability audit (child 2803b)"
date: 2026-07-19
session: 2837
ratifier: Chris
verbatim_directive: "ratify T3b as-folded"
target_doc: docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md
research_group: 2800
thread: T3b
parent_arc: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
predecessor_child:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md
  - docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md
sign_pin: pa-7ebe273640e14691
sign_cycles: 3
category: governance
deliverable_type: ratification_record
---

# S2837 — T3b orphan-and-reachability audit RATIFICATION

## 1. Ratification statement

Chris D-verdict at S2837 close (2026-07-19):

> ratify T3b as-folded

**Scope of ratification:**

- Full T3b audit doc (`2803b_docs_content_orphan_audit.md`) as authored + folded per Rigby cycle-1 refinements (Q1 grep-inflation warning + Q2 tools/validation narrowing) + cycle-1b completion (Q3 anchor-citation zero-match verification + Q4 build_docs_index root_doc list evidence + Q5(a) top-K retrieval limitation) + cycle-2 refinements (Q5(b) benign-pattern broadness + Q5(c) T3a↔T5 coupling risk callout) + cycle-3 close-out (7/7 explicit AGREE with cited line numbers + Q5(d) usage/salience limitation).
- Three-graph reachability scanner methodology (`tools/audit_2803b_orphan_reachability.py`) over 793 non-handoff in-scope files. Scanner preserved as audit artifact.
- **§10.1 v1.1 schema UNCHANGED.** Three v1.2 candidates recorded as `future_trigger` for 2899 close: (a) §5.3 `coverage_reachability` as fourth axis (third witness following T2 §5.7 + T3a §5.3); (b) §5.7 closed-arc sentinel marker OR arc-slug allowlist (mitigates `implementation_arc_artifact` + `closed_research_arc_child` broad-prefix false-negative-escalate-leak risk); (c) §6.1(7) usage/salience metric (histogram is structural not behavioral).
- **S2836 escalate-to-Chris deferral policy carries over.** 77 escalate rows (1 P1 README + 76 P2 unclassified) accumulate to 2899 arc-close judgment queue; NOT routed to Chris mid-arc per `feedback_arc_close_deferral_for_escalate_to_chris`.
- **T3a↔T5 boundary rule GENERALIZED to T3b** (§5.4): all 151 T5-territory files carry `t5_may_override: YES`. Cycle-2 Q5(c) added explicit T5 workflow directive — T5 SHOULD ingest `/tmp/t3b_orphan_scan_out.json` at 2805 authoring, not re-derive graphs.
- Migration queue frozen; routed to future §3 execution arc post-2899.

## 2. Joint Claude+Rigby SIGN provenance (3 cycles)

### Cycle 1 — 2026-07-19 (5 pressure-test questions)

**Rigby tool_runs (verified non-empty per `feedback_verify_rigby_tool_runs_before_trusting_sign`):**

- `repo_tool.search "<!-- DOC-POINTER-V2"` → 633 file matches (proved repo-wide grep as V2-count proxy is inflated ~4x vs first-1KB scan's 170)
- `repo_tool.read_file` — 3 sample V2 stubs (`docs/DEPLOYMENT_QUICKREF.md`, `docs/UNIFIED_CONTENT_PIPELINE.md`, `docs/DISCORD_COMMANDS.md`), lines 1-8 each — all confirm marker in first-1KB
- `repo_tool.tree docs/research/tools depth=3` → 27 entries including 4 top-level `tools_*.md` and 22 `validation/` subdir files
- `repo_tool.read_file docs/research/tools/tools_validation_engineering_campaign_plan.md` lines 1-40 → line 5 explicitly "awaiting Chris's review" (Rigby real leak-catch counterevidence)
- `repo_tool.read_file tools/audit_2803b_orphan_reachability.py` `SEARCH_ONLY_BENIGN_PATTERNS` tuple + `load_v2_stub_paths()` + `load_search_corpus_paths()`

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q1 V2-stub cluster shape verification | **STRENGTHEN** `numbers_mismatch_risk` | §1.5 grep-inflation warning added (633 file matches vs 170 first-1KB scan) |
| Q2 SEARCH_ONLY_BENIGN_PATTERNS rigor | **STRENGTHEN** `benign_pattern_false_negative_leak` | `docs/research/tools/` narrowed to `docs/research/tools/validation/` only; 4 top-level `tools_*.md` routed to `unclassified`; §1.4#4 doc-language updated |
| Q3 T1 counter-signal ratification | **DISAGREE-pending** `needs_repo_verification` | Rigby honestly declined pending independent tool_runs — resent as cycle 1b |
| Q4 README.md P1 finding vs. sync boundary | **DISAGREE-pending** `needs_repo_verification` | Rigby honestly declined pending independent tool_runs — resent as cycle 1b |
| Q5 zoom-out | **STRENGTHEN** (truncated at Q5(a)) — resent as cycle 1b + cycle 2 | (see cycle 1b and cycle 2) |

### Cycle 1b — 2026-07-19 (Q3+Q4 verification + Q5 completion)

**Rigby tool_runs:**

- `repo_tool.tree docs/topics depth=2` → **count=21** + full filename list including `collaboration-protocol.md`, `obs-remote-control.md`, `video-upload.md`
- `repo_tool.search "collaboration-protocol" file_type=md` → 4 matches total (audit doc, closed research inventory, out-of-scope handoff, self-doc) — **zero anchor-graph citations**
- `repo_tool.search "video-upload" file_type=md` → 3 matches total (audit doc, closed research inventory, handoff) — **zero anchor-graph citations**
- `repo_tool.read_file core/management/commands/build_docs_index.py start_line=190 end_line=270` → line 200 explicit `for root_doc in ['CLAUDE.md', '00-START-NEXT-SESSION.md']:` inclusion list (README.md NOT listed, no comment justifying exclusion)

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q3 T1 counter-signal ratification | **AGREE** `same_pr_mitigatable` | §2.7 tail added Rigby verification substrate — 21 topics enumerated; grep zero-anchor-citation proof; counter-signal confirmed real |
| Q4 README.md P1 finding | **AGREE** `same_pr_actionable`/`same_pr_mitigatable` | §5.5 tail added `build_docs_index.py:200` root_doc list evidence + ORM confirmation `Document.objects.filter(file_path='README.md', is_active=True).exists()==False`; framed as 1-line fix-scope option |
| Q5(a) corpus-inclusion vs top-K retrieval | **STRENGTHEN** `future_trigger` | §6.1(1) limitation records deferral rationale — top-K retrieval frequency requires probe-query selection + wall-clock; corpus-inclusion is load-bearing subset |

### Cycle 2 — 2026-07-19 (Q5(b)/Q5(c) completion + fold verification)

**Rigby tool_runs:**

- `repo_tool.read_file` T3b doc §1.4 (anti-pattern list, lines 150-220) + §1.5 (pre-clustering signals, lines 200-280)
- `repo_tool.read_file` T3a doc §5.6 boundary rule (lines 760-880) + T3b §5.4 boundary application
- `repo_tool.read_file tools/audit_2803b_orphan_reachability.py` (lines 220-340) for `SEARCH_ONLY_BENIGN_PATTERNS` inspection
- `repo_tool.read_file` T3b §5.5 (README build_docs_index prose)

**Verdicts:**

| Q | Verdict | Refinement folded |
|---|---|---|
| Q5(b) pattern-list false-negative leak | **STRENGTHEN** `future_trigger` + `same_pr_mitigatable` | §5.7 sub-fold added — `implementation_arc_artifact` + `closed_research_arc_child` broad-prefix risk noted; two mitigation options (closed-arc sentinel marker OR arc-slug allowlist) as `future_trigger` for 2899 |
| Q5(c) T3a↔T5 boundary coupling risk | **STRENGTHEN** | §5.4 coupling risk callout added — T5 (2805) SHOULD ingest `/tmp/t3b_orphan_scan_out.json` at authoring, not re-derive graphs; `future_trigger` for 2805 spec |

### Cycle 3 — 2026-07-19 (7/7 fold verification with cited lines + Q5(d))

**Rigby tool_runs:**

- `repo_tool.read_file` T3b §1.5 (lines 211-221) — Q1 fold verified
- `repo_tool.read_file` T3b §1.4 (lines 173-183) — Q2 fold verified
- `repo_tool.read_file` T3b §2.7 tail (lines 402-414) — Q3 fold verified
- `repo_tool.read_file` T3b §5.5 tail (lines 872-883) — Q4 fold verified
- `repo_tool.read_file` T3b §6.1(1) (lines 919-925) — Q5(a) fold verified
- `repo_tool.read_file` T3b §5.7 (lines 900-911) — Q5(b) sub-fold verified
- `repo_tool.read_file` T3b §5.4 tail (lines 841-849) — Q5(c) fold verified
- `repo_tool.read_file` T3b §2.11 summary histogram (lines 490-517) — Q5(d) grounding

**Verdicts:**

| Q | Verdict | Rationale |
|---|---|---|
| Q1 fold (§1.5 grep-inflation warning) | **AGREE** | Correctly warns grep count (633) inflated vs 170 first-1KB scan; lines 211-221 |
| Q2 fold (§1.4#4 validation/ narrowing) | **AGREE** | Correctly narrows to `docs/research/tools/validation/` + routes 4 top-level `tools_*.md` to `unclassified`; lines 173-183 |
| Q3 fold (§2.7 T1 counter-signal substrate) | **AGREE** | Correctly records 21 topics + grep zero-anchor-citation proof; lines 402-414 |
| Q4 fold (§5.5 README build_docs_index evidence) | **AGREE** | Correctly cites `['CLAUDE.md', '00-START-NEXT-SESSION.md']` root_doc list + ORM confirm + 1-line fix-scope path; lines 872-883 |
| Q5(a) fold (§6.1(1) top-K limitation) | **AGREE** | Correctly frames top-K retrieval frequency as deferred limitation + corpus-inclusion load-bearing; lines 919-925 |
| Q5(b) sub-fold (§5.7 broad-prefix risk) | **AGREE** | Correctly flags `implementation_arc_artifact` + `closed_research_arc_child` broadness + proposes sentinel/allowlist mitigations as `future_trigger`; lines 900-911 |
| Q5(c) fold (§5.4 T3a↔T5 coupling callout) | **AGREE** | Correctly directs T5 to ingest `/tmp/t3b_orphan_scan_out.json` + not re-derive graphs; lines 841-849 |
| Q5(d) usage/salience limitation | **STRENGTHEN** `future_trigger` | §6.1(7) added — histogram optimizes count-reduction story but misses operator-impact dimension; follow-up sub-arc could rank search-only files by probe-query top-K frequency or retrieval-log hit count |

## 3. Post-fold defect population

**Escalate queue accumulates to 2899 (S2836 deferral policy carries over):**

- **P0:** 0 (root-stability gate NOT triggered)
- **P1:** 1 (README.md cited-but-search-invisible — build_docs_index scope oversight)
- **P2:** 76 (unclassified search-only-reachable — real Chris judgment queue)
- **P3:** 716 (keep_as_is; ~90.3%)

**Total escalate queue (deferred to 2899): 77 rows** across 13 subdirs.

Sub-classification of 302 search-only-reachable files:
- `v2_pointer_stub`: 74 (search-only-not-anchor-cited V2 stubs; 96 more V2 stubs are ALSO anchor-cited → healthy `cited-multi-graph-OK`)
- `unclassified`: 76 (real escalate queue)
- `t5_territory`: 41 (`t5_may_override: YES` per T3a↔T5 boundary generalized)
- `ratification_envelope`: 38
- `closed_arc_pack`: 30 (`docs/cleanup/` + `docs/code-review/` only after cycle-2 narrowing)
- `closed_research_arc_tool`: 21 (`docs/research/tools/validation/` ONLY after cycle-2 Q2 narrowing)
- `implementation_arc_artifact`: 13
- `closed_research_arc_child`: 9

**Positive tree-health signal**: zero unreachable-from-all-3-graphs files across the 793-file corpus.

**Cross-cutting findings (recorded for 2899):**

- `docs/INDEX.md` is a strict subset of CLAUDE.md BFS (0 index-only files); autogen index provides zero incremental reachability
- T1 counter-signal: 3 of 21 `docs/topics/*` files miss anchor graph (feed back to T1 as 2899 refinement candidate)
- V2-stub direct-marker scan: 170 stubs total (stronger than T3a §2.3 shingle-inference "110+" bound)

## 4. Schema disposition

**Parent §10.1 v1.1 schema UNCHANGED.** T3a's ratification (§10.1 v1.1 lock at S2834 + §5.3 (i)-(iv) v1.2 acceptance criteria) carries through T3b. All 793 T3b findings inherit `schema_version: 1.1` from frontmatter (§10.1 v1.1 whole-doc default).

**Three v1.2 candidates recorded as `future_trigger` for 2899 close:**

- **§5.3** `coverage_reachability` as fourth coverage axis (third witness following T2 §5.7 `coverage_refs`/`coverage_claims` split proposal + T3a §5.3 `coverage_content_dup` third-axis proposal)
- **§5.7** Closed-arc sentinel marker OR arc-slug allowlist (mitigates `implementation_arc_artifact` + `closed_research_arc_child` broad-prefix false-negative-escalate-leak risk)
- **§6.1(7)** Usage/salience metric (histogram is structural not behavioral; future sub-arc could rank search-only files by probe-query top-K frequency or retrieval-log hit count)

Per T3a §5.3 acceptance criteria: (i) additive-only + (ii) backward-compatible + (iii) parser-compat plan + (iv) documented deprecation path — ALL v1.2 changes must satisfy at 2899 amendment.

## 5. Chris D-verdict (S2837)

> ratify T3b as-folded

Interpretation: RATIFY T3b full audit + all Rigby-folded refinements. No new arc-level policy established beyond S2836 deferral-to-2899 (which carries over automatically for T3b's 77 escalate rows).

## 6. Next action (S2838)

**T4 handoff citation-integrity + retrieval-harm audit opens at S2838 as recommended default.**

- Target artifact: `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md`
- Scope: 1058 `docs/handoffs/*.md` files
- Method per parent §4 T4: (a) citation-graph greps + hit rate + decay curve, (b) citation-integrity spot-check on 10-doc sample, (c) retrieval-harm / staleness-banner sub-loop for top-K handoffs surfacing in `search_docs` for common operational queries
- Deliverable: citation-graph summary + spot-check results + retrieval-contribution histogram + retrieval-harm banner list
- **Consumes T3b's `/tmp/t3b_orphan_scan_out.json`** for reachability signal on handoff citations (per §5.4 T3a↔T5 boundary rule generalized — T4 should also ingest, not re-derive)
- Continues escalate-queue accumulation to 2899 per S2836 policy

## 7. Twin-pointer mirror (workspace)

Per `feedback_rigby_writes_workspace_deliverables` (S2835 rule, third exercise at S2837): Rigby creates BOTH content mirror AND ratification envelope in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via PA `deliverable_tool.create`. Claude verifies tool_runs + ORM cross-check post-create. Category `governance`; `deliverable_type=ratification_record` for the envelope.

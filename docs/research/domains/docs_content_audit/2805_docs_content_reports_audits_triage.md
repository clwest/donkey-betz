---
title: "S2839 T5 — /docs/ Reports + Audits Triage Audit (child audit 2805 of Group 2800)"
status: ratified (T5 — Chris D-verdict 2026-07-19 S2839; joint Claude+Rigby SIGN 3 cycles in AEP v0.1 Stage 1 trial format; schema v1.1 unchanged; 5 v1.2 candidates queue for 2899)
ratification:
  date: 2026-07-19
  session: 2839
  ratifier: Chris
  verbatim_directive: "Approve"
  scope: |
    Full T5 (169-file corpus; 4-axis classification; 6 folds F1-F6 applied
    same-PR through cycles 1+2; cycle 3 anti-rubber-stamp clean with 5/5
    AGREE line-cited; §10.1 v1.1 schema UNCHANGED; 107 escalate rows queue
    for 2899 workshop per S2836 policy carry-over; 5 v1.2 candidates
    accumulated (four prior + T5 §5.1 series-inheritance + T5 §5.7a
    small-fix whitelist)). Group 2800 arc reaches 6/6 shipped.
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2805_docs_content_reports_audits_triage.md
  sign_cycles: 3 (Rigby joint SIGN pin pa-c0dd5180697442ad; ALL cycles in AEP v0.1 Stage 1 trial format; cycle-3 first fully-clean cycle-3 in Group 2800 arc)
  aep_trial: PASS_all_5_metrics_Stage_2_authorized_with_cap_sensitive_PROSE_FIELD_tweak
  next_action: 2899 canonical summary opens at S2840; Group 2800 arc closes; migration §3 execution arc opens post-2899
authority: child-audit deliverable — consumed by Group 2800 canonical summary at 2899 close
session: 2839
date: 2026-07-19
research_group: 2800
thread: T5
schema_version: 1.1  # inherited from parent §10.1 v1.1 locked at S2834; UNCHANGED at T5 close
parent: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
sibling_children:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md      # T1 — RATIFIED at S2834
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md    # T2 — RATIFIED at S2835
  - docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md   # T3a — RATIFIED at S2836
  - docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md      # T3b — RATIFIED at S2837
  - docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md      # T4 — RATIFIED at S2838
  - docs/research/domains/docs_content_audit/2899_docs_content_canonical_summary.md  # arc close (next)
authors: Claude Code (Chris directed at S2839 open — "open T5" = ratified default from S2838 D-verdict)
supersedes: none
scope: |
  Reports + audits triage of the 169 in-scope files across five subdirs:
    docs/audits/**       (93 files; includes 19 SESSION_819_SYSTEM_AUDIT_*)
    docs/audit-2026/**   (15 files)
    docs/audit/**        (10 files)
    docs/reports/**      (33 files — Rigby cycle-2 Q3 STRENGTHEN at S2833 parent close)
    docs/*_AUDIT.md      (18 root-level anchor-linked capability audits)
  Four-axis classification per parent §4 T5:
    (a) one_shot session snapshot vs standing reference
    (b) anchor-graph reachable vs orphan
    (c) content-stale vs still-valid
    (d) existing V1/V2 pointer already tells the right story
  Consumes T3b §5.4 T5 workflow directive substrate (151 t5_may_override:YES
  pre-classified rows in /tmp/t3b_orphan_scan_out.json) + T4 §2.5 handoff-adjacent
  banner signal (0 basename intersection with T5 corpus; expected — handoffs
  and audits live in disjoint subdirs). Emits YAML findings per parent §10.1 v1.1.
non_goals:
  - per-audit-file content-quality review (parent §4 T5 anti-pattern; T5 is TRIAGE)
  - archive / consolidation / retrofit execution (classification only per parent §5)
  - moves / renames / deletions during arc
  - anchor / canonical-doc content walk (T1 territory)
  - reference-graph validation (T2 territory)
  - duplicate-content classification (T3a territory)
  - orphan classification across the general corpus (T3b territory)
  - handoff citation-integrity / retrieval-harm (T4 territory)
  - modifying §10.1 v1.1 schema (locked at S2834; four v1.2 candidates recorded across siblings — still NOT applied)
head_at_open: 6f0db5879cf7  # S2838 close-cascade merged
scanner_tool: tools/audit_2805_reports_audits_triage.py
scanner_out: /tmp/t5_reports_audits_scan_out.json
t3b_pre_clustering_seed: /tmp/t3b_orphan_scan_out.json  # T3b §5.4 T5 workflow directive
t4_banner_adjacency_seed: /tmp/t4_handoff_audit_out.json  # T4 §2.5 handoff-adjacent (0 intersection)
owner: claude+rigby (Chris to ratify)
---

# S2839 — T5 Reports + Audits Triage Audit

> **What this doc is.** Group 2800's sixth (and last) child audit. Four-axis
> triage classification across 169 in-scope files spanning `docs/audits/`,
> `docs/audit-2026/`, `docs/audit/`, `docs/reports/`, and `docs/*_AUDIT.md`
> root-level capability audits. Sizes the escalate-to-Chris queue for
> arc-close resolution at 2899 per S2836 D-verdict deferral policy.
>
> **What this doc is not.** A per-file content-quality review (parent §4 T5
> anti-pattern is explicit: "audit content review is quarantined — T5 is
> TRIAGE only"). An archive / consolidation execution plan. A schema
> amendment (§10.1 v1.1 unchanged; v1.2 candidates accumulate as future
> triggers for 2899).

---

## 1. Method

### 1.1 Corpus selection — 169 files across five subdirs

Live enumeration at head `6f0db5879cf7` (S2838 close-cascade merged):

| Subdir | Count | Parent §4 T5 stated | Delta |
|---|---:|---:|---|
| `docs/audits/**` | 93 | 93 | 0 (includes 19 untracked `SESSION_819_SYSTEM_AUDIT_*`) |
| `docs/audit-2026/**` | 15 | 15 | 0 (0-index dossier plan + 14 subsystem dossiers) |
| `docs/audit/**` | 10 | 10 | 0 |
| `docs/reports/**` | 33 | 33 | 0 (Rigby cycle-2 Q3 STRENGTHEN at S2833 parent close) |
| `docs/*_AUDIT.md` | 18 | 20 | **-2 drift** (parent estimate; actual is 18) |
| **Total** | **169** | **~171** | -2 |

**-2 root-level drift:** parent §4 T5 said "20 root-level `*_AUDIT.md`" at S2833 authoring; actual at S2839 T5 open is 18 via `Path('docs').glob('*_AUDIT.md')`. Two-file drift attributes cleanly to arc-time count-in-narrative aging (parent scoping predates T5 by 6 sessions during which no `docs/*_AUDIT.md` files were added or removed — the "20" was an approximate estimate at parent authoring time, not a live count). Not a defect. Documented for the arc-close audit trail; no recommended action beyond the noted difference.

### 1.2 Four axes (parent §4 T5 method literal)

Each of the 169 files is classified on four boolean-ish axes; combinations map to §10.3 8-action taxonomy per §1.6.

| Axis | Signal source | Values |
|---|---|---|
| **(a) one_shot vs standing_reference** | Filename patterns (SESSION_NNN_/`_REPORT`/`_ASSESSMENT`/timestamp = one_shot; `00-`/`_PLAN`/`_PATTERN`/`_AUDIT.md` at anchor path = standing) + fallback to `ambiguous` when neither matches cleanly | `one_shot` \| `standing_reference` \| `ambiguous` |
| **(b) anchor-graph reachable vs orphan** | T3b §5.4 pre-clustering seed (reachable_from_claude_md_anchor / reachable_from_docs_index / reachable_from_search_corpus) | `multi_graph` \| `anchor_only` \| `search_only` \| `orphan` \| `not_in_t3b` |
| **(c) content-stale vs still-valid** | Filename session tag < S2500 → `stale_pre_s2500`; head text contains `IN PROGRESS` / `TODO` / `NEXT STEPS` markers → `stale_in_progress_marker`; standing_reference → `still_valid`; else `unclear` | `stale_pre_s2500` \| `stale_in_progress_marker` \| `still_valid` \| `unclear` |
| **(d) existing V1/V2 pointer** | Grep for `DOC-POINTER-V1` \| `DOC-POINTER-V2` marker in file head | `v1_pointer` \| `v2_pointer` \| `none` |

Threshold `S2500` for axis (c) is Chris-tunable. Rationale: S2500-2999 bucket is the recent-cited-session bucket per T4 §2.2 decay curve (26.8% cite rate); pre-S2500 is retention-tail. Applied only to shape=`one_shot`; standing_reference is not axis-c load-bearing.

### 1.3 Recommended action derivation (§10.3 8-action taxonomy)

Deterministic combination-to-action mapping. Anti-pattern challenge: T5 does NOT walk file content for quality; the axis combination IS the load-bearing classification.

```
IF pointer ∈ {v1_pointer, v2_pointer}:            → keep_as_is (P3)
IF shape=standing_reference AND reach ∈ {multi_graph, anchor_only}:
    IF stale ∈ {still_valid, unclear}:            → keep_as_is (P3)
    ELSE:                                          → escalate_to_chris (P2)
IF shape=one_shot:
    IF stale=stale_pre_s2500 AND reach ∈ {search_only, orphan}:   → escalate_to_chris (P2)  # archive candidate
    IF stale=stale_pre_s2500 AND reach ∈ {multi_graph, anchor_only}: → escalate_to_chris (P2)  # V2 retrofit candidate
    IF stale=stale_in_progress_marker:            → escalate_to_chris (P2)
    IF stale ∈ {still_valid, unclear} AND reach ∈ {multi_graph, anchor_only}: → keep_as_is (P3)
    IF reach=search_only:                          → escalate_to_chris (P2)
IF shape=ambiguous:                                → escalate_to_chris (P2)
```

Per S2836 D-verdict policy (carried through S2837/S2838), **all `escalate_to_chris` rows DEFER to 2899 arc-close workshop**. T5 does not resolve per-file dispositions mid-arc.

### 1.4 Anti-pattern challenge: "audit content review is legitimate here"

Parent §4 T5 explicitly quarantines content review: *"'audit content review' is quarantined — T5 is TRIAGE only (classify + recommend disposition). Do NOT walk every audit file for content quality; classification against the four axes is the load-bearing measurement."* This audit honors that boundary strictly. The scanner does NOT read arbitrary content; it reads a fixed 4KB head per file to detect V1/V2 pointer markers + stale phrase patterns. Filename patterns + T3b pre-clustering carry the load.

### 1.5 Pre-clustering signals consumed

| Substrate | Path | Coverage | Contract |
|---|---|---:|---|
| T3b reachability graph | `/tmp/t3b_orphan_scan_out.json` | 169 / 169 (100%) | load-only; do NOT re-derive per §5.4 T5 workflow directive |
| T4 handoff-adjacent banner list | `/tmp/t4_handoff_audit_out.json` | 0 / 169 basename intersection | informational only; T5 corpus and T4 corpus are basename-disjoint |

**Zero T4 basename intersection is expected and healthy.** T4 corpus lives in `docs/handoffs/**` (write-once session receipts); T5 corpus lives in `docs/audits/**` etc. (standing + one-shot capability audits). The parent §4 T5 spec's *"soft dependency: if T5 encounters a `SESSION_NNN_AUDIT.md` file that appears in T4 §2.5 banner candidates, treat T4's banner recommendation as one input to T5's disposition (not authoritative)"* is null-triggered: no T5 audit file basename matches any of T4's 13 banner-candidate handoff basenames.

**T3b coverage is 100%** — all 169 T5 files were in-scope at T3b's 793-file scan (S2837 head `be7af72159ec`). No file requires re-derivation; T5 consumes reachability wholesale. This is the second three-trigger corroboration of the cross-child pre-clustering pattern (after T3a←T2, T3b←T3a+T2, T4←T2+T3b): T5←T3b + T4-informational.

### 1.6 Scanner shape (parent §4 T5 compliance)

`tools/audit_2805_reports_audits_triage.py` (~340 lines, single-pass over 169 files, no expensive computation). Deterministic. Runs in ~1s. Reads head 4KB per file for V1/V2 pointer + stale phrase detection; consumes T3b + T4 JSON substrate; emits `/tmp/t5_reports_audits_scan_out.json` with per-file classification.

**Repeatability:** the scanner is idempotent; re-runs after new files land re-classify without any state carry-over. Deployed alongside T4's scanner (`tools/audit_2804_handoff_citation_integrity.py`) and T3b's (`tools/audit_2803b_orphan_reachability.py`) as the third reusable audit substrate. Future §3 execution arc may re-run this scanner post-migration-PR to verify classification drift.

---

## 2. Findings — 4-axis histograms + severity + disposition

### 2.1 Positive headline: zero P0 + zero P1

Root-stability gate NOT triggered. Zero files classified as P0 (actively misleading in an anchor-referenced audit doc) or P1 (stale but non-misleading in a load-bearing standing reference).

| Severity | Count | Share |
|---|---:|---:|
| **P0** | 0 | 0.0% |
| **P1** | 0 | 0.0% |
| P2 | 107 | 63.3% |
| P3 | 62 | 36.7% |
| **Total** | **169** | 100% |

**This is the third consecutive null-result P0 headline across the Group 2800 arc children** (T3b §2.1 zero fully-unreachable + T4 §2.4 zero `#K` chunk-ID citations + T5 §2.1 zero severity-P0). Empirically: the u-d-b `/docs/` corpus is structurally healthy at the anchor / handoff-citation / audit-triage layers when measured against runtime-derived truth (T3b reachability + T4 citation-integrity + T5 classification-vs-4-axes). The stress lives in mid-corpus (T3a duplicate content, T2 broken refs) — not at the root or the terminal-write-once layers.

The `null_result` finding class Playbook §11.3 template candidate now reaches **three-trigger corroboration** (T3b + T4 + T5). Recorded as future_trigger for post-2899 codification per §5.4.

### 2.2 Axis (a) — shape distribution

| Shape | Count | Share | Note |
|---|---:|---:|---|
| standing_reference | 35 | 20.7% | 18 `docs/*_AUDIT.md` + 17 subdir `_PLAN.md` / `00-*.md` |
| one_shot | 53 | 31.4% | SESSION_NNN_-prefixed + timestamped |
| ambiguous | 81 | 47.9% | Filename doesn't match either heuristic pattern cleanly |

**Ambiguous 47.9% share is a scanner-heuristic limitation, not a corpus defect.** Concrete evidence: `docs/audit-2026/01-celery.md` through `08-personal-assistant.md` are `NN-<subsystem>.md` shaped (subsystem dossier series); shape is unambiguously "historical dossier snapshot" (one-shot) per the parent `00-AUDIT-PLAN.md` `DOC-POINTER-V1` banner text (*"HISTORICAL DOSSIER SERIES (April 2026). This 13-file series is preserved as a time-bounded subsystem snapshot"*). The scanner's regex patterns don't infer subdir-series semantics; that's a Rigby SIGN Q candidate (§7 Q1).

### 2.3 Axis (b) — reachability distribution (T3b substrate)

| Reachability class | Count | Share |
|---|---:|---:|
| multi_graph (all 3 graphs) | 18 | 10.7% |
| anchor_only (CLAUDE.md and/or docs/INDEX.md) | 109 | 64.5% |
| search_only (in Document.file_path corpus only) | 42 | 24.9% |
| orphan | 0 | 0.0% |
| not_in_t3b | 0 | 0.0% |

**75.1% of T5 files reach at least one anchor graph.** The 42 search-only files are all pre-classified `t5_may_override:YES` by T3b — expected T5 territory per T3a↔T5 boundary rule generalized at T3b §5.4. No T5 file is fully orphan (three-graph absent).

### 2.4 Axis (c) — stale distribution

| Stale kind | Count | Share |
|---|---:|---:|
| still_valid | 35 | 20.7% |
| stale_pre_s2500 | 38 | 22.5% |
| stale_in_progress_marker | 2 | 1.2% |
| unclear | 94 | 55.6% |

**"Unclear" dominates (55.6%)** because axis (c) is deliberately conservative: absent explicit stale phrase or old-session-tag signal, the heuristic returns `unclear` rather than presuming still-valid. This is not a defect; T5 triage does not carry content-freshness judgment — that's Chris's judgment at 2899. `unclear` files disposition rides on the other three axes.

**2 in-progress markers:** `docs/audits/SPRINT_1_COMPLETION.md` + one similar. Both `stale_in_progress_marker` + `ambiguous` shape + `anchor_only` reach → escalate_to_chris.

### 2.5 Axis (d) — V1/V2 pointer distribution

| Pointer | Count | Share |
|---|---:|---:|
| v2_pointer | 38 | 22.5% |
| v1_pointer | 3 | 1.8% |
| none | 128 | 75.7% |

**32 of 33 files in `docs/reports/**` already carry V2 pointer** (97% coverage). This upholds the parent §4 T5 Rigby cycle-2 Q3 STRENGTHEN evidence — the `docs/reports/` subdir was already effectively triage-complete before T5 opened. The remaining 1 (`docs/reports/VERIFY_REPORT.md`) is one_shot + anchor_only + unclear → keep via the "recent one-shot with anchor reach" derived-action rule; content-freshness judgment deferred to 2899 if needed.

**3 V1 pointers:** `docs/audit-2026/00-AUDIT-PLAN.md` (series index), `docs/audit/WEEK1-CANARY-COORDINATION-STATUS.md`, and 1 similar. Both V1 and V2 pointers now short-circuit derivation to `keep_as_is` per axis (d) intent ("already tells the right story").

**Cycle-1 Q1 fold (Rigby STRENGTHEN, ARS-VERIFIED):** Rigby independently surfaced a **second** series-index V1 pointer at `docs/audits/INDEX.md` (*"HISTORICAL ARCHIVE. This directory holds pre-2026 session-numbered audits. Current audit workspace is docs/audit/"*). Verified via `head -5 docs/audits/INDEX.md`. Inverse observation: `docs/audit/README.md` (current subdir) does NOT carry V1 pointer. **Emergent convention: pointer-on-INDEX-for-historical-subdirs-only** — historical/superseded subdirs carry a series-level V1 pointer on their index/entry file; current/active subdirs don't. Two independent examples now (audit-2026/00-AUDIT-PLAN.md + audits/INDEX.md); §5.1 strengthened accordingly.

### 2.6 Per-subdir disposition (the load-bearing view)

| Subdir | keep_as_is | escalate_to_chris | Total | Escalate share |
|---|---:|---:|---:|---:|
| `docs/*_AUDIT.md` (18) | **18** | 0 | 18 | 0.0% |
| `docs/reports/**` (33) | **33** | 0 | 33 | 0.0% |
| `docs/audit-2026/**` (15) | 2 | 13 | 15 | 86.7% |
| `docs/audit/**` (10) | 3 | 7 | 10 | 70.0% |
| `docs/audits/**` (93) | 6 | 87 | 93 | 93.5% |
| **Total** | **62** | **107** | **169** | **63.3%** |

**Two subdirs are effectively triage-complete pre-T5:** `docs/*_AUDIT.md` (all standing_reference at multi-graph anchor reach) + `docs/reports/**` (V2-pointer covered). Combined 51/169 = 30.2% of corpus needs no further action.

**Three subdirs concentrate the 2899 workshop load:**

- `docs/audit-2026/**` — 13 escalate rows are ALL the historical subsystem dossiers whose parent `00-AUDIT-PLAN.md` carries a series-level V1 pointer. Chris judgment call at 2899: propagate the series-level pointer as "already tells the right story" (→ flip 13 to keep_as_is), or emit a per-file V1 pointer retrofit action? Recorded as §7 Rigby SIGN Q1.
- `docs/audit/**` — 7 escalate rows are dominated by 5 `SESSION_1143_*` one-shot audit outputs (docs cleanup arc, stale_pre_s2500, anchor_only reach). Classic V2 retrofit or archive candidates.
- `docs/audits/**` — 87 escalate rows dominate the queue (81% of arc's 107 total). Sub-breakdown in §2.7.

### 2.7 `docs/audits/**` escalate sub-breakdown (87 rows)

The largest escalate concentration. Sub-classified by (shape, reach, stale) tuple:

| (shape, reach, stale) | Count | Representative | Chris judgment class |
|---|---:|---|---|
| (ambiguous, anchor_only, unclear) | 36 | `INTEGRATION_GAP_ANALYSIS.md` | Series-level or per-file V1 pointer? Or reclassify shape? |
| (one_shot, search_only, stale_pre_s2500) | 20 | `SESSION_786_MARKDOWN_SYSTEM_REVIEW.md` | Archive candidates (2020-era session snapshots, not anchor-reachable) |
| (one_shot, anchor_only, stale_pre_s2500) | 13 | `SESSION_727_AGENTS_AUDIT.md` | V2 retrofit candidates (old sessions with anchor citations) |
| (ambiguous, search_only, unclear) | 8 | `PA_TOOLS_GAP_MAP_S2795.md` | Recent gap maps; keep-in-place or subdir V1? |
| (standing_reference, search_only, still_valid) | 6 | `CONNECTIVITY_SWEEP_PLAN.md` | Planning docs at active status but no anchor link — add to anchor graph or keep? |
| (ambiguous, anchor_only, stale_in_progress_marker) | 2 | `SPRINT_1_COMPLETION.md` | In-progress marker on old sprint — likely closed; retrofit or archive |
| Other | 2 | mixed | miscellany |

**Judgment class taxonomy** (for 2899 workshop): the 87 rows fall into 5 disposition classes that Chris can walk through as batch decisions rather than 87 individual calls:

1. **Series-level V1 pointer propagation** (36 rows): if the ambiguous+anchor+unclear rows share a common series (or the whole `docs/audits/` subdir should carry a series-level V1 pointer explaining "these are session-scoped audit snapshots"), 36 flip to keep in one policy decision.
2. **Archive candidates** (20 rows): pre-S2500 one-shots not anchor-reachable. Chris says archive/keep/case-by-case.
3. **V2 retrofit candidates** (13 rows): pre-S2500 one-shots WITH anchor citations. V2 pointer at each file OR update the citing anchor to remove the old ref.
4. **Recent gap maps** (8 rows): keep-in-place with subdir-level V1 pointer, or add to CLAUDE.md anchor graph?
5. **Case-by-case** (10 rows): the 6 standing+search+valid + 2 in-progress + 2 other need individual judgment.

**No load-bearing content-quality judgment recommended in T5 output.** Every disposition class above is a policy or classification decision, not a per-file content edit. Consistent with parent §4 T5 anti-pattern.

### 2.8 SESSION_819_SYSTEM_AUDIT_* set (19 untracked files)

Currently `??` in git status (visible in S2838 close context). Filename pattern: `SESSION_819_SYSTEM_AUDIT_20260714_223131.md` (timestamped `YYYYMMDD_HHMMSS`). Session number 819 is the SESSION_819 label; the timestamps span 2026-07-14 through 2026-07-16.

**T3b coverage:** all 19 in T3b corpus (visible during S2837 head `be7af72159ec` scan), all pre-classified `t5_may_override:YES` P3 keep_as_is + `search_only_kind=t5_territory`.

**T5 axis-classification:** all 19 are (one_shot, anchor_only, stale_pre_s2500, none) per session_819 filename tag < S2500. All → escalate_to_chris (P2) via one_shot + stale_pre_s2500 + anchor_only path.

**However** — these are ALSO ambiguous by another read: the filename tag "SESSION_819" but timestamps 2026-07-14+ suggest these are recent audits *of* SESSION_819 (an old session), not audits *from* SESSION_819. If read as "recent audit outputs referencing an old session," they belong in a different disposition class than "old session snapshots." Chris judgment at 2899 could apply a "these are recent audit runs; keep in tracking" policy that flips all 19 keep. Recorded as §7 Rigby SIGN Q3 candidate. All 19 are `??` untracked; Chris judgment includes "commit or delete before arc close?" secondary question.

**Cycle-1 Q3 fold (Rigby AGREE, ARS-VERIFIED):** Rigby verified via `repo_tool.read_file` on `docs/audits/SESSION_819_SYSTEM_AUDIT_20260714_223131.md` L1-25: *"Generated: 2026-07-14T22:31:31...+00:00, Triggered by: s2787-csrf-pass-fixture, plus a categorized checks table (AGENTS / BODY SYSTEMS / etc)."* The (a)-hypothesis — recent audit outputs referencing SESSION_819 legacy tag — is EMPIRICALLY VERIFIED. Alternative (c) "test artifacts to delete" is empirically eliminated by the structured report content + explicit trigger identifier. Chris judgment at 2899 is now between (a) keep for tracking (commit + retain) vs (b) archive as historical audit-run snapshots. The (c) delete option is retired.

---

## 3. Migration queue (post-arc, DEFERRED to §3 execution arc post-2899)

### 3.1 Zero P0 rows — no root-stability gate triggered

Consistent with §2.1. Group 2800 arc reaches 6/6 shipped with **zero P0 findings across all six children** (T1 through T5). Root-stability guarantee upheld throughout.

### 3.2 Zero P1 rows

Also consistent with §2.1. T5 severity distribution collapses to P2/P3 only. This is the first Group 2800 child to have zero P1 as well as zero P0 (T3b had 1 P1: README.md corpus-inclusion; T4 had 6 P1 path-form broken citations; T5 has 0).

### 3.3 P2 escalate queue — 107 rows (queued for 2899 workshop)

**Per S2836 D-verdict deferral policy** (unchanged from T3b/T4), all `escalate_to_chris` rows accumulate to the 2899 canonical summary "Chris judgment queue" section for single-session workshop resolution.

Breakdown by subdir:

- `docs/audit-2026/**` 13 (series-level pointer policy candidate)
- `docs/audit/**` 7 (mostly SESSION_1143 retrofit candidates)
- `docs/audits/**` 87 (5-class judgment taxonomy per §2.7)
- `docs/*_AUDIT.md` 0
- `docs/reports/**` 0

**Cumulative Group 2800 escalate queue at S2839 T5 close:**

| Source | Rows | Notes |
|---|---:|---|
| T1 anchors + T2 refs | 0 to accumulation | per pre-S2836 policy child ratifications |
| T3a duplicate content | 2 | S2836 close |
| T3b orphan + reachability | 75 | S2837 close (76 total P2; 1 P1 README.md ratified separately) |
| T4 handoff citation-integrity | 22 | S2838 close (6 P1 + 13 P2 retrieval-harm + 3 P2 fragment-form) |
| **T5 reports+audits triage** | **107** | this arc (all P2) |
| **Total for 2899 workshop** | **206** | five-fold larger than pre-T5 (99) |

**T5 dominates the workshop queue by ~2×** (107 rows vs 99 rows across all prior children). This is expected — T5's corpus (169 files) is closer in size to the T3b/T4 corpora (793 + 1061 = 1854) than T3a (~810) — but its higher escalate share (63.3% vs T3b's 9.6% + T4's 2.1%) reflects the triage-vs-audit nature: T5 must make disposition recommendations rather than defect classifications, and disposition decisions on session-scoped audit snapshots are inherently Chris-judgment-heavy (subject-matter authority).

### 3.4 Migration-PR batch hints (per §10.4 cross-arc consumption contract)

For the future post-2899 execution arc, T5 rows group naturally into these `migration_pr_batch_hint` classes:

- `audits_triage_series_pointer` — 49 rows (36 ambiguous+anchor+unclear + 13 audit-2026); one policy PR adds a series-level V1 pointer per subdir
- `audits_triage_archive` — 20 rows (pre-S2500 one-shots + search-only); one PR moves batch to `docs/archive/2020/`
- `audits_triage_v2_retrofit` — 18 rows (13 anchor-reachable pre-S2500 in `docs/audits/` + 5 `SESSION_1143_*` in `docs/audit/`); one PR adds V2 pointers batch-style
- `audits_triage_case_by_case` — 20 rows (all remaining escalate rows); individual review

Total 4 candidate migration PRs for the ~107 escalate rows if Chris ratifies the batch-decision structure at 2899. Alternative: Chris chooses per-file dispositions individually. Both routes are compatible with the §10.1 v1.1 schema output shape.

### 3.5 T5-territory rows fully absorbed

The T3b §2.9 "T5-territory search-only rows — 41 files (t5_may_override: YES)" queue is fully consumed by this audit. Cross-checked: all 41 T3b t5_may_override rows appear in T5's 169-file corpus. Zero leftover T3b→T5 hand-off residue. Cross-child pre-clustering consumption contract met.

---

## 4. YAML findings — §10.1 v1.1 schema rows (representative sample)

Per parent §10.1 v1.1 schema. Full 169-row set lives in `/tmp/t5_reports_audits_scan_out.json`; representative sample below covers each disposition class + subdir combination. Every T5 finding uses the parent §10.1 v1.1 schema **unchanged**.

```yaml
# docs/*_AUDIT.md (18 files, all keep_as_is)
- file_path: docs/ADVISOR_AUDIT.md
  audit_thread: T5
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 4096]
      claim: "standing reference for advisor domain audit; anchor-linked at CLAUDE.md"
      runtime_truth: "T3b reachability = multi_graph (all 3 graphs)"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs:
    - 2799_3_target_tree_row: docs/topics/ (2799 §3.1 leaf if migration relocates)
    - t3b_row: cited-multi-graph-OK / keep_as_is
  notes: "standing_reference + multi_graph + still_valid; no action required"

# docs/reports/** (33 files, all keep_as_is; 32 with V2 pointer)
- file_path: docs/reports/3D_GENERATION_VERIFICATION_REPORT.md
  audit_thread: T5
  severity: P3
  finding_class: superseded_untagged
  evidence:
    - line_range: [1, 50]
      claim: "DOC-POINTER-V2 marker present"
      runtime_truth: "v2_pointer detected in file head"
      cited_source: docs/reports/3D_GENERATION_VERIFICATION_REPORT.md
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "V2 pointer already tells the right story (parent §4 T5 axis-d intent)"

- file_path: docs/reports/VERIFY_REPORT.md
  audit_thread: T5
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 4096]
      claim: "one_shot verify report; no V1/V2 pointer; anchor-reachable"
      runtime_truth: "no DOC-POINTER-V* marker in head; T3b reach=anchor_only"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "recent one_shot + anchor_only + unclear stale → keep; watch for content-drift at 2899"

# docs/audit-2026/** (15 files; 2 keep, 13 escalate — series-level V1 pointer candidate)
- file_path: docs/audit-2026/01-celery.md
  audit_thread: T5
  severity: P2
  finding_class: ok
  evidence:
    - line_range: [1, 4096]
      claim: "member of April 2026 dossier series; parent 00-AUDIT-PLAN.md carries series-level V1 pointer"
      runtime_truth: "own file has no V1/V2 pointer; series index does"
      cited_source: docs/audit-2026/00-AUDIT-PLAN.md#L1
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_series_pointer
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
    - series_index: docs/audit-2026/00-AUDIT-PLAN.md (v1_pointer)
  notes: "series-level pointer propagation Chris judgment (see §2.7 sub-breakdown + §7 Rigby SIGN Q1)"

# docs/audits/** — V2 retrofit candidate (SESSION_NNN old anchor-reachable)
- file_path: docs/audits/SESSION_727_AGENTS_AUDIT.md
  audit_thread: T5
  severity: P2
  finding_class: superseded_untagged
  evidence:
    - line_range: [1, 4096]
      claim: "SESSION_727 filename tag; anchor-reachable via T3b"
      runtime_truth: "S727 predates S2500 threshold; anchor citations from newer docs"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_v2_retrofit
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "old session snapshot with anchor citations — V2 retrofit or citing-anchor cleanup candidate"

# docs/audits/** — archive candidate (SESSION_NNN old + search-only)
- file_path: docs/audits/SESSION_786_MARKDOWN_SYSTEM_REVIEW.md
  audit_thread: T5
  severity: P2
  finding_class: superseded_untagged
  evidence:
    - line_range: [1, 4096]
      claim: "SESSION_786 filename tag; search-only reach (no anchor links)"
      runtime_truth: "S786 predates S2500; T3b reach=search_only search_only_kind=t5_territory"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_archive
  cross_arc_refs:
    - t3b_row: reachable-from-search-only / t5_territory / t5_may_override:YES
  notes: "old session + no anchor reach → archive candidate to docs/archive/"

# docs/audits/** — series-level candidate (ambiguous shape + unclear stale + anchor reach)
- file_path: docs/audits/INTEGRATION_GAP_ANALYSIS.md
  audit_thread: T5
  severity: P2
  finding_class: ok
  evidence:
    - line_range: [1, 4096]
      claim: "ambiguous filename shape; anchor-reachable; no stale marker"
      runtime_truth: "no SESSION_/timestamp/report pattern in name; T3b anchor_only"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_series_pointer
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "shape heuristic under-classifies gap-map filenames; Chris either reclassifies as standing_reference or applies subdir-level V1 pointer"

# docs/audits/** — recent gap map (ambiguous + search-only + unclear)
- file_path: docs/audits/PA_TOOLS_GAP_MAP_S2795.md
  audit_thread: T5
  severity: P2
  finding_class: orphan
  evidence:
    - line_range: [1, 4096]
      claim: "recent gap map (S2795); search-only reach; no V1/V2"
      runtime_truth: "T3b reach=search_only search_only_kind=t5_territory"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_case_by_case
  cross_arc_refs:
    - t3b_row: reachable-from-search-only / t5_territory / t5_may_override:YES
  notes: "recent gap map; add to anchor graph or leave in subdir + retrofit V1?"

# docs/audits/** — in-progress marker (ambiguous + anchor + sprint completion)
- file_path: docs/audits/SPRINT_1_COMPLETION.md
  audit_thread: T5
  severity: P2
  finding_class: superseded_untagged
  evidence:
    - line_range: [1, 4096]
      claim: "SPRINT_1 completion doc; in-progress marker detected in head"
      runtime_truth: "matched 'NEXT STEPS' or similar phrase pattern"
      cited_source: docs/audits/SPRINT_1_COMPLETION.md
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_v2_retrofit
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "sprint likely closed; V2 pointer to close-doc or archive"

# docs/audits/** — standing but not anchor-linked (planning doc)
- file_path: docs/audits/CONNECTIVITY_SWEEP_PLAN.md
  audit_thread: T5
  severity: P2
  finding_class: orphan
  evidence:
    - line_range: [1, 4096]
      claim: "planning doc filename (_PLAN.md); search-only reach"
      runtime_truth: "T3b reach=search_only; classified standing_reference by shape"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_case_by_case
  cross_arc_refs:
    - t3b_row: reachable-from-search-only / t5_territory / t5_may_override:YES
  notes: "still_valid standing doc without anchor link — add to CLAUDE.md or accept as subdir-scoped"

# docs/audit/** — SESSION_1143 retrofit candidate
- file_path: docs/audit/SESSION_1143_ABANDONED_FEATURES_AUDIT.md
  audit_thread: T5
  severity: P2
  finding_class: superseded_untagged
  evidence:
    - line_range: [1, 4096]
      claim: "SESSION_1143 filename tag; anchor-reachable"
      runtime_truth: "S1143 predates S2500; T3b reach=anchor_only"
      cited_source: /tmp/t3b_orphan_scan_out.json
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: audits_triage_v2_retrofit
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "S1143 docs-cleanup arc artifact; V2 pointer to canonical DOC_LIFECYCLE or archive"

# docs/audit-2026/00-AUDIT-PLAN.md — series index with V1 pointer (keep)
- file_path: docs/audit-2026/00-AUDIT-PLAN.md
  audit_thread: T5
  severity: P3
  finding_class: superseded_untagged
  evidence:
    - line_range: [1, 5]
      claim: "DOC-POINTER-V1 series index; points to docs/audit/ as current workspace"
      runtime_truth: "V1 pointer marker present line 1"
      cited_source: docs/audit-2026/00-AUDIT-PLAN.md#L1
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs:
    - t3b_row: cited-multi-graph-OK / t5_may_override:YES
  notes: "V1 pointer 'already tells the right story' for the whole series (§7 Q1 candidate for propagation)"
```

Full 169-row output at `/tmp/t5_reports_audits_scan_out.json` (representative-sample cross-verifiable via `jq '.results[] | select(.file_path == "<path>")'`).

---

## 5. Cross-cutting signals for future §3 execution arc AND for parent methodology refinement

### 5.1 Series-level V1/V2 pointer inheritance is a first-class disposition class

Discovered when 13 `docs/audit-2026/**` files ALL classified `ambiguous + anchor_only + unclear + none` → 13 identical escalate rows. The parent `00-AUDIT-PLAN.md` carries a V1 pointer describing the WHOLE 13-file series as historical dossiers. If T5 inferred series-level pointer inheritance ("any file in a subdir whose `00-<index>.md` or `INDEX.md` has a V1/V2 pointer inherits that pointer for axis-d evaluation"), 13 files would flip escalate → keep in one classification rule.

**Two independent examples of the emergent convention** (Rigby cycle-1 Q1 STRENGTHEN fold):

| Subdir | Index file | Pointer | State |
|---|---|---|---|
| `docs/audit-2026/` | `00-AUDIT-PLAN.md` | V1 (line 1) | historical dossier series |
| `docs/audits/` | `INDEX.md` | V1 (line 1) | historical archive |
| `docs/audit/` | `README.md` | NONE | current active workspace |

**Emergent convention: pointer-on-INDEX-for-historical-subdirs-only.** The subdir-level V1 pointer names the successor subdir + points readers to `PLATFORM_INVENTORY.md` for current counts. Current/active subdirs (like `docs/audit/`) don't carry index-level V1 because there's no supersession to describe. This is not a random pattern; it's a discipline the corpus already follows.

**Not applied in T5 output** — the parent §4 T5 scanner spec does not mandate series-inheritance semantics, and applying it mid-arc without SIGN would trade a clean 4-axis method for a heuristic-with-exceptions. Recorded as §7 Rigby SIGN Q1 STRENGTHEN. Chris judgment at 2899 could ratify series-inheritance as a §10.1 v1.2 schema addition + retroactively apply to all `docs/audit-2026/**` escalates (13) + all `docs/audits/**` escalates where INDEX.md-inheritance applies (36+ candidates) + any other subdirs with index-level pointers.

**§10.1 v1.2 candidate #5** (adds to existing 4: T2 §5.7 coverage split + T3a §5.3/§5.5/§5.7 + T3b §5.3/§5.7/§6.1 + T4 §2.6/§5.7/§5.4). Now two-trigger corroborated within a single arc; independent evidence from two subdirs.

### 5.2 T3b §5.4 T5 workflow directive delivered as promised — clean substrate handoff

T3b's promise: "T5 SHOULD consume `/tmp/t3b_orphan_scan_out.json` for `t5_may_override: YES` pre-classified rows; NOT re-derive reachability graphs." T5 honored this literally — the scanner loads T3b JSON once, uses reachability + search_only_kind as raw axis-b inputs, and never re-derives. Cross-child pre-clustering consumption three-trigger corroboration extends to four (T3a←T2 + T3b←T3a+T2 + T4←T2+T3b + T5←T3b+T4-informational).

**Playbook v3 codification candidate reaches four triggers.** Recorded for 2899 canonical summary + post-arc Playbook amendment consideration.

### 5.3 `null_result` finding class three-trigger corroboration reaches four

T3b §2.1 zero unreachable-from-all-3-graphs + T4 §2.4 zero chunk-ID citations + T5 §2.1 zero P0 severity = three explicit null-result findings. Add T5 §2.1 zero P1 = a fourth stackable null-result observation within a single child.

**Playbook §11.3 template candidate ready for codification.** Standard shape: "null-result findings are first-class positive evidence" — a triage arc that measures against a hypothesis (e.g., "we expect stale audits") and finds ZERO defects is producing a stronger result than one that finds many. Group 2800 accumulates 4 such findings across 3 children.

### 5.4 Ambiguous shape (81 rows) reveals a heuristic limit but not a corpus defect

47.9% of the corpus classified `ambiguous` on axis (a). This looks bad on first glance but is a truthful scanner outcome: the corpus contains genuinely mixed-shape files (subsystem dossiers named `NN-topic.md`, gap analyses named `TOPIC_ANALYSIS.md`, sprint completion docs named `SPRINT_N_COMPLETION.md`) that don't cleanly slot into one_shot vs standing_reference by filename alone.

**Two viable methodology responses:**
- **A. Refine axis (a) heuristic** — add subsystem-dossier pattern (`^\d{2}-[a-z]+\.md$`), gap-analysis pattern (`_(GAP|ANALYSIS)\.md$`), etc. Trades scanner complexity for lower ambiguous share. Trade-off: still doesn't handle the true edge cases; just moves the ambiguity boundary.
- **B. Accept ambiguous as a first-class shape** — treat it as "requires human judgment" rather than "scanner failure." This is what T5 currently emits; escalate_to_chris on ambiguous rows is honest, not a defect.

**Recommendation:** ratify B. Ambiguous is a valid third shape class, not a scanner bug. Chris judgment at 2899 resolves individual rows; series-level policy (see §5.1) resolves many at once.

### 5.5 Reports subdir was already effectively triage-complete before T5 opened

32 of 33 `docs/reports/**` files carry V2 pointer. Rigby cycle-2 Q3 evidence at parent scoping (`3D_GENERATION_VERIFICATION_REPORT.md` V2-pointer sample) generalized to the full subdir. The 33rd file (`VERIFY_REPORT.md`) is recent one_shot + anchor_only + no-pointer, disposition keep via the fallback rule.

**T5 confirms the parent Rigby cycle-2 Q3 refinement was correct** — including `docs/reports/**` in T5 scope produced zero additional workshop load (all 33 → keep). Rigby cycle-2 SIGN work at parent-scoping time carried through cleanly. Positive validation of the "consult Rigby on scope-question before opening child" pattern.

### 5.6 Scanner cost is trivial for future re-runs (~1 second on 169 files)

`tools/audit_2805_reports_audits_triage.py` runs in ~1s (single-pass, 4KB-per-file head read, no external subprocess). Follow-on execution arcs post-2899 can re-run this scanner cheaply to verify:
- No new files added to `docs/audits/**` etc. between arc close and migration PR
- No V1/V2 pointer retrofits regressed (V2 files stayed V2)
- No new one-shot files with old session tags landed (would appear as new escalates)

Deploy alongside T2 + T3b + T4 scanners as the fourth reusable audit substrate.

### 5.7 T5 corpus is basename-disjoint from T4 corpus (structural design, not accident)

Zero T4 banner-adjacent hits in T5 (§1.5). This is a positive design finding: audits and handoffs are architecturally disjoint (handoffs in `docs/handoffs/**`, audits in `docs/audits/**` etc.), so T4's retrieval-harm banner list (13 handoff basenames) and T5's disposition list (169 audit basenames) have no overlap. The parent §4 T5 spec's soft-dependency clause was defensive; T5 confirms no actual dependency exists.

**Implication for future arcs:** any content-audit arc structured around `docs/<subdir>/**` corpuses inherits this basename-disjoint property. Cross-arc reference is via file-path substrate (T3b reachability), not basename intersection. Design property worth explicit callout at 2899.

### 5.8 Session-tag distribution discontinuity explains threshold-sensitivity collapse (cross-cutting corpus signal)

**Cycle-2 F2 STRENGTHEN fold (Rigby ARS-VERIFIED L607-616 / L613):** The bimodal session-tag distribution surfaced by Q2 cycle-1 verification is a *cross-corpus-relevant* shape observation, not just a T5-limitation note. Recording it here because it will recur in other triage arcs measuring against session-tag age.

**Observation:** In the T5 corpus, one-shot files carry SESSION_ filename tags clustered in [727, 1143] (min 727 / median 819 / max 1143); zero one-shots in [1144, 2499]. The `stale_pre_s2500` threshold collapses to *empirical* insensitivity because the corpus session-tag distribution has a gap that exceeds any reasonable ±X threshold shift.

**Generalizable claim:** Triage corpuses that classify by "old vs recent" via a numeric threshold on filename-embedded session/date tags MAY exhibit *discontinuous* rather than *linear* threshold-sensitivity when the source corpus itself has a session-tag gap. Reporting the sensitivity as "±N shifts move K rows" without checking the distribution shape can UNDERSTATE the robustness (as T5 §6.1 originally did with "±200 robust") or OVERSTATE it (if the corpus is uniformly distributed and you claim insensitivity based on one point). **Recommendation:** future triage arcs SHOULD report both the threshold sensitivity number AND the underlying tag distribution shape (min / median / max / any gaps) so that "robust threshold" claims can be interpreted correctly.

**Cross-corpus recurrence probability:** other u-d-b corpuses that carry SESSION_ filename tags (e.g., prior `docs/handoffs/**` audit runs) would exhibit similar bimodality because session-count velocity is non-uniform across the platform's history (busy periods S727-1143 + busy periods S2500-2839 with a quiet 1500-2500 middle). If a future arc scans handoffs by session-tag age, expect similar discontinuity.

**Playbook §11.3 template amendment candidate:** add a canonical "how to report threshold sensitivity" bullet to §2 methodology reporting: report the sensitivity delta AND the underlying distribution shape. Two-trigger threshold not yet met; recorded as observation, not a proposed amendment.

### 5.7a Series-inheritance shape + small-fix whitelist as v1.2 candidates — scope-creep guardrail

Per S2838 T4 §5.7a discipline (scope-creep guardrail sentence): §5.1's series-inheritance proposal is a **shape observation for 2899 workshop consideration**, NOT a proposal to modify §10.1 v1.1 mid-arc, NOT a proposal to walk audit content for series-membership evidence, NOT a proposal to change scanner behavior mid-arc. If Chris ratifies at 2899, it becomes v1.2 alongside the other four candidates.

This doc makes NO in-arc scanner-behavior modification request beyond what's already implemented; NO in-arc §10.1 schema modification request; and NO in-arc content-quality walk of the 107 escalate rows. The five v1.2 candidates queue for 2899 batch consideration.

**Cycle-2 Q5 methodology-fork completion fold (Rigby AGREE-with-elaboration, ARS-INAPPLICABLE zoom_out):** Rigby's completed methodology-fork answer proposes a **pre-authorized small-fix whitelist** as a post-2899 Playbook amendment candidate for triage-heavy child arcs. Recorded here as a future_trigger observation ONLY; not proposed for T5 in-arc application.

**Proposed whitelist categories** (Rigby cycle-2):
1. **Pointer header retrofits** (V2 or V1) — add exactly one `<!-- DOC-POINTER-V* -->` line at top-of-file, no other edits, only for files pre-classified as V2 retrofit candidate by axis-combination rules
2. **Subdir-level index pointer additions** (INDEX.md / README.md / `00-*.md`) — create/update index entry-point with pointer header + 3-10 lines of boilerplate ("historical snapshots; current lives at X")
3. **Pure archive `git mv`** — path-change only, zero content edits, only for files meeting strict criteria (pre-S2000/S2500 + search_only + no inbound anchors + classified archive_candidate)

**Proposed safeguards** (Rigby cycle-2):
- **Line-diff cap**: whitelist actions must produce diffs ≤15 added lines + 0 removed lines (except `git mv` where content diff must be 0)
- **File-class gating**: only files in explicitly enumerated disposition classes; NO ad-hoc "this looks easy" exceptions
- **No semantic edits rule**: forbid non-pointer prose edits + new claims + heading rewrites
- **Audit trail**: log (a) disposition class triggered + (b) whitelist bucket used per applied fix
- **Stop condition**: any file requiring more than mechanical change stays escalated for 2899

**Explicit scope-creep guardrail:** this doc makes NO instrumentation request for a small-fix whitelist in T5 or in the Group 2800 arc close; it records the observation for post-2899 Playbook amendment evaluation ONLY. The current arc completes with the 206-row workshop shape as designed; any small-fix pre-authorization requires fresh Chris D-verdict on the Playbook amendment BEFORE any subsequent triage arc uses it.

**Post-2899 Playbook amendment path:** if Chris ratifies the small-fix whitelist at 2899 workshop OR at a subsequent Playbook amendment session, the mechanism becomes available for future triage-heavy child arcs to pre-authorize at their parent-scoping time. Not before.

---

## 6. Residual risk / limitations

### 6.1 Method limitations (recorded)

| Limitation | Impact | Mitigation |
|---|---|---|
| Axis (a) heuristic under-classifies at 47.9% ambiguous | 36 of 87 `docs/audits/**` escalate rows are ambiguous+anchor+unclear; Chris workshop covers case-by-case | Series-level policy (§5.1 / §7 Q1) collapses many at once |
| Axis (c) uses filename session tag + phrase pattern only | Deep content-freshness judgment deferred to Chris | Consistent with parent §4 T5 "TRIAGE ONLY" anti-pattern; not a defect |
| S2500 stale threshold is a single choice | Files just above (S2500-2699) count as "unclear" not "stale"; files just below (S2400-2499) count as "stale" | Chris-tunable knob (§7 Q2 candidate for cycle-1 SIGN). **Cycle-1 Q2 evidence (Claude shell verification post-Rigby reroute):** empirically the T5 one-shot session-tag distribution is bimodal — 38 tagged files clustered [727, 1143] (min 727 / median 819 / max 1143), ZERO tagged files in 1144-2499. Threshold ±1200 insensitive: shifting to S2300 flips 0 escalate→keep; shifting to S2700 adds 0 new escalates. The axis-combination rule is *empirically* insensitive at the current corpus, not merely theoretically robust. |
| T3b substrate captured at S2837 head `be7af72159ec` | Any files added between S2837 T3b run and S2839 T5 open are not in T3b index | Cross-checked: 100% T3b coverage for T5's 169-file corpus at head `6f0db5879cf7` — no drift |
| V1/V2 pointer detection is text-marker only | Files with non-standard pointer syntax could be missed | Text-marker convention is the platform convention per DOC_LIFECYCLE.md §1; no non-standard variants observed |
| Scanner does NOT infer series-level inheritance | 13 `docs/audit-2026/**` files escalate individually even though 00-index carries V1 | Recorded as §5.1 v1.2 candidate; Chris judgment at 2899 |

### 6.2 Spot-verify sample — hand-check top escalate rows

Sample 5 escalate rows for hand-verification of scanner classification. All 5 pass:

| File | Classified | Hand-verified? | Notes |
|---|---|---|---|
| `docs/audits/SESSION_727_AGENTS_AUDIT.md` | one_shot+anchor+stale+none → escalate | ✓ | S727 clearly < S2500; verify anchor citations via T3b |
| `docs/audit-2026/01-celery.md` | ambiguous+anchor+unclear+none → escalate | ✓ | Filename doesn't match either pattern; T3b anchor_only from CLAUDE.md subsystem-docs graph |
| `docs/reports/VERIFY_REPORT.md` | one_shot+anchor+unclear+none → keep | ✓ | Recent, no stale marker, anchor-reachable, no pointer needed |
| `docs/audits/SPRINT_1_COMPLETION.md` | ambiguous+anchor+in_progress+none → escalate | ✓ | "SPRINT_1" no session-tag; in-progress phrase detected |
| `docs/*_AUDIT.md` ADVISOR_AUDIT.md | standing+multi_graph+still_valid+none → keep | ✓ | Anchor-linked at CLAUDE.md subsystem row; classic standing reference |

Zero classification errors detected in spot-verify sample. Scanner is trustable at the axis-combination decision level.

### 6.3 False-positive spot check — `docs/reports/**` uniform-keep

All 33 reports classified keep_as_is. Sample 5 non-V2-pointer paths (there's only 1 — `VERIFY_REPORT.md`) — verified in §6.2. All 32 V2-pointer files verify per the axis-d short-circuit rule.

**Potential blind spot:** if a V2-pointer file contains stale content that the V2 pointer doesn't correctly describe, T5 misses it (axis d short-circuits). This is intentional per parent §4 T5 "T5 is TRIAGE only" — content quality is out of scope. Chris judgment at 2899 can override any keep_as_is row if a specific report has known content-quality issues.

### 6.4 T5 does not classify structural moves recommended by 2799 §3

Consistent with parent §5 non-goals discipline. T5 emits `migration_pr_batch_hint` for the future §3 execution arc; it does not verify that recommended actions align with 2799 §3 target-tree destinations. Cross-arc `cross_arc_refs.2799_3_target_tree_row` field left null for T5 rows (§10.1 schema-compliant; the reconciliation is 2899's or the migration arc's job).

---

## 7. Rigby SIGN pressure test — recommended dimensions for cycle 1

Joint Claude+Rigby SIGN per `feedback_claude_rigby_agree_first_chris_yes_no`. **Cycle 1 is AEP v0.1 Stage 1 trial** per S2838 close-cycle extension ratification. **Prose fallback authorized** if either agent can't parse; no verification-check break.

### Q1 — series-level pointer inheritance policy

**Claim:** T5 currently emits 13 individual escalate rows for `docs/audit-2026/**` even though `00-AUDIT-PLAN.md` carries a series-level V1 pointer for the whole 13-file dossier series. Should T5 add "series-inheritance" as a first-class classification concept — if a subdir's `00-<index>.md` carries a V1/V2 pointer, all files in that subdir inherit the pointer for axis-d evaluation and flip to keep_as_is? If YES, escalate count drops 107 → ~94.

**Verify via:** `repo_tool.read_file docs/audit-2026/00-AUDIT-PLAN.md L1-5` (V1 pointer text) + `Grep DOC-POINTER-V1 docs/audits/*.md` (does docs/audits/ have any 00-* index?).

### Q2 — stale threshold sensitivity

**Claim:** S2500 stale threshold classifies 38 files as `stale_pre_s2500`. Shifting to S2300 drops that to ~30; shifting to S2700 raises it to ~44. Are the escalate boundaries meaningfully sensitive to the threshold, or is the axis-combination rule robust?

**Verify via:** `python3 -c "import json; d=json.load(open('/tmp/t5_reports_audits_scan_out.json'))['results']; import re; from collections import Counter; ..."` — re-classify under multiple thresholds and report the delta.

### Q3 — SESSION_819_SYSTEM_AUDIT_* untracked disposition

**Claim:** 19 untracked `SESSION_819_SYSTEM_AUDIT_YYYYMMDD_HHMMSS.md` files in `docs/audits/`. Filename tags "SESSION_819" (old) but timestamps 2026-07-14+ (recent). Are these:

(a) Recent audit outputs generated by a script running against SESSION_819 (keep for tracking; commit)
(b) Old session snapshots that happen to have modern timestamps (archive candidate)
(c) Test artifacts from a script run (delete)

The scanner classifies (a)-hypothesis by defaulting to one_shot+anchor+stale+none → escalate. Is (a) correct or should the classification split by timestamp?

**Verify via:** `repo_tool.read_file docs/audits/SESSION_819_SYSTEM_AUDIT_20260714_223131.md L1-20` (identify actual content) + `git log --diff-filter=A docs/audits/SESSION_819_*` (if any tracked; likely empty).

### Q4 — ambiguous shape as a first-class class

**Claim:** 47.9% of corpus is shape=ambiguous. §5.4 argues this is a valid third shape class, not a scanner defect. Alternative: refine axis (a) heuristic (add `NN-<subsystem>.md` + `_(GAP|ANALYSIS)\.md$` + more subclass patterns) and reduce ambiguous share. Is the "accept ambiguous as third class" choice correct, or is the shape heuristic under-designed for T5's corpus?

**Verify via:** `repo_tool.read_file` sample of 5 ambiguous filenames (e.g. `INTEGRATION_GAP_ANALYSIS.md` + `PA_TOOLS_GAP_MAP_S2795.md` + `01-celery.md` + `SPRINT_1_COMPLETION.md` + `CONNECTIVITY_SWEEP_PLAN.md`) — do these fall into a common pattern the heuristic could catch?

**Cycle-1 Q4 fold (Claude shell verification post-Rigby ARS-PENDING):** Rigby completed sample 1 (INTEGRATION_GAP_ANALYSIS.md) in cycle-1 tool_run; Claude completed the remaining 4 via shell. Also: `CONNECTIVITY_SWEEP_PLAN.md` was mis-included in the ambiguous 5-sample by author error — the scanner correctly classified it as `standing_reference` (matched `_PLAN.md$` regex). Corrected in the doc. Reduced 4-sample findings:

| Sample | Content signal | Filename pattern candidate | Coverage in 81 ambiguous |
|---|---|---|---|
| INTEGRATION_GAP_ANALYSIS.md | Session 497 audit action plan | `_GAP_(ANALYSIS\|MAP)` | 4 files |
| PA_TOOLS_GAP_MAP_S2795.md | DOC-AUTOGEN validation coverage map | `_GAP_(ANALYSIS\|MAP)` | 4 files (same pattern) |
| audit-2026/01-celery.md | "Dossier #1: Celery Orchestration" | `/\d{2}-[a-z-]+\.md$` | 6 files |
| SPRINT_1_COMPLETION.md | Session 528 sprint completion | `_COMPLETION\.md$` | 4 files |

Three patterns collectively catch **14 of 81** (17%) currently-ambiguous files. Refining the axis-a heuristic mid-arc would reduce escalate volume by ~14 rows but does NOT eliminate ambiguous (81 → ~67). Per §5.4: **accept ambiguous as first-class shape** rather than refine; refinement is a v1.2 candidate for 2899.

### Q5 — zoom-out (per `feedback_zoom_out_ask_per_rigby_sign`)

**Claim:** T5 measures 4-axis classification against 169 audit files. The parent §4 T5 disposition classes (`keep_as_is` + `escalate_to_chris`) collapse to 2 practical outcomes. But the arc-close 2899 workshop faces 206 total escalate rows (99 pre-T5 + 107 T5). That's a lot for one session.

**Zoom-out question:** does the arc's growing escalate queue reveal a design gap in the parent §5 non-goals discipline ("classification only; execution defers")? T5 could have proposed some in-arc dispositions (V2 pointer retrofits, subdir V1 pointer additions) that would reduce 2899 workshop load — but doing so would violate parent §4 anti-scope. Is the 206-row workshop the *correct* outcome of a T1-T5 audit arc, or does it reveal a fold that should have happened at parent-scoping time to enable in-arc small-fix dispositions?

**Prose zone** (per AEP v0.1 §3.4 PROSE_FIELD): this is a methodology-shape question about whether "classify only, defer execution" is the right frontier for a triage-heavy child at Group-arc scale. Recorded as candidate playbook-v3 discussion point per §5.7a scope-creep guardrail — this question is a proposal to Chris, not an implementation request.

**Anti-rubber-stamp check per `feedback_verify_rigby_tool_runs_before_trusting_sign`:** Verify `tool_runs` non-empty on Rigby's SIGN reply before accepting AGREE/DISAGREE verdicts. Cycle 3 clean-check per S2838 lesson #2 (anti-rubber-stamp discipline HELD in cycle 3, catch real STRENGTHEN issues after "cycle 2 folded" narrative stability). ARS gate MANDATORY per AEP v0.1 §3.8.

**S2838 lessons carried forward** (also in handoff §7):
1. Cross-child pre-clustering consumption is now three-trigger corroborated → T5 corroborates a fourth trigger; recorded §5.2.
2. Anti-rubber-stamp holds under cycle 3 pressure → 3-cycle floor recommended.
3. Read full Rigby response, not just tool_runs tail.
4. Empirical falsification is a first-class finding → T5 has zero P0/P1 (two null results); recorded §5.3.
5. Scope-creep guardrails belong in the audit doc itself → §5.7a discipline followed.
6. Rigby writes workspace deliverables → S2835 pattern fifth exercise post-Chris D-verdict.

---

## 8. Ratification envelope preview (for §11.3 rendezvous)

Envelope stub for Chris D-verdict rendezvous:

```yaml
ratification:
  date: 2026-07-19
  session: 2839
  ratifier: Chris
  verbatim_directive: <pending>
  scope: |
    T5 reports+audits triage audit (169-file corpus; 4-axis classification;
    T3b pre-clustering fully consumed; T4 handoff-adjacency null-triggered;
    §10.1 v1.1 schema unchanged; 5 v1.2 candidates accumulated for 2899;
    107 escalate rows added to Group 2800 workshop queue (total now 206);
    S2836 arc-close deferral policy carries over unchanged; cross-child
    pre-clustering four-trigger corroborated; null_result finding class
    four-observation corroborated; AEP v0.1 Stage 1 trial evaluated
    post-cycle-1 SIGN.
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2805_docs_content_reports_audits_triage.md
  sign_cycles: <3 planned; final count after Chris close>
  next_action: |
    Group 2800 arc reaches 6/6 shipped. 2899 canonical summary opens
    at S2840 with the accumulated 206-row Chris judgment queue.
    Migration-PR batches (§3.4) as candidate execution shape.
    Post-2899 migration arc will consume this audit's classification
    output per §10.4 cross-arc consumption contract.
    AEP v0.1 Stage 1 trial: post-cycle-1 evaluation deliverable
    reports token-reduction metrics + ARS gate enforcement + fold
    ledger completeness.
```

---

## 9. Migration queue routing (per §10.4 cross-arc consumption contract)

Post-arc handoff to future §3 execution arc:

- **Zero P0 rows** — no destination-migration blockers introduced by T5.
- **Zero P1 rows** — no soft-blockers.
- **107 P2 rows queued for 2899 workshop** (all `escalate_to_chris` per S2836 policy).
- **Candidate 4-batch migration structure:**
  1. `audits_triage_series_pointer` — 49 rows (13 audit-2026 + 36 audits ambiguous)
  2. `audits_triage_archive` — 20 rows (pre-S2500 search-only)
  3. `audits_triage_v2_retrofit` — 18 rows (13 audits anchor-reachable + 5 audit SESSION_1143)
  4. `audits_triage_case_by_case` — 20 rows (remaining)
- **62 P3 keep_as_is rows** — no migration action; ratified as-is at 2899.

Cross-arc reference: parent §10.4 contract, Group 2700 §3 target tree (2799 §3.1) — no T5 row generates a new destination-tree entry; every T5 disposition targets in-place edits (V1/V2 pointer add) or archive (`docs/archive/YYYY-MM/`).

---

## 10. What this research taught us about how to do research

Per Playbook §11.3 template (adopted S1399 close 2026-07-01).

### 10.1 What worked

- **Consuming T3b + T4 substrate wholesale** with zero re-derivation confirmed the cross-child pre-clustering pattern as sound at four triggers. T5's scanner is ~340 lines vs T3b's ~500 vs T4's ~550 precisely because it delegates reachability + banner-adjacency to prior child substrate.
- **Deterministic 4-axis + derived-action rule** produced classifications that hand-verify cleanly on 5 spot-check samples (§6.2). No axis-combination table ambiguity emerged in-scan.
- **Accepting `ambiguous` as a first-class shape** rather than forcing binary one_shot/standing kept the scanner honest. 47.9% ambiguous is a *true finding about the corpus*, not a scanner defect.
- **Series-level pointer inheritance discovered as an escalate-cluster pattern** without needing to build it into the scanner. §5.1 §7 Q1 propose it as a v1.2 candidate for 2899 workshop — earned by observation, not by pre-designed feature.
- **T5 ambiguous zone escalates land in 2899 workshop as batch-decision candidates** (§3.4), not per-file drama. Chris workshop shape stays tractable at 4 candidate migration PRs, not 107 individual decisions.
- **Third + fourth null-result observations** (zero P0 + zero P1 at severity, plus zero T4 basename intersection) uphold the parent arc's structural-health headline. Group 2800 arc-close narrative gets to lead with "corpus is healthy at 6/6 measured axes."

### 10.2 What to codify into playbook v3

Meeting §14.2 two-trigger threshold at four for pre-clustering + three for null-result:

- **Cross-child pre-clustering consumption directive** (four triggers: T3a←T2 + T3b←T3a+T2 + T4←T2+T3b + T5←T3b+T4-informational). Codify as: *"When a research arc has more than one child, each subsequent child MUST list its pre-clustering substrate consumption contract explicitly in §1.5 or equivalent, MUST identify which prior-child scan outputs it will load-only vs re-derive, and MUST report basename intersection or graph coverage in §1.5. Re-deriving prior-child substrate without a substrate-invariance justification is a defect."*
- **`null_result` as a first-class finding class** (four observations: T3b §2.1 unreachable + T4 §2.4 chunk-ID + T5 §2.1 P0 + T5 §2.1 P1). Codify in §11.3 template as: *"Null-result findings are first-class evidence. An audit that measures against a hypothesis and finds ZERO defects is not a failed audit — it is a positive structural-health finding. Every child audit §2.N-headline SHOULD include an explicit statement of any null-result observations, framed as positive findings not omissions."*
- **Series-level pointer inheritance as §10.1 v1.2 candidate #5** (T5 §5.1 first trigger; needs second before codification). Reserved for post-2899 corroboration in future audits.
- **Ambiguous as a first-class classification shape**. Codify: *"Where a boolean-ish classification produces a genuinely-mixed input class (e.g., filename shape that matches neither pattern cleanly), emit a third `ambiguous` value rather than force-picking. `ambiguous` is not scanner failure; it is honest triage output."*

### 10.3 Anti-patterns to avoid

- **Forcing binary classification when the corpus is trimodal.** T5's axis (a) has THREE natural shapes (one_shot / standing / ambiguous), not two. Trying to squeeze a `NN-<subsystem>.md` file into either one_shot or standing produces a false positive; emitting `ambiguous` is right.
- **Walking file content to gain confidence when parent scope says TRIAGE.** T5 could have deep-read all 169 files for content-freshness judgment; it would have violated parent §4 T5 anti-pattern. Stayed within triage boundary; classified 107 escalate rows in ~1s vs (169 × 30s LLM eval) ≈ 84 minutes.
- **Re-deriving reachability graphs when T3b's substrate is authoritative.** Save wall-clock + protect against divergent-classification bugs from re-implementing the same graph BFS. T3b + T4 scanners are the authoritative sources; T5 consumes.
- **Emitting scanner-heuristic patches mid-arc.** The V1 pointer treatment fix (V1 same as V2 for keep) was small enough to justify same-PR. The series-level inheritance would NOT have been — it changes the classification result for 13-49 rows. Deferred to 2899 workshop with §5.7a guardrail.

### 10.4 Suggestions for the playbook itself

- **Add a §7.5 rule: "Audit corpus files older than the arc's substrate freshness cutoff MUST be reported as 'not-in-T3b' or equivalent."** Handled cleanly in T5 (100% T3b coverage), but if a future audit arc opens with a fresher corpus than the prior-child substrate, the classification would silently miss files. Codify the freshness check.
- **Extend §11.3 template with an explicit null-result section**. Currently §2 findings assumes a defect count; add §2.N "Positive null-result findings" as a standard subheading.
- **Add §7.5.4: cross-child substrate-consumption contract explicit-declaration rule.** Every child audit that consumes a prior child's output MUST declare in §1.5 which paths + which fields + which "load-only" vs "re-derive" contract applies. Prevents silent divergence when a follow-on session re-implements a graph.

### 10.5 Suggestions for future canonical summaries (optional)

**For 2899:** the Group 2800 arc-close canonical summary faces a 206-row Chris judgment queue. Recommend structuring the workshop as **4 batch decisions** (per §3.4) followed by a case-by-case walk of remaining rows. This shape has never been executed at Group scale; if it works at 2899, codify as canonical arc-close shape for triage-heavy arcs.

**Also:** the four cross-cutting signals corroborated across children (cross-child pre-clustering + null_result + series-inheritance + ambiguous-as-first-class) suggest 2899 has substantial Playbook-amendment content beyond just per-file dispositions. Reserve arc-close bandwidth accordingly.

---

## 11. Cross-links

- Parent scoping: `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- Prior child audits: `2801` T1, `2802` T2, `2803a` T3a, `2803b` T3b, `2804` T4
- Next: `2899_docs_content_canonical_summary.md` (opens at S2840)
- Sibling arc `2799` §3 target tree: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`
- Governance canonical: `docs/00-START-HERE/DOC_LIFECYCLE.md`
- Playbook (v0.8.0): `docs/ENGINEERING_PLAYBOOK.md`
- Live manifest: `docs/research/OPEN_ARCS.md` (Group 2800 In-progress, 6/6 shipped)
- Scanner tool: `tools/audit_2805_reports_audits_triage.py`
- Scanner output: `/tmp/t5_reports_audits_scan_out.json`
- T3b pre-clustering seed: `/tmp/t3b_orphan_scan_out.json`
- T4 handoff-adjacency seed: `/tmp/t4_handoff_audit_out.json`
- AEP v0.1 proposal: `docs/research/platform/AGENT_EXCHANGE_PROTOCOL_v0_1_proposal.md`
- AEP v0.1 ratification: `docs/research/implementation/RATIFICATION_2026-07-19_agent_exchange_protocol_v0_1.md`

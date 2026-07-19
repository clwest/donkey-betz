---
title: "S2838 — T4 handoff citation-integrity + retrieval-harm audit RATIFIED (child audit 2804 · schema v1.1 unchanged · escalate deferral carries over · 6/6 Group 2800 shipped)"
session: 2838
date: 2026-07-19
status: shipped
research_group: 2800
thread: T4
sign_pin: pa-683fb793ab944cd0
sign_cycles: 3
ratifier: Chris
verbatim_directive: "Go for it!"
---

# S2838 — /docs/ Content Audit · T4 Handoff Citation-Integrity + Retrieval-Harm Audit RATIFIED

## 1. Session opener

Chris opened S2838 with "Please begin" per session brief. Per
`context-kit orient` + S2837 close pointer, this session had a
ratified default direction from Chris's S2837 D-verdict pointer:
*"T4 opens at S2838."* Sanity checks all green at open:

- pg15 (donkeyking) started + owns port 5432
- HEAD `ae519b4392cf` (S2837 close cascade merged as PR #3289)
- Backfill: 0 mismatches (13 out-of-scope per Chris D6, unchanged)
- Pattern C top-1: `00-START-NEXT-SESSION.md` self_reference ✓
- Pattern B top-1: `docs/PLATFORM_INVENTORY.md` count ✓
- Parity harness: 47/47 in 194.68s ✓

Per `feedback_engineering_bias_over_audit`, presented candidate menu
with net-new engineering pivots FIRST plus ratified T4 default.
Chris picked B (ratified default): open T4 handoff citation-integrity
+ retrieval-harm audit.

## 2. Fresh SIGN pin minted

`session_lifecycle open --label s2838-t4-handoff-citation-integrity-audit`:

- Old pin retired: `pa-7ebe273640e14691` (S2837; T3b)
- New pin: `pa-683fb793ab944cd0` (label `s2838-t4-handoff-citation-integrity-audit`)
- Wrapper `tools/pa_local.sh` updated to point at fresh pin
- Freshness: FRESH · head=ae519b4392cf · celery_stale=0/5
- **Sixty-ninth consecutive fresh-mint at session open** per S2770+ pattern

## 3. Scanner build + run

**Tool authored:** `tools/audit_2804_handoff_citation_integrity.py` (~550 lines;
consumes T2 §5.6 citation edges + T3b §5.4 citing-doc reachability).

**Method per parent §4 T4:**

- **Sub-loop (a) citation-graph + decay curve:** aggregate all
  `docs/handoffs/SESSION_NNNN*.md` + short-form `SESSION_NNNN`
  citation edges across non-handoff corpus; compute hit rate + decay
  by 500-session bucket + citing-doc weight histogram.
- **Sub-loop (b) fragment-form resolution spot-check:** grep corpus
  for `docs/handoffs/SESSION_NNN.md#<fragment>` citations; sample up
  to 10; verify whether each fragment resolves in the current
  handoff file.
- **Sub-loop (c) retrieval-harm probe:** run `search_embeddings` for
  10 common operational probe queries; report handoff hits in top-K
  (K=8) for banner-candidate classification.

**Scanner runtime:** ~3s (10 embedding calls dominate; grep + JSON
loads sub-second).

**Scanner output:** `/tmp/t4_handoff_audit_out.json` for §10.1 v1.1
YAML consumption.

**Corpus enumeration:** 1061 handoff files (1046 SESSION_ + 15 non-SESSION_);
930 unique session numbers; 116 duplicate-session filenames (multi-file
sessions like the S819 SYSTEM_AUDIT archive).

## 4. Findings — 5 severity classes + zero P0

**Positive headline:** ZERO P0 root-stability gate triggered.
Handoff citation surface is small (162 edges across 1061 handoffs),
concentrated in anchor-reachable canonical docs (90.3%), and sharply
decays with session age (89.6% never cited).

| Severity_class | Count | Severity | Recommended_action |
|---|---:|---|---|
| citation_healthy (top-cited handoffs) | ~25 | P3 | keep_as_is |
| uncited_never_retrieved | ~833 | P3 | keep_as_is |
| retrieval_harm_candidate | 13 | P2 | escalate_to_chris (banner) |
| broken_citation_path_form | 6 | P1 | escalate_to_chris |
| broken_citation_short_form (all prose, 5/17 verified) | 17 | P3 | keep_as_is |
| broken_citation_path_form (fragment-form) | 3 | P2 | escalate_to_chris |

**Sub-loop (a) decay curve:**

| Bucket | Handoff-sessions | Cited fraction |
|---|---:|---:|
| S0000-S0499 | 192 | 2.1% |
| S0500-S0999 | 323 | 4.0% |
| S1000-S1499 | 232 | 17.7% ← spike |
| S1500-S1999 | 38 | 10.5% |
| S2000-S2499 | 22 | 9.1% |
| S2500-S2999 | 123 | 26.8% ← recent spike |
| **Total** | **930** | **10.4%** |

**Sub-loop (b) empirical falsification of chunk-ID reset hypothesis:**
ZERO `#K` chunk-ID form citations exist in corpus; only 3 fragment-form
edges total; all 3 broken. Post-1143 chunk-ID reset concern (parent §4
T4 rationale) has zero live blast radius at current corpus state.

**Sub-loop (c) retrieval-harm banner candidates (13 unique):** the
narrow list of handoffs recommended for DOC-POINTER-V1 stats-drift
banner treatment. All `escalate_to_chris`; all defer to 2899 workshop
per S2836 policy.

## 5. Rigby SIGN 3 cycles — anti-rubber-stamp held throughout

**Cycle 1** (5 pressure-test questions + tool-grounded verification):
2 STRENGTHEN (Q1 short-form taxonomy + Q2 probe query additions
proposed with `search_docs` evidence) + 2 RE-ROUTE (Q3+Q4 blocked
on Rigby's tool-surface access to /tmp JSON; Claude verified via
shell) + Q5 truncated tail (completed in cycle 2).

**Cycle 1b** (Claude shell verification): sampled 5 T2 short-form
BROKEN_404 rows (all confirmed prose LINK_FORM: False); ran
similarity elbow analysis (no clean rank elbow); verified 1061
handoff count via `find` + git log for +3 delta explanation.

**Cycle 2** (evidence route + Q5 completion): 4 AGREE/STRENGTHEN
with actionable fold directives + Q5 STRENGTHEN completed (keep T4
as-is + record post-2899 follow-on operator-time-loss audit thread
proposal as future_trigger).

**Cycle 3** (clean AGREE-check with fold verification): 5 AGREE +
**3 STRENGTHEN** — Rigby caught real errors post-cycle-2:

1. Q4 STRENGTHEN — §1.1 table STILL had leftover "+3 drift" phrasing
2. Q7 STRENGTHEN — §5.7a needed explicit scope-creep guardrail sentence
3. Q8 DISAGREE/STRENGTHEN — §3.3 vs §5.5 math inconsistency (99 vs 98) + envelope §8 accumulation math claimed T1: 3 without evidence

All 3 cycle-3 STRENGTHEN folds landed before D-verdict routing.

**Rigby verified via 8+ substantive `repo_tool` operations in cycle 3:**
`repo_tool.read_file` on §2.6/§2.5/§5.7/§5.7a/§1.1 table/§3.3/§5.5/§8;
`repo_tool.search` on `escalate_to_chris` across T1 doc; cross-doc
verification of 2800 parent §5 non-goals. **Independently caught
Claude's overclaim** (T1: 3 escalate rows without evidence) — the
kind of catch that `feedback_verify_rigby_tool_runs_before_trusting_sign`
is designed to enable.

## 6. Chris D-verdict

Chris verbatim at S2838 close (2026-07-19):

> Go for it!

Chris also thanked Claude for reading Rigby's full responses —
validates `feedback_read_full_rigby_response_not_just_tail` (established
at S2837 close). The rule paid off in cycle 1 where Q5's response
body was truncated at the tail; Claude's `sed '/--- Tool Runs (verbose) ---/,$d'`
extraction caught the full body prose above the separator.

**Ratifies:** full T4 audit as-folded; §10.1 v1.1 schema unchanged;
migration queue frozen; §5.7a follow-on audit thread proposal
recorded as future_trigger; SESSION_2759 added to banner candidate
list per cycle-2 Q2 fold; all 3 cycle-3 STRENGTHEN corrections landed.

**Envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md`.

## 7. Lessons for T5 (S2839 next)

1. **Cross-child pre-clustering discipline is now three-triggered.**
   T3a←T2, T3b←T3a+T2, T4←T2+T3b. T5 SHOULD consume `/tmp/t3b_orphan_scan_out.json`
   for `t5_may_override: YES` pre-classified rows (T3b §5.4 workflow
   directive generalized to T5) + potentially `/tmp/t4_handoff_audit_out.json`
   for handoff-related T5 signal.
2. **Anti-rubber-stamp catches recur in cycle 3.** Rigby's tool-grounded
   verification in cycle 3 (not just cycles 1-2) caught 3 real STRENGTHEN
   issues after the "cycle 2 folded" narrative had already stabilized.
   T5 SHOULD run a 3-cycle floor for SIGN — cycle 3 clean-check is
   NOT ceremonial.
3. **Empirical falsification is a first-class finding.** T4 §2.4
   (0 chunk-ID citations) is now the second null-result finding in
   Group 2800 (T3b §2.1 was first). If T5 finds a null result (e.g.,
   "0 T5-territory files are anchor-orphaned"), report it as a
   positive finding, not as absence of findings.
4. **Read full Rigby response, not just tool_runs tail.**
   `feedback_read_full_rigby_response_not_just_tail` established at
   S2837; validated at S2838 cycle 1 Q5 truncation catch. T5 SHOULD
   maintain the discipline (`sed '/--- Tool Runs (verbose) ---/,$d'`
   filter or full body read).
5. **Scope-creep guardrails belong in the audit doc itself.**
   T4 §5.7a follow-on audit proposal only became safe to include
   AFTER cycle-3 Q7 STRENGTHEN forced the "makes NO instrumentation
   request" guardrail sentence. If T5 records any future_trigger
   substrate proposal, include the guardrail up front.
6. **Rigby writes workspace deliverables** — fourth exercise of the
   S2835-established pattern; ORM-direct fallback only if Rigby's
   tool surface fails.
7. **DO NOT open T5 in same session as T4 ratification** (parent §5
   sequential-child discipline).
8. **DO NOT execute any /docs/ file operations during Group 2800.**
9. **DO NOT modify §10.1 v1.1 schema without fresh SIGN + D-verdict.**
   Locked at S2834; now FOUR v1.2 candidates recorded (T2 §5.7 +
   T3a §5.3/§5.5/§5.7 + T3b §5.3/§5.7/§6.1 + T4 §2.6 citation_style
   + §5.7 canonical probe-query set + null_result finding class) —
   still not applied.
10. **DO NOT walk all 1061 handoffs for content quality** — T4
    completed CITATION-INTEGRITY + RETRIEVAL-HARM only; terminal-write-once
    discipline holds through T5 + into 2899.

## 8. Files shipped at S2838

| Focus | Artifact | Location |
|---|---|---|
| T4 child audit (1061-file scan + 3 sub-loops + 3 cycles of joint SIGN folds) | New | `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md` (~1022 lines, status ratified) |
| T4 scanner tool | New | `tools/audit_2804_handoff_citation_integrity.py` (~550 lines) |
| Ratification envelope | New | `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md` |
| Arc registration | Modified | `docs/research/OPEN_ARCS.md` (Group 2800 row updated: 6/6 shipped) |
| S2838 handoff | New | THIS file |
| S2839 pointer | Updated | `00-START-NEXT-SESSION.md` — recommended default = T5 reports+audits triage audit |
| CLAUDE.md session-history banner | Updated | trimmed per `feedback_claude_md_bloat_at_session_open` |
| Twin workspace mirror | New (via Rigby) | Donkey Betz workspace `b4503364-2573-4401-9e28-61a739e0ce50` |

## 9. Twin-pointer card at S2838 close

📁 **Repo — S2838 artifacts:**

- **T4 audit doc (RATIFIED):** `docs/research/domains/docs_content_audit/2804_docs_content_handoff_audit.md`
- **Ratification envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md`
- **Handoff:** THIS file
- **Scanner tool:** `tools/audit_2804_handoff_citation_integrity.py`
- **Scanner output:** `/tmp/t4_handoff_audit_out.json`
- **Arc registration:** `docs/research/OPEN_ARCS.md` (Group 2800 row updated, 6/6 shipped)
- **Rigby SIGN conversation:** `pa-683fb793ab944cd0` (3 cycles preserved)
- **Merge SHA:** filled at close-cascade PR merge

🖥️ **Workspace UI — S2838 twin-pointer workspace deliverables:**

- **Content mirror + Ratification envelope:** Rigby creates in
  Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
  via PA `deliverable_tool.create` per
  `feedback_rigby_writes_workspace_deliverables` (fourth exercise);
  category `governance`; `deliverable_type=ratification_record`.

## 10. Group 2800 arc state at end-of-T4

**Group 2800 /docs/ content audit arc: 6 of 6 shipped.** T5 opens
at S2839. 2899 canonical summary follows T5 close.

- ✅ Parent (S2833) — D1-D9 locked
- ✅ T1 anchor & canonical-doc content audit (S2834) — RATIFIED
- ✅ T2 reference-graph audit (S2835) — RATIFIED
- ✅ T3a duplicate-content audit (S2836) — RATIFIED
- ✅ T3b orphan-and-reachability audit (S2837) — RATIFIED
- ✅ T4 handoff citation-integrity + retrieval-harm audit (S2838) — RATIFIED
- ⏳ T5 reports+audits triage (S2839 next)
- ⏳ 2899 canonical summary (post-T5)

**2899 Chris workshop queue: 99 rows** across 5 classes:
- 6 P1 T4 path-form broken citations
- 13 P2 T4 retrieval-harm banner candidates
- 3 P2 T4 fragment-form broken citations
- 75 T3b unclassified P2 + 1 T3b P1 README.md
- 2 T3a needs-judgment (SYSTEM_ARCH_MAP + CLAUDE_CONTEXT_SYSTEM_PACK)

T5 will add more.

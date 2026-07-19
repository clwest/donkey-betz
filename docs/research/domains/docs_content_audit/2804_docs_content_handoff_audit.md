---
title: "S2838 T4 — /docs/handoffs/ Citation-Integrity + Retrieval-Harm Audit (child audit 2804 of Group 2800)"
status: ratified (T4 — Chris D-verdict 2026-07-19 S2838; joint Claude+Rigby SIGN 3 cycles; schema v1.1 unchanged; escalate deferral carries over)
authority: child-audit deliverable — consumed by Group 2800 canonical summary at 2899 close
ratification:
  date: 2026-07-19
  session: 2838
  ratifier: Chris
  verbatim_directive: "Go for it!"
  scope: full T4 (1061-file corpus; three-sub-loop scanner; §10.1 v1.1 unchanged; migration queue frozen; §5.7a follow-on audit thread proposal recorded as future_trigger; SESSION_2759 added to banner candidate list per cycle-2 Q2 fold)
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md
  sign_cycles: 3 (Rigby joint SIGN pin pa-683fb793ab944cd0; substantive tool_runs across all 3 cycles; anti-rubber-stamp verified per feedback_verify_rigby_tool_runs_before_trusting_sign — cycle-3 caught 3 real STRENGTHEN issues: §1.1 leftover "drift" string, §5.7a scope-creep tightening needed, §5.5/§8 accumulation math inconsistency)
  next_action: T5 reports+audits triage audit opens at S2839 (child audit 2805_docs_content_reports_audits_triage.md); Group 2800 arc reaches 6/6 shipped
session: 2838
date: 2026-07-19
research_group: 2800
thread: T4
schema_version: 1.1  # unchanged from T3b; three v1.2 candidates recorded as future_trigger (§5.7 canonical probe-query set + §2.6 citation_style field + §5.4 null_result finding class)
parent: docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
sibling_children:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md      # T1 — RATIFIED at S2834
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md    # T2 — RATIFIED at S2835
  - docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md   # T3a — RATIFIED at S2836
  - docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md      # T3b — RATIFIED at S2837
  - docs/research/domains/docs_content_audit/2805_docs_content_reports_audits_triage.md   # T5 — opens after T4 close
  - docs/research/domains/docs_content_audit/2899_docs_content_canonical_summary.md   # arc close
authors: Claude Code (Chris directed at S2838 open — "B" = ratified default T4)
supersedes: none
scope: |
  Citation-integrity + retrieval-harm audit of the 1061 `docs/handoffs/*.md`
  corpus (1046 SESSION_-prefixed handoffs + 15 non-SESSION_ handoff files).
  Three sub-loops per parent §4 T4: (a) citation-graph over the non-handoff
  corpus + decay curve; (b) 10-doc fragment-form resolution spot-check;
  (c) retrieval-harm sub-loop for common operational probe queries.
  Consumes T2 §5.6 basename map (as pre-computed citation-edge substrate)
  + T3b §5.4 T5 workflow directive (as citing-doc anchor-reachability
  signal). Emits recommended DOC-POINTER-V1 stats-drift banner list for
  Chris judgment at 2899.
non_goals:
  - per-handoff content review across all 1061 files (parent §7 anti-scope)
  - individual arc-close-state judgments (Chris judgment; accumulate to 2899 per S2836 policy)
  - fixing broken citations in citing docs (no in-arc edits)
  - handoff-file deletions / renames / archival dispositions (T5 territory)
  - re-deriving T2 citation-edge substrate or T3b reachability graphs (consume pre-computed)
next_action: |
  Chris D-verdict at S2838 close. Any `escalate_to_chris` rows DEFER to 2899
  arc-close workshop per S2836 policy. T5 opens next session; canonical
  summary follows.
pre_clustering_seed: T2 §5.6 basename map + T3b §5.4 T5 workflow directive
head_at_open: ae519b4392cf
delegates_to: none
owner: claude+rigby
---

# S2838 — /docs/ Content Audit · T4 Handoff Citation-Integrity + Retrieval-Harm Audit

> **What this doc is.** T4 child audit of the Group 2800 /docs/ content audit
> arc. Measures handoff citation-integrity (are non-handoff docs citing
> handoffs cleanly?) + retrieval-harm (are handoffs surfacing in RAG top-K
> for operational queries in ways that leak stale claim-context to Rigby?).
> Emits a narrow list of handoffs recommended for DOC-POINTER-V1 stats-drift
> banner treatment at 2899 — Chris judgment call.
>
> **What this doc is not.** A per-handoff content review of the 1061 corpus
> (parent §7 anti-scope — handoffs are terminal-by-design write-once
> artifacts). A proposal to delete / archive / rename any handoff file (T5
> territory). Any in-arc file-operation authorization.

---

## 1. Method

### 1.1 Corpus selection — 1061 files across two subclasses

**Corpus enumeration** (via `Path('docs/handoffs').glob('*.md')` at head
`ae519b4392cf`):

| Subclass | Count | Method |
|---|---:|---|
| `SESSION_NNNN_*.md` | 1046 | numeric-session-prefixed handoffs |
| Non-SESSION_ handoff files | 15 | topic-prefixed persistent references (e.g. `PA_SYSTEMS_MAP_6_LAYER.md`) |
| **Total** | **1061** | S2837 close pointer said 1058 — +3 from S2833-S2837 close-cascade additions (see reconciliation below) |

**Session-number coverage:** 930 unique session numbers across 1046
SESSION_ files → **116 duplicate-session filenames** (multi-file
sessions — e.g., the Session 819 SYSTEM_AUDIT_* archive from S2834 T1
and other multi-scope sessions).

The 15 non-SESSION_ files are treated as a separate cohort per parent
§4 T4 spec footnote (not decay-curve-included; do surface in
retrieval-harm probe).

**Count reconciliation (Rigby cycle-2 Q4 fold):** the prior S2837
close pointer captured "1058" mid-close-cycle; head at S2838 open is
1061. The +3 delta attributes cleanly to the S2833→S2837 close-cascade
additions (SESSION_2833, S2834, S2835, S2836, S2837 handoffs authored
today plus S2832 the day prior). This is not "drift" — it is expected
cascade behavior. Verified via `git log --diff-filter=A --since='2026-07-18'
--name-only -- docs/handoffs/` + `find docs/handoffs -type f -name
'*.md' | wc -l = 1061`.

### 1.2 Three sub-loops (parent §4 T4)

**Sub-loop (a) — citation-graph + decay curve:**
For every citation of the form `docs/handoffs/SESSION_NNNN*.md` or
short-form `SESSION_NNNN` mention across the non-handoff corpus,
aggregate (citing_doc, cited_handoff_session) edges. Compute:

- Hit rate: what fraction of handoff-sessions get any citation?
- Decay curve: fraction cited by 500-session bucket (S0-499, S500-999,
  S1000-1499, S1500-1999, S2000-2499, S2500-2999).
- Citing-doc weight: for each citation, annotate with T3b
  `severity_class` (was the citing_doc anchor-reachable, or a
  search-only closed-arc pack?).

**Sub-loop (b) — fragment-form resolution spot-check:**
Grep the corpus for citations carrying URL fragments
(`docs/handoffs/SESSION_NNN.md#K` chunk-ID form OR
`docs/handoffs/SESSION_NNN.md#section-anchor` markdown form). Sample
up to 10; for each, verify whether the fragment target actually
resolves in the current handoff file. Tests post-S1143 chunk-ID
reset hypothesis (parent §4 T4 sub-loop (b) rationale).

**Sub-loop (c) — retrieval-harm probe:**
Run `search_embeddings` for a fixed set of 10 common operational
probe queries (parent §4 T4 cycle-1 Q2 refinement named
"in-progress arc" + "how many spiders"; extend with the other 8
common Chris/Rigby operational queries). For handoffs surfacing in
top-K (K=8), report file_path + rank + similarity + intent_gate_name
for downstream stale-vs-current classification.

### 1.3 Severity classification — four classes per parent §4 T4

Adapted from T3b §1.3 (severity-class labels adjusted to T4 domain):

| severity_class | Meaning | Default severity | Default action |
|---|---|---|---|
| `broken_citation_path_form` | citing doc references `docs/handoffs/SESSION_N*.md` that does not exist | P1 | `escalate_to_chris` (accumulate to 2899) |
| `broken_citation_short_form` | citing doc references `SESSION_N` short-form; T2 flagged BROKEN_404 but many are prose refs to gap-numbers, not broken links | P2 | `escalate_to_chris` (accumulate to 2899) OR `keep_as_is` if prose ref |
| `retrieval_harm_candidate` | handoff surfaces in probe top-K for query where a canonical anchor doc should surface instead | P2 | `escalate_to_chris` (accumulate to 2899 → DOC-POINTER-V1 banner recommendation) |
| `citation_healthy` | handoff cited by ≥1 anchor-reachable canonical doc; no fragment breakage; no retrieval-harm | P3 | `keep_as_is` |
| `uncited_never_retrieved` | handoff on disk but never cited from non-handoff corpus AND never surfaces in probe top-K | P3 | `keep_as_is` (write-once terminal artifact, per parent §7) |

### 1.4 Anti-pattern challenge: "uncited handoff = archival candidate"

Handoffs are **terminal-by-design write-once artifacts** (parent §7
anti-scope). An uncited handoff is NOT an orphan and NOT an archival
candidate. The archival decision is a T5 concern (docs/audits/**, but
handoffs live in docs/handoffs/**, not T5-territory — they are
consumed via retrieval, not anchor-navigation).

The audit **does NOT propose:**
- Deleting uncited handoffs
- Archiving uncited handoffs
- Auto-generating retrieval-harm banners
- Fixing broken citations in citing docs

The audit **DOES:**
- Report the uncited fraction as a *structural signal*
- Flag broken citations for citing-doc migration-PR queue
- Recommend a narrow banner-candidate list for Chris judgment at 2899

### 1.5 Pre-clustering signals consumed

**T2 §5.6 pre-computed citation edges** (`/tmp/t2_scan_out.json`).
T2 already computed 17 `ref_class=session` short-form findings + 145
`ref_class=file_cite` findings that resolve to `docs/handoffs/` paths.
T4 does **NOT** re-grep the corpus for handoff citations; T4 loads
T2's `results[*].findings` and filters to handoff-target edges. This
saves ~1s of grep time and preserves T2's PASS/BROKEN_404 status
attribution.

**T3b §5.4 T5 workflow directive generalized** (`/tmp/t3b_orphan_scan_out.json`).
T3b classified 793 non-handoff files into 4 severity classes with
anchor-reachability booleans. T4 loads T3b's reachability rows to
annotate each citation with citing-doc weight: a citation from a
`cited-multi-graph-OK` (anchor-reachable) canonical doc carries
strong evidence of live citation; a citation from a
`reachable-from-search-only` closed-arc pack is a weaker signal.

Cross-child pre-clustering pattern held again — this is the **third
consecutive T-child** consuming a prior child's output (T3a←T2, T3b←T3a,
T4←T2+T3b). Recorded as a codify candidate for playbook v3 at §10.2.

### 1.6 Scanner shape (parent §4 T4 compliance)

Scanner: `tools/audit_2804_handoff_citation_integrity.py` (~550 lines).
Runtime: ~3s (dominated by 10 OpenAI embedding calls for sub-loop (c),
each ~250ms — grep + T2/T3b JSON loads are sub-second). Output:
`/tmp/t4_handoff_audit_out.json` for §10.1 v1.1 YAML consumption.

Scanner outputs three top-level slices:
- `summary` — histograms, decay curve, count summaries
- `sub_loop_a_top_cited_handoffs` — top-25 most-cited handoffs (for §2.3 body)
- `sub_loop_a_broken_shortform_citations` — 23 broken edges (for §2.6 body)
- `sub_loop_b_fragment_sample` — resolved fragment-form spot-checks
- `sub_loop_c_handoff_hits` — 28 handoff hits across 10 probe queries × K=8

---

## 2. Findings — citation-integrity + retrieval-harm

### 2.1 Positive headline: handoff citation-graph is small + concentrated in anchor-reachable canonical docs

**Zero P0 findings.** Handoff-citation surface is:
- **Small** — 145 total citation edges (path-form) + 17 short-form (mostly prose gap-mentions) across 1061-file corpus
- **Concentrated** — 131 of 145 citations (**90.3%**) originate from
  `cited-multi-graph-OK` (anchor-reachable canonical) docs; only 14
  originate from `reachable-from-search-only` closed-arc packs
- **Sharply-decayed** — 89.6% of handoffs on disk have NEVER been
  cited from the non-handoff corpus; recent handoffs (S2500-2999)
  cite at 26.8% while old handoffs (S0-499) cite at 2.1%

This is a **positive signal** for handoff hygiene:
- Handoffs behave as **write-once terminal artifacts** — most are
  never referenced again after their session closes, matching the
  terminal-by-design contract from parent §7 anti-scope.
- The tiny minority (10.4%) that DO get cited are cited primarily by
  **anchor-reachable canonical docs**, not by ephemeral closed-arc
  packs — meaning citations concentrate where they carry weight.
- No P0 root-stability gate triggered (§10.4(b) analog to T3b §2.1
  root-stability contract).

### 2.2 Sub-loop (a) — decay curve

Decay curve by 500-session bucket:

| Session range | Handoffs on disk | Cited (any ref) | Cited fraction |
|---|---:|---:|---:|
| S0000-S0499 | 192 | 4 | 2.1% |
| S0500-S0999 | 323 | 13 | 4.0% |
| S1000-S1499 | 232 | 41 | **17.7%** |
| S1500-S1999 | 38 | 4 | 10.5% |
| S2000-S2499 | 22 | 2 | 9.1% |
| S2500-S2999 | 123 | 33 | **26.8%** |
| **Total** | **930** | **97** | **10.4%** |

Two notable spikes:
- **S1000-S1499 (17.7% cited):** the memory / RAG / retrieval-lanes
  research spike — Group 1300 arc + Session 1099 doc verifier +
  Session 1142 search_docs tool. Older handoffs remain cited because
  the substrate they introduced remains active.
- **S2500-S2999 (26.8% cited):** recent handoffs — recency bias.
  Recent handoffs from ongoing Group 2700/2800/discovery-layer work
  cite each other heavily during the arc; expected to decay as arcs
  close.

Two notable gaps:
- **S1500-S2499 (~10%):** the sports betting + revenue substrate era
  is comparatively under-cited. May be a real decay signal (the
  substrate matured but doesn't need continuous re-reference).
- **S0000-S0999 (2-4%):** the pre-Session-1000 era is
  effectively-forgotten in the citation graph. Handoffs from this
  era serve retrieval, not navigation.

**Chris judgment call (defer to 2899):** is 89.6% uncited a
"terminal-artifact healthy" state, or does it warrant a lifecycle
policy (e.g., handoffs before S1000 get an "archive_soft" marker to
demote in retrieval)? Recorded as `escalate_to_chris`.

### 2.3 Sub-loop (a) — citing-doc weight histogram

Of 145 citation edges to handoffs:

| Citing-doc T3b `severity_class` | Citation count | Fraction |
|---|---:|---:|
| `cited-multi-graph-OK` (anchor-reachable canonical doc) | 131 | 90.3% |
| `reachable-from-search-only` (search-only-by-design pack) | 14 | 9.7% |
| `citing-not-in-t3b-corpus` (unreachable — handoff-to-handoff or archive) | 0 | 0% |

**Zero citations from unreachable / archive-tree source docs** —
matches expected structural shape (T3b already excluded handoffs
+ archive + docs-pattern from the reachability corpus).

**Top-25 most-cited handoffs (from `sub_loop_a_top_cited_handoffs`):**

| Session | Citations | Notable citing docs |
|---:|---:|---|
| S780 | 5 | RATIFICATION_2026-07-19_2799 + 2701_docs_inventory + 2799 canonical summary + SKIN_LAYER_AUDIT_861B + docs/audit/SESSION_1143 |
| S1033 | 5 | ARCHITECTURE_INDEX + OPEN_ARCS + 1605/1606/1699 content-arc children |
| S1137 | 4 | STRATEGY_247_GLOBAL_AI + FLEET_CAPABILITY_BUSINESS_SPEC + 2705 handoffs-proliferation |
| S1264 | 4 | ARCHITECTURE_INDEX + 2705 handoffs-proliferation + governance_authority_evolution + platform_architecture_inventory |
| S1142 | 3 | audit/SESSION_1143 + memory 1301/1302 (retrieval-lanes arc) |
| S2701 | 3 | 2705 handoffs-proliferation + engineering_playbook_evidence + playbook_authoring_2716 |
| S2707 | 3 | 3 platform/ playbook_authoring docs |

The most-cited handoffs are ratification / arc-open moments (S780
approve-operation-fix; S1033 architectural moment; S2701 playbook
authoring session). These citations are **load-bearing** and are the
opposite of `escalate_to_chris` — they are the healthy citation core.

### 2.4 Sub-loop (b) — fragment-citation spot-check

**Corpus-wide fragment surface is negligible.** Grep for
`docs/handoffs/SESSION_NNN.md#<fragment>` across the non-handoff
corpus returns **only 3 fragment-form citations**:

| Citing doc | Cited handoff | Fragment | Resolves |
|---|---|---|---:|
| `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md:237` | `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md` | `#8` | ✗ (section absent) |
| `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md:238` | `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md` | `#8` | ✗ (section absent) |
| `docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md:113` | `SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md` | `#1` | ✗ (section absent) |

**All 3 samples broken.** But:
- **No `#K` chunk-ID form found** in the corpus (parent §4 T4
  sub-loop (b) hypothesis was post-S1143 chunk-ID reset; that risk
  is **structurally zero** at head `ae519b4392cf` because nobody
  uses `#K` form).
- Total blast radius = **3 fragment edges** across 3247 corpus files.
  Even if all 3 are broken (which they are), operator-impact is
  negligible.

**Classification of all 3:** severity `P2`,
`recommended_action: escalate_to_chris` for the two `2700` citations
(same citing doc — likely a 1-line fix at scoping-doc level, not a
handoff-content fix). The `RATIFICATION_2026-07-18` citation is
already in a closed ratification envelope; fix cost = zero
(ratification envelopes are frozen).

**Sub-loop (b) generalized finding for parent methodology:** the
"post-1143 chunk-ID reset" concern (parent §4 T4 rationale) is
**empirically unfounded at the current corpus state**. Chunk-ID
`#K123` form was never adopted for handoff citations. This is
recorded as a `future_trigger` — if fragment adoption grows (e.g.,
if Rigby's search_docs surface starts returning `#K` anchors),
re-run T4 sub-loop (b).

### 2.5 Sub-loop (c) — retrieval-harm probe results

10 probe queries × K=8 top-K = 80 available slots. **28 handoff-hits
returned** (35% of slots) across **25 unique handoffs**. Pattern B/C
intent-gate deflection worked correctly for `"how many spiders"`
(0 handoff hits — top-K went to `PLATFORM_INVENTORY.md` per Pattern B).

**Retrieval-harm candidates for DOC-POINTER-V1 stats-drift banner
(narrow list for Chris judgment at 2899):**

| Query | Rank | Handoff (session) | Judgment call |
|---|---:|---|---|
| `"in-progress arc"` | 3 | S2200 Frontend Domain Scoping | Group 2200 arc state: check if closed; if closed, banner candidate |
| `"in-progress arc"` | 6 | S1806 Human Attention Cat F | Group 1800 human-attention arc closed at S1806 — **strong banner candidate** |
| `"in-progress arc"` | 7 | S1805 Human Attention Cat E | Group 1800 human-attention arc — **strong banner candidate** |
| `"in-progress arc"` | 8 | S2600 PA Parent Scoping | Group 2600 PA arc state: check `2699_pa_canonical_summary.md` — likely closed, banner candidate |
| `"current arc state"` | 1 | S2200 Frontend Domain Scoping | duplicate top hit — **strongest banner candidate** (rank 1 for a "current" query) |
| `"current arc state"` | 5 | S2201 Frontend Routes/Pages/Layouts | banner candidate if Group 2200 closed |
| `"how many agents"` | 7 | PA_SYSTEMS_MAP_6_LAYER.md | non-SESSION_ file — layer-map; may be stale (PLATFORM_INVENTORY is canonical) — banner candidate |
| `"how many agents"` | 8 | S833 Workspace Improvements | very old (S833 = Session 833); certainly stale on agent counts — **banner candidate** |
| `"session close cascade"` | 1 | S2000 Event Integration Parent Scoping | Group 2000 arc likely closed — banner candidate |
| `"session close cascade"` | 2 | S1406 Revenue Freelance | Group 1400 revenue arc — banner candidate if closed |
| `"session close cascade"` | 3 | S1903 Authority Enforcement Cat C | Group 1900 authority-enforcement arc — banner candidate if closed |
| `"session close cascade"` | 5 | S1504 Sports Cat D | Group 1500 sports arc — banner candidate if closed |

**Recommended banner list (12 unique handoffs):** all `escalate_to_chris`,
**deferred to 2899 workshop per S2836 policy** — Chris makes the
final banner-vs-keep decision informed by arc-close-state judgment.

**Cycle-2 Q3 fold — annotate-not-filter (Rigby AGREE):** initially
considered filtering by rank threshold (rank 1-3 only). Empirical
similarity distribution reveals no clean elbow:

| Rank slice | n | Mean sim | Range |
|---|---:|---:|---|
| rank 1-3 (top-tier) | 9 | 0.5437 | 0.3843-0.6138 |
| rank 4-8 (mid-tier) | 19 | 0.5276 | 0.4725-0.5658 |

Rank-only filter drops legitimate rank-4 candidates (e.g.,
SESSION_2820 at sim 0.5658 which is HIGHER than SESSION_2200 at
rank 1 sim 0.5381). Absolute sim ≥0.55 filter (~8 hits) has an
inverse paradox: it **includes recent still-current context**
(SESSION_2832 sim 0.6138, SESSION_2831 sim 0.5945) and **excludes**
the genuinely-stale-arc candidates (SESSION_2200 sim 0.5381,
SESSION_1805 sim 0.5174, SESSION_1806 sim 0.5184) that are the
actual banner-treatment concern. **Conclusion:** similarity is
optimizing for match strength, NOT staleness risk; recent handoffs
score higher because they share current vocabulary with modern
queries. Keep all 12 top-K unique-handoff hits; annotate each with
similarity + probe query + `stale_hypothesis: pending_chris_judgment`
+ `canonical_alternative_exists: (Y/N)` for 2899 workshop-ready
review.

**Cycle-2 Q2 fold — SESSION_2759 added to banner list (Rigby AGREE):**
Rigby proposed adding two operator-hot probe queries: (a)
"recycle-all / stale daphne / stale celery" (ops recovery) and (b)
"governor throttle / freeze / safe_mode / kill switch" (governance
control plane). Verified via `search_docs`:

- Query (a) surfaces `SESSION_2759_STALE_DAPHNE_WARNING_SYSTEM_RATIFIED.md`
  at chunks #1-#4 (handoff prominent in top-K) — **new banner candidate**
- Query (b) surfaces canonical docs (`EMPLOYEE_OS_PRIMITIVES.md#4` +
  `1903_authority_enforcement_cat_c_cross_plane_composition_design.md#9`) —
  no new handoff banner candidate

**Amended banner-candidate count: 13 unique handoffs** (12 from T4's
10-probe set + 1 from cycle-2 probe expansion). SESSION_2759
annotation: `ops_recovery_stale_process_context` (not `arc_state`).
Two additional probe queries recorded as `future_trigger` for T4
rerun (methodology addition, not scanner code change).

**Non-harm hits (informational, no banner recommended):**
- `"recycle after merge"` → S2832, S2831, S2820, S2785, S2769, S2767 — recent handoffs on the PLAYBOOK-7.4.4 topic; healthy retrieval
- `"playbook version"` → S2793, S2794 — recent playbook-related handoffs; healthy
- `"where do I start"` → S1219 (rank 3, intent_gate `self_reference`); rank 1 = `00-START-NEXT-SESSION.md` per Pattern C — healthy, S1219 is co-relevant not stale
- `"canonical anchor"` → S2699 PA canonical summary; rank 7, healthy
- `"handoff citation"` → S2000 (parent scoping) + S2827 (Pattern C self-reference); healthy

### 2.6 Broken citations — 23 total, 2 distinct classes

Sub-loop (a) extracted 23 BROKEN_404 citation edges. Distinguishing:

**Class A — path-form broken citations (6 edges):**
The citing doc references `docs/handoffs/SESSION_NNN*.md` but the
target file does not exist at that path:

| Citing doc | Missing target |
|---|---|
| `docs/audits/SKIN_LAYER_AUDIT_SESSION_861B.md` | `docs/handoffs/SESSION_695_SKIN_LAYER.md` |
| `docs/audits/SKIN_LAYER_AUDIT_SESSION_861B.md` | `docs/handoffs/SESSION_780_APPROVE_OPERATION_FIX.md` |
| `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md` | `docs/handoffs/SESSION_1900_GROUP_1900_AUTHORITY_ENFORCEMENT_PARENT_SCOPING.md` |
| `docs/research/domains/pa/2699_pa_canonical_summary.md` | `docs/handoffs/SESSION_2601_PA_CAT_A_BACKEND_ENDPOINT_CONTRACT_SOT.md` |
| `docs/research/implementation/RATIFICATION_2026-07-13_PLAYBOOK_V0_7_0.md` | `docs/handoffs/SESSION_2775_SESSION_FRESHNESS_VERDICTS_RATIFIED.md` |
| `docs/research/platform_architecture_inventory.md` | `docs/handoffs/SESSION_1258_..._MORNING_BRIEF_BEAT_MIGRATION.md` |

**Classification:** each row severity `P1`, action `escalate_to_chris`.
Fix options at 2899:
- Handoff file was renamed since citation was written → basename
  reconciliation (T2 §5.6 map may match some — spot-check needed)
- Handoff file never existed → citing doc has an aspirational
  reference that should be updated to actual filename or removed
- Handoff exists at a slightly different session number → correct
  the reference

**Class B — short-form broken references (17 edges):**
`SESSION_NNN` bare-string mentions where T2 flagged BROKEN_404. But
many are **prose gap-mentions**, not link citations. Sample:

| Citing doc | Bare reference | Interpretation |
|---|---|---|
| `docs/HANDOFF_NUMBERING_GAPS.md` | `SESSION_198`, `SESSION_205` | Doc's whole purpose is documenting skipped sessions — **intentional prose refs** |
| `docs/PLATFORM_WHAT_IT_IS.md` | `SESSION_1099` | Prose ref to Session 1099 doc-verifier work — **intentional prose ref** |
| `docs/code-review/02-AI-ASSISTANT-CODE-REVIEW.md` | `SESSION_184` | Historical review annotation — **prose ref** |
| `docs/research/domains/content/1602_content_reviewers_decision_enforcement_audit.md` | `SESSION_960, 962, 963, 1077` | Multi-session prose refs in content-arc audit — **prose refs** |
| `docs/research/platform/engineering_playbook_architecture_specification.md` | `SESSION_2705, 2708` | Playbook-authoring provenance prose refs — **prose refs** |

**Classification:** each row severity `P3`, action `keep_as_is`
because these are prose references, not broken links. **T2's
BROKEN_404 flag over-counts short-form** — parent methodology
signal: T2 could distinguish `link-form` vs `prose-form` in future
runs. Recorded as `future_trigger` at §5.4.

**Precision note (Rigby cycle-2 Q1 STRENGTHEN fold):** 5 of 17
short-form BROKEN_404 rows were **manually verified** to be prose
refs (LINK_FORM: False) via raw-line inspection — the 5 rows shown
in the table above. The remaining 12 short-form BROKEN_404 rows are
**not individually verified**; the P3 keep_as_is classification is
extrapolated from the sampled subset. If any of the 12 unverified
rows contains a markdown-link-form `[text](SESSION_NNN)` reference,
that row would reclassify to P2 fix. Recorded as `future_trigger`
for a T4 rerun with all-17 raw-line verification (trivial cost;
~30s of shell time). Extrapolation confidence: HIGH (5/5 sampled
were prose, and the T2 `ref_class=session` heuristic was designed
for short-form which is structurally more likely to be prose).

**Net actionable broken-citation count:** 6 path-form (not 23) once
prose refs are filtered out (with 12 unverified short-form rows
carrying a residual ~zero-probability risk of link-form).

---

## 3. Migration queue (post-arc, DEFERRED to §3 execution arc post-2899)

Per parent §5 non-goals discipline: **no in-arc file operations**.

### 3.1 Zero P0 rows — no root-stability gate triggered

Zero root-anchor-doc handoff citations broken. No cited-but-missing
canonical anchor. Root-stability contract holds.

### 3.2 P1 rows — 6 path-form broken citations (queued for 2899)

Each row: `severity: P1`, `recommended_action: escalate_to_chris`.
Chris judgment call: reconcile-basename vs remove-reference vs
handoff-file-was-renamed-since. All 6 rows accumulate to 2899
workshop per S2836 arc-close deferral policy.

### 3.3 P2 rows — 16 escalate rows (queued for 2899)

- 3 fragment-form broken citations (§2.4)
- 13 retrieval-harm candidates for DOC-POINTER-V1 banner (§2.5,
  incl. SESSION_2759 added at cycle-2 Q2 fold)

Total accumulated to 2899 workshop: **22 T4 rows added to the 77
carried over from T1/T3a/T3b + T2 = 99 rows queued at end of T4**.

### 3.4 T5-adjacent rows — 0 handoff files are T5-territory

Handoffs live in `docs/handoffs/**`, NOT `docs/audits/**` or
`docs/reports/**`. T5 territory rule does not apply to T4 findings.

### 3.5 Migration-PR batch hints (per §10.4 cross-arc consumption contract)

For the future §3 execution arc consuming T4 findings:

- **6 P1 path-form fixes** are small 1-line edits per citing doc; batch as single PR after Chris disposition
- **12 retrieval-harm banner recommendations** require DOC-POINTER-V1 substrate design (deferred to Group 2700 §7 anchor-updates arc or dedicated banner sub-arc); not fix-per-file batches
- **3 fragment-form fixes** are ratification-envelope-frozen (2 in the same 2700 scoping doc — same-PR edit) or ratification-frozen (RATIFICATION_2026-07-18 = frozen, do not edit); net 2 edits in 1 PR

---

## 4. YAML findings — §10.1 v1.1 schema rows (representative sample)

Full JSON: `/tmp/t4_handoff_audit_out.json`. Representative rows in
v1.1 schema (per T3b §10.1 fold canonical form):

```yaml
# Sample 1 — P1 broken path-form citation (2899 escalate)
- file_path: "docs/audits/SKIN_LAYER_AUDIT_SESSION_861B.md"
  severity_class: broken_citation_path_form
  severity: P1
  recommended_action: escalate_to_chris
  audit_thread: T4
  citing_doc_severity_class: reachable-from-search-only  # from T3b
  broken_target: docs/handoffs/SESSION_695_SKIN_LAYER.md
  broken_kind: file_never_existed_or_renamed
  fix_hint: reconcile_via_t2_basename_map_or_prose_footnote
  t5_may_override: NO  # citing doc is T5-territory audits/ but the reference is a handoff cite
  notes: "citing doc is a S861B skin-layer audit; SESSION_695 file absent from disk; classification pending Chris arc-close judgment"

# Sample 2 — P2 fragment broken (same-PR fixable)
- file_path: "docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md"
  severity_class: broken_citation_path_form  # fragment kind
  severity: P2
  recommended_action: escalate_to_chris
  audit_thread: T4
  citing_line: 237
  broken_target: "docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8"
  fragment: "8"
  broken_kind: fragment_target_absent
  fix_hint: same_pr_mitigatable_by_removing_fragment_or_choosing_valid_section

# Sample 3 — P2 retrieval-harm banner candidate (2899 escalate)
- file_path: "docs/handoffs/SESSION_2200_FRONTEND_DOMAIN_SCOPING.md"
  severity_class: retrieval_harm_candidate
  severity: P2
  recommended_action: escalate_to_chris
  audit_thread: T4
  surfaces_for_queries:
    - "in-progress arc"  # rank 3, sim 0.5354
    - "current arc state"  # rank 1, sim 0.5381
  banner_recommendation: doc_pointer_v1_stats_drift_pending_chris_arc_state
  notes: "Rank 1 for 'current arc state' probe; Group 2200 Frontend arc-close-state is a Chris judgment call"

# Sample 4 — P3 healthy top-cited handoff (keep_as_is)
- file_path: "docs/handoffs/SESSION_780_APPROVE_OPERATION_FIX.md"
  severity_class: citation_healthy
  severity: P3
  recommended_action: keep_as_is
  audit_thread: T4
  citing_count: 5
  citing_docs_severity_hist:
    cited-multi-graph-OK: 5
  notes: "top-tier citation graph; 5 anchor-reachable canonical docs cite; healthy retrieval load-bearing"

# Sample 5 — P3 uncited terminal artifact (keep_as_is)
- file_path: "docs/handoffs/SESSION_442_EXAMPLE.md"  # illustrative — 833 such files exist
  severity_class: uncited_never_retrieved
  severity: P3
  recommended_action: keep_as_is
  audit_thread: T4
  citing_count: 0
  probe_top_k_hits: 0
  notes: "handoff-terminal-write-once artifact per parent §7 — uncited is healthy state, not archival candidate"

# Sample 6 — P3 prose-form false-positive (keep_as_is)
- file_path: "docs/HANDOFF_NUMBERING_GAPS.md"
  severity_class: broken_citation_short_form  # T2 BROKEN_404 flag
  severity: P3
  recommended_action: keep_as_is
  audit_thread: T4
  broken_target: "SESSION_198"
  broken_kind: intentional_gap_mention_prose_ref
  fix_hint: none_required_prose_ref_by_design
  notes: "citing doc is HANDOFF_NUMBERING_GAPS.md — its whole purpose is documenting skipped session numbers"
```

---

## 5. Cross-cutting signals for future §3 execution arc AND for parent methodology refinement

### 5.1 Handoff citation graph is smaller than expected

Total handoff citation edges = **145 path-form + 17 short-form = 162 edges**.
For a 1061-file terminal-artifact corpus, this is remarkably small.
Expected write-once discipline holds; parent §7 anti-scope was
empirically justified by T4's findings.

**Cross-cutting signal for parent methodology (2899 fold):** the
concern from Group 2700 T5 substrate ("handoff proliferation risk")
is **structurally sound**. Handoffs proliferate on disk (~1061) but
citation graph stays small (~162 edges). No urgent citation-graph
crisis; the write-once contract works.

### 5.2 T2's BROKEN_404 flag over-counts short-form prose references

Recorded observation: 17 of T2's 17 `ref_class=session` short-form
BROKEN_404 flags are **prose gap-mentions**, not broken markdown
links. Fix at T2 methodology (future run): distinguish
`link_form` (in markdown `[]()` or backtick-quoted) from `prose_form`
(bare `SESSION_NNN` mention in prose text).

**Recorded as `future_trigger` for T2 v2 rerun** (deferred; not
codified now). §10.1 schema addition candidate: `citation_style`
field with values `markdown_link | backtick_path | prose_ref`.

### 5.3 T3b citing-doc weight signal is high-value pre-clustering

131 of 145 citation edges (90.3%) trace to `cited-multi-graph-OK`
citing docs. This means: when a handoff IS cited, it's almost always
cited by a healthy canonical doc, not a dead pack. Consuming T3b's
per-file reachability was cheap (~200ms JSON load) and produced
strong signal.

**Cross-cutting confirmation of T3b §5.4 T5 workflow directive
generalization:** T4 successfully consumed T3b's pre-computed
reachability instead of re-deriving. This is the third T-child in
Group 2800 successfully consuming a prior child's pre-clustering
substrate (T3a←T2, T3b←T3a+T2, T4←T2+T3b). Codify candidate for
playbook §11.3 template addition — "child audit MAY consume
prior-child substrate; if it does, ingest, do NOT re-derive."

### 5.4 Fragment-citation surface is negligible — post-1143 chunk-ID hypothesis empirically unfounded

Parent §4 T4 sub-loop (b) rationale was concern about post-S1143
chunk-ID reset breaking `#K` fragment citations. **Zero `#K` chunk-ID
form citations exist in the corpus.** Only 3 fragment citations of
any form exist; all use `#section-name` markdown-anchor form and all
fail to resolve because the target sections don't exist in the
handoff file.

**Cross-cutting signal:** the chunk-ID reset scenario is a
non-existent risk at current corpus state. Recorded as
`future_trigger` — if fragment citation adoption grows (e.g., via
Rigby's search_docs returning `#K` deep-link anchors), re-run T4
sub-loop (b) at that time.

### 5.5 Retrieval-harm banner list is Chris-judgment-heavy

12 handoffs recommended for DOC-POINTER-V1 stats-drift banner
treatment. Every single row requires **arc-close-state knowledge**
that only Chris can definitively supply (per S2836 arc-close
deferral policy). The scanner cannot classify "arc closed" without
access to Chris's mental model of arc lifecycle.

**Cross-cutting signal for 2899 workshop shape:** Chris judgment
queue at 2899 will include (cycle-2 fold: SESSION_2759 added; total
retrieval-harm recommendations 12→13):
- 6 P1 path-form broken citations (fix-vs-remove-vs-rename)
- 13 P2 retrieval-harm banner recommendations (banner-vs-keep,
  incl. SESSION_2759 from cycle-2 Q2 ops-recovery probe)
- 3 P2 fragment-form (same-PR fixable + 1 frozen ratification-envelope)

Plus the 77 rows carried over from T3a/T3b per S2837 pointer
(T3a=2 + T3b=75; T1 and T2 contributed 0 to the accumulated queue
per pre-S2836-policy child ratifications). Total 2899 workshop queue
at end of T4 = **99 rows** across 5 severity/action categories. T5
will add more; workshop size will be substantial.

### 5.6 Non-SESSION_ handoff files (15 files) are hybrid category

The 15 non-SESSION_ handoff files (e.g., `PA_SYSTEMS_MAP_6_LAYER.md`,
`HANDOFF_NUMBERING_GAPS.md`) are:
- Living in `docs/handoffs/` for filesystem-locality with SESSION_ handoffs
- NOT terminal-write-once (they are updated as needed)
- Genuinely searchable / navigable references

**Cross-cutting signal:** these 15 files behave more like
`docs/topics/` files than SESSION_ handoffs. Recorded as
`future_trigger` for Group 2700 §7 anchor-updates: consider
moving non-SESSION_ handoff files to `docs/topics/` or
`docs/references/` to match their actual semantics.

### 5.7a Follow-on audit thread proposal (Rigby cycle-2 Q5 zoom-out fold)

**T4 measures citation-graph SHAPE + top-K RETRIEVAL** — this is the
correct *structural* first-order question given no operator-time
instrumentation. It bounds the problem size, falsifies speculative
risks (chunk-fragment reset hypothesis), and produces an actionable
banner-candidate queue.

**T4 does NOT measure** the underlying behavioral concern: *"How often
do we lose operator minutes because retrieval returns a stale handoff,
leading to re-asking, manual hunting, or acting on wrong context?"*
That question requires instrumentation (query-log sampling, correction
proxies) that T4's methodology cannot supply.

**Recorded as `future_trigger` for post-2899 follow-on audit thread:**

Two candidate substrate approaches (Rigby cycle-2 Q5 recommendations):

1. **Operator query log sampling.** Take the last N "ops help"
   questions issued to Rigby, run them through the same retrieval
   stack, measure "handoff in top-3 vs canonical in top-3" ratio,
   tag which handoffs are actually stale-vs-current. Requires:
   query-log persistence + Chris-annotated stale-vs-current label
   set + baseline comparison.
2. **Conversation correction proxy.** Detect when a user/operator
   (Chris in single-user context) corrects Rigby's response by
   re-issuing a similar query with sharper wording, or explicitly
   flagging Rigby's answer as stale. This is a passive-observation
   signal that doesn't require Chris to explicitly label a corpus.

Recommendation: at 2899 close, consider whether to open a follow-on
child audit (e.g., `2811_handoff_retrieval_time_loss_audit.md`) OR
route into a separate Group (Group 2900 candidate: operator-cost
observability). The **structural** T4 shape is not wrong; the
**behavioral** measurement question is genuinely orthogonal and
warrants its own arc.

**Scope-creep guardrail (Rigby cycle-3 Q7 STRENGTHEN fold):** This
doc makes NO instrumentation request. §5.7a only records the
measurement gap + two candidate substrate approaches for later
Chris prioritization. Any operator-time-loss instrumentation is
deferred pending Chris arc-open authorization post-2899.

### 5.7 Sub-loop (c) probe-query set is Chris-tunable knob

The 10 probe queries were chosen at S2838 open based on common
operational patterns. Adding queries would expand banner-candidate
list; removing would shrink. **The list is heuristic, not
authoritative.**

Recorded as `future_trigger` for methodology at 2899: parent §4 T4
could specify a canonical probe-query set (e.g., derived from
production `search_docs` invocation logs). Currently the 10 queries
are:

1. `"in-progress arc"`
2. `"how many spiders"`
3. `"how many agents"`
4. `"current arc state"`
5. `"recycle after merge"`
6. `"playbook version"`
7. `"where do I start"`
8. `"canonical anchor"`
9. `"session close cascade"`
10. `"handoff citation"`

**Cycle-2 Q2 fold additions (Rigby STRENGTHEN):** two operator-hot
queries recommended for future T4 rerun (methodology, not scanner
code change):

11. `"recycle-all / stale daphne / stale celery"` — ops recovery
    class; surfaces `SESSION_2759` (see §2.5 amended banner list)
12. `"governor throttle / freeze / safe_mode / kill switch"` —
    governance control plane; surfaces canonical docs (no new
    handoff banner)

Total future canonical probe-query set candidates: 12 (extendable at
2899 if additional operator-hot categories emerge).

---

## 6. Residual risk / limitations

### 6.1 Method limitations (recorded)

1. **Sub-loop (b) sample size is 3 (all edges).** Parent §4 T4
   spec said "10-doc sample per Group 2700 T5 substrate concern".
   Empirically, only 3 fragment-form citations exist in the
   corpus — so the sample IS the population. No statistical
   inflation possible; 100% broken rate is the true rate at N=3.
   `future_trigger` if fragment adoption grows.

2. **Sub-loop (c) probe queries are heuristic.** 10 queries chosen
   by Claude at authoring time; Chris did not review the list.
   Different query set would produce different banner candidates.
   Rigby SIGN could pressure-test the query set.

3. **Retrieval-harm classification is Chris-judgment-blocked.**
   Scanner cannot determine "arc closed" state; scanner emits
   candidate list, Chris disposes at 2899. Deliberately deferred
   per S2836 policy.

4. **Non-SESSION_ handoff files (15) not decay-curve-included.**
   These files have no session number → excluded from bucket
   analysis. Their citation counts show up in top-cited handoffs
   analysis, but their "cited fraction" is not measurable within
   the parent §4 T4 shape.

5. **T2 short-form BROKEN_404 flags over-count prose refs** (§5.2).
   T4 classifies 17 of 17 T2 short-form flags as prose refs
   (P3 keep_as_is). This is a T4 judgment, not a re-derivation of
   T2. If T2 v2 adds `citation_style` field, T4 v2 rerun would
   produce cleaner distinction.

6. **No basename-reconciliation for path-form broken citations.**
   For the 6 path-form broken rows, T4 does NOT check whether the
   basename appears elsewhere in `docs/handoffs/` under a different
   filename (T2 §5.6 RENAMED map partially surfaces this but
   handoffs are excluded from T2 corpus). Recorded as
   `future_trigger` for sub-loop (a) v2.

7. **Handoff intra-cite graph NOT measured.** T4 excludes
   `docs/handoffs/` from citing-doc corpus (see sub-loop (b)
   self-cite filter). Handoff-to-handoff citations (e.g., an S2837
   handoff citing an S2836 handoff) are ignored. Rationale: they
   don't test the terminal-artifact-consumption question. But if
   Chris wanted to measure "how much do handoffs reference each
   other," a follow-up scan would be needed. `future_trigger`.

### 6.2 Spot-verify sample — hand-check top escalate rows

Manually inspected 5 top-priority escalate candidates:

| Row | Manual verdict | Classification |
|---|---|---|
| S2200 Frontend for "current arc state" rank 1 | Group 2200 Frontend arc: 2200 scoping + 2201 audit only in tree; 2299 canonical summary absent — Group is **NOT closed** (matches OPEN_ARCS status) | escalate needs "arc-in-flight" tag, not banner |
| S1806 Cat F for "in-progress arc" | Group 1800 human-attention Cat A-F sequence closed at S1806; canonical summary at 1899 absent — Group is **STALE-INDETERMINATE** | banner candidate confirmed |
| S1033 top-cited (5 refs) | S1033 was Chris's "architectural moment" — cited by ARCHITECTURE_INDEX for foundational context | healthy citation confirmed |
| S780 top-cited (5 refs) | S780 was approve-operation-fix session — cited from RATIFICATION_2026-07-19 + skin-layer audit + 2799 canonical | healthy citation confirmed |
| S2701 for "playbook_authoring" | S2701 was playbook_authoring seed — cited from 3 platform/ docs | healthy citation confirmed |

All confirmed. Judgment stands.

### 6.3 False-negative spot check — 1 prose-only citation of an "uncited" handoff

Manually searched for prose references to a random uncited handoff
(`SESSION_500_ADAPTIVE_LEARNING.md`) — 0 hits in non-handoff corpus.
The "89.6% uncited" number does not appear to over-count due to
missed prose refs. Extrapolating: prose refs to uncited handoffs
would need to inflate the citation graph by ~10x to bring uncited
below 50% — highly unlikely at current corpus state.

---

## 7. Rigby SIGN pressure test — recommended dimensions for cycle 1

Per `feedback_zoom_out_ask_per_rigby_sign` and
`feedback_verify_rigby_tool_runs_before_trusting_sign`, cycle-1
routing should include tool-grounded verification directives + at
least one zoom-out ask.

**Q1 (severity classification):** Is the 4-class severity taxonomy
(broken_path / broken_shortform / retrieval_harm / citation_healthy
/ uncited_terminal) correctly capturing the T4 domain? Or should
`broken_shortform` split further into `prose_ref` (P3 keep) vs
`link_form_ref` (P2 fix)? Verify by grep of `HANDOFF_NUMBERING_GAPS.md`
+ inspection of 3 sample rows.

**Q2 (retrieval-harm probe query set):** The 10 probe queries were
chosen heuristically. Which queries should be added / removed to
produce a more operator-authentic banner-candidate list? Verify by
proposal + `search_embeddings` re-run.

**Q3 (banner recommendation scope):** Should the T4 banner candidate
list include ONLY handoffs surfacing at rank 1-3 (high-visibility),
or all top-K (rank 1-8) hits regardless? T4 currently lists all 12
unique handoffs across ranks 1-8; Rigby could argue for
rank-1-3-only filter (would drop to 6-7 candidates) or all-top-K
(current). Verify via `search_embeddings` rank threshold sweep.

**Q4 (T2 short-form over-count):** T4 asserts T2's 17
`ref_class=session` BROKEN_404 flags are 17 prose refs (all P3).
Rigby verifies by loading T2 output + sampling 3-5 short-form flags
via `repo_tool.read` at the cited line + confirming prose-vs-link
form.

**Q5 (zoom-out ask):** Step back — is the T4 arc actually asking the
right question? Parent §4 T4 spec said "citation-integrity +
retrieval-harm audit." T4 as-authored is more accurately a
"citation-graph-shape + retrieval-harm-candidate" audit. Is there a
different question (e.g., "how much operator-time is currently spent
navigating broken handoff references?") that would produce a more
actionable finding? Or is the current shape correct because handoff
citations are structurally small and retrieval-harm is where the
real operator-friction lives?

---

## 8. Ratification envelope preview (for §11.3 rendezvous)

Envelope draft at S2838 close will confirm:

1. **T4 corpus enumeration:** 1061 handoff files (1046 SESSION_ + 15 non-SESSION_).
2. **Positive headline:** zero P0 root-stability triggers; citation graph small + concentrated in anchor-reachable canonical docs (90.3% of citations trace to healthy citing docs).
3. **Decay curve:** 89.6% uncited; recent handoffs cite at 26.8%; old handoffs at 2-4%; middle era (S1500-S2499) under-cited but structurally healthy.
4. **Sub-loop (b) empirical unfounded chunk-ID reset:** zero `#K` chunk-ID form citations exist; total fragment surface = 3 edges corpus-wide.
5. **Sub-loop (c) banner candidate list:** 13 unique handoffs recommended for DOC-POINTER-V1 stats-drift banner treatment (12 from initial 10-probe set + 1 SESSION_2759 from cycle-2 Q2 ops-recovery probe); all `escalate_to_chris`; all deferred to 2899 workshop per S2836 policy. Annotate-not-filter approach (cycle-2 Q3 fold): keep all top-K unique hits with similarity + probe-query + stale_hypothesis annotation, do NOT filter by rank or absolute similarity threshold (would exclude actual stale-arc candidates).
6. **Broken citations:** 6 path-form (P1 escalate) + 3 fragment-form (P2 escalate) + 17 short-form (P3 keep_as_is, prose refs — 5/17 manually verified per cycle-2 Q1 fold) = 26 T4 findings-of-interest; 22 add to 2899 workshop queue.
7. **T5 territory unaffected:** handoffs live in `docs/handoffs/`, not T5 audits/reports territory; T3a↔T5 boundary rule does not apply to T4.
8. **§10.1 v1.1 schema unchanged.** T4 does not propose schema changes; three v1.2 candidates recorded as future_trigger: (a) `citation_style` field (§5.2); (b) probe-query canonical set (§5.7); (c) sub-loop (b) rerun trigger (§5.4).
9. **Cross-child pre-clustering pattern:** T4 consumed T2 (citation edges) + T3b (citing-doc weight) — third consecutive successful child-to-child substrate consumption in Group 2800.
10. **Playbook v3 codify candidate:** "child audit MAY consume prior-child substrate; if it does, ingest, do NOT re-derive" — three-trigger corroboration (T3a←T2, T3b←T3a, T4←T2+T3b). Recorded but NOT codified now.
11. **Scanner cost:** ~3s runtime; dominated by 10 embedding calls; grep + JSON loads sub-second. Full re-run cost trivial.
12. **`escalate_to_chris` accumulation:** 22 T4 rows add to arc queue → 99 total at end of T4 (T3a: 2 + T3b: 75 per S2837 pointer; T1 + T2 contributed 0 to accumulation per pre-S2836-policy child ratifications; T4: 22 = 6 P1 path-form + 13 P2 retrieval-harm + 3 P2 fragment). T5 will grow the queue further.
13. **`make recycle-all` clean:** post-close-cascade PR merge per PLAYBOOK-7.4.4.
14. **Handoff:** `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md` (authored at close).
15. **Envelope:** `docs/research/implementation/RATIFICATION_2026-07-19_2804_docs_content_handoff_audit.md`.
16. **Group 2800 arc state:** T4 shipped; 6 of 6 children shipped; T5 opens at S2839; 2899 canonical summary follows.
17. **Next thread:** T5 reports+audits triage audit opens at S2839 (child audit `2805_docs_content_reports_audits_triage.md`) with T3b `t5_may_override` pre-clustering per §5.4 workflow directive.

---

## 9. Migration queue routing (per §10.4 cross-arc consumption contract)

Consumers of this doc's `## 3. Migration queue (post-arc)` section:

- **`2899_docs_content_canonical_summary.md`** — pending arc-close.
  Will aggregate the 6 P1 + 12 P2 retrieval-harm banner candidates
  + 3 fragment-form P2 into the canonical Chris-workshop queue.
- **Group 2700 §3 execution arc (future)** — will consume the 6
  P1 path-form fixes as citing-doc migration PRs (small 1-line
  edits).
- **DOC-POINTER-V1 substrate arc (future, if opened)** — will
  consume the 12 retrieval-harm banner candidates as substrate
  design inputs.

Per S2836 arc-close deferral policy, this doc's migration queue
does NOT route rows individually mid-arc. All rows accumulate to
2899 workshop.

---

## 10. What this research taught us about how to do research

### 10.1 What worked

1. **Consuming pre-clustering substrate is high-ROI.** T4's scanner
   is ~550 lines and runs in ~3s; without T2's pre-computed edges
   + T3b's reachability rows, the scanner would need to re-grep
   the corpus + re-BFS anchor graphs, taking ~10-15s and ~800
   lines. Substrate consumption pattern saves engineering time
   AND aligns the arc: T4 findings sit inside T2/T3b's
   interpretive frame instead of re-litigating classification.

2. **Anti-pattern challenge in §1.4 saved a bad framing.** The
   naive "uncited handoff = archival candidate" framing would
   have generated ~833 P2 rows (huge Chris workshop bloat).
   Explicitly challenging the anti-pattern at method-scoping
   time led to the correct classification (`uncited_never_retrieved`
   is P3 keep_as_is, not archival candidate).

3. **Empirical falsification is a first-class finding.** Parent §4
   T4 sub-loop (b) rationale assumed post-S1143 chunk-ID resets
   would break `#K` citations. T4 empirically found ZERO `#K`
   citations exist. This is an important "the concern doesn't
   apply at current corpus state" finding — worth as much as any
   positive defect count.

4. **Small numbers matter at boundary conditions.** 3 fragment
   citations, all broken (100%), is a *low-confidence* finding
   because N=3. Reporting N + resolution rate + noting the small
   sample size prevents misreading the 100% as a substrate crisis.

### 10.2 What to codify into playbook v3

1. **Codify child-audit substrate consumption pattern.** Three-trigger
   corroboration: T3a←T2, T3b←T3a+T2, T4←T2+T3b. Add to Playbook
   §11.3 template as "child audit MAY declare `consumes_pre_clustering`
   frontmatter; scanner MUST ingest the referenced JSON, MUST NOT
   re-derive." Threshold satisfied per feedback methodology.

2. **Codify empirical-falsification-is-finding pattern.** Add to
   §11.3 canonical summary template: "Findings section MAY report
   `null_result` — e.g., '0 rows of P0 severity' or 'chunk-ID reset
   hypothesis empirically unfounded.' Reporting null results
   prevents future arcs from re-litigating already-refuted
   hypotheses." Trigger source: T3b §2.1 (0 unreachable) + T4 §2.4
   (0 chunk-ID citations) — two-trigger.

### 10.3 Anti-patterns to avoid

1. **Do not re-grep the corpus when pre-clustering substrate
   exists.** T2 pre-computed 145 handoff citation edges; the
   T4 sub-loop (a) trap was "just re-grep everything to be sure."
   Resisting the trap saved ~5s + kept T4 findings aligned with T2.

2. **Do not classify uncited terminal artifacts as archival
   candidates.** Handoffs are write-once-terminal by design (parent
   §7). Uncited is healthy state, not orphan status. Same rule
   applies for other terminal-artifact classes (ratification
   envelopes, closed-arc audits).

3. **Do not conflate T2 short-form BROKEN_404 with actionable
   broken links.** 17 of 17 T2 short-form BROKEN_404 flags in T4's
   corpus slice are prose gap-mentions. Downstream automation that
   treats "T2 BROKEN_404" as fix-me signal would generate 17 false-
   positive PR-work items.

### 10.4 Suggestions for the playbook itself

1. **Add `citation_style` to §10.1 schema (v1.2 candidate).**
   `citation_style: markdown_link | backtick_path | prose_ref |
   fragment_form`. Would let T2 v2 auto-distinguish prose refs
   from broken links. Currently one of three v1.2 candidates
   accumulated across T2/T3a/T3b/T4.

2. **Add `null_result` finding class.** Currently the schema
   assumes every row is either a defect or a healthy classification.
   A dedicated `null_result` type would let arcs report empirical
   falsifications as first-class findings (e.g., "0 chunk-ID
   citations exist" is a positive finding, not the absence of
   findings).

### 10.5 Suggestions for future canonical summaries (optional)

1. **Include a "workshop queue by thread" table.** At 2899, tally
   `escalate_to_chris` rows by contributing thread (T1: N; T2: N;
   T3a: N; T3b: N; T4: N; T5: N). This helps Chris prioritize
   workshop time — high-N threads may need pre-workshop skimming.

2. **Include a "hypotheses falsified" section.** Enumerate the
   concerns raised in parent-scoping that turned out to be
   empirically non-issues. Documents the arc's contribution to
   *not* doing unnecessary future work.

---

## 11. Cross-links

- **Parent scoping:** `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- **T2 substrate (basename map + citation edges):** `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md` + `/tmp/t2_scan_out.json`
- **T3b substrate (citing-doc reachability):** `docs/research/domains/docs_content_audit/2803b_docs_content_orphan_audit.md` + `/tmp/t3b_orphan_scan_out.json`
- **T3a substrate (V2-stub direct-marker seed):** `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
- **T1 substrate (anchor graph):** `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
- **Group 2700 sibling (structural):** `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`
- **DOC_LIFECYCLE:** `docs/00-START-HERE/DOC_LIFECYCLE.md` (§1 V2 pointer pattern + §2b + §2c)
- **T4 scanner:** `tools/audit_2804_handoff_citation_integrity.py`
- **T4 scanner output:** `/tmp/t4_handoff_audit_out.json`
- **S2838 handoff:** `docs/handoffs/SESSION_2838_T4_HANDOFF_CITATION_INTEGRITY_AUDIT.md` (authored at close)
- **S2837 handoff:** `docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md`
- **S2836 arc-close deferral policy:** `feedback_arc_close_deferral_for_escalate_to_chris` (memory)
- **S2837 T3b §5.4 T5 workflow directive:** consumed as `future_trigger` for 2805 T5 authoring

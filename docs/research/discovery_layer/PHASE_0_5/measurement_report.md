---
title: "Phase-0.5 Balanced P1 Harvest — Measurement Report (S2825)"
status: LOAD-BEARING — Chris D-verdicts D1-D5 ratified 2026-07-19 (see harvest_verdict.md §4a)
authority: LOAD-BEARING
session: 2825
generated: 2026-07-19
supersedes: none
related:
  - docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md   # B1 D-RATIFIED S2823 §10 constitutional gate
  - docs/research/discovery_layer/PHASE_0_5/corpus.json                    # 20 P1 rows harvested this session
  - docs/research/discovery_layer/PHASE_0_5/harvest_dispatch_results.json  # raw dispatch envelopes
  - docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md
  - docs/research/discovery_layer/PHASE_0/RECOMMENDATION_PHASE0_SUMMARY.md # Phase-0 60-point P1-vs-P3 gap that motivated Phase-0.5
scope: |
  Per B1 §6 step 7: measurement report for the balanced P1 harvest.
  Reports per-family + per-operator + per-tier accuracy against Phase-0
  baseline. Documents §10.4 methodology-back-to-SIGN triggers surfaced
  during execution. Two-view accuracy (balanced-set primary + frequency-
  weighted sanity check) per §3.3.
---

# Phase-0.5 Balanced P1 Harvest — Measurement Report

**Session:** 2825
**Date:** 2026-07-19
**Corpus:** `docs/research/discovery_layer/PHASE_0_5/corpus.json` — 20 P1 rows, R1-provenance-tagged, field_dictionary v0 compliant.
**Dispatch batch:** `docs/research/discovery_layer/PHASE_0_5/harvest_dispatch_results.json`
**Router log SoT:** `logs/phase_0_5_router.jsonl` — 21 new rows in measurement window `win-5310154b8d764c2a`
**Integrity events:** `logs/phase_0_5_integrity_events.jsonl` — 1 event (T2 abstain-rate cap)
**Governing envelope:** `RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md`

## §1 — Harvest execution summary

**Balance targets met:**

| Operator | Hard min | Preferred | Actual |
|---|:---:|:---:|:---:|
| Chris | 5 | 8 | **5** ✓ hard-min |
| Claude | 5 | 8 | **8** ✓ preferred |
| Rigby | 5 | 8 | **7** ✓ hard-min |
| **Total** | **15** | **24** | **20** — meets §2.2 stop-condition floor |

**Family-shape distribution (aggregate, per intended_family primary):**

| Family | n | % |
|---|:---:|:---:|
| SELF-REFERENCE | 5 | 25% |
| DISCOVERY | 4 | 20% |
| IDENTITY | 4 | 20% |
| CONCEPTUAL | 3 | 15% |
| COUNT | 3 | 15% |
| PROCEDURAL | 1 | 5% |

Family-shape balance is not enforced (§3 R6 no-synthesis); PROCEDURAL is
underrepresented (1 row) because organic Claude/Rigby operational queries
that we could harvest verbatim are dominated by benchmark/validation/
navigation shapes, not "how do I do X" procedural asks.

**Dispatch results:**

- 20 corpus rows dispatched via Rigby PA kb_tool.semantic_search (per Rigby S2825 Q4 SIGN)
- 20 router_decision rows produced in measurement window `win-5310154b8d764c2a`
- **After decision #20: router self-aborted the window at T2 (abstain-rate = 0.400 > 0.300 cap)**
- Q27 + Q28 dispatched post-abort → returned `INTEGRITY_STOP_T2` decisions (no measurement)
- **18/20 rows have full measurement; 2/20 (Q27, Q28) aborted**

## §2 — §2.1 authoritative viability metric (classifier only — retrieval-accuracy correlation deferred)

Per B1 §2.1 (Chris R1 RATIFIED): authoritative viability metric = **top-1 correct `intended_family` AND top-1 correct `known_correct_target_strict` per harvested row**.

This report covers the CLASSIFIER portion of the §2.1 metric (predicted_family vs intended_family, with AMBIGUOUS-ground-truth handled per v0 rule 6). Retrieval-accuracy correlation (does chunks[0].file_path match known_correct_target_strict?) is deferred to §5 because the current router JSONL schema does not log chunk file paths — only retrieval_count — so cross-referencing requires parsing the raw dispatch envelope JSON, which is planned for §5 amendment after Rigby SIGN.

### §2.1 Classifier-only per-family results (18 measurable rows)

| Family | n | Correct | Accuracy | Floor prior | Verdict |
|---|:---:|:---:|:---:|:---:|:---:|
| COUNT | 3 | 3 | 100% | 0.90 | ✓ meets floor |
| PROCEDURAL | 1 | 1 | 100% | 0.75 | ✓ meets floor |
| DISCOVERY | 4 | 0 | 0% | 0.70 | ✗ FLOOR MISS |
| IDENTITY | 3 (Q27+Q28 aborted) | 2 | 67% | 0.90 | ✗ FLOOR MISS |
| SELF-REFERENCE | 5 | 5 | 100% | 0.90 | ✓ meets floor |
| CONCEPTUAL | 3 | 1 | 33% | 0.70 | ✗ FLOOR MISS |
| **Aggregate** | **18** | **12** | **66.7%** | — | ≥60% continue band |

DISCOVERY floor-miss is stark — 0/4 correct. All four DISCOVERY rows either got predicted differently or were UNCLASSIFIABLE. Root cause: Chris-authored questions like "What does Documentation currently include?" / "Which tools already support it?" don't match Classifier A's regex for DISCOVERY — they match CONCEPTUAL or fail all patterns.

### §2.2 Per-operator-style accuracy (§3.3 two-view reporting)

| Operator | n measured | Correct | Style accuracy |
|---|:---:|:---:|:---:|
| Chris | 5 | 1 | **20%** |
| Claude | 8 | 7 | 87.5% |
| Rigby | 5 (Q27+Q28 aborted) | 4 | 80% |

**View 1 — Balanced-set accuracy (primary, per §3.3 R1 go/no-go authority):**
(20% + 87.5% + 80%) / 3 = **62.5%**

**View 2 — Frequency-weighted accuracy (secondary, operational sanity check with ~10% Chris / ~45% Claude / ~45% Rigby):**
0.10 × 20 + 0.45 × 87.5 + 0.45 × 80 = 2 + 39.4 + 36 = **77.4%**

### §2.3 §2.2 stop-condition band verdict — draft (subject to §3 §10.4 triggers)

Per §2.2 band table (Chris R2 RATIFIED):

| Metric | Value | Band | Draft verdict |
|---|:---:|:---:|---|
| Balanced-set accuracy (primary) | 62.5% | ≥60% band | **Continue to Phase-1 advisory dogfood only** |
| Frequency-weighted (sanity check) | 77.4% | ≥60% band | Corroborates continue |
| Aggregate (raw) | 66.7% | ≥60% band | Corroborates continue |
| **Chris-style accuracy** | **20%** | **≤40% NOT viable** | **CONTRADICTS aggregate** |
| Claude-style | 87.5% | ≥60% | Continue |
| Rigby-style | 80% | ≥60% | Continue |

**The Chris-style rate is at the ≤40% NOT-viable floor while balanced-set aggregate is in the ≥60% continue band.** This is a genuine stop-condition-band-shape mismatch (§10.4 trigger) — the plan §2.2 didn't anticipate that per-operator-style rates could contradict aggregate.

## §3 — §10.4 methodology-back-to-SIGN triggers surfaced during execution

Per Chris §10.4 directive (LOAD-BEARING, S2823 D-verdict): "If execution uncovers findings that materially challenge any of these ratified assumptions, stop, document the evidence, and route the methodology back for SIGN rather than silently adapting the experiment."

**FOUR triggers surfaced during S2825 execution:**

### §3.1 Trigger — Stop-condition band shape empirically wrong

- Balanced-set aggregate at 62.5% is in the ≥60% "continue" band
- Chris-style accuracy at 20% is at the ≤40% "NOT viable" floor
- These verdicts CONTRADICT — the aggregate says continue, the sub-operator rate says not viable
- §2.2 band table does not specify what to do when per-operator rates disagree with aggregate
- **§10.4 explicit language: "Stop-condition band shape empirically wrong (e.g., harvested rows cluster tightly around 40% or 60%, suggesting the band boundaries are noise-vs-signal ambiguous)"** — Chris-rate at exactly 20% doesn't cluster around a band boundary but DOES surface a hierarchy question (aggregate vs per-style) that the bands don't address.

### §3.2 Trigger — Scoring metric edge case not covered by §2.1

- §2.1 froze the metric as "top-1 correct intended_family AND top-1 correct known_correct_target_strict per harvested row"
- Under this metric, Q12/Q15/Q16/Q25/Q27/Q28 have `secondary_family` set (AMBIGUOUS ground-truth) — the metric should credit AMBIGUOUS classifier abstain OR either primary/secondary family
- Handled in the analysis (Q12 counted correct because abstain=UNCLASSIFIABLE with secondary set; Q25 counted correct because abstain=AMBIGUOUS with secondary set)
- Q27 + Q28 have secondary_family set BUT got INTEGRITY_STOP_T2 (not a real classifier abstain — window aborted)
- **§10.4 language: "Scoring metric edge case ... where strict target is genuinely dual-valued and the top-1 discipline breaks down"** — the INTEGRITY_STOP case for rows with secondary_family is edge-case ambiguous — should it count correct? Wrong? Uncounted? Chris D-verdict needed.

### §3.3 Trigger — Router integrity stop fired during measurement

- Router T2 cap = 0.30 abstain rate (default in `PHASE_0_5_MEASUREMENT_WINDOW_N=20`)
- Measured abstain rate = 0.400 (8 abstains / 20 routed)
- Constitutional discipline working AS DESIGNED — the router said "you can't trust this measurement"
- But this MEANS the harvest is 18/20 measurable, not 20/20 — 2 rows lost to abort
- Question: is the 30% cap right for REAL P1 queries? (Phase-0 P3 synthetic showed 89% accuracy = 11% abstain; Phase-0 P1 showed 20% accuracy = often higher abstain. Real queries are messier by design.)
- **§10.4 language (implicit): "Balance targets unachievable via §4 harvest sources"** — n≥20 was achievable at harvest time but only n=18 is measurable due to abort. Whether to raise cap OR accept incomplete OR redesign measurement window are all Chris decisions.

### §3.4 Trigger — DISCOVERY family accuracy = 0

- 4/4 DISCOVERY rows misclassified (Q10 predicted CONCEPTUAL; Q11 UNCLASSIFIABLE; Q22 AMBIGUOUS; and per-row inspection needed)
- Chris R3 preserve directive (§7) is EXPLICIT: "NO DISCOVERY fixes during harvest (measure only)"
- This trigger is INFORMATIONAL, not action-requesting — Chris's directive already anticipated DISCOVERY weakness
- Documented here for completeness; no methodology change needed

## §4 — Comparison to Phase-0 baseline

Phase-0 baseline (33-row corpus, 5 P1 + 10 P2 + 18 P3, from RECOMMENDATION_PHASE0_SUMMARY.md):

| Metric | Phase-0 | Phase-0.5 (this session, 18 measured) |
|---|:---:|:---:|
| Aggregate P1 accuracy | 20% (n=5 all DISCOVERY) | 66.7% (n=18, balanced) |
| Chris-style accuracy | not stratified | 20% (n=5) |
| Claude-style accuracy | not stratified | 87.5% (n=8) |
| Rigby-style accuracy | not stratified | 80% (n=5) |

**Phase-0 P1 was 5/5 DISCOVERY rows all Rigby-originated (per corpus.json R1-R5). Phase-0.5 P1 spans 6 families across 3 operator styles. The 60-point gap Phase-0 found (P1=20%, P3=89%) MOSTLY held for Chris-style (20%) but INVERTED for Claude-style (87.5%) and Rigby-style (80%).**

**Interpretation:** the P1-vs-P3 gap in Phase-0 was NOT a real-vs-synthetic gap — it was a **Rigby-originated-DISCOVERY-shape vs synthetic-benchmark-shape** gap. Real P1 from other operator styles achieves synthetic-like accuracy. Chris-style specifically remains a hard case for classifier-only routing.

This finding has significant implications for Phase-1 disposition — see §6.

## §5 — Retrieval-accuracy correlation (OBSERVATIONAL ONLY per Rigby S2825 Q4 refinement)

Per Rigby S2825 Q4 SIGN refinement (AGREE-with-refinements, NOT F-BLOCKING): **retrieval↔accuracy correlation computed now as observational on the 18-row measurable set; EXPLICITLY BARRED from influencing the §2.2 go/no-go verdict until §10.4 triggers are Chris-D-ratified.**

Parsed from `harvest_dispatch_results.json` raw dispatch envelope tails via regex extraction of first `file_path` field per query. 2 rows (Q15, Q25) had no parseable envelope in the stdout tail (short response truncation); 2 rows (Q27, Q28) were INTEGRITY_STOP_UNMEASURED per §2.1/§3.2. Net measurable retrieval: **16 rows.**

### §5.1 Aggregate retrieval-strict-hit + loose-hit rates

| Metric | Rate | Interpretation |
|---|:---:|---|
| Retrieval top-1 in `known_correct_target_strict` | **0/16 = 0%** | Zero strict-hits across 16 measurable rows |
| Retrieval top-1 in `known_correct_target_loose` | **0/16 = 0%** | Zero loose-hits either |

**Devastating observational baseline.** The router-plus-search_embeddings combination did not return ANY row's expected target as top-1 rank across ALL 16 measurable queries. This is the retrieval-side companion to the S2813 T3 human-pain audit finding (C3/C4/C5) — retrieval systematically fails at DOC_LIFECYCLE §2c count queries + literal filename queries + POINTER_DOC self-references.

### §5.2 Per-row detail

| qid | family | top_1_returned | strict_target | strict_hit |
|---|---|---|---|:---:|
| Q9 | CONCEPTUAL | docs/research/domains/api/2599_api_canonical_summary.md | RECOMMENDATION_PHASE0_SUMMARY.md | ✗ |
| Q10 | DISCOVERY | docs/research/domains/event_integration_architecture/2001_ev... | docs/canon/INDEX.md | ✗ |
| Q11 | DISCOVERY | docs/research/domains/content/1605_content_rigby_pa_tooling... | docs/PLATFORM_INVENTORY.md | ✗ |
| Q12 | CONCEPTUAL\|DISCOVERY | docs/research/domains/authority_enforcement/1901... | docs/topics/employee-os.md | ✗ |
| Q13 | CONCEPTUAL | docs/research/tools/tools_operational_contract_domain_defini... | BALANCED_P1_HARVEST_PLAN.md | ✗ |
| Q14 | SELF-REFERENCE | docs/handoffs/SESSION_1187_UTILIZATION_RECON.md | 00-START-NEXT-SESSION.md | ✗ |
| Q15 | SELF-REFERENCE\|PROCEDURAL | NO_ENVELOPE_PARSED | — | — |
| Q16 | SELF-REFERENCE\|PROCEDURAL | docs/handoffs/SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md | 00-START-NEXT-SESSION.md | ✗ |
| Q17 | SELF-REFERENCE | docs/EOS_RULES.md | CLAUDE.md | ✗ |
| Q18 | PROCEDURAL | docs/research/domains/event_integration_architecture/2001_ev... | docs/AGENTS_REFERENCE.md | ✗ |
| Q19 | IDENTITY | docs/handoffs/SESSION_1706_OBSERVABILITY_CAT_F_ADJACENT_SEPA... | 2701_docs_inventory_topology_audit.md | ✗ |
| Q20 | SELF-REFERENCE | docs/handoffs/SESSION_1219_WATCHDOG_FIX_3_PHASE_SHIP.md | 00-START-NEXT-SESSION.md | ✗ |
| Q21 | COUNT | docs/architecture/PLATFORM_ARCHITECTURE_MAP.md | docs/PLATFORM_INVENTORY.md | ✗ |
| Q22 | DISCOVERY | docs/research/implementation/observability_spine_mission_evi... | ROUTER_SCAFFOLDING_DESIGN.md | ✗ |
| Q23 | COUNT | docs/architecture/PLATFORM_ARCHITECTURE_MAP.md | docs/PLATFORM_INVENTORY.md | ✗ |
| Q24 | IDENTITY | docs/research/platform/platform_constitutional_transition_re... | docs/PLATFORM_INVENTORY.md | ✗ |
| Q25 | DISCOVERY\|IDENTITY | NO_ENVELOPE_PARSED | (null-strict, secondary set) | — |
| Q26 | COUNT | docs/architecture/PLATFORM_ARCHITECTURE_MAP.md | docs/PLATFORM_INVENTORY.md | ✗ |
| Q27 | IDENTITY\|DISCOVERY | INTEGRITY_STOP_UNMEASURED | — | — |
| Q28 | IDENTITY\|DISCOVERY | INTEGRITY_STOP_UNMEASURED | — | — |

**Systemic pattern: COUNT queries (Q21/Q23/Q26) ALL return `docs/architecture/PLATFORM_ARCHITECTURE_MAP.md` instead of `docs/PLATFORM_INVENTORY.md`.** DOC_LIFECYCLE §2c ("PLATFORM_INVENTORY.md is the sole authoritative counts source") is not being enforced at the retrieval layer. This is Phase-0 T3 C5 human-pain reproducing at S2825 despite S2818 authority-boost + S2819 shape-C intent gating + S2820 orientation-doc exclusion pilots.

### §5.3 §2.1 authoritative metric (classifier AND retrieval)

**§2.1 = top-1 correct intended_family AND top-1 correct known_correct_target_strict per harvested row.**

- Classifier-correct rows: 12/18 (66.7%)
- Retrieval-strict-hit rows: 0/16 (0% of measurable retrieval subset)
- **§2.1-authoritative correct: 0/18 = 0%** (classifier-correct AND retrieval-strict-hit intersection is empty)

**This is the primary §2.2 stop-condition-band input. Under §2.2 as literally written: ≤40% → NOT viable, decisive floor. 0% is well below 40%.**

**Rigby Q4 refinement caveat: this retrieval finding is BARRED from influencing go/no-go until §10.4 triggers are Chris-D-ratified.** But once the triggers are resolved (whether by cap change, methodology revision, or per-style hierarchy definition), the 0% retrieval-strict-hit rate is the load-bearing evidence.

## §6 — Draft recommended verdict — REFRAMED per Rigby S2825 Q5 F-BLOCKING refinement

**Rigby Q5 F-BLOCKING refinement (2026-07-19):** the operator-style split is really a query-phenotype split. "Chris-style" queries are CONCEPTUAL/DISCOVERY meta-questions about the platform ecosystem ("What does X currently include?", "How do we determine WHICH X should Y?", "Can X be inferred from Y alone?"). The retrieval-substrate + classifier combination is failing on THIS PHENOTYPE regardless of who authored the query. Framing this as "Chris personally" mis-scopes the finding: (a) undersells the failure (any operator asking that phenotype hits the same wall) and (b) oversells any Phase-1 "partial-router" gate (a Claude/Rigby query with the same phenotype would fail too).

**Reframed draft verdict:** **Route methodology back for §2.2 revision + T2 cap methodology decision before any Phase-1 disposition. Aggregate viability (62.5% balanced-set / 66.7% classifier / 0% §2.1-authoritative-full) is contradictory across sub-metrics. Query-phenotype hierarchy must be defined by Chris before verdict-band interpretation is safe.**

**Rationale:**
- **§2.1 authoritative-full metric = 0%** (retrieval-strict-hit = 0/16). This is below the ≤40% NOT-viable floor.
- **Classifier-only aggregate = 62.5%** balanced-set (≥60% continue band). But this is HALF of §2.1 — retrieval half is 0%.
- **Query-phenotype disaggregation** shows CONCEPTUAL/DISCOVERY meta-questions fail routing AND retrieval systematically; COUNT/IDENTITY/SELF-REFERENCE well-formed queries pass classifier but STILL fail retrieval (DOC_LIFECYCLE §2c not enforced).
- Phase-1 advisory-dogfood decision under §2.2 as written cannot handle:
  - Multi-metric contradiction (classifier says continue, retrieval says NOT viable)
  - Per-phenotype hierarchy (meta-queries fail; well-formed queries pass classifier but fail retrieval)
  - T2 self-abort at 40% real-P1 abstain rate — signal the 30% cap is under-parameterized for real-op measurement

**Alternatives Chris should weigh (reframed per Q5 R):**

- **(A) Revise §2.2 methodology** — explicitly define aggregate-vs-per-phenotype hierarchy + explicitly define classifier-vs-retrieval-vs-combined metric authority + revise T2 cap for real-P1 harvest scope → then re-run measurement on refined methodology. **Highest-integrity path, moves ratified methodology forward.**
- **(B) Continue Phase-1 dogfood universally** treating classifier aggregate as authoritative → accepts 0% retrieval-strict-hit as tolerable if Phase-1 advisory doesn't drive retrieval choice → Chris R1 ADVISORY-ONLY discipline covers this.
- **(C) Partial-router: continue Phase-1 dogfood for COUNT/IDENTITY/SELF-REFERENCE phenotypes only** where classifier accuracy is high (100%) even though retrieval fails → advisory still doesn't drive retrieval → phenotype-scoped instead of operator-scoped per Q5 R.
- **(D) Shelve Phase-1 router entirely** — the 0% retrieval-strict-hit says routing-to-substrate is not the bottleneck; retrieval-quality-itself is. Redirect engineering to retrieval quality (DOC_LIFECYCLE §2c enforcement at retrieval layer, canonical target matching, etc.).

**Draft recommendation to Chris:** **(A) revise §2.2 methodology.** The finding is materially load-bearing enough that codifying the resolution PROPERLY before any Phase-1 dogfood proceeds is the highest-integrity path. If Chris wants to move faster: (C) partial-router by phenotype is defensible under §2.2 middle-band language once phenotype hierarchy is explicit.

## §7 — What worked / what to fold back / methodology-teaches

Per Playbook §11.3 xx99 template extension (S1399 close):

**§7.1 What worked:**
- Rigby joint SIGN Q1-Q6 on the harvest execution plan caught the substrate-mutation risk (Q1 wrapper refinement) + advisory-blind labeling risk (Q6 refinement)
- Anti-rubber-stamp check on Rigby SIGN passed (5+ substantive tool_runs; conversation_tool.search + repo_tool.read_file mix)
- 20 balanced-P1 rows harvested WITHOUT synthesizing to fill balance gaps
- Router self-aborted at T2 = constitutional discipline working AS DESIGNED

**§7.2 What to fold back to Playbook v0.9+:**
- Consider codifying "per-operator-style disaggregation must accompany aggregate accuracy verdicts" for stop-condition band decisions — Phase-0.5 is first evidence that aggregate can mask sub-cohort failure
- Consider extending PLAYBOOK-6.10.9 fold-authoring-evidence-admission to research-execution outcomes that trigger §10.4 methodology reviews (this measurement report IS a §10.4 trigger corpus — 4 triggers surfaced)

**§7.3 Anti-patterns avoided:**
- Did NOT synthesize rows to fill Chris-style balance gap (§3 R6 preserved even under time pressure)
- Did NOT let the router advisory influence known_correct_target_strict labeling (Q6 refinement held — labels were authored BEFORE dispatches per corpus.json `authoring_discipline.advisory_blind_labeling` note)
- Did NOT silently adapt the experiment when T2 fired (§10.4 discipline held — routing back to SIGN + Chris D-verdict)

## §8 — Rigby joint SIGN status — CLEARED with 4 F-BLOCKING refinements (all applied)

Rigby joint SIGN cycle at S2825 turn ~14 via pin `pa-5d610d3a46c9464e`.

| Q | Subject | Verdict | Refinement applied |
|---|---|---|---|
| Q1 | §2.2 hierarchy (aggregate vs per-style) | **AGREE (F-BLOCKING)** | Refined §3.1 to state hierarchy is undefined by §2.2 as ratified — genuine §10.4 trigger requiring Chris D-verdict |
| Q2 | Q27+Q28 INTEGRITY_STOP counting | **AGREE-with-refinements (F-BLOCKING)** | Applied: Q27+Q28 UNMEASURED for accuracy denominators; still counted in integrity/abort events |
| Q3 | T2 cap 0.30 for real P1 | **AGREE-with-refinements (F-BLOCKING)** | Applied: 40% observed abort rate = strong evidence cap/coverage interaction needs methodology decision (not silent tweak) |
| Q4 | §5 retrieval correlation deferral | **AGREE-with-refinements (NOT F-BLOCKING)** | Applied: computed §5 NOW as observational (result 0/16 strict-hit); §5.3 explicitly BARS this from go/no-go until §10.4 Chris-D-ratified |
| Q5 | §6 draft verdict framing (Chris personally vs query phenotype) | **AGREE-with-refinements (F-BLOCKING)** | Applied: reframed §6 as query-phenotype not operator-personal; verdict flipped from "partial-router Chris-off" to "route back for §2.2 revision" (option A) as draft recommendation |

**Anti-rubber-stamp PASSED:** Rigby tool_runs included 4 substantive `search_docs` probes on `BALANCED_P1_HARVEST_PLAN §2.2` + `ROUTER_SCAFFOLDING_DESIGN §12 T2` + `field_dictionary rule 6` + `harvest_plan §5 rule 4` before verdicts. Zero rubber-stamp signal.

## §9 — Next step: Chris D-verdict

**Routes to Chris via Chat UI for D-verdict on:**

- §2.2 stop-condition-band hierarchy definition (aggregate vs per-phenotype)
- T2 cap methodology (raise / hold / revise-window-scope)
- Q27+Q28 UNMEASURED policy (retroactive-labeling amendment to field_dictionary or corpus.json note)
- §5 retrieval-accuracy correlation admissibility for §2.2 verdict
- §6 draft verdict — Option A (revise methodology) vs B (universal) vs C (phenotype-partial) vs D (shelve)

**Chris D-verdict discipline per §10.4 LOAD-BEARING directive:** silent adaptation of ratified §2.2 methodology is a constitutional violation. Chris rules on ALL five points before any Phase-1 disposition proceeds.

## §10 — Chris D-verdicts RATIFIED 2026-07-19 (S2825 close)

**All five D-verdicts + one additional refinement ratified.** See `harvest_verdict.md` §4a for verbatim. Summary:

- **D1** RATIFIED — aggregate is diagnostic only; per-phenotype failure cannot be masked; §2.2 revision must define phenotypes + hierarchy explicitly
- **D2** RATIFIED-with-refinement — T2 cap 0.30 stays; NO silent tweaks; separate evidence required for any cap change
- **D3** RATIFIED — INTEGRITY_STOP rows UNMEASURED for accuracy denominator; reported separately as integrity evidence
- **D4** RATIFIED — strict retrieval accuracy is LOAD-BEARING; 3-stage separate measurement (classification / substrate recommendation / authoritative top-1 retrieval) with independent success criteria
- **D5** RATIFIED **Option A** — revise §2.2 methodology; no universal rollout; no phenotype-partial rollout; flag stays OFF pending revised methodology ratification
- **Additional** — "Chris-style" renamed to **CONVERSATIONAL_META query phenotype** (conversational / context-dependent / conceptual-discovery); final label subject to methodology-revision SIGN

**Chris framing (verbatim, load-bearing constitutional finding):**

> "The biggest discovery from S2825 is not classifier accuracy. It is that a classifier can appear reasonably accurate while authoritative retrieval is completely inadequate. That distinction is now constitutionally visible. That is exactly the kind of false confidence this platform exists to prevent."

**S2826 opens on §2.2 methodology revision authoring per D5 Option A.** Router substrate remains dormant (flag OFF, .env cleaned S2825 close).

---
title: "Phase-0.5 Balanced P1 Harvest — Chris D-Verdict RATIFIED (S2825)"
status: LOAD-BEARING — Chris D-verdicts D1-D5 ratified 2026-07-19 S2825
authority: LOAD-BEARING
session: 2825
generated: 2026-07-19
supersedes: none
related:
  - docs/research/discovery_layer/PHASE_0_5/measurement_report.md   # full evidence + Rigby SIGN record
  - docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md
  - docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md
---

# Phase-0.5 Balanced P1 Harvest — Chris D-Verdict Ask (S2825)

**One-paragraph summary:** The balanced P1 harvest executed per B1 §6 (20 rows: 5 Chris + 8 Claude + 7 Rigby, hard-min met). Router self-aborted at decision #20 via T2 integrity stop (40% abstain rate > 30% cap — constitutional discipline working as designed). Classifier aggregate accuracy 66.7% (≥60% continue band), BUT §2.1 authoritative-full metric (classifier AND retrieval-strict-hit) is **0% (0/16 measurable rows)** — every single retrieval returned the wrong top-1 file. FOUR §10.4 methodology-back-to-SIGN triggers surfaced. Rigby joint SIGN CLEARED with 4 F-BLOCKING refinements (all applied). Routes to Chris for D-verdict on: (1) §2.2 stop-condition hierarchy (aggregate vs per-phenotype), (2) T2 cap methodology, (3) UNMEASURED policy for INTEGRITY_STOP rows, (4) retrieval-accuracy admissibility, (5) draft verdict option.

## §1 — What harvested and measured

| Field | Value |
|---|---|
| Rows harvested | 20 (Chris 5, Claude 8, Rigby 7 — §3 hard-min met) |
| Rows measured (classifier) | 18 (Q27+Q28 aborted by T2) |
| Rows measured (retrieval) | 16 (Q15+Q25 no envelope parsed; Q27+Q28 aborted) |
| Router self-abort | Yes — T2 abstain-rate cap (0.400 > 0.300) at routed_count=20 |
| Measurement window | `win-5310154b8d764c2a` (type=session) |
| Integrity event | 1 (`docs/research/discovery_layer/PHASE_0_5/integrity_stops/evidence_integrity_stop_T2_20260719T015445_701+0000.md`) |

## §2 — Headline metrics (§2.1 authoritative + §3.3 two-view)

| Metric | Value | §2.2 band |
|---|:---:|---|
| §2.1 CLASSIFIER-only aggregate | 12/18 = **66.7%** | ≥60% continue |
| §2.1 RETRIEVAL-strict-hit | 0/16 = **0%** | ≤40% NOT viable |
| §2.1 AUTHORITATIVE-FULL (both) | 0/18 = **0%** | ≤40% NOT viable |
| §3.3 Balanced-set (primary) | 62.5% | ≥60% continue |
| §3.3 Frequency-weighted | 77.4% | ≥60% continue |
| Chris-phenotype (CONCEPTUAL/DISCOVERY meta-questions) | 20% | **≤40% NOT viable** |
| Claude-phenotype (benchmark queries) | 87.5% | ≥60% continue |
| Rigby-phenotype (validation queries) | 80% | ≥60% continue |

## §3 — The five §10.4 triggers Chris needs to rule on

### D1 — §2.2 hierarchy: aggregate vs per-phenotype

§2.2 as ratified doesn't specify what to do when aggregate says continue (62.5%) but per-phenotype rate says NOT viable (Chris-phenotype 20%). Options:
- **D1a:** aggregate is authoritative → continue Phase-1 for all phenotypes → risk misrouting meta-questions
- **D1b:** per-phenotype at NOT-viable floor overrides aggregate → partial-router only for phenotypes ≥60%
- **D1c:** revise §2.2 explicitly to define hierarchy → re-measure after revision

### D2 — T2 cap methodology (0.30 abstain-rate cap)

Router aborted at 40% real-P1 abstain rate. Is this evidence:
- **D2a:** the CLASSIFIER is under-covering real query shapes (fix classifier) → cap stays 0.30
- **D2b:** real P1 messiness legitimately produces higher abstain rates than synthetic (raise cap to 0.45)
- **D2c:** the CAP tightness is right; the sample is too small (reduce measurement-window-N below 20 for per-window stat significance)

### D3 — INTEGRITY_STOP UNMEASURED policy (Q27, Q28)

Both rows have secondary_family set (IDENTITY|DISCOVERY). Options for accuracy denominator:
- **D3a:** UNMEASURED (removed from denominator) — Rigby-recommended
- **D3b:** counted correct-abstain per v0 rule 6 AMBIGUOUS-ground-truth handling
- **D3c:** counted wrong (fell short of top-1)

### D4 — Retrieval-accuracy admissibility for §2.2 verdict

The 0% retrieval-strict-hit rate is currently OBSERVATIONAL ONLY (Rigby Q4 refinement). Should it:
- **D4a:** stay observational until D1 resolved → §2.2 verdict uses classifier-only for now
- **D4b:** be admitted immediately as §2.1 authoritative-full input → §2.2 verdict is NOT viable at ≤40% floor
- **D4c:** trigger separate methodology review of RETRIEVAL substrate (independent of Phase-0.5 router scope)

### D5 — Draft verdict option

- **D5A:** Route methodology back for §2.2 revision (highest-integrity)
- **D5B:** Continue Phase-1 dogfood universally (classifier authority, R1 advisory-only covers retrieval failure)
- **D5C:** Phenotype-partial router (continue for COUNT/IDENTITY/SELF-REFERENCE, exclude CONCEPTUAL/DISCOVERY meta)
- **D5D:** Shelve Phase-1 router — 0% retrieval-strict-hit says retrieval-quality is the bottleneck, not routing

**Claude+Rigby joint recommendation:** D5A (route methodology back). The finding is materially load-bearing enough that codifying the resolution properly before Phase-1 proceeds is highest-integrity. D5C is defensible under §2.2 middle-band once phenotype hierarchy is Chris-defined.

## §4 — What Chris needs to do

Route your D-verdict for D1/D2/D3/D4/D5 back via Chat UI (five decisions or a compound one). Silent adaptation of §2.2 without your D-verdict is a constitutional violation per §10.4.

## §4a — Chris D-verdicts RATIFIED (2026-07-19 S2825)

Chris ratified all five D-verdicts + one additional refinement. Verbatim ratifications below (see also `docs/research/implementation/RATIFICATION_2026-07-19_s2825_phase0_5_harvest.md` if opened as a separate ratification envelope).

**Chris framing (verbatim, load-bearing):**

> "The important outcome of S2825 is not that the router 'passed' or 'failed.' It is that the constitutional process exposed a methodological weakness before the platform could make a misleading claim. That is a successful experiment."

> "The biggest discovery from S2825 is not classifier accuracy. It is that a classifier can appear reasonably accurate while authoritative retrieval is completely inadequate. That distinction is now constitutionally visible. That is exactly the kind of false confidence this platform exists to prevent."

### §4a.1 D1 — §2.2 hierarchy: RATIFIED

- Aggregate classifier accuracy is **diagnostic only**.
- Aggregate results may NOT override a load-bearing failure in a required query phenotype or in strict retrieval.
- Revised methodology must explicitly define: (1) required query phenotypes, (2) whether viability is per-phenotype or aggregate rule, (3) hierarchy between those metrics.
- Until that exists, aggregate "continue" cannot mask a NOT-viable phenotype.

### §4a.2 D2 — T2 cap (0.30): RATIFIED WITH REFINEMENT

- T2 integrity stop behaved correctly and remains in force.
- **Methodology** requires review (not necessarily the cap value).
- **Do NOT silently increase or decrease the threshold.**
- Future evidence must separately determine whether: (a) classifier lacks coverage, (b) cap remains global, (c) style/phenotype-aware interpretation warranted.
- Any cap change requires **separate evidence and ratification**.

### §4a.3 D3 — INTEGRITY_STOP counting: RATIFIED

- Rows occurring after integrity stop are **UNMEASURED for classifier/retrieval accuracy**.
- Remain part of integrity evidence; reported separately.
- Do NOT belong in primary accuracy denominator.
- Q27 + Q28 confirmed UNMEASURED per this ratification.

### §4a.4 D4 — Retrieval admissibility: RATIFIED

- **Strict retrieval accuracy is LOAD-BEARING.**
- A router that correctly classifies a question but retrieves the wrong authoritative document **has not succeeded**.
- Future methodology must separately measure three stages, each with independent success criteria:
  1. Query-family classification
  2. Substrate recommendation
  3. Authoritative top-1 retrieval

### §4a.5 D5 — Verdict: RATIFIED Option A

- **Revise §2.2 methodology.**
- Do NOT proceed with universal rollout.
- Do NOT proceed with phenotype-partial rollout.
- **Router flag stays OFF** until revised methodology is SIGN reviewed AND ratified.

### §4a.6 Additional ratification — phenotype rename

- "Chris-style" is the wrong framing (Rigby S2825 Q5 refinement CONFIRMED by Chris).
- **Rename to: a query phenotype representing conversational, context-dependent, conceptual/discovery questions.**
- Working label pending methodology revision authoring: **`CONVERSATIONAL_META`** (final label subject to methodology-revision SIGN).
- The finding is about a class of natural-language queries — not about any individual operator.

## §5 — Full evidence

See `docs/research/discovery_layer/PHASE_0_5/measurement_report.md` for:
- Full per-row classifier decisions + retrieval top-1 files
- Full Rigby SIGN record (5 questions, 4 F-BLOCKING refinements applied)
- Per-family and per-operator-style breakdowns
- Comparison to Phase-0 baseline
- §7 what-worked/what-to-fold/anti-patterns (methodology-teaches per Playbook §11.3)

---
title: "S2823 Phase-0.5 Constitutional Package B1+B3+B2 D-RATIFIED (2026-07-18)"
status: active (frozen at close cascade merge per PLAYBOOK-6.10.9)
authority: ratification-record
session_added: 2823
ratification_date: 2026-07-18
ratifier: chris
routing: |
  chris-chat-ui direct D-verdicts across three artifacts same-session:
  B1 D-RATIFY (turn ~14) after Rigby SIGN 11 refinements + 0 F-BLOCKING;
  B3 D-RATIFY (turn ~18) after Rigby SIGN 15 refinements + 0 F-BLOCKING + Q4 substrate correction;
  B2 D-RATIFY (turn ~28) after Rigby SIGN 3-round 22 refinements + 2 F-BLOCKING both cleared.
scope: |
  Phase-0.5 constitutional-package ratification: BALANCED_P1_HARVEST_PLAN §10
  D-RATIFIED (3 ratifications R1-R3 + §10.4 evidence-integrity discipline
  LOAD-BEARING) + ABSTAIN_POLICY_PROPOSAL §10 D-RATIFIED (5 ratifications R1-R5
  + 2 Chris reframings: "measurement window" vs "session" + "durable persistence
  not ephemeral logs") + ROUTER_SCAFFOLDING_DESIGN §15 D-RATIFIED (7 ratifications
  R1-R7 + R2 elevation of "measurement window" to CANONICAL UNIT OF OBSERVATION
  + R6 epistemic-integrity elevation "post-hoc conclusions must never be presented
  as runtime facts" + R7 constitutional-package framing).

  Ratifies: B1 harvest plan + B3 abstain policy + B2 router scaffolding design
  as coherent constitutional single arc.
  Authorizes: B2 build execution per §13 spec at S2824+ under R1-R7 constraints.
  Does NOT authorize: any implementation that changes retrieval behavior, weakens
  no-fusion discipline, weakens evidence persistence, bypasses integrity-stop
  rules, or expands instrumentation beyond kb_tool.semantic_search (each requires
  new SIGN + new D-verdict).
serves_arc: |
  Phase-0.5 Discovery-Layer Routing Feasibility arc (opened S2823; continuation
  of Group 2700 §8 item #1 discovery-layer sub-arc; Phase-0 methodology validated
  at S2822 with Chris OPTION A-DUAL D-verdict).
predecessor_envelopes:
  - docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md
  - docs/research/implementation/RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md
  - docs/research/implementation/RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md
  - docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md
  - docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md
ratified_artifacts:
  - docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md   # B1 (§10 D-RATIFIED)
  - docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md    # B3 (§10 D-RATIFIED)
  - docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md  # B2 (§15 D-RATIFIED)
related:
  - docs/handoffs/SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md
  - docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md
  - docs/research/OPEN_ARCS.md
  - docs/RETRIEVAL_ASSUMPTIONS.md
---

# S2823 Phase-0.5 Constitutional Package Ratification — B1 + B3 + B2

## §1 — Ratification summary

Three Chris D-verdicts same-session ratifying the Phase-0.5 constitutional package:

| Artifact | Turn | Ratifications | Rigby SIGN | Refinements | F-BLOCKING |
|---|:---:|:---:|:---:|:---:|:---:|
| **B1** BALANCED_P1_HARVEST_PLAN | ~14 | R1-R3 + §10.4 discipline | 1 cycle | 11 | 0 |
| **B3** ABSTAIN_POLICY_PROPOSAL | ~18 | R1-R5 + 2 Chris reframings | 1 cycle | 15 | 0 |
| **B2** ROUTER_SCAFFOLDING_DESIGN | ~28 | R1-R7 + R2 elevation + R6 elevation | 3-round | 22 | 2 (both cleared) |
| **Total** | — | **15 ratifications + 4 elevations** | **4 SIGN cycles** | **48 refinements** | **2 F-BLOCKING both cleared same-session** |

Chris R7 framing at B2: **"B1, B2, and B3 now form a coherent constitutional package. Build authorization is granted only within the documented advisory-only constraints."**

## §2 — Chris D-verdict text (verbatim as-recorded)

Refer to the following sections of the ratified artifacts for the verbatim D-verdict text (this envelope IS the durable record; the artifacts are canonical):

- **B1 §10** in `docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md` — R1/R2/R3 + §10.4 evidence-integrity directive
- **B3 §10** in `docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md` — R1/R2/R3/R4/R5 + §10.6 two Chris reframings + §10.7 downstream discipline
- **B2 §15** in `docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md` — R1/R2/R3/R4/R5/R6/R7 + §15.2 canonical-unit elevation + §15.6 epistemic-integrity elevation + §15.7 constitutional-package framing

Per PLAYBOOK-6.10.9, this envelope records the ratifications as recorded in the artifacts; verbatim chat transcript is not tool-recoverable, so "as recorded" is the discipline used (matches S2822 §7.2 Q1 refinement).

## §3 — R1 provenance discipline (S2823 = trigger 2 for Playbook v0.10 candidate)

S2822 shipped R1 provenance discipline as methodology-outcome-primary framing (trigger 1). S2823 §10.4 elevated evidence-integrity discipline to LOAD-BEARING (trigger 2 candidate).

**Discussion:** these are related but distinct patterns:
- S2822 R1 = provenance-tier hierarchy (real / observed-failure / synthetic-with-gap-tag) as scientific discipline for benchmark corpora
- S2823 §10.4 = evidence-integrity discipline (stop + document + route back to SIGN if findings challenge ratified assumptions) as anti-silent-adaptation guardrail

Both address the same broader concern: preventing "the experiment adapts silently to preserve conclusions" failure mode. Per §20 two-triggers rule, both are candidates for Playbook v0.10 amendment. Recommended: propose them as sibling amendments (R1 provenance discipline for corpus authoring + §10.4 evidence-integrity for arc execution) at Playbook v0.10 authoring.

Recorded here for future reference; NOT authorizing v0.10 amendment this session (would require separate arc).

## §4 — Rigby joint SIGN cycles (4 total)

### §4.1 B1 SIGN cycle (turn ~10)

Executed via pin `pa-d63796dde6404d0f` label `s2823-phase0-5-dual-track`. 8 tool_runs verified against field_dictionary.md, envelope RATIFICATION_2026-07-18_s2822, corpus.json, bridge §5.3. Verdicts: Q1/Q2/Q3/Q5 AGREE-with-refinements-N + Q4 AGREE. 11 refinements applied. Detail in B1 §9.

### §4.2 B3 SIGN cycle (turn ~16)

5 tool_runs verified against measurement_report.md, S2822 envelope §7.2+§9+§11, classifier_a.py (categorical substrate discovery source), BALANCED_P1_HARVEST_PLAN §10 (ratified predecessor). Verdicts: Q1/Q2/Q3/Q5/Q6 AGREE-with-refinements-N + Q4 DISAGREE-as-parameterized/AGREE-as-intent (substrate correction). 15 refinements including §3 categorical rewrite + §7 predeclared trigger list. Detail in B3 §6.

### §4.3 B2 SIGN cycle 1 (turn ~22)

4 tool_runs verified against ABSTAIN_POLICY_PROPOSAL §10, td_handlers_ops.py:5905+5877+~6011, core/settings.py feature-flag patterns. Verdicts: Q1/Q2/Q3/Q4/Q6 AGREE-with-refinements-N + Q5 F-BLOCKING (numeric-leak + wrong-key + no-versioning). 19 refinements + F-BLOCKING fixes. Detail in B2 §14.

### §4.4 B2 SIGN cycle 2 confirmation (turn ~25 + ~27)

Cycle 2 first return: NOT CLEAR (advisory-vs-execution boundary catch on `_parallel_both`). Fixed with CRITICAL SCOPE DISTINCTION block. Cycle 2 second return: CLEAR + 1 non-blocking §1 consistency nit applied. Total 22 refinements across B2 SIGN + 2 F-BLOCKING both cleared. Detail in B2 §14.4-§14.5.

**Anti-rubber-stamp discipline across all 4 rounds:** PASSED. 12+ tool_runs total. Two F-BLOCKING catches (Q5 numeric-leak + cycle-2 advisory-vs-execution) prevented drift-vector shipments — validates B3 §10.7 downstream discipline empirically same-session.

## §5 — Folds persisted at close cascade per PLAYBOOK-6.10.8

13 substantive folds A-M documented in handoff §6.1 + 1 additional Chris-framing fold N (constitutional-package pattern). Ledger persistence to `logs/zoom_out_classifications.jsonl` at close cascade. Pre-close row count: 131. Post-close expected: ~145 (131 + 14 folds).

### §5.1 Fold classification summary

| Fold | Type | Subject |
|---|---|---|
| A | same_pr_actionable | B1 Q1 R1 scoring-definition freeze |
| B | same_pr_actionable | B1 Q1 R2 automatic middle-band extension |
| C | same_pr_actionable | B1 Q2 R2 stabilization intuition (n≈8-10) |
| D | future_trigger | Chris §10.4 evidence-integrity LOAD-BEARING elevation |
| E | same_pr_actionable | B3 Q4 categorical-vs-numeric substrate correction |
| F | same_pr_actionable | B3 Q6 C4 predeclared §10.4 trigger list |
| G | future_trigger | Chris "measurement window" (not "session") reframing |
| H | future_trigger | Chris "durable persistence not ephemeral logs" reframing |
| I | same_pr_actionable | B2 Q5 F-BLOCKING (numeric-leak + wrong-key + no-versioning) |
| J | same_pr_mitigatable | B2 cycle-2 advisory-vs-execution `_parallel_both` catch |
| K | future_trigger | Chris R6 runtime-vs-post-hoc epistemic-integrity elevation |
| L | same_pr_mitigatable | B2 Q4 4-class trigger classification pattern |
| M | same_pr_actionable | A3 pointer-discipline broken finding (Chris R3 preserve — folded no fix) |
| N | future_trigger | Chris R7 constitutional-package framing as reusable arc-shape |

**future_trigger folds (D/G/H/K/N):** 5 folds that may seed future Playbook amendments if pattern recurs in additional arcs. Recorded for cross-arc observation without silent action.

## §6 — Non-goals reinforced (constitutional package binds all three)

- NO DISCOVERY fixes during Phase-0.5 (per Chris R3 preserve)
- NO routing implementation as production decision path (per Chris R2 advisory-only)
- NO taxonomy constitutionalization (per Chris R6)
- NO context-feature classifier revision
- NO RRF or global fusion (per Chris R6)
- NO patch to frozen lexical top_k policy (per S2820)
- NO auto-adopt semantic default flip (per S2821)
- NO parallel-both execution in Phase-0.5 (per B2 R1 — LOGGED as advisory but NOT executed)
- NO numeric confidence thresholds without numeric classifier scorer (per B2 §12 T1 integrity stop trigger)
- NO ephemeral-logs-only instrumentation (per B3 §10.6.2 durable persistence)
- NO opportunistic adjacent-tool instrumentation (per B2 §3 deferred-adjacency SIGN gate)
- NO weakening of any R1-R7 rule via implementation (per Chris R7 downstream discipline)

## §7 — S2824 arc direction (build phase authorized)

Per Chris R7 build authorization: implementation lands as a single PR at S2824+ per B2 §13 build-gate spec. Contract:

1. `core/services/phase_0_5_router.py` new module
2. `core/settings.py` PHASE_0_5_ROUTER_ENABLED + PHASE_0_5_MEASUREMENT_WINDOW enum
3. `core/services/td_handlers_ops.py:5905` flag-guarded instrumentation
4. `Phase0_5RouterEvent` Django model + migration
5. `logs/phase_0_5_router.jsonl` initial file
6. `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` committed extraction script
7. `core/tests/test_phase_0_5_router.py` contract tests

**S2824 build execution binds under R1-R7 constraints.** Any implementation weakening = SIGN + new D-verdict per Chris R7 downstream discipline.

## §8 — Reopen triggers

This envelope is reopened for amendment if:
- Chris explicitly requests amendment via subsequent D-verdict
- B2 build phase surfaces implementation-shape findings that materially challenge R1-R7 (per B1 §10.4 evidence-integrity discipline)
- Any of the 5 §12 T1-T5 runtime abort triggers fires during Phase-0.5 dogfood execution
- A future arc corroborates any of the 5 future_trigger folds (D/G/H/K/N) → sibling amendment opens

## §9 — Governance-plane record

- Envelope authored: 2026-07-18 S2823 close cascade
- Envelope frozen: at close cascade PR merge per PLAYBOOK-6.10.9
- Twin-pointer workspace deliverable: DEFERRED per S2818-S2822 pattern (envelope stays in `docs/research/implementation/` as authoritative; workspace mirror at Phase-0.5 arc close)
- Reference in `docs/research/OPEN_ARCS.md` Phase-0.5 row: this envelope path
- Reference in CLAUDE.md: no immediate refresh needed (Playbook v0.8.0 unchanged; anchor block updated at post-Phase-0.5 close per bridge §4.3 deferrals)

---

**End of S2823 constitutional-package ratification envelope. B1+B3+B2 D-RATIFIED as coherent single arc under Chris R7 constitutional-package framing. Build authorization GRANTED for S2824+ under R1-R7 constraints.**

# Session 2823 — Phase-0.5 Arc Opened + Triple Chris D-Verdict on B1+B3+B2 Constitutional Package + Advisory-Only Router Design Cleared

**Date:** 2026-07-18 (direct successor to S2822 Phase-0 methodology validation)
**Session:** S2823
**PRs shipped:** 1 close cascade PR (SHA at merge; docs + design deliverables + governance envelope; no runtime code change — build authorized but deferred to S2824)
**Predecessor:** [SESSION_2822_PHASE0_EXECUTION_OPTION_A_DUAL](SESSION_2822_PHASE0_EXECUTION_OPTION_A_DUAL.md)
**Bridge:** [SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE](SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md) (required-reading executed dual-track per §5)
**Playbook:** v0.8.0 (205 rules) — unchanged (Playbook v0.9 amendment remains at 10/10 trigger; not amended this session)
**Recycle cycle:** 0 in-session + 1 close-cascade recycle post-merge (PLAYBOOK-7.4.4)

---

## §1 — Ship summary

Full dual-track execution per bridge §5. Track A ~30% /docs/ audit reconnection + Track B ~70% Phase-0.5 evidence collection. **Phase-0.5 arc OPENED** with a **triple Chris D-verdict constitutional package** (B1 + B3 + B2 all ratified in-session with 22+ Rigby-SIGN-driven refinements across 4 SIGN cycles + 2 F-BLOCKING catches + 3 substrate corrections).

**Deliverables shipped as docs (build gate authorized but implementation deferred to S2824 per design-vs-implementation separation discipline):**

- `docs/research/OPEN_ARCS.md` — modified: Phase-0.5 arc added to In-progress; Group 2700 moved to Closed (canonical summary 2799); preamble refresh acknowledging 20-session drift explicitly
- `docs/RETRIEVAL_ASSUMPTIONS.md` — new skeleton: 4 findings from bridge §1 with "Phase-0.5 evidence pending" placeholders; full v1 authoring deferred post-Phase-0.5
- `docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md` — new: draft → Rigby SIGN (11 refinements, 0 F-BLOCKING) → Chris D-verdict RATIFY with §10.4 evidence-integrity discipline elevated to LOAD-BEARING
- `docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md` — new: skeleton → Rigby SIGN (15 refinements, 0 F-BLOCKING, 1 substrate correction Q4 categorical-vs-numeric) → Chris D-verdict RATIFY with "measurement window" + "durable persistence not ephemeral logs" reframings
- `docs/research/discovery_layer/PHASE_0_5/ROUTER_SCAFFOLDING_DESIGN.md` — new: design-spec → Rigby SIGN 3-round (22 refinements, 2 F-BLOCKING both cleared) → Chris D-verdict RATIFY under R1-R7 constraints with "runtime checks must only evaluate signals actually observable at runtime" epistemic-integrity elevation

**Chris D-verdict framing (across all three):** the constitutional package B1+B3+B2 forms a coherent single-arc architecture. Build authorization granted only within the documented advisory-only constraints. Any implementation that changes retrieval behavior, weakens no-fusion discipline, weakens evidence persistence, bypasses integrity-stop rules, or expands instrumentation beyond the ratified surface must return through SIGN and a new D-verdict.

**Governance envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md` — frozen at close cascade merge per PLAYBOOK-6.10.9. Single envelope covering all three D-verdicts + methodology-outcome reframings + Rigby SIGN cycle records + Chris R1-R7 verbatim + fold classifications.

---

## §2 — Rigby joint SIGN — FOUR major SIGN cycles

**Pin:** `pa-d63796dde6404d0f` label `s2823-phase0-5-dual-track` (S2823 open fresh mint after S2822 pin `pa-fac188f02db24fcc` retired force=true, fifty-third consecutive per S2770+ pattern).

### §2.1 B1 SIGN cycle (turn ~10)

5 SIGN questions on stop-condition bands / balance targets / harvest sources / labeling discipline / zoom-out. Rigby AGREE-with-refinements across Q1/Q2/Q3/Q5 + AGREE-clean Q4. 0 F-BLOCKING. 8 tool_runs (anti-rubber-stamp PASSED). 11 refinements applied same-session including §2.1 Scoring Definition FROZEN block + §2.2 automatic-extension middle-band rule + §3.3 two-view accuracy reporting.

### §2.2 B3 SIGN cycle (turn ~16)

6 SIGN questions on AMBIGUOUS/UNCLASSIFIABLE/CONTEXT_NEEDED policies + confidence thresholds + instrumentation + zoom-out. Rigby AGREE-with-refinements across Q1/Q2/Q3/Q5/Q6 + **DISAGREE (as parameterized)/AGREE (as intent) on Q4**. 0 F-BLOCKING. 5 tool_runs. 15 refinements including:

- **CRITICAL Q4 substrate correction:** classifier_a.py emits categorical HIGH/MEDIUM/LOW confidence, NOT numeric. Original v0 numeric thresholds (≥0.70 / 0.15 / 0.35) were unimplementable. §3 rewritten as §3.1 categorical routing rules + §3.2 numeric-thresholds-DEFERRED.
- **Q6 C4 predeclared §10.4 evidence-integrity trigger list** — operationalizes Chris §10.4 "stop, document, route back to SIGN" directive with 5 concrete triggers.

### §2.3 B2 SIGN cycle 1 (turn ~22)

6 SIGN questions on single-call-site scope + measurement window transitions + hybrid durable persistence + T1-T5 runtime aborts + envelope contract + zoom-out. Rigby AGREE-with-refinements across Q1/Q2/Q3/Q4/Q6 + **F-BLOCKING on Q5** (three §7 envelope issues: numeric-confidence leak + wrong `results` key vs actual handler `chunks` + no versioning). 4 tool_runs. 19 refinements + F-BLOCKING fixes applied same-session.

### §2.4 B2 SIGN cycle 2 confirmation (turn ~25 + ~27)

Cycle 1 fixes dispatched for confirmation. Cycle 2 first return: **NOT CLEAR** — Rigby caught that my §7 `_parallel_both` envelope shape IMPLIED executing parallel retrieval, which would violate the advisory-only guardrail. Fixed with explicit CRITICAL SCOPE DISTINCTION block: B3 policy vs B2 advisory-only-execution boundary; `_parallel_both` field ALWAYS NULL in Phase-0.5; reserved-shape data contract preserved for future Phase-1+ ratification only. §12 T4 scoped as INACTIVE in Phase-0.5.

Cycle 2 second return: **CLEAR** + 1 non-blocking §1 consistency nit applied same-turn.

**Anti-rubber-stamp discipline:** PASSED across all 4 SIGN rounds. 12+ tool_runs verified against ABSTAIN_POLICY_PROPOSAL.md §10, td_handlers_ops.py:5905, core/settings.py feature-flag patterns, classifier_a.py source-of-truth for categorical confidence, and all three Phase-0.5 design docs. Two F-BLOCKING catches (Q5 numeric-leak + cycle-2 advisory-vs-execution) prevented drift-vector shipments — exactly the discipline Chris B3 §10.7 was written to enforce.

---

## §3 — Chris D-verdict framings (three ratifications, seven refinement patterns)

### §3.1 B1 D-verdict (turn ~14) — three ratifications + evidence-integrity discipline elevation

R1 §2.1 Scoring Definition + R2 §2.2 Stop-Condition Bands with automatic-middle-band + R3 §3 Balance Targets with two-view reporting. Additional directive §10.4: **"If execution uncovers findings that materially challenge ratified assumptions, stop, document the evidence, and route the methodology back for SIGN rather than silently adapting the experiment."** LOAD-BEARING. Ratified as the discipline that prevented the Q4 categorical-vs-numeric drift-shipment at B3.

### §3.2 B3 D-verdict (turn ~18) — five ratifications with two Chris reframings

R1 AMBIGUOUS (c) with fusion-by-UX-violates-R6 + R2 UNCLASSIFIABLE (d) with mandatory logging + R3 CONTEXT_NEEDED (a) with UX budget + R4 categorical-only with substrate correction + R5 predeclared triggers as BINDING.

**Chris reframings:**
- "measurement window" (not "session") for R3 clarify-cap flip rule — different scope, LOAD-BEARING
- "durable persistence location + defined extraction path — ephemeral logs alone are insufficient" — tightens §4.1 to require model-mirror or committed extraction script beyond JSONL

**Downstream discipline:** "No router build may weaken the ratified no-fusion, abstention, evidence-persistence, or integrity-stop rules." Chris explicit — binds B2 design under §10.7.

### §3.3 B2 D-verdict (turn ~28) — seven ratifications with epistemic-integrity elevation

R1 advisory-only boundary + R2 measurement windows as CANONICAL UNIT OF OBSERVATION + R3 single instrumentation surface + R4 durable evidence with divergence-integrity-event + R5 advisory contract additive-non-breaking + R6 integrity triggers with runtime-vs-post-hoc boundary + R7 build authorization within R1-R6 constraints.

**Chris epistemic-integrity elevation (R6):** "Runtime checks must only evaluate signals that are actually observable at runtime. **Post-hoc conclusions must never be presented as runtime facts.**" This elevates the T4/T5 window-level triggers to require observable runtime proxies OR downgrade to Class D post-hoc-only. Novel epistemic-integrity discipline candidate for future Playbook amendment observation.

**Chris R2 elevation to CANONICAL UNIT OF OBSERVATION:** "The measurement window becomes the canonical unit of observation." Stronger than "used for scoping." Measurement window is now the fundamental Phase-0.5 analysis primitive — supersedes session as unit.

**Chris R7 constitutional-package framing:** "B1, B2, and B3 now form a coherent constitutional package. Build authorization is granted only within the documented advisory-only constraints."

---

## §4 — Novel precedent

1. **First triple-D-verdict same-session ratification in the discovery-layer arc.** B1 + B3 + B2 all ratified in S2823 with an explicit constitutional-package framing by Chris (R7). Prior arcs typically shipped 1-2 ratifications per session.
2. **First 4-round Rigby SIGN cycle with 2 F-BLOCKING catches both cleared same-session.** B2 SIGN went cycle 1 F-BLOCKING → fix → cycle 2 NOT CLEAR (new issue caught in confirmation re-read) → fix → cycle 2 CLEAR. Novel iterative-integrity pattern.
3. **First Rigby F-BLOCKING that caught a Chris-discipline weakening in a subsequent draft.** Cycle-2 catch: my `_parallel_both` envelope shape would have weakened R2 advisory-only guardrail. This is exactly the drift-vector Chris §10.7 discipline was written to prevent — and Rigby caught it via tool-verify without needing Chris to catch it.
4. **First substrate-reality correction via SIGN (Q4 categorical-vs-numeric).** Classifier_a.py emits categorical HIGH/MED/LOW, not numeric. v0 numeric thresholds (≥0.70/0.15/0.35) were unimplementable. Rigby caught via `repo_tool.read_file` on classifier_a source. First arc where SIGN corrected an unimplementable spec via substrate verification.
5. **First Chris D-verdict elevating a scoping term to "canonical unit of observation."** R2 measurement window elevation is a stronger constitutional-framing pattern than prior "use X for scoping" directives.
6. **First Chris D-verdict codifying runtime-vs-post-hoc epistemic integrity.** R6: "Post-hoc conclusions must never be presented as runtime facts." Novel epistemic-integrity discipline; candidate for Playbook amendment observation.
7. **First multi-turn Rigby "advisory-only" enforcement that prevented spec drift into execution.** Rigby cycle-2 catch on `_parallel_both`. Building on B3 §10.7 discipline; validates the "downstream rules bind subsequent designs" pattern.
8. **First same-session 22-refinement SIGN cycle across 3 Rigby rounds on a single design doc (B2).** Prior max was ~10 refinements per doc. Iterative pressure-testing with F-BLOCKING resolution scaled cleanly.

---

## §5 — What shipped vs what didn't

**Shipped (as docs + design + governance envelope; no runtime substrate change):**
- Phase-0.5 arc opened in OPEN_ARCS with new In-progress row + Group 2700 closed
- 3 new Phase-0.5 working-directory design docs (BALANCED_P1_HARVEST_PLAN + ABSTAIN_POLICY_PROPOSAL + ROUTER_SCAFFOLDING_DESIGN) all Rigby-SIGN-cleared + Chris-D-verdict-ratified
- RETRIEVAL_ASSUMPTIONS.md skeleton with 4 Phase-0 findings as forward-looking placeholders
- Governance envelope with all three D-verdicts + methodology-outcome framings + all 4 Rigby SIGN cycles + 22+ refinement records + Chris R1-R7 verbatim + fold classifications
- A3 pointer-chunk retrievability probe with substrate-observation fold (POINTER DISCIPLINE BROKEN for 3/4 natural queries)

**Not shipped (build authorized, deferred to S2824):**
- `core/services/phase_0_5_router.py` module
- `core/settings.py` PHASE_0_5_ROUTER_ENABLED + PHASE_0_5_MEASUREMENT_WINDOW flag additions
- `core/services/td_handlers_ops.py:5905` handler diff (flag-guarded instrumentation)
- `Phase0_5RouterEvent` Django model + migration
- `logs/phase_0_5_router.jsonl` initial file
- `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` committed extraction script
- Contract-level tests in `core/tests/test_phase_0_5_router.py`
- Balanced P1 harvest execution (blocked pending build)

**Explicit non-goals held (Chris R3+R6 preserved):**
- NO DISCOVERY fixes during Phase-0.5 (A3 finding folded as substrate observation, NOT fixed)
- NO routing implementation as production decision path (advisory-only per R2)
- NO taxonomy constitutionalization
- NO context-feature classifier revision
- NO RRF or global fusion
- NO patch to frozen lexical top_k policy
- NO auto-adopt semantic default flip
- NO opportunistic instrumentation of adjacent retrieval tools

---

## §6 — Ledger + provenance + folds

- **Zoom-out ledger:** `logs/zoom_out_classifications.jsonl` — 131 rows at S2823 open; folds A-M documented in envelope §5 (13 additional folds from S2823 SIGN cycles + A3 finding). Post-close: ~144 rows expected.
- **Recycle log:** `logs/recycle_events.jsonl` — 0 in-session + 1 close-cascade recycle post-merge per PLAYBOOK-7.4.4.
- **Freshness log:** `logs/session_freshness.jsonl` — grew by 1 at S2823 open (FRESH verdict).
- **Baseline HEAD:** `5695896f8` (S2822 close cascade).
- **Ratification HEAD:** (filled at S2823 close cascade merge).

### §6.1 S2823 folds persisted (arc-close per PLAYBOOK-6.10.8)

- **Fold A (same_pr_actionable):** Rigby B1 Q1 R1 metric-precision refinement — scoring definition frozen prevents band-boundary manipulation; general discipline for any classifier viability arc.
- **Fold B (same_pr_actionable):** Rigby B1 Q1 R2 automatic-middle-band extension rule — deterministic band interpretation prevents either-or menu.
- **Fold C (same_pr_actionable):** Rigby B1 Q2 R2 stabilization-intuition (n≈8-10 per style) — statistical discipline for small-sample per-tier analysis.
- **Fold D (future_trigger):** Chris §10.4 evidence-integrity directive LOAD-BEARING elevation — "stop + document + route back to SIGN" if findings challenge ratified assumptions. First arc where Chris explicitly declared evidence-integrity discipline. Potential Playbook amendment candidate if pattern recurs.
- **Fold E (same_pr_actionable):** Rigby B3 Q4 substrate correction (categorical-vs-numeric) — validates §10.4 discipline via same-session catch; classifier_a substrate reality forced spec rewrite; drift-vector prevented.
- **Fold F (same_pr_actionable):** Rigby B3 Q6 C4 predeclared trigger list operationalizing §10.4 — first predeclared list turning interpretive discipline into concrete triggers.
- **Fold G (future_trigger):** Chris B3 R3 "measurement window" (not "session") reframing — different scope than session; supersedes session as unit of observation at B2 R2 elevation. Novel constitutional-vocabulary pattern.
- **Fold H (future_trigger):** Chris B3 R4+R5 "durable persistence not ephemeral logs" reframing — tightens instrumentation from JSONL-only to hybrid or committed-script mandatory. Downstream binding for future retrieval-instrumentation arcs.
- **Fold I (same_pr_actionable):** Rigby B2 SIGN cycle 1 Q5 F-BLOCKING catch (numeric-leak + wrong-key + no-versioning in §7 envelope example) — Q6 C1 "spec examples showing numeric confidence invite drift" observation; prevents "just implement the doc" failure mode.
- **Fold J (same_pr_mitigatable):** Rigby B2 SIGN cycle 2 catch (advisory-vs-execution boundary in `_parallel_both`) — my draft would have weakened advisory-only guardrail; Rigby caught in confirmation re-read. Validates iterative SIGN-plus-confirmation pattern.
- **Fold K (future_trigger):** Chris B2 R6 runtime-vs-post-hoc epistemic-integrity elevation — "post-hoc conclusions must never be presented as runtime facts." Novel epistemic-integrity discipline; strong Playbook amendment candidate if applied in 1 more arc.
- **Fold L (same_pr_mitigatable):** Rigby B2 Q4 R1+R2+R3 4-class trigger classification — abort trigger typology (per-event / window-level / observable-proxies / post-hoc-fallback) — reusable pattern for future runtime-instrumentation designs.
- **Fold M (same_pr_actionable):** A3 pointer-chunk finding — CLAUDE.md #6 not retrievable for 3/4 natural pointer-shape queries. Substrate observation; Chris R3 preserve holds; folded as evidence for future /docs/ restructuring arc without action.

**Additional secondary observation:** search_docs `max_chars=2000` truncates k=3 to k=2 in practice. Not folded (implementation observation not covered by Phase-0.5 scope).

**Chris methodology-outcome framing carrying forward:**
- **Fold N (future_trigger):** Constitutional-package framing (B1+B3+B2 coherent single arc) — first Chris explicit "constitutional package" framing. If pattern recurs in future multi-artifact arc, candidate Playbook §11 template extension.

---

## §7 — Candidates for S2824

**Sole recommended direction (build phase — CHRIS AUTHORIZED under R1-R7 constraints):**

1. **⭐ Execute B2 build per §13 spec** — Single PR containing:
   - `core/services/phase_0_5_router.py` new module (categorical routing + abstain policy + instrumentation dispatch)
   - `core/settings.py` diff (PHASE_0_5_ROUTER_ENABLED + PHASE_0_5_MEASUREMENT_WINDOW enum defaults)
   - `core/services/td_handlers_ops.py:5905` handler diff (flag-guarded pre-search instrumentation call)
   - `Phase0_5RouterEvent` Django model + migration (per B3 §10.6.2 durable persistence)
   - `logs/phase_0_5_router.jsonl` initial empty file
   - `docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py` committed extraction script
   - Contract tests: `core/tests/test_phase_0_5_router.py` — off-behavior guarantee + advisory-only invariant + `_parallel_both` null-in-Phase-0.5 invariant + event_id idempotency + all 4 trigger classes
   - Handoff + envelope

**Available if Chris pivots:**

- Balanced P1 harvest execution per B1 §6 (blocked on build — implementation dispatch runs harvest against instrumented endpoint)
- A3 pointer-discipline fix (would require Chris R3 re-open — currently preserved)
- Colorado Phase 4 statute-citation content quality
- BettingPage first-user trace
- Stock Intelligence end-to-end verify
- Playbook v0.9 amendment authoring (10/10 triggers, well past codification threshold)
- Playbook v0.10-candidate R1 provenance discipline (now 2/2 triggers post-S2823 — S2822 methodology-outcome framing + S2823 §10.4 evidence-integrity elevation both instances)
- Playbook v0.11-candidate epistemic-integrity discipline (1 trigger — Chris R6 runtime-vs-post-hoc elevation; watch for second)

**Recommended default:** Item #1 build execution.

---

## §8 — S2823 lessons to carry

1. **Multi-round SIGN with F-BLOCKING catches is scalable and productive.** B2 went 3 SIGN rounds catching 2 F-BLOCKING items same-session; both resolved cleanly; final CLEAR verdict + Chris D-verdict. Same-session iterative-integrity pattern is now validated at scale.
2. **Chris §10.4 evidence-integrity discipline paid off same-session.** The Q4 categorical-vs-numeric substrate discovery would have shipped a spec with unimplementable thresholds. §10.4 requires "stop + route back to SIGN"; that discipline is what enabled the recovery. Fold D confirms.
3. **Rigby's tool-verify catches drift-vectors Chris shouldn't need to catch.** Cycle-2 `_parallel_both` catch is exemplary — Rigby caught a discipline-weakening drift in confirmation re-read that Chris explicitly forewarned against in B3 §10.7. This IS the pattern.
4. **Constitutional-package framing scales cleanly.** Chris B2 R7 "B1+B3+B2 form a coherent constitutional package" — 3 ratifications in one session are compatible with careful individual SIGN discipline when each artifact preserves the others' constraints.
5. **Substrate-reality verification is load-bearing at every SIGN cycle.** Q4 categorical-vs-numeric was invisible until Rigby read classifier_a.py source. Every design SIGN routing should include a substrate-reality probe.
6. **Reserved-shape data contracts protect future ratifications.** §7 reserved `_parallel_both` shape lets future Phase-1+ SIGN + Chris D-verdict adopt parallel-both execution without re-designing envelope contract. Chris R7 explicit "any weakening returns through SIGN + new D-verdict" makes reserved shapes safe.
7. **Design-vs-implementation boundary should be preserved.** All three artifacts ratified this session are DESIGN specs; no build ships in same session. Preserves clean audit trail + prevents rushed implementation drift.
8. **A3 pointer-discipline finding validates the bridge deliverable's hypothesis.** Bridge §2.3 flagged pointer-chunk retrievability as spot-check-worthy; A3 confirmed pointer discipline BROKEN for 3/4 natural queries. Feeds Phase-0.5 corpus + validates Track A feedback loop into Track B.

---

**End of S2823 handoff. Discovery-layer arc state: Phase-0.5 OPEN with constitutional package B1+B3+B2 D-RATIFIED. Build authorization GRANTED under R1-R7 constraints. Implementation dispatch begins at S2824 per §7 item #1.**

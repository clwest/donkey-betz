---
title: "Phase-0.5 — Abstain-Policy Proposal (Rigby SIGN cleared — routes to Chris D-verdict)"
status: post-Rigby-SIGN-refined (AGREE-with-refinements across Q1/Q2/Q3/Q5/Q6 + DISAGREE-then-AGREE-with-refinements-as-intent on Q4; 0 F-BLOCKING; 15 refinements applied same-session including Q4 numeric-vs-categorical substrate correction)
authority: draft — LOAD-BEARING once Chris ratifies
session: 2823
generated: 2026-07-18
supersedes: none
related:
  - docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md   # §11 Phase-0.5 arc direction; §9 Chris D-verdict OPTION A-DUAL R4 "context-needed as separate outcome"
  - docs/research/discovery_layer/PHASE_0/measurement_report.md   # Phase-0 §5 context-needed post-hoc analysis
  - docs/research/discovery_layer/PHASE_0_5/BALANCED_P1_HARVEST_PLAN.md   # sister plan doc
  - docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md   # §5.3 B3 abstain-policy fallthrough options
scope:
  Defines the router's abstain-policy proposal — how the advisory-only feature-flag dogfood router behaves when Classifier A cannot produce a confident family+target prediction from query text alone. Three degenerate outcomes covered: AMBIGUOUS, UNCLASSIFIABLE, CONTEXT_NEEDED.
non_goals:
  - Deciding the abstain policy unilaterally (routes to Rigby SIGN then Chris D-verdict)
  - Applying to production router (advisory-only per Chris R2)
  - Extending to non-advisory paths in this arc (Phase-0.5 scope)
  - Substrate code implementation (Track B B2 handles that)
---

# Phase-0.5 Abstain-Policy Proposal

**Skeleton — routes to Rigby joint SIGN post Chris ratification of BALANCED_P1_HARVEST_PLAN scope. Do NOT treat as decided until SIGN cleared + Chris D-verdict RATIFY.**

## §1 — Why abstain policy matters

The Phase-0.5 advisory-only dogfood router (per envelope §11.2 step 3 + Chris R2) uses Classifier A to predict `intended_family` and route to a substrate. But Phase-0 evidence surfaced three failure modes where routing-from-query-text-alone cannot produce a confident answer:

1. **AMBIGUOUS** — query maps to 2+ families with roughly equal plausibility (e.g., "How does the docs cascade work" could be PROCEDURAL — walk me through it — or CONCEPTUAL — explain the concept)
2. **UNCLASSIFIABLE** — query does not map to any family confidently (rare but present: novel operator dialects; hybrid identifier+topic queries)
3. **CONTEXT_NEEDED** — the query is not answerable without additional operator-side context that the classifier cannot infer from text (e.g., "what's the state" — of what? Requires session/task-specific context)

Without an explicit abstain policy, the router silently commits to a substrate choice on low-confidence rows, and the Phase-0.5 measurement report has no way to distinguish "routing worked" from "routing guessed and got lucky."

Chris R4 (envelope §7 refinement) elevated CONTEXT_NEEDED as a SEPARATE outcome (not a routing failure) — this proposal builds on that.

## §2 — Three degenerate outcomes + four fallthrough options each

For each of AMBIGUOUS / UNCLASSIFIABLE / CONTEXT_NEEDED, the router selects one of four fallthroughs. This proposal lays out the options and requests Chris D-verdict on the per-outcome choice.

### §2.1 Fallthrough option catalog

| Code | Name | Behavior | Cost | Risk |
|---|---|---|---|---|
| **(a)** | Clarify with user | Return a clarifying question via Rigby's chat surface: "Did you mean X or Y?" | UX interrupt; adds a turn | User-friction if triggered often |
| **(b)** | Default substrate | Deterministic substrate default per family shape: lexical for HIGH-consequence (COUNT/IDENTITY/SELF-REFERENCE), semantic for CONCEPTUAL, both-in-parallel for DISCOVERY | Zero UX cost; deterministic replay | Silent low-confidence commit; may misroute if default is wrong for outcome shape |
| **(c)** | Parallel retrieval both substrates | Run BOTH lexical + semantic; present union top-k with substrate label | Retrieval cost 2x; UI needs union-view | Union-view may be noisy; requires reranker OR operator disambiguation |
| **(d)** | No action / current-best | Router abstains; falls back to whatever the current tool would have done without routing | Zero cost; "invisible" fallback | Router provides no signal for these outcomes → Phase-0.5 measurement report has fewer rows to evaluate |

### §2.2 AMBIGUOUS

**Recommended default: (c) parallel retrieval both substrates — with strict no-fusion-by-UX discipline.**

Rationale: AMBIGUOUS is where the router most-adds-value if it works: presenting both substrate results side-by-side lets the operator see the difference and disambiguate implicitly. Advisory-only means the operator's actual downstream choice is instrumentation feedback for Phase-0.5 measurement.

**No-fusion discipline (per Rigby SIGN Q1 R1 + Q6 C2 — honors Chris R6 in spirit):**

> Parallel retrieval produces TWO substrate-labeled candidate lists (one lexical, one semantic). The system MUST NOT fuse, rerank, or blend results across the substrates into a single score space or combined ranked feed. Backend keeps lists separate; UI displays them as substrate-separated blocks with explicit labels.

**Union-view guard (per Rigby SIGN Q1 R2):** If a "union view" is presented (e.g., top-3 from each substrate shown together), it MUST include:
- Explicit substrate provenance tag per item (e.g., `[lexical]`, `[semantic]`)
- Deterministic grouping (lexical block first for HIGH-consequence families COUNT/IDENTITY/SELF-REFERENCE; semantic block first for CONCEPTUAL; alternating grouping FORBIDDEN)

Interleaving or a single ranked feed = de facto fusion via UX; violates Chris R6 in spirit and corrupts Phase-0.5 measurement (see §Q6 C2 refinement below in §7).

**Alternative to weigh at Chris D-verdict:** (a) clarify with user — cheaper but adds a turn per ambiguous row.

### §2.3 UNCLASSIFIABLE

**Recommended default: (d) no action / current-best — with mandatory logging discipline (no-op ≠ no-record).**

Rationale: UNCLASSIFIABLE is genuine "the router doesn't have information to help." Silently degrading to current-best behavior (no substrate selection) matches the advisory-only guardrail (per Chris R2) — the router should not force a substrate choice on rows it can't classify. Instrumentation logs the UNCLASSIFIABLE tag for Phase-0.5 measurement analysis (are UNCLASSIFIABLE rows dominant? Rare?).

**Logging discipline (per Rigby SIGN Q2 R1):** UNCLASSIFIABLE events MUST be counted and reported EVEN WHEN the router no-ops. "No action" fallthrough means the router does not alter downstream retrieval — it does NOT mean the router keeps no record. Every UNCLASSIFIABLE occurrence writes a row to `logs/phase_0_5_router.jsonl` with full instrumentation payload per §4.

**Measurement report line item (per Rigby SIGN Q2 R2):** Phase-0.5 measurement report MUST include an UNCLASSIFIABLE analysis section reporting:
- UNCLASSIFIABLE rate by operator style (Chris / Claude / Rigby)
- UNCLASSIFIABLE rate by query length bucket (Phase-0 evidence: real P1 queries were shorter/bare-noun/identifier-heavy per measurement_report §6)

**Alternative to weigh at Chris D-verdict:** (b) default substrate (e.g., semantic as universal fallback) — risks silent misroute + hides the UNCLASSIFIABLE frequency from measurement.

### §2.4 CONTEXT_NEEDED

**Recommended default: (a) clarify with user — with UX budget cap + flip-rule + context-type logging.**

Rationale: Chris R4 explicitly elevated CONTEXT_NEEDED as a separate outcome. Semantically: the router IS confident that no substrate is right without more information. Best expression is asking. The clarifying question surfaces the missing context and lets the operator supply it — the follow-up query then routes normally.

**UX budget cap (per Rigby SIGN Q3 R1):** Clarify-rate soft cap: **≤2 clarify turns per 20 routed queries** OR **≤10% of routed queries trigger clarify**, whichever is lower. Exceeding this cap degrades UX and operators start ignoring the router.

**Flip rule on cap breach (per Rigby SIGN Q3 R2):** If clarify rate exceeds the cap within a session, CONTEXT_NEEDED fallthrough temporarily switches from (a) clarify → (d) no-action **for the remainder of the session**, WHILE STILL LOGGING the CONTEXT_NEEDED tag on every occurrence. This keeps evidence collection intact without killing operational flow.

**Context-type logging (per Rigby SIGN Q3 R3):** Every clarify prompt records which type of context it requested:
- `operational` — task/session state the operator can supply cheaply (e.g., "which arc are we in?")
- `conversational` — prior conversation backscroll the operator would have to reconstruct (e.g., "what were we discussing earlier?")

Phase-0 evidence (measurement_report §4.1) differentiates these; measurement report §NEW abstain-analysis reports operational-vs-conversational clarify ratio to distinguish "cheap" vs "expensive" clarifies.

**Missed-CONTEXT_NEEDED as tracked error mode (per Rigby SIGN Q6 C3):** Because Phase-0 evidence shows CONTEXT_NEEDED often reflects missing OPERATIONAL context (not just pronouns/short queries), a simplistic detector may misclassify these as AMBIGUOUS or UNCLASSIFIABLE. Phase-0.5 measurement report treats "missed CONTEXT_NEEDED" as an explicit error mode — surfaced by post-hoc review of clarify follow-ups + operator-response inspection.

**Alternative to weigh at Chris D-verdict:** (d) no action — doesn't surface the missing context; operator has to figure out that the router couldn't answer.

## §3 — Confidence rules — CATEGORICAL not numeric (per Rigby SIGN Q4 DISAGREE finding + Q6 C1)

**Substrate correction:** `classifier_a.py` emits **categorical** confidence values (`HIGH` / `MEDIUM` / `LOW`) plus `matched_rules`. It does NOT emit numeric confidence scores or top-2 deltas. The original v0 numeric thresholds (≥0.70 commit / 0.15 delta ambiguous / 0.35 unclassifiable) were unimplementable against the actual classifier surface.

### §3.1 Categorical routing rules (Phase-0.5 operating regime)

| Classifier output | Router action |
|---|---|
| `confidence == HIGH` AND `family` is a defined enum (not AMBIGUOUS/UNCLASSIFIABLE/CONTEXT_NEEDED) | **Commit** — route to predicted family's substrate |
| `family == AMBIGUOUS` (classifier explicit signal) | Abstain per §2.2 (parallel-both) |
| `family == UNCLASSIFIABLE` (classifier explicit signal) | Abstain per §2.3 (no-action) |
| `family == CONTEXT_NEEDED` (classifier explicit signal) | Abstain per §2.4 (clarify) |
| `confidence == MEDIUM` AND `family` is defined | **Advisory-only commit** — route substrate but log `commit_confidence=MEDIUM`; downstream Phase-0.5 measurement can slice by this |
| `confidence == LOW` AND `family` is defined | Escalate to §2.3 UNCLASSIFIABLE fallthrough (no-action + log) — LOW confidence is effectively "no meaningful signal" |

### §3.2 Numeric thresholds — DEFERRED (per Rigby SIGN Q4 R2 + Q6 C1)

Numeric thresholds are BLANK. No numeric scoring exists in `classifier_a.py`. Anyone attempting to introduce numeric thresholds without first adding a numeric scorer to the classifier substrate MUST route methodology back to Rigby SIGN per Chris §10.4 evidence-integrity directive (this is a predeclared trigger — see §Q6 C4 trigger list at §7).

### §3.3 CONTEXT_NEEDED detection

CONTEXT_NEEDED is a classifier-level output signal per Chris R4. `classifier_a.py` implementation returns this when query lacks family-recoverable content. The abstain policy consumes the signal — it does NOT re-detect via heuristics. If classifier_a's CONTEXT_NEEDED detection quality is inadequate (surfaced during Phase-0.5 measurement per §2.4 "missed-CONTEXT_NEEDED as tracked error mode"), the fix is at the classifier surface, not in this abstain layer.

## §4 — Instrumentation requirements

Every router decision (commit OR abstain) is logged per envelope §9 R2 with these Phase-0.5 fields (5 total — 5th field added per Rigby SIGN Q5 refinement):

- `abstain_reason` — one of `null` (committed), `AMBIGUOUS`, `UNCLASSIFIABLE`, `CONTEXT_NEEDED`
- `abstain_option` — one of `null` (committed), `(a)`, `(b)`, `(c)`, `(d)`
- `abstain_confidence_snapshot` — categorical (per §3): `HIGH`/`MEDIUM`/`LOW` plus matched_rules from classifier_a
- `operator_disambiguation_response` — populated if `(a)` clarify triggered; captures what operator chose (feeds back into corpus)
- **`router_recommendation_followed`** (per Rigby SIGN Q5 refinement) — enum or bool: `TRUE` (operator followed router's abstain option / substrate hint) / `FALSE` (operator overrode) / `null` (unknown / no advisory issued). Purpose: clean non-reconstructed scalar for "did the operator follow the router's recommendation?" — inferring this from messy UI clicks / downstream tool logs is fragile and undermines Phase-0.5 measurement quality.

Additional CONTEXT_NEEDED-specific fields when abstain_option = (a):
- `clarify_context_type` — `operational` or `conversational` (per §2.4 R3 discipline)

### §4.1 Persistence + query path (per Rigby SIGN Q6 C5)

**Persistence target:** `logs/phase_0_5_router.jsonl` — line-delimited JSON, appended per router decision. Persistent across worker restarts (append-only file, not in-memory).

**Extraction query path for Phase-0.5 measurement report:**
- `python docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py --log logs/phase_0_5_router.jsonl` — dedicated analysis script (to be authored at B2 build time; skeleton included with Track B B2 router-scaffolding PR).
- Feeds Phase-0.5 measurement_report.md §NEW abstain-analysis section (see below).

**Reason this matters:** Rigby Q6 C5 flagged that fields living only in ephemeral logs without a stable extraction path makes the measurement guardrail illusory. Persistence target + extraction query path are BOTH required.

### §4.2 Measurement report §NEW abstain-analysis section

Phase-0.5 measurement report §NEW section reports:
- Abstain rate per outcome (AMBIGUOUS % / UNCLASSIFIABLE % / CONTEXT_NEEDED %)
- UNCLASSIFIABLE rate by operator style + by query length bucket (per §2.3 R2)
- CONTEXT_NEEDED clarify-rate + clarify-cap breach events + operational-vs-conversational ratio (per §2.4)
- Post-abstain retrieval-outcome quality (did the fallthrough recover the correct target?)
- Operator disambiguation quality (did the operator's chosen response validate the router's abstain rationale?)
- `router_recommendation_followed` compliance rate — sliced by outcome + by operator style
- Missed-CONTEXT_NEEDED error rate (per §2.4 tracked error mode) — post-hoc via clarify follow-up + operator-response inspection

## §5 — Non-goals

- NO promotion to production routing until Phase-0.5 measurement shows the abstain policy discipline holds (per Chris R2 advisory-only)
- NO abstain-policy application outside the feature-flag dogfood router (advisory-only, one call-site: `core/services/td_handlers_ops.py:5905` kb_tool.semantic_search)
- NO auto-abstain-threshold recalibration until Phase-0.5 balanced P1 harvest closes
- NO DISCOVERY-fix implementation via abstain policy (Chris R3 preserve directive) — DISCOVERY family absorbs the (b) default-substrate parallel-substrate path per §2.1's default entry

## §6 — Rigby joint SIGN — CLEARED (15 refinements applied same-session, 0 F-BLOCKING)

**SIGN cycle executed via pin `pa-d63796dde6404d0f` at S2823 turn ~16.** Anti-rubber-stamp check: PASSED — Rigby returned 5 explicit `repo_tool.read_file` probes covering `measurement_report.md`, S2822 envelope §7 R4 + §9 R2 + §11, `classifier_a.py` (source-of-truth for the categorical-vs-numeric confidence discovery), `BALANCED_P1_HARVEST_PLAN.md`, and this proposal itself.

### §6.1 Question-by-question verdicts

| Q | Subject | Verdict | Refinements |
|---|---|---|:---:|
| Q1 | §2.2 AMBIGUOUS = (c) parallel-both | AGREE-with-refinements-2 | 2 |
| Q2 | §2.3 UNCLASSIFIABLE = (d) no-action | AGREE-with-refinements-2 | 2 |
| Q3 | §2.4 CONTEXT_NEEDED = (a) clarify | AGREE-with-refinements-3 | 3 |
| Q4 | §3 confidence thresholds | **DISAGREE (as numeric)** / **AGREE-with-refinements-2 (as policy intent)** | 2 |
| Q5 | §4 instrumentation fields | AGREE-with-refinements-1 | 1 |
| Q6 | zoom-out + §10.4 composition | AGREE-with-refinements-5 | 5 |
| — | **Total** | **1 DISAGREE-on-parameterization + 5/5 AGREE-with-refinements; 0 F-BLOCKING** | **15** |

### §6.2 Q4 substrate-correction (CRITICAL)

Rigby's Q4 DISAGREE surfaced that `classifier_a.py` emits **categorical** confidence (`HIGH`/`MEDIUM`/`LOW`) plus `matched_rules`, NOT numeric confidence or top-2 deltas. The original v0 numeric thresholds (≥0.70 / 0.15 / 0.35) were unimplementable against the actual classifier surface.

**Correction applied:** §3 rewritten as §3.1 Categorical routing rules + §3.2 Numeric-thresholds-DEFERRED. Any future attempt to reintroduce numeric thresholds without adding a numeric scorer to classifier_a MUST route back to SIGN per Chris §10.4 evidence-integrity discipline (predeclared trigger — see §7 below).

**Anti-drift note:** This is exactly the kind of finding that Chris §10.4 evidence-integrity directive was written for — the abstain policy would have shipped with unimplementable thresholds if Rigby's SIGN hadn't caught it via `classifier_a.py` tool-verify. Same-session recovery preserved the plan; silent-adaptation would have been the constitutional violation.

### §6.3 15 refinements applied

- **Q1 R1** — §2.2 add explicit no-fusion clause ("Parallel retrieval produces two substrate-labeled lists; system does not fuse or rerank across them")
- **Q1 R2** — §2.2 union-view guard (substrate provenance tags + deterministic grouping; no interleaving)
- **Q2 R1** — §2.3 UNCLASSIFIABLE events MUST be counted+reported even when no-op (no-op ≠ no-record)
- **Q2 R2** — §2.3 measurement report line item — UNCLASSIFIABLE rate by operator style + by query length bucket
- **Q3 R1** — §2.4 UX budget cap (≤2 clarify per 20 queries OR ≤10% rate)
- **Q3 R2** — §2.4 flip rule on cap breach ((a) → (d) for remainder of session while still logging)
- **Q3 R3** — §2.4 context-type logging (operational vs conversational)
- **Q4 R1** — §3 REWRITTEN as §3.1 categorical routing rules matching classifier_a HIGH/MEDIUM/LOW
- **Q4 R2** — §3.2 numeric thresholds DEFERRED unless numeric scorer exists (trigger for §10.4 methodology-back-to-SIGN)
- **Q5 R1** — §4 add 5th field `router_recommendation_followed` (enum/bool)
- **Q6 C1** — §3 categorical rules explicit (also captured in Q4)
- **Q6 C2** — §2.2 UI-level no-fusion discipline (extends Q1 to include UX layer)
- **Q6 C3** — §2.4 "missed-CONTEXT_NEEDED as tracked error mode"
- **Q6 C4** — §7 predeclared §10.4 evidence-integrity trigger list (see §7 below)
- **Q6 C5** — §4.1 persistence target + extraction query path (Rigby fields must live somewhere queryable)

## §7 — Predeclared §10.4 evidence-integrity trigger list (per Rigby SIGN Q6 C4)

Chris §10.4 in BALANCED_P1_HARVEST_PLAN elevated evidence-integrity to LOAD-BEARING: "if execution uncovers findings that materially challenge ratified assumptions, stop, document, route back for SIGN — do not silently adapt." Rigby Q6 C4 refinement flagged that "materially challenges" is too interpretive without predeclared triggers.

**Predeclared triggers — any of the following automatically routes methodology back to Rigby SIGN before continuing:**

1. **Numeric-threshold introduction without numeric scorer** — any PR/patch/commit that adds numeric confidence thresholds to the abstain policy or router without first adding a numeric scoring surface to `classifier_a.py` (or replacement). Categorical-only is the current substrate reality (per §3 + Q4 finding).

2. **AMBIGUOUS or UNCLASSIFIABLE rate exceeding cap** — if either abstain-outcome rate exceeds **30% over the first n=20 balanced P1 harvest rows**. High rates suggest the classifier's decision boundary is not text-derivable; continuing the experiment as if routing viability is measurable would be an integrity violation.

3. **Systematic operator override rate >50%** — if `router_recommendation_followed=FALSE` on more than 50% of instrumented queries. Sustained override rate means the router's advisory is systematically wrong from the operator's perspective; measurement is compromised.

4. **Parallel-retrieval-induces-operator-confusion pattern** — if AMBIGUOUS (c) parallel-both fallthrough produces measurable follow-rate drop (operator asks the same question again, or asks a disambiguating question about the router's own output). Union-view noise or UX-fusion drift.

5. **Missed CONTEXT_NEEDED errors clustering above cap** — if the "missed CONTEXT_NEEDED as tracked error mode" (per §2.4) shows systemic misclassification into AMBIGUOUS or UNCLASSIFIABLE, this is a classifier-surface problem the abstain layer cannot compensate for.

**When triggered:** STOP execution → document evidence in `logs/phase_0_5_router.jsonl` + a new `PHASE_0_5/evidence_integrity_stop_<trigger>_<date>.md` deliverable → route back to Rigby joint SIGN → Chris D-verdict on methodology adjustment. Do NOT silently modify the abstain policy, the router, or the harvest plan.

## §8 — Post-SIGN routing to Chris

- Chris ratifies the four-outcome policy (§2.2 (c) parallel-both / §2.3 (d) no-action / §2.4 (a) clarify)
- Chris ratifies §3 categorical routing rules (with numeric-thresholds-DEFERRED status)
- Chris ratifies §4 instrumentation fields (5 total including `router_recommendation_followed`)
- Chris ratifies §7 predeclared §10.4 trigger list
- On RATIFY, this proposal becomes load-bearing; Track B B2 router-scaffolding design references this as canonical abstain spec

## §10 — Chris D-verdict RATIFIED (2026-07-18 S2823 turn ~18)

**Verdict:** **RATIFY** — all five ratifications accepted as the constitutional gate for Phase-0.5 abstain policy. Downstream router build (Track B B2) must not weaken any ratified rule.

### §10.1 R1 — AMBIGUOUS: RATIFIED

- Execute both lexical and semantic retrieval paths.
- Return two explicitly substrate-labeled result sets.
- Do NOT fuse, interleave, cross-rerank, or present a blended ranking.
- **Any presentation that creates fusion-by-UX violates R6 and triggers an integrity stop.**

### §10.2 R2 — UNCLASSIFIABLE: RATIFIED

- Take no router-directed action and preserve current-best behavior.
- Every no-op MUST still create a durable measurement record.
- Report UNCLASSIFIABLE rates by operator style and query-length bucket.
- **No-action must never mean no evidence.**

### §10.3 R3 — CONTEXT_NEEDED: RATIFIED (with "measurement window" reframing)

- Ask for clarification by default.
- UX budget: ≤2 clarification turns per 20 routed queries OR ≤10%, whichever is reached first.
- **Once cap breached, switch CONTEXT_NEEDED from clarify to logged no-action for the remainder of that measurement window.** (Note: Chris framing "measurement window" replaces the proposal's "session" — see §10.6.1)
- Record whether missing context was operational or conversational.
- Track missed-CONTEXT_NEEDED as a distinct error mode.

### §10.4 R4 — Confidence Handling: RATIFIED with substrate correction

- Phase-0.5 uses classifier's existing categorical HIGH/MEDIUM/LOW confidence outputs.
- Numeric thresholds and top-two score deltas explicitly DEFERRED unless a future classifier version produces **auditable numeric scores**.
- **Do NOT invent numeric equivalents for categorical confidence.**

### §10.5 R5 — Evidence-Integrity Triggers: RATIFIED

The §7 predeclared triggers are BINDING. Pause execution and route affected methodology back through SIGN when any of the following occurs:

1. A policy depends on numeric confidence signals that do not exist.
2. AMBIGUOUS plus UNCLASSIFIABLE exceeds the ratified rate cap.
3. Operator override exceeds 50%.
4. Parallel retrieval repeatedly creates measurable operator confusion or presentation-induced bias.
5. Missed-CONTEXT_NEEDED cases cluster sufficiently to challenge the current detector assumptions.

### §10.6 Two Chris framings requiring downstream honoring

**§10.6.1 — "Measurement window" (not "session"):** Chris R3 wording uses "measurement window" rather than "session." A measurement window is a defined analysis interval (potentially larger or smaller than a session) — e.g., a Phase-0.5 harvest phase, a rolling n=20 sample, or a dedicated dogfood observation period. The router MUST identify a specific measurement window at each execution start (settings-configurable OR defined by harvest-plan scope) and apply the clarify-cap flip rule to that window scope. B2 router-scaffolding design MUST expose this.

**§10.6.2 — "Durable persistence location + defined extraction path — ephemeral logs alone are insufficient":** Chris explicitly ratified that instrumentation MUST have (a) a durable persistence location and (b) a defined extraction path for the Phase-0.5 measurement report. **Ephemeral logs alone are insufficient.** This tightens §4.1 which currently specifies `logs/phase_0_5_router.jsonl` (append-only file). Options for B2 build to satisfy this:
- Option (i): JSONL file + committed extraction analysis script that reads it deterministically
- Option (ii): Django model (e.g., `Phase0_5RouterEvent`) with ORM-queryable fields + managed retention
- Option (iii): Both — JSONL primary + optional model mirror for structured querying

Chris D-verdict does NOT prescribe which option; B2 SIGN + Chris D-verdict on B2 will resolve. Interim guidance: JSONL file MUST NOT be the sole record — either a model mirror OR a versioned extraction script that is itself committed to the repo satisfies "defined extraction path."

### §10.7 Downstream router-build discipline binding

Chris: "No router build may weaken the ratified no-fusion, abstention, evidence-persistence, or integrity-stop rules."

Track B B2 router-scaffolding design (in `ROUTER_SCAFFOLDING_DESIGN.md`) MUST be updated (during Rigby SIGN on B2) to explicitly reference:
- R1 no-fusion discipline (§10.1) as invariant in router UI/envelope contract
- R2 UNCLASSIFIABLE durable-record requirement
- R3 measurement-window scope (§10.6.1) as router configuration
- R4 categorical-only confidence handling (§10.4) — REMOVES §3 v0 numeric-threshold placeholder from the design doc
- R5 §7 trigger list as router-runtime abort conditions

### §10.8 Ratification status: LOAD-BEARING

Plan §2.2/§2.3/§2.4/§3/§7 + §4 5-field instrumentation are now the ratified constitutional gate for Phase-0.5 abstain policy. Track B B2 router-scaffolding SIGN + Chris D-verdict proceed under this constraint.

---

## §11 — Related evidence

- Phase-0 measurement_report §4-§5 context-needed post-hoc analysis (identifies CONTEXT_NEEDED rows in Phase-0 corpus + operational-vs-conversational distinction)
- Phase-0 field_dictionary §4 (secondary_family field supports the AMBIGUOUS labeling for corpus rows)
- Phase-0 classifier_a.py (categorical HIGH/MEDIUM/LOW confidence source-of-truth per Q4 finding)
- S2822 envelope §7 R4 refinement (context-needed as separate outcome, ratified Chris)
- BALANCED_P1_HARVEST_PLAN §10.4 evidence-integrity directive (predeclared trigger list in §7 operationalizes this)
- Bridge §5.3 B3 (four-option fallthrough catalog origin)

---

**End of proposal. B1 D-RATIFIED; this B3 proposal Rigby-SIGN-cleared with 15 refinements applied same-session (0 F-BLOCKING; 1 substantive substrate correction via Q4 categorical-vs-numeric discovery). NEXT: Chris D-verdict on this proposal → then Rigby joint SIGN on ROUTER_SCAFFOLDING_DESIGN (Track B B2) → then Chris D-verdict on B2 → then build authorization.**

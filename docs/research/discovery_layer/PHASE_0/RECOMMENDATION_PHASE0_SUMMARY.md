# Phase-0 Recommendation Summary — For Chris Ratification

**Session:** S2822 (Phase-0 execution — direct successor to S2821 routing-first pivot)
**Date:** 2026-07-18
**Governing envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md`
**Companion:** `measurement_report.md` (raw evidence — read first if context needed)

> Per Chris R6: **architecture follows evidence, not the reverse.** This recommendation is authored evidence-forward. If taxonomy collapse, taxonomy expansion, or routing abandonment are the honest reads, they are stated as such.

---

## §1. Headline finding

**Routing from query text alone is viable for 5 of 6 families — but P1 real-query accuracy is 20%, a 60-point gap vs synthetic queries.**

Concretely, on the 33-row Phase-0 corpus (5 P1 real / 10 P2 observed-failure / 18 P3 synthetic-gap-fill):
- Classifier A (flat) achieves F1 ≥ 0.91 on COUNT, PROCEDURAL, IDENTITY, SELF-REFERENCE, CONCEPTUAL
- Classifier A achieves F1 = 0.36 on DISCOVERY (recall 0.22 — 2/9 correct)
- **Both classifiers score 20% accuracy on P1 real operational queries (1/5 correct)** while scoring 80-89% on P2/P3
- Zero wrong-but-plausible predictions from Classifier A (R5 safety advantage)
- Two wrong-but-plausible predictions from Classifier B (R5 caution — two-axis composition introduces failure class)

**The Chris R1 provenance discipline was load-bearing.** Without it, a P3-heavy corpus would have shown ~85% aggregate accuracy and hidden the P1 signal completely.

---

## §2. Chris R6 outcome menu (which outcome the evidence supports)

Per R6, all outcomes below are considered successful Phase-0 results. My reading of the evidence:

| R6 outcome | Evidence support | Verdict |
|---|---|---|
| **Taxonomy collapse (6→5)** | IDENTITY collapses to (DOC, LOCATE) 83% but SELF-REFERENCE does NOT (0%). SR routes through (POINTER, POINT). | **PARTIAL SUPPORT** — one axis (POINT vs LOCATE) is confirmed distinct; the collapse candidate for SR-C3 is REFUTED. Recommend KEEP 6 families. |
| **Taxonomy expansion** | No structural signal for new families. AMBIGUOUS/UNCLASSIFIABLE/CONTEXT_NEEDED are correctly modeled as outputs not families. | **NO SUPPORT** for expansion. |
| **Relationship collapse (POINT→LOCATE)** | 4 POINT hits vs 8 LOCATE hits; both populated with non-overlapping row sets. | **REFUTED** — POINT distinct is confirmed. |
| **New relationship types** | No structural signal. | **NO SUPPORT.** |
| **Abandonment of routing** | 5/6 families work on Classifier A ≥ 0.91 F1 (synthetic corpus). BUT P1 = 20%. | **POSSIBLE SUPPORT** IF corpus expansion shows P1 gap holds. |
| **Fundamentally different model (context-aware, two-substrate parallel, etc.)** | Post-hoc context-needed analysis: 3/33 rows require operational context to route correctly. Classifier A caught 1/4 context-required rows (25%); Classifier B caught 0/4 (0%). | **CANDIDATE OPTION** if Chris pivots R3 constraint. |

**Evidence-forward reading:** The taxonomy holds (with POINT confirmed distinct). The question is whether **query-text-only routing** is viable given the P1 real-query gap. If P1 accuracy stays at ~20-30% with more real rows, routing-from-text-alone is not viable; a fundamentally different model (context-aware OR two-substrate parallel with merge) is warranted.

---

## §3. Recommended Phase-1 gate decision options

**OPTION A (recommended default): Phase-0.5 P1 corpus expansion before Phase-1.**

Rationale: The most consequential single finding is the P1-vs-P3 accuracy gap (20% vs 89%). At n=5 P1 rows, we cannot distinguish "real queries are structurally hard" from "5-row sample noise." Expand P1 to 20+ rows via:
- Rigby conversation-history mining (broader `conversation_tool.search` patterns)
- Handoff scan for additional tool-call query strings
- Chris Chat UI conversation history for user-shape queries
- Optional: 1-2 sessions of instrumented dogfooding (log every Chris/Rigby search query to a P1 harvest pool)

Re-measure with n≥20 P1. **Phase-0.5 termination rule (per Rigby SIGN Q3 refinement):** If P1 ≥ 20 rows and accuracy remains ≤30-40%, routing-from-text-alone is presumptively not viable — Phase-0.5 closes with Chris D-verdict escalation to Option C or D, NOT another expansion loop. If P1 rises to ≥65%, routing table is warranted for 5 families and Phase-1 proceeds.

**OPTION A-dual (Rigby SIGN Q3 alternative — preserves momentum):** Authorize Option A AND a constrained "dogfood routing" Phase-1 pilot behind a feature-flag gate on the 5 strong families only. DISCOVERY explicitly defaults; strong logging captures P1 growth from real traffic. Reversible via flag flip if evidence shows Phase-0.5 P1 accuracy holds low. Ships routing value on 5 well-differentiated families while corpus expansion runs in parallel.

**OPTION B: Proceed to Phase-1 narrow-scope routing (5 families only) with DISCOVERY = default substrate.**

Rationale: The 5 non-DISCOVERY families all clear their priors (or nearly so on Classifier A). Build a routing table that dispatches to lexical or semantic per family (COUNT → lexical PLATFORM_INVENTORY; PROCEDURAL → semantic topics; IDENTITY → lexical filename match; SELF-REFERENCE → lexical pointer; CONCEPTUAL → semantic). DISCOVERY falls through to current substrate (parallel lexical+semantic or lexical-only per current default).

Risk: P1 accuracy of 20% suggests real DISCOVERY queries are ~5/9 of realistic-user asks. Defaulting DISCOVERY to lexical parallel might not be worse than status quo, but doesn't ship the routing value the taxonomy was supposed to deliver.

**OPTION C: Abandon routing; adopt two-substrate parallel with per-family fusion.**

Rationale: If the 5 working families are cheap to classify AND DISCOVERY is unclassifiable from text alone, the architectural boundary isn't routing — it's parallel-query + result-merge. Fusion (RRF variant limited to DISCOVERY, or answer-mode-aware re-ranking) becomes the primary tool. **This is closer to Chris's own S2821 initial framing** (Path B hybrid) that he re-framed away from.

Risk: Explicit contradiction of Chris's S2821 D-verdict architectural direction. Only Option C-worthy if Chris explicitly re-opens that decision.

**OPTION D: Extend classifier to context-aware; Phase-0.5 stress-tests context features.**

Rationale: Post-hoc context-needed analysis showed 3 rows are ground-truth context-dependent (A1/A2/A3 — operational context). Classifier B fails these entirely; Classifier A catches 1/4. If context signal is added (workspace, current task, recent activity), those 3 rows might route correctly.

Risk: Chris R3 explicitly forbade context in Phase-0. Option D would require Chris to revise R3 → allow context-signal classifier input. **This is a Chris decision, not an evidence decision.**

---

## §4. My recommendation (evidence-honest)

**OPTION A — Phase-0.5 P1 corpus expansion before Phase-1 gate decision.**

The P1-vs-P3 accuracy gap is too large to make a Phase-1 gate decision at n=5. All four options (B/C/D + do-nothing) depend on whether P1 accuracy is truly ~20% or an artifact of sample size. Phase-0.5 costs 1-2 sessions of harvest + re-measurement; Phase-1 routing-table build costs substantially more if we're building the wrong architecture.

**If Chris rejects Phase-0.5 and forces immediate Phase-1 decision:** I lean OPTION B (narrow-scope routing, DISCOVERY defaults) — it ships value on the 5 well-differentiated families without over-committing to routing where evidence is weak.

---

## §5. Recommended per-family gate calibrations (R2 — evidence-forward)

Per Chris R2: priors are STARTING PRIORS, not optimization targets. Recommended revised floors based on Phase-0 evidence:

| Family | S2821 §7.6 prior | Phase-0 evidence max | Recommended | Rationale |
|---|---|---|---|---|
| COUNT | 0.90 classifier | 1.00 | **0.95** | Tightening (significant headroom); HIGH-consequence deserves it |
| PROCEDURAL | 0.75 | 1.00 | **0.90** | Tightening (family well-differentiated by verb-object) |
| DISCOVERY | 0.70 | 0.50 | **0.50 (loosened) IF routed at all** OR **N/A drop from routing** | Prior severely missed; classifier fundamentally weak; recommend Chris chooses B (loosen + include) or C (exclude from routing) |
| IDENTITY | 0.90 | 0.91 | **0.90 (hold)** | Prior barely met; do not tighten (HIGH-consequence, thin margin) |
| SELF-REFERENCE | 0.90 | 1.00 | **0.90 (hold)** | Prior met with headroom on Classifier A only; do not tighten (n=3 too thin to inform tightening) |
| CONCEPTUAL | 0.70 | 0.91 | **0.85** | Tightening (family well-differentiated by explanatory question shape) |

**Global gate:** If DISCOVERY held at prior 0.70, global gate fails on all classifiers. If DISCOVERY is dropped from routing OR loosened to 0.50, global gate passes on Classifier A only.

---

## §6. Two-axis pressure-test verdicts

1. **IDENTITY + SELF-REFERENCE-C3 → (DOC, LOCATE) collapse candidate:** **NOT SUPPORTED (n=3 SELF-REFERENCE).** IDENTITY→(DOC,LOCATE) has strong support (5/6 = 83%). SELF-REFERENCE→(DOC,LOCATE) has 0/3 support and routes through (POINTER, POINT) instead — but n=3 is thin. Per Rigby SIGN Q4 refinement: language softened from "REFUTED" — evidence currently contradicts the collapse for SR, revisit after SR corpus expands. **Operational consequence unchanged:** do NOT fold 6→5 families yet.
2. **POINT distinct from LOCATE:** **CONFIRMED.** 4 POINT hits, 8 LOCATE hits, non-overlapping row sets. Preserve POINT as distinct relationship.

---

## §7. Explicit non-recommendations retained

Per Chris R6 + S2821 §7.9:
- **NO routing implementation** (this recommendation summary is for Phase-1 gate decision, not Phase-1 build)
- **NO fusion / RRF implementation** (Option C's fusion consideration is architectural discussion only)
- **NO taxonomy constitutionalization** (working taxonomy holds unchanged; POINT confirmation is a relationship-axis note, not a family change)
- **NO code substrate change** (lexical policy frozen; semantic default flip deferred)

---

## §8. Return path — for Chris

**Chris D-verdict expected on:**
1. Which of Options A / A-dual / B / C / D to pursue (or a combination/other)
2. Whether Phase-0.5 P1 corpus expansion is authorized (if OPTION A or A-dual) — and what resource budget
3. Any revised gate floor calibrations from §5
4. Whether Chris R3 (context-neutral first) should be revised to permit context features (relevant if OPTION D considered)

## §9. Phase-1 gate checklist for Chris (per Rigby SIGN Q5 zoom-out)

Independent of the Option choice, these 4 downstream Phase-1 questions are gate-decision-load-bearing and need explicit Chris answers before any Phase-1 build begins:

1. **P1 operator-style coverage** — Are we measuring real operational queries across Chris + Claude + Rigby styles, or just one shorthand dialect? If not, Phase-1 rollout should require a minimal balanced P1 set (n≥5 per operator class).
2. **Abstain policy = product decision** — When the router outputs AMBIGUOUS/UNCLASSIFIABLE/CONTEXT_NEEDED, what is the canonical fallthrough? (Ask clarifying question / default to substrate / run both and reconcile / silent fallback?) Without this, "safe abstain" turns into high workflow friction.
3. **DISCOVERY containment** — Explicit gate choice, NOT implementation detail: (a) exempt from routing (default substrate always) / (b) route with revised loosened floor (0.50) / (c) require context-aware features (revises Chris R3).
4. **Phase-0.5 stop condition** — Threshold that triggers "routing-first is not viable for real ops queries" so corpus expansion doesn't drift into an infinite loop. Recommended (Rigby-endorsed): n≥20 P1 with accuracy ≤30-40% → routing NOT viable for text-only.

**Rigby joint SIGN completed** on this summary (S2822 Phase-0 OP3-Q3 SIGN cycle, pin pa-fac188f02db24fcc). Refinements applied: §2.1/§2.2 TP/FP/FN checksums; §3 OPTION A-dual added; §6 REFUTED softened to NOT SUPPORTED (n=3); §9 Phase-1 gate checklist added. All 5 SIGN questions returned AGREE or AGREE-with-refinements-N; zero DISAGREE-blocker. Tool_runs non-empty (4x repo_tool.read_file). Anti-rubber-stamp check PASS.

---

**End of recommendation summary. Route through Rigby OP3-Q3 joint SIGN, then to Chris for Phase-1 gate ratification.**

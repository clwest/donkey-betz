---
title: "Retrieval Assumptions — /docs/ substrate retrievability posture (skeleton — Phase-0.5 evidence pending)"
status: skeleton
authority: forward-looking guidance (not yet load-bearing — full authoring deferred to post-Phase-0.5 arc close)
session: 2823
generated: 2026-07-18
supersedes: none
related:
  - docs/handoffs/SESSION_2822_PHASE0_TO_DOCS_AUDIT_BRIDGE.md   # §1 assumption findings (source)
  - docs/research/implementation/RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md  # Phase-0 envelope (evidence base)
  - docs/research/discovery_layer/PHASE_0/RECOMMENDATION_PHASE0_SUMMARY.md  # Phase-0 recommendation
  - docs/research/discovery_layer/PHASE_0/measurement_report.md  # Phase-0 evidence report
  - docs/DOC_LIFECYCLE.md   # §2c "PLATFORM_INVENTORY authoritative counts" convention (candidate for post-Phase-0.5 refresh)
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md  # Group 2700 T3 §7 C5 discovery-failure finding
scope:
  Captures four foundational assumptions about /docs/ substrate retrievability that Phase-0 evidence (S2822) has begun to stress-test. Serves as forward-looking guidance for any future /docs/ change that would affect retrieval behavior.
non_goals:
  - Establishing final verdicts (Phase-0 provides preliminary evidence; Phase-0.5 provides load-bearing evidence base)
  - Prescribing retrieval implementation changes (Chris R3 preserve directive holds through Phase-0.5)
  - Replacing DOC_LIFECYCLE §2c (candidate refresh only after Phase-0.5 evidence in hand)
lifecycle:
  - v0 (skeleton, S2823): 4 assumption sections with Phase-0 preliminary evidence + Phase-0.5 evidence-pending markers
  - v1 (post-Phase-0.5 close): full authoring with Phase-0.5 balanced P1 evidence base
  - v2+ (post-implementation): updated as retrieval-substrate changes ship
---

# Retrieval Assumptions

**Status:** SKELETON — Phase-0.5 evidence pending. Do not treat as load-bearing until v1 authoring closes.

**Why this doc exists.** The Phase-0 measurement package (S2822) forced four foundational assumptions about /docs/ retrievability to become explicit. Each is captured here for forward-looking reference; each needs Phase-0.5 balanced P1 evidence before it becomes a verdict.

**How to use this doc.**
- **If you're proposing a /docs/ change that affects retrieval** (weights / filters / thresholds / corpus scope): read the four assumptions and record which ones your proposal depends on.
- **If you're building measurement infrastructure** (benchmarks / classifiers / evaluation harnesses): apply the discipline flags noted under each assumption.
- **If you're waiting for Phase-0.5 to close** before acting on any of these: correct posture. Full authoring lands post-Phase-0.5 close per Chris R3 preserve directive.

---

## §1 — Aggregate corpus accuracy is a valid measure of retrieval quality

**Preliminary verdict (Phase-0, S2822):** REFUTED.

**Evidence base:** Phase-0 corpus n=33 (5 P1 + 10 P2 + 18 P3), R1-provenance-tagged. Aggregate accuracy = ~85%; P1 (real operator queries) accuracy = 20%; P3 (synthetic gap-fill) accuracy = 89%. **60-point P1-vs-P3 gap.** Aggregate metric would have masked the transfer-to-real-work failure entirely.

**Discipline flag for future /docs/ retrieval work:**
- Any future PR that changes retrieval behavior MUST report per-provenance-tier accuracy alongside aggregate.
- Aggregate-only is a methodology red flag from S2822 forward.
- R1 provenance tier hierarchy (real / observed-failure / synthetic-with-gap-tag) is mandatory labeling for any benchmark corpus.

**Phase-0.5 evidence gate:** verify the 60-point gap holds (or collapses) once balanced-operator-style P1 rows are collected (n≥20 minimum, n≥5 per Chris/Claude/Rigby dialect).

**Status field for v1:** _pending Phase-0.5 close._

---

## §2 — Well-formed documentation is retrievable by well-formed queries

**Preliminary verdict (Phase-0, S2822):** PARTIALLY REFUTED.

**Evidence base:** /docs/ conventions (uppercase-heavy filenames like `PLATFORM_INVENTORY.md`, structured stem prefixes like `2701_docs_inventory_topology_audit`, canonical-authority frontmatter, category taxonomy) are optimized for the corpus author's mental model. Real operator queries observed in P1 rows use bare noun phrases (`"morning_brief workflow"`, `"agent router"`, `"BINDING DIRECTIVE"`, `"AgentDecisionSummary writer"`) — uppercase-token-heavy identifier shapes that retrieval currently does not weight for.

**Discipline flag for future /docs/ retrieval work:**
- The relevant audit question is not "are our docs well-organized" (repeatedly answered yes) but "can operators find them with the queries they actually issue" (Phase-0.5 answers this with evidence).
- Any restructuring proposal that changes filename / structure / frontmatter conventions should re-run the Phase-0.5 corpus post-change to verify retrievability didn't regress.

**Phase-0.5 evidence gate:** balanced P1 harvest from Chris + Claude + Rigby dialects will materialize the actual operator query distribution.

**Status field for v1:** _pending Phase-0.5 close._

---

## §3 — 6-family taxonomy exhaustively captures how operators query docs

**Preliminary verdict (Phase-0, S2822):** UNCONFIRMED.

**Evidence base:** Phase-0 6-family taxonomy = COUNT / PROCEDURAL / IDENTITY / SELF-REFERENCE / CONCEPTUAL / DISCOVERY. DISCOVERY F1 max = 0.50 on Classifier A (best safety); IDENTITY / COUNT / PROCEDURAL score near-perfect. DISCOVERY is exactly the family operators live in day-to-day ("find me relevant docs about X" mode) — and the classifier cannot detect it from query text alone. Meanwhile the well-classified families (IDENTITY / COUNT / PROCEDURAL) are the query shapes /docs/ is currently optimized for.

**Discipline flag for future /docs/ retrieval work:**
- If DISCOVERY is dominant in real usage but underserved by current retrieval + doc structure, and IDENTITY / COUNT / PROCEDURAL are minority but well-served, we may have optimized for the wrong query distribution.
- Do NOT constitutionalize the 6-family taxonomy (per Chris R6 non-goal for Phase-0.5).
- Do NOT restructure /docs/ around family assumptions until Phase-0.5 evidence confirms family distribution in real operator work.

**Phase-0.5 evidence gate:** balanced P1 harvest measures actual family distribution across dialects. Consider extending taxonomy only if operator queries systematically fall outside the 6 families.

**Status field for v1:** _pending Phase-0.5 close._

---

## §4 — Docs cascade (build_docs_index → build_rag_corpus → sync → embed) is sufficient for retrievability

**Preliminary verdict (Phase-0, S2822):** UNCONFIRMED.

**Evidence base:** Chunks are the retrieval unit; documents are the evaluation unit. Q1 "How many spiders do we have" fails while Q4 "How many celery tasks" succeeds on the same target document (`PLATFORM_INVENTORY.md`) — chunk-boundary structural issue documented in S2821 §6.4 remains unresolved. Every /docs/ retrieval outcome depends on this. The current 4-step docs cascade discipline works for indexing but does not validate that resulting chunks retrieve when queried.

**Discipline flag for future /docs/ retrieval work:**
- The docs cascade should grow a step 5 = "smoke-test retrievability" against a small canonical query set — otherwise the cascade completes without verifying that the corpus is queryable.
- Cascade PRs currently include step 4 (embed) as convention (per `feedback_cascade_pr_must_include_embed_step`). Step 5 (retrievability smoke test) is candidate promotion post-Phase-0.5.

**Phase-0.5 evidence gate:** the Phase-0 corpus + `analyze.py` measurement harness are prototype infrastructure for the step-5 smoke test. Phase-0.5 balanced P1 corpus expansion + reusable harness = candidate substrate for the smoke-test step itself.

**Status field for v1:** _pending Phase-0.5 close._

---

## §5 — Where this doc lives in the lifecycle

- **Skeleton (v0, this session — S2823):** captures the 4 assumption findings for forward-looking reference. Not load-bearing. Placeholder evidence-gates for each.
- **v1 authoring (post-Phase-0.5 arc close):** full evidence base filled in; verdicts move from "preliminary" to "grounded"; discipline flags may become PLAYBOOK candidates.
- **DOC_LIFECYCLE §2c refresh (deferred to post-Phase-0.5):** currently claims PLATFORM_INVENTORY is sole authoritative counts source. Post-Phase-0.5 will have retrieval-tested proof (or refutation) of this convention across balanced P1 rows.
- **Playbook v0.10 R1 provenance discipline candidate (currently 1/2 triggers, S2822 = trigger 1):** if a second arc applies R1 tier hierarchy to a benchmark corpus, R1 discipline promotes to a constitutional PLAYBOOK rule; this doc's §1 discipline flag is the corroborating substrate.

**Reopen triggers for this doc:**
- Phase-0.5 close-cascade merge → author v1
- Any retrieval-substrate change proposed for /docs/ post-Phase-0.5 → verify against this doc first
- Retrieval assumption emerges as trigger for Playbook amendment → refresh discipline flags

---

**End of skeleton. Evidence pending. Do not treat as load-bearing until v1.**

# Session 2822 Bridge — Phase-0 → /docs/ Audit Reconnection

**Date:** 2026-07-18 (S2822 close-cascade adjacent; authored per Chris directive before merge)
**Session:** S2822 (companion to SESSION_2822_PHASE0_EXECUTION_OPTION_A_DUAL.md)
**Purpose:** Intentionally reconnect Phase-0 findings to the /docs/ audit arc (Group 2700 §8 item #1 that spawned this work). Frame Phase-0.5 as a continuation of documentation + architecture work, not a new project.

> This bridge deliverable is required reading at S2823 open — before Phase-0.5 execution begins. It answers Chris's 5 questions: (1) what S2822 taught us about documentation + retrieval assumptions; (2) which docs to audit first; (3) what evidence to fold back into /docs/; (4) what doc changes are required before Phase-0.5; (5) recommended first-session dual-track plan.

---

## §1. What S2822 taught us about our documentation + retrieval assumptions

The Phase-0 evidence stress-tests foundational assumptions we have implicitly built the entire /docs/ substrate around. Four assumptions became explicit only because R1 provenance discipline forced us to look.

### §1.1 Assumption: Aggregate corpus accuracy is a valid measure of retrieval quality

**REFUTED.** Provenance-tier stratification revealed a **60-point P1-vs-P3 gap** (20% real-query accuracy vs 89% synthetic). All prior /docs/ retrieval evaluations (S2818 authority-boost pilot, S2819 Shape C intent gating, S2820 orientation-doc exclusion) used aggregate corpus metrics. Those results are now **suspect until re-measured with provenance discipline** — not necessarily wrong, but the confidence intervals we assigned them were computed from potentially inflated aggregates.

**Consequence for /docs/ retrieval work:** any future PR that changes retrieval behavior (weights, filters, thresholds, corpus scope) MUST report per-tier accuracy alongside aggregate. Aggregate alone is a methodology red flag from S2822 forward.

### §1.2 Assumption: Well-formed documentation is retrievable by well-formed queries

**PARTIALLY REFUTED.** Our /docs/ conventions — uppercase-heavy filenames (`PLATFORM_INVENTORY.md`), structured stem prefixes (`2701_docs_inventory_topology_audit`), canonical-authority frontmatter, category taxonomy — are optimized for the corpus author's mental model. Real operator queries look like `"morning_brief workflow"`, `"agent router"`, `"BINDING DIRECTIVE"`, `"AgentDecisionSummary writer"` — bare noun phrases + uppercase-token-heavy identifier-shapes that our retrieval assumptions do not account for.

**Consequence for /docs/ audit:** the audit question isn't "are our docs well-organized" — that has been repeatedly answered yes. The audit question is "**can operators find them with the queries they actually issue?**" Very different question. Most of the /docs/ arc so far has been on the first; Phase-0.5 forces the second.

### §1.3 Assumption: 6-family taxonomy exhaustively captures how operators query docs

**UNCONFIRMED.** DISCOVERY (F1 max 0.50) is the family where operators live day-to-day — the "find me relevant docs about X" mode. And it is the family the classifier cannot detect from query text alone. Meanwhile IDENTITY, COUNT, PROCEDURAL score near-perfect on the classifier — these are exactly the query shapes that /docs/ is currently optimized for.

**Consequence for /docs/ audit:** if DISCOVERY is dominant in real usage but underserved by our current retrieval + doc structure, and IDENTITY/COUNT/PROCEDURAL are minority but well-served, we may have optimized for the wrong query distribution. The 60-point P1-vs-P3 gap partially reflects this — real operator queries are mostly DISCOVERY-shape; synthetic P3 rows tilted toward IDENTITY/COUNT/CONCEPTUAL because those are easier to author labeled examples for.

### §1.4 Assumption: Docs cascade (build_docs_index → build_rag_corpus → sync → embed) is sufficient for retrievability

**UNCONFIRMED.** Chunks are the retrieval unit; documents are the evaluation unit. Q1 "How many spiders do we have" fails while Q4 "How many celery tasks" succeeds on the same target (PLATFORM_INVENTORY.md) — chunk-boundary structural issue documented in S2821 §6.4 remains unresolved. Every /docs/ retrieval outcome is affected. Docs cascade discipline works for indexing but doesn't validate that the resulting chunks retrieve when queried.

**Consequence for /docs/ pipeline:** docs cascade should grow a step 5 = "smoke-test retrievability" against a small canonical query set. Otherwise the cascade completes without verifying that the corpus is queryable.

---

## §2. Which documentation should be audited first because of these findings

Priority order based on Phase-0 evidence intensity:

### §2.1 PLATFORM_INVENTORY.md (highest priority — audit first)

**Why:** S2818 authority-boost fix was measured on aggregate. Re-audit with provenance discipline: does the fix hold on realistic count queries (P1) or only on synthetic-shaped count queries (P3)? Phase-0 corpus rows Q1-Q4 + C5 test this — but all are P2 (observed failures from prior sessions, not fresh P1). Phase-0.5 balanced P1 will include real count queries from Chris + Claude + Rigby dialects.

**Audit question:** For each canonical count listed in PLATFORM_INVENTORY (agents, spiders, models, tasks, workers, etc.), verify: does a natural-language P1 query issued by each operator style return PLATFORM_INVENTORY as top-3? If not, the DOC_LIFECYCLE §2c "sole authoritative counts source" convention is broken at the discovery layer.

### §2.2 docs/handoffs/ SESSION_XXXX_*.md (second priority — P1 harvest surface)

**Why:** Handoffs are where Phase-0.5's real P1 query harvest comes from. If handoff titles + intros are not retrievable by the queries operators use to find them (e.g., "session about docs cleanup", "the arc that shipped authority boost"), P1 harvest yields nothing usable and Phase-0.5 stalls.

**Audit question:** Given a natural-language description of what happened in session XXXX, does search return that session's handoff in top-3? Spot-check 5-10 recent handoffs with descriptions Chris/Claude/Rigby would plausibly write.

### §2.3 CLAUDE.md #6 pointer chunk (third priority — pointer/self-reference)

**Why:** S2821 evidence identified this as the target for pointer queries like Q8 "00-START-NEXT-SESSION" and S2 "where do I read this project's rules". SELF-REFERENCE F1 on Classifier A is 1.0 — but that's on synthetic queries with the literal filename. Real operators use descriptors like "the start doc" or "where do I begin."

**Audit question:** Does CLAUDE.md #6 retrieve for {"the next session start doc", "where do I start", "start here", "project rules"} across all three operator dialects?

### §2.4 docs/topics/ (fourth priority — aboutness anchors)

**Why:** Semantic retrieval targets topic files for ABOUT_TOPIC queries (CONCEPTUAL family + some DISCOVERY). We have 11 topic files each ~500-1500 lines. Do topic file titles + first-1000-tokens match "explain X" / "how does X work" / "what is X" query shapes with high recall?

**Audit question:** For each topic file, generate 3 CONCEPTUAL query variants (explain/what is/how does) and measure whether the topic file is top-3.

### §2.5 /docs/research/domains/ (fifth priority — domain audits)

**Why:** Filename stems (`NN01_<slug>_<topic>_audit.md`) map to IDENTITY family well (I2/I3/C4 corpus rows validate). But their INTERNAL retrievability — can operators find "the audit about docs restructuring T3 human pain" — is untested. Real operator queries won't use literal filename stems.

**Audit question:** For each domain audit file, generate a natural-language description of what the audit covers and measure whether the file is top-3.

### §2.6 PLATFORM_WHAT_IT_IS vs PLATFORM_INVENTORY distinction (sixth priority — CONCEPTUAL)

**Why:** K4 "why do we have both PLATFORM_WHAT_IT_IS and PLATFORM_INVENTORY" is the exemplar CONCEPTUAL query in the Phase-0 corpus. CLAUDE.md anchor block distinguishes them (narrative vs runtime). K4 was classified correctly by Classifier A + B, but Classifier A predicted CONCEPTUAL with `has_literal_identifier=true` — a corner case worth watching.

**Audit question:** Does the CLAUDE.md anchor block still hold as the canonical answer to distinction questions, or has semantic drift made a different doc more retrievable for this query family?

---

## §3. What Phase-0 evidence should be folded back into /docs/

Three levels: constitutional (repo bootstrap), working-directory (Phase-0 artifacts), and pattern (research OS).

### §3.1 Constitutional-level integrations

**docs/RETRIEVAL_ASSUMPTIONS.md (new — recommended deferred to post-Phase-0.5).** Captures the 4 assumption findings from §1 as forward-looking guidance. Any /docs/ change proposing to affect retrieval must reference this doc. Not authored yet because Phase-0.5 will provide fuller evidence — but skeleton should be drafted in S2823.

**CLAUDE.md anchor block (immediate).** Add note that "PLATFORM_WHAT_IT_IS = narrative anchor / PLATFORM_INVENTORY = runtime anchor" distinction is now retrieval-tested via Phase-0 corpus row K4. Small addition to existing anchor block.

**docs/DOC_LIFECYCLE.md §2c refresh (deferred to post-Phase-0.5).** Currently claims PLATFORM_INVENTORY is sole authoritative counts source. Post-Phase-0.5 will have retrieval-tested proof (or refutation) of this convention across balanced P1 rows. Update §2c with retrieval-tested claim once evidence in hand.

### §3.2 Working-directory-level integrations

**Phase-0 corpus (`docs/research/discovery_layer/PHASE_0/corpus.json`) becomes the standing benchmark.** Any future PR affecting retrieval MUST run the classifier evaluation harness (`analyze.py`) + attach per-family + per-provenance-tier results to the PR body. Establish as convention now; codify in Playbook when second corroborating trigger arrives.

**field_dictionary.md schema v0 becomes the reference schema.** Any future labeled corpus in the retrieval stack (Phase-0.5 expansion, downstream Phase-1 corpora, other domains) uses this schema as v0 baseline.

**analyze.py becomes the reference measurement harness.** Standard output: per-family precision/recall/F1 + confusion matrix + provenance-tier stratified + wrong-but-plausible catalog + collapse-candidate verification + POINT-vs-LOCATE check. Any new measurement report should output this shape.

### §3.3 Pattern-level integrations (research OS)

**R1 provenance discipline extension (docs/research/DOMAIN_RESEARCH_PLAYBOOK.md).** Extend to require R1 tier-hierarchy labeling in any classifier/routing/retrieval arc. Not just Phase-0.5 — any research group that touches retrieval. Chris's Playbook v0.10 amendment candidate (S2822 = trigger 1 per §20) will formalize this; interim guidance can land in the research OS.

**"P1-vs-P3 accuracy gap" as standing diagnostic.** Becomes a required question in every future measurement report: "What is the P1-vs-P3 accuracy gap?" If undetermined or > 30 pts, findings are flagged as potentially unrepresentative.

**Bridge-deliverable pattern (this doc itself).** Author-directive from Chris to reconnect Phase-X findings to their originating arc is a novel handoff-shape. If pattern recurs (2+ future arcs), consider Playbook amendment for "bridge deliverable" as canonical arc-transition artifact.

---

## §4. Documentation changes required BEFORE Phase-0.5 begins

Sorted by required vs recommended vs deferred.

### §4.1 REQUIRED before Phase-0.5 (must land in S2822 close cascade OR at S2823 open)

1. **CLAUDE.md** — no changes required to the CLAUDE.md body itself for Phase-0.5 to begin; the Phase-0 envelope + this bridge deliverable are canonical enough. Reserved for post-Phase-0.5 refresh with retrieval-tested claims.
2. **docs/research/OPEN_ARCS.md** — add Phase-0.5 arc entry; close Group 2700 §8 item #1 discovery-layer sub-arc with pointer to Phase-0 recommendation + Phase-0.5 continuation. **This is the only required doc change.** Recommended at S2823 open before Phase-0.5 execution.

### §4.2 RECOMMENDED parallel with Phase-0.5

3. **docs/research/ARCHITECTURE_INDEX.md** — timeline entry for S2822 Phase-0 methodology-outcome-primary + OPTION A-DUAL. Non-blocking; can land at Phase-0.5 close cascade.
4. **docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md** — append post-2817-close addendum linking to Phase-0/0.5 findings that emerged from the arc. Non-blocking; can land at Phase-0.5 close or later.
5. **Draft docs/RETRIEVAL_ASSUMPTIONS.md skeleton** — capture the 4 findings from §1 as forward-looking guidance. Skeleton in S2823; full authoring after Phase-0.5.

### §4.3 DEFERRED to post-Phase-0.5

6. **DOC_LIFECYCLE.md §2c refresh** — needs Phase-0.5 evidence base first
7. **docs/topics/ audit** — needs Phase-0.5 balanced P1 corpus first
8. **CLAUDE.md anchor block enrichment** — needs Phase-0.5 pointer-query evidence first
9. **/docs/research/domains/ retrievability audit** — parallel to Phase-0.5 P1 harvest; can begin S2824+

---

## §5. Recommended S2823 first-session plan — dual-track continuation

S2823 opens as CONTINUATION of the discovery-layer + /docs/ restructuring arcs. Not a new project. The dual-track ensures /docs/ audit doesn't drift while Phase-0.5 evidence grows — both feed each other.

### §5.1 Session-open protocol (~10 min)

1. `context-kit orient`
2. Read `00-START-NEXT-SESSION.md` end-to-end
3. Read S2822 handoff (`SESSION_2822_PHASE0_EXECUTION_OPTION_A_DUAL.md`) §3 novel precedent + §6 candidates + §7 lessons
4. **Read this bridge deliverable end-to-end** — reconnects Phase-0 findings to /docs/ audit
5. Read S2822 envelope §9 D-verdict + §10 methodology outcome + §11 Phase-0.5 direction
6. Sanity checks (postgres + ledger row count)
7. Mint fresh pin scoped `s2823-phase0-5-dual-track`

### §5.2 Track A: /docs/ audit reconnection (~30% session budget)

**A1. Update `docs/research/OPEN_ARCS.md`** — add Phase-0.5 arc entry; close Group 2700 §8 item #1 discovery-layer sub-arc; ensure Phase-0/0.5 is documented as the natural continuation. THIS IS THE ONLY REQUIRED CHANGE for Phase-0.5 to begin.

**A2. Draft `docs/RETRIEVAL_ASSUMPTIONS.md` skeleton** — capture the 4 findings from §1 above. Do NOT publish as v1; leave as skeleton with placeholder "Phase-0.5 evidence pending" for each assumption. Full authoring after Phase-0.5 closes.

**A3. Spot-check §2.3 CLAUDE.md #6 pointer chunk retrievability** — one-command probe: `python -c "from core.services.td_handlers_ops import ...; run search_docs on ['the next session start doc', 'where do I start', 'start here']"`. Record results. Log a fold if pointer discipline is broken; do NOT fix during Phase-0.5 (per Chris R3 preserve directive on non-DISCOVERY intents).

**A4. (Optional) Spot-check §2.2 handoff retrievability** — pick 3 recent handoffs; generate natural-language descriptions Chris would use to find them; check top-3 hits. Fold findings; do NOT fix.

### §5.3 Track B: Phase-0.5 evidence collection (~60% session budget)

**B1. Author balanced P1 harvest plan** (route via Rigby SIGN before execution).

Concrete harvest sources per operator-style:
- **Chris-originated queries:** Chat UI conversation history via `conversation_tool.search`; Chris directives in handoffs where question shape is captured (e.g., "Chris asked X")
- **Claude-originated queries:** Handoff mentions of `rg`/`grep`/`search_docs` invocations by Claude during previous sessions; PR descriptions with search patterns
- **Rigby-originated queries:** Prior `kb_tool.semantic_search` + `search_docs` + `deliverable_tool.search` calls documented in handoffs (like S2822 P1 rows R1-R5)

Target: n≥5 per operator style, n≥20 total minimum. Balanced not just in count but in query shape (COUNT/DISCOVERY/IDENTITY/etc.) if possible.

**B2. Build feature-flag advisory-only router scaffolding** — reuse `classifier_a.py` as the routing decision engine (best safety per zero wrong-but-plausible + best F1 on HIGH-consequence families). Add `settings.PHASE_0_5_ROUTER_ENABLED` feature flag; wire into a single call site (recommend `core/services/td_handlers_ops.py:5905` kb_tool.semantic_search handler as instrumentation point). Log per envelope §9 R2 spec.

**B3. Author `docs/research/discovery_layer/PHASE_0_5/ABSTAIN_POLICY_PROPOSAL.md` skeleton** — 3 sections for AMBIGUOUS / UNCLASSIFIABLE / CONTEXT_NEEDED with fallthrough options: (a) clarify with user via clarifying question, (b) default substrate (lexical for HIGH-consequence, semantic for CONCEPTUAL), (c) parallel retrieval both substrates + present both, (d) no action / return current-best. Route via Rigby SIGN then to Chris for D-verdict.

**B4. Route Phase-0.5 stop-condition to Chris for ratification** — default per Rigby SIGN: n≥20 P1 with accuracy ≤30-40% → routing-from-text-alone NOT viable. Chris ratifies at S2823 close or S2824 open.

### §5.4 Track A ↔ Track B feedback loop

The dual-track ensures each track feeds the other:
- Phase-0.5 P1 harvest (B1) generates real operator queries → those queries reveal /docs/ retrievability gaps → gap findings feed docs/RETRIEVAL_ASSUMPTIONS.md (A2) → assumptions doc guides which docs get restructured in future arcs → restructuring is validated by re-running Phase-0.5 corpus.
- /docs/ retrievability audit (A3/A4) surfaces DISCOVERY-shape failures → those failures become additional P1/P2 corpus rows → grows Phase-0.5 evidence base.

### §5.5 Close cascade at S2823 close

Standard 4-step (build_docs_index → build_rag_corpus → sync → embed) + build_docs_provenance. Persist S2823 folds. Update 00-START for S2824.

---

## §6. Framing for the next Claude session

S2823 should feel like continuing a documentation + architecture arc that has been evolving through S2817 (/docs/ restructuring arc close) → S2818/S2819/S2820 (lexical branch) → S2821 (semantic branch) → S2822 (routing-first methodology validated) → S2823 (Phase-0.5 evidence + /docs/ audit dual-track).

The frame is NOT "we're building a router now." The frame is "we're still auditing /docs/ retrievability — the routing question is a lens for that audit, and Phase-0.5 evidence collection is how we gather ground truth."

**Continuity artifacts:**
- Group 2700 arc (S2811-S2817) opened the /docs/ audit
- Group 2700 §8 item #1 (S2818-S2822) executed discovery-layer sub-audit
- Phase-0 (S2822) validated the methodology
- Phase-0.5 (S2823+) collects the evidence
- Post-Phase-0.5 continues the /docs/ audit with retrieval-tested claims

The router is a means, not the end. The end is a /docs/ substrate that retrieves reliably for real operator queries.

---

**End of bridge deliverable. Reconnects Phase-0 findings to /docs/ audit arc. Required reading at S2823 open before Phase-0.5 execution or /docs/ audit resumption.**

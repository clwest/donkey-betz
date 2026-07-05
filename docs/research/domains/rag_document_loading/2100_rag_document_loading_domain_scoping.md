---
title: "RAG / Document Loading Domain Scoping (Group 2100 — The Knowledge Loop Arc)"
session: 2100
status: active (formal S2100 arc-open 2026-07-04 post-S2099 Group 2000+ close; Chris D-override at S2099 close ratified RAG Document Loading over playbook §22 default queue)
arc: Research Group 2100 (RAG / Document Loading — Knowledge Loop framing, Chris + Claude conceptual)
category: research (playbook §11.1 parent-scoping template EIGHTH application)
authors: Claude Code (Chris-directed pre-arc draft 2026-07-04 during S2002 with 10-point framing directive; W1-W3/W7/W9/W11 revisions applied 2026-07-04 per Chris critique fold; formal S2100 arc-open 2026-07-04 post-S2099 close)
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                                # runtime counts
  - docs/PLATFORM_WHAT_IT_IS.md                                               # narrative anchor
  - docs/KNOWLEDGE_PIPELINE.md                                                # existing flow map
  - docs/research/platform_architecture_inventory.md                          # S1273 §3.14 RAG / Document Loading row
  - docs/research/platform/cross_domain_integration_audit.md                  # S1274 cross-domain integration
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                 # process contract
  - docs/research/domains/memory/1300_memory_domain_scoping.md                # boundary with Group 1300
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md     # S1301 retrieval lanes
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md # S1302 persistence
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md       # S1304 docs↔RAG boundary
  - docs/research/domains/memory/1399_memory_canonical_summary.md             # Group 1300 close
delegated_from:
  - Group 1300 Memory arc — S1304 docs↔RAG boundary audit surfaced G5 "boundary unowned" + T-tier debt items T1 (provenance-index rebuild cadence unmanaged) + T2 (`lru_cache(1)` staleness); routed forward as post-S1399 design-preparation
  - Group 1300 canonical summary S1399 §19 — R5 turn-context → RAG enrichment design-preparation
  - Group 2000+ Event / Integration Architecture arc (in-flight, pending S2099) — SPIDER_DATA stream MISSING producer / WEAK consumer (S2001 F3), suggests spider-data → RAG ingestion path is under-specified
delegates_to:
  - (arc-close will populate)
lens: >
  "Is Rigby's RAG corpus a passive document search index, or is it a
  governed institutional knowledge layer that can reliably shape future
  research, SIGN cycles, and platform decisions?"
playbook_application: §11.1 20-section parent-scoping template EIGHTH application (after S1300 first + S1400 second + S1500 third + S1600 fourth + S1700 fifth + S1800 sixth + S1900 seventh + S2000 eighth); §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline applied pre-draft + at arc-open verification; §15 SIGN cycle 1 REQUIRED at parent scoping — routed via Group 2100 arc pin `pa-18b095bb7c4740be` (minted at S2100 open via session_tool.create_fresh per playbook §16 arc-open fresh-thread discipline); §16 arc pin: `pa-18b095bb7c4740be` ACTIVE at S2100 open per NINTH formal arc (Groups 1300/1400/1500/1600/1700/1800/1900/2000+ prior); prior `pa-dd7e973617da464d` retired at S2099 close (retired=true, updated_count=35)
arc_open_provenance:
  - Chris D-override at S2099 close 2026-07-04 ratified Group 2100 = RAG Document Loading over playbook §22 default queue (per project_2100_plus_queue_ranking.md draft with RAG elevated to #1)
  - Parent scoping draft written 2026-07-04 in parallel with S2002 Group 2000+ P2 child (parallel-safety framing preserved in appendix for provenance)
  - W1-W3/W7/W9/W11 revisions applied 2026-07-04 per Chris critique fold
  - Formal arc-open executed 2026-07-04 post-S2099 close per §9.3 nine-step sequence (steps 1-3: draft flip + this doc; steps 4-9: OPEN_ARCS + ARCHITECTURE_INDEX + 00-START-NEXT-SESSION + arc pin mint (executed 2026-07-04, pa-18b095bb7c4740be) + Rigby SIGN cycle + D-verdict ratification + cascade)
---

# Group 2100 — RAG / Document Loading Domain Scoping (The Knowledge Loop Arc)

> **ACTIVE.** Formal S2100 arc-open executed 2026-07-04 post-S2099 Group 2000+
> canonical summary close per Chris D-override ratification. Group 2100 arc
> pin `pa-18b095bb7c4740be` minted at open via `session_tool.create_fresh`.
> Rigby SIGN cycle 1 REQUIRED on this parent scoping per playbook §15.
> Parent scoping originally drafted parallel-safely during S2002 (see
> Appendix A.5 for provenance).

> **Central lens question (Chris-set 2026-07-04; refined via Rigby SIGN
> cycle 1 Q3 STRENGTHEN 2026-07-04 as maturity form):**
>
> *Binary form (retained as rhetorical hook):* "Is Rigby's RAG corpus a
> passive document search index, or is it a governed institutional
> knowledge layer that can reliably shape future research, SIGN cycles,
> and platform decisions?"
>
> *Maturity form (Q3 fold — falsifiable evaluative test):* "Where on the
> spectrum from passive index → governed institutional knowledge layer
> does Rigby's corpus currently sit, and what contracts (authority /
> freshness / governance / behavior) are required to reach the next
> maturity tier?"
>
> **Institutional-knowledge-layer acceptance criteria** (Q3 fold —
> "governed institutional layer" defined with falsifiable minimums; P3
> and P4 audit against these):
> 1. Every canonical summary + closed child audit is embedded within
>    the cascade-close window
> 2. Retrieval authority framework returns non-conflicting authorities
>    for ≥95% of query classes tested
> 3. Superseded docs are demoted or excluded from top-k retrieval for
>    "current truth" queries
> 4. Corpus health score is trackable + interpretable
> 5. Freshness-bounds and authority conflicts surface visibly (not
>    silently) at retrieval time

> **Arc frame (Chris + Claude *conceptual* framing, NOT inherited canonical
> doctrine):** Group 2100 is framed as the **Knowledge Loop arc**.
>
> **Verification note (W11 fix, verified 2026-07-04):** S1799 (Group 1700
> Observability canonical summary) uses NO "loop" framing. S1899 (Group 1800
> HumanAttention canonical summary) uses "learning-loop-coupling contract"
> ONCE, in a specific finding on auto-approve short-circuit (not as
> arc-wide frame). The loop triad below is therefore a Chris + Claude
> conceptual framing proposed 2026-07-04, NOT inherited canonical doctrine.
> Group 2100 may adopt it IF Chris ratifies at formal arc open.
>
> The proposed conceptual framing:
> - **Group 1700 = execution / observability lens (retro-fitted)** —
>   can we prove what happened?
> - **Group 1800 = human feedback / learning lens (retro-fitted; partial
>   S1899 finding-level support)** — should the system change because of
>   what happened?
> - **Group 2100 = knowledge lens (proposed)** — how does validated
>   research / code / doc knowledge become operational memory that
>   improves Rigby's future behavior?
>
> **Loop-closure rubric (Rigby SIGN cycle 1 Q1 STRENGTHEN 2026-07-04):**
> - **Execution Loop** = execution signals feed ops governance
> - **Learning Loop** = human feedback feeds preference / skill updates
> - **Knowledge Loop** = corpus governance feeds retrieval behavior +
>   decisions
>
> **Q1 fold canonical disclaimer (Rigby SIGN cycle 1 2026-07-04):** The
> "three loops" model (Execution / Learning / Knowledge) is a Group 2100
> organizing taxonomy proposed by Claude + Chris. It is NOT asserted as
> inherited doctrine from Groups 1700 / 1800; those arcs can be
> retro-mapped into this schema, but their original summaries do not
> consistently use "loop" language. Future arcs should treat this as
> Group-2100-organizing-taxonomy, not doctrine.
>
> Not RAG plumbing. The framing is: *how architectural truth becomes
> retrievable, fresh, governed, and behavior-shaping inside Rigby.*

> **Conceptual model (Chris-set 2026-07-04):**
>
> ```
> Reality  → Research → Knowledge → Behavior
> ```
>
> - **Reality** — actual code, runtime, docs on disk
> - **Research** — Claude + Rigby audits that discover validated truths
> - **Knowledge** — embedded, canonicalized, cited RAG corpus
> - **Behavior** — Rigby using that knowledge to SIGN, reason, warn,
>   retrieve, guide future work
>
> **Group 2100 audits the transitions Research → Knowledge and Knowledge →
> Behavior.**

> **Load-bearing hypothesis (Chris-set 2026-07-04, to be TESTED not assumed):**
> Rigby's SIGN / verifier-loop quality is bounded by RAG freshness and corpus
> correctness. If RAG is stale, incomplete, incorrectly chunked, or missing
> canonical metadata, every future arc inherits degraded review quality.

---

## 1. Why Phase 0 (parent-first, not single-audit)

Group 2100 requires parent scoping (Phase 0) rather than a single-audit
arc for four reasons:

**(1) Coverage-vs-scope mismatch in the S1273 §3.14 row.** The inventory
row labels RAG / Document Loading as **DEEP** research coverage, but that
label reflects prior *retrieval-lane* work (Group 1300 S1301) plus prior
*boundary-lens* work (Group 1300 S1304). Neither covered the ingestion
side (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents`
→ `embed_documents`) as a first-class subject. Nor did they audit corpus
hygiene, cascade governance, retrieval authority hierarchy, or the
behavior-substrate hypothesis. A single-audit arc would either
under-cover this or over-collapse into the retrieval-lane work Group 1300
already did.

**(2) Depth/lens distinction with Group 1300 requires explicit framing
(W2 revision).** Group 1300 already touched the docs↔RAG boundary
substantively — S1304 (Documentation Corpus ↔ RAG Boundary Audit)
covered `build_docs_index`, `build_rag_corpus`, `Document` /
`DocumentEmbedding` at the boundary, cascade discipline (G1), cache
staleness (G3), boundary ownership (G5), and shipped 5 T-tier
boundary-relevant debt items. **Group 2100 is NOT "new territory."**

Corrected working distinction (depth/lens, not different substrate):

- **S1304 = Memory-era boundary audit** — LIGHT→MODERATE coverage
  per §12; boundary-integration lens from within the Memory domain.
  Focused on *how RAG touches memory/retrieval*, not on the RAG
  substrate as its own subject. Ingestion side covered as a
  handoff-flow inventory, not as a first-class subject.
- **Group 2100 = dedicated RAG / document-loading domain arc** —
  promotes the substrate that S1304 audited-at-the-boundary into
  its own first-class DEEP-coverage domain. Focused on ingestion,
  embedding, freshness, corpus governance, metadata authority,
  cascade enforcement, retrieval authority framework, and
  behavior-substrate impact — none of which S1304 designed or
  ratified as its own subject.

**Reframed positional statement:** *Group 1300 exposed and partially
bounded the RAG / document-loading surface; Group 2100 promotes that
surface into its own first-class architecture arc.* Without a parent,
Group 2100 would either duplicate S1304 findings under new framing or
drift into scope S1304's boundary-lens didn't cover.

**(3) Knowledge Loop framing has cross-cutting lenses.** Chris's 10-point
framing (Knowledge Loop triad, Reality→Research→Knowledge→Behavior model,
retrieval authority hierarchy, research-debt → knowledge-debt) applies
across multiple child audits. A parent-first approach ensures these
lenses are locked before any child audit starts, so children can
consistently apply them rather than re-establishing framing each session.

**(4) Governance-before-implementation constraint.** Chris explicit
directive (point 9): parent scoping produces domain definition, existing
knowledge inventory, success criteria, child audit sequence, load-bearing
questions, non-goals, delegated scopes, follow-on implementation
candidates. No implementation before ratified scoping. This shape
requires a parent-plus-children arc, not a single audit.

---

## 2. What existing inventory already tells us

### 2.1 Prior research chain (Groups 1300 – 2000+)

| Group | Domain | Coverage relevant to Group 2100 | Handoff |
|-------|--------|--------------------------------|---------|
| 1300 Memory | AI/user memory + two RAG retrieval lanes | S1301 retrieval-lane audit + S1302 persistence + **S1304 docs↔RAG boundary audit** | S1304 G5 "boundary is unowned" + T1 provenance-index rebuild cadence + T2 `lru_cache(1)` staleness; S1399 §19 R5 turn-context → RAG enrichment design-preparation |
| 1700 Observability | Execution + observability loop | 5-layer telemetry dedup pattern applicable to embedding pipeline observability | (indirect — pattern only) |
| 1800 HumanAttention | Human feedback + learning loop | Six-plane learning fragmentation pattern; T0/Gate items on RAG-adjacent surfaces | (indirect — Group 2100 will use pattern) |
| 1900 Authority Enforcement | Precedence policies + composition | §17.1 Plane Precedence Policy pattern applicable to retrieval authority hierarchy | (pattern reuse) |
| 2000+ Event / Integration | EventBus + HAI events | **S2001 F3 SPIDER_DATA MISSING producer / WEAK consumer** — spider-data → RAG ingestion path under-specified; **S2001 F9 CRITICAL dormant consumer** — pattern for stale-cascade risk | (in-flight; final delegations pending S2099) |

### 2.2 What S1273 §3.14 tells us (the row, condensed)

**Two lanes, one chunking strategy split:**
- **PROD lane** — `core/rag_integration.py:465` + `Document` /
  `DocumentEmbedding` tables. Chunking configurable (`chunk_size`,
  `overlap_size`, `context_before`, `context_after`). HNSW index on
  `embedding_vector` (1536D OpenAI). Semantic search.
- **LOCAL lane** — `core/rag.py:81` + `.rag/corpus.jsonl`. Fixed
  1200-char chunks (no semantic boundary preservation, string prefix
  ops). Gitignored. Token-overlap keyword ranker.

**Ingestion commands:** `build_docs_index`, `build_rag_corpus`,
`sync_docs_index_to_documents [--embed]`, `embed_documents`,
`backfill_spider_embeddings`.

**Known gap in the row itself:** "Embedding cadence for documents
**UNKNOWN**" — an inventory row admitting its own blindspot.

**Existing docs:** `docs/topics/local-askdocs.md` (S1108 LOCAL vs PROD
lane boundary), `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`,
`docs/KNOWLEDGE_PIPELINE.md`.

### 2.3 What S1304 (Group 1300 boundary audit) already covered (W2 revision)

S1304 audited the docs↔RAG boundary as a LIGHT→MODERATE-coverage
boundary-integration lens **from within the Memory domain**. Findings
become the *starting inventory* for Group 2100's first-class
substrate arc (not delegated-forward gaps — actively-audited
findings that Group 2100 deepens):

- **G1** — Cascade discipline (`build_docs_index` → `build_rag_corpus` →
  `sync_docs_index_to_documents [--embed]`) is *documented only in
  MEMORY.md workflow rules*, not in code or docs governance. First-class
  governance is missing.
- **G3** — `_load_provenance_docs()` uses `lru_cache(1)`; provenance-index
  updates after cascade don't invalidate the cache until process restart.
- **G5** — Boundary is unowned. No `AIEmployee` handle in
  `core/employees/jobs.py` binds to the E↔D handoff. Discovery-side
  (Documentation Manager) and consumption-side (`kb_tool` handlers) exist
  independently.
- **T1 (HIGH)** — `provenance-index` rebuild cadence unmanaged.
- **T2 (HIGH)** — `lru_cache(1)` manual invalidation.
- **T3 (MEDIUM)** — Two provenance systems partially decoupled.

**S1399 canonical summary §19 R5** — turn-context → RAG enrichment routed
to design-preparation post-S1399. Group 2100 owns this.

**Positional statement (W2 revision):** Where S1304 asked *"does the
boundary function?"* Group 2100 asks *"what governance, hygiene,
authority framework, and behavior substrate does this deserve?"* Same
substrate, different depth. Where S1304 handled the ingestion side as
a flow-inventory item, Group 2100 P2 audits it as a first-class
subject. Where S1304 flagged G5 boundary-unowned, Group 2100 P3
designs a governance model.

### 2.4 What MEMORY.md workflow rules already imply

Three memory rules encode ad-hoc RAG governance currently outside any
formal doc:

1. **`feedback_docs_pipeline_4_step_cascade.md`** — the 4-step cascade is
   NOT one step. `build_docs_index` alone refreshes only the file index;
   full visibility requires `build_rag_corpus` → `sync_docs_index_to_documents`
   → `sync_docs_index_to_documents --embed` (or `embed_documents
   --all-unembedded`). Session 1234 close found 12-day-stale prod corpus
   + 1820 docs never pushed.
2. **`feedback_docs_cascade_at_every_close.md`** — cascade runs at every
   arc / session close-out. Not doing this = Rigby search stale +
   long-term research continuity degrades. Chris directive S1399 close.
3. **`feedback_cascade_pr_must_include_embed_step.md`** — cascade PR must
   include step 4 embed, not just steps 1-3 sync. S1802 close 2026-07-03
   caught 6 unembedded docs — S1802 audit + handoff PLUS S1800 parent +
   handoff + S1801 audit + handoff (all previously synced but NEVER
   embedded). Rigby's RAG was blind to entire Group 1800 arc from S1800
   open through S1802 close (~2 sessions).

**These are informal patches on an unaudited substrate.** Group 2100
should formalize them into first-class governance (cascade discipline,
freshness detection, embedding verification, coverage assertions in CI).

### 2.5 What Group 2000+ inheritance (S2001, in-flight) tells us

S2001 P1 Cat A EventBus Producer/Consumer Map (S2001 handoff summary):
- **F3 SPIDER_DATA MISSING producer / WEAK consumer** — spider-data
  ingestion path to RAG is under-specified. Group 2100 P2 (ingestion
  pipeline) should audit whether spider-data flows to `DocumentEmbedding`
  via `backfill_spider_embeddings` cleanly or drops silently.
- **F9 CRITICAL consumer-beat-dormancy** — pattern for stale-cascade
  risk. Applies to backfill embeddings if beat schedule fires but
  workers aren't processing.

Group 2000+ P2 (S2002, in-flight) and later children may add more
inheritance to Group 2100 before S2099 arc close. Formal arc-open
scoping should re-verify.

---

## 3. Candidate subdomain taxonomy

Three taxonomies considered:

### 3.1 Option (a) — 3-child (minimal)

- **P1** Corpus state + freshness detection
- **P2** Ingestion / chunking / embedding pipeline
- **P3** Retrieval authority + governance design
- **xx99** Canonical summary

**Pro:** Fastest to arc-completion (~4 sessions). Matches Group 1300
S1300 shape without CONSOLIDATION.
**Con:** Behavior-substrate hypothesis (Chris point 5) doesn't get its
own child — folded into P3 where it competes with governance framing.
Central lens question testing under-served.

### 3.2 Option (b) — 4-child + xx99 (MY LEAN)

- **P1 (Cat A)** — **Corpus State: Reality→Knowledge Gap Audit** (S2101)
- **P2 (Cat B)** — **Ingestion / Chunking / Embedding Pipeline Audit** (S2102)
- **P3 (Cat C)** — **Retrieval Authority + Corpus Governance Design** (S2103)
- **P4 (Cat D)** — **Behavior Substrate: SIGN-Quality Testing + Integration** (S2104)
- **xx99** — Canonical summary (S2199)

**Pro:** Each of Chris's 10 additions maps to a specific child (see §5
below). Behavior-substrate hypothesis gets its own testing slot (P4).
Matches Group 2000+ arc shape (4-child + xx99 = 5 sessions total).
**Con:** ~5-session commitment. P4 depends on P1-P3 findings so cannot
be parallelized.

### 3.3 Option (c) — 5-child + xx99 (MC-4 durability)

- P1 corpus state
- P2 ingestion pipeline
- P3 retrieval authority hierarchy design
- P4 corpus governance design (split from P3)
- P5 behavior substrate + integration
- xx99

**Pro:** Splits P3 governance from retrieval authority — cleaner
separation. Extends MC-4 CODIFICATION-CONFIRMED-with-scope-guardrails
observation (S1999).
**Con:** ~6-session commitment. P3/P4 close-coupled, would likely
consolidate mid-arc.

### 3.4 Recommended taxonomy: Option (b) — 4-child + xx99

**Rationale:**
- Chris's 10 additions map cleanly to 4 child slots without under-covering
  or over-splitting.
- Behavior-substrate hypothesis (Chris point 5) is load-bearing — deserves
  its own child (P4) not a subsection.
- 5-session commitment matches Group 2000+ arc shape — consistent with
  playbook §11.1 template EIGHTH application.
- Central lens question ("passive index vs governed layer") tests via P4
  before xx99 synthesis.

**PENDING Chris D-verdict at formal arc open (post-S2099).**

**Q4 fold (Rigby SIGN cycle 1 STRENGTHEN 2026-07-04):** *Option (b) is
retained even after the P4 reframe: P4's scope is smaller in engineering
cost but still distinct in evidence type and necessary to close the
"Knowledge Loop" claim (how corpus state + retrieval authority actually
shapes downstream agent behavior and decisions).* P4 anti-scope cap: P4
is **evidence assembly + pattern extraction + integration implications**,
NOT new instrumentation build.

**Q5 fold (Rigby SIGN cycle 1 STRENGTHEN 2026-07-04) — belongs-to
boundary rules (prevent P1↔P2 and P3↔P4 leakage):**

- Any sentence starting with **"currently"** / "as of now" → P1 or P4
  (state / behavior)
- Any sentence starting with **"should" / "must" / "contract"** → P3
  (normative framework)
- Any sentence starting with **"step-by-step" / "pipeline" / "when X
  happens"** → P2 (process)
- **P1 deliverable** = gap matrix + metadata inventory (static
  snapshot) with only *high-level* "likely cause" tags — does NOT
  explain causality beyond brief hypotheses
- **P2 deliverable** = causal chain + failure modes + cadence design
  (dynamic process), referencing P1's matrix as baseline
- **P3 deliverable** = normative + design (what should be true;
  authority axes; governance disambiguation; conflict resolution)
- **P4 deliverable** = empirical + integration (what is true in
  practice; retrospective patterns; how to wire observability + UX so
  the P3 framework is enforceable)

---

## 4. Parent-vs-single recommendation

**Recommendation: PARENT.** See §1 (Why Phase 0) for full rationale. The
4-child taxonomy in §3.4 is designed to be run as a coordinated arc, not
independently.

**Runtime target for parent commit:** ~800-1200 lines (leaner than Group
2000+ parent at ~1450 because prior-research chain is shorter — Group
2100 inherits from 3 prior arcs, Group 2000+ inherited from 7).

---

## 5. Child mission sequence (Chris-locked pending D-verdicts at formal arc open)

Each child listed below with (a) scope, (b) which Chris directive
additions it covers, (c) load-bearing questions, (d) delegation from
prior work, (e) expected shape.

### 5.1 P1 — Corpus State: Reality→Knowledge Gap Audit (S2101)

**Scope.** Audit the current state of the RAG corpus as it exists today.
Answer: what documents exist on disk (Reality), what's in the Document
table (Research → institutional record), what's embedded and retrievable
(Knowledge), and where the gaps are.

**Covers Chris directive additions:**
- **Point 3** (Reality→Research→Knowledge→Behavior model) — establishes
  Reality→Knowledge measurement baseline for the arc
- **Point 6** (RAG artifact metadata inventory) — inventories whether
  embedded docs carry or can derive the 18 metadata fields; ROI-trim
  aspirational vs schema-backed vs derivable
- **Point 8** (research-debt → knowledge-debt framing) — inventories
  knowledge-debt: unembedded docs, stale embeddings, missing metadata,
  duplicated/superseded findings retrieved as current truth
- **Point 4 partial (W7 redistribution)** — Q1 (every closed artifact
  embedded?), Q4 (missing embeddings after cascade PRs?), Q8 partial
  (what metadata EXISTS today at schema level; P3 handles what SHOULD
  be carried)

**Load-bearing questions:**

*Corpus state (Reality → Knowledge gap baseline):*
- What documents exist on disk under `docs/`? (Reality baseline)
- What documents are indexed in `docs/_index.json`? (post-cascade step 1)
- What documents are in `.rag/corpus.jsonl`? (post-cascade step 2)
- What documents have `Document` rows? (post-cascade step 3)
- What documents have `DocumentEmbedding` rows? (post-cascade step 4)
- For each: what's the delta at each step, and how do we detect the
  delta at cascade-close time?

*Governance-question redistribution (W7 fix):*
- **Q1** — How do we know every closed research artifact is embedded?
  (State audit: sample closed xx99 canonicals + latest handoffs →
  verify each has `DocumentEmbedding` rows.)
- **Q4** — How do we detect missing embeddings after cascade PRs?
  (S1802 incident: 6 unembedded docs shipped in cascade PRs. What
  detection mechanism exists / should exist?)
- **Q8-a** — What metadata EXISTS in `DocumentEmbedding` schema
  today? (Presence audit — 4 confirmed from S1304 read: `chunk_index`,
  `embedding_model`, `source_type`, `ingested_via`. P3 designs the
  SHOULD-carry contract.)

*Metadata inventory (Chris point 6, with ROI-trim per R4 risk):*
- Chris's aspirational 18-field list: `research_group`, `session`,
  `domain_slug`, `category`, `child_slot`, `status`, `head_commit`,
  `supersedes` / `superseded_by`, `canonical_summary` flag,
  `parent_doc`, `related arcs`, `T-slot` / `R-slot` references,
  `decisions_locked`, `implementation_status`, `source path`,
  `last_embedded_at`, `content_hash` / `doc_hash`, `embedding_model`,
  `chunking_version`.
- ROI-trim pass required: which are (a) schema-present today, (b)
  derivable from other fields (e.g., `canonical_summary` from
  filename pattern NN99), (c) derivable at ingest time (e.g.,
  `head_commit` at embed time), (d) require frontmatter changes to
  every doc, (e) research-artifact-specific (may over-fit).
- Expected outcome: P1 recommends ~4-8 required + ~4-8 derivable +
  ~4-6 aspirational-for-future, not one flat 18-field mandate.

**Q9 fold (Rigby SIGN cycle 1 STRENGTHEN 2026-07-04) — hybrid contract
shape:** P1 outputs a two-tier metadata contract:

1. **Core required set (global)** — every knowledge artifact MUST
   satisfy to participate in the authority framework (fatal-if-missing
   for P1/P3 reasoning). Candidate categories: *provenance* (source_type
   / ingested_via) + *lifecycle status* (draft/active/canonical/
   superseded/deprecated) + *time* (created / updated / last_embedded_at)
   + *linkage* (supersession pointer + canonical-summary pointer +
   workspace/repo/commit pointer for code-adjacent truth)
2. **Doc-type profile (recommended + optional)** — per class of doc
   (research handoff / inventory / audit / spec / topic doc /
   canonical summary / parent scoping / child audit) with fields that
   actually matter for that class. Prevents frontmatter churn (all
   docs) while ensuring class-appropriate discipline

**Fatal-if-missing categorization** (Q9 fold): P1 audit must
distinguish (a) fatal for P1/P3 reasoning (can't do child audit
without them) vs (b) strongly recommended (query routing +
conflict-resolution accelerators — authority domain, recency proxy,
doc_class, tags) vs (c) derivable at ingest (reliably computed from
path, git metadata, filename pattern) vs (d) aspirational for future
governance layer.

**Q6 fold (Rigby SIGN cycle 1 STRENGTHEN 2026-07-04) — P4 evidence
threshold:** P4 must produce **N ≥ 10 concrete observed cases** (or
patterns) and **map each to one P3 axis + one remediation hook**. This
prevents observation drift into narrative and preserves qualitative
rigor.

**Q2 fold (Rigby SIGN cycle 1 CLEAN + optional STRENGTHEN 2026-07-04):**
Group 2100 treats S1304 as the substrate baseline and does NOT re-audit
boundary existence except where needed to support governance / authority
conclusions.

**Delegated inheritance:**
- S1304 §14 D7 `DocumentEmbedding.ingested_via` orphan claim — full-tree
  recheck routed via S1399 §19 R1
- S1304 §15 T1 provenance-index rebuild cadence — freshness inventory
  side
- MEMORY.md `feedback_cascade_pr_must_include_embed_step` — informalize
  the 6-unembedded-docs incident (S1802) as a knowledge-debt sample

**Expected shape.** ~700-1000 lines. 20-section playbook §11.2 template
child-audit shape. Ships: Reality→Knowledge gap matrix + 18-field
metadata inventory table + knowledge-debt classification framework.

### 5.2 P2 — Ingestion / Chunking / Embedding Pipeline Audit (S2102)

**Scope.** Audit the ingestion cascade end-to-end. `build_docs_index` →
`build_rag_corpus` → `sync_docs_index_to_documents [--embed]` →
`embed_documents`. Plus the two-lane structure (LOCAL keyword vs PROD
pgvector) and chunking strategy analysis.

**Covers Chris directive additions:**
- **Point 2** (do not over-collapse into Group 1300) — S1304 audited
  the boundary as a Memory-lens flow-inventory; Group 2100 P2 audits
  the ingestion substrate as a first-class subject
- **Point 8** (knowledge-debt sources) — chunking mismatch,
  provenance-index staleness, embedding-model drift, doc-change-to-
  embed latency
- **Point 4 partial (W7 redistribution)** — Q3 (detect stale after
  doc change?) + cascade mechanism documentation + refresh triggers
  + doc/content hashing substrate

**Load-bearing questions:**

*Chunking / lanes / cadence:*
- Chunking strategy — LOCAL fixed 1200-char no-boundary-preservation vs
  PROD configurable semantic-boundary-preferred. Are the two lanes
  supposed to return the same docs? If not, what's the intended
  divergence?
- Embedding cadence — S1273 §3.14 admits UNKNOWN. What triggers
  re-embedding? Content change detection? Manual? Never?
- Embedding-model migration — what happens when `embedding_model`
  changes? Are old chunks invalidated? Re-embedded automatically? Left
  stale?
- Backfill flows — `backfill_spider_embeddings` (every 15 min per §3.14)
  + spider-data ingestion path. Inherits S2001 F3 (SPIDER_DATA MISSING
  producer / WEAK consumer).
- Chunking version tagging — do chunks carry `chunking_version` metadata
  so we know which are old vs current strategy?
- Two-lane synchronization — S1108 documented LOCAL vs PROD boundary,
  but is synchronization contract enforced or aspirational?

*Governance-question redistribution (W7 fix):*
- **Q3** — How do we detect stale embeddings after docs change?
  (What content-change-detection substrate exists today? File mtime?
  Content hash? None?)
- **Cascade mechanism** — How does cascade embedding *actually work*
  end-to-end? Document the flow as a mechanism reference, not just
  as command list. Where does each step succeed silently? Fail
  silently? Log?
- **Refresh triggers** — What refresh triggers exist? Manual
  (`embed_documents --all-unembedded`)? Periodic beat
  (`backfill_spider_embeddings` every 15 min)? Event-driven (does
  cascade PR trigger anything)? File-watch (does file change trigger
  anything)?
- **Doc/content hashing substrate** — What `doc_hash` / `content_hash`
  / `chunking_version` / `head_commit` fields exist in schema today?
  What can be added? What's required for automatic stale-detection?

**Delegated inheritance:**
- S1304 G3 `lru_cache(1)` staleness (T2 HIGH) — provenance-index
  invalidation flow
- S1304 §14 D7 `ingested_via` orphan — write-site full-tree recheck
- S2001 F3 SPIDER_DATA WEAK consumer — spider-data → embedding path
  under-specification
- S2001 F9 dormant-consumer risk pattern — backfill beat dormancy check

**Expected shape.** ~800-1100 lines. Ships: cascade flow diagram +
lane-divergence matrix + chunking strategy tradeoff analysis + embedding
cadence proposed design.

### 5.3 P3 — Retrieval Authority FRAMEWORK + Corpus Governance Design (S2103) (W3 + W7 revision)

**Scope.** Design (not implement) two coupled substrates:
(a) a **retrieval authority FRAMEWORK** — NOT a single universal
ranking — with axes and conflict-resolution rules for constructing
query-appropriate authority orderings; (b) corpus governance that
names owner(s) for the E↔D boundary and formalizes cascade discipline
/ artifact lifecycle model across five distinct governance meanings.

**Why framework, not ranking (W3 correction):** The previous draft
proposed `canonical summary > child audit > parent scoping > platform
inventory > old handoff > raw notes` as a hard-coded ranking. That
ranking is defensible on some axes and wrong on others: (i) canonical
summaries are *synthesized* evidence; child audits are *primary*
evidence — for exact implementation questions, child audits should
rank *above* canonicals; (ii) `PLATFORM_INVENTORY` is *runtime
authority* per `DOC_LIFECYCLE.md §2c` inventory-wins-on-conflict —
ranking it below research artifacts contradicts existing policy;
(iii) "old handoff" is not a class — S1268-S1275 foundational handoffs
outrank any parent scoping on methodology; (iv) recency, specificity,
and lifecycle status all matter and no single ranking captures them.
P3 designs the FRAMEWORK; individual retrieval queries construct
appropriate orderings from axes + rules.

**Covers Chris directive additions:**
- **Point 7** (retrieval authority) — designs FRAMEWORK with axes,
  not fixed ranking; explicit conflict-resolution rules
- **Point 4 (W7 redistribution)** — Q5 (superseded outranking
  canonical), Q6 (draft/active/canonical/superseded/deprecated
  distinction), Q7 (Rigby knows finding authoritative), Q8-b (what
  metadata SHOULD every embedded artifact carry — the contract side;
  Q8-a schema-presence handled by P1)
- **Point 9** (governance before implementation) — design-preparation
  only; no ranker code, no schema migrations ship this arc

**Load-bearing questions — retrieval authority framework:**

*Axes to consider (per Chris directive point 7):*
- **Primary evidence vs synthesized evidence** — child audits are
  primary; canonical summaries are synthesized; PLATFORM_INVENTORY is
  runtime-derived (a different primary)
- **Runtime authority vs research authority** — inventory rows are
  runtime authoritative; research artifacts are research authoritative;
  what happens when they disagree
- **Specificity to query** — a query about a specific method may need
  the child audit that named the method; a query about domain shape
  may need the canonical summary
- **Recency / head_commit proximity** — how does the framework weight
  older-canonical vs newer-child when both are authoritative for
  their axis
- **Supersession status** — is the doc superseded by a newer one? by
  a canonical? by an inventory update?
- **Canonical summary status** — has this material been summarized?
  is the summary consistent with the child?
- **Artifact lifecycle status** — draft / active / canonical /
  superseded / deprecated — how does each status affect retrieval
  weight
- **Conflict-resolution rule (candidate)** — *PLATFORM_INVENTORY (or
  runtime inventory) wins on runtime facts*; *child audits win on
  primary implementation evidence*; *canonical summaries win on
  synthesized posture unless contradicted by newer source evidence*;
  *foundational handoffs (S1268-S1275, playbook) win on methodology*

**Q7 fold (Rigby SIGN cycle 1 STRENGTHEN 2026-07-04) — definitional
split + precedence clarifiers + tie-break rule:**

1. **Definitional split** (prevents §2c inventory-wins-on-conflict from
   over-firing):
   - **Runtime facts** = current platform state (registered agents,
     live endpoints, active config, DB schema, beat schedule, health
     checks, etc.)
   - **Research posture** = interpretation, strategy, architecture
     intent, design rationale, recommended plan
   - **§2c inventory-wins applies ONLY inside the runtime-facts
     slice**; outside it, inventory is just another artifact
2. **Precedence clarifiers**:
   - **Supersession / deprecated overrides recency** (something can
     be recent but explicitly superseded — supersession wins)
   - **Canonical summary status** is retained as a designation
     distinct from primary-vs-synthesized evidence type; changes
     default trust only in "posture" questions
3. **Tie-break rule** (when two runtime-authority artifacts disagree):
   prefer **newer measurement timestamp** (freshest probe), else fall
   back to **source-of-truth hierarchy** (e.g., live health endpoint >
   cached inventory doc > human note)

*Deliverable for retrieval authority:* NOT one universal ranking —
instead, a **framework with axes + conflict-resolution rules** that
lets each query construct an appropriate authority ordering. P3 also
ships worked examples showing how the framework resolves 4-6 real
retrieval scenarios.

**Load-bearing questions — corpus governance (W7 redistribution
Q5-Q8, plus governance-term disambiguation):**

*"Governance" disambiguation (per W5 critique):* the term is used
across 5 distinct meanings and must be answered per-axis, not as one
blob:
(i) **ownership** — an `AIEmployee` handle in `core/employees/jobs.py`
    (S1304 G5 flagged as unowned)
(ii) **discipline** — a repeated ritual (currently: cascade-at-close
    per MEMORY.md rule)
(iii) **enforcement** — CI checks, service-side validation, pre-merge
    hooks
(iv) **documentation** — a canonical doc rather than a memory rule
(v) **policy** — a stated contract with defined thresholds and
    escalation paths

Each of the following questions must be answered per-axis:

- **Q5** — How do we prevent superseded docs from outranking canonical
  summaries in specific query contexts? (ownership? discipline?
  enforcement? policy?)
- **Q6** — What lifecycle model applies to embedded artifacts (draft /
  active / canonical / superseded / deprecated)? What triggers each
  status change? Who authorizes?
- **Q7** — How does Rigby know whether a retrieved finding is still
  authoritative? Metadata contract? Cross-reference to supersession
  chain? Freshness threshold? Runtime cross-check with inventory?
- **Q8-b** — What metadata contract MUST every embedded chunk carry
  (required) vs SHOULD carry (recommended) vs MAY carry (optional)?
  Who enforces at schema level? Service level? CI level?
- **Who owns the E↔D boundary (S1304 G5)?** Add an `AIEmployee` handle?
  Reuse existing Documentation Manager (Rigby)? Split ingestion vs
  consumption ownership?
- **What is the minimum cascade discipline** — mandatory at close-out?
  CI-blocking? Advisory? Cost-tiered (mandatory for canonicals,
  advisory for handoffs)?

**Delegated inheritance:**
- S1304 G5 boundary unowned — S1399 canonical summary named it as
  post-S1399 governance decision
- S1399 §19 R5 turn-context → RAG enrichment design-preparation
- Group 1900 §17.1 Plane Precedence Policy pattern — pattern reusable
  for retrieval authority framework CONFLICT-RESOLUTION rule design
  (NOT for a fixed ranking)
- DOC_LIFECYCLE.md §2c inventory-wins-on-conflict rule — locked
  policy that the framework must respect

**Expected shape.** ~900-1200 lines. Design-preparation authority.
Ships:
- Retrieval authority FRAMEWORK (8 axes + conflict-resolution rule
  + worked-example table for 4-6 query scenarios) — NOT a fixed
  ranking
- Corpus governance policy across 5 distinguished dimensions
  (ownership / discipline / enforcement / documentation / policy)
- Boundary ownership assignment proposal (S1304 G5 resolution)
- Cascade governance first-class doc (replaces the MEMORY.md
  informal rules)
- Artifact lifecycle model (draft / active / canonical / superseded /
  deprecated) with transition triggers

### 5.4 P4 — Behavior Substrate: Structured Observation of RAG-Quality → SIGN-Quality Coupling + Integration (S2104) (W1 revision)

**Scope (REFRAMED per W1).** REFRAMED from "controlled experiment" to
**structured observation** (Option A). Retrospectively review recent
Rigby SIGN cycles for documented RAG-quality incidents. Classify how
each affected SIGN quality. Produce qualitative "RAG quality affects
SIGN quality" evidence brief. Then synthesize across P1-P3 findings
and answer the central lens question. Option B (controlled experiment
with isolated test corpus) is parked as post-arc T-slot in §6.3.

**Why observation, not experiment (W1 critique):** No isolated RAG
test harness exists. Rigby's PROD pgvector is a single shared corpus;
isolation pins isolate conversation state, NOT RAG lookup — she pulls
from the same DB regardless of pin. A controlled experiment would
require non-trivial staging infrastructure (staging pgvector or
in-memory HNSW, defined SIGN-quality metrics, blinded scoring or
rubric, non-live Rigby routing). Group 2100 delivers value WITHOUT
building that infrastructure via structured retrospective observation.
The true experiment is parked as post-arc T-slot.

**Hypothesis status:** "RAG freshness bounds SIGN quality" remains a
HYPOTHESIS (per D2100.7). Observation provides *qualitative evidence*
for or against. It does NOT provide the quantitative test the
original framing implied. That distinction must land in the P4 output
so future arcs know what's actually been established.

**Covers Chris directive additions:**
- **Point 5** (RAG freshness → SIGN quality — TEST not assume) —
  qualitative evidence brief via observation, NOT quantitative test;
  hypothesis-status remains hypothesis pending future harness-based
  Option B experiment
- **Point 1** (Knowledge Loop conceptual framing) — validates whether
  the substrate closes the proposed loop
- **Point 3** (R→R→K→B model) — end-to-end Behavior substrate
  validation via observation
- **Point 10** (central lens question) — synthesizes P1-P3 into an
  answer
- **Point 4 partial (W7 redistribution)** — Q9 (minimum corpus hygiene
  for SIGN trust)

**Load-bearing questions (Option A observation-based):**

*Incident review (evidence-brief input):*
- What recent Rigby SIGN cycles had documented RAG-quality incidents?
  Candidates (from memory): S1802 close's 6-unembedded-docs incident
  (Rigby's RAG was blind to entire Group 1800 arc S1800-S1802 through
  cascade PR merge); S1234 close's 12-day-stale prod corpus + 1820
  never-pushed docs; any SIGN cycles where Rigby's findings referenced
  stale / superseded docs as current truth.
- For each: what was the RAG-quality issue (stale / unembedded /
  superseded / missing / mis-chunked)?
- How did it affect SIGN quality — missed findings? wrong findings?
  degraded pressure-test? or no measurable effect at all?
- What signal existed at the time to detect it? Post-hoc it's obvious;
  in-flight what could Rigby / Claude / Chris have seen?

*SIGN-quality gates (Q9 + Chris directive point 4 partial):*
- **Q9** — What is the minimum corpus hygiene required before a SIGN
  cycle is trustworthy?
- What quality gates should future SIGN cycles require *before*
  accepting SIGN output as authoritative? (Candidates: corpus
  freshness threshold; canonical-summary coverage %; latest-xx99
  embedded confirmation; RAG Corpus Health Score threshold per §5.5.)
- What evidence exists that RAG freshness affects SIGN / verifier-loop
  quality? (This is the hypothesis-status question — observation
  provides evidence, not proof.)

*Integration + central lens question:*
- With P1 (state) + P2 (pipeline) + P3 (framework + governance) shipped,
  is the substrate coherent — or are there cross-child inconsistencies?
- Central lens question (Chris point 10) — *"Is Rigby's RAG corpus a
  passive document search index, or is it a governed institutional
  knowledge layer that can reliably shape future research, SIGN cycles,
  and platform decisions?"* — synthesize P1-P3 into a defended answer.

**Delegated inheritance:**
- All P1-P3 findings
- MEMORY.md incident logs (S1802 6-unembedded-docs, S1234 12-day-stale
  cascade, and others surfaced during observation review)

**Expected shape.** ~700-1000 lines. Ships:
- Observation evidence brief (~5-10 concrete incidents classified by
  RAG-quality axis + SIGN-quality effect)
- Behavior substrate validation via observation (qualitative, not
  quantitative)
- Integration matrix across P1-P3 findings
- Central lens question answer (defended, not asserted)
- SIGN-quality quality-gate proposals (referencing §5.5 Corpus Health
  Score dimensions)
- Parked Option B controlled-experiment design as T-slot detail
  (what harness would be needed; what metrics; what infrastructure
  investment before it could run)

### 5.5 Claude-originated proposal — RAG Corpus Health Score (design output candidate)

**What it is.** A composite score (0-100) that measures RAG corpus
health along multiple dimensions. **NOT implemented in this arc** —
designed across P1-P3 as a measurable arc-output, validated in P4
observation. Enables future arcs to assert corpus-quality gates
before SIGN cycles, cascade automation triggers, and observability
dashboards. This is the *Claude-originated proposal* required per
W13 critique — a contribution beyond Chris's 10 directive additions.

**Why it matters.** Gives Group 2100 a **measurable arc output**
without shipping implementation. The arc defines what corpus-health
MEASUREMENT should look like; post-arc execution items (§6.3) can
implement the scorer. Also gives future SIGN cycles a corpus-quality
gate they can reference (e.g., "corpus health > 85 required for SIGN
cycles to operate at usual quality tier"). Ties W1 P4 observation
(qualitative) to future Option B experiment (quantitative) via a
shared measurement vocabulary.

**Proposed dimensions (P1-P3 design each; P4 validates via observation):**

| # | Dimension | Owned by child | Notes |
|---|-----------|----------------|-------|
| 1 | Embedding completeness % | P1 | docs on disk vs docs with `DocumentEmbedding` rows |
| 2 | Stale chunk % | P2 | `last_embedded_at` older than `content_hash` change age (requires P2 hash-substrate design) |
| 3 | Canonical-summary coverage % | P1 + P3 | are all xx99 canonical summaries embedded + carry `canonical_summary` metadata? |
| 4 | Superseded-doc demotion % | P3 | do superseded docs surface below current docs in retrieval per authority framework? |
| 5 | Missing-metadata % | P1 | % of embedded docs with incomplete required metadata (per P3 contract) |
| 6 | Latest closed xx99 embedded? | P1 | binary flag; regressive check on cascade discipline |
| 7 | Retrieval authority conflicts detected | P3 | # of queries where framework returns conflicting authorities per axes |
| 8 | Doc-change-to-embed latency | P2 | median hours from doc save → embedded state |

**Scoring model.** Not fixed. Framework can compose dimensions as
weighted-avg (composite score) OR as pass/fail gate (all dimensions
above per-dimension threshold) depending on use context. P3 designs
the scoring model as a governance artifact.

**Interpretive tiers (candidate — refined per Q11 SIGN fold as
vitals-style dashboard, thresholds operationally-derived not fixed
doctrine):**
- **95-100 GREEN** — SIGN cycles operate at full-quality tier
- **80-94 YELLOW** — SIGN cycles operate but findings flagged for
  Chris review of RAG-quality assumptions
- **<80 RED** — SIGN cycles suppress corpus-quality-dependent
  findings; cascade discipline invocation forced pre-close

**Q11 fold (Rigby SIGN cycle 1 STRENGTHEN 2026-07-04) — vitals-style
dashboard framing:**

Treat the Corpus Health Score as a **vitals-style dashboard** (multi-
symptom coverage), NOT as pure independent-factor model. Correlation
between dimensions (e.g., embedding completeness ↔ latest-xx99-
embedded ↔ doc-change-to-embed latency) is acceptable — it's like
patient vitals where multiple correlated symptoms reinforce each
other. Composition:

- **Weighted composite 0-100** — good for trend tracking over time;
  weights declared explicitly + revisable; do NOT overfit early
- **Hard gates ("must-pass" — small set, prevent composite hiding
  critical failure)**:
  - **Gate 1:** Latest closed xx99 canonical summary IS embedded
  - **Gate 2:** Embedding completeness > floor (P4 observation
    calibrates the floor)
  - **Gate 3:** Doc-change-to-embed latency < bound (P4 calibrates)
- Any hard-gate failure → RED regardless of composite score
- Thresholds are **operationally-derived** ("what breaks?") not
  fixed doctrine — refine weights + gates after P4 observation
  evidence

**Not decided in this arc:** exact thresholds; whether to gate
Rigby SIGN cycles vs Chris-review-required; whether score is
computed daily / on-demand / arc-close-triggered; whether the score
itself gets embedded as an OpsRun-adjacent audit record.

### 5.6 xx99 — Canonical summary (S2199)

Standard playbook §11.3 12-section canonical-summary template
application (NINTH application after S1399, S1499, S1599, S1699, S1799,
S1899, S1999, and whichever S2099 lands as). Includes §10 meta-
methodology per feedback rule.

**Ships:**
- Arc-scope decision inventory
- Cross-cutting pattern extraction
- T-tier + R-tier follow-on queue
- Delegates-to routing (any findings not resolvable within the arc)
- §10 "What This Research Taught Us About How to Do Research" section
- RAG Corpus Health Score final proposal (composite of §5.5 dimensions
  + scoring model + tiers)

---

## 6. Parked candidate issues

Issues surfaced during scoping that are NOT in child slots. Preserved
for post-S2199 handoff routing:

### 6.1 Parked from S1273 §3.14 row itself

- **Embedding cadence UNKNOWN** admitted in inventory row — resolved in
  P2 as design work, not just inventory recheck
- Spider-data embedding backfill 15-min cadence — S2001 F3 already
  surfaced; P2 covers

### 6.2 Parked from Group 1300 boundary

- S1304 §17 duplicate-vs-complementary provenance systems — S1399
  reframed as "complementary, not duplicate"; consolidation decision
  ROUTED to post-S1399. Group 2100 P3 governance design may resolve
  as boundary owner assignment.
- MemorySystem T5 severity assessment blocked on IntelligentJobMatcher
  production invocation audit (S1305 §19 R6) — NOT in Group 2100 scope
  (Cat C AI/user memory territory, not institutional knowledge)

### 6.3 Parked as post-arc execution items

- **Actual cascade CI enforcement** — P3 designs it; implementation is
  post-arc execution item
- **Actual retrieval authority FRAMEWORK ranker implementation** (per
  W3 revision — framework not hierarchy) — P3 designs axes +
  conflict-resolution rules; implementation is post-arc
- **Option B — controlled experiment for "RAG freshness bounds SIGN
  quality" hypothesis (W1 revision T-slot)** — Group 2100 P4 delivers
  Option A structured observation instead. Option B requires: (a)
  isolated test corpus (staging pgvector OR in-memory HNSW), (b)
  defined SIGN-quality metrics (blinded scoring rubric), (c) stale vs
  fresh corpus conditions, (d) non-live Rigby routing, (e) N>=3 pairs
  to move beyond anecdote. Parked as **post-arc R-slot** — significant
  infrastructure investment before it can run. Estimated cost: 1-2
  full sessions to build harness + 1 session to run + 1 session to
  analyze. Group 2100 P4 output includes the harness *design spec*
  even though it doesn't build it.
- **Actual metadata backfill** for schema-present-but-empty fields
  (P1 identifies gaps; P3 defines required contract; backfill is
  post-arc)
- **Actual RAG Corpus Health Score implementation** (§5.5 designed
  in P1-P3; observed in P4; implementation of the composite scorer
  + daily / on-demand computation + dashboard surface is post-arc)
- **Actual `AIEmployee` boundary owner handle registration** (P3
  designs; adding the handle to `core/employees/jobs.py` +
  MissionRunner integration is post-arc)

### 6.4 Parked for Group 2000+ close reconciliation

Group 2000+ is in-flight at S2002 (Cat B) with S2003 (Cat C) and S2004
(Cat F CONSOLIDATION) plus S2099 xx99 remaining. Any findings from
S2003 / S2004 / S2099 that reach RAG substrate should be reviewed at
Group 2100 formal arc open and folded in.

Known so far: S2001 F3 (SPIDER_DATA) + F9 (dormant-consumer pattern).

### 6.5 Risks to Arc Success (W9 revision — new section)

Known risks that could degrade arc quality or force scope reduction
mid-arc. Preserved for pre-arc-open review by Chris + Rigby SIGN.

**R1 — No isolated RAG test harness.** Rigby's PROD pgvector is a
single shared corpus. Isolation pins isolate conversation state, not
RAG lookup. Cannot run controlled experiments without contaminating
live retrieval. Mitigation: P4 explicitly reframed as observation
(§5.4 W1 revision); Option B parked as post-arc T-slot (§6.3).
**Impact:** hypothesis testing is qualitative not quantitative;
"RAG freshness bounds SIGN quality" remains hypothesis-status after
arc closes.

**R2 — Live pgvector shared corpus makes any "does this work?"
verification hard.** Extension of R1 — even P1-P3 read-only ORM
probes need to distinguish "corpus IS X" from "corpus WAS X when
snapshot taken." Mitigation: P1 designs a "corpus-state snapshot"
metadata record so state audits are reproducible.

**R3 — Prior S1304 overlap may cause scope confusion.** Some P1/P2
findings may re-surface S1304 findings under new framing. Mitigation:
§2.3 explicit reframe as depth/lens (not different territory); §7.2
anti-scope "no Group 1300 re-audit"; P1-P3 audits must tag every
S1304 reference explicitly (`[REDEEPENED-FROM-S1304-G3]` style).

**R4 — Metadata fields may be aspirational, not schema-backed.**
Chris's 18-field metadata list is aspirational. Most fields likely
NOT in `DocumentEmbedding` schema today. P1's ROI-trim pass is
required to distinguish schema-present / derivable / absent.
**Impact:** P3 metadata contract may propose ~4-6 required fields,
not 18. Framing the 18 as "aspirational" up-front prevents scope
misalignment.

**R5 — Embedding / cascade costs may affect governance choices.**
At scale (verified by MEMORY.md rules referencing 1820 docs + 14k+
chunks), cascade-at-every-close has real ongoing OpenAI embedding
API cost. P3 governance design MUST include cost/benefit thresholds
and tiered rules (e.g., mandatory-embed for canonicals; advisory for
handoffs; batched for backfill). Not naming cost up-front risks
shipping a governance model no one can afford to enforce.

**R6 — Retrieval quality is hard to measure objectively.** RAG
Corpus Health Score (§5.5) is a proxy, not ground truth. P4
observation is qualitative. **Impact:** arc may ship framework +
proposals without settling *"how good is 'good enough'?"* — that
question requires Option B controlled experiment (parked) or
production A/B rollout (further post-arc).

**R7 — Supersession / authority conflicts may require policy
decisions, not just code audit.** Some conflicts don't have a clean
framework answer — e.g., a newer handoff that appears to contradict
an older canonical summary. Some need Chris D-verdict on precedence
per case. Mitigation: P3 framework must surface *conflict-classes
that require policy escalation* explicitly, not pretend all are
algorithmically resolvable.

**R8 — Group 2000+ concurrent work may create moving targets.**
S2003 / S2004 / S2099 may introduce RAG-adjacent findings that
require mid-arc re-scoping (e.g., if S2003 designs a cross-substrate
composition where RAG is a first-class participant, P3 governance
must respect that composition). Mitigation: §6.4 explicit parking
for Group 2000+ close reconciliation; arc-open verifier loop
re-check on ARCHITECTURE_INDEX Group 2000+ registration; scope
padding in P3 to absorb 1-2 unexpected findings.

**R9 — Rigby SIGN worker instability could jam mid-arc.** Per
`feedback_rigby_sign_worker_instability_recovery.md`, fresh Rigby
SIGN pins can jam after ~2 substantive turns on large-payload prompts.
Mitigation: batch SIGN findings 3-4 per prompt (per feedback rule);
recovery = retire jammed pin + mint fresh; two-pin ceiling before
falling back to parent-Claude verifier-loop as compensating quality
gate.

**R10 — Context degradation across 5-session arc** (Rigby SIGN cycle
1 Q10 STRENGTHEN 2026-07-04). Arc coherence risk if the parent
scoping doc evolves but the working set in-chat drifts.
**Mitigation:** pin the "current truth" pointers each session (doc
path + last-updated timestamp + 5-bullet delta log). Each child audit
opens by reading parent scoping doc + delta log; each child close
updates delta log with any parent-scope-relevant findings.

**R11 — D-verdict availability latency (Chris bandwidth)** (Q10
STRENGTHEN). Arc can stall if D-verdicts are required midstream and
Chris review is delayed. **Mitigation:** each D-verdict must be
labeled BLOCKING vs NON-BLOCKING; default proceed posture for
non-blocking is "proceed on STRENGTHEN until ratified" (arc continues
with tentative acceptance); BLOCKING D-verdicts pause the arc until
resolved.

**R12 — SIGN worker recovery protocol** (Q10 STRENGTHEN — extends
R9 with explicit protocol). Recovery sequence: (1) if a SIGN pin
jams after ~2 substantive turns, retire it via
`session_tool.retire`; (2) mint a fresh replacement via
`session_tool.create_fresh`; (3) ultra-short ping first + resume with
smaller batches (2-3 findings per prompt); (4) two-pin ceiling —
after 2 consecutive jams, fall back to parent-Claude verifier-loop
as compensating quality gate; (5) log the retirement + replacement
in the child audit's SIGN section.

**R13 — Parent scoping doc drift between arc-open and S2199** (Q10
STRENGTHEN). Risk that S2199 canonical summary cites obsolete
framing / taxonomy that has evolved mid-arc. **Mitigation:** treat
parent scoping as "living" but require a **frozen snapshot at S2199
time** — hash / revision marker recorded in S2199 §12 Appendix
Provenance; any mid-arc scoping edits logged in a delta log with
who / when / why.

---

## 7. Anti-scope

### 7.1 No implementation

Group 2100 is research + design authority ONLY. No pipeline changes,
no schema migrations, no cascade command changes, no retrieval ranker
changes ship in this arc. Implementation candidates emerge from arc as
post-arc execution items (§6.3).

Chris directive point 9: "Do not let 2100 become 'fix embed pipeline
immediately.' Parent scoping should produce: domain definition,
existing knowledge inventory, success criteria, child audit sequence,
load-bearing questions, non-goals, delegated scopes, follow-on
implementation candidates. No implementation unless Chris explicitly
ratifies after scoping."

### 7.2 No Group 1300 territory

Group 2100 does NOT re-audit `AgentMemory`, personal memories,
conversation context, memory persistence architecture, or the two-lane
retrieval semantics. Those are Group 1300 territory. If a finding
touches those, it flags for Group 1300 R-tier queue, not this arc.

### 7.3 No Group 2000+ territory

Group 2100 does NOT re-audit EventBus, HAI event contracts, or the
cross-plane composition designs. If a finding depends on Group 2000+
xx99 conclusions, it waits for S2099 to close and reconciles at formal
arc open.

### 7.4 No design-decision blur

Each child ships DESIGN + RESEARCH artifacts. It does not attempt
to build the design into runtime. This preserves the design-preparation
authority pattern established S1275 / Group 1900 §17.1.

### 7.5 No new domain expansion

Group 2100 does NOT expand into: Documentation / Research Knowledge
System (§3.15, separate future arc), API Layer (§3.22), Frontend UI
(§3.18). Boundary findings that touch those flag for their respective
future arcs.

---

## 8. Decisions recorded — Chris "agree all" ratification 2026-07-04 post-Rigby SIGN cycle 1 clean

**Formal Chris ratification at S2100 arc open 2026-07-04:** Chris
"agree all" on the 6-item D-verdict ratification card (D2100.1a + 1b +
2 + 8 + 9 RATIFY + D2100.10 DEFER per Claude-proposed dispositions
supported by Rigby SIGN Q1/Q2/Q4/Q7/Q9/Q12 verdicts). Prior directive-
ratified D-verdicts (D2100.5 + D2100.6 + D2100.7) retain their
ratification with Q3/Q12 fold refinements folded in. D2100.3 EXECUTED
(arc pin `pa-18b095bb7c4740be` minted). D2100.4 EXECUTED (SIGN cycle
1 clean).

**All 10 D-verdicts D2100.1a through D2100.10 are now RATIFIED or
EXECUTED as of 2026-07-04.**

### D2100.1a — Group 2100 SCOPE lock: RAG / Document Loading first-class domain arc (RATIFIED 2026-07-04 via Chris "agree all"; Q12 SPLIT 2026-07-04)

**Q12 fold (Rigby SIGN cycle 1 STRENGTHEN):** D2100.1 split into scope
lock (D2100.1a) and framing adoption (D2100.1b) to enable partial
ratification — Chris can agree on scope but adjust the "Knowledge
Loop" label independently.

Scope lock: Group 2100 owns institutional knowledge substrate —
ingestion cascade, corpus hygiene, retrieval authority framework,
governance, behavior-substrate observation. NOT AI/user memory
(Group 1300 territory). Depth/lens promotion of S1304 boundary-
integration audit into first-class DEEP-coverage architecture arc
per §1(2) + §2.3.

**BLOCKING** — arc cannot open on ambiguous scope.

### D2100.1b — Group 2100 FRAMING adoption: Reality→Research→Knowledge→Behavior model + Knowledge Loop lens (RATIFIED 2026-07-04 via Chris "agree all"; Q12 SPLIT 2026-07-04)

Framing adoption: arc adopts Reality → Research → Knowledge → Behavior
conceptual model + Knowledge Loop lens as arc-wide framing per §1
preamble, WITH Q1 fold canonical disclaimer (framing is conceptual,
NOT inherited doctrine from Groups 1700/1800).

**NON-BLOCKING** — if Chris ratifies scope (D2100.1a) but wants a
different framing label, arc proceeds under new label without
re-scoping child audits.

### D2100.2 — 4-child taxonomy per §3.4 (RATIFIED 2026-07-04 via Chris "agree all")

P1 Corpus State / P2 Ingestion Pipeline / P3 Retrieval Authority +
Governance Design / P4 Behavior Substrate + Integration + xx99.

Alternates: Option (a) 3-child (rejected: under-covers behavior
substrate hypothesis); Option (c) 5-child (rejected: P3/P4 close-
coupled, would consolidate mid-arc).

### D2100.3 — Mint fresh Group 2100 arc pin post-S2099 (EXECUTED 2026-07-04)

Per playbook §16 arc-standard behavior. **EXECUTED 2026-07-04**
at S2100 formal arc open — `session_tool.create_fresh` returned
`pa-18b095bb7c4740be` with title "Group 2100 — RAG / Document
Loading (Knowledge Loop)". Prior `pa-dd7e973617da464d` retired at
S2099 close (EIGHTH formal arc-pin retirement, retired=true,
updated_count=35). `tools/pa_local.sh:215` rotated to new pin +
header ledger updated with S2099 retirement + S2100 open
transition per S1900/S2000 documentation pattern.

### D2100.4 — Rigby SIGN cycle 1 on this parent scoping EXECUTED CLEAN with 9 STRENGTHEN folds (RATIFIED 2026-07-04 via successful SIGN cycle completion)

Per playbook §15 REQUIRED SIGN cycle. **EXECUTED 2026-07-04** on
Group 2100 arc pin `pa-18b095bb7c4740be`. Cycle 1 completed clean
across 4 batches (Q1-Q3 framing + Q4-Q6 taxonomy + Q7-Q9 frameworks/
governance + Q10-Q12 risks/health-score/D-verdicts) with 12 verdicts:
9 STRENGTHEN + 3 CLEAN + 0 FOLD + 0 REJECT. All 9 STRENGTHEN folds
landed pre-commit (Q1 loop-closure rubric + disclaimer / Q2 S1304
baseline clarifier / Q3 maturity-form central lens question + 5
acceptance criteria / Q4 P4 evidence-assembly cap + Option (b)
justification / Q5 belongs-to boundary rules / Q6 P4 N ≥ 10 cases
threshold / Q7 runtime-facts vs research-posture definitional split
+ precedence + tie-break / Q9 hybrid metadata contract / Q10 R10-R13
risks / Q11 vitals-dashboard framing + hard gates / Q12 D2100.1a/1b
split + D2100.7 conditional elevation + D2100.8/9/10 additions).
Cycle 2 NOT required.

**BLOCKING** — arc could not open without SIGN cycle 1 clean.
**Executed and clean.**

### D2100.5 — Design-preparation authority only (RATIFIED via Chris directive point 9)

Group 2100 is research + design authority. No implementation ships in
this arc. Post-arc execution items enumerated in §6.3.

### D2100.6 — Central lens question locked (RATIFIED via Chris directive point 10)

Arc answers: *"Is Rigby's RAG corpus a passive document search index,
or is it a governed institutional knowledge layer that can reliably
shape future research, SIGN cycles, and platform decisions?"* P4
integration report explicitly answers this.

### D2100.7 — "RAG freshness bounds SIGN quality" is a hypothesis, TESTED via structured observation (Option A) in P4; CONDITIONAL ELEVATION rule (RATIFIED via Chris directive point 5 + W1 revision 2026-07-04 + Q12 SIGN STRENGTHEN 2026-07-04)

**REVISED per W1 critique 2026-07-04 + Q12 SIGN fold 2026-07-04.**
Original framing implied "controlled experiment" — reframed as
structured observation. Group 2100 P4 delivers **Option A**:
retrospective review of recent Rigby SIGN cycles with documented
RAG-quality incidents, classified qualitatively.

**Conditional elevation rule (Q12 fold):** Hypothesis status after
arc close is CONDITIONAL on P4 evidence quality:
- **IF P4 finds repeated, attributable patterns** where freshness
  bounds correlate with retrieval / decision failures **AND** the
  framework provides enforceable remediation hooks → elevate from
  **hypothesis → provisional contract** (still revisable, but
  actionable governance foundation)
- **IF P4 evidence is weak** (no repeated patterns, weak attribution,
  or no clear remediation hooks) → keep as **hypothesis**

**Option B (controlled experiment)** parked at §6.3 as post-arc T-slot.
Requires: isolated test corpus, defined metrics, N>=3 pairs, non-live
Rigby routing, ~4 sessions of infrastructure investment. Group 2100
P4 output includes the *harness design spec* even though the arc does
not build it.

**Outcome branches:**
- If observation → provisional contract elevation → §5.5 Corpus
  Health Score gates become urgent post-arc execution items;
  Option B experiment justified for future.
- If observation → hypothesis-retention → Group 2100 still ships
  framework + governance + hierarchy, but the arc-ranking against
  other Group 2100+ candidates may re-rank; Option B experiment may
  be permanently deferred.

### D2100.8 — Adoption of the 8-axis retrieval authority framework as platform default retrieval-trust rubric (NEW; RATIFIED 2026-07-04 via Chris "agree all"; Q12 SIGN STRENGTHEN 2026-07-04)

**Q12 fold:** Adopt the P3 8-axis retrieval authority framework
(primary vs synthesized / runtime vs research / specificity / recency /
supersession / canonical status / lifecycle status + conflict-
resolution rule with runtime-facts vs research-posture split) as the
platform's default retrieval-trust rubric, even if enforcement lands
post-arc as execution item.

**BLOCKING for P3 close** — P3 cannot ship its framework without
adoption D-verdict.

### D2100.9 — Metadata contract shape: hybrid core-required + doc-type profile (NEW; RATIFIED 2026-07-04 via Chris "agree all"; Q12 SIGN STRENGTHEN 2026-07-04)

**Q12 fold:** Adopt hybrid metadata contract shape per Q9 STRENGTHEN:
(1) core required set (global, fatal-if-missing for P1/P3 reasoning) +
(2) doc-type profile (recommended + optional per doc class). Prevents
frontmatter churn while ensuring class-appropriate discipline.

**BLOCKING for P1 close** — P1 cannot converge without contract
shape D-verdict.

### D2100.10 — RAG Corpus Health Score as standing governance metric (NEW; DEFERRED to P4 close per Chris "agree all" 2026-07-04; revisit at S2199; Q12 SIGN OPTIONAL STRENGTHEN 2026-07-04)

**Q12 fold (optional per Rigby SIGN):** Decide whether the RAG Corpus
Health Score (§5.5) becomes a **standing governance metric** with
dashboard + cadence, or remains a Group 2100 arc artifact only. If
standing metric: computed on-demand / daily / arc-close-triggered;
surfaced in Rigby SIGN cycle preambles; possibly embedded as
OpsRun-adjacent audit record.

**NON-BLOCKING** — arc can close on either disposition; deferral
just parks Health Score as static arc output.

### Operational defaults / inherited constraints (not new Chris D-verdicts)

- Playbook §11.1 parent-scoping template EIGHTH application
- Playbook §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED discipline
- Playbook §11.3 §10 "What This Research Taught Us" meta-methodology
  section on xx99 (adopted S1399, seven consecutive applications)
- Playbook §16 arc-pin arc-standard behavior on formal arc open

---

## 9. Next step

### 9.1 Immediate (this draft)

- ✅ Draft parent scoping doc at `docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md`
- ✅ Update memory file `project_2100_plus_queue_ranking.md` with framing additions (already tracks the 6-arc queue)
- ✅ Do NOT commit (parallel-safety)
- ✅ Do NOT touch shared state files (parallel-safety)
- ✅ Do NOT route to Rigby SIGN (parallel-safety)

### 9.2 Waiting on

- **S2002 Cat B HAI Event Contract Design** close (parallel Claude Code
  session in-flight)
- **S2003 Cat C Cross-Substrate Composition Design** open + close
- **S2004 Cat F Adjacent / Separation Boundaries CONSOLIDATION** open + close
- **S2099 Group 2000+ canonical summary** — retires arc pin
  `pa-dd7e973617da464d`, releases Rigby SIGN pin surface

### 9.3 Formal arc-open sequence (post-S2099)

Once S2099 lands and Group 2000+ arc pin is retired:

1. Update `docs/research/OPEN_ARCS.md` — move Group 2100 row from
   §22 not-started to In-progress table
2. Update `docs/research/ARCHITECTURE_INDEX.md` — add §1.NN Group 2100
   registration + version bump
3. Overwrite `00-START-NEXT-SESSION.md` — point at S2100 open
4. Mint Group 2100 arc pin via `session_tool.create_fresh` (playbook
   §16)
5. Route Rigby SIGN cycle on this parent scoping doc (playbook §15
   REQUIRED)
6. Present D-verdicts §8 to Chris for ratification
7. Fold Rigby SIGN adjustments pre-commit
8. Flip this doc's `status: draft` → `status: active`
9. Commit + run full 4-step docs cascade + `build_docs_provenance`
   per `feedback_docs_cascade_at_every_close`

### 9.4 Arc completion path (aspirational)

If 4-child + xx99 arc completes at Group 2000+ tempo:
- S2100 parent scoping (this doc, ratified) → 2026-07-DD
- S2101 P1 Corpus State → 2026-07-DD
- S2102 P2 Ingestion Pipeline → 2026-07-DD
- S2103 P3 Retrieval Authority + Governance → 2026-07-DD
- S2104 P4 Behavior Substrate + Integration → 2026-07-DD
- S2199 xx99 Canonical Summary → 2026-07-DD

Dates deferred until formal open.

---

## Appendix — Frontmatter provenance

### A.1 Playbook §11.1 template EIGHTH application

After: S1300 first (Group 1300 Memory parent) + S1400 second (Group 1400
Revenue) + S1500 third (Group 1500 Sports/DBAO) + S1600 fourth (Group
1600 Content) + S1700 fifth (Group 1700 Observability) + S1800 sixth
(Group 1800 HumanAttention) + S1900 seventh (Group 1900 Authority
Enforcement) + S2000 eighth (Group 2000+ Event / Integration
Architecture).

Group 2100 = ninth formal arc, eighth application of §11.1 parent-
scoping template.

### A.2 Companion doc lineage

**Load-bearing prior work:**
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — process contract
- `docs/research/platform_architecture_inventory.md` §3.14 — RAG /
  Document Loading row
- `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md`
  — S1304 docs↔RAG boundary audit (Group 1300)
- `docs/research/domains/memory/1399_memory_canonical_summary.md`
  §19 — Group 1300 close-out delegations
- MEMORY.md workflow rules:
  - `feedback_docs_pipeline_4_step_cascade.md`
  - `feedback_docs_cascade_at_every_close.md`
  - `feedback_cascade_pr_must_include_embed_step.md`

**In-flight prior work (may add inheritance before formal arc open):**
- Group 2000+ arc (S2000 parent + S2001 P1 shipped, S2002-S2099
  remaining)

### A.3 Verifier loop notes

**Verifier-loop applied pre-draft (playbook §14 REQUIRED):**

- `docs/research/platform_architecture_inventory.md` §3.14 — read
  in-repo (verified 2026-07-04 lines 1199-1248 of `/Users/donkeyking/
  development/unified-donkey-betz/docs/research/platform_architecture_
  inventory.md`)
- `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md`
  — read in-repo (verified 2026-07-04 boundary audit lens finding
  set including G1 cascade discipline informal + G3 lru_cache
  staleness + G5 boundary unowned + T1/T2/T3 debt items)
- `docs/research/domains/memory/1399_memory_canonical_summary.md`
  — read in-repo (verified S1399 §19 R5 turn-context → RAG
  enrichment delegated to post-S1399)
- `docs/research/domains/event_integration_architecture/2000_event_
  integration_architecture_domain_scoping.md` — read in-repo
  (verified Group 2000+ parent template structure for §11.1
  playbook application)
- MEMORY.md workflow rules on docs cascade — read in-repo (verified
  4-step cascade rule + cascade-at-every-close rule + cascade-PR-
  must-include-embed rule)

**Verifier-loop NOT applied in this draft (deferred to formal arc open):**

- Rigby SIGN cycle on parent scoping (deferred — active Group 2000+
  arc pin has SIGN pin surface)
- Live database inspection of `Document` + `DocumentEmbedding` row
  counts + freshness distribution (deferred — would burn tokens
  before formal arc opens; will run at S2101 P1 as verifier baseline)
- Live corpus size + chunk count + embedded-vs-unembedded gap
  measurement (deferred to S2101 P1)

### A.4 Rigby SIGN routing

**EXECUTED at S2100 formal arc open 2026-07-04 on Group 2100 arc pin `pa-18b095bb7c4740be`.**

Cycle 1 completed across 4 batches (12 questions, 9 STRENGTHEN + 3
CLEAN + 0 FOLD + 0 REJECT). All 9 STRENGTHEN folds landed pre-commit:

| Batch | Questions | Verdicts | Folds landed |
|-------|-----------|----------|--------------|
| 1 (framing) | Q1 Knowledge Loop coherence + Q2 depth/lens with Group 1300 + Q3 central lens question | STRENGTHEN + CLEAN + STRENGTHEN | Q1 rubric + disclaimer; Q2 S1304-baseline clarifier; Q3 maturity-form central lens + 5 acceptance criteria |
| 2 (taxonomy) | Q4 Option (b) fit + Q5 P1-P4 distinctness + Q6 P4 observation reframe | STRENGTHEN + STRENGTHEN + CLEAN | Q4 P4 evidence-assembly cap + Option (b) retention justification; Q5 belongs-to boundary rules; Q6 P4 N ≥ 10 threshold |
| 3 (frameworks/governance) | Q7 8-axis framework + Q8 governance disambiguation + Q9 metadata ROI-trim | STRENGTHEN + CLEAN + STRENGTHEN | Q7 runtime-facts vs research-posture split + precedence + tie-break; Q9 hybrid metadata contract |
| 4 (risks/health/D-verdicts) | Q10 risk register + Q11 Health Score + Q12 D-verdicts | STRENGTHEN + STRENGTHEN + STRENGTHEN | Q10 R10-R13 additions; Q11 vitals-dashboard + hard gates; Q12 D2100.1a/1b split + D2100.7 conditional elevation + D2100.8/9/10 additions |

Cycle 2 NOT required. All folds landed pre-commit — D2100.4 RATIFIED
via successful SIGN cycle completion.

### A.5 Parallel-safe execution notes (this draft)

**Session context.** Drafted 2026-07-04 by Claude Code while a parallel
Claude Code session was executing S2002 (Group 2000+ P2 Cat B HAI Event
Contract Design child audit). Working tree shared. Constraints:
- No shared-state file writes (`OPEN_ARCS.md`, `ARCHITECTURE_INDEX.md`,
  `00-START-NEXT-SESSION.md`, `tools/pa_local.sh`)
- No git operations (`commit`, `push`, `checkout`, branch changes)
- No `manage.py` commands (would trigger DB writes and observability
  events)
- No Rigby SIGN routing (arc pin belongs to S2002)
- Only writes to fresh directory `docs/research/domains/rag_document_
  loading/` (no path collision with any S2002 work)

**Interference audit.** Confirmed at draft time:
- S2002 in-flight file: `docs/research/domains/event_integration_
  architecture/2002_event_integration_architecture_cat_b_hai_event_
  contract_design_child_audit.md` (untracked, S2002-owned)
- This draft path: `docs/research/domains/rag_document_loading/2100_
  rag_document_loading_domain_scoping.md` (untracked, disjoint
  directory)
- No overlap.

**Chris directive framing captured (updated 2026-07-04 post-W1-W3-W7-W9-W11 revision).** All 10 additions folded into scoping with W7 redistribution across children:

| # | Chris addition | Landing point (revised) |
|---|----------------|-------------------------|
| 1 | Knowledge Loop framing | §1 preamble (marked *conceptual, NOT inherited canonical doctrine* per W11) + §5.4 P4 lens |
| 2 | Distinction from Group 1300 | §1 (2) reframed as depth/lens per W2 + §2.3 opening reframe + §7.2 anti-scope |
| 3 | Reality→Research→Knowledge→Behavior model | §1 preamble + §5 child scopes reference model transitions |
| 4 | Research-governance questions (9 items) | **REDISTRIBUTED per W7:** Q1/Q4/Q8-a → P1; Q3 + cascade mechanism + refresh triggers + hashing substrate → P2; Q5/Q6/Q7/Q8-b + governance term disambiguation (5 axes) → P3; Q9 + SIGN quality gates → P4 |
| 5 | RAG freshness bounds SIGN quality hypothesis | §1 preamble + §5.4 P4 **REFRAMED per W1** as structured observation (Option A); Option B parked §6.3; D2100.7 revised |
| 6 | Metadata inventory (18 fields) | §5.1 P1 with ROI-trim pass (~4-6 required + ~4-8 derivable + ~4-6 aspirational, not flat 18-field mandate — per R4 risk) |
| 7 | Retrieval authority | **REFRAMED per W3** as retrieval authority FRAMEWORK (8 axes + conflict-resolution rules) in §5.3 P3, NOT a hard-coded ranking |
| 8 | Research-debt → knowledge-debt framing | §5.1 P1 + §5.3 P3 references |
| 9 | Governance before implementation | §7.1 anti-scope + D2100.5 ratified |
| 10 | Central lens question | §1 preamble + §5.4 P4 answers + D2100.6 ratified |

**W-fixes applied 2026-07-04 (per Chris directive post-critique):**

| W# | Fix | Landing |
|----|-----|---------|
| W1 | P4 reframed observation not experiment | §5.4 full rewrite + §6.3 Option B parked + D2100.7 revised |
| W2 | Group 1300 boundary depth/lens | §1(2) reframe + §2.3 opening reframe + positional statement |
| W3 | Retrieval authority framework not ranking | §5.3 full rewrite (axes + conflict-resolution + governance disambiguation) |
| W7 | 9 governance questions redistributed | §5.1 P1 (Q1/Q4/Q8-a) + §5.2 P2 (Q3 + cascade/refresh/hashing) + §5.3 P3 (Q5/Q6/Q7/Q8-b) + §5.4 P4 (Q9) |
| W9 | Risks to Arc Success added | New §6.5 with R1-R9 |
| W11 | Loop-triad verified conceptual not doctrine | §1 preamble caveat with verification note (S1799 zero mentions; S1899 one finding-level use) |

**Claude-originated addition (per W13 critique):**

- **§5.5 RAG Corpus Health Score** — composite score design across
  8 dimensions (embedding completeness / stale chunk / canonical-summary
  coverage / superseded-doc demotion / missing-metadata / latest-xx99
  embedded / retrieval authority conflicts / doc-change-to-embed latency)
  with tier proposal (GREEN 95-100 / YELLOW 80-94 / RED <80). Gives
  Group 2100 a measurable arc output without shipping implementation.

**Weaknesses acknowledged but NOT fixed in this revision** (retained
for arc-open handling):

- W4 — Metadata schema verification against runtime `DocumentEmbedding`
  deferred to P1 formal execution
- W5 — Governance term disambiguation (5 meanings) captured in P3
  scope but full separation happens IN the child audit
- W6 — Verifier-loop upgrade (grep code for `lru_cache(1)`, check
  employee handles, check beat schedule) deferred to formal arc-open
  verifier-loop pass
- W8 — Alternate child sequence (P4-lite early) not adopted; noted as
  optional re-sequencing at arc open if hypothesis-status becomes
  urgent
- W10 — Cost economics not fully worked; R5 risk names the issue
- W12 — Template application count "8th" still cited against
  OPEN_ARCS queue not against actual parent-scoping docs; deferred
- W14 — "Arc pin collision" language softened; real reason is
  playbook §16 arc-open discipline not physical collision
- W15 — Implementation-ready-vs-preparation distinction deferred to
  arc-open D-verdict

---

*End of parent scoping draft (post-W1/W2/W3/W7/W9/W11 revision +
Claude-originated §5.5 addition). Awaits formal arc open post-S2099
for ratification.*

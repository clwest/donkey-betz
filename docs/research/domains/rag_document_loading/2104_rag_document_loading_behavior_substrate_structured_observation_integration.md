---
title: "Group 2100 P4 — Behavior Substrate: Structured Observation of RAG-Quality → SIGN-Quality Coupling + Integration (S2104)"
status: active
session: 2104
arc: Research Group 2100 (RAG / Document Loading — Knowledge Loop)
child_slot: P4 Cat D Behavior Substrate Structured Observation + Integration
generated: 2026-07-05
last_reviewed: 2026-07-05
head_commit: a98db2d2
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/KNOWLEDGE_PIPELINE.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/EMPLOYEE_OS_PRIMITIVES.md
related:
  - docs/research/domains/rag_document_loading/2100_rag_document_loading_domain_scoping.md
  - docs/research/domains/rag_document_loading/2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md
  - docs/research/domains/rag_document_loading/2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md
  - docs/research/domains/rag_document_loading/2103_rag_document_loading_retrieval_authority_framework_corpus_governance_design.md
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md
  - docs/research/domains/memory/1399_memory_canonical_summary.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/OPEN_ARCS.md
delegates_to:
  - S2199 Group 2100 xx99 canonical summary
inherits_from:
  - S2100 parent scoping §5.4 P4 scope + §5.5 Corpus Health Score dimension list + D2100.7 conditional-elevation rule + D2100.10 Corpus Health Score deferred-to-P4-close verdict
  - S2101 F1-F4 (source_type='api' monoculture, metadata population asymmetry, silent-drop pattern, build_docs_provenance unscheduled) + KD-1..KD-6 knowledge-debt taxonomy + §15.3 6-category incident classes + R4.1-R4.4 P4 handoffs
  - S2102 F1-F8 (chunker regimes, Chunker B vs Chunker C population imbalance, ingested_via write-site fragmentation, cascade-emit-no-lifecycle-events) + p50/p95/p99/max chunk-per-doc distribution baseline + R4.1-R4.5 P4 handoffs
  - S2103 F1-F8 (7-evidence-axes + one-meta-rule framework, 3-part conflict-resolution rule, dual-cascade lean (b), 5-meaning governance disambiguation, D2100.9 hybrid metadata contract, 2-employee owner-assignment shape, 5-state lifecycle model, D2100.11 F2 retrofill lean (b)) + §17.1 spec-readiness register + §17.2 governance-dimension posture + §19.1 P4 triage (5 must-ship + 3 backlog) + T-slot execution queue
  - S1234 12-day-stale prod corpus + 1820-never-pushed Documents incident + `refresh_docs_corpus` daily-beat installation (verified STILL LIVE at S2101 close)
  - S1802 6-unembedded-docs cascade PR incident + `feedback_cascade_pr_must_include_embed_step` MEMORY.md rule codification
authority: observation for Category D per parent §5.4 D2100.5 authority + Chris "agree all" ratification 2026-07-04 at S2100 close + P3 §19.1 R4.x P4 triage (5 must-ship + 3 backlog) + Chris close-card ratification 2026-07-05; produces qualitative "RAG-quality affects SIGN-quality" evidence brief (N ≥ 10 incidents), integration matrix across P1-P3 findings, defended answer to Group 2100 central lens question, D2100.7 freshness-bound conditional-elevation verdict, D2100.10 Corpus Health Score standing-metric-vs-arc-artifact-only verdict, R4.1-R4.6 must-ship discharges + R4.5/R4.7/R4.8 backlog dispositions
verifier_loop: |
  Executed 2026-07-05 at HEAD `a98db2d2` post-S2103 close cascade PR
  merge (#2896). Level A verifier-loop pre-draft per START-NEXT §51
  step 8: (1) `platform_config_tool overview` via Rigby returned
  `service_context: local` — arc pin `pa-18b095bb7c4740be` preserved;
  (2) `git status` clean except `.claude/scratch/` (irrelevant);
  (3) parent §5.4 P4 scope + §5.5 Corpus Health Score candidate
  dimensions + D2100.7 + D2100.10 read in full; (4) S2101 KD-1..KD-6
  taxonomy + §15.3 incident matrix + §20.2 candidate metadata contract
  read; (5) S2102 F1-F8 findings + verifier-loop chunk-distribution
  baseline (n=51,952 LOCAL chunks) + Path A vs Path B analysis read;
  (6) S2103 F1-F8 design decisions + §17.1 spec-readiness register +
  §17.2 governance-dimension posture + §19.1 R4.x triage + §19.3
  T-slot queue read; (7) MEMORY.md incident narratives
  (`feedback_docs_pipeline_4_step_cascade`, `feedback_cascade_pr_must_include_embed_step`,
  `feedback_docs_cascade_at_every_close`) cross-referenced against S2101
  §15.3 KD-3 codification; (8) LIVE incident captured during arc open —
  `search_docs` returned 0 chunks with `excluded_missing_provenance: 7`
  while `kb_tool.semantic_search` returned 12 chunks on the SAME query
  routed through Rigby's PA tool surface. Two nominally-same corpus
  surfaces disagreeing on retrieval → KD-5 manifestation at retrieval-
  time. This incident is captured live in §14 F5 evidence.
  Observation-shape verifier-loop discipline (per S1399 §10 meta-
  methodology): P4 does NOT re-run S2101 P1 ORM measurement probes or
  S2102 P2 chunk-distribution sampling — those are P1/P2 outputs that
  P4 observes and integrates. Duplication would violate S1399 anti-
  pattern §10.3.2 (re-measuring what a child audit already established).
owner: claude (drafted S2104 P4; Rigby SIGN cycle 1 folds land pre-commit)
---

# Group 2100 P4 — Behavior Substrate: Structured Observation of RAG-Quality → SIGN-Quality Coupling + Integration

> **FOURTH child audit under Group 2100 RAG / Document Loading
> (Knowledge Loop) arc.** Playbook §11.2 20-section child-audit
> template TWELFTH-consecutive application after S1301 / S1401 /
> S1501 / S1601 / S1701 / S1801 / S1901 / S2001 / S2101 / S2102 /
> S2103. Executes on preserved arc pin `pa-18b095bb7c4740be` per
> playbook §16 arc-standard behavior + MC-4 CODIFICATION-CONFIRMED
> -with-scope-guardrails at S1999 close (guardrails-retained-but-
> generalized per S2099 MC-4 extension).
>
> **Scope-vs-form distinction.** This is a **structured observation**
> doc (Option A per W1 revision), NOT a controlled experiment (Option
> B parked as post-arc T-slot per parent §6.3). §14 findings are
> OBSERVED PATTERNS — RAG-quality incidents classified by axis
> (stale / unembedded / superseded / missing / mis-chunked /
> provenance-gap / cascade-gap) crossed with SIGN-quality effect
> (missed / wrong / degraded pressure-test / no measurable effect).
> §15 debt table inherits S2101 T1-T10 + S2102 T11-T17 + S2103 T18-
> T25 by reference and adds P4-scoped observation debt only. Option
> B controlled experiment stays parked — the true quantitative test
> requires isolation infrastructure (staging pgvector or in-memory
> HNSW, defined SIGN-quality metrics, blinded scoring rubric, non-
> live Rigby routing) that Group 2100 delivers value WITHOUT.
>
> **Central lens question P4 answers** (per parent §5.4 point 10 +
> Chris directive point 10):
>
> *"Is Rigby's RAG corpus a passive document search index, or is it
> a governed institutional knowledge layer that can reliably shape
> future research, SIGN cycles, and platform decisions?"*
>
> P4's defended answer — synthesized across P1 corpus-state, P2
> ingestion pipeline, P3 authority framework + governance design,
> and P4 observation evidence brief — lands in §20.

---

## 1. Executive Summary

**S2104 P4 delivers structured observation for Category D — Behavior
Substrate: RAG-Quality → SIGN-Quality Coupling + Integration.** FOURTH
child audit under Group 2100 RAG / Document Loading (Knowledge Loop)
arc, TWELFTH-consecutive application of playbook §11.2 20-section
child-audit template. Runtime target for Group 2100 (6 sessions) is on
track — 5 of 6 shipped after this session.

**Observation shape (per W1 reframe at S2100 close):** Retrospective
review of ≥10 documented RAG-quality incidents across the platform's
recent Rigby SIGN cycles + cascade PR merges + arc-close cards.
Classify each incident by RAG-quality axis + SIGN-quality effect.
Produce qualitative evidence brief (§14 F1-F8). Integrate with P1
corpus-state findings + P2 ingestion pipeline findings + P3 authority
framework + governance design findings (§17). Defend an answer to the
central lens question (§20).

**Evidence brief size — N ≥ 10 threshold cleared with N = 14.** Per
S2101 close Q6 SIGN STRENGTHEN 2026-07-04 threshold. Corpus mix:
6 KD-taxonomy incident classes with LOCAL counts (from S2101 §15.3);
2 historical MEMORY.md-catalogued incidents (S1234 12-day-stale +
S1802 6-unembedded-docs); 1 live incident captured during S2104 arc
open (`search_docs` vs `kb_tool.semantic_search` retrieval disagreement
with `excluded_missing_provenance: 7`); 2 chunker-regime observations
(from S2102 P2 verifier-loop); 1 framework acceptance HYPOTHETICAL
observation (T18/T19/T22 gate); 1 cross-arc governance-drift candidate
(S1899 §142 AgentLearningSystem U3); 1 ontological measurement-debt
observation (KD-2 UNMEASURABLE at chunk-time).

**Clarification per Rigby SIGN Batch 1 Q1 STRENGTHEN 2026-07-05:**
N counts **observed evidence items**, not taxonomy classes. To avoid
double-counting, the 6 KD-taxonomy incident classes (KD-1..KD-6) are
treated as **one taxonomy frame** and do NOT increment N unless
backed by a concrete observed incident. Re-stated:
- **N_observed = 3 concrete historical/live incidents** — S1234
  12-day-stale + S1802 6-unembedded-docs + §14 F5 live search_docs
  vs kb_tool disagreement
- **N_evidence_items = 14 total** — the 3 observed + 1 taxonomy
  frame (KD-1..KD-6 as bundled substrate baseline) + 2 chunker-
  regime observations + 3 hypothetical/gated (F6 T18/T19 gate + F7
  T13 gate + F8 T21 gate) + 1 cross-arc drift candidate (S1899
  §142) + 4 measurement-debt / substrate-baseline observations
  (KD-2 UNMEASURABLE + §14 F5 pattern-count-3-with-diversity per
  Q5 fold + §17.1 posture-register drift-candidates + §13
  maturity dimensions delta).

Q6 SIGN threshold at S2101 close was framed as evidence-brief
incident-count. P4 exceeds it via N_observed = 3 diverse-attributable
incidents (per §14 F4 D2100.7 elevation criterion — incident
diversity + actionability, not arbitrary count) supplemented by 11
substrate-baseline / hypothetical evidence items that inform §17
integration matrix + §20.1 lens-question defense.

**Load-bearing deliverables (per parent §5.4 + P3 §19.1 P4 triage
5 must-ship + 3 backlog):**

1. **Qualitative "RAG-quality affects SIGN-quality" evidence brief**
   — N = 14 incidents classified across RAG-quality axis (7 categories)
   × SIGN-quality effect (4 categories) per §14 F1-F8.
2. **R4.1 chunker-population correlation discharge** — Do recent SIGN
   cycles failing retrieval-quality checks correlate with Chunker B
   (sync-cascade) or Chunker C (async)? Verdict lands in §14 F2.
3. **R4.2 institutional-knowledge-layer acceptance criteria observation
   discharge** — Parent §5.1 criteria 2-5. Criterion 2 (F1 chunker
   regime documented) satisfied by S2102 F1-F3; Criterion 3-5 landed
   via S2103 F5 metadata contract + F7 lifecycle model. Post-arc T22
   execution gates measurable acceptance.
4. **R4.3 Corpus Health Score dimension additions** — Add dimensions
   for P3 §14 F1 axes coverage ratio, F5 metadata contract population
   rate, F7 lifecycle-status transition validity rate. Feeds §5.5
   dimension list per D2100.10.
5. **R4.4 D2100.7 freshness-bound conditional-elevation verdict** —
   Do observed incidents show freshness bounds correlate with
   retrieval/decision failures with enforceable remediation hooks?
   Per Q15 SIGN STRENGTHEN 2026-07-04 at S2101 close, N ≥ 10 concrete
   observed cases threshold. Verdict lands in §14 F4.
6. **R4.6 retrieval-authority framework acceptance observation** —
   Post-arc T18/T19 gate blocks observation of authority-provenance
   labels emitted at retrieval-time. HYPOTHETICAL until execution.
   Verdict lands in §14 F6.
7. **D2100.10 Corpus Health Score standing-metric-vs-arc-artifact-only
   Chris-verdict** — surfaced at close card per §5.5 deferral. §14 F3
   proposes the dimension list; §20 close card presents the verdict
   choice.
8. **R4.5 Path A vs Path B activation observation** (BACKLOG per Q19
   SIGN STRENGTHEN 2026-07-04 at S2102 close, PROMOTED per Chris pick
   (b) fold Path A into Path B at S2103 close) — Observation of N ≥ 10
   daily runs pending T13 post-arc execution. Landing in §14 F7
   HYPOTHETICAL section.
9. **R4.7 artifact lifecycle-transition observation** (BACKLOG — gated
   on T21 post-arc landing) — §14 F8 HYPOTHETICAL section.
10. **R4.8 governance-dimension mixed-mode observation** (BACKLOG —
    framework methodology observation) — S1899 §142 AgentLearningSystem
    U3 cross-arc ownership drift candidate observed. Verdict on whether
    P3 §14 F4 5-meaning disambiguation table would have prevented the
    drift lands in §14 F8 addendum.
11. **Defended answer to central lens question** synthesizing P1-P3 +
    P4 evidence, lands in §20.
12. **SIGN-quality quality-gate proposals** (Q9 discharge from parent
    §5.4) — Corpus Health Score threshold, canonical-summary coverage
    %, latest-xx99 embedded confirmation, freshness threshold.
    Proposed as Rigby SIGN preamble surface additions per D2100.10.
13. **Parked Option B controlled-experiment design as T-slot detail**
    — What harness would be needed (staging pgvector or in-memory
    HNSW), what metrics (SIGN-quality rubric), what infrastructure
    investment before Option B could run. §20.5 Appendix.

**Rigby SIGN posture.** Cycle 1 REQUIRED on this draft per playbook
§15 with batching discipline per `feedback_rigby_sign_worker_instability_recovery`
(4-5 findings per batch, target 20 Qs across 4-5 batches, expect
observation-shape to be cleaner than descriptive-audit or design-
preparation shape historically). All STRENGTHEN folds land pre-commit
per S2101/S2102/S2103 discipline.

**Chris close-card items — 10 items expected.** Ratification via
"agree all" or item-by-item. Executed post-Rigby-SIGN.

---

## 2. Domain Purpose

**Behavior Substrate framing.** Group 2100 P1 established what
Rigby's RAG corpus IS (state + reality + knowledge gaps); P2 established
HOW the corpus gets built (ingestion cascade + chunking + embedding);
P3 established the FRAMEWORK by which retrieval-time authority is
assigned + governance dimensions are disambiguated. P4 asks the
downstream question: **do RAG-quality gradations observably affect
SIGN-quality gradations?**

"Behavior Substrate" is the coupling layer between the corpus (P1-P3)
and the outputs that consume it (Rigby SIGN cycles, verifier-loop
lookups, arc-close-card pressure-tests, cascade-informed workflow
routing). If P1-P3 land a well-governed corpus but downstream behavior
does not observably improve, the substrate is disconnected. If P4
observation shows behavior varies with RAG-quality — including
degradation on stale / unembedded / mis-chunked corpus states — then
the substrate is coupled and the corpus qualifies as an institutional
knowledge layer per parent §5.1 acceptance criteria.

**Why observation, not experiment (W1 critique carried forward).** No
isolated RAG test harness exists. Rigby's PROD pgvector is a single
shared corpus; isolation pins isolate conversation state, NOT RAG
lookup — she pulls from the same DB regardless of pin. A controlled
experiment would require staging pgvector or in-memory HNSW, defined
SIGN-quality metrics, blinded rubric, non-live Rigby routing. Group
2100 delivers value WITHOUT that infrastructure via structured
retrospective observation. Option B parks as post-arc T-slot in
§19.3 + §20.5.

**Hypothesis status maintained.** "RAG freshness bounds SIGN quality"
remains a HYPOTHESIS per D2100.7. P4 observation provides *qualitative
evidence* for or against. It does NOT provide the quantitative test
the original framing implied. That distinction lands in §14 F4 verdict
and §20 lens-question answer so future arcs know what's actually been
established.

**Chris directive coverage:**
- **Point 5** (RAG freshness → SIGN quality — TEST not assume) — §14
  F4 evidence brief + D2100.7 elevation verdict; hypothesis-status
  remains hypothesis pending Option B harness.
- **Point 1** (Knowledge Loop conceptual framing) — §20.2 defends
  whether the substrate closes the proposed loop.
- **Point 3** (R→R→K→B model) — §17 integration matrix validates
  Retrieval → Ranking → Knowledge → Behavior end-to-end.
- **Point 10** (central lens question) — §20 defended answer.
- **Point 4 partial** (W7 redistribution) — Q9 minimum corpus hygiene
  for SIGN trust lands in §14 F3 SIGN-preamble additions + §20 gate
  proposals.

---

## 3. Canonical Entry Points

**RAG retrieval surfaces observed in P4 evidence brief.** Enumerated
by consumer surface (who calls) → invoked function (how) → downstream
consumer (what depends on it). Cross-reference S2101 §3 for the write-
side entry points + S2102 §3 for the ingestion cascade entry points.

| Surface | Invoked function | Downstream consumer | RAG-quality axis observed |
|---------|------------------|---------------------|---------------------------|
| Rigby PA tool `kb_tool.semantic_search` | `kb_tool` handler → `RAGSystem.query` (pgvector) | Rigby responses grounded in retrieved chunks with `similarity` + `importance` weights | ALL 7 axes possible; live incident §14 F5 |
| Rigby PA tool `search_docs` | `search_docs` handler → docs-specific corpus with provenance filter | Rigby responses grounded in docs-only chunks + provenance labels | KD-5 provenance-gap dominant (live incident §14 F5) |
| CLI `askdocs` (LOCAL Ollama keyword lane) | `docs_search` mgmt command → JSONL keyword search | Terminal-side developer lookups | KD-3 cascade-gap + KD-4 metadata-blank |
| Rigby SIGN cycle preamble | RAG-authoritative-doc lookup at SIGN routing | Pressure-test findings referenced against authoritative sources | KD-1 through KD-6 all-axis relevance |
| Verifier-loop pre-draft ORM probes | Direct Document / DocumentEmbedding queries | Claude Code verifier-loop discipline per RESEARCH_OS §7.1 Tier 5 | KD-2 stale-embed + KD-4 metadata-blank |
| Arc-close cascade PR `refresh_docs_corpus` | Beat task → `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents` fan-out | Post-close RAG corpus refreshed for next arc's Rigby SIGN | KD-3 cascade-PR-forgot-embed-step self-heal window |

**Two-lane structure (from S2101 §3 + S1301 P1).** LOCAL Ollama-backed
keyword lane (askdocs / docs_search) vs PROD pgvector semantic lane
(kb_tool.semantic_search / search_docs). P4 observes coupling at the
PROD lane primarily — LOCAL keyword lane is self-healing daily-beat-
driven and shows KD-1 = 0 baseline. PROD lane has the observed incidents.

**Live entry-point-disagreement incident (S2104 arc-open).** During
S2104 arc open at 2026-07-05, the same conceptual query routed to
`search_docs` returned 0 chunks with `excluded_missing_provenance: 7`
while `kb_tool.semantic_search` returned 12 chunks on the SAME PROD
pgvector backing store. Two nominally-same corpus surfaces disagreeing
on retrieval — captured live in §14 F5 as KD-5 manifestation at
retrieval-time. This is the archetype of the substrate-coupling problem
P4 investigates.

---

## 4. Major Models

**Read-side models observed in P4 evidence brief.** Reference S2101
§4 for write-side model coverage + S2102 §4 for ingestion-cascade
model coverage. P4 does not introduce new models — observation only.

| Model | Path | Relevant to P4 | Observation |
|-------|------|----------------|-------------|
| `Document` | `core/models.py` | Corpus baseline row count | 2,910 LOCAL rows at S2101 close; 2,908 embedded (99.93%) |
| `DocumentEmbedding` | `core/models.py` | Chunk-level retrieval unit | 51,952 LOCAL chunks (S2102 verifier-loop); 24,980 (48.2%) empty metadata (KD-4) |
| `DocumentChunk` | `core/models.py` | Chunk-level content unit | Same-count as DocumentEmbedding; chunker_id / chunker_version missing (S2103 T16 backlog) |
| `docs/_provenance.json` (file, not model) | Provenance store | KD-5 provenance-index-stale | INDETERMINATE freshness (S2101 KD-5); mtime matches _index.json today but no bound |
| `OpsRun(domain='mission', run_kind='docs_cascade')` | `core/models_ops_runs.py` | Cascade execution telemetry | Available via ops_tool.recent_runs (not enumerated at P4 open — deferred to §14 F1 evidence discharge) |
| `AgentExecution(agent_key='rigby_documentation_manager')` | `core/models.py` | Rigby SIGN + tool execution history | Reference surface for §14 F5 live incident routing history |
| `PeriodicTask('refresh-docs-corpus-daily')` | django-celery-beat | Cascade cadence enforcement | ENABLED, 4am Denver, hash-gated + unembedded-count fallback (S2101 §8) |

**Model-driven observations for §14:**
- KD-4 metadata-blank rate correlates with `DocumentEmbedding.metadata=={}` filter (24,980 / 51,952 = 48.2%).
- KD-3 cascade-PR-forgot-embed self-heal window bounded by daily beat cadence (~24h max persistence).
- KD-5 provenance-index-stale INDETERMINATE due to lack of freshness bound on `docs/_provenance.json` — this is itself a substrate-level measurability gap.

---

## 5. Major Services

**Retrieval-side services observed in P4 evidence brief.** Reference
S2101 §5 for write-side services + S2102 §5 for ingestion-cascade
services. P4 does not introduce new services — observation only.

| Service | Path | Relevant to P4 | Observation |
|---------|------|----------------|-------------|
| `RAGSystem` | `content/embeddings.py` | Core retrieval + embedding orchestration | Two-lane split at `RAGSystem.query` — LOCAL keyword vs PROD pgvector (S2101 §5 / S1301) |
| `_derive_source_type` | `content/embeddings.py:45-63` | Provenance write-site at ingest | `source=ContentSource.IMPORTED` monoculture (S2101 F1 root cause verified at `sync_docs_index_to_documents.py:340`) |
| `refresh_docs_corpus` | `core/tasks.py` | Beat task for daily cascade | ENABLED + hash-gated + unembedded-count fallback (S2101 §8) — self-heals partial step-4 failures |
| `MissionRunner (docs_cascade)` | `core/employees/mission_runner.py` | Employee OS-driven cascade orchestration | OpsRun(run_kind='docs_cascade') telemetry surface — feeds R4.5 Path B observation post-T13 execution |
| `kb_tool` handler | `core/services/tool_dispatcher.py` | Rigby PA tool for semantic search | Live incident §14 F5: returned 12 chunks on query where search_docs returned 0 |
| `search_docs` handler | `core/services/tool_dispatcher.py` | Rigby PA tool for docs-specific retrieval | Live incident §14 F5: returned 0 chunks with `excluded_missing_provenance: 7` on same query |
| `build_docs_provenance` mgmt command | `core/management/commands/` | Provenance-index rebuild | UNSCHEDULED (S2101 F4) — no beat, no cascade-hook; feeds R3.8 backlog + KD-5 root cause |

**Service-driven observations for §14:**
- `search_docs` vs `kb_tool.semantic_search` share the same PROD pgvector but apply different filters. `search_docs` filters on provenance-labeled chunks; when the provenance index is stale (KD-5), the filter drops chunks that DO have valid embeddings, producing the retrieval disagreement observed at S2104 arc open.
- `_derive_source_type` monoculture at `sync_docs_index_to_documents.py:340` (S2101 F1 root cause verified at S2103 close verifier-loop discharge) means the `Document.source` field is uniformly `IMPORTED` for all docs-cascade-ingested rows. This forces the retrieval authority framework (S2103 F1 7-axes) to rely on other axes (`document_class`, `is_pinned`, `min_session`) since `source` provides no discrimination.
- `MissionRunner (docs_cascade)` telemetry is the observation surface for R4.5 Path B activation once T13 (post-arc) executes. P4 flags this as HYPOTHETICAL evidence pending execution.

---

## 6. Major APIs and Interfaces

**Retrieval-time API surfaces observed in P4 evidence brief.** Focus
is on the boundaries where RAG-quality gradations become observable
to SIGN-quality consumers. Cross-reference S2101 §6 for write-side
API surfaces + S2102 §6 for ingestion API surfaces + S2103 §6 for
retrieval framework spec API surfaces.

### 6.1 Rigby PA tool retrieval boundary

**`kb_tool.semantic_search`** — Rigby's canonical PROD pgvector
semantic retrieval surface.

| Field | Value |
|-------|-------|
| Handler | `core/services/tool_dispatcher.py` |
| Underlying service | `content/embeddings.py::RAGSystem.query` |
| Filter dimensions | `category` / `document_class` / `is_pinned` / `min_session` / `include_superseded` (default true) / `similarity_threshold` (default 0.4) |
| Return shape | `{action, count, applied_filters, chunks[]}` with `similarity` + `importance` + `citation` per chunk |
| Live incident evidence | §14 F5 — returned 12 chunks on query where `search_docs` returned 0 |

**`search_docs`** — docs-specific corpus surface with provenance
filter applied at query-time.

| Field | Value |
|-------|-------|
| Handler | `core/services/tool_dispatcher.py` |
| Filter | `originating_session` + `pre_filter_count` + `excluded_mismatch` + `excluded_missing_provenance` counters returned in envelope |
| Return shape | `{query, result_count, k_requested, max_chars, truncated, total_chars, chunks[], filter}` |
| Live incident evidence | §14 F5 — returned 0 chunks with `excluded_missing_provenance: 7` on query where `kb_tool.semantic_search` returned 12 |

**Boundary observation.** Both handlers back onto the same PROD
pgvector but apply divergent filter chains. `search_docs` enforces
provenance-index match; `kb_tool.semantic_search` does not. When the
provenance index is stale (KD-5), `search_docs` under-returns while
`kb_tool` over-returns relative to human-judged retrieval intent.
Neither is "wrong" — both are honoring their filter contracts — but
the surface-vs-surface divergence is what §14 F5 observes as a
substrate-coupling incident. Retrieval-surface consistency check is
proposed as post-arc T26 in §15.

### 6.2 Cascade write-boundary

**`refresh_docs_corpus`** — beat task boundary between disk-state and
searchable corpus-state.

| Field | Value |
|-------|-------|
| Path | `core/tasks.py::refresh_docs_corpus` |
| Cadence | Daily 4am Denver (from S2101 §8) |
| Trigger conditions | (a) hash-delta on `docs/_index.json` OR (b) `unembedded_count > 0` OR (c) `force=True` param |
| Steps executed | `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → fan-out `generate_document_embeddings.delay()` per unembedded doc |
| Idempotency | Skip if hash unchanged AND `unembedded_count == 0` AND `not force` |

**Boundary observation.** `refresh_docs_corpus` is the enforceable
remediation hook cited in §14 F4 D2100.7 elevation. Its self-heal
window bounds the persistence of KD-3 cascade-PR-forgot-embed
incidents to ≤24h. Framework-wise, it is the mechanism that made
S1234's 12-day-stale incident non-repeatable (once installed) but
does NOT prevent the fresh incident from occurring at merge time —
the ≤24h window is the substrate's residual exposure.

### 6.3 Verifier-loop ORM boundary

**Django shell + management commands** — Claude Code's ORM boundary
for verifier-loop pre-draft probes per Research OS §7.1 Tier 5.

| Field | Value |
|-------|-------|
| Access surface | `python manage.py shell` |
| Common probes | `Document.objects.filter(embeddings__isnull=True).count()`, `DocumentEmbedding.objects.filter(metadata={}).count()`, `OpsRun.objects.filter(domain='mission', run_kind='docs_cascade').order_by('-created_at')[:30]`, `AgentExecution.objects.filter(agent_key='rigby_documentation_manager').order_by('-created_at')[:30]` |
| Cross-reference | S2101 §15.3 KD-1..KD-6 counts + S2102 §17 chunk-distribution stats |
| P4 observation | This surface is where the KD-taxonomy quantitative baseline lives. §14 F1-F4 reference S2101's probe outputs rather than re-running them. |

**Boundary observation.** Verifier-loop ORM probes are the pre-draft
discipline that Research OS §7.1 codifies. P4's observation shape
(§4 method) is that P1 already ran this discipline for the KD-taxonomy
baseline; P4 references those outputs rather than duplicating the
probes. Duplication would violate S1399 §10 meta-methodology anti-
pattern (re-measuring what a child audit already established).

---

## 7. Runtime Flows

**Retrieval-time runtime flow observed in P4.** Cross-reference S2102
§7 for the end-to-end ingestion (write-side) flow diagram. P4 focuses
on the read-side flow from query intent through SIGN preamble
consumption.

### 7.1 Canonical retrieval flow (`kb_tool.semantic_search`)

```
Query intent (Rigby SIGN preamble OR verifier-loop pre-draft)
    │
    ▼
kb_tool handler (core/services/tool_dispatcher.py)
    │
    ▼  applied_filters = {category, document_class, is_pinned,
    │                     min_session, include_superseded,
    │                     similarity_threshold}
    │
RAGSystem.query (content/embeddings.py)
    │
    ▼  pgvector similarity search against DocumentEmbedding.embedding
    │
    ▼  chunks[] sorted by (similarity × importance)
    │
Return envelope {action, count, chunks[]}
    │
    ▼
Rigby SIGN preamble consumption (grounded response with citations)
    OR
Verifier-loop pre-draft consumption (evidence for Claude draft)
```

### 7.2 Provenance-filtered retrieval flow (`search_docs`)

```
Query intent (Rigby SIGN preamble docs-scoped OR user askdocs)
    │
    ▼
search_docs handler (core/services/tool_dispatcher.py)
    │
    ▼  Pre-filter pgvector by embedding similarity → pre_filter_count
    │
    ▼  Apply provenance filter — cross-reference chunks against
    │  docs/_provenance.json → drop chunks with missing provenance
    │  (KD-5 chokepoint: stale provenance index drops valid chunks)
    │
    ▼  Apply session-scope filter — cross-reference chunks against
    │  originating_session → drop mismatches
    │
    ▼  Return envelope with counters:
    │  {result_count, filter: {pre_filter_count,
    │                          excluded_mismatch,
    │                          excluded_missing_provenance}}
    │
Rigby SIGN preamble consumption (docs-scoped grounded response)
```

**Divergence observation.** Both flows share the pgvector similarity
step but §14 F5 demonstrates the provenance-filter chokepoint dropping
chunks that DO have valid embeddings. The counter surface is
diagnostic (`excluded_missing_provenance: 7`) but does not
auto-trigger any remediation — the caller must interpret. Post-arc
T26 candidate: retrieval-surface consistency check + auto-trigger
provenance refresh when `excluded_missing_provenance > 0`.

### 7.3 Cascade write-side flow (reference from S2102 §7)

Not re-drawn here per anti-duplication (S1399 §10 meta-methodology).
Cross-reference S2102 §7 for `build_docs_index` → `build_rag_corpus`
→ `sync_docs_index_to_documents` → `embed_documents` fan-out.

### 7.4 SIGN preamble consumption flow

```
Rigby SIGN cycle open (on arc pin pa-18b095bb7c4740be)
    │
    ▼  Rigby chooses relevant retrieval surface based on prompt
    │  scope: kb_tool for cross-corpus; search_docs for docs-scoped
    │
    ▼  Retrieval returns chunks with citations
    │
    ▼  Rigby grounds SIGN pressure-test in retrieved chunks
    │
    ▼  Findings enumerate STRENGTHEN / CLEAN / FOLD / REJECT per Q
    │
    ▼  Claude Code folds pre-commit → doc lands
```

**Observation coupling point.** Steps 2-3 are where RAG-quality
directly affects SIGN-quality. Stale corpus (KD-3), unembedded docs
(KD-1), retrieval-surface disagreement (F5), or missing chunks
(KD-6 candidate) all manifest as SIGN pressure-test degradation. §14
F1 + F4 evidence brief documents this coupling qualitatively for
S1234 + S1802 + F5-live incidents.

---

## 8. Data Ownership and Lifecycle

**P4 observation shape.** Cross-reference S2103 §8 for the 5-state
lifecycle model (draft / active / canonical / superseded / deprecated)
+ hybrid metadata contract F5. P4 does not introduce new lifecycle
model — observation only. R4.7 lifecycle-transition observation
BACKLOG per gated-on-T21 status.

### 8.1 Lifecycle-state observation surface

Per S2103 §14 F7, the 5-state lifecycle model defines transitions:
- draft → active on Chris ratification
- active → canonical on xx99 aggregation
- active → superseded on newer-arc supersession (DE-RANKED-not-EXCLUDED per Q11 SIGN)
- any → deprecated on explicit retire signal

**P4 observation shape:** Once T21 (state-machine execution) lands,
Rigby SIGN preamble should be able to query lifecycle-state as an
authority-axis for retrieval ranking. Until then, P4 observes only
that the S2103 spec is ready and the observation window opens post-
arc.

### 8.2 Ownership shape from S2103 §18 F6 carried forward

Per S2103 F6 (owner assignments two-employee shape): Rigby EXECUTE +
Chief of Staff RECOMMEND, with NO new AIEmployee handles introduced.
P4 respects this shape — no owner assignments beyond what S2103
landed, only additions for P4-scoped observation debt (§18).

### 8.3 P4-new ownership candidates

- **Corpus Health Score ownership** (D2100.10 verdict pending — §14
  F3 + §20 close card): if D2100.10 verdict = "standing metric",
  ownership follows S2103 F6 shape (Rigby EXECUTE + CoS RECOMMEND).
- **Retrieval-surface consistency gate ownership** (T26 candidate):
  same shape.
- **Cross-arc governance-drift observation ownership** (T28 candidate
  per F8 R4.8): candidate for platform-scope observation arc —
  currently UNASSIGNED.

### 8.4 KD-taxonomy lifecycle observation

Each of KD-1..KD-6 has an implicit lifecycle:
- **Emerge**: cascade PR merge OR content-drift OR schema-drift event
- **Persist**: until remediation hook fires (daily beat / manual command / retrieval-time fallback)
- **Remediate**: `refresh_docs_corpus` (for KD-1/KD-3), `build_docs_provenance` (for KD-5), post-arc T22 (for KD-2/KD-4)
- **Verify**: verifier-loop ORM probes (§6.3)

**Observation:** the KD-1..KD-6 lifecycle is currently informal —
no telemetry surface exposes "incident opened → incident resolved"
durations. Corpus Health Score dimensions §14 F3 would formalize
this as a standing metric surface.

---

## 9. Integrations With Other Domains

**P4 observes cross-arc integration surfaces where RAG-quality
gradations couple to other domains' behavior.** Integration matrix
across Group 1300 / 1700 / 2000+ / 1800 delegated inheritance.

### 9.1 Group 1300 Memory (parent arc for RAG retrieval lanes)

**Delegated inheritance from S1301 + S1304 + S1399.** S1301 defined
the two-lane structure (LOCAL keyword vs PROD pgvector) that P4 §3
observes as the canonical entry-point split. S1304 T5 (`ingested_via`
write-path not wired to retrieval) STILL-VALID at S2101 close and
STILL-VALID at P4 observation — retrieval does not filter on
`ingested_via` today, so the KD-4 metadata-blank distribution does
not affect ranking except through the metadata-JSONField gate.

**P4 integration observation.** Memory arc gave us the retrieval lane
definitions; Group 2100 gave us the corpus governance. Coupling
point: SIGN preamble uses PROD pgvector via `kb_tool` (Memory arc
substrate) with corpus governance rules from Group 2100 (this arc's
substrate). §14 F5 live incident is the archetype of the two arcs'
substrates disagreeing at runtime.

### 9.2 Group 1700 Observability

**Delegated relationship.** S1304 T6 (filter-counter operator surface)
delegated to Group 1700 Observability arc (closed S1799). P4 observes
that `search_docs` DOES return the `pre_filter_count` +
`excluded_mismatch` + `excluded_missing_provenance` counters in its
envelope — but there is no operator-surface consumer (no Grafana
dashboard, no `logger.warning` on drop-rate threshold, no Prometheus
counter). §14 F5 live incident evidences the observability gap: the
raw counters were present but nobody was watching.

**P4-flagged observability debt:** T26 (retrieval-surface consistency
check) implies a consumer for these counters. Post-arc T-slot.

### 9.3 Group 2000+ Event / Integration Architecture

**Delegated inheritance from S2001 F3 + S2001 F9 + S2099 canonical.**
S2001 F3 identified SPIDER_DATA stream MISSING producer / WEAK
consumer pattern; the docs cascade has the analogous pattern:
cascade steps emit no lifecycle events (S2101 D7 + S2102 F-events).
Post-arc T-slot in S2103 §19.3 covers cascade-lifecycle events.

**P4 integration observation.** The event-substrate gap couples with
the observability gap (§9.2) — if cascade steps emitted
`event_bus.publish('docs_cascade.step_complete', {...})` events, the
observability consumer could subscribe to drift-detected /
embed-fanout / step-fail signals. This is exactly the shape
Group 2000+ formalized in the canonical seam statement.

### 9.4 Group 1800 Human Attention (cross-arc drift candidate)

**Cross-arc drift candidate observed.** S1899 canonical summary §142
mentions "F.d `AgentLearningSystem` ownership U3 — Sports arc
(S1599) or Learning arc (Group 1800)? U3 unresolved." — the same
substrate has ambiguous ownership across arcs. §14 F8 R4.8
observation classifies this as a governance-dimension mixed-mode
manifestation: had P3 §14 F4 5-meaning disambiguation table been
applied at S1599 or S1800 authorship, the ownership dimension would
have forced explicit resolution.

**Implication for §17 integration matrix.** Cross-arc governance drift
is a KD-adjacent incident class — the RAG substrate is not directly
implicated but the same disambiguation discipline that P3 formalizes
for RAG governance dimensions extends naturally to cross-arc
governance.

### 9.5 Employee OS integration

**Reference to `EMPLOYEE_OS_PRIMITIVES.md`.** P4 does not introduce
new employees or job contracts; per S2103 F6 shape, Rigby EXECUTE +
Chief of Staff RECOMMEND absorbs P4 owner-assignment additions.
Employee OS integration is by-reference only — the primitives are
the substrate; Group 2100 authorship extends the substrate with
corpus governance responsibilities.

---

## 10. Event Flows

**P4 observation: docs cascade is event-silent.** S2101 D7 + S2102
F-events documented that cascade steps emit no lifecycle events. P4
observes this from the read-side: verifier-loop probes cannot detect
in-flight cascade failures except via post-hoc unembedded-count
polling. §14 F1 KD-3 evidence relies on this exact detection gap —
S1802's 6-unembedded-docs incident was caught by post-hoc grep, not
by any event-driven telemetry.

### 10.1 Absent event stream inventory

Per S2101 D7 candidate design decisions, the cascade SHOULD emit
these events but does not today:

| Event | Would enable | Current substitute |
|-------|--------------|--------------------|
| `docs_cascade.step_start` | Step-level pipeline observability | None (log grep only) |
| `docs_cascade.step_complete` | Per-step timing + result envelope | Task return value only |
| `docs_cascade.step_fail` | Fail-loud on step failure | Silent success + downstream detection |
| `docs_cascade.embed_fanout_queued` | Fan-out cardinality tracking | Fan-out task creation is fire-and-forget |
| `docs_cascade.drift_detected` | KD-detection surface | Post-hoc verifier-loop only |

**Consumer candidates (post-arc):** Grafana dashboard subscribing to
step-complete for cadence + latency; Corpus Health Score
subscribing to drift-detected for real-time score updates;
verifier-loop consuming step-complete for pre-draft freshness bound.

### 10.2 Present ORM-poll event substitute

Verifier-loop discipline (§6.3) provides polling-based observability
as substitute:

- `Document.objects.filter(embeddings__isnull=True).count()` at any
  time reveals KD-1 count.
- `OpsRun.objects.filter(domain='mission', run_kind='docs_cascade')
  .order_by('-created_at')[:30]` at any time reveals recent cascade
  invocation history.
- `AgentExecution.objects.filter(agent_key='rigby_documentation_manager')
  .order_by('-created_at')[:30]` reveals recent Rigby SIGN + tool
  execution history for cross-referencing incidents.

**Observation coupling limit.** ORM-poll substitute is adequate for
retrospective observation (P4's shape) but INADEQUATE for in-flight
SIGN-preamble corpus-hygiene gates (§14 F3 Corpus Health Score
threshold + §20 lens-answer gate proposals). Corpus Health Score
implementation would require the missing event stream OR periodic
snapshotting.

---

## 11. Existing Documentation

**P4-scope documentation inventory** — the docs that either
authorized or informalized the observed incidents. Cross-reference
S2103 §11 for the retrieval framework documentation matrix.

### 11.1 Formal governance docs (post-S2103 spec)

- `2100_rag_document_loading_domain_scoping.md` — arc frame + D2100.5
  authority + §5.1 institutional-knowledge-layer acceptance criteria
  + §5.4 P4 scope + §5.5 Corpus Health Score candidate list
- `2101_rag_document_loading_corpus_state_reality_knowledge_gap_audit.md`
  — corpus baseline + KD-1..KD-6 taxonomy + §15.3 incident matrix
- `2102_rag_document_loading_ingestion_chunking_embedding_pipeline_audit.md`
  — cascade end-to-end + Path A/B distinction + chunker regime map
- `2103_rag_document_loading_retrieval_authority_framework_corpus_governance_design.md`
  — F1 7-axes framework + F5 metadata contract + F7 lifecycle model
- `KNOWLEDGE_PIPELINE.md` — existing narrative flow map (companion
  anchor)
- `DOC_LIFECYCLE.md` — §2c inventory-wins-on-conflict rule (RAG-
  adjacent governance)
- `EMPLOYEE_OS_PRIMITIVES.md` — anti-duplication + primitive re-use
  discipline (RAG substrate honors this)

### 11.2 MEMORY.md informal governance rules

These rules pre-date the S2103 formal framework and are the informal
substrate P3 F1 formalized. P4 observes they are still authoritative
at the workflow layer even though formal spec exists:

- `feedback_docs_pipeline_4_step_cascade` — 4-step cascade rule
  (build_docs_index + build_rag_corpus + sync + embed)
- `feedback_cascade_pr_must_include_embed_step` — S1802 codification
  requiring step 4 embed evidence in cascade PR body
- `feedback_docs_cascade_at_every_close` — S1399 close directive
  requiring cascade at every arc/session close
- `feedback_verify_before_deleting_dead_code` — Chris S1242 discipline
  applied indirectly to docs (verify before deprecating)
- `feedback_docs_pipeline_4_step_cascade` (Session 1234) — 4-step
  cascade discipline codification

**P4 observation.** The informal MEMORY.md substrate + the formal
S2103 spec co-exist. This is not per-se a boundary violation, but
§16 flags it as a candidate consolidation: MEMORY.md rules should
POINT INTO the S2103 formal spec once T23 (`RAG_CORPUS_GOVERNANCE.md`
publish) lands, not duplicate it.

### 11.3 Cross-arc documentation touchpoints

- S1301 memory RAG retrieval lanes audit — two-lane structure
- S1304 memory docs↔RAG boundary audit — cascade + provenance origins
- S1399 memory canonical summary — Group 1300 close
- S1699 content canonical summary — cross-arc `auto_publish` correction
- S1799 observability canonical summary — filter-counter operator surface (T6)
- S1899 human attention canonical summary — §142 AgentLearningSystem U3 (F8 R4.8)
- S1999 Employee OS canonical summary — Employee OS primitives
- S2099 Event / Integration Architecture canonical summary — event-substrate gap

### 11.4 Observation on the informal→formal transition

S2103 §14 F1 formalization of retrieval authority does not obviate
MEMORY.md — Chris relies on MEMORY.md rules as active workflow
discipline. Post-arc coordination discipline (§20 close-card
candidate): as T23/T24/T25 publish, MEMORY.md rules should be
audited for point-into-vs-duplicate posture. This is a §17
integration matrix item.

---

## 12. Research Coverage

**P4-scoped research coverage matrix.** For each RAG-quality axis and
each SIGN-quality effect category, identify what research already
established and what P4 observation adds.

### 12.1 Research already established (P1-P3 inheritance)

| Substrate area | Research doc | What it established |
|----------------|--------------|---------------------|
| Corpus state baseline | S2101 P1 | 2910 docs / 2908 embedded / KD-1..KD-6 taxonomy + LOCAL counts |
| Ingestion cascade | S2102 P2 | 4-step cascade + Chunker A/B/C regimes + Path A vs Path B + chunk distribution (n=51,952) |
| Retrieval framework | S2103 P3 | F1 7-axes + F2 3-part conflict rule + F4 5-meaning disambiguation + F5 metadata contract + F7 5-state lifecycle |
| Retrieval lanes | S1301 (Memory) | LOCAL keyword vs PROD pgvector split |
| Docs↔RAG boundary | S1304 (Memory) | T1-T8 boundary debt items — T5 (`ingested_via` retrieval-not-wired) STILL-VALID |
| Memory canonical | S1399 | Group 1300 close + R5 turn-context handoff |
| Cascade cadence | S1234 (handoff) | `refresh_docs_corpus` daily-beat installation |
| Cascade PR discipline | S1802 (handoff) | 4-step-cascade-rule + step-4-embed-required |

### 12.2 Research P4 adds (observation-shape delta)

| P4 observation contribution | Evidence source |
|------------------------------|------------------|
| Qualitative "RAG-quality affects SIGN-quality" evidence brief | §14 F1-F5 (N = 14 incidents classified) |
| D2100.7 elevation verdict | §14 F4 evidence + P2/P3 remediation hooks |
| D2100.10 Corpus Health Score standing-metric verdict candidate | §14 F3 + §20 close card |
| §14 F5 live incident capture (search_docs vs kb_tool disagreement) | S2104 arc-open Rigby tool-run verbose block |
| §17 integration matrix across P1-P3 + P4 | §17 (Pass B) |
| Defended answer to central lens question | §20 (Pass C) |
| SIGN-quality quality-gate proposals (Q9 discharge) | §14 F3 SIGN preamble additions + §20 gate proposals |

### 12.3 Research P4 explicitly does NOT do

- **Re-measure P1/P2 quantitative baselines** — anti-pattern per
  S1399 §10.3.2.
- **Introduce new lifecycle model or metadata contract** — S2103 F5/F7
  already ratified; P4 respects and observes.
- **Introduce new owner assignments beyond S2103 F6 shape** —
  P4-scoped only.
- **Run Option B controlled experiment** — parked as post-arc T-slot
  (§20.5).
- **Ship implementation** — arc anti-scope per parent §7.1.

### 12.4 Research P4 flags as NEXT (S2199 xx99 + post-arc)

- xx99 canonical seam statement synthesizing P1-P3 + P4 (§19.1 R99.1)
- Post-arc T22 metadata contract execution unblocking F6/F7 discharge
- Post-arc T13 Path B activation unblocking F7 discharge
- Post-arc T21 state-machine execution unblocking R4.7 discharge
- Post-arc structured cross-arc governance-drift observation (F8 R4.8)

---

## 13. Architecture Maturity

**P4-scoped maturity dimensions across the RAG substrate.** Table
below scores each dimension with evidence + delta from S2101/S2102/
S2103 posture. `HIGH` = production-quality + measurable +
enforceable. `MEDIUM` = designed + partially-observable but not
enforced. `LOW` = gap identified. `INDETERMINATE` = no measurement
substrate exists yet.

| Dimension | Maturity | Evidence | Delta from S2103 |
|-----------|----------|----------|--------------------|
| Cascade execution | HIGH | `refresh_docs_corpus` daily-beat idempotent + hash-gated + unembedded-count fallback (S2101 §13) | unchanged |
| Cascade coverage | HIGH | LOCAL: 100% Document rows embedded; 2905/2910 on-disk indexed (S2101 §13) | unchanged |
| Cascade freshness | MEDIUM-HIGH | Daily beat cadence + hash-delta gate (S2101 §13) | ELEVATED — §14 F4 D2100.7 provisional contract adds enforceability |
| Retrieval consistency across surfaces | LOW-MEDIUM | §14 F5 live incident: search_docs vs kb_tool disagreement | NEW P4-observed dimension — not in S2103 posture register |
| Provenance-index freshness | INDETERMINATE | KD-5 no automated freshness bound (S2101 §15.3); build_docs_provenance unscheduled (S2101 F4) | unchanged |
| Metadata population | LOW | 24,980 / 51,952 = 48.2% KD-4 blank (S2101 KD-4) | unchanged; T22 post-arc addresses |
| Chunker regime documentation | HIGH-MEDIUM | S2102 F1-F3 documented Chunker A/B/C regimes; T16 chunker_id backlog | unchanged |
| Retrieval authority spec-readiness | HIGH | S2103 F1 7-axes framework spec-complete; T18/T19 post-arc execution | unchanged (P4 §14 F6 HYPOTHETICAL) |
| Governance-dimension disambiguation | HIGH | S2103 F4 5-meaning table | unchanged |
| Artifact lifecycle model spec-readiness | HIGH | S2103 F7 5-state model; T21 post-arc execution | unchanged (P4 §14 F8 HYPOTHETICAL) |
| Hybrid metadata contract | HIGH | S2103 F5 ratified (9 core-required + 2 available + 3 profiles + 4 derivable + 5 aspirational); T22 post-arc | unchanged |
| Owner assignments | HIGH | S2103 F6 two-employee shape (Rigby EXECUTE + CoS RECOMMEND) | unchanged |
| Behavior substrate coupling — observability | LOW | This is exactly what P4 §14 evidence brief measures qualitatively | NEW — was not in S2103 posture register |
| Cascade lifecycle-event emission | LOW | S2101 D7 + S2102: no events emitted | unchanged |
| Retrieval-surface counter consumption | LOW-MEDIUM | Counters returned in envelope but no operator surface (S1304 T6 delegated to Group 1700 — no consumer) | unchanged |

### 13.1 P4-added maturity dimensions (not in S2103 posture register)

- **Retrieval consistency across surfaces** — introduced by §14 F5
  live incident observation. LOW-MEDIUM until T26 (retrieval-surface
  consistency check) lands.
- **Behavior substrate coupling observability** — the meta-dimension
  P4 investigates. LOW today. Corpus Health Score standing metric
  would elevate to MEDIUM-HIGH.
- **Retrieval-surface counter consumption** — LOW-MEDIUM. Counters
  exist; no consumer. Post-arc T26 would elevate.

### 13.2 Maturity synthesis for §20 lens-question answer

Maturity table reveals a HIGH-tier spec-readiness (F1/F5/F6/F7 ratified
by S2103) coupled with LOW-tier execution + observability today. This
is the DESIGN-COMPLETE-BUT-NOT-EXECUTED posture S2103 §17.1 identified.
P4's observation contribution is that the LOW-tier observability
directly caused the S1234 + S1802 + F5-live incidents — the substrate
IS coupled (RAG-quality affects SIGN-quality qualitatively) but the
substrate is UN-INSTRUMENTED so the coupling was invisible until
retrospective observation caught it.

**Institutional-knowledge-layer posture (per parent §5.1 criteria):**
- Criterion 1 (docs are ingestible + retrievable) — SATISFIED (LOCAL 100% embedded).
- Criterion 2 (chunker regime documented) — SATISFIED via S2102 F1-F3.
- Criterion 3 (metadata contract defined) — SATISFIED via S2103 F5 (execution gated on T22).
- Criterion 4 (lifecycle model defined) — SATISFIED via S2103 F7 (execution gated on T21).
- Criterion 5 (governance dimensions disambiguated) — SATISFIED via S2103 F4.

**All 5 acceptance criteria SATISFIED at design layer.** Execution gate
carries the residual risk. §20 defends this posture as the lens-question
answer.

---

## 14. Findings F1-F8

**Structural note.** F1-F5 are OBSERVATION findings — evidence
classified against the 14-incident corpus. F6-F8 are HYPOTHETICAL /
BACKLOG findings — flagged for post-arc T-slot observation once
execution ships. Each finding follows the standard shape: (a) thesis,
(b) evidence (with citations), (c) classification (RAG-axis × SIGN-
effect matrix), (d) verdict, (e) implication for §17 integration
matrix + §20 lens-question answer.

**Label legend per Rigby SIGN Batch 2 Q7 STRENGTHEN 2026-07-05.** Two
distinct HYPOTHETICAL shapes are distinguished:
- **HYPOTHETICAL (execution-gated)** — cannot be observed until
  implementation lands. Requires a specific T-slot to execute
  before observation can begin. Applies to F6 (T18/T19), F7 (T13),
  F8-R4.7 lifecycle transitions (T21).
- **HYPOTHETICAL (cadence-gated)** — observable today but requires
  repeated sampling to promote from EVIDENCE-CANDIDATE (single-
  instance) → EVIDENCE-SUPPORTED (repeated pattern). Applies to
  F8-R4.8 (cross-arc governance drift, S1899 §142 single instance).
- **EVIDENCE-CANDIDATE (single-instance)** — one concrete observed
  instance but not-yet-repeatable. Requires additional sampling
  before elevation. Distinguished from HYPOTHETICAL because
  observation has begun.
- **EVIDENCE-SUPPORTED** — repeated pattern across ≥2 diverse
  incidents. F1 (S1802 + KD-3 baseline) and F5 (S2104 live +
  cross-surface pattern) qualify; F4 D2100.7 elevated to
  EVIDENCE-SUPPORTED via §14 F4 diversity+actionability rationale.

### 14.1 F1 — Cascade-PR-forgot-embed-step (KD-3) is a real and observed SIGN-blindness incident class

**Thesis.** Cascade PRs that ship steps 1-3 (`build_docs_index` +
`build_rag_corpus` + `sync_docs_index_to_documents`) without step 4
(`embed_documents --all-unembedded`) produce a bounded RAG-blindness
window at PROD until the next-day `refresh_docs_corpus` beat fires.
Within that window (worst case ~24h under a healthy daily beat),
Rigby SIGN cycles pressure-testing arcs whose docs shipped in the same
PR treat as-authoritative docs the corpus cannot semantically retrieve.

**Bound note per Rigby SIGN Batch 1 Q2 STRENGTHEN 2026-07-05.** The
PROD blindness window is **bounded by the next successful corpus
refresh**, nominally ~24h under a healthy daily beat, but can exceed
24h under beat failure/delay or absent a manual refresh.

**Precision on "RAG blind" per same Q2 STRENGTHEN.** "RAG blind" here
means **semantic retrieval surfaces (`kb_tool.semantic_search` /
`search_docs` / embeddings) could not retrieve the newly-shipped
docs**, even though the docs were present in-repo and readable by
direct path (verifier-loop file-read discipline still worked; only
the semantic + provenance-filtered lanes were blind).

**Evidence.** S1802 close 2026-07-03 caught 6 unembedded docs across
Group 1800 arc S1800-S1802. Rigby's semantic retrieval surfaces
(`kb_tool` + `search_docs`) were blind to those docs for the arc
open-to-close window. Rule codified as MEMORY.md
`feedback_cascade_pr_must_include_embed_step`.

**Classification.** RAG-axis: KD-3 cascade-PR-forgot-embed-step.
SIGN-effect: DEGRADED PRESSURE-TEST (SIGN did not fail loudly; it
proceeded on stale semantic corpus with informal-narrative fallback).

**Verdict.** Elevated to R4.4 D2100.7 conditional-elevation evidence
input. Pass B expands F1 with the specific S1234 12-day-stale
predecessor incident + `refresh_docs_corpus` remediation coverage
limits (§14.4 F4 covers D2100.7 verdict).

### 14.2 F2 — Chunker B (sync-cascade) vs Chunker C (async) population imbalance is measurable but ambiguous for SIGN-effect correlation

**Thesis.** S2102 P2 F2/F3 documented Chunker B (sync-cascade write-
site at `sync_docs_index_to_documents.py:337`) vs Chunker C (async
write-site at `embed_documents` mgmt command) as two co-existing
chunker regimes with different parameter defaults. R4.1 P4 handoff
asks whether recent SIGN cycles failing retrieval-quality checks
correlate with hitting Chunker B or Chunker C populations. Observation
verdict: measurable BUT insufficient N to elevate F2 severity from
MEDIUM to HIGH.

**Evidence.** S2102 §17 chunker-population analysis (n=51,952 LOCAL
chunks). Pass B expands F2 with specific SIGN-cycle-retrieval-failure
enumeration + chunker-ID cross-reference (blocked on T16 chunker_id
schema addition — post-arc).

**Classification.** RAG-axis: KD-4 metadata-blank-at-ingest (48.2%)
correlates strongly with `ingested_via='sync_docs'` = Chunker B path.
SIGN-effect per Rigby SIGN Batch 1 Q3 STRENGTHEN 2026-07-05:
**NO OBSERVED BASELINE RETRIEVAL FAILURE** — chunks still embed +
are retrievable by similarity, but **INSUFFICIENT EVIDENCE** to
claim no effect on higher-order behaviors (filtering by metadata,
authority labeling per S2103 F1 7-axes, lifecycle gating per S2103 F7,
conflict-resolution semantics per S2103 F2). "NO MEASURABLE EFFECT"
would be too strong given P4 has not run authoritative retrieval-
quality tests that could reveal second-order harm; the safer posture
is baseline-similarity-preserved + higher-order-behavior-untested.

**Verdict.** F2 remains MEDIUM per S2102. R4.1 discharge: correlation
is documented but insufficient N to elevate. Post-arc T16 chunker_id
schema addition unblocks re-observation.

### 14.3 F3 — Corpus Health Score dimensions ratified — D2100.10 verdict candidate

**Thesis.** Per R4.3 must-ship + parent §5.5 candidate list, P4
proposes the final Corpus Health Score dimension set with weights and
threshold defaults. §14 F3 lists dimensions; §20 close card presents
D2100.10 standing-metric-vs-arc-artifact-only verdict.

**Dimensions (14 candidates, weighted — updated per Rigby SIGN Batch 1
Q4 STRENGTHEN 2026-07-05 from 12 → 14 with deduplication + additions):**

1. Cascade execution health (from S2101 §13)
2. Cascade coverage (embedded / on-disk ratio)
3. **Cascade freshness — global distribution** (daily-beat + hash-delta
   cadence). *Global freshness distribution across all corpus docs.*
4. Provenance-index freshness (KD-5 mitigation)
5. **Metadata population rate — overall non-null** (KD-4 mitigation).
   *Overall non-null rate across all metadata fields.*
6. Chunker regime distribution (Chunker B vs C balance)
7. Retrieval-surface consistency (`search_docs` vs `kb_tool` agreement)
8. Authority-axis coverage (7-axes populated per S2103 F1)
9. **D2100.9 metadata contract population rate — required-field
   completeness only.** *Distinct from #5: measures completeness of
   the 9 core-required + 2 core-available fields specifically, not
   overall metadata non-null.*
10. F7 lifecycle-status transition validity rate
11. Canonical-summary coverage (xx99 embedded confirmation)
12. **Latest-arc freshness — freshness slice.** *P95 age for last-N
    arc docs. Slice of #3 global distribution; both retained + labeled
    slice-vs-global per Q4 fold.*
13. **Cascade reliability + latency (Q4 fold NEW).** Success rate of
    cascade / embed jobs + p95 runtime. Detects beat-failure /
    embed-fanout-timeout as a substrate-level KD class not in KD-1..KD-6.
14. **Supersession graph integrity (Q4 fold NEW).** No orphan canonicals,
    no cycles, superseded-by pointers resolvable. Distinct from #10
    lifecycle-transition-validity: #10 measures per-transition rule
    compliance, #14 measures cross-transition graph consistency.

**Deduplication note per Q4 STRENGTHEN.** Dimensions #3 and #12 are
retained + labeled as global-vs-slice (rather than collapsed). Dimensions
#5 and #9 are split by scope (overall non-null vs contract-required-
field completeness) to prevent one absorbing the other. New dimensions
#13 and #14 close substrate-baseline gaps that pre-cycle SIGN preamble
would otherwise miss.

**Verdict.** Pass B fleshes out weight defaults + threshold defaults
+ dashboard-surface recommendation. §20 close card D2100.10 verdict
question: standing governance metric (with dashboard + cadence + Rigby
SIGN preamble surface) OR Group 2100 arc artifact only.

### 14.4 F4 — D2100.7 freshness-bound conditional-elevation verdict — ELEVATE hypothesis → provisional contract (evidence-supported)

**Thesis.** Per Q15 SIGN STRENGTHEN 2026-07-04 at S2101 close, D2100.7
"RAG freshness bounds SIGN quality" hypothesis elevates from hypothesis
→ provisional contract IF observation finds repeated attributable
patterns AND framework provides enforceable remediation hooks. P4
verdict: BOTH conditions met — ELEVATE.

**Evidence supporting elevation:**
- S1234 12-day-stale prod corpus + 1820-never-pushed Documents — SIGN
  cycles during the stale window necessarily missed 1820 docs' worth
  of authoritative content.
- S1802 6-unembedded-docs cascade-PR incident — RAG blind for entire
  Group 1800 arc window S1800→S1802 (~2 sessions).
- S2104 arc-open live incident (§14 F5) — `search_docs` returned 0
  chunks with `excluded_missing_provenance: 7`; retrieval-time
  freshness gap manifests as retrieval-time blindness.

**Enforceable remediation hooks (from P2 + P3):**
- `refresh_docs_corpus` daily beat (S2101 §8) — hash-gated + unembedded-
  count fallback provides self-heal window ≤24h.
- MEMORY.md `feedback_cascade_pr_must_include_embed_step` (S1802
  codification) enforces cascade PR embed step.
- Post-arc T22 metadata contract (S2103 F5) — enables freshness dimensions
  on chunks + docs.
- Post-arc T18/T19 axis-scoring service + rule engine (S2103) — enables
  freshness as a retrieval authority axis.

**Verdict per Rigby SIGN Batch 1 Q5 STRENGTHEN 2026-07-05.** ELEVATE
D2100.7 from hypothesis → **provisional contract** based on 3
independent attributable incidents (S1234 + S1802 + live S2104 §14 F5)
**plus** a **partial enforcement path available now** (manual /
`refresh_docs_corpus` daily beat + MEMORY.md
`feedback_cascade_pr_must_include_embed_step` workflow rule), with
**full enforcement gated post-arc on T22 (metadata contract) + T18
(axis-scoring service) + T19 (rule engine)**.

**Promotion threshold framing.** Not an arbitrary N=5 count.
Promotion criterion is **incident diversity + actionability**:
- Diversity satisfied — S1234 (12-day-stale), S1802 (cascade-PR-forgot-
  embed), §14 F5 (retrieval-surface disagreement at retrieval-time)
  span three distinct RAG-quality axes.
- Actionability satisfied — partial enforcement path exists NOW;
  full enforcement path is ratified (T22/T18/T19) though execution
  is post-arc.

**Revisit threshold.** After N ≥ 5 additional incidents OR after
first enforcement cycle (T22 metadata contract landing), whichever
comes first. §20 close card presents this verdict for Chris
ratification.

### 14.5 F5 — LIVE incident captured at S2104 arc open: `search_docs` vs `kb_tool.semantic_search` retrieval disagreement

**Thesis.** During S2104 arc-open ORM probes routed to Rigby, the same
conceptual query returned 0 chunks via `search_docs` (with
`excluded_missing_provenance: 7`) and 12 chunks via
`kb_tool.semantic_search`. Two nominally-same corpus surfaces backed
by the SAME PROD pgvector disagreed on retrieval. This is a KD-5
(provenance-index-stale) manifestation at retrieval-time — the
provenance filter applied by `search_docs` dropped chunks that had
valid embeddings.

**Evidence.** Captured 2026-07-05 in S2104 arc-open Rigby tool-run
verbose block:

```
[OK] search_docs (492ms)
    Result: {"result_count": 0, "chunks": [],
             "filter": {"originating_session": 0,
                        "pre_filter_count": 7,
                        "excluded_mismatch": 0,
                        "excluded_missing_provenance": 7}}

[OK] kb_tool (532ms)
    Result: {"action": "semantic_search", "count": 12, ...
             citations to
             docs/research/domains/human_attention/1899_*.md#142,
             docs/handoffs/SESSION_1804_*.md, ... }
```

**Classification.** RAG-axis: KD-5 provenance-index-stale +
retrieval-surface-inconsistency (composite). SIGN-effect: WRONG
FINDINGS candidate (if the S2104 arc-open incident-enumeration probe
had blindly trusted `search_docs`, it would have concluded the corpus
had no S1802 evidence — false negative). RECOVERED by consulting
`kb_tool` cross-surface + repo grep verification.

**Verdict.** F5 evidences the substrate-coupling problem P4 investigates
directly. Two retrieval surfaces disagreeing on the same query is the
substrate at its most visible. Recommendation: SIGN preamble should
require retrieval-surface cross-check when one surface returns 0
chunks + provenance-exclusion count > 0. Post-arc T-slot candidate.

**Remediation refinement per Rigby SIGN Batch 2 Q6 STRENGTHEN 2026-07-05.**
Auto-triggering provenance refresh solely on
`excluded_missing_provenance > 0` is too hair-trigger for HIGH severity —
can create cascading load + mask underlying indexing divergence. Split
T26 into two sub-slots:
- **T26a Detect-and-Flag** (always-on consistency check; return partial
  results with explicit warning when `excluded_missing_provenance > 0`;
  raise an attention item)
- **T26b Guarded Auto-Remediate** (trigger provenance refresh only if
  mismatch persists across ≥2 checks OR exceeds a threshold, with
  cooldown/rate-limit + audit log)

Default behavior at T26a landing: return partial results + warning.
Auto-remediation at T26b is gated on repeatability signals. §15.2 T26
row + §19.2 T-slot + §19.4 handoff table + §20.4 Item 2 close card
updated to reflect T26a/T26b split.

### 14.6 F6 — Retrieval-authority framework acceptance — HYPOTHETICAL until T18/T19 post-arc execution

**Thesis.** R4.6 P4 handoff asks whether observed retrieval queries
show authority-provenance labels matching human-judged authority. Verdict:
observation IMPOSSIBLE at present because T18 (axis-scoring service)
+ T19 (conflict-resolution rule engine) + T22 (metadata contract) are
POST-ARC EXECUTION items. Without T22 landing, no authority labels are
emitted at retrieval-time. F6 remains HYPOTHETICAL.

**Evidence.** S2103 §17.1 spec-readiness register: framework is DESIGN-
COMPLETE-BUT-NOT-EXECUTED. Post-arc T-slot queue lists T18/T19/T22 as
Track B gates.

**Classification.** RAG-axis: N/A (framework not yet acting on
retrieval). SIGN-effect: N/A pending execution.

**Verdict.** F6 remains HYPOTHETICAL. Discharge deferred to post-arc
observation after T22 lands. §19 P4 → xx99 handoff carries F6 as
DESIGN-COMPLETE-BUT-NOT-EXECUTED per S2103 xx99 §10 candidate.

### 14.7 F7 — Path A vs Path B activation — HYPOTHETICAL pending T13 execution (PROMOTED per Chris pick (b) at S2103 close)

**Thesis.** R4.5 P4 handoff (PROMOTED from BACKLOG per Chris pick (b)
fold Path A into Path B at S2103 close 2026-07-04). Observation asks
whether N ≥ 10 daily runs after Path B beat wiring show escalation
Deliverable dedupe accuracy + step_5 drift observation reliability.
Verdict: observation IMPOSSIBLE at present because T13 is Track A
T0/Gate — Path B beat not yet wired.

**Evidence.** S2103 §19.3 T-slot table: T13 depends on Chris D-verdict
at S2103 close card = (b) fold Path A into Path B → path B wired +
observed stable → then contract population instrumentation.

**Classification.** N/A pending T13 execution.

**Verdict.** F7 remains HYPOTHETICAL. Discharge deferred to post-arc
observation after T13 lands + N ≥ 10 daily runs accumulate. §19 P4
→ xx99 handoff carries F7 as DESIGN-COMPLETE-BUT-NOT-EXECUTED.

### 14.8 F8 — Governance-dimension mixed-mode + artifact lifecycle-transition — HYPOTHETICAL pending T21 execution + cross-arc drift observed

**Thesis (combined R4.7 + R4.8).** R4.7 asks whether artifact
lifecycle-transitions match designed rules after T21 state-machine
lands. R4.8 asks whether P3 §14 F4 5-meaning governance disambiguation
table would have prevented observed cross-arc governance drift. F8
combines both because both remain HYPOTHETICAL / observational-only in
this arc.

**Evidence for R4.8 candidate drift.** S1899 canonical summary §142
mentions "F.d `AgentLearningSystem` ownership U3 — Sports arc (S1599)
or Learning arc (Group 1800)? U3 unresolved." — cross-arc scope drift
where the same substrate ownership is ambiguous across arcs. P3 §14
F4 5-meaning disambiguation table applied at authorship time would
have forced explicit ownership dimension selection. Candidate incident
class for post-arc structured observation.

**Evidence for R4.7.** N/A pending T21 execution.

**Classification.** RAG-axis: cross-arc governance drift (KD-adjacent
class). SIGN-effect: DEGRADED PRESSURE-TEST candidate — SIGN cycles
during the ambiguous window would have to choose between arc-contexts
implicitly.

**Verdict per Rigby SIGN Batch 2 Q7 STRENGTHEN 2026-07-05.** F8
combined verdict now uses refined label legend (§14 preamble):
- **F8 R4.7 lifecycle-transitions** — HYPOTHETICAL (execution-gated)
  pending T21 state-machine execution.
- **F8 R4.8 cross-arc governance drift** — reclassified from
  HYPOTHETICAL → **EVIDENCE-CANDIDATE (single-instance)** with
  S1899 §142 as first observed instance. Promotion threshold: ≥2
  more instances observed via T28 cadence sweep (§15.2 + §19.2).
  Explicit "needs repeatability" note carries forward.

§19 P4 → xx99 handoff carries F8 forward with legend-consistent
labels. §20.3 R4.7 + R4.8 rows updated post-fold.

---

## 15. Known Technical Debt

**P4-scoped debt table.** Inherits S2101 T1-T10 + S2102 T11-T17 +
S2103 T18-T25 by reference (see those docs' §15). Adds P4-scoped
observation debt below.

### 15.1 Inherited debt reference (P1-P3)

- **S2101 T1-T10** — corpus-state debt (T1 `docs/_index.json`
  cadence unmanaged; T2 `lru_cache(1)` staleness; T3 provenance
  unscheduled; T4 docs-ingestion-cascade topic doc unpublished; T5
  `ingested_via` retrieval-not-wired; T6 filter-counter operator
  surface; T7 corpus-completeness gap detection; T8 provenance model
  ownership; T9 cascade emits no lifecycle events; T10 chunker
  parameters not persisted).
- **S2102 T11-T17** — pipeline debt (T11 KD-2 hash substrate; T12
  cascade instrumentation; T13 dual-cascade resolution — Track A
  T0/Gate; T14 async cascade retry policy; T15 Chunker A/B/C schema
  distinction; T16 chunker_id + chunker_version schema; T17
  `_derive_source_type` write-site fragmentation).
- **S2103 T18-T25** — framework debt (T18 axis-scoring service;
  T19 conflict-resolution rule engine; T20 owner-assignment PR; T21
  artifact lifecycle state machine; T22 D2100.9 metadata contract —
  Track B T0/Gate; T23 `RAG_CORPUS_GOVERNANCE.md` publish; T24
  `retrieval-authority-framework.md` publish; T25
  `docs-ingestion-cascade.md` publish + T-D2100.11 retrofill + T-F6
  backfill retirement).

### 15.2 P4-scoped debt additions

| T-slot | Description | Severity | Origin | Depends on |
|--------|-------------|----------|--------|-------------|
| **T26a** (P4-new, post-Q6 fold) | Retrieval-surface consistency check between `search_docs` and `kb_tool.semantic_search` — **Detect-and-Flag** — always-on check; return partial results + explicit warning when `excluded_missing_provenance > 0`; raise attention item | HIGH | §14 F5 live incident | T6 operator surface (Group 1700 delegated); independent from Track B |
| **T26b** (P4-new, post-Q6 fold) | Retrieval-surface consistency **Guarded Auto-Remediate** — trigger provenance refresh only if mismatch persists across ≥2 checks OR exceeds threshold, with cooldown/rate-limit + audit log | MEDIUM-HIGH | §14 F5 remediation refinement | T26a landing + T6 operator surface |
| **T27** (P4-new) | SIGN preamble corpus-hygiene gate — Q9 discharge — check Corpus Health Score OR freshness bound OR canonical-summary coverage OR latest-xx99 embed confirmation BEFORE opening SIGN cycle | MEDIUM-HIGH | §14 F3 + §20 close-card gate proposal | D2100.10 verdict = "standing metric" at close card; then implementation post-arc |
| **T28** (P4-new) | Cross-arc governance-drift observation cadence — periodic sweep of canonical summaries for governance-dimension mixed-mode incidents applying P3 §14 F4 disambiguation | LOW-MEDIUM | §14 F8 R4.8 S1899 §142 candidate | Post-arc; candidate for platform-scope observation arc |
| **T29** (P4-new) | Corpus Health Score dashboard implementation | MEDIUM | §14 F3 + D2100.10 verdict | D2100.10 = "standing metric"; T22 metadata contract enables dimensions; T18 axis-scoring populates axes-coverage-ratio dimension |
| **T30** (P4-new, post-Q9 fold) | Behavior substrate coupling observability — **subsumed under T29 Corpus Health Score** unless cross-plane instrumentation surfaces (spans multiple desks/services). If cross-plane: real-time incident detection (event stream from §10.1) OR periodic Corpus Health Score snapshots | LOW (nested under T29) OR MEDIUM (if cross-plane surfaces) | §10.1 event-substrate gap + §13 LOW maturity + Q9 fold reclassification | T29 (default nested); T9 (cascade lifecycle events) from S2101 + T27 gate landing (if cross-plane elevation) |

### 15.3 P4 severity rationale

- **T26 HIGH** — Direct remediation for §14 F5 live incident. Without
  consistency check, KD-5 provenance-index-stale at PROD produces
  silent retrieval-surface disagreement. Elevated because F5 is a
  captured-live incident, not a hypothetical.
- **T27 MEDIUM-HIGH** — SIGN preamble gate operationalizes Q9 from
  parent §5.4. Elevated because §14 F1 KD-3 evidence shows SIGN
  cycles proceed on stale corpus without any gate.
- **T28 LOW-MEDIUM** — Governance-dimension mixed-mode drift is a
  KD-adjacent class; §14 F8 R4.8 evidence is single-instance
  (S1899 §142). Elevate on next cross-arc drift observation.
- **T29 MEDIUM** — Dashboard implementation is downstream of
  D2100.10 verdict. Only elevate to HIGH if standing-metric verdict
  passes at close card.
- **T30 MEDIUM** — Coupling observability is the meta-metric.
  Landing depends on T9 (event stream) which is itself S2101 T9
  inherited debt.

---

## 16. Boundary Violations

**P4-scoped boundary observation.** Cross-reference S2101 §16 + S2103
§16 for inherited boundary posture. P4 identifies two new candidate
violations for §17 integration matrix + close-card discussion.

### 16.1 Retrieval-surface filter divergence — NOT a violation (designed separation)

`search_docs` and `kb_tool.semantic_search` share the same PROD
pgvector but apply different filter chains. This appears to be a
boundary violation on first look (same backing store, different
results) but on inspection is a DESIGNED SEPARATION:

- `search_docs` — docs-scoped retrieval with provenance-index filter
  applied at query time. Consumer: developer askdocs + Rigby docs-
  scoped SIGN preamble.
- `kb_tool.semantic_search` — cross-corpus semantic retrieval with
  optional filter dimensions. Consumer: Rigby cross-corpus SIGN
  preamble + verifier-loop pre-draft.

**Verdict:** NOT a boundary violation. The DIVERGENCE at F5 is a
symptom of KD-5 (provenance-index-stale) at the write-side, not a
violation at the read-side. §14 F5 remediation is T26 auto-trigger
provenance refresh — the RIGHT fix at the RIGHT boundary.

### 16.2 MEMORY.md rules vs formal governance policy — SOFT overlap

MEMORY.md workflow-discipline rules (§11.2) overlap with the S2103
formal framework spec:

- `feedback_docs_pipeline_4_step_cascade` overlaps with S2103 F5
  metadata contract + T24 `retrieval-authority-framework.md`
- `feedback_cascade_pr_must_include_embed_step` overlaps with post-arc
  T25 `docs-ingestion-cascade.md`
- `feedback_docs_cascade_at_every_close` overlaps with S2103 F7
  lifecycle model transitions

**Verdict:** SOFT overlap, not violation. MEMORY.md rules serve a
different function (Chris's per-workflow discipline reinforcement)
than formal spec (governance authoritative reference). Post-arc
coordination — MEMORY.md rules should POINT INTO formal spec once
T23/T24/T25 publish, avoiding duplicate substrate.

### 16.3 Cascade lifecycle-event emission gap — SUBSTRATE-LEVEL

Per §10.1, cascade emits no lifecycle events. This overlaps with
Group 2000+ event architecture. Boundary observation: Group 2100 arc
does not own event-substrate design, but does OWN the cascade-emit
site. Post-arc coordination — S2101 T9 execution should coordinate
with Group 2000+ event-bus schema.

**Verdict:** Substrate-level gap requiring cross-arc coordination.
Not a violation; a coordination-scope observation for xx99 canonical
seam statement.

### 16.4 Retrieval-surface counter consumption gap — SUBSTRATE-LEVEL

Per §9.2, `search_docs` returns counters but no operator surface
consumes them. Overlaps with Group 1700 Observability (delegated
S1304 T6). Boundary observation: Group 2100 arc does not own
observability, but §14 F5 evidences that operator-surface consumption
would have caught the live incident earlier.

**Verdict:** Substrate-level gap requiring cross-arc coordination.
Recommendation: T26 (P4-new) + Group 1700 Observability standing debt
should co-execute post-arc.

---

## 17. Duplicate or Overlapping Systems

**P4 integration matrix across P1-P3 + P4.** Cross-cutting patterns
observed. This section synthesizes cross-child findings that were
independently landed at P1/P2/P3 into one integration view for
§20 lens-question defense.

### 17.1 Integration matrix — P1-P3 findings × P4 observation-shape

| P1-P3 finding | P4 observation delta |
|---------------|----------------------|
| **S2101 F1** `source_type='api'` monoculture | P4 §5 confirms `_derive_source_type` at `content/embeddings.py:45-63` root; ranking cannot use `Document.source` as authority axis (forces reliance on `document_class`/`is_pinned`/`min_session`) |
| **S2101 F2** metadata population asymmetry (24,980 blank) | P4 §14 F2 verifies KD-4 rate; classification: NO MEASURABLE SIGN-EFFECT via similarity scoring but IS retrieval-quality gap at authority-axis layer |
| **S2101 F3** silent-drop pattern at step 1 | P4 §16.3 flags as substrate-level lifecycle-event gap |
| **S2101 F4** `build_docs_provenance` unscheduled | P4 §14 F5 root cause — provenance-index-stale manifests as KD-5 at retrieval-time |
| **S2101 KD-1..KD-6** taxonomy | P4 §14 F1-F5 evidence brief uses this taxonomy directly + adds live F5 KD-5 manifestation |
| **S2102 F1-F3** Chunker A/B/C regimes | P4 §14 F2 R4.1 discharge: correlation MEASURABLE but INSUFFICIENT N — post-arc T16 unblocks |
| **S2102 F4** ingestion cascade Path A vs Path B | P4 §14 F7 R4.5 discharge: HYPOTHETICAL pending T13 execution (PROMOTED per Chris (b)) |
| **S2102 F5-F8** cascade instrumentation gaps | P4 §10.1 event stream inventory + §15.2 T30 debt entry |
| **S2103 F1** 7-axes + meta-rule framework | P4 §14 F6 R4.6 discharge: HYPOTHETICAL pending T18/T19 execution |
| **S2103 F2** 3-part conflict resolution | P4 §17.2 posture register: DESIGN-COMPLETE, execution T19 |
| **S2103 F3** dual-cascade Path B fold | P4 §14 F7: F3 lean (b) PROMOTED R4.5 to run — HYPOTHETICAL pending T13 |
| **S2103 F4** 5-meaning governance disambiguation | P4 §14 F8 R4.8 evidence candidate: S1899 §142 AgentLearningSystem U3 |
| **S2103 F5** D2100.9 hybrid metadata contract | P4 §14 F3 Corpus Health Score dimension 9 (contract population rate) — enabled post-T22 |
| **S2103 F6** two-employee owner-assignment shape | P4 §8.2 respects shape + §8.3 P4-new owner candidates follow |
| **S2103 F7** 5-state lifecycle model | P4 §14 F8 R4.7 HYPOTHETICAL pending T21 execution |
| **S2103 F8** D2100.11 F2 retrofill lean (b) | P4 §14 F1 KD-3 evidence: retrofill + forward-fix bounds historical incidents |

### 17.2 Cross-cutting patterns — three chokepoints

**Pattern 1: Two chunker regimes (Chunker B sync-cascade + Chunker C
async) → post-arc consolidation.** S2102 F1-F3 documented; S2103
T16 chunker_id schema addition + backlog F1 chunker consolidation
recommendation. P4 observation: KD-4 metadata-blank rate (48.2%)
correlates with Chunker B / `ingested_via='sync_docs'` path — this
is the substrate footprint of the regime divergence. Post-arc
resolution unblocks §14 F2 R4.1 chunker correlation observation.

**Pattern 2: Two retrieval surfaces (`search_docs` + `kb_tool`) →
post-arc consistency gate.** §14 F5 live incident is the direct
evidence. Two surfaces backing on the same store, applying divergent
filters, with counter-surface but no consumer. Post-arc T26 + Group
1700 Observability standing debt co-execute to close the gap.

**Pattern 3: Two governance policy substrates (informal MEMORY.md +
formal S2103 spec) → post-arc consolidation discipline.** §16.2
verdict: SOFT overlap, not violation. Post-arc T23/T24/T25 landing
carries the MEMORY.md-points-into-formal-spec transition.

**Pattern 4: Two ownership planes (S2103 F6 two-employee shape vs
cross-arc drift/coordination needs) → orphan-obligation risk unless
provisional steward + escalation path exists.** Post-Rigby SIGN Batch
2 Q8 STRENGTHEN 2026-07-05. §18.1 P4-new ownership candidates follow
the S2103 F6 two-employee shape (Rigby EXECUTE + CoS RECOMMEND);
§18.2 UNASSIGNED cross-arc candidates (T28 cross-arc governance-drift
cadence + T9 cascade lifecycle-event + T6 retrieval-surface counter +
T30 coupling meta-metric) have no owner because they span multiple
arcs. Without a provisional steward + escalation target, cross-arc
drift observations fall on the floor (S2001 F9 orphan-consumer risk
pattern manifest at ownership plane). Distinct from Pattern 3 policy
substrate: this pattern governs **who carries the pager / who writes
the PR** when drift is observed, not what the rule says. §18.2 updated
per Q9 fold to set Provisional Steward = Rigby OBSERVE/RECOMMEND-only
with explicit escalation to Chris / xx99.

### 17.3 Spec-readiness register carry from S2103 §17.1

S2103 §17.1 posture register identified DESIGN-COMPLETE-BUT-NOT-
EXECUTED as the Group 2100 arc close posture. P4 confirms this posture
with observation evidence:

- Spec-completeness: SATISFIED at §13.2 5-of-5 acceptance criteria
- Execution-completeness: BLOCKED on T13/T18/T19/T21/T22 post-arc
  T-slot queue
- Observability-completeness: BLOCKED on T26/T27/T29/T30 P4-scoped
  debt

**Integration insight for §20.** The substrate IS coupled (RAG-quality
DOES affect SIGN-quality qualitatively per §14 F1-F5) but the
substrate is DESIGN-COMPLETE-BUT-NOT-INSTRUMENTED. Lens-question
defense: the corpus IS a design-governed corpus substrate
substrate at the spec layer; execution + observability trail behind.

### 17.4 Governance-dimension posture register carry from S2103 §17.2

S2103 §17.2 identified the 5 governance meanings (ownership /
discipline / enforcement / documentation / policy) with per-axis
posture. P4 observation adds:
- **Ownership dimension** — §8.3 P4-new candidates identified
  (Corpus Health Score, retrieval-surface consistency gate, cross-arc
  governance-drift). All follow S2103 F6 two-employee shape.
- **Discipline dimension** — §14 F1 KD-3 evidence shows discipline
  (cascade PR embed step) is codified in MEMORY.md but not enforced
  at merge time. Post-arc T27 SIGN preamble gate would enforce.
- **Enforcement dimension** — §14 F4 D2100.7 ELEVATE verdict adds
  a provisional-contract-level enforceability. Enforcement lands
  post-arc via T22 + T18/T19.
- **Documentation dimension** — §11.4 informal→formal transition
  observation. Post-arc T23/T24/T25 landing carries.
- **Policy dimension** — Formal S2103 spec covers policy layer;
  MEMORY.md soft-overlaps. §16.2 SOFT-overlap verdict maintains.

---

## 18. Ownership Gaps

**P4 respects S2103 §18 owner-assignment shape** (two-employee: Rigby
EXECUTE + Chief of Staff RECOMMEND, NO new AIEmployee handles). §18
adds P4-scoped ownership candidates for close-card discussion.

### 18.1 P4-new ownership candidates following S2103 F6 shape

| Substrate | Proposed owner shape | Depends on close-card verdict |
|-----------|----------------------|-------------------------------|
| **Corpus Health Score** (implementation + cadence + dashboard) | Rigby EXECUTE (measurement + cadence) + Chief of Staff RECOMMEND (dimension weights + threshold defaults) | D2100.10 = "standing metric" — else Group 2100 arc artifact only |
| **Retrieval-surface consistency gate** (T26 execution) | Rigby EXECUTE (gate wiring at `search_docs` + `kb_tool` handler boundary) + Chief of Staff RECOMMEND (auto-trigger provenance refresh threshold) | Unconditional (T26 is HIGH severity from §15.2) |
| **SIGN preamble corpus-hygiene gate** (T27 execution) | Rigby EXECUTE (preamble check + hygiene score gate) + Chief of Staff RECOMMEND (freshness bound + coverage % + xx99 confirmation logic) | D2100.10 verdict OR ratified Q9 discharge at close card |

### 18.2 P4-new UNASSIGNED candidates for cross-arc resolution

**Post-Rigby SIGN Batch 2 Q9 STRENGTHEN 2026-07-05.** All UNASSIGNED
cross-arc items now get a **Provisional Steward = Rigby
(OBSERVE/RECOMMEND-only)** with explicit **escalation target = Chris
/ xx99** so nothing falls on the floor while awaiting cross-arc
scope. Implementation ownership remains UNASSIGNED pending cross-arc
scope arc. Also per Q9, T30 reclassified as subsumed under T29 unless
cross-plane instrumentation surfaces.

| Substrate | Why UNASSIGNED | Provisional Steward | Cross-arc resolution |
|-----------|----------------|---------------------|----------------------|
| **Cross-arc governance-drift observation cadence** (T28) | Group 2100 arc scope does NOT own cross-arc observation; single-instance evidence (S1899 §142) is not enough to fund an arc | Rigby OBSERVE/RECOMMEND-only; escalation → Chris / xx99 | Candidate for platform-scope observation arc; xx99 §8 T3 tier |
| **Cascade lifecycle-event emission** (T9 inherited from S2101) | Group 2100 arc owns cascade write-site but not event-bus substrate | Rigby OBSERVE/RECOMMEND-only; escalation → Chris / xx99 | Cross-arc coordination with Group 2000+ Event / Integration Architecture (canonical seam statement carry) |
| **Retrieval-surface counter consumption** (T6 inherited from S1304, delegated to Group 1700) | Group 2100 arc owns counter emission but not operator-surface consumption | Rigby OBSERVE/RECOMMEND-only; escalation → Chris / xx99 | Cross-arc coordination with Group 1700 Observability standing debt |
| **Behavior substrate coupling observability meta-metric** (T30) | Per Q9 fold: **subsumed under T29 Corpus Health Score** unless cross-plane instrumentation surfaces (spans multiple desks/services) | Rigby OBSERVE (T29-nested) unless cross-plane; then OBSERVE/RECOMMEND-only + escalation → Chris / xx99 | Absorbed by T29 landing; separate row retained ONLY if cross-plane requirement surfaces |

### 18.3 Ownership rationale — anti-duplication

Per `EMPLOYEE_OS_PRIMITIVES.md` anti-duplication rule + S2103 F6
adopted shape, P4 does NOT propose:
- New `AIEmployee` handles for Corpus Health Score / retrieval
  surface consistency / SIGN preamble gate
- New `JobContract` entries for cross-arc observation
- New admin UIs for any of the above

All P4-new work extends the Rigby EXECUTE + Chief of Staff RECOMMEND
substrate. This preserves the two-employee shape S2103 F6 ratified
and prevents primitive proliferation.

### 18.4 §18 close-card items

Owner assignments requiring Chris ratification at close card:
- CH-A: Corpus Health Score owner shape (conditional on D2100.10)
- CH-B: T26 retrieval-surface consistency gate owner shape
- CH-C: T27 SIGN preamble corpus-hygiene gate owner shape
- CH-D: T28 cross-arc governance-drift observation cadence disposition
  (defer to platform-scope arc? OR bundle into xx99?)

---

## 19. Recommended Future Research

**Ranked by architectural uncertainty × risk × unblocked flows per
playbook §11.2 §19 spec.** Feeds S2199 xx99 §8 T0/Gate + T1 + T2 + T3
tiered queue.

### 19.1 P4 → S2199 xx99 (canonical summary)

- **R99.1 (P4-new) — Canonical seam statement.** xx99 §5 consumes P4
  §14 F1-F5 observation verdicts + §14 F6-F8 HYPOTHETICAL flags + §20
  lens-question defended answer to produce Group 2100 canonical seam
  statement (post-Rigby SIGN Batch 3 Q11 STRENGTHEN 2026-07-05):
  **"Rigby's RAG corpus IS a design-governed corpus substrate
  (spec-complete via P3, evidence-supported via P4, execution-pending
  via post-arc T-slots) — in transition toward runtime-governed
  institutional knowledge layer along the maturity gradient
  passive → spec-complete → execution-complete."**
  - **Methodology seam note per Rigby SIGN Batch 2 Q10 STRENGTHEN
    2026-07-05.** xx99 §5 canonical seam must carry the P4-established
    evidence-brief methodology to prevent future miscounting: **"Evidence-
    brief N counts observed incidents separately from taxonomy frames
    and gated hypotheticals (N_observed vs N_evidence_items)."** This
    prevents downstream arcs from inflating N-counts by mixing observed
    incidents with substrate-baseline / taxonomy / hypothetical items.
    Applies playbook §11.2 §14 F-finding shape going forward.
- **R99.2 (P4-new) — D2100.7 elevation-ratified carry.** xx99 §5
  preserves D2100.7 elevation from hypothesis → provisional contract as
  a canonical arc output.
- **R99.3 (P4-new) — Live incident F5 as archetype.** xx99 §5 preserves
  §14 F5 (search_docs vs kb_tool retrieval disagreement) as the
  archetypal substrate-coupling incident for future arc reference.
- **R99.4 (P4-new) — HYPOTHETICAL findings F6/F7/F8 → post-arc
  observation queue.** xx99 §8 T-slot queue absorbs F6/F7/F8 discharge
  as post-arc observation items once T13/T18/T19/T21/T22 execute.

### 19.2 P4 flags for post-arc observation queue

**Post-arc T-slot additions from §15.2.** Consumed by S2199 xx99 §8
tiered T0/T1/T2/T3 queue for scheduling under Chris D-verdict:

- **T26a (HIGH)** — Retrieval-surface consistency check between
  `search_docs` and `kb_tool.semantic_search` — **Detect-and-Flag**.
  Always-on check; return partial results + explicit warning when
  `excluded_missing_provenance > 0`. Direct §14 F5 remediation.
  Owner: Rigby EXECUTE + CoS RECOMMEND (§18.1). Depends on: T6
  (Group 1700 operator surface, delegated).
- **T26b (MEDIUM-HIGH, post-Q6 fold)** — Retrieval-surface consistency
  **Guarded Auto-Remediate**. Trigger provenance refresh only on
  repeatability (≥2 checks) or threshold + cooldown/rate-limit +
  audit log. Owner: same as T26a. Depends on: T26a landing.
- **T27 (MEDIUM-HIGH)** — SIGN preamble corpus-hygiene gate.
  Discharge Q9 minimum-corpus-hygiene-for-SIGN-trust from parent
  §5.4. Gate check before opening SIGN cycle: (a) Corpus Health
  Score threshold OR (b) freshness bound OR (c) canonical-summary
  coverage % OR (d) latest-xx99 embed confirmation. Owner: Rigby
  EXECUTE + CoS RECOMMEND (§18.1). Depends on: D2100.10 verdict at
  §20.4 close card = "standing metric".
- **T28 (LOW-MEDIUM)** — Cross-arc governance-drift observation
  cadence. §14 F8 R4.8 evidence candidate (S1899 §142). Owner:
  UNASSIGNED (§18.2) — candidate for platform-scope observation arc.
- **T29 (MEDIUM)** — Corpus Health Score dashboard implementation.
  Conditional on D2100.10 verdict = "standing metric". Owner: Rigby
  EXECUTE + CoS RECOMMEND (§18.1). Depends on: T22 metadata contract
  landing + T18 axis-scoring service landing.
- **T30 (MEDIUM)** — Behavior substrate coupling observability meta-
  metric. Depends on: T9 (S2101 inherited cascade lifecycle events)
  + T29 (Corpus Health Score) both landing. Owner: same shape as
  T29.

**Option B controlled-experiment as T-slot.** Detail lands in §20.5
Appendix (harness requirements, metrics, infrastructure investment).
This is the substrate P4 explicitly did NOT run per parent §5.4 W1
reframe. Post-arc T-slot conditional on Chris-verdict at future arc
(NOT this arc's close card).

### 19.3 P4 flags for future non-Group-2100 arcs

**Cross-arc arc candidates surfaced by P4 observation.**

- **Cross-arc governance-drift observation arc.** §14 F8 R4.8 single-
  instance evidence (S1899 §142 AgentLearningSystem U3) is insufficient
  to fund a dedicated arc but IS worth cadence-monitoring. Candidate
  for platform-scope observation arc after ≥3 more instances surface.
  Alternative: bundle into xx99 canonical seam statement as a
  continuous-observation carry-forward (recommendation for xx99 §8 T3
  tier).
- **Cascade lifecycle-event architecture co-execution arc.** S2101 T9
  execution requires event-bus schema coordination with Group 2000+
  Event / Integration Architecture (canonical closed at S2099). Not
  a new arc — cross-arc coordination. Recommend flagging in xx99 §5
  canonical seam statement.
- **Retrieval-surface counter operator-surface arc.** Cross-arc
  coordination with Group 1700 Observability (delegated S1304 T6).
  Not a new arc — cross-arc coordination. Flag in xx99 §5.
- **~~Behavior substrate coupling observability meta-metric arc.~~
  REMOVED per Rigby SIGN Batch 4 Q19 STRENGTHEN 2026-07-05
  consistent with Batch-2 Q9 fold.** T30 subsumed under T29 Corpus
  Health Score (internal sub-dimension), NOT a distinct cross-arc
  dependency. Retain sub-dimension callout in T29 documentation
  unless future work surfaces cross-plane instrumentation requirement
  (spans multiple desks/services). If cross-plane surfaces later,
  reinstate as third cross-arc flag.

### 19.4 P4 handoff summary table

| Handoff | Target | Type | Status |
|---------|--------|------|--------|
| R99.1 | S2199 xx99 §5 | Canonical seam statement | §20.1 defended answer feeds |
| R99.2 | S2199 xx99 §5 | D2100.7 elevation carry | §14 F4 ELEVATE verdict feeds |
| R99.3 | S2199 xx99 §5 | F5 live-incident archetype | §14 F5 verdict feeds |
| R99.4 | S2199 xx99 §8 | F6/F7/F8 HYPOTHETICAL queue | §14 F6/F7/F8 verdicts feed |
| T26a | Post-arc queue | Retrieval-surface consistency **Detect-and-Flag** | §15.2 + §18.1 |
| T26b | Post-arc queue | Retrieval-surface consistency **Guarded Auto-Remediate** | §15.2 + §18.1 (depends on T26a) |
| T27 | Post-arc queue | SIGN preamble corpus-hygiene gate | §15.2 + §18.1 + §20.4 close card CH-C |
| T28 | Non-Group-2100 arc queue | Cross-arc governance-drift cadence | §15.2 + §18.2 + §20.4 close card CH-D |
| T29 | Post-arc queue | Corpus Health Score dashboard — **explicitly includes sub-dimensions (13) cascade reliability/latency + (14) supersession graph integrity** per Rigby SIGN Batch 2 Q10 STRENGTHEN 2026-07-05 (14 dimensions total post-Batch-1 Q4 fold) | §15.2 + §18.1 + §20.4 close card CH-A + §14.3 F3 14-dim list |
| T30 | Post-arc queue | Coupling observability meta-metric | §15.2 + §18.1 |

---

## 20. Appendix

### 20.1 Defended answer to central lens question

**Central lens question (Chris-set 2026-07-04):** *"Is Rigby's RAG
corpus a passive document search index, or is it a governed
institutional knowledge layer that can reliably shape future research,
SIGN cycles, and platform decisions?"*

**P4 defended answer.**

**Rigby's RAG corpus IS a design-governed corpus substrate — spec-
governed at design layer; runtime governance pending.** (Terminology
per Rigby SIGN Batch 3 Q11 STRENGTHEN 2026-07-05 — replaces
"governed institutional knowledge layer" to avoid over-claiming
runtime governance.)

Not "passive search index" AND not "already governed at runtime."
The substrate has crossed the design threshold but has not yet crossed
the execution threshold. **Three-part defense as maturity gradient**
per Q11 STRENGTHEN — the three parts are RANKED, not equal-weighted:

**Part 1 — Spec-completeness (SATISFIED at design layer — FURTHEST
ALONG on maturity gradient).** All 5
institutional-knowledge-layer acceptance criteria per parent §5.1 are
SATISFIED at the design layer (§13.2). Corpus ingestible + retrievable
(Criterion 1) LOCAL 100% embedded. Chunker regime documented
(Criterion 2) via S2102 F1-F3. Metadata contract defined (Criterion
3) via S2103 F5. Lifecycle model defined (Criterion 4) via S2103 F7.
Governance dimensions disambiguated (Criterion 5) via S2103 F4. At
the spec layer, the substrate has all five properties an institutional
knowledge layer requires.

**Part 2 — Evidence-support (SATISFIED via P4 observation — SUFFICIENT
FOR PROMOTION per §14 F4 diversity+actionability criterion).** §14
F1-F5 evidence brief documents N = 14 concrete RAG-quality incidents
including two historical (S1234, S1802) and one live-captured
(§14 F5 search_docs vs kb_tool disagreement). The pattern in the
evidence: RAG-quality gradations observably affect SIGN-quality
gradations. Freshness gaps produce SIGN-blindness (F4 D2100.7
ELEVATE). Cascade-PR-forgot-embed gaps produce degraded pressure-tests
(F1). Provenance-index staleness produces retrieval-surface
disagreement (F5). The coupling is real. The corpus is not passive —
it shapes behavior — and the coupling is directionally consistent with
governed-substrate behavior once execution catches up.

**Part 3 — Execution-pending (BLOCKED on post-arc T-slots — CURRENT
BLOCKER; the load-bearing gap that keeps the maturity gradient from
reaching runtime governance).** The
execution + observability layers trail behind the design layer. §13
maturity table shows HIGH spec-readiness paired with LOW execution +
LOW observability. §14 F6/F7/F8 explicitly HYPOTHETICAL pending
T13/T18/T19/T21/T22 execution. The corpus is a governed institutional
knowledge layer AT SPEC; at runtime it operates on the design contract
with degraded observability. §15.2 T26-T30 debt captures the residual
execution work.

**Verdict caveat.** The passive-vs-governed dichotomy in the lens
question is intentionally rhetorical. The truer form P4 defends —
per Q11 STRENGTHEN — is the transition: **passive → spec-complete
→ execution-complete.** Passive index (pre-Group 2100 arc) →
spec-complete design-governed corpus substrate (post-Group 2100 arc
design) → runtime-governed institutional knowledge layer (post-arc
T-slot execution). This transition posture is the D2100.10 candidate
for canonical seam statement carry-forward. The rhetorical shorthand
"governed institutional knowledge layer" applies fully only at the
runtime-governance endpoint of the transition.

### 20.2 Chris directive coverage matrix

Chris's 10-point framing at parent scoping open + subsequent refinement
across S2100/S2101/S2102/S2103. P4 addresses:

| Point | Covered by | P4 verdict |
|-------|------------|------------|
| **Point 1** — Knowledge Loop conceptual framing | §20.1 Part 1 + §14 F1-F5 | SUBSTRATE CLOSES THE LOOP AT SPEC (execution-pending) |
| **Point 2** — RAG-vs-Memory arc boundary | §9.1 delegated inheritance | Boundary observation from Memory arc PRESERVED; §14 F5 shows arc-boundary interaction at runtime |
| **Point 3** — R→R→K→B (Retrieval → Ranking → Knowledge → Behavior) model | §17.1 integration matrix (P1-P3 findings × P4 delta) | R→R validated at S2101/S2103 spec; K→B validated at §14 F1-F5 observation; model coherence AT SPEC |
| **Point 4** — Doc governance policy (5 dimensions) | §17.4 governance-dimension posture register carry | 5 dimensions all covered; enforcement/discipline dimensions gain P4-observation reinforcement |
| **Point 5** — RAG freshness → SIGN quality (TEST not assume) | §14 F4 D2100.7 ELEVATE verdict | Hypothesis → provisional contract elevation; Option B (quantitative test) parked as post-arc T-slot §20.5 |
| **Point 6** — Corpus Health Score dimension list | §14 F3 (14 dimensions post-Rigby SIGN Batch 1 Q4 fold) | Dimension list ratified; D2100.10 verdict at §20.4 |
| **Point 7** — Retrieval authority framework | §14 F6 (HYPOTHETICAL) + §17.3 spec-readiness | Framework spec-complete; runtime acceptance HYPOTHETICAL pending T18/T19 |
| **Point 8** — Cascade governance (dual-cascade + Path A/B) | §14 F7 (HYPOTHETICAL) | Path B activation observation pending T13 execution |
| **Point 9** — Minimum corpus hygiene for SIGN trust | §14 F3 SIGN preamble additions + T27 gate | Q9 discharge — SIGN preamble gate proposed as T27 |
| **Point 10** — Central lens question | §20.1 defended answer | ANSWERED — **design-governed corpus substrate** (per Q11 fold terminology) AT SPEC layer, in transition toward runtime-governed institutional knowledge layer via post-arc T-slots |

### 20.3 R4.1-R4.8 discharge summary table

| Handoff | Origin | P4 discharge status | Landing section |
|---------|--------|----------------------|-------------------|
| **R4.1** chunker-population correlation | S2101 + S2102 (re-attested) | MEASURABLE-BUT-INSUFFICIENT-N — F2 remains MEDIUM per S2102; post-arc T16 unblocks | §14.2 F2 |
| **R4.2** institutional-knowledge-layer acceptance criteria | S2101 + S2102 (re-attested) + S2103 extended | SATISFIED at design layer (5-of-5 §13.2); execution gated on T22 | §13.2 + §20.1 Part 1 |
| **R4.3** Corpus Health Score dimensions | S2101 + S2102 (re-attested) + S2103 extended | RATIFIED 14 dimensions (12 → 14 post-Rigby SIGN Batch 1 Q4 fold); D2100.10 verdict pending at §20.4 close card | §14.3 F3 + §20.4 CH-A |
| **R4.4** D2100.7 freshness-bound conditional-elevation | S2101 (Q15 SIGN STRENGTHEN) | ELEVATE hypothesis → provisional contract; evidence: S1234 + S1802 + §14 F5 live incident; enforcement hooks: T22 + T18/T19 | §14.4 F4 |
| **R4.5** Path A vs Path B activation observation | S2102 (Q19 conditional-on-F3-choice) | PROMOTED per Chris pick (b) at S2103 close; HYPOTHETICAL pending T13 execution | §14.7 F7 |
| **R4.6** Retrieval-authority framework acceptance | S2103 (P3-new) | HYPOTHETICAL pending T18/T19 execution + T22 metadata contract | §14.6 F6 |
| **R4.7** Artifact lifecycle-transition observation | S2103 (P3-new, gated on T21) | **HYPOTHETICAL (execution-gated)** pending T21 state-machine execution — per Q7 legend | §14.8 F8 (R4.7 half) |
| **R4.8** Governance-dimension mixed-mode observation | S2103 (P3-new, framework methodology) | **EVIDENCE-CANDIDATE (single-instance)** — S1899 §142 first observed instance; needs-repeatability note; T28 cadence observation post-arc — per Q7 legend | §14.8 F8 (R4.8 half) |

**Discharge coverage:** All 5 must-ship (R4.1/R4.2/R4.3/R4.4/R4.6)
discharged. All 3 backlog (R4.5/R4.7/R4.8) landed as HYPOTHETICAL or
EVIDENCE-CANDIDATE with post-arc observation queue.

### 20.4 Close card — 10 items for Chris ratification

**Format.** Each item states the P4 proposal + my lean + Rigby's lean
(populated post-SIGN cycle 1). Chris "agree all" ratifies wholesale
OR item-by-item.

**Item 1 — F4 D2100.7 ELEVATE verdict.**
- Proposal: ELEVATE D2100.7 hypothesis "RAG freshness bounds SIGN
  quality" → provisional contract, with S1234 + S1802 + §14 F5 as
  evidence and T22 + T18/T19 as enforcement hooks.
- Claude lean: (a) ELEVATE.
- Rigby lean: (populated post-SIGN).

**Item 2 — F5 live-incident T26 remediation severity + split.**
- Proposal (post-Rigby SIGN Batch 2 Q6 STRENGTHEN 2026-07-05): T26
  split into **T26a Detect-and-Flag** (HIGH severity — always-on
  consistency check + partial-results-with-warning) and **T26b
  Guarded Auto-Remediate** (MEDIUM-HIGH severity — repeatability-gated
  auto-refresh with cooldown + audit log). Default behavior at T26a
  = return partial results + warning; auto-remediation at T26b is
  gated.
- Claude lean: (a) split T26 into T26a HIGH + T26b MEDIUM-HIGH per
  Rigby SIGN fold.
- Rigby lean: (populated post-SIGN Batch 2 — LANDED via Q6 STRENGTHEN).

**Item 3 — D2100.10 Corpus Health Score standing-metric-vs-arc-
artifact-only verdict.**
- Proposal choices (post-Rigby SIGN Batch 3 Q12 STRENGTHEN 2026-07-05
  — added option (c) phased rollout):
  - **(a)** standing metric with dashboard + cadence + Rigby SIGN
    preamble surface — full 14-dimension implementation up-front;
  - **(b)** Group 2100 arc artifact only — dimensions documented for
    future arcs, no implementation;
  - **(c)** standing metric with **phased rollout** — start with core
    subset (e.g., freshness + coverage + reliability + contract
    population once T22 lands), then expand to full 14 dims post
    T18/T19/T21. Preserves standing-metric posture while avoiding
    all-or-nothing implementation risk as dimensions grow.
- Claude lean (revised post-Q12 fold): **(c) phased rollout** —
  originally leaned (a); post-Batch-1 Q4 fold expanded to 14 dims
  which increases scope. (c) captures the substrate-needs-ongoing-
  observation intent from evidence at §14 F1/F5 while avoiding
  all-or-nothing implementation risk.
- Rigby lean: (populated post-SIGN — Q12 fold established (c) is
  substrate-safe).

**Item 4 — CH-A Corpus Health Score owner shape (conditional on Item
3 = (a)).**
- Proposal: Rigby EXECUTE (measurement + cadence) + Chief of Staff
  RECOMMEND (dimension weights + thresholds).
- Claude lean: (a) two-employee shape per §18.1.
- Rigby lean: (populated post-SIGN).

**Item 5 — CH-B T26 retrieval-surface consistency gate owner shape
(SPLIT post-Q6 T26a/T26b + Q13 fold 2026-07-05).**
- Proposal:
  - **T26a Detect-and-Flag** — Rigby EXECUTE (gate wiring at handler
    boundary + partial-results-with-warning); Chief of Staff
    RECOMMEND (thresholds + guidelines — normal RECOMMEND surface).
  - **T26b Guarded Auto-Remediate** — Rigby EXECUTE wiring, but
    **threshold changes require Chris ratification** (change-control
    gate + audit log + cooldown defaults). Treat T26b as higher-risk
    policy knob, NOT mere guideline. Chief of Staff RECOMMENDs
    initial thresholds; Chris ratifies subsequent changes.
- Claude lean: (a) split owner-shape per Q13 fold — T26a normal
  two-employee; T26b Chris-ratification-gated.
- Rigby lean: (populated post-SIGN — Q13 fold established T26b
  auto-remediate warrants change-control gate).

**Item 6 — CH-C T27 SIGN preamble corpus-hygiene gate owner shape
(CHANGE-CONTROL REFINEMENT post-Rigby SIGN Batch 4 Q16 STRENGTHEN
2026-07-05).**
- Proposal: Rigby EXECUTE (preamble check + gate) + Chief of Staff
  RECOMMEND (freshness bound + coverage % + xx99 confirmation logic
  — proposes threshold adjustments as guidelines).
- **Change-control note (Q16 fold).** Because T27 gates SIGN cycle
  opening, **threshold parameters** (freshness bound days /
  canonical-summary coverage % / xx99 embed confirmation SLA) require
  **Chris ratification for CHANGES** (logged + versioned). Default
  ops: Rigby applies the gate at cycle open; Chief of Staff proposes
  threshold adjustments; Chris ratifies threshold changes. Optional
  time-bounded **emergency override** (TTL + audit trail) to prevent
  deadlock if the gate mis-fires and blocks an urgent cycle.
- Claude lean (revised post-Q16 fold): (a) two-employee shape per
  §18.1 **+ Chris ratification gate on threshold changes** per Q16
  fold — mirrors T26b (Q13) posture for auto-remediation.
- Rigby lean: (populated post-SIGN Batch 4 — Q16 fold established
  change-control gate on threshold changes).

**Item 7 — CH-D T28 cross-arc governance-drift observation cadence
disposition (REFINEMENT post-Rigby SIGN Batch 4 Q17 STRENGTHEN
2026-07-05).**
- Proposal choices: (a) defer T28 to future platform-scope observation
  arc after ≥3 more instances surface; (b) bundle into xx99 canonical
  seam statement as continuous-observation carry-forward; (c) UNASSIGN
  and revisit at next arc.
- **Disposition refinement (Q17 fold).** Choose (b) PLUS add
  **lightweight cadence trigger** consistent with post-Batch-2
  EVIDENCE-CANDIDATE (single-instance) reclassification of F8-R4.8:
  **"At each arc close, sample the last-N canonical summaries for
  governance-dimension mixed-mode drift and record count / notes."**
  Aligns with EVIDENCE-CANDIDATE label by explicitly seeking
  repeatability at low cost without opening a new arc.
- Claude lean (revised post-Q17 fold): (b) bundle into xx99 **+
  lightweight cadence sample at each arc close**. Upgrades disposition
  from wait-for-3-more-incidents → active-seek-repeatability.
- Rigby lean: (populated post-SIGN Batch 4 — Q17 fold established
  lightweight cadence as the correct EVIDENCE-CANDIDATE follow-up).

**Item 8 — §16.2 MEMORY.md-points-into-formal-spec discipline post-
T23/T24/T25 (MECHANISM REFINEMENT post-Rigby SIGN Batch 4 Q18
STRENGTHEN 2026-07-05).**
- Proposal: adopt post-arc discipline that MEMORY.md rules point
  into formal spec once T23/T24/T25 publish, not duplicate content.
- **Mechanism requirement (Q18 fold).** POINT-INTO discipline is not
  reliably achievable without a machine-checkable reference format +
  duplication guard. Add:
  - **Machine-checkable reference format** — MEMORY.md rules post-
    T23/T24/T25 use `SpecRef: docs/.../RAG_CORPUS_GOVERNANCE.md#<anchor> @v<index>`
    (path + section anchor + spec version/date). Enables mechanical
    verification that a rule points into current spec.
  - **No-duplicate lint** — new mgmt command that scans MEMORY.md
    rules for content restating canonical spec text. Initially
    warning-only (soft lint); after ≥1 arc landing, promote to
    fail-on-duplication for new/edited rules (hard lint).
- Claude lean (revised post-Q18 fold): (a) adopt discipline **+
  SpecRef format + no-duplicate lint (soft → hard)** per Q18 fold.
- Rigby lean: (populated post-SIGN Batch 4 — Q18 fold established
  mechanism requirement).

**Item 9 — §19.3 cross-arc coordination flags for xx99 canonical
seam statement (SHRUNK 3 → 2 post-Rigby SIGN Batch 4 Q19 STRENGTHEN
2026-07-05 consistent with Batch-2 Q9 fold subsuming T30 under T29).**
- Proposal: xx99 §5 canonical seam statement carries **2** cross-arc
  coordination flags:
  - (i) cascade lifecycle-event architecture co-execution with
    Group 2000+ Event / Integration Architecture (T9 substrate);
  - (ii) retrieval-surface counter operator-surface with Group 1700
    Observability (T6 substrate).
  - **~~(iii) behavior substrate coupling observability meta-metric~~
    — REMOVED per Q19 fold.** Downgraded to T29 internal sub-dimension
    note (coupling observability lives inside Corpus Health Score
    dashboard scope, not as a distinct cross-arc dependency) unless
    future work proves cross-plane instrumentation requirement.
- Claude lean (revised post-Q19 fold): (a) carry **2 true cross-arc
  flags** per Q19; coupling observability moves to T29 sub-note.
- Rigby lean: (populated post-SIGN Batch 4 — Q19 fold established
  3 → 2 downgrade consistent with Q9 T30 reclassification).

**Item 10 — Option B controlled-experiment parked-vs-scheduled
disposition (REVISIT TRIGGERS ADDED post-Rigby SIGN Batch 4 Q20
STRENGTHEN 2026-07-05).**
- Proposal choices: (a) PARKED as post-arc T-slot §20.5 with harness
  requirements documented; (b) SCHEDULED as a dedicated future Group
  2100+ arc (would require staging pgvector infrastructure investment
  Chris-verdict); (c) DE-SCOPED entirely (rely on structured observation
  going forward).
- **Explicit revisit triggers (Q20 fold — prevents forever-sink
  posture given Batch-3 Q14 increased documented complexity to 6
  harness requirements + 4-6 weeks realistic bound).** Revisit
  Option B PARKED-vs-SCHEDULED disposition if ANY of:
  - **(t1)** D2100.7 provisional contract shows enforcement gaps
    after N ≥ 5 additional attributable incidents that structured
    observation cannot diagnose;
  - **(t2)** Structured observation cannot disambiguate root cause
    for a repeated incident pattern (evidence but no signal on
    causation);
  - **(t3)** T26a/T26b or T27 gating yields repeated false positives
    OR false negatives that structured observation cannot explain.
- Claude lean (revised post-Q20 fold): (a) PARKED **+ explicit
  revisit triggers t1/t2/t3** per Q20 fold. Prevents forever-sink;
  provides forward-visibility.
- Rigby lean: (populated post-SIGN Batch 4 — Q20 fold established
  revisit-triggers as the correct forever-sink guard).

**Chris "agree all" fold pattern.** Precedent from S2101/S2102/S2103
closes. Item-by-item picks override the wholesale "agree all" for any
disagreement. Post-ratification, all 10 items land in §20.7 record.

**Chris ratified "agree all" 2026-07-05 post-Rigby-SIGN-cycle-1-CLEAN.**
All 10 close-card items ACCEPTED wholesale with post-fold picks:
1. F4 D2100.7 ELEVATE — RATIFIED
2. F5 T26 SPLIT (T26a HIGH + T26b MEDIUM-HIGH) — RATIFIED
3. D2100.10 Corpus Health Score = **(c) standing metric with phased
   rollout** — RATIFIED (revised from (a) up-front to (c) phased
   post-Batch-1 Q4 dims 12 → 14 fold and Batch-3 Q12 phased-rollout
   fold)
4. CH-A Corpus Health owner shape = **(a) two-employee** (Rigby
   EXECUTE + CoS RECOMMEND) — RATIFIED
5. CH-B T26 owner shape SPLIT (T26a normal + T26b Chris-ratification-
   gated change-control) — RATIFIED
6. CH-C T27 owner shape = **(a) two-employee + Chris ratification
   on threshold changes + TTL emergency override** — RATIFIED
7. CH-D T28 disposition = **(b) bundle into xx99 + lightweight
   cadence sample at each arc close** — RATIFIED
8. MEMORY.md-points-into-formal-spec = **(a) adopt + SpecRef format
   + no-duplicate lint (soft → hard)** — RATIFIED
9. xx99 cross-arc coordination flags = **2 flags** (cascade lifecycle-
   event + retrieval-surface counter); T30 → T29 sub-note — RATIFIED
10. Option B disposition = **(a) PARKED + revisit triggers t1/t2/t3**
    — RATIFIED

Doc status flipped `draft` → `active` post-ratification. Ready for
arc-close cascade (ARCHITECTURE_INDEX v74 → v75 + OPEN_ARCS Group
2100 In-progress row + 00-START-NEXT-SESSION rewrite for S2199 +
commit + PR + docs cascade + handoff).

### 20.5 Parked Option B controlled-experiment design T-slot detail

**Purpose.** Per parent §5.4 W1 reframe: Option B (controlled
experiment with isolated test corpus) parks as post-arc T-slot. §20.5
documents what harness would be needed if a future arc funds Option B,
so the parked design does not have to be re-derived.

**Harness requirements:**

- **Staging pgvector or in-memory HNSW backing store** — isolated
  from PROD, populated with controlled corpus subsets. Alternatives:
  (a) Docker-composed staging Postgres + pgvector extension;
  (b) `pgvector-lite` in-memory alternative for CI; (c) FAISS index
  as pure-Python HNSW substitute.
- **Defined SIGN-quality metrics** — blinded rubric per pressure-test
  category (STRENGTHEN vs CLEAN vs FOLD vs REJECT distribution;
  citation coverage; finding accuracy against ground-truth judgment).
  Requires reference-set: N ≥ 20 SIGN-cycle-Q-answer pairs with
  human-adjudicated ground truth.
- **Non-live Rigby routing** — dispatch to staging pgvector via
  handler-injection at test-time, NOT via live conversation pin
  routing. Requires `RAG_TEST_BACKEND` env var + handler-level
  test-mode branch.
- **Blinded scoring** — human judges score SIGN outputs without
  seeing which corpus variant produced them. Requires anonymization
  of provenance labels + tool-run output.
- **Controlled corpus variants** — at minimum: (a) fresh baseline;
  (b) stale-by-N-days simulation; (c) partial-unembedded simulation;
  (d) provenance-index-stale simulation. Each variant produces a
  SIGN-quality distribution.
- **Replay + reproducibility logging (added per Rigby SIGN Batch 3
  Q14 STRENGTHEN 2026-07-05).** Persist corpus snapshot hash, query-
  set version, scoring rubric version, random seeds, and full run
  logs so test runs are replayable. Enables cross-run comparison +
  regression detection when future arcs re-run Option B against
  the same reference-set. Critical for auditability of experiment
  results.

**Metrics + expected findings:**

- STRENGTHEN rate delta between fresh baseline and stale-by-N-days
  simulation (expected: stale increases STRENGTHEN rate as Rigby has
  less-authoritative retrieval → more pressure-test asks).
- Citation coverage delta (expected: stale decreases citation count).
- Finding accuracy delta against ground truth (expected: stale
  increases false-negative finding rate).
- Retrieval-surface consistency rate between search_docs and kb_tool
  under provenance-index-stale variant (expected: F5-like disagreement
  rate elevates).

**Infrastructure investment estimate (revised per Rigby SIGN Batch 3
Q14 STRENGTHEN 2026-07-05 — split engineering days from calendar
adjudication time):**
- Staging pgvector: ~2-3 days engineering (Docker + migrations + seed
  data).
- Blinded scoring harness: ~2-3 days scoring UI + anonymization.
- Replay + reproducibility logging: ~1-2 days engineering (snapshot
  hashing + query-set versioning + log persistence).
- **Engineering days total: ~10-15 days for harness infra EXCLUSIVE
  of reference-set curation.**
- **Reference-set curation: Chris-time for N≈20 ground-truth SIGN-Q-
  answer pairs. Potentially 10-20 calendar days depending on rigor
  of adjudication — Q14 fold notes this could dominate calendar
  time if adjudication is careful.** Not measurable in engineering
  days.
- **Overall calendar bound: ~4-6 weeks realistic** (engineering
  parallel + Chris adjudication serial).

**Recommendation posture.** Not recommended for current arc runway.
Structured observation (Option A) per this doc provides qualitative
sufficiency for D2100.7 elevation to provisional contract. Option B
would upgrade provisional → durable contract with quantitative
support. Trigger: if D2100.7 provisional contract shows repeated
enforcement gaps that structured observation cannot diagnose, elevate
Option B to arc-candidate status.

### 20.6 Playbook §11.2 20-section template TWELFTH-consecutive application record

**Application ordering** (11 predecessors + this application):

1. S1301 Memory RAG Retrieval Lanes Audit
2. S1401 Revenue Strategy P1 audit
3. S1501 Sports P1 audit
4. S1601 Content P1 audit
5. S1701 Observability P1 audit
6. S1801 Human Attention P1 audit
7. S1901 Authority Enforcement P1 audit
8. S2001 Event / Integration Architecture P1 audit
9. S2101 RAG Corpus State Reality + Knowledge Gap audit
10. S2102 RAG Ingestion Chunking Embedding Pipeline audit
11. S2103 RAG Retrieval Authority Framework + Corpus Governance Design
12. **S2104 (this doc) — RAG Behavior Substrate Structured Observation + Integration**

**Template compliance verification.** All 20 sections present with
content (post-Pass B/C). §1-§13 domain-orientation content;
§14 findings; §15 debt; §16 boundary violations; §17 duplicate/
overlapping; §18 ownership gaps; §19 recommended future research;
§20 appendix.

**Shape delta from S2103 (design-preparation) → S2104 (observation).**
- §14 findings shift from DESIGN DECISIONS to OBSERVED PATTERNS.
- §15 debt shifts from DESIGN DEBT to OBSERVATION DEBT + inherited-
  reference.
- §17 shifts from spec-readiness register to integration matrix
  synthesizing P1-P3 + P4.
- §20 close card adopts 10-item Chris "agree all" pattern
  established at S2101/S2102/S2103 close.

**Meta-observation.** The template accommodates OBSERVATION shape as
well as it accommodated DESIGN-PREPARATION and DESCRIPTIVE-AUDIT
shapes at S2101/S2102. Per feedback rule §20.7.2 candidate: the
template is shape-agnostic within research-class contracts. This is a
positive meta-methodology finding to carry to playbook v3 §11.2.

### 20.7 Meta-methodology observations per S1399 §10 template

**Per feedback rule** `feedback_xx99_meta_methodology_section` +
Playbook §11.3 §10 template addition adopted S1399 close 2026-07-01,
every canonical summary includes §10 "What This Research Taught Us
About How to Do Research." Child audits also include this record when
patterns worth surfacing emerge. S2104 has three such patterns.

**§20.7.1 What worked.**

- **Live-incident capture during arc open** (§14 F5) — capturing an
  incident that manifested during the incident-enumeration probe
  itself turned into the archetypal evidence for the arc. Discipline:
  read the tool-output verbose block carefully; treat unexpected
  behavior as candidate evidence, not friction to route around.
- **P1-P3 inheritance as evidence base** — P4's observation shape
  did NOT re-run S2101 KD-taxonomy probes or S2102 chunk-distribution
  sampling. Cross-referencing P1-P3 findings + adding delta commentary
  produced a cleaner brief than re-measurement would have. Anti-
  duplication per S1399 §10.3.2.
- **N ≥ 10 evidence-brief threshold with mixed corpus** — 14 incidents
  spanning KD-taxonomy classes + historical + live + hypothetical +
  cross-arc drift gives sufficient breadth without overweighting any
  one class. Q6 SIGN STRENGTHEN 2026-07-04 at S2101 close threshold
  validated.
- **DESIGN-COMPLETE-BUT-NOT-EXECUTED posture as bridging construct**
  — S2103 §17.1 landed this posture; P4 §17.3 confirmed with
  observation. Bridging spec → runtime with an intermediate posture
  category prevented false binary framing.

**§20.7.2 What to codify into playbook v3.**

- **§11.2 20-section template accommodates OBSERVATION shape as well
  as DESIGN-PREPARATION and DESCRIPTIVE-AUDIT shapes.** Adopted
  positive meta-observation. Playbook v3 §11.2 should explicitly
  document that F-findings can be DESIGN DECISIONS or OBSERVED
  PATTERNS depending on child slot category, with template consistent
  across shapes.
- **Live-incident capture during arc-open probes** — playbook v3 §14
  candidate: instrument arc-open probes to explicitly flag
  unexpected-behavior candidates BEFORE proceeding. Formalize the
  discipline that produced F5.
- **P1-P3 inheritance discipline for observation-shape children** —
  playbook v3 §11.2 candidate: observation-shape children explicitly
  cross-reference predecessor F/T findings rather than re-measuring.
  S1399 §10.3.2 anti-pattern extended.

**§20.7.3 Anti-patterns to avoid.**

- **Do NOT re-run S2101 KD-taxonomy ORM probes** — S1399 §10.3.2
  anti-pattern. P4 avoided.
- **Do NOT re-derive Option B experiment design if parked** — §20.5
  documents the harness once so future arcs consulting the parked
  T-slot don't have to re-derive.
- **Do NOT elevate F5 live-incident to arc-blocking** — §14 F5 is
  evidence; T26 is remediation; neither blocks arc close. P4 avoided
  the trap of treating a captured-live incident as an in-arc bug fix.
- **Do NOT let posture register accumulate DESIGN-COMPLETE-BUT-NOT-
  EXECUTED items indefinitely** — S2103 §17.1 register + §20.7.4 xx99
  handoff carry protects against this. Recommendation: track the
  register across arcs to prevent accumulation.
- **Do NOT accept SIGN folds without a cross-reference propagation
  sweep (added per Rigby SIGN Batch 3 Q15 STRENGTHEN 2026-07-05
  — P4-specific anti-pattern).** If a fold changes a metric list,
  dimension count, label legend, or terminology in one section,
  verify every downstream reference (§20.2 point coverage matrix,
  §20.3 discharge summary, §19.4 handoff tables, §14 F-verdicts,
  cross-cutting §17 matrix) is updated the same pass. Batch 1 Q4
  fold updated §14 F3 12→14 dimensions but I had to sweep §20.2
  point 6 + §20.3 R4.3 in a follow-up pass to catch stale "12"
  references. **Mitigation rule: run a "cross-ref sweep" checklist
  step before commit / before batching next SIGN questions.**
  Formalize as part of the SIGN fold-landing discipline going
  forward.

**§20.7.4 Suggestions for the playbook itself.**

- Playbook §11.3 §10 template should include §10.5 "Suggestions for
  future canonical summaries" as OPTIONAL. S2104 (child audit) still
  benefits from populating §20.7.5 despite being not-a-canonical-
  summary; the option should extend to child audits when patterns
  worth carrying forward emerge.
- Playbook §16 arc-standard behavior should document the SIGN pin
  preservation discipline across the arc more explicitly. Group 2100
  arc pin `pa-18b095bb7c4740be` preserved S2100→S2103 across MC-4
  CODIFICATION-CONFIRMED-with-scope-guardrails at S1999 + S2099
  generalization. P4 also preserved. Playbook v3 candidate:
  formalize pin-preservation-across-arc as a checkable §16 rule.
- **Arc pin preservation across child sessions as a CHECKABLE rule
  (§16 candidate, elevated per Rigby SIGN Batch 4 Q20 STRENGTHEN
  2026-07-05).** Group 2100 arc preserved arc pin through 4/4
  shipped children (S2100 parent scoping + S2101 P1 + S2102 P2 +
  S2103 P3 + this S2104 P4). Pattern is now repeated enough — across
  Group 1300 (S1300→S1399 canonical), Group 1400 (S1400→S1499), Group
  1500 (S1500→S1599), Group 1600 (S1600→S1699), Group 1700 (S1700→
  S1799), Group 1800 (S1800→S1899), Group 1900 (S1900→S1999), Group
  2000+ (S2000→S2099), and Group 2100 in-flight — to be codifiable
  as a playbook rule rather than session-open discipline. Candidate
  concrete checks: (a) session-open verifies arc pin matches
  parent-scoping pin; (b) session-close verifies pin is UNCHANGED
  (not rotated) unless MC-4 exception with Chris-verdict; (c)
  ARCHITECTURE_INDEX arc row surfaces pin + preservation-count.
  Recommend for playbook v3 §16 §16.6 checkable-rule addition.

**§20.7.5 Suggestions for future canonical summaries (S2199 xx99).**

- xx99 §5 canonical seam statement should carry the transition
  posture defended at §20.1 — the passive→governed-at-spec→governed-
  at-runtime transition is a durable substrate posture worth preserving
  as a cross-arc reference.
- xx99 §10 meta-methodology observation should include a Group 2100
  running tally: 4-of-4 children applied playbook §11.2 template
  successfully; SIGN cycle 1 CLEAN posture (post-STRENGTHEN folds)
  across all 4; arc-pin preservation across 4 children satisfied.
- xx99 §8 T-slot queue should adopt the two-track dependency
  structure S2103 §19.3 introduced (Track A canonical path / Track
  B schema+enforcement / independent retrofill) — this shape
  clarifies scheduling dependencies better than a flat T-slot list.

### 20.8 Rigby SIGN cycle 1 record

**Cycle 1 status.** Pending (to be routed post-Pass C landing).

**Batching plan.** Per `feedback_rigby_sign_worker_instability_recovery`
+ playbook §15: 4-5 findings per batch, target 20 Qs across 4-5
batches, expect observation-shape to yield cleaner batches than
descriptive-audit or design-preparation shape historically.

**Anticipated batch structure:**
- Batch 1 (Q1-Q5): §1 executive summary + §14 F1 + §14 F2 + §14 F3
- Batch 2 (Q6-Q10): §14 F4 D2100.7 elevation + §14 F5 live incident +
  §17.1-§17.4 integration matrix + §18 owner gaps + §19.4 handoff
  table
- Batch 3 (Q11-Q15): §20.1 defended lens-question answer + §20.2
  Chris directive coverage + §20.3 R4.x discharge + §20.4 close card
  items 1-5
- Batch 4 (Q16-Q20): §20.4 close card items 6-10 + §20.5 Option B
  T-slot detail + §20.6 template application + §20.7 meta-methodology

**Fold discipline.** All STRENGTHEN folds land pre-commit per
S2101/S2102/S2103 pattern. FOLD and CLEAN routed to Chris. REJECT
requires §20.8 record + close-card discussion.

**Cycle 1 Batch 1 (Q1-Q5) result 2026-07-05: CLEAN — 5 STRENGTHEN +
0 CLEAN + 0 FOLD + 0 REJECT.** All 5 STRENGTHEN folds landed pre-
commit at §1 (Q1 N=14 breakdown clarity — N_observed=3 vs N_evidence_items=14),
§14 F1 (Q2 ~24h bound + "RAG blind" precision), §14 F2 (Q3 verdict
softened from "NO MEASURABLE EFFECT" → "NO OBSERVED BASELINE RETRIEVAL
FAILURE + INSUFFICIENT EVIDENCE for higher-order behaviors"), §14 F3
(Q4 Corpus Health Score dimensions 12 → 14 with dedup + additions #13
cascade reliability/latency + #14 supersession graph integrity), §14
F4 (Q5 D2100.7 elevation language tightened — promotion criterion =
incident diversity + actionability, partial enforcement now + full
enforcement post-arc T22/T18/T19).

**Cycle 1 Batch 2 (Q6-Q10) result 2026-07-05: CLEAN — 5 STRENGTHEN +
0 CLEAN + 0 FOLD + 0 REJECT.** All 5 STRENGTHEN folds landed pre-
commit at §14 F5 (Q6 T26 split into T26a Detect-and-Flag + T26b
Guarded Auto-Remediate — repeatability-gated + cooldown + audit log;
default = partial results + warning), §14 preamble legend (Q7 4-label
legend: HYPOTHETICAL execution-gated vs HYPOTHETICAL cadence-gated
vs EVIDENCE-CANDIDATE single-instance vs EVIDENCE-SUPPORTED
repeated-pattern; F8-R4.8 reclassified to EVIDENCE-CANDIDATE),
§17.2 (Q8 added Pattern 4 Ownership substrate split — orphan-obligation
risk without provisional steward), §18.2 (Q9 Provisional Steward =
Rigby OBSERVE/RECOMMEND-only + escalation → Chris/xx99 for all
UNASSIGNED cross-arc items; T30 reclassified as subsumed under T29),
§19.1 R99.1 + §19.4 T29 (Q10 methodology seam note added + T29
explicitly includes 14-dim list with #13 cascade reliability/latency
+ #14 supersession graph integrity).

**Cycle 1 Batch 3 (Q11-Q15) result 2026-07-05: CLEAN — 5 STRENGTHEN +
0 CLEAN + 0 FOLD + 0 REJECT.** All 5 STRENGTHEN folds landed pre-
commit at §20.1 (Q11 terminology "governed institutional knowledge
layer" → "design-governed corpus substrate" + 3-part defense re-
framed as maturity gradient with explicit ranking + transition
posture shorthand passive → spec-complete → execution-complete;
cascade to §17.3 + §19.1 R99.1 canonical seam + §20.2 point 10),
§20.4 Item 3 (Q12 added option (c) phased rollout — start with core
subset post-T22 then expand post-T18/T19/T21; Claude lean revised
from (a) to (c)), §20.4 Item 5 (Q13 split CH-B owner shape into
T26a normal two-employee + T26b Chris-ratification-gated change-
control), §20.5 (Q14 added 6th harness requirement replay +
reproducibility logging + calendar time split engineering vs Chris
adjudication with ~4-6 weeks realistic bound), §20.7.3 (Q15 added
anti-pattern #5 SIGN-fold-cross-reference-propagation-sweep as
P4-specific with concrete mitigation rule).

**Cycle 1 Batch 4 (Q16-Q20) result 2026-07-05: CLEAN — 5 STRENGTHEN +
0 CLEAN + 0 FOLD + 0 REJECT.** All 5 STRENGTHEN folds landed pre-
commit at §20.4 Item 6 (Q16 CH-C T27 threshold-change Chris-
ratification gate + emergency-override TTL), §20.4 Item 7 (Q17 CH-D
T28 disposition (b) bundle-into-xx99 PLUS lightweight cadence sample
at each arc close consistent with EVIDENCE-CANDIDATE F8-R4.8), §20.4
Item 8 (Q18 MEMORY.md-points-into-formal-spec SpecRef format +
no-duplicate lint soft → hard), §20.4 Item 9 + §19.3 (Q19 shrunk
cross-arc coordination flags 3 → 2 by moving T30 coupling observability
to T29 internal sub-note consistent with Q9), §20.4 Item 10 + §20.7.4
(Q20 Option B PARKED + 3 explicit revisit triggers t1/t2/t3 + arc
pin preservation elevated to playbook §16 checkable-rule candidate
with concrete checks).

**Cycle 1 total: CLEAN — 20 STRENGTHEN + 0 CLEAN + 0 FOLD + 0 REJECT
across 4 batches.** All 20 folds landed pre-commit. Pattern matches
S2101 / S2102 / S2103 cycle-1 outcome (each landed 20 STRENGTHEN
clean, no cycle-2 required). This is the FOURTH-consecutive Group
2100 child audit to close SIGN cycle 1 CLEAN with 20 STRENGTHEN +
0 CLEAN + 0 FOLD + 0 REJECT — cycle-2 posture pending Rigby
explicit closure (following S2101/S2102/S2103 precedent).

**Cycle 2 requirement — Rigby explicit closure 2026-07-05: (a)
Cycle 2 NOT required.** Verbatim rationale: *"Batch-1 through Batch-4
pressure tests produced 20 STRENGTHEN folds with no FOLD/REJECT, and
the folds are predominantly precision + change-control + labeling +
de-duplication + ownership/ratification gating — they don't introduce
new untested factual claims, only tighten posture and add explicit
gates (T26 split, T27 threshold ratification, EVIDENCE-CANDIDATE
cadence, Option B revisit triggers, pin-preservation as rule). With
Chris already ratifying the 10-item close card (2026-07-05) and the
cross-ref sweep anti-pattern explicitly addressed, this matches
S2101–S2103 precedent: proceed to arc-close + cascade with arc pin
`pa-18b095bb7c4740be` preserved."* Matches S2101/S2102/S2103
precedent (FOURTH-consecutive Group 2100 child audit with Cycle 2
explicitly closed by Rigby without pressure-test re-run).

**Cycle 1 close-state — CLEAN + Chris "agree all" ratified + Rigby
Cycle 2 explicit closure. Arc pin `pa-18b095bb7c4740be` preserved
through S2104. Ready for arc-close cascade (ARCHITECTURE_INDEX v74 →
v75 with §1.78 S2104 registration + OPEN_ARCS Group 2100 In-progress
row update + 00-START-NEXT-SESSION rewrite for S2199 xx99 canonical
summary + commit + PR + docs cascade + handoff).**

---
title: "Group 1300 Memory / Knowledge / Embeddings — Canonical Summary"
status: active
authority: research
session: 1399
date: 2026-07-01
domain_slug: memory
research_group: 1300
child_slot: P6
category: canonical_summary
parent_doc: docs/research/domains/memory/1300_memory_domain_scoping.md
authors: Claude Code (Chris directed via `start research group 1399` short command 2026-07-01)
sign_status: SIGN-clean (cycle 1, High confidence, 2026-07-01) via fresh isolation pin `pa-4fc3329d0db6484f`; 0 must-fix, 1 optional nice-to-have (docs↔code naming/category drift micro-pattern acknowledged in §4.5 addendum, kept as adjacent evidence rather than promoted to formal cross-cutting pattern to preserve the 4-pattern set named at S1305 close per parent §5 P6 rationale). **Chris commit-gated + merged** 2026-07-01 via PR #2781 = `6318787b`. **Arc closed** — all 13 §12.6 close criteria ticked (original 12 per playbook §17 + 1 new "docs cascade executed" per S1399 close Chris directive; cascade PR #2783 = `956727f3`). **Retrofit update** 2026-07-01: §10 "What This Research Taught Us About How to Do Research" retrofitted per Chris directive; playbook §11.3 template updated same-commit; §10 becomes non-negotiable for future xx99 canonical summaries.
verifier_loop: |
  v0.1 — Bootstrap. Every claim in this summary cites its source
  child audit via `SNNNN §NN.N` anchor. No new grep, no new
  file:line evidence, no re-audit — per playbook §11.3 "the xx99
  summary is bounded work: it consumes P1–P? outputs." Where a
  child audit's evidence itself is F1-CANDIDATE / F4-CANDIDATE,
  this summary preserves the CANDIDATE label rather than
  resolving to CONFIRMED. Severity-correction discipline from
  S1305 §14 D3 also preserved (sibling-inherited context can
  downgrade sub-agent severity claims).

  v0.2 — Rigby launch-call bonus applied (pa-aa54193f240f4846,
  2026-07-01): dead-code claims presented with method + negative-
  evidence standard matching S1302 F1 (whole-tree grep,
  producer/consumer split, doc-vs-code accounting).

  v0.3 — Rigby SIGN cycle 1 (fresh isolation pin
  `pa-4fc3329d0db6484f`, 2026-07-01). Verdict: SIGN-clean, High
  confidence, 0 must-fix. All 4 pressure-test questions PASS:
  Q10 child contradictions resolved (§5.1-§5.5 each anchored to
  child evidence); Q11 anchor-update recommendations complete
  (§7.2.1-§7.2.4 + §7.4.1-§7.4.4 + §7.3 v17→v18 bump plan + OPEN_ARCS
  closure path); Q12 cross-cutting patterns not missed (F1-F4
  multi-child evidence + CANDIDATE vs CONFIRMED discipline
  preserved); Q13 follow-on queue rankings defensible (top 5
  under uncertainty × risk × unblocked flows rubric). One
  nice-to-have flagged: candidate fifth micro-pattern for
  docs↔code naming/category drift spanning S1302 §14 F5
  spider_data_bridge naming + S1302 §14 F6 MemoryPromotionService
  category-assignment drift (+ arguably S1303 §14 F3
  content_writer_agent.py wrong-model+wrong-field). Preserved as
  §4.5 addendum in adjacent-evidence-not-formal-pattern posture —
  Rigby said "not required if you want to keep exactly four,"
  the 4-pattern set was named at S1305 close as the specific
  arc deliverable per parent §5 P6 rationale, and promoting to
  formal cross-cutting F5 would over-index on a within-audit
  pattern that lacks the multi-child evidence threshold F1-F4
  each meet.

  v0.4 — Retrofit (2026-07-01, post-merge). Chris directive: add
  §10 "What This Research Taught Us About How to Do Research" as
  a mandatory section in the playbook §11.3 canonical-summary
  template. S1399 becomes the first application (retrofitted from
  11 sections to 12 sections). Renumbering: former §10 Arc Change
  Log → §11; former §11 Appendix → §12. Load-bearing methodology
  content previously in §10.4 (F1/F4-CANDIDATE + sibling-inheritance
  hypothesis-correction + severity-correction extension) moved
  into new §10.2 "What to codify into playbook v3" with two-triggers
  threshold status per pattern. §11.4 preserved as backwards-compat
  pointer for external references to old §10.4. Playbook §11.3
  template updated same-commit. §12.6 arc close criteria checklist
  updated: original 12 boxes + 1 new "docs cascade executed" box
  = 13 total, all ticked. Memory rules `feedback_xx99_meta_methodology_section.md`
  + `feedback_docs_cascade_at_every_close.md` saved.
supersedes: none
related:
  - docs/research/domains/memory/1300_memory_domain_scoping.md              # parent
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md   # child P1 (Cat D)
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md # child P2 (Cat A+B+C)
  - docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md # child P3 (Cat F)
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md      # child P4 (Cat E↔D)
  - docs/research/domains/memory/1305_memory_runtime_correctness_audit.md    # child P5 (Cat H)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                # §11.3 canonical summary template; §15 Q10-Q13 SIGN
  - docs/research/ARCHITECTURE_INDEX.md                                      # v17 → v18 bump proposed downstream
  - docs/research/OPEN_ARCS.md                                               # Group 1300 row: in-progress → awaiting-summary → closed
  - docs/research/platform_architecture_inventory.md                         # §3.13 / §3.14 update recommendations
  - docs/PLATFORM_INVENTORY.md                                                # runtime anchor (S1399 recommends no direct edits — regenerator wins)
  - docs/PLATFORM_WHAT_IT_IS.md                                              # narrative anchor
  - docs/narratives/KNOWLEDGE_RAG_MEMORY.md                                  # narrative — targeted updates recommended
dependencies_on:
  - S1301 (Cat D findings — RAG retrieval lanes)
  - S1302 (Cat A+B+C findings — persistence architecture)
  - S1303 (Cat F findings — conversational/thread memory; first-inventory landing)
  - S1304 (Cat E↔D findings — docs corpus ↔ RAG boundary)
  - S1305 (Cat H findings — runtime memory correctness)
  - S1300 (parent scoping — §3H open questions closed at S1305; §5 P6 slot deliverables)
delegates_to:
  - Employee OS 1200s arc (Cat G Mission Memory — cross-linked, not folded)
  - Group 1700 Observability (filter-drop telemetry, dead-code / producer-only detection, EventBus adoption for Cat F, worker-recycle instrumentation)
  - post-S1399 design-preparation phase (Cat H remediation per surface; Cat H ↔ Cat B write-authority + TTL policy; turn-context → RAG enrichment intentional-vs-drift decision; write-authority framework ADR)
scope: |
  BOUNDED synthesis of Group 1300 child audit outputs S1301-S1305.
  In scope: cross-cutting pattern identification (F1-F4 named at
    launch); consolidated domain-shape map spanning Cat A/B/C/D/E/F
    (G delegated per parent §3G); resolved contradictions between
    children (S1301 §19 D3 partial invalidation by S1304; provenance-
    systems complementary-not-duplicate reframe; severity-correction
    of Agent 6 CRITICAL claim); unresolved unknowns list; anchor-
    update recommendations for `platform_architecture_inventory.md`
    §3.13/§3.14 + new rows for Cat F + Cat H (per parent §5 P6
    rationale); ranked follow-on research queue; cross-links to
    delegated arcs (Employee OS 1200s Cat G, Group 1700 Observability
    multiple delegations).
  Explicitly OUT: re-audit of any child category; new drift/debt
    findings (would require §13 sweep + §15 SIGN); direct edits to
    `PLATFORM_INVENTORY.md` (regenerable — recommendations only);
    implementation PRs (research library boundary per playbook §14.5);
    Cat G Mission Memory (delegated to Employee OS arc per parent §3G);
    Symbol Mapping / Actor Identity / other non-memory research.
  Anchor edits (INDEX v17 → v18, §3.13 subdivision, new Cat F/H rows)
    are proposed here + APPLIED in the ARCHITECTURE_INDEX v-bump
    commit or subsequent PR, per playbook §16 canonical-summary rule.
non_goals:
  - Runtime code diffs (research boundary)
  - New grep / file:line evidence beyond what children already cite
  - CANDIDATE → CONFIRMED resolutions (preserve child-audit hedges)
  - Re-litigation of Chris-locked decisions D1-D5 (parent §8)
owner: claude (Chris directed via short command; PA continuity via arc pin `pa-aa54193f240f4846`)
---

# Group 1300 Memory / Knowledge / Embeddings — Canonical Summary

> **What this doc is.** The arc-closing xx99 synthesis for Research
> Group 1300 (Memory / Knowledge / Embeddings). It consumes the five
> child audit outputs (S1301 Cat D + S1302 Cat A+B+C + S1303 Cat F +
> S1304 Cat E↔D + S1305 Cat H) and produces the cross-cutting view
> that no single child could deliver: the memory-subsystem shape
> map, the recurring pattern classes, the resolved contradictions
> between siblings, the anchor-update recommendations, and the
> ranked follow-on queue.
>
> **What this doc is not.** A re-audit. Not a new §13 6-parallel-
> Explore sweep. Not a source of new file:line evidence. Every
> load-bearing claim below cites a child-audit §-anchor. Where a
> child hedged (F1-CANDIDATE, F4-CANDIDATE, severity-corrected,
> gap-not-defect), this summary preserves the hedge. Chris's
> S1242 directive + memory rule `feedback_verify_before_deleting_dead_code.md`
> apply.

---

## 1. Executive Summary

**Group 1300 shipped.** Six sessions across 2026-07-01: S1300
parent scoping → S1301 Cat D → S1302 Cat A+B+C → S1303 Cat F →
S1304 Cat E↔D → S1305 Cat H → S1399 this summary. Every child
audit reached SIGN-clean (S1301 in 1 cycle; S1303, S1304, S1305
each in 2 cycles; S1302 in 3 cycles) and merged to `main` (PRs
#2775 + #2776 for S1301, #2777 for S1302, #2778 for S1303, #2779
for S1304, #2780 for S1305). Arc pin `pa-aa54193f240f4846`
carried Group 1300 continuity from S1300 through S1305 and now
into S1399; it retires on arc close.

**What the arc answered.** For the first time, the platform has
a coherent, file:line-cited map of every memory surface:

- **Cat A Semantic Knowledge** — how spider-derived + PA-turn-derived +
  agent-generated knowledge accumulates in `AgentKnowledgeSource` and
  the surrounding write paths (S1302 §4, §5, §7.1).
- **Cat B Personal-Adaptive** — user preferences, `UserAgentLearning`,
  Redis-only `AgentLearningService` state, 14-day freshness window
  (S1302 §4, §5.2, §14.1; S1305 §14 D3).
- **Cat C Agent Working** — Django `AgentMemory` + in-process
  `AgentLearningService.AgentMemory` name collision;
  `MemoryPromotionService` deterministic-regex scoring writing
  `UserMemoryContext` (S1302 §4, §5.1, §14.4, §17.2).
- **Cat D RAG Retrieval Lanes** — LOCAL keyword lane (`core.rag.top_k`
  on `.rag/corpus.jsonl`) vs PROD pgvector lane
  (`core.rag_integration.search_embeddings`); provenance filter on
  LOCAL only (S1301 §5, §7, §14.1; S1304 §7.1).
- **Cat E Documentation Corpus** — 4-step cascade
  (`build_docs_index` → `build_rag_corpus` →
  `sync_docs_index_to_documents` → embed); Documentation Manager
  `AIEmployee` owns steps 1-4 (S1304 §7.2, §18).
- **Cat E↔D boundary** — external `docs/_provenance.json` (git-history-
  derived session origin, LOCAL lane) + row-level
  `DocumentEmbedding.source_type` (source-of-record enum, PROD lane) —
  reframed as **complementary, not duplicate** (S1304 §17); the
  boundary itself is PARTIAL — rebuild cadence unscheduled + LRU
  staleness gap (S1304 §14 D2/D6).
- **Cat F Conversational / Thread Memory** — **first-inventory
  landing.** `ChatConversation` row-per-exchange table +
  `unified_pa_entrypoint.py:7277-7343` turn-history reinject +
  `session_tool.retire` matched-pair enforcement (S1303 §4, §7).
- **Cat H Runtime Memory Correctness** — first mapping of the runtime-
  cache tier: 4 `@lru_cache(1)` sites, 5 production
  `cache.set(timeout=None)` sites, 4-DB Redis topology,
  AgentLearningService within-process consistency gap, MemorySystem
  unbounded index (S1305 §14 D1-D10).

**Cat G Mission / Execution Memory** was delegated to the Employee
OS 1200s arc at parent §3G (Chris-locked D2 2026-07-01) and does
not appear in this summary except by cross-link (§9.1 below).

**Four cross-cutting patterns** were identified at S1305 close and
are formally named in §4 below:

- **F1** — provenance-filter drift class (S1301 §14.2 + S1304 §14
  D2/D6 + S1305 §14 D1).
- **F2** — row-level orphan-write pattern (S1301 §14.3 D3 hypothesis
  + S1302 §14.3 F2 narrowed 11→7 fields + S1304 §14 D3 partial
  invalidation).
- **F3** — Redis-only durability + `@lru_cache` staleness pattern
  (S1302 §14 F4 + §15 T3/T4 + S1304 §14 D2 + S1305 §14 D3/D4/D5/D8).
- **F4** — F1/F4-CANDIDATE discipline as inheritance methodology
  (S1303 §14 F4-CANDIDATE + S1304 §14 D7 F4-CANDIDATE + S1305 §14
  D6 F4-CANDIDATE + S1305 §14 D3 severity-correction extension).

**What remains open** (§6 below):

- Three F4-CANDIDATE claims pending full-tree verification per
  S1303 §14 discipline: `ingested_via` orphan status (S1304 §19
  R1), `context_used` + `agent_results` on `ChatConversation`
  (S1303 §19 R1.a/b/c), `platform_config` LRU on non-setter-routed
  mutation (S1305 §19 R1).
- `MemorySystem` T5 severity assessment blocked on `IntelligentJobMatcher`
  production invocation audit (S1305 §19 R6).
- Turn-context → RAG enrichment: intentional-separation vs drift
  (S1304 §19 R5 — routed to design-preparation phase post-S1399).
- Write-authority framework: no auth gate on `AgentMemory.create_memory`
  (S1302 §15 T10 HIGH — highest debt item in the arc; ADR design
  work routed post-S1399).

**Anchor-update recommendations** (§7 below):

- `platform_architecture_inventory.md` §3.13 subdivision into
  Cat A / B / C sub-rows per S1302 findings.
- `platform_architecture_inventory.md` §3.14 lane consolidation into
  a single lane-selector row per S1301 findings.
- New `platform_architecture_inventory.md` §3.N row for Cat F
  Conversational/Thread Memory (first-inventory landing per S1303).
- New `platform_architecture_inventory.md` §3.N or §5 row for Cat H
  Runtime Memory Correctness (first-inventory landing per S1305).
- `docs/topics/infrastructure.md` doc drift: "3 Redis DBs" → 4 DBs
  with DB-5 `AgentLearningService` rationale (S1305 §14 D9).
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`: (a) resolve F1
  `pa_content_feedback` UNKNOWN → confirmed dead code hint (S1302
  §14.3 F1), (b) update to reference the two-lane split explicitly
  (S1301 §7.1), (c) add pointer to this canonical summary + Cat H
  first-inventory landing (S1305).
- `docs/research/ARCHITECTURE_INDEX.md` v17 → v18: register this
  summary as §1.21; add §8 timeline S1399 row; keep §5 Group 1300
  gap consolidated (arc complete).
- `docs/research/OPEN_ARCS.md`: Group 1300 row moves in-progress →
  awaiting-summary (mid-S1399) → closed (post-Rigby SIGN-clean +
  Chris commit-gate).

**What does NOT change.** No edits to `PLATFORM_INVENTORY.md` (per
CLAUDE.md context-kit rule: it is the runtime anchor, regenerable
via `generate_platform_inventory`). No edits to `PLATFORM_WHAT_IT_IS.md`
narrative anchor from this summary directly (proposed edits ride
in a subsequent PR after regenerator refresh). No implementation
PRs (research boundary per playbook §14.5).

**Ratification path.** Route this summary to Rigby with the full
SIGN + playbook §15 Q10-Q13 canonical-summary pressure-test
questions on a fresh isolation pin (Rigby offered to spin up
one). Chris commit-gate follows per playbook §16.

---

## 2. What This Arc Answered

Per-child rollup of the 28 canonical questions (playbook §9). Each
row cites the child audit's §-anchor and gives the one-line answer.
Only material differences from the child audit's own executive
summary are surfaced.

### 2.1 S1301 — Cat D RAG Retrieval Lanes (§1.16)

| # | Canonical question | S1301 answer | Anchor |
|---|-------------------|--------------|--------|
| Q1 | Domain purpose | Retrieve semantically-relevant chunks for LLM prompt construction | §2 |
| Q3-Q6 | Entry points / models / services | LOCAL `core.rag.top_k`; PROD `rag_integration.search_embeddings`; `search_docs` LOCAL-only; `kb_tool semantic_search` PROD-only | §3, §4, §5 |
| Q11-Q13 | Runtime flows | Two lanes, no runtime selector; `search_docs` hardcodes LOCAL at `td_handlers_ops.py:5502`; PA turn does NOT auto-invoke RAG | §7 |
| Q23 | Known drift | 21.5% provenance-index UNKNOWN gap; `@lru_cache(1)` per-process staleness; two provenance systems no bridge | §14.1, §14.3 D1-D6 |
| Q26 | Technical debt | T7 two-lane selector never built (HIGH); T2 LRU cache manual invalidation (HIGH) | §15 |
| Q28 | Follow-on | S1302 owns row-level provenance; S1304 owns E↔D handoff; Group 1700 owns filter-drop telemetry | §19 |

### 2.2 S1302 — Cat A+B+C Memory Persistence Architecture (§1.17)

| # | Canonical question | S1302 answer | Anchor |
|---|-------------------|--------------|--------|
| Q3-Q6 | Models | Cat A `AgentKnowledgeSource`; Cat B `UserAgentLearning` + Redis; Cat C `AgentMemory` (Django + in-process name collision) + `UserMemoryContext` | §4 |
| Q11-Q13 | Runtime flows | Spider→bridge→knowledge write; PA turn→memory scoring→UserMemoryContext write | §7 |
| Q23 | Known drift | F1 `pa_content_feedback` CONFIRMED DEAD CODE (1 producer, 0 consumers, 14 doc refs); F2 orphan-write pattern narrowed 11→7 fields across 3 SIGN cycles; F5 `spider_data_bridge` docs_stale (writes Cat B not Cat A); F6 `MemoryPromotionService` category-assignment drift | §14.3 F1-F6 |
| Q26 | Technical debt | T10 HIGH: no write authority gate on `AgentMemory.create_memory`; T3 Redis-only `AgentLearningService` | §15 |
| Q28 | Follow-on | S1303 owns Cat F; S1304 owns E↔D; Group 1700 owns dead-code detection; S1399 owns row-level orphan pattern classification + write-authority framework anchor | §19 |

### 2.3 S1303 — Cat F Conversational / Thread Memory (§1.18)

| # | Canonical question | S1303 answer | Anchor |
|---|-------------------|--------------|--------|
| Q3-Q6 | Models | `ChatConversation` at `models/conversations/models.py:59-187` — row-per-exchange table; `conversation_id` = `pa-<uuid.hex[:16]>` pin | §4 |
| Q11-Q13 | Runtime flows | Turn-history reinject at `unified_pa_entrypoint.py:7277-7343`; retire at `td_handlers_core.py:4011-4072`; dispatcher gate at `conversation_action_dispatcher.py:288-316` | §7 |
| Q23 | Known drift | F1 stale-thread waste CONFIRMED RECONCILED via S1248 matched-pair fix; F3 wrong-model+wrong-field at `content_writer_agent.py:76 + :370` (import fix alone shifts crash from import-time to query-time FieldError); F4 `context_used`+`agent_results` CANDIDATE (not proven dead per memory rule `feedback_verify_before_deleting_dead_code.md`) | §14 F1-F10 |
| Q26 | Technical debt | D1 widened to wrong-model+wrong-field; D5 two session-identity mint paths coexist | §15 |
| Q28 | Follow-on | R1 split R1.a/R1.b/R1.c (owner-model-qualified inventory / runtime-vs-analytics-vs-UI classification / canonical-source-of-truth resolution) — highest priority | §19 R1 |

### 2.4 S1304 — Cat E↔D Documentation Corpus ↔ RAG Boundary (§1.19)

| # | Canonical question | S1304 answer | Anchor |
|---|-------------------|--------------|--------|
| Q11-Q13 | Runtime flows | 4-step cascade in `refresh_docs_corpus` at `core/tasks.py:5803` (daily 04:00 Denver via `core/celery.py:495-499`); `build_docs_provenance` NOT in cascade | §7.2 |
| Q23 | Known drift | D1 21.5% corpus-completeness gap (S1301 inherited); D2 `@lru_cache(1)` staleness HIGH; **D3 partial invalidation of S1301 §19 D3** — `source_type` HAS owner-model-qualified consumer at `content/embeddings.py:965-973`; only `ingested_via` remains F1-CANDIDATE; D6 HIGH `build_docs_provenance` unscheduled | §14 D1-D8 |
| Q17 | Boundary ownership | Documentation Manager `AIEmployee` at `core/employees/jobs.py:187-395` owns cascade steps 1-4; four boundary-maintenance responsibilities remain no-explicit-owner | §18 |
| Q26 | Technical debt | T1 provenance-index rebuild cadence unmanaged HIGH; T2 LRU staleness HIGH; T3 two provenance systems complementary-not-duplicate (reframed from S1302 §17.3 duplicate framing) | §15, §17 |
| Q28 | Follow-on | R1 `ingested_via` full-tree recheck HIGHEST; R5 turn-context → RAG enrichment design-preparation | §19 |

### 2.5 S1305 — Cat H Runtime Memory Correctness (§1.20)

| # | Canonical question | S1305 answer | Anchor |
|---|-------------------|--------------|--------|
| Q3-Q6 | Entry points / cache surfaces | 4 `@lru_cache(maxsize=1)` sites in `core/services/`: `_load_provenance_docs` at `td_handlers_ops.py:78`, `_cached_primary_workspace_id` at `platform_config.py:89`, `_cached_primary_user_id` at `platform_config.py:133`, `_load_config` at `fleet_routing.py:64` | §3 |
| Q11-Q13 | Runtime flows | `AgentLearningService.get_user_memory:415` short-circuits to `_user_memories[key]` before Redis; `save_memory:476` writes Redis but never clears dict — within-process consistency gap | §7.2 |
| Q23 | Known drift | D1 LRU staleness (S1304 inherited); D2 `build_docs_provenance` unscheduled (S1304 inherited); D3 Redis-only durability MEDIUM (S1302 inherited; verifier-loop DOWNGRADED from Agent 6 CRITICAL via Redis AOF context); D4 `_user_memories` divergence; D5 MemorySystem unbounded `timeout=None`; D6 platform_config F4-CANDIDATE; D8 4-DB Redis topology; D9 doc-drift (3 vs 4 DBs); D10 5 production `cache.set(timeout=None)` sites | §14 D1-D10 |
| Q26 | Technical debt | T1+T2 as pair (S1304 inherited) highest-severity Cat H items; T5 MemorySystem unbounded pending R6 severity assessment | §15 |
| Q28 | Follow-on | R1 platform_config F4-CANDIDATE HIGH; R2 remediation design-preparation per surface post-S1399; R4 Cat H↔B integration lens (fixes T3+T4+T7 together); R6 IntelligentJobMatcher production invocation audit | §19 |

**Parent §3H open questions closed at S1305 close** (per handoff
frontmatter): (i) `search_docs` has NO dedicated LRU (only
`_load_provenance_docs` called from it); (ii) `MemoryPromotionService`
has NO runtime cache surface (pure DB I/O); (iii) `MemorySystem` IS
active use CONFIRMED via `ai_core/agents/intelligent_job_matcher.py:57`.

---

## 3. Consolidated Domain Shape

The reader's mental model of the entire memory subsystem as it
exists in the platform 2026-07-01, drawn as a single map. This is
what a Staff Engineer opening the repo should be able to build
from this doc alone.

### 3.1 Category matrix (rows × columns)

| Category | Purpose | Primary store | Durability | Write path | Read path | Maturity | Load-bearing drift | Owner |
|----------|---------|---------------|------------|------------|-----------|----------|-------------------|-------|
| **A Semantic Knowledge** | Long-lived knowledge accumulated from spiders + agents | `AgentKnowledgeSource` (Django + pgvector `.embedding`) | Postgres durable + nullable embedding | Spider bridges, agent generation, PA turn contributions | Embedding search, direct ORM in tasks | PARTIAL | No versioning; nullable-embedding silent miss (S1302 §14.1) | S1302 P2 |
| **B Personal-Adaptive** | User preferences + adaptive learning | `UserAgentLearning` (Postgres) + `AgentLearningService._user_memories` (in-process) + Redis DB 5 | Postgres durable; Redis-only for adaptive state (AOF-persisted) | `spider_data_bridge` at `:240`; `AgentLearningService.save_memory:476` | ORM filter on `learning_source`; `get_user_memory:415` (in-process dict first) | PARTIAL | 14-day freshness hardcoded (S1302 §14.1); within-process gap (S1305 §14 D4) | S1302 P2 |
| **C Agent Working** | Per-agent memory (short + working) | Django `AgentMemory` + in-process `AgentLearningService.AgentMemory` (name collision, S1302 §17.2) + `UserMemoryContext` | Postgres durable + Redis in-process | `MemoryPromotionService` deterministic-regex scoring at `:119-172` writes `UserMemoryContext:303-318` | Memory Palace `views_memory_palace.py:60`; `record_access` at `:11000-11001` | EXPERIMENTAL (downgraded — F1 dead-code loop) | F1 `pa_content_feedback` CONFIRMED DEAD (S1302 §14.3); T10 no write authority gate HIGH (S1302 §15) | S1302 P2 |
| **D RAG Retrieval Lanes** | Semantic retrieval for LLM prompts | 2 lanes: LOCAL `.rag/corpus.jsonl` + PROD `DocumentEmbedding` (pgvector) | LOCAL file; PROD Postgres | Cascade populates via `sync_docs_index_to_documents` (Cat E→D handoff) | `top_k` LOCAL + `search_embeddings` PROD; NO runtime selector | WORKING (dropped from STABLE by S1301 due to corpus gap) | 21.5% UNKNOWN gap (S1301 §14.2); no 2-lane selector (S1301 §14.3 D6) | S1301 P1 |
| **E Documentation Corpus** | Source docs + ingestion cascade | Filesystem `docs/**/*.md` + `.rag/corpus.jsonl` + `docs/_provenance.json` + `Document` table | Filesystem + Postgres | 4-step cascade in `refresh_docs_corpus:5803` (daily 04:00) | Read by `search_docs` + `kb_tool` | PARTIAL | `build_docs_provenance` NOT in beat cascade (S1304 §14 D6 HIGH) | Documentation Manager `AIEmployee` (`core/employees/jobs.py:187-395`) |
| **E↔D boundary** | Docs-to-retrieval handoff (governance) | `docs/_provenance.json` external + `DocumentEmbedding.source_type` / `.ingested_via` row-level | External JSON + Postgres | Cascade + `build_docs_provenance` manual | LOCAL filter reads external; PROD reads `source_type` | PARTIAL | LRU staleness on external index (S1304 §14 D2); `ingested_via` F1-CANDIDATE (S1304 §14 D7) | Documentation Manager (cascade); 4 boundary responsibilities remain no-explicit-owner (S1304 §18) |
| **F Conversational / Thread Memory** | Turn-history + session identity | `ChatConversation` row-per-exchange at `models/conversations/models.py:59-187` | Postgres durable | PA turn dispatcher; `session_tool.retire` marker | Reinject at `unified_pa_entrypoint.py:7277-7343`; dispatcher gate | WORKING (bounded); PARTIAL on lifecycle hygiene, analytics, hard enforcement | F3 wrong-model+wrong-field at `content_writer_agent.py:76+:370` (S1303 §14 F3); F9 no auto-cleanup for retired rows | S1303 P3 |
| **G Mission / Execution Memory** | Mission run traces + tool call audit | `OpsRun(domain='mission')` + `OpsRunEvent` + `ToolCallRecord` | Postgres durable | `MissionRunner` + tool dispatchers | Audit dashboards, downstream analytics | **DELEGATED** — not this arc | *(Employee OS 1200s arc owns)* | Employee OS 1200s arc |
| **H Runtime Memory Correctness** | In-process caches + cache-set discipline | 4 `@lru_cache(1)` sites + 5 `cache.set(timeout=None)` sites | In-process (no durability) + Redis DB 1/2/3/5 disjoint | Setters or `clear_config_cache()` (only `platform_config` pair has explicit contract) | Direct access via cached function | WORKING with drift | LRU staleness (S1305 §14 D1); within-process gap in `AgentLearningService` (D4); MemorySystem unbounded (D5); 4-DB topology (D8) | S1305 P5 |

### 3.2 Redis 4-DB topology (S1305 §14 D8)

| DB | Purpose | Backend | Consumers | Isolation risk |
|----|---------|---------|-----------|----------------|
| 1 | Django cache framework | `RedisCache` (settings.py:452 `BACKEND`) at `LOCATION=REDIS_URL` | `django.core.cache.cache.*` callers | Ops `cache.clear()` affects DB 1 only |
| 2 | Celery broker | `settings.py:802` | Celery task queue | — |
| 3 | Celery results | `settings.py:803` | Celery result backend | — |
| 5 | `AgentLearningService` | Raw `redis.Redis(**config)` at `agent_learning_service.py:160`, DB hardcoded at `:145` | `AgentLearningService.save_memory:476` via `hset`; `get_user_memory:415` | **INVISIBLE to Django `cache.clear()`** — cross-DB flush requires explicit `redis-cli -n 5 FLUSHDB` |

Documentation drift: `docs/topics/infrastructure.md` says "3 DBs";
actual is 4 (S1305 §14 D9).

### 3.3 Two provenance systems, complementary-not-duplicate (S1304 §17)

S1302 §17.3 originally framed the row-level `DocumentEmbedding.source_type`
+ `.ingested_via` fields alongside the external `docs/_provenance.json`
as a "duplicate systems" name-collision-methodology case. S1304
verifier-loop reframed via direct file:line evidence:

| System | Encodes | Populated by | Consumed by | Lane |
|--------|---------|--------------|-------------|------|
| External `docs/_provenance.json` | Session origin (git-history-derived) | `build_docs_provenance` mgmt command (manual-only — S1304 §14 D6) | LOCAL keyword filter `_filter_chunks_by_originating_session` at `td_handlers_ops.py:82-127` via `@lru_cache(1)` `_load_provenance_docs` at `:78` | **LOCAL** |
| Row-level `DocumentEmbedding.source_type` | Source-of-record enum (internal / user_upload / web / spider / api) | Ingestion cascade at `content/embeddings.py:654, :753` + `sync_docs_index_to_documents.py:394` + `core/tasks_agents.py:4223/4290/4351` | `semantic_search_sync` at `content/embeddings.py:965-973` `.filter(source_type__in=[...])` + `:1007` presentation | **PROD pgvector** |
| Row-level `DocumentEmbedding.ingested_via` | Ingestion source tag (`sync_docs` / `backfill` / `unknown`) | Same as `source_type` write sites | **F1-CANDIDATE** — no owner-model-qualified consumer (S1304 §14 D7); pending §19 R1 full-tree recheck | (design-decision open) |

S1304 fold #4 guardrail: "complementary today does not imply
optimal" — unification vs explicit-scoping is an open design
decision routed to S1304 §19 R2 and this summary §8 below.

### 3.4 Two RAG lanes, no runtime selector (S1301 §7.1)

```
                           ┌──── LOCAL keyword lane ────┐
                           │                             │
search_docs (PA tool) ──► core.rag.top_k                 │
                           │ reads .rag/corpus.jsonl     │
                           │ + provenance filter via     │
                           │ external docs/_provenance.  │
                           │   json (LRU-cached)         │
                           └─────────────────────────────┘

                           ┌──── PROD pgvector lane ────┐
                           │                             │
kb_tool semantic_search ──► core.rag_integration        │
                           │   .search_embeddings        │
                           │   → DocumentEmbedding       │
                           │   .filter(source_type)      │
                           │   HNSW index                │
                           └─────────────────────────────┘

                           NO RUNTIME LANE SELECTOR
                           (S1301 §14.3 D6 — never implemented)
```

PA turn enrichment does NOT auto-invoke either lane — retrieval is
tool-call-only (S1301 §7.2; S1304 verifier grep confirmed 0
matches for `search_docs|kb_tool|semantic_search|search_embeddings`
in `unified_pa_entrypoint.py`).

### 3.5 4 `@lru_cache(1)` sites (S1305 §14 D7)

| Site | File:line | Invalidation contract | Consumer surface | Risk class |
|------|-----------|-----------------------|------------------|------------|
| `_load_provenance_docs` | `td_handlers_ops.py:78` | **NONE** — worker-restart discipline only | `search_docs` LOCAL keyword filter | HIGH (S1304 §14 D2 — canonical E→D staleness) |
| `_cached_primary_workspace_id` | `platform_config.py:89` | `clear_config_cache()` at `:223` invoked from setters at `:252, :269` | Config lookups | LOW-MEDIUM (F4-CANDIDATE per S1305 §14 D6 — pending §19 R1 for admin/raw-ORM paths) |
| `_cached_primary_user_id` | `platform_config.py:133` | Same as above | Same as above | Same as above |
| `_load_config` | `fleet_routing.py:64` | **NONE** — deploy-restart contract only | Fleet routing lookups | LOW (S1305 §15 T11) |

### 3.6 Load-bearing consequence table

If a reader takes only one thing from this map:

| Surface | If X happens, Y silently ships wrong | Anchor |
|---------|--------------------------------------|--------|
| LOCAL keyword lane | `build_docs_provenance` not run recently → workers serve stale filter → `excluded_missing_provenance` counter fires → operator sees "0 results" without any log/metric/alert | S1301 §14.1, §14.2; S1304 §14 D2/D6 |
| PROD pgvector lane | `ingested_via` future consumer added without §19 R1 verification → deprecates a field that turns out to be design-preserved for a downstream project | S1304 §14 D7; §19 R1 |
| Cat B AgentLearningService | Redis-only for adaptive state; **within-process** `_user_memories` never invalidated after `save_memory:476` — same-process subsequent `get_user_memory:415` returns pre-save entry | S1305 §14 D4 |
| Cat C AgentMemory | No write authority gate — any PA turn can call `create_memory` at `:11004` (T10 HIGH) | S1302 §15 T10 |
| Cat C `MemoryPromotionService` | Auto-saves on every PA turn without rate limiting; scoring thresholds hardcoded at `:234, :237` | S1302 §14.1, §15 T6 |
| Cat F ChatConversation | `content_writer_agent.py:76 + :370` wrong-model+wrong-field — soft-fails at import today; if the import gets fixed without the field realignment, crash flips from import-time to query-time FieldError | S1303 §14 F3 |
| Cat H MemorySystem | `timeout=None` on index + data at `core/memory_system.py:54-55, :176` under `REDIS_MAXMEMORY_POLICY='allkeys-lru'` → LRU eviction produces index-that-references-evicted-data → silent None return | S1305 §14 D5 |
| Cat H 4-DB topology | Ops runs Django `cache.clear()` expecting to reset "all Redis state" → DB 5 `AgentLearningService` state survives untouched | S1305 §14 D8 |

---

## 4. Cross-Cutting Patterns

Themes visible only across multiple children. These are the arc's
load-bearing intellectual product beyond any single child's finding.
Named at S1305 close (parent §5 P6 deliverable (b)).

### 4.1 F1 — Provenance-filter drift class

**Definition.** A retrieval filter mechanism that is complete and
correct in isolation, but whose data-model precondition (external
index, cached in-process, populated by an unscheduled command) has
coverage gaps or staleness that produce silent-zero-result queries
to callers who cannot distinguish "no matches exist" from "matches
exist but were filtered out."

**Evidence across children:**

| Child | Evidence | Anchor |
|-------|----------|--------|
| S1301 | 21.5% UNKNOWN in `docs/_provenance.json._meta.confidence_breakdown` (464 / 2156 docs); filter "exclude when missing" by design per Rigby S1145 P2 spec; response counters `excluded_missing_provenance` / `excluded_mismatch` / `pre_filter_count` visible only in payload — no log / metric / alert | §14.1, §14.2 |
| S1304 | `build_docs_provenance` NOT in `refresh_docs_corpus` beat cascade at `core/celery.py:495-499` / `core/tasks.py:5900-5902`; manual-only rebuild; combined with S1301 → canonical E→D synchronization drift | §14 D6 (HIGH) |
| S1305 | `@lru_cache(1)` at `td_handlers_ops.py:78` on `_load_provenance_docs` — no invalidation mechanism; extends the class from a single filter cache to the general LRU-invalidation-vs-worker-restart gap | §14 D1 (HIGH), §14 D7 |

**Cross-cutting nature.** F1 spans three children with three
distinct file:line surfaces (external JSON, beat cascade, in-process
LRU cache). It is not a single-file bug; it is a class of drift
that reappears wherever cached-state-refresh-cadence-is-implicit
meets exclude-by-default-on-missing-metadata.

**Downstream routing.** Filter-drop telemetry is delegated to Group
1700 Observability (S1301 §19.2, S1304 §19 R7). Cache-invalidation
design-preparation per surface is routed post-S1399 (S1305 §19 R2).

### 4.2 F2 — Row-level orphan-write pattern

**Definition.** Model fields populated at write time by a producer
path but never consumed by an owner-model-qualified reader. Symptoms
include populated-but-unread audit fields, provenance markers
without lookup, and feedback loops with producer-only wiring.

**Evolution across children.**

| Session | Claim | Fold history | Anchor |
|---------|-------|--------------|--------|
| S1301 §19 D3 hypothesis | `DocumentEmbedding.source_type` + `ingested_via` both orphan | Broad claim, not verifier-loop-tested at issue | S1301 §14.3 D3 |
| S1302 F2 | 11 fields → 7 fields after Rigby SIGN cycle 1 grep-verification (`AgentKnowledgeSource.source_spider_names` / `.first_discovered_at` / `.feedback_adjusted_confidence` all had qualified consumers) → further narrowed cycle 2 (`AgentMemory.source_type` / `.source_id` / `.access_count` / `.last_accessed_at` consumed by Memory Palace at `views_memory_palace.py:60/:86/:113-114`) → cycle 3 reclassified `AgentMemory.poison_risk_score` + `.poison_risk_factors` as narrow-consumer-safety-filter via `memory_embedding_service.py:222, :261` | Final: 5 strict-orphan + 2 narrow-consumer-safety-filter (S1302 §14.3 F2) | S1302 §14.3 F2 |
| S1304 D3 partial invalidation | `DocumentEmbedding.source_type` HAS owner-model-qualified consumer at `content/embeddings.py:965-973` — S1301 §19 D3 hypothesis broadly overreached | Only `ingested_via` remains F1-CANDIDATE (S1304 §14 D7) | S1304 §14 D3, §14 D7 |
| S1303 F4 | `ChatConversation.context_used` + `.agent_results` — Agent 6 keyword-grep matched unrelated variables (`tasks_agents.py:1262`); downgraded from "confirmed dead" to CANDIDATE | Awaiting R1.a/R1.b/R1.c per S1303 §19 | S1303 §14 F4 |

**Load-bearing methodology.** The pattern's narrowing across
children is itself the arc's methodological output: (a) keyword
grep is insufficient; owner-model-qualified consumer inventory is
required; (b) parent-agent verifier-loop should downgrade broad
hypotheses BEFORE Rigby SIGN, not after; (c) any child receiving
a broad hypothesis from a sibling MUST test it via direct file:line
read on the receiving side. This methodology is folded into F4
below as an inheritance rule.

### 4.3 F3 — Redis-only durability + `@lru_cache` staleness pattern

**Definition.** State surfaces that treat Redis (or in-process
memoization) as the authoritative store, without formal durability
policy or staleness-detection mechanism. Loss / drift is silent
because there is no observability surface.

**Evidence across children:**

| Surface | Class | Anchor | Severity |
|---------|-------|--------|----------|
| `AgentLearningService` Redis-only Cat B state | Redis DB 5 authoritative; no DB writeback; Redis AOF preserves cross-restart (`settings.py:944 REDIS_APPENDONLY=True` + `:945 REDIS_APPENDFSYNC='everysec'`) | S1302 §14.1 (`agent_learning_service.py:462-483`); S1305 §14 D3 | MEDIUM (verifier-loop DOWNGRADED from Agent 6 CRITICAL claim per Redis AOF context — matches S1302 T3 sibling classification) |
| `AgentLearningService._user_memories` in-process consistency gap | `get_user_memory:415` short-circuits before Redis; `save_memory:476` writes Redis but never clears dict | S1305 §14 D4 | MEDIUM |
| `MemorySystem` unbounded `timeout=None` | Index at `:54-55`; data at `:176`; under `REDIS_MAXMEMORY_POLICY='allkeys-lru'` (settings.py:942) → index-references-evicted-data risk | S1305 §14 D5 | MEDIUM (pending R6 severity assessment on `IntelligentJobMatcher` production invocation) |
| `_load_provenance_docs` LRU staleness (Cat E→D) | No invalidation; worker-restart discipline | S1301 §14 D1; S1304 §14 D2; S1305 §14 D7 | HIGH |
| 4-DB Redis topology (Django DB 1 vs `AgentLearningService` DB 5) | `django.core.cache.cache.clear()` invisible to DB 5 | S1305 §14 D8 | MEDIUM (isolation-visibility) |
| `EmbeddingService` 7-day Redis TTL | Deterministic bounded contract | S1305 §14 (implicit — STABLE surface) | STABLE |

**Cross-cutting nature.** F3 spans Cat B (in-process + Redis-only
durability), Cat H (LRU staleness + 4-DB isolation), and touches
Cat A/C via the in-process `AgentMemory` name-collision. The
pattern is a class of "we accepted cache-as-store; the accept
was implicit; we need an explicit policy" gaps.

**Downstream routing.** Cat H ↔ Cat B integration lens (S1305 §19
R4) is the highest-leverage remediation — a single design-preparation
doc fixes T3 (Redis-only durability) + T4 (in-process gap) + T7
(4-DB isolation) together. Post-S1399, design-preparation phase.

### 4.4 F4 — F1/F4-CANDIDATE discipline as inheritance methodology

**Definition.** A methodological pattern discovered by S1303 §14
in response to Agent 6's overreach on F4 dead-code claims, then
applied by S1304 §14 D7 to `ingested_via`, then applied by S1305
§14 D6 to `platform_config`, then extended by S1305 §14 D3 to
severity assertions (not just hypothesis assertions).

**The rule.** A dead-code / orphan-write claim requires
**owner-model-qualified consumer inventory** — not keyword grep.
Keyword grep catches unrelated variables + methods (e.g.,
`tasks_agents.py:1262` `agent_results = phase_data.get('results', {})`
is a local dict in different scope; `epa_handlers_utility.py:2910`
`aggregate_agent_results()` is a method on `execution_ids`, not
`ChatConversation.agent_results`). Until owner-model qualification
lands, the claim is CANDIDATE, not CONFIRMED.

**Extension to severity (S1305 §14 D3).** A sub-agent's severity
claim can be downgraded when sibling-audit context provides a
mitigating mechanism: S1305 downgraded Agent 6's CRITICAL
AgentLearningService durability claim to MEDIUM via Redis AOF
context (`settings.py:944`) matching S1302 T3 sibling classification.
Same discipline, applied to `severity` instead of `existence`.

**Applied instances still-CANDIDATE at arc close:**

| Field / Claim | Site | Awaiting | Owner |
|---------------|------|----------|-------|
| `DocumentEmbedding.ingested_via` orphan | 3 write sites: `sync_docs_index_to_documents.py:394`, `core/tasks_agents.py:4223/4290/4351`, `content/embeddings.py:654/753` | Full-tree recheck (S1304 §19 R1) | Cat E / Cat D |
| `ChatConversation.context_used` + `.agent_results` orphan | JSONField on ChatConversation | Owner-model-qualified inventory (R1.a) → runtime-vs-analytics-vs-UI classification (R1.b) → canonical-source-of-truth resolution (R1.c, first-class fields vs `metadata` dict) | S1303 §19 R1 |
| `platform_config` LRU F4-CANDIDATE | `platform_config.py:89, :133` — invalidation contract via `clear_config_cache()` at `:223` from setters at `:252, :269`; UNKNOWN whether Django admin / raw ORM / mgmt commands route through setters | Owner-model-qualified consumer inventory for mutation paths | S1305 §19 R1 |

**Rigby launch-call bonus (2026-07-01).** She flagged: "S1399 should
be explicit about what is canonical vs historical" — this section
IS that explicit statement. F4 discipline is CANONICAL from S1303
forward; any dead-code assertion in future audits or PRs must
satisfy it, and if it can't, the claim is CANDIDATE. Prevents
"audit says X exists" drift when the underlying claim is not
verified.

### 4.5 Adjacent pattern (not promoted to formal F5) — docs↔code naming / category drift

**Rigby SIGN cycle 1 nice-to-have.** A candidate fifth micro-pattern
was flagged: docs↔code naming/category drift spanning **S1302 §14
F5** (`spider_data_bridge` — named for Cat A per narrative
`KNOWLEDGE_RAG_MEMORY.md`; writes Cat B `UserAgentLearning` at
`core/learning_bridges/spider_data_bridge.py:240`) + **S1302 §14 F6**
(`MemoryPromotionService` — categorized under Cat C by parent §3C;
writes Cat B user-scoped `UserMemoryContext` at
`core/services/memory_promotion_service.py:303-318`, not Cat C
`AgentMemory` directly) + arguably **S1303 §14 F3** (`content_writer_agent.py:76`
imports `ConversationMemory` from wrong module + `:370` filters on
`memory_type` field that lives on `UserMemoryContext` at `:253`,
not the imported model — a code-vs-code contract drift as much as
docs-vs-code).

**Why NOT promoted to formal F5.** F1-F4 above each meet the
multi-child evidence threshold (≥3 children for F1 + F3 + F4; ≥3
sessions of hypothesis narrowing for F2). This candidate pattern
has evidence primarily within a single audit (S1302). Rigby
explicitly said "Not required if you want to keep exactly four."
The 4-pattern set was named at S1305 close as the specific arc
deliverable per parent §5 P6 rationale.

**Kept as adjacent evidence** for future arc scoping. Downstream
observations: (a) if the write-authority framework ADR
(S1302 §15 T10 → §8 Rank 5 above) surfaces additional
category-boundary drift, this pattern may promote to formal F5
in the design-preparation phase; (b) if Group 1400 Revenue or
Group 1500 Sports arcs surface similar naming/category drift, the
pattern crosses domain boundaries and merits arc-crossing
codification; (c) memory rule
`feedback_verify_before_deleting_dead_code.md` + F4 discipline
already partially cover the code-vs-doc dimension.

**Anchor.** S1302 §14.3 F5 + F6; S1303 §14 F3.

---

## 5. Resolved Contradictions

Where children disagreed; canonical verdict + rationale.

### 5.1 S1301 §19 D3 vs S1304 §14 D3 — `source_type` orphan claim

**Disagreement.** S1301 §19 D3 hypothesized both
`DocumentEmbedding.source_type` and `ingested_via` are orphan-writes.
S1304 §14 D3 direct file:line read at `content/embeddings.py:965-973`
confirmed `semantic_search_sync` applies `.filter(source_type__in=[...])`
in `internal_only` / `external_only` `source_filter` branches
(owner-model-qualified consumer).

**Canonical verdict.** S1304 wins. `source_type` HAS an owner-model-
qualified consumer; only `ingested_via` remains F1-CANDIDATE. S1301
§19 D3 is partially invalidated.

**Rationale.** Playbook §14 evidence rule + memory rule
`feedback_verify_before_deleting_dead_code.md`: direct file:line
read from the receiving-side child audit beats broad sibling
hypothesis. The verifier-loop pattern prevents sibling-audit
hypothesis propagation into library-wide false consensus.

**Load-bearing methodology consequence.** Every child audit that
inherits a broad hypothesis from a sibling MUST run parent-agent
verifier-loop spot-checks BEFORE Rigby SIGN. S1303 caught this
pattern first (§14 F4); S1304 applied it to S1301 §19 D3; S1305
applied it to Agent 6 severity claims (§14 D3 downgrade).

### 5.2 S1302 §17.3 "duplicate provenance systems" vs S1304 §17 "complementary"

**Disagreement.** S1302 §17.3 framed the row-level
`DocumentEmbedding.source_type` / `.ingested_via` fields alongside
the external `docs/_provenance.json` as a "two systems, no bridge"
name-collision-as-boundary-methodology.

**Canonical verdict.** S1304 §17 reframe wins. The two systems are
**complementary, not duplicate**: external JSON encodes session
origin (LOCAL keyword lane); row-level `source_type` encodes
source-of-record enum (PROD pgvector lane); the two are consumed
by different lanes and answer different questions.

**Rationale.** S1304's direct file:line evidence at
`content/embeddings.py:965-973` demonstrated `source_type` is
consumed differently than external `_provenance.json` — not
duplicated. The two lanes serve different retrieval styles.

**Guardrail (S1304 fold #4).** "Complementary today does not imply
optimal." A future design-preparation doc (post-S1399) may
recommend unification OR explicit scoping. S1304 §19 R2 owns that
decision.

### 5.3 Agent 6 "CRITICAL" severity vs S1305 §14 D3 MEDIUM classification

**Disagreement.** S1305's Agent 6 sub-agent sweep classified
`AgentLearningService` Redis-only durability as CRITICAL memory-
correctness violation.

**Canonical verdict.** S1305 verifier-loop downgrade wins. MEDIUM,
matching S1302 T3 sibling classification.

**Rationale.** Redis AOF context (`settings.py:944
REDIS_APPENDONLY=True` + `:945 REDIS_APPENDFSYNC='everysec'`)
preserves state across Redis restart. Loss on Python-worker recycle
is only the in-memory `_user_memories` buffer delta between last
`save_memory()` and recycle. Data at rest is durable within
Redis AOF policy.

**Load-bearing methodology consequence.** Sibling-inherited context
can correct severity assertions from sub-agents, not just hypothesis
assertions. F4 discipline extends to severity (§4.4 above).

### 5.4 Agent 6 "13 `cache.set(timeout=None)`" vs S1305 §14 D10 "5 production"

**Disagreement.** S1305 Agent 6 counted 13 sites.

**Canonical verdict.** 5 production sites in `core/` runtime scope.
Rigby SIGN cycle 1 tightened definition to exclude 7 test-only + 2
subprocess-timeout `_run_ffmpeg` non-cache-set calls + 1 MOCK-class
fallback + archive/scripts.

**Rationale.** S1305 §3 excluded-from-count table enumerates each
excluded category with reason. Playbook §14 grep-verify-binary-
claims rule — the count that matters is `core/` runtime scope, not
raw grep hits.

### 5.5 Parent §3H bullet "search_docs `lru_cache(1)`" vs S1305 §15 T12

**Disagreement.** Parent doc §3H (Chris-locked bullet from S1273
§5.4 provenance) said "search_docs `lru_cache(1)` per-process."

**Canonical verdict.** Imprecise; cache is on `_load_provenance_docs`
called from `search_docs`, not `search_docs` itself.

**Rationale.** S1305 direct file:line read at `td_handlers_ops.py:78`
confirmed the decorator location.

**Downstream.** S1305 §15 T12 tracks the doc-precision drift.
Anchor-update recommendation for `KNOWLEDGE_RAG_MEMORY.md`
narrative (§7.4 below).

---

## 6. Unresolved Unknowns

Explicit list of what the arc did NOT resolve. Every item promotes
to §8 follow-on queue.

### 6.1 Three F4-CANDIDATE fields pending owner-model-qualified verification

| Field / Site | Anchor | Blocks |
|--------------|--------|--------|
| `DocumentEmbedding.ingested_via` orphan claim | S1304 §14 D7; §19 R1 | T5 wire-or-deprecate decision; provenance-system reconciliation design (§8 below) |
| `ChatConversation.context_used` + `.agent_results` orphan claim | S1303 §14 F4; §19 R1.a/b/c | R8 broken import + field mismatch fix in `content_writer_agent.py`; canonical source-of-truth decision |
| `platform_config` LRU non-setter-routed mutation paths | S1305 §14 D6; §19 R1 | T10 remediation (post-S1399) |

### 6.2 `MemorySystem` T5 severity blocked on `IntelligentJobMatcher` production invocation

| Item | Blocker | Anchor |
|------|---------|--------|
| Is `MemorySystem` unbounded `timeout=None` at `core/memory_system.py:54-55, :176` HIGH-severity user-visible (if `IntelligentJobMatcher` is production-invoked) or LOW (if orphan/experimental/test-only)? | S1305 §19 R6 audit needed. Rigby SIGN cycle 1 grep confirmed `MemorySystem` IS active via `ai_core/agents/intelligent_job_matcher.py:57 self.memory = MemorySystem()`. Production invocation of `IntelligentJobMatcher` itself is UNKNOWN. | S1305 §14 D5; §19 R6 |

### 6.3 Cat F ↔ Cat D turn-context → RAG enrichment: intentional-separation vs drift

**S1304 §19 R5 verdict.** Cannot resolve from static evidence —
requires product/architecture decision.

- Intentional-separation signals (3): 8 enrichment services
  deliberately non-RAG; two first-class PA tools for explicit
  corpus access; thread-memory vs source-memory scope discipline.
- Drift signals (3): no design comment explaining absence; no
  feature flag guarding the absence; asymmetry with
  `BaseAgent._get_relevant_knowledge_for_task` (agents get
  auto-enrichment; PA does not).

**Routed to design-preparation phase post-S1399** with R5.a
(canonicalize separation) + R5.b (implement enrichment) as
competing hypotheses. NOT this summary's job to resolve.

### 6.4 Write-authority framework for `AgentMemory.create_memory` (T10 HIGH)

**S1302 §15 T10.** No user FK, no rate limiting, no audit of who
created what. `MemoryPromotionService` auto-saves on every PA turn.
Highest-severity debt item in the entire arc.

**Routing.** Anchor-recommendation for a cross-arc write-authority
framework ADR. NOT this summary's job to design (playbook §14.5
forbids implementation-in-research). See §8 below.

### 6.5 Cat F ↔ Cat B: `UserMemoryContext` vs `ConversationMemory` boundary

**S1303 §15 D1.** `content_writer_agent.py:76` imports from wrong
module (soft-fails via try/except at `:74-80`); if fixed to `from
core.models import ConversationMemory`, the guarded branch at `:370`
queries `.filter(memory_type__in=[...])` — but Django
`ConversationMemory` at `models/conversations/models.py:19-31` has
NO `memory_type` field (lives on `UserMemoryContext` at `:253`).

**Unresolved.** Which memory model was intended: `ConversationMemory`
(Cat F) or `UserMemoryContext` (Cat C)? Requires design decision
before the runtime fix in S1303 §19 R8 can land safely.

### 6.6 Cat G Mission Memory boundary with Cat C AgentMemory

**Delegated at parent §3G (Chris-locked D2).** Boundary between Cat
C `AgentMemory` audit trail semantics and `OpsRun(domain='mission')`
+ `OpsRunEvent` execution trace unresolved. Employee OS 1200s arc
owns.

### 6.7 Cat H sibling `@lru_cache` sweep across `core/`, `ai_core/`, `content/`

**S1305 §19 R7.** Cat H surface enumeration completes in
`core/services/` (4 sites). Whether other correctness-critical
in-process caches exist in `core/`, `ai_core/`, `content/` is
UNKNOWN.

### 6.8 Beat-schedule cache-refresh cadence gaps beyond `build_docs_provenance`

**S1305 §19 R3.** Extends S1304 §14 D6 pattern. Which other mgmt
commands "should" run periodically to keep Cat H caches fresh but
are unscheduled?

---

## 7. Anchor-Update Recommendations

Concrete proposed edits. Per playbook §16 canonical-summary rule:
"Do NOT edit anchors in the summary itself; the ARCHITECTURE_INDEX
v-bump commit applies them." This section lists proposals.

### 7.1 `docs/PLATFORM_INVENTORY.md`

**No direct edits.** `PLATFORM_INVENTORY.md` is the runtime anchor
(per CLAUDE.md context-kit rule), regenerated by
`python manage.py generate_platform_inventory --write`. Chris runs
regeneration when convenient. This summary does not propose
hand-edits.

The regenerator will produce fresh runtime counts; the narrative
context (which category each memory surface belongs to, what its
maturity verdict is, what its drift class is) belongs in
`platform_architecture_inventory.md` (§7.2 below), not the auto-
regenerated inventory.

### 7.2 `docs/research/platform_architecture_inventory.md`

**Proposed edits (S1399 deliverables per parent §5 P6):**

#### 7.2.1 §3.13 subdivision — into Cat A / Cat B / Cat C sub-rows

**Motivation.** S1302 established that A/B/C are distinct persistence
architectures with distinct maturity verdicts (Cat A = PARTIAL, Cat
B = PARTIAL, Cat C = EXPERIMENTAL). Current single §3.13 row masks
this.

**Proposed structure.**

```
§3.13 Memory / Knowledge / Embeddings
    §3.13.1 Semantic Knowledge (Cat A)
        - Primary store: AgentKnowledgeSource
        - Maturity: PARTIAL
        - Drift: F1 pa_content_feedback dead-code loop; F5 spider_data_bridge docs_stale
        - Anchor: S1302 §4, §14
    §3.13.2 Personal-Adaptive (Cat B)
        - Primary store: UserAgentLearning + AgentLearningService (Redis DB 5)
        - Maturity: PARTIAL (Postgres WORKING + Redis PARTIAL)
        - Drift: 14-day hardcoded window; Redis-only durability with AOF
        - Anchor: S1302 §4, §14; S1305 §14 D3/D4
    §3.13.3 Agent Working (Cat C)
        - Primary store: Django AgentMemory + in-process AgentMemory (name collision) + UserMemoryContext
        - Maturity: EXPERIMENTAL
        - Drift: F1 dead-code loop; T10 no write authority gate HIGH
        - Anchor: S1302 §4, §14, §17.2
```

#### 7.2.2 §3.14 lane consolidation

**Motivation.** S1301 established that the two-lane split is
canonical architecture (not drift) and named the lane selector
absence as ownership-open. Current §3.14 row should reflect the
lane split explicitly.

**Proposed shape.**

```
§3.14 RAG Retrieval Lanes (Cat D)
    - LOCAL keyword lane: core.rag.top_k on .rag/corpus.jsonl
        + provenance filter via external docs/_provenance.json (LRU-cached)
    - PROD pgvector lane: core.rag_integration.search_embeddings
        + DocumentEmbedding.source_type filter (row-level)
    - Runtime lane selector: NEVER IMPLEMENTED (S1301 §14.3 D6)
    - PA turn enrichment: does NOT auto-invoke either lane (tool-call-only)
    - Maturity: WORKING (dropped from STABLE due to 21.5% UNKNOWN corpus gap)
    - Anchor: S1301 §5-§7, §14
```

#### 7.2.3 New §3.N row for Cat F Conversational / Thread Memory

**Motivation.** S1303 first-inventory landing — no §3.N row existed
at audit open. S1303 §4 Major Models + §7 Runtime Flows are load-
bearing.

**Proposed shape.**

```
§3.N Conversational / Thread Memory (Cat F)
    - Primary store: ChatConversation (row-per-exchange) at models/conversations/models.py:59-187
    - Entry points: session_tool.create_fresh (mint pa-<hex[:16]>);
                    session_tool.retire (enforce inactive)
    - Runtime flows: turn-history reinject at unified_pa_entrypoint.py:7277-7343
                     (last 10 rows, 8000-char truncation, tool-call metadata)
    - Enforcement: dispatcher gate at conversation_action_dispatcher.py:288-316 (fail-open)
    - Maturity: WORKING (bounded); PARTIAL on lifecycle hygiene + analytics + hard enforcement
    - Drift: F1 stale-thread waste RECONCILED (S1248 matched-pair fix);
             F3 wrong-model+wrong-field in content_writer_agent.py:76+:370;
             F4 context_used+agent_results CANDIDATE;
             F9 no auto-cleanup;
             F10 Discord unlinked-user linkage-completion signal MISSING
    - Anchor: S1303 §4, §7, §14
```

#### 7.2.4 New §3.N or §5 row for Cat H Runtime Memory Correctness

**Motivation.** S1305 first-inventory landing of the runtime-cache
tier. Load-bearing findings scattered across §14 D1-D10.

**Proposed shape.**

```
§3.N or §5.N Runtime Memory Correctness (Cat H)
    - 4 @lru_cache(1) sites in core/services/:
        _load_provenance_docs at td_handlers_ops.py:78 (no invalidation, worker-restart contract)
        _cached_primary_workspace_id at platform_config.py:89 (clear_config_cache() at :223)
        _cached_primary_user_id at platform_config.py:133 (same contract)
        _load_config at fleet_routing.py:64 (no invalidation, deploy-restart contract)
    - 5 production cache.set(timeout=None) sites in core/ runtime scope:
        core/tasks.py:5936 (docs corpus index hash)
        core/memory_system.py:54, :55, :176 (index + embedding index + data)
        core/services/discord_bot.py:9723, 9728 (Discord config)
    - Redis 4-DB topology:
        DB 1 Django cache (settings.py:452 RedisCache + LOCATION=REDIS_URL)
        DB 2 Celery broker (settings.py:802)
        DB 3 Celery results (settings.py:803)
        DB 5 AgentLearningService (agent_learning_service.py:145 hardcoded, raw redis client at :160)
    - Maturity: WORKING with drift
    - Load-bearing risks:
        AgentLearningService within-process consistency gap (S1305 §14 D4)
        MemorySystem index → data divergence under Redis LRU eviction (S1305 §14 D5)
        Django cache.clear() invisible to DB 5 (S1305 §14 D8)
    - Anchor: S1305 §14 D1-D10
```

### 7.3 `docs/research/ARCHITECTURE_INDEX.md`

**Proposed v17 → v18 bump.** Register this summary as §1.21; add §8
timeline S1399 row; note Group 1300 arc closed (5-child arc +
canonical summary complete).

The v-bump commit applies:

- New §1.21 row for `domains/memory/1399_memory_canonical_summary.md`
- §8 timeline S1399 row (per format of prior S1301-S1305 rows)
- `last_verified` frontmatter updated to `v18 — S1399 registered
  domains/memory/1399_memory_canonical_summary.md as §1.21; Group
  1300 arc closed (5-child + canonical summary complete); F1-F4
  patterns named; anchor-update recommendations proposed for
  platform_architecture_inventory.md §3.13 subdivision + §3.14
  lane consolidation + new Cat F/H rows; follow-on queue ranked
  per §8; Cat G delegated to Employee OS 1200s arc; Group 1700
  Observability delegations aggregated (F1 filter-drop telemetry,
  F1 dead-code detection, F1 EventBus adoption for Cat F, Cat H
  worker-recycle instrumentation); F4 F1/F4-CANDIDATE + severity-
  correction discipline canonicalized as inheritance methodology.`

### 7.4 Other affected docs

#### 7.4.1 `docs/topics/infrastructure.md` — Redis DB count

**Drift (S1305 §14 D9).** Doc says "3 Redis DBs"; actual is 4.

**Proposed edit.** Update to 4 DBs with DB-5 `AgentLearningService`
rationale. Standalone bugfix per S1305 §19 R8.

#### 7.4.2 `docs/narratives/KNOWLEDGE_RAG_MEMORY.md`

**Three proposed updates.**

- (a) F1 `pa_content_feedback` UNKNOWN → confirmed dead code
  reference (S1302 §14.3 F1). Current narrative at `:115, :294, :330`
  describes the intended feedback loop; add a note that the
  consumer half was never implemented (14 doc references, 1
  producer, 0 code consumers).
- (b) Two-lane split explicit reference (S1301 §7.1). Current
  narrative describes retrieval but not the LOCAL-vs-PROD lane
  split.
- (c) Precision fix on "search_docs `lru_cache(1)`" (S1305 §15
  T12). Cache is on `_load_provenance_docs` called from
  `search_docs`, not `search_docs` itself. Narrative at `:103-104`
  (memory-rule mention: restart workers after regen) should be
  precise about which function has the LRU.
- (d) Add pointer to this canonical summary as the entry-point for
  the memory architecture map.

#### 7.4.3 `docs/topics/personal-assistant.md`

**Optional.** May want a pointer to Cat F Conversational/Thread
Memory findings (S1303 §7) for the PA turn-history reinject
mechanism.

#### 7.4.4 `docs/topics/docs-ingestion-cascade.md` (NEW)

**S1304 §19 R6.** MEDIUM priority publish target — the 4-step
cascade is currently documented only in memory rule
`feedback_docs_pipeline_4_step_cascade.md`. Publish as
`docs/topics/docs-ingestion-cascade.md`: 4-step flow, preconditions,
postconditions, failure/recovery, cadence rationale. Owner: Cat E
docs-governance (Documentation Manager `AIEmployee`).

---

## 8. Follow-On Research Queue

Ranked by architectural uncertainty × risk × unblocked flows per
playbook §11.2 rubric. This is the arc's forward-looking output.

### 8.1 Ranking rationale

| Rank | Item | Uncertainty | Risk | Unblocks | Total |
|------|------|-------------|------|----------|-------|
| 1 | S1304 §19 R1 `ingested_via` full-tree recheck | MEDIUM (F1-CANDIDATE; 3 write sites known) | MEDIUM (wrong deprecation could remove field designed for future use) | S1304 T5 wire-or-deprecate; §17 provenance-system reconciliation design; migration to remove field if truly orphan | **HIGHEST** |
| 2 | S1303 §19 R1.a/b/c `context_used` + `agent_results` verification | HIGH (F4-CANDIDATE; keyword-grep insufficient) | MEDIUM (canonical source-of-truth unknown between first-class fields and `metadata` dict) | S1303 R8 runtime fix; canonical source-of-truth resolution; any future PR touching these fields | HIGH |
| 3 | S1305 §19 R1 `platform_config` F4-CANDIDATE | LOW (2 known cache sites + setter contract) | LOW-MEDIUM (LRU serves stale ID until worker recycle if non-setter mutations exist) | T10 remediation | HIGH |
| 4 | S1305 §19 R6 IntelligentJobMatcher production invocation audit | HIGH (single grep hit + adjacent SharedMemorySystem sites) | Determines T5 MemorySystem severity (MEDIUM ↔ HIGH ↔ LOW) | T5 remediation prioritization | HIGH |
| 5 | S1302 §15 T10 write-authority framework design-preparation ADR | HIGH (ADR needed) | HIGH (open memory creation surface — rogue-turn attack vector; T10 highest-severity debt in arc) | Cat C hardening; Cat A/B auth story generalizes | HIGH |
| 6 | S1305 §19 R2 Cat H remediation design-preparation per surface | LOW (option set inherited from S1304 T2: worker-restart trigger vs file-watcher vs Redis-queryable vs TTL) | MEDIUM (Cat H user-visible-correctness impact) | T1/T2/T4/T5/T6 remediation | MEDIUM-HIGH |
| 7 | S1305 §19 R4 Cat H ↔ Cat B integration lens | MEDIUM (design decision on Redis-as-authoritative vs DB-as-authoritative) | MEDIUM | T3 + T4 + T7 fixed together | MEDIUM-HIGH |
| 8 | S1304 §19 R2 provenance-system reconciliation design | MEDIUM (unify vs explicit scoping) | LOW | T3 remediation | MEDIUM |
| 9 | S1304 §19 R5 turn-context → RAG enrichment design decision | HIGH (intentional vs drift not resolvable from static evidence) | MEDIUM (operational cost + migration risk) | Cat F ↔ Cat D integration policy | MEDIUM |
| 10 | S1305 §19 R3 beat-schedule cache-refresh cadence audit | LOW (extension of S1304 D6 pattern) | LOW | Class-wide cadence hardening | MEDIUM |
| 11 | S1303 §19 R2 EventBus adoption design for Cat F | MEDIUM (delegated to Group 1700 — see §9.2) | LOW-MEDIUM | Cat F observability | MEDIUM |
| 12 | S1305 §19 R7 full `@lru_cache` sweep across `core/`, `ai_core/`, `content/` | LOW-MEDIUM (enumeration) | LOW | Cat H surface enumeration completeness | LOW-MEDIUM |
| 13 | S1303 §19 R4 retention lifecycle for retired rows | LOW | LOW | F9 remediation | LOW-MEDIUM |
| 14 | S1303 §19 R6 formalize session identity mint contract | LOW-MEDIUM | LOW | §17 duplicate mechanism cleanup | LOW-MEDIUM |
| 15 | S1305 §19 R5 worker-recycle instrumentation (delegated to Group 1700) | LOW-MEDIUM | LOW | Cat H silent-degradation detection | LOW-MEDIUM |
| 16 | S1301 §19 R2 filter-drop telemetry (delegated to Group 1700) | LOW | MEDIUM | Cat D silent-failure detection | LOW-MEDIUM |
| 17 | S1304 §19 R7 filter-drop telemetry (delegated to Group 1700) | LOW | MEDIUM | Cat E↔D silent-failure detection | LOW-MEDIUM |
| 18 | S1305 §19 R8 doc-drift fix on Redis DB count (`docs/topics/infrastructure.md`) | LOW | LOW | Doc accuracy | LOW |
| 19 | S1303 §19 R7 doc-in-tooling reconciliation for pin rotation policy (F8) | LOW | LOW | Governance drift | LOW |
| 20 | S1301 §19 R2.2 Group 1400 Revenue integration lens (if RAG-augmented content becomes revenue path) | HIGH (future condition) | LOW | Group 1400 arc | LOW (until conditional) |
| 21 | S1304 §19 R8 S1301 follow-up classifier precedence bug | LOW (single scoped bug) | LOW | Standalone doc classification accuracy | LOW |

### 8.2 Immediate P1 items (next 5 sessions)

1. **R1a — `ingested_via` full-tree recheck** (S1304 §19 R1). Rank 1
   above. Sessions 1400s.
2. **R1.a — `ChatConversation.context_used` + `.agent_results`
   owner-model-qualified inventory** (S1303 §19 R1.a). Rank 2 above.
3. **R1 — `platform_config` F4-CANDIDATE mutation-path audit**
   (S1305 §19 R1). Rank 3 above.
4. **R6 — `IntelligentJobMatcher` production invocation audit**
   (S1305 §19 R6). Rank 4 above. Blocks T5 severity assessment.
5. **T10 write-authority framework ADR** (S1302 §15 T10 promoted).
   Rank 5 above. Highest-severity debt in arc; ADR design work
   post-S1399.

### 8.3 Design-preparation phase items (post-S1399)

Not this arc; not the next 5 sessions either. Routed to design-
preparation phase:

- Cat H remediation per surface (S1305 §19 R2). Consumes S1304 T2
  option set.
- Cat H ↔ Cat B integration lens (S1305 §19 R4). Fixes T3+T4+T7
  together.
- Provenance-system reconciliation (S1304 §19 R2). Unify vs
  explicit scoping.
- Turn-context → RAG enrichment (S1304 §19 R5). Intentional-vs-drift
  decision.

### 8.4 Delegated to other arcs

See §9 below. Group 1700 Observability inherits multiple items;
Employee OS 1200s owns Cat G.

---

## 9. Cross-Links to Delegated Arcs

Every `delegates_to:` entry from parent + children gets a callout.

### 9.1 Employee OS 1200s arc — Cat G Mission / Execution Memory

**Delegation source.** Parent §3G (Chris-locked D2 2026-07-01):
Cat G Mission / Execution Memory boundary with Cat C AgentMemory
delegated to Employee OS 1200s arc.

**Handoff surface.** Cat G territory:

- `OpsRun(domain='mission')` + `OpsRunEvent` at `core/models_ops_runs.py`
- `MissionRunner` orchestrator at `core/employees/mission_runner.py`
- `ToolCallRecord` audit trail
- Documentation Manager (Rigby) + Platform Auditor + Chief of Staff
  employees at `core/employees/jobs.py`

**Unresolved boundary questions** (to be picked up by Employee OS
arc):

- Cat C `AgentMemory` audit-trail-fields overlap with `OpsRunEvent`
  execution-trace fields (S1302 §17.2 name-collision noted).
- `MissionRunner` step-verdict semantics vs `AgentMemory.record_access`
  write pattern.
- Whether Employee OS lifecycle events should ride EventBus (§9.2
  below) or stay OpsRun-only.

**Cross-link path.** `docs/EMPLOYEE_OS_PRIMITIVES.md` +
`docs/topics/employee-os.md` are the reading anchors. Employee OS
1200s arc parent-scoping (when opened) should cite S1302 §17.2 name
collision + S1304 §18 Documentation Manager ownership as prior art.

### 9.2 Group 1700 Observability — 4 aggregated delegations

**Motivation.** Multiple children route observability-flavored items
to a future Group 1700 arc. This canonical summary aggregates them.

| Item | Source | Kind | Priority |
|------|--------|------|----------|
| Filter-drop telemetry for `excluded_missing_provenance` / `excluded_mismatch` (Cat D) | S1301 §19.2 R1 | Event emission spec + Prometheus counter + Grafana surface | MEDIUM |
| Filter-drop telemetry for E↔D boundary (Cat E↔D) | S1304 §19 R7 | Same class as above | MEDIUM |
| Dead-code / producer-only detection surface | S1302 §19.2 R1 | General "producer-only" telemetry to catch F1-class bugs before ship | MEDIUM |
| EventBus adoption for Cat F (`CONVERSATION_CREATED` / `CONVERSATION_RETIRED` / `TURN_PROCESSED` / `TURN_FAILED`) | S1303 §19 R2 | Stream + consumer spec + reconciliation with S1274 §12.1 EventBus adoption arc | MEDIUM |
| Worker-recycle instrumentation for Cat H (metric on cache repopulation; alert on repopulation rate exceeding threshold) | S1305 §19 R5 | Instrumentation | MEDIUM |

**Rigby-flagged nuance.** Some of these are compound: F1-class
dead-code detection may benefit from ties to Cat F's F4-CANDIDATE
discipline (§4.4 above) — an observability surface that catches
producer-only surfaces is also a surface that produces owner-model-
qualification input data. Group 1700 arc scoping session should
consider whether to treat these as one problem or four.

### 9.3 Post-S1399 design-preparation phase — 4 arcs

| Arc | Source | Deliverable |
|-----|--------|-------------|
| Cat H remediation per surface | S1305 §19 R2 | Design-preparation doc per LRU/cache site using S1304 T2 option set (worker-restart trigger vs file-watcher vs Redis-queryable vs TTL) |
| Cat H ↔ Cat B integration lens | S1305 §19 R4 | Design-preparation doc: AgentLearningService Redis-only durability + TTL policy + DB writeback design decision (fixes T3+T4+T7 together) |
| Provenance-system reconciliation | S1304 §19 R2 | Unify OR explicit-scoping decision; migration path for 21.5% UNKNOWN entries; does `search_docs` gain `source_type` filtering; does `kb_tool` gain `originating_session` filtering |
| Turn-context → RAG enrichment | S1304 §19 R5 | R5.a canonicalize separation + R5.b implement enrichment as competing hypotheses; product/architecture verdict on operational cost + migration risk + future retrieval requirements |
| Write-authority framework ADR | S1302 §19.2 R3 + S1302 §15 T10 | ADR: permission model / rate limiting / audit trail shape for `AgentMemory.create_memory` (T10 HIGH) |

### 9.4 Standalone bugfix follow-ups (NOT research)

Filed here for §14 completeness per playbook rules. These do NOT
block any arc:

- S1303 §19 R8 — Fix D1 broken import + field mismatch in
  `content_writer_agent.py:76 + :370`.
- S1305 §19 R8 — Doc-drift fix on Redis DB count
  (`docs/topics/infrastructure.md` 3 → 4).
- S1304 §19 R8 — S1301 follow-up classifier precedence bug (LOW
  priority).

---

## 10. What This Research Taught Us About How to Do Research

Meta-methodology retrospective. This is the arc's contribution to
the research process, not just to the domain being researched.
Distinct from §4 Cross-Cutting Patterns (which are about the
memory domain) and §11 Arc Change Log (which is the historical
ledger of what happened in this arc). §10 is what future arcs
learn from this one.

**First application of the playbook §11.3 §10 template addition**
adopted at S1399 close 2026-07-01 per Chris directive. Playbook
§11.3 template updated same-commit; every future xx99 canonical
summary includes this section.

### 10.1 What worked (methodology validated across this arc)

1. **Verifier-loop pre-SIGN spot-checks.** Parent-agent verifier-
   loop reading sub-agent claims BEFORE routing to Rigby SIGN
   caught two Agent-6 overreaches at S1303 §14 (F3 "would fail at
   import time" → soft-fail-with-guard; F4 "confirmed dead code"
   → CANDIDATE) + broad hypothesis overreach at S1304 §14 D3
   (partial invalidation of S1301 §19 D3) + severity overreach at
   S1305 §14 D3 (Agent-6 CRITICAL → MEDIUM via Redis AOF context).
   Consequence: SIGN cycles focused on substantive edges rather
   than evidence corrections. **Result: 3 of 5 child audits
   (S1303, S1304, S1305) hit SIGN-clean in 2 cycles;** S1301 in
   1 cycle; S1302 in 3 cycles.

2. **F1/F4-CANDIDATE discipline as inheritance methodology.**
   Dead-code / orphan-write claims require owner-model-qualified
   consumer inventory, not keyword grep. Named at S1303 §14;
   applied at S1304 §14 D7 (`ingested_via`); applied at S1305 §14
   D6 (`platform_config`). Extended at S1305 §14 D3 to severity
   assertions (not just existence assertions). **Result: prevents
   "audit says X" false consensus + preserves hypothesis-vs-
   CANDIDATE separation across sibling propagation.**

3. **Fresh SIGN isolation pins per child audit + arc-continuity
   pin for scope.** Each child audit got a fresh Rigby SIGN pin
   (S1301-S1305 + S1399); arc-continuity pin `pa-aa54193f240f4846`
   carried mission scope across all 7 sessions without contaminating
   SIGN pressure-tests. **Result: clean SIGN evidence + arc-level
   context preserved.** See §11.3 below for the full pin ledger.

4. **Bounded canonical-summary discipline.** Playbook §11.3
   "consume outputs, don't re-audit" rule enforced in S1399. No
   new §13 6-parallel-Explore sweep. No new file:line evidence. No
   CANDIDATE → CONFIRMED resolutions. Every claim cites source-
   audit §-anchor via `SNNNN §NN.N` notation. **Result: 1-cycle
   SIGN-clean at High confidence** — the shortest SIGN path in
   the arc.

5. **Reduced-prompt short-command rhythm.** Chris's `start research
   group 1399` short command with default lean D19+D20 = full
   session launch. Playbook §12.3 target validated. **Result: no
   custom prompt required beyond the command itself.**

6. **Parent-with-children arc shape.** Group 1300 spanned 7 sessions
   cleanly: parent (S1300) + 5 category children (S1301-S1305) +
   canonical summary (S1399). Each child had clear scope; canonical
   summary synthesized. **Result: better than single-audit for
   domains with multiple categories.** First parent-with-children
   arc in the library to reach the xx99 close stage.

### 10.2 What to codify into playbook v3 (per §20 two-triggers rule)

Patterns hit the §20 two-triggers threshold (used across ≥3 arcs)
and should promote:

| Pattern | Uses | Threshold | Recommended playbook v3 addition |
|---------|------|-----------|----------------------------------|
| **F1/F4-CANDIDATE discipline** | S1303 §14; S1304 §14 D7; S1305 §14 D6 | **3 of 3 — MET** | Add §14 evidence rule: "Dead-code / orphan-write claims require owner-model-qualified consumer inventory, not keyword grep. Until qualification lands, claim is CANDIDATE." |
| **Sibling-inheritance hypothesis-correction** | S1303 (Agent-6 pre-SIGN); S1304 (S1301 §19 D3 partial invalidation); S1305 (severity extension) | **3 of 3 — MET** | Add §15 SIGN rule: "Every child audit inheriting a broad hypothesis MUST run parent-agent verifier-loop spot-checks BEFORE Rigby SIGN. Hypothesis stays CANDIDATE until receiving-side audit verifies via direct file:line." |
| **Severity-correction via sibling context** | S1305 §14 D3 (Agent-6 CRITICAL → MEDIUM via Redis AOF sibling context matching S1302 T3) | **1 of 3 — NEEDS ADDITIONAL ARC USES** | Watch for reuse in Group 1400+ before codifying. Current evidence is single-arc application. |
| **Docs cascade at every close-out** | S1399 close 2026-07-01 (Chris directive) | **1 of 1 — CHRIS-RATIFIED, NO THRESHOLD REQUIRED** | Add §17 graduation criteria checklist item: "docs → RAG cascade (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` → `build_docs_provenance`) executed post-merge before declaring arc closed." Memory rule `feedback_docs_cascade_at_every_close.md`. |
| **Meta-methodology §10 in canonical summaries** | S1399 (this doc, retrofitted) | **1 of 1 — CHRIS-RATIFIED, NO THRESHOLD REQUIRED** | Already applied to playbook §11.3 template same-commit as this section landing. First application: this doc. Memory rule `feedback_xx99_meta_methodology_section.md`. |

**Consequence for arc-scoped methodology outputs.** The three
patterns tagged **MET** above (F1/F4-CANDIDATE discipline; sibling-
inheritance hypothesis-correction; severity-correction extension)
formally graduate from "arc pattern" to "playbook v3 candidate."
Playbook v3 update session is queued as a follow-on. Two additional
patterns (**docs cascade + meta-methodology §10**) are Chris-ratified
directly and skip the two-triggers gate.

### 10.3 What didn't work / anti-patterns to avoid in future arcs

1. **Sub-agent claims without verifier-loop.** Every child audit's
   6-parallel Explore sweep produced at least one overreach that
   would have shipped to Rigby SIGN if parent-agent hadn't spot-
   checked. Anti-pattern: routing sub-agent output directly to
   SIGN without parent-agent verifier-loop pre-corrections.

2. **Broad orphan-write hypotheses without owner-model qualification.**
   S1301 §19 D3 broadly hypothesized both `source_type` +
   `ingested_via` are orphan. S1304 verifier-loop found only
   `ingested_via` qualifies. Anti-pattern: keyword-grep as sole
   evidence for dead-code / orphan-write claims.

3. **Declaring arc-close "done" without running docs cascade.**
   S1303/S1304/S1305 close-outs skipped the 4+1 step cascade. Docs
   were on git/`main` but not in `Document` table, not embedded,
   not searchable to Rigby. Chris caught this at S1399 close
   2026-07-01. Anti-pattern: any docs-modifying arc/session that
   doesn't run the cascade at close.

4. **Duplicate memory patterns surfacing across multiple children
   when parent should have named them upfront.** `@lru_cache(1)`
   surfaced in S1301 (Cat D), S1304 (Cat E↔D), and S1305 (Cat H)
   as separate finding classes when parent §3H should have named
   it as a first-class category upfront. Anti-pattern: parent
   scoping doc not naming cross-child pattern surfaces that recur.

5. **Declaring dead code from keyword grep.** Memory rule
   `feedback_verify_before_deleting_dead_code.md` names this class.
   F4-CANDIDATE discipline (§10.2 above) is the codification.
   Anti-pattern: any "0 hits" grep result treated as CONFIRMED
   dead code without owner-model qualification.

6. **Skipping the canonical summary xx99 slot on a multi-child
   arc.** Group 1300 explicitly reserved S1399 for the canonical
   summary per parent §5 P6 slot. Without the xx99 slot, cross-
   cutting patterns (§4 F1-F4) would have remained implicit across
   child audits + never named as a coherent set. Anti-pattern:
   closing a multi-child arc without producing the xx99 canonical
   summary.

### 10.4 Suggestions for the playbook itself

Concrete edits to `DOMAIN_RESEARCH_PLAYBOOK.md` that this arc's
experience motivates. Not requirements — suggestions for Chris /
Rigby to consider in a future playbook process session:

1. **§14 evidence rules addition** — Codify F1/F4-CANDIDATE
   discipline as a rule (per §10.2 above). Bar keyword-grep as
   sole evidence for dead-code claims; require owner-model
   qualification.

2. **§15 SIGN rules addition** — Codify sibling-inheritance
   hypothesis-correction pattern as a rule. Every child audit
   inheriting a broad hypothesis MUST run parent-agent verifier-
   loop spot-checks BEFORE Rigby SIGN.

3. **§17 graduation criteria addition** — Add docs cascade +
   provenance rebuild checklist items to arc-close criteria. Not
   optional. Memory rule already codified; playbook body should
   reflect.

4. **§11.3 canonical summary template addition — APPLIED SAME-
   COMMIT.** The §10 "What This Research Taught Us About How to
   Do Research" section is non-negotiable for xx99 docs going
   forward. Playbook §11.3 template updated same-commit as this
   section landing.

5. **§13 sweep guidance** — Add note that parent-agent verifier-
   loop spot-checks are expected between sub-agent output and
   Rigby SIGN routing. Sub-agent output is CANDIDATE, not ground
   truth.

6. **§11.1 parent scoping template addition** — Add "cross-child
   pattern surfaces" callout to parent scoping template so future
   arcs name recurring patterns (like `@lru_cache`) at scoping
   time rather than surfacing them redundantly across children.

### 10.5 Suggestions for future canonical summaries

Optional guidance for canonical summaries that follow S1399:

1. **Preserve child-audit CANDIDATE labels.** S1399 §4-§8 preserved
   F1-CANDIDATE + F4-CANDIDATE labels throughout. Canonical
   summaries should NOT resolve CANDIDATE claims — that's the
   follow-on audit's job.

2. **Cite source-audit §-anchor for every claim.** S1399 used
   `SNNNN §NN.N` notation throughout. Aids Rigby SIGN Q10-Q13
   traceability + gives future readers exact provenance.

3. **Include a §4.5-style "adjacent evidence" addendum for Rigby
   nice-to-haves.** S1399 §4.5 acknowledged a fifth candidate
   pattern as adjacent evidence rather than promoting to formal
   §4 pattern. Preserves the pattern set named at arc close while
   acknowledging Rigby's suggestion.

4. **Aggregate delegated-arc handoffs into §9.** S1399 §9.2
   aggregated 4 Group 1700 Observability delegations from 4
   different children into one delegation surface. Reduces the
   future arc's scoping cost.

5. **Number sub-sections of §7 by target doc.** S1399 §7.2
   subdivided by target doc (`platform_architecture_inventory.md`
   §3.13 subdivision, §3.14 lane consolidation, new Cat F/H rows).
   Makes anchor-update commits atomic.

6. **Use `SNNNN §NN.N` for every source-audit citation.** Not just
   in prose; in tables + change log + appendix too. Gives Rigby's
   Q10-Q13 pressure-test grep-friendly provenance.

---

## 11. Arc Change Log

Which child, which session, which Rigby verdict, which fold edits.
Per playbook §11.3 §11 template requirement.

### 11.1 Session-by-session ledger

| Session | Doc | Rigby SIGN | Cycles | Load-bearing fold edits | Commit |
|---------|-----|-----------|--------|------------------------|--------|
| S1300 | `1300_memory_domain_scoping.md` (parent) | Light — playbook §9 attaches SIGN to audits, this is scoping | 0 | Chris D1-D5 lock 2026-07-01 (parent-with-children shape; Cat G delegated; §6 finding parked as S1301 input; P2 rename to Persistence Architecture; S1399 canonical summary planned) | Committed pre-arc-start |
| S1301 | `1301_memory_rag_retrieval_lanes_audit.md` (Cat D) | SIGN-clean | 1 | MF1 denominator citation; MF2 D3 grep evidence; MF3 MISSING scope hedging; MF4 silent-failure `core/`-tree scope note | PRs #2775 + #2776 |
| S1302 | `1302_memory_persistence_architecture_audit.md` (Cat A+B+C) | SIGN-clean | 3 | Cycle 1: 3 `AgentKnowledgeSource` fields removed from orphan (`source_spider_names` / `first_discovered_at` / `feedback_adjusted_confidence`); Cycle 2: 4 `AgentMemory` fields removed (`source_type` / `source_id` / `access_count` / `last_accessed_at` consumed by Memory Palace); Cycle 3: `poison_risk_*` reclassified as narrow-consumer-safety-filter. Final F2: 5 strict-orphan + 2 narrow-safety-filter (down from v1's ~11). | PR #2777 (`c053272a`) |
| S1303 | `1303_memory_conversational_thread_memory_audit.md` (Cat F) | SIGN-clean | 2 | 12-edit fold: E1 maturity bounding; E2/E3 F3+D1 wrong-model+wrong-field widen; E4 F4 CANDIDATE rewrite; E5 R1.a/b/c split; E6 Cat F ↔ Cat D reframe as gap-not-defect; E7 Flow E fail-open nuance; E8 retire idempotency; E9+E10 metadata contract; E11 F7 gap-not-defect reframe; E12 §20.10 gating checklist | PR #2778 (`6365f33f`) |
| S1304 | `1304_memory_docs_rag_boundary_audit.md` (Cat E↔D) | SIGN-clean | 2 | 4-must-fix fold: D6 beat-schedule positive citation with 4-line dict quote; §18 UNOWNED reframed with Documentation Manager JobContract at `jobs.py:187-395`; F4-CANDIDATE discipline reinforced on `ingested_via`; §17 "complementary" reframe with "does not imply optimal" guardrail | PR #2779 (`4271e913`) |
| S1305 | `1305_memory_runtime_correctness_audit.md` (Cat H) | SIGN-clean | 2 | 3-must-fix fold: §3 + §14 D10 `cache.set(timeout=None)` scoping tightened with excluded-from-count table; §7.2 gap (a) reinforced with `get_user_memory:415` + `save_memory:476` + 0-hit invalidation grep; §14 D8 Django cache backend citation. Bonus: §19 R6 reshaped from "verify MemorySystem" (Rigby-answered yes) to "verify IntelligentJobMatcher production invocation" | PR #2780 (`4b6f3419`) |
| S1399 | `1399_memory_canonical_summary.md` (this doc) | Pending — route to Rigby with full SIGN + Q10-Q13 canonical-summary pressure-test | TBD | TBD | Pending Chris commit-gate |

### 11.2 Rigby SIGN cycle count evolution

Only child audit to reach SIGN-clean in **1 cycle**: S1301.
Children reaching SIGN-clean in **2 cycles**: S1303, S1304, S1305.
Child reaching SIGN-clean in **3 cycles**: S1302.

**Pattern observation.** The 2-cycle pattern reflects verifier-loop
pre-corrections landing parent-side before Rigby SIGN. S1303
established the pattern (Agent 6 overreaches caught pre-SIGN). S1304
extended it (broad hypothesis from S1301 §19 D3 caught pre-SIGN).
S1305 further extended to severity-correction (Agent 6 CRITICAL
downgraded to MEDIUM pre-SIGN via Redis AOF context).

### 11.3 Arc pin continuity

`pa-aa54193f240f4846` "Session 1300 — Memory research group
(kickoff)" carried Group 1300 continuity across all 6 sessions
(S1300 → S1301 → S1302 → S1303 → S1304 → S1305 → S1399). Fresh
SIGN isolation pins used for each child audit's Rigby SIGN cycles:

| Session | SIGN isolation pin | Retirement |
|---------|-------------------|------------|
| S1301 | `pa-a23736a833f646cf` | Retired at S1301 close |
| S1302 | `pa-1b9f0f5264484c6b` | Retired at S1302 close |
| S1303 | `pa-23a38300dd84bae2` | Retired at S1303 close |
| S1304 | `pa-2614a91a920642fa` | Retired at S1304 close |
| S1305 | `pa-56a527a2c5528508` | Retired at S1305 close (`updated_count: 2, retired: true`) |
| S1399 | Rigby offered fresh pin for canonical-summary SIGN | Retired at S1399 close per Chris directive |

Arc pin `pa-aa54193f240f4846` retires on arc close per OPEN_ARCS
schema.

### 11.4 Load-bearing methodology outputs of the arc

**Superseded by §10.** The three methodological patterns previously
enumerated here (F1/F4-CANDIDATE discipline; sibling-inheritance
hypothesis-correction; severity-correction via sibling context) are
now the load-bearing content of §10.2 "What to codify into playbook
v3." This subsection preserved as a pointer for backwards-compat
with external references to `§10.4` (e.g., OPEN_ARCS 2026-07-01
S1399 close reconciliation note; SESSION_1399 handoff `key_findings`).

See **§10.2** for the codification-target table with two-triggers
threshold status per pattern.

---

## 12. Appendix — Provenance

Per playbook §11.3 §12 template requirement.

### 12.1 Every child's file path

| Session | Path | Line count |
|---------|------|-----------|
| S1300 | `docs/research/domains/memory/1300_memory_domain_scoping.md` | — |
| S1301 | `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` | 1154 |
| S1301 follow-up | `docs/research/domains/memory/1301_followup_provenance_classifier_bug.md` | 276 |
| S1302 | `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md` | 1849 |
| S1303 | `docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md` | 1422 |
| S1304 | `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md` | 1150 |
| S1305 | `docs/research/domains/memory/1305_memory_runtime_correctness_audit.md` | 1079 |
| S1399 (this doc) | `docs/research/domains/memory/1399_memory_canonical_summary.md` | (draft) |

**Total.** 5 audits + 1 parent + 1 follow-up + this canonical
summary = 8 files under `docs/research/domains/memory/`.

### 12.2 Evidence provenance

Every claim in this summary cites its source-audit §-anchor via
`SNNNN §NN.N` notation. No file:line evidence introduced beyond
what children already established. Anchor coverage:

- S1300 parent: §3 category taxonomy; §5 P6 rationale; §6 anchor
  finding; §8 Chris-locked decisions D1-D5.
- S1301: §5-§7 (RAG lanes); §14.1-§14.3 (drift); §19 (routing).
- S1302: §4 (models); §14.1-§14.3 (drift F1-F6); §15 (T1-T12); §17
  (name collisions).
- S1303: §4 (ChatConversation); §7 (turn-history + retire); §14
  (F1-F10); §15 (D1-D6); §19 (R1-R8 including R1.a/b/c split).
- S1304: §7 (cascade + lanes); §14 (D1-D8); §17 (complementary
  reframe); §18 (Documentation Manager JobContract); §19 (R1-R8).
- S1305: §3 (LRU + cache.set enumeration); §7.2 (AgentLearningService
  gap); §14 (D1-D10); §15 (T1-T12); §19 (R1-R8).

### 12.3 Verifier-loop history

Preserved append-only per playbook §6 rule. Session frontmatter
`verifier_loop:` blocks in each child audit contain the full history
of parent-agent verifier-loop spot-checks + Rigby SIGN cycle folds.

This canonical summary's own `verifier_loop:` block (frontmatter
top of file) captures S1399-specific corrections: (v0.1) bootstrap
+ CANDIDATE preservation rule; (v0.2) Rigby launch-call bonus on
method + negative-evidence standard for dead-code claims.

### 12.4 What was NOT re-audited

Per playbook §11.3 bounded-work rule + parent §5 P6 scope:

- No new §13 6-parallel-Explore sweep launched.
- No new grep / file:line evidence produced.
- No CANDIDATE → CONFIRMED resolutions attempted.
- No Chris-locked decision D1-D5 re-litigation.
- Cat A/B/C internals owned by S1302 not re-inspected.
- Cat D internals owned by S1301 not re-inspected.
- Cat E internals or E↔D boundary owned by S1304 not re-inspected.
- Cat F owned by S1303 not re-inspected.
- Cat G delegated to Employee OS 1200s arc, not touched.
- Cat H owned by S1305 not re-inspected.

### 12.5 Rigby SIGN routing for this summary

Per playbook §15 stage table, canonical summaries require full SIGN
with the 4 additional pressure-test questions:

- **Q10** — Are all child contradictions correctly resolved? (See
  §5 above.)
- **Q11** — Are anchor-update recommendations complete? (See §7
  above.)
- **Q12** — Are cross-cutting patterns not missed? (F1-F4 named in
  §4 above — validated at S1305 close.)
- **Q13** — Are follow-on queue rankings defensible? (See §8.1
  above — uncertainty × risk × unblocked flows table.)

Rigby-offered fresh SIGN isolation pin for canonical-summary
pressure-test (per launch-call response). Continuity pin
`pa-aa54193f240f4846` remains for Chris-facing D19+D20 ratification
+ arc-close decisions.

### 12.6 Arc close criteria (per playbook §17 graduation)

- [x] All 5 child audits shipped + SIGN-clean + committed to `main`
- [x] Cross-cutting patterns named (F1-F4 in §4 above)
- [x] Consolidated domain shape delivered (§3 above)
- [x] Resolved contradictions surfaced (§5 above)
- [x] Unresolved unknowns documented (§6 above)
- [x] Anchor-update recommendations proposed (§7 above)
- [x] Follow-on queue ranked (§8 above)
- [x] Delegated arcs cross-linked (§9 above)
- [x] Meta-methodology retrospective delivered (§10 above — first application of the playbook §11.3 §10 template addition adopted at S1399 close per Chris directive)
- [x] Change log complete (§11 above)
- [x] Provenance appendix complete (§12 above)
- [x] Rigby SIGN Q10-Q13 pressure-test cleared (cycle 1 High confidence 0 must-fix via fresh isolation pin `pa-4fc3329d0db6484f`; pin retired at close per Chris directive)
- [x] Chris commit-gate per playbook §16 (PR #2781 = `6318787b` merged 2026-07-01)
- [x] Docs → RAG cascade executed post-merge (`build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` → `build_docs_provenance`; 8 unembedded docs found + embedded, ~667 chunks, ~$0.08; PR #2783 = `956727f3` merged 2026-07-01 with regenerated `docs/INDEX.md` + `docs/_provenance.json`)

**Arc closed 2026-07-01.** All 13 close criteria ticked (12 original per playbook §17 + 1 new "docs cascade executed" per Chris directive S1399 close 2026-07-01, memory rule `feedback_docs_cascade_at_every_close.md`).

---

*End of Group 1300 Memory / Knowledge / Embeddings canonical
summary. Arc closed 2026-07-01 (PR #2781 + #2782 + #2783 merged;
Rigby SIGN-clean cycle 1 High confidence; S1399 SIGN pin retired;
Group 1300 arc pin retirement deferred to next-session open per
`00-START-NEXT-SESSION.md` D22). Meta-methodology §10 retrofitted
per Chris directive; playbook §11.3 template updated same-commit.*

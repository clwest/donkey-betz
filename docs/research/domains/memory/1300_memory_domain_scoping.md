---
title: "S1300 Memory — Parent Architecture Scoping (Group 1300 mission plan)"
status: active (parent — Chris decisions locked 2026-07-01)
authority: parent-doc for Group 1300 research arc
session: 1300
date: 2026-07-01
decisions_locked: 2026-07-01
domain_slug: memory
research_group: 1300
authors: Claude Code (Chris directed)
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md              # process (S1274)
  - docs/research/platform_architecture_inventory.md §3.13 # Memory / Knowledge / Embeddings (S1273)
  - docs/research/platform_architecture_inventory.md §3.14 # RAG / Document Loading (S1273)
  - docs/research/platform_architecture_inventory.md §3.15 # Documentation / Research Knowledge System (S1273)
  - docs/research/platform_architecture_inventory.md §5.4  # Multiple Memory / Knowledge Stores overlap flag (S1273)
  - docs/research/platform/cross_domain_integration_audit.md # integration lens (S1274)
  - docs/narratives/KNOWLEDGE_RAG_MEMORY.md               # S1158 comprehensive narrative
  - docs/KNOWLEDGE_PIPELINE.md                             # flow map
scope: Phase 0 domain-definition — decide whether S1300 is a single canonical audit or a parent-with-children research arc
non_goals:
  - the audit itself (that begins after Chris picks parent-vs-single)
  - answering the 28 playbook questions (that is the audit's job)
  - resolving the excluded_missing_provenance RAG finding (parked — see §6)
  - any implementation proposal (this is scoping, not architecture design)
owner: claude (Chris directed at S1300 open)
---

# Session 1300 — Memory Domain Taxonomy Proposal (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any
> domain audit begins. Chris paused the standard `Start research
> group 1300: Memory` opening sequence to check whether "Memory" is
> one domain or a parent capability composed of multiple
> architectural subdomains. This doc answers that question, records
> the excluded_missing_provenance RAG finding as a candidate
> Knowledge Memory issue, and asks Chris to pick parent-with-children
> or single-audit before any audit work starts.
>
> **What this doc is not.** The audit itself. A design proposal. A
> recommendation about *how* memory should work. Everything here is
> evidence-grounded in existing inventory rows (S1273 §3.13, §3.14,
> §3.15, §5.4) and the S1274 playbook.

---

## 1. Why Phase 0

Chris's exact wording at S1300 open (after seeing the standard a-f
scope card):

> Pause before selecting a–f. Your clarification uncovered an
> architectural ambiguity rather than a simple scoping question.
> Treat this as a Phase 0 domain-definition exercise. Before
> beginning any Memory audit, determine whether "Memory" is a single
> domain or a parent capability composed of multiple architectural
> subdomains… Produce a short domain taxonomy proposal first.
> Recommend whether Research Group 1300 should become a parent
> architecture document with child research sessions, or remain a
> single audit.

The a-f scope card asked Chris to pick between (a) conversational
memory, (b) RAG/vector, (c) Employee OS mission memory, (d) Claude
Code auto-memory, (e) system RAM, (f) something else. That framing
assumed exactly one is correct. Chris's push-back rejects the
assumption — "Memory" in this platform reads more like a parent
capability, and Phase 0 must answer that structural question first.

The playbook (S1274 §2 rule 3) explicitly permits this:

> If the domain is bigger than expected, splitting into sub-groups
> is fine. Do not force a single session to cover a multi-subsystem
> domain.

---

## 2. What existing inventory already tells us

The S1273 platform inventory groups **three separate §3 rows** under
the "Knowledge & memory" cluster (S1273 §2, line 127):

| S1273 Row | Title | Coverage | Maturity |
|-----------|-------|----------|----------|
| §3.13 | Memory / Knowledge / Embeddings | DEEP inventory | STABLE core + PARTIAL edges |
| §3.14 | RAG / Document Loading | DEEP | STABLE prod + PARTIAL local |
| §3.15 | Documentation / Research Knowledge System | CANONICAL | STABLE |

That already tells us Memory is not a single row in the parent
inventory — it is a **3-row cluster** at the inventory anchor. Any
single audit that treats all three as one loses fidelity to the
anchor.

S1273 §5.4 ("Multiple Memory / Knowledge Stores") independently
flags the overlap concern:

> `AgentKnowledgeSource` (cross-agent knowledge from spider data).
> `AgentMemory` (episodic — success/failure/feedback/technique).
> `UserAgentLearning` (per-user preference adaptation).
> `ConversationMemory` (user-agent conversation history w/ pgvector).
> `MemoryPromotionService` auto-saved facts (writes to `AgentMemory`
> but with distinct scoring logic).
> **Two RAG lanes:** `core/rag_integration.py` (pgvector, prod) vs
> `core/rag.py` (keyword, local Ollama).
>
> Rigby's memory is unified with agent knowledge (no separate PA-only
> store per Agent 4 sweep) — but the split across 5+ tables is a
> cognitive-load surface.

So the platform's own inventory has already registered "memory" as a
multi-store overlap concern needing dedicated analysis. That is
independent evidence for parent-with-children shape.

---

## 3. Candidate subdomain taxonomy

The following categories are candidates for child audits under
Research Group 1300. Each row lists the primary systems in scope,
the S1273 inventory row it maps to (if any), and the drift already
flagged.

### A — Semantic Knowledge Memory (§3.13 subset)

- **Systems:** `AgentKnowledgeSource`, `EmbeddingService`,
  `LearningBridge` migration (9 bridges S1115), spider →
  knowledge → agent prompt injection path.
- **Anchor:** S1273 §3.13.
- **Known drift:** no versioning on `AgentKnowledgeSource`;
  mutations untracked; opt-in embedding generation → risk of DB row
  without embedding.

### B — Personal / Adaptive Memory (§3.13 subset)

- **Systems:** `UserAgentLearning`, `AgentLearningService`,
  `ConversationMemory` (per-user history + pgvector), per-user Redis
  preference models.
- **Anchor:** S1273 §3.13.
- **Known drift:** Redis-only state → worker recycle can lose
  recent learning; 14-day freshness window hardcoded in
  `ConversationOrchestrator`; per-user learning maturity PARTIAL
  (live but no A/B data on behavioural impact).

### C — Agent Working Memory (§3.13 subset)

- **Systems:** `AgentMemory` (episodic), `MemoryPromotionService`
  (score-gated auto-save from PA turns), `FeedbackLoopEngine`
  (PA-to-Agent feedback closure S990).
- **Anchor:** S1273 §3.13.
- **Known drift:** `MemoryPromotionService` scoring criteria opaque
  (EXPERIMENTAL maturity); consumer of
  `spider_context['pa_content_feedback']` **UNKNOWN** (open in
  KNOWLEDGE_RAG_MEMORY.md §6).

### D — RAG / Document Retrieval (§3.14)

- **Systems:** `core/rag_integration.py` (pgvector prod),
  `core/rag.py` (local Ollama keyword), `Document`,
  `DocumentEmbedding`, HNSW index, `ScopedRetrievalService`,
  `RAGObservabilityService`, `search_docs` PA tool, provenance
  filter mechanics.
- **Anchor:** S1273 §3.14 + S1273 §5.4 (2-lane concern).
- **Known drift / debt:** 2-module confusion (rag vs
  rag_integration); local Ollama keyword-only quality delta;
  `search_docs` `lru_cache(1)` per-process → workers need restart
  after `build_docs_provenance`; embedding cadence UNKNOWN.
- **Live symptom:** S1300 opening turn — 8 candidate chunks pre-filter
  → 7 `excluded_missing_provenance` + 1 `excluded_mismatch` → 0
  returned (see §6).

### E — Documentation / Research Knowledge System (§3.15)

- **Systems:** `docs/` corpus governance, `build_docs_index`,
  `sync_docs_index_to_documents`, `verify_doc_claims` registry,
  `_index.json`, research library, DOC_LIFECYCLE.md discipline
  (inventory-wins-on-conflict).
- **Anchor:** S1273 §3.15.
- **Coverage:** already CANONICAL — this may need less audit and
  more integration-lens (how does the docs corpus become RAG-visible?
  that is the D↔E boundary).

### F — Conversational / Thread Memory (no direct S1273 §3 row)

- **Systems:** `ConversationSession`, PA session pin identity,
  `session_tool.create_fresh` carry-forward semantics, tool-call
  history reinjection into subsequent turns, pin rotation policy
  (retire vs continue heuristics), PA `unified_pa_entrypoint`
  enrichment pipeline.
- **Anchor:** none in S1273 §3.x directly. Referenced obliquely in
  Employee OS row (§4) and Agent System row (§3.2).
- **Known drift:** stale-thread dispatcher waste (Session 1212
  deliverable 777d9cd8 — ~$3.60/day on retired-thread dispatches);
  `session_tool.retire` action does not exist; retire = stop using +
  repin.
- **Gap:** this domain has NO inventory row of its own. If child
  audit runs, it will be the first inventory pass.

### G — Mission / Execution Memory (Employee OS domain — NOT §3.13)

- **Systems:** `OpsRun(domain='mission')`, `OpsRunEvent` audit rows,
  `MissionRunner` orchestrator, `JobContract.authority` +
  execution history, `AIEmployee` handle registry.
- **Anchor:** S1273 §4 (Employee OS), NOT §3.13. Also touched by
  S1275 event schema design.
- **Boundary call:** This is architecturally "memory" (state persisted
  across mission runs, cross-session), but the inventory homes it
  under Employee OS. Two options for S1300:
  - (i) Include as a child audit under Group 1300 — inclusive
    definition of "memory as anything persisting cross-session";
    RISK: overlaps with Employee OS follow-on research already
    named for 1200s range.
  - (ii) Explicitly delegate to Employee OS group 1200s follow-up —
    respects inventory boundary; Group 1300 stays knowledge-store
    flavored.
- **Recommendation:** (ii) delegate. Reason: keeps Group 1300
  scope tight; Employee OS group already has this material half-
  scoped via S1275. Cross-link only.

### H — Runtime / Cache Memory (no direct §3 row, ops-flavored)

- **Systems:** Redis embedding cache (7-day TTL),
  `AgentLearningService` Redis preference models,
  `search_docs` `lru_cache(1)`, in-process memoization surfaces.
- **Anchor:** referenced in §3.13 drift bullets; no dedicated row.
- **Boundary call:** ambiguous whether this is "architecture" or
  "infrastructure." Redis-loss-on-recycle IS an architectural drift
  (state model assumes persistence Redis doesn't guarantee);
  `lru_cache` staleness IS a memory-correctness issue.
- **Recommendation:** include a narrow child audit focused on
  **memory-correctness drift** (Redis-loss + lru staleness), not on
  Redis-ops-in-general. Ops-flavored questions (Celery worker RSS,
  PID cache, OOM) explicitly out of scope (see §7).

### Explicit non-candidates

- **System RAM / OOM handling (macOS SIGSEGV, Celery pool recycle,
  PublishGate memory pressure)** — ops-flavored, not architectural
  memory. Out of Group 1300.
- **Claude Code auto-memory (`~/.claude` MEMORY.md + topic files)** —
  Claude-side tooling, external to DBZ platform architecture. Out
  of Group 1300.

---

## 4. Parent-vs-single recommendation

**Recommendation: parent architecture doc with child research
sessions.**

Evidence for parent-with-children:

1. **Inventory anchor already treats Memory as a 3-row cluster**
   (S1273 §3.13 + §3.14 + §3.15). A single audit collapses that
   fidelity.
2. **S1273 §5.4 already flags "Multiple Memory / Knowledge Stores"
   as an overlap concern** — that overlap map alone is a full
   audit's worth of work; if buried inside a single Memory audit,
   it will not get proper enumeration.
3. **§F (conversational / thread memory) has no §3 inventory row**
   — a child audit is the right vehicle to add it, cite the parent
   for the taxonomy, and land a new §3.N row.
4. **Two RAG lanes need call-time selector research** (playbook §12
   §3.13 note): that is a well-defined child mission on its own.
5. **Playbook §2 rule 3 explicitly permits sub-grouping.**
6. **Playbook §12 queue lists Memory as one line for scheduling
   simplicity** — that is a queue-slot convenience, not a semantic
   claim that only one file should exist.

Evidence for single-audit (weaker):

1. Playbook §3 says "Every domain audit produces exactly one
   canonical file" — but this is a per-audit rule; a parent doc
   plus N children is N+1 audits, each following the rule.
2. §12 lists Memory as one queue slot. Counter: §2 rule 3 overrides
   this when the domain is bigger than the row suggests.

**Verdict: parent-with-children.**

---

## 5. Child mission sequence (Chris-locked 2026-07-01)

Under the parent, the following child audits are the locked plan
for Group 1300. Order is default; Chris can re-sequence between
missions. Each child is its own session ID within the 1300s range.

| Slot | Session ID | Child audit | Priority rationale |
|------|-----------|-------------|-------------------|
| P0 | S1300 | **Parent** — this doc (Phase 0 taxonomy + arc plan) | Foundation |
| P1 | S1301 | **RAG Retrieval Lanes** (Category D) | Live symptom today; S1273 named 2-lane selector as top research need; lands excluded_missing_provenance finding parked under §6 |
| P2 | S1302 | **Memory Persistence Architecture** (Categories A + B + C — the §3.13 subsets + §5.4 overlap) | Where does what memory live, with what durability, on what write/read paths, and where do stores overlap semantically. Renamed from "Store Overlap Audit" per Chris 2026-07-01 — the underlying question is persistence + authority, not just overlap surfacing. |
| P3 | S1303 | **Conversational / Thread Memory** (Category F) | No inventory row exists; child audit establishes the missing §3.N row |
| P4 | S1304 | **Documentation Corpus ↔ RAG Boundary** (E ↔ D) | Integration lens between §3.15 and §3.14; smaller scope; benefits from §3.14 audit landing first |
| P5 | S1305 | **Runtime Memory Correctness** (Category H — narrow scope) | Redis-loss + lru staleness only; not ops-in-general |
| P6 | **S1399** | **Group 1300 Canonical Summary** (Chris directive 2026-07-01) | Cross-cutting synthesis of P1-P5 findings; consolidated memory subsystem shape; anchor-update recommendations for `PLATFORM_INVENTORY.md` §3.13/§3.14/§3.15 + new row for Category F; follow-on research queue |
| Delegated | — | **Mission / Execution Memory** (Category G) | Delegated to Employee OS group 1200s follow-up (Chris confirmed 2026-07-01); parent doc cross-links via §7 anti-scope |

**Arc rhythm.** Group 1300 spans **S1300 → S1305 + S1399** = seven
sessions total (one parent + 5 child audits + 1 canonical summary).
That matches the S1268-S1275 architectural research library rhythm
(roughly one research doc per session).

**S1399 slot rationale.** Chris directive at 2026-07-01: "Plan for a
1399 canonical summary once the 1300-series research is complete."
The summary is *not* a re-audit — it is the cross-cutting synthesis
that makes the arc navigable as a single memory-architecture
picture. Deliverables the S1399 summary should produce:

1. Cross-cutting patterns discovered across P1–P5 (e.g.,
   provenance-filter drift class, if it recurs across categories).
2. Consolidated memory-subsystem shape — a single map showing all
   memory surfaces, their durability tier, and their authority
   boundaries.
3. `PLATFORM_INVENTORY.md` §3 update recommendations:
   - §3.13 subdivision (if warranted by P2 findings)
   - §3.14 lane consolidation (if warranted by P1 findings)
   - New §3.N row for Category F (if P3 lands the row)
4. Follow-on research queue — what did the arc *not* answer that
   deserves later attention.
5. Cross-link back to Employee OS group 1200s Mission Memory
   audit — the boundary the parent doc explicitly delegated.

The S1399 canonical summary is bounded work — it consumes P1-P5
outputs, it does not re-open scope.

---

## 6. Parked candidate issue — RAG provenance filter (Category D)

**Finding.** At S1300 open, Rigby ran `search_docs` twice against
OpsRun / MissionRunner / JobContract terms. Both calls returned:

```
result_count: 0
filter:
  originating_session: 0
  pre_filter_count: 8       # 8 candidate chunks semantically matched
  excluded_mismatch: 1       # 1 dropped for originating_session mismatch
  excluded_missing_provenance: 7  # 7 dropped for missing provenance
```

Net: the corpus **does** contain semantically relevant material, but
retrieval provenance filters exclude 100% of it. This is not
pursued in this Phase 0 exercise. It is captured here as a
**candidate finding for the S1301 RAG Retrieval Lanes child audit
(Category D)**. The audit questions it should answer:

1. What triggers `excluded_missing_provenance`? Is provenance metadata
   populated at ingestion or synthesized at query time?
2. What triggers `excluded_mismatch` on `originating_session`? Is
   the session filter meant to exclude cross-session material by
   default?
3. Is this the same class of issue as the S1142 chunk-coverage gap
   (852 / 14,149 chunks — S1273 §3.13 known drift)?
4. Under what queries does the platform silently return 0 results
   despite semantic matches existing? What is the operator-facing
   error surface?
5. How does the two-lane split (§5.4) affect this? Does
   `core/rag.py` local lane have the same provenance filter?

If Chris picks single-audit instead of parent-with-children, this
finding folds into that single audit's §14 drift section.

---

## 7. Anti-scope for Research Group 1300

Explicitly out of scope for the entire Group 1300 (even under
parent-with-children):

- **System RAM behavior** (Celery worker RSS, PID cache,
  `OBJC_DISABLE_INITIALIZE_FORK_SAFETY`, macOS SIGSEGV playbook,
  worker recycle policies). Ops topic.
- **Claude Code auto-memory** (`~/.claude` MEMORY.md + topic files).
  External to platform.
- **Employee OS Mission Memory** (Category G — OpsRun/MissionRunner
  execution audit trail). Delegated to Employee OS group 1200s
  follow-up per §3 recommendation.
- **New memory model proposals.** This is architecture research.
  New model proposals require a separate PR after the audit lands,
  gated by `EMPLOYEE_OS_PRIMITIVES.md` anti-duplication matrix.
- **Implementation PRs.** Everything Group 1300 produces is design
  research. No `core/models*.py` diffs.

---

## 8. Decisions recorded (Chris-locked 2026-07-01)

| # | Decision | Verdict | Recorded |
|---|----------|---------|----------|
| 1 | Parent-vs-single | **A. Parent-with-children** | 2026-07-01 |
| 2 | Category G (Mission Memory) boundary | **Delegated to Employee OS arc** — cross-linked in §7 anti-scope; not part of Group 1300 | 2026-07-01 |
| 3 | RAG provenance-filter finding routing | **Parked under §6 as S1301 input** — not pursued in Phase 0 | 2026-07-01 |
| 4 | Rename of P2 slot | **"Memory Persistence Architecture"** — replaces "Memory Store Overlap Audit" per Chris directive; wider frame captures durability + authority, not just overlap surfacing | 2026-07-01 |
| 5 | Group 1300 arc closure | **S1399 canonical summary** planned — cross-cutting synthesis of P1-P5 findings; anchor-update recommendations; follow-on queue | 2026-07-01 |

**Open decisions still needed** (do not block Phase 0 close, but
required before S1301 launch):

| # | Question | Options | Default lean |
|---|----------|---------|--------------|
| 6 | S1301 launch cadence | (i) immediate — Claude begins S1301 RAG lanes audit next; (ii) pause — Chris reviews parent doc, then greenlights S1301 in a later session | (ii) pause — parent doc is fresh material; Chris review before P1 kickoff protects against sequencing regret |
| 7 | Rigby SIGN routing for parent doc | (i) skip — parent doc is a scoping deliverable, not an audit; SIGN attaches per child audit under playbook §9; (ii) light SIGN — Rigby pressure-tests the taxonomy boundaries + P1-P5 sequence before P1 kickoff | (i) skip — playbook §9 attaches SIGN to audits, this is scoping |

---

## 9. Next step

**Parent doc status is now `active`.** Group 1300 arc is:

```
S1300 (parent, this doc)
  → S1301 RAG Retrieval Lanes
  → S1302 Memory Persistence Architecture
  → S1303 Conversational / Thread Memory
  → S1304 Documentation Corpus ↔ RAG Boundary
  → S1305 Runtime Memory Correctness
  → S1399 Group 1300 Canonical Summary
```

Category G (Mission / Execution Memory) is delegated to the
Employee OS 1200s follow-up arc.

**Immediate next actions** (pending answers on Decisions 6 + 7):

1. Confirm S1301 launch cadence (immediate vs pause).
2. Confirm Rigby SIGN routing (skip vs light).
3. If S1301 launches next: begin playbook §11 opening sequence
   against `1301_memory_rag_retrieval_lanes_audit.md`, feeding the
   §6 provenance-filter finding as an S1301 input.
4. Register the parent doc in `ARCHITECTURE_INDEX.md` (bump v7 →
   v8) after Chris confirms.
5. Commit gating: per playbook §10, no commit to `main` until
   Chris asks. This doc lives on the working tree in `docs/research/
   domains/memory/` until commit approval.

---

## Appendix — Frontmatter provenance

Sources cited by file:line in this document:

- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` — process,
  §2 sub-group rule, §3 file layout, §11 opening sequence.
- `docs/research/platform_architecture_inventory.md` §3.13 —
  Memory / Knowledge / Embeddings deep row (lines 1073–1198).
- `docs/research/platform_architecture_inventory.md` §3.14 — RAG /
  Document Loading (lines 1199–1249).
- `docs/research/platform_architecture_inventory.md` §3.15 — Docs
  Research Knowledge System (lines 1250+).
- `docs/research/platform_architecture_inventory.md` §5.4 —
  Multiple Memory / Knowledge Stores overlap flag (lines 2657–2672).
- Live: Rigby `search_docs` call at S1300 open — 8 → 0 excluded via
  provenance filter (captured §6).

No claim in this doc is asserted without an S1273 line reference or
a live-tool citation. Where boundaries are called (e.g., "Category
G delegate to Employee OS"), the boundary is explicit and
overridable.

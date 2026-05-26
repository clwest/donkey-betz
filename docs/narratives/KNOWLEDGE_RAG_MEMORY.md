---
title: "Knowledge + RAG + Memory — narrative (batch H)"
status: draft (batch H of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/local-askdocs.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/narratives/PERSONAL_ASSISTANT.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to local-askdocs topic doc, AGENTS.md Knowledge Pipeline section, named handoff files Sessions 400/786/930/990/991/1108/1109/1142)
provenance_note: The platform's memory has three distinct surfaces — knowledge accumulated by agents (AgentKnowledgeSource), per-user / per-agent learning (AgentLearningService), and conversational / operational memory (AgentMemory + MemoryPromotionService). Plus two RAG paths: production (`core.rag_integration` + pgvector) and local Ollama (`core.rag` + .rag/corpus.jsonl). This narrative covers all five together because they share consumers and the boundaries are operationally fuzzy. Counts anchored to PLATFORM_INVENTORY 2026-05-25.
---

# Knowledge + RAG + Memory

> Five distinct memory surfaces, two RAG paths, one
> documentation narrative. The platform's "what does it know?"
> answer is not one system — it's a knowledge pipeline
> (spider data → embeddings → bridges → AgentKnowledgeSource),
> a per-user learning loop (AgentLearningService), an agent
> memory store (AgentMemory + MemoryPromotion), a production
> RAG path (pgvector + Document table), and a local-only
> developer convenience (Ollama askdocs). This doc covers all
> five and explicitly names where the boundaries sit.

---

## 1. What this is

The platform persists three categories of "memory" plus two
retrieval mechanisms.

**Memory categories:**
1. **Agent knowledge** — what an agent has learned from its
   own past executions, surfaced via `AgentKnowledgeSource`
   and injected into every future prompt by `BaseAgent._build_prompt()`
   (Session 400 knowledge pipeline; covered in narrative A
   milestone 1).
2. **Per-user, per-agent learning** — Redis-cached preference
   models built from every `route()` call by
   `AgentLearningService` (Session 991). Surfaces as
   `user_context['agent_learned_preferences']`.
3. **Conversational + operational memory** — `AgentMemory`
   rows (memory_type ∈ {success, failure, feedback, ...}),
   plus `MemoryPromotionService` that auto-saves "ops facts"
   per PA execution with tags and scores. Visible in worker
   logs as `Memory promotion AUTO-SAVED id=N score=N tags=[...]`.

**Retrieval mechanisms (RAG paths):**
1. **Production RAG (`core.rag_integration`)** — pgvector
   `unified_embeddings` table populated from the `Document`
   model (which holds chunked `/docs/` corpus + other
   sources), embedded via `EmbeddingService`
   (`text-embedding-3-small`, Redis-cached). Used by PA
   enrichment, agent retrieval, knowledge views, ~13
   production files.
2. **Local Ollama askdocs (`core.rag`)** — `.rag/corpus.jsonl`
   flat-file corpus (gitignored), keyword scoring only, no
   embeddings, local Ollama model only. Sessions 1108–1109.
   Developer convenience for offline doc Q&A; **never** used
   by production code.

**Recent PA-facing additions:**
- `kb_tool` — PA tool browsing the `Document` table.
- `search_docs` (Session 1142) — chunked retrieval with
  inline citations over `.rag/corpus.jsonl` + Document
  table (852 / 14,149 chunks at Session 1142).

The two RAG paths are **completely independent**. `core.rag`
and `core.rag_integration` are distinct modules with non-
overlapping consumers. Changes to one have no effect on the
other. This is the most common confusion in the corpus.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`AgentKnowledgeSource`** | The knowledge-pipeline row. Carries learned material from a specific source agent (e.g., ResearchAgent learned a fact about AI trends) with title, summary, knowledge_type, confidence, and `spider_sources` provenance. Injected into every future agent prompt via `BaseAgent._build_prompt()`. |
| **Knowledge pipeline** | `Spider Data → Embeddings → Learning Bridge → AgentKnowledgeSource → Agent Prompts`. The pipeline Session 400 established. Covered in narrative A milestone 1. |
| **`_get_relevant_knowledge_for_task(task, limit=5)`** | The `BaseAgent` method that pulls knowledge relevant to the current task. Returns `[{source_agent, title, summary, knowledge_type, confidence, spider_sources}]` rows. Filtered to a 14-day freshness window (Session 988). |
| **`_get_fresh_spider_intelligence(categories, hours=24, limit=5)`** | Companion method for category-filtered fresh spider data. Returns `[{source, category, titles, item_count, relevance, timestamp}]`. Used alongside `_get_relevant_knowledge_for_task` in the prompt builder. |
| **14-day knowledge freshness window (Session 988)** | `_get_agent_knowledge()` in `ConversationOrchestrator` filters knowledge to a 14-day window. Plus prompt-level bans: no "Notion spider", no "Notion data", no dates older than 30 days as evidence, no references to 2023 or 2024 data. Prevents agents grounding on stale records. |
| **`AgentLearningService`** | `core/services/agent_learning_service.py`. Records every `route()` execution via `record_interaction()`. Builds per-user, per-agent preference models in Redis. `_get_user_context()` injects `user_context['agent_learned_preferences']`; `gather_context()` surfaces it into `spider_context['agent_learned_preferences']`. Session 991. |
| **`AgentMemory`** | The episodic memory model. `memory_type` ∈ {`success`, `failure`, `feedback`, `pa_review`, ...}, `tags`, `valence` (positive / negative / neutral). The "thing happened" log. |
| **`UserAgentLearning`** | Per-user, per-agent training row. `record_success()` on PA publish, `record_failure()` on PA archive. Powers personalization for content agents. |
| **`FeedbackLoopEngine`** | The connector. `get_feedback_for_agent()` queries recent PA reviews and produces `pa_review_feedback` + `pa_review_summary` for the agent's next execution context. Session 990 wired this end-to-end. |
| **`MemoryPromotionService`** | The "ops fact" autosaver. On every PA execution, candidate facts (with scores and tags) get auto-saved. Visible in PA worker logs as `Memory promotion AUTO-SAVED id=N score=N tags=[...]`. The platform's way of remembering what just happened without a human deciding what to capture. |
| **`Document` table** | The chunked-corpus store in `core.models`. Holds /docs/ chunks + other sources. Has embeddings for the production RAG path. Browseable via PA's `kb_tool`. |
| **`unified_embeddings`** | The pgvector table that holds production embeddings. Used by `core.rag_integration` for retrieval. |
| **`EmbeddingService`** | The production embedder. OpenAI `text-embedding-3-small` (1536 dim). Redis-cached. The only embedder used by production retrieval. |
| **`core.rag_integration`** | The **production** RAG module. Uses pgvector + `Document` table + `EmbeddingService`. Touches OpenAI. ~13 production-file consumers. |
| **`core.rag`** | The **local-only Ollama** RAG module. Uses `.rag/corpus.jsonl` (flat file, no embeddings, keyword scoring). Touches Ollama only. Two consumers: `python manage.py askdocs` and `core/ask_with_docs.py`. |
| **`.rag/corpus.jsonl`** | The local RAG corpus. Gitignored as of Session 1109. One JSON object per line: `{"file": "...", "chunk_id": N, "text": "..."}`. Regenerated via `python manage.py build_rag_corpus`. |
| **`sync_docs_index_to_documents`** | Mgmt command that populates the `Document` table from `docs/_index.json`. `--embed` flag triggers embedding generation via `EmbeddingService`. The production path. |
| **`build_rag_corpus`** | Mgmt command that builds `.rag/corpus.jsonl` from `docs/_index.json`. Sessions 1108–1109. Local-only. |
| **`kb_tool`** | PA tool. Browses the `Document` table. Production RAG path. |
| **`search_docs` (Session 1142)** | PA tool. Chunked retrieval with inline citations over `.rag/corpus.jsonl` + `Document` table. 852 / 14,149 chunks indexed at session close. Adds the `originating_session` filter (memory rule: `lru_cache(1)` per process; restart workers after corpus regen). |
| **PA worker memory-cache restart rule** | After `build_docs_provenance` or corpus changes, restart celery workers. `search_docs` and `kb_tool` cache filter results per process; stale workers serve stale results. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — embeddings + Document table** *(early sessions, Inferred + Session 786 archive ref)* | The `Document` model and basic pgvector embedding infrastructure introduced. Initial pipeline ingested specific curated docs (per archived Session 786 — "curated docs embedding pipeline"). Embeddings via OpenAI `text-embedding-3-small`, stored in pgvector with HNSW index. | The platform needed semantic retrieval before it could reason over its own knowledge. Embeddings were the unblock for everything downstream — RAG, signal clustering, knowledge injection. | Production retrieval foundation in place. Document table exists; embeddings flow; pgvector indices serve cosine-similarity queries. | **Active** — `Document` + `unified_embeddings` are the production retrieval foundation. | `docs/archive/handoffs-pre-800/SESSION_786_CURATED_DOCS_EMBEDDING_PIPELINE.md`; `core/services/embedding_service.py` |
| **Session 400 — Knowledge Pipeline (Spider → Bridges → AgentKnowledgeSource → Prompts)** | The full chain: spider data → embeddings → learning bridges → `AgentKnowledgeSource` rows → automatic injection into every agent prompt via `BaseAgent._build_prompt()`. `_get_relevant_knowledge_for_task(task, limit=5)` and `_get_fresh_spider_intelligence(categories, hours=24, limit=5)` introduced as the canonical retrieval helpers. Learning hooks: `self._record_learning_outcome(result, task, context)`, `self._create_execution_memory(result, task, memory_type='success')`, `self._share_knowledge(...)`. | The spider network was producing data; agents weren't using what other agents had learned. Without a knowledge layer, every agent run started from scratch. The pipeline made cross-agent knowledge cumulative. | Every agent inherits the prompt-injection path. Adding a new agent gives it access to the full knowledge graph automatically. Cross-ref narrative A milestone 1. | **Active** — the knowledge pipeline is the standard data flow. | `docs/AGENTS.md` §"Agent Knowledge Pipeline (Session 400)"; `core/agents/base_agent.py`; cross-ref `docs/narratives/AGENTS_AND_AUTONOMY.md` milestone 1 |
| **Session 988 — Knowledge freshness window + 2023-data ban** | `_get_agent_knowledge()` in `ConversationOrchestrator` filters `AgentKnowledgeSource` and `AgentMemory` to a 14-day window. Prompt-level bans added: "Notion spider", "Notion data", data collection dates, dataset sizes; citing dates older than 30 days as evidence; any reference to 2023 or 2024 data. | Agents were citing stale Notion records from 2023 — knowledge they had genuinely learned, but that was no longer current. The 14-day window enforced freshness at the retrieval site; the prompt-level bans backstopped at the generation site. | Stale data no longer reaches the model. Cross-ref narrative A milestone 4 (provenance & truth controls) and narrative B milestone 5 (truth controls). | **Active** — the 14-day filter and the bans are both standard. | `docs/topics/agent-system.md` §"Agent Knowledge & Conversations (Session 988)" |
| **Session 990 — PA-to-Agent feedback loop (closing the loop)** | When the PA publishes / archives / revises agent-created content, the decision now records back to the originating agent. (1) `AgentMemory` with `memory_type='feedback'`, `tags=['pa_review']`, valence mapped from action. Surfaced to agents via `_get_agent_knowledge()` in multi-agent conversations. (2) `UserAgentLearning.record_success()` on publish, `record_failure()` on archive. (3) `FeedbackLoopEngine.get_feedback_for_agent()` queries recent PA reviews → `pa_review_feedback` + `pa_review_summary` added to feedback context. (4) `gather_context()` extracts `pa_content_feedback` and `pa_review_summary` into `spider_context`. Data flow: `PA action → _record_content_feedback() → AgentMemory + UserAgentLearning → FeedbackLoopEngine → agent_router.gather_context() → spider_context`. | Agents were generating content; humans were judging it via the PA; the agents weren't learning from the judgment. The learning loop was open at the human end. Session 990 closed it. | PA review decisions are first-class context for every subsequent agent execution. The PA's "archive this blog" call results in the originating agent's prompt next time saying "the PA archived a similar blog with valence -1." | **Active** — wiring is end-to-end. Open question on whether the PA's prompt actually surfaces the feedback at the writer's prompt-builder layer (covered in narrative B Open Question § 6). | `docs/topics/content-pipeline.md` §"PA-to-Agent Content Feedback (Session 990)"; cross-ref `docs/narratives/CONTENT_PIPELINE.md` milestone 5 |
| **Session 991 — AgentLearningService (per-user preference models in Redis)** | `core/services/agent_learning_service.py` introduced. `record_interaction()` called on every agent `route()`. Per-user, per-agent preference models built in Redis. `_get_user_context()` injects the adaptive context string into `user_context['agent_learned_preferences']`; `gather_context()` surfaces it into `spider_context['agent_learned_preferences']`. | The user-context layer (Session 858, narrative A milestone 2) gave agents access to a user's stated preferences. But the platform had no way to observe revealed preferences — what the user actually responded well to, vs what they said they wanted. The learning service records every interaction and adapts. | Per-user / per-agent learning is now automatic. Adaptive context strings reach the agent's prompt without explicit user input. Lives in Redis (per-process learning state). | **Active** — the service is part of `gather_context()`. | `docs/topics/agent-system.md` §"Context Injection (12 Layers)" → "AgentLearningService" reference |
| **Sessions 1108–1109 — Local Ollama askdocs lane** | `core.rag` introduced as a developer convenience. `.rag/corpus.jsonl` flat-file corpus regenerated via `python manage.py build_rag_corpus`. `python manage.py askdocs "<question>"` mgmt command. Uses Ollama at `http://127.0.0.1:11434/v1/chat/completions` with `qwen2.5:14b-instruct` by default. Session 1109 made `.rag/` gitignored — the two former artifacts (`corpus.jsonl`, `embedding_refs.txt`) were removed from the index in PR 2 of the Option B plan. Local working copies preserved on disk and regenerated on demand. | OpenAI quota was sometimes exhausted; developers needed a way to query the docs corpus offline. The local Ollama lane gave them one without polluting the production pipeline. Critical discipline: the two RAG modules (`core.rag` and `core.rag_integration`) are completely independent — changes to one have no effect on the other. | Offline doc Q&A works. Production RAG unaffected. Local artifact is gitignored; regenerable at any time. | **Active** — `core.rag` is the local convenience; production code never touches it. | `docs/topics/local-askdocs.md` (the dedicated topic doc) |
| **MemoryPromotionService — auto-saving ops facts per PA execution** *(date Unknown — observed in worker logs)* | On every PA execution, candidate "ops facts" are extracted from the conversation context and auto-saved as memory rows with scores and tags. Visible in worker logs as `Memory promotion AUTO-SAVED id=N score=N tags=[...]`. Example tags: `['deploy', 'release', 'mobile', 'repo', 'infra']`. | The PA generates a lot of useful context per conversation that would otherwise be lost between turns. Auto-promotion captures the high-signal moments without requiring a human to decide what to save. Score gates which facts persist. | The platform accumulates conversational knowledge automatically. The memory layer grows even when no one is explicitly creating memory rows. | **Active** — observed in current production PA worker logs. | `core/services/memory_promotion_service.py`; PA worker log `Memory promotion AUTO-SAVED` entries |
| **Session 1142 — `search_docs` PA tool + chunked retrieval + threading.Lock** | New PA tool `search_docs` over `.rag/corpus.jsonl` + the `Document` table. Chunked retrieval (852 / 14,149 chunks indexed at session close) with inline citations. Adds the `originating_session` filter — `lru_cache(1)` per process (memory rule: restart workers after `build_docs_provenance` regen). Same session also added `threading.Lock` on `get_unified_pa()` (concurrency-safe init). Plus advisor rename (25 legendary → 30 functional). Disk audit 18 GB → 8.7 GB. | The PA needed a way to answer "where is this documented?" with cited chunks, not document IDs. `kb_tool` covered the browse case but not the search case. `search_docs` made citation-grounded answers the standard. The threading lock closed a class of init race observed in production logs. | The PA can answer doc questions with citations. Init races resolved. Disk usage halved as a side benefit of the corpus regen. | **Active** — `search_docs` is part of the canonical PA tool set. Cross-ref narrative D milestone 8. | `docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md`; PR #2178; MEMORY.md `project_session_1142_docs_hygiene_and_search_docs.md` |

---

## 4. What came of it

### Wins

- **Cross-agent knowledge is cumulative.** Every agent
  inherits `_get_relevant_knowledge_for_task` via
  `BaseAgent`; new agents get knowledge access for free.
  Session 400 is still the foundation.
- **Per-user adaptation is automatic.** Session 991's
  `AgentLearningService` builds preference models from
  observed interactions without requiring explicit user
  configuration.
- **Stale data doesn't reach the model.** 14-day freshness
  window + prompt-level bans (Session 988) closed the
  "agent cites 2023 Notion data" class of bug.
- **The learning loop is closed.** PA review decisions
  (publish / archive / revise) record back to the
  originating agent (Session 990). Agents learn from their
  own published-or-archived history.
- **Citation-grounded doc answers.** `search_docs` (Session
  1142) means PA answers about /docs/ carry chunk citations
  instead of "I think it's in some doc somewhere."
- **The two RAG paths don't bleed.** `core.rag` vs
  `core.rag_integration` is enforced by separate modules,
  separate consumers, and a topic doc that explicitly names
  the boundary. Local-only development won't ship to
  production.
- **MemoryPromotionService captures ops facts
  automatically.** No human in the loop deciding what's
  worth remembering.

### Tradeoffs

- **Two RAG paths is a real cognitive load.** Even with the
  explicit topic doc, new developers often confuse
  `core.rag` and `core.rag_integration`. The two names are
  similar; the consumers are not.
- **`search_docs` `originating_session` filter cache is
  `lru_cache(1)` per process.** After `build_docs_provenance`
  regen, every worker needs a restart. Memory rule:
  `feedback_celery_pid_cache_blocks_restart.md` covers the
  restart procedure. Silent footgun otherwise.
- **AgentLearningService state lives in Redis.** Per-process
  state. Worker recycling can lose recent learning if not
  promoted to durable storage.
- **MemoryPromotionService promotion criteria are
  opaque.** It auto-saves with scores and tags but the
  scoring logic isn't documented in any topic doc. Why a
  given fact got id=N with score=10 vs score=5 is not
  visible.
- **`Document` table chunk count drifts.** Session 1142
  reported 852 / 14,149 chunks indexed. *Unknown* current
  numbers — embedding backfill runs continuously; coverage
  is moving.
- **Local Ollama corpus is keyword-scored only.** No
  embeddings. Quality of retrieval is meaningfully lower
  than production. Developers should not benchmark
  production RAG quality against `askdocs` results.
- **14-day freshness window is hardcoded.** Adjusting it is
  a code change. Use cases with longer or shorter horizons
  must work around the constant.
- **Knowledge pipeline learning bridges all have their own
  contracts.** Session 1115 migrated 9 bridges to the
  `LearningBridge` ABC; the migration is recent and the
  pattern is still maturing.

### Follow-on systems enabled

- **Agent narrative (A)** — milestone 1 (knowledge pipeline)
  + milestone 4 (knowledge freshness) sit on top of this
  layer. Every agent uses `_get_relevant_knowledge_for_task`.
- **Content pipeline (B)** — `BlogPerformanceContextBuilder`
  + PA-to-Agent feedback loop both consume this layer's
  models.
- **PA (D)** — `kb_tool` + `search_docs` are the user-
  facing surfaces; `MemoryPromotionService` runs per-call
  to capture ops facts.
- **Signal Intelligence (C)** — `pgvector` semantic search
  (Session 1024) is part of the same embedding foundation;
  spider data and document data share embeddings
  infrastructure.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`). 585 concrete models;
> Knowledge pipeline live; `search_docs` + `kb_tool` are PA
> tools.

**Memory model categories.**
- `AgentKnowledgeSource` — accumulated agent knowledge.
- `AgentMemory` — episodic memory rows (success / failure /
  feedback / pa_review).
- `UserAgentLearning` — per-user per-agent training.
- `Document` — chunked corpus (/docs/ + other sources).
- `unified_embeddings` — pgvector embedding rows.

**Retrieval mechanisms.**
- **Production:** `core.rag_integration` →
  `unified_embeddings` (pgvector) → `EmbeddingService`
  (`text-embedding-3-small`, 1536 dim, Redis-cached) →
  semantic KNN.
- **Local Ollama:** `core.rag` → `.rag/corpus.jsonl`
  (gitignored, keyword scoring) → Ollama
  (`http://127.0.0.1:11434`, `qwen2.5:14b-instruct`).

**Retrieval helpers (in `BaseAgent`).**
- `_get_relevant_knowledge_for_task(task, limit=5)` —
  knowledge from `AgentKnowledgeSource` filtered to 14-day
  freshness.
- `_get_fresh_spider_intelligence(categories, hours=24,
  limit=5)` — fresh spider data by category.
- Auto-injected into every agent prompt via
  `_build_prompt()`.

**Learning services.**
- `AgentLearningService.record_interaction()` — every
  agent route() call (Session 991).
- `FeedbackLoopEngine.get_feedback_for_agent()` — recent
  PA reviews (Session 990).
- `MemoryPromotionService` — auto-saves ops facts per PA
  execution.

**PA tools.**
- `kb_tool` — browses `Document` table (production RAG).
- `search_docs` — chunked retrieval w/ inline citations
  (Session 1142).

**Management commands.**
- `python manage.py sync_docs_index_to_documents [--embed]`
  — production: populates `Document` table from
  `docs/_index.json`.
- `python manage.py build_rag_corpus` — local: builds
  `.rag/corpus.jsonl`.
- `python manage.py askdocs "<question>"` — local: query
  via Ollama.
- `python manage.py build_docs_provenance` — regenerates
  `docs/_provenance.json`. After running, restart celery
  workers (`search_docs`'s `originating_session` filter
  cache is per process).

**Knowledge freshness.** 14-day window in
`ConversationOrchestrator._get_agent_knowledge()`. Plus
prompt-level bans on stale data citations (Session 988).

**Embeddings cadence.** Backfill task
(`backfill_spider_embeddings`) every 10 min, batch 500.
Coverage ~85 % for spider data; `Document` coverage moving.

**Where to look when something stops working.**
- Agent cites stale data → 14-day window failed; check
  `_get_agent_knowledge()` filter.
- PA `search_docs` returns nothing for a known doc →
  corpus is stale; regenerate `.rag/corpus.jsonl` via
  `build_rag_corpus`, then **restart celery workers**.
- `kb_tool` returns nothing → `Document` table doesn't
  have the source; run
  `sync_docs_index_to_documents --embed`.
- `AgentLearningService` learning preferences not applied
  → Redis-side state; check the right user / agent key
  exists; worker recycling may have lost recent state.
- `MemoryPromotionService` not auto-saving → check PA
  worker log for `Memory promotion AUTO-SAVED` lines; if
  absent, the promotion path may be silently broken.
- PA-to-Agent feedback not reaching the agent's prompt →
  check the data flow (`PA action → AgentMemory +
  UserAgentLearning → FeedbackLoopEngine →
  gather_context() → spider_context`); the consumer
  agent's prompt-builder may not be reading
  `spider_context['pa_content_feedback']` (open question
  in narrative B § 6).
- Two RAG modules confusion → if you're touching
  `.rag/corpus.jsonl`, you're in the **local** path. If
  you're touching `Document` or `unified_embeddings`,
  you're in the **production** path. They do not share
  state.

---

## 6. Open questions / unknown outcomes

- **Current `Document` chunk coverage.** *Known:* Session
  1142 reported 852 / 14,149 chunks indexed.
  *Unknown:* current numbers. `Document.objects.count()`
  + a coverage query against the underlying source file
  count would answer.
- **`MemoryPromotionService` scoring criteria.** *Known:*
  facts are auto-saved with scores. *Unknown:* the scoring
  function. Why a given fact got score=10 vs score=5 is
  not documented in any topic doc; would need to read
  `core/services/memory_promotion_service.py` to enumerate.
- **`AgentLearningService` learning-preference quality.**
  *Known:* per-user, per-agent preference models built in
  Redis. *Unknown:* whether the preferences materially
  affect agent behavior in measurable ways. No A/B test
  is in the corpus.
- **Date of `MemoryPromotionService` introduction.**
  *Known:* it's in production (worker logs).
  *Unknown:* the originating session. `git log -S
  "MemoryPromotionService"` would surface it.
- **`AgentMemory` schema details.** *Known:* `memory_type`,
  `tags`, `valence`. *Unknown:* full field list and which
  consumers read which fields. Topic doc reference doesn't
  enumerate.
- **PA-to-Agent feedback consumer at the writer end.**
  *Known:* `spider_context['pa_content_feedback']` is
  populated. *Unknown:* whether ContentWriterAgent's
  parallel prompt-builder (narrative B footgun) reads
  this. The data is there; the consumer may not be wired.
- **Production RAG embedding coverage.** *Known:* ~85 %
  spider data coverage. *Unknown:* `Document` table
  coverage. Embedding backfill task runs every 10 min for
  spider data; cadence for documents not documented.
- **14-day freshness window calibration.** *Known:* the
  number is hardcoded. *Inferred:* picked when most data
  sources had week-to-monthly cadence. *Unknown:* whether
  some sources warrant a longer window (legal docs, SEC
  filings, evergreen content).
- **`core.rag_integration` consumer list.** *Known:* topic
  doc says "~13 production files." *Unknown:* the exact
  list. A `grep -r "from core.rag_integration"` would
  surface.

---

## 7. Source index

### Primary doc sources

- `docs/topics/local-askdocs.md` — the dedicated local
  Ollama RAG topic doc. Explicitly names the production-vs-
  local boundary.
- `docs/AGENTS.md` §"Agent Knowledge Pipeline (Session 400)"
  — knowledge pipeline overview.
- `docs/topics/agent-system.md` §"Agent Knowledge &
  Conversations (Session 988)" — freshness window + bans.
- `docs/topics/content-pipeline.md` §"PA-to-Agent Content
  Feedback (Session 990)" — feedback loop closure.
- `docs/PLATFORM_INVENTORY.md` — counts.

### Named session handoffs cited above

- `docs/archive/handoffs-pre-800/SESSION_786_CURATED_DOCS_EMBEDDING_PIPELINE.md`
  — foundational embedding pipeline (archived).
- Session 400 — Knowledge Pipeline (referenced; handoff
  filename in archive series).
- Session 988 — knowledge freshness + 2023-data ban.
- Session 990 — PA-to-Agent feedback closure.
- Session 991 — `AgentLearningService` per-user Redis
  preferences.
- Sessions 1108 / 1109 — local Ollama askdocs lane.
- `docs/handoffs/SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md`
  — `search_docs` PA tool + threading.Lock + advisor
  rename.

### Code anchors

- `core/services/agent_learning_service.py` —
  `AgentLearningService.record_interaction()`,
  per-user/agent Redis models.
- `core/services/embedding_service.py` —
  `EmbeddingService` (OpenAI `text-embedding-3-small`).
- `core/services/memory_promotion_service.py` —
  `MemoryPromotionService` (auto-save ops facts).
- `core/services/feedback_loop_engine.py` —
  `FeedbackLoopEngine.get_feedback_for_agent()`.
- `core/conversation_orchestrator.py` —
  `_get_agent_knowledge()` 14-day filter.
- `core/agents/base_agent.py` —
  `_get_relevant_knowledge_for_task`,
  `_get_fresh_spider_intelligence`.
- `core.rag_integration` (production path).
- `core/rag.py` (local-only path).
- `core/ask_with_docs.py` — local Ollama caller.
- `core/management/commands/sync_docs_index_to_documents.py`
  — production ingestion.
- `core/management/commands/build_rag_corpus.py` — local
  corpus builder.
- `core/management/commands/askdocs.py` — local Ollama
  query.
- `core/management/commands/build_docs_provenance.py` —
  provenance index (Session 1145; relevant to
  `search_docs` filter cache).
- `core.models` — `AgentMemory`, `UserAgentLearning`,
  `Document`, `unified_embeddings`.

### Verification commands

- `python manage.py generate_platform_inventory` —
  regenerate inventory.
- `python manage.py sync_docs_index_to_documents --embed` —
  refresh production RAG.
- `python manage.py build_rag_corpus` — refresh local
  Ollama corpus.
- `python manage.py askdocs "<question>"` — query local
  corpus (Ollama required).
- After `build_docs_provenance` regen:
  `pkill -9 -f celery; rm -f .celery*.pid; make celery` —
  worker restart so `search_docs` filter cache picks up
  new data.

---
title: "S1302 Memory Persistence Architecture — Categories A + B + C Architecture Audit"
status: draft
authority: research
sign_status: SIGN-clean (Rigby cycle 3, 2026-07-01, fresh pin pa-1b9f0f5264484c6b)
session_added: 1302
research_group: 1300
child_slot: P2
domain_slug: memory
date: 2026-07-01
last_verified: 2026-07-01
supersedes: none
related:
  - docs/research/domains/memory/1300_memory_domain_scoping.md        # parent (P0) — locks A+B+C scope
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md  # sibling (P1, Cat D) — inherits §14.3 D3 evidence
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                          # process
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                 # OS
  - docs/research/platform_architecture_inventory.md                    # §3.13 + §5.4 anchor
  - docs/research/platform/cross_domain_integration_audit.md            # S1274 integration lens
  - docs/narratives/KNOWLEDGE_RAG_MEMORY.md                             # S1158 comprehensive narrative
  - docs/KNOWLEDGE_PIPELINE.md                                          # runtime flow map
  - docs/topics/personal-assistant.md                                   # PA + enrichment context
  - docs/topics/agent-system.md                                         # 12-layer context injection reference
  - docs/handoffs/SESSION_990_PA_CONTENT_FEEDBACK_LOOP.md               # Cat C feedback-loop origin
  - docs/handoffs/SESSION_991_PROACTIVE_INTELLIGENCE_AGENT_LEARNING_WIRING.md  # Cat B AgentLearningService wiring
  - docs/handoffs/SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md             # LearningBridge 9-bridge cascade
  - docs/handoffs/SESSION_1158_CORPUS_NARRATIVE_PROGRAM.md              # KNOWLEDGE_RAG_MEMORY authoring
companion_anchors:
  - docs/PLATFORM_INVENTORY.md                                          # runtime anchor (counts)
  - docs/PLATFORM_WHAT_IT_IS.md                                         # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md                                      # anti-duplication matrix
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                 # inventory-wins-on-conflict
dependencies_on:
  - group: 1300
    slug: memory
    role: parent scoping — locks Categories A + B + C as this child's exclusive scope; renames the audit's central concern from "Store Overlap" (original P2 wording) to "Persistence Architecture" (Chris directive 2026-07-01) to widen the frame from surface-level overlap to durability + write/read paths + authority boundaries
  - group: 1300
    slug: memory
    role: sibling S1301 §14.3 D3 anchor — DocumentEmbedding row-level provenance fields populated at ingestion but never read by any retrieval query; the "orphan write path" pattern is inherited as first-order S1302 scope
delegates_to:
  - none
delegated_from:
  - group: 1300
    slug: memory
    scope: |
      Categories A + B + C per S1300 parent §5 P2 slot.
      - Cat A — Semantic Knowledge Memory: AgentKnowledgeSource (core/models_unified_system.py:521), EmbeddingService, LearningBridge migration cascade (9 bridges S1115), spider → knowledge → agent prompt injection path.
      - Cat B — Personal / Adaptive Memory: UserAgentLearning (core/models_unified_system.py:3912), AgentLearningService (core/services/agent_learning_service.py:122), ConversationMemory (core/models/conversations/models.py:19 — Django model with per-user pgvector), per-user Redis preference models.
      - Cat C — Agent Working Memory: AgentMemory (core/models_unified_system.py:10787), MemoryPromotionService (core/services/memory_promotion_service.py:119), FeedbackLoopEngine (core/services/feedback_loop_engine.py:26).
verifier_loop: |
  v1.3 (2026-07-01, S1302 Rigby SIGN cycle 3 fold + final verdict): same fresh isolation pin pa-1b9f0f5264484c6b. **Rigby cycle 3 verdict: SIGN-clean.** Overall confidence: High. One non-blocking residual folded: MF8 — AgentMemory.poison_risk_score + .poison_risk_factors reclassified from orphan → NARROW-CONSUMER-SURFACE (safety filter consumed at core/services/memory_embedding_service.py:222 via getattr + :261 via queryset.exclude(poison_risk_score__gte=0.5)); §14.3 F2 + §17.5 Cat C bullets softened with safety-consumer note. Rigby also cycle 3 grep re-verified UserAgentLearning.context_metadata + UserAgentLearning.last_used + ConversationMemory.intent all = 0 hits on the specific models (all stand). Post-fold classification: 5 strict-orphan fields + 2 narrow-consumer-safety-filter fields = 7 fields under F2 pattern (down from v1's ~11). Playbook §16 next step: Chris commit-gate → status: draft → active on merge. Ratification path per playbook §16 mirrors S1301 pattern.

  v1.2 (2026-07-01, S1302 Rigby SIGN cycle 2 fold): same fresh isolation pin pa-1b9f0f5264484c6b. Rigby cycle 2 verdict SIGN-with-edits (fold more, localized) — cycle 1 folds accepted; residual correction: AgentMemory.source_type + .source_id + .access_count + .last_accessed_at are NOT orphan (all four consumed by core/views_memory_palace.py). Parent-agent folded:
  - MF4 (§14.3 F2 second narrowing) FOLDED — removed AgentMemory.source_type + .source_id + .access_count + .last_accessed_at from orphan list with explicit reader citations (views_memory_palace.py:60/86/113-114 + models_unified_system.py:11000-11001). Revised orphan count: ~6 fields, down from cycle 1's ~9 and v1's ~11.
  - MF5 (§14.3 F2 methodology tightening) FOLDED — language updated from "0 consumers" to "no explicit-qualified references found on the model" per Rigby's epistemic-hedge requirement; audit cannot exhaustively exclude unqualified .field references on variables bound to the model at runtime without AST tracing.
  - MF6 (§17.5 Cat C row-level) FOLDED — bullet narrowed to poison_risk_score + poison_risk_factors only.
  - MF7 (§15 T8) FOLDED — T8 entry marked REMOVED (source_id consumed by Memory Palace).
  Rigby also RE-VERIFIED in cycle 2: UserAgentLearning.context_metadata disambiguation grep = 0 hits (STANDS with hedge); ConversationMemory.intent grep = 0 hits on the Django model specifically (STANDS). F6 spider_data_bridge → UserAgentLearning target now VERIFIED in-pin. Cycle 3 pending — will re-route for SIGN-clean confirmation after this fold lands.

  v1.1 (2026-07-01, S1302 Rigby SIGN cycle 1 fold): fresh isolation pin pa-1b9f0f5264484c6b (title "S1302 SIGN — Memory Persistence Architecture audit pressure-test (isolation)"; owner chris; ownership match confirmed). Rigby SIGN cycle 1 provisional verdict SIGN-with-edits — F2 orphan-fields claim overstated (Rigby grep-verified active readers on 3 of the ~11 originally-listed fields: AgentKnowledgeSource.source_spider_names + first_discovered_at + feedback_adjusted_confidence). F6 write target flagged UNVERIFIED-in-pin due to repo_tool time cap. Parent-agent folded:
  - MF1 (§14.3 F2 narrowing) FOLDED — removed source_spider_names + first_discovered_at + feedback_adjusted_confidence from orphan list with explicit reader citations; §14.5 pattern 1 recontextualized; §17.5 Cat A row-level bullet narrowed; §15 T2 narrowed to feedback_positive/_negative + downgraded MEDIUM → LOW.
  - MF2 (§14.3 F5 + F6 spider_data_bridge target) VERIFIED via parent-agent direct read of core/learning_bridges/spider_data_bridge.py:240 — `UserAgentLearning.objects.get_or_create(...)` confirms bridge writes Cat B (UserAgentLearning) not Cat A (AgentKnowledgeSource). §20.7 receipt added.
  - Additional Rigby observations (non-blocking) — EmbeddingService end-to-end trace expansion deferred to S1399; intentional-vs-accidental §9.1 framing already handled via "Agent 4 grep 0 hits" annotation matching S1301 pattern; T10 riskiest-finding vote confirmed already-ranked HIGH.

  v1 (2026-07-01, S1302 synthesis): audit doc synthesized from playbook §13 6-parallel Explore sweep. Categories A + B + C scope locked by parent §5 P2 (Chris-ratified 2026-07-01). Chris ratified D8 (immediate launch, cadence: PROCEED) + D9 (arc pin RETAIN pa-aa54193f240f4846) at S1302 open, routed via Rigby per Rigby-first comms.

  Sweep composition:
  - Agent 1 Models & Persistence — inventoried AgentKnowledgeSource (core/models_unified_system.py:521-628); UserAgentLearning (:3912-4120); AgentMemory (:10787-11100); ConversationMemory (core/models/conversations/models.py:19-56); FK graph across categories; migration lineage; retention/lifecycle. Parent-agent resolved Agent 1's "MemoryPromotionService location unknown" claim against Agent 2 — verified service exists at core/services/memory_promotion_service.py:119, :197 via direct grep (2 hits for class-and-function definitions).
  - Agent 2 Services & Runtime Flows — traced write flows + read flows for A/B/C; located 14-day freshness at core/conversation_orchestrator.py:749 (Session 988 origin — comment at :747-748); MemoryPromotionService scoring logic at core/services/memory_promotion_service.py:119-172 (regex-only deterministic; thresholds hardcoded at :234, :237).
  - Agent 3 APIs/Tools/Tasks/Commands — enumerated 5 PA tools touching A/B/C (remember_tool, conversation_tool, learning_tool, feedback_tool, db_health_tool); 2 promotion beat tasks; 4 management commands; 10+ REST endpoints across /api/memory/ and /api/user-learning/. Cross-referenced PLATFORM_INVENTORY autoblock.
  - Agent 4 Integrations — mapped inbound + outbound per category; verified STRONG Cat A → BaseAgent prompt injection (core/agent_router.py:769-776); STRONG Cat A → UserAgentLearning bridge (core/learning_bridges/spider_data_bridge.py:107-111); UNKNOWN Cat C consumer of pa_content_feedback (see verifier-loop §14.3 F1 below).
  - Agent 5 Docs & Prior Research — mapped topic docs, narratives, handoffs; extracted S1301 cite-not-re-answer boundary (§17.1 DocumentEmbedding vs AgentKnowledgeSource verdict; §17.2 DocumentEmbedding vs UserEmbedding verdict — S1302 does not re-answer either); documented 10 UNKNOWNs from KNOWLEDGE_RAG_MEMORY.md §6.
  - Agent 6 Drift/Debt/Ownership/Maturity — verified all 5 parent §3 known drift bullets; produced 10-item debt matrix; classified maturity per category (A: PARTIAL; B: PARTIAL; C: EXPERIMENTAL); surfaced 4 cross-category drift patterns (orphan write paths, hardcoded configuration, Redis coupling without durable fallback, producer-only data).

  Parent-agent verifier-loop spot-checks (direct file reads before including load-bearing claims):
  - core/agent_router.py:766 — pa_content_feedback producer: CONFIRMED verbatim. Only producer.
  - Whole-tree grep of `pa_content_feedback` including ai_core/ subtree: 15 hits total; 1 code producer (agent_router.py:766); 14 doc references (topic docs, handoffs, narratives, parent scoping, S1273 inventory). Zero code consumers across core/ AND ai_core/. F1 finding (§14.3) escalates from "parent §3 says UNKNOWN" to CONFIRMED dead code.
  - core/conversation_orchestrator.py:749 — 14-day freshness_cutoff: CONFIRMED verbatim (`freshness_cutoff = tz.now() - timedelta(days=14)`); comment at :747-748 attributes to Session 988. Hardcoded magic number; not env var or setting.
  - core/services/memory_promotion_service.py:119, :197 — MemoryPromotionService definitions: CONFIRMED (score_for_promotion at :119; check_and_promote at :197). Resolves Agent 1 vs Agent 2 conflict against Agent 2.
  - core/services/agent_learning_service.py:462, :476 — save_memory redis_client.hset: CONFIRMED Redis-only write path (hset to preferences hash; no DB writeback call). Parent §3B "Redis-only state" bullet confirmed.
  - core/models_unified_system.py:521, :3912, :10787 — model file:line: CONFIRMED for AgentKnowledgeSource, UserAgentLearning, AgentMemory. Agent 6's line ranges accepted.
  - core/models/conversations/models.py:19 vs core/conversation_memory.py:59 — ConversationMemory disambiguation: two DIFFERENT constructs share the name. `core/models/conversations/models.py:19` is the Django model (Cat B pgvector); `core/conversation_memory.py:59` is a service-layer Python class (different concern). Sub-agents referenced both; audit distinguishes.

  Rigby SIGN routing: pending. Playbook §15 requires full SIGN on child audits — will route to a fresh isolation pin (not pa-aa54193f240f4846 the arc pin) after Chris review of this draft. Fold cycle per §16 before considering canonical.
owner: claude (drafted S1302)
---

# S1302 Memory Persistence Architecture — Categories A + B + C Architecture Audit

> **What this is.** The second child audit under Research Group 1300
> (Memory / Knowledge / Embeddings). Scope = Categories A + B + C
> from the S1300 parent scoping doc: Semantic Knowledge Memory,
> Personal / Adaptive Memory, and Agent Working Memory. This audit
> answers the 28 canonical playbook questions (§9) for the
> combined A + B + C persistence surface. The central question is
> not "do these stores overlap" (that was the original P2 framing);
> it is "where does what memory live, with what durability, on
> what write/read paths, and where is write authority enforced?"
>
> **What this is not.** A design proposal. An implementation plan.
> An audit of Category D — that is S1301 (already merged on `main`).
> An audit of Categories E/F/H — those are S1304/S1303/S1305. Category
> G (Mission / Execution Memory) is delegated to the Employee OS
> 1200s follow-up arc per parent §7 anti-scope.
>
> **How to read.** §1 Executive Summary tells you what shipped and
> what remains open. §14 (Known Drift) is the finding backbone —
> five of the parent §3 known-drift bullets verified plus one
> escalated from UNKNOWN to dead-code confirmed. §7 (Runtime
> Flows) is the mechanism map: write path + read path per category.
> §18 (Ownership Gaps) answers the authority-boundary question
> that drove the P2 rename to "Persistence Architecture." §19
> queues the next arcs — S1303, S1304, S1399.

---

## 1. Executive Summary

Categories A + B + C together form the Donkey Betz **memory
persistence surface** — the durable-and-semi-durable stores that
carry semantic knowledge, per-user adaptation, and agent working
memory across sessions. They share the model `Agent` as an FK
anchor, they share the vector-embedding infrastructure
(`EmbeddingService`), and they share the same platform-level
authority question the P2 rename made explicit: *who is allowed
to write into each store, and how is that enforced?* The audit's
answer, category by category, is largely **unrestricted at the
model layer, gated by convention at the service layer, and
unmeasurable by observability.**

**Six subsystems are in scope, spread across three durability
tiers.** Category A (Semantic Knowledge Memory) is Postgres-durable
via `AgentKnowledgeSource`
(`core/models_unified_system.py:521-628`) with embeddings written
by `EmbeddingService` (`core/services/embedding_service.py:66-414`,
413 lines) and a 7-day Redis cache. Category B (Personal /
Adaptive Memory) splits across two durability tiers — durable
`UserAgentLearning` (`core/models_unified_system.py:3912-4120`) +
durable pgvector `ConversationMemory`
(`core/models/conversations/models.py:19-56`), plus **Redis-only**
per-user preference state in `AgentLearningService`
(`core/services/agent_learning_service.py:122-758`, 795 lines).
Category C (Agent Working Memory) is Postgres-durable via
`AgentMemory` (`core/models_unified_system.py:10787-11100`), written
via `MemoryPromotionService`
(`core/services/memory_promotion_service.py:119-338`,
score-gated) and consumed via `FeedbackLoopEngine`
(`core/services/feedback_loop_engine.py:26-618`).

**The subsystem verdict is PARTIAL for A + B and EXPERIMENTAL for
C.** Category A works end-to-end for spider → knowledge → prompt
injection (verified STRONG at `core/agent_router.py:769-776`) but
has no versioning on `AgentKnowledgeSource` mutations, and the
feedback fields (`feedback_positive`, `feedback_negative`) are
populated with no consumer. Category B has a working Postgres
side (`UserAgentLearning` with `learning_source` actively filtered
at `core/services/td_handlers_ops.py:5965, 5986, 6000`) plus a
Redis-only side (`AgentLearningService.save_memory` at
`core/services/agent_learning_service.py:462-483` writes via
`redis_client.hset` at line 476 with no DB backup) — worker recycle
drops the Redis-only half. Category C has a deterministic scoring
gate at `score_for_promotion` (`core/services/memory_promotion_service.py:119-172`)
with hardcoded thresholds (≥7 auto-save, 5-6 pending, ≤4 ignore;
lines 234, 237). Its scoring criteria are documented (see §14) but
not configurable.

**The single biggest finding is that the parent §3 "consumer of
`spider_context['pa_content_feedback']` UNKNOWN" bullet is not
UNKNOWN — it is confirmed dead code.** Whole-tree grep across `core/`
+ `ai_core/` finds exactly one producer
(`core/agent_router.py:766`) and zero code consumers. The other
14 grep hits are documentation describing the intended consumer
(e.g., PLATFORM_INVENTORY §3.13, KNOWLEDGE_RAG_MEMORY §6,
platform_architecture_inventory §3120) — an intent that never
became code. Session 990 wired the producer half of a PA-to-agent
feedback loop that no agent consumes. The loop is broken at
step 4.

**Three cross-category drift patterns** repeat across A + B + C
(§14.5): (a) orphan write paths — audit / provenance / tracking
fields populated at write time, never read (narrower field list
after Rigby SIGN cycles 1 + 2 fold — 7 fields removed across
two cycles after Rigby grep-verified active readers on
AgentKnowledgeSource.source_spider_names / first_discovered_at /
feedback_adjusted_confidence [cycle 1] + AgentMemory.source_type /
source_id / access_count / last_accessed_at [cycle 2]; ~6 fields
remain confirmed orphan per "no explicit-qualified references
found on the model" methodology; F2 row and §17.5 updated with
revised list); (b)
hardcoded configuration — freshness windows, score thresholds,
safety gates all magic numbers; (c) Redis coupling without
durable fallback — B's Redis preferences and A's embedding
cache both accept loss-on-recycle without a documented recovery
path. S1301 §14.3 D3's "two provenance systems, no bridge"
pattern recurs three times inside A + B + C alone (§17.2,
§17.3, §17.4).

**Recommended next research** (§19): the row-level orphan-write
pattern needs a design-preparation doc after S1399 synthesis;
S1303 (Conversational / Thread Memory, Category F) should own
the `ConversationSession` ↔ `ConversationMemory` boundary since
the F child audit will surface an inventory row that A/B/C
currently borrow; Group 1700 Observability owns the
producer-only dead-code detection surface. The write-authority
gap (§18) is a **design-preparation candidate**, not an
implementation task — this audit surfaces it, S1399 or a
follow-up ADR proposes a shape.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** Categories A + B + C form
the *state-carrying* half of the memory subsystem — the surfaces
that let the platform accumulate cumulative agent knowledge
across sessions (A), adapt to individual user behavior over time
(B), and remember specific episodic outcomes for later feedback
(C). Category A is the substrate for prompt-time knowledge
injection at `core/agents/base_agent.py:1435-1510` and
`core/conversation_orchestrator.py:752-755`. Category B is the
substrate for per-user preference adaptation via
`core/services/agent_learning_service.py:512-549`
(`get_adaptive_context`) and per-user conversation history via
`core/personal_ai_orchestrator.py:158-166`. Category C is the
substrate for the PA-to-agent feedback loop
(`docs/handoffs/SESSION_990_PA_CONTENT_FEEDBACK_LOOP.md`), the
score-gated auto-save of "ops facts" from PA turns
(`core/services/memory_promotion_service.py:197-338`), and
long-lived episodic memories with safety-class gating
(`core/models_unified_system.py:10787-11100`).

**Q2 — What does it NOT do?** It does not do retrieval-augmented
generation over the docs corpus — that is Category D, owned by
S1301. It does not do event/audit logs of platform actions — that
is Employee OS `OpsRun`/`OpsRunEvent` (Category G, delegated to
the 1200s arc). It does not do Redis-as-cache for API responses —
that is infrastructure/ops. It does not do session-thread state
(`ConversationSession` identity, pin rotation, PA turn context
carry-forward) — that is Category F, owned by S1303. And it
does not do runtime process memory correctness (worker RSS,
PID cache, macOS SIGSEGV) — that is Category H, owned by S1305.

---

## 3. Canonical Entry Points

**Q3 — Where does execution start for each category?**

| Category | Primary entry | file:line | Role |
|----------|--------------|-----------|-----|
| A | `AgentKnowledgeSource.objects.create/get_or_create` | `core/models_unified_system.py:521` (model); write callers verified at `core/services/implementation_executor.py:428, :443`, `core/management/commands/sync_agent_learning.py:457` | Knowledge row creation from decision outcomes + sync jobs |
| A | `BaseAgent._get_relevant_knowledge_for_task` | `core/agents/base_agent.py:1435-1510` | Prompt-time knowledge pull (cosine similarity via pgvector) |
| A | `EmbeddingService.create_embedding` | `core/services/embedding_service.py:66-414` | Singleton service wrapping all OpenAI embedding calls with 7-day Redis cache |
| B | `UserAgentLearning.create_learning` classmethod | `core/models_unified_system.py:4122` | Durable per-user learning row creation |
| B | `AgentLearningService.record_interaction` | `core/services/agent_learning_service.py:169-213` | In-process + Redis learning capture from every agent execution |
| B | `AgentLearningService.get_adaptive_context` | `core/services/agent_learning_service.py:512-549` | Per-user preference injection into prompts |
| B | `ConversationMemory.objects.create` (Django model) | `core/models/conversations/models.py:19-56` (schema); write caller at `core/personal_ai_orchestrator.py:421` | Per-user conversation history persistence (pgvector-eligible) |
| B | `ConversationOrchestrator._get_agent_knowledge` | `core/conversation_orchestrator.py:725-768` | Cross-category read gate — pulls both AgentKnowledgeSource (A) AND AgentMemory (C) with hardcoded 14-day freshness window at :749 |
| C | `AgentMemory.create_memory` classmethod | `core/models_unified_system.py:11004` | Episodic memory row creation |
| C | `MemoryPromotionService.check_and_promote` | `core/services/memory_promotion_service.py:197-338` | Score-gated auto-save from PA turns |
| C | `MemoryPromotionService.score_for_promotion` | `core/services/memory_promotion_service.py:119-172` | Regex-only deterministic scoring (+3 milestone, +2×N identifiers max +6, +2 wiring, -10 secret) |
| C | `FeedbackLoopEngine.get_feedback_for_agent` | `core/services/feedback_loop_engine.py:87-214` | Retrieval of AgentMemory-flagged `pa_review` rows for feedback injection |

**No REST or WebSocket entry point owns primary A/B/C write
authority.** The `/api/memory/*` and `/api/user-learning/*`
endpoints (enumerated in §6) are secondary — the primary writers
are agents (A), the AgentLearningService in-process cycle (B),
and PA turn processing (C).

---

## 4. Major Models

**Q4 — What Django models does this domain own?**

### 4.A Category A — Semantic Knowledge Memory

**`AgentKnowledgeSource`** — `core/models_unified_system.py:521-628`

- FK: `agent` → `Agent`.
- Fields: `title`, `summary`, `knowledge_type`, `knowledge_value`
  (JSON), `confidence`, `spider_sources` (ArrayField),
  `source_spider_names` (ArrayField), `embedding` (VectorField,
  1536D, nullable), `first_discovered_at` (auto_now_add),
  `last_updated_at` (auto_now), `feedback_adjusted_confidence`
  (nullable float), `feedback_positive` (int), `feedback_negative`
  (int).
- **No `created_by` / `updated_by` / version field.** Mutations are
  invisible post-hoc. Confirmed by Agent 6 direct read of
  `core/models_unified_system.py:521-628`.
- **`source_spider_names` populated but never queried.** Agent 1
  grep across `core/**/*.py` for `source_spider_names` filter/get
  returned 0 hits (migration files excluded).
- **`feedback_positive/negative/feedback_adjusted_confidence`
  populated by `apply_feedback()` but never read by any retrieval
  or prompt-builder path.** No consumer grep hits.

**`AgentInteraction`** (in-process, not persisted) —
`core/services/agent_learning_service.py:111-120` — dataclass
representing a single agent interaction; buffered in the service
before Redis persistence. **Not a Django model.** Named `AgentMemory`
in the same file (`:111`) internally, which is a NAME COLLISION
with the Cat C Django model. Disambiguation matters — the Django
`AgentMemory` is at `core/models_unified_system.py:10787`; the
in-process one is a service-layer construct.

### 4.B Category B — Personal / Adaptive Memory

**`UserAgentLearning`** — `core/models_unified_system.py:3912-4120`

- Extends `UnifiedBaseModel`.
- FK: `user` → user model.
- Fields include `learning_source` (enum CharField —
  `success_pattern`, `failure_analysis`, `performance_tracking`,
  `user_feedback`, `explicit_instruction`, `interaction_mining`),
  `learning_domain`, `learning_content`, `confidence_score`,
  `validation_count`, `context_metadata` (JSONField), `last_used`
  (DateTimeField, nullable), `expires_at` (DateTimeField, nullable).
- **`learning_source` ACTIVELY READ** — 3 filter clauses at
  `core/services/td_handlers_ops.py:5965, 5986, 6000` (Agent 1
  grep receipts). This is the exception to the orphan-write
  pattern in Category B.
- **`context_metadata` populated, never deserialized in retrieval
  path.** Agent 1 + Agent 6 grep confirmed.
- **`last_used` populated by `record_success/failure`, no
  consumer.** Agent 6 confirmed 0 consumer grep hits.
- **`expires_at` field exists but retention is not enforced** by
  any beat task or query filter. Agent 6 classified as
  `dead_code`.

**`ConversationMemory`** — `core/models/conversations/models.py:19-56`

- Django model. FK: `user` → user model; FK: `conversation` →
  `ChatConversation`.
- Fields: `content`, `intent` (CharField), `embedding`
  (VectorField or JSONField depending on `HAS_PGVECTOR`), `created_at`.
- **NAME COLLISION with `core/conversation_memory.py:59`** (an
  in-process Python class, not a Django model). Both classes are
  named `ConversationMemory`; only the Django model is the Category B
  durable store.
- No retention/lifecycle field; no provenance fields; no
  `updated_by` / audit trail. `intent` populated at create,
  no downstream use confirmed.

**Redis-only per-user preferences** — no Django model. Stored in
Redis db=5 with `REDIS_PREFIX = "agent_learning"` at
`core/services/agent_learning_service.py:139`. Key patterns:
`agent_learning:interactions:{user_id}:{agent_name}` (sorted set
via `zadd`, kept as last 100 via `zremrangebyrank`),
`agent_learning:preferences:{user_id}:{agent_name}` (hash via
`hset`, written by `save_memory` at `:476`). **No TTL / expire
call issued** on these keys (Agent 1 confirmed grep for `setex`
returned 0 hits in the service).

### 4.C Category C — Agent Working Memory

**`AgentMemory`** — `core/models_unified_system.py:10787-11100`

- FK: `agent` → `Agent`. **No FK to user** — memory is
  agent-scoped, not per-user-scoped.
- Fields: `memory_type` (enum), `title`, `content`, `tags`
  (ArrayField), `valence` (JSONField), `importance_score`,
  `source_type` (CharField, blank), `source_id` (CharField,
  blank), `safety_class` (CharField, indexed), `poison_risk_score`
  (float), `poison_risk_factors` (JSONField), `access_count`
  (PositiveIntegerField), `last_accessed_at`, `created_at`.
- Optional `embedding` (VectorField) added by migration 0160
  (Session 730); write is opt-in.
- **`source_type` / `source_id` populated on create, never read
  by any consumer.** Agent 1 + Agent 6 grep confirmed. Classified
  as `drift` (populated-but-unread).
- **`safety_class` IS enforced** — gates embedding generation at
  line 11041-11042 (`if safety_class == 'approved'`).
- **`poison_risk_score` scored at create, never re-analyzed
  post-creation.** No dashboard consumer.
- **`access_count` / `last_accessed_at` populated by
  `record_access()`, no consumer.** Access telemetry captured
  but not surfaced.

**`AgentExecutionMemory`** (referenced by `FeedbackLoopEngine`) —
schema not enumerated in this sweep; referenced by
`core/services/feedback_loop_engine.py:256-299` for user-rating
aggregation. Adjacent to the primary Category C persistence
surface; not a distinct architectural concern for S1302.

### 4.D FK graph (cross-category + outside domain)

- `AgentKnowledgeSource.agent` → `Agent` (cross-domain to Agents).
- `UserAgentLearning.user` → user model (cross-domain to Users).
- `ConversationMemory.user` + `.conversation` → user model +
  `ChatConversation` (cross-domain to Users + Conversations).
- `AgentMemory.agent` → `Agent` (cross-domain to Agents).
- **No internal FKs between A ↔ B ↔ C.** Each category's rows
  can be joined only via the shared `agent` or `user` FK; there
  is no direct table-level linkage. Cross-category state flow
  happens at the service layer, not the schema layer (see §7).

### 4.E Migration lineage — versioning attempts

- No versioning migration exists for any Category A/B/C model.
- Migration 0044 (`content/migrations/0044_provenance_and_promotion.py`)
  added row-level provenance fields on `DocumentEmbedding` — that
  is Category D (S1301 §14.3 D3). **No analogous provenance-field
  migration exists for A/B/C models** on the same pattern; the
  fields A/B/C do have (`source_type` on `AgentMemory`,
  `source_spider_names` on `AgentKnowledgeSource`) predate the
  Category D provenance-fields effort and follow different
  semantics.
- `LearningBridge` migration cascade (S1115, 9 bridges) migrated
  bridge implementations from an ad-hoc pattern to the
  `LearningBridge` ABC in `core/learning_bridges/`. Migration
  lineage: `core/learning_bridges/apps.py:32` (bridge registration).

---

## 5. Major Services

**Q5 — What service classes / modules does this domain own?**

### 5.A Category A services

**`EmbeddingService`** — `core/services/embedding_service.py:66-414`
(413 lines)

- Singleton pattern; wraps ALL OpenAI embedding API calls in the
  platform.
- Lazy-loads OpenAI client via `core/services/openai_client_factory.py`
  (per project memory rule on factory-required clients).
- Redis cache: 7-day TTL at line 80 (`CACHE_TTL = 7 * 86400`),
  deterministic hash-based keys at :79-116.
- Batch embedding support with cache hit/miss optimization at
  :218-342.
- Cost tracking to `LLMCallLog` at :349-385.
- **No cross-domain internal imports.** Isolated utility service.
- **Reused by 21 non-memory services** (Agent 4 grep):
  `content/claims_pack_builder.py`, `core/services/spider_semantic_search.py`,
  `core/services/boardroom_ml_service.py`,
  `core/services/scoped_retrieval.py`,
  `core/services/dynamic_team_builder.py`, others. This is
  utility-pattern reuse, not a boundary violation (see §16).

**Knowledge writers (no service class):** implemented as signal
receivers in `core/learning_bridges/spider_data_bridge.py`
(registered at `core/learning_bridges/apps.py:32`). Django
`post_save` on `SpiderData` triggers `spider_data_to_knowledge`
which writes `UserAgentLearning` per target agent
(**not** `AgentKnowledgeSource` directly — Agent 4 verified;
this is an architectural note: the spider bridge lands in
Category B for per-user learning, not in Category A knowledge).
Category A writes come from `implementation_executor` and sync
commands (see §7.2.A).

### 5.B Category B services

**`AgentLearningService`** — `core/services/agent_learning_service.py:122-758`
(795 lines)

- Centralized per-user preference learning.
- Redis backing: db=5 (line 146), REDIS_PREFIX="agent_learning"
  (line 139).
- In-memory cache: `_user_memories` dict (line 152), lost on
  worker recycle.
- Write methods: `record_interaction()` (:169-213),
  `_persist_interaction()` (:237-262), `save_memory()`
  (:462-482 — issues `redis_client.hset` at :476, no DB
  fallback).
- Read methods: `get_user_memory()` (:410-425),
  `get_top_preferences()` (:484-508), `get_adaptive_context()`
  (:512-549).
- Cross-domain call: imports
  `core.services.agent_collaboration_hub` at :590 (Agent 2 —
  optional collaboration path; wrapped in try/except; risk MODERATE
  but expected).

**Redis TTL check:** grep of the service for `setex` / `expire`
calls returns 0 hits (Agent 6). Preference hashes accumulate
without TTL; Redis loss on worker recycle is unrecoverable from
the service itself. UserAgentLearning is the durable backing
side but is written on a DIFFERENT path (see §7.2.B).

**`ConversationOrchestrator`** — `core/conversation_orchestrator.py`

- 14-day freshness window at `:749`
  (`freshness_cutoff = tz.now() - timedelta(days=14)`). Session
  988 origin per comment at :747-748.
- `_get_agent_knowledge(agent_name)` at :725-768 pulls
  `AgentKnowledgeSource` (A) at :752-755 AND `AgentMemory` (C)
  at :764-767 under the same 14-day gate — this is a
  cross-category service that reads from A + C.
- Feature flag `ENABLE_CROSS_AGENT_MEMORY = True` at :46
  (Agent 2).

**`ConversationMemoryService`** —
`core/services/conversation_memory_service.py:64-445` (445
lines)

- Creates cross-agent memories from conversation outcomes.
- Writes to `AgentMemory` (Category C) — cross-category writer.
- Reads from `AgentMemory`, `SharedKnowledge`.
- No external service dependencies within read path.

### 5.C Category C services

**`MemoryPromotionService`** —
`core/services/memory_promotion_service.py:119-338` (338 lines)

- **VERIFIED to exist** via parent-agent grep for
  `def score_for_promotion` and `def check_and_promote` at
  lines :119 and :197 respectively. Agent 1's earlier
  "MemoryPromotionService location unknown" finding was
  incorrect; audit reflects Agent 2's file:line.
- Not a class — module of functions.
- Scoring at `score_for_promotion(text)` — deterministic regex
  patterns:
  - Milestone language +3 (max once per text) — patterns at
    :32-47 (`_MILESTONE_PATTERNS`).
  - Identifier extraction +2 per type, capped at +6 total —
    patterns at :51-63 (`_IDENTIFIER_PATTERNS`); 11 identifier
    types (bundle_id, android_package, version_build, repo_slug,
    git_url, commit_sha, railway_service, base_url, worker_queue,
    port_binding, docker_image).
  - Wiring/topology +2 (max once per text) — patterns at :67-73
    (`_WIRING_PATTERNS`).
  - Secret detection -10 hard block — patterns at :77-86
    (`_SECRET_PATTERNS`); function `_contains_secret()` at
    :104-106 returns True on any match, saves get zero-scored.
- Thresholds at :234, :237: score ≥7 auto-save, 5-6 pending
  (log-only), ≤4 ignore. **Hardcoded; not configurable.**
- Write path: builds `UserMemoryContext` (not `AgentMemory`) at
  :303-318 — note: `MemoryPromotionService` writes into a
  `UserMemoryContext` model, NOT into `AgentMemory` directly.
  This is a cross-category writer from PA context into
  user-persistent context.
- Cross-domain call: imports `_redact_secrets` from
  `core.services.tool_dispatcher` at :253 for pre-save
  sanitization.

**`FeedbackLoopEngine`** —
`core/services/feedback_loop_engine.py:26-618` (618 lines)

- Reads `AgentExecution` + `AgentExecutionMemory` for
  performance metrics; reads `AgentMemory` for PA-review-flagged
  rows at :146-176.
- `get_feedback_for_agent(agent_name, task='', days_back=30)` at
  :87-214 is the primary read entry.
- **Not a writer for Category C in normal path** — reads
  `AgentMemory`, does NOT write it. `record_user_feedback` at
  :569-606 updates `AgentExecutionMemory.user_rating` (an
  adjacent model).
- Lazy-loads models via `@property` at :56-85 to avoid circular
  imports.

### 5.D God-service / cross-domain import findings

- **No service in scope exceeds the 3000-line god-service
  threshold** (playbook §13). Largest is `AgentLearningService`
  at 795 lines.
- Cross-domain imports found (Agent 2):
  - `AgentLearningService → agent_collaboration_hub` at :590 —
    intentional, wrapped in try/except.
  - `MemoryPromotionService → tool_dispatcher` at :253 —
    intentional utility import (`_redact_secrets`), LOW risk.
  - `FeedbackLoopEngine → @property lazy imports` at :56-85 —
    standard Django circular-dependency mitigation, no risk.
- **No boundary violations at the service layer.** See §16.

---

## 6. Major APIs and Interfaces

**Q6 — What tools, endpoints, and schemas expose this domain?**

### 6.1 PA tool schemas touching A/B/C

| Tool | Schema file:line | Actions | Handler | Categories | Mutating? |
|------|-------------------|---------|---------|-----------|-----------|
| `remember_tool` | `core/services/pa_tool_schemas.py:2134` | save, list, delete, search | `_handle_remember` at `core/services/td_handlers_core.py:2192` | B (writes UserMemoryContext) | YES |
| `conversation_tool` | `core/services/pa_tool_schemas.py:2186` | get, search, summary, pin_memory, recent | `_handle_conversation` at `core/services/td_handlers_core.py:1966` | B (reads ConversationMemory pgvector; writes pins to UserMemoryContext at :2132) | YES (pins only) |
| `learning_tool` | `core/services/pa_tool_schemas.py:1999` | list_candidates, list_approved, list_expired, approve, reject, stats | `_handle_learning` at `core/services/td_handlers_core.py:1896` | B (writes PAToolInsight status only) | YES (safety_class mutation) |
| `feedback_tool` | `core/services/pa_tool_schemas.py:404` | submit, list, stats, update | Handler location UNKNOWN — Agent 3 grep did not locate; likely in `td_handlers_ops.py` or `td_handlers_content.py` (SPECULATIVE) | C (submits to Feedback → FeedbackLoopEngine) | YES |
| `db_health_tool` (learning_stats action) | `core/services/pa_tool_schemas.py:1883` | learning_stats | `_handle_db_health` at `core/services/td_handlers_core.py:1434` | A+B+C observational | NO |

**Count reconciliation:** `docs/PLATFORM_INVENTORY.md` autoblock
reports 113 tool schemas + 156 registered handlers (per
CLAUDE.md autoblock; slightly different from Agent 3's cited
"109 + 174" — inventory autoblock as of last regeneration
takes precedence per DOC_LIFECYCLE.md §2c). 5 tools touch A/B/C
directly.

### 6.2 Celery tasks touching A/B/C

| Task | def file:line | Beat cadence | Writes to | Reads from | Category |
|------|---------------|--------------|-----------|------------|----------|
| `promote_to_shared_knowledge` | `core/tasks.py:7879` | Enabled (beat name `promote-to-shared-knowledge`) | `AgentKnowledgeSource` → `SharedKnowledge` | `AgentKnowledgeSource`, `KnowledgeTransfer` | A |
| `auto_promote_low_risk_decisions` | `core/tasks.py:6260` | Enabled (beat name `auto-promote-low-risk-decisions`) | `AgentMemory` (via MemoryPromotionService indirection) | `AgentExecution` decision history | C |
| `ai_promote_decisions` | `core/tasks.py:6268` | Enabled (beat scheduled) | `AgentMemory` | Decisions | C |
| `backfill_conversation_memory_embeddings` | `core/tasks_misc.py:1201` | **NOT beat-scheduled** — one-shot / admin trigger only | `ConversationMemory.embedding` (pgvector) | `ConversationMemory` | B |

**Beat schedule autoblock** (`docs/PLATFORM_INVENTORY.md`): 91
enabled + 5 disabled = 96 PeriodicTask rows. Memory-touching
subset = 2 promotion tasks enabled. Backfill for Cat B
embeddings is NOT beat-scheduled; a coverage-drift risk if
`ConversationMemory` rows accumulate without embeddings.

### 6.3 Management commands

| Command | file | Recurrence | Writes to | Reads from | Category |
|---------|------|-----------|-----------|------------|----------|
| `assign_memories_to_rooms` | `core/management/commands/assign_memories_to_rooms.py` | One-shot (--dry-run supported) | `AgentMemory.rooms` (M2M) | `AgentMemory` | C |
| `discover_learning_cohorts` | `core/management/commands/discover_learning_cohorts.py` | Recurring (nightly cron implied) | `UserAgentLearning` (confidence propagation) | `UserAgentLearning` | B |
| `sync_agent_learning` | `core/management/commands/sync_agent_learning.py:457` | Recurring | `AgentKnowledgeSource.get_or_create` | Spider ingest | A |
| `system_health_check` | `core/management/commands/system_health_check.py` | UNKNOWN | UNKNOWN | `AgentMemory`, `UserAgentLearning`, `ConversationMemory` | A+B+C observational |

### 6.4 REST / WebSocket surfaces

Sample of memory/learning endpoints (Agent 3 enumeration; not
exhaustive):

| Endpoint | file:line | Method | Category | Mutating? |
|----------|-----------|--------|----------|-----------|
| `/api/memory/precedents/` | `core/urls.py:1670` | GET | C | NO |
| `/api/memory/failures/` | `core/urls.py:1671` | GET | C | NO |
| `/api/memory/strategy/` | `core/urls.py:1672` | GET | C | NO |
| `/api/memory-palace/memories/` | `core/urls.py:3544` | GET | C | NO |
| `/api/memory-palace/memory/<id>/delete/` | `core/urls.py:3549` | DELETE | C | YES |
| `/api/user-learning/feedback/` | `core/urls.py:1684` | POST | B | YES (UserAgentLearning) |
| `/api/user-learning/profile-response/` | `core/urls.py:1690` | POST | B | YES (UserAgentLearning) |
| `/api/user-learning/goals/<id>/progress/` | `core/urls.py:1694` | POST | B | YES |
| `/api/learning/patterns/` | `core/urls.py:2092` | GET | B | NO |
| `/api/learning/loop/track/` | `core/urls.py:2108` | POST | B | YES |

**Categorization by write authority (§18 sets up):**

- **Category A:** primary write authority is internal (spider →
  bridges → knowledge; decision → implementation_executor →
  knowledge). No PA-facing write tool. `promote_to_shared_knowledge`
  beat task is the only cross-user promotion path.
- **Category B:** widest external write surface — PA
  `remember_tool` + REST `/api/user-learning/feedback/` +
  `/api/learning/loop/track/` + management commands. User can
  directly trigger writes.
- **Category C:** hybrid — user can DELETE memories and submit
  feedback, but memory *creation* is dominated by internal
  auto-promotion via `MemoryPromotionService` on every PA turn.

### 6.5 No dedicated WebSocket consumer for memory streams

Agent 3 grep of `core/consumers*.py` +
`core/services/websocket_bridge.py` returned no memory-specific
consumers. UNKNOWN whether `ConversationMemory` updates stream
in real-time to the PA — likely refreshed via query rather than
push.

---

## 7. Runtime Flows

**Q7 — What is the runtime execution flow, write side and read
side, per category?**

### 7.1 Category A — Semantic Knowledge Memory

#### 7.1.A Write flow (spider → knowledge)

```
Celery Beat (every 30 min per KNOWLEDGE_PIPELINE.md line 72)
  ↓
run_spider_network() [core/tasks.py]
  ↓
SpiderData.objects.create(...)
  ↓
Django post_save signal → spider_data_bridge.spider_data_to_knowledge()
  [core/learning_bridges/apps.py:32 registers; core/learning_bridges/spider_data_bridge.py:107-111]
  ↓
For each matched agent, _create_agent_learning_entry() writes
  UserAgentLearning row [line :111]
  ↓
(Note: this bridge lands in Category B UserAgentLearning, NOT
 directly in AgentKnowledgeSource. Category A knowledge writes
 come from a different path — see below.)
```

**AgentKnowledgeSource writes come from:**

- `core/services/implementation_executor.py:428, :443` —
  pilot decision outcomes create/get_or_create knowledge rows.
- `core/management/commands/sync_agent_learning.py:457` —
  spider sync pipeline get_or_create.
- **Embedding side:** written via `EmbeddingService.create_embedding`
  when opt-in (nullable `embedding` field; opt-in per
  KNOWLEDGE_RAG_MEMORY.md §4 tradeoff → risk of DB row without
  embedding).

#### 7.1.B Read flow (agent execution → prompt injection)

```
BaseAgent.execute(task)
  ↓
_build_prompt(task) → _get_relevant_knowledge_for_task(task, limit=5)
  [core/agents/base_agent.py:1435-1510]
  ↓
task_embedding = EmbeddingService.create_embedding(task) [lazy import :1488]
  ↓
AgentKnowledgeSource.objects.annotate(
    similarity=CosineDistance('embedding', task_embedding)
).filter(similarity__gt=0.5, agent=self.agent_obj).order_by('-similarity')[:5]
  ↓
Format results (source_agent, title, summary, knowledge_type,
  confidence, spider_sources)
  ↓
Inject into prompt as "## Relevant Knowledge from Past Learning"
```

**Call-time semantics:** Knowledge is PULLED at execution time;
no precomputation or per-agent cache. The `EmbeddingService`
Redis cache absorbs the OpenAI-side cost, not query cost.

#### 7.1.C Cross-category read (ConversationOrchestrator gate)

`_get_agent_knowledge(agent_name)` at
`core/conversation_orchestrator.py:725-768` pulls Category A
AND Category C rows under a shared 14-day freshness gate:

```
freshness_cutoff = tz.now() - timedelta(days=14)  [line :749, HARDCODED]
  ↓
AgentKnowledgeSource.objects.filter(agent=agent,
    last_updated_at__gte=freshness_cutoff).order_by('-last_updated_at')[:5]  [lines :752-755]
  ↓
AgentMemory.objects.filter(agent=agent,
    created_at__gte=freshness_cutoff).order_by('-created_at')[:5]  [lines :764-767]
```

This is a cross-category read (A + C) with A's freshness field
being `last_updated_at` and C's being `created_at` — an implicit
schema-level assumption that "recently updated knowledge" and
"recently created memory" both matter for prompt context.

### 7.2 Category B — Personal / Adaptive Memory

#### 7.2.A Write flow — AgentLearningService (Redis-only)

```
Agent execution completes
  ↓
record_interaction(user_id, agent_name, interaction_type,
                   input_data, output_data, rating)
  [core/services/agent_learning_service.py:169-213]
  ↓
AgentInteraction dataclass created in-memory buffer  [line :200]
  ↓
_persist_interaction(interaction)  [line :237-262]
  ↓
redis_client.zadd("agent_learning:interactions:{user_id}:{agent_name}",
  {json.dumps(interaction.to_dict()): interaction.created_at.timestamp()})
  ↓ (retain last 100 via zremrangebyrank 0 -101)
_learn_from_interaction() → in-memory _user_memories update
  [line :266-278] — extracts signals: style, model, quality, theme, color, mood
  ↓
save_memory(user_id, agent_name)  [line :462-482]
  ↓
redis_client.hset("agent_learning:preferences:{user_id}:{agent_name}",
                  "{category}:{value}", json.dumps(LearnedPreference))
  [line :476, VERIFIED — no DB fallback]
```

**Durability:** Redis-only. Worker recycle drops the in-memory
`_user_memories` cache; Redis state depends on `save_memory` being
called before recycle. No TTL on the hash key (Agent 6 grep 0
hits for `setex`).

#### 7.2.B Write flow — UserAgentLearning (Postgres-durable)

```
PA publishes/archives/revises deliverable
  ↓
tool_dispatcher._record_content_feedback(agent_name, action, summary)
  [Session 990 handoff]
  ↓
AgentMemory.objects.create(memory_type='feedback', tags=['pa_review', 'action_{action}'], valence=...)
  ↓
UserAgentLearning.record_success() or record_failure()
  [per-user learning signal, per SESSION_990]
```

`UserAgentLearning.create_learning` classmethod at
`core/models_unified_system.py:4122` sets `learning_source` from
enum; this field IS actively filtered downstream at
`core/services/td_handlers_ops.py:5965, 5986, 6000`.

#### 7.2.C Read flow — adaptive context injection

```
Agent init / task routing
  ↓
get_adaptive_context(user_id, agent_name)
  [core/services/agent_learning_service.py:512-549]
  ↓
get_top_preferences(user_id, agent_name, limit=10)
  [:484-508 — CONFIDENCE_THRESHOLD=0.6; sort by confidence * occurrences]
  ↓
get_user_memory(user_id, agent_name)
  [:410-425 — check _user_memories in-memory first, then
   _load_memory_from_redis]
  ↓
Format context string:
  "User Preferences (learned from interactions): ..."
  [:529-549]
  ↓
Inject into prompt or surface into spider_context['agent_learned_preferences']
  (KNOWLEDGE_RAG_MEMORY.md §2 says this surfacing exists via
   gather_context; Agent 4 verified STRONG architecturally but
   exact gather_context inline call point not located in this
   sweep — flagged SPECULATIVE for implementation trace, STRONG
   for architectural intent per narrative)
```

#### 7.2.D Read flow — ConversationMemory (per-user pgvector)

```
PersonalAIOrchestratorService._load_memory_from_db(user_id, limit)
  [core/personal_ai_orchestrator.py:158-166]
  ↓
ConversationMemory.objects.filter(user_id=user_id)
    .order_by('-created_at')[:limit]  [line :163]
  ↓
Load into prompt context for PA turn
```

Write side: `ConversationMemory.objects.create()` at
`core/personal_ai_orchestrator.py:421` — per-PA-turn write from
the Personal AI Orchestrator.

### 7.3 Category C — Agent Working Memory

#### 7.3.A Write flow — MemoryPromotionService

```
PA turn completes (user_msg + assistant_response + tool_results)
  ↓
check_and_promote(user_message, assistant_response, tool_runs,
                  user, trace_id)
  [core/services/memory_promotion_service.py:197-338]
  ↓
Combine all text blocks
  ↓
score_for_promotion(combined_text)  [:119-172]
  ├─ milestone patterns (+3, max once)                [:32-47]
  ├─ identifier patterns (+2/type, cap +6)             [:51-63]
  ├─ wiring patterns (+2, max once)                    [:67-73]
  └─ secret patterns (-10 hard block; sets details['blocked']) [:77-86, :104-106]
  ↓
IF score >= 7 (line :249):
  extract_promotion_content() → structured key-value lines  [:175-194]
  _redact_secrets() via tool_dispatcher                     [:253-254]
  _infer_tags(text) → up to 5 tags                          [:260]
  content hash dedup: SHA256(content.lower().strip() + ":project")[:16]  [:270-272]
  Query UserMemoryContext for existing hash → update or create  [:275-320]
  UserMemoryContext.objects.create(
    memory_type='project', importance=9, source='auto_promotion',
    tags, context_metadata={content_hash, trace_id,
                            promotion_score, milestones,
                            identifier_types}
  )  [:303-318]
  get_memory_context_service().clear_cache(user)   [:321-322]
  Log "Memory promotion AUTO-SAVED"
ELSE IF 5 <= score <= 6 (line :237):
  Log "Memory promotion PENDING", NOT saved
ELSE (score <= 4):
  No action, no log
```

**Note:** `MemoryPromotionService` writes into `UserMemoryContext`,
NOT into `AgentMemory` directly. `UserMemoryContext` is a
user-scoped memory table (Cat B by user-scope, Cat C by
score-gated-auto-save-from-PA semantics — an overlap surface;
see §17).

#### 7.3.B Read flow — FeedbackLoopEngine

```
Agent router builds execution context
  ↓
FeedbackLoopEngine.get_feedback_for_agent(agent_name, task='', days_back=30)
  [core/services/feedback_loop_engine.py:87-214]
  ↓
_get_execution_stats(agent_name, since=now()-30d)  [:224-254]
_get_memory_stats(agent_name, since)               [:256-299]
  ↓
AgentMemory.objects.filter(
  agent=agent_obj,
  memory_type='feedback',
  tags__contains=['pa_review'],
  created_at__gte=since
).order_by('-created_at')[:5]                       [:150-161]
  ↓
Build pa_review_summary = "N PA reviews: X published, ..."
  [:161-173]
  ↓
Return feedback dict with recommendations, alternatives, summary
  ↓
core/agent_router.py:765-767:
  spider_context['pa_content_feedback'] = feedback_context['pa_review_feedback']
  spider_context['pa_review_summary']    = feedback_context.get('pa_review_summary', '')
```

**Consumer:** none in code. Whole-tree grep (including `ai_core/`)
finds no code path that reads
`spider_context['pa_content_feedback']`. See §14.3 F1 for the
dead-code finding.

### 7.4 Cross-category flow map

```
Cat A ─── ConversationOrchestrator._get_agent_knowledge ────── Cat C
   │           (14-day gate, both directions)                       │
   │                                                                │
   │                                                                │
   └──── AgentLearningService.share_learning_as_knowledge ──── (Cat A)
                       (line :590; optional; try/except)
   ↑
   │
Spider → learning_bridges/spider_data_bridge → UserAgentLearning (Cat B)
   (writes Cat B, not Cat A; naming suggests otherwise but
    Agent 4 verified target is UserAgentLearning)

MemoryPromotionService → UserMemoryContext (not AgentMemory)
   (:303-318; UserMemoryContext is user-scoped table; overlap
    with strict Cat C interpretation)
```

---

## 8. Data Ownership and Lifecycle

**Q8 + Q9 — Who owns each store's data, and what is its
lifecycle?**

### 8.1 Ownership (data-scope semantics)

| Store | Scope | Owner authority | Notes |
|-------|-------|-----------------|-------|
| `AgentKnowledgeSource` | Per-Agent (FK `agent`); cross-user semantically | UNCLEAR — Category A per parent, but feedback fields suggest Cat C authorship intent | See §18 |
| `UserAgentLearning` | Per-User (FK `user`); enum `learning_source` differentiates | Category B — clear per-user scope enforcement at schema | No query-time auth check found; per-user isolation is schema-only |
| `ConversationMemory` (Django) | Per-User + Per-Conversation | Category B | FKs enforce scope; embedding is opt-in per pgvector availability |
| `AgentLearningService` Redis prefs | Per-User + Per-Agent (composite key) | Category B — process-scoped state | Ephemeral; loss on worker recycle |
| `AgentMemory` | Per-Agent (FK `agent`); no user FK | Category C — agent-scoped, cross-user | Any code with agent reference can create |
| `UserMemoryContext` | Per-User (via `MemoryPromotionService.check_and_promote(user=)`) | UNCLEAR — Cat B by user-scope; Cat C by write-trigger (PA-turn auto-save) | See §17 overlap discussion |

### 8.2 Lifecycle / retention

| Store | Retention | Enforcement | Gap |
|-------|-----------|-------------|-----|
| `AgentKnowledgeSource` | None declared | None | Rows accumulate; only freshness gate is 14-day filter at read (`conversation_orchestrator.py:749`), not deletion |
| `UserAgentLearning` | `expires_at` field exists | **NOT enforced** by any beat or query | Field is dead code — `dead_code` finding |
| `ConversationMemory` (Django) | None declared | None | Rows accumulate per user; no retention policy |
| `AgentLearningService` Redis prefs | None (no TTL) | None | Redis loss = data loss; no durable spillover |
| `AgentMemory` | None declared | None | Rows accumulate per agent |
| `UserMemoryContext` | Deduped by content hash | Update-on-hash-match at `memory_promotion_service.py:275-320` | Duplicate content merges; no time-based retention |

**No Category A/B/C store has an enforced retention policy.**
The `expires_at` field on `UserAgentLearning` is a schema
affordance without a runtime consumer. Storage growth is
unbounded; freshness is enforced only at read-time in the
14-day window (Cat A/C read) or in-service confidence threshold
(Cat B AgentLearningService reads only rows above 0.6 confidence).

### 8.3 Embedding cadence

- **Category A embedding cadence:** UNKNOWN by policy — the
  `embedding` field on `AgentKnowledgeSource` is nullable; no
  beat task backfills existing rows; ad-hoc via management
  commands (per KNOWLEDGE_RAG_MEMORY.md §4 tradeoff). Rows
  without embeddings are silently missed by cosine-similarity
  retrieval.
- **Category B `ConversationMemory` embedding cadence:** NOT
  beat-scheduled. `backfill_conversation_memory_embeddings` at
  `core/tasks_misc.py:1201` exists as a one-shot/admin trigger.
- **Category C `AgentMemory` embedding cadence:** embedding
  generation is gated on `safety_class == 'approved'` at
  `core/models_unified_system.py:11041-11042`; opt-in per write.

**Silent-missing-embedding class:** All three categories have
opt-in embedding generation. A row without an embedding is
silently invisible to cosine retrieval. No monitor detects
"row created but embedding missing." Related to S1301 §14.1's
"chunk coverage gap" pattern but different mechanism (row-level
opt-in vs corpus-level backfill).

---

## 9. Integrations With Other Domains

**Q14 + Q17 + Q18 + Q21 + Q22 — Cross-domain integrations.**

### 9.1 Inbound consumers (who reads A/B/C)

| From domain | To store | Strength | Evidence | Notes |
|-------------|----------|----------|----------|-------|
| Agents (`core/agents/`) | `AgentKnowledgeSource` (A) | STRONG | `core/agents/base_agent.py:1435-1510` `_get_relevant_knowledge_for_task`; prompt injection every execute; `core/agent_router.py:769-776` spider_context injection | Verified at multiple call sites |
| Agents (`core/agents/`) | `UserAgentLearning` (B) | STRONG (ARCHITECTURAL) / UNKNOWN (implementation line) | KNOWLEDGE_RAG_MEMORY.md §2 + Session 991 handoff; Agent 4 architectural verification; exact gather_context inline call point not located | Hedged per §7.2.C |
| Agents (`core/agents/`) | `AgentMemory` (C) via FeedbackLoopEngine | STRONG (produced) / **DEAD CODE (consumed)** | `feedback_loop_engine.py:150-161` reads; `agent_router.py:766` produces `spider_context['pa_content_feedback']`; **zero code consumers** | §14.3 F1 |
| PersonalAIOrchestrator | `ConversationMemory` (B) | STRONG | `core/personal_ai_orchestrator.py:163` reads history | Per-user, per-turn |
| ConversationOrchestrator | `AgentKnowledgeSource` + `AgentMemory` (A + C) | STRONG | `core/conversation_orchestrator.py:752-755, :764-767` | 14-day gate |
| Content Pipeline | any A/B/C store | MISSING | Agent 4 grep 0 hits on RAG imports in `core/services/content*.py` | Pattern echoes S1301 §9.1 MISSING inbound |
| Employee OS (MissionRunner) | any A/B/C store | MISSING | Agent 4 grep 0 hits | Cross-arc: Employee OS 1200s follow-up may want this |
| Signal Engine | any A/B/C store | MISSING | Agent 4 grep 0 hits | Same as S1301 §9.1 pattern |

### 9.2 Outbound producers (who writes to A/B/C)

| Domain | Writes to | Strength | Notes |
|--------|-----------|----------|-------|
| Spider ingest + `learning_bridges/spider_data_bridge` | `UserAgentLearning` (B) | STRONG | `core/learning_bridges/spider_data_bridge.py:107-111`; bridge writes B, NOT A directly |
| `implementation_executor` | `AgentKnowledgeSource` (A) | STRONG | `core/services/implementation_executor.py:428, :443` — pilot decision outcome writer |
| `sync_agent_learning` command | `AgentKnowledgeSource` (A) | STRONG | `:457` get_or_create |
| PA turn processing | `UserMemoryContext` (via MemoryPromotionService) + `AgentMemory` (via `_record_content_feedback` in tool_dispatcher) | STRONG (documented) / PARTIAL (grep found `_record_content_feedback` referenced but not located inline in this sweep) | Session 990 origin |
| REST `/api/user-learning/*` (POST) | `UserAgentLearning` (B) | STRONG | Multiple endpoints at `core/urls.py:1684+` |
| `promote_to_shared_knowledge` task | `AgentKnowledgeSource` → `SharedKnowledge` | STRONG | Beat-scheduled |

### 9.3 Cross-category flows within Memory (A ↔ B ↔ C)

- **A ↔ C via `ConversationOrchestrator`:** Both categories are
  read together in `_get_agent_knowledge` under a shared 14-day
  gate.
- **A → B via `spider_data_bridge`:** Confusingly named — the
  spider→knowledge bridge actually writes `UserAgentLearning`
  (B), not `AgentKnowledgeSource` (A). This is a *documentation
  drift* — the narrative KNOWLEDGE_RAG_MEMORY.md talks about
  spider → knowledge but the code lands in Category B.
- **PA turn → C (indirect) + Cat A via `share_learning_as_knowledge`:**
  `AgentLearningService.share_learning_as_knowledge` at
  `core/services/agent_learning_service.py:590` is an optional
  path (wrapped in try/except) that promotes Redis preferences
  to `AgentKnowledgeSource` (A).
- **C → A: no direct flow.** `AgentMemory` episodic memories
  do not auto-promote to cumulative `AgentKnowledgeSource`.
- **B → C: no direct flow.** `UserAgentLearning` does not feed
  `AgentMemory`.

---

## 10. Event Flows

**Q19 + Q20 — What events fire, and what do they carry?**

### 10.1 Django signals

- **`post_save` on `SpiderData`** → `spider_data_bridge.spider_data_to_knowledge`
  (registered at `core/learning_bridges/apps.py:32`). This is
  the sole ORM signal in scope for A/B/C write flow.
- **No `post_save` signal on `AgentKnowledgeSource` / `AgentMemory` /
  `UserAgentLearning` / `ConversationMemory`** — writes propagate
  by explicit call, not signal.

### 10.2 Log-line events (silent-observability surface)

- `MemoryPromotionService` emits `Memory promotion AUTO-SAVED
  id=N score=N tags=[...]` at info level after `check_and_promote`
  auto-saves; `Memory promotion PENDING` at info for score 5-6
  (Agent 2). **Not a metric or alert** — log-line only.
- `AgentLearningService` emits interaction logs, but no
  aggregation surface.
- **No emit for the pa_content_feedback dead-code path** — the
  producer at `agent_router.py:766` writes silently.

### 10.3 No first-class event bus for memory events

- Grep for a memory-scoped event bus channel: 0 hits. Memory
  writes are direct-to-DB or direct-to-Redis with no
  publish/subscribe surface. Any downstream consumer that
  wanted a notification of "new memory written" or "learning
  updated" would need to poll or add a signal.

---

## 11. Existing Documentation

**Q10 — What documentation exists?**

### 11.1 Topic docs

| File | Sections covering A/B/C | Notes |
|------|-------------------------|-------|
| `docs/topics/agent-system.md` | §"Context Injection (12 Layers)" §8-12; §"Agent Health" §4-5 | Names Cat A knowledge_context, Cat B feedback_context, Cat C pa_content_feedback / pa_review_summary in context-layer mechanism |
| `docs/topics/personal-assistant.md` | "Enrichment Pipeline" table; "Key Tools" | Session 1035-W2 advisor context reference; PA enrichment path |
| `docs/topics/content-pipeline.md` | §Session 990 feedback closure | Cat C feedback path |
| `docs/topics/local-askdocs.md` | (Cat D boundary; not A/B/C) | Reference only |

### 11.2 Narratives

- **`docs/narratives/KNOWLEDGE_RAG_MEMORY.md`** (S1158) is the
  primary comprehensive narrative. §1 names all three categories;
  §2 provides vocab; §3 milestone timeline; §4 wins/tradeoffs;
  §5 current-state snapshot; **§6 open questions — includes
  the pa_content_feedback consumer UNKNOWN that this audit
  escalates to CONFIRMED DEAD CODE in §14.3 F1.**

### 11.3 Handoffs

| Handoff | Session | Category coverage |
|---------|---------|-------------------|
| `SESSION_990_PA_CONTENT_FEEDBACK_LOOP.md` | 990 | C — producer wiring |
| `SESSION_991_PROACTIVE_INTELLIGENCE_AGENT_LEARNING_WIRING.md` | 991 | B — AgentLearningService wiring |
| `SESSION_1115_CONTEXT_KIT_DRIFT_CLEANUP.md` | 1115 | A — 9-bridge migration |
| `SESSION_1158_CORPUS_NARRATIVE_PROGRAM.md` | 1158 | A + B + C narrative author |
| `SESSION_1142_DOCS_HYGIENE_SEARCH_DOCS_AND_AUDIT_FIXES.md` | 1142 | A — Cat D touchpoint (search_docs; already scoped by S1301) |
| `SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md` | 1300 | Group 1300 parent |
| `SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md` | 1301 | D + row-level orphan write path inheritance for A/B/C |

**No dedicated handoff for `MemoryPromotionService` origin** —
service exists in production; git log `-S "MemoryPromotionService"`
would surface it. Left as UNKNOWN in appendix.

### 11.4 Prior research

- `docs/research/platform_architecture_inventory.md` §3.13 —
  DEEP coverage for A + B + C combined.
- §5.4 "Multiple Memory / Knowledge Stores" — the overlap flag
  that motivated Group 1300 parent scoping.
- S1301 audit — sibling; cite-not-re-answer for §17.1 + §17.2.

### 11.5 Gap analysis (what documentation does NOT cover)

- **Category A:** no doc explains the intentional non-versioning
  rationale for `AgentKnowledgeSource`; no doc explains embedding
  cadence policy.
- **Category B:** no doc justifies the 14-day freshness constant;
  no doc names Redis loss-on-recycle mitigation strategy;
  `AgentLearningService` internal state model is undocumented
  beyond narrative-level.
- **Category C:** no doc documents `MemoryPromotionService`
  scoring criteria (this audit §14 does); no doc names when the
  service was introduced; no doc names why `MemoryPromotionService`
  writes to `UserMemoryContext` and not `AgentMemory` directly.

---

## 12. Research Coverage

**Q11 — Playbook §12 classification.**

| Category | Rating | Evidence |
|----------|--------|----------|
| A | DEEP | KNOWLEDGE_RAG_MEMORY.md §1-5; PLATFORM_INVENTORY §3.13; handoffs S990/S1115/S1158 |
| B | MODERATE | AgentLearningService wiring documented (S991); freshness window origin (S988) documented; but learning-quality validation, Redis mitigation UNKNOWN in docs |
| C | LIGHT | Session 990 feedback closure documented; MemoryPromotionService scoring not documented anywhere before this audit; origin session UNKNOWN |

---

## 13. Architecture Maturity

**Q13 — Per-category verdict.**

| Category | Verdict | Rationale |
|----------|---------|-----------|
| A — Semantic Knowledge Memory | **PARTIAL** | Knowledge accumulation works end-to-end; feedback instrumentation exists (feedback_positive/negative fields) but is orphaned — no consumer. No versioning. Embedding is opt-in with silent-missing failure mode. |
| B — Personal / Adaptive Memory | **PARTIAL** | UserAgentLearning postgres side WORKING (learning_source actively filtered); AgentLearningService Redis side PARTIAL (loss on worker recycle; no durable spillover). ConversationMemory model exists but retention unenforced. |
| C — Agent Working Memory | **EXPERIMENTAL** | Auto-promotion pipeline runs and is deterministic; scoring criteria hardcoded; safety_class gating works. But **the biggest downstream feedback loop is dead-coded at the consumer side** — `pa_content_feedback` produced, never consumed. Downgrade from WORKING → EXPERIMENTAL because the loop is architecturally intended but operationally broken. |

**Subsystem verdict (combined A + B + C):** PARTIAL for the two
Postgres-durable categories; EXPERIMENTAL for the score-gated
auto-save category. Individual sub-verdicts drive the shape of
§19 recommendations.

---

## 14. Known Drift

**Q23 — What does documentation claim vs runtime reality?**

### 14.1 Parent §3 known drift bullets — verification report

Per Agent 6 verification, cross-checked by parent-agent
verifier-loop.

| Bullet | Verified? | Runtime evidence | Class | Severity |
|--------|-----------|------------------|-------|----------|
| **Cat A:** No versioning on `AgentKnowledgeSource`; mutations untracked | **VERIFIED** | `core/models_unified_system.py:521-628` — no version field; only `last_updated_at` auto_now | `drift` | MEDIUM |
| **Cat B:** Redis-only state → worker recycle can lose recent learning | **VERIFIED** | `core/services/agent_learning_service.py:462-483` — `save_memory` at :476 writes via `redis_client.hset`; no DB writeback visible; grep for `setex`/`expire` returns 0 hits | `drift` | MEDIUM |
| **Cat B:** 14-day freshness window hardcoded in `ConversationOrchestrator` | **VERIFIED** | `core/conversation_orchestrator.py:749` — `freshness_cutoff = tz.now() - timedelta(days=14)`. Inline comment at :747-748 attributes to Session 988. No env var / setting | `drift` | LOW |
| **Cat C:** `MemoryPromotionService` scoring criteria opaque (EXPERIMENTAL) | **VERIFIED (criteria documented in this audit)** | `core/services/memory_promotion_service.py:119-172` — regex-only deterministic scoring; thresholds hardcoded at :234, :237 | `drift` | MEDIUM |
| **Cat C:** Consumer of `spider_context['pa_content_feedback']` UNKNOWN | **ESCALATED — CONFIRMED DEAD CODE** | See §14.3 F1 | `dead_code` | MEDIUM |

### 14.2 Silent-failure / silent-missing surfaces

Analogous to S1301 §14.2's silent-failure characterization, three
silent-missing surfaces exist in A/B/C:

1. **Embedding not generated** — nullable `embedding` field on
   all three category-primary models (AgentKnowledgeSource,
   ConversationMemory, AgentMemory). No monitor detects "row
   created but embedding missing." Retrieval silently misses
   such rows.
2. **Redis preferences dropped on worker recycle** — no
   observability on the loss event.
3. **MemoryPromotionService "PENDING" scores (5-6)** — logged
   but not surfaced to any queue or user; the log line at
   `memory_promotion_service.py:237-247` is the only trace.

### 14.3 Drift matrix (beyond parent §3)

| Drift | Doc claim | Runtime reality | Class | Severity | Evidence |
|-------|-----------|-----------------|-------|----------|----------|
| **F1 — `pa_content_feedback` produced, never consumed (ESCALATED FROM UNKNOWN)** | Session 990 handoff + KNOWLEDGE_RAG_MEMORY.md §6 describe intended agent-side consumption; PLATFORM_INVENTORY §3.13 line 1192-1194 documents the plumbing; parent §3 flagged consumer UNKNOWN | Whole-tree grep across `core/` + `ai_core/` finds 1 producer (`core/agent_router.py:766`); 0 code consumers. 14 doc references describe the intended consumer (esp. ContentWriterAgent) but no code implements it | `dead_code` | MEDIUM | Verifier-loop grep confirmed |
| **F2 — Row-level orphan write paths recur across A/B/C (INHERITED from S1301 §14.3 D3; FOLDED twice via Rigby SIGN cycles 1 + 2)** | Fields exist on models suggesting future consumers | **Final narrowed orphan list after Rigby SIGN cycle 2 grep-verification** (methodology: "no explicit-qualified references found on the model" — where `ModelName.field` grep returns 0 hits + no unqualified `.field` reference on a variable known to be an instance of ModelName): `AgentKnowledgeSource.feedback_positive/_negative` (only internal `+=1` increment; no external reader); `UserAgentLearning.context_metadata` + `.last_used` (record_success/failure writes; `UserAgentLearning.context_metadata` grep = 0 hits — Rigby cycle 2 verified; same-named field on `UserMemoryContext` IS read at `core/unified_memory_manager.py:218-219` but that is a different model); `AgentMemory.poison_risk_score` + `.poison_risk_factors` — **reclassified post-Rigby SIGN cycle 3 as NARROW-CONSUMER-SURFACE not orphan.** Consumed as a safety filter in `core/services/memory_embedding_service.py:222` (read via `getattr`) + `:261` (`queryset.exclude(poison_risk_score__gte=0.5)`). Read scope is limited to embedding-side safety exclusion; not integrated into broader learning loops or user-facing surfaces. Rigby cycle 3 fold: soften label from "orphan" to "narrow safety-filter consumer only"; `ConversationMemory.intent` (Django model — `ConversationMemory.intent` grep = 0 hits, Rigby cycle 2 verified). **Removed from orphan list after Rigby SIGN cycle 1 grep-verification:** `AgentKnowledgeSource.source_spider_names` (actively filtered/read at `core/tasks.py:3098` + `core/tasks_agents.py:3202, 3240, 3241, 3272, 3471` + `core/views_spider_intelligence.py`); `AgentKnowledgeSource.first_discovered_at` (actively read at `core/tasks_content.py:1893`, `core/tasks_agents.py:3236, 3265, 3938, 3953, 3980, 3994, 4008, 4305, 4323, 4348`, `core/project_intelligence_consumer.py:155, 186`); `AgentKnowledgeSource.feedback_adjusted_confidence` (read via `effective_confidence` computed property at `core/models_unified_system.py:612-613, 625-626` + analytics aggregation at `core/services/project_research_bridge.py:334`). **Removed from orphan list after Rigby SIGN cycle 2 grep-verification:** `AgentMemory.source_type` + `.source_id` + `.access_count` + `.last_accessed_at` — all four consumed by `core/views_memory_palace.py`: line :60 (order by `-last_accessed_at`), :86 (`last_accessed_at` in listing payload), :113-114 (update `access_count` and `last_accessed_at` on detail view), and source_type/source_id are returned in listing payload + used for AgentExecution join in `get_memory_detail`. `record_access` at `core/models_unified_system.py:11000-11001` writes both fields via `.save(update_fields=['access_count', 'last_accessed_at'])`. Revised orphan count: **~6 fields, down from v1's ~11 (cycle 1 removed 3, cycle 2 removed 4).** Pattern class still holds but is narrower than v1 claimed. **Epistemic caveat (Rigby methodology tightening):** "no explicit-qualified references found on the model" is the correct label for these ~6 fields — not "0 consumers"; unqualified `.field` references on a variable bound to the model at runtime could not be exhaustively excluded without AST-level tracing. | `drift` (populated-but-unread on the specific model) | MEDIUM | Agent 1 + Agent 6 grep receipts + Rigby SIGN cycles 1 + 2 grep-tightening |
| **F3 — `UserAgentLearning.expires_at` never enforced** | Schema field implies retention | No query filter uses it; no beat prunes based on it | `dead_code` (field) | LOW | Agent 6 grep |
| **F4 — `AgentLearningService` Redis keys have no TTL** | Redis-standard TTL implied | No `setex`/`expire` calls; preferences accumulate | `partial_implementation` | LOW | Agent 1 + Agent 6 grep |
| **F5 — `spider_data_bridge` naming implies Cat A but writes Cat B** | Narrative says "spider → knowledge → agent prompt injection" | `core/learning_bridges/spider_data_bridge.py:107-111` writes `UserAgentLearning` (Cat B), not `AgentKnowledgeSource` (Cat A) | `docs_stale` | LOW | Agent 4 direct read |
| **F6 — `MemoryPromotionService` writes `UserMemoryContext`, not `AgentMemory`** | Parent §3C names service under Cat C | Service writes into `UserMemoryContext` at :303-318, a user-scoped table | `docs_stale` (mis-categorization) | LOW | Verifier-loop direct read |

### 14.4 F1 escalation detail — `spider_context['pa_content_feedback']` dead code

**Why F1 is load-bearing:**

Session 990's promise was "PA reviews → agent behavior adapts."
The producer half of that loop wires `AgentMemory
memory_type='feedback' tags=['pa_review']` retrieval → summary
formatting → `spider_context['pa_content_feedback']` injection.
The consumer half — an agent prompt builder reading that key
and folding it into the LLM prompt — was never implemented.

**Grep receipts (parent-agent verified):**

```
$ grep -rn "pa_content_feedback" (whole tree)
core/agent_router.py:766:                    spider_context['pa_content_feedback'] = feedback_context['pa_review_feedback']
docs/topics/agent-system.md:85                — describes intended flow
docs/topics/content-pipeline.md:141           — describes intended flow
docs/handoffs/SESSION_990_...:49, :74, :102   — Session 990 producer wiring
docs/research/platform_architecture_inventory.md:1090, :1146, :1192, :2816, :3120 — inventory + gap tracking
docs/research/domains/memory/1300_...:152     — parent flagged UNKNOWN
docs/narratives/KNOWLEDGE_RAG_MEMORY.md:115, :294, :330 — narrative gap notes
docs/PLATFORM_INVENTORY.md:… (autoblock)
00-START-NEXT-SESSION.md:55                   — S1302 mission spec inherits question
```

15 total hits — 1 code producer, 14 doc references. Zero code
consumers.

**Analogous to S1301 §14.3 D3 pattern class:** two systems that
should be joined via a bridge; the bridge was never built. In
S1301's case: row-level `DocumentEmbedding.source_type` /
`ingested_via` fields (write side) + `docs/_provenance.json`
external index (read side) with no join. In F1's case:
`FeedbackLoopEngine → spider_context` (produce side) + agent
prompt builder (consume side) with no reader.

**F1 grep methodology (Rigby cycle 3 polish note):** the
`0 code consumers` claim is scoped to whole-tree grep across
`.py` files (playbook §14 grep-verify-binary-claims rule). Paths
searched: entire repo tree including `core/`, `ai_core/`,
`content/`, service modules, and PA/enrichment/agent-router
sites (no path restriction on the parent-agent verification
grep). Case-sensitive (Python identifier-conventional). Files
included: all `*.py` under `core/` + `ai_core/`. Files excluded
from the "code consumer" count: migrations (regenerable schema
state), tests (verification not consumption), documentation
(the 14 doc hits describe intent, not runtime consumption).
Producer site verbatim: `core/agent_router.py:766` — `spider_context['pa_content_feedback'] = feedback_context['pa_review_feedback']`.
Whole-tree grep result recorded in §20.3.

### 14.5 Cross-category drift patterns (recurring themes across A/B/C)

Per Agent 6 synthesis; parent-agent confirms via evidence
already documented in F1-F6 rows:

1. **Orphan write paths.** F1, F2 (narrower field list per Rigby SIGN cycle 1 fold), F3 — audit / tracking / provenance fields populated at write, never read. F1 is the highest-severity example (dead code across an entire feedback loop). F2 recurs in all three categories but with fewer fields than the v1 draft claimed; the narrowed set still shows the pattern, but the audit was overstated pre-fold.
2. **Hardcoded configuration.** 14-day window (B), score
   thresholds (C), `SHORT_TERM_LIMIT` in AgentLearningService
   (B); no operator surface.
3. **Redis coupling without durable fallback.** F4 (Cat B
   preferences); 7-day TTL cache in EmbeddingService (Cat A
   support). Loss on recycle accepted implicitly.
4. **Producer-only data.** F1 is the most severe (dead code);
   F2 is the widely-distributed variant (write-side
   instrumentation, no consumer).

---

## 15. Known Technical Debt

**Q26 — Technical debt with severity.**

| Debt item | Location file:line | Severity | Introduced | Blocks | Enables | Category |
|-----------|-------------------|----------|------------|--------|---------|----------|
| T1 — No versioning on `AgentKnowledgeSource` mutations | `core/models_unified_system.py:521-628` | MEDIUM | Session 400 (knowledge pipeline) | Audit trail; mutation rollback; conflict detection under concurrent writers | Knowledge accumulation pattern | A |
| T2 — `feedback_positive/negative` populated (internal `+=1`) but never externally consumed. **Narrowed post-Rigby SIGN cycle 1 fold** — `feedback_adjusted_confidence` REMOVED from T2 (it IS read via `effective_confidence` computed property at `core/models_unified_system.py:612-613, 625-626` + analytics aggregation at `core/services/project_research_bridge.py:334`). | `core/models_unified_system.py:589, 595` | LOW (downgraded from MEDIUM post-fold — narrower field surface) | UNKNOWN | User-facing feedback UI; agent-side feedback loop learning | Future feedback UI integration | A |
| T3 — `AgentLearningService` Redis-only state + no DB sync | `core/services/agent_learning_service.py:462-483` | MEDIUM | Session 991 | Durable learning across worker recycles | Fast per-process learning | B |
| T4 — 14-day freshness hardcoded (no env var / setting) | `core/conversation_orchestrator.py:749` | LOW | Session 988 | Dynamic tuning per-source; use-case-specific windows | Stale-data prevention | B |
| T5 — `ConversationMemory.expires_at` unenforced | `core/models/conversations/models.py:30` | LOW | Session 729 | Retention policy enforcement | Explicit expiration support in schema | B |
| T6 — `MemoryPromotionService` score thresholds hardcoded | `core/services/memory_promotion_service.py:234, :237` | MEDIUM | UNKNOWN (introduction session UNKNOWN) | Tuning aggressiveness; A/B threshold experimentation; operational alerting on pending | Score-gated memory promotion | C |
| T7 — `spider_context['pa_content_feedback']` produced but never consumed | `core/agent_router.py:766` | MEDIUM | Session 990 | PA-to-agent feedback learning; agent adaptation | Feedback loop completion | C |
| T8 — REMOVED post-Rigby SIGN cycle 2 fold. `AgentMemory.source_id` (and `.source_type`) are consumed by `core/views_memory_palace.py` — returned in listing payload and used for AgentExecution join in `get_memory_detail`. Not orphan. | ~~`core/models_unified_system.py:10918-10921`~~ | ~~LOW~~ | ~~Session 251~~ | n/a | Memory Palace visualization uses these fields | C |
| T9 — `AgentMemory.poison_risk_score` scored at create, never re-analyzed | `core/models_unified_system.py:10879-10889` | LOW | Session 768 | Risk monitoring dashboard | Embedding poison defense | C |
| T10 — No write authority gate on `AgentMemory.create_memory` | `core/models_unified_system.py:11004` | HIGH | Session 251 | Rogue PA-turn memory injection defense; rate limiting; audit of who created what | Open memory creation | C |
| T11 — `spider_data_bridge` name misdirects (writes B, not A) | `core/learning_bridges/spider_data_bridge.py:28-49` | LOW | S1115 | Onboarding clarity | Existing bridge implementation | A/B boundary |
| T12 — Nullable embedding on all A/B/C models with no coverage monitor | `AgentKnowledgeSource.embedding`, `ConversationMemory.embedding`, `AgentMemory.embedding` | MEDIUM | Ongoing | Coverage-drift detection; silent-missing observability | Opt-in embedding cost control | A/B/C |

No CRITICAL debt items. T10 (no write authority gate on
AgentMemory) is the highest-severity item — the persistence-
architecture rename made this the audit's primary lens.

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?**

Per Agent 2 + Agent 4 boundary check, verifier-loop-consolidated.

| Violation | Location | Severity | Nature |
|-----------|----------|----------|--------|
| B1 — `AgentLearningService` imports `agent_collaboration_hub` | `core/services/agent_learning_service.py:590` | LOW (intentional per S991 optional path) | Wrapped in try/except; optional collaboration path |
| B2 — `MemoryPromotionService` imports `_redact_secrets` from `tool_dispatcher` | `core/services/memory_promotion_service.py:253` | LOW | Utility import; content sanitization; isolated use |
| B3 — `EmbeddingService` (Cat A infrastructure) imported by 21 non-memory services | 21 sites across `core/services/`, `content/` | LOW (utility pattern) | Not a boundary violation — EmbeddingService is platform-utility infrastructure. Any code needing embeddings uses it. Clean reuse. |
| B4 — `spider_data_bridge` (Cat A ingress path) writes Cat B `UserAgentLearning` | `core/learning_bridges/spider_data_bridge.py:107-111` | LOW | Cross-category write via a bridge is by design; the naming drift (F5) is documented separately |

**No CRITICAL boundary violations.** No direct DB access
bypassing service layer for critical writes; no cross-domain
imports of retrieval private methods; no unsafe raw ORM access
outside intended layers.

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models overlap with other domains?**

Per Agent 1 + Agent 5, cross-referenced against S1301 §17.

### 17.1 Cite-not-re-answer boundaries with S1301

S1301 §17.1 (DocumentEmbedding vs AgentKnowledgeSource) resolved
that these are **NOT schema duplicates** — different retrieval
mechanisms, different content shapes. S1302 accepts that
verdict and does not re-litigate.

S1301 §17.2 (DocumentEmbedding vs UserEmbedding) surfaced the
Category D × Category B overlap surface and explicitly noted
"S1302 owns the persistence architecture question here; do not
resolve in this audit." S1302 folds this into its own overlap
analysis (see 17.5).

### 17.2 `AgentMemory` (Cat C Django model) vs `AgentMemory` (in-process, `agent_learning_service.py:111`)

**NAME COLLISION.** Two different classes share the same
identifier:

| Aspect | Django `AgentMemory` (`core/models_unified_system.py:10787`) | In-process `AgentMemory` (`core/services/agent_learning_service.py:111`) |
|--------|-----------------------------------------|-----------------------------------------|
| Kind | Django model | Python dataclass |
| Scope | Cross-session, per-agent, DB-durable | Per-process, per-user-per-agent, in-memory + Redis |
| Fields | memory_type, tags, valence, importance, safety_class, poison_risk_score, source_type, source_id, embedding, ... | short_term (list), long_term (dict of LearnedPreference) |
| Owner | Category C | Category B (auxiliary service data model) |

**Verdict:** Naming drift. **Namespace collision (naming-confusion
risk), NOT runtime collision.** The two classes live in different
modules (`core.models_unified_system` vs `core.services.agent_learning_service`);
no import path forces a caller to pick one over the other by
alias. There is no observed runtime bug where code intended to
use the Django model accidentally instantiated the dataclass or
vice versa. The concern is onboarding cognitive load + future-drift
risk if a caller writes `from core.services.agent_learning_service import AgentMemory`
without noticing it isn't the Django model. The in-process
class should be renamed (e.g., `AgentInteractionMemory`) but
that is implementation, not research. Documented here as an
overlap surface for future callers to disambiguate.

### 17.3 `ConversationMemory` (Cat B Django model) vs `ConversationMemory` (in-process, `core/conversation_memory.py:59`)

Same class of NAME COLLISION. Django `ConversationMemory` at
`core/models/conversations/models.py:19` is the per-user
pgvector-eligible persistence surface. In-process
`ConversationMemory` at `core/conversation_memory.py:59` is a
service-layer construct with different concerns (likely
short-lived context assembly). Two distinct classes.

**Verdict:** Naming drift. Not a schema duplicate. **Namespace
collision (naming-confusion risk), NOT runtime collision.** Same
disambiguation as §17.2: two classes live in different modules
(`core.models.conversations.models` vs `core.conversation_memory`);
no import path forces alias ambiguity; no observed runtime bug
of misused class. Concern is onboarding cognitive load + future
drift risk.

### 17.4 `UserMemoryContext` vs `AgentMemory` — cross-category write target confusion

`MemoryPromotionService.check_and_promote` at
`core/services/memory_promotion_service.py:303-318` writes
`UserMemoryContext` — a **user-scoped** table — even though
the service is documented under Category C (agent-scoped
episodic). This is an architectural inconsistency:

- Category B has an "adaptive memory" story about per-user
  behavior. `UserMemoryContext` fits that story.
- Category C has an "episodic memory" story about per-agent
  outcomes. `AgentMemory` fits that story.
- `MemoryPromotionService` sits in Category C by parent §3C but
  writes into a user-scoped Cat-B-like table.

**Verdict:** The service's category assignment in parent §3
should be reconsidered. This is a **routing question for S1399**
(canonical summary) rather than an in-audit resolution.

### 17.5 Two provenance systems (row-level A/B/C fields vs external `docs/_provenance.json`) — extends S1301 §17.4

S1301 §17.4 established that Category D has two provenance
systems (row-level DocumentEmbedding fields + external
`docs/_provenance.json`). S1302 finds the same pattern inside
A/B/C but with different semantics:

- **Cat A row-level (FOLDED post-Rigby SIGN cycle 1):** narrower orphan set — `AgentKnowledgeSource.feedback_positive/_negative` only. `source_spider_names`, `first_discovered_at`, `feedback_adjusted_confidence` all have active readers per Rigby grep-verification (§14.3 F2 fold note).
- **Cat B row-level:** `UserAgentLearning.context_metadata` +
  `.learning_source` — `learning_source` IS queried (exception),
  `context_metadata` is not (specific check on UserAgentLearning
  model, not the same-named field on `UserMemoryContext`).
  `UserAgentLearning.last_used` also written-not-externally-read.
- **Cat C row-level (FOLDED post-Rigby SIGN cycles 2 + 3):** narrower — `source_type` + `source_id` + `access_count` + `last_accessed_at` all consumed by `core/views_memory_palace.py` (order-by / listing payload / access-tracking writes; cycle 2 fold). `poison_risk_score` + `poison_risk_factors` are NARROW-CONSUMER-SURFACE (safety filter only) via `core/services/memory_embedding_service.py:222, :261`; cycle 3 fold. No AgentMemory field remains classified as strict-orphan-write.

**Pattern name:** producer-only row-level metadata. Recurs
across four categories in the platform (A, B, C, D). This is
a **cross-cutting pattern for S1399** to name in its canonical
summary if it holds across S1303 + S1304 as well.

### 17.6 Duplicate scoring / promotion mechanisms

- `MemoryPromotionService.score_for_promotion` (Cat C) —
  regex-only, deterministic, `UserMemoryContext` target.
- `promote_to_shared_knowledge` beat task (Cat A) — different
  logic, `SharedKnowledge` target.
- `auto_promote_low_risk_decisions` beat task (Cat C) —
  ai_promote_decisions target.

Three separate promotion mechanisms with three separate
scoring logics writing to three different tables. **Not
duplicates** — different concerns — but a topology worth
naming: memory subsystems have three parallel "promote to
long-term" paths with no shared authority framework.

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

The persistence-architecture rename made this section the
audit's headline concern. Per parent §5 P2 slot decision
(Chris-locked 2026-07-01): "the underlying question is
persistence + authority, not just overlap surfacing."

### 18.1 Write authority per category

| Category | Write authority current state | Enforcement | Gap |
|----------|-------------------------------|-------------|-----|
| A `AgentKnowledgeSource` | Unrestricted at model layer — `.objects.create()` / `.save()` callable from any code path | No `@permission_required`, no service gate, no writer whitelist | Which subsystems SHOULD be allowed to write knowledge? Currently: anyone. Cross-user shared table — no per-user isolation |
| B `UserAgentLearning` | Per-user FK enforces scope at schema level; direct ORM writes via `create_learning` classmethod | Schema-level isolation; NO query-time auth check (e.g., "ensure `current_user == row.user`") | Can any code path with a user reference write learning to any user? Isolation is by convention, not query gate |
| B `AgentLearningService` Redis prefs | No auth checks; in-process singleton accessible to any code with service reference | Process-scoped; no cross-process auth | Same worker process = same authority surface |
| B `ConversationMemory` (Django) | Per-user + per-conversation FK | Schema-level; direct write from PersonalAIOrchestrator | No query-time auth |
| C `AgentMemory` | `AgentMemory.create_memory` classmethod at `core/models_unified_system.py:11004` — takes `agent`, `title`, `content`. No user FK; no rate limiting | None — any code with agent reference can create | **Highest-severity gap**: `MemoryPromotionService` auto-saves on every PA turn. A rogue PA tool could trigger unlimited memory creation. Rate limiting absent. See T10 |
| C `UserMemoryContext` (written by MemoryPromotionService) | Per-user via score-gate + hash-dedup | Score gate at :234, :237; hash-dedup at :275-320 | Score gate is authority-adjacent (denies low-signal writes) but does not enforce writer identity — the service itself is the sole gatekeeper |

### 18.2 Ownership of cross-cutting surfaces

| Surface | Current owner | UNCLEAR rationale | Impact |
|---------|--------------|------------------|--------|
| `EmbeddingService` | Category A (as infrastructure) | Used by 21 non-memory callers including Cat B and Cat D consumers; naming ties it to A but role is platform-utility | Changes to EmbeddingService coordinate against a large blast radius; ownership needs to be "platform utility," not category-owned |
| `spider_context['pa_content_feedback']` | Producer: `agent_router.py` (routing layer). Consumer: NONE | Feedback loop broken at step 4 (§14.3 F1) | Data silently dropped |
| 14-day freshness policy | `ConversationOrchestrator` — hardcoded | No config owner; no A/B rationale documented | Static, blanket policy; no way to tune per source |
| `MemoryPromotionService` scoring policy | Category C service — embedded | Score thresholds hardcoded (T6); no SLA on ≥7 threshold; no operator-tuning surface | Operators can't tune aggressiveness; audit opacity |
| Embedding coverage (spider ~85%, other UNKNOWN) | Cross-category | Cadence for `AgentKnowledgeSource` embedding is opt-in (KNOWLEDGE_RAG_MEMORY.md §4); no monitor | Silent data loss on unembedded rows |

### 18.3 Category assignment ambiguities (§17 folded)

- `MemoryPromotionService` writes `UserMemoryContext` (user-scoped) but is categorized under Cat C (agent-scoped). Category assignment fits documentation intent, not runtime target. **S1399 candidate** to resolve.
- `spider_data_bridge` (Cat A per naming) writes `UserAgentLearning` (Cat B per data). **S1399 candidate** to reconcile terminology.

---

## 19. Recommended Future Research

**Q28 — Ranked by architectural uncertainty × risk × unblocked
flows.**

### 19.1 In-arc (Group 1300 child audits + summary)

| Rank | Recommended | Owner | Why S1302 surfaces it |
|------|-------------|-------|-----------------------|
| 1 | **S1399 Group 1300 Canonical Summary** — must resolve (a) row-level orphan-write drift class (Q: does S1301 D3 + S1302 F2 + expected S1303/S1304 findings comprise a formal pattern the platform names?); (b) MemoryPromotionService's Cat B vs Cat C categorization; (c) `spider_data_bridge` Cat A vs Cat B terminology; (d) the write-authority framework as a cross-arc anchor recommendation | Group 1300 P6 | S1302 alone cannot resolve cross-arc pattern classes; that is the summary's job |
| 2 | **S1303 Conversational / Thread Memory (Cat F)** — must own the `ConversationSession` ↔ `ConversationMemory` boundary (S1302's Cat B `ConversationMemory` and Cat F's session-thread state are adjacent surfaces) | Group 1300 P3 | Cat F has no §3 inventory row today; S1303 will land the row and clarify boundary |
| 3 | **S1304 Documentation Corpus ↔ RAG Boundary (E ↔ D)** — should verify if the orphan-write pattern recurs at the docs corpus provenance-index boundary; input to S1399 pattern-class question | Group 1300 P4 | Cross-boundary provenance question S1302 escalates |

### 19.2 Cross-arc follow-on

| Rank | Recommended | Owner | Why |
|------|-------------|-------|-----|
| 1 | **Group 1700 Observability — dead-code / producer-only detection** | Group 1700 | F1 (pa_content_feedback) is the most severe example; a general "producer-only" telemetry surface would catch this class before it ships |
| 2 | **Employee OS 1200s follow-up — Category G Mission Memory** | Employee OS | Parent §7 anti-scope; boundary between Cat C `AgentMemory` and `OpsRun` audit trail is unresolved and appears again in S1302 §9.1 (MissingConnection) |
| 3 | **Design-preparation ADR — write authority framework** | Post-S1399 | The write-authority gap (§18) is a design-preparation candidate. This audit surfaces the gap; a future ADR proposes a permission model / rate limiting / audit trail shape. **NOT this audit's job (playbook §14.5).** |

### 19.3 Not-recommended (research anti-patterns per playbook §14.5)

- **Do not propose implementation of write-authority gates
  here.** That is design-preparation-phase work. S1302 surfaces
  the gap; a future `authority: design-preparation` doc
  (post-S1399 synthesis) recommends a shape.
- **Do not propose consolidation of the two `AgentMemory` or
  two `ConversationMemory` classes here.** Renaming is
  implementation; audit only documents.
- **Do not propose retention policies or beat tasks for
  `UserAgentLearning.expires_at` or Redis TTL.** Those are
  operational choices for a design-preparation doc.

---

## 20. Appendix

### 20.1 Files inspected

Grouped by sub-agent.

**Agent 1 (Models & Persistence):**
- `core/models_unified_system.py:521-628` — AgentKnowledgeSource
- `core/models_unified_system.py:3912-4120` — UserAgentLearning
- `core/models_unified_system.py:10787-11100` — AgentMemory
- `core/models/conversations/models.py:19-56` — ConversationMemory (Django)
- `core/services/agent_learning_service.py:111-165` — in-process AgentMemory dataclass + Redis config
- `core/services/agent_learning_service.py:462-483` — save_memory (Redis-only)
- `content/migrations/0044_provenance_and_promotion.py` — sibling provenance-fields migration (S1301 D3 anchor)
- `core/learning_bridges/apps.py:32` — signal registration

**Agent 2 (Services & Runtime Flows):**
- `core/services/embedding_service.py:66-414` — EmbeddingService
- `core/services/agent_learning_service.py:122-758` — AgentLearningService
- `core/services/conversation_memory_service.py:64-445` — ConversationMemoryService
- `core/conversation_orchestrator.py:725-768` — _get_agent_knowledge (14-day gate at :749)
- `core/services/memory_promotion_service.py:119-338` — MemoryPromotionService (VERIFIED existence)
- `core/services/feedback_loop_engine.py:26-618` — FeedbackLoopEngine
- `core/agents/base_agent.py:1435-1510` — _get_relevant_knowledge_for_task
- `core/agent_router.py:760-780` — spider_context injection (feedback + knowledge)

**Agent 3 (APIs / Tools / Tasks / Commands):**
- `core/services/pa_tool_schemas.py:404, 1883, 1999, 2134, 2186` — 5 A/B/C-touching tools
- `core/services/td_handlers_core.py:1434, 1896, 1966, 2192` — handler entries
- `core/tasks.py:6260, 6268, 7879` — promotion tasks
- `core/tasks_misc.py:1201` — backfill (not beat-scheduled)
- `core/tasks_conversations.py:3539` — ConversationMemory writer (per PA turn)
- `core/urls.py:1670-1672, 1684-1694, 2092, 2108, 3544-3549` — memory/learning REST endpoints
- `core/management/commands/assign_memories_to_rooms.py`
- `core/management/commands/discover_learning_cohorts.py`
- `core/management/commands/sync_agent_learning.py:457`

**Agent 4 (Integrations):**
- `core/agent_router.py:765-776` — spider_context injection (feedback + knowledge blocks)
- `core/agents/base_agent.py:1435-1510` — knowledge consumer
- `core/personal_ai_orchestrator.py:158-166, :421` — ConversationMemory read + write
- `core/learning_bridges/spider_data_bridge.py:28-49, :107-111` — bridge writer
- `core/services/implementation_executor.py:428, :443` — AgentKnowledgeSource writer
- `core/services/feedback_loop_engine.py:145-176` — AgentMemory feedback reader
- `core/services/memory_embedding_service.py` — parallel embedding service (Agent 4 discovery)

**Agent 5 (Documentation & Prior Research):**
- `docs/topics/agent-system.md`, `personal-assistant.md`, `content-pipeline.md`, `local-askdocs.md`
- `docs/narratives/KNOWLEDGE_RAG_MEMORY.md` §1-§6
- `docs/KNOWLEDGE_PIPELINE.md`
- `docs/handoffs/SESSION_990/991/1115/1142/1158/1300/1301`
- `docs/research/platform_architecture_inventory.md` §3.13 + §5.4
- `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` §17 + §14.3 D3
- `docs/PLATFORM_INVENTORY.md` autoblock

**Agent 6 (Drift/Debt/Ownership/Maturity):**
- All files above, plus verification of every parent §3 known-drift bullet + F1 escalation grep

**Parent-agent verifier-loop reads (spot-checks):**
- `core/agent_router.py:760-784` — spider_context injection confirmation
- `core/conversation_orchestrator.py:740-770` — 14-day gate + Cat A/C read code
- `core/services/memory_promotion_service.py` grep — service existence confirmation
- Whole-tree `pa_content_feedback` grep — F1 dead-code escalation

### 20.2 Docs inspected (companion anchors + related traversed)

Full list in §11 tables. Prior-research inheritance in §11.4.

### 20.3 Grep patterns used

```bash
# F1 escalation
grep -rn "pa_content_feedback"

# MemoryPromotionService existence resolution
grep -n "class MemoryPromotionService\|def score_for_promotion\|def check_and_promote" core/services/memory_promotion_service.py

# 14-day freshness confirmation
grep -n "timedelta(days=14)\|freshness_cutoff" core/conversation_orchestrator.py

# Model file:line disambiguation
grep -rn "class AgentKnowledgeSource\|class AgentMemory\b\|class UserAgentLearning\|class ConversationMemory\b\|class AgentLearningService"

# Redis-only durability check
grep -n "save_memory\|_persist_interaction\|redis_client\.hset\|redis_client\.setex" core/services/agent_learning_service.py

# Orphan write path recurrence (per model, per field)
grep -rn "source_spider_names\|source_type\s*=\|source_id\s*=" core --include="*.py" | grep -v migration
grep -rn "context_metadata\s*=\|last_used\s*=" core --include="*.py" | grep -v migration
grep -rn "poison_risk_score\s*=\|access_count\s*=" core --include="*.py" | grep -v migration
```

### 20.4 Unresolved unknowns

- **`MemoryPromotionService` introduction session UNKNOWN** —
  service exists in production; no dedicated handoff located
  (Agent 5). `git log -S "MemoryPromotionService"` would surface
  it. Left as UNKNOWN.
- **Current `Document` table embedding coverage** — S1301
  addressed; S1302 not the owner.
- **AgentLearningService gather_context inline call site for
  `agent_learned_preferences`** — Agent 4 confirmed
  architecturally per KNOWLEDGE_RAG_MEMORY §2 + Session 991;
  exact file:line for the inline `spider_context['agent_learned_preferences']`
  assignment not located in this sweep. Hedged as SPECULATIVE
  for implementation trace, STRONG for architectural intent.
- **`feedback_tool` handler location** — Agent 3 identified
  schema at `core/services/pa_tool_schemas.py:404`; handler not
  located (likely in `td_handlers_ops.py` or
  `td_handlers_content.py`). Left as UNKNOWN; not load-bearing
  for the audit.
- **`AgentMemory.source_type` valid value set** — field is
  `CharField(blank=True)` with no `choices=`; no documentation
  or enum. What values are actually written? UNKNOWN.
- **Category B `learning_source` complete enum** — 6 values
  observed in filter clauses (`success_pattern`,
  `failure_analysis`, `performance_tracking`, `user_feedback`,
  `explicit_instruction`, `interaction_mining`). Whether the
  model choices constant is complete is not verified in this
  sweep.

### 20.5 Conflicts between sources (parent-agent resolutions)

- **`MemoryPromotionService` existence:** Agent 1 claimed zero
  grep hits for definition; Agent 2 gave file:line
  `core/services/memory_promotion_service.py:119-338`.
  Parent-agent grep resolved against Agent 2 — the service
  exists at `:119` and `:197`.
- **`AgentMemory` model file:line:** Agent 1 cited `10913, 10918`
  as internal field line numbers; Agent 6 cited `10787-11100` as
  the class range. Both consistent — Agent 6's range brackets
  the fields Agent 1 identified.
- **`ConversationMemory` — two classes with the same name:**
  Sub-agents referenced both `core/models/conversations/models.py:19`
  (Django) and `core/conversation_memory.py:59` (in-process).
  Parent-agent disambiguated: they are different constructs;
  the Django model is Cat B, the in-process class is service
  auxiliary.
- **Spider-bridge target:** Narrative KNOWLEDGE_RAG_MEMORY.md
  frames "spider → knowledge" (implies Cat A). Agent 4 direct
  read confirms `core/learning_bridges/spider_data_bridge.py`
  writes `UserAgentLearning` (Cat B). Terminology drift
  documented as F5.

### 20.6 Verifier-loop corrections

- Escalated F1 (`pa_content_feedback` consumer) from parent §3
  "UNKNOWN" → CONFIRMED DEAD CODE via whole-tree grep including
  `ai_core/`. This is the audit's headline finding.
- Reclassified `spider_data_bridge` category assignment as F5
  (docs_stale) — the bridge is named for Cat A ingest but the
  target row is Cat B.
- Reclassified `MemoryPromotionService` writer target as F6
  (docs_stale / mis-categorization) — writes `UserMemoryContext`,
  not `AgentMemory`. Category assignment in parent §3C fits
  documentation intent, not runtime target.

### 20.7 Rigby SIGN fold notes

**Cycle 1 (2026-07-01, fresh isolation pin `pa-1b9f0f5264484c6b`,
ownership_verified: chris, conversation_owner_match: true).**

Rigby SIGN cycle 1 provisional verdict: **SIGN-with-edits** —
one primary must-fix (F2 overstated), one unverified-in-pin
claim to lock down (F6 write target).

**Cycle 2 (2026-07-01, same fresh pin).** Rigby verdict:
**SIGN-with-edits (fold more, localized).** Cycle 1 folds
accepted; residual correction: **`AgentMemory.source_type` +
`.source_id` + `.access_count` + `.last_accessed_at` are NOT
orphan** — all four are consumed by `core/views_memory_palace.py`
(order by `-last_accessed_at` at :60; listing payload returns
`last_accessed_at`/`source_type`/`source_id` at ~:86; access
tracking write on detail view at :113-114; source_type/source_id
join to AgentExecution in `get_memory_detail` ~:121-133).
Parent-agent folded cycle 2:

- **MF4 (§14.3 F2 second narrowing) FOLDED.** Removed
  `AgentMemory.source_type` + `.source_id` + `.access_count` +
  `.last_accessed_at` from orphan list with explicit reader
  citations. Revised orphan count: ~6 fields (from cycle 1's
  ~9, from v1's ~11).
- **MF5 (§14.3 F2 methodology tightening) FOLDED.** Language
  updated from "0 consumers" to "no explicit-qualified references
  found on the model" per Rigby methodology note — the audit
  cannot exhaustively exclude unqualified `.field` references
  on a variable bound to the model at runtime without
  AST-level tracing, so the epistemic hedge is required.
- **MF6 (§17.5 Cat C row-level) FOLDED.** Bullet narrowed to
  `poison_risk_score` + `poison_risk_factors` only. Same
  reader-citation evidence as MF4.
- **MF7 (§15 T8) FOLDED.** T8 entry marked REMOVED with strikethrough
  and rationale (source_id consumed by Memory Palace); no
  replacement debt item needed since the field IS read.

Rigby also RE-VERIFIED in cycle 2:
- `UserAgentLearning.context_metadata` disambiguation: grep for
  `UserAgentLearning.context_metadata` = 0 hits. The
  `unified_memory_manager.py:218-219` reader is on
  `UserMemoryContext.context_metadata`, a different model.
  **Disambiguation claim STANDS** with epistemic hedge.
- `ConversationMemory.intent` (Django model) grep = 0 hits on
  `ConversationMemory.intent`; general `intent =` hits are on
  other unrelated models. Orphan claim STANDS.

Rigby SIGN cycle 2 explicit conclusions:
- **F2 direction is correct** — the "some write-only fields
  exist" pattern is real; the v1 draft overstated its scope.
- **F6 spider_data_bridge → UserAgentLearning target VERIFIED
  in-pin now** (cycle 2 was able to open the file where cycle 1
  hit the tool cap).
- **Edits required are localized** — after MF4-MF7 fold, Rigby
  expects SIGN-clean without needing new research arcs.

**Cycle 3 (2026-07-01, same fresh pin).** Rigby verdict: **SIGN-clean.**
One non-blocking residual note folded:

- **MF8 (§14.3 F2 poison_risk_* reclassification) FOLDED.**
  `AgentMemory.poison_risk_score` + `.poison_risk_factors` are
  NOT strict-orphan — they are consumed as a safety filter in
  `core/services/memory_embedding_service.py:222`
  (`getattr(memory, 'poison_risk_score', 0.0)`) + `:261`
  (`queryset.exclude(poison_risk_score__gte=0.5)`). Reclassified
  as NARROW-CONSUMER-SURFACE (safety filter only); not integrated
  into broader learning loops or user-facing surfaces. §14.3 F2
  and §17.5 Cat C row-level bullets updated with this softening.

Rigby also cycle 3 grep RE-VERIFIED:
- `UserAgentLearning.context_metadata` = 0 hits (stands).
- `UserAgentLearning.last_used` = 0 hits (stands).
- `ConversationMemory.intent` (Django model specifically) = 0 hits (stands).

Rigby final cycle 3 verdict:

> **Overall confidence after fold: High. Final verdict: SIGN-clean.**

Post-cycle-3 revised orphan / narrow-consumer classification:
- **Strict orphan (no explicit-qualified references found on the
  model):** `AgentKnowledgeSource.feedback_positive` +
  `.feedback_negative`; `UserAgentLearning.context_metadata` +
  `.last_used`; `ConversationMemory.intent` (Django model) — 5
  fields.
- **Narrow-consumer-surface (used only for safety filtering,
  not broader integration):** `AgentMemory.poison_risk_score` +
  `.poison_risk_factors` — 2 fields.

Total F2 pattern scope: 7 fields (down from v1's ~11). Pattern
class stands but is significantly narrower than the v1 draft
claimed.

**MF1 — F2 narrowing FOLDED.** Rigby grep-verified (via
`repo_tool.search`) that several fields I originally flagged as
"populated but never read" have active external readers:

- `AgentKnowledgeSource.source_spider_names` — read at
  `core/tasks.py:3098` (`source_spider_names__contains=[conv_tag]`),
  `core/tasks_agents.py:3202` (list comp), :3240-3241 (real-vs-synthesized
  filtering), :3272 (write-through composition), :3471
  (synthesis marker); `core/views_spider_intelligence.py`
  (spider intelligence assembly); `core/services/learning_pattern_engine.py`;
  `core/services/agent_intelligence_context.py`.
- `AgentKnowledgeSource.first_discovered_at` — read at
  `core/tasks_content.py:1893` (24h count),
  `core/tasks_agents.py:3236, :3265, :3938, :3953, :3980,
  :3994, :4008, :4305, :4323, :4348` (age computation +
  timestamp formatting across multiple beat/task paths),
  `core/project_intelligence_consumer.py:155, :186` (ordering
  + display).
- `AgentKnowledgeSource.feedback_adjusted_confidence` — read via
  the `effective_confidence` computed property at
  `core/models_unified_system.py:612-613, :625-626`
  (`self.feedback_adjusted_confidence or self.confidence_score`)
  + analytics aggregation at
  `core/services/project_research_bridge.py:334`
  (`Avg('feedback_adjusted_confidence')`).

Fold: §14.3 F2 row narrowed from ~11 fields to ~9 fields;
§14.5 pattern 1 recontextualized ("narrower field list than v1
claimed"); §17.5 Cat A row-level bullet updated; §15 T2
narrowed to `feedback_positive/_negative` only and downgraded
LOW severity. `feedback_adjusted_confidence` removed from T2
scope.

**MF2 — F6 (spider_data_bridge write target) VERIFIED by
parent-agent direct read.** Rigby flagged UNVERIFIED-in-pin due
to repo_tool time cap. Parent-agent ran the direct read: `core/learning_bridges/spider_data_bridge.py:240`:
```python
learning_entry, created = UserAgentLearning.objects.get_or_create(
    user=system_user,
    agent_name=agent_name,
    learning_domain=learning_domain,
    learning_source=f"spider:{spider_data.spider_name}",
    ...
)
```
Confirms the bridge writes `UserAgentLearning` (Category B), NOT
`AgentKnowledgeSource` (Category A) despite the module name
`spider_data_bridge` implying Cat A ingest. F5 claim STANDS
with direct-read receipt now in §20.7.

**MF3 — F2 tightening also affects Category A maturity.** Rigby
Q3 (understated maturity anywhere?) flagged possibly Cat A —
since `source_spider_names` is actively used in tasks and
views. Fold: Cat A maturity kept at PARTIAL (per §13) because
(a) F1 dead-code loop and Rigby's other risks stand, (b) the
Cat A verdict was already based on multiple factors beyond
F2's specific field set (see §13 evidence: no versioning +
opt-in embedding + orphaned `feedback_positive/_negative`
still hold). Cat A PARTIAL verdict RETAINED with rationale
updated to remove the source_spider_names / first_discovered_at
justifications.

**Additional Rigby observations (not blocking; noted for future
work):**

- Q1: EmbeddingService end-to-end flow (writes → embedding →
  retrieval → prompt → decisions) could be traced more
  explicitly. This audit traces it partially (§5.A + §7.1);
  full-trace expansion is a candidate for the S1399 canonical
  summary.
- Q4: Intentional-separation vs missing-integration distinction
  needs sharper framing on §9.1 MISSING inbound rows
  (Content Pipeline / Employee OS / Signal Engine). Fold:
  §9.1 already annotates each MISSING as "Agent 4 grep 0
  hits" (not "should be wired but broken"), matching S1301
  §9.1 pattern; no additional edit made in cycle 1.
- Q6: Rigby's riskiest-finding vote landed on T10 (before
  response truncation). Audit already ranks T10 as HIGH
  severity in §15 with the same rationale. No change needed.

**Rigby SIGN cycle 2 will be routed after this fold** to confirm
SIGN-clean or catch remaining edits.

**Final verdict cycle 1:** SIGN-with-edits (folded above).
Pending cycle 2 confirmation of SIGN-clean.

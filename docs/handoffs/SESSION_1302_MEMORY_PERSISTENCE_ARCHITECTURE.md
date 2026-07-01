---
session: 1302
status: closed (draft-audit landed, Rigby SIGN-clean after cycles 1 + 2 + 3, Chris commit-gated)
date: 2026-07-01
arc: Research Group 1300 (Memory / Knowledge / Embeddings) — child P2 (playbook §11.2 20-section audit template). Second child audit under the parent-with-children arc. Combined-category scope Categories A + B + C (Semantic Knowledge Memory / Personal-Adaptive Memory / Agent Working Memory) per parent §5 P2 slot renamed by Chris 2026-07-01 from "Memory Store Overlap Audit" to "Memory Persistence Architecture" to widen the frame from surface-level overlap to durability + write/read paths + write authority boundaries. Inherits S1301 §14.3 D3 row-level orphan-write pattern as first-order scope; escalates parent §3 UNKNOWN "spider_context['pa_content_feedback'] consumer" bullet to CONFIRMED DEAD CODE.
prs_merged: []
prs_open:
  - "S1302 audit + INDEX v14 + OPEN_ARCS + handoff + START-NEXT rotation (branch docs/session-1302-memory-persistence-architecture off main; commit-gated on Chris per playbook §16)"
prs_upstream:
  - "S1301 commit-gate on main (PRs #2775 = b54b2409 + #2776 = 5f6b9863) — resolved between S1301 close and S1302 open; S1302 branches off main, not stacked on S1301"
branches_open:
  - "docs/session-1302-memory-persistence-architecture (base = origin/main)"
companions:
  - docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md
  - docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md
  - docs/research/domains/memory/1300_memory_domain_scoping.md
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
deliverables:
  - "docs/research/domains/memory/1302_memory_persistence_architecture_audit.md (~1700 lines, status: draft, sign_status: SIGN-clean, authority: research, research_group: 1300, child_slot: P2; 20-section playbook §11.2 template; verifier_loop v1 synthesis + v1.1 Rigby SIGN cycle 1 fold + v1.2 Rigby SIGN cycle 2 fold + v1.3 Rigby SIGN cycle 3 fold — SIGN-clean)"
  - "docs/research/ARCHITECTURE_INDEX.md — v13 → v14; §1.17 row added; §8 timeline S1302 row added; owner-line updated with v13 + v14 entries (v13 was a drift-fix carrying over the S1301 missed owner entry)"
  - "docs/research/OPEN_ARCS.md — Group 1300 in-progress row current-child advanced from 'S1301 SIGN-clean (commit-gated) + S1302 queued' to 'S1302 SIGN-clean (commit-gated) + S1303 queued'; 3 reconciliation notes added (S1301 close, S1302 open, S1302 close)"
  - "docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md (this doc)"
  - "00-START-NEXT-SESSION.md — rotated to S1303 mission spec (Category F Conversational / Thread Memory)"
key_findings:
  - "F1 headline: spider_context['pa_content_feedback'] CONFIRMED DEAD CODE. Parent §3 flagged consumer as UNKNOWN; whole-tree grep across core/ + ai_core/ finds 1 producer at core/agent_router.py:766 and 0 code consumers. 14 doc references (topic docs, handoffs, narratives, PLATFORM_INVENTORY, parent §3, S1273 §3.13, KNOWLEDGE_RAG_MEMORY §6) describe the intended consumer (esp. ContentWriterAgent) that never became code. Session 990 producer half wired; agent-side consumer half never implemented. Analogous to S1301 §14.3 D3 'two systems, no bridge' class."
  - "F2 (row-level orphan write path inherited from S1301 §14.3 D3): narrowed across three Rigby SIGN cycles. v1 draft claim: ~11 fields populated at write, never read across A/B/C. Final classification after cycle 3 fold: 5 strict-orphan fields (AgentKnowledgeSource.feedback_positive + .feedback_negative; UserAgentLearning.context_metadata + .last_used; ConversationMemory.intent Django model — Rigby cycle 3 grep re-verified all = 0 hits on the specific model) + 2 narrow-consumer-safety-filter fields (AgentMemory.poison_risk_score + .poison_risk_factors — consumed for safety exclusion at core/services/memory_embedding_service.py:222 + :261). Pattern class stands but scope is significantly narrower than v1 claimed."
  - "F5: spider_data_bridge (named for Cat A ingest per KNOWLEDGE_RAG_MEMORY.md narrative) actually writes Cat B UserAgentLearning at core/learning_bridges/spider_data_bridge.py:240 via UserAgentLearning.objects.get_or_create(...). Docs_stale terminology drift."
  - "F6: MemoryPromotionService (categorized under Cat C by parent §3C) writes UserMemoryContext (user-scoped table) at core/services/memory_promotion_service.py:303-318, NOT AgentMemory directly. Category-assignment drift."
  - "T10 HIGH severity: no write authority gate on AgentMemory.create_memory at core/models_unified_system.py:11004. No user FK; no rate limiting; MemoryPromotionService auto-saves on every PA turn without gate. Rigby cycle 2 riskiest-finding vote confirmed already-ranked HIGH in §15 debt matrix."
  - "MemoryPromotionService scoring criteria — deterministic regex patterns at core/services/memory_promotion_service.py:119-172: +3 milestone (max once), +2 per identifier type cap +6 across 11 identifier types (bundle_id, android_package, version_build, repo_slug, git_url, commit_sha, railway_service, base_url, worker_queue, port_binding, docker_image), +2 wiring (max once), -10 secret hard block. Thresholds hardcoded at :234 (≥7 auto-save), :237 (5-6 pending log-only); not configurable. Deterministic, no LLM. Resolves parent §3C 'scoring criteria opaque' UNKNOWN."
  - "14-day freshness window at core/conversation_orchestrator.py:749 verbatim `freshness_cutoff = tz.now() - timedelta(days=14)`. Hardcoded, no env var/setting. Session 988 origin per :747-748 comment. Gates both AgentKnowledgeSource (Cat A) and AgentMemory (Cat C) queries in _get_agent_knowledge."
  - "AgentLearningService Redis-only durability confirmed: save_memory at core/services/agent_learning_service.py:462-483 writes via redis_client.hset at :476 with no DB backup; grep for .expire() = 0 hits; no TTL enforcement. Worker recycle drops in-memory _user_memories cache; Redis state depends on save_memory being called before recycle."
  - "Two name collisions documented (§17.2, §17.3): (a) Django AgentMemory at core/models_unified_system.py:10787 vs in-process dataclass at core/services/agent_learning_service.py:111 — different constructs, same identifier. (b) Django ConversationMemory at core/models/conversations/models.py:19 vs in-process class at core/conversation_memory.py:59. Not schema duplicates; naming drift only."
  - "Combined-subsystem maturity verdicts: Cat A PARTIAL (knowledge accumulation works; no versioning + opt-in embedding silent-missing failure mode + orphaned feedback fields); Cat B PARTIAL (Postgres side WORKING with active learning_source filter at core/services/td_handlers_ops.py:5965/5986/6000; Redis side PARTIAL loss-on-recycle); Cat C EXPERIMENTAL (downgraded from WORKING due to F1 dead-code loop — auto-promotion pipeline runs but downstream feedback consumer is broken)."
  - "§19 downstream routing established: S1303 owns Cat F Conversational/Thread Memory (ConversationSession ↔ ConversationMemory boundary — S1302 name-collision + adjacency handoff); S1304 owns E ↔ D Docs Corpus ↔ RAG Boundary; Group 1700 Observability owns dead-code / producer-only detection surface (F1 is highest-severity example); S1399 canonical summary owns row-level orphan-write pattern class definition + write-authority framework anchor recommendation + MemoryPromotionService Cat B vs Cat C reassignment + spider_data_bridge naming reconciliation."
open_decisions_carried_forward:
  - "Chris commit-gate on S1302 branch — audit + INDEX v14 + OPEN_ARCS + handoff + S1303 START-NEXT rotation all landed on working tree; single commit-clean gesture would land the whole session's artifact set. Playbook §16 requires explicit 'commit it' from Chris."
  - "Fresh isolation pin pa-1b9f0f5264484c6b retirement — SIGN cycles 1+2+3 complete; pin may retire at Chris's discretion after commit."
  - "S1303 launch cadence — playbook default is 'immediate on session open' but Chris may want a pause to review S1302 audit findings first. Not blocking S1302 close."
rigby_sign_cycle_1:
  fresh_isolation_pin: "pa-1b9f0f5264484c6b"
  pin_title: "S1302 SIGN — Memory Persistence Architecture audit pressure-test (isolation)"
  ownership_verified: "chris (conversation_owner_match: true)"
  provisional_verdict: "SIGN-with-edits — F2 orphan-fields claim overstated per Rigby grep-verification: AgentKnowledgeSource.source_spider_names (reads at core/tasks.py:3098, core/tasks_agents.py:3202/3240/3241/3272/3471, core/views_spider_intelligence.py); .first_discovered_at (reads at core/tasks_content.py:1893, core/tasks_agents.py:3236/3265/3938/3953/3980/3994/4008/4305/4323/4348, core/project_intelligence_consumer.py:155/186); .feedback_adjusted_confidence (read via effective_confidence computed property at core/models_unified_system.py:612-613/625-626 + Avg() aggregation at core/services/project_research_bridge.py:334). F6 spider_data_bridge write target UNVERIFIED-in-pin (repo_tool time cap)."
  must_fix_folded:
    - "MF1 (§14.3 F2 narrowing) — removed 3 fields from orphan list with reader citations; §14.5 pattern 1 recontextualized; §17.5 Cat A row-level bullet narrowed; §15 T2 narrowed to feedback_positive/_negative + downgraded MEDIUM → LOW."
    - "MF2 (§14.3 F5 + F6 spider_data_bridge target) VERIFIED via parent-agent direct read of core/learning_bridges/spider_data_bridge.py:240 — UserAgentLearning.objects.get_or_create(...) confirms bridge writes Cat B not Cat A."
  additional_observations_deferred:
    - "Q1 EmbeddingService end-to-end trace expansion → deferred to S1399 canonical summary."
    - "Q4 intentional-vs-accidental §9.1 framing already handled via 'Agent 4 grep 0 hits' annotation matching S1301 pattern."
    - "Q6 T10 riskiest-finding vote → already ranked HIGH in §15."
rigby_sign_cycle_2:
  same_isolation_pin: "pa-1b9f0f5264484c6b (fresh pin preserved across cycles per playbook §15 fold cycle)"
  provisional_verdict: "SIGN-with-edits (fold more, localized) — AgentMemory.source_type + .source_id + .access_count + .last_accessed_at are NOT orphan; all four consumed by core/views_memory_palace.py (order by -last_accessed_at at :60; listing payload return at :86; access-tracking write on detail view at :113-114; source_type/source_id join to AgentExecution in get_memory_detail). Methodology tightening required: '0 consumers' → 'no explicit-qualified references found on the model' (Rigby epistemic hedge; unqualified .field references on variables bound to model at runtime cannot be exhaustively excluded without AST-level tracing)."
  must_fix_folded:
    - "MF4 (§14.3 F2 second narrowing) — removed 4 AgentMemory fields from orphan list with Memory Palace reader citations. Revised orphan count: ~6 fields (from cycle 1's ~9, from v1's ~11)."
    - "MF5 (methodology tightening) — language across §14.3 F2 + §14.5 pattern 1 updated to 'no explicit-qualified references found on the model'."
    - "MF6 (§17.5 Cat C row-level) — bullet narrowed to poison_risk_score + poison_risk_factors only."
    - "MF7 (§15 T8) — entry marked REMOVED (source_id consumed by Memory Palace)."
  re_verified_in_cycle_2:
    - "UserAgentLearning.context_metadata grep = 0 hits on the specific model (disambiguation from same-name field on UserMemoryContext stands)."
    - "ConversationMemory.intent (Django model specifically) grep = 0 hits (same-name 'intent =' hits in tree are on other unrelated models)."
    - "F6 spider_data_bridge → UserAgentLearning target now VERIFIED in-pin (cycle 2 opened the file where cycle 1 hit tool cap)."
rigby_sign_cycle_3:
  same_isolation_pin: "pa-1b9f0f5264484c6b"
  final_verdict: "SIGN-clean. Overall confidence: High."
  non_blocking_residual_folded:
    - "MF8 (§14.3 F2 poison_risk_* reclassification) — AgentMemory.poison_risk_score + .poison_risk_factors are consumed by core/services/memory_embedding_service.py:222 (via getattr) + :261 (via queryset.exclude(poison_risk_score__gte=0.5)). Reclassified from orphan → NARROW-CONSUMER-SURFACE (safety filter only); not integrated into broader learning loops or user-facing surfaces. §14.3 F2 + §17.5 Cat C bullets softened with safety-consumer note."
  re_verified_in_cycle_3:
    - "UserAgentLearning.context_metadata = 0 hits (stands)."
    - "UserAgentLearning.last_used = 0 hits (stands)."
    - "ConversationMemory.intent (Django model) = 0 hits (stands)."
  final_orphan_classification:
    strict_orphan: 5
    strict_orphan_fields:
      - "AgentKnowledgeSource.feedback_positive"
      - "AgentKnowledgeSource.feedback_negative"
      - "UserAgentLearning.context_metadata"
      - "UserAgentLearning.last_used"
      - "ConversationMemory.intent (Django model)"
    narrow_consumer_safety_filter: 2
    narrow_consumer_fields:
      - "AgentMemory.poison_risk_score"
      - "AgentMemory.poison_risk_factors"
    total_under_F2_pattern: 7
    down_from_v1_claim: "~11 (cycle 1 removed 3, cycle 2 removed 4, cycle 3 reclassified 2 to narrow-consumer)"
next_session_readiness:
  - "S1303 mission is well-scoped by parent §3F + S1302 §17.3 name-collision surface + S1302 §19.1 downstream routing. Category F (Conversational / Thread Memory) is the first sub-domain without any §3 inventory row today; S1303 will land the first inventory pass."
  - "S1302 sub-agent Explore pattern (playbook §13) validated end-to-end for the second time — parent-agent verifier-loop spot-checks caught Agent 1 vs Agent 2 conflict on MemoryPromotionService existence before Rigby SIGN. The loop works."
  - "Three-cycle Rigby SIGN fold discipline validated for combined-category child audits. Cycle 1 large correction, cycle 2 second-order correction with methodology tightening, cycle 3 SIGN-clean with one narrow-consumer reclassification. Fresh isolation pin re-used across cycles per playbook §15 fold-cycle pattern."
  - "S1302 established that 'orphan write path' is a real class but requires per-field verification, not blanket claims. Future audits (S1303, S1304) should apply the same 'no explicit-qualified references found on the model' methodology when characterizing populated-but-unread fields."
memory_rule_touches:
  - "feedback_pa_local_verify_ownership.md — S1302 confirmed ownership on both arc pin (pa-aa54193f240f4846) and fresh isolation SIGN pin (pa-1b9f0f5264484c6b). Both = chris. Both match confirmed at pin creation."
  - "feedback_claude_directs_rigby_then_verifies.md — S1302 open executed the pattern: service_context: local check directive → Rigby ran platform_config_tool overview → Claude verified. SIGN routing directive → Rigby ran fresh-pin session_tool.create_fresh → Claude verified pin ID + ownership. F1 escalation directive → Rigby ran whole-tree grep → Claude verified against ai_core/ blind spot check."
  - "feedback_rigby_tool_verification.md — S1302 SIGN cycle 1 provisional verdict looked like 'F2 mostly overstated' but reading the Tool Runs block showed Rigby had grep-hit specific reader citations across multiple files; the SIGN-with-edits verdict was substantive not procedural."
  - "feedback_docs_pipeline_4_step_cascade.md — S1302 handoff, INDEX v14, OPEN_ARCS advancement, and audit all get pushed to Documents + embedded via the 4-step cascade after Chris commit. Not run in this session."
  - "feedback_session_tool_retire_works.md — carries forward the S1301 close verification that session_tool.retire works cleanly. S1302 SIGN pin retirement is a candidate for the same discipline after commit."
  - "feedback_verifier_loop_pattern.md — S1302 exercised the pattern across three SIGN cycles: parent-agent verifies EVERY quantitative claim + file path via direct Django ORM read / grep receipt / file read before including in the audit. Caught Agent 1's incorrect 'MemoryPromotionService location unknown' claim; caught the F5 spider_data_bridge target ambiguity; front-ran Rigby's cycle 1 F2 grep-verification by running the same greps parent-side after cycle 1 verdict landed."
followup_queue:
  - "S1303 Conversational / Thread Memory (Category F — first inventory-row landing for this sub-domain) (playbook §22 queue)"
  - "S1304 Documentation Corpus ↔ RAG Boundary (Categories E ↔ D) — inherits provenance-boundary questions from S1301 + S1302"
  - "S1305 Runtime Memory Correctness (Category H narrow scope — Redis-loss + lru staleness)"
  - "S1399 Group 1300 Canonical Summary — cross-cutting synthesis; must resolve (a) row-level orphan-write drift class formalization, (b) MemoryPromotionService Cat B vs Cat C category assignment, (c) spider_data_bridge naming reconciliation, (d) write-authority framework anchor recommendation for PLATFORM_INVENTORY §3.13 update"
  - "Group 1700 Observability filter-drop + dead-code / producer-only detection telemetry follow-on"
  - "Design-preparation ADR (post-S1399) — write authority framework for A/B/C. NOT this audit's job (playbook §14.5)."
owner: claude (drafted S1302)
---

# Session 1302 — Memory Persistence Architecture (Group 1300 Child P2)

## Session shape

**Mission (opened by Chris short command 2026-07-01):** *"please begin Session 1302"* — the playbook §21 continuation form on the second child audit under Research Group 1300 (Memory / Knowledge / Embeddings).

**Executed contract:**
- Playbook §21 continuation → §11.2 20-section child-audit template.
- Playbook §13 6-parallel-Explore sub-agent sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity).
- Parent-agent verifier-loop spot-checks per playbook §13 synthesis step 2 (front-ran Rigby's `pa_content_feedback` whole-tree grep, MemoryPromotionService existence check, 14-day freshness constant read, spider_data_bridge write target direct-read).
- Playbook §15 stage-scoped Rigby routing: full SIGN required on child audits; routed to a fresh isolation pin (`pa-1b9f0f5264484c6b`) per fresh-pin discipline. Three fold cycles.
- Playbook §16 commit policy: draft-first, Chris commit-gate.

**Session close criteria met per playbook §14 completion contract:**
- Audit doc at `status: draft`, `sign_status: SIGN-clean`, all 20 sections populated with cited evidence + honest UNKNOWNs + Rigby SIGN fold history.
- Rigby SIGN cycles 1 + 2 + 3 → SIGN-clean after three localized fold cycles (F2 narrowing, AgentMemory field reclassification, poison_risk_* narrow-consumer reclassification).
- INDEX v14 registration (§1.17 + §8 timeline row + frontmatter bump + owner-line update with v13 drift-fix + v14 addition).
- OPEN_ARCS Group 1300 row current-child advancement + 3 reconciliation notes (S1301 close, S1302 open, S1302 close).
- This handoff.
- 00-START-NEXT-SESSION.md rotated to S1303.

## What the audit found (executive)

Categories A + B + C form the Donkey Betz **memory persistence surface** — the durable-and-semi-durable stores that carry semantic knowledge, per-user adaptation, and agent working memory across sessions. They share the model `Agent` as an FK anchor, they share the vector-embedding infrastructure (`EmbeddingService`), and they share the same platform-level authority question the P2 rename made explicit: *who is allowed to write into each store, and how is that enforced?* The audit's answer, category by category, is largely **unrestricted at the model layer, gated by convention at the service layer, and unmeasurable by observability.**

Six subsystems in scope across three durability tiers. Category A is Postgres-durable via `AgentKnowledgeSource` (`core/models_unified_system.py:521`) with `EmbeddingService` writing embeddings + 7-day Redis cache. Category B splits across two durability tiers — durable `UserAgentLearning` (`:3912`) + durable pgvector `ConversationMemory` (`core/models/conversations/models.py:19`), plus **Redis-only** per-user preference state in `AgentLearningService` (`core/services/agent_learning_service.py:122`, 795 lines). Category C is Postgres-durable via `AgentMemory` (`:10787`), written by `MemoryPromotionService` (`core/services/memory_promotion_service.py:119`, score-gated) and consumed by `FeedbackLoopEngine` (`core/services/feedback_loop_engine.py:26`, 618 lines).

**The subsystem verdict is PARTIAL for A + B and EXPERIMENTAL for C.** Category C was downgraded from WORKING because the **biggest downstream feedback loop is dead-coded at the consumer side** — `pa_content_feedback` produced at `core/agent_router.py:766`, never consumed. Whole-tree grep across `core/` + `ai_core/` finds 1 producer + 0 code consumers. The 14 doc references (topic docs, handoffs, narratives, PLATFORM_INVENTORY, parent §3, S1273 §3.13, KNOWLEDGE_RAG_MEMORY §6) describe the intended consumer (esp. ContentWriterAgent) that never became code. Session 990's producer half of the PA-to-agent feedback loop is intact; the agent-side consumer half never landed.

**Three cross-category drift patterns** repeat across A + B + C: (a) orphan write paths — audit / provenance / tracking fields populated at write time, never read; final scope 5 strict-orphan + 2 narrow-consumer-safety-filter fields after three Rigby SIGN fold cycles narrowed the v1 draft's ~11 to 7 total; (b) hardcoded configuration — 14-day freshness window at `core/conversation_orchestrator.py:749`, MemoryPromotionService score thresholds at `:234, :237`, safety_class gates all magic numbers; (c) Redis coupling without durable fallback — B's Redis preferences (`AgentLearningService.save_memory` via `redis_client.hset` at `:476`, no DB backup) and A's embedding cache both accept loss-on-recycle without a documented recovery path.

**T10 HIGH severity finding:** no write authority gate on `AgentMemory.create_memory` at `core/models_unified_system.py:11004`. No user FK; no rate limiting; `MemoryPromotionService` auto-saves on every PA turn. This is the riskiest finding per Rigby's cycle 2 vote — the persistence-architecture rename made §18 (Ownership Gaps — write authority framework) the audit's headline lens. Every category has unrestricted model-layer writes; per-user isolation for Cat B is schema-only (FK), not query-time enforced.

**§19 downstream routing:**
- S1303 owns Cat F Conversational/Thread Memory (ConversationSession ↔ ConversationMemory boundary + name-collision resolution — S1302 §17.3 documented the Django model vs in-process construct split).
- S1304 owns E ↔ D Docs Corpus ↔ RAG Boundary.
- Group 1700 Observability owns dead-code / producer-only detection (F1 is highest-severity example).
- S1399 canonical summary owns the row-level orphan-write pattern classification + write-authority framework anchor recommendation for PLATFORM_INVENTORY §3.13 update + MemoryPromotionService Cat B vs Cat C category assignment resolution + spider_data_bridge naming reconciliation.
- Design-preparation ADR for write authority framework: NOT this audit's job (playbook §14.5).

## What did NOT get done

- **No commit landed on `main` or on the S1302 branch.** Per playbook §16, Chris commit-gate is explicit. All artifacts on working tree.
- **No implementation PRs.** Playbook §14.5 forbids implementation during research; the audit is design-input, not design.
- **No `MemoryPromotionService` git-history trace.** Origin session UNKNOWN per S1302 §20.4. `git log -S "MemoryPromotionService"` would surface it.
- **No `ConversationMemory` embedding coverage measurement.** Cat B `ConversationMemory` has nullable embedding; backfill not beat-scheduled. Coverage snapshot deferred to S1303 or ops instrumentation.
- **No write authority ADR.** T10 HIGH-severity gap surfaced; design-preparation ADR is post-S1399 work per playbook §19.3.

## Session-close artifacts on the working tree (uncommitted)

```
docs/research/domains/memory/1302_memory_persistence_architecture_audit.md   [new, ~1700 lines]
docs/research/ARCHITECTURE_INDEX.md                                            [modified, v13 → v14, §1.17 + §8 timeline S1302 row]
docs/research/OPEN_ARCS.md                                                     [modified, Group 1300 row advanced + 3 reconciliation notes + last_updated]
docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md                  [new, this doc]
00-START-NEXT-SESSION.md                                                       [modified, S1303 mission spec]
```

## Ready-to-commit single gesture

```bash
git add docs/research/domains/memory/1302_memory_persistence_architecture_audit.md \
        docs/research/ARCHITECTURE_INDEX.md \
        docs/research/OPEN_ARCS.md \
        docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md \
        00-START-NEXT-SESSION.md
git commit -m "docs(session-1302): Memory Persistence Architecture audit + INDEX v14"
```

Chris commit-gate required per playbook §16.

## Reference — where things are

- **S1302 audit:** `docs/research/domains/memory/1302_memory_persistence_architecture_audit.md`
- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Sibling audit (Cat D):** `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.13 + §5.4
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Category A models:** `core/models_unified_system.py:521-628` (AgentKnowledgeSource)
- **Category B models:** `core/models_unified_system.py:3912-4120` (UserAgentLearning); `core/models/conversations/models.py:19-56` (ConversationMemory Django); Redis prefs in `core/services/agent_learning_service.py:122+`
- **Category C models:** `core/models_unified_system.py:10787-11100` (AgentMemory)
- **Central services:** `core/services/embedding_service.py:66-414`; `core/services/agent_learning_service.py:122-758` (795 lines); `core/services/memory_promotion_service.py:119-338`; `core/services/feedback_loop_engine.py:26-618`; `core/conversation_orchestrator.py:725-768`
- **Dead-code F1 producer site:** `core/agent_router.py:766`
- **Fresh SIGN pin (retirable at Chris discretion):** `pa-1b9f0f5264484c6b`

## Pin state

- **Arc pin (Group 1300 continuity):** `pa-aa54193f240f4846` — carries S1300 + S1301 + S1302 mission-side context. Preserved for S1303 continuity.
- **SIGN isolation pin (S1302 only):** `pa-1b9f0f5264484c6b` — SIGN cycles 1 + 2 + 3 complete + SIGN-clean. May retire at Chris's discretion after commit.

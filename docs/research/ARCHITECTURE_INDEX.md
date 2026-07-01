---
title: "Architecture Research Index — front page of Donkey Betz's engineering encyclopedia"
status: active
authority: navigation
session_added: 1268
last_verified: 2026-07-01 (v22 — **Group 1400 Revenue arc Child C (Engagement Inbound) audit S1403 shipped.** §1.25 `domains/revenue/1403_revenue_engagement_inbound_audit.md` added (S1403 Child C audit — Engagement Inbound; 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category C evidence surfaces + parent-Claude verifier-loop pre-SIGN corrections on 2 sub-agent claims + Rigby SIGN cycles 1+2 on fresh isolation pin `pa-fba0c4c81fba4922` → SIGN-clean cycle 2 High confidence after cycle 1 fold (must-fix #1 empirically CLOSED via parent-Claude Django ORM count — all 4 Category C tables = 0 rows local; must-fix #2 withdrawn as Rigby cycle-1 response artifact + 4 Q-answer folds Q1/Q4/Q5/Q6; cycle 2 SIGN-clean + 3 Q-answer folds Q7/Q8/Q9 + 2 nice-to-have folds Env Coverage Table + T.C8 three-checkbox split). §8 timeline S1403 row added. **Load-bearing findings for Category C:** (a) F.C1 ingestion path missing — CONFIRMED HIGH at CODE + RUNTIME LOCAL tiers (`EngagementEvent.objects.count() = 0` via Django ORM; grep zero-writers at HEAD `d91d30f7`; both `outreach_draft` and `opportunity` FKs schema-only — extends S1402 F.B3 with the second-FK evidence parent scoping doc + S1402 both undernamed; PROD tier UNKNOWN due to Rigby `db_health_tool env=prod` "not configured" — logged as T.C8(c) tool gap); (b) F.C2 corrected axis map — dual-sub-agent verified (Agents 1 + 5 independently refuted parent §3 Cat C hypothesis with matching evidence); actual runtime axis is **three independent surfaces** — EngagementEvent event-log axis is architecturally-declared but runtime-empty; session-aggregation axis (EngagementMetrics + OpportunityInteraction) lives at `revenue_opportunities_consumer.py:849/527/694` WebSocket-consumer dual-write; ContentEngagement is orthogonal content-pipeline learning surface with no FK bridge back to inbound engagement; OpportunityInteraction is detail-child of EngagementMetrics via nullable `engagement_session` FK, not a join artifact; (c) F.C3 OpportunityInteraction F2 orphan-write CONFIRMED at writer-site `views_opportunities.py:56-65` REST `quick_apply()` — omits `engagement_session` FK that WebSocket path always populates; runtime blast radius LOCAL bounded to ZERO (`OpportunityInteraction.objects.count() = 0`) — sibling to S1402 F.B2 zero-blast-radius pattern via a different mechanism (S1402 was dead-code; S1403 is empty-parent-write-path); PROD blast radius UNKNOWN pending T.C8; (d) F.C4 ContentEngagement docstring drift — CONFIRMED HIGH docstring / MEDIUM runtime — `models_pipeline_feedback.py:372-378` claims "closes the learning loop" but no FK to EngagementEvent/Metrics/OpportunityInteraction; runtime bridge does not exist; Rigby cycle 1 Q5 lean (i) narrow docstring NOW + post-arc FK bridge if still desired; (e) F.C5 EngagementAutonomyEngine docstring drift — CONFIRMED LOW-severity — `engagement.py:774` lists "Reply context builder (outreach, opportunity, meeting history)" but no such method exists in the 4-method surface; Rigby cycle 1 Q6 lean (iii) reframe as "planned surface"; (f) F.C6 `run_ops_autopilot` deferred-by-policy — CONFIRMED via Rigby ops probe + parent-Claude direct read jointly (analogous to S1402 D.B7 methodology extension — same joint-verifier-loop pattern) — `run_ops_autopilot` beat wrapper defined at `core/tasks.py:13090` with declared 10min cadence docstring but NOT registered as PeriodicTask (0 of 92 enabled PeriodicTask rows match `ops_autopilot`; 30d `celery_task_history` → 0 firings); intentionally deferred per AUDIT_FINDINGS.md #12 gating (`core/celery.py:507-509` + `:633-634` name it as behavior-changing task awaiting explicit green-light); ad-hoc PA-tool invocation path LIVE at `td_handlers_ops.py:1643,1674`; consequence: Category C's `evaluate()` sweeps fire only when operator triggers autopilot ad-hoc, never on autonomous cadence; memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN to correctly classify as INHERITED-BY-POLICY not new bug; Rigby cycle 2 Q1 lean (iii) separate ADR outside G1400 arc since cross-category impact spans all 6 Category A/B/C/D/E/F policy hooks. **Load-bearing sub-agent + verifier-loop corrections:** Agent 6 T.C4 CANDIDATE dead-code risk for EngagementAutonomyEngine REFUTED via direct read of `core.py:2390-2418` (`_policy_engagement_autonomy` has LIVE invoker at :2404). Agent 5 F2 CANDIDATE at `views_opportunities.py:56-65` UPGRADED to CONFIRMED writer-site via direct read (F.C3). Agent 2 undercount 6 PA tools + Agent 3 undercount 3 PA tools RECONCILED to 9 total surface actions via grep of `td_handlers_ops.py:2808-2885` + `:3102-3122`. **Category C classifications:** Coverage MODERATE (upgraded from LIGHT). Maturity **WORKING (code) / DEFERRED-BY-POLICY (autonomous runtime) / WORKING code + DORMANT local runtime (session-aggregation axis) / MISSING (canonical ingestion)** — four-way split extending S1402 §13 WORKING/PARTIAL pattern. **Cross-arc integration seam** — Category C → Category D (Meeting + Close) NEXT: S1404 inherits Category C's session-aggregation axis + read-only-EngagementEngine surface; also inherits the F.B1 → F.C1 sequential-ADR pair-design recommendation per Rigby cycle 1 Q4 (F.B1 delivery first, F.C1 ingestion stacked). **Parent-Claude verifier-loop discipline further extended:** S1403 executed 11 direct-read + Rigby-joint checkpoints (up from S1402's 9). Third joint-verifier-loop CONFIRMATION cycle: F.C1/F.C3 empirical row-count via parent-Claude Django ORM `.count()` when Rigby's `db_health_tool` returned indeterminate `row_count=-1` — extends the S1402 D.B7 pattern to include "when Rigby's tool surface returns non-definitive, parent-Claude runs direct-verification via alternate path." Memory rules triggered during audit: `feedback_audit_findings_12_canonical_celery_deferred_list.md` (F.C6 classification); `feedback_openai_client_factory.md` (Agent 2 verification path); `feedback_verify_before_deleting_dead_code.md` (Agent 6 T.C4 overreach caught). Isolation pin `pa-fba0c4c81fba4922` retires post-PR-merge per playbook §15.) — prior v21 (2026-07-01) — **Group 1400 Revenue arc Child B (Outreach Composition + Delivery) audit S1402 shipped.** §1.24 `domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` added (S1402 Child B audit — Outreach Composition + Delivery; 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category B evidence surfaces + parent-Claude verifier-loop pre-SIGN corrections on 2 sub-agent claims + Rigby SIGN cycles 1+2 on fresh isolation pin `pa-4a0a28edcb7a45ec` → SIGN-clean cycle 2 High confidence after 2 must-fix + D.B7 dead-code fold cycle 1 + 5-Q-answer fold cycle 2). §8 timeline S1402 row added. **Load-bearing findings for Category B:** (a) F.B1 delivery path missing — CONFIRMED HIGH (grep-negative at HEAD `beda00e5` across mainline; no provider SDK imports, no `EMAIL_BACKEND`, no send call sites — S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 RESOLVED to "no outbound channel at all," not just "Inbox missing"); (b) F.B3 engagement feedback loop missing — CONFIRMED HIGH (`EngagementEvent.outreach_draft` FK schema exists at `core/models_engagement.py:55-59`, zero writer sites for EngagementEvent — Category C S1403 inherits the whole seam build-out); (c) F.B4 NEW — OutreachSequencer declared 4-touch cadence has no runtime realization (only Touch 1 fires; Touches 2–4 depend on `OutreachSequencer.evaluate` which is CONFIRMED DEAD CODE via Rigby ops probe + parent-Claude direct read: zero PeriodicTask wrapper, zero CeleryTaskEvent 30d, zero PA tool action wraps `.evaluate`, zero grep hits); (d) F.B2 CONFIRMED writer-site F2 orphan-write pattern at `revenue.py:812-829` (omits `opportunity=parent.opportunity` on create; writes literal `body_text = "Draft follow-up message needed."`) — CANDIDATE at repo-wide scope — **runtime blast radius zero due to F.B4 dead code**; (e) S1273 §10.3 UNKNOWN #1 (single-shot vs reviewer chain) RESOLVED — single-shot LLM only, no Content Deliberation, no reviewer chain; verified `outreach_generation.py:340-370`; uses `get_openai_client()` factory per memory rule; (f) F1 provenance-filter drift CANDIDATE extends to Category B reader surface (`OpportunityDraftGenerator.select_candidate_queryset` filters on match_score/potential_revenue/created_at only; no source/spider_source filter); (g) F3 Redis-only durability CLEAN for Category B (all state DB-persistent); (h) S1401 §14 D6 dual-representation drift ruled OUT for Category B (reads persistent `Opportunity.objects.filter(...)` only, no `intelligence_engine.get_current_opportunities()` consumption); (i) D.B1 docstring vs runtime drift on OutreachDraft lifecycle (model docstring declares 5 states, runtime implements 3) — MEDIUM per Rigby SIGN cycle 2 Q3 (elevates to HIGH only if UI/ops relies on 5-state for compliance); (j) T.B8 no dedicated outreach queue — documented pre-Employee-OS per Rigby SIGN cycle 2 Q6; (k) D.B3 anchor-update at S1274 §2.4 line 293 recommended IMMEDIATELY per Rigby SIGN cycle 2 Q7 (truth correction, not synthesis-deferral); (l) R.B7 send-gap fence test bundled with R.B1 per Rigby SIGN cycle 2 Q9. **Cross-arc integration seam** — Category B → Category C (Engagement Inbound) NEXT: S1403 inherits F.B3 as its scope + the FK schema (`EngagementEvent.outreach_draft`); Rigby SIGN cycle 2 Q4 confirmed F.B4 interpretation (only Touch 1 fires in production; Touches 2–4 dead code) — this closes the follow-up-cadence UNKNOWN before Category C launch. **Parent-Claude verifier-loop discipline extended:** S1402 promoted 2 sub-agent findings pre-SIGN (F.B2 orphan-write elevated to CONFIRMED writer-site + literal stub via direct read of `revenue.py:812-829`; F.B1 delivery-gap reframed as "docstring-vs-runtime divergence" from Agent 4's "channel missing" via docstring direct read). Extends S1401's 5-pre-SIGN corrections methodology. Isolation pin `pa-4a0a28edcb7a45ec` retires post-PR-merge.) — prior v20 (2026-07-01) — **Group 1400 Revenue arc opened + first child audit S1401 shipped.** Two library entries land in one commit: §1.22 `domains/revenue/1400_revenue_domain_scoping.md` (S1400 parent scoping — Phase 0 doc + first application of Chris's F.i/F.ii/F.iii methodology proposed as playbook v3 §11.1 template addition; Rigby Light SIGN cycles 1+2 both SIGN-clean; 9 Chris-locked decisions D21+D23-D29 across 3 "agree all" rounds; 6-child arc shape locked A→B→C→D→E→F→xx99 at S1401-S1406 + S1499) and §1.23 `domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (S1401 Child A audit — Opportunity Discovery + Scoring; 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 evidence surfaces + parent-Claude verifier-loop pre-SIGN corrections on 5 sub-agent claims + Rigby SIGN cycles 1+2 on fresh isolation pin `pa-16d8b24d30e7a7d8` → SIGN-clean cycle 2 High confidence after 4-fold cycle 1 fold — 2 must-fix + 2 nice-to-have). §8 timeline S1400 + S1401 rows added. §5 gap entries: S1273 §10.3 UNKNOWN #1 (Opportunity model location) RESOLVED at `core/models_unified_system.py:1201`; §12.1 Category A F.iii questions all 6 answered (§20.7 audit checklist). §3 domain map: Revenue whole-domain maturity remains WORKING (Category A specifically WORKING baseline preserved; no upgrade or downgrade). Load-bearing findings for the arc: (a) sports lane resolved as SEPARATE LANE (writes `OpportunityTracking`, not mainline `Opportunity`) — S1274 §2.4 line 270 MISSING remains accurate for mainline with wording refinement "separate lane" rather than "missing implementation"; (b) NEW dual opportunity representation drift — 5 consumer sites in `consumers_base.py` stream from `intelligence_engine.get_current_opportunities()` in-memory realtime source, not persistent Django `Opportunity` — Rigby SIGN cycle 1 grep found the pattern broader than initially captured (lines 1696, 1730, 2541, 2557, 2597); (c) F1 provenance-filter drift + F3 Redis-only durability CANDIDATE both HIGH severity per S1399 methodology inheritance; (d) F2 orphan-write cluster CANDIDATE on 10-variant Opportunity family + Session Pre-38 partnership_* fields; (e) OpportunityPipelineOrchestrator vs OpportunityExecutionPipeline complementary-not-overlapping (parent-Claude verifier-loop overrode Agent 6's duplication flag via Agent 2 direct read); (f) NEW debt T5 — `score_opportunities_from_spider_data` defined TWICE in `settings.py` `task_routes` (:1277 long_running + :1484 content); later wins; (g) ownership gap CONFIRMED (S1274 §14 #36 inherited; deferred to Child E aggregate per D28). §19 follow-on queue 8 items ranked; R1 umbrella "dual-representation + provenance contract" with prerequisite R1.0 (`intelligence_engine.get_current_opportunities()` origin/lifecycle audit). Rigby cycle 2 verdict verbatim: "SIGN-clean (cycle 2 unnecessary; ship to Chris commit-gate). No remaining blockers based on your fold summary." Isolation pin `pa-16d8b24d30e7a7d8` retired at S1401 close.) — prior v19 (2026-07-01) — S1399 §10 "What This Research Taught Us About How to Do Research" retrofit landed post-close per Chris directive. Playbook §11.3 canonical-summary template updated same-commit from 11 sections to 12 sections; §10 becomes non-negotiable for every future xx99 canonical summary. S1399 renumbered: former §10 Arc Change Log → §11; former §11 Appendix — Provenance → §12. Load-bearing methodology content previously at §10.4 moved into new §10.2 "What to codify into playbook v3" with two-triggers threshold status table (3 patterns MET: F1/F4-CANDIDATE discipline, sibling-inheritance hypothesis-correction, playbook v3 additions eligible; 2 patterns Chris-ratified no-threshold: docs cascade + meta-methodology §10). §11.4 preserved as backwards-compat pointer for external references to old §10.4. §12.6 arc close criteria checklist extended from 12 to 13 boxes (added "docs → RAG cascade executed post-merge"); all 13 ticked. Memory rules `feedback_xx99_meta_methodology_section.md` + `feedback_docs_cascade_at_every_close.md` saved. External references updated: OPEN_ARCS 2026-07-01 S1399 close reconciliation note + SESSION_1399 handoff `key_findings` LOAD-BEARING METHODOLOGY row + arc close criteria checklist. §1.21 body updated with post-close retrofit callout.) — prior v18 (2026-07-01 same day) — S1399 registered `domains/memory/1399_memory_canonical_summary.md` as §1.21. **Arc-closing xx99 canonical summary for Research Group 1300 Memory / Knowledge / Embeddings.** Consumes S1301-S1305 child outputs per playbook §11.3 bounded-work rule; no §13 6-parallel-Explore sweep launched; every claim cites source-audit §-anchor via SNNNN §NN.N notation. Rigby SIGN cycle 1 on fresh isolation pin `pa-4fc3329d0db6484f` → verdict **SIGN-clean** at High confidence, 0 must-fix, 1 optional nice-to-have (docs↔code naming/category drift micro-pattern kept as §4.5 adjacent evidence rather than promoted to formal F5 — preserves the 4-pattern set named at S1305 close per parent §5 P6 rationale). **Four cross-cutting patterns named (§4):** F1 provenance-filter drift class (S1301 §14.2 + S1304 §14 D2/D6 + S1305 §14 D1); F2 row-level orphan-write pattern (S1301 §14.3 D3 hypothesis + S1302 §14.3 F2 narrowed 11→7 fields + S1304 §14 D3 partial invalidation); F3 Redis-only durability + `@lru_cache` staleness pattern (S1302 §14 F4 + §15 T3/T4 + S1304 §14 D2 + S1305 §14 D3/D4/D5/D8); F4 F1/F4-CANDIDATE + severity-correction discipline as inheritance methodology (S1303 §14 F4-CANDIDATE + S1304 §14 D7 + S1305 §14 D6 + S1305 §14 D3 severity extension). **Five contradictions resolved (§5):** S1304 §14 D3 partial-invalidates S1301 §19 D3 broad source_type orphan claim; S1304 §17 complementary reframe of S1302 §17.3 duplicate provenance systems; Agent 6 CRITICAL → MEDIUM severity downgrade via Redis AOF sibling context (settings.py:944); Agent 6 "13 cache.set(timeout=None)" → 5 production scope-tightened; parent §3H "search_docs LRU" → precision fix on `_load_provenance_docs`. **Consolidated domain shape (§3):** Cat A/B/C/D/E/F/G/H matrix; Redis 4-DB topology table; two provenance systems complementary-not-duplicate (S1304 §17 reframe canonicalized); two RAG lanes with no runtime selector; 4 @lru_cache(1) sites enumerated with invalidation contracts; load-bearing consequence table (8 rows). **Anchor-update recommendations (§7):** `platform_architecture_inventory.md` §3.13 subdivision into Cat A/B/C sub-rows; §3.14 lane consolidation as explicit two-lane statement; new §3.N row for Cat F Conversational/Thread Memory (first-inventory landing per S1303); new §3.N or §5.N row for Cat H Runtime Memory Correctness (first-inventory landing per S1305); `docs/topics/infrastructure.md` Redis DB count 3 → 4 fix; `KNOWLEDGE_RAG_MEMORY.md` 4 targeted edits (F1 pa_content_feedback dead-code note, two-lane split explicit reference, LRU precision fix on `_load_provenance_docs`, pointer to S1399); NEW `docs/topics/docs-ingestion-cascade.md` per S1304 §19 R6. NO direct edits to `PLATFORM_INVENTORY.md` (per CLAUDE.md context-kit rule — runtime anchor, regenerable via `generate_platform_inventory`). **Follow-on queue (§8):** 21 items ranked by uncertainty × risk × unblocked flows. Top 5: (1) S1304 §19 R1 `ingested_via` full-tree recheck (F1-CANDIDATE hardening); (2) S1303 §19 R1.a/b/c ChatConversation `context_used` + `agent_results` verification (F4-CANDIDATE); (3) S1305 §19 R1 `platform_config` LRU F4-CANDIDATE mutation-path audit; (4) S1305 §19 R6 `IntelligentJobMatcher` production invocation audit (routes T5 MemorySystem severity assessment); (5) S1302 §15 T10 write-authority framework design-preparation ADR (highest-severity debt in arc). **Delegated arcs (§9):** Employee OS 1200s arc owns Cat G Mission Memory (parent §3G Chris-locked D2 2026-07-01); Group 1700 Observability owns 4 aggregated items (Cat D filter-drop telemetry from S1301 R2, Cat E↔D filter-drop from S1304 R7, dead-code / producer-only detection from S1302, EventBus adoption for Cat F from S1303 R2, worker-recycle instrumentation for Cat H from S1305 R5); post-S1399 design-preparation phase owns 4 ADR/design-preparation docs (Cat H remediation per surface, Cat H ↔ Cat B integration lens, provenance-system reconciliation, turn-context → RAG enrichment). **Load-bearing methodology output:** F4 F1/F4-CANDIDATE + severity-correction discipline codified as inheritance methodology — extends to playbook v3 candidate additions per §20 two-triggers rule (now used across S1303 + S1304 + S1305). **Group 1300 arc closed** per playbook §17 graduation criteria — all 5 child audits + canonical summary shipped, SIGN-clean, committed to `main` (S1399 pending Chris commit-gate). Arc pin `pa-aa54193f240f4846` retires on Chris merge. Group 1400 Revenue next per playbook §22 queue, pending Chris directive. §8 timeline S1399 row added. First formal `authority: research` + `category: canonical_summary` doc in the library — S1268-S1275 arc predated the xx99 convention.) — prior v17 (2026-07-01) — S1305 registered `domains/memory/1305_memory_runtime_correctness_audit.md` as §1.20. **Fifth (and final) child audit under Group 1300 Memory (parent §1.13).** Category H Runtime Memory Correctness NARROW scope per parent §5 P5 slot — Redis-loss on worker recycle + `@lru_cache(1)` staleness drift class only; explicitly OUT of scope: system RAM, macOS SIGSEGV, ops-flavored infrastructure. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep + parent-agent verifier-loop pre-SIGN corrections (Agent 6 CRITICAL → MEDIUM per Redis AOF context; Agent 6 "13 timeout=None" → 5 production; Agent 6 "3 disjoint DBs" → 4; Agent 1/Agent 2 conflict on search_docs cache location resolved) + Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-56a527a2c5528508` → verdict **SIGN-clean** after 3-must-fix fold + verification pass. Pin retired at close (`updated_count: 2, retired: true`). **Load-bearing findings:** exactly 4 `@lru_cache(maxsize=1)` sites in `core/services/` grep-verified (only `platform_config` pair has explicit `clear_config_cache()` invalidation contract; other two rely on worker-restart); 5 production `cache.set(timeout=None)` sites (`core/tasks.py:5936`, `core/memory_system.py:54, :55, :176`, `core/services/discord_bot.py:9723,9728`) with 6 excluded categories enumerated at §3 excluded-from-count table; `AgentLearningService` within-process consistency gap CONFIRMED (`get_user_memory:415` short-circuits to `_user_memories[key]` before Redis; `save_memory:476` writes Redis but never clears dict; grep for invalidation = 0 hits) — distinct from S1302 T3 cross-process recycle-loss; `MemorySystem` at `core/memory_system.py:54-55, :176` writes `timeout=None` creating index → data divergence risk under `REDIS_MAXMEMORY_POLICY='allkeys-lru'` eviction; Rigby SIGN cycle 1 grep confirmed `MemorySystem` IS active via `ai_core/agents/intelligent_job_matcher.py:57`; 4-DB Redis topology (DB 1 Django cache, DB 2 Celery broker, DB 3 Celery results, DB 5 `AgentLearningService` hardcoded at `agent_learning_service.py:145`); Django `cache.clear()` operates on DB 1 only — `AgentLearningService` uses raw `redis.Redis()` at `:160` bypassing framework; `docs/topics/infrastructure.md` says "3 DBs" — doc drift. **Closes parent §3H open questions:** search_docs has NO dedicated LRU (only `_load_provenance_docs`); MemoryPromotionService has NO runtime cache (pure DB I/O); MemorySystem IS active. **§19 downstream routing:** R1 platform_config LRU F4-CANDIDATE verification (highest priority follow-on); R2 Cat H remediation design-preparation per surface per S1304 T2 option set → post-S1399; R4 Cat H ↔ Cat B integration lens (AgentLearningService Redis-only durability + TTL policy + DB writeback design decision — fixes T3 + T4 + T7 together); R5 worker-recycle instrumentation → Group 1700 Observability; R6 IntelligentJobMatcher production invocation audit; R7 full `@lru_cache` sweep across `core/`, `ai_core/`, `content/`; R8 doc-drift fix on Redis DB count. **First library audit to explicitly downgrade a sub-agent severity claim via sibling-inherited context** — extends verifier-loop pattern from hypothesis-correction (S1304 partial invalidation of S1301 §19 D3) to severity-correction (S1305 §14 D3). **Group 1300 arc now closable via S1399 canonical summary** — 5-child arc complete. Third child to reach SIGN-clean in 2 cycles (matching S1303 + S1304). §8 timeline S1305 row added.) — prior v16 (2026-07-01) — S1304 registered `domains/memory/1304_memory_docs_rag_boundary_audit.md` as §1.19. **Fourth child audit under Group 1300 Memory (parent §1.13).** Categories E ↔ D Documentation Corpus ↔ RAG Boundary — deliberately smaller boundary-lens scope per parent §5 P4 rationale ("smaller scope; benefits from §3.14 audit landing first"). 20-section playbook §11.2 template + §13 6-parallel-Explore sweep + parent-agent verifier-loop spot-checks + Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-2614a91a920642fa` → verdict **SIGN-clean** after 4-must-fix fold + verification pass. **Load-bearing finding: partial invalidation of S1301 §19 D3 hypothesis via S1304 verifier-loop before propagation to sibling audits.** S1301 §19 D3 broadly claimed both `DocumentEmbedding.source_type` + `ingested_via` are orphan-writes. Direct file:line read at `content/embeddings.py:965-973` confirms `source_type` HAS an owner-model-qualified consumer (`semantic_search_sync` applies `.filter(source_type__in=[...])` in `internal_only` / `external_only` `source_filter` branches at :971/:973) + presentation at :1007. Only `ingested_via` remains F1-CANDIDATE orphan (all 3 write-sites use fixed string constants `sync_docs` / `backfill` / `unknown`; zero owner-model-qualified read consumers per grep + serializer + admin verification). F1-CANDIDATE status pending §19 R1 full-tree recheck per S1303 §14 F4-CANDIDATE discipline. **Other load-bearing findings:** (D6 HIGH) `build_docs_provenance` beat schedule unscheduled — verified via `core/celery.py:495-499` sole `refresh-docs-corpus-daily` entry + `core/tasks.py:5900-5902` cascade call sites showing NO `build_docs_provenance` call; provenance rebuild is manual-only; combined with D2 lru_cache(1) staleness gap at `td_handlers_ops.py:78-93` this is the canonical E→D write-side/read-side sync drift. (§18) Documentation Manager `AIEmployee` handle at `core/employees/jobs.py:187-395` (registered `:1336` as `docs_manager`, employee_handle=`rigby`, `mission_run_kind=docs_cascade`) explicitly owns cascade steps 1-4; four specific boundary-maintenance responsibilities (provenance rebuild cadence, cache invalidation strategy, filter observability, row-level `ingested_via` consumer strategy) have "no explicit named runtime owner" per bounded-language refinement (SIGN cycle 1 fold #2 softened "CRITICAL" → "HIGH"). (§17) Two provenance systems reframed as **complementary, not duplicate** via S1302 §17.3 name-collision methodology — external `_provenance.json` encodes session origin (LOCAL keyword lane); row-level `source_type` encodes source-of-record enum (PROD pgvector lane); `ingested_via` was over-designed for a retrieval consumer that never materialized. Fold #4 adds "complementary today does not imply optimal" guardrail with unification-vs-explicit-scoping paths routed to §19 R2. (§19 R5) Turn-context → RAG enrichment (inherited from S1303 §19 R3) routed to design-preparation phase — three signals tilt intentional-separation vs three signals tilt drift; NOT resolvable from static evidence; requires product/architecture decision on operational cost, migration risk, future retrieval requirements. **Maturity verdict:** PARTIAL across all 4 boundary components (ingestion cascade PARTIAL — cascade operates but step 4 async fan-out not gated by beat + idempotency not verified; provenance filter WORKING — mechanism sound but 21.5% UNKNOWN input coverage + observability response-only + cache staleness gap; row-level provenance write path EXPERIMENTAL — `source_type` wired, `ingested_via` F1-CANDIDATE pending R1; E↔D boundary as a whole PARTIAL — functional but not mature). **§19 downstream routing:** R1 full-tree `ingested_via` F1-CANDIDATE verification (HIGHEST priority follow-on); R2 provenance-system reconciliation design → S1399 canonical summary; R3 rebuild cadence + cache invalidation design → Cat E governance owner; R4 boundary ownership assignment → S1399 canonical summary; R5 turn-context → RAG enrichment design decision → design-preparation phase (post-S1399); R6 ingestion-cascade published documentation → Cat E docs-governance owner; R7 filter-drop telemetry → Group 1700 Observability; R8 S1301 follow-up classifier precedence bug (standalone bugfix, LOW priority). §8 timeline S1304 row added.) — prior v15 (2026-07-01) — S1303 registered `domains/memory/1303_memory_conversational_thread_memory_audit.md` as §1.18. **Third child audit under Group 1300 Memory (parent §1.13).** Category F Conversational / Thread Memory — **first-inventory landing**: Cat F had no `platform_architecture_inventory.md` §3.N row today; this audit produces the terrain (§4 Major Models + §7 Runtime Flows load-bearing). 20-section playbook §11.2 template + §13 6-parallel-Explore sweep + parent-agent verifier-loop spot-checks + Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-23a38300dd84bae2` → verdict **SIGN-clean** after 12-edit fold + 1-cycle verification pass. **Load-bearing findings:** F1 (S1212 deliverable 777d9cd8 stale-thread dispatcher waste, ~$3.60/day) CONFIRMED RECONCILED — S1248 shipped matched-pair fix: retire handler at `td_handlers_core.py:4011-4072` sets `session_active=False`, dispatcher gate at `conversation_action_dispatcher.py:288-316` blocks (fail-open under DB errors — availability > correctness). F2 (`session_tool.retire` action existence) CONFIRMED PRESENT — memory rule `feedback_session_tool_retire_works.md` stands. F3 (`content_writer_agent.py:76` `from core.models_unified_system import ConversationMemory`) verified: SOFT FAIL at import time via try/except guard (lines 74-80) — Rigby SIGN cycle 1 surfaced deeper issue that guarded branch at line 370 filters `ConversationMemory.objects.filter(user=user, memory_type__in=['success','insight','learning'])` but Django `ConversationMemory` at `models/conversations/models.py:19-31` has NO `memory_type` field (that field lives on `UserMemoryContext` at `:253`); D1 debt widened to "wrong model + wrong field" — fix requires canonical model + ORM field realignment (import fix alone shifts crash from import-time to query-time FieldError). F4 (`ChatConversation.context_used` + `.agent_results` phantom-field candidates) DOWNGRADED FROM "CONFIRMED DEAD CODE" TO "CANDIDATE — NOT YET PROVEN EITHER WAY" per memory rule `feedback_verify_before_deleting_dead_code.md` — Rigby SIGN cycle 1 confirmed Agent-6's keyword-grep catches unrelated variables (`tasks_agents.py:1262` `agent_results = phase_data.get('results', {})` is local dict in different scope). F7 (no Cat F event stream on EventBus, 0 `CONVERSATION_*` streams in `event_bus.py:21-31`) reframed as gap/partial, delegated to Group 1700 Observability. F8 pin rotation policy lives only in `tools/pa_local.sh` header comments (policy-in-tooling). F9 no auto-cleanup for retired rows. F10 Discord unlinked-user linkage-completion signal MISSING. Cat F ↔ Cat D reframed as OBSERVED GAP + owner-confirmation-required (not defect — could be intentional separation). **Maturity verdict (post-SIGN cycle 1 bounded):** WORKING (bounded) — interactive web PA sessions with DB-backed turn reinjection are stable; PARTIAL — lifecycle hygiene (cleanup / events), analytics completeness, and hard policy enforcement (retired-thread gating is best-effort / fail-open under exceptions). **§19 downstream routing:** R1 (F4 candidate verification) split into R1.a owner-model-qualified consumer inventory (do first) / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth resolution (first-class fields vs metadata); R2 EventBus adoption design → Group 1700; R3 turn-context → RAG enrichment design → S1304 (Cat E ↔ D boundary); R4 retention lifecycle for retired rows; R5 land first-inventory §3.N row via S1399 canonical summary; R6 formalize session identity mint contract (`create_fresh` `pa-<hex[:16]>` vs `get_or_create_session` `uuid4()` duplicate mechanism at §17); R7 doc-in-tooling reconciliation (F8); R8 fix D1 broken import + field mismatch. New §20.9 subsection "Reinjection Metadata Contract" documents 4 expected metadata keys (`source`, `tool_calls`, `tool_results`, `response_id`) with producer/consumer citations to prevent F4-style false dead-code claims by distinguishing model fields from metadata dict keys. New §20.10 subsection is the explicit `status: draft` → `status: active` gating checklist (11 of 12 items ticked at close; Chris commit-gate = last item). §8 timeline S1303 row added.) — prior v14 (2026-07-01) — S1302 registered `domains/memory/1302_memory_persistence_architecture_audit.md` as §1.17. **Second child audit under Group 1300 Memory (parent §1.13).** Categories A + B + C combined scope (Semantic Knowledge / Personal-Adaptive / Agent Working Memory) per parent §5 P2 slot. Playbook §11.2 20-section template + §13 6-parallel-Explore sweep + parent-agent verifier-loop spot-checks + Rigby SIGN cycles 1 + 2 + 3 on fresh isolation pin `pa-1b9f0f5264484c6b` → verdict **SIGN-clean** after three fold cycles. Headline finding **F1**: S1301 parent §3 "spider_context['pa_content_feedback'] consumer UNKNOWN" ESCALATED to CONFIRMED DEAD CODE via whole-tree grep (1 producer at `core/agent_router.py:766`; 0 code consumers across `core/` + `ai_core/`). Row-level orphan-write pattern inherited from S1301 §14.3 D3 narrowed across 3 SIGN cycles: v1 draft claimed ~11 fields; final classification is 5 strict-orphan fields + 2 narrow-consumer-safety-filter fields (7 total under F2 pattern) after Rigby grep-verification removed AgentKnowledgeSource.source_spider_names + first_discovered_at + feedback_adjusted_confidence (cycle 1) and AgentMemory.source_type + source_id + access_count + last_accessed_at (cycle 2, consumed by Memory Palace at `core/views_memory_palace.py:60, :86, :113-114`), and reclassified AgentMemory.poison_risk_score + poison_risk_factors as narrow-consumer-surface via `core/services/memory_embedding_service.py:222, :261` safety filter (cycle 3). Other load-bearing findings: (a) MemoryPromotionService scoring criteria are deterministic regex patterns at `core/services/memory_promotion_service.py:119-172` (+3 milestone, +2/type max +6 identifier, +2 wiring, -10 secret) with hardcoded thresholds ≥7 auto-save / 5-6 pending / ≤4 ignore at :234, :237; writes into `UserMemoryContext` at :303-318, NOT `AgentMemory` — F6 category-assignment drift documented. (b) `spider_data_bridge` (Cat A per naming) writes `UserAgentLearning` (Cat B) at `core/learning_bridges/spider_data_bridge.py:240` via `UserAgentLearning.objects.get_or_create` — F5 docs_stale drift. (c) 14-day freshness window at `core/conversation_orchestrator.py:749` verbatim `freshness_cutoff = tz.now() - timedelta(days=14)` — Session 988 origin per :747-748 comment; hardcoded magic number. (d) `AgentLearningService` Redis-only durability confirmed at `core/services/agent_learning_service.py:462-483` — `save_memory` writes `redis_client.hset` at :476 with no DB backup; 0 hits for `.expire()` / `.setex()`. (e) T10 highest-severity debt: no write authority gate on `AgentMemory.create_memory` at `core/models_unified_system.py:11004`; `MemoryPromotionService` auto-saves on every PA turn without rate limiting. (f) Two name collisions documented (§17.2 two `AgentMemory` classes: Django model at `models_unified_system.py:10787` vs in-process at `agent_learning_service.py:111`; §17.3 two `ConversationMemory` classes: Django model at `core/models/conversations/models.py:19` vs in-process at `core/conversation_memory.py:59`). Per-category maturity: Cat A = PARTIAL, Cat B = PARTIAL, Cat C = EXPERIMENTAL (downgraded from WORKING due to F1 dead-code loop). §19 downstream routing: S1303 owns Conversational/Thread Memory Cat F (`ConversationSession` ↔ `ConversationMemory` boundary); S1304 owns Docs Corpus ↔ RAG Boundary (E ↔ D); Group 1700 owns dead-code / producer-only detection surface; S1399 canonical summary owns row-level orphan-write pattern classification + write-authority framework anchor recommendation. §8 timeline S1302 row added.) — prior v13 (2026-07-01) — S1301 registered `domains/memory/1301_memory_rag_retrieval_lanes_audit.md` as §1.16. **First child audit under Group 1300 Memory (parent §1.13).** Category D RAG Retrieval Lanes exclusive scope; playbook §11.2 20-section template + §13 6-parallel-Explore sweep + parent-agent verifier-loop spot-checks + Rigby SIGN cycle 1 on fresh isolation pin `pa-a23736a833f646cf` → verdict **SIGN-clean** after 4-must-fix fold. Traces parent §6 provenance-filter finding (8 pre-filter → 7 excluded_missing_provenance + 1 excluded_mismatch → 0) to root cause: HYP-1 migration-incomplete × HYP-4 never-wired-into-ingestion. Load-bearing findings resolved: (a) `search_docs` runs LOCAL keyword lane (`core.rag.top_k` on `.rag/corpus.jsonl`) — NOT prod pgvector; `kb_tool semantic_search` runs PROD pgvector lane (`core.rag_integration.search_embeddings`); verified `td_handlers_ops.py:5502`. (b) Provenance is external to chunks (git-history-derived `docs/_provenance.json`); 464 UNKNOWN / 2156 docs = 21.5% coverage gap; filter treats "path not in index" as `excluded_missing_provenance` by design per Rigby S1145 P2 spec. (c) Two provenance systems coexist without integration — row-level `DocumentEmbedding.source_type` / `ingested_via` fields (migration 0044) are populated at ingestion but never read by any retrieval path (grep receipts). (d) Prod pgvector lane bypasses the provenance filter entirely. (e) Two-lane runtime selector NEVER IMPLEMENTED. (f) PA turn enrichment does NOT auto-invoke RAG — tool-call-only. (g) Silent-failure surface confirmed system-wide-in-`core/` — no log/metric/alert on filter drops. (h) Combined maturity verdict WORKING (dropped from STABLE) due to corpus-completeness gap. §19 downstream routing: S1302 owns row-level provenance semantics (persistence-architecture); S1304 owns E↔D handoff; Group 1700 owns filter-drop telemetry. §8 timeline S1301 row added.) — prior v12 (2026-07-02) — S1279 installation. Research OS transitions from READY-WITH-MINOR-FOLLOW-UP to **CANONICAL**. Three P0 items landed in one atomic commit: (1) `CLAUDE.md` extended with a "Research Library" subsection + universal Startup checklist — pointer-only into the OS, no restatement; (2) `docs/research/OPEN_ARCS.md` created as machine-readable cross-arc manifest (source-of-truth for arc state per OS §6.6 reconciliation); (3) `docs/00-START-HERE/README.md` + `INDEX.md` extended with Research Library entry-point rows so fresh Claude naturally discovers the OS from either entry point. OS §1.14 `status:` flipped `draft` → `active`. `CURRENT_RESEARCH.md` evaluated and explicitly rejected (OPEN_ARCS with `state: in-progress` filter serves the same purpose without a duplicate maintenance surface). No architectural changes; OS §1-§19 structurally unchanged; §20.15 installation record added. §8 timeline S1279 row added. §1.14 row body updated to reflect CANONICAL status. Group 1400 Revenue may now open under the fully-installed OS.) — prior v11 (2026-07-02) — S1277 + S1278 registered `RESEARCH_OPERATING_SYSTEM.md` (v2.1) as §1.14 and `claude_research_startup_introspection.md` as §1.15. **First `authority: process` doc that governs Claude Code's entire workflow across every request class.** S1277 produced OS v1 → v1.1 → v2 across three cycles; six new parts added in v2 for expanded mission scope (Research Philosophy, Context-Kit Integration, Documentation Ownership, Research Contract, Completion Contract, Research Debt). Two Rigby SIGN cycles (fresh isolation pins pa-95ce3cbf0a2aa0cc + pa-117d3edf9d7b80f8): 15 must-fixes folded from v1 → v1.1 SIGN; 12 must-fixes folded from v2 SIGN. S1278 ratification pass: 13 playbook §-ref cascade artifact bugs corrected; §20 finalization section added (assessment, ecosystem diagram, graduation verdict, P0/P1/P2 debt sort); third Rigby SIGN cycle on fresh pin pa-30278fb65295e74c returned High-confidence SIGN-with-edits (edits = the three P0 doc-pointer follow-up items already flagged, not architectural). Ratification verdict: **READY WITH MINOR FOLLOW-UP** — architecture complete, graduated; 3 blocking items (CLAUDE.md pointer, `OPEN_ARCS.md` creation, START-HERE pointers) all documentation-only, deferred to follow-up migration session. Once P0.1-P0.3 land, OS becomes CANONICAL. §8 timeline S1276+S1277+S1278 rows added. Introspection registered as companion evidence base for OS (§1.15). §1.11 playbook body updated to cross-reference §1.14 OS. No §3 domain map / §5 gap changes; §9 roadmap notes OS canonical arc complete. Discoverability priority: OS is now the FIRST doc a fresh Claude Code should read after `CLAUDE.md` for ANY class of work (research, implementation, bug, ops); the playbook remains first-read specifically for research-class arcs.) — prior v10 (2026-07-01) — S1276 extended `DOMAIN_RESEARCH_PLAYBOOK.md` §1.11 in-place from v1 → v2. Playbook restructured into 7 parts / 24 sections; formalized fifteen areas that emerged after v1 shipped: research group lifecycle (parent → children → canonical summary → index → complete), phase discipline (research / design-preparation / design-decision / process / navigation / implementation authority values), xx99 canonical summary convention, canonical folder structure (`docs/research/domains/<slug>/`), self-describing metadata standard (adds `research_group` / `child_slot` / `dependencies_on` / `delegates_to` / `delegated_from` frontmatter fields), cross-reference policy (never duplicate — always reference), parent doc responsibilities (§8 codifies S1300 exemplar), canonical summary responsibilities (§10 pins the xx99 template), stage-scoped Rigby routing (§15 stage table), graduation criteria (§17 objective checklist per group state), dependency mapping (§18 formalizes cross-arc delegation semantics), generalization requirements (§19 pre-audit check + anti-domain-specific-language rules), evolution policy (§20 codifies additive-first + backwards-compat + reality-wins for the playbook itself). No new research findings; no §3 domain map / §5 gap / §9 roadmap changes — this is a process extension, not a research finding. Chris directed at S1276 open: playbook should evolve into the permanent foundation for all future Donkey Betz architecture research. §8 timeline S1276 row added. §1.11 body updated to cite v2 additions. Discoverability priority reinforced: playbook is the FIRST doc a fresh Claude Code should read after `CLAUDE.md` when starting a domain research group. Two-triggers rule (§20) now protects against premature codification of half-emerged patterns.) — prior v9 (2026-07-01) — S1300 registered `domains/memory/1300_memory_domain_scoping.md` as §1.13. **First parent-scoping doc in the library** — opens Research Group 1300 (Memory / Knowledge / Embeddings, playbook §12 queue slot). Phase 0 domain-definition exercise per Chris directive at S1300 open: "Pause before selecting a-f. Your clarification uncovered an architectural ambiguity rather than a simple scoping question." Doc enumerates 8 candidate memory subdomains (Categories A-H) grounded in S1273 §3.13 / §3.14 / §3.15 / §5.4 evidence, recommends parent-with-children shape citing playbook §2 rule 3, and locks Chris's 5 decisions 2026-07-01: (D1) parent-with-children over single-audit; (D2) Category G Mission Memory delegated to Employee OS 1200s arc (cross-linked, not folded); (D3) RAG excluded_missing_provenance finding parked as S1301 input under §6; (D4) P2 renamed `Memory Store Overlap Audit` → `Memory Persistence Architecture` (wider frame: durability + authority, not just overlap surfacing); (D5) S1399 canonical summary planned as arc-close deliverable (cross-cutting synthesis + PLATFORM_INVENTORY.md §3 update recommendations + follow-on queue). Group 1300 arc: S1300 parent → S1301 RAG Retrieval Lanes → S1302 Memory Persistence Architecture → S1303 Conversational/Thread Memory → S1304 Docs Corpus ↔ RAG Boundary → S1305 Runtime Memory Correctness → S1399 canonical summary. Session ended EARLY per Chris close directive — Phase 0 scoping only; no P1 audit work in this session. S1301 launch cadence + Rigby SIGN routing deferred to next session. §8 timeline S1300 row added. §9 roadmap notes Group 1300 arc opened. Playbook §11 short-command entry point exercised for the first time — validates the DOMAIN_RESEARCH_PLAYBOOK.md workflow.) — prior v8 (2026-07-01) — S1275 registered `symbol_mapping_event_schema_design.md` as §1.12. Closes §5.2d (Symbol Mapping Event Schema Design gap). Two-surface event stream (`OpsRunEvent` mission-scoped + `ToolCallRecord.parameters` non-mission tool calls) unified via new `authority_action_observed_stream` DB view; 21 payload fields; 4 v0 emitters + 1 v0 first consumer; DECLARED tier explicitly non-authoritative; drift stack with weekly sampled-truthing loop. Rigby SIGN-with-edits — 8 must-fixes + bonus #9 folded (ambient OpsRun → two-surface, drop `event_id`, drop `notes` + downscope `producer_version`, rename `delegator_actor` → `caller_actor`, reframe "5 producers" → "4 emitters + 1 consumer", rename INFERRED → DECLARED, add sampled-truthing loop, DEFINITE ≠ global truth, reserved-keys policy). §8 timeline S1275 row added. §9 roadmap STAGE 4 CLOSED; STAGE 5 has no P0 (Trust Propagation §5.3 and Employee Boundary Escalation §5.4 are both P1 — Chris picks). New §5.2e implementation-slot added (P1, blocked on Chris canonical sign-off of §1.12).) — prior v7 (2026-07-01) — S1274 registered `DOMAIN_RESEARCH_PLAYBOOK.md` as §1.11. Process document (`authority: process`, distinct from `authority: research`) that codifies the S1268-S1274 methodology into reusable short-command aliases for future domain audits. Chris explicit direction at close of playbook drafting: "register it now and commit." Playbook establishes the standard for research groups 1300-1900 (Memory / Revenue / Sports / Content / Observability / HumanAttention / Event Architecture). §8 timeline S1274 playbook row added. Discoverability priority: playbook is now the FIRST doc a fresh Claude Code should read after CLAUDE.md when starting a domain audit.) — prior v6 (2026-07-01) added §1.10 symbol_mapping_option_selection_design (concurrent S1274 mission). Prior v5 (2026-06-30) added §1.9 platform_architecture_inventory (Employee-OS arc + whole-platform inventory). Prior v4 added §1.8 Authority Enforcement Design Space
companion_anchors:
  - docs/PLATFORM_INVENTORY.md       # runtime anchor (counts source)
  - docs/PLATFORM_WHAT_IT_IS.md      # narrative anchor (glossary)
  - docs/EMPLOYEE_OS_PRIMITIVES.md   # canonical primitives + anti-duplication
  - docs/00-START-HERE/DOC_LIFECYCLE.md  # governs the corpus itself
  - docs/KNOWLEDGE_PIPELINE.md       # runtime flow map
  - docs/AUDIT_FINDINGS.md           # canonical Celery deferred list
  - docs/EVENT_SYSTEM_INVENTORY.md   # observability layers (§1.9 dep)
verifier_loop: |
  v5 update (2026-06-30, S1273 Part 2): re-inventoried docs/research/
  after S1273 landing. `ls docs/research/` now shows 8 .md files
  (7 research + this index). `platform_architecture_inventory.md`
  registered as §1.9 per §10.1 maintenance rules. Library scope
  broadens: §1.1-§1.8 remain the Employee-OS-focused arc; §1.9 is
  the whole-platform counterpart (Chris's explicit S1273-close
  direction). §1 preamble rewritten to acknowledge dual-scope
  library. §3 domain map extended for Revenue / Outreach /
  Engagement (Rigby caught this as a missed domain during S1273
  SIGN review; folded into §3.32 of §1.9 + registered here as new
  Revenue Pipeline domain row). §4 dep graph extended with whole-
  platform arc as sibling branch (does NOT depend on §1.1-§1.8 —
  parallel scope). §5: §5.4 Memory Architecture partially covered
  by §1.9 §3.13; new gaps §5.12 (Revenue Pipeline canonical
  architecture doc), §5.13 (Observability Deduplication Audit),
  §5.14 (Sports/DBAO ↔ AI Studio Integration Sketch) added per
  S1273 top-3 recommendations. §7 decision matrix +3 whole-
  platform rows. §8 timeline S1273 row. §9 lateral research list
  expanded to reference the 11-mission whole-platform roadmap in
  §1.9.
  Prior v4 update (S1273 Part 1): S1272 Authority Enforcement
  Design Space registered as §1.8 (Appendix C notes; frontmatter
  bumped to v4 mid-session).
  Prior v3 update (S1271 close): S1270 Symbol Mapping + S1271
  Actor Identity registered as §1.6 + §1.7 (Appendix B notes).
  Prior v2 note (S1269 close): added §1.4 governance research;
  §3/§4/§5/§7/§8/§9 updated per maintenance rules §10.1.
  Prior v1 note (S1268 close): inventoried docs/research/ at
  2026-06-30. Three docs present. Re-read each frontmatter before
  classifying. Self-verifier pass looked for missing docs,
  duplicate classifications, incorrect dependency ordering,
  inconsistent statuses, and discoverability gaps.
owner: claude (drafted S1268; v2 update S1269; v3 update S1271; v4 update S1273 Part 1; v5 update S1273 Part 2; v6 update S1274 Part 1 [concurrent §1.10 symbol_mapping_option_selection_design]; v7 update S1274 Part 2 [§1.11 DOMAIN_RESEARCH_PLAYBOOK v1]; v8 update S1275 [§1.12 symbol_mapping_event_schema_design]; v9 update S1300 [§1.13 domains/memory/1300_memory_domain_scoping — first parent-scoping doc; Group 1300 arc opened]; v10 update S1276 [§1.11 DOMAIN_RESEARCH_PLAYBOOK extended v1 → v2 in-place; process framework formalization]; v11 update S1277+S1278 [§1.14 RESEARCH_OPERATING_SYSTEM v2.1 canonical process framework + §1.15 claude_research_startup_introspection evidence base; three Rigby SIGN cycles; ratification READY WITH MINOR FOLLOW-UP]; v12 update S1279 [OS installation: CLAUDE.md pointer, OPEN_ARCS.md creation, START-HERE additions; OS status → active; OS CANONICAL]; v13 update S1301 [§1.16 domains/memory/1301_memory_rag_retrieval_lanes_audit — first child audit under Group 1300; Rigby SIGN-clean; owner-line drift fix on S1302 close]; v14 update S1302 [§1.17 domains/memory/1302_memory_persistence_architecture_audit — second child audit under Group 1300 covering Categories A+B+C combined; Rigby SIGN-clean after three fold cycles; F1 pa_content_feedback dead-code escalation + F2 orphan-write pattern narrowed across cycles from ~11 → 7 fields]; v15 update S1303 [§1.18 domains/memory/1303_memory_conversational_thread_memory_audit — third child audit under Group 1300, Category F Conversational / Thread Memory first-inventory landing; Rigby SIGN-clean after 12-edit fold + 1-cycle verification; F1 stale-thread waste reconciled via S1248 matched-pair fix; F3 verified soft-fail-at-import + latent-FieldError-at-query for content_writer_agent.py wrong-model+wrong-field; F4 discipline downgrade from "confirmed dead" to "CANDIDATE — not yet proven either way" per memory rule feedback_verify_before_deleting_dead_code; §19 R1 split into R1.a/b/c]; v16 update S1304 [§1.19 domains/memory/1304_memory_docs_rag_boundary_audit — fourth child audit under Group 1300, Categories E ↔ D Documentation Corpus ↔ RAG Boundary integration lens per parent §5 P4; Rigby SIGN-clean after 4-must-fix fold + verification pass; **partial invalidation of S1301 §19 D3 via S1304 verifier-loop** (source_type HAS owner-model-qualified consumer at content/embeddings.py:965-973; only ingested_via remains F1-CANDIDATE); D6 HIGH build_docs_provenance beat-unscheduled; §18 Documentation Manager JobContract at jobs.py:187-395 owns cascade steps 1-4; four boundary-maintenance responsibilities remain no-explicit-owner; §17 two provenance systems reframed complementary-not-duplicate via S1302 §17.3 methodology; §19 R5 turn-context → RAG enrichment inherited from S1303 §19 R3 routed to design-preparation phase]; v17 update S1305 [§1.20 domains/memory/1305_memory_runtime_correctness_audit — fifth (and final) child audit under Group 1300, Category H Runtime Memory Correctness NARROW scope per parent §5 P5 (Redis-loss + lru staleness only, not ops-in-general); Rigby SIGN-clean after 3-must-fix fold + verification pass on fresh pin pa-56a527a2c5528508 (retired at close); **first library audit to explicitly downgrade sub-agent severity via sibling-inherited context** — Agent 6 CRITICAL AgentLearningService durability claim → MEDIUM per Redis AOF at settings.py:944 matching S1302 T3 sibling classification; parent §3H 3 open questions closed (search_docs has no dedicated LRU, MemoryPromotionService no runtime cache, MemorySystem IS active via ai_core/agents/intelligent_job_matcher.py:57); 4 @lru_cache sites + 5 production cache.set(timeout=None) + 4-DB Redis topology + AgentLearningService within-process consistency gap + MemorySystem index→data divergence risk all with file:line cites; Group 1300 arc now closable via S1399 canonical summary next]; v18 update S1399 [§1.21 domains/memory/1399_memory_canonical_summary — **first formal xx99 canonical summary in the library** (S1268-S1275 arc predated the xx99 convention); consumes S1301-S1305 child outputs per playbook §11.3 bounded-work rule; Rigby SIGN-clean cycle 1 on fresh isolation pin pa-4fc3329d0db6484f at High confidence, 0 must-fix; four cross-cutting patterns named (F1 provenance-filter drift class; F2 row-level orphan-write pattern; F3 Redis-only durability + @lru_cache staleness; F4 F1/F4-CANDIDATE + severity-correction discipline as inheritance methodology); five contradictions resolved (§5.1-§5.5); anchor-update recommendations for platform_architecture_inventory.md §3.13 subdivision + §3.14 lane consolidation + new rows for Cat F + Cat H; 21-item ranked follow-on queue; 4 aggregated Group 1700 Observability delegations; Cat G delegated to Employee OS 1200s arc; Group 1300 arc closed per playbook §17 graduation criteria — Group 1400 Revenue next per playbook §22 queue]; v19 update S1399 §10 retrofit [meta-methodology section added to xx99 canonical summary template]; v22 update S1403 [§1.25 domains/revenue/1403_revenue_engagement_inbound_audit — third Group 1400 child audit, Category C Engagement Inbound; Rigby SIGN cycles 1+2 on fresh isolation pin pa-fba0c4c81fba4922 → SIGN-clean cycle 2 High confidence after cycle 1 fold (must-fix #1 CLOSED via parent-Claude Django ORM `.count()` on local — all 4 Category C tables 0 rows; must-fix #2 withdrawn as Rigby cycle-1 narrative artifact; 4 Q-answer folds Q1/Q4/Q5/Q6) + cycle 2 Q7/Q8/Q9 + 2 nice-to-have folds (Env Coverage Table + T.C8 three-checkbox split); load-bearing findings F.C1 zero-writer + F.C2 corrected axis map + F.C3 orphan-write CONFIRMED writer-site + F.C4/F.C5 docstring drifts + F.C6 run_ops_autopilot deferred-by-policy per AUDIT_FINDINGS.md #12; 11 verifier-loop checkpoints; sub-agent T.C4 dead-code overreach REFUTED via direct read + F2 CANDIDATE upgraded to CONFIRMED writer-site via direct read; four-way maturity split WORKING code / DEFERRED-BY-POLICY autonomous runtime / WORKING code + DORMANT local session-agg / MISSING ingestion; Rigby Q1 lean separate ADR outside G1400 for run_ops_autopilot enable-decision; Q4 lean two sequential ADRs F.B1→F.C1; isolation pin retires post-merge]; v20 update S1400+S1401 [§1.22 domains/revenue/1400_revenue_domain_scoping — Group 1400 Revenue arc opened with Phase 0 parent scoping doc + first application of Chris's F.i/F.ii/F.iii methodology; Rigby Light SIGN cycles 1+2 both SIGN-clean; 9 Chris-locked decisions across 3 "agree all" rounds — AND §1.23 domains/revenue/1401_revenue_opportunity_discovery_scoring_audit — first Group 1400 child audit shipped, Category A Opportunity Discovery + Scoring; 20-section playbook §11.2 template + §13 6-parallel-Explore sweep + parent-Claude verifier-loop pre-SIGN corrections on 5 sub-agent claims + Rigby SIGN cycles 1+2 on fresh isolation pin pa-16d8b24d30e7a7d8 → SIGN-clean cycle 2 High confidence after 4-fold cycle 1; NEW dual opportunity representation drift finding (5 consumer sites in consumers_base.py stream from intelligence_engine in-memory source, not persistent Django Opportunity); sports lane resolved as SEPARATE LANE with wording refinement; F1 provenance drift + F3 Redis-only durability CANDIDATE HIGH; NEW debt T5 Celery route duplicate; ownership gap CONFIRMED deferred to Child E per D28; S1273 §10.3 UNKNOWN #1 Opportunity model location RESOLVED at core/models_unified_system.py:1201])
---

# Architecture Research Index

> **What this is.** The front page of Donkey Betz's engineering
> encyclopedia. A Staff Engineer joining the project six months
> from now should read this document **first** — before opening
> any code, before reading CLAUDE.md, before touching a runtime
> file. It tells them what architectural research exists, why it
> exists, what order to read it in, and what decisions should
> never be made before reading specific documents.
>
> **What this is not.** A markdown link list. A taxonomy of every
> file under `docs/`. A historical archive. The wider `docs/`
> corpus has its own lifecycle (see
> `docs/00-START-HERE/DOC_LIFECYCLE.md`); this index governs the
> **research library specifically** — the docs that capture
> architectural reasoning *before* implementation.

---

## 0. Philosophy — why a research library exists

Before any system on this platform gets built or rebuilt, four
disciplines apply, in order:

1. **Research first.** Open-ended questions get a doc, not a
   sprint plan. The doc captures evidence with file:line cites
   and explicit unknowns; nothing is invented.
2. **Inventory before design.** Before you propose a primitive,
   you have to know what primitives already exist. The platform
   has **585 models**, **83 agents**, **113 PA tool schemas**,
   **91 enabled beat tasks** (see `docs/PLATFORM_INVENTORY.md`).
   Anything you "design" without that count in front of you is
   likely either re-inventing or violating
   `docs/EMPLOYEE_OS_PRIMITIVES.md` §2 (the anti-duplication
   matrix).
3. **Reuse before invention.** If an existing primitive does
   80% of the job, the right move is a wrapper, not a new model.
   Every "new model" instinct has cost an operator hour before;
   the names of those hours live in
   `EMPLOYEE_OS_PRIMITIVES.md` §2.
4. **Implementation last.** Once research + inventory + reuse
   are documented and reviewed, only then does code follow.
   PRs reference the research that justified them; the research
   exists to make the PR small.

These four disciplines map to the four document types you will
find in this library: **Audit**, **Inventory**, **Sketch**,
**Decision Record**. The first three precede code; the fourth
documents what the team decided once code is imminent.

**The verifier loop is the load-bearing rule.** Every research
doc in this library is grounded in direct file reads (Grep,
Read, ORM probes) — never recall, never assumption. When a
sub-agent produces evidence, the parent agent re-verifies a
sample by directly reading the cited file:line before
synthesizing. Rigby (the platform's PA / co-author) gets an
independent SIGN review on every doc before it's considered
publishable. Verdicts are **SIGN-clean**, **SIGN-with-edits**,
or **NEEDS-MORE**; edits are folded and the verifier_loop
frontmatter field is updated.

---

## 1. Current Architecture Research Library

The library has **two scopes as of S1273:**

- **The Employee OS arc (§1.1–§1.8):** an 8-doc chain that goes
  deep on a single subsystem. Each doc builds on the previous;
  read in order unless goal-driven (see §2 reading paths). This
  is the arc that began S1268 and closed STAGE 2 at S1272.
- **The whole-platform inventory (§1.9):** one doc, whole-
  platform scope. Independent of the Employee OS arc — read it
  when you need to know what domains exist across all of Donkey
  Betz, not when you're going deep on one subsystem. S1273 close
  registered it as "the whole-platform counterpart to the
  Employee OS research library" (Chris's direction).

**When to read which.** If your work touches a subsystem the
Employee OS arc has already researched (comms, governance,
authority, actor identity, mission orchestration), go to §1.1-
§1.8 for the deep dive. If your work touches a subsystem NOT in
that arc (frontend, spiders, RAG, betting, revenue, notifications,
etc.) — or if you're new to the platform and need the shape of
the whole thing — start with §1.9.

The two scopes will merge over time: as future missions bring
§1.9's LIGHT-coverage domains up to DEEP, they'll get their own
research docs registered as §1.10+, and §1.9 will remain the
navigation-and-classification layer.

### 1.1 `employee_os_communication_substrate_audit.md`

- **Title.** Employee OS Communication Substrate — Audit
- **Purpose.** Inventory every communication / collaboration
  primitive the platform already ships, classify each one for
  reuse, and identify the failure classes any future
  inter-employee protocol would inherit.
- **Status.** Draft → Active (SIGN-clean from Rigby S1268
  conversation `pa-01e90a1d36f54880`).
- **Research type.** Inventory + Architecture Audit + Failure
  Analysis (composite).
- **Primary questions answered.**
  - What communication substrates exist today?
  - Which are safe / wrappable / off-limits for reuse?
  - What's the receipt contract on Celery-dispatched tools?
  - What's the silent-failure history Employee OS would
    inherit?
- **Dependencies.** `PLATFORM_INVENTORY.md` (runtime
  anchor), `EMPLOYEE_OS_PRIMITIVES.md` (§2 anti-duplication
  matrix), `topics/employee-os.md`,
  `topics/agent-system.md`, `topics/personal-assistant.md`,
  `handoffs/SESSION_1267_*.md`.
- **Recommended next reads.** §1.2 (protocol sketch), then
  §1.3 (collaboration patterns).
- **Overall importance.** Foundational. Anything that touches
  inter-employee or inter-agent comms needs this read first.

### 1.2 `employee_os_communication_protocol_sketch.md`

- **Title.** Employee OS Comms Protocol Sketch — Platform
  Auditor → Chief of Staff
- **Purpose.** Take the substrate audit's `SAFE TO REUSE`
  primitives and scope the *first* concrete inter-employee
  write path. Reuse-only — explicit "do not enable
  `messaging_tool.send_message`" + explicit "no new model."
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; two substantive edits folded — L3 helper-side dedupe
  + cadence expires_at default; two clarifications folded).
- **Research type.** Design Research / Protocol Sketch (not a
  decision record — no implementation greenlight).
- **Primary questions answered.**
  - What does an inter-employee notice look like as a bounded
    DM on existing `MessageThread` + `DirectMessage`
    primitives?
  - How does it thread without polluting the existing
    per-(employee, job) shift-report channels?
  - What's the dedupe contract (helper-side L1/L2/L3,
    caller-side defense-in-depth)?
  - What stays out of scope for v0 (HumanAttentionItem
    spawning, reply lane, fan-out, cross-fleet)?
- **Dependencies.** §1.1 (substrate audit must be read
  first); `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1267_EMPLOYEE_4_BUG_TRIAGE_SHIP.md`.
- **Recommended next reads.** §1.3 (the wider collaboration
  audit Rigby asked for as the next-mission frame).
- **Overall importance.** High for anyone scoping the first
  cross-employee write surface. Lower for anyone whose work
  doesn't touch inter-employee messaging.

### 1.3 `employee_os_collaboration_patterns.md`

- **Title.** Employee OS Collaboration Patterns — Platform-
  Wide Audit
- **Purpose.** Step back from "how do employees communicate"
  to "how do autonomous components *already* collaborate
  across the platform?" — so any future Employee OS work
  reuses existing collaboration mechanisms rather than
  reinventing them.
- **Status.** Draft → Active (SIGN-with-edits from Rigby
  S1268; one substantive correction folded — MissionRunner
  `verdict_issued` event is conditional on
  `auto_emit_verdict=True`, not guaranteed; one architectural
  blind-spot note added on canonical idempotency key across
  the two orthogonal orchestration paths).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc.
  - What are the eleven distinct collaboration substrates
    already in production?
  - Which 33 primitives are SAFE to reuse, which 10 need
    wrappers, which 4 should not be reused, and which 5 are
    UNKNOWN?
  - What 29 documented failure modes does any future
    collaboration design inherit (12 new beyond the substrate
    audit's baseline)?
  - What is the canonical foundation for future Employee OS
    collaboration? (MissionRunner + OpsRun + OpsRunEvent +
    AgentFollowupSubscription + `post_shift_report`-style
    helpers.)
- **Dependencies.** §1.1 + §1.2 (both prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `topics/employee-os.md`, `topics/celery-workers.md`,
  `topics/agent-system.md`, `topics/initiative-pipeline.md`.
- **Recommended next reads.** Once this lands, the
  recommended **next research mission** is Governance +
  Authority Evolution (see §5 below). The next *design* work
  is the protocol sketch's v0 PR (assuming Chris greenlights
  it).
- **Overall importance.** Mandatory for anyone touching
  collaboration, orchestration, scheduling, mission
  coordination, or autonomy escalation.

### 1.4 `governance_authority_evolution.md`

- **Title.** Governance + Authority Evolution — Architectural
  Discovery
- **Purpose.** The canonical research anchor for every future
  authority or governance discussion. Inventories the governance
  + authority surface that exists today, identifies what's
  runtime-enforced vs. observational vs. documentation-only,
  surfaces the gaps, and recommends the next research mission
  (Symbol Mapping Architecture).
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1269;
  two must-fix edits folded — Exec Summary now uses canonical
  "four planes" framing instead of mixed "two + plus" framing,
  and gate count corrected 34→35; two clarifications folded —
  DO-NOT-REUSE-for-enforcement language on
  `JobContract.authority`, F4 budget-plane intent claim
  softened).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.3 shape).
- **Primary questions answered.**
  - Q1–Q12 from the mission spec, answered explicitly in the
    doc's §12.1.
  - What are the four governance planes (autonomy / authority /
    budget / human governance) and why don't they compose today?
  - Where is authority enforced (35 runtime gates) vs. where is
    it only observed (warn-mode telemetry) vs. where does it
    disappear entirely (between MissionRunner and step.fn
    execution)?
  - What blocks the move from warn-mode to enforce-mode?
    (Symbol mapping — F2 + §11.)
  - What is the canonical foundation for governance reuse?
    (48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED /
    3 UNKNOWN.)
- **Dependencies.** §1.1 + §1.2 + §1.3 (prior research docs);
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md` row 17
  (GovernanceState + KillSwitch); `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
  (warn-mode design + enforce-mode prereqs).
- **Recommended next reads.** §1.5 (this index, for navigation
  context). The recommended **next research mission** per §11
  is Symbol Mapping Architecture (resolves §10 Q1 + Q12 of the
  collaboration audit + this doc's §9 Q1).
- **Overall importance.** Mandatory for anyone touching
  authority enforcement, governance modes, kill switches,
  budget controls, human approval lifecycles, or feature-flag
  gates.

### 1.5 Index doc (this file)

- **Title.** Architecture Research Index
- **Purpose.** Navigation. This doc.
- **Status.** Active (v3 — S1271 added §1.6 Symbol Mapping and
  §1.7 Actor Identity entries; §3-§9 updated per maintenance
  rules).
- **Research type.** Navigation / Decision Record (light).
- **Maintenance rule.** Every future research doc must update
  this index — see §10.

### 1.6 `symbol_mapping_architecture.md`

- **Title.** Symbol Mapping Architecture — Architectural Discovery
- **Purpose.** The canonical research anchor for the "WHAT
  action" question. What architectural bridge is missing between
  `JobContract.authority` policy strings and runtime symbols
  (tool names, step names, task names, function calls, model
  writes)? Enumerates the design space so authority enforcement
  can eventually be scoped.
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1270
  conversation `pa-cbcc410b32714f60`; two must-fix + three
  strongly-recommended optional edits folded — §8 narrowed
  `_AuthorityContractMalformedError` scope, §2.6 added
  parallel-vocabulary type/shape anchor, I-S4 wording softener,
  I-S3 dual-cite F1+F3, Option E "reversibility ≠ preference"
  disclaimer; §4.1 row 24 added for
  `AssistantProfile.get_allowed_tools`; §2.4 normalization caveat;
  §9 F11 with 7 architectural blind spots).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.3 + §1.4
  shape).
- **Primary questions answered.**
  - Q1–Q8 from the mission spec, answered explicitly in the
    doc's §12.1.
  - What are the 57 unique authority strings (68 total entries),
    and where do they live?
  - What runtime action surfaces exist (12) and which carry
    action_class metadata today? (None.)
  - What identifier registries already exist on the platform
    (24) that could serve as reuse candidates?
  - What are the five mapping options (A/B/C/D/E) and their
    tradeoffs?
  - Where are the 20 candidate enforcement layers?
  - What historical failures (5 YES + 10 PARTIALLY + 8 NO of 23)
    would Symbol Mapping have prevented?
- **Dependencies.** §1.4 (the governance audit named this
  mission), §1.3, §1.1; `PLATFORM_INVENTORY.md`;
  `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication matrix;
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §1.7 (Actor Identity is the "WHO"
  companion). Then §9 roadmap STAGE 2 (Authority Enforcement
  Design Space) — the design mission that composes both.
- **Overall importance.** Mandatory for anyone scoping authority
  enforcement, adding a new employee's authority contract, or
  proposing action_class metadata on any runtime surface.

### 1.7 `actor_identity_attribution_architecture.md`

- **Title.** Actor Identity & Attribution Architecture —
  Architectural Discovery
- **Purpose.** The canonical research anchor for the "WHO
  performed it" question. Direct follow-on to §1.6 Symbol
  Mapping. When the platform records an action, how does it know
  who performed it? Both prereqs must land before authority
  enforcement can exist.
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1271
  conversation `pa-cbcc410b32714f60`; four must-fix + two
  strongly-recommended optional edits folded — §8.5 added
  introducing the executor_actor / sponsor_actor / principal_user
  3-role vocabulary as normative for the doc + §11 F11 summary
  finding; F1 language softened to "cannot answer reliably or
  queryably"; F9 softened to "the cleanest enforcement primitive";
  §3.5 added inventorying missing surfaces the platform does NOT
  ship; §9.4 Attribution-first counterargument paragraph; §5
  role-confusion framing note).
- **Research type.** Architectural Discovery + Platform-Wide
  Inventory + Failure Analysis (composite — same as §1.6 shape).
- **Primary questions answered.**
  - Q1–Q10 from the mission spec, answered explicitly in the
    doc's §14.1.
  - What actor identity concepts exist (19)?
  - Where is actor identity recorded (22 attribution surfaces —
    13 Explicit / 2 Inferred / 4 Ambiguous / 1 Unreliable /
    2 Missing)?
  - Where does identity change shape (14 shape changes, 3
    structural drop boundaries)?
  - What identity collisions have happened (15 historical
    incidents; 7 YES + 4 PARTIALLY + 4 NO — 73% effective
    case)?
  - What existing identity registries can be reused (25 — 14 SAFE
    + 7 WRAPPER + 0 DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN)?
  - What are the 17 candidate enforcement boundaries?
  - What does "actor" need to mean for Employee OS? (§8, six
    semantic questions posed.)
  - What is the relationship between actor identity and
    authority? (§9, the WHAT + WHO = enforcement primitive.)
  - What should the next research mission be? (§13.1 — Authority
    Enforcement Design Space.)
- **Dependencies.** §1.6 (Symbol Mapping is the WHAT companion),
  §1.4 (governance planes), §1.3, §1.1; `PLATFORM_INVENTORY.md`;
  `EMPLOYEE_OS_PRIMITIVES.md`; `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §9 roadmap STAGE 2 (Authority
  Enforcement Design Space) — the first design mission that
  consumes both §1.6 and §1.7.
- **Overall importance.** Mandatory for anyone touching actor
  identity on any audit surface, adding a `user` FK to OpsRun (a
  documented anti-pattern per §1.7 F11 without role clarity),
  proposing an actor primitive, or scoping the delegation/trust
  question. **F11 is especially load-bearing**: a single "actor"
  label is insufficient — enforcement-grade attribution requires
  at least executor_actor / sponsor_actor / principal_user as
  distinct roles.

### 1.8 `authority_enforcement_design_space.md`

- **Title.** Authority Enforcement Design Space — Architectural
  Discovery
- **Purpose.** The design-space research that must precede any
  enforce-mode PR. Symbol Mapping (S1270) answered WHAT action;
  Actor Attribution (S1271) answered WHO acted; this doc asks:
  given both prereqs are shipped as research, what are the
  possible ways the platform could eventually decide whether an
  actor was allowed to perform a mapped action? Enumerates the
  design space so a downstream design-with-Chris-gate mission
  can consume it. **Design-space only — no implementation,
  no decision.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1272
  conversation `pa-cbcc410b32714f60`; **Medium confidence**;
  8 must-fix edits folded — §3 gained 3 first-class boundaries
  (WebSocket, Fleet, Spider) closing a completeness gap Rigby
  flagged as "biggest architectural risk"; §9.0 neutrality
  guardrail; §9.1 + §9.2 annotation-burden failure modes;
  §9.6 policy-ossification risk; §8.4 rephrased separating
  prevent-modes from audit/warn modes; §10 Tier-0 hazards
  callout naming #1 + #8 + #15 as disproportionately-high
  blast radius; §6.1 role-propagation rule of thumb;
  §14 P0/P1 dependency-not-preference semantics + §14.2
  (i)/(ii) split.
- **Research type.** Design-Space Research + Platform-Wide
  Inventory + Composition Analysis + Failure Analysis
  (composite — first mission carrying design-space content per
  §9 STAGE 2 pacing note; still research-only, not design
  decision).
- **Primary questions answered.**
  - Q1–Q12 from the mission spec, answered explicitly in the
    doc's §15.1.
  - What are the 24 current enforcement-adjacent inputs
    (13 RUNTIME-VERIFIED / 7 OBSERVATION-ONLY / 3 ASPIRATIONAL
    / 1 UNKNOWN + 8 GAPS)?
  - What are the 20 candidate enforcement boundaries
    (17 original + 3 SIGN-added: WebSocket, Fleet, Spider)?
  - What are the 12 enforcement modes and their 204-cell
    (17×12) mode × boundary compatibility matrix?
  - What are the 4 interpretations per AuthorityLevel value
    (16 total; §5)?
  - How do executor_actor / sponsor_actor / principal_user
    compose across 11 canonical scenarios (§6)?
  - How does authority enforcement compose with the 4 governance
    planes (§7; 1 existing cross-plane touch + 8 new
    composition questions)?
  - Which historical incidents would each mode have prevented
    (33-incident matrix across 4 prior catalogs; §8)?
  - What are the 6 major design options (A-F; §9)?
  - What are the 15 anti-patterns to avoid (§10; Tier-0
    hazards flagged)?
  - What are the 15 prerequisites for enforce-mode and their
    dependency DAG (§11)?
- **Dependencies.** §1.6 (Symbol Mapping — WHAT input premise),
  §1.7 (Actor Attribution — WHO input premise), §1.4
  (governance planes), §1.1, §1.3;
  `PLATFORM_INVENTORY.md`; `EMPLOYEE_OS_PRIMITIVES.md`;
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`.
- **Recommended next reads.** §14.1 recommends Symbol Mapping
  Option Selection Design as P0 next research. The 6 design
  options in §9 will be consumed by that downstream mission +
  the Authority Enforcement Design Decision that follows it.
- **Overall importance.** Mandatory reading for anyone scoping
  authority enforcement, evaluating one of the 6 §9 design
  options, proposing an OpsRun schema change, or wiring a new
  enforcement boundary. **F1 is especially load-bearing:**
  AuthorityLevel has exactly one runtime consumer today
  (shape-counter at `mission_runner.py:864-867`) — the enum is
  policy metadata, not enforcement metadata; any design
  introduces the first decision-making consumer. **F8 fail-open
  precedent is the second load-bearing finding:** LLMEnforcer
  at `llm_enforcer.py:237-238` sets the platform's precedent
  for INLINE-gate error handling — any authority enforcement
  design must decide fail-open vs. fail-closed and cite
  rationale.
- **Boundary caveat.** The 3 SIGN-added boundaries
  (WebSocket / Fleet / Spider) are named but not yet
  cross-tabulated against the 12 modes in the 204-cell matrix.
  A future research pass or design mission should extend the
  matrix.

### 1.9 `platform_architecture_inventory.md`

- **Title.** Donkey Betz Platform Architecture Inventory — first
  whole-platform map
- **Purpose.** The whole-platform counterpart to the Employee-OS-
  focused §1.1-§1.8 arc. Inventories every major architectural
  domain of Donkey Betz — 32 domains — with maturity ratings,
  research coverage, existing docs, drift, and technical debt.
  Names the recommended next 11 research missions. **This is the
  doc a Staff Engineer new to the platform should read to
  understand the shape of the whole system.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1273
  conversation `pa-02cfd3206302352f`; Medium overall confidence;
  6 substantive edits folded — (1) added missed §3.32 Revenue /
  Outreach / Engagement Pipeline domain + §4.9 cross-domain flow;
  (2) downgraded §3.27 Auth / Permissions maturity STABLE →
  PARTIAL with trust-boundary enumeration; (3) upgraded §3.7 LLM
  Provider Registry maturity WORKING → STABLE (core registry
  stable, failover missing); (4) tightened §1 Executive Summary
  count phrasing to autoblock-consistent language; (5) added
  §3.31 Event Bus vs Observability separation-of-concerns
  paragraph; (6) expanded §9 roadmap 10 → 11 missions with
  Revenue Pipeline canonical architecture doc elevated to #2).
- **Research type.** Architectural Inventory + Platform-Wide
  Mapping + Maturity Classification (whole-platform composite;
  distinct shape from §1.1-§1.8 which are Employee-OS-focused
  audits / sketches / discovery / design-space).
- **Primary questions answered.**
  - What are the 32 major architectural domains of Donkey Betz?
  - Which domains are mature (CANONICAL/STABLE) vs risky
    (PARTIAL/EXPERIMENTAL)?
  - Which domains are under-researched (NONE/LIGHT coverage)?
  - What are the 9 cross-domain flows that traverse ≥ 2
    domains?
  - Which systems duplicate or overlap (8 categories: multiple
    orchestration paths / multiple messaging systems / multiple
    identity concepts / multiple memory stores / multiple
    governance surfaces / multiple content pipelines / multiple
    task/execution logs / multiple agent dispatch systems)?
  - What are the 11 recommended next research missions, ranked
    by architectural uncertainty × risk × reuse × decisions
    unblocked?
- **Dependencies.** `PLATFORM_INVENTORY.md` (authoritative
  counts anchor), `PLATFORM_WHAT_IT_IS.md` (narrative anchor),
  `EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives),
  `KNOWLEDGE_PIPELINE.md`, `EVENT_SYSTEM_INVENTORY.md`,
  `AUDIT_FINDINGS.md` §12. Also depends on the entire Employee
  OS arc (§1.1-§1.8) for the subset of findings that overlap;
  cites governance-authority-evolution.md (§3.23),
  symbol_mapping_architecture.md (§9.1), and
  actor_identity_attribution_architecture.md (§5.3) where
  relevant.
- **Recommended next reads.** Depends on goal:
  - If interested in specific domain: jump to that §3.n
    inventory + cited docs.
  - If interested in cross-domain flows: read §4 (9 flows).
  - If interested in what's next: read §9 (11-mission roadmap
    — top-3 are Authority Enforcement Design Space (§5.2c
    here), Revenue Pipeline canonical architecture (§5.12
    here), Observability Deduplication Audit (§5.13 here)).
- **Overall importance.** **Foundational for whole-platform
  understanding.** The Employee OS arc (§1.1-§1.8) is deep on
  one subsystem; §1.9 is wide on all of them. A new hire should
  read §1.9 first to know the map, then dive into whichever arc
  their work touches. Existing team members should reference §1.9
  when scoping cross-domain work or evaluating "does this touch
  a mature domain or an experimental one?"
- **Verifier-loop note.** Six parallel Explore sub-agents
  produced independent domain sweeps; parent synthesized into
  the 32-domain map. Every domain row is grounded in file:line
  cites OR flagged UNKNOWN. Rigby SIGN-with-edits (fresh pin
  `pa-02cfd3206302352f`, NOT the shared S1270+ arc pin
  `pa-cbcc410b32714f60` — another Claude Code was on that pin;
  Chris flagged the context-crossing risk mid-session; isolation
  pin used to keep S1273 work separate).

### 1.10 `symbol_mapping_option_selection_design.md`

- **Title.** Symbol Mapping Option Selection Design — Research +
  Design Preparation (Chris-gated decision)
- **Purpose.** The design-preparation mission that follows §1.8
  Authority Enforcement Design Space. Where §1.6-§1.8
  enumerated options neutrally, §1.10 is the **first mission
  producing an evidence-based recommendation**: which of §1.6's
  5 Symbol Mapping options should Chris choose as v0? **The
  recommendation is a starting point for Chris, not a
  substitute for his decision.**
- **Status.** Draft → Active (SIGN-with-edits from Rigby S1274
  conversation `pa-cbcc410b32714f60`; **Medium confidence**;
  Rigby recommendation: **Modify** — agree with Option E as v0
  subject to 4 must-fix tightenings; all folded).
  Four must-fix folded:
  (1) §8.8 whole-platform generalization claim tightened —
      "STRONG once producers exist; v0 coverage remains narrow
      (2/4/14 per §8.1); Fleet/WebSocket/Spider excluded until
      instrumented" (was overstated as absolute STRONG);
  (2) §10.3.1 catastrophic-action graduation guardrail added —
      4 telemetry triggers force Chris decision within 30 days
      (prevents "E-forever cope");
  (3) §12.1 non-NULL misclassification drift pattern added —
      sample-based truthing + cross-source consistency +
      golden-flow tests (higher-risk than producer omission
      per Rigby "wrong-but-non-NULL action_class" concern);
  (4) §11 employee_handle vs. executor_actor distinction
      clarified — employee_handle is Employee OS identity
      (NULL for non-mission actions); executor_actor is
      generalized runtime executor. Do NOT collapse.
- **Research type.** Design Preparation + Comparative Analysis
  + Evidence-Based Recommendation (composite; first mission in
  the S1268-founded library carrying an actual recommendation
  Chris can gate).
- **Primary questions answered.**
  - Q1-Q10 from mission spec, answered explicitly in the doc's
    §15 open questions + §16 next mission recommendation.
  - Which of §1.6's 5 Symbol Mapping options is safest v0?
  - Which is the recommended end-state?
  - What is the smallest reversible design that unlocks
    authority telemetry?
  - What must remain out-of-scope for v0?
- **Recommendation shape.**
  - **v0 (recommended):** **Option E — Evidence-only mapping.**
    Extend a minimum set of audit models (`ToolCallRecord`,
    `OpsRunEvent`, `LLMCallEvent`, `CeleryTaskEvent`,
    `AgentExecution`) with optional `action_class` field + all
    three actor role fields; instrument 3-5 highest-leverage
    producer sites incrementally; emit
    `authority_action_observed` events; **never blocks**.
  - **End-state (Chris-gated later; possibly 6-24 months
    out):** E foundation + Option B (tool schema
    `action_class` attribute) layered on top for pre-dispatch
    tool-mediated enforcement.
  - **Explicitly rejected:** Option C bundled standalone.
  - **Deferred:** Options A, B, D as tertiary layers pending
    telemetry evidence from Phase 5 E-only steady state.
  - **Maintenance note:** Option E as recommendation is for v0
    ONLY. It is **not implementation** and **not enforce-mode**.
    Chris gates every downstream step: (a) whether to ratify
    Option E as v0, (b) whether to graduate to E+B per §10.3.1
    guardrail triggers, (c) whether to add more layers.
- **Dependencies.** §1.4 (governance planes), §1.6 (5 mapping
  options — the input premise), §1.7 (3-role vocabulary — MUST
  be preserved), §1.8 (design space + 15-prereq DAG),
  `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md` (warn-mode
  precedent), `EMPLOYEE_OS_PRIMITIVES.md` §2 anti-duplication.
- **Recommended next reads.** §16 recommends Symbol Mapping
  Event Schema Design as the next mission (design the
  concrete event schema + producer instrumentation contract +
  retention policy + Bug Triage step 4 extension). Rigby SIGN
  at close of that mission.
- **Overall importance.** Foundational for anyone scoping the
  first authority-enforcement PR. Reading order: §1.6 (options
  enumerated) → §1.7 (actor vocabulary) → §1.8 (design space +
  prereqs) → §1.10 (recommendation) → downstream Symbol Mapping
  Event Schema Design mission (design → implementation gate).
  **F1 load-bearing:** the recommendation is E because it is
  the *most reversible* and *safest v0*, not because it is the
  *best end-state*. Do not read §1.10 as "E is the answer";
  read it as "E is the safest starting move." Chris re-decides
  at every phase per §10.3.1 guardrail.

### 1.11 `DOMAIN_RESEARCH_PLAYBOOK.md`

- **Title.** Domain Research Playbook — canonical framework
  for every Donkey Betz architectural research group
- **Current version.** **v2** (S1276, 2026-07-01). Extended in
  place from v1 (S1274). v2 restructures into 7 parts / 24
  sections and formalizes fifteen areas that emerged after v1
  shipped. Version history in playbook §20 changelog.
- **Purpose.** Process document that codifies the methodology
  developed across S1268-S1275 into a **reusable framework** so
  future Claude Code sessions can start a domain research group
  with a short request like *"Start research group 1300:
  Memory"* — no 4,000-word prompt required. v2 additionally
  makes arcs *closable*: Chris can now say *"Close research
  group 1300"* and the framework produces a canonical summary.
  Standardizes: numbering ranges (1300 Memory → 1900 Event
  Architecture) with xx99 canonical-summary reservation,
  parent-with-children arc lifecycle, phase discipline
  (research / design-preparation / design-decision / process /
  navigation / implementation), output paths
  (`docs/research/domains/<slug>/<session_id>_<slug>_<type>.md`),
  self-describing metadata standard, 28 canonical audit
  questions, 20-section child audit template + parent template
  + canonical summary template, 6 parallel Explore sub-agent
  sweeps, classification rules (Coverage / Maturity / Risk /
  Finding Type / Integration Strength), cross-reference
  policy, stage-scoped Rigby SIGN routing, commit rules,
  graduation criteria, cross-arc dependency mapping,
  generalization requirements, and evolution policy for the
  playbook itself.
- **Status.** Active (process documentation — no Rigby SIGN
  routed per §15's own rule for `authority: process`).
- **Research type.** Process Documentation / Meta (framework
  for other docs; does not produce research findings itself).
- **Primary questions answered.**
  - How does a future Claude Code session start a domain
    research group (single audit vs parent-with-children)?
  - What research group ranges are planned (1300s-1900s)?
  - What is the lifecycle of a research group (STAGE 0 parent
    → STAGE 1 children → STAGE 2 canonical summary → STAGE 3
    index update → STAGE 4 complete)?
  - How do research, design-preparation, and implementation
    differ, and how do docs signal which phase they belong to?
  - What belongs in a parent doc vs a child audit vs a
    canonical summary?
  - What is the canonical folder structure and file naming?
  - What metadata does every research doc need to be
    self-describing?
  - How do docs cross-reference each other without
    duplicating content?
  - What are the 28 canonical questions every child audit
    must answer?
  - What classifications must every domain audit use?
  - What is the Rigby SIGN review policy per stage?
  - When is it OK to commit vs when should draft stay
    uncommitted?
  - When is a research group *complete* (objective graduation
    criteria)?
  - How do cross-arc dependencies + delegations get recorded?
  - How does the playbook itself evolve without breaking
    older research groups?
- **Dependencies.** §1.9 (32-domain map — the audit target
  list), `docs/research/platform/cross_domain_integration_audit.md`
  (integration gap map — the S1274 sibling context each domain
  audit inherits), `docs/PLATFORM_INVENTORY.md` (runtime
  counts), `docs/research/domains/memory/1300_memory_domain_scoping.md`
  (S1300 parent-with-children exemplar — the doc that proved
  the v2 arc shape). Also inherits all lessons from §1.1-§1.8
  methodology history.
- **Recommended next reads.** For anyone starting a research
  session: read this playbook first (§1-§7 minimum), then the
  S1273 §3.N row for your target domain, then the S1274 §2.N +
  §3-§10 rows for cross-domain context, then existing topic
  docs for the domain. Only then execute STAGE 0 (parent) or
  STAGE 1 (single audit).
- **Overall importance.** **Foundational for every future
  research session.** Reading order for a fresh Claude Code:
  §1.11 (this playbook) → whatever domain the user picked.
  This should be the FIRST doc a fresh session reads after
  `CLAUDE.md`. The v2 additions make the framework
  self-describing — a fresh Claude Code that reads *only* the
  playbook + ARCHITECTURE_INDEX + PLATFORM_INVENTORY can
  execute a research arc end-to-end.
- **Initial domain queue** (from playbook §22): 1300 Memory
  (opened S1300 — parent locked), 1400 Revenue, 1500 Sports,
  1600 Content, 1700 Observability, 1800 HumanAttention, 1900
  Event Architecture. Queue order is a default, not a
  dependency — sessions can pick any.
- **Distinguishing property.** This is `authority: process`
  with `version: v2`, not `authority: research`. It sets rules
  for other docs rather than producing findings. Chris ratified
  v1 registration at S1274 close (*"register it now and
  commit"*) and v1 → v2 extension at S1276 open (*"Formalize
  the research process itself so future domain research
  becomes repeatable"*).
- **Backwards compatibility note.** Research groups closed
  under v1 (Employee OS arc §1.1-§1.8, whole-platform §1.9,
  cross-domain integration §1.10-§1.12) remain valid under
  v1. They do not retroactively conform to v2 additions. Per
  playbook §20, older research groups reference the playbook
  by version — v2 does not invalidate v1 outputs.

### 1.12 `symbol_mapping_event_schema_design.md`

- **Title.** Symbol Mapping v0 — Event Schema Design (`authority_action_observed`)
- **Purpose.** Closes §5.2d. Takes §1.10's Option E v0
  recommendation and pins the concrete event schema: canonical
  name, two-surface host (`OpsRunEvent` for mission scope +
  `ToolCallRecord.parameters` for non-mission tool calls,
  unified via a new `authority_action_observed_stream` DB
  view), 21 payload fields (7 required + 5 semi-required + 6
  optional + 3 reserved), 4 v0 emitters + 1 v0 first consumer,
  4-tier `mapping_confidence` enum with DECLARED explicitly
  non-authoritative, drift-detection stack across 6 patterns
  (NULL rate, wrong non-NULL via sampled truthing, zero-fire,
  cross-emitter disagreement, invariant + reserved-keys
  violations, schema drift), 3 golden flows, batch-mode v0
  dashboard, 15 out-of-scope items, and a change log capturing
  Rigby SIGN fold decisions.
- **Status.** Draft (Rigby SIGN-with-edits folded — 8
  must-fixes + bonus #9; awaiting Chris canonical sign-off).
- **Research type.** Design preparation (third design mission
  in the STAGE 2/3/4 Symbol Mapping arc, following §1.6
  Architectural Framing and §1.10 Option Selection).
- **Primary questions answered.**
  - What is the canonical event name? → `authority_action_observed`
  - Which existing audit surface(s) host it? → two-surface stream
    (`OpsRunEvent` + `ToolCallRecord.parameters`) + UNION view
  - What is the minimum viable schema, field by field?
  - Which 4 emitters go first, and what is the first consumer?
  - How is `action_class` populated per emitter × confidence tier?
  - How does `mapping_confidence` work — and why is DECLARED
    explicitly non-authoritative?
  - How are the 3 actor roles + graph position + identity marker
    kept separate?
  - How does the design prevent wrong-but-non-NULL
    false confidence? → sampled-truthing loop + weighted
    cross-emitter disagreement + invariant validator + golden
    flows
  - What are the first 3 golden flows?
  - What does the v0 dashboard / query API look like?
  - What is explicitly out of scope for v0? → 15-item list
- **Dependencies.** §1.10 (Option E as v0 ratified), §1.7
  (3-role actor vocabulary preserved), §1.6 (architectural
  framing), §1.8 (§11 15-prereq DAG — closes prereqs #3
  Evidence Event Schema and #4 Violation Event Schema at v0
  scope), `handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
  (`authority_contract_observed` warn-mode precedent —
  `authority_action_observed` is the action-level parallel),
  `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication —
  justification for reusing existing audit models).
- **Recommended next reads.** After Chris canonical sign-off:
  the implementation prep sequence (rollout plan §15 outlines
  P0→P5 phases across ~10 weeks). Before then: cross-read
  against §1.10 §16 (out-of-scope list — that mission handed
  off 11 items that §1.12 §16 closes with 15 items).
- **Overall importance.** **First mission in the library that
  ships a concrete implementation-ready schema.** Prior
  Symbol Mapping missions produced framing (§1.6) and selection
  (§1.10); this one produces the field-level spec. Not yet
  implemented — Chris gates every subsequent PR. Rigby SIGN
  fold captures 8 must-fixes (ambient OpsRun → two-surface,
  drop required `event_id`, drop `notes`, downscope
  `producer_version`, rename `delegator_actor` → `caller_actor`,
  reframe "5 producers" → "4 emitters + 1 consumer", rename
  INFERRED → DECLARED, add sampled-truthing loop, DEFINITE ≠
  global truth) plus bonus #9 (reserved-keys policy + per-field
  caps).
- **Maintenance note.** This is the third design-preparation
  doc in the STAGE 2/3/4 Symbol Mapping arc. Do NOT treat as
  implementation greenlight — the rollout plan in §15 is a
  sequencing sketch, not a merged PR. If Chris ratifies the
  design at review, the next research artifact is either a
  Trust Propagation Model (§5.3) or the Employee Boundary
  Escalation Contract (§5.4) — both P1s at this point.

### 1.13 `domains/memory/1300_memory_domain_scoping.md`

- **Title.** S1300 Memory — Parent Architecture Scoping
  (Group 1300 mission plan)
- **Purpose.** First **parent-scoping** doc in the library —
  a shape not previously exercised. Chris opened S1300 with
  the playbook §11 short command "Start research group 1300:
  Memory" but pushed back on the standard a-f scope-pick
  framing: "Your clarification uncovered an architectural
  ambiguity rather than a simple scoping question. Treat this
  as a Phase 0 domain-definition exercise." The doc answers
  the single structural question — is "Memory" one domain or
  a parent capability composed of multiple architectural
  subdomains — enumerates 8 candidate subdomains (Categories
  A-H) grounded in existing inventory evidence, and asks
  Chris to gate parent-with-children vs single-audit before
  any audit work begins.
- **Status.** Active (parent — Chris decisions locked
  2026-07-01). Phase 0 complete. Session S1300 closed early
  per Chris directive; no P1 audit work in this session.
- **Research type.** Domain-definition / arc scoping
  (`authority: parent-doc`). Distinct from `authority:
  research` (audit findings) and `authority: process`
  (playbook rules).
- **Primary questions answered.**
  - Is "Memory" one domain? → No. §3 taxonomy enumerates 8
    candidate subdomains; S1273 already treats Memory as a
    3-row §3 cluster (§3.13/§3.14/§3.15) with §5.4 flagging
    "Multiple Memory / Knowledge Stores" independently.
  - Parent-with-children or single canonical audit? →
    Parent-with-children (Chris D1, 2026-07-01). Playbook §2
    rule 3 explicitly permits sub-grouping.
  - What is the Group 1300 arc shape? → S1300 parent →
    S1301 RAG Retrieval Lanes → S1302 Memory Persistence
    Architecture → S1303 Conversational/Thread Memory →
    S1304 Docs Corpus ↔ RAG Boundary → S1305 Runtime Memory
    Correctness → S1399 canonical summary (7 sessions total).
  - Which subdomain owns Employee OS mission memory? →
    Category G delegated to Employee OS 1200s follow-up arc
    (Chris D2). Group 1300 cross-links only; does not fold
    G in. Boundary respected: S1273 inventory homes it
    under §4 Employee OS, not §3.13.
  - Where does the RAG excluded_missing_provenance finding
    (surfaced at S1300 open — Rigby `search_docs` returned 8
    pre-filter → 7 excluded_missing_provenance + 1
    excluded_mismatch → 0 for OpsRun/MissionRunner/
    JobContract queries) go? → Parked as S1301 audit input
    under §6 (Chris D3). Not pursued in Phase 0.
  - Why the P2 rename? → "Memory Store Overlap Audit" →
    "Memory Persistence Architecture" (Chris D4). Wider
    frame captures durability + write/read paths + authority
    boundaries, not just overlap surfacing.
  - What closes the arc? → S1399 canonical summary planned
    (Chris D5): cross-cutting patterns across P1-P5,
    consolidated memory-subsystem shape, `PLATFORM_INVENTORY.md`
    §3 update recommendations, follow-on research queue.
- **Dependencies.** `DOMAIN_RESEARCH_PLAYBOOK.md` §11 short-
  command entry point (§1.11), `platform_architecture_inventory.md`
  §3.13/§3.14/§3.15/§5.4 (§1.9), `docs/narratives/KNOWLEDGE_
  RAG_MEMORY.md` (S1158 comprehensive narrative),
  `docs/KNOWLEDGE_PIPELINE.md` (flow map).
- **Recommended next reads.** After Chris canonical sign-off
  on §1.13 parent scoping (and greenlight on S1301 launch
  cadence — open D6 at S1300 close): begin `1301_memory_rag_
  retrieval_lanes_audit.md` under playbook §11 opening
  sequence, feeding the §6 provenance-filter finding as
  S1301 input.
- **Overall importance.** **First parent-scoping doc in the
  library** — a shape not previously exercised. Introduces
  the pattern where a research group opens with a taxonomy
  proposal that gates whether the group is one audit or an
  arc of child audits. Playbook §2 rule 3 already permitted
  sub-grouping; §1.13 is the first mission to actually
  exercise it. Also validates the DOMAIN_RESEARCH_PLAYBOOK.md
  short-command workflow — Chris's "Start research group
  1300: Memory" reached the playbook §11 opening sequence
  successfully.
- **Maintenance note.** This doc is the **parent** of Group
  1300. It is NOT itself an audit — it is the arc-plan that
  gates the child audits. If any child audit contradicts the
  parent's taxonomy boundaries, the child should update the
  parent (via a new v-number pass), not silently drift.
  Session S1300 ended EARLY at Chris close directive —
  Phase 0 scoping complete but no P1 audit work landed in
  this session. Open decisions at S1300 close: (D6) S1301
  launch cadence (default: pause for Chris review before
  greenlight); (D7) Rigby SIGN routing on parent doc
  (default: skip — playbook §9 attaches SIGN to audits, not
  scoping).

### 1.14 `RESEARCH_OPERATING_SYSTEM.md`

- **Title.** Research Operating System — the OS every Claude
  Code session executes in Donkey Betz
- **Current version.** **v2.1** (S1278, 2026-07-02). v1 →
  v1.1 (S1277 Rigby SIGN fold) → v2 (S1277 re-issue with 6
  new parts) → v2.1 (S1278 ratification + playbook cross-ref
  cleanup + §20 finalization).
- **Purpose.** The canonical process framework Claude Code
  executes across **every** class of work in the repo. Where
  the playbook (§1.11) governs research-class sessions
  specifically, this OS is the *superset* — it defines
  bootstrap sequence, request classification, per-class
  startup contracts, documentation authority hierarchy,
  research/completion contracts, research debt, ownership
  matrix, and Context-Kit boundary. Turns onboarding
  deterministic and prompt-independent. The success target:
  a brand-new Claude Code reads this document, executes
  bootstrap, classifies the user request, runs the matching
  startup contract, and begins contributing — **without Chris
  writing a 4,000-word prompt.**
- **Status.** **Active — CANONICAL** as of S1279 close
  (2026-07-02). v2.1 architecture complete; 3 P0 follow-up
  items landed at S1279 installation (CLAUDE.md pointer,
  `OPEN_ARCS.md`, START-HERE additions); OS status flipped
  `draft` → `active`. Every future Claude Code session
  executes this doc.
- **Research type.** Process Documentation / Meta / Canonical
  framework (analogous to §1.11 playbook but broader scope).
- **Primary questions answered.**
  - How does a fresh Claude think? (§3 Decision tree)
  - What does bootstrap look like? (§4 Level A + Level B)
  - How is a request routed? (§5 11 request classes + boundary
    rules)
  - What state surfaces exist? (§6 session + arc + runtime)
  - What is the documentation authority hierarchy? (§7 11 tiers
    with truth-authority vs read-priority split)
  - What startup contract per class? (§8.1-§8.11)
  - What thinking templates exist? (§9 registry)
  - What is discoverable today? (§10 audit)
  - Who owns which doc? (§11 ownership matrix + anti-patterns)
  - How does research reduce prompt burden? (§12 target rhythm)
  - What is a Research Contract? (§13 8 mandatory fields)
  - What is a Completion Contract? (§14 10-item close checklist)
  - What is Research Debt? (§15 concept + 7 categories +
    priority formula + escalation)
  - What is the one-year vision? (§16)
  - What is the Research Philosophy? (§1 stop condition +
    anti-patterns)
  - What is the Context-Kit boundary? (§2 ownership +
    drift-prevention model + do-not-duplicate list)
- **Dependencies.** `DOMAIN_RESEARCH_PLAYBOOK.md` v2 (§1.11 —
  the research-class specialization the OS calls), all §1.1-
  §1.13 research library entries (context for what the OS
  governs), `docs/PLATFORM_INVENTORY.md`, `docs/PLATFORM_WHAT_IT_IS.md`,
  `docs/00-START-HERE/DOC_LIFECYCLE.md` §2c, `docs/EMPLOYEE_OS_PRIMITIVES.md`,
  Context-Kit skill + `docs/docs-pattern/`.
- **Recommended next reads.** For anyone opening a new session
  in this repo: bootstrap Level A (§4.1) is the answer. For
  understanding *how* the OS integrates: §2 Context-Kit
  Integration + §7 Documentation Authority. For starting
  research work: §5 router → §8.1 RESEARCH contract → §1.11
  playbook.
- **Overall importance.** **Foundational — the highest-
  authority process doc in the library.** The playbook
  (§1.11) is one specialization of this OS. Reading order
  for a fresh Claude Code: (1) `CLAUDE.md` — session
  instructions; (2) OS §0-§5 — orientation + routing; (3)
  Level B contract per §5 classification. This doc supersedes
  no prior work; it consolidates and formalizes the process
  discipline that emerged across S1268-S1276.
- **Rigby SIGN history.** Three cycles across S1277-S1278:
  (1) v1 draft → v1.1 SIGN-with-edits (Medium confidence,
  fresh pin `pa-95ce3cbf0a2aa0cc`, 15 must-fixes folded on
  bootstrap/router/authority/contracts/templates); (2) v2
  extension → v2 SIGN-with-edits (Medium confidence, fresh
  pin `pa-117d3edf9d7b80f8`, 12 must-fixes folded on the six
  new parts); (3) v2.1 finalization → High-confidence
  SIGN-with-edits (fresh pin `pa-30278fb65295e74c`, zero
  factual errors, edits = docs-only follow-up items already
  flagged as P0 non-blocking).
- **Distinguishing property.** This is `authority: process`
  with `version: v2.1`. Governance-tier — every future
  Claude Code session executes it. Playbook (§1.11) is a
  specialization; OS is the entry point.

### 1.15 `claude_research_startup_introspection.md`

- **Title.** Claude Code Startup + Research Execution
  Introspection — S1276 meta-research
- **Purpose.** Evidence base for the OS (§1.14). Documents
  Claude Code's *actual* startup behavior (from S1276 open
  self-observation), grep audits of CLAUDE.md + START-HERE +
  playbook + INDEX showing what fresh Claude cannot discover
  today, and P0/P1/P2 recommendations that seeded the OS
  design.
- **Status.** Active (companion evidence to §1.14).
- **Research type.** Process Introspection / Startup Audit /
  Failure Mode Catalog.
- **Primary questions answered.**
  - What does Claude Code actually do at session open today?
  - What is mandated vs learned vs manual vs prompt-dependent?
  - What is discoverable from CLAUDE.md alone (short answer:
    not much)?
  - What are the recent failure modes (wrong pin, S1273/S1274
    numbering collision, handoff drift, domain ambiguity, RAG
    provenance filter, multi-Claude session risk)?
  - What P0/P1/P2 documentation changes would extinguish each
    failure mode?
- **Dependencies.** `CLAUDE.md`, `00-START-NEXT-SESSION.md`,
  `docs/00-START-HERE/`, `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`,
  `docs/research/ARCHITECTURE_INDEX.md`, MEMORY.md
  auto-loaded feedback rules, `.claude/skills/context-kit/SKILL.md`.
- **Recommended next reads.** Chris directive at S1276 close:
  read Parts 1 + 4 for accuracy verification. The full Part
  6 recommendations became the P0 items in OS §17.1 + §20.9.
- **Overall importance.** **Foundational for understanding
  the OS's design rationale.** Not read at every session
  bootstrap (OS §1.14 replaces it as the operational doc),
  but the evidence base for OS §8 discoverability audit + §20
  fresh-Claude confusion assessment. Chris directive:
  *"you don't need Rigby this should be for how you work with
  the repo"* — the doc introspects Claude's repo-interaction
  discipline, not architectural findings.
- **Distinguishing property.** `authority: process-audit` —
  Claude self-report, not architectural finding. Not routed
  to Rigby per S1276 close directive.

### 1.16 `domains/memory/1301_memory_rag_retrieval_lanes_audit.md`

- **Title.** S1301 Memory RAG Retrieval Lanes — Category D
  Architecture Audit
- **Purpose.** First child audit under Research Group 1300
  Memory (parent §1.13). Scopes exclusively to Category D
  (RAG / Document Retrieval) per parent §3D + §5D + §6.
  Traces the parent §6 provenance-filter finding
  (`search_docs` 8 pre-filter → 7 `excluded_missing_provenance`
  + 1 `excluded_mismatch` → 0 returned) to root cause and
  answers the 28 canonical playbook questions for Category D.
- **Status.** Draft → Active (Rigby SIGN-clean, cycle 1, fresh
  isolation pin `pa-a23736a833f646cf`, 2026-07-01). Chris
  commit-gate flips to active on merge per playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Which lane runs which PA tool? `search_docs` = LOCAL
    keyword (`core.rag.top_k` on `.rag/corpus.jsonl`);
    `kb_tool semantic_search` = PROD pgvector
    (`core.rag_integration.search_embeddings`). Verified at
    `core/services/td_handlers_ops.py:5502`.
  - What drives `excluded_missing_provenance`? External
    `docs/_provenance.json` index (git-history-derived by
    `build_docs_provenance`) with 464 UNKNOWN entries out of
    2156 total (~21.5%); `_filter_chunks_by_originating_session`
    treats "path not in index" as exclusion by design
    (`td_handlers_ops.py:78-127`).
  - Does the prod lane bypass the filter? Yes — the filter
    is local-lane-only. `kb_tool semantic_search` and the
    prod `search_embeddings` path never call
    `_filter_chunks_by_originating_session`.
  - Do the row-level `DocumentEmbedding.source_type` /
    `ingested_via` fields participate in retrieval? No — grep
    receipts: 0 hits in `core/rag_integration.py`,
    `core/rag.py`, `core/services/scoped_retrieval.py`. Two
    provenance systems coexist without a bridge.
  - Is there a two-lane runtime selector? No — never
    implemented. `search_docs` hardcoded to local lane;
    `kb_tool` hardcoded to prod lane.
  - Does PA turn enrichment auto-invoke RAG? No — grep of
    `unified_pa_entrypoint.py` finds zero RAG imports.
    Tool-call-only.
- **Dependencies.** `1300_memory_domain_scoping.md`
  (parent — Categories A–H taxonomy + §6 anchor finding);
  `platform_architecture_inventory.md` §3.13 / §3.14 / §3.15
  / §5.4 (S1273 cited for 13 of 28 canonical questions
  already answered — this audit cites rather than
  re-answers); `cross_domain_integration_audit.md` (S1274
  §2.5 STRONG classification for PA + Agent RAG paths).
- **Recommended next reads.** Once this lands, next Group
  1300 child is S1302 Memory Persistence Architecture
  (Categories A + B + C — this audit surfaces the row-level
  provenance semantics question as a persistence concern
  belonging in S1302). Cross-arc follow-on: Group 1700
  Observability owns filter-drop telemetry per §14.2.
- **Overall importance.** **The audit that made the two-lane
  split visible.** Prior to S1301, tool descriptions
  implied `search_docs` and `kb_tool` were parallel
  implementations; the audit shows they run entirely
  different lanes with entirely different corpus surfaces
  and entirely different provenance semantics.
  Subsystem maturity verdict WORKING (dropped from STABLE
  in the parent scope) captures the corpus-completeness gap
  that neither individual-lane verdict conveys.
- **Distinguishing property.** First child audit of the
  library — validates playbook §11.2 template + §13
  6-parallel-Explore sub-agent sweep. Rigby SIGN independently
  grep-verified 8 numbered load-bearing claims across
  mechanism, filter design, prod-lane bypass, denominator
  quantities, row-level vs external provenance systems,
  MISSING inbound consumers, PA enrichment path, and
  silent-failure surface. All 8 CONFIRMED after SIGN cycle 1
  fold. Verifier-loop history preserved append-only per
  playbook §6.

---

### 1.17 `domains/memory/1302_memory_persistence_architecture_audit.md`

- **Title.** S1302 Memory Persistence Architecture —
  Categories A + B + C Architecture Audit
- **Purpose.** Second child audit under Research Group 1300
  Memory (parent §1.13). Combined scope of Categories A +
  B + C (Semantic Knowledge / Personal-Adaptive / Agent
  Working Memory) per parent §5 P2 slot. Answers the
  persistence-architecture question renamed by Chris
  2026-07-01 from "Store Overlap Audit": *where does what
  memory live, with what durability, on what write/read
  paths, and where is write authority enforced?*
- **Status.** Draft → Active (Rigby SIGN-clean, cycle 3, same
  fresh isolation pin `pa-1b9f0f5264484c6b` across all three
  fold cycles, 2026-07-01). Chris commit-gate flips to active
  on merge per playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Where does what memory live? Cat A `AgentKnowledgeSource`
    (`core/models_unified_system.py:521`) is Postgres-durable
    per-agent; Cat B splits across durable
    `UserAgentLearning` (`:3912`) + durable pgvector
    `ConversationMemory` (`core/models/conversations/models.py:19`)
    + Redis-only per-user preferences (`AgentLearningService`
    at `core/services/agent_learning_service.py:122`); Cat C
    `AgentMemory` (`:10787`) is Postgres-durable per-agent,
    with Redis-cached embedding side.
  - What's the write authority model? Unrestricted at the
    model layer for all three categories. Per-user isolation
    for Cat B is schema-only (FK), not query-time enforced.
    Cat C `AgentMemory.create_memory` at :11004 has no user
    FK, no rate limiting, no gate — `MemoryPromotionService`
    auto-saves on every PA turn. T10 HIGH severity.
  - Does the row-level "orphan write path" pattern from
    S1301 §14.3 D3 recur? Yes, but narrower than v1 claimed
    (Rigby SIGN cycles 1 + 2 + 3 grep-tightened). Final
    classification: 5 strict-orphan fields
    (`AgentKnowledgeSource.feedback_positive` +
    `.feedback_negative`; `UserAgentLearning.context_metadata`
    + `.last_used`; `ConversationMemory.intent` Django model)
    + 2 narrow-consumer-safety-filter fields
    (`AgentMemory.poison_risk_score` +
    `.poison_risk_factors` — consumed for safety exclusion
    only at `core/services/memory_embedding_service.py:222,
    :261`). 7 total under F2 pattern, down from v1's ~11.
  - Is `spider_context['pa_content_feedback']` consumer
    UNKNOWN as parent §3 flagged? **No — it is CONFIRMED DEAD
    CODE.** Whole-tree grep across `core/` + `ai_core/`: 1
    producer at `core/agent_router.py:766`; 0 code
    consumers. F1 headline finding.
  - Is the 14-day freshness window a magic number? Yes —
    `core/conversation_orchestrator.py:749` verbatim
    `freshness_cutoff = tz.now() - timedelta(days=14)`;
    hardcoded, no env var / setting; Session 988 origin per
    :747-748 comment.
  - Is `AgentLearningService` Redis state recoverable on
    worker recycle? No — `save_memory` at
    `core/services/agent_learning_service.py:462-483` writes
    `redis_client.hset` at :476 with no DB backup; grep for
    `.expire()`/`.setex()` = 0 hits.
  - Does `spider_data_bridge` write Cat A (naming implies)
    or Cat B (code reveals)? **Cat B.** Bridge at
    `core/learning_bridges/spider_data_bridge.py:240` calls
    `UserAgentLearning.objects.get_or_create(...)`. F5
    docs_stale.
  - Does `MemoryPromotionService` write `AgentMemory` (Cat C
    per parent §3) or `UserMemoryContext` (user-scoped)?
    **UserMemoryContext.** `core/services/memory_promotion_service.py:303-318`
    calls `UserMemoryContext.objects.create(...)`. F6
    category-assignment drift.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent —
  Categories A–H taxonomy + parent §3 known-drift bullets);
  `1301_memory_rag_retrieval_lanes_audit.md` (sibling Cat D
  audit — S1301 §14.3 D3 row-level orphan-write pattern
  inherited as first-order S1302 scope; §17.1 + §17.2 cited
  as authoritative resolutions, not re-answered);
  `platform_architecture_inventory.md` §3.13 + §5.4 (S1273
  overlap flag that motivated Group 1300);
  `cross_domain_integration_audit.md` (S1274 integration
  lens).
- **Recommended next reads.** Once this lands, next Group
  1300 child is S1303 Conversational / Thread Memory (Cat F)
  — will own the `ConversationSession` ↔ `ConversationMemory`
  boundary that S1302 documents as adjacent surface. S1304
  Docs Corpus ↔ RAG Boundary (E ↔ D) follows. Cross-arc
  follow-on: Group 1700 Observability owns dead-code /
  producer-only detection (F1 is highest-severity example);
  future design-preparation ADR (post-S1399) proposes the
  write-authority framework §18 surfaces but does not
  implement.
- **Overall importance.** **The audit that made the
  write-authority gap visible + escalated the pa_content_feedback
  loop from UNKNOWN to dead code.** The persistence-architecture
  rename by Chris 2026-07-01 made §18 (Ownership Gaps —
  authority framework) the audit's headline lens; every
  category has unrestricted model-layer writes, and Cat C
  auto-saves on every PA turn without rate limiting. Combined
  with F1's confirmed producer-only feedback loop and F2's
  narrower-but-real orphan-write pattern, the audit
  establishes that the Memory subsystem's biggest architectural
  risk is not overlap surfacing — it is the absence of a write
  authority framework.
- **Distinguishing property.** **Second child audit of the
  library; validates the fold discipline across THREE Rigby
  SIGN cycles on the same fresh isolation pin.** Cycle 1 folded
  F2 overstatement + verified F6 by parent-agent direct-read;
  cycle 2 folded AgentMemory field misclassification via
  Memory Palace consumer evidence + methodology tightening
  ("no explicit-qualified references found" replaces
  "0 consumers"); cycle 3 folded final poison_risk_*
  reclassification to narrow-consumer-safety-filter. Verifier-loop
  history preserved append-only per playbook §6. Total
  F2 orphan field count: ~11 (v1) → ~9 (cycle 1) → ~6 (cycle
  2) → 5 strict + 2 narrow-consumer (cycle 3 final). Pattern
  class stands; scope is significantly narrower than v1
  claimed. Overall confidence: High.

---

### 1.18 `domains/memory/1303_memory_conversational_thread_memory_audit.md`

- **Title.** S1303 Memory Conversational / Thread Memory —
  Category F Architecture Audit
- **Purpose.** Third child audit under Research Group 1300
  Memory (parent §1.13). Category F Conversational / Thread
  Memory exclusive scope per parent §5 P3 slot.
  **First-inventory landing** — Cat F had no
  `platform_architecture_inventory.md` §3.N row at audit open;
  this audit produces the terrain (§4 Major Models + §7
  Runtime Flows load-bearing sections). Answers: where does
  session pin identity live, how does turn history reinject
  across worker recycling, what is the retire lifecycle
  contract, and where does Cat F touch the 12 adjacent
  domains?
- **Status.** Draft → Active (Rigby SIGN-clean, cycles 1 + 2
  complete on fresh isolation pin `pa-23a38300dd84bae2`,
  2026-07-01). Chris commit-gate flips to active on merge per
  playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Where does session pin identity live? `ChatConversation`
    at `core/models/conversations/models.py:59-187` is the
    row-per-exchange table; `conversation_id` CharField (line
    76) stores the `pa-<uuid.hex[:16]>` pin (mint format at
    `td_handlers_core.py:3885`); `session_active` BooleanField
    (line 139-143) is the retire marker.
  - How does turn history reinject across Celery worker
    recycles? `_load_conversation_history_from_db()` at
    `unified_pa_entrypoint.py:7277-7343` loads the last 10
    ChatConversation rows scoped to `conversation_id`
    (7300-7302), chronologically ordered (7309), with 8000-
    char assistant-response truncation (7327, post-S1085
    bump), tool-call metadata (`tool_calls` / `tool_results`
    / `response_id`) reinjected at 7331-7336, fail-open on DB
    error at 7342.
  - Is `session_tool.retire` present + working? **YES.**
    Handler at `td_handlers_core.py:4011-4072`; requires
    `force=True` if retiring currently-bound thread (line
    4035-4050); returns `{retired: True, updated_count}` on
    success (line 4061); idempotent (`.filter(session_active=
    True).update(...)` returns 0 rows on double-retire).
    Memory rule `feedback_session_tool_retire_works.md`
    stands.
  - Was the S1212 stale-thread dispatcher waste (deliverable
    777d9cd8, ~$3.60/day) reconciled? **YES.** S1248 shipped
    matched-pair fix: retire handler flips `session_active=
    False`; dispatcher gate at `conversation_action_
    dispatcher.py:288-316` blocks. Enforcement is best-effort
    / fail-open under DB errors (line 317-323 `try/except`
    envelope) — availability > correctness by design.
  - Where is the Cat B / Cat F name-collision boundary
    (S1302 §17.3)? Django `ConversationMemory` at
    `models/conversations/models.py:19` = Cat B (S1302-
    owned); in-process `ConversationMemory` facade at
    `conversation_memory.py:59` = Cat F. Consumer imports
    split cleanly by pattern A (Cat B model) vs B (Cat F
    facade singleton). One WRONG import at
    `content_writer_agent.py:76` — see F3 below.
  - Are `ChatConversation.context_used` +
    `.agent_results` dead code? **CANDIDATE, NOT YET PROVEN
    EITHER WAY.** Rigby SIGN cycle 1 confirmed the raw-
    keyword grep catches unrelated variables (e.g.,
    `tasks_agents.py:1262` `agent_results = phase_data.get(
    'results', {})` is a local dict in different scope). Per
    memory rule `feedback_verify_before_deleting_dead_code.md`,
    dead-code verdict requires owner-model-qualified consumer
    inventory (§19 R1.a) + runtime/analytics/UI classification
    (R1.b) + canonical source-of-truth resolution vs the
    `metadata` dict (R1.c) BEFORE any deletion PR.
  - Does turn context enrich RAG queries? **Observed gap;
    owner confirmation required.** No verified wiring found
    from Cat F turn-history reinjection to Cat D retrieval
    query augmentation (0 RAG imports in
    `unified_pa_entrypoint.py`). Could be intentional
    separation (thread memory user-scoped; corpus source-
    scoped) or missing integration. §19 R3 delegates to S1304
    (Cat E ↔ D boundary).
  - What auto-cleanup exists for retired rows? **NONE.** No
    Celery task, no management command, no TTL config found
    for `ChatConversation` cleanup. Retired rows accumulate
    indefinitely. §14 F9 + §19 R4.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent
  — Cat F systems named in §3F; parent §5 P3 rationale locks
  first-inventory discipline);
  `1301_memory_rag_retrieval_lanes_audit.md` (sibling Cat D
  — silent-failure class pattern adjacent to F7 EventBus
  gap; §19 downstream routing points at S1304 E↔D);
  `1302_memory_persistence_architecture_audit.md` (sibling
  Cat A+B+C — §17.3 name-collision resolution is
  load-bearing input; §14.3 F1 dead-code detection
  methodology applied as F4-CANDIDATE, not F4-CONFIRMED, per
  verifier discipline); `platform_architecture_inventory.md`
  (S1273 — Cat F has NO §3.N row today; audit produces the
  candidate row for S1399 canonical summary landing);
  `cross_domain_integration_audit.md` (S1274 integration
  lens; 12 Cat F domain pairs mapped).
- **Recommended next reads.** Once this lands, next Group
  1300 child is S1304 Documentation Corpus ↔ RAG Boundary
  (Categories E ↔ D) — inherits provenance-boundary
  questions from S1301 + S1302 and receives §19 R3 (turn-
  context → RAG enrichment design). S1305 Runtime Memory
  Correctness (Cat H narrow scope — Redis-loss + lru
  staleness) follows. S1399 canonical summary owns first-
  inventory row landing for Cat F (§19 R5).
- **Overall importance.** **The audit that documented the
  Cat F terrain for the first time + reconciled the stale-
  thread waste anchor + surfaced F4-CANDIDATE discipline as
  a repeatable methodology guard.** ConversationSession +
  turn-history reinject + retire lifecycle now have file:line
  cites and step-by-step runtime flows for the first time in
  the library. F3 wrong-model+wrong-field finding at
  `content_writer_agent.py:370` (Django `ConversationMemory`
  has no `memory_type` field) is a live drift class not
  previously named. F4-CANDIDATE discipline (verifier
  downgrade from Agent-6's "dead code" claim to "not yet
  proven either way") extends S1302's dead-code methodology
  by adding the owner-model qualification rule — future
  audits that apply this pattern must not accept keyword-
  grep evidence for dead-code claims.
- **Distinguishing property.** **First-inventory audit in
  the library** — no prior §3.N row existed for Cat F;
  §4 Major Models + §7 Runtime Flows are load-bearing (not
  just referential). Also: **only child audit to reach SIGN-
  clean in 2 cycles** (S1301 = 1 cycle, S1302 = 3 cycles) —
  verifier-loop spot-checks caught Agent-6's two overreaches
  (F3 "would fail at import time" → SOFT FAIL soft-guarded;
  F4 "confirmed dead code" → CANDIDATE) before shipping to
  Rigby, so cycle 1 only needed to fold the substantive
  edges (metadata contract, D1 widen, Cat F ↔ Cat D
  reframe, maturity bounding, R1 split into R1.a/b/c) rather
  than correct evidence overreach. Cycle 2 was a pure
  verification pass; Rigby confirmed E3/E4/E5 held via
  direct code reads and closed SIGN-clean. Verifier-loop
  history preserved append-only per playbook §6.

---

### 1.19 `domains/memory/1304_memory_docs_rag_boundary_audit.md`

- **Title.** S1304 Memory Documentation Corpus ↔ RAG Boundary
  — Categories E ↔ D Integration Audit
- **Purpose.** Fourth child audit under Research Group 1300
  Memory (parent §1.13). Categories E (Documentation / Research
  Knowledge System — S1273 §3.15) ↔ D (RAG / Document Loading —
  S1273 §3.14 + S1301 P1 audit) exclusive **boundary lens** per
  parent §5 P4 slot. Smaller scope than P1-P3 per parent
  rationale ("smaller scope; benefits from §3.14 audit landing
  first"). Answers: how does docs corpus become RAG-visible,
  where does ingestion hand off to retrieval, where do the two
  provenance systems (external `_provenance.json` vs row-level
  `DocumentEmbedding.source_type` + `ingested_via`) disagree,
  and what routes read which?
- **Status.** Draft → Active (Rigby SIGN-clean, cycles 1 + 2
  complete on fresh isolation pin `pa-2614a91a920642fa`,
  2026-07-01). Chris commit-gate flips to active on merge per
  playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - Is S1301 §19 D3 "row-level provenance never read"
    hypothesis correct? **PARTIALLY INVALIDATED via S1304
    verifier-loop.** `DocumentEmbedding.source_type` HAS an
    owner-model-qualified consumer at
    `content/embeddings.py:965-973` (`semantic_search_sync`
    applies `.filter(source_type__in=['internal',
    'user_upload'])` at :971 and
    `.filter(source_type__in=['web', 'spider', 'api'])` at
    :973 as `source_filter` branch) + presentation at :1007
    (`getattr(embedding, 'source_type', 'unknown')`). Only
    `ingested_via` remains F1-CANDIDATE orphan — all 3
    write-sites use fixed string constants
    (`'sync_docs'` / `'backfill'` / `'unknown'`) with zero
    owner-model-qualified read consumers. F1-CANDIDATE
    verdict per S1303 §14 F4-CANDIDATE discipline (requires
    §19 R1 full-tree recheck before dead-code declaration).
  - Is `build_docs_provenance` beat-scheduled? **NO.** The
    sole `refresh-docs-corpus-daily` beat entry at
    `core/celery.py:495-499` runs `refresh_docs_corpus`
    daily at 04:00 Denver, which calls
    `build_docs_index` (`:5900`), `build_rag_corpus`
    (`:5901`), and `sync_docs_index_to_documents` (`:5902`)
    — but never `build_docs_provenance`. Provenance index
    rebuild is manual-only. Combined with the `lru_cache(1)`
    invalidation gap at `td_handlers_ops.py:78-93`, this is
    the canonical E→D write-side/read-side sync drift
    (§14 D2 + D6, both HIGH severity).
  - Who owns the E↔D boundary? **Cascade steps 1-4 owned by
    Documentation Manager `AIEmployee` handle at
    `core/employees/jobs.py:187-395` (registered `:1336` as
    `docs_manager`, employee_handle=`rigby`, `mission_run_
    kind="docs_cascade"`).** The four specific boundary-
    maintenance responsibilities (provenance rebuild
    cadence, cache invalidation strategy, filter counter
    observability, row-level `ingested_via` consumer
    strategy) have **no explicit named runtime owner** —
    Cat D + Cat E have implicit maintainers, but no
    `JobContract` binds boundary-maintenance
    responsibilities. Bounded language per playbook §12:
    "no explicit named runtime ownership" replaces the
    initial "UNOWNED" blanket verdict (fold #2 per Rigby
    SIGN cycle 1).
  - Is turn-context → RAG enrichment intentional separation
    or drift (S1303 §19 R3)? **NOT RESOLVABLE FROM STATIC
    EVIDENCE.** Three signals tilt intentional-separation
    (design discipline in 8 non-RAG enrichment services,
    tool-call-only pattern with two first-class PA tools,
    thread-memory vs source-memory scope discipline,
    no event-driven turn-signal wiring), three signals
    tilt drift (no design comment, no feature flag guarding
    absence, asymmetry with BaseAgent's
    `_get_relevant_knowledge_for_task`). Routed to §19 R5
    as design-decision hypothesis for
    design-preparation phase, NOT drift or wiring PR. R5.a
    (canonicalize separation) vs R5.b (implement enrichment)
    require product/architecture verdict on operational
    cost, migration risk, and future retrieval requirements.
  - Are the two provenance systems duplicates? **No —
    complementary, not redundant** (applied S1302 §17.3
    name-collision-as-methodology). External JSON encodes
    session origin (LOCAL keyword lane); row-level
    `source_type` encodes source-of-record enum (PROD
    pgvector lane); `ingested_via` was over-designed for a
    retrieval consumer that never materialized. Fold #4 per
    Rigby SIGN cycle 1: "complementary today does not imply
    optimal" guardrail added — unification vs explicit
    scoping is an open design decision routed to §19 R2.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent
  — Cat E + Cat D systems named in §3E + §3D; parent §5 P4
  rationale locks boundary-lens discipline);
  `1301_memory_rag_retrieval_lanes_audit.md` (sibling Cat D
  — §14.2 21.5% coverage gap + §19 downstream routing
  including row-level orphan-write pattern that S1304
  partially invalidates);
  `1302_memory_persistence_architecture_audit.md` (sibling
  Cat A+B+C — §17.3 name-collision resolution methodology
  applied to the two-provenance-system reframe);
  `1303_memory_conversational_thread_memory_audit.md`
  (sibling Cat F — §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3
  turn-context → RAG enrichment hypothesis + §14
  F4-CANDIDATE discipline enforced on
  `ingested_via` orphan claim);
  `platform_architecture_inventory.md` (S1273 §3.14 + §3.15
  + §5.4 overlap flag); `cross_domain_integration_audit.md`
  (S1274 §2.5 baseline for §9 comparison);
  `DOC_LIFECYCLE.md` (§2c inventory-wins-on-conflict rule
  as governance authority for the boundary);
  `docs/topics/local-askdocs.md` (S1108 CANONICAL boundary-
  disambiguating topic doc); `SESSION_1142` handoff
  (ingestion-moment snapshot 852 → 14,149 chunks).
- **Recommended next reads.** Once this lands, next Group
  1300 child is **S1305 Runtime Memory Correctness (Cat H
  narrow scope — Redis-loss + lru staleness)** per parent
  §5 P5 slot. Then S1399 canonical summary — owns first-
  inventory row landing for Cat F (§19 R5 inherited from
  S1303) + row-level orphan-write pattern classification
  (§19 R1 F1-CANDIDATE verification of `ingested_via`) +
  write-authority framework anchor recommendation
  (inherited from S1302 T10) + provenance-system
  reconciliation design proposal (§19 R2) + boundary-owner
  assignment (§19 R4). Follow-on delegations: R5 turn-
  context → RAG enrichment design → design-preparation
  phase post-S1399; R7 filter-drop telemetry → Group 1700
  Observability arc.
- **Overall importance.** **The audit that mapped the E↔D
  boundary integration for the first time + partially
  invalidated S1301 §19 D3 hypothesis via verifier-loop
  before it propagated to sibling audits + refined "boundary
  UNOWNED" to bounded ownership matrix + routed Cat F ↔ Cat
  D turn-context enrichment to design-decision phase.** The
  4-step ingestion cascade, provenance materialization,
  retrieval-side `lru_cache(1)` staleness gap, and
  boundary-maintenance ownership gaps now have file:line
  cites and mechanism-level explanations for the first time
  in the library. S1301 §19 D3 partial-invalidation
  demonstrates the verifier-loop pattern preventing sibling-
  audit hypothesis propagation before it hardens into
  library-wide false consensus.
- **Distinguishing property.** **First boundary-lens audit
  in the library** — scope is deliberately smaller than
  P1-P3 per parent §5 P4 rationale; audit is integration-
  focused, not re-audit of either category internals. Also:
  **only second child audit to reach SIGN-clean in 2 cycles**
  (S1301 = 1 cycle, S1302 = 3 cycles, S1303 = 2 cycles,
  S1304 = 2 cycles) — verifier-loop spot-checks caught the
  S1301 §19 D3 broad hypothesis invalidation before shipping
  to Rigby, so cycle 1 focused on substantive evidence
  additions (beat-schedule positive citation for D6,
  Documentation Manager ownership evidence for §18,
  F4-CANDIDATE hedge tightening for `ingested_via`,
  "complementary does not imply optimal" guardrail for
  §17). Cycle 2 was a pure verification pass; Rigby
  confirmed all 4 folds independently via direct code reads
  and closed SIGN-clean. Rigby-caught bonus at
  `content/embeddings.py:904` (async-path SearchResult
  presentation citation) flagged as nice-to-have, not
  SIGN-blocking. Verifier-loop history preserved
  append-only per playbook §6.

### 1.20 `domains/memory/1305_memory_runtime_correctness_audit.md`

- **Title.** S1305 Memory — Runtime Memory Correctness
  (Category H) Architecture Audit
- **Purpose.** **Fifth (and final child) audit under Research
  Group 1300 Memory (parent §1.13).** Category H Runtime Memory
  Correctness NARROW scope per parent §5 P5 slot — Redis-loss on
  worker recycle + `@lru_cache(1)` staleness drift class only.
  Explicitly OUT: system RAM, macOS SIGSEGV, Celery worker RSS,
  PID cache, ops-flavored infrastructure. Explicitly OUT: Cat A/
  B/C/D/E/F/G internals (owned by sibling audits — MAY be cited
  as adjacent evidence but NOT re-audited). Answers: where does
  the runtime model assume persistence that Redis / `@lru_cache`
  doesn't guarantee, and where does staleness silently ship
  wrong results?
- **Status.** Draft → Active (Rigby SIGN-clean, cycles 1 + 2
  complete on fresh isolation pin `pa-56a527a2c5528508` retired
  at close, 2026-07-01). Chris commit-gate flips to active on
  merge per playbook §16.
- **Research type.** Child audit (playbook §11.2 20-section
  template). `authority: research`.
- **Primary questions answered.**
  - How many `@lru_cache(maxsize=1)` sites in `core/services/`?
    **Exactly 4** grep-verified 2026-07-01: `_load_provenance_docs`
    at `td_handlers_ops.py:78` (S1304 D2 anchor);
    `_cached_primary_workspace_id` at `platform_config.py:89`;
    `_cached_primary_user_id` at `platform_config.py:133`;
    `_load_config` at `fleet_routing.py:64`. Only
    `platform_config` pair has an explicit invalidation contract
    (`clear_config_cache()` at :223); the other two rely on
    worker-restart discipline.
  - How many production `cache.set(..., timeout=None)` sites?
    **5** within scope after Rigby SIGN cycle 1 tightening
    (`core/` runtime excl. tests + subprocess-timeouts + archive
    + mock fallbacks): `core/tasks.py:5936`, `core/memory_system.py:54`,
    `:55`, `:176`, `core/services/discord_bot.py:9723,9728`.
    Full 11-file repo grep enumerated with 6 excluded-category
    justifications at §3 excluded-from-count table.
  - Is `AgentLearningService` durability actually CRITICAL as
    Agent 6 sweep claimed? **No — verifier-loop downgraded to
    MEDIUM.** Redis AOF at `settings.py:944 REDIS_APPENDONLY=True`
    + `REDIS_APPENDFSYNC='everysec'` at :945 preserves state
    across Redis restart; loss on Python-worker recycle is only
    the in-memory `_user_memories` buffer delta between last
    `save_memory()` and recycle, matching S1302 T3 sibling
    classification.
  - What is the within-process consistency gap in
    `AgentLearningService`? **CONFIRMED via direct file:line read
    + Rigby SIGN cycle 1 reinforcement.** `get_user_memory` at
    `agent_learning_service.py:415` short-circuits to
    `_user_memories[key]` BEFORE Redis on hit; `save_memory` at
    `:476` writes Redis via `hset` but never touches the dict.
    Grep across full file for `self._user_memories.clear` /
    `del self._user_memories` = 0 hits. Distinct from S1302 T3
    (cross-process recycle-loss). §14 D4 S1305-new.
  - Is `MemoryPromotionService` a Cat H surface? **NO** — Agent 2
    + verifier-loop confirmed pure DB I/O; no `@lru_cache`,
    `@cached_property`, or module-level memoization. Closes
    parent §3H open question.
  - Is `MemorySystem` at `core/memory_system.py` actively used?
    **YES** — Rigby SIGN cycle 1 grep found 9 files reference
    `MemorySystem(` or the `SharedMemorySystem` / `AIMemorySystem`
    cousins; direct instantiation confirmed at
    `ai_core/agents/intelligent_job_matcher.py:57`. §14 D5:
    unbounded `timeout=None` at `:54, :55, :176` creates index
    → data divergence risk under Redis LRU eviction
    (`REDIS_MAXMEMORY_POLICY='allkeys-lru'` at `settings.py:942`).
  - Is the Redis DB topology what documentation claims? **NO —
    4 DBs, not 3** as `docs/topics/infrastructure.md` says.
    Confirmed: DB 1 (Django cache `settings.py:448-453`), DB 2
    (Celery broker `:802`), DB 3 (Celery results `:803`), DB 5
    (`AgentLearningService` hardcoded at
    `agent_learning_service.py:145`). **Consequence:**
    `django.core.cache.cache.clear()` operates on backend at DB 1
    only; `AgentLearningService` uses raw `redis.Redis(**config)`
    at `:160` bypassing Django cache framework — DB 5 state is
    invisible to `cache.clear()`. §14 D8 + D9.
- **Dependencies.** `1300_memory_domain_scoping.md` (parent —
  §3H narrow scope defined + §5 P5 slot rationale + §7 anti-scope
  boundary); `1301_memory_rag_retrieval_lanes_audit.md` (sibling
  Cat D — §14 D1/D2 LRU staleness anchor);
  `1302_memory_persistence_architecture_audit.md` (sibling Cat A+B+C
  — §14 F4/F5 + §15 T3/T4 Redis-only durability anchor + AOF
  context); `1303_memory_conversational_thread_memory_audit.md`
  (sibling Cat F — §14 F4-CANDIDATE discipline applied to
  `platform_config` LRU F4-CANDIDATE claim);
  `1304_memory_docs_rag_boundary_audit.md` (sibling Cat E↔D —
  §14 D2/D6 canonical E→D synchronization gap + §15 T2 remediation
  option set inheritance + §18 ownership gap pattern extension);
  `platform_architecture_inventory.md` (S1273 §3.13 drift bullets
  reference Redis-only state + `lru_cache(1)` per-process).
- **Recommended next reads.** Group 1300 has now closed all 5
  child audits; **next is S1399 Canonical Summary** per parent
  §5 P6 slot. S1399 consumes S1301-S1305 outputs and produces:
  (a) consolidated memory-subsystem shape map across all 6 in-
  scope categories (A/B/C/D/E/F; G delegated), (b) cross-cutting
  patterns discovered across children (F1 provenance-filter drift
  class, F2 row-level orphan-write pattern, F3 Redis-only
  durability + `@lru_cache` staleness pattern, F4 F1-CANDIDATE
  discipline as methodology), (c) `PLATFORM_INVENTORY.md` §3
  update recommendations (§3.13 subdivision from S1302; §3.14 lane
  consolidation from S1301; new §3.N row for Cat F from S1303; new
  §3.N or §5 row for Cat H from S1305), (d) follow-on research
  queue (S1305 §19 R1 IntelligentJobMatcher production invocation;
  S1304 §19 R1 `ingested_via` full-tree recheck; S1303 §19 R1.a/b/c
  F4-CANDIDATE verification; S1302 T10 write-authority framework
  design), (e) cross-link to Employee OS 1200s Cat G Mission Memory
  arc. S1399 is bounded work (one session per playbook §11.3).
- **Overall importance.** **The audit that mapped the Cat H
  runtime-cache tier for the first time + established sibling-
  inherited severity discipline (Redis AOF context downgraded a
  CRITICAL claim to MEDIUM) + resolved 3 parent §3H open questions
  (search_docs cache location, MemoryPromotionService cache absence,
  MemorySystem active-use status).** 4 `@lru_cache` sites, 5
  production `cache.set(timeout=None)` sites, 4-DB Redis topology,
  Django cache framework vs raw redis client isolation, within-
  process consistency gap in AgentLearningService — all now have
  file:line cites and mechanism-level explanations. Second-in-a-
  row 2-cycle SIGN-clean pattern (matching S1303 + S1304
  discipline) reflects the audit landing with well-scoped
  verifier-loop pre-corrections + sibling-inheritance that let
  cycle 1 focus on substantive-scope edits rather than factual
  corrections.
- **Distinguishing property.** **Last child audit under Group
  1300; closes the 5-child arc** (S1301 Cat D + S1302 Cat A+B+C
  + S1303 Cat F + S1304 Cat E↔D + S1305 Cat H). Third child audit
  to reach SIGN-clean in 2 cycles (matching S1303 + S1304; S1301
  = 1, S1302 = 3). Also **first library audit to explicitly
  downgrade a sub-agent severity claim via sibling-inherited
  context** (Agent 6 "CRITICAL" → MEDIUM per Redis AOF at
  `settings.py:944`) — extends the verifier-loop pattern from
  hypothesis-correction (S1304 partial invalidation of S1301
  §19 D3) to severity-correction (§14 D3 downgrade). Rigby-caught
  bonus at MemorySystem active-use resolution shifted §19 R6
  from "verify MemorySystem is used" to "verify
  IntelligentJobMatcher is production-invoked" — same effort
  budget, higher-leverage question. Verifier-loop history
  preserved append-only per playbook §6.

---

### 1.21 `domains/memory/1399_memory_canonical_summary.md`

- **Title.** Group 1300 Memory / Knowledge / Embeddings —
  Canonical Summary
- **Purpose.** **Arc-closing `xx99` synthesis for Research Group
  1300** (Memory / Knowledge / Embeddings). Consumes the five
  child audit outputs (S1301 Cat D + S1302 Cat A+B+C + S1303 Cat
  F + S1304 Cat E↔D + S1305 Cat H) and produces the cross-
  cutting view that no single child could deliver: consolidated
  memory-subsystem shape map spanning Cat A/B/C/D/E/F (G
  delegated per parent §3G), recurring pattern classes named
  (F1-F4), resolved contradictions between siblings, anchor-
  update recommendations, ranked follow-on queue, and cross-
  links to delegated arcs.
- **Status.** Draft → Active (Rigby SIGN-clean cycle 1 on fresh
  isolation pin `pa-4fc3329d0db6484f`, High confidence, 0 must-
  fix, 1 optional nice-to-have re: docs↔code naming/category
  drift kept as §4.5 adjacent evidence). Chris commit-gate flips
  status → active on merge per playbook §16.
- **Research type.** Canonical summary (playbook §11.3 11-section
  template). `authority: research`, `category: canonical_summary`.
- **Primary questions answered.**
  - What are the cross-cutting patterns across all 5 child
    audits? **Four formal patterns named:** F1 provenance-
    filter drift class (S1301 §14.2 + S1304 §14 D2/D6 + S1305
    §14 D1); F2 row-level orphan-write pattern (S1301 §14.3 D3
    hypothesis + S1302 §14.3 F2 narrowed 11→7 fields + S1304
    §14 D3 partial invalidation); F3 Redis-only durability +
    `@lru_cache` staleness pattern (S1302 §14 F4 + §15 T3/T4 +
    S1304 §14 D2 + S1305 §14 D3/D4/D5/D8); F4 F1/F4-CANDIDATE
    discipline as inheritance methodology (S1303 §14 + S1304
    §14 D7 + S1305 §14 D6 + severity-correction extension at
    S1305 §14 D3). §4.5 adjacent-evidence addendum on docs↔code
    naming/category drift.
  - What contradictions between children required resolution?
    **Five resolved (§5):** (5.1) S1304 §14 D3 partial-invalidates
    S1301 §19 D3 broad `source_type` orphan hypothesis; (5.2)
    S1304 §17 "complementary" reframe of S1302 §17.3 "duplicate
    provenance systems"; (5.3) Agent 6 CRITICAL → MEDIUM
    severity downgrade via Redis AOF sibling context; (5.4)
    Agent 6 "13 cache.set(timeout=None)" → 5 production
    scope-tightened; (5.5) parent §3H bullet "search_docs LRU"
    → precision fix (cache is on `_load_provenance_docs`).
  - What anchor-update recommendations does the arc propose?
    **§7:** (a) `platform_architecture_inventory.md` §3.13
    subdivision into Cat A/B/C sub-rows (S1302); (b) §3.14 lane
    consolidation as explicit two-lane statement (S1301); (c)
    new §3.N row for Cat F Conversational/Thread Memory (S1303
    first-inventory landing); (d) new §3.N or §5.N row for Cat H
    Runtime Memory Correctness (S1305 first-inventory landing);
    (e) `docs/topics/infrastructure.md` Redis DB count 3 → 4
    (S1305 §14 D9); (f) `KNOWLEDGE_RAG_MEMORY.md` — resolve F1
    UNKNOWN + two-lane split explicit + LRU precision + pointer
    to this summary; (g) `ARCHITECTURE_INDEX.md` v17 → v18;
    (h) `docs/topics/docs-ingestion-cascade.md` NEW (S1304 §19
    R6). No direct edits to `PLATFORM_INVENTORY.md`
    (regenerable runtime anchor).
  - What's on the follow-on queue and how is it ranked? **21
    items ranked by uncertainty × risk × unblocked flows (§8.1).**
    Top 5: (1) S1304 §19 R1 `ingested_via` full-tree recheck
    (F1-CANDIDATE hardening); (2) S1303 §19 R1.a/b/c
    `ChatConversation.context_used` + `.agent_results`
    verification; (3) S1305 §19 R1 `platform_config` LRU
    F4-CANDIDATE mutation-path audit; (4) S1305 §19 R6
    `IntelligentJobMatcher` production invocation audit
    (routes T5 MemorySystem severity); (5) S1302 §15 T10
    write-authority framework design-preparation ADR (highest-
    severity debt in arc). Design-preparation items post-S1399:
    Cat H remediation per surface (S1305 §19 R2); Cat H ↔ Cat B
    integration lens (S1305 §19 R4 — fixes T3+T4+T7 together);
    provenance-system reconciliation (S1304 §19 R2); turn-context
    → RAG enrichment (S1304 §19 R5).
  - What delegated arcs receive handoffs? **§9:** Employee OS
    1200s arc (Cat G Mission Memory — parent §3G Chris-locked
    D2); Group 1700 Observability (4 aggregated items: Cat D
    filter-drop telemetry from S1301 R2, Cat E↔D filter-drop
    telemetry from S1304 R7, dead-code / producer-only detection
    from S1302, EventBus adoption for Cat F from S1303 R2,
    worker-recycle instrumentation for Cat H from S1305 R5);
    post-S1399 design-preparation phase (4 ADR/design-preparation
    docs); standalone bugfix follow-ups (S1303 R8 broken import,
    S1305 R8 doc-drift, S1304 R8 classifier bug).
- **Dependencies.**
  `1300_memory_domain_scoping.md` (parent — §5 P6 slot rationale
  + §3H open questions closed at S1305 close);
  `1301_memory_rag_retrieval_lanes_audit.md` (child P1);
  `1302_memory_persistence_architecture_audit.md` (child P2);
  `1303_memory_conversational_thread_memory_audit.md` (child P3);
  `1304_memory_docs_rag_boundary_audit.md` (child P4);
  `1305_memory_runtime_correctness_audit.md` (child P5). Also
  cross-links to `EMPLOYEE_OS_PRIMITIVES.md` (Cat G delegation
  target) and prospective Group 1700 Observability arc (multiple
  observability-flavored delegations).
- **Recommended next reads.** **Group 1300 is now closed** per
  playbook §17 graduation criteria. Next arc opens per
  `OPEN_ARCS.md` — default is **Group 1400 Revenue** (next in
  playbook §22 queue), pending Chris directive. Immediate P1
  follow-on missions (§8.2 of the summary) are eligible to open
  as single-child audits or new arcs; write-authority framework
  ADR (Rank 5) is design-preparation phase work post-arc-close.
- **Overall importance.** **The arc-closing xx99 that makes the
  entire Group 1300 arc navigable as a single memory-
  architecture picture.** Six sessions of research (S1300 parent
  + 5 children + this summary) collapse into: (a) a single Cat
  A-H matrix map any Staff Engineer can build a mental model
  from (§3); (b) four named cross-cutting pattern classes that
  now exist as vocabulary for future audits (F1-F4); (c) five
  resolved contradictions preventing sibling-audit hypothesis
  propagation into false library consensus; (d) 21 ranked
  follow-on items feeding future sessions; (e) 4 aggregated
  Group 1700 Observability delegations reducing that future
  arc's scoping cost. **First library `authority: research` +
  `category: canonical_summary` doc that follows playbook §11.3
  bounded-work discipline end-to-end.**
- **Distinguishing property.** **First formal xx99 canonical
  summary in the library** (the S1268-S1275 arc predated the
  xx99 convention per playbook §22 note). Consumes prior child
  outputs — no §13 6-parallel-Explore sweep, no new file:line
  evidence, no CANDIDATE → CONFIRMED resolutions. Every claim
  cites its source-audit §-anchor via `SNNNN §NN.N` notation.
  Rigby SIGN cycle 1 clean at High confidence — the audit
  contract's canonical-summary form works end-to-end. Chris's
  short command `start research group 1399` proved the reduced-
  prompt target rhythm from playbook §11 works for arc closure.
  Load-bearing methodology output: F4 F1/F4-CANDIDATE +
  severity-correction discipline codified as inheritance
  methodology — extends to playbook v3 candidate additions per
  §20 two-triggers rule (now used across S1303 + S1304 + S1305).
- **Post-close retrofit (2026-07-01 same day).** Chris directive
  after S1399 arc close: add §10 "What This Research Taught Us
  About How to Do Research" as a mandatory section in the playbook
  §11.3 canonical-summary template. S1399 retrofitted from 11
  sections to 12 sections as first application. Renumbering:
  former §10 Arc Change Log → §11; former §11 Appendix — Provenance
  → §12. Load-bearing methodology content previously at §10.4 moved
  into new §10.2 "What to codify into playbook v3" with two-triggers
  threshold status per pattern (3 patterns MET; 2 patterns Chris-
  ratified no-threshold). §11.4 preserved as backwards-compat
  pointer for external references to old §10.4 (OPEN_ARCS
  reconciliation notes; SESSION_1399 handoff `key_findings`).
  Playbook §11.3 template + rationale paragraph updated same-
  commit. Memory rules `feedback_xx99_meta_methodology_section.md`
  + `feedback_docs_cascade_at_every_close.md` saved. §12.6 arc
  close criteria checklist extended from 12 to 13 boxes (added
  "docs → RAG cascade executed post-merge"); all 13 ticked.
  Playbook §11.3 template becomes 12-section going forward — every
  future xx99 canonical summary includes §10 non-negotiably.

### 1.22 `domains/revenue/1400_revenue_domain_scoping.md`

- **Title.** Group 1400 Revenue / Outreach / Engagement — Parent Architecture Scoping (Phase 0)
- **Purpose.** **Arc-opening scoping deliverable for Research Group 1400** (Revenue / Outreach / Engagement — playbook §22 queue slot; S1273 §3.32 first-inventory row). Phase 0 domain-definition exercise per playbook §22 rule 3 (split large domains). First formal application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) at §10/§11/§12 — proposed as playbook v3 §11.1 template addition at parent §9.5 (D29 Chris-lock; two-triggers threshold promotion at Group 1500 close).
- **Status.** Active (Chris-locked D21+D23-D29 across three "agree all" ratification rounds 2026-07-01; Rigby Light SIGN cycles 1 + 2 both SIGN-clean at Medium and Medium-High confidence respectively; 0 must-fix after fold on both cycles).
- **Research type.** Parent scoping (playbook §11.1 template + Chris's Phase 0 methodology overlay). `authority: parent-doc`, `category: parent_scoping`.
- **Primary questions answered.**
  - Should Group 1400 be a single audit or a parent-with-children structure? **Parent-with-children** (D23; 5-point rationale at §4).
  - What is the child mission sequence? **A → B → C → D → E → F → xx99** (D24 + D25 F.i); 6 children + canonical summary at S1499.
  - Is `Ops Autopilot` in scope? **Revenue-facing modules IN; cross-cutting primitives OUT** (D26).
  - How does SIGN routing work per stage? **Light on parent, Full on each child, Q10-Q13 canonical on xx99** (D27).
  - Who owns the Opportunity → Initiative wiring? **Child E owns** per Rigby Must-fix #2 escalated to D28.
  - Should Group 1400 pilot Chris's Phase 0 F.i/F.ii/F.iii methodology? **Yes-two-triggers** (D29); playbook v3 §11.1 promotes at Group 1500 close if second application unchanged.
- **Dependencies.**
  `platform_architecture_inventory.md` §3.32 + §4.9 (S1273 v2 Rigby-added Revenue row + cross-domain flow); `platform/cross_domain_integration_audit.md` §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36 (S1274 4 findings against domain 32); `domains/memory/1300_memory_domain_scoping.md` (parent-with-children exemplar); `domains/memory/1399_memory_canonical_summary.md` (first formal xx99 + F1-F4 methodology inheritance).
- **Recommended next reads.** Group 1400 child sequence — **S1401 (§1.23) Child A Opportunity Discovery + Scoring**, then S1402 Child B (Outreach), S1403 Child C (Engagement), S1404 Child D (Meeting + Close), S1405 Child E (Attribution + Analytics), S1406 Child F (Income/Jobs lane), S1499 xx99 canonical summary.
- **Overall importance.** **First application of Chris's Phase 0 3-step methodology in the library.** Codifies domain scoping discipline (5 F.i questions + 4 F.ii questions + 4 F.iii questions + 1 group-specific artifact requirement — Revenue Lifecycle Traceability Table). If Group 1500 applies the framework unchanged, playbook v3 §11.1 promotes at Group 1500 close per two-triggers threshold (S1399 §10 codified the threshold; S1400 is trigger #1).
- **Distinguishing property.** **First arc under Chris's Phase 0 methodology + first arc where the parent scoping doc explicitly proposes a playbook v3 addition.** 15 inherited findings enumerated at §11.4 (S1273 §3.32 + §4.9 + S1274 §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36 + S1399 F1-F4 methodology). 7 overlap points documented at §10.4 with existing arcs (Group 1300 closed; Employee OS 1200s; Groups 1500/1600/1700 not-started; Group 1300 Cat G delegated; post-1400 design-preparation). Rigby cycle 2 addition §12.5 requires Revenue Lifecycle Traceability Table at S1499 (8 stages minimum + 6 columns per stage + ≥3 verified writer/reader paths per stage + F1/F2/F3/F4 diagnostic-lens verdicts + row example template at §12.5 to prevent S1499 bikeshedding).

---

### 1.24 `domains/revenue/1402_revenue_outreach_composition_delivery_audit.md`

- **Title.** Group 1400 Revenue — Category B: Outreach Composition + Delivery Architecture Audit
- **Purpose.** **Second child audit under Research Group 1400 Revenue (parent §1.22).** Category B Outreach Composition + Delivery exclusive scope per parent §10.2 evidence-surface table + §12.1 Category B F.iii questions. Verifies the `OutreachDraft` model + `OpportunityDraftGenerator` composition path + `OutreachSequencer` scheduling + outbound-channel resolution + Outreach→Engagement seam. Grounded in verified runtime evidence at `main` HEAD `beda00e5`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-4a0a28edcb7a45ec`; 2 must-fix + D.B7 dead-code fold cycle 1; 5 Q-answer folds cycle 2 with 3 nice-to-haves recorded for post-arc pickup). Pin retires post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions + all 3 parent §12.1 Category B F.iii questions:
  - **Composition path — single-shot LLM vs Content Deliberation reviewer chain?** **SINGLE-SHOT LLM.** `OpportunityDraftGenerator.render_email` at `core/services/ops_autopilot/outreach_generation.py:340` calls `client.chat.completions.create(model='gpt-5-mini', messages=[system, user], max_completion_tokens=4000, response_format={'type':'json_object'})` via `get_openai_client()` factory. No Content Deliberation invocation, no reviewer chain. Resolves S1273 §10.3 UNKNOWN #1.
  - **Where does outreach actually get SENT?** **Nowhere.** Grep across mainline for `send_outreach|dispatch_outreach|deliver_outreach|outreach\.send|outreach_send` → 0 hits. Grep for `sendgrid|postmark|mailgun|smtplib|EMAIL_BACKEND` in mainline → 0 hits (only archive/, external-project-docs/, ai_core/). `core/settings.py` defines no provider credentials. Approved drafts accumulate at `status='approved'` until they expire 30 days later. **Resolves S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 MISSING → CONFIRMED and REFINED to "entire outbound channel missing, not just Inbox."**
  - **How does OutreachSequencer scheduling work?** `approve_draft(draft_id, edited_text)` transitions `draft → approved` (line 686) and schedules `next_touch_at = now + timedelta(days=TOUCH_DAYS[touch_number])`; `evaluate(now)` scans `approved AND next_touch_at <= now AND touch_number < MAX_TOUCHES` and creates follow-up rows. **BUT: `evaluate` is CONFIRMED DEAD CODE at runtime** — Rigby ops probe (celery_task_history 30d + PeriodicTask.filter(icontains='outreach')) + parent-Claude direct read (`td_handlers_ops.py:2699-2755` shows zero PA tool action wraps `.evaluate`; only `outreach_inbox`/`outreach_approve`/`outreach_reject`/`outreach_metrics_report` exposed) + repo-wide grep for `sequencer.evaluate`/`OutreachSequencer().evaluate` (0 hits) jointly confirm no invoker. Only Touch 1 fires at runtime via `generate-outreach-drafts-daily` beat.
- **Load-bearing findings (4).**
  - **F.B1 delivery path missing (CONFIRMED HIGH, runtime).** Grep-negative evidence complete at HEAD `beda00e5` across mainline. Category B is composition-only; delivery half is a missing subsystem. Approved drafts terminate at DB row.
  - **F.B3 engagement feedback loop missing (CONFIRMED HIGH, runtime).** No reply/click/open ingestion path. `EngagementEvent.outreach_draft` FK schema exists at `core/models_engagement.py:55-59` but zero writer sites for EngagementEvent. Category C S1403 inherits the seam build-out.
  - **F.B4 cadence declared but not realized at runtime (CONFIRMED via D.B7 probe).** OutreachSequencer declares 4-touch cadence; only Touch 1 fires. Touches 2–4 depend on `evaluate` which is dead code. Divergence between declared and implemented cadence.
  - **F.B2 follow-up composition writer-site is CONFIRMED F2 orphan-write + literal-stub pattern (code HIGH; runtime blast radius ZERO due to F.B4).** `revenue.py:812-829` writes `body_text = "Draft follow-up message needed."` and omits `opportunity=parent.opportunity` on create → every follow-up would be created with `opportunity=None`. CONFIRMED writer-site; CANDIDATE at repo-wide scope. Runtime blast radius zero because `evaluate` has no invoker.
- **Inherited findings status (from parent §11.4).** S1273 §10.3 UNKNOWN #1 RESOLVED (single-shot LLM); S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 RESOLVED to "entire outbound channel missing"; S1401 §14 D6 dual-representation drift RULED OUT for Category B (reads persistent `Opportunity.objects.filter(...)` only); S1401 F1 provenance-filter drift lens CANDIDATE extends to Category B reader surface; S1401 F2 orphan-write lens CONFIRMED at writer site, CANDIDATE repo-wide, blast radius ZERO at runtime; S1401 F3 Redis-only durability lens CLEAN for Category B; ownership gap CONFIRMED for Category B (no JobContract, no dedicated queue, shared `content` queue routing) — deferred to Child E per D28.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §10.2 evidence surface + §11.4 15 inherited findings + §12.1 Category B questions); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §9.1 integration map + §14 D6 dual-representation drift + §19 R1 umbrella); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 line 293 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance].
- **Recommended next reads.** **S1403 Child C Engagement Inbound** next per parent §5 mission sequence. S1403 inherits Category B's F.B3 finding as its scope; the seam build-out (reply/click/open ingestion → EngagementEvent writes) is S1403's central deliverable. Also queued: §19 R.B1 delivery subsystem design ADR (umbrella); R.B2 follow-up composition subsystem; R.B3 F1 reader-side filter (Category-B-scoped per SIGN cycle 2 Q5); R.B4 evaluate cadence probe RESOLVED; R.B5 engagement ingestion path (S1403 owns); R.B6 offer-configuration debt; R.B7 send-gap fence test bundled with R.B1. D.B3 anchor-update at S1274 §2.4 line 293 recommended IMMEDIATELY per SIGN cycle 2 Q7 (truth correction, not synthesis).
- **Overall importance.** **Second Group 1400 child audit; first library audit to CONFIRM a missing-subsystem finding at HIGH runtime severity with complete negative-grep evidence.** Also first library audit where a Rigby ops probe + parent-Claude direct-read jointly CONFIRMED a dead-code finding (F.B4 / D.B7 / T.B5) mid-SIGN cycle 1 — extending S1401 verifier-loop from "hypothesis correction" to "runtime-liveness confirmation via ops telemetry." Load-bearing story: Category B is composition-only; the delivery half was never built AND the follow-up cadence half is dead code. This changes the arc's downstream integration seam question — Category C S1403 must build the entire ingestion path, not extend existing wiring.
- **Distinguishing property.** **First library audit where SIGN cycle 1 storage got truncated at Rigby's tool layer** — parent-Claude reconstructed the fold pass from (a) verbatim Must-fix #1 content (F.B2 CANDIDATE vs CONFIRMED classification drift), (b) inferred Must-fix #2 direction (F.B1 delivery-path severity: CONFIRMED HIGH not CANDIDATE HIGH, grep-negative evidence complete), (c) D.B7 dead-code confirmation via Rigby's ops probe + parent-Claude direct read. Cycle 2 SIGN-clean confirmed the inferred fold direction (Q3 downgraded D.B1 severity HIGH → MEDIUM as the only correction; Must-fix #2 inference verified correct). Sets pattern for future SIGN-storage-truncation recovery: reconstruct via combining verbatim excerpt + evidence-based inference + independent probe/read verification. Isolation pin `pa-4a0a28edcb7a45ec` retires post-PR-merge per playbook §15.

---

### 1.23 `domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`

- **Title.** Group 1400 Revenue — Category A: Opportunity Discovery + Scoring Architecture Audit
- **Purpose.** **First child audit under Research Group 1400 Revenue (parent §1.22).** Category A Opportunity Discovery + Scoring exclusive scope per parent §10.2 evidence-surface table + §12.1 Category A F.iii questions. Verifies the mainline `Opportunity` model family (5 owned + 5 cited-only + FreelanceOpportunity/OpportunityTracking adjacent), 8 owned services + 2 agents + 1 WebSocket consumer + `OPPORTUNITY_SCORED` EventBus event + Category-A REST/PA-tool/Celery/management-command surface. Grounded in verified runtime evidence at `main` HEAD `ae30a1fe`.
- **Status.** Draft → Active (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-16d8b24d30e7a7d8`, 4 folds — 2 must-fix + 2 nice-to-have — applied cycle 1 and accepted cycle 2). Chris commit-gate flips status → active on merge per playbook §16. Pin retired at S1401 close per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions (§20.6 checklist) + all 6 parent §12.1 Category A F.iii questions (§20.7 checklist):
  - **What IS an Opportunity?** Mainline `Opportunity` at `core/models_unified_system.py:1201` with 27 core fields + 10-variant family (5 owned + 5 sibling-lifecycle/attribution + 1 engagement-feedback) enumerated at §4.
  - **Who produces Opportunities?** 4 confirmed writers of mainline `Opportunity.objects.create(...)`: `intelligence/spider_opportunity_connector.py:~620` (STRONG), `core/agents/analysis/opportunity_scoring_agent.py:~140` (WEAK NEW), `core/services/td_handlers_agents.py` (WEAK NEW), `core/services/income_action_service.py:~95` (WEAK NEW). 25 grep files matched; 21 false positives (Category F Income/Jobs surface + FreelanceOpportunity/OpportunityTracking/RealJobOpportunity/SpiderOpportunity dataclasses) deferred to S1406.
  - **How does scoring flow?** Flow α (spider → connector → `Opportunity.create` → `_publish_scoring_event` at `scoring_dispatcher.py:21` → `publish_opportunity_scored_event` at `event_bus.py:559` → `mi:opportunity_scored` stream). Flow β (`OpportunityPipelineOrchestrator` 5-stage agent routing via PA tool). Flow γ (sports lane isolated to `OpportunityTracking`). Flow δ (hourly `score_opportunities_from_spider_data` beat per WIREMAP.md:170). Flow ε (WebSocket `opportunity-scanner` READ-ONLY from `intelligence_engine.get_current_opportunities()`).
  - **What does OPPORTUNITY_SCORED carry + who consumes?** Payload verified: opportunity_id, spider_data_id, ml_score, rule_score, hybrid_score, confidence, priority, source. Handler registered at `event_handlers.py:48` (`self.register('opportunity_scored', handle_opportunity_scored_event)`); worker subscription verified at `event_handlers.py:536` (`create_validation_worker` streams). Corrected handler action per file:line comment: DETECTS + LOGS only (HITL service creates the validation request separately, not this handler).
  - **What is OpportunityScannerConsumer for?** READ-ONLY WebSocket listener streaming from `intelligence_engine.get_current_opportunities()` in-memory realtime source — NOT persistent `Opportunity` model. Room group `opportunity_scanner`. Hard-coded initial payload `domains_monitored: [SPORTS_BETTING, CRYPTO, TRADING, REAL_ESTATE]`.
  - **Does sports_opportunity_generator produce into mainline Opportunity or a separate lane?** **SEPARATE LANE** — `intelligence/sports_opportunity_generator.py:83` writes `OpportunityTracking.objects.create(...)` (intelligence app), not mainline `Opportunity`. S1274 §2.4 line 270 MISSING classification REMAINS ACCURATE for mainline; refinement is "separate lane" wording rather than "missing implementation."
- **Load-bearing findings.**
  - **Sports lane resolved (§12.1 Q6):** separate lane framing per M1 fold.
  - **NEW dual opportunity representation drift (§14 D6 + §19 R1 umbrella):** 5 consumer sites in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597) stream from `intelligence_engine.get_current_opportunities()` in-memory source — Rigby SIGN cycle 1 grep expanded finding from 1 site to 5.
  - **F1 provenance drift CANDIDATE (HIGH):** writers tag `source` + `metadata['spider_source']` inconsistently across producers (spider connector complete; agents + PA-tool paths sparse); readers ignore provenance.
  - **F3 Redis-only durability CANDIDATE (HIGH):** `spider_opportunity_connector.py` uses async Redis with `cache_timeout=300`, no DB fallback.
  - **F2 orphan-write cluster CANDIDATE (HIGH):** 10-variant Opportunity family + Session Pre-38 partnership_* fields (10 fields with defaults, consumption sites unverified).
  - **OpportunityPipelineOrchestrator vs OpportunityExecutionPipeline COMPLEMENTARY, not overlapping** (parent-Claude verifier-loop resolved Agent 6's duplication flag via Agent 2 direct read — Orchestrator = transform Dict→Dict, ExecutionPipeline = materialize Opportunity→PartnershipProject).
  - **NEW debt T5:** `settings.py` `task_routes` defines `score_opportunities_from_spider_data` TWICE (line 1277 `long_running` + line 1484 `content`); later wins → effective queue `content`. Follow-on cleanup PR needed.
  - **Ownership gap CONFIRMED** (S1274 §14 #36 inherited HIGH); no JobContract wiring, no dedicated beat queue, no CODEOWNERS-style artifact. Deferred to Child E aggregate per D28.
  - **Maturity WORKING** (S1273 baseline preserved; no upgrade/downgrade). **Coverage LIGHT** (matches parent §11.3; upgrade candidate at S1499 xx99).
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §10.2 evidence surface + §11.4 15 inherited findings + §12.1 Category A questions + §12.5 F.iii artifact requirement); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 + §3.7 + §5.10 + §6.2 + §9.6 + §14 finding #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance].
- **Recommended next reads.** **S1402 Child B Outreach Composition + Delivery** next per parent §5 mission sequence. Also queued: §19 R1 umbrella "Dual-representation + provenance contract" post-arc design-preparation ADR; R2 scoring rate telemetry probe (Rigby-side ORM); R3 producer inventory completion → Category F S1406; R4 PeriodicTask row verify; R5 OpportunityAIAnalyzer liveness probe; R6 expires_at enforcement audit; R7 OPPORTUNITY_CREATED stream disposition; R8 T5 Celery route cleanup PR.
- **Overall importance.** **First Group 1400 child audit; validates the audit contract's parent-Claude verifier-loop discipline BEFORE Rigby.** 5 sub-agent claims corrected pre-SIGN (Agent 3 beat-schedule negative claim + orchestrator-overlap flag + publisher-line correction + dual-representation surfaced from consumer read + Celery duplicate surfaced from settings grep). Rigby SIGN cycle 1 SIGN-with-edits (4 folds — 2 must-fix + 2 nice-to-have) at High confidence; cycle 2 SIGN-clean High confidence. Sports lane verdict resolves parent §12.1 Q6 definitively (SEPARATE LANE — S1274 MISSING remains accurate for mainline). Dual opportunity representation NEW finding sets up R1 umbrella design-preparation ADR.
- **Distinguishing property.** **First library audit to surface a NEW dual-representation drift finding via a Rigby SIGN cycle 1 grep expansion** — Rigby's independent verification broadened the finding from 1 consumer site to 5, changing R1 from "single consumer's local bug" to "arc-wide contract question." Also first library audit where parent-Claude verifier-loop overrode a sub-agent's duplication flag via a competing sub-agent's direct code read (Agent 6 flagged Orchestrator ↔ ExecutionPipeline as duplication candidate; Agent 2's direct read showed complementary roles). Isolation pin `pa-16d8b24d30e7a7d8` retired at S1401 close per playbook §15.

---

### 1.25 `domains/revenue/1403_revenue_engagement_inbound_audit.md`

- **Title.** Group 1400 Revenue — Category C: Engagement Inbound Architecture Audit
- **Purpose.** **Third child audit under Research Group 1400 Revenue (parent §1.22).** Category C Engagement Inbound exclusive scope per parent §3 Cat C evidence surface + §12.1 Category C F.iii questions. Verifies the 4 engagement-shape models (`EngagementEvent` + `EngagementMetrics` + `OpportunityInteraction` + `ContentEngagement`) + `EngagementEngine` 7-method surface + `EngagementAutonomyEngine` 4-method surface + policy-engine wiring + WebSocket-consumer session-aggregation axis + F.B3 ingestion path design-preparation (inherited from S1402 as CENTRAL S1403 deliverable). Grounded in verified runtime evidence at `main` HEAD `d91d30f7`.
- **Status.** Draft → Active on Chris merge (Rigby SIGN-clean cycle 2 High confidence on fresh isolation pin `pa-fba0c4c81fba4922`; cycle 1 SIGN-with-edits Medium-High confidence → cycle 1 fold applied — must-fix #1 (runtime row-count verification) empirically CLOSED via parent-Claude Django ORM `.count()` on local env (all 4 Category C tables = 0 rows) + must-fix #2 (placeholder-stall artifact) WITHDRAWN as Rigby cycle-1 narrative artifact not audit defect + 4 Q-answer folds Q1/Q4/Q5/Q6; cycle 2 SIGN-clean High confidence + Q7/Q8/Q9 answers + 2 nice-to-have folds — Env Coverage Table + T.C8 three-checkbox split). Pin retires post-PR-merge per playbook §15.
- **Research type.** Child audit (playbook §11.2 20-section template). `authority: research`, `category: child_audit`.
- **Primary questions answered.** All 28 canonical questions + all 3+1 parent §12.1 Category C F.iii questions (the +1 = inherited "how to design F.B3 ingestion given F.B1 delivery gap"):
  - **Which of the 4 engagement models is canonical?** `EngagementEvent` at `core/models_engagement.py:18` is parent-declared canonical inbound event stream — **but has ZERO writer sites at HEAD `d91d30f7`**. Grep `EngagementEvent.objects.create|EngagementEvent(` → only class definition. Both `outreach_draft` FK (:55-59) and `opportunity` FK (:62-66) are schema-only. **Empirical runtime CONFIRMATION** via parent-Claude Django ORM: `EngagementEvent.objects.count() = 0`. Extends S1402 F.B3 with the second-FK evidence.
  - **What is the event stream vs aggregate axis?** Parent §3 Cat C hypothesized three-axis map (event log = EngagementEvent; aggregation = EngagementMetrics + ContentEngagement; join = OpportunityInteraction) — **REFUTED by dual-sub-agent verification.** Actual axis is **three independent surfaces**: (i) EngagementEvent event-log axis architecturally-declared but runtime-empty; (ii) session-aggregation axis EngagementMetrics + OpportunityInteraction lives at `revenue_opportunities_consumer.py:849/527/694` WebSocket-consumer dual-write; (iii) ContentEngagement is orthogonal content-pipeline learning surface with no FK back to inbound. OpportunityInteraction is detail-child of EngagementMetrics via nullable `engagement_session` FK, not a join artifact.
  - **What does EngagementAutonomyEngine gate + default state?** Monitoring + reporting only; **NOT gating.** SLA thresholds hardcoded (`SLA_WARNING_HOURS=4`, `SLA_CRITICAL_HOURS=24`, `SLA_BREACH_HOURS=48`). No governance §3.23 crossover — kill-switch does NOT gate engagement autonomy. Default state: no autonomy mutations, no autonomous replies.
  - **How would F.B3 ingestion path be designed given F.B1 gap?** Central S1403 deliverable per §19 R.C1: webhook receiver `/api/webhooks/engagement/<provider>/` reusing Stripe pattern at `views_stripe.py:41-53`; 4 new EventStream additions (`ENGAGEMENT_REPLIED/OPENED/CLICKED/CLASSIFIED`); writer contract + idempotency via `get_or_create(outreach_draft=..., provider_message_id=...)`; feature-gate `settings.ENGAGEMENT_INGESTION_ENABLED`. BLOCKER pre-work: `OutreachDraft.provider_message_id` field MISSING (grep zero hits in `models_outreach.py`). Rigby cycle 1 Q4 lean **two sequential ADRs** — F.B1 delivery first (establishes channel + identifiers), F.C1 inbound ingestion stacked on top; "cleaner dependency ordering and less thrash."
- **Load-bearing findings (6).**
  - **F.C1 ingestion path missing (CONFIRMED HIGH — code + runtime local, prod unknown).** Zero EngagementEvent writer sites at HEAD `d91d30f7`. Grep + Django ORM `.count() = 0` both confirm. Extends S1402 F.B3 with `opportunity` FK second-writer-gap evidence. Prod PENDING (T.C8 tool gap).
  - **F.C2 corrected axis map (CONFIRMED, dual-agent verified).** Three independent surfaces — not the parent §3 hypothesis.
  - **F.C3 OpportunityInteraction F2 orphan-write CONFIRMED at writer-site `views_opportunities.py:56-65`.** REST `quick_apply()` omits `engagement_session` FK. Runtime blast radius LOCAL = ZERO (`OpportunityInteraction.objects.count() = 0`). Prod UNKNOWN. Sibling to S1402 F.B2 zero-blast-radius pattern via different mechanism.
  - **F.C4 ContentEngagement docstring drift (CONFIRMED HIGH docstring, MEDIUM runtime).** `models_pipeline_feedback.py:372-378` claims "closes the learning loop"; no FK bridge to EngagementEvent/Metrics/OpportunityInteraction exists. Rigby cycle 1 Q5 lean (i) narrow docstring NOW.
  - **F.C5 EngagementAutonomyEngine "reply context builder" drift (CONFIRMED LOW).** `engagement.py:774` lists 4 value-adds; no such method in 4-method class body. Rigby cycle 1 Q6 lean (iii) reframe as "planned surface."
  - **F.C6 `run_ops_autopilot` deferred-by-policy (CONFIRMED, load-bearing nuance to policy-engine claims).** `core/tasks.py:13090` defines beat wrapper with declared 10min cadence docstring; NOT registered as PeriodicTask (0 of 92 enabled rows); intentionally deferred per AUDIT_FINDINGS.md #12 gating (`core/celery.py:507-509` + `:633-634`). Ad-hoc PA-tool invocation path LIVE at `td_handlers_ops.py:1643,1674`. Category C's `evaluate()` sweeps fire only on operator initiation, never autonomous. Memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN. Rigby cycle 2 Q1 lean **(iii) separate ADR outside G1400 arc** for enable-decision (cross-category impact spans all 6 categories).
- **Inherited findings status (parent §11.4 + S1402).** S1402 F.B3 CONFIRMED HIGH and EXTENDED (now includes `EngagementEvent.opportunity` FK second-writer-gap). S1402 F.B1 delivery-path-missing BLOCKER dependency for F.C1 ingestion design. S1402 F.B4 cadence-not-realized does NOT extend to Category C evaluate methods (both LIVE via policy registry, though F.C6 deferred-by-policy means autonomous cadence dormant). S1401 F1 provenance-filter drift CANDIDATE extends to Cat C readers. S1401 F2 orphan-write CONFIRMED at `views_opportunities.py:56-65` (F.C3). S1401 F3 Redis-only durability CANDIDATE holds (`revenue_opportunities_consumer.py:302-306` 5min TTL). Ownership gap S1274 §14 #36 CONFIRMED HIGH for Category C (0 JobContract + 0 AGENT_MAP + 0 task_routes hits for "engagement"). Coverage upgraded LIGHT → MODERATE. Maturity WORKING (code) / DEFERRED-BY-POLICY (autonomous runtime) / WORKING code + DORMANT local (session-agg) / MISSING (canonical ingestion) — four-way split extending S1402 WORKING/PARTIAL pattern.
- **Dependencies.**
  `1400_revenue_domain_scoping.md` (parent — §3 Cat C evidence surface + §11.4 15 inherited findings + §12.1 Category C questions); `1401_revenue_opportunity_discovery_scoring_audit.md` (sibling — §9.1 integration map); `1402_revenue_outreach_composition_delivery_audit.md` (sibling — §9 integration map + F.B3 CENTRAL inheritance + §14 D.B3 anchor-update precedent + §19 R.B5 engagement ingestion path); `platform_architecture_inventory.md` §3.32 + §4.9 [S1273]; `platform/cross_domain_integration_audit.md` §2.4 + §5.10 + §14 #36 [S1274]; `domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4 [S1399 methodology inheritance]; `docs/AUDIT_FINDINGS.md` §12 [F.C6 deferred-by-policy classification source].
- **Recommended next reads.** **S1404 Child D Meeting + Close** next per parent §5 mission sequence. Category D inherits Category C's session-aggregation axis + read-only-EngagementEngine surface + Rigby cycle 1 Q4 sequential-ADR pair-design recommendation (F.B1 → F.C1 order). Also queued: §19 R.C1 F.C1 ingestion path ADR (CENTRAL — pair-designed sequentially with F.B1); R.C2 F.C3 orphan-write fix at `views_opportunities.py:56-65`; R.C3 F.C4 ContentEngagement FK bridge (post-arc); R.C4 documentation anchor updates at `platform_architecture_inventory.md` §3.32 with per-model annotations (EngagementEvent schema-present-ingestion-missing-count=0; EngagementMetrics/OpportunityInteraction aggregation-axis-working-count=0-due-to-no-WS-activity; short note "engagement inbound relies on session/WebSocket surfaces not canonical event ingestion") per Rigby cycle 2 Q9 lean; R.C5 `OutreachDraft.provider_message_id` migration (blocks R.C1); R.C6 F.C5 "reply context builder" resolution (three-fork); R.C7 Governance §3.23 crossover ADR (bundle with Group 1700 Observability); R.C8 F1 provenance-drift repo-wide sweep (deferred until F.C1 ingestion writer contract lands). **T.C8 tool-surface gap** (ToolCallRecord query + bounded ORM count + prod DB reach) IMMEDIATE per Rigby cycle 2 Q8 — low-risk high-leverage arc-support tools.
- **Overall importance.** **Third Group 1400 child audit; first library audit to CONFIRM a canonical event log architecturally-intact-but-runtime-empty finding at both CODE and RUNTIME LOCAL tiers** via parent-Claude Django ORM `.count()` when Rigby's `db_health_tool` returned indeterminate `row_count=-1` estimate. Also first library audit where **PROD runtime tier is explicitly UNKNOWN due to Rigby tool-surface gap** (T.C8 `db_health_tool env=prod` "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN") — logged as explicit constraint on empirical falsification scope. Load-bearing story: Category C is code-complete on read-only monitoring + session-aggregation surfaces but runtime-dormant in the probed env; canonical ingestion has no writer path; the F.B1 → F.C1 pair-design sequential ADR is the arc-forward critical path.
- **Distinguishing property.** **First library audit where parent-Claude Django ORM `.count()` closed a Rigby cycle 1 must-fix that Rigby's own tool surface could not resolve** — extends the S1402 D.B7 joint-verifier-loop methodology to "when Rigby's tool returns indeterminate, parent-Claude runs direct-verification via alternate path (Django `.venv/bin/python manage.py shell` in this case)." Also first library audit where **Rigby withdraws a cycle-1 must-fix as her own narrative artifact after parent-Claude pushback** (cycle 2 Rigby: "Must-fix #2 is withdrawn: agreed it was my cycle-1 response artifact, not an audit-file defect"). Sets pattern for two verifier-loop conventions: (a) parent-Claude runs alternate direct-verification when Rigby's tool returns indeterminate; (b) parent-Claude pushback on must-fix classification is a legitimate cycle-2 fold move when the must-fix originates in Rigby's own response artifact rather than audit content. Isolation pin `pa-fba0c4c81fba4922` retires post-PR-merge per playbook §15.

---

## 2. Recommended Reading Paths

Engineers join with different goals. Each path lists docs in
order; bracketed numbers point back to §1.

### Path A — "I need to understand Employee OS"

1. `CLAUDE.md` (Quick Start + Working with Rigby section)
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` (canonical primitives +
   anti-duplication matrix)
3. `docs/topics/employee-os.md` (subsystem narrative)
4. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1]
5. `docs/research/employee_os_collaboration_patterns.md`
   [§1.3]
6. Latest handoff: `docs/handoffs/SESSION_1267_*.md`

You will now know: the four current employees, the lifecycle
primitives that compose them, the comms surfaces they expose,
and the collaboration substrates available across the wider
platform.

### Path B — "I want to design new employees"

1. Path A above (in full).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` §5 ("Quick-Start for
   Adding a New Employee").
3. `docs/research/employee_os_collaboration_patterns.md` §8
   (reuse classification — esp. SAFE rows) and §9
   (anti-duplication mapping).
4. `core/employees/jobs.py:74-162` (frozen `AIEmployee` +
   `JobContract` dataclass shapes) — read code, not docs.
5. `core/employees/mission_runner.py:1-230` (module docstring
   + lifecycle).
6. `core/employees/comms_docs_manager.py:1-122` (canonical
   per-employee comms wrapper pattern).

**Hard rule before opening a PR for Employee #5:** read
`EMPLOYEE_OS_PRIMITIVES.md` §2 + §4 in full. The 23-row "do
NOT build" matrix and the 7 explicit warnings exist because
each one cost real time before.

### Path C — "I want to understand governance"

1. `docs/research/governance_authority_evolution.md` [§1.4]
   — the canonical anchor (4 planes; 35 gates; 12 incidents;
   all Q1-Q12 answered).
2. `docs/EMPLOYEE_OS_PRIMITIVES.md` row 17 (GovernanceState +
   KillSwitch).
3. `docs/research/employee_os_collaboration_patterns.md` §2
   rows 55-56 + §10 Q11 (collaboration audit's view of
   authority enforcement).
4. `core/models_governance.py:17-189` (GovernanceState +
   KillSwitch model definitions).
5. `core/employees/mission_runner.py:258-275` (authority
   warn-mode constants + S1264 design).
6. `docs/handoffs/SESSION_1264_AUTHORITY_WARN_MODE.md`
   (authority contract observation design + Rigby SIGN edits).

**Big findings to internalize:** four governance planes don't
compose today (autonomy / authority / budget / human
governance). KillSwitch has full write path + TTL but **zero
dispatch consumers** — write surface works, enforcement
doesn't. `JobContract.authority` is observation-only;
enforcement blocked on Symbol Mapping prerequisite (P0 next
research per §5.2).

### Path D — "I want to build new communication"

1. `docs/research/employee_os_communication_substrate_audit.md`
   [§1.1] — esp. §8 reuse classifications and §7 known risks.
2. `docs/research/employee_os_communication_protocol_sketch.md`
   [§1.2] — concrete pattern to mirror.
3. `core/employees/comms.py:228-367`
   (`post_shift_report` — canonical bounded-comms helper).
4. `core/employees/comms_docs_manager.py:1-122` (thin
   wrapper pattern).
5. `core/models_messaging.py:21-141`
   (MessageThread / ThreadParticipant / DirectMessage shapes).

**Hard rule:** do NOT propose enabling
`messaging_tool.send_message` in any design. It is OFF by
design (per `EMPLOYEE_OS_PRIMITIVES.md` §4.7 and
substrate audit §8 DO-NOT-REUSE row). Free-form LLM outbound
is the wrong shape for structured comms; bounded helpers in
`core/employees/comms*.py` are the right shape.

### Path E — "I need to understand orchestration"

1. `docs/research/employee_os_collaboration_patterns.md` §3
   (12 collaboration flow diagrams) + §4 (delegation
   mechanism comparison table).
2. `docs/topics/celery-workers.md` (worker / queue topology).
3. `core/employees/mission_runner.py:1-1758` (one orchestrator).
4. `ai_core/agents/hybrid_executor.py:244,351` (the other
   orchestrator — Celery chain + group).
5. `core/agents/workflow_orchestration_agent.py:47,302`
   (ThreadPoolExecutor fan-out variant).

**Big finding to internalize:** there are **two orthogonal
durable orchestration paths** (Celery chain in
`hybrid_executor.py` vs. MissionRunner step loop in
`mission_runner.py`). They do NOT compose today. Choose one
based on durability needs; do not mix.

### Path F — "I want to understand autonomous execution"

1. `docs/topics/spider-network.md` + `docs/topics/initiative-pipeline.md`.
2. `docs/research/employee_os_collaboration_patterns.md` §3.6
   (Spider → Signal → Trigger → Work flow) and §3.7 (Spider →
   EventBus → Consumer Group flow).
3. `core/services/signal_aggregation_service.py:33-1161`
   (entity-token clustering; pattern detection).
4. `core/services/event_bus.py:21-728` (8 streams + DLQ).
5. `core/services/body_coordinator.py:110-300+` (9 body
   systems autonomic reflex layer).

**Gap to know:** autonomous→initiative auto-creation
(AutoTopic → Initiative) is UNCERTAIN per collaboration audit
§10 Q2 — no creation task traced. Treat as not-yet-wired.

### Path G — "I need to understand platform reliability"

1. `docs/research/employee_os_collaboration_patterns.md` §5
   (mission coordination — what survives process / Redis / DB
   restarts) and §7 (29 failure modes).
2. `docs/research/employee_os_communication_substrate_audit.md`
   §7 (12 incident classes).
3. `docs/AUDIT_FINDINGS.md` (canonical Celery deferred list,
   S1115 multi-batch audit).
4. `docs/topics/celery-workers.md` (queue + worker
   architecture).
5. `core/services/anthropic_client_factory.py:38-50` +
   `core/services/openai_client_factory.py:68-72`
   (centralized timeout contract — must use these factories).

**Hard rule:** any new LLM client call site MUST go through
the factory (per memory rules
`feedback_anthropic_client_factory` and
`feedback_openai_client_factory`). Bare `Anthropic()` /
`OpenAI()` defaults to 600s timeout, causing the zombie-thread
class documented in collaboration audit §7 row 17.

### Path H — "I need to understand the whole platform"

*Added S1273 v5.* This is the whole-platform onboarding path.
Use it when your work spans multiple domains or you're new to
the codebase.

1. `CLAUDE.md` (Quick Start + Working with Rigby + system stats).
2. `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor — glossary +
   subsystem summaries).
3. `docs/PLATFORM_INVENTORY.md` (runtime anchor — authoritative
   counts; regenerable via `generate_platform_inventory`).
4. `docs/research/platform_architecture_inventory.md` [§1.9] —
   the 32-domain map + 9 cross-domain flows + maturity matrix +
   11-mission roadmap.
5. Whichever specific §3.n inventory in §1.9 matches your work.
6. If that subsystem has an Employee OS-arc research doc
   (§1.1-§1.8), read it next.

**Big finding to internalize:** the platform combines four
historically-separate stacks (AI Studio + DBAO + Employee OS +
Revenue Pipeline) under one substrate. §1.9's §1 executive
summary + §5 duplicate/overlapping systems section will show you
where those stacks compose cleanly and where they don't.

---

## 3. Architecture Domains

The platform is partitioned into ~17 domains below (the S1268-
S1272 arc's view). For a **whole-platform 32-domain map**
(broader scope, added S1273 v5), see `docs/research/platform_
architecture_inventory.md` [§1.9] §2. The two are complementary:
this table is Employee-OS-adjacent depth; §1.9's table is
whole-platform breadth.

For each row, the table lists what research exists (in this
library), what is still missing, and current maturity.

| Domain | Existing research | Canonical anchors | Missing research | Maturity |
|---|---|---|---|---|
| **Employee OS — core** | §1.1, §1.2, §1.3 | EMPLOYEE_OS_PRIMITIVES.md; topics/employee-os.md | (none today; covered by §1.1 + §1.3) | **High** — 4 production employees, fully audited |
| **Mission System (MissionRunner)** | §1.3 (§2 row 19, §3.9, §6) | mission_runner.py (1758 lines); jobs.py:74-162 | Dedicated MissionRunner architecture doc (could lift from §1.3's flow + reuse rows) | **High** — production for 4 employees |
| **Governance** | §1.4 (full audit; 4 planes documented) + §1.3 (§2 rows 55-56) | models_governance.py | (well-covered; downstream is Cross-plane Composition — see §5.4) | **Medium-High** — primitives fully audited; freeze/safe_mode wired; KillSwitch enforcement missing |
| **Authority** | §1.4 (full audit; 68 entries / 30 prohibited / 35 gates) + §1.3 (§2 row 26 + §10 Q11) + §1.6 (Symbol Mapping — 57 unique action strings; 5 mapping options; 20 enforcement boundaries) + §1.7 (Actor Attribution — WHO composes with WHAT) + §1.8 (Authority Enforcement Design Space — 24 inputs / 20 boundaries / 12 modes / 6 options A-F / 33 incidents / 15 anti-patterns / 15 prereqs) | mission_runner.py:258-275 (S1264 warn-mode); jobs.py:41-52 (AuthorityLevel); llm_enforcer.py:200-262 (fail-open precedent) | **Symbol Mapping Option Selection Design** (recommended P0 next per §1.8 §14.1 — pick from §1.6's 5 options + Chris gate) | **Medium-High** — all three prereqs shipped as research (S1270 + S1271 + S1272); no design decision yet; enforcement remains observation-only |
| **Actor Identity / Attribution** | §1.7 (full audit; 19 identity concepts; 22 attribution surfaces; 15 historical failures; 25 identity registries; F11 executor/sponsor/principal role vocabulary) | `AIEmployee` (jobs.py:73-92); `UnifiedUser` (models/base/models.py:86); `_resolve_runs_as_user_id` (mission_runner.py:1585-1591); `canonicalize_agent_name` (deliverable_aliases.py:39-47) | (§1.7 F1: OpsRun has no user FK — largest attribution gap; downstream design gated by Symbol Mapping Option Selection per §1.8 §14.1) | **Medium** — mixed strong-FK / ambiguous-CharField attribution; role vocabulary proposed but not schema-enforced |
| **Authority Enforcement (design space)** | §1.8 (full design-space discovery; 6 options A-F; 12 modes; 15 anti-patterns; 15-prereq DAG) | S1264 warn-mode; LLMEnforcer fail-open pattern; MissionRunner `_emit_authority_contract_event` | Symbol Mapping Option Selection Design + downstream Authority Enforcement Design Decision (Chris-gated per §1.8 §14.3) | **Design-space only** — no runtime enforcement designed yet; **maintenance note:** enforce-mode requires §14.1 P0 selection first; do not treat §1.8 options as implementable without downstream Chris-gated design decision |
| **Communication (employee comms)** | §1.1 (full); §1.2 (specific path) | comms.py, comms_docs_manager.py, EMPLOYEE_OS_PRIMITIVES.md §4.7 | Inter-employee reply lane (§1.3 F4); cross-fleet messaging | **Medium** — outbound shift reports work; inter-employee design sketched but not built |
| **Messaging (raw substrate)** | §1.1 (§2 rows 35-37); §1.3 (§2 row 36) | models_messaging.py:21-141 | inbox UI semantics for `thread_kind='inter_employee_notice'` (frontend ticket, not research) | **High** — substrate is production |
| **Memory (employee / agent)** | (none in research library) | core/models_agent_memory.py | **Memory Architecture research doc** — esp. how do employees remember each other's past verdicts? | **Low / UNKNOWN** — no research yet |
| **Decision Making** | §1.3 (§2 rows 38-42 + §3.10) | models_human_interface.py; models_orchestration.py | Decision precedent + multi-stakeholder approvals (§1.3 §10 Q6) | **Medium** — HAI lifecycle is robust; collaborative decisions absent |
| **Human Interface** | §1.3 (§2 rows 38-42, 58-59) | HumanAttentionItem + HumanFeedbackRecord + HumanPreference; views_inbox.py | DM-arrived WebSocket event surfacing (frontend ticket) | **High** — HAI lifecycle service production |
| **Automation (workflow autopilot)** | §1.3 (§2 row 47 — `WorkspaceTrigger`) | models_skin_layer.py | `workspace_autopilot_tick` location UNKNOWN (§1.3 §10 Q1); needs trace | **Medium / UNKNOWN** |
| **Agents (BaseAgent + AGENT_MAP)** | §1.1 (§3); §1.3 (§2 rows 1-9) | core/agent_router.py; core/agents/base_agent.py; topics/agent-system.md | (well-covered) | **High** — 83 agents production |
| **Spiders** | §1.3 (§3.6 + §3.7) | ai_core/spiders/; topics/spider-network.md | (well-covered) | **High** — 80 spiders + 1.14M item hashes |
| **Signal Processing** | §1.3 (§2 rows 48-50) | signal_aggregation_service.py; content_scoring_service.py | AutoTopic → Initiative wiring (§1.3 §10 Q2) | **Medium** — clustering production; downstream uncertain |
| **Workflows (Initiative pipeline)** | §1.3 (§2 rows 43-44 + §3.8) | models_document_registry.py; topics/initiative-pipeline.md; DREAM_INITIATIVE_WORKFLOW.md | (Initiative is documented; cross-employee composition is not) | **High** (pipeline) / **Medium** (composition) |
| **Scheduling (beat)** | §1.3 (§3.11) + 5-agent scheduling sweep evidence | core/celery.py:37-797; topics/celery-workers.md; AUDIT_FINDINGS.md §12 | **Cross-employee scheduling research doc** | **Medium** — beat tasks documented; cross-employee handoffs absent |
| **Observability** | §1.3 (§6 evidence scoring) | OpsRunEvent + AgentExecution + ToolCallRecord + LLMCallEvent + CeleryTaskEvent | (well-covered) | **High** — five audit tables compose |
| **Telemetry (LLM costs)** | §1.3 (§2 rows 8, 63-64) | models_llm_telemetry.py | (well-covered) | **High** — cleanup watchdog + total-request bound |
| **Reliability** | §1.3 (§5 + §7) | anthropic_client_factory.py; openai_client_factory.py; cleanup beat tasks | (well-covered) | **High** — multi-layer defense |
| **Infrastructure** | (none in research library — runtime evidence only) | topics/infrastructure.md; topics/celery-workers.md; Procfile | Redis broker persistence config — UNKNOWN (§1.3 §10 Q5) | **Medium / UNKNOWN** |
| **Knowledge Pipeline** | (none in research library) | docs/KNOWLEDGE_PIPELINE.md | (covered by KNOWLEDGE_PIPELINE.md narrative) | **High** — production pipeline |
| **Revenue / Outreach / Engagement** *(new domain, added S1273 v5)* | §1.9 §3.32 (LIGHT coverage — models + services + agents enumerated; no canonical topic doc) | models_outreach.py:18 (OutreachDraft); models_engagement.py:18 (EngagementEvent); models_meeting.py:18 (Meeting); models_close_pack.py:20 (ClosePack); opportunity_pipeline_orchestrator.py; ops_autopilot/revenue.py + outreach_generation.py + engagement.py | **Revenue Pipeline canonical architecture doc** (models + services + agents + PA tools + outbound channel + attribution) — see §5.12 | **WORKING** (per §1.9 §3.32) — models + services + agents shipped; whether pipeline drives revenue in prod vs is scaffolding awaiting activation is UNKNOWN |

---

## 4. Architecture Dependency Graph

The library's documents build on each other in a specific
order. Reading them out of order is technically possible but
each downstream doc assumes its upstream context.

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                └────────────────────┬────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────┐
                    │  EMPLOYEE_OS_PRIMITIVES.md          │
                    │  (canonical primitives + §2 anti-   │
                    │   duplication matrix)               │
                    └─────────────────┬───────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │  research/employee_os_communication_substrate_  │
        │  audit.md                                       │
        │  (Inventory of comms primitives + reuse class)  │
        └───────────────────┬─────────────────────────────┘
                            │
            ┌───────────────┴────────────────┐
            ▼                                ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  research/employee_os_    │    │  research/employee_os_         │
│  communication_protocol_  │    │  collaboration_patterns.md     │
│  sketch.md                │    │  (Platform-wide inventory of   │
│  (One concrete path:      │    │  collaboration; 64-row table;  │
│  Auditor → Chief of Staff)│    │  11 substrates; 29 failures)   │
└──────────┬────────────────┘    └────────────────┬───────────────┘
           │                                      │
           ▼                                      ▼
┌───────────────────────────┐    ┌────────────────────────────────┐
│  [Future: v0 PR for the   │    │  research/governance_authority_│
│  protocol — gated by      │    │  evolution.md  [§1.4]          │
│  Chris's greenlight]      │    │  (4 planes; 35 gates; 12 inc.; │
│                           │    │  Symbol Mapping = P0 next)     │
└───────────────────────────┘    └────────────────┬───────────────┘
                                                  │
                                                  ▼
                                ┌──────────────────────────────────┐
                                │  research/symbol_mapping_        │
                                │  architecture.md  [§1.6]         │
                                │  (57 unique action strings; 5    │
                                │  mapping options A-E; 20         │
                                │  enforcement boundaries; SIGN-   │
                                │  with-edits from Rigby S1270)    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  research/actor_identity_        │
                                │  attribution_architecture.md     │
                                │  [§1.7]                          │
                                │  (19 identity concepts; 22       │
                                │  attribution surfaces; 25        │
                                │  registries; F11 executor/       │
                                │  sponsor/principal role vocab;   │
                                │  Rigby pressure-test SIGN-with-  │
                                │  edits S1271)                    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  research/authority_enforcement_ │
                                │  design_space.md  [§1.8]         │
                                │  (24 inputs; 20 boundaries; 12   │
                                │  modes; 6 options A-F; 15 anti-  │
                                │  patterns; 15-prereq DAG; Rigby  │
                                │  pressure-test SIGN-with-edits   │
                                │  S1272 — 3 SIGN-added boundaries │
                                │  WebSocket/Fleet/Spider)         │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  [Future research mission —      │
                                │  recommended P0 per §1.8 §14.1]  │
                                │  Symbol Mapping Option Selection │
                                │  Design (picks from §1.6's 5     │
                                │  options; Chris gate; converts   │
                                │  research to design decision)    │
                                └────────────────┬─────────────────┘
                                                 │
                                                 ▼
                                ┌──────────────────────────────────┐
                                │  [Further future research —      │
                                │  see §9 roadmap]                 │
                                │  Actor Role Propagation ·        │
                                │  Authority Enforcement Design    │
                                │  Decision · Trust Propagation ·  │
                                │  Memory · Mission Composition ·  │
                                │  Cross-Employee Scheduling · …   │
                                └──────────────────────────────────┘
```

**Sibling arc (added S1273 v5) — whole-platform inventory.**
`platform_architecture_inventory.md` [§1.9] is NOT downstream
of the Employee OS arc. It's a sibling arc off the same three
anchors:

```
                ┌─────────────────────────────────────────┐
                │  PLATFORM_INVENTORY.md (runtime anchor) │
                │  PLATFORM_WHAT_IT_IS.md (narrative)     │
                │  EMPLOYEE_OS_PRIMITIVES.md (primitives) │
                └────────────────────┬────────────────────┘
                                     │
                       ┌─────────────┴─────────────┐
                       ▼                           ▼
        ┌──────────────────────────┐  ┌───────────────────────────┐
        │  Employee OS Arc         │  │  Whole-Platform Inventory │
        │  §1.1 → §1.2/§1.3 →      │  │  §1.9 (S1273)             │
        │  §1.4 → §1.6 → §1.7 →    │  │  32 domains + 9 flows +   │
        │  §1.8 (S1268-S1272)      │  │  11-mission roadmap       │
        └──────────────────────────┘  └───────────────────────────┘
```

§1.9 cites downstream findings from §1.4 (governance planes),
§1.6 (symbol mapping), and §1.7 (actor identity) where the
Employee-OS-arc research is the source of truth for a subset of
its findings. It does NOT depend on the arc's ordering.

**Reading the graph.** The two prior anchors at the top
(`PLATFORM_INVENTORY` + `PLATFORM_WHAT_IT_IS`) and the
primitives doc (`EMPLOYEE_OS_PRIMITIVES`) are *not* in the
research library but are **load-bearing context** for
everything in it. Any research doc that doesn't honor those
three is broken at the root.

The protocol sketch (§1.2) and the collaboration patterns
audit (§1.3) are siblings, both downstream of the substrate
audit (§1.1). They were written in the same session
(S1268) — the sketch came first, the wider audit came
second once Rigby's review of the sketch surfaced the broader
"how does collaboration work everywhere" question.

**Convention.** Every new research doc declares its parents
via the `companion_docs` frontmatter field. The dependency
graph above is reconstructable from those declarations.

---

## 5. Research Gaps

The library is **young** — 3 docs, all S1268. There are real
gaps. Below are the ones that have surfaced explicitly during
S1268 research, with priority and rationale. Each is a
*research* gap — i.e., something that should get its own
research doc before it gets implemented.

### 5.1 Governance + Authority Evolution — CLOSED S1269

**Closed by:** `docs/research/governance_authority_evolution.md`
(§1.4). Audit shipped 2026-06-30; Rigby SIGN-with-edits folded.
4 governance planes documented; 35 runtime gates inventoried;
warn-mode mechanics fully traced; 12 failure modes documented;
canonical foundation identified.

**Successor gap:** Symbol Mapping Architecture (see §5.2 below
— renumbered from prior §5.2; was P1, now P0 per §1.4 §11
recommendation).

### 5.2 Symbol Mapping Architecture — CLOSED S1270

**Closed by:** `docs/research/symbol_mapping_architecture.md`
(§1.6). Research shipped 2026-06-30; Rigby SIGN-with-edits
folded. 57 unique action strings enumerated across 68 total
entries. 5 mapping options (A steps self-declare / B tool
attribute / C hybrid / D central registry / E evidence-only)
inventoried with tradeoffs. 20 candidate enforcement layers
enumerated. 23 identifier registries classified (7 SAFE + 11
WRAPPER + 3 UNKNOWN post-Rigby-folded). §9 F11 blind spots
capture 7 architectural categories the design mission must
confront.

**Successor gap:** Authority Enforcement Design Space (see
§5.2b below) — first mission that composes §1.6 (WHAT) + §1.7
(WHO) into an actual enforcement gate.

### 5.2a Actor Identity & Attribution Architecture — CLOSED S1271

**Closed by:** `docs/research/actor_identity_attribution_architecture.md`
(§1.7). Research shipped 2026-06-30; Rigby pressure-test
SIGN-with-edits folded. 19 identity concepts inventoried, 22
attribution surfaces classified (13 Explicit / 2 Inferred / 4
Ambiguous / 1 Unreliable / 2 Missing), 14 identity shape
changes traced, 15 historical incidents catalogued (73%
effective case), 25 identity registries classified (14 SAFE
+ 7 WRAPPER + 1 DEPRECATED + 3 UNKNOWN), 17 enforcement
boundaries. **F11 introduces the executor_actor /
sponsor_actor / principal_user 3-role vocabulary** as
normative for downstream missions — treating any single field
as "the actor" without declaring which role it represents
produces "confidently wrong audit trails" (Rigby SIGN).

**Not a gap that pre-existed §5.2 explicitly**, but implicit
prerequisite that surfaced during §1.6 verifier loops (Symbol
Mapping cannot bind action_class without knowing which actor
attempted the action). Landed as an immediate follow-on same
day rather than deferred.

**Successor gap:** Authority Enforcement Design Space (see
§5.2b below).

### 5.2b Authority Enforcement Design Space — CLOSED S1272

**Closed by:** `docs/research/authority_enforcement_design_space.md`
(§1.8). Research shipped 2026-06-30; Rigby pressure-test
SIGN-with-edits folded (Medium confidence). 24 current
enforcement inputs classified; 20 candidate enforcement
boundaries (17 original + 3 SIGN-added: WebSocket / Fleet /
Spider); 12 enforcement modes with existing production
precedents for 8; 6 major design options A-F enumerated
neutrally (MissionRunner-centered / ToolDispatcher-centered /
Audit-first / Human-approval / Multi-layer / Governance-plane
composition); 33-incident historical matrix; 15 anti-patterns
(3 flagged as Tier-0 hazards: blocking all model writes,
enforcement before symbol mapping, silent enforcement); 15
prerequisites forming DAG (critical path Symbol Mapping →
Evidence Schema → Violation Event → Fallback → Layer choice →
Test Coverage + Human Review → Rollback → Per-Employee Opt-In →
Metrics Window → Trust + FP Thresholds). Named Symbol Mapping
Option Selection Design as the recommended P0 next research
per §14.1.

**Maintenance note:** §1.8 is **design-space research only**.
The 6 options A-F are enumerated for future consumption; none
is designated for implementation. Do not treat §1.8 as an
implementation greenlight — the downstream Authority
Enforcement Design Decision mission (see §14.3 in that doc)
requires Chris gate.

**Successor gap:** Symbol Mapping Option Selection Design (see
§5.2c below) — the first mission where the design space
narrows to a specific selection.

### 5.2c Symbol Mapping Option Selection Design — CLOSED S1274

**Closed by:** `docs/research/symbol_mapping_option_selection_design.md`
(§1.10). Research + design-preparation shipped 2026-07-01;
Rigby SIGN-with-edits folded (Medium confidence; recommendation
= Modify with 4 must-fix tightenings). **Recommendation:
Option E — Evidence-only mapping — as v0.** Extend a minimum
set of audit models with optional `action_class` field + all 3
actor role fields; instrument 3-5 highest-leverage producer
sites incrementally; emit `authority_action_observed` events;
NEVER blocks. Explicitly rejected Option C bundled standalone;
deferred Options A/B/D as tertiary layers pending Phase 5 E-only
telemetry. Set Symbol Mapping Event Schema Design as
recommended P0 next research per §16 of that doc.

**Maintenance note:** Option E is the v0 recommendation. It is
**not implementation** and **not enforce-mode**. Chris gates
every downstream step. §10.3.1 of that doc defines 4 graduation
triggers that force Chris re-decision within 30 days of any of:
(a) Tier-0 hazard observed ≥1 time; (b) PROHIBITED-level
violation rate > 0 per employee per 14-day window; (c) NULL rate
> 30% after Phase 4; (d) ≥90 days elapsed since Phase 5. This
prevents "E-forever cope."

**Successor gap:** Symbol Mapping Event Schema Design (see
§5.2d below) — designs the concrete event schema + producer
instrumentation contract + retention policy for Option E's
`authority_action_observed` event.

### 5.2d Symbol Mapping Event Schema Design — CLOSED S1275

**Closed by:** `docs/research/symbol_mapping_event_schema_design.md`
(§1.12). Design-preparation doc shipped 2026-07-01; Rigby SIGN-
with-edits folded (8 must-fixes + bonus #9). **Recommendation:
two-surface event stream** — `OpsRunEvent.data['authority_action_observed']`
for mission-scoped emissions + `ToolCallRecord.parameters['authority_action_observed']`
for non-mission tool calls, unified via a new
`authority_action_observed_stream` DB view (`UNION ALL`).
4 v0 emitters + 1 v0 first consumer. 21 payload fields
across 4 tiers (required / semi-required / optional / reserved).
4-value `mapping_confidence` enum {DEFINITE (emitter-local
certainty, not global truth), DECLARED (coverage-only, never
authoritative), HEURISTIC (reserved, banned), UNKNOWN}. Drift
stack: NULL-rate monitor + zero-fire audit + weighted
cross-emitter disagreement (never marks producer wrong without
adjudication) + weekly sampled-truthing loop with
`authority_mapping_correction` events + invariant validator
(I1–I7) + schema-signature check. 3 golden flows (GF-1
Documentation Manager audit, GF-2 PA-invoked `deliverable_tool.list`,
GF-3 employee_tool run_now for Bug Triage). Rollout: 5-phase
sequencing over ~10 weeks P0→exit.

**Maintenance note.** Design-preparation only. Not implementation.
Not enforce-mode. Every producer wire-up requires a separate PR
Chris gates. Rigby SIGN fold produced 8 must-fixes: (1) two-surface
+ UNION view replaces earlier "ambient OpsRun" mechanism; (2) drop
required `event_id`; (3) drop `notes` free-text field + downscope
`producer_version` to canary-only; (4) rename `delegator_actor` →
`caller_actor` (graph position, not 4th role); (5) reframe "5
producers" → "4 emitters + 1 consumer"; (6) rename `INFERRED` →
`DECLARED` + non-authoritative label; (7) add sampled-truthing
loop for stable-wrong-non-NULL detection; (8) `DEFINITE` ≠
canonical truth (weighted disagreement, not "producer X is
wrong" verdict). Bonus #9: reserved-keys policy + per-field caps.

**Successor gap:** Trust Propagation Model (§5.3) or Employee
Boundary Escalation Contract (§5.4) — both P1 at S1275 close.
No P0 sits in front of them; Chris picks the next STAGE.

### 5.2e Symbol Mapping v0 Implementation (P1 — post Chris sign-off on §1.12)

- **Why it matters.** §1.12 pins the schema; §5.2e is the
  first implementation session (not research). Rollout §15 of
  §1.12 outlines 5 phases (P0 schema + invariant validator; P1
  Emitter #1 MissionRunner preflight; P2 Emitter #2 step
  lifecycle + Step.action_class; P3 Emitter #3 ToolDispatcher +
  tool-schema action_class; P4 Emitter #4 employee_tool run_now
  + Consumer C1 Bug Triage step 4). Estimated 10 weeks P0→exit
  observation window.
- **Priority.** P1 (post-research). Blocked until Chris ratifies
  §1.12 as canonical.
- **Dependencies.** §1.12 canonical sign-off; `EMPLOYEE_OS_PRIMITIVES.md`
  §2 anti-duplication mandate; new `JobContract.mission_trigger_action_class`
  field + new `Step.action_class` attribute + new
  `pa_tool_schemas.py` per-tool `action_class` field.
- **Expected outcome.** 5 sequential PRs mapping to §15
  phases. Each PR carries greppable log lines +
  `verify_authority_action_observed_claims` management command
  registrations. No PR ships without golden-flow tests.
- **Type.** Implementation (not research). §1.12 is the last
  research artifact in the Symbol Mapping arc.

### 5.3 Trust Propagation Model (P1)

- **Why it matters.** S1264 shipped `authority_contract_observed`
  in warn-mode only. Per `mission_runner.py:264-894`, the event
  emits shape evidence but **never blocks**. Every research doc
  in this library has hit "but warn-mode doesn't enforce" as a
  boundary. Cross-employee dispatch is the first surface where
  the boundary actually matters.
- **Priority.** P0 next research mission per §1.3's §11
  recommendation. Rigby SIGN-clean on that recommendation.
- **Dependencies.** §1.3 (esp. §10 Q11), `mission_runner.py:258-275`,
  `docs/handoffs/SESSION_1264_*.md`,
  `core/employees/jobs.py:489-505` (Platform Auditor
  authority dict shape).
- **Expected outcome.** A research doc that scopes the
  symbol-mapping work needed to take authority strings (like
  `"recommend_remediations"`) and bind them to runtime symbols
  (tool names, FK methods). Plus trust-propagation primitives
  (when Employee A trusts Employee B's verdict, what's the
  contract?). Plus boundary cases (what happens when an
  authority contract changes mid-run?).

### 5.4 Memory Architecture (P1)

- **Why it matters.** Employees do not "remember" each other's
  past verdicts in their reasoning today. Bug Triage *queries*
  OpsRun rows from other employees (read-only composition), but
  there is no synthesized memory layer — no "last week the
  Auditor flagged this same finding" awareness inside the
  reasoning context. Derived from §1.3 §1 Finding F4 (no
  in-platform A→A reply contract today) — memory naturally
  falls out as a sub-question under trust propagation once
  inter-employee read-of-other-employee semantics exist.
- **Priority.** P1. Probably falls out of the Governance + Authority
  research naturally — but if it doesn't, it deserves its own
  pass.
- **Dependencies.** Governance research (above);
  `core/models_agent_memory.py` (current per-agent memory shape).
- **Expected outcome.** A doc that maps the existing
  `AgentMemory` / `AgentLearning` / `LearningInsight` /
  `SharedKnowledge` primitives, identifies whether they're
  shared-readable across employees, and proposes (research-only)
  what a "cross-employee episodic memory" layer would reuse vs.
  invent.

### 5.5 Cross-Employee Scheduling (P1)

- **Why it matters.** Per §1.3 §1 Finding F4 and Q8, the
  minimum missing runtime surface for inter-employee delegation
  is **a durable "subscribe-to-(employee, verdict)" primitive**
  that routes verdicts to a target employee's *next mission's
  preflight*. Today's AgentFollowupSubscription handles
  conversation-scoped wakeups, not mission-to-mission handoffs.
- **Priority.** P1 — depends on Governance research closing
  first because authority semantics gate the dispatch.
- **Dependencies.** §1.2 (protocol sketch), §1.3 (§2 rows 27-29).
- **Expected outcome.** A research doc that scopes whether the
  primitive is (a) a new model, (b) an extension of
  `AgentFollowupSubscription`, or (c) a pure read-side query
  pattern. Not a design — just the scope of the smallest
  missing piece.

### 5.6 Mission Composition (P1)

- **Why it matters.** Per Rigby S1268 review architectural-blind-
  spot note (folded into §1.3 §10 Q12), the two durable
  orchestration paths (Celery chain vs. MissionRunner step
  loop) don't compose. When a future mission needs to chain
  Celery tasks across employees, the canonical idempotency key
  across substrates is an open question — calendar-date scope
  (MissionRunner) vs. task_id (Celery) vs. event_id (EventBus)
  vs. UUID (AgentExecution) don't reconcile.
- **Priority.** P1 — touches Reliability + Observability if
  done poorly.
- **Dependencies.** §1.3 (Q12), `topics/celery-workers.md`.
- **Expected outcome.** A doc that names the canonical
  idempotency key (or proves none exists and what would have to
  give).

### 5.7 Observability / Failure Recovery (P2 — already strong)

- **Why it matters.** Observability is well-covered by §1.3 §6
  (evidence-and-auditability scoring). Failure recovery is
  well-covered by §1.3 §7 (29 documented failure modes).
- **Priority.** P2. Most failure classes are already
  documented with mitigations. A dedicated doc would be a
  consolidation pass, not new research.
- **Dependencies.** §1.3 §6 + §7; `docs/AUDIT_FINDINGS.md`.
- **Expected outcome.** Optional consolidated "failure
  taxonomy" doc that pulls the §7 incidents into a single
  reference. Not blocking.

### 5.8 Security Model / Permission Model (P2 — needs scoping)

- **Why it matters.** Service-token auth is referenced
  (`core/auth_middleware.py:113` only documents
  `PA_DB_HEALTH_RPC_TOKEN`), but the full scope of
  dispatch surfaces requiring auth is UNKNOWN per substrate
  audit §9 Q3. Cross-fleet messaging requires this answered.
- **Priority.** P2 — only blocking if a future research
  mission wants to cross fleet boundaries.
- **Dependencies.** TBD; needs an initial scoping pass to
  even know what to audit.
- **Expected outcome.** First a *scoping* doc (one page) to
  identify which surfaces need auth; then full research if the
  surface is non-trivial.

### 5.9 Configuration Architecture (P3 — possibly out of scope)

- **Why it matters.** Feature flags
  (`RIGBY_EVENT_INTAKE_ENABLED`, `MESSAGING_TOOL_ALLOW_SEND`,
  `CTO_DIAGNOSTIC_ENABLED`, `COO_DIAGNOSTIC_ENABLED`) are
  scattered. There may be an implicit convention but no
  documented one.
- **Priority.** P3 — UNKNOWN whether this needs research or
  just a one-page note in
  `docs/00-START-HERE/DOC_LIFECYCLE.md`.
- **Dependencies.** TBD.
- **Expected outcome.** Either a one-page convention note OR
  a scoping doc.

### 5.10 Knowledge Graph (P? — not raised yet)

- **Why it matters.** Mentioned in the mission spec as a
  candidate. Not raised in any prior research. No production
  evidence found for a knowledge-graph layer today.
- **Priority.** P? — premature. Surface only if a future
  research mission has a specific use case for it.

### 5.11 Focus Mode Inventory (P? — flagged by Rigby S1269 review)

- **Why it matters.** Rigby's S1269 review on §1.4
  noted that **"focus mode"** is a governance-like throttle
  that may live outside the GovernanceState/KillSwitch plane.
  §1.4 didn't scope focus mode (wasn't part of the original
  evidence sweeps). A follow-up scoping pass should determine
  whether focus mode is a fifth governance plane, a sub-feature
  of one of the existing four, or a distinct concept entirely.
- **Priority.** P? — depends on whether Employee OS reasoning
  has any dependency on focus mode state. If not, deferred.
- **Dependencies.** §1.4 (governance audit's §10.8 flags it).
- **Expected outcome.** A scoping doc (one page) to identify
  the surfaces, NOT a full audit.

### 5.12 Revenue / Outreach / Engagement Pipeline Canonical Architecture (P0-parallel — added S1273 v5 per Rigby review)

- **Why it matters.** Rigby's S1273 review on §1.9 caught this
  as a missed whole-platform domain — it exists in tools/models/
  services but is not represented as an end-to-end platform
  subsystem with a canonical architecture doc. Missing this
  research means any revenue-adjacent feature has no baseline
  to work from.
- **Priority.** P0 (parallel with §5.2c Symbol Mapping Option
  Selection). Different scope than the Employee OS arc; runs
  independently.
- **Dependencies.** §1.9 §3.32 (domain inventory shell), §1.9
  §4.9 (cross-domain flow), models_outreach.py + models_
  engagement.py + models_meeting.py + models_close_pack.py,
  ops_autopilot/revenue.py + outreach_generation.py +
  engagement.py + impact.py, opportunity_pipeline_orchestrator.py.
- **Expected outcome.** A canonical architecture doc covering
  models + services + agents + PA tools + outbound channel
  integration + revenue-attribution logic. Verify runtime state
  vs aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_
  EMPIRE.md`, external `BILLING_MONETIZATION_SYSTEM.md`). Rigby
  SIGN review. Result: promotes §1.9 §3.32 coverage from LIGHT
  to DEEP + potentially spawns a §1.10 research doc.

### 5.13 Observability Deduplication Audit (P1 — added S1273 v5)

- **Why it matters.** Per §1.9 §5.7, the platform has 5 parallel
  execution telemetry layers (`CeleryTaskEvent`, `LLMCallEvent`,
  `AgentExecution`, `ToolCallRecord`, `OpsRunEvent`) plus 14+
  event-shaped audit models. Whether they're necessary and non-
  overlapping or duplicate is undocumented. Any future
  observability feature is guessing at the design boundary.
- **Priority.** P1. Touches every future observability feature.
- **Dependencies.** `docs/EVENT_SYSTEM_INVENTORY.md`, §1.9 §3.25,
  §1.9 §5.7.
- **Expected outcome.** Trace a single "agent executes a tool
  that calls the LLM" scenario through all 5 execution telemetry
  layers + adjacent audit tables. Recommend rationalization
  (which to keep, which to deprecate, which to merge). Rigby
  SIGN review.

### 5.14 Sports / DBAO ↔ AI Studio Integration Sketch (P1 — added S1273 v5)

- **Why it matters.** Per §1.9 §3.10 + §1.9 §4.8, the DBAO
  stack (sports/odds/betting agents + models) is
  operationally-separate from AI Studio (content/signals/
  initiatives/deliverables). `sports_odds` is not a valid
  `SignalCluster` data_type track; sports predictions do NOT
  auto-create Initiatives; betting outcomes NOT fed to
  deliberation. Resolves the platform's biggest structural
  question ("what IS Donkey Betz — one platform or two?").
- **Priority.** P1. Structural question; unblocks content-
  pipeline decisions for sports content and betting-related
  deliberation.
- **Dependencies.** §1.9 §3.10 (DBAO inventory), §1.9 §3.9
  (Signal Engine), §1.9 §3.11 (Content Pipeline), §1.9 §3.12
  (Initiative Pipeline), §1.9 §4.8 (Sports flow).
- **Expected outcome.** Research doc documenting whether and how
  MLPrediction / PlacedWager / SharpAction outcomes should feed
  Signal / Initiative / Deliverable surfaces. Alternative:
  documented intentional island. Rigby SIGN review.

---

## 6. Research Principles

The principles below are extracted from the three S1268 docs
and the verifier-loop pattern they all share. They are not
opinion — they are what *worked* on the first three docs,
verified by Rigby's SIGN reviews.

1. **Evidence before opinion.** Every claim in a research doc
   carries a file:line cite or is marked UNKNOWN. There is no
   third option. "I think the system does X" without a cite is
   forbidden.
2. **Inventory before implementation.** Before you can propose
   a primitive, you must list the existing primitives that
   already cover the same surface. Anti-duplication is load-
   bearing per `EMPLOYEE_OS_PRIMITIVES.md` §2 + §4.1.
3. **Reuse before invention.** "Wrapper" beats "new model"
   beats "new admin UI." If a wrapper fits, the new model
   doesn't ship.
4. **Architecture before code.** Research docs exist to make
   PRs small. If a PR is small because the research is solid,
   the team has won.
5. **Document uncertainty.** When evidence is thin, mark
   UNKNOWN. Don't guess; don't fill gaps with plausible
   inference. The UNKNOWN list in §10 of each doc is the
   honest seed for the next research mission.
6. **Never silently assume.** When two doc-claims disagree
   (substrate audit said 6 EventBus streams; runtime says 8),
   the runtime wins per `DOC_LIFECYCLE.md` §2c. Flag the drift
   in the new doc; do not silently inherit the wrong number.
7. **Use verifier loops.** The doc author re-reads
   sub-agent cites by direct Grep/Read before synthesizing.
   No exceptions.
8. **Rigby independent review before architectural
   decisions.** Every research doc gets routed to Rigby via
   `tools/pa_local.sh` on the S1268 pinned conversation. The
   verdict (SIGN-clean / SIGN-with-edits / NEEDS-MORE) is
   recorded in the `verifier_loop` frontmatter field. Edits
   are folded before the doc is considered Active.
9. **Frontmatter declares lineage.** Every research doc lists
   its `companion_docs` so the dependency graph in §4 is
   reconstructable. If you don't declare your parents, you're
   not ready to publish.
10. **Authority is the only "must change" boundary.**
    Research-only missions don't touch runtime. The single
    exception: if mid-doc you discover that a prior research
    claim is wrong, the doc surfaces it (drift call) but does
    not patch the prior doc — patching happens in a separate
    pass with its own review.

---

## 7. Decision Matrix — "If you're about to work on…"

A pre-PR sanity gate. Find the row that matches your work;
read the documents in column 2 first. Skipping the read is the
fastest way to land a PR that violates the anti-duplication
matrix or re-introduces a closed failure class.

| About to work on… | Read these first |
|---|---|
| **Employee communication (anything)** | §1.1 + §1.2 + `EMPLOYEE_OS_PRIMITIVES.md` §4.7 (messaging_tool send guard) |
| **A new AI Employee** | Path B in full + `EMPLOYEE_OS_PRIMITIVES.md` §5 quick-start |
| **MissionRunner internals** | §1.3 §2 rows 17-23 + `mission_runner.py:1-230` + S1267 handoff |
| **`MissionRunnerConfig.auto_emit_verdict` semantics** | §1.3 Executive Summary item 6 (corrected by Rigby S1268 SIGN-with-edits) + §1.3 §2 row 19 + §1.3 §7 row 29 (protocol invariant change) + `core/employees/mission_runner.py:1127-1145` |
| **Governance flags or modes** | §1.4 §2.1 (full autonomy plane inventory) + §1.4 §4.6 (5 autonomy gates incl. KillSwitch UNKNOWN) + Path C |
| **Authority enforcement (vs. observation)** | §1.6 (5 mapping options + 20 boundaries) + §1.7 (17 boundaries + 3-role vocabulary) + §1.4 §3 (full lifecycle trace) + §1.4 §4.7 (authority plane gates) + §5.2b (Authority Enforcement Design Space P0 next) + S1264 handoff |
| **Anything using `JobContract.authority`** | §1.6 §2 (57 unique strings enumerated) + §1.6 §5 (mapping options A-E) + §1.6 §9 F1-F10 + §1.7 F11 + §1.7 §8.5 (executor/sponsor/principal roles) — a policy string is not a runtime symbol; do NOT assume it enforces anything today |
| **Actor identity on any new model / audit surface** | §1.7 §3.1 (22 attribution surfaces classified) + §1.7 §8.5 (3-role vocabulary) + §1.7 F11 — declare which of executor_actor / sponsor_actor / principal_user the field represents |
| **Adding `user` FK to OpsRun (or any "actor" field)** | §1.7 F1 + §1.7 F11 + §1.7 §13.1 — DO NOT ship without role clarity first; §1.7 explicitly warns adding a "user" field to OpsRun without role clarity codifies the executor / principal conflation as schema |
| **Any code using `agent_name` CharField** (ToolCallRecord / AgentExecution.owner_agent / LLMCallEvent) | §1.7 F4 (three ambiguous fields, undefined delegator-vs-executor semantics) + §1.7 §3.3 (evidence) — DO NOT assume the string is either delegator or executor; trace the call chain |
| **Any code using `runs_as_username` or `_resolve_runs_as_user_id`** | §1.7 §2.4 + §1.7 F3 (silent-None on missing User) + §1.7 F11 (this is a principal_user selector, NOT the executor_actor) — treating it as "actor" is a documented anti-pattern |
| **Duplicate Agent row risk** (any new agent-creation site) | §1.7 F5 (recurring failure class per S1263 PR #2754 + migration 0374) + `deliverable_aliases.py:33-47` (`canonicalize_agent_name` + `AGENT_NAME_ALIASES`) — must canonicalize at write time |
| **PA tool actor / user context propagation** | §1.7 §7 (17 boundaries; F6 identifies 3 structural drop points) + §1.6 §6 (20 symbol boundaries) + `tool_dispatcher.py:687-720` (`AssistantProfile.get_allowed_tools` is the ONLY canonical-actor gate today per §1.7 F7) |
| **Any authority enforcement idea** | §1.8 §9 (6 options A-F evaluated neutrally) + §1.8 §10 (15 anti-patterns incl. Tier-0 hazards) + §1.8 §11 (15-prereq DAG) — DO NOT ship enforce-mode before §5.2c Symbol Mapping Option Selection lands + Chris gates |
| **`AuthorityLevel` enum usage anywhere new** | §1.8 F1 — enum has exactly 1 runtime consumer today (shape-counter at `mission_runner.py:864-867`); adding decision-making consumer is a design-decision-scoped change |
| **New enforcement gate (INLINE)** | §1.8 F8 (LLMEnforcer fail-open precedent at `llm_enforcer.py:237-238`) + §1.8 §11 prereq #5 (fallback behavior must be explicit) — cite fail-open vs. fail-closed rationale |
| **Adding action_class to any audit model** | §1.8 §11 prereq #3 (Evidence Event Schema) + §11 prereq #4 (Violation Event Schema) — schema shape must precede any model migration |
| **WebSocket / Fleet / Spider handler that touches employee-scoped work** | §1.8 §3 rows 18-20 (added per Rigby SIGN pressure-test) — these boundaries are named but not yet mode-tabulated; design mission scope |
| **Cross-plane governance interaction (authority × autonomy × budget × human)** | §1.8 §7.5 (8 new composition questions) + §1.4 F1 (planes don't compose today) — this is deferred future research per §1.8 §14.4 |
| **KillSwitch (arming, status, enforcement)** | §1.4 §2.1 row 2 + §1.4 §4.6 (UNKNOWN row) + §1.4 §8 F3 (write-only finding) — DO NOT assume KillSwitch blocks dispatch today |
| **Budget freeze / LLM cost gates** | §1.4 §2.3 + §1.4 §8 F4 (one-way sync + desync risk) + `core/llm_enforcer.py:200-260` |
| **Human attention lifecycle (auto-approve / escalate)** | §1.4 §2.4 + §1.4 §5 (full flow + 7-condition auto-approve gate + escalation ladder) |
| **Adding any new tool to PA** | §1.1 §4.4 (handler/schema delta gotcha) + memory rule `feedback_llm_autofills_boolean_params_with_false.md` |
| **`messaging_tool` (any change)** | `EMPLOYEE_OS_PRIMITIVES.md` §4.7 + §1.1 §8 DO-NOT-REUSE row + `td_handlers_core.py:3693-3711` |
| **Mission scheduling (any new beat)** | Path E + `topics/celery-workers.md` + `EMPLOYEE_OS_PRIMITIVES.md` §4.6 (app.conf.imports requirement) |
| **Observability or audit chain** | §1.3 §6 (evidence-and-auditability scoring) + §1.3 §2 rows 7-9 |
| **Reliability / timeout / retry policy** | Path G + §1.3 §7 (rows 10, 17, 18, 19 esp.) |
| **Escalation surfaces** | §1.3 §3.5 (HAI creators) + §1.3 §3.9 (MissionRunner escalation) + §1.2 §8.1 (Auditor has no HAI creation authority) |
| **Human attention (HAI lifecycle)** | §1.3 §2 rows 38-41 + §3.5 + `core/services/human_attention_lifecycle.py:36-728` |
| **Deliverable creation / status flips** | Memory rules `feedback_deliverable_tool_use_append_for_large_payloads`, `feedback_deliverable_status_via_content_complete`, `feedback_deliverable_create_defaults_to_completed` + §1.1 §7.8 |
| **Spider → downstream work chains** | Path F + §1.3 §3.6 + §3.7 |
| **Anything that says "new model"** | `EMPLOYEE_OS_PRIMITIVES.md` §2 (anti-duplication matrix) + §1.3 §9 (anti-duplication analysis). If a row matches, you are not adding a model. |
| **Onboarding / any cross-domain scoping work** *(added S1273 v5)* | §1.9 whole-platform inventory (32-domain map + 9 cross-domain flows) — start here for shape of the system. Then dive into whichever §3.n row matches your work + cited Employee-OS-arc docs. |
| **Anything touching Revenue / Outreach / Engagement / Meeting / ClosePack** *(added S1273 v5)* | §1.9 §3.32 + §1.9 §4.9 + §5.12 (canonical architecture doc gap) — DO NOT assume the pipeline flow described in aspirational docs (`MASTER_PLAN_CREATIVE_INTELLIGENCE_EMPIRE.md`, external `BILLING_MONETIZATION_SYSTEM.md`) matches runtime; verify. |
| **Anything sports/betting-adjacent that touches content or signals** *(added S1273 v5)* | §1.9 §3.10 (DBAO inventory) + §1.9 §4.8 (Sports flow) + §5.14 (Integration Sketch gap). The two sides do NOT currently compose (`sports_odds` is not a valid SignalCluster data_type); do NOT assume they do. |

---

## 8. Architecture Timeline

The library is young. Here is the actual chronology with
influence callouts.

| When | Doc | What it added | Influenced |
|---|---|---|---|
| **S1268 P0 #1** (2026-06-30) | `employee_os_communication_substrate_audit.md` (§1.1) | First inventory of comms primitives between AI employees. 36-row table. Reuse classifications. 12 incident-class failure history. Rigby SIGN-clean. | Made §1.2 possible — the protocol sketch reused the SAFE rows directly. Also stated EventBus had "6 named streams" at line 135 — runtime is **8** per `event_bus.py:21-30`. The drift was caught in §1.3 §12 and Rigby independently corroborated it. The substrate audit text itself has **not** been amended (research-only constraint per S1268); the drift is flagged in §1.3 §12 (cross-reference + documentation drift table) and propagated forward as the canonical value. |
| **S1268 P0 #2** (2026-06-30) | `employee_os_communication_protocol_sketch.md` (§1.2) | First concrete inter-employee write path scoped (Platform Auditor → Chief of Staff). Helper signature, metadata envelope, threading model, 3-layer dedupe, terminal-gate, expires_at freshness boundary. Rigby SIGN-with-edits — 2 substantive edits folded (L3 helper-side dedupe + cadence Option A default). | Surfaced the question "but how does collaboration work *everywhere else* on the platform?" — which became §1.3. |
| **S1268 P0 #3** (2026-06-30) | `employee_os_collaboration_patterns.md` (§1.3) | Platform-wide audit. 64-row primitive inventory. 11 distinct collaboration substrates. 12 flow diagrams. 29 documented failure modes (12 new). Q1-Q8 answered. Rigby SIGN-with-edits — 1 substantive correction folded (MissionRunner verdict event is conditional, not guaranteed) + 1 architectural blind-spot note added (canonical idempotency key across orchestration paths). | Set the recommendation for the next research mission (Governance + Authority Evolution). Surfaced gaps that become §5.1–§5.7. |
| **S1268 P0 #4** (2026-06-30) | `ARCHITECTURE_INDEX.md` (this doc) | The first navigation / index doc for the research library. Establishes the corpus's identity, dependency graph, and maintenance rules. | Will be cited by every future research doc's `companion_docs`. |
| **S1269** (2026-06-30) | `governance_authority_evolution.md` (§1.4) | First architectural-discovery audit of the governance + authority surface. 63-row primitive inventory across 4 planes. 35 runtime gates. 12 governance-specific failure modes (3 new beyond S1268 collaboration audit baseline). 48 SAFE / 11 WRAPPER / 0 DO-NOT-REUSE / 0 DEPRECATED / 3 UNKNOWN. Rigby SIGN-with-edits (plane-count framing consistency, gate-count typo, two clarifications folded). | Set Symbol Mapping Architecture as the recommended P0 next research mission. Index v2 updated per maintenance rules §10.1 (this row + §1.4 + §3 domain map + §4 dependency graph + §5 gap recategorization + §7 decision matrix expansion + §9 roadmap promotion). |
| **S1270** (2026-06-30) | `symbol_mapping_architecture.md` (§1.6) | First architectural-discovery of the WHAT question. 57 unique action_class strings (68 total entries) enumerated. 5 mapping options (A steps self-declare / B tool attribute / C hybrid / D central registry / E evidence-only) with tradeoffs. 20 candidate enforcement layers. 23 identifier registries classified. 23 historical incidents (5 YES + 10 PARTIALLY + 8 NO). F1-F11 findings incl. F11 (7 architectural blind spots via Rigby SIGN). Rigby SIGN-with-edits — 2 must-fix (§8 `_AuthorityContractMalformedError` scope narrowed; §2.6 parallel-vocabulary type/shape anchor added) + 3 optional (I-S4 wording, I-S3 dual-cite, Option E disclaimer) + 2 discoverability (AssistantProfile registry, §2.4 normalization caveat) folded. | Established the "WHAT" half of the enforcement primitive. Surfaced the WHO question that became §1.7 (Actor Attribution) as an immediate follow-on same session. |
| **S1271** (2026-06-30) | `actor_identity_attribution_architecture.md` (§1.7) | First architectural-discovery of the WHO question. 19 identity concepts. 22 attribution surfaces classified (13 Explicit / 2 Inferred / 4 Ambiguous / 1 Unreliable / 2 Missing including OpsRun). 14 identity shape changes + 3 structural drop boundaries (HTTP→Celery, MissionRunner config→OpsRun, MissionRunner→Step.fn). 15 historical incidents (7 YES + 4 PARTIALLY + 4 NO — 73% effective case). 25 identity registries (14 SAFE + 7 WRAPPER + 0 DO-NOT-REUSE + 1 DEPRECATED + 3 UNKNOWN). 17 enforcement boundaries. Rigby pressure-test SIGN-with-edits, Medium confidence — 4 must-fix folded incl. **§8.5 introducing the executor_actor / sponsor_actor / principal_user 3-role vocabulary as normative** (biggest architectural risk: conflating the three into a single "actor" label). F1 + F9 language softened per Rigby. §3.5 added inventorying attribution patterns the platform does NOT ship. §9.4 Attribution-first counterargument acknowledged. §5 role-confusion framing note. | Established the "WHO" half of the enforcement primitive. Together with §1.6, closes the composite prereq. Set Authority Enforcement Design Space as recommended P0 next research (design mission that composes both). Index v3 updated per §10.1 (this row + §1.7 row above + §1.6 row above + §3 domain map + §4 dependency graph + §5 gap closure + §7 decision matrix expansion + §9 roadmap advancement). |
| **S1273** (2026-07-01) | `platform_architecture_inventory.md` (§1.9) | First whole-platform architectural inventory — the counterpart to the Employee-OS-focused §1.1-§1.8 arc. Six parallel Explore sub-agent sweeps synthesized into 32 domains (Cognition & agents: 7 / Data ingestion: 4 / Content & workflow: 2 / Revenue & GTM: 1 / Knowledge & memory: 3 / Human interface: 6 / API: 1 / Governance & ops: 4 / Infrastructure: 4). 9 cross-domain flows. 8 duplicate/overlapping system categories. Architecture Maturity Matrix rating every domain across Coverage / Maturity / Operational Health / Drift Risk / Debt Risk. 11-mission recommended research roadmap. Rigby SIGN-with-edits, Medium confidence, via fresh isolation pin `pa-02cfd3206302352f` (kept separate from shared S1270+ arc pin `pa-cbcc410b32714f60` per Chris's context-crossing directive). 6 substantive edits folded: (1) added missed §3.32 Revenue / Outreach / Engagement Pipeline domain + §4.9 flow — Rigby caught this as biggest missing platform subsystem; (2) downgraded §3.27 Auth STABLE → PARTIAL with trust-boundary enumeration; (3) upgraded §3.7 LLM Provider Registry WORKING → STABLE (core; failover missing); (4) tightened §1 Exec Summary count language; (5) added §3.31 Event Bus vs Observability separation-of-concerns paragraph; (6) expanded §9 roadmap 10 → 11 missions with Revenue Pipeline canonical architecture doc elevated to #2. | Established the whole-platform counterpart to the Employee-OS-focused arc. Chris's direction at close: "the next cleanup should be updating ARCHITECTURE_INDEX.md so this becomes the whole-platform counterpart to the Employee OS research library." Index v5 updated per §10.1 (this row + §1.9 row + §1 preamble rewrite + Path H reading path + §3 Revenue Pipeline domain row + §4 sibling-arc dependency graph extension + §5.12/§5.13/§5.14 gap entries + §7 decision matrix +3 whole-platform rows + §9 roadmap lateral research expansion referencing the 11-mission whole-platform roadmap in §1.9). Also caught + corrected v4 frontmatter drift — prior pass added Appendix C but never bumped last_verified line. |
| **S1272** (2026-06-30) | `authority_enforcement_design_space.md` (§1.8) | First design-space research — the mission that consumes S1270 + S1271 as INPUT premises and enumerates enforcement design options without picking. 24 enforcement inputs (13 RUNTIME-VERIFIED / 7 OBSERVATION-ONLY / 3 ASPIRATIONAL / 1 UNKNOWN + 8 GAPS). 20 candidate enforcement boundaries (17 original + 3 Rigby SIGN-added: WebSocket, Fleet, Spider — closing the biggest boundary-completeness gap). 12 enforcement modes with 8 existing production precedents; 4 without analog. 204-cell boundary × mode compatibility matrix (17-row form; 3 SIGN-added boundaries not yet cross-tabulated). 4-per-level AuthorityLevel semantics (16 interpretations, none chosen). 11 canonical actor-role scenarios × 3 roles + audit path. 4-plane governance composition with 8 new questions + 1 existing cross-plane touch. 33-incident consolidated historical matrix. **6 major design options A-F enumerated neutrally** (MissionRunner-centered / ToolDispatcher-centered / Audit-first / Human-approval / Multi-layer / Governance-plane composition). 15 anti-patterns (3 Tier-0 hazards: blocking all model writes, enforcement before symbol mapping, silent enforcement). 15-prereq DAG. Rigby pressure-test SIGN-with-edits, Medium confidence — 8 must-fix folded: §3 gained 3 first-class boundaries (WebSocket, Fleet, Spider); §9.0 neutrality guardrail; §9.1 + §9.2 annotation-burden failure modes; §9.6 policy-ossification risk; §8.4 rephrased separating prevent-modes from audit/warn modes; §10 Tier-0 hazards callout; §6.1 role-propagation rule of thumb; §14 P0/P1 dependency-not-preference semantics + §14.2 (i)/(ii) split. F1 (AuthorityLevel has 1 runtime consumer, a shape-counter) and F8 (LLMEnforcer fail-open precedent) are load-bearing findings. | Established the design space for authority enforcement. **First mission carrying design-space content per §9 STAGE 2 pacing note.** Set Symbol Mapping Option Selection Design as recommended P0 next research (§14.1). Maintenance note: this doc is **design-space only** — the 6 options A-F are for future consumption, not implementation. Index v4 updated per §10.1 (this row + §1.8 row + §3 domain map + §4 dependency graph + §5 gap closure §5.2b + new §5.2c + §7 decision matrix expansion + §9 roadmap advancement STAGE 2 → STAGE 3). |
| **S1274** (2026-07-01) | `DOMAIN_RESEARCH_PLAYBOOK.md` (§1.11) | **First `authority: process` doc in the library.** Codifies the S1268-S1274 methodology into a reusable playbook so future Claude Code sessions can start domain audits with short commands ("Start research group 1300: Memory") instead of 4,000-word prompts. Establishes: research group numbering (1300s Memory → 1900s Event Architecture), output-path convention (`docs/research/domains/<slug>/<session_id>_<slug>_architecture_audit.md`), 27 standard audit questions, 20-section document template with frontmatter, 6-sub-agent parallel sweep pattern, classification rules verbatim from S1274 §11 (Coverage / Maturity / Risk / Finding Type), Rigby SIGN review shape including fresh-isolation-pin practice (S1273/S1274 lesson) and grep-verification pattern (S1274 EventBus lesson), commit rules (default: don't; when Chris says "commit it": specific index-update checklist). Not routed to Rigby — process doc, not research finding. Chris explicit direction at close of drafting: "register it now and commit." | Sets the standard for research groups 1300-1900. Should be the FIRST doc a fresh Claude Code reads after `CLAUDE.md` when starting a domain audit. Distinguishing property: `authority: process` (rules for other docs), not `authority: research` (findings). Index v7 updated per §10.1 (this row + §1.11 row + Appendix E pass notes). |
| **S1300** (2026-07-01) | `domains/memory/1300_memory_domain_scoping.md` (§1.13) | **First parent-scoping doc in the library.** Opens Research Group 1300 (Memory / Knowledge / Embeddings — playbook §12 queue slot 1). Chris opened via playbook §11 short command (`Start research group 1300: Memory`) but paused before standard a-f scope-pick with directive: "Your clarification uncovered an architectural ambiguity rather than a simple scoping question. Treat this as a Phase 0 domain-definition exercise." Doc enumerates 8 candidate memory subdomains (A: Semantic Knowledge / B: Personal-Adaptive / C: Agent Working / D: RAG Retrieval / E: Docs Corpus / F: Conversational-Thread [no §3 row yet] / G: Employee OS Mission Memory [delegated] / H: Runtime Cache-Correctness). Recommends parent-with-children shape citing S1273 3-row Memory cluster + §5.4 multi-store overlap flag + playbook §2 rule 3 sub-group permission. Chris D1-D5 locked 2026-07-01: (D1) parent-with-children; (D2) Category G delegated to Employee OS 1200s arc; (D3) RAG excluded_missing_provenance finding (surfaced Rigby search_docs at S1300 open — 8 pre-filter → 7 excluded_missing_provenance + 1 excluded_mismatch → 0 for OpsRun/MissionRunner/JobContract) parked as S1301 input; (D4) P2 renamed "Memory Store Overlap Audit" → "Memory Persistence Architecture" (durability + authority frame); (D5) S1399 canonical summary planned as arc closer. Group 1300 shape: S1300 parent → S1301 RAG Lanes → S1302 Persistence → S1303 Conversational → S1304 Docs↔RAG Boundary → S1305 Runtime Correctness → S1399 summary (7 sessions). Session ENDED EARLY per Chris close directive — Phase 0 scoping only; no P1 audit in this session. Open decisions at close: (D6) S1301 launch cadence — default pause; (D7) Rigby SIGN routing on parent — default skip per playbook §9. Rigby not routed for SIGN on parent doc (scoping ≠ audit). | **First parent-scoping doc** — introduces the "parent doc gates arc shape via Chris decisions" pattern. Validates the DOMAIN_RESEARCH_PLAYBOOK.md §11 short-command workflow (first exercise). Chris directives at close: (a) commit approval given for S1300 parent + INDEX bump; (b) PR "marked ended early for core research" — Phase 0 landing only, P1 (S1301) deferred; (c) pin `pa-aa54193f240f4846` preserved for S1301 continuity (no rotation). Index v9 updated per §10.1 (this row + §1.13 row). |
| **S1275** (2026-07-01) | `symbol_mapping_event_schema_design.md` (§1.12) | **First mission in the library shipping an implementation-ready schema spec.** Closes §5.2d. Takes §1.10's Option E v0 recommendation and pins the concrete event: canonical name (`authority_action_observed`), two-surface host (`OpsRunEvent` mission-scoped + `ToolCallRecord.parameters` non-mission tool calls, unified via new `authority_action_observed_stream` DB view), 21 payload fields (7 required + 5 semi-required + 6 optional + 3 reserved), 4 v0 emitters + 1 v0 first consumer (Bug Triage step 4 is consumer, not "producer #5"), 4-value `mapping_confidence` enum (DEFINITE = emitter-local certainty *not* global truth, DECLARED = coverage-only *never* authoritative, HEURISTIC reserved+banned, UNKNOWN honest NULL), drift stack across 6 patterns (NULL rate + zero-fire + weighted cross-emitter disagreement + weekly sampled-truthing loop + invariant validator I1–I7 + schema-signature check), 3 golden flows, batch-mode v0 dashboard, 15-item out-of-scope list, 5-phase ~10-week rollout sketch. Five parallel Explore sub-agents produced: (1) 7-model audit surface inventory identifying OpsRunEvent-lacks-user-FK as largest gap; (2) 5 producer candidates ranked (35-44% authority string coverage estimate); (3) actor-role availability matrix showing ToolDispatcher has all 3 roles + S1271 F4 delegator/executor ambiguity flag; (4) action_class population confidence ranking; (5) drift/quality prior-art scan finding STRONG reuse for zero-fire (S1245) + claim-verification (S1099), NO precedent for cross-source truthing (largest gap). Rigby pressure-test SIGN-with-edits — **8 must-fixes + bonus #9 folded**: (1) drop "ambient OpsRun" for two-surface + UNION view; (2) drop required `event_id`, add optional `idempotency_key`; (3) kill free-text `notes`, downscope `producer_version` to canary-only, replace with 128B-capped `debug_context`; (4) rename `delegator_actor` → `caller_actor` (graph position, not 4th role) + explicit semantics block; (5) reframe "5 v0 producers" → "4 emitters + 1 consumer"; (6) rename `INFERRED` → `DECLARED` with explicit non-authoritative label; (7) add sampled-truthing loop (weekly N=25 per emitter × tier; `authority_mapping_correction` events; correction_rate KPI) — catches stable-wrong-non-NULL that other stack layers miss; (8) `DEFINITE` ≠ canonical truth (weighted disagreement + `suspected_mislabel` never "producer X wrong" — prevents false-positive alert cannon); bonus (9) reserved-keys policy + per-field caps + hard 1024B total cap. Rigby SIGN-clean on: warn-mode-only v0 choice; two-surface honesty over ambient-run synthetic grouping. | **First implementation-ready schema in the library.** Set STAGE 5 to Trust Propagation Model (§5.3) or Employee Boundary Escalation Contract (§5.4) — both P1 with no P0 in front. Maintenance note: §1.12 is design-preparation ONLY. Not implementation. Not enforce-mode. Rollout §15 is sequencing sketch, not merged PR. Index v8 updated per §10.1 (this row + §1.12 row + §5.2d closure + new §5.2e implementation-slot + §9 roadmap STAGE 4 CLOSED / no new P0 STAGE). |
| **S1276** (2026-07-01) | `DOMAIN_RESEARCH_PLAYBOOK.md` §1.11 — **v1 → v2 extension** | **First playbook version bump.** Restructured v1 into 7 parts / 24 sections. Formalized fifteen areas that emerged after v1 shipped across the S1268-S1275 arc and the S1300 parent-scoping experiment: (§2) research group lifecycle — parent → children → canonical summary → index update → complete, five stages with rationale for each; (§3) phase discipline — the research / design-preparation / design-decision / process / navigation / implementation split with `authority:` frontmatter field distinguishing them, Symbol Mapping arc as canonical exemplar (§1.6 research → §1.10 design-prep → §1.12 design-prep → §5.2e implementation); (§4) xx99 canonical summary convention with intra-range structure (NN00 parent / NN01-NN98 children / NN99 summary); (§5) canonical folder structure with legacy-doc grandfathering rule; (§6) self-describing metadata standard — adds `research_group`, `child_slot`, `dependencies_on`, `delegates_to`, `delegated_from` frontmatter fields with a required-fields-by-doc-type matrix; (§7) cross-reference policy — never duplicate, always reference; (§8) parent doc responsibilities — codifies the S1300 exemplar into a template (§11.1); (§10) canonical summary responsibilities — pins the xx99 template (§11.3) and rationale for the slot; (§11) three doc templates — parent + child audit + canonical summary; (§15) stage-scoped Rigby routing — table maps stage to SIGN requirement, canonical summary and design-prep get extra pressure-test questions; (§17) graduation criteria — objective checklist for `single-audit` vs `parent-with-children` groups with `not-started` / `in-progress` / `awaiting-summary` / `closed` / `stalled` states; (§18) domain dependency mapping — formalizes `dependencies_on` / `delegates_to` / `delegated_from` semantics as informational-not-blocking; (§19) generalization requirements — 13-domain verification list + anti-domain-specific-language rules + pre-audit 5-minute mental check; (§20) architecture evolution policy — the playbook is a living artifact; additive-first evolution, backwards compat, reality-wins rule mirrors DOC_LIFECYCLE §2c, formal change proposal workflow, changelog now in §20. All v1 content preserved semantically. New short commands: `Continue research group NNNN: <slot>` and `Close research group NNNN`. Chris directive at S1276 open: *"formalize the research process itself so future domain research becomes repeatable instead of prompt-driven."* Not routed to Rigby — process document, not research finding (per §15's own rule for `authority: process`). | Playbook is now the load-bearing foundation for every future domain research group. v2 makes the framework self-describing: a fresh Claude Code that reads *only* the playbook + ARCHITECTURE_INDEX + PLATFORM_INVENTORY can execute a research arc end-to-end. First playbook version bump — sets the pattern for how the framework itself evolves. Older research groups closed under v1 stay valid under v1 per §20 backwards-compat rule. Index v10 updated per §10.1 (this row + §1.11 body extension). |
| **S1274** (2026-07-01) | `symbol_mapping_option_selection_design.md` (§1.10) | **First mission in the library carrying an evidence-based recommendation Chris can gate.** Narrows §1.6's 5 Symbol Mapping options to a v0 selection. Five parallel Explore sub-agents produced: (1) 24-system runtime symbol inventory with 2 verified drifts from S1270 (REMOVED_TOOL_ALIASES 12→13; GATEWAY_TOOLS 23→22); (2) 100-cell coverage × reuse matrix (A:1/7/12, B:2/6/12, C:5/7/8, D:11/7/1 flattest, E:2/4/14); (3) drift risk ranking (A/B/C VERY HIGH; D HIGH; E MEDIUM lowest); (4) actor compatibility (E only option carrying all 3 roles end-to-end IF audit models extended); (5) failure modes + rollout + minimum viable event shape. **Recommendation: Option E — Evidence-only mapping — as v0.** Extend a minimum set of audit models with optional `action_class` field + all 3 actor role fields; instrument 3-5 highest-leverage producer sites incrementally; emit `authority_action_observed` events; NEVER blocks. **End-state (Chris-gated later):** E foundation + Option B tool schema attribute for pre-dispatch enforcement. **Explicitly rejected:** Option C bundled standalone. Rigby pressure-test SIGN-with-edits, Medium confidence, recommendation = Modify — 4 must-fix folded: (1) §8.8 tone alignment on whole-platform generalization vs. 2/4/14 matrix (Fleet/WebSocket/Spider not covered at v0 until instrumented); (2) §10.3.1 catastrophic-action graduation guardrail (4 telemetry triggers forcing Chris decision within 30 days — prevents "E-forever cope"); (3) §12.1 non-NULL misclassification drift pattern (sample-based truthing + cross-source consistency + golden-flow tests — higher-risk than producer omission); (4) §11 employee_handle vs. executor_actor clarification (employee_handle is Employee OS identity, NULL for non-mission actions; executor_actor is generalized runtime executor). Rigby SIGN-clean on: risk posture + reversibility (strongest argument); actor role separation. | **First evidence-based recommendation in the library.** Set Symbol Mapping Event Schema Design as recommended P0 next research (§16). Maintenance note: Option E is v0 recommendation ONLY. Not implementation. Not enforce-mode. §10.3.1 guardrail forces Chris re-decision within 30 days of graduation triggers. Index v6 updated per §10.1 (this row + §1.10 row + §5.2c closure + new §5.2d + §7 decision matrix expansion + §9 roadmap STAGE 3 CLOSED / new STAGE 4 Event Schema Design). |

| **S1277+S1278** (2026-07-01/02) | `RESEARCH_OPERATING_SYSTEM.md` (§1.14) + `claude_research_startup_introspection.md` (§1.15) | **Canonical process framework for every Claude Code session — superset containing the playbook.** S1276 introspection audited actual startup behavior and named P0/P1/P2 documentation gaps. S1277 drafted OS v1 (10 request classes + Level A/B bootstrap + authority hierarchy + startup contracts + templates + navigation audit + repeatability target + one-year vision + P0/P1/P2 debt + migration plan). Rigby SIGN cycle 1 (fresh pin `pa-95ce3cbf0a2aa0cc`, Medium confidence) folded 15 must-fixes: Level A/B split; minimal-context capture; prescriptive/observational labeling; OPS/DEPLOY/INCIDENT class 11 + contract §8.11; class-boundary rules (Design-Prep vs ADR / Review vs Meta / Bug vs Ops); state-reconciliation ritual §6.6; Tier 1a/1b split; Tier 5/6 disambiguator; Tier 9/10 boundary; NAVIGATION QUERY output format; META-PROCESS drift-scan; Investigation Log + Ops Incident Report templates. S1277 re-issued expanded scope (16 parts + 14 deliverables); OS extended to v2 with six new parts: Research Philosophy (stop condition + 4 anti-patterns), Context-Kit Integration (§2 ownership matrix + §2.7.1 operational cadence + §2.9 do-not-duplicate list), Documentation Ownership (§11 matrix + 6 anti-patterns), Research Contract (§13 8 mandatory fields), Completion Contract (§14 10-item close checklist + handoff template), Research Debt (§15 concept + 7 categories + defensible formula + 90-day escalation). Renumbered existing parts 3-12 + 16-19 to match spec ordering; renumber cascade introduced 13 playbook §-ref bugs (cascade prefix-matching corrupted `playbook §N` external refs). Rigby SIGN cycle 2 (fresh pin `pa-117d3edf9d7b80f8`, Medium confidence) folded 12 must-fixes: §1.2 stop-condition enforcement rule; §1.5 additional anti-patterns; §2.3 drift-tooling + entrypoint pattern rows; §2.7.1 cadence; §2.9 DOC_LIFECYCLE + playbook templates entries; §11.1 owner tightening (CLAUDE.md single-owner = Chris; 00-START-NEXT-SESSION single-owner = Claude); §11.4 zombie/shared/verification anti-patterns; §13.1 field 5 Decision + Ratifier + Deadline format; §14.7 "Open risks / landmines" handoff section; §15.1.1 seven debt categories; §15.3 defensible priority formula `severity_weight × blocking_count × (1 + age/30)`; §15.6 debt vs follow-on clarification. S1278 ratification pass: 13 playbook cross-ref cascade artifact bugs corrected (playbook §5→§3 phase discipline, §4→§2 STAGE 0, §17.4→§11.4 templates section, §19→§13 sub-agents, §12→§9 canonical Qs, §8→§6 metadata, §9→§7 cross-ref policy, §17.1→§11.1 template). §20 finalization section added: fresh-Claude confusion audit (3 blocking items — all docs-only), missing-layer verdict (none), documentation ecosystem diagram (canonical Tier 0 Runtime → Tier 10 Archive stack + 5 side channels), knowledge lifecycle mapping (no new ledger — maps to existing surfaces), research lifecycle completeness (complete + Implementation Review as P2 gap), quick-start doc (no — §0 TL;DR suffices), graduation verdict (GRADUATED — diminishing returns reached), P0/P1/P2 debt sort consolidating three prior sessions, ratification recommendation READY-WITH-MINOR-FOLLOW-UP, migration checklist for S1279, Context-Kit boundary re-evaluation. Rigby SIGN cycle 3 (fresh pin `pa-30278fb65295e74c`, **High confidence**, zero factual errors): SIGN-with-edits where edits = the 3 P0 doc-pointer follow-up items I already flagged; NO architectural changes recommended. | **Highest-authority process doc in the library.** Playbook (§1.11) is one specialization of this OS. Reading order for a fresh Claude Code: CLAUDE.md → OS §0-§5 → §5 classification → Level B contract. §1.14 OS + §1.15 introspection register the process framework foundation. Ratification READY-WITH-MINOR-FOLLOW-UP: 3 docs-only P0 items (CLAUDE.md pointer, `OPEN_ARCS.md` creation, START-HERE additions) gate CANONICAL status. Once P0 lands (S1279 or equivalent), OS becomes CANONICAL and every future Claude session executes it. Index v11 updated per §10.1 (this row + §1.14 + §1.15 + §1.11 body cross-reference to §1.14). |

| **S1301** (2026-07-01) | `domains/memory/1301_memory_rag_retrieval_lanes_audit.md` (§1.16) | **First child audit under Group 1300 Memory (parent §1.13).** Category D RAG Retrieval Lanes exclusive scope. 20-section playbook §11.2 template. Playbook §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks folded direct file reads on the mechanism claims. Traces parent §6 provenance-filter finding (8 pre-filter → 7 excluded_missing_provenance + 1 excluded_mismatch → 0 returned) to root cause: HYP-1 (migration-incomplete) × HYP-4 (never-wired-into-ingestion). Load-bearing findings: (1) `search_docs` = LOCAL keyword lane (`core.rag.top_k` on `.rag/corpus.jsonl`); `kb_tool semantic_search` = PROD pgvector lane (`core.rag_integration.search_embeddings`) — verified at `td_handlers_ops.py:5502`; the two tools are NOT parallel implementations. (2) Provenance is EXTERNAL to chunks — computed at query time from `docs/_provenance.json` (git-history-derived by `build_docs_provenance`); index has 464 UNKNOWN / 2156 docs (21.5%) per `_meta.confidence_breakdown`; filter treats "path not in index" as `excluded_missing_provenance` by design per Rigby S1145 P2 spec (`td_handlers_ops.py:82-85` docstring). (3) Two provenance systems coexist without integration — row-level `DocumentEmbedding.source_type` + `ingested_via` (migration 0044, populated at ingestion) are NEVER READ by any retrieval path (grep-confirmed 0 hits in `rag_integration.py` / `rag.py` / `scoped_retrieval.py`). (4) Prod pgvector lane bypasses the provenance filter entirely — `_filter_chunks_by_originating_session` only called from `_handle_search_docs`. (5) Two-lane selector NEVER IMPLEMENTED — playbook §12 §3.13 research question resolved as negative. (6) PA turn enrichment does NOT auto-invoke RAG — tool-call-only (grep of `unified_pa_entrypoint.py` = 0 RAG imports). (7) Silent-failure surface confirmed system-wide-in-`core/` — filter counters live only in response payload, no log/metric/alert (grep of `excluded_missing_provenance|excluded_mismatch|pre_filter_count` = 2 files matched: handler + test). (8) Combined subsystem maturity WORKING (prod STABLE + local PARTIAL individually; combined verdict dropped from STABLE due to corpus-completeness gap that neither individual-lane verdict conveys). §19 downstream routing: S1302 owns row-level provenance semantics (persistence-architecture concern); S1304 owns E↔D ingestion→retrieval handoff; Group 1700 owns filter-drop telemetry. Rigby SIGN cycle 1 on fresh isolation pin `pa-a23736a833f646cf` (owner chris, ownership match confirmed) — verdict **SIGN-clean** after fold cycle. 4 must-fix folded (MF1 denominator citation, MF2 D3 grep evidence, MF3 MISSING scope hedging, MF4 silent-failure `core/`-tree scope note). 5 nice-to-have deferrable. Verifier_loop history preserved append-only per playbook §6. | **First Group 1300 child audit; first library exercise of playbook §11.2 20-section template + §13 6-parallel-Explore sweep + §15 fresh-isolation-pin Rigby SIGN discipline.** Confirms the audit contract works end-to-end from short-command open through SIGN-clean. Next Group 1300 child S1302 Memory Persistence Architecture (Categories A + B + C) inherits the row-level provenance semantics question surfaced here as first-order scope. Index v13 updated per §10.1 (this row + §1.16 row). |

| **S1302** (2026-07-01) | `domains/memory/1302_memory_persistence_architecture_audit.md` (§1.17) | **Second child audit under Group 1300 Memory. Combined-category scope: A (Semantic Knowledge) + B (Personal-Adaptive) + C (Agent Working) per parent §5 P2 slot renamed by Chris 2026-07-01 to "Memory Persistence Architecture" (durability + write/read paths + write authority frame, not just overlap surfacing).** Playbook §11.2 20-section template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks resolved Agent 1 vs Agent 2 conflict on `MemoryPromotionService` existence (Agent 2 correct: `core/services/memory_promotion_service.py:119, :197`); disambiguated `ConversationMemory` name collision (Django at `core/models/conversations/models.py:19` vs in-process at `core/conversation_memory.py:59`) and `AgentMemory` name collision (Django at `core/models_unified_system.py:10787` vs in-process at `core/services/agent_learning_service.py:111`). **Headline finding F1 — CONFIRMED DEAD CODE.** Parent §3 flagged `spider_context['pa_content_feedback']` consumer as UNKNOWN; whole-tree grep including `ai_core/` returned 1 producer at `core/agent_router.py:766` + 0 code consumers. 14 doc references describe an intended consumer that never became code. Escalates parent §3 UNKNOWN → confirmed dead code per playbook §14 evidence rules. Session 990 producer half wired; agent-side consumer half never implemented. Analogous to S1301 §14.3 D3 "two systems, no bridge" class. **F2 — orphan write path pattern INHERITED from S1301 §14.3 D3; narrowed across three Rigby SIGN cycles.** v1 claim: ~11 fields populated at write, never read. Rigby SIGN cycle 1 (fresh isolation pin `pa-1b9f0f5264484c6b`, owner chris, ownership match confirmed) verdict SIGN-with-edits — grep-verified active readers on 3 fields removed from orphan list: `AgentKnowledgeSource.source_spider_names` (read at `core/tasks.py:3098` + `core/tasks_agents.py:3202, 3240, 3241, 3272, 3471` + `core/views_spider_intelligence.py`); `AgentKnowledgeSource.first_discovered_at` (read at `core/tasks_content.py:1893` + `core/tasks_agents.py:3236, 3265, 3938, 3953, 3980, 3994, 4008, 4305, 4323, 4348` + `core/project_intelligence_consumer.py:155, :186`); `AgentKnowledgeSource.feedback_adjusted_confidence` (read via `effective_confidence` computed property at `core/models_unified_system.py:612-613, :625-626` + `Avg()` aggregation at `core/services/project_research_bridge.py:334`). Rigby SIGN cycle 2 verdict SIGN-with-edits — 4 more `AgentMemory` fields removed from orphan list: `.source_type` + `.source_id` + `.access_count` + `.last_accessed_at` all consumed by `core/views_memory_palace.py:60` (order by `-last_accessed_at`), `:86` (listing payload return), `:113-114` (access tracking write on detail view), and source_type/source_id join to AgentExecution in `get_memory_detail`; `record_access` at `core/models_unified_system.py:11000-11001` writes both fields. Methodology tightening: language changed from "0 consumers" to "no explicit-qualified references found on the model" per Rigby's epistemic hedge (unqualified `.field` references on variables bound to the model at runtime cannot be exhaustively excluded without AST-level tracing). Rigby SIGN cycle 3 verdict SIGN-clean — one non-blocking residual folded: `AgentMemory.poison_risk_score` + `.poison_risk_factors` reclassified from orphan → narrow-consumer-safety-filter (consumed at `core/services/memory_embedding_service.py:222` via `getattr` + `:261` via `queryset.exclude(poison_risk_score__gte=0.5)`). **Final F2 classification: 5 strict-orphan fields** (`AgentKnowledgeSource.feedback_positive/_negative`; `UserAgentLearning.context_metadata` + `.last_used`; `ConversationMemory.intent` Django model — Rigby cycle 3 grep re-verified all = 0 hits on the specific model) **+ 2 narrow-consumer-safety-filter fields** = 7 total, down from v1's ~11. **Other findings:** (a) F5 — `spider_data_bridge` (named for Cat A per narrative KNOWLEDGE_RAG_MEMORY.md) writes Cat B — parent-agent direct read of `core/learning_bridges/spider_data_bridge.py:240`: `UserAgentLearning.objects.get_or_create(...)`. docs_stale terminology drift. (b) F6 — `MemoryPromotionService` (categorized under Cat C by parent §3C) writes `UserMemoryContext` (user-scoped table) at `core/services/memory_promotion_service.py:303-318`, not `AgentMemory` directly. Category-assignment drift. (c) 14-day freshness window at `core/conversation_orchestrator.py:749` verbatim `freshness_cutoff = tz.now() - timedelta(days=14)` — Session 988 origin per :747-748 comment; hardcoded magic number; no env var/setting/config surface. (d) `AgentLearningService.save_memory` at `:462-483` writes via `redis_client.hset` at :476 with no DB backup; grep for `.expire()` = 0 hits; Redis-only durability confirmed. (e) `MemoryPromotionService` scoring criteria: regex-only deterministic (`_MILESTONE_PATTERNS` at :32-47 +3 max once, `_IDENTIFIER_PATTERNS` at :51-63 +2 per type cap +6 across 11 identifier types, `_WIRING_PATTERNS` at :67-73 +2 max once, `_SECRET_PATTERNS` at :77-86 -10 hard block); thresholds hardcoded at :234 (≥7 auto-save), :237 (5-6 pending log-only); not configurable. (f) T10 HIGH severity: no write authority gate on `AgentMemory.create_memory` at `core/models_unified_system.py:11004`; no user FK, no rate limiting; MemoryPromotionService auto-saves on every PA turn. Riskiest finding per Rigby vote. **Per-category maturity verdicts:** Cat A = PARTIAL (knowledge accumulation works but no versioning + opt-in embedding silent-missing failure mode + orphaned feedback_positive/_negative); Cat B = PARTIAL (Postgres side WORKING with active `learning_source` filter at `core/services/td_handlers_ops.py:5965, 5986, 6000`; Redis side PARTIAL with loss-on-worker-recycle); Cat C = EXPERIMENTAL (downgraded from WORKING due to F1 dead-code loop — auto-promotion pipeline runs but downstream feedback consumer is broken). **§19 downstream routing:** S1303 owns Conversational / Thread Memory Cat F (`ConversationSession` ↔ `ConversationMemory` boundary); S1304 owns Docs Corpus ↔ RAG Boundary (E ↔ D); S1399 canonical summary owns row-level orphan-write pattern classification + write-authority framework anchor recommendation + `MemoryPromotionService` Cat B vs Cat C reassignment resolution + `spider_data_bridge` naming reconciliation; Group 1700 Observability owns dead-code / producer-only detection surface (F1 highest-severity example). Design-preparation ADR for write authority framework anti-pattern: NOT this audit's job (playbook §14.5 forbids implementation-in-research). | **Second Group 1300 child audit; validates the audit contract's fold discipline across three SIGN cycles.** Rigby SIGN cycle 1 corrected F2 overstatement + verified F5 by parent-agent direct-read; cycle 2 corrected AgentMemory field misclassification via Memory Palace consumer evidence + methodology tightening ("no explicit-qualified references found" replaces "0 consumers"); cycle 3 folded final poison_risk_* reclassification to narrow-consumer-safety-filter. Overall Rigby confidence: **High.** Index v14 updated per §10.1 (this row + §1.17 row). |

| **S1304** (2026-07-01) | `domains/memory/1304_memory_docs_rag_boundary_audit.md` (§1.19) | **Fourth child audit under Group 1300 Memory. Categories E ↔ D Documentation Corpus ↔ RAG Boundary exclusive boundary lens per parent §5 P4 slot ("smaller scope; benefits from §3.14 audit landing first").** 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks caught a broad hypothesis overreach from S1301 §19 D3 BEFORE Rigby SIGN: S1301 §19 D3 broadly claimed both `DocumentEmbedding.source_type` + `ingested_via` are orphan-writes; direct file:line read at `content/embeddings.py:965-973` confirms `semantic_search_sync` applies `.filter(source_type__in=['internal', 'user_upload'])` at :971 and `.filter(source_type__in=['web', 'spider', 'api'])` at :973 as `source_filter` branch (owner-model-qualified consumer) + presentation read at :1007 (`getattr(embedding, 'source_type', 'unknown')`). Only `ingested_via` remains F1-CANDIDATE orphan — all 3 write-sites use fixed string constants (`'sync_docs'` at `sync_docs_index_to_documents.py:394` / `'backfill'` at `core/tasks_agents.py:4223/4290/4351` / `'unknown'` default at `content/embeddings.py:654/753`) with zero owner-model-qualified read consumers per grep + admin.py + serializers.py verification. F1-CANDIDATE status pending §19 R1 full-tree recheck per S1303 §14 F4-CANDIDATE discipline (dead-code claim requires owner-model-qualified consumer inventory, not keyword grep). **Load-bearing findings:** (1) Two RAG lanes confirmed with distinct provenance mechanisms — `search_docs` (LOCAL keyword) at `td_handlers_ops.py:5468` reads external `docs/_provenance.json` for `originating_session` filter via `_load_provenance_docs()` at `:78-93` (per-process `@lru_cache(maxsize=1)`); `kb_tool semantic_search` (PROD pgvector) reads row-level `source_type` via `semantic_search_sync` at `content/embeddings.py:965-973`. (2) `refresh_docs_corpus` beat task at `core/tasks.py:5803` scheduled daily at 04:00 Denver via sole `refresh-docs-corpus-daily` entry at `core/celery.py:495-499` runs `build_docs_index` (`:5900`) + `build_rag_corpus` (`:5901`) + `sync_docs_index_to_documents` (`:5902`) + fans out step 4 embed tasks — **does NOT include `build_docs_provenance`.** D6 HIGH: provenance rebuild is manual-only. (3) `lru_cache(1)` staleness at `td_handlers_ops.py:78-93` — no invalidation mechanism; workers serve stale filter results until process restart. Combined with D6, canonical E→D write-side/read-side sync drift. (4) 21.5% corpus-completeness gap (464 UNKNOWN / 2156 docs per `docs/_provenance.json._meta.confidence_breakdown`) — inherited from S1301 §14.2; root cause is docs predating the session-NNNN convention (introduced Session 1144) OR bulk commits lacking session attribution. Not a filter mechanism bug — provenance-index-completeness signal. (5) Cat F ↔ Cat D wiring: PA turn enrichment does NOT auto-invoke RAG (S1304 grep verifier confirmed 0 matches for `search_docs|kb_tool|semantic_search|search_embeddings` in `unified_pa_entrypoint.py`). Reframed as **§19 R5 design-decision** (NOT drift or wiring PR) — 3 signals tilt intentional-separation (design discipline in 8 non-RAG enrichment services, tool-call-only pattern with two first-class PA tools, thread-memory vs source-memory scope discipline, no event-driven turn-signal wiring), 3 signals tilt drift (no design comment, no feature flag guarding absence, asymmetry with `BaseAgent._get_relevant_knowledge_for_task`). Requires product/architecture verdict on operational cost, migration risk, future retrieval requirements. (6) Documentation Manager `AIEmployee` handle at `core/employees/jobs.py:187-395` (registered `:1336` as `docs_manager`, employee_handle=`rigby`, `mission_run_kind=docs_cascade`) explicitly owns cascade steps 1-4 per `daily_routine` (`:222-231`) + authority set (`:238-250`). **§18 refined:** four specific boundary-maintenance responsibilities (provenance rebuild cadence, cache invalidation strategy, filter counter observability, row-level `ingested_via` consumer strategy) have "no explicit named runtime owner" per bounded-language refinement (SIGN cycle 1 fold #2 softened "CRITICAL" → "HIGH"). (7) Two provenance systems reframed as **complementary, not duplicate** via S1302 §17.3 name-collision-as-methodology — external JSON encodes session origin (LOCAL keyword lane); row-level `source_type` encodes source-of-record enum (PROD pgvector lane); `ingested_via` was over-designed for a retrieval consumer that never materialized. Fold #4 adds "complementary today does not imply optimal" guardrail — unification vs explicit scoping is an open design decision routed to §19 R2. (8) `td_handlers_ops.py` = 6290 lines (GOD-SERVICE, exceeds playbook §13 3000-line threshold); `doc_claim_verification.py` = 3275 lines (GOD-SERVICE CANDIDATE, cohesive registry + lazy imports justify current size). **Per-component maturity verdicts:** ingestion cascade PARTIAL (operates daily on beat; step 4 async fan-out not gated by beat completion; hash-delta gating edge-case fragile); provenance filter WORKING (mechanism sound but 21.5% UNKNOWN input coverage + counters lack operator visibility + cache staleness gap); row-level provenance write path EXPERIMENTAL (`source_type` wired to `semantic_search_sync`; `ingested_via` F1-CANDIDATE pending §19 R1 full-tree recheck); E↔D boundary as a whole PARTIAL (functional but not mature; ownership undefined for boundary-maintenance responsibilities; provenance rebuild unscheduled; cache invalidation absent; observability response-only; cascade documentation unpublished). **§19 downstream routing:** R1 full-tree `ingested_via` F1-CANDIDATE verification per S1303 §14 discipline (HIGHEST priority follow-on); R2 provenance-system reconciliation design (unify or explicit scoping) → S1399 canonical summary + S1302 P2 arc handoff; R3 rebuild cadence + cache invalidation design (add to beat OR file-watcher OR Redis TTL) → Cat E docs-governance owner; R4 boundary ownership assignment (expand Documentation Manager authority OR create distinct boundary employee OR delegate observability to Group 1700) → S1399 canonical summary; R5 turn-context → RAG enrichment design decision (canonicalize separation vs implement enrichment) → design-preparation phase post-S1399; R6 publish `docs/topics/docs-ingestion-cascade.md` → Cat E docs-governance owner; R7 filter-drop telemetry (log emit + Prometheus counter + Grafana surface + threshold alert) → Group 1700 Observability arc; R8 S1301 follow-up classifier precedence bug (standalone bugfix, NOT blocking Group 1300 arc). Rigby SIGN cycle 1 on fresh isolation pin `pa-2614a91a920642fa` (owner chris, ownership match confirmed) — verdict SIGN-with-edits with 4 must-fix folds: (fold #1) D6 beat-schedule positive citation — added `core/celery.py:495-499` sole `refresh-docs-corpus-daily` entry with 4-line dict quote + `core/tasks.py:5900-5902` cascade call sites showing NO `build_docs_provenance` call, no bare "grep returned 0" as sole justification; (fold #2) §18 UNOWNED reframed with Documentation Manager JobContract positive evidence at `core/employees/jobs.py:187-395` + refined ownership matrix acknowledging cascade steps 1-4 ARE owned; four specific boundary-maintenance responsibilities remain "no explicit named runtime owner"; softened "CRITICAL" → "HIGH" per playbook §12 bounded-language rule; explicit bounded-language check paragraph; (fold #3) F4-CANDIDATE discipline reinforced on `ingested_via` — §9 D→E edge cell rewritten to hedge, §14 D7 explicit F4-CANDIDATE hedge added, no bare "never read" language remaining on `ingested_via`; (fold #4) §17 "complementary" reframe augmented with explicit "does not imply optimal" guardrail + unification-vs-scoping design-decision routing to §19 R2. Rigby-caught bonus: additional `source_type` consumer citation at `content/embeddings.py:904` (async-path SearchResult presentation) flagged as nice-to-have, not SIGN-blocking. Rigby SIGN cycle 2 verdict SIGN-clean — verification pass confirmed all 4 folds via direct code reads; no structural rewrite; ready for Chris commit-gate per playbook §16. **Load-bearing methodology inheritance:** F1-CANDIDATE discipline for `ingested_via` orphan claim inherits S1303 §14 F4-CANDIDATE methodology + S1302 §17.3 name-collision-as-boundary-methodology + S1301 §19 downstream routing invalidation pattern (partial invalidation via verifier-loop prevents sibling-audit hypothesis propagation before hardening into library-wide false consensus). | **Fourth Group 1300 child audit; first boundary-lens integration audit in the library.** Second child audit to reach SIGN-clean in 2 cycles (matching S1303 discipline; S1301 = 1, S1302 = 3). Sets the pattern for future boundary-focused audits: catch broad hypothesis overreach from sibling audits parent-side first (via direct file:line verification), so SIGN cycles focus on substantive additions instead of evidence corrections. Partial invalidation of S1301 §19 D3 demonstrates the verifier-loop pattern preventing sibling-audit hypothesis propagation. Index v16 updated per §10.1 (this row + §1.19 row). |

| **S1305** (2026-07-01) | `domains/memory/1305_memory_runtime_correctness_audit.md` (§1.20) | **Fifth (and final) child audit under Group 1300 Memory. Category H Runtime Memory Correctness NARROW scope per parent §5 P5 slot — Redis-loss on worker recycle + `@lru_cache(1)` staleness drift class only.** 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop pre-SIGN corrections applied to 4 sub-agent claims BEFORE Rigby: (v-l-1) Agent 6 "CRITICAL" severity on `AgentLearningService` Redis-only durability DOWNGRADED to MEDIUM per Redis AOF context (`settings.py:944 REDIS_APPENDONLY=True` + `:945 REDIS_APPENDFSYNC='everysec'`) matching S1302 T3 sibling classification; (v-l-2) Agent 6 "13 `cache.set(timeout=None)` sites" corrected to 5 production `core/` runtime (excluded 7 test-only + 2 subprocess-timeout `_run_ffmpeg` non-cache-set calls); (v-l-3) Agent 6 "3 disjoint Redis DBs" corrected to 4 (missed Celery broker DB 2 + results DB 3 split); (v-l-4) Agent 1 vs Agent 2 conflict on `search_docs` cache location resolved (Agent 2 correct: `search_docs` itself has NO LRU; only `_load_provenance_docs` called from it has the LRU at `td_handlers_ops.py:78`). **Load-bearing findings:** (1) Exactly 4 `@lru_cache(maxsize=1)` sites in `core/services/` grep-verified 2026-07-01 — `_load_provenance_docs` at `td_handlers_ops.py:78` (S1304 D2 anchor); `_cached_primary_workspace_id` at `platform_config.py:89`; `_cached_primary_user_id` at `platform_config.py:133`; `_load_config` at `fleet_routing.py:64`. Only `platform_config` pair has explicit invalidation contract via `clear_config_cache()` at `:223`; other two rely on worker-restart discipline. §14 D7 S1305-new (LRU staleness class extension of S1304 D2). (2) 5 production `cache.set(..., timeout=None)` sites within scope after Rigby SIGN cycle 1 tightening — `core/tasks.py:5936` (docs corpus index hash), `core/memory_system.py:54, :55, :176` (index + embedding-index + embedding-data), `core/services/discord_bot.py:9723,9728` (Discord bot config, out of memory-scope). §3 excluded-from-count table enumerates 6 excluded categories (subprocess-timeouts, tests, mock fallbacks, archive) with reasons. §14 D10 S1305-new. (3) `AgentLearningService` within-process consistency gap **CONFIRMED via direct file:line read + Rigby SIGN cycle 1 reinforcement** — `get_user_memory` at `agent_learning_service.py:415` short-circuits to `_user_memories[key]` BEFORE Redis on hit; `save_memory` at `:476` writes Redis via `hset` but never touches the dict; grep for `self._user_memories.clear` / `del self._user_memories` = 0 hits on the save path. Distinct from S1302 T3 cross-process recycle-loss. §14 D4 S1305-new. (4) `MemorySystem` at `core/memory_system.py:54-55, :176` writes `timeout=None` creating index → data divergence risk under Redis LRU eviction (`REDIS_MAXMEMORY_POLICY='allkeys-lru'` at `settings.py:942`). Rigby SIGN cycle 1 grep confirmed `MemorySystem` IS active — instantiated at `ai_core/agents/intelligent_job_matcher.py:57 self.memory = MemorySystem()`. §14 D5 S1305-new. (5) 4-DB Redis topology (DB 1 Django cache at `settings.py:452 RedisCache + LOCATION=REDIS_URL`; DB 2 Celery broker at `:802`; DB 3 Celery results at `:803`; DB 5 `AgentLearningService` hardcoded at `agent_learning_service.py:145`). `django.core.cache.cache.clear()` operates on backend DB 1 only; `AgentLearningService` uses raw `redis.Redis(**self.redis_config)` at `:160` bypassing Django cache framework — DB 5 state invisible to `cache.clear()`. §14 D8 S1305-new. Also `docs/topics/infrastructure.md` says "3 DBs" — doc drift; actual is 4. §14 D9. (6) `search_docs` PA tool has NO dedicated LRU cache — only `_load_provenance_docs` called from it. Parent §3H bullet "search_docs `lru_cache(1)` per-process" is imprecise; cache is on the provenance loader, not `search_docs` itself. §15 T12. (7) `MemoryPromotionService` has NO runtime cache surface — Agent 2 verified pure DB I/O (0 hits for `@lru_cache`, `@cached_property`, module-level memoization). Closes parent §3H "MemoryPromotionService runtime cache UNKNOWN." (8) Cat H ↔ Cat F integration MISSING — grep for `@lru_cache` in `conversation_orchestrator.py` = 0 hits; 14-day freshness cutoff at `:749` is a Cat F correctness boundary, not a Cat H cache surface. **Per-surface maturity verdicts:** `EmbeddingService` STABLE (bounded 7-day TTL, deterministic contract); `platform_config` LRU pair WORKING (invalidation contract explicit via `clear_config_cache()`); `_load_provenance_docs` PARTIAL (works with worker-restart discipline; no automation); `AgentLearningService` PARTIAL (works when Redis healthy; degrades silently on cross-process race + within-process staleness); `MemorySystem` EXPERIMENTAL (unbounded index + no lifecycle; index → data divergence possible); `fleet_routing._load_config` PARTIAL (deploy-restart contract; test-only invalidation). Category H as a whole: **WORKING with drift.** **§19 downstream routing:** R1 `platform_config` LRU D6 F4-CANDIDATE verification per S1303 §14 discipline (owner-model-qualified consumer inventory for Django admin / raw ORM / mgmt-command mutation paths); R2 Cat H remediation design-preparation per surface per S1304 T2 option set (worker-restart trigger vs file-watcher vs Redis-queryable vs TTL) → post-S1399; R3 beat-schedule audit for cache-refresh cadence gaps beyond `build_docs_provenance` (extends S1304 D6 pattern); R4 Cat H ↔ Cat B integration lens (`AgentLearningService` Redis-only durability + TTL policy + DB writeback design decision — fixes T3 + T4 + T7 together); R5 worker-recycle instrumentation → **delegate to Group 1700 Observability**; R6 `IntelligentJobMatcher` production invocation audit (post-Rigby-cycle-1-reshape — routes T5 severity assessment); R7 full `@lru_cache` sweep across `core/`, `ai_core/`, `content/` (completes Cat H surface enumeration); R8 doc-drift fix on Redis DB count `docs/topics/infrastructure.md` 3 → 4. Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-56a527a2c5528508` (owner chris, ownership match confirmed) → verdict **SIGN-clean** after 3-must-fix fold (cycle 1) + verification pass (cycle 2). Cycle 1 folds: (F1) §3 `cache.set(timeout=None)` scope definition + excluded-from-count table added; (F2) §7.2 gap (a) reinforced with direct file:line evidence — `get_user_memory:415` short-circuit + `save_memory:476` Redis-only write + grep-for-invalidation = 0 hits; (F3) §14 D8 Redis DB isolation tightened with Django cache backend citation (`settings.py:452 BACKEND` + `LOCATION`) + raw redis client citation (`agent_learning_service.py:160`). Bonus fold: §19 R6 reshaped from "verify MemorySystem is used" (Rigby-answered: yes) to "verify IntelligentJobMatcher production invocation paths" — same effort, higher-leverage. Cycle 2 verification pass — Rigby SIGN-clean High confidence; one optional micro-tighten flagged (§3 excluded-row rendering) but NOT blocking. Pin retired at close per Chris commit-gate directive (`updated_count: 2, retired: true`). Verifier-loop history preserved append-only per playbook §6. | **Fifth (and final) Group 1300 child audit; closes the 5-child arc (S1301-S1305).** Third child audit to reach SIGN-clean in 2 cycles (matching S1303 + S1304; S1301 = 1, S1302 = 3). Also **first library audit to explicitly downgrade a sub-agent severity claim via sibling-inherited context** — Agent 6 "CRITICAL" AgentLearningService durability claim downgraded to MEDIUM by Redis AOF context (settings.py:944 REDIS_APPENDONLY=True) matching S1302 T3 sibling classification. Extends the verifier-loop pattern from hypothesis-correction (S1304 partial invalidation of S1301 §19 D3) to severity-correction (S1305 §14 D3 downgrade). Group 1300 arc now closable via S1399 canonical summary next session — S1305 provides Cat H input material for the cross-cutting synthesis. Index v17 updated per §10.1 (this row + §1.20 row). |

| **S1399** (2026-07-01) | `domains/memory/1399_memory_canonical_summary.md` (§1.21) | **Arc-closing xx99 canonical summary for Research Group 1300 Memory / Knowledge / Embeddings.** Consumes S1301-S1305 child audit outputs per playbook §11.3 11-section canonical-summary template + bounded-work rule (no §13 6-parallel-Explore sweep launched; no new file:line evidence produced; every claim cites source-audit §-anchor via SNNNN §NN.N notation; CANDIDATE claims preserved rather than resolved to CONFIRMED per S1303 §14 F4-CANDIDATE discipline). **Rigby SIGN cycle 1 on fresh isolation pin `pa-4fc3329d0db6484f`** (owner chris, ownership match confirmed) → verdict **SIGN-clean** at **High confidence, 0 must-fix**, 1 optional nice-to-have (docs↔code naming/category drift micro-pattern acknowledged in §4.5 addendum as adjacent evidence rather than promoted to formal F5 — preserves the 4-pattern set named at S1305 close per parent §5 P6 rationale; Rigby explicitly said "not required if you want to keep exactly four"). All 4 pressure-test questions PASS: Q10 child contradictions resolved; Q11 anchor-update recommendations complete; Q12 cross-cutting patterns not missed; Q13 follow-on queue rankings defensible. **Load-bearing content:** (§3) Consolidated Cat A-H domain shape matrix + Redis 4-DB topology table + two-provenance-systems complementary-not-duplicate table + two-RAG-lanes-no-runtime-selector diagram + 4 `@lru_cache(1)` sites enumeration + 8-row load-bearing consequence table. (§4) **Four cross-cutting patterns named:** F1 provenance-filter drift class (S1301 §14.2 21.5% coverage gap + S1304 §14 D2/D6 lru staleness + cadence unscheduled + S1305 §14 D1 LRU class extension); F2 row-level orphan-write pattern (S1301 §14.3 D3 hypothesis + S1302 §14.3 F2 narrowed 11→7 fields across 3 SIGN cycles + S1304 §14 D3 partial invalidation of D3); F3 Redis-only durability + `@lru_cache` staleness pattern (S1302 §14 F4/T3/T4 + S1304 §14 D2 + S1305 §14 D3/D4/D5/D8 + Cat H 4-DB isolation); F4 F1/F4-CANDIDATE + severity-correction discipline as inheritance methodology (S1303 §14 F4-CANDIDATE + S1304 §14 D7 + S1305 §14 D6 F4-CANDIDATE + S1305 §14 D3 severity-correction extension). (§5) **Five contradictions resolved:** (5.1) S1304 §14 D3 partial-invalidates S1301 §19 D3 broad `source_type` orphan hypothesis via direct file:line at `content/embeddings.py:965-973`; (5.2) S1304 §17 complementary reframe of S1302 §17.3 duplicate provenance systems framing (external JSON = session origin LOCAL lane; row-level source_type = source-of-record enum PROD lane); (5.3) Agent 6 CRITICAL AgentLearningService durability claim DOWNGRADED to MEDIUM via Redis AOF sibling context (`settings.py:944 REDIS_APPENDONLY=True`) matching S1302 T3 classification; (5.4) Agent 6 "13 cache.set(timeout=None)" tightened to 5 production in `core/` runtime scope with excluded-from-count enumeration; (5.5) parent §3H bullet "search_docs `lru_cache(1)`" precision fix — cache is on `_load_provenance_docs` called from `search_docs`, not `search_docs` itself. (§7) **Anchor-update recommendations:** (7.2.1) `platform_architecture_inventory.md` §3.13 subdivision into Cat A/B/C sub-rows per S1302 findings; (7.2.2) §3.14 lane consolidation as explicit two-lane statement per S1301 findings; (7.2.3) new §3.N row for Cat F Conversational/Thread Memory (first-inventory landing per S1303 §4 + §7); (7.2.4) new §3.N or §5.N row for Cat H Runtime Memory Correctness (first-inventory landing per S1305 §14 D1-D10); (7.3) ARCHITECTURE_INDEX v17 → v18 bump plan; (7.4.1) `docs/topics/infrastructure.md` Redis DB count 3 → 4 fix per S1305 §14 D9; (7.4.2) `KNOWLEDGE_RAG_MEMORY.md` 4 targeted edits (F1 pa_content_feedback dead-code note, two-lane split explicit reference, LRU precision fix on `_load_provenance_docs`, pointer to S1399); (7.4.4) NEW `docs/topics/docs-ingestion-cascade.md` publish per S1304 §19 R6. NO direct edits to `PLATFORM_INVENTORY.md` per CLAUDE.md context-kit rule (runtime anchor, regenerable via `generate_platform_inventory`). (§8) **21-item follow-on queue ranked by uncertainty × risk × unblocked flows.** Top 5: (1) S1304 §19 R1 `ingested_via` full-tree recheck (F1-CANDIDATE hardening — deprecation hazard); (2) S1303 §19 R1.a/b/c `ChatConversation.context_used` + `.agent_results` owner-model-qualified inventory + runtime-vs-analytics-vs-UI classification + canonical-source-of-truth resolution; (3) S1305 §19 R1 `platform_config` LRU F4-CANDIDATE mutation-path audit; (4) S1305 §19 R6 `IntelligentJobMatcher` production invocation audit (routes T5 MemorySystem severity assessment); (5) S1302 §15 T10 write-authority framework design-preparation ADR (highest-severity debt in entire arc — no auth gate on `AgentMemory.create_memory:11004`). Design-preparation phase items post-S1399: Cat H remediation per surface (S1305 §19 R2); Cat H ↔ Cat B integration lens (S1305 §19 R4 — fixes T3+T4+T7 together); provenance-system reconciliation unify-vs-scoping (S1304 §19 R2); turn-context → RAG enrichment intentional-vs-drift decision (S1304 §19 R5). (§9) **Delegated arcs cross-linked:** Employee OS 1200s arc owns Cat G Mission Memory (parent §3G Chris-locked D2 2026-07-01); Group 1700 Observability owns 4 aggregated items (Cat D filter-drop telemetry S1301 R2 + Cat E↔D filter-drop S1304 R7 + dead-code / producer-only detection S1302 + EventBus adoption for Cat F S1303 R2 + worker-recycle instrumentation for Cat H S1305 R5); post-S1399 design-preparation phase owns 4 ADR/design-preparation docs; standalone bugfix follow-ups filed (S1303 R8 broken import + field mismatch, S1305 R8 doc-drift, S1304 R8 classifier bug). (§10) **Change log:** Session-by-session ledger of Rigby SIGN cycle counts (S1301 = 1; S1303/S1304/S1305 = 2; S1302 = 3; S1399 = 1); arc pin continuity `pa-aa54193f240f4846` across S1300 → S1399 (retires on Chris merge); fresh SIGN isolation pins per session enumerated with retirement schedule. **Load-bearing methodology outputs of the arc:** (a) F1/F4-CANDIDATE discipline; (b) sibling-inheritance hypothesis-correction; (c) severity-correction via sibling context. All three now qualify for playbook v3 additions per §20 two-triggers rule (each used across S1303 + S1304 + S1305). | **First formal xx99 canonical summary in the library** (S1268-S1275 arc predated the xx99 convention per playbook §22 note). Consumes prior child outputs — no §13 6-parallel-Explore sweep, no new file:line evidence, no CANDIDATE → CONFIRMED resolutions. Every claim cites source-audit §-anchor. Chris's short command `start research group 1399` proved the reduced-prompt target rhythm from playbook §11 works for arc closure. **Group 1300 arc closed** per playbook §17 graduation criteria — all 5 child audits + canonical summary shipped, SIGN-clean, committed to `main` (S1399 pending Chris commit-gate). Arc pin retires on merge. Group 1400 Revenue next per playbook §22 queue, pending Chris directive. Index v18 updated per §10.1 (this row + §1.21 row). |

| **S1303** (2026-07-01) | `domains/memory/1303_memory_conversational_thread_memory_audit.md` (§1.18) | **Third child audit under Group 1300 Memory. Category F Conversational / Thread Memory exclusive scope. First-inventory landing — no `platform_architecture_inventory.md` §3.N row existed for Cat F at audit open.** 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). Parent-agent verifier-loop spot-checks caught two Agent-6 overreaches BEFORE Rigby SIGN: F3 "would fail at import time" → verified content_writer_agent.py:74-80 try/except guard = SOFT FAIL at import; F4 "confirmed dead code, 0 reads" → CANDIDATE per memory rule feedback_verify_before_deleting_dead_code.md (keyword-grep insufficient without owner-model qualification). Consequence: audit shipped to Rigby with the two most-load-bearing evidence claims already downgraded, so SIGN cycles focused on substantive-edge additions instead of evidence corrections. **Load-bearing findings:** (1) `ChatConversation` at `core/models/conversations/models.py:59-187` is the Cat F row-per-exchange table; `conversation_id` CharField at line 76 stores the `pa-<uuid.hex[:16]>` pin (mint format at `td_handlers_core.py:3885`); `session_active` BooleanField at line 139-143 is the retire marker. (2) Turn-history reinject at `unified_pa_entrypoint.py:7277-7343` loads last 10 rows scoped to `conversation_id` (7300-7302) with 8000-char truncation (7327, post-S1085), tool-call metadata reinjected (7331-7336), fail-open on DB error (7342). (3) `session_tool.retire` at `td_handlers_core.py:4011-4072` confirmed present + working — memory rule `feedback_session_tool_retire_works.md` stands; requires `force=True` if retiring currently-bound thread (line 4035-4050); returns `{retired: True, updated_count}` (line 4061). (4) S1212 deliverable 777d9cd8 stale-thread waste (~$3.60/day) CONFIRMED RECONCILED via S1248 matched-pair fix — retire handler flips `session_active=False`; dispatcher gate at `conversation_action_dispatcher.py:288-316` blocks; enforcement is best-effort / fail-open under DB errors (317-323 try/except envelope) — availability > correctness by design (Rigby SIGN cycle 1 riskiest-finding call). (5) F3 wrong-model + wrong-field at `content_writer_agent.py:76` (imports ConversationMemory from wrong module) + `:370` (filters `memory_type__in=['success','insight','learning']` but Django `ConversationMemory` at `models/conversations/models.py:19-31` has NO `memory_type` field — that field lives on `UserMemoryContext` at `:253`); D1 debt widened to "wrong model + wrong field" — import fix alone shifts crash from import-time to query-time FieldError. (6) F4 candidate for `ChatConversation.context_used` + `.agent_results` — Rigby SIGN cycle 1 confirmed Agent-6's keyword grep catches unrelated variables (e.g., `tasks_agents.py:1262` `agent_results = phase_data.get('results', {})` = local dict in different scope); §19 R1 split into R1.a owner-model-qualified consumer inventory / R1.b runtime vs analytics vs UI classification / R1.c canonical source-of-truth (first-class fields vs `metadata` dict) resolution. (7) Cat F ↔ Cat D wiring reframed as **OBSERVED GAP + owner confirmation required** (no verified turn-context → RAG query enrichment; could be intentional separation — user-scoped vs source-scoped — or missing integration); delegated to S1304 E ↔ D boundary. (8) F7 no Cat F event stream on EventBus (0 `CONVERSATION_*` streams in `event_bus.py:21-31`) reframed as gap/partial, delegated to Group 1700 Observability. (9) F8 pin rotation policy lives ONLY in `tools/pa_local.sh` header comments (policy-in-tooling anti-pattern). (10) F9 no auto-cleanup for retired rows (no Celery task, no management command, no TTL). (11) F10 Discord unlinked-user linkage-completion signal MISSING. **Maturity verdict (post-SIGN cycle 1 bounded):** WORKING (bounded) — interactive web PA sessions with DB-backed turn reinjection are stable; PARTIAL — lifecycle hygiene, analytics completeness, and hard policy enforcement (fail-open under exceptions). Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-23a38300dd84bae2` (owner chris, ownership match confirmed) → verdict **SIGN-clean** after 12-edit fold (E1-E12) + 1-cycle verification pass. Cycle 1 folded: E1 maturity bounding, E2/E3 F3+D1 wrong-model+wrong-field widen, E4 F4 CANDIDATE rewrite, E5 R1.a/b/c split, E6 Cat F ↔ Cat D reframe, E7 Flow E fail-open nuance, E8 retire idempotency clause, E9+E10 metadata contract Exec Summary mention + new §20.9 subsection, E11 F7 gap-not-defect reframe, E12 new §20.10 draft→active gating checklist. Cycle 2 verification pass — Rigby re-read `content_writer_agent.py:330-450` + `models/conversations/models.py:1-31` and confirmed E3/E4/E5 held; no structural rewrite; SIGN-clean. **§19 downstream routing:** R1.a-c (F4 verification) as highest-priority follow-on; R2 Cat F ↔ EventBus adoption → Group 1700 Observability; R3 turn-context → RAG enrichment → S1304 (Cat E ↔ D boundary); R4 retention lifecycle for retired rows; R5 land first-inventory §3.N row via S1399 canonical summary; R6 formalize session identity mint contract (§17 duplicate mechanism — `create_fresh` `pa-<hex>` vs `get_or_create_session` `uuid4()`); R7 doc-in-tooling reconciliation (F8); R8 D1 broken import + field mismatch runtime fix. Verifier_loop history preserved append-only per playbook §6. New §20.9 "Reinjection Metadata Contract" documents 4 expected metadata keys with producer/consumer citations to prevent F4-style false dead-code claims by distinguishing model fields from metadata dict keys. New §20.10 explicit `status: draft` → `status: active` gating checklist. | **Third Group 1300 child audit; first-inventory landing in the library.** Only child audit to reach SIGN-clean in 2 cycles (S1301 = 1, S1302 = 3). Verifier-loop spot-checks caught Agent-6's two overreaches before Rigby ever saw them — sets the pattern for future audits: catch evidence overreach parent-side first so SIGN cycles focus on substantive additions, not corrections. F4 CANDIDATE discipline extends S1302's dead-code methodology by adding the owner-model qualification rule — future audits applying this pattern must not accept keyword-grep evidence for dead-code claims. Index v15 updated per §10.1 (this row + §1.18 row). |

| **S1400** (2026-07-01) | `domains/revenue/1400_revenue_domain_scoping.md` (§1.22) | **Arc-opening parent scoping doc for Research Group 1400 Revenue / Outreach / Engagement.** First application of Chris's Phase 0 F.i/F.ii/F.iii methodology (Domain Definition / Existing Knowledge Inventory / Success Criteria) at §10/§11/§12 — proposed as playbook v3 §11.1 template addition at parent §9.5. **9 Chris-locked decisions D21 + D23-D29 across three "agree all" ratification rounds 2026-07-01:** D21 (short-command launch); D23 (parent-with-children); D24 (child mission sequence A→B→C→D→E→F→xx99); D25 (F.i Category F Income/Jobs lane child audit as S1406, 9-file intelligence/ adjacency + FreelanceOpportunity + resume/matcher/pipeline surface); D26 (Ops Autopilot revenue-facing modules IN, cross-cutting primitives OUT); D27 (§15 stage table SIGN routing — Light on parent, Full on each child, Q10-Q13 canonical on xx99); D28 (Opportunity → Initiative wiring ownership assigned to Child E per Rigby Must-fix #2); D29 (Yes-two-triggers — Group 1400 pilots Phase 0 methodology; playbook v3 §11.1 promotes at Group 1500 close if second application unchanged per S1399 two-triggers threshold). **Rigby Light SIGN cycles 1 + 2 both SIGN-clean** — cycle 1 Medium confidence 0 must-fix after fold (Must-fix #1 downgraded to §Appendix fold-note; Must-fix #2 escalated to D28 lock); cycle 2 Medium-High confidence 0 must-fix (nice-to-haves #2 + #3 folded, #1 skipped as low-value). Rigby spot-verified 2 of 15 inherited-finding citations at file:line — S1274 §2.4 lines 290-294 + §14 finding #36 at line 1499 — both correct. Load-bearing methodology outputs: **F.i-F.iii 3-step framework** (5+4+4 questions + 1 group-specific artifact); **Revenue Lifecycle Traceability Table** as S1499 F.iii "done" artifact (Rigby cycle 2 addition — 8 stages minimum + 6 columns per stage + ≥3 verified writer/reader paths + F1/F2/F3/F4 diagnostic-lens verdicts + row example template at §12.5 to prevent S1499 bikeshedding). Frame outputs: 17 revenue-related Django models enumerated at §2.4 with file:line grep-verified citations (10 Opportunity variants + Outreach + 4 engagement + Meeting + ClosePack + FreelanceOpportunity across 8 files); 10+ services + 3 revenue-related agents + 9-file Income/Jobs adjacency (Chris-locked as Category F child audit); 15 inherited findings enumerated at §11.4 (S1273 §3.32 + §4.9 + S1274 §2.4 + §3.7 + §5.10 + §9.6 + §14 finding #36 + S1399 F1-F4 methodology); 7 overlap points documented at §10.4 with existing arcs. **Reframe-under-directive discipline** established: when Chris redirects a decision framing mid-conversation (D25 → Phase 0 methodology), route interpretation through Rigby to pressure-test, execute the reframe explicitly with default lean, surface the reframed decision in one card for Chris ratification. New arc pin `pa-34d43795e1b24bd3` minted; old Group 1300 arc pin `pa-aa54193f240f4846` retired via `session_tool.retire force=true` (`updated_count: 29, retired: true, previously_active: true, is_current_bound: false`). §8 timeline S1400 row added. | **First arc under Chris's Phase 0 methodology; first arc where the parent scoping doc explicitly proposes a playbook v3 addition.** Group 1400 Revenue is trigger #1 for the two-triggers threshold; playbook v3 §11.1 template addition promotes at Group 1500 close if second application unchanged. Sets the pattern for future arc opens: parent scoping doc must answer 13 explicit questions (5 F.i + 4 F.ii + 4 F.iii) + name a group-specific "done" artifact at F.iii before any child audit launches. Index v20 first-half updated per §10.1 (this row + §1.22 row). |

| **S1401** (2026-07-01) | `domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (§1.23) | **First child audit under Group 1400 Revenue (parent §1.22).** Category A Opportunity Discovery + Scoring exclusive scope per parent §10.2 evidence-surface table. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity). **Parent-Claude verifier-loop pre-SIGN corrections applied to 5 sub-agent claims BEFORE Rigby:** (v-l-1) Agent 3 "score_opportunities_from_spider_data NOT SCHEDULED" downgraded to UNKNOWN — WIREMAP.md:170 + SESSION_872_COMPLETE.md:147 + SESSION_223_OPPORTUNITY_ENGINE.md:124 all document hourly beat; PeriodicTask row existence unverifiable from source tree; (v-l-2) Agent 6 "OpportunityPipelineOrchestrator ↔ OpportunityExecutionPipeline duplication candidate" resolved as COMPLEMENTARY via Agent 2 direct read (Orchestrator = transform Dict→Dict 5-stage agent routing 1848 LOC; ExecutionPipeline = materialize Opportunity instance → PartnershipProject + CustomWorkflow 541 LOC; different signatures, different downstream side effects); (v-l-3) Agent 3 EventBus publisher line ":282, :480" clarified to primary invocation at `scoring_dispatcher.py:41` (line 41 is direct call; :282, :480 are S1274 §6.2 higher-level caller lines); (v-l-4) NEW LOAD-BEARING FINDING surfaced from direct read of `consumers_base.py:2540` — `OpportunityScannerConsumer` reads from `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` in-memory realtime source, NOT `Opportunity.objects.filter(...)` persistent model — dual opportunity representation drift. (v-l-5) NEW debt finding surfaced from direct grep of `core/settings.py` — `score_opportunities_from_spider_data` defined TWICE in `task_routes` at line 1277 (`long_running`) and line 1484 (`content`); later wins → effective queue `content` (drift-prone silent config bug). **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-16d8b24d30e7a7d8`** (owner chris, ownership match confirmed) → verdict **SIGN-with-edits cycle 1** (High confidence, 2 must-fix + 2 nice-to-have) → **SIGN-clean cycle 2** (High confidence, all 4 folds accepted). Rigby cycle 1 independently verified all 4 primary spot-check citations via `repo_tool.search` + `repo_tool.read_file`: sports lane at `sports_opportunity_generator.py:83` CONFIRMED; `intelligence_engine.get_current_opportunities()` **broadened finding from 1 to 5 consumer sites** in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597); Celery duplicate at `settings.py:1277` + `:1484` CONFIRMED; OPPORTUNITY_SCORED registry `event_bus.py:25` + `:581` + `event_handlers.py:536` CONFIRMED. Cycle 1 folds: (M1) sports lane wording — clarify "separate lane" vs S1274 MISSING so readers don't misread as "integration solved" (S1274 MISSING remains ACCURATE for mainline); (M2) §10.1 EventBus overreach — added handler registry citation `event_handlers.py:48` + payload composition `event_bus.py:581`; corrected handler action from "routes confidence 50-85% → HITL VALIDATION_REQUIRED event" to DETECTS + LOGS only per `event_handlers.py:186-188` inline comment ("HITL service will have already created the validation request"); downgraded `scoring_workers` + `analytics_workers` group claims from S1274 §6.2 to CANDIDATE (not re-verified this session); only `create_validation_worker` at `event_handlers.py:521+` region verified this session; (NH #3) §15 T5 operational consequence — added detail on why `content` vs `long_running` queue mismatch matters (different concurrency + memory profile + workload assumptions per settings.py:1268-1273 comments; 100-item ML scoring pass under content semantics may cause latency regression); (NH #4) §19 R1 + R4 collapsed into single umbrella R1 "Dual-representation + provenance contract" with prerequisite sub-task R1.0 = identify origin/lifecycle of `intelligence_engine.get_current_opportunities()`. Subsequent R-numbers shifted -1; added new R8 for T5 Celery route cleanup (Rigby "important-but-contained"). Cycle 2 Rigby verdict verbatim: "SIGN-clean (cycle 2 unnecessary; ship to Chris commit-gate). No remaining blockers based on your fold summary." Pin retired at S1401 close per playbook §15. **Load-bearing findings:** (1) sports lane resolved as SEPARATE LANE (writes `OpportunityTracking`, not mainline `Opportunity`); (2) NEW dual opportunity representation drift (5 consumer sites); (3) F1 provenance-filter drift CANDIDATE HIGH; (4) F3 Redis-only durability CANDIDATE HIGH; (5) F2 orphan-write cluster CANDIDATE HIGH on 10-variant + partnership_* fields; (6) Orchestrator vs ExecutionPipeline COMPLEMENTARY (not overlap); (7) NEW debt T5 Celery route duplicate; (8) ownership gap CONFIRMED (deferred to Child E per D28); (9) maturity WORKING (S1273 baseline preserved); (10) research coverage LIGHT (matches parent §11.3). Parent §12.1 Category A F.iii questions all 6 answered (§20.7 checklist). §19 follow-on queue 8 items ranked; R1 umbrella + R2 scoring rate telemetry + R3 producer inventory completion → Category F S1406 + R4-R7 immediate Rigby probes + R8 T5 cleanup. All 15 inherited findings from S1273 + S1274 + S1399 cited, not rediscovered (§20.8). All 28 canonical questions answered (§20.6). S1273 §10.3 UNKNOWN #1 Opportunity model location RESOLVED at `core/models_unified_system.py:1201`. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1401 row added. | **First Group 1400 child audit; validates parent-Claude verifier-loop discipline BEFORE Rigby.** First library audit where a Rigby SIGN cycle 1 grep BROADENED a NEW drift finding (dual opportunity representation) from 1 consumer site to 5 — changing follow-on from "single-consumer local bug" to "arc-wide contract question." Also first library audit where parent-Claude verifier-loop overrode a sub-agent's duplication flag via a competing sub-agent's direct code read (Agent 2 vs Agent 6 on Orchestrator ↔ ExecutionPipeline). Sports lane verdict definitively resolves parent §12.1 Q6 (SEPARATE LANE — S1274 MISSING remains accurate for mainline; refinement is wording). Sets pattern for Group 1400 remaining children: parent-Claude verifier-loop catches sub-agent overreach parent-side first so Rigby SIGN cycles focus on substantive edges. Index v20 second-half updated per §10.1 (this row + §1.23 row). |

| **S1402** (2026-07-01) | `domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (§1.24) | **Second child audit under Group 1400 Revenue (parent §1.22).** Category B Outreach Composition + Delivery exclusive scope per parent §10.2 evidence-surface table. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category B evidence surfaces (OutreachDraft model + OpportunityDraftGenerator composition path + OutreachSequencer scheduling + outbound-channel resolution + Outreach → Engagement seam + Category B docs + prior research + drift/debt/ownership/maturity classification). **Parent-Claude verifier-loop pre-SIGN corrections applied to 2 sub-agent claims BEFORE Rigby:** (v-l-1) Agent 6 named "OutreachSequencer.evaluate() handles touches 2-4 with hardcoded text"; parent-Claude direct read of `revenue.py:812-829` ELEVATED the finding: the hardcoded text is the literal string `"Draft follow-up message needed."` AND the `.objects.create(...)` call omits `opportunity=parent.opportunity` → live F2 orphan-write pattern for every follow-up row created. (v-l-2) Agent 4 named "no outbound channel wired"; parent-Claude direct read of `models_outreach.py:10` OutreachDraft docstring reframed as *docstring-vs-runtime lifecycle divergence*: the model docstring declares five states (`draft → approved → sent → replied/expired`) but the runtime state machine only implements three (`draft → {approved, rejected}` + `approved → expired`). Same evidence, sharper claim. **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-4a0a28edcb7a45ec`** → verdict **SIGN-with-edits cycle 1** (High confidence, 2 must-fix + 3 nice-to-have; storage truncated at Rigby's tool layer mid-Must-fix-#2) → **SIGN-clean cycle 2** (High confidence, 5 Q-answer folds applied + 3 nice-to-haves recorded). **Rigby ops probe mid-Cycle 1 CONFIRMED D.B7 dead-code finding** — `celery_task_history` 30d filter=outreach = 7 events all `generate_outreach_drafts_daily`; `PeriodicTask.filter(icontains='outreach')` = single row `generate-outreach-drafts-daily`; parent-Claude direct read of `core/services/td_handlers_ops.py:2699-2755` = zero PA tool action wraps `.evaluate` (only get_inbox/approve_draft/reject_draft/get_metrics_report exposed); repo-wide grep for `sequencer.evaluate`/`OutreachSequencer().evaluate` = 0 hits. **F.B4 CONFIRMED: OutreachSequencer's declared 4-touch cadence has no runtime realization — only Touch 1 fires; Touches 2–4 are dead code.** **Load-bearing findings (4, ranked by runtime severity):** (F.B1) delivery path missing CONFIRMED HIGH — grep-negative at HEAD `beda00e5` across mainline for send patterns + provider SDKs + EMAIL_BACKEND; approved drafts accumulate at `status='approved'` until 30d expiry; **S1274 §2.4 line 293 CONFIRMED and REFINED to "entire outbound channel missing, not just Inbox"** (recommended anchor-update IMMEDIATELY at S1274 per Rigby cycle 2 Q7); (F.B3) engagement feedback loop missing CONFIRMED HIGH — `EngagementEvent.outreach_draft` FK schema at `core/models_engagement.py:55-59` present, zero writer sites; Category C S1403 inherits the entire seam build-out; (F.B4) cadence declared but not realized at runtime — CONFIRMED via D.B7 probe (evidence bundle above); (F.B2) follow-up composition writer-site CONFIRMED F2 orphan-write + literal-stub pattern at `revenue.py:812-829` (code HIGH, runtime blast radius ZERO due to F.B4 dead code); CANDIDATE at repo-wide scope. **Inherited-finding resolutions:** S1273 §10.3 UNKNOWN #1 RESOLVED as single-shot LLM only (`outreach_generation.py:340-370`; no Content Deliberation, no reviewer chain; uses `get_openai_client()` factory + `gpt-5-mini` + `max_completion_tokens=4000` + `response_format='json_object'`); S1273 §10.3 UNKNOWN #2 + S1274 §2.4 line 293 RESOLVED to "entire outbound channel missing"; S1401 §14 D6 dual-representation drift RULED OUT for Category B (reads persistent `Opportunity.objects.filter(...)` only); F1 provenance-filter drift lens CANDIDATE extends to Category B reader surface; F3 Redis-only durability lens CLEAN for Category B. Cycle 2 fold outcomes: (Q3) D.B1 docstring-vs-runtime severity downgraded HIGH → MEDIUM per Rigby ("elevates to HIGH only if UI/ops relies on 5-state for compliance"); (Q5) R.B3 F1 reader-side filter narrowed from Group-1400-wide to Category-B-scoped; (Q6) T.B8 dedicated outreach queue documented NOW pre-Employee-OS (not deferred); (Q7) D.B3 anchor-update IMMEDIATELY at S1274 (not deferred to S1499 xx99); (Q9) R.B7 send-gap fence test bundled with R.B1 (not immediate). Cycle 2 3 nice-to-haves recorded for post-arc pickup: (NH-1) add provenance fields to OutreachDraft; (NH-2) rename UI/API "outreach delivery" → "outreach drafts" + add "no outbound channel implemented" banner; (NH-3) daily approved-drafts-older-than-X-days integrity report. Ownership gap CONFIRMED for Category B (deferred to Child E per D28). §19 follow-on queue 7 items ranked; R.B1 umbrella "outreach delivery subsystem design ADR" (highest priority); R.B2 follow-up composition subsystem; R.B3 F1 reader-side filter Category-B-scoped; R.B4 evaluate cadence probe RESOLVED via SIGN cycle 1; R.B5 engagement ingestion path Category C S1403 owns; R.B6 offer-configuration debt; R.B7 send-gap fence test bundled with R.B1. All 28 canonical questions answered; parent §12.1 Category B F.iii questions all 3 answered. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1402 row added. | **Second Group 1400 child audit; first library audit to CONFIRM a missing-subsystem finding at HIGH runtime severity with complete negative-grep evidence.** Also first library audit where a Rigby ops probe (`celery_task_history` + `PeriodicTask` ORM) + parent-Claude direct read jointly CONFIRMED a dead-code finding (F.B4 / D.B7 / T.B5) MID-SIGN-cycle-1 — extending S1401 verifier-loop methodology from "hypothesis correction" to "runtime-liveness confirmation via ops telemetry." Also first library audit where SIGN cycle 1 storage got truncated at Rigby's tool layer; parent-Claude reconstructed the fold pass from (a) verbatim Must-fix #1 content, (b) inferred Must-fix #2 direction (F.B1 CONFIRMED HIGH not CANDIDATE HIGH — grep-negative evidence complete), (c) D.B7 dead-code confirmation via ops probe + direct read. Cycle 2 SIGN-clean confirmed the inferred fold direction (Q3 D.B1 severity downgrade HIGH → MEDIUM was the only correction; Must-fix #2 inference verified). Sets pattern for future SIGN-storage-truncation recovery: reconstruct via combining verbatim excerpt + evidence-based inference + independent probe/read verification. Load-bearing story change: Category C S1403 inherits F.B3 as its central deliverable (not just a seam-verify) because there is no existing Engagement ingestion wiring to extend. Isolation pin `pa-4a0a28edcb7a45ec` retires post-PR-merge per playbook §15. Index v21 updated per §10.1 (this row + §1.24 row + frontmatter v21 preamble). |

| **S1403** (2026-07-01) | `domains/revenue/1403_revenue_engagement_inbound_audit.md` (§1.25) | **Third child audit under Group 1400 Revenue (parent §1.22).** Category C Engagement Inbound exclusive scope per parent §3 Cat C evidence surface + §12.1 Category C F.iii questions. 20-section playbook §11.2 template + §13 6-parallel-Explore sweep on 6 Category C evidence surfaces (4 engagement models canonicity + EngagementEngine read/write graph + EngagementAutonomyEngine gating + F.B3 ingestion path design + EngagementMetrics aggregation direction + Category C docs+prior research+drift/debt/ownership/maturity). **Parent-Claude verifier-loop pre-SIGN corrections applied to 2 sub-agent claims BEFORE Rigby:** (v-l-1) Agent 6 T.C4 dead-code CANDIDATE for EngagementAutonomyEngine REFUTED via direct read of `core.py:2390-2418` (`_policy_engagement_autonomy` has LIVE invoker at :2404); (v-l-2) Agent 5 F2 CANDIDATE at `views_opportunities.py:56-65` UPGRADED to CONFIRMED writer-site via direct read of REST `quick_apply()` writer inventory. **Rigby SIGN cycles 1 + 2 on fresh isolation pin `pa-fba0c4c81fba4922`** → verdict **SIGN-with-edits cycle 1** (Medium-High confidence, 2 must-fix — #1 runtime falsification for F.C1/F.C2, #2 placeholder-stall artifact) → **SIGN-clean cycle 2** (High confidence, 0 residual must-fix + Q7/Q8/Q9 + 2 nice-to-haves folded). **Cycle 1 fold applied via parent-Claude direct verification:** must-fix #1 CLOSED via Django ORM `.count()` on local env — all 4 Category C tables = 0 rows (`EngagementEvent.objects.count() = 0` empirically CONFIRMS F.C1 at RUNTIME in addition to CODE; `EngagementMetrics = 0` and `OpportunityInteraction = 0` nuance session-aggregation axis to "code WORKING + runtime-local DORMANT"; `ContentEngagement = 0` makes F.C4 docstring drift RUNTIME MOOT locally); must-fix #2 push-back accepted by Rigby cycle 2 as her own turn-1 narrative artifact not audit content. Rigby's `db_health_tool` returned `row_count=-1` (pg_class ANALYZE estimate — indeterminate) + `ops_tool.sql_query` did not return in her context + `db_health_tool env=prod` returned "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN" — logged as T.C8 three-checkbox tool-surface gap (a) ToolCallRecord query surface (b) bounded ORM row-count (c) prod DB reach. Cycle 1 Q1/Q4/Q5/Q6 folds applied; cycle 2 Q7/Q8/Q9 folds applied + 2 nice-to-haves (Env Coverage Table + T.C8 three-checkbox split). **Load-bearing findings (6, ranked by runtime severity):** (F.C1) ingestion path missing CONFIRMED HIGH at CODE + RUNTIME LOCAL tiers — Django ORM count zero + grep zero-writers at HEAD `d91d30f7`; both `outreach_draft` and `opportunity` FKs schema-only; extends S1402 F.B3 with second-FK evidence; PROD tier UNKNOWN due to T.C8(c); (F.C2) corrected axis map — dual-sub-agent verified (Agents 1 + 5 independently refuted parent §3 hypothesis with matching evidence); three independent surfaces not the hypothesized event-log-vs-aggregation-vs-join map; OpportunityInteraction is detail-child of EngagementMetrics via nullable FK not a join artifact; (F.C3) OpportunityInteraction F2 orphan-write CONFIRMED at writer-site `views_opportunities.py:56-65` REST `quick_apply()` omits `engagement_session` FK; runtime blast radius LOCAL bounded to ZERO (0 rows) — sibling to S1402 F.B2 zero-blast-radius pattern via different mechanism (empty parent write path vs dead code); (F.C4) ContentEngagement docstring "closes learning loop" drift CONFIRMED — no FK bridge to EngagementEvent/Metrics/OpportunityInteraction; Rigby Q5 lean narrow docstring NOW; (F.C5) EngagementAutonomyEngine "reply context builder" drift CONFIRMED — no such method in 4-method class body; Rigby Q6 lean reframe as "planned surface"; (F.C6) `run_ops_autopilot` deferred-by-policy CONFIRMED via Rigby ops probe + parent-Claude direct read jointly — task defined + docstring declares 10min cadence but NOT registered as PeriodicTask (0 of 92 enabled rows); intentionally deferred per AUDIT_FINDINGS.md #12 gating (`core/celery.py:507-509` + `:633-634` behavior-changing green-light list); ad-hoc PA-tool invocation LIVE at `td_handlers_ops.py:1643,1674`; consequence Category C `evaluate()` sweeps fire only on operator initiation; memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN to correctly classify; Rigby cycle 2 Q1 lean **(iii) separate ADR outside G1400 arc** for enable-decision (cross-category impact spans all 6 Category A/B/C/D/E/F policy hooks). **Inherited findings status:** S1402 F.B3 CONFIRMED HIGH and EXTENDED (adds `opportunity` FK second-writer-gap); S1402 F.B1 delivery-path-missing BLOCKER dependency for F.C1 ingestion design + `OutreachDraft.provider_message_id` MISSING (grep zero hits — R.C5 micro-migration); S1402 F.B4 does NOT extend to Category C `evaluate` methods (both LIVE via policy registry); Rigby cycle 1 Q4 lean **(ii) two sequential ADRs — F.B1 first, F.C1 stacked** ("cleaner dependency ordering and less thrash"); S1401 F1/F2/F3 lenses applied — F1 CANDIDATE holds for readers, F2 CONFIRMED at F.C3, F3 CANDIDATE at 5min Redis TTL in consumer; ownership gap S1274 §14 #36 CONFIRMED HIGH for Category C (0 JobContract + 0 AGENT_MAP + 0 task_routes hits); coverage upgraded LIGHT → MODERATE. **Maturity verdict WORKING (code) / DEFERRED-BY-POLICY (autonomous runtime) / WORKING code + DORMANT local runtime (session-aggregation axis) / MISSING (canonical ingestion)** — four-way split extending S1402 §13 WORKING/PARTIAL pattern. §19 follow-on queue 8 items ranked: R.C1 F.C1 ingestion path ADR (CENTRAL — pair-designed sequentially with F.B1); R.C2 F.C3 orphan-write fix; R.C3 F.C4 FK bridge (post-arc); R.C4 documentation anchor updates at §3.32 with per-model annotations per Rigby cycle 2 Q9 lean; R.C5 `OutreachDraft.provider_message_id` migration (blocks R.C1); R.C6 F.C5 resolution; R.C7 Governance §3.23 crossover ADR (bundle Group 1700); R.C8 F1 provenance-drift repo-wide sweep (deferred until F.C1 writer contract lands). T.C8 tool-surface gap IMMEDIATE per Rigby cycle 2 Q8 (low-risk high-leverage arc-support tools). All 28 canonical questions answered; parent §12.1 Category C F.iii questions all 3+1 answered. Verifier-loop history preserved append-only per playbook §6. §8 timeline S1403 row added. | **Third Group 1400 child audit; first library audit to CONFIRM a canonical event log architecturally-intact-but-runtime-empty finding at both CODE and RUNTIME LOCAL tiers** via parent-Claude Django ORM `.count()` when Rigby's `db_health_tool` returned indeterminate `row_count=-1` estimate. Also first library audit where **PROD runtime tier is explicitly UNKNOWN due to Rigby tool-surface gap** — logged as explicit constraint on empirical falsification scope. Also first library audit where **Rigby withdraws a cycle-1 must-fix as her own narrative artifact after parent-Claude pushback** ("Must-fix #2 is withdrawn: agreed it was my cycle-1 response artifact, not an audit-file defect"). Sets two verifier-loop pattern extensions: (a) parent-Claude runs alternate direct-verification via Django `manage.py shell` when Rigby's tool returns indeterminate — extends S1402 D.B7 joint-methodology from "confirmation" to "alternate-path direct-verification"; (b) parent-Claude pushback on must-fix classification is legitimate cycle-2 fold move when the must-fix originates in Rigby's response artifact not audit content. Load-bearing story: Category C is code-complete on read-only monitoring + session-aggregation surfaces but runtime-dormant in probed env; canonical ingestion has no writer path; F.B1 → F.C1 pair-design sequential ADR is arc-forward critical path. Isolation pin `pa-fba0c4c81fba4922` retires post-PR-merge per playbook §15. Index v22 updated per §10.1 (this row + §1.25 row + frontmatter v22 preamble). |

| **S1279** (2026-07-02) | Research OS installation: `CLAUDE.md` pointer + `docs/research/OPEN_ARCS.md` created + `docs/00-START-HERE/README.md` & `INDEX.md` extended | **Installation of the Research OS as canonical workflow.** Three P0 items landed in one atomic commit: (1) CLAUDE.md gains a "Research Library" subsection + universal 8-step Startup checklist — pointer-only into `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` (no restatement); (2) `docs/research/OPEN_ARCS.md` created as machine-readable cross-arc manifest with in-progress / awaiting-summary / closed / stalled / not-started sections + reconciliation ritual + schema reference (source-of-truth for arc state per OS §6.6); (3) `docs/00-START-HERE/README.md` + `INDEX.md` extended with Research Library discovery rows and OS entry in mandatory reading order. `CURRENT_RESEARCH.md` evaluated and explicitly rejected — OPEN_ARCS with `state: in-progress` filter serves the same purpose; adding a third file would duplicate one of OPEN_ARCS + `00-START-NEXT-SESSION.md`. OS `status:` flipped `draft` → `active` — Research OS is now **CANONICAL**. Verifier_loop appended with installation record + validation checklist. No architectural changes; OS §1-§19 structurally unchanged; §20.15 installation record section added additively. Zero circular references; zero duplicated startup instructions; zero conflicting authority. Runtime untouched. | **Installation, not extension.** S1268-S1278 built the process framework; S1279 makes it the default workflow. From this point forward: (a) every fresh Claude Code session discovers the OS naturally via CLAUDE.md or START-HERE; (b) Group 1400 Revenue may open under the fully-installed OS as the first exercise of the "Start research group NNNN" reduced-prompt target rhythm (OS §12.3); (c) future OS improvements are operational refinement (P1/P2 items: ADR corpus, Investigation Log template, Ops Incident Report template, playbook v3, `RESEARCH_DEBT.md` manifest) — not architectural redesign. The Research OS architecture is closed. Index v12 updated per §10.1 (this row + §1.14 CANONICAL status flip). |

**Pattern observation (updated S1279).** The library has grown
in **four waves plus one canonicalization event.** **First wave** (S1268-S1272): 5 docs in 5
sessions — the Employee OS depth arc following the "each doc
names the next" discipline. **Second wave** (S1273-S1275): the
whole-platform sibling arc (§1.9 inventory) + cross-domain
integration audit + design-preparation arc (§1.10 option
selection → §1.12 event schema) — first `authority: design-
preparation` docs. **Third wave** (S1274 v1 + S1276 v2 playbook,
S1300 memory scoping): the process framework itself.
`authority: process` (playbook) and `authority: parent-doc`
(S1300) enter the corpus. **Fourth wave** (S1276 introspection +
S1277 OS + S1278 ratification): the process framework becomes
self-executing. `authority: process-audit` (introspection) and
canonical Research OS (§1.14) enter the corpus. A brand-new
Claude Code can now be productive by reading only CLAUDE.md +
MEMORY.md + `00-START-NEXT-SESSION.md` + OS §0-§5 — no custom
prompt from Chris required. The library's *next* growth events
are: (a) migration session S1279+ landing OS §17 P0 items
(CLAUDE.md pointer, `OPEN_ARCS.md`, START-HERE pointers) that
convert OS from READY-WITH-MINOR-FOLLOW-UP to CANONICAL; (b)
Group 1400 Revenue opening under the OS+playbook contracts as
first exercise of "Start research group NNNN" reduced-prompt
target; (c) Group 1300 Memory children (S1301 RAG lanes queued
next); (d) whole-platform arc's top-3 next missions per §1.9
§9 — Revenue Pipeline canonical architecture (§5.12),
Observability Deduplication Audit (§5.13), Sports/DBAO ↔ AI
Studio Integration Sketch (§5.14); (e) Employee OS arc STAGE 5
(Trust Propagation §5.3 or Employee Boundary Escalation §5.4
— Chris picks). All parallel-safe if pursued independently,
per §18 dependency semantics (informational, not blocking).

---

## 9. Future Research Roadmap

Not a design. Not a build plan. A recommended *research*
ordering to minimize architectural uncertainty.

The ordering rule: each research mission unlocks the next.
Skipping a dependency means the downstream doc has to invent
context it should have inherited.

```
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 0 — Governance + Authority Evolution  ✓ CLOSED S1269     │
│                                                                  │
│  Shipped: docs/research/governance_authority_evolution.md       │
│  4 governance planes; 35 runtime gates; 12 failure modes;       │
│  authority enforcement blocked on Symbol Mapping prereq         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Symbol Mapping Architecture  ✓ CLOSED S1270          │
│                                                                  │
│  Shipped: docs/research/symbol_mapping_architecture.md          │
│  57 unique action_class strings; 5 mapping options (A-E);       │
│  20 enforcement boundaries; 23 identifier registries; F11       │
│  captures 7 architectural blind spots. Rigby SIGN-with-edits    │
│  (2 must-fix + 3 optional + 2 discoverability folded).          │
│                                                                  │
│  Answered: WHAT action happened?                                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1b — Actor Identity & Attribution  ✓ CLOSED S1271        │
│  (same-session follow-on to STAGE 1; surfaced during Symbol     │
│   Mapping verifier loops as the composite prereq)               │
│                                                                  │
│  Shipped: docs/research/actor_identity_attribution_             │
│           architecture.md                                       │
│  19 identity concepts; 22 attribution surfaces (F1: OpsRun has  │
│  no user FK); 15 historical failures; 25 registries; §8.5       │
│  executor/sponsor/principal 3-role vocabulary; F11 warning      │
│  against single-actor label conflation. Rigby pressure-test     │
│  SIGN-with-edits (4 must-fix + 2 optional folded).              │
│                                                                  │
│  Answered: WHO performed the action?                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 2 — Authority Enforcement Design Space  ✓ CLOSED S1272   │
│                                                                  │
│  Shipped: docs/research/authority_enforcement_design_space.md   │
│  24 inputs; 20 boundaries (17 + 3 SIGN-added WebSocket/Fleet/   │
│  Spider); 12 modes; 6 design options A-F enumerated neutrally;  │
│  15 anti-patterns (3 Tier-0 hazards); 15-prereq DAG.            │
│  Rigby pressure-test SIGN-with-edits, Medium confidence.        │
│                                                                  │
│  Type: DESIGN-SPACE research (first mission carrying design-    │
│  space content per §9 pacing). No option chosen. No design      │
│  decision. Chris gates any downstream selection.                │
│                                                                  │
│  Maintenance note: §1.8 is design-space only. The 6 options     │
│  are for future consumption; none is designated for             │
│  implementation. Do not treat as implementation greenlight.     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3 — Symbol Mapping Option Selection Design  ✓ CLOSED    │
│  S1274                                                          │
│                                                                  │
│  Shipped: docs/research/                                         │
│    symbol_mapping_option_selection_design.md (§1.10)            │
│  5 parallel sub-agents; 100-cell coverage matrix; drift         │
│  ranking; actor compatibility per option; failure modes.        │
│  **Recommendation: Option E (evidence-only) as v0** with 4      │
│  Rigby must-fix edits folded (generalization tone alignment;    │
│  catastrophic-action graduation guardrail; non-NULL             │
│  misclassification drift pattern; employee_handle vs.           │
│  executor_actor distinction). Rigby SIGN-with-edits, Medium     │
│  confidence, recommendation = Modify.                           │
│                                                                  │
│  Maintenance note: Option E is v0-only recommendation, NOT      │
│  implementation and NOT enforce-mode. Chris gates all           │
│  downstream steps. §10.3.1 guardrail forces re-decision.        │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 4 — Symbol Mapping Event Schema Design  ✓ CLOSED S1275   │
│                                                                  │
│  Shipped: docs/research/                                         │
│    symbol_mapping_event_schema_design.md (§1.12)                │
│  Two-surface event stream (`OpsRunEvent` mission-scoped +       │
│  `ToolCallRecord.parameters` non-mission tool calls) unified    │
│  via new `authority_action_observed_stream` DB view. 21 payload │
│  fields. 4 v0 emitters + 1 v0 first consumer. Confidence enum   │
│  {DEFINITE, DECLARED (non-authoritative), HEURISTIC (banned),   │
│  UNKNOWN}. Drift stack: NULL rate + zero-fire (S1245 reuse) +   │
│  weighted cross-emitter disagreement + weekly sampled truthing  │
│  + invariants I1-I7 + schema-signature check. 3 golden flows.   │
│  Batch-mode dashboard. 5-phase ~10-week rollout sketch.         │
│  Rigby SIGN-with-edits (8 must-fixes + bonus #9 folded).        │
│                                                                  │
│  Maintenance note: §1.12 is design-preparation only. Not        │
│  implementation. Not enforce-mode. Rollout §15 is sequencing    │
│  sketch, not merged PR. Chris gates every subsequent PR.        │
├──────────────────────────────────────────────────────────────────┤
│  STAGE 5 — no P0 gates the arc.                                 │
│                                                                  │
│  Both §5.3 Trust Propagation Model and §5.4 Employee Boundary   │
│  Escalation Contract are P1 with no P0 in front. Chris picks    │
│  the next STAGE.                                                │
│                                                                  │
│  Parallel-safe with the whole-platform arc's top-3 next         │
│  missions per §1.9 §9 — Revenue Pipeline canonical              │
│  architecture (§5.12), Observability Deduplication Audit        │
│  (§5.13), Sports/DBAO ↔ AI Studio Integration Sketch (§5.14).   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3b — Actor Role Propagation Design  (P1)                 │
│                                                                  │
│  Two layers per §1.8 §14.2 clarification:                       │
│  (i) Role schema + propagation contract — parallel-safe with    │
│      STAGE 3 (does not depend on Symbol Mapping option)         │
│  (ii) Implementation across boundaries — depends on STAGE 3     │
│       shipped                                                    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3c — Authority Enforcement Design Decision  (P1)         │
│                                                                  │
│  Convert §1.8's 6 design-space options into an actual design    │
│  decision. Consume §1.8's 33-incident catalog, 15 anti-         │
│  patterns, 15 prereqs. Rigby SIGN + Chris gate.                 │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STAGE 4a       │  │  STAGE 4b       │  │  STAGE 4c       │
│  Trust          │  │  Memory         │  │  Mission        │
│  Propagation    │  │  Architecture   │  │  Composition    │
│  (§5.3)         │  │  (§5.4)         │  │  (§5.6)         │
│                 │  │                 │  │                 │
│  Inter-employee │  │  Cross-employee │  │  Canonical      │
│  trust contract │  │  episodic       │  │  idempotency    │
│  (today only    │  │  memory shape   │  │  key across     │
│  per-employee   │  │                 │  │  orchestration  │
│  trust exists)  │  │                 │  │  paths          │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 5                     │
                │  Cross-Employee Scheduling   │
                │  (§5.5) — depends on Stage   │
                │  4a + 4b + 4c                │
                └──────────────┬───────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 6                     │
                │  Employee Delegation Design  │
                │  (DESIGN, not research —     │
                │  prerequisites must close    │
                │  first)                      │
                └──────────────┬───────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │  STAGE 7 — Implementation    │
                │  (PRs, with research as the  │
                │  justification artifact)     │
                └──────────────────────────────┘

Lateral research that does not block the main chain:

  • Cross-plane Composition (§1.7 F10 + governance F1) — how do
    autonomy / authority / budget / human governance compose
    when all four are active? Blocking STAGE 2 completeness.
  • Security / Permission scoping (§5.8) — if cross-fleet
    surfaces enter scope.
  • Configuration Architecture note (§5.9) — when feature-flag
    growth becomes a documentation problem.
  • Observability consolidation (§5.7) — optional; no blocking
    downstream.
  • Knowledge Graph scoping (§5.10) — only if a use case
    materializes.
  • Focus Mode inventory (§5.11) — if Employee OS reasoning
    surfaces a dependency on it (flagged by Rigby S1269).

  Whole-platform arc (added S1273 v5 — parallel-safe to the
  Employee OS depth arc above):

  • §5.12 Revenue / Outreach / Engagement Pipeline canonical
    architecture doc — P0 parallel. Missed domain caught by
    Rigby S1273 review; blocks any revenue-adjacent work.
  • §5.13 Observability Deduplication Audit — P1. Trace a
    single execution scenario through 5 telemetry layers.
  • §5.14 Sports/DBAO ↔ AI Studio Integration Sketch — P1.
    Structural question about whether platform is one or two.
  • Full 11-mission whole-platform roadmap: see §1.9 §9
    (Notification Unification, Event Bus Producer/Consumer
    Map, Rigby v0 Event Intake Activation Plan, Advisor
    Persistence Contract, Content ↔ Initiative Wiring Audit,
    LLM Provider Failover + Cost Tracking, Claude Code
    Tooling Design Doc, etc.).
```

**Pacing note.** Stages 0 through 1b were pure research —
inventory + classification + failure analysis. STAGE 2
(Authority Enforcement Design Space) is the first mission with
*design* content: the doc will contain a proposal Chris must
gate. Stages 3-4 return to pure research; Stage 5 is design;
Stage 6 is implementation. The discipline that holds this
together is the verifier loop + Rigby SIGN review on every
transition.

---

## 10. Maintenance Rules

This index must evolve in lockstep with the library. The
rules below apply whenever any change happens.

### 10.1 When a new research doc is added

Within the same PR (or same session if no PR yet):

1. **Add a row to §1.** With Title / Purpose / Status / Type /
   Primary questions / Dependencies / Recommended next reads /
   Importance.
2. **Add the doc to §4 dependency graph.** Show its parents
   (via `companion_docs`) and where it sits in the lineage.
3. **Update §2 reading paths.** If the new doc belongs in
   Path A-G (or a new path), add it.
4. **Update §3 domain map.** Move the relevant domain row's
   "Missing research" → "Existing research" (or update
   maturity).
5. **Update §5 gaps.** If the new doc closes one of the named
   gaps, mark it closed with a pointer. If it surfaces new
   gaps, add them.
6. **Update §7 decision matrix.** If there's a class of work
   that should now read the new doc first, add the row.
7. **Update §8 timeline.** Append a new row chronologically.
8. **Update §9 roadmap.** If the new doc was the next stage,
   move the arrow forward.
9. **Bump `last_verified` in this doc's frontmatter.**

### 10.2 When a research doc is superseded

1. Add a pointer header at the top of the superseded doc per
   `DOC_LIFECYCLE.md` V2 conventions.
2. In §1, change Status to `Deprecated` and add a "Superseded
   by: [link]" line.
3. In §4, move the superseded doc to a "historical" footnote
   below the main graph. Do not remove from the corpus —
   per memory rule `feedback_docs_never_delete`, preservation
   matters.
4. In §7 decision matrix, replace references to the
   superseded doc with the successor.

### 10.3 When a doc's status changes (Draft → Active, Active → Canonical)

1. Update the doc's own frontmatter `status` field.
2. Update §1 row Status column.
3. If the doc has been moved to Canonical, add it to the
   appropriate canonical-anchor list in adjacent docs
   (`PLATFORM_INVENTORY.md`, `EMPLOYEE_OS_PRIMITIVES.md`,
   or this index's frontmatter `companion_anchors` if
   applicable).

### 10.4 When drift between docs is discovered

1. Per `DOC_LIFECYCLE.md` §2c: **inventory wins** on counts.
2. Add a drift call to the *newer* doc's drift section (every
   research doc has one — substrate audit cross-reference
   lives in Appendix A, collaboration patterns drift section
   lives in its §12).
3. Do **not** silently edit the older doc. If the older doc
   needs correction, that's a separate review pass with its
   own SIGN verdict.

### 10.5 When this index itself drifts from the library

If `ls docs/research/` shows a doc that isn't in §1, that's
the index's drift. Open a small fix-up PR that just updates
§1, §4, §5, §7, §8. Do not bundle it with anything else.

### 10.6 Authority on this index

This index is **authority: navigation**, not
**authority: canonical** — it points to canonical docs
without being one. If the index disagrees with a canonical
anchor (EMPLOYEE_OS_PRIMITIVES, PLATFORM_INVENTORY,
DOC_LIFECYCLE), the anchor wins; the index gets edited.

---

## Appendix A — Verifier-loop pass notes

This index was drafted from direct inventory of
`docs/research/` at 2026-06-30 (`ls` showed 3 .md files),
plus frontmatter re-reads of each, plus cross-reference
against `docs/` canonical anchors via `Glob`.

**Self-verifier pass (one round) before finalization
identified and fixed:**

- **Missing doc check.** `ls docs/research/` returns exactly
  3 files; all 3 cataloged in §1. No subdirectories. No
  hidden docs. ✓
- **Duplicate classifications.** Originally tagged §1.1 as
  pure "Inventory"; on second pass added "+ Architecture
  Audit + Failure Analysis" because §7 of that doc is
  substantively failure analysis. Same fix on §1.3. ✓
- **Dependency ordering.** First draft showed §1.2 and §1.3
  as parallel children of §1.1 in §4 graph. Re-verified
  against the actual creation order (§1.2 was written
  *before* §1.3 within the same session) and timeline §8 —
  graph is correct; chronologically §1.3 was the audit that
  surfaced the "wider question" raised by Rigby's review of
  §1.2. ✓
- **Inconsistent statuses.** First draft listed all three as
  "Active." Re-read each frontmatter and found all three are
  literally `status: draft` per their YAML. Updated §1 rows
  to "Draft → Active (SIGN-... from Rigby)" to honor both the
  frontmatter literal and the review-state reality. ✓
- **Discoverability.** Originally Path G ("platform
  reliability") didn't mention the client factories. Added
  the hard-rule callout on `anthropic_client_factory.py` /
  `openai_client_factory.py` because the memory rules
  (`feedback_anthropic_client_factory`,
  `feedback_openai_client_factory`) and the zombie-thread
  failure class (§1.3 §7 row 17) all converge on that
  enforcement. ✓
- **§3 domain map** — Memory domain originally not listed;
  added on second pass because §5.2 calls it out as a real
  research gap. Same for Knowledge Pipeline (added per
  `KNOWLEDGE_PIPELINE.md` existing as a canonical anchor
  outside the research library). ✓
- **§7 decision matrix** — first draft was missing the row
  for `MissionRunnerConfig.auto_emit_verdict`. Added on second
  pass because the protocol-invariant-change row (§1.3 §7 row
  29) was Rigby's SIGN-with-edits correction and deserves a
  decision-matrix anchor of its own.

**Status after self-verifier pass.** Publishable as v1.
Rigby independent SIGN review on this index is **not**
required per S1268 mission spec scope (the spec asks for a
verifier loop, not a Rigby pass on the index itself). If a
future session wants Rigby's read on the index, that's a fine
small follow-up.

## Appendix B — v3 update pass notes (S1271)

Triggered by the same-session landing of both `symbol_mapping_architecture.md`
(§1.6) and `actor_identity_attribution_architecture.md` (§1.7).
Both docs completed the verifier loop + Rigby SIGN review before
this index update, so §10.1 was applied wholesale.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 6 files
  (5 research + this index). Both new docs cataloged in §1.6
  and §1.7 respectively. No subdirectories. No hidden docs. ✓
- **Section renumbering.** §5.2 (was "Symbol Mapping — P0
  recommended next" pre-close) marked CLOSED with pointer to
  §1.6. §5.2a added for Actor Attribution close. §5.2b added
  for new P0 next research (Authority Enforcement Design
  Space). Prior §5.3-§5.11 numbering preserved so downstream
  references don't break; renumbering deferred to a future pass
  if it becomes needed. ✓
- **Roadmap stage advancement.** Prior STAGE 1 (Symbol Mapping)
  marked CLOSED. New STAGE 1b (Actor Attribution) inserted as
  same-session follow-on. New STAGE 2 (Authority Enforcement
  Design Space) is the "recommended next." Prior STAGE 2a/2b/2c
  (Trust Propagation / Memory / Mission Composition) renumbered
  to STAGE 3a/3b/3c. Downstream stages (Cross-Employee
  Scheduling → 4, Employee Delegation Design → 5,
  Implementation → 6) bumped by one. ✓
- **Dependency graph.** ASCII diagram in §4 extended with two
  new boxes for §1.6 and §1.7 in the correct downstream
  position, then the "Future research mission" box updated to
  point at Authority Enforcement Design Space (was previously
  pointing at Symbol Mapping, now landed). ✓
- **Domain map.** Governance row's "Missing research" cleared
  (Symbol Mapping was the pending item, now shipped);
  downstream noted as Cross-plane Composition. Authority row
  updated: existing research now includes §1.6 + §1.7; missing
  research is Authority Enforcement Design Space. New "Actor
  Identity / Attribution" domain row added citing §1.7 with
  F1's OpsRun gap as the flagship finding. ✓
- **Decision matrix.** 7 new rows added covering:
  `JobContract.authority` use; actor identity on any new model /
  audit surface; adding user field to OpsRun (explicit
  anti-pattern warning per §1.7 F1 + F11); code using
  `agent_name` CharField anywhere (F4 ambiguity); code using
  `runs_as_username` (F3 + F11); duplicate Agent row risk (F5);
  PA tool actor/user context propagation (§1.6 §6 + §1.7 §7).
  Prior "Authority enforcement (vs. observation)" row updated
  to cite §1.6 + §1.7 + §5.2b instead of the now-closed §1.4 §11
  recommendation. ✓
- **Timeline.** 2 rows appended (S1270 + S1271) with full
  content summaries + influence callouts. Pattern observation
  updated to reflect the 3-session growth cadence
  (S1269/S1270/S1271) after the S1268 burst. ✓
- **Discoverability.** Both new docs now surface via §1
  (rows), §3 (domain map, esp. new Actor Identity row), §4
  (dependency graph position), §5 (closed-gap + new-gap
  entries), §7 (7 new decision-matrix rows), §8 (timeline
  chronology), and §9 (roadmap stage boxes). Reading paths §2
  not extended in this pass; a Path H for "understanding actor
  identity end-to-end" was considered but deferred — Paths A-G
  already cover the reading order via §1.6 and §1.7's
  companion_docs frontmatter chains. Future session can add
  Path H if requested. ✓
- **Frontmatter last_verified.** Bumped from "v2" to "v3" with
  a summary line naming the two shipped docs + the roadmap
  advancement. verifier_loop field expanded with the v3
  changes and prior v1/v2 history preserved. owner field
  extended: "v3 update S1271." ✓

**Status after v3 pass.** Publishable as v3. Both new docs are
discoverable via all 8 index sections (§1-§9 plus this appendix
+ maintenance rules). Rigby independent SIGN review on the
index itself remains optional per §10 discipline; if requested,
a small follow-up pass suffices.

## Appendix C — v4 update pass notes (S1273 Part 1)

Triggered by S1272's landing (`authority_enforcement_design_space.md`)
during S1273's Part 1 documentation-maintenance work. This is
the first update that includes an explicit **maintenance note**
that a docs/research/ entry is design-space only — not
implementation greenlight — per S1273 mission-spec requirement.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 7 files
  (6 research + this index). §1.8 added for `authority_enforcement_design_space.md`.
  No subdirectories. ✓
- **Design-space vs. implementation distinction.** §1.8 status,
  §3 domain map row ("Authority Enforcement (design space)"),
  §5.2b closure note, §7 decision matrix new row on enforcement
  ideas, §8 timeline row, and §9 roadmap STAGE 2 box all
  explicitly state that §1.8 is **design-space only**. This is
  the explicit "maintenance note that Authority Enforcement is
  still design-space only, not implementation" required by
  S1273 mission spec. ✓
- **Roadmap advancement.** Prior STAGE 2 (Authority Enforcement
  Design Space) marked CLOSED S1272. Two new stages added
  parallel-ordered: STAGE 3 (Symbol Mapping Option Selection
  Design — the recommended P0 next), STAGE 3b (Actor Role
  Propagation Design — P1 parallel-safe on Layer (i)), STAGE
  3c (Authority Enforcement Design Decision — P1). Prior
  STAGE 3a/3b/3c (Trust Propagation / Memory / Mission
  Composition) renumbered to STAGE 4a/4b/4c. Downstream stages
  bumped: Cross-Employee Scheduling → 5, Employee Delegation
  Design → 6, Implementation → 7. ✓
- **Dependency graph.** ASCII diagram in §4 extended with new
  §1.8 box (with SIGN-added-boundaries callout). "Future
  research mission" downstream box updated to point at Symbol
  Mapping Option Selection Design (was Authority Enforcement
  Design Space, now landed). ✓
- **Domain map.** Authority row expanded to include §1.8;
  "Missing research" changed from "Authority Enforcement Design
  Space" to "Symbol Mapping Option Selection Design"; maturity
  bumped from "Medium" to "Medium-High" (all three prereqs now
  shipped as research). New "Authority Enforcement (design
  space)" row added citing §1.8 with explicit design-space-only
  maintenance note. Actor Identity row updated to reflect the
  new gating mission. ✓
- **Decision matrix.** 6 new rows added covering: any authority
  enforcement idea (must consult §1.8 anti-patterns + prereqs),
  AuthorityLevel enum usage anywhere new (F1 warning about
  single runtime consumer), new INLINE enforcement gate (F8
  fail-open precedent), adding action_class to any audit model
  (prereq #3 + #4), WebSocket/Fleet/Spider handlers touching
  employee-scoped work (§3 rows 18-20), cross-plane governance
  interaction (§7.5 8 questions). ✓
- **Timeline.** 1 new row appended (S1272) with content
  summary + influence callout. ✓
- **Discoverability.** §1.8 now surfaces via §1 (§1.8 row), §3
  (domain map — Authority row + new Authority Enforcement row),
  §4 (dependency graph position), §5 (§5.2b closed + new §5.2c
  gap), §7 (6 new decision-matrix rows), §8 (timeline), §9
  (roadmap STAGE 2 CLOSED + STAGE 3/3b/3c). ✓
- **Frontmatter.** Bumped from "v3" to "v4" with change
  summary. verifier_loop field expansion deferred to v5 or
  next larger update to keep this pass focused. owner field
  will be extended: "v4 update S1273 Part 1" at commit time. ✓

**Status after v4 pass.** Publishable as v4. §1.8 discoverable
via all 8 index sections. Maintenance note explicit at 4 sites
(§1.8 status, §3 row, §5.2b, §9 STAGE 2 box). Rigby independent
SIGN review on the index itself remains optional per §10.

**Frontmatter-drift note (caught S1273 v5).** The v4 pass
updated Appendix C but forgot to update the frontmatter's
`last_verified` and `owner` fields to reflect v4. That drift
was carried forward until S1273 v5 caught + corrected both.
Small process lesson: bump frontmatter in the same edit as the
appendix note; do not defer.

## Appendix D — v5 update pass notes (S1273 Part 2)

Triggered by S1273's landing of `platform_architecture_
inventory.md` (§1.9) as the first whole-platform architectural
inventory. Chris's direction at S1273 close: "the next cleanup
should be updating ARCHITECTURE_INDEX.md so this becomes the
whole-platform counterpart to the Employee OS research
library." This is the first update that expands the library's
scope from Employee-OS-focused-only to Employee-OS-arc PLUS
whole-platform inventory as a sibling arc.

**Verification pass (one round) before finalization:**

- **Missing doc check.** `ls docs/research/` now shows 8 files
  (7 research + this index). §1.9 added for
  `platform_architecture_inventory.md`. No subdirectories. ✓
- **Scope split acknowledgment.** §1 preamble rewritten to
  distinguish (a) Employee OS arc §1.1-§1.8 (deep on one
  subsystem, S1268-S1272) from (b) whole-platform inventory
  §1.9 (wide on all subsystems, S1273). "When to read which"
  guidance added. ✓
- **Reading path.** New Path H "I need to understand the whole
  platform" added — CLAUDE.md → PLATFORM_WHAT_IT_IS →
  PLATFORM_INVENTORY → §1.9 → specific §3.n → optional
  Employee-OS-arc doc if subsystem covered. ✓
- **Domain map.** New Revenue / Outreach / Engagement row
  added citing §1.9 §3.32 + underlying models + services.
  Rigby caught this as a missed platform subsystem during
  S1273 SIGN review; folded into §1.9 §3.32 + registered here
  as new domain row per §10.1. Rest of §3 unchanged — the
  17-domain Employee-OS-adjacent view remains valid; §1.9's
  32-domain whole-platform view is complementary. ✓
- **Dependency graph.** Sibling-arc ASCII diagram added below
  the main graph, showing §1.9 as parallel to the Employee OS
  arc off the same three anchors (PLATFORM_INVENTORY +
  PLATFORM_WHAT_IT_IS + EMPLOYEE_OS_PRIMITIVES). §1.9 cites
  downstream findings from §1.4 + §1.6 + §1.7 where they overlap
  its own findings, but does NOT depend on the arc's ordering. ✓
- **Gap closures and additions.** §5.4 Memory Architecture
  noted as partially covered by §1.9 §3.13 (Memory / Knowledge
  / Embeddings — DEEP coverage; 5 memory tables enumerated,
  14-day freshness contract, PA-to-Agent feedback closure,
  auto-save ops facts). Three new gaps added — §5.12 Revenue
  Pipeline canonical architecture (P0 parallel; missed-domain
  finding from Rigby's S1273 review), §5.13 Observability
  Deduplication Audit (P1; addresses §1.9 §5.7 5-layer
  telemetry duplication), §5.14 Sports/DBAO ↔ AI Studio
  Integration Sketch (P1; addresses §1.9 §3.10 island-vs-
  integrated structural question). ✓
- **Decision matrix.** 3 new whole-platform rows added:
  onboarding / cross-domain scoping (start at §1.9); Revenue/
  Outreach/Engagement/Meeting/ClosePack work (§1.9 §3.32 +
  §4.9 + §5.12 gap); sports-betting content integration
  (§1.9 §3.10 + §4.8 + §5.14 gap). ✓
- **Timeline.** 1 new row appended (S1273, 2026-07-01) with
  content summary + Rigby SIGN-with-edits detail (Medium
  confidence, 6 substantive edits folded incl. missed Revenue
  Pipeline domain) + Chris's whole-platform-counterpart
  direction. Timeline note extended to reference the fresh
  isolation pin `pa-02cfd3206302352f` used for §1.9's Rigby
  review (kept separate from shared S1270+ arc pin
  `pa-cbcc410b32714f60` mid-session per context-crossing
  directive). ✓
- **Pattern observation.** Section 8 pattern-observation
  paragraph updated to reflect the two-wave library shape —
  first wave S1268-S1272 (Employee OS depth arc), second wave
  S1273 (whole-platform sibling arc). Next growth events now
  split: (a) Employee OS arc STAGE 3 Symbol Mapping Option
  Selection Design (Chris-gated); (b) whole-platform arc
  top-3 next missions (§5.12/§5.13/§5.14). Parallel-safe. ✓
- **Roadmap.** §9 lateral research list expanded to reference
  whole-platform arc with §5.12/§5.13/§5.14 as the top-3 next
  missions + pointer to §1.9 §9 for the full 11-mission
  roadmap. ✓
- **Frontmatter.** Bumped from "v4" to "v5" with change
  summary. verifier_loop field expanded with v5 changes and
  prior v1-v4 history preserved. owner field extended: "v5
  update S1273 Part 2." Also caught + corrected v4 frontmatter
  drift (v4 pass updated Appendix C but never bumped
  last_verified — see Appendix C's Frontmatter-drift note
  above). ✓
- **Discoverability.** §1.9 now surfaces via §1 (preamble +
  §1.9 row), §2 (new Path H), §3 (Revenue Pipeline row +
  cross-reference to §1.9's 32-domain map), §4 (sibling-arc
  dependency graph extension), §5 (§5.12/§5.13/§5.14 new gap
  entries + §5.4 partial-coverage note), §7 (3 new decision-
  matrix rows), §8 (timeline row + pattern-observation
  update), §9 (roadmap lateral research expansion). ✓

**Status after v5 pass.** Publishable as v5. §1.9 discoverable
via all 9 index sections. Dual-scope library shape is now
explicit throughout the doc (§1 preamble, §2 Path H, §4 sibling
arc, §8 pattern observation, §9 lateral research). Rigby
independent SIGN review on the index itself remains optional
per §10.6 — the index is `authority: navigation`, not
`authority: canonical`; anchors win when they disagree with the
index.


## Appendix E — v6 + v7 update pass notes (S1274)

Two concurrent S1274 registrations landed in the same day:

**v6 (concurrent CC session).** Registered §1.10
`symbol_mapping_option_selection_design.md` (STAGE 3 Symbol Mapping
Option Selection Design mission — Chris-gated recommendation of Option
E as v0). Frontmatter bumped v5 → v6; timeline row added; roadmap
advanced STAGE 3 CLOSED / new STAGE 4 Event Schema Design. No
appendix pass notes written by that pass — noted for record.

**v7 (this pass).** Registered §1.11 `DOMAIN_RESEARCH_PLAYBOOK.md`.

### Verification pass (v7) before finalization

- **Missing doc check.** `ls docs/research/` shows the playbook
  present as `DOMAIN_RESEARCH_PLAYBOOK.md`. Registered as §1.11. ✓
- **Concurrent-session coordination.** Detected that a parallel CC
  session bumped v5 → v6 for §1.10 while this session was drafting
  the playbook. Handled by: (a) reading the current v6 frontmatter
  before editing, (b) building on top of v6 with a v6 → v7 bump
  rather than a v5 → v6 clash, (c) adding a note in this appendix
  that v6 concurrent session did not add its own appendix. No
  content loss; both S1274 registrations coexist. ✓
- **Authority-type distinction.** §1.11 is `authority: process`, the
  first process doc in the library. Distinguished in the §1.11 row
  text so readers know it sets rules for other docs rather than
  producing findings. Considered adding a new §11 "Process Documents"
  section separately from §1; decided against — one process doc
  today does not justify a new section, and readers looking for
  "what to read first" benefit from playbook being adjacent to
  research docs. ✓
- **Discoverability.** §1.11 surfaces via §1 (row) + §8 (timeline).
  Reading paths §2 not extended in this pass — the playbook does
  not fit any existing goal-based path (it is for people STARTING
  a domain audit, not any of the current A-H personas). A future
  Path I "I want to start a domain audit" could be added if session
  volume in the 1300-1900 range grows; deferred for now since
  §1.11 row and §8 timeline give sufficient entry points. ✓
- **Domain map §3.** Not updated in this pass — playbook is process
  meta, not a domain finding. No new domain row applies. ✓
- **Gaps §5.** Not extended in this pass — playbook sets research
  GROUP structure (queue in §12 of the playbook itself); §5 tracks
  research gaps in specific domains, which is orthogonal. ✓
- **Decision matrix §7.** Not extended — playbook governs how future
  audits get written, not what class of work triggers reading a
  specific doc. Row could be added in future: "About to start a
  domain audit → read DOMAIN_RESEARCH_PLAYBOOK.md first." Deferred. ✓
- **Roadmap §9.** Not modified in this pass — playbook does not
  advance any specific research stage; it enables the next 7 groups
  in parallel-safe fashion (§12 of the playbook). ✓
- **Frontmatter.** Bumped v6 → v7. verifier_loop preserved v1-v6
  history; added v7 note about concurrent-session coordination.
  owner field extended: "v7 update S1274 Part 2 [§1.11
  DOMAIN_RESEARCH_PLAYBOOK]." ✓

**Status after v7 pass.** Publishable as v7. §1.11 discoverable via
§1 (row) and §8 (timeline). Concurrent v6 session note preserved.
Rigby SIGN review on the index itself remains optional per §10.6.

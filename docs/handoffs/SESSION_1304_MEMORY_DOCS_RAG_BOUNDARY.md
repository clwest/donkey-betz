---
session: 1304
status: closed (draft-audit landed, Rigby SIGN-clean after cycles 1 + 2, Chris commit-gated → committed)
date: 2026-07-01
arc: Research Group 1300 (Memory / Knowledge / Embeddings) — child P4 (playbook §11.2 20-section audit template). Fourth child audit under the parent-with-children arc. Categories E ↔ D Documentation Corpus ↔ RAG Boundary exclusive **boundary lens** per parent §5 P4 slot ("smaller scope; benefits from §3.14 audit landing first"). Deliberately smaller than P1-P3 — integration-focused, not re-audit of either category internals. Inherits S1301 §14.2 silent-failure surface + §19 downstream routing (including row-level orphan-write pattern that S1304 partially invalidates via verifier-loop); S1302 §17.3 name-collision resolution as boundary methodology; S1303 §9 Cat F ↔ Cat D OBSERVED GAP + §19 R3 turn-context → RAG enrichment hypothesis + §14 F4-CANDIDATE discipline (applied to `ingested_via` orphan claim).
prs_merged: []
prs_open:
  - "S1304 audit + INDEX v16 + OPEN_ARCS + handoff + START-NEXT rotation (branch docs/session-1304-memory-docs-rag-boundary off main; Chris commit-gate resolved this session → PR opens on push with `--admin` flag authorization)"
prs_upstream:
  - "S1303 commit-gate on main (PR #2778 = 6365f33f) — resolved between S1303 close and S1304 open; S1304 branches off main, not stacked on S1303"
branches_open:
  - "docs/session-1304-memory-docs-rag-boundary (base = origin/main)"
companions:
  - docs/handoffs/SESSION_1300_MEMORY_RESEARCH_GROUP_PARENT_SCOPING.md
  - docs/handoffs/SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md
  - docs/handoffs/SESSION_1302_MEMORY_PERSISTENCE_ARCHITECTURE.md
  - docs/handoffs/SESSION_1303_MEMORY_CONVERSATIONAL_THREAD_MEMORY.md
  - docs/research/domains/memory/1300_memory_domain_scoping.md
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md
  - docs/research/domains/memory/1302_memory_persistence_architecture_audit.md
  - docs/research/domains/memory/1303_memory_conversational_thread_memory_audit.md
  - docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/topics/local-askdocs.md
deliverables:
  - "docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md (~1130 lines, status: draft, sign_status: SIGN-clean, authority: research, research_group: 1300, child_slot: P4, domain_slug: memory; 20-section playbook §11.2 template; verifier_loop v0.1 skeleton + v0.2 synthesis + v0.3 SIGN cycle 1 4-must-fix fold + v0.4 SIGN cycle 2 verification pass — SIGN-clean)"
  - "docs/research/ARCHITECTURE_INDEX.md — v15 → v16; §1.19 row added; §8 timeline S1304 row added; frontmatter last_verified bump; owner-line updated with v16 entry"
  - "docs/research/OPEN_ARCS.md — Group 1300 in-progress row current-child advanced from 'S1303 SIGN-clean (commit-gated) + S1304 queued' to 'S1304 SIGN-clean (commit-gated) + S1305 queued'; 2 reconciliation notes added (S1304 open, S1304 close); next-expected pointer rotated to Category H Runtime Memory Correctness"
  - "docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md (this doc)"
  - "00-START-NEXT-SESSION.md — rotated to S1305 mission spec (Category H Runtime Memory Correctness — narrow scope, Redis-loss + lru_cache staleness only)"
key_findings:
  - "**PARTIAL INVALIDATION of S1301 §19 D3 via S1304 verifier-loop before propagation.** S1301 §19 D3 broadly hypothesized both `DocumentEmbedding.source_type` + `ingested_via` are orphan-writes populated at ingestion but never read by any retrieval path. S1304 verifier-loop applied S1303 §14 F4-CANDIDATE discipline (owner-model-qualified consumer inventory required, keyword grep insufficient). Direct file:line read at `content/embeddings.py:965-973` confirmed `semantic_search_sync` applies `DocumentEmbedding.objects.filter(source_type__in=['internal', 'user_upload'])` at :971 and `.filter(source_type__in=['web', 'spider', 'api'])` at :973 as `source_filter` branch (`internal_only` / `external_only`) — this is an **owner-model-qualified consumer**. Additional presentation-time read at :1007 (`source_type=getattr(embedding, 'source_type', 'unknown') or 'unknown'`). Rigby bonus cycle 1 grep verified an extra citation at :904 (async-path SearchResult presentation, nice-to-have). **Verdict: only `ingested_via` remains F1-CANDIDATE orphan** — all 3 write-sites use fixed string constants (`'sync_docs'` at `sync_docs_index_to_documents.py:394`; `'backfill'` at `core/tasks_agents.py:4223/4290/4351`; `'unknown'` default at `content/embeddings.py:654/753`); zero owner-model-qualified read consumers per grep + `content/admin.py:146-164` (not in DocumentEmbeddingAdmin `list_display`) + `content/serializers.py:104-118` (not in DRF field list). F1-CANDIDATE status pending §19 R1 full-tree recheck. **Sets library pattern: verifier-loop before Rigby SIGN prevents sibling-audit hypothesis propagation into library-wide false consensus.**"
  - "D6 HIGH — `build_docs_provenance` unscheduled. Positive beat-schedule evidence via `core/celery.py:495-499` sole `refresh-docs-corpus-daily` entry (crontab hour=4 minute=0 = 04:00 Denver daily) + inside `refresh_docs_corpus` at `core/tasks.py:5803` the cascade call sites at `:5900` (build_docs_index), `:5901` (build_rag_corpus), `:5902` (sync_docs_index_to_documents). NO `build_docs_provenance` call site in `core/tasks.py`. Absence-of-refs sweep supplementary: 3 files reference the command — the command itself, sibling `backfill_doc_provenance.py`, and `td_handlers_ops.py:5573-5576` (error-path suggestion). Provenance rebuild is manual-only. Combined with D2 `lru_cache(1)` staleness gap at `td_handlers_ops.py:78-93` (no invalidation mechanism; workers serve stale filter results until process restart) this is the **canonical E→D write-side/read-side sync drift**."
  - "§18 refined via Rigby SIGN cycle 1 fold #2 — Documentation Manager JobContract at `core/employees/jobs.py:187-395` (registered `:1336` as `docs_manager`, employee_handle=`rigby`) explicitly owns ingestion cascade steps 1-4 per `daily_routine` (`:222-231`): Step 1 build_docs_index, Step 2 build_rag_corpus, Step 3 sync_docs_index_to_documents, Step 4 same with --embed. Authority set at `:238-250` includes `run_docs_cascade_commands=EXECUTE`, `run_drift_observation=OBSERVE`, `modify_docs_files=PROHIBITED`, `open_pull_request=PROHIBITED`. `mission_run_kind=docs_cascade` with `OpsRun + OpsRunEvent` audit contract. **Four specific boundary-maintenance responsibilities have `no explicit named runtime owner`** (softened from initial CRITICAL blanket UNOWNED per playbook §12 bounded-language rule): provenance rebuild cadence, cache invalidation strategy, filter counter observability, row-level `ingested_via` consumer strategy. Recommendation for S1399: either (a) expand Documentation Manager authority to cover `build_docs_provenance` + cache-invalidation trigger, OR (b) create distinct `AIEmployee` handle for boundary maintenance, OR (c) delegate observability to Group 1700 while explicitly assigning provenance-freshness + cache-invalidation to Documentation Manager."
  - "§17 two provenance systems reframed as **complementary, not duplicate** via S1302 §17.3 name-collision-as-methodology. External `docs/_provenance.json` (git-history-derived by `build_docs_provenance`) encodes session origin — read by `search_docs` LOCAL keyword lane filter at `td_handlers_ops.py:5566-5590` via `_load_provenance_docs()` at `:78-93`. Row-level `DocumentEmbedding.source_type` encodes source-of-record enum — read by `kb_tool` PROD pgvector lane via `semantic_search_sync` at `content/embeddings.py:965-973`. `ingested_via` was over-designed for a retrieval consumer that never materialized. **Rigby SIGN cycle 1 fold #4 added 'Complementary today does not imply optimal' guardrail** — unification (single provenance model) vs explicit scoping (documented boundary contract + ADR) is an open design decision routed to §19 R2. Prevents 'complementary' from becoming exoneration of the split."
  - "§19 R5 Cat F ↔ Cat D turn-context → RAG enrichment routed to **design-preparation phase (post-S1399)**, NOT drift or wiring PR. Static evidence is genuinely mixed: 3 signals tilt intentional-separation (design discipline in 8 non-RAG enrichment services at `unified_pa_entrypoint.py`; tool-call-only pattern with two first-class PA tools; thread-memory vs source-memory scope discipline; no event-driven turn-signal wiring — 0 `CONVERSATION_*` streams on EventBus per S1303 §9); 3 signals tilt drift (no design comment explaining absence in enrichment pipeline; no feature flag `RAG_ENRICH_PA_TURNS`/`CORPUS_CONTEXT_ENABLED` guarding absence; asymmetry with `BaseAgent._get_relevant_knowledge_for_task` at `base_agent.py:1439-1510` which does call spider semantic search). **Not resolvable from static evidence — requires product/architecture verdict on operational cost, migration risk, future retrieval requirements.** R5.a (canonicalize separation with design comment + ADR) vs R5.b (implement enrichment as 9th enrichment service) as competing hypotheses."
  - "Confirmed PA turn enrichment does NOT auto-invoke RAG (S1301 §14 + S1303 §9 inherited). S1304 verifier-loop grep confirmed: 0 matches for `search_docs|kb_tool|semantic_search|search_embeddings` in `core/services/unified_pa_entrypoint.py`. Enrichment pipeline has 8 services (intelligence_enricher, blog_performance, domain_context, spider_trends, advisor_context, platform_briefing + 2 more per S1303 Agent 2 partial read); none touch RAG."
  - "Agent knowledge pipeline confirmed spider-fed, NOT corpus-fed. `BaseAgent._get_relevant_knowledge_for_task()` at `core/agents/base_agent.py:1439-1510` calls `spider_semantic_search.semantic_search_with_db_embeddings()` at :1469-1471. Agents access knowledge through learned knowledge layer (spider data → learning bridges → AgentKnowledgeSource → prompts). Corpus is not in this chain. This is a design choice with clear rationale (agents learn from execution, not docs); boundary working as intended."
  - "Two god-service candidates: `td_handlers_ops.py` = 6290 lines (exceeds playbook §13 3000-line refactor threshold; owns entire retrieval-side boundary surface including `search_docs` + `kb_tool` handlers + provenance filter + `_load_provenance_docs` cache; refactor candidate — split by tool namespace). `doc_claim_verification.py` = 3275 lines (AT threshold; framework provides cohesion via single verifier + 40+ claim registry; lazy imports + no circular deps reduce coupling; size justifiable given responsibility scope)."
  - "21.5% corpus-completeness gap in provenance filter — 464 UNKNOWN / 2156 docs in `docs/_provenance.json._meta.confidence_breakdown` (inherited from S1301 §14.2). Root cause per Agent 5 doc analysis: docs predating the session-NNNN convention (introduced Session 1144) OR bulk commits lacking session attribution. **NOT a filter mechanism bug** — provenance-index-completeness signal. Whether the gap should shrink is a corpus-completeness question whose remediation belongs to the ingestion side (§19 R3 + R6)."
  - "Per-component maturity verdicts (playbook §12 bounded language, S1274 continuous-language rule applied): ingestion cascade PARTIAL (cascade operates daily on beat; step 4 async fan-out not gated by beat completion; hash-delta gating edge-case fragile per Agent 3 SPECULATIVE; step 3 idempotency not verified); provenance filter WORKING (mechanism sound but 21.5% UNKNOWN input coverage + counters lack operator visibility + cache staleness gap); row-level provenance write path EXPERIMENTAL (`source_type` wired with 2 qualified consumers; `ingested_via` F1-CANDIDATE pending §19 R1 full-tree recheck); E↔D boundary as a whole PARTIAL (functional but not mature; ownership undefined for boundary-maintenance responsibilities; provenance rebuild unscheduled; cache invalidation absent; observability response-only; cascade documentation unpublished)."
  - "§19 downstream routing (updated post-SIGN): R1 full-tree `ingested_via` F1-CANDIDATE verification per S1303 §14 discipline (HIGHEST priority follow-on — do first); R2 provenance-system reconciliation design (unify or explicit scoping) → S1399 canonical summary + S1302 P2 arc handoff; R3 rebuild cadence + cache invalidation design (add to beat OR file-watcher OR Redis TTL) → Cat E docs-governance owner; R4 boundary ownership assignment → S1399 canonical summary; R5 turn-context → RAG enrichment design decision (canonicalize separation vs implement enrichment) → design-preparation phase post-S1399; R6 publish `docs/topics/docs-ingestion-cascade.md` → Cat E docs-governance owner; R7 filter-drop telemetry → Group 1700 Observability arc; R8 S1301 follow-up classifier precedence bug (standalone bugfix, NOT blocking Group 1300 arc)."
open_decisions_carried_forward:
  - "S1304 SIGN isolation pin `pa-2614a91a920642fa` retirement — SIGN cycles 1+2 complete + SIGN-clean; pin may retire at Chris's discretion after commit (same pattern as S1301+S1302+S1303 retire at their respective session closes)."
  - "S1305 launch cadence — playbook default is 'immediate on session open'. Since S1304 commit-gate resolves this session via 'push everything to main using the --admin flag if needed' directive, S1304 artifacts should land on `main` before S1305 open. S1305 branches off `main` (not stacked)."
rigby_sign_cycle_1:
  fresh_isolation_pin: "pa-2614a91a920642fa"
  pin_title: "S1304 SIGN — Memory Domain (Categories E↔D) Documentation Corpus ↔ RAG Boundary Audit pressure-test (isolation)"
  ownership_verified: "chris (via `platform_config_tool overview` confirmation of `service_context: local` before pin creation on arc pin `pa-aa54193f240f4846`)"
  provisional_verdict: "SIGN-with-edits (2 fold cycles planned). Rigby independently grep-verified load-bearing claims 1-4 via her own `repo_tool` reads. She confirmed the S1301 §19 D3 partial-invalidation is correct at `content/embeddings.py:965-973` + `:1007` and found an additional citation at `:904` (async-path SearchResult presentation) as bonus. She confirmed `refresh_docs_corpus` does NOT call `build_docs_provenance` via direct `core/tasks.py` inspection. She confirmed 0 RAG imports in `unified_pa_entrypoint.py` via search."
  must_fix_folded_4_edits:
    - "Fold #1 — D6 beat-schedule positive citation added. `core/celery.py:495-499` sole `refresh-docs-corpus-daily` entry quoted with 4-line dict + `core/tasks.py:5803` + `:5900-5902` cascade call sites showing no `build_docs_provenance` call. Absence-of-refs sweep repositioned as supplementary. Rationale: 'not scheduled' is load-bearing per playbook §14 evidence rules; grep-absence alone is insufficient — positive schedule-definition citation required."
    - "Fold #2 — §18 UNOWNED reframed with Documentation Manager JobContract positive evidence. Cited `core/employees/jobs.py:187-395` mission text + `daily_routine` (`:222-231`) + authority set (`:238-250`) + `mission_run_kind` (`:235`) + OpsRun contract (`:295-301`) + registration at `:1336`. Refined ownership matrix acknowledges cascade steps 1-4 ARE owned by Documentation Manager (`docs_manager`, employee_handle=`rigby`); four specific boundary-maintenance responsibilities (provenance rebuild cadence, cache invalidation, filter observability, row-level `ingested_via` strategy) remain 'no explicit named runtime owner'. Softened 'CRITICAL' → 'HIGH' for boundary-as-a-whole per playbook §12 bounded-language rule. Added explicit bounded-language check paragraph."
    - "Fold #3 — F4-CANDIDATE discipline reinforced on `ingested_via` per S1303 §14 methodology. §9 D→E edge cell rewritten from 'never read' to 'no owner-model-qualified consumer identified per F4-CANDIDATE discipline pending §19 R1 verification'. §14 D7 explicit F4-CANDIDATE hedge added. No bare 'never read' or 'dead' language remaining on `ingested_via` — every claim explicitly labeled F1-CANDIDATE pending full-tree recheck."
    - "Fold #4 — §17 'complementary' reframe augmented with explicit 'Complementary today does not imply optimal' guardrail. Titled paragraph names two design paths (R5.a canonicalize separation OR R5.b unification path) + routes to §19 R2 provenance-system reconciliation design. Prevents 'complementary' from becoming rhetorical exoneration of the two-system split."
  additional_observations:
    - "Q1 partial S1301 §19 D3 invalidation confirmed via Rigby's own grep — she independently verified `.filter(source_type__in=[...])` at :971/:973 and found bonus citation at :904 (async-path SearchResult presentation) that S1304 v0.2 missed. Nice-to-have addition, not SIGN-blocking."
    - "Q5 §17 'complementary' framing legitimate as descriptive reframe but 'risks letting the architecture off the hook unless explicit architecture debt / unify-or-scope guardrail added' — fold #4 satisfies."
rigby_sign_cycle_2:
  same_isolation_pin: "pa-2614a91a920642fa (fresh pin preserved across cycles per playbook §15 fold-cycle pattern)"
  final_verdict: "SIGN-clean. Verification pass (not structural rewrite). Cycle 2 confirmed all 4 folds via her own `repo_tool` search + read tools: (1) fold #1 D6 now includes positive beat-schedule evidence quoting the sole beat entry with a concrete file:line citation + cascade call sites, no 'grep returned 0' standing alone; (2) fold #2 §18 leads with positive Documentation Manager JobContract evidence + refined ownership matrix + softened bounded language + explicit bounded-language check paragraph; (3) fold #3 §9 D→E cell + §14 D7 F4-CANDIDATE hedge intact — no bare 'never read' language remaining; (4) fold #4 §17 titled paragraph names both design paths + routes to §19 R2. Bonus check: `content/embeddings.py:904` async-path citation is 'nice-to-have, not required for SIGN' — current `:965-973` + `:1007` citations are sufficient to establish 'has at least one consumer'."
  bonus_checks_passed:
    - "All 4 fold locations verified via `repo_tool.search` + `repo_tool.read_file` independent reads"
    - "Bounded-language check paragraph reads correctly; boundary-as-a-whole 'HIGH' properly distinguished from cascade-steps-1-4 'LOW' + build_docs_provenance 'HIGH' + lru_cache 'HIGH' + ingested_via 'HIGH pending R1' + filter observability 'MEDIUM pending Group 1700'"
    - "§17 'complementary today does not imply optimal' paragraph correctly frames unification vs explicit scoping as open design decision; explicitly warns not to treat complementary as exoneration"
  no_edits_required: true
next_session_readiness:
  - "S1305 mission is well-scoped: Category H Runtime Memory Correctness (narrow scope — Redis-loss + `lru_cache(1)` staleness only). Per parent §5 P5: 'not ops-in-general' — explicit anti-scope per parent §7: Celery worker RSS, PID cache, OBJC_DISABLE_INITIALIZE_FORK_SAFETY, macOS SIGSEGV all remain OUT of scope. Inherits from S1304: D2 lru_cache(1) staleness gap at `td_handlers_ops.py:78-93` as first-order scope evidence; D6 provenance rebuild cadence unscheduled as related concern (worker restart is the invalidation mechanism); T2 remediation options (worker restart trigger vs file-watcher vs Redis TTL vs Redis-backed store) as candidate design surface. Also inherits from S1302: AgentLearningService Redis-only durability (`agent_learning_service.py:462-483` writes via `redis_client.hset` at :476 with no `.expire()` — Redis-loss on worker recycle risk)."
  - "S1304 verified the boundary-lens audit pattern works — deliberately smaller scope than P1-P3 (per parent §5 P4 rationale) still produces load-bearing findings when focused on integration handoffs rather than category internals. Fourth consecutive Group 1300 child. Only second child to SIGN-clean in 2 cycles (matching S1303; S1301 = 1, S1302 = 3)."
  - "S1304 established: **verifier-loop before Rigby SIGN prevents sibling-audit hypothesis propagation into library-wide false consensus.** S1301 §19 D3 broadly hypothesized both row-level provenance fields are orphan; direct file:line read at `content/embeddings.py:965-973` invalidated half the hypothesis (source_type IS read). Had S1304 accepted S1301's broad framing without verifier-loop, the invalid claim would have propagated to S1302 §17.3 reframe (both AgentMemory + ConversationMemory Django model duplicates), S1303 §14 F4-CANDIDATE discipline (context_used + agent_results), and eventually hardened into library-wide false consensus. The pattern: **before folding sibling-audit hypotheses into a new audit, verify via direct file:line read at the specific consumer sites named in the hypothesis, applying F4-CANDIDATE discipline (owner-model-qualified consumer inventory required).**"
  - "F1-CANDIDATE status for `ingested_via` orphan-write is now the load-bearing follow-on for §19 R1 — full-tree recheck required before declaring dead code per S1303 §14 discipline. R1 verification methodology: enumerate every file that imports `DocumentEmbedding`; for each, check whether `.ingested_via` is accessed via ORM query, values(), only(), serializer field, admin list_display, template context, or business logic. Only after zero owner-qualified consumers confirmed across full tree can deprecation PR proceed. Recommendation: R1 becomes S1399 canonical summary responsibility OR standalone follow-on before deprecation."
memory_rule_touches:
  - "feedback_pa_local_verify_ownership.md — S1304 confirmed ownership on both arc pin (`pa-aa54193f240f4846`) and fresh isolation SIGN pin (`pa-2614a91a920642fa`) via `platform_config_tool overview` returning `service_context: local` before first PA call."
  - "feedback_claude_directs_rigby_then_verifies.md — S1304 open executed the pattern: service_context: local check directive → Rigby ran `platform_config_tool overview` → Claude verified. D12/D13 routing directive → Rigby ran default-lean framing → Chris ratified 'agree all' → Claude proceeded. SIGN routing: Claude directed the pressure-test on isolation pin → Rigby ran independent grep verification → Claude folded edits → Rigby verified folds → SIGN-clean."
  - "feedback_verify_before_deleting_dead_code.md — LOAD-BEARING for S1301 §19 D3 partial invalidation + `ingested_via` F1-CANDIDATE hedge. Applied memory-rule discipline: cannot claim 'dead' without owner-model-qualified consumer inventory. Direct file:line read at `content/embeddings.py:965-973` invalidated half of S1301's broad claim; `ingested_via` claim held as F1-CANDIDATE pending §19 R1 full-tree recheck. **The pattern-application that saved S1304 from propagating a wrong verdict into a sibling audit — the same discipline S1303 used to catch Agent-6's F4 overreach applies to catching hypothesis-inheritance overreach from sibling audits.**"
  - "feedback_verifier_loop_pattern.md — S1304 exercised the pattern: parent-agent verifies EVERY quantitative claim + file path via direct Django ORM read / grep receipt / file read before including in the audit AND before accepting sibling-audit hypotheses as inherited premises. Four load-bearing verifications: (1) source_type consumer read at content/embeddings.py:965-973; (2) search_docs handler location at td_handlers_ops.py:5468; (3) no beat-schedule for build_docs_provenance via grep + core/tasks.py inspection; (4) zero RAG imports in unified_pa_entrypoint.py via grep."
  - "feedback_docs_pipeline_4_step_cascade.md — S1304 audit + INDEX v16 + OPEN_ARCS advancement + handoff all get pushed to Documents + embedded via the 4-step cascade after Chris commit. The Documentation Manager `docs_manager` JobContract at `core/employees/jobs.py:187-395` explicitly owns this cascade (S1304 §18 finding). Cascade fires next 04:00 Denver beat after merge; embed step is async fan-out."
  - "feedback_no_fluff_verify_truth.md — S1304 §17 'complementary today does not imply optimal' guardrail added per Rigby SIGN cycle 1 fold #4 explicitly to prevent the 'complementary' descriptive reframe from becoming rhetorical exoneration of the two-provenance-system split. Bounded language throughout §18 (softened CRITICAL → HIGH for boundary-as-a-whole; distinguished cascade-steps-1-4 LOW ownership from build_docs_provenance HIGH no-owner)."
followup_queue:
  - "S1305 Runtime Memory Correctness (Category H narrow scope — Redis-loss + `lru_cache(1)` staleness only). Inherits S1304 D2 + D6 + T2 as first-order scope evidence. Also inherits S1302 AgentLearningService Redis-only durability finding."
  - "S1399 Group 1300 Canonical Summary — cross-cutting synthesis. Must resolve: (a) row-level orphan-write pattern classification methodology inherited from S1302 §17 F2 narrowing + S1303 §14 F4-CANDIDATE discipline + S1304 verifier-loop partial-invalidation pattern; (b) `ingested_via` F1-CANDIDATE full-tree verification (§19 R1) — HIGHEST priority follow-on; (c) provenance-system reconciliation design proposal (§19 R2 — unification vs explicit scoping); (d) boundary ownership assignment (§19 R4 — expand Documentation Manager authority OR create distinct employee OR delegate to Group 1700); (e) LAND FIRST-INVENTORY §3.N ROW for Cat F (from S1303 R5); (f) MemoryPromotionService Cat B vs Cat C category assignment (S1302 F6); (g) spider_data_bridge naming reconciliation (S1302 F5); (h) write-authority framework anchor recommendation for PLATFORM_INVENTORY §3.13 update (S1302 T10)."
  - "Group 1700 Observability filter-drop + dead-code / producer-only detection telemetry follow-on + EventBus adoption spec for Cat F (S1303 R2) + retrieval-side filter counter observability (S1304 §19 R7)."
  - "R1 full-tree `ingested_via` F4-CANDIDATE verification for `DocumentEmbedding.ingested_via` (S1304 §19 R1) — HIGHEST PRIORITY follow-on; F1 counterpart of S1303 R1.a/b/c methodology applied to different domain."
  - "R5 turn-context → RAG enrichment design decision (Cat F → Cat D wiring per S1303 §19 R3 + S1304 §19 R5) — delegated to design-preparation phase post-S1399; requires product/architecture verdict."
  - "R6 publish `docs/topics/docs-ingestion-cascade.md` — 4-step flow + preconditions + postconditions + failure/recovery + cadence + scheduling policy. Delegated to Cat E docs-governance owner (Documentation Manager)."
  - "R8 S1301 follow-up classifier precedence bug (`build_docs_provenance` body-mention over subject-tag weighting) — standalone bugfix, NOT blocking Group 1300 arc; scope: how many other docs are misclassified?"
  - "Design-preparation ADR for provenance-system reconciliation (post-S1399) — write authority framework for row-level fields + external index. Filed by S1304; carries forward."
owner: claude (drafted S1304)
---

# Session 1304 — Memory Documentation Corpus ↔ RAG Boundary (Group 1300 Child P4)

## Session shape

**Mission (opened by Chris short command 2026-07-01):** *"start research group 1304"* — the playbook §21 continuation form on the fourth child audit under Research Group 1300 (Memory / Knowledge / Embeddings). Categories E ↔ D Documentation Corpus ↔ RAG Boundary exclusive **boundary lens** per parent §5 P4 slot. Deliberately smaller than P1-P3 per parent rationale ("smaller scope; benefits from §3.14 audit landing first (S1301 shipped)").

**Executed contract:**
- Playbook §21 continuation → §11.2 20-section child-audit template.
- Playbook §13 6-parallel-Explore sub-agent sweep (Models & Persistence / Services & Runtime Flows / APIs Tools Tasks Commands / Integrations & Cross-Domain / Documentation & Prior Research / Drift Debt Ownership & Maturity).
- Parent-agent verifier-loop spot-checks per playbook §13 synthesis step 2 — front-ran S1301 §19 D3 broad hypothesis (partially invalidated), `search_docs` handler location, `build_docs_provenance` beat-schedule absence, zero RAG imports in PA enrichment.
- Playbook §15 stage-scoped Rigby routing: full SIGN required on child audits; routed to a fresh isolation pin (`pa-2614a91a920642fa`) per fresh-pin discipline. Two fold cycles (4-must-fix cycle 1 + verification-only cycle 2).
- Playbook §16 commit policy: draft-first, Chris commit-gate. Chris commit-gate resolved this session via explicit "Proceed to close artifacts, and prepare to push everything to main using the --admin flag if needed" instruction.

**Session close criteria met per playbook §14 completion contract:**
- Audit doc at `status: draft`, `sign_status: SIGN-clean`, all 20 sections populated with cited evidence + honest UNKNOWNs + Rigby SIGN fold history (v0.1 skeleton → v0.2 synthesis → v0.3 SIGN cycle 1 fold → v0.4 SIGN cycle 2 verification pass).
- Rigby SIGN cycles 1 + 2 → SIGN-clean after one 4-must-fix fold cycle + one verification pass.
- INDEX v16 registration (§1.19 + §8 timeline row + frontmatter `last_verified` bump + owner-line update).
- OPEN_ARCS Group 1300 row current-child advancement + 2 reconciliation notes (S1304 open, S1304 close).
- This handoff.
- 00-START-NEXT-SESSION.md rotated to S1305.

## What the audit found (executive)

Categories E (Documentation / Research Knowledge System — S1273 §3.15) ↔ D (RAG / Document Loading — S1273 §3.14 + S1301 P1 audit) boundary is **FUNCTIONAL but UNMATURE** (playbook §12: PARTIAL maturity across all 4 boundary components). Core mechanisms work: (a) the 4-step ingestion cascade runs daily via the `refresh_docs_corpus` beat task at 04:00 Denver (`core/tasks.py:5803` + `core/celery.py:495-499`); (b) two retrieval lanes are wired unambiguously (`search_docs` LOCAL keyword at `td_handlers_ops.py:5468`; `kb_tool semantic_search` PROD pgvector); (c) the provenance filter mechanism is logically sound and correctly implements the S1301 §14 "missing provenance = exclude by design" contract.

**Five G-level executive gaps discovered** (§1 audit body):

1. **G1 — Two provenance systems partially decoupled** (S1301 §19 D3 refined via S1304 verifier-loop). External `docs/_provenance.json` (git-history-derived) and row-level `DocumentEmbedding.source_type` + `ingested_via` (migration 0044, 2026-03-01) coexist. **Partial invalidation:** `source_type` HAS owner-model-qualified consumers (`content/embeddings.py:965-973` `semantic_search_sync` source_filter branch + `:1007` presentation). Only `ingested_via` remains F1-CANDIDATE orphan pending §19 R1 full-tree recheck.

2. **G2 — Provenance-index rebuild cadence unscheduled**. `build_docs_provenance` is load-bearing for the `search_docs` filter but has zero beat entries. Provenance staleness between manual runs is silent and undetectable.

3. **G3 — `lru_cache(1)` staleness at boundary**. `_load_provenance_docs()` at `td_handlers_ops.py:78-93` caches per-process indefinitely; no invalidation when disk file changes. Combined with G2, canonical E→D write-read sync drift.

4. **G4 — Filter counters land in response payload only** (S1301 §14.2 confirmed). `excluded_missing_provenance` + `excluded_mismatch` at `td_handlers_ops.py:5585-5590` visible only to callers who inspect the tool response. No log, metric, or alert.

5. **G5 — Boundary is unowned for maintenance responsibilities**. Documentation Manager `AIEmployee` handle at `core/employees/jobs.py:187-395` owns ingestion cascade steps 1-4 explicitly; four specific boundary-maintenance responsibilities (provenance rebuild cadence, cache invalidation strategy, filter observability, row-level `ingested_via` consumer strategy) remain "no explicit named runtime owner" per bounded-language refinement.

**Cat F ↔ Cat D reframe:** S1303 §9 OBSERVED GAP + §19 R3 turn-context → RAG enrichment hypothesis. **Not resolvable from static evidence** — 3 signals tilt intentional-separation vs 3 signals tilt drift; routed to §19 R5 as design-decision hypothesis for design-preparation phase (post-S1399), NOT drift or wiring PR.

**Two verifier corrections during synthesis** — captured in `verifier_loop:` frontmatter:

1. **S1301 §19 D3 partial invalidation.** S1301 broadly hypothesized both `source_type` + `ingested_via` are orphan-writes. Direct file:line read at `content/embeddings.py:965-973` confirmed `semantic_search_sync` applies `.filter(source_type__in=['internal', 'user_upload'])` at :971 and `.filter(source_type__in=['web', 'spider', 'api'])` at :973 as `source_filter` branch. Additional presentation-time read at :1007. **Only `ingested_via` remains F1-CANDIDATE orphan.** Rigby SIGN cycle 1 independently verified via her own grep + found bonus citation at `:904` (async-path SearchResult presentation).

2. **§18 UNOWNED refined via Documentation Manager evidence.** Initial audit claimed "E↔D boundary UNOWNED as a whole" as CRITICAL. Direct read of `core/employees/jobs.py:187-395` `DOCUMENTATION_MANAGER` `JobContract` (registered `:1336` as `docs_manager`) revealed cascade steps 1-4 ARE explicitly owned. Softened to bounded language: "no explicit named runtime ownership for [specific four responsibilities]" instead of blanket UNOWNED. Boundary-as-a-whole softened CRITICAL → HIGH.

Both corrections shipped to Rigby BEFORE final v0.2 handoff to SIGN, so cycle 1 focused on substantive additions (positive citations, evidence quotes, bounded-language reframes) instead of evidence corrections. This is the pattern S1304 validates: **catch broad hypothesis overreach from sibling audits parent-side first, so SIGN cycles focus on substantive additions**. Consequence: second child audit to reach SIGN-clean in 2 cycles (matching S1303 discipline; S1301 = 1, S1302 = 3).

**§19 downstream routing:**
- R1 full-tree `ingested_via` F1-CANDIDATE verification per S1303 §14 discipline. HIGHEST priority follow-on.
- R2 provenance-system reconciliation design (unify or explicit scoping) → S1399 canonical summary + S1302 P2 arc.
- R3 rebuild cadence + cache invalidation design → Cat E docs-governance owner.
- R4 boundary ownership assignment → S1399 canonical summary.
- R5 turn-context → RAG enrichment design decision → design-preparation phase (post-S1399).
- R6 publish `docs/topics/docs-ingestion-cascade.md` → Cat E docs-governance owner.
- R7 filter-drop telemetry → Group 1700 Observability arc.
- R8 S1301 follow-up classifier precedence bug (standalone bugfix, NOT blocking Group 1300).

## What did NOT get done

- **No implementation PRs.** Playbook §14.5 forbids implementation during research; the audit is design-input, not design.
- **No full-tree `ingested_via` verification sweep.** By design — filed as §19 R1 for follow-on research per memory rule `feedback_verify_before_deleting_dead_code.md`.
- **No `RAGObservabilityService` wiring confirmation.** Service exists at `core/services/rag_observability_service.py` (664 lines) but whether it is actually called by the retrieval path remains SPECULATIVE per Agent 2 §1. Not blocking S1304 boundary-lens scope.
- **No landing of Cat D E↔D boundary §3.N row in `platform_architecture_inventory.md`.** Per parent §5, that lands in S1399 canonical summary — audit produces the candidate content, not the row.
- **No design-preparation ADR for provenance-system reconciliation.** By design — that is R2 follow-on for design-preparation phase.
- **No F5 Cat F ↔ Cat D design decision.** By design — routed to R5 design-preparation phase; NOT resolvable from static evidence in-audit.

## Session-close artifacts on the working tree (committed by this handoff)

```
docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md   [new, ~1130 lines]
docs/research/ARCHITECTURE_INDEX.md                                    [modified, v15 → v16, §1.19 + §8 timeline S1304 row]
docs/research/OPEN_ARCS.md                                             [modified, Group 1300 row advanced + 2 reconciliation notes + last_updated]
docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md                 [new, this doc]
00-START-NEXT-SESSION.md                                               [modified, S1305 mission spec]
```

## Ready-to-commit single gesture

```bash
git add docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md \
        docs/research/ARCHITECTURE_INDEX.md \
        docs/research/OPEN_ARCS.md \
        docs/handoffs/SESSION_1304_MEMORY_DOCS_RAG_BOUNDARY.md \
        00-START-NEXT-SESSION.md
git commit -m "docs(session-1304): Memory Docs Corpus ↔ RAG Boundary audit + INDEX v16"
git push -u origin docs/session-1304-memory-docs-rag-boundary
gh pr create --title "docs(session-1304): Memory Docs Corpus ↔ RAG Boundary audit + INDEX v16" --body "..."
gh pr merge --admin --squash --delete-branch
```

Chris commit-gate: **RESOLVED** — Chris explicit "Proceed to close artifacts, and prepare to push everything to main using the --admin flag if needed" instruction 2026-07-01.

## Reference — where things are

- **S1304 audit:** `docs/research/domains/memory/1304_memory_docs_rag_boundary_audit.md`
- **Parent doc:** `docs/research/domains/memory/1300_memory_domain_scoping.md`
- **Sibling audits (Cat D, Cat A+B+C, Cat F):** `docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md` + `1302_memory_persistence_architecture_audit.md` + `1303_memory_conversational_thread_memory_audit.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **Inventory anchor:** `docs/research/platform_architecture_inventory.md` §3.14 (Cat D) + §3.15 (Cat E)
- **Runtime anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **Category E governance:** `docs/00-START-HERE/DOC_LIFECYCLE.md` §2c (inventory-wins-on-conflict)
- **Category D LOCAL lane:** `core/rag.py` + `core/services/td_handlers_ops.py:5468` (`_handle_search_docs`) + `docs/topics/local-askdocs.md` (S1108 CANONICAL boundary doc)
- **Category D PROD lane:** `core/rag_integration.py` + `core/services/td_handlers_ops.py:5379` (`_handle_kb_browse` `semantic_search` action) + `content/embeddings.py:931-1029` (`semantic_search_sync`)
- **Row-level provenance write path (source_type + ingested_via):** `content/models.py:707-918` (DocumentEmbedding) + `content/embeddings.py:45-63` (`_derive_source_type`) + `sync_docs_index_to_documents.py:385-395`
- **Row-level provenance read path (source_type ONLY):** `content/embeddings.py:965-973` (semantic_search_sync source_filter) + `:1007` (SearchResult presentation) + Rigby bonus `:904` (async-path presentation)
- **External provenance write:** `core/management/commands/build_docs_provenance.py` (unscheduled — D6)
- **External provenance read:** `core/services/td_handlers_ops.py:78-93` (`_load_provenance_docs` `@lru_cache(maxsize=1)`) + `:5566-5590` (`_handle_search_docs` filter application) + `:5585-5590` (counter payload — D8 no observability)
- **Ingestion cascade beat entry:** `core/celery.py:495-499` (`refresh-docs-corpus-daily` crontab hour=4 minute=0)
- **Ingestion cascade task:** `core/tasks.py:5803` (`refresh_docs_corpus`) + `:5900-5902` (build_docs_index + build_rag_corpus + sync_docs_index_to_documents call sites)
- **Documentation Manager JobContract:** `core/employees/jobs.py:187-395` (DOCUMENTATION_MANAGER) + `:1336` (registered as `docs_manager`)
- **Fresh SIGN pin (retirable at Chris discretion):** `pa-2614a91a920642fa`

## Pin state

- **Arc pin (Group 1300 continuity):** `pa-aa54193f240f4846` — carries S1300 + S1301 + S1302 + S1303 + S1304 mission-side context. Preserved for S1305 continuity.
- **SIGN isolation pin (S1304 only):** `pa-2614a91a920642fa` — SIGN cycles 1 + 2 complete + SIGN-clean. May retire at Chris's discretion after commit.

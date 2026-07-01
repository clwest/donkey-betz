---
title: "S1401 Revenue Category A — Opportunity Discovery + Scoring Architecture Audit"
status: draft (Rigby SIGN-clean cycle 2 High confidence; awaiting Chris commit-gate — flips to `active` per playbook §16 on commit)
authority: research
category: child_audit
session: 1401
date: 2026-07-01
research_group: 1400
child_slot: A
domain_slug: revenue
parent_doc: docs/research/domains/revenue/1400_revenue_domain_scoping.md
authors: Claude Code (Chris directed via short command "start research group 1401" + Chris "agree all" on D30 sequential + D31 retain arc pin)
supersedes: none
sign_status: SIGN-clean cycle 2 (High confidence, 2026-07-01) after SIGN-with-edits cycle 1 fold — 4 folds (2 must-fix + 2 nice-to-have) applied and Rigby SIGN-clean-confirmed on isolation pin pa-16d8b24d30e7a7d8. Pin retired at S1401 close per playbook §15.
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                          # v2 process anchor (S1276)
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                 # OS (S1278) — arc-open contract
  - docs/research/OPEN_ARCS.md                                         # In-progress row: Group 1400 current-child = S1401
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md       # parent scoping (S1400)
  - docs/research/platform_architecture_inventory.md §3.32 + §4.9      # S1273 inventory + cross-domain flow
  - docs/research/platform/cross_domain_integration_audit.md §2.4 + §3.7 + §6.2 + §14 finding #36  # S1274
  - docs/research/domains/memory/1399_memory_canonical_summary.md §4   # F1/F2/F3/F4 methodology inheritance
  - docs/PLATFORM_INVENTORY.md                                         # runtime counts anchor
  - docs/PLATFORM_WHAT_IT_IS.md                                        # narrative anchor
scope: Full audit of Category A (Opportunity Discovery + Scoring) — 5 owned models + 8 services + 2 agents + 1 WebSocket consumer + `OPPORTUNITY_SCORED` EventBus event + Category-A subset of REST/PA-tool/Celery/management-command surface; grounded in verified runtime evidence at `main` HEAD `ae30a1fe`.
non_goals:
  - Categories B/C/D/E/F child audits (each has its own S1402–S1406 slot)
  - Opportunity → Initiative wiring implementation (documented; owned by Child E per D28)
  - Runtime-owner JobContract creation (deferred to Employee OS 1200s arc)
  - Full producer inventory across Categories A + F (Category F child audit S1406 completes the picture)
  - EventBus adoption sweep (Group 1700 Observability arc scope)
  - Sports/DBAO deep integration (Group 1500 scope)
  - Implementation PRs
verifier_loop: |
  v1 (2026-07-01, S1401): draft after Chris "agree all" ratification on D30 sequential + D31 retain arc pin.
  §13 six-parallel-Explore sweep launched via 6 Agent-tool calls (Models / Services / APIs+Tools+Tasks+Commands / Integrations / Docs+Prior-Research / Drift+Debt+Ownership+Maturity). Each Explore agent returned a structured report with file:line citations.

  Parent-Claude verifier-loop spot-checks (per playbook §13 "trust but verify"):

  1. **Sports lane verdict VERIFIED.** Direct read of `intelligence/sports_opportunity_generator.py:83`:
     `opportunity = OpportunityTracking.objects.create(...)`. Sports writes to `intelligence.models.OpportunityTracking` (a separate model in the `intelligence` app label), NOT to `core.models_unified_system.Opportunity`. All three sub-agents (Agents 1, 2, 4) converged on this finding; direct read confirms. **Resolves §12.1 Q6 definitively.**

  2. **`score_opportunities_from_spider_data` beat-schedule correction.** Agent 3 claimed "NOT SCHEDULED — on-demand only." Cross-check of `docs/WIREMAP.md:170`, `docs/handoffs/SESSION_872_COMPLETE.md:147`, `docs/archive/sessions/SESSION_223_OPPORTUNITY_ENGINE.md:124` all state the task is scheduled hourly. **Agent 3's negative claim is downgraded to UNKNOWN pending Rigby-side `PeriodicTask` row inspection** — documented as scheduled by three independent doc sources, but no PeriodicTask row grep is possible from this local checkout (django-celery-beat rows are DB state, not source-controlled).

  3. **Celery queue-routing conflict discovered.** Grep of `core/settings.py` finds `score_opportunities_from_spider_data` defined TWICE in `task_routes` — line 1277 (`'queue': 'long_running'`) and line 1484 (`'queue': 'content'`). Later definition wins in dict merging → effective queue is `content`. **NEW FINDING (F1-CANDIDATE debt):** routes-dictionary duplication is silent (no runtime error) and drift-prone. Documented in §15 debt matrix.

  4. **`publish_opportunity_scored_event` call site VERIFIED.** Direct read of `core/services/scoring_dispatcher.py:41` confirms the publish invocation. Publisher wire: higher-level dispatcher → `_publish_scoring_event(...)` (helper at line 21) → `publish_opportunity_scored_event(...)` (line 41) → `EventStream.OPPORTUNITY_SCORED` = `"mi:opportunity_scored"`. Agent 3 named `:282,480` (higher-level caller lines per S1274 §6.2 registry) — both are correct but name different things; audit uses the direct-publish site at line 41 as the load-bearing citation.

  5. **OpportunityScannerConsumer NEW FINDING.** Direct read of `core/consumers_base.py:2510-2570` confirms Agent 3's characterization: read-only WebSocket listener, room group `opportunity_scanner`, initial payload declares `domains_monitored: [SPORTS_BETTING, CRYPTO, TRADING, REAL_ESTATE]`, streams first 3 opportunities from `intelligence_engine.get_current_opportunities()`. **NEW LOAD-BEARING FINDING:** the consumer reads from `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` — an in-memory realtime source — NOT from `Opportunity.objects.filter(...)`. This means Category A has a **dual opportunity representation**: (a) persistent Django `Opportunity` model (spider + agent + PA-tool ingestion), (b) `intelligence_engine` in-memory realtime source consumed by WebSocket only. Their synchronization is UNKNOWN. Documented as F1-CANDIDATE (provenance drift across dual representations) in §14 drift matrix + §19 R4 follow-on.

  Rigby SIGN routing: fresh isolation pin per playbook §15 (child audits require Full SIGN, not Light; Light SIGN is parent-only). SIGN cycle 1 pending as of frontmatter write.
owner: claude (drafted S1401 v1)
---

# Session 1401 — Category A: Opportunity Discovery + Scoring Architecture Audit

> **Provenance.** Chris typed "start research group 1401" at S1401 open (2026-07-01), invoking the D30/D31 default leans locked at S1400 close. Chris ratified `agree all` (D30 sequential + D31 retain arc pin `pa-34d43795e1b24bd3`) after the Rigby+Chris D30/D31 card was routed. Six parallel Explore agents ran per playbook §13 sub-agent sweep, followed by parent-Claude verifier-loop spot-checks and this synthesis.
>
> **What "done" means for this doc** (per parent §12.3 F.iii + playbook §17 graduation criteria): SIGN-clean on Rigby's full 9-question pressure test; all 28 canonical questions answered with cite / reference / honest UNKNOWN; §12.1 Category A questions from parent doc answered explicitly at §7 Runtime Flows + §10 Event Flows; 15 inherited findings from parent §11.4 cited (not rediscovered); Chris ratification commit-gate satisfied post-fold.

---

## 1. Executive Summary

Category A owns the mainline `Opportunity` model and its scoring surface: 5 owned models (`Opportunity`, `OpportunityScore`, `OpportunityPredictionAccuracy`, `OpportunityDigest`, `OpportunityInteraction`), 8 services spanning core/services + intelligence/ + ml_pipeline/ + top-level core/, 2 agents (`OpportunityScoringAgent`, `OpportunityPipelineAgent`), 1 WebSocket consumer (`OpportunityScannerConsumer`), 1 EventBus event (`OPPORTUNITY_SCORED`), a hourly Celery task (`score_opportunities_from_spider_data`), and a 9-endpoint REST surface. Verified runtime baseline: architecture WORKING (matches S1273 §3.32); research coverage LIGHT (matches parent §11.3 — no CANONICAL topic doc exists).

**Load-bearing findings (S1401 F.iii Category A per parent §12.1):**

- **Sports lane resolved (§12.1 Q6):** `intelligence/sports_opportunity_generator.py:83` writes to a **separate `OpportunityTracking` table** (intelligence.models.py:416), not mainline `Opportunity`. **S1274 §2.4 line 270 MISSING classification remains ACCURATE for mainline `Opportunity`; the correction is that sports is a "separate lane" (writes into `OpportunityTracking` intelligence-side) rather than "missing implementation" (no code path at all).** This resolves the classification-language ambiguity without overturning S1274's finding: mainline `Opportunity` and sports `OpportunityTracking` are two distinct persistence surfaces with no cross-wire.

- **Dual opportunity representation (NEW finding, §14 drift + §19 R1 umbrella):** the WebSocket consumer streams from `intelligence_engine.get_current_opportunities()`, an in-memory realtime source distinct from the persistent Django `Opportunity` model. **Per Rigby SIGN cycle 1 spot-check, this pattern appears at 5 sites in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597) — not just OpportunityScannerConsumer.** Synchronization contract is UNKNOWN.

- **Mainline Opportunity producer inventory (§9 producers, §12.1 Q2):** 4 confirmed producers (`intelligence/spider_opportunity_connector.py:620`, `core/agents/analysis/opportunity_scoring_agent.py`, `core/services/td_handlers_agents.py`, `core/services/income_action_service.py`) + Category F Income/Jobs surface owns additional producers (deferred to S1406). Sports lane isolated to `OpportunityTracking`.

- **F1 provenance-filter drift CANDIDATE (§9 + §14):** writers tag `source` + `metadata['spider_source']` inconsistently across producers (spider connector complete; agent + PA-tool paths sparse); readers (`OpportunityExecutionPipeline`, `OpportunityScannerConsumer`, `OpportunityDraftGenerator`) do not filter on provenance. High-confidence F1 candidate per S1399 §4 methodology.

- **F3 Redis-only durability CANDIDATE (§14):** `intelligence/spider_opportunity_connector.py` uses async Redis (`aioredis.from_url()` + 5-minute cache TTL) as the durability layer for spider-ingestion state, with no DB fallback. If Redis expires before DB write, opportunity data is lost silently. Direct S1399 §4 F3 methodology hit.

- **F2 orphan-write CANDIDATE cluster (§14):** 10-variant Opportunity family + Session Pre-38 partnership_* fields (10 fields) are prime F2 candidates — added optionally with defaults, consumption sites unknown. Requires sibling verifier-loop per S1399 F4 before hardening.

- **Producer overlap resolved (§17 duplicate/overlap):** `OpportunityPipelineOrchestrator` (1,848 LOC) and `OpportunityExecutionPipeline` (541 LOC) are **complementary**, not duplicative: Orchestrator is a transform/analysis service (Dict in → optimized Dict out, 5-stage agent routing), ExecutionPipeline is a materialization service (Opportunity instance → PartnershipProject + CustomWorkflow). No consolidation candidate.

- **Ownership gap CONFIRMED (§18 + inherited S1274 §14 finding #36):** no JobContract wiring, no dedicated beat queue, no CODEOWNERS-style artifact naming Category A owner. Deferred to Child E aggregate + Employee OS arc per D28.

- **Celery queue-routing bug (NEW finding, §15):** `score_opportunities_from_spider_data` is defined twice in `core/settings.py` `task_routes` (line 1277 `long_running`, line 1484 `content`). Later definition wins; effective queue is `content`. Silent drift-prone bug — worth a follow-on cleanup PR (design-preparation, not this audit).

**Recommended next research (§19):** R1 dual opportunity representation reconciliation; R2 `intelligence_engine.get_current_opportunities()` source verification; R3 producer-inventory completion across Category F; R4 F2 corroboration on partnership_* + metadata + expires_at candidate fields.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** (one-sentence purpose)
Category A discovers candidate revenue opportunities from external + internal signals and produces scored, actionable Opportunity records that downstream Category B (Outreach) + Category D (Meeting/Close) + Category E (Attribution) consume.

**Q2 — What problem does it solve?** (business or platform problem)
Without Category A, spider data + AI signals + manual/API-driven opportunity hypotheses have no canonical persistence, no scoring rubric, and no downstream consumers. The mainline `Opportunity` model + its scoring pipeline is the entry point that converts raw signals into revenue-pursuit units the rest of the Revenue pipeline can act on. The domain resolves the S1273 §10.3 UNKNOWN #1 ("Opportunity model exact location + schema"): the model lives at `core/models_unified_system.py:1201` and its 10-variant family lives in the same file + `core/models_engagement_metrics.py`.

**Parent §12.1 Category A F.iii question addressed:** "What IS an Opportunity?" — a persistent Django ORM row with 27 core fields + 10 sibling child models capturing the discovery→scoring→lifecycle→attribution→feedback lifecycle (see §4).

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?** (files, URLs, PA tools, management commands)

### 3.1 Files (top-level for Category A)

- Models: `core/models_unified_system.py:1201-3493` (10 Opportunity variants) + `core/models_engagement_metrics.py:164` (`OpportunityInteraction`).
- Services (Category A owns): `core/services/opportunity_pipeline_orchestrator.py:309` + `core/services/opportunity_execution_pipeline.py:35` + `core/services/opportunity_scorer.py` + `core/opportunity_ai_analyzer.py:82` (structural misplacement — see §15) + `intelligence/opportunity_storage.py:18` + `intelligence/spider_opportunity_connector.py:70` + `intelligence/sports_opportunity_generator.py:18` + `ml_pipeline/opportunity_categorizer.py:21`.
- Agents: `core/agents/analysis/opportunity_scoring_agent.py:131` (`OpportunityScoringAgent`) + `core/agents/opportunity_pipeline_agent.py:89` (`OpportunityPipelineAgent`).
- WebSocket consumer: `core/consumers_base.py:2512` (`OpportunityScannerConsumer`).
- EventBus stream + publisher: `core/services/event_bus.py:25` (`EventStream.OPPORTUNITY_SCORED = "mi:opportunity_scored"`) + `core/services/event_bus.py:559` (`publish_opportunity_scored_event`) + `core/services/scoring_dispatcher.py:41` (publish invocation site).

### 3.2 REST URLs (9 endpoints, all under `/api/opportunities/`)

| URL | View | HTTP | Purpose |
|---|---|---|---|
| `/api/opportunities/` | `opportunity_list()` at `core/views_opportunity.py:32` | GET | List (filters: status, category, min_score, sort) |
| `/api/opportunities/top/` | `opportunity_top()` at `core/views_opportunity.py:~360` | GET | Top N scored |
| `/api/opportunities/stats/` | `opportunity_stats()` at `core/views_opportunity.py:~400` | GET | Aggregate stats |
| `/api/opportunities/score/` | `opportunity_score()` at `core/views_opportunity.py:247` | POST | Trigger scoring pass |
| `/api/opportunities/analyze/` | `opportunity_analyze()` at `core/views_opportunity.py:598` | POST | Analyze custom trend |
| `/api/opportunities/<uuid>/` | `opportunity_detail()` at `core/views_opportunity.py:145` | GET | Detail view |
| `/api/opportunities/<uuid>/act/` | `opportunity_act()` at `core/views_opportunity.py:~450` | POST | Begin acting (triggers pipeline) |
| `/api/opportunities/<uuid>/dismiss/` | `opportunity_dismiss()` at `core/views_opportunity.py:~500` | POST | Dismiss/archive (Session 688) |
| `/api/opportunities/<uuid>/rescore/` | `opportunity_rescore()` at `core/views_opportunity.py:558` | POST | Re-score existing |

URL registrations at `core/urls.py:1983-2008` (from Agent 3 report).

### 3.3 PA tools

- **`run_agent`** meta-tool: `opportunity_scoring_agent` registered in `agent_name.enum` at `core/services/pa_tool_schemas.py:1095`; `opportunity_pipeline_agent` at `core/services/pa_tool_schemas.py:1111`. Handler at `core/epa_handlers_tools.py:2011` (`_handle_opportunity_scoring_agent`) for scoring; generic `_handle_agent_tool` for pipeline agent.
- **`opportunity_manager_tool`** stub registered at `core/services/tool_dispatcher.py:330` with **no handler implementation found** (Agent 3 finding — see §14 drift).

### 3.4 Celery tasks

- **`score_opportunities_from_spider_data(hours=24, limit=100)`** at `core/tasks.py:2163`. Docstring names this the entry point invoked by hourly beat (`docs/WIREMAP.md:170`, `SESSION_872_COMPLETE.md:147`). PeriodicTask row existence not verified from source tree — see §14 drift + §19 R5.
- Queue routing: **defined twice** at `core/settings.py:1277` (`long_running`) + `core/settings.py:1484` (`content`); later wins → effective queue `content`. See §15 debt.

### 3.5 Management commands

- **`rescore_opportunities`** at `core/management/commands/rescore_opportunities.py:21` — batch re-score existing opportunities using unified type-aware scorer; dry-run by default; `--apply` persists; `--retype` updates `opportunity_type` if inferred type differs.

---

## 4. Major Models

**Q4 — What are the major models?** (with file:line)
**Q16 — What data does it own?** (models exclusive to this domain)

### 4.1 Category A owned models (5)

| Model | File:line | Purpose |
|---|---|---|
| `Opportunity` | `core/models_unified_system.py:1201` | Core discovery model. 27 fields spanning identity (id UUID, user_friendly_id UNIQUE Session 433), metadata (title, opportunity_type, source, description, requirements JSON), financial (potential_revenue Decimal default 0 Session Post-223, hourly_rate optional), status (6-choice enum: active/pending/applied/accepted/rejected/expired), workspace binding (workspace FK Session Post-433), matching (match_score 0–100, recommended_by Agent FK SET_NULL), execution (project FK PartnershipProject Session 766), lifecycle (created_at auto, expires_at manual — enforcement UNKNOWN), and 10 optional partnership fields (Session Pre-38: partnership_mode, ai_contribution_potential, collaboration_feasibility, partnership_workflow, required_human_skills, ai_capabilities_match, estimated_solo_hours, estimated_partnership_hours, time_multiplier). Indexed on `workspace` + `user_friendly_id`. |
| `OpportunityScore` | `core/models_unified_system.py:1694` | OneToOne with Opportunity (CASCADE). Scoring transparency: 4 reasoning text fields (profit/competition/effort/timing), confidence_level (1–100), data_sources JSON list, advisors_consulted JSON list, scoring_model_version (default 'v1.0'), created_at + updated_at. |
| `OpportunityPredictionAccuracy` | `core/models_unified_system.py:2905` | Aggregate ML feedback — 16 fields including (user nullable for system-wide, period_start/end/type: daily/weekly/monthly, total_opportunities, opportunities_with_revenue, conversion_rate, accuracy_by_category JSON, accuracy_by_source JSON, total_predicted, total_actual, MAE, score_correlation). UNIQUE `(user, period_start, period_type)`. |
| `OpportunityDigest` | `core/models_unified_system.py:3493` | Rollup — 14 fields including (user nullable, digest_type: weekly/monthly/ad_hoc, period start/end, aggregated stats, category/source breakdown JSON, top_opportunities JSON, win_rate, avg_score_won/lost, posted_to_discord bool, discord_message_id, digest_content text). UNIQUE `(user, digest_type, period_start)`. |
| `OpportunityInteraction` | `core/models_engagement_metrics.py:164` | Scoring-feedback surface (Category A owns as feedback surface; primary engagement models belong to Category C). 13 fields — user FK, engagement_session FK EngagementMetrics CASCADE, opportunity_id/title/platform/salary (denormalized strings/decimals), interaction_type (view/click/apply/reject), was_personalized bool, personalization_boost float, match_score int, interaction_timestamp indexed, time_to_interact seconds, resulted_in_application bool, application_success nullable bool. Classmethod `get_platform_performance(user, days=30)`. |

### 4.2 Cited but NOT owned by Category A (5 sibling variants)

Category D owns: `OpportunityAction` (`core/models_unified_system.py:2552`) + `OpportunityTask` (`core/models_unified_system.py:3000`, 1:1 with Opportunity).
Category E owns: `OpportunityRevenue` (`core/models_unified_system.py:2613`) + `OpportunityOutcome` (`core/models_unified_system.py:3394`, 1:1 with OpportunityTask) + `OpportunityContent` (`core/models_unified_system.py:2805`, cross-cutting).

### 4.3 Adjacent (Category F cites; not mainline Opportunity)

- `FreelanceOpportunity` at `core/models_autonomous_situations.py:352` — **DISTINCT TABLE** (verified via Agent 1 direct read). Table name `freelance_opportunity`, no FK to mainline `Opportunity`. Fields: title, description, client_name, platform (upwork/freelancer/fiverr), gig_url, budget metadata, 4 scoring fields, source_spider string, spider_data_id UUID nullable. **FK-boundary verdict: distinct lane, no cross-reference.** Category F child audit (S1406) owns.

### 4.4 Sports lane sidecar (NOT Category A owned; documented for §17 duplicate/overlap analysis)

- `OpportunityTracking` at `intelligence/models.py:416` — separate model in the `intelligence` app label. Fields differ from mainline `Opportunity` (has `opportunity_id` string not FK, `spider_source` string on the model itself, `opportunity_data` JSON catch-all, progress/earning tracking). UNIQUE `(user, opportunity_id)`. Written by `intelligence/sports_opportunity_generator.py:83` for sports betting; also by other intelligence subsystems (see §17). **No FK to mainline Opportunity; no cross-reference wire.** Sibling lane.

---

## 5. Major Services

**Q5 — What are the major services?** (with file:line)

### 5.1 Category A owned services (8)

| Service | File:line | LOC | Role |
|---|---|---|---|
| `OpportunityPipelineOrchestrator` | `core/services/opportunity_pipeline_orchestrator.py:309` | ~1,848 | Multi-stage agent-routing orchestration + learning mixin. Takes raw opportunity Dict, iterates 5 stages (DISCOVERY / ANALYSIS / EXECUTION / OPTIMIZATION / MONITORING enum), selects agents via `AgentRouter`, records learning outcomes on success, shares pattern knowledge when `value_multiplication > 1.5`. **Does NOT write to `Opportunity` model** — pure transform service. **God-service CANDIDATE** at 1,848 LOC. |
| `OpportunityExecutionPipeline` | `core/services/opportunity_execution_pipeline.py:35` | ~541 | Materialization service: takes an `Opportunity` model instance + user, creates `PartnershipProject` + `CustomWorkflow`, dispatches to `orchestration_engine.execute_workflow()`. Reads Opportunity rows via `filter(project__isnull=True, status__in=['active','pending','scored'])`. |
| `opportunity_scorer` module | `core/services/opportunity_scorer.py` | ~570 | Stateless scorers. Top-level `score_opportunity(...)` dispatches to type-specific scorer (`_score_freelance`, `_score_sports_betting`, etc.). `infer_opportunity_type(...)` helper. Returns `score_0_1` (0.3–0.95) + `score_0_100` (1–100). Called from spider connector + agents + Celery task + management command. |
| `OpportunityAIAnalyzer` | `core/opportunity_ai_analyzer.py:82` | ~847 | Analysis-only service (25+ methods). **Structural drift: lives at top-level `core/`, not `core/services/`** — see §15 debt. Invocation sites UNKNOWN (grep found no live callers; may be orphan; §19 R6). |
| `OpportunityStorageService` | `intelligence/opportunity_storage.py:18` | ~272 | Static-method wrapper over `OpportunityTracking` (intelligence lane). Not the mainline `Opportunity` storage service — despite the name. §17 duplicate/overlap note. |
| `SpiderOpportunityConnector` | `intelligence/spider_opportunity_connector.py:70` | ~677 | Spider → mainline `Opportunity` bridge. Async Redis-heavy (lines 91, 197, 210, 499, 525, 560; `cache_timeout=300`). Calls `Opportunity.objects.create(...)` at ~line 620 with `source=platform`, `metadata['spider_source']=<spider name>`. **F3 CANDIDATE:** Redis-only durability, no DB fallback (see §14). |
| `SportsBettingOpportunityGenerator` | `intelligence/sports_opportunity_generator.py:18` | ~238 | Sports lane producer. **Writes to `OpportunityTracking` (intelligence app), NOT mainline `Opportunity`.** Constructs Kelly-Criterion-sized bet opportunities from `Game` + `BettingRecommendation` + `OddsLine`. |
| `OpportunityCategorizationSystem` | `ml_pipeline/opportunity_categorizer.py:21` | ~673 | ML categorization. `categorize_opportunity(...)` async. Reads title + description to infer `opportunity_type`. **One-way read only** — no writes to `OpportunityPredictionAccuracy` or opportunity columns (Agent 4 verified). |

### 5.2 Cited but NOT owned (Category B/C/D/E surface)

`OpportunityDraftGenerator` at `core/services/ops_autopilot/outreach_generation.py:92` (Category B); `OutreachSequencer` + `ClosePackAutonomyEngine` at `core/services/ops_autopilot/revenue.py` (Categories B/D); `EngagementEngine` + `MeetingEngine` + `EngagementAutonomyEngine` at `core/services/ops_autopilot/engagement.py` (Categories C/D); `ImpactEvent` emitter at `core/services/ops_autopilot/impact.py` (Category E).

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs?** (REST, WebSocket, PA tools)

### 6.1 REST — 9 endpoints
See §3.2 for full table + file:line.

### 6.2 WebSocket

`OpportunityScannerConsumer` at `core/consumers_base.py:2512`. Type: `AsyncWebsocketConsumer` + `SafeWebSocketMixin`. Routing: `re_path(r'^ws/opportunity-scanner/$', consumers.OpportunityScannerConsumer.as_asgi())` at `core/routing.py:95`. Room group: `opportunity_scanner`.

- **Message types accepted (via `receive`):** `ping`, `update_settings`, `request_opportunities`.
- **Message types sent (via async handlers):** `connection_established`, `new_opportunity`, `opportunity_update`, `pong`, `settings_updated`, `scanner_status`, `system_status`, `error`.
- **Connect payload declares** `domains_monitored: [SPORTS_BETTING, CRYPTO, TRADING, REAL_ESTATE]`, `current_opportunities: 12`, `avg_edge: 4.2`. **These values are hard-coded** (verified via direct read at `core/consumers_base.py:2530-2536`) — not derived from mainline Opportunity queries.
- **Read source:** `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` — an in-memory realtime source, NOT `Opportunity.objects.filter(...)`. **NEW LOAD-BEARING FINDING** — see §14 drift + §19 R4.

### 6.3 PA tools
See §3.3.

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?** (sequence diagrams or step-by-step)
**Parent §12.1 Category A questions addressed:** "Who produces Opportunities (all producers)?" + "How does scoring flow?" + "Does `sports_opportunity_generator.py` produce into mainline or a separate lane?"

### 7.1 Flow α — Spider → Opportunity → Scoring → OPPORTUNITY_SCORED event

```
Spider task (per-domain — freelance, content, sports, etc.)
    │  writes SpiderData row to DB + emits to Redis channel
    │  (e.g. spider:opportunities:freelance)
    ▼
SpiderOpportunityConnector._fetch_fresh_opportunities()
    │  (intelligence/spider_opportunity_connector.py, async Redis poll)
    │  cache_timeout=300 (5-min Redis TTL, F3 CANDIDATE)
    ▼
_filter_and_score_opportunities()
    │  calls opportunity_scorer.score_opportunity(...)
    │  dispatches to type-specific scorer
    │  returns (score_0_1, score_0_100)
    ▼
Opportunity.objects.create(...)  (line ~620 in spider_connector)
    │  source=platform, match_score=score_0_100,
    │  metadata={'spider_source': <name>, 'spider_id': <id>}
    ▼
scoring_dispatcher._publish_scoring_event(...)  (line 21)
    │  → publish_opportunity_scored_event(...)  (line 41)
    │  → EventStream.OPPORTUNITY_SCORED ("mi:opportunity_scored")
    │  Payload: opportunity_id, spider_data_id, ml_score, rule_score,
    │           hybrid_score, confidence, priority
    ▼
Event consumers:
    - handle_opportunity_scored_event() (event_handlers.py:164)
      routes confidence 50-85% → HITL validation
      (VALIDATION_REQUIRED event)
    - process_event_bus_scoring_queue (tasks.py:4726) — scoring_workers group
    - validation_workers group
    - analytics_workers group
    ▼
Downstream: OpportunityExecutionPipeline (materializes to PartnershipProject)
            OR Category B OpportunityDraftGenerator (outreach)
```

### 7.2 Flow β — `OpportunityPipelineOrchestrator` invocation

**Trigger:** UNKNOWN from service-layer read. Agent 2 found no `@shared_task`, no `@beat`, no consumer registration. Agent 3 found `opportunity_pipeline_agent` registered in `run_agent` PA-tool enum (`pa_tool_schemas.py:1111`) dispatched via generic `_handle_agent_tool`. Inference: Rigby calls `run_agent(agent_name="opportunity_pipeline_agent", task="...", context={"opportunity": {...}})` → generic dispatcher → `OpportunityPipelineAgent.execute()` — and that agent may then instantiate + invoke `OpportunityPipelineOrchestrator`. Direct invocation chain not verified end-to-end. **§19 R6.**

```
Rigby (LLM function-call) run_agent(agent_name="opportunity_pipeline_agent", ...)
    ▼
_handle_agent_tool()  (generic dispatch, td_handlers)
    ▼
OpportunityPipelineAgent.execute(task, context, ...)
    ▼
[likely] OpportunityPipelineOrchestrator.orchestrate_opportunity_pipeline(
    opportunity={dict}, pipeline_config={...}
)
    ▼
Iterate 5 stages (DISCOVERY → ANALYSIS → EXECUTION → OPTIMIZATION)
    per stage: _select_optimal_agent_for_stage()
             → AgentRouter dispatch
             → agent.execute()
             → compound value multiplier calc
    ▼
Returns {success, pipeline_id, final_value, stage_results, optimized_opportunity}
    Records learning outcome (PipelineLearningMixin)
    Shares pattern knowledge if value_multiplication > 1.5
```

### 7.3 Flow γ — Sports lane (isolated from mainline)

```
Sports betting analyzer (Games + BettingRecommendation + OddsLine)
    ▼
SportsBettingOpportunityGenerator.discover_betting_opportunities(user, hours_ahead, min_ev)
    ▼
Kelly-Criterion bet sizing (line 60-74)
    ▼
OpportunityTracking.objects.create(...)  (line 83; intelligence.models.py:416)
    NOT Opportunity.objects.create() — parallel lane
    opportunity_data JSON includes spider_source='sports_betting_analyzer'
    ▼
[No cross-wire to mainline Opportunity]
[No OPPORTUNITY_SCORED event emission from sports path]
[No integration with OpportunityScoringAgent / OpportunityPipelineAgent]
```

**Resolves parent §12.1 Q6:** sports_opportunity_generator writes to a SEPARATE lane (`OpportunityTracking`).

### 7.4 Flow δ — Hourly scoring beat

```
Celery beat scheduler (per WIREMAP.md:170, SESSION_872_COMPLETE.md:147: hourly)
    ▼  [PeriodicTask row existence UNKNOWN — §19 R5]
score_opportunities_from_spider_data(hours=24, limit=100)  (core/tasks.py:2163)
    routed to 'content' queue (settings.py:1484 wins over :1277 'long_running')
    ▼
OpportunityScoringAgent()  (direct instantiation, line 2182)
    → score_spider_data(hours, limit)
    ▼
Returns stats: total_processed, successful, high_value_opportunities (70+ scored),
              average_score
    Each high-value scored opportunity → OpportunityScore row
    (see Session 526 audit: 3 OpportunityScore records from 153 Opportunities
    at Session 526 timepoint; scoring rate 2%.)
```

### 7.5 Flow ε — WebSocket `opportunity-scanner` (READ-ONLY listener; §14 drift)

```
Frontend WebSocket client
    ▼
ws/opportunity-scanner/  (routing.py:95)
    ▼
OpportunityScannerConsumer.connect (consumers_base.py:2518)
    joins room_group_name='opportunity_scanner'
    initial payload with hard-coded domains_monitored (SPORTS_BETTING, CRYPTO,
    TRADING, REAL_ESTATE), current_opportunities=12, avg_edge=4.2
    ▼
intelligence_engine.get_current_opportunities()  (from intelligence.realtime_engine)
    NOT Opportunity.objects.filter(...) — DUAL representation
    Streams first 3 opportunities via 'new_opportunity' WebSocket message
    ▼
[No writes to Opportunity model]
```

Verified via direct read `core/consumers_base.py:2510-2570`.

---

## 8. Data Ownership and Lifecycle

**Q7 — What are the major Celery tasks?**
**Q8 — What are the major management commands?**
See §3.4 + §3.5.

**Q16–Q18 covered at §4 + §9.**

**Retention / lifecycle policies for the 5 owned models:**

| Model | Delete policy | TTL enforcement | Notes |
|---|---|---|---|
| `Opportunity` | CASCADE on user delete | `expires_at` field EXISTS but enforcement UNKNOWN — no cron grep found; **advisory-only?** §19 R7. | Deletion cascades to Score + Task + Action + Revenue + Content + Interaction (all Category-A + sibling models). |
| `OpportunityScore` | CASCADE on Opportunity delete | None | 1:1 with Opportunity. |
| `OpportunityPredictionAccuracy` | CASCADE on user delete (nullable for system-wide) | None | Permanent historical record per `(user, period_start, period_type)`. |
| `OpportunityDigest` | CASCADE on user delete (nullable) | None | Permanent aggregation. |
| `OpportunityInteraction` | CASCADE on user + engagement_session delete | None | Permanent unless engagement_session deprecated. |

**Ownership metadata on models:** NONE explicit. No `owner: CharField` or similar per Agent 1 direct grep. Category A inherits S1274 §14 finding #36 (HIGH severity: no runtime owner). See §18.

---

## 9. Integrations With Other Domains

**Q14 — What integrations does it have?**
**Q15 — What integrations are missing?**
**Q17 — What data does it consume?** (from other domains)
**Q18 — What data does it produce?** (for other domains)
**Q21 — What other domains depend on it?** (inbound consumers)
**Q22 — What domains does it depend on?** (outbound dependencies)

### 9.1 Integration map (verified against S1274 baseline; verifier-loop applied)

| Adjacent domain | S1274 baseline | S1401 Category A verified | Verdict | Evidence |
|---|---|---|---|---|
| Spider → Opportunity | STRONG | STRONG CONFIRMED | CONFIRMED | `intelligence/spider_opportunity_connector.py:~620` calls `Opportunity.objects.create(...)`; provenance tagged in `source` + `metadata`. |
| Sports/DBAO → mainline Opportunity | MISSING | **STILL MISSING for mainline** — sports writes to `OpportunityTracking` (intelligence lane), not `Opportunity` | **CONFIRMED (S1274 baseline holds for mainline).** The wording refinement is "separate lane" rather than "missing implementation" — sports opportunities ARE persisted, just NOT in mainline `Opportunity`. Cross-wire from `OpportunityTracking` → `Opportunity` does not exist. | `intelligence/sports_opportunity_generator.py:83` writes `OpportunityTracking.objects.create(...)`. Verified direct read. |
| Signal Engine → Opportunity | STRONG per S1273 §4.9 | STRONG (via spider bridge) | CONFIRMED | Spider connector consumes spider-emitted signals; signal→spider is upstream to Category A. |
| Opportunity → Content | STRONG (mediated via `OpportunityDraftGenerator`, Category B) | WEAK-mediated CONFIRMED | CONFIRMED | `OpportunityDraftGenerator` reads Opportunity rows for outreach; Category B owns write path to `OutreachDraft`. |
| Opportunity → Observability | STRONG via `ImpactEvent` | UNKNOWN (Category E owns primary evidence) | PARKED | Category E child audit S1405 resolves. |
| Opportunity → Initiative | MISSING | CONFIRMED MISSING | CONFIRMED | Zero Initiative import / FK / event bridge in Category A code (verified via Agent 4). Child E aggregates per D28. |
| Opportunity → Inbox | MISSING (outbound channel UNKNOWN) | CONFIRMED MISSING | CONFIRMED | `OpportunityDraftGenerator` produces `OutreachDraft` (Category B) — no direct Opportunity → Inbox wire. Category B child audit S1402 resolves outbound channel. |
| Opportunity → HumanAttention | MISSING | UNKNOWN (Category D owns Meeting/Close boundary) | PARKED | Category D child audit S1404 resolves. |
| Agents → Opportunity (writer) | Not in S1274 §2.4 | **WEAK NEW** | NEW FINDING | `core/agents/analysis/opportunity_scoring_agent.py` + `core/services/td_handlers_agents.py` invoke `Opportunity.objects.create(...)`. Agents write mainline Opportunity. |
| PA tool → Opportunity (writer) | Not in S1274 | **WEAK NEW** | NEW FINDING | `core/services/income_action_service.py` writes mainline Opportunity from PA `analyze_opportunity` action. |
| ML Pipeline → Opportunity | STRONG per S1273 §4.9 | **DOWNGRADED to READ-ONLY** | DOWNGRADED | `ml_pipeline/opportunity_categorizer.py` reads title/description → infers `opportunity_type`; no write to `OpportunityPredictionAccuracy` or opportunity columns. One-way categorization only. |
| Revenue Attribution Bridge → Opportunity | Inherited from S1274 §4.3 | CONFIRMED not read/write | CONFIRMED | `revenue_attribution_bridge.py` processes Revenue events; no Opportunity read/write. Category E owned. |
| Category A → `intelligence_engine` (WebSocket source) | Not in S1274 | **NEW UNKNOWN** | NEW | `OpportunityScannerConsumer` reads from `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` — separate realtime source. Sync with mainline `Opportunity` UNKNOWN. §14 drift + §19 R4. |

### 9.2 Producer inventory (inbound to mainline Opportunity)

**Confirmed writers of `Opportunity.objects.create(...)`:**

1. `intelligence/spider_opportunity_connector.py:~620` — spider ingestion (STRONG, complete provenance tags).
2. `core/agents/analysis/opportunity_scoring_agent.py:~140` — post-ML analysis creates Opportunity if score > threshold.
3. `core/services/td_handlers_agents.py` (2 sites) — PA-tool dispatch from Rigby `analyze_opportunity` action.
4. `core/services/income_action_service.py:~95` — PA-tool income analysis flow.

**25 files match `Opportunity.objects.create|Opportunity(` pattern (grep verified). The other 21 are false positives** (test fixtures, `FreelanceOpportunity` / `OpportunityTracking` / `RealJobOpportunity` / `SpiderOpportunity` dataclasses in Category F Income/Jobs surface, sports domain classes). Category F child audit S1406 completes the full producer inventory across Categories A + F.

### 9.3 Consumer inventory (outbound reads of Opportunity rows)

- `OpportunityExecutionPipeline` (Category A) — reads via `filter(project__isnull=True, status__in=['active','pending','scored'])`.
- `OpportunityDraftGenerator` (Category B) — reads `is_contactable(...)` gated rows.
- `ScoringDispatcher` (Category A) — reads Opportunity metadata for scoring re-runs.
- Views/serializers (`views_opportunity.py`, `views_opportunities.py`, `views_analytics.py`, `views_dashboard_stats.py`).
- `ml_pipeline/opportunity_categorizer.py` — one-way title/description read.

**No consumers found** for: Initiative model, HumanAttention system, Inbox model (confirms S1274 MISSING classifications).

---

## 10. Event Flows

**Q19 — What events does it emit?** (with file:line producers)
**Q20 — What events should it emit?** (gaps — reference S1274 §6)

### 10.1 `EventStream.OPPORTUNITY_SCORED` (`"mi:opportunity_scored"`)

**Fully citation-strengthened per Rigby SIGN cycle 1 fold M2.**

- **Definition (VERIFIED):** `core/services/event_bus.py:25` — `OPPORTUNITY_SCORED = "mi:opportunity_scored"` on the `EventStream(str, Enum)` class.
- **Publisher wrapper (VERIFIED):** `publish_opportunity_scored_event(opportunity_id, spider_data_id, ml_score, rule_score, hybrid_score, confidence, source="scoring_engine")` at `core/services/event_bus.py:559`.
- **Payload composition (VERIFIED):** the wrapper assembles the `Event` at `core/services/event_bus.py:581` with `stream=EventStream.OPPORTUNITY_SCORED` (Rigby SIGN cycle 1 spot-check grep hit — line 581).
- **Direct invocation site (VERIFIED):** `core/services/scoring_dispatcher.py:41` — `publish_opportunity_scored_event(opportunity_id=..., spider_data_id=str(spider_data.id), ml_score=..., rule_score=..., hybrid_score=..., confidence=..., source=f'scoring_dispatcher_{mode}')` from within the `_publish_scoring_event` helper at line 21.
- **Higher-level caller sites (S1274 §6.2 registry claim):** `scoring_dispatcher.py:282, 480` — cited from S1274; not independently re-verified in this audit. Flag: S1274-inherited citation (not this audit's spot-check).
- **Payload schema (VERIFIED via direct read of `publish_opportunity_scored_event` body):**

```json
{
  "event_type": "opportunity_scored",
  "stream": "mi:opportunity_scored",
  "data": {
    "opportunity_id": "...",
    "spider_data_id": "...",
    "hybrid_score": 75.5,
    "ml_score": 72.0,
    "rule_score": 80.0,
    "confidence": 0.82
  },
  "priority": "NORMAL|HIGH|LOW",
  "source": "scoring_dispatcher_realtime|scoring_dispatcher_batch|scoring_engine"
}
```

Priority logic (per publisher wrapper body): `confidence >= 85` → HIGH; `< 50` → LOW; else NORMAL.

- **Handler-to-event-type registration (VERIFIED via Rigby SIGN cycle 1 spot-check):** `core/services/event_handlers.py:48` — `self.register('opportunity_scored', handle_opportunity_scored_event)` on `EventHandlerRegistry.__init__`. This is the canonical handler mapping for the `opportunity_scored` event type.
- **Handler body (VERIFIED):** `handle_opportunity_scored_event(event: Event)` at `core/services/event_handlers.py:164`.
  - **Corrected action semantics (per Rigby SIGN cycle 1 fold M2 — my v1 draft overstated the routing action):** the handler DETECTS confidence in `[50, 85)` and LOGS "needs human validation" (see line 186). It does **NOT** emit a `VALIDATION_REQUIRED` event or create a validation request. The inline comment at `event_handlers.py:186-188` says "The HITL service will have already created the validation request. This handler is for analytics and notifications." Original v1 draft claim "routes confidence 50-85% → HITL VALIDATION_REQUIRED event" was inaccurate; corrected to "detects + logs."
- **Worker subscription (VERIFIED via Rigby spot-check):** `create_validation_worker(...)` at `core/services/event_handlers.py:521+` region subscribes to streams including `EventStream.OPPORTUNITY_SCORED` (see line 536: `streams=[EventStream.OPPORTUNITY_SCORED, EventStream.VALIDATION_REQUIRED]`).
- **Additional consumer groups (S1274 §6.2 registry claim; downgraded per Rigby SIGN cycle 1 fold M2 — v1 draft overreached):** S1274 §6.2 named `scoring_workers`, `validation_workers`, and `analytics_workers` as consumer groups. This audit **independently verified only `create_validation_worker`** (via Rigby spot-check at `event_handlers.py:521+`) and the handler registry mapping (line 48). The `scoring_workers` / `analytics_workers` groups + `process_event_bus_scoring_queue` task at `core/tasks.py:4726` are cited from S1274 §6.2 but **not re-verified in this audit** — flag as CANDIDATE citations pending independent grep.

### 10.2 `EventStream.OPPORTUNITY_CREATED` — DEFINED BUT DORMANT

- **Definition:** `core/services/event_bus.py:24` (Agent 4 finding).
- **Publisher:** NO grep hit. **Zero publish site found.**
- **Consumer:** UNKNOWN.
- **Classification:** DORMANT (per S1274 EventBus lesson: verify before calling "dead"). §19 R8 documents the ambiguity — is this a planned-but-unshipped event, or dead code?

### 10.3 Recommended future events (Q20 — reference S1274 §6)

- **`OPPORTUNITY_CREATED`** — activate the dormant stream (if it's the design intent) so downstream consumers can react to Opportunity creation independently of scoring.
- **`OPPORTUNITY_EXPIRED`** — no expiry event currently emitted; `expires_at` enforcement is UNKNOWN (§19 R7).
- **`OPPORTUNITY_ACTIONED`** — status transitions (active → applied → accepted → rejected) currently silent from an event-bus perspective; consumers must poll or subscribe to DB triggers.

---

## 11. Existing Documentation

**Q10 — What existing documentation exists?**

Category A has **no CANONICAL topic doc** (confirmed against parent §11.3 baseline). Existing coverage is scattered:

| Doc | Category A coverage | Completeness | Cite-forward |
|---|---|---|---|
| `docs/research/platform_architecture_inventory.md` §3.32 + §4.9 | 5 UNKNOWNs named + 7-domain cross-domain flow | cursory | S1273 v2 |
| `docs/research/platform/cross_domain_integration_audit.md` §2.4 + §3.7 + §6.2 + §14 #36 | 3 MISSING integrations + MEDIUM Opportunity→Initiative + EventBus registry + HIGH no runtime owner | partial | S1274 |
| `docs/research/domains/revenue/1400_revenue_domain_scoping.md` | Category A candidate taxonomy + 15 inherited findings + §12.1 Q's | partial (scoping-stage) | S1400 |
| `docs/handoffs/SESSION_1025_SCORING_CONTRACT.md` | Scoring contract for **SignalCluster** (reach/intent/replicability/source_confidence) — NOT Opportunity scoring | moderate but off-target | S1025 |
| `docs/audits/audit_revenue_opportunity.md` | Session 526 audit: 153 Opportunity rows, 3 OpportunityScore records (2% scoring rate); infrastructure ready but underutilized | partial | S526 |
| `docs/handoffs/SESSION_1114_ACTIVE_MODULE_OWNERSHIP_MAP.md` | Opportunity orchestration owner UNKNOWN | partial | S1114 |
| `docs/WIREMAP.md:168-172, 373-377` | `score_opportunities_from_spider_data` hourly + ML pipeline map | mention-only | — |
| `docs/PLATFORM_WHAT_IT_IS.md` | Mentions `opportunity_window` as 1-of-10 signal pattern types; no Category A architecture narrative | cursory | narrative anchor |
| `docs/PLATFORM_INVENTORY.md` | 10 Opportunity variants + 2 agents listed | mention-only | inventory anchor |

**No prior handoff dedicated to Category A architecture.** No `docs/topics/opportunity-discovery.md` or equivalent.

---

## 12. Research Coverage

**Q13 — What is the research coverage?** (per playbook §12 classification)

**Verdict: LIGHT** (confirmed against S1273 §3.32 baseline for Revenue whole-domain).

**Evidence:**
- 3 prior audit-adjacent artifacts (S1273, S1274, Session 526) each cover components, none synthesize Category A.
- Session 1025 scoring contract applies to signals, not Opportunity scoring.
- No canonical topic doc.
- 5 of §12.1 Q's are unresolved at S1400 open; this audit resolves 3 (Q1 Opportunity schema, Q2 producer inventory partial, Q6 sports lane) and elevates the others via evidence.

**Post-S1499 canonical summary is expected to promote coverage from LIGHT to MODERATE for Category A specifically.**

---

## 13. Architecture Maturity

**Q12 — What is the architecture maturity?** (per playbook §12 classification)

**Verdict: WORKING** (matches S1273 §3.32 baseline; no upgrade or downgrade for Category A).

**Evidence FOR WORKING:**
- All named components exist and are instantiable (verifier-loop confirmed 6 of 6 parent §2.4 file:line citations at HEAD `ae30a1fe`).
- 3 Celery tasks defined + at least one (`score_opportunities_from_spider_data`) documented as hourly beat across three doc sources.
- EventBus wire operational (publisher + at least one consumer + 3 consumer-group registration).
- WebSocket consumer accepts connections + streams initial data.
- Test coverage exists (`core/tests/test_opportunity_task.py` — ~36 LOC; test_outreach_generation + test_autofill_sweep referenced).

**Evidence AGAINST STABLE:**
- Namespace fragmentation (Category A code split across `core/`, `core/services/`, `intelligence/`, `ml_pipeline/`).
- No runtime owner (S1274 §14 #36 HIGH severity CONFIRMED at §18).
- Weak EventBus adoption per S1274 v2 Rigby correction (single-publisher `scoring_dispatcher.py:41`; DORMANT `OPPORTUNITY_CREATED` stream).
- F1 provenance-filter drift CANDIDATE; F2 orphan-write candidates on 10-variant + partnership_* fields; F3 Redis-only durability CANDIDATE.
- Session 526 audit noted 2% scoring rate — infrastructure underutilized at that point in time. Current rate UNKNOWN.
- Celery queue-routing duplicate-definition bug (§15) is a mild drift-prone bug.

**No evidence** of critical breakage that would warrant downgrade to PARTIAL. No experimental-tier flags. WORKING is accurate.

---

## 14. Known Drift

**Q27 — What is drift?** (with evidence)

Drift matrix — where documented claims mismatch runtime reality:

| # | Source doc | Claim | Runtime reality | Severity | Recommendation |
|---|---|---|---|---|---|
| D1 | S1273 §3.32 + parent §2.4 | 6 file:line citations for Category A services/agents/consumer | **ALL 6 VERIFIED at HEAD `ae30a1fe`** — no drift | OK | None. |
| D2 | S1273 §10.3 UNKNOWN #1 | Opportunity model location UNKNOWN | Resolved: `core/models_unified_system.py:1201` | OK | Anchor-update: update S1273 §10.3 status → RESOLVED at Group 1400 close. |
| D3 | Session 526 audit (pre-Session 872) | Scoring rate 2% (3 rows scored / 153 rows total) | UNKNOWN at current HEAD — no telemetry access from source tree | MEDIUM | §19 R2: Rigby-side telemetry check on `OpportunityScore` count vs `Opportunity` count. |
| D4 | Agent 3 sub-agent report | `score_opportunities_from_spider_data` NOT SCHEDULED | Documented as hourly in `WIREMAP.md:170`, `SESSION_872_COMPLETE.md:147`, `SESSION_223_OPPORTUNITY_ENGINE.md:124` (archive). PeriodicTask row existence UNKNOWN from source tree | MEDIUM | §19 R5: Rigby confirms via `PeriodicTask` ORM query. |
| D5 | S1274 §2.4 line 270 | Sports/DBAO → Opportunity: MISSING | Sports writes to `OpportunityTracking` (separate lane), not mainline `Opportunity`. **S1274 baseline HOLDS for mainline — MISSING is accurate.** The refinement is wording: sports IS integrated into `OpportunityTracking` (intelligence lane), so the correct framing is "separate lane" rather than "no code at all." Cross-wire from OpportunityTracking → Opportunity is what's missing. | LOW | Anchor-update: S1274 §2.4 line 270 gets a clarifying note that "MISSING" applies to the wire between `OpportunityTracking` and mainline `Opportunity`, not to opportunity creation in the intelligence lane. |
| D6 | `OpportunityScannerConsumer` (+ 4 additional consumer sites) design assumption | Consumers stream mainline Opportunity rows | Consumers stream `intelligence_engine.get_current_opportunities()` (in-memory realtime source), NOT `Opportunity.objects.filter(...)`. **NEW DUAL REPRESENTATION drift, broader than a single consumer** — Rigby SIGN cycle 1 grep found this pattern at 5 sites in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597). Synchronization contract UNKNOWN. | MEDIUM | §19 R1 umbrella: reconcile as prerequisite sub-task R1.0 (identify origin/lifecycle of `get_current_opportunities()`); then answer synchronization contract question. Design question, not just a bug. |
| D7 | Parent §2.4 producer list | 4 producers inferred | 4 confirmed via §9.2; `core/tasks_ops.py`, `intelligence/spider_decision_bridge.py`, `intelligence/realtime_engine.py`, `self_awareness/intelligence.py`, `core/super_platform/revenue_integration.py`, `ai_core/intelligence/monetization_engine.py` matched pattern but not verified as mainline Opportunity writers | UNKNOWN | §19 R3: Category F child audit S1406 completes cross-category producer inventory. |
| D8 | F1 provenance framework (S1399 §4 F1 lens) | Writers tag + readers filter consistently | Writers tag inconsistently (spider connector complete; agents + PA tools sparse); readers ignore provenance. **F1-CANDIDATE.** | HIGH | §19 R1: add reader-side provenance filter; standardize writer-side provenance tagging across all producer paths. |
| D9 | S1273 §10.3 UNKNOWN #5 | Ops Autopilot / standalone-service dedup path UNKNOWN | Category A's `OpportunityStorageService` at `intelligence/opportunity_storage.py:18` wraps `OpportunityTracking` (sports/intelligence lane), NOT mainline Opportunity — despite the class name. Naming ambiguity is itself a drift signal. | MEDIUM | Anchor-update note or class rename design-preparation. |
| D10 | `OpportunityAIAnalyzer` structural placement | Service class expected under `core/services/` | Located at top-level `core/opportunity_ai_analyzer.py:82` — namespace anomaly | LOW | Consolidation hygiene sweep post-arc close. |

---

## 15. Known Technical Debt

**Q26 — What is technical debt?** (with severity per §12)

| # | Debt item | Category | Severity | Evidence | Recommendation |
|---|---|---|---|---|---|
| T1 | Namespace fragmentation — Opportunity code split across `core/`, `core/services/`, `intelligence/`, `ml_pipeline/` (13 files, 4 namespaces) | namespace_fragmentation | MEDIUM | Direct enumeration in §3.1 + §5.1 | Post-arc consolidation ADR; do not consolidate as part of audit. |
| T2 | 10-variant Opportunity family — F2 orphan-write CANDIDATE cluster (partnership_* fields Session Pre-38, metadata dict, expires_at) | F2_candidate | HIGH | Field-level enumeration in §4.1 Opportunity row; partnership_* fields have null/blank defaults, consumption sites unverified | §19 R4: F2 corroboration via grep of readers for each candidate field. Do NOT harden to CONFIRMED until sibling verification. |
| T3 | `spider_opportunity_connector.py` uses async Redis with `cache_timeout=300` and no DB fallback | F3_candidate | HIGH | Redis calls at lines 91, 197, 210, 499, 525, 560 (Agent 2 grep) | §19 R1 addendum: hybrid Redis + DB durability + explicit fallback path. |
| T4 | F1 provenance-filter drift — writers tag inconsistently, readers ignore provenance | F1_candidate | HIGH | §9 producer inventory writer table + consumer table | §19 R1: standardize writer-side + add reader-side provenance filter. |
| T5 | `core/settings.py` `task_routes` defines `score_opportunities_from_spider_data` TWICE — line 1277 (`long_running`) + line 1484 (`content`); later wins | drift_prone_config | MEDIUM | Verified via direct grep during parent-Claude verifier-loop + Rigby SIGN cycle 1 spot-check | Follow-on cleanup PR: dedupe. **Operational consequence (per Rigby SIGN cycle 1 fold NH #3):** effective queue = `content` (later dict entry wins). This matters because `long_running` and `content` queues have different worker concurrency limits, memory profiles, and workload assumptions — `long_running` was designed for CPU/LLM-heavy batches (concurrency=1, 512MB, aggressive recycling per `settings.py:1268-1273` comments); `content` was designed for content-generation tasks (per Session 1063 grouping at `settings.py:1482`). A 100-item ML scoring pass with the concurrency/memory expectations of `long_running` is being routed to `content` — this may cause scoring latency regression during high-content periods, OR it may be a deliberate later-optimization. Follow-on PR should verify designer intent (git blame `settings.py:1484` for Session 1063 context) and drop the wrong route. |
| T6 | `OpportunityPipelineOrchestrator` at 1,848 LOC — god-service CANDIDATE | god_service_candidate | MEDIUM | Direct read + Agent 2 LOC count | Post-arc extraction proposal; not audit's job. |
| T7 | `OpportunityAIAnalyzer` — no confirmed invocation sites; may be orphan | dead_code_candidate | MEDIUM | Agent 2 grep found no callers | §19 R6: Rigby-side runtime probe (any `LLMCallEvent` history?). Do NOT delete without S1246 fleet-caller sweep per MEMORY rule `feedback_verify_before_deleting_dead_code`. |
| T8 | `opportunity_manager_tool` — schema stub registered at `tool_dispatcher.py:330` with NO handler implementation | dead_code_candidate | LOW | Agent 3 grep found no `_handle_opportunity_manager` handler | Either implement or remove registration. Design-preparation, not implementation. |
| T9 | `EventStream.OPPORTUNITY_CREATED` — defined at `event_bus.py:24` but no publisher grep hit | dead_code_candidate | LOW | Agent 4 grep + parent-Claude verifier-loop | §19 R8: Rigby verifies dormancy is intentional (dormant=not-yet-shipped) vs unintentional (dead code). |
| T10 | Dual opportunity representation — mainline Django `Opportunity` vs `intelligence_engine.get_current_opportunities()` in-memory | design_debt | MEDIUM | §14 D6 + direct read `consumers_base.py:2540` | §19 R4: reconcile or document intended separation. |
| T11 | `expires_at` field on Opportunity — enforcement path UNKNOWN | technical_debt | MEDIUM | Agent 1 grep found no cron or scheduled expiry path | §19 R7: implement expiry cron OR mark field advisory. |
| T12 | No E2E tests for full spider→score→event→execute pipeline | test_coverage_debt | MEDIUM | Sparse test count (only `test_opportunity_task.py` at ~36 LOC) | Post-arc test-plan design-preparation. |

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?** (reference S1274 §7 boundary violations)

Category A boundary check — imports/reaches from Category A code into other domains' internals:

| # | Violation | Severity | Notes |
|---|---|---|---|
| B1 | `intelligence/spider_decision_bridge.py` imports `ml_pipeline.opportunity_categorizer` | WEAK | ML pipeline is platform-wide utility; not a violation, but a cross-namespace reach worth naming. |
| B2 | `OpportunityRevenue` + `OpportunityContent` (Category E, cited but not owned by Category A) SET_NULL FK to `content.ImageHistory` / `content.VideoHistory` | MEDIUM (LOW as design intent) | Cross-domain writes into Content domain — intentional per design (Content owns content items; Revenue tracks monetization). §17 duplicate/overlap notes complementary role. Not a violation if design intent confirmed by Category E audit S1405. |
| B3 | `OpportunityInteraction` (Category A owned) CASCADE FK to `EngagementMetrics` (Category C owned) | LOW | Category A owns model but Category C owns cascade — tight coupling but intentional (engagement feedback surfaces scoring decision). Investigate whether ownership should be inverted at Category C audit S1403. |
| B4 | `OpportunityTask.project` (Category D owned) SET_NULL FK to `PartnershipProject` (Partnership domain) — inherited indirectly via Opportunity | LOW | Not Category A owned; noted for §17 completeness. |

No HARD boundary violations found. The design shows intentional cross-domain FKs; nothing bypasses domain APIs.

---

## 17. Duplicate or Overlapping Systems

**Q17 duplicate/overlap** (reference S1274 §5 duplicate/overlap analysis)
**Q23 — What models overlap with other domains?**

### 17.1 10-variant Opportunity family — INTENTIONAL SIBLINGS

Not duplicates. Clear separation of tiers:

- **Prediction tier:** `Opportunity` (score container) → `OpportunityScore` (reasoning) → `OpportunityPredictionAccuracy` (aggregate ML feedback).
- **Lifecycle tier:** `Opportunity` → `OpportunityTask` (Category D) → `OpportunityOutcome` (Category E).
- **Attribution tier:** `Opportunity` → `OpportunityAction` (Category D) → `OpportunityRevenue` + `OpportunityContent` (Category E).
- **Feedback tier:** `OpportunityInteraction` (Category A owned as feedback surface) → `OpportunityDigest` (Category A owned as rollup).

Agent 1 finding: no strict duplicates; all 10 variants have distinct purposes.

### 17.2 `Opportunity` (mainline, core.models_unified_system:1201) vs `OpportunityTracking` (intelligence.models:416)

**PARALLEL LANES.** Not duplicates. `OpportunityTracking` is the sports/intelligence lane; `Opportunity` is the mainline revenue lane. Confirmed via §7.3 Flow γ + §9.1 integration map. No cross-wire, no synchronization.

**Load-bearing framing (per Rigby SIGN cycle 1 fold):** the distinction between "separate lane" and "integration solved" matters. Sports IS integrated in the sense that sports betting opportunities are persisted somewhere (`OpportunityTracking`) rather than being lost. Sports is NOT integrated in the sense that mainline `Opportunity` — the model consumed by Category B outreach + Category D meeting/close + Category E attribution — has no knowledge of sports opportunities. S1274's MISSING classification is accurate at the mainline layer; readers should not misread §17 as saying sports integration is complete just because a table exists.

**§17 recommendation:** either integrate the two (unify under one model with an `opportunity_lane` enum) OR document the intentional separation and rename `OpportunityTracking` → `SportsOpportunity` / `IntelligenceOpportunityTracking` to signal separateness. Design-preparation, not audit's job.

### 17.3 `OpportunityPipelineOrchestrator` (1,848 LOC) vs `OpportunityExecutionPipeline` (541 LOC)

**COMPLEMENTARY, not overlapping** (parent-Claude synthesis resolved Agent 6's initial "duplication candidate" flag via Agent 2's direct code read):

- Orchestrator: transform/analysis service; Dict in → optimized Dict out; 5-stage agent routing.
- ExecutionPipeline: materialization service; Opportunity instance → PartnershipProject + CustomWorkflow.

Different signatures, different downstream side effects, different learning surfaces. Not consolidation candidates.

### 17.4 `OpportunityStorageService` naming collision

`intelligence/opportunity_storage.py:18` `OpportunityStorageService` wraps `OpportunityTracking` (sports/intelligence lane), NOT the mainline `Opportunity` — despite the class name. Naming makes this look like a mainline storage service; it isn't. §14 D9 documents.

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?** (reference S1274 §10 ownership gaps + S1274 §14 finding #36)

S1274 §14 finding #36 (HIGH severity, inherited via parent §11.4): "Revenue Pipeline has no runtime owner."

**Category A specific verification:**

| Dimension | Verified state | Gap? |
|---|---|---|
| JobContract wiring | Grep of `core/employees/jobs.py` — zero mentions of `OpportunityScoringAgent` or `OpportunityPipelineAgent` | **GAP CONFIRMED.** |
| Beat schedule + dedicated queue | `score_opportunities_from_spider_data` routes to `content` queue (settings.py:1484 wins over :1277); no `opportunity_scoring_queue` or dedicated Category A queue | **GAP CONFIRMED.** Content queue is shared. |
| Documented ownership artifact | No `docs/topics/opportunity-ownership.md` or CODEOWNERS-style file; `docs/handoffs/SESSION_1114_ACTIVE_MODULE_OWNERSHIP_MAP.md` names OpportunityScoringAgent as a **program owner** but not a **runtime operational owner** | **GAP CONFIRMED.** Program owner ≠ runtime operational owner. |
| Employee OS / MissionRunner integration | Neither Category A agent inherits from MissionRunner-aware base; no `OpsRun` / `OpsRunEvent` wiring | **GAP CONFIRMED.** |

**Category A recommendation for the parent-arc ownership question:** Child E (S1405) aggregates the parent-arc runtime-owner recommendation per D28. Category A's specific input: propose a dedicated `OpportunityScoringOwner` JobContract that (a) owns `score_opportunities_from_spider_data` beat, (b) owns the `OPPORTUNITY_SCORED` publisher path, (c) owns the WebSocket consumer's dual-representation reconciliation. This proposal is design-preparation input to Child E, not implementation.

---

## 19. Recommended Future Research

**Q28 — What should be researched next?** (recommended follow-on missions, not implementation plans)

Ranked by architectural uncertainty × risk × unblocked flows. **Rigby SIGN cycle 1 fold NH #4 consolidation: R1 (F1 provenance) + R4 (dual representation) merged into single umbrella R1 "Dual-representation + provenance contract"** — because if the WS scanner path is in-memory and readers ignore provenance, you cannot reason globally about opportunity truth/provenance. Subsequent R-numbers shift by -1.

| # | Research | Uncertainty × Risk | Unblocks | Owner |
|---|---|---|---|---|
| R1 | **Dual-representation + provenance contract (umbrella)** — treat "F1 provenance-filter drift" + "dual opportunity representation" as one architectural risk. **Prerequisite sub-task R1.0:** identify origin/lifecycle of `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` (source, refresh cadence, persistence, provenance boundary, invariants). Once R1.0 is answered, R1 subtasks are: (a) enumerate every writer + every reader across all Category A models; (b) identify writer/reader provenance mismatches; (c) propose reader-side filter framework; (d) propose F3 durability fallback design for `spider_opportunity_connector` Redis-only path. | HIGH × HIGH | Prevents silent Opportunity data loss; enables source-based analytics; feeds Category E attribution accuracy; resolves the WebSocket dual-source drift; unblocks Group 1700 Observability arc | Post-arc design-preparation ADR (writer-side standardization + reader-side filter framework + realtime consumer design + Redis fallback) |
| R2 | **Scoring rate telemetry probe** — verify current `OpportunityScore` row count vs `Opportunity` row count; verify hourly beat firing (`CeleryTaskEvent` history for `score_opportunities_from_spider_data`); reconcile Session 526's 2% scoring rate observation to current state | HIGH × MEDIUM | Grounds S1499 canonical summary's "underutilization" claim; feeds ownership recommendation | Rigby-side ORM probe (S1499 or immediate) |
| R3 | **Complete producer inventory** — resolve 21 pattern-match false positives from §9.2 by verifying each file's Opportunity write path (mainline vs FreelanceOpportunity/RealJobOpportunity/OpportunityTracking) | MEDIUM × MEDIUM | Completes Category A + Category F producer picture; enables full F1 sweep under R1 | Category F child audit S1406 |
| R4 | **PeriodicTask row verification** — Rigby probes `PeriodicTask.objects.filter(task__contains='opportunity')` to enumerate active beat schedules for Category A tasks | LOW × MEDIUM | Confirms/denies hourly-scoring drift claim (§14 D4) | Immediate Rigby-side probe |
| R5 | **`OpportunityAIAnalyzer` liveness probe** — Rigby-side `LLMCallEvent` grep for OpportunityAIAnalyzer invocations in last 30d; direct file:line inspection of any listed callers | LOW × MEDIUM | Determines if service is orphan (delete-candidate per §15 T7 with S1246 fleet-caller sweep) or deferred-by-policy | Rigby-side probe + fleet audit |
| R6 | **`expires_at` enforcement audit** — determine if any cron / query / task filter enforces `Opportunity.expires_at` or if the field is advisory-only | MEDIUM × MEDIUM | Data-hygiene design-preparation for retention policy | Post-arc design-preparation |
| R7 | **`OPPORTUNITY_CREATED` stream disposition** — Rigby verifies dormant vs dead-code intent; if dormant-planned, name the design-preparation ADR that would activate it; if dead code, remove | LOW × LOW | Simplifies EventBus registry | Immediate Rigby-side inspection |
| R8 | **T5 Celery route duplication cleanup** — dedupe `score_opportunities_from_spider_data` between `settings.py:1277` (`long_running`) and `:1484` (`content`); verify intent via git blame + Session 1063 handoff | LOW × MEDIUM (important-but-contained per Rigby SIGN cycle 1) | Removes drift-prone config; potentially restores designer-intended queue tier | Follow-on cleanup PR (design-preparation, not scoped to this arc) |

---

## 20. Appendix

### 20.1 Files inspected

**Load-bearing runtime files (verified at HEAD `ae30a1fe`):**
- `core/models_unified_system.py` (Opportunity family, lines 1201, 1694, 2552, 2613, 2805, 2905, 3000, 3394, 3493)
- `core/models_engagement_metrics.py:164` (OpportunityInteraction)
- `core/models_autonomous_situations.py:352` (FreelanceOpportunity — adjacent)
- `intelligence/models.py:416` (OpportunityTracking — sports lane)
- `core/services/opportunity_pipeline_orchestrator.py`
- `core/services/opportunity_execution_pipeline.py`
- `core/services/opportunity_scorer.py`
- `core/opportunity_ai_analyzer.py`
- `intelligence/opportunity_storage.py`
- `intelligence/spider_opportunity_connector.py`
- `intelligence/sports_opportunity_generator.py` (verified §7.3 sports lane at lines 82-111)
- `ml_pipeline/opportunity_categorizer.py`
- `core/agents/analysis/opportunity_scoring_agent.py`
- `core/agents/opportunity_pipeline_agent.py`
- `core/consumers_base.py` (lines 2510-2570 verified)
- `core/routing.py:95`
- `core/services/event_bus.py:25, 559`
- `core/services/event_handlers.py:164, 536`
- `core/services/scoring_dispatcher.py:41`
- `core/tasks.py:2163`
- `core/settings.py:1277, 1484` (queue routing duplicate verified)
- `core/views_opportunity.py`
- `core/services/pa_tool_schemas.py:1095, 1111`
- `core/services/tool_dispatcher.py:272, 289, 330`
- `core/epa_handlers_tools.py:2011`
- `core/management/commands/rescore_opportunities.py:21`

**Research docs consulted:**
- `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — full doc, §2.4 + §10.2 + §11.4 + §12.1 load-bearing
- `docs/research/platform_architecture_inventory.md` §3.32 + §4.9 + §10.3
- `docs/research/platform/cross_domain_integration_audit.md` §2.4 + §3.7 + §5.10 + §6.2 + §9.6 + §14 #36
- `docs/research/domains/memory/1399_memory_canonical_summary.md` §4 F1/F2/F3/F4
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §9 (28 canonical Q's) + §11.2 (20-section template) + §13 (sub-agent sweep) + §14 (evidence rules) + §15 (SIGN stage table) + §16 (commit policy) + §17 (graduation criteria)
- `docs/research/process/RESEARCH_OPERATING_SYSTEM.md` §0–§5 + §8.1 (research contract)
- `docs/research/OPEN_ARCS.md`
- `docs/PLATFORM_INVENTORY.md`
- `docs/handoffs/SESSION_1025_SCORING_CONTRACT.md`
- `docs/handoffs/SESSION_872_COMPLETE.md`
- `docs/handoffs/SESSION_1114_ACTIVE_MODULE_OWNERSHIP_MAP.md`
- `docs/audits/audit_revenue_opportunity.md`
- `docs/WIREMAP.md`
- `docs/audits/discovery_celery_tasks.md`
- `docs/CELERY_AUDIT.md`

### 20.2 Grep patterns used

- `Opportunity\.objects\.create|Opportunity\(` — mainline Opportunity producer discovery (25 files matched; 4 confirmed mainline producers).
- `publish_opportunity_scored_event` — event publisher call site verification (`scoring_dispatcher.py:41` confirmed).
- `score_opportunities_from_spider_data` — beat-schedule + queue routing verification.
- `OpportunityScannerConsumer` — WebSocket consumer routing + class body.
- `opportunity-scanner` — WebSocket routing verification (`core/routing.py:95`).
- Section markers in playbook + parent doc to load-bear on §-refs.

### 20.3 Unresolved unknowns (rollup from all sections)

Consolidated §7 UNKNOWNs from all 6 sub-agents + parent-Claude:

1. `PeriodicTask` row existence for hourly scoring beat (§19 R5).
2. `intelligence_engine.get_current_opportunities()` source semantics (§19 R4).
3. `OpportunityAIAnalyzer` invocation liveness (§15 T7 + §19 R6).
4. Partnership_* field population rate (§14 D-cluster + §19 R1 addendum).
5. `metadata` catch-all field key consumption (§14 + §19 R1).
6. `expires_at` enforcement path (§15 T11 + §19 R7).
7. Category F Income/Jobs surface producer contribution to Opportunity family (§19 R3).
8. `EventStream.OPPORTUNITY_CREATED` design intent (§15 T9 + §19 R8).
9. `OpportunityPipelineOrchestrator` invocation source in production (§7.2 + §19 R6).
10. Scoring rate current-state (Session 526 baseline was 2%; §19 R2).
11. `OpportunityInteraction.personalization_boost` reader existence (§14 + §19 R1).

### 20.4 Conflicts between sources

- **S1274 §2.4 line 270** "Sports → Opportunity MISSING" — accurate for mainline Opportunity; ambiguous label. Resolved at §9.1 with clarifying note (§14 D5).
- **Agent 3 (sub-agent) vs three doc sources** on beat scheduling for `score_opportunities_from_spider_data`. Resolved: three doc sources win (hourly beat is documented); Agent 3's negative claim downgraded to UNKNOWN pending PeriodicTask verification (§14 D4 + §19 R5).
- **Agent 6 (sub-agent) flagged OpportunityPipelineOrchestrator ↔ OpportunityExecutionPipeline as duplication candidate** vs Agent 2's direct code read showing complementary roles. Resolved: Agent 2 wins (§17.3 complementary, not overlapping).
- **Session 1025** scoring contract applies to SignalCluster not Opportunity — not a conflict, but a naming trap for future readers; noted at §11.

### 20.5 Verifier-loop corrections (Rigby SIGN fold notes)

**Parent-Claude verifier-loop pre-SIGN corrections** (already applied to §14 + §15 + §17):
- Agent 3 beat-schedule negative claim → downgraded to UNKNOWN.
- Agent 6 orchestrator-overlap claim → resolved as complementary via Agent 2 direct read.
- Agent 3 EventBus publisher line (282/480) → clarified to `scoring_dispatcher.py:41` at primary invocation; `282, 480` are higher-level caller lines per S1274 §6.2 registry.
- Dual opportunity representation → surfaced as NEW load-bearing finding (§14 D6 + §19 R1 umbrella) after direct read of `consumers_base.py:2540`.
- Celery queue-routing duplicate definition → surfaced as NEW debt finding (§15 T5) after direct grep of `settings.py`.

**Rigby SIGN cycle 1 fold notes (2026-07-01, isolation pin `pa-16d8b24d30e7a7d8`):**

Overall confidence: **High**. Final verdict: **SIGN-with-edits (4 folds).**

**Rigby independently verified all 4 primary spot-check citations:**
- **Sports lane (§7.3 + §9.1 D5):** `intelligence/sports_opportunity_generator.py:83` → `OpportunityTracking.objects.create(...)` — CONFIRMED.
- **Dual representation (§14 D6):** Rigby's grep of `intelligence_engine.get_current_opportunities()` **strengthened the finding by surfacing MORE call sites** — not just OpportunityScannerConsumer at `consumers_base.py:2541`, but 5 total sites (lines 1696, 1730, 2541, 2557, 2597). This means the dual-representation pattern is broader than initially captured. Folded into §14 D6 note + §19 R1 umbrella.
- **Celery duplicate (§15 T5):** `settings.py:1277` (`long_running`) + `settings.py:1484` (`content`) — CONFIRMED.
- **OPPORTUNITY_SCORED registry (§10.1):** Rigby verified `event_bus.py:25` stream def + `event_bus.py:581` Event assembly + worker subscription at `event_handlers.py:536` (`create_validation_worker` streams). She could NOT independently verify handler registry mapping in that spot-check scope — I re-verified independently at `event_handlers.py:48` (`self.register('opportunity_scored', handle_opportunity_scored_event)`).

**Fold M1 (must-fix — sports lane wording, §1 + §7.3 + §9.1 D5 + §14 D5 + §17.2):** Rigby flagged that v1's "sports is a separate lane, not MISSING" framing could be misread as "sports integration is solved." Corrected: S1274's MISSING classification **remains ACCURATE for mainline `Opportunity`**; the wording refinement is that sports IS persisted somewhere (`OpportunityTracking` intelligence lane), so "separate lane" is more precise than "missing implementation" — but from mainline `Opportunity`'s perspective, sports remains untouched. Cross-wire from `OpportunityTracking` → `Opportunity` is what's missing.

**Fold M2 (must-fix — §10.1 EventBus overreach):** v1 draft claimed the handler "routes confidence 50-85% → HITL VALIDATION_REQUIRED event"; direct read of `event_handlers.py:186-188` corrected this to DETECTS + LOGS only (the inline comment says "HITL service will have already created the validation request"). v1 also claimed 3 consumer groups (`scoring_workers`, `validation_workers`, `analytics_workers`) from S1274 §6.2 baseline; only `create_validation_worker` was independently verified this session — the others are cited from S1274 as inherited, not re-verified. §10.1 now:
- Strengthens: adds handler-to-event-type registration citation `event_handlers.py:48`; adds payload composition citation `event_bus.py:581`; adds direct source of the corrected priority logic from publisher wrapper body.
- Downgrades: `scoring_workers` + `analytics_workers` group claims marked CANDIDATE (S1274-inherited, not this-audit-verified); `process_event_bus_scoring_queue` task at `tasks.py:4726` marked CANDIDATE.
- Corrects: handler action from "routes to HITL event" → "detects + logs" per file:line comment.

**Fold NH #3 (nice-to-have — §15 T5 operational consequence):** Added detail on WHY the queue mismatch matters: `long_running` queue has concurrency=1, 512MB, aggressive recycling (per `settings.py:1268-1273` comments); `content` was designed for content-generation. A 100-item ML scoring pass under `content` semantics may cause latency regression, OR may be intentional post-Session-1063 optimization — verify designer intent via git blame + Session 1063 handoff.

**Fold NH #4 (nice-to-have — §19 R1 + R4 umbrella):** Collapsed R1 (F1 provenance drift) and R4 (dual opportunity representation) into single umbrella R1 "Dual-representation + provenance contract" with prerequisite sub-task R1.0 = "identify origin/lifecycle of `get_current_opportunities()`." Subsequent R-numbers shifted by -1 (former R5→R4, R6→R5, R7→R6, R8→R7). Added new R8 for T5 Celery route cleanup (Rigby explicitly said keep it as "important-but-contained").

**Post-fold status:** SIGN-with-edits (4 folded) → **Rigby SIGN-clean cycle 2 (High confidence, 2026-07-01)** on fold summary. Rigby verdict verbatim: "SIGN-clean (cycle 2 unnecessary; ship to Chris commit-gate). No remaining blockers based on your fold summary. The two must-fix items from cycle 1 are now addressed in the way I intended... The nice-to-haves are additive and don't introduce new risk. Ship to Chris commit-gate. You can retire the S1401 isolation pin at close per playbook §15." Now awaiting Chris commit-gate. Isolation pin `pa-16d8b24d30e7a7d8` retired at S1401 close.

### 20.6 28 canonical questions coverage checklist (per playbook §9)

- Q1 ✓ §2 (domain purpose)
- Q2 ✓ §2 (business problem)
- Q3 ✓ §3 (entry points)
- Q4 ✓ §4 (models)
- Q5 ✓ §5 (services)
- Q6 ✓ §3.2 + §6 (APIs)
- Q7 ✓ §3.4 + §8 (Celery tasks)
- Q8 ✓ §3.5 + §8 (management commands)
- Q9 ✓ §7 (runtime flows)
- Q10 ✓ §11 (existing documentation)
- Q11 ✓ §11 (research already exists)
- Q12 ✓ §13 (maturity)
- Q13 ✓ §12 (research coverage)
- Q14 ✓ §9.1 (integrations)
- Q15 ✓ §9.1 (missing integrations)
- Q16 ✓ §4.1 (data owned)
- Q17 ✓ §9 (data consumed)
- Q18 ✓ §9 (data produced)
- Q19 ✓ §10.1 (events emitted)
- Q20 ✓ §10.3 (events should emit)
- Q21 ✓ §9.3 (inbound consumers)
- Q22 ✓ §9 (outbound dependencies)
- Q23 ✓ §17 (model overlaps)
- Q24 ✓ §16 (boundary violations)
- Q25 ✓ §18 (ownership unclear)
- Q26 ✓ §15 (technical debt)
- Q27 ✓ §14 (drift)
- Q28 ✓ §19 (future research)

### 20.7 Parent §12.1 Category A F.iii questions coverage

- **What IS an Opportunity (10 variants; authoritative schema)?** ✓ §4 (mainline `Opportunity` at `core/models_unified_system.py:1201` with 27 fields + 10-variant family enumerated).
- **Who produces Opportunities (all producers, not just spiders)?** ✓ §9.2 for mainline Opportunity (4 confirmed producers + Category F handoff to S1406 for full inventory).
- **How does scoring flow through `OpportunityScoringAgent` + `OpportunityPipelineAgent` + ML categorizer?** ✓ §7 (Flows α + β + δ) + §9.1 ML pipeline integration.
- **What does `OPPORTUNITY_SCORED` event carry + who consumes?** ✓ §10.1 (payload + 4 consumer groups).
- **What is `OpportunityScannerConsumer` for?** ✓ §6.2 + §7.5 + §14 D6 (READ-ONLY listener streaming from `intelligence_engine`, NOT mainline Opportunity).
- **Does `sports_opportunity_generator.py` produce into mainline Opportunity or a separate lane?** ✓ §7.3 + §9.1 D5 (**SEPARATE LANE — writes `OpportunityTracking`**).

All 6 Category A F.iii questions answered.

### 20.8 15 inherited findings acknowledgment (parent §11.4)

All 15 inherited findings from S1273 + S1274 + S1399 cited (not rediscovered) throughout audit. Explicit citations at §7 (Spider→Opportunity STRONG at §7.1), §9.1 (integration map inheritances), §14 (drift baselines), §15 (F1/F2/F3 methodology inheritance from S1399 §4), §18 (S1274 §14 #36 ownership gap), §17 (S1274 §5.10 tight-coupling for downstream categories).

### 20.9 Gating checklist (playbook §17 single-audit graduation criteria)

- [x] Audit file exists at `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`
- [ ] Frontmatter `status: active` + `authority: research` — **currently `draft`; flips at Chris commit-gate**
- [ ] `verifier_loop` records Rigby SIGN status — **pending SIGN cycle 1**
- [x] All 28 canonical questions answered (see §20.6)
- [ ] Doc committed to branch — **pending Chris commit-gate**
- [ ] `ARCHITECTURE_INDEX.md` bumped (v18 → v19) — **at commit time**
- [x] Follow-on research queue captured in §19

Chris commit-gate is the last remaining box.

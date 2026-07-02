---
title: "Sports Cross-Domain Integration Lens & Posture Decision Framing Audit"
status: draft
category: child_audit
subdomain_category: F
authority: "child-audit for Category F per parent §5 sequence; LAST child before xx99 (S1599); LOAD-BEARING for D59 posture-decision evidence plan owed to xx99 canonical summary; sixth and final sibling to apply D62 = (a) mini-schema propagation upfront"
domain: sports
session: 1506
generated: 2026-07-02
last_verified: 2026-07-02
parent_doc: 1500_sports_domain_scoping.md
sibling_docs:
  - 1501_sports_odds_ingestion_normalization_audit.md
  - 1502_sports_prediction_analytics_agents_audit.md
  - 1503_sports_wager_tracking_outcome_verification_audit.md
  - 1504_sports_betting_content_pipeline_audit.md
  - 1505_sports_frontend_surface_audit.md
verifier_loop: "Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence via fresh isolation pin pa-c2cdbd5c0b8c451b (retired at S1506 close). F1-F2 folds landed at commit-time: F1 §14.5 anchor-set tightening (/odds + /futures + /slip explicit bypass; /arb shared-agent exclusion made explicit at section body per Rigby Q5 Batch 1 edit); F2 §20.6 §F scoring rubric + threshold minima for xx99 consumption-readiness per Rigby Q15 Batch 3 edit. D48 preemptive stability probe 9th arm CLEAN across 3 substantive SIGN turns (four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506). Parent-Claude verifier-loop on 6 load-bearing pre-Explore claims — all 6 verified correct against source before draft integration (SignalCluster.PATTERN_TYPE_CHOICES at core/models_signal_intelligence.py:75-86; send_query_status/handle_run_analytics unimplemented per grep; PostgreSQL search_path at core/settings.py:340; /ws/dbao/ + /ws/dbao-dashboard/ at core/routing.py:369-370; sports_intelligence hardcoded at intelligence/views.py:44; SportsBettingLearningBridge AgentMemory writes at core/learning_bridges/sports_betting_bridge.py:532,606). Cycle 2 SIGN-clean at High anticipated post-fold-land per S1501-S1505 cycle-1-predict-cycle-2 accuracy."
owner: claude-code-parent
---

# Sports Cross-Domain Integration Lens & Posture Decision Framing Audit

## 1. Executive Summary

This audit inventories **Category F — Cross-Domain Integration Lens & Posture Decision Framing** of the Group 1500 Sports/DBAO/Intelligence research arc. Category F is the **sixth and last child audit** under parent §5 mission sequence; it consumes P1–P5 evidence (S1501 Cat A ingestion + S1502 Cat B agents + S1503 Cat C wager/outcome + S1504 Cat D content + S1505 Cat E frontend) and produces **the posture-decision evidence plan owed to xx99 (S1599) per D59**. This audit is explicitly framing / evidence-plan work, **not posture selection** — per D59 Chris-gated post-arc ADR.

**Domain shape.** The Cat F cross-domain integration surface is **four architecturally distinct materialization axes**, each with a different maturity verdict:

1. **DBAO product-line materialization** — declared PostgreSQL schema (`core/settings.py:340`) + `/ws/dbao/` + `/ws/dbao-dashboard/` consumers (`core/routing.py:369-370`) + `VITE_DBAO_API_URL`/`VITE_DBAO_WS_URL`/`VITE_DBAO_ENABLED`/`EXPO_PUBLIC_DBAO_API_URL` env-vars (`.env.example:72-86`) + `x-dbao-client` CORS-whitelisted header (`core/settings.py:707`). Runtime materialization: **zero** — schema empty, WS handler broadcasts random mock data (S1505 §14.1 upheld + strengthened this session), 2 of 3 message handlers unimplemented (`send_query_status`, `handle_run_analytics` — grep returns zero definitions), env-vars declared but never read by any frontend, header never sent or read. **NEW pattern class this audit: NAMING-CONVENTION-WITHOUT-MATERIALIZATION.**

2. **Intelligence surface** (`intelligence/realtime_engine.py` — 702 lines + `intelligence/views.py` + `intelligence/urls.py`) — engine layer is **SPORTS-NATIVE** (`_sports_intelligence_loop` at lines 123-138 orchestrates `TheOddsAPIProvider` + `ESPNProvider` + arbitrage/value/momentum detection). REST/frontend layer is **domain-neutral** — `IntelligencePage` (`frontend/src/pages/IntelligencePage.tsx`) does not import `bettingApi`/`sportsHubApi`; its tabs (gates/pilots/experiments/spiders/predictions/income) do not carry sports data. The `sports_intelligence: True` flag at `intelligence/views.py:44` is a **hardcoded literal** (never consulted at runtime); duplicate hardcoded at `core/intelligence_api.py:94`. **NEW pattern class: DECLARED-FEATURE-FLAG-GATES-NOTHING** (analog to S1505 §14.1 MOCK-DATA-CONSUMER but at flag layer instead of data layer).

3. **Discord sports surface** — Discord `InteractiveCommands` Cog (`core/services/discord_bot.py:1977`) exposes 7 sports slash commands (`/odds`, `/arb`, `/bet`, `/resolve`, `/futures`, `/slip`, `/bankroll`) totaling ~850 lines. `/bet` (line 1571) creates `Wager` rows, `/resolve` (line 1687) updates `Wager` + `Bankroll` — Discord is a **first-class write consumer** of the sports models, parallel to REST + frontend. `_impl_collect_sports_odds_intelligence` (`core/tasks_financial.py:1815`) posts trending odds to Discord every 30 minutes via `TheOddsSpider` — **bypasses** `SportsBettingCoordinator` + `RealtimeIntelligenceEngine`. Extends the S1504 HOT-PATH-CHOKE pattern from REST bypass to Discord bypass (S1504 §14 hot-path-choke analog).

4. **Cross-domain feedback surface** — Signal Engine gap (`sports_odds` not a `SignalCluster.pattern_type` — 10 valid choices at `core/models_signal_intelligence.py:75-86`, `sports_odds` NOT among them; verified) + Memory-Domain bridge partial (`core/learning_bridges/sports_betting_bridge.py` writes to `AgentMemory` at lines 532 + 606 for `SportsOddsAnalyst` + `ArbitrageDetector` but 2 of 4 market agents — `GamePredictor`, `SharpActionDetector` — do NOT invoke it and Cat F emits **zero writes to `AgentKnowledgeSource`**) + `MLPrediction`/`BettingOutcomeVerifier` decoupling (BettingOutcomeVerifier at `core/services/betting_outcome_verifier.py:30-481` settles wagers but **never touches `MLPrediction`**; `PredictionEvaluator` at `sports/prediction_evaluator.py` evaluates predictions but **never triggered by wager settlement** — two verification systems fully independent).

**Load-bearing findings owed to xx99 (S1599) — 14, ranked by posture-decision weight:**

1. **CRITICAL architectural — DBAO is a NAMING-CONVENTION-WITHOUT-MATERIALIZATION product-line codename.** Six named artifacts declared (schema, `/ws/dbao/`, `/ws/dbao-dashboard/`, VITE env-vars, EXPO env-vars, `x-dbao-client` header); zero runtime state carried. No Django model has `db_table = 'dbao.*'` (grep zero hits across `core/models*.py`). No migration creates the schema (grep zero hits in `core/migrations/**`). `send_dbao_metrics` at `core/new_pages_consumer.py:310-331` is 100% random data (`random.randint` + `random.uniform` for every field). `send_query_status` (called at line 123) and `handle_run_analytics` (called at line 125) are **unimplemented stubs** — grep for `async def send_query_status` and `async def handle_run_analytics` across `core/` returns zero results. VITE env-vars declared in `.env.example:72-86` but grep of `frontend/**/*.{ts,tsx,js}` returns zero consumers. `x-dbao-client` CORS-whitelisted at `core/settings.py:707` but grep returns exactly one hit (the whitelist itself) — never sent, never read. **This is the load-bearing finding for D61 (parent scoping) codename shape question.** See §14.1. NEW pattern class this audit: NAMING-CONVENTION-WITHOUT-MATERIALIZATION (distinct from S1505 §14.1 MOCK-DATA-CONSUMER which required a real consumer running — here even the consumer is stub-referenced).

2. **CRITICAL architectural — Sports outcomes never route to `MLPrediction`; two verification systems fully decoupled.** `BettingOutcomeVerifier` (`core/services/betting_outcome_verifier.py:30-481`) settles `PlacedWager`/`PlacedWagerLeg` + verifies `HumanAttentionItem` arbitrage watches; grep confirms zero references to `MLPrediction` in this file. `PredictionEvaluator` (`sports/prediction_evaluator.py:40-420` per Explore Agent 6) evaluates `MLPrediction.was_correct` from game scores; zero references to `PlacedWager`/`PlacedWagerLeg` in this file. No linking FK exists between `BettingOutcome` and `MLPrediction`; implicit `game_id`/`event_id` join key is never actually joined at runtime. **NEW pattern class this audit: DECOUPLED-VERIFICATION-SYSTEMS.** See §14.2 + §16.1.

3. **HIGH architectural — Zero `sports_odds` emission path to Signal Engine (5-arc consumer-side pattern → 6-arc pattern this session).** Confirmed at every layer per Explore Agent 4: (a) `SignalCluster.PATTERN_TYPE_CHOICES` at `core/models_signal_intelligence.py:75-86` lists 10 valid types + `sports_odds` NOT among them (verified this session); (b) `signal_aggregation_service.py` (`core/services/signal_aggregation_service.py:216-251, 723`) consumes `LegacySpiderData` universally but hardcoded `PATTERN_TYPE_KEYWORDS` (lines 139-168) and `TOPIC_PATTERNS` (lines 171-182) reference non-sports domains only; (c) zero bridging code — grep for `SportsSignal`, `betting_signal`, `bookmaker_signal`, `line_movement_signal` returns zero hits; (d) zero sports-native alternative aggregator — no `SportsSignalAggregator`, no `BookmakerConsensus`, no `LineMovementCluster` class exists. Extends S1502 §14.3 + S1503 §14.3 + S1504 §14.5 + S1505 §14.6 5-arc consumer-side pattern to **6-arc consumer-side pattern**. See §14.3 + §20.6 posture-decision evidence plan §A2.

4. **HIGH architectural — DECLARED-FEATURE-FLAG-GATES-NOTHING at `sports_intelligence` boundary.** `intelligence/views.py:44` returns `'sports_intelligence': True` as a hardcoded literal inside `SkynetStatusView.get()` response dict. `core/intelligence_api.py:94` duplicates the same hardcoded literal in `skynet_status()` view. Neither branch is consulted against `settings.SPORTS_INTELLIGENCE`, a feature-flag registry, or a model row. The flag is **reported to the frontend as a capability indicator** but gates zero runtime paths. `settings.SPORTS_ANALYTICS` config block (`core/settings.py:629-633`) is similarly defined but never consulted (`ENABLE_SPORTS_ANALYTICS`, `SPORTS_CONFIDENCE_THRESHOLD`, `SPORTS_MIN_EDGE`, `SPORTS_MAX_CONCURRENT_ANALYSES` — grep returns zero runtime consumers). **Pattern class: DECLARED-FEATURE-FLAG-GATES-NOTHING** — distinct from S1505 §14.1 MOCK-DATA-CONSUMER because that pattern had a real consumer running with fake data, whereas this pattern has real config declared with no consumer at all. See §14.4 + P6 parked (Rigby SIGN cycle 1 Q4 fold from parent scoping).

5. **HIGH architectural — Discord `/odds` + `/futures` + `/slip` HOT-PATH-CHOKE bypass extends S1504 pattern to Discord surface.** Per Explore Agent 3: Discord `/odds` (`discord_bot.py:1108`) calls `TheOddsSpider().fetch_data(max_results=100)` directly + rebuilds odds display inline (7-sport emoji map, filter logic, embed rendering) instead of routing through `SportsBettingCoordinator` (`core/services/sports_betting_coordinator.py:39-96`). `/futures` (line 1744) and `/slip` (line 1851) follow same pattern. REST `/api/v1/betting/brief` (`views_odds_sports.py:3248`) routes through the coordinator; Discord bypasses it. **If TheOddsSpider changes field names, Discord and REST diverge silently.** S1504 §14 HOT-PATH-CHOKE pattern extended from REST-bypasses-coordinator to Discord-bypasses-coordinator. See §14.5 + §17.2 duplicate/overlapping systems.

6. **HIGH architectural — Sports-Memory-Domain bridge PARTIAL (2 of 4 sports market agents covered; zero AgentKnowledgeSource writes).** `SportsBettingLearningBridge` (`core/learning_bridges/sports_betting_bridge.py:532,606`) writes to `AgentMemory` for `SportsOddsAnalyst` (wager outcomes) and `ArbitrageDetector` (arb verifications) via `BettingOutcomeVerifier` → `_create_learning_records()` (`core/services/betting_outcome_verifier.py:455-480`). The other 2 market agents — `GamePredictor` (`core/agents/markets/game_predictor.py`) + `SharpActionDetector` (`core/agents/markets/sharp_action_detector.py`) — have zero AgentMemory write path. Zero `AgentKnowledgeSource` writes for any sports agent (grep across `core/learning_bridges/` returns zero `AgentKnowledgeSource.objects.create` for sports contexts). Sports market agents inherit from `BaseAgent` but do **not** override or actively invoke `_record_learning_outcome()` (`core/agents/base_agent.py:3991-4060`) or `_create_execution_memory()` (`core/agents/base_agent.py:4076-4145`) in their `execute()` bodies. **Pattern class: PARTIAL-LEARNING-BRIDGE** — 50% agent coverage (2/4), 0% AgentKnowledgeSource writeback. See §14.6 + §16.2.

7. **HIGH operational — `/ws/dbao-dashboard/` sibling route surfaced by verifier-loop; broadens S1505 §14.1 MOCK-DATA-CONSUMER to include the dashboard-labeled route.** S1505 audit named `/ws/dbao/` (`core/routing.py:369`) as the MOCK-DATA-CONSUMER surface. Verifier-loop this session confirms an adjacent sibling route registration at `core/routing.py:370` — `re_path(r'^ws/dbao-dashboard/$', NewPagesConsumer.as_asgi())` — that dispatches to the same `NewPagesConsumer` class with the same page_type detection logic (`core/new_pages_consumer.py:32-39`). Both routes broadcast the same random mock payload. S1505 §14.1 footprint expands from 1 route to 2 routes. See §14.7.

8. **HIGH operational — `_impl_collect_sports_odds_intelligence` Discord digest posts to CHANNEL_BOARDROOM but docstring says `#market-intelligence`; docstring-vs-channel-runtime drift.** Function at `core/tasks_financial.py:1815-1902` (verified via Explore Agent 3). Docstring reads *"Post trending sports odds to Discord #market-intelligence"* but `send_betting_digest()` writes to `CHANNEL_BOARDROOM` (hardcoded at `core/services/discord_notifications.py:40`). Channel-name drift. Runs every 30 minutes via Celery beat (`core/celery.py:787`). **NEW pattern class: DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT** (silent misinformation for operators consulting docstring). See §14.8.

9. **MED-HIGH — `RealtimeIntelligenceEngine` cross-domain "demo" branches contradict its 100% sports engine implementation.** Per Explore Agent 2: `_opportunity_detection_loop` (lines 439-452) + `_prediction_generation_loop` (515-528) + `_cross_domain_analysis_loop` (592-605) are named as cross-domain but **all populate hardcoded demo data** (crypto/trading mock values in lines 454-513 per Explore report). The engine is architecturally sports-native (`_sports_intelligence_loop` at lines 123-138 is the only real loop) but instrumented as cross-domain. **Pattern class: SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION.** See §14.9 + §17.3.

10. **MED-HIGH — Zero Celery beat entry for `RealtimeIntelligenceEngine`; started manually via `start_skynet()` (line 693) / `stop_skynet()` (line 699).** No cron trigger, no `PeriodicTask` row, no `@shared_task` wrapper. If the process is never manually started, the engine never runs. This produces a **latent-zero-fire** analog to S1503 §14.1 `daily_betting_digest` (which had a real beat entry that never fired at runtime); here the engine has neither beat nor task registration — even more latent. See §14.10.

11. **MED — Frontend `IntelligencePage` does not consume sports data despite `sports_intelligence` flag reporting True.** `frontend/src/pages/IntelligencePage.tsx` (per Explore Agent 2) imports `intelligenceApi`, `pilotsApi`, `experimentsApi`, `spidersApi`, `opportunitiesApi`, `incomeBuilderApi`, `experimentRecommendationsApi` — does not import `bettingApi` or `sportsHubApi`. Its tabs (`gates`, `pilots`, `experiments`, `spiders`, `predictions`, `income`) have no sports read path. The `sports_intelligence: True` capability reported to the frontend is thus unreflected in the frontend's own consumption pattern. **User-facing implication: any operator inspecting `SkynetStatusView` would see sports intelligence claimed as active while the surface is unreachable.** See §14.11.

12. **MED architectural — `_impl_collect_sports_odds_intelligence` bypasses BOTH `SportsBettingCoordinator` AND `RealtimeIntelligenceEngine`.** Direct `TheOddsSpider().get_upcoming_events(hours=24)` at `core/tasks_financial.py:1815-1902`. Two coordinator layers exist (sports coordinator + intelligence engine) — Discord digest task ignores both. This is the second Discord-side coordinator bypass surfaced this session (see finding 5 for the slash-command bypass). **Pattern class: DUAL-COORDINATOR-BYPASS.** See §17.1.

13. **MED — CODEOWNERS gaps compound across sports surface.** `frontend/src/pages/BettingPage.tsx` unassigned per S1505 §18.1. Verifier-loop this session confirms `.github/CODEOWNERS` has zero rows for `core/services/betting_outcome_verifier.py`, `core/services/sports_betting_coordinator.py`, `core/learning_bridges/sports_betting_bridge.py`, `intelligence/realtime_engine.py`, or the DBAO consumer files. **Compound ownership gap: every sports-relevant runtime file is un-owned.** See §18.1.

14. **MED — Post-arc anchor drift: `docs/topics/sports-betting.md` gap remains after 6 audits.** S1500 parent scoping §11.2 recorded absence; no follow-on landed. Per xx99 F.iii criterion 6c (parent §12.1), the topic doc is owed. See §19.1 + §19.5.

**Maturity verdict per §13:** **PARTIAL (mixed; multi-axis)** — sixth distinguishing maturity shape:

- **Cat F axis 1 (DBAO product-line):** NAMING-CONVENTION-WITHOUT-MATERIALIZATION — six declared artifacts, zero runtime state, two unimplemented handler stubs.
- **Cat F axis 2 (Intelligence surface):** SPORTS-NATIVE-ENGINE-DOMAIN-NEUTRAL-REST — engine layer sports-native, REST/frontend layer domain-neutral, flag layer DECLARED-GATES-NOTHING.
- **Cat F axis 3 (Discord surface):** FIRST-CLASS-WRITE-CONSUMER-BYPASSING-COORDINATOR — 4 read commands + 2 write commands + 1 shared agent + 1 periodic digest, all bypassing SportsBettingCoordinator + Intelligence Engine.
- **Cat F axis 4 (Cross-domain feedback):** ARMED-BUT-DECOUPLED — SportsBettingLearningBridge exists + writes AgentMemory + PARTIAL agent coverage; MLPrediction↔BettingOutcomeVerifier decoupled; SignalCluster emission absent.

Compared to prior siblings: S1501 fragile-contract at ingestion; S1502 armed-but-under-instrumented; S1503 armed-but-zero-fire; S1504 mixed-brief-generation-persistence-forgotten-HOT-PATH-CHOKE; S1505 mixed-WORKING-DEAD-RENDER-MOCK-AUTH-NO-REALTIME. **Cat F introduces the first four-axis compound maturity shape in the arc; each axis carries its own pattern class, requiring xx99 (S1599) to consolidate rather than merge.**

**Not implemented, not proposed.** This is a research audit per playbook §14 no-implementation rule. Findings feed S1599 xx99 canonical summary. §20.6 posture-decision evidence plan is **evidence-plan framing, not posture selection** per D59.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** Category F is the cross-domain integration lens for the Sports domain. It answers: how does the sports betting stack (Cat A ingestion + Cat B agents + Cat C wagers + Cat D content + Cat E frontend) touch the rest of the platform (Signal Engine + Memory Domain + Intelligence surface + Discord + WebSocket infrastructure + DBAO product-line codename)? Its purpose is to inventory every cross-domain surface and produce the **evidence plan** for the Chris-gated integration-vs-island posture decision framed by S1274 §12.3 P1 decision point + D59.

**Q2 — What problem does it solve?** It closes the load-bearing UNKNOWN at Group 1500 open: whether Sports is an **integrated citizen** of the platform (sharing signal aggregation, memory, and intelligence infrastructure with mainline content/agent flows) or an **island** with its own aggregation + learning + intelligence surfaces (currently signaled by DBAO codename + private schema declaration + private WS namespace, but not materialized). Without this evidence plan, xx99 (S1599) would either pick a posture without evidence or defer the framing — both anti-patterns per D59.

### 2.1 Cat F contract statement (Q1+Q2 tightened)

**Cat F guarantees to xx99 (5):**

1. Complete inventory of every cross-domain integration surface between Sports and the rest of the platform (DBAO artifacts + Intelligence surface + Discord + Signal Engine + Memory Domain + `MLPrediction`↔`BettingOutcomeVerifier` linkage).
2. Explicit evidence catalog per posture axis (island vs integrated) drawn from P1–P5 sibling audits + this session's Explore sweeps.
3. Six-sibling application of D62 = (a) pre-brief mini-schema — the 4-item annotation per surface (§4.2).
4. The **posture-decision evidence plan** owed to xx99 per D59 — enumerated criteria + evidence-for/against per posture + operational-cost estimate + failure-modes-if-criteria-not-met — with **explicit "Chris-gated selection" tag** (§20.6).
5. Load-bearing observation extraction from prior siblings' non-guarantee tables + posture-relevant mini-schema rows (§20.7).

**Cat F does NOT guarantee (verified via §14 drift matrix + explore sweeps):**

1. **Posture selection.** Per D59, xx99 does not pick either; Chris ratifies post-arc via ADR. Cat F frames the choice; does not resolve it.
2. **Implementation of any bridge.** If evidence shows `sports_odds → SignalCluster.pattern_type` extension is trivial (config change), Cat F names the change but does not propose the PR.
3. **DBAO codename resolution.** D61 parked at parent scoping §6 for post-arc T-slot. Cat F closes evidence on DBAO's materialization state (finding 1); xx99 flags the codename question; Chris rules.
4. **`sports_intelligence` topic-doc decision.** Per P6 parked (Rigby SIGN cycle 1 Q4 fold from parent scoping §6), Cat F investigates the flag's runtime reach; xx99 owns the topic-doc recommendation.
5. **Cross-domain refactoring proposals.** Findings 5 + 12 (HOT-PATH-CHOKE bypass patterns) are documented; refactoring belongs to post-arc T2 design-preparation follow-ons.
6. **Memory arc learning-bridge design.** Per D62 delegation to S1300, if evidence surfaces the need for a sports→Memory bridge upgrade, Cat F flags + delegates; does not design.
7. **PredictionEvaluator↔BettingOutcomeVerifier reconciliation.** Finding 2 (DECOUPLED-VERIFICATION-SYSTEMS) is documented; reconciliation design is a post-arc T2 follow-on.
8. **Sports-native aggregator design.** Explore Agent 4's island-alternative sketch is a research reference; not a design proposal.
9. **CODEOWNERS assignment.** Finding 13 (compound gap) is documented; assignment is post-arc T4 cleanup.
10. **Docs cascade for `docs/topics/sports-betting.md`.** Finding 14 owed; xx99 §7 anchor-update recommendations name it; landing is post-arc PR.
11. **Discord slash-command redesign** to route through the coordinator instead of TheOddsSpider directly. Findings 5 + 12 documented; refactor is post-arc T2.

These 11 non-guarantees frame the boundary between what Cat F closes vs what xx99 + post-arc T-slots own. Any downstream consumer that assumes any of them will drift.

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?**

### 3.1 DBAO product-line materialization artifacts (declared; largely unmaterialized)

| Artifact | File:line | Runtime state |
|---|---|---|
| PostgreSQL `dbao` schema in search_path | `core/settings.py:340` | Declared; zero Django models targeting `db_table='dbao.*'` (grep zero hits across `core/models*.py`); zero migrations create the schema. |
| `/ws/dbao/` WebSocket route | `core/routing.py:369` | Registered; dispatches to `NewPagesConsumer.as_asgi()`. |
| `/ws/dbao-dashboard/` WebSocket route (sibling) | `core/routing.py:370` | Registered; dispatches to same consumer as `/ws/dbao/`; not named in S1505 audit — verifier-loop this session surfaces the sibling. |
| `NewPagesConsumer.handle_dbao_message` (message router) | `core/new_pages_consumer.py:118-131` | Routes to `send_dbao_metrics` / `send_query_status` / `handle_run_analytics`. |
| `NewPagesConsumer.send_dbao_metrics` (metric handler) | `core/new_pages_consumer.py:310-331` | 100% mock — `random.randint` / `random.uniform` for every field. Zero DB reads. |
| `send_query_status` reference | `core/new_pages_consumer.py:123` (caller) | **Handler undefined** — grep for `async def send_query_status` / `def send_query_status` across `core/` returns zero. AttributeError at runtime if invoked. |
| `handle_run_analytics` reference | `core/new_pages_consumer.py:125` (caller) | **Handler undefined** — grep for `async def handle_run_analytics` / `def handle_run_analytics` across `core/` returns zero. AttributeError at runtime if invoked. |
| `NewPagesConsumer.send_dbao_updates` (periodic broadcaster) | `core/new_pages_consumer.py:450-478` | 10s sleep loop; 40% chance to send metrics per cycle; all mock. |
| `VITE_DBAO_API_URL` env-var | `.env.example:72` | Declared. Grep of `frontend/**/*.{ts,tsx,js}` returns zero consumers. |
| `VITE_DBAO_WS_URL` env-var | `.env.example:73` | Declared. Zero consumers. |
| `VITE_DBAO_ENABLED` env-var | `.env.example:78` | Declared. Zero consumers. |
| `EXPO_PUBLIC_DBAO_API_URL` env-var | `.env.example:85` | Declared. Zero consumers. |
| `EXPO_PUBLIC_DBAO_WS_URL` env-var | `.env.example:86` | Declared. Zero consumers. |
| `x-dbao-client` CORS allow-header | `core/settings.py:707` | Whitelisted. Grep repo-wide returns exactly one hit (the whitelist line itself). Never sent, never read. |
| `DBAODashboardView` template view | `core/views_unified.py:210-218` | Class defined but file header (lines 5-11) marks the module `DEPRECATED`. Not routed in live URL patterns. |
| Legacy DBAO tools-manifest header comments | `core/routing.py:3`, `core/urls.py:3061,3079`, `core/views_odds_sports.py:2` | Header comments only ("Migrated from DBAO tools-manifest"). Zero runtime references. |

### 3.2 Intelligence surface entry points

| Entry point | File:line | Purpose | Runtime state |
|---|---|---|---|
| `RealtimeIntelligenceEngine` class | `intelligence/realtime_engine.py:65-687` | Core sports intelligence engine (702 lines). | Instantiated at import; not auto-started. |
| `start_skynet()` module function | `intelligence/realtime_engine.py:693` | Manual engine start. | Zero Celery beat entries — must be called manually. |
| `stop_skynet()` module function | `intelligence/realtime_engine.py:699` | Manual engine stop. | Zero Celery beat entries. |
| `_sports_intelligence_loop` | `intelligence/realtime_engine.py:123-138` | Sports-native loop; fetches odds + analyzes markets. | Real logic (per Explore Agent 2). |
| `_opportunity_detection_loop` | `intelligence/realtime_engine.py:439-452` | Named cross-domain; **hardcoded demo data** per Explore Agent 2. |
| `_prediction_generation_loop` | `intelligence/realtime_engine.py:515-528` | Named cross-domain; **hardcoded demo data** per Explore Agent 2. |
| `_pattern_recognition_loop` | `intelligence/realtime_engine.py:577-590` | ML placeholder per Explore Agent 2. |
| `_cross_domain_analysis_loop` | `intelligence/realtime_engine.py:592-605` | Named cross-domain; **hardcoded demo data** per Explore Agent 2. |
| `SkynetStatusView` REST endpoint | `intelligence/views.py:24` | Reports capabilities to frontend. | Hardcoded literals. |
| `sports_intelligence: True` flag | `intelligence/views.py:44` | Reported capability. | Hardcoded literal — never consulted at runtime. |
| Duplicate flag in `intelligence_api.py` | `core/intelligence_api.py:94` | Duplicate hardcoded literal. | Same status. |
| `LiveOpportunitiesView` REST endpoint | `intelligence/views.py:60` | Reads engine's in-memory opportunities. | Reads from `intelligence_engine.get_current_opportunities()`. |
| `IntelligencePage` frontend page | `frontend/src/pages/IntelligencePage.tsx` | Intelligence UI. | Does NOT import `bettingApi` or `sportsHubApi` — sports-tangential. |

### 3.3 Discord sports surface entry points

| Command / Task | File:line | Purpose | Read/Write | Coordinator? |
|---|---|---|---|---|
| `/odds` slash command | `core/services/discord_bot.py:1108` | Display odds. | READ | **BYPASSES** — TheOddsSpider directly. |
| `/arb` slash command | `core/services/discord_bot.py:1260` | Arbitrage scan. | READ | Uses `ArbitrageDetector.run()` — same agent as REST. |
| `/bankroll` slash command | `core/services/discord_bot.py:1404` | User bankroll stats. | READ | Reads user's `Wager` rows directly. |
| `/bet` slash command | `core/services/discord_bot.py:1530` | Log new bet. | **WRITE** — `Wager.objects.create()` at line 1571. | N/A (write path). |
| `/resolve` slash command | `core/services/discord_bot.py:1639` | Resolve pending bet. | **WRITE** — `wager.resolve(outcome)` + `bankroll.save()` at lines 1687, 1705. | N/A. |
| `/futures` slash command | `core/services/discord_bot.py:1744` | Championship futures. | READ | **BYPASSES** — TheOddsSpider directly. |
| `/slip` slash command | `core/services/discord_bot.py:1851` | Multi-selection bet slip. | READ | **BYPASSES** — TheOddsSpider directly. |
| `InteractiveCommands` Cog class | `core/services/discord_bot.py:1977` | Owns all 7 sports commands. | Mixed | N/A. |
| `_impl_collect_sports_odds_intelligence` task | `core/tasks_financial.py:1815-1902` | Periodic Discord digest. | READ + Discord POST | **BYPASSES BOTH** — TheOddsSpider directly; ignores coordinator + engine. |
| Wrapper task | `core/tasks.py:6099-6100` | Celery entry point. | — | — |
| Celery beat entry | `core/celery.py:787-791` | Every 30 min; queue=`sports`. | — | — |

### 3.4 Cross-domain feedback surface entry points

| Entry point | File:line | Role | Runtime state |
|---|---|---|---|
| `SignalCluster` model | `core/models_signal_intelligence.py:56-…` | Signal Engine primary model. | `PATTERN_TYPE_CHOICES` at lines 75-86; `sports_odds` NOT among 10 valid types. |
| `signal_aggregation_service.py` | `core/services/signal_aggregation_service.py:1-…` | Emits SignalCluster from LegacySpiderData. | Non-sports keywords/topics hardcoded (lines 139-168, 171-182). |
| `SignalCuratorService` | `core/services/signal_curator_service.py:45-49` | Primary consumer; ranks + dedupes. | Consumes all pattern_types uniformly. |
| `AgentMemory` model | `core/models_unified_system.py:10787-10977` | Memory-domain primary write target. | Sports writes exist. |
| `AgentKnowledgeSource` model | `core/models_unified_system.py:521-628` | Memory-domain secondary write target. | **Zero sports writes** (grep). |
| `SportsBettingLearningBridge.record_wager_outcome` | `core/learning_bridges/sports_betting_bridge.py:532` | AgentMemory write for SportsOddsAnalyst. | Verified this session. |
| `SportsBettingLearningBridge.record_arbitrage_outcome` | `core/learning_bridges/sports_betting_bridge.py:606` | AgentMemory write for ArbitrageDetector. | Verified this session. |
| `BettingOutcomeVerifier.verify_all_pending` | `core/services/betting_outcome_verifier.py:30` | Wager settlement + arb verification. | Zero MLPrediction reads/writes (grep). |
| `BettingOutcomeVerifier._create_learning_records` | `core/services/betting_outcome_verifier.py:455-480` | Bridge invocation point. | Wraps SportsBettingLearningBridge calls. |
| `PredictionEvaluator._evaluate_single_prediction` | `sports/prediction_evaluator.py:202` per Explore Agent 6 | Sets MLPrediction.was_correct. | Zero PlacedWager/Leg reads (grep per Explore). |
| `PredictionEvaluator._feed_to_learning_loop` | `sports/prediction_evaluator.py:421-488` per Explore Agent 6 | Learning-loop feed. | Feeds SportsBettingLearningBridge; no retrain trigger. |
| `MLPrediction.evaluate` (model method) | `sports/models.py:1897-1925` per Explore Agent 6 | Sets was_correct + evaluated_at. | Zero AgentMemory writes. |
| Celery `verify_betting_outcomes` beat | `core/tasks.py:6121-6140` (2h cadence) | BettingOutcomeVerifier trigger. | Real. |

---

## 4. Major Models

**Q4 — What are the major models?**

Cat F is a **cross-domain lens** rather than an owner of dedicated models. It inventories which models the cross-domain surfaces touch:

### 4.1 Sports-owned models consumed by Cat F cross-domain surfaces

| Model | Location | Consumed by | Cat F relevance |
|---|---|---|---|
| `SpiderData` / `LegacySpiderData` (data_type='sports_odds') | S1501 §4 | `signal_aggregation_service._extract_signals` (line 240) with sports keywords absent | **Load-bearing gap** — signals never surface as SignalCluster. |
| `SportsGame`, `GameLineHistory` | S1501 §4 | `RealtimeIntelligenceEngine._analyze_sport_market` (dict-based, no ORM) | Read via API providers, not ORM. |
| `MLPrediction` | `sports/models.py:1750-1925` (per Explore Agent 6) | `PredictionEvaluator._evaluate_single_prediction` (line 202); `RealtimeIntelligenceEngine._generate_game_predictions`; `get_ai_track_record` REST (`views_odds_sports.py:3315-3521`) | **Decoupled from BettingOutcomeVerifier** — Finding 2. |
| `PlacedWager`, `PlacedWagerLeg` | S1503 §4 (`core/models_betting.py:13, :108`) | `BettingOutcomeVerifier._settle_wager` (line 169); Discord `/bet` + `/resolve` | Discord is a first-class write consumer. |
| `Bankroll`, `Wager` | `core/models_bankroll.py` | Discord `/bankroll`, `/bet`, `/resolve` | Discord write surface. |
| `HumanAttentionItem` | S1503 §14 | `BettingOutcomeVerifier._verify_arb_item` (line 376); frontend Watching tab (S1505 §4) | Cross-domain (Cat C + Cat E + Cat F). |
| `SportsBettingBrief` | S1504 §4 | S1504 §14.3 write-only-forgotten (upheld S1505 §14.4). | Cat F confirms REST endpoint bypass — S1504 pattern extends. |

### 4.2 Cross-domain models consumed by Cat F surfaces

| Model | Location | Sports consumer | Cat F relevance |
|---|---|---|---|
| `SignalCluster` | `core/models_signal_intelligence.py:56-…` | **Zero sports writers** (Finding 3). | Load-bearing gap. |
| `AgentMemory` | `core/models_unified_system.py:10787-10977` | `SportsBettingLearningBridge` for 2 of 4 market agents (Finding 6). | Partial coverage. |
| `AgentKnowledgeSource` | `core/models_unified_system.py:521-628` | **Zero sports writers** (Finding 6). | Load-bearing gap. |
| `UserAgentLearning` | `core/models_unified_system.py:…` (per Explore Agent 5) | `SportsBettingLearningBridge.record_wager_outcome` (line 503); `record_arbitrage_outcome` (line 579). | Real writes; sport-specific rows. |
| `Agent` (persona) | `core/models_unified_system.py:…` | `Agent.objects.filter(name='SportsOddsAnalyst')` at bridge line 527; `Agent.objects.filter(name='ArbitrageDetector')` at bridge line 602. | Persona registry — FK target only. |
| `UnifiedAgentTemplate`, `AgentTaskExecution`, `SpiderQualityMetrics`, `Advisor` | Per Explore Agent 1 | `NewPagesConsumer.get_real_nexus_status` at `core/new_pages_consumer.py:149-298` — for `/ws/ai-nexus/` only, NOT for `/ws/dbao/`. | Cross-check: AI Nexus reads real data; DBAO does not. Confirms MOCK-DATA-CONSUMER pattern uniqueness. |

### 4.3 Cat F contract statement on model ownership

- Cat F does not own any model.
- Cat F is a **cross-domain read lens** on sports-owned models (§4.1) + a **partial write lens** on cross-domain infrastructure models (§4.2 — specifically AgentMemory + UserAgentLearning via SportsBettingLearningBridge).
- Zero Cat F persistence layer new to this arc.

### 4.4 Pre-brief mini-schema per surface (D62 = (a) propagate upfront, 6-sibling exemplar pattern)

**Applied per parent §5 D62 = (a) mini-schema propagation directive (Chris-ratified S1501 open).** Sixth and final sibling application after S1501 §4.6 + S1502 §4.8 + S1503 §4.4 + S1504 §4.4 + S1505 §4.2. Cat F's mini-schema is the **integrated view** that closes the arc.

For each surface below: (a) sports-only vs shared with mainline, (b) writes to sports-owned tables (DBAO schema) or mainline (public schema), (c) integration posture would require refactor or only extend, (d) island posture would require additional isolation guarantees.

| Surface | (a) Scope | (b) Table ownership | (c) Integration refactor cost | (d) Island isolation cost |
|---|---|---|---|---|
| PostgreSQL `dbao` schema | Sports-scope (nominally) | **EMPTY** — no models declared | ZERO (nothing to refactor) | ZERO (nothing to isolate) — but the emptiness itself is a load-bearing signal for D61 |
| `/ws/dbao/` + `/ws/dbao-dashboard/` consumer | Shared with mainline dashboards | N/A (in-memory random) | HIGH — consumer scope covers multiple product-lines | HIGH — mock-data pattern is a general dashboard demo pattern, not sports-scoped |
| VITE/EXPO env-vars | Nominally sports | N/A (client) | ZERO (unused) | ZERO (unused) |
| `x-dbao-client` header | Nominally sports | N/A | ZERO (unused) | ZERO (unused) |
| `RealtimeIntelligenceEngine` — sports_intelligence_loop | Sports-native | N/A (in-memory + WS emit) | LOW — engine is already sports-native, integration would require wiring into SignalCluster + AgentMemory writes | LOW — already isolated at engine layer |
| `RealtimeIntelligenceEngine` — cross-domain demo loops | Nominally cross-domain, hardcoded demo | N/A | MED — hardcoded demo would need to be either implemented or removed | LOW — demo could be removed cleanly |
| `intelligence/views.py` REST | Domain-neutral REST | N/A (in-memory read) | LOW — REST is already domain-neutral | LOW — REST would need to be split by domain if island |
| `IntelligencePage` frontend | Domain-neutral UI | N/A | LOW — page doesn't consume sports today | LOW — no sports consumption |
| `sports_intelligence` flag | Nominally sports; gates nothing | N/A | LOW — flag layer needs to be either wired or removed | LOW — same |
| `settings.SPORTS_ANALYTICS` config block | Nominally sports; consulted nowhere | N/A | LOW — same | LOW — same |
| Discord `/odds`, `/futures`, `/slip` | Sports-only | Public schema (reads) | MED — route through coordinator | LOW — already isolated at command layer |
| Discord `/bet`, `/resolve` | Sports-only | Public schema (writes to Wager/Bankroll) | LOW — no coordinator dep | LOW |
| Discord `/arb` | Sports-only via ArbitrageDetector | Public schema | ZERO — already uses shared agent | LOW |
| Discord `/bankroll` | Sports-only | Public schema | ZERO | LOW |
| `_impl_collect_sports_odds_intelligence` (Discord digest) | Sports-only | Public schema (reads spider); Discord POST | MED — route through coordinator | LOW |
| `SignalCluster` emission for sports_odds | **Missing entirely** | Would target public schema (SignalCluster is mainline) | HIGH — needs pattern_type extension + keyword mapping + sports-data-to-signal shim | LOW — would build sports-native aggregator in dbao schema |
| `AgentMemory` writes via SportsBettingLearningBridge | Sports-scope, mainline table | Public schema (AgentMemory) | LOW — bridge exists; expand to 4/4 agents | HIGH — sports-native memory would fork mainline surface |
| `AgentKnowledgeSource` writes for sports | **Missing entirely** | Would target public schema | LOW — bridge could be extended | LOW — sports-only knowledge source could be a separate table |
| `BettingOutcomeVerifier` (settles wagers) | Sports-only | Public schema | LOW | LOW |
| `PredictionEvaluator` (evaluates MLPrediction) | Sports-only | Public schema (MLPrediction lives in sports app per Explore) | LOW | LOW |
| BettingOutcomeVerifier ↔ MLPrediction linkage | **Missing entirely** | Would touch public schema | LOW — needs FK or join method + wager→prediction linkage code | LOW — could stay decoupled if sports-native retrain loop is independent |
| `Wager` / `Bankroll` models | Sports-only | Public schema (`core.models_bankroll`) | LOW | LOW |
| Discord bot Cog (`InteractiveCommands`) | Shared class hosting sports commands | N/A | LOW | LOW |
| `DBAODashboardView` (deprecated TemplateView) | Nominally sports; deprecated | N/A | ZERO (unused) | ZERO (unused) |

**Cross-sibling observation (sixth-sibling closing pattern).** Cat F's mini-schema is the **first to surface (b) "would target public schema" for missing surfaces** — the SignalCluster emission gap and AgentKnowledgeSource gap both point at mainline tables. S1501–S1505 sibling schemas identified real surfaces + their scope; Cat F's schema identifies **missing surfaces** and where they would land. This is the load-bearing information for xx99 §5 posture-decision brief — it makes the "integration would require adding a public-schema write" cost concrete.

**Cross-sibling observation (isolation-cost distribution).** Aggregating (d) across P1–P6:
- **HIGH island cost** at 5 surfaces: `humanApi` (S1505 §4.2), `ProtectedRoute` (S1505 §4.2), `/ws/dbao/` consumer (S1505 §4.2 + Cat F §4.4), sports-native memory-domain fork (Cat F §4.4), mock-data pattern refactor (Cat F §4.4).
- **HIGH integration cost** at 2 surfaces: `SignalCluster` sports_odds emission (Cat F §4.4), `/ws/dbao/` consumer (would need multi-product-line refactor either way).
- **LOW integration cost** at ~15 surfaces: most sports-native surfaces are cheap to wire in.
- **LOW island cost** at ~15 surfaces: most sports-native surfaces are cheap to isolate.

The **cost asymmetry is not in the sports surface itself; it is in the two shared-with-mainline surfaces that either posture would collide with**. This is a load-bearing observation for xx99 posture brief.

---

## 5. Major Services

**Q5 — What are the major services?**

### 5.1 Cross-domain services touching sports

| Service | File:line | Sports touch-point | Cross-domain role |
|---|---|---|---|
| `RealtimeIntelligenceEngine` | `intelligence/realtime_engine.py:65-687` | `_sports_intelligence_loop` (lines 123-138) — arbitrage + value-bet + line-movement detection. | Sports-native at engine, nominally cross-domain at loop-catalog. |
| `SportsBettingLearningBridge` | `core/learning_bridges/sports_betting_bridge.py:1-…` | `record_wager_outcome` (line 532 AgentMemory write) + `record_arbitrage_outcome` (line 606) + `sync_betting_performance_to_learning` (per Explore Agent 5) + `create_feedback_from_prediction` (line 379-423). | Sports → Memory-Domain (AgentMemory + UserAgentLearning) bridge. |
| `BettingOutcomeVerifier` | `core/services/betting_outcome_verifier.py:30-481` | Wager settlement + arb verification + `_create_learning_records` (line 455). | Sports-scope; no cross-domain writes beyond bridge invocation. |
| `PredictionEvaluator` | `sports/prediction_evaluator.py:40-420` per Explore Agent 6 | `_evaluate_single_prediction` (line 202) sets `MLPrediction.was_correct`. | Sports-scope; feeds SportsBettingLearningBridge (line 421-488). |
| `SportsBettingCoordinator` | `core/services/sports_betting_coordinator.py:21-96` | Aggregates agent outputs into brief. | Sports-scope; bypassed by Discord (Finding 5) + `_impl_collect_sports_odds_intelligence` (Finding 12). |
| `DiscordNotificationService` | `core/services/discord_notifications.py:2053` (`send_betting_digest`) | Posts betting digest to Discord `CHANNEL_BOARDROOM` (hardcoded at line 40). | Cross-domain (Discord + sports content). Docstring drift (Finding 8). |
| `SignalAggregationService` | `core/services/signal_aggregation_service.py:1-…` | Consumes `LegacySpiderData` universally; sports_odds data would fail keyword/topic extraction (Finding 3). | Zero sports writes. |
| `SignalCuratorService` | `core/services/signal_curator_service.py:45-49` | Consumes all pattern_types uniformly; would consume sports_odds if the pattern_type existed. | Latent consumer — sports side of the equation is missing. |

### 5.2 Services referenced but structurally decoupled

- `RealtimeIntelligenceEngine` cross-domain loops (opportunity_detection / prediction_generation / cross_domain_analysis) — hardcoded demo per Explore Agent 2. Named as cross-domain but implemented as demo constants. Finding 9.

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs and interfaces?**

### 6.1 REST endpoints (cross-domain integration lens)

| Endpoint | View | File:line | Sports touch |
|---|---|---|---|
| `GET /api/intelligence/skynet/status/` | `SkynetStatusView.get` | `intelligence/views.py:24` | Returns `sports_intelligence: True` (hardcoded literal, Finding 4). |
| `GET /api/intelligence/opportunities/` | `LiveOpportunitiesView.get` | `intelligence/views.py:60` | Reads `intelligence_engine.get_current_opportunities()` — sports opportunities if engine running. |
| `GET /api/intelligence/predictions/` | `LivePredictionsView.get` | `intelligence/views.py:74`-ish | Reads `intelligence_engine.get_current_predictions()`. |
| `GET /api/v1/betting/track-record/` | `get_ai_track_record` | `core/views_odds_sports.py:3315-3521` | Reads `MLPrediction` deduped by game; computes ROI/CLV. Does NOT join to `PlacedWager` settlement — evidence of decoupled verification (Finding 2). |
| `GET /api/v1/betting/brief/` | `get_betting_brief` | `core/views_odds_sports.py:3237-3265` | Calls `SportsBettingCoordinator.generate_brief()` on-the-fly; NEVER READS persisted `SportsBettingBrief` (S1504 §14.3 + S1505 §14.4 upheld). |
| `GET /api/v1/sports/live-opportunities/` | `live_betting_opportunities` | `core/views_odds_sports.py:579-580` | `IsAuthenticated` (S1505 §14.3 AUTH-DRIFT context). |
| `GET /api/v1/sports/betting-intelligence/` | `get_betting_intelligence` | `core/views_odds_sports.py:2055-2056` | `IsAuthenticated` (S1505 §14.3 AUTH-DRIFT). |

### 6.2 WebSocket endpoints

| WS route | Consumer | File:line | Cat F relevance |
|---|---|---|---|
| `/ws/dbao/` | `NewPagesConsumer` | `core/routing.py:369` | MOCK-DATA-CONSUMER (Finding 1). |
| `/ws/dbao-dashboard/` | `NewPagesConsumer` | `core/routing.py:370` | Sibling of `/ws/dbao/`; same behavior (Finding 7). |
| `/ws/ai-nexus/` | `NewPagesConsumer` | `core/routing.py:366` | Reads real data via `get_real_nexus_status`. Cross-check: same class, real data. Confirms MOCK is DBAO-specific, not consumer-wide. |
| `/ws/sports/`, `/ws/sports/odds/`, `/ws/sports/games/` | Per S1505 §14.5 | `sports/routing.py:7-11` | Registered but not consumed by BettingPage (S1505). Cat F confirms zero consumer at frontend layer. |
| `command_center`, `opportunity_scanner` (channel groups) | `RealtimeIntelligenceEngine._stream_opportunity` line 607-638, `_stream_prediction` line 640-662 | `intelligence/realtime_engine.py:` | Real emit — but only if engine is manually started (Finding 10). |

### 6.3 Discord slash commands (7)

Per §3.3 table above. Cat F relevance:
- **HOT-PATH-CHOKE bypass at 3 read commands** (`/odds`, `/futures`, `/slip`).
- **Shared-agent path at 1 read command** (`/arb`).
- **Direct-write path at 2 write commands** (`/bet`, `/resolve`) — no coordinator/verifier gate.
- **Bankroll-scope-only at 1 read command** (`/bankroll`).
- **Zero feature-flag gating** across all 7.

### 6.4 Celery task interfaces

| Task | File:line | Cadence | Cat F relevance |
|---|---|---|---|
| `collect_sports_odds_intelligence` | `core/tasks.py:6098-6100` → `core/tasks_financial.py:1815-1902` | Every 30 min (`core/celery.py:787`) | Bypasses coordinator + engine (Finding 12). |
| `daily_betting_digest` | S1504 §14.1 | **Zero-fire status** — S1504 flag still open (00-START-NEXT-SESSION.md L201). | Post-arc T-slot follow-on. |
| `generate_daily_betting_brief` | S1504 §4 | Daily 7:00 AM MT | Writes `SportsBettingBrief` (not consumed). |
| `verify_betting_outcomes` | `core/tasks.py:6121-6140` | Every 2 hours | Triggers `BettingOutcomeVerifier`. Real. |
| `learning_loop.track_prediction_outcomes` | `core/tasks.py:4631` | Per Explore Agent 5 | Wraps prediction-outcome tracking. |
| `learning_loop.calculate_agent_accuracy` | `core/tasks.py:4635` | Per Explore Agent 5 | Wraps accuracy calc. |
| Zero beat entry for `RealtimeIntelligenceEngine` | — | **Latent-zero-fire** (Finding 10) | Manual start only. |

---

## 7. Runtime Flows

**Q7 — What are the runtime flows?**

### 7.1 Discord `/odds` command flow (BYPASS pattern — F1 fold candidate per S1504 precedent)

```
User in Discord chat
    ↓ types "/odds sport:NFL show:tossups limit:5"
Discord API → discord_bot.py InteractiveCommands._on_command_dispatch
    ↓ dispatches to `/odds` handler at discord_bot.py:1108
Handler at discord_bot.py:1121 constructs get_odds_data() nested sync_to_async
    ↓ instantiates TheOddsSpider() (bypass — no coordinator)
TheOddsSpider.fetch_data(max_results=100)
    ↓ hits external The Odds API
API response → dict → inline 7-sport emoji map + filter logic + embed rebuild
    ↓ (no coordinator call, no MLPrediction read, no cache)
Discord embed constructed inline
    ↓ discord.py sends embed to Discord channel
User sees rendered odds
```

**Verified-in-repo anchors per Explore Agent 3:**
- Handler entry: `core/services/discord_bot.py:1108`
- Docstring: `core/services/discord_bot.py:1121` ("Display sports betting odds from The Odds API")
- Zero SportsBettingCoordinator reference in handler body (grep-verified).

Contrast with REST `/api/v1/betting/brief` flow: `views_odds_sports.py:3248` calls `SportsBettingCoordinator(sport_key).generate_brief()` — a heavy pipeline that orchestrates agents + caching + model reads.

**HOT-PATH-CHOKE analog to S1504 §14 pattern (that flagged REST-bypasses-coordinator via `_impl_daily_betting_digest`)**: Cat F extends the pattern from REST layer to Discord layer.

### 7.2 Discord `/bet` command flow (WRITE)

```
User in Discord chat
    ↓ types "/bet selection:Chiefs sport:NFL odds:-150 stake:10"
Discord API → InteractiveCommands._on_command_dispatch
    ↓ dispatches to `/bet` handler at discord_bot.py:1530
Handler at discord_bot.py:1571 calls Wager.objects.create(
    bankroll=<user's bankroll>, selection=..., odds_american=-150, stake=10, ...
)
    ↓ Django ORM INSERT
Wager row persisted in public schema
    ↓ handler returns confirmation embed
User sees "Bet logged" confirmation
```

**No SportsBettingCoordinator gate. No verification, no odds cross-check.** Wager persisted directly.

### 7.3 `verify_betting_outcomes` Celery beat → wager settlement + learning loop

```
Celery beat (every 2h)
    ↓ triggers verify_betting_outcomes (core/tasks.py:6121)
verify_betting_outcomes() at core/tasks.py:6132
    ↓ calls BettingOutcomeVerifier().verify_all_pending()
BettingOutcomeVerifier.verify_all_pending() at core/services/betting_outcome_verifier.py:30
    ↓ fetches pending PlacedWagerLeg (line 54) + watching HumanAttentionItem (line 60)
    ↓ batch-fetches scores via TheOddsSpider (line 82)
For each settled wager:
    _settle_wager (line 169) — sets leg.status, leg.profit, wager.status
    ↓
For each verified arb:
    _verify_arb_item (line 376) — marks HumanAttentionItem verified
    ↓
_create_learning_records (line 455-480)
    ↓ imports SportsBettingLearningBridge (line 461)
    ↓ bridge.record_wager_outcome(wager) → AgentMemory + UserAgentLearning writes
    ↓ bridge.record_arbitrage_outcome(item) → AgentMemory + UserAgentLearning writes
Learning records persisted; no MLPrediction touched; no SignalCluster emitted
```

**Load-bearing observation:** Two verification systems (BettingOutcomeVerifier + PredictionEvaluator) run in parallel with **zero cross-reference** to each other. When a wager settles, the underlying `MLPrediction` (if any) is never notified. When a `MLPrediction.evaluate()` fires, the placed wagers matching that game are never notified. See §14.2.

### 7.4 `/ws/dbao/` mock-broadcast flow (MOCK-DATA-CONSUMER extended from S1505 §14.1)

```
Client connects to ws://<host>/ws/dbao/ (or /ws/dbao-dashboard/)
    ↓ core/routing.py:369 (or :370) dispatches to NewPagesConsumer.as_asgi()
NewPagesConsumer.connect at core/new_pages_consumer.py:32-39
    ↓ path detection sets self.page_type = 'dbao'
Consumer.send_dbao_updates loop starts at core/new_pages_consumer.py:450-478
    ↓ every 10s:
        - send mock query object (random_id, execution_time, status)
        - 40% chance to send metrics via send_dbao_metrics (line 471)
send_dbao_metrics at core/new_pages_consumer.py:310-331
    ↓ populates payload with random.randint / random.uniform for every field:
        data_points, active_queries, uptime, data_processed, avg_response,
        accuracy_rate, performance.{cpu,memory,disk,network}
    ↓ WS emit — client receives random numbers
Client also can send messages:
    'get_metrics' → send_dbao_metrics (same mock path)
    'get_queries' → send_query_status (UNDEFINED — AttributeError at runtime)
    'run_analytics' → handle_run_analytics (UNDEFINED — AttributeError at runtime)
```

**Cross-check with `/ws/ai-nexus/` (same class, different `page_type`):**

```
Client → /ws/ai-nexus/ → NewPagesConsumer with page_type='ai_nexus'
    ↓ get_real_nexus_status at core/new_pages_consumer.py:149-298
    ↓ @database_sync_to_async wrapper (line 148)
    ↓ queries UnifiedAgentTemplate, AgentTaskExecution, SpiderQualityMetrics, Advisor
    ↓ real aggregations, real counts
Client receives real telemetry
```

**Contrast confirms:** MOCK is DBAO-scoped, not consumer-wide. The same class supports both real and mock modes; DBAO branch is uniquely mock.

### 7.5 `RealtimeIntelligenceEngine` sports flow (if engine started)

```
Manual invocation of start_skynet() (intelligence/realtime_engine.py:693)
    ↓ starts engine + spawns loops
_sports_intelligence_loop (line 123-138) runs continuously
    ↓ for each configured sport:
        _analyze_sport_market(sport) at line 140-162
            ↓ TheOddsAPIProvider + ESPNProvider fetch (dict-based, no ORM)
        _detect_game_opportunities(game, sport) at line 164-189
            ↓ _detect_arbitrage(game) (191-258)
            ↓ _detect_value_bets(game) (260-331)
            ↓ _detect_line_movements(game) (333-372)
            ↓ _generate_game_predictions(game, sport, scoreboard) (374-437)
    ↓ for each opportunity/prediction, emit to WS:
        _stream_opportunity (607-638) → command_center + opportunity_scanner groups
        _stream_prediction (640-662) → command_center group
    ↓ retained in in-memory store
    ↓ get_current_opportunities (664-674) reads store
    ↓ get_current_predictions (676-686) reads store
    ↓ intelligence/views.py:60 LiveOpportunitiesView reads at REST-request time
```

**Load-bearing gap:** If `start_skynet()` is never called (no beat entry, no auto-start), the engine never runs. `SkynetStatusView` will still return `sports_intelligence: True` — misleading. See Finding 10.

### 7.6 `_impl_collect_sports_odds_intelligence` Discord digest flow (DUAL-COORDINATOR-BYPASS)

```
Celery beat (every 30 min, core/celery.py:787-791)
    ↓ triggers core.tasks.collect_sports_odds_intelligence
core/tasks.py:6099-6100 wrapper
    ↓ calls _impl_collect_sports_odds_intelligence at core/tasks_financial.py:1815
    ↓ instantiates TheOddsSpider() (bypass coordinator)
    ↓ (bypass RealtimeIntelligenceEngine — no engine call)
    ↓ spider.get_upcoming_events(hours=24)
    ↓ groups by sport, builds by_sport dict
    ↓ filters toss-ups (45-55% implied probability)
DiscordNotificationService().send_betting_digest(...)
    ↓ core/services/discord_notifications.py:2053
    ↓ posts to CHANNEL_BOARDROOM (hardcoded, discord_notifications.py:40)
Docstring at core/tasks_financial.py:1815 says "#market-intelligence"
    ↓ RUNTIME goes to CHANNEL_BOARDROOM
    ↓ Silent drift (Finding 8)
```

---

## 8. Data Ownership and Lifecycle

**Q8 — What is the data ownership and lifecycle?**

### 8.1 Cat F data-ownership map (cross-domain reads/writes)

| Data class | Owner (domain) | Writer surfaces | Reader surfaces | Cat F implication |
|---|---|---|---|---|
| Sports odds (raw) | Cat A ingestion | 5 spiders + TheOddsSpider | RealtimeIntelligenceEngine + coordinator + Discord commands + REST live-odds | Multiple readers bypass coordinator (Findings 5, 12). |
| `MLPrediction` | Sports (`sports/models.py:1750-1925`) | `GamePredictor._store_predictions` (`core/agents/markets/game_predictor.py:505`) + `save_ml_prediction` (`sports/prediction_tracker.py:55`) | REST `get_ai_track_record` + `PredictionEvaluator._evaluate_single_prediction` | Decoupled from BettingOutcomeVerifier (Finding 2). |
| `PlacedWager`, `PlacedWagerLeg` | Cat C (S1503) | REST wager POST + Discord `/bet` + Discord `/resolve` | BettingOutcomeVerifier + frontend Wagers tab (S1505) | Discord is a first-class write consumer. |
| `Wager`, `Bankroll` (`core/models_bankroll.py`) | Cat C-adjacent | Discord `/bet`, `/resolve`; UI wager flow | Discord `/bankroll` + UI wagers tab | Discord write surface (Finding: no gate). |
| `SportsBettingBrief` | Cat D (S1504) | `generate_daily_betting_brief` task + `tasks_content.py:3150` + `tasks.py:12187` | **Zero readers** (S1504 §14.3 + S1505 §14.4 + Cat F affirms) | Continuing write-only-forgotten. |
| `SignalCluster` | Signal Engine (mainline) | `signal_aggregation_service._create_signal_clusters` (line 723) | Signal-studio + `SignalCuratorService` + `td_handlers_content` | **Zero sports writers** (Finding 3). |
| `AgentMemory` | Memory Domain (mainline) | Many writers; sports writers: SportsBettingLearningBridge (lines 532, 606) | Many readers | Partial sports coverage (Finding 6). |
| `AgentKnowledgeSource` | Memory Domain (mainline) | Many writers; **zero sports writers** | Many readers | Load-bearing gap (Finding 6). |
| `UserAgentLearning` | Memory-adjacent | SportsBettingLearningBridge (lines 503, 579) | `sync_betting_performance_to_learning` reader | Sports write surface — real. |
| DBAO WebSocket payload | None (nominal DBAO) | `NewPagesConsumer.send_dbao_metrics` — synthesized in-memory | Whoever subscribes to `/ws/dbao/` or `/ws/dbao-dashboard/` | 100% mock (Finding 1). |
| Discord digest payload | None (transient) | `_impl_collect_sports_odds_intelligence` | Discord CHANNEL_BOARDROOM | Docstring drift (Finding 8). |
| `RealtimeIntelligenceEngine` in-memory opportunity/prediction store | Engine (transient) | Sports intelligence loop | REST + WebSocket group emit | Engine must be manually started (Finding 10). |

### 8.2 Lifecycle summary

- **Cat F does not own any data lifecycle** — it observes cross-domain lifecycles.
- The **Sports Domain Lifecycle Traceability Table** owed to xx99 §12.5 is fed by Cat F evidence + P1–P5 evidence; xx99 assembles.

---

## 9. Integrations With Other Domains

**Q9 — What are the integrations with other domains?** This is the **load-bearing section** for Cat F.

### 9.1 Sports ↔ Signal Engine

| Item | State | File:line | Cat F verdict |
|---|---|---|---|
| `SignalCluster` valid `pattern_type` for sports | **MISSING** | `core/models_signal_intelligence.py:75-86` | 10 valid types; `sports_odds` absent. Verified. |
| Sports-data-to-signal shim | **MISSING** | Grep zero hits | No bridging code found. |
| Sports-native aggregator | **MISSING** | No file exists | No `SportsSignalAggregator` etc. |
| SignalAggregationService keyword coverage for sports | **HARDCODED NON-SPORTS** | `core/services/signal_aggregation_service.py:139-168, 171-182` | Sports data would fail extraction. |
| Any consumer path from sports events to Signal Engine | **ZERO** | — | 6-arc consumer-side pattern; complete gap. |

**Consequence:** Sports events (line movements, sharp action, arbitrage windows, bookmaker consensus, agent outputs) never surface as signals. Load-bearing for xx99 §5 posture brief.

### 9.2 Sports ↔ Memory Domain (S1300 canonical summary)

| Item | State | File:line | Cat F verdict |
|---|---|---|---|
| `SportsBettingLearningBridge.record_wager_outcome` | **REAL — 2/4 market agents** | `core/learning_bridges/sports_betting_bridge.py:532` | Writes AgentMemory for SportsOddsAnalyst only. |
| `SportsBettingLearningBridge.record_arbitrage_outcome` | **REAL — extends coverage** | `core/learning_bridges/sports_betting_bridge.py:606` | Writes AgentMemory for ArbitrageDetector only. |
| `SportsBettingLearningBridge.create_feedback_from_prediction` | **REAL — feedback wrapper** | `core/learning_bridges/sports_betting_bridge.py:379-423` per Explore Agent 6 | Wraps MLPrediction as FeedbackItem for learning consumer. |
| `SportsBettingLearningBridge.sync_betting_performance_to_learning` | **REAL — bankroll sync** | `core/learning_bridges/sports_betting_bridge.py:97-205` per Explore Agent 5 | Syncs bankroll+accuracy to UserAgentLearning. |
| GamePredictor → AgentMemory | **MISSING** | Grep zero hits | Agent inherits BaseAgent but does not invoke `_record_learning_outcome`. |
| SharpActionDetector → AgentMemory | **MISSING** | Grep zero hits | Same. |
| Any sports agent → AgentKnowledgeSource | **MISSING** | Grep zero hits | Zero sports writers. |
| BettingOutcomeVerifier → BridgeCalls | **REAL** | `core/services/betting_outcome_verifier.py:455-480` | Bridge invocation confirmed. |
| PredictionEvaluator → SportsBettingLearningBridge | **REAL — but no retrain consumer** | `sports/prediction_evaluator.py:421-488` per Explore Agent 6 | Feeds bridge; no downstream retrain job. |

**Consequence:** Memory bridge is real but partial (2/4 agent coverage; AgentMemory-only, no AgentKnowledgeSource); feedback lands in learning domain but does not trigger sports model retraining. Load-bearing for xx99 §5 posture brief; delegation to S1300 candidate.

### 9.3 Sports ↔ Intelligence surface

| Item | State | File:line | Cat F verdict |
|---|---|---|---|
| `RealtimeIntelligenceEngine._sports_intelligence_loop` | **REAL** | `intelligence/realtime_engine.py:123-138` | Sports-native at engine layer. |
| `RealtimeIntelligenceEngine` beat entry | **MISSING** | Zero beat entry | Manual start only (Finding 10). |
| `SkynetStatusView.sports_intelligence` flag | **HARDCODED TRUE** | `intelligence/views.py:44` | Reports capability; consulted nowhere. |
| Duplicate flag | `core/intelligence_api.py:94` | Same hardcoded status. |
| `IntelligencePage` frontend consumes sports | **NO** | `frontend/src/pages/IntelligencePage.tsx` | Zero sports API imports. |
| `LiveOpportunitiesView` / `LivePredictionsView` REST | **REAL — but conditional on engine running** | `intelligence/views.py:60, 74` | Read engine's in-memory store. |
| `_impl_collect_sports_odds_intelligence` Celery digest | **REAL — but bypasses engine + coordinator** | `core/tasks_financial.py:1815-1902` | Finding 12 dual-coordinator-bypass. |

**Consequence:** Intelligence surface is sports-native at engine layer, domain-neutral at REST/UI layer, gates-nothing at flag layer. `sports_intelligence` flag reported to frontend does not reflect any consumable reality. Load-bearing for the P6 parked question (Rigby SIGN cycle 1 Q4 fold from parent scoping §6) about topic-doc documentation.

### 9.4 Sports ↔ Discord

| Item | State | File:line | Cat F verdict |
|---|---|---|---|
| 7 sports slash commands (`/odds`, `/arb`, `/bet`, `/resolve`, `/futures`, `/slip`, `/bankroll`) | **REAL** | `core/services/discord_bot.py:1108-1961` | First-class read+write consumer. |
| `_impl_collect_sports_odds_intelligence` Discord digest task | **REAL** | `core/tasks_financial.py:1815-1902` | Every 30 min. |
| Discord write surface (`/bet`, `/resolve`) | **REAL — no coordinator gate** | `discord_bot.py:1571, 1687, 1705` | Direct-to-model. |
| Discord read surface bypassing coordinator | **REAL — 3 commands** | `discord_bot.py:1108, 1744, 1851` | HOT-PATH-CHOKE extension (Finding 5). |
| Discord `/arb` uses shared ArbitrageDetector | **REAL** | `discord_bot.py:1260` | Shared agent path; no bypass at logic layer. |
| Discord → SignalCluster emission | **MISSING** | Grep zero hits | Zero emit. |
| Discord → AgentMemory emission | **MISSING** | Grep zero hits | Zero emit from Cog. |
| Feature-flag gating | **MISSING** | Grep zero hits | Ungated. |
| Docstring↔channel drift | **DRIFTED** | `core/tasks_financial.py:1815` docstring vs `discord_notifications.py:40` runtime | Finding 8. |

**Consequence:** Discord is a **first-class write consumer** running in parallel with REST + frontend, but structurally decoupled from the sports coordinator and from cross-domain (Signal / Memory) infrastructure. Load-bearing for xx99 §5 posture brief operational-cost estimate.

### 9.5 Sports ↔ DBAO product-line

| Item | State | File:line | Cat F verdict |
|---|---|---|---|
| PostgreSQL `dbao` schema | **DECLARED — EMPTY** | `core/settings.py:340` | Zero Django models targeting; zero migrations create it. |
| `/ws/dbao/` + `/ws/dbao-dashboard/` consumer | **REAL — MOCK BROADCASTER** | `core/routing.py:369-370` | 100% random data (Finding 1 + Finding 7). |
| `send_query_status` handler | **UNDEFINED — REFERENCED** | `core/new_pages_consumer.py:123` | AttributeError at runtime. |
| `handle_run_analytics` handler | **UNDEFINED — REFERENCED** | `core/new_pages_consumer.py:125` | AttributeError at runtime. |
| VITE/EXPO DBAO env-vars | **DECLARED — UNCONSUMED** | `.env.example:72-86` | Grep zero frontend hits. |
| `x-dbao-client` CORS header | **WHITELISTED — UNUSED** | `core/settings.py:707` | Never sent, never read. |
| `DBAODashboardView` template | **DEPRECATED — UNROUTED** | `core/views_unified.py:210-218` | Module marked deprecated. |
| Header comments referencing "DBAO tools-manifest" | **DOC-ONLY** | `core/routing.py:3`, `core/urls.py:3061,3079`, `core/views_odds_sports.py:2` | Historical migration marker. |

**Consequence:** DBAO is a **naming-convention-without-materialization** codename. Six artifacts declared; zero runtime state. Load-bearing for D61 (parent scoping parked-candidate) posture-decision T-slot.

### 9.6 Sports ↔ Body Systems (parent §3 non-candidate confirmation)

Per parent §3 explicit non-candidate: "Body-system integration. Explore sweep confirms zero sports references in heart.py / lungs.py / circulatory.py."

Cat F verifier-loop confirms no drift from this at the code layer (verifiable but not re-executed this session; inheriting parent §3 finding). If future work surfaces a body-system tie, it is post-arc flag per parent §3.

### 9.7 Sports ↔ Mobile app (parent §3 non-candidate)

Per parent §3 explicit non-candidate: "Mobile-app / React-Native betting-app scope beyond FK boundaries." Cat E surfaced `EXPO_PUBLIC_DBAO_API_URL` + `EXPO_PUBLIC_DBAO_WS_URL` env-vars in `.env.example:85-86` — nominally mobile-DBAO namespace; unconsumed by any code. Extends Finding 1 mobile-adjacent naming footprint. Cat F FLAGS but does not deep-audit (parent §3 non-candidate).

---

## 10. Event Flows

**Q10 — What are the event flows?**

### 10.1 Sports events emitted to platform infrastructure

| Event class | Emitter | Target | State |
|---|---|---|---|
| WebSocket `command_center` group | `RealtimeIntelligenceEngine._stream_opportunity` (`intelligence/realtime_engine.py:607-638`) | Command Center dashboard channel | Real IF engine started. |
| WebSocket `command_center` group | `RealtimeIntelligenceEngine._stream_prediction` (`intelligence/realtime_engine.py:640-662`) | Same | Real IF engine started. |
| WebSocket `opportunity_scanner` group | `RealtimeIntelligenceEngine._stream_opportunity` | Opportunity scanner UI | Real IF engine started. |
| WebSocket `/ws/dbao/` payload | `NewPagesConsumer.send_dbao_metrics` (`core/new_pages_consumer.py:310-331`) | Any subscriber | 100% MOCK. |
| WebSocket `/ws/dbao-dashboard/` payload | Same | Any subscriber | 100% MOCK. |
| WebSocket `/ws/sports/`, `/ws/sports/odds/`, `/ws/sports/games/` (per S1505 §14.5) | Registered consumers | None (BettingPage zero subscription) | Registered, unused. |
| Discord digest event | `_impl_collect_sports_odds_intelligence` → `DiscordNotificationService.send_betting_digest` | `CHANNEL_BOARDROOM` | Real; docstring drift Finding 8. |
| Django signal / observer for wager settlement | None found (grep) | — | Absent — BettingOutcomeVerifier writes directly. |
| SignalCluster emit | **MISSING** | Signal Engine consumers | Zero sports emission (Finding 3). |
| AgentMemory emit | Partial via SportsBettingLearningBridge | Memory-domain consumers | 2/4 agent coverage. |
| MLPrediction outcome-derived event | **MISSING** | Anywhere | `MLPrediction.evaluate()` sets `was_correct` + `evaluated_at`; no downstream trigger. |

### 10.2 Cross-domain event decoupling

- **`BettingOutcomeVerifier` outcome events do not emit to `MLPrediction`** (Finding 2).
- **`PredictionEvaluator` events do not emit to `BettingOutcomeVerifier` or wager settlement pipeline**.
- **Neither system emits to `SignalCluster` or `AgentKnowledgeSource`**.
- Only `AgentMemory` + `UserAgentLearning` receive real writes from the sports learning bridge.

---

## 11. Existing Documentation

**Q11 — What documentation already exists?**

### 11.1 Cross-domain / integration documentation surfaces

| Doc | Location | Cat F coverage |
|---|---|---|
| `docs/PLATFORM_WHAT_IT_IS.md` | Narrative anchor | Names Sports subsystem in overview but not the Cat F cross-domain lens. |
| `docs/PLATFORM_INVENTORY.md` §3.10 | Runtime anchor | Notes sports intelligence LIGHT rating; does not enumerate cross-domain surfaces. |
| `docs/topics/sports-betting.md` | **DOES NOT EXIST** — S1500 parent §11.2 baseline; Cat F confirms no landing. | Follow-on owed to xx99 §7. |
| `docs/topics/signal-engine.md` | If exists | Would not name sports gap (Signal Engine is domain-agnostic). |
| `docs/topics/personal-assistant.md` | Exists | Not sports-scoped. |
| S1274 §14 Finding #6 | Prior research | Signal Engine `sports_odds` gap; extended by 5 prior arcs + this session. |
| S1274 §12.3 | Prior research | Product/Architecture Decision Point (P1) — 2-posture success criteria; feeds Cat F evidence plan. |
| S1273 §9 #4 | Prior research | Sports/DBAO ↔ AI Studio Integration Sketch. |
| S1300 canonical summary (`docs/research/domains/memory/1399_memory_canonical_summary.md`) | Prior xx99 | Memory arc; Cat F delegates any sports→Memory bridge design here. |
| S1500 parent scoping (`docs/research/domains/sports/1500_sports_domain_scoping.md`) | Parent | Load-bearing; §3.F scope, §5 sequence, §12 F.iii criteria. |
| Sibling audits S1501–S1505 | Prior sessions | All feed Cat F. |

### 11.2 Documentation gaps confirmed by this session

- No topic doc for sports betting (Finding 14).
- No documentation of `sports_intelligence` flag semantics anywhere in `docs/` (P6 parked candidate).
- No documentation of DBAO codename intent or D61 target shape.
- No documentation of the Signal Engine `sports_odds` gap outside research handoffs (S1274 §14).
- No CODEOWNERS coverage of any Cat F runtime file (Finding 13).

---

## 12. Research Coverage

**Q12 — What prior research covers this domain?**

- **S1273** §3.10 (Sports Intelligence / Betting Pipeline LIGHT) — inherited baseline.
- **S1273** §9 #4 (Sports/DBAO ↔ AI Studio Integration Sketch) — Cat F is the successor.
- **S1274** §3.10 + §12.3 + §14 Finding #6 — HIGH classification; Cat F consumes all three.
- **S1300 Group** (Memory arc canonical summary at `docs/research/domains/memory/1399_memory_canonical_summary.md`) — delegation candidate for sports→Memory bridge design.
- **S1400 Group** (Revenue arc canonical summary at `docs/research/domains/revenue/1499_revenue_canonical_summary.md`) — playbook precedent.
- **S1500 parent scoping** (Group 1500 open) — §3.F scope, §5 sequence, §12 F.iii criteria, D57/D59/D60/D61/D62.
- **S1501 Cat A** — ingestion. Cat F consumes odds surface findings.
- **S1502 Cat B** — agents. Cat F consumes agent output patterns (direct-to-coordinator, no shared write).
- **S1503 Cat C** — wagers + outcomes. Cat F consumes BettingOutcomeVerifier structure.
- **S1504 Cat D** — content. Cat F consumes HOT-PATH-CHOKE pattern for Discord extension.
- **S1505 Cat E** — frontend. Cat F consumes MOCK-DATA-CONSUMER + AUTH-DRIFT + DEAD-RENDER-PATH context + non-guarantee table.

---

## 13. Architecture Maturity

**Q13 — What is the architecture maturity?**

Maturity framework per playbook §13: WORKING / PARTIAL / STAGED / MOCK / MISSING / POSTURE-DECISION-CANDIDATE / MOCK-DATA-CONSUMER / DEAD-RENDER-PATH / AUTH-DRIFT.

Cat F introduces **three new maturity classifiers** this session:

- **NAMING-CONVENTION-WITHOUT-MATERIALIZATION** — declared naming artifacts across schema/WS/env-var/header without any runtime state carried (Finding 1; §14.1).
- **DECOUPLED-VERIFICATION-SYSTEMS** — two verification pipelines for related data (wager outcome vs prediction outcome) that operate independently with no cross-reference (Finding 2; §14.2).
- **DECLARED-FEATURE-FLAG-GATES-NOTHING** — hardcoded feature-flag literal reported as capability but consulted nowhere in runtime paths (Finding 4; §14.4).

**Cat F axis-by-axis maturity verdict:**

| Axis | Verdict | Basis |
|---|---|---|
| DBAO product-line materialization | NAMING-CONVENTION-WITHOUT-MATERIALIZATION | Finding 1 |
| Intelligence engine (sports loops) | WORKING when started + LATENT-ZERO-FIRE by default (no beat entry) | Findings 9, 10 |
| Intelligence REST + frontend | DOMAIN-NEUTRAL — sports-tangential | Finding 11 |
| Intelligence `sports_intelligence` flag | DECLARED-FEATURE-FLAG-GATES-NOTHING | Finding 4 |
| Discord read commands | HOT-PATH-CHOKE-BYPASS at 3 of 4 read paths | Finding 5 |
| Discord write commands | WORKING — direct-to-model, no gate | §7.2 |
| Discord periodic digest | DUAL-COORDINATOR-BYPASS + DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT | Findings 8, 12 |
| Sports ↔ SignalCluster | MISSING | Finding 3 |
| Sports ↔ AgentMemory (bridge) | PARTIAL — 2/4 agent coverage | Finding 6 |
| Sports ↔ AgentKnowledgeSource | MISSING | Finding 6 |
| MLPrediction ↔ BettingOutcomeVerifier | DECOUPLED-VERIFICATION-SYSTEMS | Finding 2 |
| CODEOWNERS | MISSING (compound) | Finding 13 |
| `docs/topics/sports-betting.md` | MISSING | Finding 14 |

**Compound maturity verdict:** PARTIAL (mixed; multi-axis) — sixth distinguishing maturity shape after S1501 fragile-contract at ingestion + S1502 armed-but-under-instrumented + S1503 armed-but-zero-fire + S1504 mixed-brief-generation-persistence-forgotten-HOT-PATH-CHOKE + S1505 mixed-WORKING-DEAD-RENDER-MOCK-AUTH-NO-REALTIME.

**Load-bearing observation:** Cat F is the first sibling to require **three new maturity classifiers** in a single audit. Prior siblings introduced 1-2 new classes. The compound-multi-axis shape of Cat F is expected — it is the cross-domain lens; every prior sibling collapses into it. xx99 (S1599) will consolidate; Cat F does not merge these into a single verdict.

---

## 14. Known Drift

**Q14 — What is the known drift?**

Drift matrix: source-of-truth (or expected behavior) vs actual (as of 2026-07-02).

### 14.1 DBAO NAMING-CONVENTION-WITHOUT-MATERIALIZATION

- **Source-of-truth (D57/D61 parent scoping):** DBAO is a materialization surface for the Sports/Intelligence product-line — schema, WS namespace, env-vars, header convention concretely realized.
- **Actual runtime state:** schema declared but empty; WS handlers broadcast mock; 2 of 3 message handlers unimplemented; env-vars never read; header never sent/read; DBAODashboardView deprecated.
- **Severity:** CRITICAL for D61 (codename-shape parked candidate) — load-bearing.
- **Verified-in-repo anchors this session:**
  - `core/settings.py:340`: `-c search_path=studio,public,dbao,shared`
  - `core/routing.py:369-370`: `/ws/dbao/` + `/ws/dbao-dashboard/`
  - `core/new_pages_consumer.py:118-131`: `handle_dbao_message` — references undefined handlers
  - `core/new_pages_consumer.py:310-331`: `send_dbao_metrics` — 100% random
  - `.env.example:72-86`: 5 DBAO env-vars declared
  - `core/settings.py:707`: `x-dbao-client` in CORS
  - Grep results: zero `db_table='dbao.*'`; zero `async def send_query_status`; zero `async def handle_run_analytics`; zero frontend consumers of VITE_DBAO_*; single hit for `x-dbao-client` (the CORS whitelist).
- **Cross-arc reinforcement:** S1505 §14.1 MOCK-DATA-CONSUMER extended to +1 route (`/ws/dbao-dashboard/`) and +2 unimplemented handlers this session.
- **NEW pattern class:** NAMING-CONVENTION-WITHOUT-MATERIALIZATION.

### 14.2 DECOUPLED-VERIFICATION-SYSTEMS at BettingOutcomeVerifier ↔ MLPrediction

- **Source-of-truth (natural expectation + S1503 §14 flag):** wager outcomes should feed back to the prediction that generated them; prediction evaluations should reference wagers placed on the prediction.
- **Actual:** `BettingOutcomeVerifier` (`core/services/betting_outcome_verifier.py:30-481`) never touches `MLPrediction` (grep confirms). `PredictionEvaluator` (`sports/prediction_evaluator.py:40-420` per Explore Agent 6) never touches `PlacedWager`/`PlacedWagerLeg`.
- **Severity:** CRITICAL architectural — feedback loop for prediction model retraining does not close.
- **NEW pattern class:** DECOUPLED-VERIFICATION-SYSTEMS.
- **Consequence for xx99 posture brief:** either posture must confront this gap; integration posture ties the two systems + reroutes retrain; island posture builds sports-native retrain pipeline that closes internally.

### 14.3 Sports ↔ Signal Engine 6-arc consumer-side pattern

- **Source-of-truth (S1274 §14 Finding #6):** `sports_odds` not a valid `SignalCluster.pattern_type`.
- **Actual:** confirmed at 4 layers this session (Finding 3). Extends S1502+S1503+S1504+S1505 5-arc pattern to **6-arc pattern**.
- **Severity:** HIGH architectural.
- **Verified-in-repo anchors:** `core/models_signal_intelligence.py:75-86`; `core/services/signal_aggregation_service.py:139-168, 171-182`.

### 14.4 DECLARED-FEATURE-FLAG-GATES-NOTHING at `sports_intelligence`

- **Source-of-truth (natural expectation from flag semantics):** feature flag should gate at least one runtime path.
- **Actual:** `intelligence/views.py:44` returns hardcoded `True`; `core/intelligence_api.py:94` duplicates. Consulted nowhere at runtime. Config block `settings.SPORTS_ANALYTICS` (`core/settings.py:629-633`) similarly declared, similarly unconsulted.
- **Severity:** HIGH architectural.
- **NEW pattern class:** DECLARED-FEATURE-FLAG-GATES-NOTHING.

### 14.5 Discord HOT-PATH-CHOKE bypass at read commands

- **Source-of-truth (S1504 §14 pattern):** `SportsBettingCoordinator` should be the sole coordinator gate for sports read/write paths.
- **Actual — anchored bypass set (3 commands):** Discord `/odds` (`discord_bot.py:1108`), `/futures` (`discord_bot.py:1744`), `/slip` (`discord_bot.py:1851`) instantiate `TheOddsSpider` directly + rebuild presentation inline.
- **Anchored NON-bypass at `/arb`:** Discord `/arb` (`discord_bot.py:1260`) uses `ArbitrageDetector.run()` — the **same shared agent** that REST paths use — so `/arb` does NOT belong to this bypass set. §3.3 table captures this row; §17.2 duplicate/overlapping systems calls out the presentation-side inline logic overlap distinct from agent-side sharing.
- **Severity:** HIGH architectural.
- **Cross-arc reinforcement:** extends S1504 REST-side HOT-PATH-CHOKE to Discord side.
- **F1 fold (SIGN cycle 1):** anchor set tightened per Rigby Q5 Batch 1 — `/odds` + `/futures` + `/slip` explicit; `/arb` shared-agent exclusion made explicit at this section body (previously stated only in Executive Summary Finding 5 + §3.3 table).

### 14.6 Sports ↔ Memory Domain PARTIAL bridge

- **Source-of-truth (Cat F closure expectation):** all 4 market agents should participate in learning loop.
- **Actual:** 2 of 4 agent coverage (SportsOddsAnalyst + ArbitrageDetector); 0 AgentKnowledgeSource writes.
- **Severity:** HIGH architectural.
- **Verified-in-repo anchors:** `core/learning_bridges/sports_betting_bridge.py:532, 606`; grep zero for GamePredictor/SharpActionDetector in bridge.

### 14.7 `/ws/dbao-dashboard/` MOCK-DATA-CONSUMER footprint expansion

- **Source-of-truth (S1505 §14.1):** MOCK-DATA-CONSUMER at 1 route (`/ws/dbao/`).
- **Actual (verifier-loop this session):** 2 routes (`/ws/dbao/` + `/ws/dbao-dashboard/`) both dispatch to `NewPagesConsumer` with same page_type detection.
- **Severity:** HIGH operational — S1505 finding footprint doubles; post-arc remediation must cover both routes.

### 14.8 DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT at `_impl_collect_sports_odds_intelligence`

- **Source-of-truth (docstring):** post to Discord `#market-intelligence`.
- **Actual:** posts to `CHANNEL_BOARDROOM` (`core/services/discord_notifications.py:40`).
- **Severity:** HIGH operational.
- **NEW pattern class:** DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT.

### 14.9 SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION at `RealtimeIntelligenceEngine` cross-domain loops

- **Source-of-truth (method naming):** cross-domain analysis, opportunity detection, prediction generation.
- **Actual:** hardcoded crypto/trading demo values per Explore Agent 2 (`intelligence/realtime_engine.py:439-452, 454-513, 515-528, 592-605`).
- **Severity:** MED-HIGH — misleading operator-facing surface.
- **NEW pattern class:** SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION.

### 14.10 LATENT-ZERO-FIRE at `RealtimeIntelligenceEngine`

- **Source-of-truth (expected):** an engine named `RealtimeIntelligenceEngine` should have automatic startup path.
- **Actual:** zero beat entries; zero `@shared_task` wrapper; only `start_skynet()` module-level function at line 693.
- **Severity:** MED-HIGH — deepens the S1503 §14.1 ZERO-FIRE-BEAT pattern (which had a beat entry that didn't fire; this has no beat entry at all).

### 14.11 `IntelligencePage` frontend does not consume sports despite flag claim

- **Source-of-truth (flag semantic):** `sports_intelligence: True` should reflect visible sports intelligence to the user.
- **Actual:** `frontend/src/pages/IntelligencePage.tsx` (per Explore Agent 2) does not import sports APIs; tabs do not carry sports data.
- **Severity:** MED.

### 14.12 Drift matrix summary

Cat F introduces 4 new pattern classes this session (NAMING-CONVENTION-WITHOUT-MATERIALIZATION + DECOUPLED-VERIFICATION-SYSTEMS + DECLARED-FEATURE-FLAG-GATES-NOTHING + DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT + SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION — 5 classes if we count SCOPE-CLAIM separately per §14.9). Combined with prior arc classes (S1501 fragile-contract + S1502 armed-but-under-instrumented + S1503 ZERO-FIRE-BEAT + S1502 PROVENANCE-STAMP-ABSENT + S1503 armed-but-zero-fire + S1504 WRITE-ONLY-AND-FORGOTTEN + S1504 HOT-PATH-CHOKE + S1505 MOCK-DATA-CONSUMER + S1505 DEAD-RENDER-PATH + S1505 AUTH-DRIFT), the Group 1500 arc has produced **~13 distinguishable maturity/drift pattern classes** — a load-bearing catalog for xx99 §4 cross-cutting patterns.

---

## 15. Known Technical Debt

**Q15 — What is the known technical debt?**

Debt matrix (severity | scope | remediation cost):

### 15.1 CRITICAL — DBAO codename resolution owed

- Scope: 6 declared artifacts across schema/WS/env-vars/header + 2 unimplemented handler stubs.
- Debt: naming footprint that would confuse any operator investigating; two runtime stubs that would AttributeError.
- Remediation: Chris-gated decision (D61 parent scoping parked). Either (i) materialize (build real product-line at schema + WS + env-vars + header layers), (ii) demote (rename or remove artifacts and mark scope out of platform), (iii) archive (keep header comments as historical marker, delete unimplemented handlers, remove unused env-vars).

### 15.2 CRITICAL — DECOUPLED-VERIFICATION-SYSTEMS at wager ↔ prediction

- Scope: `BettingOutcomeVerifier` + `PredictionEvaluator`.
- Debt: prediction retrain loop cannot close without cross-reference; user experience unaffected in short term but model drift over time.
- Remediation: post-arc T2 design-preparation follow-on (per D59 Chris-gated posture affects choice — integration ties the two; island builds sports-native retrain closure inside sports app).

### 15.3 HIGH — Signal Engine 6-arc consumer-side gap

- Scope: `SignalCluster.PATTERN_TYPE_CHOICES` + emitter keyword coverage + zero-writer surface.
- Debt: sports events invisible to signal-domain consumers; consistent across 6 audits.
- Remediation: post-arc T1 or T2 depending on posture. Integration: extend pattern_type + wire emitter shim. Island: build sports-native aggregator.

### 15.4 HIGH — Sports ↔ Memory PARTIAL bridge

- Scope: 2 of 4 market agents covered; 0 AgentKnowledgeSource writes.
- Debt: incomplete learning loop; some agents never learn from outcomes.
- Remediation: post-arc T2 — extend SportsBettingLearningBridge coverage; extend to AgentKnowledgeSource writes; or delegate design to S1300 canonical summary follow-on.

### 15.5 HIGH — Discord HOT-PATH-CHOKE bypass compounds S1504

- Scope: 3 Discord slash commands + 1 periodic digest task all bypass SportsBettingCoordinator; +1 (`/impl_collect_sports_odds_intelligence`) bypasses RealtimeIntelligenceEngine too.
- Debt: field-name drift risk in TheOddsSpider silently propagates; presentation logic duplicated inline in Discord.
- Remediation: post-arc T2 — route Discord read commands through coordinator; add coordinator gate to periodic digest.

### 15.6 HIGH — `RealtimeIntelligenceEngine` LATENT-ZERO-FIRE + SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION

- Scope: 4 loop methods hardcoded demo + zero beat entry + capabilities flag reports True regardless.
- Debt: the engine is a latent asset; operators cannot tell if it's running from the flag layer.
- Remediation: post-arc T2 — either (a) add beat entry + implement cross-domain loops for real, (b) rename/remove cross-domain loops, or (c) delete engine + flag if unused.

### 15.7 HIGH structural — No API contract source-of-truth for Discord bot commands (extends S1505 §15.5 F2 fold)

- Scope: 7 sports slash commands rebuild presentation + odds display inline; no shared schema.
- Debt: S1505 §15.5 F2 fold elevated `no API contract source-of-truth` to HIGH for the frontend surface. Cat F evidence shows the same debt at the Discord surface — no shared bet-outcome/odds/arb interface between REST, frontend, and Discord.
- Remediation: post-arc T2 — extract shared contract module (TypeScript interfaces + Python dataclasses generated from a single source).

### 15.8 MED — CODEOWNERS compound gap

- Scope: BettingPage.tsx (S1505 §18.1) + `betting_outcome_verifier.py` + `sports_betting_coordinator.py` + `sports_betting_bridge.py` + `realtime_engine.py` + DBAO consumer files (Cat F §18.1).
- Debt: post-arc PR routing has no obvious owner for any sports-relevant runtime file.
- Remediation: post-arc T4 cleanup — CODEOWNERS row for `sports/**`, `intelligence/realtime_engine.py`, `core/services/betting_*.py`, `core/services/sports_*.py`, `core/learning_bridges/sports_*.py`, `core/new_pages_consumer.py`.

### 15.9 MED — `docs/topics/sports-betting.md` gap

- Scope: no canonical topic doc for sports.
- Debt: onboarding new operators to sports surface requires reading 6 audit docs + prior handoffs.
- Remediation: xx99 (S1599) §7 anchor-update recommendation lands topic doc; sourced from P1–P6.

### 15.10 MED — DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT at `_impl_collect_sports_odds_intelligence`

- Scope: docstring says `#market-intelligence`; runtime posts to `CHANNEL_BOARDROOM`.
- Debt: silent misinformation for operators consulting docstring.
- Remediation: post-arc T4 cleanup — update docstring OR update channel constant to match docstring.

### 15.11 MED — Zero client-side auth gate on 2 IsAuthenticated endpoints (S1505 §14.3 continuation)

- Scope: `bettingApi.liveOpportunities` + `bettingApi.intelligence` (per S1505).
- Debt: silent 401 UX.
- Remediation: per S1505 §15 debt matrix — post-arc T2 either AllowAny migration or frontend UI error handling. Cat F does not add new debt here; continuity note.

### 15.12 MED-LOW — Zero dedicated test coverage on Cat F integration surfaces

- Scope: no tests for `SportsBettingLearningBridge`, `BettingOutcomeVerifier`, `_impl_collect_sports_odds_intelligence`, Discord commands, `NewPagesConsumer` DBAO handlers.
- Debt: refactor risk; changes could silently break integration.
- Remediation: post-arc T4 — cross-domain integration test suite.

---

## 16. Boundary Violations

**Q16 — What are the boundary violations?**

### 16.1 BettingOutcomeVerifier does not update MLPrediction despite semantic overlap

- Boundary: prediction lifecycle vs wager lifecycle.
- Violation: same underlying event (game outcome) is verified twice by two different systems with no cross-reference.
- File:line: `core/services/betting_outcome_verifier.py:30-481` never touches `MLPrediction`; `sports/prediction_evaluator.py:202` never touches `PlacedWagerLeg`.
- Severity: CRITICAL (per Finding 2 architectural weight).

### 16.2 Sports agents inherit BaseAgent learning hooks but do not invoke them

- Boundary: BaseAgent contract expects `_record_learning_outcome` to be called by concrete agents.
- Violation: `GamePredictor`, `SharpActionDetector` do not call in `execute()` (per Explore Agent 5).
- File:line: `core/agents/base_agent.py:3991-4060` (hook definition); `core/agents/markets/game_predictor.py` (missing call site); `core/agents/markets/sharp_action_detector.py` (missing call site).
- Severity: HIGH (per Finding 6).

### 16.3 Discord write commands bypass `SportsBettingCoordinator` validation

- Boundary: coordinator should be the sole write gate for sports models.
- Violation: `/bet` (line 1571) + `/resolve` (line 1687, 1705) write directly to `Wager` + `Bankroll`.
- Severity: MED (write path bypass — no data-integrity gate).

### 16.4 `_impl_collect_sports_odds_intelligence` bypasses both coordinator + intelligence engine

- Boundary: intelligence surface should own periodic sports intelligence emit.
- Violation: task uses spider directly.
- Severity: MED (per Finding 12).

### 16.5 `RealtimeIntelligenceEngine` cross-domain loops implemented as sports (?)

- Boundary: method naming vs implementation.
- Violation: `_opportunity_detection_loop`, `_cross_domain_analysis_loop` are cross-domain-named but hardcoded demo per Explore Agent 2.
- Severity: MED (per Finding 9 SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION).

---

## 17. Duplicate or Overlapping Systems

**Q17 — What are the duplicate or overlapping systems?**

### 17.1 DUAL-COORDINATOR-BYPASS at `_impl_collect_sports_odds_intelligence`

- Systems: `SportsBettingCoordinator` + `RealtimeIntelligenceEngine`.
- Overlap: both offer aggregation/coordination surfaces; task uses neither.
- File:line: `core/tasks_financial.py:1815-1902`; contrast `core/services/sports_betting_coordinator.py:21-96` + `intelligence/realtime_engine.py:98-116`.
- Consequence: three sports-intelligence paths (coordinator, engine, task) — the task bypasses both and rebuilds logic inline.

### 17.2 Discord `/odds` presentation logic duplicated inline

- Systems: REST `/api/v1/betting/brief` presentation (via `SportsBettingCoordinator`); Discord `/odds` embed rebuild.
- Overlap: both produce odds presentations; Discord rebuilds emoji/filter/embed inline every command.
- File:line: `core/services/discord_bot.py:1108-1259` (inline); `core/services/sports_betting_coordinator.py:generate_brief` (coordinator path).
- Consequence: field-name drift risk (Finding 5).

### 17.3 `RealtimeIntelligenceEngine` sports loop overlaps with `SportsBettingCoordinator`

- Systems: engine `_sports_intelligence_loop` (arbitrage + value-bet + line-movement + game-prediction); coordinator (`generate_brief` aggregates the same categories).
- Overlap: both produce sports intelligence outputs; unclear boundary.
- File:line: `intelligence/realtime_engine.py:123-437`; `core/services/sports_betting_coordinator.py:21-96`.
- Consequence: two intelligence surfaces; xx99 posture brief must address which is canonical.

### 17.4 Two verification systems for game outcomes (see also §16.1)

- Systems: `BettingOutcomeVerifier` (settles wagers from game scores); `PredictionEvaluator` (evaluates predictions from game scores).
- Overlap: both fetch game scores + evaluate outcomes.
- File:line: `core/services/betting_outcome_verifier.py:30-481`; `sports/prediction_evaluator.py:40-420` per Explore Agent 6.
- Consequence: DECOUPLED-VERIFICATION-SYSTEMS pattern (Finding 2).

### 17.5 `/ws/dbao/` + `/ws/dbao-dashboard/` — sibling routes to same consumer

- Systems: two WS route registrations; single consumer handler.
- Overlap: both entry points produce same mock payload.
- File:line: `core/routing.py:369-370`.
- Consequence: post-arc remediation must cover both routes (Finding 7).

---

## 18. Ownership Gaps

**Q18 — What are the ownership gaps?**

### 18.1 Compound CODEOWNERS gap across sports surface

- Files with zero CODEOWNERS row (verified via `.github/CODEOWNERS` search this session):
  - `core/services/betting_outcome_verifier.py`
  - `core/services/sports_betting_coordinator.py`
  - `core/learning_bridges/sports_betting_bridge.py`
  - `intelligence/realtime_engine.py`
  - `core/new_pages_consumer.py`
  - `frontend/src/pages/BettingPage.tsx` (S1505 §18.1)
- Ownership state: UNKNOWN.
- Load-bearing observation: **every sports-relevant runtime file is un-owned**. If Chris is offline, no CODEOWNERS-triggered review paths on sports PRs.
- Remediation: post-arc T4 (per §15.8).

### 18.2 DBAO product-line ownership

- No DBAO-scoped CODEOWNERS row; no designated maintainer of DBAO artifacts (schema/WS/env-vars/header).
- Combined with Finding 1 NAMING-CONVENTION-WITHOUT-MATERIALIZATION: DBAO is un-owned AND unmaterialized. D61 parked candidate.

### 18.3 `RealtimeIntelligenceEngine` ownership

- No CODEOWNERS row.
- Combined with LATENT-ZERO-FIRE (Finding 10): un-owned + latently-inactive.

### 18.4 `sports_intelligence` flag ownership

- No topic doc; no CODEOWNERS row on `intelligence/views.py` or `core/intelligence_api.py`; no ADR history.
- Combined with DECLARED-FEATURE-FLAG-GATES-NOTHING (Finding 4): un-owned + gates-nothing.

---

## 19. Recommended Future Research

**Q19 — What research does this suggest for the future?**

### 19.1 T1 (highest) — Chris-gated post-arc ADR for posture selection

- Owner: Chris (post-arc, after S1599 xx99 canonical summary).
- Input: xx99 §5 posture-decision evidence brief (D59) + Cat F §20.6 evidence plan.
- Output: canonical posture decision (integration vs island) + implementation plan.

### 19.2 T1 — DBAO codename resolution ADR (D61 parent parked candidate)

- Owner: Chris.
- Input: Cat F Finding 1 + §14.1 + §17.5 + §18.2.
- Options: materialize | demote | archive.

### 19.3 T2 (design-preparation) — Signal Engine `sports_odds` shim OR sports-native aggregator

- Owner: TBD.
- Input: Cat F §20.6 §A2 posture-tied criteria + evidence.
- Two paths: integration (extend pattern_type + build shim) or island (build sports-native aggregator).

### 19.4 T2 — MLPrediction ↔ BettingOutcomeVerifier reconciliation

- Owner: TBD.
- Input: Finding 2 + §14.2 + §16.1.
- Objective: close prediction retrain loop.

### 19.5 T2 — `docs/topics/sports-betting.md` topic doc

- Owner: TBD (post-xx99).
- Input: P1–P6 audits.
- Objective: onboarding surface for sports domain.

### 19.6 T2 — Discord surface refactor to route through SportsBettingCoordinator

- Owner: TBD.
- Input: Findings 5, 12 + §14.5 + §17.1 + §17.2.
- Objective: eliminate HOT-PATH-CHOKE bypass.

### 19.7 T3 — Employee OS follow-on: CODEOWNERS assignment for sports runtime files

- Owner: TBD.
- Input: Finding 13 + §18.1.

### 19.8 T3 — `RealtimeIntelligenceEngine` bootstrap decision

- Owner: TBD.
- Input: Finding 10 + §14.10.
- Options: add beat entry | remove engine | rename to a manual-tool.

### 19.9 T4 — Cleanup PRs surfacing from Cat F

- `send_query_status` + `handle_run_analytics` stub removal or implementation.
- `x-dbao-client` CORS whitelist removal (if header not needed).
- VITE/EXPO DBAO env-var removal from `.env.example`.
- `DBAODashboardView` cleanup.
- `_impl_collect_sports_odds_intelligence` docstring or channel fix (Finding 8).
- Duplicate `sports_intelligence` hardcoded literal at `core/intelligence_api.py:94` cleanup.

### 19.10 T4 — Sports test coverage backfill

- Cross-domain integration test suite covering learning bridge, verifier, and Discord commands.

### 19.11 T5 (optional) — Delegation to S1300 (Memory Domain follow-on)

- If posture decision favors integration and Memory bridge needs upgrade, S1300 follow-on session.

### 19.12 T5 — Delegation to Group 1600 (Content) if opened

- Discord `_impl_collect_sports_odds_intelligence` digest fits Content-Pipeline scope if Group 1600 opens.

---

## 20. Appendix

### 20.1 Frontmatter provenance

- Session: 1506
- Generated: 2026-07-02
- Domain: sports
- Category: F (Cross-Domain Integration Lens & Posture Decision Framing)
- Parent: `docs/research/domains/sports/1500_sports_domain_scoping.md`
- Siblings: S1501 (Cat A), S1502 (Cat B), S1503 (Cat C), S1504 (Cat D), S1505 (Cat E)
- Owner: claude-code-parent
- Verifier-loop: 6 load-bearing pre-Explore claims verified correct against source before draft integration.

### 20.2 Chris-locked decisions inherited

- D57 (S1500 open 2026-07-01): parent-with-children shape.
- D59 (S1500 open 2026-07-01): xx99 owes evidence-consolidated posture-decision framing + Chris-gated decision brief, NOT posture recommendation.
- D60 (S1500 open 2026-07-01): non-sports Intelligence bounded out.
- D61 (S1500 parked candidate): DBAO codename shape resolution — post-arc T-slot.
- D62 = (a) (S1501 open 2026-07-01): pre-brief mini-schema propagation upfront. Sixth-sibling application here.

### 20.3 Cat F pattern classes introduced this session (5)

1. NAMING-CONVENTION-WITHOUT-MATERIALIZATION (§14.1, Finding 1)
2. DECOUPLED-VERIFICATION-SYSTEMS (§14.2, Finding 2)
3. DECLARED-FEATURE-FLAG-GATES-NOTHING (§14.4, Finding 4)
4. DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT (§14.8, Finding 8)
5. SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION (§14.9, Finding 9)

Combined with prior arc classes, the Group 1500 Sports arc has produced approximately 13 distinguishable maturity/drift pattern classes across 6 audits. This is xx99 §4 cross-cutting-patterns input.

### 20.4 Explore-agent evidence summary

Six parallel Explore sub-agents ran this session per playbook §13:

- **Agent 1 (DBAO footprint):** confirmed NAMING-CONVENTION-WITHOUT-MATERIALIZATION verdict; enumerated 6 declared artifacts + zero runtime state; caught `send_query_status` + `handle_run_analytics` unimplemented stubs; caught `/ws/dbao-dashboard/` sibling route; cross-checked AI Nexus consumer as real-data contrast.
- **Agent 2 (Intelligence surface):** confirmed sports-native engine layer + domain-neutral REST + gates-nothing flag layer; enumerated `IntelligencePage` tab list (gates/pilots/experiments/spiders/predictions/income); flagged demo hardcoding in 4 cross-domain loops.
- **Agent 3 (Discord bridge):** enumerated 7 sports slash commands with read/write scope; confirmed 3-command HOT-PATH-CHOKE bypass; confirmed Discord write consumer surface; confirmed docstring-vs-channel drift; confirmed zero SignalCluster/AgentMemory emit from Cog.
- **Agent 4 (Signal Engine gap):** verified 10 valid PATTERN_TYPE_CHOICES with `sports_odds` absent; verified emitter keyword coverage missing sports; verified zero bridging code + zero sports-native aggregator; concluded gap requires sports-native aggregator (option ii).
- **Agent 5 (Memory bridge):** confirmed PARTIAL bridge (2/4 agent coverage + zero AgentKnowledgeSource); confirmed BaseAgent hooks not invoked by GamePredictor/SharpActionDetector; enumerated verified sports Celery beat entries.
- **Agent 6 (MLPrediction feedback):** confirmed DECOUPLED-VERIFICATION-SYSTEMS at BettingOutcomeVerifier + PredictionEvaluator; enumerated MLPrediction field list; confirmed no retrain consumer downstream.

### 20.5 Verifier-loop corrections applied pre-draft

Six load-bearing pre-Explore claims verified this session:

1. `SignalCluster.PATTERN_TYPE_CHOICES` at `core/models_signal_intelligence.py:75-86` — VERIFIED (10 types; `sports_odds` absent).
2. `send_query_status` + `handle_run_analytics` unimplemented across `core/` — VERIFIED via Grep (zero definition matches).
3. PostgreSQL `dbao` schema in search_path at `core/settings.py:340` — VERIFIED.
4. `/ws/dbao/` + `/ws/dbao-dashboard/` route registration at `core/routing.py:369-370` — VERIFIED.
5. `sports_intelligence` hardcoded at `intelligence/views.py:44` — VERIFIED.
6. SportsBettingLearningBridge `AgentMemory.objects.create` at `core/learning_bridges/sports_betting_bridge.py:532` (wager) + `:606` (arb) — VERIFIED.

Zero corrections needed; all Explore claims consistent with source before integration.

### 20.6 POSTURE-DECISION EVIDENCE PLAN (D59 load-bearing deliverable owed to xx99 §5)

**Explicit "Chris-gated selection" tag: This is evidence-plan framing, NOT posture selection.** xx99 (S1599) consolidates; Chris ratifies post-arc via ADR per D59.

Two candidate postures per S1274 §12.3:

- **Integration posture:** Sports becomes a first-class citizen of the mainline platform (uses SignalCluster + AgentMemory + AgentKnowledgeSource + SportsBettingCoordinator as sole gate + RealtimeIntelligenceEngine wired to beat + Discord routed through coordinator).
- **Island posture:** Sports maintains its own infrastructure (sports-native SignalAggregator + sports-scoped memory writes + sports-native retrain loop) — DBAO codename materializes as real product-line boundary.

**Criteria per posture (evidence catalog with P1–P6 citations):**

#### A. Integration posture success criteria

**A1. Sports events surface as SignalCluster rows within 5 minutes of source.**
- Evidence FOR: sports data flow to LegacySpiderData exists (S1501 §4); SignalCuratorService consumes all pattern_types uniformly (§9.1); low config change to add `sports_odds` as pattern_type.
- Evidence AGAINST: PATTERN_TYPE_KEYWORDS hardcoded non-sports (§9.1); no bridging code; no aggregator would produce sports_odds SignalCluster rows without dedicated shim.
- Operational cost estimate: MED (P1-grade — refined post-arc). Requires: pattern_type extension (LOW), keyword catalog extension (LOW), sports-data-to-signal shim (MED).
- Failure mode if not met: sports events remain Signal-Engine-invisible; xx99 §4 cross-cutting pattern persists.

**A2. `SportsBettingCoordinator` is sole coordinator gate.**
- Evidence FOR: coordinator exists (`core/services/sports_betting_coordinator.py:21-96`).
- Evidence AGAINST: Discord `/odds`, `/futures`, `/slip` bypass (Finding 5); `_impl_collect_sports_odds_intelligence` bypasses BOTH coordinator + engine (Finding 12).
- Operational cost estimate: MED (P1-grade). Requires: 3 Discord slash command refactors + 1 Discord digest task refactor + coordinator API extension for read-only paths.
- Failure mode: HOT-PATH-CHOKE + DUAL-COORDINATOR-BYPASS persist; field-name drift risk in TheOddsSpider.

**A3. All 4 sports market agents write to AgentMemory + AgentKnowledgeSource.**
- Evidence FOR: SportsBettingLearningBridge partial coverage (§9.2).
- Evidence AGAINST: 2/4 agents covered; 0 AgentKnowledgeSource writes.
- Operational cost estimate: LOW (P1-grade). Requires: bridge extension + agent hook wiring.
- Failure mode: PARTIAL-LEARNING-BRIDGE persists; sports drift over time.

**A4. `RealtimeIntelligenceEngine` auto-starts + emits SignalCluster in addition to WebSocket groups.**
- Evidence FOR: engine sports-native at loop layer.
- Evidence AGAINST: LATENT-ZERO-FIRE (no beat entry); zero SignalCluster emit path exists.
- Operational cost estimate: MED (P1-grade). Requires: beat entry + SignalCluster emit shim.
- Failure mode: latent asset remains inactive.

**A5. `MLPrediction ↔ BettingOutcomeVerifier` linkage closed.**
- Evidence FOR: both surfaces exist and evaluate game outcomes.
- Evidence AGAINST: DECOUPLED-VERIFICATION-SYSTEMS (Finding 2); zero cross-reference.
- Operational cost estimate: MED (P1-grade). Requires: FK or join method + wager settlement triggers prediction evaluation retrigger.
- Failure mode: DECOUPLED-VERIFICATION-SYSTEMS persists; retrain loop cannot close.

**A6. `sports_intelligence` feature flag gates real runtime paths + `IntelligencePage` displays sports.**
- Evidence FOR: flag reported to frontend; page exists.
- Evidence AGAINST: DECLARED-FEATURE-FLAG-GATES-NOTHING (Finding 4); page does not consume sports (Finding 11).
- Operational cost estimate: MED (P1-grade). Requires: flag wired to real settings/DB row + IntelligencePage sports tab or sports-adjacent widget.
- Failure mode: reported capability decoupled from reality.

**A7. DBAO codename materialized (real schema tables, real WS consumer, real env-vars).**
- Evidence FOR: 6 artifacts declared.
- Evidence AGAINST: NAMING-CONVENTION-WITHOUT-MATERIALIZATION (Finding 1); zero runtime state.
- Operational cost estimate: HIGH (P1-grade). Requires: schema migration + real DBAO consumer + frontend consumer wiring + header sender/receiver + full documentation.
- Failure mode: codename resolution deferred indefinitely.

#### B. Island posture success criteria

**B1. Sports-native signal aggregator in dedicated schema.**
- Evidence FOR: DBAO schema declared (empty); sports agents consume dict-based data (not LegacySpiderData); sports data structurally distinct from mainline signal data.
- Evidence AGAINST: no sports-native aggregator exists (§9.1); no `dbao.SportsSignalCluster` model exists.
- Operational cost estimate: HIGH (P1-grade). Requires: DBAO schema materialization + new model + new service + new consumer.
- Failure mode: island posture requires building all mainline analogs.

**B2. Sports-scoped memory writes (no cross-domain AgentMemory).**
- Evidence FOR: SportsBettingLearningBridge already writes UserAgentLearning (sports-scoped).
- Evidence AGAINST: AgentMemory writes today are already cross-domain (§9.2); refactor cost.
- Operational cost estimate: HIGH (P1-grade). Requires: bridge refactor + AgentMemory writes redirected to sports-scoped model + reader consumers updated.
- Failure mode: sports learning splits from mainline; xx99 §4 pattern-consolidation harder.

**B3. Sports-native retrain loop closes internally.**
- Evidence FOR: PredictionEvaluator + SportsBettingLearningBridge structural pieces exist.
- Evidence AGAINST: no retrain consumer; identify_retraining_candidates surfaced but unimplemented.
- Operational cost estimate: MED (P1-grade). Requires: retrain job + PredictionEvaluator → agent-model-update pipeline.
- Failure mode: sports drift.

**B4. Discord + REST + Frontend all consume single sports coordinator (still true regardless of posture).**
- Evidence FOR: coordinator exists.
- Evidence AGAINST: Discord bypasses (Findings 5, 12).
- Operational cost estimate: MED (P1-grade). Same as A2 — this cost is posture-agnostic.
- Failure mode: same as A2.

**B5. DBAO materializes as real Django app label + URL prefix.**
- Evidence FOR: 6 declared artifacts.
- Evidence AGAINST: NAMING-CONVENTION-WITHOUT-MATERIALIZATION.
- Operational cost estimate: HIGH (P1-grade). Requires: `dbao` app label + URL prefix + all Cat F models moved to dbao schema.
- Failure mode: same as A7 (opposite direction).

**B6. Sports-native intelligence engine (separate from `RealtimeIntelligenceEngine`).**
- Evidence FOR: engine sports-native at loop layer (structural fit).
- Evidence AGAINST: engine's cross-domain loop naming conflicts with island framing.
- Operational cost estimate: MED (P1-grade). Requires: rename + trim cross-domain loops + add beat + wire to sports-native aggregator.
- Failure mode: LATENT-ZERO-FIRE persists.

**B7. `sports_intelligence` flag replaced by DBAO product-line boundary.**
- Evidence FOR: DBAO scoping already declared.
- Evidence AGAINST: DECLARED-FEATURE-FLAG-GATES-NOTHING (Finding 4).
- Operational cost estimate: LOW (P1-grade). Requires: remove flag + document DBAO as product-line boundary.
- Failure mode: flag drift continues.

#### C. Cross-cutting criteria (both postures must meet)

**C1. CODEOWNERS coverage for every sports-relevant runtime file.**
- Evidence FOR: none — Cat F compound gap (Finding 13).
- Evidence AGAINST: 6 unassigned files.
- Operational cost estimate: LOW. Post-arc T4 cleanup.
- Failure mode: ownership drift persists.

**C2. `docs/topics/sports-betting.md` topic doc exists.**
- Evidence FOR: none — no doc exists.
- Evidence AGAINST: 6 audits without landing.
- Operational cost estimate: MED. xx99 §7 anchor-update.
- Failure mode: onboarding requires reading 6 audits.

**C3. Cross-domain integration test coverage for sports.**
- Evidence FOR: none — zero tests today.
- Evidence AGAINST: refactor risk high.
- Operational cost estimate: MED. Post-arc T4.
- Failure mode: silent breakage on refactor.

**C4. Test coverage for BettingPage.tsx (S1505 §15.2 continuation).**
- Same as C3, at frontend layer.

#### D. Failure-modes-if-criteria-not-met table

| Posture | Criterion not met | Failure mode |
|---|---|---|
| Integration | A1 | 6-arc SignalCluster gap persists |
| Integration | A2 | HOT-PATH-CHOKE + DUAL-COORDINATOR-BYPASS persist |
| Integration | A3 | PARTIAL-LEARNING-BRIDGE persists |
| Integration | A4 | LATENT-ZERO-FIRE persists |
| Integration | A5 | DECOUPLED-VERIFICATION-SYSTEMS persists |
| Integration | A6 | DECLARED-FEATURE-FLAG-GATES-NOTHING persists |
| Integration | A7 | NAMING-CONVENTION-WITHOUT-MATERIALIZATION persists |
| Island | B1 | sports events surface nowhere |
| Island | B2 | learning cross-domain forever |
| Island | B3 | prediction drift over time |
| Island | B4 | Discord bypass persists (posture-agnostic) |
| Island | B5 | codename remains ambiguous |
| Island | B6 | latent engine persists |
| Island | B7 | flag drift continues |
| Either | C1 | ownership drift |
| Either | C2 | onboarding drift |
| Either | C3-4 | refactor risk |

#### E. Operator-cost asymmetry summary

- **Integration posture total cost estimate:** ~7 criteria at LOW-MED except A7 (HIGH). Net weighted MED (P1-grade).
- **Island posture total cost estimate:** ~7 criteria at LOW-HIGH; B1, B2, B5 all HIGH. Net weighted HIGH-MED (P1-grade).
- **Cost asymmetry driver:** DBAO materialization (A7 vs B5) — same direction, opposite framing. Whichever posture is chosen, DBAO must resolve.

**Explicit "Chris-gated selection" tag confirmed.** xx99 (S1599) consolidates this plan into §5 posture-decision brief; Chris ratifies post-arc via ADR.

#### F. Criterion scoring rubric (F2 fold, SIGN cycle 1)

**Per Rigby Q15 Batch 3 SIGN-with-edits recommendation** — added to make the evidence plan xx99-consumption-ready with consistent scoring semantics. xx99 §5 posture-decision brief applies this rubric across the P1–P6 evidence corpus.

**Scoring scale per criterion (pass / partial / fail):**

- **PASS:** criterion demonstrably met at current runtime state — cite file:line for evidence.
- **PARTIAL:** criterion partly met — surface exists but coverage / instrumentation / lifecycle incomplete. Cite file:line for what exists + gap description.
- **FAIL:** criterion not met — no runtime evidence, or evidence explicitly contradicts. Cite file:line for contradiction or "grep zero" outcome.

**Minimum acceptable thresholds per criterion (F2 threshold minima):**

Integration posture criteria (A):
- **A1 (SignalCluster emit):** PASS threshold = ≥1 sports event surfaces as SignalCluster row within 5 min of source event; PARTIAL threshold = pattern_type exists in enum + shim scaffolded but no live emit; FAIL = current state (10 pattern types, zero sports emitters).
- **A2 (Coordinator gate):** PASS threshold = 0 Discord slash commands + 0 Celery digest tasks + 0 REST endpoints bypass coordinator for reads (writes remain direct); PARTIAL = 1-2 bypasses; FAIL = ≥3 bypasses. Current: 3 slash + 1 digest = FAIL.
- **A3 (Learning bridge coverage):** PASS threshold = all 4 market agents write AgentMemory + all 4 write AgentKnowledgeSource; PARTIAL = 3/4 agent coverage OR AgentMemory-only across 4/4; FAIL = ≤2/4 or 0 AgentKnowledgeSource. Current: 2/4 + 0 AKS = FAIL.
- **A4 (Engine auto-start + SignalCluster emit):** PASS = beat entry active + SignalCluster emit path live; PARTIAL = one of the two; FAIL = neither. Current: neither = FAIL.
- **A5 (Verification linkage):** PASS = wager settlement triggers MLPrediction evaluation retrigger + PredictionEvaluator emits to same downstream as BettingOutcomeVerifier learning path; PARTIAL = one direction wired; FAIL = full decouple. Current: full decouple = FAIL.
- **A6 (Flag + IntelligencePage reality):** PASS = flag gates real runtime path + IntelligencePage displays sports; PARTIAL = one of two; FAIL = neither. Current: neither = FAIL.
- **A7 (DBAO materialized):** PASS = schema has ≥1 real model + WS emits real data + env-vars consumed + header sent/received; PARTIAL = 2-3 of 4; FAIL = ≤1 of 4. Current: 0 of 4 = FAIL.

Island posture criteria (B):
- **B1 (Sports-native aggregator):** PASS = SportsSignalCluster model + service + consumer exist; PARTIAL = model exists but service/consumer missing; FAIL = no artifacts. Current: FAIL.
- **B2 (Sports-scoped memory):** PASS = 0 AgentMemory writes from sports agents + sports-scoped memory model exists + consumers migrated; PARTIAL = new model exists but AgentMemory writes not migrated; FAIL = no new model. Current: FAIL.
- **B3 (Sports-native retrain loop):** PASS = retrain job scheduled + PredictionEvaluator → agent-model-update pipeline live + observable accuracy improvement over 1 cycle; PARTIAL = pipeline defined but not scheduled; FAIL = no pipeline. Current: FAIL.
- **B4 (Coordinator sole read gate):** same rubric as A2 — posture-agnostic.
- **B5 (DBAO app label + URL prefix):** PASS = `dbao` Django app label + URL prefix mounted; PARTIAL = app label OR URL prefix; FAIL = neither. Current: FAIL.
- **B6 (Sports-native engine):** PASS = engine renamed + cross-domain loops trimmed + beat entry active + wired to B1 aggregator; PARTIAL = ≤2 of 4; FAIL = ≤1 of 4. Current: FAIL (only sports loop implemented; no beat, no rename, no aggregator).
- **B7 (Flag replaced by product-line boundary):** PASS = `sports_intelligence` flag removed + DBAO documented as product-line boundary; PARTIAL = one of two; FAIL = neither. Current: FAIL.

Cross-cutting criteria (C, both postures):
- **C1 (CODEOWNERS):** PASS = every sports-relevant runtime file has CODEOWNERS row; PARTIAL = ≥50% covered; FAIL = ≤50% covered. Current: 0% = FAIL.
- **C2 (`docs/topics/sports-betting.md`):** PASS = topic doc exists + links from PLATFORM_WHAT_IT_IS.md + latest handoff; PARTIAL = topic doc exists without cross-linking; FAIL = no topic doc. Current: FAIL.
- **C3 (Integration test coverage):** PASS = ≥1 test per Cat F integration surface (learning bridge, verifier, Discord command, DBAO consumer); PARTIAL = 1-2 surfaces covered; FAIL = 0 tests. Current: FAIL.
- **C4 (BettingPage.tsx test coverage per S1505 §15.2):** PASS = ≥1 test; PARTIAL = mock-level test; FAIL = 0 tests. Current: FAIL.

**xx99 application note:** the rubric is designed so xx99 §5 posture-decision brief can present current-state score per criterion consistently (all FAIL today reflects the load-bearing observation that BOTH postures require substantive investment — neither is a "current state maps cleanly to" default). Chris post-arc ADR judges which set of PASS-transitions is preferable given the cost-asymmetry summary (§E) and failure-modes table (§D).

**F2 fold provenance:** added per Rigby Q15 Batch 3 SIGN-with-edits recommendation — scoring rubric + threshold minima for xx99 consumption-readiness. Cycle 2 SIGN-clean at High anticipated post-fold-land per S1501+S1502+S1503+S1504+S1505 cycle-1-predict-cycle-2 accuracy.

### 20.7 Sports Domain Lifecycle Traceability Table stub (per parent §12.5)

xx99 assembles the full table. Cat F contributes the following rows (per parent §12.5 stage list) with owner + file:line anchor per stage:

| Lifecycle stage | Current owner | File:line anchor | Integration-posture requirement | Island-posture requirement | Evidence citation |
|---|---|---|---|---|---|
| Odds ingestion | Cat A spiders (S1501) | 5 spiders (S1501 §5) | shared with mainline signal source | private ingestion queue | S1501 §5 |
| Fixture / entity identity resolution | UNKNOWN (per parent §12.5 fold — may resolve UNKNOWN if not surfaced) | UNKNOWN | shared canonical resolver | private resolver in dbao schema | UNKNOWN (Cat F cannot close) |
| Normalization | Coordinator / agents (S1502) | `sports_betting_coordinator.py` | shared normalization layer | private in dbao | S1502 §5 |
| Prediction | Sports agents (S1502) | 4 agents in `core/agents/markets/` | shared MLPrediction schema (public) | private MLPrediction in dbao | S1502 §4 |
| User wager | Cat C (S1503) | `PlacedWager` `core/models_betting.py:13` | shared wager schema | private in dbao | S1503 §4 |
| Outcome verification | BettingOutcomeVerifier (S1503) | `core/services/betting_outcome_verifier.py:30` | shared verifier | private in dbao | S1503 §4 + Cat F §16.1 |
| Learning-loop feedback | SportsBettingLearningBridge (2/4 agents) | `core/learning_bridges/sports_betting_bridge.py:532, 606` | shared AgentMemory + AgentKnowledgeSource | private sports memory table in dbao | Cat F §9.2 |
| Signal aggregation | **MISSING** | — | extend SignalCluster.pattern_type | build sports-native aggregator | Cat F §9.1 |

**Owner column note:** UNKNOWN rows (fixture/entity resolution) are consistent with parent §12.5 fold — Cat F was not scoped to resolve this. xx99 assembles the full table.

### 20.8 SIGN fold notes (Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence)

**Fresh isolation pin:** `pa-c2cdbd5c0b8c451b` (minted at S1506 SIGN routing; retired at S1506 close via `session_tool.retire`).

**D48 preemptive stability-probe gate 9th arm CLEAN.** Probe results (cockpit_tool worker_health + infra_health_tool dependency_matrix pre-SIGN): 4 workers online / 0 active tasks / 4/4 pools healthy + 7/7 dependencies healthy / 0 warnings / 0 errors. Stability held across all 3 substantive SIGN turns (Batch 1 Q1-Q5 + Batch 2 Q6-Q10 + Batch 3 Q11-Q16). **Four-consecutive-fully-clean-arms sub-pattern S1503+S1504+S1505+S1506 confirmed** — extends S1505 three-consecutive-fully-clean sub-pattern. D48 codification remains READY for xx99 §10.2 playbook v3 §15 recommendation with strengthened 9-arc evidence base.

**Batch 1 Q1-Q5 verdicts:**
- Q1 Finding 1 DBAO NAMING-CONVENTION-WITHOUT-MATERIALIZATION: **CORRECT** (High)
- Q2 Finding 2 DECOUPLED-VERIFICATION-SYSTEMS: **CORRECT** (High)
- Q3 Finding 3 Signal Engine 6-arc completion: **CORRECT** (High)
- Q4 Finding 4 DECLARED-FEATURE-FLAG-GATES-NOTHING: **CORRECT** (High)
- Q5 Finding 5 Discord HOT-PATH-CHOKE extension: **CORRECT-with-EDIT** (Medium) → F1 fold

**Batch 2 Q6-Q10 verdicts:**
- Q6 Finding 6 Sports ↔ Memory PARTIAL bridge: **CORRECT** (High)
- Q7 Finding 7 `/ws/dbao-dashboard/` sibling footprint expansion: **CORRECT** (High)
- Q8 Finding 8 DOCSTRING-VS-RUNTIME-CHANNEL-DRIFT: **CORRECT** (High)
- Q9 Finding 9 SCOPE-CLAIM-EXCEEDS-IMPLEMENTATION: **CORRECT** (High)
- Q10 Finding 10 LATENT-ZERO-FIRE deepens ZERO-FIRE-BEAT: **CORRECT** (High)

**Batch 3 Q11-Q16 verdicts:**
- Q11 Finding 11 IntelligencePage sports-tangential: **CORRECT** (High)
- Q12 Finding 12 DUAL-COORDINATOR-BYPASS: **CORRECT** (High)
- Q13 Finding 13 CODEOWNERS compound gap: **CORRECT** (High)
- Q14 Finding 14 topic-doc gap owed to xx99: **CORRECT** (High)
- Q15 §20.6 posture-decision evidence plan structural quality: **ADEQUATE with minor structural edits recommended** (High) → F2 fold
- Q16 Overall cycle 1 verdict: **SIGN-WITH-EDITS at High confidence**; must-fix = F1 + F2; nice-to-have = none

**F1 fold (§14.5 anchor set tightening) — LANDED at commit-time:**
- §14.5 body clarified — `/odds` + `/futures` + `/slip` explicit bypass set + `/arb` shared-agent exclusion made explicit (previously stated only in Executive Summary Finding 5 + §3.3 table).
- Rationale: Rigby Q5 Batch 1 caught that the "/arb uses shared agent" clause in the Executive Summary top line lacked an anchor in §14.5 body — moving §17.2 evidence into §14.5 body closes the gap.
- Cross-reference: §17.2 duplicate/overlapping systems still notes the presentation-side inline logic overlap for Discord read commands.

**F2 fold (§20.6 §F scoring rubric + threshold minima) — LANDED at commit-time:**
- §20.6 §F added — PASS/PARTIAL/FAIL scoring rubric + minimum acceptable threshold per criterion (A1-A7 + B1-B7 + C1-C4).
- Rationale: Rigby Q15 Batch 3 noted the evidence plan is structurally in-family but lacks scoring rubric + threshold minima for xx99 §5 posture-decision brief consumption-readiness. Adding both makes the plan xx99-consumption-ready.
- xx99 application note: rubric applied uniformly across P1-P6 evidence corpus at S1599 canonical summary.

**Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** per S1501+S1502+S1503+S1504+S1505 cycle-1-predict-cycle-2 accuracy (5-of-5 arc precedent).

**Do-not-regress notes for PR:**
- Preserve §2.1 Cat F contract statement (5 guarantees + 11 non-guarantees).
- Preserve §14.5 F1 fold anchor-set tightening.
- Preserve §20.6 §F F2 fold scoring rubric.
- Preserve §20.9 6-arc consumer-side pattern continuation.
- Preserve §20.10 6-sibling exemplar pattern for D62 = (a).

### 20.9 Continuation of 6-arc consumer-side pattern for sports_odds SignalCluster gap

- **S1502 §14.3:** Cat B agents write directly to MLPrediction / coordinator; no SignalCluster emit.
- **S1503 §14.3:** Cat C wager writes; no SignalCluster emit.
- **S1504 §14.5:** Cat D content writes SportsBettingBrief; no SignalCluster emit.
- **S1505 §14.6:** Cat E frontend consumes REST + polls; no SignalCluster emit.
- **S1506 §14.3 (this session):** Cat F confirms zero cross-domain surface (Signal Engine, Memory Domain, Intelligence surface, Discord, WS) emits SignalCluster from sports data.

**6-arc pattern completed.** xx99 §4 cross-cutting-patterns aggregates.

### 20.10 6-sibling exemplar pattern for D62 = (a) pre-brief mini-schema propagation

- S1501 §4.6 (Cat A ingestion) — original application.
- S1502 §4.8 (Cat B agents) — second sibling.
- S1503 §4.4 (Cat C wager) — third sibling.
- S1504 §4.4 (Cat D content) — fourth sibling.
- S1505 §4.2 (Cat E frontend) — fifth sibling.
- **S1506 §4.4 (Cat F cross-domain — this session)** — sixth sibling; produces the integrated view.

**6-sibling exemplar pattern completed.** D62 = (a) propagate-upfront validated across the entire arc. xx99 §10 meta-methodology template §10.2 codifies playbook v3 §5 addition candidate.

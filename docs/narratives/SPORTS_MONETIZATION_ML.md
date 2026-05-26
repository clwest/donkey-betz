---
title: "Sports + Monetization + ML — narrative (batch L)"
status: draft (batch L of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/stock-intelligence.md
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/narratives/FRONTEND.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to stock-intelligence topic doc + AGENTS.md sections + named handoff Sessions 995, 998B, 1010, 1011, 1012, 1027, 1029, 1043 in inventory)
provenance_note: This narrative covers verticals: sports (deeper than C's milestone 7), monetization (Gumroad publishing + subscription tiers), and ML predictions infrastructure (MarketIntelligenceBrief + PredictionOutcome + MLPrediction). Deliberately cross-references C, B, and D. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f).
---

# Sports + Monetization + ML predictions

> The verticals where the platform's verifiable feedback loops
> live. Sports settles in days; stocks settle in trade
> cycles; monetization settles in dollars. Each vertical has
> its own dashboard, its own pipeline of scheduled tasks, and
> its own learning loop closing on outcome data. This
> narrative pulls the strands together.

---

## 1. What this is

Three verticals share a structural similarity: each takes a
prediction or production action, lets time pass, and records
whether the prediction was right or the action made money.
The feedback signal closes the loop. Most agents in the
platform don't have this — they generate content that humans
judge, with no objective ground truth. These verticals do.

**Sports.** Spiders fetch odds and scores (`TheOddsSpider`).
`GamePredictor` produces `MLPrediction` rows. Users place
wagers (`PlacedWager`). `BettingOutcomeVerifier` settles wager
legs and verifies arbitrage items against final scores.
Result: AI Track Record (W/L rate per sport, prediction
accuracy, deduped by game). Eight scheduled tasks drive the
loop (covered in narrative E).

**Stocks.** Daily `MarketIntelligenceBrief` rows aggregate
stock analysis (~24 hours of spider data + multi-agent
debate via the StockAuditCoordinator). Bull-case + bear-case
sub-agents produce `PredictionOutcome` rows with targets
(e.g., "25%+ in 30 days"). Outcomes get evaluated; accuracy
feeds back into `_record_predictions_for_learning()`.
Dashboard at `/stocks` with 7 sub-tabs. Alert thresholds
calibrated (Yahoo Finance 2 % lowered from 5 %).

**Monetization.** Gumroad publishing (Session 487) for
direct-sale content. Discord subscription role management
(`RoleManager`, Session 439) for tier-gated access. Plus
the broader content-pipeline → blog publishing loop that
narrative B covers.

**Common threads.**
- Each has a primary spider feeding it (`TheOddsSpider` for
  sports; financial spiders for stocks).
- Each has a primary agent or coordinator producing
  predictions (`GamePredictor` / `StockAuditCoordinator`).
- Each has a verification / settlement loop.
- Each has a dashboard tab (narrative G covers betting +
  stocks frontend).
- Each has its own enrichment / context model.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`TheOddsSpider`** | The sports spider. Fetches odds + scores. `fetch_scores(sport_key, days_from=3)` returns completed + in-progress games (Session 998B added live games; previously filtered out). Joins with odds via `event_id`. |
| **`GamePredictor` agent** | Produces `MLPrediction` rows. Auto-creates League → Team → Game → MLPrediction chain (Session 1010). 21 `SPORT_KEY_LEAGUE` mappings (NFL, NCAAF, NBA, NCAAB, MLB, NHL, EPL, La Liga, Bundesliga, Serie A, Ligue 1, MLS, Champions League, Europa League, Liga MX, UFC/MMA, Boxing). Predictions > 14 days in future filtered out. |
| **`MLPrediction`** | The persistent prediction row. Carries `game`, prediction details, confidence, `was_correct` (set after settlement). Deduped by `Max('id')` per `game_id` in AI Track Record (Session 1012). |
| **`SharpActionDetector`** | Per-bookmaker odds divergence analyzer. Filters extreme odds (abs > 10,000) before computing ranges. Classifies signals HOT (≥ 30 divergence) or WARM (≥ 15). LLM prompt produces structured advice (which side to bet, best bookmaker, why, urgency: ACT NOW / MONITOR / WAIT). 13 sport keys supported. Session 1012 added `home_team` / `away_team` to signal dict for frontend rendering. |
| **`PlacedWager`** | A user's bet. Carries matchup, pick, odds, stake, sport, bookmaker. Settlement updates `status` and computes profit/loss. |
| **`BettingOutcomeVerifier`** | Settles `PlacedWager` legs and verifies arbitrage items. Consumes `TheOddsSpider.fetch_scores()` output. Runs every 30 min per scheduled-task arc. |
| **AI Track Record dedup (Session 1012)** | `get_ai_track_record()` in `core/views_odds_sports.py` deduplicates `MLPrediction` by `game_id` using `Max('id')` to prevent duplicate pending rows and inflated W/L when the prediction task runs multiple times for the same game. |
| **`MarketIntelligenceBrief`** | The daily stock analysis row. JSON fields: `total_stocks_analyzed`, `recommendations`. The brief that the Stocks Dashboard's Hub tab renders. |
| **`StockAuditCoordinator`** | Multi-agent stock orchestrator. Activates 9 agents on demand (BullCase, BearCase, MarketMovementMonitor, InstitutionalWatcher, MarketAnomalyDetector, SignalScanner, MarketIntelligenceCoordinator, StockAnalystAgent, plus the audit coordinator itself). |
| **`PredictionOutcome`** | The stock prediction row. `UniqueConstraint(brief, ticker, prediction_type)` to prevent duplicates. `_parse_target_move()` regex parses "25%+", "-25% or more". Session 994: handles numeric types from GPT JSON (int / float returned directly). Per-iteration error handling in `_record_predictions_for_learning()` — one bad ticker doesn't kill the batch. |
| **Brief save guard** | `_save_brief_for_tomorrow()` skips saving when `total_stocks_analyzed == 0`, preserving the previous good brief. 5-day weekend fallback for `_load_previous_brief`. The discipline that prevents empty-brief overwrites. |
| **Stocks dashboard sub-tabs (7)** | Hub (default) / Ticker Lookup / Overview / Market Briefs / Alerts / SEC Filings / Predictions. Each backed by a read-only endpoint at `/api/stocks/*`. |
| **`StockMarketAlert`** | Per-stock alert row. Type / symbol / action. Bookmarkable. Yahoo Finance threshold 2 % (lowered from 5 %). Title-based dedup. |
| **8 sports scheduled tasks (Sessions 1010–1011)** | `collect_sports_odds` (every 20 min), `generate_game_predictions` (every 2 h), `update_game_scores` (every 30 min), `evaluate_completed_predictions` (hourly), `verify_betting_outcomes` (every 30 min), `settle_user_bets` (every 15 min), `generate_accuracy_report` (daily 9 AM), `cleanup_old_predictions` (weekly Mon 3 AM). The full pipeline runs without human intervention. Covered in narrative E § 5. |
| **`GumroadPublishingService`** | Session 487. Direct-sale content publishing. PA tool `GumroadCommands` (Discord, narrative K) gives one-button publishing. |
| **`RoleManager` Discord Cog (Session 439)** | Subscription role management. 0 commands; event-driven. Promotes Discord roles when a user subscribes / cancels. Closes the "subscription tier → access" loop. |
| **PA `stock_intelligence_tool` (Session 979)** | 5 actions: `overview`, `briefs`, `alerts`, `predictions`, `sec_filings`. The PA's stock-vertical surface. Routing fix Session 979: `'intelligence'` keyword removed from `spider_data` intent to prevent "stock intelligence" misrouting; `spider_data_tool` made defensive — unknown actions fall back to `'recent'` instead of raising ValueError. |
| **Today's Games ESPN merge (Session 1012)** | `get_todays_games()` merges ESPN scoreboard data into odds events. Fuzzy team-name substring match. Adds `period`, `clock`, `status_detail` to each game response. Includes `h2h_odds` per-bookmaker array for comparison grids. |
| **AI Track Record W/L** | The frontend surface (Betting Dashboard, narrative G) that renders dedup'd predictions + outcomes. By-sport breakdown (NCAAB W/L%, NFL W/L%, etc.). Pending predictions list. Confidence calibration score. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — stock + sports verticals as separate dashboards** *(Inferred, early sessions)* | `/stocks` and `/betting` dashboards exist as separate frontend surfaces. `MarketIntelligenceBrief`, `StockMarketAlert`, basic `MLPrediction` and `PlacedWager` models exist. Daily brief generation. | The platform needed verticals where outcomes settle objectively — sports (bet wins/loses) and stocks (price moves). Separate dashboards give each vertical room to grow without interfering with the other. | Two dashboards in production. Each has its own data flow + UI. | **Active** — both dashboards still exist with their own routing. | `docs/topics/stock-intelligence.md`; `docs/narratives/FRONTEND.md` |
| **Session 487 — Gumroad publishing** | `GumroadPublishingService` introduced. Discord cog `GumroadCommands` (1 command). One-button publishing from Discord to Gumroad for direct-sale content (e.g., generated content packages, briefs). | The platform needed a monetization surface that didn't require building its own payments. Gumroad handled the storefront + payment; the platform handled the content + publishing trigger. | One-button publishing works from Discord. Content can be productized without bespoke commerce infrastructure. | **Active** — `GumroadPublishingService` still in `core/services/`. | `core/services/gumroad_publishing.py`; cross-ref `docs/narratives/DISCORD.md` Session 487 |
| **Session 439 — `RoleManager` (subscription tier integration)** | Discord cog `RoleManager` — 0 commands; event-driven. Promotes Discord roles when a user subscribes / cancels. Closes the subscription tier → access loop. | Subscription tiers needed an enforcement layer. Discord role-based access was the platform-native way to gate features (voice channels, gated commands, special channels) per subscription level. | Tier-gated access works in Discord without separate auth plumbing. | **Active.** | Cross-ref `docs/narratives/DISCORD.md` Session 439 |
| **Session 979 — PA `stock_intelligence_tool` + routing fix** | PA tool with 5 actions: `overview`, `briefs`, `alerts`, `predictions`, `sec_filings`. Routing fix: `'intelligence'` keyword removed from `spider_data` intent to prevent "stock intelligence" queries from misrouting to `spider_data_tool`. `spider_data_tool` made defensive — unknown actions fall back to `'recent'` instead of raising `ValueError`. | Stock queries through the PA were routing to the wrong tool because of keyword collision (`intelligence`). The fix was a two-sided patch: pull the keyword from one intent, make the other defensive against typos. | PA stock queries route correctly; defensive fallback prevents `ValueError` on tool misuse. | **Active** — both fixes in production. | `docs/topics/stock-intelligence.md` §"PA Integration (Session 979)"; `core/services/pa_tool_schemas.py` |
| **Sessions 995 + 998B — TheOddsSpider score fetching** | `TheOddsSpider.fetch_scores(sport_key, days_from=3)` from `/v4/sports/{sport}/scores`. Returns completed games initially (Session 995). Session 998B added in-progress games (`completed: False`). Returns same `event_id` as odds data for direct joining. Consumed by `BettingOutcomeVerifier` for wager settlement and arbitrage verification. | The sports vertical needed score data to verify predictions and settle bets. Without scores, wagers stayed `pending` forever. Score fetching closed the verification loop. | Wagers settle automatically once scores come in. Arbitrage items get verified. The vertical's loop is closed. | **Active.** Both sessions still relevant; `fetch_scores` returns both completed and live games. | Cross-ref `docs/narratives/SIGNAL_INTELLIGENCE.md` milestone 7 |
| **Sessions 994 + 1010 + 1011 + 1012 — sports + stocks pipeline maturation** | (994) `PredictionOutcome._parse_target_move()` handles numeric types from GPT JSON (int / float returned directly); per-iteration error handling in `_record_predictions_for_learning()` so one bad ticker doesn't kill the batch. (1010) `GamePredictor._store_predictions()` auto-creates League → Team → Game → MLPrediction chain. 21 `SPORT_KEY_LEAGUE` mappings. Predictions > 14 days in future filtered. `SharpActionDetector` classifies HOT (≥30) / WARM (≥15) signals. (1011) Sports pipeline automation — 8 scheduled tasks running unattended (covered in narrative E § 5). (1012) ESPN merge in `get_todays_games()`; `home_team` / `away_team` added to signal cards; AI Track Record dedup by game; Betting Dashboard tabs refreshed. | The two verticals had data flowing but the pipelines weren't fully automated. Sports needed scheduled prediction + verification + settlement. Stocks needed `PredictionOutcome` to handle edge cases (numeric vs string, per-ticker isolation). Both got their automation in this arc. | Sports pipeline runs end-to-end without human intervention; stock learning loop is per-ticker-resilient; AI Track Record W/L stats are correct (deduped); UI surfaces match the underlying data. | **Active** — automation is the standard. Cross-ref narrative C milestone 7 + narrative E § 5 + narrative G milestone 5. | `docs/topics/stock-intelligence.md` §"PredictionOutcome" Session 994 reference; `docs/topics/spider-network.md` §"Sports Prediction Persistence (Session 1010)"; cross-refs to C and E |
| **Sessions 1027 + 1029 + 1043 — sports queue rerouting (cross-ref E milestone 3)** | `sports` queue added to the worker fleet. Sports-specific tasks moved off `default` queue: `collect_sports_odds`, `generate_game_predictions`, `update_game_scores`, `evaluate_completed_predictions`, `verify_betting_outcomes`, `settle_user_bets`, `generate_accuracy_report`, `cleanup_old_predictions`. The OOM arc applied to the sports stack. | The sports vertical was running heavy tasks on the 200 MB `default` worker. Same problem the rest of the OOM arc had. | Sports tasks run on the dedicated `sports` queue. No OOMs from the sports vertical. | **Active** — `sports` queue is one of the standard queues. | Cross-ref `docs/narratives/WORKERS_AND_INFRASTRUCTURE.md` milestone 3 |
| **Continuous — Brief save guard + alert thresholds + dashboard refresh (steady-state)** | `_save_brief_for_tomorrow()` skips saving when `total_stocks_analyzed == 0`, preserving the previous good brief (the discipline that stops "empty brief overwrites good brief" class of bugs). 5-day weekend fallback for `_load_previous_brief`. Yahoo Finance alert threshold 2 % (lowered from 5 %). Title-based alert dedup. Brief detail UI replaced raw JSON dump with structured cards (ticker, recommendation badge, bull/bear arguments with score bars, risk factors). | The data quality work is ongoing — alerts kept double-firing on title-variant titles; briefs would empty themselves on weekends or holidays. Each fix is a small story; together they form the "the data is trustworthy" surface. | Briefs are stable over weekends. Alerts dedup correctly. UI renders briefs as cards instead of JSON. | **Active.** | `docs/topics/stock-intelligence.md` §§"Brief Save Guard", "Models", "Brief Detail UI" |

---

## 4. What came of it

### Wins

- **Verifiable feedback loops.** Sports settles. Stocks
  prediction outcomes evaluate against `was_correct`.
  Wagers settle automatically. The verticals close their
  loops without human judgment.
- **Sports pipeline runs unattended.** 8 scheduled tasks
  (cross-ref E § 5) drive the full odds → predictions →
  scores → evaluation → settlement loop.
- **AI Track Record dedup.** `Max('id')` per `game_id`
  prevents inflated W/L from re-runs. The number on the
  UI is the right number.
- **Per-ticker resilience in stocks.** Session 994's per-
  iteration error handling means one bad ticker doesn't
  kill the batch. The learning loop is robust to GPT JSON
  edge cases.
- **PA stock surface is one tool with five actions.**
  `stock_intelligence_tool` covers the stocks vertical
  from chat. Routing fix in Session 979 prevents
  `spider_data` misroutes.
- **Brief save guard prevents empty-brief overwrites.**
  Weekend / holiday gaps don't wipe out the previous good
  brief.
- **Monetization without commerce stack.** Gumroad +
  Discord roles cover the publishing + tier surfaces
  without bespoke payment infrastructure.

### Tradeoffs

- **Three verticals → three dashboards → three pipelines.**
  Cross-vertical synthesis (e.g., "is the market and
  sports sentiment correlated?") doesn't have an obvious
  home. Each vertical's UI is self-contained.
- **Stock dashboard tab count drift.** Topic doc says 7
  sub-tabs; PLATFORM_INVENTORY-derived counts vary based
  on snapshot. Authoritative count regenerated via
  inventory.
- **`MarketIntelligenceBrief` daily cadence.** One brief
  per day means market-moving events between briefs are
  caught only by alerts, not by a fresh brief.
- **`SharpActionDetector` LLM dependency.** The
  structured advice comes from an LLM call; if the LLM
  drifts in output format, the signal cards (narrative G
  § 3) may render incorrectly.
- **No cross-vertical learning surface.** Sports
  prediction accuracy doesn't inform stock prediction
  calibration (or vice versa) even though both are
  forecasting under uncertainty.
- **Gumroad coupling.** If Gumroad changes API or
  pricing, the publishing surface breaks. No abstraction
  layer.
- **Subscription tier ↔ Discord role coupling.**
  `RoleManager` assumes Discord is the access surface.
  Users without Discord can't easily use tier features.
- **`PredictionOutcome` regex (`_parse_target_move`).**
  Regex-based parsing of LLM-produced targets is fragile
  to format changes. Session 994 handled numeric types;
  future LLM output drift may need additional handlers.

### Follow-on systems enabled

- **Frontend (G)** — `/betting` (9 tabs) and `/stocks`
  (7 sub-tabs) are this layer's UI surfaces.
- **Signal Intelligence (C)** — Sports milestone 7 covers
  the same `TheOddsSpider` + `GamePredictor` +
  `SharpActionDetector` stack from a different angle
  (signal pipeline view).
- **Workers + Infrastructure (E)** — Sports `sports`
  queue + 8 scheduled tasks come from this layer's
  needs.
- **Content Pipeline (B)** — Gumroad publishing is part
  of the publishing surface; the platform's
  monetization tier sits alongside `publish_intent`.
- **Discord bot (K)** — `GumroadCommands`,
  `RoleManager`, voice features all touch this layer's
  monetization surfaces.
- **PA (D)** — `stock_intelligence_tool` is the chat
  surface; `intelligence_tool` (Session 1079
  consolidation) absorbs it.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`). Sports queue, 11
> tasks routed; stocks dashboard 7 sub-tabs; betting
> dashboard 9 tabs (UI + 12 named tabs in topic doc).

**Sports vertical.**
- Spider: `TheOddsSpider` — odds + scores
  (completed + in-progress).
- Agents: `GamePredictor`, `SharpActionDetector`,
  `BookmakerAgent`, `ArbitrageDetector`,
  `LineMovementAnalyzer`, `SportsOddsAnalyst`.
- Models: `League` / `Team` / `Game` / `MLPrediction` /
  `PlacedWager` / `SportsRecommendation`.
- Verifier: `BettingOutcomeVerifier` — settles wagers,
  verifies arbitrage.
- Frontend: `/betting` (9 tabs).
- Queue: `sports` (~11 tasks).
- Scheduled tasks (8, narrative E § 5): `collect_sports_odds`
  every 20 min; `generate_game_predictions` every 2h;
  `update_game_scores` every 30 min;
  `evaluate_completed_predictions` hourly;
  `verify_betting_outcomes` every 30 min;
  `settle_user_bets` every 15 min;
  `generate_accuracy_report` daily 9 AM;
  `cleanup_old_predictions` weekly Mon 3 AM.

**Stocks vertical.**
- Coordinator: `StockAuditCoordinator` (9-agent fan-out).
- Agents: `BullCaseAgent`, `BearCaseAgent`,
  `MarketIntelligenceCoordinator`,
  `MarketAnomalyDetector`, `SignalScanner`,
  `InstitutionalWatcher`, `MarketMovementMonitor`,
  `StockAnalystAgent`.
- Models: `MarketIntelligenceBrief`, `StockMarketAlert`,
  `PredictionOutcome`.
- Frontend: `/stocks` (7 sub-tabs — Hub default).
- PA tool: `stock_intelligence_tool` (5 actions:
  overview / briefs / alerts / predictions /
  sec_filings).
- Alert threshold: Yahoo Finance 2 % (lowered from 5 %).

**Monetization vertical.**
- `GumroadPublishingService` (Session 487) — direct-sale
  publishing.
- `RoleManager` Discord Cog (Session 439) — subscription
  tier ↔ Discord role.
- Cross-ref content pipeline (B) for blog publishing
  surface.

**Where to look when something stops working.**
- Sports wager stuck `pending` →
  `BettingOutcomeVerifier` not running, or
  `TheOddsSpider.fetch_scores()` not returning the
  game's score. Check `update_game_scores` task last-
  run timestamp.
- Stock brief is empty → check
  `total_stocks_analyzed`; the brief save guard prevents
  empty briefs from overwriting good ones, but the brief
  generation may have failed upstream. Check the
  `StockAuditCoordinator` last run.
- AI Track Record W/L inflated → AI Track Record dedup
  not applied. Check `get_ai_track_record()` uses
  `Max('id')` per `game_id`.
- Sports prediction not appearing → `GamePredictor` ran
  but failed; check `MLPrediction` rows for the game;
  predictions > 14 days in future are filtered out.
- `SharpActionDetector` signals empty → LLM call may
  have failed; check the per-bookmaker odds range was
  computable (extreme odds > 10,000 filtered out
  pre-analysis).
- PA stock query misrouted → check the routing fix
  (Session 979). `'intelligence'` should be in
  `stock_intelligence` intent, not `spider_data`.
- Gumroad publish fails → check
  `GumroadPublishingService`; Gumroad API may have
  changed.
- Discord subscription role not promoted →
  `RoleManager` is event-driven; check the subscription
  event fired and the cog received it.
- Alert duplicates → title-based dedup; if alerts have
  identical titles but different details, the dedup may
  be too aggressive.

---

## 6. Open questions / unknown outcomes

- **Cross-vertical learning.** *Known:* sports and
  stocks both forecast under uncertainty. *Unknown:*
  whether prediction-accuracy data from one vertical
  could calibrate the other. No cross-vertical learning
  surface in the corpus.
- **`MLPrediction` accuracy by sport.** *Known:* AI
  Track Record renders by-sport W/L. *Unknown:* which
  sports the platform is actually accurate on, and which
  it's not. Specific numbers not in the corpus.
- **Stock prediction accuracy.** *Known:*
  `PredictionOutcome` has `was_correct` after
  evaluation. *Unknown:* aggregate accuracy over time.
  Daily accuracy reports are generated; long-term
  trend Unknown.
- **Brief generation cost.** *Known:*
  `StockAuditCoordinator` fans out to 9 agents.
  *Unknown:* per-brief LLM cost. Daily cadence × 9
  agents could be significant. No telemetry surfaced.
- **Gumroad publishing volume.** *Known:* the service
  exists. *Unknown:* how much content has been
  published, what revenue has been generated. No
  monetization dashboard surfaces this in the corpus.
- **`RoleManager` event coverage.** *Known:* 0 commands;
  event-driven. *Unknown:* which exact subscription
  events fire it. Code-side detail not in topic doc.
- **`SharpActionDetector` calibration.** *Known:*
  thresholds HOT ≥ 30 / WARM ≥ 15. *Inferred:* set by
  the team based on observed bookmaker divergence
  ranges. *Unknown:* whether the thresholds have been
  recalibrated since first launch.
- **Sports prediction 14-day filter.** *Known:* future
  > 14 days filtered out. *Inferred:* set because odds
  for distant games are stale. *Unknown:* whether 14 d
  is right or whether a longer / shorter window
  performs better.
- **Yahoo Finance threshold change.** *Known:* lowered
  from 5 % to 2 %. *Unknown:* the originating session
  and whether the new threshold has been validated.

---

## 7. Source index

### Primary doc sources

- `docs/topics/stock-intelligence.md` — stocks vertical
  current state.
- `docs/topics/spider-network.md` §"Sports Prediction
  Persistence (Session 1010)" + §"TheOddsSpider Score
  Fetching (Session 995, updated 998B)" — sports
  vertical specifics.
- `docs/topics/agent-system.md` §"Provenance Tracking
  (Session 953)" — Stock (8) and Standalone (2:
  BookmakerAgent + CreationAgent) groups.
- `docs/PLATFORM_INVENTORY.md` — agent counts, queue
  routing for sports tasks.
- `docs/narratives/SIGNAL_INTELLIGENCE.md` (C) milestone
  7 — companion narrative on sports-as-signal-pipeline.
- `docs/narratives/FRONTEND.md` (G) milestone 5 + Betting
  Dashboard — UI side.
- `docs/narratives/WORKERS_AND_INFRASTRUCTURE.md` (E) §5
  — sports scheduled tasks.

### Named session handoffs cited above

- Session 487 — Gumroad publishing.
- Session 439 — `RoleManager`.
- Session 979 — PA stock_intelligence_tool + routing fix.
- Sessions 995 + 998B — TheOddsSpider score fetching.
- Sessions 994 + 1010 + 1011 + 1012 — sports + stocks
  maturation arc.
- Sessions 1027 + 1029 + 1043 — sports queue routing.

### Code anchors

- `core/agents/markets/game_predictor.py` —
  `GamePredictor` (`SPORT_KEY_LEAGUE` mappings).
- `core/agents/markets/sharp_action_detector.py` —
  HOT/WARM classification.
- `core/agents/markets/bookmaker_agent.py` —
  `BookmakerAgent`.
- `core/agents/stocks/*` — 9 stock agents.
- `core/views_odds_sports.py` — Betting Dashboard
  endpoints; AI Track Record dedup.
- `core/services/gumroad_publishing.py` — Gumroad
  service.
- `ai_core/spiders/odds_spider.py` (or equivalent) —
  `TheOddsSpider`.
- `core.models` — `MLPrediction`, `PlacedWager`,
  `Game`, `Team`, `League`, `MarketIntelligenceBrief`,
  `StockMarketAlert`, `PredictionOutcome`.

### Verification commands

- `python manage.py generate_platform_inventory` —
  regenerate.
- `python manage.py verify_doc_claims --only-drift` —
  drift check.
- PA: `intelligence_tool action=stocks_predictions` —
  current stocks prediction accuracy.
- PA: `intelligence_tool action=sports_record_wager` —
  manual wager recording.

# Spider Network

80 spiders across 18 categories collect real-time data that feeds agents, signals, and content. 74 working, 5 need API keys.

## Spider Categories

| Category | Count | Examples | Method |
|----------|-------|----------|--------|
| News & Media | 10 | TechCrunch, BBC, Reuters, NewsAPI (80k sources) | RSS, API |
| Financial & Crypto | 9 | CoinGecko, YahooFinance, Polygon, Kalshi, Etherscan | API |
| Tech & Development | 8 | HackerNews, DevTo, GitHub | JSON, API |
| Legal | 6 | CourtListener, FindLaw, Justia, Colorado Family Law | API, Playwright |
| Education | 5 | Teachable, Udemy, Coursera, Kaggle | RSS, API |
| Community & Social | 4 | Reddit (8+ subreddits), Bluesky, Discord | JSON |
| Design & Creative | 2 | Behance, Awwwards | RSS |
| Content & Monetization | 3 | Medium, Substack, ProductHunt | Scraper, RSS |
| Jobs & Freelance | 3 | RemoteOK, WeWorkRemotely, Adzuna | JSON, RSS, API |
| AI & ML | 3 | HuggingFace, Kaggle, Discord Training | API |
| Startups & VC | 3 | Crunchbase, VentureBeat, TechCrunch Startups | RSS |
| Specialty Tech | 5 | DefenseOne, SecurityWeek, Wired, MIT Tech Review | RSS |
| Entertainment | 4 | Spotify, Giphy, YouTube, Polygon Gaming | API |
| Lifestyle | 4 | Lifehacker, Travel, Parenting, Food | RSS |
| Weather | 2 | OpenMeteo, NOAA | API |
| Sports News | 1 | ESPN, NYT Sports, CBS Sports, Yahoo Sports, SI | RSS |
| Sports Injuries | 1 | RotoWire, CBS Injuries, RotoGrinders | RSS |
| Science & Health | 3 | Nature/ScienceDaily, WebMD/Healthline, arXiv | RSS |

**Needs API keys:** SEC Edgar, Bluesky, Discord, Spotify, YouTube

## SpiderData Model

Stored in `core.models_unified_system`. Key fields:
- `spider_name`, `source_url`, `data_type`, `raw_data` (JSON), `processed_data` (JSON)
- `relevance_score` (0-100), `insights` (JSON list)
- `embedding` (1536-dim vector via pgvector), `item_embeddings` (per-item vectors)
- `is_processed`, `is_actionable`

**Valid data_type values:** opportunity, job_posting, market_data, competitor_info, trend_data, user_feedback, product_info, pricing_data, content_idea, collaboration, news, research, tool_discovery, learning_resource, sports_news, sports_injuries, sports_odds. Default: `'research'`.

Do NOT use: market_alert, security_alert, price_alert, breaking_news (these don't exist).

## Signal Aggregation Flow

```
SpiderData (72h, raw)
  → SignalAggregationService.aggregate_signals()
    → Extract keywords + topics
      → Cluster by topic (primary) or keywords (secondary)
        → Filter below MIN_CLUSTER_SIZE (3)
          → SignalCluster (strength, confidence, novelty)
            → generate_auto_topics()
              → AutoTopic (rationale, suggested agents)
                → trigger_signal_driven_conversation()
                  → HiveMindSession → Initiative
```

**Celery task:** `scan_spider_opportunities` runs every 30 min.

**Cluster metrics:**
- Strength (0-1): signal count (40%) + source diversity (40%) + relevance (20%)
- Confidence (0-1): source count / 4
- Novelty (0-1): decays over 24h based on signal age

**7 pattern types:** demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, skill_demand, content_gap

## Spider Action Pipeline

`process_spider_actions` task (30 min) classifies actionable SpiderData:
- opportunity → create Initiative
- threat → create HumanAttentionItem (IMMUNE system)
- trend → create SignalCluster
- content_idea → create Dream

Feeds into Boardroom with dedup on `source_type + item_type + title`. Auto-approve has 24h age gate.

## Embeddings & Semantic Search (Session 1024)

- Model: OpenAI `text-embedding-3-small` (1536 dims)
- Storage: pgvector `VectorField` with HNSW index (`spiderdata_embedding_hnsw_idx`)
- Backfill: `backfill_spider_embeddings` task (every 10 min, batch 500)
- ~85% of SpiderData records have embeddings

**Primary search path (Session 1024):** `SpiderIntelligenceService.search_spider_data()` uses pgvector `CosineDistance` KNN as the primary search mechanism. Generates a query embedding, finds the 50 nearest neighbors, filters by `similarity >= 0.25`. Falls back to keyword matching only when pgvector/embeddings are unavailable.

**Key constants:** `SEMANTIC_TOP_K = 50`, `SEMANTIC_MIN_SIMILARITY = 0.25`

**Why:** Keyword matching (the old path) returned irrelevant results — e.g., a HuggingFace page mentioning "blockchain" in a tag scored `relevance=1.0` for blockchain queries. Semantic similarity fixes this at the root.

## TheOddsSpider Score Fetching (Session 995, updated 998B)

`TheOddsSpider.fetch_scores(sport_key, days_from=3)` fetches game scores (completed + live) from `/v4/sports/{sport}/scores`. Returns same `event_id` as odds data for direct joining. Used by `BettingOutcomeVerifier` to settle placed wagers and verify arbitrage items.

As of Session 998B, `fetch_scores()` returns both completed (`completed: True`) and in-progress (`completed: False`) games. Previously it filtered out live games.

## Sports Prediction Persistence (Session 1010)

`GamePredictor._store_predictions()` auto-creates League → Team → Game → MLPrediction chain from Odds API data. Uses `SPORT_KEY_LEAGUE` (21 full Odds API key → league tuple mappings) for proper league resolution. Fallback: `SPORT_PREFIX_MAP` (prefix-based). Predictions >14 days in the future are filtered out.

**Active leagues:** NFL, NCAAF, NBA, NCAAB (+ All-Stars), MLB, NHL, EPL, La Liga, Bundesliga, Serie A, Ligue 1, MLS, Champions League, Europa League, Liga MX, UFC/MMA, Boxing.

`SharpActionDetector` analyzes per-bookmaker odds divergence. Filters extreme odds (abs > 10000) before computing ranges. Classifies signals as HOT (divergence >= 30) or WARM (>= 15). Session 1012: Signal dict includes `home_team`/`away_team` for frontend recommendation rendering. LLM prompt asks for structured advice: which side to bet, best bookmaker (stale line), why (sharp/soft divergence), urgency (ACT NOW / MONITOR / WAIT). Supports 13 sport keys via frontend filter.

## Today's Games ESPN Merge (Session 1012)

`get_todays_games()` in `views_odds_sports.py` merges ESPN scoreboard data into odds events:
- Fetches ESPN scoreboards per sport_key that has live games
- Matches by fuzzy team name (substring match)
- Adds `period`, `clock`, `status_detail` to each game response
- Includes `h2h_odds` (per-bookmaker odds array) for comparison grids

## AI Track Record Dedup (Session 1012)

`get_ai_track_record()` deduplicates MLPredictions by game to prevent duplicate pending rows and inflated W/L stats when the prediction task runs multiple times for the same game. Uses `Max('id')` per `game_id` to select only the latest prediction.

## Odds-Consensus Predictions (Session 998B — Superseded by Session 1010)

Previously, `get_todays_games()` generated predictions from moneyline odds consensus. Session 1010 replaced this with persistent `MLPrediction` records stored by `GamePredictor` via `SPORT_KEY_LEAGUE` mapping.

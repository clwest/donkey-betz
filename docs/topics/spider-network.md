# Spider Network

77 spiders across 16 categories collect real-time data that feeds agents, signals, and content. 72 working, 5 need API keys.

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
| Science & Health | 3 | Nature/ScienceDaily, WebMD/Healthline, arXiv | RSS |

**Needs API keys:** SEC Edgar, Bluesky, Discord, Spotify, YouTube

## SpiderData Model

Stored in `core.models_unified_system`. Key fields:
- `spider_name`, `source_url`, `data_type`, `raw_data` (JSON), `processed_data` (JSON)
- `relevance_score` (0-100), `insights` (JSON list)
- `embedding` (1536-dim vector via pgvector), `item_embeddings` (per-item vectors)
- `is_processed`, `is_actionable`

**Valid data_type values:** opportunity, job_posting, market_data, competitor_info, trend_data, user_feedback, product_info, pricing_data, content_idea, collaboration, news, research, tool_discovery, learning_resource. Default: `'research'`.

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

## Embeddings

- Model: OpenAI `text-embedding-ada-002` (1536 dims)
- Storage: pgvector `VectorField`
- Backfill: `backfill_spider_embeddings` task (every 10 min, batch 500)
- ~88% of SpiderData records have embeddings
- Query: `SpiderIntelligenceService.query_by_text(query)` for semantic search

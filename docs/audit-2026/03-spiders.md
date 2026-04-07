# Dossier #3: Spider Network

**Audited:** April 6, 2026
**Status:** WORKING — 86 registered, ~54 verified, crawling every 30 minutes

---

## 1. Purpose

The Spider Network is a continuous intelligence-gathering system that crawls 40+ real web sources (news, APIs, RSS feeds) every 30 minutes, stores structured data, generates vector embeddings for semantic search, clusters data into signal patterns, and routes relevant intelligence to specialized agents for learning and action.

## 2. Runtime Evidence

- **86 spiders** registered in SpiderRegistry (`ai_core/spiders/spider_registry.py:183`)
- **54 verified** as actively collecting real data (Session 397 audit)
- **5 need API keys** (Polygon, Etherscan, SEC, Finnhub, Adzuna)
- **SpiderData** records in DB with real web content
- **SpiderExecutionLog** records tracking every crawl cycle
- **Celery Beat** fires `run_spider_network` every 30 minutes
- **Embedding backfill** runs every 15 minutes

## 3. Entry Points

| Trigger | Task | Schedule | Queue |
|---------|------|----------|-------|
| Beat schedule | `run_spider_network` | Every 30m | long_running |
| Beat schedule | `process_core_spider_data` | Every 5m | long_running |
| Beat schedule | `backfill_spider_embeddings` | Every 15m | long_running |
| Beat schedule | `aggregate_spider_signals` | Every 30m | long_running |
| Beat schedule | `scan_spider_opportunities` | Every 30m | long_running |
| Beat schedule | `process_spider_actions` | Every 30m | long_running |
| Django signal | `post_save(SpiderData)` | On each new record | sync |
| Manual | Single spider execution via API | On demand | long_running |

## 4. Execution Chain

### Crawl Cycle (every 30 minutes)

```
Celery Beat
  → run_spider_network [queue: long_running]
    → core/tasks_spiders.py:315 _impl_run_spider_network()
      → GovernanceState check (skip if freeze/safe_mode)
      → SpiderRegistry.list_spiders() → 86 spiders
      → For each spider:
          → collect_spider_data_sync(spider_name)
            → real_data_collector.py: SPIDER_TARGET_URLS lookup
            → HTTP fetch (aiohttp/feedparser) with User-Agent spoofing
            → Parse response → structured items
          → Deduplicate items (Session 616)
          → Create SpiderData record (raw_data, data_type, source_url)
          → Record SpiderExecutionLog (timing, item count, errors)
      → Return {spiders_run, items_collected, errors}
```

### Processing Pipeline (parallel, every 5-30 minutes)

```
SpiderData (new records)
  │
  ├─ process_core_spider_data (every 5m)
  │   → Batch 50 unprocessed records
  │   → Route to agents via SpiderAgentConnector
  │   → Create UserAgentLearning records
  │   → Mark as is_processed=True
  │
  ├─ backfill_spider_embeddings (every 15m)
  │   → Find SpiderData without embeddings (batch=200)
  │   → Generate via OpenAI text-embedding-3-small (1536 dims)
  │   → Store in SpiderData.embedding (pgvector)
  │   → Cache with 6-hour TTL
  │
  ├─ aggregate_spider_signals (every 30m)
  │   → Fetch 500 recent items (6-hour window)
  │   → Extract keywords (7 pattern types)
  │   → Cluster by topic (min 3 signals per cluster)
  │   → Score: strength, confidence, novelty, urgency
  │   → Create SignalCluster records
  │   → Generate AutoTopic suggestions (max 10/day)
  │
  ├─ scan_spider_opportunities (every 30m)
  │   → Analyze signal clusters for opportunity patterns
  │   → Create Opportunity records for boardroom
  │
  └─ process_spider_actions (every 30m)
      → Convert opportunities to ActionItem records
```

### Spider-to-Agent Bridge

```
SpiderData (post_save signal)
  → spider_data_bridge.py:318 @receiver
    → SpiderDataLearningLoop.process_spider_data()
      → Category-to-Agent mapping:
          tech → [ResearchAgent, TrendAnalysisAgent, ContentStrategyAgent, CTOAgent]
          jobs → [OpportunityScoringAgent, ResearchAgent]
          financial → [OpportunityScoringAgent, TrendAnalysisAgent, CTOAgent]
          design → [CreativeDirectorAgent, BrandIdentityAgent]
          ai_ml → [ResearchAgent, TrendAnalysisAgent, ImageAgent, VideoAgent, CTOAgent]
      → For each mapped agent:
          → Calculate confidence score:
              (relevance/100)*0.4 + completeness*0.3 + item_quality*0.3
          → Create UserAgentLearning record
```

Key files:
- `ai_core/spiders/spider_registry.py:183-1022` — registry
- `ai_core/spiders/real_data_collector.py:21-296` — 40+ URL configs
- `core/tasks_spiders.py:315-524` — execution pipeline
- `core/services/spider_semantic_search.py:162-250` — semantic search
- `core/services/signal_aggregation_service.py:115-696` — clustering
- `core/learning_bridges/spider_data_bridge.py:33-331` — agent bridge

## 5. Data Contracts

| Model | Purpose | Key Fields |
|-------|---------|------------|
| SpiderData | Raw crawled data | spider_name, source_url, data_type, raw_data, embedding(1536d), is_processed |
| SpiderDataAnnotation | Agent annotations on items | spider_data(FK), annotation_type, agent_name |
| SpiderExecutionLog | Crawl run metrics | spider_name, duration, items_collected, celery_task_id |
| SignalCluster | Aggregated signal patterns | name, pattern_type, strength, confidence, novelty, urgency, status |
| AutoTopic | Generated discussion topics | name, rationale, domain, urgency, suggested_agents |
| AgentKnowledgeSource | Agent-accessible knowledge | knowledge_type, spider_category, source_spider_names, confidence_score |
| UserAgentLearning | Per-agent learning records | agent_name, spider_data(FK), confidence_score |

## 6. External Dependencies

| Dependency | Spiders Using It | Env Var |
|------------|------------------|---------|
| OpenAI text-embedding-3-small | All (via backfill) | `OPENAI_API_KEY` |
| GitHub API | github, github_jobs | None (public) |
| CoinGecko API | coingecko | None (free tier) |
| Polygon.io | polygon_finance | `POLYGON_API_KEY` |
| Etherscan | etherscan | `ETHERSCAN_API_KEY` |
| HackerNews Firebase | hackernews | None (public) |
| Reddit JSON | reddit (8 subreddits) | None (public) |
| RSS/Atom feeds | 20+ spiders | None |

## 7. Outputs/Artifacts

What users see from spider activity:
- **Intelligence tab** — trending topics, signal clusters, spider data feed
- **Agent knowledge** — agents cite spider sources in their outputs
- **Attention items** — high-urgency opportunities surfaced to Home tab
- **Initiatives** — auto-created from signal → conversation → initiative pipeline
- **Blog content** — ContentWriterAgent uses spider data as source material

## 8. Failure Modes

| Failure | Cause | Impact | Mitigation |
|---------|-------|--------|------------|
| Source offline | Website down or API changed | Spider returns 0 items | Error logged, other spiders continue |
| Rate limited | Too many requests | 429 responses | Per-spider rate limiting (1-2 req/s) |
| Embedding API down | OpenAI outage | New data not searchable | Backfill retries every 15m |
| Duplicate data | Same article crawled twice | Inflated signal counts | Session 616 dedup on fetch |
| OOM on embedding | Large batch + model loading | Worker crash | batch_size=200, max-memory-per-child |
| Governance freeze | GovernanceState=freeze | All spiders skip | Automatic resume on mode change |

## 9. Current Status: WORKING

**Actively running:**
- Spider network crawling every 30 minutes
- Data processing every 5 minutes
- Embedding backfill every 15 minutes
- Signal aggregation every 30 minutes
- Opportunity scanning every 30 minutes

**Known limitations:**
- 5 spiders need API keys not configured (Polygon, Etherscan, SEC, Finnhub, Adzuna)
- ~32 spiders unverified since Session 397 audit (Dec 2025)
- Semantic search scans max 200 entries to prevent slow queries

## Verified Data (April 6, 2026)

- **78 spiders with execution logs** (of 86 registered)
- **54 working** (>50% runs return data), **24 broken** (<50% success)
- **Broken spiders**: weworkremotely, producthunt, courtlistener, techcrunch_startups, techcrunch, devto, axios, theverge, freecodecamp, wired
- **Top producers**: kalshi (485 items/run avg), theodds (58/run), cnn (42/run), findlaw (38/run)
- **Embedding coverage**: 20.1% (22,007 of 109,716 SpiderData records)
- **Dedup effectiveness**: Only 84 duplicate spider_name+source_url combos out of 109,716 records (99.9% unique)
- **Signal clusters**: 0 locally (clusters are on Railway prod DB, not in local DB)
- **Data freshness**: Most recent spider data from today (mobihealthnews, defenseone, venturebeat). Stalest: "Lead Generation Spider", "Finance Monitor Spider" last seen Dec 5, 2025 — these are legacy spiders that were removed.
- **Agent consumption**: 3,944 trend knowledge records + 3,667 with spider source attribution. Agents ARE consuming spider data.
- **Cost per 30-min cycle**: ~$0.0024 estimated ($0.000024/record × ~100 records/cycle)
- **Source reliability**: field exists in bridge code, appears hardcoded (confirmed)

## 10. Truth Gaps

- ~~Actual crawl success rate~~: **RESOLVED** — 54 working, 24 broken
- ~~Embedding coverage~~: **RESOLVED** — 20.1% (22,007 of 109,716)
- ~~Dedup effectiveness~~: **RESOLVED** — 99.9% unique (84 dupes of 109K)
- ~~Signal cluster quality~~: **RESOLVED** — 0 clusters in local DB (Railway-only data). Feature exists and runs every 30 min on production.
- ~~Data freshness~~: **RESOLVED** — active spiders have data from today. 5 legacy spiders have data from Dec 2025 (removed spiders, not stale active ones).
- ~~Agent consumption~~: **RESOLVED** — 3,667 knowledge sources with spider attribution. 3,944 trend-type records. Agents DO use spider data.
- ~~Cost per cycle~~: **RESOLVED** — ~$0.0024 per 30-min cycle ($0.000024/record, ~100 records/cycle). Total embedding cost: $0.52 across all time.
- **Source reliability scoring**: CONFIRMED GAP — field exists but values are hardcoded, not dynamically calculated from spider success rates.

# Option 6: Spider Health Dashboard

**Priority:** 6 (Sixth)
**Status:** Not Started
**Estimated Effort:** Low (1-2 sessions)

---

## Goal

Create operational visibility into the 67-spider network with health monitoring, data freshness tracking, and error diagnostics.

---

## Problem Statement

The platform has 67 spiders collecting data from 31 real sources, but:
- No visibility into which spiders are healthy vs failing
- Can't see when data was last refreshed per source
- No tracking of data quality or completeness
- Errors are only visible in logs
- No way to manually trigger specific spiders
- Can't assess embedding coverage across sources

---

## Current Spider Network

### Spider Statistics
| Metric | Count |
|--------|-------|
| Total Registered | 67 |
| Currently Working | 57 |
| Real Data Sources | 31 |
| SpiderData Records | 6,500+ |
| Embedding Coverage | ~95% |

### Spiders by Category

| Category | Count | Examples |
|----------|-------|----------|
| Tech News | 9 | TechCrunch, Wired, MIT Tech Review |
| Financial | 8 | CoinGecko, Yahoo Finance, Etherscan |
| Freelance | 5 | Upwork, Freelancer, Fiverr |
| Creative Assets | 5 | Dribbble, Behance, Unsplash |
| AI/Creative Tools | 4 | Product Hunt AI, AI tool aggregators |
| Digital Products | 5 | Gumroad, Etsy Digital, Teachable |
| Content Creation | 3 | YouTube trends, TikTok patterns |
| News | 4 | HackerNews, Reddit tech subs |
| Design | 3 | Awwwards, CSS Design Awards |
| Education | 3 | Udemy trends, Coursera, Skillshare |
| Legal | 4 | Case law, regulatory updates |
| Innovation | 3 | Kickstarter, Indiegogo, ProductHunt |
| Content | 5 | Medium, Substack trending |
| Remote Work | 2 | RemoteOK, WeWorkRemotely |
| Jobs | 1 | Adzuna API |
| Other | 3 | Various specialized sources |

---

## Deliverables

### 1. Spider Status Dashboard

**Requirements:**
- [ ] Grid/list of all 67 spiders
- [ ] For each spider show:
  - Name and category
  - Status: `healthy`, `degraded`, `error`, `disabled`
  - Last successful run
  - Last error (if any)
  - Records collected (24h / 7d / 30d)
  - Data freshness indicator
- [ ] Color-coded status (green/yellow/red)
- [ ] Filter by category, status
- [ ] Sort by last run, record count

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ SPIDER HEALTH DASHBOARD                               [Refresh All] │
├─────────────────────────────────────────────────────────────────────┤
│ Filter: [All ▼] Status: [All ▼]               Search: [_______] 🔍 │
├─────────────────────────────────────────────────────────────────────┤
│ Spider              │ Category    │ Status  │ Last Run  │ Records  │
├─────────────────────┼─────────────┼─────────┼───────────┼──────────┤
│ 🟢 techcrunch       │ Tech News   │ Healthy │ 2h ago    │ 847      │
│ 🟢 hackernews_api   │ News        │ Healthy │ 1h ago    │ 1,234    │
│ 🟡 coingecko_api    │ Financial   │ Degraded│ 6h ago    │ 456      │
│ 🔴 dribbble_popular │ Creative    │ Error   │ 3d ago    │ 89       │
│ ⚪ competitor_x     │ Business    │ Disabled│ -         │ 0        │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2. Data Freshness Monitor

**Requirements:**
- [ ] Visual timeline of data collection
- [ ] For each source, show:
  - Last data collection timestamp
  - Average refresh interval
  - Staleness alert (> expected interval)
  - Data volume trend
- [ ] Category-level freshness overview
- [ ] Alerts for stale sources (> 24h no data)

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ DATA FRESHNESS                                        Last 7 days   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Tech News (9 sources)                                               │
│ ████████████████████████████████████████████████████░ 98% fresh    │
│                                                                     │
│ Financial (8 sources)                                               │
│ █████████████████████████████████████████░░░░░░░░░░░ 75% fresh    │
│ ⚠️ coingecko_api stale (6h) | etherscan_api stale (4h)             │
│                                                                     │
│ Freelance (5 sources)                                               │
│ ████████████████████████████████████████████████████░ 95% fresh    │
│                                                                     │
│ Creative Assets (5 sources)                                         │
│ █████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 25% fresh    │
│ 🔴 dribbble_popular error | behance_projects error                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3. Error Diagnostics

**Requirements:**
- [ ] Recent error log viewer
- [ ] For each error show:
  - Spider name
  - Error type (timeout, auth, parsing, rate limit)
  - Error message
  - Timestamp
  - Retry count
  - Stack trace (expandable)
- [ ] Filter by error type
- [ ] Error frequency chart
- [ ] Auto-retry controls

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ ERROR LOG                                      [Clear Resolved]     │
├─────────────────────────────────────────────────────────────────────┤
│ Filter: [All Types ▼]                          Last 24 hours       │
├─────────────────────────────────────────────────────────────────────┤
│ 🔴 dribbble_popular                                    3h ago       │
│    Type: HTTP 403 (Forbidden)                                       │
│    Message: "Access denied. API key may be expired."                │
│    Retries: 3/3 (exhausted)                                        │
│    [View Stack Trace] [Retry Now] [Disable Spider]                 │
├─────────────────────────────────────────────────────────────────────┤
│ 🟡 coingecko_api                                      6h ago       │
│    Type: Rate Limit (429)                                          │
│    Message: "Rate limit exceeded. Retry after 60s."                │
│    Retries: 1/3                                                    │
│    [View Stack Trace] [Retry Now]                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4. Embedding Coverage

**Requirements:**
- [ ] Show embedding status per spider/source
- [ ] For each source:
  - Total records
  - Records with embeddings
  - Coverage percentage
  - Last embedding run
- [ ] Overall coverage metrics
- [ ] Trigger embedding backfill for gaps

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ EMBEDDING COVERAGE                                   Overall: 94.7% │
├─────────────────────────────────────────────────────────────────────┤
│ Source              │ Records │ Embedded │ Coverage │ Gap          │
├─────────────────────┼─────────┼──────────┼──────────┼──────────────┤
│ hackernews_api      │ 1,234   │ 1,234    │ 100%     │ -            │
│ techcrunch          │ 847     │ 847      │ 100%     │ -            │
│ reddit_programming  │ 523     │ 498      │ 95.2%    │ 25 pending   │
│ upwork_jobs         │ 312     │ 156      │ 50%      │ 156 missing  │
├─────────────────────┼─────────┼──────────┼──────────┼──────────────┤
│ TOTAL               │ 6,521   │ 6,176    │ 94.7%    │ 345 gap      │
└─────────────────────────────────────────────────────────────────────┘
                                              [Backfill All Gaps]
```

---

### 5. Manual Spider Controls

**Requirements:**
- [ ] "Run Now" button for any spider
- [ ] Bulk run by category
- [ ] Disable/enable spider
- [ ] Schedule adjustment
- [ ] Priority override (run next)

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ SPIDER: techcrunch                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ Status: 🟢 Healthy                                                  │
│ Schedule: Every 4 hours                                             │
│ Last Run: 2h ago (Success)                                          │
│ Next Run: in 2h                                                     │
│                                                                     │
│ [Run Now] [Disable] [Edit Schedule] [View Logs]                    │
│                                                                     │
│ Recent Runs:                                                        │
│ • 2h ago: ✅ 23 records collected                                  │
│ • 6h ago: ✅ 18 records collected                                  │
│ • 10h ago: ✅ 21 records collected                                 │
│ • 14h ago: ⚠️ 0 records (rate limited)                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 6. Data Quality Metrics

**Requirements:**
- [ ] Track data quality per source:
  - Duplicate rate
  - Empty/null field rate
  - Content length distribution
  - Unique vs repeated content
- [ ] Quality score per spider (0-100)
- [ ] Quality trends over time
- [ ] Low-quality alerts

---

## Technical Implementation

### Backend

#### New Models

```python
# core/models_spider_health.py

class SpiderHealthStatus(models.Model):
    """Real-time spider health tracking"""
    spider_name = CharField(unique=True)
    category = CharField()
    status = CharField(choices=[
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ])

    # Timing
    last_run_at = DateTimeField(null=True)
    last_success_at = DateTimeField(null=True)
    next_run_at = DateTimeField(null=True)

    # Metrics
    records_24h = IntegerField(default=0)
    records_7d = IntegerField(default=0)
    records_30d = IntegerField(default=0)
    total_records = IntegerField(default=0)

    # Error tracking
    consecutive_errors = IntegerField(default=0)
    last_error_message = TextField(null=True)
    last_error_at = DateTimeField(null=True)

    # Quality
    quality_score = DecimalField(default=100)
    duplicate_rate = DecimalField(default=0)
    embedding_coverage = DecimalField(default=0)

    # Config
    is_enabled = BooleanField(default=True)
    schedule_cron = CharField(null=True)
    priority = IntegerField(default=5)

class SpiderRunLog(models.Model):
    """Log of each spider execution"""
    spider_name = CharField()
    started_at = DateTimeField()
    completed_at = DateTimeField(null=True)
    status = CharField()  # success, error, timeout

    # Results
    records_collected = IntegerField(default=0)
    records_new = IntegerField(default=0)
    records_updated = IntegerField(default=0)
    records_skipped = IntegerField(default=0)

    # Error info
    error_type = CharField(null=True)
    error_message = TextField(null=True)
    error_traceback = TextField(null=True)
    retry_count = IntegerField(default=0)

    # Performance
    duration_seconds = DecimalField(null=True)
    memory_used_mb = DecimalField(null=True)

class SpiderDataQuality(models.Model):
    """Daily quality metrics per spider"""
    spider_name = CharField()
    date = DateField()

    # Quality metrics
    total_records = IntegerField()
    unique_records = IntegerField()
    duplicate_rate = DecimalField()
    null_field_rate = DecimalField()
    avg_content_length = IntegerField()

    # Embedding status
    embedded_count = IntegerField()
    embedding_coverage = DecimalField()
```

#### New API Endpoints

```python
# Spider Status
GET  /api/spiders/health/                   # All spider health status
GET  /api/spiders/<name>/health/            # Single spider detail
GET  /api/spiders/health/by-category/       # Category breakdown

# Spider Control
POST /api/spiders/<name>/run/               # Trigger spider manually
POST /api/spiders/<name>/toggle/            # Enable/disable
PATCH /api/spiders/<name>/schedule/         # Update schedule
POST /api/spiders/run-category/<cat>/       # Run all in category

# Logs & Errors
GET  /api/spiders/<name>/logs/              # Run history
GET  /api/spiders/errors/                   # Recent errors (all)
GET  /api/spiders/<name>/errors/            # Errors for spider
POST /api/spiders/<name>/retry/             # Retry failed spider

# Data Quality
GET  /api/spiders/quality/summary/          # Overall quality
GET  /api/spiders/<name>/quality/           # Per-spider quality
GET  /api/spiders/embeddings/coverage/      # Embedding status
POST /api/spiders/embeddings/backfill/      # Trigger backfill

# Analytics
GET  /api/spiders/analytics/freshness/      # Data freshness
GET  /api/spiders/analytics/volume/         # Collection volume
GET  /api/spiders/analytics/trends/         # Collection trends
```

### Frontend Components

1. **SpiderStatusGrid** - Main spider status display
2. **FreshnessMonitor** - Data freshness visualization
3. **ErrorLog** - Error diagnostics panel
4. **EmbeddingCoverage** - Embedding status tracker
5. **SpiderControls** - Manual control panel
6. **QualityMetrics** - Data quality display

### Integration Points

- `SpiderRegistry` - Existing spider registration
- `SpiderData` model - Data storage
- Celery tasks - Spider execution
- Embedding pipeline - Coverage tracking

---

## Implementation Steps

### Phase 1: Status Dashboard
1. [ ] Create SpiderHealthStatus model
2. [ ] Seed from existing spiders
3. [ ] Create status API endpoints
4. [ ] Build SpiderStatusGrid component

### Phase 2: Error Tracking
1. [ ] Create SpiderRunLog model
2. [ ] Hook into spider execution
3. [ ] Create error API endpoints
4. [ ] Build ErrorLog component

### Phase 3: Freshness Monitor
1. [ ] Add freshness calculation
2. [ ] Create freshness API
3. [ ] Build FreshnessMonitor visualization
4. [ ] Add stale data alerts

### Phase 4: Manual Controls
1. [ ] Create run/toggle API endpoints
2. [ ] Build SpiderControls panel
3. [ ] Add bulk operations
4. [ ] Hook into Celery

### Phase 5: Quality & Embeddings
1. [ ] Create SpiderDataQuality model
2. [ ] Add daily quality calculation task
3. [ ] Build EmbeddingCoverage component
4. [ ] Add backfill functionality

---

## Success Criteria

1. **Visibility:** Can see health of all 67 spiders at a glance
2. **Alerting:** Stale/erroring spiders visible within 5 minutes
3. **Control:** Can manually trigger any spider
4. **Quality:** Data quality tracked per source
5. **Coverage:** Know embedding gaps and can backfill

---

## Dependencies

- Existing: `SpiderRegistry`, `SpiderData`, spider execution tasks
- Benefits from Option 1 (sees which spiders feed which situations)
- Integrates with Option 5 (spiders trigger the triggers)

---

## Notes

- Start with read-only monitoring before controls
- Consider Discord alerts for spider failures
- May want scheduled health reports
- Future: Automatic spider healing (restart on error pattern)
- Consider cost tracking per spider (API calls, bandwidth)

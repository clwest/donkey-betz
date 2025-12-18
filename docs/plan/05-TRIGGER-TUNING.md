# Option 5: Trigger Tuning Interface

**Priority:** 5 (Fifth)
**Status:** Not Started
**Estimated Effort:** Low-Medium (1-2 sessions)

---

## Goal

Enable non-code adjustment of all 35 autonomous triggers, with analytics to guide threshold optimization.

---

## Problem Statement

The platform has 35 event-driven triggers across 7 domains, but:
- All thresholds are hardcoded in Python
- Changing a threshold requires code deployment
- No visibility into which triggers fire too often/rarely
- Can't A/B test different threshold values
- No way to temporarily disable noisy triggers

---

## The 35 Triggers

### Blockchain Domain (6 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| whale_movement | 100 ETH | Large transfers |
| gas_spike | 100 Gwei | Network congestion |
| contract_creation | 1M+ transactions | New major contracts |
| defi_tvl_change | 10% change | DeFi value shift |
| nft_volume_spike | 50% increase | NFT market activity |
| exchange_flow | 1000 BTC | Exchange deposits/withdrawals |

### Stock Market Domain (5 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| price_movement | 5% change | Significant price move |
| volume_spike | 200% avg volume | Unusual activity |
| earnings_surprise | 10% beat/miss | Earnings vs estimates |
| analyst_upgrade | Any | Rating changes |
| insider_trading | $1M+ | Large insider transactions |

### Content Domain (5 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| trending_topic | Top 10 HackerNews | Trending content |
| viral_prediction | 0.8+ score | High viral potential |
| engagement_spike | 300% normal | Unusual engagement |
| sentiment_shift | 0.3+ change | Opinion shift |
| competitor_content | Any major | Competitor activity |

### Income Domain (5 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| high_value_job | $150K+ | High salary opportunities |
| skill_match | 0.85+ match | Strong skill alignment |
| deadline_approaching | 24 hours | Urgent opportunities |
| new_platform | Any new source | New job platforms |
| remote_opportunity | Remote + $100K+ | Remote high-value |

### Financial Domain (5 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| market_open | 9:30 AM ET | Market hours |
| fed_announcement | Any | Federal Reserve news |
| earnings_calendar | 1 day ahead | Upcoming earnings |
| sector_rotation | 5% shift | Sector movements |
| vix_spike | VIX > 25 | Volatility increase |

### Research Domain (5 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| ai_model_release | Any major | New AI models |
| tech_announcement | Major tech news | Big tech releases |
| paper_publication | High citation | Important papers |
| github_trending | Top 25 | Trending repos |
| tool_release | Popular tools | New dev tools |

### Legal Domain (4 triggers)
| Trigger | Current Threshold | Notes |
|---------|-------------------|-------|
| case_law_update | Relevant citations | New precedents |
| regulatory_change | Any significant | Regulation updates |
| filing_deadline | 7 days ahead | Upcoming deadlines |
| court_ruling | Relevant cases | New rulings |

---

## Deliverables

### 1. Trigger Directory

**Requirements:**
- [ ] List all 35 triggers in a sortable table
- [ ] For each trigger show:
  - Name and domain
  - Current threshold
  - Enabled/disabled status
  - Fire count (24h / 7d / 30d)
  - Last fired timestamp
  - Cooldown period
- [ ] Filter by domain
- [ ] Sort by fire frequency
- [ ] Search triggers

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ TRIGGER TUNING                                        [Filter ▼]    │
├─────────────────────────────────────────────────────────────────────┤
│ Domain: [All ▼]                            Search: [_________] 🔍   │
├─────────────────────────────────────────────────────────────────────┤
│ Trigger           │ Threshold  │ Fires/7d │ Last     │ Status      │
├───────────────────┼────────────┼──────────┼──────────┼─────────────┤
│ whale_movement    │ 100 ETH    │ 23       │ 2h ago   │ ● Enabled   │
│ gas_spike         │ 100 Gwei   │ 156      │ 15m ago  │ ● Enabled   │
│ high_value_job    │ $150K+     │ 12       │ 4h ago   │ ● Enabled   │
│ vix_spike         │ VIX > 25   │ 3        │ 2d ago   │ ○ Disabled  │
│ ...               │            │          │          │             │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2. Threshold Editor

**Requirements:**
- [ ] Click trigger to open editor modal
- [ ] Display current threshold with explanation
- [ ] Input field for new threshold value
- [ ] Preview of expected fire frequency change
- [ ] Save with confirmation
- [ ] Validation (min/max bounds)
- [ ] Change history log

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ EDIT TRIGGER: whale_movement                              [× Close] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ DESCRIPTION:                                                        │
│ Fires when a single transaction moves more than X ETH               │
│                                                                     │
│ CURRENT THRESHOLD:                                                  │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  100 ETH                                                        │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ NEW THRESHOLD:                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  [150] ETH                                                      │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ IMPACT PREVIEW:                                                     │
│ • Current fire rate: 23 times/week                                  │
│ • Estimated new rate: 12 times/week (-48%)                         │
│ • Based on last 30 days of data                                     │
│                                                                     │
│ CHANGE HISTORY:                                                     │
│ • Dec 1: 50 ETH → 100 ETH (reduced noise)                          │
│ • Nov 15: Initial threshold set to 50 ETH                          │
│                                                                     │
│                                    [Cancel] [Save Changes]          │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 3. Trigger Analytics

**Requirements:**
- [ ] Fire frequency charts per trigger
- [ ] Domain comparison (which domains fire most)
- [ ] Time-of-day patterns
- [ ] Correlation analysis (triggers that fire together)
- [ ] False positive tracking (if user dismisses alert)
- [ ] Action rate (fires that led to user action)

**Visualizations:**
- Line chart: Fires over time per trigger
- Bar chart: Fires by domain
- Heatmap: Fires by hour/day of week
- Scatter plot: Fire frequency vs user action rate

---

### 4. Cooldown Management

**Requirements:**
- [ ] View current cooldown per trigger
- [ ] Adjust cooldown period (1 min to 24 hours)
- [ ] Show "in cooldown" status for recently fired triggers
- [ ] Override cooldown for urgent manual triggers
- [ ] Cooldown analytics (how often triggers are throttled)

**UI Mockup:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ COOLDOWN SETTINGS                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Trigger           │ Cooldown    │ Status         │ Next Fire       │
├───────────────────┼─────────────┼────────────────┼─────────────────┤
│ whale_movement    │ 30 min      │ Ready          │ -               │
│ gas_spike         │ 5 min       │ In Cooldown    │ in 3 min        │
│ trending_topic    │ 1 hour      │ Ready          │ -               │
│ vix_spike         │ 4 hours     │ In Cooldown    │ in 2h 15m       │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 5. A/B Testing for Thresholds

**Requirements:**
- [ ] Create threshold experiment
- [ ] Define control (current) vs variant (new) thresholds
- [ ] Split traffic (e.g., 50/50)
- [ ] Track metrics:
  - Fire rate difference
  - User action rate
  - Alert relevance score
- [ ] Automatic winner selection
- [ ] Apply winning threshold

**Workflow:**
1. Select trigger to test
2. Define variant threshold
3. Set experiment duration (1-4 weeks)
4. Monitor results
5. Apply winner or roll back

---

### 6. Enable/Disable Controls

**Requirements:**
- [ ] Quick toggle to disable any trigger
- [ ] Temporary disable with auto-re-enable
- [ ] Disable reason (optional note)
- [ ] Bulk disable by domain
- [ ] Schedule-based disable (e.g., disable stock triggers on weekends)

---

## Technical Implementation

### Backend

#### New Models

```python
# core/models_trigger_tuning.py

class TriggerConfiguration(models.Model):
    """Stores adjustable trigger thresholds"""
    trigger_name = CharField(unique=True)
    domain = CharField(choices=DOMAINS)
    description = TextField()

    # Threshold
    threshold_value = JSONField()  # Flexible storage
    threshold_type = CharField()   # numeric, percentage, boolean, etc.
    min_value = DecimalField(null=True)
    max_value = DecimalField(null=True)

    # Cooldown
    cooldown_seconds = IntegerField(default=300)
    last_fired_at = DateTimeField(null=True)

    # Status
    is_enabled = BooleanField(default=True)
    disabled_reason = TextField(null=True)
    disabled_until = DateTimeField(null=True)

    # Metrics
    fire_count_24h = IntegerField(default=0)
    fire_count_7d = IntegerField(default=0)
    fire_count_30d = IntegerField(default=0)
    user_action_count = IntegerField(default=0)

class TriggerThresholdChange(models.Model):
    """Audit log for threshold changes"""
    trigger = ForeignKey(TriggerConfiguration)
    old_value = JSONField()
    new_value = JSONField()
    changed_by = ForeignKey(User)
    changed_at = DateTimeField(auto_now_add=True)
    reason = TextField(null=True)

class TriggerExperiment(models.Model):
    """A/B test for trigger thresholds"""
    trigger = ForeignKey(TriggerConfiguration)
    control_threshold = JSONField()
    variant_threshold = JSONField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    status = CharField()  # running, completed, cancelled

    # Results
    control_fires = IntegerField(default=0)
    variant_fires = IntegerField(default=0)
    control_actions = IntegerField(default=0)
    variant_actions = IntegerField(default=0)
    winner = CharField(null=True)  # control, variant, inconclusive
```

#### New API Endpoints

```python
# Trigger Management
GET  /api/triggers/                         # List all 35 triggers
GET  /api/triggers/<name>/                  # Trigger detail
PATCH /api/triggers/<name>/threshold/       # Update threshold
PATCH /api/triggers/<name>/cooldown/        # Update cooldown
POST /api/triggers/<name>/toggle/           # Enable/disable
POST /api/triggers/<name>/disable-until/    # Temporary disable

# Analytics
GET  /api/triggers/analytics/summary/       # Overview stats
GET  /api/triggers/<name>/analytics/        # Per-trigger analytics
GET  /api/triggers/analytics/by-domain/     # Domain breakdown
GET  /api/triggers/analytics/correlations/  # Correlation matrix

# Experiments
GET  /api/triggers/experiments/             # List experiments
POST /api/triggers/<name>/experiment/       # Create experiment
PATCH /api/triggers/experiments/<id>/       # Update experiment
POST /api/triggers/experiments/<id>/apply/  # Apply winner

# History
GET  /api/triggers/<name>/history/          # Change history
```

### Frontend Components

1. **TriggerDirectory** - Main trigger list with filtering
2. **ThresholdEditor** - Modal for editing thresholds
3. **TriggerAnalytics** - Charts and metrics
4. **CooldownManager** - Cooldown settings panel
5. **ExperimentManager** - A/B test interface
6. **TriggerToggle** - Enable/disable controls

### Integration Points

The trigger tuning system must integrate with:
- `SituationTrigger` model (existing)
- `TriggerEvent` model (existing)
- Celery Beat for scheduled checks
- Discord notifications for alerts

---

## Implementation Steps

### Phase 1: Trigger Directory
1. [ ] Create TriggerConfiguration model
2. [ ] Seed with current 35 triggers
3. [ ] Create listing API endpoint
4. [ ] Build TriggerDirectory frontend

### Phase 2: Threshold Editor
1. [ ] Create update API endpoint
2. [ ] Build ThresholdEditor modal
3. [ ] Add validation and preview
4. [ ] Create change history log

### Phase 3: Analytics
1. [ ] Add fire count tracking to TriggerEvent
2. [ ] Create analytics API endpoints
3. [ ] Build TriggerAnalytics component
4. [ ] Add Chart.js visualizations

### Phase 4: Cooldown & Toggle
1. [ ] Add cooldown management API
2. [ ] Build CooldownManager panel
3. [ ] Add enable/disable toggles
4. [ ] Implement temporary disable

### Phase 5: Experiments (Optional)
1. [ ] Create TriggerExperiment model
2. [ ] Build experiment creation UI
3. [ ] Implement traffic splitting
4. [ ] Add winner calculation logic

---

## Success Criteria

1. **Visibility:** Can see all 35 triggers and their fire rates
2. **Control:** Can adjust any threshold without code deployment
3. **Analytics:** Understand which triggers are noisy vs valuable
4. **Responsiveness:** Threshold changes apply within 1 minute
5. **Safety:** Change history provides audit trail

---

## Dependencies

- Existing models: `SituationTrigger`, `TriggerEvent`
- Benefits significantly from Option 1 (see trigger activity first)
- May want to integrate with Option 4 for agent-level trigger tuning

---

## Notes

- Start with read-only view (Phase 1) before editing
- Consider "recommended threshold" based on fire patterns
- May want Discord commands for quick threshold checks
- Future: ML-based threshold optimization

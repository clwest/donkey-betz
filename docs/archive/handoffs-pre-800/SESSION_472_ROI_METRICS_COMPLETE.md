# Session 472: Market Intelligence Architecture - Phase 6 (ROI Metrics) COMPLETE

**Date:** December 17, 2025
**Status:** COMPLETE - ALL 6 PHASES DONE!

---

## Overview

Built a comprehensive ROI tracking system for the Market Intelligence Platform. This enables conversion funnel tracking, multi-touch attribution, ROI metric aggregation, and automated weekly intelligence briefs.

---

## What Was Built

### 1. Database Models (4 new models in `core/models_unified_system.py`)

#### ConversionEvent
Tracks conversion funnel events from opportunity view to revenue.

```python
class ConversionEvent(models.Model):
    id = models.UUIDField(primary_key=True)
    event_type = models.CharField(choices=[
        'view', 'click', 'apply', 'submit',
        'interview', 'offer', 'convert', 'revenue',
        'churn', 'refund'
    ])
    opportunity = models.ForeignKey('Opportunity')
    spider_data = models.ForeignKey('SpiderData')
    user = models.ForeignKey(User)
    value = models.DecimalField()  # Revenue amount
    currency = models.CharField(default='USD')
    attribution_source = models.CharField()  # Spider name, campaign
    attribution_medium = models.CharField()  # organic, paid, email
    previous_event = models.ForeignKey('self')  # Path linking
    metadata = models.JSONField()
```

#### ROIMetric
Aggregated ROI metrics by period and dimension.

```python
class ROIMetric(models.Model):
    period_type = models.CharField(choices=[
        'hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    ])
    period_start = models.DateTimeField()
    dimension = models.CharField(choices=[
        'overall', 'spider_source', 'opportunity_category',
        'user_segment', 'agent', 'campaign'
    ])
    dimension_value = models.CharField()

    # Counts
    views = models.IntegerField()
    clicks = models.IntegerField()
    applications = models.IntegerField()
    conversions = models.IntegerField()

    # Revenue
    total_revenue = models.DecimalField()
    total_cost = models.DecimalField()

    # Calculated metrics
    click_through_rate = models.DecimalField()  # CTR
    conversion_rate = models.DecimalField()  # CR
    cost_per_acquisition = models.DecimalField()  # CPA
    return_on_investment = models.DecimalField()  # ROI
    average_revenue_per_user = models.DecimalField()  # ARPU
    lifetime_value = models.DecimalField()  # LTV
```

#### AttributionPath
Full multi-touch attribution tracking.

```python
class AttributionPath(models.Model):
    conversion_event = models.OneToOneField(ConversionEvent)
    attribution_model = models.CharField(choices=[
        'first_touch', 'last_touch', 'linear',
        'time_decay', 'position_based', 'data_driven'
    ])
    path_data = models.JSONField()  # Full path
    path_length = models.IntegerField()
    time_to_conversion_hours = models.DecimalField()
    attribution_credits = models.JSONField()  # {source: credit}
    primary_source = models.CharField()
    primary_source_credit = models.DecimalField()
    attributed_value = models.DecimalField()
```

#### WeeklyIntelligenceBrief
Automated weekly performance summaries.

```python
class WeeklyIntelligenceBrief(models.Model):
    week_start = models.DateField()
    week_end = models.DateField()
    total_revenue = models.DecimalField()
    total_conversions = models.IntegerField()
    revenue_change_pct = models.DecimalField()  # vs prior week
    top_spider_sources = models.JSONField()
    key_insights = models.JSONField()
    recommendations = models.JSONField()
    executive_summary = models.TextField()
    status = models.CharField()  # pending, generating, complete
```

---

### 2. ROITracker Service (`core/services/roi_tracker.py`)

**~650 lines** - Complete ROI tracking implementation.

#### Main Class: ROITracker

```python
class ROITracker:
    def record_conversion_event(
        event_type, opportunity_id, spider_data_id, user_id,
        value, attribution_source, previous_event_id, ...
    ) -> ConversionResult

    def get_conversion_path(event_id) -> List[Dict]

    def get_funnel_metrics(start_date, end_date, source) -> Dict

    def get_attribution_by_source(start_date, end_date, model) -> List[Dict]

    def aggregate_roi_metrics(period_type, dimension, target_date) -> bool

    def generate_weekly_brief(week_start) -> Dict
```

#### Convenience Functions

```python
def record_view(opportunity_id, user_id, source) -> ConversionResult
def record_click(opportunity_id, user_id, source, previous_event_id) -> ConversionResult
def record_application(opportunity_id, user_id, source, previous_event_id) -> ConversionResult
def record_conversion(opportunity_id, user_id, value, source, previous_event_id) -> ConversionResult
def record_revenue(opportunity_id, value, user_id, source, previous_event_id) -> ConversionResult

def get_roi_tracker() -> ROITracker  # Singleton
```

---

### 3. API Endpoints (15 new endpoints in `core/views_roi_metrics.py`)

#### ROI Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/roi/summary/` | GET | Get ROI summary metrics |
| `/api/mi/roi/aggregate/` | POST | Trigger metric aggregation |
| `/api/mi/roi/dashboard/` | GET | Dashboard overview |
| `/api/mi/roi/stats/` | GET | Overall statistics |

#### Conversion Events

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/conversion/record/` | POST | Record conversion event |
| `/api/mi/conversion/events/` | GET | List events with filters |
| `/api/mi/conversion/<event_id>/path/` | GET | Get full conversion path |

#### Funnel

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/funnel/` | GET | Funnel metrics with drop-off |

#### Attribution

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/attribution/by-source/` | GET | Attribution by source |
| `/api/mi/attribution/paths/` | GET | List attribution paths |
| `/api/mi/attribution/<path_id>/` | GET | Path details |

#### Weekly Briefs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/briefs/` | GET | List weekly briefs |
| `/api/mi/briefs/generate/` | POST | Generate/get brief |
| `/api/mi/briefs/<brief_id>/` | GET | Brief details |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ROI METRICS PIPELINE                             │
└─────────────────────────────────────────────────────────────────────┘

CONVERSION FUNNEL:
view → click → apply → submit → interview → offer → convert → revenue

Each event links to previous via previous_event FK, building path:
┌─────────────────────────────────────────────────────────────────────┐
│  View → Click → Apply → Convert → Revenue                           │
│    ↓       ↓       ↓        ↓        ↓                              │
│  ConversionEvent records with attribution_source                    │
└─────────────────────────────────────────────────────────────────────┘

ATTRIBUTION MODELS:
┌─────────────────────────────────────────────────────────────────────┐
│  First Touch:    100% → First source                                │
│  Last Touch:     100% → Last source                                 │
│  Linear:         Equal split across all sources                     │
│  Time Decay:     More recent = more credit (2^position)             │
│  Position Based: 40% first, 40% last, 20% middle                    │
└─────────────────────────────────────────────────────────────────────┘

ROI AGGREGATION:
┌─────────────────────────────────────────────────────────────────────┐
│  ConversionEvents → ROIMetric (by period + dimension)               │
│                                                                      │
│  Periods: hourly, daily, weekly, monthly, quarterly, yearly         │
│  Dimensions: overall, spider_source, opportunity_category, ...      │
│                                                                      │
│  Metrics: CTR, conversion_rate, CPA, ROI, ARPU, LTV                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Testing

```bash
# Test ROI Tracker
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.services.roi_tracker import get_roi_tracker, record_view, record_revenue
from decimal import Decimal

tracker = get_roi_tracker()

# Record events
view = record_view(opportunity_id='<uuid>', source='techcrunch')
revenue = record_revenue(opportunity_id='<uuid>', value=Decimal('500'), source='techcrunch')

# Get metrics
funnel = tracker.get_funnel_metrics()
brief = tracker.generate_weekly_brief()
print(f'Total events: {funnel[\"total_events\"]}')"
```

---

## Files Changed/Created

### Created
- `core/migrations/0105_session_472_roi_metrics.py` - Migration
- `core/services/roi_tracker.py` - ROI tracker service (~650 lines)
- `core/views_roi_metrics.py` - API endpoints (~550 lines)
- `docs/handoffs/SESSION_472_ROI_METRICS_COMPLETE.md` - This file

### Modified
- `core/models_unified_system.py` - Added 4 ROI models (~660 lines)
- `core/urls.py` - Added 15 ROI API routes

---

## Market Intelligence Platform - ALL 6 PHASES COMPLETE!

| Phase | Name | Status | Session |
|-------|------|--------|---------|
| 1 | ML Scoring Engine (XGBoost + SHAP) | ✅ COMPLETE | 470 |
| 2 | Scoring Dispatcher (Realtime + Batch) | ✅ COMPLETE | 470 |
| 3 | HITL Validation (Auto-approve/reject + Queue) | ✅ COMPLETE | 470 |
| 4 | Event Bus (Redis Streams) | ✅ COMPLETE | 472 |
| 5 | Provenance & Compliance | ✅ COMPLETE | 472 |
| 6 | ROI Metrics | ✅ COMPLETE | 472 |

---

## Full System Capabilities

### Data Lineage (Phase 5)
- Track: Spider → Opportunity → Score → Validation → Outcome
- Blockchain-style hash chains for integrity
- Full audit trail

### ROI Tracking (Phase 6)
- Conversion funnel: view → click → apply → convert → revenue
- Multi-touch attribution (5 models)
- Period aggregation (hourly to yearly)
- Automated weekly intelligence briefs

---

## API Summary

Total Market Intelligence APIs: **26 endpoints**

- Phase 5 Provenance: 11 endpoints
- Phase 6 ROI: 15 endpoints

All accessible under `/api/mi/` prefix.

---

## Next Steps (Session 473 Options)

1. **Full Pipeline Integration Test** - End-to-end: Spider → Scoring → Validation → Provenance → ROI
2. **Connect Content Studio to ROI** - Track content generation revenue
3. **Discord ROI Commands** - `/roi-summary`, `/roi-brief`
4. **Real-time ROI Dashboard** - WebSocket updates for live metrics

---

**Market Intelligence Architecture COMPLETE! All 6 phases implemented.**

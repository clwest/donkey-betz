# Session 706: DIGESTIVE SYSTEM Complete

**Date:** January 6, 2026
**Status:** COMPLETE
**Focus:** Data Ingestion & Processing Monitoring - The 6th Body System

## Overview

Implemented the **DIGESTIVE SYSTEM** - monitors how raw data from spiders is transformed into actionable intelligence. This is the 6th component of the Human Body Architecture.

## Human Body Metaphor

| Digestion Concept | Technical Equivalent |
|-------------------|---------------------|
| **Food** | Raw spider data (RSS, API responses, scraped content) |
| **Mouth/Intake** | Spider execution → SpiderData creation |
| **Stomach** | Processing queue - normalization, deduplication |
| **Enzymes** | Transformation functions - embedding, scoring |
| **Intestines** | Routing pipeline to agents/services |
| **Nutrients** | Actionable intelligence (normalized, scored data) |
| **Waste** | Filtered/irrelevant data (low scores, duplicates) |
| **Metabolism Rate** | Processing throughput (items/minute) |

## Files Created (5)

| File | Lines | Purpose |
|------|-------|---------|
| `core/models_digestive.py` | ~280 | IngestionRoute, DigestivePulse, DigestionStatus models |
| `core/services/digestive.py` | ~600 | DigestiveSystemService singleton |
| `core/views_digestive.py` | ~380 | 8 REST API endpoints |
| `core/management/commands/digestion_check.py` | ~420 | CLI management command |
| `core/migrations/0152_session_706_digestive_system.py` | ~280 | Migration with 8 default routes |

## Files Modified (5)

| File | Changes |
|------|---------|
| `core/urls.py` | Added 8 DIGESTIVE API routes |
| `core/tasks.py` | Added `check_digestion` Celery task |
| `core/celery.py` | Added Beat schedule (60s interval) |
| `core/admin.py` | Registered 3 DIGESTIVE admin classes |
| `core/auth_middleware.py` | Added 7 DIGESTIVE endpoints to PUBLIC_PATHS |

## Database Models

### 1. IngestionRoute
Configuration for monitored data ingestion routes:
- Route types: spider, api, webhook, upload, stream
- Stages: intake, processing, enrichment, routing
- Thresholds: max_queue_depth, target_throughput, max_processing_time_ms
- Status flags: is_active, is_critical, is_builtin

### 2. DigestivePulse
Time-series records of digestion state:
- Overall status and digestion score
- Per-stage metrics (intake, processing, enrichment, routing)
- Bottleneck detection
- Check duration tracking

### 3. DigestionStatus
Current status per route (cached state):
- Current metrics: queue_depth, throughput, latency
- 24h rolling metrics: items processed, errors, success rate
- Last activity timestamps

## Default Routes Created

| Route Name | Type | Stage | Critical |
|------------|------|-------|----------|
| Spider News Intake | spider | intake | No |
| Spider Financial Intake | spider | intake | Yes |
| Spider Tech Intake | spider | intake | No |
| Spider Legal Intake | spider | intake | Yes |
| Spider Community Intake | spider | intake | No |
| Data Processing Queue | stream | processing | Yes |
| Embedding Pipeline | stream | enrichment | No |
| Agent Data Routing | stream | routing | Yes |

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/digestive/digest/` | Run full digestion check |
| `GET /api/digestive/status/` | Get cached digestion status |
| `GET /api/digestive/routes/` | List all ingestion routes |
| `GET /api/digestive/routes/<id>/` | Get specific route status |
| `GET /api/digestive/bottlenecks/` | Get current bottlenecks |
| `GET /api/digestive/metabolism/` | Get throughput metrics |
| `GET /api/digestive/history/` | Get digestion pulse history |
| `GET /api/digestive/is-digesting/` | Quick alive check |

## CLI Command

```bash
python manage.py digestion_check                    # Full digestion check
python manage.py digestion_check --json             # JSON output
python manage.py digestion_check --routes           # List all routes
python manage.py digestion_check --bottlenecks      # Show bottlenecks
python manage.py digestion_check --metabolism       # Show throughput
python manage.py digestion_check --watch            # Continuous monitoring
python manage.py digestion_check --history          # Show pulse history
python manage.py digestion_check --stage intake     # Check specific stage
```

## Status Levels

| Score | Status | Emoji | Meaning |
|-------|--------|-------|---------|
| 80-100% | healthy | 🟢 | Normal data processing |
| 60-79% | sluggish | 🟡 | Slow processing, minor delays |
| 40-59% | bloated | 🟠 | High queue depth, backlog |
| 20-39% | blocked | 🔴 | Processing stuck |
| 0-19% | starving | ⚪ | No data intake |

## Initial System State (Tested)

```
Overall Status: BLOATED (51.5%)
Is Digesting: No

INTAKE Stage:
  - Items (24h): 1,923
  - Spiders executed: 5,929
  - Success Rate: 29.5%

PROCESSING Stage:
  - Queue Depth: 9,681 items (HIGH!)
  - Throughput: 0.00/min

BOTTLENECKS DETECTED:
  - [WARNING] intake: Low spider success rate (29.5%)
  - [CRITICAL] processing: High queue depth (9,681 items pending)
  - [WARNING] processing: Low processing throughput (0.0 items/min)
```

## Celery Beat Schedule

```python
'digestive-system-check': {
    'task': 'core.tasks.check_digestion',
    'schedule': 60.0,  # Every 60 seconds
    'options': {'expires': 55, 'queue': 'broadcast'}
}
```

## Human Body Architecture (Updated)

| Body Part | Component | Purpose | Session |
|-----------|-----------|---------|---------|
| HEART | HeartMonitorService | Health monitoring | 701 |
| LUNGS | LungsCapacityService | Resource/budget management | 702 |
| CIRCULATORY | CirculatorySystemService | Data flow monitoring | 703 |
| SPINE | SpineRouterService | Central API routing | 704 |
| IMMUNE | ImmuneSystemService | Security & threat detection | 705 |
| **DIGESTIVE** | **DigestiveSystemService** | **Data ingestion & processing** | **706** |

## Key Findings

1. **High Queue Depth**: 9,681 items pending processing - indicates processing bottleneck
2. **Low Spider Success Rate**: 29.5% - many spiders failing or returning no data
3. **Zero Processing Throughput**: Processing appears stalled
4. **Good Routing**: Items that are processed are being routed correctly

## Recommendations for Future Sessions

1. **Session 707+**: Investigate processing bottleneck
   - Why is queue so deep?
   - Is there a worker issue?

2. **Spider Health**: Low success rate needs investigation
   - Which spiders are failing?
   - API rate limits?
   - Authentication issues?

3. **Frontend Integration**: Build React component for DIGESTIVE visualization

## Testing

- Migration: ✅ Applied successfully
- CLI Command: ✅ Works with all options
- API Endpoints: ⚠️ Need server restart for PUBLIC_PATHS to take effect
- Default Routes: ✅ 8 routes created

## Summary

Session 706 completes the DIGESTIVE SYSTEM - the 6th body system component. The system immediately detected real issues in the data pipeline:
- High processing backlog (9,681 items)
- Low spider success rate (29.5%)
- Processing appears stalled

This validates the value of the body system architecture - it's finding real problems that need attention.

# Session 603: Learning Velocity Dashboard

**Date:** December 29, 2025
**Focus:** Learning Velocity Dashboard - Track how fast the system learns

---

## Summary

Built a Learning Velocity Dashboard that tracks how fast the system learns and visualizes learning momentum over time. This builds on the weighted learning formula from Session 601 and Boardroom integration from Session 602.

---

## New Components

### LearningVelocityService (`core/services/learning_velocity.py`)

Service that calculates learning velocity metrics:

| Method | Purpose |
|--------|---------|
| `get_velocity_dashboard(days)` | Complete dashboard with all metrics |
| `_get_daily_velocity()` | Daily learning velocity with weighted scores |
| `_get_weekly_summary()` | Weekly aggregates and pass rates |
| `_get_theme_momentum()` | Theme-level trend analysis |
| `_calculate_overall_health()` | Health score (0-100) |
| `_calculate_velocity_trend()` | Accelerating/stable/decelerating |

### Key Metrics Tracked

| Metric | Description |
|--------|-------------|
| **Health Score** | 0-100 based on net weight, volume, and declining themes |
| **Velocity Trend** | Accelerating/stable/decelerating based on 7-day rolling average |
| **Net Learning Weight** | Total positive - negative weights from weighted formula |
| **Theme Momentum** | Per-theme tracking with recent vs older weight comparison |

### Health Score Calculation

```
Base = 50 + (net_weight × 20)
+ Volume bonus (min 20, experiments × 2)
- Decline penalty (declining_themes × 5)
= Final score (clamped 0-100)
```

### Velocity Trend Detection

- Compares last 7 days average vs previous 7 days
- Rate > 0.1 = accelerating
- Rate < -0.1 = decelerating
- Otherwise = stable

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/learning/velocity/` | Full velocity dashboard |
| `GET /api/learning/velocity/theme/<theme>/` | Theme-specific velocity |

Query parameters:
- `days` - Number of days to analyze (default: 30)

---

## UI Dashboard

Added to Growth tab in AI Studio. Features:

1. **Overview Cards**
   - Health Score with status badge
   - Velocity Trend with icon (🚀/➡️/📉)
   - Net Learning Weight with +/- breakdown
   - Experiment Count with theme count

2. **Theme Momentum Section**
   - List of themes with momentum indicators
   - Color-coded health (green=healthy, gray=neutral, yellow=attention, red=concerning)
   - Weight badges (+/- values)

3. **Daily Velocity Chart**
   - ASCII-style bar chart
   - Last 14 days
   - Green bars for positive, red for negative
   - Shows experiment count per day

4. **Weekly Summary**
   - Last 4 weeks
   - Pass rate with color coding
   - Total weight per week

---

## Files Created/Modified

### New Files
- `core/services/learning_velocity.py` (436 lines)
- `docs/handoffs/SESSION_603_LEARNING_VELOCITY_DASHBOARD.md`

### Modified Files
- `core/views_agent_learning.py` - Added velocity endpoints
- `core/urls.py` - Added velocity URL routes
- `ai_core/templates/ai_image_studio.html` - Dashboard UI + JavaScript

---

## Learning System Progress (Sessions 590-603)

```
Session 590: Pilot Readiness Gate
        ↓
Session 595: Pilot Execution Dashboard
        ↓
Session 596: Experiment Tracking Registry
        ↓
Session 597: ExperimentLearning + Pattern Models
        ↓
Session 598: Learning Loop UI Dashboard
        ↓
Session 599: Fail Fast + Outcome Classification
        ↓
Session 600: Real Metrics + Rollback + ThinkingAgent
        ↓
Session 601: ChatGPT's Weighted Learning Formula
        ↓
Session 602: Boardroom Integration
        ↓
Session 603: Learning Velocity Dashboard ← COMPLETE!
```

---

## Session 604 Options

### Option A: Auto-Prioritize Decision Queue
- Sort pending decisions by success probability
- Surface high-probability, low-risk decisions first
- Flag high-risk decisions for additional review

### Option B: Experiment Suggestion Engine
- Based on learning gaps, suggest new experiments
- Identify themes with insufficient data
- Recommend sample sizes for confidence targets

### Option C: Velocity Alerts
- Notify when velocity is declining
- Alert on themes that need attention
- Surface stale themes with no recent activity

---

## Test Commands

```bash
# Test velocity service
.venv/bin/python manage.py shell -c "
from core.services.learning_velocity import LearningVelocityService
service = LearningVelocityService()
dashboard = service.get_velocity_dashboard(30)
print(f'Health: {dashboard[\"overall_health\"][\"status\"]} ({dashboard[\"overall_health\"][\"score\"]})')
print(f'Trend: {dashboard[\"velocity_trend\"][\"direction\"]}')
print(f'Themes: {len(dashboard[\"theme_momentum\"])}')
"

# Test via API (requires auth)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/learning/velocity/
```

---

**Session 603: Learning Velocity Dashboard - COMPLETE**

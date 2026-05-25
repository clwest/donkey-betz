# Session 345: Intelligence Hub Dynamic Stats & Auto-Loading

**Date:** December 4, 2025
**Status:** Complete
**Focus:** Fix hardcoded/wrong values in Intelligence Hub UI, implement single source of truth API

---

## Problem

The Intelligence Hub UI was displaying hardcoded or incorrect values throughout:

| Stat | Wrong Value | Correct Value |
|------|-------------|---------------|
| Agents | 14 or 197 | **79** |
| Categories | 21 | **36** |
| Data Points | 914 | **9,779** |
| Spiders | (sometimes wrong) | **102** |
| Success Rate | -- | **98%** |

Values were hardcoded in HTML and never updated dynamically.

---

## Solution: Single Source of Truth API

### 1. Created Dashboard Stats API Endpoint

**File:** `core/views_spider_intelligence.py` (lines 714-792)

```python
@csrf_exempt
@require_http_methods(["GET"])
def dashboard_stats(request):
    """
    Session 345: Single source of truth for Intelligence Hub stats.
    Returns all dashboard statistics from actual data sources.
    """
```

**Endpoint:** `GET /api/spider-intelligence/dashboard-stats/`

**Response:**
```json
{
  "status": "success",
  "stats": {
    "spiders": {"total": 102, "categories": 36, "by_category": {...}},
    "agents": {"total": 79, "legacy": 69, "clean": 10},
    "data": {"total_points": 9779, "last_24h": 1246, "success_rate": 98}
  }
}
```

### 2. Added URL Route with Import Alias

**File:** `core/urls.py`

To avoid name conflict with existing `dashboard_stats` from `views_dashboard_stats.py`:

```python
# Line 138 - Import with alias
from core.views_spider_intelligence import dashboard_stats as spider_dashboard_stats

# Line 2215 - Route
path('api/spider-intelligence/dashboard-stats/', spider_dashboard_stats, name='spider-intelligence-dashboard-stats'),
```

### 3. Frontend JavaScript Functions

**File:** `ai_core/templates/ai_image_studio.html` (lines 15712-15782)

```javascript
// Dashboard stats cache
let dashboardStatsCache = null;
let dashboardStatsCacheTime = 0;
const DASHBOARD_STATS_CACHE_TTL = 30000; // 30 seconds

async function loadDashboardStats() {
    // Fetches from /api/spider-intelligence/dashboard-stats/
    // Caches for 30 seconds to avoid redundant calls
}

function updateDashboardStatsUI(stats) {
    // Updates all stat elements across the UI:
    // - Spider count
    // - Category count
    // - Agent count
    // - Data points
    // - Success rate
}
```

### 4. Auto-Loading Event Listeners

**File:** `ai_core/templates/ai_image_studio.html` (lines 16043-16062)

```javascript
// Session 345: Auto-load subtab content when tab becomes visible
document.addEventListener('DOMContentLoaded', function() {
    // Load Trending when Intelligence Hub panel opens
    const intelligenceHubTab = document.getElementById('agents-intelligence-tab');
    if (intelligenceHubTab) {
        intelligenceHubTab.addEventListener('shown.bs.tab', function() {
            loadTrendingTab();
        });
    }

    // Also load when switching between subtabs
    const trendingTab = document.getElementById('intel-trending-tab');
    if (trendingTab) {
        trendingTab.addEventListener('shown.bs.tab', function() {
            loadTrendingTab();
        });
    }
});
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/views_spider_intelligence.py` | Added `dashboard_stats()` endpoint (lines 714-792) |
| `core/urls.py` | Added import alias (line 138) and route (line 2215) |
| `ai_core/templates/ai_image_studio.html` | Removed hardcoded values, added JS functions, auto-loading |
| `00-START-NEXT-SESSION.md` | Updated with session summary |

---

## UI Elements Updated

All these elements now show `--` until API loads, then display live data:

1. **Top Stats Row:**
   - Total Spiders (id: varies)
   - Categories count
   - Data Points count
   - Success Rate

2. **Intelligence Hub Panel:**
   - Agent count badges
   - Spider count badges
   - Category count badges

3. **Trending Subtab:**
   - Quick Stats sidebar
   - Active Sources count

---

## Testing

### Verify API
```bash
curl http://localhost:8000/api/spider-intelligence/dashboard-stats/
```

### Expected Response
```json
{
  "status": "success",
  "stats": {
    "spiders": {"total": 102, "categories": 36},
    "agents": {"total": 79, "legacy": 69, "clean": 10},
    "data": {"total_points": 9779, "last_24h": 1246, "success_rate": 98}
  }
}
```

### UI Verification
1. Open http://localhost:8000/ai-studio/
2. Click Intelligence Hub tab
3. Verify all stats show correct values (not hardcoded)
4. Check Trending, Markets, Opportunities, Spiders tabs load data

---

## Current System State (Post-Session)

| Component | Count |
|-----------|-------|
| **Spiders** | 102 |
| **Categories** | 36 |
| **Agents** | 79 (69 legacy + 10 clean) |
| **Data Points** | 9,779 |
| **Success Rate** | 98% |

---

## Next Steps

1. Add auto-loading for other subtabs (Markets, Opportunities, Spiders)
2. Consider longer cache TTL for less frequent updates
3. Add WebSocket for real-time stat updates (optional)

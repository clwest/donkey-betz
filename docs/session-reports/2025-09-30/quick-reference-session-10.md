# Quick Reference - Session 10 Fixes

## 🚀 Quick Start Commands

```bash
# Start server
make stop && make start

# Load real job data (if empty)
python manage.py shell << 'EOF'
import json
from django.core.cache import cache
with open('spider_results.json', 'r') as f:
    spider_data = json.load(f)
opportunities = spider_data.get('opportunities', [])
cache.set('latest_opportunities', opportunities, 3600)
print(f'Loaded {len(opportunities)} opportunities')
EOF

# Verify everything works
curl -I http://localhost:8000/income/ | grep Location  # Should show redirect
```

## 🔧 Key Files & Line Numbers

### `/core/templates/unified/revenue_opportunities.html`
- **Lines 271-323**: Spider Network & Earnings Projection controls (NEW)
- **Lines 639-658**: Salary display logic (FIXED)
- **Lines 668-674**: Match score & priority display (FIXED)
- **Lines 714-762**: Custom notification system (REPLACED Bootstrap)
- **Lines 771 & 841**: Template literal backticks (FIXED)
- **Lines 1192-1266**: activateSpiders & analyzeOpportunities functions (NEW)
- **Lines 1252**: opportunitiesGrid ID fix (FIXED)

### `/core/views_unified.py`
- **Lines 52-63**: IncomeBuilderView redirect implementation

### `/core/routing.py`
- **Line 280**: WebSocket routing for income-builder → RevenueOpportunitiesConsumer

## 🐛 Common Issues & Fixes

### Problem: "No opportunities showing"
```bash
# Reload cache from spider_results.json
python manage.py shell -c "
import json; from django.core.cache import cache
with open('spider_results.json') as f: data = json.load(f)
cache.set('latest_opportunities', data['opportunities'], 3600)
"
```

### Problem: "JavaScript errors in console"
- Bootstrap toast error → Fixed with custom notification
- Null element error → Fixed with correct ID: `opportunitiesGrid`
- Template literal syntax → Fixed escaped backticks

### Problem: "All jobs show $0"
- Fixed: Now uses `salary_min/salary_max` fields
- Shows ranges like "$180k-260k" or "Salary TBD"

### Problem: "All jobs show 0% match"
- Fixed: Now uses `match_score` field from data
- Shows real percentages: 18%, 36%, etc.

## 📊 Data Structure Reference

### Real Job Object Fields:
```javascript
{
  source: "RemoteOK",
  title: "Staff Backend Engineer",
  company: "OnePay",
  salary_min: 180000,        // Used for salary display
  salary_max: 260000,        // Used for salary display
  match_score: 0.3636,       // Used for match % and priority
  url: "https://...",
  description: "...",
  tags: ["python", "django"],
  date_posted: "2025-09-27",
  location: "Remote",
  application_url: "..."
}
```

## 🎯 URLs & Access Points

- **Consolidated Interface**: `http://localhost:8000/opportunities/`
- **Legacy (redirects)**: `http://localhost:8000/income/`
- **WebSocket (both work)**:
  - `ws://localhost:8000/ws/revenue-opportunities/`
  - `ws://localhost:8000/ws/income-builder/`

## ✅ What's Working Now

1. **Single consolidated interface** at `/opportunities/`
2. **Real job data** (50 opportunities from 4 sources)
3. **Actual salary ranges** ($70k-260k, not $0)
4. **Real match scores** (18%, 36%, not 0%)
5. **Dynamic priorities** based on match scores
6. **Enhanced modal** with salary extraction
7. **Spider Network controls** integrated
8. **Custom notifications** (no Bootstrap dependency)
9. **Proper redirects** from `/income/`
10. **Clean JavaScript** (no console errors)

## 🔮 Ready for Next Phase

The platform is **ready for user profiling**:
- Infrastructure exists for personalized matching
- `analyzeOpportunities()` sends user profile
- Match scoring can use user skills/experience
- Priority assignment can be personalized

Just needs the AI interview system to gather user data!
# ☀️ Morning Checklist - October 2, 2025

## Quick Start (5 minutes)

### 1. Check Spider Health 🕷️
```bash
# Are spiders still running?
ps aux | grep deploy_spiders

# Check last 20 log entries
tail -20 spider_deployment_*.log
```

**Expected:** Process running, recent log activity, no fatal errors

---

### 2. Check Real Data Collection 📊
```bash
python manage.py shell -c "
from persistence.models import SpiderData
print(f'Spider data collected: {SpiderData.objects.count()} items')
"
```

**Expected:** > 0 items (was 0 at bedtime)

---

### 3. Test Opportunity Detail Page 🎯
1. Open: `http://localhost:8000/income/`
2. Log in as: `chris`
3. Click: "📋 View Details" on any card
4. Verify: Page shows opportunity details (not blank, not API page)

**Expected:** Detail page loads with full opportunity data

---

## If Everything Looks Good ✅

You're done! Read `SESSION_COMPLETE_2025-10-01_NIGHT.md` for full details.

---

## If Issues Found ❌

### Issue: No Real Data Collected
**Check:**
```bash
tail -50 spider_deployment_*.log | grep ERROR
```

**Common Causes:**
- API keys expired
- Network connectivity issues
- Rate limiting

**Fix:** Check specific error messages, may need to restart spiders

---

### Issue: Detail Page Still Broken
**Check:**
```bash
# Check Django logs
tail -50 /path/to/django.log

# Check browser console for JS errors
# Open: http://localhost:8000/income/
# Press F12, check Console tab
```

**Common Causes:**
- Not logged in (see 302 redirect)
- JavaScript errors
- Template rendering issues

**Fix:** Ensure logged in, check console for specific error

---

### Issue: Spiders Stopped
**Check:**
```bash
ps aux | grep deploy_spiders
```

**Fix: Restart Spiders**
```bash
python manage.py deploy_spiders &
```

---

## Next Steps (Priority Order)

1. ✅ Verify fixes from last night are working
2. 🔍 Review real data collected by spiders
3. 🗑️ Remove seed data (if real data looks good)
4. 🎨 Fix sports betting card template
5. 📱 Test full user workflow
6. 🚀 Plan next features

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `SESSION_COMPLETE_2025-10-01_NIGHT.md` | Full session documentation |
| `spider_deployment_*.log` | Spider activity logs |
| `core/views_unified.py:697-730` | Opportunity detail view (FIXED) |
| `core/templates/unified/income_builder.html` | Income builder UI (FIXED) |
| `ai_core/spiders/spider_registry.py` | Spider configuration (MODIFIED) |

---

## Emergency Contacts (If Stuck)

**Question:** "Did we actually fix the routing issue?"
**Answer:** YES! Changed `redirect('income_builder')` to `redirect('unified_income_builder')` in 3 places

**Question:** "Why is the page blank?"
**Answer:** Make sure you're logged in! View requires authentication.

**Question:** "Is this real data or seed data?"
**Answer:** Check timestamp. Seed data = 03:36:04. Real data = newer timestamps.

**Question:** "Should I see TradingView errors?"
**Answer:** NO! We disabled it last night. If you see them, something reverted.

---

**📖 For full details, read:** `SESSION_COMPLETE_2025-10-01_NIGHT.md`

**🕷️ Spiders deployed:** 1,770
**🤖 Agents active:** 154
**🧠 Advisors active:** 25
**⏰ Deployed at:** 11:18 PM, Oct 1, 2025

**Sleep well! See you in the morning! 🌅**

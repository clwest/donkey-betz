# 🕷️ Spider Recovery & Deployment Plan
## Complete Guide to Getting Real Data Collection Working

**Created:** October 2, 2025, Late Afternoon
**Status:** Ready for Implementation
**Priority:** HIGH - No real data being collected

---

## 📋 Table of Contents

1. [Current Situation Overview](#current-situation-overview)
2. [Root Cause Analysis](#root-cause-analysis)
3. [Session-by-Session Implementation Plan](#session-by-session-implementation-plan)
4. [Technical Details](#technical-details)
5. [Success Metrics](#success-metrics)
6. [Troubleshooting Guide](#troubleshooting-guide)

---

## Current Situation Overview

### What's Working ✅
- **Django Server**: Running perfectly on localhost:8000
- **Database**: PostgreSQL healthy with 8 seed opportunities
- **Redis**: Running with 1,550 spiders registered
- **Opportunity Detail Page**: Fixed last night, working correctly
- **Income Builder UI**: Fully functional frontend
- **Spider Registry**: 39 spider classes registered in codebase
- **Infrastructure**: All core services operational

### What's Not Working ❌
- **Spider Data Collection**: 0 items collected (SpiderData table empty)
- **Active Crawling**: Spiders registered but not executing
- **Celery Deployment**: Management command has deadlock bug
- **Real Opportunities**: Still showing only 8 seed opportunities from Oct 1

### The Gap
**We have the infrastructure, but the spiders aren't actually crawling websites and collecting data.**

---

## Root Cause Analysis

### Issue #1: Celery Deadlock (CRITICAL)

**Location:** `ai_core/spiders/management/commands/deploy_spiders.py:140`

**Problem Code:**
```python
# Line 140 - This causes deadlock!
result = deploy_spider_swarm_task.delay(swarm_data)
deployment = result.get(timeout=120)  # ❌ BLOCKS AND DEADLOCKS
```

**Why It Fails:**
- Calling `.get()` on a Celery AsyncResult blocks execution
- If this runs within a Celery worker context, it creates a circular wait
- The worker waits for a task that's waiting for the worker
- Result: Deadlock, spiders never deploy

**Impact:**
- Last night's `python manage.py deploy_spiders` command failed
- No spiders started crawling
- No data collected overnight

**Evidence:**
```bash
# Error from logs:
Deployment failed: Never call result.get() within a task!
```

---

### Issue #2: Registration vs Execution

**Problem:** Two different concepts being confused

**Registration** (✅ Working):
- Spider classes are defined in code
- Spiders are "registered" in Redis as available
- System knows spiders exist
- **Current Status:** 1,550 spiders registered

**Execution** (❌ Not Working):
- Actual worker processes running spider tasks
- Crawling websites, fetching data
- Processing and storing results
- **Current Status:** 0 spiders actively crawling

**The Missing Piece:**
We need worker processes that:
1. Read registered spiders from Redis
2. Execute their crawl methods
3. Collect and store data
4. Handle errors and retries
5. Respect rate limits

---

### Issue #3: Incomplete Spider Implementation

**Registered:** 39 spider classes in code
**Actually Usable:** Only 13 classes have implementations

**Available Spider Types:**
1. toptal
2. guru
3. peopleperhour
4. ninetyninedesigns
5. flexjobs
6. remoteok
7. financial
8. market_data
9. innovation
10. social_sentiment
11. news_harvester
12. medium
13. gumroad

**Missing/Incomplete:** 26 spider classes registered but not fully implemented

---

## Session-by-Session Implementation Plan

### 🎯 Session 1: Verification & Assessment (30-45 min)
**Goal:** Understand exactly what we have and what's missing

#### Tasks:
1. **Verify Redis Status**
   - Check registered spiders count
   - Verify spider metadata
   - Check for any existing tasks

2. **Check Running Processes**
   - Look for any active spider processes
   - Verify Celery workers status
   - Check Django-Q or other task runners

3. **Analyze Celery Code**
   - Review the deadlock issue in detail
   - Identify all `.get()` calls that need fixing
   - Document the current deployment flow

4. **Database Assessment**
   - Confirm SpiderData table is empty (0 rows)
   - Verify OpportunityTracking still has only 8 seed items
   - Check table schemas are correct

5. **Create Assessment Report**
   - Document findings
   - Identify quickest path to working spiders
   - Recommend immediate vs future fixes

**Deliverables:**
- ✅ Complete status report
- ✅ List of what needs fixing
- ✅ Recommended approach for Session 2

**Success Criteria:**
- Know exact spider count in Redis
- Understand which spiders are usable
- Clear picture of deployment issues
- Decision on fix approach

---

### 🔧 Session 2: Fix Celery Deployment (1-2 hours)
**Goal:** Fix the deadlock issue so spiders can deploy properly

#### Option A: Fix Celery Command (Recommended)
**Approach:** Remove blocking `.get()` calls, use async patterns

**Tasks:**
1. **Backup Current Code**
   ```bash
   cp ai_core/spiders/management/commands/deploy_spiders.py \
      ai_core/spiders/management/commands/deploy_spiders.py.backup
   ```

2. **Remove Synchronous Calls**
   - Replace `result.get(timeout=120)` with fire-and-forget
   - Use Celery's `link` or `chain` for task coordination
   - Or switch to async/await pattern

3. **Implement Proper Error Handling**
   ```python
   # Instead of:
   result = task.delay(data)
   deployment = result.get()  # ❌ Blocks

   # Use:
   result = task.delay(data)
   # Don't wait, let task complete independently
   # Check status later via result.ready() if needed
   ```

4. **Add Status Tracking**
   - Store deployment status in Redis or database
   - Create endpoint to check deployment progress
   - Add logging for debugging

5. **Test Deployment**
   ```bash
   python manage.py deploy_spiders
   # Should complete without deadlock
   ```

**Code Changes Required:**
- `ai_core/spiders/management/commands/deploy_spiders.py` (Lines ~130-150)
- Possibly add new status tracking model or Redis keys

**Deliverables:**
- ✅ Fixed deployment command
- ✅ Test results showing successful deployment
- ✅ Documentation of changes

---

#### Option B: Create Direct Orchestrator Script (Faster)
**Approach:** Bypass Celery, use direct Python script

**Tasks:**
1. **Create New Deployment Script**
   ```python
   # scripts/deploy_spiders_working.py
   # Use Spider Army Orchestrator directly
   # No Celery, just Python multiprocessing or asyncio
   ```

2. **Implement Spider Execution**
   - Load registered spiders from Redis
   - Create worker pool (multiprocessing)
   - Execute spider crawl methods
   - Store results directly in database

3. **Add Process Management**
   - Track running spiders
   - Handle crashes/restarts
   - Implement rate limiting
   - Add health checks

4. **Test with Small Subset**
   ```bash
   python scripts/deploy_spiders_working.py --limit 10
   # Run only 10 spiders as test
   ```

**Deliverables:**
- ✅ New working deployment script
- ✅ Process management system
- ✅ Test results with 10 spiders

**Recommendation:** Start with Option B (faster, simpler), fix Option A later

---

### 🚀 Session 3: Enable Spider Crawling (2-3 hours)
**Goal:** Get spiders actually crawling and collecting data

#### Tasks:

1. **Create Spider Worker Process**
   ```python
   # scripts/spider_worker.py
   # Continuously executes registered spiders
   # Respects rate limits and priorities
   ```

2. **Implement Crawl Loop**
   ```python
   while True:
       # Get next spider to execute
       spider = get_next_spider_from_redis()

       # Execute crawl
       data = spider.crawl()

       # Store results
       SpiderData.objects.create(
           spider_name=spider.name,
           data=data,
           source=spider.source
       )

       # Sleep per rate limit
       time.sleep(spider.rate_limit)
   ```

3. **Add Error Handling**
   - Try/catch around spider execution
   - Log errors without crashing
   - Retry failed spiders
   - Skip permanently broken spiders

4. **Implement Rate Limiting**
   - Per-spider rate limits
   - Per-domain rate limits
   - Global rate limiting
   - Respect robots.txt

5. **Add Health Monitoring**
   - Track successful/failed crawls
   - Monitor memory usage
   - Check response times
   - Alert on issues

6. **Test Data Collection**
   ```bash
   # Start worker in background
   python scripts/spider_worker.py &

   # Wait 5 minutes

   # Check results
   python manage.py shell -c "
   from persistence.models import SpiderData
   print(f'Collected: {SpiderData.objects.count()} items')
   "
   ```

**Code Changes Required:**
- New file: `scripts/spider_worker.py`
- Possibly update spider base classes for consistent interface

**Deliverables:**
- ✅ Working spider worker process
- ✅ Data appearing in SpiderData table
- ✅ Health monitoring dashboard

**Success Criteria:**
- SpiderData table has 10+ rows within 10 minutes
- No crashes or deadlocks
- Proper error logging
- Rate limits respected

---

### 📊 Session 4: Data Processing Pipeline (1-2 hours)
**Goal:** Convert spider data into opportunities

#### Tasks:

1. **Verify Opportunity Creation**
   - Check if OpportunityTracking gets new rows automatically
   - Or if we need to create opportunity processor

2. **Create Data Processor (if needed)**
   ```python
   # scripts/process_spider_data.py
   # Reads SpiderData entries
   # Converts to OpportunityTracking records
   ```

3. **Implement Opportunity Logic**
   - Parse spider data by type
   - Extract relevant fields
   - Calculate match scores
   - Create opportunities

4. **Test Pipeline End-to-End**
   ```bash
   # 1. Verify spider collected data
   # 2. Run processor
   # 3. Check opportunities created
   # 4. View in Income Builder UI
   ```

5. **Add Deduplication**
   - Don't create duplicate opportunities
   - Update existing if data changed
   - Archive old/expired opportunities

**Deliverables:**
- ✅ Data processing pipeline
- ✅ New opportunities appearing
- ✅ Visible in Income Builder UI

**Success Criteria:**
- OpportunityTracking has 5+ new opportunities
- Opportunities visible in /income/ page
- Detail pages work for new opportunities
- Match scores are realistic

---

### 🎯 Session 5: Full Deployment & Monitoring (1-2 hours)
**Goal:** Deploy all spiders and monitor for issues

#### Tasks:

1. **Deploy All Spiders**
   ```bash
   # Deploy all 1,550 registered spiders
   python scripts/deploy_spiders_working.py --all
   ```

2. **Monitor Initial Collection**
   - Watch for first 30 minutes
   - Check error rates
   - Verify data quality
   - Monitor resource usage

3. **Create Monitoring Dashboard**
   - Spider execution stats
   - Data collection rates
   - Error tracking
   - Opportunity creation rates

4. **Optimize Performance**
   - Adjust worker count
   - Tune rate limits
   - Fix common errors
   - Improve efficiency

5. **Verify Opportunity Flow**
   - Check Income Builder shows new opportunities
   - Test detail pages with real data
   - Verify sports betting cards render
   - Confirm match scores work

**Deliverables:**
- ✅ All spiders deployed and running
- ✅ Monitoring dashboard operational
- ✅ Real opportunities in Income Builder

**Success Criteria:**
- 50+ SpiderData entries per hour
- 5-10 new opportunities per hour
- Error rate < 10%
- No system crashes
- Income Builder shows real data

---

### 🔄 Session 6: Replace Seed Data (30 min)
**Goal:** Remove mock data, use only real data

#### Tasks:

1. **Verify Real Data Exists**
   ```bash
   python manage.py shell -c "
   from intelligence.models import OpportunityTracking
   real_opps = OpportunityTracking.objects.filter(
       created_at__gte='2025-10-02 00:00:00'
   ).count()
   print(f'Real opportunities: {real_opps}')
   "
   ```

2. **Backup Seed Data**
   ```bash
   python manage.py dumpdata intelligence.OpportunityTracking \
       --indent 2 > seed_data_backup.json
   ```

3. **Delete Seed Data**
   ```python
   # Delete only seed data from Oct 1
   OpportunityTracking.objects.filter(
       created_at__lt='2025-10-02 00:00:00'
   ).delete()
   ```

4. **Verify UI Still Works**
   - Open /income/ page
   - Should show only real opportunities
   - Test detail pages
   - Confirm everything functional

**Deliverables:**
- ✅ Seed data removed
- ✅ Only real data in system
- ✅ UI working with real data

---

### 🏗️ Session 7: Enable Remaining Spiders (2-3 hours)
**Goal:** Implement the 26 missing spider classes

#### Tasks:

1. **Identify Missing Spiders**
   - List all 39 registered classes
   - Mark which 13 are working
   - Identify which 26 need implementation

2. **Prioritize Implementation**
   - High value: LinkedIn, Upwork, Indeed
   - Medium value: SEC.gov (when ready), financial platforms
   - Low value: Nice-to-have platforms

3. **Implement Top 5 Missing Spiders**
   - Create spider class
   - Implement crawl method
   - Add data parsing
   - Test independently

4. **Register and Deploy**
   ```bash
   # Register new spiders
   python scripts/simple_spider_deploy.py

   # Deploy workers
   python scripts/spider_worker.py
   ```

5. **Verify Data Collection**
   - Check SpiderData for new sources
   - Verify opportunity creation
   - Test data quality

**Deliverables:**
- ✅ 5 new working spider classes
- ✅ Total usable spiders: 18
- ✅ More data sources feeding system

---

### 🔧 Session 8: Fix Sports Betting Card (1 hour)
**Goal:** Make sports betting opportunities render with special template

#### Issue:
The sports betting card template (lines 540-586 in income_builder.html) never renders because:
- Opportunities have `opportunity_type: "freelance"`
- Template checks for `opportunity_type === 'sports_bet'`

#### Tasks:

1. **Option A: Fix Data Model**
   ```python
   # In opportunity creation logic
   if opportunity_is_sports_bet:
       opportunity_type = 'sports_bet'  # ✅ Use correct type
   ```

2. **Option B: Update Template**
   ```javascript
   // Check both fields
   if ((opp.opportunity_type === 'sports_bet' ||
        opp.stream_type === 'Sports Bet') &&
        opp.opportunity_data) {
       // Render sports card
   }
   ```

3. **Test Sports Cards**
   - Create test sports betting opportunity
   - Verify special card renders
   - Check odds display works
   - Confirm "View Analysis" button works

**Deliverables:**
- ✅ Sports betting cards render correctly
- ✅ All sports data displayed properly
- ✅ Special UI elements working

---

### 🏛️ Session 9: Re-enable SEC.gov (When Ready)
**Goal:** Add SEC.gov spiders back after personal issues resolved

#### Files to Update:

1. **ai_core/spiders/spider_registry.py**
   ```python
   # Line 53: Add back sec.gov
   'targets': ['sec.gov', 'finance.yahoo.com', 'polygon.io']
   ```

2. **ai_core/spiders/spider_army_orchestrator.py**
   ```python
   # Line 114: Uncomment SEC.gov target
   financial_targets = [
       SpiderTarget("https://www.sec.gov/edgar/search/",
                   rate_limit=0.5, priority=1),
       ...
   ]
   ```

3. **ai_core/spiders/specialized/financial_spider.py**
   ```python
   # Lines 71-73: Uncomment SEC.gov processing
   if 'sec.gov' in target.url:
       return await self._process_sec_filing(raw_data, target)
   ```

4. **Redeploy Spiders**
   ```bash
   python scripts/deploy_spiders_working.py
   ```

**Deliverables:**
- ✅ SEC.gov data collection restored
- ✅ Financial intelligence enhanced

---

### 🎓 Session 10: Documentation & Optimization (1-2 hours)
**Goal:** Document everything and optimize performance

#### Tasks:

1. **Create Spider Documentation**
   - How to add new spiders
   - Spider development guide
   - Troubleshooting guide
   - Best practices

2. **Performance Optimization**
   - Profile slow spiders
   - Optimize database queries
   - Implement caching
   - Reduce memory usage

3. **Add Monitoring Alerts**
   - Email on critical errors
   - Slack notifications
   - Performance degradation alerts
   - Data quality checks

4. **Create Admin Dashboard**
   - View spider status
   - Pause/resume spiders
   - View error logs
   - Monitor data collection

**Deliverables:**
- ✅ Complete documentation
- ✅ Optimized performance
- ✅ Admin dashboard
- ✅ Alerting system

---

## Technical Details

### Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Django Server                        │
│                   (localhost:8000)                       │
└─────────────────────────────────────────────────────────┘
                            │
                            ├── Income Builder UI ✅
                            ├── Opportunity Detail ✅
                            ├── Decision Command ✅
                            └── Revenue Dashboard ✅

┌─────────────────────────────────────────────────────────┐
│                      PostgreSQL                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ├── SpiderData (0 rows) ❌
                            ├── OpportunityTracking (8 seed rows) ⚠️
                            └── Other tables ✅

┌─────────────────────────────────────────────────────────┐
│                        Redis                             │
└─────────────────────────────────────────────────────────┘
                            │
                            └── Registered Spiders: 1,550 ✅

┌─────────────────────────────────────────────────────────┐
│                    Spider Registry                       │
│              (39 classes, 13 usable)                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Celery Workers                         │
│                  (Deadlocked) ❌                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Spider Execution                        │
│                  (NOT RUNNING) ❌                        │
└─────────────────────────────────────────────────────────┘
```

### Target Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Django Server                        │
│                   (localhost:8000)                       │
└─────────────────────────────────────────────────────────┘
                            │
                            └── All UIs working ✅

┌─────────────────────────────────────────────────────────┐
│                      PostgreSQL                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ├── SpiderData (100s of rows) ✅
                            └── OpportunityTracking (Real data) ✅

┌─────────────────────────────────────────────────────────┐
│                        Redis                             │
└─────────────────────────────────────────────────────────┘
                            │
                            ├── Registered Spiders: 1,550+ ✅
                            └── Task Queue ✅

┌─────────────────────────────────────────────────────────┐
│                Spider Worker Processes                   │
│              (Multiple workers running)                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ├── Worker 1: Financial spiders
                            ├── Worker 2: Job board spiders
                            ├── Worker 3: Freelance spiders
                            └── Worker 4: Crypto/Innovation

┌─────────────────────────────────────────────────────────┐
│                   Data Pipeline                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ├── Collect (Spiders) ✅
                            ├── Store (SpiderData) ✅
                            ├── Process (Create Opportunities) ✅
                            └── Display (Income Builder) ✅
```

---

## Success Metrics

### Session-by-Session Goals

**Session 1 (Verification):**
- [ ] Know exact Redis spider count
- [ ] Understand deployment issue
- [ ] Clear fix strategy identified

**Session 2 (Fix Deployment):**
- [ ] Deployment command runs without errors
- [ ] No Celery deadlocks
- [ ] Can deploy spiders successfully

**Session 3 (Enable Crawling):**
- [ ] Spider worker process running
- [ ] SpiderData table has 10+ rows
- [ ] No crashes or errors

**Session 4 (Data Pipeline):**
- [ ] OpportunityTracking has new rows
- [ ] Opportunities visible in UI
- [ ] Detail pages work with real data

**Session 5 (Full Deployment):**
- [ ] 50+ SpiderData entries per hour
- [ ] 5-10 new opportunities per hour
- [ ] Monitoring dashboard operational

**Session 6 (Replace Seed Data):**
- [ ] Only real data in system
- [ ] UI working perfectly
- [ ] All features functional

### Overall Success Criteria

**Minimum Success** (End of Session 5):
- ✅ Spiders actively crawling
- ✅ Real data in SpiderData table
- ✅ New opportunities appearing
- ✅ Income Builder shows real data
- ✅ No critical errors

**Good Success** (End of Session 7):
- ✅ All of above PLUS:
- ✅ 18+ spider classes working
- ✅ 100+ opportunities collected
- ✅ Multiple data sources active
- ✅ Sports betting cards working

**Excellent Success** (End of Session 10):
- ✅ All of above PLUS:
- ✅ 30+ spider classes working
- ✅ 500+ opportunities collected
- ✅ Admin dashboard operational
- ✅ Performance optimized
- ✅ Complete documentation

---

## Troubleshooting Guide

### Issue: Spiders Still Not Collecting Data

**Check:**
1. Are worker processes running?
   ```bash
   ps aux | grep spider_worker
   ```

2. Check worker logs
   ```bash
   tail -f logs/spider_worker.log
   ```

3. Verify Redis connection
   ```bash
   redis-cli ping
   ```

4. Test single spider manually
   ```bash
   python manage.py shell -c "
   from ai_core.spiders.specialized.financial_spider import FinancialSpider
   spider = FinancialSpider()
   data = spider.crawl()
   print(data)
   "
   ```

---

### Issue: Deployment Command Still Fails

**Check:**
1. Celery workers running?
   ```bash
   ps aux | grep celery
   ```

2. Check for syntax errors
   ```bash
   python manage.py check
   ```

3. Verify changes applied
   ```bash
   git diff ai_core/spiders/management/commands/deploy_spiders.py
   ```

4. Try alternative deployment
   ```bash
   python scripts/deploy_spiders_working.py
   ```

---

### Issue: Data Not Appearing in UI

**Check:**
1. SpiderData has entries?
   ```bash
   python manage.py shell -c "
   from persistence.models import SpiderData
   print(SpiderData.objects.count())
   "
   ```

2. Opportunities being created?
   ```bash
   python manage.py shell -c "
   from intelligence.models import OpportunityTracking
   recent = OpportunityTracking.objects.order_by('-created_at')[:5]
   for opp in recent:
       print(f'{opp.opportunity_id}: {opp.created_at}')
   "
   ```

3. Check data processor logs
   ```bash
   tail -f logs/data_processor.log
   ```

4. Manually trigger opportunity creation
   ```bash
   python scripts/process_spider_data.py
   ```

---

### Issue: High Error Rate

**Check:**
1. Which spiders are failing?
   ```bash
   # Check error logs by spider
   grep ERROR logs/spider_worker.log | cut -d' ' -f5 | sort | uniq -c
   ```

2. Common error types?
   ```bash
   # Check error messages
   grep ERROR logs/spider_worker.log | tail -20
   ```

3. Rate limiting issues?
   - Increase sleep time between requests
   - Reduce worker count
   - Implement backoff strategy

4. API key problems?
   - Verify API keys in settings
   - Check API quotas
   - Test API endpoints manually

---

### Issue: System Performance Degrading

**Check:**
1. Memory usage
   ```bash
   free -h
   ps aux --sort=-%mem | head -10
   ```

2. Database connections
   ```bash
   python manage.py shell -c "
   from django.db import connection
   print(connection.queries)
   "
   ```

3. Redis memory
   ```bash
   redis-cli info memory
   ```

4. Worker count too high?
   - Reduce number of workers
   - Implement worker pool limits
   - Add memory monitoring

---

## Quick Reference Commands

### Check System Status
```bash
# Spider data count
python manage.py shell -c "
from persistence.models import SpiderData
print(f'Spider data: {SpiderData.objects.count()}')
"

# Opportunity count
python manage.py shell -c "
from intelligence.models import OpportunityTracking
print(f'Opportunities: {OpportunityTracking.objects.count()}')
"

# Redis spider count
python manage.py shell -c "
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(f'Registered: {r.scard(\"active_spiders\")}')
"

# Running processes
ps aux | grep -E "(spider|celery)"
```

### Restart Services
```bash
# Kill all spider workers
pkill -f spider_worker

# Restart workers
python scripts/spider_worker.py &

# Restart Celery
pkill -f celery
celery -A unified_donkey_betz worker -l info &
```

### Emergency Reset
```bash
# Stop everything
pkill -f spider
pkill -f celery

# Clear Redis
redis-cli FLUSHDB

# Re-register spiders
python scripts/simple_spider_deploy.py

# Restart workers
python scripts/spider_worker.py &
```

---

## Important Files Reference

### Spider Code
- `ai_core/spiders/spider_registry.py` - Spider class registry
- `ai_core/spiders/spider_army_orchestrator.py` - Orchestration logic
- `ai_core/spiders/base_spider.py` - Base spider class
- `ai_core/spiders/specialized/` - Specific spider implementations

### Deployment
- `ai_core/spiders/management/commands/deploy_spiders.py` - Current (broken) deployment
- `scripts/simple_spider_deploy.py` - Working registration script
- `scripts/spider_worker.py` - (To be created) Worker process

### Data Models
- `persistence/models.py` - SpiderData model
- `intelligence/models.py` - OpportunityTracking model

### Templates
- `core/templates/unified/income_builder.html` - Income Builder UI

### Views
- `core/views_unified.py` - Opportunity views

---

## Next Steps After Completion

Once all spiders are working and collecting real data:

1. **User Profiles** - Store user skills and preferences
2. **Personalized Matching** - ML-based opportunity ranking
3. **Application Tracking** - Track which opportunities user applied to
4. **Revenue Attribution** - Track actual earnings
5. **Advisor Consultations** - Enable interaction with 25 advisors
6. **Mobile App** - React Native app for opportunities
7. **Advanced Analytics** - Success rates, earnings projections
8. **Automated Applications** - Auto-apply to matching opportunities

---

## Summary

**Current State:**
- Infrastructure: 100% working ✅
- Spider registration: 100% working ✅
- Spider execution: 0% working ❌
- Data collection: 0% working ❌

**Target State (After All Sessions):**
- Infrastructure: 100% working ✅
- Spider registration: 100% working ✅
- Spider execution: 100% working ✅
- Data collection: 100% working ✅

**Estimated Time:** 10-15 hours across 10 sessions

**Priority Order:**
1. Session 1: Verification (START HERE)
2. Session 2: Fix deployment
3. Session 3: Enable crawling
4. Session 4: Data pipeline
5. Session 5: Full deployment
6. Remaining sessions as time permits

---

**Ready to begin Session 1: Verification!** 🚀

Let's get those spiders crawling and collecting real data!

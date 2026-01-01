# Session Roadmap: Fixing Disconnected Infrastructure

**Created:** December 31, 2025 (Session 646)
**Source:** SESSION_646_DISCONNECTED_FEATURES_AUDIT.md
**Estimated Sessions:** 5-7

---

## Overview

Breaking down the disconnected infrastructure fixes into focused sessions:

| Session | Focus | Complexity | Impact |
|---------|-------|------------|--------|
| 647 | Decision Execution Loop | HIGH | CRITICAL |
| 648 | Celery Task Scheduling | MEDIUM | HIGH |
| 649 | Autonomous Situations (7 dead) | MEDIUM | MEDIUM |
| 650 | Orphaned Services Cleanup | LOW | LOW |
| 651 | Empty Models Audit | LOW | LOW |

---

## Session 647: Decision Execution Loop (CRITICAL)

**Focus:** Wire `decision_executor.py` into the platform

**The Problem:**
- `core/services/decision_executor.py` (25.7KB, ~600 lines) exists
- Complete implementation for executing agent decisions
- ZERO imports anywhere in the codebase
- Decisions accumulate in database but never execute

**Tasks:**
1. Read and understand `decision_executor.py` architecture
2. Create Celery task `process_pending_decisions` in `core/tasks.py`
3. Add Beat schedule in `core/celery.py` (every 5 minutes)
4. Test with existing AgentDecision records
5. Verify decisions actually execute

**Success Criteria:**
- [ ] AgentDecision records are processed
- [ ] Decision outcomes are recorded
- [ ] No errors in Celery logs

**Files to Modify:**
- `core/tasks.py` - Add new task
- `core/celery.py` - Add schedule
- `core/services/decision_executor.py` - May need fixes

---

## Session 648: Celery Task Scheduling

**Focus:** Schedule the 77 unscheduled tasks (prioritize critical ones)

**The Problem:**
- 163 total Celery tasks defined
- Only 53 (32%) are scheduled in Beat
- 77 (47%) are defined but never run
- 33 (20%) are one-time/manual (OK)

**Priority Tasks to Schedule:**

| Task | Purpose | Suggested Schedule |
|------|---------|-------------------|
| `collect_spider_data` | Main spider collection | Every 4 hours |
| `sync_agent_metrics` | Performance aggregation | Every hour |
| `cleanup_old_spider_data` | Database maintenance | Daily 3 AM |
| `backfill_embeddings` | Fill missing embeddings | Every 6 hours |
| `generate_collective_report` | Intelligence summary | Daily 6 AM |

**Tasks:**
1. Audit all 77 unscheduled tasks
2. Categorize: should-schedule vs manual-only vs deprecated
3. Add Beat schedules for priority tasks
4. Test each newly scheduled task
5. Document which tasks remain manual

**Success Criteria:**
- [ ] Critical tasks are scheduled
- [ ] No task conflicts or overlaps
- [ ] Celery Beat runs without errors

**Files to Modify:**
- `core/celery.py` - Add schedules
- `core/tasks.py` - May need fixes

---

## Session 649: Activate Dead Autonomous Situations

**Focus:** Fix the 7 situations producing zero data

**Dead Situations:**
1. Job Match Intelligence
2. Freelance Opportunity Scout
3. SEC Filing Analyzer
4. Earnings Surprise Predictor
5. AI Model Release Monitor
6. Case Law Monitor
7. Regulatory Change Detector

**Working Situations (for reference):**
- Trending Topic Curator: 156 entries
- Content Opportunity Finder: 89 entries
- Sports Line Movement Tracker: 234 entries

**Tasks:**
1. Compare working vs dead situation configurations
2. Check trigger connections (spider_data vs scheduled)
3. Fix trigger signal connections
4. Test each situation manually
5. Verify data flows into SituationInsight model

**Success Criteria:**
- [ ] All 14 situations produce data
- [ ] Triggers fire correctly
- [ ] SituationInsight records created

**Files to Investigate:**
- `core/models_autonomous_situations.py`
- `core/signals/trigger_signals.py`
- `core/services/situation_*.py`

---

## Session 650: Orphaned Services Cleanup

**Focus:** Decide fate of 8 unused services (integrate or remove)

**Orphaned Services:**

| Service | Size | Decision Options |
|---------|------|------------------|
| `decision_executor.py` | 25.7KB | INTEGRATE (Session 647) |
| `recommendation_engine.py` | 881 lines | Evaluate usefulness |
| `ab_testing.py` | 15KB | Evaluate usefulness |
| `discord_voice.py` | 8KB | Discord bot feature? |
| `income_action_service.py` | 12KB | Income Builder feature? |
| `pa_learning_insights.py` | 10KB | PA enhancement? |
| `platform_intelligence_briefing.py` | 18KB | Daily briefing feature? |
| `deduplication_service.py` | 6KB | Content dedup needed? |

**Tasks:**
1. Read each service to understand purpose
2. Decide: integrate, defer, or deprecate
3. For deprecate: move to `core/services/_deprecated/`
4. For integrate: create tickets for future sessions
5. Document decisions

**Success Criteria:**
- [ ] Each service has a documented decision
- [ ] Deprecated services moved out of main path
- [ ] Integration tickets created for valuable services

---

## Session 651: Empty Models Audit

**Focus:** Decide fate of 6 model files with zero data

**Empty Model Files:**

| Model File | Tables | Decision Options |
|------------|--------|------------------|
| `models_autonomous_studio.py` | ContentChannel, ChannelEpisode | Content Studio feature |
| `models_autonomous_alerts.py` | AlertConfiguration, AlertHistory | Alerting system |
| `models_betting.py` | BettingOpportunity, BetPlacement | Sports betting |
| `models_campaign.py` | Campaign, CampaignExecution | Marketing campaigns |
| `models_ai_series.py` | AISeries, SeriesEpisode | AI content series |
| `models_podcast_studio.py` | PodcastChannel, PodcastEpisode | Podcast generation |

**Tasks:**
1. Check if each model has associated views/APIs
2. Check if each model has associated agents
3. Decide: activate feature, defer, or deprecate
4. Document decisions and create tickets

**Success Criteria:**
- [ ] Each model file has a documented decision
- [ ] Activation tickets created for priority features
- [ ] Deprecated models marked clearly

---

## Quick Reference: Session Start Commands

```bash
# Start platform
make start && make celery

# Check decision executor usage
grep -r "decision_executor" core/ --include="*.py"

# Check unscheduled tasks
python manage.py shell -c "
from core.celery import app
print(f'Scheduled: {len(app.conf.beat_schedule)}')"

# Check situation data
python manage.py shell -c "
from core.models_autonomous_situations import SituationInsight
from django.db.models import Count
for s in SituationInsight.objects.values('situation__name').annotate(c=Count('id')):
    print(f'{s[\"situation__name\"]}: {s[\"c\"]}')"
```

---

## Progress Tracker

| Session | Status | Date | Notes |
|---------|--------|------|-------|
| 647 | PENDING | - | Decision Execution |
| 648 | PENDING | - | Celery Scheduling |
| 649 | PENDING | - | Dead Situations |
| 650 | PENDING | - | Orphaned Services |
| 651 | PENDING | - | Empty Models |

---

**Start with Session 647 - Decision Execution is the highest impact fix.**

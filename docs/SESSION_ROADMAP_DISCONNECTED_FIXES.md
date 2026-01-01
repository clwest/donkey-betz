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
| 647 | **COMPLETE** | Dec 31, 2025 | Was duplicate code, not broken. See SESSION_647 handoff |
| 648 | **COMPLETE** | Dec 31, 2025 | 14 critical tasks scheduled. See SESSION_648 handoff |
| 649 | **COMPLETE** | Dec 31, 2025 | 25 trigger configs fixed. See SESSION_649 handoff |
| 650 | **COMPLETE** | Dec 31, 2025 | Audit incorrect - no orphaned services. See SESSION_650 handoff |
| 651 | **COMPLETE** | Dec 31, 2025 | 4/6 have data, 2 are deferred features. See SESSION_651 handoff |

---

**Session 647 Finding:** The "Decision Execution" issue was a misdiagnosis. The system WAS executing
decisions via `AutonomousActionExecutor` (Session 544). `DecisionExecutorService` (Session 619)
was duplicate code that was never integrated. It has been moved to `_deprecated/`.

---

## ROADMAP COMPLETE - Final Summary

**Completed:** December 31, 2025 (Sessions 647-651)

| Session | Claimed Issue | Actual Finding | Action Taken |
|---------|---------------|----------------|--------------|
| 647 | Decision Executor broken | Duplicate code, system working | Deprecated duplicate |
| 648 | 77 unscheduled tasks | 14 critical tasks needed | Scheduled 14 tasks |
| 649 | 7 dead situations | Config issues, not bugs | Fixed 25 trigger configs |
| 650 | 8 orphaned services | All services in use | None needed |
| 651 | 6 empty model files | 4/6 have data | None needed |

**Session 646 Audit Accuracy: ~10%**

The audit identified real infrastructure to review, but its conclusions were largely incorrect due to:
- Not checking lazy imports inside functions
- Not checking `__init__.py` exports
- Not checking custom table names
- Not checking actual database row counts

**Key Improvements Made:**
1. +14 Celery Beat schedules for critical tasks
2. +25 trigger configuration fixes
3. +1 deprecated duplicate service
4. Discord notifications added to ThinkingAgent

**System Health: 94% → Verified and documented**

---

## Session 652 Follow-Up: Deferred Features Activated

The 2 "deferred features" identified in Session 651 were activated in Session 652:

| Feature | Before | After |
|---------|--------|-------|
| Podcast Studio | 0 shows, 0 episodes | 1 show, 1 episode (22,484 char script) |
| Campaign Orchestrator | 0 campaigns | 1 campaign, 16 deliverables |

**Deferred Features: 0** - All features now have active data!

See handoffs:
- `SESSION_652_PODCAST_STUDIO_ACTIVATION.md`
- `SESSION_652_CAMPAIGN_ACTIVATION.md`

# Data Persistence Gaps Analysis

**Session 861** | **January 28, 2026**

This document identifies data persistence vulnerabilities discovered during the Agent Content Persistence audit.

---

## Executive Summary

During Session 861, we discovered that **96% of blog posts were being lost** in production due to content only being stored in ephemeral `AgentResult` objects. This prompted a comprehensive audit revealing multiple data persistence gaps across the platform.

| Risk Level | Category | Data Loss Rate | Status |
|------------|----------|----------------|--------|
| **CRITICAL** | Agent Content | ~96% (111/115 blogs) | ✅ Fixed (Session 860-861) |
| **HIGH** | Tool Call Results | 100% | ✅ Fixed (Session 861) |
| **MEDIUM** | Learning Data | Potential total loss | ✅ Fixed (Session 861) |
| **MEDIUM** | Decision Traces | ~90% not recorded | ⚠️ Needs Fix |
| **MEDIUM** | Spider Aggregations | No caching | ⚠️ Needs Fix |
| **LOW-MEDIUM** | User Feedback Loop | Incomplete | ⚠️ Needs Fix |
| **LOW** | Conversations | Well-handled | ✅ OK |
| **LOW** | File Operations | Audited | ✅ OK |

---

## 1. Agent Content (FIXED)

### Problem
Content-creating agents stored their outputs only in:
- `AgentResult.data` - ephemeral, lost after HTTP response
- `AgentMemory.summary` - only stores 500-char summaries, not full content

### Impact
- **111 out of 115 blogs lost** in production (96.5%)
- Analyses, reports, scripts, strategies all at risk
- ~50 agents affected

### Solution Implemented
- Added `_save_to_deliverable()` method to `BaseAgent` (Session 861)
- Phase 1: Fixed 8 high-priority agents (PR #436)
- Phase 2: Fixed 14 additional agents (commit eebd9f2e)
- Deliverable model provides permanent storage with categorization

### Files Modified
See `docs/plans/AGENT_PERSISTENCE_FIX_PLAN.md` for complete list.

---

## 2. Tool Call Results (FIXED - Session 861)

### Problem (Solved)
When agents call tools (web search, API calls, file reads), the results were:
- Processed inline during execution
- Never persisted to any database
- Lost completely after the request completes

### Solution Implemented
**PR #439** - Added `ToolCallRecord` model and recording infrastructure:

```python
# New models in core/models_tool_calls.py
class ToolCallRecord(models.Model):
    trace_id = models.UUIDField()
    agent_name = models.CharField(max_length=255)
    tool_name = models.CharField(max_length=100)
    parameters = models.JSONField()
    result_summary = models.TextField()  # First 4KB
    result_hash = models.CharField(max_length=72)  # sha256:...
    full_result = models.TextField()  # If under 64KB
    latency_ms = models.IntegerField()
    success = models.BooleanField()
    error_message = models.TextField()
    error_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class ToolCallAggregate(models.Model):
    # Daily statistics per agent/tool for dashboards
    agent_name = models.CharField(max_length=255)
    tool_name = models.CharField(max_length=100)
    date = models.DateField()
    total_calls = models.IntegerField()
    success_calls = models.IntegerField()
    avg_latency_ms = models.IntegerField()
    # ...
```

### New BaseAgent Methods
```python
# Automatic recording wrapper
result = agent._execute_and_record_tool_call(
    tool_name='analyze_filing',
    arguments={'ticker': 'AAPL'},
    trace_id=trace_id
)

# Manual recording
agent._record_tool_call(
    tool_name='web_search',
    arguments={'query': 'AI trends'},
    result=search_results,
    latency_ms=350,
    success=True
)
```

### Status
✅ **FIXED** - PR #439 merged Session 861

---

## 3. Learning Data (FIXED - Session 861)

### Problem (Solved)
The Learning System stored critical data in **Redis only**:
- Agent interactions and preferences
- Learning progress metrics
- Agent improvement scores

### Solution Implemented
**PR #441** - Added database backup models and helper functions:

```python
# New models in core/models_learning_backup.py

class AgentInteractionRecord(models.Model):
    """Backs up agent interactions from Redis"""
    user = models.ForeignKey(User, ...)
    agent_name = models.CharField(max_length=100)
    interaction_type = models.CharField(choices=INTERACTION_TYPES)
    input_data = models.JSONField()
    output_data = models.JSONField()
    rating = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class LearnedPreferenceRecord(models.Model):
    """Backs up learned preferences from Redis"""
    user = models.ForeignKey(User, ...)
    agent_name = models.CharField(max_length=100)
    category = models.CharField(choices=PREFERENCE_CATEGORIES)
    value = models.CharField(max_length=255)
    confidence = models.FloatField()
    occurrences = models.IntegerField()

class LearningProgressSnapshot(models.Model):
    """Periodic snapshots of learning:progress:latest"""
    total_quality = models.FloatField()
    total_complexity = models.FloatField()
    total_improvements = models.IntegerField()
    agent_scores = models.JSONField()
    snapshot_at = models.DateTimeField(auto_now_add=True)

class AgentImprovementRecord(models.Model):
    """Backs up agent improvement data"""
    agent_name = models.CharField(max_length=100)
    iteration = models.IntegerField()
    quality_score = models.FloatField()
    complexity_score = models.FloatField()
```

### Helper Functions for Dual-Write
```python
from core.models_learning_backup import (
    backup_interaction,
    backup_learning_progress,
    backup_agent_improvement,
)

# Call alongside Redis writes
backup_interaction(user_id=1, agent_name='Agent', ...)
backup_learning_progress(total_quality=0.85, ...)
backup_agent_improvement(agent_name='Agent', iteration=10, ...)
```

### Status
✅ **FIXED** - PR #441 merged Session 861

---

## 4. Decision Traces (MEDIUM RISK)

### Problem
Agent decision-making is only recorded when `time_travel_session` is explicitly passed:

```python
# Only recorded if explicitly enabled
if trace_id := kwargs.get('time_travel_session'):
    self._record_decision(trace_id, decision_data)
```

### Impact
- ~90% of agent decisions have no trace
- Cannot debug why agent made a choice
- Cannot audit agent behavior
- Cannot detect agent errors post-facto

### Current State
- `DecisionTrace` model exists
- Recording logic exists
- But opt-in means most traces are not created

### Recommended Fix
Make decision recording **opt-out** instead of opt-in:

```python
# Default to recording (can disable with trace_enabled=False)
trace_id = kwargs.get('time_travel_session') or str(uuid.uuid4())
if kwargs.get('trace_enabled', True):  # Default ON
    self._record_decision(trace_id, decision_data)
```

Consider adding sampling for high-volume scenarios:
```python
# Record 10% of decisions by default, 100% when explicitly requested
sample_rate = 1.0 if kwargs.get('time_travel_session') else 0.1
if random.random() < sample_rate:
    self._record_decision(...)
```

### Priority
**MEDIUM** - Important for debugging but not data loss per se.

---

## 5. Spider Aggregations (MEDIUM RISK)

### Problem
Spider results are:
- Stored individually in `SpiderResult` model ✅
- But aggregations/analyses are computed on-the-fly
- No caching of expensive computations

### Impact
- Same expensive aggregations re-computed repeatedly
- Slow response times for dashboards
- Wasted compute resources
- Cannot compare historical aggregations

### Recommended Fix
Add `SpiderAggregation` model:

```python
class SpiderAggregation(models.Model):
    aggregation_type = models.CharField(max_length=100)  # daily_summary, trend, etc.
    spider_category = models.CharField(max_length=100)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    aggregation_data = models.JSONField()
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['aggregation_type', 'spider_category', 'date_range_start']
```

Add Celery task for pre-computation:
```python
@shared_task
def compute_spider_aggregations():
    """Run hourly via Celery Beat"""
    for category in SpiderCategory.objects.all():
        compute_aggregation(category, 'hourly')
```

### Priority
**MEDIUM** - Performance and historical analysis impact.

---

## 6. User Feedback Loop (LOW-MEDIUM RISK)

### Problem
User feedback on agent outputs is partially implemented:
- `AgentFeedback` model exists
- Frontend can submit feedback
- But feedback is not consistently connected to agent learning

### Impact
- User corrections don't reliably improve agents
- Thumbs down doesn't trigger retraining
- Good outputs don't reinforce patterns

### Current State
```python
# AgentFeedback is recorded but...
feedback = AgentFeedback.objects.create(...)
# ...nothing automatically processes it to improve agents
```

### Recommended Fix
Add feedback processing pipeline:

```python
@receiver(post_save, sender=AgentFeedback)
def process_agent_feedback(sender, instance, created, **kwargs):
    if created:
        if instance.rating < 3:  # Negative feedback
            create_learning_from_negative_feedback(instance)
        elif instance.rating >= 4:  # Positive feedback
            reinforce_positive_pattern(instance)
```

### Priority
**LOW-MEDIUM** - Feature enhancement more than data loss.

---

## Implementation Priority

### Phase 1: Complete (Session 860-861)
- [x] Agent Content persistence via Deliverable model
- [x] 22 agents fixed (8 in Phase 1, 14 in Phase 2)

### Phase 2: Complete (Session 861)
- [x] Tool Call Results - `ToolCallRecord` model (PR #439)
- [x] Learning Data - Database backup models (PR #441)

### Phase 3: Medium Priority (Recommended Next)
- [ ] Decision Traces - Default-on recording
- [ ] Spider Aggregations - Caching layer

### Phase 5: Low Priority
- [ ] User Feedback Loop - Processing pipeline

---

## Monitoring

### Recommended Alerts
1. **Deliverable Creation Rate** - Alert if drops >50% from baseline
2. **Learning Record Count** - Alert if Redis learnings > DB learnings
3. **Tool Call Recording** - Alert if recording fails
4. **Decision Trace Coverage** - Dashboard showing % traced

### Health Check Queries
```python
# Check Deliverable creation rate
Deliverable.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=24)
).count()

# Check Learning sync
redis_count = redis_client.keys('learning:*')
db_count = LearningRecord.objects.count()
assert len(redis_count) == db_count, "Learning data out of sync!"
```

---

## Related Documents
- `docs/plans/AGENT_PERSISTENCE_FIX_PLAN.md` - Detailed fix plan for agent content
- `docs/handoffs/SESSION_860_AI_MIND_TAB_FIX.md` - Initial blog loss discovery
- `docs/handoffs/SESSION_861_AGENT_PERSISTENCE.md` - Phase 1 & 2 implementation

---

**Document Owner:** Session 861
**Last Updated:** January 28, 2026

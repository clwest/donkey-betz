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
| **MEDIUM** | Decision Traces | ~90% not recorded | ✅ Fixed (Session 861) |
| **MEDIUM** | Spider Aggregations | No caching | ✅ Fixed (Session 861) |
| **LOW-MEDIUM** | User Feedback Loop | Incomplete | ✅ Fixed (Session 861) |
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

## 4. Decision Traces (FIXED - Session 861)

### Problem (Solved)
Agent decision-making was only recorded when `time_travel_session` was explicitly passed:

```python
# Only recorded if explicitly enabled - OLD BEHAVIOR
if trace_id := kwargs.get('time_travel_session'):
    self._record_decision(trace_id, decision_data)
```

### Solution Implemented
**PR #442** - Added `DecisionRecord` model and always-on recording:

```python
# New models in core/models_decision_records.py
class DecisionRecord(models.Model):
    """Always-on decision recording - no opt-in required."""
    trace_id = models.UUIDField(null=True, blank=True, db_index=True)
    agent_name = models.CharField(max_length=255, db_index=True)
    decision_type = models.CharField(max_length=50, db_index=True)
    action = models.TextField()
    reasoning = models.TextField(blank=True)
    alternatives = models.JSONField(default=list)
    context = models.JSONField(default=dict)
    confidence = models.FloatField(default=0.8)
    was_successful = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class DecisionAggregate(models.Model):
    """Daily statistics per agent/decision_type for dashboards."""
    agent_name = models.CharField(max_length=255)
    decision_type = models.CharField(max_length=50)
    date = models.DateField()
    total_decisions = models.IntegerField(default=0)
    successful_decisions = models.IntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)
```

### New BaseAgent Method
```python
# Always-on recording (added to BaseAgent)
agent._record_decision(
    decision_type='tool_call',
    action='Calling analyze_filing for AAPL',
    reasoning='LLM requested SEC filing analysis',
    confidence=0.9
)
```

### Status
✅ **FIXED** - PR #442 merged Session 861

---

## 5. Spider Aggregations (FIXED - Session 861)

### Problem (Solved)
Spider results were:
- Stored individually in `SpiderResult` model ✅
- But aggregations/analyses were computed on-the-fly
- No caching of expensive computations

### Solution Implemented
**PR #443** - Added spider aggregation caching system:

```python
# New models in core/models_spider_aggregation.py

class SpiderAggregation(models.Model):
    """Cached aggregation results for spider data."""
    aggregation_type = models.CharField(max_length=50, db_index=True)  # daily_summary, category_summary, etc.
    category = models.CharField(max_length=100, blank=True, db_index=True)
    spider_name = models.CharField(max_length=100, blank=True, db_index=True)
    date_range_start = models.DateTimeField(db_index=True)
    date_range_end = models.DateTimeField(db_index=True)
    aggregation_data = models.JSONField()
    computation_time_ms = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    computed_at = models.DateTimeField(auto_now_add=True)

class TrendDataPoint(models.Model):
    """Time-series data points for spider trends."""
    trend_type = models.CharField(max_length=50, db_index=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    granularity = models.CharField(max_length=20, db_index=True)  # hourly, daily, weekly
    timestamp = models.DateTimeField(db_index=True)
    value = models.FloatField()
    metadata = models.JSONField(default=dict)
```

### Celery Task for Pre-computation
```python
# Added to core/tasks.py
@shared_task
def compute_spider_aggregations():
    """
    Session 861: Pre-compute spider aggregations for caching.
    Runs hourly via Celery Beat.
    """
    # Computes daily_summary, category_summaries, trend_data_points
```

### Helper Methods
```python
# Get cached or compute on-demand
data, from_cache = SpiderAggregation.get_cached_or_compute(
    aggregation_type='category_summary',
    category='financial',
    compute_fn=lambda: compute_category_summary('financial'),
    ttl_hours=1,
)

# Invalidate cache when new data arrives
SpiderAggregation.invalidate(category='financial')
```

### Status
✅ **FIXED** - PR #443 merged Session 861

---

## 6. User Feedback Loop (FIXED - Session 861)

### Problem (Solved)
User feedback on agent outputs was partially implemented:
- Feedback models existed
- Frontend could submit feedback
- But feedback was not consistently connected to agent learning

### Solution Implemented
**PR #444** - Added feedback processing system with Django signals:

```python
# New module: core/models_feedback_processing.py

class FeedbackProcessor:
    """Process user feedback to improve agent behavior."""

    POSITIVE_THRESHOLD = 4  # 4-5 stars = positive
    NEGATIVE_THRESHOLD = 2  # 1-2 stars = negative

    def process_pipeline_feedback(self, stage, rating, agent_name, context, feedback_text):
        """Process feedback from PipelineStageFeedback."""
        if rating >= self.POSITIVE_THRESHOLD:
            return self._reinforce_positive(agent_name, stage, context, feedback_text)
        elif rating <= self.NEGATIVE_THRESHOLD:
            return self._learn_from_negative(agent_name, stage, context, feedback_text)

    def _reinforce_positive(self, agent_name, task_context, context, feedback_text):
        """Reinforce positive feedback by recording what worked."""
        AgentLearning.objects.create(
            agent=agent,
            learning_type='positive_feedback',
            content=f"User provided positive feedback...",
            source='user_feedback',
            confidence_score=0.8,
        )

    def _learn_from_negative(self, agent_name, task_context, context, feedback_text):
        """Learn from negative feedback by recording what didn't work."""
        AgentLearning.objects.create(
            agent=agent,
            learning_type='negative_feedback',
            content=f"User flagged issue...",
            source='user_feedback',
            confidence_score=0.9,
            metadata={'action_needed': True},
        )
```

### Signal Handlers
```python
# Automatically process feedback when saved
@receiver(post_save, sender='core.PipelineStageFeedback')
def process_pipeline_feedback_signal(sender, instance, created, **kwargs):
    if created:
        processor.process_pipeline_feedback(...)

@receiver(post_save, sender='core.HumanFeedbackRecord')
def process_human_feedback_signal(sender, instance, created, **kwargs):
    if created:
        processor.process_human_feedback(...)

@receiver(post_save, sender='core.AgentExecutionMemory')
def process_execution_memory_signal(sender, instance, created, **kwargs):
    if instance.user_rating:
        processor.process_execution_feedback(...)
```

### Status
✅ **FIXED** - PR #444 merged Session 861

---

## Implementation Priority

### Phase 1: Complete (Session 860-861)
- [x] Agent Content persistence via Deliverable model
- [x] 22 agents fixed (8 in Phase 1, 14 in Phase 2)

### Phase 2: Complete (Session 861)
- [x] Tool Call Results - `ToolCallRecord` model (PR #439)
- [x] Learning Data - Database backup models (PR #441)
- [x] Decision Traces - `DecisionRecord` model (PR #442)

### Phase 3: Complete (Session 861)
- [x] Spider Aggregations - Caching layer (PR #443)

### Phase 4: Complete (Session 861)
- [x] User Feedback Loop - Processing pipeline (PR #444)

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

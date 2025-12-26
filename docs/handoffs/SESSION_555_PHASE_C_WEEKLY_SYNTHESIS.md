# Phase C: Weekly Synthesis

**Priority:** 3 of 4
**Estimated Scope:** Medium
**Dependencies:** Phase A (Artifact Extraction), Phase B helpful but not required

---

## Problem Statement

The system generates massive amounts of activity:
- 55 agents having conversations
- 800+ dreams per day
- Dozens of knowledge transfers
- Multiple extracted artifacts

But there's no high-level synthesis that says:
- "Here's what your agents discovered this week"
- "These 3 strategic themes keep emerging"
- "These proposals are still waiting for your decision"
- "These executions completed with these outcomes"

The user has to manually dig through everything to understand what's happening.

---

## Goal

Create an automated weekly (and daily) synthesis that:
1. Summarizes key themes from agent conversations
2. Highlights important discoveries and insights
3. Lists pending decisions requiring attention
4. Reports on execution outcomes
5. Identifies patterns across agent activity

---

## Data Model

### New Model: `IntelligenceBrief`

```python
# core/models_intelligence_brief.py

class IntelligenceBrief(models.Model):
    """
    Synthesized intelligence report for a time period.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    PERIOD_TYPES = [
        ('daily', 'Daily Brief'),
        ('weekly', 'Weekly Brief'),
        ('monthly', 'Monthly Brief'),
    ]
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)

    # Time range covered
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    generated_at = models.DateTimeField(auto_now_add=True)

    # Summary content
    executive_summary = models.TextField()  # 2-3 paragraph overview

    # Structured sections (JSON for flexibility)
    strategic_themes = models.JSONField(default=list)
    # Example:
    # [
    #   {
    #     "theme": "Data Quality Concerns",
    #     "description": "Multiple agents flagged insufficient sample sizes",
    #     "conversations": ["uuid1", "uuid2"],
    #     "agents_involved": ["COOAgent", "ResearchAgent"],
    #     "frequency": 5
    #   }
    # ]

    key_discoveries = models.JSONField(default=list)
    # Example:
    # [
    #   {
    #     "discovery": "Sellfy pricing clusters around $9/$19/$49",
    #     "source": "conversation_uuid",
    #     "agent": "BrandIdentityAgent",
    #     "confidence": 0.85
    #   }
    # ]

    pending_decisions = models.JSONField(default=list)
    # List of artifact IDs awaiting decision

    execution_outcomes = models.JSONField(default=list)
    # Completed executions with results

    agent_activity_summary = models.JSONField(default=dict)
    # Per-agent activity metrics

    recommendations = models.JSONField(default=list)
    # AI-generated recommendations based on patterns

    # Metrics
    metrics = models.JSONField(default=dict)
    # {
    #   "conversations": 47,
    #   "dreams": 821,
    #   "knowledge_transfers": 156,
    #   "artifacts_extracted": 23,
    #   "decisions_made": 8,
    #   "executions_completed": 3
    # }

    # User interaction
    viewed_at = models.DateTimeField(null=True)
    feedback = models.TextField(blank=True)

    class Meta:
        ordering = ['-period_end']
        unique_together = ['period_type', 'period_start']
```

---

## Synthesis Service

### New Service: `IntelligenceSynthesisService`

```python
# core/services/intelligence_synthesis.py

class IntelligenceSynthesisService:
    """
    Synthesizes intelligence briefs from system activity.
    """

    def generate_brief(self, period_type: str = 'weekly') -> IntelligenceBrief:
        """
        Generate a complete intelligence brief.

        1. Gather all activity for period
        2. Extract themes from conversations
        3. Identify key discoveries
        4. Compile pending decisions
        5. Summarize execution outcomes
        6. Generate recommendations
        7. Write executive summary
        """
        pass

    def _get_period_range(self, period_type: str) -> Tuple[datetime, datetime]:
        """Get start/end for period type."""
        now = timezone.now()
        if period_type == 'daily':
            return (now - timedelta(days=1), now)
        elif period_type == 'weekly':
            return (now - timedelta(days=7), now)
        elif period_type == 'monthly':
            return (now - timedelta(days=30), now)

    def _gather_conversations(self, start: datetime, end: datetime) -> QuerySet:
        """Get all conversations in period."""
        return AgentConversation.objects.filter(
            started_at__gte=start,
            started_at__lte=end
        ).select_related('initiator').prefetch_related('participants', 'artifacts')

    def _extract_themes(self, conversations: QuerySet) -> List[dict]:
        """
        Use LLM to identify recurring themes across conversations.

        Prompt includes all conversation topics and summaries.
        Returns clustered themes with supporting evidence.
        """
        pass

    def _identify_discoveries(self, conversations: QuerySet, knowledge: QuerySet) -> List[dict]:
        """
        Find notable discoveries from:
        - High-confidence knowledge entries
        - Insights marked as important
        - Novel information flagged by agents
        """
        pass

    def _compile_pending_decisions(self) -> List[dict]:
        """
        Get all artifacts/dreams awaiting decision.
        Sorted by importance and age.
        """
        pending_artifacts = ConversationArtifact.objects.filter(status='pending')
        pending_dreams = AgentDream.objects.filter(
            promoted_to_decision=True,
            decision_outcome='pending'
        )
        # Combine and sort
        pass

    def _summarize_executions(self, start: datetime, end: datetime) -> List[dict]:
        """
        Get execution outcomes for period.
        """
        completed = ExecutionItem.objects.filter(
            completed_at__gte=start,
            completed_at__lte=end,
            status='completed'
        )
        return [
            {
                'title': e.artifact.title,
                'outcome': e.outcome,
                'agent': e.assigned_agent.name
            }
            for e in completed
        ]

    def _calculate_agent_activity(self, start: datetime, end: datetime) -> dict:
        """
        Per-agent activity metrics:
        - Conversations participated
        - Knowledge created
        - Dreams generated
        - Executions completed
        """
        pass

    def _generate_recommendations(self, themes: List, discoveries: List, pending: List) -> List[str]:
        """
        Use LLM to generate actionable recommendations based on:
        - Recurring themes that need attention
        - Discoveries that should be acted on
        - Pending decisions that are aging
        - Patterns in agent activity
        """
        pass

    def _write_executive_summary(self, brief_data: dict) -> str:
        """
        Generate 2-3 paragraph executive summary.

        Should be readable in 30 seconds and convey:
        - Most important development this period
        - Key decision needed
        - Overall system health
        """
        pass
```

---

## Synthesis Prompts

### Theme Extraction Prompt

```
Analyze these {count} agent conversations from the past week and identify recurring strategic themes.

CONVERSATIONS:
{conversation_summaries}

Identify 3-5 major themes that appear across multiple conversations. For each theme:
1. Theme name (short, descriptive)
2. Description (2-3 sentences)
3. Which conversations support this theme
4. Which agents discussed this
5. How many times it appeared

Focus on:
- Strategic concerns (risks, opportunities)
- Repeated topics across different agent pairs
- Emerging patterns or trends
- Unresolved questions

Return as JSON array.
```

### Executive Summary Prompt

```
Write a 2-3 paragraph executive summary of this week's agent intelligence activity.

DATA:
- Conversations: {conversation_count}
- Key Themes: {themes}
- Top Discoveries: {discoveries}
- Pending Decisions: {pending_count}
- Completed Executions: {execution_count}

The summary should:
1. Lead with the most important development or insight
2. Highlight any urgent decisions needed
3. Note overall system health and activity level
4. Be readable in 30 seconds

Write in a professional but accessible tone. Address the reader as a busy executive who needs to know what matters.
```

---

## Celery Tasks

```python
# In core/tasks.py

@shared_task
def generate_daily_brief():
    """
    Generate daily intelligence brief.

    Run at 8 AM daily.
    """
    from core.services.intelligence_synthesis import synthesis_service
    brief = synthesis_service.generate_brief('daily')
    logger.info(f"Generated daily brief: {brief.id}")
    return str(brief.id)


@shared_task
def generate_weekly_brief():
    """
    Generate weekly intelligence brief.

    Run Monday at 9 AM.
    """
    from core.services.intelligence_synthesis import synthesis_service
    brief = synthesis_service.generate_brief('weekly')
    logger.info(f"Generated weekly brief: {brief.id}")

    # Optionally notify user
    notify_user_of_brief(brief)

    return str(brief.id)
```

### Celery Beat Schedule

```python
# In core/celery.py

'generate-daily-brief': {
    'task': 'core.tasks.generate_daily_brief',
    'schedule': crontab(hour=8, minute=0),  # 8 AM daily
},

'generate-weekly-brief': {
    'task': 'core.tasks.generate_weekly_brief',
    'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
},
```

---

## API Endpoints

```python
# In core/urls.py

# List all briefs
path('api/briefs/', views_briefs.list_briefs, name='list-briefs'),

# Get specific brief
path('api/briefs/<uuid:brief_id>/', views_briefs.get_brief, name='get-brief'),

# Get latest brief by type
path('api/briefs/latest/<str:period_type>/', views_briefs.latest_brief, name='latest-brief'),

# Generate brief on demand
path('api/briefs/generate/', views_briefs.generate_brief, name='generate-brief'),

# Submit feedback on brief
path('api/briefs/<uuid:brief_id>/feedback/', views_briefs.submit_feedback, name='brief-feedback'),
```

---

## UI Integration

### Intelligence Brief View

New prominent section, possibly its own tab or dashboard home:

```html
<!-- Weekly Brief -->
<div class="intelligence-brief">
    <div class="brief-header">
        <h2>📊 Weekly Intelligence Brief</h2>
        <span class="brief-period">Dec 18-25, 2025</span>
        <span class="brief-generated">Generated 2 hours ago</span>
    </div>

    <!-- Executive Summary -->
    <div class="executive-summary card">
        <h4>Executive Summary</h4>
        <p>{executive_summary}</p>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
        <div class="metric">
            <span class="metric-value">47</span>
            <span class="metric-label">Conversations</span>
        </div>
        <div class="metric">
            <span class="metric-value">821</span>
            <span class="metric-label">Dreams</span>
        </div>
        <div class="metric">
            <span class="metric-value">12</span>
            <span class="metric-label">Pending Decisions</span>
        </div>
        <div class="metric">
            <span class="metric-value">3</span>
            <span class="metric-label">Completed Executions</span>
        </div>
    </div>

    <!-- Strategic Themes -->
    <div class="themes-section card">
        <h4>🎯 Strategic Themes This Week</h4>
        <div class="themes-list">
            <!-- Theme cards -->
        </div>
    </div>

    <!-- Key Discoveries -->
    <div class="discoveries-section card">
        <h4>💡 Key Discoveries</h4>
        <ul class="discoveries-list">
            <!-- Discovery items -->
        </ul>
    </div>

    <!-- Pending Decisions -->
    <div class="pending-section card">
        <h4>⏳ Awaiting Your Decision</h4>
        <ul class="pending-list">
            <!-- Linked to artifacts/dreams -->
        </ul>
    </div>

    <!-- Recommendations -->
    <div class="recommendations-section card">
        <h4>📋 Recommendations</h4>
        <ol class="recommendations-list">
            <!-- AI recommendations -->
        </ol>
    </div>
</div>
```

### Brief Card (for dashboard)

```html
<div class="brief-card" onclick="viewBrief('{id}')">
    <div class="brief-card-header">
        <span class="brief-type">{period_type}</span>
        <span class="brief-date">{period_end}</span>
    </div>
    <div class="brief-card-summary">
        {executive_summary_preview}...
    </div>
    <div class="brief-card-stats">
        <span>{themes_count} themes</span> •
        <span>{discoveries_count} discoveries</span> •
        <span>{pending_count} pending</span>
    </div>
</div>
```

---

## Notification Integration

### Discord Notification

```python
def notify_user_of_brief(brief: IntelligenceBrief):
    """Send brief summary to Discord."""
    from core.services.discord_notifications import discord_service

    message = f"""
📊 **Weekly Intelligence Brief Ready**

{brief.executive_summary[:500]}...

**This Week:**
• {brief.metrics.get('conversations', 0)} conversations
• {len(brief.strategic_themes)} themes identified
• {len(brief.pending_decisions)} decisions awaiting you

[View Full Brief →]
    """

    discord_service.send_to_channel('system-status', message)
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `core/models_intelligence_brief.py` | CREATE | IntelligenceBrief model |
| `core/services/intelligence_synthesis.py` | CREATE | Synthesis service |
| `core/views_briefs.py` | CREATE | API endpoints |
| `core/urls.py` | MODIFY | Add brief routes |
| `core/tasks.py` | MODIFY | Add generation tasks |
| `core/celery.py` | MODIFY | Add beat schedules |
| `ai_core/templates/...` | MODIFY/CREATE | Brief view UI |
| `core/migrations/XXXX_briefs.py` | CREATE | Database migration |

---

## Success Criteria

1. Weekly briefs generated automatically every Monday
2. Daily briefs available on demand
3. Executive summary readable in 30 seconds
4. Themes accurately reflect conversation content
5. Pending decisions clearly listed with links
6. Recommendations are actionable

---

## Next Phase

Phase D (Human Feedback Loop) allows users to interact with briefs and provide feedback that flows back to agents.

---

**This phase transforms raw activity into actionable intelligence summaries.**

# Session 353: Project Learning Loop - Complete Implementation Guide

**Date:** December 5, 2025
**Status:** Planning Complete - Ready for Implementation
**Goal:** Enable projects to autonomously learn and track their domain over time

---

## Vision

A user creates a project like "Coffee Shop Trends" or "Podcast Topics for Tech". The system:
1. Runs initial research and stores findings
2. Automatically re-checks periodically (daily/weekly)
3. Detects what's NEW since last check
4. Alerts user to significant changes
5. Accumulates knowledge that compounds over time

---

## Session 353 Completed Work

### 1. PDF Button Consolidation
- Moved "Download All Research" button to top of research summaries section
- Removed individual PDF buttons from each research card
- File: `ai_core/templates/ai_image_studio.html`

### 2. Brand Asset Persistence
- Generated assets now save to `ImageHistory` model
- Linked to project via `project` ForeignKey
- File: `core/views_projects_api.py` (lines ~1732-1777)

### 3. Assistant Context Enrichment
- `_handle_creation_agent` now enriches prompts with project research
- Extracts brand colors, style keywords, industry from research summaries
- File: `core/personal_ai_assistant_enhanced.py` (lines 1400-1460)

### 4. SD3 for Logos
- Main Assistant now auto-detects logo requests
- Uses `quality='high'` (SD3) for logos instead of default SDXL
- File: `core/personal_ai_assistant_enhanced.py` (lines 1399-1405)

---

## Phase 1: Project Learning Configuration (Session 354)

### 1.1 Add Learning Fields to PartnershipProject Model

```python
# core/models_partnership.py

class PartnershipProject(models.Model):
    # ... existing fields ...

    # Session 354: Learning Loop Configuration
    learning_enabled = models.BooleanField(default=False)
    learning_topics = models.JSONField(default=list, blank=True)  # ["coffee trends", "specialty drinks"]
    learning_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Every 2 Weeks'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    last_learning_run = models.DateTimeField(null=True, blank=True)
    next_learning_run = models.DateTimeField(null=True, blank=True)
    learning_history = models.JSONField(default=list, blank=True)  # [{date, findings_count, deltas}]
```

### 1.2 Create Migration

```bash
python manage.py makemigrations core --name add_project_learning_fields
python manage.py migrate
```

### 1.3 Add UI Toggle in Project Card

In `ai_image_studio.html`, add a "Learning" section to project details:

```javascript
// In renderProjectDetails or similar
<div class="learning-config mt-3" style="background: rgba(139, 92, 246, 0.1); border-radius: 8px; padding: 12px;">
    <div class="d-flex justify-content-between align-items-center">
        <span style="color: #c4b5fd;">
            <i class="fas fa-brain me-2"></i>Continuous Learning
        </span>
        <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox"
                   id="learningEnabled_${project.id}"
                   ${project.learning_enabled ? 'checked' : ''}
                   onchange="toggleProjectLearning('${project.id}', this.checked)">
        </div>
    </div>
    ${project.learning_enabled ? `
        <div class="mt-2">
            <small style="color: #a78bfa;">
                Frequency: ${project.learning_frequency} |
                Last run: ${project.last_learning_run || 'Never'} |
                Topics: ${project.learning_topics?.join(', ') || 'Auto-detect from research'}
            </small>
        </div>
    ` : ''}
</div>
```

### 1.4 Add API Endpoint for Learning Config

```python
# core/views_projects_api.py

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_project_learning(request, project_id):
    """Enable/disable continuous learning for a project."""
    project = get_object_or_404(PartnershipProject, id=project_id, user=request.user)

    enabled = request.data.get('enabled', False)
    frequency = request.data.get('frequency', 'weekly')
    topics = request.data.get('topics', [])

    project.learning_enabled = enabled
    project.learning_frequency = frequency
    project.learning_topics = topics

    if enabled and not project.next_learning_run:
        # Schedule first run based on frequency
        from datetime import timedelta
        freq_map = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'monthly': 30}
        project.next_learning_run = timezone.now() + timedelta(days=freq_map.get(frequency, 7))

    project.save()

    return Response({
        'success': True,
        'learning_enabled': project.learning_enabled,
        'next_run': project.next_learning_run
    })
```

---

## Phase 2: Scheduled Learning Task (Session 354-355)

### 2.1 Create Celery Task for Project Learning

```python
# core/tasks.py

@shared_task(bind=True)
def run_project_learning_cycle(self):
    """
    Celery Beat task: Check all projects with learning enabled
    and run research updates for those due.
    """
    from core.models_partnership import PartnershipProject
    from django.utils import timezone

    due_projects = PartnershipProject.objects.filter(
        learning_enabled=True,
        next_learning_run__lte=timezone.now()
    )

    results = []
    for project in due_projects:
        try:
            result = run_single_project_learning.delay(str(project.id))
            results.append({
                'project_id': str(project.id),
                'project_name': project.project_name,
                'task_id': result.id
            })
        except Exception as e:
            logger.error(f"Failed to queue learning for project {project.id}: {e}")

    return {
        'projects_queued': len(results),
        'results': results
    }


@shared_task(bind=True)
def run_single_project_learning(self, project_id: str):
    """
    Run a learning cycle for a single project.
    1. Get current spider data for project topics
    2. Run research agents
    3. Compare with previous findings (delta detection)
    4. Store new learnings
    5. Schedule next run
    """
    from core.models_partnership import PartnershipProject
    from core.services.unified_intelligence_search import get_unified_intelligence_search
    from agents.competitor_analysis_agent import CompetitorAnalysisAgent
    from django.utils import timezone
    from datetime import timedelta

    project = PartnershipProject.objects.get(id=project_id)
    user = project.user

    logger.info(f"🧠 Starting learning cycle for project: {project.project_name}")

    # Step 1: Determine topics to research
    topics = project.learning_topics
    if not topics:
        # Auto-extract from project name and existing research
        topics = _extract_topics_from_project(project)

    # Step 2: Refresh spider data for topics
    search_service = get_unified_intelligence_search()
    for topic in topics:
        search_service.refresh_spiders_for_query(topic)

    # Step 3: Run competitor/trend analysis
    agent = CompetitorAnalysisAgent(user=user)
    analysis_result = agent.execute(
        business_idea=project.project_name,
        analysis_type='trend_analysis',
        project_id=str(project.id)
    )

    # Step 4: Delta detection - compare with previous
    previous_findings = project.metadata.get('research_summaries', [])
    new_findings = analysis_result.get('findings', [])

    deltas = _detect_research_deltas(previous_findings, new_findings)

    # Step 5: Store learnings
    learning_entry = {
        'date': timezone.now().isoformat(),
        'topics_researched': topics,
        'findings_count': len(new_findings),
        'deltas': deltas,
        'new_trends': deltas.get('new_items', []),
        'disappeared_trends': deltas.get('removed_items', [])
    }

    if not project.learning_history:
        project.learning_history = []
    project.learning_history.append(learning_entry)

    # Step 6: Update research summaries if significant changes
    if deltas.get('new_items'):
        # Append new research to existing
        existing_summaries = project.metadata.get('research_summaries', [])
        existing_summaries.append({
            'type': 'learning_update',
            'date': timezone.now().isoformat(),
            'summary': f"New trends detected: {', '.join(deltas['new_items'][:5])}",
            'full_analysis': analysis_result
        })
        project.metadata['research_summaries'] = existing_summaries

    # Step 7: Schedule next run
    freq_map = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'monthly': 30}
    days = freq_map.get(project.learning_frequency, 7)
    project.last_learning_run = timezone.now()
    project.next_learning_run = timezone.now() + timedelta(days=days)

    project.save()

    logger.info(f"✅ Learning cycle complete for {project.project_name}: {len(deltas.get('new_items', []))} new trends")

    # Step 8: Create notification if significant changes
    if deltas.get('new_items'):
        _create_learning_notification(project, deltas)

    return {
        'success': True,
        'project_id': project_id,
        'deltas': deltas,
        'next_run': project.next_learning_run.isoformat()
    }


def _extract_topics_from_project(project):
    """Extract learning topics from project name and research."""
    topics = []

    # From project name
    name_words = project.project_name.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'in', 'on', 'at', 'to'}
    topics.extend([w for w in name_words if w not in stop_words and len(w) > 3])

    # From existing research
    if project.metadata:
        for summary in project.metadata.get('research_summaries', []):
            if summary.get('type') == 'competitor_analysis':
                # Extract industry/market terms
                pass

    return topics[:5]  # Limit to 5 topics


def _detect_research_deltas(previous, current):
    """Compare research findings to detect what's new/changed."""
    # Extract key terms/trends from previous
    prev_trends = set()
    for item in previous:
        if isinstance(item, dict):
            summary = item.get('summary', '')
            # Simple keyword extraction
            prev_trends.update(summary.lower().split()[:20])

    # Extract from current
    curr_trends = set()
    if isinstance(current, list):
        for item in current:
            if isinstance(item, dict):
                curr_trends.update(str(item).lower().split()[:20])

    return {
        'new_items': list(curr_trends - prev_trends)[:10],
        'removed_items': list(prev_trends - curr_trends)[:10],
        'total_previous': len(prev_trends),
        'total_current': len(curr_trends)
    }


def _create_learning_notification(project, deltas):
    """Create a notification for significant learning updates."""
    from core.models_unified_system import ProactiveAlert

    try:
        ProactiveAlert.objects.create(
            user=project.user,
            alert_type='learning_update',
            title=f"New trends for {project.project_name}",
            message=f"Found {len(deltas.get('new_items', []))} new trends: {', '.join(deltas['new_items'][:3])}...",
            priority='medium',
            metadata={
                'project_id': str(project.id),
                'deltas': deltas
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create learning notification: {e}")
```

### 2.2 Add to Celery Beat Schedule

```python
# core/celery.py

app.conf.beat_schedule = {
    # ... existing schedules ...

    'project-learning-cycle': {
        'task': 'core.tasks.run_project_learning_cycle',
        'schedule': crontab(hour=6, minute=0),  # Run at 6 AM daily
        'options': {'queue': 'learning'}
    },
}
```

---

## Phase 3: Delta Detection & Intelligence (Session 355)

### 3.1 Smarter Delta Detection

```python
# core/services/learning_delta_service.py

class LearningDeltaService:
    """Intelligent comparison of research findings over time."""

    def __init__(self):
        self.embedding_service = get_memory_embedding_service()

    def compute_semantic_delta(self, previous_research, current_research):
        """Use embeddings to find semantically new content."""
        # Embed previous findings
        prev_embeddings = [
            self.embedding_service.embed_text(str(item))
            for item in previous_research
        ]

        # Embed current findings
        curr_embeddings = [
            self.embedding_service.embed_text(str(item))
            for item in current_research
        ]

        # Find items in current that are semantically distant from all previous
        new_items = []
        for i, curr_emb in enumerate(curr_embeddings):
            max_similarity = max(
                cosine_similarity(curr_emb, prev_emb)
                for prev_emb in prev_embeddings
            ) if prev_embeddings else 0

            if max_similarity < 0.7:  # Threshold for "new"
                new_items.append({
                    'content': current_research[i],
                    'novelty_score': 1 - max_similarity
                })

        return sorted(new_items, key=lambda x: x['novelty_score'], reverse=True)

    def categorize_changes(self, deltas):
        """Categorize changes into trend types."""
        categories = {
            'emerging_trends': [],    # Brand new topics
            'growing_trends': [],     # Existing topics with more mentions
            'declining_trends': [],   # Topics mentioned less
            'stable_topics': []       # Consistent topics
        }

        # Categorization logic based on mention frequency over time
        return categories
```

### 3.2 Trend Velocity Tracking

```python
# In PartnershipProject.metadata, track:
{
    "trend_velocities": {
        "oat milk": {"mentions": [5, 8, 12, 15], "velocity": "+3/week"},
        "cold brew": {"mentions": [10, 10, 11, 10], "velocity": "stable"},
        "nitro coffee": {"mentions": [2, 4, 8, 16], "velocity": "+4/week, accelerating"}
    }
}
```

---

## Phase 4: Notifications & UI (Session 356)

### 4.1 Learning History Display

Add a "Learning Timeline" tab to project details:

```javascript
function renderLearningTimeline(project) {
    if (!project.learning_history?.length) {
        return `<div class="text-muted">No learning history yet. Enable learning to start!</div>`;
    }

    return project.learning_history.map(entry => `
        <div class="learning-entry p-2 mb-2" style="background: rgba(139, 92, 246, 0.1); border-radius: 8px;">
            <div class="d-flex justify-content-between">
                <strong style="color: #c4b5fd;">${new Date(entry.date).toLocaleDateString()}</strong>
                <span class="badge bg-success">${entry.deltas?.new_items?.length || 0} new trends</span>
            </div>
            ${entry.new_trends?.length ? `
                <div class="mt-1">
                    <small style="color: #a78bfa;">New: ${entry.new_trends.slice(0, 3).join(', ')}</small>
                </div>
            ` : ''}
        </div>
    `).join('');
}
```

### 4.2 Notification Bell Integration

```javascript
// Add learning updates to existing notification system
function fetchLearningNotifications() {
    fetch('/api/notifications/learning/')
        .then(r => r.json())
        .then(data => {
            if (data.notifications?.length) {
                updateNotificationBadge(data.notifications.length);
                renderLearningNotifications(data.notifications);
            }
        });
}
```

---

## Phase 5: Knowledge Accumulation (Session 356-357)

### 5.1 Knowledge Graph for Project

```python
# core/models_partnership.py

class ProjectKnowledge(models.Model):
    """Accumulated knowledge for a project over time."""
    project = models.ForeignKey(PartnershipProject, on_delete=models.CASCADE)

    topic = models.CharField(max_length=200)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    mention_count = models.IntegerField(default=1)

    trend_direction = models.CharField(
        max_length=20,
        choices=[('rising', 'Rising'), ('stable', 'Stable'), ('declining', 'Declining')],
        default='stable'
    )

    related_topics = models.JSONField(default=list)  # ["topic1", "topic2"]
    source_articles = models.JSONField(default=list)  # [{url, title, date}]

    class Meta:
        unique_together = ['project', 'topic']
```

### 5.2 Knowledge Accumulation in Learning Cycle

```python
def accumulate_knowledge(project, new_findings):
    """Update project knowledge graph with new findings."""
    for finding in new_findings:
        topic = extract_topic(finding)

        knowledge, created = ProjectKnowledge.objects.get_or_create(
            project=project,
            topic=topic
        )

        if not created:
            knowledge.mention_count += 1
            knowledge.last_seen = timezone.now()

            # Update trend direction based on frequency
            if knowledge.mention_count > previous_count * 1.2:
                knowledge.trend_direction = 'rising'
            elif knowledge.mention_count < previous_count * 0.8:
                knowledge.trend_direction = 'declining'

        knowledge.save()
```

---

## Testing Checklist

### Phase 1 Tests
- [ ] Add learning_enabled field to project
- [ ] Toggle learning on/off via UI
- [ ] Set frequency (daily/weekly/monthly)
- [ ] Custom topics vs auto-detect

### Phase 2 Tests
- [ ] Celery task runs on schedule
- [ ] Spiders refresh for project topics
- [ ] Research agent runs with project context
- [ ] Next run scheduled correctly

### Phase 3 Tests
- [ ] Delta detection finds new trends
- [ ] Semantic comparison works
- [ ] Trend velocity calculated

### Phase 4 Tests
- [ ] Learning history displays in UI
- [ ] Notifications appear for new trends
- [ ] Notification links to project

### Phase 5 Tests
- [ ] Knowledge accumulates over runs
- [ ] Trend direction updates
- [ ] Related topics linked

---

## Example User Flow

1. **User creates project:** "Portland Coffee Scene"
2. **Initial research runs:** Competitor analysis, customer research, trends
3. **User enables learning:** Toggle on, frequency = weekly
4. **Week 1:** System researches, stores baseline
5. **Week 2:** System re-researches, finds "mushroom coffee" trending (+3 mentions)
6. **Notification:** "New trend for Portland Coffee Scene: mushroom coffee is rising"
7. **User opens project:** Sees learning timeline, knowledge graph
8. **Week 3:** "mushroom coffee" continues rising, "nitro" declining
9. **AI Assistant context:** "Create a logo" now knows about mushroom coffee trend

---

## Files to Modify

| File | Changes |
|------|---------|
| `core/models_partnership.py` | Add learning fields |
| `core/tasks.py` | Add learning cycle tasks |
| `core/celery.py` | Add beat schedule |
| `core/views_projects_api.py` | Add learning config endpoints |
| `ai_core/templates/ai_image_studio.html` | Add learning UI |
| `core/services/learning_delta_service.py` | NEW - Delta detection |

---

## Success Metrics

- Projects with learning enabled actively discover new trends
- Users receive actionable notifications about market changes
- Knowledge compounds - 3 months of learning = rich project context
- AI Assistant uses accumulated knowledge for better outputs

---

**Ready for Implementation: Session 354+**

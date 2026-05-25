# Session 425: Opportunity Pipeline Automation

**Date:** December 11, 2025
**Status:** COMPLETE
**Previous Session:** 424 - Opportunities Discord Channel

---

## Summary

Implemented complete opportunity pipeline automation with:
- Auto-task creation from high-scoring opportunities (70+/100)
- Agent linking based on opportunity type
- Outcome tracking (applied, won, lost) with revenue attribution
- Weekly opportunity digest posted to Discord #boardroom

---

## New Models Created

### OpportunityTask
Auto-generated tasks from high-scoring opportunities.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Primary key |
| `opportunity` | OneToOne | Link to source opportunity |
| `user` | ForeignKey | Task owner |
| `title` | CharField | Task title |
| `status` | CharField | pending/accepted/in_progress/applied/waiting/won/lost/expired/cancelled |
| `priority` | CharField | low/medium/high/critical |
| `assigned_agents` | ManyToMany | Agents assigned to help |
| `primary_agent` | ForeignKey | Lead agent for task |
| `opportunity_score` | Integer | Score when task created |
| `due_date` | DateTime | Optional deadline |
| `action_items` | JSONField | Checklist items |

**Key Methods:**
- `mark_won(actual_amount, notes)` - Creates revenue record, notifies Discord
- `mark_lost(reason, notes)` - Records outcome for learning
- `create_from_opportunity(opportunity, score_data)` - Factory method

### OpportunityOutcome
Track win/loss outcomes for learning.

| Field | Type | Purpose |
|-------|------|---------|
| `task` | ForeignKey | Related task |
| `outcome` | CharField | won/lost/expired/cancelled |
| `actual_amount` | Decimal | Actual revenue (if won) |
| `expected_amount` | Decimal | Expected revenue |
| `reason` | TextField | Why lost/cancelled |
| `lessons_learned` | TextField | What we learned |

### OpportunityDigest
Weekly digest records for #boardroom.

| Field | Type | Purpose |
|-------|------|---------|
| `period_start/end` | DateTime | Digest period |
| `stats` | JSONField | Full statistics |
| `top_opportunities` | JSONField | Best opportunities |
| `posted_to_discord` | Boolean | Success flag |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/opportunity-tasks/` | GET | List tasks with filters |
| `/api/opportunity-tasks/stats/` | GET | Pipeline statistics |
| `/api/opportunity-tasks/<id>/` | GET | Task details |
| `/api/opportunity-tasks/<id>/accept/` | POST | Accept task |
| `/api/opportunity-tasks/<id>/apply/` | POST | Mark as applied |
| `/api/opportunity-tasks/<id>/won/` | POST | Mark as won (creates revenue) |
| `/api/opportunity-tasks/<id>/lost/` | POST | Mark as lost |
| `/api/opportunity-tasks/<id>/action-items/` | POST | Update checklist |

### Filter Parameters
- `?status=pending` - Filter by status
- `?priority=high` - Filter by priority
- `?category=freelance` - Filter by category

---

## Agent Linking Logic

Opportunities are automatically linked to relevant agents based on type:

| Opportunity Type | Primary Agent | Additional Agents |
|------------------|---------------|-------------------|
| freelance | ResearchAgent | ContentStrategyAgent, SEOOptimizerAgent |
| digital_products | ContentStrategyAgent | SEOOptimizerAgent, SocialMediaAgent |
| content | ContentStrategyAgent | SEOOptimizerAgent, CreativeDirectorAgent |
| consulting | ResearchAgent | CTOAgent, BrandStrategyAgent |
| investment | ResearchAgent | TrendAnalysisAgent, CompetitorAnalysisAgent |
| Default | ResearchAgent | ContentStrategyAgent |

---

## Auto-Task Creation

Tasks are automatically created when:
1. Opportunity scores 70+/100 (7+/10 normalized)
2. Opportunity doesn't already have a task
3. User is authenticated

**Trigger:** `opportunity_score()` in `views_opportunity.py`

```python
# Session 425: Auto-create tasks for high-value opportunities
if high_value_opportunities and user:
    for opp_data in high_value_opportunities:
        opp = Opportunity.objects.get(id=opp_data['opportunity_id'])
        if not hasattr(opp, 'task'):
            OpportunityTask.create_from_opportunity(
                opportunity=opp,
                score_data={
                    'score': opp_data['score'],
                    'confidence': opp_data.get('confidence', 0.8)
                }
            )
```

---

## Weekly Digest

### Celery Task
`generate_weekly_opportunity_digest()` runs every Sunday at 10 AM.

### Schedule
```python
'weekly-opportunity-digest': {
    'task': 'core.tasks.generate_weekly_opportunity_digest',
    'schedule': crontab(day_of_week=0, hour=10, minute=0),
}
```

### Discord Embed
Posts to #boardroom with:
- Total opportunities found
- High-value count (70+)
- Tasks created/won/lost
- Total revenue generated
- Win rate percentage
- Top opportunities by score
- Breakdown by category

---

## Files Modified

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Added OpportunityTask, OpportunityOutcome, OpportunityDigest models |
| `core/migrations/0081_session_425_opportunity_pipeline.py` | New migration |
| `core/migrations/0012_...` | Fixed broken RemoveField operations |
| `core/views_opportunity.py` | Added 8 API endpoints + auto-task creation |
| `core/urls.py` | Added URL routes for new endpoints |
| `core/services/discord_notifications.py` | Added `send_weekly_opportunity_digest()` |
| `core/tasks.py` | Added `generate_weekly_opportunity_digest()` task |
| `core/celery.py` | Added beat schedule for weekly digest |

---

## Testing

```bash
# Verify models
python manage.py shell -c "from core.models_unified_system import OpportunityTask, OpportunityOutcome, OpportunityDigest; print('Models OK')"

# Verify API endpoints
python manage.py shell -c "from core.views_opportunity import opportunity_task_list, opportunity_task_won; print('Endpoints OK')"

# Test weekly digest manually
python manage.py shell -c "from core.tasks import generate_weekly_opportunity_digest; generate_weekly_opportunity_digest()"

# List all tasks
curl http://localhost:8000/api/opportunity-tasks/

# Get pipeline stats
curl http://localhost:8000/api/opportunity-tasks/stats/
```

---

## Usage Flow

1. **Discovery:** Spider data feeds to OpportunityScoringAgent
2. **Scoring:** Opportunities scored 0-100
3. **Task Creation:** High-scoring (70+) auto-create tasks
4. **Agent Assignment:** Relevant agents linked based on type
5. **User Action:** Accept → Apply → Track outcome
6. **Outcome:** Mark won/lost with details
7. **Revenue:** Won tasks create Revenue records
8. **Learning:** Outcomes stored for future optimization
9. **Digest:** Weekly summary to #boardroom

---

## Next Session: 426

**Topic:** Basic Discord Bot Commands

**Goals:**
- Set up discord.py bot framework
- Implement `/status` - System health check
- Implement `/agents` - List active agents
- Implement `/trending` - Get trending spider data
- Implement `/help` - Command reference

---

## Key Takeaways

1. **Factory Pattern:** `create_from_opportunity()` encapsulates task creation logic
2. **Status Machine:** Clear state transitions (pending → accepted → applied → won/lost)
3. **Revenue Attribution:** Direct link from opportunity → task → outcome → revenue
4. **Weekly Cadence:** Automated digest keeps stakeholders informed
5. **Agent Matching:** Deterministic mapping of opportunity types to agent specialties

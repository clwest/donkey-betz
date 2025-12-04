# SESSION 326: PROJECT-AGENT LEARNING BRIDGE

## Comprehensive Implementation Plan

**Session:** 326
**Date:** December 3, 2025
**Focus:** Connecting Projects with Agent Learning for Unified Intelligence
**Prerequisites:** Session 303 (Unified Intelligence Search), Session 325 (Business Research Unified)

---

## 1. THE PROBLEM

Currently we have three powerful but **disconnected** systems:

```
CURRENT STATE (Disconnected):

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     SPIDERS     │     │     AGENTS      │     │    PROJECTS     │
│                 │     │                 │     │                 │
│ • 74 spiders    │     │ • 198 agents    │     │ • Research      │
│ • 7,900+ data   │     │ • Learning cycle│     │ • Competitor    │
│ • Real sources  │     │ • Knowledge     │     │ • Customer      │
│                 │     │   transfers     │     │   analysis      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                         NOT CONNECTED!

- Spider data doesn't prioritize based on active projects
- Agent learning doesn't enhance project research
- Project research doesn't become agent knowledge
- User feedback doesn't train the system
```

---

## 2. THE SOLUTION

Create a unified intelligence system with bidirectional learning:

```
GOAL STATE (Connected):

                          ┌─────────────────────────┐
                          │   PROJECT-AGENT BRIDGE  │
                          │                         │
                          │  • Converts research    │
                          │    to agent knowledge   │
                          │  • Applies user feedback│
                          │  • Prioritizes spiders  │
                          └───────────┬─────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│     SPIDERS     │◄────────►│     AGENTS      │◄────────►│    PROJECTS     │
│                 │          │                 │          │                 │
│ Priority based  │          │ Learn from      │          │ Enhanced by     │
│ on active       │          │ project         │          │ agent           │
│ projects        │          │ research        │          │ knowledge       │
└─────────────────┘          └─────────────────┘          └─────────────────┘
         │                            │                            │
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────────┐
                          │    FEEDBACK LOOP        │
                          │                         │
                          │  User Accept/Reject     │
                          │  → Adjusts confidence   │
                          │  → Improves future      │
                          │    research             │
                          └─────────────────────────┘
```

---

## 3. DATA FLOW DIAGRAMS

### 3.1 Research → Knowledge Flow

```
User creates project     CompetitorAnalysis or      BusinessResearchResult
with research topic  →   CustomerResearch Agent  →  saved with project_id
                         executes
                                                           │
                                                           ▼
                                                    ┌──────────────┐
                                                    │ ProjectAgent │
                                                    │ Bridge       │
                                                    │ Service      │
                                                    └──────┬───────┘
                                                           │
                              ┌────────────────────────────┼────────────────────────────┐
                              │                            │                            │
                              ▼                            ▼                            ▼
                    ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
                    │ AgentKnowledge  │          │ SpiderPriority  │          │ Learning Event  │
                    │ Source created  │          │ Updated for     │          │ Broadcast via   │
                    │ from research   │          │ project topics  │          │ WebSocket       │
                    └─────────────────┘          └─────────────────┘          └─────────────────┘
```

### 3.2 Feedback → Learning Flow

```
User reviews research    ProjectResearchFeedback    FeedbackLearning
in project details   →   created with rating    →   Service processes
                                                           │
                                                           ▼
                    ┌──────────────────────────────────────────────────────┐
                    │                                                      │
                    ▼                                                      ▼
          ┌─────────────────┐                                    ┌─────────────────┐
          │ AgentKnowledge  │                                    │ Pattern         │
          │ Source          │                                    │ Detection       │
          │ confidence      │                                    │                 │
          │ adjusted        │                                    │ "User prefers   │
          │ (+0.2 accept)   │                                    │  recent data"   │
          │ (-0.3 reject)   │                                    │ "Reject outdated│
          └─────────────────┘                                    │  competitor     │
                                                                 │  info"          │
                                                                 └─────────────────┘
```

### 3.3 Spider Prioritization Flow

```
Every 6 hours:           SpiderPriorityEngine       Spider scheduler
Celery Beat runs     →   scans active projects  →   uses priorities
                                   │
                                   ▼
                         ┌─────────────────┐
                         │ Project: "AI    │
                         │ Podcast Tools"  │
                         │                 │
                         │ Topics:         │
                         │ - AI            │
                         │ - podcasting    │
                         │ - content       │
                         │   creation      │
                         └────────┬────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
   │ Tech spiders  │     │ News spiders  │     │ Reddit subs   │
   │ weight: 2.5x  │     │ weight: 1.5x  │     │ weight: 2.0x  │
   │               │     │               │     │               │
   │ • HackerNews  │     │ • TechCrunch  │     │ • r/podcasting│
   │ • Dev.to      │     │ • Axios       │     │ • r/artificial│
   │ • ProductHunt │     │ • TheVerge    │     │ • r/content   │
   └───────────────┘     └───────────────┘     └───────────────┘
```

---

## 4. DATABASE MODEL CHANGES

### 4.1 New Model: ProjectResearchFeedback

**Location:** `core/models_unified_system.py`

```python
class ProjectResearchFeedback(models.Model):
    """
    Session 326: Track user feedback on research results.

    Enables:
    1. Accept/reject tracking per research item
    2. Confidence score adjustment in AgentKnowledgeSource
    3. Pattern learning for agent improvement
    """

    FEEDBACK_TYPE_CHOICES = [
        ('accept', 'Accepted - Useful'),
        ('reject', 'Rejected - Not Useful'),
        ('partial', 'Partially Useful'),
        ('starred', 'Starred - Excellent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='research_feedback'
    )
    research = models.ForeignKey(
        'core.BusinessResearchResult',
        on_delete=models.CASCADE,
        related_name='feedback',
        null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    rating = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    reason = models.TextField(blank=True)
    feedback_context = models.JSONField(default=dict)

    applied_to_knowledge = models.BooleanField(default=False)
    knowledge_delta = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
```

### 4.2 New Model: ProjectSpiderPriority

**Location:** `core/models_unified_system.py`

```python
class ProjectSpiderPriority(models.Model):
    """
    Session 326: Link projects to spider categories for prioritization.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    project = models.ForeignKey(
        'core.PartnershipProject',
        on_delete=models.CASCADE,
        related_name='spider_priorities'
    )
    spider_category = models.ForeignKey(
        'core.SpiderCategory',
        on_delete=models.CASCADE
    )

    priority_weight = models.FloatField(default=1.0)
    matched_keywords = ArrayField(models.CharField(max_length=100), default=list)

    data_used_count = models.IntegerField(default=0)
    useful_data_count = models.IntegerField(default=0)
    is_auto_detected = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def effectiveness_score(self):
        if self.data_used_count == 0:
            return 0.5
        return self.useful_data_count / self.data_used_count
```

### 4.3 Extend AgentKnowledgeSource

**Add fields to existing model:**

```python
# Session 326: Project linkage
source_project = models.ForeignKey(
    'core.PartnershipProject',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='derived_knowledge'
)
source_research = models.ForeignKey(
    'core.BusinessResearchResult',
    on_delete=models.SET_NULL,
    null=True, blank=True
)

# Feedback-adjusted metrics
feedback_positive = models.IntegerField(default=0)
feedback_negative = models.IntegerField(default=0)
feedback_adjusted_confidence = models.FloatField(null=True, blank=True)
```

---

## 5. NEW SERVICES

### 5.1 ProjectResearchBridge

**Location:** `core/services/project_research_bridge.py`

**Responsibilities:**
- Convert BusinessResearchResult → AgentKnowledgeSource
- Apply user feedback to adjust confidence
- Detect patterns in feedback
- Trigger spider priority recalculation

**Key Methods:**
```python
class ProjectResearchBridge:
    def research_to_knowledge(self, research: BusinessResearchResult, project: PartnershipProject) -> List[AgentKnowledgeSource]
    def apply_feedback(self, feedback: ProjectResearchFeedback) -> Dict[str, Any]
    def get_project_knowledge_stats(self, project_id: str) -> Dict[str, Any]
    def recalculate_priorities(self, project: PartnershipProject) -> None
```

### 5.2 SpiderPriorityEngine

**Location:** `core/services/spider_priority_engine.py`

**Responsibilities:**
- Scan active projects for topics
- Match topics to spider categories
- Calculate priority weights
- Influence spider scheduling

**Key Methods:**
```python
class SpiderPriorityEngine:
    def calculate_priorities(self) -> Dict[str, float]
    def get_priority_for_spider(self, spider_name: str) -> float
    def update_project_priorities(self, project: PartnershipProject) -> None
    def detect_topics(self, text: str) -> List[str]
```

### 5.3 FeedbackLearningService

**Location:** `core/services/feedback_learning_service.py`

**Responsibilities:**
- Process accept/reject feedback
- Update AgentKnowledgeSource confidence
- Detect feedback patterns
- Generate learning recommendations

---

## 6. IMPLEMENTATION ORDER

### Phase 1: Database Models (30 min)
- [ ] Add `ProjectResearchFeedback` model
- [ ] Add `ProjectSpiderPriority` model
- [ ] Extend `AgentKnowledgeSource` with project fields
- [ ] Run migrations

### Phase 2: ProjectResearchBridge Service (1 hour)
- [ ] Create `core/services/project_research_bridge.py`
- [ ] Implement `research_to_knowledge()` conversion
- [ ] Implement `apply_feedback()` for learning
- [ ] Add Celery task for async processing

### Phase 3: Spider Prioritization (45 min)
- [ ] Create `core/services/spider_priority_engine.py`
- [ ] Implement topic-to-category matching
- [ ] Modify spider tasks to check priorities
- [ ] Add periodic priority recalculation task

### Phase 4: Feedback API Endpoints (30 min)
- [ ] Create `core/views_research_feedback.py`
- [ ] Add POST `/api/research/feedback/`
- [ ] Add GET `/api/research/{id}/feedback/`
- [ ] Add to `core/urls.py`

### Phase 5: Frontend UI (45 min)
- [ ] Add Accept/Reject buttons to research cards
- [ ] Add rating component (1-5 stars)
- [ ] Add feedback form modal
- [ ] Wire up API calls

### Phase 6: Learning Loop Integration (30 min)
- [ ] Modify `run_agent_learning_cycle` to include project knowledge
- [ ] Add feedback-based confidence weighting
- [ ] Add logging and monitoring

### Phase 7: Testing & Verification (30 min)
- [ ] Test research → knowledge conversion
- [ ] Test feedback → confidence adjustment
- [ ] Test spider prioritization
- [ ] End-to-end flow test

---

## 7. API ENDPOINTS

### Submit Research Feedback
```
POST /api/research/feedback/

Request:
{
    "project_id": "uuid",
    "research_id": "uuid",
    "feedback_type": "accept" | "reject" | "partial" | "starred",
    "rating": 1-5,
    "reason": "Optional explanation",
    "context": {"section": "competitors", "item": "Jasper AI"}
}

Response:
{
    "success": true,
    "feedback_id": "uuid",
    "knowledge_impact": {
        "updated_sources": 3,
        "avg_confidence_delta": -0.15
    }
}
```

### Get Project Learning Stats
```
GET /api/projects/{id}/learning/

Response:
{
    "project_id": "uuid",
    "knowledge_generated": 12,
    "feedback_given": 8,
    "acceptance_rate": 0.75,
    "spider_priorities": [
        {"category": "tech", "weight": 2.5},
        {"category": "news", "weight": 1.5}
    ],
    "learning_recommendations": [...]
}
```

---

## 8. CELERY TASKS

### New Tasks to Add

```python
# core/tasks.py

@shared_task
def process_research_feedback(feedback_id: str):
    """Process a research feedback submission."""
    pass

@shared_task
def recalculate_spider_priorities():
    """Recalculate spider priorities based on active projects. Runs every 6 hours."""
    pass

@shared_task
def sync_project_knowledge():
    """Sync BusinessResearchResult to AgentKnowledgeSource. Runs every 30 minutes."""
    pass
```

### Celery Beat Schedule Additions

```python
# core/celery.py

'sync-project-knowledge': {
    'task': 'core.tasks.sync_project_knowledge',
    'schedule': crontab(minute='*/30'),
},
'recalculate-spider-priorities': {
    'task': 'core.tasks.recalculate_spider_priorities',
    'schedule': crontab(hour='*/6'),
},
```

---

## 9. CRITICAL FILES

| File | Changes |
|------|---------|
| `core/models_unified_system.py` | Add 2 new models, extend AgentKnowledgeSource |
| `core/services/project_research_bridge.py` | NEW: Central bridge service |
| `core/services/spider_priority_engine.py` | NEW: Spider prioritization |
| `core/services/feedback_learning_service.py` | NEW: Feedback processing |
| `core/tasks.py` | Add 3 new tasks, modify learning cycle |
| `core/celery.py` | Add new scheduled tasks |
| `core/views_research_feedback.py` | NEW: API endpoints |
| `core/urls.py` | Add new routes |
| `ai_core/templates/ai_image_studio.html` | Add feedback UI |

---

## 10. SUCCESS METRICS

After implementation, we should see:

1. **Knowledge Growth**: AgentKnowledgeSource entries increase with each project research
2. **Learning Activity**: Learning feed shows project-derived knowledge transfers
3. **Spider Relevance**: Spider data becomes more relevant to active projects
4. **Feedback Loop**: User feedback visibly affects future research quality
5. **Confidence Scores**: Knowledge confidence adjusts based on feedback patterns

---

## 11. TESTING CHECKLIST

- [ ] Create project with research topic
- [ ] Run competitor analysis for project
- [ ] Verify BusinessResearchResult linked to project
- [ ] Verify AgentKnowledgeSource created from research
- [ ] Submit accept feedback
- [ ] Verify confidence score increased
- [ ] Submit reject feedback
- [ ] Verify confidence score decreased
- [ ] Check spider priority reflects project topics
- [ ] Verify run_agent_learning_cycle transfers project knowledge
- [ ] Test end-to-end: new project → research → feedback → improved future research

---

**Status:** Ready for Implementation
**Next Step:** Phase 1 - Database Models

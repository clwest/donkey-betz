# Phase B: Execution Pipeline

**Priority:** 2 of 4
**Estimated Scope:** Medium-Large
**Dependencies:** Phase A (Artifact Extraction) must be complete

---

## Problem Statement

When a user approves an artifact (proposal, experiment, action item), nothing happens. The artifact is marked "approved" but there's no mechanism to:
- Create a project or task from it
- Assign it to an agent for execution
- Track progress toward completion
- Report outcomes back to the system

Approved items sit in limbo - decided but never executed.

---

## Goal

Create an execution pipeline that:
1. Takes approved artifacts and creates executable work items
2. Assigns work to appropriate agents
3. Tracks execution progress
4. Records outcomes for learning

---

## Data Model

### New Model: `ExecutionItem`

```python
# core/models_execution.py

class ExecutionItem(models.Model):
    """
    An executable work item created from an approved artifact.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Source
    artifact = models.OneToOneField(
        'ConversationArtifact',
        on_delete=models.CASCADE,
        related_name='execution'
    )

    # Execution details
    EXECUTION_TYPES = [
        ('project', 'Create Project'),        # Creates a PartnershipProject
        ('experiment', 'Run Experiment'),      # Tracked A/B test
        ('research', 'Research Task'),         # Agent gathers information
        ('analysis', 'Analysis Task'),         # Agent analyzes data
        ('implementation', 'Implementation'),  # Build something
        ('monitoring', 'Monitoring Task'),     # Ongoing watch
    ]
    execution_type = models.CharField(max_length=20, choices=EXECUTION_TYPES)

    # Assignment
    assigned_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, related_name='assigned_executions')
    assigned_at = models.DateTimeField(null=True)

    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Start'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Timeline
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    due_date = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)

    # Execution plan
    execution_plan = models.JSONField(default=dict)
    # Example:
    # {
    #   "steps": [
    #     {"description": "Gather competitor data", "status": "pending"},
    #     {"description": "Analyze pricing patterns", "status": "pending"},
    #     {"description": "Generate report", "status": "pending"}
    #   ],
    #   "resources_needed": ["competitor_spider", "analysis_agent"],
    #   "estimated_duration": "3 days"
    # }

    # Progress tracking
    progress_percentage = models.IntegerField(default=0)
    progress_notes = models.JSONField(default=list)
    # Example: [{"timestamp": "...", "note": "Gathered 150 data points", "percentage": 30}]

    # Outcome
    outcome = models.JSONField(null=True)
    # Example for experiment:
    # {
    #   "result": "success",
    #   "metrics": {"conversion": 0.12, "revenue": 4500},
    #   "conclusion": "Mid-tier pricing performed 23% better",
    #   "recommendations": ["Roll out $19 tier", "Sunset $9 tier"]
    # }

    # Linked project (if created)
    project = models.ForeignKey('PartnershipProject', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
```

### New Model: `ExecutionUpdate`

```python
class ExecutionUpdate(models.Model):
    """
    Progress update on an execution item.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    execution = models.ForeignKey(ExecutionItem, on_delete=models.CASCADE, related_name='updates')

    created_at = models.DateTimeField(auto_now_add=True)
    created_by_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True)

    update_type = models.CharField(max_length=20, choices=[
        ('progress', 'Progress Update'),
        ('blocker', 'Blocker Identified'),
        ('milestone', 'Milestone Reached'),
        ('completion', 'Completed'),
        ('failure', 'Failed'),
    ])

    title = models.CharField(max_length=200)
    description = models.TextField()
    data = models.JSONField(default=dict)  # Type-specific data

    class Meta:
        ordering = ['created_at']
```

---

## Execution Service

### New Service: `ExecutionService`

```python
# core/services/execution_service.py

class ExecutionService:
    """
    Manages execution of approved artifacts.
    """

    def create_execution_from_artifact(self, artifact: ConversationArtifact) -> ExecutionItem:
        """
        Create an execution item from an approved artifact.

        1. Determine execution type from artifact type
        2. Select appropriate agent
        3. Generate execution plan
        4. Create ExecutionItem
        """
        pass

    def _determine_execution_type(self, artifact: ConversationArtifact) -> str:
        """
        Map artifact types to execution types:
        - proposal → project or implementation
        - experiment → experiment
        - risk → monitoring
        - data_spec → implementation
        - action_item → research or analysis
        """
        pass

    def _select_agent(self, artifact: ConversationArtifact, execution_type: str) -> Agent:
        """
        Select best agent for execution based on:
        - Artifact source agent (they proposed it, they might execute it)
        - Agent specializations matching the task
        - Agent current workload
        - Agent expertise score on related topics
        """
        pass

    def _generate_execution_plan(self, artifact: ConversationArtifact, execution_type: str) -> dict:
        """
        Use LLM to generate execution plan:
        - Break down into steps
        - Estimate duration
        - Identify resources needed
        """
        pass

    def start_execution(self, execution_id: str) -> bool:
        """
        Begin execution of an item.
        - Update status to 'in_progress'
        - Notify assigned agent
        - Schedule first step
        """
        pass

    def update_progress(self, execution_id: str, percentage: int, note: str) -> ExecutionUpdate:
        """
        Record progress on an execution.
        """
        pass

    def complete_execution(self, execution_id: str, outcome: dict) -> ExecutionItem:
        """
        Mark execution complete with outcome.
        - Update status to 'completed'
        - Record outcome
        - Trigger learning (Phase D)
        """
        pass

    def check_stale_executions(self) -> List[ExecutionItem]:
        """
        Find executions that haven't progressed.
        - No update in X days
        - Past due date
        """
        pass
```

---

## Automatic Execution Trigger

When an artifact is approved, automatically create execution:

```python
# In core/views_artifacts.py or via signal

def decide_artifact(request, artifact_id):
    artifact = ConversationArtifact.objects.get(id=artifact_id)
    decision = request.POST.get('decision')

    artifact.status = decision
    artifact.decided_at = timezone.now()
    artifact.save()

    # If approved, create execution item
    if decision == 'approved':
        from core.services.execution_service import execution_service
        execution = execution_service.create_execution_from_artifact(artifact)

        # Optionally auto-start certain types
        if artifact.artifact_type in ['action_item', 'research']:
            execution_service.start_execution(execution.id)

    return JsonResponse({'success': True, 'execution_id': str(execution.id) if decision == 'approved' else None})
```

---

## Celery Tasks

### Execution Tasks

```python
# In core/tasks.py

@shared_task
def process_pending_executions():
    """
    Start executions that are pending and ready.

    Run every 10 minutes.
    """
    from core.services.execution_service import execution_service

    pending = ExecutionItem.objects.filter(
        status='pending',
        assigned_agent__isnull=False
    )

    for execution in pending:
        execution_service.start_execution(execution.id)


@shared_task
def execute_step(execution_id: str, step_index: int):
    """
    Execute a specific step of an execution plan.

    Called by the execution pipeline as it progresses.
    """
    pass


@shared_task
def check_stale_executions():
    """
    Find and alert on stalled executions.

    Run daily.
    """
    from core.services.execution_service import execution_service

    stale = execution_service.check_stale_executions()

    for execution in stale:
        # Create alert or notification
        # Could escalate to human attention
        pass


@shared_task
def run_experiment_cycle(execution_id: str):
    """
    For experiment-type executions:
    - Collect metrics
    - Check for statistical significance
    - Update progress
    - Complete when ready
    """
    pass
```

---

## Agent Execution Interface

Agents need a way to report on their executions:

```python
# In core/agents/base_agent.py

class BaseAgent:
    def report_execution_progress(self, execution_id: str, percentage: int, note: str):
        """
        Report progress on an assigned execution.
        """
        from core.services.execution_service import execution_service
        execution_service.update_progress(execution_id, percentage, note)

    def complete_execution(self, execution_id: str, outcome: dict):
        """
        Mark an execution as complete with results.
        """
        from core.services.execution_service import execution_service
        execution_service.complete_execution(execution_id, outcome)

    def get_assigned_executions(self) -> List[ExecutionItem]:
        """
        Get list of executions assigned to this agent.
        """
        return ExecutionItem.objects.filter(
            assigned_agent__name=self.name,
            status__in=['pending', 'in_progress']
        )
```

---

## API Endpoints

```python
# In core/urls.py

# List all executions
path('api/executions/', views_execution.list_executions, name='list-executions'),

# Get execution details
path('api/executions/<uuid:execution_id>/', views_execution.get_execution, name='get-execution'),

# Update execution progress (for agents or manual)
path('api/executions/<uuid:execution_id>/progress/', views_execution.update_progress, name='update-progress'),

# Complete execution
path('api/executions/<uuid:execution_id>/complete/', views_execution.complete_execution, name='complete-execution'),

# Get agent's assigned executions
path('api/agents/<uuid:agent_id>/executions/', views_execution.agent_executions, name='agent-executions'),
```

---

## UI Integration

### Execution Dashboard

New section in Intelligence Command Center or separate tab:

```html
<!-- Execution Tracker -->
<div class="card">
    <div class="card-header">
        <h5>🚀 Active Executions</h5>
        <span class="badge bg-primary" id="exec-in-progress">0 in progress</span>
        <span class="badge bg-warning" id="exec-blocked">0 blocked</span>
    </div>
    <div class="card-body" id="executions-list">
        <!-- Execution cards -->
    </div>
</div>
```

### Execution Card Template

```html
<div class="execution-card" data-id="{id}">
    <div class="execution-header">
        <span class="badge badge-{execution_type}">{execution_type}</span>
        <span class="execution-title">{artifact.title}</span>
    </div>
    <div class="execution-assignment">
        Assigned to: {assigned_agent.name}
    </div>
    <div class="progress">
        <div class="progress-bar" style="width: {progress_percentage}%">
            {progress_percentage}%
        </div>
    </div>
    <div class="execution-status">
        Status: {status} | Due: {due_date}
    </div>
    <div class="execution-updates">
        <!-- Recent updates -->
    </div>
</div>
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `core/models_execution.py` | CREATE | ExecutionItem, ExecutionUpdate models |
| `core/services/execution_service.py` | CREATE | ExecutionService |
| `core/views_execution.py` | CREATE | API endpoints |
| `core/urls.py` | MODIFY | Add execution routes |
| `core/tasks.py` | MODIFY | Add execution tasks |
| `core/celery.py` | MODIFY | Add beat schedules |
| `core/agents/base_agent.py` | MODIFY | Add execution reporting methods |
| `ai_core/templates/...` | MODIFY | Add execution dashboard |
| `core/migrations/XXXX_execution.py` | CREATE | Database migration |

---

## Execution Type Handlers

Different artifact types need different execution approaches:

### Experiment Execution
```python
def execute_experiment(execution: ExecutionItem):
    """
    1. Set up experiment parameters
    2. Create tracking metrics
    3. Run data collection cycle
    4. Check for statistical significance
    5. Generate conclusion
    """
    pass
```

### Research Execution
```python
def execute_research(execution: ExecutionItem):
    """
    1. Identify relevant spiders
    2. Trigger targeted data collection
    3. Have agent analyze results
    4. Generate research report
    5. Add to knowledge base
    """
    pass
```

### Project Creation
```python
def execute_project_creation(execution: ExecutionItem):
    """
    1. Create PartnershipProject from artifact details
    2. Set up LivingProjectConfig
    3. Assign initial research tasks
    4. Link back to execution
    """
    pass
```

---

## Success Criteria

1. Approved artifacts automatically create execution items
2. Agents receive and can report on assigned executions
3. Progress is visible in UI
4. Completed executions have recorded outcomes
5. Stale executions are flagged

---

## Next Phase

Phase C (Weekly Synthesis) uses execution outcomes to generate insights about what's working and what's not.

---

**This phase transforms approved decisions into tracked, executable work.**

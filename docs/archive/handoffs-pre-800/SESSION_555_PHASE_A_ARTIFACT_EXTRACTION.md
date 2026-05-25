# Phase A: Conversation Artifact Extraction

**Priority:** 1 of 4 (Start Here)
**Estimated Scope:** Medium
**Dependencies:** None - this is foundational

---

## Problem Statement

Agent conversations contain valuable artifacts that are currently lost:
- Proposed experiments
- Risk assessments
- Data pipeline specifications
- Action items
- Open questions requiring decisions

After a conversation ends, these insights remain buried in conversation JSON, never surfaced for human action.

---

## Goal

Automatically extract actionable artifacts from completed agent conversations and store them in a structured format that can feed into the Boardroom decision queue.

---

## Data Model

### New Model: `ConversationArtifact`

```python
# core/models_conversation_artifacts.py

class ConversationArtifact(models.Model):
    """
    Extracted actionable item from an agent conversation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Source
    conversation = models.ForeignKey('AgentConversation', on_delete=models.CASCADE, related_name='artifacts')
    extracted_at = models.DateTimeField(auto_now_add=True)

    # Artifact details
    ARTIFACT_TYPES = [
        ('proposal', 'Proposal'),           # "We should do X"
        ('experiment', 'Experiment'),       # "Test X vs Y"
        ('risk', 'Risk Identified'),        # "Risk: X could happen"
        ('data_spec', 'Data/Pipeline Spec'),# Technical specification
        ('question', 'Open Question'),      # "We need to decide X"
        ('insight', 'Key Insight'),         # Important observation
        ('action_item', 'Action Item'),     # "Someone needs to do X"
    ]
    artifact_type = models.CharField(max_length=20, choices=ARTIFACT_TYPES)

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Attribution
    source_agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True)
    source_message_index = models.IntegerField(null=True)  # Which message in conversation

    # Extracted details (JSON for flexibility)
    details = models.JSONField(default=dict)
    # Examples:
    # For experiment: {"hypothesis": "...", "metrics": [...], "duration": "4 weeks"}
    # For risk: {"severity": "high", "mitigation": "...", "likelihood": "medium"}
    # For data_spec: {"components": [...], "technologies": [...]}

    # Decision tracking
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deferred', 'Deferred'),
        ('implemented', 'Implemented'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True)

    # Priority/scoring
    importance_score = models.FloatField(default=0.5)  # 0-1
    urgency_score = models.FloatField(default=0.5)     # 0-1

    class Meta:
        ordering = ['-extracted_at']
        indexes = [
            models.Index(fields=['status', 'artifact_type']),
            models.Index(fields=['importance_score']),
        ]
```

---

## Extraction Service

### New Service: `ArtifactExtractionService`

```python
# core/services/artifact_extraction.py

class ArtifactExtractionService:
    """
    Extracts actionable artifacts from completed agent conversations.
    """

    def extract_from_conversation(self, conversation_id: str) -> List[ConversationArtifact]:
        """
        Main extraction method. Called when a conversation completes.

        Returns list of extracted artifacts.
        """
        pass

    def _call_extraction_llm(self, conversation_text: str) -> dict:
        """
        Use GPT to identify artifacts in conversation.

        Prompt should ask for:
        - Proposals (things agents suggest doing)
        - Experiments (testable hypotheses)
        - Risks (concerns raised)
        - Data specs (technical designs)
        - Open questions (things needing human decision)
        - Action items (concrete next steps)
        """
        pass

    def _score_importance(self, artifact: dict, conversation: AgentConversation) -> float:
        """
        Score artifact importance based on:
        - How many agents agreed/referenced it
        - Agent seniority (COO > junior agent)
        - Topic relevance to active projects
        """
        pass
```

### Extraction Prompt Template

```
Analyze this agent conversation and extract actionable artifacts.

CONVERSATION:
{conversation_messages}

For each artifact found, provide:
1. type: proposal | experiment | risk | data_spec | question | action_item | insight
2. title: Short title (max 100 chars)
3. description: Full description
4. source_agent: Which agent proposed this
5. details: Structured details specific to type

Return as JSON array:
[
  {
    "type": "experiment",
    "title": "A/B test pricing tiers",
    "description": "Run 4-week experiment comparing $9/$19/$49 pricing...",
    "source_agent": "BrandIdentityAgent",
    "details": {
      "hypothesis": "Mid-tier ($19) will have highest conversion",
      "metrics": ["conversion_rate", "revenue_per_visitor", "churn_30d"],
      "duration": "4 weeks",
      "sample_size": "1000 visitors per variant"
    }
  },
  {
    "type": "risk",
    "title": "Sample size too small for conclusions",
    "description": "COO flags that 50 items from 11 sources is insufficient...",
    "source_agent": "COOAgent",
    "details": {
      "severity": "high",
      "likelihood": "confirmed",
      "mitigation": "Expand to 500+ items across 5 platforms"
    }
  }
]
```

---

## Celery Task

### New Task: `extract_conversation_artifacts`

```python
# In core/tasks.py

@shared_task
def extract_conversation_artifacts(conversation_id: str):
    """
    Extract artifacts from a completed conversation.

    Triggered when:
    - Conversation status changes to 'completed'
    - Or via scheduled batch processing of recent conversations
    """
    from core.services.artifact_extraction import extraction_service

    artifacts = extraction_service.extract_from_conversation(conversation_id)

    logger.info(f"Extracted {len(artifacts)} artifacts from conversation {conversation_id}")

    return {
        'conversation_id': conversation_id,
        'artifacts_extracted': len(artifacts),
        'by_type': Counter(a.artifact_type for a in artifacts)
    }


@shared_task
def batch_extract_artifacts(hours_back: int = 24):
    """
    Process conversations from last N hours that haven't been extracted.

    Run via Celery Beat every hour.
    """
    pass
```

### Celery Beat Schedule

```python
# In core/celery.py

'artifact-extraction-batch': {
    'task': 'core.tasks.batch_extract_artifacts',
    'schedule': crontab(minute=15),  # Every hour at :15
    'args': (24,),  # Last 24 hours
},
```

---

## API Endpoints

### New Endpoints

```python
# In core/urls.py

# List artifacts awaiting decision
path('api/artifacts/', views_artifacts.list_artifacts, name='list-artifacts'),

# Get artifact details
path('api/artifacts/<uuid:artifact_id>/', views_artifacts.get_artifact, name='get-artifact'),

# Decide on artifact (approve/reject/defer)
path('api/artifacts/<uuid:artifact_id>/decide/', views_artifacts.decide_artifact, name='decide-artifact'),

# Get artifacts by conversation
path('api/conversations/<uuid:conversation_id>/artifacts/', views_artifacts.conversation_artifacts, name='conversation-artifacts'),
```

### Response Format

```json
GET /api/artifacts/?status=pending&type=proposal

{
  "success": true,
  "artifacts": [
    {
      "id": "uuid",
      "type": "proposal",
      "title": "7-day data quality audit",
      "description": "...",
      "source_agent": "BrandIdentityAgent",
      "conversation_id": "uuid",
      "conversation_topic": "Panel: Sellfy Market Intelligence",
      "importance_score": 0.85,
      "extracted_at": "2025-12-25T17:30:00Z",
      "status": "pending"
    }
  ],
  "counts": {
    "pending": 12,
    "approved": 45,
    "rejected": 8
  }
}
```

---

## UI Integration

### Boardroom Enhancement

Add "Proposals Awaiting Decision" section alongside "Dreams Awaiting Decision":

```html
<!-- In intelligence_command_center.html -->

<div class="card" style="border: 2px solid #06b6d4;">
    <div class="card-header">
        <h5>📋 Proposals Awaiting Decision</h5>
        <span class="badge" id="proposals-pending-count">0 pending</span>
    </div>
    <div class="card-body" id="proposals-list">
        <!-- Artifact cards rendered here -->
    </div>
</div>
```

### Artifact Card Template

```html
<div class="artifact-card" data-id="{id}">
    <div class="artifact-header">
        <span class="badge badge-{type}">{type}</span>
        <span class="artifact-title">{title}</span>
    </div>
    <div class="artifact-source">
        From {source_agent} in "{conversation_topic}"
    </div>
    <div class="artifact-description">{description}</div>
    <div class="artifact-actions">
        <button onclick="decideArtifact('{id}', 'approved')">✓ Approve</button>
        <button onclick="decideArtifact('{id}', 'deferred')">⏸ Defer</button>
        <button onclick="decideArtifact('{id}', 'rejected')">✗ Reject</button>
    </div>
</div>
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `core/models_conversation_artifacts.py` | CREATE | ConversationArtifact model |
| `core/services/artifact_extraction.py` | CREATE | ArtifactExtractionService |
| `core/views_artifacts.py` | CREATE | API endpoints |
| `core/urls.py` | MODIFY | Add artifact routes |
| `core/tasks.py` | MODIFY | Add extraction tasks |
| `core/celery.py` | MODIFY | Add beat schedule |
| `ai_core/templates/components/panels/intelligence_command_center.html` | MODIFY | Add proposals section |
| `core/migrations/XXXX_conversation_artifacts.py` | CREATE | Database migration |

---

## Success Criteria

1. After a conversation completes, artifacts are extracted within 5 minutes
2. Artifacts appear in Boardroom under "Proposals Awaiting Decision"
3. User can approve/reject/defer artifacts
4. Extraction correctly identifies at least 80% of actionable items
5. No duplicate artifacts for same proposal

---

## Testing

```python
# Test extraction
def test_extract_artifacts():
    # Create a conversation with known proposals
    conversation = create_test_conversation_with_proposals()

    # Run extraction
    artifacts = extraction_service.extract_from_conversation(conversation.id)

    # Verify
    assert len(artifacts) >= 2
    assert any(a.artifact_type == 'proposal' for a in artifacts)
    assert any(a.artifact_type == 'risk' for a in artifacts)
```

---

## Next Phase

Once artifacts are being extracted and users can approve them, Phase B (Execution Pipeline) handles what happens when an artifact is approved.

---

**This phase transforms ephemeral conversations into persistent, actionable items.**

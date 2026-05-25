# Phase D: Human Feedback Loop

**Priority:** 4 of 4
**Estimated Scope:** Medium
**Dependencies:** Phases A, B, C should be complete for full value

---

## Problem Statement

Currently, human interaction with the system is passive:
- User watches agents talk
- User approves/rejects dreams
- User reads briefs

But there's no mechanism for the human to:
1. Ask agents to elaborate on something
2. Provide feedback on executed work ("this was useful" / "this was wrong")
3. Redirect agent focus ("stop researching X, focus on Y")
4. Inject domain expertise ("actually, the market works like this...")
5. Have that feedback influence future agent behavior

The system is a one-way broadcast, not a conversation.

---

## Goal

Create a feedback loop where:
1. Humans can respond to agent outputs
2. Feedback is recorded and structured
3. Agents learn from feedback
4. Future behavior is influenced by past feedback

---

## Data Model

### New Model: `HumanFeedback`

```python
# core/models_feedback.py

class HumanFeedback(models.Model):
    """
    Human feedback on agent outputs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Who gave feedback
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # What they're giving feedback on
    FEEDBACK_TARGETS = [
        ('conversation', 'Conversation'),
        ('artifact', 'Artifact'),
        ('execution', 'Execution'),
        ('dream', 'Dream'),
        ('brief', 'Brief'),
        ('knowledge', 'Knowledge Entry'),
        ('agent', 'Agent Overall'),
    ]
    target_type = models.CharField(max_length=20, choices=FEEDBACK_TARGETS)
    target_id = models.UUIDField()

    # Type of feedback
    FEEDBACK_TYPES = [
        ('rating', 'Quality Rating'),           # 1-5 stars
        ('correction', 'Correction'),           # "This is wrong because..."
        ('elaboration_request', 'Elaborate'),   # "Tell me more about..."
        ('direction', 'Direction Change'),      # "Focus on X instead"
        ('domain_knowledge', 'Domain Input'),   # "In my industry, X works like..."
        ('outcome_report', 'Outcome Report'),   # "We tried this, here's what happened"
        ('preference', 'Preference Signal'),    # "I prefer X over Y"
    ]
    feedback_type = models.CharField(max_length=25, choices=FEEDBACK_TYPES)

    # Feedback content
    rating = models.IntegerField(null=True)  # 1-5 for rating type
    content = models.TextField()             # Free text feedback
    structured_data = models.JSONField(default=dict)
    # Examples:
    # For correction: {"claim": "X is true", "correction": "Actually Y", "source": "..."}
    # For outcome: {"tried": "...", "result": "success/failure", "metrics": {...}}
    # For direction: {"stop": ["topic1"], "focus": ["topic2", "topic3"]}

    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending Processing'),
        ('processed', 'Processed'),
        ('applied', 'Applied to Agent'),
        ('rejected', 'Rejected (invalid)'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(null=True)

    # Which agent(s) this feedback applies to
    target_agents = models.ManyToManyField('Agent', blank=True, related_name='received_feedback')

    # Impact tracking
    impact_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
```

### New Model: `AgentLearningFromFeedback`

```python
class AgentLearningFromFeedback(models.Model):
    """
    Records how an agent has learned from human feedback.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    agent = models.ForeignKey('Agent', on_delete=models.CASCADE, related_name='feedback_learnings')
    feedback = models.ForeignKey(HumanFeedback, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    # What the agent learned
    learning_type = models.CharField(max_length=20, choices=[
        ('correction', 'Corrected Knowledge'),
        ('preference', 'Learned Preference'),
        ('focus_shift', 'Shifted Focus'),
        ('domain_knowledge', 'New Domain Knowledge'),
        ('behavior_adjustment', 'Behavior Adjustment'),
    ])

    description = models.TextField()
    applied_to_knowledge = models.ForeignKey('AgentKnowledgeSource', null=True, on_delete=models.SET_NULL)

    # Verification
    verified_by_user = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
```

---

## Feedback Service

### New Service: `FeedbackService`

```python
# core/services/feedback_service.py

class FeedbackService:
    """
    Processes human feedback and applies it to agents.
    """

    def submit_feedback(
        self,
        user,
        target_type: str,
        target_id: str,
        feedback_type: str,
        content: str,
        rating: int = None,
        structured_data: dict = None
    ) -> HumanFeedback:
        """
        Submit new feedback.
        """
        feedback = HumanFeedback.objects.create(
            user=user,
            target_type=target_type,
            target_id=target_id,
            feedback_type=feedback_type,
            content=content,
            rating=rating,
            structured_data=structured_data or {}
        )

        # Identify target agents
        target_agents = self._identify_target_agents(target_type, target_id)
        feedback.target_agents.set(target_agents)

        # Queue for processing
        process_feedback.delay(str(feedback.id))

        return feedback

    def _identify_target_agents(self, target_type: str, target_id: str) -> List[Agent]:
        """
        Identify which agents should receive this feedback.
        """
        if target_type == 'conversation':
            conv = AgentConversation.objects.get(id=target_id)
            return list(conv.participants.all())
        elif target_type == 'artifact':
            artifact = ConversationArtifact.objects.get(id=target_id)
            return [artifact.source_agent] if artifact.source_agent else []
        elif target_type == 'dream':
            dream = AgentDream.objects.get(id=target_id)
            return [dream.agent] if dream.agent else []
        elif target_type == 'agent':
            return [Agent.objects.get(id=target_id)]
        return []

    def process_feedback(self, feedback_id: str) -> dict:
        """
        Process feedback and apply to agents.

        1. Analyze feedback content
        2. Determine how to apply
        3. Update agent knowledge/behavior
        4. Record learning
        """
        feedback = HumanFeedback.objects.get(id=feedback_id)

        if feedback.feedback_type == 'correction':
            return self._apply_correction(feedback)
        elif feedback.feedback_type == 'elaboration_request':
            return self._trigger_elaboration(feedback)
        elif feedback.feedback_type == 'direction':
            return self._apply_direction(feedback)
        elif feedback.feedback_type == 'domain_knowledge':
            return self._inject_domain_knowledge(feedback)
        elif feedback.feedback_type == 'outcome_report':
            return self._record_outcome(feedback)
        elif feedback.feedback_type == 'rating':
            return self._apply_rating(feedback)
        elif feedback.feedback_type == 'preference':
            return self._record_preference(feedback)

    def _apply_correction(self, feedback: HumanFeedback) -> dict:
        """
        Apply a correction to agent knowledge.

        1. Find the incorrect knowledge entry
        2. Mark it as corrected
        3. Create new correct entry
        4. Record learning
        """
        for agent in feedback.target_agents.all():
            # Find related knowledge
            related_knowledge = AgentKnowledgeSource.objects.filter(
                agent=agent,
                id=feedback.target_id  # If target was knowledge
            ).first()

            if related_knowledge:
                # Deactivate incorrect knowledge
                related_knowledge.is_active = False
                related_knowledge.save()

                # Create corrected knowledge
                corrected = AgentKnowledgeSource.objects.create(
                    agent=agent,
                    title=f"[Corrected] {related_knowledge.title}",
                    summary=feedback.content,
                    knowledge_type='correction',
                    confidence_score=0.95,  # High confidence - human verified
                    source_type='human_feedback',
                )

                # Record learning
                AgentLearningFromFeedback.objects.create(
                    agent=agent,
                    feedback=feedback,
                    learning_type='correction',
                    description=f"Corrected: {related_knowledge.title}",
                    applied_to_knowledge=corrected
                )

        feedback.status = 'applied'
        feedback.processed_at = timezone.now()
        feedback.save()

        return {'status': 'applied', 'agents_updated': feedback.target_agents.count()}

    def _trigger_elaboration(self, feedback: HumanFeedback) -> dict:
        """
        Request agents to elaborate on a topic.

        Creates a directed conversation/dream about the topic.
        """
        topic = feedback.content

        # Trigger directed dream or conversation
        from core.tasks import generate_directed_dreams
        generate_directed_dreams.delay(
            topic=topic,
            agent_ids=[str(a.id) for a in feedback.target_agents.all()],
            dreams_per_agent=1
        )

        feedback.status = 'processed'
        feedback.processed_at = timezone.now()
        feedback.save()

        return {'status': 'elaboration_triggered', 'topic': topic}

    def _apply_direction(self, feedback: HumanFeedback) -> dict:
        """
        Apply focus direction to agents.

        Updates agent priorities/focus areas.
        """
        direction = feedback.structured_data
        stop_topics = direction.get('stop', [])
        focus_topics = direction.get('focus', [])

        for agent in feedback.target_agents.all():
            # Update agent focus (this might update a config or prompt)
            # Implementation depends on how agents store focus

            AgentLearningFromFeedback.objects.create(
                agent=agent,
                feedback=feedback,
                learning_type='focus_shift',
                description=f"Stop: {stop_topics}, Focus: {focus_topics}"
            )

        feedback.status = 'applied'
        feedback.processed_at = timezone.now()
        feedback.save()

        return {'status': 'applied', 'agents_updated': feedback.target_agents.count()}

    def _inject_domain_knowledge(self, feedback: HumanFeedback) -> dict:
        """
        Add human domain expertise to agent knowledge.
        """
        for agent in feedback.target_agents.all():
            knowledge = AgentKnowledgeSource.objects.create(
                agent=agent,
                title=f"Domain Knowledge: {feedback.content[:50]}",
                summary=feedback.content,
                knowledge_type='expert_input',
                confidence_score=0.95,  # High confidence - from human expert
                source_type='human_feedback',
                key_insights=feedback.structured_data.get('key_points', [])
            )

            AgentLearningFromFeedback.objects.create(
                agent=agent,
                feedback=feedback,
                learning_type='domain_knowledge',
                description=feedback.content[:200],
                applied_to_knowledge=knowledge
            )

        feedback.status = 'applied'
        feedback.processed_at = timezone.now()
        feedback.save()

        return {'status': 'applied', 'knowledge_created': feedback.target_agents.count()}

    def _record_outcome(self, feedback: HumanFeedback) -> dict:
        """
        Record outcome of an executed action.

        This is critical for closing the learning loop.
        """
        outcome_data = feedback.structured_data
        result = outcome_data.get('result')  # success/failure/partial
        metrics = outcome_data.get('metrics', {})
        learnings = outcome_data.get('learnings', '')

        # Find the execution this relates to
        if feedback.target_type == 'execution':
            execution = ExecutionItem.objects.get(id=feedback.target_id)
            execution.outcome = outcome_data
            execution.save()

        # Create knowledge from outcome
        for agent in feedback.target_agents.all():
            knowledge = AgentKnowledgeSource.objects.create(
                agent=agent,
                title=f"Outcome: {feedback.content[:50]}",
                summary=f"Result: {result}. {learnings}",
                knowledge_type='outcome',
                confidence_score=1.0,  # This is verified reality
                source_type='human_feedback',
                key_insights=metrics
            )

            AgentLearningFromFeedback.objects.create(
                agent=agent,
                feedback=feedback,
                learning_type='behavior_adjustment',
                description=f"Outcome recorded: {result}",
                applied_to_knowledge=knowledge
            )

        feedback.status = 'applied'
        feedback.processed_at = timezone.now()
        feedback.save()

        return {'status': 'applied', 'outcome_recorded': True}
```

---

## Celery Tasks

```python
# In core/tasks.py

@shared_task
def process_feedback(feedback_id: str):
    """
    Process a single feedback item.
    """
    from core.services.feedback_service import feedback_service
    return feedback_service.process_feedback(feedback_id)


@shared_task
def process_pending_feedback():
    """
    Process all pending feedback.

    Run every 5 minutes.
    """
    pending = HumanFeedback.objects.filter(status='pending')
    for feedback in pending:
        process_feedback.delay(str(feedback.id))
```

---

## API Endpoints

```python
# In core/urls.py

# Submit feedback
path('api/feedback/', views_feedback.submit_feedback, name='submit-feedback'),

# Get feedback for a target
path('api/feedback/<str:target_type>/<uuid:target_id>/', views_feedback.get_feedback, name='get-feedback'),

# Get agent's received feedback
path('api/agents/<uuid:agent_id>/feedback/', views_feedback.agent_feedback, name='agent-feedback'),

# Get agent's learnings from feedback
path('api/agents/<uuid:agent_id>/learnings/', views_feedback.agent_learnings, name='agent-learnings'),
```

---

## UI Integration

### Feedback Buttons

Add to conversation view, artifact cards, dream cards:

```html
<!-- Feedback actions -->
<div class="feedback-actions">
    <button onclick="openFeedback('{id}', 'rating')" title="Rate this">
        ⭐
    </button>
    <button onclick="openFeedback('{id}', 'elaboration_request')" title="Tell me more">
        💬
    </button>
    <button onclick="openFeedback('{id}', 'correction')" title="This is wrong">
        ✏️
    </button>
    <button onclick="openFeedback('{id}', 'domain_knowledge')" title="Add expertise">
        🧠
    </button>
</div>
```

### Feedback Modal

```html
<div class="modal" id="feedback-modal">
    <div class="modal-content">
        <h4>Provide Feedback</h4>

        <!-- Rating -->
        <div class="feedback-section" id="rating-section">
            <label>Quality Rating</label>
            <div class="star-rating">
                <span onclick="setRating(1)">⭐</span>
                <span onclick="setRating(2)">⭐</span>
                <span onclick="setRating(3)">⭐</span>
                <span onclick="setRating(4)">⭐</span>
                <span onclick="setRating(5)">⭐</span>
            </div>
        </div>

        <!-- Content -->
        <div class="feedback-section">
            <label>Your Feedback</label>
            <textarea id="feedback-content" placeholder="Share your thoughts, corrections, or expertise..."></textarea>
        </div>

        <!-- Feedback Type Specific Fields -->
        <div class="feedback-section" id="outcome-section" style="display:none;">
            <label>Outcome</label>
            <select id="outcome-result">
                <option value="success">Success</option>
                <option value="partial">Partial Success</option>
                <option value="failure">Failure</option>
            </select>
            <label>Key Metrics (optional)</label>
            <textarea id="outcome-metrics" placeholder='{"revenue": 1000, "conversion": 0.05}'></textarea>
        </div>

        <button onclick="submitFeedback()">Submit Feedback</button>
    </div>
</div>
```

### Agent Learning History

Show what an agent has learned from feedback:

```html
<div class="agent-learnings">
    <h5>📚 Learned from Your Feedback</h5>
    <ul>
        <li>
            <span class="learning-type">Correction</span>
            <span class="learning-desc">Updated pricing analysis methodology</span>
            <span class="learning-date">2 days ago</span>
        </li>
        <li>
            <span class="learning-type">Domain Knowledge</span>
            <span class="learning-desc">SaaS pricing typically uses 3-tier model</span>
            <span class="learning-date">1 week ago</span>
        </li>
    </ul>
</div>
```

---

## Feedback → Agent Behavior

How feedback actually changes agent behavior:

### 1. Corrections → Updated Knowledge
- Incorrect knowledge is deactivated
- Corrected knowledge is added with high confidence
- Agent references corrected knowledge in future

### 2. Domain Knowledge → New Knowledge Entries
- Human expertise becomes agent knowledge
- Marked as high-confidence, human-sourced
- Referenced in relevant future conversations

### 3. Outcome Reports → Learning Records
- Success/failure recorded against executions
- Patterns identified (what works, what doesn't)
- Influences future proposal scoring

### 4. Direction → Focus Adjustment
- Could update agent prompts/system messages
- Could adjust knowledge search priorities
- Could influence which topics trigger dreams

### 5. Elaboration → New Content
- Triggers directed dreams about topic
- Could start new conversation thread
- Generates more detailed knowledge

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `core/models_feedback.py` | CREATE | HumanFeedback, AgentLearningFromFeedback |
| `core/services/feedback_service.py` | CREATE | FeedbackService |
| `core/views_feedback.py` | CREATE | API endpoints |
| `core/urls.py` | MODIFY | Add feedback routes |
| `core/tasks.py` | MODIFY | Add processing tasks |
| `ai_core/templates/...` | MODIFY | Add feedback UI |
| `core/migrations/XXXX_feedback.py` | CREATE | Database migration |

---

## Success Criteria

1. Users can provide all feedback types from UI
2. Feedback is processed within 5 minutes
3. Corrections update agent knowledge
4. Outcome reports are linked to executions
5. Agent learning history is visible
6. Agents reference human feedback in future outputs

---

## The Complete Loop

With all four phases:

```
Conversations → Artifacts (A) → Approved → Execution (B) → Outcome
      ↓                                                       ↓
   Briefs (C) ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
      ↓
   Human Reviews
      ↓
   Feedback (D) → Agent Learning → Better Future Outputs
```

---

**This phase closes the loop, making the system learn from human input.**

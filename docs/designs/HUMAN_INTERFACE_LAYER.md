# HumanInterfaceLayer - Design Document

**Session:** 686
**Status:** Design Phase
**Purpose:** Connect the Human operator to the autonomous AI ecosystem

---

## Architectural Context

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HUMAN OPERATOR                               │
│   (Reviews, Approves, Overrides, Learns, Controls)                  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    HUMAN INTERFACE LAYER                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │  Attention  │ │  Feedback   │ │  Control    │ │ Preference  │   │
│  │ Aggregator  │ │  Capture    │ │   Panel     │ │  Learner    │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                   │
│  │  Priority   │ │  ML Feedback│ │Notification │                   │
│  │   Scorer    │ │    Loop     │ │   Router    │                   │
│  └─────────────┘ └─────────────┘ └─────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          BRAIN LAYER                                 │
│                       (ThinkingAgent)                                │
│              Autonomous reasoning & decision-making                  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     NERVOUS SYSTEM LAYER                             │
│                    (Agent-Model Router)                              │
│           ML auto-selection, signal routing, optimization            │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ORGAN LAYER                                  │
│                    (72+ Specialized Agents)                          │
│   Research │ Content │ Code │ Stocks │ Blockchain │ Creative │ ...  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. HumanAttentionAggregator

**Purpose:** Collect attention-worthy items from ALL system sources into one stream.

**Sources to Aggregate:**
| Source | Item Type | Example |
|--------|-----------|---------|
| SystemIntelligenceAgent | Health alerts | "5 critical issues detected" |
| ThinkingAgent | Decisions pending | "Should deploy new spider?" |
| PilotReadinessGate | Gate approvals | "Gate requires sign-off" |
| Agent executions | Failures/anomalies | "ResearchAgent failed 3x" |
| ML predictions | Low confidence | "ML confidence < 50%" |
| Spiders | High-value data | "Breaking news detected" |
| Dreams/Boardroom | Promoted items | "Dream promoted to decision" |
| Chief of Staff | Reviews pending | "Document awaiting review" |
| Discord mentions | User requests | "@bot analyze this" |

**Output:** Normalized `HumanAttentionItem` objects

---

### 2. HumanPriorityScorer

**Purpose:** Rank attention items by importance, urgency, and human preferences.

**Scoring Formula:**
```python
priority_score = (
    base_urgency * urgency_weight +
    impact_score * impact_weight +
    human_preference_boost +
    recency_decay +
    source_trust_score
)
```

**Factors:**
- **Urgency:** CRITICAL (10), HIGH (7), MEDIUM (4), LOW (1)
- **Impact:** Revenue impact, user impact, system health impact
- **Human Preference:** Learned from past engagement patterns
- **Recency:** Newer items score higher (decay over time)
- **Source Trust:** Some sources consistently produce actionable items

**Learning:** Adjusts weights based on what human actually acts on.

---

### 3. HumanFeedbackCapture

**Purpose:** Record every human decision for learning and audit.

**Decision Types:**
| Decision | Meaning | ML Signal |
|----------|---------|-----------|
| `approve` | Human agrees, proceed | Positive reinforcement |
| `reject` | Human disagrees, stop | Negative signal |
| `modify` | Human adjusts, then proceed | Partial correction |
| `defer` | Not now, remind later | Neutral |
| `delegate` | Route to another agent | Routing feedback |
| `ignore` | Not worth attention | Priority adjustment |
| `escalate` | Needs higher authority | Urgency feedback |

**Captured Context:**
- Decision timestamp
- Time spent reviewing (engagement metric)
- Free-text feedback (optional)
- Original ML prediction (for comparison)
- Human's confidence level (optional)

---

### 4. HumanToMLFeedbackLoop

**Purpose:** Feed human decisions back to improve ML predictions.

**Feedback Mechanisms:**

1. **Prediction Correction**
   - When human overrides ML, record the delta
   - Update MODEL_TASK_SCORES over time
   - Track which models human corrects most

2. **Confidence Calibration**
   - If ML says 90% confidence but human rejects, ML was overconfident
   - Adjust confidence thresholds per model
   - Learn when to flag for human review

3. **Task Type Learning**
   - Human corrections inform task classification
   - "This looked like TEXT but was actually ANOMALY"
   - Improve TaskAnalyzer heuristics

4. **Agent Routing Feedback**
   - Human routes to different agent than system chose
   - Learn better routing patterns
   - Update AGENT_ROUTING_CONFIG

---

### 5. HumanPreferenceLearner

**Purpose:** Learn individual human preferences over time.

**Tracked Preferences:**
| Preference | Example | How Learned |
|------------|---------|-------------|
| Topics of interest | "Stocks", "AI news" | Engagement patterns |
| Notification timing | "Not before 9am" | Explicit setting + behavior |
| Decision style | "Quick approver" vs "Deep reviewer" | Time-on-task analysis |
| Risk tolerance | "Conservative" vs "Aggressive" | Override patterns |
| Communication preference | Discord vs Web vs Email | Click-through rates |
| Delegation patterns | "Trust ResearchAgent" | Approval rates by source |

**Preference Model:**
```python
class HumanPreferenceProfile:
    user: User
    topic_weights: Dict[str, float]  # What they care about
    quiet_hours: List[TimeRange]     # When not to disturb
    urgency_threshold: float         # Min urgency to notify
    review_depth: str                # quick|standard|thorough
    risk_tolerance: str              # conservative|moderate|aggressive
    trusted_agents: List[str]        # Auto-approve from these
    trusted_sources: List[str]       # Higher priority from these
```

---

### 6. HumanControlPanel

**Purpose:** Give human direct control over the autonomous system.

**Control Capabilities:**

| Control | Scope | Effect |
|---------|-------|--------|
| **Pause Agent** | Single agent | Stop execution, queue tasks |
| **Pause All** | System-wide | Emergency stop |
| **Resume** | Agent/System | Continue from queue |
| **Override Decision** | Specific item | Force approve/reject |
| **Adjust Threshold** | ML model | Change confidence cutoff |
| **Block Source** | Spider/Agent | Stop feeding into attention |
| **Priority Boost** | Topic/Source | Increase priority weight |
| **Quiet Mode** | Notifications | Suppress non-critical |
| **Review Mode** | All decisions | Require human approval for all |

**Safety Features:**
- Audit log of all control actions
- Confirmation for destructive actions
- Auto-resume after timeout (prevent forgotten pauses)
- Escalation if critical items pile up during pause

---

### 7. HumanNotificationRouter

**Purpose:** Deliver attention items to human via the right channel at the right time.

**Channels:**
| Channel | Best For | Latency |
|---------|----------|---------|
| Discord DM | Urgent, interactive | Real-time |
| Discord Channel | Team visibility | Real-time |
| Web Push | Quick acknowledgment | Near real-time |
| Web Dashboard | Batch review | On-demand |
| Email Digest | Low urgency summary | Daily/Weekly |

**Routing Logic:**
```python
def route_notification(item: HumanAttentionItem, prefs: HumanPreferenceProfile):
    if item.urgency == 'CRITICAL':
        return [Channel.DISCORD_DM, Channel.WEB_PUSH]  # Multi-channel

    if is_quiet_hours(prefs):
        if item.urgency == 'HIGH':
            return [Channel.WEB_DASHBOARD]  # Queue for later
        else:
            return []  # Skip entirely

    if item.urgency == 'HIGH':
        return [Channel.DISCORD_CHANNEL]

    return [Channel.WEB_DASHBOARD]  # Default: batch review
```

---

## Data Models

### HumanAttentionItem
```python
class HumanAttentionItem(models.Model):
    """An item requiring human attention."""

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Source
    source_type = models.CharField(max_length=50)  # 'thinking_agent', 'pilot_gate', etc.
    source_id = models.CharField(max_length=100)   # ID in source system
    source_agent = models.CharField(max_length=100, null=True)

    # Content
    item_type = models.CharField(max_length=50)    # 'decision', 'alert', 'opportunity'
    title = models.CharField(max_length=200)
    summary = models.TextField()
    payload = models.JSONField()                   # Full data from source

    # Priority
    urgency = models.CharField(max_length=20)      # critical, high, medium, low
    priority_score = models.FloatField(default=0)
    impact_estimate = models.CharField(max_length=20, null=True)

    # ML Context
    ml_prediction = models.JSONField(null=True)    # What ML said
    ml_confidence = models.FloatField(null=True)
    ml_recommendation = models.CharField(max_length=100, null=True)

    # Status
    status = models.CharField(max_length=20, default='pending')
    # pending, viewed, acted, deferred, ignored, expired

    # Human Decision
    decision = models.CharField(max_length=20, null=True)
    # approve, reject, modify, defer, delegate, ignore, escalate
    decision_feedback = models.TextField(null=True)
    decision_confidence = models.FloatField(null=True)
    decided_at = models.DateTimeField(null=True)
    time_to_decision_ms = models.IntegerField(null=True)

    # Human Override
    human_overrode_ml = models.BooleanField(default=False)
    override_reason = models.TextField(null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'urgency']),
            models.Index(fields=['source_type']),
        ]
```

### HumanFeedbackRecord
```python
class HumanFeedbackRecord(models.Model):
    """Record of human feedback for ML learning."""

    attention_item = models.ForeignKey(HumanAttentionItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The Decision
    decision = models.CharField(max_length=20)
    feedback_text = models.TextField(null=True)
    confidence = models.FloatField(null=True)

    # ML Context at Decision Time
    ml_task_type = models.CharField(max_length=50, null=True)
    ml_models_used = models.JSONField(null=True)
    ml_prediction = models.JSONField(null=True)
    ml_confidence = models.FloatField(null=True)

    # Override Analysis
    human_agreed_with_ml = models.BooleanField(null=True)
    confidence_delta = models.FloatField(null=True)  # Human conf - ML conf

    # Learning Status
    fed_to_ml = models.BooleanField(default=False)
    fed_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
```

### HumanPreference
```python
class HumanPreference(models.Model):
    """Human preference settings."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Notification Preferences
    quiet_hours_start = models.TimeField(null=True)
    quiet_hours_end = models.TimeField(null=True)
    min_urgency_to_notify = models.CharField(max_length=20, default='medium')
    preferred_channel = models.CharField(max_length=50, default='discord')

    # Review Preferences
    review_depth = models.CharField(max_length=20, default='standard')
    # quick (< 30s), standard (30s-2min), thorough (> 2min)
    auto_approve_low_risk = models.BooleanField(default=False)
    require_review_above_confidence = models.FloatField(default=0.95)

    # Trust Settings
    trusted_agents = models.JSONField(default=list)      # Auto-approve from these
    blocked_sources = models.JSONField(default=list)     # Never show from these

    # Learned Preferences (auto-updated)
    topic_weights = models.JSONField(default=dict)       # {topic: weight}
    source_weights = models.JSONField(default=dict)      # {source: weight}
    avg_decision_time_ms = models.IntegerField(null=True)
    approval_rate = models.FloatField(null=True)

    updated_at = models.DateTimeField(auto_now=True)
```

### HumanControlAction
```python
class HumanControlAction(models.Model):
    """Audit log of human control actions."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    action_type = models.CharField(max_length=50)
    # pause_agent, resume_agent, override_decision, adjust_threshold,
    # block_source, priority_boost, quiet_mode, review_mode

    target_type = models.CharField(max_length=50)  # agent, source, model, system
    target_id = models.CharField(max_length=100)

    old_value = models.JSONField(null=True)
    new_value = models.JSONField(null=True)

    reason = models.TextField(null=True)
    auto_revert_at = models.DateTimeField(null=True)  # For temporary actions
    reverted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Services

### HumanInterfaceService (Main Orchestrator)
```python
class HumanInterfaceService:
    """Main service coordinating all Human Interface Layer components."""

    def __init__(self, user: User):
        self.user = user
        self.aggregator = HumanAttentionAggregator(user)
        self.scorer = HumanPriorityScorer(user)
        self.feedback = HumanFeedbackCapture(user)
        self.ml_loop = HumanToMLFeedbackLoop(user)
        self.preferences = HumanPreferenceLearner(user)
        self.control = HumanControlPanel(user)
        self.notifier = HumanNotificationRouter(user)

    def get_attention_stream(self, limit=20, urgency_filter=None):
        """Get prioritized attention items for this human."""
        items = self.aggregator.collect_all()
        scored = self.scorer.score_and_rank(items)
        filtered = self._apply_preferences(scored)
        return filtered[:limit]

    def record_decision(self, item_id, decision, feedback=None):
        """Record human decision and trigger learning."""
        item = HumanAttentionItem.objects.get(id=item_id)

        # Capture feedback
        self.feedback.record(item, decision, feedback)

        # Update item status
        item.decision = decision
        item.decided_at = timezone.now()
        item.save()

        # Trigger ML feedback loop
        if item.ml_prediction:
            self.ml_loop.process_feedback(item)

        # Update preferences
        self.preferences.learn_from_decision(item)

        return item

    def execute_control_action(self, action_type, target, value, reason=None):
        """Execute a control action with audit logging."""
        return self.control.execute(action_type, target, value, reason)
```

---

## API Endpoints

### Attention Stream
```
GET  /api/human/attention/
     ?urgency=critical,high
     &status=pending
     &limit=20

POST /api/human/attention/{id}/decide/
     {"decision": "approve", "feedback": "Looks good", "confidence": 0.9}

POST /api/human/attention/{id}/defer/
     {"remind_at": "2026-01-06T09:00:00Z"}

GET  /api/human/attention/stats/
     Returns: pending_count, by_urgency, avg_decision_time
```

### Control Panel
```
GET  /api/human/control/
     Returns: agent_states, ml_thresholds, active_overrides

POST /api/human/control/pause/
     {"target": "ResearchAgent", "duration_minutes": 30}

POST /api/human/control/override/
     {"item_id": "...", "override_value": "approve", "reason": "..."}

POST /api/human/control/threshold/
     {"model": "lstm", "new_threshold": 0.7}

GET  /api/human/control/audit/
     Returns: recent control actions
```

### Preferences
```
GET  /api/human/preferences/

PUT  /api/human/preferences/
     {"quiet_hours_start": "22:00", "min_urgency_to_notify": "high"}

GET  /api/human/preferences/learned/
     Returns: auto-learned preferences, topic weights, patterns
```

### Insights
```
GET  /api/human/insights/
     Returns: decision patterns, ML agreement rate, top sources

GET  /api/human/insights/ml-accuracy/
     Returns: how often ML matched human decisions
```

---

## Discord Commands

### /human-attention
```
Shows top attention items with action buttons.

Usage: /human-attention [urgency] [limit]

Example response:
┌─────────────────────────────────────────┐
│ 🔴 CRITICAL: Gate approval needed       │
│    Pilot "AI Humanizer" ready to deploy │
│    ML Recommendation: APPROVE (87%)     │
│    [Approve] [Reject] [Details] [Defer] │
├─────────────────────────────────────────┤
│ 🟡 HIGH: ThinkingAgent decision         │
│    "Deploy spiders for trending topic?" │
│    ML Recommendation: APPROVE (72%)     │
│    [Approve] [Reject] [Details] [Defer] │
└─────────────────────────────────────────┘
```

### /human-decide
```
Make a decision on an attention item.

Usage: /human-decide <item_id> <decision> [feedback]
```

### /human-control
```
Control panel for the autonomous system.

Usage: /human-control <action> [target] [value]

Actions:
  pause <agent>     - Pause an agent
  resume <agent>    - Resume an agent
  status            - Show system status
  quiet [minutes]   - Enable quiet mode
  review            - Enable review mode (approve all)
```

### /human-preferences
```
View and set preferences.

Usage: /human-preferences [set <key> <value>]

Keys: quiet_hours, min_urgency, channel, auto_approve
```

### /human-insights
```
View insights about your decision patterns.

Shows: approval rate, avg decision time, ML agreement, top topics
```

---

## Web UI Components

### Human Dashboard (New Tab)
```
┌─────────────────────────────────────────────────────────────────────┐
│ HUMAN COMMAND CENTER                                    [Quiet Mode]│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ATTENTION STREAM                          QUICK STATS              │
│  ┌─────────────────────────────────────┐  ┌───────────────────────┐│
│  │ 🔴 Gate: AI Humanizer deploy        │  │ Pending: 12           ││
│  │    [Approve] [Reject] [Defer]       │  │ Critical: 2           ││
│  ├─────────────────────────────────────┤  │ Avg Decision: 45s     ││
│  │ 🟡 Decision: Deploy trending spider │  │ ML Agreement: 89%     ││
│  │    [Approve] [Reject] [Defer]       │  │                       ││
│  ├─────────────────────────────────────┤  │ TODAY                 ││
│  │ 🟢 Alert: New opportunity found     │  │ Approved: 15          ││
│  │    [Acknowledge] [Investigate]      │  │ Rejected: 3           ││
│  └─────────────────────────────────────┘  │ Deferred: 5           ││
│                                           └───────────────────────┘│
│  CONTROL PANEL                             PREFERENCES             │
│  ┌─────────────────────────────────────┐  ┌───────────────────────┐│
│  │ System: [Running] [Pause All]       │  │ Notify: Discord       ││
│  │ Review Mode: [Off] [On]             │  │ Min Urgency: Medium   ││
│  │ Agents: 72 running, 0 paused        │  │ Quiet Hours: 10pm-8am ││
│  │ ML Threshold: 0.6                   │  │ Auto-approve: Off     ││
│  └─────────────────────────────────────┘  └───────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

| Phase | Component | Effort | Priority |
|-------|-----------|--------|----------|
| 1 | Data models (migration) | Low | Required |
| 2 | HumanAttentionAggregator | Medium | Core |
| 3 | HumanFeedbackCapture | Low | Core |
| 4 | Basic API endpoints | Medium | Core |
| 5 | Discord commands | Medium | High |
| 6 | HumanPriorityScorer | Medium | Enhancement |
| 7 | HumanToMLFeedbackLoop | High | Enhancement |
| 8 | HumanPreferenceLearner | Medium | Enhancement |
| 9 | Web UI components | High | Enhancement |
| 10 | HumanControlPanel | Medium | Enhancement |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to human decision | < 60s avg | Track `time_to_decision_ms` |
| Items requiring attention | < 20/day | Count pending items |
| ML-Human agreement | > 85% | Track overrides |
| False urgency rate | < 10% | Track ignored CRITICAL items |
| Preference learning accuracy | > 80% | Predict human decision |

---

## Security Considerations

1. **Audit Trail:** Every human action is logged
2. **Confirmation:** Destructive actions require confirmation
3. **Auto-Revert:** Pauses auto-expire after timeout
4. **Escalation:** Critical items escalate if ignored too long
5. **Rate Limiting:** Prevent control action spam
6. **Role-Based:** Admin vs User permissions for control actions

---

## Integration Points

| System | Integration |
|--------|-------------|
| ThinkingAgent | Subscribe to decisions, feed human overrides |
| Agent-Model Router | Receive feedback, adjust scores |
| SystemIntelligenceAgent | Pull attention items |
| PilotReadinessGate | Pull gate approvals |
| Chief of Staff | Pull review requests |
| Discord Bot | Add commands, send notifications |
| Web UI | Add Human Dashboard tab |
| Celery | Background aggregation, notification scheduling |

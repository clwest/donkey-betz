# Session 25 Handoff - Agent Learning Integration (Phase 3)

**From**: Session 24 (Model Retraining Pipeline)
**To**: Future Session (Agent Learning Integration)
**Date**: September 30, 2025 @ 3:15 AM MST
**Branch**: `feature/reality-fixes-implementation`
**Priority**: MEDIUM - Complete the agent feedback loop

---

## 🎯 Current State

### ✅ What's Working (Sessions 23 & 24 Complete)

**Session 23 - Prediction Evaluation**:
- ✅ Predictions evaluated when games complete
- ✅ `MLPrediction.was_correct` populated
- ✅ Accuracy metrics calculated per sport/model
- ✅ Celery task runs hourly

**Session 24 - Model Retraining**:
- ✅ Models retrain automatically with evaluated predictions
- ✅ New models validated before deployment
- ✅ Version tracking with performance history
- ✅ Only deploy if model improves
- ✅ Daily checks + weekly fallback

**Foundation Established**:
- ✅ Predictions → Evaluation → Retraining pipeline works
- ✅ Models learn from outcomes
- ✅ Performance improves over time
- ✅ Agents use updated models automatically (via MLEngine)

---

## 🚀 Next Mission: Phase 3 - Agent Learning Integration

### Goal
Enable agents to learn from their own prediction performance and adapt their strategies accordingly.

### Why This Matters
Currently:
- Models improve, but agents don't know their personal performance
- Agents can't adjust confidence based on track record
- No personalization per agent (all agents share same model)
- No feedback loop for agent-specific strategies

After Phase 3:
- Each agent tracks their own prediction performance
- Agents learn which sports/situations they excel at
- Agents adjust confidence based on personal track record
- Agents can specialize in areas where they perform best
- **True agent-level learning!**

---

## 📋 Implementation Plan

### Step 1: Agent Performance Tracking

**File**: `intelligence/models.py` (UPDATE)

Add performance tracking to Agent model:

```python
class AgentPerformanceMetrics(models.Model):
    """Track individual agent prediction performance"""

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)

    # Overall metrics
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0.0)  # Calculated field

    # Sport-specific metrics
    sport_type = models.CharField(max_length=10)  # 'nfl', 'nba', etc.
    sport_predictions = models.IntegerField(default=0)
    sport_correct = models.IntegerField(default=0)
    sport_accuracy = models.FloatField(default=0.0)

    # Confidence calibration
    avg_confidence_when_correct = models.FloatField(default=0.0)
    avg_confidence_when_wrong = models.FloatField(default=0.0)
    confidence_calibration_score = models.FloatField(default=0.0)

    # Learning metrics
    last_10_predictions_accuracy = models.FloatField(default=0.0)
    last_30_predictions_accuracy = models.FloatField(default=0.0)
    trend = models.CharField(
        max_length=20,
        choices=[
            ('improving', 'Improving'),
            ('stable', 'Stable'),
            ('declining', 'Declining')
        ],
        default='stable'
    )

    # Specializations
    best_sport = models.CharField(max_length=10, null=True)
    worst_sport = models.CharField(max_length=10, null=True)
    confidence_level = models.CharField(
        max_length=20,
        choices=[
            ('overconfident', 'Overconfident'),
            ('well_calibrated', 'Well Calibrated'),
            ('underconfident', 'Underconfident')
        ],
        default='well_calibrated'
    )

    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['agent', 'sport_type']
        indexes = [
            models.Index(fields=['agent', 'sport_type']),
            models.Index(fields=['accuracy']),
        ]

    def update_from_prediction(self, prediction: MLPrediction):
        """Update metrics based on new prediction result"""
        self.total_predictions += 1
        if prediction.sport_type == self.sport_type:
            self.sport_predictions += 1

        if prediction.was_correct:
            self.correct_predictions += 1
            if prediction.sport_type == self.sport_type:
                self.sport_correct += 1

        # Recalculate accuracy
        self.accuracy = self.correct_predictions / self.total_predictions
        if self.sport_predictions > 0:
            self.sport_accuracy = self.sport_correct / self.sport_predictions

        self.save()
```

---

### Step 2: Performance Update Task

**File**: `intelligence/tasks.py` (NEW)

```python
from celery import shared_task
from sports.models import MLPrediction
from intelligence.models import Agent, AgentPerformanceMetrics

@shared_task(name='intelligence.update_agent_performance')
def update_agent_performance():
    """
    Update agent performance metrics from evaluated predictions
    Runs daily after prediction evaluation
    """
    # Get recently evaluated predictions (last 24 hours)
    cutoff = timezone.now() - timedelta(hours=24)
    new_evaluations = MLPrediction.objects.filter(
        was_correct__isnull=False,
        evaluation_time__gte=cutoff
    )

    agents_updated = 0

    for prediction in new_evaluations:
        # Get agent who made this prediction
        agent = prediction.agent  # Assuming FK to Agent

        # Get or create performance metrics
        metrics, _ = AgentPerformanceMetrics.objects.get_or_create(
            agent=agent,
            sport_type=prediction.sport_type
        )

        # Update metrics
        metrics.update_from_prediction(prediction)
        agents_updated += 1

    return {
        'predictions_processed': new_evaluations.count(),
        'agents_updated': agents_updated
    }
```

---

### Step 3: Agent Self-Awareness

**File**: `intelligence/agent_learning.py` (NEW)

```python
class AgentLearningSystem:
    """
    Enables agents to learn from their performance and adapt
    """

    def __init__(self, agent: Agent):
        self.agent = agent
        self.metrics = AgentPerformanceMetrics.objects.filter(agent=agent)

    def get_confidence_adjustment(self, sport_type: str) -> float:
        """
        Adjust confidence based on agent's track record in this sport

        Returns:
            float: Multiplier for confidence (0.8 to 1.2)
        """
        try:
            metrics = self.metrics.get(sport_type=sport_type)

            # If accuracy > 60%, boost confidence
            if metrics.sport_accuracy > 0.60:
                return 1.1

            # If accuracy < 50%, reduce confidence
            if metrics.sport_accuracy < 0.50:
                return 0.9

            return 1.0

        except AgentPerformanceMetrics.DoesNotExist:
            # New to this sport - neutral confidence
            return 1.0

    def should_make_prediction(self, sport_type: str) -> bool:
        """
        Decide if agent should make prediction based on competence

        Returns:
            bool: True if agent should predict
        """
        try:
            metrics = self.metrics.get(sport_type=sport_type)

            # Don't predict if performing very poorly
            if metrics.sport_predictions > 20 and metrics.sport_accuracy < 0.40:
                return False

            return True

        except AgentPerformanceMetrics.DoesNotExist:
            # New agent - let them try
            return True

    def get_specializations(self) -> dict:
        """
        Identify which sports/areas agent excels at

        Returns:
            dict: Specialization summary
        """
        all_metrics = self.metrics.all()

        if not all_metrics:
            return {'status': 'new_agent', 'specializations': []}

        best_sport = max(all_metrics, key=lambda m: m.sport_accuracy)
        worst_sport = min(all_metrics, key=lambda m: m.sport_accuracy)

        specializations = [
            m.sport_type for m in all_metrics
            if m.sport_accuracy > 0.60 and m.sport_predictions > 10
        ]

        return {
            'best_sport': best_sport.sport_type,
            'best_accuracy': best_sport.sport_accuracy,
            'worst_sport': worst_sport.sport_type,
            'worst_accuracy': worst_sport.sport_accuracy,
            'specializations': specializations,
            'total_predictions': sum(m.sport_predictions for m in all_metrics)
        }
```

---

### Step 4: Integrate with Prediction Flow

**File**: `ml/core/ml_engine.py` (UPDATE)

Update prediction method to use agent learning:

```python
def predict_game_with_agent(self, game_id: str, sport_type: str, agent: Agent):
    """
    Generate prediction using agent learning system

    Args:
        game_id: Game identifier
        sport_type: Sport type
        agent: Agent making prediction

    Returns:
        Prediction with adjusted confidence
    """
    # Get agent learning system
    learning_system = AgentLearningSystem(agent)

    # Check if agent should make this prediction
    if not learning_system.should_make_prediction(sport_type):
        return None  # Agent declines to predict

    # Get base prediction from model
    base_prediction = self.predict_game(game_id, sport_type)

    # Adjust confidence based on agent's track record
    confidence_adjustment = learning_system.get_confidence_adjustment(sport_type)
    adjusted_confidence = base_prediction['confidence'] * confidence_adjustment

    # Clamp to valid range
    adjusted_confidence = max(0.5, min(1.0, adjusted_confidence))

    return {
        **base_prediction,
        'confidence': adjusted_confidence,
        'agent_adjustment': confidence_adjustment,
        'agent_track_record': learning_system.get_specializations()
    }
```

---

### Step 5: Agent Dashboard

**File**: `intelligence/views.py` (UPDATE)

Add agent performance dashboard:

```python
@login_required
def agent_performance_dashboard(request, agent_id):
    """
    Show agent's prediction performance and learning progress
    """
    agent = get_object_or_404(Agent, id=agent_id)
    learning_system = AgentLearningSystem(agent)

    metrics = AgentPerformanceMetrics.objects.filter(agent=agent)
    specializations = learning_system.get_specializations()

    context = {
        'agent': agent,
        'metrics': metrics,
        'specializations': specializations,
        'overall_accuracy': sum(m.accuracy for m in metrics) / len(metrics) if metrics else 0,
        'total_predictions': sum(m.total_predictions for m in metrics)
    }

    return render(request, 'intelligence/agent_dashboard.html', context)
```

---

## 🎯 Success Criteria for Phase 3

1. ✅ Agents track their own prediction performance
2. ✅ Agents adjust confidence based on track record
3. ✅ Agents can decline predictions in weak areas
4. ✅ Agents identify their specializations
5. ✅ Performance metrics updated automatically
6. ✅ Agent dashboard shows learning progress
7. ✅ Integration with existing prediction flow

---

## 📊 How To Test

### Test 1: Agent Performance Tracking
```bash
python manage.py shell -c "
from intelligence.models import Agent, AgentPerformanceMetrics
from intelligence.agent_learning import AgentLearningSystem

agent = Agent.objects.first()
learning = AgentLearningSystem(agent)
print(learning.get_specializations())
"
```

### Test 2: Confidence Adjustment
```bash
python manage.py shell -c "
from intelligence.models import Agent
from intelligence.agent_learning import AgentLearningSystem

agent = Agent.objects.first()
learning = AgentLearningSystem(agent)

for sport in ['nfl', 'nba', 'mlb', 'nhl']:
    adjustment = learning.get_confidence_adjustment(sport)
    print(f'{sport.upper()}: {adjustment:.2f}x confidence')
"
```

### Test 3: Update Agent Performance
```bash
python manage.py shell -c "
from intelligence.tasks import update_agent_performance
result = update_agent_performance()
print(f'Updated {result[\"agents_updated\"]} agents from {result[\"predictions_processed\"]} predictions')
"
```

---

## 🔄 Complete Learning Loop After Phase 3

```
┌─────────────────────────────────────────────────────────────┐
│              COMPLETE AGENT LEARNING CYCLE                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. PREDICTION (Session 22 - Working)                       │
│     Agent makes prediction using ML model                    │
│                                                               │
│  2. EVALUATION (Session 23 - Complete!)                     │
│     Game completes → Prediction evaluated                    │
│                    → was_correct populated                   │
│                                                               │
│  3. MODEL LEARNING (Session 24 - Complete!)                 │
│     Collect evaluations → Train new model                    │
│                        → Deploy if better                    │
│                                                               │
│  4. AGENT LEARNING (Session 25 - Next!)                     │
│     Track agent performance → Adjust confidence              │
│                            → Identify specializations        │
│                            → Agent gets smarter!             │
│                                                               │
│  5. IMPROVEMENT (Automatic)                                  │
│     Better models + Smarter agents = Higher accuracy! 🚀     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Files to Create/Modify - Session 25

### New Files (2):
1. `intelligence/agent_learning.py` - Agent learning system
2. `intelligence/tasks.py` - Agent performance update tasks

### Files to Update (3):
1. `intelligence/models.py` - Add AgentPerformanceMetrics model
2. `ml/core/ml_engine.py` - Integrate agent learning
3. `intelligence/views.py` - Add agent dashboard

### Migrations:
- `intelligence/migrations/000X_agent_performance.py` - Add performance tracking

**Estimated Implementation Time**: 2-3 hours

---

## 🎓 Key Concepts

### Agent Self-Awareness
- Agents track their own performance
- Learn which sports they excel at
- Adjust confidence based on track record
- Can decline predictions in weak areas

### Confidence Calibration
- Overconfident agents get adjusted down
- Underconfident agents get adjusted up
- Well-calibrated agents stay neutral
- Based on historical accuracy

### Specialization Discovery
- Agents identify their strengths
- System can route predictions to best agents
- Enables ensemble approaches
- Creates agent diversity

### Continuous Improvement
- Daily performance updates
- Trend detection (improving/stable/declining)
- Feedback loop closes at agent level
- True AI learning system!

---

## 💡 Implementation Tips

### 1. Start Simple
Implement basic performance tracking first, then add confidence adjustment.

### 2. Test with Real Data
Use actual evaluated predictions to verify metrics calculation.

### 3. Agent Selection
Consider routing predictions to agents with best track record for that sport.

### 4. Visualization
Build dashboards to show agent learning progress over time.

### 5. Ensemble Predictions
Combine predictions from multiple specialized agents for better accuracy.

---

## 🚨 Important Notes

### Migration Required
```bash
python manage.py makemigrations intelligence
python manage.py migrate
```

### Celery Beat Update
Add to `core/celery.py`:
```python
'update-agent-performance': {
    'task': 'intelligence.update_agent_performance',
    'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
    'options': {'expires': 3600}
},
```

### Link Predictions to Agents
Need to add `agent` ForeignKey to `MLPrediction` model if not already present.

---

## 🎯 Session 25 Goals

**Primary Goal**: Enable agent-level learning and adaptation

**Deliverables**:
1. Agent performance tracking system
2. Confidence adjustment based on track record
3. Specialization discovery
4. Agent learning dashboard
5. Integration with prediction flow

**Success**: An agent adjusts their confidence based on personal performance and specializes in sports where they excel.

---

## 📞 Quick Reference

### Session 24 Commands:
```bash
# Model retraining
python manage.py retrain_models --sport nfl
python manage.py retrain_models --all
python manage.py retrain_models --status
python manage.py retrain_models --versions
```

### Session 25 Commands (to build):
```bash
# Agent performance
python manage.py update_agent_performance
python manage.py show_agent_stats --agent <id>
python manage.py find_specialists --sport nfl
```

---

## 🎉 The Vision - After Phase 3

You'll have:
- ✅ Models that learn from outcomes (Phase 2)
- ✅ Agents that learn from their performance (Phase 3)
- ✅ Specialized agents for different sports
- ✅ Confidence calibration at agent level
- ✅ A true self-improving multi-agent system

**This completes the individual learning loop!** 🧠✨

**Next**: Phase 4 - System Monitoring & Optimization

---

**End of Session 25 Handoff**
*Generated: September 30, 2025 @ 3:15 AM MST*
*Ready for implementation*

**Current Status**: Phase 2 Complete, Phase 3 Documented
**Next**: Implement Agent Learning Integration! 🚀
# Session 464: Learning Loop Phase 2 - Automation & Feedback

**Previous Session:** 463 - Learning Loop Phase 1 (Foundation Complete ✅)
**Status:** Ready to build automation layer
**Branch:** `feature/session-52-ai-assistant`
**Last Commit:** `fdc5581` - Learning Loop Phase 1 Complete

---

## 🎯 MISSION FOR SESSION 464

Complete the **Market Intelligence Desk Learning Loop** by building the automation layer that:
1. Tracks prediction outcomes automatically (Celery tasks)
2. Calculates agent accuracy metrics (weekly)
3. Enables user feedback via Discord commands
4. Integrates confidence multipliers into predictions

**Goal:** Make the Market Intelligence Desk **learn and improve over time** without manual intervention.

---

## ✅ What Session 463 Accomplished

### Phase 1: Foundation (COMPLETE)

**Database Models Created:**
- ✅ `PredictionOutcome` - Tracks every bull/bear prediction vs actual outcome
- ✅ `UserBriefFeedback` - Captures user ratings and actions
- ✅ `AgentAccuracyMetrics` - Rolling accuracy scores with confidence multipliers

**Integration:**
- ✅ Coordinator creates prediction records automatically
- ✅ Discord delivery working (fixed datetime import + settings)
- ✅ Migration applied (0098_session_463_learning_loop)

**Files Modified:**
- `core/models_unified_system.py` (+680 lines)
- `core/agents/stocks/market_intelligence_coordinator.py` (+100 lines)
- `core/services/discord_notifications.py` (import fix)
- `core/settings.py` (DISCORD_BOT_TOKEN)

📖 **Full Details:** `docs/handoffs/SESSION_463_LEARNING_LOOP_PHASE1.md`

---

## 🚀 SESSION 464 TASKS (2-3 Hours)

### Task 1: Add Celery Tasks (30 min)

**File:** `core/tasks.py`

Add two new tasks at the end of the file:

#### 1.1 Prediction Outcome Tracking Task
```python
@shared_task(name='learning_loop.track_prediction_outcomes')
def track_prediction_outcomes():
    """
    Run daily at 6 PM (after market close)
    - Find predictions made 7 days ago → fetch current price → calculate accuracy
    - Find predictions made 30 days ago → fetch current price → calculate accuracy
    """
```

#### 1.2 Agent Accuracy Calculation Task
```python
@shared_task(name='learning_loop.calculate_agent_accuracy')
def calculate_agent_accuracy():
    """
    Run weekly on Sundays at 8 PM
    - Calculate BullCaseAgent and BearCaseAgent accuracy for past 30 days
    - Update confidence multipliers
    """
```

#### 1.3 Schedule Tasks in `core/celery.py`

---

### Task 2: Discord Feedback Commands (45 min)

**File:** `core/services/discord_bot.py`

Add 2 new commands:
- `/brief-feedback helpful|not-helpful [comment]`
- `/action buy|sell|hold|ignore TICKER [reason]`

---

### Task 3: Integrate Confidence Multipliers (30 min)

**Files:** `core/agents/stocks/bull_case_agent.py` and `bear_case_agent.py`

- Add `_get_confidence_multiplier()` method
- Modify `_determine_bull_conviction()` to use multiplier
- Log multiplier application

---

### Task 4: End-to-End Testing (30 min)

Test complete flow: predictions → outcomes → accuracy → multiplier → future predictions

---

## 📋 Definition of Done

- [ ] Two Celery tasks added and scheduled
- [ ] Two Discord commands working
- [ ] Confidence multipliers integrated into agents
- [ ] End-to-end test passes
- [ ] Code committed
- [ ] Handoff doc created: `SESSION_464_LEARNING_LOOP_COMPLETE.md`

---

**Session 464 Focus:** Build automation layer (Celery tasks + Discord commands + confidence integration)
**Estimated Time:** 2-3 hours
**Difficulty:** Medium

Let's complete the learning loop! 🚀

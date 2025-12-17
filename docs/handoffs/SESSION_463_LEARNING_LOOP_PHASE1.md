# Session 463: Learning Loop Phase 1 - Foundation Complete

**Date:** December 16, 2025
**Status:** ✅ Phase 1 Complete | ⏳ Phase 2 Pending
**Branch:** `feature/session-52-ai-assistant`
**Commit:** `fdc5581`

---

## 🎯 Mission Accomplished

Built the **foundation for the Market Intelligence Desk learning loop** - enabling the system to track prediction accuracy, learn from outcomes, and improve confidence calibration over time.

This is **Option 1 (Highest Value)** from the Session 462 roadmap: building a feedback loop so the autonomous situation gets smarter.

---

## ✅ What Was Built (Phase 1)

### 1. Database Models (680 lines of code)

Created 3 comprehensive models in `core/models_unified_system.py`:

#### **PredictionOutcome Model**
Tracks every bull/bear prediction vs actual price movement.

**Key Fields:**
- `ticker`, `prediction_type` (BULL/BEAR), `conviction_level` (HIGH/MEDIUM/LOW)
- `predicted_move` (percentage), `price_at_prediction`, `prediction_date`
- `price_after_7_days`, `price_after_30_days` (actual outcomes)
- `actual_move_7_days`, `actual_move_30_days` (actual returns)
- `was_correct_7_days`, `was_correct_30_days` (boolean accuracy)
- `accuracy_score_7_days`, `accuracy_score_30_days` (0-1 scoring)
- `market_regime`, `volatility_level` (context for pattern learning)
- `was_in_debate_zone`, `opposite_conviction` (debate tracking)
- `outcome_calculated`, `outcome_calculated_at` (status tracking)

**Methods:**
- `calculate_outcome(current_price, days_elapsed)` - Calculates accuracy with sophisticated scoring:
  - Right direction = 0.5-1.0 score (higher if magnitude is accurate)
  - Wrong direction = 0.0-0.3 score (penalty for large mistakes)

#### **UserBriefFeedback Model**
Captures user feedback and actions on Market Intelligence Briefs.

**Key Fields:**
- `user`, `brief` (foreign keys)
- `was_helpful` (boolean), `helpfulness_score` (1-5 stars)
- `actions_taken` (JSON array of buy/sell/hold actions per ticker)
- `viewed_at`, `acted_on_brief`, `time_to_action` (engagement metrics)
- `followed_bullish_recommendation`, `followed_bearish_warning` (follow-through)
- `explored_debate_zone` (did user research debate stocks?)
- `comment` (free-form feedback)

**Methods:**
- `record_action(ticker, action, reason)` - Records user actions with timestamps

#### **AgentAccuracyMetrics Model**
Rolling accuracy scores for BullCaseAgent and BearCaseAgent.

**Key Fields:**
- `agent_name` (BullCaseAgent or BearCaseAgent)
- `period_start`, `period_end` (measurement window)
- `total_predictions`, `correct_predictions_7_days`, `correct_predictions_30_days`
- `accuracy_rate_7_days`, `accuracy_rate_30_days` (percentage)
- `high_conviction_accuracy`, `medium_conviction_accuracy`, `low_conviction_accuracy`
- `bull_market_accuracy`, `bear_market_accuracy`, `neutral_market_accuracy`
- `debate_zone_accuracy`, `debate_zone_win_rate`
- **`confidence_multiplier`** (0.5-1.5x based on track record)

**Methods:**
- `calculate_metrics()` - Analyzes all predictions in period and updates all metrics
  - Calculates overall accuracy
  - Conviction calibration (are HIGH conviction predictions actually more accurate?)
  - Market regime performance (which markets does this agent predict best?)
  - **Dynamic confidence adjustment:**
    - >60% accuracy → increase confidence (up to 1.5x)
    - <40% accuracy → decrease confidence (down to 0.5x)
    - 50% accuracy → neutral (1.0x)

### 2. Migration

**File:** `core/migrations/0098_session_463_learning_loop.py`

- Creates all 3 models with proper indexes
- Includes foreign key relationships
- Unique constraints (one feedback per user per brief, one metric per agent per period)

### 3. Prediction Tracking Integration

**File:** `core/agents/stocks/market_intelligence_coordinator.py`

#### New Method: `_record_predictions_for_learning()`
- Called automatically after saving each brief
- Creates `PredictionOutcome` record for EVERY stock analyzed
- Captures:
  - Bull case predictions (target upside, conviction)
  - Bear case predictions (target downside, conviction)
  - Current price at prediction time
  - Market regime and volatility context
  - Debate zone status (were bull/bear in disagreement?)
  - Opposite agent's conviction level

#### Modified `_prepare_brief()` Method
Added internal storage of raw analyses:
```python
'_internal_bull_analyses': bull_results.get('bull_cases', []),
'_internal_bear_analyses': bear_results.get('bear_cases', []),
```

This allows the learning system to access full prediction details.

### 4. Discord Integration Fixes

**File:** `core/services/discord_notifications.py`
- ✅ Added missing `from datetime import datetime` import
- ✅ Fixed `datetime.datetime.utcnow()` → `datetime.utcnow()`
- ✅ Updated `DiscordNotificationService.__init__()` to read from Django settings
- ✅ Added logging when Discord is enabled/disabled

**File:** `core/settings.py`
- ✅ Added `DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')` after EXTERNAL_API_KEYS

**Result:** Discord delivery now works! Market Intelligence Briefs successfully posting to #stock-agents channel.

---

## 📊 How The Learning Loop Works

### Step 1: Predictions Made (Happening Now ✅)
Every time the Market Intelligence Desk runs:
1. Bull Case Agent analyzes 10 stocks → predictions stored in `PredictionOutcome`
2. Bear Case Agent analyzes 10 stocks → predictions stored in `PredictionOutcome`
3. Each prediction captures:
   - What we predicted (upside/downside %)
   - How confident we were (HIGH/MEDIUM/LOW)
   - Current price
   - Market context (bull/bear market, volatility)
   - Whether agents agreed or disagreed (debate zone)

### Step 2: Outcomes Tracked (Not Yet Implemented)
**Need to build:** Celery task that runs daily at 6 PM

For predictions made 7 days ago:
- Fetch current price
- Calculate actual return
- Determine if prediction was correct (direction + magnitude)
- Score accuracy (0-1 scale)

For predictions made 30 days ago:
- Same process but 30-day timeframe
- Longer-term accuracy measurement

### Step 3: Agent Performance Calculated (Not Yet Implemented)
**Need to build:** Celery task that runs weekly on Sundays

Analyzes all predictions from past 30 days:
- Bull Case Agent accuracy: X%
- Bear Case Agent accuracy: Y%
- Which conviction levels are calibrated? (is HIGH conviction actually more accurate?)
- Which market regimes does each agent perform best in?
- **Updates confidence multipliers** based on track record

### Step 4: Confidence Adjusted (Not Yet Implemented)
**Need to build:** Integration with Bull/Bear agents

When making new predictions:
- Check agent's current accuracy metrics
- Apply confidence multiplier to conviction scoring
- If agent has been wrong lately → lower confidence
- If agent has been right lately → higher confidence

### Step 5: User Feedback Incorporated (Not Yet Implemented)
**Need to build:** Discord commands

Users can rate briefs and record actions:
- `/brief-feedback helpful` → increases brief quality score
- `/action buy AAPL bull_case` → records that user followed bull recommendation
- Over time, learn which types of recommendations users actually follow

---

## 🚧 What's NOT Done Yet (Phase 2)

### 1. Celery Task: Track Prediction Outcomes
**File:** `core/tasks.py` (need to add)

```python
@shared_task(name='learning_loop.track_prediction_outcomes')
def track_prediction_outcomes():
    """
    Run daily at 6 PM (after market close)
    - Find predictions from 7 days ago → calculate outcomes
    - Find predictions from 30 days ago → calculate outcomes
    - Update PredictionOutcome records with actual results
    """
```

**Schedule:** Add to `core/celery.py`:
```python
'track-prediction-outcomes': {
    'task': 'learning_loop.track_prediction_outcomes',
    'schedule': crontab(hour=18, minute=0),  # 6 PM daily
},
```

### 2. Celery Task: Calculate Agent Accuracy
**File:** `core/tasks.py` (need to add)

```python
@shared_task(name='learning_loop.calculate_agent_accuracy')
def calculate_agent_accuracy():
    """
    Run weekly on Sundays at 8 PM
    - Calculate BullCaseAgent accuracy for past 30 days
    - Calculate BearCaseAgent accuracy for past 30 days
    - Update confidence multipliers
    - Log insights (which agent is performing better?)
    """
```

**Schedule:** Add to `core/celery.py`:
```python
'calculate-agent-accuracy': {
    'task': 'learning_loop.calculate_agent_accuracy',
    'schedule': crontab(day_of_week=0, hour=20, minute=0),  # Sunday 8 PM
},
```

### 3. Discord Feedback Commands
**File:** `core/services/discord_bot.py` (need to add)

Commands to implement:
- `/brief-feedback helpful|not-helpful [comment]` - Rate today's brief
- `/brief-feedback rate 1-5 [comment]` - Rate with stars
- `/action buy|sell|hold|ignore TICKER [reason]` - Record user action
  - Example: `/action buy AAPL bull_case`
  - Example: `/action sell TSLA bear_warning`

### 4. Confidence Multiplier Integration
**File:** `core/agents/stocks/bull_case_agent.py` and `bear_case_agent.py`

Modify `_determine_bull_conviction()` and `_determine_bear_conviction()` to:
1. Fetch latest `AgentAccuracyMetrics` for the agent
2. Get current `confidence_multiplier`
3. Apply multiplier to conviction determination logic
4. Log: "Using confidence multiplier 1.2x based on 65% recent accuracy"

### 5. Testing
- Run market desk → verify predictions created
- Wait 7 days → run outcome tracking → verify accuracy calculated
- Run accuracy calculation → verify metrics updated
- Test Discord commands → verify feedback recorded
- Verify confidence multipliers affect future predictions

---

## 📁 Files Changed

### Modified Files
- `core/models_unified_system.py` (+680 lines) - 3 new learning loop models
- `core/agents/stocks/market_intelligence_coordinator.py` (+100 lines) - Prediction tracking
- `core/services/discord_notifications.py` (+2 lines) - Import fix
- `core/settings.py` (+3 lines) - DISCORD_BOT_TOKEN setting

### New Files
- `core/migrations/0098_session_463_learning_loop.py` - Database migration

### Test Files (Not Committed)
- `test_discord_delivery.py` - Integration test for Discord delivery
- `test_learning_loop.py` - Learning loop testing
- `test_learning_loop_quick.py` - Quick smoke test

---

## 🎯 Next Session Priorities

**Session 464: Learning Loop Phase 2 - Automation**

1. **Add Celery Tasks** (30 min)
   - Implement `track_prediction_outcomes()` in tasks.py
   - Implement `calculate_agent_accuracy()` in tasks.py
   - Schedule both tasks in celery.py

2. **Add Discord Commands** (45 min)
   - Implement `/brief-feedback` command
   - Implement `/action` command
   - Link to UserBriefFeedback model

3. **Integrate Confidence Multipliers** (30 min)
   - Modify Bull/Bear agents to use multipliers
   - Log multiplier application
   - Test that low accuracy → lower confidence

4. **End-to-End Test** (30 min)
   - Run market desk → verify predictions created
   - Manually trigger outcome tracking → verify accuracy calculated
   - Trigger accuracy calculation → verify multipliers updated
   - Test Discord feedback → verify data recorded
   - Verify future predictions use adjusted confidence

**Total Estimated Time:** 2-3 hours

---

## 💡 Key Insights

### Why This Is High Value
1. **Self-Improvement:** System learns from mistakes and gets more accurate over time
2. **Calibrated Confidence:** High conviction predictions become genuinely more trustworthy
3. **Market Adaptability:** Different strategies for bull vs bear markets
4. **User Alignment:** Learns which recommendations users actually follow
5. **Feedback Loop:** Creates compounding intelligence gains

### Technical Highlights
- **Sophisticated Accuracy Scoring:** Not just right/wrong, but magnitude-aware scoring
- **Multi-Timeframe Tracking:** 7-day (short-term) and 30-day (medium-term) outcomes
- **Context Preservation:** Market regime, volatility, debate status all captured
- **Dynamic Confidence:** Automatically adjusts based on performance (0.5-1.5x range)
- **User Integration:** Bridges autonomous predictions with human decision-making

### Design Decisions
- **Separate models** instead of adding fields to existing models → cleaner, more extensible
- **Built-in calculation methods** → encapsulated logic, easy to test
- **Rolling 30-day windows** → recent performance matters more than distant past
- **Confidence multiplier cap** (0.5-1.5x) → prevents over-correction
- **Debate zone tracking** → learn when disagreement = uncertainty vs opportunity

---

## 🔗 Related Sessions

- **Session 462:** Market Intelligence Desk (First Autonomous Situation)
- **Session 419:** Discord Integration
- **Session 461:** Stock & Blockchain Audit Agents

---

## 📚 Documentation Updates Needed

- [x] Create this handoff doc
- [ ] Update `docs/CAPABILITIES.md` with learning loop features
- [ ] Update `docs/AGENTS.md` with confidence multiplier info
- [ ] Add learning loop to `CLAUDE.md` quick reference
- [ ] Update `00-START-NEXT-SESSION.md` for Session 464

---

## ✅ Verification Commands

```bash
# Check database models
.venv/bin/python manage.py shell -c "
from core.models_unified_system import PredictionOutcome, UserBriefFeedback, AgentAccuracyMetrics
print(f'PredictionOutcome: {PredictionOutcome.objects.count()}')
print(f'UserBriefFeedback: {UserBriefFeedback.objects.count()}')
print(f'AgentAccuracyMetrics: {AgentAccuracyMetrics.objects.count()}')
"

# Run market desk and check predictions created
.venv/bin/python manage.py shell -c "
from core.agents.stocks import run_market_intelligence_desk
from core.models_unified_system import PredictionOutcome
before = PredictionOutcome.objects.count()
result = run_market_intelligence_desk()
after = PredictionOutcome.objects.count()
print(f'Predictions created: {after - before}')
"

# Check Discord delivery status
curl -s http://localhost:8000/health/ping/
# Then check Discord #stock-agents channel for brief
```

---

**Session 463 Status:** ✅ Phase 1 Complete | Ready for Phase 2
**Next Up:** Celery automation tasks + Discord feedback commands + confidence integration

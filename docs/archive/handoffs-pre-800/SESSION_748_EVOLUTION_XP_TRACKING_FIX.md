# Session 748: Evolution XP Tracking Fix + Backfill

**Date:** January 14, 2026
**Focus:** Deep-dive into Evolution system - fixing XP history tracking, Celery task field mismatches, and backfilling historical XP

## Summary

Session 747 fixed the API field mismatches for the Evolution page. This session conducted a deep investigation into WHY only 1 XP record existed despite agents having accumulated 44,818 XP, and fixed multiple root causes:
1. Fixed `learning_loop.py` to use proper `award_xp()` method
2. Fixed Celery task `process_agent_activity_xp` field name mismatches
3. Created backfill command and awarded **30,284 XP** for historical activity

## Investigation Findings

### The Data Disconnect

| Metric | Before Fix |
|--------|------------|
| Total XP in Evolution records | 44,818 XP |
| XPHistory records | **1** (only 150 XP from "test" source) |
| Agents with `tasks_completed = 0` | All of them |
| Agents missing Evolution profiles | 15 |

**Question:** How did agents get 44,818 XP with only 1 XPHistory record?

### Root Cause Found

The `learning_loop.py` was directly modifying XP without creating history records:

**Before (problematic code at line 426):**
```python
evolution.total_xp += base_xp  # Direct modification - no history!

# Check for level up
old_level = evolution.current_level
new_level = self._calculate_level(evolution.total_xp)  # Custom calculation
if new_level > old_level:
    evolution.current_level = new_level
evolution.save()
```

This bypassed the model's `award_xp()` method which properly:
1. Creates XPHistory records
2. Uses consistent level calculation
3. Tracks abilities unlocked
4. Updates lifetime_xp

### XP Sources Identified

1. **Celery Task (`process_agent_activity_xp`)** - Runs every 15 minutes
   - Conversations: 5 XP each
   - Dreams: 3 XP each
   - Learning records: 8 XP each
   - Uses proper `award_xp()` method

2. **Learning Loop (`learning_loop.py`)** - The problem
   - Base: 10 XP per execution
   - +5 bonus for using spider data
   - +3 bonus for fast execution (<1s)
   - Was directly modifying XP without history

## Fixes Applied

### 1. Learning Loop XP Tracking (`core/super_platform/learning_loop.py`)

**After (fixed code):**
```python
evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)

# Build details string for XP history
details_parts = [f"Learning loop execution"]
if outcome.spider_data_used:
    details_parts.append("+5 spider data bonus")
if outcome.execution_time_ms < 1000:
    details_parts.append("+3 fast execution bonus")

# Use proper award_xp() method to create XPHistory record
result = evolution.award_xp(
    amount=base_xp,
    source='learning',
    details=', '.join(details_parts)
)

if result.get('leveled_up'):
    logger.info(f"Agent {agent_name} leveled up to {result['new_level']}!")
    if result.get('abilities_unlocked'):
        logger.info(f"Agent {agent_name} unlocked: {result['abilities_unlocked']}")
```

**Benefits:**
- XPHistory records now created for all learning loop XP
- Level calculations use model's exponential curve
- Ability unlocks tracked automatically
- Consistent with other XP sources

### 2. Removed Redundant `_calculate_level()` Method

The learning loop had its own level calculation that differed from the model's:

```python
# REMOVED - Was inconsistent with model's calculation
def _calculate_level(self, xp: int) -> int:
    thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]
    ...
```

Now uses `AgentEvolution.award_xp()` which internally uses:
```python
calculate_xp_for_level(level) = int(100 * (1.5 ** (level - 1)))
```

### 3. Initialized Missing Agent Evolution Profiles

15 agents were missing Evolution profiles:

| Agent | Status |
|-------|--------|
| ArbitrageDetector | Created |
| CampaignOrchestratorAgent | Created |
| ContentAuditAgent | Created |
| ExploitDetectorAgent | Created |
| MarketAnomalyDetectorAgent | Created |
| MarketMovementMonitorAgent | Created |
| NarrativeHistorianAgent | Created |
| PredictionMarketAnalyst | Created |
| SmartContractAuditorAgent | Created |
| SportsOddsAnalyst | Created |
| TechnicalDocumentAgent | Created |
| ThinkingAgent | Created |
| TransactionMonitorAgent | Created |
| WhaleWatcherAgent | Created |
| WorkflowOrchestrationAgent | Created |

**After:** 73 agents with Evolution profiles

## Files Modified

- `core/super_platform/learning_loop.py` - Fixed `_award_agent_xp()` to use proper `award_xp()` method, removed redundant `_calculate_level()`

## Evolution System Architecture (Documented)

### XP Award Flow

```
Agent Activity → XP Source → award_xp() → XPHistory Record
                    ↓
              Level Check → Level Up? → Ability Unlock Check
                    ↓
              Evolution.save()
```

### XP Sources

| Source | XP Amount | Trigger |
|--------|-----------|---------|
| Conversations | 5 XP | Celery task (15 min) |
| Dreams | 3 XP | Celery task (15 min) |
| Learning records | 8 XP | Celery task (15 min) |
| Learning loop execution | 10 XP base | On execution |
| Spider data used | +5 XP bonus | Learning loop |
| Fast execution (<1s) | +3 XP bonus | Learning loop |

### Level Progression

Level formula: `XP_required = 100 * (1.5 ** (level - 1))`

| Level | Title | XP Required | Cumulative XP |
|-------|-------|-------------|---------------|
| 1 | Novice | 0 | 0 |
| 2 | Apprentice | 100 | 100 |
| 3 | Journeyman | 150 | 250 |
| 4 | Adept | 225 | 475 |
| 5 | Expert | 337 | 812 |
| 6 | Master | 506 | 1,318 |
| 7 | Grandmaster | 759 | 2,077 |
| 8 | Sage | 1,138 | 3,215 |
| 9 | Oracle | 1,707 | 4,922 |
| 10 | Legendary | 2,561 | 7,483 |
| 11 | Omniscient | 3,841 | 11,324 |

### Level Distribution After Backfill

| Level | Title | Count |
|-------|-------|-------|
| 1 | Novice | 12 |
| 2 | Apprentice | 15 |
| 3 | Journeyman | 13 |
| 4 | Adept | 13 |
| 5 | Expert | 7 |
| 6 | Master | 4 |
| 7 | Grandmaster | 1 |
| 8 | Sage | 2 |
| 9 | Oracle | 1 |
| 10 | Legendary | 1 |
| 11 | Omniscient | 4 |

**Top Agent:** StockAuditCoordinator (Level 11, 9,110+ XP)

## Additional Fixes This Session

### 4. Celery Task Field Mismatches (`core/tasks.py`)

The `process_agent_activity_xp` Celery task was silently failing due to wrong field names:

| Model | Wrong Field | Correct Field |
|-------|-------------|---------------|
| AgentConversation | `created_at` | `started_at` |
| AgentConversation | `initiator`/`responder` | `participants` (M2M) |
| AgentDream | `created_at` | `dreamed_at` |
| AgentLearning | `agent` | `teacher_agent` + `student_agent` |

### 5. Backfill Management Command

Created `python manage.py backfill_evolution_xp` to award XP for all historical activity:

```bash
python manage.py backfill_evolution_xp          # Full backfill
python manage.py backfill_evolution_xp --dry-run  # Preview
python manage.py backfill_evolution_xp --days=30  # Last 30 days only
```

### Backfill Results

| Activity Type | Records | Awards | XP |
|---------------|---------|--------|-----|
| Conversations | 3,818 | 1,958 | 9,790 |
| Dreams | 7,543 | 6,762 | 20,286 |
| Learning | 49,706 | 26 | 208 |
| **TOTAL** | | **8,746** | **30,284** |

## Files Modified

- `core/super_platform/learning_loop.py` - Fixed `_award_agent_xp()` to use proper `award_xp()` method
- `core/tasks.py` - Fixed `process_agent_activity_xp` field name mismatches
- `core/management/commands/backfill_evolution_xp.py` - New backfill command

## Testing Verification

1. **Evolution Page displays all agents** - Now shows 73 agents
2. **XP Log populated** - 8,746 new XP awards created
3. **Level calculations consistent** - Using model's exponential curve
4. **Missing agents initialized** - All 15 created at Level 1
5. **Celery task fixed** - Will now award XP for new activity every 15 min

## Next Steps (Suggestions)

1. **Monitor XP Log** - Verify Celery awards XP for new activity
2. **Test ability unlocking** - No agents have unlocked abilities yet
3. **Add more XP sources** - Task completion, collaboration outcomes

# Session 747: Evolution Page API Fix

**Date:** January 14, 2026
**Focus:** Deep-dive into Evolution Page - fixing API field mismatches preventing data display

## Summary

The Evolution page was experiencing issues due to field name mismatches between what the backend API returned and what the frontend expected. This session identified and fixed these discrepancies, enabling the Evolution page to display data correctly.

## Issues Identified

### 1. Leaderboard API Field Mismatches (`/api/agent-evolution/leaderboard/`)

**Before (Backend returned):**
```json
{
  "rank": 1,
  "agent_id": "...",
  "agent_name": "...",
  "level": 11,
  "level_title": "Omniscient",
  "total_xp": 9070,
  "lifetime_xp": 0,
  "prestige": 0,        // Wrong field name
  "tasks_completed": 0,
  "tasks_failed": 0,
  "success_rate": 100.0
  // Missing: id, xp, xp_to_next_level, abilities_unlocked, created_at, updated_at
}
```

**Frontend expected:**
```typescript
interface AgentEvolution {
  id: string                    // MISSING
  agent_id: string              // OK
  agent_name: string            // OK
  level: number                 // OK
  xp: number                    // MISSING - current level progress
  xp_to_next_level: number      // MISSING
  total_xp: number              // OK
  prestige_level: number        // Backend sent "prestige"
  abilities_unlocked: string[]  // MISSING
  created_at: string            // MISSING
  updated_at: string            // MISSING
}
```

### 2. XP Gains API Field Mismatches (`/api/agent-evolution/xp-gains/`)

**Before (Backend returned):**
```json
{
  "agent_name": "ImageAgent",
  "amount": 150,           // Wrong field name
  "source": "test",        // Wrong field name
  "details": "...",
  "created_at": "..."      // Wrong field name
  // Missing: id
}
```

**Frontend expected:**
```typescript
interface XpGain {
  id: string            // MISSING
  agent_name: string    // OK
  xp_amount: number     // Backend sent "amount"
  reason: string        // Backend sent "source"
  recorded_at: string   // Backend sent "created_at"
}
```

## Fixes Applied

### 1. Leaderboard API Fix (`core/views_agent_evolution.py:374-415`)

Added missing fields and renamed `prestige` to `prestige_level`:

```python
# Session 747: Calculate XP progress within current level
xp_to_next = evo.calculate_xp_for_level(evo.current_level + 1) - evo.calculate_xp_for_level(evo.current_level)
xp_in_current_level = evo.total_xp - evo.calculate_xp_for_level(evo.current_level)

# Get unlocked abilities
abilities_unlocked = list(evo.abilities.filter(is_active=True).values_list('ability_name', flat=True))

leaderboard.append({
    'id': str(evo.id),
    'rank': rank,
    'agent_id': str(evo.agent.id),
    'agent_name': evo.agent.name,
    'level': evo.current_level,
    'level_title': evo.get_title(),
    'xp': xp_in_current_level,
    'xp_to_next_level': xp_to_next,
    'total_xp': evo.total_xp,
    'lifetime_xp': evo.lifetime_xp,
    'prestige_level': evo.prestige_level,  # Renamed from 'prestige'
    'abilities_unlocked': abilities_unlocked,
    'tasks_completed': evo.tasks_completed,
    'tasks_failed': evo.tasks_failed,
    'success_rate': ...,
    'created_at': evo.created_at.isoformat() if evo.created_at else None,
    'updated_at': evo.updated_at.isoformat() if evo.updated_at else None,
})
```

### 2. XP Gains API Fix (`core/views_agent_evolution.py:420-440`)

Renamed fields to match frontend expectations:

```python
gains.append({
    'id': str(xp.id),           # Added
    'agent_name': xp.agent.name,
    'xp_amount': xp.xp_amount,  # Renamed from 'amount'
    'reason': xp.source,        # Renamed from 'source'
    'details': xp.details,
    'recorded_at': xp.created_at.isoformat()  # Renamed from 'created_at'
})
```

## API Response After Fix

### Leaderboard (`/api/agent-evolution/leaderboard/?limit=2`)
```json
{
  "success": true,
  "leaderboard": [
    {
      "id": "647985c8-a34e-43dc-aa1c-bfa1ba77e491",
      "rank": 1,
      "agent_id": "24cdd155-5419-42bc-a835-d7c1ab130d0c",
      "agent_name": "StockAuditCoordinator",
      "level": 11,
      "level_title": "Omniscient",
      "xp": 3314,
      "xp_to_next_level": 2883,
      "total_xp": 9080,
      "lifetime_xp": 0,
      "prestige_level": 0,
      "abilities_unlocked": [],
      "tasks_completed": 0,
      "tasks_failed": 0,
      "success_rate": 100.0,
      "created_at": "2025-12-23T20:53:44.989069+00:00",
      "updated_at": "2026-01-14T19:54:00.863956+00:00"
    }
  ]
}
```

### XP Gains (`/api/agent-evolution/xp-gains/?limit=3`)
```json
{
  "success": true,
  "xp_gains": [
    {
      "id": "ed5918fb-923e-4d5e-a7c0-3f7f651d7c75",
      "agent_name": "ImageAgent",
      "xp_amount": 150,
      "reason": "test",
      "details": "Testing XP award",
      "recorded_at": "2025-11-28T21:02:07.426320+00:00"
    }
  ]
}
```

## Files Modified

- `core/views_agent_evolution.py` - Fixed leaderboard and XP gains API responses

## Evolution Page Features (Verified Working)

1. **Leaderboard Tab**
   - Shows all agents sorted by level and XP
   - XP progress bars display correctly
   - Level tiers (Novice → Legendary) with color coding
   - Prestige indicators for high-level agents
   - Search/filter functionality

2. **Abilities Tab**
   - Lists 9 unlockable abilities
   - Shows unlock level requirements
   - Displays ability descriptions

3. **XP Log Tab**
   - Shows recent XP gains across agents
   - Displays reason/source for each gain
   - Timestamps formatted correctly

4. **Agent Detail Panel**
   - Level badge with tier styling
   - XP progress bar
   - Unlocked abilities list
   - Quick stats (level, prestige, abilities count, rank)

## Current Evolution Data

| Metric | Value |
|--------|-------|
| Top Agent | StockAuditCoordinator (Level 11, 9080 XP) |
| Total XP Gains Logged | 1 |
| Available Abilities | 9 |
| Max Level Observed | 11 (Omniscient) |

## Testing Checklist

- [x] Leaderboard displays agents with correct XP progress
- [x] XP progress bars animate correctly
- [x] Level tier colors display (gray/green/blue/purple/orange/yellow/red)
- [x] Abilities tab shows all 9 abilities
- [x] XP Log shows recent gains with correct field names
- [x] Agent detail panel displays when clicking agent
- [x] Search filter works for agent names
- [x] Refresh button triggers data reload
- [x] Frontend build passes

## Next Steps (Suggestions)

1. **Add more XP gain events** - Currently only 1 XP gain logged
2. **Ability unlocking** - No agents have unlocked abilities yet
3. **Prestige system** - No agents have prestiged (reset to level 1 with bonuses)
4. **Level milestones** - Track and display when agents reach new levels
5. **XP source visualization** - Show breakdown of where XP comes from

# Session 355: Agents Tab Comprehensive Audit & Plan

**Date:** December 5, 2025
**Goal:** Make ALL features on the Agents tab work together and display correctly

---

## Current State Summary

### API Endpoints - ALL WORKING
| Endpoint | Status | Data |
|----------|--------|------|
| `/api/spider-intelligence/dashboard-stats/` | OK | 79 agents, 750 knowledge sources |
| `/api/agent-conversations/` | OK | Has data |
| `/api/agent-dreams/` | OK | 10 dreams, 179 today |
| `/api/agent-learning/activity/` | OK | 20 feed items |
| `/api/hive-mind/agents/` | OK | 24 agents |
| `/api/hive-mind/sessions/` | OK | 3 sessions |
| `/api/agent-mood/` | OK | 24 agents with moods |
| `/api/agent-relationships/` | OK | 380 relationships |
| `/api/agent-evolution/` | OK | 875 XP |
| `/api/predictions/` | OK | (empty) |
| `/api/time-capsules/` | OK | 6 sealed |

---

## Issues Found & Fixes Needed

### 1. OVERVIEW TAB Issues

| Metric | Current | Issue |
|--------|---------|-------|
| Collaborations | 0 | No collaboration sessions recorded |
| Learning Events | 0 | No learning events being tracked |
| Knowledge Transfers | 55 | Working |
| Agent Memories | 59 | Working |
| Knowledge Sources | 750 | Working |

**Root Cause:** Collaborations and learning events come from `CollaborationSession` and related models. Need to verify agents are creating these during execution.

**Fix:** Ensure `_record_learning_outcome()` is called in agent execute methods.

---

### 2. SOCIAL TAB Issues

| Feature | Status | Notes |
|---------|--------|-------|
| Agent Workspace (Slack) | Unknown | WebSocket-based, needs manual test |
| Agent Conversations | OK | Has data |
| Agent Dreams | OK | 179 today, working |
| Boardroom Decisions | Unknown | Needs test |
| Learning Activity Feed | OK | 20 items |

**Action:** Test WebSocket connections for Slack workspace.

---

### 3. INTELLIGENCE TAB Issues

| Feature | Current | Issue |
|---------|---------|-------|
| Hive Mind | 24 agents, 3 sessions | Working |
| Agent Moods | 24 agents | 23 are "calm", only 1 "inspired" - needs variety |
| Relationships | 380 total | **0 alliances, 0 rivalries** - all neutral! |

**Root Cause:** Relationships exist but none have been classified as alliance/rivalry.

**Fix:** Run `autoGenerateRelationships()` or classify existing relationships.

---

### 4. GROWTH TAB Issues

| Feature | Current | Issue |
|---------|---------|-------|
| Evolution Total XP | 875 | Has XP! |
| Evolution Levels | 0 | **No levels despite XP** |
| Evolution Agents | 0 | **No agents initialized** |
| Time Travel | Unknown | Needs test |
| Personalities | Unknown | Needs test |

**Root Cause:** XP exists but agents haven't been initialized with evolution stats.

**Fix:** Call `initializeEvolution()` to create AgentEvolution records.

---

### 5. MEMORY TAB Issues

| Feature | Current | Issue |
|---------|---------|-------|
| Memory Clusters | Unknown | Needs test |
| Predictions | 0 | **No predictions generated** |
| Time Capsules | 6 sealed, 0 ready | Working but none ready to reveal |
| Memory Palace | 59 memories | Working |

**Root Cause:** Predictions aren't being generated from dreams.

**Fix:** Call `generatePredictionsFromDreams()` to create predictions.

---

## Priority Action Plan

### Phase 1: Initialize Missing Data (Quick Wins)
1. **Initialize Evolution** - Call `/api/agent-evolution/initialize/`
2. **Generate Relationships** - Call `/api/agent-relationships/auto-generate/`
3. **Generate Predictions** - Call `/api/predictions/generate-from-dreams/`
4. **Trigger Dreams** - Ensure dreams are creating predictions

### Phase 2: Fix Data Flow
1. **Learning Events** - Verify `_record_learning_outcome()` is called
2. **Collaborations** - Check if collaboration sessions are being created
3. **Mood Variety** - Ensure moods are being updated during agent work

### Phase 3: UI Verification
1. Test each tab loads and displays data correctly
2. Test interactive features (buttons, modals, selectors)
3. Test real-time features (WebSocket, Slack workspace)

### Phase 4: Integration Testing
1. Run a full agent workflow and verify all metrics update
2. Verify UI reflects real-time changes
3. Document any remaining issues

---

## Detailed Fixes

### Fix 1: Initialize Evolution
```bash
curl -X POST http://localhost:8000/api/agent-evolution/initialize/
```

### Fix 2: Generate Relationships
```bash
curl -X POST http://localhost:8000/api/agent-relationships/auto-generate/
```

### Fix 3: Generate Predictions from Dreams
```bash
curl -X POST http://localhost:8000/api/predictions/generate-from-dreams/
```

### Fix 4: Verify Learning Events Recording
Check that agents call `_record_learning_outcome()` in their `execute()` method.

### Fix 5: Classify Neutral Relationships
Need to update relationships to have actual types (alliance/rivalry).

---

## Success Criteria

When complete, the Agents tab should show:

| Tab | Metrics Should Show |
|-----|---------------------|
| Overview | All numbers > 0, success rate shown |
| Social | Dreams with reactions, conversations streaming, learning feed active |
| Intelligence | Hive Mind working, varied moods, alliances AND rivalries |
| Growth | XP leaderboard, levels > 0, time travel sessions |
| Memory | Predictions, clusters, time capsules ready to reveal |
| Workflows | Analytics charts, training templates |

---

## Files to Check

| File | Purpose |
|------|---------|
| `core/views_scifi_features.py` | Sci-fi feature APIs |
| `core/views_hive_mind.py` | Hive Mind APIs |
| `core/views_time_travel.py` | Time Travel APIs |
| `core/views_spider_dashboard.py` | Dashboard stats |
| `core/models_unified_system.py` | All the models |
| `ai_core/templates/ai_image_studio.html` | UI JavaScript |

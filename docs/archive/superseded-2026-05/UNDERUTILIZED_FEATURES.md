# Underutilized Features

**Last Updated:** December 10, 2025 (Session 412)
**Purpose:** Inventory of features that were built but never fully integrated or used

---

## Summary

Over 411 development sessions, we've built many features that are either:
1. **Never used** - Fully implemented but not integrated
2. **Partially used** - Integrated but rarely exercised
3. **Planned but incomplete** - Blueprint exists, implementation pending

### Investment Summary

| Feature | Investment | Usage | ROI |
|---------|------------|-------|-----|
| DaVinci Resolve Node | $300+ | Never used | $0 |
| Discord Bot | ~$0 (API free) | Not deployed | $0 |
| Boardroom Decisions | ~8 hours dev | Blueprint only | $0 |
| 3D Generation | Replicate credits | Rarely used | Low |
| Flutter Mobile App | Many sessions | Archived | $0 |

---

## 1. DaVinci Resolve Render Node

**Investment:** $300+ (license) + Session 103
**Location:** `/resolve_node/`
**Status:** Complete but never integrated

### What We Built
- FastAPI REST server for render jobs
- Job queue with persistence
- DaVinci Resolve Python API integration
- Auto-upload to Django backend
- Token authentication
- Comprehensive tests

### Why Unused
- ffmpeg is faster for simple operations (2-5s vs 20-30s)
- No UI integration ever built
- Requires DaVinci Resolve running as separate process

### Activation Path
1. Add "Professional Render" toggle to Video tab
2. Create `ResolveAgent` wrapper
3. Connect to VideoEditingAgent tools

**Full Documentation:** [DAVINCI_RESOLVE.md](DAVINCI_RESOLVE.md)

---

## 2. Discord Bot Integration

**Investment:** ~2 hours (Session 399)
**Location:** `ai_core/spiders/real_data_collector.py`
**Status:** Configured but not deployed

### What We Built
- Bot token configured in `.env` as `DISCORD_BOT_TOKEN`
- Bot ID: 1444884424339755008
- Data collection function: `_collect_discord_data()`
- Can collect guild info, channel info, messages

### Why Unused
- Bot needs to be invited to servers
- No automation to trigger collection
- No UI to display Discord data

### Activation Path
1. Invite bot to relevant Discord servers
2. Add Discord spider to Celery Beat schedule
3. Display Discord insights in Intelligence tab

**Invite URL:**
```
https://discord.com/api/oauth2/authorize?client_id=1444884424339755008&permissions=66560&scope=bot
```

**Full Documentation:** [DISCORD_BOT_SETUP.md](DISCORD_BOT_SETUP.md)

---

## 3. Boardroom Decisions System

**Investment:** Session 322 (blueprint only)
**Location:** `docs/handoffs/SESSION_322_BOARDROOM_DECISIONS_BLUEPRINT.md`
**Status:** Blueprint complete, not implemented

### What Was Planned
Agent conversations generate valuable governance artifacts:
- Prompt Engineering Policies
- Memory Isolation Architecture
- Image Pipeline Specifications

The plan was to:
1. Extract structured decisions from conversation conclusions
2. Store in `AgentDecisionSummary` model
3. Display in "Boardroom Decisions" UI
4. Promote to canonical policies
5. Feed back to agents to influence behavior

### Why Not Implemented
- Other priorities (Legal Assistant, Spider Network)
- Blueprint was comprehensive but no follow-up session

### Activation Path
1. Create `AgentDecisionSummary` model
2. Add extraction logic to conversation post-save
3. Build Boardroom UI tab
4. Implement policy promotion workflow

---

## 4. 3D Model Generation

**Investment:** Replicate API integration (Session ~74)
**Location:** `content/replicate_provider.py`, `ThreeDAgent`
**Status:** Working but rarely used

### What We Built
- Integration with Replicate for 3D generation
- `ThreeDAgent` in clean architecture
- GLB download capability (Session 172)
- Sequential numbering in UI

### Why Underused
- 3D generation is slow (minutes)
- Limited use cases in current workflows
- Users primarily use image/video features

### Activation Path
- Already working! Just needs user awareness
- Could add to workflow templates
- Promote in "Create" dropdown

---

## 5. Flutter Mobile App

**Investment:** Multiple sessions (archived)
**Location:** `/archive/mobile/` (if archived) or removed
**Status:** Development paused/archived

### What Was Built
- React Native / Flutter app skeleton
- Some basic screens
- API connectivity

### Why Archived
- Focus shifted to web platform
- Maintenance burden
- Web app works on mobile browsers

### Activation Path
- Would require significant investment to revive
- Better to use PWA approach with current web app

---

## 6. Agent Prophecies/Predictions

**Investment:** Session 254
**Location:** `core/models_unified_system.py` - `AgentPrediction` model
**Status:** Model exists, rarely used

### What We Built
- `AgentPrediction` model for agent predictions
- Integration in sci-fi features
- Dream generation can create predictions

### Why Underused
- No dedicated UI to view predictions
- Not surfaced to users
- Predictions not validated against outcomes

### Activation Path
1. Add "Prophecies" sub-tab to Agents tab
2. Create prediction validation system
3. Track prediction accuracy

---

## 7. Time Capsules

**Investment:** Session 254
**Location:** `core/models_unified_system.py` - `TimeCapsule` model
**Status:** Model exists, not integrated

### What We Built
- `TimeCapsule` model for messages to future selves
- Scheduled reveal dates
- Agent authorship tracking

### Why Unused
- No UI to create or view time capsules
- No scheduled task to "open" capsules
- Cool concept, no execution

### Activation Path
1. Add "Time Capsules" UI
2. Create Celery task to reveal capsules on date
3. Add notification when capsule opens

---

## 8. Revenue Pipeline (Phases 1-6)

**Investment:** Sessions 223-236
**Location:** `core/models_unified_system.py` - Opportunity, Revenue models
**Status:** Complete but not generating revenue

### What We Built
- Opportunity scoring engine
- Revenue tracking models
- Distribution channels
- Learning loop
- Proactive alert system
- A/B testing framework

### Why Underused
- No actual revenue sources connected
- Spider data isn't monetized
- Opportunity scoring exists but isn't acted on

### Activation Path
1. Connect real revenue sources
2. Build actual monetization workflows
3. Track real money, not just opportunities

---

## 9. Executive Agents (CTO, COO, CreativeDirector)

**Investment:** Session 280
**Location:** `core/agents/`
**Status:** Exist but rarely invoked

### What We Built
- `CTOAgent` - Technical planning
- `COOAgent` - Operations planning
- `CreativeDirectorAgent` - Creative guidance
- `MeetingCoordinatorAgent` - Coordinates meetings

### Why Underused
- PersonalAssistant routes most requests to creation agents
- No explicit "consult CTO" workflow
- Users don't know they can ask for executive guidance

### Activation Path
1. Add "Consult Executive" button in UI
2. Create executive consultation workflows
3. Surface in "Strategy" tab

---

## 10. Style Memory Learning

**Investment:** Session 169
**Location:** `style_memory/` app
**Status:** Working but passive

### What We Built
- AI learns from user ratings
- Style preferences tracked
- Affects future generations

### Why Underused
- Users rarely rate images
- No prominent UI for rating
- Learning is implicit, not visible

### Activation Path
1. Add more prominent rating UI
2. Show "AI learned from your feedback" messages
3. Display style preference profile

---

## Recommendations

### Quick Wins (< 1 session each)
1. **Discord Bot** - Just invite to servers and add to Celery Beat
2. **3D Generation** - Already working, just needs promotion
3. **Executive Agents** - Add "Consult" buttons to UI

### Medium Effort (1-3 sessions)
1. **DaVinci Resolve** - Add UI toggle for professional rendering
2. **Boardroom Decisions** - Implement Phase 1 from blueprint
3. **Time Capsules** - Build simple UI and reveal task

### High Effort (3+ sessions)
1. **Revenue Pipeline Activation** - Connect real money sources
2. **Flutter Mobile App** - Better to skip, use PWA
3. **Full Boardroom System** - All 3 phases from blueprint

---

## Cost of Inaction

| Feature | Sunk Cost | Ongoing Cost | Opportunity Cost |
|---------|-----------|--------------|------------------|
| DaVinci Resolve | $300 | $0 | Pro video capabilities |
| Discord Bot | $0 | $0 | Community intelligence |
| Boardroom | ~8 hrs | $0 | Self-improving governance |
| Revenue Pipeline | ~20 hrs | $0 | Actual revenue |

**Total sunk cost:** ~$300 + ~40 hours of development time

---

## Conclusion

We have significant untapped capabilities. The most impactful would be:

1. **DaVinci Resolve** - Differentiate with pro video quality
2. **Boardroom Decisions** - Make agents self-governing
3. **Revenue Pipeline** - Turn opportunities into money

These features represent the difference between a "demo platform" and a "production platform."

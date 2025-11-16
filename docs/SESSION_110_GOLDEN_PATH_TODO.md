# SESSION 110 - Golden Path TODO

**Date:** November 15, 2025
**Status:** Phase 0 - Inventory Complete

---

## ✅ CONFIRMED WORKING COMPONENTS

### Backend
1. **Co-Leadership System** (`coleadership/`)
   - Models: `CoLeadershipDecision`, `AgentRecommendation`, `HumanDecision`, `DecisionOutcome`
   - API endpoints: `/api/v1/coleadership/`
   - Boardroom integration: `agents/meeting_coordinator_agent.py`
   - Status: ✅ Fully functional

2. **Creative Pipelines** (`pipelines/`)
   - Models: `CreativePipelineTemplate`, `CreativePipelineRun`
   - API endpoints: `/api/v1/pipelines/`
   - Status: ✅ Complete (Session 109)

3. **Video Studio** (DaVinci Resolve Render Node)
   - Models: `DaVinciRenderJob`
   - API endpoints: `/api/v1/davinci/`
   - Status: ✅ Complete (Session 103)

4. **Projects & Sessions**
   - Models: `CreativeProject`, `AISession`
   - API endpoints: `/api/v1/projects/`, `/api/v1/sessions/`
   - Status: ✅ Complete

### Mobile (Flutter)
1. **Donkey Cockpit** (`lib/features/cockpit/donkey_cockpit_screen.dart`)
   - 4 Cards: Leadership, Projects, Video Studio, System
   - Navigation to all key screens
   - Status: ✅ Working but **missing Creative Pipelines link**

2. **Leadership Screens**
   - `DecisionsListScreen`: View all decisions
   - `DecisionDetailScreen`: View decision details, commit, log outcome
   - `LeadershipDashboard`: Stats overview
   - `BoardroomFormScreen`: Start new meeting
   - Status: ✅ Complete (Session 108)

3. **Creative Pipelines Screens** (`lib/features/pipelines/`)
   - `PipelinesScreen`: Templates + Recent Runs tabs
   - `PipelineRunDetailScreen`: Run detail with live polling
   - Status: ✅ Complete (Session 109)

4. **Video Studio Screens** (`lib/features/render/`)
   - `VideoStudioScreen`: Main studio screen
   - `RenderJobsScreen`: Render queue
   - Status: ✅ Complete (Session 107)

5. **Projects & Sessions Screens** (`lib/features/projects/`)
   - `ProjectListScreen`: Browse projects
   - `ProjectDetailScreen`: View sessions and assets
   - Status: ✅ Complete (Session 101)

---

## ❌ ROUGH EDGES IDENTIFIED

### HIGH PRIORITY (Breaks Golden Paths)

1. **CRITICAL: Donkey Cockpit Missing Creative Pipelines**
   - File: `mobile/lib/features/cockpit/donkey_cockpit_screen.dart`
   - Issue: No card or section for Creative Pipelines (Session 109 feature)
   - Impact: Users cannot discover the "Idea to Assets" golden path
   - Fix: Add "Creative Pipelines" card with template shortcuts

2. **Inconsistent Terminology**
   - DecisionsListScreen empty state: "Run an executive meeting"
   - Donkey Cockpit button: "Start Boardroom Meeting"
   - Issue: Confusing - should use "Boardroom Meeting" everywhere
   - Fix: Update DecisionsListScreen to say "Start a Boardroom Meeting from the Donkey Cockpit"

3. **No Golden Path Hints**
   - PipelinesScreen: No hint about what to do first
   - DecisionsListScreen: Empty state is okay but could be better
   - Fix: Add dismissible hint banners to guide new users

### MEDIUM PRIORITY (Polish)

4. **Wordy Section Titles**
   - Donkey Cockpit: "Leadership & Co-Leadership" is verbose
   - Suggestion: Simplify to "Strategic Co-Leadership" (matches brief)

5. **Empty State Improvements**
   - PipelinesScreen: Needs better empty state guidance
   - VideoStudioScreen: Check if empty state exists and is helpful
   - Fix: Ensure all empty states have clear next action

6. **Navigation Consistency**
   - Verify all Back buttons lead to expected screens
   - Ensure no orphaned navigation states
   - Test: Full navigation flow for both golden paths

### LOW PRIORITY (Nice to Have)

7. **Status Chip Color Consistency**
   - Verify status chips use consistent colors across:
     - DecisionsListScreen
     - PipelinesScreen
     - VideoStudioScreen
   - Current: Appears consistent, verify in testing

8. **Demo Content**
   - No seeded demo data for quick demos
   - Need: Management command to create demo:
     - 1 completed decision with outcome
     - 1-2 completed pipeline runs with images
     - Sample render job

---

## 📋 GOLDEN PATHS (Draft)

### Golden Path 1: Strategic Decision Loop
**Entry:** Donkey Cockpit → Leadership & Co-Leadership card
**Flow:**
1. Tap "Start Boardroom Meeting"
2. Enter topic (e.g., "Q1 AI Feature Roadmap")
3. Submit → AI agents provide recommendations
4. View in "Open Leadership Cockpit" or DecisionsListScreen
5. Tap decision → View recommendations
6. Tap "Commit Decision" → Choose path and justify
7. Later: Log outcome
8. View "I Told You So" reflection (if enabled)

**Missing:** Creative Pipelines golden path entry!

### Golden Path 2: Idea to Publish-Ready Assets
**Entry:** ??? (NOT IN DONKEY COCKPIT YET!)
**Flow:**
1. Navigate to Pipelines (how?)
2. Templates tab → Tap "Idea to Image Set"
3. Enter idea and parameters
4. Tap "Launch"
5. Recent Runs tab → Watch progress
6. Tap run → View outputs (images)
7. (Future: Open in Video Studio for editing)

**BLOCKER:** No entry point from Donkey Cockpit!

---

## 🎯 NEXT STEPS (Phase 1)

1. Create `docs/GOLDEN_PATHS_V1.md` with official flow documentation
2. Add Creative Pipelines card to Donkey Cockpit (CRITICAL)
3. Update terminology to "Boardroom Meeting" everywhere
4. Add golden path hint banners
5. Create demo seed command
6. Polish empty states
7. Test end-to-end flows

---

**Session 110 Phase 0 - Complete!**
**Ready for Phase 1: Define Official Golden Paths**

# Claude Code Handoff Notes - UI Cleanup & System Status

## Date: 2025-01-19
## Current Working Directory: `/Users/donkeyking/development/unified-donkey-betz/frontend`

## What Was Completed

### 1. UI Overlay Issues Fixed
- **Problem**: Dashboard at `http://localhost:3000/dashboard` was covered by a large gray overlay with sparkle icons
- **Root Causes Identified & Fixed**:
  - `UnifiedAIAssistant` component (AI chat widget) - DISABLED in `/frontend/src/App.tsx` line 201
  - `StyleInsightsDashboard` component (full-screen overlay) - DISABLED in `/frontend/src/components/layout/AppLayout.tsx` line 33
  - `StyleLineageVisualization` component (another overlay) - DISABLED in `/frontend/src/components/layout/AppLayout.tsx` line 34
  - `CommandPalette` component (Cmd+K search modal) - DISABLED in `/frontend/src/App.tsx` line 200

### 2. System Architecture Confirmed
- **Startup Script**: `./start_ws_quick.sh` is the main script to start all services
  - Stops existing services
  - Starts Redis and PostgreSQL
  - Runs Django migrations
  - Starts backend with Daphne (WebSocket support) on port 8000
  - Starts frontend with Vite on port 3000
  - Monitors both services

### 3. Current File Status (from git)
- Multiple modified frontend components (not committed)
- Main changes: Disabled overlay components to fix UI visibility issues

## What Still Needs to Be Addressed

### 1. UI/UX Refactoring
- User reports "something is not right" with the UI even after removing overlays
- May need deeper investigation into:
  - Component rendering issues
  - CSS conflicts
  - Z-index problems
  - Responsive layout issues

### 2. Re-enable Features Safely
Once UI is stable, need to:
- Re-implement AI Assistant without blocking UI
- Fix StyleInsightsDashboard to not auto-show on load
- Ensure CommandPalette only shows when triggered (Cmd+K)

### 3. Component Investigation Areas
Check these files for potential issues:
- `/frontend/src/components/betting/SportsBettingDashboard.tsx` (user had this open)
- `/frontend/src/pages/dashboard/DashboardPage.tsx` (main dashboard component)
- `/frontend/src/components/layout/AppLayout.tsx` (main layout wrapper)

### 4. Potential CSS/Styling Issues
- Check for conflicting z-index values
- Look for `fixed` or `absolute` positioned elements that might overlap
- Review Tailwind classes for unintended effects
- Check if any modals/dialogs are stuck open

## Quick Commands for Debugging

```bash
# Restart everything
./start_ws_quick.sh

# Check frontend logs
tail -f frontend.log

# Check backend logs
tail -f ai_core.log

# Quick API test
python quick-api-test.py

# Force refresh frontend (if exists)
./force-refresh-frontend.sh

# Check what's running on ports
lsof -i:3000  # Frontend
lsof -i:8000  # Backend
```

## Key Files Modified (Need Review)
1. `/frontend/src/App.tsx` - Disabled CommandPalette and UnifiedAIAssistant
2. `/frontend/src/components/layout/AppLayout.tsx` - Disabled Style Memory overlays

## Recommended Next Steps
1. Get user to test current state after refresh
2. If still issues, check browser console for errors
3. Inspect element to see what's rendering on top
4. Consider removing more components temporarily to isolate issue
5. Once clean slate achieved, re-add components one by one

## Important Context
- Platform has 149 AI agents
- Uses Django backend + React frontend
- WebSocket support via Daphne
- Dark theme gaming-style UI
- Multiple complex components that may interfere with each other

## User Authentication (if needed)
- Username: command_center
- Password: donkeybetz123
- API Token: <redacted-0fb2390d-2026-04-20>

---
*This handoff document created to help next Claude instance understand the current state and continue debugging the UI issues effectively.*
# Stock Scout Display Fix Summary

## Problem Identified
Stock Scout missions were completing successfully but showing 0 opportunities in the Business Hub because:
1. Agents generate text reports with steps, not structured opportunity data
2. Opportunities need to be extracted from text and saved to StockOpportunity model
3. The UI was counting opportunities from the database, which were not being populated

## Solutions Implemented

### 1. Fixed Opportunity Count in Backend ✅
Updated `/backend/agent_orchestra/views_stock_scout.py` to:
- Check StockOpportunity model first for actual saved opportunities
- Fall back to synthesis agent output if no DB records
- Added 'Stock Synthesis Agent' to recognized template names

### 2. Added Extract Button to Frontend ✅
Updated `/donkey-betz-frontend/src/features/business-hub/components/StockScoutHistory.tsx`:
- Added `handleExtractOpportunities` function
- Shows "Extract Opportunities" button on completed missions with 0 opportunities
- Auto-extracts when viewing details of completed missions

### 3. Existing Infrastructure
The extraction endpoint already exists:
```
POST /api/agent-orchestra/stock-opportunities/extract/<orchestration_id>/
```

## How It Works Now

1. **User runs Stock Scout** → Agents generate text analysis
2. **Mission completes** → Shows in Business Hub with 0 opportunities
3. **User clicks "Extract Opportunities"** → Backend parses agent text
4. **Opportunities saved to database** → Count updates in UI
5. **Opportunities appear in Stock Dashboard** → Ready for review

## Database Status
- 12 opportunities already in database (from manual extractions)
- Orchestrations 250, 256, 288 have saved opportunities
- Recent missions need extraction

## Next Steps for User

1. **Restart Django server** to apply backend fix
2. **Refresh the Business Hub page**
3. **Click "Extract Opportunities"** on completed missions
4. **View extracted opportunities** in Stock Dashboard

## Technical Details

### Agent Output Structure
```json
{
  "step_1": "Analysis step 1...",
  "step_2": "Analysis step 2...",
  // No "opportunities" array
}
```

### What Extractor Looks For
- Stock tickers (1-5 characters, uppercase)
- Price mentions ($XX.XX)
- Investment thesis text
- Buy/sell recommendations

### Frontend Changes
- Added extract button with hover effects
- Auto-extraction on detail view
- Toast notifications for success/failure
- Automatic UI refresh after extraction

## Success Metrics
- Completed missions should show opportunity counts
- Extract button should disappear after successful extraction
- Opportunities should appear in Stock Dashboard
- No more "0 Opportunities" for completed missions
# Stock Scout Cleanup Solution

## Problem
- Stock Scout missions show 0 opportunities even after extraction
- Old missions have malformed data that can't be properly extracted
- Need to clean up and start fresh

## Solution Implemented

### 1. Frontend Delete Functionality ✅

#### Individual Mission Delete
Added delete button to each mission card in the list:
- Red trash icon appears on each mission
- Confirmation dialog before deletion
- Immediate removal from UI

#### Mission Details Delete
Added "Delete Mission" button in the details modal:
- Red button with clear labeling
- Confirmation before deletion
- Modal closes after successful deletion

### 2. Backend Support ✅
The Django REST API already supports DELETE operations on orchestrations:
```
DELETE /api/agent-orchestra/orchestrations/<id>/
```

### 3. Cleanup Script ✅
Created `clean_stock_scout_data.py` for bulk cleanup:

#### Full Cleanup Mode
```bash
python clean_stock_scout_data.py
```
- Deletes ALL Stock Scout missions
- Deletes ALL stock opportunities
- Requires confirmation

#### Selective Cleanup Mode
```bash
python clean_stock_scout_data.py --selective
```
- Only deletes failed/errored missions
- Shows list before deletion
- Safer option

## How to Use

### From the UI
1. Go to Business Hub → Stock Scout History
2. Click the trash icon on any mission to delete it
3. Or click on a mission and use "Delete Mission" button

### From Command Line
```bash
cd backend

# Delete all Stock Scout data
python clean_stock_scout_data.py

# Delete only failed missions
python clean_stock_scout_data.py --selective
```

## Code Changes

### Frontend Changes
1. **StockScoutHistory.tsx**:
   - Added `handleDeleteMission` function
   - Added delete button to mission cards
   - Added delete button to details modal
   - Added Trash2 icon import

2. **agent-orchestra.service.ts**:
   - Added `deleteOrchestration` method

### Backend Changes
- No changes needed - DELETE already supported by ModelViewSet

## Benefits

1. **Clean Slate**: Remove all old/broken missions
2. **Individual Control**: Delete specific missions as needed
3. **Bulk Operations**: Script for mass cleanup
4. **Safe Deletion**: Confirmation prompts prevent accidents

## Next Steps

1. **Clean up existing missions** using the UI or script
2. **Run new Stock Scout missions** with proper data format
3. **Extract opportunities** should now work correctly
4. **Monitor results** in Stock Dashboard

## Why This Approach?

Rather than trying to fix broken data extraction from malformed agent outputs, it's cleaner to:
1. Delete the old missions
2. Ensure new missions generate proper data
3. Have working extraction going forward

This is a pragmatic solution that gets you back to a working state quickly.
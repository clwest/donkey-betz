# Add Extract Opportunities Button to Stock Scout History

## Problem
Stock Scout missions are completing successfully but showing 0 opportunities because:
1. The agents generate text reports, not structured opportunity data
2. Opportunities need to be extracted from the text and saved to the database
3. The UI counts opportunities from the database, not from agent output

## Solution
Add an "Extract Opportunities" button to the Stock Scout History component that:
1. Calls the extraction endpoint when clicked
2. Updates the opportunity count after extraction
3. Shows the extracted opportunities in the UI

## Code Changes Needed

### 1. Add Extract Function to StockScoutHistory.tsx

```typescript
const handleExtractOpportunities = async (missionId: number) => {
  try {
    const result = await agentOrchestraService.extractOpportunitiesFromTask(missionId);
    if (result.success) {
      toast.success(`Extracted ${result.extracted} opportunities!`);
      // Reload missions to update count
      await loadMissions();
      // If viewing details, reload those too
      if (selectedMission?.id === missionId) {
        await loadMissionResults(missionId);
      }
    }
  } catch (error) {
    console.error('Failed to extract opportunities:', error);
    toast.error('Failed to extract opportunities');
  }
};
```

### 2. Add Button to Mission Card

In the mission card, add a button when opportunities_found is 0:

```typescript
{mission.opportunities_found === 0 && mission.status === 'completed' && (
  <button
    onClick={(e) => {
      e.stopPropagation();
      handleExtractOpportunities(mission.id);
    }}
    style={{
      padding: '6px 12px',
      backgroundColor: colors.accent.primary,
      color: colors.background,
      border: 'none',
      borderRadius: '6px',
      fontSize: '12px',
      cursor: 'pointer'
    }}
  >
    Extract Opportunities
  </button>
)}
```

### 3. Auto-Extract on Details View

When viewing mission details, automatically extract if no opportunities:

```typescript
const handleViewDetails = async (mission: StockScoutMission) => {
  setSelectedMission(mission);
  setShowDetails(true);
  await loadMissionResults(mission.id);
  
  // Auto-extract if completed but no opportunities
  if (mission.status === 'completed' && mission.opportunities_found === 0) {
    await handleExtractOpportunities(mission.id);
  }
};
```

## Backend Already Ready
The backend already has the extraction endpoint at:
`POST /api/agent-orchestra/stock-opportunities/extract/<orchestration_id>/`

## Expected Outcome
1. User sees "Extract Opportunities" button on completed missions with 0 opportunities
2. Clicking extracts and saves opportunities to database
3. Opportunity count updates in the UI
4. Extracted opportunities appear in the Stock Dashboard
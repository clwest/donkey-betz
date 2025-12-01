# Session 301: Create Project Button Fix

**Date:** December 1, 2025
**Status:** Complete
**Focus:** Fixed "Create Project" button routing so it uses the correct tool

## Summary

Fixed the "Create Project" button in research reports to correctly trigger the `create_project_from_research` tool instead of being mis-routed to WorkflowAgent.

## Problem

When clicking "Create Project" after running business research:
- **Before:** Message sent was `'Create a project for ${marketName} with all the research we have done'`
- **Issue:** This got routed to **WorkflowAgent** due to keyword matching ("create", "project")
- **WorkflowAgent** doesn't have the `create_project_from_research` tool - it can only delegate to specialized agents
- **Result:** "Workflow completed: 4 successful, 2 failed" with ResearchAgent steps returning empty results

## Root Cause

1. The phrase "Create a project" triggered CREATION type classification in the query classifier
2. The semantic routing matched this to WorkflowAgent based on keywords
3. WorkflowAgent tried to delegate to ResearchAgent multiple times without the ability to create projects
4. The `create_project_from_research` tool exists only on PersonalAssistantEnhanced, not WorkflowAgent

## Fix Applied

Updated the button message in `ai_core/templates/ai_image_studio.html` (2 occurrences at lines 26880 and 27110):

**Before:**
```javascript
'Create a project for ${marketName} with all the research we have done'
```

**After:**
```javascript
'Organize our research into a project for ${marketName}. Use the create_project_from_research tool to save everything.'
```

## Why This Works

1. The phrase "Organize our research" avoids the CREATION type triggers
2. Explicitly mentioning the tool name guides GPT to call the right tool
3. The `create_project_from_research` tool is available on PersonalAssistantEnhanced
4. The request stays with the primary assistant rather than being routed away

## Files Modified

- `ai_core/templates/ai_image_studio.html`:
  - Line 26880: Updated Create Project button message
  - Line 27110: Updated Create Project button message (duplicate in different section)

## Testing

1. Run competitor/customer research: "Analyze competitors for AI content generation apps"
2. Click "Create Project" button in the research report
3. Verify the message contains "Organize our research" and "create_project_from_research"
4. Confirm project is created successfully without WorkflowAgent errors

## Related Sessions

- **Session 300:** Fixed context chaining between research agents (duplicate formatAnalysisReport function)
- **Session 299:** Implemented Cumulative Intelligence Pipeline with research persistence
- **Session 293:** Added CompetitorAnalysisAgent and CustomerResearchAgent

## Architecture Note

The routing architecture has multiple layers:
1. **PersonalAssistantEnhanced** - Has direct access to all tools including `create_project_from_research`
2. **PersonalAssistantAgent (clean)** - Routes to specialized agents via AgentRouter
3. **WorkflowAgent** - Orchestrates multi-step workflows but can only delegate

Project creation must stay at the PersonalAssistantEnhanced level where the tool exists, not be delegated to WorkflowAgent which lacks this capability.

# Session 189: AI Assistant UI Overhaul + Strategic Review Workflow

**Date:** November 25, 2025
**Status:** IN PROGRESS - Workflow ordering needs fine-tuning

---

## What Was Accomplished

### 1. AI Assistant Tab (COMPLETE - from earlier in session)
- Moved AI Assistant from sidebar to dedicated tab
- Full-width chat interface
- Voice input with auto-send
- Style preferences panel
- Project context display

### 2. Over-Generation Fix (PARTIALLY WORKING)
- Added cumulative tracking across workflow iterations
- Images now count correctly: `total_generated` from backend
- Continuation messages include "🛑 IMAGE GENERATION COMPLETE" blocks
- Added instructions #14-18 to system prompt

### 3. Strategic Review Feature (NEW - needs ordering fix)
Created new `strategic_review` tool for executive team review:
- **Tool Definition:** `core/assistant/tool_definitions.py` - `_get_strategic_review_definition()`
- **Handler:** `core/views_image.py` - `_execute_strategic_review()`
- **Frontend Display:** `ai_image_studio.html` - in `formatToolResults()`
- Uses `MeetingCoordinatorAgent` to hold boardroom meeting with CTO, COO, Creative Director

---

## Current Issue: Workflow Order

**Expected workflow:**
1. `web_search` → Research the topic
2. `strategic_review` OR `coleadership_agent` → Executive team reviews research
3. `image_generation_agent` → Create images using their direction
4. `create_project_from_research` → Organize into project

**What's happening:**
- GPT is calling `image_generation_agent` FIRST (before executive review)
- Then calling `coleadership_agent` AFTER images are created
- The workflow is backwards!

**Root cause:**
GPT-5.1 is not following the workflow order in instruction #18. It sees "create logos" and immediately calls image_generation_agent without waiting for strategic review.

---

## Files Modified This Session

### Backend:
1. **`core/assistant/tool_definitions.py`**
   - Added `_get_strategic_review_definition()` function (lines 541-582)
   - Added to `get_tool_definitions()` list

2. **`core/views_image.py`**
   - Added handler for `strategic_review` tool (line 7061)
   - Added `_execute_strategic_review()` function (lines 12979-13111)

3. **`core/personal_ai_assistant_enhanced.py`**
   - Added instruction #16: NEVER REPEAT COMPLETED WORK (enhanced)
   - Added instruction #17: PROJECT CREATION AFTER RESEARCH
   - Added instruction #18: RESEARCH → STRATEGIC REVIEW → CREATE WORKFLOW
   - Added example showing correct 4-step sequence

### Frontend (`ai_core/templates/ai_image_studio.html`):
1. **Cumulative Stats Tracking** (lines 16698-16708):
   ```javascript
   let cumulativeStats = {
       imagesGenerated: 0,
       videosGenerated: 0,
       searchesCompleted: 0,
       strategicReviewCompleted: false,
       imageIds: [],
       allToolsExecuted: [],
       strategicDirection: null
   };
   ```

2. **Stats Update Logic** (lines 16744-16770):
   - Tracks `image_generation_agent` results with `total_generated`
   - Tracks `web_search` completion
   - Tracks BOTH `strategic_review` AND `coleadership_agent` as executive review

3. **Completion Blocks** (lines 16783-16799):
   - "🛑 IMAGE GENERATION COMPLETE"
   - "🛑 VIDEO GENERATION COMPLETE"
   - "🛑 STRATEGIC/EXECUTIVE REVIEW COMPLETE"

4. **Next Step Suggestions** (lines 16805-16823):
   - Guides GPT through workflow stages
   - Suggests `image_generation_agent` after review complete

5. **formatToolResults Handler** (lines 18566-18625):
   - Beautiful display of strategic review output
   - Shows executive summary, participants, recommendations

6. **Status Message** (line 17815):
   - "🏢 Executive team reviewing research..."

7. **MAX_ITERATIONS** (line 16696):
   - Set to 4 for full workflow

---

## Next Steps for Session 190

### Priority 1: Fix Workflow Order
The core issue is GPT calling `image_generation_agent` before `strategic_review`. Options:

**Option A: Stronger System Prompt**
Add explicit instruction: "When user asks to RESEARCH and CREATE, you MUST call web_search FIRST, then strategic_review SECOND, then image_generation_agent THIRD. Do not skip steps."

**Option B: Frontend Enforcement**
In the continuation message after `web_search` completes with no images, explicitly say:
"STOP! Before generating images, you MUST call strategic_review or coleadership_agent to get executive direction."

**Option C: Two-Phase Workflow**
Split into two phases:
1. Phase 1: Research + Review (block image_generation_agent until review done)
2. Phase 2: Create content

### Priority 2: Test Complete Flow
Once ordering is fixed, test the full flow:
1. "Research AI logos and create 3 modern logos"
2. Should see: search → review → images → project

### Priority 3: Verify No Over-Generation
Ensure only 3 images are created (not 5+)

---

## Key Code Locations

### Tool Definition
```
core/assistant/tool_definitions.py:541-582 - _get_strategic_review_definition()
```

### Tool Handler
```
core/views_image.py:12979-13111 - _execute_strategic_review()
```

### Cumulative Tracking
```
ai_core/templates/ai_image_studio.html:16698-16823 - cumulativeStats and continuation messages
```

### System Prompt Instructions
```
core/personal_ai_assistant_enhanced.py:4764-4778 - Instructions 16-18
```

---

## Testing Commands

Test the research → review → create workflow:
```
"Research modern AI company logo trends and create 3 professional logos"
```

Expected console output:
```
🔄 Autonomous workflow iteration 1/4
📡 Tool: web_search
📊 Cumulative stats: {searchesCompleted: 1, strategicReviewCompleted: false, imagesGenerated: 0}

🔄 Autonomous workflow iteration 2/4
📡 Tool: strategic_review OR coleadership_agent
📊 Cumulative stats: {searchesCompleted: 1, strategicReviewCompleted: true, imagesGenerated: 0}
🏢 Strategic/Executive review completed

🔄 Autonomous workflow iteration 3/4
📡 Tool: image_generation_agent (count=3)
📊 Cumulative stats: {searchesCompleted: 1, strategicReviewCompleted: true, imagesGenerated: 3}
🎨 Image generation: 3 images created

🔄 Autonomous workflow iteration 4/4
📡 Tool: create_project_from_research
✅ Project created
```

---

## Architecture Notes

### Strategic Review Flow
```
User Request
    ↓
GPT-5.1 decides on tools
    ↓
web_search (Serper API)
    ↓
strategic_review/coleadership_agent
    ↓
MeetingCoordinatorAgent.start_meeting()
    ↓
[CTO, COO, Creative Director perspectives]
    ↓
GPT-5.1 synthesis
    ↓
Strategic direction with prompt suggestions
    ↓
image_generation_agent (using suggestions)
    ↓
create_project_from_research
```

### Cumulative Stats Purpose
Tracks work across ALL iterations to:
1. Prevent duplicate tool calls (don't generate more images if already done)
2. Guide workflow progression (suggest next step based on what's complete)
3. Collect image IDs for project creation

---

## Quick Reference

| Component | Location |
|-----------|----------|
| Tool definition | `core/assistant/tool_definitions.py:541` |
| Tool handler | `core/views_image.py:12979` |
| Route registration | `core/views_image.py:7061` |
| Frontend display | `ai_image_studio.html:18566` |
| Status message | `ai_image_studio.html:17815` |
| Cumulative tracking | `ai_image_studio.html:16698` |
| System prompt | `personal_ai_assistant_enhanced.py:4764` |
| MAX_ITERATIONS | `ai_image_studio.html:16696` (set to 4) |

---

**Ready for Session 190: Fix workflow ordering so executive review happens BEFORE image generation!**

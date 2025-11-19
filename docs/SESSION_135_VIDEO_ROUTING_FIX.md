# Session 135 Follow-up: Video Display Routing Fix

**Date:** November 19, 2025
**Status:** COMPLETE
**Impact:** Videos created in project assistant now display correctly in project chat

---

## Problem

User reported: "when I use the Assistant in the Project and say 'Animate Image #' After the video is created it's showing up in the original Assistant Modal and not in the Project Assistant like it should be"

**Root Cause:** The `pollVideoStatus` function didn't know which assistant initiated the video request, so it always routed completed videos to `window.aiAssistant` (main modal) instead of the project assistant chat.

---

## Solution

Added `projectId` parameter to video polling flow to enable proper routing:

### Edit 1: Function Signature (Line 11870)
```javascript
// BEFORE:
async function pollVideoStatus(taskId, mode) {

// AFTER:
async function pollVideoStatus(taskId, mode, projectId = null) {
```

### Edit 2: Completion Handler (Lines 11913-11952)
```javascript
// Session 135: Check if this is project assistant or main modal
if (projectId) {
    // Project assistant - add to project chat
    console.log(`📌 Adding video to project chat: ${projectId}`);
    if (typeof addProjectChatMessage === 'function') {
        addProjectChatMessage(projectId, 'assistant', completionMessage);
        // Also refresh project assets to show the new video
        setTimeout(() => refreshProjectAssets(projectId), 1000);
    }
} else if (window.aiAssistant) {
    // Main modal assistant - add to modal chat
    console.log(`📌 Adding video to main modal assistant`);
    window.aiAssistant.addMessage('assistant', completionMessage);
}
```

### Edit 3: Project Assistant Call (Line 20849)
```javascript
// BEFORE:
setTimeout(() => window.pollVideoStatus(task_id, 'assistant'), 100);

// AFTER:
setTimeout(() => window.pollVideoStatus(task_id, 'assistant', projectId), 100);
```

---

## Data Flow After Fix

```
User in Project Assistant: "Animate Image 25"
    ↓
Project chat handler (line 20849)
    ↓
Calls: pollVideoStatus(task_id, 'assistant', projectId)
    ↓
Video completes → completion handler (line 11913)
    ↓
Checks: if (projectId) → TRUE!
    ↓
Calls: addProjectChatMessage(projectId, 'assistant', completionMessage)
    ↓
Video displays in PROJECT CHAT (correct!) ✅
```

---

## Files Modified

- **ai_core/templates/ai_image_studio.html**
  - Line 11870: Function signature
  - Lines 11913-11952: Completion handler routing logic
  - Line 20849: Project assistant call site

**Total Changes:** 3 edits, ~15 lines modified

---

## Testing Checklist

- [ ] Create video through project assistant → appears in project chat
- [ ] Create video through main modal → appears in main modal
- [ ] Video also appears in project assets gallery
- [ ] No regression in existing video functionality

---

## Related Documentation

- [Session 135: Project Association Fix](SESSION_135_PROJECT_ASSOCIATION_FIX.md)
- [Session 122: Critical Bug Fixes](SESSION_122_BUG_HUNT_COMPLETE.md)

---

**Session 135 Follow-up Status: COMPLETE!**

Videos now display in the correct assistant interface!

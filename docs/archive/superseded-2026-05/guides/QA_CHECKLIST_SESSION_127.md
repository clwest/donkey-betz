# 🔍 QA CHECKLIST - Session 127 Part 3 (Post-GPT-5-mini Upgrade)

**Date:** November 18, 2025
**Tester:** Manual QA with fresh browser session
**Scope:** Complete platform verification after GPT-5-mini upgrade + bug hunting

---

## 🎯 CRITICAL ISSUES TO VERIFY

### Issue #1: 3D Models Showing UUIDs Instead of Sequential Numbers ❌

**Expected Behavior:**
- 3D Model cards should show "3D Model #1", "3D Model #2", etc.
- Sequential numbering should match chronological creation order

**Current Behavior:**
- Cards showing "3D Model #UUID" with full UUID string

**Code Changes Made:**
- ✅ Added `get_sequential_number()` method to MiniFigAsset model (`content/models.py`:2246-2261)
- ✅ Updated portfolio API to include `sequential_number` (`core/views_image.py`:10101)
- ✅ Frontend should use `asset.sequential_number`

**Verification Steps:**
1. Open fresh browser session (clear cache: Cmd+Shift+R)
2. Navigate to Projects tab
3. Open "Ai Content Generation Company" project
4. Scroll to "🎨 3D Models" section
5. Verify each card shows "3D Model #1", "#2", etc.

**Expected Result:** ✅ "3D Model #1", "3D Model #2", etc.
**Pass/Fail:** ⏸️ NEEDS TESTING

---

### Issue #2: Text Removal Tool Logic Flaw 🚨 CRITICAL

**The Fundamental Problem:**
User reported: "AI says text has been removed from image #2, but text is still there"

**The Critical Insight (User's Discovery):**
> **Even if text removal worked, it would create a NEW image!**
> Original image #2 would still exist with text.
> The AI claiming "text has been removed from image #2" makes no logical sense.

**Expected Behavior (Correct):**
```
User: "Remove text from image #2"
AI: ✨ Removing text...
Result: Creates NEW image #23 without text
        Original image #2 still exists WITH text
AI Response: "I've created image #23 without text based on image #2"
```

**Current Behavior (WRONG):**
```
User: "Remove text from image #2"
AI: "The text has already been removed from image #2"
Result: No new image created
        Original image #2 unchanged
        Claim of success is FALSE
```

**Root Cause Analysis:**
1. **Conversation History Pollution?**
   - ✅ FIXED: Redis cleared completely
   - Test with fresh conversation

2. **Image ID Resolution Bug?**
   - User says "image #2"
   - AI might be mapping to wrong UUID
   - Need to verify which UUID "image #2" resolves to

3. **Tool Execution Bug?**
   - Tool might be failing silently
   - No new image created
   - But AI claims success anyway

4. **Response Parsing Bug?**
   - Tool executes correctly (creates new image)
   - But AI doesn't recognize the new image
   - Gives wrong response about original image

**Verification Steps:**
1. **BEFORE TEST:**
   - Clear browser cache (Cmd+Shift+R)
   - Verify Redis is cleared: `redis-cli KEYS "*"`
   - Check current image count: Query ImageHistory table
   - Verify image #2 UUID in database

2. **TEST 1: Simple Text Removal**
   ```
   User: "Remove text from image #2"
   ```
   - Monitor backend logs for tool execution
   - Check if new ImageHistory record is created
   - Verify new image file exists on disk
   - Check AI's response message
   - Count total images BEFORE and AFTER

3. **TEST 2: Verify Image #2 Still Exists**
   - After test 1, refresh project view
   - Verify image #2 is still in the list
   - Verify image #2 still has text
   - Verify new image was created (should be last in list)

4. **TEST 3: Image ID Resolution**
   - Ask AI: "What is the UUID of image #2?"
   - Compare with actual UUID in database
   - Verify hybrid ID resolution is working

**Expected Results:**
- ✅ New image created (image #23 or similar)
- ✅ Original image #2 still exists with text
- ✅ AI says "Created new image #23 without text"
- ✅ Image count increased by 1

**Pass/Fail:** ⏸️ NEEDS TESTING

---

### Issue #3: GPT-5-mini Model Verification

**Purpose:** Verify that OpenAI API is actually using GPT-5-mini (not falling back to another model)

**Verification Steps:**
1. Check backend logs during assistant request:
   ```bash
   grep -A 10 "OpenAI" logs/*.log | grep "model"
   ```

2. Check for API errors:
   ```bash
   grep -i "error\|invalid" logs/*.log | grep -i "model\|gpt"
   ```

3. Verify cost calculation is using GPT-5-mini pricing ($0.50/1M input + $1.50/1M output)

4. Test a simple request and check response metadata

**Expected Results:**
- ✅ Model name in logs shows "gpt-5-mini"
- ✅ No API errors about invalid model
- ✅ Costs calculated correctly

**Pass/Fail:** ⏸️ NEEDS TESTING

---

## 📋 COMPREHENSIVE PROJECT AUDIT

### A. Project Assets View

**Test Location:** Projects tab → "Ai Content Generation Company"

#### A1. Image Section (📸 Images)
- [ ] All images displayed with thumbnails
- [ ] Sequential numbers correct (#1, #2, #3...)
- [ ] Click on image opens full view
- [ ] Download button works
- [ ] Favorite button toggles (⭐/☆)
- [ ] Delete button works (with confirmation)
- [ ] Copy ID button copies correct UUID

#### A2. Video Section (🎬 Videos)
- [ ] All videos displayed with thumbnails
- [ ] Sequential numbers correct (#1, #2, #3...)
- [ ] Click on video plays video
- [ ] Download button works
- [ ] Favorite button toggles (⭐/☆)
- [ ] Delete button works (with confirmation)
- [ ] Copy ID button copies correct UUID
- [ ] Video player controls work (play, pause, volume)

#### A3. 3D Models Section (🎨 3D Models)
- [ ] All 3D models displayed
- [ ] **Sequential numbers correct (#1, #2, #3...)** ⚠️ KNOWN ISSUE
- [ ] Click on model opens .glb file in new window
- [ ] Model preview image loads
- [ ] Download button works
- [ ] Favorite button toggles (⭐/☆)
- [ ] Delete button works (with confirmation)
- [ ] Copy ID button copies correct UUID

---

### B. Embedded AI Assistant

**Test Location:** Projects tab → Click "💬 Open AI Assistant"

#### B1. Basic Functionality
- [ ] Voice input button works (🎤)
- [ ] Text input works
- [ ] Whisper transcription accurate
- [ ] Responses appear in chat
- [ ] Chat history persists during session
- [ ] Chat history clears on browser refresh

#### B2. Image Tool Execution
Test each tool with FRESH BROWSER SESSION:

**Tool 1: Upscale Image**
```
Command: "Upscale image #5"
Expected: New image created at 4x resolution
Verify:
  - [ ] New image appears in project (after polling completes)
  - [ ] Original image #5 still exists
  - [ ] New image has higher resolution
  - [ ] AI response mentions new image number
```

**Tool 2: Remove Background**
```
Command: "Remove background from image #7"
Expected: New image with transparent background
Verify:
  - [ ] New image appears in project
  - [ ] Original image #7 still exists
  - [ ] New image has transparent background (PNG)
  - [ ] AI response mentions new image number
```

**Tool 3: Create Variations**
```
Command: "Create 3 variations of image #3"
Expected: 3 new images created
Verify:
  - [ ] 3 new images appear in project
  - [ ] Original image #3 still exists
  - [ ] Variations are different from original
  - [ ] AI response mentions all 3 new image numbers
```

**Tool 4: Erase Object (TEXT REMOVAL)**
```
Command: "Remove text from image #2"
Expected: New image without text
Verify:
  - [ ] **NEW image created** ⚠️ CRITICAL
  - [ ] **Original image #2 STILL EXISTS** ⚠️ CRITICAL
  - [ ] **Original image #2 STILL HAS TEXT** ⚠️ CRITICAL
  - [ ] New image has no text
  - [ ] AI says "Created new image #X without text" (NOT "removed text from #2")
  - [ ] Total image count increased by 1
```

**Tool 5: Recolor Image**
```
Command: "Make image #4 blue"
Expected: New image with blue color
Verify:
  - [ ] New image appears in project
  - [ ] Original image #4 still exists
  - [ ] New image has blue tint
  - [ ] AI response mentions new image number
```

**Tool 6: Refine Image**
```
Command: "Make image #8 more dramatic"
Expected: New image with modifications
Verify:
  - [ ] New image appears in project
  - [ ] Original image #8 still exists
  - [ ] AI response mentions new image number
```

#### B3. Video Tool Execution

**Tool 1: Add Text Overlay**
```
Command: "Add text 'Amazing!' to video #1 at 2 seconds for 4 seconds"
Expected: Video processed with text overlay
Verify:
  - [ ] Tool executes successfully
  - [ ] DaVinci Resolve processes video
  - [ ] Text appears at correct timestamp
  - [ ] Text duration is correct (4 seconds)
```

**Tool 2: Apply Color Grading**
```
Command: "Make video #2 look cinematic"
Expected: Video with color grading applied
Verify:
  - [ ] Tool executes successfully
  - [ ] Color grading preset applied
  - [ ] Video looks different from original
```

#### B4. 3D Tool Execution

**Tool: Convert Image to 3D**
```
Command: "Make image #10 a 3D model"
Expected: New 3D model created
Verify:
  - [ ] Tool executes (or reports Replicate service unavailable)
  - [ ] If successful: New 3D model appears in project
  - [ ] Original image #10 still exists
```

---

### C. Image ID Resolution Testing

**Purpose:** Verify hybrid ID system works correctly

**Test 1: Ask AI About Image IDs**
```
Command: "What is the UUID of image #2?"
Expected: AI should be able to tell you the UUID
Verify:
  - [ ] AI provides UUID
  - [ ] UUID matches database record for 2nd oldest image
```

**Test 2: Use Different ID Formats**
```
Test A: "Remove text from image 2" (no hashtag)
Test B: "Remove text from image #2" (with hashtag)
Test C: "Remove text from image number 2" (explicit)
Expected: All should work the same
Verify:
  - [ ] All 3 formats recognized
  - [ ] All 3 resolve to same UUID
```

**Test 3: Database Verification**
```python
# Run in Django shell
from content.models import ImageHistory
from django.contrib.auth.models import User

user = User.objects.get(username='admin')
images = ImageHistory.objects.filter(user=user).order_by('created_at')

# Image #2 should be the 2nd oldest
image_2 = images[1]  # 0-indexed, so [1] is #2
print(f"Image #2 UUID: {image_2.id}")
print(f"Image #2 has sequential number: {image_2.get_sequential_number()}")
```

---

### D. Database Integrity Checks

**Run Before Testing:**
```python
# Django shell
from content.models import ImageHistory, VideoHistory, MiniFigAsset
from django.contrib.auth.models import User

user = User.objects.get(username='admin')

# Count assets
images = ImageHistory.objects.filter(user=user).count()
videos = VideoHistory.objects.filter(user=user).count()
models_3d = MiniFigAsset.objects.filter(user=user).count()

print(f"Images: {images}")
print(f"Videos: {videos}")
print(f"3D Models: {models_3d}")

# Check for orphaned assets (no project)
orphaned_images = ImageHistory.objects.filter(user=user, sessions__isnull=True).count()
orphaned_videos = VideoHistory.objects.filter(user=user, sessions__isnull=True).count()
orphaned_3d = MiniFigAsset.objects.filter(user=user, project__isnull=True).count()

print(f"Orphaned Images: {orphaned_images}")
print(f"Orphaned Videos: {orphaned_videos}")
print(f"Orphaned 3D Models: {orphaned_3d}")
```

**Run After Each Tool Test:**
- Verify asset count increased by expected amount
- Verify all new assets are linked to project
- Verify original assets still exist

---

## 🎯 SUCCESS CRITERIA

### Must Pass:
1. ✅ 3D models show sequential numbers (not UUIDs)
2. ✅ Text removal creates NEW image (original unchanged)
3. ✅ GPT-5-mini model is being used (no fallback)
4. ✅ All tool executions create new assets (don't modify originals)
5. ✅ AI responses accurately describe what happened

### Should Pass:
1. ✅ All favorites buttons work
2. ✅ All download buttons work
3. ✅ All delete buttons work
4. ✅ Video playback works
5. ✅ 3D model viewing works

### Nice to Have:
1. ✅ Voice commands work perfectly
2. ✅ Chat history persists correctly
3. ✅ Progress indicators show during processing
4. ✅ Error messages are helpful

---

## 📝 TESTING NOTES

### Pre-Test Setup:
```bash
# 1. Clear Redis
redis-cli FLUSHALL

# 2. Clear browser cache
# Cmd+Shift+R (or Ctrl+Shift+R on Windows)

# 3. Verify server is running
lsof -i :8000

# 4. Check logs are accessible
tail -f logs/*.log
```

### During Testing:
- Record exact commands used
- Screenshot any errors
- Note exact AI responses
- Monitor backend logs
- Check database after each test

### Post-Test:
- Document all failures
- Note any unexpected behavior
- Suggest fixes for issues found
- Update Reality Score if needed

---

## 🚨 KNOWN ISSUES TO VERIFY

1. **3D Model UUIDs** - Code fixed, needs verification
2. **Text Removal Logic** - Fundamental flaw, needs fix
3. **GPT-5-mini** - Model change made, needs verification
4. **Image ID Resolution** - Might be mapping wrong UUIDs

---

## 📊 RESULTS SUMMARY

**Test Date:** _____________________
**Tester:** _____________________
**Browser:** _____________________
**Reality Score Before:** 99.5%
**Reality Score After:** _____________________

### Critical Issues:
- [ ] 3D models sequential numbering
- [ ] Text removal tool logic
- [ ] GPT-5-mini model usage

### Passed: _____ / 50 tests
### Failed: _____ / 50 tests
### Blocked: _____ / 50 tests

---

**Ready to start systematic QA! 🔍**

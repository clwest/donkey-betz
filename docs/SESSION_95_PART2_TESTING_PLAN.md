# Session 95 Part 2: Agent Workflow Testing Plan

**Date:** November 14, 2025
**Status:** READY TO BEGIN
**Prerequisites:** ✅ ALL COMPLETE
**Estimated Time:** 2-3 hours

---

## ✅ Pre-Test Verification (COMPLETE)

**System Health:**
- ✅ Redis: Running (PID 85407)
- ✅ Daphne: Running (PID 99974)
- ✅ Health endpoint: UP

**Agent Status:**
- ✅ Active Agents: 10/10
  1. AudioAgent
  2. BrandStyleAgent
  3. CreativeDirectorAgent
  4. EditingOrchestratorAgent
  5. IterationAgent
  6. ReferenceLibraryAgent
  7. TemplateManagerAgent
  8. VersionControlAgent
  9. VideoAgent
  10. WorkflowCoordinatorAgent

**Test Suite Results:**
- ✅ Database Registration: PASS
- ✅ Agent Initialization: PASS
- ✅ Workflow Orchestration: PASS (7/7 sub-agents)
- ✅ Inter-Agent Communication: PASS
- ✅ AI Assistant Integration: PASS (8/8 tools)
- **Overall: 5/5 tests PASS (100%)**

**API Credentials:**
- ✅ OpenAI: Configured
- ✅ Runway ML: Configured (~900 credits)
- ✅ Stability AI: Configured (6,990 credits)
- ✅ ElevenLabs: Configured

**Critical Feature:**
- ✅ Copy ID Button: WORKING (Session 95 Part 1)

---

## 🎯 Testing Strategy

### Philosophy
Test workflows in order of complexity, building on previous successes:
1. Start simple: Multi-option generation (no image ID needed)
2. Add references: Save as template (requires Copy ID)
3. Add editing: Refine image (requires Copy ID + natural language)
4. Add training: Brand style (requires multiple IDs)
5. Finish complex: Inter-agent communication (VideoAgent ↔ AudioAgent)

### Success Criteria
**Must Pass (3/5 minimum):**
- Test 1: Multi-option generation
- Test 2: Save as template
- Test 3: Refine image

**Bonus (2/5):**
- Test 4: Brand training
- Test 5: Inter-agent communication

---

## 📋 TEST 1: Multi-Option Generation

**Agent:** CreativeDirectorAgent
**Time:** 20 minutes
**Complexity:** ⭐ Simple (no prerequisites)

### Objective
Verify CreativeDirectorAgent can generate 3 diverse image options with different styles.

### Prerequisites
- None! This is the warmup test

### Voice Command
```
"Generate three coffee shop logos"
```

### Expected Behavior
1. GPT-5 calls `generate_with_options` function
2. WorkflowCoordinatorAgent routes to CreativeDirectorAgent
3. CreativeDirectorAgent generates 3 variations
4. Each image has DIFFERENT style (diversity enforcement)
5. All 3 appear in Image Gallery with:
   - Style badges (golden gradient)
   - Seed numbers
   - Copy ID buttons
   - "⭐ Pick This One!" buttons

### What to Verify
- [ ] AI Assistant responds with generation confirmation
- [ ] 3 images appear in Image Gallery
- [ ] Each has different style (check badges):
  - Example: Impressionist, Graffiti Art, Vector Illustration
- [ ] Each has Copy ID button
- [ ] Each has visible style badge + seed number
- [ ] Can click Copy ID on each image
- [ ] Can select favorite with "⭐ Pick This One!" button

### Test Data to Record
```
Image 1 ID: _______________
Image 1 Style: _______________
Image 2 ID: _______________
Image 2 Style: _______________
Image 3 ID: _______________
Image 3 Style: _______________
```

### Success Criteria
✅ Pass: All 3 images generated with different styles, Copy ID works

### If It Fails
1. Check console for errors
2. Verify CreativeDirectorAgent in database: `python manage.py shell -c "from agents.models import UnifiedAgentTemplate; print(UnifiedAgentTemplate.objects.filter(name='CreativeDirectorAgent').exists())"`
3. Check AI Assistant tool routing in logs
4. Try text input instead of voice

---

## 📋 TEST 2: Save as Template

**Agent:** TemplateManagerAgent
**Time:** 30 minutes
**Complexity:** ⭐⭐ Medium (requires Copy ID from Test 1)

### Objective
Verify TemplateManagerAgent can save an image with all parameters for recreation.

### Prerequisites
- ✅ Test 1 complete (have image ID)
- ✅ Copy ID button working

### Voice Commands
```
1. "Save image [ID from Test 1] as Coffee Shop Logo template"
2. "Use Coffee Shop Logo template"
3. "Create variation of Coffee Shop Logo template"
```

### Expected Behavior
**Save Command:**
1. GPT-5 extracts image ID from natural language
2. Calls `save_as_template` function with ID + name
3. WorkflowCoordinatorAgent routes to TemplateManagerAgent
4. TemplateManagerAgent:
   - Looks up image in database
   - Extracts seed, model, style, prompt, dimensions
   - Stores in Redis with key: `template:user:[user_id]:Coffee Shop Logo`
5. Returns confirmation with template details

**Use Command:**
1. GPT-5 calls function with template name
2. TemplateManagerAgent retrieves from Redis
3. Uses EXACT seed for recreation
4. Returns new image that looks nearly identical

**Variation Command:**
1. Same as Use but with seed variation
2. Uses base parameters but different seed
3. Returns similar but different image

### What to Verify
**Save:**
- [ ] AI Assistant confirms template saved
- [ ] Shows saved parameters (seed, style, model)
- [ ] No errors in console

**Use:**
- [ ] New image generated
- [ ] Looks very similar to original
- [ ] Same style visible in gallery
- [ ] AI Assistant confirms recreation

**Variation:**
- [ ] New image generated
- [ ] Similar style/concept but visually different
- [ ] Different seed number
- [ ] AI Assistant confirms variation

### Test Data to Record
```
Original Image ID: _______________
Template Name: Coffee Shop Logo
Saved Seed: _______________
Saved Style: _______________
Recreated Image ID: _______________
Variation Image ID: _______________
```

### Success Criteria
✅ Pass: Template saves, recreates, and variations work

### Troubleshooting
**"Template not found":**
- Check Redis: `redis-cli GET "template:user:[user_id]:Coffee Shop Logo"`
- Verify user ID matches in agent memory

**Recreation looks completely different:**
- Verify seed was saved: Check AI Assistant response
- Check if same model used (Core/SDXL/SD3)

---

## 📋 TEST 3: Refine Image

**Agent:** IterationAgent + EditingOrchestratorAgent
**Time:** 30 minutes
**Complexity:** ⭐⭐⭐ Medium-High (requires natural language parsing)

### Objective
Verify IterationAgent can parse natural language editing requests and apply changes.

### Prerequisites
- ✅ Test 1 or 2 complete (have image ID)

### Voice Commands
Try progressively complex edits:
```
1. "Make image [ID] bigger"
2. "Make image [ID] darker and add more contrast"
3. "Change image [ID] to blue tones"
```

### Expected Behavior
1. GPT-5 extracts image ID + edit instructions
2. Calls `refine_image` function
3. IterationAgent receives request:
   - Parses natural language
   - Identifies editing operations needed
   - Routes to EditingOrchestratorAgent
4. EditingOrchestratorAgent:
   - Determines appropriate Stability AI endpoint
   - Applies transformations
   - Returns new image
5. VersionControlAgent tracks lineage (future feature)

### What to Verify
**Simple Edit ("bigger"):**
- [ ] AI Assistant confirms edit request
- [ ] New image appears in gallery
- [ ] Noticeably different size/dimensions
- [ ] Same concept/style maintained

**Complex Edit ("darker + contrast"):**
- [ ] AI Assistant understands multiple instructions
- [ ] New image shows both changes
- [ ] Overall concept preserved

**Color Edit ("blue tones"):**
- [ ] New image has blue color shift
- [ ] Structure/composition maintained
- [ ] Recognizable as variation of original

### Test Data to Record
```
Original Image ID: _______________
Edit Request: "Make image [ID] bigger"
Result Image ID: _______________
Visible Change: Yes / No / Partial

Edit Request: "darker and add more contrast"
Result Image ID: _______________
Visible Change: Yes / No / Partial

Edit Request: "blue tones"
Result Image ID: _______________
Visible Change: Yes / No / Partial
```

### Success Criteria
✅ Pass: At least 2/3 edits produce expected results

### Known Limitations
- Image-to-image editing is probabilistic
- Results may not always match expectations
- This tests the WORKFLOW, not perfect editing

### If It Fails
- Check if IterationAgent received request (console logs)
- Verify EditingOrchestratorAgent routing
- Try simpler edit requests
- Check Stability AI API limits

---

## 📋 TEST 4: Brand Style Training

**Agent:** BrandStyleAgent
**Time:** 45 minutes (15 min setup + 30 min training)
**Complexity:** ⭐⭐⭐⭐ High (requires Replicate, time, credits)

### Objective
Verify BrandStyleAgent can train a FLUX LoRA model on user images.

### Prerequisites
- ✅ Have 5+ images in gallery
- ✅ Copy IDs from 5 images
- ⚠️ Replicate credits available (~$0.10 per training)

### Voice Command
```
"Train brand style on images [ID1], [ID2], [ID3], [ID4], [ID5]"
```

### Expected Behavior
1. GPT-5 extracts 5 image IDs
2. Calls `train_brand_style` function
3. WorkflowCoordinatorAgent routes to BrandStyleAgent
4. BrandStyleAgent:
   - Creates CharacterModel database record
   - Downloads all 5 images from URLs
   - Validates images (format, size)
   - Creates ZIP file
   - Uploads to Replicate
   - Submits FLUX LoRA training job
5. Returns:
   - Training ID
   - Trigger word (e.g., "TOK")
   - Estimated completion time (~30 minutes)

### What to Verify
**Immediate (0-5 min):**
- [ ] AI Assistant confirms training started
- [ ] Shows training ID
- [ ] Shows trigger word
- [ ] Shows estimated time
- [ ] No errors in console

**After Training (30+ min):**
- [ ] Check training status:
   ```bash
   python manage.py shell -c "from content.models import CharacterModel; model = CharacterModel.objects.latest('created_at'); print(f'Status: {model.training_status}')"
   ```
- [ ] Try generating with trigger word:
   ```
   "Generate an image with TOK style robot"
   ```

### Test Data to Record
```
Image 1 ID: _______________
Image 2 ID: _______________
Image 3 ID: _______________
Image 4 ID: _______________
Image 5 ID: _______________
Training ID: _______________
Trigger Word: _______________
Start Time: _______________
Estimated Completion: _______________
```

### Success Criteria
✅ Pass: Training successfully submitted to Replicate
🎯 Bonus: Training completes and trigger word works

### If It Fails
**"Image download failed":**
- Check image URLs are accessible
- Verify images in gallery have valid file_path

**"Replicate API error":**
- Check Replicate API key in .env
- Verify Replicate account has credits
- Check rate limits

**Training Never Completes:**
- Normal! Can take 30-60 minutes
- Not a failure - just note and continue

---

## 📋 TEST 5: Inter-Agent Communication

**Agents:** VideoAgent + AudioAgent
**Time:** 30 minutes
**Complexity:** ⭐⭐⭐⭐⭐ Very High (requires video + audio + ffmpeg)

### Objective
Verify VideoAgent can autonomously query AudioAgent for audio without user intervention.

### Prerequisites
- ✅ Have at least 1 video in Video Gallery
- ⚠️ Generate audio first (needed for mixing)

### Setup Steps
**1. Generate Audio (5 min):**
```
Voice: "Generate speech: Welcome to the future of AI"
```
- Verify audio appears in Audio Gallery
- Note audio file path/ID

**2. Generate Video (if needed) (10 min):**
```
Voice: "Generate a video of ocean waves"
```
- Wait for video completion
- Verify video in Video Gallery

**3. Test Inter-Agent Communication (5 min):**
```
Voice: "Add music to my last video"
```

### Expected Behavior
1. GPT-5 calls `add_music_to_video` function
2. VideoAgent receives request:
   - Identifies "last video" (most recent)
   - **CRITICAL:** Autonomously queries AudioAgent via Agent Query Protocol
   - No user interaction needed!
3. AudioAgent receives query:
   - Returns most recent audio file path
   - Responds through Redis
4. VideoAgent receives response:
   - Downloads video (if CDN URL)
   - Downloads audio file
   - Calls ffmpeg to mix audio into video
   - Uploads new video
   - Creates VideoHistory record
5. Returns confirmation with new video URL

### What to Verify
**Agent Communication:**
- [ ] Check logs for "Agent query sent"
- [ ] Check logs for "Agent query response received"
- [ ] No errors about "no audio found"
- [ ] ffmpeg command executes (console logs)

**Result:**
- [ ] New video appears in Video Gallery
- [ ] Video has audio when played
- [ ] Original video still exists (not replaced)
- [ ] AI Assistant confirms success

### Test Data to Record
```
Audio Generated: _______________
Audio File Path: _______________
Original Video ID: _______________
Video with Audio ID: _______________
Inter-Agent Communication: Success / Failed
ffmpeg Execution Time: _______________
```

### Success Criteria
✅ Pass: VideoAgent successfully queries AudioAgent and mixes audio
**THIS IS THE BIG ONE!** Proves autonomous agent collaboration!

### If It Fails
**"No audio found":**
- Verify AudioAgent generated audio first
- Check Audio Gallery for files
- Check database: `from content.models import AudioHistory; AudioHistory.objects.count()`

**"Agent query timeout":**
- Check Redis connection: `redis-cli -n 3 PING`
- Verify Agent Query Protocol initialized (console logs)
- Check both agents registered

**"ffmpeg error":**
- Check ffmpeg installed: `ffmpeg -version`
- Check file permissions
- Check temp directory space

**Audio not audible in video:**
- Check volume levels (default: 0.5)
- Try different audio file
- Check audio file format (should be MP3/WAV)

---

## 📊 Testing Session Summary Template

Copy this after completing tests:

```
=================================================================
SESSION 95 PART 2: AGENT WORKFLOW TESTING RESULTS
=================================================================
Date: November 14, 2025
Tester: [Your Name]
Duration: _____ hours

TEST RESULTS:
[ ] Test 1: Multi-Option Generation - PASS / FAIL
[ ] Test 2: Save as Template - PASS / FAIL
[ ] Test 3: Refine Image - PASS / FAIL
[ ] Test 4: Brand Training - PASS / FAIL
[ ] Test 5: Inter-Agent Communication - PASS / FAIL

Overall: _____/5 tests passed (_____%)

NOTES:
-
-
-

ISSUES DISCOVERED:
-
-

NEXT STEPS:
-
-
=================================================================
```

---

## 🚀 Ready to Begin!

**When you return:**
1. Open AI Studio: `open http://localhost:8000/ai-studio/`
2. Navigate to AI Assistant tab
3. Start with Test 1: "Generate three coffee shop logos"
4. Use this document as your guide
5. Record results as you go

**Good luck! Let's prove these agents work! 🎯✨**

---

**Last Updated:** November 14, 2025
**Status:** READY FOR TESTING
**All prerequisites verified:** ✅

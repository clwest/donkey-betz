# Editing Agents Test Plan - Session 125

**Purpose:** Verify all editing capabilities work  
**Method:** Voice commands through AI Assistant

---

## 🎨 IMAGE EDITING TESTS

### EditingOrchestratorAgent Tests

**Test 1: Upscale Image**
```
Voice: "Upscale image 1"
Expected: Image gets upscaled 4x
Agent: EditingOrchestratorAgent
Capability: upscale_4x
```

**Test 2: Remove Background**
```
Voice: "Remove background from image 2"
Expected: Background removed, transparent PNG
Agent: EditingOrchestratorAgent
Capability: remove_background
```

**Test 3: Recolor Image**
```
Voice: "Make image 3 more vibrant"
Expected: Colors enhanced/adjusted
Agent: EditingOrchestratorAgent
Capability: recolor
```

**Test 4: Image-to-Image (Style Transfer)**
```
Voice: "Make image 4 look like image 1"
Expected: Style from image 1 applied to image 4
Agent: EditingOrchestratorAgent  
Capability: image_to_image
```

**Test 5: Inpaint (Fill/Fix)**
```
Voice: "Fix the damaged area in image 5"
Expected: AI fills in missing/damaged areas
Agent: EditingOrchestratorAgent
Capability: inpaint
```

**Test 6: Outpaint (Expand)**
```
Voice: "Expand the borders of image 6"
Expected: AI generates extended borders
Agent: EditingOrchestratorAgent
Capability: outpaint
```

---

## 🎬 VIDEO EDITING TESTS

### VideoAgent Tests

**Test 7: Add Text to Video**
```
Voice: "Add text 'Hello World' at 3 seconds for 5 seconds to video 1"
Expected: Text overlay appears 3-8 seconds
Agent: VideoAgent
Capability: add_text_to_video
```

**Test 8: Add Music to Video**
```
Voice: "Add background music to video 2"
Expected: Music added at 50% volume
Agent: VideoAgent
Capability: add_music_to_video  
```

**Test 9: Apply Color Grade**
```
Voice: "Make video 3 more cinematic"
Expected: Color grading applied
Agent: VideoAgent
Capability: apply_color_grade
```

**Test 10: Chain Videos**
```
Voice: "Combine video 1 and video 2 into one video"
Expected: Videos combined with smooth transition
Agent: VideoAgent
Capability: chain_videos
```

---

## 🎭 CREATIVE AGENTS TESTS

### CreativeDirectorAgent Test

**Test 11: Generate Multiple Options**
```
Voice: "Give me 3 different versions of this logo"
Expected: 3 variations with different styles
Agent: CreativeDirectorAgent
Capability: multi_option_generation
```

### IterationAgent Test

**Test 12: Refine/Improve**
```
Voice: "Make this image better"
Expected: AI analyzes and improves the image
Agent: IterationAgent
Capability: iteration_analysis, improvement_suggestions
```

### BrandStyleAgent Test

**Test 13: Train Custom Style (Advanced)**
```
Voice: "Train a custom style from these 5 images"
Expected: FLUX LoRA model trained (takes ~30 min)
Agent: BrandStyleAgent
Capability: flux_lora_training
Status: ADVANCED - Skip for now
```

---

## 📊 TEST RESULTS TEMPLATE

| Test # | Feature | Status | Notes |
|--------|---------|--------|-------|
| 1 | Upscale 4x | ⏸️ Not tested | |
| 2 | Remove BG | ⏸️ Not tested | |
| 3 | Recolor | ⏸️ Not tested | |
| 4 | Style Transfer | ⏸️ Not tested | |
| 5 | Inpaint | ⏸️ Not tested | |
| 6 | Outpaint | ⏸️ Not tested | |
| 7 | Text Overlay | ⏸️ Not tested | |
| 8 | Add Music | ⏸️ Not tested | |
| 9 | Color Grade | ⏸️ Not tested | |
| 10 | Chain Videos | ⏸️ Not tested | |
| 11 | Multi Options | ⏸️ Not tested | |
| 12 | Refinement | ⏸️ Not tested | |

---

## 🎯 PRIORITY TESTS (Start Here!)

**If time is limited, test these first:**

1. ✅ **Upscale image** (Test 1) - Very common use case
2. ✅ **Remove background** (Test 2) - Super useful
3. ✅ **Style transfer** (Test 4) - Already working from workflows!
4. ✅ **Add text to video** (Test 7) - Key video feature
5. ✅ **Generate variations** (Test 11) - Creative workflow

---

## 🔍 HOW TO TEST

1. **Open AI Assistant** in your browser
2. **Use voice or type** the test command
3. **Watch for:**
   - Does AI understand the command?
   - Does it call the right agent?
   - Does the operation complete?
   - Does the result appear in the gallery?
4. **Mark result:** ✅ Works | ⚠️ Partial | ❌ Failed

---

## 💡 EXPECTED BEHAVIOR

**If agent is working:**
- AI understands command
- Calls appropriate agent
- Operation completes
- Result appears in gallery
- Console shows agent execution logs

**If agent is NOT working:**
- AI doesn't understand OR
- AI understands but no agent is called OR
- Agent is called but errors out OR
- Operation completes but no result

---

**Next:** DaVinci Resolve separate test (requires DaVinci Studio installed)


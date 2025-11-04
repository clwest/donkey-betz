# 🎭 Character Performance "No Face Found" Troubleshooting

**Error:** "❌ Failed: No face found"
**Feature:** Character Performance (Act Two)
**Date:** November 4, 2025 - Session 51

---

## 🔍 What's Happening

The "No face found" error is coming from **Runway ML's Act Two API**, not our code. The API uses facial recognition to detect faces in both:
1. **Portrait image** (the character you want to animate)
2. **Reference video** (showing person performing movements)

If the API can't detect a clear face in EITHER asset, it returns this error.

---

## ✅ Runway ML Requirements

### **Portrait Image Requirements:**

**Must Have:**
- ✅ Clear, visible face (not blurry, pixelated, or occluded)
- ✅ Frontal view (looking at camera, not profile/side view)
- ✅ Face fills **20-40% of frame** (not too small, not too close)
- ✅ Good lighting (no harsh shadows on face)
- ✅ Eyes, nose, mouth clearly visible
- ✅ High resolution (minimum 512x512, recommended 1024x1024+)

**Avoid:**
- ❌ Profile/side views (must be frontal)
- ❌ Faces partially covered (hair, hands, objects)
- ❌ Multiple faces (use single portrait)
- ❌ Cartoon/anime faces (use photorealistic)
- ❌ Very small faces (<20% of frame)
- ❌ Very large faces (>50% of frame, too zoomed in)
- ❌ Blurry or low-resolution images
- ❌ Extreme lighting (too dark, too bright, harsh shadows)

---

### **Reference Video Requirements:**

**Must Have:**
- ✅ Duration: **3-30 seconds** (not shorter, not longer)
- ✅ Shows **person performing** movements/expressions
- ✅ Face visible and well-lit throughout video
- ✅ Clear facial expressions and movements
- ✅ Minimum 720p resolution
- ✅ Face fills 20-40% of frame

**Avoid:**
- ❌ Too short (<3 seconds)
- ❌ Too long (>30 seconds)
- ❌ No person visible (landscape, objects only)
- ❌ Face obscured or turned away
- ❌ Very shaky/unstable footage
- ❌ Low resolution (<720p)
- ❌ Multiple people (focus on one person)
- ❌ Face too small in frame

---

## 🐛 Common Causes & Fixes

### **Cause #1: Generated Portrait Too Small**

**Problem:**
- Used image generation with prompt like "A person in a landscape"
- Face is small part of overall image
- Runway can't detect it as primary subject

**Fix:**
```
Bad Prompt:  "A person standing in a beautiful mountain landscape"
             → Face is tiny, landscape dominates

Good Prompt: "Professional portrait of a person, front-facing, neutral expression,
              studio lighting, headshot, clear facial features, high detail"
             → Face fills 40-50% of frame
```

**Best Practice:**
- Use "headshot" or "portrait" in prompt
- Add "front-facing", "looking at camera"
- Specify "clear facial features"
- Avoid landscape/environment details

---

### **Cause #2: Webcam Video Too Dark/Blurry**

**Problem:**
- Recorded webcam video in poor lighting
- Face not well-lit or clear
- Camera quality too low

**Fix:**
1. **Improve Lighting:**
   - Face light source (lamp/window)
   - Avoid backlighting
   - Even, soft light

2. **Camera Position:**
   - Eye level
   - 2-3 feet away
   - Face fills 30-40% of frame

3. **Test Before Recording:**
   - Check webcam preview
   - Ensure face is clear and bright
   - Adjust position/lighting

---

### **Cause #3: Profile/Side View Portrait**

**Problem:**
- Portrait image shows profile or angled face
- Runway needs frontal face view

**Fix:**
```
Bad: "side profile of a person" → API can't detect frontal face
Good: "front-facing portrait" → API can detect face
```

---

### **Cause #4: Low Resolution**

**Problem:**
- Image/video too small or low quality
- Face details not clear enough for detection

**Fix:**
- **Images:** Use 1024x1024 or larger
- **Videos:** Minimum 720p (1280x720)
- **Webcam:** Ensure HD mode (1920x1080)

---

### **Cause #5: Multiple Faces**

**Problem:**
- Image shows multiple people
- Video shows group of people
- Runway doesn't know which face to use

**Fix:**
- Use single-person portraits
- Crop to show only one face
- Focus webcam on one person

---

## 🧪 Testing Your Assets

### **Test Your Portrait Image:**

**Manual Check:**
1. Open image in preview
2. Can you clearly see ONE face?
3. Is face frontal (not profile)?
4. Does face fill 20-40% of image?
5. Are eyes, nose, mouth clearly visible?
6. Is lighting even (no harsh shadows)?

**If NO to any → Fix before using!**

### **Test Your Reference Video:**

**Manual Check:**
1. Play the video
2. Is duration 3-30 seconds? ✅
3. Can you see ONE person's face throughout? ✅
4. Is face well-lit and clear? ✅
5. Are expressions/movements visible? ✅
6. Is resolution good (not pixelated)? ✅

**If NO to any → Fix before using!**

---

## 🎯 Recommended Workflow

### **Step 1: Generate Perfect Portrait**

**Use This Prompt:**
```
"Professional headshot portrait of a [person description],
front-facing, looking at camera, neutral expression,
studio lighting, clear facial features, high detail,
sharp focus, photorealistic, well-lit face"
```

**Settings:**
- Model: SD3 or SDXL (high quality)
- Size: 1024x1024
- Style: Photorealistic
- Negative prompt: "profile, side view, multiple people, blurry, dark"

**Verify:**
- Face fills 40-50% of image ✅
- Frontal view ✅
- Clear features ✅
- Good lighting ✅

---

### **Step 2: Record Perfect Reference Video**

**Setup:**
1. Good lighting (face light in front)
2. Clean background
3. Camera at eye level
4. Face fills 30-40% of frame

**Recording:**
1. Click webcam button
2. Position face in oval guide
3. Record 8-10 seconds
4. Make natural expressions:
   - Smile (2s)
   - Serious (2s)
   - Surprised (2s)
   - Talking (2s)
   - Head nods/tilts (2s)

**Verify:**
- Duration 8-10 seconds ✅
- Face visible and lit throughout ✅
- Natural movements ✅
- No extreme angles ✅

---

### **Step 3: Generate Character Performance**

**In UI:**
1. Go to Video → Character Performance
2. **Portrait:** Select generated image from gallery
3. **Reference:** Use recorded webcam video (or select from gallery)
4. **Prompt:** "Animate portrait with natural facial expressions and head movements"
5. Click "Generate"

**Wait:**
- Processing: ~60-90 seconds
- API validates assets first
- Then generates animation

---

## 🔧 Advanced Debugging

### **Check API Response:**

If still getting error, check browser console (F12):

```javascript
// Look for error details in Network tab
POST /api/v1/video/character-performance/

Response: {
  "success": false,
  "error_message": "RunwayML API error (400): ..."
}
```

**Common API Errors:**
- `"No face found in portrait"` → Fix portrait image
- `"No face found in reference video"` → Fix video
- `"Reference video too short"` → Must be >= 3 seconds
- `"Reference video too long"` → Must be <= 30 seconds
- `"Invalid image format"` → Check file type
- `"Face not frontal"` → Use front-facing portrait

---

### **Test with Known-Good Assets:**

**Download Test Assets:**

1. **Test Portrait:** Generate with this exact prompt:
   ```
   "Professional headshot portrait of a smiling person,
   front-facing, looking directly at camera,
   studio lighting, clear facial features,
   photorealistic, well-lit, high detail"
   ```

2. **Test Video:** Record 8-second webcam video with:
   - Good lighting
   - Face centered in oval guide
   - Natural smile and head nods
   - Look directly at camera

If these work → Your original assets had issues
If these fail → Check API key / system configuration

---

## 💡 Pro Tips

### **For Best Portrait Results:**

1. **Use specific prompts:**
   - "headshot portrait" not "photo of person"
   - "front-facing" not "side view"
   - "studio lighting" for even illumination

2. **Check before using:**
   - Zoom in - can you see clear facial features?
   - Face should fill 40-50% of image
   - No obstructions (hair, hands, objects)

3. **Generation settings:**
   - Use SD3 or SDXL for quality
   - 1024x1024 minimum size
   - Avoid "artistic" styles for this use case

### **For Best Video Results:**

1. **Lighting is CRITICAL:**
   - Face light in front of you
   - No bright windows behind you
   - Even, soft lighting

2. **Keep it natural:**
   - Normal speed movements
   - Natural expressions
   - Don't exaggerate

3. **Camera position:**
   - Eye level
   - Arms length away (2-3 feet)
   - Face fills 30-40% of frame

---

## ✅ Checklist Before Submission

**Portrait Image:**
- [ ] Face fills 20-40% of image
- [ ] Front-facing (not profile)
- [ ] Clear features (eyes, nose, mouth visible)
- [ ] Good lighting (no harsh shadows)
- [ ] High resolution (1024x1024+)
- [ ] Single person only
- [ ] Photorealistic (not cartoon/anime)

**Reference Video:**
- [ ] Duration 3-30 seconds (preferably 8-10s)
- [ ] Shows person performing movements
- [ ] Face visible and well-lit throughout
- [ ] Clear expressions and movements
- [ ] 720p+ resolution
- [ ] Single person only
- [ ] Face fills 20-40% of frame

**If ALL checked → Should work! ✅**
**If ANY unchecked → Fix before trying again**

---

## 📞 Still Not Working?

**Steps:**
1. Check console logs (F12 → Console tab)
2. Check network errors (F12 → Network tab)
3. Verify API key is loaded: `RUNWAY_API_KEY` in .env
4. Test with minimal example (simple prompt + webcam)
5. Share exact error message for debugging

**Common Final Issues:**
- API key not configured → Check `.env` file
- API key expired/invalid → Check Runway dashboard
- Credits exhausted → Check Runway credits
- Network error → Check internet connection

---

**Created:** November 4, 2025 - Session 51
**Status:** Comprehensive troubleshooting guide
**Next:** Test with improved assets following these guidelines

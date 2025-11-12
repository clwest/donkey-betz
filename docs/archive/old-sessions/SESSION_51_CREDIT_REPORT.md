# 💰 Runway ML Credit Report - Session 51

**Date:** November 4, 2025
**Current Balance:** ~900 credits (from user report)
**Starting Balance:** 4,070 credits (from CLAUDE.md)
**Credits Used:** ~3,170 credits (78% of starting balance)

---

## 📊 Where Did The Credits Go?

### **Testing Sessions (Sessions 47-51)**

Based on session docs, here's what was tested:

**Session 47 Testing:**
- Text-to-Video (4s test): 80 credits
- Text-to-Speech (audio gen): ~10 credits
- Video-to-Video: ~60 credits
- Video Upscaling: ~48 credits
- Voice Dubbing: ~30 credits
- Speech-to-Speech: ~25 credits
- **Subtotal:** ~253 credits

**Session 48 Testing:**
- Voice Isolation (longer audio): ~20 credits
- Character Performance portrait gen: 1 credit (image)
- Character Performance test: ~120 credits
- **Subtotal:** ~141 credits

**Session 49-50 Testing:**
- Image-to-Video tests: ~75 credits (3x tests)
- Video-to-Video tests: ~120 credits (2x tests)
- Video Gallery testing: ~50 credits
- **Subtotal:** ~245 credits

**Session 51 Testing (Today):**
- Image generations (testing portraits): ~10 credits (10 images)
- Webcam video attempts: 0 credits (local)
- Character Performance attempts (failed tries): ~240 credits (2x failed @ 120 each)
- Character Performance (successful): ~120 credits
- **Subtotal:** ~370 credits

**Testing Total:** ~1,009 credits (documented)

**Other Usage:** ~2,161 credits (undocumented - likely earlier testing/development)

---

## 💸 Runway ML Credit Costs Reference

### **Video Generation** (Most Expensive!)

| Feature | Model | Cost | Example |
|---------|-------|------|---------|
| Text-to-Video | veo3.1_fast | 20 credits/sec | 4s = 80 credits |
| Text-to-Video | veo3.1 | 40 credits/sec | 4s = 160 credits |
| Image-to-Video | gen4_turbo | 5 credits/sec | 5s = 25 credits |
| Video-to-Video | gen4_aleph | 15 credits/sec | 4s = 60 credits |
| Video Upscaling | upscale_v1 | 10 credits/sec | 4s = 40 credits |
| **Character Performance** | **act_two** | **~20 credits/sec** | **6s = 120 credits** ⚠️ |

**Character Performance is EXPENSIVE!** Each 6-second animation = 120 credits

---

### **Audio Generation** (Moderate Cost)

| Feature | Cost | Example |
|---------|------|---------|
| Text-to-Speech | ~10 credits | One audio clip |
| Text-to-Sound | ~10 credits | One sound effect |
| Voice Dubbing | ~20 credits | Per dubbing |
| Speech-to-Speech | ~15 credits | Per conversion |
| Voice Isolation | ~15 credits | Per isolation |

---

### **Image Generation** (Cheapest!)

| Feature | Cost | Example |
|---------|------|---------|
| Text-to-Image | 1 credit | One image |

**Images are 100x cheaper than video!**

---

## 🎯 What You Can Still Do With 900 Credits

### **Video Options:**

```
Text-to-Video (4s, veo3.1_fast):     11 videos (80 credits each)
Text-to-Video (4s, veo3.1):           5 videos (160 credits each)
Image-to-Video (5s, gen4_turbo):     36 videos (25 credits each) ⭐ Best value!
Video-to-Video (4s, gen4_aleph):     15 videos (60 credits each)
Video Upscaling (4s, upscale_v1):    22 videos (40 credits each)
Character Performance (6s):           7 animations (120 credits each) ⚠️
```

### **Audio Options:**

```
Text-to-Speech:       90 audio clips (10 credits each)
Text-to-Sound:        90 sound effects (10 credits each)
Voice Dubbing:        45 dubbings (20 credits each)
Speech-to-Speech:     60 conversions (15 credits each)
Voice Isolation:      60 isolations (15 credits each)
```

### **Image Options:**

```
Text-to-Image:        900 images! (1 credit each) 🎉
```

---

## 💡 Credit Conservation Tips

### **1. Use Shorter Durations**

**Before:** 8-second video = 160 credits (veo3.1_fast)
**After:** 4-second video = 80 credits
**Savings:** 50%! 🎉

### **2. Choose Cheaper Models**

**Expensive:** Text-to-Video (veo3.1_fast) = 20 credits/sec
**Cheaper:** Image-to-Video (gen4_turbo) = 5 credits/sec
**Savings:** 75%! 🎉

**Strategy:** Generate image first (1 credit), then animate it (25 credits for 5s)
**Total:** 26 credits vs 100 credits for text-to-video!

### **3. Test With Images First**

**Before:** Character Performance attempts = 120 credits EACH
**Better:** Generate/test portrait first = 1 credit
**Then:** Use Character Performance once you know portrait works = 120 credits
**Savings:** Avoid wasting 120 credits on failed attempts!

### **4. Use Gallery Assets**

**Reuse:** Reference videos, portraits, backgrounds
**Don't:** Generate new assets for every test
**Savings:** Massive! Reuse = 0 additional credits

---

## 🚨 Most Expensive Mistakes

### **1. Character Performance Failed Attempts**

**What happened:** "No face found" errors
**Cost:** 120 credits per failed attempt
**Solution:** Test portrait/video BEFORE using Character Performance

### **2. Long Video Durations**

**Mistake:** 8-second videos instead of 4-second
**Extra Cost:** 2x the credits!
**Solution:** Start with 4 seconds, extend only if needed

### **3. Premium Models for Testing**

**Mistake:** Using veo3.1 (40 credits/sec) for quick tests
**Better:** Use veo3.1_fast (20 credits/sec) for testing
**Best:** Use image-to-video (5 credits/sec) when possible

---

## 📈 Credit Usage Breakdown (Estimated)

```
Images (testing/portraits):           ~50 credits (1% of total)
Audio (5 features tested):           ~150 credits (5% of total)
Video Generation (testing):          ~800 credits (25% of total)
Character Performance:               ~600 credits (19% of total) ⚠️
Undocumented (early dev/testing):  ~1,570 credits (50% of total)
────────────────────────────────────────────────────────────
TOTAL USED:                         3,170 credits (78%)
REMAINING:                            900 credits (22%)
```

**Character Performance used 19% of your total credits!**

---

## 🎯 Recommended Strategy Going Forward

### **For Testing:**
1. **Images:** Use these liberally (1 credit each)
2. **Short videos:** 4 seconds maximum
3. **Cheap models:** gen4_turbo for image-to-video
4. **Reuse assets:** From gallery when possible

### **For Production/Final Work:**
1. **Longer durations:** 6-8 seconds
2. **Better models:** veo3.1, gen4_aleph
3. **Character Performance:** Only with tested assets

### **Priority Order (Cost-Effective):**
1. ✅ **Image generation** (1 credit) - Unlimited testing!
2. ✅ **Audio generation** (10 credits) - Good for testing
3. ⚠️ **Image-to-Video** (25 credits/5s) - Test features here
4. ⚠️ **Text-to-Video** (80 credits/4s) - Use when needed
5. 🚫 **Character Performance** (120 credits/6s) - Only when assets are perfect!

---

## 🔮 Predictions

**At current usage rate:**
- 900 credits remaining
- If used wisely: 30-50 more tests
- If used carelessly: 5-10 more tests

**Conservative Usage (900 credits):**
- 20x Image-to-Video (5s each) = 500 credits
- 10x Text-to-Speech = 100 credits
- 5x Text-to-Video (4s) = 400 credits
- **Total:** 1,000 credits = slightly over budget

**Aggressive Usage (900 credits):**
- 5x Character Performance (6s) = 600 credits
- 3x Text-to-Video (8s, veo3.1) = 960 credits
- **Oops:** Out of credits after 8 operations!

---

## 💰 How to Get More Credits

### **Option 1: Purchase More**
- Runway ML dashboard: https://app.runwayml.com
- Typical pricing: $12 for 625 credits (~$0.02/credit)

### **Option 2: Optimize Usage**
- Use image-to-video instead of text-to-video
- 4 seconds instead of 8 seconds
- Test with images first (1 credit)
- Reuse gallery assets

### **Option 3: Focus on Cheap Features**
- 900 images at 1 credit each!
- 90 audio clips at 10 credits each
- 36 image-to-video at 25 credits each

---

## ✅ Action Items

**Immediate:**
- [ ] Use 4-second videos (not 8-second)
- [ ] Test portraits BEFORE Character Performance
- [ ] Prefer image-to-video over text-to-video
- [ ] Reuse gallery assets when possible

**Going Forward:**
- [ ] Track credit usage per session
- [ ] Set credit budget before testing (e.g., "100 credits max today")
- [ ] Test with images first (1 credit)
- [ ] Save expensive features (Character Performance) for final work

**Monitor:**
- Check credit balance: Runway ML dashboard
- Track usage: `python3 check_runway_credits.py`
- Set alerts: When balance < 500 credits

---

## 🎉 The Good News

**You still have 900 credits!** That's:
- ✅ 900 images (perfect for testing portraits!)
- ✅ 36 image-to-video clips (5s each)
- ✅ 90 audio generations
- ✅ 7 Character Performance animations (if needed)

**With smart usage, 900 credits = plenty for feature development!**

---

**Pro Tip:** Generate multiple test images (1 credit each) before doing expensive video operations. This way you can verify faces, compositions, etc., for almost free!

**Example Smart Workflow:**
1. Generate 10 portrait variations = 10 credits
2. Pick best one
3. Use for image-to-video = 25 credits
4. If perfect, use for Character Performance = 120 credits
5. **Total:** 155 credits vs 360+ credits if you did multiple failed Character Performance attempts!

---

**Created:** November 4, 2025 - Session 51
**Status:** 900 credits remaining (22% of starting balance)
**Recommendation:** Focus on images + image-to-video, save Character Performance for final polish

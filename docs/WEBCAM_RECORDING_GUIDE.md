# 🎥 Webcam Recording Guide - Character Performance

**Purpose:** Record a reference video showing facial expressions and movements to animate a portrait

---

## ✅ Pre-Recording Checklist

### 1. **Browser Requirements**
- ✅ **Chrome/Edge/Brave:** Best support (recommended)
- ✅ **Safari:** Works well on macOS
- ✅ **Firefox:** Good support
- ⚠️ **Must use HTTPS or localhost** (browsers block camera on HTTP)

### 2. **Webcam Permissions**
**First Time Using Webcam:**
1. Click "🎥 Record with Webcam" button
2. Browser will ask: "Allow ai-studio to access your camera?"
3. ✅ Click "Allow" or "Yes"

**If Camera Access Denied:**
- **Chrome:** Click 🔒 padlock in address bar → Site settings → Camera → Allow
- **Safari:** System Preferences → Security & Privacy → Camera → Check browser checkbox
- **Refresh page** after changing permissions

### 3. **Webcam Hardware Check**
```bash
# macOS - Check if camera is in use
lsof | grep "AppleCamera" | grep -v "grep"

# macOS - Kill apps using camera
killall VDCAssistant  # Restart camera service
```

---

## 📸 Recording Best Practices

### **Lighting** (Most Important!)
- ✅ **Face the light source** - Window or lamp in front of you
- ✅ **Avoid backlighting** - Don't sit with bright window behind you
- ✅ **Even lighting** - No harsh shadows on face
- ✅ **Natural or soft white light** - Avoid yellow/dim lighting

### **Camera Position**
- ✅ **Eye level** - Camera at same height as your eyes
- ✅ **Arm's length distance** - About 2-3 feet away
- ✅ **Face fills 40-50% of frame** - Use the oval guide overlay
- ✅ **Center your face** - Keep inside the dashed oval

### **Background**
- ✅ **Simple, uncluttered** - Plain wall or minimal background
- ✅ **Contrasting color** - Different from your skin tone/clothing
- ⚠️ **Avoid busy patterns** - No posters, shelves, or distractions

### **Your Appearance**
- ✅ **Face clearly visible** - Hair away from face
- ✅ **Good contrast** - Face stands out from background
- ✅ **Clear features** - Remove glasses if they reflect light
- ⚠️ **Avoid face masks or obstructions**

---

## 🎬 Recording Process

### **Step 1: Initialize Webcam**
1. Go to **Video tab** → **Character Performance** mode
2. Click **"🎥 Record with Webcam"** button
3. Grant camera permission (if prompted)
4. Wait for webcam preview to appear

**Webcam Preview Shows:**
- Mirror image of yourself
- Dashed oval guide (face positioning)
- Tips overlay in top-left corner

### **Step 2: Position Yourself**
Use the overlay tips:
- Position face inside oval guide
- Face should fill 40-50% of frame
- Use good lighting (face well-lit)
- Look directly at camera
- Ready to make clear expressions

**Quality Settings (Automatic):**
- Resolution: HD 1920x1080
- Format: WebM (VP9 codec)
- Duration: 15 seconds max
- No audio recorded

### **Step 3: Start Recording**
1. Click **"▶️ Start Recording (15s)"** button
2. **3-second countdown** appears (Get ready!)
3. Recording starts automatically after countdown
4. **⏺ RECORDING** indicator appears

**During Recording (15 seconds):**
- Make natural facial expressions
- Move your head slightly (nod, tilt, turn)
- Smile, look surprised, serious
- Keep movements smooth and natural
- Stay within the oval guide

**Timer Shows:**
- Remaining time in seconds
- Auto-stops at 15 seconds
- Can stop early if needed

### **Step 4: Preview & Use**
**After Recording:**
1. Preview window shows your recorded video
2. **Play button** - Review your recording
3. **Options:**
   - ✅ **Use This Recording** - Proceed with this video
   - 🔄 **Record Again** - Discard and redo
   - ❌ **Cancel** - Exit without saving

**When You Click "Use This Recording":**
- File automatically set as reference video
- Webcam UI closes
- Ready to select portrait image and generate!

---

## 🐛 Troubleshooting

### **Problem: "Could not access webcam"**

**Solution 1: Check Browser Permissions**
```bash
# Chrome DevTools Console (F12)
navigator.mediaDevices.getUserMedia({video: true})
  .then(stream => console.log("✅ Camera works!"))
  .catch(err => console.error("❌ Error:", err));
```

**Solution 2: Close Other Apps Using Camera**
- Zoom, Skype, FaceTime, Photo Booth
- System Settings → Privacy → Camera → Check which apps have access

**Solution 3: Restart Browser**
- Close ALL browser windows
- Reopen and try again

### **Problem: Black screen / No video**

**Causes:**
1. Camera in use by another application
2. Browser needs refresh after permission change
3. macOS camera permissions not granted to browser

**Fix:**
```bash
# macOS - Restart camera service
sudo killall VDCAssistant

# Then refresh browser page
```

### **Problem: Video is too dark / Can't see face**

**Fix:**
1. Add more light in front of you
2. Move closer to window (daytime)
3. Use desk lamp or ring light
4. Adjust camera exposure (macOS: System Settings → Camera)

### **Problem: Recording stops immediately**

**Cause:** Browser doesn't support VP9 codec

**Fix:**
1. Update browser to latest version
2. Try different browser (Chrome recommended)
3. Check console for error: `MediaRecorder` not supported

### **Problem: "Could not start recording"**

**Console Check:**
```javascript
// In browser console (F12)
MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
// Should return: true
```

**Fix:**
- Update browser
- Try: `video/webm;codecs=vp8` (fallback)

---

## 🎯 Recording Tips for Best Results

### **Facial Expressions to Include:**
1. **Neutral** - Relaxed, natural face (1-2s)
2. **Smile** - Natural, genuine smile (2-3s)
3. **Serious** - Focused, thoughtful look (2-3s)
4. **Surprised** - Raised eyebrows, open mouth (1-2s)
5. **Talking** - Mouth moving naturally (2-3s)
6. **Head movements** - Subtle nods, tilts (3-4s)

### **What Makes a Good Reference Video:**
✅ **Clear, well-lit face** - All features visible
✅ **Natural movements** - Not robotic or jerky
✅ **Good resolution** - HD 1080p captures detail
✅ **Stable camera** - No shaking (use laptop/stand)
✅ **Variety of expressions** - Multiple emotions shown
✅ **3-10 seconds** - Enough variety, not too long

### **What to Avoid:**
❌ **Looking away from camera** - Keep eyes on lens
❌ **Too much movement** - Stay mostly in frame
❌ **Poor lighting** - Shadows hide features
❌ **Obstructions** - Hands, hair, objects in front of face
❌ **Extreme expressions** - Keep it natural

---

## 🔧 Technical Details

### **Webcam Request Configuration:**
```javascript
navigator.mediaDevices.getUserMedia({
    video: {
        width: { ideal: 1920 },
        height: { ideal: 1080 },
        facingMode: 'user'  // Front camera
    },
    audio: false  // No audio needed
})
```

### **Recording Configuration:**
```javascript
mediaRecorder = new MediaRecorder(stream, {
    mimeType: 'video/webm;codecs=vp9'
})
```

### **Output Format:**
- **Container:** WebM
- **Video Codec:** VP9
- **Resolution:** Up to 1920x1080 (HD)
- **Max Duration:** 15 seconds
- **No Audio Track**

### **Browser Compatibility:**
| Browser | Status | Notes |
|---------|--------|-------|
| Chrome 90+ | ✅ Full | Best support |
| Edge 90+ | ✅ Full | Chromium-based |
| Safari 14.1+ | ✅ Good | May need H.264 |
| Firefox 88+ | ✅ Good | Full VP9 support |
| Opera 76+ | ✅ Full | Chromium-based |

---

## 🎥 Alternative: Upload Video File

**If webcam doesn't work:**
1. Record video on phone/camera
2. Transfer to computer
3. Use **"Upload Reference Video"** option instead
4. Supported formats: MP4, MOV, WebM, AVI

**Requirements:**
- Duration: 3-30 seconds
- Clear face visible
- Good lighting
- HD resolution preferred

---

## ✅ Quick Checklist Before Recording

- [ ] Browser permissions granted
- [ ] No other apps using camera
- [ ] Good lighting (face visible)
- [ ] Camera at eye level
- [ ] Face fills 40-50% of frame
- [ ] Simple background
- [ ] Hair away from face
- [ ] Ready to make expressions
- [ ] 15 seconds planned out

---

## 🚀 After Recording Successfully

**Next Steps:**
1. ✅ Reference video captured
2. Select or generate portrait image
3. Enter prompt for animation style
4. Click "Generate Character Performance"
5. Wait ~60-90 seconds for result
6. Watch your portrait come to life!

---

## 📞 Still Having Issues?

**Check Console Errors:**
1. Press **F12** (open DevTools)
2. Go to **Console** tab
3. Look for red errors when clicking webcam button
4. Share error message for debugging

**Common Console Errors:**
- `NotAllowedError` - Permission denied, check browser settings
- `NotFoundError` - No camera detected, check hardware
- `NotReadableError` - Camera in use by another app
- `OverconstrainedError` - Resolution not supported by camera

---

**Created:** November 4, 2025 - Session 51
**Status:** Complete webcam recording system with HD quality
**Next:** Use for Character Performance feature testing

# 🔍 Session 83: Complete Audio Workflow Diagnostic
**Date:** November 13, 2025
**Status:** INVESTIGATING - System not working end-to-end

---

## 🎯 The Problem

**User Experience:**
1. User says: "Generate speech saying welcome to the jungle"
2. AI responds: "✅ **Speech Ready!**" with audio URL
3. User says: "Add that speech to my last video"
4. AI responds: "✅ Audio successfully added to video!"
5. **BUT:** No new video appears, no audio file was created

**Reality:** The AI Assistant is **hallucinating** the audio generation. No backend tools were called.

---

## 🔬 Complete Workflow Analysis

### **EXPECTED FLOW:**

```
User Voice Input
    ↓
Whisper Transcription
    ↓
AI Assistant (GPT-5-mini)
    ↓
TOOL CALL: generate_speech(text="welcome to the jungle")
    ↓
Backend: _execute_generate_speech()
    ↓
AudioAgent.generate_speech()
    ↓
ElevenLabs API Call
    ↓
Save MP3 to media/audio/elevenlabs/
    ↓
Store in shared memory
    ↓
Return audio_url to user
    ↓
[User says "add to video"]
    ↓
TOOL CALL: add_music_to_video()
    ↓
VideoAgent.add_music_to_video()
    ↓
Query AudioAgent for audio_url (if not provided)
    ↓
DaVinci Provider: add_music_to_video()
    ↓
Download video from CDN
    ↓
Get audio file from media/
    ↓
ffmpeg mixes video + audio
    ↓
Save to media/videos/
    ↓
Create VideoHistory record
    ↓
Return success + video_url
    ↓
Display in gallery
```

### **ACTUAL FLOW (BROKEN):**

```
User Voice Input
    ↓
Whisper Transcription ✅
    ↓
AI Assistant (GPT-5-mini) ✅
    ↓
❌ NO TOOL CALL - AI just responds with text
    ↓
AI fabricates: "✅ **Speech Ready!**"
    ↓
AI fabricates: "AUDIO_URL: /media/audio/elevenlabs/[fake-uuid].mp3"
    ↓
[User says "add to video"]
    ↓
TOOL CALL: add_music_to_video(audio_url="/media/audio/elevenlabs/[fake-uuid].mp3") ✅
    ↓
VideoAgent.add_music_to_video() ✅
    ↓
DaVinci Provider: add_music_to_video() ✅
    ↓
Download video from CDN ✅
    ↓
❌ Try to get audio file - FILE DOESN'T EXIST
    ↓
❌ Error: "Django media file not found"
    ↓
❌ Workflow fails
```

---

## 🧩 Component Status

### 1. **ElevenLabs Provider** (`content/elevenlabs_provider.py`)

**Status:** ❓ UNKNOWN (never called)

**Functions:**
- `text_to_speech(text, voice)` - Generates speech from text
- `text_to_sound(prompt, duration)` - Generates sound effects

**Expected Behavior:**
1. Call ElevenLabs API
2. Download audio bytes
3. Save to `media/audio/elevenlabs/elevenlabs_speech_{uuid}.mp3`
4. Return `{'success': True, 'audio_url': '/media/audio/elevenlabs/...'}`

**Actual Behavior:**
- ❓ Never executed during testing
- ❓ Unknown if it works

**Test Needed:**
```python
from content.elevenlabs_provider import elevenlabs_provider
result = elevenlabs_provider.text_to_speech(
    text="Hello world",
    voice="Rachel"
)
print(result)
# Should create actual file in media/audio/elevenlabs/
```

---

### 2. **AI Assistant Tool Registration** (`core/views_image.py`)

**Status:** ❌ BROKEN - generate_speech tool not being called

**Tool Definition Location:** Line ~4600+

**Expected Behavior:**
- When user says "Generate speech", GPT-5-mini should call `generate_speech` tool
- Backend executes `_execute_generate_speech()`
- Returns result to user

**Actual Behavior:**
- ❌ GPT-5-mini responds with text instead of calling tool
- ❌ AI fabricates response without backend execution
- ❌ No tool_call appears in logs

**Possible Causes:**
1. Tool description not clear enough for GPT-5-mini
2. System prompt doesn't emphasize tool usage for speech
3. GPT-5-mini sees generate_speech as "async" and responds immediately
4. Tool choice setting wrong (should be 'auto' or 'required')

**Investigation Needed:**
- Check tool definition for generate_speech
- Check if other tools work (generate_image, generate_video)
- Check system prompt for speech generation instructions

---

### 3. **AudioAgent** (`agents/audio_agent.py`)

**Status:** ✅ EXISTS but ❓ UNKNOWN if working

**Functions:**
- `generate_speech(text, voice)` - Wraps ElevenLabs
- `generate_sound_effect(description, duration)` - Wraps ElevenLabs
- Stores most recent audio in shared memory

**Expected Behavior:**
1. Call ElevenLabs provider
2. Store audio_url in shared memory
3. Return audio_url for use

**Actual Behavior:**
- ❓ Never executed during testing
- ❓ Unknown if memory storage works

**Test Needed:**
```python
from agents.audio_agent import AudioAgent
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')

agent = AudioAgent(user=user)
result = agent.generate_speech(
    text="Hello world",
    voice="Rachel"
)
print(result)
# Should return audio_url
```

---

### 4. **VideoAgent** (`agents/video_agent.py`)

**Status:** ⚠️ PARTIALLY WORKING

**Functions:**
- `add_music_to_video(video_selection, audio_url, audio_volume)`
- Queries AudioAgent if no audio_url provided

**Expected Behavior:**
1. Get video from database
2. Query AudioAgent for audio if not provided
3. Call DaVinci provider to mix
4. Save result to media/videos/
5. Create VideoHistory record
6. Return success

**Actual Behavior:**
- ✅ Gets video successfully
- ❌ Receives fake audio_url from AI Assistant
- ✅ Calls DaVinci provider
- ❌ DaVinci fails because audio file doesn't exist
- ❌ No VideoHistory record created

**Recent Fix (Session 83):**
- Added code to move ffmpeg output from /tmp/ to media/videos/
- Added code to create VideoHistory record
- ❓ Not tested yet with real audio

---

### 5. **DaVinci Provider** (`content/davinci_provider.py`)

**Status:** ✅ WORKS (ffmpeg) but ❌ FAILS on missing audio

**Functions:**
- `add_music_to_video(video_url, audio_url, audio_volume)`
- Uses ffmpeg for mixing (Session 82 switch)

**Expected Behavior:**
1. Download video to /tmp/
2. Get audio file (local or download)
3. Run ffmpeg to mix
4. Return path to mixed video

**Actual Behavior:**
- ✅ Downloads video successfully
- ✅ Checks for /media/audio/elevenlabs/ files
- ❌ File not found (because it was never created)
- ❌ Tries to download as URL → fails
- ❌ Returns error

**Test Needed:**
Test with REAL audio file that exists:
```bash
# Use existing file from yesterday
/media/audio/elevenlabs/elevenlabs_speech_0707d893-fd17-4806-b379-9c6fd7450efb.mp3
```

---

### 6. **Frontend AI Assistant** (`ai_core/templates/ai_image_studio.html`)

**Status:** ✅ WORKING - sends requests correctly

**Behavior:**
- ✅ Whisper transcription works
- ✅ Sends text to backend
- ✅ Receives AI responses
- ✅ Displays responses
- ❌ Trusts AI responses even when tools weren't called

**Not a Frontend Issue:**
- Frontend is working correctly
- Problem is backend tool execution

---

## 🔍 Root Cause Analysis

### **Primary Issue: AI Assistant Not Calling generate_speech Tool** ✅ FIXED!

**Evidence:**
```bash
# Search all logs for tool execution
$ grep "Executing tool: generate_speech" server.log
# Result: NO MATCHES

# But add_music_to_video IS called:
$ grep "Executing tool: add_music_to_video" server.log
# Result: FOUND (line 262)
```

**Root Cause Identified:**
The system prompt (lines 4305-4376 in `core/views_image.py`) **never mentioned `generate_speech` or `generate_sound_effect`**!

**What was missing:**
- ✅ generate_image - mentioned with examples
- ✅ generate_video - mentioned with examples
- ❌ **generate_speech** - NOT MENTIONED
- ❌ **generate_sound_effect** - NOT MENTIONED
- ✅ inpaint - mentioned
- ✅ web_search - mentioned

Without instructions to use the tools, GPT just responded with text instead of calling the backend.

**Fix Applied (Session 83):**
Added comprehensive instructions for speech/audio generation to system prompt:
- Added `generate_speech` description with ElevenLabs details
- Added `generate_sound_effect` description
- Added examples: `generate_speech(text="Welcome", voice="Rachel")`
- Added to "HOW TO RESPOND" section
- Emphasized: "IMPORTANT: This creates REAL audio files - don't just respond with text!"

**Location:** `core/views_image.py:4324-4332`

**Status:** ✅ FIXED - Testing in progress

### **Secondary Issue: No Error Handling for Missing Audio**

When audio file doesn't exist:
- DaVinci provider tries to download as URL
- Gets "Invalid URL" error
- Error not surfaced to user clearly
- AI says "✅ Audio successfully added!" despite failure

---

## 🎯 Investigation Priorities

### **Priority 1: Why isn't generate_speech being called?**

**Actions:**
1. Read tool definition for `generate_speech`
2. Compare to working tools like `generate_video`
3. Check system prompt for speech instructions
4. Test if tool is registered correctly
5. Test ElevenLabs directly to verify it works

### **Priority 2: Does ElevenLabs actually work?**

**Actions:**
1. Create standalone test script
2. Call ElevenLabs API directly
3. Verify file is saved to disk
4. Verify file path is correct

### **Priority 3: Does AudioAgent work?**

**Actions:**
1. Create standalone test script
2. Call AudioAgent.generate_speech()
3. Verify it calls ElevenLabs
4. Verify memory storage
5. Verify VideoAgent can query it

### **Priority 4: Does ffmpeg mixing work with real audio?**

**Actions:**
1. Test with existing audio file from yesterday
2. Verify ffmpeg command succeeds
3. Verify output file created
4. Verify Session 83 fix saves to database

---

## 📋 Testing Plan

### **Test 1: ElevenLabs Direct**
```bash
.venv/bin/python manage.py shell
>>> from content.elevenlabs_provider import elevenlabs_provider
>>> result = elevenlabs_provider.text_to_speech("Hello world", "Rachel")
>>> print(result)
>>> # Check if file exists at result['audio_url']
```

### **Test 2: AudioAgent Direct**
```bash
.venv/bin/python manage.py shell
>>> from agents.audio_agent import AudioAgent
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> agent = AudioAgent(user=user)
>>> result = agent.generate_speech("Hello world", "Rachel")
>>> print(result)
```

### **Test 3: AI Assistant Tool Call**
```
In AI Studio:
"Generate speech saying hello world"

Check logs:
tail -n 50 server.log | grep "Executing tool"
```

### **Test 4: Video Mixing with Real Audio**
```
In AI Studio:
"Add the audio file /media/audio/elevenlabs/elevenlabs_speech_0707d893-fd17-4806-b379-9c6fd7450efb.mp3 to my last video"

Check if mixed video appears in gallery
```

---

## 🔧 Known Issues

1. ❌ **AI Assistant not calling generate_speech tool**
   - Location: `core/views_image.py` (system prompt or tool definition)
   - Impact: Critical - no audio can be generated via voice

2. ❌ **No error feedback when audio file missing**
   - Location: `content/davinci_provider.py` (_download_media)
   - Impact: High - user sees success message despite failure

3. ✅ **ffmpeg mixing works** (verified in Session 82)
   - Location: `content/davinci_provider.py` (add_music_to_video)
   - Status: Working

4. ❓ **VideoHistory not created after mixing**
   - Location: `agents/video_agent.py` (add_music_to_video)
   - Status: Fixed in Session 83 but not tested

---

## 📊 Component Health Summary

| Component | Status | Confidence | Notes |
|-----------|--------|------------|-------|
| ElevenLabs Provider | ❓ Unknown | 0% | Never executed |
| AI Assistant Tool Call | ❌ Broken | 100% | Not calling generate_speech |
| AudioAgent | ❓ Unknown | 0% | Never executed |
| VideoAgent | ⚠️ Partial | 60% | Works but fails on missing audio |
| DaVinci Provider | ✅ Works | 90% | ffmpeg confirmed working |
| Frontend | ✅ Works | 95% | No issues found |
| Database | ✅ Works | 100% | No issues found |

---

## 🚀 Next Steps

1. **Read generate_speech tool definition** - Understand why GPT isn't calling it
2. **Test ElevenLabs directly** - Verify the provider works
3. **Test AudioAgent directly** - Verify agent integration works
4. **Fix AI Assistant tool calling** - Make GPT actually use the tool
5. **Test complete workflow** - Verify end-to-end functionality

---

**This diagnostic will be updated as we investigate each component.**

**Last Updated:** Session 83 - November 13, 2025 (Morning)

# Session 495 Handoff: AI Assistant Focus

**Date:** December 18, 2025
**Focus:** AI Assistant Formatting & TTS Improvements
**Priority:** User Experience Polish

---

## Overview

All 66 services are now connected (100%). Session 495 focuses on polishing the main AI Assistant experience with:
1. **Response Formatting Issues** - Clean up markdown rendering and layout
2. **TTS (Text-to-Speech) Issues** - Fix "Speak" functionality behavior

---

## Current TTS Implementation (Session 483)

### Architecture

```
User clicks "Speak" → speak_text() API → TTSTextOptimizer → ElevenLabs API → Audio playback
```

### Key Files

| File | Purpose |
|------|---------|
| `core/services/tts_optimizer.py` | Smart TTS optimization (summarization, chunking) |
| `core/views_audio.py` | `speak_text()` API endpoint (lines 289-449) |
| `ai_image_studio.html` | Frontend speak button handler (lines 29754-29759) |

### TTS Strategy (from `tts_optimizer.py`)

| Text Length | Strategy | Action |
|-------------|----------|--------|
| Under 2000 chars | DIRECT | Use text as-is |
| 2000-5000 chars | SUMMARIZE | GPT summarizes to ~1500 chars |
| Over 5000 chars | CHUNK | Summarize + split into chunks |

### Current Settings

```python
# Voice Settings (ElevenLabs)
{
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True
}

# Default voice: Rachel (21m00Tcm4TlvDq8ikWAM)
# Model: eleven_flash_v2_5 (fast for chat)
```

---

## Known Issues to Investigate

### 1. TTS "Doing Its Own Thing"

**Reported:** TTS behavior seems unpredictable when using Speak button

**Potential Causes:**
- Summarization changing content unexpectedly
- Chunk playback not sequential
- Audio cutting off or looping
- Wrong text being spoken (data-text attribute issues)

**Investigation Points:**
- Check `data-text` attribute encoding in HTML (line 29571)
- Verify summarization prompt in `tts_optimizer.py` (lines 176-192)
- Test chunk index handling (lines 340-354 in `views_audio.py`)
- Check audio playback state management (frontend)

### 2. Response Formatting Issues

**Location:** Chat message display in `ai_image_studio.html`

**Current Formatters:**
- `formatMarkdown(text)` - Global markdown formatter (line 15766)
- `formatMarkdownContent(text)` - Analysis content formatter (line 32099)

**Potential Issues:**
- Nested markdown not rendering correctly
- Code blocks not displaying properly
- Lists losing formatting
- Agent response structure not preserved

---

## Uncommitted Changes (Related to AI Assistant)

There are uncommitted changes that should be reviewed:

### 1. `core/prompts/registry.py` (+14 lines)

Added Session 483 source attribution guidance:
```python
## Session 483: Source Attribution for Trending Information
- Include source links when spider data provides URLs
- Format sources properly: [Article Title](URL)
- Add a "Sources" section at the end of trend responses
- Credit the spider source
```

### 2. `core/services/proactive_intelligence.py` (+92/-39 lines)

Fixed SpiderData field references:
- `fetched_at` → `created_at`
- `category` → filtering by `spider_name`
- `item.title` → extract from `raw_data.items`
- Added URL extraction for sources

### 3. `core/services/smart_suggestions.py` (+8/-8 lines)

Minor field reference fixes similar to proactive_intelligence.

### 4. `core/services/tts_optimizer.py` (NEW - untracked)

Complete TTS optimization service (306 lines):
- Smart text cleaning (remove markdown for speech)
- GPT-powered summarization for long text
- Natural break point chunking
- Strategy selection (DIRECT/SUMMARIZE/CHUNK)

---

## Quick Start for Session 495

### 1. Review and Commit Pending Changes

```bash
# See all pending changes
git status

# Review TTS optimizer (new file)
cat core/services/tts_optimizer.py

# Commit pending AI Assistant improvements
git add core/services/tts_optimizer.py core/prompts/registry.py \
        core/services/proactive_intelligence.py core/services/smart_suggestions.py
git commit -m "feat(Session 483): TTS optimizer + source attribution"
```

### 2. Test TTS Functionality

```bash
# Start services
make start && make celery

# Open AI Studio
open http://localhost:8000/ai-studio/

# Test steps:
# 1. Ask a question in chat
# 2. Wait for response
# 3. Click "Speak" button on response
# 4. Note any issues with:
#    - Audio quality
#    - Content accuracy (is it reading the right thing?)
#    - Summarization behavior
#    - Playback controls
```

### 3. Debug TTS Issues

```bash
# Check TTS API logs
tail -f /tmp/daphne.log | grep -i tts

# Test TTS endpoint directly
curl -X POST http://localhost:8000/api/tts/speak/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test."}' \
  | jq .

# Check ElevenLabs API key
python -c "from django.conf import settings; print(settings.EXTERNAL_API_KEYS.get('ELEVENLABS_API_KEY', '')[:10])"
```

---

## Frontend TTS Handler (Reference)

Location: `ai_image_studio.html` lines 29754-29800

```javascript
// Session 458 + 483: Speak button with smart TTS
speakBtn.addEventListener('click', async (e) => {
    const text = e.target.dataset.text;
    const btn = e.target;

    // If already speaking, stop
    if (window.currentSpeakingAudio) {
        window.currentSpeakingAudio.pause();
        window.currentSpeakingAudio = null;
        btn.innerHTML = '🔊 Speak';
        return;
    }

    btn.innerHTML = '⏳ Loading...';

    // Call TTS API
    const response = await authenticatedFetch('/api/tts/speak/', {
        method: 'POST',
        body: JSON.stringify({ text })
    });

    // Play audio...
});
```

---

## Formatting Investigation Points

### Chat Message Structure

The speak button stores text in `data-text` attribute:
```html
<button class="speak-btn"
        data-text="${originalContent.replace(/"/g, '&quot;').replace(/\n/g, ' ')}">
    🔊 Speak
</button>
```

**Potential Issue:** Newlines replaced with spaces might affect readability

### Markdown Formatter

```javascript
function formatMarkdown(text) {
    // Convert bold **text**
    // Convert italic *text*
    // Convert code `text`
    // Convert links [text](url)
    // ... etc
}
```

**Check:** Is markdown being double-processed or stripped incorrectly?

---

## Recommended Session 495 Tasks

### Priority 1: TTS Behavior

1. **Audit speak button flow** - Verify correct text is captured
2. **Test summarization** - Check GPT summary quality and accuracy
3. **Fix chunk playback** - Ensure sequential chunk playing works
4. **Improve audio controls** - Add progress indicator, stop button reliability

### Priority 2: Formatting

1. **Identify specific formatting issues** - Get user examples
2. **Fix markdown rendering** - Ensure proper nested element handling
3. **Improve code block display** - Syntax highlighting if missing
4. **Clean up agent response structure** - Consistent formatting

### Priority 3: Testing

1. **Create TTS test cases** - Short, medium, long text
2. **Test with different voices** - Default vs cloned voice
3. **Test chunked playback** - Very long responses
4. **Verify error handling** - API failures, timeouts

---

## System Status

| Metric | Value |
|--------|-------|
| Services | 66 connected (100%) |
| Agent Conversations | Fixed (Session 494) |
| TTS Optimizer | Implemented but untested |
| Spiders | 67 |
| Agents | 41 |

---

## Key Documentation

- **TTS Implementation:** `core/services/tts_optimizer.py`
- **TTS API:** `core/views_audio.py` (lines 289-449)
- **Prompts:** `core/prompts/registry.py`
- **Frontend Chat:** `ai_image_studio.html` (lines 29500-29800)

---

**Ready to polish the AI Assistant experience!**

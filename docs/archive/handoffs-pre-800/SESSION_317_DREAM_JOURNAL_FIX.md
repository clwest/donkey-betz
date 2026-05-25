# Session 317: Dream Journal Fix + Token Limit Adjustment

**Date:** December 2, 2025
**Focus:** Fix Agent Dreams generating empty content

---

## Summary

Session 317 fixed the Dream Journal feature that was showing stale data (19+ hours old) and generating empty dream content. The root cause was the same as Session 315's Agent Conversations fix: GPT-5 reasoning models require higher token limits because they allocate tokens to both internal reasoning AND visible output.

---

## Problems Identified

### 1. Stale Dream Data
Dream Journal in the Agents/Social tab showed dreams from ~19 hours ago.

**Root Cause:** Celery was idle during the 4-hour break, so `generate_agent_dreams` task didn't run.

### 2. Empty Dream Content
When dreams were generated, many had:
- Empty content (just `""`)
- Generic "Creative Thought" titles (fallback when content is empty)

**Root Cause:** Token limits too low for GPT-5 reasoning models:
- `max_completion_tokens=600` for dream content (not enough)
- `max_completion_tokens=200` for title generation (not enough)

---

## Solution Applied

Updated `core/tasks.py` `generate_agent_dreams()` function:

### Before (Session 247 implementation):
```python
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=600,  # Too low for reasoning
)

title_response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=200,  # Too low for reasoning
)
```

### After (Session 317 fix):
```python
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=1000,  # Higher for GPT-5 reasoning
)

title_response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[...],
    max_completion_tokens=500,  # Higher for GPT-5 reasoning
)
```

---

## GPT-5 Reasoning Model Token Allocation

GPT-5 reasoning models (gpt-5, gpt-5-mini, gpt-5-nano) use `max_output_tokens` or `max_completion_tokens` differently than standard models:

| Model Type | Token Allocation |
|------------|------------------|
| Standard (gpt-4, etc.) | All tokens go to visible output |
| Reasoning (gpt-5-*) | Tokens split between internal reasoning + visible output |

**Solution:** Always use higher token limits (1000-2000) for reasoning models to ensure room for both reasoning AND visible output.

### Quick Reference for Token Limits:
| Use Case | Recommended Tokens |
|----------|-------------------|
| Short generation (titles) | 500+ |
| Medium generation (dreams, comments) | 1000+ |
| Long generation (conversations, reports) | 1500-2000+ |

---

## Verification Results

### Before Fix:
- Total dreams: 6
- All dreams: ~19.9h old
- Content: Empty or minimal
- Titles: All "Creative Thought" (fallback)

### After Fix:
- Total dreams: 25+ (16 before, 9+ new)
- New dreams: Real-time generation
- Content: Rich, creative, substantive
- Titles: ~70% unique creative titles, ~30% fallback

### Example Dreams Generated:
1. **"Atomic Content Growth Engine"** - BrandIdentityAgent prediction about AI content repurposing
2. **"Neon Prompt Betting Exchange"** - BookmakerAgent creative parlor concept
3. **"Tactile Sonic Physics Engine"** - AudioGenerationAgent what-if about haptic audio
4. **"Sonic Mycelium Network Conductor"** - AudioAgent mashup of audio and mycology

---

## Files Modified

| File | Changes |
|------|---------|
| `core/tasks.py:4117-4126` | Increased dream content tokens from 600 to 1000 |
| `core/tasks.py:4137-4144` | Increased title generation tokens from 200 to 500 |

---

## Related Sessions

- **Session 315:** Fixed Agent Conversations (same root cause - token limits)
- **Session 316:** Verified Agent Learning System
- **Session 247:** Original Agent Dreams implementation

---

## Celery Beat Schedule

Dream generation runs via Celery Beat:

```python
'agent-dream-cycle': {
    'task': 'core.tasks.generate_agent_dreams',
    'schedule': crontab(minute='*/15'),  # Every 15 minutes
}
```

To trigger manually:
```python
from core.tasks import generate_agent_dreams
result = generate_agent_dreams()
print(result)  # {'dreams_generated': X, 'agents_dreaming': Y, ...}
```

---

## Testing

```bash
# Start the platform
make start && make celery

# Access Dream Journal
open http://localhost:8000/ai-studio/
# Navigate to Agents > Social > Dream Journal

# Trigger fresh dreams manually
.venv/bin/python manage.py shell -c "
from core.tasks import generate_agent_dreams
result = generate_agent_dreams()
print(f'Generated: {result[\"stats\"][\"dreams_generated\"]} dreams')
"
```

---

## Status

- Dream Journal now shows fresh, creative dreams
- Dreams have substantive content instead of empty strings
- ~70% of dreams get unique creative titles
- System verified working with Celery Beat schedule

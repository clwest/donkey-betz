# Session 628: Cross-Session Memory + Content Calendar

**Date:** December 30, 2025
**Previous Session:** 627 (Celery Beat Sync + Dream Quality Fix)
**Focus:** Hybrid feature combining personalization with content visibility

---

## Executive Summary

Implemented two complementary features that integrate:
1. **Cross-Session Memory** - PA actively uses stored preferences in responses
2. **Content Calendar** - UI to view scheduled/past autonomous content

The integration point: Content generation uses learned preferences, and the calendar shows personalized recommendations.

---

## What Was Built

### 1. MemoryContextService (`core/services/memory_context_service.py`)

A new service that builds memory context for PA prompt injection:

```python
from core.services.memory_context_service import get_memory_context_service

service = get_memory_context_service(user)
context = service.get_prompt_context(user)  # For PA prompts
prefs = service.get_content_preferences(user, channel)  # For content generation
```

**Key Features:**
- Retrieves preferences, goals, decisions from `UserMemoryContext`
- Applies decay weighting: `e^(-age_days / 21)` (Session 601 formula)
- Recent memories weighted higher than old ones
- Limits context to ~500 tokens
- 5-minute cache to reduce DB hits

**Decay Weight Examples:**
| Age (days) | Weight |
|------------|--------|
| 0 | 1.0 |
| 7 | ~0.72 |
| 21 | ~0.37 |
| 42 | ~0.14 |

### 2. PA Integration

Modified `core/personal_ai_assistant_enhanced.py` (line ~7077):

```python
# Session 628: Build comprehensive context using MemoryContextService
memory_context_service = get_memory_context_service(self.user)
memory_context = memory_context_service.get_prompt_context(self.user)
```

The PA now receives context like:
```
Profile:
- Role: Software Engineer
- Communication: prefers concise responses
- Decision style: uses pros/cons analysis
- Active projects: AI Platform, Podcast

Preferences:
- Prefers pixar visual style for content
- Uses Rachel voice for audio

Goals:
- Launch MVP by Q1 2025
```

### 3. Content Calendar API (`core/views_content_calendar.py`)

Four endpoints for calendar data:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/content-calendar/` | GET | Main calendar data (channels, upcoming, past, topics) |
| `/api/content-calendar/upcoming/` | GET | Next 10 scheduled items with preferences |
| `/api/content-calendar/history/` | GET | Past content with performance metrics |
| `/api/content-calendar/reschedule/` | POST | Change schedule date for a channel |

**Main Response Shape:**
```json
{
  "success": true,
  "channels": [...],
  "upcoming": [{"channel_name", "next_due", "preferences_applied"}],
  "past_30_days": [{"title", "views", "performance_score"}],
  "top_topics": [...],
  "calendar_events": [...],
  "stats": {"total_channels", "active_channels", "total_episodes", "avg_performance_score"},
  "user_preferences": {...}
}
```

### 4. Content Calendar UI (`ai_core/templates/components/panels/content_calendar_panel.html`)

New "Calendar" tab in AI Studio with:

- **Stats Dashboard** - Active channels, total episodes, upcoming count, avg performance
- **Upcoming Content List** - Next scheduled items with applied preferences badges
- **Recent Content List** - Published content with views, engagement, retention metrics
- **Channels Overview** - All channels with status, episode count, next due date
- **Top Performing Topics** - Best topics ranked by performance
- **User Preferences** - Current preferences applied to content

### 5. Preference Integration in Content Generation

Modified `core/agents/autonomous_content_studio_coordinator.py`:

```python
# Session 628: Get user preferences for personalization
memory_service = get_memory_context_service(channel.user)
user_prefs = memory_service.get_content_preferences(channel.user, channel)

# Apply user preferences to visual style and voice
visual_style = user_prefs.get('visual_style') or channel.visual_style
voice_id = user_prefs.get('voice_id') or channel.voice_id
```

Generated content now includes preferences in the prompt, ensuring personalized output.

---

## Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `core/services/memory_context_service.py` | ~330 | Memory injection service |
| `core/views_content_calendar.py` | ~350 | Calendar API endpoints |
| `ai_core/templates/components/panels/content_calendar_panel.html` | ~450 | Calendar UI |

## Files Modified

| File | Change |
|------|--------|
| `core/personal_ai_assistant_enhanced.py` | Added import + memory context injection |
| `core/urls.py` | Added 4 calendar API routes |
| `ai_core/templates/ai_image_studio.html` | Added Calendar tab + panel include |
| `core/agents/autonomous_content_studio_coordinator.py` | Added preference retrieval + application |

---

## Testing

### Test Calendar API
```bash
# Start platform
make start

# Test API (requires login cookie)
curl http://localhost:8000/api/content-calendar/
```

### Test UI
```bash
open http://localhost:8000/ai-studio/
# Click the "📅 Calendar" tab
```

### Test Memory Context
```bash
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django
django.setup()
from django.contrib.auth import get_user_model
from core.services.memory_context_service import MemoryContextService

User = get_user_model()
user = User.objects.first()
service = MemoryContextService(user)
print(service.get_prompt_context(user))
"
```

---

## Integration with Existing Systems

### Uses These Existing Models:
- `UserMemoryContext` - Flexible memory storage (preference, goal, decision types)
- `EnhancedUserProfile` - Static profile data (role, communication style)
- `ContentChannel` - Autonomous content channels
- `ChannelEpisode` - Published content with metrics
- `TopicPerformance` - Learning data about topic performance

### Leverages Existing Services:
- `UnifiedMemoryManager` - For fallback memory retrieval
- Session 601 weighted learning formula - For decay weighting

---

## Roadmap Status Update

| Item | Status |
|------|--------|
| Cross-session memory | ✅ DONE (Session 628) |
| Content Calendar | ✅ DONE (Session 628) |
| Profile Follow-ups | Pending |
| Agent personalities | Pending |
| Calendar grid view | Pending (list view done) |

---

## Next Steps for Session 629

1. **Polish Calendar** - Add month grid view (currently list-only)
2. **Test with Real Data** - Create a content channel and verify preferences flow
3. **Profile Follow-ups** - Deeper interview questions for personalization
4. **Monitor Reality Score** - Should still be ~97%+

# Session 630-633: Episode Script, Content Viewer, Generate Now, Error Handling

**Date:** December 30, 2025
**Previous Session:** 629 (Testing Validation)
**Focus:** Add script field, Episode Content Viewer UI, Generate Now button, and graceful error handling

---

## Session 630: Script Field Implementation

### Problem Solved

The Content Studio was generating episodes through 3-agent debates, but the actual generated content/script wasn't being stored anywhere persistent.

### Implementation

**1. Database Change:**
Added `script` TextField to `ChannelEpisode` model via migration `0139`.

**2. Code Updates (3 locations):**
- `core/tasks.py` - Main content generation (~line 13182)
- `core/tasks.py` - Narrative shift episodes (~line 14336)
- `core/agents/autonomous_content_studio_coordinator.py` (~line 639)

---

## Session 631: Episode Content Viewer

### New Features

**1. Episode Detail API Endpoint**
```
GET /api/content-calendar/episode/<uuid>/
```
Returns full episode details including:
- Script content
- 3-agent debate transcript
- Performance metrics
- Channel context

**2. Episode Detail Modal**
- Click any episode in Recent Content list to open modal
- Shows script/generated content with syntax highlighting
- Displays 3-agent debate (Topic Miner, Contrarian, Analyst)
- Shows performance metrics and channel settings

**3. Interactive Episode Cards**
- Hover effects on episode cards
- "Details" button for quick access
- Click anywhere on card to open modal

---

## Session 632: Generate Now Button

### New Features

**1. Generate Content API Endpoint**
```
POST /api/content-calendar/generate/<uuid>/
```
Triggers immediate content generation for a channel, bypassing Celery Beat schedule.

**2. Generate Now Button on Channel Cards**
- Each active channel shows a "Generate Now" button
- Disabled for paused/inactive channels
- Shows loading state during generation trigger
- Toast notification on success/failure
- Button changes to "Refresh to see" after triggering

**3. UX Features**
- Loading spinner while API call is made
- Success toast notification
- Error handling with retry capability
- Button state transitions (primary → success → info)

---

## Session 633: Graceful Error Handling in Debate Display + Root Cause Fix

### Problem Solved

Some ContentDebate records contained error messages from failed agent executions (e.g., "Error: name 'user' is not defined"). These raw error strings were being displayed in the Episode Detail Modal, confusing users.

### Implementation

**1. UI Error Handling:**
Added `formatDebateArgument()` helper function that:
- Returns "No argument provided" (muted italic) for null/undefined arguments
- Detects error messages (starting with "Error:", containing "is not defined" or "Traceback") and shows a user-friendly warning
- Otherwise truncates to 200 characters and escapes HTML

**UI Result:**
- **Before:** `Error: name 'user' is not defined`
- **After:** `⚠️ Agent encountered an error during execution`

**2. Root Cause Fix in generate_content_for_channel():**
The task was using old debate records with errors instead of creating new ones. Fixed in `core/tasks.py` (line 13044):

```python
# Before: Would find old debates with errors
recent_debate = ContentDebate.objects.filter(channel=channel).order_by('-debate_date').first()

# After: Only finds debates created during this task run
task_start_time = timezone.now() - timezone.timedelta(minutes=5)
recent_debate = ContentDebate.objects.filter(
    channel=channel,
    created_at__gte=task_start_time
).order_by('-debate_date').first()
```

**Backend Result:**
New content generation creates fresh debates with actual agent responses:
- TopicMiner: Real trending topic analysis
- Contrarian: Real saturation/opportunity analysis
- Analyst: Real performance predictions

**3. Coordinator Direct Debate Fix:**
The coordinator wasn't reliably calling its `initiate_content_debate` tool via GPT. Fixed by adding direct tool invocation in `autonomous_content_studio_coordinator.py`:

```python
# Session 633: Direct tool call for initiate_content_debate action
# This bypasses GPT to ensure reliable debate creation
if context.get('action') == 'initiate_content_debate' and context.get('channel_id'):
    logger.info(f"🎥 [SESSION 633] Direct debate initiation for channel {context['channel_id']}")
    tool_input = {'channel_id': context['channel_id']}
    debate_result = self._initiate_content_debate(tool_input)
    # ... return result
```

**Final Result:**
- `Proposed By: AutonomousContentStudioCoordinator` (not fallback!)
- `Is Fallback: False`
- Proper 3-agent debate with synthesized decision reasoning

**4. Script Extraction Fix:**
The ChannelEpisode.script field was only storing a summary message (42 chars) instead of actual script content. Fixed by extracting script from SeriesEpisode:

```python
# Session 633: Extract actual script from SeriesEpisode
from core.models_ai_series import AISeries, SeriesEpisode
recent_series = AISeries.objects.order_by('-created_at').first()
if recent_series:
    series_episode = SeriesEpisode.objects.filter(series=recent_series).order_by('-created_at').first()
    if series_episode and series_episode.script:
        actual_script = series_episode.script  # 1544 chars of real content
```

**Script Result:**
- **Before:** 42 chars - "Created educational series with 1 episodes"
- **After:** 1544 chars - Full episode script with host intro, content, and flow

**5. Expandable Text UI:**
Updated `formatDebateArgument()` to show 500 chars with expandable "[Show more/less]" toggle:
- Truncates to 500 chars initially (was 200)
- Adds clickable "[Show more]" link to expand
- Full content displayed in scrollable container (max-height: 300px)
- "[Show less]" collapses back to truncated view
- Same expandable format applied to reasoning display

---

## Files Modified

| File | Change |
|------|--------|
| `core/models_autonomous_studio.py` | Added `script` TextField |
| `core/migrations/0139_session_630_add_episode_script.py` | New migration |
| `core/tasks.py` | Updated 2 episode creation locations + fixed debate query + explicit tool prompt + script extraction |
| `core/agents/autonomous_content_studio_coordinator.py` | Updated 1 episode creation + direct debate initiation |
| `core/views_content_calendar.py` | Added episode detail + generate views |
| `core/urls.py` | Added episode detail + generate URL routes |
| `ai_core/templates/components/panels/content_calendar_panel.html` | Modal, click handlers, Generate Now button, formatDebateArgument() with expandable text |

---

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/content-calendar/` | GET | Main calendar data |
| `/api/content-calendar/episode/<uuid>/` | GET | Episode details with script |
| `/api/content-calendar/generate/<uuid>/` | POST | Trigger content generation |
| `/api/content-calendar/upcoming/` | GET | Upcoming scheduled content |
| `/api/content-calendar/history/` | GET | Past content history |
| `/api/content-calendar/reschedule/` | POST | Reschedule content |

---

## Testing

Verified:
- Migration applied successfully
- Episode detail API returns script content
- Debate information included when available
- Modal opens and displays content correctly
- Generate API triggers Celery task
- Button states update correctly
- Error messages in debate data displayed gracefully (Session 633)
- New content generation creates fresh debates with real agent data (Session 633)
- Coordinator creates debates directly (not via GPT tool call) - `Is Fallback: False`
- Script extraction from SeriesEpisode verified: 1544 chars stored (Session 633)
- Expandable text UI with "[Show more/less]" toggle working (Session 633)

---

## Related Sessions

| Session | Feature |
|---------|---------|
| 633 | Graceful error handling in debate display |
| 628 | Cross-Session Memory + Content Calendar |
| 629 | Testing Validation |
| 466 | Autonomous Content Studio original implementation |

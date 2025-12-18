# Option 3: Frontend Intelligence Surfacing

**Priority:** 3 (Third)
**Status:** Not Started
**Estimated Effort:** Medium (2-3 sessions)

---

## Goal

Make the sophisticated backend intelligence features visible and usable to end users in the web interface.

---

## Problem Statement

The platform has powerful intelligence features that users can't see:
- Smart Suggestions exist but aren't displayed as buttons
- Task Memory tracks multi-step tasks but no UI shows progress
- Reference Resolution works but users don't know it
- Proactive Intelligence generates alerts but they're not surfaced
- Knowledge Attribution tracks sources but isn't shown
- Agent explanations are available but not displayed

---

## Existing Backend Services

| Service | File | Status | Frontend |
|---------|------|--------|----------|
| Smart Suggestions | `smart_suggestions.py` | Working | None |
| Task Memory | `task_memory.py` | Working | None |
| Reference Resolver | `reference_resolver.py` | Working | None |
| Proactive Intelligence | `proactive_intelligence.py` | Working | None |
| Knowledge Attribution | `base_agent.py` | Working | None |
| Streaming Progress | `streaming_progress.py` | Working | Partial |

---

## Deliverables

### 1. Smart Suggestion Buttons

**Requirements:**
- [ ] After each AI response, show 2-4 relevant follow-up buttons
- [ ] Buttons based on context:
  - After research: "Create content", "Save to project", "Deep dive"
  - After image: "Create variations", "Upscale", "Make video"
  - After video: "Add music", "Add captions", "Trim"
- [ ] Clicking button sends that text to chat
- [ ] Buttons animate in smoothly
- [ ] Mobile-friendly layout

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ [AI Response about AI trends...]                    │
│                                                     │
│ Suggested actions:                                  │
│ [Create infographic] [Deep dive on GPT-5] [Save]   │
└─────────────────────────────────────────────────────┘
```

**Implementation:**
- API returns `suggestions` array with each response
- Frontend renders as clickable chips/buttons
- CSS transitions for smooth appearance

---

### 2. Task Progress Sidebar

**Requirements:**
- [ ] Collapsible sidebar showing active multi-step tasks
- [ ] For each task:
  - Task name/description
  - Current step (e.g., "Step 2 of 5")
  - Progress bar
  - Step details (what's happening now)
  - Estimated time remaining
- [ ] Task history (completed tasks)
- [ ] Click to view task details
- [ ] Cancel button for in-progress tasks

**UI Mockup:**
```
┌──────────────────────────┐
│ ACTIVE TASKS          ▼ │
├──────────────────────────┤
│ Brand Identity Package   │
│ ████████░░ 80%          │
│ Step 4/5: Creating logo  │
│ ~2 min remaining        │
├──────────────────────────┤
│ YouTube Thumbnail Series │
│ ██░░░░░░░░ 20%          │
│ Step 1/5: Research       │
└──────────────────────────┘
```

**Implementation:**
- WebSocket for real-time progress updates
- Task state persisted in `task_memory.py`
- Progress events via `streaming_progress.py`

---

### 3. Explainability Panel

**Requirements:**
- [ ] "Why?" button on AI responses
- [ ] Clicking shows:
  - Which agents were involved
  - Which spider sources provided data
  - Confidence score
  - Key knowledge items used
  - Decision reasoning
- [ ] Collapsible/expandable
- [ ] Links to original sources when available

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ [AI Response: "AI trends show GPT-5 is trending..."]│
│                                            [Why? ▼] │
├─────────────────────────────────────────────────────┤
│ SOURCES USED:                                       │
│ • hackernews (45 min ago) - "GPT-5 released..."    │
│ • techcrunch (2h ago) - "OpenAI announces..."      │
│ • reddit/MachineLearning - Discussion thread       │
│                                                     │
│ AGENTS INVOLVED:                                    │
│ • ResearchAgent (primary)                           │
│ • TrendAnalysisAgent (supporting)                   │
│                                                     │
│ CONFIDENCE: 87%                                     │
└─────────────────────────────────────────────────────┘
```

**Implementation:**
- Return `KnowledgeAttribution` with responses
- Frontend renders expandable panel
- Cache explanations for performance

---

### 4. Proactive Alert Bar

**Requirements:**
- [ ] Non-intrusive alert bar at top of chat
- [ ] Shows relevant proactive intelligence:
  - "3 new job opportunities match your profile"
  - "Crypto market alert: BTC down 15%"
  - "Trending topic in your domain: AI Safety"
- [ ] Click to expand/act
- [ ] Dismiss button
- [ ] Configurable (can turn off)
- [ ] Different colors by urgency (info/warning/critical)

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ 🔔 3 new opportunities match your skills  [View] [×]│
└─────────────────────────────────────────────────────┘
│                                                     │
│ [Normal chat interface below]                       │
```

**Implementation:**
- Poll `/api/proactive/alerts/` every 30 seconds
- Or use WebSocket for real-time
- Store dismissed alerts to not re-show

---

### 5. Reference Resolution Indicator

**Requirements:**
- [ ] When user says "it", "that", "the first one" - show what was resolved
- [ ] Small indicator showing resolved reference
- [ ] Clickable to see full resolution logic
- [ ] Helps users understand what AI interpreted

**UI Mockup:**
```
User: "Make it bigger"
      ↳ "it" → [Image #123: Cyberpunk logo]

AI: "I'll upscale the cyberpunk logo..."
```

**Implementation:**
- Reference resolver returns resolution metadata
- Frontend shows subtle inline indicator
- Tooltip with full context on hover

---

### 6. Live Agent Activity Indicator

**Requirements:**
- [ ] When agents are working, show which ones
- [ ] Animated indicator during processing
- [ ] Shows agent name and what it's doing
- [ ] Multiple agents shown for Hive Mind

**UI Mockup:**
```
┌─────────────────────────────────────────────────────┐
│ 🤖 Working...                                       │
│ ImageAgent is generating your logo                  │
│ [████████░░░░░░░░░░░░] 40%                         │
└─────────────────────────────────────────────────────┘
```

**Implementation:**
- Stream agent activity via WebSocket
- Show agent avatar/icon
- Progress bar when available

---

## Technical Implementation

### Backend API Enhancements

```python
# Enhanced chat response structure
{
    "response": "AI response text...",
    "suggestions": [
        {"text": "Create infographic", "action": "create"},
        {"text": "Deep dive", "action": "research"}
    ],
    "attribution": {
        "spider_sources": ["hackernews", "techcrunch"],
        "agents_used": ["ResearchAgent"],
        "confidence": 0.87,
        "knowledge_items": [...]
    },
    "task": {
        "id": "task-123",
        "name": "Brand Package",
        "step": 4,
        "total_steps": 5,
        "progress": 0.8
    },
    "reference_resolutions": [
        {"pronoun": "it", "resolved_to": "Image #123"}
    ]
}
```

### New API Endpoints

```python
GET  /api/proactive/alerts/           # Current alerts for user
POST /api/proactive/alerts/<id>/dismiss/
GET  /api/tasks/active/               # Active tasks
GET  /api/tasks/<id>/progress/        # Task progress
POST /api/tasks/<id>/cancel/          # Cancel task
```

### Frontend Components

1. **SuggestionChips** - Clickable suggestion buttons
2. **TaskSidebar** - Collapsible task list
3. **ExplainabilityPanel** - Source/agent display
4. **ProactiveAlertBar** - Top alert banner
5. **ReferenceIndicator** - Inline reference display
6. **AgentActivityIndicator** - Processing status

### WebSocket Events

```javascript
// Events to handle
{
    type: "task_progress",
    data: { task_id, step, progress, status }
}
{
    type: "agent_activity",
    data: { agent_name, action, progress }
}
{
    type: "proactive_alert",
    data: { id, message, urgency, domain }
}
```

---

## Implementation Steps

### Phase 1: Smart Suggestions
1. [ ] Modify chat API to return suggestions
2. [ ] Create SuggestionChips component
3. [ ] Wire click handlers
4. [ ] Style and animate

### Phase 2: Task Progress
1. [ ] Create TaskSidebar component
2. [ ] Add WebSocket for progress updates
3. [ ] Integrate with task_memory service
4. [ ] Add cancel functionality

### Phase 3: Explainability
1. [ ] Add attribution to API responses
2. [ ] Create ExplainabilityPanel component
3. [ ] Add "Why?" button to messages
4. [ ] Link to sources

### Phase 4: Proactive Alerts
1. [ ] Create ProactiveAlertBar component
2. [ ] Add polling/WebSocket
3. [ ] Implement dismiss functionality
4. [ ] Add settings toggle

### Phase 5: Polish
1. [ ] Reference indicators
2. [ ] Agent activity display
3. [ ] Mobile optimization
4. [ ] Performance testing

---

## Success Criteria

1. **Suggestions:** Users click suggestion buttons at least 20% of the time
2. **Task Progress:** Multi-step tasks show live progress
3. **Explainability:** Users can see sources for any AI response
4. **Proactive:** Relevant alerts appear within 30 seconds
5. **Performance:** No noticeable lag from new features

---

## Dependencies

- Existing services: smart_suggestions, task_memory, reference_resolver
- WebSocket infrastructure (Django Channels)
- May benefit from Option 1 (Autonomous Dashboard) for proactive alerts

---

## Notes

- Keep UI non-intrusive - intelligence should enhance, not overwhelm
- Mobile-first for sidebar/alerts
- Consider user preferences for verbosity
- A/B test suggestion click rates

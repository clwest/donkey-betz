# Session 663: SystemIntelligenceAgent - Platform Health Architecture

**Date:** January 5, 2026
**Focus:** Scalable system awareness for the Personal Assistant
**Status:** COMPLETE - All 6 commits applied

---

## Problem Statement

When users asked the PA about system metrics like "Pending Review: 96%", the PA:
1. Didn't understand what the metric meant (alarming users unnecessarily)
2. Didn't know where to look for context (Intelligence section)
3. Required hardcoded keywords to inject system data
4. Gave **hypothetical responses** about "a system" rather than THIS platform

The quick fix (keyword hacking) was not scalable - new metrics would require code changes.

---

## Solution: SystemIntelligenceAgent Architecture

Created a dedicated agent for platform health and attention monitoring:

```
User asks "what needs attention?"
    ↓
PA (PersonalAssistantAgent)
    ↓
AgentRouter (semantic routing via routing_config.py)
    ↓
SystemIntelligenceAgent
    ↓
SystemStateAggregator
    ↓
Rich context with explanations + recommendations
```

### Key Design Principles

1. **Single source of truth** - Queries SystemStateAggregator for all attention items
2. **Rich explanations** - Each item includes explanation, recommendations, severity
3. **Scalable** - New attention items automatically work (no keyword hacking)
4. **Actionable** - Provides specific recommendations for each issue
5. **Learning integrated** - All learning hooks connected to collective intelligence

---

## Implementation

### 1. Enhanced AttentionItem Dataclass

**File:** `core/services/system_state_aggregator.py`

Added new fields to AttentionItem:

```python
@dataclass
class AttentionItem:
    id: str
    section: str        # 'command_center', 'autonomous', 'research'
    category: str       # 'alert', 'health', 'overdue', 'stale', etc.
    priority: int       # 1-100 (higher = more urgent)
    title: str
    summary: str
    action_url: str = ''
    # Session 663: New fields
    explanation: str = ''           # What this metric means in plain English
    recommended_action: str = ''    # What the user can do about it
    severity: str = 'info'          # 'info', 'warning', 'critical'
    location: str = ''              # UI location: "Intelligence > Decisions"

    def to_rich_context(self) -> str:
        """Format as rich context string for agent consumption."""
```

### 2. Created SystemIntelligenceAgent

**File:** `core/agents/system_intelligence_agent.py` (NEW - ~408 lines)

Agent with two tools:
- `get_system_attention` - Get all current attention items with rich context
- `get_item_details` - Get detailed information about a specific item

The agent:
- Queries SystemStateAggregator for attention items
- Groups by severity (critical → warnings → info)
- Interprets what metrics mean (e.g., "96% Pending Review is normal")
- Provides actionable recommendations

**Critical: Execute signature must match BaseAgent:**
```python
def execute(
    self,
    task: str,
    context: Dict[str, Any] = None,
    scifi_context: Dict[str, Any] = None,  # Required by AgentRouter
    spider_context: Dict[str, Any] = None   # Required by AgentRouter
) -> AgentResult:
```

### 3. Registered in AgentRouter

**File:** `core/agent_router.py`

Added import and AGENT_MAP entry:
```python
from core.agents.system_intelligence_agent import SystemIntelligenceAgent

AGENT_MAP = {
    ...
    "SystemIntelligenceAgent": SystemIntelligenceAgent,
}
```

### 4. Added Routing Configuration (CRITICAL)

**File:** `core/agents/routing_config.py` (lines 559-591)

Without this, PA had no way to know to route system questions to the agent!

```python
"SystemIntelligenceAgent": {
    "description": "Check platform health, system status, pending reviews, what needs attention, execution gaps, and attention items. Queries real system data from SystemStateAggregator.",
    "examples": [
        "what needs my attention",
        "what is the system status",
        "tell me about pending review",
        "what's the pending review status",
        "check system health",
    ],
    "keywords": [
        "system status", "platform status", "system health", "health check",
        "what needs attention", "needs attention", "attention items",
        "pending review", "review status", "pending", "backlog",
        "execution gap", "execution status", "draft decisions",
        "catch me up", "what's happening", "system state", "platform state",
        "agent suggestions", "promotable", "stale suggestions",
    ],
    "category": "system",
    "priority": 30,  # High priority - system queries should route here
},
```

### 5. Learning Hooks Integration

**File:** `core/agents/system_intelligence_agent.py`

Added all required learning hooks per `docs/current/LEARNING_SYSTEM.md`:

```python
# Record learning outcome for XP and pattern detection
self._record_learning_outcome(
    result=result,
    task=task,
    context=context,
    spider_data_used=False,
    scifi_context_used=False
)

# Create memory of successful system check
self._create_execution_memory(
    result=result,
    task=task,
    memory_type="success",
    importance=0.5
)

# Share knowledge if there are critical issues
if critical_count > 0:
    self._share_knowledge(
        knowledge_type='observation',
        title=f"System Alert: {critical_count} critical items",
        knowledge_value={...},
        confidence=0.9
    )
```

### 6. UI Integration

**File:** `core/views_personal_assistant.py` (lines 491-539)

Updated API to return enhanced fields:
```python
attention_items.append({
    'id': item.id,
    'section': item.section,
    'category': item.category,
    'priority': item.priority,
    'title': item.title[:80],
    'summary': item.summary[:150],
    # Session 663: New enhanced fields
    'severity': getattr(item, 'severity', 'info'),
    'explanation': getattr(item, 'explanation', '')[:300],
    'recommended_action': getattr(item, 'recommended_action', '')[:200],
    'location': getattr(item, 'location', ''),
})
```

**File:** `frontend/src/pages/AssistantPage.tsx`

Updated interface and rendering:
```typescript
interface AttentionItem {
  id: string
  title: string
  summary?: string
  priority: number
  severity: 'critical' | 'warning' | 'info'
  explanation?: string
  recommended_action?: string
  location?: string
}

// Severity-based colors with pulse animation for critical
<span className={cn(
  'h-2 w-2 rounded-full flex-shrink-0',
  item.severity === 'critical' ? 'bg-accent-red animate-pulse' :
  item.severity === 'warning' ? 'bg-accent-amber' : 'bg-accent-green'
)} />
```

### 7. Removed Keyword Hacking

**File:** `core/services/pa_intelligence_enricher.py`

Removed Session 663 keyword additions from SYSTEM_STATE_KEYWORDS.
The proper architecture handles this through agent routing, not keyword injection.

---

## Commits (6 total)

```
8075264f fix(Session 663): Add required execute() parameters to SystemIntelligenceAgent
f246bec0 fix(Session 663): Add SystemIntelligenceAgent to routing config
62ef3d58 feat(Session 663): Connect Needs Attention UI to enhanced attention items
41a060a0 fix(Session 663): Fix AgentResult constructor in SystemIntelligenceAgent
ef0c6294 fix(Session 663): Add learning hooks to SystemIntelligenceAgent
a9c77ded feat(Session 663): Add SystemIntelligenceAgent for platform health monitoring
```

---

## Files Changed

| File | Change |
|------|--------|
| `core/services/system_state_aggregator.py` | Enhanced AttentionItem with new fields |
| `core/agents/system_intelligence_agent.py` | NEW - Agent for system health (~408 lines) |
| `core/agents/__init__.py` | Import + export SystemIntelligenceAgent |
| `core/agent_router.py` | Import + register in AGENT_MAP |
| `core/agents/routing_config.py` | **CRITICAL** - Added routing entry |
| `core/views_personal_assistant.py` | API returns enhanced fields |
| `frontend/src/pages/AssistantPage.tsx` | UI uses severity/explanation/location |
| `core/services/pa_intelligence_enricher.py` | Removed keyword hacking |
| `docs/AGENTS.md` | Added SystemIntelligenceAgent documentation |
| `docs/CAPABILITIES.md` | Updated agent count, added capability row |
| `docs/current/LEARNING_SYSTEM.md` | Updated agent counts 71 → 72 |

---

## Bugs Fixed During Implementation

| Bug | Cause | Fix |
|-----|-------|-----|
| `AgentResult.__init__() got an unexpected keyword argument 'result'` | Used `result=` instead of `message=` | Changed to `message=result_text, data={...}` |
| `SystemIntelligenceAgent.execute() got an unexpected keyword argument 'scifi_context'` | Missing parameters in execute() | Added `scifi_context` and `spider_context` params |
| PA gave hypothetical responses about "a system" | Agent not in routing_config.py | Added full routing entry with keywords/examples |

---

## AttentionItem Severity Levels

| Level | Meaning | Example |
|-------|---------|---------|
| `info` | Normal operations, no action needed | "96% Pending Review - normal backlog" |
| `warning` | Should address when convenient | "Stale suggestions - 484 over 7 days old" |
| `critical` | Immediate attention required | "Service down", "Critical failure" |

---

## Testing

The SystemIntelligenceAgent now correctly answers:
- "What needs my attention?" → Groups by severity, highlights critical
- "Tell me about the pending review status" → Explains what 96% means, recommends action
- "What's the system health?" → Comprehensive status overview

**Test output:**
```
Success: True
Items: 12 (0 critical, 1 warning, 11 info)
Response: "Summary - Current tally: 0 critical, 1 warning, 11 informational items..."
```

---

## Agent Count Update

- Previous: 71 agents (68 routable)
- Current: 72 agents (69 routable)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Question                             │
│               "What's the pending review status?"                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PersonalAssistantAgent                         │
│              (receives user's system question)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AgentRouter                               │
│    route_by_query() → checks routing_config.py keywords          │
│    Matches: "pending review" → SystemIntelligenceAgent           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SystemIntelligenceAgent                         │
│           - execute(task, context, scifi_context, spider_context)│
│           - Calls SystemStateAggregator                          │
│           - Formats items with GPT-5-mini                        │
│           - Records learning outcome                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SystemStateAggregator                          │
│           - get_attention_items(force_refresh=True)              │
│           - Returns AttentionItem[] with severity/explanation    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AgentResult                                 │
│   message: "The pending review is at 96% which is normal..."     │
│   data: {items_count: 12, critical_count: 0, ...}                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Learnings for Future Agents

1. **Always add to routing_config.py** - Without this, the agent won't be discoverable
2. **Match execute() signature** - Must accept `task, context, scifi_context, spider_context`
3. **Use correct AgentResult fields** - `message` and `data`, NOT `result` and `metadata`
4. **Add learning hooks** - `_record_learning_outcome`, `_create_execution_memory`, `_share_knowledge`
5. **Test the full flow** - Not just the agent, but PA → Router → Agent → Result

---

## Part 2: Enhanced Agents Tab (React Frontend)

### New API Endpoint

**File:** `core/views_agent_orchestration.py`

```python
@api_view(['GET'])
@permission_classes([AllowAny])
def comprehensive_agents_list(request):
    """Returns all 72 agents from AgentRouter with categories, descriptions, keywords."""
```

**Endpoint:** `/api/v1/agents/comprehensive/`

Returns:
- All 72 agents from AgentRouter
- Grouped by 15 categories
- Descriptions, keywords, examples, priority
- Stats: total, routable, categories_count

### Frontend Enhancements

**File:** `frontend/src/pages/AgentsPage.tsx`

| Feature | Description |
|---------|-------------|
| Category Grouping | 15 collapsible sections (Creation, Research, Strategy, etc.) |
| Search/Filter | Search by name, description, or keywords |
| Agent Details | Click to expand - shows keywords, examples, priority |
| Routable Badge | Shows which agents are in routing config |
| Dynamic Stats | Real counts from API (no hardcoded values) |

**Categories:** Creation, Editing, Research, Analysis, Strategy, Executive, Development, Security, Training, Legal, Orchestration, Audit, System, Content, Specialized

---

## Part 3: Activity and Learning Tabs

### Activity Tab

Connected to `/api/recent-activity/` API which aggregates:
- Agent Dreams
- Agent Conversations
- Boardroom Decisions
- Pilot Starts/Completions
- Knowledge Transfers

**Features:**
- Color-coded icons (Purple=dreams, Cyan=conversations, Amber=decisions, Green=pilots, Pink=knowledge)
- Live Updates section shows WebSocket real-time events
- Auto-refresh every 30 seconds
- Manual refresh button
- Activity type legend

### Learning Tab

Connected to `/api/agent-learning/activity/` API.

**Features:**
- Stats panel: Total Knowledge, Connections, Transfers (24h), Active Learners
- Knowledge transfer feed showing Teacher → Student transfers
- Real-time WebSocket events section
- Auto-refresh every 30 seconds

### API Additions (frontend/src/lib/api.ts)

```typescript
export const activityApi = {
  recent: (limit = 20, hours = 72) => api.get(`/recent-activity/?limit=${limit}&hours=${hours}`),
  learning: (limit = 20) => api.get(`/agent-learning/activity/?limit=${limit}`),
}

export const agentsApi = {
  // ... existing
  executionHistory: (limit = 20) => api.get(`/v1/agents/execution-history/?limit=${limit}`),
}
```

---

## All Session 663 Commits (10 total)

```
02a804c3 feat(Session 663): Connect Activity and Learning tabs to REST APIs
88158e03 feat(Session 663): Enhanced Agents tab with category grouping and search
bed57514 docs(Session 663): Complete handoff and start docs for next session
8075264f fix(Session 663): Add required execute() parameters to SystemIntelligenceAgent
f246bec0 fix(Session 663): Add SystemIntelligenceAgent to routing config
62ef3d58 feat(Session 663): Connect Needs Attention UI to enhanced attention items
41a060a0 fix(Session 663): Fix AgentResult constructor in SystemIntelligenceAgent
ef0c6294 fix(Session 663): Add learning hooks to SystemIntelligenceAgent
a9c77ded feat(Session 663): Add SystemIntelligenceAgent for platform health monitoring
```

---

## Session Stats (Final)

- **New backend files:** 1 (system_intelligence_agent.py ~408 lines)
- **New API endpoint:** /api/v1/agents/comprehensive/
- **Modified backend files:** 10
- **Modified frontend files:** 2 (AgentsPage.tsx, api.ts)
- **New agent:** SystemIntelligenceAgent (routable)
- **Frontend lines added:** ~600 lines
- **Total commits:** 10

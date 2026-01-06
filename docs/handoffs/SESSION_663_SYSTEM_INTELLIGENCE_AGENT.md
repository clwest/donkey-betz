# Session 663: SystemIntelligenceAgent - Platform Health Architecture

**Date:** January 5, 2026
**Focus:** Scalable system awareness for the Personal Assistant

---

## Problem Statement

When users asked the PA about system metrics like "Pending Review: 96%", the PA:
1. Didn't understand what the metric meant (alarming users unnecessarily)
2. Didn't know where to look for context (Intelligence section)
3. Required hardcoded keywords to inject system data

The quick fix (keyword hacking) was not scalable - new metrics would require code changes.

---

## Solution: SystemIntelligenceAgent Architecture

Created a dedicated agent for platform health and attention monitoring:

```
User asks "what needs attention?"
    ↓
PA (PersonalAssistantAgent)
    ↓
AgentRouter → SystemIntelligenceAgent
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

**File:** `core/agents/system_intelligence_agent.py` (NEW - ~320 lines)

Agent with two tools:
- `get_system_attention` - Get all current attention items with rich context
- `get_item_details` - Get detailed information about a specific item

The agent:
- Queries SystemStateAggregator for attention items
- Groups by severity (critical → warnings → info)
- Interprets what metrics mean (e.g., "96% Pending Review is normal")
- Provides actionable recommendations

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

### 4. Removed Keyword Hacking

**File:** `core/services/pa_intelligence_enricher.py`

Removed Session 663 keyword additions from SYSTEM_STATE_KEYWORDS.
The proper architecture handles this through agent routing, not keyword injection.

---

## Files Changed

| File | Change |
|------|--------|
| `core/services/system_state_aggregator.py` | Enhanced AttentionItem with new fields |
| `core/agents/system_intelligence_agent.py` | NEW - Agent for system health |
| `core/agents/__init__.py` | Import + export SystemIntelligenceAgent |
| `core/agent_router.py` | Import + register in AGENT_MAP |
| `core/services/pa_intelligence_enricher.py` | Removed keyword hacking |
| `docs/AGENTS.md` | Added SystemIntelligenceAgent documentation |
| `docs/CAPABILITIES.md` | Updated agent count, added capability row |

---

## AttentionItem Severity Levels

| Level | Meaning | Example |
|-------|---------|---------|
| `info` | Normal operations, no action needed | "96% Pending Review - normal backlog" |
| `warning` | Should address when convenient | "Stale data - 3 spiders not refreshed" |
| `critical` | Immediate attention required | "Service down", "Critical failure" |

---

## Testing

The SystemIntelligenceAgent can now answer questions like:
- "What needs my attention?" → Groups by severity, highlights critical
- "Tell me about the pending review status" → Explains what 96% means, recommends action
- "What's the system health?" → Comprehensive status overview

---

## Agent Count Update

- Previous: 71 agents (47 routable)
- Current: 72 agents (48 routable)

---

## Next Session Considerations

1. The PA may need routing hints to know when to delegate to SystemIntelligenceAgent
2. Consider adding more attention item types with rich explanations
3. Could add Discord integration for system health notifications

---

## Session Stats

- **New files:** 1 (system_intelligence_agent.py ~320 lines)
- **Modified files:** 6
- **New agent:** SystemIntelligenceAgent (routable)
- **Architecture pattern:** Agent delegation over keyword hacking

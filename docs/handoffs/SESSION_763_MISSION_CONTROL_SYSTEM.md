# Session 763: Mission Control System Implementation

**Date:** January 15, 2026
**Focus:** Wiring agent outputs to Human Page with executable action buttons
**Status:** COMPLETE - All components implemented and tested

---

## Problem Statement

Agents were executing tools, producing valuable outputs, and learning from each other, but **all results stayed hidden in the database**. Users had no unified view of "what needs my attention today" and no way to take one-click actions on agent discoveries.

**The Gap:** Beautiful AI work happening behind the scenes → Nothing visible to users

---

## Solution: Mission Control System

Created a complete pipeline from agent execution to user action:

```
Agent.execute() → AgentResult
                       ↓
       _maybe_create_attention_item()
                       ↓
       HumanAttentionBridge.create_agent_output_attention()
                       ↓
       HumanAttentionItem (DB with available_actions in payload)
                       ↓
       Human Page (Frontend)
                       ↓
       User clicks action button
                       ↓
       MissionControlExecutor.execute_action()
                       ↓
       Actual execution (publish, set_alert, queue research, etc.)
```

---

## Files Created/Modified

### Backend

| File | Changes |
|------|---------|
| `core/agents/base_agent.py` | +`ActionableOutputConfig` dataclass (lines 117-146), +`_maybe_create_attention_item()` method (lines 1827-1921) |
| `core/services/human_attention_bridge.py` | +`create_agent_output_attention()` method (~60 lines after line 334) |
| `core/services/mission_control_executor.py` | **NEW FILE** - 450+ lines with 17 action handlers |
| `core/views_human_interface.py` | +`AttentionExecuteActionView` class, +URL pattern for `/execute/` |

### Frontend

| File | Changes |
|------|---------|
| `frontend/src/lib/api.ts` | +`executeAction()` method in humanApi (line 994-996) |
| `frontend/src/pages/HumanPage.tsx` | +`AvailableAction` interface, +`ACTION_STYLE_MAP`, +`executeActionMutation`, +dynamic action button rendering |

### Agents Configured (6)

| File | Config |
|------|--------|
| `core/agents/stocks/stock_analyst_agent.py` | insight type, Review/Set Alert/Watchlist/Dismiss |
| `core/agents/stocks/stock_audit_coordinator.py` | alert type, Review Audit/Set Alerts/Watchlist/Dismiss |
| `core/agents/content_writer_agent.py` | review type, Publish/Schedule/Edit/Reject |
| `core/agents/research_agent.py` | insight type, Deep Dive/Share/Archive/Dismiss |
| `core/agents/markets/prediction_market_analyst.py` | opportunity type, Watch/Research More/Pass |
| `core/agents/markets/sports_odds_analyst.py` | opportunity type, Watch Game/Paper Trade/Research/Pass |

---

## Key Components

### 1. ActionableOutputConfig (base_agent.py)

```python
@dataclass
class ActionableOutputConfig:
    """Configuration for when an agent output creates a Mission Control attention item."""
    enabled: bool = False
    item_type: str = 'review'  # review, alert, opportunity, insight, approval
    urgency_from_field: str = None  # Field in result.data to use for urgency
    default_urgency: str = 'medium'
    required_fields: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    actions: List[Dict[str, Any]] = field(default_factory=list)  # Available actions
    payload_fields: List[str] = field(default_factory=list)  # Fields to include
    max_items_per_hour: int = 5  # Rate limiting
```

### 2. MissionControlExecutor (mission_control_executor.py)

Handler registry with 17 built-in handlers:

| Category | Handlers |
|----------|----------|
| **Review** | review, approve, reject |
| **Content** | publish, schedule, edit |
| **Stock/Market** | set_alert, watchlist, remove_watchlist |
| **Research** | deep_dive, research_more, share, archive |
| **Betting** | watch, paper_trade, pass |
| **Generic** | acknowledge, dismiss, snooze |

Each handler returns an `ExecutionResult` with status, message, data, and optional next_action.

### 3. Frontend Action Buttons

Dynamic rendering from `payload.available_actions`:

```typescript
{item.payload?.available_actions?.map((action: AvailableAction) => (
  <button
    key={action.id}
    onClick={() => onExecuteAction(action.id, feedback)}
    className={cn('btn', ACTION_STYLE_MAP[action.style || 'secondary'])}
    title={action.description}
  >
    {action.label}
  </button>
))}
```

---

## Test Results

```
Success: True
Agent: StockAnalystAgent
Tool calls: 3

Attention items from StockAnalystAgent: 1
  Title: StockAnalystAgent: Analyze AAPL stock briefly
  Type: insight
  Urgency: medium
  Status: pending
  Source: agent_output:stockanalystagent
  Has actions: True

Available Actions:
  - review: Review Analysis (primary)
  - set_alert: Set Alert (warning)
  - watchlist: Add to Watchlist (success)
  - dismiss: Dismiss (secondary)
```

---

## How Mission Control Ties Into Orchestration Layer

**CRITICAL FOR NEXT SESSION:** This Mission Control system provides the foundation for the Orchestration Layer:

### 1. Action Execution Pipeline
The `MissionControlExecutor` is already wired to execute actions. The Orchestration Layer can:
- Register additional handlers for orchestration-specific actions
- Use the same pattern for orchestrator commands
- Chain actions together (note: `next_action` field exists)

### 2. Attention Item as Work Queue
`HumanAttentionItem` can serve as a lightweight work queue:
- `status` field: pending → acted → verified
- `urgency` field: critical/high/medium/low for prioritization
- `payload` field: arbitrary JSON for context
- `source_type` field: identifies source (`agent_output:`, `orchestrator:`, etc.)

### 3. Human-in-the-Loop Integration
The Orchestration Layer can:
- Create attention items for approval gates
- Use the execute endpoint for orchestration decisions
- Leverage the existing `decide` endpoint for simple approve/reject
- Track outcomes via `verify` endpoint

### 4. Agent Configuration Pattern
The `ActionableOutputConfig` pattern shows how to configure agents declaratively:
```python
actionable_config = ActionableOutputConfig(
    enabled=True,
    item_type='orchestration_step',
    actions=[...],
    ...
)
```

### 5. Rate Limiting Infrastructure
Built-in rate limiting (`max_items_per_hour`) can prevent orchestration floods.

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/human/attention/` | Get attention stream |
| POST | `/api/human/attention/{id}/decide/` | Record simple decision |
| POST | `/api/human/attention/{id}/execute/` | **NEW** Execute action |
| POST | `/api/human/attention/{id}/verify/` | Record outcome |

### Execute Endpoint Request/Response

```json
// Request
POST /api/human/attention/{id}/execute/
{
    "action": "set_alert",
    "feedback": "Watch for price movement",
    "extra_data": {"threshold": 250}
}

// Response
{
    "success": true,
    "action": "set_alert",
    "status": "success",
    "message": "Alert created for AAPL",
    "data": {"symbol": "AAPL", "alert_type": "price"},
    "next_action": null
}
```

---

## Extending for Orchestration

### Adding New Action Handlers

```python
from core.services.mission_control_executor import mission_control_executor

def my_orchestration_handler(attention_item, user, feedback, extra_data):
    # Do orchestration work
    return ExecutionResult(
        action_id='orchestrate',
        status=ActionResult.SUCCESS,
        message="Orchestration step complete"
    )

mission_control_executor.register('orchestrate', my_orchestration_handler)
```

### Creating Orchestration Attention Items

```python
from core.services.human_attention_bridge import get_human_attention_bridge

bridge = get_human_attention_bridge()
bridge.create_agent_output_attention(
    agent_name='Orchestrator',
    item_type='approval',
    title='Workflow Step Requires Approval',
    summary='...',
    urgency='high',
    payload={
        'workflow_id': '...',
        'step_number': 3,
        'available_actions': [
            {'id': 'approve', 'label': 'Approve Step', 'style': 'success'},
            {'id': 'reject', 'label': 'Reject', 'style': 'danger'},
        ]
    }
)
```

---

## Files to Review for Orchestration Layer

1. **`core/services/mission_control_executor.py`** - Extend handler registry
2. **`core/agents/base_agent.py`** - `ActionableOutputConfig` pattern
3. **`core/services/human_attention_bridge.py`** - Item creation patterns
4. **`core/views_human_interface.py`** - API patterns
5. **`frontend/src/pages/HumanPage.tsx`** - Dynamic action rendering

---

## Summary

Session 763 built the **Mission Control System** - a complete pipeline from agent outputs to user actions. This directly enables the Orchestration Layer by providing:

- Action execution infrastructure
- Human-in-the-loop patterns
- Rate-limited work queues
- Declarative agent configuration
- Dynamic UI action rendering

The Orchestration Layer can build on top of this without reinventing the wheel.

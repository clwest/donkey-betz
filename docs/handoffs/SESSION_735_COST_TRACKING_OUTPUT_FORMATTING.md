# Session 735 - Cost Tracking & Output Formatting

**Previous Session:** 734 (System Ready after Embedding Fixes + Mythology Lab)
**Date:** January 8, 2026
**Status:** COMPLETE - Cost tracking working, output modal formatted

---

## Session 735 Accomplishments

### 1. Fixed Service Startup 500 Errors

**Issue:** Health endpoint returning 500 Internal Server Error on startup.

**Root Cause:** `core/urls.py` importing non-existent functions from `views_advanced_workflows`.

**Fix:** Removed broken imports:
```python
# REMOVED - functions not implemented:
# workflow_analytics, schedule_workflow, workflow_collaboration
```

| File | Change |
|------|--------|
| `core/urls.py` | Removed 3 non-existent function imports and URL patterns |

---

### 2. Fixed Celery SIGSEGV Crashes on macOS

**Issue:** Celery workers crashing with segmentation faults when running orchestrations.

**Root Cause:** Fork issues with PyTorch/SentenceTransformers on macOS.

**Fix:** Run Celery with `--pool=solo`:
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo
```

**Note:** This is a macOS-specific workaround. Production Linux servers can use default pool.

---

### 3. Implemented Orchestration Cost Tracking

**Issue:** Agent orchestrations showing $0.00 cost even after execution.

**Root Cause:**
- `_call_openai()` wasn't returning cost/tokens
- Agents not accumulating costs across multiple LLM calls
- `AgentResult` not receiving cost data from execution

**Fixes Applied:**

| File | Change |
|------|--------|
| `core/agents/base_agent.py` | Added `_accumulated_cost`, `_accumulated_tokens` instance vars |
| `core/agents/base_agent.py` | Added `_reset_cost_tracking()` helper method |
| `core/agents/base_agent.py` | Added `_make_result()` helper for automatic cost injection |
| `core/agents/base_agent.py` | Updated `_call_openai()` to extract and accumulate cost/tokens |
| `core/agents/base_agent.py` | Updated `_call_llm_routed()` to accumulate cost/tokens |
| `core/agent_router.py` | Inject accumulated cost from agent into result after execution |

**Cost Calculation (GPT-5-mini):**
```python
# $0.003/1K input, $0.012/1K output
call_cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.012 / 1000)
```

**Result:** Orchestrations now show real costs:
- PodcastCoordinatorAgent: $0.0097
- DebateAdvocateAgent: $0.0343
- etc.

---

### 4. Fixed PodcastCoordinatorAgent Event Loop Error

**Issue:** PodcastCoordinatorAgent failing with "Event loop is closed" error.

**Root Cause:** Using `asyncio.get_event_loop()` and `run_until_complete()` in Celery workers where the event loop is already closed.

**Fix:** Made execution fully synchronous:

| File | Change |
|------|--------|
| `core/agents/podcast/podcast_coordinator_agent.py` | Removed async wrapper, call `_execute_with_gpt()` directly |
| `core/agents/podcast/podcast_coordinator_agent.py` | Refactored to use `self._call_openai()` for cost tracking |
| `core/agents/podcast/podcast_coordinator_agent.py` | Added `_reset_cost_tracking()` at execution start |

---

### 5. Formatted Output Modal for Individual Findings

**Issue:** Agent outputs displayed as one giant text block, hard to read.

**Fix:** Updated `frontend/src/pages/AgentsPage.tsx` output modal with markdown parsing:

| Feature | Implementation |
|---------|----------------|
| Section detection | Splits by `##`, `###`, numbered bold items |
| Paragraph separation | Falls back to double newline splitting |
| Header styling | `## headers` = cyan, `### subheaders` = purple |
| Bullet points | `- ` or `• ` = green bullets with indentation |
| Numbered lists | `1. ` = amber numbers with monospace font |
| Bold text | `**text**` = white bold inline |
| Card rendering | Multiple sections as separate cards with cyan border |
| Height increase | Modal content 64 → 96 units for readability |

---

## Files Modified

| File | Lines Changed | Purpose |
|------|---------------|---------|
| `core/urls.py` | -6 | Remove broken imports |
| `core/agents/base_agent.py` | +60 | Cost tracking infrastructure |
| `core/agent_router.py` | +8 | Cost injection after execution |
| `core/agents/podcast/podcast_coordinator_agent.py` | +30/-40 | Fix async, add cost tracking |
| `frontend/src/pages/AgentsPage.tsx` | +80 | Output formatting with markdown |

---

## Technical Details

### BaseAgent Cost Tracking Methods

```python
def _reset_cost_tracking(self) -> None:
    """Reset accumulated cost and tokens before a new execution."""
    self._accumulated_cost = 0.0
    self._accumulated_tokens = 0

def _make_result(self, success, message, data, error, ...) -> AgentResult:
    """Create an AgentResult with accumulated cost/tokens."""
    return AgentResult(
        success=success,
        message=message,
        tokens_used=self._accumulated_tokens,
        cost=self._accumulated_cost,
        ...
    )
```

### Agent Router Cost Injection

```python
result = agent.execute(task=task, context=context, ...)

# Inject accumulated cost/tokens from agent into result
if hasattr(agent, '_accumulated_cost') and hasattr(agent, '_accumulated_tokens'):
    if result.cost == 0.0 and agent._accumulated_cost > 0:
        result.cost = agent._accumulated_cost
    if result.tokens_used == 0 and agent._accumulated_tokens > 0:
        result.tokens_used = agent._accumulated_tokens
```

---

## Verification Commands

```bash
# Start services (macOS)
make start
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo &
celery -A core beat -l INFO &

# Test orchestration with cost tracking
# 1. Go to Agents page
# 2. Start "Podcast Production Pipeline"
# 3. View Output - should show costs per agent

# Verify frontend build
cd frontend && npm run build
```

---

## Session 736 Priorities

### Option A: Agent Channels UI (HIGH Priority)
- Backend complete at `/api/v1/agents/channels/`
- Create Slack-like messaging interface
- 2 channels, 5 memberships exist

### Option B: Income Builder Enhancement
- 41 ActionPlans in database
- 8 endpoints need UI exposure

### Option C: More Agent Cost Optimization
- Review other agents for cost tracking
- Add cost breakdown by agent type

---

**Session 735 fixed critical infrastructure issues (Celery crashes, cost tracking) and improved UX with formatted outputs. Time for a well-deserved night off!**

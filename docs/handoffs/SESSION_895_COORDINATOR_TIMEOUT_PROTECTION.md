---
originating_session: 895
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 895 - Coordinator Timeout Protection

**Date:** January 31, 2026
**Focus:** Add timeout protection to all coordinator agents to prevent indefinite hangs
**PR:** #655

---

## Problem

Coordinator agents that call sub-agents were running indefinitely (4+ hours) when sub-agents got stuck. This was caused by:
1. No timeout protection on sub-agent executions
2. Thinking models (GPT-5.1, o1, o3) taking longer for internal reasoning
3. Nested coordinator calls (e.g., MarketIntelligenceCoordinator calling StockAuditCoordinator)

## Solution

Implemented a **two-tier timeout system** using ThreadPoolExecutor with FuturesTimeoutError handling:

| Tier | Timeout | Use Case |
|------|---------|----------|
| **SUB_AGENT_TIMEOUT** | 5 min (300s) | Standard sub-agent calls |
| **COORDINATOR_TIMEOUT** | 8 min (480s) | Nested coordinators / multi-step workflows |

### Why These Values?

- **Thinking models** (GPT-5.1, o1, o3) take 30-90 seconds for internal reasoning
- **Research agents** need time for: spider fetch (5-15s) + LLM thinking (30-90s) + processing (5-10s)
- **Nested coordinators** run multiple sub-agents internally
- Original 2-minute timeout was too short for thinking models
- Original issue was tasks running **4+ hours**, not 5-10 minutes

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/blockchain/blockchain_audit_coordinator.py` | Added 5-min timeout to `_route_to_agent` |
| `core/agents/campaign_orchestrator_agent.py` | Added 5-min timeout to all 3 content generation methods |
| `core/agents/executive/meeting_coordinator_agent.py` | Added 5-min timeout to `_get_agent_perspective` |
| `core/agents/narrative/narrative_drift_coordinator.py` | Added 5-min timeout to all 3 analysis agents |
| `core/agents/podcast/podcast_coordinator_agent.py` | Added 5-min timeout to debate agent executions |
| `core/agents/stocks/market_intelligence_coordinator.py` | Added 5-min (agents) + 8-min (nested coordinator) |
| `core/agents/stocks/stock_audit_coordinator.py` | Added 5-min timeout to all 4 sub-agents |
| `core/agents/workflow_orchestration_agent.py` | Added 8-min timeout to legacy workflow execution |

---

## Pattern Applied

All coordinators now use this pattern:

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Extended to accommodate thinking models (GPT-5.1, o1, o3)
SUB_AGENT_TIMEOUT = 300  # 5 minutes per sub-agent
COORDINATOR_TIMEOUT = 480  # 8 minutes for nested coordinator calls

def execute_agent():
    return agent.execute(task=task, context=context, ...)

try:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(execute_agent)
        result = future.result(timeout=SUB_AGENT_TIMEOUT)
except FuturesTimeoutError:
    logger.warning(f"⏰ {agent_name} timed out after {SUB_AGENT_TIMEOUT}s")
    # Graceful fallback handling
```

---

## Coordinators Updated

| Coordinator | Timeout | Methods Protected |
|------------|---------|-------------------|
| BlockchainAuditCoordinator | 5 min | `_route_to_agent` (routes to 4 blockchain agents) |
| CampaignOrchestratorAgent | 5 min | `_generate_ad_copies`, `_generate_social_posts`, `_generate_email_sequence` |
| MeetingCoordinatorAgent | 5 min | `_get_agent_perspective` (calls executive agents) |
| NarrativeDriftCoordinator | 5 min | Historian, TrendBreak, CulturalImpact agents |
| PodcastCoordinatorAgent | 5 min | Debate agent executions (multi-turn debates) |
| MarketIntelligenceCoordinator | 5 min + 8 min | `_run_bull_case`, `_run_bear_case` + `_run_risk_assessment` (nested) |
| StockAuditCoordinator | 5 min | `_run_stock_analyst`, `_run_movement_monitor`, `_run_institutional_watcher`, `_run_anomaly_detector` |
| WorkflowOrchestrationAgent | 8 min | Legacy workflow execution (multi-step) |

---

## Also Fixed in This Session

### 1. PUBLIC_PATHS Audit (PR #652)
- Added `/api/mythology/guards/` to fix Intel page Safety sub-tab 401 error

### 2. Workspace Context Fix (PR #653)
- Fixed `workspace: False` for system tasks by changing lookup from "codebase" to "donkey"

### 3. Production Task Cleanup
- Cleaned up 6 stuck production tasks (3 MarketIntelligenceAgent, 3 AutonomousContentStudioCoordinator)

---

## Testing

To verify timeouts are working:

1. **Trigger a coordinator task**:
   ```bash
   python manage.py shell -c "
   from core.agents.stocks.market_intelligence_coordinator import MarketIntelligenceCoordinator
   coord = MarketIntelligenceCoordinator()
   result = coord.execute(
       task='Generate market brief for AAPL',
       context={'tickers': ['AAPL']},
       scifi_context={},
       spider_context={}
   )
   print(result)
   "
   ```

2. **Check logs for timeout warnings**:
   ```bash
   grep "⏰" logs/celery.log
   ```

3. **Monitor production** for tasks that now complete instead of hanging

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Max task runtime | 4+ hours (indefinite) | 8 minutes max |
| Timeout handling | None | Graceful fallback with logging |
| Thinking model support | No | Yes (5-8 min allows for reasoning) |
| Stuck task cleanup | Manual | Automatic timeout |

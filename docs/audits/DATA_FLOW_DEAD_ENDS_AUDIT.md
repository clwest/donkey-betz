# Data Flow Dead Ends Audit

**Date:** April 5, 2026
**Audited by:** Claude Code + Explore Agent
**Severity:** CRITICAL — multiple data loss patterns confirmed

---

## Summary

This platform has **10 distinct data loss or misdirection patterns**. The most critical: 17 agents run daily on schedule but their results never surface anywhere users can see them. Additionally, conversation dispatches fire agent tasks and then discard the results.

---

## CRITICAL Findings

### 1. Scheduled Agent Results Lost in Void (17 Agents)

17 agents have `create_deliverable_on_schedule = False`, meaning their **scheduled** execution outputs are:
- Stored in `AgentExecution.output_data` (DB column)
- **NOT promoted to Deliverable** (invisible in product UI)
- Only visible in `/api/agent-execution/` analytics endpoints (admin-only)

**Affected Agents:**

| Agent | What It Produces | Where It Goes |
|---|---|---|
| ResearchAgent | Research reports | AgentExecution only |
| TrendAnalysisAgent | Trend analyses | AgentExecution only |
| BrandStrategyAgent | Brand strategies | AgentExecution only |
| CompetitorAnalysisAgent | Competitive intel | AgentExecution only |
| ContentStrategyAgent | Content strategies | AgentExecution only |
| CustomerResearchAgent | Customer research | AgentExecution only |
| MarketingStrategyAgent | Marketing plans | AgentExecution only |
| DistributionAgent | Distribution plans | AgentExecution only |
| EditorAgent | Edited content | AgentExecution only |
| ArbitrageDetector | Arbitrage opportunities | AgentExecution only |
| TrendBreakDetectorAgent | Trend break alerts | AgentExecution only |
| InstitutionalWatcherAgent | Institutional moves | AgentExecution only |
| MarketAnomalyDetectorAgent | Market anomalies | AgentExecution only |
| MarketMovementMonitorAgent | Market movement alerts | AgentExecution only |
| StockAnalystAgent | Stock analyses | AgentExecution only |
| SocialMediaAgent | Social media plans | AgentExecution only |

**Root Cause:** `core/agents/base_agent.py` lines ~1460-1480 (Session 1077):

```python
# Skip deliverable creation for scheduled runs
if not self.create_deliverable_on_schedule:
    is_scheduled = not user and not trace_id
    if is_scheduled:
        return None  # Output in AgentExecution, not promoted
```

**Impact:** Days or weeks of research, analyses, and intelligence reports sitting in a DB column nobody queries. These agents are doing real work with real LLM calls (real cost) and the output vanishes.

---

### 2. Conversation Dispatch Results Discarded

When `ConversationActionDispatcher` queues agent work from conversation next-steps:

```
conversation.next_steps → dispatch_actions()
  → execute_agent_task.delay(agent_name, task, context)
  → task_id logged
  → Result NEVER retrieved
  → AgentExecution created with output
  → No callback to conversation
  → No promotion to Deliverable
```

**File:** `core/services/conversation_action_dispatcher.py` lines 443-459

The `async_result` task ID is logged but `.get()` is never called anywhere. The conversation that triggered the work never learns what the agent found.

---

## HIGH Findings

### 3. Deliverables Created in 23+ Locations (No Central Gateway)

`Deliverable.objects.create()` appears in **23 different files**:

- Agent base class (main path)
- 3 specific agents (campaign_orchestrator, workflow_agent)
- 6 services (conversation_deliverable_extractor, deliverable_envelope, td_handlers x3, discord_bot)
- 3 task files (tasks_content, tasks_conversations, tasks_initiatives)
- 5 views (views_deliverables, views_diagnostics, views_demo_pipeline, views_workspace_templates)
- 1 model factory (models_deliverables, models_document_registry)
- 1 management command (import_patent_disclosures)

**Risk:** Each path may populate different metadata (title, category, tags, workspace, user). No single factory enforces consistency.

### 4. ChatConversation Created in 9 Different Locations

| Location | Source |
|---|---|
| `core/views_personal_assistant.py` | PA Web UI |
| `core/epa_handlers_utility.py` | Enhanced PA |
| `core/services/claude_code_agent.py` | Claude Code |
| `core/services/claude_code_engineer.py` | Claude Code Engineer |
| `core/services/collaboration_protocol.py` | Team collaboration |
| `core/services/discord_bot.py` | Discord |
| `core/services/td_handlers_ops.py` | Tool Dispatcher |
| `core/tasks_misc.py` | Background task |
| `core/conversation_memory_fixed.py` | Memory system |

**Risk:** Different paths may record different fields (discord_user_id, workspace, platform, source). Some may miss fields others capture.

### 5. 52 Tasks with `ignore_result=True`

52 Celery tasks configured to discard return values. If a task creates data but doesn't explicitly save to DB before returning, the data evaporates.

**Critical examples:**
- `run_spider_network()` — spider data must be saved during execution
- `run_agent_conversation()` — conversation results must persist during task
- `content_autonomy_loop()` — autonomous content decisions
- `broadcast_evolution_status()` — evolution events

**Files:** `core/tasks.py` (12+), `core/tasks_push_notifications.py` (8+), `core/tasks_preview.py` (3+)

---

## MEDIUM Findings

### 6. Orphan Models — Written but Never Read

| Model | Created In | Read In | Row Count | Latest Record | Status |
|---|---|---|---|---|---|
| `SkillGapAnalysis` | tasks.py | No reads found | 1,466 | Dec 2025 | ORPHAN — real data, never surfaced |
| `CaseLawUpdate` | tasks.py | No reads found | 0 | — | EMPTY — safe to remove |
| `RegulatoryChange` | tasks.py | No reads found | 0 | — | EMPTY — safe to remove |
| `ThumbnailVariant` | tasks_media.py | tasks_media.py only | 77 | Jan 2026 | No UI |
| `ViralContentPrediction` | tasks_misc.py | tasks_media.py | 5,351 | Jan 2026 | ORPHAN — real data, never surfaced |
| `EarningsPrediction` | tasks_financial.py | Unclear | 0 | — | EMPTY — safe to remove |
| `TechStackTrend` | tasks.py | Unclear | 12 | Unknown | Low value |
| `DesignTrend` | tasks_ops.py | discord_bot.py | 13 | Unknown | Has reads |

**Audit run:** April 5, 2026 (local DB). Production counts may differ.

**Key findings:** `ViralContentPrediction` (5,351 rows) and `SkillGapAnalysis` (1,466 rows) contain real, potentially valuable data that has never been shown to users. These could be surfaced in the Intelligence tab.

**Location:** `core/models_autonomous_situations.py` — these models are defined and populated by background tasks but may never be queried by any view or API.

### 7. Spider Data Pipeline Complexity

SpiderData flows through a multi-step pipeline that's poorly documented:

```
Spider execution → SpiderData (raw)
  → spider_data_bridge.py (transformation)
  → spider_opportunity_connector.py (routing)
  → Opportunities / FreelanceOpportunity / SideHustle (final)
```

**Risk:** Complex multi-hop pipeline means data could silently fail at any transformation step without alerting anyone.

### 8. AgentExecution output_data Not Displayed in Product

While `AgentExecution` is queried in analytics views, the actual `output_data` content is **not displayed** in the main product UI. Users see execution status (success/fail/duration) but not what the agent actually produced.

### 9. Conversation-to-Deliverable Extraction Limited

Only `ConversationDeliverableExtractor` extracts conversation insights as Deliverables, and it's called from limited locations. Conversation insights may be lost if the extractor isn't triggered.

---

## LOW Findings

### 10. Push Notifications May Not Persist Delivery Status

8 push notification tasks use `ignore_result=True`. If Expo API fails, no retry and no permanent failure record.

---

## Quantifying the Problem

To understand the actual scope, run these queries:

```python
from django.db.models import Count
from core.models import AgentExecution
from core.models_deliverables import Deliverable

# How many agent executions exist vs deliverables created?
total_executions = AgentExecution.objects.filter(
    status='completed',
    created_at__gte='2026-03-01'
).count()

total_deliverables_from_agents = Deliverable.objects.filter(
    created_at__gte='2026-03-01',
    agent_name__isnull=False
).count()

print(f"Executions: {total_executions}")
print(f"Deliverables: {total_deliverables_from_agents}")
print(f"GAP: {total_executions - total_deliverables_from_agents} results in void")

# Which agents produce the most orphan results?
from django.db.models import Subquery, OuterRef
orphan_agents = AgentExecution.objects.filter(
    status='completed',
    created_at__gte='2026-03-01'
).values('agent__name').annotate(
    count=Count('id')
).order_by('-count')[:20]
```

---

## Recommended Fix Priorities

### Tier 1: Stop the Bleeding (This Week)

1. **Enable deliverable creation for high-value agents** — flip `create_deliverable_on_schedule = True` for ResearchAgent, TrendAnalysisAgent, CompetitorAnalysisAgent, StockAnalystAgent (the ones producing actionable intelligence)
2. **Add result callback to ConversationActionDispatcher** — store agent result in conversation or promote to deliverable
3. **Count the gap** — run the quantification queries above to understand scale

### Tier 2: Centralize (Next Sprint)

4. **Create `DeliverableFactory`** — single factory method that all 23 creation paths use, ensuring consistent metadata
5. **Create `ConversationFactory`** — single factory for all 9 ChatConversation creation paths
6. **Audit orphan models** — query SkillGapAnalysis, CaseLawUpdate, RegulatoryChange for data; delete models if empty

### Tier 3: Pipeline Hardening (Following Sprint)

7. **Document spider pipeline** — trace and document SpiderData → bridge → connector → final table flow
8. **Add pipeline health checks** — Celery task that counts records at each pipeline stage and alerts on significant drops
9. **Surface AgentExecution output_data** — add "Agent Results" section to Operations tab showing recent outputs
10. **Audit ignore_result tasks** — verify each of the 52 tasks persists data before returning

---

## Key Files for Investigation

| File | Relevance |
|---|---|
| `core/agents/base_agent.py` | Deliverable creation gate (~line 1460) |
| `core/services/conversation_action_dispatcher.py` | Result discard (~line 443) |
| `core/models_deliverables.py` | Deliverable model |
| `core/models_autonomous_situations.py` | Orphan situation models |
| `core/tasks.py` | 12+ ignore_result tasks |
| `core/views_autonomous_dashboard.py` | May reference orphan models |
| `core/learning_bridges/spider_data_bridge.py` | Spider transformation layer |

---

**Bottom Line:** This platform is doing significantly more work than users ever see. The 17 agents running on schedule are producing intelligence that evaporates. The conversation system dispatches work and never checks on it. And the 23 different ways to create a deliverable means there's no guarantee of consistency. This isn't a bug — it's an architectural gap that grew organically as the platform scaled.

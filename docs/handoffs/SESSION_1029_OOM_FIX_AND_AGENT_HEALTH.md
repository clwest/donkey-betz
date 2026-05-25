---
originating_session: 1029
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1029: OOM Fix, Agent Health Audit & Struggling Agent Fixes

**Date:** February 17, 2026
**Status:** Complete
**PRs:** #1282 (OOM reroute), #1283 (secondary waste paths), #1284 (revenue trigger), #1285 (struggling agents)

## Problem

Three interrelated issues:

1. **celery-worker OOM crashes** — 3 crashes in 18 minutes. 512MB container with ~200MB parent couldn't handle tasks spiking 200-500MB.
2. **Waste agents still running** — Despite Session 1027 fixes (PR #1273), CodeGeneratorAgent/AudioAgent/OpportunityScoringAgent still ran via 2 undiscovered dispatch paths.
3. **Struggling agents** — 6 agents with <80% success rate, most due to unbounded task descriptions causing 45-min timeouts.

## Philosophy Shift

Session 1029 reframed the approach from "fix what's broken" to **"help agents succeed at what they're designed to do."** Instead of just looking at errors, we classified agents by their ability to fulfill their mission:
- **Thriving (35 agents):** >80% success, producing deliverables
- **Struggling (6 agents):** 30-80% success, need bounded tasks or data
- **Wasting (3 agents):** Running with no useful output

## Discovery: Three Parallel Scheduling Systems

Session 1027 (PR #1273) only fixed one dispatch path. Session 1029 discovered agents are dispatched from **three independent systems:**

| System | File | Mechanism | Fixed In |
|--------|------|-----------|----------|
| A: `run_*_agents()` | `core/tasks.py` | 19 group schedules via `_run_agent_group()` | PR #1273 (Session 1027) |
| B: `AGENT_WORKSPACE_REGISTRY` | `core/tasks.py` | `agent_category_rotation()` iterates registry | PR #1283 (Session 1029) |
| C: `MetricsActionTrigger` | `core/services/metrics_action_trigger.py` | Condition-based triggers from live metrics | PRs #1283, #1284 (Session 1029) |

Additionally: `workspace_autopilot_tick()` CATEGORY_AGENTS, `dream_execution_pipeline.py` DREAM_TO_WORKFLOW, and `auto_generate_podcast_episode()` all dispatch agents independently.

## Fixes Applied

### PR #1282: OOM Fix — Reroute Heavy Tasks
Moved 5 tasks from `default` queue (512MB) to `long_running` queue (-c 3, 300MB/child):
- `run_multi_agent_conversation` — loads 30 agents
- `run_autonomous_thinking_cycle` — heavy context gather
- `process_hivemind_sessions` — orchestration heavy
- `execute_approved_dreams_via_orchestration` — up to 10 dreams
- `warm_up_spider_network` — initializes 77 spiders

### PR #1283: Close Secondary Waste Paths
- Commented out CodeGeneratorAgent from `AGENT_WORKSPACE_REGISTRY`
- Commented out AudioAgent from `AGENT_WORKSPACE_REGISTRY`
- Disabled 2 remediation trigger rules in `metrics_action_trigger.py`

### PR #1284: Revenue Trigger
- Disabled `zero_revenue_7d` trigger rule — was spawning 62+ OpportunityScoringAgent "no revenue" runs/day

### PR #1285: Struggling Agent Fixes
- **TrendAnalysisAgent** (0% → expected ~80%): Bounded task from "Analyze current market and content trends from spider data" to "Summarize the top 3 trends, under 500 words"
- **CompetitorAnalysisAgent**: Bounded task to prevent LLM from interpreting as "Step 3 competitor audit"
- **CustomerResearchAgent**: Added "report no data available" instruction
- **CodeGeneratorAgent**: Replaced in `workspace_autopilot_tick()` (CATEGORY_AGENTS + TYPE_AGENTS) with FullStackDeveloperAgent, and in `dream_execution_pipeline.py` 'improvement' workflow with ContentWriterAgent
- **AudioAgent**: Disabled TTS in `auto_generate_podcast_episode()` (`generate_audio=False`)
- Cleaned up 5 stuck in_progress executions on Railway (2 WorkflowAgent, 3 TrendAnalysisAgent)

## Agent Health Report (at time of audit)

| Agent | Runs/24h | Success | Cost | Classification |
|-------|----------|---------|------|---------------|
| ResearchAgent | 173 | 96.5% | $2.22 | Thriving |
| CodeGeneratorAgent | 96 | 84.4% | $8.72 | Wasting (sandbox) |
| OpportunityScoringAgent | 68 | 92.6% | $0.66 | Wasting (no revenue loop) |
| SystemIntelligenceAgent | 60 | 95.0% | $0.00 | Thriving |
| CompetitorAnalysisAgent | 39 | 89.7% | $0.61 | Thriving (data-starved) |
| ContentWriterAgent | 37 | 78.4% | $0.00 | Needs Help |
| TrendAnalysisAgent | 30 | 30.0% | $0.18 | Struggling (timeout) |
| WorkflowAgent | 14 | 42.9% | $0.56 | Struggling (wrong tasks) |
| AudioAgent | 12 | 0.0% | $0.40 | Wasting (quota) |

## Key Files Modified
- `core/settings.py` — 5 task routes changed (default → long_running)
- `core/tasks.py` — AGENT_WORKSPACE_REGISTRY cleanup, bounded tasks, workspace autopilot CodeGen replacement, podcast audio disabled
- `core/services/metrics_action_trigger.py` — 3 trigger rules disabled
- `core/services/dream_execution_pipeline.py` — CodeGeneratorAgent replaced in 'improvement' workflow

## Key Learnings

1. **Multiple dispatch systems:** Agents can be triggered from 3+ independent paths. Disabling one doesn't stop the others. Always audit ALL paths.
2. **Unbounded tasks cause timeouts:** "Analyze all trends" → 45-min timeout. "Summarize top 3 trends, 500 words" → completes in seconds.
3. **LLMs reinterpret vague tasks:** "Research competitor activity" became "Step 3 competitor audit for Donkey Betz" with 6 specific competitors. Bounded task descriptions prevent creative reinterpretation.
4. **Evidence gates work correctly:** CompetitorAnalysisAgent and CustomerResearchAgent refuse to hallucinate when data is missing. The issue is missing data, not broken agents.

## Verification

After deploy, check 24h stats:
```
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
from django.db.models import Sum, Count, Q
since = timezone.now() - timedelta(hours=24)
execs = AgentExecution.objects.filter(created_at__gte=since)
total_cost = float(execs.aggregate(c=Sum('cost'))['c'] or 0)
print(f'Total: {execs.count()} runs, \${total_cost:.2f}')
for name in ['CodeGeneratorAgent', 'AudioAgent', 'OpportunityScoringAgent', 'TrendAnalysisAgent', 'WorkflowAgent']:
    qs = execs.filter(agent__name=name)
    count = qs.count()
    ok = qs.filter(status='completed').count()
    cost = float(qs.aggregate(c=Sum('cost'))['c'] or 0)
    print(f'  {name}: {count} runs ({ok} ok), \${cost:.2f}')
"
```
Expected: CodeGeneratorAgent=0, AudioAgent=0, TrendAnalysis success rate >50%, total cost <$8/day.

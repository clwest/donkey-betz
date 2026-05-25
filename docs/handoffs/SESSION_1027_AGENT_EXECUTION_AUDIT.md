---
originating_session: 1027
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1027: Agent Execution Audit & Waste Removal

**Date:** February 17, 2026
**Status:** Complete
**PRs:** #1271 (remediation redesign), #1272 (UserProfile fix), #1273 (agent execution waste)

## Problem

Overnight agent executions: 589 runs, $16.76/day. Audit revealed 4 waste sources burning ~$10/day:

1. **CodeGeneratorAgent ($8.76, 83 runs)** — still running via TWO paths: remediation schedules AND `run_development_tech_agents` group. Runs in Railway sandbox with no codebase access.
2. **AudioAgent ($0.41, 12 runs)** — ElevenLabs quota exceeded, 100% failure rate.
3. **WorkflowAgent spawning loop** — task "Check pending workflows and advance ready items" spawned ~30 ResearchAgent sub-tasks/day, all producing identical "audit pending workflows inventory" reports.
4. **OpportunityPipelineAgent "no revenue" loop** — triggered OpportunityScoringAgent to run "Analyze why no revenue" 51x/day. Revenue absence is expected (solo dev building the platform).

## Fixes Applied

### PR #1271: Remediation System Redesign
- Disabled 3 Celery Beat execution schedules (execute-remediation-tasks, verify-completed-fixes, run-autonomous-remediation-cycle)
- Kept 2 discovery/assignment schedules running
- Created `show_remediation_findings` management command
- Cancelled 79 stuck tasks in Railway DB, reset 69 findings to 'open', disabled 3 PeriodicTask DB entries
- See `docs/handoffs/SESSION_1026_REMEDIATION_REDESIGN.md`

### PR #1272: UserProfile Duplicate Fix
- Renamed `core/unified_storage.py:UserProfile` to `StorageUserProfile` (prevented RuntimeError conflict with canonical `core.models.users.models.UserProfile`)
- Fixed broken import in `core/services/discord_bot.py:3489` (`core.models_unified_system` -> `core.models`)
- Added dead-code markers to `core/models.py` duplicates
- Marked 6 related AuditFindings as fixed on Railway

### PR #1273: Agent Execution Waste Removal
- **Removed CodeGeneratorAgent** from `run_development_tech_agents` — can't write code in sandbox
- **Removed AudioAgent** from `run_content_creation_agents` — ElevenLabs quota exceeded
- **Rewrote WorkflowAgent task** — bounded "report summary only, do NOT delegate" instead of unbounded sub-task spawning
- **Rewrote OpportunityPipelineAgent task** — "summarize top 3 signal clusters" instead of triggering "no revenue" loop

## Agent Group Schedule Map (19 schedules)

| Schedule | Frequency | Agent Count | Queue |
|----------|-----------|-------------|-------|
| `autonomous-thinking-cycle` | 1h | 1 | default |
| `run-autonomy-cycle` | 30min | varies | long_running |
| `run-market-monitoring-agents` | 4h | 5 | long_running |
| `run-blockchain-monitoring-agents` | 6h | 4 | long_running |
| `run-content-creation-agents` | 3h | 8 (was 9) | long_running |
| `run-strategy-marketing-agents` | 4h | 5 | long_running |
| `run-stock-financial-agents` | 3h | 5 | long_running |
| `run-prediction-market-agents` | 2h | 3 | sports |
| `run-narrative-culture-agents` | 6h | 4 | long_running |
| `run-development-tech-agents` | 4h | 4 (was 5) | long_running |
| `run-executive-leadership-agents` | 6h | 4 | long_running |
| `run-podcast-debate-agents` | 8h | 4 | long_running |
| `run-system-orchestration-agents` | 2h | 5 | agents |
| `run-quality-audit-agents` | 4h | 2 | agents |
| `run-specialty-agents` | 8h | 4 | long_running |
| `run-research-analysis-agents` | 2h | 2 | agents |
| `run-content-studio-agents` | 4h | 3 | agents |
| `run-campaign-series-agents` | 6h | 2 | agents |
| `run-business-strategy-agents` | 8h | 5 | agents |

All use `_run_agent_group()` helper (tasks.py:30247) which calls `universal_agent_workspace_output()` for each agent.

## Cost Impact

| Source | Before | After | Savings |
|--------|--------|-------|---------|
| Remediation execution (PR #1271) | $9.00/day | $0 | $9.00 |
| CodeGeneratorAgent dev-tech (PR #1273) | $0.50/day | $0 | $0.50 |
| AudioAgent (PR #1273) | $0.41/day | $0 | $0.41 |
| WorkflowAgent sub-task spawning (PR #1273) | $0.40/day | $0 | $0.40 |
| OpportunityScoringAgent loop (PR #1273) | $0.50/day | $0 | $0.50 |
| **Total** | **$16.76/day** | **~$6/day** | **~$10.81/day** |

## Key Learning

**django_celery_beat DB persistence:** Commenting out schedule definitions in `celery.py` does NOT disable schedules already persisted in `django_celery_beat_periodictask` table. Must also disable via `PeriodicTask.objects.filter(name='...').update(enabled=False)`.

**Agent group schedules are the primary execution driver:** All 19 `run_*_agents` schedules use `_run_agent_group()` which calls `universal_agent_workspace_output()`. Removing an agent from these groups is the only way to stop it from running on schedule.

**Unbounded agent tasks spawn sub-tasks:** When an agent's task description says "check and advance" or "review and prioritize", the agent may delegate work to ResearchAgent or OpportunityScoringAgent, creating cascading execution chains. Bounded tasks ("report summary only, do NOT delegate") prevent this.

## Verification

After deploy, check 24h execution stats:
```
railway run python manage.py shell -c "
from core.models_unified_system import AgentExecution
from django.utils import timezone; from datetime import timedelta
from django.db.models import Sum, Count
since = timezone.now() - timedelta(hours=24)
execs = AgentExecution.objects.filter(created_at__gte=since)
total_cost = execs.aggregate(c=Sum('cost'))['c'] or 0
print(f'Total: {execs.count()} runs, \${total_cost:.2f}')
for name in ['CodeGeneratorAgent', 'AudioAgent', 'OpportunityScoringAgent', 'ResearchAgent']:
    count = execs.filter(agent__name=name).count()
    cost = execs.filter(agent__name=name).aggregate(c=Sum('cost'))['c'] or 0
    print(f'  {name}: {count} runs, \${cost:.2f}')
"
```
Expected: CodeGeneratorAgent=0, AudioAgent=0, OpportunityScoringAgent<10, ResearchAgent<150, total cost<$8.

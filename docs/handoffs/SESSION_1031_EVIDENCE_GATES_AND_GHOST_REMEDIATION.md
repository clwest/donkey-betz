---
originating_session: 1031
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1031: Evidence Gate Fixes + Ghost Remediation Block

**Date:** February 17-18, 2026
**PRs:** #1291, #1292, #1293, #1294, #1295, #1296, #1297, #1298

## Summary

Two major workstreams: (1) fixed evidence gate blocking in 4 business agents that were dropping web_search data and getting blocked by auto-extracted domain tags, and (2) traced and blocked a ghost Celery task dispatcher that was firing `execute_remediation_tasks` ~20x/day despite being disabled in all known locations.

---

## Part 1: Evidence Gate Fixes (PRs #1291-1296)

### Problem

CompetitorAnalysisAgent completing 69% of the time but 12/51 recent executions produced LOW-QUAL or BLOCKED output. Same pattern affected ResearchAgent, BrandStrategyAgent, and CustomerResearchAgent.

### Root Causes

1. **`_synthesize_analysis` silently drops dict data** — `isinstance(data, list)` check skipped web_search results (which return `{'results': [...]}` dict, not a list)
2. **Evidence gate used garbage auto-extracted domain tags** — When no project_id exists, `domain_extraction_service.extract_domains(task)` extracts meta-words from task templates ("publication-ready", "report", "analysis") instead of business-domain terms, causing 0% match → block
3. **Single-round tool calling** — GPT calls spider_query first, never gets second round for web_search
4. **WebSearchTool method name wrong** — `.search()` called instead of `.execute()` in 3 agents

### Fixes

| PR | Agent(s) | Fix |
|----|----------|-----|
| #1291 | Infrastructure | Dream-to-boardroom bridge + OOM fix for celery workers |
| #1292 | Multiple | Route specialist tasks to correct agents + 2h dedup guard |
| #1293 | CompetitorAnalysisAgent | Dict data normalization + skip evidence gate for auto-extracted tags + web_search fallback |
| #1294 | ResearchAgent | Lower evidence threshold + web_search fallback when spider_query fails |
| #1295 | BrandStrategyAgent | Dict data handling + web_search fallback |
| #1296 | 3 business agents | `WebSearchTool.search()` → `.execute()` method name fix |

### Key Code Pattern

All 4 agents now normalize dict results before synthesis:
```python
# Before iteration
if isinstance(data, dict):
    data = data.get('results', data.get('data', data.get('discussions', [data])))
    if not isinstance(data, list):
        data = [data]
```

And skip domain-relevance gate when tags were auto-extracted:
```python
domain_tags_reliable = not (project_context or {}).get('domain_tags_auto_extracted', False)
if domain_tags and domain_tags_reliable and data_relevance_score < MIN_DOMAIN_RELEVANCE:
    # Block
```

---

## Part 2: Ghost Remediation Block (PR #1297)

### Problem

`execute_remediation_tasks` ran 41 times in 48 hours and `run_autonomous_remediation_cycle` ran 4 times — despite being disabled in:
- Code-defined Celery Beat schedule (commented out since Session 1026)
- DB scheduler (PeriodicTask entries Enabled=False)
- No `.delay()` calls in code
- No `send_task()` calls
- No signal handlers
- `metrics_action_trigger.py` entries commented out

### Investigation

Traced the full pipeline:
1. `audit_tracker.py:_extract_table_findings()` — regex too greedy, matched ANY table with Issue/Problem/Gap in ANY column header
2. Informational tables (e.g., file counts, command summaries) parsed as findings
3. `AuditFinding` records created with garbage titles like "200+ | All 35+ integrations, API keys needed"
4. `autonomous_remediation_orchestrator.assign_open_findings()` created `AuditRemediationTask` entries
5. `_build_context_prompt()` used `finding.description` as base task text → raw markdown fragments sent to agents

### Fixes

1. **Hard-blocked both tasks** — Added early `return` guards to `execute_remediation_tasks` and `run_autonomous_remediation_cycle` with warning logs
2. **Tightened `_extract_table_findings`** — First column must be issue-type header; rows filtered for pure numbers, file paths, bullet fragments, short non-alpha strings
3. **Raised `_extract_gap_findings` min title** — From 10 to 25 chars
4. **Cleaned up Railway data** — 34 garbage findings marked `wont_fix`, 30 remediation tasks cancelled

### Mystery Trigger (UNSOLVED)

The ghost dispatcher that fires `execute_remediation_tasks` was NOT identified. The hard-block workaround prevents execution. Possible sources to investigate:
- django_celery_beat DatabaseScheduler may have hidden/cached entries
- Redis may have queued tasks from before the disable
- An external cron or Railway scheduled job

---

## Part 3: Endpoint Restoration (PR #1298)

### Problem

`/api/agent-learning/activity/?limit=30` returning 404 every 30 seconds in browser console. Frontend `AgentsPage.tsx:716` polls this endpoint.

### Fix

The URL route was removed in Session 1009 "orphan cleanup" but the view `get_knowledge_transfer_feed` in `views_agent_learning.py` was never removed. Re-added the route in `core/urls.py`.

---

## Post-Deploy Verification

| Check | Result |
|-------|--------|
| `/api/agent-learning/activity/` | 200 OK with valid data |
| `execute_remediation_tasks` runs | 0 post-deploy (hard-block working) |
| AudioAgent executions | 0 post-deploy |
| CompetitorAnalysisAgent | 60 runs, 54 completed (90% vs 69% before) |
| ResearchAgent | 168 runs, 163 completed (97%) |
| CodeGeneratorAgent | 4 runs still leaking (waste path NOT fully closed) |

## Open Issues for Next Session

1. **CodeGeneratorAgent still runs** — 4 executions in 2h post-deploy with garbage tasks ("Every 20 min | Execute dreams", "Lines | Key Contents"). A dispatch path remains open despite being removed from `AGENT_WORKSPACE_REGISTRY` and `run_development_tech_agents`.
2. **Ghost Celery dispatcher** — Root cause unknown. Hard-block is working.
3. **Cost at $15/day** — Above $6/day target. CodeGeneratorAgent alone is $5.66/day.
4. **WorkflowAgent 42% success rate** — 24 runs, 10 completed. Needs investigation.
5. **TrendAnalysisAgent 36% success rate** — 33 runs, 12 completed over 24h (improved to 100% in last 2h).

## Files Modified

| File | Changes |
|------|---------|
| `core/agents/business/competitor_analysis_agent.py` | Dict normalization, domain tag skip, web_search fallback |
| `core/agents/business/research_agent.py` | Lower evidence threshold, web_search fallback |
| `core/agents/business/brand_strategy_agent.py` | Dict handling, web_search fallback |
| `core/agents/business/customer_research_agent.py` | WebSearchTool method fix |
| `core/agents/business/content_strategy_agent.py` | WebSearchTool method fix |
| `core/agents/business/marketing_strategy_agent.py` | WebSearchTool method fix |
| `core/tasks.py` | Hard-block on execute_remediation_tasks + run_autonomous_remediation_cycle |
| `core/services/audit_tracker.py` | Tightened table/gap finding extraction |
| `core/urls.py` | Restored agent-learning/activity endpoint |

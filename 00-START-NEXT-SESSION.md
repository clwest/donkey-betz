# Session 809 - Production vs Local Investigation

**Previous Session:** 808 (Task Audit, Agent Flow Analysis, Persona Agent Discovery)
**Date:** January 24, 2026
**Status:** 75 Core + 139 Persona Agents | 45 Frontend Pages | ALL BODY SYSTEMS GREEN | 74 Active Celery Beat Tasks

---

## CRITICAL: START WITH FRESH TERMINAL

Start this session with a brand new terminal for 100% context. The goal is to investigate what's running on PRODUCTION vs what we've been testing locally.

---

## SESSION 809 PRIORITY: Production vs Local Investigation

### The Discovery

On production, we observed **persona agents actively participating in panel discussions**:

```
Panel: [Learned] Openmeteo - Weather Intelligence
Participants: Resume Optimizer AI, Hidden Job Market Explorer, BrandStrategyAgent, SEO Content Optimizer
Date: 1/24/2026 (today)
13 discussion turns with Tension/Grounded tags
Quality: 100% (Excellent)
```

But locally:
- Persona agents have **0 executions**
- Persona agents have **0 knowledge sources**
- Persona agents have **0 memories**
- **0 learnings in last 24 hours**

### Hypothesis

When we deployed to production, we activated dormant parts of the system that haven't run locally in months. Production is running Celery Beat tasks that:
1. Create `AgentKnowledgeSource` records for ALL agents (including persona)
2. Run `run_multi_agent_conversation` which selects agents with knowledge sources
3. Generate panel discussions using GPT with persona agent metadata
4. Store results in `AgentLearning` with `panel_agents` and `discussion_summary`

### Investigation Tasks

1. **Compare Celery Beat schedules** - What's running on prod vs local?
2. **Check AgentKnowledgeSource counts** - Prod has many, local has only 73 (core agents only)
3. **Check AgentLearning counts** - Prod has 103,245+ in 7 days, local has 0 in 24h
4. **Trace the learning pipeline** - How do persona agents get knowledge sources?
5. **Verify multi-agent conversation task** - Is it running on prod? What agents does it select?

### Key Files to Examine

| File | Purpose |
|------|---------|
| `core/tasks.py:6335` | `run_multi_agent_conversation` - Panel discussion generator |
| `core/tasks.py:6363` | Agent selection query (requires knowledge_sources) |
| `core/conversation_orchestrator.py` | Tension/Grounded validation |
| `core/services/persona_agent_context.py` | PersonaAgentContextBuilder |
| `core/management/commands/load_all_agents_advisors.py` | Persona agent definitions |

### Production Data Points (from UI screenshot)

- Panel title: `[Learned] Openmeteo - Weather Intelligence`
- Topic origin: `learned_from_Job Application Automator`
- 4 agents participated (1 core, 3 persona):
  - `Resume Optimizer AI` (PERSONA - career)
  - `Hidden Job Market Explorer` (PERSONA - job_search)
  - `BrandStrategyAgent` (CORE)
  - `SEO Content Optimizer` (PERSONA - content)
- Discussion tags: `system:pipeline`, `system:agent`, `metric:conversion`, `system:rag`, `system:a/b test`

---

## SESSION 808 COMPLETED

### Focus: Task Audit, Celery Beat Fix, Agent Flow Analysis (6 PRs)

| PR | Issue | Fix |
|----|-------|-----|
| #88 | $334/month pgvector egress | Added `.defer()` to 25 SpiderData queries |
| #89 | 5 weak muscles (dormant agents) | Added 4 Celery Beat schedules |
| #90 | 4 orphaned critical tasks | Registered workflow sync, autonomy engine, content studio |
| #92 | 51 dormant agents | Added 18 agent exercise schedules to settings.py |
| #93 | Handoff update | Documented agent flow analysis |
| #94 | Docs index | Regenerated docs index |

### Critical Discovery: settings.py Overrides celery.py

`CELERY_BEAT_SCHEDULE` in Django settings.py (56→74 entries) **completely overrides** `app.conf.beat_schedule` in celery.py (245 entries).

### Agent Architecture Clarified

| Type | Count | Description |
|------|-------|-------------|
| **Core Agents** | 75 | Python code in `AGENT_MAP`, execute via AgentRouter |
| **Persona Agents** | 139 | Database records, participate via LLM context injection |
| **Total** | 214 | Combined ecosystem |

### Local Stats (may differ significantly from prod!)

- 904 total AgentExecution records
- 73 agents with knowledge sources (all core, 0 persona)
- 7,815 AgentConversation records
- 23 CollaborationSession records (last one Dec 6, 2025)
- 0 AgentLearning in last 24h

---

## QUICK REFERENCE

### Check Production Database (via Railway)
```bash
# If Railway CLI available
railway run python manage.py shell -c "
from core.models_unified_system import Agent, AgentKnowledgeSource, AgentLearning
print(f'Knowledge Sources: {AgentKnowledgeSource.objects.count()}')
print(f'Learnings: {AgentLearning.objects.count()}')
"
```

### Check Local Database
```bash
python manage.py shell -c "
from core.models_unified_system import Agent, AgentKnowledgeSource, AgentLearning
print(f'Knowledge Sources: {AgentKnowledgeSource.objects.count()}')
print(f'Learnings: {AgentLearning.objects.count()}')
"
```

### Find Multi-Agent Conversation Task
```bash
grep -n "run_multi_agent_conversation" core/tasks.py
# Line 6335 - generates panel discussions
# Line 6363 - agent selection (requires knowledge_sources)
```

---

## Previous Sessions Reference

| Session | Focus |
|---------|-------|
| **808** | Task Audit & Agent Flow Analysis - 6 PRs |
| **807** | Production Fixes - 5 PRs (ImageAgent, migrations, timeouts) |
| **806** | Personal Assistant Context Optimization - 4 new services |
| **805** | Learning System Fix - Anomaly detection + learning extraction |
| **804** | Auto-Generated Blog Visibility Fix |
| **803** | LLM Cost Tracking + AI Assistant Performance |

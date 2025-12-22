# Remediation Roadmap - System Audit Action Plan

**Date:** December 21, 2025
**Status:** Complete
**Auditor:** Claude (Session 527)
**Source:** Priority Gap Analysis (59 issues identified)

---

## Executive Summary

This roadmap organizes the 59 identified issues into actionable work streams with clear deliverables. Work is organized into 4 phases spanning immediate fixes through long-term improvements.

---

## Phase A: Critical Security & Core Fixes (Immediate)

**Goal:** Address P0 security vulnerabilities and critical broken features.

### A1. API Security Hardening

**Issues Addressed:** 71 unprotected endpoints, 95 CSRF exemptions, no API docs

| Task | File(s) | Deliverable |
|------|---------|-------------|
| A1.1 Audit all 71 unprotected view files | `core/views*.py` | Security audit report |
| A1.2 Add authentication to sensitive endpoints | Various | Protected endpoints |
| A1.3 Review all CSRF exemptions | Various | Token auth verified |
| A1.4 Create API documentation for critical endpoints | New file | `docs/API.md` |
| A1.5 Add security middleware for all API routes | `core/auth_middleware.py` | Centralized auth |

**Verification:**
```bash
# After fixes, this should return 0
grep -l "def.*(" core/views*.py | while read f; do
  grep -q "@login_required\|@permission_classes" "$f" || echo "$f"
done | wc -l
```

### A2. Revenue Pipeline Activation

**Issues Addressed:** $0 revenue, 0 job applications, broken integration

| Task | File(s) | Deliverable |
|------|---------|-------------|
| A2.1 Connect Opportunity outcomes to Revenue model | `core/super_platform/revenue_integration.py` | Working pipeline |
| A2.2 Wire spider job data to JobApplication | `core/tasks.py` | Job tracking |
| A2.3 Enable Quick Apply functionality | `core/views*.py` | User can apply |
| A2.4 Test complete revenue flow | Manual test | Verified revenue record |

**Verification:**
```python
# After fixes, this should return > 0
from core.models_unified_system import Revenue
Revenue.objects.count()
```

### A3. Agent Database Registration

**Issues Addressed:** CampaignOrchestratorAgent, WorkflowOrchestrationAgent not in DB

| Task | File(s) | Deliverable |
|------|---------|-------------|
| A3.1 Register CampaignOrchestratorAgent | Migration | Agent in DB |
| A3.2 Register WorkflowOrchestrationAgent | Migration | Agent in DB |
| A3.3 Audit all agents for DB registration | Script | All agents registered |
| A3.4 Create auto-registration on agent import | `core/apps.py` | Automatic registration |

**Verification:**
```python
# All agents in router should be in DB
from core.agent_router import AgentRouter
from core.models_unified_system import Agent
router_agents = set(AgentRouter.AGENT_CLASSES.keys())
db_agents = set(Agent.objects.values_list('name', flat=True))
missing = router_agents - db_agents
print(f"Missing: {missing}")  # Should be empty set
```

---

## Phase B: Prompting System Integration (Week 1-2)

**Goal:** Connect all agents to the intelligent prompting system.

### B1. Create Prompting Integration Pattern

| Task | File(s) | Deliverable |
|------|---------|-------------|
| B1.1 Extract ContentWriterAgent pattern | `core/agents/content_writer_agent.py` | Reference implementation |
| B1.2 Create BaseAgent._build_intelligent_prompt() | `core/agents/base_agent.py` | Reusable method |
| B1.3 Add platform context injection | `core/agents/base_agent.py` | PLATFORM_CONTEXT included |
| B1.4 Add memory palace integration | `core/agents/base_agent.py` | Memory in prompts |
| B1.5 Add mood/evolution integration | `core/agents/base_agent.py` | Mood affects responses |

### B2. Roll Out to All Agents

| Task | Agents | Deliverable |
|------|--------|-------------|
| B2.1 Update creation agents | Image, Video, Audio, ThreeD | 4 agents updated |
| B2.2 Update research agents | Research, TrendAnalysis, Opportunity | 3 agents updated |
| B2.3 Update strategy agents | ContentStrategy, Brand, SEO, Social | 4 agents updated |
| B2.4 Update business agents | Competitor, Customer, Marketing | 3 agents updated |
| B2.5 Update development agents | CodeGenerator, FullStack, Review, DevOps | 4 agents updated |
| B2.6 Update remaining agents | All others | 24 agents updated |

**Verification:**
```bash
# After fixes, this should return 42
grep -l "DynamicPromptBuilder\|_build_intelligent_prompt" core/agents/*.py | wc -l
```

---

## Phase C: Learning System Enhancement (Week 2-3)

**Goal:** Improve knowledge retrieval and learning hooks.

### C1. Expand Knowledge Retrieval

| Task | File(s) | Deliverable |
|------|---------|-------------|
| C1.1 Increase knowledge retrieval files | `core/agents/base_agent.py` | More sources checked |
| C1.2 Add cross-agent knowledge queries | `core/agents/base_agent.py` | Agents learn from each other |
| C1.3 Connect revenue_attribution_bridge | `core/learning_bridges/` | Revenue contributes to learning |
| C1.4 Activate personalization_bridge | `core/learning_bridges/` | User prefs influence learning |

### C2. Complete Learning Hook Coverage

| Task | Agents | Deliverable |
|------|--------|-------------|
| C2.1 Add hooks to VideoAgent | `core/agents/video_agent.py` | XP tracking works |
| C2.2 Add hooks to ThreeDAgent | `core/agents/threed_agent.py` | XP tracking works |
| C2.3 Add hooks to remaining 18 agents | Various | All 42 agents have hooks |

### C3. Fix Mood/Evolution System

| Task | File(s) | Deliverable |
|------|---------|-------------|
| C3.1 Set mood_expires_at on existing moods | Migration | Moods have expiry |
| C3.2 Add mood refresh Celery task | `core/tasks.py` | Moods auto-refresh |
| C3.3 Connect mood to more agents | Various | Mood influences responses |

---

## Phase D: Code Quality & Maintainability (Week 3-4)

**Goal:** Improve long-term maintainability.

### D1. Split Monolithic Files

| Task | Source | Result |
|------|--------|--------|
| D1.1 Split tasks.py by category | `core/tasks.py` (17K) | agent_tasks.py, spider_tasks.py, etc. |
| D1.2 Consider frontend componentization | `ai_image_studio.html` (72K) | Modular structure plan |
| D1.3 Organize consumers by feature | `core/*consumer*.py` | Consolidated consumers |

### D2. Consolidate User Models

| Task | Models | Result |
|------|--------|--------|
| D2.1 Audit all 6+ user models | Various | Mapping document |
| D2.2 Choose primary model | - | Single source of truth |
| D2.3 Create migration plan | - | Consolidation strategy |

### D3. Activate Unused Features

| Task | Feature | Result |
|------|---------|--------|
| D3.1 Populate UserPreferences | Preferences tab | Preferences persist |
| D3.2 Activate workflow execution | Workflow system | Workflows running |
| D3.3 Create demo legal case | Legal Assistant | Test data exists |

---

## Quick Reference: Issue → Fix Mapping

| Issue ID | Description | Fix Phase |
|----------|-------------|-----------|
| P0-1 | 71 unprotected endpoints | A1 |
| P0-2 | 95 CSRF exemptions | A1 |
| P0-3 | No API documentation | A1 |
| P0-4 | 41/42 agents hardcoded prompts | B1, B2 |
| P0-5 | $0 revenue tracked | A2 |
| P0-6 | 0 job applications | A2 |
| P0-7 | Knowledge retrieval limited | C1 |
| P1-1 | Monolithic frontend | D1 |
| P1-2 | Massive tasks.py | D1 |
| P1-3 | Agents not in DB | A3 |
| P1-4 | Moods never expire | C3 |
| P1-5 | 0 workflow executions | D3 |

---

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Protected API endpoints | 29% | 100% | Auth decorator coverage |
| Agents using intelligent prompts | 1/42 | 42/42 | DynamicPromptBuilder usage |
| Revenue records | 0 | >0 | Revenue.objects.count() |
| Agents in database | ~40 | 42 | All router agents registered |
| Moods with expiry | 0% | 100% | NULL mood_expires_at count |
| Agents with learning hooks | 22/42 | 42/42 | record_learning usage |

---

## Implementation Order (Recommended)

```
Week 1:
├── A1: API Security Hardening (Critical)
├── A2: Revenue Pipeline Activation (Critical)
└── A3: Agent Database Registration (Quick Win)

Week 2:
├── B1: Create Prompting Integration Pattern
└── B2.1-B2.3: Update 11 agents

Week 3:
├── B2.4-B2.6: Update remaining 31 agents
├── C1: Expand Knowledge Retrieval
└── C2: Complete Learning Hook Coverage

Week 4:
├── C3: Fix Mood/Evolution System
├── D1: Split Monolithic Files
└── D2-D3: Consolidate and Activate
```

---

## Verification Checklist

After completing all phases:

- [ ] All 1,232 API endpoints documented or have auth
- [ ] All 42 agents use intelligent prompting
- [ ] Revenue model has records
- [ ] All agents registered in database
- [ ] All moods have expiry dates
- [ ] All agents have learning hooks
- [ ] tasks.py split into modules
- [ ] User preferences persisting

---

*Generated by Agent 4.2: Remediation Roadmap - December 21, 2025*

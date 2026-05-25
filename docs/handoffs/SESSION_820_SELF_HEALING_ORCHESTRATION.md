---
originating_session: 820
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 820: Self-Healing Orchestration System

**Date:** January 25, 2026
**Focus:** Make the system 100% self-contained - automatically discover audits, assign findings to agents, execute fixes, and verify results without human intervention

---

## Summary

Created a fully autonomous self-healing system that eliminates the need for manual audit posting. The system now:
1. Automatically discovers and imports audit files from `docs/audits/`
2. Assigns open findings to the appropriate agents based on category/path matching
3. Executes remediation tasks via the agent execution pipeline
4. Verifies that fixes actually worked before marking them as verified

---

## The Problem

Previously, the user had to manually post audits to Claude to get fixes implemented. The user requested: *"I shouldn't have to be posting these audits to you, the system should now know how to do everything you do between the context injection, the access to the codebase, and everything else. The system should be 100% self-contained."*

---

## The Solution: 4-Phase Autonomous Remediation Cycle

### Phase 1: Discover & Import
- Scans `docs/audits/` for new audit markdown files
- Uses existing `AuditTrackerService` to parse files
- Extracts structured findings with priority (P0-P3) and category
- Stores in `AuditReport` and `AuditFinding` models (from Session 819)

### Phase 2: Assign to Agents
- Matches findings to agents using `FINDING_TO_AGENT_MAPPING`
- Creates `AuditRemediationTask` records with assigned agent
- Prioritizes P0/P1 findings over P2/P3
- Mapping examples:
  - `security/*` → CodeReviewAgent
  - `documentation/*` → TechnicalDocumentAgent
  - `frontend/*` → FullStackDeveloperAgent
  - `performance/*` → DevOpsAgent

### Phase 3: Execute Remediation
- Retrieves assigned tasks and executes via agent pipeline
- Uses `AgentRouter` to route to the 74 available agents
- Captures agent output and stores in task record
- Marks finding as `in_progress` during execution, `fixed` on success

### Phase 4: Verify Fixes
- For findings marked as `fixed`, runs verification
- Creates `AuditVerificationRun` records
- If verification passes, marks finding as `verified`
- If verification fails, reverts to `in_progress` for retry

---

## Files Created/Modified

### New Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/services/autonomous_remediation_orchestrator.py` | ~600 | Main orchestrator service with 4-phase cycle |
| `core/management/commands/auto_remediate.py` | ~320 | Management command for manual triggering |

### Modified Files

| File | Changes |
|------|---------|
| `core/tasks.py` | +6 Celery tasks for autonomous remediation |
| `core/celery.py` | +5 Celery Beat schedule entries |
| `CLAUDE.md` | Updated stats, added Session 820 info |

---

## New Celery Tasks

```python
@shared_task
def discover_and_import_audits():
    """Phase 1: Discover and import new audit files."""

@shared_task
def assign_open_findings_to_agents():
    """Phase 2: Assign open findings to appropriate agents."""

@shared_task
def execute_remediation_tasks():
    """Phase 3: Execute assigned remediation tasks via agents."""

@shared_task
def verify_completed_fixes():
    """Phase 4: Verify that completed fixes actually worked."""

@shared_task
def run_autonomous_remediation_cycle():
    """Run complete 4-phase remediation cycle."""

@shared_task
def get_remediation_status():
    """Get current autonomous remediation status."""
```

---

## Celery Beat Schedule

| Task | Schedule | Purpose |
|------|----------|---------|
| `discover-and-import-audits` | Daily at midnight | Find new audit files |
| `assign-open-findings-to-agents` | Every 2 hours | Assign unassigned findings |
| `execute-remediation-tasks` | Every 4 hours at :30 | Execute pending tasks |
| `verify-completed-fixes` | Every 6 hours | Verify completed work |
| `run-autonomous-remediation-cycle` | Daily at 2 AM | Full cycle |

---

## Finding-to-Agent Mapping

The `FINDING_TO_AGENT_MAPPING` determines which agent handles each type of finding:

```python
FINDING_TO_AGENT_MAPPING = [
    # Category pattern, path pattern, agent name
    ('security', '*', 'CodeReviewAgent'),
    ('authentication', '*', 'CodeReviewAgent'),
    ('code_quality', 'core/agents/*', 'CodeReviewAgent'),
    ('code_quality', 'frontend/*', 'FullStackDeveloperAgent'),
    ('documentation', '*', 'TechnicalDocumentAgent'),
    ('performance', '*', 'DevOpsAgent'),
    ('database', '*', 'FullStackDeveloperAgent'),
    ('testing', '*', 'CodeReviewAgent'),
    ('api', '*', 'FullStackDeveloperAgent'),
    ('frontend', '*', 'FullStackDeveloperAgent'),
    ('infrastructure', '*', 'DevOpsAgent'),
    ('monitoring', '*', 'DevOpsAgent'),
    ('learning', '*', 'SystemIntelligenceAgent'),
    ('agent', '*', 'CodeReviewAgent'),
    ('spider', '*', 'DevOpsAgent'),
    ('celery', '*', 'DevOpsAgent'),
    ('integration', '*', 'SystemIntelligenceAgent'),
    ('*', '*', 'SystemIntelligenceAgent'),  # Default fallback
]
```

---

## Management Command Usage

```bash
# Show current remediation status
python manage.py auto_remediate --status

# Run full remediation cycle
python manage.py auto_remediate

# Run individual phases
python manage.py auto_remediate --discover
python manage.py auto_remediate --assign
python manage.py auto_remediate --execute
python manage.py auto_remediate --verify

# Preview without making changes
python manage.py auto_remediate --dry-run

# Limit items processed per phase
python manage.py auto_remediate --limit 5

# Verbose output
python manage.py auto_remediate --verbose
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELF-HEALING SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   Phase 1    │────▶│   Phase 2    │────▶│   Phase 3    │   │
│  │   Discover   │     │    Assign    │     │   Execute    │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │ docs/audits/ │     │  FINDING_TO_ │     │ AgentRouter  │   │
│  │   *.md       │     │ AGENT_MAPPING│     │ (74 agents)  │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│                                                   │            │
│                              ┌──────────────┐     │            │
│                              │   Phase 4    │◀────┘            │
│                              │    Verify    │                  │
│                              └──────────────┘                  │
│                                     │                          │
│                                     ▼                          │
│                              ┌──────────────┐                  │
│                              │   Finding    │                  │
│                              │   VERIFIED   │                  │
│                              └──────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Dependencies

Uses existing infrastructure:
- `AuditTrackerService` (Session 819) - Parses audit markdown files
- `AuditReport`, `AuditFinding`, `AuditRemediationTask`, `AuditVerificationRun` models (Session 819)
- `AgentRouter` - Routes to 74 available agents
- `BaseAgent` - Agent execution with workspace integration

---

## Verification

```bash
# Check tasks are registered
python manage.py shell -c "from core.tasks import discover_and_import_audits, run_autonomous_remediation_cycle; print('Tasks registered!')"

# Check service is importable
python manage.py shell -c "from core.services.autonomous_remediation_orchestrator import AutonomousRemediationOrchestrator; print('Service works!')"

# Check command is available
python manage.py auto_remediate --help

# Check Celery Beat schedule on production
railway run python manage.py shell -c "from django_celery_beat.models import PeriodicTask; print([t.name for t in PeriodicTask.objects.filter(name__contains='remediat')])"
```

---

## Feature 2: Tiered Documentation Injection

### Problem
System-aware agents (like TechnicalDocumentAgent) produced generic content because they didn't know actual system stats (74 agents, 77 spiders, 228 Celery tasks, etc.).

### Solution
Added `requires_system_context` flag to BaseAgent. When True, `_build_intelligent_prompt()` injects critical docs (CLAUDE.md, 00-START-NEXT-SESSION.md).

### Implementation

```python
# In BaseAgent (core/agents/base_agent.py)
requires_system_context: bool = False  # Default off for most agents

# In _build_intelligent_prompt()
if self.requires_system_context:
    from core.services.docs_context_builder import get_docs_context_builder
    builder = get_docs_context_builder()
    critical_content = builder._get_critical_docs_content()
    if critical_content:
        prompt_parts.append(f"\n\n{critical_content}")
```

### Agents Enabled (8 total)

| Agent | Reason |
|-------|--------|
| SystemIntelligenceAgent | System health monitoring |
| CTOAgent | Technical planning |
| COOAgent | Operations planning |
| TechnicalDocumentAgent | System audits |
| FullStackDeveloperAgent | Development context |
| CodeReviewAgent | Code quality |
| DevOpsAgent | Infrastructure |
| CreativeDirectorAgent | Creative guidance |

### Token Savings
~70% reduction vs injecting docs into all 74 agents.

---

## PRs Merged

| PR | Title |
|----|-------|
| #159 | feat(Session 820): Self-Healing Orchestration System |
| #160 | feat(Session 820): Tiered documentation injection for system-aware agents |
| #161 | docs(Session 820): Add tiered documentation injection to CLAUDE.md |
| #162 | fix(Session 820): Correct discover phase stats key mapping |

---

## Related Documentation

- [CLAUDE.md](/CLAUDE.md) - Updated with Session 820 stats
- [SESSION_819_AUDIT_TRACKING_MYTHOLOGY_PROMPTING.md](SESSION_819_AUDIT_TRACKING_MYTHOLOGY_PROMPTING.md) - Audit tracking models
- [SESSION_819_DELIVERABLES_MARKETPLACE.md](SESSION_819_DELIVERABLES_MARKETPLACE.md) - Complete Session 819 handoff

---

*Session 820 completed January 25, 2026*
*Making the platform truly self-healing and autonomous*

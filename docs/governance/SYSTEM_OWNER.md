<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
> **Note:** content may be stale (last refreshed Session 814) — this file is **runtime-load-bearing**: `core/services/docs_context_builder.py:184` reads from it. Do NOT move; refresh-in-place when content drifts.

# System Owner Authority

**Document Status:** CANON | **Classification:** INTERNAL | **Session:** 814

---

## System Owner

**Name:** Chris West
**Role:** Founder, System Owner, Final Authority
**Override Level:** Absolute

---

## Authority Framework

### 1. Final Decision Authority

The System Owner has **absolute override authority** over all system decisions:

- All autonomous agent decisions can be reversed
- All gate approvals can be overridden
- All automated actions can be halted
- No agent action is irreversible without explicit human approval

### 2. Human-in-the-Loop Requirements

| Action Type | Approval Required |
|-------------|-------------------|
| **Quick Check** (routine) | Automatic, reviewable |
| **Operational Gate** (standard) | Automatic with notification |
| **Strategic Gate** (significant) | Human review recommended |
| **Red Line** (critical) | **Human approval REQUIRED** |

### 3. Emergency Override Procedures

#### Immediate Halt (SKIN Lock)
```bash
# Manual SKIN lock - halt all workspace writes
python manage.py skin_lock --all

# Lock specific workspace
python manage.py skin_lock --workspace <id>
```

#### Agent Quarantine
```bash
# Disable specific agent via IMMUNE system
python manage.py quarantine_agent --name <AgentName>

# View quarantined agents
python manage.py list_quarantined
```

#### Full System Pause
```bash
# Stop all Celery tasks
celery -A core control shutdown

# Or via Makefile
make stop-celery
```

#### Rollback Capability
- All workspace writes have audit trail via WorkspaceOperation model
- Rollback available for any file write within 30 days
- Access via Human Interface → Workspace → Operations → Rollback

### 4. Escalation Path

```
Agent Decision
     ↓
Gate System (automatic)
     ↓
HumanAttentionItem (surfaces to UI)
     ↓
Human Review (Chris reviews in Human Interface)
     ↓
System Owner Override (if needed)
```

### 5. Notification Channels

| Severity | Channel | Response Time |
|----------|---------|---------------|
| Info | Dashboard only | Next session |
| Warning | Dashboard + Discord | Same day |
| Critical | Dashboard + Discord + Email | Immediate |
| Emergency | All channels + SMS (if configured) | Immediate |

---

## Principles

1. **Human Supremacy** - The system serves the human, not the reverse
2. **Reversibility** - No action should be permanently damaging without consent
3. **Transparency** - All decisions must be auditable and explainable
4. **Gradual Autonomy** - Earn trust through consistent good behavior
5. **Fail Safe** - When in doubt, halt and ask

---

## Kill Switch Triggers

The system should **automatically halt** if any of these occur:

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Cognitive Load | Increases 2 weeks in a row | Pause autonomous actions |
| False Blocks | > 30% false positive rate | Review gate system |
| Cost Spike | > 3x daily average | Halt non-essential tasks |
| Error Rate | > 20% of executions fail | Quarantine affected agents |
| System Owner Request | Any time | Immediate full halt |

---

## Contact

For emergency override outside normal channels:
- Discord: @chriswest
- Email: [configured in settings]

---

*This document is CANON and injected into all agent prompts.*
*Last updated: Session 814*

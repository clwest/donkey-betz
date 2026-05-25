<!-- DOC-POINTER-V1 (Session 1149 — §3 rewrite) -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
> **Last reviewed for drift labeling:** Session 1149 (2026-05-25)
> **Note:** content body was last refreshed Session 814; §3 emergency procedures were rewritten in Session 1149 with current operational paths. This file is **runtime-load-bearing**: `core/services/docs_context_builder.py:184` reads from it (also referenced at `:365` with priority 100). Do NOT move; refresh-in-place when content drifts.
>
> **Session 1149 §3 rewrite scope:**
> - Replaced stale `python manage.py skin_lock` / `quarantine_agent` / `list_quarantined` examples (those commands do not exist in `core/management/commands/`) with current HTTP/Rigby/Django-shell paths.
> - Fixed `make stop-celery` → `make celery-stop` (the actual Makefile target).
> - Authority framework (sections 1-2, 4-5: override authority, HITL approval table, escalation path, notification channels) and the `Kill Switch Triggers` table remain structurally correct as policy intent — only §3 was rewritten.

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

> **Rewritten Session 1149 (2026-05-25)** with current operational paths.
> No CLI `manage.py skin_lock` / `quarantine_agent` / `list_quarantined`
> commands exist — those examples were stale from Session 814. The
> paths below are verified against `core/views_platform_command.py`,
> `core/views_immune.py`, `core/management/commands/immune_check.py`,
> `core/services/pa_tool_schemas.py` (`autopilot_tool`), and the
> current `Makefile`.

#### Immediate Halt — SKIN Lock (blocks agent workspace writes)

There is no `manage.py` command. Lock via HTTP API, Rigby chat, or Django shell.

**HTTP (authenticated user required):**
```bash
# Lock
curl -X POST http://localhost:8000/api/platform/skin-lock/ \
  -H 'Content-Type: application/json' \
  -d '{"action": "lock"}'

# Unlock
curl -X POST http://localhost:8000/api/platform/skin-lock/ \
  -d '{"action": "unlock"}'
```
Implementation: `core/views_platform_command.py:skin_lock_toggle_view` flips the `SkinStatus` singleton (id=1) to `damaged` (locked) or `healthy` (unlocked).

**Django shell (emergency direct path):**
```python
from core.models_skin import SkinStatus
s, _ = SkinStatus.objects.get_or_create(id=1)
s.status = 'damaged'        # 'healthy' to unlock
s.is_healthy = False
s.health_score = 0.0
s.save()
```

**Broader emergency halt** (also creates a CRITICAL `HumanAttentionItem`
for the System Owner — recommended over a raw SKIN lock when the cause
isn't yet known):
```bash
curl -X POST http://localhost:8000/api/platform/emergency-halt/
```
Implementation: `core/views_platform_command.py:emergency_halt_view`.

#### Agent Quarantine — via IMMUNE service

**Inspect current quarantine list (CLI):**
```bash
python manage.py immune_check --quarantine          # human-readable
python manage.py immune_check --quarantine --json   # machine-readable
```

**Add to / release from quarantine (HTTP):**
```bash
# List
curl http://localhost:8000/api/immune/quarantine/

# Add (entity_type=ip|user|agent, entity_value=<identifier>)
curl -X POST http://localhost:8000/api/immune/quarantine/ \
  -H 'Content-Type: application/json' \
  -d '{"entity_type": "agent", "entity_value": "<AgentName>", "reason": "<short reason>", "is_permanent": false}'

# Release
curl -X DELETE http://localhost:8000/api/immune/quarantine/<id>/
```
Implementation: `core/views_immune.py` + `core/services/immune.py:get_immune_system()`.

**Django shell (programmatic):**
```python
from core.services.immune import get_immune_system
im = get_immune_system()
im.get_quarantine_list()
# Add/release: see core/services/immune.py for current method signatures
# (the API surface is stable; methods may add params over time).
```

#### Governance Kill Switch — broader scoped pause (preferred for partial halts)

Rigby's `autopilot_tool` (PA function-calling surface, see
`core/services/pa_tool_schemas.py:autopilot_tool`) is the modern
broad-scope kill switch — narrower than a full SKIN lock, scoped to a
named target.

**Via Rigby (preferred):**
> "Activate a governance kill switch on `<target>` for `<N>` hours,
> reason: `<reason>`."

Targets: `scheduler`, `queue`, `agent_family`, `publishing`, `outbound`, `deploys`.
TTL: default 4h, max 72h. Optional `target_detail` (queue name, agent tag, etc.).
Deactivate with `governance_deactivate_switch` (requires `switch_id`).
Status / audit: `governance_status`, `governance_audit`.

**Direct (HTTP) paths are also available — see `core/services/governance/`
and the `autopilot_tool` schema for the full action enum.**

#### Full System Pause — stop Celery workers

```bash
# Preferred: clean stop via Makefile (matches current target names)
make celery-stop

# Or broker-side shutdown signal (sends shutdown to all workers)
celery -A core control shutdown

# Hard kill if workers won't drain (Session 1142 playbook):
pkill -9 -f celery
rm -f .celery*.pid
```
Restart with `make celery`. Daphne is independent — restart it separately with `make restart-daphne` if needed. See `Makefile` for the full target list.

#### Rollback Capability

- All workspace writes have an audit trail via the `WorkspaceOperation` model (`core/models_skin_layer.py:227`) — fields include `operation_type`, `before_content`, `can_rollback`, and a self-referential `rollback_operation` FK for chained reversals.
- Rollback available for any file write within retention window (operation-level `can_rollback` flag governs eligibility).
- Access via Human Interface → Workspace → Operations → Rollback, or programmatically via `WorkspaceOperation.objects.filter(workspace=..., can_rollback=True)`.

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
*Last updated: Session 814 (body) — §3 emergency procedures rewritten Session 1149 (2026-05-25).*

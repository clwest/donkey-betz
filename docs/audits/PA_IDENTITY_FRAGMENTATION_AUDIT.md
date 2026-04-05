# PA Identity Fragmentation Audit

**Date:** April 5, 2026
**Audited by:** Claude Code + Explore Agent
**Severity:** Medium-High — data fragmentation across 6+ identity variants

---

## Summary

The Personal Assistant saves data under **6 different identity names** depending on which code path executes. This means querying "what has the PA done?" requires searching 6 different strings, and any analytics, audit trails, or attribution reports will miss data unless they account for all variants.

---

## Identity Variants Found

### 1. `"PersonalAssistant"` (Most Common)

The de facto standard, used in the majority of PA code paths.

| File | Line | Context |
|------|------|---------|
| `core/services/unified_pa_entrypoint.py` | 1141, 1189, 1243, 1276, 1311, 1347 | LLM enforcer calls (function calling loop) |
| `core/services/unified_pa_entrypoint.py` | 1722 | Learning/summary generation |
| `core/services/tool_dispatcher.py` | 615 | Operation recording (actor_id) |
| `core/services/tool_dispatcher.py` | 707 | ImpactEvent creation (agent_name) |
| `core/services/operation_recorder.py` | 15 | Default actor_id |
| `core/tasks_conversations.py` | 3480, 3495 | Deliverable save for conversation summaries |
| `core/tasks_agents.py` | 5218 | Agent task execution |
| `core/services/td_handlers_core.py` | 1787 | Pin memory deliverables |
| `core/services/td_handlers_agents.py` | 2896, 3668 | HumanAttentionItem creation (source_agent) |
| `core/epa_handlers_tools.py` | 5148 | Consultation item creation (source_agent) |

**Saves to:** Deliverables, conversation summaries, memory pins, attention items, impact events, workspace operations

### 2. `"PersonalAssistantAgent"` (With "Agent" Suffix)

Used in research & create handler and super platform coordinator.

| File | Line | Context |
|------|------|---------|
| `core/services/td_handlers_core.py` | 387 | Research-and-create deliverables (agent_name) |
| `core/super_platform/coordinator.py` | 992 | Sci-fi context service call (agent_name) |

**Saves to:** Deliverables from research-and-create tool — these show up under a DIFFERENT name than standard PA deliverables.

### 3. `"UnifiedPA"`

Used in LLM enforcement for data analysis/enrichment.

| File | Line | Context |
|------|------|---------|
| `core/services/unified_pa_entrypoint.py` | 3743 | Structured data analysis via LLM enforcer |
| `core/services/unified_pa_entrypoint.py` | 6601 | Direct response fallback via LLM enforcer |

**Saves to:** LLM enforcer logs (routing/throttling attribution)

### 4. `"personal_assistant"` (Lowercase)

| File | Line | Context |
|------|------|---------|
| `core/services/unified_pa_entrypoint.py` | 2097 | Docs context builder call (agent_name) |

**Saves to:** No direct DB saves; used for documentation context fetching. But if any downstream code logs this, it's a different string.

### 5. `"PA"` (Abbreviated)

| File | Line | Context |
|------|------|---------|
| `core/services/td_handlers_ops.py` | 1635 | Experiment creation (created_by) |

**Saves to:** Experiments in ExperimentEngine — attributed to "PA" instead of full name.

### 6. `"human_pa"` (Human-Initiated Variant)

| File | Line | Context |
|------|------|---------|
| `core/services/td_handlers_content.py` | 2327 | Initiative creation (created_by) |

**Saves to:** Initiatives when explicitly requested by user via PA chat.

---

## Data Fragmentation Impact

| Model/Table | Identity Values Used | Impact |
|---|---|---|
| **Deliverable** | `PersonalAssistant`, `PersonalAssistantAgent` | Research, summaries, memory saved under different names |
| **HumanAttentionItem** | `PersonalAssistant` (source_agent) | Attention items only findable under one variant |
| **WorkspaceOperation** | `PersonalAssistant` (actor_id) | Tool call operations split from LLM routing logs |
| **ImpactEvent** | `PersonalAssistant` (agent_name) | ROI attribution incomplete |
| **Experiment** | `PA` (created_by) | Experiments attributed to abbreviation |
| **Initiative** | `human_pa` (created_by) | Can't easily query "all PA-created initiatives" |
| **LLM Enforcer Logs** | `PersonalAssistant`, `UnifiedPA` | Throttling/routing logs fragmented |

---

## Root Causes

1. **No canonical identity constant** — each file hardcodes its own string
2. **Multiple entry points** — UnifiedPAEntrypoint, tool dispatcher handlers, EPA handlers, tasks each set identity independently
3. **Inconsistent naming conventions** — CamelCase, lowercase, abbreviated, suffixed
4. **Different modules, different authors** — built across many sessions without a shared constant
5. **LLM enforcement vs operation recording** use different identities for the same logical actor

---

## Recommended Fix

### Phase 1: Define Canonical Identity (quick)

Add a single constant to `unified_pa_entrypoint.py`:

```python
PA_IDENTITY = "Rigby"  # Canonical PA identity for all data saves
```

Update all 6 variant locations to use this constant.

### Phase 2: Data Migration (medium)

```python
# Consolidate existing records
from django.db.models import Q

pa_variants = ['PersonalAssistant', 'PersonalAssistantAgent', 'UnifiedPA', 
               'personal_assistant', 'PA', 'human_pa']

# For each model with agent_name/source_agent/actor_id/created_by:
Deliverable.objects.filter(agent_name__in=pa_variants).update(agent_name='Rigby')
HumanAttentionItem.objects.filter(source_agent__in=pa_variants).update(source_agent='Rigby')
# ... etc for each affected model
```

### Phase 3: Query Helpers (polish)

Add a utility for backward-compatible querying until migration is complete:

```python
PA_IDENTITY_VARIANTS = frozenset([
    'Rigby', 'PersonalAssistant', 'PersonalAssistantAgent', 
    'UnifiedPA', 'personal_assistant', 'PA', 'human_pa'
])

def pa_filter(**kwargs):
    """Build Q filter that matches any PA identity variant."""
    field = next(iter(kwargs))
    return Q(**{f'{field}__in': PA_IDENTITY_VARIANTS})
```

---

## Estimated Scope

- **Files to modify:** ~12 (the locations listed above)
- **DB records to migrate:** Unknown until we count, but likely thousands
- **Risk:** Low — name changes are cosmetic, no logic changes
- **Priority:** Medium-High — affects analytics, audit trails, and user-facing attribution

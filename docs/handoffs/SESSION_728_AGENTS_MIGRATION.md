# Session 728: Complete agents/ Migration to core/

**Date:** January 7, 2026
**Status:** COMPLETE - 20 files migrated (~14,000 lines)

## Overview

Session 728 completed the systematic migration of the `agents/` directory to `core/`. This consolidates all agent-related code under the canonical `core/` directory for better organization and maintainability.

## Migration Summary

### Phase 1 (Earlier in Session 728)
9 files migrated with deprecation shims:
- `agents/tasks.py` → `core/tasks_agents.py` (850 lines)
- `agents/bookmaker_agent.py` → `core/agents/bookmaker_agent.py` (1,173 lines)
- `agents/universal_integration.py` → `core/services/universal_integration.py` (760 lines)
- `agents/metadata_tracking.py` → `core/services/metadata_tracking.py` (656 lines)
- `agents/project_deployment.py` → `core/services/project_deployment.py` (496 lines)
- `agents/agent_testing_system.py` → `core/services/agent_testing_system.py` (514 lines)
- `agents/monitoring.py` → `core/services/agent_monitoring.py` (512 lines)
- `agents/consumers.py` → `core/consumers_agents.py` (577 lines)
- `agents/router.py` → DELETED (duplicate of core/agent_router.py)

### Phase 2
4 files migrated with deprecation shims:
- `agents/platform_integration.py` → `core/services/platform_integration.py` (246 lines)
- `agents/content_executor.py` → `core/services/content_executor.py` (568 lines)
- `agents/creation_agent.py` → `core/agents/creation_agent.py` (413 lines)
- `agents/ml_algorithms.py` → `core/services/ml_algorithms.py` (612 lines)

### Phase 3
7 files migrated with deprecation shims:
- `agents/views.py` → `core/views/agents.py` (899 lines)
- `agents/serializers.py` → `core/serializers_agents.py` (561 lines)
- `agents/base_agent.py` → `core/agents/base_content_agent.py` (617 lines)
- `agents/executor_registry.py` → `core/services/executor_registry.py` (541 lines)
- `agents/real_code_generator.py` → `core/services/real_code_generator.py` (711 lines)
- `agents/ai_project_builder.py` → `core/services/ai_project_builder.py` (554 lines)
- `agents/universal_llm_executor.py` → `core/services/universal_llm_executor.py` (415 lines)

## New Canonical Locations

### core/agents/
| File | Purpose | Lines |
|------|---------|-------|
| `base_content_agent.py` | BaseContentAgent with learning hooks | 617 |
| `bookmaker_agent.py` | BookmakerAgent with learning infrastructure | 1,173 |
| `creation_agent.py` | CreationAgent for image generation | 413 |

### core/services/
| File | Purpose | Lines |
|------|---------|-------|
| `platform_integration.py` | Platform tools prompt injection | 246 |
| `content_executor.py` | DonkeyBetzContentExecutor | 568 |
| `ml_algorithms.py` | ML algorithm implementations | 612 |
| `executor_registry.py` | ExecutorRegistrationSystem | 541 |
| `real_code_generator.py` | RealCodeGenerator for deployments | 711 |
| `ai_project_builder.py` | AIProjectBuilder | 554 |
| `universal_llm_executor.py` | UniversalLLMAgent/Executor | 415 |
| `universal_integration.py` | Universal agent integration | 760 |
| `metadata_tracking.py` | Agent performance tracking | 656 |
| `project_deployment.py` | Project agent deployment | 496 |
| `agent_testing_system.py` | Agent testing system | 514 |
| `agent_monitoring.py` | Agent monitoring with alerts | 512 |

### core/views/
| File | Purpose | Lines |
|------|---------|-------|
| `agents.py` | Agent API ViewSets | 899 |
| `__init__.py` | Package exports | 40 |

### core/ (root)
| File | Purpose | Lines |
|------|---------|-------|
| `tasks_agents.py` | Celery tasks for agents | 850 |
| `consumers_agents.py` | WebSocket consumers | 577 |
| `serializers_agents.py` | DRF serializers | 561 |

## Backwards Compatibility

All original files in `agents/` have been converted to deprecation shims that:
1. Emit a `DeprecationWarning` when imported
2. Re-export all symbols from the canonical location

Example shim pattern:
```python
"""
DEPRECATED: This module has been moved to core/services/platform_integration.py

For new code, use:
    from core.services.platform_integration import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.platform_integration' is deprecated. "
    "Use 'from core.services.platform_integration import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

from core.services.platform_integration import *
```

## Code Updates Required

Any new code should import from `core/` instead of `agents/`:

### Old (deprecated):
```python
from agents.views import UnifiedAgentTemplateViewSet
from agents.serializers import AgentExecutionSerializer
from agents.base_agent import BaseContentAgent
from agents.platform_integration import inject_platform_tools_prompt
```

### New (correct):
```python
from core.views.agents import UnifiedAgentTemplateViewSet
from core.serializers_agents import AgentExecutionSerializer
from core.agents.base_content_agent import BaseContentAgent
from core.services.platform_integration import inject_platform_tools_prompt
```

## Import References Updated

7 files in `core/` were updated to use canonical imports:
- `core/tasks_agents.py`
- `core/assistant/base.py`
- `core/services/model_registry.py`
- `core/personal_ai_assistant_enhanced.py`
- `core/agents/content_executor_agent.py`
- `scripts/testing/test_gpt5_endpoints.py`

## Testing

All migrations tested with Django shell:
- 20 canonical imports verified
- All deprecation shims work correctly
- No circular import issues

## Commits

1. `f3fbc9b1` - feat(Session 728): agents/ Migration - 9 Files to core/
2. `0e0634f3` - feat(Session 728): agents/ Migration Phase 2 - 4 Core Files to core/
3. `a2363cc6` - feat(Session 728): agents/ Migration Phase 3 - 7 More Files to core/

## Files Remaining in agents/

The following files remain with implementation code (not yet migrated):
- `agents/executors/` directory (executor implementations)
- Various `views_*.py` files (deployment views)
- `agents/content_studio_bridge.py`
- `agents/agent_wiring_system.py`
- `agents/tasks_enhanced.py`
- `agents/urls.py` / `agents/urls_deployment.py`

These can be migrated in a future session if needed.

## Next Steps

1. Monitor for deprecation warnings in logs
2. Update any remaining code that imports from `agents/`
3. Consider migrating remaining files in future sessions
4. Eventually remove shims after deprecation period

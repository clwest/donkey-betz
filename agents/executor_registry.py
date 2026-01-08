"""
DEPRECATED: This module has been moved to core/services/executor_registry.py

For new code, use:
    from core.services.executor_registry import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.executor_registry' is deprecated. "
    "Use 'from core.services.executor_registry import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.executor_registry import (
    ExecutorRegistrationSystem,
    executor_system,
    execute_agent_by_name,
    get_agent_execution_status,
    list_executable_agents,
    initialize_all_agent_executors,
    get_execution_statistics,
    system_health_check,
)

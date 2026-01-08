"""
DEPRECATED: Agent execution tasks have been moved to core/tasks_agents.py

For new code, use:
    from core.tasks_agents import execute_agent, execute_orchestration

This shim maintains backwards compatibility while emitting deprecation warnings.

Session 728: Migrated to core/tasks_agents.py
"""
import warnings

warnings.warn(
    "Importing from 'agents.tasks' is deprecated. "
    "Use 'from core.tasks_agents import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location for backwards compatibility
from core.tasks_agents import (
    AgentExecutionTask,
    send_execution_update,
    execute_agent,
    execute_agent_async,
    cleanup_old_executions,
    check_stuck_executions,
    execute_orchestration,
    _transform_orchestration_for_frontend,
    execute_sports_orchestration,
    update_agent_performance,
)

# Export all for wildcard imports
__all__ = [
    'AgentExecutionTask',
    'send_execution_update',
    'execute_agent',
    'execute_agent_async',
    'cleanup_old_executions',
    'check_stuck_executions',
    'execute_orchestration',
    '_transform_orchestration_for_frontend',
    'execute_sports_orchestration',
    'update_agent_performance',
]

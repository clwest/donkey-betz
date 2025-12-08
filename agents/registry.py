"""
Agent Registry - Backwards Compatibility Shim

DEPRECATED: This module has moved to core/agents/registry.py
This file exists only for backwards compatibility.

Session 392: Migrated to core/agents/registry.py
All imports should use:
    from core.agents.registry import AgentRegistry, get_agent_registry, etc.

This shim re-exports everything from the new location.
"""
import warnings

# Emit deprecation warning on import
warnings.warn(
    "agents.registry is deprecated. Use 'from core.agents.registry import ...' instead. "
    "This shim will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the canonical location
from core.agents.registry import (
    # Dataclasses
    AgentCapability,
    AgentPerformanceStats,
    RegistryStats,

    # Main class
    AgentRegistry,

    # Singleton accessor
    get_agent_registry,

    # Convenience functions
    get_agent,
    list_agents,
    find_best_agent,
    execute_agent,

    # Global instance
    agent_registry,
)

__all__ = [
    'AgentCapability',
    'AgentPerformanceStats',
    'RegistryStats',
    'AgentRegistry',
    'get_agent_registry',
    'get_agent',
    'list_agents',
    'find_best_agent',
    'execute_agent',
    'agent_registry',
]

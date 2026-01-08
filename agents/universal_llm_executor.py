"""
DEPRECATED: This module has been moved to core/services/universal_llm_executor.py

For new code, use:
    from core.services.universal_llm_executor import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.universal_llm_executor' is deprecated. "
    "Use 'from core.services.universal_llm_executor import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.universal_llm_executor import (
    UniversalLLMAgent,
    UniversalAgentExecutor,
    get_universal_executor,
    execute_agent_with_llm,
)

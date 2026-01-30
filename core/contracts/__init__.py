"""
Core Contracts - Session 872
============================

Structured output contracts that enforce consistent, validated outputs
from agents and services.

Contracts ensure:
- No contradictory states (e.g., "Complete" + "Insufficient Data")
- Specific deliverables (not vague)
- Accountability (owner, timeline)
- Confidence with reasoning
- Escalation paths for blocked work

Available contracts:
- ResearchContract: For all research operations
- ExecutionMandate: For decision enforcement after debate/synthesis
- SynthesisContract: For structured debate synthesis output
"""

from .research_contract import (
    ResearchContract,
    ResearchStatus,
    ConfidenceLevel,
    generate_deliverables_from_goal,
)

from .execution_mandate import (
    ExecutionMandate,
    MandateStatus,
    DecisionConfidence,
    SpawnedTask,
    extract_experiments_from_debate,
    extract_kill_criteria_from_debate,
)

from .synthesis_contract import (
    SynthesisContract,
    SynthesisQuality,
    ConsensusLevel,
    OwnerAssignment,
    extract_synthesis_from_decision_summary,
)

__all__ = [
    # Research Contract
    'ResearchContract',
    'ResearchStatus',
    'ConfidenceLevel',
    'generate_deliverables_from_goal',
    # Execution Mandate
    'ExecutionMandate',
    'MandateStatus',
    'DecisionConfidence',
    'SpawnedTask',
    'extract_experiments_from_debate',
    'extract_kill_criteria_from_debate',
    # Synthesis Contract
    'SynthesisContract',
    'SynthesisQuality',
    'ConsensusLevel',
    'OwnerAssignment',
    'extract_synthesis_from_decision_summary',
]

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
"""

from .research_contract import (
    ResearchContract,
    ResearchStatus,
    ConfidenceLevel,
    generate_deliverables_from_goal,
)

__all__ = [
    'ResearchContract',
    'ResearchStatus',
    'ConfidenceLevel',
    'generate_deliverables_from_goal',
]

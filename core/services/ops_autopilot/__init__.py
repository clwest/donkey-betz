"""
Ops Autopilot package — split from monolithic ops_autopilot.py.

All classes are re-exported here for backwards compatibility.
Consumers can continue to use:
    from core.services.ops_autopilot import OpsAutopilot
"""

from core.services.ops_autopilot.config import AutopilotConfig  # noqa: F401
from core.services.ops_autopilot.core import OpsAutopilot  # noqa: F401
from core.services.ops_autopilot.verification import ActionVerifier, VerifiableAction  # noqa: F401
from core.services.ops_autopilot.remediation import RemediationEngine, TimeoutRemediationPlaybook, DeliberationRemediationPlaybook  # noqa: F401
from core.services.ops_autopilot.governance import BacklogGovernor, PolicyOptimizer, PolicyArbitrator, ReleaseGovernor, GovernanceEngine  # noqa: F401
from core.services.ops_autopilot.budget import BudgetController, ROIEnforcer, BudgetAwareScheduler  # noqa: F401
from core.services.ops_autopilot.impact import ImpactCollector, PortfolioAllocator, GoalAwareAllocator, MultiTouchAttributor, AttributionDebtController  # noqa: F401
from core.services.ops_autopilot.experiment import ExperimentEngine  # noqa: F401
from core.services.ops_autopilot.revenue import RevenuePipelineAutomator, OutboundLeadEngine, OutreachSequencer, CloseTheDealEngine, RevenueOrchestrator, ClosePackAutonomyEngine  # noqa: F401
from core.services.ops_autopilot.engagement import EngagementEngine, MeetingEngine, EngagementAutonomyEngine  # noqa: F401
from core.services.ops_autopilot.intelligence import KnowledgeEngine, GrowthEngine, CapacityEngine, SecurityEngine, ComplianceEngine, DataIntegrityEngine, ValueRealizationEngine  # noqa: F401

__all__ = [
    "AutopilotConfig",
    "OpsAutopilot",
    "ActionVerifier",
    "VerifiableAction",
    "RemediationEngine",
    "TimeoutRemediationPlaybook",
    "DeliberationRemediationPlaybook",
    "BacklogGovernor",
    "PolicyOptimizer",
    "PolicyArbitrator",
    "ReleaseGovernor",
    "GovernanceEngine",
    "BudgetController",
    "ROIEnforcer",
    "BudgetAwareScheduler",
    "ImpactCollector",
    "PortfolioAllocator",
    "GoalAwareAllocator",
    "MultiTouchAttributor",
    "AttributionDebtController",
    "ExperimentEngine",
    "RevenuePipelineAutomator",
    "OutboundLeadEngine",
    "OutreachSequencer",
    "CloseTheDealEngine",
    "RevenueOrchestrator",
    "ClosePackAutonomyEngine",
    "EngagementEngine",
    "MeetingEngine",
    "EngagementAutonomyEngine",
    "KnowledgeEngine",
    "GrowthEngine",
    "CapacityEngine",
    "SecurityEngine",
    "ComplianceEngine",
    "DataIntegrityEngine",
    "ValueRealizationEngine",
]

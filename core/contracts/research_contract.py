"""
Research Contract - Session 872
================================

Enforces consistent, structured output for all research operations.
Based on feedback: research outputs should behave like internal audit tickets,
not essays.

Key principles:
1. Binary status - no contradictions ("Complete" + "Insufficient Data" is invalid)
2. Auto-generated deliverables - specific, not vague
3. Timeline and ownership - always present
4. Confidence with reason - know reliability
5. Escalation path - never silent failures

Usage:
    from core.contracts.research_contract import ResearchContract, ResearchStatus

    contract = ResearchContract.create(
        goal="Analyze experiment halt rules",
        status=ResearchStatus.BLOCKED,
        blocked_on="ExperimentExecution logs unavailable",
        owner="ResearchAgent",
        confidence=0.3,
        confidence_reason="Missing 90-day execution logs"
    )

    # Validate before returning
    contract.validate()  # Raises if invalid

    # Convert to dict for AgentResult
    result_data = contract.to_dict()
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResearchStatus(Enum):
    """
    Binary research status - no ambiguity.

    BLOCKED: Cannot proceed without external input/data
    IN_PROGRESS: Actively working, not yet complete
    COMPLETE: All deliverables satisfied, findings verified
    FAILED: Unrecoverable error, requires human intervention
    """
    BLOCKED = "BLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class ConfidenceLevel(Enum):
    """Confidence levels with semantic meaning."""
    VERY_LOW = 0.2   # Missing critical data
    LOW = 0.4        # Partial data, high uncertainty
    MEDIUM = 0.6     # Reasonable data, some gaps
    HIGH = 0.8       # Strong data, minor gaps
    VERY_HIGH = 0.95 # Comprehensive data, verified


@dataclass
class ResearchContract:
    """
    Structured contract for research outputs.

    Every research task MUST output this contract.
    No exceptions. This collapses loops and ensures accountability.
    """

    # === REQUIRED FIELDS ===

    # Goal: What are we trying to learn/prove?
    goal: str

    # Status: Binary, no contradictions
    status: ResearchStatus

    # Owner: Who is accountable?
    owner: str

    # Confidence: How reliable is this output?
    confidence: float  # 0.0 - 1.0
    confidence_reason: str  # "Low due to missing logs"

    # === CONDITIONAL FIELDS ===

    # Required if status is BLOCKED
    blocked_on: Optional[str] = None  # "DataExportAgent needs to provide logs"

    # Required if status is BLOCKED or IN_PROGRESS
    inputs_required: List[str] = field(default_factory=list)

    # Escalation: What happens if blocked for too long?
    escalation_path: Optional[str] = None  # "If no data in 24h -> SystemAdminAgent"
    escalation_after_hours: Optional[int] = None  # 24

    # === DELIVERABLES ===

    # Specific, auto-generated deliverables (not vague)
    # BAD: "Define specific deliverables"
    # GOOD: ["Table of halt rules vs firing frequency", "Top 5 false-positives"]
    deliverables: List[str] = field(default_factory=list)

    # Which deliverables are complete?
    deliverables_complete: List[str] = field(default_factory=list)

    # === TIMELINE ===

    # When do we expect completion?
    eta: Optional[str] = None  # "48h after data availability"

    # When should this be reviewed?
    review_date: Optional[str] = None

    # What triggers the next action?
    next_trigger: Optional[str] = None  # "DataExportAgent completes"

    # === FINDINGS (if status is COMPLETE or IN_PROGRESS) ===

    findings: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    data_gaps: List[str] = field(default_factory=list)

    # === METADATA ===

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    model_grounded_in: Optional[str] = None  # "core.models_experiment.ExperimentExecution"
    related_agents: List[str] = field(default_factory=list)  # Agents that may need to be involved

    def validate(self) -> bool:
        """
        Validate the contract for consistency.

        Raises:
            ValueError: If contract is invalid

        Returns:
            True if valid
        """
        errors = []

        # 1. Goal is required and non-empty
        if not self.goal or not self.goal.strip():
            errors.append("Goal is required")

        # 2. Owner is required
        if not self.owner or not self.owner.strip():
            errors.append("Owner is required")

        # 3. Confidence must be valid
        if not 0.0 <= self.confidence <= 1.0:
            errors.append(f"Confidence must be 0.0-1.0, got {self.confidence}")

        if not self.confidence_reason:
            errors.append("Confidence reason is required")

        # 4. BLOCKED status requires blocked_on
        if self.status == ResearchStatus.BLOCKED:
            if not self.blocked_on:
                errors.append("BLOCKED status requires 'blocked_on' field")
            if not self.escalation_path:
                errors.append("BLOCKED status requires 'escalation_path' field")

        # 5. COMPLETE status cannot have blocking info
        if self.status == ResearchStatus.COMPLETE:
            if self.blocked_on:
                errors.append("COMPLETE status cannot have 'blocked_on' - contradictory")
            if not self.deliverables:
                errors.append("COMPLETE status requires deliverables list")
            # All deliverables should be in deliverables_complete
            if self.deliverables and len(self.deliverables_complete) < len(self.deliverables):
                incomplete = set(self.deliverables) - set(self.deliverables_complete)
                if incomplete:
                    errors.append(f"COMPLETE status but deliverables incomplete: {incomplete}")

        # 6. Deliverables should be specific, not vague
        vague_patterns = [
            "define specific",
            "determine",
            "figure out",
            "investigate",
            "look into",
            "research",
            "analyze",  # Too vague on its own
        ]
        for deliverable in self.deliverables:
            deliverable_lower = deliverable.lower()
            # Check if deliverable is just a vague verb phrase
            if any(deliverable_lower.startswith(pattern) for pattern in vague_patterns):
                if len(deliverable.split()) < 5:  # Very short = probably vague
                    errors.append(f"Deliverable too vague: '{deliverable}'. Be specific.")

        # 7. IN_PROGRESS should have eta or next_trigger
        if self.status == ResearchStatus.IN_PROGRESS:
            if not self.eta and not self.next_trigger:
                errors.append("IN_PROGRESS status should have 'eta' or 'next_trigger'")

        if errors:
            error_msg = "; ".join(errors)
            logger.warning(f"Research Contract validation failed: {error_msg}")
            raise ValueError(f"Invalid Research Contract: {error_msg}")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary for AgentResult data."""
        return {
            'contract_type': 'research',
            'contract_version': '1.0',

            # Core fields
            'goal': self.goal,
            'status': self.status.value,
            'owner': self.owner,

            # Confidence
            'confidence': self.confidence,
            'confidence_level': self._get_confidence_level(),
            'confidence_reason': self.confidence_reason,

            # Blocking info
            'blocked_on': self.blocked_on,
            'inputs_required': self.inputs_required,
            'escalation_path': self.escalation_path,
            'escalation_after_hours': self.escalation_after_hours,

            # Deliverables
            'deliverables': self.deliverables,
            'deliverables_complete': self.deliverables_complete,
            'deliverables_pending': list(set(self.deliverables) - set(self.deliverables_complete)),

            # Timeline
            'eta': self.eta,
            'review_date': self.review_date,
            'next_trigger': self.next_trigger,

            # Findings
            'findings': self.findings,
            'recommendations': self.recommendations,
            'sources_used': self.sources_used,
            'data_gaps': self.data_gaps,

            # Metadata
            'created_at': self.created_at,
            'model_grounded_in': self.model_grounded_in,
            'related_agents': self.related_agents,
        }

    def _get_confidence_level(self) -> str:
        """Get human-readable confidence level."""
        if self.confidence >= 0.9:
            return "Very High"
        elif self.confidence >= 0.7:
            return "High"
        elif self.confidence >= 0.5:
            return "Medium"
        elif self.confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"

    def to_markdown(self) -> str:
        """Generate markdown representation of the contract."""
        md = f"# Research Contract\n\n"
        md += f"**Status:** {self.status.value}\n"
        md += f"**Owner:** {self.owner}\n"
        md += f"**Confidence:** {self.confidence:.0%} ({self._get_confidence_level()}) - {self.confidence_reason}\n\n"

        md += f"## Goal\n\n{self.goal}\n\n"

        if self.inputs_required:
            md += "## Inputs Required\n\n"
            for inp in self.inputs_required:
                md += f"- {inp}\n"
            md += "\n"

        if self.blocked_on:
            md += f"## Blocked On\n\n{self.blocked_on}\n\n"
            if self.escalation_path:
                md += f"**Escalation:** {self.escalation_path}\n\n"

        if self.deliverables:
            md += "## Deliverables\n\n"
            for d in self.deliverables:
                status = "[x]" if d in self.deliverables_complete else "[ ]"
                md += f"- {status} {d}\n"
            md += "\n"

        if self.eta or self.next_trigger:
            md += "## Timeline\n\n"
            if self.eta:
                md += f"- **ETA:** {self.eta}\n"
            if self.next_trigger:
                md += f"- **Next Trigger:** {self.next_trigger}\n"
            if self.review_date:
                md += f"- **Review Date:** {self.review_date}\n"
            md += "\n"

        if self.findings:
            md += "## Findings\n\n"
            for key, value in self.findings.items():
                md += f"### {key}\n\n{value}\n\n"

        if self.recommendations:
            md += "## Recommendations\n\n"
            for i, rec in enumerate(self.recommendations, 1):
                md += f"{i}. {rec}\n"
            md += "\n"

        if self.data_gaps:
            md += "## Data Gaps\n\n"
            for gap in self.data_gaps:
                md += f"- {gap}\n"
            md += "\n"

        if self.related_agents:
            md += f"## Related Agents\n\n"
            md += ", ".join(self.related_agents) + "\n\n"

        if self.model_grounded_in:
            md += f"---\n\n*Grounded in:* `{self.model_grounded_in}`\n"

        return md

    @classmethod
    def create(
        cls,
        goal: str,
        status: ResearchStatus,
        owner: str,
        confidence: float,
        confidence_reason: str,
        **kwargs
    ) -> 'ResearchContract':
        """
        Factory method to create a validated contract.

        Args:
            goal: Research goal
            status: Current status
            owner: Accountable agent
            confidence: 0.0-1.0
            confidence_reason: Why this confidence level
            **kwargs: Additional fields

        Returns:
            Validated ResearchContract
        """
        contract = cls(
            goal=goal,
            status=status,
            owner=owner,
            confidence=confidence,
            confidence_reason=confidence_reason,
            **kwargs
        )

        # Validate on creation
        contract.validate()

        return contract

    @classmethod
    def create_blocked(
        cls,
        goal: str,
        owner: str,
        blocked_on: str,
        escalation_path: str,
        inputs_required: List[str],
        confidence_reason: str = "Cannot assess - missing required data",
        **kwargs
    ) -> 'ResearchContract':
        """
        Factory for BLOCKED status contracts.

        Forces proper blocking documentation.
        """
        return cls.create(
            goal=goal,
            status=ResearchStatus.BLOCKED,
            owner=owner,
            confidence=0.2,  # Low confidence when blocked
            confidence_reason=confidence_reason,
            blocked_on=blocked_on,
            escalation_path=escalation_path,
            inputs_required=inputs_required,
            **kwargs
        )

    @classmethod
    def create_complete(
        cls,
        goal: str,
        owner: str,
        deliverables: List[str],
        findings: Dict[str, Any],
        confidence: float,
        confidence_reason: str,
        recommendations: List[str] = None,
        sources_used: List[str] = None,
        **kwargs
    ) -> 'ResearchContract':
        """
        Factory for COMPLETE status contracts.

        Forces proper completion documentation.
        """
        return cls.create(
            goal=goal,
            status=ResearchStatus.COMPLETE,
            owner=owner,
            confidence=confidence,
            confidence_reason=confidence_reason,
            deliverables=deliverables,
            deliverables_complete=deliverables,  # All complete
            findings=findings,
            recommendations=recommendations or [],
            sources_used=sources_used or [],
            **kwargs
        )


def generate_deliverables_from_goal(goal: str, research_type: str = 'general') -> List[str]:
    """
    Auto-generate specific deliverables from a research goal.

    This prevents vague deliverables like "Define specific deliverables".

    Args:
        goal: The research goal
        research_type: Type of research (market, technical, competitor, etc.)

    Returns:
        List of specific, actionable deliverables
    """
    deliverables = []

    goal_lower = goal.lower()

    # Pattern matching for common research types
    if 'experiment' in goal_lower or 'halt' in goal_lower or 'rule' in goal_lower:
        deliverables = [
            f"Table: Halt rules vs firing frequency (90 days)",
            f"List: Top 5 false-positive rules with evidence",
            f"YAML: Proposed configuration changes",
            f"Gap analysis: Missing instrumentation points",
        ]

    elif 'market' in goal_lower or 'competitor' in goal_lower:
        deliverables = [
            f"Competitor matrix: Features, pricing, positioning",
            f"Market size estimate with methodology",
            f"Top 3 opportunities with evidence",
            f"Risk assessment: Top 5 threats",
        ]

    elif 'trend' in goal_lower or 'analysis' in goal_lower:
        deliverables = [
            f"Trend report: Top 10 findings with sources",
            f"Sentiment analysis summary",
            f"Actionable insights (max 5)",
            f"Data sources and methodology",
        ]

    elif 'technical' in goal_lower or 'architecture' in goal_lower:
        deliverables = [
            f"Architecture diagram or description",
            f"Technical requirements list",
            f"Implementation risks and mitigations",
            f"Dependency analysis",
        ]

    elif 'user' in goal_lower or 'customer' in goal_lower:
        deliverables = [
            f"User persona summary",
            f"Pain points list (ranked by severity)",
            f"Feature requests (grouped by theme)",
            f"Competitive alternatives users mention",
        ]

    else:
        # Generic but still specific
        deliverables = [
            f"Executive summary (max 200 words)",
            f"Key findings list (max 10 items)",
            f"Data sources with links",
            f"Recommended next steps (max 3)",
        ]

    return deliverables

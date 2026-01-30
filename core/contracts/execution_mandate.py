"""
Execution Mandate Contract - Session 872
=========================================

The "Prefrontal Cortex" of the system.

Enforces decision closure after synthesis/debate.
Prevents endless loops of "further analysis recommended."

Key principles:
1. Decisive - Must pick a path, not hedge
2. Owned - Someone is accountable
3. Killable - Has explicit failure criteria
4. Time-bound - Has a deadline
5. Actionable - Spawns actual tasks

Based on ChatGPT feedback:
- "Right now you have Cortex (thinking), Sensors (spiders), Speech (blogs/docs)
   But you're missing: Prefrontal Cortex (decisions)"
- "You need a meta-agent that says: 'Enough. Do X.'"

Usage:
    from core.contracts.execution_mandate import ExecutionMandate, MandateStatus

    mandate = ExecutionMandate.create(
        chosen_path="Build salary negotiation MVP",
        reason="Strongest market signal + lowest risk",
        decision_owner="SalaryNegotiationExpert",
        experiments=["A/B test with 50 users"],
        kill_criteria=["<10% engagement after 7 days"],
        deadline="2026-02-05"
    )

    # Validate before returning
    mandate.validate()  # Raises if invalid

    # Convert to dict
    result_data = mandate.to_dict()
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class MandateStatus(Enum):
    """
    Mandate execution status.

    ACTIVE: Mandate is in effect, work is proceeding
    PAUSED: Temporarily halted pending external input
    KILLED: Kill criteria met, mandate terminated
    COMPLETED: Success criteria met, mandate fulfilled
    SUPERSEDED: Replaced by a new mandate
    """
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    KILLED = "KILLED"
    COMPLETED = "COMPLETED"
    SUPERSEDED = "SUPERSEDED"


class DecisionConfidence(Enum):
    """How confident is this decision?"""
    LOW = 0.4      # Weak signal, high uncertainty
    MEDIUM = 0.6   # Reasonable signal, some gaps
    HIGH = 0.8     # Strong signal, minor gaps
    CERTAIN = 0.95 # Overwhelming evidence


@dataclass
class SpawnedTask:
    """A task spawned by the mandate."""
    task_id: Optional[str] = None  # Populated after creation
    agent: str = ""                 # Which agent executes this
    action: str = ""                # What to do
    deadline: Optional[str] = None  # When it should complete
    depends_on: List[str] = field(default_factory=list)  # Task IDs this depends on
    priority: int = 1               # 1=highest, 5=lowest

    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'agent': self.agent,
            'action': self.action,
            'deadline': self.deadline,
            'depends_on': self.depends_on,
            'priority': self.priority,
        }


@dataclass
class ExecutionMandate:
    """
    Structured mandate for decision enforcement.

    After debate/synthesis, this contract FORCES a decision.
    No "further analysis recommended" allowed.
    """

    # === REQUIRED: THE DECISION ===

    # What path did we choose? Must be specific and actionable.
    # BAD: "Consider building a feature"
    # GOOD: "Build salary negotiation MVP targeting job seekers"
    chosen_path: str

    # Why this path? Must reference evidence from debate.
    # BAD: "Seems like a good idea"
    # GOOD: "3/4 agents agreed + market data shows 40% demand"
    reason: str

    # Who owns this decision? An agent or role that's accountable.
    decision_owner: str

    # === REQUIRED: FAILURE CONDITIONS ===

    # What would prove this decision wrong?
    # These MUST be measurable and time-bound.
    # BAD: "If users don't like it"
    # GOOD: "<10% engagement after 7 days", "No signups in 48h"
    kill_criteria: List[str]

    # When must we see results by?
    deadline: str  # ISO format date or relative ("48h", "7d")

    # === REQUIRED: EXPERIMENTS ===

    # What experiments will test this decision?
    # Must be specific and actionable.
    experiments: List[str]

    # === OPTIONAL: EXECUTION DETAILS ===

    # What was rejected and why? (prevents re-litigation)
    rejected_paths: Dict[str, str] = field(default_factory=dict)  # path -> reason

    # What risks were acknowledged?
    acknowledged_risks: List[str] = field(default_factory=list)

    # Confidence level in this decision
    confidence: float = 0.6
    confidence_reason: str = ""

    # Tasks spawned from this mandate
    spawned_tasks: List[SpawnedTask] = field(default_factory=list)

    # Status tracking
    status: MandateStatus = MandateStatus.ACTIVE

    # Source: what triggered this mandate?
    source_conversation_id: Optional[str] = None
    source_synthesis_id: Optional[str] = None

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "DecisionEnforcerAgent"

    # === ANTI-PATTERNS TO BLOCK ===

    # Phrases that indicate non-decision (will fail validation)
    WEASEL_PHRASES = [
        "further analysis",
        "more research",
        "consider",
        "might want to",
        "could potentially",
        "should explore",
        "needs investigation",
        "requires study",
        "pending review",
        "to be determined",
        "TBD",
        "we should validate",
        "recommend exploring",
    ]

    def validate(self) -> bool:
        """
        Validate the mandate for decisiveness and completeness.

        Raises:
            ValueError: If mandate is invalid

        Returns:
            True if valid
        """
        errors = []

        # 1. Chosen path must be specific and not contain weasel phrases
        if not self.chosen_path or len(self.chosen_path.strip()) < 10:
            errors.append("Chosen path too vague - must be specific (10+ chars)")

        path_lower = self.chosen_path.lower()
        for weasel in self.WEASEL_PHRASES:
            if weasel in path_lower:
                errors.append(f"Chosen path contains weasel phrase: '{weasel}' - be decisive")

        # 2. Reason must reference evidence
        if not self.reason or len(self.reason.strip()) < 20:
            errors.append("Reason too short - must explain why with evidence")

        # 3. Decision owner required
        if not self.decision_owner or not self.decision_owner.strip():
            errors.append("Decision owner required - someone must be accountable")

        # 4. Kill criteria required and must be measurable
        if not self.kill_criteria:
            errors.append("Kill criteria required - how do we know if this fails?")
        else:
            for criterion in self.kill_criteria:
                # Should contain a number or comparison
                if not re.search(r'\d|<|>|%|within|after|before', criterion.lower()):
                    errors.append(f"Kill criterion not measurable: '{criterion}' - add metrics/timeframes")

        # 5. Deadline required
        if not self.deadline:
            errors.append("Deadline required - when must we see results?")

        # 6. Experiments required
        if not self.experiments:
            errors.append("Experiments required - how do we test this decision?")
        elif len(self.experiments) < 1:
            errors.append("At least 1 experiment required")

        # 7. Confidence reason required if confidence is set
        if self.confidence < 0.5 and not self.confidence_reason:
            errors.append("Low confidence requires explanation in confidence_reason")

        if errors:
            error_msg = "; ".join(errors)
            logger.warning(f"Execution Mandate validation failed: {error_msg}")
            raise ValueError(f"Invalid Execution Mandate: {error_msg}")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert mandate to dictionary."""
        return {
            'contract_type': 'execution_mandate',
            'contract_version': '1.0',

            # Core decision
            'chosen_path': self.chosen_path,
            'reason': self.reason,
            'decision_owner': self.decision_owner,

            # Failure conditions
            'kill_criteria': self.kill_criteria,
            'deadline': self.deadline,

            # Testing
            'experiments': self.experiments,

            # Context
            'rejected_paths': self.rejected_paths,
            'acknowledged_risks': self.acknowledged_risks,
            'confidence': self.confidence,
            'confidence_reason': self.confidence_reason,

            # Execution
            'spawned_tasks': [t.to_dict() for t in self.spawned_tasks],
            'status': self.status.value,

            # Source
            'source_conversation_id': self.source_conversation_id,
            'source_synthesis_id': self.source_synthesis_id,

            # Metadata
            'created_at': self.created_at,
            'created_by': self.created_by,
        }

    def to_markdown(self) -> str:
        """Generate markdown representation of the mandate."""
        md = f"# Execution Mandate\n\n"
        md += f"**Status:** {self.status.value}\n"
        md += f"**Owner:** {self.decision_owner}\n"
        md += f"**Deadline:** {self.deadline}\n"
        md += f"**Confidence:** {self.confidence:.0%}"
        if self.confidence_reason:
            md += f" - {self.confidence_reason}"
        md += "\n\n"

        md += f"## Decision\n\n{self.chosen_path}\n\n"
        md += f"### Rationale\n\n{self.reason}\n\n"

        if self.experiments:
            md += "## Experiments\n\n"
            for i, exp in enumerate(self.experiments, 1):
                md += f"{i}. {exp}\n"
            md += "\n"

        if self.kill_criteria:
            md += "## Kill Criteria\n\n"
            md += "_If any of these are true, terminate this initiative:_\n\n"
            for criterion in self.kill_criteria:
                md += f"- [ ] {criterion}\n"
            md += "\n"

        if self.rejected_paths:
            md += "## Rejected Alternatives\n\n"
            for path, reason in self.rejected_paths.items():
                md += f"- **{path}**: {reason}\n"
            md += "\n"

        if self.acknowledged_risks:
            md += "## Acknowledged Risks\n\n"
            for risk in self.acknowledged_risks:
                md += f"- {risk}\n"
            md += "\n"

        if self.spawned_tasks:
            md += "## Spawned Tasks\n\n"
            for task in self.spawned_tasks:
                status = "pending" if not task.task_id else "created"
                md += f"- [{status}] {task.agent}: {task.action}\n"
            md += "\n"

        md += f"---\n\n*Created: {self.created_at}*\n"

        return md

    @classmethod
    def create(
        cls,
        chosen_path: str,
        reason: str,
        decision_owner: str,
        kill_criteria: List[str],
        deadline: str,
        experiments: List[str],
        **kwargs
    ) -> 'ExecutionMandate':
        """
        Factory method to create a validated mandate.

        Args:
            chosen_path: The decision made
            reason: Why this path was chosen
            decision_owner: Who is accountable
            kill_criteria: When to terminate
            deadline: When results are expected
            experiments: How to test the decision
            **kwargs: Additional fields

        Returns:
            Validated ExecutionMandate
        """
        mandate = cls(
            chosen_path=chosen_path,
            reason=reason,
            decision_owner=decision_owner,
            kill_criteria=kill_criteria,
            deadline=deadline,
            experiments=experiments,
            **kwargs
        )

        # Validate on creation
        mandate.validate()

        return mandate

    @classmethod
    def from_debate_log(
        cls,
        debate_messages: List[Dict[str, Any]],
        synthesis: Optional[Dict[str, Any]] = None
    ) -> 'ExecutionMandate':
        """
        Extract mandate from debate transcript.

        This is a stub - the DecisionEnforcerAgent uses LLM to do this.
        """
        raise NotImplementedError(
            "Use DecisionEnforcerAgent.execute() to create mandates from debates"
        )

    def add_task(
        self,
        agent: str,
        action: str,
        deadline: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        priority: int = 1
    ) -> SpawnedTask:
        """Add a task to be spawned from this mandate."""
        task = SpawnedTask(
            agent=agent,
            action=action,
            deadline=deadline or self.deadline,
            depends_on=depends_on or [],
            priority=priority
        )
        self.spawned_tasks.append(task)
        return task

    def mark_killed(self, reason: str) -> None:
        """Mark mandate as killed due to kill criteria being met."""
        self.status = MandateStatus.KILLED
        self.acknowledged_risks.append(f"KILLED: {reason}")

    def mark_completed(self) -> None:
        """Mark mandate as successfully completed."""
        self.status = MandateStatus.COMPLETED


def extract_experiments_from_debate(messages: List[Dict[str, Any]]) -> List[str]:
    """
    Extract proposed experiments from debate transcript.

    Looks for patterns like:
    - "We should test..."
    - "A/B test..."
    - "Pilot with..."
    - "Experiment:"
    """
    experiments = []
    experiment_patterns = [
        r'(?:we should |let\'s |need to )?(?:test|experiment|pilot|validate|try)[:\s]+([^.]+)',
        r'A/B test[:\s]+([^.]+)',
        r'experiment[:\s]+([^.]+)',
    ]

    for msg in messages:
        content = msg.get('content', '')
        for pattern in experiment_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    experiments.append(match.strip())

    return list(set(experiments))[:5]  # Dedupe and limit


def extract_kill_criteria_from_debate(messages: List[Dict[str, Any]]) -> List[str]:
    """
    Extract potential kill criteria from debate transcript.

    Looks for patterns like:
    - "If X doesn't happen..."
    - "Should fail if..."
    - "Red flag would be..."
    """
    criteria = []
    kill_patterns = [
        r'(?:if|should|would) fail (?:if|when)[:\s]+([^.]+)',
        r'red flag[:\s]+([^.]+)',
        r'kill (?:the |this )?(?:initiative|project|experiment) if[:\s]+([^.]+)',
        r'stop if[:\s]+([^.]+)',
    ]

    for msg in messages:
        content = msg.get('content', '')
        for pattern in kill_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    criteria.append(match.strip())

    return list(set(criteria))[:3]  # Dedupe and limit

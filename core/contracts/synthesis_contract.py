"""
Synthesis Contract - Session 872
=================================

Structured output for debate/conversation synthesis.

Based on ChatGPT feedback:
- "The Synthesis Is Weak - It threw away 80% of the intelligence"
- "Right now your system thinks well, summarizes poorly"
- No more "Productive discussion... Further analysis recommended"

This contract forces:
1. Binary categorization (validated vs rejected)
2. Explicit risk acknowledgment
3. Concrete experiments (not vague next steps)
4. Owner assignments (who does what)

Usage:
    from core.contracts.synthesis_contract import SynthesisContract

    synthesis = SynthesisContract.create(
        topic="salary negotiation MVP",
        validated=["Strong market signal - 40% demand", "Low technical risk"],
        rejected=["Full salary database - too complex for MVP"],
        open_risks=["Sample size only 77, not 500"],
        experiments=["A/B test with 50 beta users over 7 days"],
        owner_assignments={"ResearchAgent": "Gather 50 beta emails"}
    )

    # Validate
    synthesis.validate()

    # Convert to dict
    result = synthesis.to_dict()
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class SynthesisQuality(Enum):
    """Quality rating for synthesis."""
    POOR = "poor"           # Vague, no concrete conclusions
    ACCEPTABLE = "acceptable"  # Has structure but weak conclusions
    GOOD = "good"           # Clear conclusions with some gaps
    EXCELLENT = "excellent"  # Decisive, actionable, complete


class ConsensusLevel(Enum):
    """Level of agreement in the debate."""
    UNANIMOUS = "unanimous"     # All agents agreed
    MAJORITY = "majority"       # 3/4+ agreed
    SPLIT = "split"             # 50/50 or close
    MINORITY = "minority"       # Only 1-2 agents supported the conclusion
    NO_CONSENSUS = "no_consensus"  # No clear direction


@dataclass
class OwnerAssignment:
    """Task assignment from synthesis."""
    agent: str
    task: str
    deadline: Optional[str] = None
    priority: int = 1  # 1=highest

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent': self.agent,
            'task': self.task,
            'deadline': self.deadline,
            'priority': self.priority,
        }


@dataclass
class SynthesisContract:
    """
    Structured contract for debate/conversation synthesis.

    Replaces vague "DecisionSummary" with actionable intelligence.
    """

    # === REQUIRED: TOPIC ===
    topic: str  # What was debated

    # === REQUIRED: BINARY CATEGORIZATION ===

    # What was PROVEN in the debate?
    # Must be specific claims with evidence.
    # BAD: "Good discussion about the topic"
    # GOOD: "Market demand validated - 40% of users asked for salary info"
    validated: List[str]

    # What was DISPROVEN or REJECTED?
    # Must explain WHY it was rejected.
    # BAD: "Some alternatives considered"
    # GOOD: "Full salary database rejected - 6+ month timeline, exceeds MVP scope"
    rejected: List[str]

    # === REQUIRED: RISK ACKNOWLEDGMENT ===

    # What risks remain unresolved?
    # Must be honest about limitations.
    open_risks: List[str]

    # === REQUIRED: EXPERIMENTS ===

    # What experiments will test the conclusions?
    # Must be specific and measurable.
    # BAD: "We should validate this"
    # GOOD: "A/B test: salary info vs no salary info, measure CTR over 7 days"
    experiments: List[str]

    # === REQUIRED: OWNERSHIP ===

    # Who does what next?
    # Maps agent names to specific tasks.
    owner_assignments: Dict[str, str]  # agent -> task

    # === METADATA ===

    # How strong was the consensus?
    consensus_level: ConsensusLevel = ConsensusLevel.MAJORITY

    # Overall quality rating
    quality: SynthesisQuality = SynthesisQuality.ACCEPTABLE

    # Participants in the debate
    participants: List[str] = field(default_factory=list)

    # Key quotes from debate (evidence)
    key_quotes: List[Dict[str, str]] = field(default_factory=list)  # [{agent, quote}]

    # Dissenting opinions (important for context)
    dissents: List[Dict[str, str]] = field(default_factory=list)  # [{agent, position}]

    # Source conversation ID
    conversation_id: Optional[str] = None

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # === ANTI-PATTERNS TO BLOCK ===

    VAGUE_PHRASES = [
        "productive discussion",
        "good conversation",
        "interesting points",
        "further analysis",
        "more research",
        "needs investigation",
        "should explore",
        "consider looking",
        "might want to",
        "potentially could",
        "various options",
        "different approaches",
    ]

    def validate(self) -> bool:
        """
        Validate the synthesis for completeness and specificity.

        Raises:
            ValueError: If synthesis is invalid

        Returns:
            True if valid
        """
        errors = []

        # 1. Topic required
        if not self.topic or len(self.topic.strip()) < 5:
            errors.append("Topic required and must be specific")

        # 2. Must have at least 1 validated finding
        if not self.validated:
            errors.append("At least 1 validated finding required - what was proven?")
        else:
            for finding in self.validated:
                self._check_for_vagueness(finding, "validated", errors)

        # 3. Rejected can be empty but shouldn't contain vague phrases
        for finding in self.rejected:
            self._check_for_vagueness(finding, "rejected", errors)

        # 4. Must acknowledge risks
        if not self.open_risks:
            errors.append("Must acknowledge at least 1 open risk - be honest about limitations")

        # 5. Must have experiments
        if not self.experiments:
            errors.append("At least 1 experiment required - how do we test conclusions?")
        else:
            for exp in self.experiments:
                # Experiments should be measurable
                if not re.search(r'\d|%|day|week|user|test|measure|track', exp.lower()):
                    errors.append(f"Experiment not measurable: '{exp}' - add metrics/timeframes")

        # 6. Must have owner assignments
        if not self.owner_assignments:
            errors.append("At least 1 owner assignment required - who does what next?")

        # 7. Check owner assignments aren't vague
        for agent, task in self.owner_assignments.items():
            if len(task.strip()) < 10:
                errors.append(f"Task for {agent} too vague: '{task}'")
            self._check_for_vagueness(task, f"task for {agent}", errors)

        if errors:
            error_msg = "; ".join(errors)
            logger.warning(f"Synthesis Contract validation failed: {error_msg}")
            raise ValueError(f"Invalid Synthesis Contract: {error_msg}")

        return True

    def _check_for_vagueness(self, text: str, field_name: str, errors: List[str]) -> None:
        """Check text for vague phrases."""
        text_lower = text.lower()
        for phrase in self.VAGUE_PHRASES:
            if phrase in text_lower:
                errors.append(f"Vague phrase in {field_name}: '{phrase}' - be specific")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'contract_type': 'synthesis',
            'contract_version': '1.0',

            # Core content
            'topic': self.topic,
            'validated': self.validated,
            'rejected': self.rejected,
            'open_risks': self.open_risks,
            'experiments': self.experiments,
            'owner_assignments': self.owner_assignments,

            # Metadata
            'consensus_level': self.consensus_level.value,
            'quality': self.quality.value,
            'participants': self.participants,
            'key_quotes': self.key_quotes,
            'dissents': self.dissents,
            'conversation_id': self.conversation_id,
            'created_at': self.created_at,

            # Computed fields
            'validated_count': len(self.validated),
            'rejected_count': len(self.rejected),
            'risk_count': len(self.open_risks),
            'experiment_count': len(self.experiments),
            'assignment_count': len(self.owner_assignments),
        }

    def to_markdown(self) -> str:
        """Generate markdown representation."""
        md = f"# Synthesis: {self.topic}\n\n"
        md += f"**Quality:** {self.quality.value.title()}\n"
        md += f"**Consensus:** {self.consensus_level.value.replace('_', ' ').title()}\n\n"

        md += "## Validated ✓\n\n"
        if self.validated:
            for item in self.validated:
                md += f"- {item}\n"
        else:
            md += "_None explicitly validated_\n"
        md += "\n"

        md += "## Rejected ✗\n\n"
        if self.rejected:
            for item in self.rejected:
                md += f"- {item}\n"
        else:
            md += "_No alternatives explicitly rejected_\n"
        md += "\n"

        md += "## Open Risks ⚠️\n\n"
        for risk in self.open_risks:
            md += f"- {risk}\n"
        md += "\n"

        md += "## Experiments 🧪\n\n"
        for exp in self.experiments:
            md += f"- [ ] {exp}\n"
        md += "\n"

        md += "## Owner Assignments 👤\n\n"
        md += "| Agent | Task |\n|-------|------|\n"
        for agent, task in self.owner_assignments.items():
            md += f"| {agent} | {task} |\n"
        md += "\n"

        if self.dissents:
            md += "## Dissenting Views 🗣️\n\n"
            for dissent in self.dissents:
                md += f"- **{dissent.get('agent', 'Unknown')}**: {dissent.get('position', '')}\n"
            md += "\n"

        if self.key_quotes:
            md += "## Key Quotes 💬\n\n"
            for quote in self.key_quotes[:3]:  # Limit to top 3
                md += f"> \"{quote.get('quote', '')}\" — {quote.get('agent', 'Unknown')}\n\n"

        md += f"---\n\n_Created: {self.created_at}_\n"

        return md

    @classmethod
    def create(
        cls,
        topic: str,
        validated: List[str],
        rejected: List[str],
        open_risks: List[str],
        experiments: List[str],
        owner_assignments: Dict[str, str],
        **kwargs
    ) -> 'SynthesisContract':
        """
        Factory method to create a validated synthesis.

        Args:
            topic: What was debated
            validated: What was proven
            rejected: What was disproven
            open_risks: Unresolved risks
            experiments: How to test conclusions
            owner_assignments: Who does what
            **kwargs: Additional fields

        Returns:
            Validated SynthesisContract
        """
        synthesis = cls(
            topic=topic,
            validated=validated,
            rejected=rejected,
            open_risks=open_risks,
            experiments=experiments,
            owner_assignments=owner_assignments,
            **kwargs
        )

        # Validate on creation
        synthesis.validate()

        return synthesis

    @classmethod
    def from_debate_messages(
        cls,
        messages: List[Dict[str, Any]],
        topic: str
    ) -> 'SynthesisContract':
        """
        Create synthesis from raw debate messages.

        This is a stub - use SynthesisAgent to do this via LLM.
        """
        raise NotImplementedError(
            "Use SynthesisAgent or conversation_orchestrator to create synthesis from debates"
        )

    def get_quality_score(self) -> int:
        """Calculate a 0-100 quality score."""
        score = 0

        # Validated findings (up to 25 points)
        score += min(len(self.validated) * 8, 25)

        # Rejected alternatives (up to 15 points)
        score += min(len(self.rejected) * 5, 15)

        # Risk acknowledgment (up to 15 points)
        score += min(len(self.open_risks) * 5, 15)

        # Experiments (up to 20 points)
        score += min(len(self.experiments) * 10, 20)

        # Owner assignments (up to 15 points)
        score += min(len(self.owner_assignments) * 5, 15)

        # Consensus bonus (up to 10 points)
        consensus_scores = {
            ConsensusLevel.UNANIMOUS: 10,
            ConsensusLevel.MAJORITY: 7,
            ConsensusLevel.SPLIT: 3,
            ConsensusLevel.MINORITY: 1,
            ConsensusLevel.NO_CONSENSUS: 0,
        }
        score += consensus_scores.get(self.consensus_level, 0)

        return min(100, score)

    def to_decision_summary_format(self) -> str:
        """
        Convert to legacy DecisionSummary format for backwards compatibility.

        This allows gradual migration from the old format.
        """
        lines = ["=== DecisionSummary ==="]
        lines.append("Insights:")
        for i, finding in enumerate(self.validated[:3], 1):
            lines.append(f"{i}. {finding}")

        lines.append("")
        lines.append("Proposed Feature:")
        if self.experiments:
            lines.append(f"- Name: {self.topic} Experiment")
            lines.append(f"- Inputs: User data, current metrics")
            lines.append(f"- Outputs: Validation results")
            lines.append(f"- Where it plugs into the system: A/B testing framework")

        lines.append("")
        lines.append("Next Steps:")
        for agent, task in list(self.owner_assignments.items())[:3]:
            lines.append(f"- {agent}: {task}")

        return "\n".join(lines)


def extract_synthesis_from_decision_summary(
    decision_summary: Dict[str, Any],
    topic: str,
    participants: Optional[List[str]] = None
) -> SynthesisContract:
    """
    Convert old DecisionSummary format to new SynthesisContract.

    This enables gradual migration from the old format.

    Args:
        decision_summary: The old-format decision summary dict
        topic: What was debated
        participants: Agent names that participated

    Returns:
        SynthesisContract (may not validate if old format was weak)
    """
    # Extract validated from insights
    validated = []
    for insight in decision_summary.get('insights', []):
        if isinstance(insight, str) and len(insight.strip()) > 10:
            validated.append(insight)

    # Old format doesn't have explicit rejections
    rejected = []

    # Extract risks from high_value_signals
    open_risks = []
    high_value = decision_summary.get('high_value_signals', {})
    for risk in high_value.get('risks', []):
        open_risks.append(risk)
    if not open_risks:
        open_risks.append("Risk assessment not captured in original synthesis")

    # Extract experiments
    experiments = []
    for exp in high_value.get('experiments', []):
        experiments.append(exp)
    if not experiments:
        # Fall back to next_steps
        for step in decision_summary.get('next_steps', [])[:2]:
            experiments.append(f"Experiment: {step}")

    # Extract owner assignments from next_steps
    owner_assignments = {}
    for step in decision_summary.get('next_steps', []):
        # Try to extract agent name from step
        if ':' in step:
            parts = step.split(':', 1)
            owner_assignments[parts[0].strip()] = parts[1].strip()
        elif participants:
            # Assign to first participant
            owner_assignments[participants[0]] = step

    if not owner_assignments:
        owner_assignments["Unassigned"] = "Review synthesis and assign tasks"

    return SynthesisContract(
        topic=topic,
        validated=validated,
        rejected=rejected,
        open_risks=open_risks,
        experiments=experiments,
        owner_assignments=owner_assignments,
        participants=participants or [],
        conversation_id=decision_summary.get('conversation_id'),
        quality=SynthesisQuality.ACCEPTABLE,
    )

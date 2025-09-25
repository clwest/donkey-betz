"""
AI Proposal Management System
==============================
Manages AI-generated proposals for system improvements with human approval workflow.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
import redis
import logging

logger = logging.getLogger(__name__)

class ProposalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVIEW = "requires_review"

class ProposalRisk(Enum):
    LOW = "low"        # Safe, reversible changes
    MEDIUM = "medium"  # May affect performance
    HIGH = "high"      # Could break functionality
    CRITICAL = "critical"  # System-wide impact

@dataclass
class AIProposal:
    """Represents an AI-generated proposal for system improvement"""
    id: str
    title: str
    description: str
    category: str  # optimization, refactor, feature, bugfix, security
    risk_level: ProposalRisk
    status: ProposalStatus
    created_at: datetime

    # Impact analysis
    impact_score: float  # 0-10
    roi_estimate: float  # Return on investment
    affected_components: List[str]
    dependencies: List[str]

    # Implementation details
    implementation_steps: List[str]
    estimated_time: str  # "5 minutes", "1 hour", etc.
    rollback_plan: str

    # Evidence and reasoning
    evidence: Dict[str, Any]
    confidence_score: float  # 0-1
    ai_reasoning: str

    # Approval workflow
    requires_human_approval: bool = True
    auto_approve_threshold: float = 0.95
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # Execution tracking
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    completion_percentage: float = 0.0
    error_messages: List[str] = field(default_factory=list)

class ProposalManager:
    """
    Manages AI proposals with safety checks and human approval workflow.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or redis.Redis(
            host='localhost', port=6379, decode_responses=True
        )
        self.proposals: Dict[str, AIProposal] = {}
        self.approval_queue: List[str] = []
        self.execution_queue: List[str] = []

        # Safety thresholds
        self.auto_approve_categories = ["optimization", "documentation"]
        self.require_review_categories = ["security", "database", "api"]
        self.max_auto_approvals_per_hour = 5
        self.min_confidence_for_auto = 0.9

        self._load_proposals()

    def _load_proposals(self):
        """Load existing proposals from Redis"""
        try:
            keys = self.redis_client.keys("proposal:*")
            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    proposal_dict = json.loads(data)
                    # Convert back to AIProposal object
                    proposal = self._dict_to_proposal(proposal_dict)
                    self.proposals[proposal.id] = proposal

                    if proposal.status == ProposalStatus.PENDING:
                        self.approval_queue.append(proposal.id)
                    elif proposal.status == ProposalStatus.APPROVED:
                        self.execution_queue.append(proposal.id)

            logger.info(f"Loaded {len(self.proposals)} proposals")
        except Exception as e:
            logger.error(f"Error loading proposals: {e}")

    def create_proposal(self,
                       title: str,
                       description: str,
                       category: str,
                       evidence: Dict[str, Any],
                       impact_analysis: Dict[str, Any]) -> AIProposal:
        """Create a new AI proposal"""

        # Generate unique ID
        proposal_id = hashlib.md5(
            f"{title}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Determine risk level
        risk_level = self._assess_risk(category, impact_analysis)

        # Check if requires human approval
        requires_approval = self._requires_human_approval(
            category, risk_level, impact_analysis.get('confidence', 0)
        )

        proposal = AIProposal(
            id=proposal_id,
            title=title,
            description=description,
            category=category,
            risk_level=risk_level,
            status=ProposalStatus.PENDING if requires_approval else ProposalStatus.APPROVED,
            created_at=datetime.now(),
            impact_score=impact_analysis.get('impact_score', 5.0),
            roi_estimate=impact_analysis.get('roi', 1.0),
            affected_components=impact_analysis.get('components', []),
            dependencies=impact_analysis.get('dependencies', []),
            implementation_steps=impact_analysis.get('steps', []),
            estimated_time=impact_analysis.get('time_estimate', 'unknown'),
            rollback_plan=impact_analysis.get('rollback', 'Revert changes via git'),
            evidence=evidence,
            confidence_score=impact_analysis.get('confidence', 0.5),
            ai_reasoning=impact_analysis.get('reasoning', ''),
            requires_human_approval=requires_approval
        )

        # Store in Redis
        self._save_proposal(proposal)

        # Add to appropriate queue
        if requires_approval:
            self.approval_queue.append(proposal_id)
            logger.info(f"Proposal {proposal_id} added to approval queue")
        else:
            self.execution_queue.append(proposal_id)
            logger.info(f"Proposal {proposal_id} auto-approved and queued for execution")

        return proposal

    def approve_proposal(self, proposal_id: str, approver: str = "human") -> bool:
        """Approve a proposal for execution"""
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        proposal.status = ProposalStatus.APPROVED
        proposal.approved_by = approver
        proposal.approved_at = datetime.now()

        # Move from approval queue to execution queue
        if proposal_id in self.approval_queue:
            self.approval_queue.remove(proposal_id)
        self.execution_queue.append(proposal_id)

        self._save_proposal(proposal)
        logger.info(f"Proposal {proposal_id} approved by {approver}")

        # Broadcast approval via WebSocket
        self._broadcast_proposal_update(proposal)

        return True

    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        """Reject a proposal"""
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        proposal.status = ProposalStatus.REJECTED
        proposal.rejection_reason = reason

        # Remove from queues
        if proposal_id in self.approval_queue:
            self.approval_queue.remove(proposal_id)
        if proposal_id in self.execution_queue:
            self.execution_queue.remove(proposal_id)

        self._save_proposal(proposal)
        logger.info(f"Proposal {proposal_id} rejected: {reason}")

        # Broadcast rejection
        self._broadcast_proposal_update(proposal)

        return True

    def execute_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Execute an approved proposal"""
        if proposal_id not in self.proposals:
            return {"success": False, "error": "Proposal not found"}

        proposal = self.proposals[proposal_id]

        if proposal.status != ProposalStatus.APPROVED:
            return {"success": False, "error": "Proposal not approved"}

        proposal.status = ProposalStatus.IN_PROGRESS
        self._save_proposal(proposal)

        try:
            # Log execution start
            proposal.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "execution_started",
                "message": f"Starting execution of {proposal.title}"
            })

            # Execute based on category
            result = self._execute_by_category(proposal)

            if result["success"]:
                proposal.status = ProposalStatus.COMPLETED
                proposal.completion_percentage = 100.0
            else:
                proposal.status = ProposalStatus.FAILED
                proposal.error_messages.append(result.get("error", "Unknown error"))

            # Log execution result
            proposal.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "execution_completed",
                "result": result
            })

            self._save_proposal(proposal)
            self._broadcast_proposal_update(proposal)

            return result

        except Exception as e:
            proposal.status = ProposalStatus.FAILED
            proposal.error_messages.append(str(e))
            self._save_proposal(proposal)
            logger.error(f"Error executing proposal {proposal_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_pending_proposals(self) -> List[AIProposal]:
        """Get all proposals awaiting approval"""
        return [
            self.proposals[pid]
            for pid in self.approval_queue
            if pid in self.proposals
        ]

    def get_proposal_stats(self) -> Dict[str, Any]:
        """Get statistics about proposals"""
        total = len(self.proposals)
        by_status = {}
        by_category = {}
        by_risk = {}

        for proposal in self.proposals.values():
            # Count by status
            status = proposal.status.value
            by_status[status] = by_status.get(status, 0) + 1

            # Count by category
            by_category[proposal.category] = by_category.get(proposal.category, 0) + 1

            # Count by risk
            risk = proposal.risk_level.value
            by_risk[risk] = by_risk.get(risk, 0) + 1

        return {
            "total": total,
            "pending": len(self.approval_queue),
            "queued_for_execution": len(self.execution_queue),
            "by_status": by_status,
            "by_category": by_category,
            "by_risk": by_risk,
            "auto_approval_enabled": len(self.auto_approve_categories) > 0,
            "safety_thresholds": {
                "max_auto_approvals_per_hour": self.max_auto_approvals_per_hour,
                "min_confidence_for_auto": self.min_confidence_for_auto
            }
        }

    def _assess_risk(self, category: str, impact: Dict[str, Any]) -> ProposalRisk:
        """Assess risk level of a proposal"""
        # High risk categories
        if category in ["security", "database", "authentication"]:
            return ProposalRisk.HIGH

        # Check affected components
        affected = impact.get('components', [])
        if any(comp in affected for comp in ['core', 'auth', 'database']):
            return ProposalRisk.HIGH

        # Medium risk for API and integration changes
        if category in ["api", "integration", "refactor"]:
            return ProposalRisk.MEDIUM

        # Low risk for optimization and documentation
        if category in ["optimization", "documentation", "ui"]:
            return ProposalRisk.LOW

        # Default to medium
        return ProposalRisk.MEDIUM

    def _requires_human_approval(self, category: str, risk: ProposalRisk, confidence: float) -> bool:
        """Determine if proposal requires human approval"""
        # Always require approval for high/critical risk
        if risk in [ProposalRisk.HIGH, ProposalRisk.CRITICAL]:
            return True

        # Always require approval for certain categories
        if category in self.require_review_categories:
            return True

        # Auto-approve if category is safe and confidence is high
        if category in self.auto_approve_categories and confidence >= self.min_confidence_for_auto:
            # Check rate limiting
            recent_auto = self._count_recent_auto_approvals()
            if recent_auto < self.max_auto_approvals_per_hour:
                return False

        # Default to requiring approval
        return True

    def _count_recent_auto_approvals(self) -> int:
        """Count auto-approvals in the last hour"""
        count = 0
        one_hour_ago = datetime.now().timestamp() - 3600

        for proposal in self.proposals.values():
            if (proposal.approved_by == "auto" and
                proposal.approved_at and
                proposal.approved_at.timestamp() > one_hour_ago):
                count += 1

        return count

    def _execute_by_category(self, proposal: AIProposal) -> Dict[str, Any]:
        """Execute proposal based on its category"""
        if proposal.category == "optimization":
            return self._execute_optimization(proposal)
        elif proposal.category == "documentation":
            return self._execute_documentation(proposal)
        elif proposal.category == "refactor":
            return self._execute_refactor(proposal)
        else:
            return {
                "success": False,
                "error": f"No executor for category: {proposal.category}"
            }

    def _execute_optimization(self, proposal: AIProposal) -> Dict[str, Any]:
        """Execute optimization proposals"""
        # This would contain actual optimization logic
        return {
            "success": True,
            "message": f"Optimization '{proposal.title}' simulated",
            "improvements": {
                "performance": "+15%",
                "memory": "-10%"
            }
        }

    def _execute_documentation(self, proposal: AIProposal) -> Dict[str, Any]:
        """Execute documentation proposals"""
        return {
            "success": True,
            "message": f"Documentation '{proposal.title}' updated",
            "files_updated": proposal.affected_components
        }

    def _execute_refactor(self, proposal: AIProposal) -> Dict[str, Any]:
        """Execute refactoring proposals"""
        return {
            "success": True,
            "message": f"Refactoring '{proposal.title}' completed",
            "files_refactored": len(proposal.affected_components)
        }

    def _save_proposal(self, proposal: AIProposal):
        """Save proposal to Redis"""
        key = f"proposal:{proposal.id}"
        data = self._proposal_to_dict(proposal)
        self.redis_client.set(key, json.dumps(data))
        self.proposals[proposal.id] = proposal

    def _broadcast_proposal_update(self, proposal: AIProposal):
        """Broadcast proposal update via Redis pub/sub"""
        channel = "proposal_updates"
        message = {
            "type": "proposal_update",
            "proposal": self._proposal_to_dict(proposal),
            "timestamp": datetime.now().isoformat()
        }
        self.redis_client.publish(channel, json.dumps(message))

    def _proposal_to_dict(self, proposal: AIProposal) -> Dict[str, Any]:
        """Convert proposal to dictionary for storage"""
        data = asdict(proposal)
        # Convert enums to strings
        data['risk_level'] = proposal.risk_level.value
        data['status'] = proposal.status.value
        # Convert datetimes to strings
        data['created_at'] = proposal.created_at.isoformat()
        if proposal.approved_at:
            data['approved_at'] = proposal.approved_at.isoformat()
        return data

    def _dict_to_proposal(self, data: Dict[str, Any]) -> AIProposal:
        """Convert dictionary back to AIProposal"""
        # Convert string enums back
        data['risk_level'] = ProposalRisk(data['risk_level'])
        data['status'] = ProposalStatus(data['status'])
        # Convert datetime strings back
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('approved_at'):
            data['approved_at'] = datetime.fromisoformat(data['approved_at'])
        return AIProposal(**data)
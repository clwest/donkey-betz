"""
Human-in-the-Loop Validation Service
Session 470: Market Intelligence Architecture - Phase 3

Manages the validation workflow for ML-scored opportunities
that fall within the human review confidence range.

Updated Session 472: Integrated with Event Bus for centralized event publishing.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Dict, Any, List
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


def _publish_validation_event(event_type: str, data: Dict[str, Any]):
    """Helper to publish validation events to the event bus."""
    try:
        from core.services.event_bus import (
            publish_validation_required_event,
            publish_validation_decided_event
        )

        if event_type == 'validation_required':
            publish_validation_required_event(
                validation_request_id=data.get('validation_request_id'),
                opportunity_id=data.get('opportunity_id'),
                confidence=data.get('confidence', 0),
                priority=data.get('priority', 3),
                source=data.get('source', 'hitl_service')
            )
        elif event_type == 'validation_decided':
            publish_validation_decided_event(
                validation_request_id=data.get('validation_request_id'),
                opportunity_id=data.get('opportunity_id'),
                decision=data.get('decision'),
                decided_by=data.get('decided_by'),
                override_score=data.get('override_score'),
                source=data.get('source', 'hitl_service')
            )

        logger.debug(f"📡 Published {event_type} event to event bus")

    except ImportError:
        logger.debug("Event bus not available, skipping event publish")
    except Exception as e:
        logger.warning(f"Failed to publish {event_type} event: {e}")


def _create_validation_provenance(
    validation_id: str,
    decision: str,
    decided_by: str = None,
    override_score: float = None,
    metadata: Dict = None,
    user=None
):
    """Helper to create provenance for validation decisions."""
    try:
        from core.services.provenance_tracker import create_validation_provenance

        create_validation_provenance(
            validation_id=validation_id,
            scoring_provenance_id=None,  # Would be linked in full integration
            decision=decision,
            decided_by=decided_by,
            override_score=override_score,
            metadata=metadata or {},
            user=user
        )

        logger.debug(f"📜 Created provenance for validation {validation_id}")

    except ImportError:
        logger.debug("Provenance tracker not available, skipping provenance creation")
    except Exception as e:
        logger.warning(f"Failed to create validation provenance: {e}")


@dataclass
class ValidationResult:
    """Result of a validation check."""
    action: str  # 'auto_approved', 'auto_rejected', 'queued_for_review'
    validation_request_id: Optional[str] = None
    reason: Optional[str] = None
    confidence: float = 0.0


@dataclass
class DecisionResult:
    """Result of making a decision."""
    success: bool
    decision: Optional[str] = None
    validation_request_id: Optional[str] = None
    error: Optional[str] = None


class HITLValidationService:
    """
    Human-in-the-Loop Validation Service.

    Session 470: Market Intelligence Architecture - Phase 3

    Handles:
    - Checking if opportunities need human validation
    - Creating validation requests
    - Auto-approval/rejection based on confidence
    - Assignment to reviewers
    - Recording decisions and learning from them
    - Escalation of overdue items
    """

    def __init__(self):
        logger.info("👤 HITL Validation Service initialized")

    def check_and_route(
        self,
        opportunity,
        scoring_result,
        user=None
    ) -> ValidationResult:
        """
        Check a scored opportunity and route it appropriately.

        Args:
            opportunity: The Opportunity model instance
            scoring_result: MLScoringResult from the scoring engine
            user: Optional user context for configuration

        Returns:
            ValidationResult indicating what action was taken
        """
        from core.models_unified_system import ValidationConfig

        config = ValidationConfig.get_config(user)
        confidence = scoring_result.confidence

        logger.info(
            f"👤 [HITL] Checking opportunity {opportunity.id} "
            f"(confidence: {confidence:.1f}%)"
        )

        # High confidence: Auto-approve
        if confidence >= config.auto_approve_threshold:
            self._record_auto_decision(opportunity, scoring_result, 'auto_approved', config)
            logger.info(f"👤 [HITL] Auto-approved: confidence {confidence:.1f}% >= {config.auto_approve_threshold}%")
            return ValidationResult(
                action='auto_approved',
                reason=f'Confidence {confidence:.1f}% exceeds auto-approve threshold',
                confidence=confidence
            )

        # Low confidence: Auto-reject
        if confidence < config.auto_reject_threshold:
            self._record_auto_decision(opportunity, scoring_result, 'auto_rejected', config)
            logger.info(f"👤 [HITL] Auto-rejected: confidence {confidence:.1f}% < {config.auto_reject_threshold}%")
            return ValidationResult(
                action='auto_rejected',
                reason=f'Confidence {confidence:.1f}% below auto-reject threshold',
                confidence=confidence
            )

        # Middle range: Queue for human review
        validation_request = self._create_validation_request(
            opportunity, scoring_result, config
        )

        # Try to auto-assign
        if config.enable_auto_assignment:
            self._try_auto_assign(validation_request, config)

        logger.info(
            f"👤 [HITL] Queued for review: confidence {confidence:.1f}% "
            f"(request: {validation_request.id})"
        )

        return ValidationResult(
            action='queued_for_review',
            validation_request_id=str(validation_request.id),
            reason=f'Confidence {confidence:.1f}% requires human validation',
            confidence=confidence
        )

    def _create_validation_request(
        self,
        opportunity,
        scoring_result,
        config
    ):
        """Create a validation request for human review."""
        from core.models_unified_system import ValidationRequest, ScoringExplanation

        # Find the scoring explanation if it exists.
        # Session 1103c: was 'except Exception: pass' which silently
        # broke HITL traceability — a DB error here meant the
        # validation proceeded without ScoringExplanation linkage and
        # there was no audit trail explaining how the opportunity was
        # scored. Now logs the failure so missing explanations have a
        # named cause.
        explanation = None
        try:
            explanation = ScoringExplanation.objects.filter(
                opportunity=opportunity
            ).first()
        except Exception as e:
            logger.warning(
                "hitl_validation: ScoringExplanation lookup failed "
                "for opportunity=%s (%s: %s) — validation request will "
                "be created without scoring linkage",
                getattr(opportunity, 'id', '<unknown>'),
                type(e).__name__, e,
            )

        # Calculate priority based on opportunity value
        priority = self._calculate_priority(opportunity, scoring_result)

        # Set deadlines
        now = timezone.now()
        deadline = now + timedelta(hours=config.default_deadline_hours)
        escalate_after = now + timedelta(hours=config.escalation_delay_hours)

        validation_request = ValidationRequest.objects.create(
            opportunity=opportunity,
            scoring_explanation=explanation,
            ml_score=scoring_result.ml_score,
            rule_score=scoring_result.rule_score,
            hybrid_score=scoring_result.hybrid_score,
            confidence=scoring_result.confidence,
            priority=priority,
            deadline=deadline,
            escalate_after=escalate_after,
            request_reason='confidence_threshold',
            request_source='auto'
        )

        # Publish event to event bus
        _publish_validation_event('validation_required', {
            'validation_request_id': str(validation_request.id),
            'opportunity_id': str(opportunity.id),
            'confidence': scoring_result.confidence,
            'priority': priority
        })

        return validation_request

    def _calculate_priority(self, opportunity, scoring_result) -> int:
        """Calculate review priority based on opportunity characteristics."""
        # Start with normal priority
        priority = 3

        # Higher value opportunities get higher priority
        if hasattr(opportunity, 'profit_potential'):
            if opportunity.profit_potential >= 90:
                priority = 1  # Critical
            elif opportunity.profit_potential >= 70:
                priority = 2  # High

        # Time-sensitive opportunities get higher priority
        if hasattr(opportunity, 'time_sensitivity'):
            if opportunity.time_sensitivity >= 80:
                priority = min(priority, 2)  # At least High

        # Lower confidence needs faster review
        if scoring_result.confidence < 60:
            priority = min(priority, 2)  # At least High

        return priority

    def _try_auto_assign(self, validation_request, config):
        """Try to automatically assign validation to a reviewer."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Find users with reviewer permissions and available capacity
        # In a real system, you'd check for specific permissions
        # For now, we'll find staff users with the fewest assignments

        eligible_users = User.objects.filter(
            is_staff=True,
            is_active=True
        ).annotate(
            pending_count=Count(
                'assigned_validations',
                filter=Q(assigned_validations__status__in=['pending', 'assigned'])
            )
        ).filter(
            pending_count__lt=config.max_assignments_per_user
        ).order_by('pending_count')

        if eligible_users.exists():
            assigned_user = eligible_users.first()
            validation_request.assign_to(assigned_user)
            logger.info(
                f"👤 [HITL] Auto-assigned {validation_request.id} to {assigned_user.username}"
            )

    def _record_auto_decision(
        self,
        opportunity,
        scoring_result,
        decision_type: str,
        config
    ):
        """Record an automatic approval/rejection."""
        from core.models_unified_system import ValidationRequest, ValidationDecision

        # Create a validation request record for tracking
        request = ValidationRequest.objects.create(
            opportunity=opportunity,
            ml_score=scoring_result.ml_score,
            rule_score=scoring_result.rule_score,
            hybrid_score=scoring_result.hybrid_score,
            confidence=scoring_result.confidence,
            status=decision_type,
            request_reason='confidence_threshold',
            request_source='auto',
            completed_at=timezone.now()
        )

        # Create decision record
        decision = 'approve' if decision_type == 'auto_approved' else 'reject'
        ValidationDecision.objects.create(
            validation_request=request,
            decision=decision,
            reasoning=f'Auto-{decision}ed based on confidence threshold',
            reasoning_tags=['auto_decision', decision_type],
            decision_time_seconds=0
        )

        # Create provenance record for auto-decision
        _create_validation_provenance(
            validation_id=str(request.id),
            decision=decision_type,
            decided_by='system',
            metadata={
                'opportunity_id': str(opportunity.id),
                'confidence': scoring_result.confidence,
                'auto_decision': True,
                'decision_type': decision_type,
            }
        )

        # Update config metrics
        config.record_decision(decision_type, 0)

    def make_decision(
        self,
        validation_request_id: str,
        decision: str,
        user,
        override_score: float = None,
        reasoning: str = '',
        reasoning_tags: List[str] = None
    ) -> DecisionResult:
        """
        Record a human decision on a validation request.

        Args:
            validation_request_id: UUID of the validation request
            decision: 'approve', 'approve_with_changes', 'reject', 'escalate', 'defer'
            user: User making the decision
            override_score: New score if overriding ML (for approve_with_changes)
            reasoning: Why this decision was made
            reasoning_tags: Structured tags for the reasoning

        Returns:
            DecisionResult
        """
        from core.models_unified_system import (
            ValidationRequest, ValidationDecision, ValidationConfig
        )

        try:
            request = ValidationRequest.objects.get(id=validation_request_id)
        except ValidationRequest.DoesNotExist:
            return DecisionResult(
                success=False,
                error=f'Validation request {validation_request_id} not found'
            )

        # Check if already decided
        if hasattr(request, 'decision'):
            return DecisionResult(
                success=False,
                error='This validation request already has a decision'
            )

        # Check if user is authorized
        if request.assigned_to and request.assigned_to != user and not user.is_superuser:
            return DecisionResult(
                success=False,
                error='This validation is assigned to another reviewer'
            )

        # Get config for validation
        config = ValidationConfig.get_config(user)

        # Validate reasoning requirements
        if decision == 'approve_with_changes' and config.require_reasoning_for_overrides:
            if not reasoning:
                return DecisionResult(
                    success=False,
                    error='Reasoning is required when overriding ML score'
                )

        # Calculate decision time
        decision_time = None
        if request.assigned_at:
            delta = timezone.now() - request.assigned_at
            decision_time = int(delta.total_seconds())

        # Create decision record
        validation_decision = ValidationDecision.objects.create(
            validation_request=request,
            decision=decision,
            decided_by=user,
            override_score=override_score if decision == 'approve_with_changes' else None,
            reasoning=reasoning,
            reasoning_tags=reasoning_tags or [],
            decision_time_seconds=decision_time
        )

        # Update request status
        if decision == 'approve':
            request.status = 'approved'
        elif decision == 'approve_with_changes':
            request.status = 'approved'
        elif decision == 'reject':
            request.status = 'rejected'
        elif decision == 'escalate':
            request.status = 'escalated'
            # Re-queue with higher priority
            request.priority = max(1, request.priority - 1)
            request.assigned_to = None
            request.assigned_at = None

        request.completed_at = timezone.now()
        request.save()

        # Update metrics
        config.record_decision(decision, decision_time)

        logger.info(
            f"👤 [HITL] Decision recorded: {decision} for {request.opportunity.title[:30]}... "
            f"by {user.username}"
        )

        # Publish event to event bus
        _publish_validation_event('validation_decided', {
            'validation_request_id': str(request.id),
            'opportunity_id': str(request.opportunity.id),
            'decision': decision,
            'decided_by': user.username,
            'override_score': override_score
        })

        # Create provenance record for validation decision
        _create_validation_provenance(
            validation_id=str(request.id),
            decision=decision,
            decided_by=user.username,
            override_score=override_score,
            metadata={
                'opportunity_id': str(request.opportunity.id),
                'reasoning': reasoning,
                'reasoning_tags': reasoning_tags or [],
                'decision_time_seconds': decision_time,
            },
            user=user
        )

        return DecisionResult(
            success=True,
            decision=decision,
            validation_request_id=str(request.id)
        )

    def get_pending_queue(
        self,
        user=None,
        status: str = 'pending',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get pending validation requests.

        Args:
            user: Optional user to filter assigned validations
            status: Filter by status ('pending', 'assigned', 'all')
            limit: Maximum items to return

        Returns:
            List of validation request dicts
        """
        from core.models_unified_system import ValidationRequest

        queryset = ValidationRequest.objects.select_related(
            'opportunity', 'scoring_explanation', 'assigned_to'
        )

        if status == 'pending':
            queryset = queryset.filter(status='pending')
        elif status == 'assigned':
            queryset = queryset.filter(status='assigned')
        else:  # 'all' - include both
            queryset = queryset.filter(status__in=['pending', 'assigned'])

        if user:
            queryset = queryset.filter(
                Q(assigned_to=user) | Q(assigned_to__isnull=True)
            )

        queryset = queryset.order_by('priority', 'created_at')[:limit]

        results = []
        for req in queryset:
            results.append({
                'id': str(req.id),
                'opportunity_id': str(req.opportunity.id),
                'opportunity_title': req.opportunity.title,
                'ml_score': req.ml_score,
                'rule_score': req.rule_score,
                'hybrid_score': req.hybrid_score,
                'confidence': req.confidence,
                'priority': req.priority,
                'status': req.status,
                'assigned_to': req.assigned_to.username if req.assigned_to else None,
                'deadline': req.deadline.isoformat() if req.deadline else None,
                'is_overdue': req.is_overdue,
                'created_at': req.created_at.isoformat(),
            })

        return results

    def process_escalations(self) -> Dict[str, int]:
        """
        Process validation requests that need escalation.

        Returns:
            Dict with counts of escalated items
        """
        from core.models_unified_system import ValidationRequest

        now = timezone.now()

        # Find items past escalation time
        to_escalate = ValidationRequest.objects.filter(
            status__in=['pending', 'assigned'],
            escalate_after__lt=now
        )

        escalated_count = 0
        for request in to_escalate:
            # Increase priority
            if request.priority > 1:
                request.priority -= 1

            # Mark as needing attention
            request.request_source = 'escalation'

            # Extend deadline
            request.deadline = now + timedelta(hours=24)
            request.escalate_after = now + timedelta(hours=4)

            # Unassign so it can be reassigned
            request.assigned_to = None
            request.assigned_at = None

            request.save()
            escalated_count += 1

        if escalated_count > 0:
            logger.warning(f"👤 [HITL] Escalated {escalated_count} overdue validation requests")

        return {'escalated': escalated_count}

    def expire_overdue(self) -> Dict[str, int]:
        """
        Expire validation requests that are past deadline.

        Returns:
            Dict with counts of expired items
        """
        from core.models_unified_system import ValidationRequest

        now = timezone.now()

        expired = ValidationRequest.objects.filter(
            status__in=['pending', 'assigned'],
            deadline__lt=now
        )

        count = expired.count()
        expired.update(status='expired', completed_at=now)

        if count > 0:
            logger.info(f"👤 [HITL] Expired {count} overdue validation requests")

        return {'expired': count}

    def get_stats(self, user=None) -> Dict[str, Any]:
        """Get validation statistics."""
        from core.models_unified_system import (
            ValidationRequest, ValidationDecision, ValidationConfig
        )

        config = ValidationConfig.get_config(user)

        # Count by status
        status_counts = dict(
            ValidationRequest.objects.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        # Recent decisions
        recent_decisions = dict(
            ValidationDecision.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values('decision')
            .annotate(count=Count('id'))
            .values_list('decision', 'count')
        )

        # ML agreement rate
        recent_with_decisions = ValidationDecision.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        )
        agreement_rate = recent_with_decisions.filter(
            agreement_with_ml=True
        ).count() / max(recent_with_decisions.count(), 1) * 100

        return {
            'thresholds': {
                'auto_approve': config.auto_approve_threshold,
                'auto_reject': config.auto_reject_threshold
            },
            'queue_status': status_counts,
            'recent_decisions': recent_decisions,
            'ml_agreement_rate': round(agreement_rate, 1),
            'metrics': {
                'total_validations': config.total_validations,
                'total_approved': config.total_approved,
                'total_rejected': config.total_rejected,
                'total_overrides': config.total_overrides,
                'avg_decision_time_seconds': round(config.avg_decision_time_seconds, 1)
            }
        }


# Singleton instance
_hitl_service_instance: Optional[HITLValidationService] = None


def get_hitl_validation_service() -> HITLValidationService:
    """Get singleton HITL validation service instance."""
    global _hitl_service_instance
    if _hitl_service_instance is None:
        _hitl_service_instance = HITLValidationService()
    return _hitl_service_instance

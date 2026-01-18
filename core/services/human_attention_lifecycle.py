"""
Human Attention Lifecycle Service
==================================

Session 766: Manages the lifecycle of Human Attention Items.

Solves Dead End #6: 992 items with only 1.3% acted upon.

Features:
1. Auto-expire stale items (based on expires_at)
2. Auto-approve low-risk items (based on user preferences)
3. Auto-escalate aging items (increase urgency for old pending items)
4. Connect approved items to orchestration workflows

Usage:
    from core.services.human_attention_lifecycle import attention_lifecycle

    # Process lifecycle (called by Celery Beat)
    stats = attention_lifecycle.process_lifecycle()

    # Auto-approve an item
    attention_lifecycle.auto_approve_item(item)
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, F

logger = logging.getLogger(__name__)


class HumanAttentionLifecycleService:
    """
    Manages lifecycle events for Human Attention Items.

    Prevents items from accumulating in pending state by:
    - Auto-expiring old items
    - Auto-approving low-risk items
    - Auto-escalating important items
    - Triggering orchestration for approved items
    """

    # Escalation thresholds (hours without action)
    ESCALATION_THRESHOLDS = {
        'low': 72,      # 3 days -> escalate to medium
        'medium': 48,   # 2 days -> escalate to high
        'high': 24,     # 1 day -> escalate to critical
    }

    # Auto-dismiss thresholds by urgency (hours)
    AUTO_DISMISS_HOURS = {
        'low': 168,      # 7 days
        'medium': 120,   # 5 days
        'high': 96,      # 4 days
        'critical': 72,  # 3 days (with escalation first)
    }

    # Low-risk source types that can be auto-approved
    LOW_RISK_SOURCES = [
        'spider_insight',
        'content_review',
        'blog_review',
        'trend_analysis',
        'observation',
    ]

    # Item types that can be auto-approved
    AUTO_APPROVABLE_TYPES = [
        'content',
        'insight',
        'observation',
        'analysis',
        'suggestion',
    ]

    def __init__(self):
        self._orchestration_engine = None

    @property
    def orchestration_engine(self):
        """Lazy-load orchestration engine."""
        if self._orchestration_engine is None:
            from core.services.orchestration_engine import orchestration_engine
            self._orchestration_engine = orchestration_engine
        return self._orchestration_engine

    def process_lifecycle(self) -> Dict[str, Any]:
        """
        Process all lifecycle events for Human Attention Items.

        Called by Celery Beat every 10 minutes.

        Returns:
            Dict with processing statistics
        """
        stats = {
            'expired': 0,
            'auto_dismissed': 0,
            'auto_approved': 0,
            'escalated': 0,
            'orchestrations_triggered': 0,
            'errors': 0,
        }

        logger.info("🧑 [LIFECYCLE] Starting Human Attention lifecycle processing")

        try:
            # 1. Expire items past their expires_at
            stats['expired'] = self._expire_old_items()

            # 2. Auto-dismiss stale items
            stats['auto_dismissed'] = self._auto_dismiss_stale_items()

            # 3. Auto-escalate aging items
            stats['escalated'] = self._auto_escalate_aging_items()

            # 4. Auto-approve low-risk items
            auto_approved, orchestrations = self._auto_approve_low_risk_items()
            stats['auto_approved'] = auto_approved
            stats['orchestrations_triggered'] = orchestrations

        except Exception as e:
            logger.error(f"❌ [LIFECYCLE] Processing failed: {e}")
            stats['errors'] += 1

        total = sum(stats.values()) - stats['errors']
        logger.info(f"🧑 [LIFECYCLE] Complete: {total} items processed - {stats}")

        return stats

    def _expire_old_items(self) -> int:
        """Mark items past their expires_at as expired."""
        from core.models_human_interface import HumanAttentionItem

        now = timezone.now()

        # Find items that have expired
        expired_count = HumanAttentionItem.objects.filter(
            status__in=['pending', 'viewed', 'deferred'],
            expires_at__lt=now,
        ).update(status='expired')

        if expired_count > 0:
            logger.info(f"⏰ [LIFECYCLE] Expired {expired_count} items past their deadline")

        return expired_count

    def _auto_dismiss_stale_items(self) -> int:
        """Auto-dismiss items that have been pending too long."""
        from core.models_human_interface import HumanAttentionItem

        now = timezone.now()
        dismissed_count = 0

        for urgency, hours in self.AUTO_DISMISS_HOURS.items():
            threshold = now - timedelta(hours=hours)

            count = HumanAttentionItem.objects.filter(
                status__in=['pending', 'viewed'],
                urgency=urgency,
                created_at__lt=threshold,
                expires_at__isnull=True,  # Only if no explicit expiration
            ).update(
                status='ignored',
                decision='auto_dismiss',
                decision_feedback=f'Auto-dismissed after {hours} hours of inaction',
                decided_at=now,
            )

            dismissed_count += count

        if dismissed_count > 0:
            logger.info(f"🗑️ [LIFECYCLE] Auto-dismissed {dismissed_count} stale items")

        return dismissed_count

    def _auto_escalate_aging_items(self) -> int:
        """Escalate items that have been pending too long."""
        from core.models_human_interface import HumanAttentionItem

        now = timezone.now()
        escalated_count = 0

        # Escalation mapping
        escalate_to = {
            'low': 'medium',
            'medium': 'high',
            'high': 'critical',
        }

        for urgency, hours in self.ESCALATION_THRESHOLDS.items():
            threshold = now - timedelta(hours=hours)

            items = HumanAttentionItem.objects.filter(
                status__in=['pending', 'viewed'],
                urgency=urgency,
                created_at__lt=threshold,
            )

            for item in items:
                new_urgency = escalate_to.get(urgency)
                if new_urgency:
                    old_urgency = item.urgency
                    item.urgency = new_urgency
                    # Boost priority score
                    item.priority_score = item.priority_score * 1.5
                    item.save(update_fields=['urgency', 'priority_score'])

                    logger.debug(
                        f"📈 [LIFECYCLE] Escalated {item.id}: {old_urgency} -> {new_urgency}"
                    )
                    escalated_count += 1

        if escalated_count > 0:
            logger.info(f"📈 [LIFECYCLE] Escalated {escalated_count} aging items")

        return escalated_count

    def _auto_approve_low_risk_items(self) -> tuple:
        """
        Auto-approve low-risk items based on user preferences.

        Returns:
            Tuple of (approved_count, orchestrations_triggered)
        """
        from core.models_human_interface import (
            HumanAttentionItem,
            HumanPreference,
            HumanSystemState,
        )

        approved_count = 0
        orchestrations_triggered = 0

        # Get system state
        system_state = HumanSystemState.get_state()

        # Skip if system is in review mode
        if system_state.review_mode:
            logger.debug("⏸️ [LIFECYCLE] Review mode enabled, skipping auto-approve")
            return 0, 0

        # Get users who have auto-approve enabled
        auto_approve_users = HumanPreference.objects.filter(
            auto_approve_low_risk=True
        ).values_list('user_id', flat=True)

        if not auto_approve_users:
            return 0, 0

        # Find low-risk items for these users
        now = timezone.now()
        candidates = HumanAttentionItem.objects.filter(
            user_id__in=auto_approve_users,
            status='pending',
            urgency='low',
            # Only items older than 1 hour (give human a chance first)
            created_at__lt=now - timedelta(hours=1),
        ).filter(
            Q(source_type__in=self.LOW_RISK_SOURCES) |
            Q(item_type__in=self.AUTO_APPROVABLE_TYPES)
        )

        for item in candidates[:50]:  # Process max 50 per run
            try:
                # Check ML confidence if available
                user_pref = HumanPreference.objects.get(user=item.user)
                threshold = user_pref.require_review_above_confidence

                # Only auto-approve if ML confidence is high enough
                if item.ml_confidence and item.ml_confidence < threshold:
                    continue

                # Auto-approve the item
                result = self.auto_approve_item(item)
                if result['success']:
                    approved_count += 1

                    # Check if this triggers orchestration
                    if result.get('orchestration_triggered'):
                        orchestrations_triggered += 1

            except Exception as e:
                logger.warning(f"⚠️ [LIFECYCLE] Failed to auto-approve {item.id}: {e}")

        if approved_count > 0:
            logger.info(
                f"✅ [LIFECYCLE] Auto-approved {approved_count} low-risk items, "
                f"triggered {orchestrations_triggered} orchestrations"
            )

        return approved_count, orchestrations_triggered

    def auto_approve_item(
        self,
        item,
        reason: str = 'Auto-approved low-risk item'
    ) -> Dict[str, Any]:
        """
        Auto-approve a single Human Attention Item.

        Args:
            item: HumanAttentionItem instance
            reason: Reason for auto-approval

        Returns:
            Dict with approval result
        """
        from core.models_human_interface import HumanFeedbackRecord

        try:
            with transaction.atomic():
                # Record the decision
                item.decision = 'approve'
                item.decision_feedback = reason
                item.status = 'acted'
                item.decided_at = timezone.now()
                item.save()

                # Create feedback record
                HumanFeedbackRecord.objects.create(
                    attention_item=item,
                    user=item.user,
                    decision='approve',
                    feedback_text=reason,
                    confidence=1.0,  # System is 100% confident in auto-approval
                    ml_prediction=item.ml_prediction,
                    ml_confidence=item.ml_confidence,
                    human_agreed_with_ml=True if item.ml_recommendation == 'approve' else None,
                )

                # Check if this should trigger orchestration
                orchestration_result = self._maybe_trigger_orchestration(item)

                return {
                    'success': True,
                    'item_id': str(item.id),
                    'orchestration_triggered': orchestration_result.get('triggered', False),
                    'orchestration_id': orchestration_result.get('execution_id'),
                }

        except Exception as e:
            logger.error(f"❌ [LIFECYCLE] Failed to auto-approve {item.id}: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def _maybe_trigger_orchestration(self, item) -> Dict[str, Any]:
        """
        Check if an approved item should trigger orchestration.

        Connects approved Human Attention Items to the Orchestration Layer.
        """
        # Types that can trigger orchestration
        ORCHESTRATION_TRIGGERS = {
            'opportunity': self._create_opportunity_workflow,
            'action': self._create_action_workflow,
            'recommendation': self._create_recommendation_workflow,
            'project': self._create_project_workflow,
        }

        item_type = item.item_type

        if item_type not in ORCHESTRATION_TRIGGERS:
            return {'triggered': False}

        try:
            # Get the workflow creator for this type
            workflow_creator = ORCHESTRATION_TRIGGERS[item_type]
            result = workflow_creator(item)

            if result.get('success'):
                logger.info(
                    f"🚀 [LIFECYCLE] Triggered orchestration for {item_type}: "
                    f"{result.get('execution_id')}"
                )
                return {
                    'triggered': True,
                    'execution_id': result.get('execution_id'),
                }

            return {'triggered': False}

        except Exception as e:
            logger.warning(f"⚠️ [LIFECYCLE] Failed to trigger orchestration: {e}")
            return {'triggered': False, 'error': str(e)}

    def _create_opportunity_workflow(self, item) -> Dict[str, Any]:
        """Create and execute workflow for an opportunity item."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep
        from django.utils.text import slugify

        payload = item.payload or {}
        title = item.title[:100]

        try:
            with transaction.atomic():
                # Create workflow
                workflow = CustomWorkflow.objects.create(
                    created_by=item.user,
                    name=f"Opportunity: {title}",
                    slug=f"opp-{slugify(title)[:30]}-{str(item.id)[:8]}",
                    description=f"Workflow for approved opportunity: {item.summary}",
                    content_type='opportunity_execution',
                    category='auto_generated',
                    status='active',
                    execution_mode='sequential',
                    max_retries=2,
                    timeout_seconds=3600,
                    config={
                        'source': 'human_attention_lifecycle',
                        'attention_item_id': str(item.id),
                    }
                )

                # Create steps based on opportunity type
                steps = [
                    ('ResearchAgent', 'Research the opportunity details'),
                    ('OpportunityScoringAgent', 'Score and validate the opportunity'),
                    ('ContentWriterAgent', 'Create action plan document'),
                ]

                for order, (agent, description) in enumerate(steps, start=1):
                    CustomWorkflowStep.objects.create(
                        workflow=workflow,
                        order=order,
                        name=f"Step {order}: {description}",
                        description=f"{description}\n\nOpportunity: {item.summary}",
                        agent=agent,
                        config={'opportunity_context': payload},
                        timeout_seconds=600,
                    )

                # Execute workflow
                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=item.user,
                    input_data={
                        'attention_item_id': str(item.id),
                        'title': item.title,
                        'summary': item.summary,
                        'payload': payload,
                    },
                    async_mode=True,
                )

                return {
                    'success': True,
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                }

        except Exception as e:
            logger.error(f"Failed to create opportunity workflow: {e}")
            return {'success': False, 'error': str(e)}

    def _create_action_workflow(self, item) -> Dict[str, Any]:
        """Create and execute workflow for an action item."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep
        from django.utils.text import slugify

        payload = item.payload or {}
        title = item.title[:100]
        agent_name = payload.get('agent_name', 'ResearchAgent')

        try:
            with transaction.atomic():
                workflow = CustomWorkflow.objects.create(
                    created_by=item.user,
                    name=f"Action: {title}",
                    slug=f"action-{slugify(title)[:30]}-{str(item.id)[:8]}",
                    description=f"Workflow for approved action: {item.summary}",
                    content_type='action_execution',
                    category='auto_generated',
                    status='active',
                    execution_mode='sequential',
                    max_retries=2,
                    timeout_seconds=1800,
                    config={
                        'source': 'human_attention_lifecycle',
                        'attention_item_id': str(item.id),
                    }
                )

                # Single step to execute the action
                CustomWorkflowStep.objects.create(
                    workflow=workflow,
                    order=1,
                    name=f"Execute: {title[:50]}",
                    description=item.summary,
                    agent=agent_name,
                    config={'action_context': payload},
                    timeout_seconds=900,
                )

                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=item.user,
                    input_data={
                        'attention_item_id': str(item.id),
                        'title': item.title,
                        'summary': item.summary,
                        'payload': payload,
                    },
                    async_mode=True,
                )

                return {
                    'success': True,
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                }

        except Exception as e:
            logger.error(f"Failed to create action workflow: {e}")
            return {'success': False, 'error': str(e)}

    def _create_recommendation_workflow(self, item) -> Dict[str, Any]:
        """Create and execute workflow for a recommendation item."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep
        from django.utils.text import slugify

        payload = item.payload or {}
        title = item.title[:100]

        try:
            with transaction.atomic():
                workflow = CustomWorkflow.objects.create(
                    created_by=item.user,
                    name=f"Recommendation: {title}",
                    slug=f"rec-{slugify(title)[:30]}-{str(item.id)[:8]}",
                    description=f"Workflow for approved recommendation: {item.summary}",
                    content_type='recommendation_execution',
                    category='auto_generated',
                    status='active',
                    execution_mode='sequential',
                    max_retries=2,
                    timeout_seconds=2400,
                    config={
                        'source': 'human_attention_lifecycle',
                        'attention_item_id': str(item.id),
                    }
                )

                steps = [
                    ('ResearchAgent', 'Validate recommendation feasibility'),
                    ('ContentStrategyAgent', 'Develop implementation plan'),
                ]

                for order, (agent, description) in enumerate(steps, start=1):
                    CustomWorkflowStep.objects.create(
                        workflow=workflow,
                        order=order,
                        name=f"Step {order}: {description}",
                        description=f"{description}\n\nRecommendation: {item.summary}",
                        agent=agent,
                        config={'recommendation_context': payload},
                        timeout_seconds=600,
                    )

                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=item.user,
                    input_data={
                        'attention_item_id': str(item.id),
                        'title': item.title,
                        'summary': item.summary,
                        'payload': payload,
                    },
                    async_mode=True,
                )

                return {
                    'success': True,
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                }

        except Exception as e:
            logger.error(f"Failed to create recommendation workflow: {e}")
            return {'success': False, 'error': str(e)}

    def _create_project_workflow(self, item) -> Dict[str, Any]:
        """Create and execute workflow for a project item."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep
        from core.models_partnership import PartnershipProject
        from django.utils.text import slugify

        payload = item.payload or {}
        title = item.title[:100]

        try:
            with transaction.atomic():
                # Create project
                project = PartnershipProject.objects.create(
                    user=item.user,
                    project_name=title,
                    project_type='auto_generated',
                    description=item.summary,
                    status='active',
                    ai_contribution_percent=70,
                    human_contribution_percent=30,
                )

                workflow = CustomWorkflow.objects.create(
                    created_by=item.user,
                    name=f"Project: {title}",
                    slug=f"proj-{slugify(title)[:30]}-{str(item.id)[:8]}",
                    description=f"Workflow for approved project: {item.summary}",
                    content_type='project_execution',
                    category='auto_generated',
                    status='active',
                    execution_mode='sequential',
                    max_retries=2,
                    timeout_seconds=7200,
                    config={
                        'source': 'human_attention_lifecycle',
                        'attention_item_id': str(item.id),
                        'project_id': str(project.id),
                    }
                )

                steps = [
                    ('ResearchAgent', 'Research project requirements'),
                    ('ContentStrategyAgent', 'Create project plan'),
                    ('ContentWriterAgent', 'Draft project deliverables'),
                ]

                for order, (agent, description) in enumerate(steps, start=1):
                    CustomWorkflowStep.objects.create(
                        workflow=workflow,
                        order=order,
                        name=f"Step {order}: {description}",
                        description=f"{description}\n\nProject: {item.summary}",
                        agent=agent,
                        config={'project_context': payload},
                        timeout_seconds=900,
                    )

                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=item.user,
                    input_data={
                        'attention_item_id': str(item.id),
                        'project_id': str(project.id),
                        'title': item.title,
                        'summary': item.summary,
                        'payload': payload,
                    },
                    async_mode=True,
                )

                return {
                    'success': True,
                    'project_id': str(project.id),
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                }

        except Exception as e:
            logger.error(f"Failed to create project workflow: {e}")
            return {'success': False, 'error': str(e)}

    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """Get statistics about Human Attention lifecycle."""
        from core.models_human_interface import HumanAttentionItem
        from django.db.models import Count

        now = timezone.now()

        items = HumanAttentionItem.objects.all()

        # Status breakdown
        by_status = dict(
            items.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        # Pending by urgency
        pending_by_urgency = dict(
            items.filter(status='pending')
            .values('urgency')
            .annotate(count=Count('id'))
            .values_list('urgency', 'count')
        )

        # Age of pending items
        pending = items.filter(status='pending')
        aging_stats = {
            'pending_1h': pending.filter(created_at__gte=now - timedelta(hours=1)).count(),
            'pending_1d': pending.filter(
                created_at__lt=now - timedelta(hours=1),
                created_at__gte=now - timedelta(days=1)
            ).count(),
            'pending_3d': pending.filter(
                created_at__lt=now - timedelta(days=1),
                created_at__gte=now - timedelta(days=3)
            ).count(),
            'pending_7d+': pending.filter(created_at__lt=now - timedelta(days=7)).count(),
        }

        # Auto-approved in last 24h
        auto_approved = items.filter(
            decision='approve',
            decision_feedback__startswith='Auto-approved',
            decided_at__gte=now - timedelta(hours=24),
        ).count()

        return {
            'by_status': by_status,
            'pending_by_urgency': pending_by_urgency,
            'aging_stats': aging_stats,
            'auto_approved_24h': auto_approved,
            'total_items': items.count(),
            'pending_count': by_status.get('pending', 0),
            'acted_count': by_status.get('acted', 0),
        }


# Singleton instance
attention_lifecycle = HumanAttentionLifecycleService()


def get_attention_lifecycle() -> HumanAttentionLifecycleService:
    """Get the singleton attention lifecycle service instance."""
    return attention_lifecycle

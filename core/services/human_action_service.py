"""
Human Action Service - Session 549

Creates and manages notifications that require human policy decisions.
These are concerns that cannot be auto-resolved and need user input.

Categories of human action required:
- legal_review: Legal/privacy concerns requiring policy decisions
- data_provenance: Data source verification needed
- security_review: Security implications requiring assessment
- compliance: Compliance decisions needed
- policy_decision: General policy decisions

This integrates with:
- TrackedConcern model (concern tracking)
- ProactiveNotification model (UI alerts)
- Discord notifications (optional)
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class HumanActionService:
    """
    Service for creating and managing human action required notifications.
    """

    # Mapping of concern patterns to action categories
    ACTION_CATEGORIES = {
        'legal': 'legal_review',
        'privacy': 'legal_review',
        'provenance': 'data_provenance',
        'community-sourced': 'data_provenance',
        'creativemarket': 'data_provenance',
        'security': 'security_review',
        'unverified': 'security_review',
        'misinformation': 'security_review',
        'compliance': 'compliance',
        'policy': 'policy_decision',
    }

    # Category metadata for UI display
    CATEGORY_METADATA = {
        'legal_review': {
            'icon': 'gavel',
            'color': '#dc2626',  # Red
            'label': 'Legal Review Required',
            'description': 'This concern involves legal or privacy implications that require human review.',
        },
        'data_provenance': {
            'icon': 'database',
            'color': '#f59e0b',  # Amber
            'label': 'Data Provenance Check',
            'description': 'Data source verification or licensing review needed.',
        },
        'security_review': {
            'icon': 'shield-exclamation',
            'color': '#ef4444',  # Red
            'label': 'Security Review',
            'description': 'Security implications need to be assessed.',
        },
        'compliance': {
            'icon': 'clipboard-check',
            'color': '#8b5cf6',  # Purple
            'label': 'Compliance Decision',
            'description': 'Compliance-related decision needed.',
        },
        'policy_decision': {
            'icon': 'scale',
            'color': '#06b6d4',  # Cyan
            'label': 'Policy Decision',
            'description': 'A policy decision is required.',
        },
    }

    # Quick action templates by category
    QUICK_ACTIONS = {
        'legal_review': [
            {'action': 'approve', 'label': 'Approve After Review', 'style': 'success'},
            {'action': 'reject', 'label': 'Reject - Too Risky', 'style': 'danger'},
            {'action': 'defer', 'label': 'Need More Info', 'style': 'secondary'},
        ],
        'data_provenance': [
            {'action': 'verified', 'label': 'Source Verified', 'style': 'success'},
            {'action': 'block', 'label': 'Block Source', 'style': 'danger'},
            {'action': 'monitor', 'label': 'Monitor Only', 'style': 'warning'},
        ],
        'security_review': [
            {'action': 'safe', 'label': 'Marked Safe', 'style': 'success'},
            {'action': 'block', 'label': 'Block Content', 'style': 'danger'},
            {'action': 'investigate', 'label': 'Investigate Further', 'style': 'warning'},
        ],
        'compliance': [
            {'action': 'compliant', 'label': 'Mark Compliant', 'style': 'success'},
            {'action': 'non_compliant', 'label': 'Non-Compliant', 'style': 'danger'},
            {'action': 'remediate', 'label': 'Needs Remediation', 'style': 'warning'},
        ],
        'policy_decision': [
            {'action': 'accept', 'label': 'Accept Risk', 'style': 'success'},
            {'action': 'reject', 'label': 'Reject', 'style': 'danger'},
            {'action': 'defer', 'label': 'Defer Decision', 'style': 'secondary'},
        ],
    }

    def __init__(self):
        from core.models_unified_system import ProactiveNotification, TrackedConcern
        self.ProactiveNotification = ProactiveNotification
        self.TrackedConcern = TrackedConcern

    def _categorize_concern(self, concern_text: str) -> str:
        """Determine the action category based on concern text."""
        text_lower = concern_text.lower()
        for keyword, category in self.ACTION_CATEGORIES.items():
            if keyword in text_lower:
                return category
        return 'policy_decision'

    def create_action_notification(
        self,
        concern,
        user=None,
    ) -> Optional[Any]:
        """
        Create a human action required notification for a concern.

        Args:
            concern: TrackedConcern instance
            user: Optional user to notify (defaults to first admin)

        Returns:
            ProactiveNotification instance or None
        """
        # Determine action category
        category = self._categorize_concern(concern.concern_text)
        metadata = self.CATEGORY_METADATA.get(category, self.CATEGORY_METADATA['policy_decision'])
        quick_actions = self.QUICK_ACTIONS.get(category, self.QUICK_ACTIONS['policy_decision'])

        # Get user (default to first superuser/admin)
        if not user:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()

        if not user:
            logger.warning("No user found to notify")
            return None

        # Check if notification already exists for this concern
        existing = self.ProactiveNotification.objects.filter(
            rich_content__concern_id=str(concern.id),
            notification_type='action_required',
            is_dismissed=False,
        ).first()

        if existing:
            logger.info(f"Notification already exists for concern {concern.id}")
            return existing

        # Create notification
        notification = self.ProactiveNotification.objects.create(
            user=user,
            notification_type='action_required',
            priority='high' if concern.severity in ['critical', 'high'] else 'medium',
            title=f"🚨 {metadata['label']}",
            message=concern.concern_text,
            icon=metadata['icon'],
            action_url=f'/ai-studio/#research-concerns',
            action_label='Review Concern',
            quick_actions=quick_actions,
            rich_content={
                'concern_id': str(concern.id),
                'category': category,
                'severity': concern.severity,
                'times_detected': concern.times_detected,
                'days_active': concern.days_active,
                'color': metadata['color'],
                'description': metadata['description'],
            },
            scheduled_at=timezone.now(),
            sent_at=timezone.now(),
            delivery_status='sent',
        )

        logger.info(f"Created action_required notification for concern: {concern.id}")
        return notification

    def create_notifications_for_active_concerns(self) -> Dict[str, Any]:
        """
        Create notifications for all active concerns that need human action.

        Returns:
            Summary of created notifications.
        """
        # Get concerns that are active/in_progress and categorized as 'general'
        # (general category means they can't be auto-verified)
        active_concerns = self.TrackedConcern.objects.filter(
            status__in=['active', 'in_progress', 'recurring'],
            category='general',  # General concerns need human review
        )

        results = {
            'total_concerns': active_concerns.count(),
            'notifications_created': 0,
            'already_notified': 0,
            'concerns': [],
        }

        for concern in active_concerns:
            notification = self.create_action_notification(concern)
            if notification:
                if notification.created_at >= timezone.now() - timezone.timedelta(seconds=5):
                    results['notifications_created'] += 1
                else:
                    results['already_notified'] += 1
                results['concerns'].append({
                    'id': str(concern.id),
                    'text': concern.concern_text[:60],
                    'severity': concern.severity,
                })

        logger.info(f"Created {results['notifications_created']} action notifications "
                   f"({results['already_notified']} already existed)")

        return results

    def handle_action_response(
        self,
        notification_id: str,
        action: str,
        notes: str = None,
    ) -> Dict[str, Any]:
        """
        Handle user's response to an action-required notification.

        Args:
            notification_id: The notification ID
            action: The action taken (e.g., 'approve', 'reject', 'defer')
            notes: Optional notes from the user

        Returns:
            Result of the action handling.
        """
        try:
            notification = self.ProactiveNotification.objects.get(id=notification_id)
        except self.ProactiveNotification.DoesNotExist:
            return {'success': False, 'error': 'Notification not found'}

        concern_id = notification.rich_content.get('concern_id')
        if not concern_id:
            return {'success': False, 'error': 'No concern linked to notification'}

        try:
            concern = self.TrackedConcern.objects.get(id=concern_id)
        except self.TrackedConcern.DoesNotExist:
            return {'success': False, 'error': 'Concern not found'}

        # Update concern based on action
        action_results = {
            'approve': ('resolved', 'Approved by user'),
            'verified': ('resolved', 'Source verified by user'),
            'safe': ('resolved', 'Marked safe by user'),
            'compliant': ('resolved', 'Marked compliant by user'),
            'accept': ('accepted', 'Risk accepted by user'),
            'reject': ('resolved', 'Rejected and blocked by user'),
            'block': ('resolved', 'Blocked by user'),
            'non_compliant': ('resolved', 'Marked non-compliant - action taken'),
            'defer': ('monitoring', 'Deferred - needs more information'),
            'monitor': ('monitoring', 'Set to monitor only'),
            'investigate': ('in_progress', 'Under investigation'),
            'remediate': ('in_progress', 'Remediation in progress'),
        }

        new_status, resolution_note = action_results.get(action, ('active', f'Action: {action}'))

        # Update concern
        concern.status = new_status
        concern.resolution_notes = f"{resolution_note}. {notes or ''}".strip()
        if new_status in ['resolved', 'accepted']:
            concern.resolved_at = timezone.now()
        concern.save()

        # Mark notification as acted upon
        notification.is_acted_upon = True
        notification.acted_at = timezone.now()
        notification.action_result = {
            'action': action,
            'notes': notes,
            'new_status': new_status,
        }
        notification.is_dismissed = True
        notification.dismissed_at = timezone.now()
        notification.save()

        logger.info(f"Handled action '{action}' for concern {concern_id}, new status: {new_status}")

        return {
            'success': True,
            'concern_id': str(concern.id),
            'new_status': new_status,
            'resolution_note': resolution_note,
        }

    def get_pending_actions(self, user=None) -> Dict[str, Any]:
        """
        Get all pending action-required notifications.

        Returns:
            List of pending action notifications with metadata.
        """
        query = self.ProactiveNotification.objects.filter(
            notification_type='action_required',
            is_dismissed=False,
            is_acted_upon=False,
        ).order_by('-created_at')

        if user:
            query = query.filter(user=user)

        notifications = []
        for n in query[:20]:  # Limit to 20
            notifications.append({
                'id': str(n.id),
                'title': n.title,
                'message': n.message,
                'priority': n.priority,
                'icon': n.icon,
                'category': n.rich_content.get('category'),
                'color': n.rich_content.get('color'),
                'severity': n.rich_content.get('severity'),
                'concern_id': n.rich_content.get('concern_id'),
                'quick_actions': n.quick_actions,
                'created_at': n.created_at.isoformat(),
                'is_read': n.is_read,
            })

        return {
            'total': query.count(),
            'notifications': notifications,
        }


# Singleton instance
_human_action_service = None

def get_human_action_service() -> HumanActionService:
    """Get or create the human action service instance."""
    global _human_action_service
    if _human_action_service is None:
        _human_action_service = HumanActionService()
    return _human_action_service

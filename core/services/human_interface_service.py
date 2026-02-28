"""
Human Interface Service - Main Orchestrator
============================================

Session 686: The Human layer connecting the operator to the autonomous AI ecosystem.

This service:
1. Aggregates attention items from all system sources
2. Captures and records human decisions
3. Feeds human feedback back to ML systems
4. Manages system control state
"""

import logging
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db.models import Avg, Count, Q, Sum
from datetime import timedelta

logger = logging.getLogger(__name__)


class HumanInterfaceService:
    """
    Main service coordinating all Human Interface Layer components.

    Usage:
        from core.services.human_interface_service import get_human_interface_service

        service = get_human_interface_service(user)
        items = service.get_attention_stream(limit=20)
        service.record_decision(item_id, 'approve', feedback='Looks good')
    """

    def __init__(self, user):
        self.user = user

    # =========================================================================
    # ATTENTION STREAM
    # =========================================================================

    def get_attention_stream(
        self,
        limit: int = 20,
        urgency_filter: List[str] = None,
        status_filter: List[str] = None,
        include_ml_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get prioritized attention items for this human.

        Args:
            limit: Maximum items to return
            urgency_filter: List of urgency levels to include
            status_filter: List of statuses to include
            include_ml_context: Include ML prediction context

        Returns:
            List of attention items sorted by priority
        """
        from core.models_human_interface import HumanAttentionItem

        # Build query
        query = HumanAttentionItem.objects.filter(user=self.user)

        if urgency_filter:
            query = query.filter(urgency__in=urgency_filter)

        if status_filter:
            query = query.filter(status__in=status_filter)
        else:
            # Default: pending and viewed items
            query = query.filter(status__in=['pending', 'viewed'])

        # Exclude expired items
        query = query.exclude(
            expires_at__lt=timezone.now()
        )

        # Order by priority and recency
        items = query.order_by('-priority_score', '-created_at')[:limit]

        # Convert to dicts
        result = []
        for item in items:
            item_dict = {
                'id': str(item.id),
                'source_type': item.source_type,
                'source_id': item.source_id,  # Session 742: Added for source linking
                'source_agent': item.source_agent,
                'item_type': item.item_type,
                'title': item.title,
                'summary': item.summary,
                'urgency': item.urgency,
                'priority_score': item.priority_score,
                'impact_estimate': item.impact_estimate,  # Session 742: Added
                'status': item.status,
                'created_at': item.created_at.isoformat(),
                'expires_at': item.expires_at.isoformat() if item.expires_at else None,  # Session 742: Added
                'deferred_until': item.deferred_until.isoformat() if item.deferred_until else None,  # Session 742
                'payload': item.payload,
                # Session 742: Add ML fields at top level for easier frontend access
                'ml_confidence': item.ml_confidence,
                'ml_recommendation': item.ml_recommendation,
                # Session 746: Add decision fields
                'decision': item.decision,
                'decision_feedback': item.decision_feedback,
                'decision_confidence': item.decision_confidence,
                'decided_at': item.decided_at.isoformat() if item.decided_at else None,
                'time_to_decision_ms': item.time_to_decision_ms,
                'viewed_at': item.viewed_at.isoformat() if item.viewed_at else None,
                # Session 746: Add ML override fields
                'human_overrode_ml': item.human_overrode_ml,
                'override_reason': item.override_reason,
                # Session 746: Add verification fields for Watch & Verify
                'verification_outcome': item.verification_outcome,
                'verified_at': item.verified_at.isoformat() if item.verified_at else None,
                'verification_profit': item.verification_profit,
                'verification_notes': item.verification_notes,
                'event_completed_at': item.event_completed_at.isoformat() if item.event_completed_at else None,
            }

            if include_ml_context and item.ml_prediction:
                item_dict['ml_context'] = {
                    'prediction': item.ml_prediction,
                    'confidence': item.ml_confidence,
                    'recommendation': item.ml_recommendation,
                }

            result.append(item_dict)

        return result

    def get_attention_stats(self) -> Dict[str, Any]:
        """Get statistics about attention items."""
        from core.models_human_interface import HumanAttentionItem, HumanFeedbackRecord, HumanControlAction

        items = HumanAttentionItem.objects.filter(user=self.user)

        pending_count = items.filter(status='pending').count()
        by_urgency = dict(
            items.filter(status='pending')
            .values('urgency')
            .annotate(count=Count('id'))
            .values_list('urgency', 'count')
        )

        # Average decision time
        avg_time = items.filter(
            time_to_decision_ms__isnull=False
        ).aggregate(avg=Avg('time_to_decision_ms'))['avg']

        # ML agreement rate
        total_with_ml = items.filter(ml_prediction__isnull=False, decision__isnull=False).count()
        agreed_with_ml = items.filter(
            ml_prediction__isnull=False,
            decision__isnull=False,
            human_overrode_ml=False
        ).count()
        ml_agreement = (agreed_with_ml / total_with_ml * 100) if total_with_ml > 0 else None

        # Session 746: Add comprehensive stats

        # By item type (pending items only - Session 766 fix)
        pending_items = items.filter(status='pending')
        by_type = dict(
            pending_items.values('item_type')
            .annotate(count=Count('id'))
            .values_list('item_type', 'count')
        )

        # By source agent (pending items only - Session 766 fix)
        by_source = dict(
            pending_items.exclude(source_agent='')
            .values('source_agent')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
            .values_list('source_agent', 'count')
        )

        # By status
        by_status = dict(
            items.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        # By decision (for acted items)
        by_decision = dict(
            items.exclude(decision__isnull=True)
            .values('decision')
            .annotate(count=Count('id'))
            .values_list('decision', 'count')
        )

        # Verification stats (for Watch & Verify)
        watching_count = items.filter(status='watching').count()
        verified_count = items.filter(status='verified').count()
        verification_outcomes = dict(
            items.exclude(verification_outcome__isnull=True)
            .values('verification_outcome')
            .annotate(count=Count('id'))
            .values_list('verification_outcome', 'count')
        )
        # Calculate paper P/L
        paper_profit = items.filter(
            verification_profit__isnull=False
        ).aggregate(total=Sum('verification_profit'))['total'] or 0

        # ML override stats
        override_count = items.filter(human_overrode_ml=True).count()

        # Feedback records
        feedback_count = HumanFeedbackRecord.objects.filter(user=self.user).count()
        fed_to_ml_count = HumanFeedbackRecord.objects.filter(user=self.user, fed_to_ml=True).count()

        # Recent control actions
        recent_actions = list(
            HumanControlAction.objects.filter(user=self.user)
            .order_by('-created_at')[:10]
            .values('action_type', 'target_type', 'target_id', 'reason', 'created_at')
        )
        for action in recent_actions:
            action['created_at'] = action['created_at'].isoformat()

        return {
            'pending_count': pending_count,
            'by_urgency': by_urgency,
            'avg_decision_time_ms': int(avg_time) if avg_time else None,
            'ml_agreement_rate': round(ml_agreement, 1) if ml_agreement else None,
            'total_with_ml_context': total_with_ml,
            # Session 746: New stats
            'by_type': by_type,
            'by_source': by_source,
            'by_status': by_status,
            'by_decision': by_decision,
            'watching_count': watching_count,
            'verified_count': verified_count,
            'verification_outcomes': verification_outcomes,
            'paper_profit': round(paper_profit, 2) if paper_profit else 0,
            'override_count': override_count,
            'feedback_count': feedback_count,
            'fed_to_ml_count': fed_to_ml_count,
            'recent_actions': recent_actions,
            'total_items': items.count(),
        }

    # =========================================================================
    # DECISION RECORDING
    # =========================================================================

    def record_decision(
        self,
        item_id: str,
        decision: str,
        feedback: str = '',
        confidence: float = None
    ) -> Dict[str, Any]:
        """
        Record a human decision on an attention item.

        Args:
            item_id: UUID of the attention item
            decision: Decision type (approve, reject, modify, defer, etc.)
            feedback: Optional feedback text
            confidence: Human's confidence in the decision (0-1)

        Returns:
            Updated item data
        """
        from core.models_human_interface import HumanAttentionItem, HumanFeedbackRecord

        try:
            item = HumanAttentionItem.objects.get(id=item_id, user=self.user)
        except HumanAttentionItem.DoesNotExist:
            return {'success': False, 'error': 'Item not found'}

        # Record the decision
        item.record_decision(decision, feedback, confidence)

        # Create feedback record for ML learning
        HumanFeedbackRecord.objects.create(
            attention_item=item,
            user=self.user,
            decision=decision,
            feedback_text=feedback,
            confidence=confidence,
            ml_task_type=item.ml_prediction.get('task_type') if item.ml_prediction else None,
            ml_models_used=item.ml_prediction.get('models_used') if item.ml_prediction else None,
            ml_prediction=item.ml_prediction,
            ml_confidence=item.ml_confidence,
            human_agreed_with_ml=not item.human_overrode_ml if item.ml_prediction else None,
            confidence_delta=(confidence - item.ml_confidence) if confidence and item.ml_confidence else None,
        )

        # Update user preferences based on decision
        self._update_preferences_from_decision(item)

        # Trigger ML feedback if applicable
        if item.ml_prediction and item.human_overrode_ml:
            self._feed_to_ml(item)

        logger.info(f"Human decision recorded: {decision} on {item.title}")

        return {
            'success': True,
            'item_id': str(item.id),
            'decision': decision,
            'human_overrode_ml': item.human_overrode_ml,
        }

    def defer_item(self, item_id: str, remind_at: timezone.datetime) -> Dict[str, Any]:
        """Defer an attention item until a specific time."""
        from core.models_human_interface import HumanAttentionItem

        try:
            item = HumanAttentionItem.objects.get(id=item_id, user=self.user)
        except HumanAttentionItem.DoesNotExist:
            return {'success': False, 'error': 'Item not found'}

        item.status = 'deferred'
        item.deferred_until = remind_at
        item.save(update_fields=['status', 'deferred_until'])

        return {'success': True, 'deferred_until': remind_at.isoformat()}

    # =========================================================================
    # CONTROL PANEL
    # =========================================================================

    def get_system_state(self) -> Dict[str, Any]:
        """Get current system control state."""
        from core.models_human_interface import HumanSystemState

        state = HumanSystemState.get_state()

        return {
            'system_paused': state.system_paused,
            'review_mode': state.review_mode,
            'quiet_mode': state.quiet_mode,
            'quiet_mode_until': state.quiet_mode_until.isoformat() if state.quiet_mode_until else None,
            'paused_agents': state.paused_agents,
            'ml_confidence_threshold': state.ml_confidence_threshold,
            'auto_approve_threshold': state.auto_approve_threshold,
        }

    def pause_agent(self, agent_name: str, reason: str = '') -> Dict[str, Any]:
        """Pause a specific agent."""
        from core.models_human_interface import HumanSystemState, HumanControlAction

        state = HumanSystemState.get_state()
        old_value = state.paused_agents.copy()

        state.pause_agent(agent_name)
        state.updated_by = self.user
        state.save()

        # Log the action
        HumanControlAction.objects.create(
            user=self.user,
            action_type='pause_agent',
            target_type='agent',
            target_id=agent_name,
            old_value=old_value,
            new_value=state.paused_agents,
            reason=reason,
        )

        return {'success': True, 'paused_agents': state.paused_agents}

    def resume_agent(self, agent_name: str, reason: str = '') -> Dict[str, Any]:
        """Resume a specific agent."""
        from core.models_human_interface import HumanSystemState, HumanControlAction

        state = HumanSystemState.get_state()
        old_value = state.paused_agents.copy()

        state.resume_agent(agent_name)
        state.updated_by = self.user
        state.save()

        HumanControlAction.objects.create(
            user=self.user,
            action_type='resume_agent',
            target_type='agent',
            target_id=agent_name,
            old_value=old_value,
            new_value=state.paused_agents,
            reason=reason,
        )

        return {'success': True, 'paused_agents': state.paused_agents}

    def set_quiet_mode(self, enabled: bool, duration_minutes: int = None) -> Dict[str, Any]:
        """Enable or disable quiet mode."""
        from core.models_human_interface import HumanSystemState, HumanControlAction

        state = HumanSystemState.get_state()
        old_value = {'quiet_mode': state.quiet_mode, 'quiet_mode_until': str(state.quiet_mode_until)}

        state.quiet_mode = enabled
        if enabled and duration_minutes:
            state.quiet_mode_until = timezone.now() + timedelta(minutes=duration_minutes)
        elif not enabled:
            state.quiet_mode_until = None

        state.updated_by = self.user
        state.save()

        new_value = {'quiet_mode': state.quiet_mode, 'quiet_mode_until': str(state.quiet_mode_until)}

        HumanControlAction.objects.create(
            user=self.user,
            action_type='quiet_mode',
            target_type='system',
            target_id='global',
            old_value=old_value,
            new_value=new_value,
        )

        return {
            'success': True,
            'quiet_mode': state.quiet_mode,
            'quiet_mode_until': state.quiet_mode_until.isoformat() if state.quiet_mode_until else None
        }

    def set_review_mode(self, enabled: bool) -> Dict[str, Any]:
        """Enable or disable review mode (all decisions require human approval)."""
        from core.models_human_interface import HumanSystemState, HumanControlAction

        state = HumanSystemState.get_state()
        old_value = state.review_mode

        state.review_mode = enabled
        state.updated_by = self.user
        state.save()

        HumanControlAction.objects.create(
            user=self.user,
            action_type='review_mode',
            target_type='system',
            target_id='global',
            old_value=old_value,
            new_value=enabled,
        )

        return {'success': True, 'review_mode': state.review_mode}

    def adjust_ml_threshold(self, threshold: float) -> Dict[str, Any]:
        """Adjust the ML confidence threshold."""
        from core.models_human_interface import HumanSystemState, HumanControlAction

        if not 0 <= threshold <= 1:
            return {'success': False, 'error': 'Threshold must be between 0 and 1'}

        state = HumanSystemState.get_state()
        old_value = state.ml_confidence_threshold

        state.ml_confidence_threshold = threshold
        state.updated_by = self.user
        state.save()

        HumanControlAction.objects.create(
            user=self.user,
            action_type='adjust_threshold',
            target_type='model',
            target_id='ml_confidence',
            old_value=old_value,
            new_value=threshold,
        )

        return {'success': True, 'ml_confidence_threshold': threshold}

    # =========================================================================
    # PREFERENCES
    # =========================================================================

    def get_preferences(self) -> Dict[str, Any]:
        """Get user's human interface preferences."""
        from core.models_human_interface import HumanPreference

        pref, created = HumanPreference.objects.get_or_create(user=self.user)

        return {
            'quiet_hours_start': str(pref.quiet_hours_start) if pref.quiet_hours_start else None,
            'quiet_hours_end': str(pref.quiet_hours_end) if pref.quiet_hours_end else None,
            'min_urgency_to_notify': pref.min_urgency_to_notify,
            'preferred_channel': pref.preferred_channel,
            'review_depth': pref.review_depth,
            'auto_approve_low_risk': pref.auto_approve_low_risk,
            'trusted_agents': pref.trusted_agents,
            'blocked_sources': pref.blocked_sources,
            # Learned preferences
            'topic_weights': pref.topic_weights,
            'avg_decision_time_ms': pref.avg_decision_time_ms,
            'approval_rate': pref.approval_rate,
            'total_decisions': pref.total_decisions,
        }

    def update_preferences(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        from core.models_human_interface import HumanPreference

        pref, _ = HumanPreference.objects.get_or_create(user=self.user)

        allowed_fields = [
            'quiet_hours_start', 'quiet_hours_end', 'min_urgency_to_notify',
            'preferred_channel', 'review_depth', 'auto_approve_low_risk',
            'trusted_agents', 'blocked_sources'
        ]

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(pref, field, value)

        pref.save()

        return {'success': True, 'preferences': self.get_preferences()}

    # =========================================================================
    # ITEM CREATION (for other services to use)
    # =========================================================================

    def create_attention_item(
        self,
        source_type: str,
        item_type: str,
        title: str,
        summary: str,
        urgency: str = 'medium',
        payload: Dict = None,
        ml_prediction: Dict = None,
        ml_confidence: float = None,
        ml_recommendation: str = '',
        source_id: str = '',
        source_agent: str = '',
        expires_at: timezone.datetime = None,
        deduplicate: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new attention item.

        This is called by other services (ThinkingAgent, PilotGate, etc.)
        to surface items requiring human attention.

        Args:
            deduplicate: If True (default), skip creating if a similar item exists
                        that hasn't been acted upon yet. This prevents duplicate
                        arbitrage alerts and other repetitive items.
        """
        from core.models_human_interface import HumanAttentionItem

        # Session 746: Deduplication logic to prevent duplicate items
        if deduplicate:
            # Build query to find existing similar items
            # that are still pending/viewed (not acted, expired, watching, or verified)
            query = HumanAttentionItem.objects.filter(
                user=self.user,
                source_type=source_type,
                item_type=item_type,
                status__in=[
                    HumanAttentionItem.STATUS_PENDING,
                    HumanAttentionItem.STATUS_VIEWED,
                    HumanAttentionItem.STATUS_DEFERRED,
                ],
            )

            # If source_id is available, use it for exact matching
            # Otherwise, fall back to matching by title (handles empty source_id cases)
            if source_id:
                query = query.filter(source_id=source_id)
            else:
                query = query.filter(title=title)

            existing_item = query.first()

            if existing_item:
                # Update mutable fields so repeated runs refresh severity/payload
                update_fields = []
                if summary and existing_item.summary != summary:
                    existing_item.summary = summary
                    update_fields.append('summary')
                if urgency and existing_item.urgency != urgency:
                    existing_item.urgency = urgency
                    update_fields.append('urgency')
                if payload and existing_item.payload != payload:
                    existing_item.payload = payload
                    update_fields.append('payload')
                new_score = self._calculate_priority_score(
                    urgency=urgency or existing_item.urgency,
                    ml_confidence=ml_confidence,
                    source_type=source_type,
                )
                if existing_item.priority_score != new_score:
                    existing_item.priority_score = new_score
                    update_fields.append('priority_score')
                if update_fields:
                    existing_item.save(update_fields=update_fields)
                    logger.debug(
                        f"Updated duplicate attention item {existing_item.id}: "
                        f"{', '.join(update_fields)}"
                    )
                return {
                    'success': True,
                    'item_id': str(existing_item.id),
                    'priority_score': existing_item.priority_score,
                    'deduplicated': True,
                    'fields_updated': update_fields,
                    'message': 'Similar item already exists',
                }

        # Calculate priority score
        priority_score = self._calculate_priority_score(
            urgency=urgency,
            ml_confidence=ml_confidence,
            source_type=source_type,
        )

        item = HumanAttentionItem.objects.create(
            user=self.user,
            source_type=source_type,
            source_id=source_id,
            source_agent=source_agent,
            item_type=item_type,
            title=title,
            summary=summary,
            urgency=urgency,
            priority_score=priority_score,
            payload=payload or {},
            ml_prediction=ml_prediction,
            ml_confidence=ml_confidence,
            ml_recommendation=ml_recommendation,
            expires_at=expires_at,
        )

        logger.info(f"Created attention item: [{urgency.upper()}] {title}")

        return {
            'success': True,
            'item_id': str(item.id),
            'priority_score': priority_score,
        }

    # =========================================================================
    # PRIVATE HELPERS
    # =========================================================================

    def _calculate_priority_score(
        self,
        urgency: str,
        ml_confidence: float = None,
        source_type: str = '',
    ) -> float:
        """Calculate priority score for an attention item."""
        from core.models_human_interface import HumanPreference

        # Base urgency scores
        urgency_scores = {
            'critical': 10.0,
            'high': 7.0,
            'medium': 4.0,
            'low': 1.0,
        }

        score = urgency_scores.get(urgency, 4.0)

        # Boost for low ML confidence (needs human review)
        if ml_confidence is not None and ml_confidence < 0.7:
            score += 2.0 * (1 - ml_confidence)

        # Apply user's source preferences
        try:
            pref = HumanPreference.objects.get(user=self.user)
            source_weight = pref.source_weights.get(source_type, 1.0)
            score *= source_weight
        except HumanPreference.DoesNotExist:
            pass

        return round(score, 2)

    def _update_preferences_from_decision(self, item) -> None:
        """Update learned preferences based on a decision."""
        from core.models_human_interface import HumanPreference

        pref, _ = HumanPreference.objects.get_or_create(user=self.user)

        # Update source weights based on engagement
        if item.source_type:
            weights = pref.source_weights
            current = weights.get(item.source_type, 1.0)
            # Slight boost for sources user engages with
            weights[item.source_type] = min(2.0, current * 1.05)
            pref.source_weights = weights

        pref.update_learned_stats()

    def _feed_to_ml(self, item) -> None:
        """Feed human override back to ML system."""
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # This would update model scores based on human corrections
            # For now, just log the feedback
            logger.info(
                f"ML Feedback: Human overrode {item.ml_recommendation} -> {item.decision} "
                f"(confidence was {item.ml_confidence})"
            )

            # Mark feedback as fed to ML
            from core.models_human_interface import HumanFeedbackRecord
            HumanFeedbackRecord.objects.filter(
                attention_item=item,
                fed_to_ml=False
            ).update(fed_to_ml=True, fed_at=timezone.now())

        except Exception as e:
            logger.warning(f"Failed to feed to ML: {e}")


# Factory function
_service_cache = {}


def get_human_interface_service(user) -> HumanInterfaceService:
    """
    Get or create a HumanInterfaceService for a user.

    Args:
        user: Django User object

    Returns:
        HumanInterfaceService instance
    """
    user_id = user.id if user else None

    if user_id not in _service_cache:
        _service_cache[user_id] = HumanInterfaceService(user)

    return _service_cache[user_id]

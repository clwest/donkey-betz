"""
Human Attention Bridge - Integration Layer
==========================================

Session 687: Connects system events to the Human Interface attention stream.

This bridge listens to various system events and creates attention items
when human review/decision is needed.

Integration points:
1. Pilot Gates - When gates need approval
2. Agent Executions - Important completions or failures
3. Arbitrage Detection - Betting opportunities found
4. System Alerts - High API usage, errors, etc.
5. Content Review - Generated content needing approval
"""

import logging
from datetime import datetime, date
from typing import Optional, Any
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def _serialize_for_json(obj: Any) -> Any:
    """
    Session 736: Recursively serialize objects for JSON storage.
    Handles datetime objects that cause 'Object of type datetime is not JSON serializable' errors.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    return obj


class HumanAttentionBridge:
    """
    Bridge that creates attention items from system events.

    Usage:
        from core.services.human_attention_bridge import attention_bridge

        # Manually create attention item for a user
        attention_bridge.create_pilot_gate_attention(gate, user)

        # Or let signals auto-create from model changes
    """

    @staticmethod
    def get_admin_users():
        """Get users who should receive system-wide attention items."""
        return User.objects.filter(is_staff=True, is_active=True)

    @staticmethod
    def get_service(user):
        """Get the HumanInterfaceService for a user."""
        from core.services.human_interface_service import get_human_interface_service
        return get_human_interface_service(user)

    # =========================================================================
    # PILOT GATES
    # =========================================================================

    def create_pilot_gate_attention(self, gate, user=None):
        """
        Create attention item when a pilot gate needs approval.

        Args:
            gate: PilotReadinessGate instance
            user: Target user (if None, notifies all admins)
        """
        try:
            from core.models_pilot_readiness import PilotReadinessGate

            # Skip if not pending review
            if gate.status != 'pending_review':
                return

            users = [user] if user else self.get_admin_users()

            for target_user in users:
                service = self.get_service(target_user)

                # Build summary
                summary = f"Pilot gate '{gate.decision.topic[:50]}' is ready for review."
                if gate.risk_level:
                    summary += f" Risk level: {gate.risk_level}."

                service.create_attention_item(
                    source_type='pilot_gate',
                    source_id=str(gate.id),
                    source_agent='ThinkingAgent',
                    item_type='approval',
                    title=f"Pilot Gate: {gate.decision.topic[:40]}",
                    summary=summary,
                    urgency='high' if gate.risk_level in ['high', 'critical'] else 'medium',
                    payload={
                        'gate_id': str(gate.id),
                        'decision_id': str(gate.decision.id),
                        'risk_level': gate.risk_level,
                        'checklist_progress': gate.checklist_progress,
                    },
                )
                logger.info(f"Created pilot gate attention for user {target_user.username}")

        except Exception as e:
            logger.error(f"Failed to create pilot gate attention: {e}")

    # =========================================================================
    # AGENT EXECUTIONS
    # =========================================================================

    def create_agent_execution_attention(
        self,
        execution,
        urgency: str = 'medium',
        user=None
    ):
        """
        Create attention item for important agent executions.

        Called for:
        - Failed executions of critical agents
        - Completed executions requiring review
        - High-value outputs
        """
        try:
            users = [user] if user else self.get_admin_users()

            agent_name = execution.template.name if execution.template else 'Unknown Agent'
            is_failure = execution.status == 'failed'

            for target_user in users:
                service = self.get_service(target_user)

                if is_failure:
                    title = f"Agent Failed: {agent_name}"
                    summary = f"{agent_name} execution failed. Task: {execution.task_description[:100]}"
                    item_type = 'alert'
                    urgency = 'high'
                else:
                    title = f"Agent Complete: {agent_name}"
                    summary = f"{agent_name} completed task. Review output for quality."
                    item_type = 'review'

                service.create_attention_item(
                    source_type='agent_execution',
                    source_id=str(execution.id),
                    source_agent=agent_name,
                    item_type=item_type,
                    title=title,
                    summary=summary,
                    urgency=urgency,
                    payload={
                        'execution_id': str(execution.id),
                        'agent_name': agent_name,
                        'status': execution.status,
                        'task_type': execution.task_type,
                        'execution_time': execution.execution_time_seconds,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to create agent execution attention: {e}")

    # =========================================================================
    # ARBITRAGE / BETTING OPPORTUNITIES
    # =========================================================================

    def create_arbitrage_attention(
        self,
        opportunity: dict,
        user=None
    ):
        """
        Create attention item for arbitrage opportunities.

        Args:
            opportunity: Dict with keys: title, profit_pct, markets, expires_at
            user: Target user
        """
        try:
            users = [user] if user else self.get_admin_users()

            profit_pct = opportunity.get('profit_pct', 0)

            # Determine urgency based on profit
            if profit_pct >= 5:
                urgency = 'critical'
            elif profit_pct >= 2:
                urgency = 'high'
            else:
                urgency = 'medium'

            # Session 736: Serialize payload to handle datetime objects
            serialized_payload = _serialize_for_json(opportunity)

            for target_user in users:
                service = self.get_service(target_user)

                service.create_attention_item(
                    source_type='arbitrage_detection',
                    source_id=opportunity.get('id', ''),
                    source_agent='ArbitrageDetector',
                    item_type='arbitrage',
                    title=f"Arbitrage: {opportunity.get('title', 'Opportunity Found')}",
                    summary=f"{profit_pct:.1f}% guaranteed profit detected across {', '.join(opportunity.get('markets', []))}",
                    urgency=urgency,
                    payload=serialized_payload,
                    expires_at=opportunity.get('expires_at'),
                )
                logger.info(f"Created arbitrage attention for user {target_user.username}")

        except Exception as e:
            logger.error(f"Failed to create arbitrage attention: {e}")

    # =========================================================================
    # SYSTEM ALERTS
    # =========================================================================

    def create_system_alert(
        self,
        alert_type: str,
        title: str,
        summary: str,
        urgency: str = 'medium',
        payload: dict = None,
        user=None
    ):
        """
        Create attention item for system alerts.

        Args:
            alert_type: Type of alert (api_usage, error, security, etc.)
            title: Alert title
            summary: Alert description
            urgency: critical, high, medium, low
            payload: Additional data
            user: Target user (or all admins)
        """
        try:
            users = [user] if user else self.get_admin_users()

            for target_user in users:
                service = self.get_service(target_user)

                service.create_attention_item(
                    source_type=f'system_alert:{alert_type}',
                    source_agent='SystemIntelligenceAgent',
                    item_type='alert',
                    title=title,
                    summary=summary,
                    urgency=urgency,
                    payload=payload or {},
                )

        except Exception as e:
            logger.error(f"Failed to create system alert attention: {e}")

    # =========================================================================
    # DIAGNOSTIC ALERTS (Session 1093 — CTOAgent + future scheduled diagnostics)
    # =========================================================================

    def create_diagnostic_alert(
        self,
        diagnostic_type: str,
        source_agent: str,
        title: str,
        summary: str,
        urgency: str = 'medium',
        payload: dict = None,
        user=None,
    ):
        """
        Create attention item for scheduled diagnostic agents (CTOAgent
        daily reliability report, etc.). Distinct from create_system_alert
        because:
          - source_agent is honored (not hardcoded)
          - source_type is namespaced as `diagnostic:{diagnostic_type}`
          - JSON serialization runs through _serialize_for_json so payloads
            with datetime fields don't blow up at insert time

        Args:
            diagnostic_type: Diagnostic identifier (e.g., 'cto_daily_diagnostic')
            source_agent: The agent that produced the analysis (e.g., 'CTOAgent')
            title: Alert title (kept under 200 chars by caller)
            summary: Markdown body, 2-8 KB recommended
            urgency: critical, high, medium, low
            payload: Structured payload (will be JSON-serialized; datetimes OK)
            user: Target user; defaults to all staff/admin users
        """
        try:
            users = [user] if user else self.get_admin_users()
            safe_payload = _serialize_for_json(payload or {})

            for target_user in users:
                service = self.get_service(target_user)
                service.create_attention_item(
                    source_type=f'diagnostic:{diagnostic_type}',
                    source_agent=source_agent,
                    item_type='alert',
                    title=title,
                    summary=summary,
                    urgency=urgency,
                    payload=safe_payload,
                )
                logger.info(
                    f"Created diagnostic attention ({diagnostic_type}/{urgency}) "
                    f"for user {getattr(target_user, 'username', target_user)}"
                )

        except Exception as e:
            logger.error(f"Failed to create diagnostic attention: {e}")

    # =========================================================================
    # MYTHOLOGY ALERT BRIDGE (Session 1095 Tier 1b)
    # =========================================================================

    def create_mythology_alert(
        self,
        mythology_alert_id: str,
        alert_type: str,
        title: str,
        summary: str,
        urgency: str = 'high',
        payload: dict = None,
        user=None,
    ):
        """
        Surface a critical/high MythologyAlert into the operator governance
        inbox as a HumanAttentionItem. Session 1095 audit found 312 critical
        unacknowledged mythology alerts sitting silent because nobody was
        looking at /mythology-lab — this bridge connects them to the inbox
        operators already watch.

        Args:
            mythology_alert_id: UUID of the source MythologyAlert row
                (used as source_id so the operator can jump back).
            alert_type: MythologyAlert.alert_type (e.g. 'new_myth',
                'wide_propagation', 'cleanup_needed').
            title: Human-readable title.
            summary: Markdown body.
            urgency: critical | high | medium | low. Maps from
                MythologyAlert.severity directly.
            payload: Extra context (pattern types, event counts, etc.)
            user: Target user; defaults to all staff/admin users.

        item_type is fixed to `'mythology_alert'` so COO and the inbox UI
        can count these distinctly from generic alerts.
        """
        try:
            users = [user] if user else self.get_admin_users()
            safe_payload = _serialize_for_json(payload or {})

            for target_user in users:
                service = self.get_service(target_user)
                service.create_attention_item(
                    source_type=f'mythology:{alert_type}',
                    source_id=str(mythology_alert_id),
                    source_agent='MythologyDetectionService',
                    item_type='mythology_alert',
                    title=title[:200],
                    summary=summary[:8000],
                    urgency=urgency,
                    payload=safe_payload,
                )
                logger.info(
                    f"Created mythology attention ({alert_type}/{urgency}) "
                    f"for user {getattr(target_user, 'username', target_user)}"
                )
        except Exception as e:
            logger.error(f"Failed to create mythology attention: {e}")

    # =========================================================================
    # CONTENT REVIEW
    # =========================================================================

    def create_content_review_attention(
        self,
        content_type: str,
        title: str,
        summary: str,
        content_id: str,
        agent_name: str = 'ContentWriterAgent',
        quality_score: float = None,
        user=None
    ):
        """
        Create attention item for content needing review.

        Args:
            content_type: blog, social, email, etc.
            title: Content title
            summary: Brief description
            content_id: ID of the content
            agent_name: Agent that created it
            quality_score: Optional ML quality score (0-100)
            user: Target user
        """
        try:
            users = [user] if user else self.get_admin_users()

            # Determine urgency based on quality score
            if quality_score is not None:
                if quality_score < 60:
                    urgency = 'high'  # Low quality needs attention
                elif quality_score < 80:
                    urgency = 'medium'
                else:
                    urgency = 'low'  # High quality, just FYI
            else:
                urgency = 'medium'

            for target_user in users:
                service = self.get_service(target_user)

                summary_with_score = summary
                if quality_score is not None:
                    summary_with_score += f" Quality score: {quality_score}/100."

                service.create_attention_item(
                    source_type=f'content:{content_type}',
                    source_id=content_id,
                    source_agent=agent_name,
                    item_type='review',
                    title=f"Content Review: {title[:40]}",
                    summary=summary_with_score,
                    urgency=urgency,
                    payload={
                        'content_type': content_type,
                        'content_id': content_id,
                        'quality_score': quality_score,
                    },
                    ml_confidence=quality_score / 100 if quality_score else None,
                    ml_recommendation='approve' if quality_score and quality_score >= 80 else 'review',
                )

        except Exception as e:
            logger.error(f"Failed to create content review attention: {e}")

    # =========================================================================
    # AGENT OUTPUT - MISSION CONTROL
    # =========================================================================

    def create_agent_output_attention(
        self,
        agent_name: str,
        item_type: str,
        title: str,
        summary: str,
        urgency: str = 'medium',
        payload: dict = None,
        result_data: dict = None,
        user=None
    ):
        """
        Session 763: Create attention item from agent output for Mission Control.

        This is the generic factory for agent outputs. Called by BaseAgent's
        _maybe_create_attention_item() when an agent has actionable_config enabled.

        Args:
            agent_name: Name of the agent that produced the output
            item_type: Type of item (review, alert, opportunity, insight, approval)
            title: Human-readable title
            summary: Brief description of what needs attention
            urgency: critical, high, medium, low
            payload: Dict including available_actions for Mission Control buttons
            result_data: The agent's result.data for additional context
            user: Target user (or all admins if None)

        The payload should include:
            - available_actions: List of action dicts with {id, label, style, description}
            - Any agent-specific data for display
        """
        try:
            users = [user] if user else self.get_admin_users()

            # Merge result_data into payload for full context
            full_payload = payload or {}
            if result_data:
                full_payload['result_data'] = _serialize_for_json(result_data)

            # Ensure available_actions exists (even if empty)
            if 'available_actions' not in full_payload:
                full_payload['available_actions'] = []

            for target_user in users:
                service = self.get_service(target_user)

                service.create_attention_item(
                    source_type=f'agent_output:{agent_name.lower()}',
                    source_agent=agent_name,
                    item_type=item_type,
                    title=title,
                    summary=summary,
                    urgency=urgency,
                    payload=_serialize_for_json(full_payload),
                )
                logger.info(f"Created agent output attention from {agent_name} for user {target_user.username}")

        except Exception as e:
            logger.error(f"Failed to create agent output attention from {agent_name}: {e}")

    # =========================================================================
    # SPIDER DATA ALERTS
    # =========================================================================

    def create_spider_alert(
        self,
        spider_name: str,
        alert_type: str,
        title: str,
        summary: str,
        data: dict = None,
        urgency: str = 'medium',
        user=None
    ):
        """
        Create attention item for important spider data.

        Args:
            spider_name: Name of the spider
            alert_type: market_move, security, opportunity, etc.
            title: Alert title
            summary: Alert description
            data: Spider data payload
            urgency: Priority level
            user: Target user
        """
        try:
            users = [user] if user else self.get_admin_users()

            for target_user in users:
                service = self.get_service(target_user)

                service.create_attention_item(
                    source_type=f'spider:{spider_name}',
                    source_agent=f'{spider_name.title()}Spider',
                    item_type='insight',
                    title=title,
                    summary=summary,
                    urgency=urgency,
                    payload={
                        'spider_name': spider_name,
                        'alert_type': alert_type,
                        'data': data or {},
                    },
                )

        except Exception as e:
            logger.error(f"Failed to create spider alert attention: {e}")


# Singleton instance
attention_bridge = HumanAttentionBridge()


# =============================================================================
# DJANGO SIGNALS - Auto-create attention items from model changes
# =============================================================================

@receiver(post_save, sender='core.PilotReadinessGate')
def on_pilot_gate_change(sender, instance, created, **kwargs):
    """Auto-create attention when pilot gate status changes to pending_review."""
    if instance.status == 'pending_review':
        attention_bridge.create_pilot_gate_attention(instance)


@receiver(post_save, sender='core.AgentExecution')
def on_agent_execution_complete(sender, instance, created, **kwargs):
    """Auto-create attention for failed agent executions."""
    if not created and instance.status == 'failed':
        # Only for important/critical agents
        critical_agents = [
            'ThinkingAgent', 'ArbitrageDetector', 'PredictionMarketAnalyst',
            'BlockchainAuditCoordinator', 'StockAuditCoordinator',
        ]
        agent_name = (instance.template.name if hasattr(instance, 'template') and instance.template
                      else instance.agent.name if hasattr(instance, 'agent') and instance.agent
                      else '')
        if agent_name in critical_agents:
            attention_bridge.create_agent_execution_attention(instance)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_attention_for_user(user, **kwargs):
    """
    Convenience function to create an attention item for a specific user.

    Usage:
        create_attention_for_user(
            user=request.user,
            source_type='manual',
            item_type='task',
            title='Review this',
            summary='Something needs your attention',
            urgency='medium'
        )
    """
    from core.services.human_interface_service import get_human_interface_service
    service = get_human_interface_service(user)
    return service.create_attention_item(**kwargs)


def create_attention_for_admins(**kwargs):
    """
    Create attention item for all admin users.

    Usage:
        create_attention_for_admins(
            source_type='system',
            item_type='alert',
            title='System Notice',
            summary='Something important happened',
            urgency='high'
        )
    """
    results = []
    for user in User.objects.filter(is_staff=True, is_active=True):
        from core.services.human_interface_service import get_human_interface_service
        service = get_human_interface_service(user)
        result = service.create_attention_item(**kwargs)
        results.append(result)
    return results

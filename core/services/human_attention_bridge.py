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
    # SIGNAL PATTERN CRITICALITY  (Session 2734 — Capability Chain §6)
    # =========================================================================

    def create_signal_pattern_attention(self, cluster, user=None):
        """
        Create attention item for a high-strength ``SignalCluster``.

        Called by ``core/signals/signal_pattern_criticality_signals.py``
        when a newly-created cluster's ``strength`` crosses the
        configurable ``signal_pattern_criticality_threshold`` (default
        0.9). Extends the existing 5-category bridge with a sixth
        producer per Platform Capability Graph §6 wire-up.

        Args:
            cluster: ``SignalCluster`` instance with ``pattern_type``,
                ``strength``, ``name``, ``keywords``, etc.
            user: Optional target user; defaults to all admins.

        Chain:
            SignalCluster written by SignalAggregationService
            → post_save receiver checks strength >= threshold
            → transaction.on_commit → this method
            → HumanInterfaceService.create_attention_item()
            → HumanAttentionItem row
            → Frontend inbox / cockpit surface
        """
        try:
            users = [user] if user else self.get_admin_users()

            strength = float(getattr(cluster, 'strength', 0.0) or 0.0)
            pattern_type = getattr(cluster, 'pattern_type', 'unknown') or 'unknown'
            cluster_name = getattr(cluster, 'name', '') or 'Unnamed pattern'
            keywords = list(getattr(cluster, 'keywords', []) or [])[:5]
            source_breakdown = getattr(cluster, 'source_breakdown', {}) or {}

            urgency = 'critical' if strength >= 0.95 else 'high'
            pattern_label = pattern_type.replace('_', ' ').title()

            summary_parts = [
                f"{pattern_label} detected at strength {strength:.2f}"
            ]
            if keywords:
                summary_parts.append(f"Keywords: {', '.join(keywords)}")
            if source_breakdown:
                sources_summary = ', '.join(
                    f"{k}={v}" for k, v in list(source_breakdown.items())[:3]
                )
                summary_parts.append(f"Sources: {sources_summary}")
            summary = '. '.join(summary_parts) + '.'

            payload = _serialize_for_json({
                'cluster_id': str(getattr(cluster, 'id', '')),
                'pattern_type': pattern_type,
                'strength': strength,
                'urgency_score': float(getattr(cluster, 'urgency', 0.0) or 0.0),
                'confidence': float(getattr(cluster, 'confidence', 0.0) or 0.0),
                'novelty': float(getattr(cluster, 'novelty', 0.0) or 0.0),
                'name': cluster_name,
                'keywords': keywords,
                'source_breakdown': source_breakdown,
            })

            for target_user in users:
                service = self.get_service(target_user)
                service.create_attention_item(
                    source_type='signal_pattern',
                    source_id=str(getattr(cluster, 'id', '')),
                    source_agent='SignalAggregationService',
                    item_type='alert',
                    title=f"Signal: {cluster_name[:80]}",
                    summary=summary[:400],
                    urgency=urgency,
                    payload=payload,
                )
                logger.info(
                    "[HAI_BRIDGE] signal_pattern attention created "
                    "user=%s cluster_id=%s strength=%.3f urgency=%s",
                    target_user.username, cluster.id, strength, urgency,
                )

        except Exception as e:
            logger.error(f"Failed to create signal pattern attention: {e}")

    # =========================================================================
    # MISSION VERDICT ATTENTION  (Session 2734 — Capability Chain §1 closure)
    # =========================================================================

    def create_mission_verdict_attention(self, run, verdict: str, user=None):
        """
        Create attention item when a MissionRunner emits a non-certified
        verdict — Category B closure of §1 Item 9 HAI production.

        Called by ``core/signals/mission_verdict_attention_signals.py``
        with the parent ``OpsRun`` (mission-domain) and the raw verdict
        string ('rejected' | 'deferred').

        Urgency policy (per Rigby SIGN pa-47bd5d75158948f5 refinement):
          * ``rejected`` → ``urgency='high'`` — inbox visibility only.
            Explicitly NOT ``critical`` because critical would trigger
            Expo push via ``signals_push_notifications.on_critical_
            attention_item`` and risks double-alerting when another
            escalation (agent execution failure / body-system critical)
            already fired for the same underlying incident.
          * ``deferred`` → ``urgency='medium'`` — action-worthy but not
            page-worthy. Rigby couldn't decide; a human should look
            same-day but not immediately.
          * ``certified`` NEVER reaches this method — filtered upstream
            in the signal receiver.

        Args:
            run: Parent ``OpsRun`` with ``domain='mission'``.
            verdict: ``'rejected'`` or ``'deferred'``.
            user: Optional target user; defaults to admins.
        """
        try:
            users = [user] if user else self.get_admin_users()

            verdict_lc = (verdict or '').lower()
            urgency = 'high' if verdict_lc == 'rejected' else 'medium'

            title_verb = 'rejected' if verdict_lc == 'rejected' else 'deferred'
            title = f"Mission {title_verb}: {getattr(run, 'title', '')[:60]}"

            summary = (
                f"MissionRunner emitted verdict '{verdict_lc}' on mission "
                f"{getattr(run, 'mission_id', None)} "
                f"(run_kind='{getattr(run, 'run_kind', '') or 'unknown'}'). "
                f"Review the run's OpsRunEvent timeline for rationale."
            )

            payload = _serialize_for_json({
                'run_id': str(getattr(run, 'id', '')),
                'mission_id': (
                    str(getattr(run, 'mission_id', None))
                    if getattr(run, 'mission_id', None) else None
                ),
                'verdict': verdict_lc,
                'run_kind': getattr(run, 'run_kind', '') or '',
                'run_type': getattr(run, 'run_type', '') or '',
                'title': getattr(run, 'title', ''),
                'summary_snapshot': getattr(run, 'summary', {}) or {},
                'started_at': getattr(run, 'started_at', None),
                'finished_at': getattr(run, 'finished_at', None),
            })

            for target_user in users:
                service = self.get_service(target_user)
                service.create_attention_item(
                    source_type='mission_verdict',
                    source_id=str(getattr(run, 'id', '')),
                    source_agent='MissionRunner',
                    item_type='review',
                    title=title[:120],
                    summary=summary[:400],
                    urgency=urgency,
                    payload=payload,
                )
                logger.info(
                    "[HAI_BRIDGE] mission_verdict attention created "
                    "user=%s run_id=%s verdict=%s urgency=%s",
                    target_user.username, run.id, verdict_lc, urgency,
                )

        except Exception as e:
            logger.error(f"Failed to create mission verdict attention: {e}")

    # =========================================================================
    # BODY-SYSTEM DEGRADATION  (Session 2734 — Capability Chain §14)
    # =========================================================================

    def create_body_system_degradation_attention(self, heartbeat, user=None):
        """
        Create attention item when a ``HeartBeat`` records
        ``overall_status`` of ``critical`` or ``offline``.

        Called by
        ``core/signals/body_system_degradation_signals.py`` after the
        signal-side dedup gate (no existing open HAI in the last hour).
        Seventh producer category on this bridge per Platform
        Capability Graph §14 wire-up.

        Args:
            heartbeat: ``HeartBeat`` instance with ``overall_status``,
                ``health_score``, ``components``, etc.
            user: Optional target user; defaults to all admins.

        Chain:
            BodyCoordinator every-10-min scan
            → HeartBeat.save(overall_status='critical'|'offline')
            → post_save receiver (dedup + kill switch guard)
            → transaction.on_commit
            → this method
            → HumanInterfaceService.create_attention_item()
            → HumanAttentionItem row
        """
        try:
            users = [user] if user else self.get_admin_users()

            overall_status = getattr(heartbeat, 'overall_status', 'unknown') or 'unknown'
            health_score = float(getattr(heartbeat, 'health_score', 0.0) or 0.0)
            components_checked = int(getattr(heartbeat, 'components_checked', 0) or 0)
            components_healthy = int(getattr(heartbeat, 'components_healthy', 0) or 0)
            is_alive = bool(getattr(heartbeat, 'is_alive', False))
            components = getattr(heartbeat, 'components', {}) or {}

            # 'critical' is the wake-someone-up state; 'offline' means the
            # coordinator itself flagged the system as unreachable — same
            # urgency for the human inbox.
            urgency = 'critical'
            components_degraded = max(components_checked - components_healthy, 0)

            summary = (
                f"Platform health {overall_status} — "
                f"score {health_score:.1f}/100, "
                f"{components_degraded} of {components_checked} components unhealthy"
                + ('' if is_alive else ' (is_alive=False)')
                + '.'
            )

            payload = _serialize_for_json({
                'heartbeat_id': str(getattr(heartbeat, 'id', '')),
                'overall_status': overall_status,
                'health_score': health_score,
                'is_alive': is_alive,
                'components_checked': components_checked,
                'components_healthy': components_healthy,
                'components_degraded': components_degraded,
                'components': components,
                'recorded_at': getattr(heartbeat, 'recorded_at', None),
            })

            for target_user in users:
                service = self.get_service(target_user)
                service.create_attention_item(
                    source_type='body_system_degradation',
                    source_id=str(getattr(heartbeat, 'id', '')),
                    source_agent='BodyCoordinator',
                    item_type='alert',
                    title=f"Platform health {overall_status}: score {health_score:.0f}/100",
                    summary=summary[:400],
                    urgency=urgency,
                    payload=payload,
                )
                logger.info(
                    "[HAI_BRIDGE] body_system_degradation attention created "
                    "user=%s heartbeat_id=%s status=%s score=%.1f",
                    target_user.username, heartbeat.id, overall_status,
                    health_score,
                )

        except Exception as e:
            logger.error(f"Failed to create body system degradation attention: {e}")

    # =========================================================================
    # WORKER FAILURE CLUSTER  (Session 2734 — Capability Chain §15 closure)
    # =========================================================================

    def create_failure_cluster_attention(self, snapshot, user=None):
        """
        Create an attention item when a ``FailureClusterSnapshot`` breaches
        the configured threshold — Category B closure of §15 Item 14.

        Called by ``core/signals/failure_cluster_signals.py`` after the
        ``CeleryTaskEvent.status='FAILURE'`` post_save receiver computes
        the sliding-window cluster and confirms the dedup gate (no open
        ``failure_cluster`` HAI for the same ``(task_name, urgency_band)``
        in the last 30 minutes).

        Urgency policy (per Rigby SIGN ``pa-74ecac300bba4ab3`` Q3
        refinement — dedup on ``(task_name, urgency_band)`` allows a
        previously-``high`` cluster to re-escalate to ``critical`` when
        the count crosses the critical threshold within the dedup
        window):

          * ``urgency_band='high'`` — 5+ distinct task_ids failed in the
            5-minute window. Inbox visibility only. Does NOT trigger
            Expo push.
          * ``urgency_band='critical'`` — 15+ distinct task_ids failed.
            Worker-storm territory. Triggers Expo push via
            ``signals_push_notifications.on_critical_attention_item``.

        Args:
            snapshot: ``FailureClusterSnapshot`` from
                ``core.services.failure_cluster_aggregator.compute_cluster``.
                Must have ``exceeds_threshold=True``.
            user: Optional target user; defaults to admins.
        """
        try:
            users = [user] if user else self.get_admin_users()

            task_name = getattr(snapshot, 'task_name', '') or 'unknown'
            distinct_count = int(getattr(snapshot, 'distinct_task_id_count', 0) or 0)
            total_count = int(getattr(snapshot, 'total_event_count', 0) or 0)
            urgency_band = getattr(snapshot, 'urgency_band', 'high') or 'high'
            urgency = 'critical' if urgency_band == 'critical' else 'high'
            window_minutes = int(getattr(snapshot, 'window_minutes', 5) or 5)
            # Per Rigby SIGN pa-74ecac300bba4ab3 post-implementation Q3
            # refinement: truncate long-tail lists to top-5 samples +
            # keep total counts so the inbox payload does not bloat when
            # a storm hits many workers/queues/error types at once.
            _PAYLOAD_SAMPLE_MAX = 5
            all_queues = list(getattr(snapshot, 'distinct_queues', ()) or ())
            all_workers = list(getattr(snapshot, 'distinct_workers', ()) or ())
            all_error_types = list(
                getattr(snapshot, 'distinct_error_types', ()) or ()
            )
            distinct_queues = all_queues[:_PAYLOAD_SAMPLE_MAX]
            distinct_workers = all_workers[:_PAYLOAD_SAMPLE_MAX]
            distinct_error_types = all_error_types[:_PAYLOAD_SAMPLE_MAX]
            top_error_signature = getattr(snapshot, 'top_error_signature', '') or ''
            sample_task_ids = list(
                getattr(snapshot, 'sample_task_ids', ()) or ()
            )[:_PAYLOAD_SAMPLE_MAX]
            idempotency_key = getattr(snapshot, 'idempotency_key', '') or ''

            title = (
                f"Worker failure cluster: {task_name[:60]} — "
                f"{distinct_count} failures in {window_minutes}m"
            )

            summary_parts = [
                f"{distinct_count} distinct Celery tasks failed in the last "
                f"{window_minutes} minute(s) for task '{task_name}'."
            ]
            if top_error_signature:
                summary_parts.append(f"Top error: {top_error_signature}.")
            if distinct_queues:
                summary_parts.append(
                    f"Queues: {', '.join(distinct_queues[:3])}."
                )
            if distinct_workers:
                summary_parts.append(
                    f"Workers: {', '.join(distinct_workers[:3])}."
                )
            summary = ' '.join(summary_parts)

            payload = _serialize_for_json({
                'task_name': task_name,
                'window_minutes': window_minutes,
                'window_start': getattr(snapshot, 'window_start', None),
                'window_end': getattr(snapshot, 'window_end', None),
                'distinct_task_id_count': distinct_count,
                'total_event_count': total_count,
                'distinct_queues': distinct_queues,
                'distinct_queues_total': len(all_queues),
                'distinct_workers': distinct_workers,
                'distinct_workers_total': len(all_workers),
                'distinct_error_types': distinct_error_types,
                'distinct_error_types_total': len(all_error_types),
                'top_error_signature': top_error_signature,
                'sample_task_ids': sample_task_ids,
                'earliest_finished_at': getattr(
                    snapshot, 'earliest_finished_at', None,
                ),
                'latest_finished_at': getattr(
                    snapshot, 'latest_finished_at', None,
                ),
                'threshold': int(getattr(snapshot, 'threshold', 5) or 5),
                'critical_threshold': int(
                    getattr(snapshot, 'critical_threshold', 15) or 15
                ),
                'urgency_band': urgency_band,
                'idempotency_key': idempotency_key,
            })

            for target_user in users:
                service = self.get_service(target_user)
                service.create_attention_item(
                    source_type='failure_cluster',
                    source_id=idempotency_key or f'failure_cluster:{task_name}',
                    source_agent='CeleryTelemetry',
                    item_type='alert',
                    title=title[:200],
                    summary=summary[:400],
                    urgency=urgency,
                    payload=payload,
                )
                logger.info(
                    "[HAI_BRIDGE] failure_cluster attention created "
                    "user=%s task_name=%s distinct=%d band=%s idempotency=%s",
                    target_user.username, task_name, distinct_count,
                    urgency_band, idempotency_key,
                )

        except Exception as e:
            logger.error(f"Failed to create failure cluster attention: {e}")

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

"""
Signal-triggered agent dispatch service — Session 2933 A3 v1.

Path B (Rigby zoom-out ratified S2933): mapping table lives in Python
code below (``SIGNAL_DISPATCH_RULES``). The only DB row is
``core.models_signal_dispatch.SignalDispatch`` — audit only. No admin
editing surface in v1.

Flow:
    beat_schedule 'scan-signal-dispatch-rules' (every 5 min)
        → tasks.scan_signal_dispatch_rules
        → SignalDispatchService.scan_and_dispatch()
        → for each rule × eligible cluster: create SignalDispatch(outcome='queued')
                                             + enqueue dispatch_agent_for_signal_cluster.delay
        → dispatch_agent_for_signal_cluster (per-cluster Celery task)
        → SignalDispatchService.execute_dispatch(dispatch_id)
        → AgentRouter.route(agent_name=rule.agent_name, ...)
        → SignalDispatch.outcome = succeeded|failed  + agent_execution_id

Safety net (Rigby SIGN Q6):
    * Global ``MAX_DISPATCHES_PER_SCAN`` cap (settings-overridable)
    * Per-rule ``max_per_day`` cap enforced by SignalDispatch count over 24h
    * Per (cluster, rule_key) dedup — a succeeded/in-flight dispatch blocks
      re-fire; a prior 'failed' does NOT block, so manual/scan retry works
    * Rules gate on ``SignalCluster.is_actionable`` (status='active' AND
      strength >= 0.5 AND confidence >= 0.5) + rule's own min_strength /
      min_confidence floors

Kill switch: ``settings.SIGNAL_DISPATCH_ENABLED`` (default True).
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, Optional

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─── Rule definitions (v1 — 2 pairs, hard-coded) ─────────────────────────

@dataclass(frozen=True)
class SignalDispatchRuleDef:
    """Static rule mapping a SignalCluster pattern_type to an AGENT_MAP agent."""
    key: str
    pattern_type: str
    agent_name: str
    min_strength: float = 0.5
    min_confidence: float = 0.5
    max_per_day: int = 10


SIGNAL_DISPATCH_RULES: tuple[SignalDispatchRuleDef, ...] = (
    # v1 pair (a): validated by Rigby (agent_introspection_tool) — TrendAnalysisAgent
    # 110 executions / 100% 7d success / specialized for spider-intelligence trend briefs.
    SignalDispatchRuleDef(
        key='trend_emergence__trend_analysis',
        pattern_type='trend_emergence',
        agent_name='TrendAnalysisAgent',
        min_strength=0.5,
        min_confidence=0.5,
        max_per_day=10,
    ),
    # v1 pair (b): ContentStrategyAgent (post-S2932 fail-loud gate).
    SignalDispatchRuleDef(
        key='content_gap__content_strategy',
        pattern_type='content_gap',
        agent_name='ContentStrategyAgent',
        min_strength=0.5,
        min_confidence=0.5,
        max_per_day=10,
    ),
    # S2934 A5: OpportunityScoringAgent. Verified at S2934 open via
    # agent_introspection_tool — 33 total executions, effectiveness 96,
    # recent 7d 2/2 100% success. Cluster volume verified via ORM —
    # 117 opportunity_window clusters exist (1 currently active, others
    # rotate through detecting/decayed/archived).
    SignalDispatchRuleDef(
        key='opportunity_window__opportunity_scoring',
        pattern_type='opportunity_window',
        agent_name='OpportunityScoringAgent',
        min_strength=0.5,
        min_confidence=0.5,
        max_per_day=10,
    ),
)


DEFAULT_MAX_DISPATCHES_PER_SCAN = 10


def _rules_by_key() -> dict[str, SignalDispatchRuleDef]:
    return {r.key: r for r in SIGNAL_DISPATCH_RULES}


def get_rule(rule_key: str) -> Optional[SignalDispatchRuleDef]:
    return _rules_by_key().get(rule_key)


# ─── Service ─────────────────────────────────────────────────────────────


class SignalDispatchService:
    """v1 scanner + dispatcher for signal-triggered agent runs."""

    def __init__(self, rules: Optional[Iterable[SignalDispatchRuleDef]] = None):
        self.rules = tuple(rules) if rules is not None else SIGNAL_DISPATCH_RULES

    # ── Scanner (called by the periodic Celery task) ────────────────────

    def scan_and_dispatch(self, scan_run_id: Optional[str] = None) -> dict:
        """Scan all rules × eligible clusters, enqueue dispatches. Idempotent.

        Returns a summary dict for logging + test assertions.
        """
        if not getattr(settings, 'SIGNAL_DISPATCH_ENABLED', True):
            logger.info("[SIGNAL_DISPATCH] disabled via SIGNAL_DISPATCH_ENABLED=False")
            return {'enqueued': 0, 'skipped': 0, 'disabled': True, 'per_rule': {}}

        run_id = scan_run_id or uuid.uuid4().hex[:16]
        global_cap = int(getattr(
            settings, 'SIGNAL_DISPATCH_MAX_PER_SCAN', DEFAULT_MAX_DISPATCHES_PER_SCAN,
        ))
        enqueued = 0
        per_rule: dict[str, int] = {}
        skipped_cap = 0

        for rule in self.rules:
            per_rule.setdefault(rule.key, 0)
            if enqueued >= global_cap:
                skipped_cap += 1
                logger.info(
                    "[SIGNAL_DISPATCH] global cap %d reached, halting scan run_id=%s",
                    global_cap, run_id,
                )
                break

            eligible = self._eligible_clusters_for_rule(rule)
            for cluster in eligible:
                if enqueued >= global_cap:
                    skipped_cap += 1
                    break
                if self._rule_daily_cap_reached(rule):
                    logger.info(
                        "[SIGNAL_DISPATCH] rule %s reached max_per_day=%d",
                        rule.key, rule.max_per_day,
                    )
                    break

                dispatch = self._create_queued_dispatch(rule, cluster, run_id)
                if dispatch is None:
                    continue  # dedup — already queued/succeeded for this pair

                self._enqueue(dispatch.id)
                enqueued += 1
                per_rule[rule.key] += 1

        logger.info(
            "[SIGNAL_DISPATCH] scan complete run_id=%s enqueued=%d skipped_cap=%d per_rule=%s",
            run_id, enqueued, skipped_cap, per_rule,
        )
        return {
            'run_id': run_id,
            'enqueued': enqueued,
            'skipped_cap': skipped_cap,
            'per_rule': per_rule,
            'disabled': False,
        }

    def _eligible_clusters_for_rule(self, rule: SignalDispatchRuleDef):
        from core.models_signal_intelligence import SignalCluster
        from core.models_signal_dispatch import SignalDispatch

        already = set(
            SignalDispatch.objects
            .filter(rule_key=rule.key)
            .exclude(outcome='failed')
            .values_list('signal_cluster_id', flat=True)
        )
        qs = (
            SignalCluster.objects.filter(
                pattern_type=rule.pattern_type,
                status='active',
                strength__gte=rule.min_strength,
                confidence__gte=rule.min_confidence,
            )
            .exclude(id__in=already)
            .order_by('-strength', '-detected_at')
        )
        return list(qs)

    def _rule_daily_cap_reached(self, rule: SignalDispatchRuleDef) -> bool:
        from core.models_signal_dispatch import SignalDispatch
        since = timezone.now() - timedelta(hours=24)
        count = SignalDispatch.objects.filter(
            rule_key=rule.key,
            dispatched_at__gte=since,
        ).exclude(outcome__in=('rejected_agent_missing', 'rejected_unknown_rule')).count()
        return count >= rule.max_per_day

    def _create_queued_dispatch(self, rule, cluster, run_id):
        from core.models_signal_dispatch import SignalDispatch
        exists = SignalDispatch.objects.filter(
            signal_cluster=cluster,
            rule_key=rule.key,
        ).exclude(outcome='failed').exists()
        if exists:
            return None
        return SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='queued',
            input_payload=self._build_payload(rule, cluster),
            scan_run_id=run_id,
        )

    def _enqueue(self, dispatch_id):
        from core.tasks import dispatch_agent_for_signal_cluster
        dispatch_agent_for_signal_cluster.delay(str(dispatch_id))

    def _build_payload(self, rule, cluster) -> dict:
        return {
            'dispatch_source': 'signal_dispatch_v1',
            'rule_key': rule.key,
            'pattern_type': cluster.pattern_type,
            'cluster_id': str(cluster.id),
            'cluster_name': cluster.name,
            'strength': float(cluster.strength or 0.0),
            'confidence': float(cluster.confidence or 0.0),
            'keywords': list(cluster.keywords or []),
            'detected_at': cluster.detected_at.isoformat() if cluster.detected_at else None,
        }

    # ── Per-dispatch executor (called by the fan-out Celery task) ──────

    def execute_dispatch(self, dispatch_id: str) -> dict:
        """Run the agent for a queued SignalDispatch. Idempotent on re-run."""
        from core.models_signal_dispatch import SignalDispatch
        from core.agent_router import AgentRouter, AgentNotFoundError

        dispatch = SignalDispatch.objects.select_related('signal_cluster').get(id=dispatch_id)

        rule = get_rule(dispatch.rule_key)
        if rule is None:
            self._finalize(dispatch, 'rejected_unknown_rule', error=f"rule_key '{dispatch.rule_key}' not registered")
            return {'outcome': 'rejected_unknown_rule', 'dispatch_id': dispatch_id}

        router = AgentRouter()
        if rule.agent_name not in router.AGENT_MAP:
            self._finalize(dispatch, 'rejected_agent_missing', error=f"agent '{rule.agent_name}' not in AGENT_MAP")
            return {'outcome': 'rejected_agent_missing', 'dispatch_id': dispatch_id}

        cluster = dispatch.signal_cluster
        task_str = self._build_task_string(rule, cluster)
        context = {**dispatch.input_payload}

        try:
            result = router.route(
                agent_name=rule.agent_name,
                task=task_str,
                context=context,
                trigger_source='signal_dispatch_v1',
            )
        except AgentNotFoundError as e:
            self._finalize(dispatch, 'rejected_agent_missing', error=str(e))
            return {'outcome': 'rejected_agent_missing', 'dispatch_id': dispatch_id}
        except Exception as e:
            self._finalize(dispatch, 'failed', error=f"{type(e).__name__}: {e}")
            return {'outcome': 'failed', 'dispatch_id': dispatch_id, 'error': str(e)}

        exec_id = getattr(result, 'execution_id', None)
        if result and result.success:
            self._finalize(dispatch, 'succeeded', agent_execution_id=exec_id)
            return {'outcome': 'succeeded', 'dispatch_id': dispatch_id, 'execution_id': exec_id}

        err = (result.error or result.message or 'agent returned success=False') if result else 'router returned no result'
        self._finalize(dispatch, 'failed', error=err[:2000], agent_execution_id=exec_id)
        return {'outcome': 'failed', 'dispatch_id': dispatch_id, 'error': err}

    def _finalize(self, dispatch, outcome, error='', agent_execution_id=None):
        dispatch.outcome = outcome
        dispatch.error_summary = error or ''
        if agent_execution_id:
            try:
                dispatch.agent_execution_id = uuid.UUID(str(agent_execution_id))
            except (ValueError, TypeError):
                pass
        dispatch.completed_at = timezone.now()
        dispatch.save(update_fields=['outcome', 'error_summary', 'agent_execution_id', 'completed_at'])

    def _build_task_string(self, rule, cluster) -> str:
        kw = ', '.join((cluster.keywords or [])[:8]) or '(no keywords)'
        return (
            f"[signal_dispatch_v1] SignalCluster '{cluster.name}' "
            f"(pattern={cluster.pattern_type}, strength={cluster.strength:.2f}, "
            f"confidence={cluster.confidence:.2f}) crossed rule '{rule.key}'. "
            f"Keywords: {kw}. Produce your normal output for this input."
        )

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
    # S2949 A9: MarketMovementMonitorAgent. Verified at S2949 open via
    # agent_introspection_tool — 22 total executions, effectiveness 84,
    # semantic isomorph to "demand spike" (momentum/velocity framing).
    # Cluster volume verified via ORM — 251 demand_spike clusters exist
    # (0 currently active, 9 detecting, 187 decayed, 55 archived —
    # ~2× volume vs skill_demand=133; skill_demand queued for A10).
    SignalDispatchRuleDef(
        key='demand_spike__market_movement_monitor',
        pattern_type='demand_spike',
        agent_name='MarketMovementMonitorAgent',
        min_strength=0.5,
        min_confidence=0.5,
        max_per_day=10,
    ),
)


DEFAULT_MAX_DISPATCHES_PER_SCAN = 10
MANUAL_SCAN_RUN_ID = 'manual'
DEFAULT_MANUAL_GUARD_WINDOW_MINUTES = 5


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
        # S2949 A9: per-rule diagnostics for starvation-by-ordering visibility.
        # Rigby zoom-out fold (S2949) flagged 4-rule fan-out risk under a
        # shared global cap; these counters make starvation observable
        # without changing the drain-in-order semantics.
        per_rule_diagnostics: dict[str, dict[str, int]] = {}
        skipped_cap = 0

        for rule in self.rules:
            per_rule.setdefault(rule.key, 0)
            per_rule_diagnostics.setdefault(rule.key, {
                'eligible_count': 0,
                'blocked_by_cap': 0,
                'blocked_by_dedupe': 0,
                'blocked_by_daily_cap': 0,
            })
            if enqueued >= global_cap:
                skipped_cap += 1
                logger.info(
                    "[SIGNAL_DISPATCH] global cap %d reached, halting scan run_id=%s",
                    global_cap, run_id,
                )
                break

            eligible, dedupe_excluded = self._eligible_clusters_for_rule(rule)
            per_rule_diagnostics[rule.key]['eligible_count'] = len(eligible)
            per_rule_diagnostics[rule.key]['blocked_by_dedupe'] = dedupe_excluded
            for cluster in eligible:
                if enqueued >= global_cap:
                    skipped_cap += 1
                    per_rule_diagnostics[rule.key]['blocked_by_cap'] += 1
                    break
                if self._rule_daily_cap_reached(rule):
                    per_rule_diagnostics[rule.key]['blocked_by_daily_cap'] += 1
                    logger.info(
                        "[SIGNAL_DISPATCH] rule %s reached max_per_day=%d",
                        rule.key, rule.max_per_day,
                    )
                    break

                dispatch = self._create_queued_dispatch(rule, cluster, run_id)
                if dispatch is None:
                    # Race-condition belt-and-suspenders: eligibility query
                    # already excluded dedupes, so this only fires if a
                    # concurrent scan created the dispatch between filter
                    # and create. Tracked in blocked_by_dedupe alongside
                    # the query-level count.
                    per_rule_diagnostics[rule.key]['blocked_by_dedupe'] += 1
                    continue

                self._enqueue(dispatch.id)
                enqueued += 1
                per_rule[rule.key] += 1

        logger.info(
            "[SIGNAL_DISPATCH] scan complete run_id=%s enqueued=%d skipped_cap=%d "
            "per_rule=%s per_rule_diagnostics=%s",
            run_id, enqueued, skipped_cap, per_rule, per_rule_diagnostics,
        )
        return {
            'run_id': run_id,
            'enqueued': enqueued,
            'skipped_cap': skipped_cap,
            'per_rule': per_rule,
            'per_rule_diagnostics': per_rule_diagnostics,
            'disabled': False,
        }

    def _eligible_clusters_for_rule(
        self,
        rule: SignalDispatchRuleDef,
    ) -> tuple[list, int]:
        """Return ``(clusters, dedupe_excluded_count)`` for a rule.

        S2949 A9: returns dedupe count as a diagnostic — how many
        pattern-matching clusters were dropped by rule-key dedupe
        (already have a non-failed dispatch for this rule).
        """
        from core.models_signal_intelligence import SignalCluster
        from core.models_signal_dispatch import SignalDispatch

        already = set(
            SignalDispatch.objects
            .filter(rule_key=rule.key)
            .exclude(outcome='failed')
            .values_list('signal_cluster_id', flat=True)
        )
        base = SignalCluster.objects.filter(
            pattern_type=rule.pattern_type,
            status='active',
            strength__gte=rule.min_strength,
            confidence__gte=rule.min_confidence,
        )
        clusters = list(
            base.exclude(id__in=already).order_by('-strength', '-detected_at')
        )
        dedupe_excluded = base.filter(id__in=already).count()
        return clusters, dedupe_excluded

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

    # ── On-demand manual dispatch (S2947 A8) ───────────────────────────

    def create_manual_dispatch(
        self,
        cluster_id: str,
        rule_key: Optional[str] = None,
        force: bool = False,
        guard_window_minutes: int = DEFAULT_MANUAL_GUARD_WINDOW_MINUTES,
        sync: bool = False,
    ) -> dict:
        """Create a manually-triggered SignalDispatch for a specific cluster.

        Shared logic between the ``dispatch_signal`` mgmt command and the
        ``POST /api/v1/agents/signal-dispatches/manual/`` endpoint.

        Returns a dict shape usable by both callers:
            success: {'success': True, 'dispatch_id', 'cluster_id',
                      'cluster_name', 'rule_key', 'agent_name',
                      'sync_result'?}
            error:   {'success': False, 'error_code', 'error',
                      'existing_dispatch_id'?}

        Error codes:
            cluster_not_found | unknown_rule_key | rule_pattern_mismatch |
            no_matching_rule | multiple_matching_rules | guard_blocked
        """
        from core.models_signal_dispatch import SignalDispatch
        from core.models_signal_intelligence import SignalCluster

        try:
            cluster = SignalCluster.objects.get(id=cluster_id)
        except SignalCluster.DoesNotExist:
            return {
                'success': False,
                'error_code': 'cluster_not_found',
                'error': f"SignalCluster {cluster_id} not found",
            }

        if rule_key:
            rule = get_rule(rule_key)
            if rule is None:
                return {
                    'success': False,
                    'error_code': 'unknown_rule_key',
                    'error': f"Rule '{rule_key}' not in SIGNAL_DISPATCH_RULES",
                }
            if rule.pattern_type != cluster.pattern_type:
                return {
                    'success': False,
                    'error_code': 'rule_pattern_mismatch',
                    'error': (
                        f"Rule '{rule_key}' targets pattern_type='{rule.pattern_type}' "
                        f"but cluster has pattern_type='{cluster.pattern_type}'"
                    ),
                }
        else:
            matches = [r for r in self.rules if r.pattern_type == cluster.pattern_type]
            if not matches:
                return {
                    'success': False,
                    'error_code': 'no_matching_rule',
                    'error': (
                        f"No rule in SIGNAL_DISPATCH_RULES matches pattern_type="
                        f"'{cluster.pattern_type}'. Pass rule_key explicitly or add a rule."
                    ),
                }
            if len(matches) > 1:
                keys = ', '.join(r.key for r in matches)
                return {
                    'success': False,
                    'error_code': 'multiple_matching_rules',
                    'error': (
                        f"Multiple rules match pattern_type='{cluster.pattern_type}': "
                        f"{keys}. Pass rule_key explicitly."
                    ),
                }
            rule = matches[0]

        if not force:
            since = timezone.now() - timedelta(minutes=guard_window_minutes)
            blocker = SignalDispatch.objects.filter(
                signal_cluster=cluster,
                rule_key=rule.key,
                dispatched_at__gte=since,
            ).exclude(outcome='failed').first()
            if blocker is not None:
                return {
                    'success': False,
                    'error_code': 'guard_blocked',
                    'error': (
                        f"Idempotent guard: dispatch {blocker.id} for "
                        f"(cluster={cluster_id}, rule={rule.key}) exists within "
                        f"{guard_window_minutes}min window (outcome={blocker.outcome})."
                    ),
                    'existing_dispatch_id': str(blocker.id),
                }

        new_dispatch = SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='queued',
            input_payload=self._build_payload(rule, cluster),
            scan_run_id=MANUAL_SCAN_RUN_ID,
        )

        result = {
            'success': True,
            'dispatch_id': str(new_dispatch.id),
            'cluster_id': str(cluster.id),
            'cluster_name': cluster.name,
            'rule_key': rule.key,
            'agent_name': rule.agent_name,
        }

        if sync:
            result['sync_result'] = self.execute_dispatch(str(new_dispatch.id))
        else:
            from core.tasks import dispatch_agent_for_signal_cluster
            dispatch_agent_for_signal_cluster.delay(str(new_dispatch.id))

        return result

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

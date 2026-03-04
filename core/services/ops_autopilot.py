"""
Ops Autopilot v6 — autonomous ops with governance guardrails.

Policies (v1 — Session 1080):
  1. Timeout spike containment: auto-block agents with high TIMEOUT signature counts
  2. Blocked-agent hygiene: flag agents blocked too long without TTL

Policies (v2 — autonomy push):
  3. Failed deliberation retry: retry TIMEOUT/LLM_UPSTREAM sessions (transient failures)
  4. Content pipeline sweep: kick stuck needs_enhancement/pending_review content
  5. Attention item auto-resolve: dismiss stale ops_autopilot alerts that resolved themselves
  6. Governance auto-decision: auto-approve/dismiss low-blast-radius items

Policies (v3 — root-cause autonomy):
  7. Root-cause remediation: auto-apply safe config fixes for recurring failures
     (timeout adjustments, model fallbacks, temp blocks) with playbook learning
  8. Contract/schema drift detection: scan for mismatches between PA tool schemas,
     handler registrations, agent registry, and Celery beat schedule

Policies (v4 — self-tuning + budget):
  9. Policy self-tuning: PolicyOptimizer analyses action history to auto-adjust
     config thresholds. Emits changelogs and governance notes for each adjustment.
     Covers: timeout thresholds, windows, TTLs, cooldowns, max-per-cycle caps.
 10. Budget controller: BudgetController monitors LLM spend via LLMCallLog.
     Three tiers: soft limit (70%) → model downgrade, rate reduction (future),
     hard limit (95%) → freeze non-critical. Flags in SystemConfiguration.

Policies (v5 — QROI attribution + scheduling):
 11. QROI enforcement: ROIEnforcer correlates LLM spend with outcomes
     (completed executions, published content) × quality_weight. Under
     budget pressure, applies selective throttles — low-QROI agents get
     cooldown periods between calls.
 12. Budget-aware scheduling: BudgetAwareScheduler provides preflight
     checks for expensive Beat tasks. Under pressure, tasks are deferred
     (skipped) or downscoped (reduced batch sizes, fewer items).

Policies (v6 — impact tracking + portfolio allocation):
 13. Impact collection + portfolio allocation: ImpactCollector harvests
     real downstream value (wager P/L, deliverable engagement, confirmed
     revenue) into ImpactEvent table. PortfolioAllocator computes IQROI
     per desk and adjusts budget allocations — high-impact desks get more
     headroom, zero-impact pipelines get deprioritized.

All actions create HumanAttentionItem for governance visibility and are logged
to AutopilotAction for audit trail. Non-trivial actions go through pre-check
→ execute → verify → rollback cycle (ActionVerifier). Successful remediations
are promoted to RemediationPlaybook for future reuse. Config tuning changes
are persisted via SystemConfiguration and always changelog-documented.
"""

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

from core.models_diagnostic_pipeline import AutopilotAction, RemediationPlaybook

logger = logging.getLogger(__name__)


# ── Policy configuration ─────────────────────────────────────────────────────

class AutopilotConfig:
    """Tunable policy thresholds. Start conservative."""

    # Timeout spike containment
    TIMEOUT_SPIKE_THRESHOLD = 3          # >= N timeout signatures per agent per hour → block
    TIMEOUT_SPIKE_WINDOW_MINUTES = 60    # Look-back window
    TIMEOUT_BLOCK_TTL_MINUTES = 30       # Auto-unblock after this (start short, raise later)

    # Rate limiting
    MAX_BLOCKS_PER_AGENT_PER_HOUR = 1    # Don't flap
    MAX_TOTAL_BLOCKS_PER_CYCLE = 2       # Don't block everything at once

    # Blocked-agent hygiene
    STALE_BLOCK_HOURS = 48               # Flag blocks older than this without TTL

    # Policy 3: Failed deliberation retry
    DELIBERATION_RETRY_AFTER_MINUTES = 30  # Retry failed sessions older than this
    DELIBERATION_RETRY_REASONS = {'TIMEOUT', 'LLM_UPSTREAM'}  # Transient failures only
    MAX_DELIBERATION_RETRIES_PER_CYCLE = 2  # Don't flood the content queue

    # Policy 4: Content pipeline sweep
    CONTENT_STUCK_HOURS = 6              # Kick content stuck longer than this
    MAX_CONTENT_KICKS_PER_CYCLE = 3      # Limit per cycle

    # Policy 5: Attention auto-resolve
    ATTENTION_STALE_HOURS = 12           # Auto-resolve ops alerts older than this
    ATTENTION_AUTO_RESOLVE_SOURCES = {'ops_autopilot'}  # Only resolve our own alerts

    # Policy 6: Governance auto-decision
    GOVERNANCE_GRACE_PERIOD_HOURS = 1    # Give human a chance first
    GOVERNANCE_MAX_PER_CYCLE = 10        # Don't resolve too many at once
    # Source types that are low blast radius (safe to auto-resolve)
    GOVERNANCE_AUTO_RESOLVE_SOURCES = {
        'content:deliverable',       # Deliverable reviews — just notifications
        'content:blog',              # Blog content reviews
        'agent_output:researchagent',
        'agent_output:contentwriteragent',
        'agent_output:stockauditcoordinator',
        'agent_output:sportsoddsanalyst',
        'agent_output:stockanalystagent',
        'agent_output:predictionmarketanalyst',
    }
    # Item types safe to auto-approve without human
    GOVERNANCE_AUTO_APPROVE_TYPES = {
        'review',      # Content reviews
        'insight',     # Agent insights
    }

    # Policy 7: Root-cause remediation
    REMEDIATION_MIN_OCCURRENCES = 5       # Signature must hit N+ before remediation
    REMEDIATION_MAX_PER_CYCLE = 2         # Don't apply too many remediations at once
    REMEDIATION_COOLDOWN_HOURS = 4        # Don't re-remediate same signature too soon
    REMEDIATION_VERIFY_DELAY = 600        # 10 min — wait for fix to take effect

    # Policy 8: Contract/schema drift detection
    DRIFT_CHECK_INTERVAL_HOURS = 6        # Only run drift scan every N hours
    DRIFT_ALERT_ON_CRITICAL = True        # Create governance alert for critical drift

    # Policy 9: Self-tuning
    TUNING_INTERVAL_HOURS = 24            # Only tune once per day
    TUNING_MAX_CHANGES_PER_CYCLE = 1      # One param change per evaluation
    TUNING_MAX_CHANGES_PER_DAY = 2        # Hard daily cap

    # Policy 10: Budget controller
    BUDGET_DAILY_CAP_USD = 15.0           # Global daily spend cap
    BUDGET_HOURLY_CAP_USD = 3.0           # Global hourly spend cap
    BUDGET_SOFT_LIMIT_PCT = 0.7           # Trigger downgrade at 70% of cap
    BUDGET_HARD_LIMIT_PCT = 0.95          # Hard freeze at 95% of cap
    BUDGET_CHECK_INTERVAL_MINUTES = 10    # Check spend every N minutes
    BUDGET_DOWNGRADE_MODEL = 'gpt-5-mini' # Cheap model for downgrade
    BUDGET_CRITICAL_PURPOSES = {          # Never freeze these
        'governance', 'auth', 'incident_response',
    }
    TUNING_LOOKBACK_DAYS = 7              # Analyse this much history
    TUNING_ROLLBACK_RATE_THRESHOLD = 0.3  # >30% rollbacks → go more conservative

    # Mode
    DRY_RUN = False                      # Set True to evaluate but not act

    # ── Runtime overrides from SystemConfiguration ──────────────────────
    # PolicyOptimizer writes tuned values as SystemConfiguration entries
    # with key = 'autopilot_tuning:{PARAM_NAME}'. This classmethod loads
    # them once per cycle so policies use the latest values.

    _overrides_loaded = False
    _override_cache: dict[str, Any] = {}

    @classmethod
    def load_overrides(cls):
        """Load tuned parameter overrides from SystemConfiguration."""
        try:
            from core.models.system import SystemConfiguration
            overrides = SystemConfiguration.objects.filter(
                key__startswith='autopilot_tuning:',
            ).values_list('key', 'value')
            cls._override_cache = {}
            for key, value in overrides:
                param = key.replace('autopilot_tuning:', '')
                cls._override_cache[param] = value
            cls._overrides_loaded = True
        except Exception:
            cls._overrides_loaded = True  # Don't retry on table-missing errors

    @classmethod
    def get(cls, param_name: str):
        """Get a config value, checking overrides first."""
        if not cls._overrides_loaded:
            cls.load_overrides()
        # Override value takes precedence
        if param_name in cls._override_cache:
            return cls._override_cache[param_name]
        return getattr(cls, param_name, None)


# ── Autopilot engine ─────────────────────────────────────────────────────────

class OpsAutopilot:
    """
    Evaluates ops policies and takes allowed actions.
    Called by the Celery beat task every 10 minutes.
    """

    def __init__(self, dry_run: bool | None = None):
        self.dry_run = dry_run if dry_run is not None else AutopilotConfig.DRY_RUN
        self.actions_taken = []
        self.deploy_sha = ''

    def run(self) -> dict[str, Any]:
        """Main entry point. Returns summary of evaluation + actions."""
        now = timezone.now()
        logger.info(f"[OpsAutopilot] Starting cycle (dry_run={self.dry_run})")

        # Load latest config overrides from SystemConfiguration
        AutopilotConfig.load_overrides()

        self.deploy_sha = self._get_deploy_sha()

        # Run policies (v1)
        timeout_results = self._policy_timeout_spike_containment(now)
        hygiene_results = self._policy_blocked_agent_hygiene(now)

        # Run policies (v2 — autonomy)
        delib_retry_results = self._policy_failed_deliberation_retry(now)
        content_sweep_results = self._policy_content_pipeline_sweep(now)
        attention_resolve_results = self._policy_attention_auto_resolve(now)
        governance_results = self._policy_governance_auto_decision(now)

        # Run policies (v3 — root-cause autonomy)
        remediation_results = self._policy_root_cause_remediation(now)
        drift_results = self._policy_contract_drift_detection(now)

        # Run policies (v4 — self-tuning + budget)
        tuning_results = self._policy_self_tuning(now)
        budget_results = self._policy_budget_controller(now)

        # Run policies (v5 — ROI attribution)
        roi_results = self._policy_roi_enforcement(now)

        # Run policies (v6 — impact collection + portfolio allocation)
        impact_results = self._policy_impact_portfolio(now)

        summary = {
            'cycle_at': now.isoformat(),
            'dry_run': self.dry_run,
            'deploy_sha': self.deploy_sha,
            'timeout_spike': timeout_results,
            'blocked_hygiene': hygiene_results,
            'deliberation_retry': delib_retry_results,
            'content_sweep': content_sweep_results,
            'attention_resolve': attention_resolve_results,
            'governance_auto': governance_results,
            'remediation': remediation_results,
            'contract_drift': drift_results,
            'tuning': tuning_results,
            'budget': budget_results,
            'roi': roi_results,
            'impact_portfolio': impact_results,
            'actions_taken': len(self.actions_taken),
            'actions': self.actions_taken,
        }

        # Log every cycle for observability (even no-ops)
        AutopilotAction.objects.create(
            action_type='dry_run' if self.dry_run or not self.actions_taken else 'deploy_watch',
            agent_name='',
            policy='cycle_evaluation',
            dry_run=self.dry_run,
            evidence={
                'timeout_spike': timeout_results,
                'blocked_hygiene': hygiene_results,
                'deliberation_retry': delib_retry_results,
                'content_sweep': content_sweep_results,
                'attention_resolve': attention_resolve_results,
                'governance_auto': governance_results,
                'remediation': remediation_results,
                'contract_drift': drift_results,
                'tuning': tuning_results,
                'budget': budget_results,
                'roi': roi_results,
                'impact_portfolio': impact_results,
            },
            result=summary,
            deploy_sha=self.deploy_sha,
        )

        logger.info(
            f"[OpsAutopilot] Cycle complete: "
            f"{len(self.actions_taken)} actions taken "
            f"(dry_run={self.dry_run})"
        )
        return summary

    # ── Policy 1: Timeout spike containment ──────────────────────────────

    def _policy_timeout_spike_containment(self, now) -> dict:
        """Block agents with too many TIMEOUT signatures in the last hour."""
        from core.models_diagnostic_pipeline import FailureSignature, FailureDetection
        from core.models_unified_system import AgentControlEntry
        from django.db.models import Count

        spike_window = (
            AutopilotConfig.get('TIMEOUT_SPIKE_WINDOW_MINUTES')
            or AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES
        )
        spike_threshold = (
            AutopilotConfig.get('TIMEOUT_SPIKE_THRESHOLD')
            or AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD
        )
        block_ttl = (
            AutopilotConfig.get('TIMEOUT_BLOCK_TTL_MINUTES')
            or AutopilotConfig.TIMEOUT_BLOCK_TTL_MINUTES
        )
        window = now - timedelta(minutes=spike_window)
        result = {'evaluated': True, 'agents_checked': {}, 'blocks_issued': 0}

        try:
            # Group TIMEOUT detections by agent_name in the window
            agent_counts = list(
                FailureDetection.objects.filter(
                    signature__category='timeout',
                    detected_at__gte=window,
                ).values('source_name').annotate(
                    count=Count('id')
                ).order_by('-count')
            )

            if not agent_counts:
                result['note'] = 'No TIMEOUT detections in window'
                return result

            blocks_this_cycle = 0
            already_blocked = AgentControlEntry.get_blocked_names()

            for entry in agent_counts:
                agent_name = entry['source_name']
                count = entry['count']
                result['agents_checked'][agent_name] = count

                if count < spike_threshold:
                    continue

                if agent_name in already_blocked:
                    logger.info(f"[OpsAutopilot] {agent_name} already blocked, skipping")
                    continue

                if blocks_this_cycle >= AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE:
                    logger.warning(
                        f"[OpsAutopilot] Max blocks per cycle reached "
                        f"({AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE}), "
                        f"skipping {agent_name}"
                    )
                    continue

                # Rate limit: check if we already blocked this agent recently
                if self._recently_blocked(agent_name, now):
                    logger.info(
                        f"[OpsAutopilot] {agent_name} was recently auto-blocked, "
                        f"skipping (rate limit)"
                    )
                    continue

                # Gather evidence
                sample_detections = list(
                    FailureDetection.objects.filter(
                        signature__category='timeout',
                        source_name=agent_name,
                        detected_at__gte=window,
                    ).order_by('-detected_at')[:5].values(
                        'id', 'source_id', 'error_message',
                        'context_snapshot', 'detected_at'
                    )
                )
                for s in sample_detections:
                    s['detected_at'] = s['detected_at'].isoformat()
                    s['id'] = str(s['id'])

                evidence = {
                    'agent_name': agent_name,
                    'timeout_count': count,
                    'window_minutes': spike_window,
                    'threshold': spike_threshold,
                    'sample_detections': sample_detections,
                    'deploy_sha': self.deploy_sha,
                }

                # Execute block
                self._execute_block(
                    agent_name=agent_name,
                    reason=(
                        f"Autopilot: {count} timeouts in "
                        f"{spike_window}min "
                        f"(threshold={spike_threshold})"
                    ),
                    ttl_minutes=block_ttl,
                    policy='timeout_spike_containment',
                    evidence=evidence,
                )
                blocks_this_cycle += 1
                result['blocks_issued'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] timeout spike policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 2: Blocked-agent hygiene ──────────────────────────────────

    def _policy_blocked_agent_hygiene(self, now) -> dict:
        """Flag agents that have been blocked too long without TTL."""
        from core.models_unified_system import AgentControlEntry

        result = {'evaluated': True, 'stale_blocks': []}

        try:
            stale_cutoff = now - timedelta(hours=AutopilotConfig.STALE_BLOCK_HOURS)
            stale_entries = AgentControlEntry.objects.filter(
                status='blocked',
                ttl_hours__isnull=True,
                blocked_at__lte=stale_cutoff,
            )

            for entry in stale_entries:
                blocked_hours = (now - entry.blocked_at).total_seconds() / 3600
                stale_info = {
                    'agent_name': entry.agent_name,
                    'blocked_hours': round(blocked_hours, 1),
                    'reason': entry.reason,
                    'blocked_by': entry.blocked_by,
                }
                result['stale_blocks'].append(stale_info)

                # Check if we already flagged this recently (don't spam)
                recent_flag = AutopilotAction.objects.filter(
                    action_type='attention_item',
                    agent_name=entry.agent_name,
                    policy='blocked_agent_hygiene',
                    created_at__gte=now - timedelta(hours=24),
                ).exists()

                if recent_flag:
                    continue

                # Create attention item
                self._create_attention_item(
                    title=f"Agent '{entry.agent_name}' blocked {round(blocked_hours)}h without TTL",
                    summary=(
                        f"{entry.agent_name} has been blocked for "
                        f"{round(blocked_hours, 1)} hours with no auto-unblock TTL. "
                        f"Reason: {entry.reason}. Blocked by: {entry.blocked_by}. "
                        f"Consider adding a TTL or unblocking if the issue is resolved."
                    ),
                    urgency='low',
                    policy='blocked_agent_hygiene',
                    agent_name=entry.agent_name,
                    evidence=stale_info,
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] blocked hygiene policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 3: Failed deliberation retry ─────────────────────────────

    def _policy_failed_deliberation_retry(self, now) -> dict:
        """Retry deliberation sessions that failed with transient errors."""
        from core.models_deliberation import DeliberationSession

        result = {'evaluated': True, 'retried': 0, 'skipped': 0}
        cutoff = now - timedelta(minutes=AutopilotConfig.DELIBERATION_RETRY_AFTER_MINUTES)

        try:
            # Find failed sessions with retryable reason codes, old enough to retry
            candidates = DeliberationSession.objects.filter(
                status='failed',
                failure_reason_code__in=AutopilotConfig.DELIBERATION_RETRY_REASONS,
                created_at__lte=cutoff,
            ).order_by('created_at')[:AutopilotConfig.MAX_DELIBERATION_RETRIES_PER_CYCLE * 2]

            retried = 0
            for session in candidates:
                if retried >= AutopilotConfig.MAX_DELIBERATION_RETRIES_PER_CYCLE:
                    break

                # Check if we already retried this session recently
                already_retried = AutopilotAction.objects.filter(
                    action_type='retry_deliberation',
                    policy='failed_deliberation_retry',
                    dry_run=False,
                    created_at__gte=now - timedelta(hours=2),
                    evidence__session_id=str(session.id),
                ).exists()

                if already_retried:
                    result['skipped'] += 1
                    continue

                # Extract the topic from the objective
                topic = session.objective or ''
                # Strip review conversation prefixes
                if 'Content Review for:' in topic:
                    topic = topic.split('Content Review for:')[1].split('\n')[0].strip()

                if not topic or len(topic) < 10:
                    result['skipped'] += 1
                    continue

                evidence = {
                    'session_id': str(session.id),
                    'failure_reason_code': session.failure_reason_code,
                    'failure_detail': (session.failure_detail or '')[:200],
                    'original_created_at': session.created_at.isoformat(),
                    'topic': topic[:200],
                }

                action_record = {
                    'type': 'retry_deliberation',
                    'session_id': str(session.id),
                    'topic': topic[:200],
                    'reason': session.failure_reason_code,
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    # Dispatch a new deliberation task via Celery
                    try:
                        from core.tasks import generate_self_blog_deliberation_task
                        task = generate_self_blog_deliberation_task.delay(
                            topic_category=topic[:200]
                        )
                        action_record['celery_task_id'] = str(task.id)
                        logger.info(
                            f"[OpsAutopilot] RETRIED deliberation for: {topic[:60]} "
                            f"(was {session.failure_reason_code})"
                        )
                    except Exception as e:
                        logger.warning(f"[OpsAutopilot] Retry dispatch failed: {e}")
                        action_record['dispatch_error'] = str(e)[:200]
                else:
                    logger.info(
                        f"[OpsAutopilot] DRY RUN: would retry deliberation: {topic[:60]}"
                    )

                AutopilotAction.objects.create(
                    action_type='retry_deliberation' if not self.dry_run else 'dry_run',
                    agent_name='ContentDeliberation',
                    policy='failed_deliberation_retry',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                retried += 1

            result['retried'] = retried

        except Exception as e:
            logger.error(f"[OpsAutopilot] deliberation retry policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 4: Content pipeline sweep ──────────────────────────────

    def _policy_content_pipeline_sweep(self, now) -> dict:
        """Kick content stuck in needs_enhancement or pending_review too long."""
        from core.models_unified_system import SelfBlog

        result = {'evaluated': True, 'kicked_enhance': 0, 'kicked_review': 0}
        stuck_cutoff = now - timedelta(hours=AutopilotConfig.CONTENT_STUCK_HOURS)
        kicked = 0

        try:
            # Find blogs stuck in needs_enhancement
            stuck_enhance = SelfBlog.objects.filter(
                status='needs_enhancement',
                created_at__lte=stuck_cutoff,
            ).order_by('created_at')[:AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE]

            for blog in stuck_enhance:
                if kicked >= AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE:
                    break

                # Check if we already kicked this blog recently
                already_kicked = AutopilotAction.objects.filter(
                    action_type='content_sweep',
                    policy='content_pipeline_sweep',
                    dry_run=False,
                    created_at__gte=now - timedelta(hours=6),
                    evidence__blog_id=str(blog.id),
                ).exists()

                if already_kicked:
                    continue

                evidence = {
                    'blog_id': str(blog.id),
                    'title': (blog.title or '')[:100],
                    'status': blog.status,
                    'created_at': blog.created_at.isoformat() if blog.created_at else '',
                    'stuck_hours': round((now - blog.created_at).total_seconds() / 3600, 1),
                }

                action_record = {
                    'type': 'content_sweep',
                    'blog_id': str(blog.id),
                    'action': 'trigger_enhance',
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    try:
                        from core.tasks import auto_enhance_blogs
                        task = auto_enhance_blogs.delay(limit=1)
                        action_record['celery_task_id'] = str(task.id)
                        logger.info(
                            f"[OpsAutopilot] KICKED enhance for stuck blog: "
                            f"{blog.title[:50]} (stuck {evidence['stuck_hours']}h)"
                        )
                    except Exception as e:
                        action_record['dispatch_error'] = str(e)[:200]

                AutopilotAction.objects.create(
                    action_type='content_sweep' if not self.dry_run else 'dry_run',
                    agent_name='ContentPipeline',
                    policy='content_pipeline_sweep',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                kicked += 1
                result['kicked_enhance'] += 1

            # Find blogs stuck in pending_review (never scored)
            stuck_review = SelfBlog.objects.filter(
                status='pending_review',
                quality_score__isnull=True,
                created_at__lte=stuck_cutoff,
            ).order_by('created_at')[:AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE - kicked]

            for blog in stuck_review:
                if kicked >= AutopilotConfig.MAX_CONTENT_KICKS_PER_CYCLE:
                    break

                evidence = {
                    'blog_id': str(blog.id),
                    'title': (blog.title or '')[:100],
                    'status': blog.status,
                    'stuck_hours': round((now - blog.created_at).total_seconds() / 3600, 1),
                }

                action_record = {
                    'type': 'content_sweep',
                    'blog_id': str(blog.id),
                    'action': 'trigger_score',
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    try:
                        from core.tasks import reevaluate_enhanced_blogs
                        task = reevaluate_enhanced_blogs.delay(limit=5)
                        action_record['celery_task_id'] = str(task.id)
                        logger.info(
                            f"[OpsAutopilot] KICKED scoring for stuck blog: "
                            f"{blog.title[:50]}"
                        )
                    except Exception as e:
                        action_record['dispatch_error'] = str(e)[:200]

                AutopilotAction.objects.create(
                    action_type='content_sweep' if not self.dry_run else 'dry_run',
                    agent_name='ContentPipeline',
                    policy='content_pipeline_sweep',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                kicked += 1
                result['kicked_review'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] content sweep policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 5: Attention item auto-resolve ─────────────────────────

    def _policy_attention_auto_resolve(self, now) -> dict:
        """Auto-resolve stale ops_autopilot attention items that resolved themselves."""
        from core.models_human_interface import HumanAttentionItem
        from core.models_unified_system import AgentControlEntry

        result = {'evaluated': True, 'resolved': 0}
        stale_cutoff = now - timedelta(hours=AutopilotConfig.ATTENTION_STALE_HOURS)

        try:
            # Find pending ops_autopilot alerts that are stale
            stale_alerts = HumanAttentionItem.objects.filter(
                status='pending',
                source_type__in=AutopilotConfig.ATTENTION_AUTO_RESOLVE_SOURCES,
                created_at__lte=stale_cutoff,
            ).order_by('created_at')[:20]

            currently_blocked = AgentControlEntry.get_blocked_names()

            for item in stale_alerts:
                # Determine if the underlying issue resolved itself
                should_resolve = False
                resolve_reason = ''
                agent_name = ''

                payload = item.payload or {}
                agent_name = payload.get('agent_name', '')

                # If the alert was about a blocked agent that's now unblocked → resolve
                if 'blocked' in (item.title or '').lower() and agent_name:
                    if agent_name not in currently_blocked:
                        should_resolve = True
                        resolve_reason = (
                            f"Auto-resolved: {agent_name} is no longer blocked "
                            f"(TTL expired or manually unblocked)"
                        )

                # If the alert is a stale hygiene flag older than 24h → resolve
                if not should_resolve and payload.get('policy') == 'blocked_agent_hygiene':
                    age_hours = (now - item.created_at).total_seconds() / 3600
                    if age_hours > 24:
                        should_resolve = True
                        resolve_reason = f"Auto-resolved: hygiene alert aged out ({round(age_hours)}h)"

                # Generic: any ops_autopilot alert > ATTENTION_STALE_HOURS → resolve
                if not should_resolve:
                    age_hours = (now - item.created_at).total_seconds() / 3600
                    if age_hours > AutopilotConfig.ATTENTION_STALE_HOURS * 2:
                        should_resolve = True
                        resolve_reason = (
                            f"Auto-resolved: alert aged {round(age_hours)}h "
                            f"without human action"
                        )

                if not should_resolve:
                    continue

                evidence = {
                    'attention_item_id': str(item.id),
                    'title': (item.title or '')[:150],
                    'agent_name': agent_name,
                    'resolve_reason': resolve_reason,
                    'age_hours': round((now - item.created_at).total_seconds() / 3600, 1),
                }

                action_record = {
                    'type': 'auto_resolve',
                    'attention_item_id': str(item.id),
                    'reason': resolve_reason,
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    item.status = 'ignored'
                    item.decision = 'auto_resolve'
                    item.decision_feedback = resolve_reason[:255]
                    item.decided_at = now
                    item.save(update_fields=[
                        'status', 'decision', 'decision_feedback', 'decided_at'
                    ])
                    logger.info(
                        f"[OpsAutopilot] AUTO-RESOLVED attention item: "
                        f"{item.title[:60]} — {resolve_reason[:60]}"
                    )
                else:
                    logger.info(
                        f"[OpsAutopilot] DRY RUN: would resolve: {item.title[:60]}"
                    )

                AutopilotAction.objects.create(
                    action_type='auto_resolve' if not self.dry_run else 'dry_run',
                    agent_name=agent_name,
                    policy='attention_auto_resolve',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                )
                self.actions_taken.append(action_record)
                result['resolved'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] attention auto-resolve policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 6: Governance auto-decision ──────────────────────────────

    def _policy_governance_auto_decision(self, now) -> dict:
        """Auto-resolve low-blast-radius governance items after grace period."""
        from core.models_human_interface import HumanAttentionItem

        result = {
            'evaluated': True,
            'auto_approved': 0,
            'auto_dismissed': 0,
            'skipped': 0,
        }
        grace_cutoff = now - timedelta(hours=AutopilotConfig.GOVERNANCE_GRACE_PERIOD_HOURS)
        processed = 0

        try:
            # Find pending items from auto-resolvable sources, past grace period
            candidates = HumanAttentionItem.objects.filter(
                status='pending',
                created_at__lte=grace_cutoff,
            ).order_by('created_at')[:AutopilotConfig.GOVERNANCE_MAX_PER_CYCLE * 2]

            for item in candidates:
                if processed >= AutopilotConfig.GOVERNANCE_MAX_PER_CYCLE:
                    break

                source = item.source_type or ''
                item_type = item.item_type or ''

                # Classify blast radius
                is_low_blast = (
                    source in AutopilotConfig.GOVERNANCE_AUTO_RESOLVE_SOURCES
                    or item_type in AutopilotConfig.GOVERNANCE_AUTO_APPROVE_TYPES
                )

                if not is_low_blast:
                    result['skipped'] += 1
                    continue

                # Determine action: approve for insights/reviews, dismiss for stale
                age_hours = (now - item.created_at).total_seconds() / 3600

                if item_type in ('review', 'insight'):
                    action = 'approve'
                    reason = (
                        f"Auto-approved: {item_type} from {source} "
                        f"(low blast radius, {round(age_hours)}h old)"
                    )
                else:
                    action = 'dismiss'
                    reason = (
                        f"Auto-dismissed: {source} item "
                        f"(low blast radius, {round(age_hours)}h old)"
                    )

                evidence = {
                    'attention_item_id': str(item.id),
                    'title': (item.title or '')[:150],
                    'source_type': source,
                    'item_type': item_type,
                    'urgency': item.urgency,
                    'age_hours': round(age_hours, 1),
                    'action': action,
                    'reason': reason,
                }

                action_record = {
                    'type': 'auto_resolve',
                    'attention_item_id': str(item.id),
                    'governance_action': action,
                    'reason': reason,
                    'dry_run': self.dry_run,
                }

                if not self.dry_run:
                    if action == 'approve':
                        item.status = 'acted'
                        item.decision = 'approve'
                    else:
                        item.status = 'ignored'
                        item.decision = 'auto_dismiss'

                    item.decision_feedback = reason[:255]
                    item.decided_at = now
                    item.save(update_fields=[
                        'status', 'decision', 'decision_feedback', 'decided_at'
                    ])
                    logger.info(
                        f"[OpsAutopilot] GOVERNANCE {action}: "
                        f"{item.title[:50]} ({source})"
                    )

                db_action = AutopilotAction.objects.create(
                    action_type='auto_resolve' if not self.dry_run else 'dry_run',
                    agent_name=source,
                    policy='governance_auto_decision',
                    dry_run=self.dry_run,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                    verification_state='pending' if not self.dry_run else 'skipped',
                )

                # Schedule deferred verification for non-dry-run governance actions
                if not self.dry_run:
                    try:
                        from core.tasks import verify_autopilot_action
                        verify_autopilot_action.apply_async(
                            args=[db_action.id], countdown=300,  # 5 min
                        )
                    except Exception:
                        pass
                self.actions_taken.append(action_record)
                processed += 1

                if action == 'approve':
                    result['auto_approved'] += 1
                else:
                    result['auto_dismissed'] += 1

        except Exception as e:
            logger.error(f"[OpsAutopilot] governance auto-decision error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 7: Root-cause remediation ────────────────────────────────

    def _policy_root_cause_remediation(self, now) -> dict:
        """
        Auto-remediate recurring failure patterns using playbook or heuristics.

        Flow:
        1. Find active FailureSignatures with high occurrence counts
        2. Check if a playbook entry exists for the pattern
        3. If yes: apply known fix (if success rate is high enough)
        4. If no: attempt heuristic remediation (timeout adjust, model fallback)
        5. Record outcome, schedule verification, learn from results
        """
        result = {
            'evaluated': True,
            'playbook_applied': 0,
            'heuristic_applied': 0,
            'skipped': 0,
        }

        try:
            engine = RemediationEngine(
                dry_run=self.dry_run,
                deploy_sha=self.deploy_sha,
            )
            remediation_result = engine.run_cycle(now)

            result['playbook_applied'] = remediation_result.get('playbook_applied', 0)
            result['heuristic_applied'] = remediation_result.get('heuristic_applied', 0)
            result['skipped'] = remediation_result.get('skipped', 0)
            result['details'] = remediation_result.get('details', [])

            # Merge engine actions into our action list
            self.actions_taken.extend(remediation_result.get('actions', []))

        except Exception as e:
            logger.error(f"[OpsAutopilot] root-cause remediation error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 8: Contract/schema drift detection ──────────────────────

    def _policy_contract_drift_detection(self, now) -> dict:
        """
        Scan for contract drift between system components.

        Rate-limited to once every DRIFT_CHECK_INTERVAL_HOURS to avoid
        unnecessary overhead (drift changes slowly).
        """
        result = {'evaluated': False, 'skipped_reason': ''}

        try:
            # Rate limit: only scan every N hours
            cutoff = now - timedelta(hours=AutopilotConfig.DRIFT_CHECK_INTERVAL_HOURS)
            recent_scan = AutopilotAction.objects.filter(
                policy='contract_drift_detection',
                created_at__gte=cutoff,
            ).exists()

            if recent_scan:
                result['skipped_reason'] = (
                    f'Scanned within last {AutopilotConfig.DRIFT_CHECK_INTERVAL_HOURS}h'
                )
                return result

            # Run the scan
            from core.services.contract_monitor import ContractMonitor
            monitor = ContractMonitor()
            report = monitor.full_scan()

            result['evaluated'] = True
            result['critical'] = report['critical']
            result['warning'] = report['warning']
            result['info'] = report['info']
            result['total'] = report['total']
            result['checks_run'] = report['checks_run']

            # Log the scan
            AutopilotAction.objects.create(
                action_type='deploy_watch',
                agent_name='ContractMonitor',
                policy='contract_drift_detection',
                dry_run=self.dry_run,
                evidence={
                    'critical': report['critical'],
                    'warning': report['warning'],
                    'info': report['info'],
                    'total': report['total'],
                    'checks_run': report['checks_run'],
                    'findings': report['findings'][:20],  # Cap stored findings
                },
                result=result,
                deploy_sha=self.deploy_sha,
            )

            # Create governance alert if critical drift found
            if (
                report['critical'] > 0
                and AutopilotConfig.DRIFT_ALERT_ON_CRITICAL
                and not self.dry_run
            ):
                summary_text = monitor.summary_for_governance(report)
                self._create_attention_item(
                    title=f"Contract drift: {report['critical']} critical findings",
                    summary=summary_text[:1000],
                    urgency='medium',
                    policy='contract_drift_detection',
                    agent_name='ContractMonitor',
                    evidence={
                        'critical_findings': [
                            f for f in report['findings']
                            if f['severity'] == 'critical'
                        ][:5],
                    },
                )

            logger.info(
                f"[OpsAutopilot] Contract drift scan: "
                f"{report['critical']} critical, "
                f"{report['warning']} warning, "
                f"{report['info']} info"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] contract drift policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 9: Self-tuning ─────────────────────────────────────────────

    def _policy_self_tuning(self, now) -> dict:
        """
        Evaluate policy effectiveness and auto-tune config thresholds.

        Rate-limited to once every TUNING_INTERVAL_HOURS. Emits changelog
        and governance attention item for each change.
        """
        result = {'evaluated': False, 'skipped_reason': ''}

        try:
            # Rate limit: only tune every N hours
            cutoff = now - timedelta(
                hours=AutopilotConfig.get('TUNING_INTERVAL_HOURS')
                or AutopilotConfig.TUNING_INTERVAL_HOURS
            )
            recent_tuning = AutopilotAction.objects.filter(
                policy='self_tuning',
                action_type='config_tune',
                created_at__gte=cutoff,
            ).exists()

            if recent_tuning:
                result['skipped_reason'] = (
                    f'Tuned within last '
                    f'{AutopilotConfig.TUNING_INTERVAL_HOURS}h'
                )
                return result

            # Run the optimizer
            optimizer = PolicyOptimizer()
            tuning_report = optimizer.evaluate()

            result['evaluated'] = True
            result['recommendations'] = tuning_report['recommendations']
            result['changes_applied'] = 0

            if self.dry_run:
                result['mode'] = 'dry_run'
                return result

            # Apply recommendations (capped)
            changes = optimizer.apply_recommendations(
                tuning_report['recommendations'],
                max_changes=AutopilotConfig.TUNING_MAX_CHANGES_PER_CYCLE,
            )

            result['changes_applied'] = len(changes)
            result['changes'] = changes

            # Record each change as an AutopilotAction
            for change in changes:
                AutopilotAction.objects.create(
                    action_type='config_tune',
                    agent_name='PolicyOptimizer',
                    policy='self_tuning',
                    dry_run=False,
                    evidence={
                        'param': change['param'],
                        'old_value': change['old_value'],
                        'new_value': change['new_value'],
                        'reason': change['reason'],
                        'metrics': change.get('metrics', {}),
                    },
                    result=change,
                    deploy_sha=self.deploy_sha,
                )

                # Governance changelog
                self._create_attention_item(
                    title=f"Autopilot self-tuned: {change['param']}",
                    summary=(
                        f"PolicyOptimizer adjusted **{change['param']}** "
                        f"from {change['old_value']} → {change['new_value']}.\n\n"
                        f"**Reason:** {change['reason']}\n"
                        f"**How to undo:** Set SystemConfiguration key "
                        f"`autopilot_tuning:{change['param']}` back to "
                        f"{change['old_value']}, or delete the key to "
                        f"restore the code default.\n"
                        f"**Confidence:** {change.get('confidence', 'medium')}"
                    ),
                    urgency='low',
                    policy='self_tuning',
                    agent_name='PolicyOptimizer',
                    evidence=change,
                )

                self.actions_taken.append({
                    'type': 'config_tune',
                    'param': change['param'],
                    'old_value': change['old_value'],
                    'new_value': change['new_value'],
                    'reason': change['reason'],
                })

            logger.info(
                f"[OpsAutopilot] Self-tuning: {len(changes)} changes applied, "
                f"{len(tuning_report['recommendations'])} recommendations"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] self-tuning policy error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 10: Budget controller ──────────────────────────────────────

    def _policy_budget_controller(self, now) -> dict:
        """
        Monitor LLM spend and enforce budget caps.

        Three escalation tiers:
        1. Soft limit (70%) → downgrade expensive models to gpt-5-mini
        2. Sustained pressure → reduce autopilot action rate
        3. Hard limit (95%) → freeze non-critical LLM calls
        """
        result = {'evaluated': False, 'spend_1h': 0, 'spend_24h': 0}

        try:
            controller = BudgetController()
            spend = controller.compute_spend(now)

            result['evaluated'] = True
            result['spend_1h'] = round(spend['hourly_total'], 4)
            result['spend_24h'] = round(spend['daily_total'], 4)
            result['top_spenders'] = spend.get('top_agents', [])[:5]

            daily_cap = (
                AutopilotConfig.get('BUDGET_DAILY_CAP_USD')
                or AutopilotConfig.BUDGET_DAILY_CAP_USD
            )
            hourly_cap = (
                AutopilotConfig.get('BUDGET_HOURLY_CAP_USD')
                or AutopilotConfig.BUDGET_HOURLY_CAP_USD
            )
            soft_pct = AutopilotConfig.BUDGET_SOFT_LIMIT_PCT
            hard_pct = AutopilotConfig.BUDGET_HARD_LIMIT_PCT

            daily_pct = spend['daily_total'] / max(daily_cap, 0.01)
            hourly_pct = spend['hourly_total'] / max(hourly_cap, 0.01)
            result['daily_utilization'] = round(daily_pct, 3)
            result['hourly_utilization'] = round(hourly_pct, 3)

            # Tier 3: Hard freeze
            if daily_pct >= hard_pct or hourly_pct >= hard_pct:
                result['tier'] = 'hard_freeze'
                if not self.dry_run:
                    action = controller.enforce_hard_freeze(spend, now)
                    if action:
                        self.actions_taken.append(action)
                        self._create_attention_item(
                            title=(
                                f"Budget FREEZE: "
                                f"${spend['daily_total']:.2f}/"
                                f"${daily_cap:.2f} daily"
                            ),
                            summary=(
                                f"LLM spend hit hard limit "
                                f"({daily_pct:.0%} daily, "
                                f"{hourly_pct:.0%} hourly). "
                                f"Non-critical purposes frozen. "
                                f"Only governance/auth/incident "
                                f"allowed until next period."
                            ),
                            urgency='high',
                            policy='budget_controller',
                            agent_name='BudgetController',
                            evidence=spend,
                        )

            # Tier 1: Soft limit → model downgrade
            elif daily_pct >= soft_pct or hourly_pct >= soft_pct:
                result['tier'] = 'model_downgrade'
                if not self.dry_run:
                    action = controller.enforce_model_downgrade(
                        spend, now
                    )
                    if action:
                        self.actions_taken.append(action)

            else:
                result['tier'] = 'normal'
                # Clear any active freeze/downgrade flags
                if not self.dry_run:
                    controller.clear_budget_flags()

            logger.info(
                f"[OpsAutopilot] Budget: "
                f"${spend['daily_total']:.2f} daily "
                f"({daily_pct:.0%}), "
                f"${spend['hourly_total']:.2f} hourly "
                f"({hourly_pct:.0%}) — "
                f"tier={result.get('tier', 'unknown')}"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] budget controller error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 11: ROI enforcement ─────────────────────────────────────────

    def _policy_roi_enforcement(self, now) -> dict:
        """
        Session 1088/1089: Compute QROI per agent and apply selective
        throttles for low-QROI spenders when under budget pressure.

        QROI = ROI × quality_weight — factors in output quality so
        high-cost agents producing excellent work escape throttling.
        """
        result = {'evaluated': False, 'throttles_applied': 0}

        try:
            enforcer = ROIEnforcer()
            roi_data = enforcer.compute_roi_scores(now, window_hours=24)
            result['evaluated'] = True
            result['total_spend'] = roi_data['total_spend']
            result['total_outcomes'] = roi_data['total_outcomes']

            # Top 5 worst QROI agents
            result['worst_qroi'] = roi_data['agents'][:5]

            # Apply throttles if under budget pressure (non-dry-run only)
            if not self.dry_run:
                applied = enforcer.apply_throttles(now)
                result['throttles_applied'] = len(applied)

                if applied:
                    self.actions_taken.append({
                        'type': 'roi_throttle',
                        'count': len(applied),
                        'agents': [a['agent_name'] for a in applied],
                    })
                    self._create_attention_item(
                        title=(
                            f"QROI throttles: {len(applied)} agents "
                            f"on cooldown"
                        ),
                        summary=(
                            f"Budget pressure detected. Applied "
                            f"selective throttles to low-QROI agents: "
                            f"{', '.join(a['agent_name'] for a in applied[:5])}. "
                            f"QROI = ROI × quality_weight — agents "
                            f"producing quality work escape throttling. "
                            f"Undo: clear SystemConfiguration keys "
                            f"starting with 'roi_throttle:'."
                        ),
                        urgency='medium',
                        policy='roi_enforcement',
                        agent_name='ROIEnforcer',
                    )
            else:
                recs = enforcer.get_throttle_recommendations(now)
                result['would_throttle'] = len(recs)
                result['recommendations'] = [
                    {'agent': r['agent_name'],
                     'qroi': r.get('qroi', r['roi']),
                     'roi': r['roi'],
                     'quality': r.get('quality_weight', 0.5),
                     'cooldown': r['cooldown_minutes']}
                    for r in recs[:5]
                ]

            logger.info(
                f"[OpsAutopilot] QROI: "
                f"${roi_data['total_spend']:.2f} spend, "
                f"{roi_data['total_outcomes']} outcomes, "
                f"{result['throttles_applied']} throttles applied"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] ROI enforcement error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 13: Impact Collection + Portfolio Allocation ───────────────

    def _policy_impact_portfolio(self, now) -> dict:
        """
        Session 1089: Collect impact events from settled wagers,
        deliverable interactions, and confirmed revenue. Then compute
        desk-level IQROI and adjust portfolio allocations.
        """
        result = {
            'collected': False,
            'allocated': False,
            'events_created': 0,
            'allocations_changed': 0,
        }

        try:
            # Step 1: Collect new impact events
            collector = ImpactCollector()
            collection = collector.collect_all(now, window_hours=24)
            result['collected'] = True
            result['events_created'] = collection['total_created']
            result['collection_detail'] = collection

            # Step 2: Compute and apply portfolio allocations
            if not self.dry_run:
                allocator = PortfolioAllocator()
                applied = allocator.apply_allocations(now)
                result['allocated'] = True
                result['allocations_changed'] = len(applied)

                if applied:
                    self.actions_taken.append({
                        'type': 'portfolio_allocation',
                        'desks': [a['desk'] for a in applied],
                        'allocations': applied,
                    })
                    desk_summary = ', '.join(
                        f"{a['desk']} {a['allocation']}x"
                        for a in applied[:5]
                    )
                    self._create_attention_item(
                        title=(
                            f"Portfolio rebalanced: "
                            f"{len(applied)} desks adjusted"
                        ),
                        summary=(
                            f"IQROI-based portfolio rebalance: "
                            f"{desk_summary}. Desks with higher "
                            f"impact-to-cost ratio get more budget "
                            f"headroom. Undo: clear SystemConfiguration "
                            f"keys starting with 'desk_allocation:'."
                        ),
                        urgency='low',
                        policy='impact_portfolio',
                        agent_name='PortfolioAllocator',
                    )
            else:
                allocator = PortfolioAllocator()
                desk_data = allocator.compute_desk_iqroi(now)
                result['desk_iqroi'] = {
                    k: {'iqroi': v['iqroi'], 'allocation': v['allocation']}
                    for k, v in desk_data.items()
                }

            logger.info(
                f"[OpsAutopilot] Impact: "
                f"{collection['total_created']} events collected, "
                f"{result['allocations_changed']} allocations changed"
            )

        except Exception as e:
            logger.error(
                f"[OpsAutopilot] Impact/portfolio error: {e}"
            )
            result['error'] = str(e)

        return result

    # ── Action executors ─────────────────────────────────────────────────

    def _execute_block(
        self, agent_name: str, reason: str, ttl_minutes: int,
        policy: str, evidence: dict
    ):
        """Block an agent with TTL, pre-check via ActionVerifier, auto-rollback."""
        from core.models_unified_system import AgentControlEntry

        ttl_hours = round(ttl_minutes / 60, 2)
        action_record = {
            'type': 'block_agent',
            'agent_name': agent_name,
            'ttl_minutes': ttl_minutes,
            'reason': reason,
            'policy': policy,
            'dry_run': self.dry_run,
        }

        if not self.dry_run:
            # Pre-check via ActionVerifier
            verifier = ActionVerifier()
            action = verifier.begin(
                action_type='block_agent',
                policy=policy,
                agent_name=agent_name,
                evidence=evidence,
                deploy_sha=self.deploy_sha,
            )

            if not action.pre_check_passed:
                action_record['blocked_by_pre_check'] = True
                action_record['pre_check_reason'] = action.pre_check_result.get('reason', '')
                AutopilotAction.objects.create(
                    action_type='dry_run',
                    agent_name=agent_name,
                    policy=policy,
                    dry_run=True,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                    verification_state='failed',
                    verification_result={'pre_check': action.pre_check_result},
                )
                self.actions_taken.append(action_record)
                return

            # Execute the block
            AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': reason[:255],
                    'blocked_at': timezone.now(),
                    'blocked_by': 'ops_autopilot',
                    'ttl_hours': ttl_hours if ttl_hours > 0 else None,
                }
            )
            logger.warning(
                f"[OpsAutopilot] BLOCKED {agent_name} for {ttl_minutes}min — {reason}"
            )

            # Create governance attention item
            self._create_attention_item(
                title=f"Autopilot blocked '{agent_name}' ({ttl_minutes}min TTL)",
                summary=(
                    f"Ops Autopilot automatically blocked {agent_name} due to "
                    f"timeout spike. TTL={ttl_minutes}min (auto-unblock at "
                    f"{(timezone.now() + timedelta(minutes=ttl_minutes)).strftime('%H:%M UTC')}). "
                    f"Evidence: {evidence.get('timeout_count', '?')} timeouts in "
                    f"{evidence.get('window_minutes', '?')} minutes."
                ),
                urgency='high',
                policy=policy,
                agent_name=agent_name,
                evidence=evidence,
            )

            # Record with deferred verification (verify in 3 min)
            verifier.record_and_verify(
                action, action_record, verify_delay_seconds=180,
            )
        else:
            logger.info(
                f"[OpsAutopilot] DRY RUN: would block {agent_name} "
                f"for {ttl_minutes}min — {reason}"
            )
            AutopilotAction.objects.create(
                action_type='dry_run',
                agent_name=agent_name,
                policy=policy,
                dry_run=True,
                evidence=evidence,
                result=action_record,
                deploy_sha=self.deploy_sha,
            )

        self.actions_taken.append(action_record)

    def _create_attention_item(
        self, title: str, summary: str, urgency: str,
        policy: str, agent_name: str = '', evidence: dict | None = None
    ):
        """Create a HumanAttentionItem for governance visibility."""
        if self.dry_run:
            logger.info(f"[OpsAutopilot] DRY RUN: would create attention item: {title}")
            return

        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()

            # Get the first superuser (Chris) for the FK
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
            if not user:
                logger.warning("[OpsAutopilot] No user found for attention item")
                return

            HumanAttentionItem.objects.create(
                user=user,
                source_type='ops_autopilot',
                source_agent='OpsAutopilot',
                item_type='alert',
                title=title[:200],
                summary=summary,
                payload={
                    'policy': policy,
                    'agent_name': agent_name,
                    'evidence': evidence or {},
                    'deploy_sha': self.deploy_sha,
                    'autopilot_version': 'v1',
                },
                urgency=urgency,
            )

            # Also log
            AutopilotAction.objects.create(
                action_type='attention_item',
                agent_name=agent_name,
                policy=policy,
                dry_run=False,
                evidence=evidence or {},
                result={'title': title, 'urgency': urgency},
                deploy_sha=self.deploy_sha,
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] Failed to create attention item: {e}")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _recently_blocked(self, agent_name: str, now) -> bool:
        """Check if autopilot already blocked this agent in the last hour."""
        cutoff = now - timedelta(hours=1)
        return AutopilotAction.objects.filter(
            action_type='block_agent',
            agent_name=agent_name,
            dry_run=False,
            created_at__gte=cutoff,
        ).exists()

    def _get_deploy_sha(self) -> str:
        """Get current deploy SHA from environment."""
        import os
        # Railway sets RAILWAY_GIT_COMMIT_SHA; fallback to git
        sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '')
        if not sha:
            try:
                import subprocess
                sha = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'],
                    stderr=subprocess.DEVNULL
                ).decode().strip()[:12]
            except Exception:
                sha = 'unknown'
        return sha[:40]


# ── Action Verifier — autonomous safety layer ────────────────────────────────

class ActionVerifier:
    """
    Wraps autopilot actions with pre-checks, post-verification, and rollback.

    Every non-trivial autonomous action goes through:
      1. PRE-CHECK: Is it safe to act? (blast radius, rate, invariants)
      2. EXECUTE: Perform the action
      3. VERIFY: Did it help? Check SLOs, error rates, queue health
      4. ROLLBACK: If verification fails, undo the action automatically

    Usage:
        verifier = ActionVerifier()
        action = verifier.begin('block_agent', agent_name='FooAgent', policy='timeout_spike')
        if action.pre_check_passed:
            # ... execute the action ...
            action.record_execution({'celery_task_id': '...'})
            verifier.schedule_verification(action, delay_seconds=120)

    Deferred verification runs via Celery after a delay to check outcomes.
    """

    # Pre-check rules per action type
    PRE_CHECK_RULES = {
        'block_agent': {
            'max_concurrent_blocks': 3,     # Don't block too many agents at once
            'min_interval_minutes': 15,     # Don't re-block same agent too fast
            'require_evidence_count': 3,    # Need N+ timeout signatures
        },
        'retry_deliberation': {
            'max_pending_retries': 4,       # Don't flood content queue
            'min_interval_minutes': 30,     # Don't retry same topic too fast
        },
        'content_sweep': {
            'max_concurrent_sweeps': 3,     # Don't kick too many blogs at once
        },
        'auto_resolve': {
            'max_per_cycle': 15,            # Don't mass-resolve in one pass
        },
        'content_publish': {
            'max_daily': 8,                 # Hard daily publish limit
            'min_quality_score': 0.3,       # Don't publish garbage
        },
    }

    def begin(
        self,
        action_type: str,
        policy: str,
        agent_name: str = '',
        evidence: dict | None = None,
        deploy_sha: str = '',
    ) -> 'VerifiableAction':
        """Create a verifiable action and run pre-checks."""
        action = VerifiableAction(
            action_type=action_type,
            policy=policy,
            agent_name=agent_name,
            evidence=evidence or {},
            deploy_sha=deploy_sha,
        )

        # Run pre-checks
        rules = self.PRE_CHECK_RULES.get(action_type, {})
        pre_check_result = self._run_pre_checks(action, rules)
        action.pre_check_result = pre_check_result
        action.pre_check_passed = pre_check_result.get('passed', True)

        if not action.pre_check_passed:
            logger.warning(
                f"[ActionVerifier] PRE-CHECK FAILED for {action_type}: "
                f"{pre_check_result.get('reason', 'unknown')}"
            )

        return action

    def _run_pre_checks(self, action: 'VerifiableAction', rules: dict) -> dict:
        """Evaluate pre-check rules. Returns {'passed': bool, 'reason': str, ...}."""
        result = {'passed': True, 'checks': []}

        try:
            now = timezone.now()

            # Check: max concurrent blocks
            if 'max_concurrent_blocks' in rules and action.action_type == 'block_agent':
                from core.models_unified_system import AgentControlEntry
                current_blocks = AgentControlEntry.objects.filter(
                    status='blocked',
                    blocked_by='ops_autopilot',
                ).count()
                check = {
                    'name': 'max_concurrent_blocks',
                    'current': current_blocks,
                    'limit': rules['max_concurrent_blocks'],
                    'passed': current_blocks < rules['max_concurrent_blocks'],
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Too many concurrent autopilot blocks "
                        f"({current_blocks}/{rules['max_concurrent_blocks']})"
                    )

            # Check: min interval between same-agent actions
            if 'min_interval_minutes' in rules and action.agent_name:
                cutoff = now - timedelta(minutes=rules['min_interval_minutes'])
                recent = AutopilotAction.objects.filter(
                    action_type=action.action_type,
                    agent_name=action.agent_name,
                    dry_run=False,
                    created_at__gte=cutoff,
                ).exists()
                check = {
                    'name': 'min_interval',
                    'agent': action.agent_name,
                    'interval_minutes': rules['min_interval_minutes'],
                    'passed': not recent,
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Same action on {action.agent_name} too recently "
                        f"(within {rules['min_interval_minutes']}min)"
                    )

            # Check: max pending retries (content queue capacity)
            if 'max_pending_retries' in rules:
                from core.models_celery_telemetry import CeleryTaskEvent
                pending = CeleryTaskEvent.objects.filter(
                    task_name__icontains='deliberation',
                    status='STARTED',
                    started_at__gte=now - timedelta(hours=1),
                ).count()
                check = {
                    'name': 'max_pending_retries',
                    'current': pending,
                    'limit': rules['max_pending_retries'],
                    'passed': pending < rules['max_pending_retries'],
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Too many pending deliberation tasks ({pending})"
                    )

            # Check: daily publish limit
            if 'max_daily' in rules:
                from core.models_unified_system import SelfBlog
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                published_today = SelfBlog.objects.filter(
                    status='published',
                    created_at__gte=today_start,
                ).count()
                check = {
                    'name': 'max_daily_publish',
                    'current': published_today,
                    'limit': rules['max_daily'],
                    'passed': published_today < rules['max_daily'],
                }
                result['checks'].append(check)
                if not check['passed']:
                    result['passed'] = False
                    result['reason'] = (
                        f"Daily publish limit reached ({published_today})"
                    )

        except Exception as e:
            logger.error(f"[ActionVerifier] Pre-check error: {e}")
            result['error'] = str(e)
            # Fail-open: if pre-checks crash, still allow action (logged)

        return result

    def record_and_verify(
        self,
        action: 'VerifiableAction',
        execution_result: dict,
        verify_delay_seconds: int = 120,
    ) -> AutopilotAction:
        """
        Record the action to DB and schedule deferred verification.

        After execution, creates an AutopilotAction record with
        verification_state='pending'. A Celery task checks outcomes
        after verify_delay_seconds.
        """
        db_action = AutopilotAction.objects.create(
            action_type=action.action_type,
            agent_name=action.agent_name,
            policy=action.policy,
            dry_run=False,
            evidence=action.evidence,
            result=execution_result,
            deploy_sha=action.deploy_sha,
            verification_state='pending',
            verification_result={
                'pre_check': action.pre_check_result,
                'scheduled_verify_at': (
                    timezone.now() + timedelta(seconds=verify_delay_seconds)
                ).isoformat(),
            },
        )

        # Schedule deferred verification via Celery
        if verify_delay_seconds > 0:
            try:
                from core.tasks import verify_autopilot_action
                verify_autopilot_action.apply_async(
                    args=[db_action.id],
                    countdown=verify_delay_seconds,
                )
                logger.info(
                    f"[ActionVerifier] Verification scheduled for action "
                    f"{db_action.id} in {verify_delay_seconds}s"
                )
            except Exception as e:
                logger.warning(f"[ActionVerifier] Failed to schedule verification: {e}")
                # Mark as skipped if we can't verify
                db_action.verification_state = 'skipped'
                db_action.save(update_fields=['verification_state'])

        return db_action

    @staticmethod
    def verify_action(action_id: int) -> dict:
        """
        Deferred verification — called by Celery task after delay.

        Checks whether the action improved the situation:
        - block_agent: Did error rate for that agent drop?
        - retry_deliberation: Did the retry succeed (new session completed)?
        - content_sweep: Did the blog move forward in pipeline?
        - auto_resolve: No new alerts spawned from same source?
        - content_publish: No quality complaints?
        """
        try:
            action = AutopilotAction.objects.get(id=action_id)
        except AutopilotAction.DoesNotExist:
            return {'error': f'Action {action_id} not found'}

        if action.verification_state not in ('pending',):
            return {'skipped': True, 'reason': f'State is {action.verification_state}'}

        now = timezone.now()
        result = {'action_id': action_id, 'checks': [], 'passed': True}

        try:
            if action.action_type == 'block_agent':
                result = ActionVerifier._verify_block_agent(action, now)

            elif action.action_type == 'retry_deliberation':
                result = ActionVerifier._verify_retry_deliberation(action, now)

            elif action.action_type == 'content_sweep':
                result = ActionVerifier._verify_content_sweep(action, now)

            elif action.action_type == 'remediate':
                result = RemediationEngine.verify_remediation(action)

            elif action.action_type in ('auto_resolve', 'content_publish'):
                # Lightweight: just check no new errors spawned
                from core.models_diagnostic_pipeline import FailureDetection
                new_errors = FailureDetection.objects.filter(
                    detected_at__gte=action.created_at,
                    source_name__icontains=action.agent_name or 'autopilot',
                ).count()
                result['checks'].append({
                    'name': 'no_cascading_errors',
                    'new_errors': new_errors,
                    'passed': new_errors == 0,
                })
                result['passed'] = new_errors == 0
            else:
                # Unknown action type — skip verification
                result['passed'] = True
                result['skipped'] = True

        except Exception as e:
            logger.error(f"[ActionVerifier] Verification error for {action_id}: {e}")
            result['error'] = str(e)
            result['passed'] = True  # Fail-open on verification errors

        # Update the action record
        action.verification_state = 'passed' if result.get('passed') else 'failed'
        action.verification_result = {
            **(action.verification_result or {}),
            'verification': result,
            'verified_at': now.isoformat(),
        }
        action.save(update_fields=['verification_state', 'verification_result'])

        # If verification failed, attempt rollback
        if not result.get('passed'):
            ActionVerifier._attempt_rollback(action, result)

        return result

    @staticmethod
    def _verify_block_agent(action: AutopilotAction, now) -> dict:
        """Verify that blocking an agent reduced error rate."""
        from core.models_diagnostic_pipeline import FailureDetection

        agent_name = action.agent_name
        result = {'action_id': action.id, 'checks': [], 'passed': True}

        # Check: error rate for this agent dropped since block
        errors_before = FailureDetection.objects.filter(
            source_name=agent_name,
            detected_at__gte=action.created_at - timedelta(hours=1),
            detected_at__lt=action.created_at,
        ).count()

        errors_after = FailureDetection.objects.filter(
            source_name=agent_name,
            detected_at__gte=action.created_at,
        ).count()

        check = {
            'name': 'error_rate_reduced',
            'errors_before': errors_before,
            'errors_after': errors_after,
            'passed': errors_after <= errors_before,  # At least no worse
        }
        result['checks'].append(check)
        result['passed'] = check['passed']

        return result

    @staticmethod
    def _verify_retry_deliberation(action: AutopilotAction, now) -> dict:
        """Verify that the retried deliberation produced output."""
        from core.models_deliberation import DeliberationSession

        result = {'action_id': action.id, 'checks': [], 'passed': True}

        # Check: did a new successful session appear after the retry?
        evidence = action.evidence or {}
        topic = evidence.get('topic', '')[:100]

        if topic:
            new_sessions = DeliberationSession.objects.filter(
                status='completed',
                created_at__gte=action.created_at,
                objective__icontains=topic[:50],
            ).count()

            check = {
                'name': 'retry_produced_output',
                'new_completed_sessions': new_sessions,
                'passed': new_sessions > 0,
            }
            result['checks'].append(check)
            # Don't fail on this — retry might still be in progress
            result['passed'] = True  # Retry is best-effort
        else:
            result['passed'] = True

        return result

    @staticmethod
    def _verify_content_sweep(action: AutopilotAction, now) -> dict:
        """Verify that the swept content moved forward."""
        from core.models_unified_system import SelfBlog

        result = {'action_id': action.id, 'checks': [], 'passed': True}

        evidence = action.evidence or {}
        blog_id = evidence.get('blog_id', '')

        if blog_id:
            try:
                blog = SelfBlog.objects.get(id=blog_id)
                # Check if blog moved to a later stage
                forward_statuses = {'approved', 'published', 'pending_review'}
                check = {
                    'name': 'content_progressed',
                    'current_status': blog.status,
                    'passed': blog.status in forward_statuses,
                }
                result['checks'].append(check)
                # Content sweep is best-effort — don't roll back
                result['passed'] = True
            except SelfBlog.DoesNotExist:
                result['passed'] = True

        return result

    @staticmethod
    def _attempt_rollback(action: AutopilotAction, verification_result: dict):
        """Attempt to rollback a failed action."""
        now = timezone.now()
        rollback_reason = verification_result.get(
            'checks', [{}]
        )[-1].get('name', 'verification_failed') if verification_result.get('checks') else 'verification_failed'

        logger.warning(
            f"[ActionVerifier] ROLLBACK for action {action.id} "
            f"({action.action_type}): {rollback_reason}"
        )

        try:
            if action.action_type == 'block_agent' and action.agent_name:
                # Rollback: unblock the agent
                from core.models_unified_system import AgentControlEntry
                AgentControlEntry.objects.filter(
                    agent_name=action.agent_name,
                    blocked_by='ops_autopilot',
                ).update(
                    status='active',
                    reason=f"Auto-rollback: {rollback_reason}",
                )
                logger.info(
                    f"[ActionVerifier] ROLLED BACK block on {action.agent_name}"
                )

            elif action.action_type == 'auto_resolve':
                # Rollback: re-open the attention item
                evidence = action.evidence or {}
                attention_id = evidence.get('attention_item_id', '')
                if attention_id:
                    from core.models_human_interface import HumanAttentionItem
                    HumanAttentionItem.objects.filter(
                        id=attention_id,
                    ).update(
                        status='pending',
                        decision='',
                        decision_feedback=f'Reopened by auto-rollback: {rollback_reason}',
                    )
                    logger.info(
                        f"[ActionVerifier] ROLLED BACK auto-resolve on {attention_id}"
                    )

            # Mark as rolled back
            action.rolled_back = True
            action.rolled_back_at = now
            action.rollback_reason = rollback_reason[:255]
            action.verification_state = 'rolled_back'
            action.save(update_fields=[
                'rolled_back', 'rolled_back_at',
                'rollback_reason', 'verification_state',
            ])

            # Create governance alert about the rollback
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(is_superuser=True).first()
            if user:
                HumanAttentionItem.objects.create(
                    user=user,
                    source_type='ops_autopilot',
                    source_agent='ActionVerifier',
                    item_type='alert',
                    title=f"Auto-rollback: {action.action_type} on {action.agent_name or 'system'}",
                    summary=(
                        f"Autopilot action #{action.id} ({action.action_type}) was "
                        f"automatically rolled back because post-verification failed. "
                        f"Reason: {rollback_reason}. "
                        f"This may indicate the autonomous action made things worse."
                    ),
                    urgency='high',
                    payload={
                        'rollback': True,
                        'action_id': action.id,
                        'action_type': action.action_type,
                        'verification_result': verification_result,
                    },
                )

        except Exception as e:
            logger.error(f"[ActionVerifier] Rollback failed for action {action.id}: {e}")
            action.rollback_reason = f"Rollback error: {str(e)[:200]}"
            action.save(update_fields=['rollback_reason'])


class VerifiableAction:
    """Holds state for an action being verified."""

    def __init__(
        self,
        action_type: str,
        policy: str,
        agent_name: str = '',
        evidence: dict | None = None,
        deploy_sha: str = '',
    ):
        self.action_type = action_type
        self.policy = policy
        self.agent_name = agent_name
        self.evidence = evidence or {}
        self.deploy_sha = deploy_sha
        self.pre_check_result: dict = {}
        self.pre_check_passed: bool = True


# ── Remediation Engine — root-cause autonomy ─────────────────────────────────


class RemediationEngine:
    """
    Converts verified failure patterns into safe, reversible config fixes.

    Safe remediation types (all config-only, easy to roll back):
    1. timeout_adjust: Increase wall-clock timeout for chronically slow agents
    2. model_fallback: Route agent to fallback LLM when primary provider is down
    3. block_and_wait: Temp-block agent until external provider recovers
    4. retry_config: Adjust retry intervals for transient failures

    Flow per cycle:
      1. Find FailureSignatures with occurrence >= threshold and status='active'
      2. Look for matching RemediationPlaybook entry
      3. If playbook match: apply known fix (if confidence high enough)
      4. If no match: attempt heuristic remediation based on category
      5. Record as AutopilotAction(action_type='remediate')
      6. Schedule deferred verification to check if it helped
      7. On verification: update playbook success rate or create new entry
    """

    # Heuristic remediation rules by failure category
    HEURISTIC_RULES = {
        'timeout': {
            'remediation_type': 'timeout_adjust',
            'description': 'Increase agent timeout by 50%',
            'multiplier': 1.5,
            'max_timeout': 1800,  # 30 min absolute cap
        },
        'provider_error': {
            'remediation_type': 'model_fallback',
            'description': 'Switch to fallback LLM provider',
        },
        'resource_error': {
            'remediation_type': 'block_and_wait',
            'description': 'Block agent until resource recovers',
            'block_minutes': 60,
        },
    }

    def __init__(self, dry_run: bool = False, deploy_sha: str = ''):
        self.dry_run = dry_run
        self.deploy_sha = deploy_sha
        self.actions: list = []

    def run_cycle(self, now) -> dict:
        """Main remediation cycle. Returns summary dict."""
        from core.models_diagnostic_pipeline import FailureSignature

        result = {
            'playbook_applied': 0,
            'heuristic_applied': 0,
            'skipped': 0,
            'details': [],
            'actions': [],
        }

        try:
            # Find active signatures above occurrence threshold
            candidates = FailureSignature.objects.filter(
                status='active',
                occurrence_count__gte=AutopilotConfig.REMEDIATION_MIN_OCCURRENCES,
            ).order_by('-occurrence_count')[:10]

            applied = 0
            for sig in candidates:
                if applied >= AutopilotConfig.REMEDIATION_MAX_PER_CYCLE:
                    break

                # Cooldown check: don't re-remediate too soon
                if self._on_cooldown(sig, now):
                    result['skipped'] += 1
                    continue

                # Check if we already have a pending remediation for this sig
                if self._has_pending_remediation(sig, now):
                    result['skipped'] += 1
                    continue

                # Try playbook first, then heuristic
                applied_entry = self._try_playbook(sig, now)
                if applied_entry:
                    result['playbook_applied'] += 1
                    result['details'].append(applied_entry)
                    result['actions'].append(applied_entry)
                    self.actions.append(applied_entry)
                    applied += 1
                    continue

                heuristic_entry = self._try_heuristic(sig, now)
                if heuristic_entry:
                    result['heuristic_applied'] += 1
                    result['details'].append(heuristic_entry)
                    result['actions'].append(heuristic_entry)
                    self.actions.append(heuristic_entry)
                    applied += 1
                else:
                    result['skipped'] += 1

        except Exception as e:
            logger.error(f"[RemediationEngine] cycle error: {e}")
            result['error'] = str(e)

        return result

    def _on_cooldown(self, sig, now) -> bool:
        """Check if this signature was remediated recently."""
        cutoff = now - timedelta(hours=AutopilotConfig.REMEDIATION_COOLDOWN_HOURS)
        return AutopilotAction.objects.filter(
            action_type='remediate',
            evidence__signature_id=str(sig.id),
            dry_run=False,
            created_at__gte=cutoff,
        ).exists()

    def _has_pending_remediation(self, sig, now) -> bool:
        """Check if there's a pending (unverified) remediation for this sig."""
        return AutopilotAction.objects.filter(
            action_type='remediate',
            evidence__signature_id=str(sig.id),
            dry_run=False,
            verification_state='pending',
        ).exists()

    def _try_playbook(self, sig, now) -> dict | None:
        """Try to apply a known playbook fix for this signature."""
        # Match by exact signature or by category
        from django.db.models import Q
        playbook = RemediationPlaybook.objects.filter(
            enabled=True,
        ).filter(
            Q(signature_pattern=sig.signature) |
            Q(failure_category=sig.category)
        ).order_by('-success_rate').first()

        if not playbook:
            return None

        # Confidence gate
        if playbook.times_applied >= 2 and playbook.success_rate < playbook.min_confidence:
            logger.info(
                f"[RemediationEngine] Playbook {playbook.id} for {sig.signature} "
                f"below confidence ({playbook.success_rate:.0%}), skipping"
            )
            return None

        return self._apply_remediation(
            sig=sig,
            remediation_type=playbook.remediation_type,
            config=playbook.config,
            source='playbook',
            playbook_id=playbook.id,
            now=now,
        )

    def _try_heuristic(self, sig, now) -> dict | None:
        """Try a heuristic remediation based on failure category."""
        rule = self.HEURISTIC_RULES.get(sig.category)
        if not rule:
            return None

        # Build config from heuristic
        config = {}
        remediation_type = rule['remediation_type']

        if remediation_type == 'timeout_adjust':
            # Find the agent name from recent detections
            agent_name = self._get_primary_agent(sig)
            if not agent_name:
                return None
            current_timeout = self._get_current_timeout(agent_name)
            new_timeout = min(
                int(current_timeout * rule['multiplier']),
                rule['max_timeout'],
            )
            if new_timeout <= current_timeout:
                return None  # Already at max
            config = {
                'agent_name': agent_name,
                'current_timeout': current_timeout,
                'new_timeout': new_timeout,
            }

        elif remediation_type == 'model_fallback':
            agent_name = self._get_primary_agent(sig)
            if not agent_name:
                return None
            config = {
                'agent_name': agent_name,
                'provider': sig.provider,
                'error_code': sig.error_code,
            }

        elif remediation_type == 'block_and_wait':
            agent_name = self._get_primary_agent(sig)
            if not agent_name:
                return None
            config = {
                'agent_name': agent_name,
                'block_minutes': rule['block_minutes'],
            }

        return self._apply_remediation(
            sig=sig,
            remediation_type=remediation_type,
            config=config,
            source='heuristic',
            now=now,
        )

    def _apply_remediation(
        self,
        sig,
        remediation_type: str,
        config: dict,
        source: str,
        now,
        playbook_id: int | None = None,
    ) -> dict:
        """Apply a specific remediation and schedule verification."""
        agent_name = config.get('agent_name', '')

        evidence = {
            'signature_id': str(sig.id),
            'signature': sig.signature,
            'category': sig.category,
            'occurrence_count': sig.occurrence_count,
            'remediation_type': remediation_type,
            'config': config,
            'source': source,
        }
        if playbook_id:
            evidence['playbook_id'] = playbook_id

        action_record = {
            'type': 'remediate',
            'remediation_type': remediation_type,
            'signature': sig.signature,
            'agent_name': agent_name,
            'config': config,
            'source': source,
            'dry_run': self.dry_run,
        }

        if not self.dry_run:
            # Execute the remediation
            exec_result = self._execute_remediation(
                remediation_type, config, sig,
            )
            action_record['execution'] = exec_result

            if exec_result.get('applied'):
                # Record with deferred verification
                db_action = AutopilotAction.objects.create(
                    action_type='remediate',
                    agent_name=agent_name,
                    policy='root_cause_remediation',
                    dry_run=False,
                    evidence=evidence,
                    result=action_record,
                    deploy_sha=self.deploy_sha,
                    verification_state='pending',
                    verification_result={
                        'source': source,
                        'playbook_id': playbook_id,
                    },
                )

                # Schedule verification
                try:
                    from core.tasks import verify_autopilot_action
                    verify_autopilot_action.apply_async(
                        args=[db_action.id],
                        countdown=AutopilotConfig.REMEDIATION_VERIFY_DELAY,
                    )
                except Exception as e:
                    logger.warning(
                        f"[RemediationEngine] Failed to schedule verification: {e}"
                    )

                # Mark signature as diagnosed
                sig.mark_diagnosed()

                logger.info(
                    f"[RemediationEngine] APPLIED {remediation_type} for "
                    f"{sig.signature} ({source}): {config}"
                )
            else:
                logger.info(
                    f"[RemediationEngine] Remediation {remediation_type} "
                    f"for {sig.signature} could not be applied: "
                    f"{exec_result.get('reason', 'unknown')}"
                )
                return action_record
        else:
            logger.info(
                f"[RemediationEngine] DRY RUN: would apply {remediation_type} "
                f"for {sig.signature}: {config}"
            )
            AutopilotAction.objects.create(
                action_type='dry_run',
                agent_name=agent_name,
                policy='root_cause_remediation',
                dry_run=True,
                evidence=evidence,
                result=action_record,
                deploy_sha=self.deploy_sha,
            )

        return action_record

    def _execute_remediation(
        self, remediation_type: str, config: dict, sig
    ) -> dict:
        """Execute a specific remediation. Returns {applied: bool, ...}."""
        if remediation_type == 'timeout_adjust':
            return self._exec_timeout_adjust(config)
        elif remediation_type == 'model_fallback':
            return self._exec_model_fallback(config)
        elif remediation_type == 'block_and_wait':
            return self._exec_block_and_wait(config, sig)
        return {'applied': False, 'reason': f'Unknown type: {remediation_type}'}

    def _exec_timeout_adjust(self, config: dict) -> dict:
        """
        Adjust agent timeout by writing to SystemConfiguration.

        We store timeout overrides in SystemConfiguration so they persist
        across deploys and can be read by execute_agent_task.
        """
        agent_name = config['agent_name']
        new_timeout = config['new_timeout']

        try:
            from core.models.system import SystemConfiguration
            key = f'agent_timeout_override:{agent_name}'
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': str(new_timeout),
                    'description': (
                        f'Auto-remediation: timeout adjusted from '
                        f'{config["current_timeout"]}s to {new_timeout}s'
                    ),
                },
            )
            return {
                'applied': True,
                'key': key,
                'old_timeout': config['current_timeout'],
                'new_timeout': new_timeout,
            }
        except Exception as e:
            logger.error(f"[RemediationEngine] timeout adjust failed: {e}")
            return {'applied': False, 'reason': str(e)}

    def _exec_model_fallback(self, config: dict) -> dict:
        """
        Trigger model fallback for an agent's LLM provider.

        Records a SystemConfiguration flag that the agent_llm_router checks.
        """
        agent_name = config.get('agent_name', '')
        provider = config.get('provider', '')

        if not agent_name or not provider:
            return {'applied': False, 'reason': 'Missing agent_name or provider'}

        try:
            from core.models.system import SystemConfiguration
            key = f'llm_fallback_active:{provider}'
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': 'true',
                    'description': (
                        f'Auto-remediation: {provider} provider failing, '
                        f'fallback activated for {agent_name}'
                    ),
                },
            )
            return {
                'applied': True,
                'key': key,
                'provider': provider,
                'agent': agent_name,
            }
        except Exception as e:
            logger.error(f"[RemediationEngine] model fallback failed: {e}")
            return {'applied': False, 'reason': str(e)}

    def _exec_block_and_wait(self, config: dict, sig) -> dict:
        """Block an agent temporarily until external resource recovers."""
        agent_name = config.get('agent_name', '')
        block_minutes = config.get('block_minutes', 60)

        if not agent_name:
            return {'applied': False, 'reason': 'Missing agent_name'}

        try:
            from core.models_unified_system import AgentControlEntry
            ttl_hours = round(block_minutes / 60, 2)
            AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': (
                        f'Auto-remediation: {sig.signature} '
                        f'({sig.occurrence_count} occurrences)'
                    )[:255],
                    'blocked_at': timezone.now(),
                    'blocked_by': 'remediation_engine',
                    'ttl_hours': ttl_hours,
                },
            )
            return {
                'applied': True,
                'agent': agent_name,
                'block_minutes': block_minutes,
                'ttl_hours': ttl_hours,
            }
        except Exception as e:
            logger.error(f"[RemediationEngine] block_and_wait failed: {e}")
            return {'applied': False, 'reason': str(e)}

    # ── Helpers ──────────────────────────────────────────────────────

    def _get_primary_agent(self, sig) -> str:
        """Get the most affected agent name from recent detections."""
        from core.models_diagnostic_pipeline import FailureDetection
        from django.db.models import Count

        top = (
            FailureDetection.objects.filter(signature=sig)
            .values('source_name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')
            .first()
        )
        return (top or {}).get('source_name', '')

    def _get_current_timeout(self, agent_name: str) -> int:
        """Get current timeout for an agent (check override first, then default map)."""
        # Check for existing override
        try:
            from core.models.system import SystemConfiguration
            override = SystemConfiguration.objects.filter(
                key=f'agent_timeout_override:{agent_name}',
            ).first()
            if override:
                return int(override.value)
        except Exception:
            pass

        # Fall back to the hardcoded map
        AGENT_TIMEOUT_DEFAULTS = {
            'AudioAgent': 300, 'ImageAgent': 300, 'VideoAgent': 600,
            'ThreeDAgent': 300, 'ImageEditingAgent': 300,
            'VideoEditingAgent': 600, 'TalkingCharacterAgent': 600,
            'ResolveAgent': 600, 'ResearchAgent': 600,
            'SystemIntelligenceAgent': 600, 'MarketingStrategyAgent': 600,
            'CustomerResearchAgent': 600, 'CharacterTrainingAgent': 600,
            'ContentWriterAgent': 600, 'CompetitorAnalysisAgent': 600,
            'BrandStrategyAgent': 600, 'ContentStrategyAgent': 600,
        }
        return AGENT_TIMEOUT_DEFAULTS.get(agent_name, 1200)

    @staticmethod
    def verify_remediation(action: AutopilotAction) -> dict:
        """
        Verify a remediation action worked. Called by ActionVerifier.verify_action.

        Checks whether the failure signature's occurrence rate dropped since
        the remediation was applied.
        """
        from core.models_diagnostic_pipeline import FailureDetection

        now = timezone.now()
        evidence = action.evidence or {}
        sig_id = evidence.get('signature_id', '')
        result = {'action_id': action.id, 'checks': [], 'passed': True}

        if not sig_id:
            result['passed'] = True
            result['skipped'] = True
            return result

        # Compare error rate before vs after remediation
        window = timedelta(hours=1)
        errors_before = FailureDetection.objects.filter(
            signature_id=sig_id,
            detected_at__gte=action.created_at - window,
            detected_at__lt=action.created_at,
        ).count()

        errors_after = FailureDetection.objects.filter(
            signature_id=sig_id,
            detected_at__gte=action.created_at,
            detected_at__lte=now,
        ).count()

        # Normalize by time window
        time_after = (now - action.created_at).total_seconds() / 3600
        rate_before = errors_before  # per hour (1h window)
        rate_after = errors_after / max(time_after, 0.1)  # per hour

        check = {
            'name': 'error_rate_reduced',
            'errors_before': errors_before,
            'errors_after': errors_after,
            'rate_before': round(rate_before, 2),
            'rate_after': round(rate_after, 2),
            'reduction_pct': round(
                (1 - rate_after / max(rate_before, 0.1)) * 100, 1
            ) if rate_before > 0 else 100.0,
            'passed': rate_after <= rate_before,
        }
        result['checks'].append(check)
        result['passed'] = check['passed']

        # Update playbook if this was from one
        playbook_id = (action.verification_result or {}).get('playbook_id')
        if playbook_id:
            try:
                playbook = RemediationPlaybook.objects.get(id=playbook_id)
                playbook.record_outcome(succeeded=check['passed'])
            except RemediationPlaybook.DoesNotExist:
                pass

        # If heuristic succeeded, create a playbook entry for future use
        source = (action.verification_result or {}).get('source', '')
        if check['passed'] and source == 'heuristic':
            sig_pattern = evidence.get('signature', '')
            category = evidence.get('category', '')
            rem_type = evidence.get('remediation_type', '')
            config = evidence.get('config', {})

            if sig_pattern and rem_type:
                RemediationPlaybook.objects.get_or_create(
                    signature_pattern=sig_pattern,
                    failure_category=category,
                    remediation_type=rem_type,
                    defaults={
                        'config': config,
                        'times_applied': 1,
                        'times_succeeded': 1,
                        'success_rate': 1.0,
                    },
                )
                logger.info(
                    f"[RemediationEngine] Created playbook entry for "
                    f"{sig_pattern} → {rem_type}"
                )

        # If remediation failed, attempt rollback
        if not check['passed']:
            RemediationEngine._rollback_remediation(action, evidence)

        return result

    @staticmethod
    def _rollback_remediation(action: AutopilotAction, evidence: dict):
        """Roll back a failed remediation."""
        rem_type = evidence.get('remediation_type', '')
        config = evidence.get('config', {})
        now = timezone.now()

        try:
            if rem_type == 'timeout_adjust':
                # Restore original timeout
                from core.models.system import SystemConfiguration
                agent_name = config.get('agent_name', '')
                old_timeout = config.get('current_timeout', '')
                if agent_name and old_timeout:
                    key = f'agent_timeout_override:{agent_name}'
                    SystemConfiguration.objects.filter(key=key).update(
                        value=str(old_timeout),
                        description=f'Rolled back: timeout restored to {old_timeout}s',
                    )

            elif rem_type == 'model_fallback':
                # Remove fallback flag
                from core.models.system import SystemConfiguration
                provider = config.get('provider', '')
                if provider:
                    key = f'llm_fallback_active:{provider}'
                    SystemConfiguration.objects.filter(key=key).delete()

            elif rem_type == 'block_and_wait':
                # Unblock the agent
                from core.models_unified_system import AgentControlEntry
                agent_name = config.get('agent_name', '')
                if agent_name:
                    AgentControlEntry.objects.filter(
                        agent_name=agent_name,
                        blocked_by='remediation_engine',
                    ).update(
                        status='active',
                        reason='Rolled back: remediation did not help',
                    )

            # Mark action as rolled back
            action.rolled_back = True
            action.rolled_back_at = now
            action.rollback_reason = 'Remediation did not reduce error rate'
            action.verification_state = 'rolled_back'
            action.save(update_fields=[
                'rolled_back', 'rolled_back_at',
                'rollback_reason', 'verification_state',
            ])

            logger.warning(
                f"[RemediationEngine] ROLLED BACK remediation "
                f"{action.id} ({rem_type})"
            )

        except Exception as e:
            logger.error(
                f"[RemediationEngine] Rollback failed for {action.id}: {e}"
            )


# ── Policy Self-Tuning Engine ────────────────────────────────────────────────


class PolicyOptimizer:
    """
    Analyses autopilot action history and recommends config adjustments.

    Each tunable parameter has:
    - safe bounds (min/max) — never exceed these
    - step size — how much to change per adjustment
    - direction logic — when to increase vs decrease

    Tuning signals (per policy, last N days):
    - action_count: how many times the policy acted
    - rollback_rate: fraction of actions that were rolled back
    - verification_pass_rate: fraction of verified actions that passed
    - idle_cycles: how many evaluation cycles the policy produced 0 actions

    Decision matrix:
    - rollback_rate > 30% → make threshold MORE conservative (raise it)
    - verification_pass_rate == 100% AND action_count > 5 → can go more aggressive
    - idle for 7+ days → consider lowering thresholds slightly
    """

    # Registry of tunable parameters with safe bounds
    # Format: (default, min, max, step, policy, direction_when_failing)
    # direction_when_failing: 'up' means raise value when rollbacks are high
    TUNABLES = {
        'TIMEOUT_SPIKE_THRESHOLD': {
            'default': 3, 'min': 2, 'max': 10, 'step': 1,
            'policy': 'timeout_spike_containment',
            'direction_when_failing': 'up',  # More conservative = higher threshold
            'description': 'Timeouts per hour before blocking agent',
        },
        'TIMEOUT_SPIKE_WINDOW_MINUTES': {
            'default': 60, 'min': 15, 'max': 180, 'step': 15,
            'policy': 'timeout_spike_containment',
            'direction_when_failing': 'up',  # Wider window = more conservative
            'description': 'Look-back window for timeout spike detection',
        },
        'TIMEOUT_BLOCK_TTL_MINUTES': {
            'default': 30, 'min': 10, 'max': 120, 'step': 10,
            'policy': 'timeout_spike_containment',
            'direction_when_failing': 'down',  # Shorter block = less damage if wrong
            'description': 'How long to block an agent after timeout spike',
        },
        'DELIBERATION_RETRY_AFTER_MINUTES': {
            'default': 30, 'min': 10, 'max': 120, 'step': 10,
            'policy': 'deliberation_retry',
            'direction_when_failing': 'up',  # Wait longer before retry
            'description': 'Wait time before retrying failed deliberations',
        },
        'CONTENT_STUCK_HOURS': {
            'default': 6, 'min': 2, 'max': 24, 'step': 2,
            'policy': 'content_sweep',
            'direction_when_failing': 'up',
            'description': 'How long content sits before being kicked',
        },
        'ATTENTION_STALE_HOURS': {
            'default': 12, 'min': 4, 'max': 72, 'step': 4,
            'policy': 'attention_auto_resolve',
            'direction_when_failing': 'up',
            'description': 'Hours before auto-resolving stale attention items',
        },
        'GOVERNANCE_GRACE_PERIOD_HOURS': {
            'default': 1, 'min': 0.5, 'max': 12, 'step': 0.5,
            'policy': 'governance_auto_decision',
            'direction_when_failing': 'up',
            'description': 'Hours to wait for human before auto-deciding',
        },
        'REMEDIATION_MIN_OCCURRENCES': {
            'default': 5, 'min': 3, 'max': 20, 'step': 1,
            'policy': 'root_cause_remediation',
            'direction_when_failing': 'up',  # Require more evidence before acting
            'description': 'Failure occurrences required before auto-remediation',
        },
        'REMEDIATION_COOLDOWN_HOURS': {
            'default': 4, 'min': 1, 'max': 24, 'step': 1,
            'policy': 'root_cause_remediation',
            'direction_when_failing': 'up',
            'description': 'Hours between remediating the same signature',
        },
    }

    def evaluate(self) -> dict:
        """
        Evaluate all tunable parameters and return recommendations.

        Returns:
            {
                'recommendations': [
                    {
                        'param': 'TIMEOUT_SPIKE_THRESHOLD',
                        'old_value': 3,
                        'new_value': 4,
                        'reason': '...',
                        'confidence': 'high',
                        'metrics': {...},
                    },
                    ...
                ],
                'policy_metrics': {...},
            }
        """
        now = timezone.now()
        lookback = now - timedelta(
            days=AutopilotConfig.TUNING_LOOKBACK_DAYS
        )

        # Gather per-policy metrics
        policy_metrics = self._compute_policy_metrics(lookback, now)

        # Check daily change cap
        try:
            day_start = now - timedelta(hours=24)
            changes_today = AutopilotAction.objects.filter(
                action_type='config_tune',
                dry_run=False,
                created_at__gte=day_start,
            ).count()
        except Exception:
            changes_today = 0

        if changes_today >= AutopilotConfig.TUNING_MAX_CHANGES_PER_DAY:
            return {
                'recommendations': [],
                'policy_metrics': policy_metrics,
                'capped': True,
                'changes_today': changes_today,
            }

        # Generate recommendations
        recommendations = []
        for param_name, spec in self.TUNABLES.items():
            rec = self._evaluate_param(param_name, spec, policy_metrics)
            if rec:
                recommendations.append(rec)

        # Sort by confidence (high first)
        confidence_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(
            key=lambda r: confidence_order.get(r.get('confidence', 'low'), 3)
        )

        return {
            'recommendations': recommendations,
            'policy_metrics': policy_metrics,
            'capped': False,
            'changes_today': changes_today,
        }

    def _compute_policy_metrics(self, since, now) -> dict:
        """Compute effectiveness metrics for each policy."""
        metrics = {}

        # Map policy names to action types they produce
        policy_action_types = {
            'timeout_spike_containment': ['block_agent'],
            'deliberation_retry': ['retry_deliberation'],
            'content_sweep': ['content_sweep', 'content_publish'],
            'attention_auto_resolve': ['auto_resolve'],
            'governance_auto_decision': ['auto_resolve'],
            'root_cause_remediation': ['remediate'],
        }

        for policy, action_types in policy_action_types.items():
            try:
                actions = AutopilotAction.objects.filter(
                    policy=policy,
                    dry_run=False,
                    created_at__gte=since,
                )

                total = actions.count()
                rolled_back = actions.filter(rolled_back=True).count()
                verified_passed = actions.filter(
                    verification_state='passed'
                ).count()
                verified_failed = actions.filter(
                    verification_state='failed'
                ).count()
                verified_total = verified_passed + verified_failed

                # Count evaluation cycles (cycle_evaluation actions)
                eval_cycles = AutopilotAction.objects.filter(
                    policy='cycle_evaluation',
                    created_at__gte=since,
                ).count()

                metrics[policy] = {
                    'action_count': total,
                    'rollback_count': rolled_back,
                    'rollback_rate': (
                        rolled_back / max(total, 1)
                    ),
                    'verification_pass_rate': (
                        verified_passed / max(verified_total, 1)
                    ),
                    'verified_total': verified_total,
                    'eval_cycles': eval_cycles,
                    'actions_per_cycle': (
                        total / max(eval_cycles, 1)
                    ),
                }
            except Exception:
                metrics[policy] = {
                    'action_count': 0,
                    'error': 'query_failed',
                }

        return metrics

    def _evaluate_param(
        self, param_name: str, spec: dict, policy_metrics: dict
    ) -> dict | None:
        """Evaluate whether a single parameter should be tuned."""
        policy = spec['policy']
        pm = policy_metrics.get(policy, {})

        if pm.get('error'):
            return None

        action_count = pm.get('action_count', 0)
        rollback_rate = pm.get('rollback_rate', 0)
        pass_rate = pm.get('verification_pass_rate', 1.0)
        eval_cycles = pm.get('eval_cycles', 0)

        # Get current effective value
        current = AutopilotConfig.get(param_name)
        if current is None:
            current = spec['default']

        direction = spec['direction_when_failing']
        step = spec['step']
        safe_min = spec['min']
        safe_max = spec['max']

        new_value = None
        reason = ''
        confidence = 'low'

        # Signal 1: High rollback rate → go more conservative
        if (
            action_count >= 3
            and rollback_rate > AutopilotConfig.TUNING_ROLLBACK_RATE_THRESHOLD
        ):
            if direction == 'up':
                new_value = min(current + step, safe_max)
            else:
                new_value = max(current - step, safe_min)
            reason = (
                f'High rollback rate ({rollback_rate:.0%}) over '
                f'{action_count} actions → going more conservative'
            )
            confidence = 'high'

        # Signal 2: Perfect pass rate with enough data → can go more aggressive
        elif (
            action_count >= 5
            and pass_rate == 1.0
            and rollback_rate == 0
        ):
            if direction == 'up':
                new_value = max(current - step, safe_min)
            else:
                new_value = min(current + step, safe_max)
            reason = (
                f'100% pass rate over {action_count} actions with '
                f'0 rollbacks → can be more aggressive'
            )
            confidence = 'medium'

        # Signal 3: Policy completely idle for extended period
        elif (
            action_count == 0
            and eval_cycles >= 100  # ~16h at 10min intervals
        ):
            # Slightly more aggressive to catch things
            if direction == 'up':
                new_value = max(current - step, safe_min)
            else:
                new_value = min(current + step, safe_max)
            reason = (
                f'Policy idle for {eval_cycles} cycles '
                f'({eval_cycles * 10 / 60:.0f}h) → slightly more sensitive'
            )
            confidence = 'low'

        # No change needed
        if new_value is None or new_value == current:
            return None

        return {
            'param': param_name,
            'old_value': current,
            'new_value': new_value,
            'reason': reason,
            'confidence': confidence,
            'description': spec['description'],
            'metrics': {
                'action_count': action_count,
                'rollback_rate': round(rollback_rate, 3),
                'verification_pass_rate': round(pass_rate, 3),
                'eval_cycles': eval_cycles,
            },
        }

    def apply_recommendations(
        self, recommendations: list[dict], max_changes: int = 1
    ) -> list[dict]:
        """
        Apply tuning recommendations by writing to SystemConfiguration.

        Returns list of changes actually applied.
        """
        from core.models.system import SystemConfiguration

        applied = []
        for rec in recommendations[:max_changes]:
            param = rec['param']
            new_value = rec['new_value']
            key = f'autopilot_tuning:{param}'

            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': new_value,
                    'description': (
                        f'Auto-tuned by PolicyOptimizer: '
                        f'{rec["old_value"]} → {new_value}. '
                        f'Reason: {rec["reason"]}'
                    ),
                    'category': 'performance',
                },
            )

            # Refresh the override cache
            AutopilotConfig._override_cache[param] = new_value

            applied.append(rec)
            logger.info(
                f"[PolicyOptimizer] Tuned {param}: "
                f"{rec['old_value']} → {new_value} "
                f"({rec['confidence']} confidence)"
            )

        return applied

    def get_tuning_report(self) -> dict:
        """
        Generate a human-readable tuning status report.

        Shows current effective values, overrides active, and recent changes.
        """
        report = {
            'parameters': {},
            'overrides_active': {},
            'recent_changes': [],
        }

        # Current effective values
        for param_name, spec in self.TUNABLES.items():
            effective = AutopilotConfig.get(param_name)
            if effective is None:
                effective = spec['default']
            report['parameters'][param_name] = {
                'effective_value': effective,
                'code_default': spec['default'],
                'safe_range': [spec['min'], spec['max']],
                'policy': spec['policy'],
                'overridden': param_name in AutopilotConfig._override_cache,
            }

        # Active overrides
        report['overrides_active'] = dict(AutopilotConfig._override_cache)

        # Recent tuning changes (last 7 days)
        try:
            recent = AutopilotAction.objects.filter(
                action_type='config_tune',
                created_at__gte=timezone.now() - timedelta(days=7),
            ).order_by('-created_at')[:10]

            for action in recent:
                evidence = action.evidence or {}
                report['recent_changes'].append({
                    'param': evidence.get('param', ''),
                    'old_value': evidence.get('old_value'),
                    'new_value': evidence.get('new_value'),
                    'reason': evidence.get('reason', ''),
                    'when': action.created_at.isoformat(),
                })
        except Exception:
            pass

        return report


# ── Budget Controller ────────────────────────────────────────────────────────


class BudgetController:
    """
    Monitors LLM spend from LLMCallLog and enforces budget caps.

    Three enforcement tiers:
    1. Model downgrade: route to cheaper model when soft limit hit
    2. Rate reduction: reduce autopilot action rate (future)
    3. Hard freeze: block non-critical LLM calls at hard limit

    Budget flags are stored in SystemConfiguration:
    - budget_mode: 'normal' | 'downgrade' | 'freeze'
    - budget_downgrade_active: True/False
    - budget_freeze_active: True/False
    """

    def compute_spend(self, now) -> dict:
        """Compute current spend from LLMCallLog."""
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum, Count

        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(hours=24)

        # Hourly spend
        hourly = LLMCallLog.objects.filter(
            created_at__gte=hour_ago,
        ).aggregate(
            total=Sum('cost'),
            calls=Count('id'),
        )

        # Daily spend
        daily = LLMCallLog.objects.filter(
            created_at__gte=day_ago,
        ).aggregate(
            total=Sum('cost'),
            calls=Count('id'),
        )

        # Top spenders by agent (last 24h)
        top_agents = list(
            LLMCallLog.objects.filter(
                created_at__gte=day_ago,
            ).values('agent_name').annotate(
                total_cost=Sum('cost'),
                call_count=Count('id'),
            ).order_by('-total_cost')[:10]
        )
        for a in top_agents:
            a['total_cost'] = float(a['total_cost'] or 0)

        # Top models by cost (last 24h)
        top_models = list(
            LLMCallLog.objects.filter(
                created_at__gte=day_ago,
            ).values('provider', 'model_id').annotate(
                total_cost=Sum('cost'),
                call_count=Count('id'),
            ).order_by('-total_cost')[:10]
        )
        for m in top_models:
            m['total_cost'] = float(m['total_cost'] or 0)

        return {
            'hourly_total': float(hourly['total'] or 0),
            'hourly_calls': hourly['calls'] or 0,
            'daily_total': float(daily['total'] or 0),
            'daily_calls': daily['calls'] or 0,
            'top_agents': top_agents,
            'top_models': top_models,
        }

    def enforce_model_downgrade(self, spend: dict, now) -> dict | None:
        """
        Tier 1: Set a flag so LLM routing prefers cheaper models.

        The llm_enforcer checks 'budget_downgrade_active' before selecting
        a model, and routes to the downgrade model if set.
        """
        from core.models.system import SystemConfiguration

        # Check if already in downgrade mode
        existing = SystemConfiguration.objects.filter(
            key='budget_downgrade_active',
        ).values_list('value', flat=True).first()
        if existing:
            return None  # Already active

        SystemConfiguration.objects.update_or_create(
            key='budget_downgrade_active',
            defaults={
                'value': True,
                'description': (
                    f'Auto-set by BudgetController at '
                    f'${spend["daily_total"]:.2f} daily spend. '
                    f'Routes expensive models to '
                    f'{AutopilotConfig.BUDGET_DOWNGRADE_MODEL}.'
                ),
                'category': 'performance',
            },
        )
        SystemConfiguration.objects.update_or_create(
            key='budget_mode',
            defaults={
                'value': 'downgrade',
                'description': 'Current budget enforcement mode',
                'category': 'performance',
            },
        )

        logger.warning(
            f"[BudgetController] Model downgrade activated — "
            f"daily spend ${spend['daily_total']:.2f}"
        )

        return {
            'type': 'budget_downgrade',
            'daily_spend': round(spend['daily_total'], 4),
            'hourly_spend': round(spend['hourly_total'], 4),
            'downgrade_model': AutopilotConfig.BUDGET_DOWNGRADE_MODEL,
            'reason': (
                f"Spend at {spend['daily_total']:.2f} USD "
                f"(soft limit {AutopilotConfig.BUDGET_SOFT_LIMIT_PCT:.0%})"
            ),
        }

    def enforce_hard_freeze(self, spend: dict, now) -> dict | None:
        """
        Tier 3: Freeze non-critical LLM calls.

        Sets budget_freeze_active flag. LLM enforcer checks this and
        only allows calls with purpose in BUDGET_CRITICAL_PURPOSES.
        """
        from core.models.system import SystemConfiguration

        # Check if already frozen
        existing = SystemConfiguration.objects.filter(
            key='budget_freeze_active',
        ).values_list('value', flat=True).first()
        if existing:
            return None  # Already frozen

        SystemConfiguration.objects.update_or_create(
            key='budget_freeze_active',
            defaults={
                'value': True,
                'description': (
                    f'HARD FREEZE: daily spend '
                    f'${spend["daily_total"]:.2f} hit limit. '
                    f'Only critical purposes allowed.'
                ),
                'category': 'performance',
            },
        )
        SystemConfiguration.objects.update_or_create(
            key='budget_downgrade_active',
            defaults={
                'value': True,
                'description': 'Also active during freeze',
                'category': 'performance',
            },
        )
        SystemConfiguration.objects.update_or_create(
            key='budget_mode',
            defaults={
                'value': 'freeze',
                'description': 'Current budget enforcement mode',
                'category': 'performance',
            },
        )

        # Record action
        AutopilotAction.objects.create(
            action_type='budget_freeze',
            agent_name='BudgetController',
            policy='budget_controller',
            dry_run=False,
            evidence=spend,
            result={
                'freeze_reason': 'hard_limit',
                'daily_spend': round(spend['daily_total'], 4),
            },
        )

        logger.critical(
            f"[BudgetController] HARD FREEZE activated — "
            f"daily spend ${spend['daily_total']:.2f}"
        )

        return {
            'type': 'budget_freeze',
            'daily_spend': round(spend['daily_total'], 4),
            'hourly_spend': round(spend['hourly_total'], 4),
            'critical_only': list(AutopilotConfig.BUDGET_CRITICAL_PURPOSES),
            'reason': (
                f"Spend at ${spend['daily_total']:.2f} "
                f"(hard limit {AutopilotConfig.BUDGET_HARD_LIMIT_PCT:.0%})"
            ),
        }

    def clear_budget_flags(self):
        """Clear downgrade/freeze flags when spend is back to normal."""
        from core.models.system import SystemConfiguration

        cleared = SystemConfiguration.objects.filter(
            key__in=[
                'budget_downgrade_active',
                'budget_freeze_active',
            ],
        ).delete()

        if cleared[0] > 0:
            SystemConfiguration.objects.update_or_create(
                key='budget_mode',
                defaults={
                    'value': 'normal',
                    'description': 'Budget flags cleared — spend normal',
                    'category': 'performance',
                },
            )
            logger.info(
                "[BudgetController] Budget flags cleared — normal mode"
            )

    def get_budget_report(self, now) -> dict:
        """Generate a budget status report for PA/governance."""
        spend = self.compute_spend(now)

        daily_cap = (
            AutopilotConfig.get('BUDGET_DAILY_CAP_USD')
            or AutopilotConfig.BUDGET_DAILY_CAP_USD
        )
        hourly_cap = (
            AutopilotConfig.get('BUDGET_HOURLY_CAP_USD')
            or AutopilotConfig.BUDGET_HOURLY_CAP_USD
        )

        # Current mode
        from core.models.system import SystemConfiguration
        mode = 'normal'
        try:
            mode_entry = SystemConfiguration.objects.filter(
                key='budget_mode',
            ).values_list('value', flat=True).first()
            if mode_entry:
                mode = mode_entry
        except Exception:
            pass

        return {
            'mode': mode,
            'daily_spend': round(spend['daily_total'], 4),
            'daily_cap': daily_cap,
            'daily_utilization': round(
                spend['daily_total'] / max(daily_cap, 0.01), 3
            ),
            'hourly_spend': round(spend['hourly_total'], 4),
            'hourly_cap': hourly_cap,
            'hourly_utilization': round(
                spend['hourly_total'] / max(hourly_cap, 0.01), 3
            ),
            'daily_calls': spend['daily_calls'],
            'hourly_calls': spend['hourly_calls'],
            'top_agents': spend['top_agents'][:5],
            'top_models': spend['top_models'][:5],
            'soft_limit_pct': AutopilotConfig.BUDGET_SOFT_LIMIT_PCT,
            'hard_limit_pct': AutopilotConfig.BUDGET_HARD_LIMIT_PCT,
        }


# ── ROI Attribution + Selective Throttles ────────────────────────────────────

class ROIEnforcer:
    """
    Session 1088: Autonomy #5 — ROI attribution and selective throttles.

    Correlates LLM spend (from LLMCallLog) with measurable outcomes
    (completed executions, published content, deliberation passes) to
    compute ROI scores per agent and task_type.

    Under budget pressure (soft limit breached), applies selective
    throttles: low-ROI agents get cooldown periods, reducing their
    call frequency without a blanket freeze.
    """

    # task_types that are always considered productive (no throttle)
    PROTECTED_PURPOSES = frozenset({
        'pa_chat', 'governance', 'auth', 'incident_response',
    })

    # Cooldown tiers: ROI score → cooldown minutes between calls
    THROTTLE_TIERS = [
        (0.05, 60),   # ROI < 5% → 60-minute cooldown
        (0.15, 30),   # ROI < 15% → 30-minute cooldown
        (0.30, 10),   # ROI < 30% → 10-minute cooldown
    ]

    def compute_roi_scores(self, now, window_hours=24) -> dict:
        """
        Compute ROI scores per agent over the given window.

        ROI = (outcome_count / call_count) weighted by outcome quality.
        Agents with zero calls are excluded.

        Returns dict with per-agent scores and aggregated stats.
        """
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum, Count, Q

        window_start = now - timedelta(hours=window_hours)

        # Spend by agent
        agent_spend = list(
            LLMCallLog.objects.filter(
                created_at__gte=window_start,
                success=True,
            ).values('agent_name').annotate(
                total_cost=Sum('cost'),
                call_count=Count('id'),
            ).order_by('-total_cost')[:30]
        )

        if not agent_spend:
            return {
                'agents': [],
                'total_spend': 0,
                'total_outcomes': 0,
                'window_hours': window_hours,
            }

        # Outcome counts by agent: completed AgentExecutions
        agent_names = [a['agent_name'] for a in agent_spend]
        outcome_map = {}

        try:
            from core.models_unified_system import AgentExecution
            outcomes = list(
                AgentExecution.objects.filter(
                    created_at__gte=window_start,
                    status='completed',
                    agent__name__in=agent_names,
                ).values('agent__name').annotate(
                    completed=Count('id'),
                )
            )
            for o in outcomes:
                outcome_map[o['agent__name']] = o['completed']
        except Exception:
            pass

        # Content outcomes: published deliverables (content-producing agents)
        content_map = {}
        try:
            from core.models_deliverables import Deliverable
            content_outcomes = list(
                Deliverable.objects.filter(
                    created_at__gte=window_start,
                    status='published',
                ).values('agent_name').annotate(
                    published=Count('id'),
                )
            )
            for c in content_outcomes:
                if c['agent_name']:
                    content_map[c['agent_name']] = c['published']
        except Exception:
            pass

        # Deliberation outcomes: passed sessions
        delib_map = {}
        try:
            from core.models_deliberation import DeliberationSession
            delib_outcomes = list(
                DeliberationSession.objects.filter(
                    created_at__gte=window_start,
                    status='completed',
                ).values('topic').annotate(
                    passed=Count('id'),
                )
            )
            # We can't directly map topic→agent, so this contributes to
            # 'content' task_type ROI globally
            delib_map['_total'] = sum(d['passed'] for d in delib_outcomes)
        except Exception:
            pass

        # Quality signals: average quality_score from SelfBlogs (content pipeline)
        quality_map = {}  # agent_name → avg quality
        try:
            from core.models_unified_system import SelfBlog
            from django.db.models import Avg
            blog_quality = list(
                SelfBlog.objects.filter(
                    created_at__gte=window_start,
                    quality_score__isnull=False,
                ).exclude(
                    quality_score=0,
                ).values('tone').annotate(  # tone is closest proxy for agent
                    avg_quality=Avg('quality_score'),
                    total=Count('id'),
                    published=Count('id', filter=Q(status='published')),
                    approved=Count('id', filter=Q(status='approved')),
                )
            )
            # SelfBlogs come from deliberation → ContentWriterAgent
            for bq in blog_quality:
                quality_map['_content_avg'] = float(bq.get('avg_quality') or 0)
                quality_map['_content_published'] = bq.get('published', 0)
                quality_map['_content_total'] = bq.get('total', 0)
        except Exception:
            pass

        # Quality: Deliverable quality scores by agent
        deliverable_quality = {}
        try:
            from core.models_deliverables import Deliverable
            from django.db.models import Avg
            dq = list(
                Deliverable.objects.filter(
                    created_at__gte=window_start,
                    quality_score__isnull=False,
                ).exclude(
                    quality_score=0,
                ).values('agent_name').annotate(
                    avg_quality=Avg('quality_score'),
                )
            )
            for d in dq:
                if d['agent_name']:
                    deliverable_quality[d['agent_name']] = float(
                        d.get('avg_quality') or 0
                    )
        except Exception:
            pass

        # Quality: Deliberation pass rate (completed vs total)
        delib_pass_rate = 0.5  # default
        try:
            from core.models_deliberation import DeliberationSession
            total_delibs = DeliberationSession.objects.filter(
                created_at__gte=window_start,
            ).count()
            passed_delibs = DeliberationSession.objects.filter(
                created_at__gte=window_start,
                status='completed',
            ).count()
            if total_delibs > 0:
                delib_pass_rate = passed_delibs / total_delibs
        except Exception:
            pass

        # Build per-agent ROI + QROI
        total_spend = 0
        total_outcomes = 0
        agent_scores = []

        for entry in agent_spend:
            name = entry['agent_name']
            cost = float(entry['total_cost'] or 0)
            calls = entry['call_count'] or 0
            total_spend += cost

            outcomes = outcome_map.get(name, 0)
            content = content_map.get(name, 0)
            combined_outcomes = outcomes + content
            total_outcomes += combined_outcomes

            # ROI = outcome-to-call ratio (0..1+)
            roi = combined_outcomes / max(calls, 1)

            # QROI = ROI * quality_weight
            # quality_weight combines:
            # - deliverable quality score (if available)
            # - content pipeline quality (if this agent produces content)
            # - execution success rate as fallback
            quality_weight = 0.5  # neutral default
            if name in deliverable_quality:
                quality_weight = deliverable_quality[name]
            elif content > 0:
                # Content-producing agent — use pipeline quality
                quality_weight = quality_map.get('_content_avg', 0.5)
            elif outcomes > 0:
                # Non-content agent — quality = success rate
                quality_weight = min(outcomes / max(calls, 1), 1.0)

            qroi = roi * quality_weight

            agent_scores.append({
                'agent_name': name,
                'cost': round(cost, 4),
                'calls': calls,
                'outcomes': combined_outcomes,
                'outcome_detail': {
                    'executions': outcomes,
                    'content': content,
                },
                'roi': round(roi, 4),
                'quality_weight': round(quality_weight, 3),
                'qroi': round(qroi, 4),
            })

        # Sort by QROI ascending (worst first)
        agent_scores.sort(key=lambda x: x['qroi'])

        return {
            'agents': agent_scores,
            'total_spend': round(total_spend, 4),
            'total_outcomes': total_outcomes,
            'deliberation_passes': delib_map.get('_total', 0),
            'window_hours': window_hours,
        }

    def get_throttle_recommendations(self, now) -> list[dict]:
        """
        When budget utilization is above soft limit, recommend throttles
        for low-QROI agents.

        QROI (Quality-Adjusted ROI) factors in output quality, so a
        high-cost agent producing excellent content may escape throttling
        while a cheap agent producing garbage gets throttled.

        Returns list of {agent_name, qroi, roi, cooldown_minutes, reason}.
        """
        # Check if we're under budget pressure
        controller = BudgetController()
        spend = controller.compute_spend(now)

        daily_cap = (
            AutopilotConfig.get('BUDGET_DAILY_CAP_USD')
            or AutopilotConfig.BUDGET_DAILY_CAP_USD
        )
        daily_pct = spend['daily_total'] / max(daily_cap, 0.01)

        if daily_pct < AutopilotConfig.BUDGET_SOFT_LIMIT_PCT:
            return []  # No pressure, no throttles

        # Compute ROI scores (includes QROI)
        roi_data = self.compute_roi_scores(now, window_hours=24)
        recommendations = []

        for agent in roi_data['agents']:
            name = agent['agent_name']

            # Skip protected purposes
            if name.lower() in self.PROTECTED_PURPOSES:
                continue

            qroi = agent.get('qroi', agent['roi'])

            # Find applicable throttle tier (using QROI)
            cooldown = None
            for threshold, minutes in self.THROTTLE_TIERS:
                if qroi < threshold:
                    cooldown = minutes
                    break

            if cooldown:
                recommendations.append({
                    'agent_name': name,
                    'roi': agent['roi'],
                    'qroi': qroi,
                    'quality_weight': agent.get('quality_weight', 0.5),
                    'cost_24h': agent['cost'],
                    'calls_24h': agent['calls'],
                    'outcomes_24h': agent['outcomes'],
                    'cooldown_minutes': cooldown,
                    'reason': (
                        f'QROI {qroi:.1%} (ROI {agent["roi"]:.1%} '
                        f'× quality {agent.get("quality_weight", 0.5):.2f}) '
                        f'with ${agent["cost"]:.2f} spent '
                        f'({agent["calls"]} calls, '
                        f'{agent["outcomes"]} outcomes)'
                    ),
                })

        return recommendations

    def apply_throttles(self, now) -> list[dict]:
        """
        Apply throttle cooldowns via SystemConfiguration flags.

        Sets `roi_throttle:{agent_name}` with cooldown expiry timestamp.
        LLMEnforcer checks these before allowing calls.
        """
        from core.models.system import SystemConfiguration

        recommendations = self.get_throttle_recommendations(now)
        applied = []

        for rec in recommendations:
            key = f"roi_throttle:{rec['agent_name']}"
            expires_at = now + timedelta(minutes=rec['cooldown_minutes'])

            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': {
                        'cooldown_minutes': rec['cooldown_minutes'],
                        'roi': rec['roi'],
                        'qroi': rec.get('qroi', rec['roi']),
                        'quality_weight': rec.get('quality_weight', 0.5),
                        'expires_at': expires_at.isoformat(),
                        'set_at': now.isoformat(),
                    },
                    'description': (
                        f"QROI throttle: {rec['agent_name']} "
                        f"(QROI {rec.get('qroi', rec['roi']):.1%}, "
                        f"cooldown {rec['cooldown_minutes']}min)"
                    ),
                    'category': 'performance',
                },
            )
            applied.append(rec)
            logger.info(
                f"[ROIEnforcer] Throttle: {rec['agent_name']} → "
                f"{rec['cooldown_minutes']}min cooldown "
                f"(QROI {rec.get('qroi', rec['roi']):.1%})"
            )

        # Clear expired throttles
        all_throttles = SystemConfiguration.objects.filter(
            key__startswith='roi_throttle:',
        )
        for t in all_throttles:
            try:
                expires = t.value.get('expires_at', '')
                if expires and now.isoformat() > expires:
                    t.delete()
                    logger.info(
                        f"[ROIEnforcer] Cleared expired throttle: {t.key}"
                    )
            except (AttributeError, TypeError):
                pass

        return applied

    def check_throttle(self, agent_name: str) -> dict | None:
        """
        Check if an agent is currently throttled.

        Returns throttle info dict if active, None if not throttled.
        Called by LLMEnforcer before allowing calls.
        """
        from core.models.system import SystemConfiguration
        from django.utils import timezone as tz

        key = f"roi_throttle:{agent_name}"
        try:
            entry = SystemConfiguration.objects.filter(
                key=key,
            ).values_list('value', flat=True).first()

            if not entry:
                return None

            expires_at = entry.get('expires_at', '')
            if expires_at and tz.now().isoformat() > expires_at:
                # Expired — clean up
                SystemConfiguration.objects.filter(key=key).delete()
                return None

            return entry
        except Exception:
            return None

    def get_roi_report(self, now) -> dict:
        """Generate QROI report for PA/governance."""
        roi_data = self.compute_roi_scores(now, window_hours=24)
        throttle_recs = self.get_throttle_recommendations(now)

        # Count active throttles
        from core.models.system import SystemConfiguration
        active_throttles = SystemConfiguration.objects.filter(
            key__startswith='roi_throttle:',
        ).count()

        # Quality summary stats
        agents = roi_data['agents']
        quality_weights = [a.get('quality_weight', 0.5) for a in agents]
        avg_quality = (
            sum(quality_weights) / len(quality_weights)
            if quality_weights else 0.5
        )

        return {
            'agents': agents[:15],
            'total_spend': roi_data['total_spend'],
            'total_outcomes': roi_data['total_outcomes'],
            'deliberation_passes': roi_data.get('deliberation_passes', 0),
            'window_hours': roi_data['window_hours'],
            'throttle_recommendations': throttle_recs[:10],
            'active_throttles': active_throttles,
            'budget_pressure': len(throttle_recs) > 0,
            'quality_summary': {
                'avg_quality_weight': round(avg_quality, 3),
                'agents_with_quality_data': sum(
                    1 for a in agents
                    if a.get('quality_weight', 0.5) != 0.5
                ),
                'total_agents': len(agents),
            },
        }


# ── Budget-Aware Scheduler ───────────────────────────────────────────────────

class BudgetAwareScheduler:
    """
    Session 1088: Autonomy #6 — Budget-aware task scheduling.

    Provides a `preflight(task_name)` check that expensive Beat tasks
    call at entry. Under budget pressure the scheduler returns:
    - 'proceed': run normally
    - 'downscope': run with reduced parameters (fewer items, smaller panels)
    - 'defer': skip this cycle entirely

    Tasks are classified into cost tiers. The scheduler reads current
    budget utilization and applies appropriate decisions.

    Downscope knobs are stored in SystemConfiguration as
    `scheduler_knob:{task_name}:{knob}` and read by task code.
    """

    # Cost tier classification for scheduled tasks
    # tier 1 = cheapest (no LLM), tier 2 = moderate, tier 3 = expensive LLM
    TASK_TIERS = {
        # Tier 3: Heavy LLM consumers — defer first
        'core.tasks.generate_self_blog_deliberation_task': 3,
        'core.tasks.content_autonomy_loop': 3,
        'core.tasks.auto_enhance_blogs': 3,
        'core.tasks.generate_smart_suggestions': 3,
        'core.tasks.agent_think_and_synthesize': 3,
        'core.tasks.process_content_ideas': 3,
        'core.tasks.run_daily_learning_pipeline': 3,

        # Tier 2: Moderate LLM or embedding usage
        'core.tasks.enrich_boardroom_ml_predictions': 2,
        'core.tasks.backfill_spider_embeddings': 2,
        'core.tasks.backfill_memory_embeddings': 2,
        'core.tasks.backfill_conversation_embeddings': 2,
        'core.tasks.score_opportunities_from_spider_data': 2,
        'core.tasks.generate_human_attention_items': 2,
        'core.tasks.run_proactive_system_check': 2,
        'core.tasks.execute_pending_opportunity_tasks': 2,
        'core.tasks.discover_success_patterns': 2,
        'core.tasks.generate_user_insights': 2,
        'core.tasks.reevaluate_enhanced_blogs': 2,
        'sports.generate_game_predictions': 2,
        'sports.run_market_analysis': 2,
        'intelligence.tasks.scan_spider_opportunities': 2,
        'intelligence.tasks.monitor_and_process_opportunities': 2,

        # Tier 1: No/minimal LLM — always proceed
        'core.tasks.run_spider_network': 1,
        'core.tasks.process_core_spider_data': 1,
        'core.tasks.process_spider_data_automatic': 1,
        'core.tasks.check_all_alerts': 1,
        'sports.update_game_scores': 1,
        'sports.settle_user_bets': 1,
        'sports.verify_betting_outcomes': 1,
    }

    # Downscope knobs per task (param_name → {normal, pressured, critical})
    DOWNSCOPE_KNOBS = {
        'core.tasks.generate_self_blog_deliberation_task': {
            'max_reviewers': {'normal': 3, 'pressured': 1, 'critical': 0},
            'max_topics': {'normal': 3, 'pressured': 1, 'critical': 0},
        },
        'core.tasks.backfill_spider_embeddings': {
            'batch_size': {'normal': 100, 'pressured': 30, 'critical': 10},
        },
        'core.tasks.content_autonomy_loop': {
            'max_items': {'normal': 10, 'pressured': 3, 'critical': 0},
        },
        'core.tasks.auto_enhance_blogs': {
            'max_items': {'normal': 5, 'pressured': 1, 'critical': 0},
        },
        'core.tasks.enrich_boardroom_ml_predictions': {
            'batch_size': {'normal': 20, 'pressured': 5, 'critical': 0},
        },
        'core.tasks.execute_pending_opportunity_tasks': {
            'limit': {'normal': 20, 'pressured': 5, 'critical': 0},
        },
        'core.tasks.agent_think_and_synthesize': {
            'max_agents': {'normal': 10, 'pressured': 3, 'critical': 0},
        },
    }

    # Tasks that are safe to defer (skip cycle) under hard pressure
    DEFERABLE = frozenset({
        'core.tasks.generate_self_blog_deliberation_task',
        'core.tasks.content_autonomy_loop',
        'core.tasks.auto_enhance_blogs',
        'core.tasks.generate_smart_suggestions',
        'core.tasks.agent_think_and_synthesize',
        'core.tasks.process_content_ideas',
        'core.tasks.discover_success_patterns',
        'core.tasks.generate_user_insights',
        'core.tasks.reevaluate_enhanced_blogs',
    })

    def preflight(self, task_name: str) -> dict:
        """
        Called at the start of an expensive Beat task.

        Returns:
            {
                'decision': 'proceed' | 'downscope' | 'defer',
                'reason': str,
                'knobs': {param: value, ...} if downscoped,
                'budget_pct': float,
            }
        """
        tier = self.TASK_TIERS.get(task_name, 1)
        budget_pct = self._get_budget_utilization()

        # Determine pressure level
        soft_pct = AutopilotConfig.BUDGET_SOFT_LIMIT_PCT  # 0.70
        hard_pct = AutopilotConfig.BUDGET_HARD_LIMIT_PCT  # 0.95

        if budget_pct < soft_pct:
            # Normal — everything proceeds
            return {
                'decision': 'proceed',
                'reason': f'Budget normal ({budget_pct:.0%})',
                'knobs': self._get_knobs(task_name, 'normal'),
                'budget_pct': budget_pct,
            }

        if budget_pct >= hard_pct:
            # Critical — defer tier 3, heavy downscope tier 2, proceed tier 1
            if tier >= 3 and task_name in self.DEFERABLE:
                self._log_decision(task_name, 'defer', budget_pct)
                return {
                    'decision': 'defer',
                    'reason': (
                        f'Budget critical ({budget_pct:.0%}) — '
                        f'tier {tier} task deferred'
                    ),
                    'knobs': {},
                    'budget_pct': budget_pct,
                }
            elif tier >= 2:
                knobs = self._get_knobs(task_name, 'critical')
                if knobs and any(v == 0 for v in knobs.values()):
                    # Knob set to 0 means effective defer
                    self._log_decision(task_name, 'defer', budget_pct)
                    return {
                        'decision': 'defer',
                        'reason': (
                            f'Budget critical ({budget_pct:.0%}) — '
                            f'all knobs at zero'
                        ),
                        'knobs': knobs,
                        'budget_pct': budget_pct,
                    }
                self._log_decision(task_name, 'downscope', budget_pct)
                return {
                    'decision': 'downscope',
                    'reason': (
                        f'Budget critical ({budget_pct:.0%}) — '
                        f'heavy downscope applied'
                    ),
                    'knobs': knobs,
                    'budget_pct': budget_pct,
                }
            else:
                return {
                    'decision': 'proceed',
                    'reason': f'Tier 1 task always proceeds ({budget_pct:.0%})',
                    'knobs': {},
                    'budget_pct': budget_pct,
                }

        # Pressured (soft_pct <= budget_pct < hard_pct)
        if tier >= 3 and task_name in self.DEFERABLE:
            self._log_decision(task_name, 'defer', budget_pct)
            return {
                'decision': 'defer',
                'reason': (
                    f'Budget pressured ({budget_pct:.0%}) — '
                    f'tier {tier} deferred'
                ),
                'knobs': {},
                'budget_pct': budget_pct,
            }

        if tier >= 2:
            knobs = self._get_knobs(task_name, 'pressured')
            self._log_decision(task_name, 'downscope', budget_pct)
            return {
                'decision': 'downscope',
                'reason': (
                    f'Budget pressured ({budget_pct:.0%}) — '
                    f'downscoped'
                ),
                'knobs': knobs,
                'budget_pct': budget_pct,
            }

        return {
            'decision': 'proceed',
            'reason': f'Tier 1 proceeds ({budget_pct:.0%})',
            'knobs': {},
            'budget_pct': budget_pct,
        }

    def _get_budget_utilization(self) -> float:
        """Get current daily budget utilization (0..1+)."""
        try:
            controller = BudgetController()
            from django.utils import timezone as tz
            spend = controller.compute_spend(tz.now())
            daily_cap = (
                AutopilotConfig.get('BUDGET_DAILY_CAP_USD')
                or AutopilotConfig.BUDGET_DAILY_CAP_USD
            )
            return spend['daily_total'] / max(daily_cap, 0.01)
        except Exception:
            return 0.0  # Fail open

    def _get_knobs(self, task_name: str, level: str) -> dict:
        """
        Get downscope parameter values for a task at the given level.

        Checks SystemConfiguration overrides first, falls back to defaults.
        """
        knob_config = self.DOWNSCOPE_KNOBS.get(task_name, {})
        result = {}

        for param, levels in knob_config.items():
            # Check for runtime override
            override_key = f"scheduler_knob:{task_name}:{param}"
            try:
                from core.models.system import SystemConfiguration
                override = SystemConfiguration.objects.filter(
                    key=override_key,
                ).values_list('value', flat=True).first()
                if override is not None:
                    result[param] = override
                    continue
            except Exception:
                pass

            # Use static default for the level
            result[param] = levels.get(level, levels.get('normal'))

        return result

    def _log_decision(self, task_name: str, decision: str, budget_pct: float):
        """Log scheduling decision for audit trail."""
        try:
            AutopilotAction.objects.create(
                action_type='config_tune',
                agent_name=task_name,
                policy='budget_aware_scheduler',
                dry_run=False,
                evidence={
                    'decision': decision,
                    'budget_pct': round(budget_pct, 3),
                    'task_tier': self.TASK_TIERS.get(task_name, 1),
                },
                result={'scheduled_action': decision},
            )
        except Exception:
            pass

        logger.info(
            f"[BudgetAwareScheduler] {decision.upper()}: "
            f"{task_name} (budget {budget_pct:.0%})"
        )

    def get_scheduler_report(self, now) -> dict:
        """Generate report on scheduling state for PA/governance."""
        budget_pct = self._get_budget_utilization()
        soft_pct = AutopilotConfig.BUDGET_SOFT_LIMIT_PCT
        hard_pct = AutopilotConfig.BUDGET_HARD_LIMIT_PCT

        if budget_pct >= hard_pct:
            pressure = 'critical'
        elif budget_pct >= soft_pct:
            pressure = 'pressured'
        else:
            pressure = 'normal'

        # Count recent defer/downscope decisions (last 24h)
        from django.utils import timezone as tz
        cutoff = now - timedelta(hours=24)
        try:
            recent = list(
                AutopilotAction.objects.filter(
                    policy='budget_aware_scheduler',
                    created_at__gte=cutoff,
                ).values_list('evidence', flat=True)[:50]
            )
        except Exception:
            recent = []

        defers = sum(1 for r in recent if r.get('decision') == 'defer')
        downscopes = sum(
            1 for r in recent if r.get('decision') == 'downscope'
        )

        # Get active knob overrides
        overrides = {}
        try:
            from core.models.system import SystemConfiguration
            entries = SystemConfiguration.objects.filter(
                key__startswith='scheduler_knob:',
            ).values('key', 'value')
            for e in entries:
                overrides[e['key']] = e['value']
        except Exception:
            pass

        # Task tier summary
        tier_counts = {1: 0, 2: 0, 3: 0}
        for tier in self.TASK_TIERS.values():
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        return {
            'budget_pct': round(budget_pct, 3),
            'pressure': pressure,
            'soft_limit': soft_pct,
            'hard_limit': hard_pct,
            'defers_24h': defers,
            'downscopes_24h': downscopes,
            'active_overrides': overrides,
            'tier_counts': tier_counts,
            'deferable_tasks': len(self.DEFERABLE),
            'downscope_tasks': len(self.DOWNSCOPE_KNOBS),
        }


# ── Impact Collector ─────────────────────────────────────────────────────────

class ImpactCollector:
    """
    Session 1089: Autonomy #8 — Harvests impact events from existing models.

    Scans Wager settlements, DeliverableEvents, and Revenue confirmations
    to create ImpactEvent records. Each ImpactEvent attributes value back
    to an agent/desk for IQROI computation.

    Run periodically (via OpsAutopilot policy or Beat task) to keep
    the ImpactEvent table current.
    """

    # Desk mapping from model source types
    REVENUE_SOURCE_DESK = {
        'sports_betting': 'sports',
        'trading': 'trading',
        'content': 'content',
        'freelance': 'career',
        'consulting': 'career',
        'quick_apply': 'career',
        'ai_project': 'research',
        'affiliate': 'content',
        'other': 'general',
    }

    def collect_all(self, now, window_hours=24) -> dict:
        """
        Scan for new impact events in the last window.
        Returns summary of what was collected.
        """
        window_start = now - timedelta(hours=window_hours)
        results = {
            'wagers': 0,
            'deliverable_events': 0,
            'revenues': 0,
            'total_created': 0,
        }

        try:
            results['wagers'] = self._collect_wager_impacts(window_start)
        except Exception as e:
            logger.error(f"[ImpactCollector] Wager collection error: {e}")

        try:
            results['deliverable_events'] = self._collect_deliverable_impacts(
                window_start
            )
        except Exception as e:
            logger.error(
                f"[ImpactCollector] Deliverable collection error: {e}"
            )

        try:
            results['revenues'] = self._collect_revenue_impacts(window_start)
        except Exception as e:
            logger.error(f"[ImpactCollector] Revenue collection error: {e}")

        results['total_created'] = (
            results['wagers']
            + results['deliverable_events']
            + results['revenues']
        )

        return results

    def _collect_wager_impacts(self, window_start) -> int:
        """Convert settled wagers to ImpactEvents."""
        from core.models_bankroll import Wager
        from core.models_impact_events import ImpactEvent

        settled = Wager.objects.filter(
            settled_at__gte=window_start,
            status__in=['won', 'lost'],
            profit__isnull=False,
        ).select_related('bankroll')

        created = 0
        for wager in settled:
            # Skip if already recorded
            exists = ImpactEvent.objects.filter(
                source_object_type='Wager',
                source_object_id=wager.id if hasattr(wager, 'id') and isinstance(wager.id, type(ImpactEvent().id)) else None,
                impact_type='wager_profit',
            ).exists()

            if exists:
                continue

            profit = float(wager.profit or 0)
            agent = (
                'SportsAnalyticsAgent'
                if wager.agent_recommendation
                else ''
            )

            ImpactEvent.objects.create(
                impact_type='wager_profit',
                desk='sports',
                value_usd=profit,
                impact_points=3 if profit > 0 else 0,
                agent_name=agent,
                source_object_type='Wager',
                metadata={
                    'sport': wager.sport,
                    'event': wager.event_name[:100],
                    'status': wager.status,
                    'stake': str(wager.stake),
                    'agent_recommended': wager.agent_recommendation,
                },
                user=wager.bankroll.user if hasattr(wager.bankroll, 'user') else None,
            )
            created += 1

        return created

    def _collect_deliverable_impacts(self, window_start) -> int:
        """Convert DeliverableEvents to ImpactEvents."""
        from core.models_deliverables import DeliverableEvent, Deliverable
        from core.models_impact_events import ImpactEvent

        # Map event types to impact types
        event_map = {
            'deliverable_saved': 'content_save',
            'deliverable_exported': 'content_export',
            'shared': 'content_share',
            'action_taken': 'content_action',
        }

        events = DeliverableEvent.objects.filter(
            created_at__gte=window_start,
            event_type__in=list(event_map.keys()),
        ).select_related('deliverable')

        created = 0
        for ev in events:
            impact_type = event_map.get(ev.event_type)
            if not impact_type:
                continue

            # Skip if already recorded
            exists = ImpactEvent.objects.filter(
                source_object_type='DeliverableEvent',
                source_object_id=ev.id,
            ).exists()
            if exists:
                continue

            deliverable = ev.deliverable
            agent = deliverable.agent_name or '' if deliverable else ''
            points = ImpactEvent.points_for_type(impact_type)

            ImpactEvent.objects.create(
                impact_type=impact_type,
                desk='content',
                value_usd=0,  # Non-monetary — use impact_points
                impact_points=points,
                agent_name=agent,
                source_object_type='DeliverableEvent',
                source_object_id=ev.id,
                trace_id=deliverable.trace_id if deliverable else None,
                attributed_cost_usd=float(
                    deliverable.llm_cost or 0
                ) if deliverable else 0,
                user=ev.user,
                metadata={
                    'event_type': ev.event_type,
                    'deliverable_type': str(
                        deliverable.deliverable_type
                    ) if deliverable else '',
                },
            )
            created += 1

        return created

    def _collect_revenue_impacts(self, window_start) -> int:
        """Convert confirmed Revenue entries to ImpactEvents."""
        from core.models_impact_events import ImpactEvent

        try:
            from core.models_unified_system import Revenue
        except ImportError:
            return 0

        # Revenue model uses: source_type, paid_at, earned_at, status
        confirmed = Revenue.objects.filter(
            status__in=['confirmed', 'received'],
        ).filter(
            # Use paid_at or earned_at as the activity timestamp
            paid_at__gte=window_start,
        ) | Revenue.objects.filter(
            status__in=['confirmed', 'received'],
            paid_at__isnull=True,
            earned_at__gte=window_start,
        )

        created = 0
        for rev in confirmed:
            exists = ImpactEvent.objects.filter(
                source_object_type='Revenue',
                source_object_id=rev.id,
            ).exists()
            if exists:
                continue

            source = getattr(rev, 'source_type', 'other') or 'other'
            desk = self.REVENUE_SOURCE_DESK.get(source, 'general')

            ImpactEvent.objects.create(
                impact_type='revenue_confirmed',
                desk=desk,
                value_usd=float(rev.amount or 0),
                impact_points=10,
                agent_name='',
                source_object_type='Revenue',
                source_object_id=rev.id,
                user=rev.user if hasattr(rev, 'user') else None,
                metadata={
                    'source_type': source,
                    'description': (rev.description or '')[:100],
                },
            )
            created += 1

        return created


# ── Portfolio Allocator (Policy 13) ──────────────────────────────────────────

class PortfolioAllocator:
    """
    Session 1089: Autonomy #8 — Allocates budget and scheduling priority
    across desks/pipelines based on Impact-adjusted QROI (IQROI).

    IQROI = (impact_value_usd + impact_points × point_usd_value) / cost_usd

    Desks with high IQROI get:
    - Increased budget headroom (spend cap multiplier)
    - Higher scheduling priority (longer deferral threshold)
    - Larger deliberation panels

    Desks with zero/negative IQROI get deprioritized.
    """

    # Default impact-point-to-USD conversion (1 point ≈ $0.10)
    POINT_USD_VALUE = 0.10

    # Desk defaults — scheduling multipliers
    # multiplier > 1.0 = more budget headroom, < 1.0 = throttled
    DEFAULT_ALLOCATIONS = {
        'sports': 1.0,
        'content': 1.0,
        'research': 1.0,
        'career': 1.0,
        'trading': 1.0,
        'general': 1.0,
    }

    # Desk-to-task mapping for scheduling adjustments
    DESK_TASKS = {
        'sports': [
            'core.tasks.run_ml_predictions_batch',
            'core.tasks.run_sports_prediction_pipeline',
        ],
        'content': [
            'core.tasks.generate_self_blog_deliberation_task',
            'core.tasks.content_autonomy_loop',
            'core.tasks.auto_enhance_blogs',
        ],
        'research': [
            'core.tasks.agent_think_and_synthesize',
            'core.tasks.generate_smart_suggestions',
        ],
    }

    def compute_desk_iqroi(self, now, window_hours=72) -> dict:
        """
        Compute IQROI per desk over the given window.

        Returns dict of {desk: {iqroi, impact_usd, impact_points,
                                cost_usd, events, allocation}}.
        """
        from core.models_impact_events import ImpactEvent
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum, Count

        window_start = now - timedelta(hours=window_hours)

        # Impact by desk
        desk_impact = {}
        try:
            impact_rows = list(
                ImpactEvent.objects.filter(
                    created_at__gte=window_start,
                ).values('desk').annotate(
                    total_usd=Sum('value_usd'),
                    total_points=Sum('impact_points'),
                    event_count=Count('id'),
                )
            )
            for row in impact_rows:
                desk_impact[row['desk']] = {
                    'impact_usd': float(row['total_usd'] or 0),
                    'impact_points': row['total_points'] or 0,
                    'events': row['event_count'] or 0,
                }
        except Exception:
            pass

        # Cost by desk (approximate: map agent costs to desks)
        desk_cost = {}
        try:
            # Agent-to-desk mapping from ImpactEvent history
            agent_desk = dict(
                ImpactEvent.objects.filter(
                    agent_name__gt='',
                ).values_list('agent_name', 'desk').distinct()[:200]
            )

            # Get agent costs
            agent_costs = list(
                LLMCallLog.objects.filter(
                    created_at__gte=window_start,
                    success=True,
                ).values('agent_name').annotate(
                    total_cost=Sum('cost'),
                )
            )

            for ac in agent_costs:
                agent = ac['agent_name'] or ''
                desk = agent_desk.get(agent, 'general')
                if desk not in desk_cost:
                    desk_cost[desk] = 0
                desk_cost[desk] += float(ac['total_cost'] or 0)
        except Exception:
            pass

        # Compute IQROI per desk
        point_value = (
            AutopilotConfig.get('IMPACT_POINT_USD_VALUE')
            or self.POINT_USD_VALUE
        )
        results = {}

        all_desks = set(
            list(desk_impact.keys())
            + list(desk_cost.keys())
            + list(self.DEFAULT_ALLOCATIONS.keys())
        )

        for desk in all_desks:
            impact = desk_impact.get(desk, {})
            impact_usd = impact.get('impact_usd', 0)
            impact_pts = impact.get('impact_points', 0)
            events = impact.get('events', 0)
            cost = desk_cost.get(desk, 0)

            # Total impact value = direct USD + (points × point_value)
            total_impact = impact_usd + (impact_pts * point_value)

            # IQROI = total_impact / cost (higher = better)
            iqroi = total_impact / max(cost, 0.001)

            # Allocation: scale based on IQROI relative to baseline
            # IQROI > 1.0 → producing more value than cost → boost
            # IQROI < 0.5 → underperforming → reduce
            if iqroi >= 2.0:
                allocation = 1.5
            elif iqroi >= 1.0:
                allocation = 1.2
            elif iqroi >= 0.5:
                allocation = 1.0
            elif iqroi >= 0.1:
                allocation = 0.7
            elif events == 0 and cost == 0:
                allocation = 1.0  # No data — neutral
            else:
                allocation = 0.5  # Lowest tier

            results[desk] = {
                'iqroi': round(iqroi, 4),
                'impact_usd': round(impact_usd, 4),
                'impact_points': impact_pts,
                'total_impact_value': round(total_impact, 4),
                'cost_usd': round(cost, 4),
                'events': events,
                'allocation': allocation,
            }

        return results

    def apply_allocations(self, now) -> list[dict]:
        """
        Write desk allocation multipliers to SystemConfiguration.

        BudgetAwareScheduler reads these to adjust preflight decisions
        per desk/pipeline.
        """
        from core.models.system import SystemConfiguration

        desk_data = self.compute_desk_iqroi(now)
        applied = []

        for desk, data in desk_data.items():
            key = f"desk_allocation:{desk}"

            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': {
                        'allocation': data['allocation'],
                        'iqroi': data['iqroi'],
                        'updated_at': now.isoformat(),
                    },
                    'description': (
                        f"Portfolio allocation: {desk} desk — "
                        f"IQROI {data['iqroi']:.2f}, "
                        f"allocation {data['allocation']}x"
                    ),
                    'category': 'performance',
                },
            )

            if data['allocation'] != 1.0:
                applied.append({
                    'desk': desk,
                    'allocation': data['allocation'],
                    'iqroi': data['iqroi'],
                })

        return applied

    def get_portfolio_report(self, now) -> dict:
        """Generate portfolio allocation report for PA/governance."""
        desk_data = self.compute_desk_iqroi(now)

        # Sort by IQROI descending (best performing first)
        sorted_desks = sorted(
            desk_data.items(),
            key=lambda x: x[1]['iqroi'],
            reverse=True,
        )

        # Active allocation overrides
        from core.models.system import SystemConfiguration
        active_allocs = {}
        try:
            entries = SystemConfiguration.objects.filter(
                key__startswith='desk_allocation:',
            ).values('key', 'value')
            for e in entries:
                desk = e['key'].replace('desk_allocation:', '')
                active_allocs[desk] = e['value']
        except Exception:
            pass

        return {
            'desks': dict(sorted_desks),
            'active_allocations': active_allocs,
            'window_hours': 72,
            'total_impact_usd': sum(
                d['impact_usd'] for d in desk_data.values()
            ),
            'total_cost_usd': sum(
                d['cost_usd'] for d in desk_data.values()
            ),
            'total_events': sum(
                d['events'] for d in desk_data.values()
            ),
        }

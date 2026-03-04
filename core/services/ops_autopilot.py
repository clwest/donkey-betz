"""
Ops Autopilot v7 — autonomous ops with governance guardrails.

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

Policies (v7 — attribution debt + experiment engine + decision ledger + remediation):
 14. Attribution debt controller: AttributionDebtController maps LLM
     spend to desks via agent→desk lookup. Unattributed spend (agents
     without desk mapping) is "debt" that distorts IQROI. When debt
     exceeds 40% of spend, portfolio reallocation is blocked. When
     debt exceeds 20%, EWMA smoothing is increased to reduce sensitivity.
     Reports top unattributed agents for remediation.
 15. Experiment engine: A/B testing for policy parameters. Creates
     experiments with baseline + treatment params, collects metrics
     (IQROI, debt %, impact USD, publish rate, error rate), auto-promotes
     winners and auto-rollbacks losers. Only one active experiment per
     policy. Supports: portfolio_allocator, roi_throttle, budget_controller.
 16. Decision ledger: Every policy evaluation is recorded as a
     DecisionLedgerEntry with structured inputs, outputs, decision_type,
     and counterfactual context. Grouped by cycle_id for replay and
     debugging. Queryable by policy, desk, decision_type, experiment_id.
 17. Timeout remediation playbook: Graduated remediation ladder for
     agents with sustained timeouts. L0=monitoring, L1=increase timeout
     50%, L2=reduce batch size 50%, L3=temporary block (4h TTL).
     Auto-escalates after 6 cycles without improvement, auto-de-escalates
     after 12 clean cycles. Governance items at L2+.
 18. Deliberation failure remediation: Monitors deliberation session
     failure rate (TIMEOUT, LLM_UPSTREAM, EMPTY_TURN, TOOL_ERROR,
     DRAFT_FAILED). L1=reduce panel (3→2), L2=reviewer model fallback,
     L3=single-reviewer bypass. Auto-escalates when rate >25% for 6
     cycles, de-escalates when rate <10% for 12 cycles.
 19. Backlog governor: Monitors Deliverable backlog KPIs — publish-ready
     count, p95 age hours, draft→published conversion rate. Graduated
     actions: L1=throttle new generation, L2=governance attention batch,
     L3=auto-archive stale drafts (>14d, no engagement). Guardrails:
     never archive pinned, saved, starred, high-quality (>0.7), or
     initiative-linked deliverables.
 20. Goal-aware allocator: Maps system-level objectives (revenue, sports
     profit, content engagement, quality, freshness) to desk-level budget
     multipliers via a weighted utility function. Balanced default weights.
     Desk floors (0.75x) and ceilings (1.25x). Goal weights stored in
     SystemConfiguration and adjustable via PA tool. Modulates existing
     PortfolioAllocator multipliers.
 21. Multi-touch attribution: Allocates ImpactEvent credit across
     upstream agents/desks. 70% last-touch, 30% assist (split among
     upstream links via trace_id, initiative, dream). Max 2 hops,
     max 30% total assist cap. ImpactCredit model for queryable
     credit attribution per desk/agent.
 22. Policy arbitrator: Detects conflicts when multiple policies write
     the same SystemConfiguration knob. Knob registry with priority +
     merge strategy (priority_wins, max, min, bool_or). Anti-flap
     detection (3+ changes in 24h). Hold-time violation reporting.
     FinalAppliedOverrides snapshot per cycle. PA tool: policy_conflict_report.
 23. Release/deploy governor: Monitors Railway deploy health with
     graduated safety ladder. L0=observe (track deploy frequency,
     SHA changes, error rate). L1=backoff (serialize builds, 5min gap).
     L2=gate (require healthy status). L3=freeze (auto-freeze on SLO
     breach). PA tools: release_report, release_freeze/unfreeze.
 24. Revenue pipeline automation: Monitors Opportunity pipeline health.
     Flags stale opportunities (48h no activity), critical stale (7d+),
     high-value opportunities. Generates follow-up suggestions with
     cadence tracking. Guardrails: never auto-send, max 3 follow-ups
     per opp. PA tool: revenue_pipeline_report.
 25. Outbound lead engine: Discovers prospecting leads from SpiderData
     (job postings, startup news, business signals). Scores leads on
     recency, revenue potential, and channel fit. Generates outreach
     drafts (approval required — never auto-sends). Deduplication by
     source_url. Daily rate limit (20 leads/day). Tracks which spider
     sources produce converting leads. PA tools: prospecting_queue,
     lead_source_report.
 26. Outreach sequencer: Manages outreach draft lifecycle — inbox,
     approval, rejection, follow-up timers. Touch cadence: Day 0, 3,
     7, 14. Max 4 touches per lead. Daily approval cap: 10. Generates
     follow-up drafts for approved messages when next_touch_at is due.
     Expires 30-day-old approved drafts with no follow-up. Tracks
     reply rate and conversion funnel. PA tools: outreach_inbox,
     outreach_approve, outreach_reject, outreach_metrics_report.
 27. Close-the-deal engine: Generates deal-closing document bundles
     (ClosePacks) when an opportunity reaches high-intent stage.
     Each pack contains a 1-page proposal, SOW/MSA-lite contract, and
     invoice draft. 4 offer templates: ai_automation, content_engine,
     analytics_dashboard, consulting. Follow-up cadence: 5d, 10d after
     sent. Max 2 follow-ups per pack. Expires sent packs after 30d with
     no response. PA tools: close_pack_generate, close_pack_inbox,
     close_pack_approve, close_pack_metrics_report.

All actions create HumanAttentionItem for governance visibility and are logged
to AutopilotAction for audit trail. Non-trivial actions go through pre-check
→ execute → verify → rollback cycle (ActionVerifier). Successful remediations
are promoted to RemediationPlaybook for future reuse. Config tuning changes
are persisted via SystemConfiguration and always changelog-documented.
"""

import logging
import time
import uuid as _uuid
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

    # Policy registry: (summary_key, policy_name, method_name)
    _POLICY_REGISTRY = [
        ('timeout_spike', 'timeout_spike_containment', '_policy_timeout_spike_containment'),
        ('blocked_hygiene', 'blocked_agent_hygiene', '_policy_blocked_agent_hygiene'),
        ('deliberation_retry', 'failed_deliberation_retry', '_policy_failed_deliberation_retry'),
        ('content_sweep', 'content_pipeline_sweep', '_policy_content_pipeline_sweep'),
        ('attention_resolve', 'attention_auto_resolve', '_policy_attention_auto_resolve'),
        ('governance_auto', 'governance_auto_decision', '_policy_governance_auto_decision'),
        ('remediation', 'root_cause_remediation', '_policy_root_cause_remediation'),
        ('contract_drift', 'contract_drift_detection', '_policy_contract_drift_detection'),
        ('tuning', 'self_tuning', '_policy_self_tuning'),
        ('budget', 'budget_controller', '_policy_budget_controller'),
        ('roi', 'roi_enforcement', '_policy_roi_enforcement'),
        ('impact_portfolio', 'impact_portfolio', '_policy_impact_portfolio'),
        ('attribution_debt', 'attribution_debt', '_policy_attribution_debt'),
        ('experiments', 'experiment_engine', '_policy_experiment_engine'),
        ('timeout_playbook', 'timeout_remediation_playbook', '_policy_timeout_remediation_playbook'),
        ('deliberation_playbook', 'deliberation_remediation_playbook', '_policy_deliberation_remediation_playbook'),
        ('backlog_governor', 'backlog_governor', '_policy_backlog_governor'),
        ('goal_allocator', 'goal_aware_allocator', '_policy_goal_aware_allocator'),
        ('attribution', 'multi_touch_attribution', '_policy_multi_touch_attribution'),
        ('arbitrator', 'policy_arbitrator', '_policy_policy_arbitrator'),
        ('release', 'release_governor', '_policy_release_governor'),
        ('revenue_pipeline', 'revenue_pipeline', '_policy_revenue_pipeline'),
        ('outbound_leads', 'outbound_lead_engine', '_policy_outbound_leads'),
        ('outreach', 'outreach_sequencer', '_policy_outreach_sequencer'),
        ('close_deal', 'close_the_deal', '_policy_close_the_deal'),
    ]

    def run(self) -> dict[str, Any]:
        """Main entry point. Returns summary of evaluation + actions."""
        now = timezone.now()
        cycle_id = _uuid.uuid4()
        logger.info(f"[OpsAutopilot] Starting cycle {cycle_id} (dry_run={self.dry_run})")

        # Load latest config overrides from SystemConfiguration
        AutopilotConfig.load_overrides()

        self.deploy_sha = self._get_deploy_sha()

        # Active experiment lookup for ledger context
        active_experiments = self._get_active_experiment_map()

        # Run all policies and record ledger entries
        results = {}
        for summary_key, policy_name, method_name in self._POLICY_REGISTRY:
            t0 = time.monotonic()
            actions_before = len(self.actions_taken)
            try:
                policy_result = getattr(self, method_name)(now)
            except Exception as e:
                logger.error(f"[OpsAutopilot] Policy {policy_name} error: {e}")
                policy_result = {'error': str(e)}

            elapsed_ms = int((time.monotonic() - t0) * 1000)
            results[summary_key] = policy_result

            # Determine decision type
            actions_after = len(self.actions_taken)
            decision_type = self._classify_decision(
                policy_result, actions_after - actions_before,
            )

            # Record ledger entry
            self._record_ledger_entry(
                cycle_id=cycle_id,
                cycle_ts=now,
                policy=policy_name,
                decision_type=decision_type,
                policy_result=policy_result,
                duration_ms=elapsed_ms,
                active_experiments=active_experiments,
            )

        summary = {
            'cycle_at': now.isoformat(),
            'cycle_id': str(cycle_id),
            'dry_run': self.dry_run,
            'deploy_sha': self.deploy_sha,
            **results,
            'actions_taken': len(self.actions_taken),
            'actions': self.actions_taken,
        }

        # Log every cycle for observability (even no-ops)
        AutopilotAction.objects.create(
            action_type='dry_run' if self.dry_run or not self.actions_taken else 'deploy_watch',
            agent_name='',
            policy='cycle_evaluation',
            dry_run=self.dry_run,
            evidence={k: v for k, v in results.items()},
            result=summary,
            deploy_sha=self.deploy_sha,
        )

        logger.info(
            f"[OpsAutopilot] Cycle {cycle_id} complete: "
            f"{len(self.actions_taken)} actions taken "
            f"(dry_run={self.dry_run})"
        )
        return summary

    # ── Decision Ledger helpers (Policy 16) ─────────────────────────────

    def _get_active_experiment_map(self) -> dict[str, str]:
        """Return {policy_name: experiment_id} for active experiments."""
        try:
            from core.models_policy_experiment import PolicyExperiment
            return {
                exp.policy_name: str(exp.id)
                for exp in PolicyExperiment.objects.filter(status='active')
            }
        except Exception:
            return {}

    @staticmethod
    def _classify_decision(policy_result: dict, new_actions: int) -> str:
        """Classify a policy evaluation into a decision type."""
        if policy_result.get('error'):
            return 'skipped'
        if policy_result.get('allocation_blocked_reason'):
            return 'blocked'
        if new_actions > 0:
            return 'action_taken'
        return 'no_op'

    def _record_ledger_entry(
        self,
        cycle_id,
        cycle_ts,
        policy: str,
        decision_type: str,
        policy_result: dict,
        duration_ms: int,
        active_experiments: dict,
    ):
        """Create a DecisionLedgerEntry for one policy evaluation."""
        try:
            from core.models_decision_ledger import DecisionLedgerEntry

            # Extract desk if present
            desk = policy_result.get('desk', '')
            if not desk and 'desk_allocations' in policy_result:
                desk = ''  # multi-desk policy, no single desk

            # Build summary
            summary_parts = []
            if decision_type == 'no_op':
                summary_parts.append('No action needed')
            elif decision_type == 'skipped':
                summary_parts.append(f"Error: {policy_result.get('error', 'unknown')[:150]}")
            elif decision_type == 'blocked':
                summary_parts.append(
                    policy_result.get('allocation_blocked_reason', 'Blocked')[:150]
                )
            elif decision_type == 'action_taken':
                # Summarize what was done
                actions = policy_result.get('actions', [])
                if isinstance(actions, list) and actions:
                    summary_parts.append(f"{len(actions)} action(s)")
                else:
                    summary_parts.append('Action taken')

            # Experiment context
            experiment_id = active_experiments.get(policy)

            DecisionLedgerEntry.objects.create(
                cycle_id=cycle_id,
                cycle_ts=cycle_ts,
                policy=policy,
                desk=desk[:20] if desk else '',
                decision_type=decision_type,
                decision_summary='; '.join(summary_parts)[:200],
                inputs=self._safe_json(policy_result),
                outputs={'actions_taken': decision_type == 'action_taken'},
                experiment_id=experiment_id,
                params_used={},
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.warning(f"[OpsAutopilot] Ledger entry failed for {policy}: {e}")

    @staticmethod
    def _safe_json(data: Any) -> dict:
        """Ensure data is JSON-serializable by converting via str fallback."""
        import json
        try:
            json.dumps(data, default=str)
            return data if isinstance(data, dict) else {'data': str(data)}
        except (TypeError, ValueError):
            return {'raw': str(data)[:500]}

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
        Session 1089/1090: Collect impact events from settled wagers,
        deliverable interactions, and confirmed revenue. Then compute
        desk-level IQROI and adjust portfolio allocations.

        Session 1090: Attribution debt check — if too many LLM calls
        can't be attributed to a desk, reallocation is blocked or
        smoothing is increased to prevent bad decisions.
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

            # Step 1.5: Check attribution debt (Policy 14)
            debt_ctrl = AttributionDebtController()
            debt = debt_ctrl.compute_debt(now, window_hours=24)
            result['attribution_debt_pct'] = debt['debt_pct']
            result['attribution_debt_usd'] = debt['unattributed_spend']

            if debt_ctrl.should_block_reallocation(debt):
                result['allocated'] = False
                result['allocation_blocked_reason'] = (
                    f"Attribution debt {debt['debt_pct']:.0f}% exceeds "
                    f"critical threshold — reallocation unsafe"
                )
                self._create_attention_item(
                    title=(
                        f"Portfolio reallocation blocked: "
                        f"{debt['debt_pct']:.0f}% attribution debt"
                    ),
                    summary=(
                        f"${debt['unattributed_spend']:.2f} of "
                        f"${debt['total_spend']:.2f} LLM spend (24h) "
                        f"cannot be attributed to a desk. Top offenders: "
                        f"{', '.join(u['agent'] for u in debt['top_unattributed'][:5])}. "
                        f"Add these agents to AttributionDebtController."
                        f"AGENT_DESK_MAP to fix."
                    ),
                    urgency='medium',
                    policy='attribution_debt',
                    agent_name='AttributionDebtController',
                )
                logger.warning(
                    f"[OpsAutopilot] Portfolio reallocation blocked: "
                    f"{debt['debt_pct']:.0f}% attribution debt"
                )
                return result

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

    # ── Policy 14: Attribution debt monitoring ────────────────────────────

    def _policy_attribution_debt(self, now) -> dict:
        """
        Session 1090: Monitor attribution debt — LLM spend that can't be
        attributed to a desk. Creates governance alerts when debt is high.
        """
        result = {
            'debt_pct': 0,
            'debt_usd': 0,
            'status': 'healthy',
            'alert_created': False,
        }

        try:
            ctrl = AttributionDebtController()
            debt = ctrl.compute_debt(now, window_hours=24)
            result['debt_pct'] = debt['debt_pct']
            result['debt_usd'] = debt['unattributed_spend']

            warning_pct = (
                AutopilotConfig.get('DEBT_WARNING_PCT')
                or ctrl.DEBT_WARNING_PCT
            )

            if (
                debt['debt_pct'] >= warning_pct
                and debt['unattributed_spend'] > ctrl.DEBT_USD_FLOOR
            ):
                result['status'] = 'warning'
                top_agents = ', '.join(
                    u['agent'] for u in debt['top_unattributed'][:5]
                )
                self._create_attention_item(
                    title=(
                        f"Attribution debt: {debt['debt_pct']:.0f}% "
                        f"of LLM spend unattributed"
                    ),
                    summary=(
                        f"${debt['unattributed_spend']:.2f} of "
                        f"${debt['total_spend']:.2f} LLM spend (24h) "
                        f"lacks desk attribution. Top unattributed: "
                        f"{top_agents}. Add to AGENT_DESK_MAP to fix. "
                        f"Portfolio reallocation reliability: "
                        f"{'blocked' if ctrl.should_block_reallocation(debt) else 'degraded'}."
                    ),
                    urgency='low',
                    policy='attribution_debt',
                    agent_name='AttributionDebtController',
                )
                result['alert_created'] = True

            logger.info(
                f"[OpsAutopilot] Attribution debt: "
                f"{debt['debt_pct']:.1f}% "
                f"(${debt['unattributed_spend']:.2f})"
            )

        except Exception as e:
            logger.error(
                f"[OpsAutopilot] Attribution debt error: {e}"
            )
            result['error'] = str(e)

        return result

    # ── Policy 15: Experiment engine ──────────────────────────────────────

    def _policy_experiment_engine(self, now) -> dict:
        """
        Session 1090: Evaluate active experiments — auto-promote or
        rollback based on metric comparison.
        """
        result = {
            'experiments_evaluated': 0,
            'actions': [],
        }

        try:
            engine = ExperimentEngine()
            evaluations = engine.evaluate_experiments(now)
            result['experiments_evaluated'] = len(evaluations)

            for eval_result in evaluations:
                action = eval_result.get('action', 'continue')
                if action in ('promoted', 'rolled_back', 'expired'):
                    result['actions'].append(eval_result)
                    self.actions_taken.append({
                        'type': f'experiment_{action}',
                        'experiment_id': eval_result['experiment_id'],
                        'policy': eval_result['policy'],
                    })
                    self._create_attention_item(
                        title=(
                            f"Experiment {action}: "
                            f"{eval_result['policy']}"
                        ),
                        summary=(
                            f"Experiment {eval_result['experiment_id'][:8]} "
                            f"on {eval_result['policy']} was {action}. "
                            f"Change: {eval_result.get('pct_change', 'N/A')}% "
                            f"on metric."
                        ),
                        urgency='medium' if action == 'rolled_back' else 'low',
                        policy='experiment_engine',
                        agent_name='ExperimentEngine',
                    )

            logger.info(
                f"[OpsAutopilot] Experiments: "
                f"{len(evaluations)} evaluated, "
                f"{len(result['actions'])} decisions"
            )

        except Exception as e:
            logger.error(
                f"[OpsAutopilot] Experiment engine error: {e}"
            )
            result['error'] = str(e)

        return result

    # ── Policy 17: Timeout Remediation Playbook ──────────────────────────

    def _policy_timeout_remediation_playbook(self, now) -> dict:
        """
        Graduated timeout remediation: monitor → increase timeout →
        reduce scope → block. With auto-de-escalation on recovery.
        """
        result = {
            'agents_evaluated': 0,
            'escalations': 0,
            'de_escalations': 0,
        }

        try:
            playbook = TimeoutRemediationPlaybook(
                dry_run=self.dry_run,
                deploy_sha=self.deploy_sha,
            )
            eval_result = playbook.evaluate(now)

            result['agents_evaluated'] = eval_result['agents_evaluated']
            result['escalations'] = eval_result['escalations']
            result['de_escalations'] = eval_result['de_escalations']
            result['details'] = eval_result.get('details', [])

            # Merge actions
            self.actions_taken.extend(playbook.actions)

            # Create governance items for escalations to L2+
            for detail in eval_result.get('details', []):
                if detail.get('action') == 'escalate' and detail.get('to_level', 0) >= 2:
                    self._create_attention_item(
                        title=(
                            f"Timeout ladder L{detail['to_level']}: "
                            f"{detail['agent_name']}"
                        ),
                        summary=(
                            f"{detail['agent_name']} escalated to "
                            f"level {detail['to_level']} "
                            f"({detail.get('timeout_count', '?')} timeouts/hr). "
                            f"{'Batch reduction applied.' if detail['to_level'] == 2 else ''}"
                            f"{'Agent blocked.' if detail['to_level'] == 3 else ''}"
                        ),
                        urgency='medium' if detail['to_level'] == 3 else 'low',
                        policy='timeout_remediation_playbook',
                        agent_name=detail['agent_name'],
                    )

            logger.info(
                f"[OpsAutopilot] Timeout playbook: "
                f"{result['agents_evaluated']} evaluated, "
                f"{result['escalations']} escalations, "
                f"{result['de_escalations']} de-escalations"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] timeout playbook error: {e}")
            result['error'] = str(e)

        return result

    # ── Policy 18: Deliberation Failure Remediation Playbook ─────────────

    def _policy_deliberation_remediation_playbook(self, now) -> dict:
        """
        Monitor deliberation failure rate and apply graduated fixes:
        L1=reduce panel, L2=fallback model, L3=single-reviewer bypass.
        """
        result = {
            'failure_rate_pct': 0.0,
            'total_sessions': 0,
            'failed_sessions': 0,
            'current_level': 0,
            'action_taken': None,
        }

        try:
            playbook = DeliberationRemediationPlaybook(
                dry_run=self.dry_run,
                deploy_sha=self.deploy_sha,
            )
            eval_result = playbook.evaluate(now)

            result['failure_rate_pct'] = eval_result.get('failure_rate_pct', 0.0)
            result['total_sessions'] = eval_result.get('total_sessions', 0)
            result['failed_sessions'] = eval_result.get('failed_sessions', 0)
            result['current_level'] = eval_result.get('current_level', 0)

            action = eval_result.get('action')
            if action:
                result['action_taken'] = action
                self.actions_taken.extend(playbook.actions)

                # Governance item for escalations to L2+
                if action.get('action') == 'escalate' and action.get('to_level', 0) >= 2:
                    self._create_attention_item(
                        title=(
                            f"Deliberation ladder L{action['to_level']}: "
                            f"fail rate {action.get('failure_rate_pct', '?')}%"
                        ),
                        summary=(
                            f"Deliberation pipeline escalated to L{action['to_level']}. "
                            f"{'Reviewer model fallback active.' if action['to_level'] == 2 else ''}"
                            f"{'Single-reviewer bypass active.' if action['to_level'] == 3 else ''}"
                        ),
                        urgency='medium' if action['to_level'] == 3 else 'low',
                        policy='deliberation_remediation_playbook',
                        agent_name='ContentDeliberation',
                    )

            logger.info(
                f"[OpsAutopilot] Delib playbook: "
                f"rate={result['failure_rate_pct']:.1f}% "
                f"level={result['current_level']} "
                f"action={action['action'] if action else 'none'}"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] delib playbook error: {e}")
            result['error'] = str(e)

        return result

    def _policy_backlog_governor(self, now) -> dict:
        """
        Monitor deliverable backlog and apply graduated clearance actions:
        L1=throttle generation, L2=governance batch, L3=auto-archive stale.
        """
        result = {
            'publish_ready_count': 0,
            'draft_count': 0,
            'p95_age_hours': 0.0,
            'conversion_rate_pct': 0.0,
            'current_level': 0,
            'action_taken': None,
        }

        try:
            governor = BacklogGovernor(
                dry_run=self.dry_run,
                deploy_sha=self.deploy_sha,
            )
            eval_result = governor.evaluate(now)

            result['publish_ready_count'] = eval_result.get('publish_ready_count', 0)
            result['draft_count'] = eval_result.get('draft_count', 0)
            result['p95_age_hours'] = eval_result.get('p95_age_hours', 0.0)
            result['conversion_rate_pct'] = eval_result.get('conversion_rate_pct', 0.0)
            result['current_level'] = eval_result.get('current_level', 0)

            action = eval_result.get('action')
            if action:
                result['action_taken'] = action
                self.actions_taken.extend(governor.actions)

                # Governance item for L2+ escalations
                if action.get('action') == 'escalate' and action.get('to_level', 0) >= 2:
                    self._create_attention_item(
                        title=(
                            f"Backlog governor L{action['to_level']}: "
                            f"{eval_result.get('publish_ready_count', '?')} items backed up"
                        ),
                        summary=(
                            f"Deliverable backlog escalated to L{action['to_level']}. "
                            f"p95 age: {eval_result.get('p95_age_hours', 0):.0f}h. "
                            f"{'Auto-archiving stale drafts.' if action['to_level'] == 3 else 'Review backlog.'}"
                        ),
                        urgency='medium' if action['to_level'] == 3 else 'low',
                        policy='backlog_governor',
                        agent_name='BacklogGovernor',
                    )

            logger.info(
                f"[OpsAutopilot] Backlog governor: "
                f"ready={result['publish_ready_count']} "
                f"draft={result['draft_count']} "
                f"p95={result['p95_age_hours']:.0f}h "
                f"level={result['current_level']} "
                f"action={action['action'] if action else 'none'}"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] backlog governor error: {e}")
            result['error'] = str(e)

        return result

    def _policy_goal_aware_allocator(self, now) -> dict:
        """
        Compute goal-derived utility scores per desk and apply
        goal-weighted allocation multipliers on top of IQROI.
        """
        result = {
            'applied': False,
            'desks_adjusted': 0,
            'adjustments': {},
        }

        try:
            allocator = GoalAwareAllocator()
            adjustments = allocator.apply_goal_allocations(now)
            result['applied'] = True
            result['desks_adjusted'] = len(adjustments)
            result['adjustments'] = adjustments
            result['weights'] = allocator.get_weights()

            if adjustments and not self.dry_run:
                self.actions_taken.append({
                    'type': 'goal_allocation',
                    'desks_adjusted': len(adjustments),
                    'adjustments': adjustments,
                })

            logger.info(
                f"[OpsAutopilot] Goal allocator: "
                f"{len(adjustments)} desks adjusted"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] goal allocator error: {e}")
            result['error'] = str(e)

        return result

    def _policy_multi_touch_attribution(self, now) -> dict:
        """
        Attribute ImpactEvent credit to upstream agents/desks.
        70% last-touch, 30% assist (split among linked upstream).
        """
        result = {
            'events_processed': 0,
            'credits_created': 0,
            'errors': 0,
        }

        try:
            attributor = MultiTouchAttributor()
            attr_result = attributor.attribute_recent(now, window_hours=24)
            result['events_processed'] = attr_result.get('events_processed', 0)
            result['credits_created'] = attr_result.get('credits_created', 0)
            result['errors'] = attr_result.get('errors', 0)

            logger.info(
                f"[OpsAutopilot] Attribution: "
                f"{result['events_processed']} events, "
                f"{result['credits_created']} credits"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] attribution error: {e}")
            result['error'] = str(e)

        return result

    def _policy_revenue_pipeline(self, now) -> dict:
        """
        Monitor Opportunity pipeline health. Flag stale opps,
        suggest follow-ups, track pipeline metrics.
        """
        result = {
            'total_active': 0,
            'stale_count': 0,
            'actions_suggested': 0,
        }

        try:
            automator = RevenuePipelineAutomator()
            eval_result = automator.evaluate(now)
            result['total_active'] = eval_result.get('total_active', 0)
            result['stale_count'] = eval_result.get('stale_count', 0)
            result['critical_stale'] = eval_result.get('critical_stale', 0)
            result['high_value_active'] = eval_result.get('high_value_active', 0)
            result['actions_suggested'] = eval_result.get('actions_suggested', 0)

            # Create attention items for critical stale opps
            if eval_result.get('critical_stale', 0) > 0:
                try:
                    from core.models_human_interface import HumanAttentionItem
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.first()
                    if user:
                        HumanAttentionItem.objects.create(
                            user=user,
                            source='ops_autopilot',
                            category='revenue_pipeline',
                            title=(
                                f"Revenue pipeline: {eval_result['critical_stale']} "
                                f"critically stale opportunities (>7d)"
                            ),
                            description=(
                                f"Active: {eval_result['total_active']}, "
                                f"Stale: {eval_result['stale_count']}, "
                                f"High-value: {eval_result.get('high_value_active', 0)}"
                            ),
                            priority='high',
                            auto_dismissable=True,
                        )
                except Exception as e:
                    logger.warning(
                        f"[OpsAutopilot] revenue pipeline attention failed: {e}"
                    )

            logger.info(
                f"[OpsAutopilot] Revenue pipeline: "
                f"{result['total_active']} active, "
                f"{result['stale_count']} stale, "
                f"{result['actions_suggested']} suggestions"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] revenue pipeline error: {e}")
            result['error'] = str(e)

        return result

    def _policy_outbound_leads(self, now) -> dict:
        """
        Discover prospecting leads from spider data, score them,
        surface the top queue for human outreach. Never auto-sends.
        """
        result = {
            'leads_discovered': 0,
            'leads_queued': 0,
            'sources_active': 0,
        }

        try:
            engine = OutboundLeadEngine()
            eval_result = engine.evaluate(now)
            result['leads_discovered'] = eval_result.get('leads_discovered', 0)
            result['leads_queued'] = eval_result.get('leads_queued', 0)
            result['sources_active'] = eval_result.get('sources_active', 0)
            result['top_leads'] = eval_result.get('top_leads', [])[:5]

            # Create attention item when high-value leads are found
            high_value = [
                l for l in eval_result.get('top_leads', [])
                if l.get('score', 0) >= 70
            ]
            if high_value:
                try:
                    from core.models_human_interface import HumanAttentionItem
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.first()
                    if user:
                        HumanAttentionItem.objects.create(
                            user=user,
                            source='ops_autopilot',
                            category='outbound_leads',
                            title=(
                                f"Outbound leads: {len(high_value)} high-value "
                                f"leads ready for review"
                            ),
                            description=(
                                f"Total discovered: {result['leads_discovered']}, "
                                f"Queued: {result['leads_queued']}, "
                                f"Sources: {result['sources_active']}"
                            ),
                            priority='medium',
                            auto_dismissable=True,
                        )
                except Exception as e:
                    logger.warning(
                        f"[OpsAutopilot] outbound leads attention failed: {e}"
                    )

            logger.info(
                f"[OpsAutopilot] Outbound leads: "
                f"{result['leads_discovered']} discovered, "
                f"{result['leads_queued']} queued"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] outbound leads error: {e}")
            result['error'] = str(e)

        return result

    def _policy_outreach_sequencer(self, now) -> dict:
        """
        Manage outreach draft lifecycle — generate follow-ups,
        expire stale drafts, report inbox stats.
        """
        result = {
            'pending_drafts': 0,
            'followups_generated': 0,
            'expired': 0,
        }

        try:
            sequencer = OutreachSequencer()
            eval_result = sequencer.evaluate(now)
            result.update(eval_result)

            logger.info(
                f"[OpsAutopilot] Outreach: "
                f"{result['pending_drafts']} pending, "
                f"{result['followups_generated']} follow-ups generated, "
                f"{result['expired']} expired"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] outreach sequencer error: {e}")
            result['error'] = str(e)

        return result

    def _policy_close_the_deal(self, now) -> dict:
        """
        Manage close pack lifecycle — follow-up scheduling,
        expiration, and deal pipeline stats.
        """
        result = {
            'pending_packs': 0,
            'followups_scheduled': 0,
            'expired': 0,
        }

        try:
            engine = CloseTheDealEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            logger.info(
                f"[OpsAutopilot] Close-the-Deal: "
                f"{result['pending_packs']} pending, "
                f"{result['followups_scheduled']} follow-ups, "
                f"{result['expired']} expired"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] close-the-deal error: {e}")
            result['error'] = str(e)

        return result

    def _policy_release_governor(self, now) -> dict:
        """
        Monitor deploy health and apply graduated safety measures.
        L0=observe, L1=backoff, L2=gate, L3=freeze.
        """
        result = {
            'level': 0,
            'deploy_rate_per_hour': 0.0,
            'error_rate': 0.0,
            'frozen': False,
        }

        try:
            governor = ReleaseGovernor()
            eval_result = governor.evaluate(now)
            result.update(eval_result)

            # Create governance attention item for L2+
            if result['level'] >= 2:
                try:
                    from core.models_human_interface import HumanAttentionItem
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.first()
                    if user:
                        HumanAttentionItem.objects.create(
                            user=user,
                            source='ops_autopilot',
                            category='deploy_health',
                            title=(
                                f"Release governor L{result['level']}: "
                                f"{'FROZEN' if result['frozen'] else 'gated'}"
                            ),
                            description=(
                                f"Deploy rate: {result['deploy_rate_per_hour']:.1f}/hr, "
                                f"Error rate: {result['error_rate']:.1%}"
                            ),
                            priority='high' if result['level'] >= 3 else 'medium',
                            auto_dismissable=True,
                        )
                except Exception as e:
                    logger.warning(
                        f"[OpsAutopilot] release attention item failed: {e}"
                    )

            logger.info(
                f"[OpsAutopilot] Release: L{result['level']}, "
                f"rate={result['deploy_rate_per_hour']:.1f}/hr, "
                f"err={result['error_rate']:.1%}"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] release governor error: {e}")
            result['error'] = str(e)

        return result

    def _policy_policy_arbitrator(self, now) -> dict:
        """
        Post-hoc conflict detection + FinalAppliedOverrides snapshot.
        Runs LAST in the policy registry so all other policies have
        already written their values.
        """
        result = {
            'conflicts': 0,
            'flaps': 0,
            'suppressed': 0,
        }

        try:
            arbitrator = PolicyArbitrator()
            report = arbitrator.detect_conflicts(now)
            result['conflicts'] = report.get('conflict_count', 0)
            result['flaps'] = report.get('flap_count', 0)
            result['suppressed'] = report.get('suppressed_count', 0)

            # Record overrides snapshot
            cycle_id = _uuid.uuid4()
            snapshot = arbitrator.record_overrides_snapshot(now, cycle_id)
            result['snapshot_knobs'] = snapshot.get('knob_count', 0)

            # If conflicts detected, create governance attention item
            if result['conflicts'] > 0:
                try:
                    from core.models_human_interface import HumanAttentionItem
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.first()
                    if user:
                        HumanAttentionItem.objects.create(
                            user=user,
                            source='ops_autopilot',
                            category='policy_conflict',
                            title=(
                                f"Policy arbitrator: {result['conflicts']} "
                                f"conflict(s) detected"
                            ),
                            description=(
                                f"Conflicts: {result['conflicts']}, "
                                f"Flaps: {result['flaps']}, "
                                f"Hold violations: {result['suppressed']}"
                            ),
                            priority='medium',
                            auto_dismissable=True,
                        )
                except Exception as e:
                    logger.warning(
                        f"[OpsAutopilot] arbitrator attention item failed: {e}"
                    )

            logger.info(
                f"[OpsAutopilot] Arbitrator: {result['conflicts']} conflicts, "
                f"{result['flaps']} flaps, {result['suppressed']} suppressed"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] arbitrator error: {e}")
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


# ── Policy 17: Timeout Remediation Playbook ──────────────────────────────────


class TimeoutRemediationPlaybook:
    """
    Graduated remediation ladder for agents with sustained timeout issues.

    Unlike the RemediationEngine (which does one-shot heuristic fixes),
    this playbook tracks remediation LEVEL per agent and escalates:

      Level 0: Monitoring only (no action)
      Level 1: Increase timeout by 50% via SystemConfiguration
      Level 2: Reduce scope — set batch_size_reduction flag for the agent
      Level 3: Temporary block with TTL + governance attention item

    Escalation: if timeout rate doesn't improve within EVAL_WINDOW_CYCLES
    after a remediation, escalate to next level.

    De-escalation: if timeout rate drops to 0 for RECOVERY_CYCLES, step
    down one level and clean up overrides.

    Auto-rollback: if error_rate or impact_value degrades after remediation,
    immediately roll back one level.
    """

    # How many cycles to wait before escalating if no improvement
    EVAL_WINDOW_CYCLES = 6  # ~60 min at 10min/cycle
    # How many clean cycles before de-escalating
    RECOVERY_CYCLES = 12  # ~2 hours clean
    # Max timeouts per hour to trigger ladder entry
    ENTRY_THRESHOLD = 5
    # Max timeout multiplier
    MAX_TIMEOUT_MULTIPLIER = 2.0
    MAX_TIMEOUT_ABSOLUTE = 1800  # 30 min
    # TTL for level-3 block (hours)
    BLOCK_TTL_HOURS = 4

    # SystemConfiguration key patterns
    KEY_LEVEL = 'timeout_ladder_level:{agent}'
    KEY_LEVEL_TS = 'timeout_ladder_level_ts:{agent}'
    KEY_CLEAN_CYCLES = 'timeout_ladder_clean:{agent}'
    KEY_BATCH_REDUCTION = 'timeout_ladder_batch_reduce:{agent}'

    def __init__(self, dry_run: bool = False, deploy_sha: str = ''):
        self.dry_run = dry_run
        self.deploy_sha = deploy_sha
        self.actions: list[dict] = []

    def evaluate(self, now) -> dict:
        """
        Evaluate all agents for timeout remediation ladder.

        Returns summary of evaluations, escalations, and de-escalations.
        """
        from core.models_diagnostic_pipeline import FailureDetection
        from django.db.models import Count

        result = {
            'agents_evaluated': 0,
            'escalations': 0,
            'de_escalations': 0,
            'rollbacks': 0,
            'details': [],
        }

        try:
            # Find agents with timeouts in the last hour
            window = now - timedelta(hours=1)
            agent_timeouts = list(
                FailureDetection.objects.filter(
                    signature__category='timeout',
                    detected_at__gte=window,
                ).values('source_name').annotate(
                    count=Count('id')
                ).order_by('-count')
            )

            # Also check agents currently on the ladder that may have recovered
            current_levels = self._get_all_levels()

            # Combine: agents with current timeouts + agents on ladder
            agent_names = set()
            timeout_counts = {}
            for entry in agent_timeouts:
                name = entry['source_name']
                if name:
                    agent_names.add(name)
                    timeout_counts[name] = entry['count']

            for name in current_levels:
                agent_names.add(name)

            for agent_name in agent_names:
                count = timeout_counts.get(agent_name, 0)
                current_level = current_levels.get(agent_name, 0)

                action = self._evaluate_agent(
                    agent_name, count, current_level, now,
                )
                result['agents_evaluated'] += 1

                if action:
                    result['details'].append(action)
                    if action['action'] == 'escalate':
                        result['escalations'] += 1
                    elif action['action'] == 'de_escalate':
                        result['de_escalations'] += 1
                    elif action['action'] == 'rollback':
                        result['rollbacks'] += 1

        except Exception as e:
            logger.error(f"[TimeoutPlaybook] evaluation error: {e}")
            result['error'] = str(e)

        return result

    def _evaluate_agent(
        self, agent_name: str, timeout_count: int,
        current_level: int, now,
    ) -> dict | None:
        """Evaluate a single agent and decide on escalation/de-escalation."""

        # Case 1: Agent not on ladder and below threshold → skip
        if current_level == 0 and timeout_count < self.ENTRY_THRESHOLD:
            return None

        # Case 2: Agent not on ladder but above threshold → enter level 1
        if current_level == 0 and timeout_count >= self.ENTRY_THRESHOLD:
            return self._escalate(agent_name, 0, 1, timeout_count, now)

        # Case 3: Agent on ladder, check if clean (recovered)
        if timeout_count == 0:
            clean = self._increment_clean_cycles(agent_name)
            if clean >= self.RECOVERY_CYCLES:
                return self._de_escalate(agent_name, current_level, now)
            return None  # Still recovering, wait

        # Case 4: Agent on ladder and still timing out → reset clean counter
        self._reset_clean_cycles(agent_name)

        # Check if enough cycles have passed since last escalation
        level_ts = self._get_level_timestamp(agent_name)
        if level_ts:
            cycles_since = (now - level_ts).total_seconds() / 600  # 10min cycles
            if cycles_since < self.EVAL_WINDOW_CYCLES:
                return None  # Too soon to escalate again

        # Still failing after eval window → escalate
        if current_level < 3:
            return self._escalate(
                agent_name, current_level, current_level + 1,
                timeout_count, now,
            )

        # Already at max level (3) — nothing more to do
        return None

    def _escalate(
        self, agent_name: str, from_level: int, to_level: int,
        timeout_count: int, now,
    ) -> dict:
        """Escalate an agent to the next remediation level."""
        from core.models.system import SystemConfiguration

        action = {
            'action': 'escalate',
            'agent_name': agent_name,
            'from_level': from_level,
            'to_level': to_level,
            'timeout_count': timeout_count,
        }

        if self.dry_run:
            action['dry_run'] = True
            return action

        # Apply the appropriate remediation for the new level
        if to_level == 1:
            # Increase timeout by 50%
            engine = RemediationEngine(dry_run=False, deploy_sha=self.deploy_sha)
            current_timeout = engine._get_current_timeout(agent_name)
            new_timeout = min(
                int(current_timeout * 1.5),
                self.MAX_TIMEOUT_ABSOLUTE,
            )
            SystemConfiguration.objects.update_or_create(
                key=f'agent_timeout_override:{agent_name}',
                defaults={
                    'value': str(new_timeout),
                    'description': (
                        f'Timeout ladder L1: {current_timeout}s → {new_timeout}s '
                        f'({timeout_count} timeouts/hr)'
                    ),
                },
            )
            action['timeout_change'] = {
                'from': current_timeout, 'to': new_timeout,
            }

        elif to_level == 2:
            # Set batch size reduction flag
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_BATCH_REDUCTION.format(agent=agent_name),
                defaults={
                    'value': '0.5',  # 50% batch size
                    'description': (
                        f'Timeout ladder L2: batch reduction for {agent_name} '
                        f'({timeout_count} timeouts/hr)'
                    ),
                },
            )
            action['batch_reduction'] = 0.5

        elif to_level == 3:
            # Temporary block
            from core.models_unified_system import AgentControlEntry
            AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': (
                        f'Timeout ladder L3: sustained timeouts '
                        f'({timeout_count}/hr after L1+L2 remediation)'
                    )[:255],
                    'blocked_at': now,
                    'blocked_by': 'timeout_playbook',
                    'ttl_hours': self.BLOCK_TTL_HOURS,
                },
            )
            action['blocked_ttl_hours'] = self.BLOCK_TTL_HOURS

        # Record level
        self._set_level(agent_name, to_level, now)
        self._reset_clean_cycles(agent_name)

        # Log
        AutopilotAction.objects.create(
            action_type='remediate',
            agent_name=agent_name,
            policy='timeout_remediation_playbook',
            dry_run=False,
            evidence={
                'ladder_from': from_level,
                'ladder_to': to_level,
                'timeout_count': timeout_count,
                **action,
            },
            result=action,
            deploy_sha=self.deploy_sha,
        )

        self.actions.append(action)

        logger.info(
            f"[TimeoutPlaybook] ESCALATE {agent_name}: "
            f"L{from_level} → L{to_level} "
            f"({timeout_count} timeouts/hr)"
        )

        return action

    def _de_escalate(
        self, agent_name: str, current_level: int, now,
    ) -> dict:
        """De-escalate an agent that has recovered."""
        from core.models.system import SystemConfiguration

        new_level = current_level - 1
        action = {
            'action': 'de_escalate',
            'agent_name': agent_name,
            'from_level': current_level,
            'to_level': new_level,
        }

        if self.dry_run:
            action['dry_run'] = True
            return action

        # Clean up the remediation for the current level
        if current_level == 1:
            # Remove timeout override
            SystemConfiguration.objects.filter(
                key=f'agent_timeout_override:{agent_name}',
            ).delete()

        elif current_level == 2:
            # Remove batch reduction flag
            SystemConfiguration.objects.filter(
                key=self.KEY_BATCH_REDUCTION.format(agent=agent_name),
            ).delete()

        elif current_level == 3:
            # Unblock agent
            from core.models_unified_system import AgentControlEntry
            AgentControlEntry.objects.filter(
                agent_name=agent_name,
                blocked_by='timeout_playbook',
            ).update(
                status='active',
                reason=f'Timeout ladder recovered: L{current_level} → L{new_level}',
            )

        # Update level
        if new_level > 0:
            self._set_level(agent_name, new_level, now)
        else:
            # Fully recovered — clean up all ladder state
            self._clear_level(agent_name)

        self._reset_clean_cycles(agent_name)

        # Log
        AutopilotAction.objects.create(
            action_type='remediate',
            agent_name=agent_name,
            policy='timeout_remediation_playbook',
            dry_run=False,
            evidence={
                'ladder_from': current_level,
                'ladder_to': new_level,
                'recovery': True,
            },
            result=action,
            deploy_sha=self.deploy_sha,
        )

        self.actions.append(action)

        logger.info(
            f"[TimeoutPlaybook] DE-ESCALATE {agent_name}: "
            f"L{current_level} → L{new_level}"
        )

        return action

    # ── Level tracking via SystemConfiguration ──────────────────────

    def _get_all_levels(self) -> dict[str, int]:
        """Return {agent_name: level} for all agents currently on the ladder."""
        from core.models.system import SystemConfiguration
        entries = SystemConfiguration.objects.filter(
            key__startswith='timeout_ladder_level:',
        ).exclude(
            key__contains='_ts:',
        ).exclude(
            key__contains='_clean:',
        ).exclude(
            key__contains='_batch_reduce:',
        )
        result = {}
        for entry in entries:
            agent = entry.key.split(':', 1)[1] if ':' in entry.key else ''
            if agent:
                try:
                    result[agent] = int(entry.value)
                except (ValueError, TypeError):
                    pass
        return result

    def _set_level(self, agent_name: str, level: int, now):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL.format(agent=agent_name),
            defaults={'value': str(level)},
        )
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL_TS.format(agent=agent_name),
            defaults={'value': now.isoformat()},
        )

    def _clear_level(self, agent_name: str):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.filter(
            key__in=[
                self.KEY_LEVEL.format(agent=agent_name),
                self.KEY_LEVEL_TS.format(agent=agent_name),
                self.KEY_CLEAN_CYCLES.format(agent=agent_name),
                self.KEY_BATCH_REDUCTION.format(agent=agent_name),
            ]
        ).delete()

    def _get_level_timestamp(self, agent_name: str):
        from core.models.system import SystemConfiguration
        from django.utils.dateparse import parse_datetime
        entry = SystemConfiguration.objects.filter(
            key=self.KEY_LEVEL_TS.format(agent=agent_name),
        ).first()
        if entry:
            return parse_datetime(entry.value)
        return None

    def _increment_clean_cycles(self, agent_name: str) -> int:
        from core.models.system import SystemConfiguration
        obj, _ = SystemConfiguration.objects.get_or_create(
            key=self.KEY_CLEAN_CYCLES.format(agent=agent_name),
            defaults={'value': '0'},
        )
        new_val = int(obj.value or '0') + 1
        obj.value = str(new_val)
        obj.save(update_fields=['value'])
        return new_val

    def _reset_clean_cycles(self, agent_name: str):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.filter(
            key=self.KEY_CLEAN_CYCLES.format(agent=agent_name),
        ).update(value='0')

    def get_ladder_report(self) -> dict:
        """Report current state of all agents on the timeout ladder."""
        levels = self._get_all_levels()
        if not levels:
            return {'agents_on_ladder': 0, 'agents': []}

        agents = []
        for agent_name, level in sorted(levels.items()):
            level_ts = self._get_level_timestamp(agent_name)
            agents.append({
                'agent_name': agent_name,
                'level': level,
                'level_since': level_ts.isoformat() if level_ts else None,
                'level_description': {
                    1: 'Timeout increased 50%',
                    2: 'Batch size reduced 50%',
                    3: f'Blocked (TTL {self.BLOCK_TTL_HOURS}h)',
                }.get(level, 'Unknown'),
            })

        return {
            'agents_on_ladder': len(agents),
            'agents': agents,
        }


# ── Policy 18: Deliberation Failure Remediation Playbook ─────────────────────


class DeliberationRemediationPlaybook:
    """
    Graduated remediation for recurring deliberation pipeline failures.

    Monitors DeliberationSession failure rates by failure_reason_code and
    applies progressive fixes:

      Level 0: Monitoring only
      Level 1: Reduce panel size (3→2 reviewers) to lower LLM load
      Level 2: Switch reviewer model to fallback (cheaper/faster)
      Level 3: Single-reviewer mode (bypass multi-agent deliberation)

    Failure rate = failed sessions / total sessions in the last RATE_WINDOW_HOURS.
    Entry threshold: failure rate > ENTRY_RATE_PCT.

    Auto-escalates after EVAL_WINDOW_CYCLES without improvement.
    Auto-de-escalates after RECOVERY_CYCLES below normal threshold.
    """

    # Thresholds
    RATE_WINDOW_HOURS = 6  # Look at last 6h of deliberation sessions
    ENTRY_RATE_PCT = 25.0  # Start remediating when >25% fail
    RECOVERY_RATE_PCT = 10.0  # De-escalate when <10% fail
    EVAL_WINDOW_CYCLES = 6  # Wait 6 cycles before escalating
    RECOVERY_CYCLES = 12  # 12 clean cycles to de-escalate

    # SystemConfiguration keys
    KEY_LEVEL = 'delib_ladder_level'
    KEY_LEVEL_TS = 'delib_ladder_level_ts'
    KEY_CLEAN_CYCLES = 'delib_ladder_clean'
    KEY_PANEL_SIZE = 'deliberation_panel_size_override'
    KEY_REVIEWER_MODEL = 'deliberation_reviewer_model_override'
    KEY_SINGLE_REVIEWER = 'deliberation_single_reviewer_mode'

    # Failure reasons we remediate (all except GATE_REJECT which is quality, not infra)
    REMEDIABLE_REASONS = {'TIMEOUT', 'LLM_UPSTREAM', 'EMPTY_TURN', 'TOOL_ERROR', 'DRAFT_FAILED'}

    def __init__(self, dry_run: bool = False, deploy_sha: str = ''):
        self.dry_run = dry_run
        self.deploy_sha = deploy_sha
        self.actions: list[dict] = []

    def evaluate(self, now) -> dict:
        """Evaluate deliberation pipeline health and manage remediation level."""
        result = {
            'failure_rate_pct': 0.0,
            'total_sessions': 0,
            'failed_sessions': 0,
            'current_level': 0,
            'action': None,
        }

        try:
            from core.models_deliberation import DeliberationSession

            window = now - timedelta(hours=self.RATE_WINDOW_HOURS)

            total = DeliberationSession.objects.filter(
                created_at__gte=window,
            ).count()

            failed = DeliberationSession.objects.filter(
                created_at__gte=window,
                status='failed',
                failure_reason_code__in=self.REMEDIABLE_REASONS,
            ).count()

            result['total_sessions'] = total
            result['failed_sessions'] = failed

            if total < 3:
                result['note'] = 'Too few sessions for rate calculation'
                return result

            rate = (failed / total) * 100
            result['failure_rate_pct'] = round(rate, 1)

            current_level = self._get_level()
            result['current_level'] = current_level

            # Decide action
            if current_level == 0 and rate >= self.ENTRY_RATE_PCT:
                action = self._escalate(0, 1, rate, now)
                result['action'] = action

            elif current_level > 0 and rate < self.RECOVERY_RATE_PCT:
                clean = self._increment_clean_cycles()
                if clean >= self.RECOVERY_CYCLES:
                    action = self._de_escalate(current_level, now)
                    result['action'] = action

            elif current_level > 0 and rate >= self.ENTRY_RATE_PCT:
                self._reset_clean_cycles()
                # Check if enough time passed to escalate
                level_ts = self._get_level_timestamp()
                if level_ts:
                    cycles_since = (now - level_ts).total_seconds() / 600
                    if cycles_since >= self.EVAL_WINDOW_CYCLES and current_level < 3:
                        action = self._escalate(current_level, current_level + 1, rate, now)
                        result['action'] = action

        except Exception as e:
            logger.error(f"[DelibPlaybook] evaluation error: {e}")
            result['error'] = str(e)

        return result

    def _escalate(self, from_level: int, to_level: int, rate: float, now) -> dict:
        """Escalate to next remediation level."""
        from core.models.system import SystemConfiguration

        action = {
            'action': 'escalate',
            'from_level': from_level,
            'to_level': to_level,
            'failure_rate_pct': rate,
        }

        if self.dry_run:
            action['dry_run'] = True
            return action

        if to_level == 1:
            # Reduce panel from 3→2
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_PANEL_SIZE,
                defaults={
                    'value': '2',
                    'description': (
                        f'Delib ladder L1: panel 3→2 '
                        f'(fail rate {rate:.1f}%)'
                    ),
                },
            )
            action['panel_size'] = 2

        elif to_level == 2:
            # Switch to fallback model
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_REVIEWER_MODEL,
                defaults={
                    'value': 'gpt-4o-mini',
                    'description': (
                        f'Delib ladder L2: reviewer model fallback '
                        f'(fail rate {rate:.1f}%)'
                    ),
                },
            )
            action['reviewer_model'] = 'gpt-4o-mini'

        elif to_level == 3:
            # Single-reviewer mode
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_SINGLE_REVIEWER,
                defaults={
                    'value': 'true',
                    'description': (
                        f'Delib ladder L3: single-reviewer bypass '
                        f'(fail rate {rate:.1f}%)'
                    ),
                },
            )
            action['single_reviewer'] = True

        self._set_level(to_level, now)
        self._reset_clean_cycles()

        AutopilotAction.objects.create(
            action_type='remediate',
            agent_name='ContentDeliberation',
            policy='deliberation_remediation_playbook',
            dry_run=False,
            evidence={
                'ladder_from': from_level,
                'ladder_to': to_level,
                'failure_rate_pct': rate,
                **action,
            },
            result=action,
            deploy_sha=self.deploy_sha,
        )

        self.actions.append(action)
        logger.info(
            f"[DelibPlaybook] ESCALATE L{from_level}→L{to_level} "
            f"(fail rate {rate:.1f}%)"
        )
        return action

    def _de_escalate(self, current_level: int, now) -> dict:
        """De-escalate one level — clean up current level's overrides."""
        from core.models.system import SystemConfiguration

        new_level = current_level - 1
        action = {
            'action': 'de_escalate',
            'from_level': current_level,
            'to_level': new_level,
        }

        if self.dry_run:
            action['dry_run'] = True
            return action

        # Clean up current level's config
        cleanup_keys = {
            1: [self.KEY_PANEL_SIZE],
            2: [self.KEY_REVIEWER_MODEL],
            3: [self.KEY_SINGLE_REVIEWER],
        }
        for key in cleanup_keys.get(current_level, []):
            SystemConfiguration.objects.filter(key=key).delete()

        if new_level > 0:
            self._set_level(new_level, now)
        else:
            self._clear_state()

        self._reset_clean_cycles()

        AutopilotAction.objects.create(
            action_type='remediate',
            agent_name='ContentDeliberation',
            policy='deliberation_remediation_playbook',
            dry_run=False,
            evidence={
                'ladder_from': current_level,
                'ladder_to': new_level,
                'recovery': True,
            },
            result=action,
            deploy_sha=self.deploy_sha,
        )

        self.actions.append(action)
        logger.info(
            f"[DelibPlaybook] DE-ESCALATE L{current_level}→L{new_level}"
        )
        return action

    # ── State tracking ──────────────────────────────────────────────

    def _get_level(self) -> int:
        from core.models.system import SystemConfiguration
        entry = SystemConfiguration.objects.filter(key=self.KEY_LEVEL).first()
        return int(entry.value) if entry else 0

    def _set_level(self, level: int, now):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL,
            defaults={'value': str(level)},
        )
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL_TS,
            defaults={'value': now.isoformat()},
        )

    def _get_level_timestamp(self):
        from core.models.system import SystemConfiguration
        from django.utils.dateparse import parse_datetime
        entry = SystemConfiguration.objects.filter(key=self.KEY_LEVEL_TS).first()
        return parse_datetime(entry.value) if entry else None

    def _increment_clean_cycles(self) -> int:
        from core.models.system import SystemConfiguration
        obj, _ = SystemConfiguration.objects.get_or_create(
            key=self.KEY_CLEAN_CYCLES,
            defaults={'value': '0'},
        )
        new_val = int(obj.value or '0') + 1
        obj.value = str(new_val)
        obj.save(update_fields=['value'])
        return new_val

    def _reset_clean_cycles(self):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.filter(key=self.KEY_CLEAN_CYCLES).update(value='0')

    def _clear_state(self):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.filter(
            key__in=[
                self.KEY_LEVEL, self.KEY_LEVEL_TS, self.KEY_CLEAN_CYCLES,
                self.KEY_PANEL_SIZE, self.KEY_REVIEWER_MODEL, self.KEY_SINGLE_REVIEWER,
            ]
        ).delete()

    def get_pipeline_report(self, now) -> dict:
        """Report current deliberation pipeline health + remediation state."""
        from core.models_deliberation import DeliberationSession
        from django.db.models import Count

        window = now - timedelta(hours=self.RATE_WINDOW_HOURS)

        total = DeliberationSession.objects.filter(created_at__gte=window).count()
        by_reason = dict(
            DeliberationSession.objects.filter(
                created_at__gte=window, status='failed',
            ).values_list('failure_reason_code').annotate(
                count=Count('id')
            )
        )

        level = self._get_level()
        level_ts = self._get_level_timestamp()

        return {
            'window_hours': self.RATE_WINDOW_HOURS,
            'total_sessions': total,
            'failures_by_reason': by_reason,
            'failure_rate_pct': round(
                sum(by_reason.values()) / max(total, 1) * 100, 1,
            ),
            'ladder_level': level,
            'ladder_level_since': level_ts.isoformat() if level_ts else None,
            'level_description': {
                0: 'Normal operation',
                1: 'Panel reduced (3→2)',
                2: 'Reviewer model fallback (gpt-4o-mini)',
                3: 'Single-reviewer bypass mode',
            }.get(level, 'Unknown'),
            'overrides_active': self._get_active_overrides(),
        }

    def _get_active_overrides(self) -> dict:
        from core.models.system import SystemConfiguration
        result = {}
        for key in [self.KEY_PANEL_SIZE, self.KEY_REVIEWER_MODEL, self.KEY_SINGLE_REVIEWER]:
            entry = SystemConfiguration.objects.filter(key=key).first()
            if entry:
                result[key] = entry.value
        return result


# ── Backlog Governor ─────────────────────────────────────────────────────────


class BacklogGovernor:
    """
    Ship-or-kill governor for the Deliverable backlog.

    Monitors the pipeline between "ready" deliverables and actual publishing
    to ensure content moves through the last mile. Graduated actions:

      Level 0: Monitoring only — backlog within healthy bounds
      Level 1: Throttle new generation (set config flag)
      Level 2: Batch governance attention items for manual review
      Level 3: Auto-archive stale drafts/ready items (>STALE_AGE_DAYS)

    KPIs tracked:
    - publish_ready_count: deliverables in 'ready' or 'draft' status
    - p95_age_hours: 95th percentile age of publish-ready items
    - conversion_rate: published / (published + ready + draft) over window

    Guardrails (never auto-archive):
    - is_pinned = True
    - is_saved = True
    - is_starred = True
    - quality_score >= 0.7
    - linked to initiative (initiative_id not null)
    """

    # Thresholds
    READY_COUNT_THRESHOLD = 10  # L1 trigger: >=10 items backed up
    P95_AGE_THRESHOLD_HOURS = 72  # L1 trigger: p95 age > 72h
    STALE_AGE_DAYS = 14  # L3 auto-archive: older than 14 days
    QUALITY_FLOOR = 0.7  # Never archive above this quality
    KPI_WINDOW_DAYS = 7  # Conversion rate lookback window

    # Escalation/recovery
    EVAL_WINDOW_CYCLES = 6  # Wait 6 cycles before escalating
    RECOVERY_CYCLES = 12  # 12 clean cycles to de-escalate

    # SystemConfiguration keys
    KEY_LEVEL = 'backlog_governor_level'
    KEY_LEVEL_TS = 'backlog_governor_level_ts'
    KEY_CLEAN_CYCLES = 'backlog_governor_clean'
    KEY_THROTTLE = 'backlog_generation_throttled'

    def __init__(self, dry_run: bool = False, deploy_sha: str = ''):
        self.dry_run = dry_run
        self.deploy_sha = deploy_sha
        self.actions: list[dict] = []

    def evaluate(self, now) -> dict:
        """Evaluate backlog health and manage governor level."""
        result = {
            'publish_ready_count': 0,
            'draft_count': 0,
            'p95_age_hours': 0.0,
            'conversion_rate_pct': 0.0,
            'current_level': 0,
            'action': None,
        }

        try:
            from core.models_deliverables import Deliverable
            from django.db.models import Count

            # Count backlog
            ready_count = Deliverable.objects.filter(status='ready').count()
            draft_count = Deliverable.objects.filter(status='draft').count()
            result['publish_ready_count'] = ready_count
            result['draft_count'] = draft_count

            # p95 age of ready + draft items
            backlog_qs = Deliverable.objects.filter(
                status__in=['ready', 'draft'],
            ).order_by('created_at')

            if backlog_qs.exists():
                total = backlog_qs.count()
                p95_idx = max(0, int(total * 0.95) - 1)
                p95_item = backlog_qs[p95_idx]
                p95_age = (now - p95_item.created_at).total_seconds() / 3600
                result['p95_age_hours'] = round(p95_age, 1)

            # Conversion rate over window
            window = now - timedelta(days=self.KPI_WINDOW_DAYS)
            window_total = Deliverable.objects.filter(
                created_at__gte=window,
            ).count()
            window_published = Deliverable.objects.filter(
                created_at__gte=window, status='published',
            ).count()
            if window_total > 0:
                result['conversion_rate_pct'] = round(
                    (window_published / window_total) * 100, 1,
                )

            # Current level
            current_level = self._get_level()
            result['current_level'] = current_level

            # Backlog is unhealthy if either threshold is breached
            backlog_unhealthy = (
                ready_count >= self.READY_COUNT_THRESHOLD
                or result['p95_age_hours'] >= self.P95_AGE_THRESHOLD_HOURS
            )

            if current_level == 0 and backlog_unhealthy:
                action = self._escalate(0, 1, result, now)
                result['action'] = action

            elif current_level > 0 and not backlog_unhealthy:
                # Backlog is healthy — count clean cycles toward de-escalation
                clean = self._increment_clean_cycles()
                if clean >= self.RECOVERY_CYCLES:
                    action = self._de_escalate(current_level, now)
                    result['action'] = action

            elif current_level > 0 and backlog_unhealthy:
                self._reset_clean_cycles()
                # Check if stuck long enough to escalate further
                level_ts = self._get_level_timestamp()
                if level_ts and current_level < 3:
                    cycles_since = (now - level_ts).total_seconds() / 600
                    if cycles_since >= self.EVAL_WINDOW_CYCLES:
                        action = self._escalate(
                            current_level, current_level + 1, result, now,
                        )
                        result['action'] = action

        except Exception as e:
            logger.error(f"[BacklogGovernor] evaluation error: {e}")
            result['error'] = str(e)

        return result

    def _escalate(self, from_level: int, to_level: int, kpis: dict, now) -> dict:
        """Escalate to next governor level."""
        from core.models.system import SystemConfiguration

        action = {
            'action': 'escalate',
            'from_level': from_level,
            'to_level': to_level,
            'publish_ready_count': kpis.get('publish_ready_count', 0),
            'p95_age_hours': kpis.get('p95_age_hours', 0),
        }

        if self.dry_run:
            action['dry_run'] = True
            return action

        if to_level == 1:
            # Throttle new content generation
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_THROTTLE,
                defaults={
                    'value': 'true',
                    'description': (
                        f'Backlog L1: throttle generation '
                        f'(ready={kpis["publish_ready_count"]}, '
                        f'p95={kpis["p95_age_hours"]:.0f}h)'
                    ),
                },
            )
            action['throttle_enabled'] = True

        elif to_level == 2:
            # Batch governance attention item
            self._create_backlog_attention(kpis)
            action['attention_created'] = True

        elif to_level == 3:
            # Auto-archive stale items
            archived = self._auto_archive_stale(now)
            action['archived_count'] = archived

        self._set_level(to_level, now)
        self._reset_clean_cycles()

        AutopilotAction.objects.create(
            action_type='backlog_govern',
            agent_name='BacklogGovernor',
            policy='backlog_governor',
            dry_run=False,
            evidence={
                'ladder_from': from_level,
                'ladder_to': to_level,
                **{k: v for k, v in kpis.items() if k != 'action'},
            },
            result=action,
            deploy_sha=self.deploy_sha,
        )

        self.actions.append(action)
        logger.info(
            f"[BacklogGovernor] ESCALATE L{from_level}→L{to_level} "
            f"(ready={kpis.get('publish_ready_count')}, "
            f"p95={kpis.get('p95_age_hours', 0):.0f}h)"
        )
        return action

    def _de_escalate(self, current_level: int, now) -> dict:
        """De-escalate one level — clean up current level's state."""
        from core.models.system import SystemConfiguration

        new_level = current_level - 1
        action = {
            'action': 'de_escalate',
            'from_level': current_level,
            'to_level': new_level,
        }

        if self.dry_run:
            action['dry_run'] = True
            return action

        # Clean up current level's config
        if current_level == 1:
            SystemConfiguration.objects.filter(key=self.KEY_THROTTLE).delete()

        if new_level > 0:
            self._set_level(new_level, now)
        else:
            self._clear_state()

        self._reset_clean_cycles()

        AutopilotAction.objects.create(
            action_type='backlog_govern',
            agent_name='BacklogGovernor',
            policy='backlog_governor',
            dry_run=False,
            evidence={
                'ladder_from': current_level,
                'ladder_to': new_level,
                'recovery': True,
            },
            result=action,
            deploy_sha=self.deploy_sha,
        )

        self.actions.append(action)
        logger.info(
            f"[BacklogGovernor] DE-ESCALATE L{current_level}→L{new_level}"
        )
        return action

    def _auto_archive_stale(self, now) -> int:
        """
        Archive stale deliverables with guardrails.

        Never archive:
        - is_pinned, is_saved, is_starred
        - quality_score >= QUALITY_FLOOR
        - linked to an initiative
        """
        from core.models_deliverables import Deliverable

        stale_cutoff = now - timedelta(days=self.STALE_AGE_DAYS)

        stale_qs = Deliverable.objects.filter(
            status__in=['draft', 'ready'],
            created_at__lt=stale_cutoff,
            is_pinned=False,
            is_saved=False,
            is_starred=False,
            initiative__isnull=True,
        ).exclude(
            quality_score__gte=self.QUALITY_FLOOR,
        )

        count = stale_qs.count()
        if count > 0:
            stale_qs.update(status='archived')
            logger.info(
                f"[BacklogGovernor] Auto-archived {count} stale deliverables "
                f"(older than {self.STALE_AGE_DAYS} days)"
            )
        return count

    def _create_backlog_attention(self, kpis: dict):
        """Create governance attention item for backlog review."""
        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()

            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user = User.objects.first()
            if not user:
                return

            HumanAttentionItem.objects.create(
                user=user,
                source_type='ops_autopilot',
                source_agent='BacklogGovernor',
                item_type='alert',
                title=(
                    f"Backlog review: {kpis.get('publish_ready_count', 0)} "
                    f"items, p95 age {kpis.get('p95_age_hours', 0):.0f}h"
                )[:200],
                summary=(
                    f"Deliverable backlog needs attention. "
                    f"{kpis.get('publish_ready_count', 0)} ready/draft items, "
                    f"p95 age {kpis.get('p95_age_hours', 0):.0f}h, "
                    f"conversion rate {kpis.get('conversion_rate_pct', 0):.1f}%. "
                    f"Review and publish or archive stale items."
                ),
                payload={
                    'policy': 'backlog_governor',
                    **{k: v for k, v in kpis.items() if k != 'action'},
                },
                urgency='medium',
            )
        except Exception as e:
            logger.error(f"[BacklogGovernor] attention item error: {e}")

    # ── State tracking ──────────────────────────────────────────────

    def _get_level(self) -> int:
        from core.models.system import SystemConfiguration
        entry = SystemConfiguration.objects.filter(key=self.KEY_LEVEL).first()
        return int(entry.value) if entry else 0

    def _set_level(self, level: int, now):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL,
            defaults={'value': str(level)},
        )
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL_TS,
            defaults={'value': now.isoformat()},
        )

    def _get_level_timestamp(self):
        from core.models.system import SystemConfiguration
        from django.utils.dateparse import parse_datetime
        entry = SystemConfiguration.objects.filter(key=self.KEY_LEVEL_TS).first()
        return parse_datetime(entry.value) if entry else None

    def _increment_clean_cycles(self) -> int:
        from core.models.system import SystemConfiguration
        obj, _ = SystemConfiguration.objects.get_or_create(
            key=self.KEY_CLEAN_CYCLES,
            defaults={'value': '0'},
        )
        new_val = int(obj.value or '0') + 1
        obj.value = str(new_val)
        obj.save(update_fields=['value'])
        return new_val

    def _reset_clean_cycles(self):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.filter(key=self.KEY_CLEAN_CYCLES).update(value='0')

    def _clear_state(self):
        from core.models.system import SystemConfiguration
        SystemConfiguration.objects.filter(
            key__in=[
                self.KEY_LEVEL, self.KEY_LEVEL_TS, self.KEY_CLEAN_CYCLES,
                self.KEY_THROTTLE,
            ]
        ).delete()

    def get_backlog_report(self, now) -> dict:
        """Report current backlog health + governor state."""
        from core.models_deliverables import Deliverable
        from django.db.models import Count, Avg

        # Status distribution
        by_status = dict(
            Deliverable.objects.values_list('status').annotate(
                count=Count('id')
            )
        )

        # Backlog KPIs
        ready_count = by_status.get('ready', 0)
        draft_count = by_status.get('draft', 0)

        # p95 age
        backlog_qs = Deliverable.objects.filter(
            status__in=['ready', 'draft'],
        ).order_by('created_at')

        p95_age = 0.0
        if backlog_qs.exists():
            total = backlog_qs.count()
            p95_idx = max(0, int(total * 0.95) - 1)
            p95_item = backlog_qs[p95_idx]
            p95_age = round(
                (now - p95_item.created_at).total_seconds() / 3600, 1,
            )

        # Conversion rate
        window = now - timedelta(days=self.KPI_WINDOW_DAYS)
        window_total = Deliverable.objects.filter(
            created_at__gte=window,
        ).count()
        window_published = Deliverable.objects.filter(
            created_at__gte=window, status='published',
        ).count()
        conversion = round(
            (window_published / max(window_total, 1)) * 100, 1,
        )

        # Protected items count
        from django.db.models import Q
        protected = Deliverable.objects.filter(
            status__in=['ready', 'draft'],
        ).filter(
            Q(is_pinned=True)
            | Q(is_saved=True)
            | Q(is_starred=True)
            | Q(quality_score__gte=self.QUALITY_FLOOR)
            | Q(initiative__isnull=False)
        ).count()

        # Stale items eligible for archive
        stale_cutoff = now - timedelta(days=self.STALE_AGE_DAYS)
        stale_archivable = Deliverable.objects.filter(
            status__in=['draft', 'ready'],
            created_at__lt=stale_cutoff,
            is_pinned=False,
            is_saved=False,
            is_starred=False,
            initiative__isnull=True,
        ).exclude(
            quality_score__gte=self.QUALITY_FLOOR,
        ).count()

        # Governor state
        level = self._get_level()
        level_ts = self._get_level_timestamp()

        return {
            'status_distribution': by_status,
            'publish_ready_count': ready_count,
            'draft_count': draft_count,
            'p95_age_hours': p95_age,
            'conversion_rate_pct': conversion,
            'window_days': self.KPI_WINDOW_DAYS,
            'protected_items': protected,
            'stale_archivable': stale_archivable,
            'stale_age_days': self.STALE_AGE_DAYS,
            'governor_level': level,
            'governor_level_since': level_ts.isoformat() if level_ts else None,
            'level_description': {
                0: 'Normal operation',
                1: 'Generation throttled',
                2: 'Governance attention batch active',
                3: 'Auto-archiving stale items',
            }.get(level, 'Unknown'),
            'throttle_active': self._is_throttled(),
        }

    def _is_throttled(self) -> bool:
        from core.models.system import SystemConfiguration
        entry = SystemConfiguration.objects.filter(key=self.KEY_THROTTLE).first()
        return entry is not None and entry.value == 'true'


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

        # Never throttle PA or its core subsystems — user-facing chat must
        # always work regardless of ROI score.
        THROTTLE_EXEMPT = frozenset({
            'PersonalAssistant', 'KnowledgeFirstRouter',
            'conversation_tool', 'scoped_retrieval', 'system',
        })

        for rec in recommendations:
            if rec['agent_name'] in THROTTLE_EXEMPT:
                continue
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

    def backfill(self, days=14) -> dict:
        """
        Backfill ImpactEvents for the last N days.
        Idempotent — skips events that already exist (keyed on
        source_object_type + source_object_id).
        """
        from django.utils import timezone as tz
        now = tz.now()
        window_start = now - timedelta(days=days)

        results = {'wagers': 0, 'deliverable_events': 0, 'revenues': 0}

        try:
            results['wagers'] = self._collect_wager_impacts(window_start)
        except Exception as e:
            logger.error(f"[ImpactCollector] Backfill wager error: {e}")

        try:
            results['deliverable_events'] = (
                self._collect_deliverable_impacts(window_start)
            )
        except Exception as e:
            logger.error(f"[ImpactCollector] Backfill deliverable error: {e}")

        try:
            results['revenues'] = self._collect_revenue_impacts(window_start)
        except Exception as e:
            logger.error(f"[ImpactCollector] Backfill revenue error: {e}")

        results['total_created'] = sum(results.values())
        results['backfill_days'] = days

        logger.info(
            f"[ImpactCollector] Backfill {days}d: "
            f"{results['total_created']} events created "
            f"(wagers={results['wagers']}, "
            f"deliverables={results['deliverable_events']}, "
            f"revenues={results['revenues']})"
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
    Session 1089: Autonomy #8/#9 — Allocates budget and scheduling
    priority across desks/pipelines based on Impact-adjusted QROI (IQROI).

    IQROI = (impact_value_usd + impact_points × point_usd_value) / cost_usd

    Guardrails (Session 1089 — smoothing):
    - MIN_EVENTS: minimum impact events before reallocating (prevents noise)
    - MIN_COST_USD: minimum spend before reallocating (ignore trivial desks)
    - ALLOCATION_FLOOR / CEILING: bounds to prevent starvation or runaway
    - EWMA smoothing: blend new IQROI with prior allocation to avoid swings
    """

    # Default impact-point-to-USD conversion (1 point ≈ $0.10)
    POINT_USD_VALUE = 0.10

    # Minimum thresholds before we deviate from neutral allocation
    MIN_EVENTS = 3       # Need at least 3 impact events to reallocate
    MIN_COST_USD = 0.05  # Need at least $0.05 spend to be worth tracking

    # Allocation bounds — no desk gets starved or runs away
    ALLOCATION_FLOOR = 0.5    # Minimum allocation multiplier
    ALLOCATION_CEILING = 1.5  # Maximum allocation multiplier

    # EWMA smoothing factor (0.3 = 30% new value, 70% prior)
    EWMA_ALPHA = 0.3

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

            # Determine raw allocation from IQROI
            # IQROI > 1.0 → producing more value than cost → boost
            # IQROI < 0.5 → underperforming → reduce
            insufficient_data = (
                events < self.MIN_EVENTS
                and cost < self.MIN_COST_USD
            )

            if insufficient_data:
                raw_allocation = 1.0  # Neutral — not enough data
            elif iqroi >= 2.0:
                raw_allocation = 1.5
            elif iqroi >= 1.0:
                raw_allocation = 1.2
            elif iqroi >= 0.5:
                raw_allocation = 1.0
            elif iqroi >= 0.1:
                raw_allocation = 0.7
            else:
                raw_allocation = 0.5

            # EWMA smoothing: blend with prior allocation
            prior = self._get_prior_allocation(desk)
            if prior is not None and not insufficient_data:
                allocation = (
                    self.EWMA_ALPHA * raw_allocation
                    + (1 - self.EWMA_ALPHA) * prior
                )
            else:
                allocation = raw_allocation

            # Clamp to floor/ceiling
            allocation = max(
                self.ALLOCATION_FLOOR,
                min(self.ALLOCATION_CEILING, allocation),
            )
            allocation = round(allocation, 2)

            results[desk] = {
                'iqroi': round(iqroi, 4),
                'impact_usd': round(impact_usd, 4),
                'impact_points': impact_pts,
                'total_impact_value': round(total_impact, 4),
                'cost_usd': round(cost, 4),
                'events': events,
                'allocation': allocation,
                'raw_allocation': raw_allocation,
                'insufficient_data': insufficient_data,
            }

        return results

    def _get_prior_allocation(self, desk: str) -> float | None:
        """Read prior allocation from SystemConfiguration for EWMA."""
        from core.models.system import SystemConfiguration

        try:
            entry = SystemConfiguration.objects.filter(
                key=f'desk_allocation:{desk}',
            ).values_list('value', flat=True).first()

            if entry and isinstance(entry, dict):
                return entry.get('allocation')
        except Exception:
            pass
        return None

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


# ═══════════════════════════════════════════════════════════════════════
# Goal-Aware Allocator — Policy 20 (Autonomy #16)
# ═══════════════════════════════════════════════════════════════════════


class GoalAwareAllocator:
    """
    Maps system-level objectives to desk-level budget multipliers
    via a weighted utility function.

    Objectives (default balanced weights):
      - sports_profit   0.25  — wager P/L from ImpactEvent
      - confirmed_revenue 0.25 — revenue_confirmed from ImpactEvent
      - content_engagement 0.20 — content action/save/export points
      - quality          0.15  — avg quality_score of recent deliverables
      - freshness        0.15  — recently published as % of total

    Each desk computes a utility score [0,1] from the objectives
    relevant to it. The score maps to an allocation multiplier:
      utility 0 → 0.75x (floor)
      utility 1 → 1.25x (ceiling)

    Multipliers are written to SystemConfiguration as
    'goal_allocation:{desk}' and modulate the IQROI-based allocation
    from PortfolioAllocator.

    Weights are stored in SystemConfiguration key 'goal_weights'
    and adjustable via PA tool action 'goal_set_weights'.
    """

    # Default objective weights (sum = 1.0)
    DEFAULT_WEIGHTS = {
        'sports_profit': 0.25,
        'confirmed_revenue': 0.25,
        'content_engagement': 0.20,
        'quality': 0.15,
        'freshness': 0.15,
    }

    # Desk→objective relevance matrix (which objectives matter for each desk)
    DESK_OBJECTIVES = {
        'sports': ['sports_profit', 'confirmed_revenue', 'quality'],
        'content': ['confirmed_revenue', 'content_engagement', 'quality', 'freshness'],
        'research': ['quality', 'freshness'],
        'career': ['confirmed_revenue', 'quality'],
        'trading': ['sports_profit', 'confirmed_revenue', 'quality'],
        'general': ['quality'],
    }

    # Allocation bounds (tighter than PortfolioAllocator to avoid conflict)
    FLOOR = 0.75
    CEILING = 1.25
    EWMA_ALPHA = 0.3

    # Metric lookback
    WINDOW_HOURS = 72

    # SystemConfiguration keys
    KEY_WEIGHTS = 'goal_weights'

    def get_weights(self) -> dict:
        """Get current objective weights from config or defaults."""
        from core.models.system import SystemConfiguration
        try:
            entry = SystemConfiguration.objects.filter(
                key=self.KEY_WEIGHTS,
            ).first()
            if entry and isinstance(entry.value, dict):
                return entry.value
        except Exception:
            pass
        return dict(self.DEFAULT_WEIGHTS)

    def set_weights(self, weights: dict) -> dict:
        """Set objective weights. Normalizes to sum=1.0."""
        from core.models.system import SystemConfiguration

        total = sum(weights.values())
        if total <= 0:
            return {'error': 'Weights must sum to > 0'}

        normalized = {k: round(v / total, 4) for k, v in weights.items()}

        SystemConfiguration.objects.update_or_create(
            key=self.KEY_WEIGHTS,
            defaults={
                'value': normalized,
                'description': 'Goal-aware allocator objective weights',
                'category': 'performance',
            },
        )
        return {'weights': normalized, 'normalized': True}

    def compute_metrics(self, now) -> dict:
        """Compute current system-level objective metrics."""
        from django.db.models import Sum, Count, Avg

        window = now - timedelta(hours=self.WINDOW_HOURS)
        metrics = {}

        # Sports profit — total wager P/L from ImpactEvent
        try:
            from core.models_impact_events import ImpactEvent
            sports_impact = ImpactEvent.objects.filter(
                created_at__gte=window,
                desk='sports',
                impact_type='wager_profit',
            ).aggregate(total=Sum('value_usd'))
            val = float(sports_impact['total'] or 0)
            # Normalize: $0 = 0.5, ±$100 = 0/1 (sigmoid-like)
            metrics['sports_profit'] = max(0, min(1, 0.5 + val / 200))
        except Exception:
            metrics['sports_profit'] = 0.5

        # Confirmed revenue
        try:
            from core.models_impact_events import ImpactEvent
            rev = ImpactEvent.objects.filter(
                created_at__gte=window,
                impact_type='revenue_confirmed',
            ).aggregate(total=Sum('value_usd'))
            val = float(rev['total'] or 0)
            # Normalize: $0 = 0, $50+ = 1.0
            metrics['confirmed_revenue'] = min(1.0, val / 50)
        except Exception:
            metrics['confirmed_revenue'] = 0.0

        # Content engagement (impact points from content actions)
        try:
            from core.models_impact_events import ImpactEvent
            eng = ImpactEvent.objects.filter(
                created_at__gte=window,
                desk='content',
                impact_type__in=[
                    'content_action', 'content_save',
                    'content_export', 'content_share',
                ],
            ).aggregate(total=Sum('impact_points'))
            pts = eng['total'] or 0
            # Normalize: 0 pts = 0, 50+ pts = 1.0
            metrics['content_engagement'] = min(1.0, pts / 50)
        except Exception:
            metrics['content_engagement'] = 0.0

        # Quality — average quality_score of recent deliverables
        try:
            from core.models_deliverables import Deliverable
            avg_q = Deliverable.objects.filter(
                created_at__gte=window,
                quality_score__gt=0,
            ).aggregate(avg=Avg('quality_score'))
            metrics['quality'] = float(avg_q['avg'] or 0)
        except Exception:
            metrics['quality'] = 0.0

        # Freshness — ratio of published in window vs total unpublished
        try:
            from core.models_deliverables import Deliverable
            published = Deliverable.objects.filter(
                created_at__gte=window, status='published',
            ).count()
            unpublished = Deliverable.objects.filter(
                status__in=['draft', 'ready'],
            ).count()
            total = published + unpublished
            metrics['freshness'] = (published / max(total, 1))
        except Exception:
            metrics['freshness'] = 0.0

        return metrics

    def compute_desk_utility(self, now) -> dict:
        """
        Compute utility score per desk based on objective weights
        and desk-relevant metrics.
        """
        weights = self.get_weights()
        metrics = self.compute_metrics(now)

        desk_scores = {}
        for desk, objectives in self.DESK_OBJECTIVES.items():
            # Weighted average of relevant objectives
            total_weight = 0
            weighted_sum = 0
            for obj in objectives:
                w = weights.get(obj, 0)
                m = metrics.get(obj, 0)
                weighted_sum += w * m
                total_weight += w

            utility = weighted_sum / max(total_weight, 0.001)
            desk_scores[desk] = {
                'utility': round(utility, 4),
                'objectives': {
                    obj: {
                        'weight': weights.get(obj, 0),
                        'metric': round(metrics.get(obj, 0), 4),
                    }
                    for obj in objectives
                },
            }

        return desk_scores

    def apply_goal_allocations(self, now) -> dict:
        """
        Compute goal-derived multipliers and write to SystemConfiguration.

        Returns dict of {desk: {multiplier, utility, prior}}.
        """
        from core.models.system import SystemConfiguration

        desk_scores = self.compute_desk_utility(now)
        adjustments = {}

        for desk, data in desk_scores.items():
            utility = data['utility']

            # Linear map: utility 0 → floor, utility 1 → ceiling
            raw_mult = self.FLOOR + (self.CEILING - self.FLOOR) * utility

            # EWMA with prior
            prior = self._get_prior(desk)
            if prior is not None:
                mult = self.EWMA_ALPHA * raw_mult + (1 - self.EWMA_ALPHA) * prior
            else:
                mult = raw_mult

            mult = round(max(self.FLOOR, min(self.CEILING, mult)), 3)

            key = f'goal_allocation:{desk}'
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': {
                        'multiplier': mult,
                        'utility': utility,
                        'updated_at': now.isoformat(),
                    },
                    'description': (
                        f"Goal allocation: {desk} — "
                        f"utility {utility:.3f}, mult {mult}x"
                    ),
                    'category': 'performance',
                },
            )

            adjustments[desk] = {
                'multiplier': mult,
                'utility': utility,
                'raw_multiplier': round(raw_mult, 3),
                'prior': prior,
            }

        return adjustments

    def _get_prior(self, desk: str):
        """Read prior goal allocation for EWMA."""
        from core.models.system import SystemConfiguration
        try:
            entry = SystemConfiguration.objects.filter(
                key=f'goal_allocation:{desk}',
            ).values_list('value', flat=True).first()
            if entry and isinstance(entry, dict):
                return entry.get('multiplier')
        except Exception:
            pass
        return None

    def get_goal_report(self, now) -> dict:
        """Generate goal allocation report for PA/governance."""
        weights = self.get_weights()
        metrics = self.compute_metrics(now)
        desk_scores = self.compute_desk_utility(now)

        # Active allocations
        from core.models.system import SystemConfiguration
        active = {}
        try:
            entries = SystemConfiguration.objects.filter(
                key__startswith='goal_allocation:',
            ).values('key', 'value')
            for e in entries:
                desk = e['key'].replace('goal_allocation:', '')
                active[desk] = e['value']
        except Exception:
            pass

        return {
            'weights': weights,
            'metrics': {k: round(v, 4) for k, v in metrics.items()},
            'desk_scores': desk_scores,
            'active_allocations': active,
            'window_hours': self.WINDOW_HOURS,
            'bounds': {'floor': self.FLOOR, 'ceiling': self.CEILING},
        }


# ═══════════════════════════════════════════════════════════════════════
# Multi-Touch Attributor — Policy 21 (Autonomy #17)
# ═══════════════════════════════════════════════════════════════════════


class MultiTouchAttributor:
    """
    Allocates ImpactEvent credit across upstream agents/desks using
    multi-touch attribution.

    Credit split:
    - 70% last-touch: the agent/desk directly producing the impact
    - 30% assist: split among upstream linked agents/desks

    Links are discovered via:
    1. trace_id: same orchestration trace → shared credit
    2. initiative: deliverable linked to initiative → initiative creator
    3. dream: deliverable linked to dream → dream agent
    4. agent_chain: AgentExecution parent → child relationships

    Guardrails:
    - Max 2 hops upstream
    - Max 30% total assist credit
    - Only explicit links (no guessing)
    - Idempotent: skip events already attributed
    """

    LAST_TOUCH_SHARE = 0.70
    ASSIST_SHARE = 0.30
    MAX_HOPS = 2

    # Desk lookup for known agents (reuse from AttributionDebtController)
    # Falls back to ImpactEvent.desk or 'general'

    def attribute_recent(self, now, window_hours: int = 24) -> dict:
        """
        Process recent ImpactEvents that don't have credits yet.
        Idempotent: skips events already attributed.
        """
        from core.models_impact_events import ImpactEvent
        from core.models_impact_credit import ImpactCredit

        window = now - timedelta(hours=window_hours)

        # Find unattributed events (no credits yet)
        attributed_ids = set(
            ImpactCredit.objects.filter(
                created_at__gte=window,
            ).values_list('impact_event_id', flat=True).distinct()
        )

        events = ImpactEvent.objects.filter(
            created_at__gte=window,
        ).exclude(id__in=attributed_ids)

        result = {
            'events_processed': 0,
            'credits_created': 0,
            'errors': 0,
        }

        for event in events:
            try:
                credits = self._attribute_event(event)
                result['credits_created'] += len(credits)
                result['events_processed'] += 1
            except Exception as e:
                logger.error(
                    f"[MultiTouchAttributor] Error attributing "
                    f"event {event.id}: {e}"
                )
                result['errors'] += 1

        return result

    def _attribute_event(self, event) -> list:
        """
        Attribute a single ImpactEvent. Creates ImpactCredit rows.

        Returns list of created ImpactCredit objects.
        """
        from core.models_impact_credit import ImpactCredit

        value_usd = float(event.value_usd or 0)
        points = event.impact_points or 0
        credits = []

        # Discover upstream links
        upstream = self._find_upstream(event)

        if not upstream:
            # No assist — 100% last touch
            credits.append(ImpactCredit.objects.create(
                impact_event=event,
                desk=event.desk,
                agent_name=event.agent_name or '',
                credit_type='last_touch',
                credit_usd=value_usd,
                credit_points=points,
                credit_share=1.0,
                hop_distance=0,
                link_type='direct',
            ))
        else:
            # Last touch gets 70%
            credits.append(ImpactCredit.objects.create(
                impact_event=event,
                desk=event.desk,
                agent_name=event.agent_name or '',
                credit_type='last_touch',
                credit_usd=round(value_usd * self.LAST_TOUCH_SHARE, 4),
                credit_points=int(points * self.LAST_TOUCH_SHARE),
                credit_share=self.LAST_TOUCH_SHARE,
                hop_distance=0,
                link_type='direct',
            ))

            # Assist 30% split evenly among upstream
            assist_per = self.ASSIST_SHARE / len(upstream)
            for link in upstream:
                credits.append(ImpactCredit.objects.create(
                    impact_event=event,
                    desk=link['desk'],
                    agent_name=link.get('agent_name', ''),
                    credit_type='assist',
                    credit_usd=round(value_usd * assist_per, 4),
                    credit_points=int(points * assist_per),
                    credit_share=round(assist_per, 4),
                    hop_distance=link.get('hop', 1),
                    link_type=link.get('link_type', 'unknown'),
                ))

        return credits

    def _find_upstream(self, event) -> list:
        """
        Discover upstream agents/desks linked to this impact event.

        Returns list of dicts: [{'desk', 'agent_name', 'hop', 'link_type'}]
        """
        upstream = []

        # Strategy 1: trace_id — find other agents in same orchestration
        if event.trace_id:
            trace_links = self._find_by_trace(event)
            upstream.extend(trace_links)

        # Strategy 2: source_object → Deliverable → initiative/dream
        if event.source_object_type == 'Deliverable' and event.source_object_id:
            deliverable_links = self._find_by_deliverable(event)
            upstream.extend(deliverable_links)

        # Deduplicate by (desk, agent_name) and cap at MAX_HOPS
        seen = set()
        deduped = []
        for link in upstream:
            key = (link['desk'], link.get('agent_name', ''))
            # Skip self-attribution
            if key == (event.desk, event.agent_name or ''):
                continue
            if key not in seen and link.get('hop', 1) <= self.MAX_HOPS:
                seen.add(key)
                deduped.append(link)

        return deduped

    def _find_by_trace(self, event) -> list:
        """Find upstream agents via shared trace_id."""
        links = []
        try:
            from core.models_deliverables import Deliverable

            # Find deliverables with same trace_id
            related = Deliverable.objects.filter(
                trace_id=event.trace_id,
            ).exclude(
                agent_name=event.agent_name or '',
            ).values('agent_name', 'initiative_id').distinct()[:5]

            for d in related:
                agent = d['agent_name'] or ''
                desk = self._agent_to_desk(agent)
                links.append({
                    'desk': desk,
                    'agent_name': agent,
                    'hop': 1,
                    'link_type': 'trace_id',
                })
        except Exception:
            pass
        return links

    def _find_by_deliverable(self, event) -> list:
        """Find upstream agents via deliverable → initiative/dream chain."""
        links = []
        try:
            from core.models_deliverables import Deliverable

            deliverable = Deliverable.objects.filter(
                id=event.source_object_id,
            ).select_related('initiative', 'dream').first()

            if not deliverable:
                return links

            # Initiative link — the initiative was created by some upstream work
            if deliverable.initiative_id:
                links.append({
                    'desk': 'research',
                    'agent_name': 'InitiativePipeline',
                    'hop': 1,
                    'link_type': 'initiative',
                })

            # Dream link — the dream was the creative spark
            if deliverable.dream_id:
                try:
                    dream_agent = deliverable.dream.agent_name or 'DreamAgent'
                    links.append({
                        'desk': self._agent_to_desk(dream_agent),
                        'agent_name': dream_agent,
                        'hop': 1,
                        'link_type': 'dream',
                    })
                except Exception:
                    links.append({
                        'desk': 'research',
                        'agent_name': 'DreamAgent',
                        'hop': 1,
                        'link_type': 'dream',
                    })

            # SelfBlog link — upstream content agent
            if deliverable.self_blog_id:
                links.append({
                    'desk': 'content',
                    'agent_name': 'ContentWriterAgent',
                    'hop': 1,
                    'link_type': 'self_blog',
                })

        except Exception:
            pass
        return links

    def _agent_to_desk(self, agent_name: str) -> str:
        """Map agent name to desk. Falls back to 'general'."""
        try:
            desk_map = AttributionDebtController.AGENT_DESK_MAP
            return desk_map.get(agent_name, 'general')
        except Exception:
            return 'general'

    def get_attribution_report(self, now) -> dict:
        """Report on multi-touch attribution state."""
        from core.models_impact_credit import ImpactCredit
        from django.db.models import Sum, Count

        window = now - timedelta(hours=72)

        # Credits by desk and type
        desk_credits = list(
            ImpactCredit.objects.filter(
                created_at__gte=window,
            ).values('desk', 'credit_type').annotate(
                total_usd=Sum('credit_usd'),
                total_points=Sum('credit_points'),
                count=Count('id'),
            ).order_by('desk', 'credit_type')
        )

        # Format
        by_desk = {}
        for row in desk_credits:
            desk = row['desk']
            if desk not in by_desk:
                by_desk[desk] = {'last_touch': {}, 'assist': {}}
            by_desk[desk][row['credit_type']] = {
                'usd': float(row['total_usd'] or 0),
                'points': row['total_points'] or 0,
                'count': row['count'] or 0,
            }

        # Total attributed vs unattributed
        from core.models_impact_events import ImpactEvent
        total_events = ImpactEvent.objects.filter(
            created_at__gte=window,
        ).count()
        attributed_events = ImpactCredit.objects.filter(
            created_at__gte=window,
            credit_type='last_touch',
        ).count()

        return {
            'window_hours': 72,
            'total_events': total_events,
            'attributed_events': attributed_events,
            'unattributed_events': total_events - attributed_events,
            'credits_by_desk': by_desk,
            'total_credits': ImpactCredit.objects.filter(
                created_at__gte=window,
            ).count(),
        }


# ═══════════════════════════════════════════════════════════════════════
# Policy Arbitrator — Policy 22 (Autonomy #18)
# ═══════════════════════════════════════════════════════════════════════

class PolicyArbitrator:
    """
    Resolves conflicts when multiple policies write the same
    SystemConfiguration knob in the same autopilot cycle.

    Design:
    - Maintains a knob registry mapping config keys to owning policies
      with priority and merge strategy.
    - Anti-flap: minimum hold time (2h) and max delta (±0.05) per cycle
      for numeric knobs.
    - Records a FinalAppliedOverrides snapshot per cycle in the
      DecisionLedger for audit trail.

    Merge strategies:
    - priority_wins: highest-priority policy's value applies
    - max: largest numeric value wins (conservative/safe)
    - min: smallest numeric value wins (conservative/safe)
    - last_writer_wins: last policy to write wins (legacy default)
    - bool_or: any True wins (safety: if any policy wants a freeze, freeze)
    - bool_and: all must agree True (permissive)
    """

    # Priority: lower number = higher priority
    # Safety/Reliability > Budget > Remediation > Backlog > Goal optimization
    KNOB_REGISTRY = {
        # Budget controller (P10) — safety-critical
        'budget_freeze_active': {
            'owner': 'budget_controller',
            'priority': 10,
            'merge': 'bool_or',
            'hold_hours': 1,
        },
        'budget_downgrade_active': {
            'owner': 'budget_controller',
            'priority': 10,
            'merge': 'bool_or',
            'hold_hours': 1,
        },
        'budget_mode': {
            'owner': 'budget_controller',
            'priority': 10,
            'merge': 'priority_wins',
            'hold_hours': 1,
        },
        # ROI enforcer (P11)
        'roi_throttle:*': {
            'owner': 'roi_enforcement',
            'priority': 20,
            'merge': 'priority_wins',
            'hold_hours': 2,
        },
        # Portfolio allocator (P12) — desk allocations
        'desk_allocation:*': {
            'owner': 'impact_portfolio',
            'priority': 30,
            'merge': 'max',
            'hold_hours': 2,
            'max_delta': 0.05,
        },
        # Goal allocator (P20) — goal-derived multipliers
        'goal_allocation:*': {
            'owner': 'goal_aware_allocator',
            'priority': 35,
            'merge': 'priority_wins',
            'hold_hours': 2,
            'max_delta': 0.05,
        },
        'goal_weights': {
            'owner': 'goal_aware_allocator',
            'priority': 35,
            'merge': 'priority_wins',
            'hold_hours': 4,
        },
        # Timeout remediation playbook (P15)
        'timeout_ladder_level:*': {
            'owner': 'timeout_remediation_playbook',
            'priority': 25,
            'merge': 'max',
            'hold_hours': 2,
        },
        'timeout_ladder_batch_reduce:*': {
            'owner': 'timeout_remediation_playbook',
            'priority': 25,
            'merge': 'priority_wins',
            'hold_hours': 2,
        },
        # Deliberation remediation playbook (P16)
        'delib_ladder_level': {
            'owner': 'deliberation_remediation_playbook',
            'priority': 25,
            'merge': 'max',
            'hold_hours': 2,
        },
        'deliberation_panel_size_override': {
            'owner': 'deliberation_remediation_playbook',
            'priority': 25,
            'merge': 'min',
            'hold_hours': 2,
        },
        'deliberation_reviewer_model_override': {
            'owner': 'deliberation_remediation_playbook',
            'priority': 25,
            'merge': 'priority_wins',
            'hold_hours': 2,
        },
        'deliberation_single_reviewer_mode': {
            'owner': 'deliberation_remediation_playbook',
            'priority': 25,
            'merge': 'bool_or',
            'hold_hours': 2,
        },
        # Backlog governor (P19)
        'backlog_generation_throttled': {
            'owner': 'backlog_governor',
            'priority': 40,
            'merge': 'bool_or',
            'hold_hours': 2,
        },
        'backlog_governor_level': {
            'owner': 'backlog_governor',
            'priority': 40,
            'merge': 'max',
            'hold_hours': 2,
        },
        # Release governor (P23)
        'deploy_freeze': {
            'owner': 'release_governor',
            'priority': 5,
            'merge': 'bool_or',
            'hold_hours': 1,
        },
        'deploy_backoff_seconds': {
            'owner': 'release_governor',
            'priority': 5,
            'merge': 'max',
            'hold_hours': 1,
        },
        'deploy_governor_level': {
            'owner': 'release_governor',
            'priority': 5,
            'merge': 'max',
            'hold_hours': 1,
        },
    }

    # Anti-flap defaults
    DEFAULT_HOLD_HOURS = 2
    DEFAULT_MAX_DELTA = 0.05  # for numeric desk/goal allocations

    def __init__(self):
        self._pending_writes: dict[str, list[dict]] = {}

    def register_write(self, key: str, value: Any, policy: str):
        """
        Record an intended write from a policy. Call this instead of
        writing directly to SystemConfiguration.

        For now this is observational — policies still write directly,
        and the arbitrator detects conflicts post-hoc.
        """
        if key not in self._pending_writes:
            self._pending_writes[key] = []
        self._pending_writes[key].append({
            'policy': policy,
            'value': value,
            'ts': timezone.now().isoformat(),
        })

    def _match_registry(self, key: str) -> dict | None:
        """Look up knob registry entry, supporting wildcard patterns."""
        if key in self.KNOB_REGISTRY:
            return self.KNOB_REGISTRY[key]

        # Check wildcard patterns (e.g., 'desk_allocation:*')
        prefix = key.split(':')[0] + ':*' if ':' in key else None
        if prefix and prefix in self.KNOB_REGISTRY:
            return self.KNOB_REGISTRY[prefix]

        return None

    def detect_conflicts(self, now) -> dict:
        """
        Scan SystemConfiguration for knobs recently written by multiple
        policies (post-hoc conflict detection).

        Returns conflict report with:
        - conflicts: list of {key, writers, resolution}
        - flap_knobs: keys that changed value multiple times recently
        - suppressed: writes that should have been blocked by hold time
        """
        conflicts = []
        try:
            from core.models_decision_ledger import DecisionLedgerEntry

            window = now - timedelta(hours=6)

            # Get recent ledger entries to see which policies took actions
            entries = list(
                DecisionLedgerEntry.objects.filter(
                    cycle_ts__gte=window,
                    decision_type='action_taken',
                ).values('policy', 'inputs', 'cycle_ts', 'cycle_id')
                .order_by('-cycle_ts')[:200]
            )

            # Extract config key writes from policy inputs
            key_writers: dict[str, list[dict]] = {}
            for entry in entries:
                policy = entry['policy']
                inputs = entry.get('inputs') or {}

                # Infer which keys this policy wrote
                written_keys = self._infer_written_keys(policy, inputs)
                for key in written_keys:
                    if key not in key_writers:
                        key_writers[key] = []
                    key_writers[key].append({
                        'policy': policy,
                        'cycle_ts': str(entry['cycle_ts']),
                        'cycle_id': str(entry['cycle_id']),
                    })

            # Find actual conflicts (same key, multiple policies)
            for key, writers in key_writers.items():
                policies = list(set(w['policy'] for w in writers))
                if len(policies) > 1:
                    registry = self._match_registry(key)
                    resolution = 'unregistered'
                    if registry:
                        resolution = (
                            f"{registry['merge']} (owner={registry['owner']}, "
                            f"priority={registry['priority']})"
                        )
                    conflicts.append({
                        'key': key,
                        'writers': policies,
                        'write_count': len(writers),
                        'resolution': resolution,
                    })
        except Exception:
            pass

        # Detect flap knobs — keys that changed frequently
        flap_knobs = self._detect_flaps(now)

        # Detect hold-time violations
        suppressed = self._detect_hold_violations(now)

        return {
            'window_hours': 6,
            'conflicts': conflicts,
            'conflict_count': len(conflicts),
            'flap_knobs': flap_knobs,
            'flap_count': len(flap_knobs),
            'suppressed': suppressed,
            'suppressed_count': len(suppressed),
            'registered_knobs': len(self.KNOB_REGISTRY),
        }

    def _infer_written_keys(self, policy: str, inputs: dict) -> list[str]:
        """
        Infer which SystemConfiguration keys a policy wrote,
        based on known policy→key mappings.
        """
        keys = []

        # Budget controller
        if policy == 'budget_controller':
            for k in ['budget_freeze_active', 'budget_downgrade_active', 'budget_mode']:
                if inputs.get(k) or inputs.get('freeze') or inputs.get('downgrade'):
                    keys.append(k)

        # ROI enforcement
        elif policy == 'roi_enforcement':
            throttled = inputs.get('throttled_agents', [])
            if isinstance(throttled, list):
                for t in throttled:
                    name = t.get('agent_name', '') if isinstance(t, dict) else str(t)
                    if name:
                        keys.append(f'roi_throttle:{name}')

        # Impact portfolio
        elif policy == 'impact_portfolio':
            allocs = inputs.get('desk_allocations', {})
            if isinstance(allocs, dict):
                for desk in allocs:
                    keys.append(f'desk_allocation:{desk}')

        # Goal-aware allocator
        elif policy == 'goal_aware_allocator':
            allocs = inputs.get('allocations', {})
            if isinstance(allocs, dict):
                for desk in allocs:
                    keys.append(f'goal_allocation:{desk}')
            if inputs.get('weights_updated'):
                keys.append('goal_weights')

        # Timeout playbook
        elif policy == 'timeout_remediation_playbook':
            agent = inputs.get('agent_name', '')
            if agent:
                keys.append(f'timeout_ladder_level:{agent}')

        # Deliberation playbook
        elif policy == 'deliberation_remediation_playbook':
            if inputs.get('level') is not None:
                keys.append('delib_ladder_level')

        # Backlog governor
        elif policy == 'backlog_governor':
            if inputs.get('level') is not None:
                keys.append('backlog_governor_level')
            if inputs.get('throttled'):
                keys.append('backlog_generation_throttled')

        return keys

    def _detect_flaps(self, now) -> list[dict]:
        """
        Detect knobs that changed value 3+ times in the past 24 hours.
        Uses AutopilotAction history.
        """
        try:
            from core.models_diagnostic_pipeline import AutopilotAction
            from django.db.models import Count

            window = now - timedelta(hours=24)

            # Count action_taken entries per policy
            actions = list(
                AutopilotAction.objects.filter(
                    created_at__gte=window,
                    action_type__in=['deploy_watch', 'remediation'],
                ).values('policy').annotate(
                    count=Count('id'),
                ).filter(count__gte=3)
                .order_by('-count')[:10]
            )

            flaps = []
            for a in actions:
                policy = a['policy']
                # Map policy → knobs
                registry_knobs = [
                    k for k, v in self.KNOB_REGISTRY.items()
                    if v['owner'] == policy
                ]
                if registry_knobs:
                    flaps.append({
                        'policy': policy,
                        'action_count': a['count'],
                        'affected_knobs': registry_knobs,
                    })

            return flaps
        except Exception:
            return []

    def _detect_hold_violations(self, now) -> list[dict]:
        """
        Detect knobs that were changed before their hold time expired.
        """
        suppressed = []
        try:
            from core.models.system import SystemConfiguration
            from core.models_decision_ledger import DecisionLedgerEntry

            for key, registry in self.KNOB_REGISTRY.items():
                if '*' in key:
                    continue

                hold_hours = registry.get('hold_hours', self.DEFAULT_HOLD_HOURS)
                hold_window = now - timedelta(hours=hold_hours)

                entry = SystemConfiguration.objects.filter(key=key).first()
                if not entry:
                    continue

                if hasattr(entry, 'updated_at') and entry.updated_at:
                    if entry.updated_at > hold_window:
                        changes = DecisionLedgerEntry.objects.filter(
                            policy=registry['owner'],
                            decision_type='action_taken',
                            cycle_ts__gte=hold_window,
                        ).count()
                        if changes >= 2:
                            suppressed.append({
                                'key': key,
                                'owner': registry['owner'],
                                'hold_hours': hold_hours,
                                'changes_in_window': changes,
                            })
        except Exception:
            pass

        return suppressed

    def record_overrides_snapshot(self, now, cycle_id) -> dict:
        """
        Record a FinalAppliedOverrides snapshot in SystemConfiguration.
        Captures the current state of all registered knobs.
        """
        from core.models.system import SystemConfiguration
        import json

        snapshot = {}

        # Read all registered knobs (non-wildcard)
        for key, registry in self.KNOB_REGISTRY.items():
            if '*' in key:
                continue
            entry = SystemConfiguration.objects.filter(key=key).first()
            if entry:
                snapshot[key] = {
                    'value': entry.value,
                    'owner': registry['owner'],
                    'priority': registry['priority'],
                }

        # Also capture wildcard knobs by prefix
        for pattern in self.KNOB_REGISTRY:
            if '*' not in pattern:
                continue
            prefix = pattern.replace(':*', ':')
            entries = SystemConfiguration.objects.filter(
                key__startswith=prefix,
            ).values_list('key', 'value')[:50]
            for k, v in entries:
                snapshot[k] = {
                    'value': v,
                    'owner': self.KNOB_REGISTRY[pattern]['owner'],
                    'priority': self.KNOB_REGISTRY[pattern]['priority'],
                }

        # Store snapshot
        SystemConfiguration.objects.update_or_create(
            key='policy_arbitrator_snapshot',
            defaults={'value': json.dumps({
                'cycle_id': str(cycle_id),
                'ts': now.isoformat(),
                'knobs': snapshot,
                'knob_count': len(snapshot),
            })},
        )

        return {
            'knob_count': len(snapshot),
            'cycle_id': str(cycle_id),
        }

    def get_conflict_report(self, now, days: int = 1,
                            knob: str = '', policy: str = '') -> dict:
        """
        PA-facing conflict report with optional filters.
        """
        report = self.detect_conflicts(now)

        # Apply filters
        if knob:
            report['conflicts'] = [
                c for c in report['conflicts'] if knob in c['key']
            ]
            report['conflict_count'] = len(report['conflicts'])

        if policy:
            report['conflicts'] = [
                c for c in report['conflicts']
                if policy in c['writers']
            ]
            report['conflict_count'] = len(report['conflicts'])
            report['flap_knobs'] = [
                f for f in report['flap_knobs']
                if f['policy'] == policy
            ]
            report['flap_count'] = len(report['flap_knobs'])

        return report


# ═══════════════════════════════════════════════════════════════════════
# Release / Deploy Governor — Policy 23 (Autonomy #19)
# ═══════════════════════════════════════════════════════════════════════

class ReleaseGovernor:
    """
    Monitors Railway deploy health and applies graduated safety measures.

    Ladder:
      L0 — Observe: track deploy frequency, success rate, time-to-healthy.
      L1 — Backoff: enforce minimum gap between deploys, serialize builds.
      L2 — Gate: require healthy status before allowing next deploy.
      L3 — Freeze: auto-freeze deploys on SLO breach, governance attention.

    Knobs (SystemConfiguration):
      deploy_freeze           — bool, blocks all deploys
      deploy_backoff_seconds  — int, min gap between deploys
      deploy_governor_level   — current ladder level (0-3)
      deploy_governor_level_ts — when level last changed
      deploy_governor_clean   — consecutive clean cycles

    SLO signals:
      - AutopilotAction history for deploy_watch events
      - Error rate from recent cycles
      - Deploy SHA changes (frequency)
    """

    # Ladder thresholds
    EVAL_WINDOW_HOURS = 6
    DEPLOYS_PER_HOUR_WARNING = 4    # > 4 deploys/hour → L1
    DEPLOYS_PER_HOUR_CRITICAL = 8   # > 8 deploys/hour → L2
    ERROR_RATE_L2 = 0.15            # 15%+ error rate → L2
    ERROR_RATE_L3 = 0.30            # 30%+ error rate → L3

    # Backoff
    DEFAULT_BACKOFF_SECONDS = 300   # 5 minutes between deploys at L1
    FREEZE_BACKOFF_SECONDS = 1800   # 30 minutes at L3

    # Escalation / de-escalation
    ESCALATION_CYCLES = 3           # consecutive warning cycles to escalate
    RECOVERY_CYCLES = 6             # consecutive clean cycles to de-escalate

    # State keys
    KEY_LEVEL = 'deploy_governor_level'
    KEY_LEVEL_TS = 'deploy_governor_level_ts'
    KEY_CLEAN = 'deploy_governor_clean'
    KEY_FREEZE = 'deploy_freeze'
    KEY_BACKOFF = 'deploy_backoff_seconds'
    KEY_LAST_SHA = 'deploy_last_sha'
    KEY_LAST_DEPLOY_TS = 'deploy_last_ts'

    def evaluate(self, now) -> dict:
        """
        Evaluate deploy health and return ladder status.
        """
        from core.models.system import SystemConfiguration

        result = {
            'level': 0,
            'deploys_recent': 0,
            'deploy_rate_per_hour': 0.0,
            'error_rate': 0.0,
            'sha_changes': 0,
            'frozen': False,
        }

        # Current level
        level_entry = SystemConfiguration.objects.filter(
            key=self.KEY_LEVEL,
        ).first()
        current_level = int(level_entry.value) if level_entry else 0

        # Track deploy SHA changes
        current_sha = self._get_current_sha()
        last_sha_entry = SystemConfiguration.objects.filter(
            key=self.KEY_LAST_SHA,
        ).first()
        last_sha = last_sha_entry.value if last_sha_entry else ''

        if current_sha and current_sha != last_sha:
            # New deploy detected
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_LAST_SHA,
                defaults={'value': current_sha},
            )
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_LAST_DEPLOY_TS,
                defaults={'value': now.isoformat()},
            )

        # Count recent deploys (SHA changes in window)
        deploy_metrics = self._count_recent_deploys(now)
        result['deploys_recent'] = deploy_metrics['count']
        result['deploy_rate_per_hour'] = deploy_metrics['rate_per_hour']
        result['sha_changes'] = deploy_metrics['sha_changes']
        result['error_rate'] = deploy_metrics['error_rate']

        # Determine target level
        target_level = 0
        if result['error_rate'] >= self.ERROR_RATE_L3:
            target_level = 3
        elif (result['error_rate'] >= self.ERROR_RATE_L2
              or result['deploy_rate_per_hour'] >= self.DEPLOYS_PER_HOUR_CRITICAL):
            target_level = 2
        elif result['deploy_rate_per_hour'] >= self.DEPLOYS_PER_HOUR_WARNING:
            target_level = 1

        # Apply escalation / de-escalation
        if target_level > current_level:
            new_level = self._escalate(current_level, target_level, now)
        elif target_level < current_level:
            new_level = self._de_escalate(current_level, now)
        else:
            new_level = current_level
            # Track clean cycles for de-escalation
            if target_level == 0 and current_level > 0:
                self._increment_clean_cycles()

        # Apply level actions
        self._apply_level_actions(new_level, now)

        result['level'] = new_level
        result['frozen'] = new_level >= 3

        return result

    def _get_current_sha(self) -> str:
        """Get current deploy SHA."""
        import os
        sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '')
        if not sha:
            try:
                import subprocess
                sha = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'],
                    stderr=subprocess.DEVNULL,
                ).decode().strip()[:12]
            except Exception:
                sha = ''
        return sha[:40]

    def _count_recent_deploys(self, now) -> dict:
        """Count deploy events in evaluation window."""
        result = {
            'count': 0,
            'rate_per_hour': 0.0,
            'sha_changes': 0,
            'error_rate': 0.0,
        }

        try:
            from core.models_diagnostic_pipeline import AutopilotAction

            window = now - timedelta(hours=self.EVAL_WINDOW_HOURS)

            # Count cycle evaluations (each cycle records the SHA)
            cycles = list(
                AutopilotAction.objects.filter(
                    created_at__gte=window,
                    policy='cycle_evaluation',
                ).values_list('deploy_sha', flat=True)
            )

            # Count unique SHAs (= number of deploys)
            unique_shas = set(s for s in cycles if s)
            result['sha_changes'] = len(unique_shas)
            result['count'] = len(unique_shas)
            result['rate_per_hour'] = (
                len(unique_shas) / self.EVAL_WINDOW_HOURS
                if self.EVAL_WINDOW_HOURS > 0 else 0
            )

            # Error rate from recent cycles
            total_cycles = AutopilotAction.objects.filter(
                created_at__gte=window,
                policy='cycle_evaluation',
            ).count()

            error_cycles = AutopilotAction.objects.filter(
                created_at__gte=window,
                policy='cycle_evaluation',
                result__has_key='error',
            ).count()

            if total_cycles > 0:
                result['error_rate'] = round(error_cycles / total_cycles, 3)

        except Exception:
            pass

        return result

    def _escalate(self, current: int, target: int, now) -> int:
        """Escalate to higher level."""
        from core.models.system import SystemConfiguration

        new_level = min(current + 1, target)

        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL,
            defaults={'value': str(new_level)},
        )
        SystemConfiguration.objects.update_or_create(
            key=self.KEY_LEVEL_TS,
            defaults={'value': now.isoformat()},
        )
        # Reset clean counter
        clean_entry = SystemConfiguration.objects.filter(
            key=self.KEY_CLEAN,
        ).first()
        if clean_entry:
            clean_entry.value = '0'
            clean_entry.save(update_fields=['value'])

        logger.info(
            f"[ReleaseGovernor] Escalated {current} → {new_level}"
        )
        return new_level

    def _de_escalate(self, current: int, now) -> int:
        """De-escalate if enough clean cycles."""
        from core.models.system import SystemConfiguration

        clean_entry = SystemConfiguration.objects.filter(
            key=self.KEY_CLEAN,
        ).first()
        clean_cycles = int(clean_entry.value) if clean_entry else 0

        if clean_cycles >= self.RECOVERY_CYCLES:
            new_level = max(current - 1, 0)
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_LEVEL,
                defaults={'value': str(new_level)},
            )
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_LEVEL_TS,
                defaults={'value': now.isoformat()},
            )
            # Reset clean counter
            if clean_entry:
                clean_entry.value = '0'
                clean_entry.save(update_fields=['value'])

            # Remove freeze if dropping below L3
            if new_level < 3:
                SystemConfiguration.objects.filter(
                    key=self.KEY_FREEZE,
                ).delete()

            logger.info(
                f"[ReleaseGovernor] De-escalated {current} → {new_level}"
            )
            return new_level

        return current

    def _increment_clean_cycles(self):
        """Increment clean cycle counter."""
        from core.models.system import SystemConfiguration

        obj, _ = SystemConfiguration.objects.get_or_create(
            key=self.KEY_CLEAN,
            defaults={'value': '0'},
        )
        obj.value = str(int(obj.value or '0') + 1)
        obj.save(update_fields=['value'])

    def _apply_level_actions(self, level: int, now):
        """Apply actions based on current level."""
        from core.models.system import SystemConfiguration

        if level >= 1:
            # Set backoff between deploys
            backoff = (self.FREEZE_BACKOFF_SECONDS if level >= 3
                       else self.DEFAULT_BACKOFF_SECONDS)
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_BACKOFF,
                defaults={'value': str(backoff)},
            )
        else:
            # Clear backoff at L0
            SystemConfiguration.objects.filter(
                key=self.KEY_BACKOFF,
            ).delete()

        if level >= 3:
            # Freeze deploys
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_FREEZE,
                defaults={'value': 'true'},
            )
        else:
            # Clear freeze below L3
            SystemConfiguration.objects.filter(
                key=self.KEY_FREEZE,
            ).delete()

    def set_freeze(self, freeze: bool, reason: str = '') -> dict:
        """Manually freeze/unfreeze deploys."""
        from core.models.system import SystemConfiguration

        if freeze:
            SystemConfiguration.objects.update_or_create(
                key=self.KEY_FREEZE,
                defaults={'value': 'true'},
            )
            return {
                'frozen': True,
                'reason': reason or 'manual freeze',
            }
        else:
            SystemConfiguration.objects.filter(
                key=self.KEY_FREEZE,
            ).delete()
            return {
                'frozen': False,
                'reason': reason or 'manual unfreeze',
            }

    def get_release_report(self, now) -> dict:
        """PA-facing release/deploy status report."""
        from core.models.system import SystemConfiguration

        # Current state
        level_entry = SystemConfiguration.objects.filter(
            key=self.KEY_LEVEL,
        ).first()
        level = int(level_entry.value) if level_entry else 0

        freeze_entry = SystemConfiguration.objects.filter(
            key=self.KEY_FREEZE,
        ).first()
        frozen = bool(freeze_entry)

        backoff_entry = SystemConfiguration.objects.filter(
            key=self.KEY_BACKOFF,
        ).first()
        backoff = int(backoff_entry.value) if backoff_entry else 0

        last_sha_entry = SystemConfiguration.objects.filter(
            key=self.KEY_LAST_SHA,
        ).first()
        last_sha = last_sha_entry.value if last_sha_entry else 'unknown'

        last_deploy_entry = SystemConfiguration.objects.filter(
            key=self.KEY_LAST_DEPLOY_TS,
        ).first()
        last_deploy_ts = last_deploy_entry.value if last_deploy_entry else None

        clean_entry = SystemConfiguration.objects.filter(
            key=self.KEY_CLEAN,
        ).first()
        clean_cycles = int(clean_entry.value) if clean_entry else 0

        # Recent deploy metrics
        metrics = self._count_recent_deploys(now)

        level_labels = {
            0: 'L0 — Observing (normal)',
            1: 'L1 — Backoff (serialize builds)',
            2: 'L2 — Gate (require healthy)',
            3: 'L3 — Frozen (SLO breach)',
        }

        return {
            'level': level,
            'level_label': level_labels.get(level, f'L{level}'),
            'frozen': frozen,
            'backoff_seconds': backoff,
            'last_deploy_sha': last_sha,
            'last_deploy_ts': last_deploy_ts,
            'clean_cycles': clean_cycles,
            'recovery_at': self.RECOVERY_CYCLES - clean_cycles,
            'deploy_rate_per_hour': metrics['rate_per_hour'],
            'deploys_in_window': metrics['count'],
            'error_rate': metrics['error_rate'],
            'window_hours': self.EVAL_WINDOW_HOURS,
        }


# ═══════════════════════════════════════════════════════════════════════
# Revenue Pipeline Automator — Policy 24 (Autonomy #20)
# ═══════════════════════════════════════════════════════════════════════

class RevenuePipelineAutomator:
    """
    Monitors Opportunity pipeline and generates follow-up actions.

    Graduated ladder:
      L1 — Hygiene: flag stale opportunities (no activity in 48h+),
           generate follow-up task suggestions.
      L2 — Proposal drafts: identify high-intent opps ready for proposals,
           create draft follow-up action items.
      L3 — Close loop: identify opps with sent proposals that need
           follow-up sequences (5d, 10d cadence).

    Guardrails:
      - Never sends messages automatically (human approval required)
      - Rate limit: max 3 follow-ups per opportunity
      - Only processes opportunities with status in ('active', 'applied', 'pending')

    All actions create HumanAttentionItems for governance visibility.
    """

    # Pipeline config
    STALE_HOURS = 48             # No activity in 48h = stale
    CRITICAL_STALE_HOURS = 168   # 7 days = critical
    MAX_FOLLOWUPS = 3            # Max follow-ups per opportunity
    FOLLOWUP_CADENCE_DAYS = [2, 5, 10]  # Day intervals for follow-up sequence

    # Active statuses (skip rejected/expired/accepted)
    ACTIVE_STATUSES = ['active', 'pending', 'applied']

    # Revenue thresholds for proposal automation
    HIGH_VALUE_THRESHOLD = 500   # $500+ → high priority
    MATCH_SCORE_THRESHOLD = 60   # 60%+ match → worth pursuing

    def evaluate(self, now) -> dict:
        """Evaluate pipeline health and generate actions."""
        from core.models_unified_system import Opportunity, OpportunityAction

        result = {
            'total_active': 0,
            'stale_count': 0,
            'critical_stale': 0,
            'high_value_active': 0,
            'actions_suggested': 0,
            'by_status': {},
        }

        # Get active opportunities
        active_opps = Opportunity.objects.filter(
            status__in=self.ACTIVE_STATUSES,
        )
        result['total_active'] = active_opps.count()

        # Count by status
        from django.db.models import Count
        status_counts = dict(
            active_opps.values_list('status').annotate(
                c=Count('id'),
            ).values_list('status', 'c')
        )
        result['by_status'] = status_counts

        # Find stale opportunities
        stale_cutoff = now - timedelta(hours=self.STALE_HOURS)
        critical_cutoff = now - timedelta(hours=self.CRITICAL_STALE_HOURS)

        stale_opps = active_opps.filter(created_at__lt=stale_cutoff)
        result['stale_count'] = stale_opps.count()
        result['critical_stale'] = active_opps.filter(
            created_at__lt=critical_cutoff,
        ).count()

        # High-value opportunities
        from django.db.models import Q
        high_value = active_opps.filter(
            Q(potential_revenue__gte=self.HIGH_VALUE_THRESHOLD)
            | Q(match_score__gte=self.MATCH_SCORE_THRESHOLD)
        )
        result['high_value_active'] = high_value.count()

        # Generate follow-up suggestions for stale opps
        suggestions = self._generate_suggestions(stale_opps, now)
        result['actions_suggested'] = len(suggestions)
        result['suggestions'] = suggestions[:10]  # Cap at 10

        return result

    def _generate_suggestions(self, stale_opps, now) -> list:
        """Generate follow-up suggestions for stale opportunities."""
        from core.models_unified_system import OpportunityAction

        suggestions = []

        for opp in stale_opps[:20]:  # Process max 20
            # Count existing follow-up actions
            action_count = OpportunityAction.objects.filter(
                opportunity=opp,
            ).count()

            if action_count >= self.MAX_FOLLOWUPS:
                continue

            age_hours = (now - opp.created_at).total_seconds() / 3600
            revenue = float(opp.potential_revenue or 0)

            # Determine suggestion type
            if age_hours > self.CRITICAL_STALE_HOURS:
                suggestion_type = 'last_chance'
                priority = 'high'
            elif revenue >= self.HIGH_VALUE_THRESHOLD:
                suggestion_type = 'high_value_followup'
                priority = 'high'
            else:
                suggestion_type = 'standard_followup'
                priority = 'medium'

            suggestions.append({
                'opportunity_id': str(opp.id),
                'title': opp.title[:80],
                'type': suggestion_type,
                'priority': priority,
                'age_hours': round(age_hours, 1),
                'revenue': revenue,
                'status': opp.status,
                'actions_taken': action_count,
            })

        return suggestions

    def get_pipeline_report(self, now) -> dict:
        """PA-facing pipeline report."""
        eval_result = self.evaluate(now)

        # Add summary metrics
        total = eval_result['total_active']
        stale = eval_result['stale_count']
        health = 'healthy'
        if total > 0:
            stale_pct = stale / total
            if stale_pct > 0.5:
                health = 'critical'
            elif stale_pct > 0.25:
                health = 'needs_attention'

        return {
            'health': health,
            **eval_result,
        }


# ═══════════════════════════════════════════════════════════════════════
# Outbound Lead Engine — Policy 25 (Autonomy #21)
# ═══════════════════════════════════════════════════════════════════════

class OutboundLeadEngine:
    """
    Discovers prospecting leads from SpiderData, scores them, and
    surfaces a prioritised queue for human outreach.

    Lead sources (spider data_types):
      - job_listing: company hiring → potential client for AI/automation
      - startup_news: funded startups → potential partnership
      - business_signal: revenue/growth mentions → outbound target
      - tech_article: companies using AI → warm approach angle

    Scoring rubric (0-100):
      - Recency: 0-30 pts (fresher = better)
      - Revenue signal: 0-30 pts (mentions of funding/revenue/growth)
      - Channel fit: 0-20 pts (contact info / company identifiable)
      - Source quality: 0-20 pts (historical conversion rate of source)

    Guardrails:
      - Never auto-sends anything — all outreach is draft-only
      - Dedup by source_url (same URL won't surface twice)
      - Daily rate limit: max 20 new leads queued per day
      - Only surfaces leads from last 7 days of spider data
    """

    # Config
    MAX_LEADS_PER_DAY = 20
    LOOKBACK_DAYS = 7
    MIN_SCORE = 30  # Don't queue leads below this score

    # Spider data_types that can yield leads
    LEAD_DATA_TYPES = [
        'job_listing', 'startup_news', 'business_signal',
        'tech_article', 'financial',
    ]

    # Revenue signal keywords that boost score
    REVENUE_KEYWORDS = [
        'funding', 'raised', 'revenue', 'growth', 'series',
        'million', 'billion', 'investment', 'ipo', 'acquisition',
        'hiring', 'expanding', 'launch', 'scale',
    ]

    def evaluate(self, now) -> dict:
        """Discover and score leads from recent spider data."""
        from core.models_unified_system import SpiderData

        result = {
            'leads_discovered': 0,
            'leads_queued': 0,
            'sources_active': 0,
            'top_leads': [],
            'source_breakdown': {},
        }

        lookback = now - timedelta(days=self.LOOKBACK_DAYS)

        # Get recent spider data from lead-relevant types
        spider_qs = SpiderData.objects.filter(
            created_at__gte=lookback,
            data_type__in=self.LEAD_DATA_TYPES,
        ).order_by('-created_at')

        result['leads_discovered'] = spider_qs.count()

        # Count active sources
        from django.db.models import Count
        source_counts = dict(
            spider_qs.values_list('spider_name').annotate(
                c=Count('id'),
            ).values_list('spider_name', 'c')
        )
        result['sources_active'] = len(source_counts)
        result['source_breakdown'] = source_counts

        # Score and deduplicate top leads
        seen_urls = set()
        scored_leads = []

        for item in spider_qs[:200]:  # Process max 200 recent items
            url = item.source_url or ''
            if url in seen_urls:
                continue
            seen_urls.add(url)

            score = self._score_lead(item, now)
            if score < self.MIN_SCORE:
                continue

            raw = item.raw_data or {}
            title = raw.get('title', '') or item.embedding_text[:80] if item.embedding_text else ''

            scored_leads.append({
                'spider_data_id': str(item.id),
                'title': title[:100],
                'source': item.spider_name,
                'data_type': item.data_type,
                'source_url': url[:200],
                'score': score,
                'age_hours': round(
                    (now - item.created_at).total_seconds() / 3600, 1
                ),
            })

        # Sort by score descending, cap at daily limit
        scored_leads.sort(key=lambda x: x['score'], reverse=True)
        queued = scored_leads[:self.MAX_LEADS_PER_DAY]

        result['leads_queued'] = len(queued)
        result['top_leads'] = queued

        return result

    def _score_lead(self, spider_item, now) -> int:
        """Score a spider data item as a prospecting lead (0-100)."""
        score = 0
        raw = spider_item.raw_data or {}
        text = (
            (raw.get('title', '') or '') + ' ' +
            (raw.get('description', '') or '') + ' ' +
            (spider_item.embedding_text or '')
        ).lower()

        # Recency score (0-30): newer = better
        age_hours = (now - spider_item.created_at).total_seconds() / 3600
        if age_hours < 24:
            score += 30
        elif age_hours < 48:
            score += 25
        elif age_hours < 72:
            score += 20
        elif age_hours < 120:
            score += 10
        else:
            score += 5

        # Revenue signal score (0-30): keyword matches
        keyword_hits = sum(
            1 for kw in self.REVENUE_KEYWORDS if kw in text
        )
        score += min(keyword_hits * 6, 30)

        # Channel fit score (0-20): identifiable company/contact
        if spider_item.source_url:
            score += 10
        if any(k in text for k in ['email', 'contact', '@', 'apply']):
            score += 10

        # Source quality score (0-20): known high-quality sources
        high_quality_sources = {
            'adzuna', 'crunchbase', 'techcrunch_startups',
            'hackernews', 'producthunt', 'github_jobs',
        }
        if spider_item.spider_name in high_quality_sources:
            score += 20
        elif spider_item.spider_name in {'venturebeat', 'techcrunch', 'axios'}:
            score += 15
        else:
            score += 5

        return min(score, 100)

    def get_prospecting_queue(self, now) -> dict:
        """PA-facing: top leads ready for outreach."""
        eval_result = self.evaluate(now)
        return {
            'queue_size': eval_result['leads_queued'],
            'leads': eval_result['top_leads'],
            'sources_active': eval_result['sources_active'],
            'source_breakdown': eval_result['source_breakdown'],
        }

    def get_lead_source_report(self, now) -> dict:
        """PA-facing: which spider sources produce leads."""
        from core.models_unified_system import SpiderData
        from django.db.models import Count

        lookback = now - timedelta(days=30)

        # 30-day source breakdown
        source_stats = list(
            SpiderData.objects.filter(
                created_at__gte=lookback,
                data_type__in=self.LEAD_DATA_TYPES,
            ).values('spider_name', 'data_type').annotate(
                count=Count('id'),
            ).order_by('-count')[:20]
        )

        # 7-day vs 30-day trend
        week_lookback = now - timedelta(days=7)
        week_count = SpiderData.objects.filter(
            created_at__gte=week_lookback,
            data_type__in=self.LEAD_DATA_TYPES,
        ).count()
        month_count = SpiderData.objects.filter(
            created_at__gte=lookback,
            data_type__in=self.LEAD_DATA_TYPES,
        ).count()

        weekly_avg = month_count / 4.0 if month_count > 0 else 0
        trend = 'growing' if week_count > weekly_avg * 1.2 else (
            'declining' if week_count < weekly_avg * 0.8 else 'stable'
        )

        return {
            'source_stats': source_stats,
            'week_count': week_count,
            'month_count': month_count,
            'trend': trend,
        }


# ═══════════════════════════════════════════════════════════════════════
# Outreach Sequencer — Policy 26 (Autonomy #22)
# ═══════════════════════════════════════════════════════════════════════

class OutreachSequencer:
    """
    Manages outreach draft lifecycle: inbox, approval, follow-up timers.

    Touch cadence:
      Touch 1: Day 0 (initial outreach)
      Touch 2: Day 3 (follow-up)
      Touch 3: Day 7 (value-add)
      Touch 4: Day 14 (close the loop)

    Guardrails:
      - Never auto-sends without approval
      - Max 4 touches per lead
      - Daily approval cap: 10 (prevents spam)
      - Dedup: won't create draft for spider_data_id with existing active drafts
    """

    MAX_TOUCHES = 4
    TOUCH_DAYS = [0, 3, 7, 14]
    DAILY_APPROVE_CAP = 10

    def get_inbox(self, now) -> dict:
        """PA-facing: drafts pending review."""
        from core.models_outreach import OutreachDraft
        from django.db.models import Count

        try:
            drafts = list(
                OutreachDraft.objects.filter(
                    status='draft',
                ).order_by('-lead_score', '-created_at').values(
                    'id', 'lead_title', 'lead_source', 'lead_url',
                    'lead_score', 'offer_key', 'subject_line',
                    'body_text', 'channel', 'touch_number', 'created_at',
                )[:20]
            )

            # Serialize
            for d in drafts:
                d['id'] = str(d['id'])
                if hasattr(d.get('created_at'), 'isoformat'):
                    d['created_at'] = d['created_at'].isoformat()

            # Counts by status
            status_counts = dict(
                OutreachDraft.objects.values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )

            # Today's approvals
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_approved = OutreachDraft.objects.filter(
                status='approved',
                updated_at__gte=today_start,
            ).count()

            return {
                'drafts': drafts,
                'total_pending': status_counts.get('draft', 0),
                'total_approved': status_counts.get('approved', 0),
                'total_sent': status_counts.get('sent', 0),
                'total_replied': status_counts.get('replied', 0),
                'today_approved': today_approved,
                'daily_cap': self.DAILY_APPROVE_CAP,
                'remaining_approvals': max(
                    0, self.DAILY_APPROVE_CAP - today_approved
                ),
            }
        except Exception as e:
            return {'error': str(e), 'drafts': []}

    def approve_draft(self, draft_id: str, edited_text: str = '') -> dict:
        """Approve a draft for sending. Schedules next follow-up."""
        from core.models_outreach import OutreachDraft

        try:
            draft = OutreachDraft.objects.get(id=draft_id, status='draft')
        except OutreachDraft.DoesNotExist:
            return {'error': f'Draft {draft_id} not found or not in draft status'}

        draft.status = 'approved'
        if edited_text:
            draft.edited_text = edited_text

        # Schedule next follow-up if not at max touches
        if draft.touch_number < self.MAX_TOUCHES:
            next_idx = draft.touch_number  # 0-indexed into TOUCH_DAYS
            if next_idx < len(self.TOUCH_DAYS):
                days_until_next = self.TOUCH_DAYS[next_idx]
                draft.next_touch_at = (
                    timezone.now() + timedelta(days=days_until_next)
                )

        draft.save()

        return {
            'approved': True,
            'draft_id': str(draft.id),
            'touch_number': draft.touch_number,
            'next_touch_at': (
                draft.next_touch_at.isoformat()
                if draft.next_touch_at else None
            ),
        }

    def reject_draft(self, draft_id: str, reason: str = '') -> dict:
        """Reject a draft — prevents re-queue."""
        from core.models_outreach import OutreachDraft

        try:
            draft = OutreachDraft.objects.get(id=draft_id, status='draft')
        except OutreachDraft.DoesNotExist:
            return {'error': f'Draft {draft_id} not found or not in draft status'}

        draft.status = 'rejected'
        draft.rejection_reason = reason
        draft.save()

        return {
            'rejected': True,
            'draft_id': str(draft.id),
            'reason': reason,
        }

    def get_metrics_report(self, now) -> dict:
        """PA-facing: outreach conversion metrics."""
        from core.models_outreach import OutreachDraft
        from django.db.models import Count, Avg

        try:
            # Overall funnel
            total = OutreachDraft.objects.count()
            by_status = dict(
                OutreachDraft.objects.values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )

            # By channel
            by_channel = dict(
                OutreachDraft.objects.values_list('channel').annotate(
                    c=Count('id'),
                ).values_list('channel', 'c')
            )

            # By offer
            by_offer = dict(
                OutreachDraft.objects.exclude(
                    offer_key='',
                ).values_list('offer_key').annotate(
                    c=Count('id'),
                ).values_list('offer_key', 'c')
            )

            # Avg score
            avg_score = OutreachDraft.objects.aggregate(
                avg=Avg('lead_score'),
            )['avg'] or 0

            # Reply rate
            sent = by_status.get('sent', 0) + by_status.get('replied', 0)
            replied = by_status.get('replied', 0)
            reply_rate = (replied / sent * 100) if sent > 0 else 0

            return {
                'total': total,
                'by_status': by_status,
                'by_channel': by_channel,
                'by_offer': by_offer,
                'avg_lead_score': round(avg_score, 1),
                'reply_rate_pct': round(reply_rate, 1),
            }
        except Exception as e:
            return {'error': str(e)}

    def evaluate(self, now) -> dict:
        """Policy evaluation — generate follow-up drafts for approved messages."""
        from core.models_outreach import OutreachDraft

        result = {
            'pending_drafts': 0,
            'followups_generated': 0,
            'expired': 0,
        }

        try:
            result['pending_drafts'] = OutreachDraft.objects.filter(
                status='draft',
            ).count()

            # Generate follow-ups for approved drafts with due next_touch_at
            due_followups = OutreachDraft.objects.filter(
                status='approved',
                next_touch_at__lte=now,
                touch_number__lt=self.MAX_TOUCHES,
            )

            for parent in due_followups[:10]:  # Max 10 per cycle
                # Check if follow-up already exists
                existing = OutreachDraft.objects.filter(
                    parent_draft=parent,
                ).exists()
                if existing:
                    continue

                # Create follow-up draft
                OutreachDraft.objects.create(
                    spider_data_id=parent.spider_data_id,
                    lead_title=parent.lead_title,
                    lead_source=parent.lead_source,
                    lead_url=parent.lead_url,
                    lead_score=parent.lead_score,
                    offer_key=parent.offer_key,
                    channel=parent.channel,
                    touch_number=parent.touch_number + 1,
                    parent_draft=parent,
                    body_text=(
                        f"[Follow-up #{parent.touch_number + 1} for: "
                        f"{parent.lead_title[:60]}]\n\n"
                        f"Draft follow-up message needed."
                    ),
                    trace_id=parent.trace_id,
                    user=parent.user,
                )
                result['followups_generated'] += 1

            # Expire old approved drafts with no next touch
            stale_cutoff = now - timedelta(days=30)
            expired = OutreachDraft.objects.filter(
                status='approved',
                next_touch_at__isnull=True,
                updated_at__lt=stale_cutoff,
            ).update(status='expired')
            result['expired'] = expired

        except Exception as e:
            result['error'] = str(e)

        return result


# ═══════════════════════════════════════════════════════════════════════
# Close-the-Deal Engine — Policy 27 (Autonomy #23)
# ═══════════════════════════════════════════════════════════════════════

class CloseTheDealEngine:
    """
    Generates deal-closing document bundles (ClosePacks) when
    an opportunity reaches high-intent stage.

    Close Pack contents:
      - 1-page proposal (scope, timeline, price, assumptions)
      - SOW/MSA-lite contract draft
      - Invoice draft (line items, payment terms)

    Guardrails:
      - Nothing sent without human approval
      - Requires price + offer_key before generating
      - Max 2 follow-ups per pack
      - Follow-up cadence: 5d, 10d after sent
    """

    MAX_FOLLOWUPS = 2
    FOLLOWUP_DAYS = [5, 10]

    # Offer templates with default scope descriptions
    OFFER_TEMPLATES = {
        'ai_automation': {
            'name': 'AI Automation Sprint',
            'scope': (
                'AI-powered workflow automation for your business processes. '
                'Includes: needs assessment, custom AI agent development, '
                'integration with existing tools, testing, and deployment.'
            ),
            'deliverables': [
                'Custom AI agent(s) deployed',
                'Integration with existing workflows',
                'Documentation and training',
                '30-day support period',
            ],
        },
        'content_engine': {
            'name': 'Content Engine Setup',
            'scope': (
                'Automated content generation pipeline powered by AI. '
                'Includes: content strategy, AI agent configuration, '
                'quality control system, and publishing automation.'
            ),
            'deliverables': [
                'Content generation pipeline',
                'Quality scoring system',
                'Publishing automation',
                '30-day content calendar',
            ],
        },
        'analytics_dashboard': {
            'name': 'Analytics Dashboard',
            'scope': (
                'Custom analytics dashboard with AI-powered insights. '
                'Includes: data integration, visualization design, '
                'predictive analytics, and alerting system.'
            ),
            'deliverables': [
                'Custom dashboard',
                'Data integrations',
                'Predictive models',
                'Alerting system',
            ],
        },
        'consulting': {
            'name': 'AI Strategy Consulting',
            'scope': (
                'Strategic AI assessment and roadmap for your organization. '
                'Includes: current state analysis, opportunity identification, '
                'implementation roadmap, and vendor evaluation.'
            ),
            'deliverables': [
                'AI readiness assessment',
                'Implementation roadmap',
                'Vendor comparison matrix',
                'Executive presentation',
            ],
        },
    }

    def generate_pack(
        self, opportunity_id: str, offer_key: str,
        price: float, timeline_days: int = 14,
    ) -> dict:
        """Generate a close pack for an opportunity."""
        from core.models_close_pack import ClosePack

        template = self.OFFER_TEMPLATES.get(
            offer_key, self.OFFER_TEMPLATES.get('consulting')
        )

        # Generate proposal
        deliverables_text = '\n'.join(
            f'  - {d}' for d in template['deliverables']
        )
        proposal = (
            f"# Proposal: {template['name']}\n\n"
            f"## Scope\n{template['scope']}\n\n"
            f"## Deliverables\n{deliverables_text}\n\n"
            f"## Timeline\n{timeline_days} business days from project kickoff.\n\n"
            f"## Investment\n${price:,.2f} USD\n\n"
            f"## Payment Terms\n"
            f"50% upon project start, 50% upon completion.\n\n"
            f"## Next Steps\n"
            f"1. Review and approve this proposal\n"
            f"2. Sign the attached agreement\n"
            f"3. Schedule kickoff call\n"
        )

        # Generate contract
        contract = (
            f"# Statement of Work\n\n"
            f"## Project: {template['name']}\n\n"
            f"### Scope of Work\n{template['scope']}\n\n"
            f"### Deliverables\n{deliverables_text}\n\n"
            f"### Timeline\n{timeline_days} business days.\n\n"
            f"### Compensation\n${price:,.2f} USD total.\n"
            f"Payment schedule: 50/50 (start/completion).\n\n"
            f"### Terms\n"
            f"- Changes to scope require written agreement and may adjust timeline/price.\n"
            f"- Client provides timely feedback (within 2 business days).\n"
            f"- Intellectual property transfers to client upon final payment.\n"
        )

        # Generate invoice
        invoice = (
            f"# Invoice\n\n"
            f"## Service: {template['name']}\n\n"
            f"| Item | Amount |\n"
            f"|------|--------|\n"
            f"| {template['name']} — Phase 1 (50%) | ${price/2:,.2f} |\n"
            f"| Due upon completion — Phase 2 (50%) | ${price/2:,.2f} |\n"
            f"| **Total** | **${price:,.2f}** |\n\n"
            f"**Payment Terms:** Net 15 days\n"
            f"**Payment Methods:** Bank transfer, Stripe\n"
        )

        # Create ClosePack
        opp_id = opportunity_id if opportunity_id else None
        try:
            pack = ClosePack.objects.create(
                opportunity_id=opp_id,
                offer_key=offer_key,
                price=price,
                timeline_days=timeline_days,
                proposal_text=proposal,
                contract_text=contract,
                invoice_text=invoice,
            )
            return {
                'pack_id': str(pack.id),
                'offer': template['name'],
                'price': price,
                'timeline_days': timeline_days,
                'status': 'draft',
                'documents': ['proposal', 'contract', 'invoice'],
            }
        except Exception as e:
            return {'error': str(e)}

    def get_inbox(self, now) -> dict:
        """PA-facing: close packs pending approval."""
        from core.models_close_pack import ClosePack
        from django.db.models import Count, Sum

        try:
            drafts = list(
                ClosePack.objects.filter(
                    status='draft',
                ).order_by('-created_at').values(
                    'id', 'offer_key', 'price', 'timeline_days',
                    'status', 'created_at',
                )[:20]
            )

            for d in drafts:
                d['id'] = str(d['id'])
                if hasattr(d.get('created_at'), 'isoformat'):
                    d['created_at'] = d['created_at'].isoformat()
                d['price'] = float(d.get('price', 0))

            # Counts by status
            status_counts = dict(
                ClosePack.objects.values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )

            # Total pipeline value
            pipeline_value = ClosePack.objects.filter(
                status__in=['draft', 'approved', 'sent'],
            ).aggregate(total=Sum('price'))['total'] or 0

            return {
                'packs': drafts,
                'total_draft': status_counts.get('draft', 0),
                'total_sent': status_counts.get('sent', 0),
                'total_won': status_counts.get('won', 0),
                'total_lost': status_counts.get('lost', 0),
                'pipeline_value_usd': float(pipeline_value),
            }
        except Exception as e:
            return {'error': str(e), 'packs': []}

    def approve_pack(self, pack_id: str, edits: dict = None) -> dict:
        """Approve a close pack and schedule follow-up."""
        from core.models_close_pack import ClosePack

        try:
            pack = ClosePack.objects.get(id=pack_id, status='draft')
        except ClosePack.DoesNotExist:
            return {'error': f'Pack {pack_id} not found or not in draft status'}

        # Apply edits if provided
        if edits:
            if 'proposal' in edits:
                pack.edited_proposal = edits['proposal']
            if 'contract' in edits:
                pack.edited_contract = edits['contract']
            if 'invoice' in edits:
                pack.edited_invoice = edits['invoice']

        pack.status = 'approved'

        # Schedule first follow-up
        if self.FOLLOWUP_DAYS:
            pack.followup_at = (
                timezone.now() + timedelta(days=self.FOLLOWUP_DAYS[0])
            )

        pack.save()

        return {
            'approved': True,
            'pack_id': str(pack.id),
            'followup_at': (
                pack.followup_at.isoformat() if pack.followup_at else None
            ),
        }

    def get_metrics_report(self, now) -> dict:
        """PA-facing: deal metrics."""
        from core.models_close_pack import ClosePack
        from django.db.models import Count, Sum, Avg

        try:
            total = ClosePack.objects.count()
            by_status = dict(
                ClosePack.objects.values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )
            by_offer = dict(
                ClosePack.objects.values_list('offer_key').annotate(
                    c=Count('id'),
                ).values_list('offer_key', 'c')
            )

            # Win rate
            sent = by_status.get('sent', 0) + by_status.get('won', 0) + by_status.get('lost', 0)
            won = by_status.get('won', 0)
            win_rate = (won / sent * 100) if sent > 0 else 0

            # Revenue
            won_value = ClosePack.objects.filter(
                status='won',
            ).aggregate(total=Sum('price'))['total'] or 0

            avg_deal = ClosePack.objects.filter(
                status='won',
            ).aggregate(avg=Avg('price'))['avg'] or 0

            return {
                'total': total,
                'by_status': by_status,
                'by_offer': by_offer,
                'win_rate_pct': round(win_rate, 1),
                'won_revenue_usd': float(won_value),
                'avg_deal_size_usd': round(float(avg_deal), 2),
            }
        except Exception as e:
            return {'error': str(e)}

    def evaluate(self, now) -> dict:
        """Policy evaluation — schedule follow-ups for sent packs."""
        from core.models_close_pack import ClosePack

        result = {
            'pending_packs': 0,
            'followups_scheduled': 0,
            'expired': 0,
        }

        try:
            result['pending_packs'] = ClosePack.objects.filter(
                status='draft',
            ).count()

            # Process due follow-ups
            due = ClosePack.objects.filter(
                status__in=['approved', 'sent'],
                followup_at__lte=now,
                followup_count__lt=self.MAX_FOLLOWUPS,
            )

            for pack in due[:10]:
                pack.followup_count += 1
                # Schedule next follow-up if available
                if pack.followup_count < len(self.FOLLOWUP_DAYS):
                    next_days = self.FOLLOWUP_DAYS[pack.followup_count]
                    pack.followup_at = now + timedelta(days=next_days)
                else:
                    pack.followup_at = None
                pack.save()
                result['followups_scheduled'] += 1

            # Expire old sent packs with no response (30 days)
            stale_cutoff = now - timedelta(days=30)
            expired = ClosePack.objects.filter(
                status='sent',
                followup_at__isnull=True,
                updated_at__lt=stale_cutoff,
            ).update(status='expired')
            result['expired'] = expired

        except Exception as e:
            result['error'] = str(e)

        return result


# ═══════════════════════════════════════════════════════════════════════
# Attribution Debt Controller — Policy 14 (Session 1090, Autonomy #10)
# ═══════════════════════════════════════════════════════════════════════

class AttributionDebtController:
    """
    Session 1090: Autonomy #10 — Identifies LLM spend that cannot be
    attributed to a specific desk, reports debt metrics, and protects
    PortfolioAllocator from making decisions on low-confidence data.

    Attribution debt = LLM cost from agents that don't map to any desk.
    High debt means IQROI calculations are unreliable (costs land in
    'general' by default, distorting real desk-level ROI).

    Thresholds (configurable via AutopilotConfig):
    - DEBT_WARNING_PCT: alert governance when debt exceeds this % (default 20%)
    - DEBT_CRITICAL_PCT: block portfolio reallocation above this % (default 40%)
    - DEBT_USD_FLOOR: ignore debt below this $ amount (default $0.10)
    """

    # Known agent→desk mappings (static, covers most common agents)
    # Agents not in this map fall back to ImpactEvent history, then 'general'
    AGENT_DESK_MAP = {
        # Sports desk
        'SportsBettingAgent': 'sports',
        'MLPredictionAgent': 'sports',
        'StockAnalystAgent': 'trading',
        'StockAuditCoordinator': 'trading',
        'MarketMovementMonitorAgent': 'trading',
        'InstitutionalWatcherAgent': 'trading',
        'MarketAnomalyDetectorAgent': 'trading',
        'BullCaseAgent': 'trading',
        'BearCaseAgent': 'trading',
        'SignalScannerAgent': 'trading',
        'MarketIntelligenceCoordinator': 'trading',
        'BlockchainAuditCoordinator': 'trading',
        'SmartContractAuditorAgent': 'trading',
        'TransactionMonitorAgent': 'trading',
        'WhaleWatcherAgent': 'trading',
        'ExploitDetectorAgent': 'trading',

        # Content desk
        'ContentWriterAgent': 'content',
        'EditorAgent': 'content',
        'ContentStrategyAgent': 'content',
        'SEOOptimizerAgent': 'content',
        'SocialMediaAgent': 'content',
        'ImageAgent': 'content',
        'VideoAgent': 'content',
        'AudioAgent': 'content',
        'TalkingCharacterAgent': 'content',
        'ThreeDAgent': 'content',
        'ImageEditingAgent': 'content',
        'VideoEditingAgent': 'content',
        'CreativeDirectorAgent': 'content',
        'AutonomousContentStudioCoordinator': 'content',
        'TopicMinerAgent': 'content',
        'ContrarianAgent': 'content',
        'BrandIdentityAgent': 'content',
        'AISeriesWorkflowAgent': 'content',
        'PromptEngineeringAgent': 'content',

        # Research desk
        'ResearchAgent': 'research',
        'TrendAnalysisAgent': 'research',
        'NarrativeDriftCoordinator': 'research',
        'NarrativeHistorianAgent': 'research',
        'TrendBreakDetectorAgent': 'research',
        'CulturalImpactAgent': 'research',
        'CompetitorAnalysisAgent': 'research',
        'CustomerResearchAgent': 'research',
        'MarketIntelligenceAgent': 'research',

        # Career desk
        'LegalDocDrafterAgent': 'career',
        'MarketingStrategyAgent': 'career',
        'BrandStrategyAgent': 'career',
        'OpportunityScoringAgent': 'career',

        # General (internal tools, auditing)
        'PlatformAuditAgent': 'general',
        'ContentAuditAgent': 'general',
        'CodeGeneratorAgent': 'general',
        'FullStackDeveloperAgent': 'general',
        'CodeReviewAgent': 'general',
        'DevOpsAgent': 'general',
        'CTOAgent': 'general',
        'COOAgent': 'general',
        'MeetingCoordinatorAgent': 'general',
        'MemoryIsolationAgent': 'general',
        'CharacterTrainingAgent': 'general',
        'TrainedCreationAgent': 'general',

        # PA / system agents
        'PersonalAssistant': 'general',
        'InterviewAssistant': 'career',
        'DynamicPersonaAgent': 'general',
    }

    # Thresholds (overridable via AutopilotConfig)
    DEBT_WARNING_PCT = 20.0    # % of total spend
    DEBT_CRITICAL_PCT = 40.0   # % — block reallocation
    DEBT_USD_FLOOR = 0.10      # Ignore debt below this

    def get_agent_desk(self, agent_name: str) -> str | None:
        """
        Resolve an agent name to a desk.
        Returns None if unattributed (= debt).
        """
        if not agent_name:
            return None

        # 1. Static map (fast, authoritative)
        desk = self.AGENT_DESK_MAP.get(agent_name)
        if desk:
            return desk

        # 2. Check ImpactEvent history (dynamic, covers persona agents)
        try:
            from core.models_impact_events import ImpactEvent
            ie_desk = ImpactEvent.objects.filter(
                agent_name=agent_name,
            ).values_list('desk', flat=True).first()
            if ie_desk:
                return ie_desk
        except Exception:
            pass

        return None

    def compute_debt(self, now, window_hours=24) -> dict:
        """
        Compute attribution debt metrics for the given window.

        Returns:
            total_spend: total LLM spend in window
            attributed_spend: spend mapped to a desk
            unattributed_spend: spend not mapped (= debt)
            debt_pct: unattributed / total × 100
            top_unattributed: top agents by unattributed cost
            desk_breakdown: attributed spend by desk
        """
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum

        window_start = now - timedelta(hours=window_hours)

        try:
            agent_costs = list(
                LLMCallLog.objects.filter(
                    created_at__gte=window_start,
                    success=True,
                ).values('agent_name').annotate(
                    total_cost=Sum('cost'),
                ).order_by('-total_cost')
            )
        except Exception:
            return {
                'total_spend': 0,
                'attributed_spend': 0,
                'unattributed_spend': 0,
                'debt_pct': 0,
                'top_unattributed': [],
                'desk_breakdown': {},
                'window_hours': window_hours,
            }

        total_spend = 0.0
        attributed_spend = 0.0
        unattributed_spend = 0.0
        desk_breakdown = {}
        top_unattributed = []

        for ac in agent_costs:
            agent = ac['agent_name'] or ''
            cost = float(ac['total_cost'] or 0)
            total_spend += cost

            desk = self.get_agent_desk(agent)
            if desk:
                attributed_spend += cost
                desk_breakdown[desk] = desk_breakdown.get(desk, 0) + cost
            else:
                unattributed_spend += cost
                top_unattributed.append({
                    'agent': agent or '(empty)',
                    'cost_usd': round(cost, 4),
                })

        debt_pct = (
            (unattributed_spend / total_spend * 100)
            if total_spend > 0 else 0
        )

        # Sort unattributed by cost descending
        top_unattributed.sort(key=lambda x: x['cost_usd'], reverse=True)

        return {
            'total_spend': round(total_spend, 4),
            'attributed_spend': round(attributed_spend, 4),
            'unattributed_spend': round(unattributed_spend, 4),
            'debt_pct': round(debt_pct, 1),
            'top_unattributed': top_unattributed[:15],
            'desk_breakdown': {
                k: round(v, 4) for k, v in
                sorted(desk_breakdown.items(), key=lambda x: -x[1])
            },
            'window_hours': window_hours,
        }

    def should_block_reallocation(self, debt_report: dict) -> bool:
        """True if attribution debt is too high for reliable reallocation."""
        critical_pct = (
            AutopilotConfig.get('DEBT_CRITICAL_PCT')
            or self.DEBT_CRITICAL_PCT
        )
        return (
            debt_report['debt_pct'] > critical_pct
            and debt_report['unattributed_spend'] > self.DEBT_USD_FLOOR
        )

    def get_smoothing_adjustment(self, debt_report: dict) -> float:
        """
        Returns an EWMA alpha adjustment based on debt level.
        Higher debt → lower alpha (more conservative smoothing).

        Normal:    alpha stays at 0.3
        Warning:   alpha drops to 0.15 (slower to react)
        Critical:  alpha drops to 0.05 (near-frozen allocations)
        """
        warning_pct = (
            AutopilotConfig.get('DEBT_WARNING_PCT')
            or self.DEBT_WARNING_PCT
        )
        critical_pct = (
            AutopilotConfig.get('DEBT_CRITICAL_PCT')
            or self.DEBT_CRITICAL_PCT
        )

        pct = debt_report['debt_pct']

        if pct >= critical_pct:
            return 0.05
        elif pct >= warning_pct:
            return 0.15
        return PortfolioAllocator.EWMA_ALPHA  # Default 0.3

    def get_debt_report(self, now) -> dict:
        """Generate full attribution debt report for PA/governance."""
        debt_24h = self.compute_debt(now, window_hours=24)
        debt_72h = self.compute_debt(now, window_hours=72)

        warning_pct = (
            AutopilotConfig.get('DEBT_WARNING_PCT')
            or self.DEBT_WARNING_PCT
        )
        critical_pct = (
            AutopilotConfig.get('DEBT_CRITICAL_PCT')
            or self.DEBT_CRITICAL_PCT
        )

        status = 'healthy'
        if debt_24h['debt_pct'] >= critical_pct:
            status = 'critical'
        elif debt_24h['debt_pct'] >= warning_pct:
            status = 'warning'

        return {
            'status': status,
            'last_24h': debt_24h,
            'last_72h': debt_72h,
            'thresholds': {
                'warning_pct': warning_pct,
                'critical_pct': critical_pct,
                'usd_floor': self.DEBT_USD_FLOOR,
            },
            'reallocation_blocked': self.should_block_reallocation(debt_24h),
            'smoothing_alpha': self.get_smoothing_adjustment(debt_24h),
            'mapped_agents': len(self.AGENT_DESK_MAP),
        }


# ═══════════════════════════════════════════════════════════════════════
# Experiment Engine — Policy 15 (Session 1090, Autonomy #11)
# ═══════════════════════════════════════════════════════════════════════

class ExperimentEngine:
    """
    Session 1090: Autonomy #11 — A/B testing for policy parameter changes.

    Creates experiments that:
    1. Snapshot current policy params as baseline
    2. Apply treatment params
    3. Collect metrics during both periods
    4. Auto-promote (treatment wins) or auto-rollback (treatment loses)

    Supported policy levers:
    - portfolio_allocator: ALLOCATION_FLOOR, ALLOCATION_CEILING, EWMA_ALPHA
    - roi_throttle: THROTTLE_TIERS cooldown thresholds
    - budget_controller: BUDGET_SOFT_PCT, BUDGET_HARD_PCT

    Each experiment writes params to SystemConfiguration so policies read
    them dynamically. On rollback, baseline params are restored.
    """

    # Config key prefix for experiment-managed parameters
    EXPERIMENT_CONFIG_PREFIX = 'experiment_param'

    # Policy → parameter names that can be experimented on
    EXPERIMENTABLE_PARAMS = {
        'portfolio_allocator': [
            'ALLOCATION_FLOOR',
            'ALLOCATION_CEILING',
            'EWMA_ALPHA',
            'IMPACT_POINT_USD_VALUE',
        ],
        'roi_throttle': [
            'THROTTLE_TIER_0_ROI',
            'THROTTLE_TIER_0_MINUTES',
            'THROTTLE_TIER_1_ROI',
            'THROTTLE_TIER_1_MINUTES',
        ],
        'budget_controller': [
            'BUDGET_SOFT_PCT',
            'BUDGET_HARD_PCT',
            'BUDGET_DAILY_USD',
        ],
    }

    # Metric collectors keyed by success_metric name
    METRIC_COLLECTORS = {
        'avg_desk_iqroi': '_collect_avg_iqroi',
        'attribution_debt_pct': '_collect_debt_pct',
        'total_impact_usd': '_collect_total_impact',
        'publish_pass_rate': '_collect_publish_rate',
        'error_rate': '_collect_error_rate',
    }

    def create_experiment(
        self,
        policy_name: str,
        treatment_params: dict,
        success_metric: str = 'avg_desk_iqroi',
        description: str = '',
        success_threshold_pct: float = 5.0,
        failure_threshold_pct: float = -10.0,
        min_duration_hours: int = 24,
        max_duration_hours: int = 168,
        created_by: str = 'autopilot',
    ) -> dict:
        """Create a new experiment (draft). Must be started separately."""
        from core.models_policy_experiment import PolicyExperiment

        if policy_name not in self.EXPERIMENTABLE_PARAMS:
            return {
                'error': (
                    f"Unknown policy '{policy_name}'. "
                    f"Valid: {list(self.EXPERIMENTABLE_PARAMS.keys())}"
                ),
            }

        if success_metric not in self.METRIC_COLLECTORS:
            return {
                'error': (
                    f"Unknown metric '{success_metric}'. "
                    f"Valid: {list(self.METRIC_COLLECTORS.keys())}"
                ),
            }

        # Check for existing active experiment on this policy
        active = PolicyExperiment.objects.filter(
            policy_name=policy_name,
            status='active',
        ).exists()
        if active:
            return {
                'error': (
                    f"Policy '{policy_name}' already has an active experiment. "
                    f"Finish or rollback the current one first."
                ),
            }

        # Snapshot current baseline params
        baseline = self._get_current_params(policy_name)

        # Validate treatment params
        allowed = set(self.EXPERIMENTABLE_PARAMS[policy_name])
        invalid = set(treatment_params.keys()) - allowed
        if invalid:
            return {
                'error': (
                    f"Invalid params for {policy_name}: {invalid}. "
                    f"Allowed: {allowed}"
                ),
            }

        exp = PolicyExperiment.objects.create(
            policy_name=policy_name,
            description=description or (
                f"Test {list(treatment_params.keys())} changes on {policy_name}"
            ),
            baseline_params=baseline,
            treatment_params=treatment_params,
            success_metric=success_metric,
            success_threshold_pct=success_threshold_pct,
            failure_threshold_pct=failure_threshold_pct,
            min_duration_hours=min_duration_hours,
            max_duration_hours=max_duration_hours,
            created_by=created_by,
        )

        return {
            'experiment_id': str(exp.id),
            'policy': policy_name,
            'status': 'draft',
            'baseline': baseline,
            'treatment': treatment_params,
            'success_metric': success_metric,
        }

    def start_experiment(self, experiment_id: str) -> dict:
        """Activate an experiment — apply treatment params."""
        from core.models_policy_experiment import PolicyExperiment

        try:
            exp = PolicyExperiment.objects.get(id=experiment_id)
        except PolicyExperiment.DoesNotExist:
            return {'error': f'Experiment {experiment_id} not found'}

        if exp.status != 'draft':
            return {'error': f'Experiment is {exp.status}, can only start drafts'}

        # Capture baseline metrics before switching
        now = timezone.now()
        exp.baseline_metrics = self._collect_metrics(exp.success_metric, now)

        # Apply treatment params to SystemConfiguration
        self._apply_params(exp.policy_name, exp.treatment_params)

        exp.start()  # sets status='active', started_at=now

        return {
            'experiment_id': str(exp.id),
            'status': 'active',
            'baseline_metrics': exp.baseline_metrics,
            'treatment_params_applied': exp.treatment_params,
        }

    def evaluate_experiments(self, now) -> list[dict]:
        """
        Check all active experiments and decide: promote, rollback, or continue.
        Called by OpsAutopilot on each cycle.
        """
        from core.models_policy_experiment import PolicyExperiment

        results = []
        active = PolicyExperiment.objects.filter(status='active')

        for exp in active:
            result = self._evaluate_single(exp, now)
            results.append(result)

        return results

    def _evaluate_single(self, exp, now) -> dict:
        """Evaluate a single experiment."""
        result = {
            'experiment_id': str(exp.id),
            'policy': exp.policy_name,
            'action': 'continue',
        }

        # Check expiration first
        if exp.is_expired:
            self._rollback_experiment(exp, 'Max duration exceeded')
            result['action'] = 'expired'
            return result

        # Not mature enough yet
        if not exp.is_mature:
            elapsed_h = 0
            if exp.started_at:
                elapsed_h = (now - exp.started_at).total_seconds() / 3600
            result['elapsed_hours'] = round(elapsed_h, 1)
            result['min_hours'] = exp.min_duration_hours
            return result

        # Collect treatment metrics
        treatment_metrics = self._collect_metrics(exp.success_metric, now)
        exp.treatment_metrics = treatment_metrics
        exp.save(update_fields=['treatment_metrics', 'updated_at'])

        # Compare baseline vs treatment
        baseline_val = exp.baseline_metrics.get('value', 0)
        treatment_val = treatment_metrics.get('value', 0)

        if baseline_val == 0:
            pct_change = 100.0 if treatment_val > 0 else 0.0
        else:
            pct_change = ((treatment_val - baseline_val) / abs(baseline_val)) * 100

        result['baseline_value'] = baseline_val
        result['treatment_value'] = treatment_val
        result['pct_change'] = round(pct_change, 2)

        # Decision
        if pct_change >= exp.success_threshold_pct:
            self._promote_experiment(exp, pct_change)
            result['action'] = 'promoted'
        elif pct_change <= exp.failure_threshold_pct:
            self._rollback_experiment(
                exp,
                f'Treatment underperformed by {abs(pct_change):.1f}%'
            )
            result['action'] = 'rolled_back'
        else:
            result['action'] = 'continue'

        return result

    def _promote_experiment(self, exp, pct_change: float):
        """Treatment won — persist treatment params as new defaults."""
        from core.models.system import SystemConfiguration

        # Treatment params are already in SystemConfiguration,
        # just update the description to note they're promoted
        for param, value in exp.treatment_params.items():
            key = f"{self.EXPERIMENT_CONFIG_PREFIX}:{exp.policy_name}:{param}"
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': {'value': value, 'promoted': True},
                    'description': (
                        f"Promoted from experiment {str(exp.id)[:8]}: "
                        f"+{pct_change:.1f}% on {exp.success_metric}"
                    ),
                    'category': 'experiment',
                },
            )

        exp.promote(
            f"Treatment +{pct_change:.1f}% on {exp.success_metric} "
            f"(threshold: +{exp.success_threshold_pct}%)"
        )

    def _rollback_experiment(self, exp, reason: str):
        """Revert to baseline params."""
        # Restore baseline params in SystemConfiguration
        self._apply_params(exp.policy_name, exp.baseline_params)
        exp.rollback(reason)

    def _apply_params(self, policy_name: str, params: dict):
        """Write experiment params to SystemConfiguration."""
        from core.models.system import SystemConfiguration

        for param, value in params.items():
            key = f"{self.EXPERIMENT_CONFIG_PREFIX}:{policy_name}:{param}"
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': {'value': value},
                    'description': (
                        f"Experiment param: {policy_name}.{param}"
                    ),
                    'category': 'experiment',
                },
            )

    def _get_current_params(self, policy_name: str) -> dict:
        """Read current parameter values (from config or defaults)."""
        from core.models.system import SystemConfiguration

        defaults = {
            'portfolio_allocator': {
                'ALLOCATION_FLOOR': PortfolioAllocator.ALLOCATION_FLOOR,
                'ALLOCATION_CEILING': PortfolioAllocator.ALLOCATION_CEILING,
                'EWMA_ALPHA': PortfolioAllocator.EWMA_ALPHA,
                'IMPACT_POINT_USD_VALUE': PortfolioAllocator.POINT_USD_VALUE,
            },
            'roi_throttle': {
                'THROTTLE_TIER_0_ROI': 0.05,
                'THROTTLE_TIER_0_MINUTES': 120,
                'THROTTLE_TIER_1_ROI': 0.2,
                'THROTTLE_TIER_1_MINUTES': 60,
            },
            'budget_controller': {
                'BUDGET_SOFT_PCT': 70.0,
                'BUDGET_HARD_PCT': 95.0,
                'BUDGET_DAILY_USD': 5.0,
            },
        }

        current = dict(defaults.get(policy_name, {}))

        # Override with SystemConfiguration values if present
        for param in current:
            key = f"{self.EXPERIMENT_CONFIG_PREFIX}:{policy_name}:{param}"
            try:
                entry = SystemConfiguration.objects.filter(
                    key=key,
                ).values_list('value', flat=True).first()
                if entry and isinstance(entry, dict) and 'value' in entry:
                    current[param] = entry['value']
            except Exception:
                pass

        return current

    def get_experiment_param(self, policy_name: str, param: str, default=None):
        """
        Read a single experiment-managed parameter.
        Policies call this to get the currently active value.
        """
        from core.models.system import SystemConfiguration

        key = f"{self.EXPERIMENT_CONFIG_PREFIX}:{policy_name}:{param}"
        try:
            entry = SystemConfiguration.objects.filter(
                key=key,
            ).values_list('value', flat=True).first()
            if entry and isinstance(entry, dict) and 'value' in entry:
                return entry['value']
        except Exception:
            pass

        return default

    # ── Metric collectors ──────────────────────────────────────────────

    def _collect_metrics(self, metric_name: str, now) -> dict:
        """Dispatch to the appropriate metric collector."""
        method_name = self.METRIC_COLLECTORS.get(metric_name)
        if not method_name:
            return {'value': 0, 'error': f'Unknown metric: {metric_name}'}

        collector = getattr(self, method_name, None)
        if not collector:
            return {'value': 0, 'error': f'Collector not found: {method_name}'}

        try:
            return collector(now)
        except Exception as e:
            return {'value': 0, 'error': str(e)}

    def _collect_avg_iqroi(self, now) -> dict:
        """Average IQROI across all desks (72h window)."""
        allocator = PortfolioAllocator()
        desk_data = allocator.compute_desk_iqroi(now)
        if not desk_data:
            return {'value': 0, 'desks': 0}

        iqrois = [d['iqroi'] for d in desk_data.values()]
        avg = sum(iqrois) / len(iqrois) if iqrois else 0
        return {
            'value': round(avg, 4),
            'desks': len(desk_data),
            'per_desk': {k: v['iqroi'] for k, v in desk_data.items()},
        }

    def _collect_debt_pct(self, now) -> dict:
        """Attribution debt % (24h)."""
        ctrl = AttributionDebtController()
        debt = ctrl.compute_debt(now, window_hours=24)
        return {
            'value': debt['debt_pct'],
            'total_spend': debt['total_spend'],
        }

    def _collect_total_impact(self, now) -> dict:
        """Total impact USD (72h)."""
        from core.models_impact_events import ImpactEvent
        from django.db.models import Sum

        window = now - timedelta(hours=72)
        result = ImpactEvent.objects.filter(
            created_at__gte=window,
        ).aggregate(total=Sum('value_usd'))
        total = float(result['total'] or 0)
        return {'value': round(total, 2)}

    def _collect_publish_rate(self, now) -> dict:
        """Deliverable publish rate (72h)."""
        from core.models_deliverables import Deliverable
        window = now - timedelta(hours=72)
        try:
            total = Deliverable.objects.filter(
                created_at__gte=window,
            ).count()
            published = Deliverable.objects.filter(
                created_at__gte=window,
                status='published',
            ).count()
            rate = (published / total * 100) if total > 0 else 0
            return {
                'value': round(rate, 1),
                'published': published,
                'total': total,
            }
        except Exception:
            return {'value': 0}

    def _collect_error_rate(self, now) -> dict:
        """Agent execution error rate (24h)."""
        from core.models_unified_system import AgentExecution
        window = now - timedelta(hours=24)
        try:
            total = AgentExecution.objects.filter(
                created_at__gte=window,
            ).count()
            failed = AgentExecution.objects.filter(
                created_at__gte=window,
                status='failed',
            ).count()
            rate = (failed / total * 100) if total > 0 else 0
            return {
                'value': round(rate, 1),
                'failed': failed,
                'total': total,
            }
        except Exception:
            return {'value': 0}

    def get_experiments_report(self, now) -> dict:
        """Generate experiment status report for PA/governance."""
        from core.models_policy_experiment import PolicyExperiment

        active = list(
            PolicyExperiment.objects.filter(
                status='active',
            ).values(
                'id', 'policy_name', 'description',
                'success_metric', 'started_at',
                'baseline_metrics', 'treatment_metrics',
                'treatment_params', 'baseline_params',
                'success_threshold_pct', 'failure_threshold_pct',
            )
        )

        recent = list(
            PolicyExperiment.objects.filter(
                status__in=['promoted', 'rolled_back', 'expired'],
            ).order_by('-ended_at').values(
                'id', 'policy_name', 'status',
                'decision_reason', 'ended_at',
            )[:10]
        )

        # Serialize UUIDs and datetimes
        for exp in active + recent:
            for k, v in exp.items():
                if hasattr(v, 'isoformat'):
                    exp[k] = v.isoformat()
                elif hasattr(v, 'hex'):
                    exp[k] = str(v)

        return {
            'active_experiments': active,
            'recent_decisions': recent,
            'supported_policies': list(self.EXPERIMENTABLE_PARAMS.keys()),
            'supported_metrics': list(self.METRIC_COLLECTORS.keys()),
        }

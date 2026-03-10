"""
Ops Autopilot v8 — autonomous ops with governance guardrails.

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
 28. Engagement engine: Captures and classifies inbound prospect
     engagement (replies, meeting bookings, form fills). Classifies
     intent (positive, neutral, objection, meeting, unsubscribe).
     Suggests next actions. Draft replies require approval — never
     auto-sends. Permanent suppress on unsubscribe. Auto-closes
     stale unread events after 30 days. PA tools: engagement_inbox,
     engagement_classify, engagement_draft_reply, engagement_approve_reply,
     engagement_disqualify, engagement_metrics_report.
 29. Meeting engine: Tracks meetings from scheduling through follow-up.
     Generates pre-call briefs with prospect context, discovery questions,
     and suggested agenda. Post-meeting recap drafts (approval-gated).
     Manual-first v1 (no calendar integration). Flags meetings needing
     briefs (T-24h) and completed meetings awaiting follow-up (>48h).
     PA tools: meeting_create, meeting_inbox, meeting_brief,
     meeting_recap, meeting_metrics_report.
 30. Governance & safe-mode controls: GovernanceEngine manages global
     autonomy mode (normal/throttle/freeze/safe_mode) with per-agent
     and per-desk overrides. Kill switches with mandatory TTL for
     emergency stops. Auto-expires stale states to prevent deadlocks.
     Syncs budget flags with governance mode. Diagnostic "why are we
     throttled?" report. PA tools: governance_status, governance_set_mode,
     governance_kill_switch, governance_deactivate_switch,
     governance_throttle_report, governance_audit.
 31. Revenue pipeline orchestrator: RevenueOrchestrator unifies
     OutboundLeadEngine, OutreachSequencer, EngagementEngine,
     MeetingEngine, and CloseTheDealEngine into a single funnel view.
     Full pipeline status, conversion funnel metrics, and weighted
     revenue forecasts. Flags stale items across all stages.
     PA tools: revenue_full_pipeline, revenue_funnel, revenue_forecast.
 32. Knowledge & citation engine: KnowledgeEngine monitors citation
     health across the system via CitationViolation tracking, spider
     data freshness, research result quality, and source provenance.
     Reports violation trends, top offending agents, block rates,
     spider source coverage, and staleness detection with refresh
     recommendations. PA tools: knowledge_health, knowledge_citation_report,
     knowledge_source_report, knowledge_staleness_report.
 33. Close pack autonomy: ClosePackAutonomyEngine adds automated
     follow-up sequencing (draft generation for due packs), risk
     assessment (pricing guardrails, timeline checks, attribution
     gaps), pipeline velocity tracking (time-to-close, stage
     durations), and lifecycle evaluation (overdue follow-ups,
     stale drafts, high-risk flags). PA tools: close_pack_followup_queue,
     close_pack_risk_report, close_pack_velocity.
 34. Engagement autonomy: EngagementAutonomyEngine adds SLA-aware
     reply queue (warning/critical/breach tiers), auto-meeting
     suggestions for positive/meeting intent events, engagement-to-
     meeting-to-deal conversion funnel, and response time tracking.
     PA tools: engagement_sla_queue, engagement_meeting_suggestions,
     engagement_conversion_report.
 35. Growth & distribution autonomy: GrowthEngine finds distribution-ready
     content (published deliverables, blogs that passed quality gates),
     ranks by freshness + quality + revenue adjacency, tracks channel
     distribution (exports by format), manages scheduling with rate limits,
     and reports distribution funnel (candidates → exported → engaged →
     actions). PA tools: growth_candidates, growth_schedule,
     growth_channel_report, growth_funnel.
 36. Cost & capacity planning autonomy: CapacityEngine monitors task
     throughput (CeleryTaskEvent p50/p95 latency), identifies bottlenecks
     (slow agents, overloaded queues), projects spend vs budget caps, and
     provides throttle recommendations. PA tools: capacity_forecast,
     capacity_bottleneck_report, capacity_throttle_plan, capacity_budget_envelope.
 37. Security & abuse detection autonomy: SecurityEngine monitors for
     permission drift (admin-only routes, missing decorators), abuse
     patterns (unusual audit log activity, failed operations), secrets
     in content (API keys in deliverables/logs), and kill switch health.
     PA tools: security_permission_drift, security_abuse_queue,
     security_containment_plan, security_secrets_scan.

 38. Privacy, data governance & compliance autonomy: ComplianceEngine enforces
     data-handling rules — detects PII in deliverables/logs, monitors data
     retention TTLs, audits agent data access patterns, generates compliance
     reports. Read-only scanning; remediation is recommendation-only.
     PA tools: compliance_pii_scan, compliance_retention_report,
     compliance_access_audit, compliance_report.

 39. Data quality, schema drift & contract testing autonomy:
     DataIntegrityEngine monitors data quality across spider feeds,
     detects null/zero spikes, duplicate explosions, stale loads,
     and maintains per-source reliability scores.
     PA tools: integrity_quality_report, integrity_null_spike_scan,
     integrity_duplicate_report, integrity_reliability_scores.

 40. Customer value & outcomes autonomy: ValueRealizationEngine measures
     whether users are getting real value — tracks value events (agent
     executions, deliverables, revenue), computes outcome rates, detects
     usage without outcomes, generates value realization reports.
     PA tools: value_events_report, value_outcome_rates,
     value_usage_gaps, value_realization_summary.

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
        from core.services.ops_autopilot.impact import PortfolioAllocator
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
        from core.services.ops_autopilot.impact import PortfolioAllocator
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
        from core.services.ops_autopilot.impact import AttributionDebtController
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


# ── Policy 30: Governance & Safe-Mode Controls ─────────────────────────────



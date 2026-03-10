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
from core.services.ops_autopilot.config import AutopilotConfig
from core.services.ops_autopilot.verification import ActionVerifier


logger = logging.getLogger(__name__)


# ── Policy configuration ─────────────────────────────────────────────────────


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
        ('engagement', 'engagement_engine', '_policy_engagement_engine'),
        ('meetings', 'meeting_engine', '_policy_meeting_engine'),
        ('governance', 'governance_controls', '_policy_governance_controls'),
        ('revenue_orchestrator', 'revenue_orchestrator', '_policy_revenue_orchestrator'),
        ('knowledge', 'knowledge_citation_engine', '_policy_knowledge_citation_engine'),
        ('close_pack_autonomy', 'close_pack_autonomy', '_policy_close_pack_autonomy'),
        ('engagement_autonomy', 'engagement_autonomy', '_policy_engagement_autonomy'),
        ('growth_distribution', 'growth_distribution', '_policy_growth_distribution'),
        ('capacity_planning', 'capacity_planning', '_policy_capacity_planning'),
        ('security_abuse', 'security_abuse', '_policy_security_abuse'),
        ('compliance', 'compliance', '_policy_compliance'),
        ('data_integrity', 'data_integrity', '_policy_data_integrity'),
        ('value_realization', 'value_realization', '_policy_value_realization'),
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
        from core.services.ops_autopilot.remediation import RemediationEngine
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
        from core.services.ops_autopilot.governance import PolicyOptimizer
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
        from core.services.ops_autopilot.budget import BudgetController
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
        from core.services.ops_autopilot.budget import ROIEnforcer
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
        from core.services.ops_autopilot.impact import AttributionDebtController
        from core.services.ops_autopilot.impact import ImpactCollector
        from core.services.ops_autopilot.impact import PortfolioAllocator
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
        from core.services.ops_autopilot.impact import AttributionDebtController
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
        from core.services.ops_autopilot.experiment import ExperimentEngine
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
        from core.services.ops_autopilot.remediation import TimeoutRemediationPlaybook
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
        from core.services.ops_autopilot.remediation import DeliberationRemediationPlaybook
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
        from core.services.ops_autopilot.governance import BacklogGovernor
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
        from core.services.ops_autopilot.impact import GoalAwareAllocator
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
        from core.services.ops_autopilot.impact import MultiTouchAttributor
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
        from core.services.ops_autopilot.revenue import RevenuePipelineAutomator
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
        from core.services.ops_autopilot.revenue import OutboundLeadEngine
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
        from core.services.ops_autopilot.revenue import OutreachSequencer
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
        from core.services.ops_autopilot.revenue import CloseTheDealEngine
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

    def _policy_engagement_engine(self, now) -> dict:
        """
        Monitor engagement inbox — auto-close stale events,
        report unread/needs_reply counts.
        """
        from core.services.ops_autopilot.engagement import EngagementEngine
        result = {
            'unread': 0,
            'needs_reply': 0,
            'stale_closed': 0,
        }

        try:
            engine = EngagementEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            logger.info(
                f"[OpsAutopilot] Engagement: "
                f"{result['unread']} unread, "
                f"{result['needs_reply']} needs reply, "
                f"{result['stale_closed']} auto-closed"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] engagement engine error: {e}")
            result['error'] = str(e)

        return result

    def _policy_meeting_engine(self, now) -> dict:
        """
        Monitor meeting pipeline — flag meetings needing briefs,
        stale follow-ups, and upcoming meeting counts.
        """
        from core.services.ops_autopilot.engagement import MeetingEngine
        result = {
            'upcoming': 0,
            'needs_brief': 0,
            'past_no_followup': 0,
        }

        try:
            engine = MeetingEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            logger.info(
                f"[OpsAutopilot] Meetings: "
                f"{result['upcoming']} upcoming, "
                f"{result['needs_brief']} need brief, "
                f"{result['past_no_followup']} need follow-up"
            )

        except Exception as e:
            logger.error(f"[OpsAutopilot] meeting engine error: {e}")
            result['error'] = str(e)

        return result

    def _policy_governance_controls(self, now) -> dict:
        """
        Auto-expire governance states and kill switches.
        Sync budget flags when governance mode changes.
        """
        from core.services.ops_autopilot.governance import GovernanceEngine
        result = {
            'expired_states': 0,
            'expired_switches': 0,
        }

        try:
            engine = GovernanceEngine()
            eval_result = engine.evaluate(now)
            if eval_result:
                result.update(eval_result)

                if eval_result.get('expired_states', 0) > 0:
                    logger.info(
                        f"[OpsAutopilot] Governance: expired "
                        f"{eval_result['expired_states']} states, "
                        f"{eval_result.get('expired_switches', 0)} switches"
                    )

        except Exception as e:
            logger.error(f"[OpsAutopilot] governance controls error: {e}")
            result['error'] = str(e)

        return result

    def _policy_revenue_orchestrator(self, now) -> dict:
        """
        Monitor unified revenue pipeline health.
        Flags stale items across all pipeline stages.
        """
        from core.services.ops_autopilot.revenue import RevenueOrchestrator
        result = {
            'issue_count': 0,
            'healthy': True,
        }

        try:
            engine = RevenueOrchestrator()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if eval_result.get('issue_count', 0) > 0:
                logger.info(
                    f"[OpsAutopilot] Revenue pipeline: "
                    f"{eval_result['issue_count']} issues — "
                    f"{', '.join(eval_result.get('pipeline_issues', []))}"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] revenue orchestrator error: {e}")
            result['error'] = str(e)

        return result

    def _policy_knowledge_citation_engine(self, now) -> dict:
        """
        Monitor citation health and knowledge quality.
        Flags high violation rates and stale knowledge sources.
        """
        from core.services.ops_autopilot.intelligence import KnowledgeEngine
        result = {
            'violation_count_24h': 0,
            'block_count_24h': 0,
            'spider_staleness': {},
            'healthy': True,
        }

        try:
            engine = KnowledgeEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Knowledge engine: "
                    f"{eval_result.get('violation_count_24h', 0)} violations, "
                    f"{eval_result.get('block_count_24h', 0)} blocks"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] knowledge citation engine error: {e}")
            result['error'] = str(e)

        return result

    def _policy_close_pack_autonomy(self, now) -> dict:
        """
        Monitor close pack lifecycle: follow-up sequencing, risk flags,
        stale drafts.
        """
        from core.services.ops_autopilot.revenue import ClosePackAutonomyEngine
        result = {
            'overdue_followups': 0,
            'high_risk_packs': 0,
            'healthy': True,
        }

        try:
            engine = ClosePackAutonomyEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Close pack autonomy: "
                    f"{eval_result.get('overdue_followups', 0)} overdue, "
                    f"{eval_result.get('high_risk_packs', 0)} high-risk"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] close pack autonomy error: {e}")
            result['error'] = str(e)

        return result

    def _policy_engagement_autonomy(self, now) -> dict:
        """
        Monitor engagement SLA health: breaches, high-intent backlogs,
        queue size.
        """
        from core.services.ops_autopilot.engagement import EngagementAutonomyEngine
        result = {
            'sla_breaches': 0,
            'high_intent_unactioned': 0,
            'healthy': True,
        }

        try:
            engine = EngagementAutonomyEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Engagement autonomy: "
                    f"{eval_result.get('sla_breaches', 0)} SLA breaches, "
                    f"{eval_result.get('high_intent_unactioned', 0)} high-intent unactioned"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] engagement autonomy error: {e}")
            result['error'] = str(e)

        return result

    def _policy_growth_distribution(self, now) -> dict:
        """
        Monitor distribution pipeline health: undistributed content backlog,
        channel coverage, scheduling gaps.
        """
        from core.services.ops_autopilot.intelligence import GrowthEngine
        result = {
            'undistributed': 0,
            'scheduled': 0,
            'healthy': True,
        }

        try:
            engine = GrowthEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Growth distribution: "
                    f"{eval_result.get('undistributed', 0)} undistributed, "
                    f"{eval_result.get('stale_scheduled', 0)} stale scheduled"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] growth distribution error: {e}")
            result['error'] = str(e)

        return result

    def _policy_capacity_planning(self, now) -> dict:
        """
        Monitor capacity health: task throughput, queue wait times,
        bottlenecks, spend projections.
        """
        from core.services.ops_autopilot.intelligence import CapacityEngine
        result = {
            'bottlenecks': 0,
            'projected_overspend': False,
            'healthy': True,
        }

        try:
            engine = CapacityEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Capacity planning: "
                    f"{eval_result.get('bottleneck_count', 0)} bottlenecks, "
                    f"queue backlog {eval_result.get('total_pending', 0)}"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] capacity planning error: {e}")
            result['error'] = str(e)

        return result

    def _policy_security_abuse(self, now) -> dict:
        """
        Monitor security health: permission drift, abuse patterns,
        kill switch hygiene, secrets exposure.
        """
        from core.services.ops_autopilot.intelligence import SecurityEngine
        result = {
            'abuse_flags': 0,
            'drift_issues': 0,
            'healthy': True,
        }

        try:
            engine = SecurityEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Security: "
                    f"{eval_result.get('abuse_flags', 0)} abuse flags, "
                    f"{eval_result.get('drift_issues', 0)} drift issues"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] security abuse error: {e}")
            result['error'] = str(e)

        return result

    def _policy_compliance(self, now) -> dict:
        """
        Monitor data governance: PII exposure in content,
        retention TTL compliance, agent data access patterns.
        """
        from core.services.ops_autopilot.intelligence import ComplianceEngine
        result = {
            'pii_findings': 0,
            'retention_violations': 0,
            'healthy': True,
        }

        try:
            engine = ComplianceEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] Compliance: "
                    f"{eval_result.get('pii_findings', 0)} PII findings, "
                    f"{eval_result.get('retention_violations', 0)} retention violations"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] compliance error: {e}")
            result['error'] = str(e)

        return result

    def _policy_data_integrity(self, now) -> dict:
        """
        Monitor data quality: null spikes, duplicate explosions,
        stale feeds, per-source reliability scores.
        """
        from core.services.ops_autopilot.intelligence import DataIntegrityEngine
        result = {
            'null_spikes': 0,
            'duplicate_issues': 0,
            'healthy': True,
        }

        try:
            engine = DataIntegrityEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] DataIntegrity: "
                    f"{eval_result.get('null_spikes', 0)} null spikes, "
                    f"{eval_result.get('duplicate_issues', 0)} duplicate issues"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] data integrity error: {e}")
            result['error'] = str(e)

        return result

    def _policy_value_realization(self, now) -> dict:
        """
        Monitor user value realization: value events, outcome rates,
        usage gaps, overall value health.
        """
        from core.services.ops_autopilot.intelligence import ValueRealizationEngine
        result = {
            'value_events': 0,
            'outcome_rate': 0.0,
            'healthy': True,
        }

        try:
            engine = ValueRealizationEngine()
            eval_result = engine.evaluate(now)
            result.update(eval_result)

            if not eval_result.get('healthy', True):
                logger.info(
                    f"[OpsAutopilot] ValueRealization: "
                    f"{eval_result.get('value_events', 0)} events, "
                    f"{eval_result.get('outcome_rate', 0):.0%} outcome rate"
                )

        except Exception as e:
            logger.error(f"[OpsAutopilot] value realization error: {e}")
            result['error'] = str(e)

        return result

    def _policy_release_governor(self, now) -> dict:
        """
        Monitor deploy health and apply graduated safety measures.
        L0=observe, L1=backoff, L2=gate, L3=freeze.
        """
        from core.services.ops_autopilot.governance import ReleaseGovernor
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
        from core.services.ops_autopilot.governance import PolicyArbitrator
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


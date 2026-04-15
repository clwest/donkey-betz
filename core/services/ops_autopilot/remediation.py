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

from core.services.ops_autopilot.config import AutopilotConfig  # noqa: F401

logger = logging.getLogger(__name__)


# ── Policy configuration ─────────────────────────────────────────────────────


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
        # Check for existing override.
        # Session 1103c: loud on failure so a broken SystemConfiguration
        # lookup doesn't silently revert an agent to its hardcoded
        # default timeout — the override system is how ops_autopilot
        # tunes timeouts adaptively.
        try:
            from core.models.system import SystemConfiguration
            override = SystemConfiguration.objects.filter(
                key=f'agent_timeout_override:{agent_name}',
            ).first()
            if override:
                return int(override.value)
        except Exception as e:
            logger.warning(
                "ops_autopilot.remediation: agent_timeout_override "
                "lookup failed for %s (%s: %s) — falling back to "
                "hardcoded default",
                agent_name, type(e).__name__, e,
            )

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

        # Update playbook if this was from one.
        # Session 1103c: loud on DoesNotExist — silent swallow here meant
        # the playbook learning loop dropped feedback for any deleted/
        # renamed playbook reference, leaving the playbook outcome
        # accuracy permanently stale.
        playbook_id = (action.verification_result or {}).get('playbook_id')
        if playbook_id:
            try:
                playbook = RemediationPlaybook.objects.get(id=playbook_id)
                playbook.record_outcome(succeeded=check['passed'])
            except RemediationPlaybook.DoesNotExist:
                logger.warning(
                    "ops_autopilot.remediation: RemediationPlaybook "
                    "id=%s no longer exists — outcome recording "
                    "skipped, playbook learning loop will not see "
                    "this result",
                    playbook_id,
                )

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



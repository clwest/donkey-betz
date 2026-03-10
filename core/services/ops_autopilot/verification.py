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
        from core.services.ops_autopilot.remediation import RemediationEngine
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



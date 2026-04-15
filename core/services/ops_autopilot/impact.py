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
        except Exception as _e:
            # Session 1103c: was 'except Exception: pass' which
            # silently dropped per-desk impact aggregation. The IQROI
            # calculation downstream then ran on empty desk_impact
            # and produced misleading per-desk ROI numbers with no
            # signal that the upstream query had broken.
            logger.warning(
                "ops_autopilot.impact: desk_impact aggregation failed "
                "(%s: %s) — IQROI per-desk numbers will be missing "
                "this slice",
                type(_e).__name__, _e,
            )

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
        except Exception as _e:
            # Session 1103c: sibling fix to the desk_impact swallow
            # above. Without desk_cost, IQROI per-desk
            # (impact / cost) divides by an empty dict and produces
            # zero-cost ROI numbers — making every desk look
            # infinitely profitable.
            logger.warning(
                "ops_autopilot.impact: desk_cost aggregation failed "
                "(%s: %s) — IQROI per-desk cost basis will be "
                "missing, ROI numbers will look artificially high",
                type(_e).__name__, _e,
            )

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
        """Read prior allocation from SystemConfiguration for EWMA.

        Session 1083 (Rigby audit): was `except Exception: pass` which
        silently returned None on DB error, which the EWMA path treats
        as "first run — use current score". A transient DB hiccup
        during normal operation would therefore erase the smoothing
        history and let allocation decisions bounce around.
        """
        from core.models.system import SystemConfiguration

        try:
            entry = SystemConfiguration.objects.filter(
                key=f'desk_allocation:{desk}',
            ).values_list('value', flat=True).first()

            if entry and isinstance(entry, dict):
                return entry.get('allocation')
        except Exception as e:
            logger.warning(
                "PortfolioAllocator._get_prior_allocation: lookup for "
                "desk=%s failed (%s: %s) — EWMA smoothing will reset",
                desk, type(e).__name__, e,
            )
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
        except Exception as exc:
            logger.warning(
                "get_portfolio_report: active allocations query failed "
                "(%s: %s) — report will show empty allocations map",
                type(exc).__name__, exc,
            )

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
        """Get current objective weights from config or defaults.

        Session 1083: was bare-pass — if the config table had a real DB
        error, the allocator silently reverted to DEFAULT_WEIGHTS and
        Chris's operator-configured weights were ignored until process
        restart with no visible signal. Log loud.
        """
        from core.models.system import SystemConfiguration
        try:
            entry = SystemConfiguration.objects.filter(
                key=self.KEY_WEIGHTS,
            ).first()
            if entry and isinstance(entry.value, dict):
                return entry.value
        except Exception as e:
            logger.warning(
                "GoalAwareAllocator.get_weights: config read failed "
                "(%s: %s) — falling back to DEFAULT_WEIGHTS, any "
                "operator-configured weights will be ignored",
                type(e).__name__, e,
            )
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
        """Read prior goal allocation for EWMA.

        Session 1083: was bare-pass — same EWMA-smoothing erase risk as
        PortfolioAllocator._get_prior_allocation above.
        """
        from core.models.system import SystemConfiguration
        try:
            entry = SystemConfiguration.objects.filter(
                key=f'goal_allocation:{desk}',
            ).values_list('value', flat=True).first()
            if entry and isinstance(entry, dict):
                return entry.get('multiplier')
        except Exception as e:
            logger.warning(
                "GoalAwareAllocator._get_prior: lookup for desk=%s "
                "failed (%s: %s) — EWMA smoothing will reset",
                desk, type(e).__name__, e,
            )
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
        except Exception as exc:
            logger.warning(
                "get_goal_report: active allocations query failed "
                "(%s: %s) — report will show empty map",
                type(exc).__name__, exc,
            )

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
        except Exception as e:
            # Session 1083: was bare pass — trace_id attribution would
            # silently drop every upstream link, dragging every cost
            # into unattributed spend when the query degraded.
            logger.warning(
                "MultiTouchAttributor._find_by_trace: query failed "
                "(%s: %s) — trace-based attribution dropped for this event",
                type(e).__name__, e,
            )
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

        except Exception as e:
            # Session 1083: was bare pass — same attribution LIAR as
            # _find_by_trace above. Deliverable-chain linkage would
            # silently drop every upstream agent credit.
            logger.warning(
                "MultiTouchAttributor._find_by_deliverable: query "
                "failed (%s: %s) — deliverable-chain attribution dropped",
                type(e).__name__, e,
            )
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
        except Exception as e:
            # Session 1083: was bare pass — ImpactEvent-based desk
            # lookup silently returned None, which pushes the agent's
            # cost into unattributed spend (raising debt_pct).
            logger.warning(
                "get_agent_desk: ImpactEvent lookup for agent=%s "
                "failed (%s: %s) — desk will be reported as None and "
                "cost counted as unattributed",
                agent_name, type(e).__name__, e,
            )

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


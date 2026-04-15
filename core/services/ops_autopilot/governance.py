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

        # Check daily change cap.
        # Session 1103c: was 'except Exception: changes_today = 0'
        # which is fail-OPEN — DB query failure silently bypassed the
        # daily cap and let self-tuning proceed as if no changes had
        # been made today, allowing unbounded config tuning during a
        # partial DB outage exactly when governance should be
        # conservative. Now fails CLOSED to the cap so tuning is
        # blocked when we can't verify how many changes have already
        # happened.
        try:
            day_start = now - timedelta(hours=24)
            changes_today = AutopilotAction.objects.filter(
                action_type='config_tune',
                dry_run=False,
                created_at__gte=day_start,
            ).count()
        except Exception as _e:
            logger.error(
                "ops_autopilot.governance: daily change cap query "
                "failed (%s: %s) — failing CLOSED (treating as "
                "AT-CAP) to prevent unbounded tuning during a "
                "partial DB outage",
                type(_e).__name__, _e,
            )
            changes_today = AutopilotConfig.TUNING_MAX_CHANGES_PER_DAY

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
        except Exception as _e:
            logger.warning(
                "ops_governance.get_tuning_report: swallowed (%s: %s) — report may be partial",
                type(_e).__name__, _e,
            )

        return report


# ── Budget Controller ────────────────────────────────────────────────────────


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
        except Exception as _e:
            logger.warning(
                "ops_governance.detect_conflicts: swallowed (%s: %s) — report may be partial",
                type(_e).__name__, _e,
            )

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
        except Exception as _e:
            logger.warning(
                "ops_governance._detect_hold_violations: swallowed (%s: %s) — report may be partial",
                type(_e).__name__, _e,
            )

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

        except Exception as _e:
            logger.warning(
                "ops_governance._count_recent_deploys: swallowed (%s: %s) — report may be partial",
                type(_e).__name__, _e,
            )

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

class GovernanceEngine:
    """
    Autonomy control plane — single source of truth for system-wide
    governance state, per-agent overrides, and kill switches.

    Modes (escalation ladder):
      normal   → full autonomy, all systems go
      throttle → reduced batch sizes, deferred non-critical tasks
      freeze   → only critical LLM calls allowed
      safe_mode → all autonomous actions paused, human approval for everything

    Kill switches: targeted emergency controls with mandatory TTL.
    """

    MODE_SEVERITY = {'normal': 0, 'throttle': 1, 'freeze': 2, 'safe_mode': 3}
    VALID_MODES = set(MODE_SEVERITY.keys())
    DEFAULT_TTL_HOURS = 4  # Kill switches expire after 4h by default
    MAX_TTL_HOURS = 72     # No kill switch longer than 72h

    # ── Status ────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Full governance status report."""
        from core.models_governance import GovernanceState, KillSwitch
        from django.utils import timezone as tz

        now = tz.now()

        # Global mode
        global_state = GovernanceState.objects.filter(
            scope='global', scope_target='',
        ).first()

        if not global_state:
            global_mode = 'normal'
            global_reason = 'No explicit governance state set'
            global_expires = None
        else:
            global_mode = global_state.effective_mode
            global_reason = global_state.reason
            global_expires = (
                global_state.expires_at.isoformat()
                if global_state.expires_at else None
            )

        # Per-scope overrides
        overrides = []
        for ov in GovernanceState.objects.exclude(
            scope='global',
        ).order_by('scope', 'scope_target'):
            overrides.append({
                'scope': ov.scope,
                'target': ov.scope_target,
                'mode': ov.effective_mode,
                'reason': ov.reason,
                'set_by': ov.set_by,
                'expires_at': ov.expires_at.isoformat() if ov.expires_at else None,
                'expired': ov.is_expired,
            })

        # Active kill switches
        active_switches = []
        for ks in KillSwitch.objects.filter(is_active=True):
            active_switches.append({
                'id': str(ks.id),
                'target': ks.target,
                'detail': ks.target_detail,
                'reason': ks.reason,
                'activated_by': ks.activated_by,
                'expires_at': ks.expires_at.isoformat(),
                'expired': ks.is_expired,
                'time_remaining': str(ks.expires_at - now) if ks.expires_at > now else 'expired',
            })

        # Budget state
        from core.models.system import SystemConfiguration
        budget_flags = {}
        for key in ['budget_freeze_active', 'budget_downgrade_active', 'budget_mode']:
            val = SystemConfiguration.objects.filter(
                key=key, is_active=True,
            ).values_list('value', flat=True).first()
            budget_flags[key] = val or ''

        # Active throttles
        throttle_count = SystemConfiguration.objects.filter(
            key__startswith='roi_throttle:', is_active=True,
        ).count()

        return {
            'global_mode': global_mode,
            'global_reason': global_reason,
            'global_expires_at': global_expires,
            'overrides': overrides,
            'active_kill_switches': active_switches,
            'budget_flags': budget_flags,
            'active_throttle_count': throttle_count,
            'timestamp': now.isoformat(),
        }

    # ── Set mode ──────────────────────────────────────────────────────

    def set_mode(
        self,
        mode: str,
        reason: str = '',
        scope: str = 'global',
        scope_target: str = '',
        ttl_hours: float | None = None,
        set_by: str = 'user',
        user=None,
    ) -> dict:
        """Set governance mode for a scope."""
        from core.models_governance import GovernanceState
        from django.utils import timezone as tz

        if mode not in self.VALID_MODES:
            return {'error': f'Invalid mode: {mode}. Valid: {list(self.VALID_MODES)}'}

        if scope not in ('global', 'agent', 'desk'):
            return {'error': f'Invalid scope: {scope}'}

        if scope != 'global' and not scope_target:
            return {'error': f'scope_target required for scope={scope}'}

        expires_at = None
        if ttl_hours:
            ttl_hours = min(ttl_hours, self.MAX_TTL_HOURS)
            expires_at = tz.now() + timedelta(hours=ttl_hours)

        state, created = GovernanceState.objects.update_or_create(
            scope=scope,
            scope_target=scope_target or '',
            defaults={
                'mode': mode,
                'reason': reason,
                'set_by': set_by,
                'expires_at': expires_at,
                'user': user,
            },
        )

        # Sync budget flags when setting global mode
        if scope == 'global':
            self._sync_budget_flags(mode)

        return {
            'id': str(state.id),
            'scope': scope,
            'target': scope_target,
            'mode': mode,
            'reason': reason,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'created': created,
        }

    def _sync_budget_flags(self, mode: str):
        """Sync SystemConfiguration budget flags with governance mode."""
        from core.models.system import SystemConfiguration

        if mode == 'normal':
            # Clear freeze/downgrade
            SystemConfiguration.objects.filter(
                key__in=['budget_freeze_active', 'budget_downgrade_active'],
            ).update(value='', is_active=False)
            SystemConfiguration.objects.update_or_create(
                key='budget_mode',
                defaults={'value': 'normal', 'category': 'performance', 'is_active': True},
            )
        elif mode == 'throttle':
            SystemConfiguration.objects.filter(
                key='budget_freeze_active',
            ).update(value='', is_active=False)
            SystemConfiguration.objects.update_or_create(
                key='budget_downgrade_active',
                defaults={'value': True, 'category': 'performance', 'is_active': True},
            )
            SystemConfiguration.objects.update_or_create(
                key='budget_mode',
                defaults={'value': 'downgrade', 'category': 'performance', 'is_active': True},
            )
        elif mode in ('freeze', 'safe_mode'):
            SystemConfiguration.objects.update_or_create(
                key='budget_freeze_active',
                defaults={'value': True, 'category': 'performance', 'is_active': True},
            )
            SystemConfiguration.objects.update_or_create(
                key='budget_downgrade_active',
                defaults={'value': True, 'category': 'performance', 'is_active': True},
            )
            SystemConfiguration.objects.update_or_create(
                key='budget_mode',
                defaults={'value': 'freeze', 'category': 'performance', 'is_active': True},
            )

    # ── Kill switch ───────────────────────────────────────────────────

    def activate_kill_switch(
        self,
        target: str,
        reason: str = '',
        target_detail: str = '',
        ttl_hours: float | None = None,
        activated_by: str = 'user',
        user=None,
    ) -> dict:
        """Activate an emergency kill switch."""
        from core.models_governance import KillSwitch
        from django.utils import timezone as tz

        valid_targets = {c[0] for c in KillSwitch.TARGET_CHOICES}
        if target not in valid_targets:
            return {'error': f'Invalid target: {target}. Valid: {valid_targets}'}

        ttl = ttl_hours or self.DEFAULT_TTL_HOURS
        ttl = min(ttl, self.MAX_TTL_HOURS)
        expires_at = tz.now() + timedelta(hours=ttl)

        ks = KillSwitch.objects.create(
            target=target,
            target_detail=target_detail,
            reason=reason,
            activated_by=activated_by,
            expires_at=expires_at,
            user=user,
        )

        return {
            'id': str(ks.id),
            'target': target,
            'detail': target_detail,
            'reason': reason,
            'expires_at': expires_at.isoformat(),
            'ttl_hours': ttl,
        }

    def deactivate_kill_switch(self, switch_id: str) -> dict:
        """Manually deactivate a kill switch."""
        from core.models_governance import KillSwitch

        try:
            ks = KillSwitch.objects.get(id=switch_id, is_active=True)
        except KillSwitch.DoesNotExist:
            return {'error': f'Kill switch {switch_id} not found or already inactive'}

        ks.deactivate()
        return {
            'id': str(ks.id),
            'target': ks.target,
            'detail': ks.target_detail,
            'deactivated': True,
        }

    # ── Diagnostics ───────────────────────────────────────────────────

    def get_throttle_report(self) -> dict:
        """'Why are we throttled?' diagnostic report."""
        from core.models.system import SystemConfiguration
        from core.models_governance import GovernanceState
        from django.utils import timezone as tz

        now = tz.now()

        # Current governance mode
        global_state = GovernanceState.objects.filter(
            scope='global', scope_target='',
        ).first()
        current_mode = global_state.effective_mode if global_state else 'normal'

        # Budget state
        budget_info = {}
        for key in ['budget_freeze_active', 'budget_downgrade_active', 'budget_mode',
                     'BUDGET_DAILY_CAP_USD', 'budget_daily_cap_usd']:
            val = SystemConfiguration.objects.filter(
                key=key,
            ).values_list('value', 'is_active').first()
            if val:
                budget_info[key] = {'value': val[0], 'is_active': val[1]}

        # Active ROI throttles
        throttles = []
        for entry in SystemConfiguration.objects.filter(
            key__startswith='roi_throttle:',
        ).values('key', 'value', 'is_active'):
            throttles.append({
                'agent': entry['key'].replace('roi_throttle:', ''),
                'is_active': entry['is_active'],
                'data': entry['value'],
            })

        # Recent spend (last 24h)
        from django.db.models import Sum
        from core.models_llm_routing import LLMCallLog
        day_ago = now - timedelta(hours=24)
        spend_24h = LLMCallLog.objects.filter(
            created_at__gte=day_ago,
        ).aggregate(total=Sum('cost'))['total'] or 0

        hour_ago = now - timedelta(hours=1)
        spend_1h = LLMCallLog.objects.filter(
            created_at__gte=hour_ago,
        ).aggregate(total=Sum('cost'))['total'] or 0

        # Budget cap
        cap = (
            AutopilotConfig.get('BUDGET_DAILY_CAP_USD')
            or AutopilotConfig.BUDGET_DAILY_CAP_USD
        )
        try:
            cap = float(cap)
        except (TypeError, ValueError):
            cap = 100.0

        return {
            'current_mode': current_mode,
            'spend_24h_usd': round(float(spend_24h), 4),
            'spend_1h_usd': round(float(spend_1h), 4),
            'budget_cap_usd': cap,
            'spend_pct': round(float(spend_24h) / cap * 100, 1) if cap > 0 else 0,
            'budget_flags': budget_info,
            'active_throttles': [t for t in throttles if t['is_active']],
            'inactive_throttles': [t for t in throttles if not t['is_active']],
            'diagnosis': self._diagnose(current_mode, float(spend_24h), cap, throttles),
        }

    def _diagnose(self, mode: str, spend: float, cap: float, throttles: list) -> list[str]:
        """Generate human-readable diagnosis of why the system is constrained."""
        issues = []

        if mode != 'normal':
            issues.append(f'Global mode is "{mode}" — not all systems are running freely')

        pct = spend / cap * 100 if cap > 0 else 0
        if pct > 95:
            issues.append(
                f'Daily spend ${spend:.2f} is {pct:.0f}% of ${cap:.0f} cap — '
                f'hard freeze threshold reached'
            )
        elif pct > 70:
            issues.append(
                f'Daily spend ${spend:.2f} is {pct:.0f}% of ${cap:.0f} cap — '
                f'soft limit / downgrade zone'
            )

        active = [t for t in throttles if t['is_active']]
        if active:
            names = ', '.join(t['agent'] for t in active[:5])
            issues.append(f'{len(active)} agents on ROI cooldown: {names}')

        if not issues:
            issues.append('System is operating normally — no constraints detected')

        return issues

    # ── Evaluate (called by autopilot cycle) ─────────────────────────

    def evaluate(self, now) -> dict | None:
        """
        Auto-expire stale governance states and kill switches.
        Called by the autopilot cycle.
        """
        from core.models_governance import GovernanceState, KillSwitch

        expired_states = 0
        expired_switches = 0

        # Auto-expire governance states
        for state in GovernanceState.objects.filter(
            expires_at__isnull=False,
            expires_at__lt=now,
        ).exclude(mode='normal'):
            state.mode = 'normal'
            state.reason = f'Auto-expired (was: {state.reason[:100]})'
            state.set_by = 'autopilot_expire'
            state.expires_at = None
            state.save(update_fields=['mode', 'reason', 'set_by', 'expires_at', 'updated_at'])
            expired_states += 1

        # Auto-expire kill switches
        for ks in KillSwitch.objects.filter(
            is_active=True,
            expires_at__lt=now,
        ):
            ks.deactivate()
            expired_switches += 1

        # Sync global mode → budget flags (in case expire changed it)
        global_state = GovernanceState.objects.filter(
            scope='global', scope_target='',
        ).first()
        if global_state and global_state.effective_mode == 'normal':
            self._sync_budget_flags('normal')

        if expired_states == 0 and expired_switches == 0:
            return None

        return {
            'type': 'governance_expire',
            'expired_states': expired_states,
            'expired_switches': expired_switches,
        }

    # ── Audit log ─────────────────────────────────────────────────────

    def get_audit_log(self, limit: int = 20) -> dict:
        """Recent governance changes."""
        from core.models_governance import GovernanceState, KillSwitch

        recent_states = list(
            GovernanceState.objects.order_by('-updated_at').values(
                'id', 'scope', 'scope_target', 'mode', 'reason',
                'set_by', 'expires_at', 'updated_at',
            )[:limit]
        )

        recent_switches = list(
            KillSwitch.objects.order_by('-created_at').values(
                'id', 'target', 'target_detail', 'reason',
                'activated_by', 'is_active', 'expires_at',
                'created_at', 'deactivated_at',
            )[:limit]
        )

        # Serialize
        for item in recent_states + recent_switches:
            for k, v in item.items():
                if hasattr(v, 'isoformat'):
                    item[k] = v.isoformat()
                elif hasattr(v, 'hex'):
                    item[k] = str(v)

        return {
            'recent_state_changes': recent_states,
            'recent_kill_switches': recent_switches,
        }


# ── Policy 31: Revenue Pipeline Orchestrator ────────────────────────────────



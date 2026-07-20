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
            key='budget_freeze_active', is_active=True,
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

    # ─────────────────────────────────────────────────────────────────
    # Session 2846 (A1 W1 Phase 2) — per-workspace attribution & caps.
    #
    # Cap-keying policy (Fold 2, ratified S2846):
    #   Caps are keyed by workspace_id, NOT by owner. If a workspace is
    #   reassigned or its owning user is deleted, the cap follows the
    #   workspace id. This decouples billing from user identity and
    #   supports future multi-owner workspaces.
    #
    # Null-bucket policy (Fold 3, ratified S2846):
    #   LLMCallLog rows with workspace=NULL are treated as a distinct
    #   "system" bucket (embedding jobs, background tasks without user
    #   context). compute_workspace_spend(workspace_id=None) reports
    #   spend on that bucket separately. enforce_workspace_freeze does
    #   NOT freeze the null bucket — global freeze is the mechanism.
    #
    # Cache policy (Fold 4, ratified S2846):
    #   No memoization in W1. Every is_workspace_frozen call hits the
    #   SystemConfiguration DB. Fine for pre-prod; revisit at scale.
    # ─────────────────────────────────────────────────────────────────

    _WORKSPACE_CAP_KEY_PREFIX = 'workspace_daily_cap:'
    _WORKSPACE_FREEZE_KEY_PREFIX = 'workspace_freeze_active:'
    _WORKSPACE_DOWNGRADE_KEY_PREFIX = 'workspace_downgrade_active:'

    # S2848 W1.5: hysteresis threshold — auto-clear downgrade when spend
    # drops below 60% of cap (set at 70%, clear at 60%). Prevents flap on
    # small caps where a single call could cross 70% and drop back.
    _WORKSPACE_DOWNGRADE_CLEAR_PCT = 0.60

    # S2849 W2 #2a — global default cap key. Lazy fallback: workspaces
    # without an explicit workspace_daily_cap:<uuid> row use this value
    # via get_effective_workspace_daily_cap(). Autopilot enforcement is
    # still caps-only (iterates list_workspace_caps), so backfill_defaults
    # is required to bring existing workspaces under enforcement.
    _WORKSPACE_DEFAULT_CAP_KEY = 'workspace_default_daily_cap'

    def compute_workspace_spend(self, now, workspace_id=None) -> dict:
        """Per-workspace spend from LLMCallLog.

        workspace_id=<uuid>: spend for that specific workspace.
        workspace_id=None: spend for the null-workspace bucket (system
        tasks / embedding jobs — Fold 3 explicit null handling).
        """
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum, Count

        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(hours=24)

        if workspace_id is None:
            base_qs = LLMCallLog.objects.filter(workspace__isnull=True)
        else:
            base_qs = LLMCallLog.objects.filter(workspace_id=workspace_id)

        daily = base_qs.filter(created_at__gte=day_ago).aggregate(
            total=Sum('cost'),
            calls=Count('id'),
        )
        hourly = base_qs.filter(created_at__gte=hour_ago).aggregate(
            total=Sum('cost'),
            calls=Count('id'),
        )

        return {
            'workspace_id': str(workspace_id) if workspace_id else None,
            'daily_total': float(daily['total'] or 0),
            'daily_calls': daily['calls'] or 0,
            'hourly_total': float(hourly['total'] or 0),
            'hourly_calls': hourly['calls'] or 0,
        }

    def get_workspace_daily_cap(self, workspace_id):
        """Look up the per-workspace daily cap ($ USD) from SystemConfiguration.

        Returns the EXPLICIT cap (float) or None (no per-workspace cap
        row). Does NOT fall back to the global default — that's what
        get_effective_workspace_daily_cap is for. Autopilot enforcement
        and the existing operator surfaces intentionally read explicit
        caps only.
        """
        if workspace_id is None:
            return None
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_CAP_KEY_PREFIX}{workspace_id}"
        entry = (
            SystemConfiguration.objects
            .filter(key=key)
            .values_list('value', flat=True)
            .first()
        )
        if entry is None:
            return None
        try:
            return float(entry)
        except (TypeError, ValueError):
            logger.warning(
                "BudgetController: workspace_daily_cap for workspace_id=%s "
                "is not a valid float (value=%r) — treating as no cap",
                workspace_id, entry,
            )
            return None

    def get_workspace_default_cap(self):
        """Read the global default per-workspace daily cap ($ USD).

        S2849 W2 #2a. Returns float or None when unset. Operator
        configurable via workspace_budget_tool.set_default_cap.
        """
        from core.models.system import SystemConfiguration
        entry = (
            SystemConfiguration.objects
            .filter(key=self._WORKSPACE_DEFAULT_CAP_KEY)
            .values_list('value', flat=True)
            .first()
        )
        if entry is None:
            return None
        try:
            return float(entry)
        except (TypeError, ValueError):
            logger.warning(
                "BudgetController: workspace_default_daily_cap value=%r "
                "is not a valid float — treating as unset",
                entry,
            )
            return None

    def set_workspace_default_cap(self, cap, actor_user_id=None):
        """Write/update the global default per-workspace daily cap.

        S2849 W2 #2a. cap must be > 0. Writes an AutopilotAction row
        when actor_user_id is provided so operator changes are audit-
        trailed alongside set_workspace_daily_cap events.
        """
        try:
            cap = float(cap)
        except (TypeError, ValueError):
            raise ValueError(f"default cap must be a float, got {cap!r}")
        if cap <= 0:
            raise ValueError(f"default cap must be > 0, got {cap}")
        from core.models.system import SystemConfiguration
        previous = self.get_workspace_default_cap()
        SystemConfiguration.objects.update_or_create(
            key=self._WORKSPACE_DEFAULT_CAP_KEY,
            defaults={
                'value': cap,
                'description': (
                    'Global default per-workspace daily cap ($ USD). '
                    'Lazy fallback for workspaces without an explicit '
                    'workspace_daily_cap:<uuid>. Enforcement still '
                    'requires backfill_defaults to write explicit rows.'
                ),
                'category': 'performance',
            },
        )
        changed = previous != cap
        logger.info(
            "[BudgetController] Set workspace default daily cap — "
            "cap=$%.2f (previous=%s, changed=%s)",
            cap, previous, changed,
        )
        if actor_user_id is not None and changed:
            AutopilotAction.objects.create(
                action_type='workspace_default_cap_set',
                agent_name='workspace_budget_tool',
                policy='workspace_budget_tool',
                dry_run=False,
                evidence={
                    'actor_user_id': str(actor_user_id),
                    'previous_cap': previous,
                },
                result={'cap': cap, 'previous_cap': previous},
            )
        return {'cap': cap, 'previous_cap': previous, 'changed': changed}

    def get_effective_workspace_daily_cap(self, workspace_id):
        """Return {cap, source} where source is 'explicit', 'default', or 'unset'.

        S2849 W2 #2a. Read-only view combining the explicit per-workspace
        cap with the global default fallback. Used by operator surfaces
        (get_status, list_caps with include_defaults=True) to make the
        distinction visible. Autopilot enforcement does NOT read this —
        the cycle only iterates workspaces with explicit caps set.
        """
        explicit = self.get_workspace_daily_cap(workspace_id)
        if explicit is not None:
            return {'cap': explicit, 'source': 'explicit'}
        default = self.get_workspace_default_cap()
        if default is not None:
            return {'cap': default, 'source': 'default'}
        return {'cap': None, 'source': 'unset'}

    def enforce_workspace_freeze(
        self, spend, now, workspace_id,
        actor_user_id=None, trigger='autopilot_cycle',
    ):
        """Freeze the given workspace when its daily spend crosses its cap.

        Freeze-tier only for W1 (per Rigby's D6 tweak — downgrade-tier
        deferred to W1.5). Idempotent: no-op if already frozen or no
        cap is set.

        S2850 #3.0a: when actor_user_id is passed, the AutopilotAction row
        is attributed to workspace_budget_tool (operator surface) instead
        of the autopilot cycle, and `trigger` is recorded in evidence.
        Threshold + idempotency logic UNCHANGED regardless of actor.
        """
        if workspace_id is None:
            return None  # null bucket has no per-workspace freeze
        cap = self.get_workspace_daily_cap(workspace_id)
        if cap is None:
            return None
        if spend['daily_total'] < cap:
            return None

        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_FREEZE_KEY_PREFIX}{workspace_id}"

        # Idempotent — don't re-fire on already-frozen workspace
        existing = (
            SystemConfiguration.objects
            .filter(key=key)
            .values_list('value', flat=True)
            .first()
        )
        if existing:
            return None

        SystemConfiguration.objects.update_or_create(
            key=key,
            defaults={
                'value': True,
                'description': (
                    f'WORKSPACE FREEZE: workspace_id={workspace_id} '
                    f'daily spend ${spend["daily_total"]:.2f} '
                    f'exceeds cap ${cap:.2f} (Session 2846 A1 W1)'
                ),
                'category': 'performance',
            },
        )

        operator_triggered = actor_user_id is not None
        evidence = {**spend, 'cap': cap, 'trigger': trigger}
        if operator_triggered:
            evidence['actor_user_id'] = str(actor_user_id)
        AutopilotAction.objects.create(
            action_type='workspace_budget_freeze',
            agent_name=(
                'workspace_budget_tool' if operator_triggered
                else 'BudgetController'
            ),
            policy=(
                'workspace_budget_tool' if operator_triggered
                else 'workspace_budget_controller'
            ),
            dry_run=False,
            evidence=evidence,
            result={
                'workspace_id': str(workspace_id),
                'daily_spend': round(spend['daily_total'], 4),
                'cap': cap,
            },
        )

        logger.warning(
            f"[BudgetController] WORKSPACE FREEZE activated — "
            f"workspace_id={workspace_id} daily spend "
            f"${spend['daily_total']:.2f} vs cap ${cap:.2f}"
        )

        return {
            'type': 'workspace_budget_freeze',
            'workspace_id': str(workspace_id),
            'daily_spend': round(spend['daily_total'], 4),
            'cap': cap,
        }

    def is_workspace_frozen(self, workspace_id) -> bool:
        """Hot-path check — is this workspace currently frozen?

        Called from llm_enforcer BEFORE firing the LLM call. Fold 4
        says no caching in W1; every call hits SystemConfiguration.
        """
        if workspace_id is None:
            return False
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_FREEZE_KEY_PREFIX}{workspace_id}"
        entry = (
            SystemConfiguration.objects
            .filter(key=key)
            .values_list('value', flat=True)
            .first()
        )
        return bool(entry)

    def clear_workspace_freeze(self, workspace_id, actor_user_id=None) -> bool:
        """Clear the freeze flag for a specific workspace. Returns True if
        a flag was actually cleared.

        actor_user_id (S2847 Phase 3): when passed from a manual PA-tool
        clear, an AutopilotAction row is written so that operator unlocks
        show up symmetrically with the auto-freeze logged by
        enforce_workspace_freeze. When None (autopilot path), no row is
        written from here — the caller is responsible for its own audit.
        """
        if workspace_id is None:
            return False
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_FREEZE_KEY_PREFIX}{workspace_id}"
        deleted, _ = SystemConfiguration.objects.filter(key=key).delete()
        if deleted:
            logger.info(
                "[BudgetController] Cleared workspace freeze for "
                "workspace_id=%s",
                workspace_id,
            )
            if actor_user_id is not None:
                AutopilotAction.objects.create(
                    action_type='workspace_freeze_cleared',
                    agent_name='workspace_budget_tool',
                    policy='workspace_budget_tool',
                    dry_run=False,
                    evidence={
                        'workspace_id': str(workspace_id),
                        'actor_user_id': str(actor_user_id),
                    },
                    result={'cleared': True},
                )
        return bool(deleted)

    # ─────────────────────────────────────────────────────────────────
    # S2848 A1 W1.5 — per-workspace soft downgrade tier.
    #
    # Mirrors freeze plumbing above but at BUDGET_SOFT_LIMIT_PCT (70%)
    # instead of the hard cap. On trigger, writes flag at
    # workspace_downgrade_active:<uuid>. llm_enforcer hot-path reads
    # is_workspace_downgraded and swaps to BUDGET_DOWNGRADE_MODEL
    # (gpt-5-mini) before the API call. Freeze wins over downgrade —
    # a frozen workspace never gets the model-swap.
    #
    # Hysteresis policy: set at 70% of cap, auto-clear at 60% (see
    # _WORKSPACE_DOWNGRADE_CLEAR_PCT). Prevents flap on small caps.
    # Manual clear via clear_workspace_downgrade (operator override).
    # ─────────────────────────────────────────────────────────────────

    def enforce_workspace_downgrade(
        self, spend, now, workspace_id,
        actor_user_id=None, trigger='autopilot_cycle',
    ):
        """Set/clear the downgrade flag based on the workspace's daily spend.

        Called from _policy_budget_controller cycle per-workspace. Idempotent
        with hysteresis: set at BUDGET_SOFT_LIMIT_PCT of cap, clear at
        _WORKSPACE_DOWNGRADE_CLEAR_PCT (60%). Returns action dict when
        state changes; None on no-op.

        S2850 #3.0a: when actor_user_id is passed (operator-triggered via
        set_cap), BOTH state transitions (set-on-cross-up and auto-clear-
        on-hysteresis) attribute the AutopilotAction row to
        workspace_budget_tool with actor_user_id + trigger in evidence.
        Per Rigby SIGN #4 Q2: any state transition caused by an operator-
        induced call is attributed to the operator regardless of branch.
        Threshold + hysteresis logic UNCHANGED regardless of actor.
        """
        if workspace_id is None:
            return None
        cap = self.get_workspace_daily_cap(workspace_id)
        if cap is None:
            return None

        set_threshold = cap * AutopilotConfig.BUDGET_SOFT_LIMIT_PCT
        clear_threshold = cap * self._WORKSPACE_DOWNGRADE_CLEAR_PCT
        currently_downgraded = self.is_workspace_downgraded(workspace_id)

        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_DOWNGRADE_KEY_PREFIX}{workspace_id}"

        operator_triggered = actor_user_id is not None

        # Auto-clear when spend drops below hysteresis floor
        if currently_downgraded and spend['daily_total'] < clear_threshold:
            SystemConfiguration.objects.filter(key=key).delete()
            evidence = {
                **spend, 'cap': cap, 'clear_threshold': clear_threshold,
                'trigger': trigger,
            }
            if operator_triggered:
                evidence['actor_user_id'] = str(actor_user_id)
            AutopilotAction.objects.create(
                action_type='workspace_downgrade_cleared',
                agent_name=(
                    'workspace_budget_tool' if operator_triggered
                    else 'BudgetController'
                ),
                policy=(
                    'workspace_budget_tool' if operator_triggered
                    else 'workspace_budget_controller'
                ),
                dry_run=False,
                evidence=evidence,
                result={
                    'workspace_id': str(workspace_id),
                    'reason': (
                        'operator_cap_change_hysteresis'
                        if operator_triggered else 'auto_hysteresis'
                    ),
                },
            )
            logger.info(
                f"[BudgetController] Workspace downgrade auto-cleared — "
                f"workspace_id={workspace_id} spend "
                f"${spend['daily_total']:.4f} < clear threshold "
                f"${clear_threshold:.4f} ({self._WORKSPACE_DOWNGRADE_CLEAR_PCT:.0%})"
            )
            return {
                'type': 'workspace_downgrade_cleared',
                'workspace_id': str(workspace_id),
                'daily_spend': round(spend['daily_total'], 4),
                'cap': cap,
            }

        # Set on cross-up (idempotent — no-op if already downgraded)
        if spend['daily_total'] >= set_threshold and not currently_downgraded:
            SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': True,
                    'description': (
                        f'WORKSPACE DOWNGRADE: workspace_id={workspace_id} '
                        f'daily spend ${spend["daily_total"]:.2f} '
                        f'>= ${set_threshold:.2f} '
                        f'({AutopilotConfig.BUDGET_SOFT_LIMIT_PCT:.0%} of cap ${cap:.2f}) '
                        f'(Session 2848 A1 W1.5)'
                    ),
                    'category': 'performance',
                },
            )
            set_evidence = {
                **spend, 'cap': cap, 'set_threshold': set_threshold,
                'trigger': trigger,
            }
            if operator_triggered:
                set_evidence['actor_user_id'] = str(actor_user_id)
            AutopilotAction.objects.create(
                action_type='workspace_downgrade_set',
                agent_name=(
                    'workspace_budget_tool' if operator_triggered
                    else 'BudgetController'
                ),
                policy=(
                    'workspace_budget_tool' if operator_triggered
                    else 'workspace_budget_controller'
                ),
                dry_run=False,
                evidence=set_evidence,
                result={
                    'workspace_id': str(workspace_id),
                    'daily_spend': round(spend['daily_total'], 4),
                    'downgrade_model': AutopilotConfig.BUDGET_DOWNGRADE_MODEL,
                },
            )
            logger.warning(
                f"[BudgetController] WORKSPACE DOWNGRADE activated — "
                f"workspace_id={workspace_id} spend "
                f"${spend['daily_total']:.2f} >= "
                f"${set_threshold:.2f} ({AutopilotConfig.BUDGET_SOFT_LIMIT_PCT:.0%} of cap)"
            )
            return {
                'type': 'workspace_downgrade_set',
                'workspace_id': str(workspace_id),
                'daily_spend': round(spend['daily_total'], 4),
                'cap': cap,
                'downgrade_model': AutopilotConfig.BUDGET_DOWNGRADE_MODEL,
            }

        return None

    def is_workspace_downgraded(self, workspace_id) -> bool:
        """Hot-path check — is this workspace currently in downgrade tier?

        Called from llm_enforcer BEFORE the LLM call to decide whether to
        swap to BUDGET_DOWNGRADE_MODEL. No caching (matches Phase 2 Fold 4).
        """
        if workspace_id is None:
            return False
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_DOWNGRADE_KEY_PREFIX}{workspace_id}"
        entry = (
            SystemConfiguration.objects
            .filter(key=key)
            .values_list('value', flat=True)
            .first()
        )
        return bool(entry)

    def clear_workspace_downgrade(self, workspace_id, actor_user_id=None) -> bool:
        """Clear the downgrade flag for a specific workspace.

        Symmetric with clear_workspace_freeze. actor_user_id (S2848 Phase 3
        pattern) writes an AutopilotAction row when passed from a manual
        PA-tool clear so operator overrides are as auditable as auto-hysteresis.
        """
        if workspace_id is None:
            return False
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_DOWNGRADE_KEY_PREFIX}{workspace_id}"
        deleted, _ = SystemConfiguration.objects.filter(key=key).delete()
        if deleted:
            logger.info(
                "[BudgetController] Cleared workspace downgrade for "
                "workspace_id=%s (actor=%s)",
                workspace_id, actor_user_id,
            )
            if actor_user_id is not None:
                AutopilotAction.objects.create(
                    action_type='workspace_downgrade_cleared',
                    agent_name='workspace_budget_tool',
                    policy='workspace_budget_tool',
                    dry_run=False,
                    evidence={
                        'workspace_id': str(workspace_id),
                        'actor_user_id': str(actor_user_id),
                        'reason': 'manual_operator_clear',
                    },
                    result={'cleared': True},
                )
        return bool(deleted)

    def set_workspace_daily_cap(
        self, workspace_id, daily_cap_usd, actor_user_id=None,
    ) -> dict:
        """Write the per-workspace daily cap ($ USD) to SystemConfiguration.

        S2847 Phase 3 — symmetric with get_workspace_daily_cap. When
        actor_user_id is passed, records an AutopilotAction so operator
        cap changes are as auditable as auto-freezes.

        Idempotent: repeat set_cap with the same value is a no-op with
        `changed=False`. Returns {workspace_id, cap, previous_cap, changed}.
        """
        if workspace_id is None:
            raise ValueError("workspace_id is required")
        try:
            cap = float(daily_cap_usd)
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"daily_cap_usd must be numeric, got {daily_cap_usd!r}"
            ) from e
        if cap <= 0:
            raise ValueError(
                f"daily_cap_usd must be > 0, got {cap}"
            )
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_CAP_KEY_PREFIX}{workspace_id}"
        previous = self.get_workspace_daily_cap(workspace_id)
        SystemConfiguration.objects.update_or_create(
            key=key,
            defaults={
                'value': cap,
                'description': (
                    f'Per-workspace daily cap ($ USD) — workspace_id='
                    f'{workspace_id}. Enforced by BudgetController.'
                    f'enforce_workspace_freeze against last-24h spend.'
                ),
                'category': 'performance',
            },
        )
        changed = previous != cap
        logger.info(
            "[BudgetController] Set workspace daily cap — workspace_id=%s "
            "cap=$%.2f (previous=%s, changed=%s)",
            workspace_id, cap, previous, changed,
        )
        if actor_user_id is not None and changed:
            AutopilotAction.objects.create(
                action_type='workspace_cap_set',
                agent_name='workspace_budget_tool',
                policy='workspace_budget_tool',
                dry_run=False,
                evidence={
                    'workspace_id': str(workspace_id),
                    'actor_user_id': str(actor_user_id),
                    'previous_cap': previous,
                },
                result={'cap': cap, 'previous_cap': previous},
            )
        return {
            'workspace_id': str(workspace_id),
            'cap': cap,
            'previous_cap': previous,
            'changed': changed,
        }

    def clear_workspace_daily_cap(
        self, workspace_id, actor_user_id=None,
    ) -> bool:
        """Delete the per-workspace daily cap. Returns True if a cap row
        was actually deleted.

        S2847 Phase 3 — symmetric undo for set_workspace_daily_cap.
        Deleting the cap does NOT clear an existing freeze; callers who
        want both should call clear_workspace_freeze separately (keeps
        the two operations independently auditable).
        """
        if workspace_id is None:
            return False
        from core.models.system import SystemConfiguration
        key = f"{self._WORKSPACE_CAP_KEY_PREFIX}{workspace_id}"
        deleted, _ = SystemConfiguration.objects.filter(key=key).delete()
        if deleted:
            logger.info(
                "[BudgetController] Cleared workspace daily cap — "
                "workspace_id=%s",
                workspace_id,
            )
            if actor_user_id is not None:
                AutopilotAction.objects.create(
                    action_type='workspace_cap_cleared',
                    agent_name='workspace_budget_tool',
                    policy='workspace_budget_tool',
                    dry_run=False,
                    evidence={
                        'workspace_id': str(workspace_id),
                        'actor_user_id': str(actor_user_id),
                    },
                    result={'cleared': True},
                )
        return bool(deleted)

    def list_workspace_caps(self) -> list:
        """Return every workspace with a configured cap.

        S2847 Phase 3 — inventory for workspace_budget_tool.list_caps.
        Returns [{workspace_id, cap}] rows straight from SystemConfiguration.
        The handler is responsible for joining ProjectWorkspace.name +
        current spend + freeze status for operator visibility.
        """
        from core.models.system import SystemConfiguration
        rows = SystemConfiguration.objects.filter(
            key__startswith=self._WORKSPACE_CAP_KEY_PREFIX,
        ).values_list('key', 'value')
        out = []
        for key, value in rows:
            workspace_id = key[len(self._WORKSPACE_CAP_KEY_PREFIX):]
            try:
                cap = float(value)
            except (TypeError, ValueError):
                logger.warning(
                    "[BudgetController] list_workspace_caps: skipping "
                    "workspace_id=%s — value=%r not a valid float",
                    workspace_id, value,
                )
                continue
            out.append({'workspace_id': workspace_id, 'cap': cap})
        return out

    def backfill_workspace_defaults(
        self,
        default_cap=None,
        include_workspace_ids=None,
        exclude_workspace_ids=None,
        force=False,
        dry_run=True,
        actor_user_id=None,
    ) -> dict:
        """Write the default cap to workspaces missing an explicit cap.

        S2849 W2 #2a. Autopilot enforcement iterates only workspaces with
        explicit workspace_daily_cap:<uuid> rows (see _policy_budget_
        controller in core.py). Lazy defaults alone do not bring
        unconfigured workspaces under enforcement; this method makes the
        default explicit for the current 16-workspace population.

        Args:
            default_cap: cap value ($ USD) to write. When None, reads
                get_workspace_default_cap(). Raises ValueError if both
                are unset.
            include_workspace_ids: iterable of workspace UUIDs to touch.
                When None, considers all ProjectWorkspace rows.
            exclude_workspace_ids: iterable of workspace UUIDs to skip.
                Applied after include filter.
            force: when False (default), skip workspaces that already
                have an explicit cap. When True, overwrite them with
                default_cap.
            dry_run: when True (default), plan only — no writes. Return
                shape includes 'planned' list.
            actor_user_id: staff/owner id for audit. Passed through to
                set_workspace_daily_cap so per-workspace writes emit
                workspace_cap_set actions with the actor.

        Returns:
            dict with counts + per-workspace details:
              {
                'dry_run': bool,
                'default_cap': float,
                'total_workspaces': int,
                'planned': int,        # would-write count
                'wrote': int,          # actual writes (0 when dry_run)
                'skipped_existing': int,
                'skipped_excluded': int,
                'skipped_not_included': int,
                'errors': int,
                'details': [{workspace_id, workspace_name, action,
                             previous_cap, new_cap, error?}],
              }
        """
        from core.models_skin_layer import ProjectWorkspace

        if default_cap is None:
            default_cap = self.get_workspace_default_cap()
        if default_cap is None:
            raise ValueError(
                "backfill_workspace_defaults: no default_cap passed and "
                "workspace_default_daily_cap is unset — set the global "
                "default first or pass default_cap explicitly"
            )
        try:
            default_cap = float(default_cap)
        except (TypeError, ValueError):
            raise ValueError(
                f"default_cap must be a float, got {default_cap!r}"
            )
        if default_cap <= 0:
            raise ValueError(
                f"default_cap must be > 0, got {default_cap}"
            )

        # Empty list from OpenAI function-calling (models often pass [] for
        # optional array params rather than omitting) is treated as "no
        # filter" — the alternative (empty-set = match-none) blocks every
        # workspace and produces zero writes, which is never what the
        # operator wants when they didn't specify an allowlist.
        include_set = (
            {str(w) for w in include_workspace_ids}
            if include_workspace_ids else None
        )
        exclude_set = (
            {str(w) for w in exclude_workspace_ids}
            if exclude_workspace_ids else set()
        )

        result = {
            'dry_run': bool(dry_run),
            'default_cap': default_cap,
            'total_workspaces': 0,
            'planned': 0,
            'wrote': 0,
            'skipped_existing': 0,
            'skipped_excluded': 0,
            'skipped_not_included': 0,
            'errors': 0,
            'details': [],
        }

        for ws in ProjectWorkspace.objects.all().only('id', 'name'):
            result['total_workspaces'] += 1
            wid = str(ws.id)

            if include_set is not None and wid not in include_set:
                result['skipped_not_included'] += 1
                continue
            if wid in exclude_set:
                result['skipped_excluded'] += 1
                result['details'].append({
                    'workspace_id': wid,
                    'workspace_name': ws.name,
                    'action': 'skipped_excluded',
                })
                continue

            existing = self.get_workspace_daily_cap(ws.id)
            if existing is not None and not force:
                result['skipped_existing'] += 1
                result['details'].append({
                    'workspace_id': wid,
                    'workspace_name': ws.name,
                    'action': 'skipped_existing',
                    'previous_cap': existing,
                })
                continue

            result['planned'] += 1
            if dry_run:
                result['details'].append({
                    'workspace_id': wid,
                    'workspace_name': ws.name,
                    'action': 'would_write',
                    'previous_cap': existing,
                    'new_cap': default_cap,
                })
                continue

            try:
                write_result = self.set_workspace_daily_cap(
                    ws.id, default_cap, actor_user_id=actor_user_id,
                )
                result['wrote'] += 1
                result['details'].append({
                    'workspace_id': wid,
                    'workspace_name': ws.name,
                    'action': 'wrote',
                    'previous_cap': write_result['previous_cap'],
                    'new_cap': write_result['cap'],
                    'changed': write_result['changed'],
                })
            except Exception as e:
                result['errors'] += 1
                result['details'].append({
                    'workspace_id': wid,
                    'workspace_name': ws.name,
                    'action': 'error',
                    'error': f'{type(e).__name__}: {e}',
                })
                logger.error(
                    "[BudgetController] backfill_workspace_defaults error "
                    "for workspace_id=%s: %s", wid, e,
                )

        logger.info(
            "[BudgetController] backfill_workspace_defaults complete: "
            "dry_run=%s, planned=%d, wrote=%d, skipped_existing=%d, "
            "skipped_excluded=%d, errors=%d",
            dry_run, result['planned'], result['wrote'],
            result['skipped_existing'], result['skipped_excluded'],
            result['errors'],
        )
        return result

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

        # Current mode.
        # Session 1103c: was 'except Exception: pass' which silently
        # left mode='normal' (no constraints) when SystemConfiguration
        # lookup failed. That's fail-OPEN on budget enforcement —
        # exactly when the DB/config layer is unhealthy, the system
        # should fail-CLOSED to 'freeze' (assume constrained) rather
        # than fail-open to 'normal' (assume unconstrained), to
        # prevent runaway LLM spend during incidents. Now logs ERROR
        # and flips to 'freeze' as the safe default.
        from core.models.system import SystemConfiguration
        mode = 'normal'
        try:
            mode_entry = SystemConfiguration.objects.filter(
                key='budget_mode',
            ).values_list('value', flat=True).first()
            if mode_entry:
                mode = mode_entry
        except Exception as _e:
            logger.error(
                "ops_autopilot.budget: SystemConfiguration lookup for "
                "'budget_mode' failed (%s: %s) — failing CLOSED to "
                "'freeze' to prevent runaway spend during incidents",
                type(_e).__name__, _e,
            )
            mode = 'freeze'

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
        'pa_chat', 'personalassistant', 'unifiedpa',
        'governance', 'auth', 'incident_response',
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

        # Session 1083 (Rigby audit): compute_roi_scores used to bare-
        # except every outcome/quality source and silently drop the
        # missing data. When 2-3 sources were degraded simultaneously,
        # every agent's ROI looked artificially low and the enforcer
        # would issue throttle recommendations against perfectly healthy
        # agents. Track degraded sources so callers can detect partial
        # telemetry and skip throttle actions.
        outcome_sources_degraded: list[str] = []

        # Outcome counts by agent: completed AgentExecutions
        agent_names = [a['agent_name'] for a in agent_spend]
        outcome_map = {}

        try:
            from core.models_unified_system import AgentExecution
            # Arc I-0100 P4 §4.2 F1 fold (PR-B1 §3.1 #6 ratified):
            # explicit PA exclude. The agent__name__in allowlist above
            # already prevents PA from naturally appearing in the
            # aggregate (agent_names comes from the agent_spend list,
            # which does not include PA). The explicit .exclude() here
            # is defensive + documents the semantic intent: this
            # aggregation attributes router-agent ROI outcomes only.
            # If a future caller passes 'PersonalAssistant' in
            # agent_names, this exclude keeps ROI attribution correct.
            # Use agent__name form per ADR-0002 F1 fold equivalent
            # (Postgres JSONField NULL-semantics make the
            # input_data__source='pa' form unsafe for pre-flag-flip rows).
            outcomes = list(
                AgentExecution.objects.filter(
                    created_at__gte=window_start,
                    status='completed',
                    agent__name__in=agent_names,
                ).exclude(agent__name='PersonalAssistant').values(
                    'agent__name'
                ).annotate(
                    completed=Count('id'),
                )
            )
            for o in outcomes:
                outcome_map[o['agent__name']] = o['completed']
        except Exception as e:
            outcome_sources_degraded.append('agent_executions')
            logger.warning(
                "compute_roi_scores: AgentExecution outcomes failed "
                "(%s: %s) — per-agent completion counts will be zero",
                type(e).__name__, e,
            )

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
        except Exception as e:
            outcome_sources_degraded.append('deliverables')
            logger.warning(
                "compute_roi_scores: Deliverable outcomes failed "
                "(%s: %s) — published content counts will be zero",
                type(e).__name__, e,
            )

        # Session 1098: ImpactEvent outcomes — captures PA tool completions
        # and other impact-tracked events (wager profit, revenue, content actions)
        impact_map = {}
        try:
            from core.models_impact_events import ImpactEvent
            impact_outcomes = list(
                ImpactEvent.objects.filter(
                    created_at__gte=window_start,
                    agent_name__in=agent_names,
                ).values('agent_name').annotate(
                    impacts=Count('id'),
                )
            )
            for ie in impact_outcomes:
                if ie['agent_name']:
                    impact_map[ie['agent_name']] = ie['impacts']
        except Exception as e:
            outcome_sources_degraded.append('impact_events')
            logger.warning(
                "compute_roi_scores: ImpactEvent outcomes failed "
                "(%s: %s) — PA tool / revenue attribution will be zero",
                type(e).__name__, e,
            )

        # Deliberation outcomes: passed sessions.
        # Session 1083 (Rigby audit): this used to `.values('topic')`
        # but the DeliberationSession model's field is `objective`, not
        # `topic` — had been throwing FieldError silently on every
        # compute_roi_scores call since the schema rename. The bare-pass
        # swallowed it, so the enforcer had been missing deliberation
        # outcomes entirely. Simplified to a plain count since the
        # group-by was vestigial (result was summed immediately).
        delib_map = {}
        try:
            from core.models_deliberation import DeliberationSession
            delib_map['_total'] = DeliberationSession.objects.filter(
                created_at__gte=window_start,
                status='completed',
            ).count()
        except Exception as e:
            outcome_sources_degraded.append('deliberation_outcomes')
            logger.warning(
                "compute_roi_scores: DeliberationSession outcomes failed "
                "(%s: %s)", type(e).__name__, e,
            )

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
        except Exception as e:
            outcome_sources_degraded.append('selfblog_quality')
            logger.warning(
                "compute_roi_scores: SelfBlog quality_score query failed "
                "(%s: %s) — content quality signals will be empty",
                type(e).__name__, e,
            )

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
        except Exception as e:
            outcome_sources_degraded.append('deliverable_quality')
            logger.warning(
                "compute_roi_scores: Deliverable quality aggregation "
                "failed (%s: %s)", type(e).__name__, e,
            )

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
        except Exception as e:
            outcome_sources_degraded.append('delib_pass_rate')
            logger.warning(
                "compute_roi_scores: DeliberationSession pass-rate query "
                "failed (%s: %s) — falling back to 0.5 default",
                type(e).__name__, e,
            )

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
            impacts = impact_map.get(name, 0)
            combined_outcomes = outcomes + content + impacts
            total_outcomes += combined_outcomes

            # ROI = outcome-to-call ratio (0..1+)
            roi = combined_outcomes / max(calls, 1)

            # QROI = ROI * quality_weight
            # quality_weight combines:
            # - deliverable quality score (if available)
            # - content pipeline quality (if this agent produces content)
            # - impact event history (PA tool completions, wager profits, etc.)
            # - execution success rate as fallback
            quality_weight = 0.5  # neutral default
            if name in deliverable_quality:
                quality_weight = deliverable_quality[name]
            elif content > 0:
                # Content-producing agent — use pipeline quality
                quality_weight = quality_map.get('_content_avg', 0.5)
            elif impacts > 0:
                # Impact-tracked agent (e.g. PA) — quality = impact rate
                quality_weight = min(impacts / max(calls, 1), 1.0)
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
                    'impacts': impacts,
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
            'outcome_sources_degraded': outcome_sources_degraded,
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

        # Session 1083 (Rigby audit): if any outcome/quality source is
        # degraded, our per-agent ROI is unreliable — throttling agents
        # based on partial telemetry is worse than doing nothing. Fail
        # closed by returning no recommendations.
        degraded = roi_data.get('outcome_sources_degraded') or []
        if degraded:
            logger.warning(
                "get_throttle_recommendations: skipping throttle decisions "
                "because ROI telemetry is degraded (sources=%s). No "
                "recommendations will be returned until next healthy cycle.",
                degraded,
            )
            return []

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
                key=key, is_active=True,
            ).values_list('value', flat=True).first()

            if not entry:
                return None

            expires_at = entry.get('expires_at', '')
            if expires_at and tz.now().isoformat() > expires_at:
                # Expired — clean up
                SystemConfiguration.objects.filter(key=key).delete()
                return None

            return entry
        except Exception as _e:
            logger.warning(
                "budget.check_throttle: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
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
            except Exception as e:
                # Session 1083: was bare pass — runtime override lookup
                # failure silently dropped operator-configured values in
                # favor of hardcoded defaults. Log so Chris can see when
                # scheduler knob overrides are being ignored.
                logger.warning(
                    "_get_knobs: override lookup for %s failed (%s: %s) — "
                    "falling back to static default",
                    override_key, type(e).__name__, e,
                )

            # Use static default for the level
            result[param] = levels.get(level, levels.get('normal'))

        return result

    def _log_decision(self, task_name: str, decision: str, budget_pct: float):
        """Log scheduling decision for audit trail.

        Session 1083: was `except Exception: pass` which silently dropped
        every scheduler decision from the audit trail when AutopilotAction
        writes failed. The decision itself still got applied downstream,
        so Chris would see agents getting throttled / deferred with zero
        audit trail — permanently unanalyzable in post-incident review.
        Now logs ERROR so the failure surfaces loudly.
        """
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
        except Exception as e:
            logger.error(
                "_log_decision: failed to write AutopilotAction audit "
                "row for task=%s decision=%s budget_pct=%.3f (%s: %s) — "
                "audit trail will be missing this decision",
                task_name, decision, budget_pct, type(e).__name__, e,
            )

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
        except Exception as e:
            logger.warning(
                "get_scheduler_report: recent decisions query failed "
                "(%s: %s) — defers_24h / downscopes_24h will report 0",
                type(e).__name__, e,
            )
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
        except Exception as exc:
            logger.warning(
                "get_scheduler_report: active knob overrides query failed "
                "(%s: %s) — report will show empty overrides map",
                type(exc).__name__, exc,
            )

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


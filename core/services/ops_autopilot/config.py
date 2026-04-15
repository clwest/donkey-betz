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
from typing import Any

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
    BUDGET_DAILY_CAP_USD = 100.0          # Global daily spend cap
    BUDGET_HOURLY_CAP_USD = 5.0           # Session 1098: raised from 3.0 — was triggering at 108%
    BUDGET_SOFT_LIMIT_PCT = 0.7           # Trigger downgrade at 70% of cap
    BUDGET_HARD_LIMIT_PCT = 0.95          # Hard freeze at 95% of cap
    BUDGET_CHECK_INTERVAL_MINUTES = 10    # Check spend every N minutes
    BUDGET_DOWNGRADE_MODEL = 'gpt-5-mini' # Cheap model for downgrade
    BUDGET_CRITICAL_PURPOSES = {          # Never freeze these
        'governance', 'auth', 'incident_response', 'pa_chat',
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
    _override_load_failed = False
    _override_cache: dict[str, Any] = {}

    @classmethod
    def load_overrides(cls):
        """Load tuned parameter overrides from SystemConfiguration.

        Session 1083 (Rigby audit): previously this bare-excepted every
        exception and flipped ``_overrides_loaded = True`` so the autopilot
        would silently run on hardcoded defaults for the rest of the
        process lifetime if the ``system_configuration`` table was
        unreachable at cache-build time. Now we log loudly and set
        ``_override_load_failed`` so downstream code (and observability)
        can see when the autopilot is running config-blind.
        """
        import logging
        logger = logging.getLogger(__name__)
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
            cls._override_load_failed = False
        except Exception as e:
            cls._overrides_loaded = True
            cls._override_load_failed = True
            logger.warning(
                "autopilot config overrides failed to load — running on "
                "hardcoded defaults. Operator tuning will be ignored until "
                "the next successful reload. error=%s: %s",
                type(e).__name__,
                e,
            )

    @classmethod
    def get(cls, param_name: str):
        """Get a config value, checking overrides first.

        Session 1098: Coerce override values to match the type of the class
        default.  SystemConfiguration.value is JSONField — JSON stores all
        numbers as floats, but Django may deserialize them as strings when
        the value was saved via admin or raw SQL.  Without coercion,
        ``max(daily_cap, 0.01)`` explodes with ``'>' not supported between
        instances of 'float' and 'str'``.
        """
        if not cls._overrides_loaded:
            cls.load_overrides()
        # Override value takes precedence
        if param_name in cls._override_cache:
            raw = cls._override_cache[param_name]
            # Coerce to match type of the class-level default
            default = getattr(cls, param_name, None)
            if default is not None and raw is not None:
                try:
                    # bool before int — bool is subclass of int in Python
                    if isinstance(default, bool) and not isinstance(raw, bool):
                        if isinstance(raw, str):
                            return raw.lower() in ('true', '1', 'yes')
                        return bool(raw)
                    if isinstance(default, float) and not isinstance(raw, float):
                        return float(raw)
                    if isinstance(default, int) and not isinstance(raw, (int, bool)):
                        return int(float(raw))  # handles "100.0" → 100
                except (ValueError, TypeError):
                    pass  # Fall through to raw value
            return raw
        return getattr(cls, param_name, None)

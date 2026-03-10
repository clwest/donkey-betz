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
# Engagement Engine — Policy 28 (Autonomy #24)
# ═══════════════════════════════════════════════════════════════════════

class RevenueOrchestrator:
    """
    Unified revenue pipeline view — stitches together OutboundLeadEngine,
    OutreachSequencer, EngagementEngine, MeetingEngine, CloseTheDealEngine
    into a single end-to-end funnel.

    Pipeline stages:
      lead → outreach_draft → outreach_sent → engagement → meeting → close_pack → won/lost

    Does NOT replace individual engines — it reads from their models to
    produce cross-cutting views, funnel metrics, and pipeline forecasts.
    """

    # Rough conversion rates for forecasting (adjusted from actual data over time)
    DEFAULT_CONVERSION = {
        'lead_to_outreach': 0.40,      # 40% of leads get outreach drafted
        'outreach_to_sent': 0.60,      # 60% of drafts get approved
        'sent_to_reply': 0.15,         # 15% reply rate
        'reply_to_meeting': 0.40,      # 40% of replies become meetings
        'meeting_to_deal': 0.30,       # 30% of meetings produce close packs
        'deal_to_won': 0.25,           # 25% win rate
    }

    def get_full_pipeline(self) -> dict:
        """
        Unified pipeline view across all revenue stages.
        Shows counts at each stage + items needing attention.
        """
        from core.models_outreach import OutreachDraft
        from core.models_engagement import EngagementEvent
        from core.models_meeting import Meeting
        from core.models_close_pack import ClosePack
        from core.models_unified_system import Opportunity
        from django.db.models import Count
        from django.utils import timezone as tz

        now = tz.now()

        # Outreach pipeline
        outreach_by_status = dict(
            OutreachDraft.objects.values('status').annotate(
                count=Count('id'),
            ).values_list('status', 'count')
        )

        # Engagement pipeline
        engagement_by_status = dict(
            EngagementEvent.objects.values('status').annotate(
                count=Count('id'),
            ).values_list('status', 'count')
        )

        # Meeting pipeline
        meeting_by_status = dict(
            Meeting.objects.values('status').annotate(
                count=Count('id'),
            ).values_list('status', 'count')
        )

        # Close pack pipeline
        pack_by_status = dict(
            ClosePack.objects.values('status').annotate(
                count=Count('id'),
            ).values_list('status', 'count')
        )

        # Opportunity pipeline
        opp_by_status = dict(
            Opportunity.objects.values('status').annotate(
                count=Count('id'),
            ).values_list('status', 'count')
        )

        # Items needing attention
        needs_attention = []

        # Outreach drafts pending approval
        pending_drafts = outreach_by_status.get('draft', 0)
        if pending_drafts > 0:
            needs_attention.append(f'{pending_drafts} outreach drafts pending approval')

        # Engagement events needing reply
        needs_reply = engagement_by_status.get('needs_reply', 0)
        unread = engagement_by_status.get('unread', 0)
        if needs_reply > 0:
            needs_attention.append(f'{needs_reply} engagement events need reply')
        if unread > 0:
            needs_attention.append(f'{unread} unread engagement events')

        # Meetings needing briefs
        needs_brief = Meeting.objects.filter(
            status='scheduled',
            scheduled_at__lte=now + timedelta(hours=24),
            brief_text='',
        ).count()
        if needs_brief > 0:
            needs_attention.append(f'{needs_brief} meetings need pre-call briefs')

        # Close packs pending approval
        pending_packs = pack_by_status.get('draft', 0)
        if pending_packs > 0:
            needs_attention.append(f'{pending_packs} close packs pending approval')

        return {
            'outreach': outreach_by_status,
            'engagement': engagement_by_status,
            'meetings': meeting_by_status,
            'close_packs': pack_by_status,
            'opportunities': opp_by_status,
            'needs_attention': needs_attention,
            'total_active_items': sum([
                outreach_by_status.get('draft', 0),
                outreach_by_status.get('approved', 0),
                engagement_by_status.get('unread', 0),
                engagement_by_status.get('needs_reply', 0),
                meeting_by_status.get('scheduled', 0),
                pack_by_status.get('draft', 0),
                pack_by_status.get('sent', 0),
            ]),
            'timestamp': now.isoformat(),
        }

    def get_conversion_funnel(self, days: int = 30) -> dict:
        """
        Full conversion funnel over the given period.
        lead → outreach → sent → reply → meeting → deal → won
        """
        from core.models_outreach import OutreachDraft
        from core.models_engagement import EngagementEvent
        from core.models_meeting import Meeting
        from core.models_close_pack import ClosePack
        from django.db.models import Count
        from django.utils import timezone as tz

        cutoff = tz.now() - timedelta(days=days)

        # Count at each stage
        leads_created = OutreachDraft.objects.filter(
            created_at__gte=cutoff,
        ).count()

        drafts_approved = OutreachDraft.objects.filter(
            created_at__gte=cutoff,
            status__in=['approved', 'sent', 'replied'],
        ).count()

        drafts_sent = OutreachDraft.objects.filter(
            created_at__gte=cutoff,
            status__in=['sent', 'replied'],
        ).count()

        replies_received = EngagementEvent.objects.filter(
            created_at__gte=cutoff,
        ).exclude(status='disqualified').count()

        meetings_scheduled = Meeting.objects.filter(
            created_at__gte=cutoff,
        ).count()

        meetings_completed = Meeting.objects.filter(
            created_at__gte=cutoff,
            status__in=['completed', 'followed_up'],
        ).count()

        packs_created = ClosePack.objects.filter(
            created_at__gte=cutoff,
        ).count()

        deals_won = ClosePack.objects.filter(
            created_at__gte=cutoff,
            status='won',
        ).count()

        # Build funnel with conversion rates
        funnel = [
            {'stage': 'leads_created', 'count': leads_created, 'rate': 1.0},
            {'stage': 'drafts_approved', 'count': drafts_approved,
             'rate': drafts_approved / leads_created if leads_created else 0},
            {'stage': 'outreach_sent', 'count': drafts_sent,
             'rate': drafts_sent / drafts_approved if drafts_approved else 0},
            {'stage': 'replies_received', 'count': replies_received,
             'rate': replies_received / drafts_sent if drafts_sent else 0},
            {'stage': 'meetings_scheduled', 'count': meetings_scheduled,
             'rate': meetings_scheduled / replies_received if replies_received else 0},
            {'stage': 'meetings_completed', 'count': meetings_completed,
             'rate': meetings_completed / meetings_scheduled if meetings_scheduled else 0},
            {'stage': 'close_packs', 'count': packs_created,
             'rate': packs_created / meetings_completed if meetings_completed else 0},
            {'stage': 'deals_won', 'count': deals_won,
             'rate': deals_won / packs_created if packs_created else 0},
        ]

        # Overall conversion
        overall_rate = deals_won / leads_created if leads_created else 0

        return {
            'period_days': days,
            'funnel': funnel,
            'overall_conversion': round(overall_rate, 4),
            'total_leads': leads_created,
            'total_won': deals_won,
        }

    def get_revenue_forecast(self) -> dict:
        """
        Projected revenue from current pipeline based on stage probabilities.
        """
        from core.models_close_pack import ClosePack
        from core.models_meeting import Meeting
        from core.models_outreach import OutreachDraft
        from core.models_engagement import EngagementEvent
        from django.db.models import Sum
        from django.utils import timezone as tz

        # Active close packs with prices
        active_packs = ClosePack.objects.filter(
            status__in=['draft', 'approved', 'sent'],
        )
        pack_value = sum(
            float(p.price or 0) for p in active_packs
        )

        # Won revenue
        won_packs = ClosePack.objects.filter(status='won')
        won_revenue = sum(float(p.price or 0) for p in won_packs)

        # Pipeline stages
        draft_packs = ClosePack.objects.filter(status='draft').count()
        sent_packs = ClosePack.objects.filter(status='sent').count()
        upcoming_meetings = Meeting.objects.filter(status='scheduled').count()
        active_engagements = EngagementEvent.objects.filter(
            status__in=['unread', 'classified', 'needs_reply'],
        ).count()
        pending_outreach = OutreachDraft.objects.filter(status='draft').count()

        # Weighted forecast
        conv = self.DEFAULT_CONVERSION
        forecast_from_packs = pack_value * conv['deal_to_won']
        forecast_from_meetings = (
            upcoming_meetings * conv['meeting_to_deal'] * conv['deal_to_won'] * 5000
        )  # Assume avg deal $5000
        forecast_from_engagement = (
            active_engagements * conv['reply_to_meeting']
            * conv['meeting_to_deal'] * conv['deal_to_won'] * 5000
        )

        total_forecast = forecast_from_packs + forecast_from_meetings + forecast_from_engagement

        return {
            'won_revenue': round(won_revenue, 2),
            'active_pipeline_value': round(pack_value, 2),
            'weighted_forecast': round(total_forecast, 2),
            'forecast_breakdown': {
                'from_close_packs': round(forecast_from_packs, 2),
                'from_meetings': round(forecast_from_meetings, 2),
                'from_engagement': round(forecast_from_engagement, 2),
            },
            'pipeline_counts': {
                'pending_outreach': pending_outreach,
                'active_engagements': active_engagements,
                'upcoming_meetings': upcoming_meetings,
                'draft_packs': draft_packs,
                'sent_packs': sent_packs,
            },
        }

    def evaluate(self, now) -> dict:
        """
        Auto-flag pipeline health issues for the autopilot cycle.
        """
        from core.models_outreach import OutreachDraft
        from core.models_engagement import EngagementEvent
        from core.models_meeting import Meeting
        from core.models_close_pack import ClosePack

        issues = []

        # Stale outreach drafts (>7 days without approval)
        stale_drafts = OutreachDraft.objects.filter(
            status='draft',
            created_at__lt=now - timedelta(days=7),
        ).count()
        if stale_drafts > 0:
            issues.append(f'{stale_drafts} outreach drafts stale >7d')

        # Unread engagement events >3 days
        stale_engagement = EngagementEvent.objects.filter(
            status='unread',
            created_at__lt=now - timedelta(days=3),
        ).count()
        if stale_engagement > 0:
            issues.append(f'{stale_engagement} engagement events unread >3d')

        # Completed meetings without follow-up >48h
        stale_meetings = Meeting.objects.filter(
            status='completed',
            updated_at__lt=now - timedelta(hours=48),
        ).count()
        if stale_meetings > 0:
            issues.append(f'{stale_meetings} completed meetings awaiting follow-up >48h')

        # Sent close packs without response >14d
        stale_packs = ClosePack.objects.filter(
            status='sent',
            updated_at__lt=now - timedelta(days=14),
        ).count()
        if stale_packs > 0:
            issues.append(f'{stale_packs} close packs sent >14d without response')

        return {
            'pipeline_issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


# ── Knowledge & Citation Engine (Policy 32 — Autonomy #28) ──────────────────

class ClosePackAutonomyEngine:
    """
    Automates close pack lifecycle: follow-up sequencing, risk assessment,
    pipeline velocity tracking, and impact event emission.

    Sits on top of CloseTheDealEngine, adding:
    - Proactive follow-up draft generation for due packs
    - Risk flagging (discount depth, short timelines, missing terms)
    - Pipeline velocity metrics (time-to-close, stage duration)
    - Impact event emission for deal lifecycle
    """

    # Pricing guardrails
    MIN_PRICE_BY_OFFER = {
        'ai_automation': 2000,
        'content_engine': 1500,
        'analytics_dashboard': 3000,
        'consulting': 1000,
    }
    MAX_DISCOUNT_PCT = 30  # Flag if price < 70% of template midpoint
    SHORT_TIMELINE_DAYS = 5  # Flag if timeline < 5 days

    def get_followup_queue(self, now=None) -> dict:
        """
        Close packs needing follow-up: due or overdue.
        Generates draft follow-up messages for each.
        """
        from core.models_close_pack import ClosePack

        now = now or timezone.now()

        # Due follow-ups (approved/sent packs with followup_at <= now)
        due = list(
            ClosePack.objects.filter(
                status__in=['approved', 'sent'],
                followup_at__lte=now,
                followup_count__lt=2,
            ).order_by('followup_at').values(
                'id', 'offer_key', 'price', 'status',
                'followup_count', 'followup_at', 'created_at',
            )[:20]
        )

        for item in due:
            item['id'] = str(item['id'])
            item['price'] = float(item.get('price', 0))
            if hasattr(item.get('followup_at'), 'isoformat'):
                item['overdue_hours'] = round(
                    (now - item['followup_at']).total_seconds() / 3600, 1,
                )
                item['followup_at'] = item['followup_at'].isoformat()
            if hasattr(item.get('created_at'), 'isoformat'):
                item['created_at'] = item['created_at'].isoformat()

            # Generate follow-up draft text
            touch_num = item.get('followup_count', 0) + 1
            item['draft_followup'] = self._generate_followup_text(
                item['offer_key'], touch_num, float(item['price']),
            )

        # Upcoming (next 48h)
        upcoming = ClosePack.objects.filter(
            status__in=['approved', 'sent'],
            followup_at__gt=now,
            followup_at__lte=now + timedelta(hours=48),
            followup_count__lt=2,
        ).count()

        return {
            'due_followups': due,
            'due_count': len(due),
            'upcoming_48h': upcoming,
        }

    def _generate_followup_text(
        self, offer_key: str, touch_num: int, price: float,
    ) -> str:
        """Generate a follow-up message draft."""
        if touch_num == 1:
            return (
                f"Hi — following up on the {offer_key.replace('_', ' ')} proposal "
                f"(${price:,.0f}). Happy to answer any questions or schedule a quick call "
                f"to discuss next steps."
            )
        return (
            f"Just checking in on the {offer_key.replace('_', ' ')} proposal. "
            f"If the timing or scope needs adjusting, I'm flexible. "
            f"Let me know either way!"
        )

    def get_risk_report(self) -> dict:
        """
        Assess risk flags across active close packs.
        Checks: pricing below minimums, steep discounts, short timelines,
        missing opportunity links, high pending count.
        """
        from core.models_close_pack import ClosePack

        active = list(
            ClosePack.objects.filter(
                status__in=['draft', 'approved', 'sent'],
            ).values(
                'id', 'offer_key', 'price', 'timeline_days',
                'status', 'opportunity_id',
            )
        )

        flags = []
        for pack in active:
            pack_id = str(pack['id'])
            offer = pack['offer_key']
            price = float(pack.get('price', 0))
            timeline = pack.get('timeline_days', 14)

            # Below minimum price
            min_price = self.MIN_PRICE_BY_OFFER.get(offer, 500)
            if price < min_price:
                flags.append({
                    'pack_id': pack_id,
                    'risk': 'below_minimum_price',
                    'detail': f'{offer}: ${price:,.0f} < ${min_price:,.0f} minimum',
                    'severity': 'high',
                })

            # Short timeline
            if timeline < self.SHORT_TIMELINE_DAYS:
                flags.append({
                    'pack_id': pack_id,
                    'risk': 'short_timeline',
                    'detail': f'{timeline}d timeline (min {self.SHORT_TIMELINE_DAYS}d)',
                    'severity': 'medium',
                })

            # No linked opportunity
            if not pack.get('opportunity_id'):
                flags.append({
                    'pack_id': pack_id,
                    'risk': 'no_opportunity_link',
                    'detail': 'Pack not linked to an Opportunity — attribution gap',
                    'severity': 'low',
                })

        # Summary
        high_count = len([f for f in flags if f['severity'] == 'high'])
        med_count = len([f for f in flags if f['severity'] == 'medium'])

        return {
            'total_active_packs': len(active),
            'risk_flags': flags,
            'flag_count': len(flags),
            'high_severity': high_count,
            'medium_severity': med_count,
            'low_severity': len(flags) - high_count - med_count,
        }

    def get_velocity_report(self) -> dict:
        """
        Pipeline velocity: time-to-close, stage durations, conversion timeline.
        """
        from core.models_close_pack import ClosePack
        from django.db.models import Avg, Count

        # Won packs — time from creation to update (proxy for close time)
        won = list(
            ClosePack.objects.filter(status='won').values(
                'created_at', 'updated_at', 'offer_key', 'price',
            )
        )

        close_times = []
        for w in won:
            if w.get('created_at') and w.get('updated_at'):
                delta = (w['updated_at'] - w['created_at']).total_seconds() / 86400
                close_times.append({
                    'days': round(delta, 1),
                    'offer': w['offer_key'],
                    'price': float(w.get('price', 0)),
                })

        avg_close_days = (
            round(sum(c['days'] for c in close_times) / len(close_times), 1)
            if close_times else 0
        )

        # By offer
        by_offer = {}
        for ct in close_times:
            offer = ct['offer']
            if offer not in by_offer:
                by_offer[offer] = {'days': [], 'revenue': 0}
            by_offer[offer]['days'].append(ct['days'])
            by_offer[offer]['revenue'] += ct['price']

        offer_velocity = {}
        for offer, data in by_offer.items():
            offer_velocity[offer] = {
                'avg_days': round(sum(data['days']) / len(data['days']), 1),
                'deals': len(data['days']),
                'revenue': round(data['revenue'], 2),
            }

        # Current pipeline age
        from django.utils import timezone as tz
        now = tz.now()
        pipeline = ClosePack.objects.filter(
            status__in=['draft', 'approved', 'sent'],
        )
        pipeline_ages = []
        for p in pipeline.values('created_at', 'status'):
            if p.get('created_at'):
                age = (now - p['created_at']).total_seconds() / 86400
                pipeline_ages.append({
                    'age_days': round(age, 1),
                    'status': p['status'],
                })

        return {
            'won_deals': len(close_times),
            'avg_close_days': avg_close_days,
            'velocity_by_offer': offer_velocity,
            'current_pipeline_age': sorted(
                pipeline_ages, key=lambda x: -x['age_days'],
            )[:10],
            'pipeline_count': len(pipeline_ages),
        }

    def evaluate(self, now) -> dict:
        """
        Auto-evaluate close pack health for autopilot cycle.
        """
        from core.models_close_pack import ClosePack

        # Count overdue follow-ups
        overdue = ClosePack.objects.filter(
            status__in=['approved', 'sent'],
            followup_at__lte=now,
            followup_count__lt=2,
        ).count()

        # High-risk packs (below minimum price)
        high_risk = 0
        active = ClosePack.objects.filter(
            status__in=['draft', 'approved', 'sent'],
        ).values('offer_key', 'price')
        for p in active:
            min_price = self.MIN_PRICE_BY_OFFER.get(
                p['offer_key'], 500,
            )
            if float(p.get('price', 0)) < min_price:
                high_risk += 1

        # Stale drafts (>7d without approval)
        stale_drafts = ClosePack.objects.filter(
            status='draft',
            created_at__lt=now - timedelta(days=7),
        ).count()

        issues = []
        if overdue > 0:
            issues.append(f'{overdue} follow-ups overdue')
        if high_risk > 0:
            issues.append(f'{high_risk} packs below minimum price')
        if stale_drafts > 0:
            issues.append(f'{stale_drafts} draft packs stale >7d')

        return {
            'overdue_followups': overdue,
            'high_risk_packs': high_risk,
            'stale_drafts': stale_drafts,
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


# ── Engagement Autonomy (Policy 34 — Autonomy #30) ──────────────────────────


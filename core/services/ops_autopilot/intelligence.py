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


class KnowledgeEngine:
    """
    Knowledge & Citation diagnostics engine.

    Monitors citation health across the system by querying:
    - CitationViolation: tracks outputs that failed citation requirements
    - SpiderData: knowledge freshness and source coverage
    - ResearchResult: research completion and quality
    - Deliverable: output provenance and source linking

    Provides:
    - knowledge_health: overall health dashboard
    - citation_report: violation trends, top offending agents, block rates
    - source_report: spider data coverage, freshness, top sources
    - staleness_report: stale knowledge detection and refresh recommendations
    """

    # Freshness thresholds by data type (hours)
    FRESHNESS_THRESHOLDS = {
        'odds': 1,
        'sports_odds': 1,
        'live_scores': 0.5,
        'crypto_prices': 2,
        'stock_data': 4,
        'news': 24,
        'job_listings': 72,
        'legislation': 168,
        'research': 168,
    }
    DEFAULT_FRESHNESS_HOURS = 48

    def get_health(self) -> dict:
        """
        Overall knowledge health dashboard.
        """
        from core.models_orchestration import CitationViolation
        from core.models_unified_system import SpiderData
        from core.models_research import ResearchResult
        from django.db.models import Count

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        # Citation violations (24h and 7d)
        violations_24h = CitationViolation.objects.filter(
            created_at__gte=day_ago,
        ).count()
        violations_7d = CitationViolation.objects.filter(
            created_at__gte=week_ago,
        ).count()
        blocks_24h = CitationViolation.objects.filter(
            created_at__gte=day_ago,
            was_blocked=True,
        ).count()

        # Unresolved violations
        unresolved = CitationViolation.objects.filter(
            is_resolved=False,
        ).count()

        # Spider data freshness (last 24h ingestion)
        spider_24h = SpiderData.objects.filter(
            created_at__gte=day_ago,
        ).count()
        spider_7d = SpiderData.objects.filter(
            created_at__gte=week_ago,
        ).count()

        # Spider data by type (top 10)
        spider_by_type = list(
            SpiderData.objects.filter(created_at__gte=week_ago)
            .values('data_type')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Active spiders (distinct spider names in last 7d)
        active_spiders = SpiderData.objects.filter(
            created_at__gte=week_ago,
        ).values('spider_name').distinct().count()

        # Research results
        research_pending = ResearchResult.objects.filter(
            status='pending',
        ).count()
        research_blocked = ResearchResult.objects.filter(
            status='blocked',
        ).count()
        research_complete_7d = ResearchResult.objects.filter(
            status='complete',
            completed_at__gte=week_ago,
        ).count()

        # Health assessment
        health_issues = []
        if violations_24h > 10:
            health_issues.append(f'High violation rate: {violations_24h} in 24h')
        if blocks_24h > 5:
            health_issues.append(f'High block rate: {blocks_24h} outputs blocked in 24h')
        if spider_24h == 0:
            health_issues.append('No spider data ingested in 24h')
        if research_blocked > 3:
            health_issues.append(f'{research_blocked} research tasks blocked')

        return {
            'healthy': len(health_issues) == 0,
            'health_issues': health_issues,
            'citations': {
                'violations_24h': violations_24h,
                'violations_7d': violations_7d,
                'blocks_24h': blocks_24h,
                'unresolved': unresolved,
            },
            'knowledge_sources': {
                'spider_records_24h': spider_24h,
                'spider_records_7d': spider_7d,
                'active_spiders': active_spiders,
                'spider_by_type': spider_by_type,
            },
            'research': {
                'pending': research_pending,
                'blocked': research_blocked,
                'completed_7d': research_complete_7d,
            },
            'timestamp': now.isoformat(),
        }

    def get_citation_report(self, days: int = 7) -> dict:
        """
        Citation violation trends and top offending agents.
        """
        from core.models_orchestration import CitationViolation
        from django.db.models import Count

        now = timezone.now()
        since = now - timedelta(days=days)

        violations = CitationViolation.objects.filter(created_at__gte=since)

        # By type
        by_type = list(
            violations.values('violation_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # By agent (top offenders)
        by_agent = list(
            violations.values('agent_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Block rate
        total = violations.count()
        blocked = violations.filter(was_blocked=True).count()
        block_rate = round(blocked / total, 4) if total > 0 else 0.0

        # Resolution rate
        resolved = violations.filter(is_resolved=True).count()
        resolution_rate = round(resolved / total, 4) if total > 0 else 0.0

        # Daily trend (last N days)
        from django.db.models.functions import TruncDate
        daily_trend = list(
            violations
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        # Serialize dates
        for entry in daily_trend:
            entry['day'] = entry['day'].isoformat() if entry.get('day') else None

        return {
            'period_days': days,
            'total_violations': total,
            'blocked_count': blocked,
            'block_rate': block_rate,
            'resolved_count': resolved,
            'resolution_rate': resolution_rate,
            'by_violation_type': by_type,
            'top_offending_agents': by_agent,
            'daily_trend': daily_trend,
        }

    def get_source_report(self) -> dict:
        """
        Spider data coverage and source quality metrics.
        """
        from core.models_unified_system import SpiderData
        from django.db.models import Count, Avg, Max

        now = timezone.now()
        week_ago = now - timedelta(days=7)

        # Top sources by volume
        top_spiders = list(
            SpiderData.objects.filter(created_at__gte=week_ago)
            .values('spider_name')
            .annotate(
                count=Count('id'),
                avg_relevance=Avg('relevance_score'),
                latest=Max('created_at'),
            )
            .order_by('-count')[:15]
        )
        for s in top_spiders:
            s['avg_relevance'] = round(float(s['avg_relevance'] or 0), 2)
            s['latest'] = s['latest'].isoformat() if s.get('latest') else None

        # Data type distribution
        type_dist = list(
            SpiderData.objects.filter(created_at__gte=week_ago)
            .values('data_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Source URL diversity (unique domains)
        from django.db.models import Value
        all_urls = list(
            SpiderData.objects.filter(created_at__gte=week_ago)
            .values_list('source_url', flat=True)[:1000]
        )
        domains = set()
        for url in all_urls:
            if url:
                try:
                    parts = url.split('//')
                    domain = parts[1].split('/')[0] if len(parts) > 1 else parts[0].split('/')[0]
                    domains.add(domain)
                except (IndexError, AttributeError):
                    pass

        # Research sources used
        from core.models_research import ResearchResult
        research_with_external = ResearchResult.objects.filter(
            status='complete',
            completed_at__gte=week_ago,
        ).exclude(external_sources=[]).count()
        research_total = ResearchResult.objects.filter(
            status='complete',
            completed_at__gte=week_ago,
        ).count()

        return {
            'top_spiders': top_spiders,
            'data_type_distribution': type_dist,
            'unique_domains': len(domains),
            'total_sources_7d': sum(s['count'] for s in top_spiders),
            'research_with_sources': research_with_external,
            'research_total': research_total,
            'research_source_rate': round(
                research_with_external / research_total, 4
            ) if research_total > 0 else 0.0,
        }

    def get_staleness_report(self) -> dict:
        """
        Detect stale knowledge sources and recommend refreshes.
        """
        from core.models_unified_system import SpiderData
        from django.db.models import Max

        now = timezone.now()

        # Latest record per data_type
        latest_by_type = list(
            SpiderData.objects.values('data_type')
            .annotate(latest=Max('created_at'), )
            .order_by('data_type')
        )

        stale_types = []
        fresh_types = []
        for entry in latest_by_type:
            dt = entry['data_type']
            latest = entry['latest']
            threshold_hours = self.FRESHNESS_THRESHOLDS.get(
                dt, self.DEFAULT_FRESHNESS_HOURS,
            )
            age_hours = (now - latest).total_seconds() / 3600 if latest else 999999

            item = {
                'data_type': dt,
                'latest_record': latest.isoformat() if latest else None,
                'age_hours': round(age_hours, 1),
                'threshold_hours': threshold_hours,
            }

            if age_hours > threshold_hours:
                item['status'] = 'stale'
                item['overdue_hours'] = round(age_hours - threshold_hours, 1)
                stale_types.append(item)
            else:
                item['status'] = 'fresh'
                fresh_types.append(item)

        # Latest record per spider
        latest_by_spider = list(
            SpiderData.objects.values('spider_name')
            .annotate(latest=Max('created_at'))
            .order_by('spider_name')
        )
        dormant_spiders = []
        for entry in latest_by_spider:
            latest = entry['latest']
            if latest:
                age_hours = (now - latest).total_seconds() / 3600
                if age_hours > 168:  # 7 days without data
                    dormant_spiders.append({
                        'spider_name': entry['spider_name'],
                        'last_active': latest.isoformat(),
                        'dormant_hours': round(age_hours, 1),
                    })

        return {
            'stale_data_types': stale_types,
            'fresh_data_types': fresh_types,
            'stale_count': len(stale_types),
            'fresh_count': len(fresh_types),
            'dormant_spiders': dormant_spiders[:20],
            'dormant_spider_count': len(dormant_spiders),
            'recommendations': self._staleness_recommendations(stale_types, dormant_spiders),
        }

    def _staleness_recommendations(self, stale_types: list, dormant_spiders: list) -> list:
        """Generate actionable recommendations for stale data."""
        recs = []
        for st in stale_types[:5]:
            recs.append(
                f"Refresh {st['data_type']} data — {st['overdue_hours']:.0f}h overdue "
                f"(threshold: {st['threshold_hours']}h)"
            )
        if len(dormant_spiders) > 5:
            recs.append(
                f"{len(dormant_spiders)} spiders dormant >7d — review spider health"
            )
        elif dormant_spiders:
            for ds in dormant_spiders[:3]:
                recs.append(
                    f"Spider {ds['spider_name']} dormant {ds['dormant_hours']:.0f}h — check schedule"
                )
        return recs

    def evaluate(self, now) -> dict:
        """
        Auto-evaluate knowledge health for autopilot cycle.
        Returns key metrics and flags issues.
        """
        from core.models_orchestration import CitationViolation
        from core.models_unified_system import SpiderData

        day_ago = now - timedelta(hours=24)

        violations_24h = CitationViolation.objects.filter(
            created_at__gte=day_ago,
        ).count()
        blocks_24h = CitationViolation.objects.filter(
            created_at__gte=day_ago,
            was_blocked=True,
        ).count()

        spider_24h = SpiderData.objects.filter(
            created_at__gte=day_ago,
        ).count()

        issues = []
        if violations_24h > 10:
            issues.append(f'{violations_24h} citation violations in 24h')
        if blocks_24h > 5:
            issues.append(f'{blocks_24h} outputs blocked by citation gate in 24h')
        if spider_24h == 0:
            issues.append('No spider data ingested in 24h — knowledge going stale')

        return {
            'violation_count_24h': violations_24h,
            'block_count_24h': blocks_24h,
            'spider_ingestion_24h': spider_24h,
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


# ── Close Pack Autonomy (Policy 33 — Autonomy #29) ──────────────────────────

class GrowthEngine:
    """
    Growth & distribution autonomy — finds distribution-ready content,
    tracks channel distribution, manages scheduling, and reports funnel.

    Channels: x_twitter, linkedin, email, discord
    Content sources: Deliverable (published), SelfBlog (published)

    Guardrails:
    - Only content that passed quality gates (quality_score >= 0.5)
    - Respects governance mode — freeze/safe_mode blocks scheduling
    - Manual-first v1 — generates drafts, never auto-posts
    - Rate limits: max 10 items/day per channel
    """

    CHANNELS = ['x_twitter', 'linkedin', 'email', 'discord']
    MIN_QUALITY = 0.5
    MAX_DAILY_PER_CHANNEL = 10
    STALE_CANDIDATE_DAYS = 14

    def get_candidates(self, limit: int = 20) -> dict:
        """
        Find distribution-ready content ranked by freshness + quality.
        Sources: published Deliverables + SelfBlogs with quality gate.
        """
        from datetime import timedelta as td

        from django.db.models import Q
        from django.utils import timezone as tz

        from core.models_deliverables import Deliverable, DeliverableExport

        now = tz.now()
        stale_cutoff = now - td(days=self.STALE_CANDIDATE_DAYS)

        deliverables = list(
            Deliverable.objects.filter(
                quality_score__gte=self.MIN_QUALITY,
                created_at__gte=stale_cutoff,
            )
            .exclude(
                Q(deliverable_type='template') | Q(deliverable_type='code')
            )
            .order_by('-quality_score', '-created_at')[:limit]
        )

        candidates = []
        exported_ids = set(
            DeliverableExport.objects.filter(
                deliverable__in=deliverables
            ).values_list('deliverable_id', flat=True)
        )

        for d in deliverables:
            age_hours = (now - d.created_at).total_seconds() / 3600
            freshness_score = max(0, 1.0 - (age_hours / (self.STALE_CANDIDATE_DAYS * 24)))

            candidates.append({
                'id': str(d.id),
                'title': d.title,
                'type': d.deliverable_type,
                'category': d.category or '',
                'quality': round(d.quality_score, 2),
                'freshness': round(freshness_score, 2),
                'rank_score': round(
                    d.quality_score * 0.6 + freshness_score * 0.4, 3
                ),
                'age_hours': round(age_hours, 1),
                'already_exported': str(d.id) in {str(x) for x in exported_ids},
                'source': 'deliverable',
            })

        try:
            from core.models_unified_system import SelfBlog
            blogs = list(
                SelfBlog.objects.filter(
                    created_at__gte=stale_cutoff,
                    status='published',
                ).order_by('-created_at')[:limit // 2]
            )
            for b in blogs:
                age_hours = (now - b.created_at).total_seconds() / 3600
                freshness_score = max(0, 1.0 - (age_hours / (self.STALE_CANDIDATE_DAYS * 24)))
                quality = 0.7
                candidates.append({
                    'id': str(b.id),
                    'title': b.title,
                    'type': 'blog',
                    'category': getattr(b, 'blog_type', 'blog'),
                    'quality': quality,
                    'freshness': round(freshness_score, 2),
                    'rank_score': round(quality * 0.6 + freshness_score * 0.4, 3),
                    'age_hours': round(age_hours, 1),
                    'already_exported': False,
                    'source': 'self_blog',
                })
        except Exception:
            pass

        candidates.sort(key=lambda x: x['rank_score'], reverse=True)
        candidates = candidates[:limit]

        return {
            'candidates': candidates,
            'total': len(candidates),
            'from_deliverables': sum(1 for c in candidates if c['source'] == 'deliverable'),
            'from_blogs': sum(1 for c in candidates if c['source'] == 'self_blog'),
            'already_distributed': sum(1 for c in candidates if c.get('already_exported')),
        }

    def get_schedule(self, days: int = 7) -> dict:
        """
        Distribution schedule: recent exports by channel + rate usage.
        """
        from datetime import timedelta as td

        from django.db.models import Count
        from django.utils import timezone as tz

        from core.models_deliverables import DeliverableExport

        now = tz.now()
        window = now - td(days=days)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        exports = list(
            DeliverableExport.objects.filter(
                created_at__gte=window,
            )
            .values('export_format')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        today_exports = DeliverableExport.objects.filter(
            created_at__gte=today_start,
        ).count()

        timeline = list(
            DeliverableExport.objects.filter(
                created_at__gte=window,
            ).order_by('-created_at')
            .values('deliverable__title', 'export_format', 'created_at')[:20]
        )
        for t in timeline:
            t['created_at'] = t['created_at'].isoformat()

        max_daily = self.MAX_DAILY_PER_CHANNEL * len(self.CHANNELS)

        return {
            'period_days': days,
            'by_format': {e['export_format']: e['count'] for e in exports},
            'total_exports': sum(e['count'] for e in exports),
            'today_exports': today_exports,
            'daily_limit': max_daily,
            'rate_used_pct': round(today_exports / max_daily * 100, 1) if max_daily > 0 else 0,
            'recent_timeline': timeline,
        }

    def get_channel_report(self) -> dict:
        """
        Channel-level distribution stats: formats used, engagement, coverage gaps.
        """
        from datetime import timedelta as td

        from django.db.models import Avg, Count
        from django.utils import timezone as tz

        from core.models_deliverables import Deliverable, DeliverableEvent, DeliverableExport

        now = tz.now()
        last_30d = now - td(days=30)

        format_stats = list(
            DeliverableExport.objects.filter(
                created_at__gte=last_30d,
            )
            .values('export_format')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        event_stats = list(
            DeliverableEvent.objects.filter(
                created_at__gte=last_30d,
            )
            .values('event_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        type_stats = list(
            Deliverable.objects.filter(
                created_at__gte=last_30d,
                quality_score__gte=self.MIN_QUALITY,
            )
            .values('deliverable_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        avg_quality = DeliverableExport.objects.filter(
            created_at__gte=last_30d,
        ).aggregate(
            avg_quality=Avg('deliverable__quality_score'),
        )['avg_quality'] or 0

        used_formats = {f['export_format'] for f in format_stats}
        available_formats = {'pdf', 'docx', 'html', 'markdown', 'json'}
        unused = available_formats - used_formats

        return {
            'period_days': 30,
            'by_format': {f['export_format']: f['count'] for f in format_stats},
            'by_event_type': {e['event_type']: e['count'] for e in event_stats},
            'by_content_type': {t['deliverable_type']: t['count'] for t in type_stats},
            'avg_distributed_quality': round(avg_quality, 2),
            'unused_formats': sorted(unused),
            'total_exports': sum(f['count'] for f in format_stats),
            'total_engagement_events': sum(e['count'] for e in event_stats),
        }

    def get_funnel(self, days: int = 30) -> dict:
        """
        Distribution funnel: candidates -> exported -> engaged -> actions taken.
        """
        from datetime import timedelta as td

        from django.db.models import Count
        from django.utils import timezone as tz

        from core.models_deliverables import Deliverable, DeliverableEvent, DeliverableExport

        now = tz.now()
        window = now - td(days=days)

        candidates = Deliverable.objects.filter(
            quality_score__gte=self.MIN_QUALITY,
            created_at__gte=window,
        ).count()

        exported_count = DeliverableExport.objects.filter(
            created_at__gte=window,
        ).values('deliverable_id').distinct().count()

        engaged = DeliverableEvent.objects.filter(
            created_at__gte=window,
        ).values('deliverable_id').distinct().count()

        actions_taken = DeliverableEvent.objects.filter(
            created_at__gte=window,
            event_type='action_taken',
        ).values('deliverable_id').distinct().count()

        export_rate = round(exported_count / candidates * 100, 1) if candidates > 0 else 0
        engage_rate = round(engaged / exported_count * 100, 1) if exported_count > 0 else 0
        action_rate = round(actions_taken / engaged * 100, 1) if engaged > 0 else 0

        return {
            'period_days': days,
            'candidates': candidates,
            'exported': exported_count,
            'engaged': engaged,
            'actions_taken': actions_taken,
            'export_rate_pct': export_rate,
            'engage_rate_pct': engage_rate,
            'action_rate_pct': action_rate,
        }

    def evaluate(self, now) -> dict:
        """
        Auto-evaluate distribution health for autopilot cycle.
        """
        from core.models_deliverables import Deliverable, DeliverableExport

        cutoff = now - timedelta(days=self.STALE_CANDIDATE_DAYS)
        quality_deliverables = Deliverable.objects.filter(
            quality_score__gte=self.MIN_QUALITY,
            created_at__gte=cutoff,
        )
        exported_ids = set(
            DeliverableExport.objects.filter(
                deliverable__in=quality_deliverables,
            ).values_list('deliverable_id', flat=True)
        )
        total_candidates = quality_deliverables.count()
        undistributed = total_candidates - len(exported_ids)

        stale_cutoff = now - timedelta(days=7)
        stale_scheduled = DeliverableExport.objects.filter(
            created_at__lt=stale_cutoff,
            deliverable__events__isnull=True,
        ).count()

        issues = []
        if undistributed > 10:
            issues.append(f'{undistributed} quality deliverables not distributed')
        if total_candidates > 0 and undistributed / total_candidates > 0.7:
            issues.append(
                f'Distribution coverage low: {round((1 - undistributed / total_candidates) * 100)}%'
            )
        if stale_scheduled > 5:
            issues.append(f'{stale_scheduled} exports with zero engagement')

        return {
            'total_candidates': total_candidates,
            'undistributed': undistributed,
            'distributed': len(exported_ids),
            'stale_scheduled': stale_scheduled,
            'coverage_pct': round(
                len(exported_ids) / total_candidates * 100, 1
            ) if total_candidates > 0 else 0,
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


# ── Policy 36: Cost & Capacity Planning Autonomy ──────────────────────────────


class CapacityEngine:
    """
    Cost & capacity planning — monitors task throughput, identifies
    bottlenecks, projects spend, and recommends throttle actions.

    Data sources:
    - CeleryTaskEvent: task latency, queue wait times, failure rates
    - LLMCallLog: token spend, model costs
    - AgentExecution: agent throughput and success rates

    Guardrails:
    - Read-only analysis — never auto-throttles without governance
    - Recommendations only, tied to GovernanceEngine for enforcement
    """

    # Latency thresholds (seconds)
    P95_WARNING = 120       # 2 min
    P95_CRITICAL = 300      # 5 min
    QUEUE_BACKLOG_WARNING = 50
    QUEUE_BACKLOG_CRITICAL = 200

    def get_capacity_forecast(self, hours: int = 24) -> dict:
        """
        Forecast task volume, latency, and spend for the next N hours
        based on recent trends.
        """
        from django.db.models import Avg, Count, Max, Sum
        from django.utils import timezone as tz

        from core.models_celery_telemetry import CeleryTaskEvent

        now = tz.now()
        lookback = now - timedelta(hours=hours)

        # Recent task volume and latency
        recent_tasks = CeleryTaskEvent.objects.filter(
            started_at__gte=lookback,
        )

        total_tasks = recent_tasks.count()
        completed = recent_tasks.filter(status='SUCCESS').count()
        failed = recent_tasks.filter(status='FAILURE').count()

        # Latency stats
        latency_stats = recent_tasks.filter(
            duration_seconds__isnull=False,
            status='SUCCESS',
        ).aggregate(
            avg=Avg('duration_seconds'),
            max=Max('duration_seconds'),
        )

        # p95 approximation — top 5% slowest
        success_count = recent_tasks.filter(
            duration_seconds__isnull=False,
            status='SUCCESS',
        ).count()
        p95_idx = max(0, int(success_count * 0.95))
        p95_tasks = list(
            recent_tasks.filter(
                duration_seconds__isnull=False,
                status='SUCCESS',
            ).order_by('duration_seconds')
            .values_list('duration_seconds', flat=True)[p95_idx:p95_idx + 1]
        )
        p95 = p95_tasks[0] if p95_tasks else 0

        # By queue
        by_queue = list(
            recent_tasks.filter(queue__gt='')
            .values('queue')
            .annotate(
                count=Count('id'),
                avg_duration=Avg('duration_seconds'),
                failures=Count('id', filter=__import__('django').db.models.Q(status='FAILURE')),
            )
            .order_by('-count')[:10]
        )
        for q in by_queue:
            q['avg_duration'] = round(q['avg_duration'] or 0, 2)
            q['failure_rate_pct'] = round(
                q['failures'] / q['count'] * 100, 1
            ) if q['count'] > 0 else 0

        # Memory usage
        memory_stats = recent_tasks.filter(
            rss_mb_end__isnull=False,
        ).aggregate(
            avg_rss=Avg('rss_mb_end'),
            max_rss=Max('rss_mb_end'),
            avg_delta=Avg('rss_delta_mb'),
        )

        # Spend projection (from LLMCallLog if available)
        spend_data = self._get_spend_projection(lookback, now, hours)

        # Task rate (tasks per hour)
        hours_actual = max(1, (now - lookback).total_seconds() / 3600)
        task_rate = round(total_tasks / hours_actual, 1)

        return {
            'forecast_hours': hours,
            'recent_tasks': total_tasks,
            'completed': completed,
            'failed': failed,
            'failure_rate_pct': round(failed / total_tasks * 100, 1) if total_tasks > 0 else 0,
            'task_rate_per_hour': task_rate,
            'projected_tasks': round(task_rate * hours),
            'latency': {
                'avg_seconds': round(latency_stats['avg'] or 0, 2),
                'max_seconds': round(latency_stats['max'] or 0, 2),
                'p95_seconds': round(p95, 2),
            },
            'memory': {
                'avg_rss_mb': round(memory_stats['avg_rss'] or 0, 1),
                'max_rss_mb': round(memory_stats['max_rss'] or 0, 1),
                'avg_delta_mb': round(memory_stats['avg_delta'] or 0, 1),
            },
            'by_queue': by_queue,
            'spend': spend_data,
        }

    def get_bottleneck_report(self, hours: int = 24) -> dict:
        """
        Identify top bottlenecks: slow agents, overloaded queues, failing tasks.
        """
        from django.db.models import Avg, Count
        from django.utils import timezone as tz

        from core.models_celery_telemetry import CeleryTaskEvent

        now = tz.now()
        lookback = now - timedelta(hours=hours)

        # Slowest task types
        slow_tasks = list(
            CeleryTaskEvent.objects.filter(
                started_at__gte=lookback,
                duration_seconds__isnull=False,
                status='SUCCESS',
            )
            .values('task_name')
            .annotate(
                count=Count('id'),
                avg_duration=Avg('duration_seconds'),
            )
            .filter(avg_duration__gte=30)  # only tasks >30s avg
            .order_by('-avg_duration')[:10]
        )
        for t in slow_tasks:
            t['avg_duration'] = round(t['avg_duration'], 2)

        # Highest failure rate tasks
        failing_tasks = list(
            CeleryTaskEvent.objects.filter(
                started_at__gte=lookback,
            )
            .values('task_name')
            .annotate(
                total=Count('id'),
                failures=Count('id', filter=__import__('django').db.models.Q(status='FAILURE')),
            )
            .filter(failures__gte=1, total__gte=3)
            .order_by('-failures')[:10]
        )
        for t in failing_tasks:
            t['failure_rate_pct'] = round(t['failures'] / t['total'] * 100, 1)

        # Memory hogs
        memory_hogs = list(
            CeleryTaskEvent.objects.filter(
                started_at__gte=lookback,
                rss_delta_mb__isnull=False,
                rss_delta_mb__gte=50,
            )
            .values('task_name')
            .annotate(
                count=Count('id'),
                avg_delta=Avg('rss_delta_mb'),
            )
            .order_by('-avg_delta')[:10]
        )
        for m in memory_hogs:
            m['avg_delta'] = round(m['avg_delta'], 1)

        bottlenecks = []
        for t in slow_tasks[:3]:
            bottlenecks.append({
                'type': 'slow_task',
                'name': t['task_name'],
                'detail': f"avg {t['avg_duration']}s ({t['count']} runs)",
            })
        for t in failing_tasks[:3]:
            bottlenecks.append({
                'type': 'failing_task',
                'name': t['task_name'],
                'detail': f"{t['failure_rate_pct']}% failure rate ({t['failures']}/{t['total']})",
            })
        for m in memory_hogs[:2]:
            bottlenecks.append({
                'type': 'memory_hog',
                'name': m['task_name'],
                'detail': f"avg +{m['avg_delta']}MB per run",
            })

        return {
            'period_hours': hours,
            'slow_tasks': slow_tasks,
            'failing_tasks': failing_tasks,
            'memory_hogs': memory_hogs,
            'bottlenecks': bottlenecks,
            'bottleneck_count': len(bottlenecks),
        }

    def get_throttle_plan(self) -> dict:
        """
        Propose throttle actions based on current capacity state.
        Read-only — never auto-applies.
        """
        from django.db.models import Avg, Count
        from django.utils import timezone as tz

        from core.models_celery_telemetry import CeleryTaskEvent

        now = tz.now()
        last_1h = now - timedelta(hours=1)

        # Current throughput
        recent = CeleryTaskEvent.objects.filter(started_at__gte=last_1h)
        total = recent.count()
        failures = recent.filter(status='FAILURE').count()
        failure_rate = failures / total * 100 if total > 0 else 0

        # p95 latency
        success_tasks = recent.filter(
            duration_seconds__isnull=False,
            status='SUCCESS',
        )
        success_count = success_tasks.count()
        p95_idx = max(0, int(success_count * 0.95))
        p95_vals = list(
            success_tasks.order_by('duration_seconds')
            .values_list('duration_seconds', flat=True)[p95_idx:p95_idx + 1]
        )
        p95 = p95_vals[0] if p95_vals else 0

        # Current governance mode
        gov_mode = 'normal'
        try:
            from core.models_governance import GovernanceState
            gs = GovernanceState.objects.filter(scope='global').first()
            if gs:
                gov_mode = gs.effective_mode
        except Exception:
            pass

        # Generate recommendations
        recommendations = []
        if p95 > self.P95_CRITICAL:
            recommendations.append({
                'action': 'reduce_concurrency',
                'reason': f'p95 latency {round(p95)}s > {self.P95_CRITICAL}s threshold',
                'severity': 'critical',
            })
        elif p95 > self.P95_WARNING:
            recommendations.append({
                'action': 'monitor_latency',
                'reason': f'p95 latency {round(p95)}s approaching critical threshold',
                'severity': 'warning',
            })

        if failure_rate > 20:
            recommendations.append({
                'action': 'pause_non_critical',
                'reason': f'Failure rate {round(failure_rate, 1)}% exceeds 20% threshold',
                'severity': 'critical',
            })
        elif failure_rate > 10:
            recommendations.append({
                'action': 'investigate_failures',
                'reason': f'Failure rate {round(failure_rate, 1)}% elevated',
                'severity': 'warning',
            })

        if total > 200:  # More than 200 tasks/hour
            recommendations.append({
                'action': 'defer_batch_tasks',
                'reason': f'{total} tasks/hour — consider deferring non-critical batches',
                'severity': 'info',
            })

        return {
            'current_state': {
                'tasks_last_hour': total,
                'failure_rate_pct': round(failure_rate, 1),
                'p95_seconds': round(p95, 2),
                'governance_mode': gov_mode,
            },
            'recommendations': recommendations,
            'recommendation_count': len(recommendations),
            'needs_action': any(r['severity'] == 'critical' for r in recommendations),
        }

    def get_budget_envelope(self, days: int = 7) -> dict:
        """
        Per-queue/agent spend tracking with budget envelope projections.
        """
        from django.db.models import Count, Sum
        from django.utils import timezone as tz

        from core.models_celery_telemetry import CeleryTaskEvent

        now = tz.now()
        window = now - timedelta(days=days)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Task volume by queue (proxy for resource consumption)
        by_queue = list(
            CeleryTaskEvent.objects.filter(
                started_at__gte=window,
                queue__gt='',
            )
            .values('queue')
            .annotate(
                total=Count('id'),
                total_duration=Sum('duration_seconds'),
            )
            .order_by('-total')
        )
        for q in by_queue:
            q['total_duration'] = round(q['total_duration'] or 0, 1)
            q['avg_per_day'] = round(q['total'] / max(1, days), 1)

        # Today's task count
        today_tasks = CeleryTaskEvent.objects.filter(
            started_at__gte=today_start,
        ).count()

        # LLM spend if available
        spend = self._get_spend_projection(window, now, days * 24)

        # Budget cap from config
        budget_cap = 5.0  # default
        try:
            from core.models.system import SystemConfiguration
            cap_entry = SystemConfiguration.objects.filter(
                key='BUDGET_DAILY_CAP_USD',
            ).first()
            if cap_entry and cap_entry.value:
                val = cap_entry.value
                if isinstance(val, dict):
                    budget_cap = float(val.get('value', 5.0))
                else:
                    budget_cap = float(val)
        except Exception:
            pass

        daily_spend = spend.get('daily_avg_usd', 0)
        projected_monthly = round(daily_spend * 30, 2)

        return {
            'period_days': days,
            'by_queue': by_queue,
            'today_tasks': today_tasks,
            'spend': spend,
            'budget_cap_daily_usd': budget_cap,
            'daily_spend_usd': daily_spend,
            'projected_monthly_usd': projected_monthly,
            'budget_utilization_pct': round(
                daily_spend / budget_cap * 100, 1
            ) if budget_cap > 0 else 0,
        }

    def _get_spend_projection(self, start, end, hours: int) -> dict:
        """
        Calculate spend from LLMCallLog for the given window.
        """
        result = {
            'total_usd': 0,
            'daily_avg_usd': 0,
            'by_model': {},
        }

        try:
            from django.db.models import Count, Sum
            from core.models_llm_routing import LLMCallLog

            calls = LLMCallLog.objects.filter(
                created_at__gte=start,
                created_at__lte=end,
            )
            total_cost = calls.aggregate(
                total=Sum('cost_usd'),
            )['total'] or 0

            by_model = list(
                calls.values('model_name')
                .annotate(
                    cost=Sum('cost_usd'),
                    count=Count('id'),
                )
                .order_by('-cost')[:10]
            )

            days = max(1, hours / 24)
            result['total_usd'] = round(float(total_cost), 4)
            result['daily_avg_usd'] = round(float(total_cost) / days, 4)
            result['by_model'] = {
                m['model_name']: {
                    'cost_usd': round(float(m['cost'] or 0), 4),
                    'calls': m['count'],
                }
                for m in by_model
            }
        except Exception:
            pass

        return result

    def evaluate(self, now) -> dict:
        """
        Auto-evaluate capacity health for autopilot cycle.
        """
        from core.models_celery_telemetry import CeleryTaskEvent

        last_1h = now - timedelta(hours=1)

        # Recent task stats
        recent = CeleryTaskEvent.objects.filter(started_at__gte=last_1h)
        total = recent.count()
        failures = recent.filter(status='FAILURE').count()
        failure_rate = failures / total * 100 if total > 0 else 0

        # p95 latency
        success_tasks = recent.filter(
            duration_seconds__isnull=False,
            status='SUCCESS',
        )
        success_count = success_tasks.count()
        p95_idx = max(0, int(success_count * 0.95))
        p95_vals = list(
            success_tasks.order_by('duration_seconds')
            .values_list('duration_seconds', flat=True)[p95_idx:p95_idx + 1]
        )
        p95 = p95_vals[0] if p95_vals else 0

        # Pending tasks (started but not finished)
        total_pending = CeleryTaskEvent.objects.filter(
            status='STARTED',
            started_at__lt=now - timedelta(minutes=5),
        ).count()

        issues = []
        if p95 > self.P95_CRITICAL:
            issues.append(f'p95 latency {round(p95)}s exceeds {self.P95_CRITICAL}s')
        if failure_rate > 20:
            issues.append(f'Failure rate {round(failure_rate, 1)}% exceeds 20%')
        if total_pending > self.QUEUE_BACKLOG_CRITICAL:
            issues.append(f'{total_pending} stale pending tasks (>5min)')

        # Check spend
        try:
            spend = self._get_spend_projection(
                now - timedelta(hours=24), now, 24
            )
            daily_spend = spend.get('daily_avg_usd', 0)
            if daily_spend > 4.0:  # Near default cap
                issues.append(f'Daily spend ${daily_spend:.2f} approaching cap')
        except Exception:
            pass

        return {
            'tasks_last_hour': total,
            'failure_rate_pct': round(failure_rate, 1),
            'p95_seconds': round(p95, 2),
            'total_pending': total_pending,
            'bottleneck_count': len(issues),
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


# ── Policy 37: Security & Abuse Detection Autonomy ────────────────────────────


class SecurityEngine:
    """
    Security & abuse detection — monitors for permission drift,
    abuse patterns, secrets exposure, and kill switch hygiene.

    Data sources:
    - CockpitAuditLog: mutation audit trail
    - KillSwitch: emergency control health
    - GovernanceState: governance mode tracking
    - Deliverable/SelfBlog: content scanning for secrets

    Guardrails:
    - Read-only analysis — never auto-contains without governance
    - Recommendations only in v1
    """

    AUDIT_SPIKE_THRESHOLD = 50
    FAILED_OPS_THRESHOLD = 10
    SECRETS_PATTERNS = [
        r'sk-[a-zA-Z0-9]{20,}',
        r'AKIA[A-Z0-9]{16}',
        r'ghp_[a-zA-Z0-9]{36}',
        r'xoxb-[0-9]+-[a-zA-Z0-9]+',
        r'whsec_[a-zA-Z0-9]+',
    ]

    def get_permission_drift_report(self, hours: int = 24) -> dict:
        """
        Check for permission-related anomalies in audit logs.
        """
        from django.db.models import Count
        from django.utils import timezone as tz

        now = tz.now()
        lookback = now - timedelta(hours=hours)
        drift_issues = []
        total_actions = 0
        hourly_rate = 0.0

        try:
            from core.models_cockpit_audit import CockpitAuditLog

            action_counts = list(
                CockpitAuditLog.objects.filter(
                    created_at__gte=lookback,
                )
                .values('action')
                .annotate(count=Count('id'))
                .order_by('-count')[:20]
            )

            total_actions = sum(a['count'] for a in action_counts)
            hourly_rate = total_actions / max(1, hours)

            if hourly_rate > self.AUDIT_SPIKE_THRESHOLD:
                drift_issues.append({
                    'type': 'audit_spike',
                    'severity': 'warning',
                    'detail': f'{total_actions} audit actions in {hours}h ({hourly_rate:.0f}/hr)',
                })

            config_changes = [a for a in action_counts if 'config' in a['action'].lower()]
            config_count = sum(c['count'] for c in config_changes)
            if config_count > 10:
                drift_issues.append({
                    'type': 'config_churn',
                    'severity': 'warning',
                    'detail': f'{config_count} config changes in {hours}h',
                })
        except Exception:
            pass

        try:
            from core.models_governance import GovernanceState
            recent_gov = GovernanceState.objects.filter(
                updated_at__gte=lookback,
            ).count()
            if recent_gov > 5:
                drift_issues.append({
                    'type': 'governance_churn',
                    'severity': 'info',
                    'detail': f'{recent_gov} governance state changes in {hours}h',
                })
        except Exception:
            pass

        try:
            from core.models_governance import KillSwitch
            expired_active = KillSwitch.objects.filter(
                is_active=True,
                expires_at__lt=now,
            ).count()
            if expired_active > 0:
                drift_issues.append({
                    'type': 'stale_kill_switch',
                    'severity': 'warning',
                    'detail': f'{expired_active} expired kill switches still active',
                })
        except Exception as e:
            logger.warning(
                "ops_autopilot.intelligence: stale_kill_switch audit "
                "check failed (%s: %s) — drift_issues report will not "
                "include expired kill switches",
                type(e).__name__, e,
            )

        return {
            'period_hours': hours,
            'drift_issues': drift_issues,
            'issue_count': len(drift_issues),
            'total_audit_actions': total_actions,
            'audit_rate_per_hour': round(hourly_rate, 1),
        }

    def get_abuse_risk_queue(self, hours: int = 24, limit: int = 50) -> dict:
        """
        Flag suspicious patterns: rapid audit activity by user/IP.
        """
        from django.db.models import Count
        from django.utils import timezone as tz

        now = tz.now()
        lookback = now - timedelta(hours=hours)
        flags = []

        try:
            from core.models_cockpit_audit import CockpitAuditLog

            by_user = list(
                CockpitAuditLog.objects.filter(
                    created_at__gte=lookback,
                    user__isnull=False,
                )
                .values('user__username')
                .annotate(count=Count('id'))
                .order_by('-count')[:limit]
            )
            for u in by_user:
                if u['count'] > self.AUDIT_SPIKE_THRESHOLD:
                    flags.append({
                        'type': 'high_activity_user',
                        'severity': 'warning',
                        'user': u['user__username'],
                        'detail': f'{u["count"]} actions in {hours}h',
                    })

            by_ip = list(
                CockpitAuditLog.objects.filter(
                    created_at__gte=lookback,
                    ip_address__isnull=False,
                )
                .values('ip_address')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            for ip in by_ip:
                if ip['count'] > self.AUDIT_SPIKE_THRESHOLD * 2:
                    flags.append({
                        'type': 'high_activity_ip',
                        'severity': 'critical',
                        'ip': ip['ip_address'],
                        'detail': f'{ip["count"]} actions from single IP',
                    })
        except Exception as e:
            logger.warning(
                "ops_autopilot.intelligence: abuse_risk_queue user/IP "
                "audit failed (%s: %s) — security flags for high-activity "
                "users and IPs will be missing",
                type(e).__name__, e,
            )

        try:
            from core.models_diagnostic_pipeline import AutopilotAction
            failed_actions = AutopilotAction.objects.filter(
                created_at__gte=lookback,
                status='failed',
            ).count()
            if failed_actions > self.FAILED_OPS_THRESHOLD:
                flags.append({
                    'type': 'failed_operations',
                    'severity': 'warning',
                    'detail': f'{failed_actions} failed autopilot actions in {hours}h',
                })
        except Exception as e:
            logger.warning(
                "ops_autopilot.intelligence: AutopilotAction failure "
                "count audit failed (%s: %s) — failed_operations flag "
                "will be missing from abuse_risk_queue",
                type(e).__name__, e,
            )

        return {
            'period_hours': hours,
            'flags': flags[:limit],
            'flag_count': len(flags),
            'has_critical': any(f['severity'] == 'critical' for f in flags),
        }

    def get_containment_plan(self, dry_run: bool = True) -> dict:
        """
        Generate containment recommendations based on current risk state.
        """
        from django.utils import timezone as tz

        now = tz.now()
        drift = self.get_permission_drift_report(hours=6)
        abuse = self.get_abuse_risk_queue(hours=6)

        recommendations = []
        for issue in drift.get('drift_issues', []):
            if issue['type'] == 'stale_kill_switch':
                recommendations.append({
                    'action': 'deactivate_expired_switches',
                    'reason': issue['detail'],
                    'severity': 'warning',
                    'auto_actionable': True,
                })
            elif issue['type'] == 'audit_spike':
                recommendations.append({
                    'action': 'investigate_audit_spike',
                    'reason': issue['detail'],
                    'severity': 'warning',
                    'auto_actionable': False,
                })

        for flag in abuse.get('flags', []):
            if flag['severity'] == 'critical':
                recommendations.append({
                    'action': 'rate_limit_investigation',
                    'reason': flag['detail'],
                    'severity': 'critical',
                    'auto_actionable': False,
                })

        try:
            from core.models_governance import KillSwitch
            expired = KillSwitch.objects.filter(
                is_active=True, expires_at__lt=now,
            )
            expired_count = expired.count()
            if expired_count > 0 and not dry_run:
                for ks in expired:
                    ks.deactivate()
                recommendations.append({
                    'action': 'deactivated_expired_switches',
                    'reason': f'Auto-deactivated {expired_count} expired switches',
                    'severity': 'info',
                    'executed': True,
                })
            elif expired_count > 0:
                recommendations.append({
                    'action': 'deactivate_expired_switches',
                    'reason': f'{expired_count} expired switches need cleanup',
                    'severity': 'info',
                    'executed': False,
                })
        except Exception:
            pass

        return {
            'dry_run': dry_run,
            'risk_summary': {
                'drift_issues': drift.get('issue_count', 0),
                'abuse_flags': abuse.get('flag_count', 0),
                'has_critical': abuse.get('has_critical', False),
            },
            'recommendations': recommendations,
            'recommendation_count': len(recommendations),
            'needs_human_review': any(
                r['severity'] == 'critical' for r in recommendations
            ),
        }

    def get_secrets_scan(self, days: int = 7) -> dict:
        """
        Scan recent content for potential secrets/API key exposure.
        """
        import re

        from django.utils import timezone as tz
        from core.models_deliverables import Deliverable

        now = tz.now()
        window = now - timedelta(days=days)
        findings = []

        deliverables = list(
            Deliverable.objects.filter(
                created_at__gte=window,
            ).only('id', 'title', 'content', 'created_at')[:200]
        )

        for d in deliverables:
            content = d.content or ''
            for pattern in self.SECRETS_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    redacted = [
                        m[:6] + '...' + m[-4:] if len(m) > 10 else '***'
                        for m in matches
                    ]
                    findings.append({
                        'source': 'deliverable',
                        'id': str(d.id),
                        'title': d.title,
                        'pattern': pattern[:20],
                        'match_count': len(matches),
                        'redacted_samples': redacted[:3],
                        'severity': 'critical',
                    })

        try:
            from core.models_unified_system import SelfBlog
            blogs = list(
                SelfBlog.objects.filter(
                    created_at__gte=window,
                ).only('id', 'title', 'content')[:100]
            )
            for b in blogs:
                content = b.content or ''
                for pattern in self.SECRETS_PATTERNS:
                    matches = re.findall(pattern, content)
                    if matches:
                        redacted = [
                            m[:6] + '...' + m[-4:] if len(m) > 10 else '***'
                            for m in matches
                        ]
                        findings.append({
                            'source': 'self_blog',
                            'id': str(b.id),
                            'title': b.title,
                            'pattern': pattern[:20],
                            'match_count': len(matches),
                            'redacted_samples': redacted[:3],
                            'severity': 'critical',
                        })
        except Exception:
            pass

        return {
            'period_days': days,
            'findings': findings,
            'finding_count': len(findings),
            'has_exposure': len(findings) > 0,
            'scanned_deliverables': len(deliverables),
        }

    def evaluate(self, now) -> dict:
        """Auto-evaluate security health for autopilot cycle."""
        drift = self.get_permission_drift_report(hours=6)
        abuse = self.get_abuse_risk_queue(hours=6)

        issues = []
        for issue in drift.get('drift_issues', []):
            if issue.get('severity') in ('warning', 'critical'):
                issues.append(f"drift: {issue['detail']}")
        for flag in abuse.get('flags', []):
            if flag.get('severity') in ('warning', 'critical'):
                issues.append(f"abuse: {flag['detail']}")

        return {
            'drift_issues': drift.get('issue_count', 0),
            'abuse_flags': abuse.get('flag_count', 0),
            'has_critical': abuse.get('has_critical', False),
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


class ComplianceEngine:
    """
    Privacy, data governance & compliance — scans for PII exposure,
    monitors data retention TTLs, audits agent data access patterns,
    and generates compliance summary reports.

    Data sources:
    - Deliverable/SelfBlog: content scanning for PII
    - AgentExecution: agent data access patterns
    - CockpitAuditLog: data mutation audit trail
    - User models: consent/retention tracking

    Guardrails:
    - Read-only analysis — never modifies or deletes data
    - Recommendations only; human approval required for any action
    """

    # PII patterns — conservative regex for common PII types
    PII_PATTERNS = [
        (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn', 'Social Security Number'),
        (r'\b\d{16}\b', 'credit_card_16', 'Credit Card (16 digits)'),
        (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'credit_card', 'Credit Card'),
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email', 'Email Address'),
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone', 'Phone Number'),
    ]

    # Retention thresholds (days) — content older than this should be reviewed
    RETENTION_THRESHOLDS = {
        'agent_execution': 90,
        'audit_log': 180,
        'spider_data': 60,
        'conversation_memory': 365,
    }

    def get_pii_scan(self, days: int = 7, limit: int = 50) -> dict:
        """Scan recent deliverables and blogs for PII patterns."""
        import re
        from django.utils import timezone as tz

        cutoff = tz.now() - timedelta(days=days)
        findings = []

        # Scan Deliverables
        try:
            from core.models_deliverables import Deliverable
            deliverables = list(
                Deliverable.objects.filter(created_at__gte=cutoff)
                .values('id', 'title', 'deliverable_type', 'created_at')
                .order_by('-created_at')[:limit]
            )
            for d in deliverables:
                try:
                    obj = Deliverable.objects.get(id=d['id'])
                    content = str(obj.content or '')
                    for pattern, pii_type, label in self.PII_PATTERNS:
                        matches = re.findall(pattern, content)
                        if matches:
                            findings.append({
                                'source': 'deliverable',
                                'source_id': str(d['id']),
                                'title': d.get('title', ''),
                                'pii_type': pii_type,
                                'pii_label': label,
                                'match_count': len(matches),
                                'created_at': str(d['created_at']),
                            })
                except Exception:
                    continue
        except Exception:
            pass

        # Scan SelfBlogs
        try:
            from core.models_unified_system import SelfBlog
            blogs = list(
                SelfBlog.objects.filter(created_at__gte=cutoff)
                .values('id', 'title', 'created_at')
                .order_by('-created_at')[:limit]
            )
            for b in blogs:
                try:
                    obj = SelfBlog.objects.get(id=b['id'])
                    content = str(getattr(obj, 'content', '') or '')
                    for pattern, pii_type, label in self.PII_PATTERNS:
                        matches = re.findall(pattern, content)
                        if matches:
                            findings.append({
                                'source': 'self_blog',
                                'source_id': str(b['id']),
                                'title': b.get('title', ''),
                                'pii_type': pii_type,
                                'pii_label': label,
                                'match_count': len(matches),
                                'created_at': str(b['created_at']),
                            })
                except Exception:
                    continue
        except Exception:
            pass

        return {
            'period_days': days,
            'findings': findings,
            'finding_count': len(findings),
            'has_pii': len(findings) > 0,
            'by_type': self._group_by_key(findings, 'pii_type'),
        }

    def get_retention_report(self) -> dict:
        """Check data retention compliance across key tables."""
        from django.utils import timezone as tz

        now = tz.now()
        violations = []

        # Check AgentExecution retention
        try:
            from core.models_unified_system import AgentExecution
            threshold = now - timedelta(days=self.RETENTION_THRESHOLDS['agent_execution'])
            old_count = AgentExecution.objects.filter(created_at__lt=threshold).count()
            total = AgentExecution.objects.count()
            if old_count > 0:
                violations.append({
                    'table': 'AgentExecution',
                    'threshold_days': self.RETENTION_THRESHOLDS['agent_execution'],
                    'records_past_retention': old_count,
                    'total_records': total,
                    'severity': 'warning' if old_count < 1000 else 'critical',
                    'recommendation': f'Review {old_count} records older than {self.RETENTION_THRESHOLDS["agent_execution"]} days',
                })
        except Exception:
            pass

        # Check CockpitAuditLog retention
        try:
            from core.models_cockpit_audit import CockpitAuditLog
            threshold = now - timedelta(days=self.RETENTION_THRESHOLDS['audit_log'])
            old_count = CockpitAuditLog.objects.filter(created_at__lt=threshold).count()
            total = CockpitAuditLog.objects.count()
            if old_count > 0:
                violations.append({
                    'table': 'CockpitAuditLog',
                    'threshold_days': self.RETENTION_THRESHOLDS['audit_log'],
                    'records_past_retention': old_count,
                    'total_records': total,
                    'severity': 'warning' if old_count < 500 else 'critical',
                    'recommendation': f'Review {old_count} audit records older than {self.RETENTION_THRESHOLDS["audit_log"]} days',
                })
        except Exception:
            pass

        # Check SpiderData retention
        try:
            from core.models_unified_system import SpiderData
            threshold = now - timedelta(days=self.RETENTION_THRESHOLDS['spider_data'])
            old_count = SpiderData.objects.filter(created_at__lt=threshold).count()
            total = SpiderData.objects.count()
            if old_count > 0:
                violations.append({
                    'table': 'SpiderData',
                    'threshold_days': self.RETENTION_THRESHOLDS['spider_data'],
                    'records_past_retention': old_count,
                    'total_records': total,
                    'severity': 'info' if old_count < 5000 else 'warning',
                    'recommendation': f'Review {old_count} spider records older than {self.RETENTION_THRESHOLDS["spider_data"]} days',
                })
        except Exception:
            pass

        # Check ConversationMemory retention
        try:
            from core.models.conversations import ConversationMemory
            threshold = now - timedelta(days=self.RETENTION_THRESHOLDS['conversation_memory'])
            old_count = ConversationMemory.objects.filter(created_at__lt=threshold).count()
            total = ConversationMemory.objects.count()
            if old_count > 0:
                violations.append({
                    'table': 'ConversationMemory',
                    'threshold_days': self.RETENTION_THRESHOLDS['conversation_memory'],
                    'records_past_retention': old_count,
                    'total_records': total,
                    'severity': 'info',
                    'recommendation': f'Review {old_count} conversation memories older than {self.RETENTION_THRESHOLDS["conversation_memory"]} days',
                })
        except Exception:
            pass

        return {
            'thresholds': self.RETENTION_THRESHOLDS,
            'violations': violations,
            'violation_count': len(violations),
            'has_violations': len(violations) > 0,
        }

    def get_access_audit(self, hours: int = 24) -> dict:
        """Audit agent data access patterns for anomalies."""
        from django.utils import timezone as tz
        from django.db.models import Count

        cutoff = tz.now() - timedelta(hours=hours)
        anomalies = []

        # Check agent execution frequency — flag agents with unusually high activity
        try:
            from core.models_unified_system import AgentExecution
            agent_counts = list(
                AgentExecution.objects.filter(created_at__gte=cutoff)
                .values('agent__name')
                .annotate(exec_count=Count('id'))
                .order_by('-exec_count')[:20]
            )

            if agent_counts:
                avg_count = sum(a['exec_count'] for a in agent_counts) / len(agent_counts)
                for ac in agent_counts:
                    if ac['exec_count'] > avg_count * 3 and ac['exec_count'] > 10:
                        anomalies.append({
                            'type': 'high_frequency_agent',
                            'agent': ac['agent__name'],
                            'exec_count': ac['exec_count'],
                            'average': round(avg_count, 1),
                            'severity': 'warning' if ac['exec_count'] < avg_count * 5 else 'critical',
                            'detail': f"{ac['agent__name']} ran {ac['exec_count']}x (avg {avg_count:.0f})",
                        })
        except Exception as e:
            logger.warning(
                "ops_autopilot.intelligence: high-frequency agent "
                "audit failed (%s: %s) — anomaly report will be missing "
                "high-frequency agent flags",
                type(e).__name__, e,
            )

        # Check audit log for bulk data operations
        try:
            from core.models_cockpit_audit import CockpitAuditLog
            bulk_ops = list(
                CockpitAuditLog.objects.filter(
                    created_at__gte=cutoff,
                    action__in=['bulk_delete', 'bulk_update', 'export', 'data_download'],
                ).values('action', 'user__username', 'created_at')
                .order_by('-created_at')[:20]
            )
            for op in bulk_ops:
                anomalies.append({
                    'type': 'bulk_data_operation',
                    'action': op['action'],
                    'user': op.get('user__username', 'system'),
                    'timestamp': str(op['created_at']),
                    'severity': 'warning',
                    'detail': f"Bulk {op['action']} by {op.get('user__username', 'system')}",
                })
        except Exception as e:
            logger.warning(
                "ops_autopilot.intelligence: bulk_data_operation audit "
                "failed (%s: %s) — anomaly report missing bulk-op flags",
                type(e).__name__, e,
            )

        return {
            'period_hours': hours,
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'has_anomalies': len(anomalies) > 0,
        }

    def get_compliance_report(self) -> dict:
        """Generate comprehensive compliance summary."""
        pii = self.get_pii_scan(days=30)
        retention = self.get_retention_report()
        access = self.get_access_audit(hours=72)

        # Overall risk level
        risk_factors = []
        if pii.get('has_pii'):
            risk_factors.append(f"{pii['finding_count']} PII findings in content")
        if retention.get('has_violations'):
            risk_factors.append(f"{retention['violation_count']} retention policy violations")
        if access.get('has_anomalies'):
            risk_factors.append(f"{access['anomaly_count']} access anomalies")

        if any('critical' in str(v.get('severity', '')) for v in retention.get('violations', [])):
            risk_level = 'high'
        elif risk_factors:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'pii_summary': {
                'findings': pii.get('finding_count', 0),
                'has_pii': pii.get('has_pii', False),
            },
            'retention_summary': {
                'violations': retention.get('violation_count', 0),
                'has_violations': retention.get('has_violations', False),
            },
            'access_summary': {
                'anomalies': access.get('anomaly_count', 0),
                'has_anomalies': access.get('has_anomalies', False),
            },
            'recommendations': risk_factors,
            'healthy': risk_level == 'low',
        }

    def evaluate(self, now) -> dict:
        """Auto-evaluate compliance health for autopilot cycle."""
        pii = self.get_pii_scan(days=7)
        retention = self.get_retention_report()

        issues = []
        if pii.get('has_pii'):
            issues.append(f"PII detected: {pii['finding_count']} findings")
        for v in retention.get('violations', []):
            if v.get('severity') in ('warning', 'critical'):
                issues.append(f"retention: {v['table']} has {v['records_past_retention']} old records")

        return {
            'pii_findings': pii.get('finding_count', 0),
            'retention_violations': retention.get('violation_count', 0),
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }

    @staticmethod
    def _group_by_key(items: list, key: str) -> dict:
        groups: dict[str, int] = {}
        for item in items:
            k = item.get(key, 'unknown')
            groups[k] = groups.get(k, 0) + 1
        return groups


class DataIntegrityEngine:
    """
    Data quality, schema drift & contract testing — monitors spider feeds
    for null/zero spikes, duplicate explosions, stale loads, and maintains
    per-source data reliability scores.

    Data sources:
    - SpiderData: primary data feed quality
    - AgentExecution: execution output quality
    - Deliverable: content quality metrics

    Guardrails:
    - Read-only analysis — never quarantines data without approval
    - Recommendations only in v1
    """

    # Thresholds
    NULL_SPIKE_THRESHOLD = 0.3    # >30% nulls in a batch = spike
    DUPLICATE_THRESHOLD = 0.2     # >20% duplicates = explosion
    STALE_HOURS = 48              # No new data in 48h = stale

    def get_quality_report(self, hours: int = 24) -> dict:
        """Overall data quality report across spider feeds."""
        from django.utils import timezone as tz
        from django.db.models import Count, Q

        cutoff = tz.now() - timedelta(hours=hours)
        issues = []
        by_source = {}

        try:
            from core.models_unified_system import SpiderData

            # Per-spider quality stats
            spider_stats = list(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('spider_name')
                .annotate(
                    total=Count('id'),
                    null_content=Count('id', filter=Q(raw_data__isnull=True) | Q(raw_data={})),
                )
                .order_by('-total')[:30]
            )

            for s in spider_stats:
                total = s['total']
                null_count = s['null_content']
                null_rate = null_count / total if total > 0 else 0

                source_info = {
                    'spider': s['spider_name'],
                    'total_records': total,
                    'null_count': null_count,
                    'null_rate': round(null_rate, 3),
                }
                by_source[s['spider_name']] = source_info

                if null_rate > self.NULL_SPIKE_THRESHOLD and total > 5:
                    issues.append({
                        'type': 'null_spike',
                        'spider': s['spider_name'],
                        'null_rate': round(null_rate, 3),
                        'null_count': null_count,
                        'total': total,
                        'severity': 'critical' if null_rate > 0.5 else 'warning',
                        'detail': f"{s['spider_name']}: {null_rate:.0%} null rate ({null_count}/{total})",
                    })

            # Check for overall volume drop
            total_recent = SpiderData.objects.filter(created_at__gte=cutoff).count()
            prev_cutoff = cutoff - timedelta(hours=hours)
            total_prev = SpiderData.objects.filter(
                created_at__gte=prev_cutoff, created_at__lt=cutoff
            ).count()

            volume_change = 0
            if total_prev > 0:
                volume_change = round((total_recent - total_prev) / total_prev, 3)
                if volume_change < -0.5 and total_prev > 20:
                    issues.append({
                        'type': 'volume_drop',
                        'change': volume_change,
                        'current': total_recent,
                        'previous': total_prev,
                        'severity': 'warning',
                        'detail': f"Volume dropped {abs(volume_change):.0%} ({total_prev} → {total_recent})",
                    })

        except Exception:
            pass

        return {
            'period_hours': hours,
            'issues': issues,
            'issue_count': len(issues),
            'sources_checked': len(by_source),
            'by_source': by_source,
            'has_issues': len(issues) > 0,
        }

    def get_null_spike_scan(self, hours: int = 24) -> dict:
        """Scan for null/empty data spikes in spider feeds."""
        from django.utils import timezone as tz
        from django.db.models import Count, Q

        cutoff = tz.now() - timedelta(hours=hours)
        spikes = []

        try:
            from core.models_unified_system import SpiderData

            spider_stats = list(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('spider_name', 'data_type')
                .annotate(
                    total=Count('id'),
                    null_raw=Count('id', filter=Q(raw_data__isnull=True) | Q(raw_data={})),
                    null_processed=Count('id', filter=Q(processed_data__isnull=True) | Q(processed_data={})),
                    null_embedding=Count('id', filter=Q(embedding_text__isnull=True) | Q(embedding_text='')),
                )
                .order_by('-total')
            )

            for s in spider_stats:
                total = s['total']
                if total < 3:
                    continue

                for field, count_key in [
                    ('raw_data', 'null_raw'),
                    ('processed_data', 'null_processed'),
                    ('embedding_text', 'null_embedding'),
                ]:
                    null_count = s[count_key]
                    null_rate = null_count / total if total > 0 else 0
                    if null_rate > self.NULL_SPIKE_THRESHOLD:
                        spikes.append({
                            'spider': s['spider_name'],
                            'data_type': s['data_type'],
                            'field': field,
                            'null_count': null_count,
                            'total': total,
                            'null_rate': round(null_rate, 3),
                            'severity': 'critical' if null_rate > 0.5 else 'warning',
                        })
        except Exception as e:
            logger.warning(
                "ops_autopilot.intelligence: spider null-rate audit "
                "failed (%s: %s) — data-quality spikes report will be "
                "incomplete",
                type(e).__name__, e,
            )

        return {
            'period_hours': hours,
            'spikes': spikes,
            'spike_count': len(spikes),
            'has_spikes': len(spikes) > 0,
        }

    def get_duplicate_report(self, hours: int = 24) -> dict:
        """Detect duplicate data explosions in spider feeds."""
        from django.utils import timezone as tz
        from django.db.models import Count

        cutoff = tz.now() - timedelta(hours=hours)
        duplicates = []

        try:
            from core.models_unified_system import SpiderData

            # Check for duplicate source_urls per spider
            dup_urls = list(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .exclude(source_url__isnull=True)
                .exclude(source_url='')
                .values('spider_name', 'source_url')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .order_by('-count')[:20]
            )

            for d in dup_urls:
                duplicates.append({
                    'spider': d['spider_name'],
                    'source_url': d['source_url'][:100],
                    'duplicate_count': d['count'],
                    'severity': 'warning' if d['count'] < 5 else 'critical',
                })

            # Per-spider duplicate summary
            by_spider: dict[str, int] = {}
            for d in dup_urls:
                spider = d['spider_name']
                by_spider[spider] = by_spider.get(spider, 0) + (d['count'] - 1)

        except Exception:
            by_spider = {}

        return {
            'period_hours': hours,
            'duplicates': duplicates,
            'duplicate_count': len(duplicates),
            'wasted_records': sum(by_spider.values()),
            'by_spider': by_spider,
            'has_duplicates': len(duplicates) > 0,
        }

    def get_reliability_scores(self) -> dict:
        """Calculate per-source reliability scores based on recent quality."""
        from django.utils import timezone as tz
        from django.db.models import Count, Q, Avg

        cutoff_24h = tz.now() - timedelta(hours=24)
        cutoff_7d = tz.now() - timedelta(days=7)
        scores = []

        try:
            from core.models_unified_system import SpiderData

            # 7-day stats per spider
            spider_stats = list(
                SpiderData.objects.filter(created_at__gte=cutoff_7d)
                .values('spider_name')
                .annotate(
                    total_7d=Count('id'),
                    null_7d=Count('id', filter=Q(raw_data__isnull=True) | Q(raw_data={})),
                    recent_24h=Count('id', filter=Q(created_at__gte=cutoff_24h)),
                )
                .order_by('-total_7d')[:40]
            )

            for s in spider_stats:
                total = s['total_7d']
                if total == 0:
                    continue

                null_rate = s['null_7d'] / total
                freshness = 1.0 if s['recent_24h'] > 0 else 0.5
                completeness = 1.0 - null_rate

                # Reliability = 60% completeness + 40% freshness
                reliability = round(completeness * 0.6 + freshness * 0.4, 3)

                scores.append({
                    'spider': s['spider_name'],
                    'reliability_score': reliability,
                    'completeness': round(completeness, 3),
                    'freshness': freshness,
                    'total_7d': total,
                    'recent_24h': s['recent_24h'],
                    'null_rate_7d': round(null_rate, 3),
                    'grade': 'A' if reliability >= 0.9 else 'B' if reliability >= 0.7 else 'C' if reliability >= 0.5 else 'F',
                })

            scores.sort(key=lambda x: x['reliability_score'])
        except Exception:
            pass

        avg_score = round(sum(s['reliability_score'] for s in scores) / len(scores), 3) if scores else 0

        return {
            'scores': scores,
            'source_count': len(scores),
            'average_reliability': avg_score,
            'grade_distribution': {
                'A': sum(1 for s in scores if s['grade'] == 'A'),
                'B': sum(1 for s in scores if s['grade'] == 'B'),
                'C': sum(1 for s in scores if s['grade'] == 'C'),
                'F': sum(1 for s in scores if s['grade'] == 'F'),
            },
        }

    def evaluate(self, now) -> dict:
        """Auto-evaluate data integrity health for autopilot cycle."""
        quality = self.get_quality_report(hours=12)
        duplicates = self.get_duplicate_report(hours=12)

        issues = []
        for issue in quality.get('issues', []):
            if issue.get('severity') in ('warning', 'critical'):
                issues.append(issue.get('detail', str(issue)))
        if duplicates.get('wasted_records', 0) > 10:
            issues.append(f"duplicates: {duplicates['wasted_records']} wasted records")

        return {
            'null_spikes': sum(1 for i in quality.get('issues', []) if i.get('type') == 'null_spike'),
            'duplicate_issues': duplicates.get('duplicate_count', 0),
            'wasted_records': duplicates.get('wasted_records', 0),
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


class ValueRealizationEngine:
    """
    Customer value & outcomes — measures whether users are getting real
    value from the platform by tracking value events, computing outcome
    rates, detecting usage without outcomes.

    Data sources:
    - AgentExecution: agent usage patterns
    - Deliverable: content creation outcomes
    - Revenue: monetization outcomes
    - EngagementEvent: user engagement
    - ClosePack: deal progression

    Guardrails:
    - Read-only analysis — observation and recommendation only
    """

    # Value event categories
    VALUE_CATEGORIES = {
        'agent_usage': 'Agent execution completed successfully',
        'content_created': 'Deliverable created',
        'revenue_generated': 'Revenue recorded',
        'engagement': 'User engagement event',
        'deal_progress': 'Deal/close pack progressed',
    }

    def get_value_events_report(self, days: int = 7) -> dict:
        """Report on value-generating events across the platform."""
        from django.utils import timezone as tz
        from django.db.models import Count

        cutoff = tz.now() - timedelta(days=days)
        events = {}

        # Agent executions (successful)
        try:
            from core.models_unified_system import AgentExecution
            agent_count = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='completed'
            ).count()
            events['agent_completions'] = agent_count

            # Top agents by usage
            top_agents = list(
                AgentExecution.objects.filter(created_at__gte=cutoff, status='completed')
                .values('agent__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            events['top_agents'] = [
                {'agent': a['agent__name'], 'count': a['count']}
                for a in top_agents
            ]
        except Exception:
            events['agent_completions'] = 0

        # Deliverables created
        try:
            from core.models_deliverables import Deliverable
            deliv_count = Deliverable.objects.filter(created_at__gte=cutoff).count()
            events['deliverables_created'] = deliv_count
        except Exception:
            events['deliverables_created'] = 0

        # Revenue recorded
        try:
            from core.models_unified_system import Revenue
            from django.db.models import Sum
            rev = Revenue.objects.filter(created_at__gte=cutoff).aggregate(
                total=Sum('amount'), count=Count('id')
            )
            events['revenue_count'] = rev['count'] or 0
            events['revenue_total'] = float(rev['total'] or 0)
        except Exception:
            events['revenue_count'] = 0
            events['revenue_total'] = 0.0

        # Engagement events
        try:
            from core.models_engagement import EngagementEvent
            eng_count = EngagementEvent.objects.filter(created_at__gte=cutoff).count()
            events['engagement_events'] = eng_count
        except Exception:
            events['engagement_events'] = 0

        # Close packs
        try:
            from core.models_close_pack import ClosePack
            pack_count = ClosePack.objects.filter(created_at__gte=cutoff).count()
            events['close_packs'] = pack_count
        except Exception:
            events['close_packs'] = 0

        total_events = sum([
            events.get('agent_completions', 0),
            events.get('deliverables_created', 0),
            events.get('revenue_count', 0),
            events.get('engagement_events', 0),
            events.get('close_packs', 0),
        ])

        return {
            'period_days': days,
            'events': events,
            'total_value_events': total_events,
        }

    def get_outcome_rates(self, days: int = 30) -> dict:
        """Compute outcome/conversion rates across the value chain."""
        from django.utils import timezone as tz
        from django.db.models import Count

        cutoff = tz.now() - timedelta(days=days)
        rates = {}

        # Agent success rate
        try:
            from core.models_unified_system import AgentExecution
            total = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            completed = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='completed'
            ).count()
            rates['agent_success_rate'] = round(completed / total, 3) if total > 0 else 0
            rates['agent_total'] = total
            rates['agent_completed'] = completed
        except Exception:
            rates['agent_success_rate'] = 0

        # Deliverable quality rate (quality_score > 0.5)
        try:
            from core.models_deliverables import Deliverable
            from django.db.models import Q, Avg
            total = Deliverable.objects.filter(created_at__gte=cutoff).count()
            high_quality = Deliverable.objects.filter(
                created_at__gte=cutoff, quality_score__gt=0.5
            ).count()
            avg_quality = Deliverable.objects.filter(
                created_at__gte=cutoff
            ).aggregate(avg=Avg('quality_score'))['avg']
            rates['deliverable_quality_rate'] = round(high_quality / total, 3) if total > 0 else 0
            rates['deliverable_total'] = total
            rates['deliverable_avg_quality'] = round(float(avg_quality or 0), 3)
        except Exception:
            rates['deliverable_quality_rate'] = 0

        # Outreach → meeting conversion
        try:
            from core.models_outreach import OutreachDraft
            from core.models_meeting import Meeting
            outreach_count = OutreachDraft.objects.filter(created_at__gte=cutoff).count()
            meeting_count = Meeting.objects.filter(created_at__gte=cutoff).count()
            rates['outreach_to_meeting'] = round(meeting_count / outreach_count, 3) if outreach_count > 0 else 0
            rates['outreach_count'] = outreach_count
            rates['meeting_count'] = meeting_count
        except Exception:
            rates['outreach_to_meeting'] = 0

        return {
            'period_days': days,
            'rates': rates,
        }

    def get_usage_gaps(self, days: int = 7) -> dict:
        """Detect areas with high usage but low outcomes."""
        from django.utils import timezone as tz
        from django.db.models import Count

        cutoff = tz.now() - timedelta(days=days)
        gaps = []

        # Agents with high execution count but high failure rate
        try:
            from core.models_unified_system import AgentExecution
            agent_stats = list(
                AgentExecution.objects.filter(created_at__gte=cutoff)
                .values('agent__name')
                .annotate(
                    total=Count('id'),
                    failed=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(status='failed')),
                )
                .filter(total__gte=5)
                .order_by('-total')[:20]
            )
            for s in agent_stats:
                fail_rate = s['failed'] / s['total'] if s['total'] > 0 else 0
                if fail_rate > 0.3:
                    gaps.append({
                        'type': 'high_failure_agent',
                        'agent': s['agent__name'],
                        'total': s['total'],
                        'failed': s['failed'],
                        'fail_rate': round(fail_rate, 3),
                        'severity': 'critical' if fail_rate > 0.5 else 'warning',
                        'detail': f"{s['agent__name']}: {fail_rate:.0%} failure rate ({s['failed']}/{s['total']})",
                    })
        except Exception:
            pass

        # Deliverables with low quality scores
        try:
            from core.models_deliverables import Deliverable
            low_quality = Deliverable.objects.filter(
                created_at__gte=cutoff, quality_score__lt=0.3
            ).count()
            total_deliverables = Deliverable.objects.filter(created_at__gte=cutoff).count()
            if low_quality > 0 and total_deliverables > 0:
                low_rate = low_quality / total_deliverables
                if low_rate > 0.2:
                    gaps.append({
                        'type': 'low_quality_content',
                        'low_quality_count': low_quality,
                        'total': total_deliverables,
                        'low_rate': round(low_rate, 3),
                        'severity': 'warning',
                        'detail': f"{low_rate:.0%} of deliverables have quality < 0.3 ({low_quality}/{total_deliverables})",
                    })
        except Exception:
            pass

        return {
            'period_days': days,
            'gaps': gaps,
            'gap_count': len(gaps),
            'has_gaps': len(gaps) > 0,
        }

    def get_realization_summary(self) -> dict:
        """Comprehensive value realization summary."""
        events = self.get_value_events_report(days=30)
        rates = self.get_outcome_rates(days=30)
        gaps = self.get_usage_gaps(days=7)

        # Overall health assessment
        health_issues = []
        agent_rate = rates.get('rates', {}).get('agent_success_rate', 0)
        if agent_rate < 0.7 and rates.get('rates', {}).get('agent_total', 0) > 10:
            health_issues.append(f"Low agent success rate: {agent_rate:.0%}")
        if gaps.get('has_gaps'):
            health_issues.append(f"{gaps['gap_count']} usage gaps detected")
        if events.get('total_value_events', 0) == 0:
            health_issues.append("No value events in past 30 days")

        return {
            'events_summary': {
                'total': events.get('total_value_events', 0),
                'agents': events.get('events', {}).get('agent_completions', 0),
                'deliverables': events.get('events', {}).get('deliverables_created', 0),
                'revenue': events.get('events', {}).get('revenue_total', 0),
            },
            'outcome_rates': rates.get('rates', {}),
            'gaps': gaps.get('gaps', []),
            'health_issues': health_issues,
            'healthy': len(health_issues) == 0,
        }

    def evaluate(self, now) -> dict:
        """Auto-evaluate value realization health for autopilot cycle."""
        events = self.get_value_events_report(days=7)
        rates = self.get_outcome_rates(days=7)

        issues = []
        agent_rate = rates.get('rates', {}).get('agent_success_rate', 0)
        if agent_rate < 0.7 and rates.get('rates', {}).get('agent_total', 0) > 10:
            issues.append(f"Low agent success rate: {agent_rate:.0%}")
        if events.get('total_value_events', 0) == 0:
            issues.append("No value events in past 7 days")

        return {
            'value_events': events.get('total_value_events', 0),
            'outcome_rate': agent_rate,
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }

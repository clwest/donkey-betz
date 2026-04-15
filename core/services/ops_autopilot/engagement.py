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

class EngagementEngine:
    """
    Captures and classifies inbound prospect engagement (replies,
    meeting bookings, form fills). Routes to appropriate next action.

    Guardrails:
      - Never auto-sends replies — approval required
      - Hard opt-out handling (unsubscribe → permanent suppress)
      - Dedup: one thread per outreach draft
    """

    INTENT_ACTIONS = {
        'positive': 'reply_with_info',
        'neutral': 'reply_with_answer',
        'objection': 'reply_address_objection',
        'meeting': 'book_call',
        'unsubscribe': 'suppress',
        'unknown': 'review_manually',
    }

    def get_inbox(self, now, status_filter='unread') -> dict:
        """PA-facing: engagement events by status."""
        from core.models_engagement import EngagementEvent

        try:
            qs = EngagementEvent.objects.filter(suppressed=False)
            if status_filter != 'all':
                qs = qs.filter(status=status_filter)

            events = list(
                qs.order_by('-created_at').values(
                    'id', 'prospect_name', 'prospect_company',
                    'channel', 'intent', 'status', 'subject_line',
                    'suggested_action', 'created_at',
                )[:20]
            )

            for e in events:
                e['id'] = str(e['id'])
                if hasattr(e.get('created_at'), 'isoformat'):
                    e['created_at'] = e['created_at'].isoformat()

            # Counts
            from django.db.models import Count
            status_counts = dict(
                EngagementEvent.objects.filter(
                    suppressed=False,
                ).values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )

            return {
                'events': events,
                'filter': status_filter,
                'total_unread': status_counts.get('unread', 0),
                'total_needs_reply': status_counts.get('needs_reply', 0),
                'total_classified': status_counts.get('classified', 0),
            }
        except Exception as e:
            return {'error': str(e), 'events': []}

    def classify_event(self, event_id: str, intent: str, summary: str = '') -> dict:
        """Classify an engagement event's intent."""
        from core.models_engagement import EngagementEvent

        try:
            event = EngagementEvent.objects.get(id=event_id)
        except EngagementEvent.DoesNotExist:
            return {'error': f'Event {event_id} not found'}

        if event.suppressed:
            return {'error': 'Event is suppressed (opt-out)'}

        event.intent = intent
        if summary:
            event.summary = summary
        event.suggested_action = self.INTENT_ACTIONS.get(intent, 'review_manually')
        event.status = 'classified'

        # Auto-suppress unsubscribe
        if intent == 'unsubscribe':
            event.suppressed = True
            event.status = 'closed'

        event.save()

        return {
            'classified': True,
            'event_id': str(event.id),
            'intent': intent,
            'suggested_action': event.suggested_action,
            'suppressed': event.suppressed,
        }

    def draft_reply(self, event_id: str, reply_text: str) -> dict:
        """Set a draft reply for approval."""
        from core.models_engagement import EngagementEvent

        try:
            event = EngagementEvent.objects.get(id=event_id)
        except EngagementEvent.DoesNotExist:
            return {'error': f'Event {event_id} not found'}

        if event.suppressed:
            return {'error': 'Cannot reply — prospect opted out'}

        event.draft_reply = reply_text
        event.status = 'needs_reply'
        event.save()

        return {
            'drafted': True,
            'event_id': str(event.id),
            'status': 'needs_reply',
        }

    def approve_reply(self, event_id: str, edited_text: str = '') -> dict:
        """Approve a draft reply (optionally with edits)."""
        from core.models_engagement import EngagementEvent

        try:
            event = EngagementEvent.objects.get(
                id=event_id, status='needs_reply',
            )
        except EngagementEvent.DoesNotExist:
            return {'error': f'Event {event_id} not found or not in needs_reply status'}

        if edited_text:
            event.edited_reply = edited_text

        event.status = 'actioned'
        event.save()

        return {
            'approved': True,
            'event_id': str(event.id),
            'reply_text': edited_text or event.draft_reply,
        }

    def disqualify(self, event_id: str, reason: str = '') -> dict:
        """Disqualify an engagement."""
        from core.models_engagement import EngagementEvent

        try:
            event = EngagementEvent.objects.get(id=event_id)
        except EngagementEvent.DoesNotExist:
            return {'error': f'Event {event_id} not found'}

        event.status = 'disqualified'
        event.disqualify_reason = reason
        event.save()

        return {
            'disqualified': True,
            'event_id': str(event.id),
            'reason': reason,
        }

    def get_metrics_report(self, now) -> dict:
        """PA-facing: engagement funnel metrics."""
        from core.models_engagement import EngagementEvent
        from django.db.models import Count

        try:
            total = EngagementEvent.objects.filter(suppressed=False).count()
            by_status = dict(
                EngagementEvent.objects.filter(
                    suppressed=False,
                ).values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )
            by_intent = dict(
                EngagementEvent.objects.filter(
                    suppressed=False,
                ).values_list('intent').annotate(
                    c=Count('id'),
                ).values_list('intent', 'c')
            )
            by_channel = dict(
                EngagementEvent.objects.filter(
                    suppressed=False,
                ).values_list('channel').annotate(
                    c=Count('id'),
                ).values_list('channel', 'c')
            )

            # Conversion: actioned / total
            actioned = by_status.get('actioned', 0) + by_status.get('closed', 0)
            conversion_pct = (actioned / total * 100) if total > 0 else 0

            suppressed_count = EngagementEvent.objects.filter(
                suppressed=True,
            ).count()

            return {
                'total': total,
                'by_status': by_status,
                'by_intent': by_intent,
                'by_channel': by_channel,
                'conversion_pct': round(conversion_pct, 1),
                'suppressed': suppressed_count,
            }
        except Exception as e:
            return {'error': str(e)}

    def evaluate(self, now) -> dict:
        """Policy evaluation — auto-close stale events, report stats."""
        from core.models_engagement import EngagementEvent

        result = {
            'unread': 0,
            'needs_reply': 0,
            'stale_closed': 0,
        }

        try:
            result['unread'] = EngagementEvent.objects.filter(
                status='unread', suppressed=False,
            ).count()
            result['needs_reply'] = EngagementEvent.objects.filter(
                status='needs_reply', suppressed=False,
            ).count()

            # Auto-close classified events older than 30 days with no action
            stale_cutoff = now - timedelta(days=30)
            stale_closed = EngagementEvent.objects.filter(
                status__in=['unread', 'classified'],
                created_at__lt=stale_cutoff,
                suppressed=False,
            ).update(status='closed')
            result['stale_closed'] = stale_closed

        except Exception as e:
            result['error'] = str(e)

        return result


# ═══════════════════════════════════════════════════════════════════════
# Meeting Engine — Policy 29 (Autonomy #25)
# ═══════════════════════════════════════════════════════════════════════

class MeetingEngine:
    """
    Tracks meetings from scheduling through follow-up.
    Generates pre-call briefs with prospect context.

    Guardrails:
      - No auto-sending (recap drafts need approval)
      - Manual-first v1 (no calendar integration)
      - Brief auto-generated before meeting
    """

    def create_meeting(
        self, opportunity_id: str, scheduled_at: str,
        title: str = '', channel: str = 'zoom',
        duration_minutes: int = 30, meeting_link: str = '',
        prospect_name: str = '', prospect_company: str = '',
        attendees: list = None,
    ) -> dict:
        """Create a meeting for an opportunity."""
        from core.models_meeting import Meeting
        from django.utils.dateparse import parse_datetime

        dt = parse_datetime(scheduled_at)
        if not dt:
            return {'error': f'Invalid datetime: {scheduled_at}'}

        try:
            opp_id = opportunity_id if opportunity_id else None
            meeting = Meeting.objects.create(
                opportunity_id=opp_id,
                title=title or f'Meeting with {prospect_name or "prospect"}',
                scheduled_at=dt,
                duration_minutes=duration_minutes,
                channel=channel,
                meeting_link=meeting_link,
                prospect_name=prospect_name,
                prospect_company=prospect_company,
                attendees=attendees or [],
            )
            return {
                'meeting_id': str(meeting.id),
                'title': meeting.title,
                'scheduled_at': dt.isoformat(),
                'channel': channel,
                'status': 'scheduled',
            }
        except Exception as e:
            return {'error': str(e)}

    def get_inbox(self, now, filter_type='upcoming') -> dict:
        """PA-facing: meetings by filter type."""
        from core.models_meeting import Meeting
        from django.db.models import Count

        try:
            if filter_type == 'upcoming':
                qs = Meeting.objects.filter(
                    scheduled_at__gte=now,
                    status__in=['scheduled', 'briefed'],
                ).order_by('scheduled_at')
            elif filter_type == 'needs_brief':
                qs = Meeting.objects.filter(
                    scheduled_at__gte=now,
                    status='scheduled',
                    brief_text='',
                ).order_by('scheduled_at')
            elif filter_type == 'past_needs_followup':
                qs = Meeting.objects.filter(
                    scheduled_at__lt=now,
                    status='completed',
                ).order_by('-scheduled_at')
            else:
                qs = Meeting.objects.all().order_by('-scheduled_at')

            meetings = list(
                qs.values(
                    'id', 'title', 'scheduled_at', 'channel',
                    'prospect_name', 'prospect_company', 'status',
                    'duration_minutes',
                )[:20]
            )

            for m in meetings:
                m['id'] = str(m['id'])
                if hasattr(m.get('scheduled_at'), 'isoformat'):
                    m['scheduled_at'] = m['scheduled_at'].isoformat()

            status_counts = dict(
                Meeting.objects.values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )

            return {
                'meetings': meetings,
                'filter': filter_type,
                'total_scheduled': status_counts.get('scheduled', 0),
                'total_completed': status_counts.get('completed', 0),
                'total_no_show': status_counts.get('no_show', 0),
            }
        except Exception as e:
            return {'error': str(e), 'meetings': []}

    def generate_brief(self, meeting_id: str) -> dict:
        """Generate a pre-call brief for a meeting."""
        from core.models_meeting import Meeting

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            return {'error': f'Meeting {meeting_id} not found'}

        lines = [f"# Pre-Call Brief: {meeting.title}"]
        lines.append(f"\n## Meeting Details")
        lines.append(f"- **When:** {meeting.scheduled_at.strftime('%A, %B %d at %I:%M %p')}")
        lines.append(f"- **Duration:** {meeting.duration_minutes} minutes")
        lines.append(f"- **Channel:** {meeting.get_channel_display()}")
        if meeting.meeting_link:
            lines.append(f"- **Link:** {meeting.meeting_link}")

        lines.append(f"\n## Prospect")
        lines.append(f"- **Name:** {meeting.prospect_name or 'Unknown'}")
        lines.append(f"- **Company:** {meeting.prospect_company or 'Unknown'}")

        if meeting.engagement_id:
            try:
                from core.models_engagement import EngagementEvent
                eng = EngagementEvent.objects.get(id=meeting.engagement_id)
                if eng.extracted_fields:
                    fields = eng.extracted_fields
                    if fields.get('need'):
                        lines.append(f"- **Need:** {fields['need']}")
                    if fields.get('budget_cues'):
                        lines.append(f"- **Budget cues:** {fields['budget_cues']}")
            except Exception as _e:
                logger.warning(
                    "engagement.generate_brief: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        lines.append(f"\n## Suggested Agenda")
        lines.append("1. Introduction and rapport (2 min)")
        lines.append("2. Understand current situation (5 min)")
        lines.append("3. Pain points and goals (10 min)")
        lines.append("4. Present relevant solution (8 min)")
        lines.append("5. Q&A and objection handling (5 min)")

        lines.append(f"\n## Discovery Questions")
        lines.append("- What's your biggest challenge right now?")
        lines.append("- What have you tried so far?")
        lines.append("- What does success look like for you?")
        lines.append("- What's your timeline for a solution?")
        lines.append("- Who else is involved in the decision?")

        lines.append(f"\n## Definition of Done")
        lines.append("- Prospect confirms interest in specific offer")
        lines.append("- Agreement on next step (proposal, trial, follow-up)")
        lines.append("- Clear timeline established")

        brief = '\n'.join(lines)
        meeting.brief_text = brief
        meeting.brief_generated_at = timezone.now()
        meeting.status = 'briefed'
        meeting.save()

        return {
            'meeting_id': str(meeting.id),
            'brief_generated': True,
            'brief_preview': brief[:500],
        }

    def add_recap(
        self, meeting_id: str, notes: str = '',
        outcome: str = '', next_steps: str = '',
    ) -> dict:
        """Add post-meeting notes, outcome, and draft recap."""
        from core.models_meeting import Meeting

        try:
            meeting = Meeting.objects.get(id=meeting_id)
        except Meeting.DoesNotExist:
            return {'error': f'Meeting {meeting_id} not found'}

        if notes:
            meeting.notes = notes
        if outcome:
            meeting.outcome = outcome
        if next_steps:
            meeting.next_steps = next_steps

        recap_lines = [f"# Meeting Recap: {meeting.title}"]
        recap_lines.append(f"\nThank you for taking the time to meet!")
        if notes:
            recap_lines.append(f"\n## Summary\n{notes}")
        if next_steps:
            recap_lines.append(f"\n## Next Steps\n{next_steps}")
        recap_lines.append(f"\nLooking forward to our continued conversation.")

        meeting.recap_draft = '\n'.join(recap_lines)
        meeting.status = 'completed'
        meeting.save()

        return {
            'meeting_id': str(meeting.id),
            'status': 'completed',
            'outcome': outcome,
            'recap_preview': meeting.recap_draft[:300],
        }

    def get_metrics_report(self, now) -> dict:
        """PA-facing: meeting pipeline metrics."""
        from core.models_meeting import Meeting
        from django.db.models import Count

        try:
            total = Meeting.objects.count()
            by_status = dict(
                Meeting.objects.values_list('status').annotate(
                    c=Count('id'),
                ).values_list('status', 'c')
            )
            by_outcome = dict(
                Meeting.objects.exclude(
                    outcome='',
                ).values_list('outcome').annotate(
                    c=Count('id'),
                ).values_list('outcome', 'c')
            )

            completed = by_status.get('completed', 0) + by_status.get('followed_up', 0)
            no_show = by_status.get('no_show', 0)
            show_rate = (
                completed / (completed + no_show) * 100
            ) if (completed + no_show) > 0 else 0

            return {
                'total': total,
                'by_status': by_status,
                'by_outcome': by_outcome,
                'upcoming': by_status.get('scheduled', 0) + by_status.get('briefed', 0),
                'show_rate_pct': round(show_rate, 1),
            }
        except Exception as e:
            return {'error': str(e)}

    def evaluate(self, now) -> dict:
        """Policy evaluation — flag meetings needing briefs, stale follow-ups."""
        from core.models_meeting import Meeting

        result = {
            'upcoming': 0,
            'needs_brief': 0,
            'past_no_followup': 0,
        }

        try:
            result['upcoming'] = Meeting.objects.filter(
                scheduled_at__gte=now,
                status__in=['scheduled', 'briefed'],
            ).count()

            brief_cutoff = now + timedelta(hours=24)
            result['needs_brief'] = Meeting.objects.filter(
                scheduled_at__lte=brief_cutoff,
                scheduled_at__gte=now,
                status='scheduled',
                brief_text='',
            ).count()

            followup_cutoff = now - timedelta(hours=48)
            result['past_no_followup'] = Meeting.objects.filter(
                status='completed',
                scheduled_at__lt=followup_cutoff,
            ).count()

        except Exception as e:
            result['error'] = str(e)

        return result


# ═══════════════════════════════════════════════════════════════════════
# Attribution Debt Controller — Policy 14 (Session 1090, Autonomy #10)
# ═══════════════════════════════════════════════════════════════════════

class EngagementAutonomyEngine:
    """
    Automates engagement lifecycle: SLA tracking for reply queue,
    auto-meeting suggestions for positive/meeting intent, engagement-to-
    meeting conversion tracking, and reply context assembly.

    Sits on top of EngagementEngine, adding:
    - SLA-aware reply queue with time-since-receipt
    - Auto-meeting booking suggestions for high-intent events
    - Conversion funnel from engagement → meeting → deal
    - Reply context builder (outreach, opportunity, meeting history)
    """

    # SLA thresholds (hours)
    SLA_WARNING_HOURS = 4    # Flag after 4h without reply
    SLA_CRITICAL_HOURS = 24  # Critical after 24h
    SLA_BREACH_HOURS = 48    # SLA breach after 48h

    def get_sla_queue(self, now=None) -> dict:
        """
        Events needing reply, ranked by SLA urgency.
        Shows time-since-receipt and SLA status.
        """
        from core.models_engagement import EngagementEvent

        now = now or timezone.now()

        # Events that need action (unread, classified, needs_reply)
        events = list(
            EngagementEvent.objects.filter(
                status__in=['unread', 'classified', 'needs_reply'],
                suppressed=False,
            ).order_by('created_at').values(
                'id', 'prospect_name', 'prospect_company', 'channel',
                'intent', 'status', 'subject_line', 'created_at',
            )[:30]
        )

        for e in events:
            e['id'] = str(e['id'])
            created = e.get('created_at')
            if created:
                age_hours = (now - created).total_seconds() / 3600
                e['age_hours'] = round(age_hours, 1)
                if age_hours >= self.SLA_BREACH_HOURS:
                    e['sla_status'] = 'breach'
                elif age_hours >= self.SLA_CRITICAL_HOURS:
                    e['sla_status'] = 'critical'
                elif age_hours >= self.SLA_WARNING_HOURS:
                    e['sla_status'] = 'warning'
                else:
                    e['sla_status'] = 'ok'
                e['created_at'] = created.isoformat()

        # Counts by SLA status
        breach = len([e for e in events if e.get('sla_status') == 'breach'])
        critical = len([e for e in events if e.get('sla_status') == 'critical'])
        warning = len([e for e in events if e.get('sla_status') == 'warning'])

        return {
            'events': events,
            'total': len(events),
            'breach': breach,
            'critical': critical,
            'warning': warning,
            'ok': len(events) - breach - critical - warning,
        }

    def get_meeting_suggestions(self, now=None) -> dict:
        """
        Engagement events with meeting/positive intent that should
        be converted to meetings. Shows which events need meeting creation.
        """
        from core.models_engagement import EngagementEvent
        from core.models_meeting import Meeting

        now = now or timezone.now()

        # Events with meeting or positive intent, not yet actioned
        candidates = list(
            EngagementEvent.objects.filter(
                intent__in=['meeting', 'positive'],
                status__in=['unread', 'classified', 'needs_reply'],
                suppressed=False,
            ).order_by('-created_at').values(
                'id', 'prospect_name', 'prospect_company',
                'prospect_role', 'channel', 'intent', 'status',
                'subject_line', 'opportunity_id', 'created_at',
            )[:20]
        )

        # Check which already have meetings linked via opportunity
        for c in candidates:
            c['id'] = str(c['id'])
            c['has_meeting'] = False
            opp_id = c.get('opportunity_id')
            if opp_id:
                c['opportunity_id'] = str(opp_id)
                c['has_meeting'] = Meeting.objects.filter(
                    opportunity_id=opp_id,
                    status__in=['scheduled', 'briefed'],
                ).exists()
            if hasattr(c.get('created_at'), 'isoformat'):
                c['created_at'] = c['created_at'].isoformat()

        needs_meeting = [c for c in candidates if not c['has_meeting']]

        return {
            'candidates': candidates,
            'needs_meeting': needs_meeting,
            'needs_meeting_count': len(needs_meeting),
            'already_booked': len(candidates) - len(needs_meeting),
        }

    def get_conversion_report(self, days: int = 30) -> dict:
        """
        Engagement → meeting → deal conversion metrics.
        """
        from core.models_engagement import EngagementEvent
        from core.models_meeting import Meeting
        from core.models_close_pack import ClosePack
        from django.db.models import Count

        now = timezone.now()
        since = now - timedelta(days=days)

        # Total engagements
        total = EngagementEvent.objects.filter(
            created_at__gte=since, suppressed=False,
        ).count()

        # By intent
        by_intent = dict(
            EngagementEvent.objects.filter(
                created_at__gte=since, suppressed=False,
            ).values_list('intent').annotate(
                c=Count('id'),
            ).values_list('intent', 'c')
        )

        # Actioned (replied)
        actioned = EngagementEvent.objects.filter(
            created_at__gte=since, status='actioned',
        ).count()

        # Meetings created from engagements
        meetings_from_engagement = Meeting.objects.filter(
            engagement__isnull=False,
            created_at__gte=since,
        ).count()

        # Meetings completed
        meetings_completed = Meeting.objects.filter(
            engagement__isnull=False,
            created_at__gte=since,
            status='completed',
        ).count()

        # Deal packs from opportunities linked to engagements
        eng_opp_ids = list(
            EngagementEvent.objects.filter(
                created_at__gte=since,
                opportunity_id__isnull=False,
            ).values_list('opportunity_id', flat=True).distinct()[:100]
        )
        deals_from_engagement = ClosePack.objects.filter(
            opportunity_id__in=eng_opp_ids,
        ).count()

        # Conversion rates
        reply_rate = round(actioned / total * 100, 1) if total > 0 else 0
        meeting_rate = round(meetings_from_engagement / total * 100, 1) if total > 0 else 0
        deal_rate = round(deals_from_engagement / total * 100, 1) if total > 0 else 0

        # Average response time (for actioned events)
        actioned_events = EngagementEvent.objects.filter(
            created_at__gte=since, status='actioned',
        ).values('created_at', 'updated_at')[:100]
        response_times = []
        for e in actioned_events:
            if e.get('created_at') and e.get('updated_at'):
                hours = (e['updated_at'] - e['created_at']).total_seconds() / 3600
                response_times.append(hours)
        avg_response_hours = (
            round(sum(response_times) / len(response_times), 1)
            if response_times else 0
        )

        return {
            'period_days': days,
            'total_engagements': total,
            'by_intent': by_intent,
            'actioned': actioned,
            'reply_rate_pct': reply_rate,
            'meetings_from_engagement': meetings_from_engagement,
            'meetings_completed': meetings_completed,
            'meeting_conversion_pct': meeting_rate,
            'deals_from_engagement': deals_from_engagement,
            'deal_conversion_pct': deal_rate,
            'avg_response_hours': avg_response_hours,
        }

    def evaluate(self, now) -> dict:
        """
        Auto-evaluate engagement health for autopilot cycle.
        """
        from core.models_engagement import EngagementEvent

        # SLA breaches
        breach_cutoff = now - timedelta(hours=self.SLA_BREACH_HOURS)
        sla_breaches = EngagementEvent.objects.filter(
            status__in=['unread', 'classified', 'needs_reply'],
            suppressed=False,
            created_at__lt=breach_cutoff,
        ).count()

        # Events needing reply (unactioned positive/meeting intent)
        high_intent_unactioned = EngagementEvent.objects.filter(
            intent__in=['meeting', 'positive'],
            status__in=['unread', 'classified'],
            suppressed=False,
        ).count()

        # Overall queue size
        queue_size = EngagementEvent.objects.filter(
            status__in=['unread', 'classified', 'needs_reply'],
            suppressed=False,
        ).count()

        issues = []
        if sla_breaches > 0:
            issues.append(f'{sla_breaches} engagement SLA breaches (>{self.SLA_BREACH_HOURS}h)')
        if high_intent_unactioned > 3:
            issues.append(f'{high_intent_unactioned} high-intent events unactioned')
        if queue_size > 20:
            issues.append(f'Engagement queue backlog: {queue_size} events')

        return {
            'sla_breaches': sla_breaches,
            'high_intent_unactioned': high_intent_unactioned,
            'queue_size': queue_size,
            'issues': issues,
            'issue_count': len(issues),
            'healthy': len(issues) == 0,
        }


# ── Policy 35: Growth & Distribution Autonomy ─────────────────────────────────



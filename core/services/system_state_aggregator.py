"""
Session 573: System State Aggregator Service

Aggregates attention items from all 3 main UI sections (Command Center, Autonomous, Research)
and provides a unified view of what needs attention across the entire platform.

This allows the PA to proactively surface what requires action without the user
manually checking each section.

Architecture:
    - Queries each section for attention items
    - Priority-scores and deduplicates items
    - Caches results (60s TTL) for performance
    - Conditionally injects into PA context
"""

import hashlib
import logging
from dataclasses import dataclass, asdict
from datetime import timedelta
from typing import List, Dict, Any, Optional

from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone

logger = logging.getLogger(__name__)

# Cache key for aggregated state
SYSTEM_STATE_CACHE_KEY = 'system_state_aggregator:attention_items'
SYSTEM_STATE_CACHE_TTL = 60  # 60 seconds


@dataclass
class AttentionItem:
    """
    A single item that needs user attention.

    Session 663: Enhanced with explanation, recommended_action, severity
    to support SystemIntelligenceAgent providing rich context to users.
    """
    id: str
    section: str        # 'command_center', 'autonomous', 'research'
    category: str       # 'alert', 'health', 'overdue', 'stale', etc.
    priority: int       # 1-100 (higher = more urgent)
    title: str
    summary: str
    action_url: str = ''
    # Session 663: New fields for SystemIntelligenceAgent
    explanation: str = ''           # What this metric means in plain English
    recommended_action: str = ''    # What the user can do about it
    severity: str = 'info'          # 'info', 'warning', 'critical'
    location: str = ''              # UI location: "Intelligence > Decisions"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_rich_context(self) -> str:
        """Format as rich context string for agent consumption."""
        parts = [f"**{self.title}**"]
        if self.location:
            parts.append(f"Location: {self.location}")
        parts.append(f"Summary: {self.summary}")
        if self.explanation:
            parts.append(f"Context: {self.explanation}")
        if self.recommended_action:
            parts.append(f"Recommended: {self.recommended_action}")
        if self.action_url:
            parts.append(f"Action URL: {self.action_url}")
        return "\n".join(parts)


# Priority base scores by category
PRIORITY_SCORES = {
    'critical_alert': 90,
    'security_alert': 85,
    'pending_review': 82,    # Session 589: Added for decision pending review (renamed from execution_gap)
    'health_failure': 80,
    'execution_failure': 75,
    'overdue_task': 70,
    'recurring_concern': 65,
    'stale_concern': 60,
    'pending_decision': 50,
    'opportunity': 40,
    'informational': 20,
}


class SystemStateAggregator:
    """
    Aggregates attention items from Command Center, Autonomous, and Research sections.

    Usage:
        aggregator = SystemStateAggregator()
        items = aggregator.get_attention_items()
        urgent = aggregator.get_urgent_items()  # priority >= 80
    """

    def __init__(self, use_cache: bool = True):
        """
        Initialize the aggregator.

        Args:
            use_cache: Whether to use Redis caching (default True)
        """
        self.use_cache = use_cache
        self.logger = logging.getLogger(f"{__name__}.SystemStateAggregator")

    def get_attention_items(self, max_per_section: int = 5, force_refresh: bool = False) -> List[AttentionItem]:
        """
        Get all attention items across sections, sorted by priority.

        Args:
            max_per_section: Maximum items per section (default 5)
            force_refresh: Skip cache and query fresh (default False)

        Returns:
            List of AttentionItem objects sorted by priority (descending)
        """
        # Check cache first
        if self.use_cache and not force_refresh:
            cached = cache.get(SYSTEM_STATE_CACHE_KEY)
            if cached:
                self.logger.debug("Returning cached attention items")
                return [AttentionItem(**item) for item in cached]

        # Collect from each section
        items = []

        try:
            items.extend(self._get_command_center_items(max_per_section))
        except Exception as e:
            self.logger.error(f"Error getting Command Center items: {e}")

        try:
            items.extend(self._get_autonomous_items(max_per_section))
        except Exception as e:
            self.logger.error(f"Error getting Autonomous items: {e}")

        try:
            items.extend(self._get_research_items(max_per_section))
        except Exception as e:
            self.logger.error(f"Error getting Research items: {e}")

        # Session 589: Add pending review monitoring
        try:
            items.extend(self._get_pending_review_items())
        except Exception as e:
            self.logger.error(f"Error getting Pending Review items: {e}")

        # Session 709: Add body system health monitoring
        try:
            items.extend(self._get_body_system_items())
        except Exception as e:
            self.logger.error(f"Error getting Body System items: {e}")

        # Session 970: Add deliberation session health
        try:
            items.extend(self._get_deliberation_items())
        except Exception as e:
            self.logger.error(f"Error getting Deliberation items: {e}")

        # Session 970: Add signal cluster freshness
        try:
            items.extend(self._get_signal_cluster_items())
        except Exception as e:
            self.logger.error(f"Error getting Signal Cluster items: {e}")

        # Deduplicate by hashing title+summary
        seen_hashes = set()
        unique_items = []
        for item in items:
            item_hash = hashlib.md5(f"{item.title}{item.summary}".encode()).hexdigest()[:16]
            if item_hash not in seen_hashes:
                seen_hashes.add(item_hash)
                unique_items.append(item)

        # Sort by priority (descending)
        unique_items.sort(key=lambda x: x.priority, reverse=True)

        # Cache the results
        if self.use_cache:
            cache.set(
                SYSTEM_STATE_CACHE_KEY,
                [item.to_dict() for item in unique_items],
                SYSTEM_STATE_CACHE_TTL
            )

        self.logger.info(f"Aggregated {len(unique_items)} attention items across sections")
        return unique_items

    def get_urgent_items(self, threshold: int = 80) -> List[AttentionItem]:
        """
        Get only urgent items (priority >= threshold).

        Args:
            threshold: Minimum priority (default 80)

        Returns:
            List of urgent AttentionItem objects
        """
        all_items = self.get_attention_items()
        return [item for item in all_items if item.priority >= threshold]

    def has_urgent_items(self, threshold: int = 80) -> bool:
        """Quick check if there are any urgent items."""
        return len(self.get_urgent_items(threshold)) > 0

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of attention items for quick display.

        Returns:
            Dict with counts and top items per section
        """
        items = self.get_attention_items()

        summary = {
            'total_items': len(items),
            'urgent_count': len([i for i in items if i.priority >= 80]),
            'by_section': {
                'command_center': [],
                'autonomous': [],
                'research': []
            },
            'top_3': [item.to_dict() for item in items[:3]]
        }

        for item in items:
            if len(summary['by_section'].get(item.section, [])) < 3:
                summary['by_section'][item.section].append(item.to_dict())

        return summary

    # =========================================================================
    # SECTION-SPECIFIC QUERY METHODS
    # =========================================================================

    def _get_command_center_items(self, limit: int = 5) -> List[AttentionItem]:
        """
        Get attention items from Command Center section.

        Checks:
        - Failed autonomous thinking cycles (24h)
        - Recurring/stale concerns
        - System health issues
        """
        items = []
        now = timezone.now()

        try:
            from core.models_unified_system import ThoughtRecord, TrackedConcern

            # 1. Failed thinking cycles in last 24h
            failed_cycles = ThoughtRecord.objects.filter(
                execution_status='error',
                started_at__gte=now - timedelta(hours=24)
            ).order_by('-started_at')[:limit]

            for cycle in failed_cycles:
                items.append(AttentionItem(
                    id=f"thought_{cycle.id}",
                    section='command_center',
                    category='execution_failure',
                    priority=PRIORITY_SCORES['execution_failure'],
                    title=f"Thinking Cycle Failed",
                    summary=f"Cycle from {cycle.started_at.strftime('%H:%M')} failed: {(cycle.observations or '')[:80]}",
                    action_url='/ai-studio/?tab=autonomous',
                    explanation="A scheduled thinking cycle encountered an error. Thinking cycles are "
                               "autonomous processes where agents analyze data, generate insights, and learn.",
                    recommended_action="Check the Autonomous tab for error details. The system will "
                                      "retry automatically, but persistent failures may need investigation.",
                    severity='warning',
                    location='Command Center > Autonomous'
                ))

            # 2. Recurring concerns (came back after being resolved)
            recurring = TrackedConcern.objects.filter(
                status='recurring'
            ).order_by('-updated_at')[:limit]

            for concern in recurring:
                items.append(AttentionItem(
                    id=f"concern_recurring_{concern.id}",
                    section='command_center',
                    category='recurring_concern',
                    priority=PRIORITY_SCORES['recurring_concern'],
                    title=f"Recurring: {concern.concern_text[:40]}...",
                    summary=f"Detected {concern.times_detected}x in {concern.category}",
                    action_url='/ai-studio/?tab=autonomous&subtab=thinking',
                    explanation="This concern was previously resolved but has reappeared. Recurring "
                               "issues often indicate a root cause that wasn't fully addressed.",
                    recommended_action="Investigate the underlying cause. Consider creating a permanent "
                                      "fix or policy to prevent recurrence.",
                    severity='warning',
                    location='Command Center > Thinking'
                ))

            # 3. Stale concerns (active > 7 days)
            stale_threshold = now - timedelta(days=7)
            stale = TrackedConcern.objects.filter(
                status='active',
                created_at__lt=stale_threshold
            ).order_by('-times_detected')[:limit]

            for concern in stale:
                items.append(AttentionItem(
                    id=f"concern_stale_{concern.id}",
                    section='command_center',
                    category='stale_concern',
                    priority=PRIORITY_SCORES['stale_concern'],
                    title=f"Stale: {concern.concern_text[:40]}...",
                    summary=f"Active for {concern.days_active} days, no resolution",
                    action_url='/ai-studio/?tab=autonomous&subtab=thinking',
                    explanation="This concern has been open for over a week without resolution. "
                               "Long-standing issues may indicate complexity or deprioritization.",
                    recommended_action="Either resolve the concern, mark it as won't-fix with a reason, "
                                      "or escalate if it requires additional resources.",
                    severity='info',
                    location='Command Center > Thinking'
                ))

        except ImportError as e:
            self.logger.warning(f"Could not import Command Center models: {e}")
        except Exception as e:
            self.logger.error(f"Error querying Command Center: {e}")

        return items[:limit]

    def _get_autonomous_items(self, limit: int = 5) -> List[AttentionItem]:
        """
        Get attention items from Autonomous section.

        Checks:
        - Content channels overdue for content
        - Unverified narrative shifts
        - Critical trigger events
        - Failed autonomous actions
        """
        items = []
        now = timezone.now()

        try:
            # 1. Overdue content channels
            from core.models_autonomous_studio import ContentChannel

            overdue_channels = ContentChannel.objects.filter(
                status='active',
                next_content_due__lt=now
            ).order_by('next_content_due')[:limit]

            for channel in overdue_channels:
                hours_overdue = (now - channel.next_content_due).total_seconds() / 3600
                priority = PRIORITY_SCORES['overdue_task']
                if hours_overdue > 24:
                    priority += 10  # Boost priority if very overdue

                items.append(AttentionItem(
                    id=f"channel_{channel.id}",
                    section='autonomous',
                    category='overdue_task',
                    priority=min(priority, 95),
                    title=f"Overdue: {channel.name[:30]}",
                    summary=f"Content due {int(hours_overdue)}h ago",
                    action_url='/ai-studio/?tab=autonomous&subtab=content-studio'
                ))

        except ImportError:
            pass  # Content studio models may not exist

        try:
            # 2. Unverified narrative shifts
            from core.models_narrative_drift import NarrativeShift

            unverified_shifts = NarrativeShift.objects.filter(
                verified=False,
                detected_at__gte=now - timedelta(days=7)
            ).order_by('-confidence')[:limit]

            for shift in unverified_shifts:
                items.append(AttentionItem(
                    id=f"shift_{shift.id}",
                    section='autonomous',
                    category='pending_decision',
                    priority=PRIORITY_SCORES['pending_decision'] + int(float(shift.confidence or 0) * 20),
                    title=f"Narrative Shift: {shift.narrative.title[:30] if shift.narrative else 'Unknown'}",
                    summary=f"From '{shift.old_status}' to '{shift.new_status}' ({int(float(shift.confidence or 0) * 100)}% confidence)",
                    action_url='/ai-studio/?tab=autonomous&subtab=narrative'
                ))

        except ImportError:
            pass  # Narrative models may not exist

        try:
            # 3. Critical trigger events
            from core.models_situation_triggers import SituationTriggerEvent

            critical_events = SituationTriggerEvent.objects.filter(
                status='pending',
                severity__in=['critical', 'high'],
                created_at__gte=now - timedelta(days=3)
            ).order_by('-created_at')[:limit]

            for event in critical_events:
                priority = PRIORITY_SCORES['critical_alert'] if event.severity == 'critical' else PRIORITY_SCORES['security_alert']
                items.append(AttentionItem(
                    id=f"trigger_{event.id}",
                    section='autonomous',
                    category='critical_alert',
                    priority=priority,
                    title=f"Trigger: {event.event_type[:30]}",
                    summary=f"{event.severity.upper()}: {event.description[:60]}",
                    action_url='/ai-studio/?tab=autonomous&subtab=triggers'
                ))

        except ImportError:
            pass  # Trigger models may not exist

        try:
            # 4. Failed autonomous actions (last 24h)
            from core.models_unified_system import AutonomousAction

            failed_actions = AutonomousAction.objects.filter(
                status='failed',
                created_at__gte=now - timedelta(hours=24)
            ).order_by('-created_at')[:limit]

            for action in failed_actions:
                items.append(AttentionItem(
                    id=f"action_{action.id}",
                    section='autonomous',
                    category='execution_failure',
                    priority=PRIORITY_SCORES['execution_failure'],
                    title=f"Failed: {action.action_type}",
                    summary=f"{action.reasoning[:60] if action.reasoning else 'No details'}",
                    action_url='/ai-studio/?tab=autonomous&subtab=actions'
                ))

        except ImportError:
            pass

        return items[:limit]

    def _get_research_items(self, limit: int = 5) -> List[AttentionItem]:
        """
        Get attention items from Research section.

        Checks:
        - Stale spiders (no data in 24h for active spiders)
        - High-value opportunities not yet acted on
        - Knowledge gaps detected
        """
        items = []
        now = timezone.now()

        try:
            from core.models_unified_system import SpiderData

            # 1. Check for stale spider categories
            # Get categories that had data recently vs those that are stale
            recent_threshold = now - timedelta(hours=24)

            # Count recent data by spider_name
            recent_sources = SpiderData.objects.filter(
                created_at__gte=recent_threshold
            ).values('spider_name').annotate(count=Count('id'))

            recent_source_names = {s['spider_name'] for s in recent_sources if s['spider_name']}

            # Expected active sources (critical spiders that should have data)
            expected_sources = [
                'hackernews', 'techcrunch', 'reddit', 'coingecko',
                'adzuna', 'remoteok', 'weworkremotely', 'newsapi'
            ]

            stale_sources = [s for s in expected_sources if s not in recent_source_names]

            if stale_sources:
                items.append(AttentionItem(
                    id='spider_stale',
                    section='research',
                    category='stale_concern',
                    priority=PRIORITY_SCORES['stale_concern'],
                    title=f"Stale Spiders ({len(stale_sources)})",
                    summary=f"No data in 24h: {', '.join(stale_sources[:3])}{'...' if len(stale_sources) > 3 else ''}",
                    action_url='/ai-studio/?tab=intel&subtab=spiders'
                ))

        except ImportError:
            pass

        try:
            # 2. High-value pending dreams not yet shown/decided
            from core.models_unified_system import AgentDream

            # Dreams that haven't been shown to user yet with high scores
            pending_dreams = AgentDream.objects.filter(
                shown_to_user=False,
                composite_score__gte=0.75,
                dreamed_at__gte=now - timedelta(days=7)
            ).order_by('-composite_score')[:limit]

            for dream in pending_dreams:
                items.append(AttentionItem(
                    id=f"dream_{dream.id}",
                    section='research',
                    category='opportunity',
                    priority=PRIORITY_SCORES['opportunity'] + int((dream.composite_score or 0) * 20),
                    title=f"Dream: {(dream.title or dream.content[:30])[:35]}",
                    summary=f"From {dream.agent.name if dream.agent else 'Unknown'} (score: {dream.composite_score:.0%})",
                    action_url='/ai-studio/?tab=social&subtab=dreams'
                ))

        except ImportError:
            pass

        try:
            # 3. Pending boardroom decisions
            from core.models_unified_system import AgentDecisionSummary

            pending_decisions = AgentDecisionSummary.objects.filter(
                is_canonical=False,
                created_at__gte=now - timedelta(days=7)
            ).order_by('-created_at')[:limit]

            for decision in pending_decisions:
                # Session 574: Strip existing prefixes to avoid "Decision: Decision: ..."
                clean_topic = decision.topic or 'Untitled'
                # Strip multiple nested prefixes
                prefixes = ['Decision: ', 'Panel: ', 'Research: ', 'Research topic: ', 'Discussion: ', '[Learned] ', 'Test: ']
                changed = True
                while changed:
                    changed = False
                    for prefix in prefixes:
                        if clean_topic.startswith(prefix):
                            clean_topic = clean_topic[len(prefix):]
                            changed = True
                            break

                # Session 574: Skip items with short/meaningless topics
                if len(clean_topic.strip()) < 15:
                    continue

                items.append(AttentionItem(
                    id=f"decision_{decision.id}",
                    section='research',
                    category='pending_decision',
                    priority=PRIORITY_SCORES['pending_decision'],
                    title=f"Boardroom: {clean_topic[:50]}",
                    summary=f"{decision.decision_type}: awaiting review",
                    action_url='/ai-studio/?tab=decisions&subtab=pending'
                ))

        except ImportError:
            pass

        return items[:limit]

    def _get_pending_review_items(self) -> List[AttentionItem]:
        """
        Session 589: Get attention items for pending review (agent decisions awaiting action).

        This monitors agent-generated decisions that haven't been reviewed yet.
        Note: High percentages are normal - agents generate many suggestions,
        only important ones need promotion to canonical.

        Checks:
        - Percentage of decisions in DRAFT status (> 70% triggers informational alert)
        - Stale drafts (decisions > 7 days old)
        - Auto-promotable decisions that could reduce backlog
        """
        items = []

        try:
            from core.services.decision_promotion_rules import get_pending_review_metrics

            metrics = get_pending_review_metrics()
            review = metrics.get('pending_review', {})
            age_dist = metrics.get('age_distribution', {})
            auto_promotable = metrics.get('auto_promotable', {})

            review_pct = review.get('draft_percentage', 0)
            stale_count = age_dist.get('7_to_30_days', 0) + age_dist.get('over_30_days', 0)
            promotable_count = auto_promotable.get('count', 0)

            # Alert if > 70% pending (informational, not critical)
            if review_pct > 70:
                items.append(AttentionItem(
                    id='pending_review_backlog',
                    section='autonomous',
                    category='pending_review',
                    priority=PRIORITY_SCORES['pending_review'],
                    title=f"Pending Review: {review_pct:.0f}%",
                    summary=f"{review.get('draft_count', 0)} agent suggestions in draft, {review.get('canonical_count', 0)} promoted to canonical.",
                    action_url='/ai-studio/?tab=decisions&subtab=pending',
                    explanation="This metric shows agent-generated suggestions awaiting human review. "
                               "Agents continuously generate ideas, insights, and recommendations. "
                               "High percentages are normal and expected - only the most valuable "
                               "suggestions should be promoted to 'canonical' status.",
                    recommended_action="Review high-value suggestions in the Decisions tab, or run "
                                      "auto-promotion to clear low-risk guidelines automatically.",
                    severity='info',
                    location='Intelligence > Decisions'
                ))

            # Alert if many stale decisions
            if stale_count > 50:
                items.append(AttentionItem(
                    id='pending_review_stale',
                    section='autonomous',
                    category='stale_concern',
                    priority=PRIORITY_SCORES['stale_concern'] + 5,  # Boost slightly
                    title=f"Stale Suggestions: {stale_count}",
                    summary=f"{stale_count} agent suggestions are over 7 days old.",
                    action_url='/ai-studio/?tab=decisions&subtab=pending',
                    explanation="These suggestions have been waiting for review for over a week. "
                               "Old suggestions may no longer be relevant as the system has evolved.",
                    recommended_action="Archive or reject outdated suggestions, or batch-review "
                                      "to clear the backlog. Consider enabling auto-archival for old drafts.",
                    severity='warning',
                    location='Intelligence > Decisions'
                ))

            # Opportunity: auto-promotable decisions available
            if promotable_count > 0:
                items.append(AttentionItem(
                    id='pending_review_promotable',
                    section='autonomous',
                    category='opportunity',
                    priority=PRIORITY_SCORES['opportunity'] + 15,  # Higher priority opportunity
                    title=f"Auto-Promotable: {promotable_count}",
                    summary=f"{promotable_count} low-risk guidelines are ready for automatic promotion.",
                    action_url='/ai-studio/?tab=decisions&subtab=auto-promote',
                    explanation="These are low-risk guideline suggestions that meet the criteria "
                               "for automatic promotion (aged 24+ hours, low-impact areas like "
                               "prompting, product, or workflow improvements).",
                    recommended_action="Run the auto-promotion process to clear these automatically, "
                                      "or review them manually if you prefer hands-on approval.",
                    severity='info',
                    location='Intelligence > Decisions > Auto-Promote'
                ))

        except ImportError as e:
            self.logger.debug(f"Decision promotion rules not available: {e}")
        except Exception as e:
            self.logger.error(f"Error getting pending review metrics: {e}")

        return items

    def _get_body_system_items(self) -> List[AttentionItem]:
        """
        Session 709: Get attention items from body systems (HEART, LUNGS, IMMUNE, etc).

        This monitors the 7 body systems and generates alerts for:
        - Critical health issues (HEART critical/offline)
        - Budget exhaustion (LUNGS < 20%)
        - Security threats (IMMUNE high/severe threat level)
        - Data pipeline issues (DIGESTIVE blocked/bloated)
        - Agent execution problems (MUSCULAR strained/paralyzed)
        """
        items = []

        try:
            from core.services.body_vitals import get_body_vitals_service
            vitals_service = get_body_vitals_service()
            all_vitals = vitals_service.get_all_vitals()

            systems = all_vitals.get('systems', {})

            # ===== HEART - Core Component Health =====
            heart = systems.get('heart', {})
            heart_status = heart.get('status', 'unknown')
            heart_score = heart.get('score', 100)

            if heart_status in ['critical', 'offline']:
                items.append(AttentionItem(
                    id=f'body_heart_{heart_status}',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'],
                    title=f"HEART: {heart_status.upper()}",
                    summary=f"System health score: {heart_score}% - core components need attention",
                    action_url='/ai-studio/',
                    explanation="The HEART system monitors core platform components (brain, organs, "
                               "sensory, memory). Critical status means multiple components are failing.",
                    recommended_action="Check service status, restart failing services, "
                                      "and review logs for errors.",
                    severity='critical',
                    location='Body Health Dashboard'
                ))
            elif heart_status == 'degraded' and heart_score < 70:
                items.append(AttentionItem(
                    id='body_heart_degraded',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'] - 10,
                    title=f"HEART: Degraded ({heart_score}%)",
                    summary=f"Some platform components are unhealthy",
                    action_url='/ai-studio/',
                    explanation="The HEART system shows degraded status. Some components "
                               "may be experiencing issues.",
                    recommended_action="Monitor system health and check component status.",
                    severity='warning',
                    location='Body Health Dashboard'
                ))

            # ===== LUNGS - Budget/Resource Management =====
            lungs = systems.get('lungs', {})
            oxygen_level = lungs.get('oxygen_level', 100)
            lungs_status = lungs.get('status', 'normal')

            if oxygen_level < 10:
                items.append(AttentionItem(
                    id='body_lungs_exhausted',
                    section='body_systems',
                    category='critical_alert',
                    priority=PRIORITY_SCORES['critical_alert'],
                    title=f"LUNGS: Budget Exhausted ({oxygen_level}%)",
                    summary="API budget nearly depleted - operations may be blocked",
                    action_url='/ai-studio/',
                    explanation="The LUNGS system tracks API token and cost budgets. "
                               "Below 10% means operations should be restricted.",
                    recommended_action="Reduce LLM usage immediately, increase budget, "
                                      "or wait for budget reset.",
                    severity='critical',
                    location='Body Health Dashboard > LUNGS'
                ))
            elif oxygen_level < 20:
                items.append(AttentionItem(
                    id='body_lungs_low',
                    section='body_systems',
                    category='critical_alert',
                    priority=PRIORITY_SCORES['critical_alert'] - 5,
                    title=f"LUNGS: Budget Low ({oxygen_level}%)",
                    summary="API budget running low - consider reducing usage",
                    action_url='/ai-studio/',
                    explanation="Budget is below 20%. Expensive operations should be avoided.",
                    recommended_action="Use efficient models (GPT-4o-mini, Haiku), "
                                      "avoid video generation and batch operations.",
                    severity='warning',
                    location='Body Health Dashboard > LUNGS'
                ))

            # ===== IMMUNE - Security/Threat Detection =====
            immune = systems.get('immune', {})
            threat_level = immune.get('threat_level', 'none')
            immune_score = immune.get('score', 100)

            if threat_level in ['high', 'severe']:
                items.append(AttentionItem(
                    id=f'body_immune_{threat_level}',
                    section='body_systems',
                    category='security_alert',
                    priority=PRIORITY_SCORES['security_alert'],
                    title=f"IMMUNE: {threat_level.upper()} Threat Level",
                    summary=f"Active security threats detected - review immediately",
                    action_url='/ai-studio/',
                    explanation="The IMMUNE system has detected active security threats. "
                               "This may include rate abuse, authentication attacks, or injection attempts.",
                    recommended_action="Review threat logs, check quarantine list, "
                                      "and consider blocking suspicious IPs/users.",
                    severity='critical',
                    location='Body Health Dashboard > IMMUNE'
                ))
            elif threat_level == 'elevated':
                items.append(AttentionItem(
                    id='body_immune_elevated',
                    section='body_systems',
                    category='security_alert',
                    priority=PRIORITY_SCORES['security_alert'] - 10,
                    title="IMMUNE: Elevated Threat Level",
                    summary="Security monitoring shows elevated activity",
                    action_url='/ai-studio/',
                    explanation="Some suspicious activity has been detected but not at critical levels.",
                    recommended_action="Monitor threat logs for any escalation.",
                    severity='warning',
                    location='Body Health Dashboard > IMMUNE'
                ))

            # ===== DIGESTIVE - Data Pipeline =====
            digestive = systems.get('digestive', {})
            digestive_status = digestive.get('status', 'healthy')
            digestive_score = digestive.get('score', 100)

            if digestive_status in ['blocked', 'starving']:
                items.append(AttentionItem(
                    id=f'body_digestive_{digestive_status}',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'],
                    title=f"DIGESTIVE: {digestive_status.upper()}",
                    summary="Data ingestion pipeline has stopped",
                    action_url='/ai-studio/',
                    explanation="The DIGESTIVE system processes spider data. "
                               "Blocked means the pipeline has stopped processing.",
                    recommended_action="Check Celery workers, review spider execution logs, "
                                      "clear any stuck queue items.",
                    severity='critical',
                    location='Body Health Dashboard > DIGESTIVE'
                ))
            elif digestive_status == 'bloated':
                items.append(AttentionItem(
                    id='body_digestive_bloated',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'] - 10,
                    title="DIGESTIVE: Queue Backlog",
                    summary=f"Data pipeline has significant backlog (score: {digestive_score}%)",
                    action_url='/ai-studio/',
                    explanation="The processing queue is backing up. "
                               "Data may be arriving faster than it's being processed.",
                    recommended_action="Check Celery worker capacity, consider scaling workers.",
                    severity='warning',
                    location='Body Health Dashboard > DIGESTIVE'
                ))

            # ===== MUSCULAR - Agent Execution =====
            muscular = systems.get('muscular', {})
            muscular_status = muscular.get('status', 'strong')
            muscular_score = muscular.get('score', 100)

            if muscular_status == 'paralyzed':
                items.append(AttentionItem(
                    id='body_muscular_paralyzed',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'] - 5,
                    title="MUSCULAR: No Agent Activity",
                    summary="Agents are not executing tasks",
                    action_url='/ai-studio/',
                    explanation="The MUSCULAR system tracks agent execution. "
                               "Paralyzed status means no recent agent activity.",
                    recommended_action="Run some agent tasks to warm up the system. "
                                      "This may be normal during low-activity periods.",
                    severity='warning',
                    location='Body Health Dashboard > MUSCULAR'
                ))
            elif muscular_status == 'strained':
                items.append(AttentionItem(
                    id='body_muscular_strained',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'] - 15,
                    title=f"MUSCULAR: Agent Strain ({muscular_score}%)",
                    summary="Agent execution showing high error rates",
                    action_url='/ai-studio/',
                    explanation="Agents are experiencing more failures than normal.",
                    recommended_action="Check agent logs for common errors, "
                                      "review failed executions.",
                    severity='warning',
                    location='Body Health Dashboard > MUSCULAR'
                ))

            # ===== CIRCULATORY - Data Flow (only critical) =====
            circulatory = systems.get('circulatory', {})
            circ_status = circulatory.get('status', 'flowing')

            if circ_status == 'blocked':
                items.append(AttentionItem(
                    id='body_circulatory_blocked',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'],
                    title="CIRCULATORY: Data Flow Blocked",
                    summary="Redis/Celery data flow has stopped",
                    action_url='/ai-studio/',
                    explanation="Data is not flowing through the system. "
                               "This affects all real-time processing.",
                    recommended_action="Check Redis server, restart Celery workers, "
                                      "review queue depths.",
                    severity='critical',
                    location='Body Health Dashboard > CIRCULATORY'
                ))

            # ===== SPINE - API Routing (only critical) =====
            spine = systems.get('spine', {})
            spine_status = spine.get('status', 'aligned')

            if spine_status == 'injured':
                items.append(AttentionItem(
                    id='body_spine_injured',
                    section='body_systems',
                    category='health_failure',
                    priority=PRIORITY_SCORES['health_failure'],
                    title="SPINE: API Routing Failure",
                    summary="Multiple API routes are failing",
                    action_url='/ai-studio/',
                    explanation="The SPINE system shows API routing is severely degraded. "
                               "This affects the ability to serve requests.",
                    recommended_action="Check API error logs, review failing endpoints, "
                                      "restart the Django server if needed.",
                    severity='critical',
                    location='Body Health Dashboard > SPINE'
                ))

        except ImportError as e:
            self.logger.debug(f"Body vitals service not available: {e}")
        except Exception as e:
            self.logger.error(f"Error getting body system items: {e}")

        return items

    def _get_deliberation_items(self, limit: int = 5) -> List[AttentionItem]:
        """
        Session 970: Get attention items from deliberation sessions.

        Checks:
        - Failed or stuck deliberation sessions (status != completed, older than 1h)
        - Sessions with 0 contracts (decision enforcement gap)
        """
        items = []
        now = timezone.now()

        try:
            from core.models_deliberation import DeliberationSession, ContractRecord

            # 1. Stuck sessions (not completed after 1 hour)
            stuck = DeliberationSession.objects.filter(
                status__in=['in_progress', 'pending'],
                created_at__lt=now - timedelta(hours=1)
            ).order_by('-created_at')[:limit]

            for session in stuck:
                age_hours = (now - session.created_at).total_seconds() / 3600
                items.append(AttentionItem(
                    id=f'deliberation_stuck_{session.id}',
                    section='autonomous',
                    category='stale_concern',
                    priority=PRIORITY_SCORES['stale_concern'] + 5,
                    title=f"Stuck Deliberation ({age_hours:.0f}h)",
                    summary=f"Session '{(session.objective or '')[:50]}' still {session.status}",
                    action_url='/ai-studio/?tab=orchestration&subtab=monitor',
                    explanation="A deliberation session has not completed within the expected timeframe.",
                    recommended_action="Check orchestration logs. The session may need to be "
                                      "manually completed or cancelled.",
                    severity='warning',
                    location='Workspace > Orchestration > Monitor'
                ))

            # 2. Completed sessions with no contracts (decision gap)
            no_contract_sessions = DeliberationSession.objects.filter(
                status='completed',
                created_at__gte=now - timedelta(hours=24)
            ).exclude(
                id__in=ContractRecord.objects.values_list('session_id', flat=True)
            ).count()

            if no_contract_sessions > 0:
                items.append(AttentionItem(
                    id='deliberation_no_contracts',
                    section='autonomous',
                    category='pending_decision',
                    priority=PRIORITY_SCORES['pending_decision'] + 5,
                    title=f"Contractless Deliberations: {no_contract_sessions}",
                    summary=f"{no_contract_sessions} completed session(s) in 24h produced no contracts",
                    action_url='/ai-studio/?tab=orchestration&subtab=monitor',
                    explanation="Deliberation sessions completed without generating execution "
                               "or synthesis contracts, meaning no actionable decisions were captured.",
                    recommended_action="Review recent sessions in the Orchestration Monitor. "
                                      "Check if decision enforcement is working correctly.",
                    severity='info',
                    location='Workspace > Orchestration > Monitor'
                ))

        except ImportError:
            pass

        return items

    def _get_signal_cluster_items(self, limit: int = 5) -> List[AttentionItem]:
        """
        Session 970: Get attention items from signal clusters.

        Checks:
        - Stale active clusters (no update in 48h)
        - High-strength signals not yet triggering conversations
        """
        items = []
        now = timezone.now()

        try:
            from core.models_signal_intelligence import SignalCluster

            # 1. Stale active clusters (active but not detected in 48h)
            stale_threshold = now - timedelta(hours=48)
            stale_clusters = SignalCluster.objects.filter(
                status='active',
                detected_at__lt=stale_threshold
            ).count()

            if stale_clusters > 0:
                items.append(AttentionItem(
                    id='signal_clusters_stale',
                    section='research',
                    category='stale_concern',
                    priority=PRIORITY_SCORES['stale_concern'],
                    title=f"Stale Signal Clusters: {stale_clusters}",
                    summary=f"{stale_clusters} active cluster(s) not detected in 48h",
                    action_url='/ai-studio/?tab=intel&subtab=signals',
                    explanation="Signal clusters aggregate spider data into actionable patterns. "
                               "Stale clusters may indicate spider data flow issues.",
                    recommended_action="Check spider execution status. Run signal aggregation "
                                      "manually if needed: manage.py run_signal_aggregation.",
                    severity='info',
                    location='Intel > Signals'
                ))

            # 2. High-strength detecting clusters not yet triggered
            untriggered = SignalCluster.objects.filter(
                status='detecting',
                strength__gte=0.7
            ).count()

            if untriggered >= 3:
                items.append(AttentionItem(
                    id='signal_clusters_untriggered',
                    section='research',
                    category='opportunity',
                    priority=PRIORITY_SCORES['opportunity'] + 10,
                    title=f"Strong Untriggered Signals: {untriggered}",
                    summary=f"{untriggered} high-strength clusters awaiting conversation trigger",
                    action_url='/ai-studio/?tab=intel&subtab=signals',
                    explanation="Multiple signal clusters with strength >= 0.7 are in 'detecting' "
                               "status but haven't triggered agent conversations yet.",
                    recommended_action="Review signal clusters and manually trigger conversations "
                                      "for the strongest patterns, or lower the trigger threshold.",
                    severity='info',
                    location='Intel > Signals'
                ))

        except ImportError:
            pass

        return items

    def format_for_pa_context(self, max_items: int = 10) -> str:
        """
        Format attention items as text for PA context injection.

        Args:
            max_items: Maximum items to include

        Returns:
            Formatted string for prompt injection
        """
        items = self.get_attention_items()[:max_items]

        if not items:
            return ""

        urgent = [i for i in items if i.priority >= 80]
        important = [i for i in items if 50 <= i.priority < 80]

        parts = ["## System Attention Required"]

        if urgent:
            parts.append("\n### URGENT (needs immediate attention):")
            for item in urgent[:5]:
                parts.append(f"- [{item.section.upper()}] {item.title}: {item.summary}")

        if important:
            parts.append("\n### Important:")
            for item in important[:5]:
                parts.append(f"- [{item.section}] {item.title}: {item.summary}")

        parts.append("\nYou can proactively mention these items when relevant to the user's query.")

        return "\n".join(parts)


# Singleton instance
_system_state_aggregator = None


def get_system_state_aggregator() -> SystemStateAggregator:
    """Get or create the singleton SystemStateAggregator instance."""
    global _system_state_aggregator
    if _system_state_aggregator is None:
        _system_state_aggregator = SystemStateAggregator()
    return _system_state_aggregator

"""
Session 854: Content Voice & Narrative System
==============================================

This module provides:
1. VoiceProfile - Brand identity and founder voice storage
2. NarrativeInjectionService - Pulls real incidents from system logs
3. CTALibrary - Strong calls-to-action for different contexts
4. FlagshipBlogTemplate - The new content generation pattern

The goal: Transform "Gen-1 Polished Generic" into "unmistakably Donkey Betz"
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


# =============================================================================
# VOICE PROFILE - The Donkey Betz Brand Identity
# =============================================================================

@dataclass
class VoiceProfile:
    """
    The unique voice of Donkey Betz / Chris West.

    This isn't a generic AI startup - this is a personal journey of building
    something through challenges, with hard-won lessons and authentic struggles.
    """

    # Core identity
    brand_name: str = "Donkey Betz"
    founder_name: str = "Chris"
    tagline: str = "AI-Powered Intelligence Platform Built Through Hell"

    # The origin story - what makes this different
    origin_story: str = """
    Donkey Betz didn't start in a Silicon Valley boardroom. It started with
    one person - Chris - who got tired of watching AI promise everything and
    deliver PowerPoints. So he built something real. Agents that actually work.
    Dreams that actually execute. A system that learns from every failure
    (and there were plenty).

    This isn't another "AI will change everything" platform. This is the result
    of thousands of hours debugging at 3am, of watching agents fail spectacularly
    and learning from it, of building the infrastructure that most people
    talk about but never ship.
    """

    # Voice characteristics
    tone_attributes: List[str] = None

    # Signature phrases that make content feel authentic
    signature_phrases: List[str] = None

    # Things we explicitly DON'T do
    anti_patterns: List[str] = None

    # Hard-won wisdom (real lessons, not fictional stories)
    lessons_learned: List[str] = None

    def __post_init__(self):
        if self.tone_attributes is None:
            self.tone_attributes = [
                "Direct - no corporate fluff",
                "Technical but accessible - we explain without condescension",
                "Honest about failures - they're how we learned",
                "Pragmatic - what actually works, not what sounds good",
                "Passionate but not hype-bro - genuine enthusiasm",
                "Builder-first - we ship, then talk about it",
            ]

        if self.signature_phrases is None:
            self.signature_phrases = [
                "Built this through hell",
                "Not another PowerPoint",
                "Agents that actually work",
                "Dreams that actually execute",
                "Learn from every failure",
                "The hard way is the only way that sticks",
                "Ship first, optimize later",
                "Real data, real decisions, real results",
                "Watch it happen in real-time",
                "The system remembers",
            ]

        if self.anti_patterns is None:
            self.anti_patterns = [
                "Don't say 'revolutionary' - show the revolution",
                "Don't say 'cutting-edge' - show the edge",
                "Don't promise 'AI will...' - show what it DID",
                "Don't use 'leverage' as a verb",
                "Don't be vague - specific numbers, specific outcomes",
                "Don't hide failures - they're the best stories",
                "Don't sound like every other AI startup",
            ]

        # Session 913: Removed fictional struggles (e.g., "The Great Agent Rebellion of 2025")
        # Real incidents are now pulled from NarrativeInjectionService instead

        if self.lessons_learned is None:
            self.lessons_learned = [
                "Agents need to fail safely, not never fail",
                "Memory is more important than intelligence",
                "The best orchestration is invisible",
                "Users don't want AI - they want outcomes",
                "Every metric lies until you watch it in production",
                "Self-healing systems aren't optional, they're survival",
                "The boring infrastructure is what makes magic possible",
            ]

    def get_voice_injection(self) -> str:
        """Get a random voice element to inject into content."""
        elements = []

        # Add a signature phrase
        elements.append(f"Signature phrase to work in naturally: \"{random.choice(self.signature_phrases)}\"")

        # Session 913: Removed fictional struggle stories
        # Real incidents are now injected via NarrativeInjectionService in FlagshipBlogTemplate

        # Add a lesson
        elements.append(f"Hard-won lesson: {random.choice(self.lessons_learned)}")

        return "\n".join(elements)

    def get_anti_pattern_check(self) -> str:
        """Get anti-patterns to avoid."""
        return "AVOID: " + " | ".join(random.sample(self.anti_patterns, min(3, len(self.anti_patterns))))


# =============================================================================
# NARRATIVE INJECTION SERVICE - Pull Real Incidents from the System
# =============================================================================

class NarrativeInjectionService:
    """
    Session 951: Enhanced with topic relevance, diversity constraints, and fallbacks.

    Pulls real incidents from system logs to inject into content.

    These are the concrete examples that make content memorable:
    "Last week, Agent X noticed Y, triggered Z, and within 14 minutes the system rerouted..."

    Improvements (Session 951):
    - Topic relevance gating: Only inject incidents matching post topic/domain
    - Diversity constraints: Max 1 incident per type to prevent dominance
    - Fallback incidents: Generic "build in public" moments when DB is empty
    - Domain tagging: Each incident tagged with relevant domains
    """

    # Domain keywords for topic matching
    DOMAIN_KEYWORDS = {
        'ai': ['ai', 'agent', 'llm', 'gpt', 'machine learning', 'neural', 'model', 'automation'],
        'finance': ['stock', 'market', 'trading', 'investment', 'crypto', 'bitcoin', 'portfolio'],
        'sports': ['sports', 'betting', 'odds', 'nba', 'nfl', 'mlb', 'game', 'team', 'player'],
        'tech': ['software', 'code', 'developer', 'api', 'infrastructure', 'system', 'platform'],
        'content': ['blog', 'content', 'writing', 'podcast', 'video', 'media', 'publish'],
        'business': ['startup', 'revenue', 'growth', 'customer', 'product', 'market'],
    }

    # Fallback incidents when database has no real ones
    FALLBACK_INCIDENTS = [
        {
            'type': 'learning',
            'title': 'System Evolution',
            'narrative': "Every week, the system processes thousands of decisions. Each one teaches "
                        "something - which patterns work, which fail, what users actually need. "
                        "This isn't static software; it's a learning organism.",
            'domain': ['ai', 'tech'],
            'is_fallback': True,
        },
        {
            'type': 'decision',
            'title': 'Autonomous Decision-Making',
            'narrative': "When faced with ambiguous data, the system doesn't freeze. It weighs options, "
                        "considers confidence levels, and makes a call. Sometimes wrong, always learning.",
            'domain': ['ai', 'tech'],
            'is_fallback': True,
        },
        {
            'type': 'recovery',
            'title': 'Resilience by Design',
            'narrative': "Failures happen - APIs timeout, models hallucinate, data gets messy. "
                        "The difference is what happens next: automatic retry, graceful degradation, "
                        "and a learning record so it doesn't happen the same way twice.",
            'domain': ['tech', 'ai'],
            'is_fallback': True,
        },
    ]

    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=30)

    def get_recent_incidents(self, limit: int = 5, topic: str = None) -> List[Dict[str, Any]]:
        """
        Get recent notable incidents from the system.

        Args:
            limit: Maximum incidents to return
            topic: Optional topic for relevance filtering

        Returns:
            List of incidents, filtered by topic relevance if provided
        """
        incidents = []

        try:
            # Get agent recovery stories
            incidents.extend(self._get_agent_recoveries(limit=2))

            # Get dream executions
            incidents.extend(self._get_dream_stories(limit=2))

            # Get learning moments
            incidents.extend(self._get_learning_moments(limit=2))

            # Get decision outcomes
            incidents.extend(self._get_decision_outcomes(limit=2))

            # Session 951: Spider discoveries removed - they're routine telemetry, not incidents

        except Exception as e:
            logger.warning(f"Error fetching incidents: {e}")

        # Session 951: Apply topic relevance filtering if topic provided
        if topic and incidents:
            incidents = self._filter_by_topic_relevance(incidents, topic)

        # Session 951: Apply diversity constraints - max 1 per type
        incidents = self._apply_diversity_constraints(incidents)

        # Session 951: Add fallback incidents if we have none
        if not incidents:
            incidents = self._get_fallback_incidents(topic, limit)

        # Shuffle and return
        random.shuffle(incidents)
        return incidents[:limit]

    def _detect_topic_domain(self, topic: str) -> List[str]:
        """Detect which domains a topic belongs to."""
        if not topic:
            return []

        topic_lower = topic.lower()
        matched_domains = []

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in topic_lower for kw in keywords):
                matched_domains.append(domain)

        return matched_domains if matched_domains else ['general']

    def _filter_by_topic_relevance(
        self,
        incidents: List[Dict[str, Any]],
        topic: str
    ) -> List[Dict[str, Any]]:
        """
        Filter incidents to only those relevant to the topic.

        If no incidents match, returns all incidents (better than empty).
        """
        topic_domains = self._detect_topic_domain(topic)

        if not topic_domains or topic_domains == ['general']:
            return incidents  # No filtering if we can't detect domain

        relevant = []
        for incident in incidents:
            incident_domains = incident.get('domain', [])
            if not incident_domains:
                # Infer domain from agent name or title
                incident_domains = self._infer_incident_domain(incident)

            # Check for domain overlap
            if any(d in topic_domains for d in incident_domains):
                relevant.append(incident)

        # Return relevant if we have any, otherwise return all
        return relevant if relevant else incidents

    def _infer_incident_domain(self, incident: Dict[str, Any]) -> List[str]:
        """Infer domain from incident content."""
        text = f"{incident.get('title', '')} {incident.get('narrative', '')} {incident.get('agent', '')}".lower()

        domains = []
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                domains.append(domain)

        return domains if domains else ['general']

    def _apply_diversity_constraints(
        self,
        incidents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Apply diversity constraints: max 1 incident per type.

        This prevents "5 recovery stories" or "3 decision stories" dominating.
        """
        seen_types = set()
        diverse_incidents = []

        for incident in incidents:
            incident_type = incident.get('type', 'unknown')
            if incident_type not in seen_types:
                seen_types.add(incident_type)
                diverse_incidents.append(incident)

        return diverse_incidents

    def _get_fallback_incidents(
        self,
        topic: str = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get fallback incidents when database has no real ones.

        These are generic "build in public" style nuggets that are
        always true and relevant.
        """
        fallbacks = self.FALLBACK_INCIDENTS.copy()

        # Filter by topic if provided
        if topic:
            topic_domains = self._detect_topic_domain(topic)
            if topic_domains and topic_domains != ['general']:
                fallbacks = [
                    f for f in fallbacks
                    if any(d in topic_domains for d in f.get('domain', []))
                ]

        # If no topic-matched fallbacks, use all
        if not fallbacks:
            fallbacks = self.FALLBACK_INCIDENTS.copy()

        random.shuffle(fallbacks)
        return fallbacks[:limit]

    def _get_agent_recoveries(self, limit: int = 2) -> List[Dict[str, Any]]:
        """Get stories of agents recovering from failures."""
        incidents = []

        try:
            from core.models_unified_system import AgentExecution

            # Find executions that failed then succeeded
            recent_successes = AgentExecution.objects.filter(
                status='success',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).select_related('agent').order_by('-created_at')[:50]

            for exec_obj in recent_successes:
                if exec_obj.agent and exec_obj.execution_time_ms:
                    # Check if there was a recent failure for same agent
                    recent_failure = AgentExecution.objects.filter(
                        agent=exec_obj.agent,
                        status='failed',
                        created_at__lt=exec_obj.created_at,
                        created_at__gte=exec_obj.created_at - timedelta(hours=24)
                    ).first()

                    if recent_failure:
                        incidents.append({
                            'type': 'recovery',
                            'title': f'{exec_obj.agent.name} Recovery Story',
                            'narrative': f"After failing at {recent_failure.created_at.strftime('%I:%M %p')}, "
                                        f"{exec_obj.agent.name} recovered and successfully completed the task "
                                        f"in {exec_obj.execution_time_ms}ms. The system learned from the failure.",
                            'timestamp': exec_obj.created_at,
                            'agent': exec_obj.agent.name,
                            'metrics': {
                                'recovery_time_hours': round((exec_obj.created_at - recent_failure.created_at).total_seconds() / 3600, 1),
                                'execution_time_ms': exec_obj.execution_time_ms,
                            }
                        })

                        if len(incidents) >= limit:
                            break

        except Exception as e:
            logger.debug(f"Could not fetch agent recoveries: {e}")

        return incidents[:limit]

    def _get_dream_stories(self, limit: int = 2) -> List[Dict[str, Any]]:
        """Get stories of dreams that led to real improvements.

        Session 1083 (Rigby audit): AgentDream schema had drifted —
        old fields `status`, `executed_at`, `execution_time_ms`,
        `priority`, `impact_score` don't exist anymore. Current
        equivalents:
          status='executed'   → promoted_to_decision=True
          executed_at         → promoted_at
          priority            → vividness_score
          impact_score        → composite_score
          execution_time_ms   → (removed, no replacement)
        Same pattern as DeliberationSession.topic and LLMCallLog.cost_usd
        bugs earlier this session.
        """
        incidents = []

        try:
            from core.models_unified_system import AgentDream

            executed_dreams = AgentDream.objects.filter(
                promoted_to_decision=True,
                promoted_at__gte=timezone.now() - timedelta(days=14)
            ).select_related('agent').order_by('-promoted_at')[:limit * 2]

            for dream in executed_dreams:
                when = dream.promoted_at or dream.dreamed_at
                incidents.append({
                    'type': 'dream',
                    'title': f'Dream → Reality: {str(dream.title)[:40]}',
                    'narrative': (
                        f"On {when.strftime('%B %d') if when else 'an unknown date'}, "
                        f"the system dreamed about '{dream.title}'. "
                        f"Vividness: {dream.vividness_score:.2f}. "
                        f"Impact (composite): {dream.composite_score:.2f}."
                    ),
                    'timestamp': when,
                    'agent': dream.agent.name if dream.agent else 'System',
                    'metrics': {
                        'vividness': dream.vividness_score,
                        'composite': dream.composite_score,
                        'creativity': dream.creativity_score,
                    }
                })

        except Exception as e:
            logger.warning(
                "content_voice_system._get_dream_stories failed "
                "(%s: %s) — no dream narrative this cycle",
                type(e).__name__, e,
            )

        return incidents[:limit]

    def _get_learning_moments(self, limit: int = 2) -> List[Dict[str, Any]]:
        """Get stories of the system learning something significant.

        Session 1083 (Rigby audit): this method had 5 schema-drift bugs
        that were all silently swallowed via the broad except at the end:
          confidence → confidence_score
          pattern_type → decision_type
          insight → key_insight
          created_at → extracted_at
          source_agent → extracted_by
        The debug-level log hid them even from the noisy logs Chris
        sees. Third schema-drift bug surfaced tonight via the
        "tighten the swallow" pattern.
        """
        incidents = []

        try:
            from core.models_pilot_readiness import ExperimentLearning

            # Get recent high-impact learnings
            learnings = ExperimentLearning.objects.filter(
                extracted_at__gte=timezone.now() - timedelta(days=7),
                confidence_score__gte=0.7
            ).order_by('-confidence_score', '-extracted_at')[:limit * 2]

            for learning in learnings:
                incidents.append({
                    'type': 'learning',
                    'title': f'Learning: {learning.decision_type}',
                    'narrative': (
                        f"The system discovered: {str(learning.key_insight)[:150]}... "
                        f"Confidence: {learning.confidence_score:.0%}. "
                        f"This learning now influences future decisions."
                    ),
                    'timestamp': learning.extracted_at,
                    'agent': learning.extracted_by or 'System',
                    'metrics': {
                        'confidence': learning.confidence_score,
                        'decision_type': learning.decision_type,
                    }
                })

        except Exception as e:
            logger.warning(
                "content_voice_system._get_learning_moments failed "
                "(%s: %s) — no learning narrative this cycle",
                type(e).__name__, e,
            )

        return incidents[:limit]

    def _get_decision_outcomes(self, limit: int = 2) -> List[Dict[str, Any]]:
        """Get stories of decisions and their outcomes."""
        incidents = []

        try:
            from core.models_unified_system import DecisionPoint

            decisions = DecisionPoint.objects.filter(
                status='executed',
                executed_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-executed_at')[:limit * 2]

            for decision in decisions:
                time_to_decide = None
                if decision.executed_at and decision.created_at:
                    time_to_decide = round((decision.executed_at - decision.created_at).total_seconds() / 60, 1)

                decision_confidence = getattr(decision, 'confidence', None)
                decision_agent = getattr(decision, 'assigned_agent', None) or 'System'

                incidents.append({
                    'type': 'decision',
                    'title': f'Decision: {decision.title[:40]}',
                    'narrative': f"Faced with '{decision.title}', the system analyzed options and "
                                f"executed in {time_to_decide or '?'} minutes. "
                                f"Confidence: {decision_confidence:.0%}." if decision_confidence else
                                f"Faced with '{decision.title}', the system made a call.",
                    'timestamp': decision.executed_at,
                    'agent': decision_agent,
                    'metrics': {
                        'time_to_decide_minutes': time_to_decide,
                        'confidence': decision_confidence,
                    }
                })

        except Exception as e:
            logger.debug(f"Could not fetch decision outcomes: {e}")

        return incidents[:limit]

    def _get_spider_discoveries(self, limit: int = 2) -> List[Dict[str, Any]]:
        """Get stories of spiders discovering valuable intelligence."""
        incidents = []

        try:
            from core.models_unified_system import SpiderData

            # Get recent high-value spider results
            results = SpiderData.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=3)
            ).order_by('-created_at')[:100]

            # Find ones with interesting data
            for result in results:
                data = getattr(result, 'raw_data', {}) or getattr(result, 'processed_data', {}) or {}
                if data and isinstance(data, dict):
                    item_count = len(data.get('items', data.get('results', [])))
                    spider_name = getattr(result, 'spider_name', 'intelligence')
                    if item_count > 5:
                        incidents.append({
                            'type': 'spider',
                            'title': f'Spider Discovery: {spider_name}',
                            'narrative': f"The {spider_name} spider crawled and discovered "
                                        f"{item_count} items. Real-time intelligence flowing into the system.",
                            'timestamp': result.created_at,
                            'agent': 'Spider Network',
                            'metrics': {
                                'items_found': item_count,
                                'spider': spider_name,
                            }
                        })

                        if len(incidents) >= limit:
                            break

        except Exception as e:
            logger.debug(f"Could not fetch spider discoveries: {e}")

        return incidents[:limit]

    def format_incident_for_content(self, incident: Dict[str, Any]) -> str:
        """Format an incident as a narrative paragraph for blog content."""
        templates = {
            'recovery': "Last {timeframe}, {agent} hit a wall - the task failed. But here's where it gets interesting: within {recovery_time} hours, the system diagnosed the issue, adapted, and executed successfully in {exec_time}ms. That's not magic, that's learning in action.",

            'dream': "On {date}, something unexpected happened. The system 'dreamed' about {dream_topic} - not in a science fiction way, but in the way that insights emerge when you let an AI reflect on its own patterns. {exec_time}ms later, that dream became a real improvement.",

            'learning': "The system recently discovered something: {insight}. Confidence: {confidence}%. This isn't just stored - it's now actively influencing how decisions get made.",

            'decision': "When faced with '{decision}', the system didn't freeze. It analyzed, decided, and executed in {time} minutes. That's the difference between an AI that talks about decisions and one that makes them.",

            'spider': "The {spider} spider just pulled {count} items of fresh intelligence. Not yesterday's news - right now. That data is already flowing into agent decisions.",
        }

        template = templates.get(incident['type'], "Something interesting happened: {narrative}")

        # Build context for formatting
        ctx = {
            'timeframe': self._relative_time(incident.get('timestamp')),
            'date': incident.get('timestamp', timezone.now()).strftime('%B %d'),
            'agent': incident.get('agent', 'the system'),
            'narrative': incident.get('narrative', ''),
        }

        metrics = incident.get('metrics', {})
        ctx['recovery_time'] = metrics.get('recovery_time_hours', '?')
        ctx['exec_time'] = metrics.get('execution_time_ms', metrics.get('execution_ms', '?'))
        ctx['dream_topic'] = incident.get('title', '').replace('Dream → Reality: ', '')
        ctx['insight'] = incident.get('narrative', '')[:150]
        ctx['confidence'] = int(metrics.get('confidence', 0) * 100) if metrics.get('confidence') else '?'
        ctx['decision'] = incident.get('title', '').replace('Decision: ', '')
        ctx['time'] = metrics.get('time_to_decide_minutes', '?')
        ctx['spider'] = metrics.get('spider', 'intelligence')
        ctx['count'] = metrics.get('items_found', '?')

        try:
            return template.format(**ctx)
        except KeyError:
            return incident.get('narrative', 'An interesting event occurred in the system.')

    def _relative_time(self, dt: Optional[datetime]) -> str:
        """Convert datetime to relative time string."""
        if not dt:
            return "recently"

        now = timezone.now()
        if dt.tzinfo is None:
            dt = timezone.make_aware(dt)

        diff = now - dt

        if diff.days == 0:
            if diff.seconds < 3600:
                return f"{diff.seconds // 60} minutes ago"
            return f"{diff.seconds // 3600} hours ago"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return dt.strftime('%B %d')


# =============================================================================
# CTA LIBRARY - Strong Calls-to-Action
# =============================================================================

class CTALibrary:
    """
    Library of strong calls-to-action for different content types and audiences.

    No more "Join the conversation..." weak endings.
    """

    # CTA categories with options
    CTAS = {
        'demo': {
            'name': 'Request Demo',
            'options': [
                {
                    'headline': 'See It In Action',
                    'text': "Ready to see {agent_count} agents working together? Book a 20-minute demo and watch the system think in real-time.",
                    'button': 'Book Your Demo',
                    'urgency': 'high',
                },
                {
                    'headline': 'Watch Real AI Work',
                    'text': "Not another slide deck. We'll show you live agents, real decisions, actual learning. 20 minutes. No fluff.",
                    'button': 'See It Live',
                    'urgency': 'high',
                },
            ]
        },
        'early_access': {
            'name': 'Early Access',
            'options': [
                {
                    'headline': 'Get Early Access',
                    'text': "We're onboarding builders who want to push this system to its limits. Limited spots. Real feedback loop.",
                    'button': 'Apply for Early Access',
                    'urgency': 'medium',
                },
                {
                    'headline': 'Be One of the First',
                    'text': "Join the founding users shaping what this becomes. Your use cases. Your feedback. Direct line to the builders.",
                    'button': 'Join Early Access',
                    'urgency': 'medium',
                },
            ]
        },
        'newsletter': {
            'name': 'Newsletter',
            'options': [
                {
                    'headline': 'The Build Log',
                    'text': "Weekly: What we shipped, what broke, what we learned. No marketing speak. Just the real story of building in public.",
                    'button': 'Subscribe to Build Log',
                    'urgency': 'low',
                },
                {
                    'headline': 'Inside the System',
                    'text': "Get the unfiltered updates. New agents. New capabilities. Lessons from the trenches. Delivered weekly.",
                    'button': 'Get Updates',
                    'urgency': 'low',
                },
            ]
        },
        'investor': {
            'name': 'Investor Info',
            'options': [
                {
                    'headline': 'Invest in Real AI',
                    'text': "Not another pitch deck company. {conversation_count} conversations. {dream_count} self-improvements. {decision_count} autonomous decisions. Real metrics, real traction.",
                    'button': 'Request Investor Deck',
                    'urgency': 'high',
                },
            ]
        },
        'pilot': {
            'name': 'Pilot Program',
            'options': [
                {
                    'headline': 'Run a Pilot',
                    'text': "Test the system on your use case. 30-day pilot. Full access. Direct support. See what {agent_count} agents can do for your workflow.",
                    'button': 'Start Your Pilot',
                    'urgency': 'medium',
                },
            ]
        },
        'github': {
            'name': 'GitHub',
            'options': [
                {
                    'headline': 'See the Code',
                    'text': "Building in public means you can see exactly how this works. Star the repo. Open issues. Contribute.",
                    'button': 'View on GitHub',
                    'urgency': 'low',
                },
            ]
        },
    }

    def __init__(self):
        self._stats_cache = None
        self._stats_cache_time = None

    def get_cta(
        self,
        cta_type: str = 'newsletter',
        content_type: str = 'blog_post',
        audience: str = 'tech_enthusiasts'
    ) -> Dict[str, Any]:
        """Get an appropriate CTA based on context."""

        # Get system stats for personalization
        stats = self._get_system_stats()

        # Select CTA category
        category = self.CTAS.get(cta_type, self.CTAS['newsletter'])

        # Pick a random option from the category
        option = random.choice(category['options'])

        # Format with stats
        formatted = {
            'headline': option['headline'],
            'text': option['text'].format(
                agent_count=stats.get('agent_count', 74),
                conversation_count=stats.get('conversation_count', '6,000+'),
                dream_count=stats.get('dream_count', '1,900+'),
                decision_count=stats.get('decision_count', '500+'),
            ),
            'button': option['button'],
            'urgency': option['urgency'],
            'type': cta_type,
        }

        return formatted

    def get_cta_for_audience(self, audience: str) -> Dict[str, Any]:
        """Get the most appropriate CTA for an audience."""

        audience_cta_map = {
            'tech_enthusiasts': 'github',
            'developers': 'github',
            'investors': 'investor',
            'enterprise': 'pilot',
            'founders': 'demo',
            'builders': 'early_access',
            'general': 'newsletter',
        }

        cta_type = audience_cta_map.get(audience, 'newsletter')
        return self.get_cta(cta_type=cta_type, audience=audience)

    def _get_system_stats(self) -> Dict[str, Any]:
        """Get current system stats for CTA personalization."""

        # Cache for 10 minutes
        if (self._stats_cache and self._stats_cache_time and
            timezone.now() - self._stats_cache_time < timedelta(minutes=10)):
            return self._stats_cache

        stats = {
            'agent_count': 74,
            'conversation_count': '6,000+',
            'dream_count': '1,900+',
            'decision_count': '500+',
        }

        try:
            from core.models_unified_system import Agent, AgentConversation, AgentDream, DecisionPoint

            stats['agent_count'] = Agent.objects.count() or 74

            conv_count = AgentConversation.objects.count()
            stats['conversation_count'] = f"{conv_count:,}" if conv_count else '6,000+'

            dream_count = AgentDream.objects.count()
            stats['dream_count'] = f"{dream_count:,}" if dream_count else '1,900+'

            decision_count = DecisionPoint.objects.count()
            stats['decision_count'] = f"{decision_count:,}" if decision_count else '500+'

        except Exception as e:
            logger.debug(f"Could not fetch stats for CTA: {e}")

        self._stats_cache = stats
        self._stats_cache_time = timezone.now()

        return stats


# =============================================================================
# FLAGSHIP BLOG TEMPLATE - The New Content Pattern
# =============================================================================

class FlagshipBlogTemplate:
    """
    The template for creating distinctive, memorable content.

    Pattern:
    1. Vision - The big picture hook
    2. Real Stat - Grounding with actual numbers
    3. Real Incident - A concrete story from the system
    4. System Response - How the platform handled it
    5. Lesson Learned - The takeaway
    6. Strong CTA - Clear next step
    """

    def __init__(self):
        self.voice = VoiceProfile()
        self.narrative_service = NarrativeInjectionService()
        self.cta_library = CTALibrary()

    def generate_flagship_prompt_injection(
        self,
        topic: str,
        audience: str = 'tech_enthusiasts',
        cta_type: str = 'newsletter'
    ) -> str:
        """
        Generate the prompt injection for flagship-quality content.

        This is added to the ContentWriterAgent's prompt to guide
        the content toward the flagship pattern.

        Session 951: Now passes topic to get_recent_incidents for relevance filtering.
        """

        # Get real incidents - Session 951: filtered by topic relevance
        incidents = self.narrative_service.get_recent_incidents(limit=3, topic=topic)
        incident_stories = []
        for incident in incidents:
            formatted = self.narrative_service.format_incident_for_content(incident)
            incident_stories.append(f"- {formatted}")

        # Get voice elements
        voice_injection = self.voice.get_voice_injection()
        anti_patterns = self.voice.get_anti_pattern_check()

        # Get CTA
        cta = self.cta_library.get_cta(cta_type=cta_type, audience=audience)

        # Session 913: Removed fictional struggle stories - now using only real incidents

        prompt = f"""
## SESSION 854: FLAGSHIP CONTENT REQUIREMENTS

This content must be UNMISTAKABLY Donkey Betz - not generic AI startup content.

### THE DONKEY BETZ VOICE
{self.voice.origin_story}

Tone: {', '.join(self.voice.tone_attributes[:3])}
{anti_patterns}

### VOICE ELEMENTS TO INCLUDE
{voice_injection}

### REAL INCIDENTS TO REFERENCE (Pick one and work it in naturally)
{chr(10).join(incident_stories) if incident_stories else "- Focus on general system capabilities if no specific incidents available"}

### FLAGSHIP STRUCTURE REQUIREMENTS
Your content MUST follow this pattern:

1. **VISION HOOK** (First 2 sentences)
   - Not "AI is changing everything" generic
   - Specific, bold, grounded in what we've actually built

2. **REAL STAT** (Within first paragraph)
   - Use actual system numbers: agents, conversations, dreams, decisions
   - Numbers ground the narrative and prove this is real

3. **REAL INCIDENT** (Mid-content)
   - Include at least ONE concrete story from the incidents above
   - "Last week...", "On Tuesday...", "Recently..."
   - Specific agent names, specific outcomes, specific timeframes

4. **SYSTEM RESPONSE** (After the incident)
   - How did the platform handle it?
   - What made the response interesting?

5. **LESSON LEARNED** (Before conclusion)
   - What did we/the system learn?
   - Connect to the reader's situation

6. **STRONG CTA** (End)
   Use this CTA:
   **{cta['headline']}**
   {cta['text']}
   Button: [{cta['button']}]

### WHAT MAKES THIS FLAGSHIP (NOT GENERIC)
- Sounds like it was written by someone who actually built this at 3am
- Includes specific, verifiable details from the actual system
- Has personality - the reader should feel they know who built this
- Tells a story, not just explains features
- Makes the reader want to see it in action

### SIGNATURE PHRASES (Work in naturally if appropriate)
{', '.join(random.sample(self.voice.signature_phrases, 3))}

Now write content that could ONLY come from Donkey Betz. Make it unforgettable.
"""

        return prompt

    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system stats for content."""
        return self.cta_library._get_system_stats()


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def get_voice_profile() -> VoiceProfile:
    """Get the Donkey Betz voice profile."""
    return VoiceProfile()


def get_narrative_service() -> NarrativeInjectionService:
    """Get the narrative injection service."""
    return NarrativeInjectionService()


def get_cta_library() -> CTALibrary:
    """Get the CTA library."""
    return CTALibrary()


def get_flagship_template() -> FlagshipBlogTemplate:
    """Get the flagship blog template."""
    return FlagshipBlogTemplate()


def generate_flagship_injection(
    topic: str,
    audience: str = 'tech_enthusiasts',
    cta_type: str = 'newsletter'
) -> str:
    """
    Convenience function to generate flagship prompt injection.

    Usage in ContentWriterAgent:
        from core.services.content_voice_system import generate_flagship_injection

        flagship_prompt = generate_flagship_injection(
            topic="AI Agents in 2026",
            audience="tech_enthusiasts",
            cta_type="demo"
        )

        # Add to the content generation prompt
        full_prompt = base_prompt + flagship_prompt
    """
    template = FlagshipBlogTemplate()
    return template.generate_flagship_prompt_injection(
        topic=topic,
        audience=audience,
        cta_type=cta_type
    )

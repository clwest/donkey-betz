"""
Proactive Intelligence Service - Session 482

Connects the 19 Autonomous Situations to the AI Assistant for proactive suggestions.

Features:
- Fetches recent trigger events relevant to user context
- Retrieves active alerts from all situations
- Formats intelligence for natural conversation injection
- Prioritizes by relevance and recency

The 19 Situations by Domain:
- Content: Content Studio, Narrative Drift
- Creative: Design Trends, Viral Predictor, Thumbnails
- Income: Job Match, Freelance Scout, Side Hustles
- Financial: Market Intelligence, SEC Filing, Earnings, Crypto, Blockchain
- Research: Tech Stack, AI Models, Skill Gaps
- Legal: Case Law, Regulatory
"""

import logging
from datetime import timedelta
from typing import List, Dict, Any, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProactiveIntelligenceService:
    """
    Service to fetch and format proactive intelligence from autonomous situations.

    Connects the 19 event-driven situations to the AI Assistant, enabling
    proactive suggestions based on real-time intelligence.
    """

    # Domain mappings for context relevance
    DOMAIN_KEYWORDS = {
        'content': ['content', 'video', 'article', 'blog', 'post', 'create', 'write', 'publish'],
        'creative': ['design', 'logo', 'image', 'visual', 'thumbnail', 'brand', 'style'],
        'income': ['job', 'work', 'freelance', 'gig', 'money', 'income', 'earn', 'career', 'salary'],
        'financial': ['stock', 'crypto', 'bitcoin', 'market', 'invest', 'trading', 'finance', 'sec'],
        'research': ['ai', 'technology', 'learn', 'skill', 'course', 'trending', 'tech'],
        'legal': ['legal', 'law', 'court', 'case', 'regulation', 'compliance'],
    }

    # Situation types by domain
    DOMAIN_SITUATIONS = {
        'content': ['content_studio', 'narrative_drift'],
        'creative': ['design_trends', 'viral_prediction', 'thumbnail_optimization'],
        'income': ['job_matching', 'freelance_scout', 'side_hustle'],
        'financial': ['market_intelligence', 'blockchain', 'stock_market', 'sec_filing', 'crypto_sentiment', 'earnings_prediction'],
        'research': ['tech_stack', 'ai_model', 'skill_gap'],
        'legal': ['case_law', 'regulatory'],
    }

    def __init__(self, user=None):
        self.user = user

    def get_relevant_intelligence(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        max_alerts: int = 3,
        hours_lookback: int = 24
    ) -> Dict[str, Any]:
        """
        Get intelligence relevant to the user's message/context.

        Args:
            message: User's current message
            context: Optional conversation context
            max_alerts: Maximum alerts to return
            hours_lookback: How far back to look for events

        Returns:
            Dict with relevant alerts, suggestions, and metadata
        """
        try:
            # Detect relevant domains from message
            relevant_domains = self._detect_domains(message, context)

            # Fetch intelligence from each relevant domain
            intelligence = {
                'alerts': [],
                'suggestions': [],
                'trending_topics': [],
                'opportunities': [],
                'metadata': {
                    'domains_checked': relevant_domains,
                    'timestamp': timezone.now().isoformat(),
                    'hours_lookback': hours_lookback
                }
            }

            # Get trigger events
            trigger_events = self._get_recent_trigger_events(
                domains=relevant_domains,
                hours=hours_lookback,
                limit=max_alerts * 2  # Get more, filter later
            )

            # Get domain-specific intelligence
            for domain in relevant_domains:
                domain_intel = self._get_domain_intelligence(domain, hours_lookback)

                if domain_intel.get('alerts'):
                    intelligence['alerts'].extend(domain_intel['alerts'][:max_alerts])
                if domain_intel.get('opportunities'):
                    intelligence['opportunities'].extend(domain_intel['opportunities'])
                if domain_intel.get('trending'):
                    intelligence['trending_topics'].extend(domain_intel['trending'])

            # Format trigger events as alerts
            for event in trigger_events[:max_alerts]:
                alert = self._format_trigger_event(event)
                if alert and alert not in intelligence['alerts']:
                    intelligence['alerts'].append(alert)

            # Generate proactive suggestions
            intelligence['suggestions'] = self._generate_suggestions(
                message,
                relevant_domains,
                intelligence['alerts']
            )

            # Deduplicate and limit
            intelligence['alerts'] = intelligence['alerts'][:max_alerts]
            intelligence['suggestions'] = intelligence['suggestions'][:3]

            logger.info(f"📡 ProactiveIntelligence: Found {len(intelligence['alerts'])} alerts, "
                       f"{len(intelligence['suggestions'])} suggestions for domains: {relevant_domains}")

            return intelligence

        except Exception as e:
            logger.error(f"Error getting proactive intelligence: {e}")
            return {
                'alerts': [],
                'suggestions': [],
                'trending_topics': [],
                'opportunities': [],
                'metadata': {'error': str(e)}
            }

    def _detect_domains(self, message: str, context: Optional[Dict] = None) -> List[str]:
        """Detect which domains are relevant based on message content."""
        message_lower = message.lower()
        relevant = []

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    if domain not in relevant:
                        relevant.append(domain)
                    break

        # Check context for additional domains
        if context:
            conversation_history = context.get('conversation_history', [])
            for msg in conversation_history[-3:]:  # Last 3 messages
                content = msg.get('content', '').lower()
                for domain, keywords in self.DOMAIN_KEYWORDS.items():
                    if domain not in relevant:
                        for keyword in keywords:
                            if keyword in content:
                                relevant.append(domain)
                                break

        # Default to general domains if none detected
        if not relevant:
            relevant = ['research', 'content']  # Safe defaults

        return relevant

    def _get_recent_trigger_events(
        self,
        domains: List[str],
        hours: int = 24,
        limit: int = 10
    ) -> List[Any]:
        """Get recent trigger events for specified domains."""
        try:
            from core.models_situation_triggers import TriggerEvent

            cutoff = timezone.now() - timedelta(hours=hours)

            # Get situation types for domains
            situation_types = []
            for domain in domains:
                situation_types.extend(self.DOMAIN_SITUATIONS.get(domain, []))

            # Query trigger events
            events = TriggerEvent.objects.filter(
                fired_at__gte=cutoff,
            ).select_related('trigger').order_by('-fired_at')[:limit]

            return list(events)

        except Exception as e:
            logger.error(f"Error fetching trigger events: {e}")
            return []

    def _get_domain_intelligence(self, domain: str, hours: int = 24) -> Dict[str, Any]:
        """Get domain-specific intelligence."""
        cutoff = timezone.now() - timedelta(hours=hours)
        intel = {'alerts': [], 'opportunities': [], 'trending': []}

        try:
            if domain == 'financial':
                intel.update(self._get_financial_intelligence(cutoff))
            elif domain == 'income':
                intel.update(self._get_income_intelligence(cutoff))
            elif domain == 'content':
                intel.update(self._get_content_intelligence(cutoff))
            elif domain == 'creative':
                intel.update(self._get_creative_intelligence(cutoff))
            elif domain == 'research':
                intel.update(self._get_research_intelligence(cutoff))
            elif domain == 'legal':
                intel.update(self._get_legal_intelligence(cutoff))

        except Exception as e:
            logger.error(f"Error getting {domain} intelligence: {e}")

        return intel

    def _get_financial_intelligence(self, cutoff) -> Dict[str, Any]:
        """Get financial domain intelligence."""
        alerts = []

        try:
            # Blockchain security alerts
            from core.models_autonomous_alerts import BlockchainSecurityAlert
            blockchain_alerts = BlockchainSecurityAlert.objects.filter(
                created_at__gte=cutoff,
                severity__in=['critical', 'high']
            ).order_by('-created_at')[:3]

            for alert in blockchain_alerts:
                alerts.append({
                    'type': 'blockchain_security',
                    'severity': alert.severity,
                    'title': alert.title,
                    'summary': alert.summary[:200],
                    'domain': 'financial'
                })
        except Exception as e:
            logger.debug(f"No blockchain alerts: {e}")

        try:
            # Market intelligence briefs
            from core.models_unified_system import MarketIntelligenceBrief
            briefs = MarketIntelligenceBrief.objects.filter(
                generated_at__gte=cutoff
            ).order_by('-generated_at')[:1]

            for brief in briefs:
                if brief.high_conviction_opportunities:
                    alerts.append({
                        'type': 'market_intelligence',
                        'severity': 'info',
                        'title': 'Market Intelligence Update',
                        'summary': f"{len(brief.high_conviction_opportunities)} high conviction opportunities identified",
                        'domain': 'financial',
                        'data': brief.high_conviction_opportunities[:3]
                    })
        except Exception as e:
            logger.debug(f"No market briefs: {e}")

        return {'alerts': alerts}

    def _get_income_intelligence(self, cutoff) -> Dict[str, Any]:
        """Get income/job domain intelligence."""
        opportunities = []

        try:
            from core.models_unified_system import Opportunity
            jobs = Opportunity.objects.filter(
                created_at__gte=cutoff,
                status='active',
                source__in=['RemoteOK', 'WeWorkRemotely', 'Adzuna', 'Remotive']
            ).order_by('-score')[:5]

            for job in jobs:
                opportunities.append({
                    'type': 'job_opportunity',
                    'title': job.title,
                    'source': job.source,
                    'score': job.score,
                    'url': job.url
                })
        except Exception as e:
            logger.debug(f"No job opportunities: {e}")

        return {'opportunities': opportunities}

    def _get_content_intelligence(self, cutoff) -> Dict[str, Any]:
        """Get content domain intelligence."""
        trending = []

        try:
            from core.models_unified_system import SpiderData
            # Get trending content topics - use correct field names
            # Session 807: Defer embedding fields to reduce egress costs
            content_data = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=['techcrunch', 'hackernews', 'theverge', 'wired', 'reddit']
            ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:10]

            for item in content_data[:5]:
                # Extract title from raw_data
                title = ''
                if item.raw_data and 'items' in item.raw_data:
                    items = item.raw_data.get('items', [])
                    if items and len(items) > 0:
                        title = items[0].get('title', '')[:100]
                trending.append({
                    'type': 'trending_topic',
                    'title': title or f'Update from {item.spider_name}',
                    'source': item.spider_name,
                    'category': item.data_type,
                    'url': item.source_url  # Session 483: Include URL
                })
        except Exception as e:
            logger.debug(f"No content trends: {e}")

        return {'trending': trending}

    def _get_creative_intelligence(self, cutoff) -> Dict[str, Any]:
        """Get creative/design domain intelligence."""
        trending = []

        try:
            from core.models_unified_system import SpiderData
            # Session 807: Defer embedding fields to reduce egress costs
            design_data = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=['behance', 'dribbble', 'awwwards', 'unsplash']
            ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:5]

            for item in design_data:
                # Extract title from raw_data
                title = ''
                if item.raw_data and 'items' in item.raw_data:
                    items = item.raw_data.get('items', [])
                    if items and len(items) > 0:
                        title = items[0].get('title', '')[:100]
                trending.append({
                    'type': 'design_trend',
                    'title': title or f'Update from {item.spider_name}',
                    'source': item.spider_name,
                    'url': item.source_url  # Session 483: Include URL
                })
        except Exception as e:
            logger.debug(f"No design trends: {e}")

        return {'trending': trending}

    def _get_research_intelligence(self, cutoff) -> Dict[str, Any]:
        """Get research/tech domain intelligence."""
        trending = []

        try:
            from core.models_unified_system import SpiderData
            # Session 807: Defer embedding fields to reduce egress costs
            tech_data = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=['techcrunch', 'hackernews', 'theverge', 'wired', 'mit_tech_review', 'arstechnica']
            ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:10]

            # Filter for AI/ML content
            ai_keywords = ['ai', 'gpt', 'llm', 'claude', 'openai', 'anthropic', 'machine learning']
            for item in tech_data:
                # Extract title from raw_data
                title = ''
                if item.raw_data and 'items' in item.raw_data:
                    items = item.raw_data.get('items', [])
                    for raw_item in items[:5]:  # Check first 5 items
                        raw_title = raw_item.get('title', '')
                        if any(kw in raw_title.lower() for kw in ai_keywords):
                            title = raw_title[:100]
                            url = raw_item.get('url', raw_item.get('link', '')) or item.source_url
                            trending.append({
                                'type': 'ai_trend',
                                'title': title,
                                'source': item.spider_name,
                                'url': url
                            })
                            break
        except Exception as e:
            logger.debug(f"No tech trends: {e}")

        return {'trending': trending[:5]}

    def _get_legal_intelligence(self, cutoff) -> Dict[str, Any]:
        """Get legal domain intelligence."""
        alerts = []

        try:
            from core.models_unified_system import SpiderData
            # Session 807: Defer embedding fields to reduce egress costs
            legal_data = SpiderData.objects.filter(
                created_at__gte=cutoff,
                spider_name__in=['courtlistener', 'legal_news', 'findlaw', 'colorado_family_law']
            ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:5]

            for item in legal_data:
                # Extract title from raw_data
                title = ''
                if item.raw_data and 'items' in item.raw_data:
                    items = item.raw_data.get('items', [])
                    if items and len(items) > 0:
                        title = items[0].get('title', '')[:100]
                alerts.append({
                    'type': 'legal_update',
                    'title': title or f'Update from {item.spider_name}',
                    'source': item.spider_name,
                    'url': item.source_url
                })
        except Exception as e:
            logger.debug(f"No legal updates: {e}")

        return {'alerts': alerts}

    def _format_trigger_event(self, event) -> Optional[Dict[str, Any]]:
        """Format a trigger event as an alert."""
        try:
            return {
                'type': 'trigger_event',
                'trigger_name': event.trigger.name,
                'trigger_type': event.trigger.trigger_type,
                'matched_value': event.matched_value[:100],
                'fired_at': event.fired_at.isoformat(),
                'severity': 'info'
            }
        except Exception as _e:
            logger.warning(
                "proactive_intelligence._format_trigger_event: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _generate_suggestions(
        self,
        message: str,
        domains: List[str],
        alerts: List[Dict]
    ) -> List[str]:
        """Generate proactive suggestions based on context and alerts."""
        suggestions = []

        # Content-related suggestions
        if 'content' in domains and alerts:
            suggestions.append(
                "I noticed some trending topics that might be good for content creation. "
                "Would you like me to show you what's trending?"
            )

        # Job/income suggestions
        if 'income' in domains:
            suggestions.append(
                "I've been tracking job opportunities. Would you like me to show you "
                "the highest-scoring matches for your profile?"
            )

        # Financial suggestions
        if 'financial' in domains and any(a.get('type') == 'blockchain_security' for a in alerts):
            suggestions.append(
                "There are some security alerts in the crypto space. "
                "Would you like a summary of recent findings?"
            )

        # Research/AI suggestions
        if 'research' in domains:
            suggestions.append(
                "There have been some interesting AI developments. "
                "Want me to summarize the latest trends?"
            )

        return suggestions

    def format_for_prompt(self, intelligence: Dict[str, Any]) -> str:
        """
        Format intelligence for injection into AI Assistant prompt.

        Session 483: Enhanced to include source URLs for proper attribution.
        """
        if not intelligence.get('alerts') and not intelligence.get('suggestions'):
            return ""

        lines = ["\n## Proactive Intelligence (from Autonomous Situations)\n"]

        # Add alerts with source links
        if intelligence.get('alerts'):
            lines.append("**Recent Alerts:**")
            for alert in intelligence['alerts'][:3]:
                severity = alert.get('severity', 'info').upper()
                title = alert.get('title', 'Alert')
                url = alert.get('url', '')
                if url:
                    lines.append(f"- [{severity}] {title} ([source]({url}))")
                else:
                    lines.append(f"- [{severity}] {title}")

        # Add trending topics with source links
        if intelligence.get('trending_topics'):
            lines.append("\n**Trending Topics (with sources):**")
            for topic in intelligence['trending_topics'][:5]:
                title = topic.get('title', 'Topic')
                source = topic.get('source', 'unknown')
                url = topic.get('url', '')
                if url:
                    lines.append(f"- [{title}]({url}) (via {source})")
                else:
                    lines.append(f"- {title} (via {source})")

        # Add opportunities with links
        if intelligence.get('opportunities'):
            lines.append("\n**Opportunities:**")
            for opp in intelligence['opportunities'][:3]:
                title = opp.get('title', 'Opportunity')
                score = opp.get('score', 'N/A')
                url = opp.get('url', '')
                if url:
                    lines.append(f"- [{title}]({url}) (score: {score})")
                else:
                    lines.append(f"- {title} (score: {score})")

        # Session 483: Instruction for source attribution
        lines.append("\n**IMPORTANT: When presenting trending information to the user:**")
        lines.append("- Include clickable source links when available")
        lines.append("- Format as: [Article Title](URL) or 'Source: Publication Name'")
        lines.append("- Add a 'Sources:' section at the end with links\n")

        return "\n".join(lines)


# Singleton instance
_proactive_intelligence_service = None

def get_proactive_intelligence_service(user=None) -> ProactiveIntelligenceService:
    """Get or create the proactive intelligence service."""
    global _proactive_intelligence_service
    if _proactive_intelligence_service is None or user:
        _proactive_intelligence_service = ProactiveIntelligenceService(user)
    return _proactive_intelligence_service

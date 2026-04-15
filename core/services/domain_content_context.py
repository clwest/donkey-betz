"""
Domain Content Context Router
Session 891: Unified context injection for ALL content domains.

This router detects the topic domain and injects relevant platform data:
- Finance/Markets: Spider data, predictions, advisor wisdom
- Sports/Betting: Live odds, betting performance, value bets
- AI/Technology: Agent insights, platform capabilities, dev learnings
- Crypto/Blockchain: Chain data, whale activity, DeFi analysis
- Legal: Case research, precedents, jurisdiction info
- Career/Jobs: Market trends, application success rates, skills data
- Health/Wellness: Research summaries, trend data
- News/Media: Source aggregation, trending topics

Each domain gets its own "builder voice" - real platform experience, not generic journalism.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Q

logger = logging.getLogger(__name__)


# =============================================================================
# Domain Keywords for Topic Detection
# =============================================================================

DOMAIN_KEYWORDS = {
    'finance': [
        'stock', 'market', 'invest', 'trading', 'portfolio', 'earnings',
        'nasdaq', 'dow', 'sp500', 's&p', 'bull', 'bear', 'dividend',
        'nvidia', 'tesla', 'apple', 'amazon', 'netflix', 'meta', 'google',
        'finance', 'financial', 'economy', 'fed', 'interest rate', 'inflation',
        'recession', 'gdp', 'bonds', 'etf', 'mutual fund', 'ipo', 'earnings',
    ],
    'crypto': [
        'crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'nft',
        'web3', 'token', 'coin', 'mining', 'wallet', 'exchange',
        'solana', 'cardano', 'polygon', 'avalanche', 'chainlink',
        'smart contract', 'dao', 'staking', 'yield', 'liquidity',
    ],
    'sports': [
        'nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ncaaf', 'ncaab',
        'football', 'basketball', 'baseball', 'hockey', 'soccer',
        'super bowl', 'world series', 'stanley cup', 'playoffs', 'finals',
        'premier league', 'champions league', 'mls', 'ufc', 'mma', 'boxing',
        'tennis', 'golf', 'athlete', 'game', 'match', 'championship',
    ],
    'betting': [
        'betting', 'bet', 'wager', 'odds', 'spread', 'moneyline',
        'over/under', 'parlay', 'prop', 'handicap', 'sportsbook',
        'value bet', 'arbitrage', 'line movement', 'sharp', 'bankroll',
        'pick', 'picks', 'prediction', 'favorite', 'underdog',
    ],
    'ai_tech': [
        'ai', 'artificial intelligence', 'machine learning', 'ml', 'llm',
        'gpt', 'claude', 'agent', 'automation', 'neural', 'deep learning',
        'nlp', 'computer vision', 'robotics', 'autonomous', 'chatbot',
        'transformer', 'model', 'training', 'inference', 'prompt',
        'python', 'javascript', 'react', 'django', 'api', 'developer',
        'software', 'code', 'programming', 'tech', 'startup', 'saas',
    ],
    'legal': [
        'legal', 'law', 'court', 'attorney', 'lawyer', 'case',
        'lawsuit', 'litigation', 'contract', 'compliance', 'regulation',
        'patent', 'trademark', 'copyright', 'intellectual property',
        'criminal', 'civil', 'family law', 'divorce', 'custody',
        'estate', 'trust', 'will', 'probate', 'bankruptcy',
    ],
    'career': [
        'job', 'career', 'resume', 'interview', 'hiring', 'salary',
        'remote work', 'freelance', 'gig', 'contractor', 'employment',
        'linkedin', 'networking', 'skill', 'certification', 'promotion',
        'layoff', 'recession', 'job market', 'application', 'ats',
    ],
    'health': [
        'health', 'wellness', 'fitness', 'nutrition', 'diet', 'exercise',
        'mental health', 'anxiety', 'depression', 'therapy', 'meditation',
        'sleep', 'stress', 'weight', 'muscle', 'cardio', 'yoga',
        'disease', 'treatment', 'symptom', 'doctor', 'medical',
    ],
    'education': [
        'education', 'learning', 'course', 'tutorial', 'online learning',
        'mooc', 'university', 'college', 'degree', 'certification',
        'skill development', 'training', 'bootcamp', 'curriculum',
    ],
}


class DomainContentContextBuilder:
    """
    Session 891: Unified context builder for all content domains.

    Detects topic domain and injects relevant platform data to give
    content the authentic "builder voice" of someone who actually
    tracks this data and uses these tools.
    """

    def __init__(self):
        self._spider_service = None
        self._domain_cache = {}

    @property
    def spider_service(self):
        """Lazy load spider intelligence service."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import get_spider_intelligence
                self._spider_service = get_spider_intelligence()
            except Exception as e:
                logger.warning(f"Could not load spider service: {e}")
        return self._spider_service

    def detect_domain(self, topic: str, content: str = "") -> Tuple[str, float]:
        """
        Detect the primary domain of the content.

        Returns:
            Tuple of (domain_name, confidence_score)
        """
        combined = f"{topic} {content}".lower()

        # Count keyword matches for each domain
        domain_scores = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in combined)
            if matches > 0:
                domain_scores[domain] = matches

        if not domain_scores:
            return ('general', 0.0)

        # Get domain with most matches
        primary_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[primary_domain]

        # Calculate confidence based on number of keyword matches
        confidence = min(max_score / 5.0, 1.0)  # 5+ matches = full confidence

        return (primary_domain, confidence)

    def detect_all_domains(self, topic: str, content: str = "") -> List[Tuple[str, float]]:
        """
        Detect all relevant domains (for multi-domain content).

        Returns list of (domain, confidence) tuples sorted by confidence.
        """
        combined = f"{topic} {content}".lower()

        domain_scores = []
        for domain, keywords in DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in combined)
            if matches > 0:
                confidence = min(matches / 5.0, 1.0)
                domain_scores.append((domain, confidence))

        return sorted(domain_scores, key=lambda x: x[1], reverse=True)

    # =========================================================================
    # Domain-Specific Context Builders
    # =========================================================================

    def _get_finance_context(self, topic: str) -> str:
        """Get finance/markets context."""
        parts = []
        try:
            # Import the dedicated finance context builder
            from core.services.finance_content_context import get_finance_content_context
            ctx = get_finance_content_context(topic)
            if ctx:
                return ctx
        except ImportError:
            pass

        # Fallback: basic finance context
        parts.append("## Finance Content Guidelines")
        parts.append("- Reference market data with specifics")
        parts.append("- Include price movements and percentages")
        parts.append("- Cite analyst perspectives when available")

        return "\n".join(parts)

    def _get_sports_context(self, topic: str) -> str:
        """Get sports/betting context."""
        try:
            from core.services.sports_content_context import get_sports_content_context
            ctx = get_sports_content_context(topic)
            if ctx:
                return ctx
        except ImportError:
            pass

        # Fallback
        parts = ["## Sports Content Guidelines"]
        parts.append("- Include specific stats and records")
        parts.append("- Reference recent game results")
        parts.append("- Use proper sports terminology")
        return "\n".join(parts)

    def _get_crypto_context(self, topic: str) -> str:
        """Get crypto/blockchain context."""
        parts = []

        try:
            # Get recent crypto spider data
            if self.spider_service:
                crypto_data = self.spider_service.get_category_data(
                    category='crypto',
                    hours=24,
                    limit=5
                )
                if crypto_data:
                    parts.append("## Crypto Market Intelligence (from our spiders)")
                    for item in crypto_data[:3]:
                        title = item.get('title', '')[:80]
                        parts.append(f"- {title}")
        except Exception as e:
            logger.debug(f"Could not fetch crypto data: {e}")

        # Get on-chain data if available
        try:
            from core.models_unified_system import AgentExecution
            whale_analyses = AgentExecution.objects.filter(
                Q(agent__name__icontains='whale') | Q(agent__name__icontains='blockchain'),
                created_at__gte=timezone.now() - timedelta(days=7),
                status='completed'
            ).order_by('-created_at')[:3]

            if whale_analyses.exists():
                parts.append("## Recent On-Chain Analysis")
                for analysis in whale_analyses:
                    agent_name = analysis.agent.name if analysis.agent else "BlockchainAgent"
                    parts.append(f"- {agent_name} analysis completed")
        except Exception as _e:
            logger.warning(
                "domain_context._get_crypto_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        parts.extend([
            "",
            "## Crypto Content Guidelines",
            "- Reference on-chain data and whale movements",
            "- Include TVL, volume, and market cap metrics",
            "- Cite smart contract interactions when relevant",
            "- Use 'Our chain analysis shows...' not 'Reports indicate...'",
        ])

        return "\n".join(parts)

    def _get_ai_tech_context(self, topic: str) -> str:
        """Get AI/Technology context - this is where we shine!"""
        parts = []

        try:
            # Our own agent ecosystem stats
            from core.models_unified_system import Agent, AgentExecution

            agent_count = Agent.objects.filter(is_active=True).count()
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()

            parts.append("## Platform AI Capabilities (Our Lived Experience)")
            parts.append(f"- Active agents: {agent_count}")
            parts.append(f"- Agent executions this week: {recent_executions}")

            # Recent successful agent patterns
            successful = AgentExecution.objects.filter(
                status='completed',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values('agent__name').annotate(
                count=Count('id')
            ).order_by('-count')[:3]

            if successful:
                parts.append("- Most active agents:")
                for item in successful:
                    parts.append(f"  • {item['agent__name']}: {item['count']} executions")

        except Exception as e:
            logger.debug(f"Could not fetch AI stats: {e}")

        # Get tech spider data
        try:
            if self.spider_service:
                tech_data = self.spider_service.get_category_data(
                    category='tech',
                    hours=48,
                    limit=5
                )
                if tech_data:
                    parts.append("## Tech News (from our spider network)")
                    for item in tech_data[:3]:
                        title = item.get('title', '')[:80]
                        parts.append(f"- {title}")
        except Exception as _e:
            logger.warning(
                "domain_context._get_ai_tech_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        parts.extend([
            "",
            "## AI/Tech Content Guidelines",
            "- Reference our agent architecture and learnings",
            "- Include specific technical details (models, frameworks)",
            "- Share what we've built and learned firsthand",
            "- Use 'In our implementation...' not 'Experts recommend...'",
        ])

        return "\n".join(parts)

    def _get_legal_context(self, topic: str) -> str:
        """Get legal context from legal spiders."""
        parts = []

        try:
            if self.spider_service:
                legal_data = self.spider_service.get_category_data(
                    category='legal',
                    hours=72,
                    limit=5
                )
                if legal_data:
                    parts.append("## Legal Intelligence (from our spiders)")
                    for item in legal_data[:3]:
                        title = item.get('title', '')[:80]
                        source = item.get('source', 'Legal Source')
                        parts.append(f"- {title} (via {source})")
        except Exception as _e:
            logger.warning(
                "domain_context._get_legal_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        parts.extend([
            "",
            "## Legal Content Guidelines",
            "- Reference specific cases and precedents",
            "- Include jurisdiction-specific information",
            "- Cite authoritative legal sources",
            "- Add disclaimer for non-attorney readers",
        ])

        return "\n".join(parts)

    def _get_career_context(self, topic: str) -> str:
        """Get career/jobs context from platform data."""
        parts = []

        try:
            # Get job application stats if available
            from core.models import JobApplication

            recent_apps = JobApplication.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            )

            if recent_apps.exists():
                total = recent_apps.count()
                interviews = recent_apps.filter(status='interview').count()
                offers = recent_apps.filter(status='offer').count()

                parts.append("## Platform Job Search Activity (Last 30 Days)")
                parts.append(f"- Applications tracked: {total}")
                if total > 0:
                    parts.append(f"- Interview rate: {(interviews/total)*100:.1f}%")
                    parts.append(f"- Offer rate: {(offers/total)*100:.1f}%")
        except Exception as _e:
            logger.warning(
                "domain_context._get_career_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        # Get job spider data
        try:
            if self.spider_service:
                job_data = self.spider_service.get_category_data(
                    category='jobs',
                    hours=48,
                    limit=5
                )
                if job_data:
                    parts.append("## Job Market Trends (from our spiders)")
                    for item in job_data[:3]:
                        title = item.get('title', '')[:80]
                        parts.append(f"- {title}")
        except Exception as _e:
            logger.warning(
                "domain_context._get_career_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        parts.extend([
            "",
            "## Career Content Guidelines",
            "- Include specific salary ranges and market data",
            "- Reference application success patterns we've observed",
            "- Share resume/interview insights from our tracking",
            "- Use 'Our job tracker shows...' not 'Career experts say...'",
        ])

        return "\n".join(parts)

    def _get_health_context(self, topic: str) -> str:
        """Get health/wellness context."""
        parts = []

        try:
            if self.spider_service:
                health_data = self.spider_service.get_category_data(
                    category='health',
                    hours=48,
                    limit=5
                )
                if health_data:
                    parts.append("## Health Research (from our spiders)")
                    for item in health_data[:3]:
                        title = item.get('title', '')[:80]
                        parts.append(f"- {title}")
        except Exception as _e:
            logger.warning(
                "domain_context._get_health_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        parts.extend([
            "",
            "## Health Content Guidelines",
            "- Reference peer-reviewed research when possible",
            "- Include specific data points and studies",
            "- Add appropriate health disclaimers",
            "- Avoid making medical claims",
        ])

        return "\n".join(parts)

    def _get_education_context(self, topic: str) -> str:
        """Get education/learning context."""
        parts = []

        try:
            if self.spider_service:
                edu_data = self.spider_service.get_category_data(
                    category='education',
                    hours=72,
                    limit=5
                )
                if edu_data:
                    parts.append("## Education Trends (from our spiders)")
                    for item in edu_data[:3]:
                        title = item.get('title', '')[:80]
                        parts.append(f"- {title}")
        except Exception as _e:
            logger.warning(
                "domain_context._get_education_context: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        parts.extend([
            "",
            "## Education Content Guidelines",
            "- Include specific learning outcomes",
            "- Reference course ratings and reviews where available",
            "- Provide actionable learning paths",
        ])

        return "\n".join(parts)

    def _get_general_context(self, topic: str) -> str:
        """Fallback for topics that don't match a specific domain."""
        parts = [
            "## General Content Guidelines",
            "- Write with authority based on platform data",
            "- Include specific examples and data points",
            "- Use first-person platform voice where appropriate",
        ]
        return "\n".join(parts)

    # =========================================================================
    # Main Context Builder
    # =========================================================================

    def build_context(
        self,
        topic: str,
        content: str = "",
        max_domains: int = 2
    ) -> str:
        """
        Build complete context for content generation.

        Detects all relevant domains and combines their context.

        Args:
            topic: Blog topic/title
            content: Optional existing content for context detection
            max_domains: Maximum number of domain contexts to include

        Returns:
            Formatted context string for prompt injection
        """
        # Detect all relevant domains
        detected_domains = self.detect_all_domains(topic, content)

        if not detected_domains:
            return self._get_general_context(topic)

        context_parts = [
            "=" * 60,
            "DOMAIN CONTENT CONTEXT (Session 891)",
            "Use this real platform data to write with authority.",
            "=" * 60,
        ]

        # Map domains to context builders
        domain_builders = {
            'finance': self._get_finance_context,
            'crypto': self._get_crypto_context,
            'sports': self._get_sports_context,
            'betting': self._get_sports_context,  # Betting uses sports context
            'ai_tech': self._get_ai_tech_context,
            'legal': self._get_legal_context,
            'career': self._get_career_context,
            'health': self._get_health_context,
            'education': self._get_education_context,
        }

        # Add context for top domains
        domains_added = 0
        for domain, confidence in detected_domains[:max_domains]:
            if domain in domain_builders and confidence >= 0.2:
                try:
                    domain_ctx = domain_builders[domain](topic)
                    if domain_ctx:
                        context_parts.append(f"\n## {domain.upper()} CONTEXT (confidence: {confidence:.0%})")
                        context_parts.append(domain_ctx)
                        domains_added += 1
                        logger.info(f"📚 Session 891: Added {domain} context ({confidence:.0%} confidence)")
                except Exception as e:
                    logger.warning(f"Error building {domain} context: {e}")

        if domains_added == 0:
            context_parts.append(self._get_general_context(topic))

        context_parts.append("\n" + "=" * 60)

        return "\n".join(context_parts)


# =============================================================================
# Module-level functions
# =============================================================================

_domain_context_builder = None


def get_domain_content_context(topic: str, content: str = "", **kwargs) -> str:
    """
    Get domain-specific content context for a topic.

    This is the main entry point - automatically detects domains
    and returns relevant platform context.

    Usage:
        from core.services.domain_content_context import get_domain_content_context

        context = get_domain_content_context(
            topic="NVIDIA Stock Analysis and AI Chip Market"
        )
        # Returns combined finance + ai_tech context
    """
    global _domain_context_builder

    if _domain_context_builder is None:
        _domain_context_builder = DomainContentContextBuilder()

    return _domain_context_builder.build_context(topic, content, **kwargs)


def detect_content_domain(topic: str, content: str = "") -> Tuple[str, float]:
    """
    Detect the primary domain of content.

    Returns:
        Tuple of (domain_name, confidence)
    """
    global _domain_context_builder

    if _domain_context_builder is None:
        _domain_context_builder = DomainContentContextBuilder()

    return _domain_context_builder.detect_domain(topic, content)


def detect_all_content_domains(topic: str, content: str = "") -> List[Tuple[str, float]]:
    """
    Detect all relevant domains for content.

    Returns:
        List of (domain, confidence) tuples sorted by confidence
    """
    global _domain_context_builder

    if _domain_context_builder is None:
        _domain_context_builder = DomainContentContextBuilder()

    return _domain_context_builder.detect_all_domains(topic, content)

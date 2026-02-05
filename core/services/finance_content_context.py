"""
Finance Content Context Builder
Session 891: Inject financial system data into blog content.

Problem: Finance blogs lack "lived experience" - they read like generic journalism
instead of insights from a platform that actually tracks markets and predictions.

Solution: Pull real data from:
1. Financial spiders (theodds, yahoo_finance, kalshi, polygon, etc.)
2. Platform betting/prediction history
3. Agent market analysis memory

This gives finance content the same "builder voice" that AI Dev content has.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q

logger = logging.getLogger(__name__)


class FinanceContentContextBuilder:
    """
    Session 891: Build rich context for finance/markets content.

    Injects:
    - Real market data from spiders
    - Platform prediction history (what we got right/wrong)
    - Advisor wisdom (Warren Buffett, Ray Dalio)
    - Agent analysis memory
    """

    FINANCE_KEYWORDS = [
        'stock', 'market', 'invest', 'trading', 'portfolio', 'earnings',
        'nasdaq', 'dow', 'sp500', 's&p', 'bull', 'bear', 'dividend',
        'nvidia', 'tesla', 'apple', 'amazon', 'netflix', 'meta', 'google',
        'crypto', 'bitcoin', 'ethereum', 'finance', 'financial', 'economy',
        'fed', 'interest rate', 'inflation', 'recession', 'gdp',
        'betting', 'odds', 'prediction', 'wager', 'spread', 'moneyline'
    ]

    BETTING_KEYWORDS = [
        'betting', 'odds', 'spread', 'moneyline', 'over/under', 'parlay',
        'prediction', 'wager', 'sports', 'nfl', 'nba', 'mlb', 'nhl',
        'arbitrage', 'line movement', 'sharp', 'public'
    ]

    def __init__(self):
        self._spider_service = None
        self._advisor_service = None

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

    def is_finance_topic(self, topic: str, content: str = "") -> bool:
        """Check if topic/content is finance-related."""
        combined = f"{topic} {content}".lower()
        return any(kw in combined for kw in self.FINANCE_KEYWORDS)

    def is_betting_topic(self, topic: str, content: str = "") -> bool:
        """Check if topic/content is betting/odds-related."""
        combined = f"{topic} {content}".lower()
        return any(kw in combined for kw in self.BETTING_KEYWORDS)

    def get_market_data_context(self, topic: str) -> str:
        """
        Get real market data from spiders.

        Returns formatted context about recent market movements.

        Session 936: Fixed to use get_market_insights() instead of non-existent
        get_aggregated_intelligence() method.
        """
        context_parts = []

        try:
            if not self.spider_service:
                return ""

            # Session 936: Use actual method that exists in SpiderIntelligenceService
            # get_market_insights() returns market data from financial spiders
            market_data = self.spider_service.get_market_insights()

            if market_data:
                context_parts.append("## Recent Market Intelligence (from our spider network)")

                # Extract crypto prices if available
                if market_data.get('crypto_prices'):
                    context_parts.append("### Crypto Markets")
                    for coin in market_data['crypto_prices'][:5]:
                        name = coin.get('name', 'Unknown')
                        price = coin.get('price', 0)
                        change = coin.get('change_24h', 0)
                        context_parts.append(f"- {name}: ${price:,.2f} ({change:+.2f}%)")

                # Extract stock data if available
                if market_data.get('stock_movers'):
                    context_parts.append("### Stock Movers")
                    for stock in market_data['stock_movers'][:5]:
                        symbol = stock.get('symbol', '???')
                        change = stock.get('change_percent', 0)
                        context_parts.append(f"- {symbol}: {change:+.2f}%")

                # Also get trending topics from financial category
                trending = self.spider_service.get_trending_topics(
                    category='financial',
                    hours=48,
                    limit=5
                )
                if trending:
                    context_parts.append("### Trending Financial Topics")
                    for item in trending[:5]:
                        title = item.get('title', item.get('topic', 'Unknown'))
                        source = item.get('source', item.get('spider', 'Unknown'))
                        context_parts.append(f"- {title} (via {source})")

        except Exception as e:
            logger.debug(f"Could not fetch market data: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def get_betting_data_context(self) -> str:
        """
        Get betting/odds data from theodds spider and platform history.
        """
        context_parts = []

        try:
            # Get recent odds data
            from core.models_sports_betting import Wager, BettingOpportunity

            # Get recent platform betting activity
            recent_wagers = Wager.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:10]

            if recent_wagers.exists():
                wins = recent_wagers.filter(outcome='win').count()
                losses = recent_wagers.filter(outcome='loss').count()
                total = wins + losses

                if total > 0:
                    win_rate = (wins / total) * 100
                    context_parts.append(f"## Platform Betting Performance (Last 30 Days)")
                    context_parts.append(f"- Win rate: {win_rate:.1f}% ({wins}W-{losses}L)")

            # Get recent arbitrage opportunities
            arb_opps = BettingOpportunity.objects.filter(
                opportunity_type='arbitrage',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()

            if arb_opps > 0:
                context_parts.append(f"- Arbitrage opportunities found this week: {arb_opps}")

        except Exception as e:
            logger.debug(f"Could not fetch betting data: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def get_prediction_history_context(self) -> str:
        """
        Get platform prediction history - what we got right/wrong.

        This is the "lived experience" that makes content feel authentic.
        """
        context_parts = []

        try:
            from core.models_unified_system import AgentExecution

            # Get recent market analysis agent executions
            market_analyses = AgentExecution.objects.filter(
                Q(agent__name__icontains='market') |
                Q(agent__name__icontains='stock') |
                Q(agent__name__icontains='prediction'),
                created_at__gte=timezone.now() - timedelta(days=30),
                status='completed'
            ).order_by('-created_at')[:5]

            if market_analyses.exists():
                context_parts.append("## Recent Agent Market Analysis")
                for analysis in market_analyses:
                    # Extract key insight from result if available
                    result_preview = str(analysis.result)[:100] if analysis.result else "Analysis completed"
                    context_parts.append(f"- {analysis.agent.name}: {result_preview}...")

        except Exception as e:
            logger.debug(f"Could not fetch prediction history: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def get_advisor_wisdom_context(self, topic: str) -> str:
        """
        Get relevant advisor wisdom for finance content.

        Maps to Warren Buffett, Ray Dalio, Cathie Wood, etc.
        """
        context_parts = []

        try:
            from core.models_unified_system import Advisor

            # Get finance-related advisors
            finance_advisors = Advisor.objects.filter(
                Q(expertise__icontains='invest') |
                Q(expertise__icontains='market') |
                Q(expertise__icontains='finance') |
                Q(name__in=['Warren Buffett', 'Ray Dalio', 'Cathie Wood', 'Peter Lynch']),
                is_active=True
            )[:3]

            if finance_advisors.exists():
                context_parts.append("## Financial Advisor Perspectives")
                for advisor in finance_advisors:
                    if advisor.wisdom:
                        context_parts.append(f"- {advisor.name}: \"{advisor.wisdom[:150]}...\"")

        except Exception as e:
            logger.debug(f"Could not fetch advisor wisdom: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def build_finance_context(
        self,
        topic: str,
        content: str = "",
        include_market_data: bool = True,
        include_betting: bool = True,
        include_predictions: bool = True,
        include_advisors: bool = True
    ) -> str:
        """
        Build complete finance context for content generation.

        Args:
            topic: Blog topic/title
            content: Optional existing content for context detection
            include_*: Flags to control which context sections to include

        Returns:
            Formatted context string for prompt injection
        """
        if not self.is_finance_topic(topic, content):
            return ""

        context_parts = [
            "=" * 60,
            "FINANCE CONTENT CONTEXT (Session 891)",
            "Use this real platform data to write with authority.",
            "Reference specific data points - this is YOUR lived experience.",
            "=" * 60,
        ]

        # Market data from spiders
        if include_market_data:
            market_ctx = self.get_market_data_context(topic)
            if market_ctx:
                context_parts.append(market_ctx)

        # Betting data if relevant
        if include_betting and self.is_betting_topic(topic, content):
            betting_ctx = self.get_betting_data_context()
            if betting_ctx:
                context_parts.append(betting_ctx)

        # Prediction history
        if include_predictions:
            pred_ctx = self.get_prediction_history_context()
            if pred_ctx:
                context_parts.append(pred_ctx)

        # Advisor wisdom
        if include_advisors:
            advisor_ctx = self.get_advisor_wisdom_context(topic)
            if advisor_ctx:
                context_parts.append(advisor_ctx)

        # Writing guidance for finance content
        context_parts.extend([
            "",
            "## Finance Content Writing Rules",
            "- Reference our spider data with specifics: 'Our market spiders tracked X movement'",
            "- Include platform predictions: 'Last month we called Y, here's what happened'",
            "- Cite advisor frameworks: 'As Buffett would say about margin of safety...'",
            "- Use first-person platform voice: 'Our analysis shows...' not 'Analysts say...'",
            "- Include specific numbers, dates, percentages from the data above",
            "",
            "=" * 60,
        ])

        return "\n".join(context_parts)


# Singleton instance
_finance_context_builder = None


def get_finance_content_context(
    topic: str,
    content: str = "",
    **kwargs
) -> str:
    """
    Get finance content context for a blog topic.

    Usage:
        from core.services.finance_content_context import get_finance_content_context

        context = get_finance_content_context(
            topic="NVIDIA Stock Analysis: Is Now the Time to Buy?",
            include_betting=False
        )
        # Inject into ContentWriterAgent prompt
    """
    global _finance_context_builder

    if _finance_context_builder is None:
        _finance_context_builder = FinanceContentContextBuilder()

    return _finance_context_builder.build_finance_context(topic, content, **kwargs)


def is_finance_topic(topic: str, content: str = "") -> bool:
    """Check if a topic is finance-related."""
    global _finance_context_builder

    if _finance_context_builder is None:
        _finance_context_builder = FinanceContentContextBuilder()

    return _finance_context_builder.is_finance_topic(topic, content)

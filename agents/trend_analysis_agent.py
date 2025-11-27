"""
Trend Analysis Agent - Spider Intelligence Analyst
===================================================

Session 209: Created as part of Phase A - Spider Intelligence Enhancement

This agent provides intelligent trend analysis by:
1. Analyzing patterns across all spider data
2. Generating daily/weekly trend reports
3. Identifying emerging opportunities
4. Detecting market shifts and tech trends
5. Providing actionable insights from spider intelligence

The TrendAnalysisAgent works with SpiderIntelligenceService to transform
raw spider data into strategic intelligence.

Example:
    agent = TrendAnalysisAgent()

    # Get daily intelligence briefing
    report = agent.generate_daily_briefing()

    # Analyze specific sector
    tech_analysis = agent.analyze_sector('tech', days=7)

    # Find emerging opportunities
    opportunities = agent.find_emerging_opportunities()
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class TrendReport:
    """Result from trend analysis."""
    success: bool
    report_type: str  # 'daily', 'weekly', 'sector', 'opportunity'
    generated_at: datetime
    period_start: datetime
    period_end: datetime

    # Core analysis
    top_trends: List[Dict[str, Any]] = field(default_factory=list)
    emerging_topics: List[Dict[str, Any]] = field(default_factory=list)
    declining_topics: List[Dict[str, Any]] = field(default_factory=list)

    # Sector breakdowns
    tech_highlights: List[str] = field(default_factory=list)
    market_highlights: List[str] = field(default_factory=list)
    job_highlights: List[str] = field(default_factory=list)

    # Opportunities
    opportunities: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    data_sources: List[str] = field(default_factory=list)
    total_data_points: int = 0
    confidence_score: float = 0.0

    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'report_type': self.report_type,
            'generated_at': self.generated_at.isoformat(),
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat(),
            },
            'top_trends': self.top_trends,
            'emerging_topics': self.emerging_topics,
            'declining_topics': self.declining_topics,
            'highlights': {
                'tech': self.tech_highlights,
                'market': self.market_highlights,
                'jobs': self.job_highlights,
            },
            'opportunities': self.opportunities,
            'metadata': {
                'data_sources': self.data_sources,
                'total_data_points': self.total_data_points,
                'confidence_score': self.confidence_score,
            },
            'error': self.error,
        }

    def to_markdown(self) -> str:
        """Generate markdown-formatted report."""
        lines = [
            f"# {self.report_type.title()} Trend Report",
            f"*Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M')}*",
            f"*Period: {self.period_start.strftime('%Y-%m-%d')} to {self.period_end.strftime('%Y-%m-%d')}*",
            "",
        ]

        if self.top_trends:
            lines.append("## Top Trends")
            for i, trend in enumerate(self.top_trends[:5], 1):
                lines.append(f"{i}. **{trend.get('topic', 'Unknown')}** - {trend.get('mentions', 0)} mentions ({', '.join(trend.get('sources', []))})")
            lines.append("")

        if self.emerging_topics:
            lines.append("## Emerging Topics")
            for topic in self.emerging_topics[:5]:
                lines.append(f"- {topic.get('topic', 'Unknown')} (+{topic.get('growth', 0):.0%} growth)")
            lines.append("")

        if self.tech_highlights:
            lines.append("## Tech Highlights")
            for highlight in self.tech_highlights[:5]:
                lines.append(f"- {highlight}")
            lines.append("")

        if self.market_highlights:
            lines.append("## Market Highlights")
            for highlight in self.market_highlights[:5]:
                lines.append(f"- {highlight}")
            lines.append("")

        if self.job_highlights:
            lines.append("## Job Market")
            for highlight in self.job_highlights[:5]:
                lines.append(f"- {highlight}")
            lines.append("")

        if self.opportunities:
            lines.append("## Opportunities")
            for opp in self.opportunities[:5]:
                lines.append(f"- **{opp.get('title', 'Opportunity')}**: {opp.get('description', '')}")
            lines.append("")

        lines.append(f"---")
        lines.append(f"*Data sources: {', '.join(self.data_sources)} | {self.total_data_points} data points | Confidence: {self.confidence_score:.0%}*")

        return "\n".join(lines)


class TrendAnalysisAgent:
    """
    Intelligent trend analysis agent that transforms spider data into insights.

    This agent analyzes patterns across all collected spider data to:
    - Identify trending topics and emerging themes
    - Generate comprehensive intelligence reports
    - Find actionable opportunities
    - Track market and tech sector shifts
    """

    # Opportunity detection keywords
    OPPORTUNITY_KEYWORDS = {
        'tech': ['new framework', 'breakthrough', 'launch', 'release', 'announced'],
        'market': ['surge', 'rally', 'breakout', 'all-time high', 'opportunity'],
        'jobs': ['hiring', 'remote', 'high salary', 'urgent', 'multiple positions'],
        'content': ['viral', 'trending', 'popular', 'featured'],
    }

    def __init__(self):
        """Initialize TrendAnalysisAgent with SpiderIntelligenceService."""
        self._intelligence_service = None
        self._spider_data_model = None

    @property
    def intelligence_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._intelligence_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._intelligence_service = SpiderIntelligenceService()
        return self._intelligence_service

    @property
    def SpiderData(self):
        """Lazy load SpiderData model."""
        if self._spider_data_model is None:
            from core.models_unified_system import SpiderData
            self._spider_data_model = SpiderData
        return self._spider_data_model

    def generate_daily_briefing(self) -> TrendReport:
        """
        Generate a comprehensive daily intelligence briefing.

        Returns:
            TrendReport with all daily insights
        """
        logger.info("Generating daily intelligence briefing...")

        try:
            from django.utils import timezone
            now = timezone.now()
            period_start = now - timedelta(hours=24)

            # Gather all intelligence
            trends = self.intelligence_service.get_trending_topics(hours=24, limit=15)
            market = self.intelligence_service.get_market_insights()
            tech = self.intelligence_service.get_tech_trends(hours=24, limit=10)
            jobs = self.intelligence_service.get_job_market_summary(hours=24, limit=10)
            summary = self.intelligence_service.get_data_summary(hours=24)

            # Analyze for emerging topics (compare 24h vs 48h)
            emerging = self._find_emerging_topics(hours_recent=24, hours_compare=48)

            # Find opportunities
            opportunities = self._find_opportunities(trends, market, tech, jobs)

            # Build highlights
            tech_highlights = self._build_tech_highlights(tech)
            market_highlights = self._build_market_highlights(market)
            job_highlights = self._build_job_highlights(jobs)

            # Calculate confidence based on data volume
            total_data = summary.get('total_items', 0)
            confidence = min(1.0, total_data / 100)  # Full confidence at 100+ data points

            return TrendReport(
                success=True,
                report_type='daily',
                generated_at=now,
                period_start=period_start,
                period_end=now,
                top_trends=trends[:10],
                emerging_topics=emerging,
                declining_topics=[],  # Would need historical comparison
                tech_highlights=tech_highlights,
                market_highlights=market_highlights,
                job_highlights=job_highlights,
                opportunities=opportunities,
                data_sources=list(summary.get('by_spider', {}).keys()),
                total_data_points=total_data,
                confidence_score=confidence,
            )

        except Exception as e:
            logger.error(f"Error generating daily briefing: {e}")
            from django.utils import timezone
            now = timezone.now()
            return TrendReport(
                success=False,
                report_type='daily',
                generated_at=now,
                period_start=now - timedelta(hours=24),
                period_end=now,
                error=str(e),
            )

    def generate_weekly_report(self) -> TrendReport:
        """
        Generate a comprehensive weekly trend report.

        Returns:
            TrendReport with weekly analysis and week-over-week comparisons
        """
        logger.info("Generating weekly trend report...")

        try:
            from django.utils import timezone
            now = timezone.now()
            period_start = now - timedelta(days=7)

            # Gather weekly intelligence
            trends = self.intelligence_service.get_trending_topics(hours=168, limit=20)
            market = self.intelligence_service.get_market_insights()
            tech = self.intelligence_service.get_tech_trends(hours=168, limit=15)
            jobs = self.intelligence_service.get_job_market_summary(hours=168, limit=20)
            summary = self.intelligence_service.get_data_summary(hours=168)

            # Week-over-week comparison
            emerging = self._find_emerging_topics(hours_recent=168, hours_compare=336)

            # Find opportunities
            opportunities = self._find_opportunities(trends, market, tech, jobs)

            # Build highlights
            tech_highlights = self._build_tech_highlights(tech)
            market_highlights = self._build_market_highlights(market)
            job_highlights = self._build_job_highlights(jobs)

            total_data = summary.get('total_items', 0)
            confidence = min(1.0, total_data / 200)

            return TrendReport(
                success=True,
                report_type='weekly',
                generated_at=now,
                period_start=period_start,
                period_end=now,
                top_trends=trends[:15],
                emerging_topics=emerging,
                declining_topics=[],
                tech_highlights=tech_highlights,
                market_highlights=market_highlights,
                job_highlights=job_highlights,
                opportunities=opportunities,
                data_sources=list(summary.get('by_spider', {}).keys()),
                total_data_points=total_data,
                confidence_score=confidence,
            )

        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            from django.utils import timezone
            now = timezone.now()
            return TrendReport(
                success=False,
                report_type='weekly',
                generated_at=now,
                period_start=now - timedelta(days=7),
                period_end=now,
                error=str(e),
            )

    def analyze_sector(self, sector: str, days: int = 7) -> TrendReport:
        """
        Analyze trends for a specific sector.

        Args:
            sector: Sector to analyze ('tech', 'financial', 'jobs', 'creative')
            days: Number of days to analyze

        Returns:
            TrendReport focused on the specified sector
        """
        logger.info(f"Analyzing sector: {sector} for {days} days")

        try:
            from django.utils import timezone
            now = timezone.now()
            hours = days * 24
            period_start = now - timedelta(days=days)

            # Get sector-specific trends
            trends = self.intelligence_service.get_trending_topics(
                category=sector, hours=hours, limit=20
            )

            summary = self.intelligence_service.get_data_summary(hours=hours)

            # Sector-specific data
            highlights = []
            if sector == 'tech':
                tech = self.intelligence_service.get_tech_trends(hours=hours, limit=15)
                highlights = self._build_tech_highlights(tech)
            elif sector == 'financial':
                market = self.intelligence_service.get_market_insights()
                highlights = self._build_market_highlights(market)
            elif sector == 'jobs':
                jobs = self.intelligence_service.get_job_market_summary(hours=hours, limit=15)
                highlights = self._build_job_highlights(jobs)

            total_data = summary.get('total_items', 0)

            return TrendReport(
                success=True,
                report_type=f'sector_{sector}',
                generated_at=now,
                period_start=period_start,
                period_end=now,
                top_trends=trends[:15],
                tech_highlights=highlights if sector == 'tech' else [],
                market_highlights=highlights if sector == 'financial' else [],
                job_highlights=highlights if sector == 'jobs' else [],
                data_sources=list(summary.get('by_spider', {}).keys()),
                total_data_points=total_data,
                confidence_score=min(1.0, total_data / 50),
            )

        except Exception as e:
            logger.error(f"Error analyzing sector {sector}: {e}")
            from django.utils import timezone
            now = timezone.now()
            return TrendReport(
                success=False,
                report_type=f'sector_{sector}',
                generated_at=now,
                period_start=now - timedelta(days=days),
                period_end=now,
                error=str(e),
            )

    def find_emerging_opportunities(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Find emerging opportunities across all sectors.

        Args:
            hours: Look back period

        Returns:
            List of opportunity dictionaries
        """
        try:
            trends = self.intelligence_service.get_trending_topics(hours=hours, limit=20)
            market = self.intelligence_service.get_market_insights()
            tech = self.intelligence_service.get_tech_trends(hours=hours)
            jobs = self.intelligence_service.get_job_market_summary(hours=hours)

            return self._find_opportunities(trends, market, tech, jobs)

        except Exception as e:
            logger.error(f"Error finding opportunities: {e}")
            return []

    def get_insights_for_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Get relevant trend insights for a user prompt.

        This is used by other agents (like PersonalAssistant) to enhance
        their responses with trend data.

        Args:
            prompt: User's prompt/question

        Returns:
            Dict with relevant insights
        """
        try:
            # Use the intelligence service's prompt analysis
            insights = self.intelligence_service.get_insights_for_prompt(prompt, limit=5)

            # Add trend context
            trends = self.intelligence_service.get_trending_topics(hours=24, limit=5)

            return {
                'relevant_data': insights,
                'current_trends': trends[:3],
                'has_insights': bool(insights.get('results')),
            }

        except Exception as e:
            logger.error(f"Error getting insights for prompt: {e}")
            return {'relevant_data': {}, 'current_trends': [], 'has_insights': False}

    # ==================== Private Helper Methods ====================

    def _find_emerging_topics(self, hours_recent: int, hours_compare: int) -> List[Dict[str, Any]]:
        """Find topics that are growing in mentions."""
        try:
            recent_trends = self.intelligence_service.get_trending_topics(
                hours=hours_recent, limit=30
            )
            older_trends = self.intelligence_service.get_trending_topics(
                hours=hours_compare, limit=50
            )

            # Create lookup for older trends
            older_lookup = {t.get('topic', ''): t.get('mentions', 0) for t in older_trends}

            emerging = []
            for trend in recent_trends:
                topic = trend.get('topic', '')
                recent_mentions = trend.get('mentions', 0)
                older_mentions = older_lookup.get(topic, 0)

                # Calculate growth rate
                if older_mentions == 0 and recent_mentions > 0:
                    # New topic
                    emerging.append({
                        'topic': topic,
                        'mentions': recent_mentions,
                        'growth': float('inf'),
                        'is_new': True,
                        'sources': trend.get('sources', []),
                    })
                elif older_mentions > 0:
                    growth = (recent_mentions - older_mentions) / older_mentions
                    if growth > 0.2:  # 20% growth threshold
                        emerging.append({
                            'topic': topic,
                            'mentions': recent_mentions,
                            'growth': growth,
                            'is_new': False,
                            'sources': trend.get('sources', []),
                        })

            # Sort by growth rate (new topics first)
            emerging.sort(key=lambda x: (x.get('is_new', False), x.get('growth', 0)), reverse=True)
            return emerging[:10]

        except Exception as e:
            logger.error(f"Error finding emerging topics: {e}")
            return []

    def _find_opportunities(
        self,
        trends: List[Dict],
        market: Dict,
        tech: Dict,
        jobs: Dict
    ) -> List[Dict[str, Any]]:
        """Extract actionable opportunities from the data."""
        opportunities = []

        # Tech opportunities
        for discussion in tech.get('discussions', [])[:5]:
            title = discussion.get('title', '')
            if any(kw in title.lower() for kw in self.OPPORTUNITY_KEYWORDS['tech']):
                opportunities.append({
                    'type': 'tech',
                    'title': title[:100],
                    'description': f"Hot tech topic from {discussion.get('source', 'unknown')}",
                    'url': discussion.get('url'),
                    'score': discussion.get('score', 0),
                })

        # Market opportunities
        for crypto in market.get('crypto', [])[:5]:
            change = crypto.get('change_24h', 0) or 0
            if change > 5:  # 5% gain
                opportunities.append({
                    'type': 'market',
                    'title': f"{crypto.get('name', 'Unknown')} up {change:.1f}%",
                    'description': f"Current price: ${crypto.get('price', 0):,.2f}",
                    'symbol': crypto.get('symbol'),
                    'change': change,
                })

        # Job opportunities
        for job in jobs.get('jobs', [])[:5]:
            title = job.get('title', '')
            if any(kw in title.lower() for kw in self.OPPORTUNITY_KEYWORDS['jobs']):
                opportunities.append({
                    'type': 'job',
                    'title': title[:100],
                    'description': f"From {job.get('source', 'unknown')}",
                    'url': job.get('url'),
                    'company': job.get('company'),
                })

        # Trending topic opportunities
        for trend in trends[:5]:
            if trend.get('mentions', 0) >= 3:  # Multiple mentions = hot topic
                opportunities.append({
                    'type': 'trend',
                    'title': f"Hot topic: {trend.get('topic', 'Unknown')}",
                    'description': f"{trend.get('mentions', 0)} mentions across {len(trend.get('sources', []))} sources",
                    'sources': trend.get('sources', []),
                })

        return opportunities[:10]

    def _build_tech_highlights(self, tech: Dict) -> List[str]:
        """Build tech highlight strings."""
        highlights = []

        discussions = tech.get('discussions', [])
        for d in discussions[:5]:
            title = d.get('title', '')[:80]
            source = d.get('source', 'unknown')
            score = d.get('score', 0)
            highlights.append(f"{title} ({source}, {score} points)")

        topics = tech.get('topics', [])
        if topics:
            # Topics are dicts with 'topic' and 'count' keys
            topic_names = [t.get('topic', str(t)) if isinstance(t, dict) else str(t) for t in topics[:5]]
            highlights.append(f"Hot topics: {', '.join(topic_names)}")

        return highlights

    def _build_market_highlights(self, market: Dict) -> List[str]:
        """Build market highlight strings."""
        highlights = []

        for crypto in market.get('crypto', [])[:5]:
            name = crypto.get('name', 'Unknown')
            price = crypto.get('price', 0)
            change = crypto.get('change_24h', 0) or 0
            direction = "+" if change >= 0 else ""
            highlights.append(f"{name}: ${price:,.2f} ({direction}{change:.1f}%)")

        for stock in market.get('stocks', [])[:3]:
            symbol = stock.get('symbol', 'Unknown')
            price = stock.get('price', 0)
            highlights.append(f"{symbol}: ${price:,.2f}")

        return highlights

    def _build_job_highlights(self, jobs: Dict) -> List[str]:
        """Build job market highlight strings."""
        highlights = []

        total = jobs.get('total_found', 0)
        if total:
            highlights.append(f"Found {total} remote job opportunities")

        categories = jobs.get('categories', [])
        if categories:
            # Categories are dicts with 'category' and 'count' keys
            top_cats = [c.get('category', str(c)) if isinstance(c, dict) else str(c) for c in categories[:3]]
            highlights.append(f"Top categories: {', '.join(top_cats)}")

        for job in jobs.get('jobs', [])[:3]:
            title = job.get('title', '')[:60]
            company = job.get('company', 'Unknown')
            highlights.append(f"{title} at {company}")

        return highlights


# Convenience function for quick access
def get_daily_briefing() -> TrendReport:
    """Quick function to get daily intelligence briefing."""
    agent = TrendAnalysisAgent()
    return agent.generate_daily_briefing()


def get_weekly_report() -> TrendReport:
    """Quick function to get weekly trend report."""
    agent = TrendAnalysisAgent()
    return agent.generate_weekly_report()

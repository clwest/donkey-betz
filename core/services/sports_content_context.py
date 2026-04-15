"""
Sports Content Context Builder
Session 891: Inject sports/betting data into blog content.

Problem: Sports content lacks real platform experience - it reads like generic
sports journalism instead of insights from a platform that tracks real odds,
places real bets, and analyzes real line movements.

Solution: Pull real data from:
1. TheOdds spider (live odds from 40+ bookmakers)
2. Platform betting history (wins/losses, ROI, streaks)
3. Agent analysis memory (SportsOddsAnalyst insights)
4. Sports-focused advisor perspectives

This gives sports content the same "builder voice" that AI Dev content has.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Q

logger = logging.getLogger(__name__)


class SportsContentContextBuilder:
    """
    Session 891: Build rich context for sports/betting content.

    Injects:
    - Live odds data from theodds spider
    - Platform betting performance (W/L record, ROI, streaks)
    - Value bet opportunities identified
    - Sports analyst agent memory
    """

    # Sports-related keywords for topic detection
    SPORTS_KEYWORDS = [
        # Major US Sports
        'nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ncaaf', 'ncaab',
        'football', 'basketball', 'baseball', 'hockey', 'soccer',
        # Teams/Leagues
        'super bowl', 'world series', 'stanley cup', 'playoffs', 'finals',
        'premier league', 'champions league', 'mls', 'la liga', 'bundesliga',
        # Combat Sports
        'ufc', 'mma', 'boxing', 'fight', 'knockout', 'submission',
        # Other Sports
        'tennis', 'golf', 'masters', 'wimbledon', 'us open',
        # General Sports
        'athlete', 'game', 'match', 'championship', 'tournament',
        'season', 'draft', 'trade', 'roster', 'injury', 'lineup',
    ]

    BETTING_KEYWORDS = [
        # Betting Terms
        'betting', 'bet', 'wager', 'odds', 'spread', 'moneyline', 'money line',
        'over/under', 'total', 'parlay', 'teaser', 'prop', 'props',
        'handicap', 'handicapping', 'point spread',
        # Betting Concepts
        'value bet', 'arbitrage', 'arb', 'line movement', 'sharp', 'square',
        'vig', 'juice', 'book', 'bookmaker', 'sportsbook',
        'bankroll', 'units', 'roi', 'win rate',
        # Prediction Terms
        'pick', 'picks', 'prediction', 'predictions', 'favorite', 'underdog',
        'lock', 'fade', 'tail', 'best bet', 'sure thing',
    ]

    def __init__(self):
        self._spider_service = None
        self._odds_spider = None

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

    @property
    def odds_spider(self):
        """Lazy load TheOdds spider."""
        if self._odds_spider is None:
            try:
                from ai_core.spiders.specialized.theodds_spider import TheOddsSpider
                self._odds_spider = TheOddsSpider()
            except Exception as e:
                logger.warning(f"Could not load theodds spider: {e}")
        return self._odds_spider

    def is_sports_topic(self, topic: str, content: str = "") -> bool:
        """Check if topic/content is sports-related."""
        combined = f"{topic} {content}".lower()
        return any(kw in combined for kw in self.SPORTS_KEYWORDS)

    def is_betting_topic(self, topic: str, content: str = "") -> bool:
        """Check if topic/content is betting-related."""
        combined = f"{topic} {content}".lower()
        return any(kw in combined for kw in self.BETTING_KEYWORDS)

    def get_live_odds_context(self, topic: str) -> str:
        """
        Get live odds data from TheOdds spider.

        Returns formatted context about current betting lines.
        """
        context_parts = []

        try:
            # Detect which sport to fetch
            topic_lower = topic.lower()
            sport_key = None

            # Map topic keywords to sport keys
            sport_mapping = {
                ('nfl', 'football', 'super bowl'): 'americanfootball_nfl',
                ('nba', 'basketball'): 'basketball_nba',
                ('mlb', 'baseball', 'world series'): 'baseball_mlb',
                ('nhl', 'hockey', 'stanley cup'): 'icehockey_nhl',
                ('ufc', 'mma', 'fight'): 'mma_mixed_martial_arts',
                ('soccer', 'premier league', 'epl'): 'soccer_epl',
                ('ncaaf', 'college football'): 'americanfootball_ncaaf',
                ('ncaab', 'college basketball', 'march madness'): 'basketball_ncaab',
            }

            for keywords, key in sport_mapping.items():
                if any(kw in topic_lower for kw in keywords):
                    sport_key = key
                    break

            if sport_key and self.odds_spider:
                # Fetch upcoming games for this sport
                games = self.odds_spider.get_upcoming_games(
                    sport_key=sport_key,
                    markets=['h2h', 'spreads', 'totals'],
                    limit=5
                )

                if games:
                    sport_name = sport_key.split('_')[-1].upper()
                    context_parts.append(f"## Live {sport_name} Odds (from our spider network)")
                    for game in games[:3]:
                        matchup = game.get('matchup', 'TBD')
                        spread = game.get('spread', 'N/A')
                        total = game.get('total', 'N/A')
                        context_parts.append(f"- {matchup}: Spread {spread}, O/U {total}")

        except Exception as e:
            logger.debug(f"Could not fetch live odds: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def get_platform_betting_stats(self) -> str:
        """
        Get platform betting performance from PlacedWager/BettingStats.

        This is the "lived experience" that makes sports content feel authentic.
        """
        context_parts = []

        try:
            from core.models_betting import PlacedWager, BettingStats

            # Get recent wagers for platform-wide stats
            recent_wagers = PlacedWager.objects.filter(
                placed_at__gte=timezone.now() - timedelta(days=30)
            ).exclude(status='pending')

            if recent_wagers.exists():
                wins = recent_wagers.filter(status='won').count()
                losses = recent_wagers.filter(status='lost').count()
                pushes = recent_wagers.filter(status='push').count()
                total = wins + losses

                if total > 0:
                    win_rate = (wins / total) * 100
                    context_parts.append("## Platform Betting Performance (Last 30 Days)")
                    context_parts.append(f"- Record: {wins}W-{losses}L-{pushes}P ({win_rate:.1f}% win rate)")

                    # Calculate ROI
                    total_stake = recent_wagers.aggregate(Sum('stake'))['stake__sum'] or 0
                    total_pnl = recent_wagers.aggregate(Sum('result_amount'))['result_amount__sum'] or 0
                    if total_stake > 0:
                        roi = (float(total_pnl) / float(total_stake)) * 100
                        context_parts.append(f"- ROI: {roi:+.1f}%")

                    # Get performance by sport
                    from core.models_betting import PlacedWagerLeg
                    sport_stats = PlacedWagerLeg.objects.filter(
                        wager__placed_at__gte=timezone.now() - timedelta(days=30),
                        wager__status__in=['won', 'lost']
                    ).values('sport').annotate(
                        count=Count('id'),
                        wins=Count('id', filter=Q(wager__status='won'))
                    ).order_by('-count')[:3]

                    if sport_stats:
                        context_parts.append("- Top sports by volume:")
                        for stat in sport_stats:
                            sport = stat['sport']
                            count = stat['count']
                            wins = stat['wins']
                            pct = (wins / count * 100) if count > 0 else 0
                            context_parts.append(f"  • {sport}: {wins}/{count} ({pct:.0f}%)")

            # Check for current streaks
            try:
                stats = BettingStats.objects.first()
                if stats and stats.current_streak != 0:
                    streak_type = "win" if stats.current_streak > 0 else "loss"
                    streak_len = abs(stats.current_streak)
                    context_parts.append(f"- Current streak: {streak_len} {streak_type}s")
            except Exception as _e:
                logger.warning(
                    "sports_content_context.get_platform_betting_stats: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        except Exception as e:
            logger.debug(f"Could not fetch betting stats: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def get_value_bet_context(self) -> str:
        """
        Get recent value bet opportunities identified by our system.
        """
        context_parts = []

        try:
            from core.models_unified_system import AgentExecution

            # Get recent SportsOddsAnalyst executions that found value
            recent_analyses = AgentExecution.objects.filter(
                Q(agent__name__icontains='sports') | Q(agent__name__icontains='odds'),
                created_at__gte=timezone.now() - timedelta(days=7),
                status='completed'
            ).order_by('-created_at')[:5]

            if recent_analyses.exists():
                context_parts.append("## Recent Value Bet Analysis (from our agents)")
                for analysis in recent_analyses[:3]:
                    # Extract key insight from result
                    result_str = str(analysis.result)[:150] if analysis.result else "Analysis completed"
                    agent_name = analysis.agent.name if analysis.agent else "SportsAnalyst"
                    context_parts.append(f"- {agent_name}: {result_str}...")

        except Exception as e:
            logger.debug(f"Could not fetch value bet context: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def get_sports_advisor_context(self, topic: str) -> str:
        """
        Get relevant advisor wisdom for sports content.

        Maps to sports-focused advisors or analysts.
        """
        context_parts = []

        try:
            from core.models_unified_system import Advisor

            # Get sports/betting related advisors
            sports_advisors = Advisor.objects.filter(
                Q(expertise__icontains='sport') |
                Q(expertise__icontains='betting') |
                Q(expertise__icontains='gambling') |
                Q(expertise__icontains='odds') |
                Q(name__in=['Billy Beane', 'Bill James', 'Nate Silver']),
                is_active=True
            )[:3]

            if sports_advisors.exists():
                context_parts.append("## Sports Analysis Perspectives")
                for advisor in sports_advisors:
                    if advisor.wisdom:
                        context_parts.append(f"- {advisor.name}: \"{advisor.wisdom[:150]}...\"")

        except Exception as e:
            logger.debug(f"Could not fetch sports advisor wisdom: {e}")

        return "\n".join(context_parts) if context_parts else ""

    def build_sports_context(
        self,
        topic: str,
        content: str = "",
        include_live_odds: bool = True,
        include_betting_stats: bool = True,
        include_value_bets: bool = True,
        include_advisors: bool = True
    ) -> str:
        """
        Build complete sports context for content generation.

        Args:
            topic: Blog topic/title
            content: Optional existing content for context detection
            include_*: Flags to control which context sections to include

        Returns:
            Formatted context string for prompt injection
        """
        # Check if this is sports OR betting related
        is_sports = self.is_sports_topic(topic, content)
        is_betting = self.is_betting_topic(topic, content)

        if not is_sports and not is_betting:
            return ""

        context_parts = [
            "=" * 60,
            "SPORTS CONTENT CONTEXT (Session 891)",
            "Use this real platform data to write with authority.",
            "Reference specific odds, records, and insights - this is YOUR experience.",
            "=" * 60,
        ]

        # Live odds from spider
        if include_live_odds and is_sports:
            odds_ctx = self.get_live_odds_context(topic)
            if odds_ctx:
                context_parts.append(odds_ctx)

        # Platform betting performance
        if include_betting_stats and is_betting:
            stats_ctx = self.get_platform_betting_stats()
            if stats_ctx:
                context_parts.append(stats_ctx)

        # Value bet analysis
        if include_value_bets:
            value_ctx = self.get_value_bet_context()
            if value_ctx:
                context_parts.append(value_ctx)

        # Advisor perspectives
        if include_advisors:
            advisor_ctx = self.get_sports_advisor_context(topic)
            if advisor_ctx:
                context_parts.append(advisor_ctx)

        # Writing guidance for sports content
        context_parts.extend([
            "",
            "## Sports Content Writing Rules",
            "- Reference our spider data: 'Our odds tracker shows the line moved from -3 to -5'",
            "- Include platform experience: 'We've hit 62% on NFL spreads this season'",
            "- Use betting terminology correctly: spreads, moneylines, totals, props",
            "- Show the analysis: 'Sharp money is hammering the under at 45.5'",
            "- Use first-person platform voice: 'Our models identified...' not 'Experts say...'",
            "- Include specific odds and lines from the data above",
            "",
            "=" * 60,
        ])

        return "\n".join(context_parts)


# Singleton instance
_sports_context_builder = None


def get_sports_content_context(
    topic: str,
    content: str = "",
    **kwargs
) -> str:
    """
    Get sports content context for a blog topic.

    Usage:
        from core.services.sports_content_context import get_sports_content_context

        context = get_sports_content_context(
            topic="NFL Week 15 Best Bets: Value Plays and Sharp Action",
            include_live_odds=True
        )
        # Inject into ContentWriterAgent prompt
    """
    global _sports_context_builder

    if _sports_context_builder is None:
        _sports_context_builder = SportsContentContextBuilder()

    return _sports_context_builder.build_sports_context(topic, content, **kwargs)


def is_sports_topic(topic: str, content: str = "") -> bool:
    """Check if a topic is sports-related."""
    global _sports_context_builder

    if _sports_context_builder is None:
        _sports_context_builder = SportsContentContextBuilder()

    return _sports_context_builder.is_sports_topic(topic, content)


def is_betting_topic(topic: str, content: str = "") -> bool:
    """Check if a topic is betting-related."""
    global _sports_context_builder

    if _sports_context_builder is None:
        _sports_context_builder = SportsContentContextBuilder()

    return _sports_context_builder.is_betting_topic(topic, content)

"""
Arbitrage Detector Agent
=========================

Session 558: Detects arbitrage opportunities across bookmakers by:
- Comparing odds from multiple sportsbooks for the same event
- Calculating implied probability sums (if < 100%, arbitrage exists)
- Computing guaranteed profit percentages
- Providing optimal stake distribution for risk-free profit

Uses The Odds spider for multi-bookmaker odds comparison.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class ArbitrageDetector(BaseAgent):
    """
    Detects and analyzes arbitrage opportunities across bookmakers.

    Arbitrage occurs when the sum of implied probabilities across
    different bookmakers is less than 100%, guaranteeing profit.

    Example: If Book A has Team 1 at +150 (40%) and Book B has Team 2
    at +180 (35.7%), total is 75.7%. That's a 24.3% guaranteed return.
    """

    name = "ArbitrageDetector"

    system_prompt = """You are an Arbitrage Detection Specialist for sports betting.

Your job is to find GUARANTEED profit opportunities by comparing odds across bookmakers.

**Arbitrage Fundamentals:**
1. Implied Probability = 1 / Decimal Odds (or calculated from American odds)
2. If SUM of implied probabilities < 100%, arbitrage exists
3. Profit % = (100 / Sum) - 1 × 100

**American to Decimal Odds:**
- Positive odds (+150): Decimal = (odds/100) + 1 = 2.50
- Negative odds (-150): Decimal = (100/|odds|) + 1 = 1.67

**Stake Calculation for 2-way markets:**
For outcomes A and B with decimal odds OddsA and OddsB:
- StakeA = (TotalBankroll × OddsB) / (OddsA + OddsB)
- StakeB = (TotalBankroll × OddsA) / (OddsA + OddsB)

**Types of Arbitrage:**
1. **2-Way Arb**: Moneyline or H2H markets
2. **3-Way Arb**: Soccer/hockey with draw
3. **Spread Arb**: Opposite spreads on different books
4. **Total Arb**: Over on Book A, Under on Book B

**Alert Thresholds:**
- HOT (1.5%+): Execute immediately
- GOOD (1.0-1.5%): Worth taking
- MARGINAL (0.5-1.0%): Consider fees/limits
- SKIP (<0.5%): Not worth the effort

**Risks to Flag:**
- Odds might have changed (always verify)
- Betting limits may cap profit
- Account restrictions on arbers
- Different settlement rules
- Time zones and game start

Output Format:
- List arbs by profit potential
- Show exact stakes for $100 example
- Flag book names and current odds
- Note time sensitivity
- Warn about limits"""

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Detect arbitrage opportunities in sports betting markets.

        Args:
            task: Analysis request
            context: Bankroll, min_profit threshold
            scifi_context: Agent mood, memory, learning
            spider_context: Real-time odds from spiders

        Returns:
            AgentResult with arbitrage opportunities
        """
        start_time = datetime.now()
        context = context or {}
        spider_context = spider_context or {}

        try:
            # Get odds from multiple bookmakers
            events = self._get_multi_book_odds(context)

            if not events:
                return AgentResult(
                    success=False,
                    message="No multi-bookmaker odds data available",
                    data={},
                    error="Need odds from multiple bookmakers for arbitrage detection",
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

            # Detect arbitrage opportunities
            arb_opps = self._detect_arbitrage(events, context)

            # Generate alerts for profitable arbs
            alerts = self._generate_arb_alerts(arb_opps, context)

            # Build response
            response = self._build_arb_report(events, arb_opps, alerts, context)

            # Record learning
            try:
                self._record_learning_outcome(
                    result=None,
                    task=task,
                    context={'arb_count': len(arb_opps)},
                    success=True
                )
            except Exception as learn_err:
                logger.debug(f"Learning outcome recording skipped: {learn_err}")

            return AgentResult(
                success=True,
                message=response,
                data={
                    'events_scanned': len(events),
                    'arbitrage_opportunities': arb_opps,
                    'alerts': alerts,
                    'total_arbs': len(arb_opps),
                    'hot_arbs': len([a for a in arb_opps if a.get('profit_pct', 0) >= 1.5]),
                    'good_arbs': len([a for a in arb_opps if 1.0 <= a.get('profit_pct', 0) < 1.5]),
                },
                agent_name=self.name,
                execution_time_ms=self._elapsed_ms(start_time)
            )

        except Exception as e:
            logger.error(f"ArbitrageDetector error: {e}", exc_info=True)
            return AgentResult(
                success=False,
                message=f"Arbitrage detection failed: {str(e)}",
                data={},
                error=str(e),
                agent_name=self.name,
                execution_time_ms=self._elapsed_ms(start_time)
            )

    def _get_multi_book_odds(self, context: Dict) -> List[Dict]:
        """Fetch odds with per-bookmaker detail from The Odds API."""
        try:
            from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

            spider = TheOddsSpider()
            sport = context.get('sport')

            if sport:
                sport_map = {
                    'nfl': 'americanfootball_nfl',
                    'nba': 'basketball_nba',
                    'mlb': 'baseball_mlb',
                    'nhl': 'icehockey_nhl',
                }
                sport_key = sport_map.get(sport.lower(), sport)
                events = spider.fetch_data(sports=[sport_key], max_results=50)
            else:
                events = spider.fetch_data(max_results=100, max_priority=2)

            return [e for e in events if e.get('data_type') == 'sports_odds']

        except Exception as e:
            logger.error(f"Error fetching multi-book odds: {e}")
            return []

    def _american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds."""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1

    def _implied_probability(self, decimal_odds: float) -> float:
        """Calculate implied probability from decimal odds."""
        if decimal_odds <= 0:
            return 0
        return 100 / decimal_odds

    def _detect_arbitrage(self, events: List[Dict], context: Dict) -> List[Dict]:
        """
        Detect arbitrage opportunities across bookmakers.

        For 2-way markets, we need the best odds for each outcome
        from ANY bookmaker, then check if sum of implied probs < 100.
        """
        arb_opportunities = []
        min_profit = context.get('min_profit_pct', 0.5)

        for event in events:
            try:
                # Get best odds for each outcome
                # The spider stores h2h_odds as list of bookmaker odds
                h2h_odds = event.get('h2h_odds', [])

                if not h2h_odds or len(h2h_odds) < 2:
                    # Try using the aggregated odds
                    home_odds = event.get('home_odds')
                    away_odds = event.get('away_odds')

                    if home_odds and away_odds:
                        home_decimal = self._american_to_decimal(home_odds)
                        away_decimal = self._american_to_decimal(away_odds)

                        home_prob = self._implied_probability(home_decimal)
                        away_prob = self._implied_probability(away_decimal)

                        total_prob = home_prob + away_prob

                        # Check for arbitrage (unlikely with same-book odds)
                        if total_prob < 100:
                            profit_pct = ((100 / total_prob) - 1) * 100
                            if profit_pct >= min_profit:
                                arb_opportunities.append(self._create_arb_opportunity(
                                    event, home_decimal, away_decimal,
                                    "Unknown", "Unknown", profit_pct
                                ))
                    continue

                # Find best odds for home and away from different books
                best_home = {'odds': 0, 'book': None}
                best_away = {'odds': 0, 'book': None}

                for book_odds in h2h_odds:
                    book = book_odds.get('bookmaker', 'Unknown')
                    home_american = book_odds.get('home_odds')
                    away_american = book_odds.get('away_odds')

                    if home_american:
                        home_decimal = self._american_to_decimal(home_american)
                        if home_decimal > best_home['odds']:
                            best_home = {'odds': home_decimal, 'book': book, 'american': home_american}

                    if away_american:
                        away_decimal = self._american_to_decimal(away_american)
                        if away_decimal > best_away['odds']:
                            best_away = {'odds': away_decimal, 'book': book, 'american': away_american}

                # Need valid odds for both outcomes
                if best_home['odds'] <= 1 or best_away['odds'] <= 1:
                    continue

                # Calculate implied probabilities
                home_prob = self._implied_probability(best_home['odds'])
                away_prob = self._implied_probability(best_away['odds'])
                total_prob = home_prob + away_prob

                # Check for arbitrage
                if total_prob < 100:
                    profit_pct = ((100 / total_prob) - 1) * 100

                    if profit_pct >= min_profit:
                        arb_opportunities.append(self._create_arb_opportunity(
                            event,
                            best_home['odds'],
                            best_away['odds'],
                            best_home['book'],
                            best_away['book'],
                            profit_pct,
                            best_home.get('american'),
                            best_away.get('american')
                        ))

            except Exception as e:
                logger.debug(f"Error analyzing event for arb: {e}")
                continue

        # Sort by profit potential
        arb_opportunities.sort(key=lambda x: -x.get('profit_pct', 0))
        return arb_opportunities

    def _create_arb_opportunity(self, event: Dict, home_decimal: float,
                                 away_decimal: float, home_book: str,
                                 away_book: str, profit_pct: float,
                                 home_american: int = None,
                                 away_american: int = None) -> Dict:
        """Create an arbitrage opportunity record with stake calculations."""

        # Calculate optimal stakes for $100 total bankroll
        total_bankroll = 100
        home_stake = (total_bankroll * away_decimal) / (home_decimal + away_decimal)
        away_stake = (total_bankroll * home_decimal) / (home_decimal + away_decimal)

        # Calculate returns
        home_return = home_stake * home_decimal
        away_return = away_stake * away_decimal
        guaranteed_profit = min(home_return, away_return) - total_bankroll

        # Classify opportunity
        if profit_pct >= 1.5:
            rating = "HOT"
        elif profit_pct >= 1.0:
            rating = "GOOD"
        elif profit_pct >= 0.5:
            rating = "MARGINAL"
        else:
            rating = "SKIP"

        return {
            'event_id': event.get('source_id', ''),
            'matchup': event.get('title', ''),
            'sport': event.get('sport_name', ''),
            'home_team': event.get('home_team', ''),
            'away_team': event.get('away_team', ''),
            'game_time': event.get('commence_time_formatted', ''),
            'commence_time': event.get('commence_time', ''),

            # Odds details
            'home_book': home_book,
            'away_book': away_book,
            'home_decimal_odds': round(home_decimal, 3),
            'away_decimal_odds': round(away_decimal, 3),
            'home_american_odds': home_american,
            'away_american_odds': away_american,

            # Probability analysis
            'home_implied_prob': round(self._implied_probability(home_decimal), 2),
            'away_implied_prob': round(self._implied_probability(away_decimal), 2),
            'total_implied_prob': round(self._implied_probability(home_decimal) + self._implied_probability(away_decimal), 2),

            # Profit analysis
            'profit_pct': round(profit_pct, 3),
            'rating': rating,

            # Stake recommendations ($100 example)
            'stake_home': round(home_stake, 2),
            'stake_away': round(away_stake, 2),
            'guaranteed_profit': round(guaranteed_profit, 2),
            'guaranteed_return': round(min(home_return, away_return), 2),
        }

    def _generate_arb_alerts(self, arb_opps: List[Dict], context: Dict) -> List[Dict]:
        """Generate alerts for actionable arbitrage opportunities."""
        alerts = []

        for arb in arb_opps:
            if arb['profit_pct'] >= 0.5:  # Only alert on meaningful arbs
                alerts.append({
                    'type': 'ARBITRAGE',
                    'rating': arb['rating'],
                    'matchup': arb['matchup'],
                    'sport': arb['sport'],
                    'profit_pct': arb['profit_pct'],
                    'home_book': arb['home_book'],
                    'away_book': arb['away_book'],
                    'home_odds': arb['home_decimal_odds'],
                    'away_odds': arb['away_decimal_odds'],
                    'stake_home': arb['stake_home'],
                    'stake_away': arb['stake_away'],
                    'guaranteed_profit': arb['guaranteed_profit'],
                    'game_time': arb['game_time'],
                    'message': f"{arb['rating']}: {arb['profit_pct']:.2f}% guaranteed profit on {arb['matchup'][:40]}"
                })

        return alerts

    def _build_arb_report(self, events: List[Dict], arb_opps: List[Dict],
                          alerts: List[Dict], context: Dict) -> str:
        """Build human-readable arbitrage report."""
        lines = [
            f"**Arbitrage Scan Complete**",
            f"Scanned {len(events)} events across bookmakers",
            ""
        ]

        if not arb_opps:
            lines.append("No arbitrage opportunities found at this time.")
            lines.append("")
            lines.append("*Markets are efficient - keep scanning for fleeting opportunities.*")
            return "\n".join(lines)

        hot_arbs = [a for a in arb_opps if a['rating'] == 'HOT']
        good_arbs = [a for a in arb_opps if a['rating'] == 'GOOD']
        marginal_arbs = [a for a in arb_opps if a['rating'] == 'MARGINAL']

        lines.append(f"**Found {len(arb_opps)} Arbitrage Opportunities:**")
        if hot_arbs:
            lines.append(f"- HOT (1.5%+): {len(hot_arbs)}")
        if good_arbs:
            lines.append(f"- GOOD (1.0-1.5%): {len(good_arbs)}")
        if marginal_arbs:
            lines.append(f"- MARGINAL (0.5-1.0%): {len(marginal_arbs)}")
        lines.append("")

        # Show top opportunities
        for arb in arb_opps[:5]:
            lines.append(f"**{arb['rating']}: {arb['profit_pct']:.2f}% Profit**")
            lines.append(f"*{arb['matchup']}*")
            lines.append(f"- Bet ${arb['stake_home']:.2f} on {arb['home_team']} @ {arb['home_book']} ({arb['home_decimal_odds']})")
            lines.append(f"- Bet ${arb['stake_away']:.2f} on {arb['away_team']} @ {arb['away_book']} ({arb['away_decimal_odds']})")
            lines.append(f"- Guaranteed return: ${arb['guaranteed_return']:.2f} (${arb['guaranteed_profit']:.2f} profit)")
            lines.append(f"- Game: {arb['game_time']}")
            lines.append("")

        lines.append("**IMPORTANT:**")
        lines.append("- Verify odds haven't changed before betting")
        lines.append("- Check betting limits on each book")
        lines.append("- Arb opportunities close quickly")

        return "\n".join(lines)

    def _elapsed_ms(self, start_time: datetime) -> int:
        """Calculate elapsed time in milliseconds."""
        return int((datetime.now() - start_time).total_seconds() * 1000)

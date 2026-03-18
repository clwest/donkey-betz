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

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


# =============================================================================
# Session 683: ML Integration for Arbitrage Detection (Anomaly)
# =============================================================================

def detect_arb_anomalies_with_ml(odds_data: dict) -> dict:
    """Detect arbitrage anomalies using ML models."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(data=odds_data, task_hint=TaskType.ANOMALY, max_models=2)
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'anomaly'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'anomalies': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML arbitrage detection failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class ArbitrageDetector(BaseAgent):
    """
    Detects and analyzes arbitrage opportunities across bookmakers.

    Arbitrage occurs when the sum of implied probabilities across
    different bookmakers is less than 100%, guaranteeing profit.

    Example: If Book A has Team 1 at +150 (40%) and Book B has Team 2
    at +180 (35.7%), total is 75.7%. That's a 24.3% guaranteed return.
    """

    name = "ArbitrageDetector"
    create_deliverable_on_schedule = False  # Session 1077: scheduled outputs go to AgentExecution only

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

        # Session 750: Time Travel integration
        with self.time_travel_session("arbitrage_detection", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting arbitrage detection",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip detection", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

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

                # Session 687: Create Human Interface attention items for HOT arbs
                self._create_attention_items(arb_opps)

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

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Arbitrage Detection: {task[:80]}",
                    content=response,
                    deliverable_type='analysis',
                    category='Arbitrage Detection',
                    tags=['arbitrage', 'sports'],
                    metadata={'task': task[:200], 'total_arbs': len(arb_opps), 'events_scanned': len(events)},
                )

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
        if american_odds is None:
            return 0
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

        For 2-way markets (NFL, NBA, etc.), we need odds for 2 outcomes.
        For 3-way markets (soccer), we MUST have odds for all 3 outcomes
        (home, away, draw) otherwise it's not a real arbitrage.
        """
        arb_opportunities = []
        min_profit = context.get('min_profit_pct', 0.5)

        # Sports that have 3-way markets (with draws)
        soccer_sports = ['soccer', 'soccer_epl', 'soccer_spain_la_liga', 'soccer_germany_bundesliga',
                        'soccer_italy_serie_a', 'soccer_france_ligue_one', 'soccer_usa_mls',
                        'soccer_uefa_champs_league', 'soccer_uefa_europa_league']

        for event in events:
            try:
                h2h_odds = event.get('h2h_odds', [])
                sport_key = event.get('sport_key', '')
                category = event.get('category', '')

                # Determine if this is a 3-way market (soccer)
                is_3way = category == 'soccer' or any(s in sport_key for s in ['soccer', 'epl', 'la_liga',
                                                                                'bundesliga', 'serie_a',
                                                                                'ligue_one', 'mls',
                                                                                'champs_league', 'europa'])

                # Need at least 2 bookmakers for arbitrage
                if not h2h_odds or len(h2h_odds) < 2:
                    continue

                if is_3way:
                    # 3-way arbitrage: need best odds for home, away, AND draw
                    arb = self._detect_3way_arbitrage(event, h2h_odds, min_profit)
                    if arb:
                        arb_opportunities.append(arb)
                else:
                    # 2-way arbitrage: home vs away
                    arb = self._detect_2way_arbitrage(event, h2h_odds, min_profit)
                    if arb:
                        arb_opportunities.append(arb)

            except Exception as e:
                logger.debug(f"Error analyzing event for arb: {e}")
                continue

        # Sort by profit potential
        arb_opportunities.sort(key=lambda x: -x.get('profit_pct', 0))
        return arb_opportunities

    def _detect_2way_arbitrage(self, event: Dict, h2h_odds: List[Dict], min_profit: float) -> Optional[Dict]:
        """Detect 2-way arbitrage (NFL, NBA, NHL, MLB, etc.)."""
        best_home = {'odds': 0, 'book': None, 'american': None}
        best_away = {'odds': 0, 'book': None, 'american': None}

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
            return None

        # Calculate implied probabilities
        home_prob = self._implied_probability(best_home['odds'])
        away_prob = self._implied_probability(best_away['odds'])
        total_prob = home_prob + away_prob

        # SANITY CHECK: Real 2-way markets have total implied prob of 100-115%
        # If total is below 85%, the data is clearly wrong (stale odds, mixed markets, etc.)
        # This filters out false positives from bad API data
        if total_prob < 85:
            logger.debug(f"Skipping {event.get('title')} - implausible total prob {total_prob:.1f}%")
            return None

        # Check for arbitrage (must be less than 100%)
        if total_prob < 100:
            profit_pct = ((100 / total_prob) - 1) * 100

            # Additional sanity check: Real arbs are typically 0.5-5%
            # Anything above 10% is almost certainly bad data
            if profit_pct > 10:
                logger.debug(f"Skipping {event.get('title')} - implausible profit {profit_pct:.1f}%")
                return None

            if profit_pct >= min_profit:
                return self._create_arb_opportunity(
                    event,
                    best_home['odds'],
                    best_away['odds'],
                    best_home['book'],
                    best_away['book'],
                    profit_pct,
                    best_home.get('american'),
                    best_away.get('american'),
                    is_3way=False
                )
        return None

    def _detect_3way_arbitrage(self, event: Dict, h2h_odds: List[Dict], min_profit: float) -> Optional[Dict]:
        """Detect 3-way arbitrage (soccer with draw)."""
        best_home = {'odds': 0, 'book': None, 'american': None}
        best_away = {'odds': 0, 'book': None, 'american': None}
        best_draw = {'odds': 0, 'book': None, 'american': None}

        for book_odds in h2h_odds:
            book = book_odds.get('bookmaker', 'Unknown')
            home_american = book_odds.get('home_odds')
            away_american = book_odds.get('away_odds')
            draw_american = book_odds.get('draw_odds')

            if home_american:
                home_decimal = self._american_to_decimal(home_american)
                if home_decimal > best_home['odds']:
                    best_home = {'odds': home_decimal, 'book': book, 'american': home_american}

            if away_american:
                away_decimal = self._american_to_decimal(away_american)
                if away_decimal > best_away['odds']:
                    best_away = {'odds': away_decimal, 'book': book, 'american': away_american}

            if draw_american:
                draw_decimal = self._american_to_decimal(draw_american)
                if draw_decimal > best_draw['odds']:
                    best_draw = {'odds': draw_decimal, 'book': book, 'american': draw_american}

        # 3-way arb REQUIRES all three outcomes
        if best_home['odds'] <= 1 or best_away['odds'] <= 1 or best_draw['odds'] <= 1:
            return None

        # Calculate implied probabilities for ALL 3 outcomes
        home_prob = self._implied_probability(best_home['odds'])
        away_prob = self._implied_probability(best_away['odds'])
        draw_prob = self._implied_probability(best_draw['odds'])
        total_prob = home_prob + away_prob + draw_prob

        # SANITY CHECK: Real 3-way markets have total implied prob of 100-120%
        # If total is below 90%, the data is clearly wrong
        if total_prob < 90:
            logger.debug(f"Skipping 3-way {event.get('title')} - implausible total prob {total_prob:.1f}%")
            return None

        # Check for arbitrage
        if total_prob < 100:
            profit_pct = ((100 / total_prob) - 1) * 100

            # Sanity check: Real arbs are typically 0.5-5%, max 10%
            if profit_pct > 10:
                logger.debug(f"Skipping 3-way {event.get('title')} - implausible profit {profit_pct:.1f}%")
                return None

            if profit_pct >= min_profit:
                return self._create_3way_arb_opportunity(
                    event, best_home, best_away, best_draw, profit_pct
                )
        return None

    def _create_3way_arb_opportunity(self, event: Dict, best_home: Dict,
                                      best_away: Dict, best_draw: Dict,
                                      profit_pct: float) -> Dict:
        """Create a 3-way arbitrage opportunity record with stake calculations."""
        # Calculate optimal stakes for $100 total bankroll
        total_bankroll = 100
        home_decimal = best_home['odds']
        away_decimal = best_away['odds']
        draw_decimal = best_draw['odds']

        # Calculate stakes to guarantee equal returns from any outcome
        total_inverse = (1/home_decimal) + (1/away_decimal) + (1/draw_decimal)
        home_stake = total_bankroll / (home_decimal * total_inverse)
        away_stake = total_bankroll / (away_decimal * total_inverse)
        draw_stake = total_bankroll / (draw_decimal * total_inverse)

        # Guaranteed return (same regardless of outcome)
        guaranteed_return = home_stake * home_decimal
        guaranteed_profit = guaranteed_return - total_bankroll

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
            'is_3way': True,

            # Home bet
            'home_book': best_home['book'],
            'home_decimal_odds': round(home_decimal, 3),
            'home_american_odds': best_home['american'],
            'stake_home': round(home_stake, 2),

            # Away bet
            'away_book': best_away['book'],
            'away_decimal_odds': round(away_decimal, 3),
            'away_american_odds': best_away['american'],
            'stake_away': round(away_stake, 2),

            # Draw bet
            'draw_book': best_draw['book'],
            'draw_decimal_odds': round(draw_decimal, 3),
            'draw_american_odds': best_draw['american'],
            'stake_draw': round(draw_stake, 2),

            # Probability analysis
            'home_implied_prob': round(self._implied_probability(home_decimal), 2),
            'away_implied_prob': round(self._implied_probability(away_decimal), 2),
            'draw_implied_prob': round(self._implied_probability(draw_decimal), 2),
            'total_implied_prob': round(
                self._implied_probability(home_decimal) +
                self._implied_probability(away_decimal) +
                self._implied_probability(draw_decimal), 2
            ),

            # Profit analysis
            'profit_pct': round(profit_pct, 3),
            'rating': rating,
            'guaranteed_profit': round(guaranteed_profit, 2),
            'guaranteed_return': round(guaranteed_return, 2),
        }

    def _create_arb_opportunity(self, event: Dict, home_decimal: float,
                                 away_decimal: float, home_book: str,
                                 away_book: str, profit_pct: float,
                                 home_american: int = None,
                                 away_american: int = None,
                                 is_3way: bool = False) -> Dict:
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
            'is_3way': is_3way,

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

    def _create_attention_items(self, arb_opps: List[Dict]) -> None:
        """Session 687: Create Human Interface attention items for actionable arbs."""
        try:
            from core.services.human_attention_bridge import attention_bridge
            from dateutil.parser import parse as parse_datetime

            # Only create attention for HOT and GOOD arbs
            for arb in arb_opps:
                if arb.get('rating') not in ['HOT', 'GOOD']:
                    continue

                # Parse game time as expiry
                expires_at = None
                if arb.get('commence_time'):
                    try:
                        expires_at = parse_datetime(arb['commence_time'])
                    except Exception:
                        pass

                attention_bridge.create_arbitrage_attention(
                    opportunity={
                        'id': arb.get('event_id', ''),
                        'title': arb.get('matchup', 'Arbitrage Opportunity'),
                        'profit_pct': arb.get('profit_pct', 0),
                        'markets': [arb.get('home_book', ''), arb.get('away_book', '')],
                        'sport': arb.get('sport', ''),
                        'rating': arb.get('rating', ''),
                        'stake_home': arb.get('stake_home', 0),
                        'stake_away': arb.get('stake_away', 0),
                        'guaranteed_profit': arb.get('guaranteed_profit', 0),
                        'home_team': arb.get('home_team', ''),
                        'away_team': arb.get('away_team', ''),
                        'game_time': arb.get('game_time', ''),
                        'expires_at': expires_at,
                    }
                )
                logger.info(f"Created attention item for {arb.get('rating')} arb: {arb.get('matchup')}")

        except Exception as e:
            logger.warning(f"Failed to create attention items for arbs: {e}")

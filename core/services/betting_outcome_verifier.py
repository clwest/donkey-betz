"""
Session 995: Betting Outcome Verification Service

Closes the feedback loop for sports betting:
1. Finds pending PlacedWagerLeg records where games should be finished
2. Finds HumanAttentionItem records in 'watching' status (arb verification)
3. Fetches completed scores from The Odds API
4. Settles wagers and verifies arb items
5. Creates learning records via SportsBettingLearningBridge
"""

import logging
import re
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


class BettingOutcomeVerifier:
    """
    Verifies betting outcomes by fetching game scores and settling
    pending wagers and watched arbitrage items.
    """

    # Hours after commence_time before we try to verify
    MIN_HOURS_AFTER_START = 3

    def verify_all_pending(self):
        """
        Main entry point. Find pending wagers and watching arb items,
        fetch scores, settle everything, create learning records.

        Returns:
            dict with summary of actions taken
        """
        from core.models_betting import PlacedWager, PlacedWagerLeg
        from core.models_human_interface import HumanAttentionItem

        summary = {
            'wagers_settled': 0,
            'wagers_skipped': 0,
            'arb_items_verified': 0,
            'arb_items_skipped': 0,
            'legs_settled': 0,
            'learning_records': 0,
            'errors': [],
        }

        cutoff = timezone.now() - timedelta(hours=self.MIN_HOURS_AFTER_START)

        # 1. Find pending wager legs where game should be finished
        pending_legs = PlacedWagerLeg.objects.filter(
            status='pending',
            commence_time__lt=cutoff,
        ).select_related('wager')

        # 2. Find watching arb items
        watching_items = HumanAttentionItem.objects.filter(
            status=HumanAttentionItem.STATUS_WATCHING,
            item_type='arbitrage',
        )

        if not pending_legs.exists() and not watching_items.exists():
            logger.info("[OUTCOME-VERIFY] No pending wagers or watching items to verify")
            return summary

        # 3. Collect unique (sport, event_id) pairs
        sport_event_pairs = set()
        for leg in pending_legs:
            sport_event_pairs.add((leg.sport, leg.event_id))

        for item in watching_items:
            payload = item.payload or {}
            sport = payload.get('sport_key') or payload.get('sport', '')
            event_id = payload.get('event_id', '')
            if sport and event_id:
                sport_event_pairs.add((sport, event_id))

        # 4. Batch-fetch scores per sport
        score_lookup = self._fetch_all_scores(sport_event_pairs)

        logger.info(
            f"[OUTCOME-VERIFY] Found {pending_legs.count()} pending legs, "
            f"{watching_items.count()} watching items, "
            f"{len(score_lookup)} completed scores"
        )

        # 5. Settle wagers
        settled_wagers = []
        # Group legs by wager
        wager_ids = pending_legs.values_list('wager_id', flat=True).distinct()
        wagers = PlacedWager.objects.filter(
            id__in=wager_ids,
            status='pending',
        ).prefetch_related('legs')

        for wager in wagers:
            try:
                settled = self._settle_wager(wager, score_lookup)
                if settled:
                    settled_wagers.append(wager)
                    summary['wagers_settled'] += 1
                    summary['legs_settled'] += wager.legs.exclude(status='pending').count()
                else:
                    summary['wagers_skipped'] += 1
            except Exception as e:
                logger.error(f"[OUTCOME-VERIFY] Error settling wager {wager.id}: {e}")
                summary['errors'].append(f"wager {wager.id}: {str(e)}")

        # 6. Verify arb items
        verified_items = []
        for item in watching_items:
            try:
                verified = self._verify_arb_item(item, score_lookup)
                if verified:
                    verified_items.append(item)
                    summary['arb_items_verified'] += 1
                else:
                    summary['arb_items_skipped'] += 1
            except Exception as e:
                logger.error(f"[OUTCOME-VERIFY] Error verifying arb item {item.id}: {e}")
                summary['errors'].append(f"arb_item {item.id}: {str(e)}")

        # 7. Create learning records
        learning_count = self._create_learning_records(settled_wagers, verified_items)
        summary['learning_records'] = learning_count

        logger.info(
            f"[OUTCOME-VERIFY] Complete: {summary['wagers_settled']} wagers settled, "
            f"{summary['arb_items_verified']} arb items verified, "
            f"{summary['learning_records']} learning records created"
        )

        return summary

    def _fetch_all_scores(self, sport_event_pairs):
        """
        Batch-fetch scores from The Odds API for all unique sports.

        Args:
            sport_event_pairs: set of (sport_key, event_id) tuples

        Returns:
            dict mapping event_id -> score data
        """
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

        # Group by sport
        sports = set()
        for sport, _ in sport_event_pairs:
            if sport and 'winner' not in sport and 'championship' not in sport:
                sports.add(sport)

        spider = TheOddsSpider()
        score_lookup = {}

        for sport_key in sports:
            try:
                scores = spider.fetch_scores(sport_key, days_from=3)
                for score_data in scores:
                    score_lookup[score_data['event_id']] = score_data
            except Exception as e:
                logger.error(f"[OUTCOME-VERIFY] Error fetching scores for {sport_key}: {e}")

        return score_lookup

    def _settle_wager(self, wager, score_lookup):
        """
        Settle a wager based on score data.

        Returns True if settled, False if skipped (missing scores).
        """
        legs = list(wager.legs.all())

        # Check if all legs have scores available
        for leg in legs:
            if leg.status != 'pending':
                continue
            if leg.event_id not in score_lookup:
                # Missing score for at least one leg — skip entire wager, retry next run
                return False

        # Determine outcome for each pending leg
        leg_outcomes = []
        for leg in legs:
            if leg.status != 'pending':
                # Already settled leg — use existing status
                leg_outcomes.append(leg.status)
                continue

            score_data = score_lookup[leg.event_id]
            outcome = self._determine_leg_outcome(leg, score_data)

            # Update leg
            leg.status = outcome
            leg.final_score = f"{score_data['home_score']}-{score_data['away_score']}"
            leg.save(update_fields=['status', 'final_score'])

            leg_outcomes.append(outcome)

        # Determine wager outcome
        if wager.wager_type == 'parlay':
            # Parlay: all legs must win. Any loss = lost. All push = push.
            if 'lost' in leg_outcomes:
                wager.settle(won=False)
            elif all(o == 'push' for o in leg_outcomes):
                wager.settle(won=False, push=True)
            elif all(o in ('won', 'push') for o in leg_outcomes):
                # Won with some pushes — treat as won (push legs reduce payout but wager wins)
                wager.settle(won=True)
            else:
                wager.settle(won=False)
        else:
            # Single bet: outcome = leg outcome
            outcome = leg_outcomes[0] if leg_outcomes else 'lost'
            if outcome == 'won':
                wager.settle(won=True)
            elif outcome == 'push':
                wager.settle(won=False, push=True)
            else:
                wager.settle(won=False)

        logger.info(f"[OUTCOME-VERIFY] Settled wager {wager.id}: {wager.status}")
        return True

    def _determine_leg_outcome(self, leg, score_data):
        """
        Determine if a leg won, lost, or pushed based on score data.

        Args:
            leg: PlacedWagerLeg instance
            score_data: dict with home_team, away_team, home_score, away_score

        Returns:
            'won', 'lost', or 'push'
        """
        home_score = score_data['home_score']
        away_score = score_data['away_score']
        home_team = score_data['home_team']
        away_team = score_data['away_team']

        market = leg.market_type
        pick = leg.pick or ''
        line = float(leg.line) if leg.line is not None else None

        if market == 'h2h':
            return self._evaluate_h2h(pick, home_team, away_team, home_score, away_score)
        elif market == 'spreads':
            return self._evaluate_spread(pick, home_team, away_team, home_score, away_score, line)
        elif market == 'totals':
            return self._evaluate_total(pick, home_score, away_score, line)
        else:
            # Unsupported market type (props, futures) — can't auto-verify
            logger.warning(f"[OUTCOME-VERIFY] Unsupported market type: {market} for leg {leg.id}")
            return 'pending'

    def _evaluate_h2h(self, pick, home_team, away_team, home_score, away_score):
        """Evaluate moneyline bet."""
        picked_home = self._teams_match(pick, home_team)
        picked_away = self._teams_match(pick, away_team)

        if not picked_home and not picked_away:
            # Check if pick contains 'Draw' for soccer
            if 'draw' in pick.lower():
                return 'won' if home_score == away_score else 'lost'
            logger.warning(f"[OUTCOME-VERIFY] Could not match pick '{pick}' to {home_team}/{away_team}")
            return 'lost'

        if picked_home:
            if home_score > away_score:
                return 'won'
            elif home_score == away_score:
                return 'push'
            else:
                return 'lost'
        else:
            if away_score > home_score:
                return 'won'
            elif home_score == away_score:
                return 'push'
            else:
                return 'lost'

    def _evaluate_spread(self, pick, home_team, away_team, home_score, away_score, line):
        """Evaluate spread bet."""
        if line is None:
            # Try to parse line from pick (e.g., "Lakers -5.5")
            line = self._parse_line_from_pick(pick)
            if line is None:
                return 'lost'

        picked_home = self._teams_match(pick, home_team)

        if picked_home:
            adjusted = home_score + line
        else:
            adjusted = away_score + line

        opponent_score = away_score if picked_home else home_score

        if adjusted > opponent_score:
            return 'won'
        elif adjusted == opponent_score:
            return 'push'
        else:
            return 'lost'

    def _evaluate_total(self, pick, home_score, away_score, line):
        """Evaluate totals (over/under) bet."""
        if line is None:
            line = self._parse_line_from_pick(pick)
            if line is None:
                return 'lost'

        total = home_score + away_score
        is_over = 'over' in pick.lower()

        if is_over:
            if total > line:
                return 'won'
            elif total == line:
                return 'push'
            else:
                return 'lost'
        else:
            if total < line:
                return 'won'
            elif total == line:
                return 'push'
            else:
                return 'lost'

    def _parse_line_from_pick(self, pick):
        """
        Parse a numeric line from a pick string.
        e.g., "Lakers -5.5" -> -5.5, "Over 220.5" -> 220.5
        """
        match = re.search(r'([+-]?\d+\.?\d*)\s*$', pick.strip())
        if match:
            return float(match.group(1))
        return None

    def _teams_match(self, pick, team_name):
        """
        Check if a pick string references a team.
        Uses substring matching — The Odds API uses consistent team names.
        """
        if not pick or not team_name:
            return False

        pick_lower = pick.lower().strip()
        team_lower = team_name.lower().strip()

        # Direct contains
        if team_lower in pick_lower or pick_lower.startswith(team_lower):
            return True

        # Strip trailing numbers/signs from pick for team matching
        # e.g., "Lakers -5.5" -> "lakers"
        pick_team = re.sub(r'\s*[+-]?\d+\.?\d*\s*$', '', pick_lower).strip()
        if pick_team and (pick_team in team_lower or team_lower in pick_team):
            return True

        # Word overlap (at least the last word — usually the identifier)
        pick_words = pick_team.split()
        team_words = team_lower.split()
        if pick_words and team_words:
            # Check if last word of pick matches last word of team (e.g., "Lakers" matches "Los Angeles Lakers")
            if pick_words[-1] == team_words[-1]:
                return True

        return False

    def _verify_arb_item(self, item, score_lookup):
        """
        Verify a watched arbitrage HumanAttentionItem.

        Returns True if verified, False if skipped.
        """
        payload = item.payload or {}
        event_id = payload.get('event_id', '')

        if not event_id or event_id not in score_lookup:
            return False

        score_data = score_lookup[event_id]
        home_score = score_data['home_score']
        away_score = score_data['away_score']

        # Determine which side of the arb won
        home_team = score_data['home_team']
        away_team = score_data['away_team']

        if home_score > away_score:
            winning_side = 'home'
        elif away_score > home_score:
            winning_side = 'away'
        else:
            winning_side = 'draw'

        # Calculate actual profit from arb data
        # Arb payload should contain stakes and odds for each side
        profit = self._calculate_arb_profit(payload, winning_side)
        outcome = 'won' if profit > 0 else ('push' if profit == 0 else 'lost')

        notes = (
            f"Final score: {home_team} {home_score} - {away_team} {away_score}. "
            f"Winner: {winning_side}. Calculated profit: ${profit:.2f}"
        )

        item.record_verification(outcome=outcome, profit=profit, notes=notes)
        logger.info(f"[OUTCOME-VERIFY] Verified arb item {item.id}: {outcome} (${profit:.2f})")
        return True

    def _calculate_arb_profit(self, payload, winning_side):
        """
        Calculate actual profit from an arbitrage opportunity.

        Arb payloads typically contain:
        - total_stake or stakes per side
        - odds per bookmaker/side
        - profit_pct (predicted)
        """
        total_stake = payload.get('total_stake', 0)
        if not total_stake:
            # Try to infer from individual stakes
            home_stake = payload.get('home_stake', 0)
            away_stake = payload.get('away_stake', 0)
            total_stake = home_stake + away_stake

        if not total_stake:
            # Can't calculate without stake info
            return 0.0

        # Get the winning side's decimal odds and stake
        if winning_side == 'home':
            odds = payload.get('home_odds_decimal') or payload.get('home_decimal_odds', 0)
            stake = payload.get('home_stake', total_stake / 2)
        elif winning_side == 'away':
            odds = payload.get('away_odds_decimal') or payload.get('away_decimal_odds', 0)
            stake = payload.get('away_stake', total_stake / 2)
        else:
            # Draw — arb on h2h markets typically doesn't cover draws
            return -total_stake

        if not odds:
            return 0.0

        payout = stake * odds
        profit = payout - total_stake
        return round(profit, 2)

    def _create_learning_records(self, settled_wagers, verified_items):
        """
        Create learning records for settled wagers and verified arb items.

        Returns count of learning records created.
        """
        from core.learning_bridges.sports_betting_bridge import SportsBettingLearningBridge

        bridge = SportsBettingLearningBridge()
        count = 0

        for wager in settled_wagers:
            try:
                bridge.record_wager_outcome(wager)
                count += 1
            except Exception as e:
                logger.error(f"[OUTCOME-VERIFY] Error creating learning record for wager {wager.id}: {e}")

        for item in verified_items:
            try:
                bridge.record_arbitrage_outcome(item)
                count += 1
            except Exception as e:
                logger.error(f"[OUTCOME-VERIFY] Error creating learning record for arb item {item.id}: {e}")

        return count

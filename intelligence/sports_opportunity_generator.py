"""
import logging
logger = logging.getLogger(__name__)

🎲 SPORTS BETTING OPPORTUNITY GENERATOR
Converts sports betting recommendations into unified income opportunities
"""

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from sports.models import Game, BettingRecommendation, OddsLine
from sports.bankroll_management import BankrollManagement
from intelligence.models import OpportunityTracking, OpportunityType, OpportunityStatus


class SportsBettingOpportunityGenerator:
    """Convert sports betting recommendations into income opportunities"""

    def discover_betting_opportunities(self, user, hours_ahead=24, min_ev=0.03):
        """
        Find profitable betting opportunities for next N hours

        Args:
            user: User to generate opportunities for
            hours_ahead: Hours ahead to look for games (default 24)
            min_ev: Minimum expected value (default 3%)

        Returns:
            List of OpportunityTracking objects with opportunity_type='sports_bet'
        """
        # Get upcoming games
        now = timezone.now()
        cutoff = now + timedelta(hours=hours_ahead)

        upcoming_games = Game.objects.filter(
            game_time__lte=cutoff,
            game_time__gte=now,
            status='scheduled'
        ).select_related('home_team', 'away_team', 'league')

        opportunities = []

        for game in upcoming_games:
            # Get betting recommendations with positive expected value
            recommendations = BettingRecommendation.objects.filter(
                game=game,
                expected_value__gte=min_ev,  # At least 3% edge
                is_active=True
            ).order_by('-expected_value')[:3]  # Top 3 recommendations per game

            for rec in recommendations:
                try:
                    # Get latest odds
                    odds_line = OddsLine.objects.filter(
                        game=game,
                        bet_type=rec.bet_type
                    ).order_by('-timestamp').first()

                    if not odds_line:
                        continue

                    # Calculate Kelly Criterion bet size
                    try:
                        bankroll = BankrollManagement.get_for_user(user)
                        kelly_fraction = self.calculate_kelly(
                            prob=rec.predicted_probability,
                            odds=float(odds_line.odds_decimal)
                        )
                        suggested_bet = float(bankroll.current_balance) * kelly_fraction * 0.5  # Half Kelly
                    except Exception:
                        # Fallback if bankroll doesn't exist
                        suggested_bet = 25.00  # Default $25 bet

                    # Calculate potential profit
                    potential_profit = suggested_bet * (float(odds_line.odds_decimal) - 1)

                    # Calculate user match score based on sport/team preferences
                    match_score = self.calculate_user_match(user, game)

                    # Create opportunity
                    opportunity = OpportunityTracking.objects.create(
                        user=user,
                        opportunity_type=OpportunityType.SPORTS_BET,
                        opportunity_id=f"bet_{rec.id}",
                        title=f"{game.away_team.name} @ {game.home_team.name} - {rec.bet_type}",
                        description=f"{rec.recommendation_text} (EV: {rec.expected_value*100:.1f}%)",
                        potential_revenue=Decimal(str(potential_profit)),
                        confidence_score=rec.confidence_level,
                        match_score=match_score,
                        opportunity_data={
                            'game_id': str(game.id),
                            'game_time': game.game_time.isoformat(),
                            'sport': game.sport,
                            'league': game.league.name if game.league else None,
                            'home_team': game.home_team.name,
                            'away_team': game.away_team.name,
                            'bet_type': rec.bet_type,
                            'odds_decimal': float(odds_line.odds_decimal),
                            'odds_american': odds_line.odds_american,
                            'suggested_bet_amount': float(suggested_bet),
                            'expected_value': float(rec.expected_value),
                            'kelly_fraction': float(kelly_fraction) if 'kelly_fraction' in locals() else 0,
                            'recommendation_id': str(rec.id),
                        },
                        status=OpportunityStatus.DISCOVERED,
                        spider_source='sports_betting_analyzer',
                        expires_at=game.game_time,  # Bet expires at game time!
                        discovered_at=now
                    )

                    opportunities.append(opportunity)

                except Exception as e:
                    print(f"Error creating sports betting opportunity: {e}")
                    continue

        return opportunities

    def calculate_kelly(self, prob, odds):
        """
        Calculate Kelly Criterion bet size

        Formula: (p * odds - 1) / (odds - 1)
        where p is probability of winning
        """
        if odds <= 1:
            return 0

        kelly = (prob * odds - 1) / (odds - 1)

        # Cap at 25% of bankroll for safety
        return max(0, min(kelly, 0.25))

    def calculate_user_match(self, user, game):
        """
        Calculate how well this opportunity matches user preferences

        Returns score 0.0 - 1.0
        """
        score = 0.5  # Base score

        try:
            from core.models import UserProfile
            profile = UserProfile.objects.get(user=user)

            # Check if user has expressed interest in this sport
            if hasattr(profile, 'preferred_sports'):
                if game.sport in profile.preferred_sports:
                    score += 0.3

            # Check if user follows these teams
            if hasattr(profile, 'followed_teams'):
                if game.home_team.id in profile.followed_teams or game.away_team.id in profile.followed_teams:
                    score += 0.2

        except Exception as _e:
            logger.warning(
                "sports_opportunity_generator.calculate_user_match: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        return min(score, 1.0)

    def mark_bet_placed(self, opportunity_id, bet_amount, bet_details=None):
        """
        Mark that a bet was placed for this opportunity

        Args:
            opportunity_id: OpportunityTracking ID
            bet_amount: Amount actually bet
            bet_details: Additional details (sportsbook, etc.)
        """
        try:
            opportunity = OpportunityTracking.objects.get(id=opportunity_id)
            opportunity.status = OpportunityStatus.ACTION_TAKEN
            opportunity.action_taken_at = timezone.now()

            # Update opportunity data with bet details
            opportunity.opportunity_data['bet_placed'] = True
            opportunity.opportunity_data['actual_bet_amount'] = float(bet_amount)
            if bet_details:
                opportunity.opportunity_data.update(bet_details)

            opportunity.save()

            return True
        except OpportunityTracking.DoesNotExist:
            return False

    def record_bet_outcome(self, opportunity_id, won, payout_amount=None):
        """
        Record the outcome of a bet

        Args:
            opportunity_id: OpportunityTracking ID
            won: Boolean - did the bet win?
            payout_amount: Actual payout received (if won)
        """
        try:
            opportunity = OpportunityTracking.objects.get(id=opportunity_id)

            if won:
                opportunity.status = OpportunityStatus.COMPLETED
                opportunity.success_outcome = True
                if payout_amount:
                    opportunity.actual_revenue = Decimal(str(payout_amount))
                    opportunity.revenue_date = timezone.now()

                    # Create revenue record
                    from intelligence.models import UnifiedRevenueTracking, RevenueStream
                    UnifiedRevenueTracking.objects.create(
                        user=opportunity.user,
                        revenue_stream=RevenueStream.SPORTS_BETTING,
                        source_opportunity=opportunity,
                        amount=Decimal(str(payout_amount)),
                        revenue_date=timezone.now(),
                        description=f"Sports bet win: {opportunity.title}",
                        revenue_data=opportunity.opportunity_data,
                        verified=True,
                        verification_method='sportsbook_api'
                    )
            else:
                opportunity.status = OpportunityStatus.COMPLETED
                opportunity.success_outcome = False
                opportunity.actual_revenue = Decimal('0')
                opportunity.revenue_date = timezone.now()

            opportunity.learning_insights = {
                'outcome': 'won' if won else 'lost',
                'recorded_at': timezone.now().isoformat()
            }
            opportunity.save()

            return True
        except OpportunityTracking.DoesNotExist:
            return False

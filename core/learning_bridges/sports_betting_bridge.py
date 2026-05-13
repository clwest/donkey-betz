"""
Sports Betting Learning Bridge

Connects the sports betting learning system to the core unified learning pipeline.
Syncs performance data, insights, and feedback between isolated sports system and core learning.

Session 1115 batch-13: refactored to inherit from `LearningBridge` ABC.
Unlike the other bridges, this one is invocation-driven (not signal-driven)
— it's called by `sync_user_betting_to_learning(user)` and similar
sync-utility convenience functions, plus by the learning orchestrator
in `core.self_development.learning_orchestrator`. The `event_data`
passed to `process_event` is the User object whose betting performance
should be synced. The original `sync_betting_performance_to_learning`
remains as a back-compat method so all existing callers keep working.
"""

import logging
from typing import Any, Dict, List

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg

from core.learning_bridges.base import LearningBridge

logger = logging.getLogger(__name__)


class SportsBettingLearningBridge(LearningBridge):
    """
    Bridge between sports betting system and core unified learning system.

    Responsibilities:
    - Sync BankrollManagement metrics → UserAgentLearning
    - Sync AgentPerformanceMetrics → UserAgentLearning
    - Generate cross-domain insights from sports betting patterns
    - Feed sports prediction results into learning loop

    ABC contract mapping:
      - `process_event(user)` triggers a full sync for the given user.
      - `_extract_patterns(user)` returns the sync targets (bankroll +
        agent metrics) without doing any DB writes yet.
      - `_update_learning(patterns)` performs the actual sync writes
        via the existing `sync_betting_performance_to_learning` method
        (which mutates UserAgentLearning rows).
      - `_generate_insights(patterns)` returns short summary strings.
    """

    def __init__(self, user=None):
        super().__init__(bridge_name='sports_betting')
        self.user = user

    # ------------------------------------------------------------------
    # ABC contract — `event_data` is the User to sync
    # ------------------------------------------------------------------
    def process_event(self, event_data: Any) -> Dict:
        """Run a betting-performance sync for the given user."""
        user = event_data or self.user
        if not user:
            return {'status': 'skipped', 'reason': 'no_user'}

        self.log_event(f"Syncing betting performance for user={user.id}")
        try:
            result = self.sync_betting_performance_to_learning(user=user)
            if result.get('success'):
                self.log_success(
                    f"Betting performance synced for user={user.id}"
                )
            else:
                self.log_error(
                    f"Betting performance sync failed: {result.get('error')}"
                )
            return result
        except Exception as e:
            self.log_error(f"Error in betting performance sync: {e}")
            return {'status': 'error', 'error': str(e)}

    def _extract_patterns(self, event_data: Any) -> Dict:
        """No separate extraction step — the bridge reads bankroll + agent
        metrics inline during the sync. Return the user as a thin pattern
        so `_update_learning` can still be called independently."""
        user = event_data or self.user
        return {'_user': user}

    def _update_learning(self, patterns: Dict) -> None:
        """Perform the sync. Delegates to the existing implementation."""
        user = patterns.get('_user') or self.user
        if user:
            self.sync_betting_performance_to_learning(user=user)

    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Bridge doesn't produce per-event insights — sync is idempotent."""
        user = patterns.get('_user') or self.user
        return [f"betting performance synced (user={user.id})"] if user else []

    def sync_betting_performance_to_learning(self, user=None):
        """
        Sync BankrollManagement metrics → UserAgentLearning

        Creates/updates UserAgentLearning entries for:
        - Overall betting risk management
        - Sport-specific performance (NFL, NBA, MLB, NHL)

        Args:
            user: User object (optional, uses self.user if not provided)

        Returns:
            Dict with sync results
        """
        from core.models_unified_system import UserAgentLearning
        from sports.models import BankrollManagement, UserBet
        from django.contrib.auth import get_user_model

        User = get_user_model()
        target_user = user or self.user

        if not target_user:
            logger.error("No user provided for betting performance sync")
            return {'success': False, 'error': 'No user provided'}

        try:
            bankroll = BankrollManagement.objects.get(user=target_user)
        except BankrollManagement.DoesNotExist:
            logger.info(f"No bankroll found for user {target_user.id}")
            return {'success': False, 'error': 'No bankroll data'}

        results = {'success': True, 'synced': []}

        # Sync overall betting risk management
        overall_learning, created = UserAgentLearning.objects.update_or_create(
            user=target_user,
            agent_name='SportsBettingSystem',
            learning_domain='betting_risk_management',
            defaults={
                'learning_content': {
                    'win_rate': float(bankroll.win_rate) if bankroll.win_rate else 0.0,
                    'roi_percentage': float(bankroll.roi_percentage) if bankroll.roi_percentage else 0.0,
                    'risk_tolerance': bankroll.risk_tolerance,
                    'kelly_multiplier': float(bankroll.kelly_multiplier),
                    'total_wagered': float(bankroll.total_wagered),
                    'current_balance': float(bankroll.current_balance),
                    'volatility': float(bankroll.volatility_score) if bankroll.volatility_score else 0.0,
                    'max_bet_percentage': float(bankroll.max_bet_percentage),
                    'synced_at': timezone.now().isoformat()
                },
                'confidence_score': (bankroll.win_rate / 100.0) if bankroll.win_rate else 0.5,
                'validation_count': int(bankroll.total_wagered) if bankroll.total_wagered else 0,
                'success_rate': (bankroll.win_rate / 100.0) if bankroll.win_rate else 0.0
            }
        )

        results['synced'].append({
            'domain': 'betting_risk_management',
            'created': created,
            'confidence': float(overall_learning.confidence_score)
        })

        # Sync sport-specific performance
        sport_types = ['nfl', 'nba', 'mlb', 'nhl']

        for sport in sport_types:
            sport_bets = UserBet.objects.filter(
                user=target_user,
                prediction__sport_type=sport
            )

            if sport_bets.exists():
                total_bets = sport_bets.count()
                won_bets = sport_bets.filter(profit_loss__gt=0).count()
                win_rate = (won_bets / total_bets * 100) if total_bets > 0 else 0

                avg_profit = sport_bets.aggregate(
                    avg_profit=Avg('profit_loss')
                )['avg_profit'] or Decimal('0')

                sport_learning, created = UserAgentLearning.objects.update_or_create(
                    user=target_user,
                    agent_name='SportsBettingSystem',
                    learning_domain=f'sports_betting_{sport}',
                    defaults={
                        'learning_content': {
                            'sport': sport,
                            'total_bets': total_bets,
                            'won_bets': won_bets,
                            'win_rate': win_rate,
                            'avg_profit': float(avg_profit),
                            'specialization_level': self._calculate_specialization(win_rate, total_bets),
                            'synced_at': timezone.now().isoformat()
                        },
                        'confidence_score': win_rate / 100.0,
                        'validation_count': total_bets,
                        'success_rate': win_rate / 100.0
                    }
                )

                results['synced'].append({
                    'domain': f'sports_betting_{sport}',
                    'created': created,
                    'win_rate': win_rate,
                    'total_bets': total_bets
                })

        logger.info(f"Synced {len(results['synced'])} learning entries for user {target_user.id}")
        return results

    def sync_agent_sports_performance(self, agent):
        """
        Sync AgentPerformanceMetrics → UserAgentLearning for specific agent

        Args:
            agent: UnifiedAgentTemplate instance

        Returns:
            Dict with sync results
        """
        from core.models_unified_system import UserAgentLearning
        from intelligence.models import AgentPerformanceMetrics

        try:
            metrics = AgentPerformanceMetrics.objects.get(agent=agent)
        except AgentPerformanceMetrics.DoesNotExist:
            logger.info(f"No performance metrics for agent {agent.name}")
            return {'success': False, 'error': 'No metrics data'}

        results = {'success': True, 'synced': []}
        sport_types = ['nfl', 'nba', 'mlb', 'nhl']

        for sport in sport_types:
            sport_predictions = getattr(metrics, f'{sport}_predictions', 0)

            if sport_predictions > 0:
                sport_correct = getattr(metrics, f'{sport}_correct', 0)
                sport_accuracy = (sport_correct / sport_predictions * 100) if sport_predictions > 0 else 0

                # Get users who have worked with this agent
                from sports.models import MLPrediction
                users_worked = MLPrediction.objects.filter(
                    agent=agent,
                    sport_type=sport
                ).values_list('user_id', flat=True).distinct()

                # Create learning entries for each user
                for user_id in users_worked:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()

                    try:
                        user = User.objects.get(id=user_id)

                        learning, created = UserAgentLearning.objects.update_or_create(
                            user=user,
                            agent_name=agent.name,
                            learning_domain=f'sports_betting_{sport}',
                            defaults={
                                'learning_content': {
                                    'sport': sport,
                                    'predictions_made': sport_predictions,
                                    'correct_predictions': sport_correct,
                                    'accuracy': sport_accuracy,
                                    'confidence_calibration': float(metrics.confidence_calibration_score or 0),
                                    'agent_specialization': self._calculate_specialization(sport_accuracy, sport_predictions),
                                    'synced_at': timezone.now().isoformat()
                                },
                                'confidence_score': sport_accuracy / 100.0,
                                'validation_count': sport_predictions,
                                'success_rate': sport_accuracy / 100.0
                            }
                        )

                        results['synced'].append({
                            'user_id': user_id,
                            'agent': agent.name,
                            'sport': sport,
                            'created': created
                        })

                    except User.DoesNotExist:
                        continue

        logger.info(f"Synced {len(results['synced'])} agent learning entries for {agent.name}")
        return results

    def generate_sports_insights(self, user, lookback_days=30):
        """
        Generate learning insights from sports betting patterns

        Used by UnifiedLearningPipeline to extract cross-domain intelligence

        Args:
            user: User object
            lookback_days: How far back to analyze

        Returns:
            List of LearningInsight objects
        """
        from core.unified_learning_pipeline import LearningInsight, LearningType
        from sports.models import UserBet, BankrollManagement

        insights = []

        # Get recent betting activity
        cutoff = timezone.now() - timedelta(days=lookback_days)
        recent_bets = UserBet.objects.filter(
            user=user,
            created_at__gte=cutoff
        )

        if not recent_bets.exists():
            return insights

        # Insight 1: Sport preferences
        sport_breakdown = recent_bets.values(
            'prediction__sport_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        if sport_breakdown:
            preferred_sports = [
                s['prediction__sport_type']
                for s in sport_breakdown
                if s['count'] >= 3 and s['prediction__sport_type']
            ]

            if preferred_sports:
                insights.append(LearningInsight(
                    insight_type=LearningType.USER_PREFERENCE,
                    source_system='sports_betting',
                    target_systems=['assistant', 'agents', 'advisors'],
                    insight_summary=f"User prefers betting on {', '.join(preferred_sports).upper()}",
                    confidence_score=0.8,
                    applicable_contexts=['sports_betting', 'opportunity_matching', 'user_preferences']
                ))

        # Insight 2: Risk behavior & profitability
        try:
            bankroll = BankrollManagement.objects.get(user=user)

            if bankroll.roi_percentage and bankroll.roi_percentage > 10:
                insights.append(LearningInsight(
                    insight_type=LearningType.SUCCESS_PATTERN,
                    source_system='sports_betting',
                    target_systems=['assistant', 'agents'],
                    insight_summary=f"User shows profitable sports betting (ROI: {bankroll.roi_percentage:.1f}%, Win Rate: {bankroll.win_rate:.1f}%)",
                    confidence_score=0.85,
                    applicable_contexts=['risk_assessment', 'decision_making', 'analytical_skills']
                ))

            # Insight 3: Analytical strength (high win rate = strong pattern recognition)
            if bankroll.win_rate and bankroll.win_rate > 55:
                insights.append(LearningInsight(
                    insight_type=LearningType.CAPABILITY_DISCOVERY,
                    source_system='sports_betting',
                    target_systems=['agents', 'opportunity_matching'],
                    insight_summary=f"User demonstrates strong analytical skills ({bankroll.win_rate:.1f}% betting accuracy)",
                    confidence_score=0.75,
                    applicable_contexts=['data_science_roles', 'analytical_positions', 'pattern_recognition']
                ))

            # Insight 4: Risk tolerance
            risk_profile = self._analyze_risk_tolerance(bankroll, recent_bets)
            if risk_profile:
                insights.append(LearningInsight(
                    insight_type=LearningType.BEHAVIORAL_PATTERN,
                    source_system='sports_betting',
                    target_systems=['assistant', 'agents'],
                    insight_summary=risk_profile['summary'],
                    confidence_score=risk_profile['confidence'],
                    applicable_contexts=['risk_assessment', 'job_negotiation', 'investment_opportunities']
                ))

        except BankrollManagement.DoesNotExist:
            pass

        logger.info(f"Generated {len(insights)} sports betting insights for user {user.id}")
        return insights

    def create_feedback_from_prediction(self, prediction):
        """
        Create FeedbackItem from evaluated sports prediction

        Used by PredictionEvaluator to feed results into learning loop

        Args:
            prediction: MLPrediction instance (with was_correct evaluated)

        Returns:
            FeedbackItem object ready for learning loop
        """
        from ai_core.intelligence.learning_loop import FeedbackItem

        # Determine rating based on correctness and confidence
        if prediction.was_correct:
            # Correct prediction - rating based on confidence
            # High confidence + correct = 1.0
            # Low confidence + correct = 0.7 (got lucky)
            rating = 0.7 + (prediction.confidence / 100.0 * 0.3)
        else:
            # Incorrect prediction - rating based on confidence
            # High confidence + wrong = 0.1 (very bad)
            # Low confidence + wrong = 0.4 (knew uncertainty)
            rating = 0.4 - (prediction.confidence / 100.0 * 0.3)

        feedback = FeedbackItem(
            id=str(prediction.id),
            timestamp=timezone.now(),
            source="sports_prediction_evaluator",
            category="prediction_accuracy",
            target=prediction.agent.name if prediction.agent else "sports_betting_system",
            rating=rating,
            message=f"{prediction.sport_type.upper()} prediction: {'correct' if prediction.was_correct else 'incorrect'} ({prediction.confidence}% confidence)",
            context={
                'sport': prediction.sport_type,
                'confidence': prediction.confidence,
                'was_correct': prediction.was_correct,
                'predicted_winner': prediction.predicted_winner.name if prediction.predicted_winner_id else None,
                'prediction_id': str(prediction.id),
                'game_date': prediction.game.scheduled_start.isoformat() if prediction.game_id else None
            }
        )

        return feedback

    # Private helper methods

    def _calculate_specialization(self, accuracy, sample_size):
        """Calculate specialization level based on accuracy and sample size"""
        if sample_size < 10:
            return 'novice'
        elif sample_size < 50:
            if accuracy > 60:
                return 'intermediate'
            return 'novice'
        elif sample_size >= 50:
            if accuracy > 65:
                return 'expert'
            elif accuracy > 55:
                return 'advanced'
            elif accuracy > 50:
                return 'intermediate'
            return 'novice'
        return 'novice'

    def _analyze_risk_tolerance(self, bankroll, recent_bets):
        """Analyze user's risk tolerance from betting patterns"""
        if not recent_bets.exists():
            return None

        # Calculate average bet size relative to bankroll
        avg_bet = recent_bets.aggregate(Avg('bet_amount'))['bet_amount__avg']
        if not avg_bet or not bankroll.current_balance or bankroll.current_balance == 0:
            return None

        avg_bet_percentage = (float(avg_bet) / float(bankroll.current_balance)) * 100

        # Determine profile
        if avg_bet_percentage > 10:
            risk_level = 'aggressive'
            summary = f"User exhibits aggressive risk-taking behavior (avg {avg_bet_percentage:.1f}% of bankroll per bet)"
            confidence = 0.8
        elif avg_bet_percentage > 5:
            risk_level = 'moderate'
            summary = f"User shows moderate risk tolerance (avg {avg_bet_percentage:.1f}% of bankroll per bet)"
            confidence = 0.75
        else:
            risk_level = 'conservative'
            summary = f"User demonstrates conservative risk management (avg {avg_bet_percentage:.1f}% of bankroll per bet)"
            confidence = 0.85

        return {
            'risk_level': risk_level,
            'summary': summary,
            'confidence': confidence,
            'avg_bet_percentage': avg_bet_percentage
        }

    def record_wager_outcome(self, wager):
        """
        Session 995: Record settled wager outcome into the learning loop.

        Creates/updates UserAgentLearning for SportsOddsAnalyst and creates
        AgentMemory entries with outcome details.

        Args:
            wager: PlacedWager instance (must be settled — won/lost/push)
        """
        from core.models_unified_system import UserAgentLearning, AgentMemory, Agent

        if not wager.user or wager.status == 'pending':
            return

        # Determine sport from first leg
        first_leg = wager.legs.first()
        if not first_leg:
            return

        sport_key = first_leg.sport or 'unknown'
        # Normalize sport key to short form for learning domain
        sport_short = sport_key.split('_')[-1] if '_' in sport_key else sport_key

        # Update/create UserAgentLearning for SportsOddsAnalyst
        learning, created = UserAgentLearning.objects.update_or_create(
            user=wager.user,
            agent_name='SportsOddsAnalyst',
            learning_domain=f'sports_betting_{sport_short}',
            defaults={
                'learning_content': {
                    'last_wager_id': str(wager.id),
                    'last_status': wager.status,
                    'last_result_amount': float(wager.result_amount or 0),
                    'wager_type': wager.wager_type,
                    'synced_at': timezone.now().isoformat(),
                },
                'learning_source': 'performance_tracking',
            }
        )

        if wager.status == 'won':
            learning.record_success()
        elif wager.status == 'lost':
            learning.record_failure()
        # push doesn't count as success or failure

        # Create AgentMemory entry
        try:
            agent = Agent.objects.filter(name='SportsOddsAnalyst').first()
            if agent:
                legs_summary = ', '.join(
                    f"{leg.pick} ({leg.matchup})" for leg in wager.legs.all()
                )
                AgentMemory.objects.create(
                    agent=agent,
                    title=f"Wager {wager.status}: {wager.wager_type} ${wager.stake}",
                    content=(
                        f"Wager settled as {wager.status}. "
                        f"Stake: ${wager.stake}, P/L: ${wager.result_amount or 0}. "
                        f"Legs: {legs_summary}"
                    ),
                    context=f"Sport: {sport_key}, Type: {wager.wager_type}",
                    memory_type='success' if wager.status == 'won' else 'failure',
                    valence='positive' if wager.status == 'won' else 'negative',
                    importance_score=0.6 if wager.status == 'won' else 0.8,
                    memory_outcome='success' if wager.status == 'won' else 'failure',
                    safety_class='approved',
                    source_type='betting_outcome_verification',
                    source_id=str(wager.id),
                    tags=[sport_short, wager.wager_type, 'verified', wager.status],
                )
        except Exception as e:
            logger.warning(f"Could not create AgentMemory for wager {wager.id}: {e}")

        logger.info(f"Recorded wager outcome: {wager.id} → {wager.status}")

    def record_arbitrage_outcome(self, arb_item):
        """
        Session 995: Record arbitrage verification outcome into the learning loop.

        Creates/updates UserAgentLearning for ArbitrageDetector and creates
        AgentMemory entries with predicted vs actual profit.

        Args:
            arb_item: HumanAttentionItem instance (must be verified)
        """
        from core.models_unified_system import UserAgentLearning, AgentMemory, Agent

        if not arb_item.user or arb_item.status != 'verified':
            return

        payload = arb_item.payload or {}
        sport = payload.get('sport', 'unknown')
        predicted_profit = payload.get('profit_pct', 0)
        actual_profit = arb_item.verification_profit or 0
        outcome = arb_item.verification_outcome

        is_success = outcome == 'won'

        # Update/create UserAgentLearning for ArbitrageDetector
        learning, created = UserAgentLearning.objects.update_or_create(
            user=arb_item.user,
            agent_name='ArbitrageDetector',
            learning_domain='general',
            defaults={
                'learning_content': {
                    'last_item_id': str(arb_item.id),
                    'last_outcome': outcome,
                    'last_predicted_profit': predicted_profit,
                    'last_actual_profit': actual_profit,
                    'synced_at': timezone.now().isoformat(),
                },
                'learning_source': 'performance_tracking',
            }
        )

        if is_success:
            learning.record_success()
        else:
            learning.record_failure()

        # Create AgentMemory entry
        try:
            agent = Agent.objects.filter(name='ArbitrageDetector').first()
            if agent:
                bookmakers = payload.get('bookmakers', [])
                bookmaker_str = ' vs '.join(bookmakers) if bookmakers else 'unknown'
                AgentMemory.objects.create(
                    agent=agent,
                    title=f"Arb {outcome}: {sport} ({bookmaker_str})",
                    content=(
                        f"Arbitrage verification: {outcome}. "
                        f"Predicted profit: {predicted_profit}%, Actual: ${actual_profit:.2f}. "
                        f"Bookmakers: {bookmaker_str}. Sport: {sport}. "
                        f"Event: {arb_item.title}"
                    ),
                    context=f"Sport: {sport}, Bookmakers: {bookmaker_str}",
                    memory_type='success' if is_success else 'failure',
                    valence='positive' if is_success else 'negative',
                    importance_score=0.6 if is_success else 0.8,
                    memory_outcome='success' if is_success else 'failure',
                    safety_class='approved',
                    source_type='arbitrage_verification',
                    source_id=str(arb_item.id),
                    tags=[sport, 'arbitrage', 'verified', outcome],
                )
        except Exception as e:
            logger.warning(f"Could not create AgentMemory for arb item {arb_item.id}: {e}")

        logger.info(
            f"Recorded arbitrage outcome: {arb_item.id} → {outcome} "
            f"(predicted {predicted_profit}%, actual ${actual_profit:.2f})"
        )


# Convenience functions for common operations

def sync_user_betting_to_learning(user):
    """
    Convenience function: Sync user's betting performance to core learning

    Args:
        user: User object

    Returns:
        Dict with sync results
    """
    bridge = SportsBettingLearningBridge(user=user)
    return bridge.sync_betting_performance_to_learning()


def sync_all_active_users():
    """
    Sync betting performance for all users with recent activity

    Returns:
        Dict with total sync results
    """
    from django.contrib.auth import get_user_model
    from sports.models import UserBet
    from datetime import timedelta

    User = get_user_model()
    cutoff = timezone.now() - timedelta(days=30)

    # Find users with recent betting activity
    active_user_ids = UserBet.objects.filter(
        created_at__gte=cutoff
    ).values_list('user_id', flat=True).distinct()

    results = {
        'success': True,
        'total_users': 0,
        'total_synced': 0,
        'errors': []
    }

    for user_id in active_user_ids:
        try:
            user = User.objects.get(id=user_id)
            sync_result = sync_user_betting_to_learning(user)

            if sync_result.get('success'):
                results['total_users'] += 1
                results['total_synced'] += len(sync_result.get('synced', []))
        except Exception as e:
            results['errors'].append({
                'user_id': user_id,
                'error': str(e)
            })
            logger.error(f"Error syncing user {user_id}: {e}")

    logger.info(
        f"Synced {results['total_synced']} learning entries "
        f"for {results['total_users']} users"
    )

    return results

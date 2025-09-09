"""
Sports Analytics Signals

Signal handlers for sports data updates, agent orchestration integration,
and real-time notifications through WebSocket channels.
"""

import logging
from typing import Dict, Any

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import (
    OddsLine, LineMovement, ArbitrageOpportunity, BettingRecommendation,
    Game, BettingMarket, Bet, GameStatus, MarketStatus
)
from core.models import PlatformMetrics

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@receiver(post_save, sender=OddsLine)
def handle_odds_update(sender, instance, created, **kwargs):
    """Handle odds line updates and broadcast to WebSocket clients"""
    if created and instance.is_current:
        # New odds line created
        try:
            # Record metric
            PlatformMetrics.record_metric(
                'odds_updates', 1, 'counter', 'sports',
                labels={
                    'sportsbook': instance.sportsbook.name,
                    'market_type': instance.market.market_type
                }
            )
            
            # Broadcast to WebSocket clients
            if channel_layer:
                # Send to market-specific group
                market_group = f"odds_{instance.market.id}"
                game_group = f"odds_game_{instance.market.game.id}"
                
                odds_data = {
                    'market_id': str(instance.market.id),
                    'game_id': str(instance.market.game.id),
                    'sportsbook': instance.sportsbook.name,
                    'sportsbook_id': str(instance.sportsbook.id),
                    'home_odds': instance.home_odds,
                    'away_odds': instance.away_odds,
                    'home_spread': instance.home_spread,
                    'away_spread': instance.away_spread,
                    'total_line': instance.total_line,
                    'over_odds': instance.over_odds,
                    'under_odds': instance.under_odds,
                    'line_sequence': instance.line_sequence,
                    'timestamp': instance.created_at.isoformat()
                }
                
                async_to_sync(channel_layer.group_send)(
                    market_group,
                    {
                        'type': 'odds_update',
                        'data': odds_data
                    }
                )
                
                async_to_sync(channel_layer.group_send)(
                    game_group,
                    {
                        'type': 'odds_update',
                        'data': odds_data
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling odds update: {e}")


@receiver(post_save, sender=LineMovement)
def handle_line_movement(sender, instance, created, **kwargs):
    """Handle line movements and broadcast significant moves"""
    if created:
        try:
            # Record metric
            PlatformMetrics.record_metric(
                'line_movements', 1, 'counter', 'sports',
                labels={
                    'significant': instance.is_significant,
                    'direction': instance.movement_direction,
                    'sportsbook': instance.sportsbook.name
                }
            )
            
            # Broadcast significant movements
            if instance.is_significant and channel_layer:
                market_group = f"odds_{instance.market.id}"
                game_group = f"odds_game_{instance.market.game.id}"
                
                movement_data = {
                    'market_id': str(instance.market.id),
                    'game_id': str(instance.market.game.id),
                    'sportsbook': instance.sportsbook.name,
                    'movement_size': instance.movement_size,
                    'movement_direction': instance.movement_direction,
                    'trigger_event': instance.trigger_event,
                    'is_significant': instance.is_significant,
                    'timestamp': instance.created_at.isoformat()
                }
                
                async_to_sync(channel_layer.group_send)(
                    market_group,
                    {
                        'type': 'line_movement',
                        'data': movement_data
                    }
                )
                
                async_to_sync(channel_layer.group_send)(
                    game_group,
                    {
                        'type': 'line_movement',
                        'data': movement_data
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling line movement: {e}")


@receiver(post_save, sender=ArbitrageOpportunity)
def handle_arbitrage_opportunity(sender, instance, created, **kwargs):
    """Handle arbitrage opportunity creation and updates"""
    if created:
        try:
            # Record metric
            PlatformMetrics.record_metric(
                'arbitrage_opportunities', 1, 'counter', 'sports',
                labels={
                    'profit_percentage': f"{instance.arbitrage_percentage:.1f}",
                    'market_type': instance.market_type,
                    'league': instance.game.league.abbreviation
                }
            )
            
            # Broadcast to arbitrage subscribers
            if channel_layer and instance.arbitrage_percentage >= 1.0:  # Only broadcast >1% opportunities
                arbitrage_group = "arbitrage_alerts"
                sport_group = f"arbitrage_{instance.game.league.sport_type}"
                
                arbitrage_data = {
                    'opportunity_id': str(instance.id),
                    'game_id': str(instance.game.id),
                    'game_matchup': f"{instance.game.away_team.abbreviation} @ {instance.game.home_team.abbreviation}",
                    'market_type': instance.market_type,
                    'profit_percentage': instance.arbitrage_percentage,
                    'minimum_profit': float(instance.minimum_profit),
                    'sportsbook_1': instance.sportsbook_1.name,
                    'sportsbook_2': instance.sportsbook_2.name,
                    'selection_1': instance.selection_1,
                    'selection_2': instance.selection_2,
                    'odds_1': instance.odds_1,
                    'odds_2': instance.odds_2,
                    'stake_1_percentage': instance.stake_1_percentage,
                    'stake_2_percentage': instance.stake_2_percentage,
                    'expires_at': instance.expires_at.isoformat(),
                    'confidence_score': instance.confidence_score,
                    'timestamp': instance.created_at.isoformat()
                }
                
                # Send to general arbitrage group
                async_to_sync(channel_layer.group_send)(
                    arbitrage_group,
                    {
                        'type': 'arbitrage_alert',
                        'data': arbitrage_data
                    }
                )
                
                # Send to sport-specific group
                async_to_sync(channel_layer.group_send)(
                    sport_group,
                    {
                        'type': 'arbitrage_alert',
                        'data': arbitrage_data
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling arbitrage opportunity: {e}")


@receiver(pre_save, sender=ArbitrageOpportunity)
def handle_arbitrage_expiration(sender, instance, **kwargs):
    """Handle arbitrage opportunity expiration"""
    if instance.pk:  # Only for updates, not new creations
        try:
            old_instance = ArbitrageOpportunity.objects.get(pk=instance.pk)
            
            # Check if opportunity is being deactivated
            if old_instance.is_active and not instance.is_active:
                # Broadcast expiration
                if channel_layer:
                    arbitrage_group = "arbitrage_alerts"
                    sport_group = f"arbitrage_{instance.game.league.sport_type}"
                    
                    expiration_data = {
                        'opportunity_id': str(instance.id),
                        'game_id': str(instance.game.id),
                        'reason': instance.closed_reason or 'Opportunity expired',
                        'timestamp': instance.updated_at.isoformat()
                    }
                    
                    async_to_sync(channel_layer.group_send)(
                        arbitrage_group,
                        {
                            'type': 'arbitrage_expired',
                            'data': expiration_data
                        }
                    )
                    
                    async_to_sync(channel_layer.group_send)(
                        sport_group,
                        {
                            'type': 'arbitrage_expired',
                            'data': expiration_data
                        }
                    )
                    
        except ArbitrageOpportunity.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error handling arbitrage expiration: {e}")


@receiver(post_save, sender=BettingRecommendation)
def handle_betting_recommendation(sender, instance, created, **kwargs):
    """Handle betting recommendation creation and updates"""
    if created:
        try:
            # Record metric
            PlatformMetrics.record_metric(
                'betting_recommendations', 1, 'counter', 'sports',
                labels={
                    'risk_level': instance.risk_level,
                    'expected_value': f"{float(instance.expected_value):.2f}",
                    'agent': instance.generating_agent
                }
            )
            
            # Broadcast to user's recommendation channel
            if channel_layer and instance.expected_value > 0:  # Only positive EV recommendations
                user_group = f"recommendations_{instance.user.id}"
                
                recommendation_data = {
                    'recommendation_id': str(instance.id),
                    'game_id': str(instance.game.id),
                    'game_matchup': f"{instance.game.away_team.abbreviation} @ {instance.game.home_team.abbreviation}",
                    'recommended_selection': instance.recommended_selection,
                    'recommended_sportsbook': instance.recommended_sportsbook.name,
                    'recommended_odds': instance.recommended_odds,
                    'recommended_stake': float(instance.recommended_stake),
                    'expected_value': float(instance.expected_value),
                    'win_probability': instance.win_probability,
                    'confidence_level': instance.confidence_level,
                    'risk_level': instance.risk_level,
                    'kelly_percentage': instance.kelly_percentage,
                    'reasoning': instance.reasoning,
                    'expires_at': instance.expires_at.isoformat(),
                    'timestamp': instance.created_at.isoformat()
                }
                
                async_to_sync(channel_layer.group_send)(
                    user_group,
                    {
                        'type': 'new_recommendation',
                        'data': recommendation_data
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling betting recommendation: {e}")


@receiver(post_save, sender=Game)
def handle_game_update(sender, instance, created, **kwargs):
    """Handle game status and score updates"""
    if not created:  # Only for updates
        try:
            # Check if this is a score or status update
            if instance.status in [GameStatus.LIVE, GameStatus.FINAL]:
                # Record metric
                PlatformMetrics.record_metric(
                    'game_updates', 1, 'counter', 'sports',
                    labels={
                        'status': instance.status,
                        'league': instance.league.abbreviation
                    }
                )
                
                # Broadcast game updates
                if channel_layer:
                    game_group = f"game_{instance.id}"
                    
                    game_data = {
                        'game_id': str(instance.id),
                        'status': instance.status,
                        'home_score': instance.home_score,
                        'away_score': instance.away_score,
                        'current_period': instance.current_period,
                        'time_remaining': instance.time_remaining,
                        'timestamp': instance.updated_at.isoformat()
                    }
                    
                    # Determine message type
                    message_type = 'score_update' if instance.home_score is not None else 'game_update'
                    
                    async_to_sync(channel_layer.group_send)(
                        game_group,
                        {
                            'type': message_type,
                            'data': game_data
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Error handling game update: {e}")


@receiver(post_save, sender=Bet)
def handle_bet_placement(sender, instance, created, **kwargs):
    """Handle bet placement and settlement"""
    if created:
        try:
            # Record bet placement metric
            PlatformMetrics.record_metric(
                'bets_placed', 1, 'counter', 'sports',
                labels={
                    'bet_type': instance.bet_type,
                    'sportsbook': instance.sportsbook.name,
                    'risk_level': instance.risk_level
                }
            )
            
            # Update user's dashboard
            if channel_layer:
                dashboard_group = f"dashboard_{instance.user.id}"
                
                bet_data = {
                    'bet_id': str(instance.id),
                    'selection': instance.selection,
                    'stake': float(instance.stake),
                    'odds': instance.odds_taken,
                    'potential_profit': float(instance.potential_profit),
                    'status': instance.status,
                    'timestamp': instance.created_at.isoformat()
                }
                
                async_to_sync(channel_layer.group_send)(
                    dashboard_group,
                    {
                        'type': 'dashboard_update',
                        'data': {
                            'type': 'bet_placed',
                            'bet': bet_data
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling bet placement: {e}")
    
    elif instance.status in ['won', 'lost', 'push'] and instance.settled_at:
        try:
            # Record bet settlement metric
            PlatformMetrics.record_metric(
                'bets_settled', 1, 'counter', 'sports',
                labels={
                    'result': instance.status,
                    'bet_type': instance.bet_type
                }
            )
            
            # Update user's dashboard with settlement
            if channel_layer:
                dashboard_group = f"dashboard_{instance.user.id}"
                
                settlement_data = {
                    'bet_id': str(instance.id),
                    'selection': instance.selection,
                    'result': instance.status,
                    'result_amount': float(instance.result_amount),
                    'settled_at': instance.settled_at.isoformat()
                }
                
                async_to_sync(channel_layer.group_send)(
                    dashboard_group,
                    {
                        'type': 'dashboard_update',
                        'data': {
                            'type': 'bet_settled',
                            'settlement': settlement_data
                        }
                    }
                )
                
        except Exception as e:
            logger.error(f"Error handling bet settlement: {e}")


@receiver(post_save, sender=BettingMarket)
def handle_market_status_change(sender, instance, created, **kwargs):
    """Handle betting market status changes"""
    if not created:  # Only for updates
        try:
            # Check if market status changed to closed or resulted
            if instance.status in [MarketStatus.CLOSED, MarketStatus.RESULTED]:
                # Record metric
                PlatformMetrics.record_metric(
                    'markets_closed', 1, 'counter', 'sports',
                    labels={
                        'market_type': instance.market_type,
                        'status': instance.status
                    }
                )
                
                # Broadcast market status change
                if channel_layer:
                    market_group = f"markets_{instance.game.id}"
                    
                    market_data = {
                        'market_id': str(instance.id),
                        'game_id': str(instance.game.id),
                        'market_type': instance.market_type,
                        'status': instance.status,
                        'settlement_value': instance.settlement_value,
                        'settled_at': instance.settled_at.isoformat() if instance.settled_at else None,
                        'timestamp': instance.updated_at.isoformat()
                    }
                    
                    async_to_sync(channel_layer.group_send)(
                        market_group,
                        {
                            'type': 'market_update',
                            'data': market_data
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Error handling market status change: {e}")


# Agent orchestration integration signals
@receiver(post_save, sender=OddsLine)
def trigger_agent_analysis(sender, instance, created, **kwargs):
    """Trigger agent analysis when new odds are posted"""
    if created and instance.is_current:
        try:
            # This would trigger agent analysis in a production system
            # For now, we'll just log the trigger
            logger.info(f"Triggering agent analysis for new odds: {instance}")
            
            # Could trigger:
            # - Value betting analysis
            # - Arbitrage detection
            # - Line movement analysis
            # - Recommendation generation
            
        except Exception as e:
            logger.error(f"Error triggering agent analysis: {e}")
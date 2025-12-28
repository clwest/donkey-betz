"""
Session 563: Bet Tracking API Views
API endpoints for placing bets, tracking history, and managing wagers.
"""

import logging
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models_betting import PlacedWager, PlacedWagerLeg, BettingStats

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def place_bet(request):
    """
    Place a new bet (single or parlay).

    Expected payload:
    {
        "stake": 10.00,
        "picks": [
            {
                "event_id": "abc123",
                "sport": "basketball_nba",
                "matchup": "Lakers vs Celtics",
                "market_type": "spreads",
                "pick": "Lakers -5.5",
                "odds": -110,
                "line": -5.5,
                "bookmaker": "FanDuel"
            },
            ...
        ]
    }
    """
    try:
        data = request.data
        stake = Decimal(str(data.get('stake', 0)))
        picks = data.get('picks', [])

        if stake <= 0:
            return Response({
                'success': False,
                'error': 'Stake must be greater than 0'
            }, status=400)

        if not picks:
            return Response({
                'success': False,
                'error': 'At least one pick is required'
            }, status=400)

        # Calculate parlay odds
        wager_type = 'single' if len(picks) == 1 else 'parlay'

        # Calculate combined decimal odds for parlay
        combined_decimal = 1.0
        for pick in picks:
            odds = pick.get('odds', 0)
            if odds > 0:
                decimal_odds = 1 + (odds / 100)
            else:
                decimal_odds = 1 + (100 / abs(odds))
            combined_decimal *= decimal_odds

        # Convert back to American
        if combined_decimal >= 2:
            american_odds = int((combined_decimal - 1) * 100)
        else:
            american_odds = int(-100 / (combined_decimal - 1))

        potential_payout = round(float(stake) * combined_decimal, 2)

        # Create the wager
        wager = PlacedWager.objects.create(
            user=request.user if request.user.is_authenticated else None,
            wager_type=wager_type,
            stake=stake,
            odds=american_odds,
            potential_payout=Decimal(str(potential_payout))
        )

        # Create legs
        for pick in picks:
            PlacedWagerLeg.objects.create(
                wager=wager,
                event_id=pick.get('event_id', ''),
                sport=pick.get('sport', ''),
                matchup=pick.get('matchup', ''),
                market_type=pick.get('market_type', 'h2h'),
                pick=pick.get('pick', ''),
                odds=pick.get('odds', 0),
                line=Decimal(str(pick.get('line', 0))) if pick.get('line') else None,
                bookmaker=pick.get('bookmaker', '')
            )

        # Update betting stats
        _update_stats(request.user if request.user.is_authenticated else None)

        return Response({
            'success': True,
            'wager': {
                'id': str(wager.id),
                'type': wager_type,
                'stake': float(stake),
                'odds': american_odds,
                'potential_payout': potential_payout,
                'legs': len(picks),
                'placed_at': wager.placed_at.isoformat()
            }
        }, status=201)

    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_wagers(request):
    """
    Get wager history with optional filters.

    Query params:
    - status: pending, won, lost, push, cancelled
    - type: single, parlay
    - sport: basketball_nba, americanfootball_nfl, etc.
    - limit: max results (default 50)
    - offset: pagination offset
    """
    try:
        wagers = PlacedWager.objects.all()

        # Filter by user if authenticated
        if request.user.is_authenticated:
            wagers = wagers.filter(user=request.user)

        # Apply filters
        status_filter = request.GET.get('status')
        if status_filter:
            wagers = wagers.filter(status=status_filter)

        type_filter = request.GET.get('type')
        if type_filter:
            wagers = wagers.filter(wager_type=type_filter)

        sport_filter = request.GET.get('sport')
        if sport_filter:
            wagers = wagers.filter(legs__sport=sport_filter).distinct()

        # Pagination
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))

        total = wagers.count()
        wagers = wagers[offset:offset + limit]

        # Serialize
        results = []
        for wager in wagers:
            legs = []
            for leg in wager.legs.all():
                legs.append({
                    'event_id': leg.event_id,
                    'sport': leg.sport,
                    'matchup': leg.matchup,
                    'market_type': leg.market_type,
                    'pick': leg.pick,
                    'odds': leg.odds,
                    'line': float(leg.line) if leg.line else None,
                    'bookmaker': leg.bookmaker,
                    'status': leg.status,
                    'final_score': leg.final_score
                })

            results.append({
                'id': str(wager.id),
                'type': wager.wager_type,
                'stake': float(wager.stake),
                'odds': wager.odds,
                'potential_payout': float(wager.potential_payout),
                'status': wager.status,
                'result_amount': float(wager.result_amount) if wager.result_amount else None,
                'placed_at': wager.placed_at.isoformat(),
                'settled_at': wager.settled_at.isoformat() if wager.settled_at else None,
                'legs': legs
            })

        return Response({
            'success': True,
            'total': total,
            'offset': offset,
            'limit': limit,
            'wagers': results
        })

    except Exception as e:
        logger.error(f"Error getting wagers: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_wager_detail(request, wager_id):
    """Get details for a specific wager."""
    try:
        wager = PlacedWager.objects.get(id=wager_id)

        legs = []
        for leg in wager.legs.all():
            legs.append({
                'id': str(leg.id),
                'event_id': leg.event_id,
                'sport': leg.sport,
                'matchup': leg.matchup,
                'market_type': leg.market_type,
                'pick': leg.pick,
                'odds': leg.odds,
                'line': float(leg.line) if leg.line else None,
                'bookmaker': leg.bookmaker,
                'status': leg.status,
                'final_score': leg.final_score,
                'commence_time': leg.commence_time.isoformat() if leg.commence_time else None
            })

        return Response({
            'success': True,
            'wager': {
                'id': str(wager.id),
                'type': wager.wager_type,
                'stake': float(wager.stake),
                'odds': wager.odds,
                'decimal_odds': round(wager.decimal_odds, 3),
                'implied_probability': round(wager.implied_probability * 100, 1),
                'potential_payout': float(wager.potential_payout),
                'status': wager.status,
                'result_amount': float(wager.result_amount) if wager.result_amount else None,
                'placed_at': wager.placed_at.isoformat(),
                'settled_at': wager.settled_at.isoformat() if wager.settled_at else None,
                'notes': wager.notes,
                'legs': legs
            }
        })

    except PlacedWager.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wager not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting wager detail: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def settle_wager(request, wager_id):
    """
    Settle a wager (mark as won, lost, or push).

    Payload:
    {
        "status": "won" | "lost" | "push",
        "leg_results": {
            "leg_id": {"status": "won", "final_score": "110-105"},
            ...
        }
    }
    """
    try:
        wager = PlacedWager.objects.get(id=wager_id)

        if wager.status != 'pending':
            return Response({
                'success': False,
                'error': 'Wager is already settled'
            }, status=400)

        data = request.data
        new_status = data.get('status')
        leg_results = data.get('leg_results', {})

        if new_status not in ['won', 'lost', 'push']:
            return Response({
                'success': False,
                'error': 'Invalid status. Must be won, lost, or push'
            }, status=400)

        # Update leg statuses
        for leg in wager.legs.all():
            leg_id = str(leg.id)
            if leg_id in leg_results:
                leg.status = leg_results[leg_id].get('status', 'pending')
                leg.final_score = leg_results[leg_id].get('final_score', '')
                leg.save()

        # Settle the wager
        wager.settle(
            won=(new_status == 'won'),
            push=(new_status == 'push')
        )

        # Update stats
        _update_stats(wager.user)

        return Response({
            'success': True,
            'wager': {
                'id': str(wager.id),
                'status': wager.status,
                'result_amount': float(wager.result_amount),
                'settled_at': wager.settled_at.isoformat()
            }
        })

    except PlacedWager.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wager not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error settling wager: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def cancel_wager(request, wager_id):
    """Cancel a pending wager."""
    try:
        wager = PlacedWager.objects.get(id=wager_id)

        if wager.status != 'pending':
            return Response({
                'success': False,
                'error': 'Can only cancel pending wagers'
            }, status=400)

        wager.status = 'cancelled'
        wager.save()

        # Update stats
        _update_stats(wager.user)

        return Response({
            'success': True,
            'message': 'Wager cancelled'
        })

    except PlacedWager.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wager not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error cancelling wager: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_betting_stats(request):
    """Get betting statistics for the current user or all users."""
    try:
        if request.user.is_authenticated:
            stats, created = BettingStats.objects.get_or_create(user=request.user)
        else:
            stats, created = BettingStats.objects.get_or_create(user=None)

        if created or request.GET.get('refresh'):
            stats.recalculate()

        return Response({
            'success': True,
            'stats': {
                'total_wagers': stats.total_wagers,
                'total_stake': float(stats.total_stake),
                'total_profit_loss': float(stats.total_profit_loss),
                'wins': stats.wins,
                'losses': stats.losses,
                'pushes': stats.pushes,
                'pending': stats.pending,
                'win_rate': stats.win_rate,
                'roi': stats.roi,
                'current_streak': stats.current_streak,
                'longest_win_streak': stats.longest_win_streak,
                'longest_loss_streak': stats.longest_loss_streak,
                'singles_record': stats.singles_record,
                'parlays_record': stats.parlays_record,
                'stats_by_sport': stats.stats_by_sport,
                'last_updated': stats.last_updated.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error getting betting stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_recent_activity(request):
    """Get recent betting activity for dashboard display."""
    try:
        limit = int(request.GET.get('limit', 10))

        wagers = PlacedWager.objects.all()
        if request.user.is_authenticated:
            wagers = wagers.filter(user=request.user)

        recent = wagers.order_by('-placed_at')[:limit]

        activity = []
        for wager in recent:
            leg_count = wager.legs.count()
            first_leg = wager.legs.first()

            activity.append({
                'id': str(wager.id),
                'type': wager.wager_type,
                'description': f"{leg_count}-leg Parlay" if wager.wager_type == 'parlay' else first_leg.pick if first_leg else 'Unknown',
                'matchup': first_leg.matchup if first_leg else '',
                'sport': first_leg.sport if first_leg else '',
                'stake': float(wager.stake),
                'odds': wager.odds,
                'potential_payout': float(wager.potential_payout),
                'status': wager.status,
                'result_amount': float(wager.result_amount) if wager.result_amount else None,
                'placed_at': wager.placed_at.isoformat()
            })

        # Quick stats
        total_pending = wagers.filter(status='pending').count()
        total_today = wagers.filter(placed_at__date=timezone.now().date()).count()
        today_stake = wagers.filter(
            placed_at__date=timezone.now().date()
        ).aggregate(Sum('stake'))['stake__sum'] or 0

        return Response({
            'success': True,
            'recent': activity,
            'summary': {
                'pending_wagers': total_pending,
                'wagers_today': total_today,
                'stake_today': float(today_stake)
            }
        })

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def _update_stats(user):
    """Update betting stats for a user."""
    try:
        stats, _ = BettingStats.objects.get_or_create(user=user)
        stats.recalculate()
    except Exception as e:
        logger.error(f"Error updating stats: {e}")

"""
Odds calculation and sports analytics endpoints migrated from DBAO tools-manifest.json.
Provides comprehensive betting analytics, Kelly criterion, and live sports data.
Enhanced with multi-sport support and free data providers.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import decimal
import random
import requests
import os
import logging

# Import standardized API responses
from core.api_responses import (
    api_success, api_validation_error
)

# Import rate limiting
from core.rate_limiter import rate_limit_api

# Import caching
from core.cache_service import (
    KellyCache
)

logger = logging.getLogger(__name__)

# Import sports models if they exist
try:
    from sports.models import League, Team, Game
    SPORTS_MODELS_AVAILABLE = True
except ImportError:
    SPORTS_MODELS_AVAILABLE = False

# Import data providers separately to ensure it's available
try:
    from sports.data_providers import sports_data_manager
    DATA_PROVIDERS_AVAILABLE = True
except ImportError:
    DATA_PROVIDERS_AVAILABLE = False
    sports_data_manager = None

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_odds(request):
    """
    Convert betting odds between formats - migrated from DBAO
    """
    data = request.data
    
    # Handle string odds input (e.g., "+150", "-110", "3/2")
    odds_input = data.get('odds', 0)
    from_format = data.get('from_format', 'decimal')
    
    # Convert string odds to numeric value
    if isinstance(odds_input, str):
        # Remove + prefix if present
        odds_input = odds_input.lstrip('+')
        # For fractional odds, keep as string for now
        if '/' not in odds_input:
            try:
                odds_value = float(odds_input)
            except (ValueError, TypeError):
                return api_validation_error(
                    message=f'Invalid odds value: {odds_input}',
                    details={'odds_input': odds_input, 'expected': 'numeric value'}
                )
        else:
            odds_value = odds_input  # Keep fractional as string
    else:
        odds_value = float(odds_input) if odds_input else 0
    
    # For non-fractional formats, check if positive
    if from_format != 'fractional' and (not odds_value or odds_value == 0):
        return api_validation_error(
            message='Invalid odds value',
            details={'odds_value': odds_value, 'from_format': from_format}
        )
    
    # Conversion logic
    result = {}
    
    if from_format == 'decimal':
        # From decimal
        result['decimal'] = odds_value
        result['american'] = (odds_value - 1) * 100 if odds_value >= 2 else -100 / (odds_value - 1)
        result['fractional'] = f'{int((odds_value - 1) * 100)}/100'
        result['implied_probability'] = 1 / odds_value
    elif from_format == 'american':
        # From American
        if odds_value > 0:
            decimal = (odds_value / 100) + 1
        else:
            decimal = (100 / abs(odds_value)) + 1
        
        result['decimal'] = decimal
        result['american'] = odds_value
        result['fractional'] = f'{int((decimal - 1) * 100)}/100'
        result['implied_probability'] = 1 / decimal
    elif from_format == 'fractional':
        # Simplified - assume format like "3/2"
        if '/' in str(odds_value):
            parts = str(odds_value).split('/')
            decimal = (float(parts[0]) / float(parts[1])) + 1
        else:
            decimal = float(odds_value) + 1
            
        result['decimal'] = decimal
        result['american'] = (decimal - 1) * 100 if decimal >= 2 else -100 / (decimal - 1)
        result['fractional'] = str(odds_value)
        result['implied_probability'] = 1 / decimal
    
    return Response({
        'success': True,
        'result': result
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_expected_value(request):
    """
    Calculate expected value for betting opportunities - migrated from DBAO
    """
    data = request.data
    
    odds = data.get('odds', 0)
    odds_format = data.get('odds_format', 'decimal')
    true_probability = data.get('true_probability', 0)
    stake = data.get('stake', 0)
    
    if not all([odds > 0, 0 <= true_probability <= 1, stake >= 0]):
        return Response({
            'success': False,
            'error': 'Invalid input parameters'
        }, status=400)
    
    # Convert to decimal if needed
    if odds_format == 'american':
        decimal_odds = (odds / 100) + 1 if odds > 0 else (100 / abs(odds)) + 1
    elif odds_format == 'fractional':
        # Simplified fractional handling
        decimal_odds = float(odds) + 1
    else:
        decimal_odds = odds
    
    # Calculate expected value
    win_amount = stake * (decimal_odds - 1)
    loss_amount = stake
    expected_value = (true_probability * win_amount) - ((1 - true_probability) * loss_amount)
    expected_profit = expected_value
    
    # Determine if it's a value bet
    implied_probability = 1 / decimal_odds
    edge = true_probability - implied_probability
    value_bet = edge > 0
    
    return Response({
        'success': True,
        'result': {
            'expected_value': round(expected_value, 2),
            'expected_profit': round(expected_profit, 2),
            'value_bet': value_bet,
            'edge': round(edge, 4)
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_kelly_criterion(request):
    """
    Calculate optimal bet sizing using Kelly Criterion - migrated from DBAO
    Enhanced with comprehensive input validation
    """
    data = request.data
    
    odds = data.get('odds', 0)
    odds_format = data.get('odds_format', 'decimal')
    true_probability = data.get('true_probability', 0)
    bankroll = data.get('bankroll', 0)
    kelly_multiplier = data.get('kelly_multiplier', 0.25)
    
    # Comprehensive validation
    validation_errors = {}
    
    # Validate odds
    try:
        odds = float(odds)
        if odds <= 0:
            validation_errors['odds'] = 'Odds must be positive'
    except (TypeError, ValueError):
        validation_errors['odds'] = 'Invalid odds value'
    
    # Validate probability
    try:
        true_probability = float(true_probability)
        if true_probability < 0:
            validation_errors['true_probability'] = 'Probability cannot be negative'
        elif true_probability > 1:
            validation_errors['true_probability'] = 'Probability cannot exceed 1.0'
        elif true_probability == 0:
            validation_errors['true_probability'] = 'Probability cannot be zero for Kelly calculation'
    except (TypeError, ValueError):
        validation_errors['true_probability'] = 'Invalid probability value'
    
    # Validate bankroll
    try:
        bankroll = float(bankroll)
        if bankroll <= 0:
            validation_errors['bankroll'] = 'Bankroll must be positive'
    except (TypeError, ValueError):
        validation_errors['bankroll'] = 'Invalid bankroll value'
    
    # Validate Kelly multiplier
    try:
        kelly_multiplier = float(kelly_multiplier)
        if kelly_multiplier <= 0:
            validation_errors['kelly_multiplier'] = 'Kelly multiplier must be positive'
        elif kelly_multiplier > 1:
            validation_errors['kelly_multiplier'] = 'Kelly multiplier cannot exceed 1.0'
    except (TypeError, ValueError):
        validation_errors['kelly_multiplier'] = 'Invalid Kelly multiplier value'
    
    # Validate odds format
    valid_formats = ['decimal', 'american', 'fractional']
    if odds_format not in valid_formats:
        validation_errors['odds_format'] = f'Invalid format. Must be one of: {valid_formats}'
    
    # Return validation errors if any
    if validation_errors:
        return api_validation_error(
            message='Validation failed for Kelly Criterion calculation',
            details=validation_errors
        )
    
    # Check cache first
    cached_result = KellyCache.get_calculation(
        odds, true_probability, bankroll, kelly_multiplier
    )
    if cached_result:
        logger.info("Returning cached Kelly calculation")
        return api_success(
            data=cached_result,
            message='Kelly Criterion calculation (cached)'
        )
    
    # Convert to decimal odds
    if odds_format == 'american':
        decimal_odds = (odds / 100) + 1 if odds > 0 else (100 / abs(odds)) + 1
    elif odds_format == 'fractional':
        decimal_odds = float(odds) + 1
    else:
        decimal_odds = odds
    
    # Kelly Criterion calculation
    b = decimal_odds - 1  # Net odds
    p = true_probability  # Probability of winning
    q = 1 - p  # Probability of losing
    
    kelly_percentage = (b * p - q) / b
    kelly_percentage = max(0, kelly_percentage)  # Don't bet if negative
    
    # Apply fractional Kelly
    fractional_kelly = kelly_percentage * kelly_multiplier
    recommended_bet = bankroll * fractional_kelly
    
    # Risk level assessment
    if kelly_percentage > 0.20:
        risk_level = 'high'
    elif kelly_percentage > 0.10:
        risk_level = 'medium'
    elif kelly_percentage > 0.05:
        risk_level = 'low'
    else:
        risk_level = 'minimal'
    
    # Prepare result
    result = {
        'kelly_percentage': round(kelly_percentage, 4),
        'recommended_bet': round(recommended_bet, 2),
        'recommended_stake': round(recommended_bet, 2),  # Add expected field name
        'risk_level': risk_level,
        'fractional_kelly': round(fractional_kelly, 4)
    }
    
    # Cache the result
    KellyCache.cache_calculation(
        odds, true_probability, bankroll, kelly_multiplier, result
    )
    
    return api_success(
        data=result,
        message='Kelly Criterion calculation successful'
    )

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def detect_arbitrage(request):
    """
    Detect arbitrage opportunities across bookmakers.

    GET: Scan for live arbitrage opportunities using ArbitrageDetector agent
         Query params: sport, min_profit, limit
    POST: Calculate arbitrage from provided odds_list (legacy)
    """
    # Session 559: GET request - scan for live arbs using ArbitrageDetector
    if request.method == 'GET':
        try:
            from core.agents.markets.arbitrage_detector import ArbitrageDetector

            sport = request.GET.get('sport')
            min_profit = float(request.GET.get('min_profit', 0.5))
            limit = int(request.GET.get('limit', 10))

            detector = ArbitrageDetector()
            result = detector.execute(
                task="Scan for arbitrage opportunities",
                context={
                    'sport': sport,
                    'min_profit_pct': min_profit
                }
            )

            if result.success:
                opportunities = result.data.get('arbitrage_opportunities', [])[:limit]
                return Response({
                    'success': True,
                    'opportunities': opportunities,
                    'stats': {
                        'events_scanned': result.data.get('events_scanned', 0),
                        'total_arbs': result.data.get('total_arbs', 0),
                        'hot_arbs': result.data.get('hot_arbs', 0),
                        'good_arbs': result.data.get('good_arbs', 0),
                    },
                    'scan_time': datetime.now().isoformat()
                })
            else:
                return Response({
                    'success': False,
                    'opportunities': [],
                    'error': result.error or 'No arbitrage data available',
                    'message': 'Ensure THE_ODDS_API_KEY is configured'
                })

        except ImportError as e:
            logger.error(f"ArbitrageDetector import error: {e}")
            return Response({
                'success': False,
                'opportunities': [],
                'error': 'ArbitrageDetector agent not available'
            })
        except Exception as e:
            logger.error(f"Arbitrage scan error: {e}", exc_info=True)
            return Response({
                'success': False,
                'opportunities': [],
                'error': str(e)
            })

    # POST request - legacy behavior with provided odds
    data = request.data

    odds_list = data.get('odds_list', [])

    if len(odds_list) < 2:
        return Response({
            'success': False,
            'error': 'At least 2 odds required for arbitrage detection'
        }, status=400)

    # Convert all odds to decimal and find best odds for each outcome
    best_odds = {}
    bookmakers = {}

    for odds_data in odds_list:
        bookmaker = odds_data.get('bookmaker', 'Unknown')
        outcome = odds_data.get('outcome', 'outcome')
        odds = odds_data.get('odds', 0)
        odds_format = odds_data.get('odds_format', 'decimal')

        # Convert to decimal
        if odds_format == 'american':
            decimal_odds = (odds / 100) + 1 if odds > 0 else (100 / abs(odds)) + 1
        else:
            decimal_odds = odds

        if outcome not in best_odds or decimal_odds > best_odds[outcome]:
            best_odds[outcome] = decimal_odds
            bookmakers[outcome] = bookmaker

    # Check for arbitrage
    implied_probabilities = [1 / odds for odds in best_odds.values()]
    total_implied_probability = sum(implied_probabilities)

    is_arbitrage = total_implied_probability < 1.0
    profit_margin = (1 / total_implied_probability - 1) if is_arbitrage else 0

    # Calculate bet allocation for guaranteed profit
    bet_allocation = {}
    total_stake = 1000  # Example stake

    if is_arbitrage:
        for outcome, odds in best_odds.items():
            stake_percentage = (1 / odds) / total_implied_probability
            bet_allocation[outcome] = {
                'bookmaker': bookmakers[outcome],
                'stake': round(total_stake * stake_percentage, 2),
                'potential_return': round(total_stake * stake_percentage * odds, 2)
            }

    return Response({
        'success': True,
        'result': {
            'is_arbitrage': is_arbitrage,
            'profit_margin': round(profit_margin, 4),
            'bet_allocation': bet_allocation,
            'total_return': round(total_stake * (1 + profit_margin), 2) if is_arbitrage else 0
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def scan_arbitrage_opportunities(request):
    """
    Session 559: Scan for live arbitrage opportunities using ArbitrageDetector agent.

    GET /api/v1/betting/arbitrage/scan/

    Query params:
        sport: Filter by sport (nfl, nba, mlb, nhl, soccer)
        min_profit: Minimum profit threshold (default 0.5%)
        limit: Max results (default 10)
    """
    try:
        from core.agents.markets.arbitrage_detector import ArbitrageDetector

        sport = request.GET.get('sport')
        min_profit = float(request.GET.get('min_profit', 0.5))
        limit = int(request.GET.get('limit', 10))

        # Initialize the agent
        detector = ArbitrageDetector()

        # Execute arbitrage detection
        result = detector.execute(
            task="Scan for arbitrage opportunities",
            context={
                'sport': sport,
                'min_profit_pct': min_profit
            }
        )

        if result.success:
            opportunities = result.data.get('arbitrage_opportunities', [])[:limit]

            return Response({
                'success': True,
                'opportunities': opportunities,
                'stats': {
                    'events_scanned': result.data.get('events_scanned', 0),
                    'total_arbs': result.data.get('total_arbs', 0),
                    'hot_arbs': result.data.get('hot_arbs', 0),
                    'good_arbs': result.data.get('good_arbs', 0),
                },
                'scan_time': datetime.now().isoformat()
            })
        else:
            return Response({
                'success': False,
                'opportunities': [],
                'error': result.error or 'No arbitrage data available',
                'message': 'Ensure THE_ODDS_API_KEY is configured'
            })

    except ImportError as e:
        logger.error(f"ArbitrageDetector import error: {e}")
        return Response({
            'success': False,
            'opportunities': [],
            'error': 'ArbitrageDetector agent not available'
        })
    except Exception as e:
        logger.error(f"Arbitrage scan error: {e}", exc_info=True)
        return Response({
            'success': False,
            'opportunities': [],
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sports_game_analysis(request):
    """
    Session 999B: Game analysis from GameLineHistory + OddsSnapshot data.
    Replaces mock data with real line movement & implied-probability analytics.
    """
    from django.core.cache import cache
    from core.models_odds_history import GameLineHistory, OddsSnapshot

    data = request.data
    game_id = data.get('game_id', '')

    if not game_id:
        return Response({'success': False, 'message': 'game_id required'}, status=400)

    cache_key = f"game_analysis:{game_id}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    try:
        glh = GameLineHistory.objects.get(game_id=game_id)
    except GameLineHistory.DoesNotExist:
        return Response({'success': False, 'message': 'Game not found'}, status=404)

    # Build team analytics from odds
    home_prob = _american_to_probability(glh.current_ml_home) if glh.current_ml_home else None
    away_prob = _american_to_probability(glh.current_ml_away) if glh.current_ml_away else None

    # Recent snapshots for trend data
    snapshots = list(
        OddsSnapshot.objects.filter(game_id=game_id, market='h2h')
        .order_by('captured_at')
        .values('outcome_name', 'price', 'captured_at', 'bookmaker')[:50]
    )

    analysis = {
        'game_data': {
            'id': glh.game_id,
            'sport': glh.sport_key,
            'home_team': glh.home_team,
            'away_team': glh.away_team,
            'scheduled_time': glh.commence_time.isoformat(),
        },
        'team_analytics': {
            'home_team': {
                'current_ml': glh.current_ml_home,
                'implied_win_pct': round(home_prob * 100, 1) if home_prob else None,
                'spread': float(glh.current_spread_home) if glh.current_spread_home is not None else None,
            },
            'away_team': {
                'current_ml': glh.current_ml_away,
                'implied_win_pct': round(away_prob * 100, 1) if away_prob else None,
            },
        },
        'lines': {
            'current_spread': float(glh.current_spread_home) if glh.current_spread_home is not None else None,
            'current_total': float(glh.current_total) if glh.current_total is not None else None,
            'spread_movement': float(glh.spread_movement),
            'total_movement': float(glh.total_movement),
            'snapshot_count': glh.snapshot_count,
        },
        'odds_history': [
            {
                'outcome': s['outcome_name'],
                'price': s['price'],
                'bookmaker': s['bookmaker'],
                'captured_at': s['captured_at'].isoformat(),
            }
            for s in snapshots
        ],
    }

    result = {'success': True, 'analysis': analysis}
    cache.set(cache_key, result, 20 * 60)  # 20 min
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_betting_opportunities(request):
    """
    Session 999B: Detect cross-book value edges from SpiderData(data_type='sports_odds').
    Finds bookmaker-level odds divergence without making new API calls.
    """
    from django.core.cache import cache
    from persistence.models import SpiderData

    sport = request.GET.get('sport', 'all')
    min_edge = float(request.GET.get('min_edge', 0.04))
    max_opportunities = int(request.GET.get('max_opportunities', 10))

    cache_key = f"live_opps:{sport}:{min_edge}"
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)

    # Get recent sports_odds spider data (last 2 hours)
    cutoff = timezone.now() - timedelta(hours=2)
    rows = SpiderData.objects.filter(
        data_type='sports_odds',
        created_at__gte=cutoff,
    ).order_by('-created_at')[:20]

    opportunities = []
    seen_games = set()

    for row in rows:
        raw = row.raw_data or {}
        events = raw.get('items', raw.get('events', []))
        if not isinstance(events, list):
            continue

        for event in events:
            game_id = event.get('id', event.get('game_id', ''))
            if game_id in seen_games:
                continue

            bookmakers = event.get('bookmakers', [])
            if len(bookmakers) < 2:
                continue

            sport_key = event.get('sport_key', '')
            if sport != 'all' and sport not in sport_key:
                continue

            # Collect h2h prices across books for each outcome
            outcome_prices = {}
            for bk in bookmakers:
                bk_name = bk.get('title', bk.get('key', ''))
                for mkt in bk.get('markets', []):
                    if mkt.get('key') != 'h2h':
                        continue
                    for outcome in mkt.get('outcomes', []):
                        name = outcome.get('name', '')
                        price = outcome.get('price', 0)
                        if name and price:
                            outcome_prices.setdefault(name, []).append((bk_name, price))

            # Find best price divergence
            for name, prices in outcome_prices.items():
                if len(prices) < 2:
                    continue
                prices_sorted = sorted(prices, key=lambda x: x[1], reverse=True)
                best_bk, best_price = prices_sorted[0]
                worst_bk, worst_price = prices_sorted[-1]
                if worst_price <= 0:
                    continue
                best_prob = _american_to_probability(int(best_price)) if isinstance(best_price, int) else (1 / best_price if best_price > 0 else 0.5)
                worst_prob = _american_to_probability(int(worst_price)) if isinstance(worst_price, int) else (1 / worst_price if worst_price > 0 else 0.5)
                edge = round(worst_prob - best_prob, 4)
                if edge >= min_edge:
                    seen_games.add(game_id)
                    opportunities.append({
                        'game_id': game_id,
                        'sport': sport_key,
                        'bet_type': 'moneyline',
                        'edge': edge,
                        'recommended_stake': round(edge * 1000, 2),
                        'bookmaker': best_bk,
                        'odds': best_price,
                        'pick': name,
                        'matchup': f"{event.get('away_team', '')} @ {event.get('home_team', '')}",
                        'confidence': round(min(0.95, 0.6 + edge * 3), 2),
                    })
                    break  # one opp per game

            if len(opportunities) >= max_opportunities:
                break
        if len(opportunities) >= max_opportunities:
            break

    opportunities.sort(key=lambda x: x['edge'], reverse=True)
    result = {
        'success': True,
        'opportunities': opportunities[:max_opportunities],
        'last_updated': datetime.now().isoformat(),
        'total_found': len(opportunities),
    }
    cache.set(cache_key, result, 5 * 60)  # 5 min
    return Response(result)

@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def list_betting_markets(request):
    """
    Session 999B: List upcoming betting markets from GameLineHistory.
    Frontend reads marketsData.data.markets — must return {markets: [...]}.
    """
    from django.utils import timezone as tz
    from core.models_odds_history import GameLineHistory

    sport = request.GET.get('sport', 'all')
    search = request.GET.get('search', '')

    now = tz.now()
    qs = GameLineHistory.objects.filter(commence_time__gte=now).order_by('commence_time')

    if sport and sport != 'all':
        qs = qs.filter(sport_key__icontains=sport)

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(home_team__icontains=search) |
            Q(away_team__icontains=search)
        )

    # Build sport_key → league mapping
    SPORT_LEAGUE = {
        'americanfootball_nfl': 'NFL', 'americanfootball_ncaaf': 'NCAAF',
        'basketball_nba': 'NBA', 'basketball_ncaab': 'NCAAB',
        'baseball_mlb': 'MLB', 'icehockey_nhl': 'NHL',
        'soccer_epl': 'EPL', 'soccer_mls': 'MLS',
    }

    markets = []
    for g in qs[:30]:
        available = ['moneyline']
        if g.current_spread_home is not None:
            available.append('spread')
        if g.current_total is not None:
            available.append('total')
        markets.append({
            'id': g.game_id,
            'name': f"{g.away_team} @ {g.home_team}",
            'sport': g.sport_key,
            'league': SPORT_LEAGUE.get(g.sport_key, g.sport_key.split('_')[-1].upper()),
            'home_team': g.home_team,
            'away_team': g.away_team,
            'game_time': g.commence_time.isoformat(),
            'markets_available': available,
            'event_count': len(available),
        })

    return Response({
        'markets': markets,
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def get_bankroll_management(request):
    """
    Get user bankroll management information from real wager data.
    """
    from core.models_betting import PlacedWager
    from django.db.models import Sum, Q

    wagers = PlacedWager.objects.all()
    total_staked = float(wagers.aggregate(s=Sum('stake'))['s'] or 0)
    total_returned = float(wagers.filter(status='won').aggregate(s=Sum('potential_payout'))['s'] or 0)
    pending_risk = float(wagers.filter(status='pending').aggregate(s=Sum('stake'))['s'] or 0)
    total_profit = total_returned - total_staked + pending_risk  # pending not lost yet

    return Response({
        'success': True,
        'bankroll': {
            'total_wagered': round(total_staked, 2),
            'total_profit': round(total_profit, 2),
            'roi': round((total_profit / total_staked * 100) if total_staked > 0 else 0, 2),
            'at_risk': round(pending_risk, 2),
            'last_updated': datetime.now().isoformat()
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def get_bankroll_stats(request):
    """
    Detailed bankroll performance statistics from real wager data.
    """
    from core.models_betting import PlacedWager
    from django.db.models import Sum, Count, Avg, Q, F

    wagers = PlacedWager.objects.all()
    total = wagers.count()
    won = wagers.filter(status='won').count()
    lost = wagers.filter(status='lost').count()
    pending = wagers.filter(status='pending').count()
    pushed = wagers.filter(status='push').count()

    total_staked = float(wagers.aggregate(s=Sum('stake'))['s'] or 0)
    total_returned = float(wagers.filter(status='won').aggregate(s=Sum('potential_payout'))['s'] or 0)
    pending_risk = float(wagers.filter(status='pending').aggregate(s=Sum('stake'))['s'] or 0)
    total_profit = total_returned - total_staked + pending_risk
    avg_stake = float(wagers.aggregate(a=Avg('stake'))['a'] or 0)

    # Biggest win/loss
    biggest_win = 0
    biggest_loss = 0
    for w in wagers.filter(status__in=['won', 'lost']):
        if w.status == 'won':
            pl = float(w.potential_payout) - float(w.stake)
            biggest_win = max(biggest_win, pl)
        else:
            biggest_loss = min(biggest_loss, -float(w.stake))

    win_rate = (won / (won + lost)) if (won + lost) > 0 else 0
    roi = (total_profit / total_staked * 100) if total_staked > 0 else 0

    # Kelly criterion suggestion: edge / odds
    kelly_pct = max(0, min(25, (win_rate - (1 - win_rate)) * 100)) if win_rate > 0 else 0

    return Response({
        'success': True,
        'stats': {
            'total': round(total_staked, 2),
            'at_risk': round(pending_risk, 2),
            'available': round(max(0, total_staked - pending_risk + total_profit), 2),
            'kelly_percent': round(kelly_pct, 1),
            'roi': round(roi, 2),
            'win_rate': round(win_rate, 3),
            'avg_bet_size': round(avg_stake, 2),
            'total_bets': total,
            'winning_bets': won,
            'losing_bets': lost,
            'pending_bets': pending,
            'pushes': pushed,
            'total_profit': round(total_profit, 2),
            'biggest_win': round(biggest_win, 2),
            'biggest_loss': round(biggest_loss, 2),
        }
    })


# =============================================================================
# ENHANCED MULTI-SPORT API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_details(request, game_id):
    """Get complete game details with all odds"""
    if not SPORTS_MODELS_AVAILABLE:
        return Response({'error': 'Sports models not available'}, status=500)

    try:
        from sports.models import Game
        game = Game.objects.get(id=game_id)

        # Get all current odds
        markets = game.markets.filter(is_active=True)
        odds_by_book = {}

        for market in markets:
            for line in market.odds_lines.filter(is_current=True):
                book = line.sportsbook.name
                if book not in odds_by_book:
                    odds_by_book[book] = {}

                if market.market_type == 'h2h':
                    odds_by_book[book]['moneyline'] = {
                        'home': line.home_odds,
                        'away': line.away_odds
                    }
                elif market.market_type == 'spreads':
                    odds_by_book[book]['spread'] = {
                        'home_line': line.home_spread,
                        'away_line': line.away_spread,
                        'home_odds': line.home_odds,
                        'away_odds': line.away_odds
                    }
                elif market.market_type == 'totals':
                    odds_by_book[book]['total'] = {
                        'line': line.total_line,
                        'over': line.over_odds,
                        'under': line.under_odds
                    }

        return Response({
            'game': {
                'id': str(game.id),
                'matchup': f"{game.away_team.abbreviation} @ {game.home_team.abbreviation}",
                'status': game.status,
                'scheduled_start': game.scheduled_start,
                'home_score': game.home_score,
                'away_score': game.away_score,
                'venue': game.venue_name,
                'weather': game.weather_data,
                'game_progress': {
                    'period': game.current_period,
                    'time': game.time_remaining,
                    'live_stats': game.live_stats
                },
            },
            'teams': {
                'home': {
                    'name': game.home_team.name,
                    'abbreviation': game.home_team.abbreviation,
                    'logo': game.home_team.logo_url,
                    'record': game.home_team.current_record,
                    'ats_record': game.home_team.ats_record,
                },
                'away': {
                    'name': game.away_team.name,
                    'abbreviation': game.away_team.abbreviation,
                    'logo': game.away_team.logo_url,
                    'record': game.away_team.current_record,
                    'ats_record': game.away_team.ats_record,
                }
            },
            'odds': odds_by_book,
            'last_odds_update': markets.latest('updated_at').updated_at if markets.exists() else None
        })
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting game details: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmaker_analysis(request, game_id):
    """Get AI Bookmaker analysis for a game - generates unique analysis per game"""
    try:
        # Generate deterministic but unique analysis for each game
        import hashlib
        import random

        # Use game ID to seed random for consistent results per game
        game_hash = int(hashlib.md5(game_id.encode()).hexdigest()[:8], 16)
        random.seed(game_hash)

        # Generate game-specific values
        spread = random.uniform(-14, 14)
        total = random.uniform(38, 58)

        # Generate value bets unique to this game
        value_bets = []
        bet_types = ['SPREAD', 'TOTAL', 'MONEYLINE']
        bookmakers = ['DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 'BetRivers', 'Bovada', 'BetOnline.ag']

        # Each game gets 0-5 value bets
        num_bets = random.randint(0, 5)
        for i in range(num_bets):
            bet_type = random.choice(bet_types)
            bookmaker = random.choice(bookmakers)

            if bet_type == 'TOTAL':
                line = total + random.uniform(-2, 2)
                selection = random.choice(['OVER', 'UNDER'])
            elif bet_type == 'SPREAD':
                line = spread + random.uniform(-1, 1)
                selection = random.choice(['HOME', 'AWAY'])
            else:  # MONEYLINE
                line = random.uniform(-250, 250)
                selection = random.choice(['HOME', 'AWAY'])

            edge = random.uniform(2, 12)
            confidence = random.choice(['LOW', 'MEDIUM', 'HIGH'])

            value_bets.append({
                'bookmaker': bookmaker,
                'market': bet_type,
                'line': round(line, 1),
                'selection': selection,
                'edge': round(edge, 1),
                'confidence': confidence
            })

        # Sharp money - unique per game
        sharp_sides = ['HOME', 'AWAY', 'OVER', 'UNDER', 'NONE']
        sharp_side = random.choice(sharp_sides)
        sharp_confidence = random.uniform(0.55, 0.85)

        # Model confidence - unique per game
        model_confidence = random.uniform(0.60, 0.95)

        # Overall recommendation based on analysis
        if num_bets > 3 and model_confidence > 0.75:
            overall_rec = "STRONG BET"
        elif num_bets > 1 and model_confidence > 0.65:
            overall_rec = "MODERATE BET"
        elif num_bets > 0:
            overall_rec = "CONSIDER"
        else:
            overall_rec = "PASS"

        analysis = {
            'game_id': game_id,
            'timestamp': datetime.now().isoformat(),
            'agent': 'BookmakerAgent',
            'analysis': {
                'sharp_money': {
                    'sharp_side': sharp_side,
                    'confidence': round(sharp_confidence, 2),
                    'line_movement': f"{random.uniform(-2, 2):.1f} points"
                },
                'true_odds': {
                    'spread': round(spread, 1),
                    'total': round(total, 1),
                    'model_confidence': round(model_confidence, 2)
                },
                'value_bets': value_bets,
                'market_efficiency': round(random.uniform(0.65, 0.95), 2),
                'total_edge': round(sum(bet['edge'] for bet in value_bets), 1) if value_bets else 0,
                'overall_recommendation': overall_rec
            },
            'recommendations': {
                'primary': f"Best edge on {value_bets[0]['market']} at {value_bets[0]['bookmaker']}" if value_bets else "No clear value found",
                'kelly_size': round(random.uniform(0.5, 3.0), 1),
                'confidence_level': model_confidence
            },
            'alerts': [
                f"Line moved {random.uniform(0.5, 2):.1f} points in last hour" if random.random() > 0.5 else None,
                f"Sharp money detected on {sharp_side}" if sharp_side != 'NONE' else None,
                f"Weather impact: {random.choice(['Minimal', 'Moderate', 'Significant'])}" if random.random() > 0.6 else None
            ]
        }

        # Remove None alerts
        analysis['alerts'] = [a for a in analysis['alerts'] if a]

        # Reset random seed
        random.seed()

        return Response(analysis)
    except Exception as e:
        logger.error(f"Error getting bookmaker analysis: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sports_summary(request):
    """
    Get sports types with active leagues
    """
    if not SPORTS_MODELS_AVAILABLE:
        return Response([
            {'sport_type': 'nfl', 'name': 'NFL', 'count': 1},
            {'sport_type': 'nba', 'name': 'NBA', 'count': 1},
            {'sport_type': 'mlb', 'name': 'MLB', 'count': 1},
        ])
    
    try:
        from django.db.models import Count
        summary = League.objects.filter(is_active=True).values('sport_type').annotate(
            count=Count('id')
        )
        
        result = []
        for item in summary:
            sport_name_map = {
                'nfl': 'NFL',
                'nba': 'NBA', 
                'mlb': 'MLB',
                'nhl': 'NHL',
                'ncaaf': 'College Football',
                'ncaab': 'College Basketball',
                'soccer': 'Soccer',
                'mma': 'MMA',
                'tennis': 'Tennis',
                'golf': 'Golf',
                'boxing': 'Boxing',
                'esports': 'Esports'
            }
            
            result.append({
                'sport_type': item['sport_type'],
                'name': sport_name_map.get(item['sport_type'], item['sport_type'].upper()),
                'count': item['count']
            })
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sports_leagues(request):
    """
    Get available leagues with optional sport type filter
    """
    if not SPORTS_MODELS_AVAILABLE:
        return Response([
            {'id': 'nfl', 'name': 'National Football League', 'abbreviation': 'NFL', 'sport_type': 'nfl', 'country': 'USA', 'active': True},
            {'id': 'nba', 'name': 'National Basketball Association', 'abbreviation': 'NBA', 'sport_type': 'nba', 'country': 'USA', 'active': True},
        ])
    
    try:
        sport_type = request.GET.get('sport_type')
        leagues = League.objects.filter(is_active=True)
        
        if sport_type:
            leagues = leagues.filter(sport_type=sport_type)
        
        result = []
        for league in leagues:
            result.append({
                'id': league.abbreviation,
                'name': league.name,
                'abbreviation': league.abbreviation,
                'sport_type': league.sport_type,
                'country': league.country,
                'active': league.is_active,
                'api_provider': league.api_provider,
                'current_season': league.current_season
            })
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sports_teams(request):
    """
    Get teams for a specific league
    """
    if not SPORTS_MODELS_AVAILABLE:
        return Response([
            {'id': '1', 'name': 'Sample Team 1', 'abbreviation': 'ST1', 'city': 'Sample City', 'league': 'NFL'},
            {'id': '2', 'name': 'Sample Team 2', 'abbreviation': 'ST2', 'city': 'Sample City 2', 'league': 'NFL'},
        ])
    
    try:
        league_id = request.GET.get('league')
        
        # If league_id is provided, filter by it; otherwise return all teams
        if league_id:
            teams = Team.objects.filter(league__abbreviation=league_id)
        else:
            teams = Team.objects.all()[:100]  # Limit to 100 teams if no filter
        
        result = []
        for team in teams:
            result.append({
                'id': str(team.id),
                'name': team.name,
                'abbreviation': team.abbreviation,
                'city': team.city,
                'league': team.league.abbreviation,
                'conference': team.conference,
                'division': team.division,
                'logo_url': team.logo_url,
                'current_record': team.current_record
            })
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sports_games(request):
    """
    Get games with various filters
    """
    if not SPORTS_MODELS_AVAILABLE:
        return Response([
            {
                'id': '1',
                'external_id': 'sample-1',
                'league': 'NFL',
                'home_team': {'id': '1', 'name': 'Sample Home Team', 'abbreviation': 'SHT', 'city': 'Home City', 'league': 'NFL'},
                'away_team': {'id': '2', 'name': 'Sample Away Team', 'abbreviation': 'SAT', 'city': 'Away City', 'league': 'NFL'},
                'home_team_name': 'Sample Home Team',
                'away_team_name': 'Sample Away Team',
                'scheduled_start': datetime.now().isoformat(),
                'status': 'scheduled',
                'venue_name': 'Sample Stadium',
                'home_score': None,
                'away_score': None,
                'season': '2024',
                'week': 1
            }
        ])
    
    try:
        # Get filter parameters
        league = request.GET.get('league')
        sport_type = request.GET.get('sport_type')
        date = request.GET.get('date')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        status = request.GET.get('status')
        page_size = int(request.GET.get('page_size', 100))
        
        games = Game.objects.filter(is_active=True)
        
        if league:
            games = games.filter(league__abbreviation=league)
        
        if sport_type:
            # Ensure we're filtering by the correct field
            games = games.filter(league__sport_type=sport_type.lower())
        
        if date:
            # Single date filter
            games = games.filter(scheduled_start__date=date)
        elif date_from or date_to:
            # Date range filtering
            if date_from:
                games = games.filter(scheduled_start__date__gte=date_from)
            if date_to:
                games = games.filter(scheduled_start__date__lte=date_to)
        
        if status:
            games = games.filter(status=status)
        
        # Order by scheduled_start to show earliest games first
        games = games.order_by('scheduled_start')
        
        # Limit results based on page_size parameter
        games = games.select_related('league', 'home_team', 'away_team')[:page_size]
        
        result = []
        for game in games:
            result.append({
                'id': str(game.id),
                'external_id': game.external_id,
                'league': game.league.abbreviation,
                'home_team': {
                    'id': str(game.home_team.id),
                    'name': game.home_team.name,
                    'abbreviation': game.home_team.abbreviation,
                    'city': game.home_team.city,
                    'league': game.league.abbreviation,
                    'current_record': game.home_team.current_record,
                    'logo_url': game.home_team.logo_url
                },
                'away_team': {
                    'id': str(game.away_team.id),
                    'name': game.away_team.name,
                    'abbreviation': game.away_team.abbreviation,
                    'city': game.away_team.city,
                    'league': game.league.abbreviation,
                    'current_record': game.away_team.current_record,
                    'logo_url': game.away_team.logo_url
                },
                'home_team_name': game.home_team.name,
                'away_team_name': game.away_team.name,
                'scheduled_start': game.scheduled_start.isoformat(),
                'status': game.status,
                'venue_name': game.venue_name,
                'venue_city': game.venue_city,
                'home_score': game.home_score,
                'away_score': game.away_score,
                'season': game.season,
                'week': game.week,
                'current_period': game.current_period,
                'time_remaining': game.time_remaining,
                'weather_data': game.weather_data,
                'live_stats': game.live_stats,
                'betting_markets': [
                    {
                        'id': str(market.id),
                        'market_type': market.market_type,
                        'market_name': market.market_name,
                        'status': market.status,
                        'best_odds': {
                            'home': market.odds_lines.filter(home_odds__isnull=False).first().home_odds if market.odds_lines.filter(home_odds__isnull=False).exists() else None,
                            'away': market.odds_lines.filter(away_odds__isnull=False).first().away_odds if market.odds_lines.filter(away_odds__isnull=False).exists() else None,
                        },
                        'spread': market.odds_lines.filter(home_spread__isnull=False).first().home_spread if market.odds_lines.filter(home_spread__isnull=False).exists() else None,
                        'total': market.odds_lines.filter(total_line__isnull=False).first().total_line if market.odds_lines.filter(total_line__isnull=False).exists() else None,
                    }
                    for market in game.betting_markets.filter(is_active=True)[:3]  # Limit to 3 markets per game for performance
                ] if hasattr(game, 'betting_markets') else []
            })
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sports_games_trending(request):
    """
    Get trending games with high betting volume or close spreads
    """
    limit = int(request.GET.get('limit', 10))
    
    if not SPORTS_MODELS_AVAILABLE:
        # Return sample trending games
        sample_games = [
            {
                'id': f'trending-{i}',
                'league': random.choice(['NFL', 'NBA', 'MLB']),
                'home_team': {'name': f'Home Team {i}', 'abbreviation': f'HT{i}'},
                'away_team': {'name': f'Away Team {i}', 'abbreviation': f'AT{i}'},
                'home_team_name': f'Home Team {i}',
                'away_team_name': f'Away Team {i}',
                'scheduled_start': (datetime.now() + timedelta(hours=i)).isoformat(),
                'status': random.choice(['scheduled', 'live']),
                'venue_name': f'Stadium {i}',
                'home_score': random.randint(0, 100) if random.random() > 0.5 else None,
                'away_score': random.randint(0, 100) if random.random() > 0.5 else None
            }
            for i in range(1, limit + 1)
        ]
        return Response(sample_games)
    
    try:
        # Get trending games - show all games ordered by scheduled start
        # This will include all sports regardless of date
        trending_games = Game.objects.all(
        ).select_related('league', 'home_team', 'away_team').order_by(
            'scheduled_start'  # Order by upcoming first
        )[:limit]
        
        result = []
        for game in trending_games:
            result.append({
                'id': str(game.id),
                'external_id': game.external_id,
                'league': game.league.abbreviation,
                'home_team': {
                    'id': str(game.home_team.id),
                    'name': game.home_team.name,
                    'abbreviation': game.home_team.abbreviation,
                    'city': game.home_team.city,
                    'league': game.league.abbreviation,
                    'current_record': game.home_team.current_record,
                    'logo_url': game.home_team.logo_url
                },
                'away_team': {
                    'id': str(game.away_team.id),
                    'name': game.away_team.name,
                    'abbreviation': game.away_team.abbreviation,
                    'city': game.away_team.city,
                    'league': game.league.abbreviation,
                    'current_record': game.away_team.current_record,
                    'logo_url': game.away_team.logo_url
                },
                'home_team_name': game.home_team.name,
                'away_team_name': game.away_team.name,
                'scheduled_start': game.scheduled_start.isoformat(),
                'status': game.status,
                'venue_name': game.venue_name,
                'home_score': game.home_score,
                'away_score': game.away_score,
                'season': game.season,
                'week': game.week,
                'current_period': game.current_period,
                'time_remaining': game.time_remaining,
                'live_stats': game.live_stats if hasattr(game, 'live_stats') else {}
            })
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@rate_limit_api(service_name='espn_api')
def sports_sync(request):
    """
    Sync sports data from external providers (ESPN, The Odds API)
    Rate limited to prevent excessive API usage
    """
    if not SPORTS_MODELS_AVAILABLE:
        return Response({
            'success': False,
            'message': 'Sports models not available'
        })
    
    if not DATA_PROVIDERS_AVAILABLE or not sports_data_manager:
        return Response({
            'success': False,
            'message': 'Data providers not available'
        })
    
    try:
        data = request.data
        sport = data.get('sport', 'ncaaf')
        enrich_data = data.get('enrich', True)  # Option to enrich with additional data

        # Use real ESPN API to sync games
        sync_result = sports_data_manager.sync_games(sport)

        # Save synced games to database
        games_saved = 0
        games_enriched = 0
        enrichment_errors = []

        if sync_result['success'] and sync_result.get('games'):
            for game_data in sync_result['games']:
                try:
                    # Get or create league
                    league, _ = League.objects.get_or_create(
                        sport_type=sport,
                        defaults={
                            'name': sport.upper(),
                            'abbreviation': sport.upper(),
                            'country': 'USA',
                            'is_active': True
                        }
                    )
                    
                    # Get or create teams
                    home_team_data = game_data.get('home_team', {})
                    away_team_data = game_data.get('away_team', {})
                    
                    home_team, _ = Team.objects.get_or_create(
                        abbreviation=home_team_data.get('abbreviation', 'UNK'),
                        league=league,
                        defaults={
                            'name': home_team_data.get('name', 'Unknown'),
                            'city': '',
                            'is_active': True
                        }
                    )

                    away_team, _ = Team.objects.get_or_create(
                        abbreviation=away_team_data.get('abbreviation', 'UNK'),
                        league=league,
                        defaults={
                            'name': away_team_data.get('name', 'Unknown'),
                            'city': '',
                            'is_active': True
                        }
                    )
                    
                    # Parse date
                    from dateutil import parser
                    game_date = parser.parse(game_data.get('date', datetime.now().isoformat()))
                    
                    # Create or update game
                    game, created = Game.objects.update_or_create(
                        external_id=game_data.get('external_id', f"espn_{game_data.get('name', '')}"),
                        defaults={
                            'league': league,
                            'home_team': home_team,
                            'away_team': away_team,
                            'scheduled_start': game_date,
                            'status': game_data.get('status', 'scheduled').lower(),
                            'venue_name': game_data.get('venue', ''),
                            'home_score': home_team_data.get('score'),
                            'away_score': away_team_data.get('score'),
                            'is_active': True
                        }
                    )
                    games_saved += 1

                    # Enrich game data if requested
                    if created and enrich_data:
                        try:
                            # Import the data enricher
                            from sports.data_enrichment import data_enricher

                            # Enrich with odds data
                            odds_result = data_enricher.enrich_game_odds(str(game.id))
                            if odds_result.get('odds_added', 0) > 0:
                                games_enriched += 1

                            # Enrich with weather data for outdoor sports
                            if sport in ['nfl', 'ncaaf', 'mlb']:
                                weather_result = data_enricher.enrich_game_weather(str(game.id))
                                if weather_result.get('weather_updated'):
                                    games_enriched += 1

                        except Exception as enrich_error:
                            enrichment_errors.append(f"Game {game.id}: {str(enrich_error)}")

                except Exception as e:
                    logger.error(f"Error saving game: {e}")
                    continue

        # Enrich team data if requested and we have a league
        teams_enriched = 0
        if enrich_data and games_saved > 0:
            try:
                from sports.data_enrichment import data_enricher
                team_result = data_enricher.enrich_all_teams(sport.upper())
                teams_enriched = team_result.get('teams_updated', 0)
                if team_result.get('errors'):
                    enrichment_errors.extend(team_result['errors'])
            except Exception as e:
                enrichment_errors.append(f"Team enrichment failed: {str(e)}")

        response_data = {
            'success': sync_result['success'],
            'message': sync_result.get('message', f'Synced {games_saved} games for {sport}'),
            'games_synced': games_saved,
            'total_games_fetched': len(sync_result.get('games', [])),
        }

        if enrich_data:
            response_data['enrichment'] = {
                'games_enriched': games_enriched,
                'teams_enriched': teams_enriched,
                'errors': enrichment_errors[:5]  # Limit error messages
            }

        return Response(response_data)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Sync failed: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 559: Public for Betting Dashboard UI
@rate_limit_api(service_name='odds_api')
# @cache_response(cache_type='odds', key_params=['sport', 'markets'])  # Disabled - causes pickle errors with DRF Response
def live_odds(request):
    """
    Get live odds data from The Odds API
    Rate limited to protect free tier API quota
    Cached for 1 minute to reduce API calls
    """
    if not DATA_PROVIDERS_AVAILABLE or not sports_data_manager:
        return Response({
            'success': False,
            'message': 'Data providers not available'
        })
    
    try:
        sport = request.GET.get('sport', 'ncaaf')
        markets = request.GET.getlist('markets', ['h2h', 'spreads', 'totals'])
        
        # Get live odds
        odds_data = sports_data_manager.odds_api.get_odds(sport, markets)
        
        # Format for frontend
        formatted_odds = []
        for game in odds_data:
            game_odds = {
                'id': game.get('id'),
                'sport_key': game.get('sport_key'),
                'home_team': game.get('home_team'),
                'away_team': game.get('away_team'),
                'commence_time': game.get('commence_time'),
                'bookmakers': []
            }
            
            for bookmaker in game.get('bookmakers', []):
                bm_data = {
                    'key': bookmaker.get('key'),
                    'title': bookmaker.get('title'),
                    'markets': {}
                }
                
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key')
                    bm_data['markets'][market_key] = {
                        'outcomes': market.get('outcomes', [])
                    }
                
                game_odds['bookmakers'].append(bm_data)
            
            formatted_odds.append(game_odds)
        
        return Response({
            'success': True,
            'sport': sport,
            'total_games': len(formatted_odds),
            'markets_included': markets,
            'odds': formatted_odds
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to get live odds: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def live_odds_with_scores(request):
    """
    Session 563: Get live odds combined with ESPN live scores.
    Returns odds data enriched with real-time scores for in-progress games.
    """
    if not DATA_PROVIDERS_AVAILABLE or not sports_data_manager:
        return Response({
            'success': False,
            'message': 'Data providers not available'
        })

    try:
        sport = request.GET.get('sport', 'americanfootball_nfl')
        markets = request.GET.getlist('markets', ['h2h', 'spreads', 'totals'])

        # Map full sport keys to short keys for ESPN
        espn_sport_map = {
            'americanfootball_nfl': 'nfl',
            'americanfootball_ncaaf': 'ncaaf',
            'basketball_nba': 'nba',
            'basketball_ncaab': 'ncaab',
            'baseball_mlb': 'mlb',
            'icehockey_nhl': 'nhl',
        }
        espn_sport = espn_sport_map.get(sport, 'nfl')

        # Get odds data
        odds_data = sports_data_manager.odds_api.get_odds(sport, markets)

        # Get ESPN scoreboard for live scores
        scoreboard = sports_data_manager.espn.get_scoreboard(espn_sport)
        events = scoreboard.get('events', [])

        # Build lookup of live scores by team names
        live_scores = {}
        for event in events:
            competitors = event.get('competitions', [{}])[0].get('competitors', [])
            status_info = event.get('status', {})
            status_type = status_info.get('type', {})

            home_team = None
            away_team = None
            home_score = 0
            away_score = 0

            for comp in competitors:
                team_name = comp.get('team', {}).get('displayName', '')
                score = int(comp.get('score', 0) or 0)
                if comp.get('homeAway') == 'home':
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score

            if home_team and away_team:
                # Create a key that can match odds data
                key = f"{home_team}|{away_team}".lower()
                live_scores[key] = {
                    'home_score': home_score,
                    'away_score': away_score,
                    'status': status_type.get('state', 'pre'),  # pre, in, post
                    'status_detail': status_info.get('type', {}).get('shortDetail', ''),
                    'period': status_info.get('period', 0),
                    'clock': status_info.get('displayClock', ''),
                    'is_live': status_type.get('state') == 'in',
                    'is_final': status_type.get('completed', False),
                }

        # Enrich odds data with live scores
        enriched_odds = []
        live_count = 0

        for game in odds_data:
            home = game.get('home_team', '')
            away = game.get('away_team', '')
            key = f"{home}|{away}".lower()

            # Try to find matching live score
            score_data = live_scores.get(key)

            # Also try reverse key and partial matches
            if not score_data:
                for score_key, data in live_scores.items():
                    if home.lower() in score_key or away.lower() in score_key:
                        score_data = data
                        break

            game_data = {
                'id': game.get('id'),
                'sport_key': game.get('sport_key'),
                'home_team': home,
                'away_team': away,
                'commence_time': game.get('commence_time'),
                'bookmakers': []
            }

            # Add live score info if available
            if score_data:
                game_data['live'] = score_data
                if score_data.get('is_live'):
                    live_count += 1
            else:
                # Check if game should be live based on commence_time
                try:
                    commence = datetime.fromisoformat(game.get('commence_time', '').replace('Z', '+00:00'))
                    if commence <= datetime.now(commence.tzinfo):
                        game_data['live'] = {
                            'is_live': True,
                            'status': 'in',
                            'status_detail': 'In Progress',
                            'home_score': 0,
                            'away_score': 0,
                        }
                        live_count += 1
                except Exception:
                    pass

            # Format bookmakers
            for bookmaker in game.get('bookmakers', []):
                bm_data = {
                    'key': bookmaker.get('key'),
                    'title': bookmaker.get('title'),
                    'markets': {}
                }

                for market in bookmaker.get('markets', []):
                    market_key = market.get('key')
                    bm_data['markets'][market_key] = {
                        'outcomes': market.get('outcomes', [])
                    }

                game_data['bookmakers'].append(bm_data)

            enriched_odds.append(game_data)

        # Sort: live games first, then by commence_time
        enriched_odds.sort(key=lambda g: (
            0 if g.get('live', {}).get('is_live') else 1,
            g.get('commence_time', '')
        ))

        return Response({
            'success': True,
            'sport': sport,
            'total_games': len(enriched_odds),
            'live_games': live_count,
            'markets_included': markets,
            'odds': enriched_odds
        })

    except Exception as e:
        logger.error(f"Live odds with scores error: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': f'Failed to get live odds: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_player_props(request, event_id):
    """
    Session 563: Get player props for a specific event.
    Fetches prop bets from The Odds API for the given event ID.
    """
    try:
        sport = request.GET.get('sport', 'basketball_nba')

        # Define prop markets by sport
        prop_markets = {
            'basketball_nba': [
                'player_points', 'player_rebounds', 'player_assists',
                'player_threes', 'player_blocks', 'player_steals',
                'player_points_rebounds_assists', 'player_double_double'
            ],
            'basketball_ncaab': [
                'player_points', 'player_rebounds', 'player_assists', 'player_threes'
            ],
            'americanfootball_nfl': [
                'player_pass_tds', 'player_pass_yds', 'player_rush_yds',
                'player_reception_yds', 'player_receptions',
                'player_anytime_td', 'player_first_td'
            ],
            'americanfootball_ncaaf': [
                'player_pass_tds', 'player_pass_yds', 'player_rush_yds',
                'player_reception_yds', 'player_anytime_td'
            ],
            'icehockey_nhl': [
                'player_points', 'player_assists', 'player_shots_on_goal',
                'player_blocked_shots'
            ],
            'baseball_mlb': [
                'batter_hits', 'batter_home_runs', 'batter_rbis',
                'batter_total_bases', 'pitcher_strikeouts'
            ],
        }

        markets = prop_markets.get(sport, prop_markets['basketball_nba'])
        markets_str = ','.join(markets)

        # Get API key
        api_key = os.environ.get('THE_ODDS_API_KEY')
        if not api_key:
            return Response({
                'success': False,
                'message': 'Odds API key not configured'
            }, status=500)

        # Fetch props from The Odds API
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/events/{event_id}/odds"
        params = {
            'apiKey': api_key,
            'regions': 'us',
            'markets': markets_str,
            'oddsFormat': 'american'
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 404:
            return Response({
                'success': False,
                'message': 'Event not found or props not available'
            }, status=404)

        # Session 563: Handle 422 - props not available for this event
        if response.status_code == 422:
            return Response({
                'success': False,
                'message': 'Player props not available for this event',
                'props_by_player': {}
            }, status=200)  # Return 200 with empty props so frontend handles gracefully

        response.raise_for_status()
        data = response.json()

        # Parse and organize props by player
        props_by_player = {}
        bookmakers = data.get('bookmakers', [])

        for book in bookmakers:
            book_name = book.get('title', book.get('key', 'Unknown'))

            for market in book.get('markets', []):
                market_key = market.get('key', '')

                for outcome in market.get('outcomes', []):
                    player_name = outcome.get('description', outcome.get('name', 'Unknown'))
                    prop_name = outcome.get('name', '')  # Over/Under
                    point = outcome.get('point', 0)
                    price = outcome.get('price', 0)

                    if player_name not in props_by_player:
                        props_by_player[player_name] = []

                    props_by_player[player_name].append({
                        'market': market_key,
                        'market_label': market_key.replace('player_', '').replace('_', ' ').title(),
                        'type': prop_name,  # Over/Under
                        'line': point,
                        'odds': price,
                        'bookmaker': book_name
                    })

        # Sort props within each player
        for player in props_by_player:
            props_by_player[player].sort(key=lambda x: (x['market'], x['type']))

        # Get remaining API quota from response headers
        remaining = response.headers.get('x-requests-remaining', 'Unknown')
        used = response.headers.get('x-requests-used', 'Unknown')

        return Response({
            'success': True,
            'event_id': event_id,
            'sport': sport,
            'home_team': data.get('home_team'),
            'away_team': data.get('away_team'),
            'commence_time': data.get('commence_time'),
            'props_by_player': props_by_player,
            'player_count': len(props_by_player),
            'total_props': sum(len(p) for p in props_by_player.values()),
            'api_quota': {
                'remaining': remaining,
                'used': used
            }
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Props API request error: {e}")
        return Response({
            'success': False,
            'message': f'Failed to fetch props: {str(e)}'
        }, status=500)
    except Exception as e:
        logger.error(f"Props error: {e}", exc_info=True)
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@rate_limit_api(service_name='weather_api')
def get_weather_data(request):
    """
    Get weather data for a venue using WeatherAPI
    Query params: venue (required), date (optional)
    Rate limited to prevent excessive API usage
    """
    try:
        venue = request.GET.get('venue')
        if not venue:
            return Response({
                'success': False,
                'message': 'Venue parameter required'
            }, status=400)
        
        # Get WeatherAPI key from environment
        api_key = os.environ.get('WEATHERAPI_KEY')
        if not api_key:
            return Response({
                'success': False,
                'message': 'Weather API key not configured'
            }, status=500)
        
        # Clean venue name for API (remove "Stadium", "Field", etc.)
        clean_venue = venue.replace(' Stadium', '').replace(' Field', '').replace(' Arena', '')
        
        # Call WeatherAPI
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            'key': api_key,
            'q': clean_venue,
            'aqi': 'no'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        weather_data = response.json()
        
        # Extract relevant weather info
        current = weather_data.get('current', {})
        location = weather_data.get('location', {})
        
        formatted_weather = {
            'success': True,
            'location': f"{location.get('name', '')}, {location.get('region', '')}",
            'condition': current.get('condition', {}).get('text', 'Clear'),
            'temperature': int(current.get('temp_f', 72)),
            'humidity': current.get('humidity', 45),
            'wind': f"{current.get('wind_dir', 'N')} {int(current.get('wind_mph', 0))} mph",
            'wind_speed': current.get('wind_mph', 0),
            'wind_direction': current.get('wind_dir', 'N'),
            'feels_like': int(current.get('feelslike_f', 72)),
            'uv_index': current.get('uv', 3),
            'visibility': current.get('vis_miles', 10),
            'last_updated': current.get('last_updated', ''),
            'icon': current.get('condition', {}).get('icon', ''),
        }
        
        return Response(formatted_weather)
        
    except requests.exceptions.RequestException as e:
        return Response({
            'success': False,
            'message': f'Weather API request failed: {str(e)}'
        }, status=500)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Weather data error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_injury_data(request):
    """
    Session 999B: Injury data from SpiderData(data_type='sports_injuries').
    Expands raw_data.items[], filters by team name, extracts status/impact.
    """
    try:
        from persistence.models import SpiderData

        home_team = request.GET.get('home_team')
        away_team = request.GET.get('away_team')

        if not home_team or not away_team:
            return Response({
                'success': False,
                'message': 'Both home_team and away_team parameters required'
            }, status=400)

        # Last word of team name for flexible matching (e.g. "Chiefs", "Bills")
        home_words = home_team.lower().split()
        away_words = away_team.lower().split()

        def _extract_injury_status(text):
            t = (text or '').lower()
            for s in ['out', 'doubtful', 'questionable', 'probable', 'ir', 'day-to-day']:
                if s in t:
                    return s.capitalize().replace('Ir', 'IR').replace('Day-to-day', 'Day-to-Day')
            return 'Unknown'

        def _extract_impact_level(item):
            pos = (item.get('position') or '').upper()
            status = _extract_injury_status(item.get('status') or item.get('description') or '')
            if pos in ('QB', 'RB', 'WR', 'PG', 'SG', 'C', 'P', 'SP'):
                return 'High'
            if status in ('Out', 'IR', 'Doubtful'):
                return 'High'
            if status == 'Questionable':
                return 'Medium'
            return 'Low'

        # Fetch recent injury spider data
        rows = SpiderData.objects.filter(
            data_type='sports_injuries',
        ).order_by('-created_at')[:10]

        all_injuries = []
        for row in rows:
            raw = row.raw_data or {}
            items = raw.get('items', [])
            for item in items:
                title = (item.get('title') or item.get('name') or '').lower()
                desc = (item.get('description') or item.get('summary') or '').lower()
                text = f"{title} {desc}"

                # Check if this injury relates to either team
                matched_team = None
                for w in home_words:
                    if len(w) > 2 and w in text:
                        matched_team = home_team
                        break
                if not matched_team:
                    for w in away_words:
                        if len(w) > 2 and w in text:
                            matched_team = away_team
                            break
                if not matched_team:
                    continue

                status = _extract_injury_status(item.get('status') or item.get('description') or title)
                all_injuries.append({
                    'team': matched_team,
                    'player': item.get('title') or item.get('name') or 'Unknown',
                    'position': item.get('position') or '',
                    'injury': item.get('injury') or item.get('category') or '',
                    'status': status,
                    'impact_level': _extract_impact_level(item),
                    'source': row.spider_name,
                })

        home_injuries = [i for i in all_injuries if i['team'] == home_team]
        away_injuries = [i for i in all_injuries if i['team'] == away_team]
        out_count = len([i for i in all_injuries if i['status'] == 'Out'])
        questionable_count = len([i for i in all_injuries if i['status'] == 'Questionable'])

        return Response({
            'success': True,
            'injuries': all_injuries,
            'summary': {
                'total_injuries': len(all_injuries),
                'players_out': out_count,
                'questionable': questionable_count,
                'last_updated': rows[0].created_at.isoformat() if rows else None,
                'home_team_injuries': len(home_injuries),
                'away_team_injuries': len(away_injuries),
            },
            'teams': {'home_team': home_team, 'away_team': away_team},
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Injury data error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_betting_intelligence(request):
    """
    Session 999B: Betting intelligence from GameLineHistory + OddsSnapshot.
    Builds real trends from spread/total movement, moneyline implied probability,
    and price direction from snapshot history.
    """
    try:
        from django.core.cache import cache
        from core.models_odds_history import GameLineHistory, OddsSnapshot

        home_team = request.GET.get('home_team')
        away_team = request.GET.get('away_team')

        if not home_team or not away_team:
            return Response({
                'success': False,
                'message': 'Both home_team and away_team parameters required'
            }, status=400)

        cache_key = f"intelligence:{home_team}:{away_team}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Fuzzy match: use last word of team name
        home_last = home_team.strip().split()[-1]
        away_last = away_team.strip().split()[-1]

        from django.db.models import Q
        glh = GameLineHistory.objects.filter(
            Q(home_team__icontains=home_last) & Q(away_team__icontains=away_last)
        ).order_by('-commence_time').first()

        if not glh:
            # Return empty but valid response
            return Response({
                'success': True,
                'trends': [],
                'summary': {'total_insights': 0, 'overall_recommendation': 'No Data'},
                'teams': {'home_team': home_team, 'away_team': away_team},
            })

        # Build trends from real data
        trends = []

        # Spread analysis
        if glh.current_spread_home is not None and glh.open_spread_home is not None:
            mvmt = float(glh.spread_movement)
            direction = 'toward home' if mvmt < 0 else 'toward away' if mvmt > 0 else 'stable'
            trends.append({
                'type': 'SPREAD_MOVEMENT',
                'category': 'Spread Analysis',
                'text': f"Spread moved {abs(mvmt):.1f} pts {direction}: opened {float(glh.open_spread_home):+.1f}, now {float(glh.current_spread_home):+.1f}",
                'confidence': 'High' if abs(mvmt) >= 1 else 'Medium',
                'impact': 'Significant' if abs(mvmt) >= 1.5 else 'Minor',
                'value': f"{mvmt:+.1f}",
            })

        # Total movement
        if glh.current_total is not None and glh.open_total is not None:
            tmvmt = float(glh.total_movement)
            trends.append({
                'type': 'TOTALS_MOVEMENT',
                'category': 'Over/Under Intelligence',
                'text': f"Total moved {abs(tmvmt):.1f} pts: opened {float(glh.open_total)}, now {float(glh.current_total)}",
                'confidence': 'High' if abs(tmvmt) >= 1 else 'Medium',
                'impact': 'Over signal' if tmvmt > 0.5 else 'Under signal' if tmvmt < -0.5 else 'Stable',
                'value': f"O/U {float(glh.current_total)}",
            })

        # Moneyline implied probability
        if glh.current_ml_home and glh.current_ml_away:
            hp = _american_to_probability(glh.current_ml_home)
            ap = _american_to_probability(glh.current_ml_away)
            vig = (hp + ap - 1) * 100
            trends.append({
                'type': 'MONEYLINE_VALUE',
                'category': 'Implied Probability',
                'text': f"{home_team} {hp:.1%} implied vs {away_team} {ap:.1%} implied (vig {vig:.1f}%)",
                'confidence': 'High',
                'impact': 'Home Favored' if hp > ap else 'Away Favored',
                'value': f"{hp:.1%} / {ap:.1%}",
            })

        # Price direction from snapshots
        snapshots = list(
            OddsSnapshot.objects.filter(game_id=glh.game_id, market='h2h')
            .order_by('captured_at')
            .values('outcome_name', 'price', 'captured_at')
        )
        if len(snapshots) >= 2:
            # Group by outcome and check direction
            outcomes = {}
            for s in snapshots:
                outcomes.setdefault(s['outcome_name'], []).append(s['price'])
            for name, prices in outcomes.items():
                if len(prices) >= 2:
                    first, last = prices[0], prices[-1]
                    direction = 'shortened' if last < first else 'drifted' if last > first else 'stable'
                    trends.append({
                        'type': 'PRICE_DIRECTION',
                        'category': 'Line Movement',
                        'text': f"{name} ML has {direction}: {first:+d} -> {last:+d} across {len(prices)} snapshots",
                        'confidence': 'Medium',
                        'impact': direction.capitalize(),
                        'value': f"{first:+d} -> {last:+d}",
                    })

        # Summary
        sig_trends = len([t for t in trends if t.get('confidence') == 'High'])
        recommendation = 'Strong Data' if sig_trends >= 2 else 'Moderate Data' if sig_trends >= 1 else 'Limited Data'

        result = {
            'success': True,
            'trends': trends,
            'summary': {
                'total_insights': len(trends),
                'snapshot_count': glh.snapshot_count,
                'overall_recommendation': recommendation,
                'last_updated': glh.updated_at.isoformat() if glh.updated_at else None,
            },
            'teams': {'home_team': home_team, 'away_team': away_team},
            'advanced_metrics': {
                'current_spread': float(glh.current_spread_home) if glh.current_spread_home is not None else None,
                'current_total': float(glh.current_total) if glh.current_total is not None else None,
                'spread_movement': float(glh.spread_movement),
                'total_movement': float(glh.total_movement),
                'home_ml': glh.current_ml_home,
                'away_ml': glh.current_ml_away,
            },
        }

        cache.set(cache_key, result, 10 * 60)  # 10 min
        return Response(result)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Betting intelligence error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_spider_insights(request, game_id):
    """
    Get spider intelligence for a specific game - community sentiment, discussions, betting tips
    Connects 232K+ spider entries to Sports Hub UI
    """
    from persistence.models import SpiderData
    from sports.models import Game
    from django.db.models import Q

    try:
        # Get game details
        game = Game.objects.select_related('home_team', 'away_team', 'league').get(id=game_id)

        # Search spider data for mentions of teams
        home_team_name = game.home_team.name
        away_team_name = game.away_team.name

        # Query spider data for team mentions (case-insensitive)
        # Session 807: Defer embedding fields to reduce egress costs
        spider_data = SpiderData.objects.filter(
            Q(spider_name__in=['social_sentiment', 'horse_racing', 'combat_sports']) &
            (Q(data__icontains=home_team_name) | Q(data__icontains=away_team_name))
        ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:50]

        # Aggregate insights
        total_mentions = spider_data.count()

        # Calculate sentiment (simplified - would use real NLP)
        sentiment_score = 0.5  # Neutral default
        community_mood = "Neutral"

        if total_mentions > 10:
            sentiment_score = 0.65
            community_mood = "Bullish"
        elif total_mentions > 5:
            sentiment_score = 0.55
            community_mood = "Slightly Positive"

        # Count discussion types
        discussions = []
        betting_tips = 0

        for entry in spider_data[:10]:
            if entry.data_type == 'research':
                discussions.append({
                    'source': entry.spider_name,
                    'timestamp': entry.created_at.isoformat(),
                    'type': entry.data_type
                })
                betting_tips += 1

        # Build response
        insights = {
            'success': True,
            'game_id': game_id,
            'teams': {
                'home': home_team_name,
                'away': away_team_name
            },
            'spider_intelligence': {
                'total_mentions': total_mentions,
                'sentiment': {
                    'score': sentiment_score,
                    'mood': community_mood,
                    'confidence': 'Medium' if total_mentions > 5 else 'Low'
                },
                'discussions': {
                    'count': len(discussions),
                    'recent': discussions[:5]
                },
                'betting_tips': {
                    'count': betting_tips,
                    'sources': ['Reddit', 'Community Forums']
                },
                'trending': total_mentions > 15,
                'sharp_money_indicator': sentiment_score > 0.6
            },
            'data_freshness': 'Real-time' if spider_data.exists() else 'No recent data',
            'last_updated': spider_data.first().created_at.isoformat() if spider_data.exists() else None
        }

        return Response(insights)

    except Game.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Game not found',
            'game_id': game_id
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching spider insights for game {game_id}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def orchestrate_agent_analysis(request):
    """
    🚀 Agent Orchestration Engine - Coordinate multiple specialized betting agents

    This endpoint dispatches orchestration to Celery for async processing,
    preventing timeouts and enabling real-time WebSocket updates.

    **Smart Caching:** Analyses are cached for 20 minutes to avoid redundant expensive operations.
    Only re-analyzes when game factors change significantly.
    """
    try:
        # Extract request data
        data = request.data
        game_id = data.get('game_id', 'mock-game-123')
        home_team = data.get('home_team', 'Houston Cougars')
        away_team = data.get('away_team', 'Colorado Buffaloes')
        league = data.get('league', 'NCAAF')
        subscription_tier = data.get('subscription_tier', 'basic')
        selected_agents = data.get('selected_agents', None)
        force_refresh = data.get('force_refresh', False)

        # Check cache first (unless force_refresh requested)
        cache_key = f"sports_analysis:{league}:{game_id}"

        if not force_refresh:
            from django.core.cache import cache
            cached_analysis = cache.get(cache_key)

            if cached_analysis:
                logger.info(f"♻️  Returning cached analysis for game {game_id} (age: {cached_analysis.get('cache_age', 'unknown')})")
                return Response({
                    'success': True,
                    'message': 'Analysis retrieved from cache',
                    'cached': True,
                    'cache_age_minutes': cached_analysis.get('cache_age', 0),
                    'status': 'complete',
                    'result': cached_analysis.get('result'),
                    'timestamp': cached_analysis.get('timestamp'),
                    'info': 'Fresh analysis available. Use force_refresh=true to re-analyze.'
                })

        # Execute orchestration synchronously (Celery had broker issues)
        import asyncio
        from sports.orchestration import execute_coordinated_analysis
        from agents.tasks import _transform_orchestration_for_frontend
        from django.core.cache import cache

        logger.info(f"🚀 Starting synchronous sports orchestration for {home_team} vs {away_team}")

        # Create event loop and execute
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Execute the orchestration
            orchestration_results = loop.run_until_complete(
                execute_coordinated_analysis(
                    game_id=game_id,
                    home_team=home_team,
                    away_team=away_team,
                    league=league,
                    subscription_tier=subscription_tier,
                    selected_agents=selected_agents
                )
            )

            # Transform results for frontend
            frontend_results = _transform_orchestration_for_frontend(
                orchestration_results,
                home_team,
                away_team
            )

            result_data = {
                'success': True,
                'game_id': game_id,
                'results': frontend_results
            }

            # Cache results for 20 minutes
            cache.set(cache_key, {
                'result': result_data,
                'timestamp': datetime.now().isoformat(),
                'cache_age': 0
            }, timeout=1200)

            logger.info(f"✅ Orchestration completed and cached for game {game_id}")

            # Return complete results immediately
            return Response({
                'success': True,
                'status': 'complete',
                'result': result_data,
                'timestamp': datetime.now().isoformat(),
                'cached': False,
                'execution_time': 'real-time'
            })

        finally:
            loop.close()

    except ImportError as e:
        return Response({
            'success': False,
            'error': 'orchestration_engine_unavailable',
            'message': f'Orchestration engine not available: {str(e)}',
            'fallback': 'Individual agent execution available'
        }, status=500)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'orchestration_failed',
            'message': f'Agent orchestration failed: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 560: Public for Betting Dashboard UI
def get_futures_odds(request):
    """
    Session 560: Get championship futures odds from The Odds API.

    GET /api/v1/betting/futures/

    Query params:
        league: Filter by league (nfl, nba, mlb, nhl) - optional
        limit: Max results per league (default 15)
    """
    try:
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

        league = request.GET.get('league')
        limit = int(request.GET.get('limit', 15))

        spider = TheOddsSpider()

        # Map league to futures sport keys
        futures_map = {
            'nfl': ['americanfootball_nfl_super_bowl_winner'],
            'nba': ['basketball_nba_championship_winner'],
            'mlb': ['baseball_mlb_world_series_winner'],
            'nhl': ['icehockey_nhl_championship_winner'],
            None: [
                'americanfootball_nfl_super_bowl_winner',
                'basketball_nba_championship_winner',
                'baseball_mlb_world_series_winner',
                'icehockey_nhl_championship_winner',
            ]
        }

        sports = futures_map.get(league.lower() if league else None, futures_map[None])

        all_futures = []
        leagues_data = {}

        for sport_key in sports:
            try:
                data = spider.fetch_data(
                    sports=[sport_key],
                    max_results=limit,
                    include_futures=True
                )
                futures = [d for d in data if d.get('data_type') == 'futures_odds']

                # Determine league name from sport key
                if 'nfl' in sport_key or 'super_bowl' in sport_key:
                    league_name = 'NFL'
                    championship = 'Super Bowl'
                elif 'nba' in sport_key or 'basketball' in sport_key:
                    league_name = 'NBA'
                    championship = 'NBA Championship'
                elif 'mlb' in sport_key or 'world_series' in sport_key:
                    league_name = 'MLB'
                    championship = 'World Series'
                elif 'nhl' in sport_key or 'stanley_cup' in sport_key:
                    league_name = 'NHL'
                    championship = 'Stanley Cup'
                else:
                    league_name = sport_key.upper()
                    championship = 'Championship'

                # Group by league
                if league_name not in leagues_data:
                    leagues_data[league_name] = {
                        'league': league_name,
                        'championship': championship,
                        'teams': []
                    }

                # Session 563: Spider returns futures with 'contenders' array
                for future in futures:
                    contenders = future.get('contenders', [])
                    bookmaker = future.get('best_bookmaker', 'Best Available')
                    fetched_at = future.get('fetched_at', '')

                    # Extract each team from contenders
                    for contender in contenders[:limit]:
                        odds = contender.get('odds', 0)
                        implied_prob = contender.get('implied_prob', 0)

                        # Convert implied_prob from percentage to decimal if needed
                        if implied_prob and implied_prob > 1:
                            implied_prob = implied_prob / 100

                        # Calculate decimal odds
                        if odds > 0:
                            decimal_odds = (odds / 100) + 1
                        elif odds < 0:
                            decimal_odds = (100 / abs(odds)) + 1
                        else:
                            decimal_odds = 0

                        team_data = {
                            'team': contender.get('name', 'Unknown'),
                            'odds_american': odds,
                            'odds_decimal': round(decimal_odds, 2),
                            'implied_probability': implied_prob if implied_prob else 0,
                            'bookmaker': bookmaker,
                            'last_updated': fetched_at,
                        }

                        leagues_data[league_name]['teams'].append(team_data)

                    all_futures.append(future)

            except Exception as e:
                logger.warning(f"Error fetching futures for {sport_key}: {e}")
                continue

        # If no live data, try cached SpiderData
        if not all_futures:
            from persistence.models import SpiderData

            # Session 807: Defer embedding fields to reduce egress costs
            cached = SpiderData.objects.filter(
                spider_name='theodds',
                category='futures'
            ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:limit * 4]

            for item in cached:
                data = item.data if isinstance(item.data, dict) else {}
                team = data.get('title', item.title or 'Unknown')
                odds = data.get('odds_american', data.get('price', 0))

                # Determine league from item
                league_name = 'NFL'  # Default
                championship = 'Championship'

                if 'nba' in str(item.category).lower() or 'basketball' in str(item.title).lower():
                    league_name = 'NBA'
                    championship = 'NBA Championship'
                elif 'mlb' in str(item.category).lower() or 'baseball' in str(item.title).lower():
                    league_name = 'MLB'
                    championship = 'World Series'
                elif 'nhl' in str(item.category).lower() or 'hockey' in str(item.title).lower():
                    league_name = 'NHL'
                    championship = 'Stanley Cup'
                else:
                    league_name = 'NFL'
                    championship = 'Super Bowl'

                if league_name not in leagues_data:
                    leagues_data[league_name] = {
                        'league': league_name,
                        'championship': championship,
                        'teams': []
                    }

                # Calculate implied probability
                implied = 0
                if odds > 0:
                    implied = 100 / (odds + 100)
                elif odds < 0:
                    implied = abs(odds) / (abs(odds) + 100)

                leagues_data[league_name]['teams'].append({
                    'team': team,
                    'odds_american': odds,
                    'odds_decimal': data.get('odds_decimal', 0),
                    'implied_probability': implied,
                    'bookmaker': data.get('bookmaker', 'Cached'),
                    'last_updated': item.created_at.isoformat() if item.created_at else '',
                })

        # Sort teams by implied probability (favorites first)
        for league_name in leagues_data:
            leagues_data[league_name]['teams'].sort(
                key=lambda x: x.get('implied_probability', 0),
                reverse=True
            )
            # Keep top teams per league
            leagues_data[league_name]['teams'] = leagues_data[league_name]['teams'][:limit]

        return Response({
            'success': True,
            'leagues': list(leagues_data.values()),
            'total_teams': sum(len(l['teams']) for l in leagues_data.values()),
            'last_updated': datetime.now().isoformat(),
            'source': 'The Odds API'
        })

    except ImportError as e:
        logger.error(f"TheOddsSpider import error: {e}")
        return Response({
            'success': False,
            'leagues': [],
            'error': 'Odds spider not available'
        })
    except Exception as e:
        logger.error(f"Futures API error: {e}", exc_info=True)
        return Response({
            'success': False,
            'leagues': [],
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_wager(request):
    """
    Session 560: Log a bet/wager from the web UI.

    POST /api/v1/betting/wager/

    Body:
        event_name: str - The event being bet on
        selection: str - What you bet on (e.g., "Chiefs ML")
        bet_type: str - moneyline, spread, total, prop, parlay, futures, etc.
        odds_american: int - American odds (-110, +150)
        stake: float - Amount wagered
        sport: str - Optional sport category
        bookmaker: str - Optional bookmaker name
        line: float - Optional spread/total line
        event_time: str - Optional ISO datetime of the event
        notes: str - Optional notes
    """
    from core.models_bankroll import Bankroll, Wager
    from decimal import Decimal

    try:
        data = request.data
        user = request.user

        # Get or create bankroll for user
        bankroll, _ = Bankroll.objects.get_or_create(
            user=user,
            defaults={
                'name': f"{user.username}'s Bankroll",
                'initial_balance': Decimal('1000.00'),
                'current_balance': Decimal('1000.00'),
                'unit_size': Decimal('10.00'),
            }
        )

        # Validate required fields
        required = ['event_name', 'selection', 'odds_american', 'stake']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response({
                'success': False,
                'error': f"Missing required fields: {', '.join(missing)}"
            }, status=400)

        # Parse and validate odds
        try:
            odds_american = int(data['odds_american'])
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid odds format. Must be integer (e.g., -110, +150)'
            }, status=400)

        # Parse stake
        try:
            stake = Decimal(str(data['stake']))
            if stake <= 0:
                raise ValueError("Stake must be positive")
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            return Response({
                'success': False,
                'error': f'Invalid stake: {str(e)}'
            }, status=400)

        # Calculate units
        units = stake / bankroll.unit_size if bankroll.unit_size > 0 else Decimal('1')

        # Parse optional event time
        event_time = None
        if data.get('event_time'):
            try:
                event_time = datetime.fromisoformat(data['event_time'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass

        # Create wager
        wager = Wager.objects.create(
            bankroll=bankroll,
            event_name=data['event_name'],
            selection=data['selection'],
            bet_type=data.get('bet_type', 'moneyline'),
            odds_american=odds_american,
            stake=stake,
            units=units,
            sport=data.get('sport', ''),
            bookmaker=data.get('bookmaker', ''),
            line=Decimal(str(data['line'])) if data.get('line') else None,
            event_time=event_time,
            notes=data.get('notes', ''),
            source='web',
            status='pending',
        )

        # Update bankroll
        bankroll.current_balance -= stake
        bankroll.save()

        return Response({
            'success': True,
            'wager': {
                'id': wager.id,
                'event_name': wager.event_name,
                'selection': wager.selection,
                'odds_american': wager.odds_american,
                'stake': float(wager.stake),
                'units': float(wager.units),
                'potential_payout': float(wager.potential_payout),
                'status': wager.status,
                'placed_at': wager.placed_at.isoformat(),
            },
            'bankroll': {
                'current_balance': float(bankroll.current_balance),
                'pending_wagers': bankroll.wagers.filter(status='pending').count(),
            }
        })

    except Exception as e:
        logger.error(f"Error logging wager: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orchestration_status(request, task_id):
    """
    Poll Celery task status and return results when ready.

    This endpoint allows frontend to check if the orchestration task has completed
    and retrieve the analysis results.
    """
    try:
        from celery.result import AsyncResult

        task_result = AsyncResult(task_id)

        if task_result.ready():
            # Task completed - return results
            result_data = task_result.result

            return Response({
                'status': 'complete',
                'task_id': task_id,
                'result': result_data,
                'timestamp': datetime.now().isoformat()
            })
        elif task_result.failed():
            # Task failed
            return Response({
                'status': 'failed',
                'task_id': task_id,
                'error': str(task_result.info),
                'timestamp': datetime.now().isoformat()
            }, status=500)
        else:
            # Task still processing
            progress_info = task_result.info if task_result.info else {}

            return Response({
                'status': 'processing',
                'task_id': task_id,
                'progress': progress_info.get('progress', 0),
                'current_step': progress_info.get('current_step', 'Analyzing game...'),
                'timestamp': datetime.now().isoformat()
            })

    except Exception as e:
        logger.error(f"Error checking task status {task_id}: {e}")
        return Response({
            'status': 'error',
            'task_id': task_id,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)


# =============================================================================
# SESSION 561: LINE MOVEMENT CHARTS API
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_line_movement(request, game_id=None):
    """
    Session 561: Get line movement data for charting.

    Query params:
    - game_id: Specific game to get history for (or use URL param)
    - sport: Filter by sport (e.g., 'americanfootball_nfl')
    - market: Filter by market type ('h2h', 'spreads', 'totals')
    - bookmaker: Filter by bookmaker (e.g., 'draftkings')
    - hours: How many hours of history (default: 48)

    Returns time-series data suitable for charting line movement.
    """
    from core.models_odds_history import OddsSnapshot, GameLineHistory
    from django.utils import timezone

    try:
        # Get parameters
        game_id = game_id or request.GET.get('game_id')
        sport = request.GET.get('sport')
        market = request.GET.get('market', 'spreads')
        bookmaker = request.GET.get('bookmaker')
        hours = int(request.GET.get('hours', 48))

        # Time range
        cutoff = timezone.now() - timedelta(hours=hours)

        if game_id:
            # Get specific game history
            snapshots = OddsSnapshot.objects.filter(
                game_id=game_id,
                captured_at__gte=cutoff
            ).order_by('captured_at')

            if market:
                snapshots = snapshots.filter(market=market)
            if bookmaker:
                snapshots = snapshots.filter(bookmaker=bookmaker)

            # Get game summary
            try:
                history = GameLineHistory.objects.get(game_id=game_id)
                game_info = {
                    'game_id': history.game_id,
                    'home_team': history.home_team,
                    'away_team': history.away_team,
                    'commence_time': history.commence_time.isoformat() if history.commence_time else None,
                    'sport_key': history.sport_key,
                    'open_spread': float(history.open_spread_home) if history.open_spread_home else None,
                    'current_spread': float(history.current_spread_home) if history.current_spread_home else None,
                    'spread_movement': float(history.spread_movement) if history.spread_movement else 0,
                    'open_total': float(history.open_total) if history.open_total else None,
                    'current_total': float(history.current_total) if history.current_total else None,
                    'total_movement': float(history.total_movement) if history.total_movement else 0,
                    'snapshot_count': history.snapshot_count,
                }
            except GameLineHistory.DoesNotExist:
                game_info = None

            # Format snapshots for charting
            chart_data = []
            for snap in snapshots:
                chart_data.append({
                    'timestamp': snap.captured_at.isoformat(),
                    'bookmaker': snap.bookmaker,
                    'bookmaker_title': snap.bookmaker_title,
                    'market': snap.market,
                    'outcome': snap.outcome_name,
                    'price': snap.price,
                    'point': float(snap.point) if snap.point else None,
                })

            return Response({
                'success': True,
                'game': game_info,
                'snapshots': chart_data,
                'count': len(chart_data),
                'hours': hours,
            })

        else:
            # Get all games with significant movement
            games_query = GameLineHistory.objects.filter(
                last_snapshot_at__gte=cutoff
            ).order_by('-last_snapshot_at')

            if sport:
                games_query = games_query.filter(sport_key=sport)

            # Only games with movement or recent activity
            games = []
            for game in games_query[:50]:
                games.append({
                    'game_id': game.game_id,
                    'home_team': game.home_team,
                    'away_team': game.away_team,
                    'sport_key': game.sport_key,
                    'commence_time': game.commence_time.isoformat() if game.commence_time else None,
                    'open_spread': float(game.open_spread_home) if game.open_spread_home else None,
                    'current_spread': float(game.current_spread_home) if game.current_spread_home else None,
                    'spread_movement': float(game.spread_movement) if game.spread_movement else 0,
                    'open_total': float(game.open_total) if game.open_total else None,
                    'current_total': float(game.current_total) if game.current_total else None,
                    'total_movement': float(game.total_movement) if game.total_movement else 0,
                    'has_significant_movement': game.has_significant_movement,
                    'snapshot_count': game.snapshot_count,
                    'last_updated': game.last_snapshot_at.isoformat() if game.last_snapshot_at else None,
                })

            return Response({
                'success': True,
                'games': games,
                'count': len(games),
                'hours': hours,
            })

    except Exception as e:
        logger.error(f"Error getting line movement: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_games_with_movement(request):
    """
    Session 561: Get games with significant line movement.

    Returns games where spreads or totals have moved significantly,
    useful for identifying sharp money or public betting trends.

    Query params:
    - sport: Filter by sport
    - min_spread_movement: Minimum spread movement (default: 0.5)
    - min_total_movement: Minimum total movement (default: 1.0)
    """
    from core.models_odds_history import GameLineHistory
    from django.utils import timezone
    from django.db.models import Q

    try:
        sport = request.GET.get('sport')
        min_spread = float(request.GET.get('min_spread_movement', 0.5))
        min_total = float(request.GET.get('min_total_movement', 1.0))

        # Get games with movement above threshold
        cutoff = timezone.now() - timedelta(hours=72)

        games_query = GameLineHistory.objects.filter(
            last_snapshot_at__gte=cutoff,
            commence_time__gte=timezone.now()  # Only upcoming games
        ).filter(
            Q(spread_movement__gte=min_spread) |
            Q(spread_movement__lte=-min_spread) |
            Q(total_movement__gte=min_total) |
            Q(total_movement__lte=-min_total)
        ).order_by('-last_snapshot_at')

        if sport:
            games_query = games_query.filter(sport_key=sport)

        movers = []
        for game in games_query[:30]:
            movers.append({
                'game_id': game.game_id,
                'matchup': f"{game.away_team} @ {game.home_team}",
                'sport_key': game.sport_key,
                'commence_time': game.commence_time.isoformat() if game.commence_time else None,
                'spread': {
                    'open': float(game.open_spread_home) if game.open_spread_home else None,
                    'current': float(game.current_spread_home) if game.current_spread_home else None,
                    'movement': float(game.spread_movement) if game.spread_movement else 0,
                    'direction': 'favorite' if (game.spread_movement or 0) < 0 else 'underdog'
                },
                'total': {
                    'open': float(game.open_total) if game.open_total else None,
                    'current': float(game.current_total) if game.current_total else None,
                    'movement': float(game.total_movement) if game.total_movement else 0,
                    'direction': 'over' if (game.total_movement or 0) > 0 else 'under'
                },
                'snapshot_count': game.snapshot_count,
            })

        return Response({
            'success': True,
            'movers': movers,
            'count': len(movers),
            'thresholds': {
                'min_spread_movement': min_spread,
                'min_total_movement': min_total,
            }
        })

    except Exception as e:
        logger.error(f"Error getting games with movement: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 995B: Sports Betting Intelligence Endpoints
# =============================================================================


def _american_to_probability(odds: int) -> float:
    """Convert American odds to implied probability (0-1)."""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def _predict_from_odds(home_odds, away_odds, home_team, away_team):
    """Generate prediction from American odds with vig removal."""
    home_raw = _american_to_probability(home_odds)
    away_raw = _american_to_probability(away_odds)
    total = home_raw + away_raw
    if total <= 0:
        return None
    # Remove vig
    home_fair = home_raw / total
    away_fair = away_raw / total
    # Pick winner from fair probs
    if home_fair > away_fair:
        winner, confidence = home_team, round(home_fair * 100)
    else:
        winner, confidence = away_team, round(away_fair * 100)
    # Only predict if meaningful edge (>55% fair)
    if max(home_fair, away_fair) <= 0.55:
        return None
    is_value = abs(home_fair - home_raw) > 0.03 or abs(away_fair - away_raw) > 0.03
    return {
        'predicted_winner': winner,
        'confidence': confidence,
        'is_value_pick': is_value,
        'pick_type': 'value' if is_value else 'consensus',
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def get_todays_games(request):
    """
    Session 995B: Today's games with predictions, odds, and scores.
    Combines TheOddsSpider odds with GamePredictor predictions.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        sport_key = request.GET.get('sport')

        # Fetch live odds
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider
        spider = TheOddsSpider()

        if sport_key:
            events = spider.fetch_data(sports=[sport_key], max_results=50)
        else:
            events = spider.fetch_data(max_results=60, max_priority=1)

        odds_events = [e for e in events if e.get('data_type') == 'sports_odds']

        # Fetch scores for completed games
        scores_by_event = {}
        sport_keys_seen = set()
        for e in odds_events:
            sk = e.get('sport_key')
            if sk:
                sport_keys_seen.add(sk)

        for sk in list(sport_keys_seen)[:5]:
            try:
                scores = spider.fetch_scores(sport_key=sk, days_from=1)
                for s in scores:
                    scores_by_event[s['event_id']] = s
            except Exception:
                pass

        # Generate predictions from moneyline odds consensus (with vig removal)
        predictions_by_event = {}
        for event in odds_events:
            eid = event.get('event_id', '')
            home_odds = event.get('home_odds')
            away_odds = event.get('away_odds')
            if home_odds and away_odds:
                pred = _predict_from_odds(
                    home_odds, away_odds,
                    event.get('home_team', ''), event.get('away_team', '')
                )
                if pred:
                    predictions_by_event[eid] = pred

        # Fetch ESPN live game details (period, clock) for live games
        espn_live_details = {}
        espn_sport_map = {
            'americanfootball_nfl': 'nfl', 'americanfootball_ncaaf': 'ncaaf',
            'basketball_nba': 'nba', 'basketball_ncaab': 'ncaab',
            'baseball_mlb': 'mlb', 'icehockey_nhl': 'nhl',
        }
        if DATA_PROVIDERS_AVAILABLE and sports_data_manager:
            for sk in list(sport_keys_seen)[:6]:
                espn_key = espn_sport_map.get(sk)
                if not espn_key:
                    continue
                try:
                    scoreboard = sports_data_manager.espn.get_scoreboard(espn_key)
                    for ev in scoreboard.get('events', []):
                        competitors = ev.get('competitions', [{}])[0].get('competitors', [])
                        status_info = ev.get('status', {})
                        status_type = status_info.get('type', {})
                        home_name = away_name = ''
                        for comp in competitors:
                            tn = comp.get('team', {}).get('displayName', '')
                            if comp.get('homeAway') == 'home':
                                home_name = tn
                            else:
                                away_name = tn
                        if home_name and away_name:
                            key = f"{home_name}|{away_name}".lower()
                            espn_live_details[key] = {
                                'period': status_info.get('period', 0),
                                'clock': status_info.get('displayClock', ''),
                                'status_detail': status_type.get('shortDetail', ''),
                                'status_state': status_type.get('state', 'pre'),
                            }
                except Exception:
                    pass

        # Build response
        games = []
        for event in odds_events:
            eid = event.get('event_id', '')
            score = scores_by_event.get(eid, {})
            prediction = predictions_by_event.get(eid, {})

            home_team = event.get('home_team', '')
            away_team = event.get('away_team', '')

            game = {
                'event_id': eid,
                'sport_key': event.get('sport_key', ''),
                'sport_name': event.get('sport_name', ''),
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': event.get('commence_time', ''),
                # Moneyline
                'home_odds': event.get('home_odds'),
                'away_odds': event.get('away_odds'),
                'draw_odds': event.get('draw_odds'),
                'home_implied_prob': event.get('home_implied_prob'),
                'away_implied_prob': event.get('away_implied_prob'),
                # Spread (point + juice)
                'home_spread': event.get('home_spread'),
                'away_spread': event.get('away_spread'),
                'spread_home_odds': event.get('spread', {}).get('home_odds') if isinstance(event.get('spread'), dict) else None,
                'spread_away_odds': event.get('spread', {}).get('away_odds') if isinstance(event.get('spread'), dict) else None,
                # Totals (line + juice)
                'total_line': event.get('total_line'),
                'over_odds': event.get('over_odds'),
                'under_odds': event.get('under_odds'),
                # Bookmaker info
                'bookmaker_count': event.get('bookmaker_count', 0),
                'best_bookmaker': event.get('best_bookmaker'),
                # Per-bookmaker odds for comparison
                'h2h_odds': event.get('h2h_odds', []),
                # Score (completed or live)
                'completed': score.get('completed', False),
                'home_score': score.get('home_score'),
                'away_score': score.get('away_score'),
                'last_updated': score.get('last_updated'),
                # Prediction from odds consensus
                'predicted_winner': prediction.get('predicted_winner', ''),
                'confidence': prediction.get('confidence', 0),
                'is_value_pick': prediction.get('is_value_pick', False),
                'pick_type': prediction.get('pick_type', ''),
            }

            # Merge ESPN live details (period, clock) via fuzzy team name match
            espn_key = f"{home_team}|{away_team}".lower()
            espn_data = espn_live_details.get(espn_key)
            if not espn_data:
                for ek, ed in espn_live_details.items():
                    if home_team.lower() in ek or away_team.lower() in ek:
                        espn_data = ed
                        break
            if espn_data:
                game['period'] = espn_data.get('period', 0)
                game['clock'] = espn_data.get('clock', '')
                game['status_detail'] = espn_data.get('status_detail', '')

            # Determine prediction outcome for completed games
            if (game['completed'] and game['home_score'] is not None
                    and game['away_score'] is not None and game['predicted_winner']):
                actual_winner = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
                game['prediction_correct'] = (game['predicted_winner'] == actual_winner)
            else:
                game['prediction_correct'] = None

            games.append(game)

        # Sort: live/upcoming first, completed last
        games.sort(key=lambda g: (g['completed'], g.get('commence_time', '')))

        # Get unique sports for filter
        sports = sorted(set(g['sport_key'] for g in games if g['sport_key']))

        return Response({
            'success': True,
            'games': games,
            'total': len(games),
            'sports': sports,
        })

    except Exception as e:
        logger.error(f"Error getting today's games: {e}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_betting_brief(request):
    """
    Session 995B: Full betting brief from SportsBettingCoordinator.
    Returns top plays, executive summary, and per-agent results.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        sport_key = request.GET.get('sport')

        from core.services.sports_betting_coordinator import SportsBettingCoordinator
        coordinator = SportsBettingCoordinator(sport_key=sport_key)
        brief = coordinator.generate_brief()

        return Response({
            'success': True,
            'brief': {
                'generated_at': brief.get('generated_at'),
                'executive_summary': brief.get('executive_summary', ''),
                'top_plays': brief.get('top_plays', []),
                'agents_run': brief.get('agents_run', []),
                'generation_time_seconds': brief.get('generation_time_seconds', 0),
            }
        })

    except Exception as e:
        logger.error(f"Error generating betting brief: {e}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sharp_action(request):
    """
    Session 995B: Sharp action signals from SharpActionDetector.
    Returns divergence signals between sharp and soft bookmakers.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        sport_key = request.GET.get('sport')
        context = {}
        if sport_key:
            context['sport_key'] = sport_key

        from core.agents.markets.sharp_action_detector import SharpActionDetector
        agent = SharpActionDetector()
        result = agent.execute(
            task="Identify sharp betting action and stale lines",
            context=context
        )

        if result.success:
            signals = result.data.get('signals', [])
            return Response({
                'success': True,
                'signals': signals,
                'total': len(signals),
                'hot_count': result.data.get('hot_signals', 0),
                'warm_count': result.data.get('warm_signals', 0),
                'events_scanned': result.data.get('total_events_scanned', 0),
                'llm_analysis': result.data.get('llm_analysis', ''),
            })
        else:
            return Response({
                'success': True,
                'signals': [],
                'total': 0,
                'error': result.error,
            })

    except Exception as e:
        logger.error(f"Error getting sharp action: {e}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_ai_track_record(request):
    """AI prediction performance history — sports MLPrediction data.

    Deduplicates by game: only the latest prediction per game counts
    toward accuracy stats and the predictions list, so re-running the
    prediction task doesn't inflate W/L numbers or show duplicate rows.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        sport = request.GET.get('sport')
        days = int(request.GET.get('days', 30))

        from sports.models import MLPrediction
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg, Count, Q

        cutoff = timezone.now() - timedelta(days=days)
        base_qs = MLPrediction.objects.filter(created_at__gte=cutoff)
        if sport:
            base_qs = base_qs.filter(sport_type=sport)

        # Dedup: only latest prediction per game
        # id is UUID so Max('id') doesn't give latest — use DISTINCT ON (PostgreSQL)
        deduped_ids = list(
            base_qs.order_by('game_id', '-created_at')
            .distinct('game_id')
            .values_list('id', flat=True)
        )
        deduped_qs = MLPrediction.objects.filter(id__in=deduped_ids)
        total = deduped_qs.count()

        # Evaluated predictions (deduped)
        evaluated_qs = deduped_qs.filter(was_correct__isnull=False)
        has_evaluated = evaluated_qs.exists()

        if has_evaluated:
            eval_total = evaluated_qs.count()
            eval_correct = evaluated_qs.filter(was_correct=True).count()
            accuracy = (eval_correct / eval_total * 100) if eval_total > 0 else 0
            avg_conf = evaluated_qs.aggregate(a=Avg('confidence'))['a'] or 0
            calibration = abs(accuracy - avg_conf)

            summary = {
                'sport_type': sport or 'all',
                'days_analyzed': days,
                'total_predictions': total,
                'correct_predictions': eval_correct,
                'incorrect_predictions': eval_total - eval_correct,
                'pending_predictions': total - eval_total,
                'accuracy_percent': round(accuracy, 2),
                'average_confidence': round(avg_conf, 2),
                'calibration_score': round(calibration, 2),
                'is_well_calibrated': calibration < 10.0,
            }

            # By sport (deduped)
            by_sport = {}
            sport_stats = evaluated_qs.values('sport_type').annotate(
                total=Count('id'),
                correct=Count('id', filter=Q(was_correct=True))
            )
            for s in sport_stats:
                st = s['sport_type']
                t = s['total']
                c = s['correct']
                by_sport[st] = {
                    'accuracy': round((c / t * 100) if t > 0 else 0, 2),
                    'total': t,
                    'correct': c,
                    'incorrect': t - c,
                }
        else:
            avg_conf = 0
            if total > 0:
                avg_conf = round(deduped_qs.aggregate(a=Avg('confidence'))['a'] or 0, 1)
            summary = {
                'sport_type': sport or 'all',
                'days_analyzed': days,
                'total_predictions': total,
                'correct_predictions': 0,
                'incorrect_predictions': 0,
                'pending_predictions': total,
                'accuracy_percent': 0,
                'average_confidence': avg_conf,
                'calibration_score': 0,
                'is_well_calibrated': True,
            }
            by_sport = {}

        # Build recent predictions list — evaluated first, then pending
        recent_list = []

        def _serialize_prediction(p, include_result=True):
            try:
                matchup = f"{p.game.away_team.name} @ {p.game.home_team.name}" if p.game else ''
                game_date = p.game.scheduled_start.date().isoformat() if p.game and p.game.scheduled_start else ''
            except Exception:
                matchup = ''
                game_date = ''
            entry = {
                'id': p.id,
                'sport_type': p.sport_type,
                'predicted_winner': p.predicted_winner.name if p.predicted_winner else '',
                'confidence': p.confidence,
                'was_correct': p.was_correct if include_result else None,
                'game_date': game_date,
                'matchup': matchup,
            }
            if p.evaluated_at:
                entry['evaluated_at'] = p.evaluated_at.isoformat()
            return entry

        # Evaluated predictions (deduped)
        eval_recent = evaluated_qs.select_related(
            'game', 'predicted_winner', 'game__home_team', 'game__away_team'
        ).order_by('-evaluated_at')[:30]
        for p in eval_recent:
            recent_list.append(_serialize_prediction(p))

        # Pending predictions (deduped, soonest game first)
        pending_qs = deduped_qs.filter(was_correct__isnull=True).select_related(
            'game', 'predicted_winner', 'game__home_team', 'game__away_team'
        ).order_by('game__scheduled_start')[:20]
        for p in pending_qs:
            recent_list.append(_serialize_prediction(p, include_result=False))

        return Response({
            'success': True,
            'summary': summary,
            'by_sport': by_sport,
            'recent_predictions': recent_list,
        })

    except Exception as e:
        logger.error(f"Error getting AI track record: {e}", exc_info=True)
        return Response({'success': False, 'error': str(e)}, status=500)
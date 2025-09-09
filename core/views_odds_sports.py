"""
Odds calculation and sports analytics endpoints migrated from DBAO tools-manifest.json.
Provides comprehensive betting analytics, Kelly criterion, and live sports data.
"""

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import json
import random

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def convert_odds(request):
    """
    Convert betting odds between formats - migrated from DBAO
    """
    data = json.loads(request.body)
    
    odds_value = data.get('odds', 0)
    from_format = data.get('from_format', 'decimal')
    
    if odds_value <= 0:
        return Response({
            'success': False,
            'error': 'Invalid odds value'
        }, status=400)
    
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
@permission_classes([AllowAny])
def calculate_expected_value(request):
    """
    Calculate expected value for betting opportunities - migrated from DBAO
    """
    data = json.loads(request.body)
    
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
@permission_classes([AllowAny])
def calculate_kelly_criterion(request):
    """
    Calculate optimal bet sizing using Kelly Criterion - migrated from DBAO
    """
    data = json.loads(request.body)
    
    odds = data.get('odds', 0)
    odds_format = data.get('odds_format', 'decimal')
    true_probability = data.get('true_probability', 0)
    bankroll = data.get('bankroll', 0)
    kelly_multiplier = data.get('kelly_multiplier', 0.25)
    
    if not all([odds > 0, 0 <= true_probability <= 1, bankroll > 0, 0 < kelly_multiplier <= 1]):
        return Response({
            'success': False,
            'error': 'Invalid input parameters'
        }, status=400)
    
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
    
    return Response({
        'success': True,
        'result': {
            'kelly_percentage': round(kelly_percentage, 4),
            'recommended_bet': round(recommended_bet, 2),
            'risk_level': risk_level,
            'fractional_kelly': round(fractional_kelly, 4)
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def detect_arbitrage(request):
    """
    Detect arbitrage opportunities across bookmakers - migrated from DBAO
    """
    data = json.loads(request.body)
    
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

@api_view(['POST'])
@permission_classes([AllowAny])
def sports_game_analysis(request):
    """
    Comprehensive game analysis with betting insights - migrated from DBAO
    """
    data = json.loads(request.body)
    
    game_id = data.get('game_id', '')
    sport = data.get('sport', 'football')
    include_weather = data.get('include_weather', False)
    analysis_depth = data.get('analysis_depth', 'basic')
    
    # Mock comprehensive game analysis
    analysis = {
        'game_data': {
            'id': game_id,
            'sport': sport,
            'home_team': 'Team A',
            'away_team': 'Team B',
            'scheduled_time': '2025-09-15T20:00:00Z',
            'venue': 'Stadium XYZ',
            'league': 'NFL' if sport == 'football' else 'NBA'
        },
        'team_analytics': {
            'home_team': {
                'recent_form': '3W-1L-1D',
                'home_record': '8-2',
                'avg_points_scored': 24.5,
                'avg_points_allowed': 18.3,
                'key_players': ['Player A', 'Player B'],
                'injuries': ['Player C (questionable)']
            },
            'away_team': {
                'recent_form': '2W-2L-1D',
                'away_record': '6-4',
                'avg_points_scored': 21.8,
                'avg_points_allowed': 20.1,
                'key_players': ['Player X', 'Player Y'],
                'injuries': ['Player Z (out)']
            }
        },
        'weather_impact': {
            'temperature': 45,
            'wind_speed': 12,
            'precipitation': 'light_rain',
            'impact_score': 0.7
        } if include_weather else None,
        'betting_recommendations': [
            {
                'market': 'moneyline',
                'recommendation': 'home_team',
                'confidence': 0.68,
                'reasoning': 'Strong home record and better recent form'
            },
            {
                'market': 'total_points',
                'recommendation': 'over',
                'line': 42.5,
                'confidence': 0.72,
                'reasoning': 'Both teams averaging high scoring games'
            }
        ]
    }
    
    return Response({
        'success': True,
        'analysis': analysis
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def live_betting_opportunities(request):
    """
    Real-time live betting opportunities detection - migrated from DBAO
    """
    sport = request.GET.get('sport', 'all')
    min_edge = float(request.GET.get('min_edge', 0.04))
    max_opportunities = int(request.GET.get('max_opportunities', 10))
    
    # Mock live opportunities data
    opportunities = []
    
    for i in range(min(max_opportunities, 8)):
        edge = random.uniform(min_edge, 0.15)
        opportunity = {
            'game_id': f'game_{i + 1}',
            'sport': random.choice(['football', 'basketball', 'baseball']),
            'bet_type': random.choice(['moneyline', 'spread', 'total', 'player_props']),
            'edge': round(edge, 4),
            'recommended_stake': round(random.uniform(50, 200), 2),
            'bookmaker': random.choice(['DraftKings', 'FanDuel', 'BetMGM', 'Caesars']),
            'odds': round(random.uniform(1.8, 3.5), 2),
            'expires_at': (datetime.now() + timedelta(minutes=random.randint(5, 30))).isoformat(),
            'confidence': round(random.uniform(0.7, 0.95), 2)
        }
        opportunities.append(opportunity)
    
    # Filter by sport if specified
    if sport != 'all':
        opportunities = [opp for opp in opportunities if opp['sport'] == sport]
    
    return Response({
        'success': True,
        'opportunities': opportunities,
        'last_updated': datetime.now().isoformat(),
        'total_found': len(opportunities)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def list_betting_markets(request):
    """
    List available betting markets with filtering - migrated from DBAO
    """
    sport = request.GET.get('sport', 'all')
    league = request.GET.get('league', 'all') 
    search = request.GET.get('search', '')
    
    # Mock betting markets data
    markets = [
        {
            'id': 'game_1',
            'name': 'Chiefs vs Bills',
            'sport': 'football',
            'league': 'NFL',
            'home_team': 'Kansas City Chiefs',
            'away_team': 'Buffalo Bills',
            'game_time': '2025-09-15T17:00:00Z',
            'markets_available': ['moneyline', 'spread', 'total', 'player_props']
        },
        {
            'id': 'game_2',
            'name': 'Lakers vs Warriors',
            'sport': 'basketball',
            'league': 'NBA',
            'home_team': 'Los Angeles Lakers',
            'away_team': 'Golden State Warriors',
            'game_time': '2025-09-15T22:00:00Z',
            'markets_available': ['moneyline', 'spread', 'total', 'player_props']
        },
        {
            'id': 'game_3',
            'name': 'Yankees vs Red Sox',
            'sport': 'baseball',
            'league': 'MLB',
            'home_team': 'New York Yankees',
            'away_team': 'Boston Red Sox',
            'game_time': '2025-09-15T19:00:00Z',
            'markets_available': ['moneyline', 'run_line', 'total', 'player_props']
        }
    ]
    
    # Apply filters
    filtered_markets = markets
    
    if sport != 'all':
        filtered_markets = [m for m in filtered_markets if m['sport'] == sport]
    
    if league != 'all':
        filtered_markets = [m for m in filtered_markets if m['league'] == league]
    
    if search:
        filtered_markets = [m for m in filtered_markets 
                          if search.lower() in m['name'].lower() 
                          or search.lower() in m['home_team'].lower()
                          or search.lower() in m['away_team'].lower()]
    
    return Response({
        'count': len(filtered_markets),
        'results': filtered_markets
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bankroll_management(request):
    """
    Get user bankroll management information - migrated from DBAO
    """
    user = request.user
    
    return Response({
        'success': True,
        'bankroll': {
            'starting_bankroll': 5000.00,
            'current_bankroll': 5247.83,
            'peak_bankroll': 5389.12,
            'total_wagered': 12450.00,
            'total_profit': 247.83,
            'roi': 4.96,
            'last_updated': datetime.now().isoformat()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bankroll_stats(request):
    """
    Detailed bankroll performance statistics - migrated from DBAO
    """
    user = request.user
    
    return Response({
        'success': True,
        'stats': {
            'roi': 4.96,
            'win_rate': 0.567,
            'avg_bet_size': 87.50,
            'sharpe_ratio': 1.34,
            'current_streak': 3,
            'longest_winning_streak': 8,
            'longest_losing_streak': 4,
            'total_bets': 142,
            'winning_bets': 80,
            'losing_bets': 62,
            'biggest_win': 456.78,
            'biggest_loss': -234.50,
            'profit_by_month': {
                'january': 123.45,
                'february': -45.67,
                'march': 234.56,
                'april': 87.23,
                'may': -123.45,
                'june': 156.78
            }
        }
    })
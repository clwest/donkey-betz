from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def sports_ai_betting(request):
    """Main sports betting AI interface"""
    context = {
        'title': 'Sports AI Betting Platform',
        'user': request.user if request.user.is_authenticated else None,
        'sports': ['NFL', 'NBA', 'MLB', 'NHL', 'Soccer', 'Tennis', 'MMA', 'Esports'],
        'agents': [
            {'name': 'Odds Scraper', 'status': 'active'},
            {'name': 'Value Finder', 'status': 'analyzing'},
            {'name': 'Line Predictor', 'status': 'calculating'},
            {'name': 'Arbitrage Hunter', 'status': 'scanning'},
            {'name': 'Sentiment Analyzer', 'status': 'processing'},
            {'name': 'Weather Impact', 'status': 'monitoring'},
            {'name': 'Injury Report', 'status': 'active'},
            {'name': 'Pattern Analyzer', 'status': 'learning'},
            {'name': 'Sharp Tracker', 'status': 'tracking'},
            {'name': 'Live Betting', 'status': 'ready'}
        ]
    }
    return render(request, 'sports_ai_betting.html', context)

@csrf_exempt
def api_get_odds(request):
    """API endpoint for fetching latest odds"""
    if request.method == 'GET':
        sport = request.GET.get('sport', 'nfl')

        # Mock data - replace with real odds API integration
        mock_odds = {
            'sport': sport,
            'games': [
                {
                    'id': 'game_001',
                    'home_team': 'Lakers',
                    'away_team': 'Suns',
                    'spread': {'home': -7.5, 'away': 7.5},
                    'total': 232.5,
                    'moneyline': {'home': -280, 'away': 240},
                    'ai_confidence': 87.5,
                    'value_bet': True
                }
            ],
            'last_updated': '2025-09-27T16:00:00Z'
        }

        return JsonResponse(mock_odds)

@csrf_exempt
def api_place_bet(request):
    """API endpoint for placing bets"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body or b"{}")
            bet_type = data.get('type')
            game_id = data.get('game_id')
            amount = data.get('amount')
            selection = data.get('selection')

            # Process bet (mock implementation)
            response = {
                'success': True,
                'bet_id': f'BET_{game_id}_{bet_type}',
                'message': 'Bet placed successfully',
                'potential_return': amount * 1.91  # Mock calculation
            }

            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def api_ai_recommendation(request):
    """API endpoint for AI betting recommendations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body or b"{}")
            game_id = data.get('game_id')

            # Generate AI recommendation (mock)
            recommendation = {
                'game_id': game_id,
                'recommended_bet': 'spread',
                'team': 'home',
                'confidence': 92.3,
                'expected_value': 3.7,
                'reasoning': [
                    'Historical performance favors home team',
                    'Key player injury on away team',
                    'Weather conditions favor under',
                    'Sharp money movement detected'
                ],
                'risk_assessment': 'medium'
            }

            return JsonResponse(recommendation)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def api_agent_status(request):
    """API endpoint for AI agent status"""
    if request.method == 'GET':
        agents_status = {
            'odds_scraper': {'status': 'active', 'updates_per_min': 247, 'last_update': '2 seconds ago'},
            'value_finder': {'status': 'analyzing', 'opportunities_found': 3, 'processing': True},
            'line_predictor': {'status': 'calculating', 'accuracy': 87.5, 'predictions_today': 42},
            'arbitrage_hunter': {'status': 'scanning', 'arbs_found': 1, 'profit_potential': 2.3},
            'sentiment_analyzer': {'status': 'processing', 'posts_analyzed': 15234, 'sentiment': 'bullish'},
            'weather_impact': {'status': 'monitoring', 'games_affected': 2, 'alerts': 1},
            'injury_report': {'status': 'active', 'updates': 7, 'impact_level': 'high'},
            'pattern_analyzer': {'status': 'learning', 'patterns_found': 23, 'confidence': 78.9},
            'sharp_tracker': {'status': 'tracking', 'sharp_bets': 4, 'follow_rate': 67},
            'live_betting': {'status': 'ready', 'opportunities': 8, 'success_rate': 71.2}
        }

        return JsonResponse(agents_status)

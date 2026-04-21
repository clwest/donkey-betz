"""
Views for odds calculation.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([AllowAny])
def kelly_criterion(request):
    """
    Calculate Kelly Criterion for optimal bet sizing.
    """
    # Get parameters from request (support both 'win_probability' and 'true_probability')
    win_probability = request.data.get('win_probability') or request.data.get('true_probability', 0.5)
    odds = request.data.get('odds', 2.0)
    odds_format = request.data.get('odds_format', 'decimal')
    bankroll = request.data.get('bankroll', 1000)
    kelly_multiplier = request.data.get('kelly_multiplier', 0.25)
    
    # Convert odds to decimal based on format
    if odds_format == 'american':
        if isinstance(odds, str):
            odds = odds.lstrip('+')
            odds = float(odds)
        if odds > 0:
            decimal_odds = 1 + (odds / 100)
        else:
            decimal_odds = 1 + (100 / abs(odds))
    elif odds_format == 'fractional':
        if isinstance(odds, str) and '/' in odds:
            parts = odds.split('/')
            decimal_odds = 1 + (float(parts[0]) / float(parts[1]))
        else:
            decimal_odds = float(odds) + 1
    else:  # decimal format
        if isinstance(odds, str):
            if odds.startswith('+'):
                decimal_odds = 1 + (float(odds[1:]) / 100)
            elif odds.startswith('-'):
                decimal_odds = 1 + (100 / abs(float(odds[1:])))
            else:
                decimal_odds = float(odds)
        else:
            decimal_odds = float(odds)
    
    # Calculate Kelly percentage
    # f* = (bp - q) / b
    # where b = decimal_odds - 1, p = win probability, q = 1 - p
    b = decimal_odds - 1
    p = float(win_probability)
    q = 1 - p
    
    # Kelly formula
    if b > 0:
        kelly_percentage = (b * p - q) / b
        # Only bet if there's positive expected value
        if kelly_percentage < 0:
            kelly_percentage = 0
    else:
        kelly_percentage = 0
    
    # Apply Kelly fraction (usually 0.25 for safety)
    adjusted_kelly = kelly_percentage * kelly_multiplier
    
    # Calculate bet size
    bet_size = bankroll * adjusted_kelly if adjusted_kelly > 0 else 0
    
    return Response({
        'kelly_percentage': kelly_percentage,
        'adjusted_kelly': adjusted_kelly,
        'recommended_bet': bet_size,
        'bankroll': bankroll,
        'win_probability': p,
        'odds': odds,
        'decimal_odds': decimal_odds,
        'edge': (p * decimal_odds - 1) if decimal_odds else 0
    })
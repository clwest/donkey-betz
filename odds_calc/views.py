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
    # Get parameters from request
    win_probability = request.data.get('win_probability', 0.5)
    odds = request.data.get('odds', 2.0)
    bankroll = request.data.get('bankroll', 1000)
    
    # Convert odds to decimal if needed
    if isinstance(odds, str):
        if odds.startswith('+'):
            odds = 1 + (float(odds[1:]) / 100)
        elif odds.startswith('-'):
            odds = 1 + (100 / abs(float(odds[1:])))
        else:
            odds = float(odds)
    
    # Calculate Kelly percentage
    # f* = (bp - q) / b
    # where b = odds - 1, p = win probability, q = 1 - p
    b = odds - 1
    p = win_probability
    q = 1 - p
    
    kelly_percentage = (b * p - q) / b if b > 0 else 0
    
    # Apply Kelly fraction (usually 0.25 for safety)
    kelly_fraction = 0.25
    adjusted_kelly = kelly_percentage * kelly_fraction
    
    # Calculate bet size
    bet_size = bankroll * adjusted_kelly if adjusted_kelly > 0 else 0
    
    return Response({
        'kelly_percentage': kelly_percentage,
        'adjusted_kelly': adjusted_kelly,
        'recommended_bet': bet_size,
        'bankroll': bankroll,
        'win_probability': win_probability,
        'odds': odds
    })
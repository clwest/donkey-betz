"""
Sports Analytics Dashboard Views
Provides comprehensive dashboard endpoints for sports betting analytics
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Avg, Count, Max
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Game, Bet, BankrollManagement, ArbitrageOpportunity, 
    BettingRecommendation, OddsLine, LineMovement
)

class SportsDashboardView(LoginRequiredMixin, TemplateView):
    """Main sports analytics dashboard"""
    template_name = 'sports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current user's bankroll management
        try:
            bankroll = BankrollManagement.objects.get(user=self.request.user)
        except BankrollManagement.DoesNotExist:
            bankroll = None
        
        # Calculate basic stats
        user_bets = Bet.objects.filter(user=self.request.user)
        total_bets = user_bets.count()
        total_wagered = user_bets.aggregate(Sum('amount'))['amount__sum'] or 0
        total_profit = user_bets.filter(
            status='won'
        ).aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
        
        # Recent activity
        recent_bets = user_bets.order_by('-created_at')[:10]
        recent_opportunities = ArbitrageOpportunity.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        recent_recommendations = BettingRecommendation.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-created_at')[:5]
        
        context.update({
            'bankroll': bankroll,
            'total_bets': total_bets,
            'total_wagered': total_wagered,
            'total_profit': total_profit,
            'win_rate': self._calculate_win_rate(user_bets),
            'roi': self._calculate_roi(total_wagered, total_profit),
            'recent_bets': recent_bets,
            'recent_opportunities': recent_opportunities,
            'recent_recommendations': recent_recommendations,
        })
        
        return context
    
    def _calculate_win_rate(self, bets):
        """Calculate win rate percentage"""
        total = bets.filter(status__in=['won', 'lost']).count()
        if total == 0:
            return 0
        wins = bets.filter(status='won').count()
        return round((wins / total) * 100, 2)
    
    def _calculate_roi(self, wagered, profit):
        """Calculate return on investment percentage"""
        if wagered == 0:
            return 0
        return round((profit / wagered) * 100, 2)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    """API endpoint for dashboard metrics"""
    user = request.user
    
    # Time period filter
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # User bets in time period
    user_bets = Bet.objects.filter(user=user, created_at__gte=start_date)
    
    # Basic metrics
    total_bets = user_bets.count()
    total_wagered = user_bets.aggregate(Sum('amount'))['amount__sum'] or 0
    total_profit = user_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0
    
    # Win/loss breakdown
    wins = user_bets.filter(status='won').count()
    losses = user_bets.filter(status='lost').count()
    pending = user_bets.filter(status='pending').count()
    
    # Average bet size and odds
    avg_bet_size = user_bets.aggregate(Avg('amount'))['amount__avg'] or 0
    avg_odds = user_bets.aggregate(Avg('odds'))['odds__avg'] or 0
    
    # Sport breakdown
    sport_breakdown = user_bets.values(
        'game__league__sport'
    ).annotate(
        count=Count('id'),
        total_wagered=Sum('amount'),
        profit=Sum('profit_loss')
    ).order_by('-count')
    
    # League breakdown
    league_breakdown = user_bets.values(
        'game__league__name'
    ).annotate(
        count=Count('id'),
        total_wagered=Sum('amount'),
        profit=Sum('profit_loss')
    ).order_by('-count')
    
    # Market type breakdown
    market_breakdown = user_bets.values(
        'betting_market__market_type'
    ).annotate(
        count=Count('id'),
        total_wagered=Sum('amount'),
        profit=Sum('profit_loss')
    ).order_by('-count')
    
    # Recent performance trend (daily)
    daily_performance = []
    for i in range(days):
        date = (timezone.now() - timedelta(days=i)).date()
        day_bets = user_bets.filter(created_at__date=date)
        daily_performance.append({
            'date': date.isoformat(),
            'bets': day_bets.count(),
            'wagered': float(day_bets.aggregate(Sum('amount'))['amount__sum'] or 0),
            'profit': float(day_bets.aggregate(Sum('profit_loss'))['profit_loss__sum'] or 0)
        })
    
    # Bankroll information
    try:
        bankroll = BankrollManagement.objects.get(user=user)
        bankroll_data = {
            'current_balance': float(bankroll.current_balance),
            'initial_balance': float(bankroll.initial_balance),
            'total_wagered': float(bankroll.total_wagered),
            'total_profit': float(bankroll.total_profit),
            'kelly_multiplier': float(bankroll.kelly_multiplier),
            'max_bet_percentage': float(bankroll.max_bet_percentage)
        }
    except BankrollManagement.DoesNotExist:
        bankroll_data = None
    
    return Response({
        'period_days': days,
        'basic_metrics': {
            'total_bets': total_bets,
            'total_wagered': float(total_wagered),
            'total_profit': float(total_profit),
            'win_rate': round((wins / (wins + losses)) * 100, 2) if (wins + losses) > 0 else 0,
            'roi': round((total_profit / total_wagered) * 100, 2) if total_wagered > 0 else 0,
            'avg_bet_size': float(avg_bet_size),
            'avg_odds': float(avg_odds)
        },
        'bet_status': {
            'wins': wins,
            'losses': losses,
            'pending': pending
        },
        'breakdowns': {
            'by_sport': list(sport_breakdown),
            'by_league': list(league_breakdown),
            'by_market': list(market_breakdown)
        },
        'daily_performance': daily_performance,
        'bankroll': bankroll_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def arbitrage_dashboard(request):
    """API endpoint for arbitrage opportunities dashboard"""
    
    # Active opportunities
    active_opportunities = ArbitrageOpportunity.objects.filter(
        is_active=True
    ).order_by('-profit_percentage')[:20]
    
    # Opportunities by sport
    sport_opportunities = ArbitrageOpportunity.objects.filter(
        is_active=True
    ).values(
        'game__league__sport'
    ).annotate(
        count=Count('id'),
        avg_profit=Avg('profit_percentage'),
        max_profit=Max('profit_percentage')
    ).order_by('-avg_profit')
    
    # Recent opportunities (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_opportunities = ArbitrageOpportunity.objects.filter(
        created_at__gte=week_ago
    ).order_by('-created_at')
    
    # Daily opportunity count trend
    daily_opportunities = []
    for i in range(7):
        date = (timezone.now() - timedelta(days=i)).date()
        day_count = ArbitrageOpportunity.objects.filter(
            created_at__date=date
        ).count()
        avg_profit = ArbitrageOpportunity.objects.filter(
            created_at__date=date
        ).aggregate(Avg('profit_percentage'))['profit_percentage__avg'] or 0
        
        daily_opportunities.append({
            'date': date.isoformat(),
            'count': day_count,
            'avg_profit': float(avg_profit)
        })
    
    # Serialize active opportunities
    opportunities_data = []
    for opp in active_opportunities:
        opportunities_data.append({
            'id': opp.id,
            'game': f"{opp.game.away_team.name} @ {opp.game.home_team.name}",
            'market': opp.market_type,
            'profit_percentage': float(opp.profit_percentage),
            'total_stake': float(opp.total_stake),
            'sportsbooks': opp.sportsbooks_involved,
            'created_at': opp.created_at.isoformat(),
            'expires_at': opp.expires_at.isoformat() if opp.expires_at else None
        })
    
    return Response({
        'active_opportunities': opportunities_data,
        'opportunities_by_sport': list(sport_opportunities),
        'daily_trend': daily_opportunities,
        'summary': {
            'total_active': active_opportunities.count(),
            'avg_profit': float(active_opportunities.aggregate(
                Avg('profit_percentage')
            )['profit_percentage__avg'] or 0),
            'max_profit': float(active_opportunities.aggregate(
                Max('profit_percentage')
            )['profit_percentage__max'] or 0),
            'opportunities_today': ArbitrageOpportunity.objects.filter(
                created_at__date=timezone.now().date()
            ).count()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations_dashboard(request):
    """API endpoint for betting recommendations dashboard"""
    user = request.user
    
    # Active recommendations for user
    active_recs = BettingRecommendation.objects.filter(
        user=user,
        is_active=True
    ).order_by('-confidence_score')
    
    # Recommendations by sport
    sport_recs = BettingRecommendation.objects.filter(
        user=user,
        is_active=True
    ).values(
        'game__league__sport'
    ).annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence_score'),
        avg_expected_value=Avg('expected_value')
    ).order_by('-avg_confidence')
    
    # Recent recommendation performance
    recent_recs = BettingRecommendation.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    # Followed vs not followed
    followed_count = recent_recs.filter(followed=True).count()
    not_followed_count = recent_recs.filter(followed=False).count()
    
    # Success rate of followed recommendations
    followed_recs = recent_recs.filter(followed=True)
    successful_followed = followed_recs.filter(
        outcome='won'
    ).count()
    
    success_rate = 0
    if followed_count > 0:
        completed_followed = followed_recs.exclude(outcome='pending').count()
        if completed_followed > 0:
            success_rate = (successful_followed / completed_followed) * 100
    
    # Serialize active recommendations
    recommendations_data = []
    for rec in active_recs[:20]:  # Limit to top 20
        recommendations_data.append({
            'id': rec.id,
            'game': f"{rec.game.away_team.name} @ {rec.game.home_team.name}",
            'market': rec.betting_market.market_type,
            'recommended_bet': rec.recommended_bet,
            'confidence_score': float(rec.confidence_score),
            'expected_value': float(rec.expected_value),
            'kelly_bet_size': float(rec.kelly_bet_size),
            'reasoning': rec.reasoning,
            'created_at': rec.created_at.isoformat(),
            'game_date': rec.game.scheduled_date.isoformat()
        })
    
    return Response({
        'active_recommendations': recommendations_data,
        'recommendations_by_sport': list(sport_recs),
        'performance_metrics': {
            'total_recommendations_30d': recent_recs.count(),
            'followed_count': followed_count,
            'not_followed_count': not_followed_count,
            'success_rate': round(success_rate, 2),
            'avg_confidence': float(recent_recs.aggregate(
                Avg('confidence_score')
            )['confidence_score__avg'] or 0),
            'avg_expected_value': float(recent_recs.aggregate(
                Avg('expected_value')
            )['expected_value__avg'] or 0)
        },
        'summary': {
            'active_count': active_recs.count(),
            'high_confidence_count': active_recs.filter(
                confidence_score__gte=80
            ).count(),
            'positive_ev_count': active_recs.filter(
                expected_value__gt=0
            ).count()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def market_overview(request):
    """API endpoint for overall market overview"""
    
    # Games today
    today = timezone.now().date()
    games_today = Game.objects.filter(scheduled_date__date=today)
    
    # Total odds lines available
    total_odds_lines = OddsLine.objects.filter(is_active=True).count()
    
    # Line movements in last 24 hours
    yesterday = timezone.now() - timedelta(hours=24)
    recent_movements = LineMovement.objects.filter(
        timestamp__gte=yesterday
    ).count()
    
    # Most active games (by line movements)
    active_games = Game.objects.filter(
        scheduled_date__gte=timezone.now(),
        scheduled_date__date__lte=timezone.now().date() + timedelta(days=7)
    ).annotate(
        movement_count=Count('bettingmarket__oddsline__lineMovement')
    ).order_by('-movement_count')[:10]
    
    # Sports with most activity
    sport_activity = Game.objects.filter(
        scheduled_date__date=today
    ).values(
        'league__sport'
    ).annotate(
        game_count=Count('id')
    ).order_by('-game_count')
    
    # Sportsbooks with most lines
    sportsbook_lines = OddsLine.objects.filter(
        is_active=True
    ).values(
        'sportsbook__name'
    ).annotate(
        line_count=Count('id')
    ).order_by('-line_count')[:10]
    
    # Serialize active games
    active_games_data = []
    for game in active_games:
        active_games_data.append({
            'id': game.id,
            'matchup': f"{game.away_team.name} @ {game.home_team.name}",
            'league': game.league.name,
            'sport': game.league.sport,
            'scheduled_date': game.scheduled_date.isoformat(),
            'movement_count': game.movement_count,
            'status': game.status
        })
    
    return Response({
        'games_today': games_today.count(),
        'total_active_lines': total_odds_lines,
        'recent_movements_24h': recent_movements,
        'most_active_games': active_games_data,
        'activity_by_sport': list(sport_activity),
        'sportsbook_coverage': list(sportsbook_lines),
        'market_summary': {
            'total_leagues': Game.objects.values('league').distinct().count(),
            'total_sportsbooks': OddsLine.objects.values('sportsbook').distinct().count(),
            'games_next_7_days': Game.objects.filter(
                scheduled_date__gte=timezone.now(),
                scheduled_date__lte=timezone.now() + timedelta(days=7)
            ).count()
        }
    })
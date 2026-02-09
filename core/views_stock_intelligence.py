"""
Stock Intelligence Dashboard API endpoints.

Surfaces MarketIntelligenceBrief, StockMarketAlert, PredictionOutcome,
and SEC spider data in the web UI.
"""
import logging

from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models_unified_system import (
    MarketIntelligenceBrief,
    PredictionOutcome,
    SpiderData,
)
from core.models_autonomous_alerts import StockMarketAlert

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_dashboard(request):
    """Overview stats for the stock intelligence dashboard."""
    try:
        # Latest brief
        latest_brief = MarketIntelligenceBrief.objects.first()  # ordered by -brief_date
        latest_brief_data = None
        if latest_brief:
            latest_brief_data = {
                'id': str(latest_brief.id),
                'brief_date': latest_brief.brief_date.isoformat(),
                'executive_summary': latest_brief.executive_summary,
                'total_stocks_analyzed': latest_brief.total_stocks_analyzed,
                'debate_zone_count': latest_brief.debate_zone_count,
                'situation_health': latest_brief.situation_health,
            }

        # Alert counts by type
        alert_counts = dict(
            StockMarketAlert.objects.values_list('alert_type')
            .annotate(count=Count('id'))
            .values_list('alert_type', 'count')
        )
        total_alerts = sum(alert_counts.values())

        # Prediction accuracy
        predictions_with_7d = PredictionOutcome.objects.filter(
            was_correct_7_days__isnull=False
        )
        total_predictions = predictions_with_7d.count()
        correct_7d = predictions_with_7d.filter(was_correct_7_days=True).count()
        accuracy_7d = round((correct_7d / total_predictions) * 100, 1) if total_predictions > 0 else None

        predictions_with_30d = PredictionOutcome.objects.filter(
            was_correct_30_days__isnull=False
        )
        total_30d = predictions_with_30d.count()
        correct_30d = predictions_with_30d.filter(was_correct_30_days=True).count()
        accuracy_30d = round((correct_30d / total_30d) * 100, 1) if total_30d > 0 else None

        # SEC filings count
        sec_filings_count = SpiderData.objects.filter(spider_name='sec_edgar').count()

        # Total briefs
        total_briefs = MarketIntelligenceBrief.objects.count()

        return Response({
            'success': True,
            'latest_brief': latest_brief_data,
            'total_briefs': total_briefs,
            'total_alerts': total_alerts,
            'alert_counts_by_type': alert_counts,
            'prediction_accuracy_7d': accuracy_7d,
            'prediction_accuracy_30d': accuracy_30d,
            'total_predictions': total_predictions,
            'sec_filings_count': sec_filings_count,
        })
    except Exception as e:
        logger.exception("Error fetching stock dashboard")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_briefs(request):
    """Paginated list of MarketIntelligenceBrief entries."""
    try:
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))

        qs = MarketIntelligenceBrief.objects.all()  # ordered by -brief_date via Meta
        total = qs.count()
        briefs = qs[offset:offset + limit]

        results = []
        for b in briefs:
            results.append({
                'id': str(b.id),
                'brief_date': b.brief_date.isoformat(),
                'brief_type': b.brief_type,
                'executive_summary': b.executive_summary[:300],
                'total_stocks_analyzed': b.total_stocks_analyzed,
                'debate_zone_count': b.debate_zone_count,
                'situation_health': b.situation_health,
                'confidence_distribution': b.confidence_distribution,
                'generated_at': b.generated_at.isoformat() if b.generated_at else None,
            })

        return Response({
            'success': True,
            'results': results,
            'total': total,
            'limit': limit,
            'offset': offset,
        })
    except Exception as e:
        logger.exception("Error fetching stock briefs")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_brief_detail(request, brief_id):
    """Single brief with full JSON fields."""
    try:
        brief = MarketIntelligenceBrief.objects.get(id=brief_id)
        return Response({
            'success': True,
            'brief': {
                'id': str(brief.id),
                'brief_date': brief.brief_date.isoformat(),
                'brief_type': brief.brief_type,
                'executive_summary': brief.executive_summary,
                'high_conviction_opportunities': brief.high_conviction_opportunities,
                'debate_zone': brief.debate_zone,
                'bullish_opportunities': brief.bullish_opportunities,
                'bearish_warnings': brief.bearish_warnings,
                'risk_alerts': brief.risk_alerts,
                'changes_from_yesterday': brief.changes_from_yesterday,
                'is_first_brief': brief.is_first_brief,
                'total_stocks_analyzed': brief.total_stocks_analyzed,
                'confidence_distribution': brief.confidence_distribution,
                'debate_zone_count': brief.debate_zone_count,
                'situation_health': brief.situation_health,
                'gpt_success_rate': brief.gpt_success_rate,
                'generated_at': brief.generated_at.isoformat() if brief.generated_at else None,
            },
        })
    except MarketIntelligenceBrief.DoesNotExist:
        return Response({'success': False, 'error': 'Brief not found'}, status=404)
    except Exception as e:
        logger.exception("Error fetching brief detail")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_alerts(request):
    """Paginated StockMarketAlert list with filters."""
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        qs = StockMarketAlert.objects.all()  # ordered by -detected_at via Meta

        # Filters
        alert_type = request.GET.get('type')
        if alert_type:
            qs = qs.filter(alert_type=alert_type)

        symbol = request.GET.get('symbol')
        if symbol:
            qs = qs.filter(symbol__iexact=symbol)

        action = request.GET.get('action')
        if action:
            qs = qs.filter(recommended_action=action)

        bookmarked = request.GET.get('bookmarked')
        if bookmarked == 'true':
            qs = qs.filter(bookmarked=True)

        total = qs.count()
        alerts = qs[offset:offset + limit]

        results = []
        for a in alerts:
            results.append({
                'id': str(a.id),
                'alert_type': a.alert_type,
                'symbol': a.symbol,
                'company_name': a.company_name,
                'sector': a.sector,
                'title': a.title,
                'summary': a.summary,
                'bull_case': a.bull_case,
                'bear_case': a.bear_case,
                'disagreement_level': a.disagreement_level,
                'confidence_score': float(a.confidence_score),
                'bull_score': a.bull_score,
                'bear_score': a.bear_score,
                'current_price': float(a.current_price) if a.current_price else None,
                'price_change_24h': float(a.price_change_24h) if a.price_change_24h else None,
                'recommended_action': a.recommended_action,
                'bookmarked': a.bookmarked,
                'detected_at': a.detected_at.isoformat() if a.detected_at else None,
            })

        return Response({
            'success': True,
            'results': results,
            'total': total,
            'limit': limit,
            'offset': offset,
        })
    except Exception as e:
        logger.exception("Error fetching stock alerts")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_predictions(request):
    """PredictionOutcome list with accuracy stats."""
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        qs = PredictionOutcome.objects.all()  # ordered by -prediction_date, ticker via Meta

        ticker = request.GET.get('ticker')
        if ticker:
            qs = qs.filter(ticker__iexact=ticker)

        total = qs.count()
        predictions = qs[offset:offset + limit]

        results = []
        for p in predictions:
            results.append({
                'id': str(p.id),
                'ticker': p.ticker,
                'prediction_type': p.prediction_type,
                'conviction_level': p.conviction_level,
                'predicted_move': float(p.predicted_move),
                'price_at_prediction': float(p.price_at_prediction),
                'prediction_date': p.prediction_date.isoformat(),
                'price_after_7_days': float(p.price_after_7_days) if p.price_after_7_days else None,
                'price_after_30_days': float(p.price_after_30_days) if p.price_after_30_days else None,
                'actual_move_7_days': float(p.actual_move_7_days) if p.actual_move_7_days else None,
                'actual_move_30_days': float(p.actual_move_30_days) if p.actual_move_30_days else None,
                'was_correct_7_days': p.was_correct_7_days,
                'was_correct_30_days': p.was_correct_30_days,
                'accuracy_score_7_days': p.accuracy_score_7_days,
                'accuracy_score_30_days': p.accuracy_score_30_days,
                'was_in_debate_zone': p.was_in_debate_zone,
                'outcome_calculated': p.outcome_calculated,
            })

        # Aggregate stats
        evaluated = qs.filter(was_correct_7_days__isnull=False)
        eval_count = evaluated.count()
        correct_7d = evaluated.filter(was_correct_7_days=True).count()
        correct_30d = evaluated.filter(was_correct_30_days=True).count()
        avg_accuracy_7d = evaluated.aggregate(avg=Avg('accuracy_score_7_days'))['avg']

        return Response({
            'success': True,
            'results': results,
            'total': total,
            'limit': limit,
            'offset': offset,
            'stats': {
                'evaluated_count': eval_count,
                'accuracy_7d_pct': round((correct_7d / eval_count) * 100, 1) if eval_count else None,
                'accuracy_30d_pct': round((correct_30d / eval_count) * 100, 1) if eval_count else None,
                'avg_accuracy_score_7d': round(avg_accuracy_7d, 3) if avg_accuracy_7d else None,
            },
        })
    except Exception as e:
        logger.exception("Error fetching stock predictions")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_sec_filings(request):
    """SEC Edgar spider data entries."""
    try:
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        qs = SpiderData.objects.filter(spider_name='sec_edgar').order_by('-created_at')
        total = qs.count()
        filings = qs[offset:offset + limit]

        results = []
        for f in filings:
            results.append({
                'id': str(f.id),
                'spider_name': f.spider_name,
                'source_url': f.source_url,
                'data_type': f.data_type,
                'raw_data': f.raw_data,
                'relevance_score': f.relevance_score,
                'created_at': f.created_at.isoformat() if f.created_at else None,
            })

        return Response({
            'success': True,
            'results': results,
            'total': total,
            'limit': limit,
            'offset': offset,
        })
    except Exception as e:
        logger.exception("Error fetching SEC filings")
        return Response({'success': False, 'error': str(e)}, status=500)

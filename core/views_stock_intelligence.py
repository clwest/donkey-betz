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

from django.db import IntegrityError

from core.models_unified_system import (
    MarketIntelligenceBrief,
    PredictionOutcome,
    SpiderData,
    UserWatchlistItem,
)
from core.models_autonomous_alerts import StockMarketAlert

logger = logging.getLogger(__name__)

FINANCIAL_NEWS_SPIDERS = [
    'polygon_finance', 'finnhub', 'financial',
]

# Map spider_name → human-readable fallback; RSS items may carry their own 'source' field
SPIDER_SOURCE_NAMES = {
    'polygon_finance': 'Polygon',
    'finnhub': 'Finnhub',
    'financial': 'Financial News',
    'yahoo_finance': 'Yahoo Finance',
    'coingecko': 'CoinGecko',
    'sec_edgar': 'SEC EDGAR',
}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_hub(request):
    """Consolidated hub view — latest brief, top alerts, movers, predictions, news, SEC."""
    try:
        # Latest brief
        latest_brief = MarketIntelligenceBrief.objects.first()
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

        # Stats
        total_briefs = MarketIntelligenceBrief.objects.count()
        total_alerts = StockMarketAlert.objects.count()

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

        sec_filings_count = SpiderData.objects.filter(spider_name='sec_edgar').count()

        # Top alerts (6 most recent)
        top_alerts = []
        for a in StockMarketAlert.objects.all()[:6]:
            top_alerts.append({
                'id': str(a.id),
                'alert_type': a.alert_type,
                'symbol': a.symbol,
                'company_name': a.company_name,
                'title': a.title,
                'summary': (a.summary or '')[:200],
                'confidence_score': float(a.confidence_score),
                'bull_score': a.bull_score,
                'bear_score': a.bear_score,
                'recommended_action': a.recommended_action,
                'detected_at': a.detected_at.isoformat() if a.detected_at else None,
            })

        # Top predictions (8 most recent with results, one per ticker+type)
        top_predictions = []
        for p in PredictionOutcome.objects.filter(
            was_correct_7_days__isnull=False
        ).order_by('ticker', 'prediction_type', '-prediction_date').distinct(
            'ticker', 'prediction_type'
        )[:8]:
            top_predictions.append({
                'id': str(p.id),
                'ticker': p.ticker,
                'prediction_type': p.prediction_type,
                'predicted_move': float(p.predicted_move),
                'actual_move_7_days': float(p.actual_move_7_days) if p.actual_move_7_days is not None else None,
                'was_correct_7_days': p.was_correct_7_days,
                'prediction_date': p.prediction_date.isoformat(),
            })

        # Market news — expand raw_data.items from financial spiders
        market_news = []
        for row in SpiderData.objects.filter(
            spider_name__in=FINANCIAL_NEWS_SPIDERS
        ).order_by('-created_at')[:20]:
            raw = row.raw_data or {}
            entries = raw.get('items', [])
            spider_ts = row.created_at.isoformat() if row.created_at else None
            fallback_source = SPIDER_SOURCE_NAMES.get(row.spider_name, row.spider_name)
            for entry in entries:
                market_news.append({
                    'spider_name': row.spider_name,
                    'source': entry.get('source') or fallback_source,
                    'title': entry.get('title', ''),
                    'description': (entry.get('description') or entry.get('summary') or '')[:200],
                    'link': entry.get('link') or row.source_url,
                    'published': entry.get('published') or spider_ts,
                    'category': entry.get('category') or raw.get('category', ''),
                })
                if len(market_news) >= 10:
                    break
            if len(market_news) >= 10:
                break

        # SEC recent — expand raw_data.items
        sec_recent = []
        for row in SpiderData.objects.filter(
            spider_name='sec_edgar'
        ).order_by('-created_at')[:10]:
            raw = row.raw_data or {}
            entries = raw.get('items', [])
            spider_ts = row.created_at.isoformat() if row.created_at else None
            for entry in entries:
                sec_recent.append({
                    'title': entry.get('title') or entry.get('name', ''),
                    'description': (entry.get('description') or '')[:200],
                    'link': entry.get('link') or row.source_url,
                    'published': entry.get('published') or spider_ts,
                    'filing_type': entry.get('filing_type') or entry.get('form_type') or '',
                })
                if len(sec_recent) >= 5:
                    break
            if len(sec_recent) >= 5:
                break

        return Response({
            'success': True,
            'stats': {
                'total_briefs': total_briefs,
                'total_alerts': total_alerts,
                'total_predictions': total_predictions,
                'accuracy_7d': accuracy_7d,
                'accuracy_30d': accuracy_30d,
                'sec_filings_count': sec_filings_count,
            },
            'latest_brief': latest_brief_data,
            'top_alerts': top_alerts,
            'top_predictions': top_predictions,
            'market_news': market_news,
            'sec_recent': sec_recent,
        })
    except Exception as e:
        logger.exception("Error fetching stock hub")
        return Response({'success': False, 'error': str(e)}, status=500)


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

        # Watchlist filter: only show alerts for user's watched symbols
        watchlist = request.GET.get('watchlist')
        if watchlist == 'true':
            watched = UserWatchlistItem.objects.filter(
                user=request.user,
            ).values_list('symbol', flat=True)
            qs = qs.filter(symbol__in=watched)

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

        # Watchlist filter
        watchlist = request.GET.get('watchlist')
        if watchlist == 'true':
            watched = UserWatchlistItem.objects.filter(
                user=request.user,
            ).values_list('symbol', flat=True)
            qs = qs.filter(ticker__in=watched)

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_market_news(request):
    """Paginated market news feed from financial spiders with source filtering."""
    try:
        limit = min(int(request.GET.get('limit', 20)), 50)
        offset = int(request.GET.get('offset', 0))
        source_filter = request.GET.get('source', '').strip()

        # Collect all news items from financial spiders
        all_news = []
        sources_seen = set()
        for row in SpiderData.objects.filter(
            spider_name__in=FINANCIAL_NEWS_SPIDERS
        ).order_by('-created_at')[:200]:
            raw = row.raw_data or {}
            entries = raw.get('items', [])
            spider_ts = row.created_at.isoformat() if row.created_at else None
            fallback_source = SPIDER_SOURCE_NAMES.get(row.spider_name, row.spider_name)
            for entry in entries:
                source = entry.get('source') or fallback_source
                sources_seen.add(source)
                if source_filter and source != source_filter:
                    continue
                all_news.append({
                    'spider_name': row.spider_name,
                    'source': source,
                    'title': entry.get('title', ''),
                    'description': (entry.get('description') or entry.get('summary') or '')[:300],
                    'link': entry.get('link') or row.source_url,
                    'published': entry.get('published') or spider_ts,
                    'category': entry.get('category') or raw.get('category', ''),
                })

        total = len(all_news)
        page = all_news[offset:offset + limit]

        return Response({
            'success': True,
            'results': page,
            'total': total,
            'limit': limit,
            'offset': offset,
            'sources': sorted(sources_seen),
        })
    except Exception as e:
        logger.exception("Error fetching market news")
        return Response({'success': False, 'error': str(e)}, status=500)


# List of financial spider names whose raw_data may reference ticker symbols
FINANCIAL_SPIDERS = [
    'yahoo_finance', 'polygon_finance', 'coingecko', 'sec_edgar',
]

# Brief JSON fields that contain per-ticker entries
BRIEF_TICKER_FIELDS = [
    'high_conviction_opportunities',
    'debate_zone',
    'bullish_opportunities',
    'bearish_warnings',
]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticker_lookup(request, symbol):
    """
    Unified single-ticker intelligence.

    Aggregates live quote, alerts, predictions, brief mentions,
    SEC filings, and spider data for one symbol.
    """
    symbol = symbol.upper().strip()
    result = {
        'success': True,
        'symbol': symbol,
        'live_quote': None,
        'alerts': {'results': [], 'total': 0},
        'predictions': {'results': [], 'total': 0},
        'brief_mentions': [],
        'sec_filings': {'results': [], 'total': 0},
        'spider_data': {'results': [], 'total': 0},
    }

    # 1. Live quote via MarketDataService
    try:
        from core.services.market_data_service import get_market_data_service
        svc = get_market_data_service()
        quote = svc.get_stock_details(symbol)
        if quote and not quote.get('error'):
            result['live_quote'] = quote
    except Exception as e:
        logger.warning(f"Ticker lookup live quote error for {symbol}: {e}")

    # 2. Alerts
    try:
        alert_qs = StockMarketAlert.objects.filter(
            symbol__iexact=symbol
        ).order_by('-detected_at')
        result['alerts']['total'] = alert_qs.count()
        for a in alert_qs[:20]:
            result['alerts']['results'].append({
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
    except Exception as e:
        logger.warning(f"Ticker lookup alerts error for {symbol}: {e}")

    # 3. Predictions
    try:
        pred_qs = PredictionOutcome.objects.filter(
            ticker__iexact=symbol
        ).order_by('-prediction_date')
        result['predictions']['total'] = pred_qs.count()
        for p in pred_qs[:20]:
            result['predictions']['results'].append({
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
    except Exception as e:
        logger.warning(f"Ticker lookup predictions error for {symbol}: {e}")

    # 4. Brief mentions — scan recent briefs for ticker in JSON fields
    try:
        recent_briefs = MarketIntelligenceBrief.objects.all()[:30]
        for brief in recent_briefs:
            mentions = []
            for field_name in BRIEF_TICKER_FIELDS:
                items = getattr(brief, field_name, None) or []
                if not isinstance(items, list):
                    continue
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    if (item.get('ticker', '') or '').upper() == symbol:
                        mentions.append({
                            'section': field_name,
                            'ticker': item.get('ticker'),
                            'recommendation': item.get('recommendation'),
                            'confidence': item.get('confidence'),
                            'reasoning': item.get('reasoning'),
                        })
            if mentions:
                result['brief_mentions'].append({
                    'brief_id': str(brief.id),
                    'brief_date': brief.brief_date.isoformat(),
                    'mentions': mentions,
                })
    except Exception as e:
        logger.warning(f"Ticker lookup brief mentions error for {symbol}: {e}")

    # 5. SEC filings — search by company name prefix from alerts or live quote
    try:
        company_name = None
        # Try to get company name from alerts first (cheapest)
        if result['alerts']['results']:
            company_name = result['alerts']['results'][0].get('company_name')
        # Fall back to live quote
        if not company_name and result['live_quote']:
            company_name = result['live_quote'].get('company_name') or result['live_quote'].get('name')

        if company_name:
            # Use the first word of the company name to avoid suffix mismatches
            search_term = company_name.split()[0] if company_name else symbol
            sec_qs = SpiderData.objects.filter(
                spider_name='sec_edgar',
                raw_data__icontains=search_term,
            ).order_by('-created_at')
            result['sec_filings']['total'] = sec_qs.count()
            for f in sec_qs[:10]:
                result['sec_filings']['results'].append({
                    'id': str(f.id),
                    'spider_name': f.spider_name,
                    'source_url': f.source_url,
                    'data_type': f.data_type,
                    'raw_data': f.raw_data,
                    'relevance_score': f.relevance_score,
                    'created_at': f.created_at.isoformat() if f.created_at else None,
                })
    except Exception as e:
        logger.warning(f"Ticker lookup SEC filings error for {symbol}: {e}")

    # 6. Spider data — recent mentions across financial spiders
    try:
        spider_qs = SpiderData.objects.filter(
            spider_name__in=FINANCIAL_SPIDERS,
            raw_data__icontains=symbol,
        ).exclude(
            spider_name='sec_edgar',  # Already covered above
        ).order_by('-created_at')
        result['spider_data']['total'] = spider_qs.count()
        for s in spider_qs[:10]:
            result['spider_data']['results'].append({
                'id': str(s.id),
                'spider_name': s.spider_name,
                'source_url': s.source_url,
                'data_type': s.data_type,
                'summary': (s.raw_data or {}).get('summary') or (s.raw_data or {}).get('title', ''),
                'relevance_score': s.relevance_score,
                'created_at': s.created_at.isoformat() if s.created_at else None,
            })
    except Exception as e:
        logger.warning(f"Ticker lookup spider data error for {symbol}: {e}")

    return Response(result)


# ── Watchlist ────────────────────────────────────────────────────────────────


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def watchlist_list(request):
    """List the authenticated user's watchlist symbols."""
    items = UserWatchlistItem.objects.filter(user=request.user)
    return Response({
        'success': True,
        'symbols': [
            {'symbol': w.symbol, 'added_at': w.created_at.isoformat()}
            for w in items
        ],
        'count': items.count(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def watchlist_add(request):
    """Add a symbol to the user's watchlist."""
    symbol = (request.data.get('symbol') or '').upper().strip()
    if not symbol or len(symbol) > 10:
        return Response({'error': 'Valid symbol is required'}, status=400)

    try:
        item = UserWatchlistItem.objects.create(user=request.user, symbol=symbol)
        return Response({
            'success': True,
            'symbol': item.symbol,
            'added_at': item.created_at.isoformat(),
        }, status=201)
    except IntegrityError:
        return Response({'success': True, 'symbol': symbol, 'already_exists': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def watchlist_remove(request, symbol):
    """Remove a symbol from the user's watchlist."""
    symbol = symbol.upper().strip()
    deleted, _ = UserWatchlistItem.objects.filter(
        user=request.user, symbol=symbol,
    ).delete()
    if not deleted:
        return Response({'error': f'{symbol} not in watchlist'}, status=404)
    return Response({'success': True, 'symbol': symbol, 'removed': True})

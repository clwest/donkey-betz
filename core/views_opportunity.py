"""
Opportunity API Endpoints - The Creative Intelligence Empire
=============================================================

Session 223: Phase 1 API endpoints for the Opportunity Engine

Endpoints:
    GET  /api/opportunities/             - List opportunities
    GET  /api/opportunities/<id>/        - Get opportunity detail
    POST /api/opportunities/score/       - Trigger scoring of spider data
    POST /api/opportunities/<id>/act/    - Start acting on an opportunity
    GET  /api/opportunities/top/         - Get top-scored opportunities
    POST /api/opportunities/<id>/rescore/ - Re-score an opportunity
    POST /api/opportunities/analyze/     - Analyze a custom trend
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
import json

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def opportunity_list(request):
    """
    GET /api/opportunities/
    List opportunities with optional filters.

    Query params:
        - status: Filter by status (new, reviewing, creating, published, earning)
        - category: Filter by category (digital_product, freelance, content, etc.)
        - source_type: Filter by source type (trend, job, product, news, etc.)
        - min_score: Minimum overall score (default: 0)
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        - sort: Sort field (overall_score, created_at, profit_potential)
        - order: Sort order (desc, asc)
    """
    try:
        from core.models_unified_system import Opportunity

        # Get query params
        status = request.GET.get('status')
        category = request.GET.get('category')
        source_type = request.GET.get('source_type')
        min_score = int(request.GET.get('min_score', 0))
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        sort = request.GET.get('sort', 'overall_score')
        order = request.GET.get('order', 'desc')

        # Build queryset
        queryset = Opportunity.objects.all()

        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category=category)
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        if min_score > 0:
            queryset = queryset.filter(overall_score__gte=min_score)

        # Filter by user if authenticated
        if request.user.is_authenticated:
            queryset = queryset.filter(user=request.user)

        # Sorting
        sort_field = {
            'overall_score': 'overall_score',
            'created_at': 'created_at',
            'profit_potential': 'profit_potential',
            'time_sensitivity': 'time_sensitivity',
        }.get(sort, 'overall_score')

        if order == 'asc':
            queryset = queryset.order_by(sort_field)
        else:
            queryset = queryset.order_by(f'-{sort_field}')

        # Pagination
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        # Build response
        opportunities = []
        for opp in page_obj:
            opportunities.append({
                'id': str(opp.id),
                'title': opp.title,
                'description': opp.description[:300] if opp.description else '',
                'source_type': opp.source_type,
                'category': opp.category,
                'status': opp.status,
                'scores': {
                    'profit_potential': opp.profit_potential,
                    'competition_level': opp.competition_level,
                    'effort_required': opp.effort_required,
                    'time_sensitivity': opp.time_sensitivity,
                    'overall_score': opp.overall_score,
                },
                'urgency_level': opp.urgency_level if hasattr(opp, 'urgency_level') else 'medium',
                'is_scored': opp.is_scored if hasattr(opp, 'is_scored') else False,
                'suggested_content_types': opp.suggested_content_types or [],
                'suggested_workflows': opp.suggested_workflows or [],
                'keywords': opp.keywords or [],
                'estimated_revenue': float(opp.potential_revenue) if opp.potential_revenue else 0,
                'estimated_cost': float(opp.estimated_cost) if opp.estimated_cost else 0,
                'created_at': opp.created_at.isoformat(),
                'scored_at': opp.scored_at.isoformat() if opp.scored_at else None,
                'expires_at': opp.expires_at.isoformat() if opp.expires_at else None,
            })

        return JsonResponse({
            'success': True,
            'opportunities': opportunities,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })

    except Exception as e:
        logger.error(f"Error listing opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def opportunity_detail(request, opportunity_id):
    """
    GET /api/opportunities/<id>/
    Get detailed information about a specific opportunity.
    """
    try:
        from core.models_unified_system import Opportunity, OpportunityScore, OpportunityAction

        opportunity = Opportunity.objects.get(id=opportunity_id)

        # Get score details if available
        score_details = None
        try:
            score = opportunity.score_details
            score_details = {
                'profit_reasoning': score.profit_reasoning,
                'competition_reasoning': score.competition_reasoning,
                'effort_reasoning': score.effort_reasoning,
                'timing_reasoning': score.timing_reasoning,
                'confidence_level': score.confidence_level,
                'data_sources': score.data_sources,
                'advisors_consulted': score.advisors_consulted,
                'scoring_model_version': score.scoring_model_version,
            }
        except OpportunityScore.DoesNotExist:
            pass

        # Get actions history
        actions = []
        for action in opportunity.actions.all()[:20]:
            actions.append({
                'id': str(action.id),
                'action_type': action.action_type,
                'workflow_used': action.workflow_used,
                'content_ids': action.content_ids,
                'outcome': action.outcome,
                'notes': action.notes,
                'created_at': action.created_at.isoformat(),
            })

        response_data = {
            'success': True,
            'opportunity': {
                'id': str(opportunity.id),
                'title': opportunity.title,
                'description': opportunity.description,
                'source_type': opportunity.source_type,
                'category': opportunity.category,
                'status': opportunity.status,
                'scores': {
                    'profit_potential': opportunity.profit_potential,
                    'competition_level': opportunity.competition_level,
                    'effort_required': opportunity.effort_required,
                    'time_sensitivity': opportunity.time_sensitivity,
                    'overall_score': opportunity.overall_score,
                },
                'score_details': score_details,
                'urgency_level': opportunity.urgency_level if hasattr(opportunity, 'urgency_level') else 'medium',
                'is_scored': opportunity.is_scored if hasattr(opportunity, 'is_scored') else False,
                'suggested_content_types': opportunity.suggested_content_types or [],
                'suggested_workflows': opportunity.suggested_workflows or [],
                'keywords': opportunity.keywords or [],
                'market_data': opportunity.market_data or {},
                'competitor_info': opportunity.competitor_info or {},
                'advisor_recommendations': opportunity.advisor_recommendations or {},
                'estimated_revenue': float(opportunity.potential_revenue) if opportunity.potential_revenue else 0,
                'estimated_cost': float(opportunity.estimated_cost) if opportunity.estimated_cost else 0,
                'estimated_roi': opportunity.estimated_roi if hasattr(opportunity, 'estimated_roi') else 0,
                'actions': actions,
                'created_at': opportunity.created_at.isoformat(),
                'scored_at': opportunity.scored_at.isoformat() if opportunity.scored_at else None,
                'acted_on_at': opportunity.acted_on_at.isoformat() if opportunity.acted_on_at else None,
                'expires_at': opportunity.expires_at.isoformat() if opportunity.expires_at else None,
            }
        }

        return JsonResponse(response_data)

    except Opportunity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting opportunity detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def opportunity_score(request):
    """
    POST /api/opportunities/score/
    Trigger scoring of spider data to create new opportunities.

    Request body:
        - hours: Look back period (default: 24)
        - limit: Max items to score (default: 50)
    """
    try:
        from agents.opportunity_scoring_agent import OpportunityScoringAgent

        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        hours = int(data.get('hours', 24))
        limit = int(data.get('limit', 50))

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        # Run scoring
        agent = OpportunityScoringAgent()
        results = agent.score_spider_data(hours=hours, limit=limit, user=user)

        # Build response
        scored_opportunities = []
        for result in results:
            if result.success:
                scored_opportunities.append({
                    'opportunity_id': result.opportunity_id,
                    'overall_score': result.overall_score,
                    'profit_potential': result.profit_potential,
                    'suggested_content_types': result.suggested_content_types,
                    'estimated_revenue': float(result.estimated_revenue),
                })

        return JsonResponse({
            'success': True,
            'message': f'Scored {len(scored_opportunities)} opportunities',
            'scored_count': len(scored_opportunities),
            'opportunities': scored_opportunities[:10],  # Return top 10
        })

    except Exception as e:
        logger.error(f"Error scoring opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def opportunity_act(request, opportunity_id):
    """
    POST /api/opportunities/<id>/act/
    Start acting on an opportunity (mark as in-progress).

    Request body:
        - workflow: Which workflow to use (optional)
        - content_types: Which content types to create (optional)
        - notes: Any notes (optional)
    """
    try:
        from core.models_unified_system import Opportunity, OpportunityAction

        opportunity = Opportunity.objects.get(id=opportunity_id)

        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        workflow = data.get('workflow', '')
        content_types = data.get('content_types', opportunity.suggested_content_types or [])
        notes = data.get('notes', '')

        # Update opportunity status
        opportunity.status = 'creating' if opportunity.status in ['new', 'active', 'reviewing', 'approved'] else opportunity.status
        opportunity.acted_on_at = timezone.now()
        opportunity.save()

        # Create action record
        user = request.user if request.user.is_authenticated else None
        if user:
            action = OpportunityAction.objects.create(
                opportunity=opportunity,
                user=user,
                action_type='started',
                workflow_used=workflow,
                notes=notes,
            )

            return JsonResponse({
                'success': True,
                'message': f'Started working on opportunity: {opportunity.title}',
                'opportunity_id': str(opportunity.id),
                'action_id': str(action.id),
                'status': opportunity.status,
                'suggested_workflow': workflow or (opportunity.suggested_workflows[0] if opportunity.suggested_workflows else None),
                'content_types': content_types,
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f'Started working on opportunity: {opportunity.title}',
                'opportunity_id': str(opportunity.id),
                'status': opportunity.status,
            })

    except Opportunity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error acting on opportunity: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def opportunity_top(request):
    """
    GET /api/opportunities/top/
    Get top-scored opportunities.

    Query params:
        - limit: Number of opportunities (default: 10, max: 50)
        - min_score: Minimum score (default: 50)
        - category: Filter by category (optional)
    """
    try:
        from agents.opportunity_scoring_agent import OpportunityScoringAgent

        limit = min(int(request.GET.get('limit', 10)), 50)
        min_score = int(request.GET.get('min_score', 50))
        category = request.GET.get('category')

        user = request.user if request.user.is_authenticated else None

        agent = OpportunityScoringAgent()
        opportunities = agent.get_top_opportunities(
            limit=limit,
            min_score=min_score,
            category=category,
            user=user
        )

        return JsonResponse({
            'success': True,
            'count': len(opportunities),
            'opportunities': opportunities,
        })

    except Exception as e:
        logger.error(f"Error getting top opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def opportunity_rescore(request, opportunity_id):
    """
    POST /api/opportunities/<id>/rescore/
    Re-score an existing opportunity with fresh data.
    """
    try:
        from agents.opportunity_scoring_agent import OpportunityScoringAgent

        agent = OpportunityScoringAgent()
        result = agent.rescore_opportunity(opportunity_id)

        if result.success:
            return JsonResponse({
                'success': True,
                'message': 'Opportunity re-scored successfully',
                'opportunity_id': result.opportunity_id,
                'new_scores': {
                    'profit_potential': result.profit_potential,
                    'competition_level': result.competition_level,
                    'effort_required': result.effort_required,
                    'time_sensitivity': result.time_sensitivity,
                    'overall_score': result.overall_score,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error
            }, status=400)

    except Exception as e:
        logger.error(f"Error rescoring opportunity: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def opportunity_analyze(request):
    """
    POST /api/opportunities/analyze/
    Analyze a custom trend/topic and create an opportunity.

    Request body:
        - topic: The trend or topic to analyze (required)
        - data: Additional trend data (optional)
    """
    try:
        from agents.opportunity_scoring_agent import OpportunityScoringAgent

        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)

        topic = data.get('topic')
        if not topic:
            return JsonResponse({
                'success': False,
                'error': 'topic is required'
            }, status=400)

        trend_data = data.get('data', {})
        user = request.user if request.user.is_authenticated else None

        agent = OpportunityScoringAgent()
        result = agent.analyze_trend(topic, trend_data=trend_data, user=user)

        return JsonResponse({
            'success': result.success,
            'opportunity_id': result.opportunity_id,
            'scores': {
                'profit_potential': result.profit_potential,
                'competition_level': result.competition_level,
                'effort_required': result.effort_required,
                'time_sensitivity': result.time_sensitivity,
                'overall_score': result.overall_score,
            },
            'reasoning': {
                'profit': result.profit_reasoning,
                'competition': result.competition_reasoning,
                'effort': result.effort_reasoning,
                'timing': result.timing_reasoning,
            },
            'suggestions': {
                'content_types': result.suggested_content_types,
                'workflows': result.suggested_workflows,
                'keywords': result.keywords,
            },
            'estimates': {
                'revenue': float(result.estimated_revenue),
                'cost': float(result.estimated_cost),
            },
            'error': result.error,
        })

    except Exception as e:
        logger.error(f"Error analyzing trend: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def opportunity_stats(request):
    """
    GET /api/opportunities/stats/
    Get opportunity statistics.
    """
    try:
        from core.models_unified_system import Opportunity
        from django.db.models import Count, Avg

        user = request.user if request.user.is_authenticated else None

        queryset = Opportunity.objects.all()
        if user:
            queryset = queryset.filter(user=user)

        # Status counts
        status_counts = queryset.values('status').annotate(count=Count('id'))

        # Category counts
        category_counts = queryset.filter(category__isnull=False).values('category').annotate(count=Count('id'))

        # Source type counts
        source_type_counts = queryset.filter(source_type__isnull=False).values('source_type').annotate(count=Count('id'))

        # Average scores
        avg_scores = queryset.filter(overall_score__isnull=False).aggregate(
            avg_overall=Avg('overall_score'),
            avg_profit=Avg('profit_potential'),
            avg_competition=Avg('competition_level'),
            avg_effort=Avg('effort_required'),
            avg_timing=Avg('time_sensitivity'),
        )

        # High-value opportunities (score >= 70)
        high_value_count = queryset.filter(overall_score__gte=70).count()

        return JsonResponse({
            'success': True,
            'stats': {
                'total': queryset.count(),
                'high_value': high_value_count,
                'by_status': {item['status']: item['count'] for item in status_counts},
                'by_category': {item['category']: item['count'] for item in category_counts},
                'by_source_type': {item['source_type']: item['count'] for item in source_type_counts},
                'average_scores': {
                    'overall': round(avg_scores['avg_overall'] or 0, 1),
                    'profit_potential': round(avg_scores['avg_profit'] or 0, 1),
                    'competition_level': round(avg_scores['avg_competition'] or 0, 1),
                    'effort_required': round(avg_scores['avg_effort'] or 0, 1),
                    'time_sensitivity': round(avg_scores['avg_timing'] or 0, 1),
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting opportunity stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 224: Revenue Reality - Revenue Tracking Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def opportunity_log_revenue(request, opportunity_id):
    """
    POST /api/opportunities/<id>/revenue/
    Log revenue generated from an opportunity.

    Request body:
        - amount: Revenue amount (required)
        - currency: Currency code (default: USD)
        - platform_fee: Platform/marketplace fee (default: 0)
        - content_type: Type of content (image, video, service, etc.)
        - platform: Where sold (etsy, gumroad, direct, etc.)
        - description: Description of the sale
        - sale_date: When the sale occurred (default: now)
        - external_reference: External order ID
        - image_history_id: Link to ImageHistory if applicable
        - video_history_id: Link to VideoHistory if applicable
    """
    try:
        from core.models_unified_system import Opportunity, OpportunityRevenue, OpportunityAction
        from decimal import Decimal

        opportunity = Opportunity.objects.get(id=opportunity_id)

        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)

        amount = data.get('amount')
        if not amount:
            return JsonResponse({
                'success': False,
                'error': 'amount is required'
            }, status=400)

        user = request.user if request.user.is_authenticated else None

        # Create revenue record
        revenue = OpportunityRevenue(
            opportunity=opportunity,
            user=user,
            amount=Decimal(str(amount)),
            currency=data.get('currency', 'USD'),
            platform_fee=Decimal(str(data.get('platform_fee', 0))),
            content_type=data.get('content_type', 'image'),
            platform=data.get('platform', 'direct'),
            description=data.get('description', ''),
            sale_date=timezone.now() if not data.get('sale_date') else data.get('sale_date'),
            external_reference=data.get('external_reference', ''),
        )

        # Set net_amount before save (or let save() calculate it)
        revenue.net_amount = revenue.amount - revenue.platform_fee

        # Link to content if provided
        if data.get('image_history_id'):
            from content.models import ImageHistory
            try:
                revenue.image_history = ImageHistory.objects.get(id=data['image_history_id'])
            except ImageHistory.DoesNotExist:
                pass

        if data.get('video_history_id'):
            from content.models import VideoHistory
            try:
                revenue.video_history = VideoHistory.objects.get(id=data['video_history_id'])
            except VideoHistory.DoesNotExist:
                pass

        # Use opportunity's predicted revenue for accuracy tracking
        if opportunity.potential_revenue:
            revenue.estimated_revenue = opportunity.potential_revenue

        revenue.save()

        # Create action record
        if user:
            OpportunityAction.objects.create(
                opportunity=opportunity,
                user=user,
                action_type='revenue_logged',
                outcome={
                    'revenue_id': str(revenue.id),
                    'amount': float(revenue.amount),
                    'net_amount': float(revenue.net_amount),
                    'platform': revenue.platform,
                }
            )

        return JsonResponse({
            'success': True,
            'message': f'Revenue of ${revenue.amount} logged successfully',
            'revenue': {
                'id': str(revenue.id),
                'amount': float(revenue.amount),
                'net_amount': float(revenue.net_amount),
                'currency': revenue.currency,
                'platform': revenue.platform,
                'content_type': revenue.content_type,
                'prediction_accuracy': revenue.prediction_accuracy,
                'is_better_than_predicted': revenue.is_better_than_predicted,
            }
        })

    except Opportunity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error logging revenue: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def opportunity_revenue_list(request, opportunity_id):
    """
    GET /api/opportunities/<id>/revenue/
    Get all revenue records for an opportunity.
    """
    try:
        from core.models_unified_system import Opportunity, OpportunityRevenue

        opportunity = Opportunity.objects.get(id=opportunity_id)

        revenues = []
        total_amount = 0
        total_net = 0

        for rev in opportunity.revenues.all():
            revenues.append({
                'id': str(rev.id),
                'amount': float(rev.amount),
                'net_amount': float(rev.net_amount),
                'currency': rev.currency,
                'platform_fee': float(rev.platform_fee),
                'status': rev.status,
                'content_type': rev.content_type,
                'platform': rev.platform,
                'description': rev.description,
                'sale_date': rev.sale_date.isoformat(),
                'prediction_accuracy': rev.prediction_accuracy,
                'is_better_than_predicted': rev.is_better_than_predicted,
                'created_at': rev.created_at.isoformat(),
            })
            if rev.status == 'received':
                total_amount += float(rev.amount)
                total_net += float(rev.net_amount)

        return JsonResponse({
            'success': True,
            'opportunity_id': str(opportunity.id),
            'revenues': revenues,
            'summary': {
                'count': len(revenues),
                'total_amount': total_amount,
                'total_net': total_net,
                'estimated_revenue': float(opportunity.potential_revenue) if opportunity.potential_revenue else 0,
                'actual_vs_estimated': (total_amount / float(opportunity.potential_revenue) * 100) if opportunity.potential_revenue else None,
            }
        })

    except Opportunity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting opportunity revenues: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def revenue_stats(request):
    """
    GET /api/opportunities/revenue/stats/
    Get overall revenue statistics from opportunities.

    Query params:
        - days: Look back period (default: 30)
    """
    try:
        from core.models_unified_system import OpportunityRevenue, Opportunity
        from django.db.models import Sum, Avg, Count, Q
        from datetime import timedelta

        days = int(request.GET.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)

        user = request.user if request.user.is_authenticated else None

        # Base queryset
        queryset = OpportunityRevenue.objects.filter(sale_date__gte=since_date)
        if user:
            queryset = queryset.filter(user=user)

        # Aggregate stats
        stats = queryset.filter(status='received').aggregate(
            total_revenue=Sum('amount'),
            total_net=Sum('net_amount'),
            total_fees=Sum('platform_fee'),
            count=Count('id'),
            avg_amount=Avg('amount'),
            avg_accuracy=Avg('prediction_accuracy'),
        )

        # By platform breakdown
        by_platform = list(
            queryset.filter(status='received')
            .values('platform')
            .annotate(
                total=Sum('amount'),
                count=Count('id')
            )
            .order_by('-total')
        )

        # By content type breakdown
        by_content_type = list(
            queryset.filter(status='received')
            .values('content_type')
            .annotate(
                total=Sum('amount'),
                count=Count('id')
            )
            .order_by('-total')
        )

        # Prediction accuracy stats
        with_predictions = queryset.filter(
            status='received',
            prediction_accuracy__isnull=False
        )
        accuracy_stats = with_predictions.aggregate(
            avg_accuracy=Avg('prediction_accuracy'),
            better_than_predicted=Count('id', filter=Q(prediction_accuracy__gt=100)),
            worse_than_predicted=Count('id', filter=Q(prediction_accuracy__lt=100)),
        )

        # Top performing opportunities
        top_opportunities = list(
            queryset.filter(status='received')
            .values('opportunity__id', 'opportunity__title')
            .annotate(total=Sum('amount'))
            .order_by('-total')[:5]
        )

        # Session 225: Revenue by date for trend chart
        from django.db.models.functions import TruncDate
        by_date = list(
            queryset.filter(status='received')
            .annotate(date=TruncDate('sale_date'))
            .values('date')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('date')
        )

        return JsonResponse({
            'success': True,
            'period_days': days,
            'stats': {
                'total_revenue': float(stats['total_revenue'] or 0),
                'total_net_revenue': float(stats['total_net'] or 0),
                'total_fees': float(stats['total_fees'] or 0),
                'transaction_count': stats['count'] or 0,
                'average_transaction': float(stats['avg_amount'] or 0),
            },
            'prediction_accuracy': {
                'average_accuracy': float(accuracy_stats['avg_accuracy'] or 0),
                'better_than_predicted': accuracy_stats['better_than_predicted'] or 0,
                'worse_than_predicted': accuracy_stats['worse_than_predicted'] or 0,
            },
            'by_platform': [
                {'platform': p['platform'], 'total': float(p['total']), 'count': p['count']}
                for p in by_platform
            ],
            'by_content_type': [
                {'content_type': ct['content_type'], 'total': float(ct['total']), 'count': ct['count']}
                for ct in by_content_type
            ],
            'top_opportunities': [
                {
                    'id': str(opp['opportunity__id']),
                    'title': opp['opportunity__title'],
                    'total_revenue': float(opp['total'])
                }
                for opp in top_opportunities
            ],
            # Session 225: Date breakdown for trend chart
            'by_date': [
                {
                    'date': d['date'].isoformat() if d['date'] else None,
                    'total': float(d['total']),
                    'count': d['count']
                }
                for d in by_date
            ]
        })

    except Exception as e:
        logger.error(f"Error getting revenue stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def opportunity_link_content(request, opportunity_id):
    """
    POST /api/opportunities/<id>/content/
    Link content created from this opportunity.

    Request body:
        - content_type: image, video, audio, 3d_model, template
        - image_history_id: ID of ImageHistory (if content_type is image)
        - video_history_id: ID of VideoHistory (if content_type is video)
        - workflow_used: Which workflow created this content
        - production_cost: Cost to create (API costs, etc.)
    """
    try:
        from core.models_unified_system import Opportunity, OpportunityContent, OpportunityAction
        from decimal import Decimal

        opportunity = Opportunity.objects.get(id=opportunity_id)

        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)

        content_type = data.get('content_type', 'image')
        user = request.user if request.user.is_authenticated else None

        # Create content link
        content = OpportunityContent(
            opportunity=opportunity,
            user=user,
            content_type=content_type,
            workflow_used=data.get('workflow_used', ''),
            workflow_execution_id=data.get('workflow_execution_id', ''),
            production_cost=Decimal(str(data.get('production_cost', 0))),
        )

        # Link to actual content
        if content_type == 'image' and data.get('image_history_id'):
            from content.models import ImageHistory
            try:
                content.image_history = ImageHistory.objects.get(id=data['image_history_id'])
            except ImageHistory.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'ImageHistory not found'
                }, status=404)

        if content_type == 'video' and data.get('video_history_id'):
            from content.models import VideoHistory
            try:
                content.video_history = VideoHistory.objects.get(id=data['video_history_id'])
            except VideoHistory.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'VideoHistory not found'
                }, status=404)

        content.save()

        # Create action record
        if user:
            OpportunityAction.objects.create(
                opportunity=opportunity,
                user=user,
                action_type='content_created',
                content_ids=[str(content.id)],
                workflow_used=content.workflow_used,
            )

        # Update opportunity status
        if opportunity.status in ['new', 'active', 'approved']:
            opportunity.status = 'creating'
            opportunity.save(update_fields=['status'])

        return JsonResponse({
            'success': True,
            'message': f'{content_type} content linked to opportunity',
            'content': {
                'id': str(content.id),
                'content_type': content.content_type,
                'workflow_used': content.workflow_used,
                'production_cost': float(content.production_cost),
            }
        })

    except Opportunity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error linking content: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def opportunity_content_list(request, opportunity_id):
    """
    GET /api/opportunities/<id>/content/
    Get all content created from this opportunity.
    """
    try:
        from core.models_unified_system import Opportunity

        opportunity = Opportunity.objects.get(id=opportunity_id)

        content_items = []
        total_cost = 0
        total_revenue = 0

        for content in opportunity.created_content.all():
            item = {
                'id': str(content.id),
                'content_type': content.content_type,
                'workflow_used': content.workflow_used,
                'production_cost': float(content.production_cost),
                'is_published': content.is_published,
                'published_at': content.published_at.isoformat() if content.published_at else None,
                'published_platforms': content.published_platforms,
                'total_revenue': float(content.total_revenue),
                'roi': content.roi,
                'created_at': content.created_at.isoformat(),
            }

            # Add content details if available
            if content.image_history:
                item['image'] = {
                    'id': str(content.image_history.id),
                    'filename': content.image_history.filename,
                    'thumbnail': content.image_history.thumbnail,
                }
            if content.video_history:
                item['video'] = {
                    'id': str(content.video_history.id),
                    'title': getattr(content.video_history, 'title', 'Video'),
                }

            content_items.append(item)
            total_cost += float(content.production_cost)
            total_revenue += float(content.total_revenue)

        return JsonResponse({
            'success': True,
            'opportunity_id': str(opportunity.id),
            'content': content_items,
            'summary': {
                'count': len(content_items),
                'total_production_cost': total_cost,
                'total_revenue': total_revenue,
                'overall_roi': ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else None,
            }
        })

    except Opportunity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Opportunity not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting opportunity content: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

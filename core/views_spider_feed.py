"""
Spider News Feed API Views
Session 783: Human-facing news feed with agent annotations.

Endpoints:
    GET  /api/spider-feed/                    - Main feed with filters & pagination
    GET  /api/spider-feed/trending/           - Most annotated items (24h)
    GET  /api/spider-feed/item/<id>/          - Single item detail
    POST /api/spider-feed/<id>/annotate/      - Agent creates annotation
    POST /api/spider-feed/<id>/vote/          - Human upvote/downvote
    GET  /api/spider-feed/stats/              - Feed statistics
"""

import logging
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Q, Sum, F
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator

from core.models_unified_system import SpiderData, SpiderDataAnnotation

logger = logging.getLogger(__name__)


def _serialize_spider_item(spider_data, include_full_data=False):
    """Serialize a SpiderData item with its annotations for the feed."""
    # Get annotations for this item
    annotations = list(
        spider_data.annotations.all()
        .values('annotation_type', 'agent_name', 'confidence_score', 'note', 'upvotes', 'downvotes', 'created_at')
    )

    # Build preview from raw_data
    preview = ""
    title = ""
    items = spider_data.raw_data.get('items', []) if spider_data.raw_data else []
    if items:
        first_item = items[0]
        title = first_item.get('title') or first_item.get('name') or first_item.get('modelId') or ''
        description = first_item.get('description') or first_item.get('summary') or ''
        preview = description[:200] + ('...' if len(description) > 200 else '')

    # Get unique badges (annotation types)
    badges = list(set(a['annotation_type'] for a in annotations))

    # Calculate net score
    net_score = sum(a['upvotes'] - a['downvotes'] for a in annotations)

    result = {
        'id': str(spider_data.id),
        'spider_name': spider_data.spider_name,
        'data_type': spider_data.data_type,
        'title': title,
        'preview': preview,
        'source_url': spider_data.source_url,
        'created_at': spider_data.created_at.isoformat() if spider_data.created_at else None,
        'relevance_score': spider_data.relevance_score,
        'is_actionable': spider_data.is_actionable,
        'annotations': [
            {
                'type': a['annotation_type'],
                'agent': a['agent_name'],
                'confidence': a['confidence_score'],
                'note': a['note'],
                'upvotes': a['upvotes'],
                'downvotes': a['downvotes'],
                'created_at': a['created_at'].isoformat() if a['created_at'] else None,
            }
            for a in annotations
        ],
        'score': net_score,
        'badges': badges,
        'annotation_count': len(annotations),
    }

    if include_full_data:
        result['raw_data'] = spider_data.raw_data
        result['processed_data'] = spider_data.processed_data
        result['insights'] = spider_data.insights

    return result


@csrf_exempt
@require_http_methods(["GET"])
def spider_feed(request):
    """
    Main feed endpoint with filters and pagination.

    Query params:
        page: Page number (default: 1)
        per_page: Items per page (default: 20, max: 100)
        source: Filter by spider_name
        category: Filter by data_type
        annotation_type: Filter by annotation type (must have this annotation)
        search: Full-text search in titles and descriptions
        sort: newest, popular (by score), trending (by annotation count)
        hours: Only items from last N hours (default: all)
    """
    try:
        # Parse query params
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 20)), 100)
        source = request.GET.get('source')
        category = request.GET.get('category')
        annotation_type = request.GET.get('annotation_type')
        search = request.GET.get('search', '').strip()
        sort = request.GET.get('sort', 'newest')
        hours = request.GET.get('hours')

        # Base query - only items with annotations
        queryset = SpiderData.objects.filter(
            annotations__isnull=False
        ).distinct().prefetch_related('annotations')

        # Apply filters
        if source:
            queryset = queryset.filter(spider_name__iexact=source)

        if category:
            queryset = queryset.filter(data_type__iexact=category)

        if annotation_type:
            queryset = queryset.filter(annotations__annotation_type=annotation_type)

        if hours:
            cutoff = timezone.now() - timedelta(hours=int(hours))
            queryset = queryset.filter(created_at__gte=cutoff)

        if search:
            # Search in spider_name, data_type, and raw_data (PostgreSQL JSON)
            queryset = queryset.filter(
                Q(spider_name__icontains=search) |
                Q(data_type__icontains=search) |
                Q(raw_data__icontains=search)
            )

        # Apply sorting
        if sort == 'popular':
            # Sort by net score (upvotes - downvotes)
            queryset = queryset.annotate(
                net_score=Coalesce(
                    Sum(F('annotations__upvotes') - F('annotations__downvotes')),
                    0
                )
            ).order_by('-net_score', '-created_at')
        elif sort == 'trending':
            # Sort by annotation count
            queryset = queryset.annotate(
                ann_count=Count('annotations')
            ).order_by('-ann_count', '-created_at')
        else:  # newest
            queryset = queryset.order_by('-created_at')

        # Paginate
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        # Serialize items
        items = [_serialize_spider_item(item) for item in page_obj]

        return JsonResponse({
            'status': 'success',
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'filters': {
                'source': source,
                'category': category,
                'annotation_type': annotation_type,
                'search': search if search else None,
                'sort': sort,
                'hours': int(hours) if hours else None,
            }
        })

    except Exception as e:
        logger.exception("Error in spider_feed")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spider_feed_trending(request):
    """
    Get trending items - most annotated in the last 24 hours.

    Query params:
        hours: Look back period (default: 24)
        limit: Max items (default: 10)
    """
    try:
        hours = int(request.GET.get('hours', 24))
        limit = min(int(request.GET.get('limit', 10)), 50)

        cutoff = timezone.now() - timedelta(hours=hours)

        # Get items with recent annotations, ranked by annotation count
        trending = SpiderData.objects.filter(
            annotations__created_at__gte=cutoff
        ).annotate(
            recent_annotation_count=Count('annotations', filter=Q(annotations__created_at__gte=cutoff)),
            net_score=Coalesce(
                Sum(
                    F('annotations__upvotes') - F('annotations__downvotes'),
                    filter=Q(annotations__created_at__gte=cutoff)
                ),
                0
            )
        ).order_by('-recent_annotation_count', '-net_score')[:limit]

        items = [_serialize_spider_item(item) for item in trending.prefetch_related('annotations')]

        return JsonResponse({
            'status': 'success',
            'items': items,
            'params': {
                'hours': hours,
                'limit': limit,
            }
        })

    except Exception as e:
        logger.exception("Error in spider_feed_trending")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spider_feed_item_detail(request, item_id):
    """
    Get full details for a single spider data item.
    """
    try:
        spider_data = SpiderData.objects.prefetch_related('annotations').get(id=item_id)

        # Increment view count on all annotations
        SpiderDataAnnotation.objects.filter(spider_data=spider_data).update(
            view_count=F('view_count') + 1
        )

        item = _serialize_spider_item(spider_data, include_full_data=True)

        return JsonResponse({
            'status': 'success',
            'item': item
        })

    except SpiderData.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Item not found'
        }, status=404)
    except Exception as e:
        logger.exception("Error in spider_feed_item_detail")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def spider_feed_annotate(request, item_id):
    """
    Create or update an annotation on a spider data item.

    POST body:
        annotation_type: One of the ANNOTATION_TYPES
        confidence: 0.0-1.0 (default: 0.7)
        note: Optional note explaining the annotation
        agent_name: Name of the agent creating the annotation
    """
    import json
    try:
        spider_data = SpiderData.objects.get(id=item_id)

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON body'
            }, status=400)

        annotation_type = data.get('annotation_type')
        confidence = float(data.get('confidence', 0.7))
        note = data.get('note', '')
        agent_name = data.get('agent_name')

        if not annotation_type:
            return JsonResponse({
                'status': 'error',
                'message': 'annotation_type is required'
            }, status=400)

        if not agent_name:
            return JsonResponse({
                'status': 'error',
                'message': 'agent_name is required'
            }, status=400)

        # Validate annotation type
        valid_types = [t[0] for t in SpiderDataAnnotation.ANNOTATION_TYPES]
        if annotation_type not in valid_types:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid annotation_type. Must be one of: {valid_types}'
            }, status=400)

        # Create or update annotation
        annotation, created = SpiderDataAnnotation.objects.update_or_create(
            spider_data=spider_data,
            agent_name=agent_name,
            annotation_type=annotation_type,
            defaults={
                'confidence_score': max(0.0, min(1.0, confidence)),
                'note': note,
            }
        )

        return JsonResponse({
            'status': 'success',
            'annotation': {
                'id': str(annotation.id),
                'type': annotation.annotation_type,
                'agent': annotation.agent_name,
                'confidence': annotation.confidence_score,
                'note': annotation.note,
                'created': created,
            }
        })

    except SpiderData.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Item not found'
        }, status=404)
    except Exception as e:
        logger.exception("Error in spider_feed_annotate")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def spider_feed_vote(request, item_id):
    """
    Upvote or downvote an annotation.

    POST body:
        annotation_id: UUID of the annotation to vote on
        direction: 'up' or 'down'
    """
    import json
    try:
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON body'
            }, status=400)

        annotation_id = data.get('annotation_id')
        direction = data.get('direction')

        if not annotation_id:
            return JsonResponse({
                'status': 'error',
                'message': 'annotation_id is required'
            }, status=400)

        if direction not in ['up', 'down']:
            return JsonResponse({
                'status': 'error',
                'message': "direction must be 'up' or 'down'"
            }, status=400)

        annotation = SpiderDataAnnotation.objects.get(id=annotation_id, spider_data_id=item_id)

        if direction == 'up':
            annotation.upvotes = F('upvotes') + 1
        else:
            annotation.downvotes = F('downvotes') + 1

        annotation.save(update_fields=['upvotes', 'downvotes'])
        annotation.refresh_from_db()

        return JsonResponse({
            'status': 'success',
            'annotation': {
                'id': str(annotation.id),
                'upvotes': annotation.upvotes,
                'downvotes': annotation.downvotes,
                'score': annotation.score,
            }
        })

    except SpiderDataAnnotation.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Annotation not found'
        }, status=404)
    except Exception as e:
        logger.exception("Error in spider_feed_vote")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spider_feed_stats(request):
    """
    Get statistics about the spider feed.
    """
    try:
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Total stats
        total_annotated_items = SpiderData.objects.filter(annotations__isnull=False).distinct().count()
        total_annotations = SpiderDataAnnotation.objects.count()

        # Activity stats
        annotations_24h = SpiderDataAnnotation.objects.filter(created_at__gte=last_24h).count()
        annotations_7d = SpiderDataAnnotation.objects.filter(created_at__gte=last_7d).count()

        # Top sources (by annotation count)
        top_sources = list(
            SpiderData.objects.filter(annotations__isnull=False)
            .values('spider_name')
            .annotate(count=Count('annotations'))
            .order_by('-count')[:5]
        )

        # Annotation type distribution
        type_distribution = list(
            SpiderDataAnnotation.objects.values('annotation_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Top agents
        top_agents = list(
            SpiderDataAnnotation.objects.values('agent_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Most engaged items (highest total votes)
        most_engaged = list(
            SpiderDataAnnotation.objects.values('spider_data_id')
            .annotate(
                total_votes=Sum(F('upvotes') + F('downvotes'))
            )
            .order_by('-total_votes')[:5]
        )

        return JsonResponse({
            'status': 'success',
            'stats': {
                'total_annotated_items': total_annotated_items,
                'total_annotations': total_annotations,
                'annotations_24h': annotations_24h,
                'annotations_7d': annotations_7d,
                'top_sources': top_sources,
                'type_distribution': type_distribution,
                'top_agents': top_agents,
                'most_engaged_item_ids': [str(m['spider_data_id']) for m in most_engaged],
            }
        })

    except Exception as e:
        logger.exception("Error in spider_feed_stats")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

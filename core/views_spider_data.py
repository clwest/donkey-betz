"""
Spider Data Viewer API
View actual data collected by spiders
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json

from core.models_unified_system import SpiderData
from ai_core.spiders.spider_registry import SpiderRegistry


@require_http_methods(["GET"])
def get_spider_items(request, spider_name):
    """Get actual items collected by a specific spider"""
    try:
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        # Get filter parameters
        actionable_only = request.GET.get('actionable', '').lower() == 'true'
        processed_only = request.GET.get('processed', '').lower() == 'true'

        # Build query
        query = SpiderData.objects.filter(spider_name__icontains=spider_name)

        if actionable_only:
            query = query.filter(is_actionable=True)

        if processed_only:
            query = query.filter(is_processed=True)

        # Order by newest first
        query = query.order_by('-created_at')

        # Paginate
        paginator = Paginator(query, page_size)
        page_obj = paginator.get_page(page)

        # Format items
        items = []
        for spider_data in page_obj:
            item = {
                'id': str(spider_data.id),
                'spider_name': spider_data.spider_name,
                'data_type': spider_data.data_type,
                'created_at': spider_data.created_at.isoformat(),
                'is_actionable': spider_data.is_actionable,
                'is_processed': spider_data.is_processed,
                'source_url': spider_data.source_url,
                'data': spider_data.raw_data  # The actual collected data
            }

            # Add formatted preview based on data type
            if isinstance(spider_data.raw_data, dict):
                if 'title' in spider_data.raw_data:
                    item['preview'] = {
                        'title': spider_data.raw_data.get('title', ''),
                        'company': spider_data.raw_data.get('company', ''),
                        'salary': spider_data.raw_data.get('salary', ''),
                        'location': spider_data.raw_data.get('location', ''),
                        'description': spider_data.raw_data.get('description', '')[:200]
                    }
                else:
                    # Generic preview for other data types
                    item['preview'] = {k: str(v)[:100] for k, v in list(spider_data.raw_data.items())[:5]}

            items.append(item)

        return JsonResponse({
            'success': True,
            'spider_name': spider_name,
            'total_items': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'items': items,
            'stats': {
                'total': SpiderData.objects.filter(spider_name__icontains=spider_name).count(),
                'actionable': SpiderData.objects.filter(
                    spider_name__icontains=spider_name,
                    is_actionable=True
                ).count(),
                'processed': SpiderData.objects.filter(
                    spider_name__icontains=spider_name,
                    is_processed=True
                ).count(),
                'unprocessed': SpiderData.objects.filter(
                    spider_name__icontains=spider_name,
                    is_processed=False
                ).count()
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_spider_summary(request):
    """Get summary of all spider data"""
    try:
        registry = SpiderRegistry()
        spiders = registry.list_spiders()

        summaries = []
        for spider_name in spiders:
            spider_data = SpiderData.objects.filter(spider_name=spider_name)

            # Get sample items
            sample_items = []
            for item in spider_data[:3]:
                if isinstance(item.raw_data, dict):
                    sample_items.append({
                        'title': item.raw_data.get('title', 'N/A'),
                        'type': item.data_type,
                        'created': item.created_at.isoformat()
                    })

            summaries.append({
                'spider_name': spider_name,
                'total_items': spider_data.count(),
                'actionable': spider_data.filter(is_actionable=True).count(),
                'processed': spider_data.filter(is_processed=True).count(),
                'latest_activity': spider_data.first().created_at.isoformat() if spider_data.exists() else None,
                'sample_items': sample_items
            })

        return JsonResponse({
            'success': True,
            'total_spiders': len(spiders),
            'total_items': SpiderData.objects.count(),
            'summaries': summaries
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def mark_spider_item_processed(request, item_id):
    """Mark a spider data item as processed"""
    try:
        spider_data = SpiderData.objects.get(id=item_id)
        spider_data.is_processed = True
        spider_data.save()

        return JsonResponse({
            'success': True,
            'message': 'Item marked as processed',
            'item_id': str(item_id)
        })

    except SpiderData.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Item not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
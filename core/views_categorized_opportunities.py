"""
Views for categorized opportunities API
"""

import json
import logging
from typing import Dict, List, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views import View
from intelligence.unified_spider_job_bridge import UnifiedSpiderJobBridge
from ml_pipeline.opportunity_categorizer import get_opportunity_categorizer
import asyncio

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class CategorizedOpportunitiesView(View):
    """API for categorized opportunities"""

    async def get(self, request):
        """Get categorized opportunities and summary"""
        try:
            # Try to get from cache first
            categorized_opportunities = cache.get('categorized_opportunities', [])
            category_summary = cache.get('opportunity_category_summary', {})

            if not categorized_opportunities:
                # If no cached data, trigger spider deployment
                bridge = UnifiedSpiderJobBridge()

                deployment = await bridge.activate_spider_deployment(
                    user_request="Get categorized opportunities for frontend",
                    search_criteria={
                        'keywords': ['remote', 'freelance', 'job', 'opportunity'],
                        'comprehensive_scan': True
                    }
                )

                # Get the categorized data
                categorized_opportunities = cache.get('categorized_opportunities', [])
                category_summary = cache.get('opportunity_category_summary', {})

            return JsonResponse({
                'success': True,
                'opportunities': categorized_opportunities,
                'summary': category_summary,
                'total_count': len(categorized_opportunities),
                'message': 'Categorized opportunities retrieved successfully'
            })

        except Exception as e:
            logger.error(f"Error getting categorized opportunities: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'opportunities': [],
                'summary': {}
            }, status=500)

    async def post(self, request):
        """Trigger new categorization or refresh data"""
        try:
            data = json.loads(request.body) if request.body else {}

            # Get search criteria from request
            search_criteria = data.get('search_criteria', {
                'keywords': ['remote', 'freelance', 'tech', 'writing', 'development'],
                'comprehensive_scan': True,
                'force_refresh': True
            })

            # Deploy spiders with ML categorization
            bridge = UnifiedSpiderJobBridge()
            deployment = await bridge.activate_spider_deployment(
                user_request="Refresh categorized opportunities",
                search_criteria=search_criteria
            )

            # Get the fresh categorized data
            categorized_opportunities = cache.get('categorized_opportunities', [])
            category_summary = cache.get('opportunity_category_summary', {})

            return JsonResponse({
                'success': True,
                'deployment_id': deployment['deployment_id'],
                'opportunities': categorized_opportunities,
                'summary': category_summary,
                'total_count': len(categorized_opportunities),
                'spiders_deployed': deployment.get('spider_count', 0),
                'message': 'Opportunities refreshed and categorized successfully'
            })

        except Exception as e:
            logger.error(f"Error refreshing categorized opportunities: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def select_opportunity(request):
    """Handle opportunity selection"""
    try:
        data = json.loads(request.body)
        opportunity_id = data.get('opportunity_id')
        category = data.get('category')
        action = data.get('action', 'apply')

        # Get the opportunity from cache
        categorized_opportunities = cache.get('categorized_opportunities', [])
        selected_opportunity = None

        for opp in categorized_opportunities:
            if opp.get('id') == opportunity_id:
                selected_opportunity = opp
                break

        if not selected_opportunity:
            return JsonResponse({
                'success': False,
                'error': 'Opportunity not found'
            }, status=404)

        # Log the selection
        logger.info(f"User selected opportunity: {selected_opportunity.get('title')} ({category})")

        # Here you would typically:
        # 1. Add to user's selected opportunities
        # 2. Trigger agent application process
        # 3. Update tracking systems

        # For now, we'll just return success
        return JsonResponse({
            'success': True,
            'message': f'Selected "{selected_opportunity.get("title")}" for {action}',
            'opportunity_id': opportunity_id,
            'next_steps': [
                'Opportunity added to your pipeline',
                'Agent will be assigned for application',
                'You will receive updates on progress'
            ]
        })

    except Exception as e:
        logger.error(f"Error selecting opportunity: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def category_stats(request):
    """Get category statistics and insights"""
    try:
        category_summary = cache.get('opportunity_category_summary', {})
        categorized_opportunities = cache.get('categorized_opportunities', [])

        if not category_summary:
            return JsonResponse({
                'success': False,
                'error': 'No category data available'
            }, status=404)

        # Calculate additional insights
        insights = {
            'trending_categories': [],
            'highest_paying_categories': [],
            'easiest_entry_categories': [],
            'remote_friendly_categories': []
        }

        # Analyze categories for insights
        category_data = {}
        for opp in categorized_opportunities:
            cat_key = opp.get('category', {}).get('main', 'unknown')
            if cat_key not in category_data:
                category_data[cat_key] = {
                    'count': 0,
                    'total_budget': 0,
                    'remote_count': 0,
                    'entry_level_count': 0,
                    'display_name': opp.get('category', {}).get('display_name', cat_key)
                }

            category_data[cat_key]['count'] += 1

            # Budget analysis
            budget = opp.get('financial', {}).get('budget_max') or opp.get('financial', {}).get('budget_min')
            if budget:
                category_data[cat_key]['total_budget'] += budget

            # Remote analysis
            if 'remote' in opp.get('location', '').lower():
                category_data[cat_key]['remote_count'] += 1

            # Entry level analysis
            if opp.get('enrichment', {}).get('difficulty_level') == 'beginner':
                category_data[cat_key]['entry_level_count'] += 1

        # Generate insights
        for cat_key, data in category_data.items():
            if data['count'] > 0:
                avg_budget = data['total_budget'] / data['count'] if data['total_budget'] > 0 else 0
                remote_percentage = data['remote_count'] / data['count']
                entry_percentage = data['entry_level_count'] / data['count']

                if data['count'] >= 5:  # Trending threshold
                    insights['trending_categories'].append({
                        'category': cat_key,
                        'display_name': data['display_name'],
                        'count': data['count']
                    })

                if avg_budget >= 50000:  # High paying threshold
                    insights['highest_paying_categories'].append({
                        'category': cat_key,
                        'display_name': data['display_name'],
                        'average_budget': avg_budget
                    })

                if entry_percentage >= 0.3:  # Easy entry threshold
                    insights['easiest_entry_categories'].append({
                        'category': cat_key,
                        'display_name': data['display_name'],
                        'entry_percentage': entry_percentage
                    })

                if remote_percentage >= 0.7:  # Remote friendly threshold
                    insights['remote_friendly_categories'].append({
                        'category': cat_key,
                        'display_name': data['display_name'],
                        'remote_percentage': remote_percentage
                    })

        return JsonResponse({
            'success': True,
            'summary': category_summary,
            'insights': insights,
            'last_updated': cache.get('last_categorization_update', 'Unknown')
        })

    except Exception as e:
        logger.error(f"Error getting category stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Async view wrapper
async def async_categorized_opportunities_view(request):
    """Async wrapper for categorized opportunities view"""
    view = CategorizedOpportunitiesView()
    if request.method == 'GET':
        return await view.get(request)
    elif request.method == 'POST':
        return await view.post(request)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
"""
Opportunity Aggregator - Collects all opportunities and content for Revenue Dashboard
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


class OpportunityAggregator:
    """
    Aggregates all opportunities, content, and revenue potential
    for display in the Revenue Dashboard
    """

    @staticmethod
    def get_all_opportunities() -> Dict[str, Any]:
        """
        Get all opportunities from various sources

        Returns:
            Aggregated opportunities data
        """
        opportunities = {
            'jobs': [],
            'content': [],
            'applications': [],
            'listings': [],
            'total_potential_revenue': 0,
            'timestamp': datetime.now().isoformat()
        }

        # Load real job opportunities
        try:
            if os.path.exists('/tmp/real_opportunities.json'):
                with open('/tmp/real_opportunities.json', 'r') as f:
                    job_data = json.load(f)
                    opportunities['jobs'] = job_data

                    # Calculate potential from jobs
                    for job in job_data:
                        if job.get('salary_max'):
                            opportunities['total_potential_revenue'] += job['salary_max'] / 12  # Monthly
        except Exception as e:
            logger.error(f"Error loading job opportunities: {e}")

        # Load created content
        try:
            content_files = [f for f in os.listdir('/tmp') if f.startswith('content_') and f.endswith('.json')]
            for content_file in content_files:
                with open(f'/tmp/{content_file}', 'r') as f:
                    content = json.load(f)
                    opportunities['content'].append({
                        'id': content_file.replace('.json', ''),
                        'type': content.get('type'),
                        'title': content.get('title', content.get('project', 'Untitled')),
                        'value': content.get('value_estimate', 0),
                        'created_at': content.get('created_at'),
                        'ready_to_sell': content.get('ready_to_sell', True),
                        'word_count': content.get('word_count', 0)
                    })
                    opportunities['total_potential_revenue'] += content.get('value_estimate', 0)
        except Exception as e:
            logger.error(f"Error loading content: {e}")

        # Load applications sent
        try:
            if os.path.exists('/tmp/applications_tracker.json'):
                with open('/tmp/applications_tracker.json', 'r') as f:
                    applications = json.load(f)
                    opportunities['applications'] = applications
        except Exception as e:
            logger.error(f"Error loading applications: {e}")

        # Load content listings
        try:
            if os.path.exists('/tmp/content_listings.json'):
                with open('/tmp/content_listings.json', 'r') as f:
                    listings = json.load(f)
                    opportunities['listings'] = listings
        except Exception as e:
            logger.error(f"Error loading listings: {e}")

        # Calculate statistics
        opportunities['statistics'] = {
            'total_jobs_found': len(opportunities['jobs']),
            'total_content_created': len(opportunities['content']),
            'total_applications_sent': len(opportunities['applications']),
            'total_content_listed': len(opportunities['listings']),
            'content_value': sum(c.get('value', 0) for c in opportunities['content']),
            'average_job_salary': sum(j.get('salary_max', 0) for j in opportunities['jobs']) / max(len(opportunities['jobs']), 1)
        }

        logger.info(f"📊 Aggregated {len(opportunities['jobs'])} jobs, {len(opportunities['content'])} content pieces")

        return opportunities

    @staticmethod
    def get_actionable_items() -> List[Dict[str, Any]]:
        """
        Get items that need action (not yet applied/listed)

        Returns:
            List of actionable items
        """
        actionable = []
        all_opps = OpportunityAggregator.get_all_opportunities()

        # Find jobs not yet applied to
        applied_job_ids = {app.get('opportunity_id') for app in all_opps['applications']}
        for job in all_opps['jobs']:
            if job.get('id') not in applied_job_ids:
                actionable.append({
                    'type': 'job_application',
                    'item': job,
                    'action': 'Apply Now',
                    'potential_value': job.get('salary_max', 0),
                    'urgency': 'high' if 'senior' in job.get('title', '').lower() else 'medium'
                })

        # Find content not yet listed
        listed_content_ids = {listing.get('content_id') for listing in all_opps['listings']}
        for content in all_opps['content']:
            if content.get('id') not in listed_content_ids:
                actionable.append({
                    'type': 'content_listing',
                    'item': content,
                    'action': 'List for Sale',
                    'potential_value': content.get('value', 0),
                    'urgency': 'medium'
                })

        # Sort by potential value
        actionable.sort(key=lambda x: x.get('potential_value', 0), reverse=True)

        logger.info(f"🎯 Found {len(actionable)} actionable items")

        return actionable


@csrf_exempt
@require_http_methods(["GET"])
def get_opportunities(request):
    """API endpoint to get all opportunities"""
    try:
        opportunities = OpportunityAggregator.get_all_opportunities()
        return JsonResponse({
            'success': True,
            'data': opportunities
        })
    except Exception as e:
        logger.error(f"Error in get_opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_actionable(request):
    """API endpoint to get actionable items"""
    try:
        actionable = OpportunityAggregator.get_actionable_items()
        return JsonResponse({
            'success': True,
            'data': actionable
        })
    except Exception as e:
        logger.error(f"Error in get_actionable: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
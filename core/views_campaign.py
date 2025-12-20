"""
Campaign Orchestrator API Views - Session 513

The Campaign Orchestrator is the HUB that finally connects:
- Intelligence (spider data, web search, research)
- Agents (creation, strategy, writing)
- Autonomous (performance monitoring)
- Delivery (Discord, download, client management)

A customer gives: Product + Target Market + Budget
The system produces: Ad copies, images, videos, emails, social posts
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from core.models_campaign import Campaign, CampaignDeliverable, CampaignResearch
from core.agent_router import AgentRouter

logger = logging.getLogger(__name__)


def _campaign_to_dict(campaign: Campaign) -> dict:
    """Convert a Campaign to a dictionary for API response."""
    deliverables = campaign.deliverables.all()
    deliverable_counts = {}
    for d in deliverables:
        dtype = d.deliverable_type
        deliverable_counts[dtype] = deliverable_counts.get(dtype, 0) + 1

    return {
        'id': str(campaign.id),
        'name': campaign.name,
        'status': campaign.status,
        'status_display': campaign.get_status_display(),
        'budget_tier': campaign.budget_tier,
        'budget_info': campaign.get_budget_info(),
        'client_name': campaign.client_name,
        'product_name': campaign.product_name,
        'product_description': campaign.product_description[:200] + '...' if len(campaign.product_description) > 200 else campaign.product_description,
        'target_market': campaign.target_market[:200] + '...' if len(campaign.target_market) > 200 else campaign.target_market,
        'target_location': campaign.target_location,
        'platforms': campaign.platforms,
        'progress_percent': campaign.progress_percent,
        'current_phase': campaign.current_phase,
        'deliverable_counts': deliverable_counts,
        'total_deliverables': len(deliverables),
        'created_at': campaign.created_at.isoformat(),
        'updated_at': campaign.updated_at.isoformat(),
        'started_at': campaign.started_at.isoformat() if campaign.started_at else None,
        'completed_at': campaign.completed_at.isoformat() if campaign.completed_at else None,
    }


def _deliverable_to_dict(deliverable: CampaignDeliverable) -> dict:
    """Convert a CampaignDeliverable to a dictionary for API response."""
    return {
        'id': str(deliverable.id),
        'type': deliverable.deliverable_type,
        'type_display': deliverable.get_deliverable_type_display(),
        'name': deliverable.name,
        'description': deliverable.description,
        'status': deliverable.status,
        'status_display': deliverable.get_status_display(),
        'platform': deliverable.platform,
        'platform_display': deliverable.get_platform_display(),
        'content_text': deliverable.content_text,
        'file_url': deliverable.file_url,
        'file_path': deliverable.file_path,
        'width': deliverable.width,
        'height': deliverable.height,
        'version': deliverable.version,
        'variant': deliverable.variant,
        'tags': deliverable.tags,
        'created_by_agent': deliverable.created_by_agent,
        'created_at': deliverable.created_at.isoformat(),
    }


def _research_to_dict(research: CampaignResearch) -> dict:
    """Convert a CampaignResearch to a dictionary for API response."""
    return {
        'id': str(research.id),
        'type': research.research_type,
        'type_display': research.get_research_type_display(),
        'title': research.title,
        'summary': research.summary,
        'data': research.data,
        'source': research.source,
        'source_urls': research.source_urls,
        'agent_name': research.agent_name,
        'created_at': research.created_at.isoformat(),
    }


@login_required
@require_http_methods(["GET"])
def campaign_list(request):
    """
    List all campaigns for the current user.

    GET /api/campaigns/

    Query params:
        - status: Filter by status (intake, research, strategy, creation, review, complete, etc.)
        - limit: Number of results (default 20)
        - offset: Pagination offset (default 0)
    """
    try:
        status_filter = request.GET.get('status', '')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        campaigns = Campaign.objects.filter(user=request.user).order_by('-created_at')

        if status_filter:
            campaigns = campaigns.filter(status=status_filter)

        total_count = campaigns.count()
        campaigns = campaigns[offset:offset + limit]

        # Get status counts
        status_counts = {}
        for status, label in Campaign.STATUS_CHOICES:
            status_counts[status] = Campaign.objects.filter(user=request.user, status=status).count()

        return JsonResponse({
            'success': True,
            'campaigns': [_campaign_to_dict(c) for c in campaigns],
            'total_count': total_count,
            'status_counts': status_counts,
            'budget_tiers': Campaign.BUDGET_TIERS,
        })

    except Exception as e:
        logger.error(f"Error listing campaigns: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def campaign_create(request):
    """
    Create a new campaign.

    POST /api/campaigns/create/

    Body:
    {
        "name": "Mike's Auto - Honda Civic Sale",
        "product_name": "2019 Honda Civic",
        "product_description": "Low miles, clean title, great condition...",
        "target_market": "Young professionals in Denver metro area",
        "target_location": "Denver, CO",
        "budget_tier": "pro",  # starter, pro, enterprise, premium
        "platforms": ["facebook", "craigslist", "email"],
        "client_name": "Mike's Auto",
        "competitors": ["CarMax", "AutoNation"],
        "brand_colors": ["#FF0000", "#000000"],
        "brand_style": "professional"
    }
    """
    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ['name', 'product_name', 'product_description', 'target_market']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f"Missing required field: {field}"
                }, status=400)

        # Create campaign
        campaign = Campaign.objects.create(
            user=request.user,
            name=data['name'],
            product_name=data['product_name'],
            product_description=data['product_description'],
            target_market=data['target_market'],
            target_location=data.get('target_location', ''),
            budget_tier=data.get('budget_tier', 'starter'),
            platforms=data.get('platforms', ['general']),
            client_name=data.get('client_name', ''),
            competitors=data.get('competitors', []),
            brand_colors=data.get('brand_colors', []),
            brand_fonts=data.get('brand_fonts', []),
            brand_style=data.get('brand_style', ''),
            product_features=data.get('product_features', []),
            target_demographics=data.get('target_demographics', {}),
        )

        logger.info(f"Created campaign {campaign.id}: {campaign.name}")

        return JsonResponse({
            'success': True,
            'campaign': _campaign_to_dict(campaign),
            'message': f"Campaign '{campaign.name}' created successfully. Ready to start."
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating campaign: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def campaign_detail(request, campaign_id):
    """
    Get full details of a campaign including deliverables and research.

    GET /api/campaigns/<campaign_id>/
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id, user=request.user)

        # Get full campaign data
        campaign_data = _campaign_to_dict(campaign)

        # Add full product description and target market
        campaign_data['product_description_full'] = campaign.product_description
        campaign_data['target_market_full'] = campaign.target_market
        campaign_data['product_features'] = campaign.product_features
        campaign_data['target_demographics'] = campaign.target_demographics
        campaign_data['competitors'] = campaign.competitors
        campaign_data['brand_colors'] = campaign.brand_colors
        campaign_data['brand_fonts'] = campaign.brand_fonts
        campaign_data['brand_style'] = campaign.brand_style

        # Add research data
        campaign_data['research_data'] = campaign.research_data
        campaign_data['competitor_analysis'] = campaign.competitor_analysis
        campaign_data['market_trends'] = campaign.market_trends

        # Add strategy data
        campaign_data['content_strategy'] = campaign.content_strategy
        campaign_data['brand_direction'] = campaign.brand_direction
        campaign_data['seo_keywords'] = campaign.seo_keywords

        # Add execution data
        campaign_data['phase_details'] = campaign.phase_details
        campaign_data['execution_log'] = campaign.execution_log[-20:]  # Last 20 entries
        campaign_data['total_api_calls'] = campaign.total_api_calls
        campaign_data['total_tokens_used'] = campaign.total_tokens_used

        # Get deliverables
        deliverables = campaign.deliverables.all().order_by('deliverable_type', '-created_at')
        campaign_data['deliverables'] = [_deliverable_to_dict(d) for d in deliverables]

        # Get research items
        research_items = campaign.research_items.all().order_by('-created_at')
        campaign_data['research_items'] = [_research_to_dict(r) for r in research_items]

        return JsonResponse({
            'success': True,
            'campaign': campaign_data
        })

    except Campaign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': "Campaign not found"
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting campaign detail: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def campaign_start(request, campaign_id):
    """
    Start a campaign - kicks off the Campaign Orchestrator Agent.

    POST /api/campaigns/<campaign_id>/start/

    This triggers:
    1. Research phase (market trends, competitor analysis)
    2. Strategy phase (content strategy, SEO keywords)
    3. Creation phase (ad copies, social posts, emails)

    The orchestrator runs asynchronously and updates the campaign as it progresses.
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id, user=request.user)

        if campaign.status != 'intake':
            return JsonResponse({
                'success': False,
                'error': f"Campaign is already in '{campaign.get_status_display()}' phase. Cannot restart."
            }, status=400)

        # Mark as started
        campaign.start_campaign()

        # Build task description for the orchestrator
        task = f"""
        Execute full marketing campaign for:

        Campaign: {campaign.name}
        Product: {campaign.product_name}
        Description: {campaign.product_description}
        Target Market: {campaign.target_market}
        Location: {campaign.target_location or 'Not specified'}
        Budget Tier: {campaign.budget_tier} ({campaign.get_budget_info()['name']})
        Platforms: {', '.join(campaign.platforms) if campaign.platforms else 'General'}

        Competitors to analyze: {', '.join(campaign.competitors) if campaign.competitors else 'None specified'}

        Please run through all phases:
        1. RESEARCH - Market trends, competitor analysis
        2. STRATEGY - Content strategy, SEO keywords, brand direction
        3. CREATION - Generate all deliverables for this budget tier
        """

        # Route to Campaign Orchestrator Agent
        router = AgentRouter(user=request.user)

        context = {
            'campaign_id': str(campaign.id),
            'budget_tier': campaign.budget_tier,
            'platforms': campaign.platforms,
        }

        result = router.route(
            agent_name="CampaignOrchestratorAgent",
            task=task,
            context=context
        )

        # Update campaign with initial results
        if result.success:
            campaign.log_execution("campaign_started", {
                'agent': 'CampaignOrchestratorAgent',
                'message': result.message
            })

            return JsonResponse({
                'success': True,
                'message': f"Campaign '{campaign.name}' started successfully!",
                'campaign': _campaign_to_dict(campaign),
                'agent_result': {
                    'message': result.message,
                    'data': result.data
                }
            })
        else:
            campaign.status = 'intake'  # Revert to intake on failure
            campaign.save()

            return JsonResponse({
                'success': False,
                'error': result.error or "Campaign orchestrator failed to start"
            }, status=500)

    except Campaign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': "Campaign not found"
        }, status=404)
    except Exception as e:
        logger.error(f"Error starting campaign: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def campaign_status(request, campaign_id):
    """
    Get quick status of a campaign.

    GET /api/campaigns/<campaign_id>/status/
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id, user=request.user)

        deliverables = campaign.deliverables.all()
        completed_count = deliverables.filter(status='complete').count()
        total_count = deliverables.count()

        return JsonResponse({
            'success': True,
            'id': str(campaign.id),
            'name': campaign.name,
            'status': campaign.status,
            'status_display': campaign.get_status_display(),
            'progress_percent': campaign.progress_percent,
            'current_phase': campaign.current_phase,
            'deliverables_completed': completed_count,
            'deliverables_total': total_count,
            'last_updated': campaign.updated_at.isoformat(),
            'phase_details': campaign.phase_details,
        })

    except Campaign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': "Campaign not found"
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def campaign_deliverables(request, campaign_id):
    """
    Get deliverables for a campaign.

    GET /api/campaigns/<campaign_id>/deliverables/

    Query params:
        - type: Filter by type (ad_copy, image, video, email, social_post, etc.)
        - status: Filter by status (pending, creating, complete, failed)
        - platform: Filter by platform (facebook, instagram, craigslist, etc.)
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id, user=request.user)

        type_filter = request.GET.get('type', '')
        status_filter = request.GET.get('status', '')
        platform_filter = request.GET.get('platform', '')

        deliverables = campaign.deliverables.all()

        if type_filter:
            deliverables = deliverables.filter(deliverable_type=type_filter)
        if status_filter:
            deliverables = deliverables.filter(status=status_filter)
        if platform_filter:
            deliverables = deliverables.filter(platform=platform_filter)

        deliverables = deliverables.order_by('deliverable_type', '-created_at')

        # Group by type
        by_type = {}
        for d in deliverables:
            dtype = d.deliverable_type
            if dtype not in by_type:
                by_type[dtype] = []
            by_type[dtype].append(_deliverable_to_dict(d))

        return JsonResponse({
            'success': True,
            'campaign_id': str(campaign.id),
            'campaign_name': campaign.name,
            'deliverables': [_deliverable_to_dict(d) for d in deliverables],
            'by_type': by_type,
            'total_count': len(deliverables),
        })

    except Campaign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': "Campaign not found"
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting campaign deliverables: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def campaign_delete(request, campaign_id):
    """
    Delete a campaign and all its deliverables.

    DELETE /api/campaigns/<campaign_id>/
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id, user=request.user)

        name = campaign.name
        campaign.delete()

        logger.info(f"Deleted campaign: {name}")

        return JsonResponse({
            'success': True,
            'message': f"Campaign '{name}' deleted successfully"
        })

    except Campaign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': "Campaign not found"
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def campaign_budget_tiers(request):
    """
    Get available budget tiers.

    GET /api/campaigns/budget-tiers/
    """
    return JsonResponse({
        'success': True,
        'budget_tiers': Campaign.BUDGET_TIERS
    })

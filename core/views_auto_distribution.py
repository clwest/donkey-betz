"""
Session 230: Automated Distribution System
==========================================

This module implements automated content distribution workflows:
- Auto-upload workflows for images/videos
- Distribution scheduling
- Batch upload support
- Multi-platform distribution automation

Key Features:
- Queue-based distribution using Celery
- Smart scheduling based on optimal posting times
- Batch operations for multiple content items
- Cross-platform distribution from single action
"""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from core.models_unified_system import (
    UserPlatformAccount,
    ContentDistribution,
    DistributionAnalytics,
)
from core.api_responses import api_success, api_error

logger = logging.getLogger(__name__)


# =============================================================================
# Distribution Queue Models
# =============================================================================

# We'll use Celery tasks with Django models for queue management


# =============================================================================
# Auto-Upload Workflows
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def create_auto_distribution(request):
    """
    POST /api/distribution/auto/create/

    Create an automated distribution across multiple platforms.

    Request body:
    {
        "content_type": "image",
        "image_history_id": "uuid",  // or video_history_id
        "title": "My AI Art",
        "description": "Beautiful AI-generated artwork",
        "tags": ["ai", "art", "digital"],
        "platforms": ["etsy", "gumroad", "shutterstock"],  // or "all" for all connected
        "pricing": {
            "etsy": 29.99,
            "gumroad": 9.99,
            "shutterstock": null  // Shutterstock sets pricing
        },
        "schedule": {
            "type": "immediate" | "scheduled" | "optimal",
            "datetime": "2025-11-28T10:00:00Z"  // For scheduled
        }
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return api_error("Invalid JSON")

    required_fields = ['content_type', 'title']
    for field in required_fields:
        if field not in data:
            return api_error(f"Missing required field: {field}")

    # Get user's connected platforms
    connected_accounts = UserPlatformAccount.objects.filter(
        user=request.user,
        account_status='active'
    ).select_related('platform')

    if not connected_accounts.exists():
        return api_error("No platforms connected. Please connect at least one platform.")

    # Determine target platforms
    target_platforms = data.get('platforms', [])
    if target_platforms == 'all' or not target_platforms:
        target_accounts = list(connected_accounts)
    else:
        target_accounts = [
            acc for acc in connected_accounts
            if acc.platform.name.lower() in [p.lower() for p in target_platforms]
        ]

    if not target_accounts:
        return api_error("No matching connected platforms found")

    # Get content reference
    content_id = None
    image = None
    video = None

    if data['content_type'] == 'image' and data.get('image_history_id'):
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=data['image_history_id'])
            content_id = str(image.id)
        except ImageHistory.DoesNotExist:
            return api_error("Image not found")

    elif data['content_type'] == 'video' and data.get('video_history_id'):
        from content.models import VideoHistory
        try:
            video = VideoHistory.objects.get(id=data['video_history_id'])
            content_id = str(video.id)
        except VideoHistory.DoesNotExist:
            return api_error("Video not found")

    # Parse schedule
    schedule_type = data.get('schedule', {}).get('type', 'immediate')
    scheduled_time = None

    if schedule_type == 'scheduled':
        try:
            scheduled_time = datetime.fromisoformat(
                data['schedule']['datetime'].replace('Z', '+00:00')
            )
        except (KeyError, ValueError):
            return api_error("Invalid scheduled datetime")

    elif schedule_type == 'optimal':
        # Calculate optimal posting time based on platform analytics
        scheduled_time = calculate_optimal_posting_time(request.user, target_accounts)

    # Create distribution records
    created_distributions = []
    pricing = data.get('pricing', {})

    with transaction.atomic():
        for account in target_accounts:
            platform_name = account.platform.name.lower()

            # Get platform-specific pricing
            price = pricing.get(platform_name) or pricing.get('default')
            if price is not None:
                price = Decimal(str(price))

            distribution = ContentDistribution.objects.create(
                user=request.user,
                platform_account=account,
                content_type=data['content_type'],
                image_history=image,
                video_history=video,
                title=data['title'],
                description=data.get('description', ''),
                tags=data.get('tags', []),
                price=price,
                status='pending' if schedule_type == 'immediate' else 'draft',
                platform_metadata={
                    'auto_distribution': True,
                    'schedule_type': schedule_type,
                    'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                    'source_content_id': content_id,
                }
            )

            created_distributions.append({
                'distribution_id': str(distribution.id),
                'platform': account.platform.name,
                'status': distribution.status,
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
            })

            # Queue for processing if immediate
            if schedule_type == 'immediate':
                queue_distribution_task(distribution)

            # Schedule for later if scheduled/optimal
            elif scheduled_time:
                schedule_distribution_task(distribution, scheduled_time)

    return api_success({
        'message': f'Auto-distribution created for {len(created_distributions)} platforms',
        'distributions': created_distributions,
        'schedule_type': schedule_type,
        'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
    })


def calculate_optimal_posting_time(user, accounts) -> datetime:
    """
    Calculate optimal posting time based on historical performance.
    """
    # Get historical analytics
    analytics = DistributionAnalytics.objects.filter(
        user=user,
        platform__in=[a.platform for a in accounts],
        date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-total_sales')

    # Find best day/time patterns
    # For now, default to next day at 10 AM in user's timezone
    optimal_time = timezone.now().replace(
        hour=10, minute=0, second=0, microsecond=0
    ) + timedelta(days=1)

    # If we have analytics data, try to find the best time
    if analytics.exists():
        best_day = analytics.first().date
        # Use the same day of week for next occurrence
        days_ahead = (best_day.weekday() - timezone.now().weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        optimal_time = timezone.now().replace(
            hour=10, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_ahead)

    return optimal_time


def queue_distribution_task(distribution):
    """Queue a distribution for immediate processing via Celery."""
    try:
        from core.tasks import process_distribution
        process_distribution.delay(str(distribution.id))
        logger.info(f"Queued distribution {distribution.id} for processing")
    except Exception as e:
        logger.error(f"Failed to queue distribution {distribution.id}: {e}")


def schedule_distribution_task(distribution, scheduled_time):
    """Schedule a distribution for future processing via Celery."""
    try:
        from core.tasks import process_distribution
        process_distribution.apply_async(
            args=[str(distribution.id)],
            eta=scheduled_time
        )
        logger.info(f"Scheduled distribution {distribution.id} for {scheduled_time}")
    except Exception as e:
        logger.error(f"Failed to schedule distribution {distribution.id}: {e}")


# =============================================================================
# Batch Operations
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def batch_distribute(request):
    """
    POST /api/distribution/batch/

    Distribute multiple content items to multiple platforms.

    Request body:
    {
        "items": [
            {
                "content_type": "image",
                "image_history_id": "uuid1",
                "title": "Art 1",
                "tags": ["art"]
            },
            {
                "content_type": "image",
                "image_history_id": "uuid2",
                "title": "Art 2",
                "tags": ["art"]
            }
        ],
        "platforms": ["etsy", "gumroad"],
        "default_pricing": {
            "etsy": 29.99,
            "gumroad": 9.99
        },
        "schedule": {
            "type": "staggered",
            "interval_minutes": 30  // Space items 30 minutes apart
        }
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return api_error("Invalid JSON")

    items = data.get('items', [])
    if not items:
        return api_error("No items provided")

    if len(items) > 50:
        return api_error("Maximum 50 items per batch")

    # Get target platforms
    platforms = data.get('platforms', [])
    connected_accounts = UserPlatformAccount.objects.filter(
        user=request.user,
        account_status='active'
    ).select_related('platform')

    if platforms:
        target_accounts = [
            acc for acc in connected_accounts
            if acc.platform.name.lower() in [p.lower() for p in platforms]
        ]
    else:
        target_accounts = list(connected_accounts)

    if not target_accounts:
        return api_error("No matching connected platforms found")

    # Parse schedule
    schedule = data.get('schedule', {'type': 'immediate'})
    schedule_type = schedule.get('type', 'immediate')
    interval_minutes = schedule.get('interval_minutes', 0)

    # Default pricing
    default_pricing = data.get('default_pricing', {})

    # Create all distributions
    created_distributions = []
    base_time = timezone.now()

    with transaction.atomic():
        for item_idx, item in enumerate(items):
            # Calculate scheduled time for staggered distribution
            if schedule_type == 'staggered' and interval_minutes > 0:
                scheduled_time = base_time + timedelta(minutes=interval_minutes * item_idx)
            else:
                scheduled_time = None

            # Get content
            image = None
            video = None
            content_type = item.get('content_type', 'image')

            if content_type == 'image' and item.get('image_history_id'):
                from content.models import ImageHistory
                try:
                    image = ImageHistory.objects.get(id=item['image_history_id'])
                except ImageHistory.DoesNotExist:
                    continue  # Skip invalid items

            elif content_type == 'video' and item.get('video_history_id'):
                from content.models import VideoHistory
                try:
                    video = VideoHistory.objects.get(id=item['video_history_id'])
                except VideoHistory.DoesNotExist:
                    continue

            # Create distribution for each platform
            for account in target_accounts:
                platform_name = account.platform.name.lower()
                price = default_pricing.get(platform_name)
                if price is not None:
                    price = Decimal(str(price))

                distribution = ContentDistribution.objects.create(
                    user=request.user,
                    platform_account=account,
                    content_type=content_type,
                    image_history=image,
                    video_history=video,
                    title=item.get('title', f'Content {item_idx + 1}'),
                    description=item.get('description', ''),
                    tags=item.get('tags', []),
                    price=price,
                    status='pending',
                    platform_metadata={
                        'batch_distribution': True,
                        'batch_index': item_idx,
                        'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                    }
                )

                created_distributions.append({
                    'distribution_id': str(distribution.id),
                    'platform': account.platform.name,
                    'title': distribution.title,
                    'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                })

                # Queue or schedule
                if scheduled_time:
                    schedule_distribution_task(distribution, scheduled_time)
                else:
                    queue_distribution_task(distribution)

    return api_success({
        'message': f'Batch distribution created: {len(items)} items to {len(target_accounts)} platforms',
        'total_distributions': len(created_distributions),
        'distributions': created_distributions[:20],  # Return first 20
        'schedule_type': schedule_type,
    })


# =============================================================================
# Scheduling Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_scheduled_distributions(request):
    """
    GET /api/distribution/scheduled/

    List all scheduled (not yet published) distributions.
    """
    # Session 745: Return empty data for anonymous users instead of 401
    if not request.user.is_authenticated:
        return api_success({'scheduled_distributions': [], 'scheduled': [], 'total_pending': 0})

    distributions = ContentDistribution.objects.filter(
        user=request.user,
        status__in=['draft', 'pending'],
    ).select_related('platform_account__platform').order_by('platform_metadata__scheduled_time')

    scheduled = []
    for d in distributions:
        scheduled_time = d.platform_metadata.get('scheduled_time') if d.platform_metadata else None

        scheduled.append({
            'id': str(d.id),
            'title': d.title,
            'platform': d.platform_account.platform.name,
            'status': d.status,
            'scheduled_time': scheduled_time,
            'created_at': d.created_at.isoformat(),
        })

    return api_success({
        'scheduled_distributions': scheduled,
        'total_pending': len(scheduled),
    })


@csrf_exempt
@require_http_methods(["POST"])
def reschedule_distribution(request, distribution_id):
    """
    POST /api/distribution/<distribution_id>/reschedule/

    Reschedule a pending distribution.

    Request body:
    {
        "scheduled_time": "2025-11-28T10:00:00Z"
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    try:
        distribution = ContentDistribution.objects.get(
            id=distribution_id,
            user=request.user
        )
    except ContentDistribution.DoesNotExist:
        return api_error("Distribution not found", status_code=404)

    if distribution.status not in ['draft', 'pending']:
        return api_error("Can only reschedule draft or pending distributions")

    try:
        data = json.loads(request.body)
        new_time = datetime.fromisoformat(
            data['scheduled_time'].replace('Z', '+00:00')
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return api_error("Invalid scheduled_time")

    # Update metadata
    metadata = distribution.platform_metadata or {}
    metadata['scheduled_time'] = new_time.isoformat()
    metadata['rescheduled'] = True
    distribution.platform_metadata = metadata
    distribution.save()

    # Reschedule Celery task
    schedule_distribution_task(distribution, new_time)

    return api_success({
        'distribution_id': str(distribution.id),
        'new_scheduled_time': new_time.isoformat(),
        'message': 'Distribution rescheduled successfully'
    })


@csrf_exempt
@require_http_methods(["POST"])
def cancel_scheduled_distribution(request, distribution_id):
    """
    POST /api/distribution/<distribution_id>/cancel/

    Cancel a scheduled distribution.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    try:
        distribution = ContentDistribution.objects.get(
            id=distribution_id,
            user=request.user
        )
    except ContentDistribution.DoesNotExist:
        return api_error("Distribution not found", status_code=404)

    if distribution.status not in ['draft', 'pending']:
        return api_error("Can only cancel draft or pending distributions")

    # Update status
    distribution.status = 'removed'
    metadata = distribution.platform_metadata or {}
    metadata['cancelled'] = True
    metadata['cancelled_at'] = timezone.now().isoformat()
    distribution.platform_metadata = metadata
    distribution.save()

    # Note: Celery task will check status before processing

    return api_success({
        'distribution_id': str(distribution.id),
        'status': 'removed',
        'message': 'Distribution cancelled successfully'
    })


# =============================================================================
# Auto-Distribution Settings
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def auto_distribution_settings(request):
    """
    GET/POST /api/distribution/auto/settings/

    Manage auto-distribution settings for user's platforms.

    GET: Returns current settings
    POST: Updates settings

    Request body for POST:
    {
        "etsy": {
            "auto_upload": true,
            "default_price": 29.99,
            "default_tags": ["ai", "art"],
            "auto_renew": true
        },
        "gumroad": {
            "auto_upload": true,
            "default_price": 9.99,
            "auto_publish": false
        }
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    accounts = UserPlatformAccount.objects.filter(
        user=request.user,
        account_status='active'
    ).select_related('platform')

    if request.method == 'GET':
        settings_data = {}
        for account in accounts:
            platform_name = account.platform.name.lower()
            settings_data[platform_name] = {
                'auto_upload_enabled': account.auto_upload_enabled,
                'notification_settings': account.notification_settings,
                'platform_id': str(account.platform.id),
                'account_username': account.account_username,
            }

        return api_success({
            'settings': settings_data,
            'connected_platforms': [a.platform.name for a in accounts],
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return api_error("Invalid JSON")

        updated = []
        for account in accounts:
            platform_name = account.platform.name.lower()
            if platform_name in data:
                platform_settings = data[platform_name]

                if 'auto_upload' in platform_settings:
                    account.auto_upload_enabled = platform_settings['auto_upload']

                # Store other settings in notification_settings (we can expand this model later)
                notification_settings = account.notification_settings or {}
                notification_settings.update({
                    'default_price': platform_settings.get('default_price'),
                    'default_tags': platform_settings.get('default_tags', []),
                    'auto_publish': platform_settings.get('auto_publish', False),
                    'auto_renew': platform_settings.get('auto_renew', False),
                })
                account.notification_settings = notification_settings
                account.save()

                updated.append(platform_name)

        return api_success({
            'message': f'Settings updated for {len(updated)} platforms',
            'updated_platforms': updated,
        })


# =============================================================================
# Distribution Templates
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def distribution_templates(request):
    """
    GET /api/distribution/templates/

    Get predefined distribution templates for different content types.
    """
    templates = {
        'ai_art_print': {
            'name': 'AI Art Print',
            'description': 'Sell AI-generated art as prints',
            'platforms': ['etsy', 'redbubble', 'society6'],
            'suggested_pricing': {
                'etsy': {'min': 15, 'max': 50, 'recommended': 29.99},
                'redbubble': {'min': 20, 'max': 100, 'recommended': 35},
                'society6': {'min': 20, 'max': 100, 'recommended': 35},
            },
            'recommended_tags': ['ai art', 'digital art', 'wall art', 'home decor', 'modern art'],
            'best_for': ['images', 'illustrations'],
        },
        'digital_download': {
            'name': 'Digital Download Pack',
            'description': 'Sell downloadable digital assets',
            'platforms': ['gumroad', 'etsy', 'creative_market'],
            'suggested_pricing': {
                'gumroad': {'min': 5, 'max': 50, 'recommended': 9.99},
                'etsy': {'min': 3, 'max': 30, 'recommended': 7.99},
                'creative_market': {'min': 10, 'max': 100, 'recommended': 19},
            },
            'recommended_tags': ['digital download', 'instant download', 'digital art', 'graphics'],
            'best_for': ['images', 'templates', 'graphics'],
        },
        'stock_content': {
            'name': 'Stock Photo/Video',
            'description': 'License content through stock agencies',
            'platforms': ['shutterstock', 'adobe_stock', 'istock'],
            'suggested_pricing': {
                'shutterstock': {'note': 'Agency determines pricing'},
                'adobe_stock': {'note': 'Agency determines pricing'},
                'istock': {'note': 'Agency determines pricing'},
            },
            'recommended_tags': ['stock photo', 'commercial use', 'editorial'],
            'best_for': ['photos', 'videos', 'illustrations'],
            'notes': 'Content must meet editorial standards and be free of recognizable faces/brands without releases',
        },
        'nft_collection': {
            'name': 'NFT Collection',
            'description': 'Mint and sell as NFTs',
            'platforms': ['opensea'],
            'suggested_pricing': {
                'opensea': {'min': 0.01, 'max': 10, 'recommended': 0.05, 'currency': 'ETH'},
            },
            'recommended_tags': ['nft', 'crypto art', 'digital collectible', 'ai art'],
            'best_for': ['images', 'animations', 'video'],
            'notes': 'Requires crypto wallet setup',
        },
        'freelance_portfolio': {
            'name': 'Freelance Services',
            'description': 'Showcase for client work',
            'platforms': ['fiverr', 'upwork'],
            'suggested_pricing': {
                'fiverr': {'min': 5, 'max': 500, 'recommended': 50},
                'upwork': {'min': 20, 'max': 1000, 'recommended': 100, 'type': 'hourly/fixed'},
            },
            'recommended_tags': ['ai artist', 'digital artist', 'content creator'],
            'best_for': ['portfolio pieces', 'samples'],
        },
    }

    return api_success({
        'templates': templates,
        'total_templates': len(templates),
    })


@csrf_exempt
@require_http_methods(["POST"])
def apply_distribution_template(request):
    """
    POST /api/distribution/templates/apply/

    Apply a distribution template to create distributions.

    Request body:
    {
        "template": "ai_art_print",
        "content_type": "image",
        "image_history_id": "uuid",
        "title": "My AI Art",
        "description": "Beautiful AI artwork",
        "custom_pricing": {
            "etsy": 35.00
        }
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return api_error("Invalid JSON")

    template_name = data.get('template')
    templates = {
        'ai_art_print': ['etsy', 'redbubble', 'society6'],
        'digital_download': ['gumroad', 'etsy', 'creative_market'],
        'stock_content': ['shutterstock', 'adobe_stock', 'istock'],
        'nft_collection': ['opensea'],
        'freelance_portfolio': ['fiverr', 'upwork'],
    }

    if template_name not in templates:
        return api_error(f"Unknown template: {template_name}")

    # Use the auto_distribution endpoint with template platforms
    data['platforms'] = templates[template_name]

    # Simulate the request
    from django.test import RequestFactory
    factory = RequestFactory()
    new_request = factory.post(
        '/api/distribution/auto/create/',
        data=json.dumps(data),
        content_type='application/json'
    )
    new_request.user = request.user

    return create_auto_distribution(new_request)

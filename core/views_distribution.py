"""
Session 229: Smart Distribution - Phase 4 of Creative Intelligence Empire
Distribution platform integration and content placement APIs.
"""
import json
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from core.models_unified_system import (
    DistributionPlatform,
    UserPlatformAccount,
    ContentDistribution,
    DistributionRecommendation,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Platform Management APIs
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_platforms(request):
    """
    GET /api/distribution/platforms/
    List all distribution platforms with stats.
    """
    try:
        platforms = DistributionPlatform.objects.filter(is_active=True)

        platform_data = []
        for platform in platforms:
            # Get stats for this platform
            distributions = ContentDistribution.objects.filter(
                platform_account__platform=platform
            )

            platform_data.append({
                'id': str(platform.id),
                'name': platform.name,
                'platform_type': platform.platform_type,
                'platform_type_display': platform.get_platform_type_display(),
                'description': platform.description,
                'website_url': platform.website_url,
                'commission_percent': float(platform.commission_percent),
                'supported_content_types': platform.supported_content_types,
                'supported_formats': platform.supported_formats,
                'api_available': platform.api_available,
                'payment_threshold': float(platform.payment_threshold),
                'popularity_score': platform.popularity_score,
                'competition_level': platform.competition_level,
                'stats': {
                    'total_distributions': distributions.count(),
                    'live': distributions.filter(status='live').count(),
                    'total_views': distributions.aggregate(Sum('views'))['views__sum'] or 0,
                    'total_revenue': float(distributions.aggregate(Sum('revenue'))['revenue__sum'] or 0),
                }
            })

        return JsonResponse({
            'success': True,
            'platforms': platform_data,
            'count': len(platform_data)
        })

    except Exception as e:
        logger.error(f"Error listing platforms: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_platform(request):
    """
    POST /api/distribution/platforms/create/
    Create a new distribution platform.
    """
    try:
        data = json.loads(request.body)

        platform = DistributionPlatform.objects.create(
            name=data.get('name'),
            platform_type=data.get('platform_type', 'marketplace'),
            description=data.get('description', ''),
            website_url=data.get('website_url', ''),
            commission_percent=Decimal(str(data.get('commission_percent', 0))),
            supported_content_types=data.get('supported_content_types', []),
            supported_formats=data.get('supported_formats', []),
            api_available=data.get('api_available', False),
            api_documentation_url=data.get('api_documentation_url', ''),
            payment_threshold=Decimal(str(data.get('payment_threshold', 0))),
            popularity_score=data.get('popularity_score', 50),
            competition_level=data.get('competition_level', 'medium'),
        )

        return JsonResponse({
            'success': True,
            'platform': {
                'id': str(platform.id),
                'name': platform.name,
                'platform_type': platform.platform_type,
            },
            'message': f'Platform "{platform.name}" created successfully'
        })

    except Exception as e:
        logger.error(f"Error creating platform: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_platform(request, platform_id):
    """
    GET /api/distribution/platforms/<id>/
    Get platform details.
    """
    try:
        platform = DistributionPlatform.objects.get(id=platform_id)

        # Get all distributions on this platform
        distributions = ContentDistribution.objects.filter(
            platform_account__platform=platform
        ).order_by('-created_at')[:10]

        return JsonResponse({
            'success': True,
            'platform': {
                'id': str(platform.id),
                'name': platform.name,
                'platform_type': platform.platform_type,
                'platform_type_display': platform.get_platform_type_display(),
                'description': platform.description,
                'website_url': platform.website_url,
                'commission_percent': float(platform.commission_percent),
                'supported_content_types': platform.supported_content_types,
                'supported_formats': platform.supported_formats,
                'api_available': platform.api_available,
                'api_documentation_url': platform.api_documentation_url,
                'payment_threshold': float(platform.payment_threshold),
                'popularity_score': platform.popularity_score,
                'competition_level': platform.competition_level,
                'requires_approval': platform.requires_approval,
                'is_active': platform.is_active,
            },
            'recent_distributions': [
                {
                    'id': str(d.id),
                    'title': d.title,
                    'status': d.status,
                    'views': d.views,
                    'revenue': float(d.revenue),
                }
                for d in distributions
            ]
        })

    except DistributionPlatform.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Platform not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting platform: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# User Platform Account APIs
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_user_accounts(request):
    """
    GET /api/distribution/accounts/
    List user's connected platform accounts.
    """
    try:
        # Get all accounts (in production, filter by user)
        accounts = UserPlatformAccount.objects.select_related('platform').all()

        account_data = []
        for account in accounts:
            distributions = account.distributions.all()

            account_data.append({
                'id': str(account.id),
                'platform': {
                    'id': str(account.platform.id),
                    'name': account.platform.name,
                    'platform_type': account.platform.platform_type,
                },
                'account_username': account.account_username,
                'account_url': account.account_url,
                'account_status': account.account_status,
                'total_revenue': float(account.total_revenue),
                'total_sales': account.total_sales,
                'connected_at': account.created_at.isoformat(),
                'stats': {
                    'distributions': distributions.count(),
                    'live': distributions.filter(status='live').count(),
                    'pending': distributions.filter(status='pending').count(),
                }
            })

        return JsonResponse({
            'success': True,
            'accounts': account_data,
            'count': len(account_data)
        })

    except Exception as e:
        logger.error(f"Error listing accounts: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def connect_platform(request):
    """
    POST /api/distribution/accounts/connect/
    Connect a user's account to a distribution platform.
    """
    try:
        data = json.loads(request.body)

        platform = DistributionPlatform.objects.get(id=data.get('platform_id'))

        # Get user if authenticated, otherwise use first user for demo
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = request.user if request.user.is_authenticated else User.objects.first()

        account, created = UserPlatformAccount.objects.get_or_create(
            user=user,
            platform=platform,
            account_username=data.get('username', ''),
            defaults={
                'account_url': data.get('account_url', ''),
                'api_key': data.get('api_key', ''),
                'api_secret': data.get('api_secret', ''),
                'account_status': 'pending',
            }
        )

        if not created:
            # Update existing account
            account.account_url = data.get('account_url', account.account_url)
            if data.get('api_key'):
                account.api_key = data['api_key']
            if data.get('api_secret'):
                account.api_secret = data['api_secret']
            account.save()

        return JsonResponse({
            'success': True,
            'account': {
                'id': str(account.id),
                'platform': platform.name,
                'username': account.account_username,
                'account_status': account.account_status,
            },
            'created': created,
            'message': f'{"Connected to" if created else "Updated"} {platform.name}'
        })

    except DistributionPlatform.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Platform not found'}, status=404)
    except Exception as e:
        logger.error(f"Error connecting platform: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Content Distribution APIs
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_distributions(request):
    """
    GET /api/distribution/content/
    List all content distributions.
    """
    try:
        status_filter = request.GET.get('status')
        platform_filter = request.GET.get('platform')

        distributions = ContentDistribution.objects.select_related(
            'platform_account', 'platform_account__platform'
        ).order_by('-created_at')

        if status_filter:
            distributions = distributions.filter(status=status_filter)
        if platform_filter:
            distributions = distributions.filter(platform_account__platform_id=platform_filter)

        distribution_data = []
        for dist in distributions[:50]:  # Limit to 50
            distribution_data.append({
                'id': str(dist.id),
                'platform': {
                    'id': str(dist.platform_account.platform.id),
                    'name': dist.platform_account.platform.name,
                    'type': dist.platform_account.platform.platform_type,
                },
                'title': dist.title,
                'description': dist.description[:200] if dist.description else '',
                'content_type': dist.content_type,
                'status': dist.status,
                'status_display': dist.get_status_display(),
                'platform_listing_url': dist.platform_listing_url,
                'price': float(dist.price) if dist.price else None,
                'currency': dist.currency,
                'views': dist.views,
                'downloads': dist.downloads,
                'sales': dist.sales,
                'revenue': float(dist.revenue),
                'listed_at': dist.listed_at.isoformat() if dist.listed_at else None,
                'last_sale_at': dist.last_sale_at.isoformat() if dist.last_sale_at else None,
                'created_at': dist.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'distributions': distribution_data,
            'count': len(distribution_data)
        })

    except Exception as e:
        logger.error(f"Error listing distributions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_distribution(request):
    """
    POST /api/distribution/content/create/
    Create a new content distribution.
    """
    try:
        data = json.loads(request.body)

        account = UserPlatformAccount.objects.get(id=data.get('account_id'))

        # Get user if authenticated, otherwise use first user for demo
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = request.user if request.user.is_authenticated else User.objects.first()

        distribution = ContentDistribution.objects.create(
            user=user,
            platform_account=account,
            title=data.get('title'),
            description=data.get('description', ''),
            content_type=data.get('content_type', 'image'),
            price=Decimal(str(data.get('price', 0))) if data.get('price') else None,
            currency=data.get('currency', 'USD'),
            tags=data.get('tags', []),
            categories=data.get('categories', []),
            platform_metadata=data.get('metadata', {}),
            status='draft',
        )

        return JsonResponse({
            'success': True,
            'distribution': {
                'id': str(distribution.id),
                'title': distribution.title,
                'platform': account.platform.name,
                'status': distribution.status,
            },
            'message': f'Distribution "{distribution.title}" created'
        })

    except UserPlatformAccount.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating distribution: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_distribution(request, distribution_id):
    """
    POST /api/distribution/content/<id>/submit/
    Submit content for distribution (change status to pending).
    """
    try:
        distribution = ContentDistribution.objects.get(id=distribution_id)

        if distribution.status not in ['draft', 'rejected']:
            return JsonResponse({
                'success': False,
                'error': f'Cannot submit distribution with status: {distribution.status}'
            }, status=400)

        distribution.status = 'pending'
        distribution.save()

        return JsonResponse({
            'success': True,
            'distribution': {
                'id': str(distribution.id),
                'title': distribution.title,
                'status': distribution.status,
                'updated_at': distribution.updated_at.isoformat(),
            },
            'message': 'Distribution submitted for review'
        })

    except ContentDistribution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Distribution not found'}, status=404)
    except Exception as e:
        logger.error(f"Error submitting distribution: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def publish_distribution(request, distribution_id):
    """
    POST /api/distribution/content/<id>/publish/
    Mark content as published (simulate platform approval).
    """
    try:
        data = json.loads(request.body) if request.body else {}
        distribution = ContentDistribution.objects.get(id=distribution_id)

        distribution.status = 'live'  # Use 'live' as the model uses that instead of 'published'
        distribution.listed_at = timezone.now()
        if data.get('platform_listing_url'):
            distribution.platform_listing_url = data['platform_listing_url']
        if data.get('platform_listing_id'):
            distribution.platform_listing_id = data['platform_listing_id']
        distribution.save()

        return JsonResponse({
            'success': True,
            'distribution': {
                'id': str(distribution.id),
                'title': distribution.title,
                'status': distribution.status,
                'listed_at': distribution.listed_at.isoformat(),
                'listing_url': distribution.platform_listing_url,
            },
            'message': f'"{distribution.title}" is now live!'
        })

    except ContentDistribution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Distribution not found'}, status=404)
    except Exception as e:
        logger.error(f"Error publishing distribution: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def record_sale(request, distribution_id):
    """
    POST /api/distribution/content/<id>/sale/
    Record a sale for a distribution.
    """
    try:
        data = json.loads(request.body)
        distribution = ContentDistribution.objects.get(id=distribution_id)

        sale_amount = Decimal(str(data.get('amount', distribution.price or 0)))

        # Update distribution stats
        distribution.sales += 1
        distribution.revenue += sale_amount
        distribution.save()

        # Update account stats
        account = distribution.platform_account
        account.total_sales += 1
        account.total_revenue += sale_amount
        account.save()

        return JsonResponse({
            'success': True,
            'sale': {
                'distribution_id': str(distribution.id),
                'amount': float(sale_amount),
                'total_sales': distribution.sales,
                'total_revenue': float(distribution.revenue),
            },
            'message': f'Sale recorded: ${sale_amount}'
        })

    except ContentDistribution.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Distribution not found'}, status=404)
    except Exception as e:
        logger.error(f"Error recording sale: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Distribution Recommendations APIs
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_recommendations(request):
    """
    GET/POST /api/distribution/recommendations/
    Get AI-powered distribution recommendations for content.

    Session 745: Added GET support for frontend compatibility.
    """
    try:
        # Support both GET (query params) and POST (body)
        if request.method == 'GET':
            content_type = request.GET.get('content_type', 'image')
            tags = request.GET.getlist('tags', [])
            style = request.GET.get('style', '')
        else:
            data = json.loads(request.body) if request.body else {}
            content_type = data.get('content_type', 'image')
            tags = data.get('tags', [])
            style = data.get('style', '')

        # Get platforms that support this content type
        platforms = DistributionPlatform.objects.filter(
            is_active=True,
            supported_content_types__contains=[content_type]
        )

        recommendations = []
        for platform in platforms:
            # Calculate confidence based on match
            confidence = 0.5  # Base confidence

            # Boost for matching content type
            if content_type in platform.supported_content_types:
                confidence += 0.2

            # Boost for low commission
            if platform.commission_percent < 20:
                confidence += 0.1

            # Boost for API availability (easier to integrate)
            if platform.api_available:
                confidence += 0.1

            # Suggest price based on platform type
            suggested_price = None
            if platform.platform_type == 'stock':
                suggested_price = 15.00  # Stock photo typical price
            elif platform.platform_type == 'marketplace':
                suggested_price = 25.00  # Marketplace item price
            elif platform.platform_type == 'print_on_demand':
                suggested_price = 20.00  # POD margin
            elif platform.platform_type == 'nft':
                suggested_price = 50.00  # NFT floor price

            recommendations.append({
                'platform': {
                    'id': str(platform.id),
                    'name': platform.name,
                    'type': platform.platform_type,
                    'commission': float(platform.commission_percent),
                },
                'recommendation_type': 'platform_match',
                'confidence_score': min(confidence, 1.0),
                'suggested_price': suggested_price,
                'reasoning': f"{platform.name} is a good fit for {content_type} content with {platform.commission_percent}% commission",
                'estimated_revenue_potential': suggested_price * (1 - float(platform.commission_percent) / 100) if suggested_price else None,
            })

        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)

        # Save recommendations to database (skip metadata field if not supported)
        for rec in recommendations[:5]:  # Top 5
            try:
                DistributionRecommendation.objects.create(
                    platform_id=rec['platform']['id'],
                    content_type=content_type,
                    recommendation_type='platform_match',
                    confidence_score=Decimal(str(rec['confidence_score'])),
                    suggested_price=Decimal(str(rec['suggested_price'])) if rec['suggested_price'] else None,
                    reasoning=rec['reasoning'],
                )
            except Exception:
                pass  # Skip saving if model fields don't match

        return JsonResponse({
            'success': True,
            'recommendations': recommendations[:5],
            'content_type': content_type,
            'total_platforms_analyzed': len(platforms),
        })

    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Distribution Analytics APIs
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def distribution_stats(request):
    """
    GET /api/distribution/stats/
    Get overall distribution statistics.
    """
    try:
        # Overall stats
        total_distributions = ContentDistribution.objects.count()
        live = ContentDistribution.objects.filter(status='live').count()
        pending = ContentDistribution.objects.filter(status='pending').count()

        # Revenue stats
        revenue_stats = ContentDistribution.objects.aggregate(
            total_revenue=Sum('revenue'),
            total_views=Sum('views'),
            total_downloads=Sum('downloads'),
            total_sales=Sum('sales'),
        )

        # Platform breakdown
        platform_breakdown = []
        platforms = DistributionPlatform.objects.filter(is_active=True)
        for platform in platforms:
            dists = ContentDistribution.objects.filter(
                platform_account__platform=platform
            )
            platform_breakdown.append({
                'platform': platform.name,
                'platform_type': platform.platform_type,
                'distributions': dists.count(),
                'revenue': float(dists.aggregate(Sum('revenue'))['revenue__sum'] or 0),
            })

        # Recent activity
        recent = ContentDistribution.objects.order_by('-updated_at')[:5]
        recent_activity = [
            {
                'id': str(d.id),
                'title': d.title,
                'platform': d.platform_account.platform.name,
                'status': d.status,
                'updated_at': d.updated_at.isoformat(),
            }
            for d in recent
        ]

        return JsonResponse({
            'success': True,
            'stats': {
                'total_distributions': total_distributions,
                'live': live,
                'pending': pending,
                'draft': ContentDistribution.objects.filter(status='draft').count(),
                'total_revenue': float(revenue_stats['total_revenue'] or 0),
                'total_views': revenue_stats['total_views'] or 0,
                'total_downloads': revenue_stats['total_downloads'] or 0,
                'total_sales': revenue_stats['total_sales'] or 0,
            },
            'platform_breakdown': platform_breakdown,
            'recent_activity': recent_activity,
            'connected_platforms': UserPlatformAccount.objects.filter(account_status='active').count(),
        })

    except Exception as e:
        logger.error(f"Error getting distribution stats: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def platform_analytics(request, platform_id):
    """
    GET /api/distribution/analytics/<platform_id>/
    Get detailed analytics for a specific platform.
    """
    try:
        platform = DistributionPlatform.objects.get(id=platform_id)

        # Get all distributions for this platform
        distributions = ContentDistribution.objects.filter(
            platform_account__platform=platform
        )

        # Time-based analytics (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_dists = distributions.filter(created_at__gte=thirty_days_ago)

        # Content type breakdown
        content_breakdown = distributions.values('content_type').annotate(
            count=Count('id'),
            revenue=Sum('revenue'),
        )

        # Top performers
        top_performers = distributions.filter(
            status='live'
        ).order_by('-revenue')[:5]

        return JsonResponse({
            'success': True,
            'platform': {
                'id': str(platform.id),
                'name': platform.name,
                'type': platform.platform_type,
            },
            'analytics': {
                'total_distributions': distributions.count(),
                'live': distributions.filter(status='live').count(),
                'total_revenue': float(distributions.aggregate(Sum('revenue'))['revenue__sum'] or 0),
                'total_views': distributions.aggregate(Sum('views'))['views__sum'] or 0,
                'total_sales': distributions.aggregate(Sum('sales'))['sales__sum'] or 0,
                'avg_price': float(distributions.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0),
            },
            'last_30_days': {
                'new_distributions': recent_dists.count(),
                'revenue': float(recent_dists.aggregate(Sum('revenue'))['revenue__sum'] or 0),
            },
            'content_breakdown': list(content_breakdown),
            'top_performers': [
                {
                    'id': str(d.id),
                    'title': d.title,
                    'revenue': float(d.revenue),
                    'sales': d.sales,
                    'views': d.views,
                }
                for d in top_performers
            ],
        })

    except DistributionPlatform.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Platform not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Seed Default Platforms
# =============================================================================

def seed_distribution_platforms():
    """
    Seed default distribution platforms.
    Called during setup or migrations.
    """
    platforms = [
        # Marketplaces
        {
            'name': 'Etsy',
            'platform_type': 'marketplace',
            'description': 'Global marketplace for creative goods',
            'website_url': 'https://etsy.com',
            'commission_percent': Decimal('6.5'),
            'supported_content_types': ['image', 'design', 'template', 'printable'],
            'supported_formats': ['png', 'jpg', 'pdf', 'svg'],
            'api_available': True,
            'payment_threshold': Decimal('25'),
            'popularity_score': 90,
            'competition_level': 'high',
        },
        {
            'name': 'Creative Market',
            'platform_type': 'marketplace',
            'description': 'Design assets marketplace',
            'website_url': 'https://creativemarket.com',
            'commission_percent': Decimal('40'),
            'supported_content_types': ['design', 'template', 'font', 'graphics'],
            'supported_formats': ['png', 'ai', 'psd', 'sketch', 'svg'],
            'api_available': False,
            'payment_threshold': Decimal('20'),
            'popularity_score': 85,
            'competition_level': 'medium',
        },
        {
            'name': 'Gumroad',
            'platform_type': 'marketplace',
            'description': 'Direct-to-creator sales platform',
            'website_url': 'https://gumroad.com',
            'commission_percent': Decimal('10'),
            'supported_content_types': ['image', 'video', 'design', 'template', 'ebook', 'course'],
            'supported_formats': ['png', 'jpg', 'mp4', 'pdf', 'zip'],
            'api_available': True,
            'payment_threshold': Decimal('10'),
            'popularity_score': 80,
            'competition_level': 'medium',
        },
        # Stock Content
        {
            'name': 'Shutterstock',
            'platform_type': 'stock',
            'description': 'Leading stock content marketplace',
            'website_url': 'https://shutterstock.com',
            'commission_percent': Decimal('70'),
            'supported_content_types': ['image', 'video', 'music'],
            'supported_formats': ['jpg', 'png', 'eps', 'mp4'],
            'api_available': True,
            'requires_approval': True,
            'payment_threshold': Decimal('35'),
            'popularity_score': 95,
            'competition_level': 'very_high',
            'avg_earnings_per_item': Decimal('0.25'),
        },
        {
            'name': 'Adobe Stock',
            'platform_type': 'stock',
            'description': 'Adobe integrated stock marketplace',
            'website_url': 'https://stock.adobe.com',
            'commission_percent': Decimal('67'),
            'supported_content_types': ['image', 'video', 'template', '3d'],
            'supported_formats': ['jpg', 'png', 'ai', 'psd', 'mp4'],
            'api_available': True,
            'requires_approval': True,
            'payment_threshold': Decimal('25'),
            'popularity_score': 90,
            'competition_level': 'high',
            'avg_earnings_per_item': Decimal('0.33'),
        },
        {
            'name': 'iStock',
            'platform_type': 'stock',
            'description': 'Getty Images stock content',
            'website_url': 'https://istockphoto.com',
            'commission_percent': Decimal('75'),
            'supported_content_types': ['image', 'video', 'audio'],
            'supported_formats': ['jpg', 'png', 'eps', 'mp4', 'mp3'],
            'api_available': True,
            'requires_approval': True,
            'payment_threshold': Decimal('100'),
            'popularity_score': 85,
            'competition_level': 'very_high',
            'avg_earnings_per_item': Decimal('0.20'),
        },
        # Print on Demand
        {
            'name': 'Redbubble',
            'platform_type': 'print_on_demand',
            'description': 'Print-on-demand products',
            'website_url': 'https://redbubble.com',
            'commission_percent': Decimal('80'),
            'supported_content_types': ['design', 'artwork', 'illustration'],
            'supported_formats': ['png', 'jpg'],
            'api_available': False,
            'payment_threshold': Decimal('20'),
            'popularity_score': 75,
            'competition_level': 'high',
            'avg_earnings_per_item': Decimal('2.00'),
        },
        {
            'name': 'Society6',
            'platform_type': 'print_on_demand',
            'description': 'Art prints and home decor',
            'website_url': 'https://society6.com',
            'commission_percent': Decimal('90'),
            'supported_content_types': ['artwork', 'design', 'illustration'],
            'supported_formats': ['png', 'jpg'],
            'api_available': False,
            'payment_threshold': Decimal('10'),
            'popularity_score': 70,
            'competition_level': 'medium',
            'avg_earnings_per_item': Decimal('1.50'),
        },
        {
            'name': 'Printful',
            'platform_type': 'print_on_demand',
            'description': 'Custom print products with integration',
            'website_url': 'https://printful.com',
            'commission_percent': Decimal('0'),  # No commission, you set markup
            'supported_content_types': ['design', 'artwork'],
            'supported_formats': ['png', 'jpg', 'svg'],
            'api_available': True,
            'payment_threshold': Decimal('25'),
            'popularity_score': 80,
            'competition_level': 'low',
        },
        # Social Media
        {
            'name': 'Instagram',
            'platform_type': 'social',
            'description': 'Visual content social platform',
            'website_url': 'https://instagram.com',
            'commission_percent': Decimal('0'),
            'supported_content_types': ['image', 'video', 'reel'],
            'supported_formats': ['jpg', 'png', 'mp4'],
            'api_available': True,
            'payment_threshold': Decimal('0'),
            'popularity_score': 95,
            'competition_level': 'very_high',
        },
        {
            'name': 'TikTok',
            'platform_type': 'social',
            'description': 'Short-form video platform',
            'website_url': 'https://tiktok.com',
            'commission_percent': Decimal('0'),
            'supported_content_types': ['video', 'short_video'],
            'supported_formats': ['mp4', 'mov'],
            'api_available': True,
            'payment_threshold': Decimal('50'),
            'popularity_score': 98,
            'competition_level': 'very_high',
        },
        # NFT
        {
            'name': 'OpenSea',
            'platform_type': 'nft',
            'description': 'Largest NFT marketplace',
            'website_url': 'https://opensea.io',
            'commission_percent': Decimal('2.5'),
            'supported_content_types': ['nft', 'artwork', 'collectible'],
            'supported_formats': ['png', 'jpg', 'gif', 'mp4', 'mp3', 'glb'],
            'api_available': True,
            'payment_threshold': Decimal('0'),
            'popularity_score': 85,
            'competition_level': 'high',
        },
        # Freelance
        {
            'name': 'Fiverr',
            'platform_type': 'freelance',
            'description': 'Freelance services marketplace',
            'website_url': 'https://fiverr.com',
            'commission_percent': Decimal('20'),
            'supported_content_types': ['service', 'design', 'video', 'audio'],
            'supported_formats': ['any'],
            'api_available': False,
            'payment_threshold': Decimal('50'),
            'popularity_score': 90,
            'competition_level': 'very_high',
        },
        {
            'name': 'Upwork',
            'platform_type': 'freelance',
            'description': 'Professional freelance platform',
            'website_url': 'https://upwork.com',
            'commission_percent': Decimal('10'),
            'supported_content_types': ['service', 'project'],
            'supported_formats': ['any'],
            'api_available': True,
            'payment_threshold': Decimal('100'),
            'popularity_score': 88,
            'competition_level': 'high',
        },
    ]

    created_count = 0
    for platform_data in platforms:
        platform, created = DistributionPlatform.objects.get_or_create(
            name=platform_data['name'],
            defaults=platform_data
        )
        if created:
            created_count += 1
            logger.info(f"Created distribution platform: {platform.name}")

    return created_count


@csrf_exempt
@require_http_methods(["POST"])
def seed_platforms_api(request):
    """
    POST /api/distribution/seed/
    Seed default distribution platforms.
    """
    try:
        created_count = seed_distribution_platforms()
        total_count = DistributionPlatform.objects.count()

        return JsonResponse({
            'success': True,
            'created': created_count,
            'total_platforms': total_count,
            'message': f'Seeded {created_count} new platforms. Total: {total_count}'
        })

    except Exception as e:
        logger.error(f"Error seeding platforms: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

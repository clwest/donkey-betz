"""
Session 230: Platform API Integrations
=====================================

This module implements OAuth and API integrations for distribution platforms:
- Etsy OAuth 2.0 integration
- Shutterstock Contributor API
- Gumroad upload API
- Generic platform integration framework

Each platform integration supports:
- OAuth authentication flow
- Token refresh
- Content upload
- Listing management
- Revenue/sales tracking
"""

import os
import json
import logging
import hashlib
import hmac
import base64
import time
from datetime import timedelta
from decimal import Decimal
from urllib.parse import urlencode

from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from core.models_unified_system import (
    DistributionPlatform,
    UserPlatformAccount,
    ContentDistribution,
)
from core.api_responses import api_success
from core.security.error_envelope import emit_error_envelope

logger = logging.getLogger(__name__)


# =============================================================================
# Platform Configuration
# =============================================================================

PLATFORM_CONFIGS = {
    'etsy': {
        'name': 'Etsy',
        'auth_url': 'https://www.etsy.com/oauth/connect',
        'token_url': 'https://api.etsy.com/v3/public/oauth/token',
        'api_base': 'https://openapi.etsy.com/v3',
        'scopes': ['listings_r', 'listings_w', 'shops_r', 'transactions_r'],
        'required_env': ['ETSY_CLIENT_ID', 'ETSY_CLIENT_SECRET'],
    },
    'shutterstock': {
        'name': 'Shutterstock',
        'auth_url': 'https://api.shutterstock.com/v2/oauth/authorize',
        'token_url': 'https://api.shutterstock.com/v2/oauth/access_token',
        'api_base': 'https://api.shutterstock.com/v2',
        'scopes': ['collections.view', 'collections.edit', 'user.view'],
        'required_env': ['SHUTTERSTOCK_CLIENT_ID', 'SHUTTERSTOCK_CLIENT_SECRET'],
    },
    'gumroad': {
        'name': 'Gumroad',
        'auth_url': 'https://gumroad.com/oauth/authorize',
        'token_url': 'https://api.gumroad.com/oauth/token',
        'api_base': 'https://api.gumroad.com/v2',
        'scopes': ['view_sales', 'edit_products'],
        'required_env': ['GUMROAD_CLIENT_ID', 'GUMROAD_CLIENT_SECRET'],
    },
    'creative_market': {
        'name': 'Creative Market',
        'api_base': 'https://api.creativemarket.com/v2',
        'auth_type': 'api_key',
        'required_env': ['CREATIVE_MARKET_API_KEY'],
    },
    'adobe_stock': {
        'name': 'Adobe Stock',
        'auth_url': 'https://ims-na1.adobelogin.com/ims/authorize/v2',
        'token_url': 'https://ims-na1.adobelogin.com/ims/token/v3',
        'api_base': 'https://stock.adobe.io/Rest',
        'scopes': ['openid', 'AdobeID', 'stock_contributor_sdk'],
        'required_env': ['ADOBE_CLIENT_ID', 'ADOBE_CLIENT_SECRET'],
    },
}


# =============================================================================
# OAuth Flow Helpers
# =============================================================================

def generate_state_token(user_id, platform):
    """Generate a secure state token for OAuth flow."""
    secret = getattr(settings, 'SECRET_KEY', 'default-secret-key')
    timestamp = str(int(time.time()))
    data = f"{user_id}:{platform}:{timestamp}"
    signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:16]
    return base64.urlsafe_b64encode(f"{data}:{signature}".encode()).decode()


def verify_state_token(state_token, max_age_seconds=600):
    """Verify a state token and extract user_id and platform."""
    try:
        secret = getattr(settings, 'SECRET_KEY', 'default-secret-key')
        decoded = base64.urlsafe_b64decode(state_token.encode()).decode()
        parts = decoded.rsplit(':', 3)
        if len(parts) != 4:
            return None, None

        user_id, platform, timestamp, signature = parts

        # Verify timestamp
        if int(time.time()) - int(timestamp) > max_age_seconds:
            return None, None

        # Verify signature
        data = f"{user_id}:{platform}:{timestamp}"
        expected_signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]

        if not hmac.compare_digest(signature, expected_signature):
            return None, None

        return int(user_id), platform
    except Exception as e:
        logger.error(f"State token verification failed: {e}")
        return None, None


def get_platform_credentials(platform):
    """Get OAuth credentials for a platform from environment."""
    config = PLATFORM_CONFIGS.get(platform, {})
    creds = {}

    for env_var in config.get('required_env', []):
        value = os.environ.get(env_var)
        if value:
            key_name = env_var.split('_')[-1].lower()
            if 'CLIENT_ID' in env_var:
                creds['client_id'] = value
            elif 'CLIENT_SECRET' in env_var:
                creds['client_secret'] = value
            elif 'API_KEY' in env_var:
                creds['api_key'] = value

    return creds


# =============================================================================
# OAuth Initiation Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def oauth_connect(request, platform):
    """
    GET /api/distribution/oauth/<platform>/connect/

    Initiates OAuth flow for a platform.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'oauth_connect'},
        )

    if platform not in PLATFORM_CONFIGS:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'oauth_connect', 'reason': 'unsupported_platform', 'platform': platform},
        )

    config = PLATFORM_CONFIGS[platform]
    creds = get_platform_credentials(platform)

    if not creds.get('client_id'):
        return emit_error_envelope(
            reason_code='unavailable',
            request=request,
            hint={'source': 'oauth_connect', 'reason': 'platform_not_configured', 'platform': platform},
        )

    # Generate state token
    state = generate_state_token(request.user.id, platform)

    # Build redirect URI
    redirect_uri = request.build_absolute_uri(f'/api/distribution/oauth/{platform}/callback/')

    # Build authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': creds['client_id'],
        'redirect_uri': redirect_uri,
        'state': state,
        'scope': ' '.join(config.get('scopes', [])),
    }

    # Platform-specific params
    if platform == 'etsy':
        # Etsy uses PKCE
        import secrets
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')

        auth_params['code_challenge'] = code_challenge
        auth_params['code_challenge_method'] = 'S256'

        # Store code verifier in session
        request.session[f'{platform}_code_verifier'] = code_verifier

    auth_url = f"{config['auth_url']}?{urlencode(auth_params)}"

    return api_success({
        'auth_url': auth_url,
        'platform': platform,
        'message': f'Redirect user to auth_url to complete {config["name"]} authorization'
    })


@csrf_exempt
@require_http_methods(["GET"])
def oauth_callback(request, platform):
    """
    GET /api/distribution/oauth/<platform>/callback/

    Handles OAuth callback and exchanges code for tokens.
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    if error:
        return emit_error_envelope(
            reason_code='validation_error',
            request=request,
            hint={'source': 'oauth_callback', 'reason': 'oauth_provider_error', 'platform': platform, 'error': error},
        )

    if not code or not state:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'oauth_callback', 'reason': 'missing_code_or_state'},
        )

    # Verify state token
    user_id, verified_platform = verify_state_token(state)
    if not user_id or verified_platform != platform:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'oauth_callback', 'reason': 'invalid_state_token'},
        )

    config = PLATFORM_CONFIGS.get(platform)
    creds = get_platform_credentials(platform)

    if not config or not creds.get('client_id'):
        return emit_error_envelope(
            reason_code='unavailable',
            request=request,
            hint={'source': 'oauth_callback', 'reason': 'platform_not_configured', 'platform': platform},
        )

    # Exchange code for tokens
    redirect_uri = request.build_absolute_uri(f'/api/distribution/oauth/{platform}/callback/')

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
    }

    # Platform-specific token exchange
    if platform == 'etsy':
        code_verifier = request.session.get(f'{platform}_code_verifier')
        if code_verifier:
            token_data['code_verifier'] = code_verifier

    try:
        import requests as http_requests

        response = http_requests.post(
            config['token_url'],
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'oauth_callback',
                    'reason': 'token_exchange_failed',
                    'platform': platform,
                    'upstream_status': response.status_code,
                },
            )

        tokens = response.json()

        # Get or create platform record
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)

        platform_obj = DistributionPlatform.objects.filter(
            name__icontains=config['name']
        ).first()

        if not platform_obj:
            return emit_error_envelope(
                reason_code='internal_error',
                request=request,
                hint={
                    'source': 'oauth_callback',
                    'reason': 'platform_missing_in_db',
                    'platform_name': config['name'],
                },
            )

        # Save tokens to user account
        account, created = UserPlatformAccount.objects.update_or_create(
            user=user,
            platform=platform_obj,
            defaults={
                'access_token': tokens.get('access_token', ''),
                'refresh_token': tokens.get('refresh_token', ''),
                'token_expires_at': timezone.now() + timedelta(
                    seconds=tokens.get('expires_in', 3600)
                ),
                'account_status': 'active',
            }
        )

        # Fetch user info from platform
        user_info = fetch_platform_user_info(platform, tokens.get('access_token'))
        if user_info:
            account.account_username = user_info.get('username', '')
            account.account_url = user_info.get('profile_url', '')
            account.save()

        # Redirect to success page
        return redirect(f'/ai-studio/?oauth_success={platform}')

    except Exception as e:
        logger.exception(f"OAuth callback error for {platform}: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'oauth_callback',
                'reason': 'oauth_unhandled_exception',
                'platform': platform,
                'exc_type': type(e).__name__,
            },
        )


def fetch_platform_user_info(platform, access_token):
    """Fetch user info from platform API."""
    config = PLATFORM_CONFIGS.get(platform)
    if not config:
        return None

    try:
        import requests as http_requests

        headers = {'Authorization': f'Bearer {access_token}'}

        if platform == 'etsy':
            response = http_requests.get(
                f"{config['api_base']}/application/users/me",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'username': data.get('login_name', ''),
                    'profile_url': f"https://www.etsy.com/shop/{data.get('shop_name', '')}",
                }

        elif platform == 'shutterstock':
            response = http_requests.get(
                f"{config['api_base']}/user",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'username': data.get('username', ''),
                    'profile_url': f"https://www.shutterstock.com/g/{data.get('contributor', {}).get('id', '')}",
                }

        elif platform == 'gumroad':
            response = http_requests.get(
                f"{config['api_base']}/user",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json().get('user', {})
                return {
                    'username': data.get('name', ''),
                    'profile_url': data.get('profile_url', ''),
                }

    except Exception as e:
        logger.error(f"Error fetching user info from {platform}: {e}")

    return None


# =============================================================================
# Token Management
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request, platform):
    """
    POST /api/distribution/oauth/<platform>/refresh/

    Refresh OAuth tokens for a platform.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'refresh_token'},
        )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains=platform
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'refresh_token', 'reason': 'no_account_connected', 'platform': platform},
        )

    if not account.refresh_token:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'refresh_token', 'reason': 'no_refresh_token', 'platform': platform},
        )

    config = PLATFORM_CONFIGS.get(platform)
    creds = get_platform_credentials(platform)

    if not config or not creds.get('client_id'):
        return emit_error_envelope(
            reason_code='unavailable',
            request=request,
            hint={'source': 'refresh_token', 'reason': 'platform_not_configured', 'platform': platform},
        )

    try:
        import requests as http_requests

        response = http_requests.post(
            config['token_url'],
            data={
                'grant_type': 'refresh_token',
                'refresh_token': account.refresh_token,
                'client_id': creds['client_id'],
                'client_secret': creds['client_secret'],
            }
        )

        if response.status_code != 200:
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'refresh_token',
                    'reason': 'refresh_upstream_failed',
                    'platform': platform,
                    'upstream_status': response.status_code,
                },
            )

        tokens = response.json()

        account.access_token = tokens.get('access_token', account.access_token)
        if tokens.get('refresh_token'):
            account.refresh_token = tokens['refresh_token']
        account.token_expires_at = timezone.now() + timedelta(
            seconds=tokens.get('expires_in', 3600)
        )
        account.save()

        return api_success({
            'message': 'Token refreshed successfully',
            'expires_at': account.token_expires_at.isoformat()
        })

    except Exception as e:
        logger.exception(f"Token refresh error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'refresh_token',
                'reason': 'refresh_unhandled_exception',
                'platform': platform,
                'exc_type': type(e).__name__,
            },
        )


# =============================================================================
# Etsy Integration
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def etsy_get_shop(request):
    """
    GET /api/distribution/etsy/shop/

    Get user's Etsy shop information.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'etsy_get_shop'},
        )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains='Etsy',
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'etsy_get_shop', 'reason': 'no_active_account', 'platform': 'etsy'},
        )

    try:
        import requests as http_requests

        config = PLATFORM_CONFIGS['etsy']
        creds = get_platform_credentials('etsy')

        headers = {
            'Authorization': f'Bearer {account.access_token}',
            'x-api-key': creds.get('client_id', ''),
        }

        # Get user's shops
        response = http_requests.get(
            f"{config['api_base']}/application/users/me/shops",
            headers=headers
        )

        if response.status_code == 401:
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'etsy_get_shop', 'reason': 'token_expired', 'platform': 'etsy'},
            )

        if response.status_code != 200:
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'etsy_get_shop',
                    'reason': 'upstream_error',
                    'platform': 'etsy',
                    'upstream_status': response.status_code,
                },
            )

        data = response.json()
        shops = data.get('results', [])

        return api_success({
            'shops': [{
                'shop_id': shop.get('shop_id'),
                'shop_name': shop.get('shop_name'),
                'title': shop.get('title'),
                'currency_code': shop.get('currency_code'),
                'listing_count': shop.get('listing_active_count', 0),
                'url': shop.get('url'),
            } for shop in shops]
        })

    except Exception as e:
        logger.exception(f"Etsy shop fetch error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'etsy_get_shop',
                'reason': 'unhandled_exception',
                'exc_type': type(e).__name__,
            },
        )


@csrf_exempt
@require_http_methods(["POST"])
def etsy_create_listing(request):
    """
    POST /api/distribution/etsy/listings/create/

    Create a new listing on Etsy.

    Request body:
    {
        "shop_id": "12345",
        "title": "AI Generated Art Print",
        "description": "Beautiful AI-generated artwork...",
        "price": 29.99,
        "quantity": 100,
        "tags": ["art", "ai", "digital"],
        "image_history_id": "uuid",  // Optional - link to our content
        "materials": ["digital"],
        "who_made": "i_did",
        "when_made": "2020_2025",
        "taxonomy_id": 1  // Etsy category ID
    }
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'etsy_create_listing'},
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'etsy_create_listing', 'reason': 'json_decode_error'},
        )

    required_fields = ['shop_id', 'title', 'description', 'price', 'quantity']
    for field in required_fields:
        if field not in data:
            return emit_error_envelope(
                reason_code='invalid_input',
                request=request,
                hint={'source': 'etsy_create_listing', 'reason': 'missing_field', 'field': field},
            )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains='Etsy',
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'etsy_create_listing', 'reason': 'no_active_account', 'platform': 'etsy'},
        )

    try:
        import requests as http_requests

        config = PLATFORM_CONFIGS['etsy']
        creds = get_platform_credentials('etsy')

        headers = {
            'Authorization': f'Bearer {account.access_token}',
            'x-api-key': creds.get('client_id', ''),
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        listing_data = {
            'title': data['title'],
            'description': data['description'],
            'price': float(data['price']),
            'quantity': int(data['quantity']),
            'who_made': data.get('who_made', 'i_did'),
            'when_made': data.get('when_made', '2020_2025'),
            'taxonomy_id': data.get('taxonomy_id', 1),
            'tags': ','.join(data.get('tags', []))[:13],  # Etsy max 13 tags
        }

        if data.get('materials'):
            listing_data['materials'] = ','.join(data['materials'])

        response = http_requests.post(
            f"{config['api_base']}/application/shops/{data['shop_id']}/listings",
            headers=headers,
            data=listing_data
        )

        if response.status_code == 401:
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'etsy_create_listing', 'reason': 'token_expired', 'platform': 'etsy'},
            )

        if response.status_code not in [200, 201]:
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'etsy_create_listing',
                    'reason': 'upstream_error',
                    'platform': 'etsy',
                    'upstream_status': response.status_code,
                },
            )

        etsy_listing = response.json()

        # Create ContentDistribution record
        distribution = ContentDistribution.objects.create(
            user=request.user,
            platform_account=account,
            content_type='image',
            title=data['title'],
            description=data['description'],
            price=Decimal(str(data['price'])),
            tags=data.get('tags', []),
            platform_listing_id=str(etsy_listing.get('listing_id', '')),
            platform_listing_url=etsy_listing.get('url', ''),
            platform_metadata=etsy_listing,
            status='live' if etsy_listing.get('state') == 'active' else 'pending',
            listed_at=timezone.now() if etsy_listing.get('state') == 'active' else None,
        )

        # Link to image history if provided
        if data.get('image_history_id'):
            from content.models import ImageHistory
            try:
                image = ImageHistory.objects.get(id=data['image_history_id'])
                distribution.image_history = image
                distribution.save()
            except ImageHistory.DoesNotExist:
                pass

        # Update account stats
        account.total_items_listed += 1
        account.save()

        return api_success({
            'listing_id': str(etsy_listing.get('listing_id', '')),
            'distribution_id': str(distribution.id),
            'url': etsy_listing.get('url', ''),
            'state': etsy_listing.get('state', 'draft'),
            'message': 'Listing created successfully'
        })

    except Exception as e:
        logger.exception(f"Etsy listing creation error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'etsy_create_listing',
                'reason': 'unhandled_exception',
                'exc_type': type(e).__name__,
            },
        )


# =============================================================================
# Shutterstock Integration
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def shutterstock_get_portfolio(request):
    """
    GET /api/distribution/shutterstock/portfolio/

    Get user's Shutterstock contributor portfolio.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'shutterstock_get_portfolio'},
        )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains='Shutterstock',
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'shutterstock_get_portfolio', 'reason': 'no_active_account', 'platform': 'shutterstock'},
        )

    try:
        import requests as http_requests

        config = PLATFORM_CONFIGS['shutterstock']

        headers = {
            'Authorization': f'Bearer {account.access_token}',
        }

        # Get contributor stats
        response = http_requests.get(
            f"{config['api_base']}/contributor/stats",
            headers=headers
        )

        if response.status_code == 401:
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'shutterstock_get_portfolio', 'reason': 'token_expired', 'platform': 'shutterstock'},
            )

        if response.status_code != 200:
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'shutterstock_get_portfolio',
                    'reason': 'upstream_error',
                    'platform': 'shutterstock',
                    'upstream_status': response.status_code,
                },
            )

        stats = response.json()

        # Get portfolio items
        portfolio_response = http_requests.get(
            f"{config['api_base']}/contributor/sets",
            headers=headers
        )

        portfolio = []
        if portfolio_response.status_code == 200:
            portfolio = portfolio_response.json().get('data', [])

        return api_success({
            'stats': {
                'total_earnings': stats.get('lifetime_earnings', 0),
                'total_downloads': stats.get('lifetime_downloads', 0),
                'total_images': stats.get('total_images', 0),
            },
            'portfolio': portfolio[:20],  # First 20 items
        })

    except Exception as e:
        logger.exception(f"Shutterstock portfolio fetch error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'shutterstock_get_portfolio',
                'reason': 'unhandled_exception',
                'exc_type': type(e).__name__,
            },
        )


@csrf_exempt
@require_http_methods(["POST"])
def shutterstock_submit_content(request):
    """
    POST /api/distribution/shutterstock/submit/

    Submit content for Shutterstock contributor review.

    Request body:
    {
        "image_url": "https://...",
        "title": "AI Generated Landscape",
        "description": "Beautiful mountain scenery...",
        "keywords": ["landscape", "mountain", "nature"],
        "categories": ["Nature"],
        "image_history_id": "uuid"
    }
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'shutterstock_submit_content'},
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'shutterstock_submit_content', 'reason': 'json_decode_error'},
        )

    required_fields = ['image_url', 'title', 'description', 'keywords']
    for field in required_fields:
        if field not in data:
            return emit_error_envelope(
                reason_code='invalid_input',
                request=request,
                hint={'source': 'shutterstock_submit_content', 'reason': 'missing_field', 'field': field},
            )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains='Shutterstock',
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'shutterstock_submit_content', 'reason': 'no_active_account', 'platform': 'shutterstock'},
        )

    # For Shutterstock, submissions go through their contributor portal
    # This endpoint creates a tracking record and provides guidance

    distribution = ContentDistribution.objects.create(
        user=request.user,
        platform_account=account,
        content_type='image',
        title=data['title'],
        description=data['description'],
        tags=data.get('keywords', []),
        categories=data.get('categories', []),
        status='pending',  # Pending review
        platform_metadata={
            'image_url': data['image_url'],
            'submission_type': 'contributor',
            'submitted_at': timezone.now().isoformat(),
        }
    )

    # Link to image history if provided
    if data.get('image_history_id'):
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=data['image_history_id'])
            distribution.image_history = image
            distribution.save()
        except ImageHistory.DoesNotExist:
            pass

    return api_success({
        'distribution_id': str(distribution.id),
        'status': 'pending',
        'message': 'Content tracked for Shutterstock submission. Upload via contributor portal.',
        'contributor_portal': 'https://submit.shutterstock.com/',
        'guidelines': {
            'min_resolution': '4MP (recommended 50MP+)',
            'accepted_formats': ['JPEG', 'PNG', 'TIFF'],
            'review_time': '5-10 business days',
        }
    })


# =============================================================================
# Gumroad Integration
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def gumroad_get_products(request):
    """
    GET /api/distribution/gumroad/products/

    Get user's Gumroad products.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'gumroad_get_products'},
        )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains='Gumroad',
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'gumroad_get_products', 'reason': 'no_active_account', 'platform': 'gumroad'},
        )

    try:
        import requests as http_requests

        config = PLATFORM_CONFIGS['gumroad']

        response = http_requests.get(
            f"{config['api_base']}/products",
            params={'access_token': account.access_token}
        )

        if response.status_code == 401:
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'gumroad_get_products', 'reason': 'token_expired', 'platform': 'gumroad'},
            )

        if response.status_code != 200:
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'gumroad_get_products',
                    'reason': 'upstream_error',
                    'platform': 'gumroad',
                    'upstream_status': response.status_code,
                },
            )

        data = response.json()
        products = data.get('products', [])

        return api_success({
            'products': [{
                'id': p.get('id'),
                'name': p.get('name'),
                'price': p.get('price', 0) / 100,  # Convert cents to dollars
                'sales_count': p.get('sales_count', 0),
                'revenue': p.get('sales_usd_cents', 0) / 100,
                'url': p.get('short_url'),
                'published': p.get('published', False),
            } for p in products]
        })

    except Exception as e:
        logger.exception(f"Gumroad products fetch error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'gumroad_get_products',
                'reason': 'unhandled_exception',
                'exc_type': type(e).__name__,
            },
        )


@csrf_exempt
@require_http_methods(["POST"])
def gumroad_create_product(request):
    """
    POST /api/distribution/gumroad/products/create/

    Create a new product on Gumroad.

    Request body:
    {
        "name": "AI Art Pack",
        "description": "Collection of AI-generated artwork...",
        "price": 9.99,
        "preview_url": "https://...",
        "file_url": "https://...",
        "tags": ["ai", "art", "digital"],
        "image_history_id": "uuid"
    }
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'gumroad_create_product'},
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'gumroad_create_product', 'reason': 'json_decode_error'},
        )

    required_fields = ['name', 'description', 'price']
    for field in required_fields:
        if field not in data:
            return emit_error_envelope(
                reason_code='invalid_input',
                request=request,
                hint={'source': 'gumroad_create_product', 'reason': 'missing_field', 'field': field},
            )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains='Gumroad',
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'gumroad_create_product', 'reason': 'no_active_account', 'platform': 'gumroad'},
        )

    try:
        import requests as http_requests

        config = PLATFORM_CONFIGS['gumroad']

        product_data = {
            'access_token': account.access_token,
            'name': data['name'],
            'description': data['description'],
            'price': int(float(data['price']) * 100),  # Convert to cents
        }

        if data.get('preview_url'):
            product_data['preview_url'] = data['preview_url']
        if data.get('url'):
            product_data['url'] = data.get('url')

        response = http_requests.post(
            f"{config['api_base']}/products",
            data=product_data
        )

        if response.status_code == 401:
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'gumroad_create_product', 'reason': 'token_expired', 'platform': 'gumroad'},
            )

        if response.status_code not in [200, 201]:
            return emit_error_envelope(
                reason_code='upstream_provider_error',
                request=request,
                hint={
                    'source': 'gumroad_create_product',
                    'reason': 'upstream_error',
                    'platform': 'gumroad',
                    'upstream_status': response.status_code,
                },
            )

        gumroad_product = response.json().get('product', {})

        # Create ContentDistribution record
        distribution = ContentDistribution.objects.create(
            user=request.user,
            platform_account=account,
            content_type='image',
            title=data['name'],
            description=data['description'],
            price=Decimal(str(data['price'])),
            tags=data.get('tags', []),
            platform_listing_id=gumroad_product.get('id', ''),
            platform_listing_url=gumroad_product.get('short_url', ''),
            platform_metadata=gumroad_product,
            status='live' if gumroad_product.get('published') else 'draft',
            listed_at=timezone.now() if gumroad_product.get('published') else None,
        )

        # Link to image history if provided
        if data.get('image_history_id'):
            from content.models import ImageHistory
            try:
                image = ImageHistory.objects.get(id=data['image_history_id'])
                distribution.image_history = image
                distribution.save()
            except ImageHistory.DoesNotExist:
                pass

        # Update account stats
        account.total_items_listed += 1
        account.save()

        return api_success({
            'product_id': gumroad_product.get('id', ''),
            'distribution_id': str(distribution.id),
            'url': gumroad_product.get('short_url', ''),
            'published': gumroad_product.get('published', False),
            'message': 'Product created successfully'
        })

    except Exception as e:
        logger.exception(f"Gumroad product creation error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'gumroad_create_product',
                'reason': 'unhandled_exception',
                'exc_type': type(e).__name__,
            },
        )


@csrf_exempt
@require_http_methods(["POST"])
def gumroad_publish_image(request):
    """
    POST /api/distribution/gumroad/publish/

    Publish an AI-generated image to Gumroad with actual file upload.

    Session 487: Golden Egg Strategy - This endpoint uses GumroadPublishingService
    to download the image and upload it to Gumroad with multipart file handling.

    Request body:
    {
        "image_id": 123,  // ImageHistory ID or sequential_number
        "title": "Custom Title",  // Optional
        "price": 9.99,  // Optional, defaults to 9.99
        "description": "Custom description"  // Optional
    }
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'gumroad_publish_image'},
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'gumroad_publish_image', 'reason': 'json_decode_error'},
        )

    image_id = data.get('image_id')
    if not image_id:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={'source': 'gumroad_publish_image', 'reason': 'missing_field', 'field': 'image_id'},
        )

    try:
        from core.services.gumroad_publishing import GumroadPublishingService
        from content.models import ImageHistory

        # Find the image - try sequential_number first, then primary key
        image = ImageHistory.objects.filter(
            user=request.user,
            sequential_number=image_id
        ).first()

        if not image:
            try:
                image = ImageHistory.objects.get(id=image_id, user=request.user)
            except (ImageHistory.DoesNotExist, ValueError):
                return emit_error_envelope(
                    reason_code='not_found',
                    request=request,
                    hint={'source': 'gumroad_publish_image', 'reason': 'image_not_found', 'image_id': image_id},
                )

        # Initialize publishing service
        service = GumroadPublishingService(request.user)

        if not service.account:
            return emit_error_envelope(
                reason_code='not_found',
                request=request,
                hint={'source': 'gumroad_publish_image', 'reason': 'no_active_account', 'platform': 'gumroad'},
            )

        # Publish to Gumroad with actual file upload
        distribution = service.publish_image(
            image_id=image.id,
            title=data.get('title'),
            price=Decimal(str(data.get('price', 9.99))),
            description=data.get('description')
        )

        return api_success({
            'success': True,
            'distribution_id': str(distribution.id),
            'product_url': distribution.platform_listing_url,
            'product_id': distribution.platform_listing_id,
            'title': distribution.title,
            'price': str(distribution.price),
            'message': 'Image published to Gumroad successfully!'
        })

    except ValueError as e:
        return emit_error_envelope(
            reason_code='invalid_input',
            request=request,
            hint={
                'source': 'gumroad_publish_image',
                'reason': 'value_error',
                'exc_type': 'ValueError',
                'exc_msg': str(e),
            },
        )
    except Exception as e:
        logger.exception(f"Gumroad publish error: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'gumroad_publish_image',
                'reason': 'unhandled_exception',
                'exc_type': type(e).__name__,
            },
        )


@csrf_exempt
@require_http_methods(["POST"])
def gumroad_webhook(request):
    """
    POST /api/distribution/gumroad/webhook/

    Webhook endpoint for Gumroad sale notifications.

    Session 487: Receives sale events from Gumroad and updates
    ContentDistribution records with sales/revenue data.

    Gumroad sends form data (not JSON) with fields:
    - product_id: The Gumroad product ID
    - price: Price in cents
    - email: Buyer's email
    - full_name: Buyer's name
    - purchaser_id: Gumroad user ID
    - sale_id: Unique sale ID
    - seller_id: Your Gumroad ID
    - etc.

    Note: Configure this webhook URL in Gumroad dashboard:
    https://app.gumroad.com/settings/advanced
    """
    try:
        # Gumroad sends form data, not JSON
        data = request.POST.dict()

        if not data:
            # Try JSON body as fallback
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'No data received'}, status=400)

        product_id = data.get('product_id')
        price_cents = int(data.get('price', 0))
        sale_id = data.get('sale_id')

        if not product_id:
            return JsonResponse({'status': 'error', 'message': 'Missing product_id'}, status=400)

        # Find the distribution by Gumroad product ID
        distribution = ContentDistribution.objects.filter(
            platform='gumroad',
            platform_listing_id=product_id
        ).first()

        if distribution:
            # Update sales count and revenue
            distribution.sales = (distribution.sales or 0) + 1
            distribution.revenue = (distribution.revenue or Decimal('0')) + (Decimal(price_cents) / 100)
            distribution.save()

            logger.info(
                f"Gumroad sale recorded: Product {product_id}, "
                f"Sale {sale_id}, ${price_cents/100:.2f}, "
                f"Total sales: {distribution.sales}"
            )

            # Also update the UserPlatformAccount totals
            if distribution.platform_account:
                distribution.platform_account.total_sales = (distribution.platform_account.total_sales or 0) + 1
                distribution.platform_account.total_revenue = (
                    (distribution.platform_account.total_revenue or Decimal('0')) +
                    (Decimal(price_cents) / 100)
                )
                distribution.platform_account.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Sale recorded',
                'distribution_id': str(distribution.id),
                'total_sales': distribution.sales,
                'total_revenue': str(distribution.revenue)
            })
        else:
            # Log unknown product (might be a product created outside our system)
            logger.warning(f"Gumroad webhook received for unknown product: {product_id}")
            return JsonResponse({
                'status': 'success',
                'message': 'Product not tracked in system'
            })

    except Exception as e:
        logger.exception(f"Gumroad webhook error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =============================================================================
# Revenue Sync Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def sync_platform_revenue(request, platform):
    """
    POST /api/distribution/<platform>/sync-revenue/

    Sync revenue data from platform API.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'sync_platform_revenue'},
        )

    try:
        account = UserPlatformAccount.objects.select_related('platform').get(
            user=request.user,
            platform__name__icontains=platform,
            account_status='active'
        )
    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'sync_platform_revenue', 'reason': 'no_active_account', 'platform': platform},
        )

    synced_data = {
        'platform': platform,
        'total_revenue': Decimal('0'),
        'total_sales': 0,
        'items_synced': 0,
    }

    try:
        if platform.lower() == 'gumroad':
            synced_data = sync_gumroad_revenue(account)
        elif platform.lower() == 'etsy':
            synced_data = sync_etsy_revenue(account)
        else:
            return emit_error_envelope(
                reason_code='unavailable',
                request=request,
                hint={'source': 'sync_platform_revenue', 'reason': 'not_implemented', 'platform': platform},
            )

        # Update account totals
        account.total_revenue = synced_data.get('total_revenue', account.total_revenue)
        account.total_sales = synced_data.get('total_sales', account.total_sales)
        account.save()

        return api_success({
            'synced': True,
            **synced_data,
        })

    except Exception as e:
        logger.exception(f"Revenue sync error for {platform}: {e}")
        return emit_error_envelope(
            reason_code='internal_error',
            request=request,
            hint={
                'source': 'sync_platform_revenue',
                'reason': 'unhandled_exception',
                'platform': platform,
                'exc_type': type(e).__name__,
            },
        )


def sync_gumroad_revenue(account):
    """Sync revenue from Gumroad."""
    import requests as http_requests

    config = PLATFORM_CONFIGS['gumroad']

    response = http_requests.get(
        f"{config['api_base']}/sales",
        params={
            'access_token': account.access_token,
            'after': (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        }
    )

    if response.status_code != 200:
        raise Exception(f"Gumroad API error: {response.status_code}")

    sales = response.json().get('sales', [])

    total_revenue = Decimal('0')
    total_sales = len(sales)

    for sale in sales:
        revenue = Decimal(str(sale.get('price', 0))) / 100
        total_revenue += revenue

        # Update distribution record if exists
        product_id = sale.get('product_id')
        if product_id:
            distribution = ContentDistribution.objects.filter(
                platform_account=account,
                platform_listing_id=product_id
            ).first()

            if distribution:
                distribution.sales += 1
                distribution.revenue += revenue
                distribution.last_sale_at = timezone.now()
                distribution.save()

    return {
        'platform': 'gumroad',
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'items_synced': len(sales),
    }


def sync_etsy_revenue(account):
    """Sync revenue from Etsy."""
    import requests as http_requests

    config = PLATFORM_CONFIGS['etsy']
    creds = get_platform_credentials('etsy')

    headers = {
        'Authorization': f'Bearer {account.access_token}',
        'x-api-key': creds.get('client_id', ''),
    }

    # Get shop transactions
    response = http_requests.get(
        f"{config['api_base']}/application/shops/{account.account_username}/transactions",
        headers=headers,
        params={'limit': 100}
    )

    if response.status_code != 200:
        raise Exception(f"Etsy API error: {response.status_code}")

    transactions = response.json().get('results', [])

    total_revenue = Decimal('0')
    total_sales = len(transactions)

    for txn in transactions:
        revenue = Decimal(str(txn.get('price', {}).get('amount', 0))) / 100
        total_revenue += revenue

        # Update distribution record if exists
        listing_id = str(txn.get('listing_id', ''))
        if listing_id:
            distribution = ContentDistribution.objects.filter(
                platform_account=account,
                platform_listing_id=listing_id
            ).first()

            if distribution:
                distribution.sales += 1
                distribution.revenue += revenue
                distribution.last_sale_at = timezone.now()
                distribution.save()

    return {
        'platform': 'etsy',
        'total_revenue': total_revenue,
        'total_sales': total_sales,
        'items_synced': len(transactions),
    }


# =============================================================================
# Platform Status Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_platform_integrations(request):
    """
    GET /api/distribution/integrations/

    List all available platform integrations and their status.
    """
    integrations = []

    for platform_key, config in PLATFORM_CONFIGS.items():
        creds = get_platform_credentials(platform_key)

        integration_status = {
            'platform': platform_key,
            'name': config['name'],
            'configured': bool(creds.get('client_id') or creds.get('api_key')),
            'auth_type': config.get('auth_type', 'oauth'),
            'features': {
                'oauth': 'auth_url' in config,
                'upload': platform_key in ['etsy', 'gumroad', 'shutterstock'],
                'revenue_sync': platform_key in ['etsy', 'gumroad'],
            }
        }

        # Check if user has connected account
        if request.user.is_authenticated:
            connected = UserPlatformAccount.objects.filter(
                user=request.user,
                platform__name__icontains=config['name'],
                account_status='active'
            ).exists()
            integration_status['connected'] = connected

        integrations.append(integration_status)

    return api_success({
        'integrations': integrations,
        'total_configured': sum(1 for i in integrations if i['configured']),
        'total_connected': sum(1 for i in integrations if i.get('connected', False)),
    })


@csrf_exempt
@require_http_methods(["POST"])
def disconnect_platform(request, platform):
    """
    POST /api/distribution/oauth/<platform>/disconnect/

    Disconnect a platform account.
    """
    if not request.user.is_authenticated:
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'disconnect_platform'},
        )

    try:
        account = UserPlatformAccount.objects.get(
            user=request.user,
            platform__name__icontains=platform
        )

        # Revoke tokens if possible (platform-specific)
        # Most platforms don't have a revoke endpoint, so we just delete locally

        account.access_token = ''
        account.refresh_token = ''
        account.account_status = 'inactive'
        account.save()

        return api_success({
            'message': f'{platform} disconnected successfully',
            'platform': platform,
        })

    except UserPlatformAccount.DoesNotExist:
        return emit_error_envelope(
            reason_code='not_found',
            request=request,
            hint={'source': 'disconnect_platform', 'reason': 'no_account_found', 'platform': platform},
        )

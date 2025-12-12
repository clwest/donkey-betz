"""
Session 429: Discord Integration API Views

API endpoints for Discord account linking and management.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def generate_discord_link_code(request):
    """
    Generate a temporary code for linking Discord account.

    POST /api/discord/generate-link-code/

    Returns:
        {
            "success": true,
            "code": "ABC123",
            "expires_in_minutes": 10,
            "instructions": "Use /link ABC123 in Discord"
        }
    """
    from core.models import DiscordLinkCode

    try:
        # Check if user already has Discord linked
        if request.user.discord_id:
            return JsonResponse({
                'success': False,
                'error': 'Discord account already linked',
                'discord_username': request.user.discord_username,
                'linked_at': request.user.discord_linked_at.isoformat() if request.user.discord_linked_at else None
            }, status=400)

        # Generate new link code
        link_code = DiscordLinkCode.create_for_user(request.user)

        return JsonResponse({
            'success': True,
            'code': link_code.code,
            'expires_in_minutes': 10,
            'expires_at': link_code.expires_at.isoformat(),
            'instructions': f'Use /link {link_code.code} in Discord to link your account'
        })

    except Exception as e:
        logger.exception(f"Error generating Discord link code: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_discord_status(request):
    """
    Get current Discord link status for the user.

    GET /api/discord/status/

    Returns:
        {
            "success": true,
            "linked": true/false,
            "discord_id": "123456789",
            "discord_username": "user#1234",
            "linked_at": "2025-12-12T..."
        }
    """
    try:
        return JsonResponse({
            'success': True,
            'linked': bool(request.user.discord_id),
            'discord_id': request.user.discord_id,
            'discord_username': request.user.discord_username,
            'linked_at': request.user.discord_linked_at.isoformat() if request.user.discord_linked_at else None
        })

    except Exception as e:
        logger.exception(f"Error getting Discord status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def unlink_discord(request):
    """
    Unlink Discord account from web user.

    POST /api/discord/unlink/

    Returns:
        {
            "success": true,
            "message": "Discord account unlinked"
        }
    """
    try:
        if not request.user.discord_id:
            return JsonResponse({
                'success': False,
                'error': 'No Discord account linked'
            }, status=400)

        old_username = request.user.discord_username
        request.user.discord_id = None
        request.user.discord_username = None
        request.user.discord_linked_at = None
        request.user.save(update_fields=['discord_id', 'discord_username', 'discord_linked_at'])

        logger.info(f"User {request.user.username} unlinked Discord account: {old_username}")

        return JsonResponse({
            'success': True,
            'message': 'Discord account unlinked successfully'
        })

    except Exception as e:
        logger.exception(f"Error unlinking Discord: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verify_discord_link_code(request):
    """
    Verify a link code and connect Discord account.

    This endpoint is called by the Discord bot when a user runs /link <code>.
    It's internal-only (no user auth required, but validates bot secret).

    POST /api/discord/verify-link-code/
    Body: {
        "code": "ABC123",
        "discord_id": "123456789",
        "discord_username": "user#1234",
        "bot_secret": "..."
    }

    Returns:
        {
            "success": true,
            "user_id": "uuid",
            "username": "webuser"
        }
    """
    import json
    import os

    try:
        data = json.loads(request.body)
        code = data.get('code', '').upper()
        discord_id = data.get('discord_id')
        discord_username = data.get('discord_username')
        bot_secret = data.get('bot_secret')

        # Validate bot secret (use DISCORD_BOT_TOKEN as secret)
        expected_secret = os.environ.get('DISCORD_BOT_TOKEN', '')[:20]  # Use first 20 chars
        if not bot_secret or bot_secret != expected_secret:
            return JsonResponse({
                'success': False,
                'error': 'Invalid bot authentication'
            }, status=403)

        if not code or not discord_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: code, discord_id'
            }, status=400)

        from core.models import DiscordLinkCode, UnifiedUser

        # Check if Discord account is already linked to someone
        existing_user = UnifiedUser.objects.filter(discord_id=discord_id).first()
        if existing_user:
            return JsonResponse({
                'success': False,
                'error': f'This Discord account is already linked to {existing_user.username}'
            }, status=400)

        # Find the link code
        link_code = DiscordLinkCode.objects.filter(
            code=code,
            used=False
        ).select_related('user').first()

        if not link_code:
            return JsonResponse({
                'success': False,
                'error': 'Invalid or expired link code'
            }, status=400)

        if link_code.is_expired:
            return JsonResponse({
                'success': False,
                'error': 'Link code has expired. Please generate a new one.'
            }, status=400)

        # Link the accounts
        user = link_code.user
        user.discord_id = discord_id
        user.discord_username = discord_username
        user.discord_linked_at = timezone.now()
        user.save(update_fields=['discord_id', 'discord_username', 'discord_linked_at'])

        # Mark code as used
        link_code.used = True
        link_code.used_at = timezone.now()
        link_code.save(update_fields=['used', 'used_at'])

        logger.info(f"Discord account {discord_username} ({discord_id}) linked to user {user.username}")

        return JsonResponse({
            'success': True,
            'user_id': str(user.id),
            'username': user.username,
            'message': f'Successfully linked to {user.username}'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.exception(f"Error verifying Discord link code: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

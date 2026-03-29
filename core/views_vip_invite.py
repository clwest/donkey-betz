"""
VIP Invite API — magic-link creation, exchange, and revocation.

Endpoints:
  POST /api/v1/vip-invites/create/   (admin-only)  → token + accept_url
  POST /api/v1/vip-invites/exchange/  (public)      → API key for VIP account
  POST /api/v1/vip-invites/revoke/    (admin-only)  → soft-revoke
  GET  /api/v1/vip-invites/           (admin-only)  → list all invites
"""

import secrets
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from core.models_vip_invite import VIPInvite

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def vip_invite_create(request):
    """Create a new VIP magic-link invite (admin-only).

    Optional params:
        workspace_id: UUID — scope the VIP view to this workspace
        prospect_profile_id: UUID — deliverable ID for personalization
        recipient_name: str — display name for the invitee
    """
    label = request.data.get('label', '')
    workspace_id = request.data.get('workspace_id')
    prospect_profile_id = request.data.get('prospect_profile_id')
    recipient_name = request.data.get('recipient_name', '')

    kwargs = {
        'created_by': request.user,
        'label': label,
        'recipient_name': recipient_name,
    }

    if workspace_id:
        from core.models_skin_layer import ProjectWorkspace
        ws = ProjectWorkspace.objects.filter(id=workspace_id).first()
        if ws:
            kwargs['workspace'] = ws

    if prospect_profile_id:
        from core.models_deliverables import Deliverable
        profile = Deliverable.objects.filter(id=prospect_profile_id).first()
        if profile:
            kwargs['prospect_profile'] = profile

    invite = VIPInvite.objects.create(**kwargs)

    import os
    base_url = os.environ.get(
        'VIP_ACCEPT_BASE_URL',
        request.build_absolute_uri('/'),
    )
    accept_url = f"{base_url.rstrip('/')}/vip/accept?token={invite.token}"

    return Response({
        'id': str(invite.id),
        'token': invite.token,
        'accept_url': accept_url,
        'token_expires_at': invite.token_expires_at.isoformat(),
        'account_expires_at': invite.account_expires_at.isoformat(),
        'label': invite.label,
        'recipient_name': invite.recipient_name,
        'workspace_id': str(invite.workspace_id) if invite.workspace_id else None,
        'workspace_name': invite.workspace.name if invite.workspace else None,
        'prospect_profile_id': str(invite.prospect_profile_id) if invite.prospect_profile_id else None,
    }, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def vip_invite_exchange(request):
    """Exchange a magic-link token for a VIP API key."""
    token = request.data.get('token', '').strip()
    if not token:
        return Response({'error': 'Token is required.'}, status=400)

    try:
        invite = VIPInvite.objects.get(token=token)
    except VIPInvite.DoesNotExist:
        return Response({'error': 'Invalid or expired invite.'}, status=404)

    if not invite.is_valid:
        return Response({'error': 'This invite has expired or been used.'}, status=410)

    # Create VIP user account
    username = f"vip_{secrets.token_hex(4)}"
    vip_user = User.objects.create_user(
        username=username,
        password=None,  # No password — token-only access
        is_active=True,
    )

    # Set primary_role on the profile
    try:
        from core.models import EnhancedUserProfile
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=vip_user)
        profile.primary_role = 'vip_demo_viewer'
        profile.save(update_fields=['primary_role'])
    except Exception:
        logger.warning("Could not set VIP primary_role on profile for %s", username)

    # Create DRF auth token
    from rest_framework.authtoken.models import Token
    api_token, _ = Token.objects.get_or_create(user=vip_user)

    # Mark invite as redeemed
    invite.redeemed_at = timezone.now()
    invite.redeemed_by = vip_user
    invite.save(update_fields=['redeemed_at', 'redeemed_by'])

    logger.info("VIP invite redeemed: invite=%s user=%s label=%s", invite.id, username, invite.label)

    # Record operation
    try:
        from core.services.operation_recorder import record_op
        record_op(
            op_type='vip_invite_exchange',
            title=f"VIP invite redeemed: {invite.label or 'unlabeled'}",
            description=f"User {username} created, role: vip_demo_viewer",
            actor_type='user',
            actor_id=username,
            entity_type='vip_invite',
            entity_id=str(invite.id),
        )
    except Exception:
        pass

    return Response({
        'api_key': api_token.key,
        'username': username,
        'expires_at': invite.account_expires_at.isoformat(),
        'role': 'vip_demo_viewer',
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def vip_invite_revoke(request):
    """Revoke a VIP invite token (admin-only)."""
    token = request.data.get('token', '').strip()
    invite_id = request.data.get('id', '').strip()

    if not token and not invite_id:
        return Response({'error': 'Provide token or id.'}, status=400)

    try:
        if invite_id:
            invite = VIPInvite.objects.get(id=invite_id)
        else:
            invite = VIPInvite.objects.get(token=token)
    except VIPInvite.DoesNotExist:
        return Response({'error': 'Invite not found.'}, status=404)

    if invite.revoked_at:
        return Response({'error': 'Already revoked.'}, status=409)

    invite.revoked_at = timezone.now()
    invite.save(update_fields=['revoked_at'])

    # Deactivate the VIP user if invite was redeemed
    if invite.redeemed_by:
        invite.redeemed_by.is_active = False
        invite.redeemed_by.save(update_fields=['is_active'])

    return Response({'status': 'revoked', 'id': str(invite.id)})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def vip_invite_list(request):
    """List all VIP invites (admin-only)."""
    invites = VIPInvite.objects.select_related(
        'created_by', 'redeemed_by', 'workspace', 'prospect_profile',
    ).all()[:50]
    data = []
    for inv in invites:
        data.append({
            'id': str(inv.id),
            'label': inv.label,
            'recipient_name': inv.recipient_name or '',
            'is_valid': inv.is_valid,
            'token_expires_at': inv.token_expires_at.isoformat(),
            'account_expires_at': inv.account_expires_at.isoformat(),
            'redeemed_at': inv.redeemed_at.isoformat() if inv.redeemed_at else None,
            'redeemed_by': inv.redeemed_by.username if inv.redeemed_by else None,
            'revoked_at': inv.revoked_at.isoformat() if inv.revoked_at else None,
            'created_by': inv.created_by.username,
            'created_at': inv.created_at.isoformat(),
            'workspace_id': str(inv.workspace_id) if inv.workspace_id else None,
            'workspace_name': inv.workspace.name if inv.workspace else None,
            'prospect_profile_id': str(inv.prospect_profile_id) if inv.prospect_profile_id else None,
        })
    return Response(data)

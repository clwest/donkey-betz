"""
Mobile-specific API views — push token registration, etc.
"""

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models_mobile import MobilePushToken


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_push_token(request):
    """Register or update an Expo push token for the current user."""
    token = request.data.get('expo_push_token')
    platform = request.data.get('platform')

    if not token or not platform:
        return Response(
            {'success': False, 'error': 'expo_push_token and platform are required'},
            status=400,
        )

    if platform not in ('ios', 'android'):
        return Response(
            {'success': False, 'error': 'platform must be ios or android'},
            status=400,
        )

    device_name = request.data.get('device_name', '')

    # Upsert: update existing token or create new one
    obj, created = MobilePushToken.objects.update_or_create(
        token=token,
        defaults={
            'user': request.user,
            'platform': platform,
            'device_name': device_name,
            'last_seen_at': timezone.now(),
            'revoked_at': None,
        },
    )

    return Response({
        'success': True,
        'created': created,
        'token_id': str(obj.pk),
    })

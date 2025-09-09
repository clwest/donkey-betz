"""
Views for campaigns app.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def campaigns_list(request):
    """
    Get list of campaigns.
    """
    return Response([])

@api_view(['GET'])
@permission_classes([AllowAny])
def campaign_templates(request):
    """
    Get campaign templates.
    """
    return Response({
        'templates': [
            {
                'id': 1,
                'name': 'Email Campaign',
                'description': 'Template for email marketing campaigns',
                'type': 'email',
                'icon': 'EnvelopeIcon'
            },
            {
                'id': 2,
                'name': 'Social Media Campaign',
                'description': 'Template for social media campaigns',
                'type': 'social',
                'icon': 'MegaphoneIcon'
            },
            {
                'id': 3,
                'name': 'Content Marketing',
                'description': 'Template for content marketing campaigns',
                'type': 'content',
                'icon': 'DocumentTextIcon'
            }
        ]
    })
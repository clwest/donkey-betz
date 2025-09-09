"""
Authentication views for the Unified Donkey Betz Platform.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and return token.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'credits': user.preferences.get('credits', 10000) if hasattr(user, 'preferences') else 10000,
                'subscription': user.preferences.get('subscription', 'premium') if hasattr(user, 'preferences') else user.subscription_tier
            }
        })
    else:
        return Response(
            {'detail': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout_view(request):
    """
    Logout user by deleting their token.
    """
    try:
        request.user.auth_token.delete()
        return Response({'detail': 'Successfully logged out'})
    except:
        return Response({'detail': 'Logout successful'})


@api_view(['GET'])
def current_user(request):
    """
    Get current authenticated user info.
    """
    if request.user.is_authenticated:
        return Response({
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'credits': getattr(request.user, 'credits', 1000),
                'subscription': getattr(request.user, 'subscription', 'premium')
            }
        })
    else:
        return Response(
            {'detail': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def user_profile(request):
    """
    Get or update user profile information.
    """
    if request.method == 'GET':
        # In production, get real user data
        # For now, return comprehensive mock data
        return Response({
            'id': 1,
            'username': 'demo_user',
            'email': 'demo@unified-donkey-betz.com',
            'full_name': 'Demo User',
            'credits': 10000,
            'subscription': 'premium',
            'joined': '2025-01-01T00:00:00Z',
            'last_login': '2025-09-09T18:00:00Z',
            'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo_user',
            'preferences': {
                'theme': 'dark',
                'language': 'en',
                'notifications': True,
                'email_updates': True,
                'default_model': 'gpt-5-mini',
                'auto_save': True,
                'show_tips': True
            },
            'stats': {
                'total_agents': 42,
                'content_generated': 1337,
                'tokens_used': 250000,
                'bets_analyzed': 89,
                'win_rate': 0.67
            }
        })
    
    elif request.method == 'PUT':
        # Handle profile updates
        # In production, update real user data
        return Response({
            'message': 'Profile updated successfully',
            'user': request.data
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def profile_stats(request):
    """
    Get user profile statistics.
    """
    # In production, calculate real stats from database
    # For now, return comprehensive mock statistics
    return Response({
        'total_agents_created': 42,
        'total_content_generated': 1337,
        'total_bets_analyzed': 89,
        'credits_used': 2500,
        'credits_remaining': 7500,
        'ai_tokens_consumed': 250000,
        'models_used': {
            'gpt-5': 15,
            'gpt-5-mini': 127,
            'gpt-5-nano': 95,
            'claude-3-sonnet': 23,
            'gpt-4': 12
        },
        'content_breakdown': {
            'blog_posts': 234,
            'social_media': 456,
            'emails': 189,
            'video_scripts': 78,
            'ebooks': 12,
            'podcasts': 45
        },
        'recent_activity': [
            {
                'type': 'content',
                'action': 'Generated blog post',
                'timestamp': '2025-09-09T17:30:00Z',
                'model': 'gpt-5-mini'
            },
            {
                'type': 'agent',
                'action': 'Created betting analysis agent',
                'timestamp': '2025-09-09T16:45:00Z',
                'model': 'gpt-5'
            },
            {
                'type': 'analysis',
                'action': 'Analyzed NCAAF odds',
                'timestamp': '2025-09-09T15:20:00Z',
                'model': 'gpt-5-nano'
            }
        ],
        'performance_metrics': {
            'avg_response_time': 1.2,
            'success_rate': 0.98,
            'satisfaction_score': 4.8,
            'cost_per_request': 0.03
        }
    })
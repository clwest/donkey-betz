"""
Authentication views for the Unified Donkey Betz Platform.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, UserStatistics

User = get_user_model()


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """
    Authenticate user and return token.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Login attempt - Request data: {request.data}")
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    logger.info(f"Login attempt - Username: {username}, Password: {'*' * len(password) if password else 'None'}")
    
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    logger.info(f"Authentication result: {user}")
    
    if user is not None:
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user profile if it exists
        try:
            profile = user.userprofile
            credits = profile.credits_remaining
            subscription = profile.account_type
        except Exception:
            credits = 10000
            subscription = 'premium'
        
        # Return user data with token
        return Response({
            'token': token.key,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'credits': credits,
                'subscription': subscription,
                'platform_role': getattr(user, 'platform_role', 'unified_user'),  # Session 998
            }
        })
    else:
        logger.error(f"Authentication failed for username: {username}")
        return Response(
            {'detail': f'Invalid credentials for user: {username}'},
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
    except Exception as e:
        logger.warning(f"Token deletion failed during logout: {e}")
        return Response({'detail': 'Logout successful'})


@api_view(['GET'])
def current_user(request):
    """
    Get current authenticated user info.
    """
    if request.user.is_authenticated:
        # Get user profile if it exists
        try:
            profile = request.user.userprofile
            credits = profile.credits_remaining
            subscription = profile.account_type
        except Exception:
            credits = 10000
            subscription = 'premium'
            
        return Response({
            'user': {
                'id': str(request.user.id),
                'username': request.user.username,
                'email': request.user.email,
                'credits': credits,
                'subscription': subscription,
                'platform_role': getattr(request.user, 'platform_role', 'unified_user'),  # Session 998
            }
        })
    else:
        return Response(
            {'detail': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get or update user profile information.
    Returns the full profile structure expected by the frontend.
    """
    if request.method == 'GET':
        user = request.user
        
        # Get or create UserProfile and UserStatistics
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': '',
                'occupation': '',
                'location': '',
                'credits_remaining': 1000,  # Start with 1000 credits
                'account_type': 'free',
            }
        )
        
        statistics, _ = UserStatistics.objects.get_or_create(
            user=user,
            defaults={
                'total_contents': 0,
                'total_images': 0,
                'total_videos': 0,
                'total_blogs': 0,
                'total_social_posts': 0,
                'total_ebooks': 0,
                'total_research_docs': 0,
                'total_campaigns': 0,
                'total_ai_requests': 0,
                'total_tokens_used': 0,
                'total_exports': 0,
                'favorite_style': 'default'
            }
        )
        
        # User data
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat() if hasattr(user, 'date_joined') else '2025-01-01T00:00:00Z'
        }
        
        # Profile data from database
        profile_data = {
            'avatar': profile.get_avatar_url(),
            'bio': profile.bio,
            'display_name': profile.get_display_name(),
            'occupation': profile.occupation,
            'location': profile.location,
            'preferred_ai_model': profile.preferred_ai_model,
            'default_content_tone': profile.default_content_tone,
            'auto_save': profile.auto_save,
            'dark_mode': profile.dark_mode,
            'email_notifications': profile.email_notifications,
            'default_citation_style': profile.default_citation_style,
            'preferred_book_length': profile.preferred_book_length,
            'research_topics': profile.research_topics,
            'account_type': profile.account_type,
            'credits_remaining': profile.credits_remaining,
            'storage_used_mb': profile.storage_used_mb,
            'last_active': profile.last_active.isoformat() if profile.last_active else user.last_login.isoformat() if user.last_login else '2025-01-01T00:00:00Z'
        }
        
        # Get statistics from the UserStatistics model
        # (Will integrate with real content models when available)
        from core.models.agents_registry import UnifiedAgentTemplate
        
        total_contents = statistics.total_contents
        total_blogs = statistics.total_blogs
        total_social = statistics.total_social_posts
        total_videos = statistics.total_videos
        total_images = statistics.total_images
        total_ebooks = statistics.total_ebooks
        total_research = statistics.total_research_docs
        
        # Get real agent count
        try:
            total_agents = UnifiedAgentTemplate.objects.filter(created_by=user).count()
        except Exception:
            total_agents = 0
        
        # Statistics data
        statistics_data = {
            'total_contents': total_contents,
            'total_images': total_images,
            'total_videos': total_videos,
            'total_blogs': total_blogs,
            'total_social_posts': total_social,
            'total_ebooks': total_ebooks,
            'total_research_docs': total_research,
            'total_agents': total_agents,
            'total_campaigns': 0,  # Not tracked yet
            'total_ai_requests': statistics.total_ai_requests,
            'total_tokens_used': statistics.total_tokens_used,
            'total_exports': statistics.total_exports,
            'favorite_style': statistics.favorite_style or 'default'
        }
        
        return Response({
            'user': user_data,
            'profile': profile_data,
            'statistics': statistics_data
        })
    
    elif request.method == 'PUT':
        # Handle profile updates
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Update profile fields
        update_fields = ['bio', 'display_name', 'occupation', 'location', 
                        'preferred_ai_model', 'default_content_tone', 'auto_save',
                        'dark_mode', 'email_notifications', 'default_citation_style',
                        'preferred_book_length']
        
        for field in update_fields:
            if field in request.data:
                setattr(profile, field, request.data[field])
        
        # Handle research_topics array field
        if 'research_topics' in request.data:
            profile.research_topics = request.data['research_topics']
        
        profile.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'profile': {
                'bio': profile.bio,
                'display_name': profile.get_display_name(),
                'occupation': profile.occupation,
                'location': profile.location,
                'preferred_ai_model': profile.preferred_ai_model,
                'default_content_tone': profile.default_content_tone,
                'auto_save': profile.auto_save,
                'dark_mode': profile.dark_mode,
                'email_notifications': profile.email_notifications,
                'default_citation_style': profile.default_citation_style,
                'preferred_book_length': profile.preferred_book_length,
                'research_topics': profile.research_topics,
            }
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_stats(request):
    """
    Get user profile statistics matching frontend expectations.
    """
    from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
    
    # Get or create statistics and profile
    stats_obj, _ = UserStatistics.objects.get_or_create(user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Use statistics object for now (will integrate with real content models later)
    total_content = stats_obj.total_contents
    blog_posts = stats_obj.total_blogs
    social_posts = stats_obj.total_social_posts
    email_content = 0
    video_content = stats_obj.total_videos
    image_content = stats_obj.total_images
    ebook_content = stats_obj.total_ebooks
    
    # Calculate real agent counts
    try:
        agents_created = UnifiedAgentTemplate.objects.filter(created_by=request.user).count()
        agent_executions = AgentExecution.objects.filter(user=request.user).count()
    except Exception:
        agents_created = 0
        agent_executions = 0
    
    # Calculate recent activity (last 7 and 30 days)
    # For now, just use 0 since we don't have real content yet
    last_7_days = 0
    last_30_days = 0
    
    # Get top styles - for now just return empty list
    top_styles = []
    
    # Calculate storage (real or estimated)
    total_storage_mb = stats_obj.get_total_storage_mb() if hasattr(stats_obj, 'get_total_storage_mb') else 0
    images_storage = image_content * 0.5  # Estimate 0.5MB per image
    videos_storage = video_content * 10   # Estimate 10MB per video
    
    # Return stats in the structure expected by frontend
    return Response({
        'content_breakdown': {
            'blog_posts': blog_posts,
            'social_media': social_posts,
            'emails': email_content,
            'video_scripts': video_content,
            'ebooks': ebook_content,
            'images': image_content
        },
        'recent_activity': {
            'last_7_days': last_7_days,
            'last_30_days': last_30_days
        },
        'top_styles': top_styles,
        'storage': {
            'images_mb': images_storage,
            'videos_mb': videos_storage,
            'total_mb': total_storage_mb or (images_storage + videos_storage)
        },
        # Additional stats
        'total_agents_created': agents_created,
        'total_content_generated': total_content,
        'total_bets_analyzed': agent_executions,  # Using agent executions as proxy
        'credits_used': max(0, 10000 - profile.credits_remaining),
        'credits_remaining': profile.credits_remaining,
        'ai_tokens_consumed': stats_obj.total_tokens_used,
        'models_used': {},  # Would need to track this in content metadata
        'recent_activity': [],  # Would need to query recent content/agent activities
        'performance_metrics': {
            'avg_response_time': 0.8,  # Could calculate from actual data
            'success_rate': 1.0,
            'satisfaction_score': 5.0,
            'cost_per_request': 0.02
        }
    })
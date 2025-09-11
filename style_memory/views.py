"""
Style Memory views for tracking and analyzing user style preferences.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import StyleMemory, StylePattern, StyleSuggestion, ContentLineage
from .serializers import (
    StyleMemorySerializer,
    StylePatternSerializer,
    StyleSuggestionSerializer,
    ContentLineageSerializer,
    InteractionRequestSerializer,
    StyleInsightsSerializer,
    VariationRequestSerializer
)
import random
import uuid


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any for testing
def capture_interaction(request):
    """Capture user interaction with generated content"""
    print(f"DEBUG: Received data: {request.data}")
    print(f"DEBUG: Headers: {request.headers}")
    serializer = InteractionRequestSerializer(data=request.data)
    if not serializer.is_valid():
        print(f"DEBUG: Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create test user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.user.is_authenticated:
        user = request.user
    else:
        # Use chris user for testing
        user = User.objects.filter(username='chris').first()
        if not user:
            user = User.objects.first()
    
    # Create style memory entry
    style_memory = StyleMemory.objects.create(
        user=user,
        content_id=serializer.validated_data['content_id'],
        interaction_type=serializer.validated_data['interaction_type'],
        parent_content_id=serializer.validated_data.get('parent_content_id'),
        notes=serializer.validated_data.get('notes', ''),
        recipe={
            'style': 'modern',
            'color_scheme': 'vibrant',
            'mood': 'energetic'
        },
        style_elements=['minimalist', 'bold', 'contemporary'],
        color_palette=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )
    
    # Update or create patterns
    _update_patterns(user, style_memory)
    
    # Generate suggestions if needed
    suggestion_count = _generate_suggestions(user)
    
    return Response({
        'success': True,
        'style_memory_id': str(style_memory.id),
        'recipe': style_memory.recipe,
        'patterns_detected': StylePattern.objects.filter(user=user).count(),
        'new_suggestions': suggestion_count
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_insights(request):
    """Get comprehensive style insights for the user"""
    # Get user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.filter(username='chris').first()
    
    if not user:
        return Response({
            'total_interactions': 0,
            'favorite_styles': [],
            'color_preferences': [],
            'recent_patterns': [],
            'suggestions_available': 0,
            'evolution_data': {}
        })
    
    # Get insights
    total_interactions = StyleMemory.objects.filter(user=user).count()
    
    # Get favorite styles
    favorite_styles = StylePattern.objects.filter(
        user=user,
        pattern_type='style'
    ).order_by('-confidence')[:5].values('pattern_value', 'confidence', 'frequency')
    
    # Get color preferences
    color_preferences = StylePattern.objects.filter(
        user=user,
        pattern_type='color'
    ).order_by('-frequency')[:5].values('pattern_value', 'confidence', 'frequency')
    
    # Get recent patterns
    recent_patterns = StylePattern.objects.filter(
        user=user
    ).order_by('-last_seen')[:10].values('pattern_type', 'pattern_value', 'confidence')
    
    # Count available suggestions
    suggestions_available = StyleSuggestion.objects.filter(
        user=user,
        status='pending'
    ).count()
    
    # Evolution data (simplified)
    evolution_data = {
        'trend': 'evolving',
        'consistency_score': 0.75,
        'exploration_rate': 0.3
    }
    
    return Response({
        'total_interactions': total_interactions,
        'favorite_styles': list(favorite_styles),
        'color_preferences': list(color_preferences),
        'recent_patterns': list(recent_patterns),
        'suggestions_available': suggestions_available,
        'evolution_data': evolution_data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_similar(request):
    """Generate variations based on style preferences"""
    serializer = VariationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Mock response for now
    return Response({
        'success': True,
        'variations': [
            {
                'id': str(uuid.uuid4()),
                'prompt': 'Generated variation prompt based on your style',
                'confidence': 0.85,
                'preview_url': None
            }
        ],
        'recipe_applied': {
            'base_style': 'modern',
            'modifications': ['increased vibrancy', 'enhanced contrast']
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_lineage(request, content_id):
    """Get the family tree of a content piece"""
    # Try to find lineage
    lineage = ContentLineage.objects.filter(
        Q(content_id=content_id) | Q(root_id=content_id)
    ).order_by('generation')
    
    serializer = ContentLineageSerializer(lineage, many=True)
    
    return Response({
        'content_id': content_id,
        'lineage': serializer.data,
        'total_descendants': lineage.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_suggestions(request):
    """Get AI-powered suggestions for the user"""
    # Get user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.filter(username='chris').first()
    
    if not user:
        return Response([])
    
    suggestions = StyleSuggestion.objects.filter(
        user=user,
        status='pending'
    ).order_by('-confidence')[:10]
    
    serializer = StyleSuggestionSerializer(suggestions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def respond_to_suggestion(request, suggestion_id):
    """Respond to a suggestion (use it or dismiss it)"""
    try:
        suggestion = StyleSuggestion.objects.get(id=suggestion_id)
    except StyleSuggestion.DoesNotExist:
        return Response({'error': 'Suggestion not found'}, status=status.HTTP_404_NOT_FOUND)
    
    response_type = request.data.get('response')
    if response_type not in ['used', 'dismissed']:
        return Response({'error': 'Invalid response type'}, status=status.HTTP_400_BAD_REQUEST)
    
    suggestion.status = response_type
    if response_type == 'used':
        suggestion.used_at = timezone.now()
        suggestion.result_content_id = request.data.get('result_content_id', '')
    
    suggestion.save()
    
    return Response({
        'success': True,
        'suggestion_id': str(suggestion.id),
        'status': suggestion.status
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_style_memories(request):
    """Get style memories for the user"""
    limit = int(request.GET.get('limit', 50))
    
    # Get user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.filter(username='chris').first()
    
    if not user:
        return Response([])
    
    memories = StyleMemory.objects.filter(user=user)[:limit]
    serializer = StyleMemorySerializer(memories, many=True)
    return Response(serializer.data)


def _update_patterns(user, style_memory):
    """Update patterns based on new interaction"""
    # Extract patterns from the interaction
    for element in style_memory.style_elements:
        pattern, created = StylePattern.objects.get_or_create(
            user=user,
            pattern_type='style',
            pattern_value=element,
            defaults={'confidence': 0.5, 'frequency': 0}
        )
        pattern.frequency += 1
        pattern.last_seen = timezone.now()
        pattern.confidence = min(0.95, pattern.confidence + 0.05)
        pattern.save()
        pattern.related_memories.add(style_memory)
    
    # Update color patterns
    for color in style_memory.color_palette:
        pattern, created = StylePattern.objects.get_or_create(
            user=user,
            pattern_type='color',
            pattern_value=color,
            defaults={'confidence': 0.5, 'frequency': 0}
        )
        pattern.frequency += 1
        pattern.last_seen = timezone.now()
        pattern.save()
        pattern.related_memories.add(style_memory)


def _generate_suggestions(user):
    """Generate new suggestions based on patterns"""
    # Check if we should generate new suggestions
    existing_pending = StyleSuggestion.objects.filter(
        user=user,
        status='pending'
    ).count()
    
    if existing_pending >= 5:
        return 0
    
    # Get top patterns
    top_patterns = StylePattern.objects.filter(
        user=user
    ).order_by('-confidence')[:3]
    
    if not top_patterns:
        return 0
    
    # Generate a suggestion
    suggestion = StyleSuggestion.objects.create(
        user=user,
        title=f"Try combining {top_patterns[0].pattern_value} style",
        description="Based on your recent preferences, this style might interest you",
        prompt_template=f"Create an image in {top_patterns[0].pattern_value} style with vibrant colors",
        confidence=top_patterns[0].confidence * 0.8
    )
    
    for pattern in top_patterns:
        suggestion.based_on_patterns.add(pattern)
    
    return 1

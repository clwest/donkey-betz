# Feedback System Implementation Handoff

## Executive Summary
The AI Content Studio has a partially implemented feedback system with a UserFeedback model and one working endpoint for blog posts. This document outlines requirements to expand it into a comprehensive feedback and rating system across all content types, with analytics and learning capabilities.

**Priority**: HIGH - Critical for improving AI generation quality and user satisfaction
**Estimated Time**: 4-5 hours for complete implementation
**Current Status**: 20% COMPLETE (Model exists, one endpoint working)

## Current State Analysis

### What Exists ✅
1. **Backend Model**
   - `UserFeedback` model in `content/models_universal.py`
   - Fields: rating (1-5), comments, helpful, feedback_type
   - Linked to User and Content models
   - Unique constraint: one feedback per content per user

2. **Single API Endpoint**
   - `/api/content/blog/<id>/feedback/` - Submit blog feedback only
   - Basic implementation in `views_blog.py`

3. **Minimal Frontend**
   - Star rating in BlogViewer component only
   - No feedback UI for other content types
   - No feedback analytics or display

### What's Missing ❌
1. **API Coverage** - No feedback endpoints for:
   - Images
   - Videos  
   - Social posts
   - eBooks
   - Voice transcriptions
   - Research documents

2. **Feedback UI Components** - Missing:
   - Reusable feedback widget
   - Feedback modal/popup
   - Inline feedback buttons
   - Feedback history view

3. **Analytics & Insights** - Not implemented:
   - Feedback dashboard
   - Average ratings display
   - Feedback trends
   - AI learning from feedback

4. **Feedback Actions** - Missing:
   - Edit/delete feedback
   - Respond to feedback
   - Flag content based on feedback
   - Regenerate with feedback

## Implementation Requirements

## Phase 1: Backend - Expand Feedback System (60 minutes)

### Step 1.1: Enhanced Feedback Models
**File**: `backend/content/models_feedback.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q
import json

class ContentFeedback(models.Model):
    """Enhanced feedback model for all content types"""
    
    RATING_CHOICES = [(i, f'{i} Stars') for i in range(1, 6)]
    
    FEEDBACK_TYPES = [
        ('quality', 'Quality'),
        ('accuracy', 'Accuracy'),
        ('relevance', 'Relevance'),
        ('creativity', 'Creativity'),
        ('tone', 'Tone'),
        ('length', 'Length'),
        ('style', 'Style'),
        ('usefulness', 'Usefulness'),
    ]
    
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('blog', 'Blog Post'),
        ('social', 'Social Post'),
        ('ebook', 'eBook'),
        ('voice', 'Voice Transcript'),
        ('research', 'Research Document'),
    ]
    
    # Core relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_feedback')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()  # Generic FK to any content
    
    # Ratings
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    quality_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    accuracy_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    usefulness_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    # Detailed feedback
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='quality')
    comments = models.TextField(blank=True)
    suggestions = models.TextField(blank=True, help_text="Suggestions for improvement")
    
    # Quick feedback options
    would_recommend = models.BooleanField(null=True, blank=True)
    met_expectations = models.BooleanField(null=True, blank=True)
    saved_time = models.BooleanField(null=True, blank=True)
    
    # Tags for categorization
    tags = models.JSONField(default=list, blank=True)
    
    # Metadata
    generation_params = models.JSONField(default=dict, blank=True)  # Store generation params for learning
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin response
    admin_response = models.TextField(blank=True)
    admin_responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'content_type', 'content_id']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['overall_rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.overall_rating}★ on {self.content_type}"
    
    @classmethod
    def get_content_stats(cls, content_type, content_id):
        """Get aggregated feedback stats for content"""
        feedback = cls.objects.filter(
            content_type=content_type,
            content_id=content_id
        )
        
        if not feedback.exists():
            return None
            
        return {
            'average_rating': feedback.aggregate(Avg('overall_rating'))['overall_rating__avg'],
            'total_feedback': feedback.count(),
            'rating_distribution': {
                i: feedback.filter(overall_rating=i).count() 
                for i in range(1, 6)
            },
            'recommendations': feedback.filter(would_recommend=True).count(),
            'recent_comments': list(
                feedback.exclude(comments='')
                .values('user__username', 'comments', 'overall_rating', 'created_at')
                [:5]
            )
        }


class FeedbackAction(models.Model):
    """Track actions taken based on feedback"""
    
    ACTION_TYPES = [
        ('regenerate', 'Content Regenerated'),
        ('edit', 'Content Edited'),
        ('delete', 'Content Deleted'),
        ('flag', 'Content Flagged'),
        ('improve', 'AI Model Improved'),
        ('respond', 'Admin Response'),
    ]
    
    feedback = models.ForeignKey(ContentFeedback, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_details = models.JSONField(default=dict)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class FeedbackAnalytics(models.Model):
    """Daily analytics for feedback trends"""
    
    date = models.DateField(unique=True)
    content_type = models.CharField(max_length=20)
    
    # Metrics
    total_feedback = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    positive_feedback = models.IntegerField(default=0)  # 4-5 stars
    neutral_feedback = models.IntegerField(default=0)   # 3 stars
    negative_feedback = models.IntegerField(default=0)  # 1-2 stars
    
    # Top issues
    top_complaints = models.JSONField(default=list)
    top_praises = models.JSONField(default=list)
    
    # Recommendations
    recommendation_rate = models.FloatField(default=0)
    improvement_suggestions = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date', 'content_type']
```

### Step 1.2: Create Comprehensive Feedback Views
**File**: `backend/api/views_feedback.py`

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from content.models_feedback import ContentFeedback, FeedbackAction, FeedbackAnalytics
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """
    Universal feedback submission for any content type
    POST /api/feedback/submit/
    """
    try:
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        
        if not content_type or not content_id:
            return Response(
                {'error': 'content_type and content_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate content type
        valid_types = ['text', 'image', 'video', 'blog', 'social', 'ebook', 'voice', 'research']
        if content_type not in valid_types:
            return Response(
                {'error': f'Invalid content_type. Must be one of {valid_types}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract feedback data
        feedback_data = {
            'user': request.user,
            'content_type': content_type,
            'content_id': content_id,
            'overall_rating': request.data.get('overall_rating'),
            'quality_rating': request.data.get('quality_rating'),
            'accuracy_rating': request.data.get('accuracy_rating'),
            'usefulness_rating': request.data.get('usefulness_rating'),
            'feedback_type': request.data.get('feedback_type', 'quality'),
            'comments': request.data.get('comments', ''),
            'suggestions': request.data.get('suggestions', ''),
            'would_recommend': request.data.get('would_recommend'),
            'met_expectations': request.data.get('met_expectations'),
            'saved_time': request.data.get('saved_time'),
            'tags': request.data.get('tags', []),
            'generation_params': request.data.get('generation_params', {}),
            'session_id': request.data.get('session_id', ''),
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
        
        # Validate rating
        if not feedback_data['overall_rating'] or feedback_data['overall_rating'] not in range(1, 6):
            return Response(
                {'error': 'overall_rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or update feedback
        feedback, created = ContentFeedback.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            content_id=content_id,
            defaults={k: v for k, v in feedback_data.items() if k not in ['user', 'content_type', 'content_id']}
        )
        
        # Trigger analytics update
        update_feedback_analytics.delay(content_type, timezone.now().date())
        
        # Check if we need to take automatic actions
        if feedback.overall_rating <= 2:
            # Flag for review if rating is very low
            FeedbackAction.objects.create(
                feedback=feedback,
                action_type='flag',
                action_details={'reason': 'Low rating', 'auto_flagged': True},
                performed_by=request.user
            )
        
        return Response({
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id,
            'created': created
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return Response(
            {'error': 'Failed to submit feedback'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_content_feedback(request, content_type, content_id):
    """
    Get all feedback for specific content
    GET /api/feedback/<content_type>/<content_id>/
    """
    try:
        # Get user's own feedback
        user_feedback = ContentFeedback.objects.filter(
            user=request.user,
            content_type=content_type,
            content_id=content_id
        ).first()
        
        # Get aggregated stats
        stats = ContentFeedback.get_content_stats(content_type, content_id)
        
        # Get recent feedback (anonymized if not own)
        recent_feedback = ContentFeedback.objects.filter(
            content_type=content_type,
            content_id=content_id
        ).exclude(comments='').order_by('-created_at')[:10]
        
        feedback_list = []
        for fb in recent_feedback:
            feedback_list.append({
                'id': fb.id,
                'username': fb.user.username if fb.user == request.user else 'Anonymous',
                'rating': fb.overall_rating,
                'comments': fb.comments,
                'created_at': fb.created_at,
                'is_own': fb.user == request.user
            })
        
        return Response({
            'user_feedback': {
                'rating': user_feedback.overall_rating if user_feedback else None,
                'comments': user_feedback.comments if user_feedback else '',
                'created_at': user_feedback.created_at if user_feedback else None,
            } if user_feedback else None,
            'stats': stats,
            'recent_feedback': feedback_list
        })
        
    except Exception as e:
        logger.error(f"Error getting feedback: {str(e)}")
        return Response(
            {'error': 'Failed to get feedback'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_feedback_history(request):
    """
    Get user's feedback history
    GET /api/feedback/history/
    """
    try:
        feedback = ContentFeedback.objects.filter(user=request.user).order_by('-created_at')
        
        # Apply filters
        content_type = request.GET.get('content_type')
        if content_type:
            feedback = feedback.filter(content_type=content_type)
        
        min_rating = request.GET.get('min_rating')
        if min_rating:
            feedback = feedback.filter(overall_rating__gte=int(min_rating))
        
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page
        
        feedback_list = []
        for fb in feedback[start:end]:
            feedback_list.append({
                'id': fb.id,
                'content_type': fb.content_type,
                'content_id': fb.content_id,
                'overall_rating': fb.overall_rating,
                'quality_rating': fb.quality_rating,
                'accuracy_rating': fb.accuracy_rating,
                'usefulness_rating': fb.usefulness_rating,
                'comments': fb.comments,
                'suggestions': fb.suggestions,
                'created_at': fb.created_at,
                'admin_response': fb.admin_response,
            })
        
        return Response({
            'feedback': feedback_list,
            'total': feedback.count(),
            'page': page,
            'per_page': per_page,
            'total_pages': (feedback.count() + per_page - 1) // per_page
        })
        
    except Exception as e:
        logger.error(f"Error getting feedback history: {str(e)}")
        return Response(
            {'error': 'Failed to get feedback history'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_feedback(request, feedback_id):
    """
    Update or delete user's own feedback
    PUT/DELETE /api/feedback/<feedback_id>/
    """
    try:
        feedback = ContentFeedback.objects.get(id=feedback_id, user=request.user)
        
        if request.method == 'DELETE':
            feedback.delete()
            return Response({'message': 'Feedback deleted successfully'})
        
        # Update feedback
        updateable_fields = [
            'overall_rating', 'quality_rating', 'accuracy_rating',
            'usefulness_rating', 'comments', 'suggestions',
            'would_recommend', 'met_expectations', 'saved_time', 'tags'
        ]
        
        for field in updateable_fields:
            if field in request.data:
                setattr(feedback, field, request.data[field])
        
        feedback.save()
        
        return Response({
            'message': 'Feedback updated successfully',
            'feedback_id': feedback.id
        })
        
    except ContentFeedback.DoesNotExist:
        return Response(
            {'error': 'Feedback not found or not authorized'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error managing feedback: {str(e)}")
        return Response(
            {'error': 'Failed to manage feedback'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feedback_analytics(request):
    """
    Get feedback analytics and trends
    GET /api/feedback/analytics/
    """
    try:
        # Date range
        days = int(request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get analytics
        analytics = FeedbackAnalytics.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        content_type = request.GET.get('content_type')
        if content_type:
            analytics = analytics.filter(content_type=content_type)
        
        # Aggregate by content type
        by_type = {}
        for item in analytics:
            if item.content_type not in by_type:
                by_type[item.content_type] = {
                    'total_feedback': 0,
                    'average_rating': [],
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0
                }
            
            by_type[item.content_type]['total_feedback'] += item.total_feedback
            by_type[item.content_type]['average_rating'].append(item.average_rating)
            by_type[item.content_type]['positive'] += item.positive_feedback
            by_type[item.content_type]['neutral'] += item.neutral_feedback
            by_type[item.content_type]['negative'] += item.negative_feedback
        
        # Calculate averages
        for content_type in by_type:
            ratings = by_type[content_type]['average_rating']
            by_type[content_type]['average_rating'] = sum(ratings) / len(ratings) if ratings else 0
        
        # Get user's contribution
        user_feedback_count = ContentFeedback.objects.filter(
            user=request.user,
            created_at__date__gte=start_date
        ).count()
        
        return Response({
            'period': {'start': start_date, 'end': end_date, 'days': days},
            'by_content_type': by_type,
            'user_contribution': user_feedback_count,
            'total_feedback': sum(item['total_feedback'] for item in by_type.values()),
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return Response(
            {'error': 'Failed to get analytics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_feedback(request):
    """
    Submit quick feedback (thumbs up/down)
    POST /api/feedback/quick/
    """
    try:
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        is_positive = request.data.get('is_positive')  # True for thumbs up, False for thumbs down
        
        if not all([content_type, content_id, is_positive is not None]):
            return Response(
                {'error': 'content_type, content_id, and is_positive are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert to rating
        rating = 4 if is_positive else 2
        
        feedback, created = ContentFeedback.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            content_id=content_id,
            defaults={
                'overall_rating': rating,
                'feedback_type': 'quality',
                'met_expectations': is_positive,
            }
        )
        
        return Response({
            'message': 'Quick feedback submitted',
            'is_positive': is_positive,
            'created': created
        })
        
    except Exception as e:
        logger.error(f"Error submitting quick feedback: {str(e)}")
        return Response(
            {'error': 'Failed to submit quick feedback'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Celery task for analytics (if using Celery)
def update_feedback_analytics(content_type, date):
    """Update feedback analytics for a given date and content type"""
    try:
        feedback = ContentFeedback.objects.filter(
            content_type=content_type,
            created_at__date=date
        )
        
        if not feedback.exists():
            return
        
        total = feedback.count()
        avg_rating = feedback.aggregate(Avg('overall_rating'))['overall_rating__avg']
        
        analytics, created = FeedbackAnalytics.objects.update_or_create(
            date=date,
            content_type=content_type,
            defaults={
                'total_feedback': total,
                'average_rating': avg_rating,
                'positive_feedback': feedback.filter(overall_rating__gte=4).count(),
                'neutral_feedback': feedback.filter(overall_rating=3).count(),
                'negative_feedback': feedback.filter(overall_rating__lte=2).count(),
                'recommendation_rate': feedback.filter(would_recommend=True).count() / total if total > 0 else 0,
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating analytics: {str(e)}")
```

### Step 1.3: Add URL Patterns
**File**: `backend/api/urls.py`

Add these patterns:
```python
from api.views_feedback import (
    submit_feedback, get_content_feedback, get_user_feedback_history,
    manage_feedback, get_feedback_analytics, quick_feedback
)

urlpatterns = [
    # ... existing patterns
    
    # Feedback System
    path('feedback/submit/', submit_feedback, name='api_submit_feedback'),
    path('feedback/quick/', quick_feedback, name='api_quick_feedback'),
    path('feedback/history/', get_user_feedback_history, name='api_feedback_history'),
    path('feedback/analytics/', get_feedback_analytics, name='api_feedback_analytics'),
    path('feedback/<str:content_type>/<int:content_id>/', get_content_feedback, name='api_get_feedback'),
    path('feedback/<int:feedback_id>/', manage_feedback, name='api_manage_feedback'),
]
```

## Phase 2: Frontend - Feedback Components (90 minutes)

### Step 2.1: Create Feedback Service
**File**: `ai-studio-web/src/services/feedbackService.ts`

```typescript
import { apiRequest } from './api';

export interface Feedback {
  id?: number;
  content_type: 'text' | 'image' | 'video' | 'blog' | 'social' | 'ebook' | 'voice' | 'research';
  content_id: number;
  overall_rating: number;
  quality_rating?: number;
  accuracy_rating?: number;
  usefulness_rating?: number;
  feedback_type?: string;
  comments?: string;
  suggestions?: string;
  would_recommend?: boolean;
  met_expectations?: boolean;
  saved_time?: boolean;
  tags?: string[];
  generation_params?: Record<string, any>;
  created_at?: string;
  admin_response?: string;
}

export interface FeedbackStats {
  average_rating: number;
  total_feedback: number;
  rating_distribution: Record<number, number>;
  recommendations: number;
  recent_comments: Array<{
    user__username: string;
    comments: string;
    overall_rating: number;
    created_at: string;
  }>;
}

export interface FeedbackAnalytics {
  period: {
    start: string;
    end: string;
    days: number;
  };
  by_content_type: Record<string, {
    total_feedback: number;
    average_rating: number;
    positive: number;
    neutral: number;
    negative: number;
  }>;
  user_contribution: number;
  total_feedback: number;
}

class FeedbackService {
  async submitFeedback(feedback: Feedback): Promise<any> {
    return apiRequest('/api/feedback/submit/', 'POST', feedback);
  }

  async quickFeedback(
    content_type: string,
    content_id: number,
    is_positive: boolean
  ): Promise<any> {
    return apiRequest('/api/feedback/quick/', 'POST', {
      content_type,
      content_id,
      is_positive,
    });
  }

  async getContentFeedback(
    content_type: string,
    content_id: number
  ): Promise<{
    user_feedback: Feedback | null;
    stats: FeedbackStats | null;
    recent_feedback: any[];
  }> {
    return apiRequest(`/api/feedback/${content_type}/${content_id}/`, 'GET');
  }

  async getFeedbackHistory(params?: {
    content_type?: string;
    min_rating?: number;
    page?: number;
    per_page?: number;
  }): Promise<any> {
    const queryParams = new URLSearchParams(params as any).toString();
    return apiRequest(`/api/feedback/history/?${queryParams}`, 'GET');
  }

  async updateFeedback(feedbackId: number, data: Partial<Feedback>): Promise<any> {
    return apiRequest(`/api/feedback/${feedbackId}/`, 'PUT', data);
  }

  async deleteFeedback(feedbackId: number): Promise<any> {
    return apiRequest(`/api/feedback/${feedbackId}/`, 'DELETE');
  }

  async getAnalytics(days: number = 30, content_type?: string): Promise<FeedbackAnalytics> {
    const params = new URLSearchParams({ days: days.toString() });
    if (content_type) params.append('content_type', content_type);
    return apiRequest(`/api/feedback/analytics/?${params}`, 'GET');
  }
}

export const feedbackService = new FeedbackService();
```

### Step 2.2: Create Reusable Feedback Widget
**File**: `ai-studio-web/src/components/feedback/FeedbackWidget.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Star, ThumbsUp, ThumbsDown, MessageSquare, 
  Send, X, ChevronDown, TrendingUp, AlertCircle 
} from 'lucide-react';
import { feedbackService, Feedback, FeedbackStats } from '../../services/feedbackService';
import toast from 'react-hot-toast';

interface FeedbackWidgetProps {
  contentType: Feedback['content_type'];
  contentId: number;
  contentTitle?: string;
  inline?: boolean;
  showStats?: boolean;
  onFeedbackSubmit?: () => void;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  contentType,
  contentId,
  contentTitle = 'this content',
  inline = false,
  showStats = true,
  onFeedbackSubmit,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [userFeedback, setUserFeedback] = useState<Feedback | null>(null);
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comments, setComments] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [detailedRatings, setDetailedRatings] = useState({
    quality: 0,
    accuracy: 0,
    usefulness: 0,
  });
  const [quickAnswers, setQuickAnswers] = useState({
    would_recommend: null as boolean | null,
    met_expectations: null as boolean | null,
    saved_time: null as boolean | null,
  });
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadFeedback();
  }, [contentType, contentId]);

  const loadFeedback = async () => {
    try {
      const data = await feedbackService.getContentFeedback(contentType, contentId);
      if (data.user_feedback) {
        setUserFeedback(data.user_feedback);
        setRating(data.user_feedback.overall_rating);
        setComments(data.user_feedback.comments || '');
        setSuggestions(data.user_feedback.suggestions || '');
        setDetailedRatings({
          quality: data.user_feedback.quality_rating || 0,
          accuracy: data.user_feedback.accuracy_rating || 0,
          usefulness: data.user_feedback.usefulness_rating || 0,
        });
        setQuickAnswers({
          would_recommend: data.user_feedback.would_recommend || null,
          met_expectations: data.user_feedback.met_expectations || null,
          saved_time: data.user_feedback.saved_time || null,
        });
      }
      setStats(data.stats);
    } catch (error) {
      console.error('Failed to load feedback:', error);
    }
  };

  const handleQuickFeedback = async (isPositive: boolean) => {
    try {
      await feedbackService.quickFeedback(contentType, contentId, isPositive);
      toast.success(`Thank you for your feedback!`);
      loadFeedback();
      onFeedbackSubmit?.();
    } catch (error) {
      toast.error('Failed to submit feedback');
    }
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      toast.error('Please select a rating');
      return;
    }

    setLoading(true);
    try {
      const feedback: Feedback = {
        content_type: contentType,
        content_id: contentId,
        overall_rating: rating,
        quality_rating: detailedRatings.quality || undefined,
        accuracy_rating: detailedRatings.accuracy || undefined,
        usefulness_rating: detailedRatings.usefulness || undefined,
        comments,
        suggestions,
        would_recommend: quickAnswers.would_recommend || undefined,
        met_expectations: quickAnswers.met_expectations || undefined,
        saved_time: quickAnswers.saved_time || undefined,
        feedback_type: rating <= 2 ? 'quality' : rating >= 4 ? 'usefulness' : 'general',
      };

      await feedbackService.submitFeedback(feedback);
      toast.success('Feedback submitted successfully!');
      setIsOpen(false);
      loadFeedback();
      onFeedbackSubmit?.();
    } catch (error) {
      toast.error('Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  const StarRating = ({ value, onChange, size = 'md' }: any) => {
    const sizes = {
      sm: 'w-4 h-4',
      md: 'w-6 h-6',
      lg: 'w-8 h-8',
    };

    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onClick={() => onChange(star)}
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            className="transition-transform hover:scale-110"
          >
            <Star
              className={`${sizes[size]} ${
                (hoverRating || value) >= star
                  ? 'fill-yellow-500 text-yellow-500'
                  : 'text-gray-400'
              }`}
            />
          </button>
        ))}
      </div>
    );
  };

  if (inline) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-white">Rate {contentTitle}</h4>
          {stats && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Star className="w-3 h-3 fill-current" />
              <span>{stats.average_rating?.toFixed(1) || 'N/A'}</span>
              <span>({stats.total_feedback} reviews)</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-4">
          <StarRating value={rating} onChange={setRating} size="sm" />
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleQuickFeedback(true)}
              className="p-1.5 rounded-lg bg-green-600/20 text-green-400 hover:bg-green-600/30 transition-colors"
            >
              <ThumbsUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleQuickFeedback(false)}
              className="p-1.5 rounded-lg bg-red-600/20 text-red-400 hover:bg-red-600/30 transition-colors"
            >
              <ThumbsDown className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsOpen(true)}
              className="p-1.5 rounded-lg bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
            </button>
          </div>
        </div>

        {userFeedback && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <p className="text-xs text-gray-400">
              You rated this {userFeedback.overall_rating} stars
              {userFeedback.created_at && ` on ${new Date(userFeedback.created_at).toLocaleDateString()}`}
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <>
      {/* Floating Feedback Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full shadow-lg flex items-center justify-center text-white z-40"
      >
        <MessageSquare className="w-6 h-6" />
      </motion.button>

      {/* Feedback Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-gray-900 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="sticky top-0 bg-gray-900 border-b border-gray-800 p-6 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">Share Your Feedback</h2>
                  <p className="text-sm text-gray-400 mt-1">Help us improve {contentTitle}</p>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Overall Rating */}
                <div>
                  <label className="block text-sm font-medium text-white mb-3">
                    Overall Rating
                  </label>
                  <div className="flex items-center gap-4">
                    <StarRating value={rating} onChange={setRating} size="lg" />
                    <span className="text-gray-400">
                      {rating === 0 ? 'Select rating' : 
                       rating === 1 ? 'Poor' :
                       rating === 2 ? 'Fair' :
                       rating === 3 ? 'Good' :
                       rating === 4 ? 'Very Good' : 'Excellent'}
                    </span>
                  </div>
                </div>

                {/* Quick Questions */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-white mb-2">
                    Quick Questions
                  </label>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <span className="text-sm text-gray-300">Would you recommend this?</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, would_recommend: true })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.would_recommend === true
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, would_recommend: false })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.would_recommend === false
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <span className="text-sm text-gray-300">Did it meet expectations?</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, met_expectations: true })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.met_expectations === true
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, met_expectations: false })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.met_expectations === false
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                    <span className="text-sm text-gray-300">Did it save you time?</span>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, saved_time: true })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.saved_time === true
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        Yes
                      </button>
                      <button
                        onClick={() => setQuickAnswers({ ...quickAnswers, saved_time: false })}
                        className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                          quickAnswers.saved_time === false
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        No
                      </button>
                    </div>
                  </div>
                </div>

                {/* Detailed Ratings */}
                <div>
                  <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="flex items-center gap-2 text-sm text-purple-400 hover:text-purple-300 transition-colors"
                  >
                    <ChevronDown className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
                    Detailed Ratings (Optional)
                  </button>
                  
                  {showDetails && (
                    <div className="mt-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-300">Quality</span>
                        <StarRating 
                          value={detailedRatings.quality} 
                          onChange={(v: number) => setDetailedRatings({ ...detailedRatings, quality: v })}
                          size="sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-300">Accuracy</span>
                        <StarRating 
                          value={detailedRatings.accuracy} 
                          onChange={(v: number) => setDetailedRatings({ ...detailedRatings, accuracy: v })}
                          size="sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-300">Usefulness</span>
                        <StarRating 
                          value={detailedRatings.usefulness} 
                          onChange={(v: number) => setDetailedRatings({ ...detailedRatings, usefulness: v })}
                          size="sm"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Comments */}
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Comments (Optional)
                  </label>
                  <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    placeholder="What did you like or dislike?"
                    rows={3}
                    className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                  />
                </div>

                {/* Suggestions */}
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Suggestions for Improvement (Optional)
                  </label>
                  <textarea
                    value={suggestions}
                    onChange={(e) => setSuggestions(e.target.value)}
                    placeholder="How can we make this better?"
                    rows={3}
                    className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none"
                  />
                </div>

                {/* Statistics */}
                {showStats && stats && (
                  <div className="bg-gray-800/30 rounded-lg p-4">
                    <h4 className="text-sm font-medium text-white mb-3">Community Feedback</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Average Rating</span>
                        <div className="flex items-center gap-2 mt-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          <span className="text-white font-medium">
                            {stats.average_rating?.toFixed(1) || 'N/A'}
                          </span>
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-400">Total Reviews</span>
                        <p className="text-white font-medium mt-1">{stats.total_feedback}</p>
                      </div>
                    </div>
                    
                    {stats.rating_distribution && (
                      <div className="mt-4 space-y-2">
                        {[5, 4, 3, 2, 1].map((star) => (
                          <div key={star} className="flex items-center gap-2">
                            <span className="text-xs text-gray-400 w-3">{star}</span>
                            <Star className="w-3 h-3 fill-yellow-500 text-yellow-500" />
                            <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-yellow-500 to-orange-500"
                                style={{
                                  width: `${(stats.rating_distribution[star] / stats.total_feedback) * 100}%`,
                                }}
                              />
                            </div>
                            <span className="text-xs text-gray-400 w-8 text-right">
                              {stats.rating_distribution[star]}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="sticky bottom-0 bg-gray-900 border-t border-gray-800 p-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-400">
                    {userFeedback && (
                      <span className="flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        You already rated this content
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => setIsOpen(false)}
                      className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={loading || rating === 0}
                      className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {loading ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          Submit Feedback
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
```

### Step 2.3: Create Feedback Dashboard
**File**: `ai-studio-web/src/pages/feedback/FeedbackDashboard.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Star, TrendingUp, TrendingDown, MessageSquare,
  ThumbsUp, ThumbsDown, BarChart3, Calendar,
  Filter, Download, ChevronRight
} from 'lucide-react';
import { feedbackService, FeedbackAnalytics } from '../../services/feedbackService';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

export const FeedbackDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [feedbackHistory, setFeedbackHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [selectedType, setSelectedType] = useState<string>('all');

  useEffect(() => {
    loadData();
  }, [selectedPeriod, selectedType]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [analyticsData, historyData] = await Promise.all([
        feedbackService.getAnalytics(selectedPeriod, selectedType === 'all' ? undefined : selectedType),
        feedbackService.getFeedbackHistory({ content_type: selectedType === 'all' ? undefined : selectedType })
      ]);
      
      setAnalytics(analyticsData);
      setFeedbackHistory(historyData.feedback);
    } catch (error) {
      console.error('Failed to load feedback data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      text: 'from-blue-500 to-cyan-500',
      image: 'from-purple-500 to-pink-500',
      video: 'from-green-500 to-emerald-500',
      blog: 'from-orange-500 to-red-500',
      social: 'from-indigo-500 to-purple-500',
      ebook: 'from-yellow-500 to-orange-500',
      voice: 'from-teal-500 to-green-500',
      research: 'from-pink-500 to-rose-500',
    };
    return colors[type] || 'from-gray-500 to-gray-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Feedback Analytics</h1>
        <p className="text-gray-400">Track and analyze user feedback across all content</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-8">
        <div className="flex items-center gap-2 bg-gray-800/50 rounded-lg p-1">
          {[7, 30, 90].map((days) => (
            <button
              key={days}
              onClick={() => setSelectedPeriod(days)}
              className={`px-4 py-2 rounded-md transition-all ${
                selectedPeriod === days
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {days}d
            </button>
          ))}
        </div>

        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white"
        >
          <option value="all">All Content Types</option>
          <option value="text">Text</option>
          <option value="image">Images</option>
          <option value="video">Videos</option>
          <option value="blog">Blog Posts</option>
          <option value="social">Social Posts</option>
          <option value="ebook">eBooks</option>
          <option value="voice">Voice</option>
          <option value="research">Research</option>
        </select>

        <button className="ml-auto px-4 py-2 bg-gray-800/50 text-gray-400 rounded-lg hover:text-white transition-colors flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {analytics && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <MessageSquare className="w-8 h-8 text-purple-500" />
                <span className="text-2xl font-bold text-white">
                  {analytics.total_feedback}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Total Feedback</p>
              <p className="text-xs text-gray-500 mt-1">Last {selectedPeriod} days</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <Star className="w-8 h-8 text-yellow-500" />
                <span className="text-2xl font-bold text-white">
                  {Object.values(analytics.by_content_type)
                    .reduce((sum, item) => sum + item.average_rating, 0) / 
                    Object.keys(analytics.by_content_type).length || 0
                  }.toFixed(1)}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Average Rating</p>
              <div className="flex items-center gap-1 mt-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`w-3 h-3 ${
                      star <= Math.round(4.2) 
                        ? 'fill-yellow-500 text-yellow-500'
                        : 'text-gray-600'
                    }`}
                  />
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <ThumbsUp className="w-8 h-8 text-green-500" />
                <span className="text-2xl font-bold text-white">
                  {Object.values(analytics.by_content_type)
                    .reduce((sum, item) => sum + item.positive, 0)}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Positive Feedback</p>
              <p className="text-xs text-green-500 mt-1">4-5 star ratings</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-blue-500" />
                <span className="text-2xl font-bold text-white">
                  {analytics.user_contribution}
                </span>
              </div>
              <p className="text-gray-400 text-sm">Your Contribution</p>
              <p className="text-xs text-gray-500 mt-1">Feedback given</p>
            </motion.div>
          </div>

          {/* Content Type Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-6">Feedback by Content Type</h3>
              <div className="space-y-4">
                {Object.entries(analytics.by_content_type).map(([type, data]) => (
                  <div key={type} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300 capitalize">{type}</span>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-400">
                          {data.total_feedback} reviews
                        </span>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                          <span className="text-white font-medium">
                            {data.average_rating.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <div
                        className="h-2 bg-green-500 rounded-l"
                        style={{ width: `${(data.positive / data.total_feedback) * 100}%` }}
                      />
                      <div
                        className="h-2 bg-yellow-500"
                        style={{ width: `${(data.neutral / data.total_feedback) * 100}%` }}
                      />
                      <div
                        className="h-2 bg-red-500 rounded-r"
                        style={{ width: `${(data.negative / data.total_feedback) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Feedback */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-6">Recent Feedback</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {feedbackHistory.slice(0, 5).map((feedback) => (
                  <div
                    key={feedback.id}
                    className="p-3 bg-gray-900/50 rounded-lg border border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium bg-gradient-to-r ${
                          getTypeColor(feedback.content_type)
                        } text-white`}>
                          {feedback.content_type}
                        </span>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3 h-3 ${
                                i < feedback.overall_rating
                                  ? 'fill-yellow-500 text-yellow-500'
                                  : 'text-gray-600'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(feedback.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {feedback.comments && (
                      <p className="text-sm text-gray-300 line-clamp-2">
                        {feedback.comments}
                      </p>
                    )}
                  </div>
                ))}
              </div>
              
              <button className="mt-4 w-full py-2 bg-purple-600/20 text-purple-400 rounded-lg hover:bg-purple-600/30 transition-colors flex items-center justify-center gap-2">
                View All Feedback
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
```

## Phase 3: Integration Examples (30 minutes)

### Step 3.1: Add Feedback to Image Generator
```tsx
// In ImageGenerator.tsx, after image generation:
import { FeedbackWidget } from '../../components/feedback/FeedbackWidget';

// In the component:
{generatedImage && (
  <div className="mt-4">
    <FeedbackWidget
      contentType="image"
      contentId={generatedImage.id}
      contentTitle="generated image"
      inline={true}
    />
  </div>
)}
```

### Step 3.2: Add Feedback to Video Player
```tsx
// In VideoPlayer.tsx:
{video && (
  <FeedbackWidget
    contentType="video"
    contentId={video.id}
    contentTitle={video.title}
    showStats={true}
  />
)}
```

### Step 3.3: Add Quick Feedback Buttons
```tsx
// Add to any content display:
<div className="flex items-center gap-2">
  <button
    onClick={() => feedbackService.quickFeedback('blog', blogId, true)}
    className="p-2 hover:bg-green-600/20 rounded-lg transition-colors"
  >
    <ThumbsUp className="w-5 h-5 text-green-500" />
  </button>
  <button
    onClick={() => feedbackService.quickFeedback('blog', blogId, false)}
    className="p-2 hover:bg-red-600/20 rounded-lg transition-colors"
  >
    <ThumbsDown className="w-5 h-5 text-red-500" />
  </button>
</div>
```

## Phase 4: Testing & Deployment (30 minutes)

### Migration Commands
```bash
python manage.py makemigrations
python manage.py migrate
```

### Test Checklist
- [ ] Submit feedback for each content type
- [ ] Quick feedback (thumbs up/down) works
- [ ] Star ratings save correctly
- [ ] Comments and suggestions persist
- [ ] Analytics dashboard shows correct data
- [ ] Feedback history displays user's feedback
- [ ] Edit/delete own feedback works
- [ ] Stats calculate correctly
- [ ] Recent feedback shows anonymized data

## API Endpoints Summary

```
# Core Feedback
POST /api/feedback/submit/           # Submit detailed feedback
POST /api/feedback/quick/           # Quick thumbs up/down
GET  /api/feedback/<type>/<id>/     # Get content feedback & stats
PUT  /api/feedback/<feedback_id>/   # Update own feedback
DELETE /api/feedback/<feedback_id>/ # Delete own feedback

# Analytics & History
GET  /api/feedback/history/         # User's feedback history
GET  /api/feedback/analytics/       # Feedback analytics dashboard

# Legacy (keep working)
POST /api/content/blog/<id>/feedback/ # Blog-specific feedback
```

## Success Criteria

The feedback system will be complete when:
- ✅ Users can rate all content types (1-5 stars)
- ✅ Quick feedback (thumbs up/down) available
- ✅ Detailed feedback with comments and suggestions
- ✅ Feedback analytics dashboard working
- ✅ User can view/edit/delete their feedback
- ✅ Average ratings display on content
- ✅ Recent feedback shows (anonymized)
- ✅ Analytics track trends over time
- ✅ AI can learn from feedback patterns

## Next Steps & Enhancements

1. **AI Learning Pipeline** - Use feedback to improve generation
2. **Sentiment Analysis** - Auto-analyze comment sentiment
3. **Feedback Rewards** - Gamification for quality feedback
4. **A/B Testing** - Compare feedback between variations
5. **Export Reports** - PDF/CSV feedback reports
6. **Notification System** - Alert on negative feedback
7. **Feedback API** - Public API for third-party integrations
8. **Machine Learning** - Predict content quality before generation

---

**Prepared by**: Claude
**Date**: 2025-09-01
**For**: AI Content Studio Development Team
**Priority**: HIGH - Essential for quality improvement
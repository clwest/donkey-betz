"""
Views for the mythology lab dashboard and hallucination review system.
"""

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
import uuid
import logging
from typing import Dict, Any, List

from .models import (
    FlaggedHallucination, HallucinationReview, MythologyAlert, 
    MythologyEvent, MythPattern, MythologyGuard
)
from .services import (
    HallucinationFlaggingService, HallucinationVerificationService,
    MythologyDetectionService
)

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for mythology review system.
    Returns stats in the format expected by the frontend.
    """
    try:
        # Get real data from the models
        from django.utils import timezone
        from django.db.models import Q, Avg
        
        today = timezone.now().date()
        
        # Real statistics from database
        total_flagged = FlaggedHallucination.objects.count()
        pending_review = FlaggedHallucination.objects.filter(
            verification_status='pending'
        ).count()
        
        high_priority = FlaggedHallucination.objects.filter(
            priority__in=['high', 'critical']
        ).count()
        
        resolved_today = FlaggedHallucination.objects.filter(
            reviewed_at__date=today,
            verification_status__in=['verified_safe', 'verified_hallucination', 'false_positive']
        ).count()
        
        # Calculate false positive rate
        total_reviewed = FlaggedHallucination.objects.exclude(
            verification_status='pending'
        ).count()
        false_positives = FlaggedHallucination.objects.filter(
            verification_status='false_positive'
        ).count()
        false_positive_rate = (false_positives / total_reviewed * 100) if total_reviewed > 0 else 0.0
        
        # Get average review time
        avg_review_time = HallucinationReview.objects.aggregate(
            avg_time=Avg('review_time_seconds')
        )['avg_time'] or 0.0
        
        # Get recent mythology events
        recent_events = MythologyEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Get unacknowledged alerts
        unacknowledged_alerts = MythologyAlert.objects.filter(acknowledged=False).count()
        
        # Calculate processing rates and neural stats
        total_processed = MythologyEvent.objects.count()
        events_last_hour = MythologyEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Calculate prevention success rate
        prevented_events = MythologyEvent.objects.filter(was_prevented=True).count()
        prevention_rate = (prevented_events / total_processed * 100) if total_processed > 0 else 0.0
        
        # Calculate average risk score
        avg_risk = MythologyEvent.objects.aggregate(
            avg_risk=Avg('risk_level')
        )['avg_risk'] or 0.0
        
        stats = {
            # Main dashboard stats
            'total_flagged': total_flagged,
            'pending_review': pending_review,
            'high_priority': high_priority,
            'resolved_today': resolved_today,
            'false_positive_rate': round(false_positive_rate, 1),
            'avg_review_time': round(avg_review_time, 1),
            'recent_events_24h': recent_events,
            'unacknowledged_alerts': unacknowledged_alerts,
            
            # Neural Processing Stats (to replace N/A values)
            'total_processed': total_processed,
            'events_last_hour': events_last_hour,
            'prevention_success_rate': round(prevention_rate, 1),
            'avg_risk_score': round(avg_risk, 2),
            'processing_rate_per_hour': events_last_hour,  # Events processed in last hour
            'system_efficiency': round(prevention_rate, 1),  # Same as prevention rate
        }
        
        # Add additional stats
        try:
            active_patterns = MythPattern.objects.filter(is_active=True).count()
            stats['active_patterns'] = active_patterns
        except:
            # Models might not exist yet
            pass
        
        return Response(stats, status=200)
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return Response({
            'total_flagged': 0,
            'pending_review': 0,
            'high_priority': 0,
            'resolved_today': 0,
            'false_positive_rate': 0.0,
            'avg_review_time': 0.0
        }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_reviews(request):
    """
    Get pending hallucinations that need review.
    """
    try:
        limit = int(request.GET.get('limit', 50))
        priority = request.GET.get('priority', None)
        flagged_type = request.GET.get('type', None)
        
        queryset = FlaggedHallucination.objects.filter(verification_status='pending')
        
        if priority:
            queryset = queryset.filter(priority=priority)
        if flagged_type:
            queryset = queryset.filter(flagged_type=flagged_type)
            
        flagged_items = list(
            queryset.order_by('-requires_immediate_attention', '-priority', '-flagged_at')[:limit]
        )
        
        # Serialize flagged items
        items_data = []
        for item in flagged_items:
            items_data.append({
                'id': str(item.id),
                'flagged_type': item.flagged_type,
                'flagged_type_display': item.get_flagged_type_display(),
                'original_prompt': item.original_prompt[:200] + '...' if len(item.original_prompt) > 200 else item.original_prompt,
                'flagged_content': item.flagged_content[:300] + '...' if len(item.flagged_content) > 300 else item.flagged_content,
                'patterns_detected': item.patterns_detected,
                'risk_score': item.risk_score,
                'priority': item.priority,
                'priority_color': item.get_severity_color(),
                'requires_immediate_attention': item.requires_immediate_attention,
                'flagged_at': item.flagged_at.isoformat(),
                'auto_verification_attempted': item.auto_verification_attempted,
                'auto_verification_result': item.auto_verification_result if item.auto_verification_attempted else None,
                'user_id': str(item.user.id) if item.user else None,
                'username': item.user.username if item.user else 'Anonymous'
            })
        
        return Response({
            'success': True,
            'items': items_data,
            'count': len(items_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Pending reviews error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_flagged_content(request, flagged_id):
    """
    Trigger auto-verification of flagged content.
    """
    try:
        verification_service = HallucinationVerificationService()
        result = verification_service.verify_flagged_content(flagged_id)
        
        if result['success']:
            return Response({
                'success': True,
                'verification_result': result,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Verification failed')
            }, status=400)
            
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_flagged_content(request, flagged_id):
    """
    Submit human review of flagged content.
    """
    try:
        action = request.data.get('action')  # approved, rejected, needs_investigation, etc.
        notes = request.data.get('notes', '')
        confidence = int(request.data.get('confidence', 5))
        
        if not action:
            return Response({
                'success': False,
                'error': 'Review action is required'
            }, status=400)
        
        # Get flagged item
        try:
            flagged = FlaggedHallucination.objects.get(id=flagged_id)
        except FlaggedHallucination.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Flagged content not found'
            }, status=404)
        
        # Create review record
        review = HallucinationReview.objects.create(
            flagged_hallucination=flagged,
            reviewer=request.user,
            review_action=action,
            review_notes=notes,
            confidence_rating=confidence
        )
        
        # Update flagged status based on action
        status_map = {
            'approved': 'verified_safe',
            'rejected': 'verified_hallucination', 
            'false_positive': 'false_positive',
            'needs_investigation': 'needs_human_review'
        }
        
        new_status = status_map.get(action, 'needs_human_review')
        flagged.verification_status = new_status
        flagged.verified_by = request.user
        flagged.verified_at = datetime.now()
        flagged.reviewed_at = datetime.now()
        flagged.save()
        
        # If confirmed hallucination, potentially update patterns/guards
        if action == 'rejected':
            _learn_from_hallucination(flagged, review)
        
        return Response({
            'success': True,
            'review_id': str(review.id),
            'new_status': new_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Review submission error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_hallucination(request):
    """
    Allow users to report suspected hallucinations.
    """
    try:
        original_prompt = request.data.get('original_prompt', '')
        reported_content = request.data.get('reported_content', '')
        user_notes = request.data.get('user_notes', '')
        session_id = request.data.get('session_id', '')
        
        if not reported_content:
            return Response({
                'success': False,
                'error': 'Reported content is required'
            }, status=400)
        
        flagging_service = HallucinationFlaggingService()
        flagged = flagging_service.flag_user_reported(
            original_prompt=original_prompt,
            reported_content=reported_content,
            user_notes=user_notes,
            user=request.user,
            session_id=session_id
        )
        
        return Response({
            'success': True,
            'flagged_id': str(flagged.id),
            'message': 'Thank you for reporting this content. It has been flagged for review.',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Report hallucination error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mythology_alerts(request):
    """
    Get recent mythology alerts.
    """
    try:
        limit = int(request.GET.get('limit', 20))
        unacknowledged_only = request.GET.get('unacknowledged', 'false').lower() == 'true'
        
        queryset = MythologyAlert.objects.all()
        if unacknowledged_only:
            queryset = queryset.filter(acknowledged=False)
            
        alerts = list(queryset.order_by('-created_at')[:limit])
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': str(alert.id),
                'alert_type': alert.alert_type,
                'alert_type_display': alert.get_alert_type_display(),
                'severity': alert.severity,
                'severity_display': alert.get_severity_display(),
                'title': alert.title,
                'description': alert.description,
                'acknowledged': alert.acknowledged,
                'acknowledged_by': alert.acknowledged_by.username if alert.acknowledged_by else None,
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'created_at': alert.created_at.isoformat(),
                'data': alert.data
            })
        
        return Response({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Mythology alerts error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, alert_id):
    """
    Acknowledge a mythology alert.
    """
    try:
        alert = MythologyAlert.objects.get(id=alert_id)
        alert.acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = datetime.now()
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alert acknowledged',
            'timestamp': datetime.now().isoformat()
        })
        
    except MythologyAlert.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Alert not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Acknowledge alert error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def flagged_content_detail(request, flagged_id):
    """
    Get detailed information about a specific flagged content.
    """
    try:
        flagged = FlaggedHallucination.objects.get(id=flagged_id)
        
        # Get related reviews
        reviews = list(flagged.reviews.all().order_by('-created_at'))
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': str(review.id),
                'reviewer': review.reviewer.username if review.reviewer else 'System',
                'review_action': review.review_action,
                'review_action_display': review.get_review_action_display(),
                'review_notes': review.review_notes,
                'confidence_rating': review.confidence_rating,
                'created_at': review.created_at.isoformat()
            })
        
        detail_data = {
            'id': str(flagged.id),
            'flagged_type': flagged.flagged_type,
            'flagged_type_display': flagged.get_flagged_type_display(),
            'original_prompt': flagged.original_prompt,
            'flagged_content': flagged.flagged_content,
            'context': flagged.context,
            'patterns_detected': flagged.patterns_detected,
            'risk_score': flagged.risk_score,
            'confidence_score': flagged.confidence_score,
            'detection_method': flagged.detection_method,
            'verification_status': flagged.verification_status,
            'verification_status_display': flagged.get_verification_status_display(),
            'verification_notes': flagged.verification_notes,
            'priority': flagged.priority,
            'priority_color': flagged.get_severity_color(),
            'requires_immediate_attention': flagged.requires_immediate_attention,
            'auto_verification_attempted': flagged.auto_verification_attempted,
            'auto_verification_result': flagged.auto_verification_result,
            'auto_verification_agent': flagged.auto_verification_agent,
            'flagged_at': flagged.flagged_at.isoformat(),
            'reviewed_at': flagged.reviewed_at.isoformat() if flagged.reviewed_at else None,
            'user': flagged.user.username if flagged.user else 'Anonymous',
            'session_id': flagged.session_id,
            'metadata': flagged.metadata,
            'reviews': reviews_data
        }
        
        return Response({
            'success': True,
            'flagged_content': detail_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except FlaggedHallucination.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Flagged content not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Flagged content detail error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def _learn_from_hallucination(flagged: FlaggedHallucination, review: HallucinationReview):
    """
    Learn from confirmed hallucinations to improve detection.
    """
    try:
        # Update pattern frequencies
        for pattern_type in flagged.patterns_detected:
            try:
                pattern = MythPattern.objects.get(pattern_type=pattern_type)
                pattern.frequency_count += 1
                pattern.last_seen = datetime.now()
                pattern.save()
            except MythPattern.DoesNotExist:
                # Create new pattern if it doesn't exist
                MythPattern.objects.create(
                    pattern_type=pattern_type,
                    description=f'Pattern detected from flagged content: {flagged.id}',
                    frequency_count=1,
                    last_seen=datetime.now()
                )
        
        # Mark as added to training
        flagged.pattern_updated = True
        flagged.save()
        
        logger.info(f"Learned from hallucination {flagged.id}: updated {len(flagged.patterns_detected)} patterns")
        
    except Exception as e:
        logger.error(f"Learning from hallucination error: {e}")


# New API endpoints for frontend
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def flagged_content_list(request):
    """Get flagged content with filtering and pagination"""
    try:
        from django.core.paginator import Paginator
        from django.utils import timezone
        
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        status_filter = request.GET.get('status', None)
        priority_filter = request.GET.get('priority', None)
        
        # Build queryset
        queryset = FlaggedHallucination.objects.all().order_by('-flagged_at')
        
        if status_filter:
            queryset = queryset.filter(verification_status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Paginate
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize results to match frontend FlaggedContent interface
        results = []
        for item in page_obj.object_list:
            # Map verification_status to frontend status values
            status_mapping = {
                'pending': 'pending',
                'needs_human_review': 'reviewing',
                'verified_safe': 'resolved',
                'verified_hallucination': 'resolved',
                'false_positive': 'dismissed',
            }
            
            # Map flagged_type to frontend flag_type values
            flag_type_mapping = {
                'hallucination': 'misinformation',
                'factual_error': 'misinformation', 
                'inconsistent_knowledge': 'misinformation',
                'temporal_confusion': 'misinformation',
                'harmful_content': 'harmful',
                'inappropriate_content': 'inappropriate',
                'spam_content': 'spam',
                'other': 'other',
            }
            
            results.append({
                'id': item.id,  # Keep as int, not string
                'content_type': 'text',  # Default content type
                'content_id': item.id,  # Use flagged item ID as content ID
                'flag_type': flag_type_mapping.get(item.flagged_type, 'other'),
                'priority': item.priority,
                'status': status_mapping.get(item.verification_status, 'pending'),
                'content_preview': item.flagged_content[:150] + '...' if len(item.flagged_content) > 150 else item.flagged_content,
                'reason': item.patterns_detected[0] if item.patterns_detected else 'Automated detection',
                'flagged_by': {
                    'id': item.user.id if item.user else 1,
                    'username': item.user.username if item.user else 'System',
                    'email': item.user.email if item.user else 'system@donkeybetz.ai'
                },
                'flagged_at': item.flagged_at.isoformat(),
                'reviewed_by': {
                    'id': item.verified_by.id,
                    'username': item.verified_by.username,
                    'email': item.verified_by.email
                } if item.verified_by else None,
                'reviewed_at': item.reviewed_at.isoformat() if item.reviewed_at else None,
                'review_notes': item.verification_notes,
                'metadata': {
                    'risk_score': item.risk_score,
                    'patterns_detected': item.patterns_detected,
                    'priority_color': item.get_severity_color(),
                    'requires_immediate_attention': item.requires_immediate_attention,
                    'original_prompt': item.original_prompt[:100] + '...' if len(item.original_prompt) > 100 else item.original_prompt,
                }
            })
        
        return Response({
            'results': results,
            'count': paginator.count,
            'next': f"/api/v1/mythology/flagged-content/?page={page + 1}" if page_obj.has_next() else None,
            'previous': f"/api/v1/mythology/flagged-content/?page={page - 1}" if page_obj.has_previous() else None,
        }, status=200)
        
    except Exception as e:
        logger.error(f"Flagged content list error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_events(request):
    """Get recent mythology events for Neural Scan section"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # Get query parameters
        limit = int(request.GET.get('limit', 10))
        hours = int(request.GET.get('hours', 24))
        
        # Get recent mythology events
        cutoff_time = timezone.now() - timedelta(hours=hours)
        events = MythologyEvent.objects.filter(
            created_at__gte=cutoff_time
        ).order_by('-created_at')[:limit]
        
        # Serialize events
        events_data = []
        for event in events:
            events_data.append({
                'id': str(event.id),
                'event_type': event.get_event_type_display(),
                'mutation_type': event.get_mutation_type_display() if event.mutation_type else None,
                'patterns_detected': event.patterns_detected,
                'risk_level': event.risk_level,
                'confidence_score': event.confidence_score,
                'was_prevented': event.was_prevented,
                'prevention_method': event.prevention_method,
                'created_at': event.created_at.isoformat(),
                'content_preview': event.original_content[:100] + '...' if len(event.original_content) > 100 else event.original_content,
            })
        
        return Response({
            'events': events_data,
            'count': len(events_data),
            'timeframe_hours': hours,
        }, status=200)
        
    except Exception as e:
        logger.error(f"Recent events error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def submit_review(request):
    """Submit review action for flagged content"""
    try:
        # Mock implementation - replace with actual logic
        return Response({
            'success': True,
            'message': 'Review submitted successfully'
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def report_content(request):
    """Report content for review"""
    try:
        # Mock implementation - replace with actual logic
        return Response({
            'success': True,
            'message': 'Content reported successfully',
            'flag_id': 1
        }, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def notifications_list(request):
    """Get notifications"""
    try:
        # Mock data for now
        return Response([], status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PATCH'])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        return Response({'success': True}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    try:
        return Response({'success': True}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

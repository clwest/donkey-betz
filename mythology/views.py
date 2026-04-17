"""
Views for the mythology lab dashboard and hallucination review system.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta
import logging

from .models import (
    FlaggedHallucination, HallucinationReview, MythologyAlert,
    MythologyEvent, MythPattern, MythologyGuard
)
from .services import (
    HallucinationFlaggingService, HallucinationVerificationService
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
        from django.db.models import Avg
        
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
def flagged_content_detail(request, content_id):
    """
    Get detailed information about a specific flagged content.
    """
    try:
        flagged = FlaggedHallucination.objects.get(id=content_id)
        
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
                'id': str(item.id),  # Convert UUID to string for frontend
                'content_type': 'text',  # Default content type
                'content_id': str(item.id),  # Use flagged item ID as content ID
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
            # Session 898: Extract agent name from source_id when source_type is 'agent'
            agent_name = None
            if event.source_type == 'agent' and event.source_id:
                agent_name = event.source_id  # source_id contains the agent name

            events_data.append({
                'id': str(event.id),
                'event_type': event.get_event_type_display(),
                'mutation_type': event.get_mutation_type_display() if event.mutation_type else None,
                'patterns_detected': event.patterns_detected,
                'risk_level': event.risk_level,
                'confidence_score': event.confidence_score,
                'was_prevented': event.was_prevented,
                'prevention_method': event.prevention_method if event.prevention_method else None,
                'created_at': event.created_at.isoformat(),
                'content_preview': event.original_content[:150] + '...' if len(event.original_content) > 150 else event.original_content,
                'original_content': event.original_content,  # Full content for expanded view
                'mutated_content': event.mutated_content if event.mutated_content else None,  # If mutation occurred
                'source_type': event.source_type if event.source_type else None,
                'source_id': event.source_id if event.source_id else None,  # Session 898: Include source_id
                'agent_name': agent_name,  # Session 898: Direct agent name field
                'metadata': event.metadata if event.metadata else {},
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
@permission_classes([IsAuthenticated])
def submit_review(request):
    """Submit review action for flagged content"""
    try:
        content_id = request.data.get('content_id')
        action = request.data.get('action')
        notes = request.data.get('notes', '')
        edit_content = request.data.get('edit_content', None)
        
        if not content_id or not action:
            return Response({
                'success': False,
                'message': 'Content ID and action are required'
            }, status=400)
        
        # Get the flagged content
        try:
            flagged = FlaggedHallucination.objects.get(id=content_id)
        except FlaggedHallucination.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Flagged content not found'
            }, status=404)
        
        # Map action to verification status
        status_mapping = {
            'approve': 'verified_safe',
            'remove': 'verified_hallucination',
            'edit': 'verified_safe',  # After editing, it's considered safe
            'flag_false_positive': 'false_positive'
        }
        
        # Update flagged content status
        flagged.verification_status = status_mapping.get(action, 'needs_human_review')
        flagged.verification_notes = notes
        flagged.verified_by = request.user
        flagged.verified_at = timezone.now()
        flagged.reviewed_at = timezone.now()
        
        # If content was edited, update it
        if action == 'edit' and edit_content:
            flagged.flagged_content = edit_content
            flagged.metadata['edited'] = True
            flagged.metadata['original_content'] = flagged.flagged_content
        
        flagged.save()
        
        # Create a review record
        review = HallucinationReview.objects.create(
            flagged_hallucination=flagged,
            reviewer=request.user,
            review_action=action,
            review_notes=notes,
            confidence_rating=5  # Default confidence
        )

        # Session 1095 Tier 1: feed the review back to pattern quality tuning.
        # Over-broad patterns that produce false positives gradually lose
        # severity weight and eventually auto-disable. Correct catches
        # reinforce the pattern.
        tuning_result = {}
        try:
            from .feedback_tuning import tune_patterns_from_review
            tuning_result = tune_patterns_from_review(flagged, action)
        except Exception as e:
            logger.warning(f"Pattern tuning failed for review {review.id}: {e}")

        return Response({
            'success': True,
            'message': f'Content has been {action}d successfully',
            'pattern_tuning': tuning_result,
        }, status=200)
    except Exception as e:
        logger.error(f"Submit review error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_review(request):
    """Session 1095 Tier 1: bulk-review pending FlaggedHallucinations by pattern.

    When an over-broad regex produces hundreds of false-positive flags,
    operators shouldn't have to click through each one. This endpoint
    marks all pending flags matching a `pattern_type` with a single
    review action, and applies pattern tuning ONCE (not N times) to
    avoid unfairly nuking a pattern's severity from one bulk action.

    Request body:
        {
            "pattern_type": "dangerous_myth",
            "action": "flag_false_positive",
            "notes": "regex catches research content about legal topics",
            "priority": "critical"  // optional filter
        }

    Response:
        {
            "success": true,
            "reviewed_count": 312,
            "new_status": "false_positive",
            "pattern_tuning": {
                "patterns_updated": 1,
                "auto_disabled": [],
                "action_class": "false_positive"
            }
        }
    """
    try:
        pattern_type = request.data.get('pattern_type', '').strip()
        action = request.data.get('action', '').strip()
        notes = request.data.get('notes', '')
        priority = request.data.get('priority', '').strip() or None

        if not pattern_type or not action:
            return Response({
                'success': False,
                'message': 'pattern_type and action are required',
            }, status=400)

        valid_actions = {
            'approve', 'remove', 'flag_false_positive',
            'verified_safe', 'verified_hallucination',
        }
        if action not in valid_actions:
            return Response({
                'success': False,
                'message': f'Invalid action. Must be one of: {sorted(valid_actions)}',
            }, status=400)

        from .feedback_tuning import bulk_review_by_pattern
        result = bulk_review_by_pattern(
            pattern_type=pattern_type,
            review_action=action,
            reviewer=request.user,
            notes=notes,
            priority_filter=priority,
        )
        return Response({
            'success': True,
            **result,
        }, status=200)
    except Exception as e:
        logger.exception(f"Bulk review error: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_content(request):
    """Report content for review"""
    try:
        content_type = request.data.get('content_type')
        content_id = request.data.get('content_id')
        flag_type = request.data.get('flag_type')
        reason = request.data.get('reason')
        additional_info = request.data.get('additional_info', '')
        
        if not all([content_type, content_id, flag_type, reason]):
            return Response({
                'success': False,
                'message': 'All required fields must be provided'
            }, status=400)
        
        # Map flag types to flagged types
        flag_type_mapping = {
            'misinformation': 'hallucination',
            'harmful': 'harmful_content',
            'inappropriate': 'inappropriate_content',
            'spam': 'spam_content',
            'other': 'other'
        }
        
        # Create flagged content entry
        flagged = FlaggedHallucination.objects.create(
            flagged_type=flag_type_mapping.get(flag_type, 'other'),
            original_prompt=f"User reported {content_type} #{content_id}",
            flagged_content=f"{reason}\n\nAdditional info: {additional_info}" if additional_info else reason,
            patterns_detected=[flag_type],
            risk_score=0.5,  # Default medium risk for user reports
            confidence_score=0.8,  # High confidence for user reports
            detection_method='user_report',
            verification_status='pending',
            priority='medium' if flag_type != 'harmful' else 'high',
            requires_immediate_attention=flag_type == 'harmful',
            user=request.user,
            session_id=request.session.session_key if hasattr(request, 'session') else None,
            metadata={
                'content_type': content_type,
                'content_id': content_id,
                'flag_type': flag_type,
                'user_reason': reason,
                'additional_info': additional_info
            }
        )
        
        # Create an alert if it's high priority
        if flagged.priority in ['high', 'critical']:
            MythologyAlert.objects.create(
                alert_type='immediate_review',
                severity='high' if flagged.priority == 'high' else 'critical',
                title=f'User reported {flag_type} content',
                description=f"User {request.user.username} reported {content_type} #{content_id} as {flag_type}",
                data={
                    'flagged_id': str(flagged.id),
                    'reporter': request.user.username,
                    'content_info': {
                        'type': content_type,
                        'id': content_id
                    }
                }
            )
        
        return Response({
            'success': True,
            'message': 'Content reported successfully',
            'flag_id': flagged.id
        }, status=200)
    except Exception as e:
        logger.error(f"Report content error: {e}")
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


# =============================================================================
# Session 541: Mythology Quarantine API
# =============================================================================

@api_view(['GET'])
def quarantine_list(request):
    """
    List quarantined knowledge transfers blocked by mythology validation.

    GET /api/v1/mythology/quarantine/

    Query params:
        status: pending|approved|rejected|edited (default: all)
        teacher: Filter by teacher agent name
        limit: Max items to return (default: 50)
    """
    try:
        from core.models import MythologyQuarantine

        queryset = MythologyQuarantine.objects.all()

        # Filter by status
        status = request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by teacher
        teacher = request.GET.get('teacher')
        if teacher:
            queryset = queryset.filter(teacher_agent__name__icontains=teacher)

        # Limit results
        limit = int(request.GET.get('limit', 50))
        queryset = queryset.order_by('-created_at')[:limit]

        items = []
        for q in queryset:
            items.append({
                'id': str(q.id),
                'teacher': q.teacher_agent.name,
                'student': q.student_agent.name,
                'blocked_title': q.blocked_title,
                'blocked_content': q.blocked_content[:500] if q.blocked_content else '',
                'violation_type': q.violation_type,
                'violation_count': q.violation_count,
                'violation_patterns': q.violation_patterns,
                'mythology_warning': q.mythology_warning,
                'spider_sources': q.spider_sources,
                'status': q.status,
                'created_at': q.created_at.isoformat(),
                'reviewed_at': q.reviewed_at.isoformat() if q.reviewed_at else None,
                'reviewed_by': q.reviewed_by,
            })

        # Get summary stats
        total = MythologyQuarantine.objects.count()
        pending = MythologyQuarantine.objects.filter(status='pending').count()

        return Response({
            'success': True,
            'items': items,
            'total': total,
            'pending': pending,
            'returned': len(items),
        })
    except Exception as e:
        logger.exception(f"Quarantine list error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def quarantine_detail(request, quarantine_id):
    """
    Get details of a specific quarantined item.

    GET /api/v1/mythology/quarantine/<uuid>/
    """
    try:
        from core.models import MythologyQuarantine

        q = MythologyQuarantine.objects.select_related(
            'teacher_agent', 'student_agent', 'connection', 'source_knowledge'
        ).get(id=quarantine_id)

        return Response({
            'success': True,
            'item': {
                'id': str(q.id),
                'teacher': {
                    'name': q.teacher_agent.name,
                    'id': str(q.teacher_agent.id),
                },
                'student': {
                    'name': q.student_agent.name,
                    'id': str(q.student_agent.id),
                },
                'connection': {
                    'id': str(q.connection.id) if q.connection else None,
                    'strength': q.connection.strength if q.connection else None,
                    'mythology_blocks': q.connection.mythology_blocks if q.connection else 0,
                },
                'source_knowledge': {
                    'id': str(q.source_knowledge.id) if q.source_knowledge else None,
                    'title': q.source_knowledge.title if q.source_knowledge else None,
                    'is_active': q.source_knowledge.is_active if q.source_knowledge else None,
                },
                'blocked_title': q.blocked_title,
                'blocked_content': q.blocked_content,
                'blocked_summary': q.blocked_summary,
                'violation_type': q.violation_type,
                'violation_count': q.violation_count,
                'violation_patterns': q.violation_patterns,
                'mythology_warning': q.mythology_warning,
                'spider_sources': q.spider_sources,
                'source_urls': q.source_urls,
                'status': q.status,
                'created_at': q.created_at.isoformat(),
                'reviewed_at': q.reviewed_at.isoformat() if q.reviewed_at else None,
                'reviewed_by': q.reviewed_by,
                'review_notes': q.review_notes,
            }
        })
    except MythologyQuarantine.DoesNotExist:
        return Response({'error': 'Quarantine item not found'}, status=404)
    except Exception as e:
        logger.exception(f"Quarantine detail error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def quarantine_approve(request, quarantine_id):
    """
    Approve a quarantined item (mark as false positive).

    POST /api/v1/mythology/quarantine/<uuid>/approve/
    """
    try:
        from core.models import MythologyQuarantine

        q = MythologyQuarantine.objects.get(id=quarantine_id)
        reviewed_by = request.user.username if request.user.is_authenticated else 'anonymous'
        q.approve(reviewed_by=reviewed_by)

        logger.info(f"🟢 [QUARANTINE] Approved: {q.blocked_title[:50]} by {reviewed_by}")

        return Response({
            'success': True,
            'message': f'Quarantine item approved as false positive',
            'id': str(q.id),
            'status': q.status,
        })
    except MythologyQuarantine.DoesNotExist:
        return Response({'error': 'Quarantine item not found'}, status=404)
    except Exception as e:
        logger.exception(f"Quarantine approve error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def quarantine_reject(request, quarantine_id):
    """
    Reject a quarantined item (confirm as myth, optionally deactivate source).

    POST /api/v1/mythology/quarantine/<uuid>/reject/
    Body: { "notes": "optional review notes", "deactivate_source": true }
    """
    try:
        from core.models import MythologyQuarantine

        q = MythologyQuarantine.objects.get(id=quarantine_id)
        reviewed_by = request.user.username if request.user.is_authenticated else 'anonymous'
        notes = request.data.get('notes', '')

        q.reject(reviewed_by=reviewed_by, notes=notes)

        # Optionally deactivate the source knowledge
        if request.data.get('deactivate_source') and q.source_knowledge:
            q.source_knowledge.is_active = False
            q.source_knowledge.save()

        logger.info(f"🔴 [QUARANTINE] Rejected: {q.blocked_title[:50]} by {reviewed_by}")

        return Response({
            'success': True,
            'message': f'Quarantine item rejected as confirmed myth',
            'id': str(q.id),
            'status': q.status,
            'source_deactivated': request.data.get('deactivate_source', False),
        })
    except MythologyQuarantine.DoesNotExist:
        return Response({'error': 'Quarantine item not found'}, status=404)
    except Exception as e:
        logger.exception(f"Quarantine reject error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def quarantine_stats(request):
    """
    Get quarantine statistics.

    GET /api/v1/mythology/quarantine/stats/
    """
    try:
        from core.models import MythologyQuarantine, AgentLearningConnection
        from django.db.models import Count, Sum

        # Basic counts
        total = MythologyQuarantine.objects.count()
        by_status = dict(MythologyQuarantine.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))

        # By violation type
        by_type = dict(MythologyQuarantine.objects.values('violation_type').annotate(count=Count('id')).values_list('violation_type', 'count'))

        # Top teachers with blocks
        top_teachers = list(
            MythologyQuarantine.objects.values('teacher_agent__name')
            .annotate(blocks=Count('id'))
            .order_by('-blocks')[:10]
        )

        # Connection trust decay stats
        connections_with_blocks = AgentLearningConnection.objects.filter(
            mythology_blocks__gt=0
        ).count()
        total_connection_blocks = AgentLearningConnection.objects.aggregate(
            total=Sum('mythology_blocks')
        )['total'] or 0

        return Response({
            'success': True,
            'stats': {
                'total_quarantined': total,
                'by_status': {
                    'pending': by_status.get('pending', 0),
                    'approved': by_status.get('approved', 0),
                    'rejected': by_status.get('rejected', 0),
                    'edited': by_status.get('edited', 0),
                },
                'by_violation_type': by_type,
                'top_teachers_with_blocks': top_teachers,
                'connections_with_blocks': connections_with_blocks,
                'total_connection_blocks': total_connection_blocks,
            }
        })
    except Exception as e:
        logger.exception(f"Quarantine stats error: {e}")
        return Response({'error': str(e)}, status=500)


# Session 972: Patterns and Guards list endpoints (requested by IntelligenceTab Safety sub-tab)

@api_view(['GET'])
@permission_classes([])
def list_patterns(request):
    """GET /api/mythology/patterns/ — list active myth patterns."""
    try:
        limit = int(request.GET.get('limit', 20))
        patterns = MythPattern.objects.filter(is_active=True).order_by('-frequency_count')[:limit]
        return Response({
            'success': True,
            'patterns': [{
                'id': str(p.id),
                'pattern_type': p.pattern_type,
                'description': p.description,
                'frequency_count': p.frequency_count,
                'times_prevented': p.times_prevented,
                'prevention_success_rate': p.prevention_success_rate,
                'severity_weight': p.severity_weight,
                'last_seen': p.last_seen.isoformat() if p.last_seen else None,
                'detection_keywords': p.detection_keywords,
            } for p in patterns],
            'count': len(patterns),
        })
    except Exception as e:
        logger.exception(f"List patterns error: {e}")
        return Response({'success': True, 'patterns': [], 'count': 0})


@api_view(['GET'])
@permission_classes([])
def list_guards(request):
    """GET /api/mythology/guards/ — list active mythology guards."""
    try:
        limit = int(request.GET.get('limit', 20))
        guards = MythologyGuard.objects.filter(is_active=True).order_by('-priority')[:limit]
        return Response({
            'success': True,
            'guards': [{
                'id': str(g.id),
                'name': g.name,
                'description': g.description,
                'guard_type': g.guard_type,
                'times_triggered': g.times_triggered,
                'times_successful': g.times_successful,
                'effectiveness_rate': g.effectiveness_rate,
                'priority': g.priority,
            } for g in guards],
            'count': len(guards),
        })
    except Exception as e:
        logger.exception(f"List guards error: {e}")
        return Response({'success': True, 'guards': [], 'count': 0})

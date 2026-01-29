"""
WorkspaceTrigger API - Autonomous Work Queue Management
Session 861B: Expose WorkspaceTrigger system for UI visibility

This provides REST API access to the WorkspaceTrigger queue,
enabling visibility into the autonomous workspace autopilot system.
"""

import logging
from uuid import UUID
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers

from core.models_skin_layer import (
    ProjectWorkspace,
    WorkspaceTrigger,
    WorkspaceTriggerConfig,
    WorkspaceTriggerType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Serializers
# =============================================================================


class WorkspaceTriggerSerializer(serializers.ModelSerializer):
    """Full serializer for workspace trigger details."""

    workspace_name = serializers.CharField(source='workspace.name', read_only=True, allow_null=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    time_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceTrigger
        fields = [
            'id',
            'trigger_type',
            'trigger_type_display',
            'title',
            'description',
            'workspace',
            'workspace_name',
            'target_agent',
            'target_category',
            'source_spider',
            'source_spider_data_id',
            'source_agent',
            'source_user_id',
            'context_data',
            'priority',
            'priority_display',
            'expires_at',
            'is_expired',
            'time_until_expiry',
            'ttl_hours',
            'status',
            'execution_id',
            'result_summary',
            'error_message',
            'queued_at',
            'started_at',
            'completed_at',
            'execution_time_ms',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'dedupe_hash',
            'execution_id',
            'result_summary',
            'error_message',
            'queued_at',
            'started_at',
            'completed_at',
            'execution_time_ms',
            'created_at',
            'updated_at',
        ]

    def get_time_until_expiry(self, obj) -> str:
        """Get human-readable time until expiry."""
        if obj.is_expired:
            return 'Expired'
        delta = obj.expires_at - timezone.now()
        hours = int(delta.total_seconds() / 3600)
        minutes = int((delta.total_seconds() % 3600) / 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class WorkspaceTriggerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for trigger list views."""

    workspace_name = serializers.CharField(source='workspace.name', read_only=True, allow_null=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkspaceTrigger
        fields = [
            'id',
            'trigger_type',
            'trigger_type_display',
            'title',
            'workspace_name',
            'target_agent',
            'target_category',
            'source_spider',
            'priority',
            'priority_display',
            'status',
            'is_expired',
            'expires_at',
            'created_at',
            'execution_time_ms',
        ]
        read_only_fields = fields


class WorkspaceTriggerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating manual triggers."""

    class Meta:
        model = WorkspaceTrigger
        fields = [
            'trigger_type',
            'title',
            'description',
            'workspace',
            'target_agent',
            'target_category',
            'context_data',
            'priority',
            'ttl_hours',
        ]

    def create(self, validated_data):
        """Create trigger with proper defaults."""
        import hashlib

        # Generate dedupe hash
        title = validated_data.get('title', '')
        target_agent = validated_data.get('target_agent', '')
        target_category = validated_data.get('target_category', '')
        trigger_type = validated_data.get('trigger_type', '')
        dedupe_string = f"{trigger_type}:{title}:{target_agent}:{target_category}:manual"
        validated_data['dedupe_hash'] = hashlib.sha256(dedupe_string.encode()).hexdigest()

        # Calculate expires_at
        ttl_hours = validated_data.get('ttl_hours', 24)
        validated_data['expires_at'] = timezone.now() + timedelta(hours=ttl_hours)

        return super().create(validated_data)


class WorkspaceTriggerConfigSerializer(serializers.ModelSerializer):
    """Full serializer for trigger configuration."""

    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)

    class Meta:
        model = WorkspaceTriggerConfig
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'target_spiders',
            'match_field',
            'match_operator',
            'match_value',
            'trigger_type',
            'trigger_type_display',
            'trigger_title_template',
            'priority',
            'ttl_hours',
            'target_agent',
            'target_category',
            'cooldown_minutes',
            'last_triggered_at',
            'total_triggers_created',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'last_triggered_at',
            'total_triggers_created',
            'created_at',
            'updated_at',
        ]


# =============================================================================
# Pagination
# =============================================================================


class TriggerPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# =============================================================================
# ViewSets
# =============================================================================


class WorkspaceTriggerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkspaceTrigger CRUD and actions.

    Session 861B: Exposes the autonomous workspace trigger queue.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = TriggerPagination

    def get_queryset(self):
        """Filter triggers - optionally by status, type, priority."""
        qs = WorkspaceTrigger.objects.all().select_related('workspace')

        # Status filter
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        # Type filter
        type_filter = self.request.query_params.get('trigger_type')
        if type_filter:
            qs = qs.filter(trigger_type=type_filter)

        # Priority filter
        min_priority = self.request.query_params.get('min_priority')
        if min_priority:
            qs = qs.filter(priority__gte=int(min_priority))

        # Category filter
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(target_category=category)

        # Workspace filter
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        # Expired filter
        show_expired = self.request.query_params.get('show_expired', 'false').lower() == 'true'
        if not show_expired:
            qs = qs.filter(
                Q(expires_at__gt=timezone.now()) | Q(status__in=['completed', 'failed'])
            )

        return qs.order_by('-priority', '-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkspaceTriggerListSerializer
        if self.action == 'create':
            return WorkspaceTriggerCreateSerializer
        return WorkspaceTriggerSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get trigger queue statistics."""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Base queryset
        all_triggers = WorkspaceTrigger.objects.all()

        # Status counts
        status_counts = dict(
            all_triggers.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )

        # By type (last 7d)
        by_type = dict(
            all_triggers.filter(created_at__gte=last_7d)
            .values('trigger_type')
            .annotate(count=Count('id'))
            .values_list('trigger_type', 'count')
        )

        # By priority (pending only)
        by_priority = dict(
            all_triggers.filter(status='pending')
            .values('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )

        # Execution stats (last 24h)
        completed_24h = all_triggers.filter(
            status='completed',
            completed_at__gte=last_24h
        )
        failed_24h = all_triggers.filter(
            status='failed',
            completed_at__gte=last_24h
        )

        # Average execution time (completed last 24h)
        from django.db.models import Avg
        avg_exec_time = completed_24h.aggregate(avg=Avg('execution_time_ms'))['avg'] or 0

        # Expired triggers (last 7d)
        expired_count = all_triggers.filter(
            status='expired',
            updated_at__gte=last_7d
        ).count()

        return Response({
            'status_counts': {
                'pending': status_counts.get('pending', 0),
                'queued': status_counts.get('queued', 0),
                'in_progress': status_counts.get('in_progress', 0),
                'completed': status_counts.get('completed', 0),
                'failed': status_counts.get('failed', 0),
                'expired': status_counts.get('expired', 0),
                'skipped': status_counts.get('skipped', 0),
            },
            'by_type_7d': by_type,
            'by_priority_pending': {
                1: by_priority.get(1, 0),  # Low
                2: by_priority.get(2, 0),  # Normal
                3: by_priority.get(3, 0),  # High
                4: by_priority.get(4, 0),  # Urgent
                5: by_priority.get(5, 0),  # Critical
            },
            'last_24h': {
                'completed': completed_24h.count(),
                'failed': failed_24h.count(),
                'avg_execution_time_ms': round(avg_exec_time, 2),
            },
            'expired_7d': expired_count,
            'queue_depth': status_counts.get('pending', 0) + status_counts.get('queued', 0),
        })

    @action(detail=False, methods=['get'])
    def trigger_types(self, request):
        """Get available trigger types."""
        return Response({
            'types': [
                {'value': choice[0], 'label': choice[1]}
                for choice in WorkspaceTriggerType.choices
            ]
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a pending trigger."""
        trigger = self.get_object()

        if trigger.status not in ['pending', 'queued']:
            return Response(
                {'error': f'Cannot cancel trigger in status: {trigger.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        trigger.status = 'skipped'
        trigger.result_summary = 'Cancelled by user'
        trigger.save()

        return Response({'status': 'cancelled', 'trigger_id': str(trigger.id)})

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed trigger."""
        trigger = self.get_object()

        if trigger.status not in ['failed', 'expired', 'skipped']:
            return Response(
                {'error': f'Cannot retry trigger in status: {trigger.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reset status and extend TTL
        trigger.status = 'pending'
        trigger.expires_at = timezone.now() + timedelta(hours=trigger.ttl_hours)
        trigger.error_message = ''
        trigger.result_summary = ''
        trigger.execution_id = None
        trigger.queued_at = None
        trigger.started_at = None
        trigger.completed_at = None
        trigger.execution_time_ms = None
        trigger.save()

        return Response({'status': 'retried', 'trigger_id': str(trigger.id)})

    @action(detail=True, methods=['post'])
    def bump_priority(self, request, pk=None):
        """Increase trigger priority."""
        trigger = self.get_object()

        if trigger.status != 'pending':
            return Response(
                {'error': f'Cannot bump priority for trigger in status: {trigger.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_priority = min(5, trigger.priority + 1)
        trigger.priority = new_priority
        trigger.save()

        return Response({
            'status': 'bumped',
            'trigger_id': str(trigger.id),
            'new_priority': new_priority,
            'priority_display': trigger.get_priority_display(),
        })


class WorkspaceTriggerConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkspaceTriggerConfig CRUD.

    Session 861B: Manage trigger configuration rules.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = WorkspaceTriggerConfigSerializer
    pagination_class = TriggerPagination

    def get_queryset(self):
        """Filter configs - optionally by active status."""
        qs = WorkspaceTriggerConfig.objects.all()

        # Active filter
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')

        # Trigger type filter
        trigger_type = self.request.query_params.get('trigger_type')
        if trigger_type:
            qs = qs.filter(trigger_type=trigger_type)

        return qs.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle config active status."""
        config = self.get_object()
        config.is_active = not config.is_active
        config.save()

        return Response({
            'id': str(config.id),
            'name': config.name,
            'is_active': config.is_active,
        })

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test config against sample data (dry run)."""
        config = self.get_object()

        # Get sample data from request
        sample_data = request.data.get('sample_data', {})

        if not sample_data:
            return Response(
                {'error': 'sample_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Test the match
        import re
        from functools import reduce

        def get_nested_value(data, path):
            """Get value from nested dict using dot notation."""
            try:
                return reduce(lambda d, key: d[int(key) if key.isdigit() else key],
                             path.split('.'), data)
            except (KeyError, IndexError, TypeError):
                return None

        value = get_nested_value(sample_data, config.match_field)

        if value is None:
            return Response({
                'match': False,
                'reason': f'Field "{config.match_field}" not found in sample data',
                'extracted_value': None,
            })

        # Test operator
        match = False
        if config.match_operator == 'contains':
            keywords = [k.strip().lower() for k in config.match_value.split('|')]
            match = any(k in str(value).lower() for k in keywords)
        elif config.match_operator == 'regex':
            try:
                match = bool(re.search(config.match_value, str(value), re.IGNORECASE))
            except re.error:
                return Response({
                    'match': False,
                    'reason': 'Invalid regex pattern',
                    'extracted_value': str(value),
                })
        elif config.match_operator == 'gt':
            try:
                match = float(value) > float(config.match_value)
            except (ValueError, TypeError):
                match = False
        elif config.match_operator == 'lt':
            try:
                match = float(value) < float(config.match_value)
            except (ValueError, TypeError):
                match = False

        return Response({
            'match': match,
            'extracted_value': str(value) if value else None,
            'operator': config.match_operator,
            'match_value': config.match_value,
            'would_create_trigger': match and config.is_active,
        })


# =============================================================================
# Standalone Endpoints
# =============================================================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def autopilot_status(request):
    """
    Get autopilot system status.

    Returns queue health, last execution info, and configuration.
    """
    now = timezone.now()
    last_hour = now - timedelta(hours=1)

    # Queue stats
    pending = WorkspaceTrigger.objects.filter(status='pending').count()
    in_progress = WorkspaceTrigger.objects.filter(status='in_progress').count()

    # Recent completions
    recent_completed = WorkspaceTrigger.objects.filter(
        status='completed',
        completed_at__gte=last_hour
    ).count()
    recent_failed = WorkspaceTrigger.objects.filter(
        status='failed',
        completed_at__gte=last_hour
    ).count()

    # Last trigger processed
    last_processed = WorkspaceTrigger.objects.filter(
        status__in=['completed', 'failed']
    ).order_by('-completed_at').first()

    # Active configs
    active_configs = WorkspaceTriggerConfig.objects.filter(is_active=True).count()
    total_configs = WorkspaceTriggerConfig.objects.count()

    return Response({
        'queue': {
            'pending': pending,
            'in_progress': in_progress,
            'depth': pending + in_progress,
        },
        'last_hour': {
            'completed': recent_completed,
            'failed': recent_failed,
            'success_rate': (
                round(recent_completed / (recent_completed + recent_failed) * 100, 1)
                if (recent_completed + recent_failed) > 0
                else 100.0
            ),
        },
        'last_processed': {
            'id': str(last_processed.id) if last_processed else None,
            'title': last_processed.title if last_processed else None,
            'status': last_processed.status if last_processed else None,
            'completed_at': last_processed.completed_at if last_processed else None,
        } if last_processed else None,
        'configs': {
            'active': active_configs,
            'total': total_configs,
        },
        'status': 'healthy' if in_progress <= 5 else 'busy',
    })

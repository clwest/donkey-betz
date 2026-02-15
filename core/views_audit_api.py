"""
Session 972: Read-only API ViewSets for audit trail models.

Exposes DecisionRecord, ToolCallRecord, and SignalCluster via
REST API so the frontend (and external tools) can query agent
decisions and tool calls that were previously write-only.

Endpoints (all under /api/v1/):
  GET /decision-records/          — paginated list
  GET /decision-records/<uuid>/   — detail
  GET /tool-call-records/         — paginated list
  GET /tool-call-records/<uuid>/  — detail
  GET /signal-clusters/           — paginated list
  GET /signal-clusters/<uuid>/    — detail
"""

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from core.views.agents import StandardResultsSetPagination
from core.models_decision_records import DecisionRecord
from core.models_tool_calls import ToolCallRecord, ToolCallAggregate
from core.models_signal_intelligence import SignalCluster
from core.serializers_audit import (
    DecisionRecordListSerializer,
    DecisionRecordDetailSerializer,
    ToolCallRecordListSerializer,
    ToolCallRecordDetailSerializer,
    ToolCallAggregateSerializer,
    SignalClusterListSerializer,
    SignalClusterDetailSerializer,
)


class DecisionRecordViewSet(ReadOnlyModelViewSet):
    queryset = DecisionRecord.objects.order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['agent_name', 'decision_type', 'was_successful']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DecisionRecordDetailSerializer
        return DecisionRecordListSerializer


class ToolCallRecordViewSet(ReadOnlyModelViewSet):
    queryset = ToolCallRecord.objects.order_by('-created_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['agent_name', 'tool_name', 'success']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ToolCallRecordDetailSerializer
        return ToolCallRecordListSerializer


class ToolCallAggregateViewSet(ReadOnlyModelViewSet):
    """Session 1007: Pre-aggregated tool call stats for dashboard queries."""
    queryset = ToolCallAggregate.objects.order_by('-date', '-total_calls')
    serializer_class = ToolCallAggregateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['agent_name', 'tool_name', 'date']


class SignalClusterViewSet(ReadOnlyModelViewSet):
    queryset = SignalCluster.objects.order_by('-detected_at')
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pattern_type', 'status']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SignalClusterDetailSerializer
        return SignalClusterListSerializer

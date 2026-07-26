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

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
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
    """S2971: extended with custom filters for Signal Intelligence UI.

    Base filters via DjangoFilterBackend: pattern_type, status.
    Extra filters parsed in get_queryset() (JSONField / computed cutoffs
    that DjangoFilterBackend can't express declaratively):
      - window_hours (int)   → detected_at >= now - hours
      - min_confidence (float) → confidence__gte
      - source_spider (str, may repeat) → source_breakdown__has_key
      - query (str)          → name/keywords icontains OR
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pattern_type', 'status']

    # S2971: base queryset is a classmethod-friendly default. get_queryset()
    # layers imperative filters on top so DjangoFilterBackend still handles
    # pattern_type + status declaratively without a custom FilterSet class.
    queryset = SignalCluster.objects.order_by('-detected_at')

    def get_queryset(self):
        qs = SignalCluster.objects.all().order_by('-detected_at')
        params = self.request.query_params

        window_hours_raw = params.get('window_hours')
        if window_hours_raw:
            try:
                hours = max(1, min(int(window_hours_raw), 24 * 90))
                cutoff = timezone.now() - timedelta(hours=hours)
                qs = qs.filter(detected_at__gte=cutoff)
            except (TypeError, ValueError):
                pass

        min_confidence_raw = params.get('min_confidence')
        if min_confidence_raw:
            try:
                min_conf = float(min_confidence_raw)
                qs = qs.filter(confidence__gte=min_conf)
            except (TypeError, ValueError):
                pass

        # ?source_spider=reddit&source_spider=bluesky OR comma-separated
        source_spiders = params.getlist('source_spider') or []
        if not source_spiders:
            raw = params.get('source_spider') or ''
            if raw:
                source_spiders = [p.strip() for p in raw.split(',') if p.strip()]
        for spider in source_spiders:
            # source_breakdown is a JSONField dict {spider_name: count}. Matching
            # keys with has_key is the right shape for "clusters that saw this
            # source at all". Rigby T1 gotcha #2.
            qs = qs.filter(source_breakdown__has_key=spider)

        query = (params.get('query') or '').strip()
        if query:
            # keywords is JSONField(list); icontains on JSONField stringifies
            # the JSON and substring-matches — works for our v1 needs (Rigby
            # T1 gotcha #1). Widen to name OR keywords.
            qs = qs.filter(Q(name__icontains=query) | Q(keywords__icontains=query))

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SignalClusterDetailSerializer
        return SignalClusterListSerializer

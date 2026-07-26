"""
Session 972: Serializers for audit trail API endpoints.

Provides read-only serializers for DecisionRecord, ToolCallRecord,
and SignalCluster — models that auto-record agent decisions and tool
calls but previously had no way to query them via API.
"""

from rest_framework import serializers

from core.models_decision_records import DecisionRecord
from core.models_tool_calls import ToolCallRecord, ToolCallAggregate
from core.models_signal_intelligence import SignalCluster


# ── DecisionRecord ──

class DecisionRecordListSerializer(serializers.ModelSerializer):
    action_preview = serializers.SerializerMethodField()

    class Meta:
        model = DecisionRecord
        fields = [
            'id', 'agent_name', 'decision_type', 'action_preview',
            'confidence', 'was_successful', 'created_at',
        ]

    def get_action_preview(self, obj):
        return obj.action[:100] if obj.action else ''


class DecisionRecordDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionRecord
        fields = [
            'id', 'trace_id', 'conversation_id', 'agent_name',
            'decision_type', 'action', 'reasoning', 'alternatives',
            'context', 'task_summary', 'confidence',
            'was_successful', 'outcome_notes', 'created_at',
        ]


# ── ToolCallRecord ──

class ToolCallRecordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolCallRecord
        fields = [
            'id', 'agent_name', 'tool_name', 'success',
            'latency_ms', 'created_at',
        ]


class ToolCallRecordDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolCallRecord
        fields = [
            'id', 'trace_id', 'conversation_id', 'agent_name',
            'tool_name', 'parameters', 'result_summary', 'result_hash',
            'result_size_bytes', 'success', 'error_message', 'error_type',
            'latency_ms', 'task_summary', 'created_at',
        ]


# ── ToolCallAggregate ──

class ToolCallAggregateSerializer(serializers.ModelSerializer):
    success_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = ToolCallAggregate
        fields = [
            'id', 'agent_name', 'tool_name', 'date',
            'total_calls', 'success_calls', 'failed_calls',
            'avg_latency_ms', 'min_latency_ms', 'max_latency_ms',
            'p95_latency_ms', 'top_errors', 'success_rate', 'updated_at',
        ]


# ── SignalCluster ──

class SignalClusterListSerializer(serializers.ModelSerializer):
    # S2971: Signal Intelligence UI Cluster Explorer table needs these fields
    # inline so it doesn't N+1 into the detail endpoint per row.
    signal_count = serializers.IntegerField(source='total_signals', read_only=True)
    total_signals = serializers.IntegerField(read_only=True)

    class Meta:
        model = SignalCluster
        fields = [
            'id', 'name', 'pattern_type', 'strength', 'novelty',
            'confidence', 'urgency', 'status', 'detected_at',
            'signal_count', 'total_signals',
            'source_breakdown', 'keywords',
        ]


class SignalClusterDetailSerializer(serializers.ModelSerializer):
    total_signals = serializers.IntegerField(read_only=True)

    class Meta:
        model = SignalCluster
        fields = [
            'id', 'name', 'pattern_type', 'spider_data_ids',
            'trigger_event_ids', 'source_breakdown', 'strength',
            'novelty', 'confidence', 'urgency', 'keywords',
            'sample_signals', 'signal_window_start', 'signal_window_end',
            'status', 'detected_at', 'confirmed_at', 'decay_rate',
            'expires_at', 'total_signals',
        ]

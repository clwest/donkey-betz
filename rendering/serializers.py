"""
Rendering Serializers - Session 105

DRF serializers for RenderJob API.
"""

from rest_framework import serializers
from .models import RenderJob


class RenderJobSerializer(serializers.ModelSerializer):
    """
    Serializer for RenderJob model.

    Read-only fields are automatically populated.
    Write-only project_id/session_id are used for creation.
    """

    project_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    session_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    timeline_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    template = serializers.CharField(write_only=True, default='default_mp4')

    progress_percentage = serializers.FloatField(read_only=True, source='progress_percentage')

    class Meta:
        model = RenderJob
        fields = [
            'id',
            'title',  # Session 106
            'status',
            'progress',
            'progress_percentage',
            'project_id',
            'session_id',
            'timeline_name',
            'template',
            'result_url',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
        ]
        read_only_fields = [
            'id',
            'title',  # Auto-generated
            'status',
            'progress',
            'progress_percentage',
            'result_url',
            'error_message',
            'created_at',
            'updated_at',
            'completed_at',
        ]


class RenderJobDetailSerializer(RenderJobSerializer):
    """
    Extended serializer with additional details.

    Includes source_payload and result_payload for debugging.
    """

    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    session_title = serializers.CharField(source='session.title', read_only=True, allow_null=True)

    class Meta(RenderJobSerializer.Meta):
        fields = RenderJobSerializer.Meta.fields + [
            'project_name',
            'session_title',
            'source_payload',
            'result_payload',
            'node_job_id',
        ]
        read_only_fields = RenderJobSerializer.Meta.read_only_fields + [
            'project_name',
            'session_title',
            'source_payload',
            'result_payload',
            'node_job_id',
        ]

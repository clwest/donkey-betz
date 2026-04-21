from rest_framework import serializers

from .models import ProjectWorkspace


class ProjectWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectWorkspace
        fields = ["id", "name", "repo_url", "repo_dir", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

"""
Workspace Hosted Previews — API Views

Authenticated endpoints for workspace project management + preview orchestration.
Public endpoints for magic link review portal + feedback submission.
"""

import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models_preview_system import (
    DeployJob,
    FeedbackItem,
    MagicLink,
    PreviewDeployment,
    PreviewEnvironment,
    PreviewService,
    ProjectEnvVar,
    ProjectRepo,
    WorkspaceProject,
)

logger = logging.getLogger(__name__)


# ── Serializers ───────────────────────────────────────────────────────────


class ProjectRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectRepo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ProjectEnvVarSerializer(serializers.ModelSerializer):
    display_value = serializers.SerializerMethodField()

    class Meta:
        model = ProjectEnvVar
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {"value": {"write_only": True}}

    def get_display_value(self, obj):
        return "****" if obj.is_secret else obj.value


class PreviewServiceSerializer(serializers.ModelSerializer):
    repo_name = serializers.CharField(source="repo.name", read_only=True)
    repo_type = serializers.CharField(source="repo.type", read_only=True)

    class Meta:
        model = PreviewService
        fields = "__all__"
        read_only_fields = ("id",)


class DeployJobSerializer(serializers.ModelSerializer):
    repo_name = serializers.CharField(source="repo.name", read_only=True)
    repo_type = serializers.CharField(source="repo.type", read_only=True)

    class Meta:
        model = DeployJob
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class PreviewDeploymentSerializer(serializers.ModelSerializer):
    jobs = DeployJobSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = PreviewDeployment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_duration(self, obj):
        return obj.duration_seconds


class MagicLinkSerializer(serializers.ModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = MagicLink
        fields = "__all__"
        read_only_fields = ("id", "token_hash", "uses", "created_at")

    def get_url(self, obj):
        # The raw token is only available at creation time
        return None


class FeedbackItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackItem
        fields = "__all__"
        read_only_fields = (
            "id", "created_at", "updated_at", "triaged_by", "triaged_at",
        )


class PreviewEnvironmentSerializer(serializers.ModelSerializer):
    services = PreviewServiceSerializer(many=True, read_only=True)
    magic_links = MagicLinkSerializer(many=True, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    web_url = serializers.CharField(read_only=True)
    api_url = serializers.CharField(read_only=True)
    feedback_count = serializers.SerializerMethodField()

    class Meta:
        model = PreviewEnvironment
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_feedback_count(self, obj):
        return obj.feedback_items.count()


class WorkspaceProjectSerializer(serializers.ModelSerializer):
    repos = ProjectRepoSerializer(many=True, read_only=True)
    preview_env_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceProject
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_preview_env_count(self, obj):
        return obj.preview_envs.count()


# ── Authenticated ViewSets ────────────────────────────────────────────────


class WorkspaceProjectViewSet(viewsets.ModelViewSet):
    """CRUD for workspace projects (project bundles)."""

    serializer_class = WorkspaceProjectSerializer
    queryset = WorkspaceProject.objects.prefetch_related("repos").all()

    def get_queryset(self):
        qs = super().get_queryset()
        workspace_id = self.request.query_params.get("workspace")
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs


class ProjectRepoViewSet(viewsets.ModelViewSet):
    """CRUD for repos within a project."""

    serializer_class = ProjectRepoSerializer
    queryset = ProjectRepo.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class ProjectEnvVarViewSet(viewsets.ModelViewSet):
    """CRUD for project environment variables."""

    serializer_class = ProjectEnvVarSerializer
    queryset = ProjectEnvVar.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs


class PreviewEnvironmentViewSet(viewsets.ModelViewSet):
    """Manage preview environments."""

    serializer_class = PreviewEnvironmentSerializer
    queryset = PreviewEnvironment.objects.prefetch_related(
        "services", "magic_links", "feedback_items"
    ).all()

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")
        ttl = project.default_preview_ttl_minutes if project else 4320
        serializer.save(
            created_by=self.request.user,
            ttl_expires_at=timezone.now() + timedelta(minutes=ttl),
        )

    @action(detail=True, methods=["post"])
    def deploy(self, request, pk=None):
        """Trigger a deployment for this preview environment."""
        preview_env = self.get_object()
        if preview_env.is_expired:
            return Response(
                {"error": "Preview environment has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deployment = PreviewDeployment.objects.create(
            preview_env=preview_env,
            trigger=PreviewDeployment.Trigger.MANUAL,
            created_by=request.user,
        )

        # Create deploy jobs for each repo
        for repo in preview_env.project.repos.all():
            DeployJob.objects.create(
                deployment=deployment,
                repo=repo,
            )

        return Response(
            PreviewDeploymentSerializer(deployment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def create_magic_link(self, request, pk=None):
        """Generate a magic link for customer review."""
        preview_env = self.get_object()
        if preview_env.is_expired:
            return Response(
                {"error": "Preview environment has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        label = request.data.get("label", "Review link")
        scope = request.data.get("scope", MagicLink.Scope.REVIEW)
        ttl_hours = int(request.data.get("ttl_hours", 72))
        max_uses = request.data.get("max_uses")

        raw_token, token_hash = MagicLink.generate_token()
        link = MagicLink.objects.create(
            preview_env=preview_env,
            token_hash=token_hash,
            label=label,
            scope=scope,
            expires_at=timezone.now() + timedelta(hours=ttl_hours),
            max_uses=max_uses,
            created_by=request.user,
        )

        data = MagicLinkSerializer(link).data
        data["raw_token"] = raw_token
        data["review_url"] = f"/r/{raw_token}"

        logger.info(
            "Magic link created: %s for preview %s by user %s",
            link.label, preview_env.name, request.user,
        )

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def feedback(self, request, pk=None):
        """List feedback for this preview environment."""
        preview_env = self.get_object()
        feedback = preview_env.feedback_items.all()

        severity = request.query_params.get("severity")
        if severity:
            feedback = feedback.filter(severity=severity)

        fb_status = request.query_params.get("status")
        if fb_status:
            feedback = feedback.filter(status=fb_status)

        return Response(FeedbackItemSerializer(feedback, many=True).data)


class FeedbackItemViewSet(viewsets.ModelViewSet):
    """Manage feedback items (internal)."""

    serializer_class = FeedbackItemSerializer
    queryset = FeedbackItem.objects.select_related(
        "preview_env", "magic_link", "linked_repo"
    ).all()

    def get_queryset(self):
        qs = super().get_queryset()
        preview_env = self.request.query_params.get("preview_env")
        if preview_env:
            qs = qs.filter(preview_env_id=preview_env)
        return qs

    @action(detail=True, methods=["post"])
    def triage(self, request, pk=None):
        """Mark feedback as triaged."""
        item = self.get_object()
        item.status = FeedbackItem.Status.TRIAGED
        item.triaged_by = request.user
        item.triaged_at = timezone.now()
        item.save(update_fields=["status", "triaged_by", "triaged_at", "updated_at"])
        return Response(FeedbackItemSerializer(item).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Mark feedback as resolved."""
        item = self.get_object()
        item.status = FeedbackItem.Status.RESOLVED
        item.resolution_note = request.data.get("resolution_note", "")
        item.save(update_fields=["status", "resolution_note", "updated_at"])
        return Response(FeedbackItemSerializer(item).data)


# ── Public Review Endpoints (magic link) ──────────────────────────────────


class ReviewThrottle(ScopedRateThrottle):
    scope = "review"


class FeedbackThrottle(ScopedRateThrottle):
    scope = "review_feedback"


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def review_context(request, token):
    """Public: validate magic link token and return preview context."""
    link = MagicLink.lookup(token)
    if not link:
        return Response(
            {"error": "Invalid or expired review link"},
            status=status.HTTP_404_NOT_FOUND,
        )

    link.record_use()

    preview_env = link.preview_env
    project = preview_env.project

    services = {}
    for svc in preview_env.services.all():
        services[svc.service_type] = {
            "url": svc.public_url,
            "health": svc.health_status,
        }

    return Response({
        "project_name": project.name,
        "preview_name": preview_env.name,
        "scope": link.scope,
        "expires_at": link.expires_at.isoformat(),
        "services": services,
        "can_submit_feedback": link.scope == MagicLink.Scope.REVIEW,
    })


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def review_feedback(request, token):
    """Public: submit feedback via magic link."""
    link = MagicLink.lookup(token)
    if not link:
        return Response(
            {"error": "Invalid or expired review link"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if link.scope != MagicLink.Scope.REVIEW:
        return Response(
            {"error": "This link is view-only"},
            status=status.HTTP_403_FORBIDDEN,
        )

    message = request.data.get("message", "").strip()
    if not message:
        return Response(
            {"error": "Message is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    feedback = FeedbackItem.objects.create(
        preview_env=link.preview_env,
        magic_link=link,
        source=FeedbackItem.Source.MAGIC_LINK,
        page_url=request.data.get("page_url", ""),
        page_path=request.data.get("page_path", ""),
        page_title=request.data.get("page_title", ""),
        message=message,
        severity=request.data.get("severity", FeedbackItem.Severity.IMPORTANT),
        category=request.data.get("category", FeedbackItem.Category.OTHER),
        client_context=request.data.get("client_context", {}),
        reporter_name=request.data.get("reporter_name", ""),
        reporter_email=request.data.get("reporter_email", ""),
        reporter_phone=request.data.get("reporter_phone", ""),
    )

    logger.info(
        "Feedback submitted via magic link %s: [%s] %s",
        link.label, feedback.severity, feedback.message[:80],
    )

    return Response(
        {"id": str(feedback.id), "status": "submitted"},
        status=status.HTTP_201_CREATED,
    )

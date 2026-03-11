import json
import os
from datetime import datetime
from pathlib import Path

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ProjectWorkspace
from .serializers import ProjectWorkspaceSerializer


def _get_clone_status(repo_dir: Path) -> dict:
    """
    Inspect sentinel files under repo_dir and return status fields.
    Read-only: no writes are performed.

    Sentinel files:
      .clone.in_progress  – JSON with optional ``started_at`` key (ISO8601)
      .clone.ok           – JSON with optional ``head_sha`` / ``sha`` key
      .clone.error        – plain text or JSON; first line used as error_message

    Status rules:
      ready   – .git exists AND .clone.in_progress absent
      cloning – .clone.in_progress exists
      error   – .clone.error exists (and not cloning)
      missing – none of the above
    """
    git_dir = repo_dir / ".git"
    sentinel_in_progress = repo_dir / ".clone.in_progress"
    sentinel_ok = repo_dir / ".clone.ok"
    sentinel_error = repo_dir / ".clone.error"

    clone_started_at = None
    head_sha = None
    error_message = None
    retry_after_seconds = 0

    # Always try to read head_sha from .clone.ok
    if sentinel_ok.exists():
        try:
            data = json.loads(sentinel_ok.read_text())
            head_sha = data.get("head_sha") or data.get("sha") or None
        except Exception:
            pass

    if git_dir.exists() and not sentinel_in_progress.exists():
        status = "ready"

    elif sentinel_in_progress.exists():
        status = "cloning"
        retry_after_seconds = 5
        try:
            data = json.loads(sentinel_in_progress.read_text())
            raw_ts = data.get("started_at") or data.get("clone_started_at")
            if raw_ts:
                # Validate parseable ISO8601 before returning
                datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                clone_started_at = raw_ts
        except Exception:
            pass

    elif sentinel_error.exists():
        status = "error"
        try:
            text = sentinel_error.read_text()
            try:
                data = json.loads(text)
                msg = data.get("error") or data.get("message") or text
            except (json.JSONDecodeError, ValueError):
                msg = text
            error_message = str(msg).splitlines()[0][:200] if str(msg).strip() else None
        except Exception:
            error_message = "unknown error"

    else:
        status = "missing"

    return {
        "status": status,
        "clone_started_at": clone_started_at,
        "head_sha": head_sha,
        "error_message": error_message,
        "retry_after_seconds": retry_after_seconds,
    }


def _resolve_repo_dir(workspace) -> Path:
    """
    Determine the local repo directory for a workspace instance.
    Tries common attributes/methods in priority order, then falls back
    to ``WORKSPACE_REPOS_ROOT`` env var + workspace id.
    """
    if hasattr(workspace, "get_repo_dir") and callable(workspace.get_repo_dir):
        return Path(workspace.get_repo_dir())
    if hasattr(workspace, "repo_dir") and workspace.repo_dir:
        return Path(workspace.repo_dir)
    if hasattr(workspace, "path") and workspace.path:
        return Path(workspace.path)
    base = os.environ.get("WORKSPACE_REPOS_ROOT", "/tmp/workspaces")
    return Path(base) / str(workspace.id)


class ProjectWorkspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProjectWorkspace CRUD.

    Extra action
    ------------
    GET /api/workspaces/{id}/clone_status/
        Returns clone status derived from sentinel files under the workspace
        repo directory.  Never triggers a scan or clone.  Always HTTP 200
        unless the workspace is not found (404).

        Response fields:
          status               – 'ready' | 'cloning' | 'error' | 'missing'
          workspace_id         – string UUID
          clone_started_at     – ISO8601 string or null
          head_sha             – string or null
          error_message        – string or null (first line, max 200 chars)
          retry_after_seconds  – 5 when cloning, else 0
    """

    serializer_class = ProjectWorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProjectWorkspace.objects.filter(user=self.request.user)

    @action(detail=True, methods=["get"], url_path="clone_status")
    def clone_status(self, request, pk=None):
        """
        Read-only clone status for a specific workspace.
        HTTP 200 for all status values; 404 if workspace not found.
        """
        workspace = self.get_object()  # raises Http404 if not found / no permission
        repo_dir = _resolve_repo_dir(workspace)
        fields = _get_clone_status(repo_dir)
        return Response(
            {"workspace_id": str(workspace.id), **fields},
            status=200,
        )

import uuid

from django.conf import settings
from django.db import models


class ProjectWorkspace(models.Model):
    """A workspace that wraps a cloned git repository."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspaces",
    )
    name = models.CharField(max_length=255)
    repo_url = models.URLField(blank=True, default="")
    # Local filesystem path to the cloned repo
    repo_dir = models.CharField(max_length=1024, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.id})"

import json
import tempfile
import uuid
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import ProjectWorkspace

User = get_user_model()


class CloneStatusActionTests(TestCase):
    """Tests for GET /api/workspaces/{id}/clone_status/"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.force_authenticate(user=self.user)

    # ------------------------------------------------------------------ helpers

    def _url(self, workspace_id) -> str:
        return f"/api/workspaces/{workspace_id}/clone_status/"

    def _make_workspace(self, repo_dir: str) -> ProjectWorkspace:
        return ProjectWorkspace.objects.create(
            user=self.user,
            name="test-ws",
            repo_url="https://example.com/repo.git",
            repo_dir=repo_dir,
        )

    # ------------------------------------------------------------------ tests

    def test_404_for_unknown_workspace(self):
        resp = self.client.get(self._url(uuid.uuid4()))
        self.assertEqual(resp.status_code, 404)

    def test_status_missing_when_no_git_and_no_sentinels(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data["status"], "missing")
            self.assertEqual(data["workspace_id"], str(ws.id))
            self.assertIsNone(data["clone_started_at"])
            self.assertIsNone(data["head_sha"])
            self.assertIsNone(data["error_message"])
            self.assertEqual(data["retry_after_seconds"], 0)

    def test_status_ready_when_git_dir_exists(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".git").mkdir()
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()["status"], "ready")
            self.assertEqual(resp.json()["retry_after_seconds"], 0)

    def test_status_cloning_overrides_git_dir(self):
        """If .clone.in_progress exists, status is 'cloning' even if .git present."""
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".git").mkdir()
            Path(d, ".clone.in_progress").write_text(
                json.dumps({"started_at": "2024-06-01T12:00:00Z"})
            )
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            data = resp.json()
            self.assertEqual(data["status"], "cloning")
            self.assertEqual(data["retry_after_seconds"], 5)
            self.assertEqual(data["clone_started_at"], "2024-06-01T12:00:00Z")

    def test_status_cloning_without_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".clone.in_progress").write_text(json.dumps({}))
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            data = resp.json()
            self.assertEqual(data["status"], "cloning")
            self.assertIsNone(data["clone_started_at"])

    def test_status_error_plain_text(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".clone.error").write_text("fatal: repository not found\nmore detail")
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            data = resp.json()
            self.assertEqual(data["status"], "error")
            self.assertEqual(data["error_message"], "fatal: repository not found")

    def test_status_error_json(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".clone.error").write_text(
                json.dumps({"error": "authentication failed"})
            )
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            data = resp.json()
            self.assertEqual(data["status"], "error")
            self.assertEqual(data["error_message"], "authentication failed")

    def test_head_sha_from_clone_ok(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, ".git").mkdir()
            Path(d, ".clone.ok").write_text(json.dumps({"head_sha": "deadbeef"}))
            ws = self._make_workspace(d)
            resp = self.client.get(self._url(ws.id))
            data = resp.json()
            self.assertEqual(data["status"], "ready")
            self.assertEqual(data["head_sha"], "deadbeef")

    def test_no_write_side_effects(self):
        """clone_status must not create or modify any files in the repo dir."""
        with tempfile.TemporaryDirectory() as d:
            before = set(os.listdir(d))
            ws = self._make_workspace(d)
            self.client.get(self._url(ws.id))
            after = set(os.listdir(d))
            self.assertEqual(before, after)

    def test_unauthenticated_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self._make_workspace(d)
            anon = APIClient()
            resp = anon.get(self._url(ws.id))
            self.assertIn(resp.status_code, [401, 403])

    def test_other_user_cannot_access(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self._make_workspace(d)
            other = User.objects.create_user(username="other", password="pass")
            other_client = APIClient()
            other_client.force_authenticate(user=other)
            resp = other_client.get(self._url(ws.id))
            self.assertEqual(resp.status_code, 404)


# need os for test_no_write_side_effects
import os  # noqa: E402

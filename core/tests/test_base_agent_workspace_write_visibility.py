from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from core.agents.base_agent import AgentResult, BaseAgent


class _WorkspaceWriteAgent(BaseAgent):
    name = "WorkspaceWriteAgent"
    system_prompt = "test"

    def execute(self, task, context, scifi_context, spider_context):
        return AgentResult(
            success=True,
            message="workspace output",
            data={
                "results": [
                    {
                        "data": {
                            "files": [
                                {"filename": "ok.txt", "content": "hello", "language": "text"},
                                {"filename": "bad.txt", "content": "broken", "language": "text"},
                            ]
                        }
                    }
                ]
            },
            agent_name=self.name,
        )


class TestWorkspaceWriteVisibility(SimpleTestCase):
    def test_partial_file_write_sets_top_level_metadata(self):
        agent = _WorkspaceWriteAgent()

        class FakeWorkspace:
            name = "main"
            root_path = "/tmp/main"
            allow_file_write = True

        class FakeOperation:
            def __init__(self, success, op_id, error_message=""):
                self.success = success
                self.id = op_id
                self.error_message = error_message

        class FakeManager:
            def __init__(self):
                self.calls = []

            def get_active_workspace(self):
                return FakeWorkspace()

            def write_file(self, workspace, file_path, content, agent_name):
                self.calls.append((file_path, content, agent_name))
                if file_path.endswith("bad.txt"):
                    return FakeOperation(False, "op-bad", "permission denied")
                return FakeOperation(True, "op-ok")

        fake_manager = FakeManager()

        with patch.object(agent, "_get_workspace_manager", return_value=fake_manager), \
             patch.object(agent, "_capture_single_file_artifact", return_value=None):
            result = agent.execute_with_workspace(
                task="write files",
                context={},
                write_to_workspace=True,
            )

        self.assertTrue(result.success)
        self.assertIn("workspace_write", result.data)
        self.assertTrue(result.data["partial_failure"])
        self.assertEqual(result.data["file_write_failures"], 1)
        self.assertEqual(result.data["workspace_write"]["file_write_failures"], 1)
        self.assertEqual(result.data["workspace_write"]["total_failed"], 1)
        self.assertFalse(result.data["workspace_write"]["success"])
        self.assertEqual(result.data["workspace_write"]["files_failed"][0]["path"], "bad.txt")
        self.assertEqual(result.data["workspace_write"]["files_failed"][0]["error"], "permission denied")


class TestAllFilesFailedPartialFailurePath(SimpleTestCase):
    """Session 1231 P2 — when ALL files fail, written=False so the
    `elif partial_failure` branch in execute_with_workspace fires.
    Pre-fix that branch raised KeyError('files_generated') because
    _write_files_to_workspace's main-path return shape omits that key.
    Post-fix it composes the message from total_written + total_failed.

    Closes Session 1230 F1 — COOAgent scheduled daily diagnostic was
    silently failing with error_message="'files_generated'" every
    13:30 UTC fire (f2ecd6f9-…, 86796586-…)."""

    def test_all_files_failed_does_not_raise_key_error(self):
        agent = _WorkspaceWriteAgent()

        class FakeWorkspace:
            name = "main"
            root_path = "/tmp/main"
            allow_file_write = True

        class FakeOperation:
            def __init__(self):
                self.success = False
                self.id = "op-fail"
                self.error_message = "permission denied"

        class FakeManager:
            def get_active_workspace(self):
                return FakeWorkspace()

            def write_file(self, workspace, file_path, content, agent_name):
                # Fail every write — triggers written=False + partial_failure=True
                return FakeOperation()

        with patch.object(agent, "_get_workspace_manager", return_value=FakeManager()), \
             patch.object(agent, "_capture_single_file_artifact", return_value=None):
            # Pre-fix this raised KeyError('files_generated') inside the
            # f-string at base_agent.py:5482. Post-fix it returns cleanly.
            result = agent.execute_with_workspace(
                task="write files",
                context={},
                write_to_workspace=True,
            )

        self.assertTrue(result.success)
        self.assertTrue(result.data["partial_failure"])
        self.assertFalse(result.data["workspace_write"]["written"])
        # Both files failed → total_attempted = 0 + 2 = 2.
        self.assertIn("Workspace write partially failed: 2 of 2 files failed",
                      result.message)

    def test_partial_failure_path_uses_safe_getters(self):
        """Source-level guard: lock the elif branch wiring against
        future revert to bare write_result['files_generated'] access."""
        import re
        from pathlib import Path
        src = Path('core/agents/base_agent.py').read_text()
        # Locate the partial_failure elif and check the bare access is gone.
        bad = re.search(
            r"write_result\['files_generated'\]",
            src,
        )
        self.assertIsNone(
            bad,
            msg="bare write_result['files_generated'] access reintroduced; "
                "use .get() with safe default or compute from total_written + "
                "total_failed (Session 1231 P2 fix for COOAgent scheduled "
                "diagnostic KeyError).",
        )

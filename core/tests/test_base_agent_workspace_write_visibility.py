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

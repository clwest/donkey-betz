from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from core.agents.base_agent import BaseAgent


class _DocWriteAgent(BaseAgent):
    name = "DocWriteAgent"
    system_prompt = "test"

    def execute(self, task, context, scifi_context, spider_context):
        raise NotImplementedError


class TestBaseAgentDocWriteFailureVisibility(SimpleTestCase):
    def test_write_doc_access_denied_returns_structured_failure(self):
        agent = _DocWriteAgent.__new__(_DocWriteAgent)
        agent.name = "DocAgent"

        with patch("django.conf.settings.BASE_DIR", Path("/tmp/project")):
            result = agent._write_doc("outside.txt", "content", create_backup=False)

        self.assertFalse(result["success"])
        self.assertEqual(result["error_type"], "AccessDenied")
        self.assertEqual(result["reason"], "docs_directory_only")
        self.assertIn("Access denied", result["error"])

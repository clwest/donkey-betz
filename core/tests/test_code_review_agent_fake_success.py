from contextlib import contextmanager
from unittest.mock import Mock

from django.test import SimpleTestCase

from core.agents.code_review_agent import CodeReviewAgent


class CodeReviewAgentFakeSuccessTests(SimpleTestCase):
    def _make_agent(self, tool_calls, tool_results):
        agent = CodeReviewAgent.__new__(CodeReviewAgent)
        agent.name = "CodeReviewAgent"
        agent.agent_name = "CodeReviewAgent"
        agent.user = None
        agent._tt_decision_count = 0

        agent._build_intelligent_prompt = Mock(return_value="prompt")
        agent._call_openai = Mock(return_value={"tool_calls": tool_calls})
        agent._execute_tool_call = Mock(side_effect=lambda tool_name, arguments: tool_results[tool_name])
        agent.record_decision = Mock()
        agent.mark_decision_outcome = Mock()
        agent._record_learning_outcome = Mock()
        agent._save_to_deliverable = Mock()
        agent._render_agent_output_markdown = Mock(return_value="rendered")

        @contextmanager
        def _noop_session(*args, **kwargs):
            yield None

        agent.time_travel_session = _noop_session
        return agent

    def test_failed_review_tool_after_read_file_returns_failure(self):
        agent = self._make_agent(
            tool_calls=[
                {"name": "read_file", "arguments": {"file_path": "core/example.py"}},
                {"name": "comprehensive_review", "arguments": {"code": "print('x')", "language": "python"}},
            ],
            tool_results={
                "read_file": {
                    "success": True,
                    "file_path": "core/example.py",
                    "language": "python",
                    "content": "print('x')",
                },
                "comprehensive_review": {
                    "success": False,
                    "error": "review failed",
                    "review_type": "comprehensive",
                },
            },
        )

        result = agent.execute(
            task="Review core/example.py",
            context={},
            scifi_context={},
            spider_context={},
        )

        self.assertFalse(result.success)
        self.assertIn("review", result.message.lower())
        self.assertTrue(result.data["file_read_success"])
        self.assertTrue(result.data["review_tool_attempted"])
        self.assertFalse(result.data["review_tool_success"])
        self.assertEqual(result.data["review_tool_failures"], [{"tool": "comprehensive_review", "error": "review failed"}])
        self.assertTrue(result.data["partial_failure"])
        self.assertEqual(result.error, result.message)

    def test_no_tool_calls_returns_failure_without_fake_success(self):
        agent = CodeReviewAgent.__new__(CodeReviewAgent)
        agent.name = "CodeReviewAgent"
        agent.agent_name = "CodeReviewAgent"
        agent.user = None
        agent._tt_decision_count = 0

        agent._build_intelligent_prompt = Mock(return_value="prompt")
        agent._call_openai = Mock(return_value={"content": "Looks good"})
        agent.record_decision = Mock()
        agent.mark_decision_outcome = Mock()
        agent._record_learning_outcome = Mock()
        agent._save_to_deliverable = Mock()

        @contextmanager
        def _noop_session(*args, **kwargs):
            yield None

        agent.time_travel_session = _noop_session

        result = agent.execute(
            task="Review core/example.py",
            context={},
            scifi_context={},
            spider_context={},
        )

        self.assertFalse(result.success)
        self.assertEqual(result.message, "No code inspection or review completed")
        self.assertFalse(result.data["file_read_success"])
        self.assertFalse(result.data["review_tool_attempted"])
        self.assertFalse(result.data["review_tool_success"])
        self.assertEqual(result.data["review_tool_failures"], [])
        self.assertFalse(result.data["partial_failure"])

    def test_successful_review_tool_still_returns_success(self):
        agent = self._make_agent(
            tool_calls=[
                {"name": "read_file", "arguments": {"file_path": "core/example.py"}},
                {"name": "comprehensive_review", "arguments": {"code": "print('x')", "language": "python"}},
            ],
            tool_results={
                "read_file": {
                    "success": True,
                    "file_path": "core/example.py",
                    "language": "python",
                    "content": "print('x')",
                },
                "comprehensive_review": {
                    "success": True,
                    "language": "python",
                    "review_type": "comprehensive",
                    "lines_reviewed": 1,
                    "review": "Looks good",
                },
            },
        )

        result = agent.execute(
            task="Review core/example.py",
            context={},
            scifi_context={},
            spider_context={},
        )

        self.assertTrue(result.success)
        self.assertIn("completed", result.message.lower())
        self.assertTrue(result.data["file_read_success"])
        self.assertTrue(result.data["review_tool_attempted"])
        self.assertTrue(result.data["review_tool_success"])
        self.assertEqual(result.data["review_tool_failures"], [])
        self.assertFalse(result.data["partial_failure"])

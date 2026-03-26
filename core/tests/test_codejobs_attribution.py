"""
Tests: CodeWorker / Claude Code message attribution.

Verifies that tool/system events injected into conversations are
persisted with role='tool' (never 'user') and the correct source field.
"""

from unittest.mock import MagicMock

import pytest

from core.codejobs.event_emitter import (
    ROLE_TOOL,
    SOURCE_CODE_WORKER,
    SOURCE_CLAUDE_CODE,
    build_code_worker_message,
    build_claude_code_message,
    persist_tool_message,
)
from core.codejobs.pipeline import post_code_worker_result, post_claude_code_status


# ── Unit tests: message-dict builders ─────────────────────────────────────

class TestBuildCodeWorkerMessage:
    def test_role_is_tool(self):
        msg = build_code_worker_message("done")
        assert msg["role"] == ROLE_TOOL, "CodeWorker messages must NOT have role='user'"

    def test_source_is_code_worker(self):
        msg = build_code_worker_message("done")
        assert msg["source"] == SOURCE_CODE_WORKER

    def test_content_preserved(self):
        msg = build_code_worker_message("hello world")
        assert msg["content"] == "hello world"

    def test_metadata_included(self):
        msg = build_code_worker_message("x", metadata={"run_id": "abc"})
        assert msg["metadata"]["run_id"] == "abc"

    def test_no_metadata_when_none(self):
        msg = build_code_worker_message("x")
        assert "metadata" not in msg


class TestBuildClaudeCodeMessage:
    def test_role_is_tool(self):
        msg = build_claude_code_message("status update")
        assert msg["role"] == ROLE_TOOL, "Claude Code messages must NOT have role='user'"

    def test_source_is_claude_code(self):
        msg = build_claude_code_message("status update")
        assert msg["source"] == SOURCE_CLAUDE_CODE

    def test_content_preserved(self):
        msg = build_claude_code_message("running tests")
        assert msg["content"] == "running tests"


# ── Unit tests: persist_tool_message ──────────────────────────────────────

class TestPersistToolMessage:
    def test_persists_via_add_message_api(self):
        conv = MagicMock()
        persist_tool_message(conv, "result", SOURCE_CODE_WORKER)
        conv.add_message.assert_called_once()
        kwargs = conv.add_message.call_args.kwargs
        assert kwargs.get("role") == ROLE_TOOL
        assert kwargs.get("source") == SOURCE_CODE_WORKER

    def test_persists_via_json_field(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        persist_tool_message(conv, "result", SOURCE_CODE_WORKER)
        assert len(conv.messages) == 1
        assert conv.messages[0]["role"] == ROLE_TOOL
        assert conv.messages[0]["source"] == SOURCE_CODE_WORKER
        conv.save.assert_called_once_with(update_fields=["messages"])

    def test_never_writes_user_role(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        persist_tool_message(conv, "x", SOURCE_CODE_WORKER)
        for msg in conv.messages:
            assert msg.get("role") != "user", (
                "Tool/system messages must never be stored with role='user'"
            )


# ── Integration-style tests: pipeline helpers ─────────────────────────────

class TestPostCodeWorkerResult:
    def _make_run(self, status="succeeded", pr_url="https://gh.test/pr/1",
                  commit_sha="abc123", failure_reason=""):
        run = MagicMock()
        run.id = "run-uuid-1"
        run.status = status
        run.pr_url = pr_url
        run.commit_sha = commit_sha
        run.failure_reason_code = failure_reason
        return run

    def test_success_stores_role_tool(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_code_worker_result(conv, self._make_run())
        assert conv.messages[0]["role"] == ROLE_TOOL

    def test_success_stores_source_code_worker(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_code_worker_result(conv, self._make_run())
        assert conv.messages[0]["source"] == SOURCE_CODE_WORKER

    def test_failure_stores_role_tool(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_code_worker_result(conv, self._make_run(status="failed", failure_reason="TESTS_FAILED"))
        assert conv.messages[0]["role"] == ROLE_TOOL

    def test_failure_stores_source_code_worker(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_code_worker_result(conv, self._make_run(status="failed"))
        assert conv.messages[0]["source"] == SOURCE_CODE_WORKER

    def test_metadata_contains_run_id(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_code_worker_result(conv, self._make_run())
        metadata = conv.messages[0].get("metadata", {})
        assert metadata.get("run_id") == "run-uuid-1"


class TestPostClaudeCodeStatus:
    def test_stores_role_tool(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_claude_code_status(conv, "Running tests...")
        assert conv.messages[0]["role"] == ROLE_TOOL

    def test_stores_source_claude_code(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_claude_code_status(conv, "Running tests...")
        assert conv.messages[0]["source"] == SOURCE_CLAUDE_CODE

    def test_content_passed_through(self):
        conv = MagicMock(spec=["messages", "save"])
        conv.messages = []
        post_claude_code_status(conv, "All tests passed")
        assert "All tests passed" in conv.messages[0]["content"]

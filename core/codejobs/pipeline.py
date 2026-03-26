"""
CodeWorker job pipeline helpers.

When a CodeWorker job completes (succeeded or failed) and we need to
inject the result into an attached conversation we must use
role='tool' / source='code-worker'.  This module provides the
single entry-point for that operation so the attribution contract
cannot be violated by callers.
"""

from __future__ import annotations

import logging
from typing import Any

from .event_emitter import (
    SOURCE_CODE_WORKER,
    SOURCE_CLAUDE_CODE,
    persist_tool_message,
)

logger = logging.getLogger(__name__)


def post_code_worker_result(
    conversation: Any,
    run: Any,
    extra_metadata: dict | None = None,
) -> None:
    """
    Inject a CodeWorker job result into *conversation*.

    The stored message will always have:
      role   = 'tool'
      source = 'code-worker'

    Args:
        conversation: AgentConversation (or compatible) instance.
        run: ExecutionRun instance (provides status, pr_url, etc.).
        extra_metadata: Additional data to embed in the message metadata.
    """
    status = getattr(run, "status", "unknown")
    pr_url = getattr(run, "pr_url", "") or ""
    commit_sha = getattr(run, "commit_sha", "") or ""
    failure_reason = getattr(run, "failure_reason_code", "") or ""

    if status == "succeeded":
        content = "\u2705 CodeWorker job completed successfully."
        if pr_url:
            content += f"\nPR: {pr_url}"
        if commit_sha:
            content += f"\nCommit: {commit_sha}"
    else:
        content = f"\u274c CodeWorker job ended with status: {status}."
        if failure_reason:
            content += f" Reason: {failure_reason}"

    metadata: dict[str, Any] = {
        "run_id": str(getattr(run, "id", "")),
        "status": status,
    }
    if extra_metadata:
        metadata.update(extra_metadata)

    persist_tool_message(
        conversation=conversation,
        content=content,
        source=SOURCE_CODE_WORKER,
        metadata=metadata,
    )


def post_claude_code_status(
    conversation: Any,
    status_text: str,
    metadata: dict | None = None,
) -> None:
    """
    Inject a Claude Code status/result message into *conversation*.

    The stored message will always have:
      role   = 'tool'
      source = 'claude-code'
    """
    persist_tool_message(
        conversation=conversation,
        content=status_text,
        source=SOURCE_CLAUDE_CODE,
        metadata=metadata,
    )

"""
CodeWorker / Claude Code event emitter helpers.

Tool/system events injected into conversations must NOT be persisted or
streamed with role='user'. This module centralises that contract:

  - CodeWorker completion  -> role='tool', source='code-worker'
  - Claude Code status     -> role='tool', source='claude-code'

Any caller that creates conversation messages for these event types
should go through the helpers below so the source-of-truth lives in
one place.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

ROLE_TOOL = "tool"
SOURCE_CODE_WORKER = "code-worker"
SOURCE_CLAUDE_CODE = "claude-code"


# ── Message-dict builders ──────────────────────────────────────────────────

def build_code_worker_message(content: str, metadata: dict | None = None) -> dict:
    """
    Return a message dict suitable for persisting a CodeWorker result.

    role='tool' and source='code-worker' are the canonical values.
    Callers must not override these fields downstream.
    """
    msg: dict[str, Any] = {
        "role": ROLE_TOOL,
        "source": SOURCE_CODE_WORKER,
        "content": content,
    }
    if metadata:
        msg["metadata"] = metadata
    return msg


def build_claude_code_message(content: str, metadata: dict | None = None) -> dict:
    """
    Return a message dict suitable for persisting a Claude Code status/result.

    role='tool' and source='claude-code' are the canonical values.
    """
    msg: dict[str, Any] = {
        "role": ROLE_TOOL,
        "source": SOURCE_CLAUDE_CODE,
        "content": content,
    }
    if metadata:
        msg["metadata"] = metadata
    return msg


# ── Conversation message persistence helper ────────────────────────────────

def persist_tool_message(
    conversation: Any,
    content: str,
    source: str,
    metadata: dict | None = None,
) -> None:
    """
    Persist a tool/system message into *conversation*.

    Works with AgentConversation (has .messages JSONField) or any object
    that exposes an ``add_message(role, content, **kwargs)`` method.

    Ensures role='tool' is always written — never 'user'.
    """
    role = ROLE_TOOL

    # Try structured add_message API first
    if hasattr(conversation, "add_message"):
        try:
            conversation.add_message(
                role=role,
                content=content,
                source=source,
                **(metadata or {}),
            )
            return
        except TypeError:
            pass  # fallback to direct JSONField append

    # Direct JSONField append (AgentConversation.messages is a list)
    if hasattr(conversation, "messages") and isinstance(conversation.messages, list):
        entry: dict[str, Any] = {
            "role": role,
            "source": source,
            "content": content,
        }
        if metadata:
            entry["metadata"] = metadata
        conversation.messages.append(entry)
        conversation.save(update_fields=["messages"])
        return

    logger.warning(
        "persist_tool_message: conversation %r has no supported message API; "
        "skipping persist for source=%s",
        conversation,
        source,
    )

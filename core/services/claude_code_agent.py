"""
Autonomous Claude Code Agent
==============================

A persistent AI participant that watches PA conversations and responds
independently when addressed. Runs as a Celery task, uses the Anthropic
Claude API to generate responses, and posts them back to the conversation
via the store-only endpoint.

This enables true 3-way collaboration: Chris (human), Rigby (PA/GPT-5.2),
and Claude Code (engineering AI/Claude) in the same conversation.

Architecture:
- Triggered by a Celery task when a new message mentions "claude code" or "@claude"
- Loads recent conversation history for context
- Calls Anthropic Claude API with engineering-focused system prompt
- Posts response via store-only endpoint + WebSocket broadcast
- Does NOT trigger Rigby (avoids infinite loops)
"""
import json
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Patterns that indicate a message is directed at Claude Code
CLAUDE_CODE_PATTERNS = [
    re.compile(r'@claude[\s\-_]?code', re.IGNORECASE),
    re.compile(r'\bclaude\s*code\b', re.IGNORECASE),
    re.compile(r'^claude[,:\s]', re.IGNORECASE),  # "Claude, can you..."
]

# Don't respond to messages from ourselves
SELF_SOURCES = {'claude-code', 'claude_code_agent'}


def should_claude_code_respond(message_text: str, source: str) -> bool:
    """Check if a message is directed at Claude Code and should get a response."""
    if source in SELF_SOURCES:
        return False
    return any(p.search(message_text) for p in CLAUDE_CODE_PATTERNS)


def get_conversation_history(conversation_id: str, limit: int = 20) -> list:
    """Load recent conversation messages for context."""
    from core.models import ChatConversation

    rows = (
        ChatConversation.objects
        .filter(conversation_id=conversation_id)
        .order_by('-created_at')[:limit]
    )

    messages = []
    for row in reversed(list(rows)):
        if row.user_message:
            source = row.source or 'web'
            role_label = {
                'web': 'Chris',
                'claude-code': 'Claude Code',
                'claude_code_agent': 'Claude Code',
            }.get(source, source)
            messages.append({
                'role': 'user',
                'content': f"[{role_label}]: {row.user_message}",
            })
        if row.assistant_response:
            messages.append({
                'role': 'assistant',
                'content': f"[Rigby]: {row.assistant_response}",
            })

    return messages


SYSTEM_PROMPT = """You are Claude Code, an autonomous AI engineering assistant participating in a real-time collaborative chat.

PARTICIPANTS:
- Chris (DonkeyKing): The boss and primary decision-maker. A senior developer who built this platform.
- Rigby: The Personal Assistant (PA), powered by GPT-5.2. Handles tools, data queries, ops, and platform management.
- You (Claude Code): The engineering AI. You handle code, architecture, debugging, deployments, and technical problem-solving.

YOUR ROLE:
- You are a peer participant in the conversation, not a chatbot being prompted.
- Respond naturally and conversationally, like a senior developer in a team chat.
- Keep responses concise — this is a chat, not a document. 2-5 sentences is usually right.
- When you can help, offer to do so. When you can't, say so honestly.
- You can ask Rigby for data by saying "@rigby" in your response.
- You can suggest code changes, debug issues, and propose solutions.

WHAT YOU KNOW:
- This is the Donkey Betz Unified AI Platform (Django + Celery + PostgreSQL + Redis)
- 82 agents, 77 spiders, 134 services, 9 body systems
- You have deep knowledge of the codebase architecture
- You work on Railway (production deployment)

BEHAVIOR RULES:
- Only respond when directly addressed (your name is mentioned in the message).
- Be brief and actionable. No fluff.
- If Chris asks you AND Rigby something, respond with your part and let Rigby handle his.
- Never pretend to execute code or make changes — be honest about what you can and can't do from this context.
- Don't repeat what Rigby already said unless you're adding something new.
"""


def generate_response(conversation_id: str, trigger_message: str, trigger_source: str) -> Optional[str]:
    """
    Generate a Claude Code response using the Anthropic API.

    Args:
        conversation_id: The PA conversation ID
        trigger_message: The message that triggered the response
        trigger_source: Who sent the trigger message (web, pa, etc.)

    Returns:
        Generated response text, or None if generation fails
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        logger.error("[ClaudeCodeAgent] ANTHROPIC_API_KEY not set")
        return None

    # Build conversation context
    history = get_conversation_history(conversation_id, limit=20)

    # Build messages for Claude API
    messages = []
    for msg in history:
        messages.append(msg)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        content = response.content[0].text if response.content else None

        if content:
            logger.info(f"[ClaudeCodeAgent] Generated response ({len(content)} chars) for {conversation_id}")

        return content

    except Exception as e:
        logger.error(f"[ClaudeCodeAgent] API call failed: {e}")
        return None


def post_response(conversation_id: str, response_text: str):
    """Post Claude Code's response to the conversation via store-only + WebSocket."""
    from core.models import ChatConversation

    # Store the message
    chat_row = ChatConversation.objects.create(
        conversation_id=conversation_id,
        user_message=response_text,
        assistant_response='',  # No PA response — this IS the response
        source='claude-code',
        platform='agent',
        metadata={'autonomous': True, 'agent': 'claude_code_agent'},
    )

    # Broadcast via WebSocket
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"pa_conversation_{conversation_id}",
                {
                    "type": "message.created",
                    "message": {
                        "id": str(chat_row.id),
                        "role": "user",
                        "content": response_text,
                        "source": "claude-code",
                        "timestamp": chat_row.created_at.isoformat(),
                    }
                }
            )
    except Exception as e:
        logger.debug(f"[ClaudeCodeAgent] WebSocket broadcast failed: {e}")

    return chat_row


def handle_message(conversation_id: str, message_text: str, source: str) -> Optional[str]:
    """
    Full pipeline: check if we should respond, generate, and post.

    Called by Celery task or signal handler whenever a new message is stored.
    Returns the response text if one was generated, None otherwise.
    """
    if not should_claude_code_respond(message_text, source):
        return None

    logger.info(f"[ClaudeCodeAgent] Responding to message in {conversation_id} (from {source})")

    response = generate_response(conversation_id, message_text, source)
    if not response:
        return None

    post_response(conversation_id, response)
    return response

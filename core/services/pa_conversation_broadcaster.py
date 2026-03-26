"""
Helpers for broadcasting PA conversation messages over Django Channels.
Centralises role/source preservation so WebSocket events never drop metadata.
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


TOOL_SOURCES = frozenset({'code-worker', 'claude-code'})


def _resolve_role(role, source):
    """Return the canonical role, applying the legacy source fallback."""
    if role and role != 'user':
        return role
    if source in TOOL_SOURCES:
        return 'tool'
    return role or 'user'


def build_message_payload(message_obj=None, *, role=None, source=None,
                          content='', message_id=None, created_at=None,
                          metadata=None, **extra):
    """
    Build a WebSocket-ready dict for a conversation message.

    Accepts either a model instance (message_obj) or keyword arguments.
    Always emits role and source.
    """
    if message_obj is not None:
        role = getattr(message_obj, 'role', None)
        source = getattr(message_obj, 'source', None)
        content = getattr(message_obj, 'content', '')
        message_id = str(getattr(message_obj, 'id', '') or '')
        ts = getattr(message_obj, 'created_at', None)
        created_at = ts.isoformat() if ts else None
        metadata = getattr(message_obj, 'metadata', None) or {}

    resolved_role = _resolve_role(role, source)

    payload = {
        'type': 'chat_message',
        'role': resolved_role,
        'source': source or '',
        'content': content or '',
        'id': message_id or '',
        'created_at': created_at or '',
        'metadata': metadata or {},
        **extra,
    }
    return payload


def broadcast_message(group_name, message_obj=None, **kwargs):
    """
    Send a message payload to a channel group synchronously.

    Usage:
        broadcast_message('pa_user_42', message_obj=msg_instance)
    """
    payload = build_message_payload(message_obj, **kwargs)
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(group_name, payload)
    return payload

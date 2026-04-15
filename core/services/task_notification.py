"""
Task Completion Notifications — auto-post results to PA conversations.

When the PA triggers a Celery task via cockpit_tool.trigger_task, this
module stores notification metadata (conversation_id, user_id) in Redis.
When the task completes, the postrun signal handler reads the metadata
and posts a structured result message back to the conversation.

This closes the loop: Rigby triggers a task → task runs → result appears
automatically in the ChatUI without the user having to ask.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# Redis key prefix and TTL for notification metadata
_KEY_PREFIX = 'task_notify:'
_TTL_SECONDS = 3600  # 1 hour — tasks should complete well within this


def _get_redis():
    """Get a Redis connection, or None if unavailable."""
    try:
        from django.core.cache import caches
        cache = caches['default']
        # django-redis exposes the raw client
        if hasattr(cache, 'client'):
            return cache.client.get_client()
        # Fallback: try to connect directly
        import redis
        redis_url = getattr(settings, 'REDIS_URL', None)
        if redis_url:
            return redis.from_url(redis_url)
    except Exception as e:
        # Session 1103c: silently swallowing here meant every
        # register_task_notification call returned False with no
        # visible cause. The whole task-notification system (dispatch
        # receipts for PA "your task is running" toasts) was
        # effectively dark whenever Redis had a hiccup — now loud.
        logger.warning(
            "task_notification: Redis connection failed "
            "(%s: %s) — task dispatch receipts will be dropped",
            type(e).__name__, e,
        )
    return None


def register_task_notification(
    task_id: str,
    task_name: str,
    user_id,
    conversation_id: str,
) -> bool:
    """Store notification metadata for a dispatched task.

    Called at dispatch time (in cockpit_tool.trigger_task).
    Returns True if metadata was stored, False otherwise.
    """
    if not conversation_id:
        return False

    r = _get_redis()
    if not r:
        logger.debug('[TaskNotify] Redis unavailable, skipping registration for %s', task_id)
        return False

    key = f'{_KEY_PREFIX}{task_id}'
    data = json.dumps({
        'task_name': task_name,
        'user_id': str(user_id) if user_id else None,
        'conversation_id': conversation_id,
    })

    try:
        r.setex(key, _TTL_SECONDS, data)
        logger.info('[TaskNotify] Registered notification for task %s → conversation %s', task_id, conversation_id)
        return True
    except Exception as e:
        logger.debug('[TaskNotify] Failed to register: %s', e)
        return False


def check_and_notify(task_id: str, state: str, result=None, error=None) -> bool:
    """Check if a completed task has notification metadata and post to conversation.

    Called from the task_postrun / task_failure signal handlers.
    Returns True if a notification was posted, False otherwise.
    """
    r = _get_redis()
    if not r:
        return False

    key = f'{_KEY_PREFIX}{task_id}'
    try:
        raw = r.get(key)
        if not raw:
            return False  # No notification registered for this task

        data = json.loads(raw)
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        task_name = data.get('task_name', 'unknown')

        if not conversation_id:
            return False

        # Clean up the key immediately
        r.delete(key)

        # Resolve user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = None
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass

        # Build and post the notification
        from core.services.collaboration_protocol import post_structured_message

        # Format the task name for display
        short_name = task_name.rsplit('.', 1)[-1] if '.' in task_name else task_name

        if state == 'SUCCESS':
            # Format result for display
            body_parts = [f'Task `{task_name}` completed successfully.']
            if isinstance(result, dict):
                output = result.get('output', '')
                if output:
                    body_parts.append(f'\n```\n{str(output)[:1500]}\n```')
                else:
                    # Show top-level keys
                    summary = {k: str(v)[:200] for k, v in result.items()}
                    body_parts.append(f'\n```json\n{json.dumps(summary, indent=2)[:1500]}\n```')
            elif result is not None:
                body_parts.append(f'\n```\n{str(result)[:1500]}\n```')

            post_structured_message(
                user=user,
                conversation_id=conversation_id,
                msg_type='RESULT',
                title=f'{short_name} completed',
                body='\n'.join(body_parts),
                source='pa',
                metadata={'task_id': task_id, 'task_name': task_name},
            )
        else:
            # FAILURE
            error_str = str(error)[:1000] if error else 'Unknown error'
            post_structured_message(
                user=user,
                conversation_id=conversation_id,
                msg_type='ERROR',
                title=f'{short_name} failed',
                body=f'Task `{task_name}` failed.\n\nError: {error_str}',
                source='pa',
                metadata={'task_id': task_id, 'task_name': task_name, 'state': state},
            )

        logger.info(
            '[TaskNotify] Posted %s notification for task %s to conversation %s',
            state, task_id, conversation_id,
        )
        return True

    except Exception as e:
        logger.warning('[TaskNotify] Failed to notify for task %s: %s', task_id, e)
        return False

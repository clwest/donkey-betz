"""
In-App Messaging / Inbox API
==============================

Endpoints for user-to-user direct messaging with Rigby routing support.

- GET  /api/inbox/threads/              — list threads for current user
- POST /api/inbox/threads/              — create a new thread
- GET  /api/inbox/threads/<id>/messages/ — messages in a thread
- POST /api/inbox/threads/<id>/messages/ — send a message
- POST /api/inbox/threads/<id>/read/    — mark thread as read
- GET  /api/inbox/unread-count/         — total unread count
"""

import logging

from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Subquery, OuterRef, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models_messaging import MessageThread, ThreadParticipant, DirectMessage

logger = logging.getLogger(__name__)
User = get_user_model()


def _serialize_thread(thread, participant, other_users):
    """Serialize a thread for the API response."""
    last_msg = thread.messages.order_by('-created_at').first()
    return {
        'id': str(thread.id),
        'subject': thread.subject,
        'thread_type': thread.thread_type,
        'participants': [
            {'id': u.id, 'username': u.username}
            for u in other_users
        ],
        'unread_count': participant.unread_count if participant else 0,
        'is_muted': participant.is_muted if participant else False,
        'last_message': {
            'body': last_msg.body[:120] if last_msg else None,
            'sender': last_msg.sender.username if last_msg and last_msg.sender else last_msg.sender_type if last_msg else None,
            'created_at': last_msg.created_at.isoformat() if last_msg else None,
        } if last_msg else None,
        'updated_at': thread.updated_at.isoformat(),
        'created_at': thread.created_at.isoformat(),
    }


def _serialize_message(msg):
    """Serialize a message for the API response."""
    return {
        'id': str(msg.id),
        'body': msg.body,
        'sender': {
            'id': msg.sender.id if msg.sender else None,
            'username': msg.sender.username if msg.sender else None,
        },
        'sender_type': msg.sender_type,
        'created_at': msg.created_at.isoformat(),
        'metadata': msg.metadata,
    }


# ── Thread List / Create ────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def inbox_threads(request):
    """List or create message threads."""
    if request.method == 'GET':
        return _list_threads(request)
    return _create_thread(request)


def _list_threads(request):
    """List threads the user participates in, ordered by most recent activity."""
    participations = (
        ThreadParticipant.objects
        .filter(user=request.user, thread__is_archived=False)
        .select_related('thread')
        .order_by('-thread__updated_at')[:50]
    )

    threads = []
    for p in participations:
        other_users = User.objects.filter(
            thread_participations__thread=p.thread
        ).exclude(id=request.user.id)
        threads.append(_serialize_thread(p.thread, p, list(other_users)))

    return Response({'success': True, 'threads': threads})


def _create_thread(request):
    """Create a new thread with specified participants."""
    participant_ids = request.data.get('participants', [])
    # Also accept usernames
    participant_usernames = request.data.get('participant_usernames', [])
    subject = request.data.get('subject', '')
    initial_message = request.data.get('message', '')
    thread_type = request.data.get('thread_type', 'dm')

    if not participant_ids and not participant_usernames:
        return Response({'success': False, 'error': 'participants or participant_usernames required'}, status=400)

    # Resolve users
    users = set()
    if participant_ids:
        users.update(User.objects.filter(id__in=participant_ids))
    if participant_usernames:
        users.update(User.objects.filter(username__in=participant_usernames))

    if not users:
        return Response({'success': False, 'error': 'No valid participants found'}, status=400)

    # Always include the sender
    users.add(request.user)

    # For DMs, check if a thread already exists between these exact users
    if thread_type == 'dm' and len(users) == 2:
        other_user = (users - {request.user}).pop()
        existing = (
            MessageThread.objects
            .filter(thread_type='dm', is_archived=False)
            .filter(threadparticipant__user=request.user)
            .filter(threadparticipant__user=other_user)
            .first()
        )
        if existing:
            # Return existing thread instead of creating duplicate
            participant = ThreadParticipant.objects.get(thread=existing, user=request.user)
            other_users = [other_user]
            result = _serialize_thread(existing, participant, other_users)

            # Send the initial message in the existing thread if provided
            if initial_message:
                msg = DirectMessage.objects.create(
                    thread=existing,
                    sender=request.user,
                    body=initial_message,
                    sender_type='user',
                )
                existing.updated_at = timezone.now()
                existing.save(update_fields=['updated_at'])
                result['last_message'] = _serialize_message(msg)

            return Response({'success': True, 'thread': result, 'existed': True})

    # Create new thread
    thread = MessageThread.objects.create(
        subject=subject,
        thread_type=thread_type,
    )

    # Add participants
    for u in users:
        ThreadParticipant.objects.create(thread=thread, user=u)

    # Send initial message if provided
    if initial_message:
        DirectMessage.objects.create(
            thread=thread,
            sender=request.user,
            body=initial_message,
            sender_type='user',
        )

    participant = ThreadParticipant.objects.get(thread=thread, user=request.user)
    other_users = list(users - {request.user})
    result = _serialize_thread(thread, participant, other_users)

    # Broadcast to recipients via WebSocket
    _broadcast_thread_update(thread, request.user)

    return Response({'success': True, 'thread': result, 'existed': False}, status=201)


# ── Thread Messages ──────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def thread_messages(request, thread_id):
    """Get or send messages in a thread."""
    # Verify participation
    try:
        participant = ThreadParticipant.objects.select_related('thread').get(
            thread_id=thread_id, user=request.user
        )
    except ThreadParticipant.DoesNotExist:
        return Response({'success': False, 'error': 'Thread not found'}, status=404)

    if request.method == 'GET':
        return _get_messages(request, participant)
    return _send_message(request, participant)


def _get_messages(request, participant):
    """Get messages in a thread, ordered chronologically."""
    messages = (
        DirectMessage.objects
        .filter(thread=participant.thread)
        .select_related('sender')
        .order_by('created_at')[:200]
    )

    return Response({
        'success': True,
        'thread_id': str(participant.thread_id),
        'messages': [_serialize_message(m) for m in messages],
    })


def _send_message(request, participant):
    """Send a message in a thread."""
    body = request.data.get('body', '').strip()
    if not body:
        return Response({'success': False, 'error': 'Message body required'}, status=400)

    msg = DirectMessage.objects.create(
        thread=participant.thread,
        sender=request.user,
        body=body,
        sender_type='user',
        metadata=request.data.get('metadata', {}),
    )

    # Update thread timestamp
    participant.thread.updated_at = timezone.now()
    participant.thread.save(update_fields=['updated_at'])

    # Auto-mark as read for sender
    participant.last_read_at = timezone.now()
    participant.save(update_fields=['last_read_at'])

    # Broadcast to other participants
    _broadcast_new_message(participant.thread, msg)

    return Response({
        'success': True,
        'message': _serialize_message(msg),
    }, status=201)


# ── Mark Read ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_thread_read(request, thread_id):
    """Mark all messages in a thread as read for the current user."""
    try:
        participant = ThreadParticipant.objects.get(
            thread_id=thread_id, user=request.user
        )
    except ThreadParticipant.DoesNotExist:
        return Response({'success': False, 'error': 'Thread not found'}, status=404)

    participant.last_read_at = timezone.now()
    participant.save(update_fields=['last_read_at'])

    return Response({'success': True})


# ── Unread Count ─────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """Return total unread message count across all threads."""
    participations = ThreadParticipant.objects.filter(
        user=request.user,
        thread__is_archived=False,
        is_muted=False,
    )

    total = 0
    for p in participations:
        total += DirectMessage.objects.filter(
            thread=p.thread,
            created_at__gt=p.last_read_at,
        ).exclude(sender=request.user).count()

    return Response({'success': True, 'unread_count': total})


# ── WebSocket Broadcasting ──────────────────────────────────────────────────

def _broadcast_new_message(thread, message):
    """Broadcast a new message to all thread participants via WebSocket."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        participants = ThreadParticipant.objects.filter(thread=thread).select_related('user')
        for p in participants:
            if p.user_id == (message.sender_id if message.sender else None):
                continue  # Don't notify sender
            async_to_sync(channel_layer.group_send)(
                f"inbox_{p.user_id}",
                {
                    'type': 'inbox.new_message',
                    'thread_id': str(thread.id),
                    'message': _serialize_message(message),
                }
            )
    except Exception as e:
        logger.debug("Inbox broadcast failed: %s", e)


def _broadcast_thread_update(thread, sender_user):
    """Broadcast thread update (new thread created) to participants."""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        if not channel_layer:
            return

        participants = ThreadParticipant.objects.filter(thread=thread).select_related('user')
        for p in participants:
            if p.user_id == sender_user.id:
                continue
            async_to_sync(channel_layer.group_send)(
                f"inbox_{p.user_id}",
                {
                    'type': 'inbox.thread_created',
                    'thread_id': str(thread.id),
                }
            )
    except Exception as e:
        logger.debug("Inbox thread broadcast failed: %s", e)

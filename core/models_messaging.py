"""
In-App Messaging System
========================

Direct messaging between platform users, with Rigby (PA) as an optional
routing intermediary.  Users can message each other directly or say
"Hey Rigby, ask Chris about X" and Rigby creates a routed message.

Models:
- MessageThread: A conversation between 2+ users
- ThreadParticipant: M2M join with per-user read cursor
- DirectMessage: Individual message in a thread
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class MessageThread(models.Model):
    """A conversation thread between platform users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=255, blank=True, default='')

    THREAD_TYPE_CHOICES = [
        ('dm', 'Direct Message'),
        ('group', 'Group'),
        ('rigby_routed', 'Rigby Routed'),
    ]
    thread_type = models.CharField(
        max_length=20,
        choices=THREAD_TYPE_CHOICES,
        default='dm',
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False, db_index=True)

    # Metadata for Rigby-routed messages
    metadata = models.JSONField(default=dict, blank=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ThreadParticipant',
        related_name='message_threads',
    )

    class Meta:
        app_label = 'core'
        db_table = 'message_threads'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Thread {self.id} ({self.thread_type})"

    @property
    def participant_usernames(self):
        return list(
            self.threadparticipant_set
            .select_related('user')
            .values_list('user__username', flat=True)
        )


class ThreadParticipant(models.Model):
    """Join table: tracks per-user read state in a thread."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='thread_participations',
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(default=timezone.now)
    is_muted = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'
        db_table = 'thread_participants'
        unique_together = [('thread', 'user')]

    def __str__(self):
        return f"{self.user} in {self.thread_id}"

    @property
    def unread_count(self):
        return DirectMessage.objects.filter(
            thread=self.thread,
            created_at__gt=self.last_read_at,
        ).exclude(sender=self.user).count()


class DirectMessage(models.Model):
    """A single message in a thread."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(
        MessageThread,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_messages',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Optional: who/what triggered this message
    SENDER_TYPE_CHOICES = [
        ('user', 'User'),
        ('rigby', 'Rigby (PA)'),
        ('system', 'System'),
    ]
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_TYPE_CHOICES,
        default='user',
    )

    # Rich metadata (routed_by, priority, original_prompt, etc.)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'core'
        db_table = 'direct_messages'
        ordering = ['created_at']

    def __str__(self):
        sender_name = self.sender.username if self.sender else self.sender_type
        return f"{sender_name}: {self.body[:50]}"

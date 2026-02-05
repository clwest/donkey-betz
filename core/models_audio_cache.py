"""
Audio Cache Model - Session 926
================================

Caches TTS audio to avoid regenerating the same content.
Uses content_hash (SHA256 of text + voice_id) for deduplication.
"""

import hashlib
import uuid
from django.db import models
from django.utils import timezone


def audio_cache_upload_path(instance, filename):
    """Generate upload path: audio_cache/YYYY/MM/filename"""
    now = timezone.now()
    return f"audio_cache/{now.year}/{now.month:02d}/{filename}"


class AudioCache(models.Model):
    """
    Caches generated TTS audio to avoid redundant API calls.

    Deduplication is based on content_hash = SHA256(text + voice_id).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Deduplication key
    content_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="SHA256 hash of text + voice_id for deduplication"
    )

    # Audio file
    audio_file = models.FileField(
        upload_to=audio_cache_upload_path,
        help_text="Cached audio file (MP3)"
    )

    # Content metadata
    text_preview = models.CharField(
        max_length=200,
        help_text="First 200 chars of the text for debugging"
    )
    text_length = models.IntegerField(
        help_text="Full length of the original text"
    )
    voice_id = models.CharField(
        max_length=100,
        help_text="ElevenLabs voice ID used"
    )
    voice_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Human-readable voice name if known"
    )

    # Audio metadata
    duration_seconds = models.FloatField(
        null=True, blank=True,
        help_text="Duration of the audio file"
    )
    file_size_bytes = models.IntegerField(
        help_text="Size of the audio file in bytes"
    )

    # Cost tracking
    generation_cost = models.DecimalField(
        max_digits=6, decimal_places=4, default=0,
        help_text="Estimated cost in USD (~$0.30 per 1000 chars)"
    )

    # Access metrics for cache eviction
    access_count = models.IntegerField(
        default=1,
        help_text="Number of times this cache entry was accessed"
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text="Last time this cache entry was accessed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Audio Cache"
        verbose_name_plural = "Audio Cache"
        ordering = ['-last_accessed']
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['last_accessed']),
            models.Index(fields=['voice_id']),
        ]

    def __str__(self):
        return f"AudioCache({self.voice_name or self.voice_id}: {self.text_preview[:50]}...)"

    @classmethod
    def compute_hash(cls, text: str, voice_id: str) -> str:
        """Compute the content hash for deduplication."""
        content = f"{text}|{voice_id}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @classmethod
    def get_cached(cls, text: str, voice_id: str):
        """
        Look up cached audio by text and voice_id.

        Returns the AudioCache instance if found, None otherwise.
        Updates access_count and last_accessed on hit.
        """
        content_hash = cls.compute_hash(text, voice_id)
        try:
            cache_entry = cls.objects.get(content_hash=content_hash)
            # Update access metrics
            cache_entry.access_count += 1
            cache_entry.save(update_fields=['access_count', 'last_accessed'])
            return cache_entry
        except cls.DoesNotExist:
            return None

    @classmethod
    def estimate_cost(cls, text_length: int) -> float:
        """Estimate TTS cost based on text length (~$0.30 per 1000 chars)."""
        return (text_length / 1000) * 0.30

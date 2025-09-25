"""
Style Memory models for tracking user preferences and style patterns.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
import uuid

User = get_user_model()


class StyleMemory(models.Model):
    """Tracks user interactions with generated content"""
    
    INTERACTION_TYPES = [
        ('love', 'Love'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('save', 'Save'),
        ('share', 'Share'),
        ('download', 'Download'),
        ('remix', 'Remix'),
        ('delete', 'Delete'),
        ('rate_1', 'Rate 1 Star'),
        ('rate_2', 'Rate 2 Stars'),
        ('rate_3', 'Rate 3 Stars'),
        ('rate_4', 'Rate 4 Stars'),
        ('rate_5', 'Rate 5 Stars'),
        ('generate_similar', 'Generate Similar'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='style_memories')
    content_id = models.CharField(max_length=255, db_index=True)
    parent_content_id = models.CharField(max_length=255, null=True, blank=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    
    # Style analysis
    recipe = models.JSONField(default=dict, blank=True)
    style_elements = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    color_palette = ArrayField(
        models.CharField(max_length=7),
        default=list,
        blank=True
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    prompt = models.TextField(blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'style_memory'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['content_id']),
            models.Index(fields=['interaction_type']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.content_id}"


class StylePattern(models.Model):
    """Detected patterns in user preferences"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='style_patterns')
    pattern_type = models.CharField(max_length=50)  # color, composition, subject, style
    pattern_value = models.CharField(max_length=255)
    confidence = models.FloatField(default=0.5)
    frequency = models.IntegerField(default=1)
    
    # Relationships
    related_memories = models.ManyToManyField(StyleMemory, blank=True)
    
    # Timestamps
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    
    class Meta:
        app_label = 'style_memory'
        unique_together = ['user', 'pattern_type', 'pattern_value']
        ordering = ['-confidence', '-frequency']
        
    def __str__(self):
        return f"{self.user.username} - {self.pattern_type}: {self.pattern_value}"


class StyleSuggestion(models.Model):
    """AI-generated style suggestions based on patterns"""
    
    SUGGESTION_STATUS = [
        ('pending', 'Pending'),
        ('used', 'Used'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='style_suggestions')
    
    # Suggestion content
    title = models.CharField(max_length=255)
    description = models.TextField()
    prompt_template = models.TextField()
    confidence = models.FloatField(default=0.5)
    
    # Based on patterns
    based_on_patterns = models.ManyToManyField(StylePattern)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=SUGGESTION_STATUS, default='pending')
    used_at = models.DateTimeField(null=True, blank=True)
    result_content_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'style_memory'
        ordering = ['-confidence', '-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ContentLineage(models.Model):
    """Track the evolution and relationships between content"""
    
    content_id = models.CharField(max_length=255, unique=True)
    parent_id = models.CharField(max_length=255, null=True, blank=True)
    root_id = models.CharField(max_length=255)
    
    # Generation metadata
    generation = models.IntegerField(default=0)
    branch_name = models.CharField(max_length=100, blank=True)
    
    # Variation details
    variation_type = models.CharField(max_length=50, blank=True)  # remix, upscale, variation, etc.
    variation_params = models.JSONField(default=dict, blank=True)
    
    # Performance metrics
    total_interactions = models.IntegerField(default=0)
    positive_interactions = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        app_label = 'style_memory'
        ordering = ['root_id', 'generation', 'created_at']
        indexes = [
            models.Index(fields=['content_id']),
            models.Index(fields=['parent_id']),
            models.Index(fields=['root_id']),
        ]
        
    def __str__(self):
        return f"Lineage: {self.content_id} (Gen {self.generation})"

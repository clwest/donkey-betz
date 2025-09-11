"""
Style Memory serializers.
"""

from rest_framework import serializers
from .models import StyleMemory, StylePattern, StyleSuggestion, ContentLineage


class StyleMemorySerializer(serializers.ModelSerializer):
    """Serializer for StyleMemory model"""
    
    class Meta:
        model = StyleMemory
        fields = [
            'id', 'user', 'content_id', 'parent_content_id', 'interaction_type',
            'recipe', 'style_elements', 'color_palette', 'notes', 'prompt',
            'model_used', 'parameters', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StylePatternSerializer(serializers.ModelSerializer):
    """Serializer for StylePattern model"""
    
    class Meta:
        model = StylePattern
        fields = [
            'id', 'user', 'pattern_type', 'pattern_value', 'confidence',
            'frequency', 'first_seen', 'last_seen'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen']


class StyleSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for StyleSuggestion model"""
    
    class Meta:
        model = StyleSuggestion
        fields = [
            'id', 'user', 'title', 'description', 'prompt_template',
            'confidence', 'status', 'used_at', 'result_content_id',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']


class ContentLineageSerializer(serializers.ModelSerializer):
    """Serializer for ContentLineage model"""
    
    class Meta:
        model = ContentLineage
        fields = [
            'content_id', 'parent_id', 'root_id', 'generation', 'branch_name',
            'variation_type', 'variation_params', 'total_interactions',
            'positive_interactions', 'created_at'
        ]
        read_only_fields = ['created_at']


class InteractionRequestSerializer(serializers.Serializer):
    """Serializer for capturing interactions"""
    
    content_id = serializers.CharField(max_length=255)
    interaction_type = serializers.ChoiceField(choices=[
        'love', 'like', 'dislike', 'save', 'share', 'download', 'remix', 'delete',
        'rate_1', 'rate_2', 'rate_3', 'rate_4', 'rate_5',  # Support star ratings
        'generate_similar'  # Support variation generation
    ])
    parent_content_id = serializers.CharField(max_length=255, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class StyleInsightsSerializer(serializers.Serializer):
    """Serializer for style insights response"""
    
    total_interactions = serializers.IntegerField()
    favorite_styles = serializers.ListField(child=serializers.DictField())
    color_preferences = serializers.ListField(child=serializers.DictField())
    recent_patterns = serializers.ListField(child=serializers.DictField())
    suggestions_available = serializers.IntegerField()
    evolution_data = serializers.DictField()


class VariationRequestSerializer(serializers.Serializer):
    """Serializer for variation generation requests"""
    
    base_content_id = serializers.CharField(max_length=255)
    variation_strength = serializers.FloatField(min_value=0.0, max_value=1.0, default=0.5)
    preserve_elements = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    modify_elements = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    custom_prompt = serializers.CharField(required=False, allow_blank=True)
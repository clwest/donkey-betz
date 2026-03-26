"""
Serializers for PAConversation / PAConversationMessage that preserve
role and source without defaulting to 'user'.
"""
from rest_framework import serializers


class PAConversationMessageSerializer(serializers.ModelSerializer):
    """
    Serializes a single PA conversation message.
    Ensures role and source are always present in the payload so the
    frontend can determine how to render the bubble without guessing.
    """

    role = serializers.CharField(read_only=True)
    source = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        # Import lazily to avoid circular imports at module load time.
        from core.models import PAConversationMessage  # noqa: F401
        model = PAConversationMessage
        fields = [
            'id',
            'role',
            'source',
            'content',
            'created_at',
            'metadata',
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Guarantee role is never silently absent or None.
        if not data.get('role'):
            src = data.get('source') or ''
            if src in ('code-worker', 'claude-code'):
                data['role'] = 'tool'
            else:
                data['role'] = 'user'
        return data

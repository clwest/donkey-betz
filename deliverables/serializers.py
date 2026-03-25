from rest_framework import serializers
from .models import Deliverable


class DeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverable
        fields = [
            'id',
            'title',
            'description',
            'status',
            'workspace',
            'content',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

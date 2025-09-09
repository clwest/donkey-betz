"""
Content Management System Serializers

REST API serializers for content management, generation, and RAG operations.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    ContentTemplate, Document, DocumentEmbedding, KnowledgeBase,
    ContentGeneration, ContentWorkflow, WorkflowExecution, ContentAnalytics,
    EmbeddingModel
)
from .processors import pipeline
from .embeddings import rag_system

User = get_user_model()


class ContentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for content templates"""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentTemplate
        fields = [
            'id', 'name', 'display_name', 'description', 'template_type',
            'system_prompt', 'user_prompt_template', 'variables', 'output_format',
            'llm_provider', 'llm_model', 'generation_config', 'tags', 'category',
            'usage_count', 'avg_generation_time', 'success_rate', 'avg_user_rating',
            'creator', 'creator_name', 'is_public', 'is_verified', 'is_active',
            'created_at', 'updated_at', 'usage_stats'
        ]
        read_only_fields = ['id', 'creator', 'usage_count', 'avg_generation_time', 
                           'success_rate', 'avg_user_rating', 'created_at', 'updated_at']
    
    def get_usage_stats(self, obj):
        """Get usage statistics"""
        return {
            'total_uses': obj.usage_count,
            'success_rate': obj.success_rate,
            'avg_time': obj.avg_generation_time,
            'avg_rating': obj.avg_user_rating
        }
    
    def validate_variables(self, value):
        """Validate template variables structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Variables must be a dictionary")
        
        for var_name, var_config in value.items():
            if not isinstance(var_config, dict):
                raise serializers.ValidationError(f"Variable '{var_name}' config must be a dictionary")
            
            required_fields = ['type', 'description']
            for field in required_fields:
                if field not in var_config:
                    raise serializers.ValidationError(f"Variable '{var_name}' missing required field: {field}")
        
        return value


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for documents"""
    
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    has_embeddings = serializers.SerializerMethodField()
    processing_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'document_type', 'file_path',
            'original_filename', 'file_size', 'mime_type', 'raw_content',
            'processed_content', 'content_hash', 'status', 'source',
            'processing_log', 'error_message', 'language', 'word_count',
            'readability_score', 'extracted_metadata', 'key_phrases', 'entities',
            'tags', 'category', 'collection', 'owner', 'owner_name', 'is_public',
            'view_count', 'download_count', 'last_accessed', 'source_system',
            'source_reference', 'cross_references', 'created_at', 'updated_at',
            'has_embeddings', 'processing_status'
        ]
        read_only_fields = ['id', 'owner', 'content_hash', 'processing_log', 
                           'word_count', 'readability_score', 'extracted_metadata',
                           'key_phrases', 'entities', 'view_count', 'download_count',
                           'last_accessed', 'created_at', 'updated_at']
    
    def get_has_embeddings(self, obj):
        """Check if document has embeddings"""
        return obj.embeddings.exists()
    
    def get_processing_status(self, obj):
        """Get processing status summary"""
        return {
            'status': obj.status,
            'error_message': obj.error_message if obj.error_message else None,
            'last_step': obj.processing_log[-1] if obj.processing_log else None
        }


class DocumentEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer for document embeddings"""
    
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentEmbedding
        fields = [
            'id', 'document', 'document_title', 'embedding_model', 'chunk_index',
            'chunk_text', 'chunk_size', 'overlap_size', 'embedding_dimension',
            'context_before', 'context_after', 'metadata', 'processing_time_ms',
            'embedding_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'embedding_dimension', 'processing_time_ms',
                           'embedding_cost', 'created_at', 'updated_at']


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """Serializer for knowledge bases"""
    
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    statistics = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'name', 'description', 'embedding_model', 'chunk_size',
            'chunk_overlap', 'categories', 'tags', 'document_count',
            'total_chunks', 'total_tokens', 'last_indexed', 'owner', 'owner_name',
            'is_public', 'domain', 'integration_config', 'created_at',
            'updated_at', 'statistics', 'documents'
        ]
        read_only_fields = ['id', 'owner', 'document_count', 'total_chunks',
                           'total_tokens', 'last_indexed', 'created_at', 'updated_at']
    
    def get_statistics(self, obj):
        """Get knowledge base statistics"""
        return {
            'documents': obj.document_count,
            'chunks': obj.total_chunks,
            'tokens': obj.total_tokens,
            'last_indexed': obj.last_indexed
        }
    
    def get_documents(self, obj):
        """Get recent documents in knowledge base"""
        documents = obj.get_documents()[:10]  # Limit to 10 recent documents
        return DocumentSerializer(documents, many=True, context=self.context).data


class ContentGenerationSerializer(serializers.ModelSerializer):
    """Serializer for content generation requests and results"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    template_name = serializers.CharField(source='template.display_name', read_only=True)
    kb_name = serializers.CharField(source='knowledge_base.name', read_only=True)
    performance_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentGeneration
        fields = [
            'id', 'user', 'user_name', 'template', 'template_name', 'prompt',
            'system_prompt', 'generation_config', 'knowledge_base', 'kb_name',
            'rag_context', 'generated_content', 'status', 'generation_time_ms',
            'token_usage', 'generation_cost', 'quality_score', 'user_rating',
            'user_feedback', 'error_message', 'retry_count', 'source_system',
            'workflow_context', 'output_document', 'export_formats',
            'created_at', 'updated_at', 'performance_metrics'
        ]
        read_only_fields = ['id', 'user', 'generated_content', 'status',
                           'generation_time_ms', 'token_usage', 'generation_cost',
                           'quality_score', 'error_message', 'retry_count',
                           'output_document', 'export_formats', 'created_at', 'updated_at']
    
    def get_performance_metrics(self, obj):
        """Get performance metrics"""
        metrics = {
            'generation_time': obj.generation_time_ms,
            'cost': float(obj.generation_cost) if obj.generation_cost else 0.0,
            'status': obj.status
        }
        
        if obj.token_usage:
            metrics['tokens'] = obj.token_usage
        
        if obj.quality_score:
            metrics['quality_score'] = obj.quality_score
        
        if obj.user_rating:
            metrics['user_rating'] = obj.user_rating
        
        return metrics


class ContentWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for content workflows"""
    
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    workflow_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentWorkflow
        fields = [
            'id', 'name', 'description', 'workflow_steps', 'default_config',
            'execution_count', 'success_rate', 'avg_execution_time',
            'creator', 'creator_name', 'is_public', 'domain', 'integration_points',
            'created_at', 'updated_at', 'workflow_stats'
        ]
        read_only_fields = ['id', 'creator', 'execution_count', 'success_rate',
                           'avg_execution_time', 'created_at', 'updated_at']
    
    def get_workflow_stats(self, obj):
        """Get workflow statistics"""
        return {
            'executions': obj.execution_count,
            'success_rate': obj.success_rate,
            'avg_time': obj.avg_execution_time
        }
    
    def validate_workflow_steps(self, value):
        """Validate workflow steps structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Workflow steps must be a list")
        
        for i, step in enumerate(value):
            if not isinstance(step, dict):
                raise serializers.ValidationError(f"Step {i} must be a dictionary")
            
            required_fields = ['name', 'type']
            for field in required_fields:
                if field not in step:
                    raise serializers.ValidationError(f"Step {i} missing required field: {field}")
        
        return value


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for workflow executions"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    execution_status = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'user', 'user_name', 'input_data',
            'execution_config', 'status', 'current_step', 'progress_percentage',
            'step_results', 'final_output', 'started_at', 'completed_at',
            'execution_time_seconds', 'error_message', 'error_step',
            'agent_execution', 'websocket_channel', 'created_at', 'updated_at',
            'execution_status'
        ]
        read_only_fields = ['id', 'user', 'status', 'current_step', 'progress_percentage',
                           'step_results', 'final_output', 'started_at', 'completed_at',
                           'execution_time_seconds', 'error_message', 'error_step',
                           'created_at', 'updated_at']
    
    def get_execution_status(self, obj):
        """Get execution status summary"""
        return {
            'status': obj.status,
            'progress': obj.progress_percentage,
            'current_step': obj.current_step,
            'error': obj.error_message if obj.error_message else None
        }


class ContentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for content analytics"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ContentAnalytics
        fields = [
            'id', 'metric_name', 'metric_type', 'metric_value', 'context',
            'subsystem', 'timestamp', 'time_period', 'user', 'user_name',
            'document', 'template', 'knowledge_base'
        ]
        read_only_fields = ['id', 'timestamp']


# Special serializers for API operations

class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    
    file = serializers.FileField()
    title = serializers.CharField(max_length=500, required=False)
    description = serializers.CharField(required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    category = serializers.CharField(max_length=100, required=False)
    collection = serializers.CharField(max_length=200, required=False)
    is_public = serializers.BooleanField(default=False)
    auto_process = serializers.BooleanField(default=True)
    generate_embeddings = serializers.BooleanField(default=True)
    embedding_model = serializers.ChoiceField(
        choices=[choice.value for choice in EmbeddingModel],
        default=EmbeddingModel.OPENAI_SMALL.value,
        required=False
    )


class SemanticSearchSerializer(serializers.Serializer):
    """Serializer for semantic search requests"""
    
    query = serializers.CharField(max_length=1000)
    knowledge_base_id = serializers.UUIDField(required=False)
    embedding_model = serializers.ChoiceField(
        choices=[choice.value for choice in EmbeddingModel],
        default=EmbeddingModel.OPENAI_SMALL.value,
        required=False
    )
    limit = serializers.IntegerField(min_value=1, max_value=50, default=10)
    similarity_threshold = serializers.FloatField(min_value=0.0, max_value=1.0, default=0.7)
    include_metadata = serializers.BooleanField(default=True)


class ContentGenerationRequestSerializer(serializers.Serializer):
    """Serializer for content generation requests"""
    
    template_id = serializers.UUIDField(required=False)
    prompt = serializers.CharField(max_length=5000)
    system_prompt = serializers.CharField(max_length=2000, required=False)
    variables = serializers.DictField(required=False)
    use_rag = serializers.BooleanField(default=False)
    knowledge_base_id = serializers.UUIDField(required=False)
    rag_query = serializers.CharField(max_length=1000, required=False)
    generation_config = serializers.DictField(required=False)
    output_format = serializers.ChoiceField(
        choices=['text', 'markdown', 'html', 'json'],
        default='markdown',
        required=False
    )
    save_as_document = serializers.BooleanField(default=True)


class WorkflowExecutionRequestSerializer(serializers.Serializer):
    """Serializer for workflow execution requests"""
    
    workflow_id = serializers.UUIDField()
    input_data = serializers.DictField()
    execution_config = serializers.DictField(required=False)
    async_execution = serializers.BooleanField(default=True)
    websocket_channel = serializers.CharField(max_length=255, required=False)
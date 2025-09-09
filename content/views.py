"""
Content Management System Views

Comprehensive REST API views for content management, generation, and RAG operations.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List
from decimal import Decimal

from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import Http404, FileResponse

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (
    ContentTemplate, Document, DocumentEmbedding, KnowledgeBase,
    ContentGeneration, ContentWorkflow, WorkflowExecution, ContentAnalytics,
    EmbeddingModel, ContentStatus
)
from .serializers import (
    ContentTemplateSerializer, DocumentSerializer, DocumentEmbeddingSerializer,
    KnowledgeBaseSerializer, ContentGenerationSerializer, ContentWorkflowSerializer,
    WorkflowExecutionSerializer, ContentAnalyticsSerializer,
    DocumentUploadSerializer, SemanticSearchSerializer,
    ContentGenerationRequestSerializer, WorkflowExecutionRequestSerializer
)
from .processors import pipeline
from .embeddings import rag_system
from .services import ContentGenerationService, WorkflowExecutionService

logger = logging.getLogger(__name__)


class ContentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing content templates"""
    
    serializer_class = ContentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get templates based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return ContentTemplate.objects.all()
        
        # Regular users see public templates and their own
        return ContentTemplate.objects.filter(
            Q(is_public=True, is_active=True) | Q(creator=user)
        )
    
    def perform_create(self, serializer):
        """Set creator when creating template"""
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_generation(self, request, pk=None):
        """Test content generation with a template"""
        template = self.get_object()
        
        # Get test variables from request
        variables = request.data.get('variables', {})
        
        try:
            # Render prompt
            rendered_prompt = template.render_prompt(**variables)
            
            return Response({
                'success': True,
                'rendered_prompt': rendered_prompt,
                'system_prompt': template.system_prompt,
                'generation_config': template.generation_config
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular templates by usage"""
        templates = self.get_queryset().filter(
            usage_count__gt=0
        ).order_by('-usage_count')[:20]
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get available template categories"""
        categories = ContentTemplate.objects.filter(
            is_active=True, is_public=True
        ).values_list('category', flat=True).distinct()
        
        return Response({
            'categories': [cat for cat in categories if cat]
        })


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents"""
    
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Get documents based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return Document.objects.all()
        
        # Regular users see public documents and their own
        return Document.objects.filter(
            Q(is_public=True, is_active=True) | 
            Q(owner=user) |
            Q(allowed_users=user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Set owner when creating document"""
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process a new document"""
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get uploaded file
            uploaded_file = serializer.validated_data['file']
            
            # Save file
            file_path = default_storage.save(
                f'documents/{uploaded_file.name}',
                uploaded_file
            )
            
            # Create document
            document_data = {
                'title': serializer.validated_data.get('title', uploaded_file.name),
                'description': serializer.validated_data.get('description', ''),
                'original_filename': uploaded_file.name,
                'file_path': file_path,
                'file_size': uploaded_file.size,
                'mime_type': uploaded_file.content_type,
                'tags': serializer.validated_data.get('tags', []),
                'category': serializer.validated_data.get('category', ''),
                'collection': serializer.validated_data.get('collection', ''),
                'is_public': serializer.validated_data.get('is_public', False),
                'owner': request.user,
                'source': 'upload',
                'status': 'pending'
            }
            
            # Detect document type based on file extension and MIME type
            document_type = self._detect_document_type(uploaded_file.name, uploaded_file.content_type)
            document_data['document_type'] = document_type
            
            document = Document.objects.create(**document_data)
            
            # Process document if requested
            if serializer.validated_data.get('auto_process', True):
                self._process_document_async(
                    document, 
                    serializer.validated_data.get('generate_embeddings', True),
                    serializer.validated_data.get('embedding_model', EmbeddingModel.OPENAI_SMALL.value)
                )
            
            doc_serializer = DocumentSerializer(document, context={'request': request})
            return Response(doc_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            return Response({
                'error': 'Document upload failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process document content and generate embeddings"""
        document = self.get_object()
        
        if document.status == 'processing':
            return Response({
                'error': 'Document is already being processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        embedding_model = request.data.get('embedding_model', EmbeddingModel.OPENAI_SMALL.value)
        generate_embeddings = request.data.get('generate_embeddings', True)
        
        # Start processing
        self._process_document_async(document, generate_embeddings, embedding_model)
        
        return Response({
            'message': 'Document processing started',
            'status': 'processing'
        })
    
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        """Get document content"""
        document = self.get_object()
        document.increment_view_count()
        
        return Response({
            'title': document.title,
            'content': document.get_content(),
            'metadata': document.extracted_metadata,
            'word_count': document.word_count,
            'language': document.language,
            'key_phrases': document.key_phrases
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download original document file"""
        document = self.get_object()
        
        if not document.file_path or not default_storage.exists(document.file_path):
            raise Http404("File not found")
        
        document.download_count += 1
        document.save(update_fields=['download_count'])
        
        file_path = default_storage.path(document.file_path)
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=document.original_filename or document.title
        )
        return response
    
    @action(detail=True, methods=['get'])
    def embeddings(self, request, pk=None):
        """Get document embeddings"""
        document = self.get_object()
        embeddings = document.embeddings.all()
        
        serializer = DocumentEmbeddingSerializer(embeddings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search documents by content"""
        query = request.data.get('query', '')
        if not query:
            return Response({
                'error': 'Query parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Text-based search
        documents = self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(processed_content__icontains=query) |
            Q(key_phrases__contains=[query])
        )[:20]
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    def _detect_document_type(self, filename: str, mime_type: str) -> str:
        """Detect document type from filename and MIME type"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        type_mapping = {
            'txt': 'text',
            'md': 'markdown',
            'markdown': 'markdown',
            'html': 'html',
            'htm': 'html',
            'pdf': 'pdf',
            'docx': 'docx',
            'rtf': 'rtf',
            'json': 'json',
            'csv': 'csv',
            'xml': 'xml',
            'yaml': 'yaml',
            'yml': 'yaml',
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'sql': 'sql',
        }
        
        return type_mapping.get(ext, 'text')
    
    def _process_document_async(self, document: Document, generate_embeddings: bool, embedding_model: str):
        """Start asynchronous document processing"""
        # In production, this would be handled by Celery or similar
        # For now, we'll just update the status
        try:
            # Process document content
            if document.file_path and default_storage.exists(document.file_path):
                file_path = default_storage.path(document.file_path)
                result = pipeline.process_document(file_path)
                
                if result.success:
                    document.raw_content = result.raw_content
                    document.processed_content = result.processed_content
                    document.extracted_metadata = result.metadata
                    document.language = result.language
                    document.word_count = result.word_count
                    document.key_phrases = result.key_phrases
                    document.entities = result.entities
                    document.processing_log = result.processing_steps
                    document.status = ContentStatus.PROCESSED
                else:
                    document.error_message = result.error_message
                    document.processing_log = result.processing_steps
                    document.status = ContentStatus.FAILED
                
                document.save()
                
                # Generate embeddings if requested and processing was successful
                if generate_embeddings and result.success:
                    # This would be handled asynchronously in production
                    pass
        
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            document.status = ContentStatus.FAILED
            document.error_message = str(e)
            document.save()


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing knowledge bases"""
    
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get knowledge bases based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return KnowledgeBase.objects.all()
        
        return KnowledgeBase.objects.filter(
            Q(is_public=True, is_active=True) | Q(owner=user) | Q(contributors=user)
        ).distinct()
    
    def perform_create(self, serializer):
        """Set owner when creating knowledge base"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """Add document to knowledge base"""
        kb = self.get_object()
        document_id = request.data.get('document_id')
        
        try:
            document = Document.objects.get(id=document_id, owner=request.user)
            document.collection = kb.name
            document.save()
            
            # Update knowledge base statistics
            kb.update_statistics()
            
            return Response({
                'message': 'Document added to knowledge base',
                'document_title': document.title
            })
        
        except Document.DoesNotExist:
            return Response({
                'error': 'Document not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def semantic_search(self, request, pk=None):
        """Perform semantic search within knowledge base"""
        kb = self.get_object()
        serializer = SemanticSearchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Perform async search
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            search_results = loop.run_until_complete(
                rag_system.semantic_search(
                    query=serializer.validated_data['query'],
                    knowledge_base=kb,
                    embedding_model=EmbeddingModel(serializer.validated_data['embedding_model']),
                    limit=serializer.validated_data['limit'],
                    similarity_threshold=serializer.validated_data['similarity_threshold']
                )
            )
            
            return Response({
                'results': [
                    {
                        'document_id': result.document_id,
                        'document_title': result.document_title,
                        'chunk_text': result.chunk_text,
                        'similarity_score': result.similarity_score,
                        'metadata': result.metadata if serializer.validated_data.get('include_metadata') else None
                    }
                    for result in search_results
                ],
                'total_results': len(search_results)
            })
        
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return Response({
                'error': 'Search failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reindex(self, request, pk=None):
        """Reindex knowledge base embeddings"""
        kb = self.get_object()
        
        # Start reindexing process
        # In production, this would be handled asynchronously
        kb.last_indexed = timezone.now()
        kb.save()
        
        return Response({
            'message': 'Reindexing started',
            'status': 'processing'
        })


class ContentGenerationViewSet(viewsets.ModelViewSet):
    """ViewSet for content generation"""
    
    serializer_class = ContentGenerationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get generations for current user"""
        return ContentGeneration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user when creating generation"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate content using templates and RAG"""
        serializer = ContentGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = ContentGenerationService(request.user)
            generation = service.generate_content(serializer.validated_data)
            
            gen_serializer = ContentGenerationSerializer(
                generation, context={'request': request}
            )
            return Response(gen_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return Response({
                'error': 'Content generation failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate generated content"""
        generation = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if not rating or rating < 1 or rating > 5:
            return Response({
                'error': 'Rating must be between 1 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        generation.user_rating = rating
        generation.user_feedback = feedback
        generation.save()
        
        # Update template statistics if applicable
        if generation.template:
            generation.template.update_stats(rating=rating)
        
        return Response({
            'message': 'Rating saved',
            'rating': rating
        })
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export generated content to document"""
        generation = self.get_object()
        
        if not generation.generated_content:
            return Response({
                'error': 'No content to export'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = generation.create_document()
            doc_serializer = DocumentSerializer(document, context={'request': request})
            
            return Response({
                'message': 'Content exported to document',
                'document': doc_serializer.data
            })
        
        except Exception as e:
            return Response({
                'error': 'Export failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContentWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for content workflows"""
    
    serializer_class = ContentWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get workflows based on user permissions"""
        user = self.request.user
        if user.is_superuser:
            return ContentWorkflow.objects.all()
        
        return ContentWorkflow.objects.filter(
            Q(is_public=True, is_active=True) | Q(creator=user)
        )
    
    def perform_create(self, serializer):
        """Set creator when creating workflow"""
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute workflow"""
        workflow = self.get_object()
        serializer = WorkflowExecutionRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = WorkflowExecutionService(request.user)
            execution = service.execute_workflow(workflow, serializer.validated_data)
            
            exec_serializer = WorkflowExecutionSerializer(
                execution, context={'request': request}
            )
            return Response(exec_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return Response({
                'error': 'Workflow execution failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for workflow executions"""
    
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get executions for current user"""
        return WorkflowExecution.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel workflow execution"""
        execution = self.get_object()
        
        if execution.status not in ['pending', 'processing']:
            return Response({
                'error': 'Cannot cancel completed execution'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        execution.status = 'cancelled'
        execution.error_message = 'Cancelled by user'
        execution.completed_at = timezone.now()
        execution.save()
        
        return Response({
            'message': 'Execution cancelled'
        })


class ContentAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for content analytics"""
    
    serializer_class = ContentAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get analytics data"""
        user = self.request.user
        if user.is_superuser:
            return ContentAnalytics.objects.all()
        
        return ContentAnalytics.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics"""
        user = request.user
        
        # Get user's content statistics
        documents_count = Document.objects.filter(owner=user).count()
        generations_count = ContentGeneration.objects.filter(user=user).count()
        workflows_count = WorkflowExecution.objects.filter(user=user).count()
        
        # Recent activity
        recent_documents = Document.objects.filter(
            owner=user
        ).order_by('-created_at')[:5]
        
        recent_generations = ContentGeneration.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        return Response({
            'summary': {
                'documents': documents_count,
                'generations': generations_count,
                'workflows': workflows_count
            },
            'recent_documents': DocumentSerializer(
                recent_documents, many=True, context={'request': request}
            ).data,
            'recent_generations': ContentGenerationSerializer(
                recent_generations, many=True, context={'request': request}
            ).data
        })
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def blog_list(request):
    """Placeholder blog list endpoint"""
    return Response([])


"""
API views for the Data Persistence system.

Provides REST endpoints for:
- Unified semantic search across all content
- Agent knowledge sharing and discovery
- Spider data querying and routing
- Embedding management and analytics
- Cross-agent collaboration interfaces
"""

import json
import logging
from typing import Dict, List, Any

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse

from .models import (
    UnifiedEmbedding, AgentKnowledge, SpiderData, SpiderDataRoute,
    AgentCollaborationSession, DataPersistenceMetrics
)
from .services import (
    EmbeddingService, AgentKnowledgeService, SpiderDataService,
    UnifiedSearchService
)
from .content_integration import document_persistence, content_generation_integration

logger = logging.getLogger(__name__)


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UnifiedSearchView(APIView):
    """
    Unified semantic search across all content types.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Perform semantic search across all data types.

        Expected payload:
        {
            "query": "search query text",
            "content_types": ["agent_knowledge", "spider_data", "document_chunk"],
            "filters": {"source_system": "agents"},
            "limit": 20
        }
        """
        try:
            data = request.data
            query = data.get('query', '')
            content_types = data.get('content_types', None)
            filters = data.get('filters', {})
            limit = min(data.get('limit', 20), 100)  # Cap at 100 results

            if not query.strip():
                return Response(
                    {'error': 'Query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Use unified search service
            search_service = UnifiedSearchService()
            results = search_service.search_everything(
                query=query,
                search_types=content_types,
                filters=filters,
                limit=limit
            )

            # Add search metadata
            total_results = sum(len(results[t]) for t in results)
            response_data = {
                'query': query,
                'total_results': total_results,
                'content_types_searched': list(results.keys()),
                'results': results,
                'timestamp': timezone.now().isoformat()
            }

            return Response(response_data)

        except Exception as e:
            logger.error(f"Unified search failed: {e}")
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AgentKnowledgeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Agent Knowledge management.
    """
    queryset = AgentKnowledge.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        """Filter knowledge based on access permissions."""
        queryset = super().get_queryset()

        # Filter by agent name if provided
        agent_name = self.request.query_params.get('agent_name')
        if agent_name:
            queryset = queryset.filter(agent_name=agent_name)

        # Filter by knowledge type
        knowledge_type = self.request.query_params.get('knowledge_type')
        if knowledge_type:
            queryset = queryset.filter(knowledge_type=knowledge_type)

        # Filter by domain tags
        domain_tags = self.request.query_params.getlist('domain_tags')
        if domain_tags:
            queryset = queryset.filter(domain_tags__overlap=domain_tags)

        return queryset.order_by('-confidence_score', '-created_at')

    @action(detail=False, methods=['post'])
    def create_knowledge(self, request):
        """
        Create new agent knowledge entry.

        Expected payload:
        {
            "agent_name": "income_builder",
            "knowledge_type": "solution",
            "title": "Effective freelance proposal writing",
            "content": {"steps": [...], "tips": [...]},
            "summary": "Guide for writing winning proposals",
            "context": {"applicable_platforms": ["upwork", "freelancer"]},
            "domain_tags": ["freelancing", "proposals"]
        }
        """
        try:
            data = request.data
            required_fields = ['agent_name', 'knowledge_type', 'title', 'content', 'summary']

            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create knowledge using service
            knowledge_service = AgentKnowledgeService()
            knowledge = knowledge_service.create_knowledge(
                agent_name=data['agent_name'],
                knowledge_type=data['knowledge_type'],
                title=data['title'],
                content=data['content'],
                summary=data['summary'],
                context=data.get('context', {}),
                domain_tags=data.get('domain_tags', []),
                applicable_agents=data.get('applicable_agents', []),
                is_public=data.get('is_public', True),
                confidence_score=data.get('confidence_score', 0.5)
            )

            return Response({
                'id': str(knowledge.id),
                'message': 'Knowledge created successfully',
                'embedding_generated': knowledge.embedding is not None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to create agent knowledge: {e}")
            return Response(
                {'error': 'Failed to create knowledge', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def search_knowledge(self, request):
        """
        Search agent knowledge using semantic search.

        Expected payload:
        {
            "query": "how to write proposals",
            "agent_name": "income_builder",
            "knowledge_types": ["solution", "best_practice"],
            "domain_tags": ["freelancing"],
            "limit": 10
        }
        """
        try:
            data = request.data
            query = data.get('query', '')

            if not query.strip():
                return Response(
                    {'error': 'Query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Search using model method
            knowledge_entries = AgentKnowledge.search_knowledge(
                query=query,
                agent_name=data.get('agent_name'),
                knowledge_types=data.get('knowledge_types'),
                domain_tags=data.get('domain_tags'),
                limit=data.get('limit', 10)
            )

            # Serialize results
            results = []
            for knowledge in knowledge_entries:
                results.append({
                    'id': str(knowledge.id),
                    'title': knowledge.title,
                    'agent_name': knowledge.agent_name,
                    'knowledge_type': knowledge.knowledge_type,
                    'summary': knowledge.summary,
                    'confidence_score': knowledge.confidence_score,
                    'usage_count': knowledge.usage_count,
                    'success_rate': knowledge.success_rate,
                    'domain_tags': knowledge.domain_tags,
                    'created_at': knowledge.created_at.isoformat()
                })

            return Response({
                'query': query,
                'results': results,
                'total_found': len(results)
            })

        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def record_usage(self, request, pk=None):
        """
        Record usage of knowledge by an agent.

        Expected payload:
        {
            "agent_name": "income_builder",
            "success": true,
            "feedback": "Very helpful for proposal writing"
        }
        """
        try:
            knowledge = self.get_object()
            data = request.data

            agent_name = data.get('agent_name')
            if not agent_name:
                return Response(
                    {'error': 'agent_name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = data.get('success', True)
            knowledge.record_usage(agent_name, success)

            return Response({
                'message': 'Usage recorded successfully',
                'new_confidence_score': knowledge.confidence_score,
                'usage_count': knowledge.usage_count
            })

        except Exception as e:
            logger.error(f"Failed to record knowledge usage: {e}")
            return Response(
                {'error': 'Failed to record usage', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SpiderDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Spider Data management.
    """
    queryset = SpiderData.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    def get_queryset(self):
        """Filter spider data based on query parameters."""
        queryset = super().get_queryset()

        # Filter by spider name
        spider_name = self.request.query_params.get('spider_name')
        if spider_name:
            queryset = queryset.filter(spider_name=spider_name)

        # Filter by source platform
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(source_platform=platform)

        # Filter by data type
        data_type = self.request.query_params.get('data_type')
        if data_type:
            queryset = queryset.filter(data_type=data_type)

        # Filter by conversion status
        conversion_status = self.request.query_params.get('conversion_status')
        if conversion_status:
            queryset = queryset.filter(conversion_status=conversion_status)

        # Filter by minimum opportunity score
        min_score = self.request.query_params.get('min_opportunity_score')
        if min_score:
            try:
                queryset = queryset.filter(opportunity_score__gte=float(min_score))
            except ValueError:
                pass

        return queryset.order_by('-opportunity_score', '-discovered_at')

    @action(detail=False, methods=['post'])
    def store_discovery(self, request):
        """
        Store new spider discovery.

        Expected payload:
        {
            "spider_name": "reddit_spider",
            "source_url": "https://reddit.com/r/freelance/...",
            "source_platform": "reddit",
            "title": "Freelance opportunity for content writing",
            "content": "Looking for a content writer...",
            "data_type": "opportunity",
            "structured_data": {...},
            "opportunity_score": 0.8
        }
        """
        try:
            data = request.data
            required_fields = ['spider_name', 'source_url', 'source_platform', 'title', 'content', 'data_type']

            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Store using service
            spider_service = SpiderDataService()
            spider_data = spider_service.store_spider_discovery(
                spider_name=data['spider_name'],
                source_url=data['source_url'],
                source_platform=data['source_platform'],
                title=data['title'],
                content=data['content'],
                data_type=data['data_type'],
                structured_data=data.get('structured_data', {}),
                spider_version=data.get('spider_version', '1.0.0'),
                category=data.get('category', ''),
                tags=data.get('tags', []),
                relevance_score=data.get('relevance_score', 0.0),
                opportunity_score=data.get('opportunity_score', 0.0),
                quality_score=data.get('quality_score', 0.0),
                urgency_score=data.get('urgency_score', 0.0),
                revenue_potential=data.get('revenue_potential'),
                raw_html=data.get('raw_html', '')
            )

            return Response({
                'id': str(spider_data.id),
                'message': 'Discovery stored successfully',
                'routed_to_agents': spider_data.routed_to_agents,
                'embedding_generated': spider_data.embedding is not None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to store spider discovery: {e}")
            return Response(
                {'error': 'Failed to store discovery', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def search_discoveries(self, request):
        """
        Search spider discoveries using semantic search.

        Expected payload:
        {
            "query": "freelance writing opportunities",
            "data_types": ["opportunity"],
            "platforms": ["reddit", "upwork"],
            "min_opportunity_score": 0.5,
            "limit": 20
        }
        """
        try:
            data = request.data
            query = data.get('query', '')

            if not query.strip():
                return Response(
                    {'error': 'Query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Search using service
            spider_service = SpiderDataService()
            spider_data_list = spider_service.search_spider_data(
                query=query,
                data_types=data.get('data_types'),
                platforms=data.get('platforms'),
                min_opportunity_score=data.get('min_opportunity_score', 0.0),
                limit=data.get('limit', 20)
            )

            # Serialize results
            results = []
            for spider_data in spider_data_list:
                results.append({
                    'id': str(spider_data.id),
                    'title': spider_data.title,
                    'spider_name': spider_data.spider_name,
                    'source_platform': spider_data.source_platform,
                    'source_url': spider_data.source_url,
                    'data_type': spider_data.data_type,
                    'opportunity_score': spider_data.opportunity_score,
                    'relevance_score': spider_data.relevance_score,
                    'conversion_status': spider_data.conversion_status,
                    'revenue_generated': float(spider_data.revenue_generated),
                    'is_processed': spider_data.is_processed,
                    'routed_to_agents': spider_data.routed_to_agents,
                    'discovered_at': spider_data.discovered_at.isoformat()
                })

            return Response({
                'query': query,
                'results': results,
                'total_found': len(results)
            })

        except Exception as e:
            logger.error(f"Spider data search failed: {e}")
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_conversion(self, request, pk=None):
        """
        Update conversion status and revenue for spider data.

        Expected payload:
        {
            "status": "converted",
            "revenue": 500.00,
            "agent_name": "income_builder"
        }
        """
        try:
            spider_data = self.get_object()
            data = request.data

            status_value = data.get('status')
            revenue = data.get('revenue')
            agent_name = data.get('agent_name')

            if status_value:
                spider_service = SpiderDataService()
                spider_service.update_conversion_metrics(
                    spider_data_id=spider_data.id,
                    status=status_value,
                    revenue=revenue,
                    agent_name=agent_name
                )

            return Response({
                'message': 'Conversion updated successfully',
                'new_status': spider_data.conversion_status,
                'total_revenue': float(spider_data.revenue_generated)
            })

        except Exception as e:
            logger.error(f"Failed to update conversion: {e}")
            return Response(
                {'error': 'Failed to update conversion', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmbeddingManagementView(APIView):
    """
    API for managing embeddings and semantic search.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Create embedding for arbitrary content.

        Expected payload:
        {
            "content_text": "Text to embed",
            "content_type": "custom_content",
            "content_id": "uuid-string",
            "source_system": "api",
            "metadata": {"key": "value"}
        }
        """
        try:
            data = request.data
            required_fields = ['content_text', 'content_type', 'content_id', 'source_system']

            for field in required_fields:
                if field not in data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create embedding using service
            embedding_service = EmbeddingService()
            embedding = embedding_service.create_embedding(
                content_text=data['content_text'],
                content_type=data['content_type'],
                content_id=data['content_id'],
                source_system=data['source_system'],
                creator_user=request.user,
                metadata=data.get('metadata', {}),
                content_title=data.get('content_title', ''),
                tags=data.get('tags', []),
                category=data.get('category', ''),
                importance_score=data.get('importance_score', 0.5),
                relevance_score=data.get('relevance_score', 0.5),
                confidence_score=data.get('confidence_score', 0.5),
            )

            return Response({
                'id': str(embedding.id),
                'message': 'Embedding created successfully',
                'dimension': embedding.embedding_dimension,
                'cost': float(embedding.generation_cost)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return Response(
                {'error': 'Failed to create embedding', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """Get embedding statistics and analytics."""
        try:
            # Get cache key for stats
            cache_key = 'embedding_stats'
            stats = cache.get(cache_key)

            if not stats:
                # Calculate statistics
                total_embeddings = UnifiedEmbedding.objects.filter(is_active=True).count()

                by_content_type = UnifiedEmbedding.objects.filter(is_active=True).values(
                    'content_type'
                ).annotate(count=Count('id')).order_by('-count')

                by_source_system = UnifiedEmbedding.objects.filter(is_active=True).values(
                    'source_system'
                ).annotate(count=Count('id')).order_by('-count')

                avg_scores = UnifiedEmbedding.objects.filter(is_active=True).aggregate(
                    avg_importance=Avg('importance_score'),
                    avg_relevance=Avg('relevance_score'),
                    avg_confidence=Avg('confidence_score'),
                    total_cost=Sum('generation_cost'),
                    total_access=Sum('access_count')
                )

                stats = {
                    'total_embeddings': total_embeddings,
                    'by_content_type': list(by_content_type),
                    'by_source_system': list(by_source_system),
                    'average_scores': avg_scores,
                    'generated_at': timezone.now().isoformat()
                }

                # Cache for 5 minutes
                cache.set(cache_key, stats, 300)

            return Response(stats)

        except Exception as e:
            logger.error(f"Failed to get embedding stats: {e}")
            return Response(
                {'error': 'Failed to get statistics', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SystemInsightsView(APIView):
    """
    System-wide insights and analytics for the persistence infrastructure.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get comprehensive system insights."""
        try:
            # Get cached insights
            cache_key = 'system_insights'
            insights = cache.get(cache_key)

            if not insights:
                search_service = UnifiedSearchService()
                insights = search_service.get_system_insights()

                # Add additional platform metrics
                insights.update({
                    'collaboration_sessions': AgentCollaborationSession.objects.filter(
                        is_active=True
                    ).count(),
                    'active_spider_routes': SpiderDataRoute.objects.filter(
                        status='pending'
                    ).count(),
                    'recent_discoveries': SpiderData.objects.filter(
                        discovered_at__gte=timezone.now() - timezone.timedelta(hours=24)
                    ).count(),
                    'high_value_opportunities': SpiderData.objects.filter(
                        opportunity_score__gte=0.8,
                        conversion_status__in=['discovered', 'analyzed', 'pursued']
                    ).count(),
                })

                # Cache for 10 minutes
                cache.set(cache_key, insights, 600)

            return Response(insights)

        except Exception as e:
            logger.error(f"Failed to get system insights: {e}")
            return Response(
                {'error': 'Failed to get insights', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Document integration endpoints
class DocumentSearchView(APIView):
    """Document search using unified embedding system."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Search documents using semantic search."""
        try:
            data = request.data
            query = data.get('query', '')

            if not query.strip():
                return Response(
                    {'error': 'Query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            results = document_persistence.search_documents(
                query=query,
                document_types=data.get('document_types'),
                categories=data.get('categories'),
                limit=data.get('limit', 20)
            )

            return Response({
                'query': query,
                'results': results,
                'total_found': len(results)
            })

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContentGenerationSearchView(APIView):
    """Search generated content using unified embedding system."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Search generated content."""
        try:
            data = request.data
            query = data.get('query', '')

            if not query.strip():
                return Response(
                    {'error': 'Query parameter is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            results = content_generation_integration.search_generated_content(
                query=query,
                templates=data.get('templates'),
                limit=data.get('limit', 20)
            )

            return Response({
                'query': query,
                'results': results,
                'total_found': len(results)
            })

        except Exception as e:
            logger.error(f"Generated content search failed: {e}")
            return Response(
                {'error': 'Search failed', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
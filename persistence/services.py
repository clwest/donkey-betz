"""
Data Persistence Services for Unified Donkey Betz Platform

Core services for:
- Embedding generation and caching
- Semantic search across all content types
- Agent knowledge sharing and discovery
- Spider data processing and routing
- Cross-platform data integration
"""

import hashlib
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Avg, Count, Sum

from .models import (
    UnifiedEmbedding, AgentKnowledge, SpiderData, SpiderDataRoute,
    AgentCollaborationSession, DataPersistenceMetrics
)

logger = logging.getLogger(__name__)

# --- add these imports with your others ---
import math
from statistics import fmean

# Optional, but best for accurate token counts
try:
    import tiktoken
    _HAS_TIKTOKEN = True
except Exception:
    _HAS_TIKTOKEN = False


def _get_tokenizer_for_embeddings(model_name: str):
    """
    OpenAI embedding models use cl100k_base.
    If tiktoken isn't available, return None and we’ll fall back to a char heuristic.
    """
    if not _HAS_TIKTOKEN:
        return None
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception as _e:
        logger.warning(
            "services._get_tokenizer_for_embeddings: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None


def _chunk_text_for_embedding(text: str, model_name: str, max_tokens: int = 7500):
    """
    Yield text chunks each <= max_tokens (leaving headroom under 8192).
    Uses tiktoken if present; otherwise ~4 chars ≈ 1 token heuristic.
    """
    tok = _get_tokenizer_for_embeddings(model_name)
    if tok:
        ids = tok.encode(text)
        for i in range(0, len(ids), max_tokens):
            yield tok.decode(ids[i:i + max_tokens])
    else:
        # Heuristic fallback: ~4 chars per token
        approx_chars_per_token = 4
        max_chars = max_tokens * approx_chars_per_token
        for i in range(0, len(text), max_chars):
            yield text[i:i + max_chars]


def _l2_normalize(vec):
    s = math.fsum(x * x for x in vec)
    if s <= 0:
        return vec
    norm = math.sqrt(s)
    return [x / norm for x in vec]


class EmbeddingService:
    """
    Service for generating, storing, and searching embeddings across all content types.

    Provides unified embedding capabilities with:
    - Multiple embedding model support
    - Intelligent caching to avoid redundant API calls
    - Batch processing for efficiency
    - Automatic deduplication
    """

    def __init__(self):
        self.default_model = 'text-embedding-3-small'
        self.cache_timeout = 3600 * 24  # 24 hours
        self.max_cache_size = 10000

    def generate_embedding_vector(self, text: str, model: str = None) -> List[float]:
        """
        Generate embedding vector for text using specified model.

        Args:
            text: Text content to embed
            model: Embedding model to use (defaults to default_model)

        Returns:
            List of floats representing the embedding vector

        Raises:
            Exception: If embedding generation fails
        """
        model = model or self.default_model

        # Create cache key
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        cache_key = f"embedding:{model}:{text_hash[:16]}"

        # Check cache first
        cached_embedding = cache.get(cache_key)
        if cached_embedding:
            logger.debug(f"Retrieved cached embedding for text hash {text_hash[:8]}")
            return cached_embedding

        # Generate new embedding
        start_time = time.time()

        try:
            if model.startswith('text-embedding'):
                # OpenAI embedding
                embedding_vector = self._generate_openai_embedding(text, model)
            elif model == 'sentence-transformer':
                # Sentence transformer embedding
                embedding_vector = self._generate_sentence_transformer_embedding(text)
            else:
                raise ValueError(f"Unsupported embedding model: {model}")

            generation_time = int((time.time() - start_time) * 1000)

            # Cache the result
            cache.set(cache_key, embedding_vector, self.cache_timeout)

            # Record metrics
            DataPersistenceMetrics.record_metric(
                name='embedding_generation_time_ms',
                value=generation_time,
                metric_type='timer',
                subsystem='embeddings',
                metadata={'model': model, 'text_length': len(text)}
            )

            logger.debug(f"Generated embedding using {model} in {generation_time}ms")
            return embedding_vector

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Record error metric
            DataPersistenceMetrics.record_metric(
                name='embedding_generation_errors',
                value=1,
                metric_type='counter',
                subsystem='embeddings',
                metadata={'model': model, 'error': str(e)}
            )
            raise
    
    def _generate_openai_embedding(self, text: str, model: str) -> List[float]:
        """
        Chunk long text to <= 7,500 tokens, embed each chunk, average, then L2-normalize.
        This avoids 400 errors for inputs over the model's context window.
        """
        try:
            import openai
            openai.api_key = settings.AI_PROVIDERS['OPENAI_API_KEY']

            chunks = list(_chunk_text_for_embedding(text, model_name=model, max_tokens=7500))
            if not chunks:
                chunks = [""]

            vectors: List[List[float]] = []
            for chunk in chunks:
                resp = openai.embeddings.create(
                    model=model,
                    input=chunk,
                    encoding_format="float",
                )
                vectors.append(resp.data[0].embedding)

            # Average across chunks (dimension-stable) then normalize for cosine distance
            dim = len(vectors[0])
            avg = [fmean(v[i] for v in vectors) for i in range(dim)]
            return _l2_normalize(avg)

        except ImportError:
            raise Exception("OpenAI package not installed")
        except Exception as e:
            raise Exception(f"OpenAI embedding generation failed: {e}")

    def _generate_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using Sentence Transformers"""
        try:
            from sentence_transformers import SentenceTransformer

            # Use cached model or load new one
            model_cache_key = "sentence_transformer_model"
            model = cache.get(model_cache_key)

            if not model:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                cache.set(model_cache_key, model, 3600)  # Cache for 1 hour

            embedding = model.encode(text)
            return embedding.tolist()

        except ImportError:
            raise Exception("Sentence Transformers package not installed")
        except Exception as e:
            raise Exception(f"Sentence Transformer embedding generation failed: {e}")

    def create_embedding(self, content_text: str, content_type: str, content_id: Any,
                        source_system: str, creator_agent: str = None,
                        creator_user=None, model: str = None,
                        metadata: Dict = None, **kwargs) -> UnifiedEmbedding:
        """
        Create and store a unified embedding with full metadata.

        Args:
            content_text: Text content to embed
            content_type: Type of content (agent_knowledge, spider_data, etc.)
            content_id: UUID of the content object
            source_system: System that created this content
            creator_agent: Agent that created this (optional)
            creator_user: User that created this (optional)
            model: Embedding model to use
            metadata: Additional metadata
            **kwargs: Additional fields for UnifiedEmbedding

        Returns:
            UnifiedEmbedding instance
        """
        model = model or self.default_model

        # Check for existing embedding to avoid duplicates
        content_hash = hashlib.sha256(content_text.encode('utf-8')).hexdigest()
        existing_embedding = UnifiedEmbedding.objects.filter(
            content_type=content_type,
            content_id=content_id,
            content_hash=content_hash
        ).first()

        if existing_embedding:
            logger.debug(f"Reusing existing embedding for {content_type}:{content_id}")
            return existing_embedding

        # Generate embedding vector
        try:
            embedding_vector = self.generate_embedding_vector(content_text, model)

            # Calculate cost (approximate)
            cost = self._calculate_embedding_cost(content_text, model)

            # Create embedding record
            with transaction.atomic():
                embedding = UnifiedEmbedding.objects.create(
                    content_type=content_type,
                    content_id=content_id,
                    content_text=content_text,
                    content_title=kwargs.get('content_title', ''),
                    content_metadata=metadata or {},
                    embedding_model=model,
                    embedding=embedding_vector,
                    embedding_dimension=len(embedding_vector),
                    source_system=source_system,
                    creator_agent=creator_agent,
                    creator_user=creator_user,
                    importance_score=kwargs.get('importance_score', 0.5),
                    relevance_score=kwargs.get('relevance_score', 0.5),
                    confidence_score=kwargs.get('confidence_score', 0.5),
                    generation_cost=cost,
                    content_hash=content_hash,
                    tags=kwargs.get('tags', []),
                    category=kwargs.get('category', ''),
                    content_timestamp=kwargs.get('content_timestamp'),
                    expires_at=kwargs.get('expires_at'),
                )

                # Record creation metric
                DataPersistenceMetrics.record_metric(
                    name='embeddings_created',
                    value=1,
                    metric_type='counter',
                    subsystem='embeddings',
                    metadata={
                        'content_type': content_type,
                        'source_system': source_system,
                        'model': model
                    }
                )

                logger.info(f"Created embedding for {content_type}:{content_id}")
                return embedding

        except Exception as e:
            logger.error(f"Failed to create embedding for {content_type}:{content_id}: {e}")
            raise

    def _calculate_embedding_cost(self, text: str, model: str) -> Decimal:
        """Calculate approximate cost for generating embedding"""
        token_count = len(text.split()) * 1.3  # Rough token estimation

        # Cost per 1K tokens (approximate OpenAI pricing)
        costs = {
            'text-embedding-3-small': 0.00002,
            'text-embedding-3-large': 0.00013,
            'text-embedding-ada-002': 0.0001,
        }

        cost_per_1k = costs.get(model, 0.0001)
        total_cost = (token_count / 1000) * cost_per_1k

        return Decimal(str(round(total_cost, 6)))

    def batch_create_embeddings(self, content_items: List[Dict]) -> List[UnifiedEmbedding]:
        """
        Create multiple embeddings in batch for efficiency.

        Args:
            content_items: List of dicts with embedding parameters

        Returns:
            List of created UnifiedEmbedding instances
        """
        embeddings = []

        for item in content_items:
            try:
                embedding = self.create_embedding(**item)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to create embedding in batch: {e}")
                continue

        logger.info(f"Created {len(embeddings)} embeddings in batch")
        return embeddings

    def search_all_content(self, query: str, content_types: List[str] = None,
                          limit: int = 20, filters: Dict = None) -> List[Dict]:
        """
        Perform unified semantic search across all content types.

        Args:
            query: Search query text
            content_types: Filter by specific content types
            limit: Maximum number of results
            filters: Additional filters

        Returns:
            List of search results with unified format
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding_vector(query)

            # Search embeddings
            embeddings = UnifiedEmbedding.search_similar(
                query_embedding=query_embedding,
                content_types=content_types,
                limit=limit,
                filters=filters or {}
            )

            results = []
            for embedding in embeddings:
                # Get source object
                source_object = self._get_source_object(embedding)

                result = {
                    'id': str(embedding.content_id),
                    'type': embedding.content_type,
                    'title': embedding.content_title or embedding.content_text[:100],
                    'content': embedding.content_text,
                    'source_system': embedding.source_system,
                    'creator': embedding.creator_agent or (
                        embedding.creator_user.username if embedding.creator_user else 'System'
                    ),
                    'created_at': embedding.created_at.isoformat(),
                    'importance_score': embedding.importance_score,
                    'relevance_score': embedding.relevance_score,
                    'tags': embedding.tags,
                    'category': embedding.category,
                    'metadata': embedding.content_metadata,
                    'source_object': source_object,
                }
                results.append(result)

                # Increment access count
                embedding.increment_access()

            # Record search metric
            DataPersistenceMetrics.record_metric(
                name='unified_searches',
                value=1,
                metric_type='counter',
                subsystem='search',
                metadata={
                    'query_length': len(query),
                    'results_count': len(results),
                    'content_types': content_types or 'all'
                }
            )

            logger.info(f"Unified search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Unified search failed: {e}")
            return []

    def _get_source_object(self, embedding: UnifiedEmbedding) -> Optional[Dict]:
        """Get the source object that this embedding represents"""
        try:
            if embedding.content_type == 'agent_knowledge':
                knowledge = AgentKnowledge.objects.get(id=embedding.content_id)
                return {
                    'agent_name': knowledge.agent_name,
                    'knowledge_type': knowledge.knowledge_type,
                    'confidence_score': knowledge.confidence_score,
                    'usage_count': knowledge.usage_count,
                }
            elif embedding.content_type == 'spider_data':
                spider_data = SpiderData.objects.get(id=embedding.content_id)
                return {
                    'spider_name': spider_data.spider_name,
                    'source_platform': spider_data.source_platform,
                    'data_type': spider_data.data_type,
                    'opportunity_score': spider_data.opportunity_score,
                    'conversion_status': spider_data.conversion_status,
                }
            # Add more content types as needed

        except Exception as e:
            logger.debug(f"Could not retrieve source object for embedding {embedding.id}: {e}")

        return None


class AgentKnowledgeService:
    """
    Service for managing shared agent knowledge and collaboration.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def create_knowledge(self, agent_name: str, knowledge_type: str, title: str,
                        content: Dict, summary: str, context: Dict = None,
                        domain_tags: List[str] = None, **kwargs) -> AgentKnowledge:
        """
        Create new agent knowledge entry with automatic embedding generation.

        Args:
            agent_name: Name of the agent creating the knowledge
            knowledge_type: Type of knowledge (fact, skill, pattern, etc.)
            title: Clear title for the knowledge
            content: Structured knowledge content
            summary: Human-readable summary
            context: Context for applicability
            domain_tags: Domain tags for categorization
            **kwargs: Additional fields

        Returns:
            AgentKnowledge instance
        """
        try:
            with transaction.atomic():
                knowledge = AgentKnowledge.objects.create(
                    agent_name=agent_name,
                    agent_id=kwargs.get('agent_id'),
                    knowledge_type=knowledge_type,
                    title=title,
                    content=content,
                    summary=summary,
                    context=context or {},
                    domain_tags=domain_tags or [],
                    applicable_agents=kwargs.get('applicable_agents', []),
                    is_public=kwargs.get('is_public', True),
                    access_level=kwargs.get('access_level', 'read'),
                    confidence_score=kwargs.get('confidence_score', 0.5),
                )

                # Embedding will be generated automatically in post_save

                logger.info(f"Created knowledge '{title}' for agent {agent_name}")
                return knowledge

        except Exception as e:
            logger.error(f"Failed to create knowledge for {agent_name}: {e}")
            raise

    def share_knowledge(self, knowledge_id: Any, target_agents: List[str],
                       access_level: str = 'read') -> bool:
        """
        Share knowledge with specific agents.

        Args:
            knowledge_id: ID of the knowledge to share
            target_agents: List of agent names to share with
            access_level: Access level for shared knowledge

        Returns:
            True if successful, False otherwise
        """
        try:
            knowledge = AgentKnowledge.objects.get(id=knowledge_id)

            # Add target agents to shared_with list
            for agent in target_agents:
                if agent not in knowledge.shared_with:
                    knowledge.shared_with.append(agent)

            knowledge.access_level = access_level
            knowledge.save()

            logger.info(f"Shared knowledge {knowledge_id} with {len(target_agents)} agents")
            return True

        except AgentKnowledge.DoesNotExist:
            logger.error(f"Knowledge {knowledge_id} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to share knowledge {knowledge_id}: {e}")
            return False

    def discover_relevant_knowledge(self, query: str, agent_name: str,
                                  domain_tags: List[str] = None,
                                  knowledge_types: List[str] = None,
                                  limit: int = 10) -> List[AgentKnowledge]:
        """
        Discover relevant knowledge for an agent using semantic search.

        Args:
            query: Search query describing needed knowledge
            agent_name: Name of the requesting agent
            domain_tags: Filter by domain tags
            knowledge_types: Filter by knowledge types
            limit: Maximum number of results

        Returns:
            List of relevant AgentKnowledge instances
        """
        try:
            # Use the search method from AgentKnowledge model
            knowledge_entries = AgentKnowledge.search_knowledge(
                query=query,
                agent_name=None,  # Search all agents' knowledge
                knowledge_types=knowledge_types,
                domain_tags=domain_tags,
                limit=limit
            )

            # Filter by accessibility
            accessible_knowledge = []
            for knowledge in knowledge_entries:
                if self._can_access_knowledge(knowledge, agent_name):
                    accessible_knowledge.append(knowledge)

            logger.info(f"Discovered {len(accessible_knowledge)} relevant knowledge entries for {agent_name}")
            return accessible_knowledge

        except Exception as e:
            logger.error(f"Failed to discover knowledge for {agent_name}: {e}")
            return []

    def _can_access_knowledge(self, knowledge: AgentKnowledge, agent_name: str) -> bool:
        """Check if an agent can access specific knowledge"""
        # Public knowledge is accessible to all
        if knowledge.is_public and knowledge.is_active:
            return True

        # Check if agent is in shared_with list
        if agent_name in knowledge.shared_with:
            return True

        # Check if agent is in applicable_agents (empty means all agents)
        if not knowledge.applicable_agents or agent_name in knowledge.applicable_agents:
            return True

        return False

    def record_knowledge_usage(self, knowledge_id: Any, agent_name: str,
                             success: bool = True, feedback: str = None):
        """
        Record usage of knowledge by an agent.

        Args:
            knowledge_id: ID of the knowledge used
            agent_name: Name of the agent using the knowledge
            success: Whether the usage was successful
            feedback: Optional feedback about the usage
        """
        try:
            knowledge = AgentKnowledge.objects.get(id=knowledge_id)
            knowledge.record_usage(agent_name, success)

            # Record metric
            DataPersistenceMetrics.record_metric(
                name='knowledge_usage',
                value=1,
                metric_type='counter',
                subsystem='agent_knowledge',
                metadata={
                    'agent_name': agent_name,
                    'knowledge_type': knowledge.knowledge_type,
                    'success': success
                }
            )

            logger.info(f"Recorded knowledge usage: {agent_name} used {knowledge_id} (success: {success})")

        except AgentKnowledge.DoesNotExist:
            logger.error(f"Knowledge {knowledge_id} not found for usage recording")
        except Exception as e:
            logger.error(f"Failed to record knowledge usage: {e}")


class SpiderDataService:
    """
    Service for managing spider data persistence and routing.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def store_spider_discovery(self, spider_name: str, source_url: str,
                             source_platform: str, title: str, content: str,
                             data_type: str, structured_data: Dict = None,
                             **kwargs) -> SpiderData:
        """
        Store data discovered by a spider with automatic processing.

        Args:
            spider_name: Name of the spider that made the discovery
            source_url: URL where data was found
            source_platform: Platform (reddit, upwork, etc.)
            title: Title of the discovered content
            content: Raw content text
            data_type: Type of data discovered
            structured_data: Structured data extracted
            **kwargs: Additional fields

        Returns:
            SpiderData instance
        """
        try:
            # Check for duplicate content
            similar_data = SpiderData.find_similar(content)
            if similar_data.exists():
                logger.info(f"Similar content found, linking to existing data")
                existing_data = similar_data.first()
                existing_data.similar_discoveries.add(*similar_data[1:])
                return existing_data

            with transaction.atomic():
                spider_data = SpiderData.objects.create(
                    spider_name=spider_name,
                    spider_version=kwargs.get('spider_version', '1.0.0'),
                    spider_execution_id=kwargs.get('spider_execution_id'),
                    source_url=source_url,
                    source_platform=source_platform,
                    source_metadata=kwargs.get('source_metadata', {}),
                    title=title,
                    content=content,
                    structured_data=structured_data or {},
                    raw_html=kwargs.get('raw_html', ''),
                    data_type=data_type,
                    category=kwargs.get('category', ''),
                    tags=kwargs.get('tags', []),
                    relevance_score=kwargs.get('relevance_score', 0.0),
                    opportunity_score=kwargs.get('opportunity_score', 0.0),
                    quality_score=kwargs.get('quality_score', 0.0),
                    urgency_score=kwargs.get('urgency_score', 0.0),
                    revenue_potential=kwargs.get('revenue_potential'),
                    expires_at=kwargs.get('expires_at'),
                )

                # Embedding will be generated automatically in post_save

                # Route to relevant agents if opportunity score is high
                if spider_data.opportunity_score > 0.7:
                    self.route_high_value_data(spider_data)

                logger.info(f"Stored spider discovery: {title} from {source_platform}")
                return spider_data

        except Exception as e:
            logger.error(f"Failed to store spider discovery: {e}")
            raise

    def route_high_value_data(self, spider_data: SpiderData):
        """
        Automatically route high-value spider data to appropriate agents.

        Args:
            spider_data: SpiderData instance to route
        """
        try:
            # Define routing rules based on data type and platform
            routing_rules = {
                'opportunity': ['income_builder', 'business_development'],
                'job_posting': ['freelance_hunter', 'opportunity_analyzer'],
                'market_data': ['market_analyst', 'trend_predictor'],
                'competitor_info': ['competitive_intelligence', 'market_analyst'],
                'content_idea': ['content_creator', 'social_media_manager'],
            }

            target_agents = routing_rules.get(spider_data.data_type, ['general_processor'])

            for agent_name in target_agents:
                priority = 'high' if spider_data.opportunity_score > 0.8 else 'normal'
                spider_data.route_to_agent(agent_name, priority)

            logger.info(f"Routed spider data {spider_data.id} to {len(target_agents)} agents")

        except Exception as e:
            logger.error(f"Failed to route spider data {spider_data.id}: {e}")

    def search_spider_data(self, query: str, data_types: List[str] = None,
                          platforms: List[str] = None, min_opportunity_score: float = 0.0,
                          limit: int = 20) -> List[SpiderData]:
        """
        Search spider data using semantic search and filters.

        Args:
            query: Search query
            data_types: Filter by data types
            platforms: Filter by source platforms
            min_opportunity_score: Minimum opportunity score
            limit: Maximum number of results

        Returns:
            List of relevant SpiderData instances
        """
        try:
            # Build base filters
            filters = {'is_active': True}
            if data_types:
                filters['data_type__in'] = data_types
            if platforms:
                filters['source_platform__in'] = platforms
            if min_opportunity_score > 0:
                filters['opportunity_score__gte'] = min_opportunity_score

            # Use embedding service for semantic search
            results = self.embedding_service.search_all_content(
                query=query,
                content_types=['spider_data'],
                limit=limit,
                filters=filters
            )

            # Convert to SpiderData objects
            spider_data_ids = [result['id'] for result in results]
            spider_data_objects = SpiderData.objects.filter(id__in=spider_data_ids)

            # Preserve order from search results
            spider_data_dict = {str(obj.id): obj for obj in spider_data_objects}
            ordered_results = [spider_data_dict[obj_id] for obj_id in spider_data_ids
                             if obj_id in spider_data_dict]

            logger.info(f"Spider data search returned {len(ordered_results)} results")
            return ordered_results

        except Exception as e:
            logger.error(f"Spider data search failed: {e}")
            return []

    def update_conversion_metrics(self, spider_data_id: Any, status: str,
                                revenue: Decimal = None, agent_name: str = None):
        """
        Update conversion status and revenue metrics for spider data.

        Args:
            spider_data_id: ID of the spider data
            status: New conversion status
            revenue: Revenue generated (if any)
            agent_name: Agent responsible for conversion
        """
        try:
            spider_data = SpiderData.objects.get(id=spider_data_id)
            spider_data.update_conversion_status(status, revenue)

            # Record conversion metric
            DataPersistenceMetrics.record_metric(
                name='spider_data_conversions',
                value=1,
                metric_type='counter',
                subsystem='spider_data',
                metadata={
                    'status': status,
                    'platform': spider_data.source_platform,
                    'data_type': spider_data.data_type,
                    'agent_name': agent_name,
                    'revenue': float(revenue) if revenue else 0.0
                }
            )

            logger.info(f"Updated conversion status for spider data {spider_data_id}: {status}")

        except SpiderData.DoesNotExist:
            logger.error(f"Spider data {spider_data_id} not found")
        except Exception as e:
            logger.error(f"Failed to update conversion metrics: {e}")


class UnifiedSearchService:
    """
    Unified search service across all data types and systems.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.agent_service = AgentKnowledgeService()
        self.spider_service = SpiderDataService()

    def search_everything(self, query: str, search_types: List[str] = None,
                         filters: Dict = None, limit: int = 50) -> Dict[str, List]:
        """
        Perform comprehensive search across all data types.

        Args:
            query: Search query
            search_types: Types to search (agent_knowledge, spider_data, documents, etc.)
            filters: Additional filters
            limit: Maximum results per type

        Returns:
            Dictionary with results grouped by type
        """
        search_types = search_types or ['agent_knowledge', 'spider_data', 'document_chunk']
        results = {}

        try:
            # Perform unified search
            all_results = self.embedding_service.search_all_content(
                query=query,
                content_types=search_types,
                limit=limit * len(search_types),
                filters=filters
            )

            # Group results by type
            for search_type in search_types:
                type_results = [r for r in all_results if r['type'] == search_type]
                results[search_type] = type_results[:limit]

            # Record search metrics
            total_results = sum(len(results[t]) for t in results)
            DataPersistenceMetrics.record_metric(
                name='unified_searches',
                value=1,
                metric_type='counter',
                subsystem='search',
                metadata={
                    'query_length': len(query),
                    'search_types': search_types,
                    'total_results': total_results
                }
            )

            logger.info(f"Unified search returned {total_results} results across {len(search_types)} types")
            return results

        except Exception as e:
            logger.error(f"Unified search failed: {e}")
            return {search_type: [] for search_type in search_types}

    def get_system_insights(self) -> Dict[str, Any]:
        """
        Get insights about the entire data persistence system.

        Returns:
            Dictionary with system insights and metrics
        """
        try:
            insights = {}

            # Embedding statistics
            total_embeddings = UnifiedEmbedding.objects.filter(is_active=True).count()
            embedding_by_type = UnifiedEmbedding.objects.filter(is_active=True).values(
                'content_type'
            ).annotate(count=Count('id'))

            insights['embeddings'] = {
                'total': total_embeddings,
                'by_type': {item['content_type']: item['count'] for item in embedding_by_type}
            }

            # Agent knowledge statistics
            knowledge_stats = AgentKnowledge.objects.filter(is_active=True).aggregate(
                total=Count('id'),
                avg_confidence=Avg('confidence_score'),
                total_usage=Sum('usage_count')
            )
            insights['agent_knowledge'] = knowledge_stats

            # Spider data statistics
            spider_stats = SpiderData.objects.filter(is_active=True).aggregate(
                total=Count('id'),
                total_revenue=Sum('revenue_generated'),
                avg_opportunity_score=Avg('opportunity_score'),
                processed_count=Count('id', filter=Q(is_processed=True))
            )
            insights['spider_data'] = spider_stats

            # Recent metrics
            recent_metrics = DataPersistenceMetrics.objects.filter(
                timestamp__gte=timezone.now() - timedelta(hours=24)
            ).values('subsystem').annotate(
                count=Count('id')
            )
            insights['recent_activity'] = {
                item['subsystem']: item['count'] for item in recent_metrics
            }

            logger.info("Generated system insights")
            return insights

        except Exception as e:
            logger.error(f"Failed to generate system insights: {e}")
            return {}
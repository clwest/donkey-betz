"""
Learning Embeddings Generator
Creates vector embeddings for learned content to enable semantic search
"""

import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# OpenAI for embeddings
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

# Import models
try:
    from .models import (
        AgentLearningEvent,
        LearningDocument,
        LearningEmbedding,
        AgentKnowledgeBase
    )
except ImportError:
    AgentLearningEvent = None
    LearningDocument = None
    LearningEmbedding = None
    AgentKnowledgeBase = None

# Import existing embeddings infrastructure
try:
    from self_awareness.embeddings import SemanticCodeSearchEngine
except ImportError:
    SemanticCodeSearchEngine = None

import os
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class LearningEmbeddingGenerator:
    """Generates embeddings for learning content"""

    def __init__(self):
        self.client = None
        self.embedding_model = "text-embedding-3-small"
        self.vector_dimensions = 1536
        self.batch_size = 50
        self.rate_limit_delay = 0.1  # Delay between API calls

        # Initialize OpenAI client
        self._initialize_client()

        # Stats tracking
        self.stats = {
            'embeddings_generated': 0,
            'total_tokens_processed': 0,
            'api_calls_made': 0,
            'processing_time': 0.0,
            'errors_encountered': 0
        }

    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and OpenAI:
                self.client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized for embeddings")
            else:
                logger.warning("OpenAI API key not found or OpenAI not installed")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    async def generate_embedding_for_learning_event(self, event: 'AgentLearningEvent') -> Optional[Dict]:
        """Generate embedding for a single learning event"""
        if not self.client or not LearningEmbedding:
            return None

        try:
            # Prepare content for embedding
            content_parts = [
                f"Agent: {event.agent_name} ({event.agent_specialization})",
                f"Signal Type: {event.signal_type}",
                f"Source: {event.source_api}",
                f"Learned Insights: {json.dumps(event.learned_insights)}",
            ]

            # Add processed content if available
            if event.processed_content:
                content_parts.append(f"Content: {json.dumps(event.processed_content)}")

            content_text = "\n".join(content_parts)

            # Generate content hash
            content_hash = hashlib.sha256(content_text.encode()).hexdigest()

            # Check if embedding already exists
            existing_embedding = LearningEmbedding.objects.filter(
                content_hash=content_hash,
                embedding_model=self.embedding_model
            ).first()

            if existing_embedding:
                logger.debug(f"Embedding already exists for event {event.event_id}")
                return {
                    'embedding_id': str(existing_embedding.embedding_id),
                    'status': 'existing'
                }

            # Generate embedding
            start_time = datetime.now()

            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=content_text
            )

            embedding_vector = response.data[0].embedding
            tokens_used = response.usage.total_tokens

            # Create embedding record
            learning_embedding = LearningEmbedding.objects.create(
                learning_event=event,
                content_text=content_text,
                content_hash=content_hash,
                content_type='learning_event',
                embedding_vector=embedding_vector,
                embedding_model=self.embedding_model,
                vector_dimensions=len(embedding_vector),
                agent_id=event.agent_id,
                agent_specialization=event.agent_specialization,
                token_count=tokens_used,
                quality_score=event.quality_score
            )

            # Update stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self.stats['embeddings_generated'] += 1
            self.stats['total_tokens_processed'] += tokens_used
            self.stats['api_calls_made'] += 1
            self.stats['processing_time'] += processing_time

            logger.debug(f"Generated embedding for event {event.event_id}")

            return {
                'embedding_id': str(learning_embedding.embedding_id),
                'status': 'created',
                'tokens_used': tokens_used,
                'processing_time': processing_time
            }

        except Exception as e:
            logger.error(f"Error generating embedding for event {event.event_id}: {e}")
            self.stats['errors_encountered'] += 1
            return None

    async def generate_embedding_for_document(self, document: 'LearningDocument') -> Optional[Dict]:
        """Generate embedding for a learning document"""
        if not self.client or not LearningEmbedding:
            return None

        try:
            # Prepare document content for embedding
            content_parts = [
                f"Title: {document.title}",
                f"Type: {document.document_type}",
                f"Agent: {document.agent_name}",
                f"Summary: {document.summary}",
                f"Content: {document.content[:2000]}"  # Limit content length
            ]

            content_text = "\n".join(content_parts)
            content_hash = hashlib.sha256(content_text.encode()).hexdigest()

            # Check for existing embedding
            existing_embedding = LearningEmbedding.objects.filter(
                document=document,
                content_hash=content_hash,
                embedding_model=self.embedding_model
            ).first()

            if existing_embedding:
                return {
                    'embedding_id': str(existing_embedding.embedding_id),
                    'status': 'existing'
                }

            # Generate embedding
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=content_text
            )

            embedding_vector = response.data[0].embedding
            tokens_used = response.usage.total_tokens

            # Create embedding record
            learning_embedding = LearningEmbedding.objects.create(
                document=document,
                content_text=content_text,
                content_hash=content_hash,
                content_type='document',
                embedding_vector=embedding_vector,
                embedding_model=self.embedding_model,
                vector_dimensions=len(embedding_vector),
                agent_id=document.agent_id,
                agent_specialization=document.agent_name,  # Use agent_name as fallback
                token_count=tokens_used,
                quality_score=document.confidence_level
            )

            # Update stats
            self.stats['embeddings_generated'] += 1
            self.stats['total_tokens_processed'] += tokens_used
            self.stats['api_calls_made'] += 1

            logger.debug(f"Generated embedding for document {document.document_id}")

            return {
                'embedding_id': str(learning_embedding.embedding_id),
                'status': 'created',
                'tokens_used': tokens_used
            }

        except Exception as e:
            logger.error(f"Error generating embedding for document {document.document_id}: {e}")
            self.stats['errors_encountered'] += 1
            return None

    async def process_recent_learning_events(self, hours_back: int = 24) -> Dict[str, Any]:
        """Process embeddings for recent learning events"""
        if not AgentLearningEvent:
            return {'error': 'Models not available'}

        try:
            # Get recent events without embeddings
            cutoff_time = datetime.now(timezone.utc) - timezone.timedelta(hours=hours_back)

            events_without_embeddings = AgentLearningEvent.objects.filter(
                timestamp__gte=cutoff_time,
                embedding__isnull=True  # Events without embeddings
            ).order_by('-timestamp')[:self.batch_size]

            if not events_without_embeddings:
                logger.info("No recent learning events need embeddings")
                return {'processed': 0, 'message': 'No events to process'}

            # Process events in batch
            results = []
            for event in events_without_embeddings:
                result = await self.generate_embedding_for_learning_event(event)
                if result:
                    results.append(result)

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

            successful = len([r for r in results if r and r['status'] == 'created'])

            logger.info(f"Processed {len(results)} events, {successful} new embeddings created")

            return {
                'processed': len(results),
                'created': successful,
                'existing': len(results) - successful,
                'events_processed': [r for r in results if r]
            }

        except Exception as e:
            logger.error(f"Error processing recent learning events: {e}")
            return {'error': str(e)}

    async def process_recent_documents(self, hours_back: int = 24) -> Dict[str, Any]:
        """Process embeddings for recent documents"""
        if not LearningDocument:
            return {'error': 'Models not available'}

        try:
            cutoff_time = datetime.now(timezone.utc) - timezone.timedelta(hours=hours_back)

            # Get recent documents without embeddings
            documents_without_embeddings = LearningDocument.objects.filter(
                created_at__gte=cutoff_time,
                embeddings__isnull=True
            ).order_by('-created_at')[:self.batch_size]

            if not documents_without_embeddings:
                return {'processed': 0, 'message': 'No documents to process'}

            # Process documents
            results = []
            for document in documents_without_embeddings:
                result = await self.generate_embedding_for_document(document)
                if result:
                    results.append(result)

                await asyncio.sleep(self.rate_limit_delay)

            successful = len([r for r in results if r and r['status'] == 'created'])

            logger.info(f"Processed {len(results)} documents, {successful} new embeddings created")

            return {
                'processed': len(results),
                'created': successful,
                'existing': len(results) - successful
            }

        except Exception as e:
            logger.error(f"Error processing recent documents: {e}")
            return {'error': str(e)}

    async def semantic_search_learning_content(self, query: str, agent_id: str = None, limit: int = 10) -> List[Dict]:
        """Search learning content using semantic similarity"""
        if not self.client or not LearningEmbedding:
            return []

        try:
            # Generate query embedding
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=query
            )

            query_vector = response.data[0].embedding

            # Get embeddings to search through
            embeddings_query = LearningEmbedding.objects.all()

            if agent_id:
                embeddings_query = embeddings_query.filter(agent_id=agent_id)

            embeddings = embeddings_query.order_by('-created_at')[:200]  # Limit search space

            # Calculate similarity scores
            similarities = []
            for embedding in embeddings:
                # Calculate cosine similarity
                dot_product = sum(a * b for a, b in zip(query_vector, embedding.embedding_vector))
                norm_query = sum(a * a for a in query_vector) ** 0.5
                norm_embedding = sum(b * b for b in embedding.embedding_vector) ** 0.5

                similarity = dot_product / (norm_query * norm_embedding) if norm_query * norm_embedding > 0 else 0

                similarities.append({
                    'embedding': embedding,
                    'similarity': similarity
                })

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_results = similarities[:limit]

            results = []
            for item in top_results:
                embedding = item['embedding']
                result = {
                    'similarity_score': item['similarity'],
                    'agent_id': embedding.agent_id,
                    'content_type': embedding.content_type,
                    'content_preview': embedding.content_text[:200] + "..." if len(embedding.content_text) > 200 else embedding.content_text,
                    'created_at': embedding.created_at.isoformat(),
                    'quality_score': embedding.quality_score
                }

                if embedding.learning_event:
                    result['learning_event_id'] = str(embedding.learning_event.event_id)
                    result['signal_type'] = embedding.learning_event.signal_type

                if embedding.document:
                    result['document_id'] = str(embedding.document.document_id)
                    result['document_title'] = embedding.document.title

                results.append(result)

            logger.info(f"Semantic search returned {len(results)} results for query: {query[:50]}...")

            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    async def build_agent_knowledge_graph(self, agent_id: str) -> Dict[str, Any]:
        """Build a knowledge graph for an agent based on embeddings"""
        if not LearningEmbedding:
            return {}

        try:
            # Get all embeddings for the agent
            agent_embeddings = LearningEmbedding.objects.filter(
                agent_id=agent_id
            ).order_by('-created_at')[:100]

            if not agent_embeddings:
                return {'message': 'No embeddings found for agent'}

            # Group by content type and signal type
            knowledge_graph = {
                'agent_id': agent_id,
                'total_embeddings': len(agent_embeddings),
                'content_types': {},
                'signal_types': {},
                'knowledge_clusters': []
            }

            # Analyze content types
            content_type_counts = {}
            signal_type_counts = {}

            for embedding in agent_embeddings:
                # Content type analysis
                content_type = embedding.content_type
                if content_type not in content_type_counts:
                    content_type_counts[content_type] = 0
                content_type_counts[content_type] += 1

                # Signal type analysis (for learning events)
                if embedding.learning_event:
                    signal_type = embedding.learning_event.signal_type
                    if signal_type not in signal_type_counts:
                        signal_type_counts[signal_type] = 0
                    signal_type_counts[signal_type] += 1

            knowledge_graph['content_types'] = content_type_counts
            knowledge_graph['signal_types'] = signal_type_counts

            # Find knowledge clusters (similar embeddings)
            clusters = await self._find_knowledge_clusters(agent_embeddings)
            knowledge_graph['knowledge_clusters'] = clusters

            return knowledge_graph

        except Exception as e:
            logger.error(f"Error building knowledge graph for {agent_id}: {e}")
            return {'error': str(e)}

    async def _find_knowledge_clusters(self, embeddings: List) -> List[Dict]:
        """Find clusters of similar knowledge"""
        clusters = []

        try:
            # Simple clustering approach: find embeddings with high similarity
            processed = set()

            for i, embedding1 in enumerate(embeddings[:20]):  # Limit for performance
                if i in processed:
                    continue

                cluster = {
                    'center_embedding_id': str(embedding1.embedding_id),
                    'content_preview': embedding1.content_text[:100],
                    'similar_items': []
                }

                for j, embedding2 in enumerate(embeddings):
                    if i != j and j not in processed:
                        # Calculate similarity
                        similarity = self._calculate_cosine_similarity(
                            embedding1.embedding_vector,
                            embedding2.embedding_vector
                        )

                        if similarity > 0.8:  # High similarity threshold
                            cluster['similar_items'].append({
                                'embedding_id': str(embedding2.embedding_id),
                                'similarity': similarity,
                                'content_preview': embedding2.content_text[:100]
                            })
                            processed.add(j)

                if cluster['similar_items']:  # Only add clusters with similar items
                    clusters.append(cluster)
                    processed.add(i)

        except Exception as e:
            logger.error(f"Error finding knowledge clusters: {e}")

        return clusters

    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5

            return dot_product / (norm1 * norm2) if norm1 * norm2 > 0 else 0
        except Exception as _e:
            logger.warning(
                "embedding_generator._calculate_cosine_similarity: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding generation statistics"""
        return self.stats.copy()

    async def cleanup_old_embeddings(self, days_to_keep: int = 90):
        """Clean up old embeddings"""
        if LearningEmbedding:
            cutoff = datetime.now(timezone.utc) - timezone.timedelta(days=days_to_keep)
            deleted = LearningEmbedding.objects.filter(created_at__lt=cutoff).delete()
            logger.info(f"Cleaned up {deleted[0]} old embeddings")


# Global instance
embedding_generator = LearningEmbeddingGenerator()
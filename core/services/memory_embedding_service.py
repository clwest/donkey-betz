"""
Memory Embedding Service - Semantic Memory for Agents
======================================================

Session 293: Connect the embedding system to AgentMemory.

This service:
1. Generates embeddings for agent memories when created/updated
2. Enables semantic search across an agent's memory palace
3. Finds related memories for memory connections
4. Supports memory retrieval by semantic similarity

Usage:
    from core.services.memory_embedding_service import MemoryEmbeddingService

    service = MemoryEmbeddingService()

    # Store a new memory with embedding
    memory = service.create_memory(
        agent=my_agent,
        title="User prefers minimalist logos",
        content="When creating logos, user consistently chooses...",
        memory_type="preference"
    )

    # Search memories semantically
    results = service.search_memories(
        agent=my_agent,
        query="What does the user like for logo design?",
        top_k=5
    )
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import OpenAI for embeddings
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.warning("OpenAI not available for memory embeddings")


@dataclass
class MemorySearchResult:
    """Result from semantic memory search."""
    memory_id: str
    title: str
    content: str
    memory_type: str
    similarity: float
    importance_score: float
    access_count: int


class MemoryEmbeddingService:
    """
    Service for generating and searching memory embeddings.

    Uses OpenAI embeddings to enable semantic search across agent memories.
    """

    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None and HAS_OPENAI:
            api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
            if api_key:
                self._client = openai.OpenAI(api_key=api_key)
        return self._client

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        if not self.client:
            logger.warning("OpenAI client not available for embedding generation")
            return None

        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

    def _build_memory_text(self, title: str, content: str, context: str = "", memory_type: str = "") -> str:
        """Build text representation of a memory for embedding."""
        parts = [f"Title: {title}", f"Content: {content}"]
        if context:
            parts.append(f"Context: {context}")
        if memory_type:
            parts.append(f"Type: {memory_type}")
        return "\n".join(parts)

    def create_memory(
        self,
        agent,
        title: str,
        content: str,
        memory_type: str = "interaction",
        context: str = "",
        valence: str = "neutral",
        importance_score: float = 0.5,
        source_type: str = "",
        source_id: str = "",
        tags: List[str] = None
    ):
        """
        Create a new memory with auto-generated embedding.

        Args:
            agent: The Agent model instance
            title: Brief summary of the memory
            content: Full content of the memory
            memory_type: success, failure, preference, technique, insight, interaction, feedback
            context: Context in which memory was formed
            valence: positive, negative, neutral
            importance_score: 0-1 importance rating
            source_type: What triggered this memory
            source_id: ID of the source event
            tags: List of tags for grouping

        Returns:
            Created AgentMemory instance
        """
        from core.models_unified_system import AgentMemory

        # Generate embedding
        memory_text = self._build_memory_text(title, content, context, memory_type)
        embedding = self._generate_embedding(memory_text)

        # Create memory
        memory = AgentMemory.objects.create(
            agent=agent,
            title=title,
            content=content,
            context=context,
            memory_type=memory_type,
            valence=valence,
            importance_score=importance_score,
            embedding=embedding,
            source_type=source_type,
            source_id=source_id,
            tags=tags or []
        )

        logger.info(f"Created memory '{title}' for agent {agent.name} (embedding: {'yes' if embedding else 'no'})")

        # Find and connect related memories
        if embedding:
            self._connect_related_memories(memory, threshold=0.7)

        return memory

    def update_memory_embedding(self, memory) -> bool:
        """
        Update embedding for an existing memory.

        Use this when memory content has changed or to backfill missing embeddings.

        Returns:
            True if embedding was updated successfully
        """
        memory_text = self._build_memory_text(
            memory.title,
            memory.content,
            memory.context,
            memory.memory_type
        )
        embedding = self._generate_embedding(memory_text)

        if embedding:
            memory.embedding = embedding
            memory.save(update_fields=['embedding'])
            logger.info(f"Updated embedding for memory {memory.id}")
            return True

        return False

    def backfill_embeddings(self, agent=None, batch_size: int = 50) -> Dict[str, int]:
        """
        Generate embeddings for memories that don't have them.

        Args:
            agent: Optional agent to filter by (None = all agents)
            batch_size: Number of memories to process at a time

        Returns:
            Dict with counts: {processed, succeeded, failed}
        """
        from core.models_unified_system import AgentMemory

        # Find memories without embeddings
        queryset = AgentMemory.objects.filter(embedding__isnull=True)
        if agent:
            queryset = queryset.filter(agent=agent)

        memories = queryset[:batch_size]

        stats = {'processed': 0, 'succeeded': 0, 'failed': 0}

        for memory in memories:
            stats['processed'] += 1
            if self.update_memory_embedding(memory):
                stats['succeeded'] += 1
            else:
                stats['failed'] += 1

        logger.info(f"Backfill complete: {stats}")
        return stats

    def search_memories(
        self,
        agent,
        query: str,
        top_k: int = 5,
        memory_type: str = None,
        min_importance: float = None
    ) -> List[MemorySearchResult]:
        """
        Search agent memories by semantic similarity.

        Args:
            agent: The Agent to search memories for
            query: Search query text
            top_k: Number of results to return
            memory_type: Filter by memory type
            min_importance: Minimum importance score filter

        Returns:
            List of MemorySearchResult sorted by similarity (highest first)
        """
        from core.models_unified_system import AgentMemory

        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            logger.warning("Could not generate query embedding")
            return []

        # Get agent's memories with embeddings
        queryset = AgentMemory.objects.filter(
            agent=agent,
            embedding__isnull=False
        )

        if memory_type:
            queryset = queryset.filter(memory_type=memory_type)

        if min_importance is not None:
            queryset = queryset.filter(importance_score__gte=min_importance)

        memories = list(queryset)

        if not memories:
            return []

        # Calculate similarities
        results = []
        for memory in memories:
            similarity = self._cosine_similarity(query_embedding, memory.embedding)
            results.append(MemorySearchResult(
                memory_id=str(memory.id),
                title=memory.title,
                content=memory.content,
                memory_type=memory.memory_type,
                similarity=similarity,
                importance_score=memory.importance_score,
                access_count=memory.access_count
            ))

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x.similarity, reverse=True)

        # Update access counts for retrieved memories
        retrieved_ids = [r.memory_id for r in results[:top_k]]
        AgentMemory.objects.filter(id__in=retrieved_ids).update(
            access_count=models.F('access_count') + 1
        )

        return results[:top_k]

    def _connect_related_memories(self, memory, threshold: float = 0.7, max_connections: int = 3):
        """
        Find and connect semantically related memories.

        Creates connections in the memory graph for visualization.
        """
        from core.models_unified_system import AgentMemory

        if not memory.embedding:
            return

        # Get other memories for the same agent with embeddings
        other_memories = AgentMemory.objects.filter(
            agent=memory.agent,
            embedding__isnull=False
        ).exclude(id=memory.id)

        # Find similar memories
        similar = []
        for other in other_memories:
            similarity = self._cosine_similarity(memory.embedding, other.embedding)
            if similarity >= threshold:
                similar.append((other, similarity))

        # Sort by similarity and take top connections
        similar.sort(key=lambda x: x[1], reverse=True)
        for other_memory, similarity in similar[:max_connections]:
            memory.connected_memories.add(other_memory)
            logger.debug(f"Connected memories: '{memory.title}' <-> '{other_memory.title}' (sim={similarity:.3f})")

    def get_memory_context(
        self,
        agent,
        query: str,
        max_memories: int = 3,
        max_chars: int = 1500
    ) -> str:
        """
        Get relevant memory context for a query as formatted text.

        Useful for injecting into agent prompts.

        Args:
            agent: The Agent
            query: The current query/task
            max_memories: Maximum number of memories to include
            max_chars: Maximum total characters

        Returns:
            Formatted string with relevant memories
        """
        results = self.search_memories(agent, query, top_k=max_memories)

        if not results:
            return ""

        lines = ["Relevant memories:"]
        total_chars = len(lines[0])

        for result in results:
            if result.similarity < 0.4:  # Skip low-relevance memories
                continue

            memory_line = f"- [{result.memory_type}] {result.title}: {result.content[:200]}..."
            if total_chars + len(memory_line) > max_chars:
                break

            lines.append(memory_line)
            total_chars += len(memory_line)

        return "\n".join(lines) if len(lines) > 1 else ""


# Need to import models for F expression
from django.db import models

# Global instance
_memory_service: Optional[MemoryEmbeddingService] = None


def get_memory_embedding_service() -> MemoryEmbeddingService:
    """Get the global memory embedding service instance."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryEmbeddingService()
    return _memory_service

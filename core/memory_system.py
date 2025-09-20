"""
Memory System for AI Agents
Provides persistent memory storage and retrieval for learning agents
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
import hashlib
import numpy as np

logger = logging.getLogger(__name__)


class MemorySystem:
    """
    Unified memory system for agents to store and retrieve experiences
    """

    def __init__(self, namespace: str = "default"):
        """
        Initialize memory system

        Args:
            namespace: Memory namespace for isolation
        """
        self.namespace = namespace
        self.cache_prefix = f"memory_{namespace}"
        self.embedding_prefix = f"embedding_{namespace}"

        # Memory indices
        self.memory_index = {}
        self.embedding_index = {}

        # Load existing indices
        self._load_indices()

        logger.info(f"🧠 Memory System initialized for namespace: {namespace}")

    def _load_indices(self):
        """Load memory indices from cache"""
        try:
            self.memory_index = cache.get(f"{self.cache_prefix}_index", {})
            self.embedding_index = cache.get(f"{self.embedding_prefix}_index", {})
        except Exception as e:
            logger.warning(f"Could not load memory indices: {e}")
            self.memory_index = {}
            self.embedding_index = {}

    def _save_indices(self):
        """Save memory indices to cache"""
        try:
            cache.set(f"{self.cache_prefix}_index", self.memory_index, timeout=None)
            cache.set(f"{self.embedding_prefix}_index", self.embedding_index, timeout=None)
        except Exception as e:
            logger.error(f"Failed to save memory indices: {e}")

    async def store_memory(self, key: str, content: Dict[str, Any], ttl: Optional[int] = None):
        """
        Store a memory

        Args:
            key: Unique key for the memory
            content: Memory content as dictionary
            ttl: Time to live in seconds (None for permanent)
        """
        try:
            # Add metadata
            memory = {
                **content,
                '_stored_at': datetime.now().isoformat(),
                '_key': key,
                '_namespace': self.namespace
            }

            # Store in cache
            cache_key = f"{self.cache_prefix}_{key}"
            cache.set(cache_key, memory, timeout=ttl)

            # Update index
            self.memory_index[key] = {
                'stored_at': memory['_stored_at'],
                'ttl': ttl,
                'size': len(json.dumps(memory))
            }
            self._save_indices()

            logger.debug(f"💾 Stored memory: {key}")

        except Exception as e:
            logger.error(f"Failed to store memory {key}: {e}")

    async def retrieve_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a memory by key

        Args:
            key: Memory key

        Returns:
            Memory content or None if not found
        """
        try:
            cache_key = f"{self.cache_prefix}_{key}"
            memory = cache.get(cache_key)

            if memory:
                # Update access time
                memory['_last_accessed'] = datetime.now().isoformat()
                cache.set(cache_key, memory, timeout=cache.ttl(cache_key))

            return memory

        except Exception as e:
            logger.error(f"Failed to retrieve memory {key}: {e}")
            return None

    async def search_memories(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search memories based on query criteria

        Args:
            query: Search criteria
            limit: Maximum results

        Returns:
            List of matching memories
        """
        try:
            results = []

            for key in self.memory_index:
                memory = await self.retrieve_memory(key)
                if memory and self._matches_query(memory, query):
                    results.append(memory)
                    if len(results) >= limit:
                        break

            return results

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []

    def _matches_query(self, memory: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if memory matches query criteria"""
        for key, value in query.items():
            if key not in memory:
                return False
            if isinstance(value, list) and memory[key] not in value:
                return False
            elif memory[key] != value:
                return False
        return True

    async def store_embedding(self, key: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """
        Store an embedding vector

        Args:
            key: Unique key for the embedding
            embedding: Embedding vector
            metadata: Optional metadata
        """
        try:
            # Store embedding
            cache_key = f"{self.embedding_prefix}_{key}"
            embedding_data = {
                'vector': embedding,
                'metadata': metadata or {},
                'stored_at': datetime.now().isoformat(),
                'dimension': len(embedding)
            }

            cache.set(cache_key, embedding_data, timeout=None)

            # Update index
            self.embedding_index[key] = {
                'dimension': len(embedding),
                'stored_at': embedding_data['stored_at']
            }
            self._save_indices()

            logger.debug(f"📊 Stored embedding: {key} (dim: {len(embedding)})")

        except Exception as e:
            logger.error(f"Failed to store embedding {key}: {e}")

    async def retrieve_embedding(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an embedding by key

        Args:
            key: Embedding key

        Returns:
            Embedding data or None
        """
        try:
            cache_key = f"{self.embedding_prefix}_{key}"
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Failed to retrieve embedding {key}: {e}")
            return None

    async def find_similar_embeddings(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar embeddings using cosine similarity

        Args:
            query_embedding: Query vector
            top_k: Number of results

        Returns:
            List of (key, similarity) tuples
        """
        try:
            similarities = []
            query_vec = np.array(query_embedding)

            for key in self.embedding_index:
                embedding_data = await self.retrieve_embedding(key)
                if embedding_data:
                    stored_vec = np.array(embedding_data['vector'])

                    # Cosine similarity
                    similarity = np.dot(query_vec, stored_vec) / (
                        np.linalg.norm(query_vec) * np.linalg.norm(stored_vec)
                    )

                    similarities.append((key, float(similarity)))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    async def forget_memory(self, key: str):
        """
        Remove a memory

        Args:
            key: Memory key to forget
        """
        try:
            # Remove from cache
            cache_key = f"{self.cache_prefix}_{key}"
            cache.delete(cache_key)

            # Remove from index
            if key in self.memory_index:
                del self.memory_index[key]
                self._save_indices()

            logger.debug(f"🗑️ Forgot memory: {key}")

        except Exception as e:
            logger.error(f"Failed to forget memory {key}: {e}")

    async def clear_namespace(self):
        """Clear all memories in this namespace"""
        try:
            # Clear all memories
            for key in list(self.memory_index.keys()):
                await self.forget_memory(key)

            # Clear all embeddings
            for key in list(self.embedding_index.keys()):
                cache_key = f"{self.embedding_prefix}_{key}"
                cache.delete(cache_key)

            # Clear indices
            self.memory_index = {}
            self.embedding_index = {}
            self._save_indices()

            logger.info(f"🧹 Cleared namespace: {self.namespace}")

        except Exception as e:
            logger.error(f"Failed to clear namespace: {e}")

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            'namespace': self.namespace,
            'total_memories': len(self.memory_index),
            'total_embeddings': len(self.embedding_index),
            'memory_size_bytes': sum(m.get('size', 0) for m in self.memory_index.values()),
            'oldest_memory': min(
                (m['stored_at'] for m in self.memory_index.values()),
                default=None
            ),
            'newest_memory': max(
                (m['stored_at'] for m in self.memory_index.values()),
                default=None
            )
        }


# Global memory system instance
_global_memory = None


def get_memory_system(namespace: str = "default") -> MemorySystem:
    """Get or create memory system instance"""
    global _global_memory
    if _global_memory is None or _global_memory.namespace != namespace:
        _global_memory = MemorySystem(namespace)
    return _global_memory
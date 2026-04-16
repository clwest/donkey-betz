"""
Centralized Embedding Service - Session 744

This service wraps ALL OpenAI embedding API calls to provide:
1. Automatic usage tracking to LLMCallLog
2. Cost calculation and logging
3. Centralized configuration (model, retry logic)
4. Singleton pattern for efficiency

All services that need embeddings should use this instead of calling OpenAI directly.

Usage:
    from core.services.embedding_service import get_embedding_service
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

    service = get_embedding_service()

    # Single embedding
    embedding = service.create_embedding("Hello world")

    # Batch embeddings
    embeddings = service.create_embeddings(["text1", "text2", "text3"])
"""

import hashlib
import logging
import time
from decimal import Decimal
from typing import List, Optional
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)

# OpenAI embedding pricing per 1M tokens (as of Jan 2026)
EMBEDDING_COSTS = {
    'text-embedding-3-small': Decimal('0.02'),   # $0.02 per 1M tokens
    'text-embedding-3-large': Decimal('0.13'),   # $0.13 per 1M tokens
    'text-embedding-ada-002': Decimal('0.10'),   # $0.10 per 1M tokens (legacy)
}

DEFAULT_MODEL = 'text-embedding-3-small'


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    embedding: List[float]
    tokens_used: int
    cost: Decimal
    model: str
    latency_ms: int


@dataclass
class BatchEmbeddingResult:
    """Result of a batch embedding operation."""
    embeddings: List[List[float]]
    total_tokens: int
    cost: Decimal
    model: str
    latency_ms: int


class EmbeddingService:
    """
    Centralized service for all OpenAI embedding operations.

    Features:
    - Automatic usage tracking to LLMCallLog
    - Cost calculation
    - Batch support
    - Error handling with retries
    """

    _instance = None

    # Cache config
    CACHE_TTL = 7 * 86400  # 7 days — same text+model always returns same vector
    CACHE_PREFIX = 'emb'

    def __init__(self):
        self._client = None
        self._initialized = False

    # ── Cache helpers ────────────────────────────────────────────

    @staticmethod
    def _text_hash(text: str, model: str) -> str:
        """Deterministic hash for cache key. Strip whitespace, collapse spaces."""
        normalized = ' '.join(text.split())  # collapse whitespace (don't lowercase — changes semantics)
        return hashlib.sha256(f'{model}:{normalized}'.encode()).hexdigest()[:16]

    def _cache_get(self, text: str, model: str) -> Optional[List[float]]:
        """Try to fetch cached embedding from Redis."""
        try:
            from django.core.cache import cache
            key = f'{self.CACHE_PREFIX}:{model}:{self._text_hash(text, model)}'
            return cache.get(key)
        except Exception as _e:
            logger.warning(
                "embedding_service._cache_get: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _cache_set(self, text: str, model: str, embedding: List[float]) -> None:
        """Store embedding in Redis cache."""
        try:
            from django.core.cache import cache
            key = f'{self.CACHE_PREFIX}:{model}:{self._text_hash(text, model)}'
            cache.set(key, embedding, timeout=self.CACHE_TTL)
        except Exception as e:
            logger.debug(f"Embedding cache set failed (non-fatal): {e}")

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            from core.services.openai_client_factory import get_openai_client
            self._client = get_openai_client(api_key=settings.OPENAI_API_KEY)
        return self._client

    def create_embedding(
        self,
        text: str,
        model: str = DEFAULT_MODEL,
        user: Optional[str] = None,  # noqa: ARG002 - reserved for user tracking
        agent_name: str = 'system',
        log_usage: bool = True
    ) -> EmbeddingResult:
        """
        Create a single embedding and log usage.

        Args:
            text: Text to embed
            model: Embedding model to use
            user: Optional user identifier for tracking
            agent_name: Name of agent/service making the call
            log_usage: Whether to log to LLMCallLog (default True)

        Returns:
            EmbeddingResult with embedding vector and usage stats
        """
        # Check Redis cache first
        cached = self._cache_get(text, model)
        if cached is not None:
            logger.info("[embedding_cache] HIT model=%s agent=%s", model, agent_name)
            return EmbeddingResult(
                embedding=cached,
                tokens_used=0,
                cost=Decimal('0'),
                model=model,
                latency_ms=0
            )

        logger.info("[embedding_cache] MISS model=%s agent=%s", model, agent_name)
        start_time = time.time()

        try:
            response = self.client.embeddings.create(
                input=text,
                model=model,
                encoding_format='float'
            )

            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.total_tokens
            cost = self._calculate_cost(tokens_used, model)
            embedding = response.data[0].embedding

            # Store in cache
            self._cache_set(text, model, embedding)

            # Log usage
            if log_usage:
                self._log_usage(
                    model=model,
                    tokens=tokens_used,
                    cost=cost,
                    latency_ms=latency_ms,
                    agent_name=agent_name,
                    success=True,
                    batch_size=1
                )

            logger.debug(
                f"Embedding created: {tokens_used} tokens, ${cost:.6f}, {latency_ms}ms"
            )

            return EmbeddingResult(
                embedding=embedding,
                tokens_used=tokens_used,
                cost=cost,
                model=model,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)

            # Log failed attempt
            if log_usage:
                self._log_usage(
                    model=model,
                    tokens=0,
                    cost=Decimal('0'),
                    latency_ms=latency_ms,
                    agent_name=agent_name,
                    success=False,
                    error_message=str(e)
                )

            logger.error(f"Embedding creation failed: {e}")
            raise

    def create_embeddings(
        self,
        texts: List[str],
        model: str = DEFAULT_MODEL,
        user: Optional[str] = None,  # noqa: ARG002 - reserved for user tracking
        agent_name: str = 'system',
        log_usage: bool = True
    ) -> BatchEmbeddingResult:
        """
        Create embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to embed
            model: Embedding model to use
            user: Optional user identifier for tracking
            agent_name: Name of agent/service making the call
            log_usage: Whether to log to LLMCallLog (default True)

        Returns:
            BatchEmbeddingResult with embedding vectors and usage stats
        """
        if not texts:
            return BatchEmbeddingResult(
                embeddings=[],
                total_tokens=0,
                cost=Decimal('0'),
                model=model,
                latency_ms=0
            )

        # Check cache for each text — only API-call the misses
        results: list = [None] * len(texts)
        miss_indices: list = []
        miss_texts: list = []
        for i, text in enumerate(texts):
            cached = self._cache_get(text, model)
            if cached is not None:
                results[i] = cached
            else:
                miss_indices.append(i)
                miss_texts.append(text)

        if not miss_texts:
            # All cached
            logger.info(
                "[embedding_cache] BATCH all_cached=%d agent=%s",
                len(texts), agent_name
            )
            return BatchEmbeddingResult(
                embeddings=results,
                total_tokens=0,
                cost=Decimal('0'),
                model=model,
                latency_ms=0
            )

        cache_hits = len(texts) - len(miss_texts)
        if cache_hits:
            logger.info(
                "[embedding_cache] BATCH hits=%d misses=%d agent=%s",
                cache_hits, len(miss_texts), agent_name
            )

        start_time = time.time()

        try:
            response = self.client.embeddings.create(
                input=miss_texts,
                model=model,
                encoding_format='float'
            )

            latency_ms = int((time.time() - start_time) * 1000)
            total_tokens = response.usage.total_tokens
            cost = self._calculate_cost(total_tokens, model)

            # Extract embeddings in correct order and merge with cached results
            api_embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
            for j, idx in enumerate(miss_indices):
                results[idx] = api_embeddings[j]
                self._cache_set(miss_texts[j], model, api_embeddings[j])

            # Log usage
            if log_usage:
                self._log_usage(
                    model=model,
                    tokens=total_tokens,
                    cost=cost,
                    latency_ms=latency_ms,
                    agent_name=agent_name,
                    success=True,
                    batch_size=len(miss_texts)
                )

            logger.debug(
                f"Batch embeddings created: {len(miss_texts)} texts, {total_tokens} tokens, "
                f"${cost:.6f}, {latency_ms}ms"
            )

            return BatchEmbeddingResult(
                embeddings=results,
                total_tokens=total_tokens,
                cost=cost,
                model=model,
                latency_ms=latency_ms
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)

            # Log failed attempt
            if log_usage:
                self._log_usage(
                    model=model,
                    tokens=0,
                    cost=Decimal('0'),
                    latency_ms=latency_ms,
                    agent_name=agent_name,
                    success=False,
                    error_message=str(e),
                    batch_size=len(texts)
                )

            logger.error(f"Batch embedding creation failed: {e}")
            raise

    def _calculate_cost(self, tokens: int, model: str) -> Decimal:
        """Calculate cost based on token usage and model."""
        cost_per_million = EMBEDDING_COSTS.get(model, EMBEDDING_COSTS[DEFAULT_MODEL])
        return (Decimal(tokens) / Decimal('1000000')) * cost_per_million

    def _log_usage(
        self,
        model: str,
        tokens: int,
        cost: Decimal,
        latency_ms: int,
        agent_name: str,
        success: bool,
        error_message: Optional[str] = None,
        batch_size: int = 1  # noqa: ARG002 - reserved for future batch tracking
    ):
        """Log embedding usage to LLMCallLog."""
        try:
            from core.models_llm_routing import LLMCallLog

            LLMCallLog.objects.create(
                agent_name=agent_name,
                provider='openai',
                model_id=model,
                task_type='embedding',
                prompt_tokens=tokens,  # For embeddings, all tokens are "input"
                completion_tokens=0,
                total_tokens=tokens,
                latency_ms=latency_ms,
                cost=cost,
                success=success,
                error_message=error_message or '',
                was_fallback=False,
                was_auto_selected=False,
            )

            logger.debug(f"Logged embedding usage: {tokens} tokens, ${cost:.6f}")

        except Exception as e:
            # Don't fail the embedding call if logging fails
            logger.warning(f"Failed to log embedding usage: {e}")

    def get_embedding_sync(self, text: str, model: str = DEFAULT_MODEL) -> List[float]:
        """
        Simple synchronous method to get just the embedding vector.
        For backwards compatibility with existing code.
        """
        result = self.create_embedding(text, model=model)
        return result.embedding

    def get_embeddings_sync(self, texts: List[str], model: str = DEFAULT_MODEL) -> List[List[float]]:
        """
        Simple synchronous method to get just the embedding vectors.
        For backwards compatibility with existing code.
        """
        result = self.create_embeddings(texts, model=model)
        return result.embeddings


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the singleton EmbeddingService instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
        logger.info("EmbeddingService initialized")
    return _embedding_service

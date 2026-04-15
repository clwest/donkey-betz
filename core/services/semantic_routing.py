"""
Semantic Routing Service - Embedding-Based Agent Routing
=========================================================

Session 293: Finally connecting the RAG/embedding system to agent routing!

This service uses semantic similarity (embeddings) instead of keyword matching
to route user queries to the most appropriate agent.

Key Features:
1. Pre-computed agent capability embeddings
2. Real-time query embedding
3. Cosine similarity matching
4. Confidence scoring
5. Fallback to keyword matching if embeddings fail

Usage:
    from core.services.semantic_routing import SemanticRoutingService

    router = SemanticRoutingService()
    result = router.route_query("Research the AI market for my startup idea")
    print(result.agent_name)  # "CompetitorAnalysisAgent"
    print(result.confidence)  # 0.87
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import numpy as np
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Session 454: Import from unified routing config
try:
    from core.agents.routing_config import get_semantic_capabilities
    AGENT_CAPABILITIES = get_semantic_capabilities()
    logger.info("Loaded agent capabilities from unified routing config")
except ImportError:
    logger.warning("Could not import from routing_config, using fallback")
    AGENT_CAPABILITIES = {}  # Will be defined below as fallback

# Session 744: Use centralized EmbeddingService for all embedding calls
from core.services.embedding_service import get_embedding_service

HAS_OPENAI = True  # EmbeddingService handles this internally


@dataclass
class RoutingResult:
    """Result of semantic routing."""
    agent_name: str
    confidence: float
    method: str  # 'semantic' or 'keyword_fallback'
    all_matches: List[Tuple[str, float]]  # All agents with scores
    query_embedding_time_ms: int = 0
    match_time_ms: int = 0


# Session 454: AGENT_CAPABILITIES now imported from routing_config.py (single source of truth)
# Fallback definition only used if import fails
if not AGENT_CAPABILITIES:
    logger.warning("Using fallback AGENT_CAPABILITIES - import from routing_config failed")
    AGENT_CAPABILITIES = {
        "ImageAgent": {
            "description": "Generate images, logos, banners, illustrations",
            "examples": ["create a logo", "generate an illustration"],
            "keywords": ["image", "logo", "banner", "illustration"],
        },
        "VideoAgent": {
            "description": "Create videos and animations",
            "examples": ["create a video", "animate this image"],
            "keywords": ["video", "animate", "animation"],
        },
        "ResearchAgent": {
            "description": "Search for information and trends",
            "examples": ["what's trending", "find news"],
            "keywords": ["search", "find", "trending"],
        },
    }


class SemanticRoutingService:
    """
    Routes user queries to agents using semantic similarity.

    Uses OpenAI embeddings to find the most semantically similar agent
    based on their capability descriptions and example queries.
    """

    CACHE_KEY_PREFIX = "semantic_routing:"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    CACHE_TTL = 3600 * 24  # 24 hours for agent embeddings

    def __init__(self):
        self._embedding_service = None
        self._agent_embeddings: Dict[str, np.ndarray] = {}
        self._initialized = False

    @property
    def embedding_service(self):
        """Session 744: Lazy-load centralized EmbeddingService for tracked embedding calls."""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    def initialize(self) -> bool:
        """
        Initialize the service by pre-computing agent embeddings.

        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True

        # Session 744: EmbeddingService handles client initialization internally
        if not self.embedding_service:
            logger.warning("EmbeddingService not available, semantic routing disabled")
            return False

        try:
            # Load or generate agent embeddings
            for agent_name in AGENT_CAPABILITIES.keys():
                embedding = self._get_agent_embedding(agent_name)
                if embedding is not None:
                    self._agent_embeddings[agent_name] = embedding

            if len(self._agent_embeddings) >= len(AGENT_CAPABILITIES) * 0.8:
                self._initialized = True
                logger.info(f"Semantic routing initialized with {len(self._agent_embeddings)} agents")
                return True
            else:
                logger.warning(f"Only {len(self._agent_embeddings)} agent embeddings available")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize semantic routing: {e}")
            return False

    def _get_agent_embedding(self, agent_name: str) -> Optional[np.ndarray]:
        """
        Get or generate embedding for an agent's capabilities.

        Uses cache to avoid regenerating embeddings on every startup.
        """
        cache_key = f"{self.CACHE_KEY_PREFIX}agent:{agent_name}"

        # Try cache first
        cached = cache.get(cache_key)
        if cached is not None:
            try:
                return np.array(cached)
            except Exception as _e:
                logger.warning(
                    "semantic_routing._get_agent_embedding: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        # Generate embedding
        capability = AGENT_CAPABILITIES.get(agent_name)
        if not capability:
            return None

        # Build text representation of agent capabilities
        text_parts = [
            f"Agent: {agent_name}",
            f"Description: {capability['description']}",
            "Example queries this agent handles:",
        ]
        text_parts.extend([f"- {ex}" for ex in capability['examples']])
        text_parts.append(f"Keywords: {', '.join(capability['keywords'])}")

        text = "\n".join(text_parts)

        try:
            embedding = self._generate_embedding(text)
            if embedding is not None:
                # Cache for future use
                cache.set(cache_key, embedding.tolist(), self.CACHE_TTL)
                return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding for {agent_name}: {e}")

        return None

    def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text using centralized EmbeddingService."""
        try:
            # Session 744: Use centralized service for tracking
            result = self.embedding_service.create_embedding(
                text=text,
                model=self.EMBEDDING_MODEL,
                agent_name='SemanticRoutingService'
            )
            return np.array(result.embedding)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def route_query(self, query: str, top_k: int = 3) -> RoutingResult:
        """
        Route a user query to the most appropriate agent.

        Args:
            query: The user's input text
            top_k: Number of top matches to return

        Returns:
            RoutingResult with agent name, confidence, and all matches
        """
        import time

        # Initialize if needed
        if not self._initialized:
            self.initialize()

        # If no embeddings available, fall back to keyword matching
        if not self._agent_embeddings:
            return self._keyword_fallback(query)

        # Generate query embedding
        start_time = time.time()
        query_embedding = self._generate_embedding(query)
        embedding_time = int((time.time() - start_time) * 1000)

        if query_embedding is None:
            return self._keyword_fallback(query)

        # Calculate similarity to each agent
        start_time = time.time()
        scores = {}
        for agent_name, agent_embedding in self._agent_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, agent_embedding)
            scores[agent_name] = similarity
        match_time = int((time.time() - start_time) * 1000)

        # Sort by similarity
        sorted_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_matches = sorted_matches[:top_k]

        if top_matches:
            best_agent, best_score = top_matches[0]
            return RoutingResult(
                agent_name=best_agent,
                confidence=best_score,
                method='semantic',
                all_matches=top_matches,
                query_embedding_time_ms=embedding_time,
                match_time_ms=match_time,
            )

        return self._keyword_fallback(query)

    def _keyword_fallback(self, query: str) -> RoutingResult:
        """Fall back to keyword matching if semantic routing fails."""
        query_lower = query.lower()

        # Session 300: Priority phrases that override individual keyword matches
        # These are checked first before general keyword matching
        PRIORITY_PHRASES = {
            "CompetitorAnalysisAgent": [
                "competitor analysis", "analyze competitors", "competitive analysis",
                "market analysis", "swot analysis", "business landscape",
                "who are the competitors", "research the market"
            ],
            "CustomerResearchAgent": [
                "customer research", "customer pain points", "customer personas",
                "target audience", "user pain points", "customer needs"
            ],
            "WorkflowAgent": [
                "research and create", "create a package", "brand identity package",
                "thumbnail package"
            ],
        }

        # Check priority phrases first
        for agent_name, phrases in PRIORITY_PHRASES.items():
            for phrase in phrases:
                if phrase in query_lower:
                    return RoutingResult(
                        agent_name=agent_name,
                        confidence=0.9,
                        method='keyword_fallback_priority',
                        all_matches=[(agent_name, 0.9)],
                    )

        scores = {}
        for agent_name, capability in AGENT_CAPABILITIES.items():
            score = 0
            for keyword in capability['keywords']:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                scores[agent_name] = score / len(capability['keywords'])

        if scores:
            sorted_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_agent, best_score = sorted_matches[0]
            return RoutingResult(
                agent_name=best_agent,
                confidence=best_score,
                method='keyword_fallback',
                all_matches=sorted_matches[:3],
            )

        # Default to ResearchAgent
        return RoutingResult(
            agent_name="ResearchAgent",
            confidence=0.3,
            method='keyword_fallback',
            all_matches=[("ResearchAgent", 0.3)],
        )

    def get_agent_similarity(self, query: str, agent_name: str) -> float:
        """Get similarity score between query and specific agent."""
        if not self._initialized:
            self.initialize()

        if agent_name not in self._agent_embeddings:
            return 0.0

        query_embedding = self._generate_embedding(query)
        if query_embedding is None:
            return 0.0

        return self._cosine_similarity(query_embedding, self._agent_embeddings[agent_name])

    def explain_routing(self, query: str) -> Dict[str, Any]:
        """
        Explain why a query was routed to a particular agent.

        Useful for debugging and understanding the routing decision.
        """
        result = self.route_query(query, top_k=5)

        explanation = {
            'query': query,
            'selected_agent': result.agent_name,
            'confidence': result.confidence,
            'method': result.method,
            'all_scores': {name: round(score, 4) for name, score in result.all_matches},
            'timing': {
                'embedding_ms': result.query_embedding_time_ms,
                'matching_ms': result.match_time_ms,
            },
        }

        # Add agent description
        if result.agent_name in AGENT_CAPABILITIES:
            cap = AGENT_CAPABILITIES[result.agent_name]
            explanation['agent_description'] = cap['description']
            explanation['agent_examples'] = cap['examples'][:3]

        return explanation


# Global instance
_semantic_router: Optional[SemanticRoutingService] = None


def get_semantic_router() -> SemanticRoutingService:
    """Get the global semantic routing service instance."""
    global _semantic_router
    if _semantic_router is None:
        _semantic_router = SemanticRoutingService()
    return _semantic_router
